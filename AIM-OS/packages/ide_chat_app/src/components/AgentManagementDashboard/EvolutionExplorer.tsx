/**
 * Evolution Explorer Component
 * Dual-Panel view for Timeline ↔ Chain Bidirectional Graph
 * 
 * Features:
 * - Synchronized selection between Timeline and Chains
 * - Bidirectional navigation (Timeline → Chain, Chain → Timeline)
 * - Visual connection lines
 * - Node-level drill-down
 * - Evolution path visualization
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { Calendar, Link, ArrowRight, ArrowLeft, Zap, RefreshCw, Filter, Search, Eye, ChevronRight } from 'lucide-react'
import { getServiceBridge } from '../../services/serviceBridge'
import { getMCPAPI } from '../../services/mcpApi'

interface TimelineEntry {
  id: string
  prompt_id: string
  timestamp: string
  user_input: string
  summary: string
  executed_via_chain_id?: string
  chain_execution_id?: string
  chain_node_id?: string
  context_state?: any
}

interface ChainInfo {
  id: string
  chain_id?: string
  atom_id?: string
  name: string
  description?: string
  timeline_entry_ids?: string[]
  execution_count?: number
  nodes?: any[]
  edges?: any[]
}

interface EvolutionExplorerProps {
  onSelectTimelineEntry?: (entry: TimelineEntry) => void
  onSelectChain?: (chain: ChainInfo) => void
}

export const EvolutionExplorer: React.FC<EvolutionExplorerProps> = ({
  onSelectTimelineEntry,
  onSelectChain
}) => {
  const [timelineEntries, setTimelineEntries] = useState<TimelineEntry[]>([])
  const [chains, setChains] = useState<ChainInfo[]>([])
  const [selectedTimelineEntry, setSelectedTimelineEntry] = useState<string | null>(null)
  const [selectedChain, setSelectedChain] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [timelineSearch, setTimelineSearch] = useState('')
  const [chainSearch, setChainSearch] = useState('')
  const [showChainConnections, setShowChainConnections] = useState(true)

  // Load timeline entries
  const loadTimelineEntries = useCallback(async () => {
    try {
      setLoading(true)
      // Use MCP get_timeline_entries tool
      const mcpApi = getMCPAPI()
      
      const result = await mcpApi.executeTool('get_timeline_entries', {
        limit: 100
      })
      
      if (result.success && result.result) {
        // MCP server returns: {success: true, entries: [...], message: "..."}
        // Extension wraps it: {success: true, tool: 'get_timeline_entries', result: {success: true, entries: [...], message: "..."}}
        let parsedResult = result.result
        if (typeof parsedResult === 'string') {
          try {
            parsedResult = JSON.parse(parsedResult)
          } catch (e) {
            console.error('[EvolutionExplorer] Failed to parse result as JSON:', e)
            return
          }
        }
        
        // Handle nested result structure
        if (parsedResult.result && parsedResult.result.entries) {
          parsedResult = parsedResult.result
        }
        
        const entries = parsedResult.entries || []
        setTimelineEntries(entries.map((entry: any) => ({
          id: entry.prompt_id || entry.id,
          prompt_id: entry.prompt_id || entry.id,
          timestamp: entry.timestamp || entry.context_snapshot?.timestamp || new Date().toISOString(),
          user_input: entry.user_input || '',
          summary: entry.summary || entry.user_input || '',
          executed_via_chain_id: entry.executed_via_chain_id || entry.context_state?.chain_id || entry.context_state?.executed_via_chain_id,
          chain_execution_id: entry.chain_execution_id || entry.context_state?.chain_execution_id,
          chain_node_id: entry.chain_node_id || entry.context_state?.chain_node_id,
          context_state: entry.context_state
        })))
      }
    } catch (error) {
      console.error('Failed to load timeline entries:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  // Load chains
  const loadChains = useCallback(async () => {
    try {
      const serviceBridge = getServiceBridge()
      const result = await serviceBridge.listPromptChains({}, 100)
      if (result.success && result.chains) {
        setChains(result.chains.map((chain: any) => ({
          id: chain.chain_id || chain.atom_id,
          chain_id: chain.chain_id,
          atom_id: chain.atom_id,
          name: chain.name || 'Unnamed Chain',
          description: chain.description || '',
          timeline_entry_ids: chain.metadata?.timeline_entry_ids || [],
          execution_count: chain.metadata?.execution_count || 0,
          nodes: chain.nodes || [],
          edges: chain.edges || []
        })))
      }
    } catch (error) {
      console.error('Failed to load chains:', error)
    }
  }, [])

  useEffect(() => {
    loadTimelineEntries()
    loadChains()
    
    // Poll for updates
    const interval = setInterval(() => {
      loadTimelineEntries()
      loadChains()
    }, 10000) // Poll every 10 seconds
    
    return () => clearInterval(interval)
  }, [loadTimelineEntries, loadChains])

  // Handle timeline entry selection
  const handleTimelineSelect = useCallback((entry: TimelineEntry) => {
    setSelectedTimelineEntry(entry.id)
    setSelectedChain(null) // Clear chain selection
    
    // If entry has chain connection, highlight it
    if (entry.executed_via_chain_id) {
      const chain = chains.find(c => c.id === entry.executed_via_chain_id)
      if (chain) {
        // Don't auto-select, but highlight
      }
    }
    
    onSelectTimelineEntry?.(entry)
  }, [chains, onSelectTimelineEntry])

  // Handle chain selection
  const handleChainSelect = useCallback((chain: ChainInfo) => {
    setSelectedChain(chain.id)
    setSelectedTimelineEntry(null) // Clear timeline selection
    
    // Highlight timeline entries produced by this chain
    if (chain.timeline_entry_ids && chain.timeline_entry_ids.length > 0) {
      // Timeline entries will be highlighted via CSS
    }
    
    onSelectChain?.(chain)
  }, [onSelectChain])

  // Filter timeline entries
  const filteredTimelineEntries = useMemo(() => {
    let filtered = timelineEntries
    
    if (timelineSearch) {
      const searchLower = timelineSearch.toLowerCase()
      filtered = filtered.filter(entry =>
        entry.user_input.toLowerCase().includes(searchLower) ||
        entry.summary.toLowerCase().includes(searchLower) ||
        entry.executed_via_chain_id?.toLowerCase().includes(searchLower)
      )
    }
    
    // Filter by selected chain if showing connections
    if (showChainConnections && selectedChain) {
      filtered = filtered.filter(entry =>
        entry.executed_via_chain_id === selectedChain
      )
    }
    
    return filtered.sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    )
  }, [timelineEntries, timelineSearch, showChainConnections, selectedChain])

  // Filter chains
  const filteredChains = useMemo(() => {
    let filtered = chains
    
    if (chainSearch) {
      const searchLower = chainSearch.toLowerCase()
      filtered = filtered.filter(chain =>
        chain.name.toLowerCase().includes(searchLower) ||
        chain.description?.toLowerCase().includes(searchLower)
      )
    }
    
    // Filter by selected timeline entry if showing connections
    if (showChainConnections && selectedTimelineEntry) {
      const entry = timelineEntries.find(e => e.id === selectedTimelineEntry)
      if (entry?.executed_via_chain_id) {
        filtered = filtered.filter(chain => chain.id === entry.executed_via_chain_id)
      }
    }
    
    return filtered.sort((a, b) => 
      (b.execution_count || 0) - (a.execution_count || 0)
    )
  }, [chains, chainSearch, showChainConnections, selectedTimelineEntry, timelineEntries])

  // Get connected chains for a timeline entry
  const getConnectedChains = useCallback((entry: TimelineEntry) => {
    if (!entry.executed_via_chain_id) return []
    return chains.filter(c => c.id === entry.executed_via_chain_id)
  }, [chains])

  // Get connected timeline entries for a chain
  const getConnectedTimelineEntries = useCallback((chain: ChainInfo) => {
    if (!chain.timeline_entry_ids || chain.timeline_entry_ids.length === 0) {
      // Fallback: find entries by chain_id
      return timelineEntries.filter(e => e.executed_via_chain_id === chain.id)
    }
    return timelineEntries.filter(e => 
      chain.timeline_entry_ids?.includes(e.id) || e.executed_via_chain_id === chain.id
    )
  }, [timelineEntries])

  return (
    <div className="h-full flex flex-col bg-cursor-bg text-cursor-text">
      {/* Header */}
      <div className="p-2 border-b border-cursor-border">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-cursor-status-bar" />
            <h2 className="text-sm font-semibold" style={{ fontSize: '13px' }}>Evolution Explorer</h2>
          </div>
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setShowChainConnections(!showChainConnections)}
              className={`px-2 py-1 rounded text-xs cursor-button ${
                showChainConnections
                  ? 'bg-cursor-status-bar text-white'
                  : 'bg-cursor-hover text-cursor-text-secondary'
              }`}
              style={{ fontSize: '11px' }}
            >
              {showChainConnections ? 'Hide' : 'Show'} Connections
            </button>
            <button
              onClick={() => {
                loadTimelineEntries()
                loadChains()
              }}
              className="p-1 bg-cursor-hover hover:bg-cursor-active rounded cursor-button"
              title="Refresh"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Dual Panel Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Timeline Panel (Left) */}
        <div className="flex-1 flex flex-col border-r border-cursor-border overflow-hidden">
          <div className="p-2 border-b border-cursor-border">
            <div className="flex items-center gap-1.5 mb-1.5">
              <Calendar className="w-3.5 h-3.5 text-cursor-text-secondary" />
              <span className="text-xs font-semibold" style={{ fontSize: '12px' }}>Timeline Entries</span>
              <span className="text-xs text-cursor-text-muted" style={{ fontSize: '10px' }}>
                ({filteredTimelineEntries.length})
              </span>
            </div>
            <div className="relative">
              <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-cursor-text-muted" />
              <input
                type="text"
                placeholder="Search timeline entries..."
                value={timelineSearch}
                onChange={(e) => setTimelineSearch(e.target.value)}
                className="w-full bg-cursor-input-bg text-cursor-text px-7 py-1 rounded border border-cursor-border focus:outline-none focus:border-cursor-status-bar cursor-input"
                style={{ fontSize: '11px' }}
              />
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-2 cursor-scrollbar">
            {loading && timelineEntries.length === 0 && (
              <div className="flex items-center justify-center p-4">
                <RefreshCw className="w-5 h-5 animate-spin text-cursor-text-secondary" />
              </div>
            )}
            
            {filteredTimelineEntries.length === 0 && !loading && (
              <div className="flex flex-col items-center justify-center p-8 text-center">
                <Calendar className="w-12 h-12 text-cursor-text-secondary mb-2 opacity-50" />
                <p className="text-sm text-cursor-text-secondary">No timeline entries found</p>
              </div>
            )}
            
            <div className="space-y-2">
              {filteredTimelineEntries.map((entry) => {
                const isSelected = selectedTimelineEntry === entry.id
                const connectedChains = getConnectedChains(entry)
                const hasChainConnection = entry.executed_via_chain_id !== undefined
                
                return (
                  <div
                    key={entry.id}
                    onClick={() => handleTimelineSelect(entry)}
                    className={`bg-cursor-sidebar rounded p-2 border transition-all cursor-pointer cursor-list-item ${
                      isSelected
                        ? 'border-cursor-status-bar bg-cursor-status-bar/10'
                        : 'border-cursor-border hover:border-cursor-status-bar/50'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-1">
                      <div className="flex-1">
                        <div className="flex items-center gap-1.5 mb-0.5">
                          <span className="text-xs font-semibold text-cursor-text" style={{ fontSize: '12px' }}>
                            {entry.summary || entry.user_input.substring(0, 50)}
                          </span>
                          {hasChainConnection && (
                            <span className="px-1.5 py-0.5 text-[10px] rounded bg-green-900/30 text-green-300">
                              🔗 Chain
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-cursor-text-secondary" style={{ fontSize: '11px' }}>
                          {entry.user_input.substring(0, 100)}
                          {entry.user_input.length > 100 ? '...' : ''}
                        </p>
                      </div>
                    </div>
                    
                    {/* Chain Connection Info */}
                    {hasChainConnection && connectedChains.length > 0 && (
                      <div className="mt-1.5 pt-1.5 border-t border-cursor-border">
                        <div className="flex items-center gap-1 text-xs text-cursor-text-secondary" style={{ fontSize: '10px' }}>
                          <ArrowRight className="w-3 h-3" />
                          <span>Executed via:</span>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleChainSelect(connectedChains[0])
                            }}
                            className="text-cursor-status-bar hover:underline font-medium"
                          >
                            {connectedChains[0].name}
                          </button>
                          {entry.chain_node_id && (
                            <>
                              <span>•</span>
                              <span className="text-cursor-text-muted">Node: {entry.chain_node_id.substring(0, 8)}...</span>
                            </>
                          )}
                        </div>
                      </div>
                    )}
                    
                    {/* Metadata */}
                    <div className="flex items-center gap-2 mt-1.5 text-xs text-cursor-text-muted" style={{ fontSize: '10px' }}>
                      <span>{new Date(entry.timestamp).toLocaleTimeString()}</span>
                      {entry.chain_execution_id && (
                        <>
                          <span>•</span>
                          <span>Exec: {entry.chain_execution_id.substring(0, 8)}...</span>
                        </>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>

        {/* Chain Panel (Right) */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="p-2 border-b border-cursor-border">
            <div className="flex items-center gap-1.5 mb-1.5">
              <Link className="w-3.5 h-3.5 text-cursor-text-secondary" />
              <span className="text-xs font-semibold" style={{ fontSize: '12px' }}>Prompt Chains</span>
              <span className="text-xs text-cursor-text-muted" style={{ fontSize: '10px' }}>
                ({filteredChains.length})
              </span>
            </div>
            <div className="relative">
              <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-cursor-text-muted" />
              <input
                type="text"
                placeholder="Search chains..."
                value={chainSearch}
                onChange={(e) => setChainSearch(e.target.value)}
                className="w-full bg-cursor-input-bg text-cursor-text px-7 py-1 rounded border border-cursor-border focus:outline-none focus:border-cursor-status-bar cursor-input"
                style={{ fontSize: '11px' }}
              />
            </div>
          </div>
          
          <div className="flex-1 overflow-y-auto p-2 cursor-scrollbar">
            {loading && chains.length === 0 && (
              <div className="flex items-center justify-center p-4">
                <RefreshCw className="w-5 h-5 animate-spin text-cursor-text-secondary" />
              </div>
            )}
            
            {filteredChains.length === 0 && !loading && (
              <div className="flex flex-col items-center justify-center p-8 text-center">
                <Link className="w-12 h-12 text-cursor-text-secondary mb-2 opacity-50" />
                <p className="text-sm text-cursor-text-secondary">No chains found</p>
              </div>
            )}
            
            <div className="space-y-2">
              {filteredChains.map((chain) => {
                const isSelected = selectedChain === chain.id
                const connectedEntries = getConnectedTimelineEntries(chain)
                const hasTimelineConnections = connectedEntries.length > 0
                
                return (
                  <div
                    key={chain.id}
                    onClick={() => handleChainSelect(chain)}
                    className={`bg-cursor-sidebar rounded p-2 border transition-all cursor-pointer cursor-list-item ${
                      isSelected
                        ? 'border-cursor-status-bar bg-cursor-status-bar/10'
                        : 'border-cursor-border hover:border-cursor-status-bar/50'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-1">
                      <div className="flex-1">
                        <div className="flex items-center gap-1.5 mb-0.5">
                          <span className="text-xs font-semibold text-cursor-text" style={{ fontSize: '12px' }}>
                            {chain.name}
                          </span>
                          {hasTimelineConnections && (
                            <span className="px-1.5 py-0.5 text-[10px] rounded bg-blue-900/30 text-blue-300">
                              📅 {connectedEntries.length} entries
                            </span>
                          )}
                        </div>
                        {chain.description && (
                          <p className="text-xs text-cursor-text-secondary" style={{ fontSize: '11px' }}>
                            {chain.description.substring(0, 100)}
                            {chain.description.length > 100 ? '...' : ''}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    {/* Timeline Connection Info */}
                    {hasTimelineConnections && (
                      <div className="mt-1.5 pt-1.5 border-t border-cursor-border">
                        <div className="flex items-center gap-1 text-xs text-cursor-text-secondary mb-1" style={{ fontSize: '10px' }}>
                          <ArrowLeft className="w-3 h-3" />
                          <span>Produced {connectedEntries.length} timeline entr{connectedEntries.length === 1 ? 'y' : 'ies'}</span>
                        </div>
                        <div className="space-y-1">
                          {connectedEntries.slice(0, 3).map((entry) => (
                            <button
                              key={entry.id}
                              onClick={(e) => {
                                e.stopPropagation()
                                handleTimelineSelect(entry)
                              }}
                              className="w-full text-left px-1.5 py-0.5 rounded bg-cursor-input-bg hover:bg-cursor-hover text-xs text-cursor-text-secondary transition-colors flex items-center gap-1"
                              style={{ fontSize: '10px' }}
                            >
                              <ChevronRight className="w-2.5 h-2.5" />
                              <span className="truncate">{entry.summary || entry.user_input.substring(0, 40)}</span>
                            </button>
                          ))}
                          {connectedEntries.length > 3 && (
                            <div className="text-xs text-cursor-text-muted px-1.5" style={{ fontSize: '9px' }}>
                              +{connectedEntries.length - 3} more
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                    
                    {/* Metadata */}
                    <div className="flex items-center gap-2 mt-1.5 text-xs text-cursor-text-muted" style={{ fontSize: '10px' }}>
                      <span>{chain.nodes?.length || 0} nodes</span>
                      <span>•</span>
                      <span>{chain.execution_count || 0} executions</span>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

