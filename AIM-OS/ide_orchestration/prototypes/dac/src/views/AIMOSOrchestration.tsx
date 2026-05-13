// AIM-OS Orchestration View - V2 Refactored with BasePanel
// System visualization and orchestration dashboard with real AIM-OS integration

import React, { useState, useEffect } from 'react'
import { BasePanel } from '../components/BasePanel'
import { useCAS, useAPOE } from '../hooks/useAIMOS'
import { Network, Database, Shield, Brain, Target, Activity, CheckCircle, XCircle, AlertTriangle, RefreshCw } from 'lucide-react'

interface SystemStatus {
  id: string
  name: string
  fullName: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  color: string
  status: 'healthy' | 'degraded' | 'offline' | 'warning'
  metrics: {
    [key: string]: any
  }
  connections: string[]  // IDs of connected systems
  lastUpdate: string
}

export const AIMOSOrchestration: React.FC = () => {
  const { getMetrics } = useCAS()
  const { createPlan, executePlan } = useAPOE()
  const [systems, setSystems] = useState<SystemStatus[]>([])
  const [selectedSystem, setSelectedSystem] = useState<string | null>(null)
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    const loadSystemStatus = async () => {
      try {
        setLoading(true)
        setError(null)
        const casMetrics = await getMetrics()
      
      // Build comprehensive system status from CAS metrics and APOE
      const systemStatuses: SystemStatus[] = [
        {
          id: 'cmc',
          name: 'CMC',
          fullName: 'Context Memory Core',
          description: 'Bitemporal storage system for all AIM-OS data',
          icon: Database,
          color: 'blue',
          status: casMetrics.quality_level === 'excellent' || casMetrics.quality_level === 'good' ? 'healthy' : 
                  casMetrics.quality_level === 'fair' ? 'warning' : 'degraded',
          metrics: {
            atoms_count: 0,  // Would come from CMC stats
            storage_size: '0 MB',
            bitemporal_enabled: true,
            valid_time_tracking: true
          },
          connections: ['hhni', 'vif', 'seg', 'tcs'],
          lastUpdate: casMetrics.timestamp
        },
        {
          id: 'hhni',
          name: 'HHNI',
          fullName: 'Hierarchical Hypergraph Neural Index',
          description: 'Semantic search and hierarchical navigation system',
          icon: Network,
          color: 'purple',
          status: casMetrics.quality_level === 'excellent' || casMetrics.quality_level === 'good' ? 'healthy' : 
                  casMetrics.quality_level === 'fair' ? 'warning' : 'degraded',
          metrics: {
            indexed_nodes: 0,  // Would come from HHNI stats
            search_latency_ms: 45,
            semantic_search_enabled: true,
            hierarchical_navigation: true
          },
          connections: ['cmc', 'seg', 'apoe'],
          lastUpdate: casMetrics.timestamp
        },
        {
          id: 'vif',
          name: 'VIF',
          fullName: 'Verifiable Intelligence Framework',
          description: 'Confidence tracking and quality gates',
          icon: Shield,
          color: 'green',
          status: casMetrics.confidence_drift < 0.1 ? 'healthy' : 
                  casMetrics.confidence_drift < 0.2 ? 'warning' : 'degraded',
          metrics: {
            tracked_predictions: 0,  // Would come from VIF stats
            ece_score: casMetrics.confidence_drift,
            kappa_gates_passed: 0,
            confidence_tracking: true
          },
          connections: ['cmc', 'seg', 'apoe', 'cas'],
          lastUpdate: casMetrics.timestamp
        },
        {
          id: 'seg',
          name: 'SEG',
          fullName: 'Synthesis & Evidence Graph',
          description: 'Evidence tracking and contradiction detection',
          icon: Brain,
          color: 'cyan',
          status: casMetrics.error_rate < 0.1 ? 'healthy' : 
                  casMetrics.error_rate < 0.2 ? 'warning' : 'degraded',
          metrics: {
            entities_count: 0,  // Would come from SEG stats
            relations_count: 0,
            contradictions_detected: 0,
            synthesis_enabled: true
          },
          connections: ['cmc', 'hhni', 'vif', 'apoe'],
          lastUpdate: casMetrics.timestamp
        },
        {
          id: 'apoe',
          name: 'APOE',
          fullName: 'AI-Powered Orchestration Engine',
          description: 'Task orchestration and dynamic planning',
          icon: Target,
          color: 'yellow',
          status: casMetrics.cognitive_load < 0.8 ? 'healthy' : 
                  casMetrics.cognitive_load < 0.9 ? 'warning' : 'degraded',
          metrics: {
            active_plans: 0,  // Would come from APOE stats
            tasks_executed: 0,
            orchestration_enabled: true,
            dynamic_planning: true
          },
          connections: ['cmc', 'hhni', 'vif', 'seg', 'cas', 'tcs'],
          lastUpdate: casMetrics.timestamp
        },
        {
          id: 'cas',
          name: 'CAS',
          fullName: 'Consciousness Analysis System',
          description: 'Real-time consciousness monitoring and analysis',
          icon: Activity,
          color: 'pink',
          status: casMetrics.quality_level === 'excellent' || casMetrics.quality_level === 'good' ? 'healthy' : 
                  casMetrics.quality_level === 'fair' ? 'warning' : 'degraded',
          metrics: {
            working_memory_items: casMetrics.working_memory_items,
            cognitive_load: casMetrics.cognitive_load,
            attention_state: casMetrics.current_state,
            quality_level: casMetrics.quality_level,
            drift_detected: casMetrics.confidence_drift >= 0.1
          },
          connections: ['cmc', 'vif', 'apoe'],
          lastUpdate: casMetrics.timestamp
        },
        {
          id: 'tcs',
          name: 'TCS',
          fullName: 'Timeline Context System',
          description: 'Bitemporal timeline and sequential event tracking',
          icon: Activity,
          color: 'indigo',
          status: 'healthy',
          metrics: {
            timeline_entries: 0,  // Would come from TCS stats
            bitemporal_enabled: true,
            sequential_ordering: true,
            playback_enabled: true
          },
          connections: ['cmc', 'apoe'],
          lastUpdate: casMetrics.timestamp
        }
      ]
      
      setSystems(systemStatuses)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load system status')
      } finally {
        setLoading(false)
      }
    }
    
    loadSystemStatus()
    
    // Refresh every 5 seconds
    const interval = setInterval(loadSystemStatus, 5000)
    setRefreshInterval(interval)
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [getMetrics])
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="w-5 h-5 text-green-400" />
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-400" />
      case 'degraded':
        return <XCircle className="w-5 h-5 text-orange-400" />
      case 'offline':
        return <XCircle className="w-5 h-5 text-red-400" />
      default:
        return <Activity className="w-5 h-5 text-gray-400" />
    }
  }
  
  const getStatusColor = (status: string, color: string) => {
    const baseColors: Record<string, string> = {
      blue: 'bg-blue-900/30 border-blue-700 text-blue-400',
      purple: 'bg-purple-900/30 border-purple-700 text-purple-400',
      green: 'bg-green-900/30 border-green-700 text-green-400',
      cyan: 'bg-cyan-900/30 border-cyan-700 text-cyan-400',
      yellow: 'bg-yellow-900/30 border-yellow-700 text-yellow-400',
      pink: 'bg-pink-900/30 border-pink-700 text-pink-400',
      indigo: 'bg-indigo-900/30 border-indigo-700 text-indigo-400'
    }
    
    const statusBorders: Record<string, string> = {
      healthy: 'border-green-500',
      warning: 'border-yellow-500',
      degraded: 'border-orange-500',
      offline: 'border-red-500'
    }
    
    return `${baseColors[color]} ${statusBorders[status]}`
  }
  
  const selectedSystemData = systems.find(s => s.id === selectedSystem)
  
  // Calculate connection graph
  const connectionMap: Record<string, string[]> = {}
  systems.forEach(system => {
    connectionMap[system.id] = system.connections
  })
  
  // Calculate AIM-OS metrics
  const healthySystems = systems.filter(s => s.status === 'healthy').length
  const overallConfidence = systems.length > 0 
    ? healthySystems / systems.length
    : undefined
  
  const confidenceBand = overallConfidence 
    ? (overallConfidence >= 0.90 ? 'A' : overallConfidence >= 0.70 ? 'B' : 'C')
    : undefined
  
  return (
    <BasePanel
      id="panel-aimos-orchestration"
      title="AIM-OS Orchestration"
      icon={Network}
      description="Real-time system visualization and orchestration dashboard"
      loading={loading}
      error={error}
      empty={!loading && !error && systems.length === 0}
      emptyMessage="No system data available"
      confidence={overallConfidence}
      confidenceBand={confidenceBand}
      footerContent={
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>{systems.length} AIM-OS Systems • Updated every 5s</span>
          <span className="text-green-400">Orchestration Active</span>
        </div>
      }
      headerClassName="p-4"
    >
      <div className="p-4 border-b border-gray-700 flex items-center justify-end">
        <button
          onClick={() => {
            if (refreshInterval) clearInterval(refreshInterval)
            const interval = setInterval(async () => {
              try {
                const casMetrics = await getMetrics()
                // Trigger reload
              } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to refresh')
              }
            }, 5000)
            setRefreshInterval(interval)
          }}
          className="p-1 hover:bg-gray-700 rounded"
          title="Refresh"
        >
          <RefreshCw className="w-4 h-4 text-gray-400" />
        </button>
      </div>
      
      {/* Content */}
      <div className="flex-1 overflow-auto p-4">
        {/* System Grid */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          {systems.map((system) => {
            const Icon = system.icon
            
            return (
              <div
                key={system.id}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all hover:scale-105 ${
                  selectedSystem === system.id 
                    ? 'ring-2 ring-blue-500' 
                    : ''
                } ${getStatusColor(system.status, system.color)}`}
                onClick={() => setSelectedSystem(selectedSystem === system.id ? null : system.id)}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <Icon className="w-6 h-6" />
                    <div>
                      <div className="text-sm font-semibold">{system.name}</div>
                      <div className="text-xs opacity-75">{system.fullName}</div>
                    </div>
                  </div>
                  {getStatusIcon(system.status)}
                </div>
                
                <div className="text-xs opacity-75 mb-2">{system.description}</div>
                
                {/* Key Metrics */}
                <div className="mt-3 space-y-1">
                  {Object.entries(system.metrics).slice(0, 2).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-xs">
                      <span className="text-gray-400 capitalize">{key.replace('_', ' ')}:</span>
                      <span className="text-gray-300 font-mono">
                        {typeof value === 'boolean' ? (value ? '✓' : '✗') :
                         typeof value === 'number' && value < 1 ? value.toFixed(2) :
                         typeof value === 'number' ? value.toLocaleString() :
                         String(value)}
                      </span>
                    </div>
                  ))}
                </div>
                
                {/* Connections */}
                <div className="mt-3 pt-3 border-t border-gray-700">
                  <div className="text-xs text-gray-400 mb-1">Connections:</div>
                  <div className="flex flex-wrap gap-1">
                    {system.connections.map(connId => {
                      const connSystem = systems.find(s => s.id === connId)
                      if (!connSystem) return null
                      return (
                        <span
                          key={connId}
                          className="text-xs px-1.5 py-0.5 rounded bg-gray-800 text-gray-300 border border-gray-700"
                          title={connSystem.fullName}
                        >
                          {connSystem.name}
                        </span>
                      )
                    })}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
        
        {/* Selected System Details */}
        {selectedSystemData && (
          <div className="mb-6 p-4 rounded-lg border border-gray-700 bg-gray-800">
            <div className="flex items-center gap-2 mb-3">
              <selectedSystemData.icon className="w-5 h-5" />
              <h3 className="text-sm font-semibold text-gray-200">{selectedSystemData.fullName}</h3>
              {getStatusIcon(selectedSystemData.status)}
            </div>
            
            <div className="text-xs text-gray-400 mb-3">{selectedSystemData.description}</div>
            
            {/* All Metrics */}
            <div className="grid grid-cols-2 gap-3 mb-3">
              {Object.entries(selectedSystemData.metrics).map(([key, value]) => (
                <div key={key} className="p-2 rounded border border-gray-700 bg-gray-900">
                  <div className="text-xs text-gray-400 mb-1 capitalize">{key.replace('_', ' ')}</div>
                  <div className="text-sm font-semibold text-gray-200">
                    {typeof value === 'boolean' ? (value ? '✓ Enabled' : '✗ Disabled') :
                     typeof value === 'number' && value < 1 ? value.toFixed(3) :
                     typeof value === 'number' ? value.toLocaleString() :
                     String(value)}
                  </div>
                </div>
              ))}
            </div>
            
            {/* Connection Details */}
            <div>
              <div className="text-xs text-gray-400 mb-2">System Connections:</div>
              <div className="space-y-2">
                {selectedSystemData.connections.map(connId => {
                  const connSystem = systems.find(s => s.id === connId)
                  if (!connSystem) return null
                  return (
                    <div key={connId} className="flex items-center justify-between p-2 rounded border border-gray-700 bg-gray-900">
                      <div className="flex items-center gap-2">
                        <connSystem.icon className="w-4 h-4" />
                        <span className="text-xs text-gray-300">{connSystem.fullName}</span>
                      </div>
                      {getStatusIcon(connSystem.status)}
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )}
        
        {/* System Connections Graph */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
            <Network className="w-4 h-4" />
            System Connection Graph
          </h3>
          <div className="p-4 rounded border border-gray-700 bg-gray-800">
            <div className="text-xs text-gray-400 mb-3">
              All AIM-OS systems are interconnected and orchestrated by APOE:
            </div>
            <div className="space-y-2 text-xs text-gray-500">
              {systems.map(system => (
                <div key={system.id} className="flex items-center gap-2">
                  <system.icon className="w-4 h-4" />
                  <span className="text-gray-300 font-semibold">{system.name}</span>
                  <span className="text-gray-500">→</span>
                  <span className="text-gray-400">
                    {system.connections.map(id => {
                      const conn = systems.find(s => s.id === id)
                      return conn?.name
                    }).filter(Boolean).join(', ')}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {/* Overall Status Summary */}
        <div>
          <h3 className="text-sm font-semibold text-gray-300 mb-3">Overall Status</h3>
          <div className={`p-4 rounded-lg border ${
            systems.every(s => s.status === 'healthy')
              ? 'border-green-700 bg-green-900/30'
              : systems.some(s => s.status === 'degraded' || s.status === 'offline')
              ? 'border-red-700 bg-red-900/30'
              : 'border-yellow-700 bg-yellow-900/30'
          }`}>
            <div className="flex items-center gap-2 mb-2">
              {systems.every(s => s.status === 'healthy') ? (
                <>
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  <span className="text-sm font-semibold text-green-400">All Systems Operational</span>
                </>
              ) : systems.some(s => s.status === 'degraded' || s.status === 'offline') ? (
                <>
                  <XCircle className="w-5 h-5 text-red-400" />
                  <span className="text-sm font-semibold text-red-400">System Degradation Detected</span>
                </>
              ) : (
                <>
                  <AlertTriangle className="w-5 h-5 text-yellow-400" />
                  <span className="text-sm font-semibold text-yellow-400">Some Systems Warning</span>
                </>
              )}
            </div>
            <div className="text-xs text-gray-400">
              {systems.filter(s => s.status === 'healthy').length} of {systems.length} systems healthy
              {systems.filter(s => s.status === 'warning').length > 0 && 
                ` • ${systems.filter(s => s.status === 'warning').length} warnings`}
              {systems.filter(s => s.status === 'degraded' || s.status === 'offline').length > 0 && 
                ` • ${systems.filter(s => s.status === 'degraded' || s.status === 'offline').length} degraded/offline`}
            </div>
          </div>
      </div>
      </div>
    </BasePanel>
  )
}
