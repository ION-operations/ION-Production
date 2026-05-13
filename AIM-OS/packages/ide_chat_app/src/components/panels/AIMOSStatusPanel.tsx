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
    daemon
  } = useAIMOS()

  const [stats, setStats] = React.useState({
    cmc: { total: 0, recent: 0 },
    hhni: { searches: 0 },
    vif: { validations: 0 },
    seg: { evidence: 0 },
    apoe: { plans: 0 },
    tcs: { entries: 0 },
    cas: { health: 0 }
  })

  // Determine connection status from daemon
  const isConnected = daemon.status?.status === 'running' || daemon.health?.healthy === true

  // Load stats on mount
  React.useEffect(() => {
    const loadStats = async () => {
      try {
        // Try to get stats from each system
        if (cmc && typeof cmc.getMemoryStats === 'function') {
          const cmcStats = await cmc.getMemoryStats()
          setStats(prev => ({
            ...prev,
            cmc: { total: cmcStats?.total || 0, recent: cmcStats?.recent || 0 }
          }))
        }
      } catch (error) {
        console.error('Failed to load stats:', error)
      }
    }
    loadStats()
  }, [cmc])

  return (
    <div className="h-full flex flex-col bg-gray-900 text-gray-200 p-4">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-gray-300 flex items-center gap-2">
          <Brain className="w-5 h-5 text-blue-400" />
          AIM-OS Status
        </h2>
        <div className={`mt-2 text-sm ${isConnected ? 'text-green-400' : 'text-yellow-400'}`}>
          {isConnected ? (
            <span className="flex items-center gap-1">
              <CheckCircle className="w-4 h-4" />
              Connected
            </span>
          ) : (
            <span>Disconnected (Mock Mode)</span>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3">
        {/* CMC Status */}
        <div className="p-3 bg-gray-800 rounded border border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <Database className="w-4 h-4 text-purple-400" />
            <span className="text-sm font-medium text-gray-300">CMC</span>
          </div>
          <div className="text-xs text-gray-400">
            Total: {stats.cmc.total} | Recent: {stats.cmc.recent}
          </div>
        </div>

        {/* HHNI Status */}
        <div className="p-3 bg-gray-800 rounded border border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <Network className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-medium text-gray-300">HHNI</span>
          </div>
          <div className="text-xs text-gray-400">
            Searches: {stats.hhni.searches}
          </div>
        </div>

        {/* VIF Status */}
        <div className="p-3 bg-gray-800 rounded border border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <Shield className="w-4 h-4 text-green-400" />
            <span className="text-sm font-medium text-gray-300">VIF</span>
          </div>
          <div className="text-xs text-gray-400">
            Validations: {stats.vif.validations}
          </div>
        </div>

        {/* SEG Status */}
        <div className="p-3 bg-gray-800 rounded border border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-4 h-4 text-yellow-400" />
            <span className="text-sm font-medium text-gray-300">SEG</span>
          </div>
          <div className="text-xs text-gray-400">
            Evidence: {stats.seg.evidence}
          </div>
        </div>

        {/* APOE Status */}
        <div className="p-3 bg-gray-800 rounded border border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <Target className="w-4 h-4 text-orange-400" />
            <span className="text-sm font-medium text-gray-300">APOE</span>
          </div>
          <div className="text-xs text-gray-400">
            Plans: {stats.apoe.plans}
          </div>
        </div>

        {/* TCS Status */}
        <div className="p-3 bg-gray-800 rounded border border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-4 h-4 text-cyan-400" />
            <span className="text-sm font-medium text-gray-300">TCS</span>
          </div>
          <div className="text-xs text-gray-400">
            Entries: {stats.tcs.entries}
          </div>
        </div>

        {/* CAS Status */}
        <div className="p-3 bg-gray-800 rounded border border-gray-700">
          <div className="flex items-center gap-2 mb-2">
            <Brain className="w-4 h-4 text-pink-400" />
            <span className="text-sm font-medium text-gray-300">CAS</span>
          </div>
          <div className="text-xs text-gray-400">
            Health: {stats.cas.health}%
          </div>
        </div>
      </div>
    </div>
  )
}

