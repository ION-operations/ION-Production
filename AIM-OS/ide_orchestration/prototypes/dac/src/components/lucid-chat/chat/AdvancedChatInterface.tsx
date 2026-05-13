/**
 * Advanced Chat Interface Component
 * Enhanced chat UI with special AI output rendering and full Lucid Chat integration
 */

import React, { useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { User, Bot, Copy, Check, Brain, Search, GitBranch, Zap } from 'lucide-react'
import { AIVisualOutputRenderer } from '../output/AIVisualOutputRenderer'
import { OutputDetector } from '../output/OutputDetector'
import type { AdvancedChatMessage } from '../../../store/lucid-chat/advancedLLMStore'

interface AdvancedChatInterfaceProps {
  messages: AdvancedChatMessage[]
  streamingMessage?: string
  streamingProtocol?: AdvancedChatMessage['outputProtocol']
  isStreaming?: boolean
  onSend?: (message: string) => void
  input?: string
  onInputChange?: (value: string) => void
  placeholder?: string
  maxLength?: number
  disabled?: boolean
  thinkingMode?: string
  deepSearchEnabled?: boolean
  branchReasoningEnabled?: boolean
  apoeEnabled?: boolean
}

export const AdvancedChatInterface: React.FC<AdvancedChatInterfaceProps> = ({
  messages,
  streamingMessage,
  streamingProtocol,
  isStreaming = false,
  onSend,
  input = '',
  onInputChange,
  placeholder = 'Ask me anything...',
  maxLength = 4000,
  disabled = false,
  thinkingMode,
  deepSearchEnabled,
  branchReasoningEnabled,
  apoeEnabled,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [copiedId, setCopiedId] = React.useState<string | null>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, streamingMessage])

  const handleCopy = async (text: string, id: string) => {
    await navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && onSend && !disabled) {
      onSend(input.trim())
      if (onInputChange) {
        onInputChange('')
      }
    }
  }

  const renderMessage = (message: AdvancedChatMessage, index: number) => {
    const messageId = `msg-${index}`
    const isUser = message.role === 'user'

    // Detect outputs in message
    const detectedOutputs = OutputDetector.detect(message.content, message.outputProtocol)
    const remainingMarkdown = OutputDetector.getRemainingMarkdown(message.content, detectedOutputs)

    return (
      <div
        key={index}
        className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}
      >
        {!isUser && (
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
            <Bot className="w-5 h-5 text-white" />
          </div>
        )}

        <div
          className={`max-w-[85%] rounded-lg p-4 ${
            isUser
              ? 'bg-blue-900/30 text-gray-100'
              : 'bg-gray-800 text-gray-200'
          }`}
        >
          {/* Message Header */}
          <div className="flex items-start justify-between gap-2 mb-2">
            <div className="flex items-center gap-2 flex-wrap">
              <div className="text-xs font-medium text-gray-400">
                {isUser ? 'You' : 'AI'}
              </div>
              {!isUser && message.aimos && (
                <>
                  {message.aimos.apoe && (
                    <div className="flex items-center gap-1 text-xs text-blue-400">
                      <Zap className="w-3 h-3" />
                      <span>APOE</span>
                    </div>
                  )}
                  {message.aimos.vif && message.aimos.vif.confidence && (
                    <div className="text-xs text-green-400">
                      {Math.round(message.aimos.vif.confidence * 100)}% confidence
                    </div>
                  )}
                </>
              )}
            </div>
            <button
              onClick={() => handleCopy(message.content, messageId)}
              className="p-1 text-gray-500 hover:text-gray-300 transition-colors"
              title="Copy message"
            >
              {copiedId === messageId ? (
                <Check className="w-3 h-3 text-green-400" />
              ) : (
                <Copy className="w-3 h-3" />
              )}
            </button>
          </div>

          {/* Message Content */}
          <div className="space-y-3">
            {/* Render special outputs */}
            {detectedOutputs.length > 0 && (
              <AIVisualOutputRenderer message={message} content={message.content} />
            )}

            {/* Render remaining markdown */}
            {remainingMarkdown && (
              <div className="prose prose-invert prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {remainingMarkdown}
                </ReactMarkdown>
              </div>
            )}

            {/* Sources */}
            {message.sources && message.sources.length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-700">
                <div className="text-xs font-medium text-gray-400 mb-2">Sources:</div>
                <div className="space-y-1">
                  {message.sources.map((source, i) => (
                    <a
                      key={i}
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block text-xs text-blue-400 hover:text-blue-300 truncate"
                    >
                      {i + 1}. {source.title}
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Reasoning Steps */}
            {message.reasoning && message.reasoning.steps && (
              <div className="mt-3 pt-3 border-t border-gray-700">
                <div className="text-xs font-medium text-gray-400 mb-2">Reasoning:</div>
                <div className="space-y-2">
                  {message.reasoning.steps.map((step, i) => (
                    <div key={i} className="text-xs text-gray-400">
                      <span className="text-blue-400">Step {step.step}:</span> {step.thought}
                      {step.confidence && (
                        <span className="ml-2 text-green-400">
                          ({Math.round(step.confidence * 100)}%)
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Message Footer */}
          <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-700/50">
            <div className="text-xs text-gray-500">
              {message.timestamp.toLocaleTimeString()}
            </div>
            {message.tokensUsed && (
              <div className="text-xs text-gray-500">
                {message.tokensUsed.toLocaleString()} tokens
              </div>
            )}
          </div>
        </div>

        {isUser && (
          <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
            <User className="w-5 h-5 text-white" />
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-gray-950">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !isStreaming && (
          <div className="text-center text-gray-500 mt-8">
            <Bot className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>Start a conversation</p>
            <p className="text-xs text-gray-600 mt-2">
              Use thinking modes, deep search, and branch reasoning for advanced AI capabilities
            </p>
          </div>
        )}

        {messages.map((message, index) => renderMessage(message, index))}

        {/* Streaming Message */}
        {isStreaming && streamingMessage && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="max-w-[85%] rounded-lg p-4 bg-gray-800 text-gray-200">
              <div className="flex items-center gap-2 mb-2">
                <div className="text-xs font-medium text-gray-400">AI</div>
                {thinkingMode && (
                  <div className="flex items-center gap-1 text-xs text-blue-400">
                    <Brain className="w-3 h-3" />
                    <span className="capitalize">{thinkingMode}</span>
                  </div>
                )}
                {deepSearchEnabled && (
                  <div className="flex items-center gap-1 text-xs text-purple-400">
                    <Search className="w-3 h-3" />
                    <span>Deep Search</span>
                  </div>
                )}
                {branchReasoningEnabled && (
                  <div className="flex items-center gap-1 text-xs text-yellow-400">
                    <GitBranch className="w-3 h-3" />
                    <span>Branch Reasoning</span>
                  </div>
                )}
                {apoeEnabled && (
                  <div className="flex items-center gap-1 text-xs text-green-400">
                    <Zap className="w-3 h-3" />
                    <span>APOE</span>
                  </div>
                )}
              </div>
              <div className="space-y-3">
                {streamingProtocol && (
                  <AIVisualOutputRenderer
                    message={{
                      role: 'assistant',
                      content: streamingMessage,
                      timestamp: new Date(),
                      outputProtocol: streamingProtocol,
                    }}
                    content={streamingMessage}
                  />
                )}
                {!streamingProtocol && (
                  <div className="prose prose-invert prose-sm max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {streamingMessage}
                    </ReactMarkdown>
                    <span className="animate-pulse inline-block ml-1">▊</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-800">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => onInputChange?.(e.target.value)}
            placeholder={placeholder}
            maxLength={maxLength}
            disabled={disabled}
            rows={3}
            className="flex-1 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={!input.trim() || disabled}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors self-end"
          >
            Send
          </button>
        </div>
        <div className="text-xs text-gray-500 mt-1 text-right">
          {input.length}/{maxLength}
        </div>
      </form>
    </div>
  )
}

