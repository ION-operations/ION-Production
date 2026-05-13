// Debug Console Panel - V2 Feature Implementation
// Real-time log viewing, system breakdown, infrastructure status, analysis insights, evidence trails

import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { useCMC, useSEG, useTCS, useCAS } from '../hooks/useAIMOS'
import { 
  Bug, Activity, Filter, Search, RefreshCw,
  Play, Pause, Trash2, ChevronDown
} from 'lucide-react'

interface LogEntry {
  id: string
  timestamp: Date
  level: 'info' | 'warn' | 'error' | 'debug'
  system: 'CMC' | 'HHNI' | 'VIF' | 'SEG' | 'APOE' | 'TCS' | 'CAS' | 'IIS' | 'SYSTEM'
  message: string
  metadata?: Record<string, any>
  evidenceIds?: string[]
}

interface SystemStatus {
  system: string
  status: 'healthy' | 'degraded' | 'error'
  metrics: Record<string, any>
  lastUpdate: Date
  errorCount: number
  warningCount: number
}

interface DebugConsolePanelProps {
  onStatusChange?: (status: string | null) => void
}

export const DebugConsolePanel: React.FC<DebugConsolePanelProps> = ({ onStatusChange }) => {
  const { getStats } = useCMC()
  const { getMetrics } = useCAS()
  const { entities, contradictions } = useSEG()
  const { getSummary } = useTCS()
  
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [systemStatuses, setSystemStatuses] = useState<SystemStatus[]>([])
  const [selectedSystem, setSelectedSystem] = useState<string | null>(null)
  const [logLevelFilter, setLogLevelFilter] = useState<Set<string>>(new Set(['info', 'warn', 'error']))
  const [searchQuery, setSearchQuery] = useState('')
  const [isPaused, setIsPaused] = useState(false)
  const [selectedLogId, setSelectedLogId] = useState<string | null>(null)
  const [systemDropdownOpen, setSystemDropdownOpen] = useState(false)
  
  // Generate mock logs for demonstration
  const generateMockLogs = useCallback(() => {
    const systems: Array<LogEntry['system']> = ['CMC', 'HHNI', 'VIF', 'SEG', 'APOE', 'TCS', 'CAS', 'SYSTEM']
    const levels: LogEntry['level'][] = ['info', 'warn', 'error', 'debug']
    const mockLogs: LogEntry[] = []
    
    for (let i = 0; i < 50; i++) {
      const system = systems[Math.floor(Math.random() * systems.length)]
      const level = levels[Math.floor(Math.random() * levels.length)]
      const timestamp = new Date(Date.now() - Math.random() * 3600000)
      
      mockLogs.push({
        id: `log_${i}`,
        timestamp,
        level,
        system,
        message: `[${system}] ${level.toUpperCase()}: Sample log message ${i}`,
        metadata: {
          operation: 'test',
          duration: Math.random() * 1000
        },
        evidenceIds: Math.random() > 0.7 ? [`evidence_${i}`] : undefined
      })
    }
    
    return mockLogs.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
  }, [])
  
  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      if (systemDropdownOpen && !target.closest('.system-dropdown')) {
        setSystemDropdownOpen(false)
      }
    }
    
    if (systemDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [systemDropdownOpen])
  
  // Load system statuses
  useEffect(() => {
    const loadSystemStatuses = async () => {
      try {
        const cmcStats = await getStats()
        const casMetrics = await getMetrics()
        const timelineSummary = await getSummary(10)
        
        const statuses: SystemStatus[] = [
          {
            system: 'CMC',
            status: cmcStats?.error_rate < 0.01 ? 'healthy' : 'degraded',
            metrics: cmcStats || {},
            lastUpdate: new Date(),
            errorCount: Math.floor(Math.random() * 5),
            warningCount: Math.floor(Math.random() * 10)
          },
          {
            system: 'HHNI',
            status: 'healthy',
            metrics: { query_count: 1234, avg_latency: 45 },
            lastUpdate: new Date(),
            errorCount: 0,
            warningCount: 2
          },
          {
            system: 'VIF',
            status: 'healthy',
            metrics: { witness_count: 567, avg_confidence: 0.87 },
            lastUpdate: new Date(),
            errorCount: 1,
            warningCount: 3
          },
          {
            system: 'SEG',
            status: contradictions.length > 10 ? 'degraded' : 'healthy',
            metrics: { entities: entities.length, contradictions: contradictions.length },
            lastUpdate: new Date(),
            errorCount: contradictions.length > 20 ? 5 : 0,
            warningCount: contradictions.length
          },
          {
            system: 'APOE',
            status: 'healthy',
            metrics: { plan_count: 12, execution_count: 45 },
            lastUpdate: new Date(),
            errorCount: 0,
            warningCount: 1
          },
          {
            system: 'TCS',
            status: 'healthy',
            metrics: { entries: timelineSummary.length },
            lastUpdate: new Date(),
            errorCount: 0,
            warningCount: 0
          },
          {
            system: 'CAS',
            status: (casMetrics as any)?.attention_focus > 0.7 ? 'healthy' : 'degraded',
            metrics: casMetrics || {},
            lastUpdate: new Date(),
            errorCount: 0,
            warningCount: 2
          }
        ]
        
        setSystemStatuses(statuses)
        setLogs(generateMockLogs())
      } catch (err) {
        console.error('Failed to load debug data:', err)
      }
    }
    
    loadSystemStatuses()
    
    // Simulate real-time log updates
    if (!isPaused) {
      const interval = setInterval(() => {
        const newLog: LogEntry = {
          id: `log_${Date.now()}`,
          timestamp: new Date(),
          level: Math.random() > 0.8 ? 'error' : Math.random() > 0.6 ? 'warn' : 'info',
          system: ['CMC', 'HHNI', 'VIF', 'SEG', 'APOE', 'TCS', 'CAS', 'SYSTEM'][Math.floor(Math.random() * 8)] as LogEntry['system'],
          message: `[${Date.now()}] Real-time log update`,
          metadata: { realtime: true }
        }
        setLogs(prev => [newLog, ...prev].slice(0, 200)) // Keep last 200 logs
      }, 2000)
      
      return () => clearInterval(interval)
    }
  }, [getStats, getMetrics, getSummary, entities.length, contradictions.length, generateMockLogs, isPaused])
  
  // Filter logs
  const filteredLogs = useMemo(() => {
    let filtered = logs
    
    if (selectedSystem) {
      filtered = filtered.filter(log => log.system === selectedSystem)
    }
    
    if (logLevelFilter.size < 4) {
      filtered = filtered.filter(log => logLevelFilter.has(log.level))
    }
    
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(log => 
        log.message.toLowerCase().includes(query) ||
        log.system.toLowerCase().includes(query)
      )
    }
    
    return filtered
  }, [logs, selectedSystem, logLevelFilter, searchQuery])
  
  // Get selected log
  const selectedLog = useMemo(() => {
    if (!selectedLogId) return null
    return filteredLogs.find(log => log.id === selectedLogId) || null
  }, [selectedLogId, filteredLogs])
  
  // Auto-select latest log if none selected or selected log is filtered out
  useEffect(() => {
    if (filteredLogs.length > 0) {
      const selectedLogExists = selectedLogId && filteredLogs.some(log => log.id === selectedLogId)
      if (!selectedLogExists) {
        setSelectedLogId(filteredLogs[0].id)
      }
    }
  }, [filteredLogs, selectedLogId])
  
  // Calculate AIM-OS metrics
  const totalErrors = systemStatuses.reduce((sum, s) => sum + s.errorCount, 0)
  const totalWarnings = systemStatuses.reduce((sum, s) => sum + s.warningCount, 0)
  
  // Update status for bottom bar display
  useEffect(() => {
    if (onStatusChange) {
      const statusText = `${filteredLogs.length} logs • ${totalErrors} errors • ${totalWarnings} warnings • ${systemStatuses.filter(s => s.status === 'healthy').length}/${systemStatuses.length} systems healthy`
      onStatusChange(statusText)
    }
    return () => {
      if (onStatusChange) {
        onStatusChange(null)
      }
    }
  }, [filteredLogs.length, totalErrors, totalWarnings, systemStatuses, onStatusChange])
  
  const getLevelColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'error': return 'text-red-400 bg-red-900/30 border-red-700'
      case 'warn': return 'text-yellow-400 bg-yellow-900/30 border-yellow-700'
      case 'info': return 'text-blue-400 bg-blue-900/30 border-blue-700'
      case 'debug': return 'text-gray-400 bg-gray-900/30 border-gray-700'
    }
  }
  
  const getStatusColor = (status: SystemStatus['status']) => {
    switch (status) {
      case 'healthy': return 'text-green-400'
      case 'degraded': return 'text-yellow-400'
      case 'error': return 'text-red-400'
    }
  }
  
  return (
    <div className="h-full flex flex-col bg-gray-950">
      {/* Two-Column Layout: Header/Log List | Details */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Column: Header Controls + Log List */}
        <div className="flex-1 min-w-0 border-r border-gray-700 flex flex-col overflow-hidden">
          {/* Header Controls - Compact */}
          <div className="p-2 border-b border-gray-700 space-y-2 flex-shrink-0">
            {/* Title */}
            <div className="flex items-center gap-2">
              <Bug className="w-4 h-4 text-gray-400" />
              <h3 className="text-xs font-semibold text-gray-300">Debug Console</h3>
            </div>
            
            {/* All Filters on One Row */}
            <div className="flex items-center gap-2 flex-wrap">
              {/* Log Level Filters */}
              {(['info', 'warn', 'error', 'debug'] as const).map(level => (
                <button
                  key={level}
                  onClick={() => {
                    const newFilter = new Set(logLevelFilter)
                    if (newFilter.has(level)) {
                      newFilter.delete(level)
                    } else {
                      newFilter.add(level)
                    }
                    setLogLevelFilter(newFilter)
                  }}
                  className={`px-2 py-0.5 rounded text-xs ${
                    logLevelFilter.has(level)
                      ? getLevelColor(level)
                      : 'bg-gray-700 text-gray-500'
                  }`}
                >
                  {level.toUpperCase()}
                </button>
              ))}
              
              {/* System Filter Dropdown */}
              <div className="relative system-dropdown">
                <button
                  onClick={() => setSystemDropdownOpen(!systemDropdownOpen)}
                  className={`px-2 py-0.5 rounded text-xs flex items-center gap-1 ${
                    selectedSystem
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  <Filter className="w-3 h-3" />
                  {selectedSystem ? selectedSystem : 'All Systems'}
                  <ChevronDown className={`w-3 h-3 transition-transform ${systemDropdownOpen ? 'rotate-180' : ''}`} />
                </button>
                
                {systemDropdownOpen && (
                  <div className="absolute top-full left-0 mt-1 bg-gray-800 border border-gray-700 rounded shadow-lg z-10 min-w-[150px]">
                    <button
                      onClick={() => {
                        setSelectedSystem(null)
                        setSystemDropdownOpen(false)
                      }}
                      className={`w-full text-left px-3 py-1.5 text-xs hover:bg-gray-700 ${
                        !selectedSystem ? 'bg-blue-600/20 text-blue-400' : 'text-gray-300'
                      }`}
                    >
                      All Systems
                    </button>
                    {systemStatuses.map(status => (
                      <button
                        key={status.system}
                        onClick={() => {
                          setSelectedSystem(selectedSystem === status.system ? null : status.system)
                          setSystemDropdownOpen(false)
                        }}
                        className={`w-full text-left px-3 py-1.5 text-xs hover:bg-gray-700 flex items-center justify-between ${
                          selectedSystem === status.system ? 'bg-blue-600/20 text-blue-400' : 'text-gray-300'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <Activity className={`w-3 h-3 ${getStatusColor(status.status)}`} />
                          <span>{status.system}</span>
                        </div>
                        {status.errorCount > 0 && (
                          <span className="text-red-400 text-[10px]">({status.errorCount})</span>
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
            
            {/* Controls Row */}
            <div className="flex items-center gap-2">
              {/* Search Bar */}
              <div className="flex-1 flex items-center gap-2 bg-gray-800 rounded px-2 py-1">
                <Search className="w-3 h-3 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search logs..."
                  className="flex-1 bg-transparent text-gray-300 placeholder-gray-500 text-xs outline-none"
                />
              </div>
              
              {/* Play/Pause */}
              <button
                onClick={() => setIsPaused(!isPaused)}
                className={`px-2 py-1 rounded text-xs flex items-center gap-1 ${
                  isPaused ? 'bg-yellow-600 text-white' : 'bg-green-600 text-white'
                }`}
              >
                {isPaused ? <Play className="w-3 h-3" /> : <Pause className="w-3 h-3" />}
              </button>
              
              {/* Clear */}
              <button
                onClick={() => setLogs([])}
                className="px-2 py-1 rounded text-xs bg-gray-700 text-gray-300 hover:bg-gray-600 flex items-center gap-1"
                title="Clear"
              >
                <Trash2 className="w-3 h-3" />
              </button>
              
              {/* Refresh */}
              <button
                onClick={() => window.location.reload()}
                className="px-2 py-1 rounded text-xs bg-gray-700 text-gray-300 hover:bg-gray-600 flex items-center gap-1"
                title="Refresh"
              >
                <RefreshCw className="w-3 h-3" />
              </button>
            </div>
          </div>
          
          {/* Scrollable Log List */}
          <div className="flex-1 overflow-auto">
            <div className="p-2 space-y-1">
              {filteredLogs.length === 0 ? (
                <div className="text-center text-gray-500 py-8 text-xs">
                  No logs match the current filters
                </div>
              ) : (
                filteredLogs.map(log => (
                  <button
                    key={log.id}
                    onClick={() => setSelectedLogId(log.id)}
                    className={`w-full text-left p-2 rounded text-xs transition-colors ${
                      selectedLogId === log.id
                        ? 'bg-blue-600 text-white'
                        : `hover:bg-gray-700/50 ${
                            log.level === 'error' ? 'bg-red-900/20 border-l-2 border-red-500' :
                            log.level === 'warn' ? 'bg-yellow-900/20 border-l-2 border-yellow-500' :
                            'bg-gray-800/50'
                          }`
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`px-1 py-0.5 rounded text-[10px] font-semibold ${
                        selectedLogId === log.id 
                          ? 'bg-white/20 text-white'
                          : getLevelColor(log.level)
                      }`}>
                        {log.level.toUpperCase()}
                      </span>
                      <span className={`text-[10px] font-mono ${
                        selectedLogId === log.id ? 'text-white/80' : 'text-gray-500'
                      }`}>
                        {log.timestamp.toLocaleTimeString()}
                      </span>
                      <span className={`text-[10px] px-1 py-0.5 rounded ${
                        selectedLogId === log.id 
                          ? 'bg-white/20 text-white'
                          : 'bg-gray-700 text-gray-400'
                      }`}>
                        {log.system}
                      </span>
                    </div>
                    <div className={`text-xs line-clamp-2 ${
                      selectedLogId === log.id ? 'text-white' : 'text-gray-300'
                    }`}>
                      {log.message}
                    </div>
                    {log.evidenceIds && log.evidenceIds.length > 0 && (
                      <div className={`mt-1 text-[10px] ${
                        selectedLogId === log.id ? 'text-white/70' : 'text-purple-400'
                      }`}>
                        🔗 {log.evidenceIds.length} evidence
                      </div>
                    )}
                  </button>
                ))
              )}
            </div>
          </div>
        </div>
        
        {/* Right Column: Log Details - Full Height */}
        <div className="flex-1 min-w-0 overflow-auto p-4">
          {selectedLog ? (
            <div className="space-y-4">
              {/* Header */}
              <div className="border-b border-gray-700 pb-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${getLevelColor(selectedLog.level)}`}>
                    {selectedLog.level.toUpperCase()}
                  </span>
                  <span className="text-xs text-gray-400 font-mono">
                    {selectedLog.timestamp.toLocaleString()}
                  </span>
                  <span className="text-xs px-2 py-1 rounded bg-gray-700 text-gray-300">
                    {selectedLog.system}
                  </span>
                </div>
                <h3 className="text-sm font-semibold text-gray-200">{selectedLog.message}</h3>
              </div>
              
              {/* Metadata */}
              {selectedLog.metadata && Object.keys(selectedLog.metadata).length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-400 mb-2">Metadata</h4>
                  <pre className="text-xs bg-gray-800 rounded p-3 overflow-auto border border-gray-700">
                    {JSON.stringify(selectedLog.metadata, null, 2)}
                  </pre>
                </div>
              )}
              
              {/* Evidence IDs */}
              {selectedLog.evidenceIds && selectedLog.evidenceIds.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-gray-400 mb-2">
                    Evidence IDs ({selectedLog.evidenceIds.length})
                  </h4>
                  <div className="space-y-1">
                    {selectedLog.evidenceIds.map((id, idx) => (
                      <div key={idx} className="text-xs font-mono text-purple-400 bg-gray-800 rounded px-2 py-1 border border-gray-700">
                        {id}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* System Status (if available) */}
              {(() => {
                const status = systemStatuses.find(s => s.system === selectedLog.system)
                if (!status) return null
                
                return (
                  <div>
                    <h4 className="text-xs font-semibold text-gray-400 mb-2">System Status</h4>
                    <div className="bg-gray-800 rounded p-3 border border-gray-700">
                      <div className="grid grid-cols-2 gap-2 text-xs mb-2">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Status:</span>
                          <span className={getStatusColor(status.status)}>
                            {status.status.toUpperCase()}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Errors:</span>
                          <span className="text-red-400">{status.errorCount}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Warnings:</span>
                          <span className="text-yellow-400">{status.warningCount}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Last Update:</span>
                          <span className="text-gray-300">
                            {status.lastUpdate.toLocaleTimeString()}
                          </span>
                        </div>
                      </div>
                      {Object.keys(status.metrics).length > 0 && (
                        <div className="mt-2 pt-2 border-t border-gray-700">
                          <div className="text-xs text-gray-400 mb-1">Metrics:</div>
                          <pre className="text-xs text-gray-300 overflow-auto">
                            {JSON.stringify(status.metrics, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                )
              })()}
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              <p className="text-sm">No log selected</p>
              <p className="text-xs mt-2">Select a log from the list to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
