/**
 * AIM-OS System Visualization
 * Comprehensive visualization of all AIM-OS systems with real-time data
 */

import React, { useState } from 'react'
import { 
  Database, 
  Network, 
  Monitor, 
  Brain, 
  GitBranch, 
  Activity,
  Zap,
  TrendingUp,
  Clock,
  AlertCircle,
  CheckCircle,
  XCircle,
  RefreshCw
} from 'lucide-react'

interface SystemMetrics {
  id: string
  name: string
  status: 'healthy' | 'warning' | 'error' | 'offline'
  health: number
  performance: number
  lastActivity: Date
  metrics: {
    [key: string]: {
      value: number
      unit: string
      trend: 'up' | 'down' | 'stable'
      threshold: { warning: number; critical: number }
    }
  }
  connections: string[]
  metadata: Record<string, any>
}

interface AIMOSSystemVisualizationProps {
  systemId: string
  className?: string
}

export const AIMOSSystemVisualization: React.FC<AIMOSSystemVisualizationProps> = ({
  systemId,
  className = ''
}) => {
  const [_, setmetrics] = useState<SystemMetrics | null>(null)
  const [_, setisLoading] = useState(true)
  const [_, setlastUpdate] = useState<Date>(new Date())

  useEffect(() => {
    loadSystemMetrics()
    const interval = setInterval(loadSystemMetrics, 5000) // Update every 5 seconds
    return () => clearInterval(interval)
  }, [systemId])

  const loadSystemMetrics = async () => {
    setIsLoading(true)
    try {
      // Simulate loading system metrics
      const mockMetrics = generateMockMetrics(systemId)
      setMetrics(mockMetrics)
      setLastUpdate(new Date())
    } catch (error) {
      console.error('Error loading system metrics:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const generateMockMetrics = (systemId: string): SystemMetrics => {
    const baseMetrics = {
      id: systemId,
      name: getSystemName(systemId),
      status: Math.random() > 0.1 ? 'healthy' : 'warning',
      health: 0.7 + Math.random() * 0.3,
      performance: 0.6 + Math.random() * 0.4,
      lastActivity: new Date(Date.now() - Math.random() * 300000),
      connections: getSystemConnections(systemId),
      metadata: {}
    }

    const systemSpecificMetrics = getSystemSpecificMetrics(systemId)
    return { ...baseMetrics, metrics: systemSpecificMetrics }
  }

  const getSystemName = (systemId: string): string => {
    const names: Record<string, string> = {
      'cmc': 'Context Memory Core',
      'hhni': 'Hierarchical Hypergraph Neural Index',
      'vif': 'Verifiable Intelligence Framework',
      'seg': 'Shared Evidence Graph',
      'apoe': 'AI-Powered Orchestration Engine',
      'sdfcvf': 'Atomic Evolution Framework'
    }
    return names[systemId] || systemId
  }

  const getSystemConnections = (systemId: string): string[] => {
    const connections: Record<string, string[]> = {
      'cmc': ['hhni', 'vif'],
      'hhni': ['cmc', 'seg'],
      'vif': ['cmc', 'apoe'],
      'seg': ['hhni', 'apoe'],
      'apoe': ['vif', 'seg', 'sdfcvf'],
      'sdfcvf': ['apoe']
    }
    return connections[systemId] || []
  }

  const getSystemSpecificMetrics = (systemId: string): SystemMetrics['metrics'] => {
    const metricsMap: Record<string, SystemMetrics['metrics']> = {
      'cmc': {
        memoryCount: { value: 1247, unit: 'atoms', trend: 'up', threshold: { warning: 1000, critical: 2000 } },
        memorySize: { value: 45.2, unit: 'MB', trend: 'stable', threshold: { warning: 50, critical: 100 } },
        accessRate: { value: 156, unit: 'req/min', trend: 'up', threshold: { warning: 200, critical: 500 } },
        hitRate: { value: 0.89, unit: '%', trend: 'stable', threshold: { warning: 0.8, critical: 0.7 } }
      },
      'hhni': {
        nodeCount: { value: 5432, unit: 'nodes', trend: 'up', threshold: { warning: 5000, critical: 10000 } },
        connectionCount: { value: 12847, unit: 'edges', trend: 'up', threshold: { warning: 15000, critical: 30000 } },
        searchLatency: { value: 12.5, unit: 'ms', trend: 'down', threshold: { warning: 20, critical: 50 } },
        indexSize: { value: 234.7, unit: 'MB', trend: 'up', threshold: { warning: 300, critical: 500 } }
      },
      'vif': {
        confidenceScore: { value: 0.87, unit: '', trend: 'up', threshold: { warning: 0.8, critical: 0.7 } },
        verifications: { value: 342, unit: 'count', trend: 'up', threshold: { warning: 500, critical: 1000 } },
        falsePositives: { value: 0.03, unit: '%', trend: 'down', threshold: { warning: 0.05, critical: 0.1 } },
        processingTime: { value: 8.3, unit: 'ms', trend: 'down', threshold: { warning: 15, critical: 30 } }
      },
      'seg': {
        evidenceCount: { value: 892, unit: 'items', trend: 'up', threshold: { warning: 1000, critical: 2000 } },
        synthesisRate: { value: 0.76, unit: 'ops/sec', trend: 'up', threshold: { warning: 0.5, critical: 0.3 } },
        graphDensity: { value: 0.34, unit: '', trend: 'stable', threshold: { warning: 0.5, critical: 0.8 } },
        queryComplexity: { value: 2.3, unit: 'avg', trend: 'down', threshold: { warning: 3, critical: 5 } }
      },
      'apoe': {
        activePlans: { value: 12, unit: 'count', trend: 'stable', threshold: { warning: 20, critical: 50 } },
        completedTasks: { value: 156, unit: 'tasks', trend: 'up', threshold: { warning: 200, critical: 500 } },
        planComplexity: { value: 3.2, unit: 'avg', trend: 'down', threshold: { warning: 4, critical: 6 } },
        executionTime: { value: 45.7, unit: 'ms', trend: 'down', threshold: { warning: 100, critical: 200 } }
      },
      'sdfcvf': {
        atomicOperations: { value: 2341, unit: 'ops', trend: 'up', threshold: { warning: 3000, critical: 5000 } },
        evolutionCycles: { value: 45, unit: 'cycles', trend: 'up', threshold: { warning: 100, critical: 200 } },
        mutationRate: { value: 0.12, unit: '%', trend: 'stable', threshold: { warning: 0.2, critical: 0.5 } },
        fitnessScore: { value: 0.78, unit: '', trend: 'up', threshold: { warning: 0.7, critical: 0.6 } }
      }
    }
    return metricsMap[systemId] || {}
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="w-5 h-5 text-green-400" />
      case 'warning': return <AlertCircle className="w-5 h-5 text-yellow-400" />
      case 'error': return <XCircle className="w-5 h-5 text-red-400" />
      case 'offline': return <XCircle className="w-5 h-5 text-gray-400" />
      default: return <AlertCircle className="w-5 h-5 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-400'
      case 'warning': return 'text-yellow-400'
      case 'error': return 'text-red-400'
      case 'offline': return 'text-gray-400'
      default: return 'text-gray-400'
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp className="w-4 h-4 text-green-400" />
      case 'down': return <TrendingUp className="w-4 h-4 text-red-400 transform rotate-180" />
      case 'stable': return <Activity className="w-4 h-4 text-blue-400" />
      default: return <Activity className="w-4 h-4 text-gray-400" />
    }
  }

  const getMetricStatus = (metric: SystemMetrics['metrics'][string]) => {
    if (metric.value >= metric.threshold.critical) return 'critical'
    if (metric.value >= metric.threshold.warning) return 'warning'
    return 'healthy'
  }

  const getMetricColor = (status: string) => {
    switch (status) {
      case 'critical': return 'text-red-400'
      case 'warning': return 'text-yellow-400'
      case 'healthy': return 'text-green-400'
      default: return 'text-gray-400'
    }
  }

  if (isLoading) {
    return (
      <div className={`h-full bg-gray-800 flex items-center justify-center ${className}`}>
        <div className="text-center">
          <RefreshCw className="w-8 h-8 mx-auto mb-2 animate-spin text-blue-400" />
          <p className="text-gray-400">Loading system metrics...</p>
        </div>
      </div>
    )
  }

  if (!metrics) {
    return (
      <div className={`h-full bg-gray-800 flex items-center justify-center ${className}`}>
        <div className="text-center">
          <AlertCircle className="w-8 h-8 mx-auto mb-2 text-red-400" />
          <p className="text-gray-400">Failed to load system metrics</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`h-full bg-gray-800 flex flex-col ${className}`}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
        <div className="flex items-center gap-3">
          {getStatusIcon(metrics.status)}
          <div>
            <h3 className="text-white font-semibold">{metrics.name}</h3>
            <div className="flex items-center gap-2 text-sm">
              <span className={getStatusColor(metrics.status)}>
                {metrics.status.toUpperCase()}
              </span>
              <span className="text-gray-400">•</span>
              <span className="text-gray-400">
                {Math.round(metrics.health * 100)}% health
              </span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <div className="text-xs text-gray-400">
            <Clock className="w-3 h-3 inline mr-1" />
            {lastUpdate.toLocaleTimeString()}
          </div>
          <button
            onClick={loadSystemMetrics}
            className="p-1 bg-gray-700 hover:bg-gray-600 rounded text-gray-400 hover:text-white"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Health Overview */}
      <div className="px-4 py-3 border-b border-gray-700">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-gray-400 mb-1">Health Score</div>
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-green-400 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${metrics.health * 100}%` }}
                ></div>
              </div>
              <span className="text-sm text-white">{Math.round(metrics.health * 100)}%</span>
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-400 mb-1">Performance</div>
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-blue-400 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${metrics.performance * 100}%` }}
                ></div>
              </div>
              <span className="text-sm text-white">{Math.round(metrics.performance * 100)}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-4">
          {Object.entries(metrics.metrics).map(([key, metric]) => {
            const status = getMetricStatus(metric)
            return (
              <div key={key} className="bg-gray-700 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm text-white font-medium capitalize">
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                  </div>
                  <div className="flex items-center gap-1">
                    {getTrendIcon(metric.trend)}
                    <span className={`text-sm ${getMetricColor(status)}`}>
                      {metric.value} {metric.unit}
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center gap-2 text-xs text-gray-400">
                  <span>Threshold: {metric.threshold.warning} - {metric.threshold.critical}</span>
                  <span className={getMetricColor(status)}>
                    {status.toUpperCase()}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Connections */}
      {metrics.connections.length > 0 && (
        <div className="px-4 py-3 border-t border-gray-700">
          <div className="text-sm text-gray-400 mb-2">Connected Systems</div>
          <div className="flex flex-wrap gap-1">
            {metrics.connections.map(connection => (
              <span
                key={connection}
                className="px-2 py-1 bg-blue-900 text-blue-100 text-xs rounded"
              >
                {connection.toUpperCase()}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
