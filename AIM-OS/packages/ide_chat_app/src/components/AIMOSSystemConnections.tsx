/**
 * AIM-OS System Connections Component
 * Displays connections to CMC, HHNI, VIF, APOE, SEG, and their status
 */

import React, { useState, useEffect } from 'react'
import { Database, Search, Shield, Zap, Network, Activity, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { aimosService } from '../services/AIMOSService'

interface SystemConnection {
  id: string
  name: string
  icon: React.ReactNode
  status: 'connected' | 'disconnected' | 'error'
  description: string
  metrics?: {
    label: string
    value: string | number
  }[]
}

export const AIMOSSystemConnections: React.FC = () => {
  const [systems, setSystems] = useState<SystemConnection[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadSystemStatus = async () => {
      try {
        const status = await aimosService.getSystemStatus()
        
        const systemList: SystemConnection[] = [
          {
            id: 'cmc',
            name: 'CMC',
            icon: <Database className="w-5 h-5" />,
            status: status.cmc.connected ? 'connected' : 'disconnected',
            description: 'Context Memory Core - Persistent memory storage',
            metrics: status.cmc.connected ? [
              { label: 'Atoms', value: status.cmc.atoms_count.toLocaleString() }
            ] : undefined
          },
          {
            id: 'hhni',
            name: 'HHNI',
            icon: <Search className="w-5 h-5" />,
            status: status.hhni.connected ? 'connected' : 'disconnected',
            description: 'Hierarchical Hypergraph Neural Index - Semantic search',
            metrics: status.hhni.connected ? [
              { label: 'Indexed Nodes', value: status.hhni.indexed_nodes.toLocaleString() }
            ] : undefined
          },
          {
            id: 'vif',
            name: 'VIF',
            icon: <Shield className="w-5 h-5" />,
            status: status.vif.connected ? 'connected' : 'disconnected',
            description: 'Verifiable Intelligence Framework - Confidence tracking',
            metrics: status.vif.connected ? [
              { label: 'Tracked Predictions', value: status.vif.tracked_predictions.toLocaleString() },
              { label: 'ECE Score', value: status.vif.ece_score ? status.vif.ece_score.toFixed(3) : 'N/A' }
            ] : undefined
          },
          {
            id: 'apoe',
            name: 'APOE',
            icon: <Zap className="w-5 h-5" />,
            status: status.apoe.connected ? 'connected' : 'disconnected',
            description: 'AI-Powered Orchestration Engine - Plan execution',
            metrics: status.apoe.connected ? [
              { label: 'Active Plans', value: status.apoe.active_plans || 0 }
            ] : undefined
          },
          {
            id: 'seg',
            name: 'SEG',
            icon: <Network className="w-5 h-5" />,
            status: status.seg.connected ? 'connected' : 'disconnected',
            description: 'Shared Evidence Graph - Knowledge synthesis',
            metrics: status.seg.connected ? [
              { label: 'Entities', value: status.seg.entities_count.toLocaleString() },
              { label: 'Relations', value: status.seg.relations_count.toLocaleString() }
            ] : undefined
          },
          {
            id: 'daemon',
            name: 'Daemon',
            icon: <Activity className="w-5 h-5" />,
            status: status.daemon.connected ? 'connected' : 'disconnected',
            description: 'Intelligent tool selection & orchestration',
            metrics: status.daemon.connected ? [
              { label: 'Status', value: status.daemon.status }
            ] : undefined
          }
        ]

        setSystems(systemList)
      } catch (error) {
        console.error('Failed to load system status:', error)
      } finally {
        setLoading(false)
      }
    }

    loadSystemStatus()
    const interval = setInterval(loadSystemStatus, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="w-4 h-4 text-green-400" />
      case 'error':
        return <XCircle className="w-4 h-4 text-red-400" />
      default:
        return <AlertCircle className="w-4 h-4 text-yellow-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return 'border-green-500 bg-green-500/10'
      case 'error':
        return 'border-red-500 bg-red-500/10'
      default:
        return 'border-yellow-500 bg-yellow-500/10'
    }
  }

  if (loading) {
    return (
      <div className="p-4 flex items-center justify-center">
        <Activity className="w-5 h-5 animate-spin text-gray-400" />
      </div>
    )
  }

  return (
    <div className="aimos-system-connections p-4 space-y-3">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-5 h-5" />
        <h2 className="text-lg font-semibold">AIM-OS System Connections</h2>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {systems.map((system) => (
          <div
            key={system.id}
            className={`p-4 rounded-lg border-2 ${getStatusColor(system.status)} transition-all hover:opacity-80`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                {system.icon}
                <div>
                  <div className="font-semibold">{system.name}</div>
                  <div className="text-xs text-gray-400">{system.description}</div>
                </div>
              </div>
              {getStatusIcon(system.status)}
            </div>

            {system.metrics && system.metrics.length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-700">
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {system.metrics.map((metric, index) => (
                    <div key={index}>
                      <span className="text-gray-400">{metric.label}:</span>{' '}
                      <span className="font-semibold">{metric.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default AIMOSSystemConnections

