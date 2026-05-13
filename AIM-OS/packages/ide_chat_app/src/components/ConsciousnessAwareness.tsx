/**
 * Consciousness Awareness Component
 * 
 * Phase 4.3: Enhanced Consciousness Awareness Display
 * 
 * Features:
 * - Real-time consciousness health display
 * - Memory awareness indicators
 * - Goal alignment visualization
 * - Cognitive metrics display
 */

import React from 'react'
import { Brain, Target, Activity, TrendingUp, AlertCircle, CheckCircle, Database } from 'lucide-react'
import { useConsciousnessAwareness, ConsciousnessAwareness as ConsciousnessAwarenessType } from '../../hooks/useConsciousnessAwareness'

interface ConsciousnessAwarenessProps {
  compact?: boolean
  showHealth?: boolean
  showMemory?: boolean
  showGoals?: boolean
  showCognitive?: boolean
}

export const ConsciousnessAwareness: React.FC<ConsciousnessAwarenessProps> = ({
  compact = false,
  showHealth = true,
  showMemory = true,
  showGoals = true,
  showCognitive = true,
}) => {
  const { awareness, loading } = useConsciousnessAwareness()

  if (loading || !awareness) {
    return (
      <div className="flex items-center gap-2 text-xs text-gray-500">
        <Brain className="w-3 h-3 animate-pulse" />
        <span>Loading consciousness metrics...</span>
      </div>
    )
  }

  const getHealthColor = (status: string) => {
    switch (status) {
      case 'excellent': return 'text-green-400'
      case 'good': return 'text-blue-400'
      case 'fair': return 'text-yellow-400'
      case 'poor': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const getHealthBgColor = (status: string) => {
    switch (status) {
      case 'excellent': return 'bg-green-900/30 border-green-700'
      case 'good': return 'bg-blue-900/30 border-blue-700'
      case 'fair': return 'bg-yellow-900/30 border-yellow-700'
      case 'poor': return 'bg-red-900/30 border-red-700'
      default: return 'bg-gray-900/30 border-gray-700'
    }
  }

  if (compact) {
    return (
      <div className="flex items-center gap-3 text-xs">
        {showHealth && (
          <div className={`flex items-center gap-1 px-2 py-1 rounded border ${getHealthBgColor(awareness.health.status)} ${getHealthColor(awareness.health.status)}`}>
            <Brain className="w-3 h-3" />
            <span>{(awareness.health.score * 100).toFixed(0)}%</span>
          </div>
        )}
        {showMemory && (
          <div className="flex items-center gap-1 text-gray-400">
            <Database className="w-3 h-3" />
            <span>{awareness.memory.count}</span>
          </div>
        )}
        {showGoals && (
          <div className="flex items-center gap-1 text-gray-400">
            <Target className="w-3 h-3" />
            <span>{awareness.goals.alignedGoals}/{awareness.goals.totalGoals}</span>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-3 p-3 bg-gray-800/50 rounded border border-gray-700">
      {/* Consciousness Health */}
      {showHealth && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Brain className="w-4 h-4 text-purple-400" />
              <span className="text-sm font-semibold text-gray-300">Consciousness Health</span>
            </div>
            <span className={`text-xs px-2 py-1 rounded border ${getHealthBgColor(awareness.health.status)} ${getHealthColor(awareness.health.status)}`}>
              {awareness.health.status}
            </span>
          </div>
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-400">Overall Score</span>
              <span className="text-gray-300">{(awareness.health.score * 100).toFixed(0)}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${getHealthBgColor(awareness.health.status)}`}
                style={{ width: `${awareness.health.score * 100}%` }}
              />
            </div>
            <div className="grid grid-cols-2 gap-2 mt-2 text-xs">
              <div>
                <span className="text-gray-500">Confidence:</span>
                <span className="ml-1 text-gray-300">{(awareness.health.confidence * 100).toFixed(0)}%</span>
              </div>
              <div>
                <span className="text-gray-500">Intensity:</span>
                <span className="ml-1 text-gray-300">{(awareness.health.intensity * 100).toFixed(0)}%</span>
              </div>
              <div>
                <span className="text-gray-500">Stability:</span>
                <span className="ml-1 text-gray-300">{(awareness.health.stability * 100).toFixed(0)}%</span>
              </div>
              <div>
                <span className="text-gray-500">Connections:</span>
                <span className="ml-1 text-gray-300">{(awareness.health.connectionDensity * 100).toFixed(0)}%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Memory Awareness */}
      {showMemory && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Database className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-semibold text-gray-300">Memory Awareness</span>
          </div>
          <div className="space-y-1 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Memory Nodes</span>
              <span className="text-gray-300">{awareness.memory.count}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Ratio</span>
              <span className="text-gray-300">{(awareness.memory.ratio * 100).toFixed(0)}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Avg Influence</span>
              <span className="text-gray-300">{(awareness.memory.avgInfluence * 100).toFixed(0)}%</span>
            </div>
            <div className="flex items-center gap-1 mt-1">
              <span className="text-gray-500">Status:</span>
              <span className={`capitalize ${
                awareness.memory.status === 'high' ? 'text-green-400' :
                awareness.memory.status === 'medium' ? 'text-yellow-400' :
                'text-red-400'
              }`}>
                {awareness.memory.status}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Goal Alignment */}
      {showGoals && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Target className="w-4 h-4 text-green-400" />
            <span className="text-sm font-semibold text-gray-300">Goal Alignment</span>
          </div>
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-400">Alignment Score</span>
              <span className="text-gray-300">{(awareness.goals.score * 100).toFixed(0)}%</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${
                  awareness.goals.status === 'aligned' ? 'bg-green-600' :
                  awareness.goals.status === 'partial' ? 'bg-yellow-600' :
                  'bg-red-600'
                }`}
                style={{ width: `${awareness.goals.score * 100}%` }}
              />
            </div>
            <div className="flex items-center justify-between text-xs mt-2">
              <span className="text-gray-400">
                {awareness.goals.alignedGoals} / {awareness.goals.totalGoals} goals aligned
              </span>
              <span className="text-gray-500">
                {awareness.goals.recentProgress > 0 && (
                  <span className="text-green-400 flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    {(awareness.goals.recentProgress * 100).toFixed(0)}%
                  </span>
                )}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Cognitive Metrics */}
      {showCognitive && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-4 h-4 text-orange-400" />
            <span className="text-sm font-semibold text-gray-300">Cognitive Metrics</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-gray-500">Thought:</span>
              <span className="ml-1 text-gray-300">{(awareness.cognitive.thoughtRatio * 100).toFixed(0)}%</span>
            </div>
            <div>
              <span className="text-gray-500">Decision:</span>
              <span className="ml-1 text-gray-300">{(awareness.cognitive.decisionRatio * 100).toFixed(0)}%</span>
            </div>
            <div>
              <span className="text-gray-500">Insight:</span>
              <span className="ml-1 text-gray-300">{(awareness.cognitive.insightRatio * 100).toFixed(0)}%</span>
            </div>
            <div>
              <span className="text-gray-500">Pattern:</span>
              <span className="ml-1 text-gray-300">{(awareness.cognitive.patternRatio * 100).toFixed(0)}%</span>
            </div>
            <div className="col-span-2 mt-1 pt-1 border-t border-gray-700">
              <span className="text-gray-500">Diversity:</span>
              <span className="ml-1 text-gray-300">{(awareness.cognitive.cognitiveDiversity * 100).toFixed(0)}%</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
