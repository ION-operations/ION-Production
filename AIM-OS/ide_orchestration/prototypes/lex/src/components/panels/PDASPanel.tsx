// PDAS Panel (Proactive Debugging & Auditing System)
import React, { useState, useEffect } from 'react'
import { AlertTriangle, CheckCircle, Clock, Play, Pause, RefreshCw, Search, Filter } from 'lucide-react'
import { Panel } from '@/types'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

interface PDASProps {
  panel: Panel
}

interface AuditEntry {
  id: string
  operation: string
  intent: string
  expectedOutcome: string
  status: 'pending' | 'in-progress' | 'success' | 'error'
  timestamp: string
  agent: string
  confidence: number
}

interface ObservabilityData {
  operationId: string
  phase: 'pre-execution' | 'execution' | 'post-execution'
  state: 'pending' | 'in-progress' | 'success' | 'error'
  checkpoints: Array<{ name: string; status: 'passed' | 'failed' | 'pending'; timestamp: string }>
  metrics: {
    startTime: string
    memoryBefore: string
    memoryAfter: string
    cpuUsage: number
  }
}

const mockAuditEntries: AuditEntry[] = [
  {
    id: 'audit-1',
    operation: 'createAtom',
    intent: 'Create new CMC atom with data',
    expectedOutcome: 'Immutable atom created with unique ID',
    status: 'success',
    timestamp: '2025-11-07T17:00:00Z',
    agent: 'Lex',
    confidence: 0.95,
  },
  {
    id: 'audit-2',
    operation: 'updatePanel',
    intent: 'Update panel configuration',
    expectedOutcome: 'Panel updated successfully',
    status: 'in-progress',
    timestamp: '2025-11-07T17:05:00Z',
    agent: 'Lex',
    confidence: 0.88,
  },
  {
    id: 'audit-3',
    operation: 'loadSystemData',
    intent: 'Load system data for display',
    expectedOutcome: 'System data loaded and displayed',
    status: 'pending',
    timestamp: '2025-11-07T17:10:00Z',
    agent: 'System',
    confidence: 0.92,
  },
]

const mockObservabilityData: ObservabilityData[] = [
  {
    operationId: 'audit-1',
    phase: 'post-execution',
    state: 'success',
    checkpoints: [
      { name: 'validation', status: 'passed', timestamp: '2025-11-07T17:00:01Z' },
      { name: 'storage', status: 'passed', timestamp: '2025-11-07T17:00:02Z' },
      { name: 'indexing', status: 'passed', timestamp: '2025-11-07T17:00:03Z' },
    ],
    metrics: {
      startTime: '2025-11-07T17:00:00Z',
      memoryBefore: '100MB',
      memoryAfter: '105MB',
      cpuUsage: 2.5,
    },
  },
  {
    operationId: 'audit-2',
    phase: 'execution',
    state: 'in-progress',
    checkpoints: [
      { name: 'validation', status: 'passed', timestamp: '2025-11-07T17:05:01Z' },
      { name: 'storage', status: 'in-progress', timestamp: '2025-11-07T17:05:02Z' },
      { name: 'indexing', status: 'pending', timestamp: '2025-11-07T17:05:03Z' },
    ],
    metrics: {
      startTime: '2025-11-07T17:05:00Z',
      memoryBefore: '105MB',
      memoryAfter: '107MB',
      cpuUsage: 3.2,
    },
  },
]

export const PDASPanel: React.FC<PDASProps> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const [activeTab, setActiveTab] = useState<'audit' | 'observability' | 'debug' | 'comparison'>('audit')
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState<'all' | 'pending' | 'in-progress' | 'success' | 'error'>('all')

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

  const filteredAuditEntries = mockAuditEntries.filter((entry) => {
    const matchesSearch = entry.operation.toLowerCase().includes(searchQuery.toLowerCase()) || entry.intent.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesFilter = filterStatus === 'all' || entry.status === filterStatus
    return matchesSearch && matchesFilter
  })

  const getStatusColor = (status: AuditEntry['status']) => {
    switch (status) {
      case 'success':
        return '#10B981'
      case 'in-progress':
        return '#F59E0B'
      case 'error':
        return '#EF4444'
      default:
        return '#6B7280'
    }
  }

  const getStatusIcon = (status: AuditEntry['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle size={14} />
      case 'in-progress':
        return <RefreshCw size={14} className="animate-spin" />
      case 'error':
        return <AlertTriangle size={14} />
      default:
        return <Clock size={14} />
    }
  }

  return (
    <BasePanel
      panel={panel}
      headerActions={
        <span style={{ fontSize: '11px', color: '#9CA3AF' }}>⭐ Proactive Debugging</span>
      }
    >
      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid #374151' }}>
        {(['audit', 'observability', 'debug', 'comparison'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '8px 16px',
              borderBottom: activeTab === tab ? '2px solid #3B82F6' : 'none',
              backgroundColor: activeTab === tab ? '#374151' : 'transparent',
              color: '#F9FAFB',
              fontSize: '12px',
              cursor: 'pointer',
              textTransform: 'capitalize',
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflow: 'auto', padding: '12px' }}>
        {activeTab === 'audit' && (
          <div>
            {/* Search and Filter */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
              <div style={{ flex: 1, position: 'relative' }}>
                <Search size={16} style={{ position: 'absolute', left: '8px', top: '50%', transform: 'translateY(-50%)', color: '#9CA3AF' }} />
                <input
                  type="text"
                  placeholder="Search operations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '6px 8px 6px 32px',
                    backgroundColor: '#111827',
                    border: '1px solid #374151',
                    borderRadius: '4px',
                    color: '#F9FAFB',
                    fontSize: '12px',
                  }}
                />
              </div>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as any)}
                style={{
                  padding: '6px 12px',
                  backgroundColor: '#111827',
                  border: '1px solid #374151',
                  borderRadius: '4px',
                  color: '#F9FAFB',
                  fontSize: '12px',
                }}
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="in-progress">In Progress</option>
                <option value="success">Success</option>
                <option value="error">Error</option>
              </select>
            </div>

            {/* Audit Entries */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {filteredAuditEntries.map((entry) => (
                <div
                  key={entry.id}
                  style={{
                    padding: '12px',
                    backgroundColor: '#111827',
                    border: '1px solid #374151',
                    borderRadius: '4px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ color: getStatusColor(entry.status) }}>{getStatusIcon(entry.status)}</span>
                      <span style={{ fontWeight: 'bold', fontSize: '13px' }}>{entry.operation}</span>
                      <span style={{ fontSize: '11px', color: '#9CA3AF' }}>by {entry.agent}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '11px', color: '#9CA3AF' }}>{new Date(entry.timestamp).toLocaleTimeString()}</span>
                      <span style={{ fontSize: '11px', color: entry.confidence > 0.8 ? '#10B981' : entry.confidence > 0.6 ? '#F59E0B' : '#EF4444' }}>
                        {(entry.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  <div style={{ fontSize: '12px', color: '#D1D5DB', marginBottom: '4px' }}>
                    <strong>Intent:</strong> {entry.intent}
                  </div>
                  <div style={{ fontSize: '12px', color: '#D1D5DB' }}>
                    <strong>Expected:</strong> {entry.expectedOutcome}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'observability' && (
          <div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {mockObservabilityData.map((data) => (
                <div
                  key={data.operationId}
                  style={{
                    padding: '12px',
                    backgroundColor: '#111827',
                    border: '1px solid #374151',
                    borderRadius: '4px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontWeight: 'bold', fontSize: '13px' }}>Operation: {data.operationId}</span>
                    <span
                      style={{
                        padding: '2px 8px',
                        borderRadius: '4px',
                        fontSize: '11px',
                        backgroundColor: data.state === 'success' ? '#10B981' : data.state === 'in-progress' ? '#F59E0B' : '#6B7280',
                        color: '#F9FAFB',
                      }}
                    >
                      {data.state}
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', color: '#D1D5DB', marginBottom: '8px' }}>
                    <strong>Phase:</strong> {data.phase} | <strong>State:</strong> {data.state}
                  </div>
                  <div style={{ marginBottom: '8px' }}>
                    <div style={{ fontSize: '12px', color: '#D1D5DB', marginBottom: '4px' }}>
                      <strong>Checkpoints:</strong>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginLeft: '16px' }}>
                      {data.checkpoints.map((checkpoint, idx) => (
                        <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px' }}>
                          <span style={{ color: checkpoint.status === 'passed' ? '#10B981' : checkpoint.status === 'failed' ? '#EF4444' : '#6B7280' }}>
                            {checkpoint.status === 'passed' ? '✓' : checkpoint.status === 'failed' ? '✗' : '○'}
                          </span>
                          <span style={{ color: '#D1D5DB' }}>{checkpoint.name}</span>
                          <span style={{ color: '#9CA3AF' }}>{new Date(checkpoint.timestamp).toLocaleTimeString()}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div style={{ fontSize: '12px', color: '#D1D5DB' }}>
                    <strong>Metrics:</strong> Memory: {data.metrics.memoryBefore} → {data.metrics.memoryAfter} | CPU: {data.metrics.cpuUsage}%
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'debug' && (
          <div>
            <div style={{ padding: '12px', backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '4px', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <Play size={16} style={{ color: '#10B981' }} />
                <span style={{ fontWeight: 'bold', fontSize: '13px' }}>Debug Console</span>
              </div>
              <div style={{ fontSize: '12px', color: '#D1D5DB', fontFamily: 'monospace', backgroundColor: '#000', padding: '8px', borderRadius: '4px' }}>
                <div style={{ color: '#10B981' }}>✓ Operation replay ready</div>
                <div style={{ color: '#10B981' }}>✓ State explorer available</div>
                <div style={{ color: '#10B981' }}>✓ Error simulation ready</div>
                <div style={{ color: '#10B981' }}>✓ Invariant checker active</div>
              </div>
            </div>
            <div style={{ fontSize: '12px', color: '#9CA3AF', fontStyle: 'italic' }}>
              Debug console provides interactive debugging interface for all operations. Features include operation replay, state exploration, error simulation, and invariant verification.
            </div>
          </div>
        )}

        {activeTab === 'comparison' && (
          <div>
            <div style={{ padding: '12px', backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '4px', marginBottom: '12px' }}>
              <div style={{ fontWeight: 'bold', fontSize: '13px', marginBottom: '8px' }}>Expected vs Actual Comparison</div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div>
                  <div style={{ fontSize: '11px', color: '#9CA3AF', marginBottom: '4px' }}>Expected Outcome</div>
                  <div style={{ fontSize: '12px', color: '#D1D5DB', padding: '8px', backgroundColor: '#000', borderRadius: '4px', fontFamily: 'monospace' }}>
                    Immutable atom created with unique ID
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', color: '#9CA3AF', marginBottom: '4px' }}>Actual Outcome</div>
                  <div style={{ fontSize: '12px', color: '#10B981', padding: '8px', backgroundColor: '#000', borderRadius: '4px', fontFamily: 'monospace' }}>
                    ✓ Atom created successfully with ID atom-123
                  </div>
                </div>
              </div>
              <div style={{ marginTop: '8px', fontSize: '11px', color: '#10B981' }}>✓ No deviations detected</div>
            </div>
            <div style={{ fontSize: '12px', color: '#9CA3AF', fontStyle: 'italic' }}>
              Compare expected outcomes (from audit logs) with actual outcomes (from observability) to detect deviations and identify root causes.
            </div>
          </div>
        )}
      </div>
    </BasePanel>
  )
}

