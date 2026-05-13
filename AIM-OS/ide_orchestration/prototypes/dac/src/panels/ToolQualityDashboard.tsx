// Tool Quality Dashboard - Router Telemetry
// Displays Router tool quality metrics: latency, success rate, cost, and per-tool statistics

import React from 'react'
import { useRouter } from '../hooks/useRouter'
import { BasePanel } from '../components/BasePanel'
import { LoadingSpinner, ErrorDisplay } from '../components/shared/shared'
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  Clock,
  CheckCircle,
  DollarSign
} from 'lucide-react'

export const ToolQualityDashboard: React.FC = () => {
  const { telemetry, loading, error } = useRouter()

  if (loading) {
    return (
      <BasePanel id="tool-quality-dashboard" title="Tool Quality" icon={Activity}>
        <LoadingSpinner />
      </BasePanel>
    )
  }

  if (error) {
    return (
      <BasePanel id="tool-quality-dashboard" title="Tool Quality" icon={Activity}>
        <ErrorDisplay error={error} />
      </BasePanel>
    )
  }

  if (!telemetry) {
    return (
      <BasePanel id="tool-quality-dashboard" title="Tool Quality" icon={Activity}>
        <div className="text-gray-400 text-sm text-center py-8">
          No telemetry data available
        </div>
      </BasePanel>
    )
  }

  return (
    <BasePanel id="tool-quality-dashboard" title="Tool Quality" icon={Activity}>
      <div className="flex flex-col gap-4 p-4">
        <MetricsGrid telemetry={telemetry} />
        <ToolList tools={telemetry.tools} />
      </div>
    </BasePanel>
  )
}

interface MetricsGridProps {
  telemetry: any
}

const MetricsGrid: React.FC<MetricsGridProps> = ({ telemetry }) => {
  const TrendIcon = telemetry.latency_trend === 'up' 
    ? TrendingUp 
    : telemetry.latency_trend === 'down'
    ? TrendingDown
    : Minus

  const SuccessTrendIcon = telemetry.success_trend === 'up'
    ? TrendingUp
    : telemetry.success_trend === 'down'
    ? TrendingDown
    : Minus

  const CostTrendIcon = telemetry.cost_trend === 'up'
    ? TrendingUp
    : telemetry.cost_trend === 'down'
    ? TrendingDown
    : Minus

  return (
    <div className="grid grid-cols-3 gap-4">
      <MetricCard
        label="Average Latency"
        value={`${telemetry.avg_latency.toFixed(0)}ms`}
        icon={Clock}
        trend={telemetry.latency_trend}
        trendIcon={TrendIcon}
      />
      <MetricCard
        label="Success Rate"
        value={`${(telemetry.success_rate * 100).toFixed(1)}%`}
        icon={CheckCircle}
        trend={telemetry.success_trend}
        trendIcon={SuccessTrendIcon}
      />
      <MetricCard
        label="Average Cost"
        value={`$${telemetry.avg_cost.toFixed(4)}`}
        icon={DollarSign}
        trend={telemetry.cost_trend}
        trendIcon={CostTrendIcon}
      />
    </div>
  )
}

interface MetricCardProps {
  label: string
  value: string
  icon: React.ComponentType<{ className?: string }>
  trend: 'up' | 'down' | 'stable'
  trendIcon: React.ComponentType<{ className?: string }>
}

const MetricCard: React.FC<MetricCardProps> = ({ label, value, icon: Icon, trend, trendIcon: TrendIcon }) => {
  const trendColor = trend === 'up' 
    ? 'text-green-400' 
    : trend === 'down'
    ? 'text-red-400'
    : 'text-gray-400'

  return (
    <div className="border border-gray-700 rounded-lg p-3 bg-gray-800/50">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4 text-gray-400" />
          <span className="text-xs text-gray-400">{label}</span>
        </div>
        <TrendIcon className={`w-4 h-4 ${trendColor}`} />
      </div>
      <div className="text-lg font-semibold text-gray-200">{value}</div>
    </div>
  )
}

interface ToolListProps {
  tools: Array<{
    name: string
    latency: number
    success_rate: number
    cost: number
    call_count: number
  }>
}

const ToolList: React.FC<ToolListProps> = ({ tools }) => {
  return (
    <div className="border border-gray-700 rounded-lg">
      <div className="p-3 border-b border-gray-700">
        <h3 className="text-sm font-semibold text-gray-200">Per-Tool Statistics</h3>
      </div>
      <div className="divide-y divide-gray-700">
        {tools.length === 0 ? (
          <div className="p-4 text-center text-gray-400 text-sm">
            No tool statistics available
          </div>
        ) : (
          tools.map((tool, idx) => (
            <div key={idx} className="p-3 hover:bg-gray-800/50 transition-colors">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-200">{tool.name}</span>
                <span className="text-xs text-gray-400">{tool.call_count} calls</span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div>
                  <span className="text-gray-400">Latency:</span>
                  <span className="ml-1 text-gray-300">{tool.latency.toFixed(0)}ms</span>
                </div>
                <div>
                  <span className="text-gray-400">Success:</span>
                  <span className={`ml-1 ${
                    tool.success_rate > 0.8 ? 'text-green-400' :
                    tool.success_rate > 0.6 ? 'text-yellow-400' :
                    'text-red-400'
                  }`}>
                    {(tool.success_rate * 100).toFixed(1)}%
                  </span>
                </div>
                <div>
                  <span className="text-gray-400">Cost:</span>
                  <span className="ml-1 text-gray-300">${tool.cost.toFixed(4)}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

