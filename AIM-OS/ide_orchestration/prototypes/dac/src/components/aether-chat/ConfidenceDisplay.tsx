/**
 * Confidence Display Component
 * Visualizes confidence scores and bands with detailed metrics
 * Created by Sage - Frontend Integration Specialist
 * Integrates with Alex's VIF hook
 */

import React from 'react'
import { TrendingUp, TrendingDown, Minus, BarChart3 } from 'lucide-react'
import { ConfidenceBadge } from '../shared'
import type { VIFWitness } from '../../hooks/useAIMOS'

export interface ConfidenceDisplayProps {
  confidence: number
  confidenceBand?: 'A' | 'B' | 'C'
  previousConfidence?: number
  witness?: VIFWitness
  showTrend?: boolean
  showDetails?: boolean
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export const ConfidenceDisplay: React.FC<ConfidenceDisplayProps> = ({
  confidence,
  confidenceBand,
  previousConfidence,
  witness,
  showTrend = true,
  showDetails = true,
  size = 'md',
  className = '',
}) => {
  // Determine confidence band if not provided
  const band: 'A' | 'B' | 'C' = confidenceBand || 
    (confidence >= 0.90 ? 'A' :
     confidence >= 0.70 ? 'B' : 'C')

  // Calculate trend
  const trend = previousConfidence !== undefined
    ? confidence - previousConfidence
    : null

  // Size configuration
  const sizeConfig = {
    sm: {
      badge: 'sm' as const,
      text: 'text-xs',
      barHeight: 'h-1',
      iconSize: 'w-3 h-3'
    },
    md: {
      badge: 'md' as const,
      text: 'text-sm',
      barHeight: 'h-2',
      iconSize: 'w-4 h-4'
    },
    lg: {
      badge: 'lg' as const,
      text: 'text-base',
      barHeight: 'h-3',
      iconSize: 'w-5 h-5'
    }
  }

  const config = sizeConfig[size]

  return (
    <div className={`flex flex-col gap-3 ${className}`}>
      {/* Main Confidence Display */}
      <div className="flex items-center gap-3">
        <ConfidenceBadge 
          confidence={confidence} 
          band={band} 
          size={config.badge}
          showPercentage={true}
        />
        {showTrend && trend !== null && (
          <div className="flex items-center gap-1">
            {trend > 0 ? (
              <TrendingUp className={`${config.iconSize} text-green-400`} />
            ) : trend < 0 ? (
              <TrendingDown className={`${config.iconSize} text-red-400`} />
            ) : (
              <Minus className={`${config.iconSize} text-gray-400`} />
            )}
            {trend !== 0 && (
              <span className={`${config.text} ${
                trend > 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {trend > 0 ? '+' : ''}{(trend * 100).toFixed(1)}%
              </span>
            )}
          </div>
        )}
      </div>

      {/* Confidence Bar */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center justify-between">
          <span className={`${config.text} text-gray-400`}>Confidence</span>
          <span className={`${config.text} font-semibold text-gray-200`}>
            {(confidence * 100).toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-gray-700 rounded-full overflow-hidden">
          <div
            className={`${config.barHeight} rounded-full transition-all ${
              band === 'A' ? 'bg-green-500' :
              band === 'B' ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${confidence * 100}%` }}
          />
        </div>
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>0%</span>
          <span className="flex items-center gap-1">
            <BarChart3 className="w-3 h-3" />
            {band === 'A' && 'High (90-100%)'}
            {band === 'B' && 'Medium (70-89%)'}
            {band === 'C' && 'Low (<70%)'}
          </span>
          <span>100%</span>
        </div>
      </div>

      {/* Details */}
      {showDetails && (
        <div className="bg-gray-800 rounded p-3 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400">Confidence Band</span>
            <span className={`text-xs font-semibold ${
              band === 'A' ? 'text-green-400' :
              band === 'B' ? 'text-yellow-400' : 'text-red-400'
            }`}>
              {band}
            </span>
          </div>
          {witness && (
            <>
              {witness.kappa_gate_passed !== undefined && (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-400">Kappa Gate</span>
                  <span className={`text-xs font-semibold ${
                    witness.kappa_gate_passed ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {witness.kappa_gate_passed ? 'Passed' : 'Failed'}
                  </span>
                </div>
              )}
              {witness.ece_score !== undefined && (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-400">ECE Score</span>
                  <span className={`text-xs font-semibold ${
                    witness.ece_score < 0.1 ? 'text-green-400' :
                    witness.ece_score < 0.2 ? 'text-yellow-400' : 'text-red-400'
                  }`}>
                    {witness.ece_score.toFixed(3)}
                  </span>
                </div>
              )}
              {witness.task_criticality && (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-400">Task Criticality</span>
                  <span className="text-xs font-semibold text-gray-300">
                    {witness.task_criticality.charAt(0).toUpperCase() + witness.task_criticality.slice(1)}
                  </span>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}

