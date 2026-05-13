/**
 * Tool Quality Dashboard Panel Component
 * 
 * Phase 2.1: Left Drawer Panels
 * 
 * Monitor tool quality and performance.
 * Features:
 * - Tool performance metrics
 * - Success/failure rates
 * - Response times
 * - Confidence scores (VIF)
 * - Tool usage statistics
 * - AIM-OS integration (VIF confidence, SEG evidence)
 */

import React, { useState, useMemo, useEffect, useCallback } from 'react'
import { BarChart3, TrendingUp, TrendingDown, Clock, CheckCircle, XCircle, Activity, Zap, AlertTriangle, Shield, Target, RefreshCw, Wifi, WifiOff, Radio } from 'lucide-react'
import { useAIMOS } from '../../hooks/useAIMOS'
import { LoadingState } from '../LoadingState'
import { ErrorBoundary } from '../ErrorBoundary'
import { getAllMCPMetrics, getMCPToolMetrics, getMCPConnectionStatus, getMCPConnectionHealth, mcpToolService } from '../../services/mcpToolService'

interface ToolMetric {
  id: string
  name: string
  category: 'mcp' | 'api' | 'internal' | 'external'
  successRate: number
  avgResponseTime: number
  totalCalls: number
  failures: number
  confidence: number
  trend: 'up' | 'down' | 'stable'
  recentCalls?: number[] // Last 10 call response times
  errorBreakdown?: Array<{
    type: string
    count: number
    percentage: number
  }>
  lastUpdated?: string
}

const mockMetrics: ToolMetric[] = [
  {
    id: 'store_memory',
    name: 'Store Memory',
    category: 'mcp',
    successRate: 98.5,
    avgResponseTime: 120,
    totalCalls: 1250,
    failures: 19,
    confidence: 0.95,
    trend: 'up',
    recentCalls: [115, 125, 118, 122, 130, 115, 120, 125, 118, 122],
    errorBreakdown: [
      { type: 'Timeout', count: 12, percentage: 63.2 },
      { type: 'Validation Error', count: 5, percentage: 26.3 },
      { type: 'Network Error', count: 2, percentage: 10.5 },
    ],
    lastUpdated: '2025-11-07T10:30:00Z',
  },
  {
    id: 'retrieve_memory',
    name: 'Retrieve Memory',
    category: 'mcp',
    successRate: 97.2,
    avgResponseTime: 85,
    totalCalls: 2100,
    failures: 59,
    confidence: 0.92,
    trend: 'stable',
    recentCalls: [80, 90, 85, 88, 82, 90, 85, 88, 82, 85],
    errorBreakdown: [
      { type: 'Not Found', count: 35, percentage: 59.3 },
      { type: 'Timeout', count: 18, percentage: 30.5 },
      { type: 'Permission Error', count: 6, percentage: 10.2 },
    ],
    lastUpdated: '2025-11-07T10:29:00Z',
  },
  {
    id: 'track_confidence',
    name: 'Track Confidence',
    category: 'mcp',
    successRate: 99.1,
    avgResponseTime: 45,
    totalCalls: 890,
    failures: 8,
    confidence: 0.98,
    trend: 'up',
    recentCalls: [42, 48, 45, 43, 46, 44, 47, 45, 43, 46],
    errorBreakdown: [
      { type: 'Invalid Input', count: 5, percentage: 62.5 },
      { type: 'Timeout', count: 3, percentage: 37.5 },
    ],
    lastUpdated: '2025-11-07T10:31:00Z',
  },
  {
    id: 'add_timeline_entry',
    name: 'Add Timeline Entry',
    category: 'mcp',
    successRate: 96.8,
    avgResponseTime: 65,
    totalCalls: 1560,
    failures: 50,
    confidence: 0.90,
    trend: 'down',
    recentCalls: [70, 60, 65, 68, 62, 70, 65, 68, 62, 65],
    errorBreakdown: [
      { type: 'Serialization Error', count: 28, percentage: 56.0 },
      { type: 'Timeout', count: 15, percentage: 30.0 },
      { type: 'Validation Error', count: 7, percentage: 14.0 },
    ],
    lastUpdated: '2025-11-07T10:28:00Z',
  },
  {
    id: 'get_panel_state',
    name: 'Get Panel State',
    category: 'internal',
    successRate: 99.9,
    avgResponseTime: 5,
    totalCalls: 5000,
    failures: 5,
    confidence: 1.0,
    trend: 'stable',
    recentCalls: [4, 5, 6, 4, 5, 4, 6, 5, 4, 5],
    errorBreakdown: [
      { type: 'State Locked', count: 3, percentage: 60.0 },
      { type: 'Invalid Panel ID', count: 2, percentage: 40.0 },
    ],
    lastUpdated: '2025-11-07T10:32:00Z',
  },
]

export const ToolQualityDashboardPanel: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<'all' | ToolMetric['category']>('all')
  const [sortBy, setSortBy] = useState<'success' | 'time' | 'confidence'>('success')
  const [selectedTool, setSelectedTool] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'list' | 'charts'>('list')
  const [metrics, setMetrics] = useState<ToolMetric[]>(mockMetrics)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [refreshInterval, setRefreshInterval] = useState(3000) // 3 seconds for real-time feel
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking')
  const [connectionHealth, setConnectionHealth] = useState<{ status: string; lastCheck: number; uptime: number } | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())
  const [daemonHealth, setDaemonHealth] = useState<any>(null)
  const [daemonStatus, setDaemonStatus] = useState<any>(null)

  // AIM-OS integration
  const { vif, daemon, isConnected, useMockData, loading } = useAIMOS()

  // Load real MCP tool metrics
  const loadMetrics = useCallback(async () => {
    if (!useMockData && isConnected) {
      try {
        // Check connection status
        const connStatus = getMCPConnectionStatus()
        setConnectionStatus(connStatus)
        
        const health = getMCPConnectionHealth()
        setConnectionHealth(health)
        
        // Load daemon status if available
        if (daemon.status) {
          setDaemonStatus(daemon.status)
        }
        if (daemon.health) {
          setDaemonHealth(daemon.health)
        }
        
        // Get all MCP metrics from mcpToolService
        const allMetrics = getAllMCPMetrics()
        
        // Transform to ToolMetric format
        const loadedMetrics: ToolMetric[] = allMetrics.map((toolMetrics) => ({
          id: toolMetrics.tool,
          name: toolMetrics.tool.replace('mcp_lucid-mcp_', '').replace(/_/g, ' '),
          category: 'mcp' as const,
          successRate: toolMetrics.successRate * 100,
          avgResponseTime: toolMetrics.averageLatency || toolMetrics.avgLatency,
          totalCalls: toolMetrics.callCount,
          failures: toolMetrics.errorCount,
          confidence: toolMetrics.confidence || 0.9,
          trend: toolMetrics.trend || 'stable',
          recentCalls: toolMetrics.recentCalls || [],
          errorBreakdown: toolMetrics.errorBreakdown || [],
          lastUpdated: toolMetrics.lastCallTime || new Date().toISOString(),
        }))
        
        if (loadedMetrics.length > 0) {
          setMetrics(loadedMetrics)
          setLastUpdate(new Date())
        } else {
          // If no real metrics yet, use mock data
          setMetrics(mockMetrics)
        }
      } catch (error) {
        console.warn('Failed to load MCP metrics, using mock data', error)
        // Keep mock metrics as fallback
        setMetrics(mockMetrics)
      }
    } else {
      // Use mock data when disconnected or in mock mode
      setMetrics(mockMetrics)
      setConnectionStatus('disconnected')
    }
  }, [isConnected, useMockData, daemon])

  // Real-time refresh
  useEffect(() => {
    loadMetrics()
    
    if (autoRefresh) {
      const interval = setInterval(() => {
        loadMetrics()
      }, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [loadMetrics, autoRefresh, refreshInterval])

  // Manual refresh handler
  const handleRefresh = useCallback(() => {
    loadMetrics()
  }, [loadMetrics])

  const filteredMetrics = metrics
    .filter(m => selectedCategory === 'all' || m.category === selectedCategory)
    .sort((a, b) => {
      switch (sortBy) {
        case 'success':
          return b.successRate - a.successRate
        case 'time':
          return a.avgResponseTime - b.avgResponseTime
        case 'confidence':
          return b.confidence - a.confidence
        default:
          return 0
      }
    })

  const getSuccessColor = (rate: number) => {
    if (rate >= 98) return 'text-green-400'
    if (rate >= 95) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.95) return 'text-green-400'
    if (confidence >= 0.90) return 'text-yellow-400'
    return 'text-red-400'
  }

  const selectedMetric = useMemo(() => {
    return filteredMetrics.find(m => m.id === selectedTool)
  }, [selectedTool, filteredMetrics])

  const renderBarChart = (value: number, max: number, color: string) => {
    const percentage = (value / max) * 100
    return (
      <div className="w-full bg-gray-700 rounded-full h-2">
        <div
          className={`h-2 rounded-full ${color}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    )
  }

  const renderResponseTimeChart = (recentCalls?: number[]) => {
    if (!recentCalls || recentCalls.length === 0) return null
    
    const maxTime = Math.max(...recentCalls, 1)
    const minHeight = 4
    const maxHeight = 40

    return (
      <div className="flex items-end gap-1 h-12">
        {recentCalls.map((time, idx) => {
          const height = minHeight + ((time / maxTime) * (maxHeight - minHeight))
          const color = time < 50 ? 'bg-green-500' : time < 100 ? 'bg-yellow-500' : 'bg-red-500'
          return (
            <div
              key={idx}
              className={`${color} rounded-t transition-all`}
              style={{ width: '8px', height: `${height}px` }}
              title={`${time}ms`}
            />
          )
        })}
      </div>
    )
  }

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-800" role="complementary" aria-label="Tool Quality Dashboard">
        {loading.vif ? (
          <LoadingState message="Loading tool metrics..." />
        ) : (
          <>
      {/* Header */}
      <div className="h-12 bg-gray-900 border-b border-gray-700 flex items-center justify-between px-3 shrink-0">
        <div className="flex items-center gap-3">
          <BarChart3 className="w-4 h-4 text-gray-400" />
          <span className="text-sm font-semibold text-gray-300">MCP Tool Usage</span>
          {/* Connection Status Indicator */}
          <div className="flex items-center gap-1.5">
            {connectionStatus === 'connected' ? (
              <div className="flex items-center gap-1 text-green-400">
                <Wifi className="w-3 h-3" />
                <span className="text-xs">Connected</span>
              </div>
            ) : connectionStatus === 'checking' ? (
              <div className="flex items-center gap-1 text-yellow-400">
                <Radio className="w-3 h-3 animate-pulse" />
                <span className="text-xs">Checking...</span>
              </div>
            ) : (
              <div className="flex items-center gap-1 text-red-400">
                <WifiOff className="w-3 h-3" />
                <span className="text-xs">Disconnected</span>
              </div>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {/* Auto-refresh toggle */}
          <label className="flex items-center gap-1.5 text-xs text-gray-400 cursor-pointer">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
            <span>Auto-refresh</span>
          </label>
          <button
            onClick={() => setViewMode(viewMode === 'list' ? 'charts' : 'list')}
            className="p-1 text-gray-400 hover:text-gray-300 transition-colors"
            title={viewMode === 'list' ? 'Switch to Charts View' : 'Switch to List View'}
          >
            {viewMode === 'list' ? <BarChart3 className="w-4 h-4" /> : <Activity className="w-4 h-4" />}
          </button>
          <button
            onClick={handleRefresh}
            className="p-1 text-gray-400 hover:text-gray-300 transition-colors"
            title="Refresh Metrics Now"
          >
            <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="px-2 py-2 border-b border-gray-700 shrink-0 space-y-2">
        {/* Daemon Status Badge */}
        {daemonHealth && daemon.isConnected && (
          <div className="flex items-center gap-2 px-2 py-1 bg-blue-600/20 border border-blue-600/30 rounded text-xs">
            <Activity className="w-3 h-3 text-blue-400" />
            <span className="text-gray-300">Daemon:</span>
            <span className="text-green-400 font-semibold">{daemonHealth.daemon_status || 'Running'}</span>
            {daemonStatus?.metrics && (
              <>
                <span className="text-gray-500">|</span>
                <span className="text-gray-300">Requests: {daemonStatus.metrics.total_requests || 0}</span>
                <span className="text-gray-500">|</span>
                <span className="text-green-400">Success: {daemonStatus.metrics.successful_requests || 0}</span>
              </>
            )}
          </div>
        )}
        <div className="flex gap-1 overflow-x-auto">
          {(['all', 'mcp', 'api', 'internal', 'external'] as const).map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 text-xs rounded whitespace-nowrap transition-colors ${
                selectedCategory === cat
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>
        <div className="flex gap-1">
          <span className="text-xs text-gray-400">Sort by:</span>
          {(['success', 'time', 'confidence'] as const).map((sort) => (
            <button
              key={sort}
              onClick={() => setSortBy(sort)}
              className={`px-2 py-0.5 text-xs rounded transition-colors ${
                sortBy === sort
                  ? 'bg-gray-700 text-gray-300'
                  : 'text-gray-500 hover:text-gray-400'
              }`}
            >
              {sort.charAt(0).toUpperCase() + sort.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Metrics List */}
      <div className="flex-1 overflow-y-auto p-2">
        {viewMode === 'list' ? (
          <div className="space-y-2">
            {filteredMetrics.map((metric) => (
              <div
                key={metric.id}
                className={`p-3 bg-gray-700/50 rounded border transition-colors cursor-pointer ${
                  selectedTool === metric.id
                    ? 'border-blue-500 bg-blue-600/20'
                    : 'border-gray-700 hover:bg-gray-700'
                }`}
                onClick={() => setSelectedTool(selectedTool === metric.id ? null : metric.id)}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Zap className="w-4 h-4 text-blue-400" />
                    <span className="text-sm font-medium text-gray-300">{metric.name}</span>
                    <span className="text-xs text-gray-500">({metric.category})</span>
                  </div>
                  {metric.trend === 'up' && <TrendingUp className="w-4 h-4 text-green-400" />}
                  {metric.trend === 'down' && <TrendingDown className="w-4 h-4 text-red-400" />}
                  {metric.trend === 'stable' && <Activity className="w-4 h-4 text-gray-400" />}
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs mb-2">
                  <div>
                    <div className="text-gray-400 mb-1">Success Rate</div>
                    <div className={`font-semibold ${getSuccessColor(metric.successRate)}`}>
                      {metric.successRate.toFixed(1)}%
                    </div>
                    {renderBarChart(metric.successRate, 100, 'bg-green-500')}
                    <div className="text-gray-500 mt-1">
                      {metric.totalCalls - metric.failures}/{metric.totalCalls} calls
                    </div>
                  </div>

                  <div>
                    <div className="text-gray-400 mb-1">Avg Response</div>
                    <div className="text-gray-300 font-semibold">{metric.avgResponseTime}ms</div>
                    {renderBarChart(metric.avgResponseTime, 200, 'bg-blue-500')}
                    <div className="text-gray-500 mt-1 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {metric.avgResponseTime < 100 ? 'Fast' : metric.avgResponseTime < 500 ? 'Normal' : 'Slow'}
                    </div>
                  </div>

                  <div>
                    <div className="text-gray-400 mb-1">Confidence (VIF)</div>
                    <div className={`font-semibold ${getConfidenceColor(metric.confidence)}`}>
                      {(metric.confidence * 100).toFixed(0)}%
                    </div>
                    {renderBarChart(metric.confidence * 100, 100, 'bg-purple-500')}
                    <div className="text-gray-500 mt-1 flex items-center gap-1">
                      <Shield className="w-3 h-3" />
                      VIF Score
                    </div>
                  </div>

                  <div>
                    <div className="text-gray-400 mb-1">Failures</div>
                    <div className={`font-semibold ${metric.failures === 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {metric.failures}
                    </div>
                    {renderBarChart(metric.failures, Math.max(metric.totalCalls * 0.1, 1), 'bg-red-500')}
                    <div className="text-gray-500 mt-1">
                      {metric.failures > 0 ? (
                        <span className="text-red-400">{(metric.failures / metric.totalCalls * 100).toFixed(2)}%</span>
                      ) : (
                        <span className="text-green-400">Perfect</span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Response Time Chart */}
                {metric.recentCalls && (
                  <div className="mt-2 pt-2 border-t border-gray-600">
                    <div className="text-xs text-gray-400 mb-1">Recent Response Times</div>
                    {renderResponseTimeChart(metric.recentCalls)}
                  </div>
                )}

                {/* Expanded Details */}
                {selectedTool === metric.id && (
                  <div className="mt-3 pt-3 border-t border-gray-600 space-y-2">
                    {metric.errorBreakdown && metric.errorBreakdown.length > 0 && (
                      <div>
                        <div className="text-xs text-gray-400 mb-2 flex items-center gap-1">
                          <AlertTriangle className="w-3 h-3" />
                          Error Breakdown
                        </div>
                        <div className="space-y-1">
                          {metric.errorBreakdown.map((error, idx) => (
                            <div key={idx} className="flex items-center justify-between text-xs">
                              <span className="text-gray-300">{error.type}</span>
                              <div className="flex items-center gap-2">
                                <div className="w-24 bg-gray-700 rounded-full h-1.5">
                                  <div
                                    className="bg-red-500 h-1.5 rounded-full"
                                    style={{ width: `${error.percentage}%` }}
                                  />
                                </div>
                                <span className="text-gray-400 w-12 text-right">
                                  {error.count} ({error.percentage.toFixed(1)}%)
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {metric.lastUpdated && (
                      <div className="text-xs text-gray-500 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        Last updated: {new Date(metric.lastUpdated).toLocaleTimeString()}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {/* Success Rate Chart */}
            <div className="bg-gray-700/50 rounded p-3 border border-gray-700">
              <h3 className="text-sm font-semibold text-gray-300 mb-3">Success Rates</h3>
              <div className="space-y-2">
                {filteredMetrics.map((metric) => (
                  <div key={metric.id} className="flex items-center gap-2">
                    <span className="text-xs text-gray-400 w-32 truncate">{metric.name}</span>
                    <div className="flex-1">
                      {renderBarChart(metric.successRate, 100, 'bg-green-500')}
                    </div>
                    <span className={`text-xs font-semibold w-12 text-right ${getSuccessColor(metric.successRate)}`}>
                      {metric.successRate.toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Response Time Chart */}
            <div className="bg-gray-700/50 rounded p-3 border border-gray-700">
              <h3 className="text-sm font-semibold text-gray-300 mb-3">Average Response Times</h3>
              <div className="space-y-2">
                {filteredMetrics.map((metric) => (
                  <div key={metric.id} className="flex items-center gap-2">
                    <span className="text-xs text-gray-400 w-32 truncate">{metric.name}</span>
                    <div className="flex-1">
                      {renderBarChart(metric.avgResponseTime, 200, 'bg-blue-500')}
                    </div>
                    <span className="text-xs text-gray-300 w-12 text-right">{metric.avgResponseTime}ms</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Confidence Chart */}
            <div className="bg-gray-700/50 rounded p-3 border border-gray-700">
              <h3 className="text-sm font-semibold text-gray-300 mb-3">VIF Confidence Scores</h3>
              <div className="space-y-2">
                {filteredMetrics.map((metric) => (
                  <div key={metric.id} className="flex items-center gap-2">
                    <span className="text-xs text-gray-400 w-32 truncate">{metric.name}</span>
                    <div className="flex-1">
                      {renderBarChart(metric.confidence * 100, 100, 'bg-purple-500')}
                    </div>
                    <span className={`text-xs font-semibold w-12 text-right ${getConfidenceColor(metric.confidence)}`}>
                      {(metric.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Summary */}
      <div className="h-20 bg-gray-900 border-t border-gray-700 px-3 py-2 shrink-0">
        <div className="flex items-center justify-between text-xs mb-2">
          <div className="text-gray-400">
            Total Tools: <span className="text-gray-300 font-semibold">{filteredMetrics.length}</span>
          </div>
          <div className="text-gray-400">
            Avg Success: <span className="text-green-400 font-semibold">
              {filteredMetrics.length > 0 ? (filteredMetrics.reduce((sum, m) => sum + m.successRate, 0) / filteredMetrics.length).toFixed(1) : '0.0'}%
            </span>
          </div>
          <div className="text-gray-400">
            Avg Confidence: <span className="text-green-400 font-semibold">
              {filteredMetrics.length > 0 ? (filteredMetrics.reduce((sum, m) => sum + m.confidence, 0) / filteredMetrics.length * 100).toFixed(0) : '0'}%
            </span>
          </div>
        </div>
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center gap-2">
            <Clock className="w-3 h-3" />
            <span>Last update: {lastUpdate.toLocaleTimeString()}</span>
          </div>
          {connectionHealth && (
            <div className="flex items-center gap-2">
              <Activity className="w-3 h-3" />
              <span>Uptime: {Math.floor(connectionHealth.uptime / 1000)}s</span>
            </div>
          )}
          {autoRefresh && (
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span>Live</span>
            </div>
          )}
        </div>
      </div>
          </>
        )}
      </div>
    </ErrorBoundary>
  )
}

