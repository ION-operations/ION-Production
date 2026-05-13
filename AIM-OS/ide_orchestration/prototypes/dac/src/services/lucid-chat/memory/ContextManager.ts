/**
 * Context Manager
 * 
 * Intelligent context window management
 * 
 * Epic 2.4: Context Management
 */

import { ChatMessage } from './ChatHistoryService'

/**
 * Context Window Strategy
 */
export type ContextStrategy = 'recent' | 'relevant' | 'sliding' | 'summary'

/**
 * Context Window Configuration
 */
export interface ContextConfig {
  maxTokens: number
  strategy: ContextStrategy
  preserveSystem?: boolean
  includeSummary?: boolean
}

/**
 * Context Manager Implementation
 */
export class ContextManager {
  private commandServerUrl: string

  constructor(commandServerUrl: string = 'http://localhost:5001') {
    this.commandServerUrl = commandServerUrl
  }

  /**
   * Manage context window
   */
  async manageContext(
    messages: ChatMessage[],
    config: ContextConfig
  ): Promise<ChatMessage[]> {
    switch (config.strategy) {
      case 'recent':
        return this.recentStrategy(messages, config)
      case 'relevant':
        return await this.relevantStrategy(messages, config)
      case 'sliding':
        return this.slidingStrategy(messages, config)
      case 'summary':
        return await this.summaryStrategy(messages, config)
      default:
        return messages
    }
  }

  /**
   * Recent strategy - keep most recent messages
   */
  private recentStrategy(messages: ChatMessage[], config: ContextConfig): ChatMessage[] {
    const estimatedTokens = this.estimateTokens(messages)

    if (estimatedTokens <= config.maxTokens) {
      return messages
    }

    // Keep system messages
    const systemMessages = config.preserveSystem
      ? messages.filter(m => m.role === 'system')
      : []

    // Take most recent messages until token limit
    let tokenCount = this.estimateTokens(systemMessages)
    const recentMessages: ChatMessage[] = []

    for (let i = messages.length - 1; i >= 0; i--) {
      const message = messages[i]
      if (message.role === 'system' && config.preserveSystem) continue

      const messageTokens = this.estimateTokens([message])
      if (tokenCount + messageTokens > config.maxTokens) break

      recentMessages.unshift(message)
      tokenCount += messageTokens
    }

    return [...systemMessages, ...recentMessages]
  }

  /**
   * Relevant strategy - keep most relevant messages using HHNI
   */
  private async relevantStrategy(
    messages: ChatMessage[],
    config: ContextConfig
  ): Promise<ChatMessage[]> {
    // Get last user message as query
    const lastUserMessage = messages.filter(m => m.role === 'user').slice(-1)[0]

    if (!lastUserMessage) {
      return this.recentStrategy(messages, config)
    }

    // Find relevant messages via HHNI
    try {
      const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tool: 'retrieve_memory',
          arguments: {
            query: lastUserMessage.content,
            memory_type: 'chat_message',
            limit: 10,
          },
        }),
      })

      const result = await response.json()

      if (result.success && result.data) {
        // Get relevant message IDs
        const relevantIds = result.data.results?.map((r: any) => {
          const msg = JSON.parse(r.content)
          return msg.id
        }) || []

        // Filter messages by relevance
        const relevantMessages = messages.filter(m => relevantIds.includes(m.id))

        // Combine with recent messages
        return this.recentStrategy([...relevantMessages, ...messages.slice(-5)], config)
      }
    } catch (error) {
      console.warn('[ContextManager] Relevant strategy failed:', error)
    }

    return this.recentStrategy(messages, config)
  }

  /**
   * Sliding window strategy - maintain fixed window size
   */
  private slidingStrategy(messages: ChatMessage[], config: ContextConfig): ChatMessage[] {
    const windowSize = Math.floor(config.maxTokens / 100) // ~100 tokens per message average

    const systemMessages = config.preserveSystem
      ? messages.filter(m => m.role === 'system')
      : []

    const nonSystemMessages = messages.filter(m => m.role !== 'system')
    const window = nonSystemMessages.slice(-windowSize)

    return [...systemMessages, ...window]
  }

  /**
   * Summary strategy - summarize old messages
   */
  private async summaryStrategy(
    messages: ChatMessage[],
    config: ContextConfig
  ): Promise<ChatMessage[]> {
    const estimatedTokens = this.estimateTokens(messages)

    if (estimatedTokens <= config.maxTokens) {
      return messages
    }

    // Split into old and recent
    const splitPoint = Math.floor(messages.length * 0.5)
    const oldMessages = messages.slice(0, splitPoint)
    const recentMessages = messages.slice(splitPoint)

    // Summarize old messages
    try {
      const summary = await this.summarizeMessages(oldMessages)

      const summaryMessage: ChatMessage = {
        id: `summary_${Date.now()}`,
        role: 'system',
        content: `Previous conversation summary:\n${summary}`,
        timestamp: new Date(),
      }

      return [summaryMessage, ...recentMessages]
    } catch (error) {
      console.warn('[ContextManager] Summary strategy failed:', error)
      return this.recentStrategy(messages, config)
    }
  }

  /**
   * Summarize messages using LLM
   */
  private async summarizeMessages(messages: ChatMessage[]): Promise<string> {
    const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tool: 'call_api',
        arguments: {
          provider: 'anthropic',
          endpoint: 'chat-completion',
          method: 'POST',
          data: {
            model: 'claude-3-5-sonnet-20241022',
            messages: [
              {
                role: 'user',
                content: `Summarize this conversation concisely:

${messages.map(m => `${m.role}: ${m.content}`).join('\n\n')}

Provide a clear, concise summary highlighting key points and decisions.`,
              },
            ],
            temperature: 0.3,
            max_tokens: 500,
          },
        },
      }),
    })

    const result = await response.json()

    if (result.success && result.data) {
      return result.data.content || result.data.text || 'Summary unavailable'
    }

    return 'Summary unavailable'
  }

  /**
   * Estimate token count (rough approximation)
   */
  private estimateTokens(messages: ChatMessage[]): number {
    const totalChars = messages.reduce((sum, m) => sum + m.content.length, 0)
    return Math.ceil(totalChars / 4) // Rough estimate: 1 token ≈ 4 chars
  }
}

// Singleton instance
let contextManagerInstance: ContextManager | null = null

export function getContextManager(commandServerUrl?: string): ContextManager {
  if (!contextManagerInstance) {
    contextManagerInstance = new ContextManager(commandServerUrl)
  }
  return contextManagerInstance
}

