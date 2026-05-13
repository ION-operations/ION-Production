/**
 * Chat Interface Tab Component
 * Tab 2: Multi-agent chat interface for Cursor AI agents
 * 
 * Phase 1: Multi-Agent Discussion - Integrated with MCP AI collaboration tools
 */

import React, { useState, useRef, useEffect, useMemo } from 'react'
import { MessageSquare, Send, Bot, User, Loader, Copy, Trash2, RefreshCw, Users, MessageCircle, Search, X, AlertCircle } from 'lucide-react'
import { useAIChat, AIMessage } from '../../hooks/useAIChat'
import { getMessageMonitor } from '../../services/messageMonitorService'

interface ChatMessage {
  id: string
  agentId: string
  agentName: string
  content: string
  timestamp: Date
  type: 'user' | 'agent' | 'system'
  messageType?: string
  priority?: string
  threadId?: string
}

interface ChatInterfaceTabProps {
  initialAgent?: string | null
  onAgentChange?: (agent: string | null) => void
}

export const ChatInterfaceTab: React.FC<ChatInterfaceTabProps> = ({ 
  initialAgent = null,
  onAgentChange 
}) => {
  const [inputText, setInputText] = useState('')
  const [selectedAgent, setSelectedAgent] = useState<string | null>(initialAgent)
  const [selectedThread, setSelectedThread] = useState<string | undefined>(undefined)
  const [showStartDiscussion, setShowStartDiscussion] = useState(false)
  const [discussionTopic, setDiscussionTopic] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [localError, setLocalError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Sync initialAgent prop to selectedAgent state
  useEffect(() => {
    if (initialAgent && initialAgent !== selectedAgent) {
      setSelectedAgent(initialAgent)
    }
  }, [initialAgent])

  // Use AI chat hook with selected agent/thread filter
  // IMPORTANT: When selectedAgent is null, pass undefined to show ALL messages (shared chat)
  const {
    messages: aiMessages,
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
  } = useAIChat(selectedAgent || undefined, selectedThread)
  
  // Debug: Log aiMessages changes
  useEffect(() => {
    console.log('[ChatInterfaceTab] aiMessages changed:', aiMessages.length, aiMessages)
  }, [aiMessages])

  // Start message monitoring when component mounts
  useEffect(() => {
    const messageMonitor = getMessageMonitor()
    
    // Start monitoring with callbacks
    messageMonitor.startMonitoring({
      onMessageDetected: (message) => {
        console.log('[ChatInterfaceTab] Proceed message detected:', message.message_id)
        // Refresh messages to show agent updates
        fetchMessages()
      },
      onAgentTriggered: (agentId, messageId) => {
        console.log(`[ChatInterfaceTab] Agent ${agentId} triggered by message ${messageId}`)
        // Show notification or update UI
        setLocalError(null) // Clear any errors
      },
      onAgentWaiting: (agentId, waitingFor) => {
        console.log(`[ChatInterfaceTab] Agent ${agentId} waiting for reply from ${waitingFor}`)
        // Refresh to show waiting state
        fetchMessages()
      },
      onAgentContinued: (agentId) => {
        console.log(`[ChatInterfaceTab] Agent ${agentId} continued after receiving reply`)
        // Refresh to show continued work
        fetchMessages()
      },
      onAgentStopped: (agentId, reason) => {
        console.log(`[ChatInterfaceTab] Agent ${agentId} stopped: ${reason}`)
        // Refresh to show stopped state
        fetchMessages()
      },
      onError: (error) => {
        console.error('[ChatInterfaceTab] Message monitor error:', error)
        setLocalError(`Message monitor error: ${error.message}`)
      }
    })

    // Cleanup: stop monitoring when component unmounts
    return () => {
      messageMonitor.stopMonitoring()
    }
  }, [fetchMessages])

  // Convert AI messages to ChatMessage format with search filtering
  const messages = useMemo<ChatMessage[]>(() => {
    const converted: ChatMessage[] = []

    console.log('[ChatInterfaceTab] Converting messages, aiMessages:', aiMessages.length, aiMessages)

    // Add helpful welcome message if no messages
    if (aiMessages.length === 0) {
      converted.push({
        id: 'system-1',
        agentId: 'system',
        agentName: 'System',
        content: 'Welcome to the AIM-OS Multi-Agent Chat!\n\n💬 This is a shared chat room where:\n• All agents can see all messages\n• You can chat with everyone at once\n• Or select a specific agent from the dropdown for direct messages\n• Messages from all agents appear here automatically\n\n🚀 Just type and press Enter to start chatting!',
        timestamp: new Date(),
        type: 'system'
      })
    }

    // Convert AI messages to ChatMessage format
    aiMessages.forEach((msg: AIMessage) => {
      console.log('[ChatInterfaceTab] Converting message:', msg.message_id, msg.from_ai, msg.content.substring(0, 50))
      converted.push({
        id: msg.message_id,
        agentId: msg.from_ai.toLowerCase(),
        agentName: msg.from_ai,
        content: msg.content,
        timestamp: new Date(msg.timestamp),
        type: 'agent',
        messageType: msg.message_type,
        priority: msg.priority,
        threadId: msg.thread_id
      })
    })

    // Apply search filter if query exists
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      return converted.filter(msg => 
        msg.content.toLowerCase().includes(query) ||
        msg.agentName.toLowerCase().includes(query) ||
        (msg.threadId && msg.threadId.toLowerCase().includes(query))
      )
    }

    console.log('[ChatInterfaceTab] Final converted messages:', converted.length, converted)
    return converted
  }, [aiMessages, searchQuery])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!inputText.trim()) return

    const messageContent = inputText.trim()
    setInputText('') // Clear input immediately for better UX

    try {
      // If agent selected, send direct message to that agent
      // Otherwise, broadcast to all agents (send to first available agent or use a broadcast mechanism)
      if (selectedAgent) {
        // Direct message to specific agent
        await sendMessage(
          selectedAgent,
          messageContent,
          'discussion',
          'medium'
        )
      } else {
        // Broadcast to all agents - send to the first discovered agent or use a broadcast agent
        // For now, if no agent selected, try sending to "Aether" as default broadcast target
        // In the future, we could add a "broadcast" mode that sends to all agents
        const targetAgent = discoveredAgents.length > 0 ? discoveredAgents[0] : 'Aether'
        await sendMessage(
          targetAgent,
          `[Broadcast to all agents] ${messageContent}`,
          'discussion',
          'medium'
        )
      }
      
      // Messages will refresh automatically via polling (every 3 seconds)
      // No need to manually refresh
    } catch (err) {
      console.error('Failed to send message:', err)
      setLocalError(`Failed to send message: ${err instanceof Error ? err.message : 'Unknown error'}. Make sure the Extension is running (Cursor must be open).`)
      setTimeout(() => setLocalError(null), 8000)
      // Restore input text on error
      setInputText(messageContent)
    }
  }

  const handleStartDiscussion = async () => {
    if (!discussionTopic.trim() || !inputText.trim() || !selectedAgent) {
      alert('Please fill in topic, select an agent, and write an initial message')
      return
    }

    try {
      const threadId = await startDiscussion(
        selectedAgent,
        discussionTopic,
        inputText
      )
      setSelectedThread(threadId)
      setShowStartDiscussion(false)
      setDiscussionTopic('')
      setInputText('')
    } catch (err) {
      console.error('Failed to start discussion:', err)
      alert(`Failed to start discussion: ${err instanceof Error ? err.message : 'Unknown error'}`)
    }
  }

  return (
    <div className="h-full flex flex-col bg-cursor-bg text-cursor-text">
      {/* Header */}
      <div className="p-2 border-b border-cursor-border">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-base font-semibold flex items-center gap-1.5" style={{ fontSize: '15px' }}>
            <MessageSquare className="w-4 h-4" />
            Chat Interface
          </h2>
          <div className="flex gap-1.5">
            {/* Thread Selector */}
            {threads.length > 0 && (
              <select
                value={selectedThread || ''}
                onChange={(e) => setSelectedThread(e.target.value || undefined)}
                className="bg-cursor-input-bg text-cursor-text px-2 py-1 rounded text-xs border border-cursor-border cursor-input"
                style={{ fontSize: '12px' }}
              >
                <option value="">All Threads</option>
                {threads.map((thread) => (
                  <option key={thread.thread_id} value={thread.thread_id}>
                    {thread.topic} ({thread.participants.length} agents)
                  </option>
                ))}
              </select>
            )}
            {/* Agent Selector - Optional: Select specific agent for direct messages */}
            <select
              value={selectedAgent || ''}
              onChange={(e) => {
                const newAgent = e.target.value || null
                setSelectedAgent(newAgent)
                setSelectedThread(undefined) // Clear thread when changing agent
                if (onAgentChange) {
                  onAgentChange(newAgent)
                }
              }}
              className="bg-cursor-input-bg text-cursor-text px-2 py-1 rounded text-xs border border-cursor-border cursor-input"
              style={{ fontSize: '12px' }}
              title={selectedAgent ? `Sending direct messages to ${selectedAgent}` : 'Chat with all agents (select an agent for direct messages)'}
            >
              <option value="">💬 Chat with All Agents</option>
              {discoveredAgents.length > 0 ? (
                discoveredAgents.map((agent) => (
                  <option key={agent} value={agent}>
                    📩 Direct: {agent}
                  </option>
                ))
              ) : (
                <>
                  {/* Fallback to known agents if none discovered yet */}
                  <option value="Aether">📩 Direct: Aether</option>
                  <option value="Lexicon">📩 Direct: Lexicon</option>
                  <option value="Sonnet">📩 Direct: Sonnet</option>
                  <option value="Scribe">📩 Direct: Scribe</option>
                  <option value="Solo">📩 Direct: Solo</option>
                  <option value="Atlas">📩 Direct: Atlas</option>
                </>
              )}
            </select>
            {/* Start Discussion Button */}
            <button
              onClick={() => setShowStartDiscussion(!showStartDiscussion)}
              className="px-2 py-1 bg-cursor-status-bar hover:bg-cursor-status-bar/80 rounded text-xs flex items-center gap-1 cursor-button"
              style={{ fontSize: '12px' }}
            >
              <MessageCircle className="w-3.5 h-3.5" />
              Start Discussion
            </button>
            {/* Refresh Button */}
            <button
              onClick={() => fetchMessages()}
              disabled={loading}
              className="p-1.5 bg-cursor-hover hover:bg-cursor-active rounded disabled:opacity-50 cursor-button"
              title="Refresh messages"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
        {/* Search Bar */}
        <div className="px-2 pb-1">
          <div className="relative">
            <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-3.5 h-3.5 text-cursor-text-secondary" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search messages..."
              className="w-full bg-cursor-input-bg text-cursor-text px-8 py-1 rounded border border-cursor-border text-xs focus:outline-none focus:border-cursor-status-bar cursor-input"
              style={{ fontSize: '12px' }}
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 text-cursor-text-secondary hover:text-cursor-text cursor-button"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
          {searchQuery && (
            <div className="mt-1 text-xs text-cursor-text-secondary">
              Found {messages.length} message{messages.length !== 1 ? 's' : ''}
            </div>
          )}
        </div>
        {/* Start Discussion Form */}
        {showStartDiscussion && (
          <div className="mt-2 p-2 bg-cursor-sidebar rounded border border-cursor-border">
            <div className="flex flex-col gap-1.5">
              <input
                type="text"
                value={discussionTopic}
                onChange={(e) => setDiscussionTopic(e.target.value)}
                placeholder="Discussion topic..."
                className="bg-cursor-input-bg text-cursor-text px-2 py-1 rounded text-xs border border-cursor-border cursor-input"
                style={{ fontSize: '12px' }}
              />
              <div className="flex gap-1.5">
                <button
                  onClick={handleStartDiscussion}
                  disabled={!discussionTopic.trim() || !inputText.trim() || !selectedAgent}
                  className="px-2 py-1 bg-green-600 hover:bg-green-700 disabled:bg-cursor-input-bg disabled:cursor-not-allowed rounded text-xs cursor-button"
                  style={{ fontSize: '12px' }}
                >
                  Start
                </button>
                <button
                  onClick={() => {
                    setShowStartDiscussion(false)
                    setDiscussionTopic('')
                  }}
                  className="px-2 py-1 bg-cursor-hover hover:bg-cursor-active rounded text-xs cursor-button"
                  style={{ fontSize: '12px' }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
        {/* Error Display */}
        {(error || localError) && (
          <div className="mt-2 p-3 bg-red-900/30 border border-red-700 rounded-lg text-sm text-red-300 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold mb-1">Error:</div>
              <div>{error || localError}</div>
            </div>
          </div>
        )}
        
        {/* Info Display - Connection Status */}
        {discoveredAgents.length === 0 && !loading && (
          <div className="mt-2 p-3 bg-blue-900/20 border border-blue-700/50 rounded-lg text-sm text-blue-300">
            <div className="font-semibold mb-1">💡 No agents discovered yet</div>
            <div>Don't worry! You can still send messages. Agents will appear automatically when they respond via MCP.</div>
            <div className="mt-2 text-xs opacity-75">Make sure Cursor is open with the Extension installed for full functionality.</div>
          </div>
        )}
        
        {/* Show selected agent indicator */}
        {selectedAgent && (
          <div className="mt-2 p-2 bg-purple-900/20 border border-purple-700/50 rounded-lg text-xs text-purple-300">
            📩 Sending direct messages to <span className="font-semibold">{selectedAgent}</span>. Select "Chat with All Agents" to broadcast.
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2 cursor-scrollbar">
        {/* Debug: Show message count */}
        {messages.length > 0 && (
          <div className="mb-1 p-1.5 bg-cursor-status-bar/20 border border-cursor-status-bar/50 rounded text-xs text-cursor-status-bar">
            📊 Debug: {messages.length} message{messages.length !== 1 ? 's' : ''} ready to display
          </div>
        )}
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-2 ${
              message.type === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.type !== 'user' && (
              <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
                message.agentName === 'Aether' ? 'bg-purple-600' :
                message.agentName === 'Lexicon' ? 'bg-cursor-status-bar' :
                message.agentName === 'Sonnet' ? 'bg-green-600' :
                message.agentName === 'Scribe' ? 'bg-yellow-600' :
                message.agentName === 'Solo' ? 'bg-orange-600' :
                'bg-cursor-input-bg'
              }`}>
                <Bot className="w-3.5 h-3.5" />
              </div>
            )}
            <div
              className={`max-w-[70%] rounded p-2 ${
                message.type === 'user'
                  ? 'bg-cursor-status-bar text-white'
                  : message.type === 'system'
                  ? 'bg-cursor-sidebar text-cursor-text-secondary'
                  : 'bg-cursor-sidebar text-cursor-text'
              }`}
              style={{ fontSize: '12px' }}
            >
              {message.type !== 'user' && (
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-semibold" style={{ fontSize: '11px' }}>{message.agentName}</span>
                    {message.messageType && message.messageType !== 'discussion' && (
                      <span className="text-xs px-1 py-0.5 bg-cursor-input-bg rounded" style={{ fontSize: '10px' }}>
                        {message.messageType.replace('_', ' ')}
                      </span>
                    )}
                  </div>
                  {message.priority && message.priority !== 'medium' && (
                    <span className={`text-xs px-1 py-0.5 rounded font-medium ${
                      message.priority === 'urgent' ? 'bg-red-900/50 text-red-300' :
                      message.priority === 'high' ? 'bg-orange-900/50 text-orange-300' :
                      'bg-cursor-status-bar/50 text-cursor-status-bar'
                    }`} style={{ fontSize: '10px' }}>
                      {message.priority.toUpperCase()}
                    </span>
                  )}
                </div>
              )}
              <div className="text-xs whitespace-pre-wrap break-words" style={{ fontSize: '12px', lineHeight: '1.4' }}>{message.content}</div>
              <div className="flex items-center justify-between mt-1 pt-1 border-t border-cursor-border/50">
                <div className="flex items-center gap-1.5 text-xs opacity-70" style={{ fontSize: '10px' }}>
                  <span>{message.timestamp.toLocaleTimeString()}</span>
                  {message.threadId && (
                    <span className="text-cursor-status-bar" title={`Thread ID: ${message.threadId}`}>
                      • Thread: {message.threadId.slice(-6)}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-1.5">
                  {message.messageType && (
                    <span className="text-xs px-1 py-0.5 bg-cursor-input-bg rounded opacity-70" style={{ fontSize: '10px' }}>
                      {message.messageType}
                    </span>
                  )}
                  {message.priority === 'urgent' && (
                    <span className="text-xs px-1 py-0.5 bg-red-900/50 text-red-300 rounded font-semibold" style={{ fontSize: '10px' }}>
                      ⚠️ URGENT
                    </span>
                  )}
                </div>
              </div>
            </div>
            {message.type === 'user' && (
              <div className="w-7 h-7 rounded-full bg-green-600 flex items-center justify-center flex-shrink-0">
                <User className="w-3.5 h-3.5" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex gap-2 justify-start">
            <div className="w-7 h-7 rounded-full bg-cursor-status-bar flex items-center justify-center">
              <Bot className="w-3.5 h-3.5" />
            </div>
            <div className="bg-cursor-sidebar rounded p-2">
              <Loader className="w-3.5 h-3.5 animate-spin" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-2 border-t border-cursor-border">
        <div className="flex gap-1.5">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                handleSend()
              }
            }}
            placeholder={
              selectedAgent
                ? `Message ${selectedAgent} (or leave empty to chat with everyone)...`
                : selectedThread
                ? 'Reply in thread...'
                : 'Type a message to all agents and press Enter...'
            }
            className="flex-1 bg-cursor-input-bg text-cursor-text px-2 py-1 rounded border border-cursor-border focus:outline-none focus:border-cursor-status-bar cursor-input"
            style={{ fontSize: '12px' }}
          />
          <button
            onClick={handleSend}
            disabled={!inputText.trim() || loading}
            className="px-2 py-1 bg-cursor-status-bar hover:bg-cursor-status-bar/80 disabled:bg-cursor-input-bg disabled:cursor-not-allowed rounded flex items-center gap-1.5 cursor-button transition-colors"
            style={{ fontSize: '12px' }}
            title={inputText.trim() ? `Send message to ${selectedAgent || 'all agents'} (or press Enter)` : 'Type a message'}
          >
            {loading ? (
              <Loader className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Send className="w-3.5 h-3.5" />
            )}
            Send
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInterfaceTab

