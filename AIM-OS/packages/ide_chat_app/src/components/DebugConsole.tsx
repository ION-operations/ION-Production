// Debug Console Component
// Built-in debug infrastructure for IDE
// V2 Enhancement - Week 1 Foundation, Week 3 Integration

import React, { useState, useEffect, useRef } from 'react'
import { AlertTriangle, X, Download, Trash2, Filter, Search } from 'lucide-react'
import { usePerformanceMonitoring } from '../services/performanceMonitor'
import { useRealTimeUpdates } from '../services/realTimeUpdateService'
import { getErrorTrackingService } from '../services/errorTrackingService'

export interface DebugError {
  id: string
  message: string
  stack?: string
  timestamp: Date
  severity: 'error' | 'warning' | 'info'
  source: string
  context?: any
}

export interface PerformanceMetric {
  id: string
  type: 'render' | 'api' | 'mcp' | 'memory'
  value: number
  timestamp: Date
  label?: string
}

export interface DebugLog {
  id: string
  level: 'log' | 'info' | 'warn' | 'error'
  message: string
  timestamp: Date
  source?: string
  data?: any
}

export interface NetworkRequest {
  id: string
  method: string
  url: string
  status?: number
  duration: number
  timestamp: Date
  requestData?: any
  responseData?: any
}

interface DebugConsoleProps {
  className?: string
}

type TabType = 'errors' | 'performance' | 'logs' | 'network' | 'memory'

export const DebugConsole: React.FC<DebugConsoleProps> = ({ className = '' }) => {
  const [activeTab, setActiveTab] = useState<TabType>('errors')
  const [errors, setErrors] = useState<DebugError[]>([])
  const [performance, setPerformance] = useState<PerformanceMetric[]>([])
  const [logs, setLogs] = useState<DebugLog[]>([])
  const [network, setNetwork] = useState<NetworkRequest[]>([])
  const [filter, setFilter] = useState<string>('')
  const [severityFilter, setSeverityFilter] = useState<'all' | 'error' | 'warning' | 'info'>('all')
  const logsEndRef = useRef<HTMLDivElement>(null)

  // Performance monitoring integration
  const { snapshot, startMonitoring, stopMonitoring } = usePerformanceMonitoring()
  const performanceUpdate = useRealTimeUpdates('performance')
  const errorTrackingService = getErrorTrackingService()

  // Error tracking integration
  useEffect(() => {
    const unsubscribe = errorTrackingService.subscribe((error) => {
      setErrors(prev => [...prev.slice(-99), error])
    })

    // Load existing errors
    const existingErrors = errorTrackingService.getErrors()
    if (existingErrors.length > 0) {
      setErrors(existingErrors.slice(-100))
    }

    return () => {
      unsubscribe()
    }
  }, [errorTrackingService])

  // Real-time performance updates
  useEffect(() => {
    if (performanceUpdate.update && performanceUpdate.update.data) {
      const perfData = performanceUpdate.update.data
      if (perfData.memoryUsage !== undefined) {
        const metric: PerformanceMetric = {
          id: `perf-realtime-${Date.now()}`,
          type: 'memory',
          value: perfData.memoryUsage,
          timestamp: new Date(perfData.timestamp || Date.now()),
          label: 'Memory Usage (Real-time)'
        }
        setPerformance(prev => [...prev.slice(-99), metric])
      }
    }
  }, [performanceUpdate.update])

  // Performance snapshot integration
  useEffect(() => {
    if (snapshot && snapshot.summary) {
      // Add render time metrics
      if (snapshot.summary.renderTime > 0) {
        const renderMetric: PerformanceMetric = {
          id: `perf-render-${Date.now()}`,
          type: 'render',
          value: snapshot.summary.renderTime,
          timestamp: new Date(),
          label: 'Render Time'
        }
        setPerformance(prev => [...prev.slice(-99), renderMetric])
      }

      // Add memory metrics
      if (snapshot.summary.memoryUsage > 0) {
        const memoryMetric: PerformanceMetric = {
          id: `perf-memory-${Date.now()}`,
          type: 'memory',
          value: snapshot.summary.memoryUsage,
          timestamp: new Date(),
          label: 'Memory Usage'
        }
        setPerformance(prev => [...prev.slice(-99), memoryMetric])
      }

      // Add network request metrics
      if (snapshot.summary.networkRequests > 0) {
        const networkMetric: PerformanceMetric = {
          id: `perf-network-${Date.now()}`,
          type: 'api',
          value: snapshot.summary.networkRequests,
          timestamp: new Date(),
          label: 'Network Requests'
        }
        setPerformance(prev => [...prev.slice(-99), networkMetric])
      }
    }
  }, [snapshot])

  // Start/stop monitoring based on active tab
  useEffect(() => {
    if (activeTab === 'performance' || activeTab === 'memory') {
      startMonitoring()
    } else {
      stopMonitoring()
    }
    return () => {
      stopMonitoring()
    }
  }, [activeTab, startMonitoring, stopMonitoring])

  // Error tracking
  useEffect(() => {
    const originalError = console.error
    const originalWarn = console.warn
    const originalInfo = console.info
    const originalLog = console.log

    console.error = (...args: any[]) => {
      originalError(...args)
      const error: DebugError = {
        id: `error-${Date.now()}-${Math.random()}`,
        message: args.map(a => typeof a === 'string' ? a : JSON.stringify(a)).join(' '),
        stack: new Error().stack,
        timestamp: new Date(),
        severity: 'error',
        source: 'console',
        context: args
      }
      setErrors(prev => [...prev.slice(-99), error]) // Keep last 100
    }

    console.warn = (...args: any[]) => {
      originalWarn(...args)
      const error: DebugError = {
        id: `warn-${Date.now()}-${Math.random()}`,
        message: args.map(a => typeof a === 'string' ? a : JSON.stringify(a)).join(' '),
        timestamp: new Date(),
        severity: 'warning',
        source: 'console',
        context: args
      }
      setErrors(prev => [...prev.slice(-99), error])
    }

    console.info = (...args: any[]) => {
      originalInfo(...args)
      const log: DebugLog = {
        id: `info-${Date.now()}-${Math.random()}`,
        level: 'info',
        message: args.map(a => typeof a === 'string' ? a : JSON.stringify(a)).join(' '),
        timestamp: new Date(),
        source: 'console',
        data: args
      }
      setLogs(prev => [...prev.slice(-99), log])
    }

    console.log = (...args: any[]) => {
      originalLog(...args)
      const log: DebugLog = {
        id: `log-${Date.now()}-${Math.random()}`,
        level: 'log',
        message: args.map(a => typeof a === 'string' ? a : JSON.stringify(a)).join(' '),
        timestamp: new Date(),
        source: 'console',
        data: args
      }
      setLogs(prev => [...prev.slice(-99), log])
    }

    // Performance monitoring
    const performanceInterval = setInterval(() => {
      if (performance.memory) {
        const memoryUsage = (performance.memory as any).usedJSHeapSize / 1024 / 1024 // MB
        const metric: PerformanceMetric = {
          id: `perf-${Date.now()}`,
          type: 'memory',
          value: memoryUsage,
          timestamp: new Date(),
          label: 'Memory Usage'
        }
        setPerformance(prev => [...prev.slice(-99), metric])
      }
    }, 5000)

    return () => {
      console.error = originalError
      console.warn = originalWarn
      console.info = originalInfo
      console.log = originalLog
      clearInterval(performanceInterval)
    }
  }, [])

  // Auto-scroll logs
  useEffect(() => {
    if (activeTab === 'logs' && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs, activeTab])

  const filteredErrors = errors.filter(error => {
    const matchesFilter = !filter || error.message.toLowerCase().includes(filter.toLowerCase())
    const matchesSeverity = severityFilter === 'all' || error.severity === severityFilter
    return matchesFilter && matchesSeverity
  })

  const filteredLogs = logs.filter(log => {
    return !filter || log.message.toLowerCase().includes(filter.toLowerCase())
  })

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'error': return 'text-red-400 bg-red-900/20 border-red-500'
      case 'warning': return 'text-yellow-400 bg-yellow-900/20 border-yellow-500'
      case 'info': return 'text-blue-400 bg-blue-900/20 border-blue-500'
      default: return 'text-gray-400 bg-gray-800 border-gray-600'
    }
  }

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'error': return 'text-red-400'
      case 'warn': return 'text-yellow-400'
      case 'info': return 'text-blue-400'
      default: return 'text-gray-400'
    }
  }

  const exportData = () => {
    const data = {
      errors,
      performance,
      logs,
      network,
      exportedAt: new Date().toISOString()
    }
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `debug-console-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const clearData = () => {
    if (activeTab === 'errors') setErrors([])
    if (activeTab === 'performance') setPerformance([])
    if (activeTab === 'logs') setLogs([])
    if (activeTab === 'network') setNetwork([])
  }

  return (
    <div className={`flex flex-col h-full bg-gray-900 text-gray-100 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-yellow-400" />
          <h2 className="text-lg font-semibold">Debug Console</h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={exportData}
            className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 rounded flex items-center gap-2"
            title="Export logs"
          >
            <Download className="w-4 h-4" />
            Export
          </button>
          <button
            onClick={clearData}
            className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 rounded flex items-center gap-2"
            title="Clear logs"
          >
            <Trash2 className="w-4 h-4" />
            Clear
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-700">
        {(['errors', 'performance', 'logs', 'network', 'memory'] as TabType[]).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium capitalize transition-colors ${
              activeTab === tab
                ? 'bg-gray-800 text-white border-b-2 border-blue-500'
                : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
            }`}
          >
            {tab} {tab === 'errors' && errors.length > 0 && `(${errors.length})`}
          </button>
        ))}
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2 px-4 py-2 border-b border-gray-700 bg-gray-800">
        <div className="flex items-center gap-2 flex-1">
          <Search className="w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="flex-1 px-2 py-1 bg-gray-700 border border-gray-600 rounded text-sm text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
          />
        </div>
        {activeTab === 'errors' && (
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value as any)}
            className="px-2 py-1 bg-gray-700 border border-gray-600 rounded text-sm text-white focus:outline-none focus:border-blue-500"
          >
            <option value="all">All</option>
            <option value="error">Errors</option>
            <option value="warning">Warnings</option>
            <option value="info">Info</option>
          </select>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'errors' && (
          <div className="space-y-2">
            {filteredErrors.length === 0 ? (
              <div className="text-center text-gray-400 py-8">No errors</div>
            ) : (
              filteredErrors.map(error => (
                <div
                  key={error.id}
                  className={`p-3 rounded border ${getSeverityColor(error.severity)}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="font-medium mb-1">{error.message}</div>
                      <div className="text-xs text-gray-400">
                        {error.timestamp.toLocaleTimeString()} • {error.source}
                      </div>
                    </div>
                  </div>
                  {error.stack && (
                    <details className="mt-2">
                      <summary className="text-xs text-gray-400 cursor-pointer hover:text-gray-300">
                        Stack trace
                      </summary>
                      <pre className="mt-2 text-xs text-gray-500 overflow-x-auto">
                        {error.stack}
                      </pre>
                    </details>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'performance' && (
          <div className="space-y-4">
            {/* Current Snapshot Summary */}
            {snapshot && snapshot.summary && (
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="p-3 bg-gray-800 rounded border border-gray-700">
                  <div className="text-xs text-gray-400 mb-1">Render Time</div>
                  <div className={`text-lg font-bold ${
                    snapshot.summary.renderTime > 33.33 ? 'text-red-400' :
                    snapshot.summary.renderTime > 16.67 ? 'text-yellow-400' :
                    'text-green-400'
                  }`}>
                    {snapshot.summary.renderTime.toFixed(2)}ms
                  </div>
                </div>
                <div className="p-3 bg-gray-800 rounded border border-gray-700">
                  <div className="text-xs text-gray-400 mb-1">Memory Usage</div>
                  <div className={`text-lg font-bold ${
                    snapshot.summary.memoryUsage > 500 ? 'text-red-400' :
                    snapshot.summary.memoryUsage > 300 ? 'text-yellow-400' :
                    'text-green-400'
                  }`}>
                    {snapshot.summary.memoryUsage.toFixed(2)}MB
                  </div>
                </div>
                <div className="p-3 bg-gray-800 rounded border border-gray-700">
                  <div className="text-xs text-gray-400 mb-1">Network Requests</div>
                  <div className="text-lg font-bold text-blue-400">
                    {snapshot.summary.networkRequests}
                  </div>
                </div>
              </div>
            )}

            {/* Performance Metrics List */}
            <div className="space-y-2">
              {performance.length === 0 ? (
                <div className="text-center text-gray-400 py-8">No performance metrics</div>
              ) : (
                performance.slice(-20).reverse().map(metric => (
                  <div key={metric.id} className="p-3 bg-gray-800 rounded border border-gray-700">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">{metric.label || metric.type}</span>
                      <span className={`text-sm font-medium ${
                        metric.type === 'memory' && metric.value > 500 ? 'text-red-400' :
                        metric.type === 'memory' && metric.value > 300 ? 'text-yellow-400' :
                        metric.type === 'render' && metric.value > 33.33 ? 'text-red-400' :
                        metric.type === 'render' && metric.value > 16.67 ? 'text-yellow-400' :
                        'text-gray-300'
                      }`}>
                        {metric.type === 'memory' ? `${metric.value.toFixed(2)} MB` : 
                         metric.type === 'api' ? `${metric.value}` :
                         `${metric.value.toFixed(2)}ms`}
                      </span>
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      {metric.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="space-y-1 font-mono text-sm">
            {filteredLogs.length === 0 ? (
              <div className="text-center text-gray-400 py-8">No logs</div>
            ) : (
              <>
                {filteredLogs.slice(-100).reverse().map(log => (
                  <div key={log.id} className="flex items-start gap-2 py-1">
                    <span className={`text-xs ${getLevelColor(log.level)}`}>
                      [{log.level.toUpperCase()}]
                    </span>
                    <span className="text-xs text-gray-400">
                      {log.timestamp.toLocaleTimeString()}
                    </span>
                    <span className="flex-1">{log.message}</span>
                  </div>
                ))}
                <div ref={logsEndRef} />
              </>
            )}
          </div>
        )}

        {activeTab === 'network' && (
          <div className="space-y-2">
            {network.length === 0 ? (
              <div className="text-center text-gray-400 py-8">No network requests</div>
            ) : (
              network.slice(-20).reverse().map(req => (
                <div key={req.id} className="p-3 bg-gray-800 rounded border border-gray-700">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium">{req.method} {req.url}</span>
                    <span className={`text-sm ${
                      req.status && req.status >= 400 ? 'text-red-400' : 'text-green-400'
                    }`}>
                      {req.status || 'Pending'}
                    </span>
                  </div>
                  <div className="text-xs text-gray-400">
                    {req.duration.toFixed(2)}ms • {req.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'memory' && (
          <div className="space-y-4">
            {/* Current Memory Stats */}
            {snapshot && snapshot.summary && (
              <div className="p-4 bg-gray-800 rounded border border-gray-700">
                <div className="text-sm font-medium mb-2">Current Memory Usage</div>
                <div className="text-2xl font-bold mb-2">
                  {snapshot.summary.memoryUsage.toFixed(2)} MB
                </div>
                <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${
                      snapshot.summary.memoryUsage > 500 ? 'bg-red-500' :
                      snapshot.summary.memoryUsage > 300 ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}
                    style={{ width: `${Math.min((snapshot.summary.memoryUsage / 1000) * 100, 100)}%` }}
                  />
                </div>
                <div className="text-xs text-gray-400 mt-2">
                  Target: &lt;300MB (optimal), &lt;500MB (acceptable)
                </div>
              </div>
            )}

            {/* Browser Memory API (if available) */}
            {typeof performance !== 'undefined' && (performance as any).memory ? (
              <div className="p-4 bg-gray-800 rounded border border-gray-700">
                <div className="text-sm font-medium mb-2">Browser Memory API</div>
                <div className="text-2xl font-bold">
                  {(((performance as any).memory.usedJSHeapSize) / 1024 / 1024).toFixed(2)} MB
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  Used of {(((performance as any).memory.jsHeapSizeLimit) / 1024 / 1024).toFixed(2)} MB limit
                </div>
              </div>
            ) : (
              <div className="p-4 bg-gray-800 rounded border border-gray-700">
                <div className="text-sm text-gray-400">Browser Memory API not available</div>
                <div className="text-xs text-gray-500 mt-1">
                  Using performance monitoring service instead
                </div>
              </div>
            )}

            {/* Memory Metrics History */}
            <div className="space-y-2">
              <div className="text-sm font-medium text-gray-300 mb-2">Memory History</div>
              {performance.filter(m => m.type === 'memory').length === 0 ? (
                <div className="text-center text-gray-400 py-4">No memory metrics recorded</div>
              ) : (
                performance
                  .filter(m => m.type === 'memory')
                  .slice(-10)
                  .reverse()
                  .map(metric => (
                    <div key={metric.id} className="p-2 bg-gray-800 rounded border border-gray-700">
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-400">{metric.timestamp.toLocaleTimeString()}</span>
                        <span className={`text-sm font-medium ${
                          metric.value > 500 ? 'text-red-400' :
                          metric.value > 300 ? 'text-yellow-400' :
                          'text-green-400'
                        }`}>
                          {metric.value.toFixed(2)} MB
                        </span>
                      </div>
                    </div>
                  ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

