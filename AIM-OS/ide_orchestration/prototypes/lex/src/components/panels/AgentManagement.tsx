// Agent Management Panel
import React, { useState, useEffect } from 'react'
import { Users, Activity, CheckCircle, AlertCircle, Clock } from 'lucide-react'
import { Panel } from '@/types'
import { mockAgents } from '@/mockData/agents'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

interface AgentManagementProps {
  panel: Panel
}

export const AgentManagement: React.FC<AgentManagementProps> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)

  useEffect(() => {
    const handleTogglePanel = (e: CustomEvent) => {
      if (e.detail.panelId === panel.id) {
        togglePanelVisibility(panel.id)
      }
    }
    window.addEventListener('togglePanel', handleTogglePanel as EventListener)
    return () => {
      window.removeEventListener('togglePanel', handleTogglePanel as EventListener)
    }
  }, [panel.id, togglePanelVisibility])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return '#10B981'
      case 'busy':
        return '#F59E0B'
      case 'idle':
        return '#6B7280'
      default:
        return '#EF4444'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle size={14} />
      case 'busy':
        return <Activity size={14} />
      case 'idle':
        return <Clock size={14} />
      default:
        return <AlertCircle size={14} />
    }
  }

  return (
    <BasePanel
      panel={panel}
      headerActions={<Users size={16} style={{ color: '#9CA3AF' }} />}
    >
      <div style={{ padding: '8px' }}>
        {mockAgents.map((agent) => (
          <div
            key={agent.id}
            onClick={() => setSelectedAgent(agent.id)}
            style={{
              padding: '10px',
              marginBottom: '8px',
              backgroundColor: selectedAgent === agent.id ? '#374151' : '#111827',
              border: '1px solid #374151',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
              <span style={{ fontWeight: 'bold', fontSize: '13px' }}>{agent.name}</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ color: getStatusColor(agent.status) }}>{getStatusIcon(agent.status)}</span>
                <span style={{ fontSize: '11px', color: getStatusColor(agent.status) }}>{agent.status}</span>
              </div>
            </div>
            <div style={{ fontSize: '11px', color: '#9CA3AF', marginBottom: '4px' }}>{agent.role}</div>
            {agent.currentTask && (
              <div style={{ fontSize: '11px', color: '#D1D5DB', marginBottom: '4px' }}>
                <strong>Task:</strong> {agent.currentTask}
              </div>
            )}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
              <span style={{ fontSize: '10px', color: '#9CA3AF' }}>Confidence:</span>
              <span
                style={{
                  fontSize: '11px',
                  color: agent.confidenceScore && agent.confidenceScore > 0.8 ? '#10B981' : agent.confidenceScore && agent.confidenceScore > 0.6 ? '#F59E0B' : '#EF4444',
                }}
              >
                {agent.confidenceScore ? (agent.confidenceScore * 100).toFixed(0) : 'N/A'}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </BasePanel>
  )
}

