/**
 * AI Agent Chat Component
 * Enhanced chat interface for AI agents with real-time collaboration
 */

import React, { useState, useEffect, useRef } from 'react'
import { Send, Bot, Sparkles, Code, MessageSquare, Users, Zap } from 'lucide-react'
import { aiAgentService, AIAgent, AgentMessage, AgentResponse } from '../lib/ai-agent-service'

interface AIAgentChatProps {
  agentId: string
  title: string
  subtitle: string
  icon: React.ReactNode
  className?: string
}

export const AIAgentChat: React.FC<AIAgentChatProps> = ({
  agentId,
  title,
  subtitle,
  icon,
  className = ''
}) => {
  const [messages, setMessages] = useState<AgentMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [agent, setAgent] = useState<AIAgent | null>(null)
  const [collaborationMode, setCollaborationMode] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const agentData = aiAgentService.getAgent(agentId)
    setAgent(agentData || null)
    
    // Load message history
    const history = aiAgentService.getMessageHistory(agentId)
    setMessages(history)
  }, [agentId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !agent) return

    const userMessage: AgentMessage = {
      id: `user_${Date.now()}`,
      from: 'user',
      to: agentId,
      content: inputValue,
      timestamp: new Date(),
      type: 'request',
      metadata: { isUser: true }
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsTyping(true)

    try {
      // Send message to agent
      const response = await aiAgentService.sendMessage('user', agentId, inputValue)
      
      // Add agent response to messages
      const agentMessage: AgentMessage = {
        id: `agent_${Date.now()}`,
        from: agentId,
        to: 'user',
        content: response.content,
        timestamp: new Date(),
        type: 'response',
        metadata: {
          confidence: response.confidence,
          suggestions: response.suggestions,
          followUpQuestions: response.followUpQuestions,
          ...response.metadata
        }
      }

      setMessages(prev => [...prev, agentMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: AgentMessage = {
        id: `error_${Date.now()}`,
        from: 'system',
        to: 'user',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        type: 'notification',
        metadata: { isError: true }
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const getMessageIcon = (message: AgentMessage) => {
    if (message.metadata?.isUser) return <Users className="w-4 h-4" />
    if (message.metadata?.isError) return <Zap className="w-4 h-4 text-red-400" />
    if (message.metadata?.provider === 'gemini') return <Sparkles className="w-4 h-4 text-blue-400" />
    if (message.metadata?.provider === 'cerebras') return <Zap className="w-4 h-4 text-purple-400" />
    return <Bot className="w-4 h-4" />
  }

  const getMessageStyle = (message: AgentMessage) => {
    if (message.metadata?.isUser) {
      return 'bg-blue-600 text-white ml-auto'
    }
    if (message.metadata?.isError) {
      return 'bg-red-900 text-red-100 border border-red-700'
    }
    if (message.metadata?.provider === 'gemini') {
      return 'bg-blue-900 text-blue-100 border border-blue-700'
    }
    if (message.metadata?.provider === 'cerebras') {
      return 'bg-purple-900 text-purple-100 border border-purple-700'
    }
    return 'bg-gray-700 text-gray-100'
  }

  if (!agent) {
    return (
      <div className={`h-full bg-gray-800 flex items-center justify-center text-gray-400 ${className}`}>
        <div className="text-center">
          <Bot className="w-8 h-8 mx-auto mb-2" />
          <p>Agent not found</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`h-full bg-gray-800 flex flex-col ${className}`}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 flex items-center gap-3">
        <div className="flex items-center gap-2">
          {icon}
          <div>
            <div className="text-white text-sm font-semibold flex items-center gap-2">
              {title}
              {agent.isActive && (
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              )}
            </div>
            <div className="text-xs text-gray-500">{subtitle}</div>
          </div>
        </div>
        
        <div className="ml-auto flex items-center gap-2">
          <div className="text-xs text-gray-400">
            {agent.provider === 'gemini' ? '🤖 Gemini' : '⚡ Cerebras'}
          </div>
          <button
            onClick={() => setCollaborationMode(!collaborationMode)}
            className={`p-1 rounded text-xs ${
              collaborationMode 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-700 text-gray-400 hover:text-white'
            }`}
            title="Toggle collaboration mode"
          >
            <MessageSquare className="w-3 h-3" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 ? (
          <div className="text-center text-gray-400 py-8">
            <Bot className="w-8 h-8 mx-auto mb-2" />
            <p className="text-sm">Start a conversation with {agent.name}</p>
            <p className="text-xs mt-1">Specialized in: {agent.capabilities.slice(0, 2).join(', ')}</p>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className="flex gap-2">
              <div className="flex-shrink-0 w-6 h-6 rounded-full bg-gray-700 flex items-center justify-center">
                {getMessageIcon(message)}
              </div>
              <div className="flex-1">
                <div className={`p-3 rounded-lg max-w-xs ${getMessageStyle(message)}`}>
                  <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                  <div className="text-xs opacity-70 mt-1">
                    {formatTimestamp(message.timestamp)}
                    {message.metadata?.confidence && (
                      <span className="ml-2">
                        ({Math.round(message.metadata.confidence * 100)}% confidence)
                      </span>
                    )}
                  </div>
                </div>
                
                {/* Suggestions */}
                {message.metadata?.suggestions && message.metadata.suggestions.length > 0 && (
                  <div className="mt-2 space-y-1">
                    <div className="text-xs text-gray-400">Suggestions:</div>
                    {message.metadata.suggestions.slice(0, 3).map((suggestion: string, index: number) => (
                      <div key={index} className="text-xs bg-gray-700 px-2 py-1 rounded">
                        • {suggestion}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        
        {isTyping && (
          <div className="flex gap-2">
            <div className="flex-shrink-0 w-6 h-6 rounded-full bg-gray-700 flex items-center justify-center">
              {getMessageIcon({} as AgentMessage)}
            </div>
            <div className="bg-gray-700 p-3 rounded-lg">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Ask ${agent.name}...`}
            className="flex-1 bg-gray-700 text-white text-sm px-3 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isTyping}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isTyping}
            className="bg-blue-600 text-white p-2 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        
        {/* Agent capabilities hint */}
        <div className="mt-2 text-xs text-gray-500">
          Capabilities: {agent.capabilities.slice(0, 3).join(' • ')}
        </div>
      </div>
    </div>
  )
}
