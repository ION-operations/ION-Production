/**
 * useAIChat Hook
 * React hook for AI-to-AI chat functionality
 * 
 * Provides:
 * - Fetch messages from AI agents (via MCP when available)
 * - Send messages to AI agents (via MCP when available)
 * - Start discussion threads
 * - Real-time updates (polling)
 * - Auto-detection of agents from messages
 * - Optional Aether Chat orchestrator integration for enhanced processing
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { getServiceBridge } from '../services/serviceBridge'

// Optional Aether Chat orchestrator integration
// Import only if orchestrator is available (DAC prototype)
let runAetherChatTurn: any = null
try {
  // Try to import orchestrator (may not be available in all contexts)
  const orchestratorModule = require('../../ide_orchestration/prototypes/dac/src/services/aetherChatOrchestrator')
  runAetherChatTurn = orchestratorModule.runAetherChatTurn
} catch (error) {
  // Orchestrator not available - use basic MCP flow
  console.log('[useAIChat] Aether Chat orchestrator not available, using basic MCP flow')
}

const serviceBridge = getServiceBridge()

export interface AIMessage {
  message_id: string
  from_ai: string
  to_ai: string
  content: string
  message_type: string
  priority: string
  thread_id?: string
  timestamp: string
  response_required: boolean
}

export interface ChatThread {
  thread_id: string
  topic: string
  participants: string[]
  last_message?: AIMessage
  unread_count: number
}

export function useAIChat(agentId?: string, threadId?: string) {
  const [messages, setMessages] = useState<AIMessage[]>([])
  const [threads, setThreads] = useState<ChatThread[]>([])
  const [discoveredAgents, setDiscoveredAgents] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isPolling, setIsPolling] = useState(true)
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null)

  /**
   * Fetch messages from AI agents (via MCP when available)
   */
  const fetchMessages = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      console.log('[useAIChat] Fetching messages...', { agentId, threadId })

      // Fetch messages via ServiceBridge (routes to MCP or HTTP)
      // For shared chat (no agentId): show ALL messages
      // For direct chat (with agentId): show messages involving that agent (from OR to)
      let fetchedMessages: AIMessage[]
      if (agentId) {
        // Fetch messages FROM the agent AND TO the agent (to show full conversation)
        const [fromMessages, toMessages] = await Promise.all([
          serviceBridge.getAIMessages(agentId, undefined), // Messages FROM agent
          serviceBridge.getAIMessages(undefined, agentId)  // Messages TO agent
        ])
        // Combine and deduplicate by message_id
        const messageMap = new Map<string, AIMessage>()
        fromMessages.forEach(msg => messageMap.set(msg.message_id, msg))
        toMessages.forEach(msg => messageMap.set(msg.message_id, msg))
        fetchedMessages = Array.from(messageMap.values())
      } else {
        // Shared chat: show ALL messages
        fetchedMessages = await serviceBridge.getAIMessages(undefined, undefined)
      }

      console.log('[useAIChat] Received messages:', fetchedMessages?.length || 0, fetchedMessages)

      // Filter by thread if specified
      let filteredMessages = fetchedMessages
      if (threadId) {
        filteredMessages = fetchedMessages.filter(msg => msg.thread_id === threadId)
      }

      // Sort by timestamp (oldest first - standard chat order)
      filteredMessages.sort((a, b) => 
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      )

      console.log('[useAIChat] Filtered messages:', filteredMessages.length)

      setMessages(filteredMessages)

      // Auto-detect agents from messages
      const agentSet = new Set<string>()
      filteredMessages.forEach((msg) => {
        if (msg.from_ai && msg.from_ai !== 'electron-app' && msg.from_ai !== 'User') {
          agentSet.add(msg.from_ai)
        }
        if (msg.to_ai && msg.to_ai !== 'electron-app' && msg.to_ai !== 'User') {
          agentSet.add(msg.to_ai)
        }
      })
      // FIXED: Only update if agents actually changed to prevent infinite loops
      const newAgents = Array.from(agentSet).sort()
      setDiscoveredAgents(prev => {
        if (JSON.stringify(prev) !== JSON.stringify(newAgents)) {
          return newAgents
        }
        return prev
      })

      // Derive threads from messages
      const threadMap = new Map<string, ChatThread>()
      filteredMessages.forEach((msg) => {
        if (msg.thread_id) {
          if (!threadMap.has(msg.thread_id)) {
            threadMap.set(msg.thread_id, {
              thread_id: msg.thread_id,
              topic: `Thread ${msg.thread_id.slice(-6)}`, // Use last 6 chars as topic
              participants: [msg.from_ai, msg.to_ai],
              last_message: msg,
              unread_count: 0
            })
          } else {
            const thread = threadMap.get(msg.thread_id)!
            if (!thread.participants.includes(msg.from_ai)) {
              thread.participants.push(msg.from_ai)
            }
            if (!thread.participants.includes(msg.to_ai)) {
              thread.participants.push(msg.to_ai)
            }
            // Update last message if this one is newer
            if (new Date(msg.timestamp) > new Date(thread.last_message?.timestamp || 0)) {
              thread.last_message = msg
            }
          }
        }
      })
      setThreads(Array.from(threadMap.values()))
    } catch (err) {
      console.error('Failed to fetch AI messages:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch messages')
    } finally {
      setLoading(false)
    }
  }, [agentId, threadId])

  /**
   * Send message to AI agent (via MCP when available)
   * Optionally uses Aether Chat orchestrator if available for enhanced processing
   */
  const sendMessage = useCallback(async (
    toAI: string,
    content: string,
    messageType: 'discussion' | 'task_handoff' | 'problem_solving' | 'profile_sharing' | 'status_update' | 'urgent' = 'discussion',
    priority: 'low' | 'medium' | 'high' | 'urgent' = 'medium',
    overrideThreadId?: string,
    useOrchestrator: boolean = false // Optional: use Aether Chat orchestrator for enhanced processing
  ) => {
    try {
      setLoading(true)
      setError(null)

      // Use overrideThreadId if provided, otherwise use threadId from hook closure
      const targetThreadId = overrideThreadId !== undefined ? overrideThreadId : threadId

      // Optionally use Aether Chat orchestrator for enhanced processing
      if (useOrchestrator && runAetherChatTurn) {
        try {
          // Map AI-to-AI message to RawUserTurn format
          const rawTurn = {
            sessionId: targetThreadId || `ai_chat_${Date.now()}`,
            userId: undefined,
            source: 'standalone' as const,
            message: content,
            timestamp: new Date().toISOString(),
            conversationHistory: messages.map(msg => ({
              id: msg.message_id,
              timestamp: new Date(msg.timestamp),
              role: (msg.from_ai === toAI ? 'assistant' : 'user') as 'user' | 'assistant',
              content: msg.content
            }))
          }

          // Process through orchestrator
          const finalTurn = await runAetherChatTurn(rawTurn)

          // Extract enhanced content from orchestrator result
          const enhancedContent = finalTurn.assistantText || content

          // Send via MCP with enhanced content
          const result = await serviceBridge.sendAIMessage(
            toAI,
            enhancedContent,
            messageType,
            priority,
            targetThreadId
          )

          if (result && result.message_id) {
            // Store orchestrator metadata (confidence, evidence) if needed
            // This could be stored in message metadata for later retrieval
            await fetchMessages()
            return { 
              success: true, 
              message_id: result.message_id,
              orchestrator_metadata: {
                confidence: finalTurn.confidence,
                evidence_count: finalTurn.evidence.length,
                context_web_nodes: finalTurn.contextWeb.nodes.length
              }
            }
          } else {
            throw new Error('Failed to send message (no response from service)')
          }
        } catch (orchestratorError) {
          console.warn('[useAIChat] Orchestrator processing failed, falling back to basic MCP flow:', orchestratorError)
          // Fall through to basic MCP flow
        }
      }

      // Basic MCP flow (default or fallback)
      const result = await serviceBridge.sendAIMessage(
        toAI,
        content,
        messageType,
        priority,
        targetThreadId
      )

      if (result && result.message_id) {
        // Refresh messages after sending
        await fetchMessages()
        return { success: true, message_id: result.message_id }
      } else {
        throw new Error('Failed to send message (no response from service)')
      }
    } catch (err) {
      console.error('Failed to send AI message:', err)
      setError(err instanceof Error ? err.message : 'Failed to send message')
      throw err
    } finally {
      setLoading(false)
    }
  }, [fetchMessages, threadId, messages])

  /**
   * Start new discussion thread (via MCP when available)
   */
  const startDiscussion = useCallback(async (
    toAI: string,
    topic: string,
    initialMessage: string
  ) => {
    try {
      setLoading(true)
      setError(null)

      // Use MCP API directly for discussion creation
      const { getMCPAPI } = await import('../services/mcpApi')
      const mcpApi = getMCPAPI()
      
      const result = await mcpApi.startAIDiscussion(toAI, topic, initialMessage)

      if (result && result.thread_id) {
        // Refresh messages after starting discussion
        await fetchMessages()
        return result.thread_id
      } else {
        throw new Error('Failed to start discussion (no thread_id returned)')
      }
    } catch (err) {
      console.error('Failed to start AI discussion:', err)
      setError(err instanceof Error ? err.message : 'Failed to start discussion')
      throw err
    } finally {
      setLoading(false)
    }
  }, [fetchMessages])

  /**
   * Initialize polling for real-time updates
   */
  useEffect(() => {
    if (!isPolling) return

    // Initial fetch
    fetchMessages()

    // Set up polling interval (every 5 seconds - reduced from 3 to prevent excessive API calls)
    pollingIntervalRef.current = setInterval(() => {
      fetchMessages()
    }, 5000)

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
        pollingIntervalRef.current = null
      }
    }
    // FIXED: Only depend on agentId, threadId, and isPolling - not fetchMessages
    // fetchMessages is stable due to useCallback dependencies
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [agentId, threadId, isPolling])

  /**
   * Stop polling
   */
  const stopPolling = useCallback(() => {
    setIsPolling(false)
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current)
      pollingIntervalRef.current = null
    }
  }, [])

  /**
   * Resume polling
   */
  const resumePolling = useCallback(() => {
    setIsPolling(true)
  }, [])

  return {
    messages,
    threads,
    discoveredAgents,
    loading,
    error,
    isPolling,
    fetchMessages,
    sendMessage,
    startDiscussion,
    stopPolling,
    resumePolling
  }
}

