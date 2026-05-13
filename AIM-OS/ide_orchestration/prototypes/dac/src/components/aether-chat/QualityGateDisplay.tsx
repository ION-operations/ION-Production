/**
 * Quality Gate Display Component
 * Displays VIF quality gate status and kappa gate results
 * Created by Sage - Frontend Integration Specialist
 * Integrates with Alex's VIF hook
 */

import React from 'react'
import { Shield, CheckCircle, XCircle, AlertTriangle, Info } from 'lucide-react'
import { ConfidenceBadge } from '../shared'
import type { VIFWitness } from '../../hooks/useAIMOS'

export interface QualityGateDisplayProps {
  witness?: VIFWitness
  confidence?: number
  confidenceBand?: 'A' | 'B' | 'C'
  kappaGatePassed?: boolean
  kappaThreshold?: number
  taskCriticality?: 'critical' | 'important' | 'routine' | 'low_stakes'
  eceScore?: number
  showDetails?: boolean
  className?: string
}

export const QualityGateDisplay: React.FC<QualityGateDisplayProps> = ({
  witness,
  confidence = witness?.confidence_score,
  confidenceBand = witness?.confidence_band,
  kappaGatePassed = witness?.kappa_gate_passed,
  kappaThreshold = witness?.kappa_threshold,
  taskCriticality = witness?.task_criticality || 'routine',
  eceScore = witness?.ece_score,
  showDetails = true,
  className = '',
}) => {
  // Determine gate status
  const gateStatus = kappaGatePassed ? 'passed' : 'failed'
  const hasWitness = !!witness

  // Task criticality configuration
  const criticalityConfig = {
    critical: {
      label: 'Critical',
      color: 'text-red-400',
      bgColor: 'bg-red-900/20',
      borderColor: 'border-red-700/50',
      threshold: 0.95
    },
    important: {
      label: 'Important',
      color: 'text-orange-400',
      bgColor: 'bg-orange-900/20',
      borderColor: 'border-orange-700/50',
      threshold: 0.85
    },
    routine: {
      label: 'Routine',
      color: 'text-blue-400',
      bgColor: 'bg-blue-900/20',
      borderColor: 'border-blue-700/50',
      threshold: 0.70
    },
    low_stakes: {
      label: 'Low Stakes',
      color: 'text-gray-400',
      bgColor: 'bg-gray-900/20',
      borderColor: 'border-gray-700/50',
      threshold: 0.60
    }
  }

  const critConfig = criticalityConfig[taskCriticality]
  const threshold = kappaThreshold || critConfig.threshold

  return (
    <div className={`flex flex-col gap-3 ${className}`}>
      {/* Main Gate Status */}
      <div className={`flex items-center gap-3 p-4 rounded-lg border ${
        gateStatus === 'passed'
          ? 'bg-green-900/20 border-green-700/50'
          : 'bg-red-900/20 border-red-700/50'
      }`}>
        <div className="flex-shrink-0">
          {gateStatus === 'passed' ? (
            <CheckCircle className="w-6 h-6 text-green-400" />
          ) : (
            <XCircle className="w-6 h-6 text-red-400" />
          )}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <Shield className="w-4 h-4 text-gray-400" />
            <span className={`text-sm font-semibold ${
              gateStatus === 'passed' ? 'text-green-400' : 'text-red-400'
            }`}>
              Quality Gate {gateStatus === 'passed' ? 'Passed' : 'Failed'}
            </span>
          </div>
          <div className="flex items-center gap-3">
            {confidence !== undefined && (
              <ConfidenceBadge confidence={confidence} band={confidenceBand} size="sm" />
            )}
            <span className="text-xs text-gray-400">
              Threshold: {(threshold * 100).toFixed(0)}%
            </span>
            <span className={`text-xs ${critConfig.color}`}>
              {critConfig.label}
            </span>
          </div>
        </div>
      </div>

      {/* Details */}
      {showDetails && (
        <div className="flex flex-col gap-2">
          {/* Confidence Details */}
          {confidence !== undefined && (
            <div className="bg-gray-800 rounded p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-gray-400">Confidence Score</span>
                <span className="text-sm font-semibold text-gray-200">
                  {(confidence * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${
                    confidence >= 0.90 ? 'bg-green-500' :
                    confidence >= 0.70 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${confidence * 100}%` }}
                />
              </div>
              {confidenceBand && (
                <div className="mt-2 text-xs text-gray-500">
                  Band: <span className="font-medium">{confidenceBand}</span>
                  {confidenceBand === 'A' && ' (0.90-1.00)'}
                  {confidenceBand === 'B' && ' (0.70-0.89)'}
                  {confidenceBand === 'C' && ' (<0.70)'}
                </div>
              )}
            </div>
          )}

          {/* Kappa Gate Details */}
          {kappaThreshold !== undefined && (
            <div className="bg-gray-800 rounded p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-gray-400">Kappa Gate</span>
                <span className={`text-xs font-semibold ${
                  kappaGatePassed ? 'text-green-400' : 'text-red-400'
                }`}>
                  {kappaGatePassed ? 'PASSED' : 'FAILED'}
                </span>
              </div>
              <div className="text-xs text-gray-500">
                Required: {(kappaThreshold * 100).toFixed(0)}% for {critConfig.label} tasks
                {confidence !== undefined && (
                  <span className="ml-2">
                    ({confidence >= kappaThreshold ? '✓' : '✗'} {(confidence * 100).toFixed(1)}%)
                  </span>
                )}
              </div>
            </div>
          )}

          {/* ECE Score */}
          {eceScore !== undefined && (
            <div className="bg-gray-800 rounded p-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-400">ECE Score</span>
                <span className={`text-xs font-semibold ${
                  eceScore < 0.1 ? 'text-green-400' :
                  eceScore < 0.2 ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {eceScore.toFixed(3)}
                </span>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Expected Calibration Error (lower is better)
              </div>
            </div>
          )}

          {/* Witness Info */}
          {hasWitness && witness && (
            <div className="bg-gray-800 rounded p-3">
              <div className="flex items-center gap-2 mb-2">
                <Info className="w-3 h-3 text-gray-400" />
                <span className="text-xs font-medium text-gray-400">VIF Witness</span>
              </div>
              <div className="text-xs text-gray-500 space-y-1">
                <div>ID: <span className="font-mono text-gray-400">{witness.id.slice(0, 16)}...</span></div>
                {witness.model_id && (
                  <div>Model: <span className="text-gray-400">{witness.model_id}</span></div>
                )}
                {witness.prompt_tokens && (
                  <div>Tokens: <span className="text-gray-400">{witness.prompt_tokens}</span></div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

