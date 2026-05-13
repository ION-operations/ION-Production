/**
 * ChatMessage Component
 * Shared message component with agent identification and cross-agent communication
 */

import React from 'react'
import { Code, Sparkles, Bot, User, MessageSquare, ArrowRight, Clock, CheckCircle, AlertTriangle } from 'lucide-react'

export interface ChatMessage {
  id: string
  content: string
  role: 'user' | 'assistant' | 'system'
  agent?: 'coding' | 'planning' | 'system'
  timestamp: Date
  type: 'message' | 'code' | 'suggestion' | 'question' | 'handoff' | 'review' | 'consensus'
  metadata?: {
    relatedFile?: string
    conversationId?: string
    taskId?: string
    confidence?: number
    codeBlock?: {
      language: string
      content: string
    }
    crossAgent?: {
      from: 'coding' | 'planning'
      to: 'coding' | 'planning'
      requiresResponse: boolean
    }
  }
}

interface ChatMessageProps {
  message: ChatMessage
  onCodeClick?: (code: string, language: string) => void
  onFileClick?: (filePath: string) => void
  onApplySuggestion?: (suggestion: string) => void
  onCrossAgentResponse?: (messageId: string, response: string) => void
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  onCodeClick,
  onFileClick,
  onApplySuggestion,
  onCrossAgentResponse
}) => {
  // Get agent icon and color
  const getAgentIcon = (agent?: string) => {
    switch (agent) {
      case 'coding': return <Code className="w-4 h-4 text-blue-400" />
      case 'planning': return <Sparkles className="w-4 h-4 text-purple-400" />
      case 'system': return <Bot className="w-4 h-4 text-gray-400" />
      default: return <User className="w-4 h-4 text-gray-400" />
    }
  }

  // Get agent color
  const getAgentColor = (agent?: string) => {
    switch (agent) {
      case 'coding': return 'text-blue-400'
      case 'planning': return 'text-purple-400'
      case 'system': return 'text-gray-400'
      default: return 'text-gray-400'
    }
  }

  // Get type icon
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'code': return <Code className="w-3 h-3" />
      case 'suggestion': return <CheckCircle className="w-3 h-3" />
      case 'question': return <MessageSquare className="w-3 h-3" />
      case 'handoff': return <ArrowRight className="w-3 h-3" />
      case 'review': return <AlertTriangle className="w-3 h-3" />
      case 'consensus': return <CheckCircle className="w-3 h-3" />
      default: return <MessageSquare className="w-3 h-3" />
    }
  }

  // Get type color
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'code': return 'text-blue-300'
      case 'suggestion': return 'text-green-300'
      case 'question': return 'text-yellow-300'
      case 'handoff': return 'text-cyan-300'
      case 'review': return 'text-orange-300'
      case 'consensus': return 'text-green-300'
      default: return 'text-gray-300'
    }
  }

  // Render code block
  const renderCodeBlock = (codeBlock: { language: string; content: string }) => {
    return (
      <div className="mt-2 bg-gray-800 rounded-lg overflow-hidden">
        <div className="flex items-center justify-between px-3 py-2 bg-gray-700 border-b border-gray-600">
          <span className="text-xs text-gray-300">{codeBlock.language}</span>
          <button
            onClick={() => onCodeClick?.(codeBlock.content, codeBlock.language)}
            className="text-xs text-blue-400 hover:text-blue-300"
          >
            Copy & Apply
          </button>
        </div>
        <pre className="p-3 text-sm text-gray-100 overflow-x-auto">
          <code>{codeBlock.content}</code>
        </pre>
      </div>
    )
  }

  // Render cross-agent communication
  const renderCrossAgent = (crossAgent: { from: string; to: string; requiresResponse: boolean }) => {
    return (
      <div className="mt-2 p-2 bg-gray-700/50 rounded border-l-2 border-cyan-400">
        <div className="flex items-center gap-2 text-xs text-cyan-300">
          <ArrowRight className="w-3 h-3" />
          <span>Cross-agent: {crossAgent.from} → {crossAgent.to}</span>
          {crossAgent.requiresResponse && (
            <span className="text-yellow-300">(Response needed)</span>
          )}
        </div>
        {crossAgent.requiresResponse && (
          <button
            onClick={() => onCrossAgentResponse?.(message.id, '')}
            className="mt-1 text-xs text-blue-400 hover:text-blue-300"
          >
            Respond to {crossAgent.to} agent
          </button>
        )}
      </div>
    )
  }

  // Render file reference
  const renderFileReference = (filePath: string) => {
    return (
      <div className="mt-2 p-2 bg-gray-700/30 rounded border-l-2 border-blue-400">
        <div className="flex items-center gap-2 text-xs text-blue-300">
          <Code className="w-3 h-3" />
          <button
            onClick={() => onFileClick?.(filePath)}
            className="hover:text-blue-200 underline"
          >
            {filePath}
          </button>
        </div>
      </div>
    )
  }

  // Render suggestion actions
  const renderSuggestionActions = () => {
    if (message.type !== 'suggestion') return null

    return (
      <div className="mt-2 flex gap-2">
        <button
          onClick={() => onApplySuggestion?.(message.content)}
          className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-xs rounded"
        >
          Apply Suggestion
        </button>
        <button className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white text-xs rounded">
          Modify
        </button>
        <button className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white text-xs rounded">
          Reject
        </button>
      </div>
    )
  }

  return (
    <div className={`flex gap-3 p-3 ${
      message.role === 'user' ? 'justify-end' : 'justify-start'
    }`}>
      {message.role !== 'user' && (
        <div className="flex-shrink-0">
          {getAgentIcon(message.agent)}
        </div>
      )}
      
      <div className={`max-w-[80%] ${
        message.role === 'user' ? 'order-first' : ''
      }`}>
        {/* Message Header */}
        <div className="flex items-center gap-2 mb-1">
          {message.role === 'user' ? (
            <User className="w-4 h-4 text-gray-400" />
          ) : (
            getAgentIcon(message.agent)
          )}
          
          <span className={`text-sm font-medium ${
            message.role === 'user' ? 'text-white' : getAgentColor(message.agent)
          }`}>
            {message.role === 'user' ? 'You' : 
             message.agent === 'coding' ? 'AI Coding Agent' :
             message.agent === 'planning' ? 'AI Planning Agent' :
             'System'}
          </span>
          
          <div className="flex items-center gap-1">
            <div className={`text-xs px-1 py-0.5 rounded ${
              message.type === 'code' ? 'bg-blue-900/30 text-blue-300' :
              message.type === 'suggestion' ? 'bg-green-900/30 text-green-300' :
              message.type === 'question' ? 'bg-yellow-900/30 text-yellow-300' :
              message.type === 'handoff' ? 'bg-cyan-900/30 text-cyan-300' :
              message.type === 'review' ? 'bg-orange-900/30 text-orange-300' :
              message.type === 'consensus' ? 'bg-green-900/30 text-green-300' :
              'bg-gray-900/30 text-gray-300'
            }`}>
              {getTypeIcon(message.type)}
              <span className="ml-1">{message.type}</span>
            </div>
          </div>
          
          <span className="text-xs text-gray-400">
            {message.timestamp.toLocaleTimeString()}
          </span>
          
          {message.metadata?.confidence && (
            <span className="text-xs text-gray-500">
              {(message.metadata.confidence * 100).toFixed(0)}% confidence
            </span>
          )}
        </div>

        {/* Message Content */}
        <div className={`p-3 rounded-lg ${
          message.role === 'user' 
            ? 'bg-blue-600 text-white' 
            : message.type === 'suggestion'
            ? 'bg-green-900/20 text-green-100 border border-green-700'
            : message.type === 'code'
            ? 'bg-blue-900/20 text-blue-100 border border-blue-700'
            : 'bg-gray-700 text-white'
        }`}>
          <div className="text-sm whitespace-pre-wrap">
            {message.content}
          </div>
          
          {/* Code Block */}
          {message.metadata?.codeBlock && renderCodeBlock(message.metadata.codeBlock)}
          
          {/* File Reference */}
          {message.metadata?.relatedFile && renderFileReference(message.metadata.relatedFile)}
          
          {/* Cross-Agent Communication */}
          {message.metadata?.crossAgent && renderCrossAgent(message.metadata.crossAgent)}
          
          {/* Suggestion Actions */}
          {renderSuggestionActions()}
        </div>
      </div>
    </div>
  )
}
