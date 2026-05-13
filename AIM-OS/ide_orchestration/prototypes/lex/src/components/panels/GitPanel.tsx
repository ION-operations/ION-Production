// Git Panel (Version Control Integration)
import React, { useState, useEffect } from 'react'
import { GitBranch, GitCommit, GitMerge, AlertCircle, CheckCircle } from 'lucide-react'
import { Panel } from '@/types'
import { useVIF } from '@/hooks/useAIMOS'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

interface GitPanelProps {
  panel: Panel
}

interface GitStatus {
  branch: string
  ahead: number
  behind: number
  changes: {
    modified: string[]
    added: string[]
    deleted: string[]
  }
}

interface GitCommit {
  hash: string
  message: string
  author: string
  timestamp: string
  confidence?: number
}

const mockGitStatus: GitStatus = {
  branch: 'main',
  ahead: 2,
  behind: 0,
  changes: {
    modified: ['src/components/panels/PDASPanel.tsx', 'src/store/layoutStore.ts'],
    added: ['src/components/panels/AgentManagement.tsx', 'src/components/panels/ProblemsPanel.tsx'],
    deleted: [],
  },
}

const mockCommits: GitCommit[] = [
  {
    hash: 'a1b2c3d',
    message: 'Add PDAS Panel implementation',
    author: 'Lex',
    timestamp: '2025-11-07T17:00:00Z',
    confidence: 0.95,
  },
  {
    hash: 'e4f5g6h',
    message: 'Add AgentManagement and ProblemsPanel',
    author: 'Lex',
    timestamp: '2025-11-07T17:30:00Z',
    confidence: 0.92,
  },
  {
    hash: 'i7j8k9l',
    message: 'Update layout store with expanded panels',
    author: 'Lex',
    timestamp: '2025-11-07T18:00:00Z',
    confidence: 0.90,
  },
]

export const GitPanel: React.FC<GitPanelProps> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const [activeTab, setActiveTab] = useState<'status' | 'commits' | 'branches'>('status')
  const { getConfidence } = useVIF()

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

  const totalChanges = mockGitStatus.changes.modified.length + mockGitStatus.changes.added.length + mockGitStatus.changes.deleted.length

  const headerActions = totalChanges > 0 ? (
    <span style={{ fontSize: '11px', color: '#F59E0B', backgroundColor: '#374151', padding: '2px 6px', borderRadius: '4px' }}>
      {totalChanges} changes
    </span>
  ) : undefined

  return (
    <BasePanel panel={panel} headerActions={headerActions}>
      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid #374151' }}>
        {(['status', 'commits', 'branches'] as const).map((tab) => (
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
        {activeTab === 'status' && (
          <div>
            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <GitBranch size={14} />
                <span style={{ fontWeight: 'bold', fontSize: '13px' }}>{mockGitStatus.branch}</span>
                {mockGitStatus.ahead > 0 && (
                  <span style={{ fontSize: '11px', color: '#10B981' }}>↑ {mockGitStatus.ahead}</span>
                )}
                {mockGitStatus.behind > 0 && (
                  <span style={{ fontSize: '11px', color: '#EF4444' }}>↓ {mockGitStatus.behind}</span>
                )}
              </div>
            </div>

            {mockGitStatus.changes.modified.length > 0 && (
              <div style={{ marginBottom: '12px' }}>
                <div style={{ fontSize: '12px', color: '#9CA3AF', marginBottom: '6px' }}>Modified ({mockGitStatus.changes.modified.length})</div>
                {mockGitStatus.changes.modified.map((file) => (
                  <div key={file} style={{ fontSize: '11px', color: '#F59E0B', padding: '4px 8px', backgroundColor: '#111827', borderRadius: '4px', marginBottom: '4px' }}>
                    M {file}
                  </div>
                ))}
              </div>
            )}

            {mockGitStatus.changes.added.length > 0 && (
              <div style={{ marginBottom: '12px' }}>
                <div style={{ fontSize: '12px', color: '#9CA3AF', marginBottom: '6px' }}>Added ({mockGitStatus.changes.added.length})</div>
                {mockGitStatus.changes.added.map((file) => (
                  <div key={file} style={{ fontSize: '11px', color: '#10B981', padding: '4px 8px', backgroundColor: '#111827', borderRadius: '4px', marginBottom: '4px' }}>
                    A {file}
                  </div>
                ))}
              </div>
            )}

            {mockGitStatus.changes.deleted.length > 0 && (
              <div style={{ marginBottom: '12px' }}>
                <div style={{ fontSize: '12px', color: '#9CA3AF', marginBottom: '6px' }}>Deleted ({mockGitStatus.changes.deleted.length})</div>
                {mockGitStatus.changes.deleted.map((file) => (
                  <div key={file} style={{ fontSize: '11px', color: '#EF4444', padding: '4px 8px', backgroundColor: '#111827', borderRadius: '4px', marginBottom: '4px' }}>
                    D {file}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'commits' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {mockCommits.map((commit) => {
              const confidence = commit.confidence || getConfidence(`Commit: ${commit.hash}`)?.confidence || 0.85
              return (
                <div
                  key={commit.hash}
                  style={{
                    padding: '10px',
                    backgroundColor: '#111827',
                    border: '1px solid #374151',
                    borderRadius: '4px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <GitCommit size={14} style={{ color: '#9CA3AF' }} />
                    <span style={{ fontSize: '11px', fontFamily: 'monospace', color: '#3B82F6' }}>{commit.hash.substring(0, 7)}</span>
                    <span style={{ fontSize: '12px', fontWeight: 'bold' }}>{commit.message}</span>
                  </div>
                  <div style={{ fontSize: '11px', color: '#9CA3AF', marginBottom: '4px' }}>
                    {commit.author} • {new Date(commit.timestamp).toLocaleString()}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '10px', color: '#9CA3AF' }}>Confidence:</span>
                    <span
                      style={{
                        fontSize: '10px',
                        color: confidence > 0.8 ? '#10B981' : confidence > 0.6 ? '#F59E0B' : '#EF4444',
                      }}
                    >
                      {(confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {activeTab === 'branches' && (
          <div style={{ fontSize: '12px', color: '#9CA3AF', textAlign: 'center', padding: '20px' }}>
            Branch management coming soon
          </div>
        )}
      </div>
    </BasePanel>
  )
}

