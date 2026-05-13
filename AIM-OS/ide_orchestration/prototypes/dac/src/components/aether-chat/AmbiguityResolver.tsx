/**
 * Ambiguity Resolver Component
 * Forked Path UI for clarifying ambiguous user queries
 * 
 * Phase 1 Week 3: Ambiguity Detection Enhancement
 */

import React from 'react'
import { HelpCircle, CheckCircle2, AlertCircle, FileText, MessageSquare, Link } from 'lucide-react'
import { ConfidenceDisplay } from './ConfidenceDisplay'
import type { AmbiguityState } from '../../types/aetherChatTypes'

export interface AmbiguityResolverProps {
  ambiguity: AmbiguityState
  onResolve: (selectedInterpretation: number) => void
  onCancel?: () => void
  className?: string
}

/**
 * Ambiguity Resolver Component
 * Displays "Forked Path" UI when user query is ambiguous
 */
export const AmbiguityResolver: React.FC<AmbiguityResolverProps> = ({
  ambiguity,
  onResolve,
  onCancel,
  className = ''
}) => {
  if (!ambiguity.isAmbiguous || ambiguity.interpretations.length === 0) {
    return null
  }

  return (
    <div className={`bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4 ${className}`}>
      <div className="flex items-start gap-3 mb-4">
        <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-yellow-300 mb-1">
            {ambiguity.forkedPathUI?.question || "I see multiple potential interpretations. Which one?"}
          </h3>
          <p className="text-xs text-yellow-400/80">
            Ambiguity Score: {(ambiguity.ambiguityScore * 100).toFixed(0)}%
          </p>
        </div>
      </div>

      <div className="space-y-2 mb-4">
        {ambiguity.interpretations.map((interpretation, index) => (
          <PathOption
            key={index}
            interpretation={interpretation}
            index={index}
            onSelect={() => onResolve(index)}
          />
        ))}
      </div>

      {onCancel && (
        <div className="flex justify-end pt-3 border-t border-yellow-500/20">
          <button
            onClick={onCancel}
            className="text-xs text-yellow-400/80 hover:text-yellow-300 transition-colors"
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  )
}

/**
 * Individual Path Option Component
 */
interface PathOptionProps {
  interpretation: {
    intent: string
    confidence: {
      value: number
      band: 'A' | 'B' | 'C' | 'S'
    }
    supportingEvidence?: string[]
  }
  index: number
  onSelect: () => void
}

const PathOption: React.FC<PathOptionProps> = ({
  interpretation,
  index,
  onSelect
}) => {
  const [showEvidence, setShowEvidence] = React.useState(false)

  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3 hover:border-yellow-500/50 transition-colors">
      <button
        onClick={onSelect}
        className="w-full text-left"
      >
        <div className="flex items-start gap-3">
          {/* Option Number */}
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-yellow-500/20 border border-yellow-500/30 flex items-center justify-center">
            <span className="text-sm font-semibold text-yellow-300">
              {index + 1}
            </span>
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-medium text-gray-200">
                {interpretation.intent}
              </span>
              <ConfidenceDisplay
                confidence={interpretation.confidence.value}
                confidenceBand={interpretation.confidence.band}
                size="xs"
              />
            </div>

            {/* Evidence Count */}
            {interpretation.supportingEvidence && interpretation.supportingEvidence.length > 0 && (
              <div className="flex items-center gap-1 mt-2">
                <FileText className="w-3 h-3 text-gray-500" />
                <span className="text-xs text-gray-500">
                  {interpretation.supportingEvidence.length} evidence source{interpretation.supportingEvidence.length !== 1 ? 's' : ''}
                </span>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    setShowEvidence(!showEvidence)
                  }}
                  className="text-xs text-blue-400 hover:text-blue-300 ml-2"
                >
                  {showEvidence ? 'Hide' : 'Show'} evidence
                </button>
              </div>
            )}

            {/* Evidence List */}
            {showEvidence && interpretation.supportingEvidence && interpretation.supportingEvidence.length > 0 && (
              <div className="mt-2 pl-4 border-l-2 border-gray-700 space-y-1">
                {interpretation.supportingEvidence.map((evidenceId, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-2 text-xs text-gray-400"
                  >
                    <Link className="w-3 h-3" />
                    <span className="font-mono truncate">{evidenceId}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Select Indicator */}
          <div className="flex-shrink-0">
            <CheckCircle2 className="w-5 h-5 text-gray-600 group-hover:text-yellow-400 transition-colors" />
          </div>
        </div>
      </button>
    </div>
  )
}

/**
 * Ambiguity Badge Component
 * Small indicator for ambiguous messages
 */
export interface AmbiguityBadgeProps {
  ambiguityScore: number
  className?: string
}

export const AmbiguityBadge: React.FC<AmbiguityBadgeProps> = ({
  ambiguityScore,
  className = ''
}) => {
  if (ambiguityScore < 0.3) {
    return null // Don't show badge for low ambiguity
  }

  const getColor = () => {
    if (ambiguityScore >= 0.7) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
    if (ambiguityScore >= 0.5) return 'bg-orange-500/20 text-orange-400 border-orange-500/30'
    return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
  }

  return (
    <div className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs border ${getColor()} ${className}`}>
      <HelpCircle className="w-3 h-3" />
      <span>Ambiguous ({(ambiguityScore * 100).toFixed(0)}%)</span>
    </div>
  )
}

