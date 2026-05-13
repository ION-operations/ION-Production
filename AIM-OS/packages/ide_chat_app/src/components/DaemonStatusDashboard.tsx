/**
 * Daemon Status Dashboard Component
 * Displays real-time daemon status, metrics, and health
 */

import React, { useEffect, useState } from 'react'
import { Activity, Server, Zap, TrendingUp, AlertCircle, CheckCircle, RefreshCw } from 'lucide-react'
import { useDaemon } from '../hooks/useDaemon'

export const DaemonStatusDashboard: React.FC = () => {
  const {
    isConnected,
    status,
    tools,
    ragStats,
    isLoading,
    error,
    checkConnection,
    loadTools,
    loadRAGStats
  } = useDaemon()

  const [autoRefresh, setAutoRefresh] = useState(true)

  useEffect(() => {
    if (autoRefresh && isConnected) {
      const interval = setInterval(() => {
        checkConnection()
        loadTools()
        loadRAGStats()
      }, 5000) // Refresh every 5 seconds

      return () => clearInterval(interval)
    }
  }, [autoRefresh, isConnected, checkConnection, loadTools, loadRAGStats])

  return (
    <div className="daemon-status-dashboard p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Server className="w-5 h-5" />
          <h2 className="text-lg font-semibold">Daemon Status</h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => checkConnection()}
            className="p-2 hover:bg-gray-700 rounded"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh
          </label>
        </div>
      </div>

      {/* Connection Status */}
      <div className={`p-4 rounded-lg border-2 ${isConnected ? 'border-green-500 bg-green-500/10' : 'border-red-500 bg-red-500/10'}`}>
        <div className="flex items-center gap-2">
          {isConnected ? (
            <CheckCircle className="w-5 h-5 text-green-500" />
          ) : (
            <AlertCircle className="w-5 h-5 text-red-500" />
          )}
          <span className="font-semibold">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
          {status && (
            <span className="text-sm text-gray-400">
              ({status.daemon_status || status.status})
            </span>
          )}
        </div>
        {error && (
          <div className="mt-2 text-sm text-red-400">{error}</div>
        )}
      </div>

      {/* Metrics Grid */}
      {status && isConnected && (
        <div className="grid grid-cols-2 gap-4">
          {/* Performance Metrics */}
          {status.metrics && (
            <div className="p-4 bg-gray-800 rounded-lg">
              <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
                <Zap className="w-4 h-4" />
                Performance
              </h3>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Requests:</span>
                  <span>{status.metrics.total_requests || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Success Rate:</span>
                  <span>
                    {status.metrics.total_requests
                      ? ((status.metrics.successful_requests || 0) / status.metrics.total_requests * 100).toFixed(1)
                      : 0}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Avg Response:</span>
                  <span>{status.metrics.average_response_time_ms?.toFixed(1) || 0}ms</span>
                </div>
              </div>
            </div>
          )}

          {/* Server Status */}
          {status.server_status && (
            <div className="p-4 bg-gray-800 rounded-lg">
              <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
                <Server className="w-4 h-4" />
                Servers
              </h3>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Total:</span>
                  <span>{status.server_status.total_servers || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Running:</span>
                  <span className="text-green-400">{status.server_status.running_servers || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Available:</span>
                  <span className="text-green-400">{status.server_status.available_servers || 0}</span>
                </div>
              </div>
            </div>
          )}

          {/* Resource Usage */}
          {status.resource_usage && (
            <div className="p-4 bg-gray-800 rounded-lg">
              <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
                <Activity className="w-4 h-4" />
                Resources
              </h3>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Memory:</span>
                  <span>{status.resource_usage.memory_usage_mb?.toFixed(1) || 0} MB</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">CPU:</span>
                  <span>{status.resource_usage.cpu_usage_percent?.toFixed(1) || 0}%</span>
                </div>
              </div>
            </div>
          )}

          {/* Configuration */}
          {status.configuration && (
            <div className="p-4 bg-gray-800 rounded-lg">
              <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Config
              </h3>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Max Tools:</span>
                  <span>{status.configuration.max_tools || 40}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Learning:</span>
                  <span>{status.configuration.learning_enabled ? 'Enabled' : 'Disabled'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Monitoring:</span>
                  <span>{status.configuration.performance_monitoring_enabled ? 'On' : 'Off'}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tools List */}
      {tools && tools.total_tools > 0 && (
        <div className="p-4 bg-gray-800 rounded-lg">
          <h3 className="text-sm font-semibold mb-2">Available Tools</h3>
          <div className="text-sm text-gray-400">
            {tools.total_tools} tools registered
          </div>
        </div>
      )}

      {/* RAG Statistics */}
      {ragStats && ragStats.total_patterns > 0 && (
        <div className="p-4 bg-gray-800 rounded-lg">
          <h3 className="text-sm font-semibold mb-2">RAG Learning</h3>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Total Patterns:</span>
              <span>{ragStats.total_patterns}</span>
            </div>
            {ragStats.patterns_by_type && (
              <div className="flex justify-between">
                <span className="text-gray-400">Success Rate:</span>
                <span>
                  {ragStats.patterns_by_type.SUCCESS
                    ? ((ragStats.patterns_by_type.SUCCESS / ragStats.total_patterns) * 100).toFixed(1)
                    : 0}%
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default DaemonStatusDashboard

