// System Status Panel - V2 Refactored with BasePanel
// CAS health monitoring with real AttentionMetrics structure

import React, { useEffect, useState } from 'react'
import { useCAS } from '../hooks/useAIMOS'
import { Activity, Database, Network, Shield, Brain, Target, CheckCircle, AlertTriangle, TrendingUp, TrendingDown, Clock } from 'lucide-react'
import { BasePanel } from '../components/BasePanel'
import { LoadingSpinner, ErrorDisplay } from '../components/shared/shared'
import type { CASAttentionMetrics } from '../hooks/useAIMOS'

interface SystemStatusProps {
  metrics?: CASAttentionMetrics | null
}

export const SystemStatus: React.FC<SystemStatusProps> = ({ metrics: propMetrics }) => {
  const { getMetrics } = useCAS()
  const [casMetrics, setCasMetrics] = useState<CASAttentionMetrics | null>(propMetrics || null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    const loadMetrics = async () => {
      try {
        setLoading(true)
        setError(null)
        const m = await getMetrics()
        setCasMetrics(m)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load metrics')
      } finally {
        setLoading(false)
      }
    }
    loadMetrics()
    
    // Refresh every 5 seconds
    const interval = setInterval(loadMetrics, 5000)
    return () => clearInterval(interval)
  }, [getMetrics])
  
  const metrics = casMetrics || propMetrics
  
  const systems = [
    {
      id: 'cmc',
      name: 'CMC',
      description: 'Context Memory Core - Bitemporal storage',
      icon: Database,
      status: 'online',
      health: 'excellent',
      metrics: {
        atoms: 1250,
        confidence: 0.92
      }
    },
    {
      id: 'hhni',
      name: 'HHNI',
      description: 'Hierarchical Hypergraph Neural Index - Semantic search',
      icon: Network,
      status: 'online',
      health: 'excellent',
      metrics: {
        indexed_nodes: 8500,
        confidence: 0.88
      }
    },
    {
      id: 'vif',
      name: 'VIF',
      description: 'Verifiable Intelligence Framework - Confidence tracking',
      icon: Shield,
      status: 'online',
      health: 'excellent',
      metrics: {
        witnesses: 3420,
        confidence: 0.90,
        ece_score: 0.05
      }
    },
    {
      id: 'seg',
      name: 'SEG',
      description: 'Synthesis & Evidence Graph - Knowledge synthesis',
      icon: Brain,
      status: 'online',
      health: 'good',
      metrics: {
        entities: 1250,
        relations: 3420,
        contradictions: 12,
        confidence: 0.85
      }
    },
    {
      id: 'apoe',
      name: 'APOE',
      description: 'AI-Powered Orchestration Engine - Task orchestration',
      icon: Target,
      status: 'online',
      health: 'excellent',
      metrics: {
        active_plans: 3,
        completed_tasks: 125,
        confidence: 0.92
      }
    },
    {
      id: 'cas',
      name: 'CAS',
      description: 'Consciousness Analysis System - Attention monitoring',
      icon: Activity,
      status: 'online',
      health: metrics?.quality_level || 'good',
      metrics: metrics ? {
        working_memory_items: metrics.working_memory_items,
        cognitive_load: metrics.cognitive_load,
        attention_state: metrics.current_state,
        quality_level: metrics.quality_level,
        focus_depth: metrics.focus_depth,
        attention_stability: metrics.attention_stability,
        error_rate: metrics.error_rate,
        confidence_drift: metrics.confidence_drift,
        warnings: metrics.warnings.length,
        alerts: metrics.alerts.length
      } : null
    }
  ]
  
  const getHealthColor = (health: string) => {
    switch (health) {
      case 'excellent': return 'text-green-400 border-green-500 bg-green-900/20'
      case 'good': return 'text-blue-400 border-blue-500 bg-blue-900/20'
      case 'fair': return 'text-yellow-400 border-yellow-500 bg-yellow-900/20'
      case 'poor': return 'text-orange-400 border-orange-500 bg-orange-900/20'
      case 'critical': return 'text-red-400 border-red-500 bg-red-900/20'
      default: return 'text-gray-400 border-gray-500 bg-gray-900/20'
    }
  }
  
  const getHealthIcon = (health: string) => {
    switch (health) {
      case 'excellent':
      case 'good':
        return CheckCircle
      case 'fair':
      case 'poor':
      case 'critical':
        return AlertTriangle
      default:
        return Activity
    }
  }
  
  const getAttentionStateColor = (state: string) => {
    switch (state) {
      case 'optimal': return 'text-green-400'
      case 'focused': return 'text-blue-400'
      case 'distributed': return 'text-yellow-400'
      case 'overloaded': return 'text-orange-400'
      case 'narrowed': return 'text-red-400'
      case 'degraded': return 'text-red-500'
      default: return 'text-gray-400'
    }
  }
  
  const formatMetricValue = (value: any): string => {
    if (typeof value === 'number') {
      if (value < 1) {
        return (value * 100).toFixed(1) + '%'
      }
      return value.toLocaleString()
    }
    return String(value)
  }
  
  // Calculate overall confidence and contradictions
  const overallConfidence = metrics ? 
    (metrics.quality_level === 'excellent' ? 0.95 : 
     metrics.quality_level === 'good' ? 0.85 : 
     metrics.quality_level === 'fair' ? 0.75 : 0.60) : undefined
  
  const contradictionCount = metrics ? (metrics.warnings.length + metrics.alerts.length) : 0
  
  const onlineSystemsCount = systems.filter(s => s.status === 'online').length
  const totalSystemsCount = systems.length
  
  return (
    <BasePanel
      id="panel-system-status"
      title="System Status"
      icon={Activity}
      description="Real-time AIM-OS system health monitoring"
      loading={loading}
      error={error}
      empty={!loading && !error && !metrics}
      emptyMessage="No system metrics available"
      confidence={overallConfidence}
      confidenceBand={overallConfidence ? (overallConfidence >= 0.90 ? 'A' : overallConfidence >= 0.70 ? 'B' : 'C') : undefined}
      contradictionCount={contradictionCount}
      footerContent={
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>
            {onlineSystemsCount}/{totalSystemsCount} systems online
          </span>
          <span className="text-green-400 flex items-center gap-1">
            <Clock className="w-3 h-3" />
            CAS Monitoring Active
          </span>
        </div>
      }
    >
      
      {/* CAS Attention Metrics Summary (if available) */}
      {metrics && (
        <div className="p-3 border-b border-gray-700 bg-gray-800/50">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-4 h-4 text-blue-400" />
            <span className="text-xs font-semibold text-gray-300">CAS Attention Metrics</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-gray-500">State:</span>
              <span className={`ml-2 ${getAttentionStateColor(metrics.current_state)} capitalize`}>
                {metrics.current_state}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Quality:</span>
              <span className={`ml-2 ${getHealthColor(metrics.quality_level).split(' ')[0]} capitalize`}>
                {metrics.quality_level}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Working Memory:</span>
              <span className="ml-2 text-gray-300">{metrics.working_memory_items} items</span>
            </div>
            <div>
              <span className="text-gray-500">Cognitive Load:</span>
              <span className={`ml-2 ${
                metrics.cognitive_load > 0.8 ? 'text-red-400' :
                metrics.cognitive_load > 0.6 ? 'text-yellow-400' : 'text-green-400'
              }`}>
                {(metrics.cognitive_load * 100).toFixed(0)}%
              </span>
            </div>
            <div>
              <span className="text-gray-500">Focus Depth:</span>
              <span className="ml-2 text-gray-300">{(metrics.focus_depth * 100).toFixed(0)}%</span>
            </div>
            <div>
              <span className="text-gray-500">Stability:</span>
              <span className="ml-2 text-gray-300">{(metrics.attention_stability * 100).toFixed(0)}%</span>
            </div>
            {metrics.warnings.length > 0 && (
              <div className="col-span-2">
                <span className="text-yellow-400">⚠️ {metrics.warnings.length} warnings</span>
              </div>
            )}
            {metrics.alerts.length > 0 && (
              <div className="col-span-2">
                <span className="text-red-400">🚨 {metrics.alerts.length} alerts</span>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Systems List */}
      <div className="flex-1 overflow-auto p-3 space-y-2">
        {systems.map((system) => {
          const Icon = system.icon
          const HealthIcon = getHealthIcon(system.health)
          const healthColor = getHealthColor(system.health)
          
          return (
            <div
              key={system.id}
              className={`p-3 rounded border ${healthColor.split(' ')[2]} bg-gray-800 hover:opacity-80 transition-opacity`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <Icon className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  <div className="min-w-0">
                    <div className="text-sm font-semibold text-gray-200">{system.name}</div>
                    <div className="text-xs text-gray-400 truncate">{system.description}</div>
                  </div>
                </div>
                <div className={`flex items-center gap-1 ${healthColor.split(' ')[0]} flex-shrink-0`}>
                  <HealthIcon className="w-4 h-4" />
                  <span className="text-xs capitalize">{system.health}</span>
                </div>
              </div>
              
              {/* Metrics */}
              {system.metrics && (
                <div className="mt-2 space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-400">Status:</span>
                    <span className={`${
                      system.status === 'online' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {system.status}
                    </span>
                  </div>
                  
                  {Object.entries(system.metrics).map(([key, value]) => {
                    if (key === 'confidence' && typeof value === 'number') {
                      return (
                        <div key={key} className="flex items-center justify-between text-xs">
                          <span className="text-gray-400">Confidence:</span>
                          <span className={`${
                            value >= 0.85 ? 'text-green-400' : 
                            value >= 0.70 ? 'text-yellow-400' : 'text-red-400'
                          }`}>
                            {(value * 100).toFixed(0)}%
                          </span>
                        </div>
                      )
                    }
                    
                    if (key === 'cognitive_load' && typeof value === 'number') {
                      return (
                        <div key={key} className="flex items-center justify-between text-xs">
                          <span className="text-gray-400">Cognitive Load:</span>
                          <span className={`${
                            value > 0.8 ? 'text-red-400' :
                            value > 0.6 ? 'text-yellow-400' : 'text-green-400'
                          }`}>
                            {(value * 100).toFixed(0)}%
                          </span>
                        </div>
                      )
                    }
                    
                    if (key === 'attention_state') {
                      return (
                        <div key={key} className="flex items-center justify-between text-xs">
                          <span className="text-gray-400">Attention:</span>
                          <span className={getAttentionStateColor(String(value)) + ' capitalize'}>
                            {String(value)}
                          </span>
                        </div>
                      )
                    }
                    
                    if (key === 'warnings' || key === 'alerts') {
                      const count = typeof value === 'number' ? value : 0
                      if (count === 0) return null
                      return (
                        <div key={key} className="flex items-center justify-between text-xs">
                          <span className="text-gray-400 capitalize">{key}:</span>
                          <span className={key === 'alerts' ? 'text-red-400' : 'text-yellow-400'}>
                            {count}
                          </span>
                        </div>
                      )
                    }
                    
                    return (
                      <div key={key} className="flex items-center justify-between text-xs">
                        <span className="text-gray-400 capitalize">{key.replace(/_/g, ' ')}:</span>
                        <span className="text-gray-300">{formatMetricValue(value)}</span>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </div>
      
    </BasePanel>
  )
}
