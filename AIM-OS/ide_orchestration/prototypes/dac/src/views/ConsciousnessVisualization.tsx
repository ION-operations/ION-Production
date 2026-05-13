// Consciousness Visualization View - V2 Refactored with BasePanel
// Real-time consciousness state visualization with CAS AttentionMetrics

import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { BasePanel } from '../components/BasePanel'
import { useCAS, useCMC, useHHNI } from '../hooks/useAIMOS'
import { Brain, Activity, TrendingUp, TrendingDown, AlertTriangle, CheckCircle, XCircle, Database, Target, Zap, RefreshCw } from 'lucide-react'
import type { AttentionMetrics } from '../hooks/useAIMOS'

export const ConsciousnessVisualization: React.FC = () => {
  const { getMetrics, detectDrift } = useCAS()
  const { getStats: getCMCStats } = useCMC()
  const { getStats: getHHNIStats } = useHHNI()
  const [metrics, setMetrics] = useState<AttentionMetrics | null>(null)
  const [driftDetected, setDriftDetected] = useState<boolean>(false)
  const [metricsHistory, setMetricsHistory] = useState<AttentionMetrics[]>([])
  const [memoryStats, setMemoryStats] = useState<any>(null)
  const [hhniStats, setHHNIStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [refreshInterval, setRefreshInterval] = useState(3000)
  
  const loadAllMetrics = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Load CAS metrics
      const m = await getMetrics()
      setMetrics(m)
      
      // Add to history (keep last 50 for trend analysis)
      setMetricsHistory(prev => {
        const updated = m ? [m, ...prev].slice(0, 50) : prev
        return updated
      })
      
      // Check for drift
      if (m) {
        const drift = await detectDrift(
          m.context_size_tokens,
          m.error_rate,
          m.working_memory_items
        )
        setDriftDetected(drift.drift_detected)
      }
      
      // Load memory stats
      try {
        const cmcStats = await getCMCStats()
        setMemoryStats(cmcStats)
      } catch (err) {
        console.warn('Failed to load CMC stats:', err)
      }
      
      // Load HHNI stats
      try {
        const hhniStatsData = await getHHNIStats()
        setHHNIStats(hhniStatsData)
      } catch (err) {
        console.warn('Failed to load HHNI stats:', err)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load consciousness metrics')
    } finally {
      setLoading(false)
    }
  }, [getMetrics, detectDrift, getCMCStats, getHHNIStats])
  
  useEffect(() => {
    loadAllMetrics()
    
    if (autoRefresh) {
      const interval = setInterval(loadAllMetrics, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [loadAllMetrics, autoRefresh, refreshInterval])
  
  const getHealthColor = (health: string) => {
    switch (health) {
      case 'excellent': return 'text-green-400 bg-green-900/30 border-green-700'
      case 'good': return 'text-green-400 bg-green-900/30 border-green-700'
      case 'fair': return 'text-yellow-400 bg-yellow-900/30 border-yellow-700'
      case 'poor': return 'text-orange-400 bg-orange-900/30 border-orange-700'
      case 'critical': return 'text-red-400 bg-red-900/30 border-red-700'
      default: return 'text-gray-400 bg-gray-800 border-gray-700'
    }
  }
  
  const getStateColor = (state: string) => {
    switch (state) {
      case 'optimal': return 'text-green-400'
      case 'focused': return 'text-blue-400'
      case 'distributed': return 'text-yellow-400'
      case 'overloaded': return 'text-orange-400'
      case 'narrowed': return 'text-purple-400'
      case 'degraded': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }
  
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.85) return 'text-green-400'
    if (confidence >= 0.70) return 'text-yellow-400'
    return 'text-red-400'
  }
  
  // Calculate attention heatmap data (only if metrics exists)
  const attentionData = metrics ? [
    { label: 'Working Memory', value: metrics.working_memory_items, max: 50, color: 'bg-blue-500' },
    { label: 'Context Size', value: metrics.context_size_tokens, max: 200000, color: 'bg-purple-500' },
    { label: 'Attention Span', value: metrics.attention_span_minutes, max: 60, color: 'bg-green-500' },
    { label: 'Task Switches', value: metrics.task_switches_per_hour, max: 20, color: 'bg-yellow-500' },
    { label: 'Focus Depth', value: metrics.focus_depth, max: 1.0, color: 'bg-cyan-500' },
    { label: 'Attention Stability', value: metrics.attention_stability, max: 1.0, color: 'bg-indigo-500' },
    { label: 'Cognitive Load', value: metrics.cognitive_load, max: 1.0, color: 'bg-red-500' },
    { label: 'Error Rate', value: metrics.error_rate, max: 1.0, color: 'bg-orange-500' },
    { label: 'Retry Frequency', value: metrics.retry_frequency, max: 1.0, color: 'bg-pink-500' },
    { label: 'Confidence Drift', value: metrics.confidence_drift, max: 1.0, color: 'bg-rose-500' }
  ] : []
  
  // Calculate trend (comparing current to previous)
  const getTrend = (current: number, previous: number) => {
    if (current > previous) return 'up'
    if (current < previous) return 'down'
    return 'stable'
  }
  
  // Calculate trend data for charts
  const trendData = useMemo(() => {
    if (metricsHistory.length < 2) return null
    
    return {
      workingMemory: metricsHistory.map(m => ({ time: m.timestamp, value: m.working_memory_items })),
      cognitiveLoad: metricsHistory.map(m => ({ time: m.timestamp, value: m.cognitive_load })),
      confidence: metricsHistory.map(m => ({ time: m.timestamp, value: 1 - m.confidence_drift })),
      errorRate: metricsHistory.map(m => ({ time: m.timestamp, value: m.error_rate }))
    }
  }, [metricsHistory])
  
  // Calculate memory health
  const memoryHealth = useMemo(() => {
    if (!memoryStats) return null
    
    const totalAtoms = memoryStats.total_atoms || 0
    const recentAtoms = memoryStats.recent_atoms_24h || 0
    const avgConfidence = memoryStats.average_confidence || 0.85
    
    return {
      totalAtoms,
      recentAtoms,
      avgConfidence,
      health: avgConfidence >= 0.90 ? 'excellent' : avgConfidence >= 0.70 ? 'good' : 'fair'
    }
  }, [memoryStats])
  
  // Calculate HHNI health
  const hhniHealth = useMemo(() => {
    if (!hhniStats) return null
    
    const totalNodes = hhniStats.total_nodes || 0
    const avgDepth = hhniStats.average_depth || 0
    
    return {
      totalNodes,
      avgDepth,
      health: avgDepth >= 3 ? 'excellent' : avgDepth >= 2 ? 'good' : 'fair'
    }
  }, [hhniStats])
  const overallConfidence = metrics 
    ? (metrics.attention_stability + (1 - metrics.confidence_drift) + (1 - metrics.error_rate)) / 3
    : undefined
  
  const confidenceBand = overallConfidence 
    ? (overallConfidence >= 0.90 ? 'A' : overallConfidence >= 0.70 ? 'B' : 'C')
    : undefined
  
  return (
    <BasePanel
      id="panel-consciousness-visualization"
      title="Consciousness Visualization"
      icon={Brain}
      description="Real-time visualization of AI consciousness state via CAS (Consciousness Analysis System)"
      loading={loading}
      error={error}
      empty={!loading && !error && !metrics}
      emptyMessage="No consciousness metrics available"
      confidence={overallConfidence}
      confidenceBand={confidenceBand}
      footerContent={
        <div className="flex items-center justify-between text-xs text-gray-400">
          <div className="flex items-center gap-3">
            <span>CAS Metrics</span>
            {autoRefresh && (
              <span className="flex items-center gap-1">
                <RefreshCw className="w-3 h-3 animate-spin" />
                Auto-refresh: {refreshInterval / 1000}s
              </span>
            )}
          </div>
          <span className="text-green-400">Consciousness Monitoring Active</span>
        </div>
      }
      headerClassName="p-4"
    >
      {/* Controls */}
      <div className="p-4 border-b border-gray-700 flex items-center gap-3 flex-wrap">
        <button
          onClick={() => setAutoRefresh(!autoRefresh)}
          className={`px-3 py-1 rounded text-xs flex items-center gap-1 ${
            autoRefresh
              ? 'bg-green-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          <RefreshCw className={`w-3 h-3 ${autoRefresh ? 'animate-spin' : ''}`} />
          Auto-refresh
        </button>
        
        <select
          value={refreshInterval}
          onChange={(e) => setRefreshInterval(Number(e.target.value))}
          className="px-2 py-1 rounded text-xs bg-gray-700 text-gray-300 border border-gray-600"
          disabled={!autoRefresh}
        >
          <option value="1000">1s</option>
          <option value="3000">3s</option>
          <option value="5000">5s</option>
          <option value="10000">10s</option>
        </select>
        
        <button
          onClick={loadAllMetrics}
          className="px-3 py-1 rounded text-xs bg-blue-600 text-white hover:bg-blue-700 flex items-center gap-1"
        >
          <Zap className="w-3 h-3" />
          Refresh Now
        </button>
      </div>
      
      {/* Status Indicators */}
      {metrics && (
        <div className="p-4 border-b border-gray-700 flex items-center gap-2 flex-wrap">
          <span className={`text-xs px-2 py-1 rounded ${getHealthColor(metrics.quality_level)}`}>
            {metrics.quality_level.toUpperCase()}
          </span>
          {driftDetected && (
            <span className="text-xs px-2 py-1 rounded bg-red-900/30 border border-red-700 text-red-400 flex items-center gap-1">
              <AlertTriangle className="w-3 h-3" />
              DRIFT DETECTED
            </span>
          )}
        </div>
      )}
      
      {/* Memory Awareness Section */}
      {(memoryHealth || hhniHealth) && (
        <div className="p-4 border-b border-gray-700">
          <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
            <Database className="w-4 h-4" />
            Memory Awareness
          </h3>
          <div className="grid grid-cols-2 gap-3">
            {memoryHealth && (
              <div className={`p-3 rounded border ${
                memoryHealth.health === 'excellent' ? 'border-green-700 bg-green-900/20' :
                memoryHealth.health === 'good' ? 'border-blue-700 bg-blue-900/20' :
                'border-yellow-700 bg-yellow-900/20'
              }`}>
                <div className="text-xs text-gray-400 mb-1">CMC Memory Health</div>
                <div className="text-lg font-semibold text-gray-200 capitalize">{memoryHealth.health}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {memoryHealth.totalAtoms.toLocaleString()} atoms • {memoryHealth.recentAtoms.toLocaleString()} recent
                </div>
                <div className="text-xs text-gray-500">
                  Avg Confidence: {(memoryHealth.avgConfidence * 100).toFixed(0)}%
                </div>
              </div>
            )}
            
            {hhniHealth && (
              <div className={`p-3 rounded border ${
                hhniHealth.health === 'excellent' ? 'border-green-700 bg-green-900/20' :
                hhniHealth.health === 'good' ? 'border-blue-700 bg-blue-900/20' :
                'border-yellow-700 bg-yellow-900/20'
              }`}>
                <div className="text-xs text-gray-400 mb-1">HHNI Index Health</div>
                <div className="text-lg font-semibold text-gray-200 capitalize">{hhniHealth.health}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {hhniHealth.totalNodes.toLocaleString()} nodes • Avg Depth: {hhniHealth.avgDepth.toFixed(1)}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Trend Visualization */}
      {trendData && metricsHistory.length > 1 && (
        <div className="p-4 border-b border-gray-700">
          <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Trend Analysis ({metricsHistory.length} data points)
          </h3>
          <div className="space-y-4">
            {trendData.workingMemory.length > 1 && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Working Memory Trend</div>
                <div className="flex items-end gap-1 h-20">
                  {trendData.workingMemory.slice(0, 20).map((point, idx) => {
                    const maxValue = Math.max(...trendData.workingMemory.map(p => p.value))
                    const height = maxValue > 0 ? (point.value / maxValue) * 100 : 0
                    return (
                      <div
                        key={idx}
                        className="flex-1 bg-blue-500 rounded-t transition-all"
                        style={{ height: `${height}%` }}
                        title={`${point.value} items`}
                      />
                    )
                  })}
                </div>
              </div>
            )}
            
            {trendData.cognitiveLoad.length > 1 && (
              <div>
                <div className="text-xs text-gray-400 mb-1">Cognitive Load Trend</div>
                <div className="flex items-end gap-1 h-20">
                  {trendData.cognitiveLoad.slice(0, 20).map((point, idx) => {
                    const height = point.value * 100
                    const color = height >= 80 ? 'bg-red-500' : height >= 60 ? 'bg-yellow-500' : 'bg-green-500'
                    return (
                      <div
                        key={idx}
                        className={`flex-1 ${color} rounded-t transition-all`}
                        style={{ height: `${height}%` }}
                        title={`${(point.value * 100).toFixed(0)}%`}
                      />
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Content */}
      {metrics && (
        <div className="flex-1 overflow-auto p-4 space-y-6">
        {/* Current State Overview */}
        <div className="grid grid-cols-3 gap-4">
          <div className={`p-4 rounded-lg border ${getHealthColor(metrics.quality_level)}`}>
            <div className="text-xs text-gray-400 mb-1 uppercase">Quality Level</div>
            <div className="text-2xl font-bold capitalize">{metrics.quality_level}</div>
            <div className="text-xs text-gray-500 mt-1">Overall system quality</div>
          </div>
          
          <div className={`p-4 rounded-lg border ${getStateColor(metrics.current_state)} border-gray-700`}>
            <div className="text-xs text-gray-400 mb-1 uppercase">Current State</div>
            <div className={`text-2xl font-bold capitalize ${getStateColor(metrics.current_state)}`}>
              {metrics.current_state}
            </div>
            <div className="text-xs text-gray-500 mt-1">Attention state</div>
          </div>
          
          <div className="p-4 rounded-lg border border-gray-700 bg-gray-800">
            <div className="text-xs text-gray-400 mb-1 uppercase">Session ID</div>
            <div className="text-sm font-mono text-gray-300 truncate">{metrics.session_id}</div>
            <div className="text-xs text-gray-500 mt-1">Last updated: {new Date(metrics.timestamp).toLocaleTimeString()}</div>
          </div>
        </div>
        
        {/* Attention Heatmap */}
        <div>
          <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Attention Heatmap
          </h3>
          <div className="space-y-3">
            {attentionData.map((item, index) => {
              const percentage = (item.value / item.max) * 100
              const trend = previousMetrics ? getTrend(item.value, (previousMetrics as any)[Object.keys(metrics)[index]]) : 'stable'
              
              return (
                <div key={item.label} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-400 capitalize">{item.label.replace('_', ' ')}</span>
                    <div className="flex items-center gap-2">
                      {previousMetrics && (
                        trend === 'up' ? (
                          <TrendingUp className="w-3 h-3 text-green-400" />
                        ) : trend === 'down' ? (
                          <TrendingDown className="w-3 h-3 text-red-400" />
                        ) : null
                      )}
                      <span className="text-gray-300 font-mono">
                        {typeof item.value === 'number' && item.value < 1 
                          ? item.value.toFixed(2) 
                          : Math.round(item.value).toLocaleString()}
                      </span>
                      <span className="text-gray-500">/ {Math.round(item.max).toLocaleString()}</span>
                    </div>
                  </div>
                  <div className="relative bg-gray-800 rounded-full h-6 overflow-hidden">
                    <div
                      className={`${item.color} h-6 rounded-full transition-all duration-300 flex items-center justify-end pr-2`}
                      style={{ width: `${Math.min(percentage, 100)}%` }}
                    >
                      {percentage > 10 && (
                        <span className="text-xs text-white font-semibold">
                          {percentage.toFixed(0)}%
                        </span>
                      )}
                    </div>
                    {percentage <= 10 && (
                      <span className="absolute inset-0 flex items-center justify-end pr-2 text-xs text-gray-500">
                        {percentage.toFixed(0)}%
                      </span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
        
        {/* Cognitive Metrics Grid */}
        <div>
          <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
            <Brain className="w-4 h-4" />
            Cognitive Metrics
          </h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 rounded border border-gray-700 bg-gray-800">
              <div className="text-xs text-gray-400 mb-1">Working Memory Items</div>
              <div className="text-lg font-semibold text-gray-200">{metrics.working_memory_items}</div>
              <div className="text-xs text-gray-500 mt-1">Current active items</div>
            </div>
            
            <div className="p-3 rounded border border-gray-700 bg-gray-800">
              <div className="text-xs text-gray-400 mb-1">Context Size (Tokens)</div>
              <div className="text-lg font-semibold text-gray-200">
                {metrics.context_size_tokens.toLocaleString()}
              </div>
              <div className="text-xs text-gray-500 mt-1">Current context window</div>
            </div>
            
            <div className="p-3 rounded border border-gray-700 bg-gray-800">
              <div className="text-xs text-gray-400 mb-1">Attention Span</div>
              <div className="text-lg font-semibold text-gray-200">
                {metrics.attention_span_minutes.toFixed(1)} min
              </div>
              <div className="text-xs text-gray-500 mt-1">Average focus duration</div>
            </div>
            
            <div className="p-3 rounded border border-gray-700 bg-gray-800">
              <div className="text-xs text-gray-400 mb-1">Task Switches/Hour</div>
              <div className="text-lg font-semibold text-gray-200">
                {metrics.task_switches_per_hour.toFixed(1)}
              </div>
              <div className="text-xs text-gray-500 mt-1">Context switching frequency</div>
            </div>
            
            <div className="p-3 rounded border border-gray-700 bg-gray-800">
              <div className="text-xs text-gray-400 mb-1">Focus Depth</div>
              <div className={`text-lg font-semibold ${getConfidenceColor(metrics.focus_depth)}`}>
                {(metrics.focus_depth * 100).toFixed(0)}%
              </div>
              <div className="text-xs text-gray-500 mt-1">Depth of current focus</div>
            </div>
            
            <div className="p-3 rounded border border-gray-700 bg-gray-800">
              <div className="text-xs text-gray-400 mb-1">Attention Stability</div>
              <div className={`text-lg font-semibold ${getConfidenceColor(metrics.attention_stability)}`}>
                {(metrics.attention_stability * 100).toFixed(0)}%
              </div>
              <div className="text-xs text-gray-500 mt-1">Stability of attention</div>
            </div>
            
            <div className="p-3 rounded border border-gray-700 bg-gray-800">
              <div className="text-xs text-gray-400 mb-1">Cognitive Load</div>
              <div className={`text-lg font-semibold ${
                metrics.cognitive_load >= 0.8 ? 'text-red-400' :
                metrics.cognitive_load >= 0.6 ? 'text-yellow-400' : 'text-green-400'
              }`}>
                {(metrics.cognitive_load * 100).toFixed(0)}%
              </div>
              <div className="text-xs text-gray-500 mt-1">Current cognitive load</div>
            </div>
            
            <div className="p-3 rounded border border-gray-700 bg-gray-800">
              <div className="text-xs text-gray-400 mb-1">Confidence Drift</div>
              <div className={`text-lg font-semibold ${
                metrics.confidence_drift >= 0.2 ? 'text-red-400' :
                metrics.confidence_drift >= 0.1 ? 'text-yellow-400' : 'text-green-400'
              }`}>
                {(metrics.confidence_drift * 100).toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500 mt-1">Confidence drift from baseline</div>
            </div>
          </div>
        </div>
        
        {/* Error & Quality Metrics */}
        <div>
          <h3 className="text-sm font-semibold text-gray-300 mb-3">Error & Quality Metrics</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 rounded border border-gray-700 bg-gray-800">
              <div className="text-xs text-gray-400 mb-1">Error Rate</div>
              <div className={`text-lg font-semibold ${
                metrics.error_rate >= 0.2 ? 'text-red-400' :
                metrics.error_rate >= 0.1 ? 'text-yellow-400' : 'text-green-400'
              }`}>
                {(metrics.error_rate * 100).toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500 mt-1">Recent error frequency</div>
            </div>
            
            <div className="p-3 rounded border border-gray-700 bg-gray-800">
              <div className="text-xs text-gray-400 mb-1">Retry Frequency</div>
              <div className={`text-lg font-semibold ${
                metrics.retry_frequency >= 0.3 ? 'text-red-400' :
                metrics.retry_frequency >= 0.15 ? 'text-yellow-400' : 'text-green-400'
              }`}>
                {(metrics.retry_frequency * 100).toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500 mt-1">Retry attempt frequency</div>
            </div>
          </div>
        </div>
        
        {/* Warnings & Alerts */}
        {(metrics.warnings.length > 0 || metrics.alerts.length > 0) && (
          <div>
            <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-yellow-400" />
              Warnings & Alerts
            </h3>
            <div className="space-y-2">
              {metrics.warnings.map((warning, index) => (
                <div key={index} className="p-3 rounded border border-yellow-700 bg-yellow-900/20 text-yellow-300 text-sm flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>{warning}</span>
                </div>
              ))}
              {metrics.alerts.map((alert, index) => (
                <div key={index} className="p-3 rounded border border-red-700 bg-red-900/20 text-red-300 text-sm flex items-start gap-2">
                  <XCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>{alert}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Drift Detection Status */}
        {driftDetected && (
          <div className="p-4 rounded-lg border border-red-700 bg-red-900/20">
            <div className="flex items-center gap-2 mb-2">
              <TrendingDown className="w-5 h-5 text-red-400" />
              <h3 className="text-sm font-semibold text-red-400">Cognitive Drift Detected</h3>
            </div>
            <div className="text-sm text-red-300">
              Attention narrowing or cognitive load increase detected. System may require intervention or recalibration.
            </div>
          </div>
        )}
        
        {/* Health Status Summary */}
        {metrics.quality_level === 'excellent' && !driftDetected && metrics.warnings.length === 0 && (
          <div className="p-4 rounded-lg border border-green-700 bg-green-900/20 flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-400" />
            <div className="text-sm text-green-300">
              All systems operating optimally. Consciousness state is healthy and stable.
            </div>
          </div>
        )}
        )}
      </div>
    </BasePanel>
  )
}
