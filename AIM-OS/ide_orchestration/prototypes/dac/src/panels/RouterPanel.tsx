// Router Panel - Right Drawer Tool Selection
// Displays Router tool proposals with probabilities, reasons, and preconditions

import React from 'react'
import { useRouter } from '../hooks/useRouter'
import { BasePanel } from '../components/BasePanel'
import { LoadingSpinner, ErrorDisplay } from '../components/shared/shared'
import { 
  Zap, 
  CheckCircle, 
  XCircle, 
  Clock, 
  TrendingUp, 
  TrendingDown,
  Play,
  Info
} from 'lucide-react'

export const RouterPanel: React.FC = () => {
  const { tools, suggestions, loading, error, executeTool } = useRouter()

  if (loading) {
    return (
      <BasePanel id="router-panel" title="Tool Selection" icon={Zap}>
        <LoadingSpinner />
      </BasePanel>
    )
  }

  if (error) {
    return (
      <BasePanel id="router-panel" title="Tool Selection" icon={Zap}>
        <ErrorDisplay error={error} />
      </BasePanel>
    )
  }

  const displayTools = suggestions.length > 0 ? suggestions : tools

  return (
    <BasePanel id="router-panel" title="Tool Selection" icon={Zap}>
      <div className="flex flex-col gap-2 p-2">
        {displayTools.length === 0 ? (
          <div className="text-gray-400 text-sm text-center py-8">
            No tool suggestions available
          </div>
        ) : (
          displayTools.map((tool, index) => (
            <ToolCard
              key={`${tool.tool_name}-${index}`}
              tool={tool}
              onExecute={executeTool}
            />
          ))
        )}
      </div>
    </BasePanel>
  )
}

interface ToolCardProps {
  tool: any
  onExecute: (toolName: string, args: Record<string, any>) => Promise<any>
}

const ToolCard: React.FC<ToolCardProps> = ({ tool, onExecute }) => {
  const [executing, setExecuting] = React.useState(false)

  const handleExecute = async () => {
    setExecuting(true)
    try {
      await onExecute(tool.tool_name, tool.draft_arguments || {})
    } catch (err) {
      console.error('Failed to execute tool:', err)
    } finally {
      setExecuting(false)
    }
  }

  const probability = tool.probability || tool.confidence || 0
  const probabilityPercent = Math.round(probability * 100)

  return (
    <div className="border border-gray-700 rounded-lg p-3 bg-gray-800/50 hover:bg-gray-800 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-semibold text-sm text-gray-200">
              {tool.tool_name}
            </h4>
            {tool.precondition_satisfied !== undefined && (
              tool.precondition_satisfied ? (
                <CheckCircle className="w-4 h-4 text-green-400" />
              ) : (
                <XCircle className="w-4 h-4 text-red-400" />
              )
            )}
          </div>
          
          {tool.rationale && (
            <p className="text-xs text-gray-400 mb-2">{tool.rationale}</p>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <div className="text-right">
            <div className="text-xs text-gray-400">Probability</div>
            <div className="text-sm font-semibold text-blue-400">
              {probabilityPercent}%
            </div>
          </div>
          <button
            onClick={handleExecute}
            disabled={executing || !tool.precondition_satisfied}
            className="px-2 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded text-xs flex items-center gap-1"
          >
            <Play className="w-3 h-3" />
            {executing ? 'Running...' : 'Run'}
          </button>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mt-2">
        {tool.context_fit !== undefined && (
          <MetricBadge
            label="Fit"
            value={Math.round(tool.context_fit * 100)}
            icon={TrendingUp}
          />
        )}
        {tool.success_rate !== undefined && (
          <MetricBadge
            label="Success"
            value={Math.round(tool.success_rate * 100)}
            icon={tool.success_rate > 0.7 ? TrendingUp : TrendingDown}
          />
        )}
        {tool.expected_info_gain !== undefined && (
          <MetricBadge
            label="Info Gain"
            value={Math.round(tool.expected_info_gain * 100)}
            icon={Info}
          />
        )}
        {tool.parallelizable && (
          <span className="text-xs text-gray-500 flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Parallel
          </span>
        )}
      </div>
    </div>
  )
}

interface MetricBadgeProps {
  label: string
  value: number
  icon: React.ComponentType<{ className?: string }>
}

const MetricBadge: React.FC<MetricBadgeProps> = ({ label, value, icon: Icon }) => (
  <div className="flex items-center gap-1 text-xs text-gray-400">
    <Icon className="w-3 h-3" />
    <span>{label}: {value}%</span>
  </div>
)

