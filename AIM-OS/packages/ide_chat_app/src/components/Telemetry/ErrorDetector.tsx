/**
 * Error Detection & Alerting System
 * Smart error pattern matching and critical error detection
 */

import React, { useState, useEffect, useMemo } from 'react'
import { AlertTriangle, X, RefreshCw, Filter, Search, Bell, BellOff, CheckCircle, XCircle } from 'lucide-react'

interface ErrorPattern {
  id: string
  pattern: RegExp
  severity: 'critical' | 'warning' | 'info'
  category: string
  description: string
  count: number
  lastSeen: string
}

interface DetectedError {
  id: string
  message: string
  pattern: ErrorPattern
  timestamp: string
  source: string
  context?: string
  resolved: boolean
}

interface LogEntry {
  timestamp: string
  level: string
  source: string
  message: string
}

// Use existing logAPI from LogViewer - don't redeclare global

// Common error patterns for AIM-OS ecosystem
const ERROR_PATTERNS: ErrorPattern[] = [
  {
    id: 'mcp-connection-failed',
    pattern: /(?:MCP|mcp).*connection.*failed|Cannot connect to MCP server|MCP server.*not available/i,
    severity: 'critical',
    category: 'MCP',
    description: 'MCP server connection failure',
    count: 0,
    lastSeen: ''
  },
  {
    id: 'mcp-timeout',
    pattern: /(?:MCP|mcp).*timeout|request timeout|connection timeout/i,
    severity: 'warning',
    category: 'MCP',
    description: 'MCP request timeout',
    count: 0,
    lastSeen: ''
  },
  {
    id: 'electron-ipc-error',
    pattern: /IPC.*error|ipc.*failed|remote method.*error/i,
    severity: 'critical',
    category: 'Electron',
    description: 'Electron IPC communication error',
    count: 0,
    lastSeen: ''
  },
  {
    id: 'extension-not-loaded',
    pattern: /extension.*not.*loaded|no provider registered|extension.*failed/i,
    severity: 'critical',
    category: 'Extension',
    description: 'Cursor extension not loaded or failed',
    count: 0,
    lastSeen: ''
  },
  {
    id: 'daemon-down',
    pattern: /daemon.*down|daemon.*not.*available|backend.*not.*available/i,
    severity: 'critical',
    category: 'Daemon',
    description: 'AIM-OS daemon not available',
    count: 0,
    lastSeen: ''
  },
  {
    id: 'memory-leak',
    pattern: /memory.*leak|out of memory|heap.*overflow/i,
    severity: 'critical',
    category: 'System',
    description: 'Memory leak detected',
    count: 0,
    lastSeen: ''
  },
  {
    id: 'port-conflict',
    pattern: /port.*in use|address.*already.*in use|EADDRINUSE/i,
    severity: 'warning',
    category: 'Network',
    description: 'Port conflict detected',
    count: 0,
    lastSeen: ''
  },
  {
    id: 'permission-denied',
    pattern: /permission.*denied|EACCES|access.*denied/i,
    severity: 'warning',
    category: 'System',
    description: 'Permission denied error',
    count: 0,
    lastSeen: ''
  },
  {
    id: 'file-not-found',
    pattern: /file.*not.*found|ENOENT|cannot.*find.*file/i,
    severity: 'warning',
    category: 'File System',
    description: 'File not found error',
    count: 0,
    lastSeen: ''
  },
  {
    id: 'network-error',
    pattern: /network.*error|ECONNREFUSED|ENOTFOUND|timeout.*network/i,
    severity: 'warning',
    category: 'Network',
    description: 'Network connection error',
    count: 0,
    lastSeen: ''
  }
]

export const ErrorDetector: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [detectedErrors, setDetectedErrors] = useState<DetectedError[]>([])
  const [errorPatterns, setErrorPatterns] = useState<ErrorPattern[]>(ERROR_PATTERNS)
  const [alertsEnabled, setAlertsEnabled] = useState(true)
  const [filterSeverity, setFilterSeverity] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [autoRefresh, setAutoRefresh] = useState(true)

  // Fetch logs and detect errors
  const fetchAndDetect = async () => {
    if (!window.logAPI) return

    try {
      // Fetch error and warn level logs
      const errorResult = await window.logAPI.readLogs({ limit: 500, level: 'error' })
      const warnResult = await window.logAPI.readLogs({ limit: 500, level: 'warn' })
      
      const allLogs = [
        ...(errorResult.logs || []),
        ...(warnResult.logs || [])
      ]
      
      setLogs(allLogs)

      // Detect errors using patterns
      const newErrors: DetectedError[] = []
      const updatedPatterns = [...errorPatterns]

      allLogs.forEach(log => {
        errorPatterns.forEach((pattern, index) => {
          if (pattern.pattern.test(log.message)) {
            updatedPatterns[index].count++
            updatedPatterns[index].lastSeen = log.timestamp

            // Check if we've already detected this error recently (within 5 minutes)
            const existingError = detectedErrors.find(
              e => e.pattern.id === pattern.id && 
              new Date(log.timestamp).getTime() - new Date(e.timestamp).getTime() < 300000
            )

            if (!existingError) {
              newErrors.push({
                id: `${pattern.id}-${Date.now()}-${Math.random()}`,
                message: log.message,
                pattern: updatedPatterns[index],
                timestamp: log.timestamp,
                source: log.source,
                context: log.message.substring(0, 200),
                resolved: false
              })

              // Show alert for critical errors
              if (alertsEnabled && pattern.severity === 'critical') {
                console.warn(`🚨 CRITICAL ERROR DETECTED: ${pattern.description}`, log.message)
              }
            }
          }
        })
      })

      setErrorPatterns(updatedPatterns)
      setDetectedErrors(prev => [...newErrors, ...prev].slice(0, 100)) // Keep last 100 errors
    } catch (error) {
      console.error('Failed to fetch logs for error detection:', error)
    }
  }

  useEffect(() => {
    if (autoRefresh) {
      fetchAndDetect()
      const interval = setInterval(fetchAndDetect, 5000) // Check every 5 seconds
      return () => clearInterval(interval)
    }
  }, [autoRefresh, errorPatterns])

  // Filter detected errors
  const filteredErrors = useMemo(() => {
    let filtered = detectedErrors

    if (filterSeverity !== 'all') {
      filtered = filtered.filter(e => e.pattern.severity === filterSeverity)
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(e => 
        e.message.toLowerCase().includes(query) ||
        e.pattern.description.toLowerCase().includes(query) ||
        e.pattern.category.toLowerCase().includes(query)
      )
    }

    return filtered.sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    )
  }, [detectedErrors, filterSeverity, searchQuery])

  // Mark error as resolved
  const markResolved = (errorId: string) => {
    setDetectedErrors(prev => 
      prev.map(e => e.id === errorId ? { ...e, resolved: true } : e)
    )
  }

  // Get severity color
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400 bg-red-900/20 border-red-700/50'
      case 'warning': return 'text-yellow-400 bg-yellow-900/20 border-yellow-700/50'
      case 'info': return 'text-blue-400 bg-blue-900/20 border-blue-700/50'
      default: return 'text-gray-400 bg-gray-800 border-gray-700'
    }
  }

  // Statistics
  const stats = useMemo(() => {
    const critical = detectedErrors.filter(e => e.pattern.severity === 'critical' && !e.resolved).length
    const warnings = detectedErrors.filter(e => e.pattern.severity === 'warning' && !e.resolved).length
    const resolved = detectedErrors.filter(e => e.resolved).length
    
    return { critical, warnings, resolved, total: detectedErrors.length }
  }, [detectedErrors])

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-800">
        <div className="flex items-center gap-4">
          <AlertTriangle className="w-6 h-6 text-red-400" />
          <h2 className="text-xl font-semibold">Error Detection & Alerting</h2>
          {stats.critical > 0 && (
            <span className="px-3 py-1 bg-red-600/20 text-red-400 rounded-full text-sm font-semibold">
              {stats.critical} Critical
            </span>
          )}
          {stats.warnings > 0 && (
            <span className="px-3 py-1 bg-yellow-600/20 text-yellow-400 rounded-full text-sm font-semibold">
              {stats.warnings} Warnings
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setAlertsEnabled(!alertsEnabled)}
            className={`px-3 py-1 rounded text-sm flex items-center gap-2 ${
              alertsEnabled ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            {alertsEnabled ? <Bell className="w-4 h-4" /> : <BellOff className="w-4 h-4" />}
            {alertsEnabled ? 'Alerts On' : 'Alerts Off'}
          </button>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-3 py-1 rounded text-sm flex items-center gap-2 ${
              autoRefresh ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin' : ''}`} />
            Auto Refresh
          </button>
          <button
            onClick={fetchAndDetect}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
          >
            <RefreshCw className="w-4 h-4 inline mr-1" />
            Refresh
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="p-4 border-b border-gray-800 bg-gray-800/50">
        <div className="flex items-center gap-4">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search errors..."
            className="flex-1 bg-gray-900 text-white px-3 py-2 rounded border border-gray-700 text-sm focus:outline-none focus:border-blue-500"
          />
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="bg-gray-900 text-white px-3 py-2 rounded border border-gray-700 text-sm focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical Only</option>
            <option value="warning">Warnings Only</option>
            <option value="info">Info Only</option>
          </select>
        </div>
      </div>

      {/* Statistics */}
      <div className="p-4 border-b border-gray-800 bg-gray-800/30">
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-400">{stats.critical}</div>
            <div className="text-sm text-gray-400">Critical Errors</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-400">{stats.warnings}</div>
            <div className="text-sm text-gray-400">Warnings</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">{stats.resolved}</div>
            <div className="text-sm text-gray-400">Resolved</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">{stats.total}</div>
            <div className="text-sm text-gray-400">Total Detected</div>
          </div>
        </div>
      </div>

      {/* Error Patterns */}
      <div className="p-4 border-b border-gray-800 bg-gray-800/20">
        <h3 className="text-sm font-semibold mb-2 text-gray-400">Error Patterns</h3>
        <div className="flex flex-wrap gap-2">
          {errorPatterns.map(pattern => (
            <div
              key={pattern.id}
              className={`px-3 py-1 rounded text-xs border ${getSeverityColor(pattern.severity)}`}
            >
              {pattern.description}: {pattern.count}
            </div>
          ))}
        </div>
      </div>

      {/* Error List */}
      <div className="flex-1 overflow-auto p-4">
        {filteredErrors.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-400" />
            <p>No errors detected</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredErrors.map(error => (
              <div
                key={error.id}
                className={`p-4 rounded-lg border ${
                  error.resolved 
                    ? 'bg-gray-800/50 border-gray-700 opacity-60' 
                    : getSeverityColor(error.pattern.severity)
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${getSeverityColor(error.pattern.severity)}`}>
                        {error.pattern.severity.toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-400">{error.pattern.category}</span>
                      <span className="text-xs text-gray-500">{new Date(error.timestamp).toLocaleString()}</span>
                    </div>
                    <div className="font-semibold mb-1">{error.pattern.description}</div>
                    <div className="text-sm text-gray-300 mb-2">{error.message}</div>
                    <div className="text-xs text-gray-500">
                      Source: {error.source} • Pattern: {error.pattern.id}
                    </div>
                  </div>
                  {!error.resolved && (
                    <button
                      onClick={() => markResolved(error.id)}
                      className="ml-4 px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm flex items-center gap-1"
                    >
                      <CheckCircle className="w-4 h-4" />
                      Resolve
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

