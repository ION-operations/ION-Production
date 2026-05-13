/**
 * Debug Console Panel Component
 * 
 * Phase 2.3: Bottom Drawer Panels
 * 
 * Advanced debugging console with AIM-OS integration.
 * Features:
 * - Console log viewer
 * - Error tracking
 * - Performance metrics
 * - Debug breakpoints
 * - AIM-OS integration (VIF debugging, CAS analysis, SDF-CVF feedback)
 */

import React, { useState, useCallback, useRef, useEffect, useMemo } from 'react'
import { Bug, AlertCircle, Info, X, Trash2, Filter, Play, Pause, Square, RefreshCw, Search, Copy, Download, Zap, Brain, Shield, Clock, FileCode, ChevronDown, ChevronRight, Activity, Eye } from 'lucide-react'
import { useAIMOS } from '../../hooks/useAIMOS'
import { useDebounce } from '../../hooks/useDebounce'
import { usePDAS } from '../../hooks/usePDAS'
import { ErrorBoundary } from '../ErrorBoundary'
import { LoadingState } from '../LoadingState'

interface LogEntry {
  id: string
  timestamp: string
  level: 'log' | 'info' | 'warn' | 'error' | 'debug' | 'system'
  message: string
  source?: string
  stack?: string
  metadata?: Record<string, any>
  correlationId?: string // Link to related events/atoms
  agent?: string // Agent that generated the log
  vifConfidence?: number // VIF confidence for log entry
  cmcAtomId?: string // CMC integration
}

const mockLogs: LogEntry[] = [
  {
    id: 'log-1',
    timestamp: '2025-11-07T10:30:15.123Z',
    level: 'info',
    message: 'RevIDELayout initialized',
    source: 'RevIDELayout.tsx',
    metadata: { component: 'RevIDELayout', phase: 'initialization' },
    agent: 'Rev',
    vifConfidence: 0.98,
    cmcAtomId: 'cmc-log-001',
  },
  {
    id: 'log-2',
    timestamp: '2025-11-07T10:30:16.456Z',
    level: 'log',
    message: 'FileExplorerPanel mounted',
    source: 'FileExplorerPanel.tsx',
    metadata: { component: 'FileExplorerPanel', files: 12 },
    agent: 'Rev',
    vifConfidence: 0.95,
  },
  {
    id: 'log-3',
    timestamp: '2025-11-07T10:30:17.789Z',
    level: 'warn',
    message: 'AIM-OS connection timeout',
    source: 'AIMOSService.ts',
    metadata: { service: 'CMC', timeout: 5000 },
    agent: 'System',
    correlationId: 'corr-001',
  },
  {
    id: 'log-4',
    timestamp: '2025-11-07T10:30:18.012Z',
    level: 'error',
    message: 'Failed to load memory: Connection refused',
    source: 'AIMemoryPanel.tsx',
    stack: 'Error: Connection refused\n    at AIMOSService.retrieveMemory (AIMOSService.ts:45)\n    at AIMemoryPanel.loadMemories (AIMemoryPanel.tsx:123)',
    metadata: { service: 'CMC', endpoint: '/api/memory/retrieve' },
    agent: 'System',
    correlationId: 'corr-001',
    cmcAtomId: 'cmc-log-002',
  },
  {
    id: 'log-5',
    timestamp: '2025-11-07T10:30:19.345Z',
    level: 'debug',
    message: 'Panel state updated: leftDrawerSize=20',
    source: 'RevIDELayout.tsx',
    metadata: { panel: 'leftDrawer', size: 20 },
    agent: 'Rev',
    vifConfidence: 0.99,
  },
  {
    id: 'log-6',
    timestamp: '2025-11-07T10:30:20.567Z',
    level: 'system',
    message: 'VIF validation completed',
    source: 'VIFService.ts',
    metadata: { validationType: 'quintet_parity', score: 0.96 },
    agent: 'VIF',
    vifConfidence: 0.99,
    cmcAtomId: 'cmc-log-003',
  },
]

export const DebugConsolePanel: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>(mockLogs)
  const [filterLevel, setFilterLevel] = useState<'all' | LogEntry['level']>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [isPaused, setIsPaused] = useState(false)
  const [autoScroll, setAutoScroll] = useState(true)
  const [expandedLog, setExpandedLog] = useState<string | null>(null)
  const [selectedLog, setSelectedLog] = useState<LogEntry | null>(null)
  const [showPDAS, setShowPDAS] = useState(false)
  const logContainerRef = useRef<HTMLDivElement>(null)

  // Debounce search query for performance
  const debouncedSearchQuery = useDebounce(searchQuery, 300)

  // AIM-OS integration
  const { vif, cas, cmc, isConnected, useMockData, loading } = useAIMOS()
  
  // PDAS integration
  const { auditTrail, metrics, getAuditTrail, getMetrics } = usePDAS('DebugConsolePanel')

  // Load debug logs from AIM-OS (CMC + VIF + CAS)
  useEffect(() => {
    const loadDebugLogs = async () => {
      if (!useMockData && isConnected) {
        try {
          // Load recent CMC atoms with debug/tool modality
          const debugAtoms = await cmc.retrieve('debug error warn log', 100)
          
          // Transform CMC atoms to LogEntry format
          const loadedLogs: LogEntry[] = debugAtoms
            .filter(atom => atom.modality === 'event' || atom.modality === 'tool')
            .map(atom => ({
              id: atom.id,
              timestamp: atom.created_at,
              level: atom.metadata?.level || 'log',
              message: atom.content.inline || '',
              source: atom.metadata?.source,
              stack: atom.metadata?.stack,
              metadata: atom.metadata,
              correlationId: atom.witness.correlation_id,
              agent: atom.metadata?.agent,
              vifConfidence: atom.witness.uncertainty_band === 'green' ? 0.9 : 
                           atom.witness.uncertainty_band === 'yellow' ? 0.7 : 0.5,
              cmcAtomId: atom.id,
            }))
          
          setLogs(loadedLogs)
        } catch (error) {
          console.warn('Failed to load debug logs from AIM-OS, using mock data', error)
          // Keep mock logs as fallback
        }
      }
    }
    
    loadDebugLogs()
    // Refresh every 5 seconds
    const interval = setInterval(loadDebugLogs, 5000)
    return () => clearInterval(interval)
  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight
    }
  }, [logs, autoScroll])

  const filteredLogs = useMemo(() => {
    return logs.filter((log) => {
      const matchesLevel = filterLevel === 'all' || log.level === filterLevel
      const matchesSearch =
        log.message.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
        log.source?.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
        log.agent?.toLowerCase().includes(debouncedSearchQuery.toLowerCase())
      return matchesLevel && matchesSearch
    })
  }, [logs, filterLevel, debouncedSearchQuery])

  const errorCount = useMemo(() => logs.filter(l => l.level === 'error').length, [logs])
  const warningCount = useMemo(() => logs.filter(l => l.level === 'warn').length, [logs])
  const groupedByCorrelation = useMemo(() => {
    const groups: Record<string, LogEntry[]> = {}
    logs.forEach(log => {
      if (log.correlationId) {
        if (!groups[log.correlationId]) groups[log.correlationId] = []
        groups[log.correlationId].push(log)
      }
    })
    return groups
  }, [logs])

  const getLevelIcon = (level: LogEntry['level']) => {
    switch (level) {
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-400" />
      case 'warn':
        return <AlertCircle className="w-4 h-4 text-yellow-400" />
      case 'info':
        return <Info className="w-4 h-4 text-blue-400" />
      case 'debug':
        return <Bug className="w-4 h-4 text-gray-400" />
      case 'system':
        return <Zap className="w-4 h-4 text-purple-400" />
      default:
        return <Info className="w-4 h-4 text-gray-400" />
    }
  }

  const getLevelColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'error':
        return 'text-red-400 border-red-500/20 bg-red-500/10'
      case 'warn':
        return 'text-yellow-400 border-yellow-500/20 bg-yellow-500/10'
      case 'info':
        return 'text-blue-400 border-blue-500/20 bg-blue-500/10'
      case 'debug':
        return 'text-gray-400 border-gray-500/20 bg-gray-500/10'
      case 'system':
        return 'text-purple-400 border-purple-500/20 bg-purple-500/10'
      default:
        return 'text-gray-300 border-gray-500/20 bg-gray-500/10'
    }
  }

  const handleClear = useCallback(() => {
    setLogs([])
  }, [])

  const handlePause = useCallback(() => {
    setIsPaused((prev) => !prev)
  }, [])

  const handleExport = useCallback(() => {
    const logText = logs.map(log => 
      `[${log.timestamp}] [${log.level.toUpperCase()}] ${log.source || 'Unknown'}: ${log.message}`
    ).join('\n')
    const blob = new Blob([logText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `debug-console-${new Date().toISOString()}.log`
    a.click()
    URL.revokeObjectURL(url)
  }, [logs])

  const handleCopyLog = useCallback((log: LogEntry) => {
    const logText = `[${log.timestamp}] [${log.level.toUpperCase()}] ${log.source || 'Unknown'}: ${log.message}${log.stack ? '\n' + log.stack : ''}`
    navigator.clipboard.writeText(logText)
  }, [])

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-900 font-mono text-sm" role="complementary" aria-label="Debug Console Panel">
        {loading.cmc || loading.vif ? (
          <LoadingState message="Loading debug logs..." />
        ) : (
          <>
      {/* Header */}
      <div className="h-10 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-3 shrink-0">
        <div className="flex items-center">
          <Bug className="w-4 h-4 mr-2 text-red-400" />
          <span className="text-sm font-semibold text-gray-300">Debug Console</span>
          <span className="ml-2 px-2 py-0.5 bg-gray-700 text-gray-400 text-xs rounded">
            {filteredLogs.length} {filteredLogs.length === 1 ? 'entry' : 'entries'}
          </span>
          {/* PDAS Toggle */}
          <button
            onClick={() => setShowPDAS(!showPDAS)}
            className={`ml-2 px-2 py-0.5 text-xs rounded transition-colors flex items-center gap-1 ${
              showPDAS
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
            }`}
            title="Toggle PDAS view"
            aria-label="Toggle PDAS view"
          >
            <Eye className="w-3 h-3" />
            PDAS
          </button>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={handlePause}
            className={`p-1.5 rounded transition-colors ${
              isPaused ? 'bg-yellow-600/20 text-yellow-400' : 'text-gray-400 hover:bg-gray-700'
            }`}
            aria-label={isPaused ? 'Resume logging' : 'Pause logging'}
            title={isPaused ? 'Resume' : 'Pause'}
          >
            {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
          </button>
          <button
            onClick={handleExport}
            className="p-1.5 text-gray-400 hover:text-gray-300 hover:bg-gray-700 rounded transition-colors"
            aria-label="Export logs"
            title="Export logs"
          >
            <Download className="w-4 h-4" />
          </button>
          <button
            onClick={handleClear}
            className="p-1.5 text-gray-400 hover:text-gray-300 hover:bg-gray-700 rounded transition-colors"
            aria-label="Clear logs"
            title="Clear logs"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* PDAS View */}
      {showPDAS && (
        <div className="px-3 py-2 border-b border-gray-700 bg-gray-800/50 shrink-0">
          <div className="flex items-center gap-4 mb-2">
            <div className="flex items-center gap-2">
              <Eye className="w-4 h-4 text-blue-400" />
              <span className="text-xs font-semibold text-gray-300">PDAS Observability</span>
            </div>
            {metrics.renderTime && (
              <div className="flex items-center gap-1 text-xs text-gray-400">
                <Activity className="w-3 h-3" />
                Render: {metrics.renderTime.toFixed(0)}ms
              </div>
            )}
            {metrics.errorRate !== undefined && (
              <div className={`flex items-center gap-1 text-xs ${metrics.errorRate > 0 ? 'text-red-400' : 'text-green-400'}`}>
                <AlertCircle className="w-3 h-3" />
                Error Rate: {metrics.errorRate.toFixed(1)}%
              </div>
            )}
          </div>
          {auditTrail.length > 0 && (
            <div className="text-xs text-gray-500">
              {auditTrail.length} audit entries | Last: {auditTrail[auditTrail.length - 1]?.action || 'N/A'}
            </div>
          )}
        </div>
      )}

      {/* Filters */}
      <div className="px-3 py-2 border-b border-gray-700 bg-gray-800 shrink-0">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <div className="flex gap-1">
            {['all', 'error', 'warn', 'info', 'log', 'debug', 'system'].map((level) => (
              <button
                key={level}
                onClick={() => setFilterLevel(level as any)}
                className={`px-2 py-1 text-xs rounded ${
                  filterLevel === level
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {level}
              </button>
            ))}
          </div>
          <div className="relative ml-auto flex-1 max-w-xs">
            <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
            <input
              type="text"
              placeholder="Search logs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-8 pr-2 py-1 bg-gray-900 border border-gray-700 rounded text-xs text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-500"
              aria-label="Search logs"
            />
          </div>
        </div>
      </div>

      {/* Logs */}
      <div
        ref={logContainerRef}
        className="flex-1 overflow-y-auto p-2 space-y-1"
        onScroll={() => {
          if (logContainerRef.current) {
            const { scrollTop, scrollHeight, clientHeight } = logContainerRef.current
            setAutoScroll(scrollTop + clientHeight >= scrollHeight - 10)
          }
        }}
      >
        {filteredLogs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm">
            <Bug className="w-8 h-8 mb-2 opacity-50" />
            <p>No logs found</p>
            {(searchQuery || filterLevel !== 'all') && (
              <button
                onClick={() => {
                  setSearchQuery('')
                  setFilterLevel('all')
                }}
                className="mt-2 px-3 py-1 text-xs bg-blue-600 hover:bg-blue-700 rounded text-white"
              >
                Clear Filters
              </button>
            )}
          </div>
        ) : (
          <>
            {filteredLogs.map((log) => {
            const isExpanded = expandedLog === log.id
            return (
              <div
                key={log.id}
                className={`p-2 rounded border cursor-pointer transition-colors ${getLevelColor(log.level)} ${
                  selectedLog?.id === log.id ? 'ring-2 ring-blue-500' : ''
                }`}
                onClick={() => setSelectedLog(log)}
              >
                <div className="flex items-start gap-2">
                  {getLevelIcon(log.level)}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className="text-xs text-gray-500 font-mono">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                      {log.source && (
                        <>
                          <span className="text-gray-600">•</span>
                          <span className="text-xs text-gray-500 font-mono">{log.source}</span>
                        </>
                      )}
                      {log.agent && (
                        <>
                          <span className="text-gray-600">•</span>
                          <span className="text-xs text-purple-400 flex items-center gap-0.5">
                            <Brain className="w-3 h-3" />
                            {log.agent}
                          </span>
                        </>
                      )}
                      {log.vifConfidence !== undefined && (
                        <>
                          <span className="text-gray-600">•</span>
                          <span className={`text-xs px-1 py-0.5 rounded flex items-center gap-0.5 ${
                            log.vifConfidence >= 0.95 ? 'bg-green-600/20 text-green-400' :
                            log.vifConfidence >= 0.90 ? 'bg-yellow-600/20 text-yellow-400' :
                            'bg-red-600/20 text-red-400'
                          }`} title="VIF Confidence">
                            <Shield className="w-3 h-3" />
                            {(log.vifConfidence * 100).toFixed(0)}%
                          </span>
                        </>
                      )}
                      {log.correlationId && (
                        <>
                          <span className="text-gray-600">•</span>
                          <span className="text-xs text-blue-400 font-mono">
                            {log.correlationId}
                          </span>
                        </>
                      )}
                      {(log.stack || log.metadata) && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setExpandedLog(isExpanded ? null : log.id)
                          }}
                          className="ml-auto p-0.5 hover:bg-gray-700 rounded"
                        >
                          {isExpanded ? (
                            <ChevronDown className="w-3 h-3 text-gray-400" />
                          ) : (
                            <ChevronRight className="w-3 h-3 text-gray-400" />
                          )}
                        </button>
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleCopyLog(log)
                        }}
                        className="p-0.5 hover:bg-gray-700 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                        title="Copy log"
                      >
                        <Copy className="w-3 h-3 text-gray-400" />
                      </button>
                    </div>
                    <div className="text-sm mb-1">{log.message}</div>
                    {isExpanded && (
                      <>
                        {log.stack && (
                          <div className="mt-2 p-2 bg-gray-900/50 rounded text-xs text-gray-400 font-mono whitespace-pre-wrap">
                            {log.stack}
                          </div>
                        )}
                        {log.metadata && (
                          <div className="mt-2 p-2 bg-gray-900/50 rounded text-xs">
                            <div className="text-gray-500 mb-1 flex items-center gap-1">
                              <FileCode className="w-3 h-3" />
                              Metadata:
                            </div>
                            {Object.entries(log.metadata).map(([key, value]) => (
                              <div key={key} className="text-gray-400">
                                <span className="text-gray-500">{key}:</span> {String(value)}
                              </div>
                            ))}
                          </div>
                        )}
                        {log.cmcAtomId && (
                          <div className="mt-2 text-xs text-purple-400 flex items-center gap-1">
                            <Brain className="w-3 h-3" />
                            CMC Atom: <span className="font-mono">{log.cmcAtomId}</span>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
            )
            })}
          </>
        )}
      </div>

      {/* Footer */}
      <div className="h-8 bg-gray-800 border-t border-gray-700 flex items-center justify-between px-3 shrink-0">
        <div className="flex items-center gap-4 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <AlertCircle className="w-3 h-3 text-red-400" />
            Errors: {errorCount}
          </span>
          <span className="flex items-center gap-1">
            <AlertCircle className="w-3 h-3 text-yellow-400" />
            Warnings: {warningCount}
          </span>
          {Object.keys(groupedByCorrelation).length > 0 && (
            <span className="text-blue-400">
              {Object.keys(groupedByCorrelation).length} correlation{Object.keys(groupedByCorrelation).length !== 1 ? 's' : ''}
            </span>
          )}
        </div>
        <div className="text-xs text-gray-500 flex items-center gap-2">
          {isPaused && <span className="text-yellow-400 flex items-center gap-1"><Pause className="w-3 h-3" /> Paused</span>}
          {autoScroll && !isPaused && <span className="text-green-400 flex items-center gap-1"><Play className="w-3 h-3" /> Auto-scroll</span>}
        </div>
      </div>
          </>
        )}
      </div>
    </ErrorBoundary>
  )
}

