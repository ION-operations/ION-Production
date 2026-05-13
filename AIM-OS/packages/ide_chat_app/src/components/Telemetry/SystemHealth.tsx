/**
 * System Health Dashboard
 * Real-time system health monitoring and alerts
 */

import React, { useState, useEffect, useMemo } from 'react'
import { Activity, Cpu, HardDrive, Wifi, AlertCircle, CheckCircle, TrendingUp, TrendingDown, RefreshCw, X } from 'lucide-react'

interface HealthMetric {
  id: string
  name: string
  value: number
  unit: string
  status: 'healthy' | 'warning' | 'critical'
  threshold: { warning: number; critical: number }
  trend: 'up' | 'down' | 'stable'
  history: Array<{ timestamp: number; value: number }>
}

interface ProcessHealth {
  pid: number
  name: string
  cpu: number
  memory: number
  status: 'healthy' | 'warning' | 'critical'
}

interface ProcessInfo {
  pid: number
  name: string
  cpu: number
  memory: number
  command: string
  parentPid?: number
}

// Use existing systemAPI from SystemTools - don't redeclare global

export const SystemHealth: React.FC = () => {
  const [systemInfo, setSystemInfo] = useState<any>(null)
  const [processes, setProcesses] = useState<ProcessHealth[]>([])
  const [healthMetrics, setHealthMetrics] = useState<HealthMetric[]>([])
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [alerts, setAlerts] = useState<Array<{ id: string; message: string; severity: 'warning' | 'critical'; timestamp: string }>>([])

  // Fetch system health data
  const fetchHealthData = async () => {
    if (!window.systemAPI) return

    try {
      // Fetch system info
      const sysResult = await window.systemAPI.getSystemInfo()
      if (sysResult.success && sysResult.info) {
        setSystemInfo(sysResult.info)

        // Calculate health metrics
        const metrics: HealthMetric[] = [
          {
            id: 'cpu',
            name: 'CPU Usage',
            value: sysResult.info.cpu?.usage || 0,
            unit: '%',
            status: sysResult.info.cpu?.usage > 80 ? 'critical' : sysResult.info.cpu?.usage > 60 ? 'warning' : 'healthy',
            threshold: { warning: 60, critical: 80 },
            trend: 'stable',
            history: []
          },
          {
            id: 'memory',
            name: 'Memory Usage',
            value: sysResult.info.memory?.percentage || 0,
            unit: '%',
            status: sysResult.info.memory?.percentage > 85 ? 'critical' : sysResult.info.memory?.percentage > 70 ? 'warning' : 'healthy',
            threshold: { warning: 70, critical: 85 },
            trend: 'stable',
            history: []
          },
          {
            id: 'disk',
            name: 'Disk Usage',
            value: sysResult.info.disk?.percentage || 0,
            unit: '%',
            status: sysResult.info.disk?.percentage > 90 ? 'critical' : sysResult.info.disk?.percentage > 80 ? 'warning' : 'healthy',
            threshold: { warning: 80, critical: 90 },
            trend: 'stable',
            history: []
          }
        ]

        setHealthMetrics(metrics)

        // Generate alerts
        const newAlerts: typeof alerts = []
        metrics.forEach(metric => {
          if (metric.status === 'critical') {
            newAlerts.push({
              id: `alert-${metric.id}-${Date.now()}`,
              message: `${metric.name} is critically high: ${metric.value}${metric.unit}`,
              severity: 'critical',
              timestamp: new Date().toISOString()
            })
          } else if (metric.status === 'warning') {
            newAlerts.push({
              id: `alert-${metric.id}-${Date.now()}`,
              message: `${metric.name} is elevated: ${metric.value}${metric.unit}`,
              severity: 'warning',
              timestamp: new Date().toISOString()
            })
          }
        })

        setAlerts(prev => [...newAlerts, ...prev].slice(0, 20)) // Keep last 20 alerts
      }

      // Fetch processes
      const procResult = await window.systemAPI.getProcesses()
      if (procResult.success && procResult.processes) {
        const processHealth: ProcessHealth[] = procResult.processes.map((proc: ProcessInfo) => ({
          pid: proc.pid,
          name: proc.name,
          cpu: proc.cpu || 0,
          memory: proc.memory || 0,
          status: proc.cpu > 80 || proc.memory > 1024 * 1024 * 1024 * 2 // 2GB
            ? 'critical'
            : proc.cpu > 50 || proc.memory > 1024 * 1024 * 1024
            ? 'warning'
            : 'healthy'
        }))

        setProcesses(processHealth)
      }
    } catch (error) {
      console.error('Failed to fetch health data:', error)
    }
  }

  useEffect(() => {
    if (autoRefresh) {
      fetchHealthData()
      const interval = setInterval(fetchHealthData, 5000) // Refresh every 5 seconds
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-400 bg-green-900/20'
      case 'warning': return 'text-yellow-400 bg-yellow-900/20'
      case 'critical': return 'text-red-400 bg-red-900/20'
      default: return 'text-gray-400 bg-gray-800'
    }
  }

  // Critical processes (high CPU/memory)
  const criticalProcesses = useMemo(() => 
    processes.filter(p => p.status === 'critical').slice(0, 10),
    [processes]
  )

  // Overall health status
  const overallHealth = useMemo(() => {
    const criticalMetrics = healthMetrics.filter(m => m.status === 'critical').length
    const warningMetrics = healthMetrics.filter(m => m.status === 'warning').length
    
    if (criticalMetrics > 0) return 'critical'
    if (warningMetrics > 0) return 'warning'
    return 'healthy'
  }, [healthMetrics])

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="h-full flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-800">
        <div className="flex items-center gap-4">
          <Activity className="w-6 h-6 text-blue-400" />
          <h2 className="text-xl font-semibold">System Health Dashboard</h2>
          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusColor(overallHealth)}`}>
            {overallHealth.toUpperCase()}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-3 py-1 rounded text-sm flex items-center gap-2 ${
              autoRefresh ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            <RefreshCw className={`w-4 h-4 ${autoRefresh ? 'animate-spin' : ''}`} />
            Auto Refresh
          </button>
          <button
            onClick={fetchHealthData}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
          >
            <RefreshCw className="w-4 h-4 inline mr-1" />
            Refresh
          </button>
        </div>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="p-4 border-b border-gray-800 bg-gray-800/50">
          <div className="space-y-2">
            {alerts.slice(0, 5).map(alert => (
              <div
                key={alert.id}
                className={`p-3 rounded-lg flex items-center gap-3 ${
                  alert.severity === 'critical' ? 'bg-red-900/20 border border-red-700/50' : 'bg-yellow-900/20 border border-yellow-700/50'
                }`}
              >
                <AlertCircle className={`w-5 h-5 ${alert.severity === 'critical' ? 'text-red-400' : 'text-yellow-400'}`} />
                <div className="flex-1">
                  <div className="font-semibold">{alert.message}</div>
                  <div className="text-xs text-gray-400">{new Date(alert.timestamp).toLocaleString()}</div>
                </div>
                <button
                  onClick={() => setAlerts(prev => prev.filter(a => a.id !== alert.id))}
                  className="text-gray-400 hover:text-white"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Health Metrics */}
      <div className="p-4 border-b border-gray-800">
        <h3 className="text-sm font-semibold mb-3 text-gray-400">System Metrics</h3>
        <div className="grid grid-cols-3 gap-4">
          {healthMetrics.map(metric => (
            <div
              key={metric.id}
              className={`p-4 rounded-lg border ${getStatusColor(metric.status)}`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold">{metric.name}</span>
                {metric.trend === 'up' && <TrendingUp className="w-4 h-4 text-red-400" />}
                {metric.trend === 'down' && <TrendingDown className="w-4 h-4 text-green-400" />}
              </div>
              <div className="text-3xl font-bold mb-1">{metric.value.toFixed(1)}{metric.unit}</div>
              <div className="text-xs text-gray-400">
                Warning: {metric.threshold.warning}{metric.unit} • Critical: {metric.threshold.critical}{metric.unit}
              </div>
              {/* Progress bar */}
              <div className="mt-2 h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all ${
                    metric.status === 'critical' ? 'bg-red-500' : metric.status === 'warning' ? 'bg-yellow-500' : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min(metric.value, 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Critical Processes */}
      {criticalProcesses.length > 0 && (
        <div className="p-4 border-b border-gray-800">
          <h3 className="text-sm font-semibold mb-3 text-gray-400 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-400" />
            Critical Processes (High Resource Usage)
          </h3>
          <div className="space-y-2">
            {criticalProcesses.map(proc => (
              <div
                key={proc.pid}
                className="p-3 bg-red-900/20 border border-red-700/50 rounded-lg"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold">{proc.name}</div>
                    <div className="text-xs text-gray-400">PID: {proc.pid}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-red-400 font-semibold">CPU: {proc.cpu.toFixed(1)}%</div>
                    <div className="text-xs text-gray-400">Memory: {formatBytes(proc.memory)}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System Info */}
      {systemInfo && (
        <div className="flex-1 overflow-auto p-4">
          <h3 className="text-sm font-semibold mb-3 text-gray-400">System Information</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-gray-800 rounded-lg">
              <div className="text-xs text-gray-400 mb-1">Platform</div>
              <div className="font-semibold">{systemInfo.platform}</div>
            </div>
            <div className="p-3 bg-gray-800 rounded-lg">
              <div className="text-xs text-gray-400 mb-1">Architecture</div>
              <div className="font-semibold">{systemInfo.arch}</div>
            </div>
            <div className="p-3 bg-gray-800 rounded-lg">
              <div className="text-xs text-gray-400 mb-1">CPU Cores</div>
              <div className="font-semibold">{systemInfo.cpu?.cores || 'N/A'}</div>
            </div>
            <div className="p-3 bg-gray-800 rounded-lg">
              <div className="text-xs text-gray-400 mb-1">Total Memory</div>
              <div className="font-semibold">{formatBytes(systemInfo.memory?.total || 0)}</div>
            </div>
            <div className="p-3 bg-gray-800 rounded-lg">
              <div className="text-xs text-gray-400 mb-1">Node.js Version</div>
              <div className="font-semibold">{systemInfo.nodeVersion}</div>
            </div>
            <div className="p-3 bg-gray-800 rounded-lg">
              <div className="text-xs text-gray-400 mb-1">Electron Version</div>
              <div className="font-semibold">{systemInfo.electronVersion}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

