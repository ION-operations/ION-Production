/**
 * AIM-OS Dashboard
 * Comprehensive dashboard showing all AIM-OS systems and their status
 */

import React, { useState } from 'react'
import { 
  Activity, 
  Database, 
  Network, 
  Monitor, 
  Brain, 
  GitBranch, 
  Zap,
  RefreshCw,
  Settings,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  BarChart3
} from 'lucide-react'
import { AIMOSSystemVisualization } from './AIMOSSystemVisualization'

interface SystemOverview {
  id: string
  name: string
  status: 'healthy' | 'warning' | 'error' | 'offline'
  health: number
  performance: number
  lastActivity: Date
  icon: React.ReactNode
  color: string
}

export const AIMOSDashboard: React.FC = () => {
  const [_, setsystems] = useState<SystemOverview[]>([])
  const [_, setselectedSystem] = useState<string | null>(null)
  const [_, setisLoading] = useState(true)
  const [_, setlastUpdate] = useState<Date>(new Date())
  const [_, setviewMode] = useState<'overview' | 'detailed'>('overview')

  useEffect(() => {
    loadSystemOverview()
    const interval = setInterval(loadSystemOverview, 10000) // Update every 10 seconds
    return () => clearInterval(interval)
  }, [])

  const loadSystemOverview = async () => {
    setIsLoading(true)
    try {
      const systemData = generateSystemOverview()
      setSystems(systemData)
      setLastUpdate(new Date())
    } catch (error) {
      console.error('Error loading system overview:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const generateSystemOverview = (): SystemOverview[] => {
    const systemConfigs = [
      {
        id: 'cmc',
        name: 'Context Memory Core',
        icon: <Database className="w-6 h-6" />,
        color: 'blue'
      },
      {
        id: 'hhni',
        name: 'Hierarchical Hypergraph Neural Index',
        icon: <Network className="w-6 h-6" />,
        color: 'green'
      },
      {
        id: 'vif',
        name: 'Verifiable Intelligence Framework',
        icon: <Monitor className="w-6 h-6" />,
        color: 'purple'
      },
      {
        id: 'seg',
        name: 'Shared Evidence Graph',
        icon: <Brain className="w-6 h-6" />,
        color: 'orange'
      },
      {
        id: 'apoe',
        name: 'AI-Powered Orchestration Engine',
        icon: <GitBranch className="w-6 h-6" />,
        color: 'red'
      },
      {
        id: 'sdfcvf',
        name: 'Atomic Evolution Framework',
        icon: <Activity className="w-6 h-6" />,
        color: 'yellow'
      }
    ]

    return systemConfigs.map(config => ({
      ...config,
      status: Math.random() > 0.1 ? 'healthy' : Math.random() > 0.5 ? 'warning' : 'error',
      health: 0.6 + Math.random() * 0.4,
      performance: 0.5 + Math.random() * 0.5,
      lastActivity: new Date(Date.now() - Math.random() * 600000)
    }))
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-400" />
      case 'error': return <XCircle className="w-4 h-4 text-red-400" />
      case 'offline': return <XCircle className="w-4 h-4 text-gray-400" />
      default: return <AlertTriangle className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'border-green-500 bg-green-900'
      case 'warning': return 'border-yellow-500 bg-yellow-900'
      case 'error': return 'border-red-500 bg-red-900'
      case 'offline': return 'border-gray-500 bg-gray-900'
      default: return 'border-gray-500 bg-gray-900'
    }
  }

  const getColorClasses = (color: string) => {
    const colorMap: Record<string, string> = {
      blue: 'text-blue-400',
      green: 'text-green-400',
      purple: 'text-purple-400',
      orange: 'text-orange-400',
      red: 'text-red-400',
      yellow: 'text-yellow-400'
    }
    return colorMap[color] || 'text-gray-400'
  }

  const getOverallHealth = () => {
    if (systems.length === 0) return 0
    const totalHealth = systems.reduce((sum, system) => sum + system.health, 0)
    return totalHealth / systems.length
  }

  const getSystemCounts = () => {
    const counts = {
      healthy: systems.filter(s => s.status === 'healthy').length,
      warning: systems.filter(s => s.status === 'warning').length,
      error: systems.filter(s => s.status === 'error').length,
      offline: systems.filter(s => s.status === 'offline').length
    }
    return counts
  }

  const formatTime = (date: Date) => {
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)
    
    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h ago`
    const days = Math.floor(hours / 24)
    return `${days}d ago`
  }

  if (isLoading) {
    return (
      <div className="h-full bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 mx-auto mb-2 animate-spin text-blue-400" />
          <p className="text-gray-400">Loading AIM-OS systems...</p>
        </div>
      </div>
    )
  }

  if (viewMode === 'detailed' && selectedSystem) {
    return (
      <div className="h-full flex flex-col">
        <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
          <button
            onClick={() => setViewMode('overview')}
            className="text-blue-400 hover:text-blue-300 text-sm"
          >
            ← Back to Overview
          </button>
          <div className="text-white font-semibold">
            {systems.find(s => s.id === selectedSystem)?.name}
          </div>
          <div></div>
        </div>
        <div className="flex-1">
          <AIMOSSystemVisualization systemId={selectedSystem} />
        </div>
      </div>
    )
  }

  return (
    <div className="h-full bg-gray-900 flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <BarChart3 className="w-5 h-5 text-blue-400" />
          <div>
            <h2 className="text-white text-lg font-semibold">AIM-OS Dashboard</h2>
            <p className="text-gray-400 text-sm">System health and performance overview</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <div className="text-xs text-gray-400">
            <Clock className="w-3 h-3 inline mr-1" />
            {lastUpdate.toLocaleTimeString()}
          </div>
          <button
            onClick={loadSystemOverview}
            className="p-2 bg-gray-800 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button className="p-2 bg-gray-800 hover:bg-gray-700 rounded text-gray-400 hover:text-white">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Overall Health */}
      <div className="px-4 py-3 border-b border-gray-700">
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-white">
              {Math.round(getOverallHealth() * 100)}%
            </div>
            <div className="text-sm text-gray-400">Overall Health</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">
              {getSystemCounts().healthy}
            </div>
            <div className="text-sm text-gray-400">Healthy</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-400">
              {getSystemCounts().warning}
            </div>
            <div className="text-sm text-gray-400">Warning</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-400">
              {getSystemCounts().error}
            </div>
            <div className="text-sm text-gray-400">Error</div>
          </div>
        </div>
      </div>

      {/* Systems Grid */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="grid grid-cols-2 gap-4">
          {systems.map(system => (
            <div
              key={system.id}
              className={`bg-gray-800 rounded-lg p-4 border-2 cursor-pointer transition-all hover:shadow-lg ${
                getStatusColor(system.status)
              }`}
              onClick={() => {
                setSelectedSystem(system.id)
                setViewMode('detailed')
              }}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={getColorClasses(system.color)}>
                    {system.icon}
                  </div>
                  <div>
                    <h3 className="text-white font-semibold text-sm">{system.name}</h3>
                    <div className="flex items-center gap-2 text-xs">
                      {getStatusIcon(system.status)}
                      <span className="text-gray-400">{system.status.toUpperCase()}</span>
                    </div>
                  </div>
                </div>
                <div className="text-xs text-gray-400">
                  {formatTime(system.lastActivity)}
                </div>
              </div>

              <div className="space-y-2">
                <div>
                  <div className="flex justify-between text-xs text-gray-400 mb-1">
                    <span>Health</span>
                    <span>{Math.round(system.health * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-green-400 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${system.health * 100}%` }}
                    ></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-xs text-gray-400 mb-1">
                    <span>Performance</span>
                    <span>{Math.round(system.performance * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      className="bg-blue-400 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${system.performance * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                <span>Click for details</span>
                <TrendingUp className="w-3 h-3" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-gray-700">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <div>
            Last updated: {lastUpdate.toLocaleString()}
          </div>
          <div className="flex items-center gap-4">
            <span>Auto-refresh: 10s</span>
            <span>Systems: {systems.length}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
