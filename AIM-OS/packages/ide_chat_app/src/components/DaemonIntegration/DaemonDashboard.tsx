import React, { useState, useEffect } from 'react'
import { Server, Activity, Zap, TrendingUp, AlertCircle, CheckCircle, RefreshCw, Play, Square, RotateCw, Info, Database, FileText, Cog, BarChart3 } from 'lucide-react'
import { useAIMOS } from '../../hooks/useAIMOS'
import { daemonService } from '../../services/daemonService'
import { LoadingState } from '../LoadingState'
import { ErrorBoundary } from '../ErrorBoundary'

interface DaemonStats {
  metrics?: {
    total_requests?: number
    successful_requests?: number
    failed_requests?: number
    average_response_time_ms?: number
  }
  server_status?: {
    total_servers?: number
    running_servers?: number
    available_servers?: number
  }
  resource_usage?: {
    memory_usage_mb?: number
    cpu_usage_percent?: number
  }
  configuration?: {
    max_tools?: number
    learning_enabled?: boolean
    performance_monitoring_enabled?: boolean
  }
}

export const DaemonDashboard: React.FC = () => {
  const { daemon, isConnected, useMockData } = useAIMOS()
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [ragStats, setRagStats] = useState<any>(null)
  const [tools, setTools] = useState<string[]>([])
  const [activeTab, setActiveTab] = useState<'status' | 'details' | 'data' | 'control'>('status')

  // Fetch RAG statistics
  const fetchRAGStats = async () => {
    try {
      const stats = await daemonService.getRAGStatistics()
      if (stats) {
        setRagStats(stats)
      }
    } catch (error) {
      console.error('Failed to fetch RAG statistics:', error)
    }
  }

  // Fetch available tools
  const fetchTools = async () => {
    try {
      const toolList = await daemonService.getTools()
      if (toolList) {
        setTools(toolList)
      }
    } catch (error) {
      console.error('Failed to fetch tools:', error)
    }
  }

  useEffect(() => {
    if (!useMockData && isConnected) {
      fetchRAGStats()
      fetchTools()
      
      if (autoRefresh) {
        const interval = setInterval(() => {
          daemon.checkHealth()
          daemon.getStatus()
          fetchRAGStats()
          fetchTools()
        }, 10000) // Refresh every 10 seconds

        return () => clearInterval(interval)
      }
    }
  }, [autoRefresh, isConnected, useMockData, daemon])

  // Daemon control functions
  const handleStartDaemon = async () => {
    // TODO: Implement daemon start via IPC or HTTP endpoint
    console.log('Starting daemon...')
    alert('Daemon start functionality - to be implemented')
  }

  const handleStopDaemon = async () => {
    // TODO: Implement daemon stop via IPC or HTTP endpoint
    console.log('Stopping daemon...')
    alert('Daemon stop functionality - to be implemented')
  }

  const handleRestartDaemon = async () => {
    // TODO: Implement daemon restart via IPC or HTTP endpoint
    console.log('Restarting daemon...')
    alert('Daemon restart functionality - to be implemented')
  }

  const daemonStatus = daemon.status
  const daemonHealth = daemon.health
  const isDaemonConnected = daemon.isConnected || false

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-900 text-white">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <div className="flex items-center gap-4">
            <Server className="w-6 h-6 text-blue-400" />
            <h2 className="text-xl font-semibold">Daemon Dashboard</h2>
            <div className={`px-3 py-1 rounded-full text-sm font-semibold ${
              isDaemonConnected ? 'bg-green-600/20 text-green-400' : 'bg-red-600/20 text-red-400'
            }`}>
              {isDaemonConnected ? 'Online' : 'Offline'}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                daemon.checkHealth()
                daemon.getStatus()
                fetchRAGStats()
                fetchTools()
              }}
              disabled={daemon.loading}
              className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm flex items-center gap-2 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${daemon.loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded"
              />
              Auto-refresh
            </label>
          </div>
        </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-800 bg-gray-800/50">
        <button
          onClick={() => setActiveTab('status')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'status' 
              ? 'border-b-2 border-blue-500 text-blue-400' 
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Status
          </div>
        </button>
        <button
          onClick={() => setActiveTab('details')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'details' 
              ? 'border-b-2 border-blue-500 text-blue-400' 
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <div className="flex items-center gap-2">
            <Info className="w-4 h-4" />
            Details
          </div>
        </button>
        <button
          onClick={() => setActiveTab('data')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'data' 
              ? 'border-b-2 border-blue-500 text-blue-400' 
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Data & Systems
          </div>
        </button>
        <button
          onClick={() => setActiveTab('control')}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            activeTab === 'control' 
              ? 'border-b-2 border-blue-500 text-blue-400' 
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <div className="flex items-center gap-2">
            <Cog className="w-4 h-4" />
            Control
          </div>
        </button>
      </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          {daemon.loading ? (
            <LoadingState message="Loading daemon status..." />
          ) : (
            <>
              {activeTab === 'status' && (
                <div className="space-y-4">
                  {/* Connection Status Card */}
                  <div className={`p-6 rounded-lg border-2 ${
                    isDaemonConnected ? 'border-green-500 bg-green-500/10' : 'border-red-500 bg-red-500/10'
                  }`}>
                    <div className="flex items-center gap-3 mb-4">
                      {isDaemonConnected ? (
                        <CheckCircle className="w-6 h-6 text-green-400" />
                      ) : (
                        <AlertCircle className="w-6 h-6 text-red-400" />
                      )}
                      <div>
                        <h3 className="text-lg font-semibold">
                          {isDaemonConnected ? 'Daemon Connected' : 'Daemon Disconnected'}
                        </h3>
                        <p className="text-sm text-gray-400">
                          {daemonStatus?.status || daemonHealth?.daemon_status || 'Unknown status'}
                        </p>
                      </div>
                    </div>
                    {daemon.error && (
                      <div className="mt-2 text-sm text-red-400">{daemon.error.message}</div>
                    )}
                  </div>

                  {/* Metrics Grid */}
                  {daemonStatus?.metrics && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="p-4 bg-gray-800 rounded-lg">
                        <div className="text-sm text-gray-400 mb-1">Total Requests</div>
                        <div className="text-2xl font-bold">{daemonStatus.metrics.total_requests || 0}</div>
                      </div>
                      <div className="p-4 bg-gray-800 rounded-lg">
                        <div className="text-sm text-gray-400 mb-1">Successful</div>
                        <div className="text-2xl font-bold text-green-400">{daemonStatus.metrics.successful_requests || 0}</div>
                      </div>
                      <div className="p-4 bg-gray-800 rounded-lg">
                        <div className="text-sm text-gray-400 mb-1">Failed</div>
                        <div className="text-2xl font-bold text-red-400">{daemonStatus.metrics.failed_requests || 0}</div>
                      </div>
                      <div className="p-4 bg-gray-800 rounded-lg">
                        <div className="text-sm text-gray-400 mb-1">Avg Response</div>
                        <div className="text-2xl font-bold">{daemonStatus.metrics.average_response_time_ms?.toFixed(1) || 0}ms</div>
                      </div>
                    </div>
                  )}

                  {/* Resource Usage */}
                  {daemonStatus?.resource_usage && (
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-gray-800 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <Activity className="w-4 h-4 text-blue-400" />
                          <span className="text-sm font-semibold">Memory Usage</span>
                        </div>
                        <div className="text-2xl font-bold">{daemonStatus.resource_usage.memory_usage_mb?.toFixed(1) || 0} MB</div>
                      </div>
                      <div className="p-4 bg-gray-800 rounded-lg">
                        <div className="flex items-center gap-2 mb-2">
                          <Zap className="w-4 h-4 text-yellow-400" />
                          <span className="text-sm font-semibold">CPU Usage</span>
                        </div>
                        <div className="text-2xl font-bold">{daemonStatus.resource_usage.cpu_usage_percent?.toFixed(1) || 0}%</div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'details' && (
                <div className="space-y-4">
                  {/* Version Info */}
                  {daemonHealth && (
                    <div className="p-4 bg-gray-800 rounded-lg">
                      <h3 className="text-lg font-semibold mb-4">Daemon Information</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <div className="text-sm text-gray-400 mb-1">Version</div>
                          <div className="font-semibold">{daemonHealth.version || 'Unknown'}</div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-400 mb-1">Status</div>
                          <div className="font-semibold">{daemonHealth.daemon_status || 'Unknown'}</div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-400 mb-1">Timestamp</div>
                          <div className="font-semibold">{daemonHealth.timestamp || 'Unknown'}</div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-400 mb-1">Port</div>
                          <div className="font-semibold">5000</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Configuration */}
                  {daemonStatus?.configuration && (
                    <div className="p-4 bg-gray-800 rounded-lg">
                      <h3 className="text-lg font-semibold mb-4">Configuration</h3>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Max Tools</span>
                          <span className="font-semibold">{daemonStatus.configuration.max_tools || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Learning Enabled</span>
                          <span className={`font-semibold ${daemonStatus.configuration.learning_enabled ? 'text-green-400' : 'text-red-400'}`}>
                            {daemonStatus.configuration.learning_enabled ? 'Yes' : 'No'}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Performance Monitoring</span>
                          <span className={`font-semibold ${daemonStatus.configuration.performance_monitoring_enabled ? 'text-green-400' : 'text-red-400'}`}>
                            {daemonStatus.configuration.performance_monitoring_enabled ? 'Enabled' : 'Disabled'}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Server Status */}
                  {daemonStatus?.server_status && (
                    <div className="p-4 bg-gray-800 rounded-lg">
                      <h3 className="text-lg font-semibold mb-4">Server Status</h3>
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <div className="text-sm text-gray-400 mb-1">Total Servers</div>
                          <div className="text-2xl font-bold">{daemonStatus.server_status.total_servers || 0}</div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-400 mb-1">Running</div>
                          <div className="text-2xl font-bold text-green-400">{daemonStatus.server_status.running_servers || 0}</div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-400 mb-1">Available</div>
                          <div className="text-2xl font-bold text-blue-400">{daemonStatus.server_status.available_servers || 0}</div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'data' && (
                <div className="space-y-4">
                  {/* RAG Statistics */}
                  {ragStats && (
                    <div className="p-4 bg-gray-800 rounded-lg">
                      <h3 className="text-lg font-semibold mb-4">RAG Statistics</h3>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <div className="text-sm text-gray-400 mb-1">Total Patterns</div>
                          <div className="text-2xl font-bold">{ragStats.total_patterns || 0}</div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-400 mb-1">Learning Events</div>
                          <div className="text-2xl font-bold">{ragStats.learning_stats?.total_learning_events || 0}</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Tools */}
                  {tools && tools.length > 0 && (
                    <div className="p-4 bg-gray-800 rounded-lg">
                      <h3 className="text-lg font-semibold mb-4">Available Tools</h3>
                      <div className="text-sm text-gray-400 mb-2">{tools.length} tools available</div>
                      <div className="max-h-64 overflow-y-auto">
                        <div className="flex flex-wrap gap-2">
                          {tools.map((tool, index) => (
                            <span key={index} className="px-2 py-1 bg-gray-700 rounded text-xs">
                              {tool}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'control' && (
                <div className="space-y-4">
                  <div className="p-6 bg-gray-800 rounded-lg">
                    <h3 className="text-lg font-semibold mb-4">Daemon Control</h3>
                    <div className="flex flex-wrap gap-4">
                      <button
                        onClick={handleStartDaemon}
                        disabled={isDaemonConnected}
                        className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-sm flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Play className="w-4 h-4" />
                        Start Daemon
                      </button>
                      <button
                        onClick={handleStopDaemon}
                        disabled={!isDaemonConnected}
                        className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded text-sm flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Square className="w-4 h-4" />
                        Stop Daemon
                      </button>
                      <button
                        onClick={handleRestartDaemon}
                        disabled={!isDaemonConnected}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <RotateCw className="w-4 h-4" />
                        Restart Daemon
                      </button>
                    </div>
                    <div className="mt-4 text-sm text-gray-400">
                      <p>Note: Daemon control functionality requires IPC implementation.</p>
                      <p>Currently daemon runs independently and connects via HTTP on port 5000.</p>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </ErrorBoundary>
  )
}

