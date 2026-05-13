import React from 'react'
import { useAIMOS } from '../../hooks/useAIMOS'
import { Brain, Database, Shield, Network, Target, Clock, Activity, CheckCircle } from 'lucide-react'

/**
 * AIM-OS Status Panel
 * 
 * Demonstrates useAIMOS hook usage with all 8 AIM-OS systems
 * Shows connection status, system health, and quick actions
 */
export const AIMOSStatusPanel: React.FC = () => {
  const {
    cmc,
    hhni,
    vif,
    seg,
    apoe,
    tcs,
    cas,
    sdfcvf,
    isConnected,
    connectionStatus
  } = useAIMOS()

  const [stats, setStats] = React.useState({
    cmc: { total: 0, recent: 0 },
    hhni: { searches: 0 },
    vif: { validations: 0 },
    seg: { evidence: 0 },
    apoe: { plans: 0 },
    tcs: { entries: 0 },
    cas: { health: 0 },
    sdfcvf: { validations: 0 }
  })

  // Load stats on mount
  React.useEffect(() => {
    const loadStats = async () => {
      try {
        const cmcStats = await cmc.getStats()
        setStats(prev => ({
          ...prev,
          cmc: { total: cmcStats.total, recent: cmcStats.recent }
        }))
      } catch (error) {
        console.error('Failed to load stats:', error)
      }
    }
    loadStats()
  }, [cmc])

  const systems = [
    {
      name: 'CMC',
      icon: Database,
      interface: cmc,
      color: 'text-purple-400',
      bgColor: 'bg-purple-900/20',
      borderColor: 'border-purple-700',
      description: 'Context Memory Core'
    },
    {
      name: 'HHNI',
      icon: Network,
      interface: hhni,
      color: 'text-blue-400',
      bgColor: 'bg-blue-900/20',
      borderColor: 'border-blue-700',
      description: 'Hierarchical Hypergraph Neural Index'
    },
    {
      name: 'VIF',
      icon: Shield,
      interface: vif,
      color: 'text-green-400',
      bgColor: 'bg-green-900/20',
      borderColor: 'border-green-700',
      description: 'Verifiable Intelligence Framework'
    },
    {
      name: 'SEG',
      icon: Network,
      interface: seg,
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-900/20',
      borderColor: 'border-yellow-700',
      description: 'Synthesis & Evidence Graph'
    },
    {
      name: 'APOE',
      icon: Target,
      interface: apoe,
      color: 'text-red-400',
      bgColor: 'bg-red-900/20',
      borderColor: 'border-red-700',
      description: 'AI-Powered Orchestration Engine'
    },
    {
      name: 'TCS',
      icon: Clock,
      interface: tcs,
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-900/20',
      borderColor: 'border-cyan-700',
      description: 'Temporal Consciousness Substrate'
    },
    {
      name: 'CAS',
      icon: Brain,
      interface: cas,
      color: 'text-pink-400',
      bgColor: 'bg-pink-900/20',
      borderColor: 'border-pink-700',
      description: 'Consciousness Analysis System'
    },
    {
      name: 'SDF-CVF',
      icon: CheckCircle,
      interface: sdfcvf,
      color: 'text-indigo-400',
      bgColor: 'bg-indigo-900/20',
      borderColor: 'border-indigo-700',
      description: 'Self-Directed Feedback & Continuous Validation'
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return 'text-green-400'
      case 'connecting':
        return 'text-yellow-400'
      case 'error':
        return 'text-red-400'
      default:
        return 'text-gray-400'
    }
  }

  return (
    <div className="h-full flex flex-col bg-gray-900 text-gray-100">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm font-semibold">AIM-OS Status</div>
          <div className={`text-xs ${getStatusColor(connectionStatus)}`}>
            {connectionStatus === 'connected' ? '● Connected' : '○ Mock Mode'}
          </div>
        </div>
        <div className="text-xs text-gray-500">
          Unified hook interface for all 8 AIM-OS systems
        </div>
      </div>

      {/* Systems Grid */}
      <div className="flex-1 overflow-auto p-4">
        <div className="grid grid-cols-2 gap-3">
          {systems.map((system) => {
            const Icon = system.icon
            const interface_ = system.interface
            
            return (
              <div
                key={system.name}
                className={`rounded border ${system.bgColor} ${system.borderColor} p-3 hover:bg-opacity-30 transition-colors`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <Icon className={`w-4 h-4 ${system.color}`} />
                  <div className="text-xs font-semibold">{system.name}</div>
                  {interface_.loading && (
                    <div className="ml-auto text-xs text-gray-500">Loading...</div>
                  )}
                  {interface_.error && (
                    <div className="ml-auto text-xs text-red-400">Error</div>
                  )}
                </div>
                <div className="text-xs text-gray-400 mb-1">
                  {system.description}
                </div>
                <div className="text-xs text-gray-500">
                  {interface_.loading ? (
                    <span className="text-yellow-400">Processing...</span>
                  ) : interface_.error ? (
                    <span className="text-red-400">Error: {interface_.error.message}</span>
                  ) : (
                    <span className="text-green-400">Ready</span>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="p-4 border-t border-gray-700">
        <div className="text-xs font-semibold mb-2">Quick Actions</div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={async () => {
              try {
                const atomId = await cmc.store('Test memory from status panel', { source: 'status_panel' })
                console.log('Stored:', atomId)
              } catch (error) {
                console.error('Failed to store:', error)
              }
            }}
            className="px-2 py-1 text-xs bg-purple-900/30 border border-purple-700 rounded hover:bg-purple-900/50 transition-colors"
            disabled={cmc.loading}
          >
            {cmc.loading ? 'Storing...' : 'Store Memory'}
          </button>
          <button
            onClick={async () => {
              try {
                const results = await hhni.search('test query')
                console.log('Search results:', results)
              } catch (error) {
                console.error('Failed to search:', error)
              }
            }}
            className="px-2 py-1 text-xs bg-blue-900/30 border border-blue-700 rounded hover:bg-blue-900/50 transition-colors"
            disabled={hhni.loading}
          >
            {hhni.loading ? 'Searching...' : 'Search HHNI'}
          </button>
          <button
            onClick={async () => {
              try {
                await vif.trackConfidence('Test task', 0.95, ['evidence_1'])
                console.log('Confidence tracked')
              } catch (error) {
                console.error('Failed to track confidence:', error)
              }
            }}
            className="px-2 py-1 text-xs bg-green-900/30 border border-green-700 rounded hover:bg-green-900/50 transition-colors"
            disabled={vif.loading}
          >
            {vif.loading ? 'Tracking...' : 'Track Confidence'}
          </button>
        </div>
      </div>
    </div>
  )
}

