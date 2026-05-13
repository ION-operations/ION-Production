/**
 * AI Chat Drawer Panel
 * Compact agent list and chat interface for right drawer
 * Shows online agents, agents awaiting replies, inter-agent conversations, and allows chatting with individual agents
 */

import React, { useState, useRef, useEffect, useMemo } from 'react'
import { Send, Bot, User, Loader, Circle, Clock, Users } from 'lucide-react'
import { useAIChat, AIMessage } from '../../hooks/useAIChat'
import { getMessageMonitor } from '../../services/messageMonitorService'

interface AgentStatus {
  name: string
  isOnline: boolean
  awaitingReply: boolean
  lastMessage?: Date
  unreadCount: number
}

interface ThreadInfo {
  threadId: string
  participants: string[]
  lastMessage?: Date
  lastMessageContent?: string
  unreadCount: number
}

interface ChatMessage {
  id: string
  agentId: string
  agentName: string
  content: string
  timestamp: Date
  type: 'user' | 'agent' | 'system'
}

interface AIChatDrawerProps {
  selectedAgent?: string | null
  selectedThread?: string | null
  onAgentChange?: (agent: string | null) => void
  onThreadChange?: (threadId: string | null) => void
}

export const AIChatDrawer: React.FC<AIChatDrawerProps> = ({ 
  selectedAgent = null,
  selectedThread = null,
  onAgentChange,
  onThreadChange
}) => {
  const [inputText, setInputText] = useState('')
  const [currentAgent, setCurrentAgent] = useState<string | null>(selectedAgent)
  const [currentThread, setCurrentThread] = useState<string | null>(selectedThread)
  const [localError, setLocalError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Sync selectedAgent/selectedThread props
  useEffect(() => {
    if (selectedAgent !== currentAgent) {
      setCurrentAgent(selectedAgent)
      setCurrentThread(null) // Clear thread when agent changes
    }
  }, [selectedAgent])

  useEffect(() => {
    if (selectedThread !== currentThread) {
      setCurrentThread(selectedThread)
      setCurrentAgent(null) // Clear agent when thread changes
    }
  }, [selectedThread])

  // Fetch all messages to determine agent status and threads
  const {
    messages: allMessages,
    threads,
    discoveredAgents,
    loading,
    error,
    fetchMessages,
    sendMessage
  } = useAIChat(undefined, undefined) // Fetch all messages for status

  // Fetch messages for selected agent or thread
  const {
    messages: chatMessages,
    loading: chatLoading
  } = useAIChat(currentAgent || undefined, currentThread || undefined)

  // Calculate agent statuses
  const agentStatuses = useMemo<AgentStatus[]>(() => {
    const statusMap = new Map<string, AgentStatus>()

    // Initialize all discovered agents
    discoveredAgents.forEach(agent => {
      statusMap.set(agent, {
        name: agent,
        isOnline: false,
        awaitingReply: false,
        unreadCount: 0
      })
    })

    // Analyze messages to determine status
    allMessages.forEach((msg: AIMessage) => {
      // Mark agent as online if they've sent a message recently (within last 5 minutes)
      const messageTime = new Date(msg.timestamp)
      const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000)
      if (messageTime > fiveMinutesAgo && msg.from_ai) {
        const status = statusMap.get(msg.from_ai) || {
          name: msg.from_ai,
          isOnline: true,
          awaitingReply: false,
          unreadCount: 0
        }
        status.isOnline = true
        if (!status.lastMessage || messageTime > status.lastMessage) {
          status.lastMessage = messageTime
        }
        statusMap.set(msg.from_ai, status)
      }

      // Check if agent is awaiting reply
      if (msg.response_required && msg.to_ai) {
        const status = statusMap.get(msg.to_ai) || {
          name: msg.to_ai,
          isOnline: false,
          awaitingReply: true,
          unreadCount: 0
        }
        status.awaitingReply = true
        statusMap.set(msg.to_ai, status)
      }
    })

    // Sort: awaiting reply first, then online, then offline
    return Array.from(statusMap.values()).sort((a, b) => {
      if (a.awaitingReply && !b.awaitingReply) return -1
      if (!a.awaitingReply && b.awaitingReply) return 1
      if (a.isOnline && !b.isOnline) return -1
      if (!a.isOnline && b.isOnline) return 1
      return a.name.localeCompare(b.name)
    })
  }, [allMessages, discoveredAgents])

  // Process threads into ThreadInfo format - only show inter-agent conversations
  const threadList = useMemo<ThreadInfo[]>(() => {
    return threads.map(thread => {
      const participants = thread.participants.filter(p => 
        p !== 'electron-app' && p !== 'User' && discoveredAgents.includes(p)
      )
      
      // Only show threads with 2+ agents (inter-agent conversations)
      if (participants.length < 2) return null

      return {
        threadId: thread.thread_id,
        participants: participants.sort(),
        lastMessage: thread.last_message ? new Date(thread.last_message.timestamp) : undefined,
        lastMessageContent: thread.last_message?.content,
        unreadCount: thread.unread_count || 0
      }
    }).filter((t): t is ThreadInfo => t !== null)
      .sort((a, b) => {
        // Sort by last message time (most recent first)
        if (a.lastMessage && b.lastMessage) {
          return b.lastMessage.getTime() - a.lastMessage.getTime()
        }
        if (a.lastMessage) return -1
        if (b.lastMessage) return 1
        return 0
      })
  }, [threads, discoveredAgents])

  // Convert chat messages to ChatMessage format
  const messages = useMemo<ChatMessage[]>(() => {
    if (!currentAgent && !currentThread) return []

    const converted: ChatMessage[] = []
    chatMessages.forEach((msg: AIMessage) => {
      // For agent view: show messages from/to that agent
      if (currentAgent && (msg.from_ai === currentAgent || msg.to_ai === currentAgent)) {
        converted.push({
          id: msg.message_id,
          agentId: msg.from_ai.toLowerCase(),
          agentName: msg.from_ai,
          content: msg.content,
          timestamp: new Date(msg.timestamp),
          type: msg.from_ai === currentAgent ? 'agent' : 'user'
        })
      }
      // For thread view: show all messages in thread
      else if (currentThread && msg.thread_id === currentThread) {
        converted.push({
          id: msg.message_id,
          agentId: msg.from_ai.toLowerCase(),
          agentName: msg.from_ai,
          content: msg.content,
          timestamp: new Date(msg.timestamp),
          type: 'agent'
        })
      }
    })

    return converted.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())
  }, [chatMessages, currentAgent, currentThread])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Start message monitoring
  useEffect(() => {
    const messageMonitor = getMessageMonitor()
    
    messageMonitor.startMonitoring({
      onMessageDetected: () => {
        fetchMessages()
      },
      onAgentWaiting: () => {
        fetchMessages()
      },
      onAgentContinued: () => {
        fetchMessages()
      },
      onError: (error) => {
        console.error('[AIChatDrawer] Message monitor error:', error)
      }
    })

    return () => {
      messageMonitor.stopMonitoring()
    }
  }, [fetchMessages])

  const handleSend = async () => {
    if (!inputText.trim()) return

    const messageContent = inputText.trim()
    setInputText('')

    try {
      if (currentAgent) {
        // Sending to specific agent
        await sendMessage(
          currentAgent,
          messageContent,
          'discussion',
          'medium'
        )
      } else if (currentThread) {
        // Sending to thread - get first participant that's not us
        const thread = threadList.find(t => t.threadId === currentThread)
        if (thread && thread.participants.length > 0) {
          await sendMessage(
            thread.participants[0],
            messageContent,
            'discussion',
            'medium',
            currentThread
          )
        }
      }
    } catch (err) {
      console.error('Failed to send message:', err)
      setLocalError(`Failed to send: ${err instanceof Error ? err.message : 'Unknown error'}`)
      setTimeout(() => setLocalError(null), 5000)
      setInputText(messageContent)
    }
  }

  const handleSelectAgent = (agentName: string) => {
    setCurrentAgent(agentName)
    setCurrentThread(null)
    if (onAgentChange) {
      onAgentChange(agentName)
    }
    if (onThreadChange) {
      onThreadChange(null)
    }
  }

  const handleSelectThread = (threadId: string) => {
    setCurrentThread(threadId)
    setCurrentAgent(null)
    if (onThreadChange) {
      onThreadChange(threadId)
    }
    if (onAgentChange) {
      onAgentChange(null)
    }
  }

  const getDisplayName = () => {
    if (currentThread) {
      const thread = threadList.find(t => t.threadId === currentThread)
      return thread ? thread.participants.join(' ↔ ') : 'Thread'
    }
    return currentAgent || 'Select Agent'
  }

  return (
    <div className="h-full flex flex-col bg-cursor-bg text-cursor-text">
      {/* Agent/Thread List View */}
      {!currentAgent && !currentThread ? (
        <>
          <div className="p-2 border-b border-cursor-border">
            <div className="flex items-center gap-1.5 mb-1.5">
              <Bot className="w-3.5 h-3.5 text-cursor-text-secondary" />
              <div className="text-xs font-semibold text-cursor-text" style={{ fontSize: '12px' }}>
                Select Agent or Conversation
              </div>
            </div>
          </div>

          {/* Inter-Agent Conversations */}
          {threadList.length > 0 && (
            <div className="px-2 pt-2 pb-1">
              <div className="flex items-center gap-1.5 mb-1">
                <Users className="w-3 h-3 text-cursor-text-secondary" />
                <div className="text-xs font-semibold text-cursor-text-secondary" style={{ fontSize: '11px' }}>
                  Conversations ({threadList.length})
                </div>
              </div>
              <div className="space-y-0.5 mb-2">
                {threadList.map((thread) => (
                  <button
                    key={thread.threadId}
                    onClick={() => handleSelectThread(thread.threadId)}
                    className="w-full p-1.5 rounded cursor-list-item hover:bg-cursor-hover transition-colors text-left"
                  >
                    <div className="flex items-center gap-1.5">
                      <Users className="w-3 h-3 text-cursor-status-bar flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="text-xs font-medium text-cursor-text truncate" style={{ fontSize: '11px' }}>
                          {thread.participants.join(' ↔ ')}
                        </div>
                        {thread.lastMessageContent && (
                          <div className="text-xs text-cursor-text-secondary truncate mt-0.5" style={{ fontSize: '10px' }}>
                            {thread.lastMessageContent.slice(0, 40)}
                            {thread.lastMessageContent.length > 40 ? '...' : ''}
                          </div>
                        )}
                        {thread.lastMessage && (
                          <div className="text-xs text-cursor-text-muted mt-0.5" style={{ fontSize: '9px' }}>
                            {thread.lastMessage.toLocaleTimeString()}
                          </div>
                        )}
                      </div>
                      {thread.unreadCount > 0 && (
                        <span className="w-4 h-4 bg-red-500 text-white text-[10px] rounded-full flex items-center justify-center flex-shrink-0" style={{ fontSize: '9px' }}>
                          {thread.unreadCount > 9 ? '9+' : thread.unreadCount}
                        </span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Agents List */}
          <div className="flex-1 overflow-y-auto p-1 cursor-scrollbar">
            {agentStatuses.length === 0 && threadList.length === 0 && !loading && (
              <div className="text-xs text-cursor-text-secondary p-2 text-center">
                No agents or conversations discovered yet. Agents will appear when they send messages.
              </div>
            )}

            {agentStatuses.length > 0 && (
              <div className="px-2 pb-1">
                <div className="flex items-center gap-1.5 mb-1">
                  <Bot className="w-3 h-3 text-cursor-text-secondary" />
                  <div className="text-xs font-semibold text-cursor-text-secondary" style={{ fontSize: '11px' }}>
                    Agents ({agentStatuses.length})
                  </div>
                </div>
              </div>
            )}

            {agentStatuses.map((agent) => (
              <button
                key={agent.name}
                onClick={() => handleSelectAgent(agent.name)}
                className="w-full p-2 rounded cursor-list-item mb-0.5 hover:bg-cursor-hover transition-colors text-left"
              >
                <div className="flex items-center gap-2">
                  {/* Status Indicator */}
                  <div className="relative">
                    {agent.awaitingReply ? (
                      <Clock className="w-3.5 h-3.5 text-yellow-400" />
                    ) : agent.isOnline ? (
                      <Circle className="w-3 h-3 fill-green-500 text-green-500" />
                    ) : (
                      <Circle className="w-3 h-3 fill-cursor-text-muted text-cursor-text-muted" />
                    )}
                  </div>

                  {/* Agent Name */}
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-medium text-cursor-text truncate" style={{ fontSize: '12px' }}>
                      {agent.name}
                    </div>
                    <div className="text-xs text-cursor-text-secondary" style={{ fontSize: '10px' }}>
                      {agent.awaitingReply ? '⏳ Awaiting reply' : agent.isOnline ? 'Online' : 'Offline'}
                    </div>
                  </div>

                  {/* Unread Badge */}
                  {agent.unreadCount > 0 && (
                    <span className="w-4 h-4 bg-red-500 text-white text-[10px] rounded-full flex items-center justify-center" style={{ fontSize: '9px' }}>
                      {agent.unreadCount > 9 ? '9+' : agent.unreadCount}
                    </span>
                  )}
                </div>
              </button>
            ))}

            {loading && (
              <div className="flex items-center justify-center p-2">
                <Loader className="w-3.5 h-3.5 animate-spin text-cursor-text-secondary" />
              </div>
            )}
          </div>
        </>
      ) : (
        <>
          {/* Chat View with Selected Agent/Thread */}
          <div className="p-2 border-b border-cursor-border">
            <div className="flex items-center gap-1.5 mb-1.5">
              <button
                onClick={() => {
                  setCurrentAgent(null)
                  setCurrentThread(null)
                  if (onAgentChange) {
                    onAgentChange(null)
                  }
                  if (onThreadChange) {
                    onThreadChange(null)
                  }
                }}
                className="text-cursor-text-secondary hover:text-cursor-text cursor-button"
                title="Back to agent/conversation list"
              >
                ←
              </button>
              {currentThread ? (
                <Users className="w-3.5 h-3.5 text-cursor-text-secondary" />
              ) : (
                <Bot className="w-3.5 h-3.5 text-cursor-text-secondary" />
              )}
              <div className="text-xs font-semibold text-cursor-text flex-1" style={{ fontSize: '12px' }}>
                {getDisplayName()}
              </div>
              {currentAgent && agentStatuses.find(a => a.name === currentAgent)?.awaitingReply && (
                <div title="Awaiting reply">
                  <Clock className="w-3 h-3 text-yellow-400" />
                </div>
              )}
            </div>
            {(error || localError) && (
              <div className="text-xs text-red-400 mt-1">
                {error || localError}
              </div>
            )}
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-1.5 space-y-1.5 cursor-scrollbar">
            {messages.length === 0 && !chatLoading && (
              <div className="text-xs text-cursor-text-secondary p-2 text-center">
                No messages yet. Start the conversation!
              </div>
            )}

            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-1.5 ${
                  message.type === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.type !== 'user' && (
                  <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 bg-cursor-status-bar">
                    <Bot className="w-3 h-3" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded p-1.5 ${
                    message.type === 'user'
                      ? 'bg-cursor-status-bar text-white'
                      : 'bg-cursor-sidebar text-cursor-text'
                  }`}
                  style={{ fontSize: '11px', lineHeight: '1.3' }}
                >
                  {message.type !== 'user' && (
                    <div className="text-xs font-semibold mb-0.5" style={{ fontSize: '10px' }}>
                      {message.agentName}
                    </div>
                  )}
                  <div className="text-xs whitespace-pre-wrap break-words" style={{ fontSize: '11px' }}>
                    {message.content}
                  </div>
                  <div className="text-xs opacity-60 mt-0.5" style={{ fontSize: '9px' }}>
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
                {message.type === 'user' && (
                  <div className="w-5 h-5 rounded-full bg-green-600 flex items-center justify-center flex-shrink-0">
                    <User className="w-3 h-3" />
                  </div>
                )}
              </div>
            ))}

            {chatLoading && (
              <div className="flex gap-1.5 justify-start">
                <div className="w-5 h-5 rounded-full bg-cursor-status-bar flex items-center justify-center">
                  <Bot className="w-3 h-3" />
                </div>
                <div className="bg-cursor-sidebar rounded p-1.5">
                  <Loader className="w-3 h-3 animate-spin" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-1.5 border-t border-cursor-border">
            <div className="flex gap-1">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    handleSend()
                  }
                }}
                placeholder={currentThread ? `Reply in conversation...` : `Message ${currentAgent}...`}
                className="flex-1 bg-cursor-input-bg text-cursor-text px-1.5 py-1 rounded border border-cursor-border focus:outline-none focus:border-cursor-status-bar cursor-input"
                style={{ fontSize: '11px' }}
              />
              <button
                onClick={handleSend}
                disabled={!inputText.trim() || chatLoading}
                className="px-1.5 py-1 bg-cursor-status-bar hover:bg-cursor-status-bar/80 disabled:bg-cursor-input-bg disabled:cursor-not-allowed rounded flex items-center cursor-button transition-colors"
                style={{ fontSize: '11px' }}
              >
                {chatLoading ? (
                  <Loader className="w-3 h-3 animate-spin" />
                ) : (
                  <Send className="w-3 h-3" />
                )}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
