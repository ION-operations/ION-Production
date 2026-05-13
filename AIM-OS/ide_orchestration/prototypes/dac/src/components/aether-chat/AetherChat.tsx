/**
 * Aether Chat Component
 * Main chat interface integrating all AIM-OS systems and UI components
 * Created by Sage - Frontend Integration Specialist
 * Integrates with Alex's backend and Nova's ICIP
 */

import React, { useState, useRef, useEffect, useCallback, useMemo } from 'react'
import { useTopicStore } from '../../store/topicStore'
import { useCMC, useVIF, useSEG, useAPOE, useCAS, useTCS } from '../../hooks/useAIMOS'
import { ErrorBoundary } from '../ErrorBoundary'
import { ErrorDisplay, LoadingSpinner, ConfidenceBadge } from '../shared'
import { HookLoadingState, ICIPLoadingState } from './LoadingStates'
import { CodeGenerationInput } from './CodeGenerationInput'
import { MessageRenderer } from './MessageRenderer'
import { TopicSelector } from './TopicSelector'
import { Send, Code, MessageSquare, Sparkles, Settings, X, FolderTree } from 'lucide-react'
import { runAetherChatTurn } from '../../services/aetherChatOrchestrator'
import type { RawUserTurn, FinalChatTurn, PlanStreamChunk, ResponsePlan, ReasoningTrace, LucidLayers, ContextWeb } from '../../types/aetherChatTypes'

export interface AetherChatMessage {
  id: string
  role: 'user' | 'aether' | 'system'
  content: string
  timestamp: Date
  topicId?: string
  codeGeneration?: CodeGenerationResult
  executionResult?: ExecutionResult
  confidence?: number
  confidenceBand?: 'A' | 'B' | 'C' | 'S'
  witnessId?: string
  error?: Error
  errorType?: 'network' | 'timeout' | 'validation' | 'api' | 'system'
  // Aether Chat orchestrator fields
  evidence?: Array<{
    id: string
    kind: 'file_snippet' | 'doc_snippet' | 'prior_msg' | 'test_output' | 'other'
    sourceId: string
    excerpt: string
    trust: number
  }>
  contextWeb?: ContextWeb // Full ContextWeb from orchestrator (Phase 5 Week 20)
  reasoningSummary?: string
  reasoningTrace?: ReasoningTrace // Phase 3 Week 13-14: LUCID Empire reasoning trace
  lucidLayers?: LucidLayers // Phase 3 Week 13-14: All 5 LUCID Empire layers
  uiHints?: {
    showContextWeb: boolean
    showEvidencePanel: boolean
    showThinkingMode: boolean
    showLucidEmpire?: boolean // Phase 3 Week 13-14: Show LUCID Empire display
  }
  // Dynamic κ-Gating (Phase 1 Week 4)
  gatingDetermination?: 'PROCEED' | 'SPECULATE_WITH_WARNING' | 'ABSTAIN_AND_CLARIFY'
  riskAssessment?: {
    riskScore: number
    riskLevel: 'low' | 'medium' | 'high' | 'critical'
    category: 'casual' | 'informational' | 'modification' | 'destructive' | 'critical'
  }
}

export interface AetherChatProps {
  initialTopicId?: string
  onTopicChange?: (topicId: string) => void
  className?: string
}

export const AetherChat: React.FC<AetherChatProps> = ({
  initialTopicId,
  onTopicChange,
  className = '',
}) => {
  const [messages, setMessages] = useState<AetherChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [showCodeGeneration, setShowCodeGeneration] = useState(false)
  const [showTopicSelector, setShowTopicSelector] = useState(false)
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  // Streaming plan state
  const [currentStreamingChunks, setCurrentStreamingChunks] = useState<PlanStreamChunk[]>([])
  const [currentPlan, setCurrentPlan] = useState<ResponsePlan | undefined>(undefined)
  const [isStreamingPlan, setIsStreamingPlan] = useState(false)

  // Topic store
  const {
    topics,
    activeTopicId,
    setActiveTopic,
    createTopic,
  } = useTopicStore()

  // AIM-OS hooks
  const { storeAtom, retrieveAtoms } = useCMC()
  const { trackConfidence, getWitnesses } = useVIF()
  const { synthesizeKnowledge } = useSEG()
  const { createPlan } = useAPOE()
  const { getMetrics } = useCAS()
  const { addEntry } = useTCS()

  // Set initial topic
  useEffect(() => {
    if (initialTopicId) {
      setActiveTopic(initialTopicId)
    }
  }, [initialTopicId, setActiveTopic])

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Handle code generation (will integrate with Nova's useICIP hook)
  const handleCodeGeneration = useCallback(async (
    type: 'function' | 'class' | 'test' | 'documentation' | 'completion' | 'refactoring',
    prompt: string,
    language?: string,
    context?: string
  ) => {
    setIsProcessing(true)
    try {
      // TODO: Integrate with Nova's useICIP hook
      // const { generateFunction, generateClass, ... } = useICIP()
      // const result = await generateFunction(prompt, language, context)
      
      // Mock implementation for now
      const mockResult: CodeGenerationResult = {
        generated_code: `// Generated ${type} in ${language || 'typescript'}\n// ${prompt}\nfunction example() {\n  return "Hello, World!"\n}`,
        explanation: `Generated ${type} based on your prompt`,
        confidence: 0.85,
        language: language || 'typescript',
        dependencies: [],
        test_cases: [],
        documentation: ''
      }

      // Track confidence
      const { witness_id, witness } = await trackConfidence(
        `Code generation: ${type}`,
        mockResult.confidence,
        [],
        `Generated ${type} in ${language || 'typescript'}`
      )

      // Store in CMC
      await storeAtom(mockResult.generated_code, 'code', {
        type,
        language: language || 'typescript',
        prompt,
        witness_id
      })

      // Add timeline entry
      await addEntry({
        prompt_id: `code_gen_${Date.now()}`,
        context_index: { type, language, prompt },
        summary: `Generated ${type} code`,
        confidence_metrics: { confidence: mockResult.confidence }
      })

      // Add message with code generation result
      const newMessage: AetherChatMessage = {
        id: `msg_${Date.now()}`,
        role: 'aether',
        content: `I've generated the ${type} you requested.`,
        timestamp: new Date(),
        topicId: activeTopicId,
        codeGeneration: mockResult,
        confidence: mockResult.confidence,
        confidenceBand: witness?.confidence_band,
        witnessId: witness_id
      }

      setMessages(prev => [...prev, newMessage])
      setShowCodeGeneration(false)
    } catch (error) {
      const errorMessage: AetherChatMessage = {
        id: `msg_error_${Date.now()}`,
        role: 'system',
        content: 'Code generation failed',
        timestamp: new Date(),
        topicId: activeTopicId,
        error: error instanceof Error ? error : new Error('Unknown error'),
        errorType: 'system'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsProcessing(false)
    }
  }, [trackConfidence, storeAtom, addEntry, activeTopicId])

  // Handle code execution (will integrate with Nova's execution service)
  const handleCodeExecution = useCallback(async (
    code: string,
    language: string
  ): Promise<ExecutionResult> => {
    // TODO: Integrate with Nova's code execution service
    // Mock implementation for now
    return {
      success: true,
      output: 'Execution result: Hello, World!',
      executionTime: 150,
      memoryUsed: 10
    }
  }, [])

  // Handle message send - wired to orchestrator
  const handleSend = useCallback(async () => {
    if (!input.trim() || isProcessing) return

    const userMessage: AetherChatMessage = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
      topicId: activeTopicId
    }

    setMessages(prev => [...prev, userMessage])
    const userInput = input.trim()
    setInput('')
    setIsProcessing(true)

    try {
      // Map to RawUserTurn
      const rawTurn: RawUserTurn = {
        sessionId,
        userId: undefined, // TODO: Get from auth context
        source: 'standalone',
        message: userInput,
        timestamp: new Date().toISOString(),
        conversationHistory: messages
          .filter(m => m.role === 'user' || m.role === 'aether')
          .map(m => ({
            id: m.id,
            timestamp: m.timestamp,
            role: m.role === 'user' ? 'user' as const : 'assistant' as const,
            content: m.content
          }))
      }

      // Reset streaming state
      setCurrentStreamingChunks([])
      setCurrentPlan(undefined)
      setIsStreamingPlan(true)

      // Create a placeholder message for streaming
      const streamingMessageId = `msg_streaming_${Date.now()}`
      const streamingMessage: AetherChatMessage = {
        id: streamingMessageId,
        role: 'aether',
        content: 'Thinking...',
        timestamp: new Date(),
        topicId: activeTopicId,
        streamingChunks: [],
        isStreamingPlan: true
      }
      setMessages(prev => [...prev, streamingMessage])

      // Run orchestrator with streaming support
      // Note: For now, orchestrator is synchronous, so we'll update the message after completion
      // Future: Add streaming callback support to orchestrator
      const finalTurn: FinalChatTurn = await runAetherChatTurn(rawTurn)
      
      // Update streaming message with final result
      setIsStreamingPlan(false)

      // Map FinalChatTurn back to AetherChatMessage
      const response: AetherChatMessage = {
        id: finalTurn.messageId,
        role: 'aether',
        content: finalTurn.assistantText,
        timestamp: new Date(finalTurn.timestamp),
        topicId: activeTopicId,
        confidence: finalTurn.confidence.value,
        confidenceBand: finalTurn.confidence.band,
        evidence: finalTurn.evidence.map(e => ({
          id: e.id,
          kind: e.kind,
          sourceId: e.sourceId,
          excerpt: e.excerpt,
          trust: e.trust
        })),
        contextWeb: {
          nodes: finalTurn.contextWeb.nodes.map(n => ({
            id: n.id,
            label: n.label,
            relevance: n.relevance
          })),
          edges: finalTurn.contextWeb.edges.map(e => ({
            from: e.from,
            to: e.to,
            relation: e.relation
          }))
        },
        reasoningSummary: finalTurn.reasoningSummary,
        reasoningTrace: finalTurn.reasoningTrace, // Phase 3 Week 13-14: LUCID Empire trace
        lucidLayers: finalTurn.lucidLayers, // Phase 3 Week 13-14: All 5 layers
        uiHints: finalTurn.uiHints,
        // Include plan and streaming data if available
        plan: finalTurn.plan,
        streamingChunks: finalTurn.streamingChunks || currentStreamingChunks,
        isStreamingPlan: false,
        // Include ambiguity state if ambiguous
        ambiguity: finalTurn.ambiguity,
        // Include gating determination and risk assessment (Phase 1 Week 4)
        gatingDetermination: finalTurn.gatingDetermination,
        riskAssessment: finalTurn.riskAssessment
      }

      // Replace streaming message with final response
      setMessages(prev => prev.map(msg => 
        msg.id === streamingMessageId ? response : msg
      ))
      
      // Clear streaming state
      setCurrentStreamingChunks([])
      setCurrentPlan(undefined)
    } catch (error) {
      console.error('Aether Chat orchestrator error:', error)
      const errorMessage: AetherChatMessage = {
        id: `msg_error_${Date.now()}`,
        role: 'system',
        content: error instanceof Error ? error.message : 'Failed to process message',
        timestamp: new Date(),
        topicId: activeTopicId,
        error: error instanceof Error ? error : new Error('Unknown error'),
        errorType: 'system'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsProcessing(false)
    }
  }, [input, isProcessing, activeTopicId, sessionId, messages])

  // Get witness for message
  const getMessageWitness = useCallback(async (witnessId?: string) => {
    if (!witnessId) return undefined
    const witnesses = await getWitnesses(witnessId)
    return witnesses[0]
  }, [getWitnesses])

  // Handle ambiguity resolution
  const handleAmbiguityResolve = useCallback(async (messageId: string, selectedInterpretation: number) => {
    // Find the message with ambiguity
    const ambiguousMessage = messages.find(m => m.id === messageId && m.ambiguity?.isAmbiguous)
    if (!ambiguousMessage || !ambiguousMessage.ambiguity) return

    // Get the selected interpretation
    const selected = ambiguousMessage.ambiguity.interpretations[selectedInterpretation]
    if (!selected) return

    // Create a new user message with the clarified intent
    const clarifiedMessage: AetherChatMessage = {
      id: `msg_clarified_${Date.now()}`,
      role: 'user',
      content: `[Clarification] ${selected.intent}`,
      timestamp: new Date(),
      topicId: activeTopicId
    }

    setMessages(prev => [...prev, clarifiedMessage])

    // Process the clarified message through orchestrator
    const rawTurn: RawUserTurn = {
      sessionId,
      userId: undefined,
      source: 'standalone',
      message: selected.intent,
      timestamp: new Date().toISOString(),
      conversationHistory: messages
        .filter(m => m.role === 'user' || m.role === 'aether')
        .map(m => ({
          id: m.id,
          timestamp: m.timestamp,
          role: m.role === 'user' ? 'user' as const : 'assistant' as const,
          content: m.content
        }))
    }

    setIsProcessing(true)
    try {
      const finalTurn: FinalChatTurn = await runAetherChatTurn(rawTurn)
      
      const response: AetherChatMessage = {
        id: finalTurn.messageId,
        role: 'aether',
        content: finalTurn.assistantText,
        timestamp: new Date(finalTurn.timestamp),
        topicId: activeTopicId,
        confidence: finalTurn.confidence.value,
        confidenceBand: finalTurn.confidence.band,
        evidence: finalTurn.evidence.map(e => ({
          id: e.id,
          kind: e.kind,
          sourceId: e.sourceId,
          excerpt: e.excerpt,
          trust: e.trust
        })),
        contextWeb: {
          nodes: finalTurn.contextWeb.nodes.map(n => ({
            id: n.id,
            label: n.label,
            relevance: n.relevance
          })),
          edges: finalTurn.contextWeb.edges.map(e => ({
            from: e.from,
            to: e.to,
            relation: e.relation
          }))
        },
        reasoningSummary: finalTurn.reasoningSummary,
        reasoningTrace: finalTurn.reasoningTrace, // Phase 3 Week 13-14: LUCID Empire trace
        lucidLayers: finalTurn.lucidLayers, // Phase 3 Week 13-14: All 5 layers
        uiHints: finalTurn.uiHints,
        plan: finalTurn.plan,
        streamingChunks: finalTurn.streamingChunks,
        isStreamingPlan: false
      }

      setMessages(prev => [...prev, response])
    } catch (error) {
      console.error('Ambiguity resolution error:', error)
    } finally {
      setIsProcessing(false)
    }
  }, [messages, activeTopicId, sessionId])

  return (
    <ErrorBoundary panelName="Aether Chat">
      <div className={`flex flex-col h-full bg-gray-900 ${className}`}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-400" />
            <h1 className="text-lg font-semibold text-gray-200">Aether Chat</h1>
            {activeTopicId && (
              <span className="text-sm text-gray-400">
                {topics.find(t => t.id === activeTopicId)?.name || 'Topic'}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowTopicSelector(!showTopicSelector)}
              className={`p-2 rounded transition-colors ${
                showTopicSelector
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700'
              }`}
              title="Topics"
            >
              <FolderTree className="w-4 h-4" />
            </button>
            <button
              onClick={() => setShowCodeGeneration(!showCodeGeneration)}
              className={`p-2 rounded transition-colors ${
                showCodeGeneration
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700'
              }`}
              title="Code Generation"
            >
              <Code className="w-4 h-4" />
            </button>
            <button
              className="p-2 rounded text-gray-400 hover:text-gray-200 hover:bg-gray-700 transition-colors"
              title="Settings"
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Topic Selector Panel */}
        {showTopicSelector && (
          <div className="border-b border-gray-700 p-4 bg-gray-800/50">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-medium text-gray-300">Topics</h2>
              <button
                onClick={() => setShowTopicSelector(false)}
                className="p-1 rounded text-gray-400 hover:text-gray-200 hover:bg-gray-700 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <TopicSelector
              activeTopicId={activeTopicId}
              onTopicSelect={(topicId) => {
                setActiveTopic(topicId)
                onTopicChange?.(topicId)
              }}
              showCreate={true}
            />
          </div>
        )}

        {/* Code Generation Panel */}
        {showCodeGeneration && (
          <div className="border-b border-gray-700 p-4 bg-gray-800/50">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-medium text-gray-300">Code Generation</h2>
              <button
                onClick={() => setShowCodeGeneration(false)}
                className="p-1 rounded text-gray-400 hover:text-gray-200 hover:bg-gray-700 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <CodeGenerationInput
              onGenerate={handleCodeGeneration}
              generating={isProcessing}
            />
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-gray-500">
              <MessageSquare className="w-12 h-12 mb-4 opacity-50" />
              <p className="text-sm">Start a conversation or generate code</p>
            </div>
          )}

          {messages.map((message) => (
            <MessageRenderer
              key={message.id}
              message={message}
              onCodeExecute={handleCodeExecution}
              onErrorDismiss={(messageId) => {
                setMessages(prev => prev.filter(m => m.id !== messageId))
              }}
              onAmbiguityResolve={handleAmbiguityResolve}
            />
          ))}

          {isProcessing && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <div className="bg-gray-800 rounded-lg p-3">
                <LoadingSpinner size="sm" message="Processing..." />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-700 p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
              placeholder="Type a message..."
              className="flex-1 px-4 py-2 rounded bg-gray-800 text-gray-200 border border-gray-700 focus:outline-none focus:border-blue-500"
              disabled={isProcessing}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isProcessing}
              className="px-4 py-2 rounded bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  )
}

