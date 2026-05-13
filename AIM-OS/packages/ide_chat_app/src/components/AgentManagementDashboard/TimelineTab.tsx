/**
 * Timeline Tab Component
 * Tab 5: Timeline and calendar system
 * Enhanced with Evolution Explorer for Timeline ↔ Chain bidirectional graph
 * 
 * Created: 2025-10-31
 * Enhanced: 2025-11-02 (Added Evolution Explorer)
 * Agent: Aether
 */

import React, { useState, useEffect } from 'react'
import { Calendar, Clock, Brain, Activity, Zap, Code, RefreshCw, Filter, GitBranch } from 'lucide-react'
import AIMOSService from '../../services/AIMOSService'
import { EvolutionExplorer } from './EvolutionExplorer'

const aimosService = new AIMOSService()

interface TimelineEntry {
  id: string
  timestamp: Date
  type: 'ai_interaction' | 'memory_stored' | 'confidence_tracked' | 'agent_action' | 'system_event'
  content: string
  agentId?: string
  confidence?: number
  context?: any
  // NEW: Chain Connection Fields
  executed_via_chain_id?: string
  chain_execution_id?: string
  chain_node_id?: string
}

const TimelineTab: React.FC = () => {
  const [viewMode, setViewMode] = useState<'timeline' | 'evolution'>('timeline')
  const [entries, setEntries] = useState<TimelineEntry[]>([
    {
      id: '1',
      timestamp: new Date(Date.now() - 30000),
      type: 'ai_interaction',
      content: 'User asked about IDE features',
      agentId: 'aether'
    },
    {
      id: '2',
      timestamp: new Date(Date.now() - 60000),
      type: 'memory_stored',
      content: 'Stored IDE session context',
      agentId: 'lexicon'
    },
    {
      id: '3',
      timestamp: new Date(Date.now() - 120000),
      type: 'confidence_tracked',
      content: 'Tracked confidence: 0.85',
      agentId: 'solo',
      confidence: 0.85
    },
    {
      id: '4',
      timestamp: new Date(Date.now() - 180000),
      type: 'agent_action',
      content: 'Lexicon completed Agent Management Dashboard',
      agentId: 'lexicon'
    },
    {
      id: '5',
      timestamp: new Date(Date.now() - 240000),
      type: 'system_event',
      content: 'MCP tools connection established',
      agentId: undefined
    }
  ])

  const [filterType, setFilterType] = useState<string>('all')
  const [filterAgent, setFilterAgent] = useState<string>('all')

  // Load initial timeline entries
  useEffect(() => {
    const loadEntries = async () => {
      try {
        const fetchedEntries = await aimosService.getTimelineEntries(50)
        if (fetchedEntries.length > 0) {
          setEntries(fetchedEntries)
        }
      } catch (error) {
        console.error('Failed to load timeline entries:', error)
        // Keep mock data on error
      }
    }
    
    loadEntries()
    const interval = setInterval(loadEntries, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const filteredEntries = entries.filter(entry => {
    if (filterType !== 'all' && entry.type !== filterType) return false
    if (filterAgent !== 'all' && entry.agentId !== filterAgent) return false
    return true
  })

  const getIcon = (type: string) => {
    switch (type) {
      case 'ai_interaction': return <Brain className="w-4 h-4 text-blue-400" />
      case 'memory_stored': return <Activity className="w-4 h-4 text-purple-400" />
      case 'confidence_tracked': return <Zap className="w-4 h-4 text-yellow-400" />
      case 'agent_action': return <Code className="w-4 h-4 text-green-400" />
      case 'system_event': return <Activity className="w-4 h-4 text-gray-400" />
      default: return <Clock className="w-4 h-4 text-gray-400" />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'ai_interaction': return 'bg-blue-900/30 text-blue-300 border-blue-700'
      case 'memory_stored': return 'bg-purple-900/30 text-purple-300 border-purple-700'
      case 'confidence_tracked': return 'bg-yellow-900/30 text-yellow-300 border-yellow-700'
      case 'agent_action': return 'bg-green-900/30 text-green-300 border-green-700'
      case 'system_event': return 'bg-gray-900/30 text-gray-300 border-gray-700'
      default: return 'bg-gray-900/30 text-gray-300 border-gray-700'
    }
  }

  const formatTime = (date: Date) => {
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)

    if (seconds < 60) return `${seconds}s ago`
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }

  return (
    <div className="h-full flex flex-col bg-cursor-bg text-cursor-text">
      {/* View Mode Toggle */}
      <div className="p-2 border-b border-cursor-border">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-cursor-status-bar" />
            <div>
              <h1 className="text-base font-semibold" style={{ fontSize: '15px' }}>Timeline</h1>
              <p className="text-xs text-cursor-text-secondary">Activity timeline and evolution explorer</p>
            </div>
          </div>
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setViewMode('timeline')}
              className={`px-2 py-1 rounded text-xs cursor-button transition-colors ${
                viewMode === 'timeline'
                  ? 'bg-cursor-status-bar text-white'
                  : 'bg-cursor-hover text-cursor-text-secondary hover:bg-cursor-active'
              }`}
              style={{ fontSize: '11px' }}
            >
              <Calendar className="w-3.5 h-3.5 inline mr-1" />
              Timeline
            </button>
            <button
              onClick={() => setViewMode('evolution')}
              className={`px-2 py-1 rounded text-xs cursor-button transition-colors ${
                viewMode === 'evolution'
                  ? 'bg-cursor-status-bar text-white'
                  : 'bg-cursor-hover text-cursor-text-secondary hover:bg-cursor-active'
              }`}
              style={{ fontSize: '11px' }}
            >
              <GitBranch className="w-3.5 h-3.5 inline mr-1" />
              Evolution
            </button>
          </div>
        </div>
      </div>

      {/* Render Evolution Explorer or Timeline View */}
      {viewMode === 'evolution' ? (
        <EvolutionExplorer
          onSelectTimelineEntry={(entry) => {
            console.log('Timeline entry selected:', entry)
            // Could navigate to detailed view or show in drawer
          }}
          onSelectChain={(chain) => {
            console.log('Chain selected:', chain)
            // Could navigate to chain editor or show in drawer
          }}
        />
      ) : (
        <>
          {/* Original Timeline View */}
          {/* Filters */}
          <div className="p-2 border-b border-cursor-border">
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5">
                <Filter className="w-3.5 h-3.5 text-cursor-text-secondary" />
                <span className="text-xs text-cursor-text-secondary">Type:</span>
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="bg-cursor-input-bg text-cursor-text px-2 py-1 rounded text-xs border border-cursor-border cursor-input"
                  style={{ fontSize: '12px' }}
                >
                  <option value="all">All</option>
                  <option value="ai_interaction">AI Interaction</option>
                  <option value="memory_stored">Memory Stored</option>
                  <option value="confidence_tracked">Confidence Tracked</option>
                  <option value="agent_action">Agent Action</option>
                  <option value="system_event">System Event</option>
                </select>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-xs text-cursor-text-secondary">Agent:</span>
                <select
                  value={filterAgent}
                  onChange={(e) => setFilterAgent(e.target.value)}
                  className="bg-cursor-input-bg text-cursor-text px-2 py-1 rounded text-xs border border-cursor-border cursor-input"
                  style={{ fontSize: '12px' }}
                >
                  <option value="all">All</option>
                  <option value="aether">Aether</option>
                  <option value="lexicon">Lexicon</option>
                  <option value="solo">Solo</option>
                  <option value="atlas">Atlas</option>
                </select>
              </div>
              <div className="ml-auto text-xs text-cursor-text-secondary">
                {filteredEntries.length} entries
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div className="flex-1 overflow-y-auto p-2 cursor-scrollbar">
            <div className="relative">
              {/* Timeline line */}
              <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-cursor-border" />

              {/* Entries */}
              <div className="space-y-2">
                {filteredEntries.map((entry, index) => (
                  <div key={entry.id} className="relative flex items-start gap-2">
                    {/* Icon */}
                    <div className="relative z-10 flex items-center justify-center w-4 h-4 rounded-full bg-cursor-sidebar border-2 border-cursor-border">
                      {getIcon(entry.type)}
                    </div>

                    {/* Content */}
                    <div className="flex-1 pt-0">
                      <div className="bg-cursor-sidebar rounded p-2 border border-cursor-border hover:border-cursor-border/80 transition-colors cursor-list-item">
                        <div className="flex items-start justify-between mb-1">
                          <div className="flex items-center gap-1.5">
                            <span className={`px-1.5 py-0.5 text-xs rounded border ${getTypeColor(entry.type)}`} style={{ fontSize: '10px' }}>
                              {entry.type.replace('_', ' ')}
                            </span>
                            {entry.agentId && (
                              <span className="text-xs text-cursor-text-secondary">Agent: {entry.agentId}</span>
                            )}
                            {entry.confidence !== undefined && (
                              <span className={`text-xs px-1.5 py-0.5 rounded ${
                                entry.confidence >= 0.90 ? 'bg-green-900/30 text-green-300' :
                                entry.confidence >= 0.70 ? 'bg-yellow-900/30 text-yellow-300' :
                                'bg-red-900/30 text-red-300'
                              }`} style={{ fontSize: '10px' }}>
                                {(entry.confidence * 100).toFixed(0)}% confidence
                              </span>
                            )}
                          </div>
                          <span className="text-xs text-cursor-text-secondary">{formatTime(entry.timestamp)}</span>
                        </div>
                        <p className="text-xs text-cursor-text" style={{ fontSize: '12px', lineHeight: '1.4' }}>{entry.content}</p>
                        {entry.context && (
                          <div className="mt-1 text-xs text-cursor-text-secondary font-mono bg-cursor-bg p-1.5 rounded" style={{ fontSize: '10px' }}>
                            {JSON.stringify(entry.context, null, 2).slice(0, 200)}
                            {JSON.stringify(entry.context, null, 2).length > 200 && '...'}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default TimelineTab
