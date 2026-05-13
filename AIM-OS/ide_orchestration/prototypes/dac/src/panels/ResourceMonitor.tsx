// Resource Monitor Panel - Comprehensive Diagnostics & Error Reporting
// Enhanced with error tracking, diagnostics, and one-click error reporting

import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { resourceTracker } from '../utils/resourceTracker'
import { errorTracker, PanelDiagnostics } from '../utils/errorTracker'
import { PANEL_REGISTRY, getAllPanelIds, getPanelName, getPanelDefinition } from '../utils/panelRegistry'
import { PanelPreview } from '../components/PanelPreview'
import { LayoutVisualization } from '../components/LayoutVisualization'
import { usePanelStore } from '../store/panelStore'
import {
  Activity,
  Database,
  MemoryStick,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle,
  X,
  Copy,
  Download,
  FileText,
  Search,
  Filter,
  RefreshCw,
  AlertTriangle,
  Bug,
  Zap,
  Network,
  Code,
  Eye,
  EyeOff,
  ChevronDown,
  ChevronRight,
  ExternalLink
} from 'lucide-react'
import { BasePanel } from '../components/BasePanel'

type ViewMode = 'overview' | 'errors' | 'performance' | 'network' | 'diagnostics'
type FilterType = 'all' | 'errors' | 'warnings' | 'healthy'

export const ResourceMonitor: React.FC = () => {
  const [panels, setPanels] = useState(resourceTracker.getAllPanels())
  const [memoryInfo, setMemoryInfo] = useState(resourceTracker.getBrowserMemoryInfo())
  const [diagnostics, setDiagnostics] = useState<PanelDiagnostics[]>(errorTracker.getAllDiagnostics())
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [viewMode, setViewMode] = useState<ViewMode>('overview')
  const [filter, setFilter] = useState<FilterType>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedPanels, setExpandedPanels] = useState<Set<string>>(new Set())
  const [selectedPanel, setSelectedPanel] = useState<string | null>(null)
  const [copySuccess, setCopySuccess] = useState<string | null>(null)
  
  // Get current layout configuration from store
  const { currentPanelConfiguration, mainView } = usePanelStore()
  
  useEffect(() => {
    const updateData = () => {
      setPanels(resourceTracker.getAllPanels())
      setMemoryInfo(resourceTracker.getBrowserMemoryInfo())
      
      // Ensure all panels from registry have diagnostics entries
      const allPanelIds = getAllPanelIds()
      allPanelIds.forEach(panelId => {
        const panelDef = getPanelDefinition(panelId)
        if (panelDef) {
          errorTracker.getOrCreateDiagnostics(panelId, panelDef.name)
        }
      })
      
      setDiagnostics(errorTracker.getAllDiagnostics())
    }
    
    updateData()
    
    // Subscribe to error events
    const unsubscribe = errorTracker.subscribe((panelId, error) => {
      updateData()
    })
    
    if (autoRefresh) {
      const interval = setInterval(updateData, 1000)
      return () => {
        clearInterval(interval)
        unsubscribe()
      }
    }
    
    return unsubscribe
  }, [autoRefresh])
  
  // Create comprehensive panel list combining registry and tracked panels
  const comprehensivePanels = useMemo(() => {
    const trackedPanels = new Map(panels.map(p => [p.id, p]))
    const diagnosticsMap = new Map(diagnostics.map(d => [d.panelId, d]))
    
    // Start with all panels from registry
    return PANEL_REGISTRY.map(panelDef => {
      const tracked = trackedPanels.get(panelDef.id)
      const diag = diagnosticsMap.get(panelDef.id) || errorTracker.getOrCreateDiagnostics(panelDef.id, panelDef.name)
      
      return {
        id: panelDef.id,
        name: panelDef.name,
        category: panelDef.category,
        // Use tracked data if available, otherwise use defaults
        status: tracked?.status || (diag.errors.length > 0 ? 'error' : 'unloaded'),
        mountCount: tracked?.mountCount || diag.mountCount || 0,
        renderCount: tracked?.renderCount || diag.renderCount || 0,
        estimatedMemoryMB: tracked?.estimatedMemoryMB || panelDef.estimatedMemoryMB || 5,
        loadTime: tracked?.loadTime || diag.loadTime,
        lastMounted: tracked?.lastMounted,
        lastUnmounted: tracked?.lastUnmounted,
        // Diagnostics data
        diagnostics: diag,
        hasErrors: diag.errors.length > 0,
        errorCount: diag.errors.length,
        unresolvedErrorCount: diag.errors.filter(e => !e.resolved).length
      }
    })
  }, [panels, diagnostics])
  
  const togglePanelExpansion = useCallback((panelId: string) => {
    setExpandedPanels(prev => {
      const next = new Set(prev)
      if (next.has(panelId)) {
        next.delete(panelId)
      } else {
        next.add(panelId)
      }
      return next
    })
  }, [])
  
  const handleCopyDiagnostics = useCallback(async (panelId?: string) => {
    try {
      const report = errorTracker.generateDiagnosticsReport(panelId)
      await navigator.clipboard.writeText(report)
      setCopySuccess(panelId || 'all')
      setTimeout(() => setCopySuccess(null), 2000)
    } catch (err) {
      console.error('Failed to copy diagnostics:', err)
    }
  }, [])
  
  const handleCopyMarkdown = useCallback(async (panelId?: string) => {
    try {
      const report = errorTracker.generateMarkdownReport(panelId)
      await navigator.clipboard.writeText(report)
      setCopySuccess(`${panelId || 'all'}-md`)
      setTimeout(() => setCopySuccess(null), 2000)
    } catch (err) {
      console.error('Failed to copy markdown:', err)
    }
  }, [])
  
  const handleDownloadDiagnostics = useCallback((panelId?: string) => {
    const report = errorTracker.generateDiagnosticsReport(panelId)
    const blob = new Blob([report], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `diagnostics-${panelId || 'all'}-${Date.now()}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }, [])
  
  // Filter to loaded panels (mounted or cached) - these are what we focus on
  const loadedPanels = useMemo(() => {
    return comprehensivePanels.filter(p => p.status === 'mounted' || p.status === 'cached')
  }, [comprehensivePanels])
  
  // Filter loaded panels based on search/filter
  const filteredLoadedPanels = useMemo(() => {
    return loadedPanels.filter(d => {
      if (filter === 'errors' && !d.hasErrors) return false
      if (filter === 'warnings' && d.diagnostics.status !== 'warning') return false
      if (filter === 'healthy' && (d.hasErrors || d.diagnostics.status === 'error')) return false
      if (searchQuery && !d.name.toLowerCase().includes(searchQuery.toLowerCase()) && 
          !d.id.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false
      }
      return true
    })
  }, [loadedPanels, filter, searchQuery])
  
  // Get selected panel details
  const selectedPanelData = useMemo(() => {
    if (!selectedPanel) return null
    return comprehensivePanels.find(p => p.id === selectedPanel)
  }, [selectedPanel, comprehensivePanels])
  
  const totalErrors = comprehensivePanels.reduce((sum, d) => sum + d.errorCount, 0)
  const unresolvedErrors = comprehensivePanels.reduce((sum, d) => sum + d.unresolvedErrorCount, 0)
  const panelsWithErrors = comprehensivePanels.filter(d => d.hasErrors).length
  
  const mountedPanels = comprehensivePanels.filter(p => p.status === 'mounted')
  const cachedPanels = comprehensivePanels.filter(p => p.status === 'cached')
  const totalEstimatedMemory = comprehensivePanels
    .filter(p => p.status === 'mounted' || p.status === 'cached')
    .reduce((sum, p) => sum + p.estimatedMemoryMB, 0)
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'mounted': return 'text-green-400'
      case 'cached': return 'text-yellow-400'
      case 'loading': return 'text-blue-400'
      case 'unmounted': return 'text-gray-500'
      case 'error': return 'text-red-400'
      case 'warning': return 'text-yellow-400'
      case 'healthy': return 'text-green-400'
      default: return 'text-gray-400'
    }
  }
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'mounted':
      case 'healthy': return <CheckCircle className="w-3 h-3" />
      case 'cached': return <Clock className="w-3 h-3" />
      case 'loading': return <Activity className="w-3 h-3 animate-spin" />
      case 'error': return <AlertCircle className="w-3 h-3" />
      case 'warning': return <AlertTriangle className="w-3 h-3" />
      default: return <X className="w-3 h-3" />
    }
  }
  
  const formatMemory = (mb: number) => {
    if (mb < 1) return `${(mb * 1024).toFixed(0)} KB`
    return `${mb.toFixed(1)} MB`
  }
  
  const formatTime = (date?: Date) => {
    if (!date) return 'Never'
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000)
    if (seconds < 60) return `${seconds}s ago`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`
    return `${Math.floor(seconds / 3600)}h ago`
  }
  
  const formatDuration = (ms?: number) => {
    if (!ms) return 'N/A'
    if (ms < 1000) return `${ms.toFixed(0)}ms`
    return `${(ms / 1000).toFixed(2)}s`
  }
  
  return (
    <BasePanel title="Panel Diagnostics & Resource Monitor" icon={MemoryStick}>
      <div className="h-full flex flex-col">
        {/* Header with View Modes and Actions */}
        <div className="p-3 border-b border-gray-700 space-y-2">
          {/* View Mode Tabs */}
          <div className="flex items-center gap-1 bg-gray-800 rounded p-1">
            {(['overview', 'errors', 'performance', 'network', 'diagnostics'] as ViewMode[]).map(mode => (
              <button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors capitalize ${
                  viewMode === mode
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-gray-700'
                }`}
              >
                {mode}
              </button>
            ))}
          </div>
          
          {/* Quick Actions */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-3 h-3 text-gray-500" />
                <input
                  type="text"
                  placeholder="Search panels..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-7 pr-2 py-1 bg-gray-800 border border-gray-700 rounded text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />
              </div>
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value as FilterType)}
                className="px-2 py-1 bg-gray-800 border border-gray-700 rounded text-xs text-gray-200 focus:outline-none focus:border-blue-500"
              >
                <option value="all">All</option>
                <option value="errors">Errors</option>
                <option value="warnings">Warnings</option>
                <option value="healthy">Healthy</option>
              </select>
            </div>
            
            <div className="flex items-center gap-2">
              <button
                onClick={() => handleCopyDiagnostics()}
                className="px-2 py-1 bg-gray-800 hover:bg-gray-700 rounded text-xs text-gray-300 flex items-center gap-1 transition-colors"
                title="Copy all diagnostics (JSON)"
              >
                <Copy className="w-3 h-3" />
                {copySuccess === 'all' && <span className="text-green-400">Copied!</span>}
              </button>
              <button
                onClick={() => handleCopyMarkdown()}
                className="px-2 py-1 bg-gray-800 hover:bg-gray-700 rounded text-xs text-gray-300 flex items-center gap-1 transition-colors"
                title="Copy markdown report"
              >
                <FileText className="w-3 h-3" />
                {copySuccess === 'all-md' && <span className="text-green-400">Copied!</span>}
              </button>
              <button
                onClick={() => handleDownloadDiagnostics()}
                className="px-2 py-1 bg-gray-800 hover:bg-gray-700 rounded text-xs text-gray-300 flex items-center gap-1 transition-colors"
                title="Download diagnostics JSON"
              >
                <Download className="w-3 h-3" />
              </button>
              <label className="text-xs text-gray-400 flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="w-3 h-3 rounded"
                />
                Auto-refresh
              </label>
            </div>
          </div>
        </div>
        
        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-4">
          {viewMode === 'overview' && (
            <div className="space-y-4">
              {/* Summary Cards */}
              <div className="grid grid-cols-4 gap-3">
                <div className="bg-gray-800 rounded p-3">
                  <div className="text-xs text-gray-400 mb-1">Loaded Panels</div>
                  <div className="text-lg font-semibold text-green-400">{loadedPanels.length}</div>
                  <div className="text-[10px] text-gray-500 mt-0.5">
                    {mountedPanels.length} mounted, {cachedPanels.length} cached
                  </div>
                </div>
                <div className="bg-gray-800 rounded p-3">
                  <div className="text-xs text-gray-400 mb-1">Total Panels</div>
                  <div className="text-lg font-semibold text-blue-400">{comprehensivePanels.length}</div>
                  <div className="text-[10px] text-gray-500 mt-0.5">
                    {comprehensivePanels.length - loadedPanels.length} unloaded
                  </div>
                </div>
                <div className="bg-gray-800 rounded p-3">
                  <div className="text-xs text-gray-400 mb-1">Est. Memory</div>
                  <div className="text-lg font-semibold text-blue-400">{formatMemory(totalEstimatedMemory)}</div>
                  <div className="text-[10px] text-gray-500 mt-0.5">
                    Loaded panels only
                  </div>
                </div>
                <div className={`rounded p-3 ${unresolvedErrors > 0 ? 'bg-red-900/30 border border-red-700' : 'bg-gray-800'}`}>
                  <div className="text-xs text-gray-400 mb-1">Unresolved Errors</div>
                  <div className={`text-lg font-semibold ${unresolvedErrors > 0 ? 'text-red-400' : 'text-green-400'}`}>
                    {unresolvedErrors}
                  </div>
                  <div className="text-[10px] text-gray-500 mt-0.5">
                    {panelsWithErrors} panel{panelsWithErrors !== 1 ? 's' : ''} affected
                  </div>
                </div>
              </div>
              
              {/* Browser Memory Info */}
              {memoryInfo.usedJSHeapSize && (
                <div className="bg-gray-800 rounded p-3">
                  <div className="text-xs text-gray-400 mb-2">Browser Memory (Chrome/Edge)</div>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-300">Used:</span>
                      <span className="text-blue-400">{formatMemory(memoryInfo.usedJSHeapSize)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Total:</span>
                      <span className="text-gray-400">{formatMemory(memoryInfo.totalJSHeapSize || 0)}</span>
                    </div>
                    {memoryInfo.jsHeapSizeLimit && (
                      <div className="flex justify-between">
                        <span className="text-gray-300">Limit:</span>
                        <span className="text-gray-500">{formatMemory(memoryInfo.jsHeapSizeLimit)}</span>
                      </div>
                    )}
                    {memoryInfo.jsHeapSizeLimit && memoryInfo.usedJSHeapSize && (
                      <div className="mt-2">
                        <div className="w-full bg-gray-700 rounded-full h-2">
                          <div
                            className="bg-blue-500 h-2 rounded-full transition-all"
                            style={{
                              width: `${(memoryInfo.usedJSHeapSize / memoryInfo.jsHeapSizeLimit) * 100}%`
                            }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              {/* Loaded Panels Grid - Mini UI Previews */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
                    Loaded Panels ({loadedPanels.length})
                  </div>
                  <div className="text-xs text-gray-500">
                    {filteredLoadedPanels.length} shown
                  </div>
                </div>
                
                {filteredLoadedPanels.length === 0 ? (
                  <div className="text-xs text-gray-500 p-8 text-center bg-gray-800 rounded border border-gray-700">
                    {loadedPanels.length === 0 
                      ? 'No panels are currently loaded. Open a panel to see it here.'
                      : 'No loaded panels match your filters'}
                  </div>
                ) : (
                  <div className="space-y-4">
                    {/* Layout Visualization */}
                    <div className="h-64 bg-gray-900 rounded-lg border border-gray-700">
                      <LayoutVisualization
                        loadedPanels={filteredLoadedPanels}
                        leftTopPanel={currentPanelConfiguration.leftTopPanel}
                        leftBottomPanel={currentPanelConfiguration.leftBottomPanel}
                        rightTopPanel={currentPanelConfiguration.rightTopPanel}
                        rightBottomPanel={currentPanelConfiguration.rightBottomPanel}
                        bottomLeftPanel={currentPanelConfiguration.bottomLeftPanel}
                        bottomRightPanel={currentPanelConfiguration.bottomRightPanel}
                        mainView={mainView}
                        leftPanelOpen={currentPanelConfiguration.leftPanelOpen}
                        rightPanelOpen={currentPanelConfiguration.rightPanelOpen}
                        bottomPanelOpen={currentPanelConfiguration.bottomPanelOpen}
                        onPanelClick={setSelectedPanel}
                        selectedPanel={selectedPanel}
                      />
                    </div>
                    
                    {/* Selected Panel Details */}
                    {selectedPanel && selectedPanelData && (
                      <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
                        <h3 className="text-sm font-semibold text-gray-200 mb-3">
                          {selectedPanelData.name} Details
                        </h3>
                        {/* Panel details will be shown below */}
                      </div>
                    )}
                  </div>
                )}
              </div>
              
              {/* Selected Panel Full Details */}
              {selectedPanelData && (
                <div className="bg-gray-800 rounded-lg border-2 border-blue-500/50 p-4 space-y-4">
                  <div className="flex items-center justify-between border-b border-gray-700 pb-3">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold text-gray-200">{selectedPanelData.name}</h3>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(selectedPanelData.status)}`}>
                        {selectedPanelData.status}
                      </span>
                      <span className={`px-2 py-1 rounded text-xs ${
                        selectedPanelData.category === 'left' ? 'bg-blue-900/30 text-blue-300' :
                        selectedPanelData.category === 'right' ? 'bg-purple-900/30 text-purple-300' :
                        selectedPanelData.category === 'bottom' ? 'bg-green-900/30 text-green-300' :
                        selectedPanelData.category === 'main' ? 'bg-yellow-900/30 text-yellow-300' :
                        'bg-gray-700/30 text-gray-300'
                      }`}>
                        {selectedPanelData.category}
                      </span>
                      {selectedPanelData.hasErrors && (
                        <span className="px-2 py-1 bg-red-900/50 text-red-300 rounded text-xs font-medium">
                          {selectedPanelData.errorCount} error{selectedPanelData.errorCount !== 1 ? 's' : ''}
                        </span>
                      )}
                    </div>
                    <button
                      onClick={() => setSelectedPanel(null)}
                      className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-gray-200 transition-colors"
                      title="Close details"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  
                  {/* Organized Details Sections */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Status & Performance */}
                    <div className="space-y-3">
                      <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wide flex items-center gap-2">
                        <Zap className="w-3 h-3" />
                        Status & Performance
                      </h4>
                      <div className="bg-gray-900 rounded p-3 space-y-2 text-xs">
                        <div className="grid grid-cols-2 gap-2">
                          <div className="flex justify-between">
                            <span className="text-gray-400">Panel ID:</span>
                            <span className="text-gray-200 font-mono text-[10px]">{selectedPanelData.id}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Status:</span>
                            <span className={getStatusColor(selectedPanelData.status)}>{selectedPanelData.status}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Mount Count:</span>
                            <span className="text-gray-200">{selectedPanelData.mountCount}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">Render Count:</span>
                            <span className="text-gray-200">{selectedPanelData.renderCount}</span>
                          </div>
                          {selectedPanelData.loadTime && (
                            <div className="flex justify-between">
                              <span className="text-gray-400">Load Time:</span>
                              <span className="text-gray-200">{formatDuration(selectedPanelData.loadTime)}</span>
                            </div>
                          )}
                          <div className="flex justify-between">
                            <span className="text-gray-400">Memory:</span>
                            <span className="text-gray-200">{formatMemory(selectedPanelData.estimatedMemoryMB)}</span>
                          </div>
                          {selectedPanelData.lastMounted && (
                            <div className="flex justify-between col-span-2">
                              <span className="text-gray-400">Last Mounted:</span>
                              <span className="text-gray-200">{formatTime(selectedPanelData.lastMounted)}</span>
                            </div>
                          )}
                        </div>
                        
                        {selectedPanelData.diagnostics.performanceMetrics && (
                          <div className="pt-2 border-t border-gray-800">
                            <div className="text-[10px] text-gray-500 mb-1 font-medium">Performance Metrics</div>
                            <div className="grid grid-cols-2 gap-2">
                              {selectedPanelData.diagnostics.performanceMetrics.averageRenderTime && (
                                <div className="flex justify-between">
                                  <span className="text-gray-400">Avg Render:</span>
                                  <span className="text-gray-200">{formatDuration(selectedPanelData.diagnostics.performanceMetrics.averageRenderTime)}</span>
                                </div>
                              )}
                              {selectedPanelData.diagnostics.performanceMetrics.slowestRender && (
                                <div className="flex justify-between">
                                  <span className="text-gray-400">Slowest:</span>
                                  <span className="text-yellow-400">{formatDuration(selectedPanelData.diagnostics.performanceMetrics.slowestRender)}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {/* Errors Section */}
                    {selectedPanelData.hasErrors ? (
                      <div className="space-y-3">
                        <h4 className="text-xs font-semibold text-red-400 uppercase tracking-wide flex items-center gap-2">
                          <Bug className="w-3 h-3" />
                          Errors ({selectedPanelData.errorCount})
                        </h4>
                        <div className="bg-gray-900 rounded p-3 space-y-2 max-h-64 overflow-y-auto">
                          {selectedPanelData.diagnostics.errors.map((error) => (
                            <div key={error.id} className="bg-gray-800 rounded p-2 border border-red-900/30">
                              <div className="flex items-start justify-between gap-2 mb-2">
                                <div className="flex-1 min-w-0">
                                  <div className="text-xs text-red-300 font-medium mb-1">{error.error.message}</div>
                                  <div className="text-[10px] text-gray-500">
                                    {formatTime(error.timestamp)} • {error.resolved ? '✅ Resolved' : '❌ Unresolved'}
                                  </div>
                                </div>
                                <button
                                  onClick={() => {
                                    const fullError = `Panel: ${error.panelName} (${error.panelId})\nError ID: ${error.id}\nTimestamp: ${error.timestamp.toISOString()}\n\nError Message:\n${error.error.message}\n\nStack Trace:\n${error.error.stack || 'N/A'}\n\nComponent Stack:\n${error.componentStack || 'N/A'}\n\nContext:\n${JSON.stringify(error.context || {}, null, 2)}`
                                    navigator.clipboard.writeText(fullError)
                                    setCopySuccess(error.id)
                                    setTimeout(() => setCopySuccess(null), 2000)
                                  }}
                                  className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-blue-400 transition-colors flex-shrink-0"
                                  title="Copy error details"
                                >
                                  <Copy className="w-3 h-3" />
                                </button>
                              </div>
                              {error.componentStack && (
                                <details className="mt-2">
                                  <summary className="text-[10px] text-gray-500 cursor-pointer hover:text-gray-400">
                                    Component Stack
                                  </summary>
                                  <pre className="text-[9px] text-gray-600 mt-1 overflow-auto max-h-20 whitespace-pre-wrap">
                                    {error.componentStack}
                                  </pre>
                                </details>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        <h4 className="text-xs font-semibold text-green-400 uppercase tracking-wide flex items-center gap-2">
                          <CheckCircle className="w-3 h-3" />
                          Status
                        </h4>
                        <div className="bg-gray-900 rounded p-3 text-xs text-green-400 flex items-center gap-2">
                          <CheckCircle className="w-4 h-4" />
                          <span>No errors detected. Panel is operating normally.</span>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {/* Network & Console Errors */}
                  {(selectedPanelData.diagnostics.networkRequests?.length || selectedPanelData.diagnostics.consoleErrors?.length) && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {selectedPanelData.diagnostics.networkRequests && selectedPanelData.diagnostics.networkRequests.length > 0 && (
                        <div className="space-y-2">
                          <h4 className="text-xs font-semibold text-purple-400 uppercase tracking-wide flex items-center gap-2">
                            <Network className="w-3 h-3" />
                            Network Requests ({selectedPanelData.diagnostics.networkRequests.length})
                          </h4>
                          <div className="bg-gray-900 rounded p-2 space-y-1 max-h-32 overflow-y-auto text-[10px]">
                            {selectedPanelData.diagnostics.networkRequests.slice(-10).map((req, idx) => (
                              <div key={idx} className="flex items-center justify-between text-gray-400">
                                <span className="truncate flex-1 min-w-0">{req.method} {req.url}</span>
                                <span className={`ml-2 flex-shrink-0 ${
                                  req.status && req.status >= 400 ? 'text-red-400' :
                                  req.status && req.status >= 300 ? 'text-yellow-400' :
                                  'text-green-400'
                                }`}>
                                  {req.status || '?'}
                                </span>
                                {req.duration && (
                                  <span className="text-gray-500 ml-2 flex-shrink-0">{formatDuration(req.duration)}</span>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {selectedPanelData.diagnostics.consoleErrors && selectedPanelData.diagnostics.consoleErrors.length > 0 && (
                        <div className="space-y-2">
                          <h4 className="text-xs font-semibold text-orange-400 uppercase tracking-wide flex items-center gap-2">
                            <AlertTriangle className="w-3 h-3" />
                            Console Errors ({selectedPanelData.diagnostics.consoleErrors.length})
                          </h4>
                          <div className="bg-gray-900 rounded p-2 space-y-1 max-h-32 overflow-y-auto text-[10px]">
                            {selectedPanelData.diagnostics.consoleErrors.slice(-10).map((err, idx) => (
                              <div key={idx} className="text-orange-300">
                                {err.message}
                                {err.source && (
                                  <span className="text-gray-500 ml-1">
                                    ({err.source}:{err.line}:{err.column})
                                  </span>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {/* Actions */}
                  <div className="flex items-center gap-2 pt-2 border-t border-gray-700">
                    <button
                      onClick={() => handleCopyDiagnostics(selectedPanelData.id)}
                      className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded text-xs text-white flex items-center gap-2 transition-colors"
                    >
                      <Copy className="w-3 h-3" />
                      Copy Full Diagnostics
                      {copySuccess === selectedPanelData.id && <span className="text-green-300">✓</span>}
                    </button>
                    <button
                      onClick={() => handleCopyMarkdown(selectedPanelData.id)}
                      className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-xs text-gray-200 flex items-center gap-2 transition-colors"
                    >
                      <FileText className="w-3 h-3" />
                      Copy Markdown
                    </button>
                    <button
                      onClick={() => handleDownloadDiagnostics(selectedPanelData.id)}
                      className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-xs text-gray-200 flex items-center gap-2 transition-colors"
                    >
                      <Download className="w-3 h-3" />
                      Download JSON
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
          
          {viewMode === 'errors' && (
            <div className="space-y-4">
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
                Panels with Errors ({panelsWithErrors})
              </div>
              {comprehensivePanels.filter(d => d.hasErrors).length === 0 ? (
                <div className="text-xs text-gray-500 p-8 text-center bg-gray-800 rounded border border-gray-700">
                  No errors detected! 🎉
                </div>
              ) : (
                <>
                  {/* Error Panel Previews */}
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                    {comprehensivePanels
                      .filter(d => d.hasErrors)
                      .map(panelData => (
                        <PanelPreview
                          key={panelData.id}
                          panelId={panelData.id}
                          panelName={panelData.name}
                          category={panelData.category}
                          status={panelData.status}
                          hasErrors={panelData.hasErrors}
                          errorCount={panelData.errorCount}
                          renderCount={panelData.renderCount}
                          mountCount={panelData.mountCount}
                          estimatedMemoryMB={panelData.estimatedMemoryMB}
                          loadTime={panelData.loadTime}
                          onClick={() => {
                            setSelectedPanel(selectedPanel === panelData.id ? null : panelData.id)
                          }}
                          isSelected={selectedPanel === panelData.id}
                        />
                      ))}
                  </div>
                  
                  {/* Selected Error Panel Details */}
                  {selectedPanelData && selectedPanelData.hasErrors && (
                    <div className="bg-gray-800 rounded-lg border-2 border-red-500/50 p-4 space-y-4 mt-4">
                      <div className="flex items-center justify-between border-b border-gray-700 pb-3">
                        <div className="flex items-center gap-3">
                          <h3 className="text-lg font-semibold text-gray-200">{selectedPanelData.name}</h3>
                          <span className="px-2 py-1 bg-red-900/50 text-red-300 rounded text-xs font-medium">
                            {selectedPanelData.errorCount} error{selectedPanelData.errorCount !== 1 ? 's' : ''}
                          </span>
                        </div>
                        <button
                          onClick={() => setSelectedPanel(null)}
                          className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-gray-200 transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                      
                      <div className="space-y-3">
                        {selectedPanelData.diagnostics.errors.map((error) => (
                          <div key={error.id} className="bg-gray-900 rounded p-3 border border-red-900/30">
                            <div className="flex items-start justify-between gap-2 mb-2">
                              <div className="flex-1 min-w-0">
                                <div className="text-sm text-red-300 font-medium mb-1">{error.error.message}</div>
                                <div className="text-xs text-gray-500">
                                  {formatTime(error.timestamp)} • {error.resolved ? '✅ Resolved' : '❌ Unresolved'}
                                </div>
                              </div>
                              <button
                                onClick={() => {
                                  const fullError = `Panel: ${error.panelName} (${error.panelId})\nError ID: ${error.id}\nTimestamp: ${error.timestamp.toISOString()}\n\nError Message:\n${error.error.message}\n\nStack Trace:\n${error.error.stack || 'N/A'}\n\nComponent Stack:\n${error.componentStack || 'N/A'}\n\nContext:\n${JSON.stringify(error.context || {}, null, 2)}`
                                  navigator.clipboard.writeText(fullError)
                                  setCopySuccess(error.id)
                                  setTimeout(() => setCopySuccess(null), 2000)
                                }}
                                className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-blue-400 transition-colors flex-shrink-0"
                                title="Copy full error details"
                              >
                                <Copy className="w-4 h-4" />
                              </button>
                            </div>
                            {error.error.stack && (
                              <details className="mt-2">
                                <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-400">
                                  Stack Trace
                                </summary>
                                <pre className="text-xs text-gray-600 mt-1 overflow-auto max-h-40 whitespace-pre-wrap">
                                  {error.error.stack}
                                </pre>
                              </details>
                            )}
                            {error.componentStack && (
                              <details className="mt-2">
                                <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-400">
                                  Component Stack
                                </summary>
                                <pre className="text-xs text-gray-600 mt-1 overflow-auto max-h-40 whitespace-pre-wrap">
                                  {error.componentStack}
                                </pre>
                              </details>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
          
          {viewMode === 'performance' && (
            <div className="space-y-2">
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">
                Performance Metrics
              </div>
              {comprehensivePanels
                .filter(d => d.diagnostics.performanceMetrics || d.loadTime || d.renderCount > 0)
                .map(panelData => {
                  const diag = panelData.diagnostics
                  return (
                  <div key={panelData.id} className="bg-gray-800 rounded p-3">
                    <div className="font-medium text-gray-200 mb-2">{panelData.name}</div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Status:</span>
                        <span className={getStatusColor(panelData.status)}>{panelData.status}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Mount Count:</span>
                        <span className="text-gray-200">{panelData.mountCount}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Render Count:</span>
                        <span className="text-gray-200">{panelData.renderCount}</span>
                      </div>
                      {panelData.loadTime && (
                        <div className="flex justify-between">
                          <span className="text-gray-400">Load Time:</span>
                          <span className="text-gray-200">{formatDuration(panelData.loadTime)}</span>
                        </div>
                      )}
                      {diag.performanceMetrics?.averageRenderTime && (
                        <div className="flex justify-between">
                          <span className="text-gray-400">Avg Render:</span>
                          <span className="text-gray-200">{formatDuration(diag.performanceMetrics.averageRenderTime)}</span>
                        </div>
                      )}
                      {diag.performanceMetrics?.slowestRender && (
                        <div className="flex justify-between">
                          <span className="text-gray-400">Slowest Render:</span>
                          <span className="text-yellow-400">{formatDuration(diag.performanceMetrics.slowestRender)}</span>
                        </div>
                      )}
                      {panelData.lastMounted && (
                        <div className="flex justify-between">
                          <span className="text-gray-400">Last Mounted:</span>
                          <span className="text-gray-200">{formatTime(panelData.lastMounted)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  )
                })}
            </div>
          )}
          
          {viewMode === 'diagnostics' && (
            <div className="space-y-4">
              <div className="bg-blue-900/20 border border-blue-800 rounded p-3 text-xs text-blue-300">
                <div className="font-semibold mb-2">Comprehensive Diagnostics Report</div>
                <div className="space-y-1 text-blue-200/80">
                  <p>This view provides complete diagnostic information for all {PANEL_REGISTRY.length} panels in the IDE, including errors, performance metrics, network requests, and console errors.</p>
                  <p className="mt-2">Use the copy buttons to export diagnostics in JSON or Markdown format for sharing with developers or debugging.</p>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleCopyDiagnostics()}
                  className="px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm text-white flex items-center gap-2"
                >
                  <Copy className="w-4 h-4" />
                  Copy Full Diagnostics (JSON)
                  {copySuccess === 'all' && <span className="text-green-300 ml-2">✓ Copied!</span>}
                </button>
                <button
                  onClick={() => handleCopyMarkdown()}
                  className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-200 flex items-center gap-2"
                >
                  <FileText className="w-4 h-4" />
                  Copy Markdown Report
                  {copySuccess === 'all-md' && <span className="text-green-300 ml-2">✓ Copied!</span>}
                </button>
                <button
                  onClick={() => handleDownloadDiagnostics()}
                  className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-200 flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Download JSON
                </button>
              </div>
              
              <div className="bg-gray-800 rounded p-3">
                <div className="text-xs font-semibold text-gray-400 mb-2">Report Summary</div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total Panels:</span>
                    <span className="text-gray-200">{comprehensivePanels.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Panels with Errors:</span>
                    <span className="text-red-400">{panelsWithErrors}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total Errors:</span>
                    <span className="text-gray-200">{totalErrors}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Unresolved Errors:</span>
                    <span className="text-red-400">{unresolvedErrors}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Mounted Panels:</span>
                    <span className="text-green-400">{mountedPanels.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Unloaded Panels:</span>
                    <span className="text-gray-400">{comprehensivePanels.filter(p => p.status === 'unloaded').length}</span>
                  </div>
                </div>
          </div>
        </div>
          )}
        </div>
      </div>
    </BasePanel>
  )
}
