import React, { useState, useEffect, useMemo } from 'react'
import { Copy, Download, Filter, RefreshCw, Search, X, ChevronDown, ChevronUp } from 'lucide-react'

interface LogEntry {
  timestamp: string
  level: 'log' | 'error' | 'warn' | 'info'
  source: string
  message: string
}

interface LogViewerProps {
  onClose?: () => void
}

declare global {
  interface Window {
    logAPI?: {
      readLogs: (options?: { limit?: number; level?: string; source?: string }) => Promise<{
        success: boolean
        logs?: LogEntry[]
        error?: string
      }>
    }
  }
}

export const LogViewer: React.FC<LogViewerProps> = ({ onClose }) => {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [levelFilter, setLevelFilter] = useState<string>('all')
  const [sourceFilter, setSourceFilter] = useState<string>('all')
  const [timeFilter, setTimeFilter] = useState<'newest' | 'oldest'>('newest')
  const [expandedSessions, setExpandedSessions] = useState<Set<string>>(new Set())

  // Fetch logs
  const fetchLogs = async () => {
    if (!window.logAPI) return
    
    setLoading(true)
    try {
      const result = await window.logAPI.readLogs({ limit: 1000 })
      if (result.success && result.logs) {
        setLogs(result.logs)
      }
    } catch (error) {
      console.error('Failed to fetch logs:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLogs()
    // Refresh every 3 seconds
    const interval = setInterval(fetchLogs, 3000)
    return () => clearInterval(interval)
  }, [])

  // Group logs by session (approximate - using time gaps)
  const groupedLogs = useMemo(() => {
    const groups: { [key: string]: LogEntry[] } = {}
    let currentSession = 'session-1'
    let lastTimestamp: Date | null = null

    logs.forEach(log => {
      const logTime = new Date(log.timestamp)
      if (lastTimestamp && (logTime.getTime() - lastTimestamp.getTime()) > 60000) {
        // 1 minute gap = new session
        const sessionNum = parseInt(currentSession.split('-')[1]) + 1
        currentSession = `session-${sessionNum}`
      }
      
      if (!groups[currentSession]) {
        groups[currentSession] = []
      }
      groups[currentSession].push(log)
      lastTimestamp = logTime
    })

    return groups
  }, [logs])

  // Filter logs
  const filteredLogs = useMemo(() => {
    let filtered = logs

    // Apply level filter
    if (levelFilter !== 'all') {
      filtered = filtered.filter(log => log.level === levelFilter)
    }

    // Apply source filter
    if (sourceFilter !== 'all') {
      filtered = filtered.filter(log => log.source === sourceFilter.toUpperCase())
    }

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(log =>
        log.message.toLowerCase().includes(query) ||
        log.source.toLowerCase().includes(query) ||
        log.timestamp.toLowerCase().includes(query)
      )
    }

    // Sort by time
    filtered.sort((a, b) => {
      const timeA = new Date(a.timestamp).getTime()
      const timeB = new Date(b.timestamp).getTime()
      return timeFilter === 'newest' ? timeB - timeA : timeA - timeB
    })

    return filtered
  }, [logs, levelFilter, sourceFilter, searchQuery, timeFilter])

  // Copy logs to clipboard
  const copyLogs = async () => {
    const logText = filteredLogs.map(log =>
      `[${log.timestamp}] [${log.level.toUpperCase()}] [${log.source}] ${log.message}`
    ).join('\n')
    
    try {
      await navigator.clipboard.writeText(logText)
      alert(`Copied ${filteredLogs.length} logs to clipboard!`)
    } catch (error) {
      console.error('Failed to copy logs:', error)
    }
  }

  // Export logs to file
  const exportLogs = () => {
    const logText = filteredLogs.map(log =>
      `[${log.timestamp}] [${log.level.toUpperCase()}] [${log.source}] ${log.message}`
    ).join('\n')
    
    const blob = new Blob([logText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `aimos-logs-${new Date().toISOString()}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'error': return 'text-red-400 bg-red-900/20'
      case 'warn': return 'text-yellow-400 bg-yellow-900/20'
      case 'info': return 'text-blue-400 bg-blue-900/20'
      default: return 'text-gray-400 bg-gray-800/20'
    }
  }

  const toggleSession = (session: string) => {
    const newExpanded = new Set(expandedSessions)
    if (newExpanded.has(session)) {
      newExpanded.delete(session)
    } else {
      newExpanded.add(session)
    }
    setExpandedSessions(newExpanded)
  }

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-800">
        <div className="flex items-center gap-4">
          <h2 className="text-lg font-semibold">Developer Tools - Console Logs</h2>
          <button
            onClick={fetchLogs}
            disabled={loading}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm flex items-center gap-2 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={copyLogs}
            className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-sm flex items-center gap-2"
            title="Copy filtered logs to clipboard"
          >
            <Copy className="w-4 h-4" />
            Copy ({filteredLogs.length})
          </button>
          <button
            onClick={exportLogs}
            className="px-3 py-1 bg-purple-600 hover:bg-purple-700 rounded text-sm flex items-center gap-2"
            title="Export filtered logs to file"
          >
            <Download className="w-4 h-4" />
            Export
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
            >
              Close
            </button>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="p-4 border-b border-gray-800 bg-gray-800/50">
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search logs..."
              className="w-full bg-gray-900 text-white px-10 py-2 rounded-lg border border-gray-700 text-sm focus:outline-none focus:border-blue-500"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Level Filter */}
          <select
            value={levelFilter}
            onChange={(e) => setLevelFilter(e.target.value)}
            className="bg-gray-900 text-white px-3 py-2 rounded-lg border border-gray-700 text-sm focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Levels</option>
            <option value="error">Errors</option>
            <option value="warn">Warnings</option>
            <option value="info">Info</option>
            <option value="log">Logs</option>
          </select>

          {/* Source Filter */}
          <select
            value={sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value)}
            className="bg-gray-900 text-white px-3 py-2 rounded-lg border border-gray-700 text-sm focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Sources</option>
            <option value="main">Main Process</option>
            <option value="renderer">Renderer Process</option>
          </select>

          {/* Time Filter */}
          <select
            value={timeFilter}
            onChange={(e) => setTimeFilter(e.target.value as 'newest' | 'oldest')}
            className="bg-gray-900 text-white px-3 py-2 rounded-lg border border-gray-700 text-sm focus:outline-none focus:border-blue-500"
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
          </select>

          {/* Stats */}
          <div className="text-sm text-gray-400">
            Showing {filteredLogs.length} of {logs.length} logs
          </div>
        </div>
      </div>

      {/* Log List */}
      <div className="flex-1 overflow-auto p-4">
        {loading && logs.length === 0 ? (
          <div className="text-center text-gray-400 py-8">Loading logs...</div>
        ) : filteredLogs.length === 0 ? (
          <div className="text-center text-gray-400 py-8">No logs found</div>
        ) : (
          <div className="space-y-1">
            {filteredLogs.map((log, index) => (
              <div
                key={index}
                className="p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 border border-gray-700/50 font-mono text-xs"
              >
                <div className="flex items-start gap-3">
                  {/* Level Badge */}
                  <span className={`px-2 py-0.5 rounded text-xs font-semibold ${getLevelColor(log.level)}`}>
                    {log.level.toUpperCase()}
                  </span>
                  
                  {/* Timestamp */}
                  <span className="text-gray-500 text-xs">
                    {new Date(log.timestamp).toLocaleString()}
                  </span>
                  
                  {/* Source */}
                  <span className="text-blue-400 text-xs font-semibold">
                    [{log.source}]
                  </span>
                  
                  {/* Message */}
                  <span className="text-gray-300 flex-1 break-words">
                    {log.message}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

