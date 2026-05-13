/**
 * Enhanced Chat Interface Component
 * Chat UI with markdown rendering and syntax highlighting
 */

import React, { useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import remarkGfm from 'remark-gfm'
import { User, Bot, Copy, Check } from 'lucide-react'

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
}

interface EnhancedChatInterfaceProps {
  messages: ChatMessage[]
  streamingMessage?: string
  isStreaming?: boolean
  onSend?: (message: string) => void
  input?: string
  onInputChange?: (value: string) => void
  placeholder?: string
  maxLength?: number
  disabled?: boolean
}

export const EnhancedChatInterface: React.FC<EnhancedChatInterfaceProps> = ({
  messages,
  streamingMessage,
  isStreaming = false,
  onSend,
  input = '',
  onInputChange,
  placeholder = 'Ask me anything...',
  maxLength = 4000,
  disabled = false,
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

  return (
    <div className="h-full flex flex-col bg-gray-950">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !isStreaming && (
          <div className="text-center text-gray-500 mt-8">
            <Bot className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>Start a conversation</p>
          </div>
        )}

        {messages.map((message, index) => {
          const messageId = `msg-${index}`
          const isUser = message.role === 'user'

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
                className={`max-w-[80%] rounded-lg p-4 ${
                  isUser
                    ? 'bg-blue-900/30 text-gray-100'
                    : 'bg-gray-800 text-gray-200'
                }`}
              >
                <div className="flex items-start justify-between gap-2 mb-1">
                  <div className="text-xs font-medium text-gray-400">
                    {isUser ? 'You' : 'AI'}
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

                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      code({ node, inline, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || '')
                        const codeString = String(children).replace(/\n$/, '')
                        return !inline && match ? (
                          <div className="relative">
                            <SyntaxHighlighter
                              style={vscDarkPlus}
                              language={match[1]}
                              PreTag="div"
                              {...props}
                            >
                              {codeString}
                            </SyntaxHighlighter>
                            <button
                              onClick={() => handleCopy(codeString, `${messageId}-code`)}
                              className="absolute top-2 right-2 p-1 bg-gray-700 rounded text-xs text-gray-300 hover:bg-gray-600"
                            >
                              {copiedId === `${messageId}-code` ? (
                                <Check className="w-3 h-3" />
                              ) : (
                                <Copy className="w-3 h-3" />
                              )}
                            </button>
                          </div>
                        ) : (
                          <code className={className} {...props}>
                            {children}
                          </code>
                        )
                      },
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>

                <div className="text-xs text-gray-500 mt-2">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>

              {isUser && (
                <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                  <User className="w-5 h-5 text-white" />
                </div>
              )}
            </div>
          )
        })}

        {/* Streaming Message */}
        {isStreaming && streamingMessage && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="max-w-[80%] rounded-lg p-4 bg-gray-800 text-gray-200">
              <div className="text-xs font-medium text-gray-400 mb-1">AI</div>
              <div className="prose prose-invert prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {streamingMessage}
                </ReactMarkdown>
                <span className="animate-pulse inline-block ml-1">▊</span>
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

