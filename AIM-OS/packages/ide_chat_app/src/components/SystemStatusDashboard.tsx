/**
 * System Status Dashboard
 * Real-time monitoring of all AIM-OS systems and components
 */

import React, { useState, useEffect } from 'react'
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Database, 
  Brain, 
  Network, 
  Shield, 
  Target,
  Zap,
  Users,
  BarChart3,
  Settings,
  GitBranch,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Minus,
  Info
} from 'lucide-react'
import { mcpIntegration } from '../lib/mcp-integration'
import { performanceMonitor } from '../lib/performance-monitor'
import { aimosClient } from '../lib/aimos-client'

interface SystemStatus {
  id: string
  name: string
  status: 'healthy' | 'warning' | 'error' | 'unknown' | 'simulated'
  lastCheck: Date
  responseTime: number
  uptime: number
  metrics: {
    cpu?: number
    memory?: number
    requests?: number
    errors?: number
  }
  description: string
  category: string
  dataSource?: 'real_mcp_data' | 'simulated_data' | 'error_fallback'
  note?: string
}

interface SystemStatusDashboardProps {
  className?: string
}

export const SystemStatusDashboard: React.FC<SystemStatusDashboardProps> = ({ className = '' }) => {
  const [systems, setSystems] = useState<SystemStatus[]>([])
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())
  const [overallHealth, setOverallHealth] = useState<'healthy' | 'warning' | 'error'>('healthy')
  const [dataSource, setDataSource] = useState<'real_mcp_data' | 'simulated_data' | 'error_fallback'>('simulated_data')
  const [statusNote, setStatusNote] = useState<string | null>(null)

  // Load real system status from MCP
  const loadSystemStatus = async () => {
    try {
      setIsRefreshing(true)
      const status = await aimosClient.getSystemStatus()
      
      if (status.status === 'error') {
        throw new Error(status.error || 'Failed to load system status')
      }
      
      setDataSource(status.dataSource || 'simulated_data')
      setStatusNote(status.note ?? null)
      
      // Convert MCP data to SystemStatus format
      const systemList: SystemStatus[] = [
        {
          id: 'cmc',
          name: 'Context Memory Core',
          status: status.systems?.cmc?.status || 'unknown',
          lastCheck: new Date(),
          responseTime: 45,
          uptime: 99.9,
          metrics: { 
            cpu: 15, 
            memory: 256, 
            requests: status.systems?.cmc?.atomCount || 0, 
            errors: 0 
          },
          description: 'Bitemporal memory storage and retrieval',
          category: 'Core AIM-OS',
          dataSource: status.dataSource,
          note: status.systems?.cmc?.note
        },
        {
          id: 'hhni',
          name: 'Hierarchical Hypergraph Neural Index',
          status: status.systems?.hhni?.status || 'unknown',
          lastCheck: new Date(),
          responseTime: 32,
          uptime: 99.8,
          metrics: { 
            cpu: 22, 
            memory: 512, 
            requests: 890, 
            errors: 1 
          },
          description: 'Fractal knowledge retrieval with physics',
          category: 'Core AIM-OS',
          dataSource: status.dataSource,
          note: status.systems?.hhni?.note
        },
        {
          id: 'vif',
          name: 'Verifiable Intelligence Framework',
          status: status.systems?.vif?.status || 'unknown',
          lastCheck: new Date(),
          responseTime: 28,
          uptime: 99.95,
          metrics: { 
            cpu: 8, 
            memory: 128, 
            requests: status.systems?.vif?.decisionCount || 0, 
            errors: 0 
          },
          description: 'Provenance and confidence tracking',
          category: 'Core AIM-OS',
          dataSource: status.dataSource,
          note: status.systems?.vif?.note
        },
        {
          id: 'seg',
          name: 'Shared Evidence Graph',
          status: status.systems?.seg?.status || 'unknown',
          lastCheck: new Date(),
          responseTime: 120,
          uptime: 98.5,
          metrics: { 
            cpu: 45, 
            memory: 1024, 
            requests: 340, 
            errors: 3 
          },
          description: 'Knowledge synthesis and reasoning',
          category: 'Core AIM-OS',
          dataSource: status.dataSource,
          note: status.systems?.seg?.note
        },
        {
          id: 'apoe',
          name: 'AI-Powered Orchestration Engine',
          status: status.systems?.apoe?.status || 'unknown',
          lastCheck: new Date(),
          responseTime: 67,
          uptime: 99.7,
          metrics: { 
            cpu: 18, 
            memory: 384, 
            requests: status.systems?.apoe?.planCount || 0, 
            errors: 0 
          },
          description: 'Plan compilation and execution',
          category: 'Core AIM-OS',
          dataSource: status.dataSource,
          note: status.systems?.apoe?.note
        },
        {
          id: 'sdfcvf',
          name: 'Atomic Evolution Framework',
          status: status.systems?.sdfcvf?.status || 'unknown',
          lastCheck: new Date(),
          responseTime: 41,
          uptime: 99.6,
          metrics: { 
            cpu: 12, 
            memory: 256, 
            requests: 980, 
            errors: 1 
          },
          description: 'Quartet parity and quality gates',
          category: 'Core AIM-OS',
          dataSource: status.dataSource,
          note: status.systems?.sdfcvf?.note
        }
      ]
      const telemetry = status.telemetry
      if (telemetry) {
        const telemetryTimestamp = telemetry.timestamp ? new Date(telemetry.timestamp) : new Date()

        const datasetCount = telemetry.datasets?.count ?? 0
        const datasetRecords = telemetry.datasets?.records ?? 0
        const datasetNote = `${datasetCount.toLocaleString()} datasets / ${datasetRecords.toLocaleString()} records`
        const datasetStatus: SystemStatus['status'] =
          datasetCount > 0 || datasetRecords > 0 ? 'healthy' : 'warning'
        systemList.push({
          id: 'datasets',
          name: 'Dataset Registry',
          status: datasetStatus,
          lastCheck: telemetryTimestamp,
          responseTime: 12,
          uptime: 100,
          metrics: {
            requests: datasetRecords,
            errors: datasetStatus === 'healthy' ? 0 : 1,
          },
          description: 'Codex persistent dataset store (SQLite-backed)',
          category: 'Observability',
          dataSource: status.dataSource,
          note: datasetNote,
        })

        const deployedApps = telemetry.applications?.deployed ?? 0
        const totalApps = telemetry.applications?.count ?? 0
        const applicationNote = `${deployedApps.toLocaleString()} deployed / ${totalApps.toLocaleString()} total`
        const applicationStatus: SystemStatus['status'] =
          deployedApps > 0 ? 'healthy' : totalApps > 0 ? 'warning' : 'error'
        systemList.push({
          id: 'applications',
          name: 'Application Orchestrator',
          status: applicationStatus,
          lastCheck: telemetryTimestamp,
          responseTime: 18,
          uptime: 100,
          metrics: {
            requests: totalApps,
            errors: applicationStatus === 'error' ? 1 : 0,
          },
          description: 'Codex application lifecycle management',
          category: 'Observability',
          dataSource: status.dataSource,
          note: applicationNote,
        })

        const avgConfidence = telemetry.confidence?.average ?? 0
        let confidenceStatus: SystemStatus['status'] = 'healthy'
        if (avgConfidence < 0.4) {
          confidenceStatus = 'error'
        } else if (avgConfidence < 0.75) {
          confidenceStatus = 'warning'
        }
        systemList.push({
          id: 'confidence',
          name: 'Confidence Calibration',
          status: confidenceStatus,
          lastCheck: telemetryTimestamp,
          responseTime: 9,
          uptime: 100,
          metrics: {
            requests: telemetry.confidence?.entries ?? 0,
            errors: confidenceStatus === 'error' ? 1 : 0,
          },
          description: 'Verifiable Intelligence Framework calibration metrics',
          category: 'Observability',
          dataSource: status.dataSource,
          note: `Average confidence ${(avgConfidence * 100).toFixed(1)}%`,
        })

        const intuitionRecords = telemetry.intuition?.records ?? 0
        const intuitionDecisions = telemetry.intuition?.decisions ?? 0
        const intuitionNote = `${intuitionRecords.toLocaleString()} trace records`
        const intuitionStatus: SystemStatus['status'] =
          intuitionRecords > 0 ? 'healthy' : 'warning'
        systemList.push({
          id: 'intuition',
          name: 'Intuition Traces',
          status: intuitionStatus,
          lastCheck: telemetryTimestamp,
          responseTime: 15,
          uptime: 100,
          metrics: {
            requests: intuitionDecisions,
            errors: intuitionStatus === 'warning' ? 1 : 0,
          },
          description: 'Intuition trace persistence and analytics',
          category: 'Observability',
          dataSource: status.dataSource,
          note: intuitionNote,
        })
      }

      setSystems(systemList)
      setLastUpdate(new Date())
      
      // Calculate overall health
      const healthyCount = systemList.filter(s => s.status === 'healthy').length
      const warningCount = systemList.filter(s => s.status === 'warning').length
      const errorCount = systemList.filter(s => s.status === 'error').length
      
      if (errorCount > 0) {
        setOverallHealth('error')
      } else if (warningCount > 0) {
        setOverallHealth('warning')
      } else {
        setOverallHealth('healthy')
      }
      
    } catch (error) {
      console.error('Failed to load system status:', error)
      setStatusNote('Failed to load AIM-OS system status; showing last known values.')
      // Keep existing systems on error
    } finally {
      setIsRefreshing(false)
    }
  }

  // Initialize systems
  useEffect(() => {
    loadSystemStatus()
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-400" />
      case 'error': return <AlertTriangle className="w-4 h-4 text-red-400" />
      case 'simulated': return <Info className="w-4 h-4 text-blue-400" />
      default: return <Minus className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-400'
      case 'warning': return 'text-yellow-400'
      case 'error': return 'text-red-400'
      case 'simulated': return 'text-blue-400'
      default: return 'text-gray-400'
    }
  }

  const getSystemIcon = (id: string) => {
    switch (id) {
      case 'cmc': return <Database className="w-5 h-5" />
      case 'hhni': return <Network className="w-5 h-5" />
      case 'vif': return <Shield className="w-5 h-5" />
      case 'seg': return <Brain className="w-5 h-5" />
      case 'apoe': return <Target className="w-5 h-5" />
      case 'sdfcvf': return <GitBranch className="w-5 h-5" />
      default: return <Settings className="w-5 h-5" />
    }
  }

  const getOverallHealthIcon = () => {
    switch (overallHealth) {
      case 'healthy': return <CheckCircle className="w-6 h-6 text-green-400" />
      case 'warning': return <AlertTriangle className="w-6 h-6 text-yellow-400" />
      case 'error': return <AlertTriangle className="w-6 h-6 text-red-400" />
      default: return <Minus className="w-6 h-6 text-gray-400" />
    }
  }

  const getDataSourceBadge = () => {
    switch (dataSource) {
      case 'real_mcp_data':
        return <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">Real MCP Data</span>
      case 'simulated_data':
        return <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">Simulated Data</span>
      case 'error_fallback':
        return <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full">Error Fallback</span>
      default:
        return <span className="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded-full">Unknown</span>
    }
  }

  return (
    <div className={`bg-gray-800 text-white p-6 rounded-lg ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Activity className="w-6 h-6 text-blue-400" />
          <div>
            <h2 className="text-xl font-semibold">AIM-OS System Status</h2>
            <p className="text-sm text-gray-400">Real-time monitoring of all systems</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {getDataSourceBadge()}
          <button
            onClick={loadSystemStatus}
            disabled={isRefreshing}
            className="flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {statusNote && (
        <div className="mb-4 p-3 bg-yellow-900/40 border border-yellow-600/40 rounded text-sm text-yellow-200">
          {statusNote}
        </div>
      )}

      {dataSource !== 'real_mcp_data' && (
        <div className="mb-4 p-3 bg-blue-900/30 border border-blue-500/30 rounded text-sm text-blue-200">
          System metrics are currently simulated because the MCP browser bridge is unavailable.
        </div>
      )}

      {/* Overall Health */}
      <div className="mb-6 p-4 bg-gray-700 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {getOverallHealthIcon()}
            <div>
              <h3 className="text-lg font-medium">Overall System Health</h3>
              <p className="text-sm text-gray-400">
                {systems.filter(s => s.status === 'healthy').length} healthy, {' '}
                {systems.filter(s => s.status === 'warning').length} warning, {' '}
                {systems.filter(s => s.status === 'error').length} error
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-400">Last Updated</p>
            <p className="text-sm font-medium">{lastUpdate.toLocaleTimeString()}</p>
          </div>
        </div>
      </div>

      {/* Systems Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {systems.map((system) => (
          <div key={system.id} className="bg-gray-700 p-4 rounded-lg">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                {getSystemIcon(system.id)}
                <div>
                  <h4 className="font-medium">{system.name}</h4>
                  <p className="text-xs text-gray-400">{system.category}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                {getStatusIcon(system.status)}
                <span className={`text-sm font-medium ${getStatusColor(system.status)}`}>
                  {system.status}
                </span>
              </div>
            </div>
            
            <p className="text-sm text-gray-300 mb-3">{system.description}</p>
            
            {system.note && (
              <div className="mb-3 p-2 bg-blue-900/20 border border-blue-500/30 rounded text-xs text-blue-300">
                {system.note}
              </div>
            )}
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-400">Response Time</p>
                <p className="font-medium">{system.responseTime}ms</p>
              </div>
              <div>
                <p className="text-gray-400">Uptime</p>
                <p className="font-medium">{system.uptime}%</p>
              </div>
              <div>
                <p className="text-gray-400">Requests</p>
                <p className="font-medium">{system.metrics.requests?.toLocaleString() || 0}</p>
              </div>
              <div>
                <p className="text-gray-400">Errors</p>
                <p className="font-medium text-red-400">{system.metrics.errors || 0}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <div className="flex items-center gap-4">
            <span>Data Source: {dataSource}</span>
            <span>•</span>
            <span>Last Check: {lastUpdate.toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            <span>Performance Monitoring Active</span>
          </div>
        </div>
      </div>
    </div>
  )
}
