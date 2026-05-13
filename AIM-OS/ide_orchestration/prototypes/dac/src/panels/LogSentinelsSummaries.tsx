// Log-Sentinels Summaries Panel - Bottom Right AI Summaries
// Displays Scout reports with summaries, confidence, severity, and suggested tools

import React from 'react'
import { useLogSentinels } from '../hooks/useLogSentinels'
import { BasePanel } from '../components/BasePanel'
import { LoadingSpinner, ErrorDisplay } from '../components/shared/shared'
import { 
  Brain, 
  AlertCircle, 
  CheckCircle, 
  Zap,
  Clock
} from 'lucide-react'

export const LogSentinelsSummaries: React.FC = () => {
  const { scouts, loading, error } = useLogSentinels()

  if (loading) {
    return (
      <BasePanel id="log-sentinels-summaries" title="AI Summaries" icon={Brain}>
        <LoadingSpinner />
      </BasePanel>
    )
  }

  if (error) {
    return (
      <BasePanel id="log-sentinels-summaries" title="AI Summaries" icon={Brain}>
        <ErrorDisplay error={error} />
      </BasePanel>
    )
  }

  return (
    <BasePanel id="log-sentinels-summaries" title="AI Summaries" icon={Brain}>
      <div className="flex flex-col gap-2 p-2">
        {scouts.length === 0 ? (
          <div className="text-gray-400 text-sm text-center py-8">
            No Scout reports available
          </div>
        ) : (
          scouts.map((scout) => (
            <ScoutCard key={scout.window_id} scout={scout} />
          ))
        )}
      </div>
    </BasePanel>
  )
}

interface ScoutCardProps {
  scout: any
}

const ScoutCard: React.FC<ScoutCardProps> = ({ scout }) => {
  const severityColors = {
    low: 'text-blue-400 border-blue-500 bg-blue-900/20',
    medium: 'text-yellow-400 border-yellow-500 bg-yellow-900/20',
    high: 'text-red-400 border-red-500 bg-red-900/20'
  }

  const severityColor = severityColors[scout.severity] || severityColors.low

  return (
    <div className="border border-gray-700 rounded-lg p-3 bg-gray-800/50 hover:bg-gray-800 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-xs px-2 py-1 rounded border ${severityColor}`}>
              {scout.severity.toUpperCase()}
            </span>
            <span className="text-xs text-gray-400">
              {scout.confidence ? `${Math.round(scout.confidence * 100)}% conf` : ''}
            </span>
          </div>
          
          <p className="text-sm text-gray-200 mb-2">{scout.summary}</p>
          
          {scout.tags && scout.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              {scout.tags.map((tag: string, idx: number) => (
                <span
                  key={idx}
                  className="text-xs px-2 py-0.5 bg-gray-700 rounded text-gray-300"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
        
        {scout.timestamp && (
          <div className="text-xs text-gray-500 flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {new Date(scout.timestamp).toLocaleTimeString()}
          </div>
        )}
      </div>

      {scout.suggested_tools && scout.suggested_tools.length > 0 && (
        <div className="mt-2 pt-2 border-t border-gray-700">
          <div className="flex items-center gap-1 mb-1">
            <Zap className="w-3 h-3 text-blue-400" />
            <span className="text-xs text-gray-400">Suggested Tools:</span>
          </div>
          <div className="flex flex-wrap gap-1">
            {scout.suggested_tools.map((tool: string, idx: number) => (
              <span
                key={idx}
                className="text-xs px-2 py-0.5 bg-blue-900/30 border border-blue-700 rounded text-blue-300"
              >
                {tool}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

