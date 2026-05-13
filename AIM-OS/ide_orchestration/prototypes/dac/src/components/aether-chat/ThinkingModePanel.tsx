/**
 * Thinking Mode Panel Component
 * Displays streaming APOE plan generation in real-time
 * 
 * Phase 1 Week 2: Thinking Mode Enhancements (Task 4)
 */

import React, { useState, useEffect } from 'react'
import { Brain, Loader2, CheckCircle2, Circle, Clock, Edit2, Trash2, GripVertical } from 'lucide-react'
import { JITInterventionHandler, type JITInterventionState } from './JITInterventionHandler'
import type { StreamingPlanStep, PlanStreamChunk, ResponsePlan } from '../../types/aetherChatTypes'

export interface ThinkingModePanelProps {
  plan?: ResponsePlan
  streamingChunks?: PlanStreamChunk[]
  isStreaming?: boolean
  onEditStep?: (stepId: string, newAction: string) => void
  onDeleteStep?: (stepId: string) => void
  onIntervention?: (state: JITInterventionState) => void
  onSavePlan?: (editedPlan: ResponsePlan) => void
  enableJIT?: boolean // Enable JIT Intervention (Phase 3 Week 12)
  className?: string
}

/**
 * Role type icons mapping
 */
const ROLE_ICONS: Record<string, React.ReactNode> = {
  planner: <Brain className="w-4 h-4" />,
  retriever: <Circle className="w-4 h-4" />,
  reasoner: <Brain className="w-4 h-4" />,
  builder: <Edit2 className="w-4 h-4" />,
  verifier: <CheckCircle2 className="w-4 h-4" />,
  critic: <Circle className="w-4 h-4" />,
  operator: <Circle className="w-4 h-4" />
}

/**
 * Role type colors
 */
const ROLE_COLORS: Record<string, string> = {
  planner: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
  retriever: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
  reasoner: 'bg-green-500/20 text-green-300 border-green-500/30',
  builder: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
  verifier: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  critic: 'bg-red-500/20 text-red-300 border-red-500/30',
  operator: 'bg-gray-500/20 text-gray-300 border-gray-500/30'
}

export const ThinkingModePanel: React.FC<ThinkingModePanelProps> = ({
  plan,
  streamingChunks = [],
  isStreaming = false,
  onEditStep,
  onDeleteStep,
  onIntervention,
  onSavePlan,
  enableJIT = false,
  className = ''
}) => {
  const [streamingSteps, setStreamingSteps] = useState<Map<string, StreamingPlanStep>>(new Map())
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set())

  // Process streaming chunks
  useEffect(() => {
    streamingChunks.forEach(chunk => {
      if (chunk.type === 'step_start') {
        setStreamingSteps(prev => {
          const updated = new Map(prev)
          updated.set(chunk.stepId, {
            stepId: chunk.stepId,
            role: chunk.role || 'builder',
            action: chunk.partialAction || '',
            status: 'GENERATING',
            partialText: chunk.partialAction
          })
          return updated
        })
      } else if (chunk.type === 'step_update') {
        setStreamingSteps(prev => {
          const updated = new Map(prev)
          const existing = updated.get(chunk.stepId)
          if (existing) {
            updated.set(chunk.stepId, {
              ...existing,
              action: chunk.partialAction || existing.action,
              partialText: chunk.partialAction || existing.partialText
            })
          }
          return updated
        })
      } else if (chunk.type === 'step_complete') {
        setStreamingSteps(prev => {
          const updated = new Map(prev)
          const existing = updated.get(chunk.stepId)
          if (existing) {
            updated.set(chunk.stepId, {
              ...existing,
              status: 'COMPLETE'
            })
          }
          return updated
        })
        setCompletedSteps(prev => new Set([...prev, chunk.stepId]))
      }
    })
  }, [streamingChunks])

  // Merge plan steps with streaming steps
  const displaySteps = React.useMemo(() => {
    if (plan && plan.steps.length > 0) {
      return plan.steps.map(step => {
        const streamingStep = streamingSteps.get(step.stepId)
        if (streamingStep) {
          return {
            ...step,
            status: streamingStep.status,
            partialText: streamingStep.partialText
          }
        }
        return {
          ...step,
          status: completedSteps.has(step.stepId) ? 'COMPLETE' : 'GENERATING' as const
        }
      })
    }
    
    // If no plan yet, show streaming steps
    return Array.from(streamingSteps.values())
  }, [plan, streamingSteps, completedSteps])

  if (displaySteps.length === 0 && !isStreaming) {
    return null
  }

  return (
    <div className={`bg-gray-900/50 border border-gray-700 rounded-lg p-4 ${className}`}>
      <div className="flex items-center gap-2 mb-4">
        <Brain className="w-5 h-5 text-blue-400" />
        <h3 className="text-sm font-semibold text-gray-200">Thinking Mode</h3>
        {isStreaming && (
          <div className="flex items-center gap-2 ml-auto">
            <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
            <span className="text-xs text-gray-400">Generating plan...</span>
          </div>
        )}
      </div>

      {plan && (
        <div className="mb-3 p-2 bg-gray-800/50 rounded border border-gray-700">
          <div className="text-xs text-gray-400 mb-1">Goal</div>
          <div className="text-sm text-gray-200">{plan.goal}</div>
          {plan.budget && (
            <div className="flex gap-4 mt-2 text-xs text-gray-400">
              <span>Tokens: {plan.budget.tokens.toLocaleString()}</span>
              <span>Cost: ${plan.budget.cost.toFixed(4)}</span>
            </div>
          )}
        </div>
      )}

      <div className="space-y-2">
        {displaySteps.map((step, index) => {
          const roleColor = ROLE_COLORS[step.role] || ROLE_COLORS.builder
          const roleIcon = ROLE_ICONS[step.role] || ROLE_ICONS.builder
          const isGenerating = step.status === 'GENERATING'
          const isComplete = step.status === 'COMPLETE'

          return (
            <div
              key={step.stepId}
              className={`p-3 rounded border transition-all ${
                isComplete
                  ? 'bg-green-500/10 border-green-500/30'
                  : isGenerating
                  ? 'bg-blue-500/10 border-blue-500/30'
                  : 'bg-gray-800/50 border-gray-700'
              }`}
            >
              <div className="flex items-start gap-3">
                {/* Step Number & Status */}
                <div className="flex-shrink-0 mt-0.5">
                  {isComplete ? (
                    <CheckCircle2 className="w-5 h-5 text-green-400" />
                  ) : isGenerating ? (
                    <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                  ) : (
                    <Circle className="w-5 h-5 text-gray-500" />
                  )}
                </div>

                {/* Step Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded text-xs border ${roleColor}`}>
                      {roleIcon}
                      <span className="capitalize">{step.role}</span>
                    </div>
                    <span className="text-xs text-gray-500">Step {index + 1}</span>
                  </div>
                  
                  <div className="text-sm text-gray-200">
                    {step.partialText || step.action || 'Generating...'}
                    {isGenerating && step.partialText && (
                      <span className="inline-block w-2 h-4 bg-blue-400 ml-1 animate-pulse" />
                    )}
                  </div>

                  {/* Dependencies */}
                  {step.dependencies && step.dependencies.length > 0 && (
                    <div className="mt-2 text-xs text-gray-400">
                      Depends on: {step.dependencies.join(', ')}
                    </div>
                  )}

                  {/* Edit/Delete Actions (if editable) */}
                  {onEditStep && onDeleteStep && isComplete && (
                    <div className="flex gap-2 mt-2">
                      <button
                        onClick={() => onEditStep(step.stepId, step.action)}
                        className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
                      >
                        <Edit2 className="w-3 h-3" />
                        Edit
                      </button>
                      <button
                        onClick={() => onDeleteStep(step.stepId)}
                        className="text-xs text-red-400 hover:text-red-300 flex items-center gap-1"
                      >
                        <Trash2 className="w-3 h-3" />
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Progress Indicator */}
      {isStreaming && displaySteps.length > 0 && (
        <div className="mt-4 pt-3 border-t border-gray-700">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <span>
              {displaySteps.filter(s => s.status === 'COMPLETE').length} / {displaySteps.length} steps complete
            </span>
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              Generating...
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

