// Log Analysis Dashboard - Log-Sentinels Telemetry
// Displays Log-Sentinels statistics: Scout calls, Forensics calls, escalations, tool suggestions, and timeline

import React from 'react'
import { useLogSentinels } from '../hooks/useLogSentinels'
import { BasePanel } from '../components/BasePanel'
import { LoadingSpinner, ErrorDisplay } from '../components/shared/shared'
import { 
  BarChart3, 
  Brain, 
  AlertTriangle, 
  Zap,
  TrendingUp
} from 'lucide-react'

export const LogAnalysisDashboard: React.FC = () => {
  const { telemetry, loading, error } = useLogSentinels()

  if (loading) {
    return (
      <BasePanel id="log-analysis-dashboard" title="Log Analysis" icon={BarChart3}>
        <LoadingSpinner />
      </BasePanel>
    )
  }

  if (error) {
    return (
      <BasePanel id="log-analysis-dashboard" title="Log Analysis" icon={BarChart3}>
        <ErrorDisplay error={error} />
      </BasePanel>
    )
  }

  if (!telemetry) {
    return (
      <BasePanel id="log-analysis-dashboard" title="Log Analysis" icon={BarChart3}>
        <div className="text-gray-400 text-sm text-center py-8">
          No telemetry data available
        </div>
      </BasePanel>
    )
  }

  return (
    <BasePanel id="log-analysis-dashboard" title="Log Analysis" icon={BarChart3}>
      <div className="flex flex-col gap-4 p-4">
        <StatsGrid telemetry={telemetry} />
        <TimelineChart data={telemetry.timeline} />
      </div>
    </BasePanel>
  )
}

interface StatsGridProps {
  telemetry: any
}

const StatsGrid: React.FC<StatsGridProps> = ({ telemetry }) => {
  return (
    <div className="grid grid-cols-4 gap-4">
      <StatCard
        label="Scout Calls"
        value={telemetry.scout_calls}
        icon={Brain}
        color="text-blue-400"
      />
      <StatCard
        label="Forensics Calls"
        value={telemetry.forensics_calls}
        icon={AlertTriangle}
        color="text-yellow-400"
      />
      <StatCard
        label="Escalations"
        value={telemetry.escalations}
        icon={TrendingUp}
        color="text-orange-400"
      />
      <StatCard
        label="Tool Suggestions"
        value={telemetry.tool_suggestions}
        icon={Zap}
        color="text-green-400"
      />
    </div>
  )
}

interface StatCardProps {
  label: string
  value: number
  icon: React.ComponentType<{ className?: string }>
  color: string
}

const StatCard: React.FC<StatCardProps> = ({ label, value, icon: Icon, color }) => {
  return (
    <div className="border border-gray-700 rounded-lg p-3 bg-gray-800/50">
      <div className="flex items-center gap-2 mb-2">
        <Icon className={`w-4 h-4 ${color}`} />
        <span className="text-xs text-gray-400">{label}</span>
      </div>
      <div className={`text-2xl font-semibold ${color}`}>{value}</div>
    </div>
  )
}

interface TimelineChartProps {
  data: Array<{
    timestamp: string
    scout_calls: number
    forensics_calls: number
    escalations: number
  }>
}

const TimelineChart: React.FC<TimelineChartProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="border border-gray-700 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-gray-200 mb-4">Timeline</h3>
        <div className="text-center text-gray-400 text-sm py-8">
          No timeline data available
        </div>
      </div>
    )
  }

  const maxValue = Math.max(
    ...data.flatMap(d => [d.scout_calls, d.forensics_calls, d.escalations])
  )

  return (
    <div className="border border-gray-700 rounded-lg p-4">
      <h3 className="text-sm font-semibold text-gray-200 mb-4">Timeline</h3>
      <div className="space-y-2">
        {data.slice(0, 20).map((entry, idx) => (
          <div key={idx} className="flex items-center gap-2">
            <div className="text-xs text-gray-400 w-24">
              {new Date(entry.timestamp).toLocaleTimeString()}
            </div>
            <div className="flex-1 flex items-center gap-1">
              <div
                className="h-4 bg-blue-500 rounded"
                style={{ width: `${(entry.scout_calls / maxValue) * 100}%` }}
                title={`Scout: ${entry.scout_calls}`}
              />
              <div
                className="h-4 bg-yellow-500 rounded"
                style={{ width: `${(entry.forensics_calls / maxValue) * 100}%` }}
                title={`Forensics: ${entry.forensics_calls}`}
              />
              <div
                className="h-4 bg-red-500 rounded"
                style={{ width: `${(entry.escalations / maxValue) * 100}%` }}
                title={`Escalations: ${entry.escalations}`}
              />
            </div>
          </div>
        ))}
      </div>
      <div className="flex items-center gap-4 mt-4 text-xs text-gray-400">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-blue-500 rounded" />
          <span>Scout</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-yellow-500 rounded" />
          <span>Forensics</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 bg-red-500 rounded" />
          <span>Escalations</span>
        </div>
      </div>
    </div>
  )
}

