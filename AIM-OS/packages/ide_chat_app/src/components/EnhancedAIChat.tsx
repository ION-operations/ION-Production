/**
 * Enhanced AI Chat Component
 * Multi-agent AI chat with Gemini and Cerebras integration
 */

import React, { useState, useEffect, useRef } from 'react'
import { Send, Bot, User, Zap, Brain, Code, Settings, Loader2 } from 'lucide-react'
import { enhancedAIService, AIRequest, AIResponse, AIAgent } from '../lib/ai-service-enhanced'
import { performanceMonitor } from '../lib/performance-monitor'

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  agent?: string
  provider?: string
  confidence?: number
  timestamp: Date
  metadata?: any
}

interface EnhancedAIChatProps {
  conversationId?: string
  initialAgent?: string
  onAgentChange?: (agent: string) => void
}

export const EnhancedAIChat: React.FC<EnhancedAIChatProps> = ({
  conversationId = 'default',
  initialAgent = 'coding',
  onAgentChange
}) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [selectedAgent, setSelectedAgent] = useState(initialAgent)
  const [isLoading, setIsLoading] = useState(false)
  const [agents, setAgents] = useState<AIAgent[]>([])
  const [showAgentSelector, setShowAgentSelector] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Initialize agents
  useEffect(() => {
    const availableAgents = enhancedAIService.getActiveAgents()
    setAgents(availableAgents)
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Handle agent change
  const handleAgentChange = (agentId: string) => {
    setSelectedAgent(agentId)
    onAgentChange?.(agentId)
    
    // Add system message about agent change
    const agent = agents.find(a => a.id === agentId)
    if (agent) {
      addMessage({
        content: `Switched to ${agent.name} - ${agent.description}`,
        role: 'assistant',
        agent: agentId,
        timestamp: new Date(),
        metadata: { type: 'agent_change' }
      })
    }
  }

  // Add message to conversation
  const addMessage = (message: Omit<Message, 'id'>) => {
    const newMessage: Message = {
      id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      content: message.content,
      role: message.role,
      agent: message.agent,
      provider: message.provider,
      confidence: message.confidence,
      timestamp: message.timestamp,
      metadata: message.metadata
    }
    setMessages(prev => [...prev, newMessage])
    return newMessage
  }

  // Handle send message
  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setIsLoading(true)

    // Add user message
    addMessage({
      content: userMessage,
      role: 'user',
      timestamp: new Date()
    })

    try {
      // Prepare AI request
      const request: AIRequest = {
        prompt: userMessage,
        provider: selectedAgent as any,
        options: {
          temperature: 0.7,
          maxTokens: 2048
        }
      }

      // Generate response
      const response = await enhancedAIService.generateAgentResponse(selectedAgent, request)
      
      // Add AI response
      addMessage({
        content: response.content,
        role: 'assistant',
        agent: selectedAgent,
        provider: response.provider,
        confidence: response.metadata.confidence,
        timestamp: new Date(),
        metadata: {
          model: response.model,
          responseTime: response.metadata.responseTime,
          usage: response.usage
        }
      })

      // Track performance
      performanceMonitor.recordAIMOSOperation('chat_message_processed', response.metadata.responseTime)

    } catch (error) {
      console.error('Failed to generate response:', error)
      addMessage({
        content: 'Sorry, I encountered an error while processing your request. Please try again.',
        role: 'assistant',
        agent: selectedAgent,
        timestamp: new Date(),
        metadata: { type: 'error', error: (error as Error).message }
      })
    } finally {
      setIsLoading(false)
    }
  }

  // Handle key press
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Get agent icon
  const getAgentIcon = (agentId: string) => {
    switch (agentId) {
      case 'coding': return <Code className="w-4 h-4" />
      case 'planning': return <Brain className="w-4 h-4" />
      case 'research': return <Zap className="w-4 h-4" />
      default: return <Bot className="w-4 h-4" />
    }
  }

  // Get agent color
  const getAgentColor = (agentId: string) => {
    switch (agentId) {
      case 'coding': return 'text-green-400'
      case 'planning': return 'text-blue-400'
      case 'research': return 'text-purple-400'
      default: return 'text-gray-400'
    }
  }

  return (
    <div className="h-full flex flex-col bg-gray-800">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-blue-400" />
          <div>
            <div className="text-white text-sm font-semibold">AI Chat</div>
            <div className="text-xs text-gray-500">Enhanced with Gemini & Cerebras</div>
          </div>
        </div>
        
        {/* Agent Selector */}
        <div className="relative">
          <button
            onClick={() => setShowAgentSelector(!showAgentSelector)}
            className="flex items-center gap-2 px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-300 transition-colors"
          >
            {getAgentIcon(selectedAgent)}
            <span>{agents.find(a => a.id === selectedAgent)?.name || 'Select Agent'}</span>
            <Settings className="w-3 h-3" />
          </button>
          
          {showAgentSelector && (
            <div className="absolute right-0 top-full mt-1 w-64 bg-gray-700 rounded-lg shadow-lg border border-gray-600 z-10">
              <div className="p-2">
                <div className="text-xs text-gray-400 mb-2">Select AI Agent</div>
                {agents.map(agent => (
                  <button
                    key={agent.id}
                    onClick={() => {
                      handleAgentChange(agent.id)
                      setShowAgentSelector(false)
                    }}
                    className={`w-full text-left p-2 rounded hover:bg-gray-600 transition-colors ${
                      selectedAgent === agent.id ? 'bg-gray-600' : ''
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <div className={getAgentColor(agent.id)}>
                        {getAgentIcon(agent.id)}
                      </div>
                      <div>
                        <div className="text-sm font-medium text-white">{agent.name}</div>
                        <div className="text-xs text-gray-400">{agent.description}</div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-400 text-sm py-8">
            <Bot className="w-12 h-12 mx-auto mb-4 text-gray-600" />
            <div>Start a conversation with your AI assistant</div>
            <div className="text-xs mt-2">Select an agent above to get specialized help</div>
          </div>
        ) : (
          messages.map(message => (
            <div
              key={message.id}
              className={`flex gap-3 ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.role === 'assistant' && (
                <div className={`flex-shrink-0 w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center ${getAgentColor(message.agent || '')}`}>
                  {getAgentIcon(message.agent || '')}
                </div>
              )}
              
              <div className={`max-w-[80%] ${message.role === 'user' ? 'order-first' : ''}`}>
                <div className={`rounded-lg p-3 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-100'
                }`}>
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  
                  {/* Message metadata */}
                  {message.metadata && (
                    <div className="mt-2 text-xs opacity-70">
                      {message.provider && (
                        <span className="mr-2">via {message.provider}</span>
                      )}
                      {message.confidence && (
                        <span className="mr-2">confidence: {(message.confidence * 100).toFixed(0)}%</span>
                      )}
                      {message.metadata.responseTime && (
                        <span>{message.metadata.responseTime}ms</span>
                      )}
                    </div>
                  )}
                </div>
                
                {/* Agent info for assistant messages */}
                {message.role === 'assistant' && message.agent && (
                  <div className="text-xs text-gray-500 mt-1">
                    {agents.find(a => a.id === message.agent)?.name}
                  </div>
                )}
              </div>
              
              {message.role === 'user' && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
              )}
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
              <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
            </div>
            <div className="bg-gray-700 rounded-lg p-3 text-gray-300">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Thinking...</span>
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
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={isLoading}
            className="flex-1 bg-gray-700 text-white px-3 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
