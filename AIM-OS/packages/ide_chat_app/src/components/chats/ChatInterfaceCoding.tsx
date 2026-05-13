/**
 * Chat Interface for Coding Agent
 * Left drawer - Technical, implementation-focused AI agent
 */

import React, { useState, useRef, useEffect } from 'react'
import { 
  Code, 
  Send, 
  Bot, 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  Zap,
  Play,
  Square,
  RefreshCw,
  Settings,
  GitBranch,
  Bug,
  Wrench,
  TestTube
} from 'lucide-react'
import { ChatMessage } from './ChatMessage'
import { useCodingAgent } from '../../contexts/CodingAgentContext'
import { crossChatBridge, createCrossAgentMessage } from '../../lib/cross-chat-bridge'
import { enhancedAIService } from '../../lib/ai-service-enhanced'
import { performanceMonitor } from '../../lib/performance-monitor'

interface ChatInterfaceCodingProps {
  className?: string
}

export const ChatInterfaceCoding: React.FC<ChatInterfaceCodingProps> = ({ className = '' }) => {
  const { state, addMessage, setTyping, setErrorContext, clearErrorContext } = useCodingAgent()
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showQuickActions, setShowQuickActions] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [state.messages])

  // Subscribe to cross-agent messages
  useEffect(() => {
    const unsubscribe = crossChatBridge.subscribe('coding', (crossMessage) => {
      const chatMessage = crossChatBridge.convertToChatMessage(crossMessage)
      addMessage(chatMessage)
    })

    return unsubscribe
  }, [addMessage])

  // Handle send message
  const handleSendMessage = async () => {
    if (inputValue.trim() === '' || isLoading) return

    const userMessage = inputValue.trim()
    setInputValue('')
    setIsLoading(true)
    setTyping(true)

    // Add user message
    addMessage({
      content: userMessage,
      role: 'user',
      agent: 'coding',
      type: 'message'
    })

    try {
      // Generate AI response
      const response = await enhancedAIService.generateAgentResponse('coding', {
        prompt: userMessage,
        provider: 'coding' as any
      })

      // Add AI response
      addMessage({
        content: response.content,
        role: 'assistant',
        agent: 'coding',
        type: 'message',
        metadata: {
          confidence: response.metadata.confidence,
          codeBlock: response.content.includes('```') ? {
            language: 'typescript',
            content: response.content
          } : undefined
        }
      })

      // Track performance
      performanceMonitor.recordAIMOSOperation('coding_agent_response', response.metadata.responseTime)

    } catch (error) {
      console.error('Failed to generate response:', error)
      
      // Set error context
      setErrorContext({
        message: (error as Error).message,
        file: state.currentFile || 'unknown',
        line: state.cursorPosition?.line || 0,
        column: state.cursorPosition?.column || 0,
        type: 'error'
      })

      addMessage({
        content: `I encountered an error: ${(error as Error).message}. Let me help you debug this.`,
        role: 'assistant',
        agent: 'coding',
        type: 'message',
        metadata: {
          confidence: 0.3
        }
      })
    } finally {
      setIsLoading(false)
      setTyping(false)
    }
  }

  // Handle quick actions
  const handleQuickAction = async (action: string) => {
    const actionPrompts: Record<string, string> = {
      'generate': 'Generate code for the current context',
      'debug': 'Help debug the current error',
      'refactor': 'Refactor the current code for better performance',
      'test': 'Generate tests for the current code',
      'optimize': 'Optimize the current code',
      'explain': 'Explain the current code'
    }

    const prompt = actionPrompts[action] || action
    setInputValue(prompt)
    setShowQuickActions(false)
  }

  // Handle code click
  const handleCodeClick = (code: string, language: string) => {
    // In a real implementation, this would apply the code to the editor
    console.log('Applying code:', code, 'Language:', language)
    addMessage({
      content: `Code applied successfully! The ${language} code has been inserted into your editor.`,
      role: 'assistant',
      agent: 'coding',
      type: 'suggestion'
    })
  }

  // Handle file click
  const handleFileClick = (filePath: string) => {
    // In a real implementation, this would open the file
    console.log('Opening file:', filePath)
    addMessage({
      content: `Opening file: ${filePath}`,
      role: 'assistant',
      agent: 'coding',
      type: 'message'
    })
  }

  // Handle apply suggestion
  const handleApplySuggestion = (suggestion: string) => {
    // In a real implementation, this would apply the suggestion
    console.log('Applying suggestion:', suggestion)
    addMessage({
      content: `Suggestion applied: ${suggestion}`,
      role: 'assistant',
      agent: 'coding',
      type: 'suggestion'
    })
  }

  // Handle cross-agent response
  const handleCrossAgentResponse = (messageId: string, response: string) => {
    // Send response back to planning agent
    crossChatBridge.sendMessage(createCrossAgentMessage(
      'coding',
      'planning',
      'consensus',
      response,
      { conversationId: messageId },
      true
    ))
  }

  // Quick action buttons
  const quickActions = [
    { id: 'generate', label: 'Generate', icon: <Code className="w-4 h-4" /> },
    { id: 'debug', label: 'Debug', icon: <Bug className="w-4 h-4" /> },
    { id: 'refactor', label: 'Refactor', icon: <Wrench className="w-4 h-4" /> },
    { id: 'test', label: 'Test', icon: <TestTube className="w-4 h-4" /> },
    { id: 'optimize', label: 'Optimize', icon: <Zap className="w-4 h-4" /> },
    { id: 'explain', label: 'Explain', icon: <FileText className="w-4 h-4" /> }
  ]

  return (
    <div className={`h-full bg-gray-800 flex flex-col ${className}`}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Code className="w-5 h-5 text-blue-400" />
            <div>
              <div className="text-white text-sm font-semibold">AI Coding Agent</div>
              <div className="text-xs text-gray-500">
                Technical implementation & code generation
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${state.isTyping ? 'bg-blue-500 animate-pulse' : 'bg-green-500'}`} />
            <span className="text-xs text-gray-400">
              {state.isTyping ? 'Typing...' : 'Ready'}
            </span>
            
            <button
              onClick={() => setShowQuickActions(!showQuickActions)}
              className="p-1 hover:bg-gray-700 rounded"
            >
              <Settings className="w-4 h-4 text-gray-400" />
            </button>
          </div>
        </div>

        {/* Context Info */}
        {state.currentFile && (
          <div className="mt-2 text-xs text-gray-400">
            <FileText className="w-3 h-3 inline mr-1" />
            {state.currentFile}
            {state.cursorPosition && (
              <span className="ml-2">
                Line {state.cursorPosition.line}, Col {state.cursorPosition.column}
              </span>
            )}
          </div>
        )}

        {/* Error Context */}
        {state.errorContext && (
          <div className="mt-2 p-2 bg-red-900/20 border border-red-700 rounded">
            <div className="flex items-center gap-2 text-xs text-red-300">
              <AlertTriangle className="w-3 h-3" />
              <span>{state.errorContext.message}</span>
              <button
                onClick={clearErrorContext}
                className="ml-auto text-red-400 hover:text-red-300"
              >
                ×
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      {showQuickActions && (
        <div className="px-4 py-2 border-b border-gray-700">
          <div className="text-xs text-gray-400 mb-2">Quick Actions</div>
          <div className="grid grid-cols-3 gap-2">
            {quickActions.map(action => (
              <button
                key={action.id}
                onClick={() => handleQuickAction(action.id)}
                className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded"
              >
                {action.icon}
                {action.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-3">
          {state.messages.map(message => (
            <ChatMessage
              key={message.id}
              message={message}
              onCodeClick={handleCodeClick}
              onFileClick={handleFileClick}
              onApplySuggestion={handleApplySuggestion}
              onCrossAgentResponse={handleCrossAgentResponse}
            />
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask me to generate, debug, refactor, or explain code..."
            className="flex-1 bg-gray-700 text-white text-sm rounded p-3 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows={2}
            disabled={isLoading}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSendMessage()
              }
            }}
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || inputValue.trim() === ''}
            className="p-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded"
          >
            {isLoading ? (
              <RefreshCw className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
        
        {/* Status */}
        <div className="mt-2 text-xs text-gray-400">
          {state.openTabs.length > 0 && (
            <span className="mr-4">
              {state.openTabs.length} tab{state.openTabs.length !== 1 ? 's' : ''} open
            </span>
          )}
          {state.context.gitStatus !== 'clean' && (
            <span className="mr-4">
              Git: {state.context.gitStatus}
            </span>
          )}
          <span>
            Last activity: {state.lastActivity.toLocaleTimeString()}
          </span>
        </div>
      </div>
    </div>
  )
}
