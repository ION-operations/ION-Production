/**
 * Message Renderer Component
 * Renders individual chat messages with all integrated features
 * Created by Sage - Frontend Integration Specialist
 */

import React, { useState, useEffect } from 'react'
import { Sparkles, ChevronDown, ChevronUp, FileText, MessageSquare, TestTube, Link } from 'lucide-react'
import { CodeBlockRenderer, type CodeGenerationResult } from './CodeBlockRenderer'
import { CodeExecutionUI, type ExecutionResult } from './CodeExecutionUI'
import { QualityGateDisplay } from './QualityGateDisplay'
import { ConfidenceDisplay } from './ConfidenceDisplay'
import { ThinkingModePanel } from './ThinkingModePanel'
import { AmbiguityResolver } from './AmbiguityResolver'
import { DynamicGatingBadge, SpeculativeModeBadge, ActionBlockedBadge } from './DynamicGatingBadge'
import { ContextWebPanel } from './ContextWebPanel'
import { EvidencePanel } from './EvidencePanel'
import { RenderTextWithCitations, parseCitations } from './CitationPill'
import { LucidEmpireDisplay } from './LucidEmpireDisplay'
import { ErrorDisplay, type ErrorType } from '../shared'
import type { AetherChatMessage } from './AetherChat'
import type { EvidenceItem, ConfidenceScore, ReasoningTrace, LucidLayers } from '../../types/aetherChatTypes'

export interface MessageRendererProps {
  message: AetherChatMessage
  onCodeExecute?: (code: string, language: string) => Promise<ExecutionResult>
  onErrorDismiss?: (messageId: string) => void
  onAmbiguityResolve?: (messageId: string, selectedInterpretation: number) => void
  className?: string
}

export const MessageRenderer: React.FC<MessageRendererProps> = ({
  message,
  onCodeExecute,
  onErrorDismiss,
  onAmbiguityResolve,
  className = '',
}) => {
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'
  const [showEvidence, setShowEvidence] = useState(false)
  const [showContextWeb, setShowContextWeb] = useState(false)
  const [isContextWebExpanded, setIsContextWebExpanded] = useState(false)
  const [xRayMode, setXRayMode] = useState(false)

  // X-Ray Mode toggle (Alt/Option key)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.altKey || e.metaKey) {
        setXRayMode(true)
      }
    }
    const handleKeyUp = (e: KeyboardEvent) => {
      if (!e.altKey && !e.metaKey) {
        setXRayMode(false)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)
    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
    }
  }, [])

  // Parse citations from message content
  const citations = React.useMemo(() => {
    if (!message.content || isUser) return []
    return parseCitations(message.content)
  }, [message.content, isUser])

  // Build evidence items map for citations
  const evidenceItemsMap = React.useMemo(() => {
    if (!message.evidence) return new Map<string, EvidenceItem>()
    const map = new Map<string, EvidenceItem>()
    message.evidence.forEach((item) => {
      map.set(item.id, item)
    })
    return map
  }, [message.evidence])

  // Build confidence map for citations
  const confidenceMap = React.useMemo(() => {
    const map = new Map<string, ConfidenceScore>()
    if (message.evidence && message.confidence !== undefined) {
      message.evidence.forEach((item) => {
        map.set(item.id, {
          value: item.trust,
          band: (message.confidenceBand === 'S' ? 'A' : message.confidenceBand) || 'B'
        })
      })
    }
    return map
  }, [message.evidence, message.confidence, message.confidenceBand])

  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'} ${className}`}>
      {/* Avatar */}
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
          {isSystem ? (
            <span className="text-xs text-white">S</span>
          ) : (
            <Sparkles className="w-4 h-4 text-white" />
          )}
        </div>
      )}

      {/* Message Content */}
      <div className={`flex flex-col gap-2 max-w-2xl ${isUser ? 'items-end' : 'items-start'}`}>
        {/* Message Text */}
        <div className={`rounded-lg p-3 ${
          isUser
            ? 'bg-blue-600 text-white'
            : isSystem
            ? 'bg-gray-800 text-gray-300'
            : 'bg-gray-800 text-gray-200'
        }`}>
          {citations.length > 0 && !isUser ? (
            <RenderTextWithCitations
              text={message.content}
              citations={citations}
              evidenceItems={evidenceItemsMap}
              confidenceMap={confidenceMap}
              onViewSource={(sourceId) => {
                // TODO: Implement source viewing
                console.log('View source:', sourceId)
              }}
              className="text-sm whitespace-pre-wrap"
            />
          ) : (
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          )}
          {xRayMode && citations.length > 0 && (
            <div className="mt-2 text-xs text-gray-400">
              X-Ray Mode: {citations.length} citation{citations.length !== 1 ? 's' : ''} detected
            </div>
          )}
        </div>

        {/* Code Generation Result */}
        {message.codeGeneration && (
          <div className="w-full">
            <CodeBlockRenderer
              result={message.codeGeneration}
              onExecute={onCodeExecute ? () => {
                if (message.codeGeneration) {
                  onCodeExecute(
                    message.codeGeneration.generated_code,
                    message.codeGeneration.language
                  )
                }
              } : undefined}
              showConfidence={true}
            />
          </div>
        )}

        {/* Code Execution Result */}
        {message.executionResult && message.codeGeneration && (
          <div className="w-full">
            <CodeExecutionUI
              code={message.codeGeneration.generated_code}
              language={message.codeGeneration.language}
              onExecute={onCodeExecute || (async () => message.executionResult!)}
              result={message.executionResult}
            />
          </div>
        )}

        {/* Quality Gate Display */}
        {message.witnessId && (
          <div className="w-full">
            <QualityGateDisplay
              confidence={message.confidence}
              confidenceBand={message.confidenceBand}
            />
          </div>
        )}

        {/* Confidence Display */}
        {message.confidence !== undefined && !message.witnessId && (
          <ConfidenceDisplay
            confidence={message.confidence}
            confidenceBand={message.confidenceBand}
            size="sm"
          />
        )}

        {/* Evidence Panel (Phase 5 Week 21) */}
        {message.evidence && message.evidence.length > 0 && message.uiHints?.showEvidencePanel && (
          <div className="w-full mb-2">
            <EvidencePanel
              evidencePack={{
                items: message.evidence.map(e => ({
                  id: e.id,
                  kind: e.kind,
                  sourceId: e.sourceId,
                  excerpt: e.excerpt,
                  trust: e.trust,
                  location: undefined,
                  timestamp: undefined
                })),
                totalTrust: message.evidence.reduce((sum, e) => sum + e.trust, 0) / message.evidence.length,
                completeness: {
                  isComplete: message.evidence.length > 0,
                  completenessScore: message.evidence.length > 0 ? 1.0 : 0.0,
                  missingTypes: [],
                  recommendations: []
                }
              }}
              evidenceChain={message.panelData?.evidence?.chain}
              onItemClick={(item) => {
                console.log('Evidence item clicked:', item)
                // Phase 5 Week 21: Enhanced evidence item click interactions
                // TODO: Navigate to source (file/doc/message)
              }}
              onViewSource={(sourceId) => {
                console.log('View source:', sourceId)
                // TODO: Open source in appropriate viewer
              }}
              showXRayMode={xRayMode}
              onToggleXRay={() => setXRayMode(!xRayMode)}
              isExpanded={showEvidence}
              onToggleExpand={() => setShowEvidence(!showEvidence)}
            />
          </div>
        )}

        {/* Context Web Panel (Phase 2 Week 7-8) */}
        {message.contextWeb && message.contextWeb.nodes.length > 0 && message.uiHints?.showContextWeb && (
          <div className="w-full mb-2">
            <ContextWebPanel
              contextWeb={message.contextWeb}
              panelData={message.panelData?.contextWeb}
              onNodeClick={(node) => {
                console.log('Context node clicked:', node)
                // Phase 5 Week 20: Enhanced node click interactions
                // Open node details or navigate to source based on node type
                if (node.type === 'file') {
                  // TODO: Open file in editor
                  console.log('Open file:', node.id)
                } else if (node.type === 'doc') {
                  // TODO: Open documentation
                  console.log('Open doc:', node.id)
                } else if (node.type === 'msg') {
                  // TODO: Navigate to message
                  console.log('Navigate to message:', node.id)
                }
              }}
              onEdgeClick={(edge) => {
                console.log('Context edge clicked:', edge)
                // Phase 5 Week 20: Enhanced edge click interactions
                // Show relationship details with SEG integration
                console.log('Relationship:', edge.relation, 'Strength:', edge.strength)
              }}
              onSearch={async (query) => {
                // Use panelData interaction if available
                if (message.panelData?.contextWeb?.interactions?.semanticSearch) {
                  return await message.panelData.contextWeb.interactions.semanticSearch(query)
                }
                // Fallback: simple text search
                return message.contextWeb!.nodes.filter(node =>
                  node.label.toLowerCase().includes(query.toLowerCase()) ||
                  node.context?.toLowerCase().includes(query.toLowerCase())
                )
              }}
              isExpanded={isContextWebExpanded}
              onToggleExpand={() => setIsContextWebExpanded(!isContextWebExpanded)}
            />
          </div>
        )}

        {/* Ambiguity Resolver (Phase 1 Week 3) */}
        {message.ambiguity && message.ambiguity.isAmbiguous && (
          <div className="w-full mb-2">
            <AmbiguityResolver
              ambiguity={message.ambiguity}
              onResolve={(selectedInterpretation) => {
                if (onAmbiguityResolve) {
                  onAmbiguityResolve(message.id, selectedInterpretation)
                }
              }}
            />
          </div>
        )}

        {/* Thinking Mode Panel (Streaming Plan Generation + JIT Intervention) */}
        {(message.uiHints?.showThinkingMode || message.plan || message.streamingChunks) && (
          <div className="w-full">
            <ThinkingModePanel
              plan={message.plan}
              streamingChunks={message.streamingChunks}
              isStreaming={message.isStreamingPlan}
              enableJIT={true} // Enable JIT Intervention (Phase 3 Week 12)
              onEditStep={(stepId, newAction) => {
                // TODO: Implement step editing via orchestrator
                console.log('Edit step:', stepId, newAction)
              }}
              onDeleteStep={(stepId) => {
                // TODO: Implement step deletion via orchestrator
                console.log('Delete step:', stepId)
              }}
              onIntervention={(state) => {
                // TODO: Handle intervention state changes
                console.log('JIT Intervention:', state)
              }}
              onSavePlan={(editedPlan) => {
                // TODO: Save edited plan via orchestrator
                console.log('Save edited plan:', editedPlan)
              }}
            />
          </div>
        )}

        {/* Dynamic κ-Gating Badge (Phase 1 Week 4) */}
        {message.gatingDetermination && (
          <div className="w-full mb-2">
            <DynamicGatingBadge
              determination={message.gatingDetermination}
              riskAssessment={message.riskAssessment}
              requiredConfidence={message.confidence ? undefined : undefined} // TODO: Get from orchestrator
              actualConfidence={message.confidence}
            />
          </div>
        )}

        {/* Speculative Mode Badge (if applicable) */}
        {message.gatingDetermination === 'SPECULATE_WITH_WARNING' && (
          <div className="w-full mb-2">
            <SpeculativeModeBadge />
          </div>
        )}

        {/* Action Blocked Badge (if applicable) */}
        {message.gatingDetermination === 'ABSTAIN_AND_CLARIFY' && (
          <div className="w-full mb-2">
            <ActionBlockedBadge reason="Confidence below required threshold" />
          </div>
        )}

        {/* LUCID Empire Reasoning Display (Phase 3 Week 13-14) */}
        {message.reasoningTrace && message.lucidLayers && (
          <div className="w-full mb-3">
            <LucidEmpireDisplay
              reasoningTrace={message.reasoningTrace}
              lucidLayers={message.lucidLayers}
              onExploreLayer={(layer, data) => {
                // TODO: Implement layer exploration (e.g., show in modal or expand panel)
                console.log('Explore LUCID layer:', layer, data)
              }}
            />
          </div>
        )}

        {/* Reasoning Summary (fallback if no full trace) */}
        {message.reasoningSummary && !message.reasoningTrace && (
          <div className="w-full bg-gray-800 rounded-lg border border-gray-700 p-3">
            <p className="text-xs text-gray-400 mb-1">Reasoning Summary</p>
            <p className="text-sm text-gray-300">{message.reasoningSummary}</p>
          </div>
        )}

        {/* Error Display */}
        {message.error && (
          <ErrorDisplay
            error={message.error}
            errorType={message.errorType}
            onDismiss={onErrorDismiss ? () => onErrorDismiss(message.id) : undefined}
          />
        )}

        {/* Timestamp */}
        <span className="text-xs text-gray-500">
          {message.timestamp.toLocaleTimeString()}
        </span>
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center flex-shrink-0">
          <span className="text-xs text-gray-400">U</span>
        </div>
      )}
    </div>
  )
}

