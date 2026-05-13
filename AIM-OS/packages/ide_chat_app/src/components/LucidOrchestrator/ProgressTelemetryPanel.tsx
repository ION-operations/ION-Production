import React from 'react'
import { RefreshCw, TrendingUp, AlertTriangle } from 'lucide-react'
import { ProgressTelemetrySnapshot } from '@/services/progressTelemetryService'

interface ProgressTelemetryPanelProps {
  snapshot: ProgressTelemetrySnapshot | null
  loading?: boolean
  error?: string | null
  onRefresh?: () => void
}

export const ProgressTelemetryPanel: React.FC<ProgressTelemetryPanelProps> = ({
  snapshot,
  loading = false,
  error = null,
  onRefresh,
}) => {
  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-indigo-400" />
            Orchestrator Progress
          </h3>
          <p className="text-sm text-gray-400">
            {snapshot?.last_updated ? `Last updated: ${snapshot.last_updated}` : 'Prototype snapshot'}
          </p>
        </div>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-600/20 text-indigo-200 hover:bg-indigo-600/30 transition"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-sm text-amber-300 bg-amber-500/10 border border-amber-500/30 rounded-lg px-3 py-2">
          <AlertTriangle className="w-4 h-4" />
          {error}
        </div>
      )}

      {!snapshot && !error && (
        <div className="text-gray-400 text-sm">No telemetry snapshot available.</div>
      )}

      {snapshot && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(snapshot.phases).map(([phaseId, metrics]) => (
            <div key={phaseId} className="bg-white/5 rounded-2xl border border-white/10 p-4 space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-base font-semibold text-white">
                  {formatPhaseName(phaseId)}
                </h4>
                <span className="text-indigo-300 text-sm">{metrics.percent_complete.toFixed(1)}%</span>
              </div>
              <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                <div
                  className="h-full bg-indigo-500 transition-all duration-500"
                  style={{ width: `${Math.min(metrics.percent_complete, 100)}%` }}
                />
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm text-gray-300">
                <div>
                  <p className="text-gray-400">Remaining Tasks</p>
                  <p className="font-semibold text-white">{metrics.remaining_tasks}</p>
                </div>
                <div>
                  <p className="text-gray-400">ETA (days)</p>
                  <p className="font-semibold text-white">
                    {metrics.eta_days < 0 ? 'TBD' : metrics.eta_days.toFixed(1)}
                  </p>
                </div>
                {metrics.velocity_tasks_per_day !== undefined && (
                  <div>
                    <p className="text-gray-400">Velocity</p>
                    <p className="font-semibold text-white">
                      {metrics.velocity_tasks_per_day.toFixed(2)} tasks/day
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

const formatPhaseName = (phaseId: string) =>
  phaseId
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase())
