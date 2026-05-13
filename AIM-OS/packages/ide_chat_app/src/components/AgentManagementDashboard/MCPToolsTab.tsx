/**
 * MCP Tools Tab Component
 * Tab 4: MCP tools activity and orchestration
 * 
 * Created: 2025-10-31
 * Agent: Aether
 */

import React, { useState, useEffect } from 'react'
import { Wrench, Zap, Activity, Clock, CheckCircle, XCircle, AlertCircle, RefreshCw } from 'lucide-react'
import AIMOSService from '../../services/AIMOSService'

const aimosService = new AIMOSService()

interface MCPToolCall {
  id: string
  toolName: string
  category: string
  agentId?: string
  timestamp: Date
  status: 'success' | 'error' | 'pending'
  duration?: number
  result?: any
  error?: string
}

export const MCPToolsTab: React.FC = () => {
  const [toolCalls, setToolCalls] = useState<MCPToolCall[]>([
    {
      id: 'call-1',
      toolName: 'store_memory',
      category: 'CMC',
      agentId: 'aether',
      timestamp: new Date(Date.now() - 120000),
      status: 'success',
      duration: 45,
      result: { atom_id: 'atom-123', success: true }
    },
    {
      id: 'call-2',
      toolName: 'track_confidence',
      category: 'VIF',
      agentId: 'lexicon',
      timestamp: new Date(Date.now() - 90000),
      status: 'success',
      duration: 32,
      result: { success: true, witness_id: 'wit-456' }
    },
    {
      id: 'call-3',
      toolName: 'retrieve_memory',
      category: 'HHNI',
      agentId: 'solo',
      timestamp: new Date(Date.now() - 60000),
      status: 'success',
      duration: 128,
      result: { memories: [{ atom_id: 'atom-123', content: '...' }] }
    },
    {
      id: 'call-4',
      toolName: 'create_plan',
      category: 'APOE',
      agentId: 'atlas',
      timestamp: new Date(Date.now() - 30000),
      status: 'pending',
      duration: undefined
    }
  ])

  const [filterCategory, setFilterCategory] = useState<string>('all')
  const [filterStatus, setFilterStatus] = useState<string>('all')

  // Load initial tool calls
  useEffect(() => {
    const loadToolCalls = async () => {
      try {
        const fetchedCalls = await aimosService.getMCPToolCalls(50)
        if (fetchedCalls.length > 0) {
          setToolCalls(fetchedCalls)
        }
      } catch (error) {
        console.error('Failed to load MCP tool calls:', error)
        // Keep mock data on error
      }
    }
    
    loadToolCalls()
    const interval = setInterval(loadToolCalls, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const categories = ['all', 'CMC', 'HHNI', 'VIF', 'APOE', 'SEG', 'SDF-CVF', 'CAS']
  const statuses = ['all', 'success', 'error', 'pending']

  const filteredCalls = toolCalls.filter(call => {
    if (filterCategory !== 'all' && call.category !== filterCategory) return false
    if (filterStatus !== 'all' && call.status !== filterStatus) return false
    return true
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'error': return <XCircle className="w-4 h-4 text-red-400" />
      case 'pending': return <Clock className="w-4 h-4 text-yellow-400 animate-pulse" />
      default: return <AlertCircle className="w-4 h-4 text-gray-400" />
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'CMC': return 'bg-blue-900/30 text-blue-300 border-blue-700'
      case 'HHNI': return 'bg-purple-900/30 text-purple-300 border-purple-700'
      case 'VIF': return 'bg-green-900/30 text-green-300 border-green-700'
      case 'APOE': return 'bg-yellow-900/30 text-yellow-300 border-yellow-700'
      case 'SEG': return 'bg-cyan-900/30 text-cyan-300 border-cyan-700'
      case 'SDF-CVF': return 'bg-orange-900/30 text-orange-300 border-orange-700'
      case 'CAS': return 'bg-pink-900/30 text-pink-300 border-pink-700'
      default: return 'bg-gray-900/30 text-gray-300 border-gray-700'
    }
  }

  return (
    <div className="h-full flex flex-col bg-cursor-bg text-cursor-text">
      {/* Header */}
      <div className="p-2 border-b border-cursor-border">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Wrench className="w-5 h-5 text-cursor-status-bar" />
            <div>
              <h1 className="text-base font-semibold" style={{ fontSize: '15px' }}>MCP Tools</h1>
              <p className="text-xs text-cursor-text-secondary">Monitor MCP tools activity and orchestration</p>
            </div>
          </div>
          <button 
            onClick={() => {
              aimosService.getMCPToolCalls(50).then(setToolCalls).catch(console.error)
            }}
            className="p-1.5 bg-cursor-hover hover:bg-cursor-active rounded cursor-button"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5">
            <span className="text-xs text-cursor-text-secondary">Category:</span>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="bg-cursor-input-bg text-cursor-text px-2 py-1 rounded text-xs border border-cursor-border cursor-input"
              style={{ fontSize: '12px' }}
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-xs text-cursor-text-secondary">Status:</span>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-cursor-input-bg text-cursor-text px-2 py-1 rounded text-xs border border-cursor-border cursor-input"
              style={{ fontSize: '12px' }}
            >
              {statuses.map(status => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
          </div>
          <div className="ml-auto text-xs text-cursor-text-secondary">
            {filteredCalls.length} tool calls
          </div>
        </div>
      </div>

      {/* Tool Calls List */}
      <div className="flex-1 overflow-y-auto p-2 cursor-scrollbar">
        <div className="space-y-2">
          {filteredCalls.map((call) => (
            <div
              key={call.id}
              className="bg-cursor-sidebar rounded p-2 border border-cursor-border hover:border-cursor-border/80 transition-colors cursor-list-item"
            >
              <div className="flex items-start justify-between mb-1">
                <div className="flex items-center gap-2 flex-1">
                  {getStatusIcon(call.status)}
                  <div>
                    <div className="flex items-center gap-1.5 mb-0.5">
                      <span className="font-semibold text-xs" style={{ fontSize: '12px' }}>{call.toolName}</span>
                      <span className={`px-1.5 py-0.5 text-xs rounded border ${getCategoryColor(call.category)}`} style={{ fontSize: '10px' }}>
                        {call.category}
                      </span>
                    </div>
                    {call.agentId && (
                      <span className="text-xs text-cursor-text-secondary">Agent: {call.agentId}</span>
                    )}
                  </div>
                </div>
                <div className="text-xs text-cursor-text-secondary">
                  {Math.round((Date.now() - call.timestamp.getTime()) / 1000)}s ago
                </div>
              </div>

              {/* Result/Error */}
              {call.status === 'success' && call.result && (
                <div className="mt-1 p-1.5 bg-green-900/20 rounded border border-green-700/50">
                  <div className="text-xs text-green-300 font-mono" style={{ fontSize: '10px' }}>
                    {JSON.stringify(call.result, null, 2).slice(0, 200)}
                    {JSON.stringify(call.result, null, 2).length > 200 && '...'}
                  </div>
                </div>
              )}
              {call.status === 'error' && call.error && (
                <div className="mt-1 p-1.5 bg-red-900/20 rounded border border-red-700/50">
                  <div className="text-xs text-red-300" style={{ fontSize: '11px' }}>{call.error}</div>
                </div>
              )}
              {call.status === 'pending' && (
                <div className="mt-1 p-1.5 bg-yellow-900/20 rounded border border-yellow-700/50">
                  <div className="flex items-center gap-1.5 text-xs text-yellow-300" style={{ fontSize: '11px' }}>
                    <Activity className="w-3 h-3 animate-pulse" />
                    Processing...
                  </div>
                </div>
              )}

              {/* Duration */}
              {call.duration && (
                <div className="mt-1 text-xs text-cursor-text-secondary">
                  Duration: {call.duration}ms
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default MCPToolsTab

