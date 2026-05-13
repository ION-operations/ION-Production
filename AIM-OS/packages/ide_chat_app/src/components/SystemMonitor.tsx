import React, { useState } from 'react'
import { 
  Activity, 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  Clock,
  Database,
  Search,
  Shield,
  Network,
  Target,
  GitBranch
} from 'lucide-react'

interface SystemStatus {
  name: string
  status: 'healthy' | 'degraded' | 'error' | 'unknown'
  uptime: string
  metrics: {
    requests: number
    avgLatency: number
    errorRate: number
  }
  icon: React.ReactNode
  color: string
}

export const SystemMonitor: React.FC = () => {
  const [systems] = useState<SystemStatus[]>([
    {
      name: 'CMC (Context Memory Core)',
      status: 'healthy',
      uptime: '7d 14h 32m',
      metrics: { requests: 1247, avgLatency: 45, errorRate: 0 },
      icon: <Database className="w-5 h-5" />,
      color: 'text-blue-400'
    },
    {
      name: 'HHNI (Neural Index)',
      status: 'healthy',
      uptime: '7d 14h 32m',
      metrics: { requests: 893, avgLatency: 23, errorRate: 0 },
      icon: <Search className="w-5 h-5" />,
      color: 'text-green-400'
    },
    {
      name: 'VIF (Verifiable Intelligence)',
      status: 'healthy',
      uptime: '7d 14h 32m',
      metrics: { requests: 2156, avgLatency: 12, errorRate: 0 },
      icon: <Shield className="w-5 h-5" />,
      color: 'text-purple-400'
    },
    {
      name: 'SEG (Evidence Graph)',
      status: 'healthy',
      uptime: '7d 14h 32m',
      metrics: { requests: 432, avgLatency: 67, errorRate: 0 },
      icon: <Network className="w-5 h-5" />,
      color: 'text-orange-400'
    },
    {
      name: 'APOE (Orchestration Engine)',
      status: 'healthy',
      uptime: '7d 14h 32m',
      metrics: { requests: 678, avgLatency: 34, errorRate: 0 },
      icon: <Target className="w-5 h-5" />,
      color: 'text-yellow-400'
    },
    {
      name: 'SDF-CVF (Quality Framework)',
      status: 'healthy',
      uptime: '7d 14h 32m',
      metrics: { requests: 1543, avgLatency: 19, errorRate: 0 },
      icon: <GitBranch className="w-5 h-5" />,
      color: 'text-cyan-400'
    }
  ])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />
      case 'degraded':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />
      default:
        return <Clock className="w-5 h-5 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'border-green-500 bg-green-500/10'
      case 'degraded':
        return 'border-yellow-500 bg-yellow-500/10'
      case 'error':
        return 'border-red-500 bg-red-500/10'
      default:
        return 'border-gray-500 bg-gray-500/10'
    }
  }

  return (
    <div className="h-full bg-gray-800 overflow-y-auto">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 flex items-center gap-2">
        <Activity className="w-5 h-5 text-blue-400" />
        <div>
          <div className="text-white text-sm font-semibold">System Monitor</div>
          <div className="text-xs text-gray-500">Real-time AIM-OS system health</div>
        </div>
      </div>

      {/* System Cards */}
      <div className="p-4 space-y-3">
        {systems.map((system, index) => (
          <div
            key={index}
            className={`border rounded-lg p-3 ${getStatusColor(system.status)}`}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className={system.color}>
                  {system.icon}
                </div>
                <div>
                  <div className="text-sm font-semibold text-white">{system.name}</div>
                  <div className="text-xs text-gray-400 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {system.uptime}
                  </div>
                </div>
              </div>
              {getStatusIcon(system.status)}
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-3 gap-3 mt-3">
              <div className="bg-gray-700/50 rounded p-2">
                <div className="text-xs text-gray-400">Requests</div>
                <div className="text-sm font-semibold text-white">{system.metrics.requests.toLocaleString()}</div>
              </div>
              <div className="bg-gray-700/50 rounded p-2">
                <div className="text-xs text-gray-400">Avg Latency</div>
                <div className="text-sm font-semibold text-white">{system.metrics.avgLatency}ms</div>
              </div>
              <div className="bg-gray-700/50 rounded p-2">
                <div className="text-xs text-gray-400">Error Rate</div>
                <div className="text-sm font-semibold text-white">{system.metrics.errorRate}%</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Overall Status */}
      <div className="px-4 py-3 border-t border-gray-700">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-400">Overall Status</div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-green-500" />
            <span className="text-sm font-semibold text-green-500">All Systems Operational</span>
          </div>
        </div>
      </div>
    </div>
  )
}
