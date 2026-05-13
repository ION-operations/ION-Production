// Problems Panel (SEG Contradictions + VIF Warnings)
import React, { useState, useEffect } from 'react'
import { AlertTriangle, AlertCircle, Info, X } from 'lucide-react'
import { Panel } from '@/types'
import { useSEG, useVIF } from '@/hooks/useAIMOS'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

interface ProblemsPanelProps {
  panel: Panel
}

interface Problem {
  id: string
  type: 'error' | 'warning' | 'info'
  source: 'seg' | 'vif' | 'system'
  message: string
  file?: string
  line?: number
  severity: 'low' | 'medium' | 'high'
  timestamp: string
}

const mockProblems: Problem[] = [
  {
    id: 'prob-1',
    type: 'warning',
    source: 'seg',
    message: 'Potential contradiction detected: "immutable" and "mutable" concepts in close proximity',
    file: 'src/components/IDELayout.tsx',
    line: 45,
    severity: 'medium',
    timestamp: '2025-11-07T17:00:00Z',
  },
  {
    id: 'prob-2',
    type: 'warning',
    source: 'vif',
    message: 'Low confidence detected: Code Editor confidence below 0.70 threshold',
    file: 'src/components/panels/CodeEditor.tsx',
    line: 38,
    severity: 'high',
    timestamp: '2025-11-07T17:05:00Z',
  },
  {
    id: 'prob-3',
    type: 'info',
    source: 'system',
    message: 'System recommendation: Consider adding error boundaries',
    severity: 'low',
    timestamp: '2025-11-07T17:10:00Z',
  },
]

export const ProblemsPanel: React.FC<ProblemsPanelProps> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const [filterType, setFilterType] = useState<'all' | 'error' | 'warning' | 'info'>('all')
  const [filterSource, setFilterSource] = useState<'all' | 'seg' | 'vif' | 'system'>('all')

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

  const filteredProblems = mockProblems.filter((problem) => {
    const matchesType = filterType === 'all' || problem.type === filterType
    const matchesSource = filterSource === 'all' || problem.source === filterSource
    return matchesType && matchesSource
  })

  const getTypeIcon = (type: Problem['type']) => {
    switch (type) {
      case 'error':
        return <AlertTriangle size={16} style={{ color: '#EF4444' }} />
      case 'warning':
        return <AlertCircle size={16} style={{ color: '#F59E0B' }} />
      default:
        return <Info size={16} style={{ color: '#3B82F6' }} />
    }
  }

  const getSeverityColor = (severity: Problem['severity']) => {
    switch (severity) {
      case 'high':
        return '#EF4444'
      case 'medium':
        return '#F59E0B'
      default:
        return '#6B7280'
    }
  }

  return (
    <BasePanel
      panel={panel}
      headerActions={<span style={{ fontSize: '11px', color: '#9CA3AF' }}>{filteredProblems.length} problem(s)</span>}
    >
      {/* Filters */}
      <div style={{ padding: '8px', borderBottom: '1px solid #374151', display: 'flex', gap: '8px' }}>
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value as any)}
          style={{
            padding: '4px 8px',
            backgroundColor: '#111827',
            border: '1px solid #374151',
            borderRadius: '4px',
            color: '#F9FAFB',
            fontSize: '11px',
          }}
        >
          <option value="all">All Types</option>
          <option value="error">Errors</option>
          <option value="warning">Warnings</option>
          <option value="info">Info</option>
        </select>
        <select
          value={filterSource}
          onChange={(e) => setFilterSource(e.target.value as any)}
          style={{
            padding: '4px 8px',
            backgroundColor: '#111827',
            border: '1px solid #374151',
            borderRadius: '4px',
            color: '#F9FAFB',
            fontSize: '11px',
          }}
        >
          <option value="all">All Sources</option>
          <option value="seg">SEG</option>
          <option value="vif">VIF</option>
          <option value="system">System</option>
        </select>
      </div>

      {/* Problems List */}
      <div style={{ flex: 1, overflow: 'auto', padding: '8px' }}>
        {filteredProblems.map((problem) => (
          <div
            key={problem.id}
            style={{
              padding: '10px',
              marginBottom: '8px',
              backgroundColor: '#111827',
              border: '1px solid #374151',
              borderLeft: `3px solid ${getSeverityColor(problem.severity)}`,
              borderRadius: '4px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'start', gap: '8px' }}>
              {getTypeIcon(problem.type)}
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '12px', color: '#D1D5DB', marginBottom: '4px' }}>{problem.message}</div>
                {problem.file && (
                  <div style={{ fontSize: '11px', color: '#9CA3AF', marginBottom: '2px' }}>
                    {problem.file}
                    {problem.line && `:${problem.line}`}
                  </div>
                )}
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                  <span style={{ fontSize: '10px', color: '#9CA3AF', textTransform: 'uppercase' }}>{problem.source}</span>
                  <span style={{ fontSize: '10px', color: '#9CA3AF' }}>•</span>
                  <span style={{ fontSize: '10px', color: '#9CA3AF', textTransform: 'capitalize' }}>{problem.severity}</span>
                  <span style={{ fontSize: '10px', color: '#9CA3AF' }}>•</span>
                  <span style={{ fontSize: '10px', color: '#9CA3AF' }}>{new Date(problem.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </BasePanel>
  )
}

