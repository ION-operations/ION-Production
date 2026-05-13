/**
 * Chat History Service
 * 
 * Manages chat history with CMC/HHNI integration
 * 
 * Epic 2.4: Context Management
 */

import { BaseAPIService, APIResponse } from '../base/BaseAPIService'

/**
 * Chat Message
 */
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  metadata?: {
    tokensUsed?: number
    confidence?: number
    model?: string
    provider?: string
  }
}

/**
 * Chat Session
 */
export interface ChatSession {
  id: string
  userId?: string
  title?: string
  messages: ChatMessage[]
  startTime: Date
  lastUpdate: Date
  metadata?: {
    totalMessages?: number
    totalTokens?: number
    topics?: string[]
  }
}

/**
 * Chat History Service Implementation
 */
export class ChatHistoryService extends BaseAPIService {
  private currentSession: ChatSession | null = null

  constructor(commandServerUrl: string = 'http://localhost:5001') {
    super('chat_history', commandServerUrl, undefined, 'chat_history')
  }

  /**
   * Start new chat session
   */
  async startSession(userId?: string, title?: string): Promise<APIResponse<ChatSession>> {
    return this.handleRequest(
      async () => {
        const session: ChatSession = {
          id: `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          userId,
          title: title || 'New Chat',
          messages: [],
          startTime: new Date(),
          lastUpdate: new Date(),
          metadata: {
            totalMessages: 0,
            totalTokens: 0,
            topics: [],
          },
        }

        this.currentSession = session

        // Store session in CMC
        await this.storeSession(session)

        return session
      },
      'startSession',
      { userId, title }
    )
  }

  /**
   * Add message to current session
   */
  async addMessage(message: Omit<ChatMessage, 'id' | 'timestamp'>): Promise<APIResponse<ChatMessage>> {
    return this.handleRequest(
      async () => {
        if (!this.currentSession) {
          throw new Error('No active session')
        }

        const fullMessage: ChatMessage = {
          ...message,
          id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          timestamp: new Date(),
        }

        this.currentSession.messages.push(fullMessage)
        this.currentSession.lastUpdate = new Date()
        this.currentSession.metadata!.totalMessages! += 1

        if (message.metadata?.tokensUsed) {
          this.currentSession.metadata!.totalTokens! += message.metadata.tokensUsed
        }

        // Store message in CMC
        await this.storeMessage(fullMessage, this.currentSession.id)

        // Index in HHNI for retrieval
        await this.indexMessage(fullMessage)

        return fullMessage
      },
      'addMessage',
      message
    )
  }

  /**
   * Get current session
   */
  getCurrentSession(): ChatSession | null {
    return this.currentSession
  }

  /**
   * Load session by ID
   */
  async loadSession(sessionId: string): Promise<APIResponse<ChatSession>> {
    return this.handleRequest(
      async () => {
        // Retrieve from CMC
        const response = await fetch(`${this.baseURL}/mcp/execute`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tool: 'retrieve_memory',
            arguments: {
              query: `session ${sessionId}`,
              memory_type: 'chat_session',
              limit: 1,
            },
          }),
        })

        const result = await response.json()

        if (!result.success || !result.data) {
          throw new Error('Session not found')
        }

        const session: ChatSession = JSON.parse(result.data.content)
        this.currentSession = session

        return session
      },
      'loadSession',
      { sessionId }
    )
  }

  /**
   * Get message history (last N messages)
   */
  getRecentMessages(limit: number = 10): ChatMessage[] {
    if (!this.currentSession) {
      return []
    }

    return this.currentSession.messages.slice(-limit)
  }

  /**
   * Search messages
   */
  async searchMessages(query: string, limit: number = 10): Promise<APIResponse<ChatMessage[]>> {
    return this.handleRequest(
      async () => {
        const response = await fetch(`${this.baseURL}/mcp/execute`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tool: 'retrieve_memory',
            arguments: {
              query,
              memory_type: 'chat_message',
              limit,
            },
          }),
        })

        const result = await response.json()

        if (!result.success || !result.data) {
          return []
        }

        return result.data.results?.map((r: any) => JSON.parse(r.content)) || []
      },
      'searchMessages',
      { query, limit }
    )
  }

  /**
   * Store session in CMC
   */
  private async storeSession(session: ChatSession): Promise<void> {
    try {
      await fetch(`${this.baseURL}/mcp/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool: 'store_memory',
          arguments: {
            content: JSON.stringify(session),
            memory_type: 'chat_session',
            tags: ['chat', 'session', session.id],
            metadata: {
              session_id: session.id,
              user_id: session.userId,
              timestamp: session.startTime.toISOString(),
            },
          },
        }),
      })
    } catch (error) {
      console.warn('[ChatHistory] Failed to store session:', error)
    }
  }

  /**
   * Store message in CMC
   */
  private async storeMessage(message: ChatMessage, sessionId: string): Promise<void> {
    try {
      await fetch(`${this.baseURL}/mcp/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool: 'store_memory',
          arguments: {
            content: JSON.stringify(message),
            memory_type: 'chat_message',
            tags: ['chat', 'message', sessionId, message.role],
            metadata: {
              message_id: message.id,
              session_id: sessionId,
              role: message.role,
              timestamp: message.timestamp.toISOString(),
            },
          },
        }),
      })
    } catch (error) {
      console.warn('[ChatHistory] Failed to store message:', error)
    }
  }

  /**
   * Index message in HHNI for semantic retrieval
   */
  private async indexMessage(message: ChatMessage): Promise<void> {
    // HHNI indexing happens automatically via store_memory
    // This is a placeholder for any additional indexing logic
  }

  isAvailable(): boolean {
    return true
  }
}

// Singleton instance
let chatHistoryServiceInstance: ChatHistoryService | null = null

export function getChatHistoryService(commandServerUrl?: string): ChatHistoryService {
  if (!chatHistoryServiceInstance) {
    chatHistoryServiceInstance = new ChatHistoryService(commandServerUrl)
  }
  return chatHistoryServiceInstance
}

