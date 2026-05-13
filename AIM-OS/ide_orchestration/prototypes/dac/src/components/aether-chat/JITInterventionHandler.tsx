/**
 * JIT Intervention Handler Component
 * Handles Just-in-Time intervention for editable APOE plans
 * 
 * Phase 3 Week 12: JIT Intervention (Gemini Pro Enhancement)
 */

import React, { useState } from 'react'
import { Pause, Play, Save, X, AlertCircle, CheckCircle2, DollarSign } from 'lucide-react'
import type { ResponsePlan, StreamingPlanStep } from '../../types/aetherChatTypes'

export interface JITInterventionState {
  isPaused: boolean
  editedSteps: Map<string, { action: string; originalAction: string }>
  deletedSteps: Set<string>
  reorderedSteps: string[] // Step IDs in new order
  validationErrors: Array<{ stepId: string; error: string }>
  costSaved: number // Estimated cost saved from interventions
}

export interface JITInterventionHandlerProps {
  plan: ResponsePlan
  streamingSteps?: StreamingPlanStep[]
  onIntervention?: (state: JITInterventionState) => void
  onPause?: () => void
  onResume?: () => void
  onSave?: (editedPlan: ResponsePlan) => void
  onCancel?: () => void
  className?: string
}

export const JITInterventionHandler: React.FC<JITInterventionHandlerProps> = ({
  plan,
  streamingSteps = [],
  onIntervention,
  onPause,
  onResume,
  onSave,
  onCancel,
  className = ''
}) => {
  const [isPaused, setIsPaused] = useState(false)
  const [editedSteps, setEditedSteps] = useState<Map<string, { action: string; originalAction: string }>>(new Map())
  const [deletedSteps, setDeletedSteps] = useState<Set<string>>(new Set())
  const [reorderedSteps, setReorderedSteps] = useState<string[]>(plan.steps.map(s => s.stepId))
  const [validationErrors, setValidationErrors] = useState<Array<{ stepId: string; error: string }>>([])
  const [editingStepId, setEditingStepId] = useState<string | null>(null)
  const [editText, setEditText] = useState('')

  // Calculate cost saved from interventions
  const calculateCostSaved = (): number => {
    let saved = 0
    deletedSteps.forEach(stepId => {
      const step = plan.steps.find(s => s.stepId === stepId)
      if (step) {
        // Estimate cost based on action length (rough estimate: $0.001 per 100 tokens)
        const estimatedTokens = step.action.length / 4 // Rough estimate
        saved += (estimatedTokens / 1000) * 0.001
      }
    })
    return saved
  }

  const costSaved = calculateCostSaved()

  // Validate plan after intervention
  const validatePlan = (): Array<{ stepId: string; error: string }> => {
    const errors: Array<{ stepId: string; error: string }> = []
    const remainingSteps = plan.steps.filter(s => !deletedSteps.has(s.stepId))
    
    // Check for circular dependencies
    const stepIds = new Set(remainingSteps.map(s => s.stepId))
    remainingSteps.forEach(step => {
      step.dependencies?.forEach(depId => {
        if (!stepIds.has(depId) && !deletedSteps.has(depId)) {
          errors.push({
            stepId: step.stepId,
            error: `Dependency ${depId} not found or was deleted`
          })
        }
      })
    })

    // Check for empty actions
    remainingSteps.forEach(step => {
      const editedAction = editedSteps.get(step.stepId)?.action
      const action = editedAction || step.action
      if (!action || action.trim().length === 0) {
        errors.push({
          stepId: step.stepId,
          error: 'Action cannot be empty'
        })
      }
    })

    return errors
  }

  const handlePause = () => {
    setIsPaused(true)
    onPause?.()
  }

  const handleResume = () => {
    const errors = validatePlan()
    setValidationErrors(errors)
    
    if (errors.length === 0) {
      setIsPaused(false)
      onResume?.()
    }
  }

  const handleEditStep = (stepId: string) => {
    const step = plan.steps.find(s => s.stepId === stepId)
    if (step) {
      const edited = editedSteps.get(stepId)
      setEditText(edited?.action || step.action)
      setEditingStepId(stepId)
    }
  }

  const handleSaveEdit = () => {
    if (editingStepId) {
      const step = plan.steps.find(s => s.stepId === editingStepId)
      if (step) {
        const updated = new Map(editedSteps)
        updated.set(editingStepId, {
          action: editText,
          originalAction: step.action
        })
        setEditedSteps(updated)
        
        // Validate after edit
        const errors = validatePlan()
        setValidationErrors(errors)
        
        // Notify parent
        const interventionState: JITInterventionState = {
          isPaused,
          editedSteps: updated,
          deletedSteps,
          reorderedSteps,
          validationErrors: errors,
          costSaved: calculateCostSaved()
        }
        onIntervention?.(interventionState)
      }
      setEditingStepId(null)
      setEditText('')
    }
  }

  const handleDeleteStep = (stepId: string) => {
    const updated = new Set(deletedSteps)
    updated.add(stepId)
    setDeletedSteps(updated)
    
    // Remove from reordered steps
    setReorderedSteps(prev => prev.filter(id => id !== stepId))
    
    // Validate after deletion
    const errors = validatePlan()
    setValidationErrors(errors)
    
    // Notify parent
    const interventionState: JITInterventionState = {
      isPaused,
      editedSteps,
      deletedSteps: updated,
      reorderedSteps: reorderedSteps.filter(id => id !== stepId),
      validationErrors: errors,
      costSaved: calculateCostSaved()
    }
    onIntervention?.(interventionState)
  }

  const handleSave = () => {
    const errors = validatePlan()
    if (errors.length > 0) {
      setValidationErrors(errors)
      return
    }

    // Build edited plan
    const remainingSteps = plan.steps
      .filter(s => !deletedSteps.has(s.stepId))
      .map(step => {
        const edited = editedSteps.get(step.stepId)
        return {
          ...step,
          action: edited?.action || step.action
        }
      })
      .sort((a, b) => {
        const aIndex = reorderedSteps.indexOf(a.stepId)
        const bIndex = reorderedSteps.indexOf(b.stepId)
        return aIndex - bIndex
      })

    const editedPlan: ResponsePlan = {
      ...plan,
      steps: remainingSteps,
      budget: {
        ...plan.budget,
        cost: (plan.budget?.cost || 0) - costSaved
      }
    }

    onSave?.(editedPlan)
  }

  return (
    <div className={`bg-gray-800/50 border border-gray-700 rounded-lg p-4 ${className}`}>
      {/* Intervention Controls */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          {isPaused ? (
            <>
              <Pause className="w-4 h-4 text-yellow-400" />
              <span className="text-sm text-yellow-400 font-medium">Paused for Intervention</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 text-green-400" />
              <span className="text-sm text-gray-300">Plan Execution Active</span>
            </>
          )}
        </div>
        <div className="flex items-center gap-2">
          {costSaved > 0 && (
            <div className="flex items-center gap-1 px-2 py-1 bg-green-500/20 border border-green-500/30 rounded text-xs text-green-400">
              <DollarSign className="w-3 h-3" />
              <span>Saved: ${costSaved.toFixed(4)}</span>
            </div>
          )}
          {!isPaused ? (
            <button
              onClick={handlePause}
              className="px-3 py-1 bg-yellow-600 hover:bg-yellow-700 text-white text-xs rounded transition-colors flex items-center gap-1"
            >
              <Pause className="w-3 h-3" />
              Pause
            </button>
          ) : (
            <button
              onClick={handleResume}
              className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-xs rounded transition-colors flex items-center gap-1"
            >
              <Play className="w-3 h-3" />
              Resume
            </button>
          )}
          {isPaused && (
            <>
              <button
                onClick={handleSave}
                className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors flex items-center gap-1"
              >
                <Save className="w-3 h-3" />
                Save Changes
              </button>
              {onCancel && (
                <button
                  onClick={onCancel}
                  className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white text-xs rounded transition-colors flex items-center gap-1"
                >
                  <X className="w-3 h-3" />
                  Cancel
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {/* Validation Errors */}
      {validationErrors.length > 0 && (
        <div className="mb-4 p-3 bg-red-500/20 border border-red-500/30 rounded">
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="w-4 h-4 text-red-400" />
            <span className="text-sm font-medium text-red-400">Validation Errors</span>
          </div>
          <ul className="space-y-1">
            {validationErrors.map((error, index) => (
              <li key={index} className="text-xs text-red-300">
                Step {error.stepId}: {error.error}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Edit Step Modal */}
      {editingStepId && (
        <div className="mb-4 p-3 bg-gray-900 border border-gray-700 rounded">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-300">Edit Step</span>
            <button
              onClick={() => {
                setEditingStepId(null)
                setEditText('')
              }}
              className="text-gray-400 hover:text-gray-300"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          <textarea
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            className="w-full p-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-200 resize-none"
            rows={3}
            placeholder="Enter step action..."
          />
          <div className="flex justify-end gap-2 mt-2">
            <button
              onClick={() => {
                setEditingStepId(null)
                setEditText('')
              }}
              className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white text-xs rounded transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveEdit}
              className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors flex items-center gap-1"
            >
              <CheckCircle2 className="w-3 h-3" />
              Save
            </button>
          </div>
        </div>
      )}

      {/* Intervention Summary */}
      {isPaused && (editedSteps.size > 0 || deletedSteps.size > 0) && (
        <div className="mb-4 p-3 bg-blue-500/20 border border-blue-500/30 rounded">
          <div className="text-sm font-medium text-blue-400 mb-2">Intervention Summary</div>
          <div className="space-y-1 text-xs text-gray-300">
            {editedSteps.size > 0 && (
              <div>Edited steps: {editedSteps.size}</div>
            )}
            {deletedSteps.size > 0 && (
              <div>Deleted steps: {deletedSteps.size}</div>
            )}
            {reorderedSteps.length !== plan.steps.length && (
              <div>Reordered steps: {plan.steps.length} → {reorderedSteps.length}</div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

