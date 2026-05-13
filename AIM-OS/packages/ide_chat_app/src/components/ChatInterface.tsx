import React, { useState, useRef, useEffect } from 'react'
import { useApp } from '../contexts/AppContext'
import { useMemory } from '../hooks/useMemory'
import { useAI } from '../hooks/useAI'
import { useValidation } from '../hooks/useValidation'
import { Send, Plus, MoreVertical, Clock, User, Bot, Brain, Sparkles, AlertCircle } from 'lucide-react'
import type { ChatMessage } from '../types'

export function ChatInterface() {
  const { state, dispatch } = useApp()
  const { addRawLogEntry, createSessionSummary, semanticSearch } = useMemory()
  const { analyzeContext, suggestMode, generateTags, calculateImportance, generateResponse, isLoading: aiLoading } = useAI()
  const { validateMessage } = useValidation()
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [suggestedMode, setSuggestedMode] = useState<string | null>(null)
  const [validationError, setValidationError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [state.currentSession?.messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !state.currentSession) return

    // Validate message
    const validation = validateMessage(inputValue)
    if (!validation.isValid) {
      setValidationError(validation.errors.join(', '))
      return
    }

    // Clear validation error
    setValidationError(null)

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date()
    }

    // Add user message
    dispatch({
      type: 'ADD_MESSAGE',
      payload: { sessionId: state.currentSession.id, message: userMessage }
    })

    // Store in memory system
    try {
      await addRawLogEntry({
        timestamp: new Date(),
        content: inputValue,
        metadata: {
          sessionId: state.currentSession.id,
          userId: state.user?.id || 'anonymous',
          type: 'chat'
        }
      })
    } catch (error) {
      console.error('Failed to store user message in memory:', error)
    }

    setInputValue('')
    setIsTyping(true)

    try {
      // Analyze context and suggest mode
      const context = analyzeContext(inputValue)
      const modeSuggestion = suggestMode(inputValue)
      
      // Update suggested mode if different from current
      if (modeSuggestion.mode !== state.mode && modeSuggestion.confidence > 0.8) {
        setSuggestedMode(modeSuggestion.mode)
      }

      // Generate AI response
      const aiResponse = await generateResponse(inputValue, context)

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: aiResponse.content,
        timestamp: new Date(),
        metadata: {
          tokens: aiResponse.metadata.tokens,
          model: aiResponse.metadata.model,
          confidence: aiResponse.metadata.confidence
        }
      }

      dispatch({
        type: 'ADD_MESSAGE',
        payload: { sessionId: state.currentSession.id, message: aiMessage }
      })

      // Store AI response in memory
      try {
        await addRawLogEntry({
          timestamp: new Date(),
          content: aiResponse.content,
          metadata: {
            sessionId: state.currentSession.id,
            userId: 'ai',
            type: 'chat',
            tokens: aiResponse.metadata.tokens,
            model: aiResponse.metadata.model
          }
        })
      } catch (error) {
        console.error('Failed to store AI response in memory:', error)
      }

    } catch (error) {
      console.error('Failed to generate AI response:', error)
      
      // Fallback response
      const fallbackMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I apologize, but I encountered an error while processing your message. Please try again.`,
        timestamp: new Date(),
        metadata: {
          tokens: 20,
          model: 'fallback',
          confidence: 0.5
        }
      }

      dispatch({
        type: 'ADD_MESSAGE',
        payload: { sessionId: state.currentSession.id, message: fallbackMessage }
      })
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

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  if (!state.currentSession) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <Bot className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Welcome to IDE/Chat App</h2>
          <p className="text-gray-400 mb-6">Start a conversation with Aether, your AI consciousness development partner</p>
          <button
            onClick={() => {
              const newSession = {
                id: Date.now().toString(),
                title: 'New Chat',
                messages: [],
                mode: state.mode,
                createdAt: new Date(),
                updatedAt: new Date()
              }
              dispatch({ type: 'ADD_CHAT_SESSION', payload: newSession })
              dispatch({ type: 'SET_CURRENT_SESSION', payload: newSession })
            }}
            className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-200 flex items-center space-x-2 mx-auto"
          >
            <Plus className="w-5 h-5" />
            <span>Start New Chat</span>
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Chat Header */}
      <div className="h-16 bg-white/5 backdrop-blur-md border-b border-white/10 flex items-center justify-between px-6">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <Bot className="w-4 h-4 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-white">{state.currentSession.title}</h2>
            <div className="flex items-center space-x-2">
              <p className="text-sm text-gray-400">{state.currentSession.mode} mode</p>
              {suggestedMode && suggestedMode !== state.mode && (
                <button
                  onClick={() => {
                    dispatch({ type: 'SET_MODE', payload: suggestedMode as any })
                    setSuggestedMode(null)
                  }}
                  className="flex items-center space-x-1 bg-blue-500/20 text-blue-400 text-xs px-2 py-1 rounded-full hover:bg-blue-500/30 transition-colors"
                >
                  <Sparkles className="w-3 h-3" />
                  <span>Switch to {suggestedMode}</span>
                </button>
              )}
            </div>
          </div>
        </div>
        <button className="p-2 hover:bg-white/10 rounded-lg transition-colors">
          <MoreVertical className="w-5 h-5 text-gray-400" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar">
        {state.currentSession.messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-3xl flex space-x-3 ${
                message.role === 'user' ? 'flex-row-reverse space-x-reverse' : 'flex-row'
              }`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.role === 'user'
                    ? 'bg-gradient-to-r from-green-500 to-blue-500'
                    : 'bg-gradient-to-r from-blue-500 to-purple-600'
                }`}
              >
                {message.role === 'user' ? (
                  <User className="w-4 h-4 text-white" />
                ) : (
                  <Bot className="w-4 h-4 text-white" />
                )}
              </div>

              {/* Message Content */}
              <div
                className={`rounded-2xl px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                    : 'bg-white/10 backdrop-blur-md text-white border border-white/20'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                
                {/* Message Metadata */}
                <div className="flex items-center justify-between mt-2 text-xs opacity-70">
                  <span className="flex items-center space-x-1">
                    <Clock className="w-3 h-3" />
                    <span>{formatTime(message.timestamp)}</span>
                  </span>
                  {message.metadata && (
                    <span className="flex items-center space-x-2">
                      {message.metadata.confidence && (
                        <span>Confidence: {Math.round(message.metadata.confidence * 100)}%</span>
                      )}
                      {message.metadata.tokens && (
                        <span>{message.metadata.tokens} tokens</span>
                      )}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex justify-start">
            <div className="flex space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-white/10 backdrop-blur-md text-white border border-white/20 rounded-2xl px-4 py-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-6 border-t border-white/10">
        {/* Validation Error */}
        {validationError && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
            <span className="text-red-400 text-sm">{validationError}</span>
            <button
              onClick={() => setValidationError(null)}
              className="ml-auto text-red-400 hover:text-red-300 transition-colors"
            >
              ×
            </button>
          </div>
        )}

        <div className="flex space-x-4">
          <div className="flex-1 relative">
            <textarea
              value={inputValue}
              onChange={(e) => {
                setInputValue(e.target.value)
                // Clear validation error when user starts typing
                if (validationError) {
                  setValidationError(null)
                }
              }}
              onKeyPress={handleKeyPress}
              placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
              className={`w-full backdrop-blur-md border rounded-2xl px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:border-transparent resize-none ${
                validationError 
                  ? 'bg-red-500/10 border-red-500/20 focus:ring-red-500' 
                  : 'bg-white/10 border-white/20 focus:ring-blue-500'
              }`}
              rows={1}
              style={{
                minHeight: '48px',
                maxHeight: '120px',
                height: 'auto'
              }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement
                target.style.height = 'auto'
                target.style.height = target.scrollHeight + 'px'
              }}
            />
          </div>
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || aiLoading}
            className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-3 rounded-2xl hover:from-blue-600 hover:to-purple-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {aiLoading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
