/**
 * Dynamic κ-Gating Badge Component
 * Displays gating determination and risk assessment
 * 
 * Phase 1 Week 4: Dynamic κ-Gating Enhancement
 */

import React from 'react'
import { AlertTriangle, CheckCircle2, XCircle, Lightbulb, Shield, Lock } from 'lucide-react'
import { getRiskCategoryColor, getRiskLevelColor } from '../../services/aetherChat/riskAssessment'
import type { RiskAssessment } from '../../services/aetherChat/riskAssessment'

export interface DynamicGatingBadgeProps {
  determination: 'PROCEED' | 'SPECULATE_WITH_WARNING' | 'ABSTAIN_AND_CLARIFY'
  riskAssessment?: {
    riskScore: number
    riskLevel: 'low' | 'medium' | 'high' | 'critical'
    category: 'casual' | 'informational' | 'modification' | 'destructive' | 'critical'
  }
  requiredConfidence?: number
  actualConfidence?: number
  className?: string
}

/**
 * Dynamic κ-Gating Badge Component
 * Shows the gating determination and risk level
 */
export const DynamicGatingBadge: React.FC<DynamicGatingBadgeProps> = ({
  determination,
  riskAssessment,
  requiredConfidence,
  actualConfidence,
  className = ''
}) => {
  const getDeterminationConfig = () => {
    switch (determination) {
      case 'PROCEED':
        return {
          icon: <CheckCircle2 className="w-4 h-4" />,
          text: 'Approved',
          color: 'bg-green-500/20 text-green-400 border-green-500/30',
          bgColor: 'bg-green-500/10'
        }
      case 'SPECULATE_WITH_WARNING':
        return {
          icon: <Lightbulb className="w-4 h-4" />,
          text: 'Speculative Mode',
          color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
          bgColor: 'bg-yellow-500/10'
        }
      case 'ABSTAIN_AND_CLARIFY':
        return {
          icon: <XCircle className="w-4 h-4" />,
          text: 'Blocked - Needs Clarification',
          color: 'bg-red-500/20 text-red-400 border-red-500/30',
          bgColor: 'bg-red-500/10'
        }
    }
  }

  const config = getDeterminationConfig()

  return (
    <div className={`rounded-lg border p-3 ${config.bgColor} ${className}`}>
      <div className="flex items-center gap-2 mb-2">
        {config.icon}
        <span className={`text-sm font-semibold ${config.color.replace('bg-', 'text-').replace('/20', '').replace('border-', '')}`}>
          {config.text}
        </span>
      </div>

      {riskAssessment && (
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-400">Risk Level:</span>
            <span className={getRiskLevelColor(riskAssessment.riskLevel)}>
              {riskAssessment.riskLevel.toUpperCase()} ({(riskAssessment.riskScore * 100).toFixed(0)}%)
            </span>
          </div>
          
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-400">Category:</span>
            <span className={`px-1.5 py-0.5 rounded text-xs border ${getRiskCategoryColor(riskAssessment.category)}`}>
              {riskAssessment.category}
            </span>
          </div>
        </div>
      )}

      {requiredConfidence !== undefined && actualConfidence !== undefined && (
        <div className="mt-2 pt-2 border-t border-gray-700">
          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-400">Confidence:</span>
            <div className="flex items-center gap-2">
              <span className={actualConfidence >= requiredConfidence ? 'text-green-400' : 'text-red-400'}>
                {(actualConfidence * 100).toFixed(0)}%
              </span>
              <span className="text-gray-500">/</span>
              <span className="text-gray-400">
                {(requiredConfidence * 100).toFixed(0)}% required
              </span>
            </div>
          </div>
        </div>
      )}

      {determination === 'ABSTAIN_AND_CLARIFY' && (
        <div className="mt-2 pt-2 border-t border-gray-700">
          <div className="flex items-start gap-2 text-xs text-yellow-400">
            <AlertTriangle className="w-3 h-3 mt-0.5 flex-shrink-0" />
            <span>
              This operation requires higher confidence. Please provide more context or clarification.
            </span>
          </div>
        </div>
      )}

      {determination === 'SPECULATE_WITH_WARNING' && (
        <div className="mt-2 pt-2 border-t border-gray-700">
          <div className="flex items-start gap-2 text-xs text-yellow-400">
            <Lightbulb className="w-3 h-3 mt-0.5 flex-shrink-0" />
            <span>
              This is a speculative response. Use with caution in production environments.
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * Speculative Mode Badge (for low-risk, low-confidence responses)
 */
export interface SpeculativeModeBadgeProps {
  className?: string
}

export const SpeculativeModeBadge: React.FC<SpeculativeModeBadgeProps> = ({ className = '' }) => {
  return (
    <div className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs border bg-yellow-500/20 text-yellow-400 border-yellow-500/30 ${className}`}>
      <Lightbulb className="w-3 h-3" />
      <span>Speculative Mode</span>
    </div>
  )
}

/**
 * Action Blocked Badge (for high-risk, low-confidence operations)
 */
export interface ActionBlockedBadgeProps {
  reason?: string
  className?: string
}

export const ActionBlockedBadge: React.FC<ActionBlockedBadgeProps> = ({ reason, className = '' }) => {
  return (
    <div className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs border bg-red-500/20 text-red-400 border-red-500/30 ${className}`}>
      <Lock className="w-3 h-3" />
      <span>Action Blocked</span>
      {reason && <span className="ml-1 text-xs">({reason})</span>}
    </div>
  )
}

