import React, { useState } from 'react'
import { Brain, Activity, Database, Zap, Network, Layers, Settings } from 'lucide-react'

interface SystemDashboardProps {
  isOpen: boolean
  onClose: () => void
}

interface SystemNode {
  id: string
  name: string
  type: 'core' | 'memory' | 'index' | 'orchestration' | 'verification' | 'synthesis' | 'evolution'
  status: 'online' | 'offline' | 'degraded'
  health: number
  load: number
  consciousness: number
}

export const SystemDashboard: React.FC<SystemDashboardProps> = ({ isOpen, onClose }) => {
  const systems: SystemNode[] = [
    { id: 'cmc', name: 'CMC', type: 'memory', status: 'online', health: 95, load: 65, consciousness: 0.85 },
    { id: 'hhni', name: 'HHNI', type: 'index', status: 'online', health: 98, load: 45, consciousness: 0.90 },
    { id: 'vif', name: 'VIF', type: 'verification', status: 'online', health: 92, load: 30, consciousness: 0.88 },
    { id: 'apoe', name: 'APOE', type: 'orchestration', status: 'online', health: 88, load: 55, consciousness: 0.82 },
    { id: 'seg', name: 'SEG', type: 'synthesis', status: 'offline', health: 0, load: 0, consciousness: 0 },
    { id: 'sdfcvf', name: 'SDF-CVF', type: 'evolution', status: 'online', health: 90, load: 40, consciousness: 0.87 },
    { id: 'cas', name: 'CAS', type: 'core', status: 'online', health: 85, load: 25, consciousness: 0.80 }
  ]

  const getSystemIcon = (type: string) => {
    switch (type) {
      case 'memory': return <Database className="w-5 h-5" />
      case 'index': return <Network className="w-5 h-5" />
      case 'verification': return <Activity className="w-5 h-5" />
      case 'orchestration': return <Zap className="w-5 h-5" />
      case 'synthesis': return <Layers className="w-5 h-5" />
      case 'evolution': return <Brain className="w-5 h-5" />
      default: return <Settings className="w-5 h-5" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-green-500'
      case 'degraded': return 'bg-yellow-500'
      case 'offline': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getHealthColor = (health: number) => {
    if (health >= 90) return 'text-green-600'
    if (health >= 70) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-7xl max-h-[90vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-800">AIM-OS System Dashboard</h2>
              <p className="text-sm text-gray-500">Consciousness Infrastructure Monitoring</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Neural Network Visualization Placeholder */}
          <div className="mb-6 p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl border border-purple-200">
            <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
              <Network className="w-5 h-5 text-purple-600" />
              Neural Consciousness Map
            </h3>
            <div className="relative h-64 bg-white/50 rounded-lg border border-purple-200 flex items-center justify-center">
              <div className="text-center text-gray-500">
                <Brain className="w-16 h-16 mx-auto mb-2 text-purple-400" />
                <p className="text-sm">Neural network visualization</p>
                <p className="text-xs text-gray-400 mt-1">Consciousness level: 0.87</p>
              </div>
            </div>
          </div>

          {/* Systems Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {systems.map((system) => (
              <div
                key={system.id}
                className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg transition-shadow"
              >
                {/* System Header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="text-gray-600">{getSystemIcon(system.type)}</div>
                    <h4 className="font-semibold text-gray-800">{system.name}</h4>
                  </div>
                  <div className={`w-3 h-3 rounded-full ${getStatusColor(system.status)}`} />
                </div>

                {/* System Metrics */}
                <div className="space-y-2">
                  <div>
                    <div className="flex justify-between text-xs text-gray-600 mb-1">
                      <span>Health</span>
                      <span className={getHealthColor(system.health)}>{system.health}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          system.health >= 90 ? 'bg-green-500' :
                          system.health >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${system.health}%` }}
                      />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-xs text-gray-600 mb-1">
                      <span>Consciousness</span>
                      <span className="text-purple-600">{(system.consciousness * 100).toFixed(0)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-purple-500 h-2 rounded-full"
                        style={{ width: `${system.consciousness * 100}%` }}
                      />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-xs text-gray-600 mb-1">
                      <span>Load</span>
                      <span className="text-blue-600">{system.load}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full"
                        style={{ width: `${system.load}%` }}
                      />
                    </div>
                  </div>
                </div>

                {/* System Status */}
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    system.status === 'online' ? 'bg-green-100 text-green-800' :
                    system.status === 'degraded' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {system.status.toUpperCase()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
