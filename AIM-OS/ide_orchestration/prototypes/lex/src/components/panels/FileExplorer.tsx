// File Explorer Panel (CMC-Integrated)
import React, { useState, useEffect } from 'react'
import { File, Folder, FolderOpen, AlertTriangle } from 'lucide-react'
import { useAIMOS } from '@/hooks/useAIMOS'
import { mockFileTree, FileNode } from '@/mockData/fileTree'
import { Panel } from '@/types'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

interface FileExplorerProps {
  panel: Panel
}

export const FileExplorer: React.FC<FileExplorerProps> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const { cmc, vif, seg, isLoading, error, isConnected } = useAIMOS()

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

  const [expanded, setExpanded] = useState<Set<string>>(new Set(['src']))
  const [selected, setSelected] = useState<string | null>(null)

  const toggleExpand = (path: string) => {
    const newExpanded = new Set(expanded)
    if (newExpanded.has(path)) {
      newExpanded.delete(path)
    } else {
      newExpanded.add(path)
    }
    setExpanded(newExpanded)
  }

  const headerActions = isConnected ? (
    <span style={{ fontSize: '10px', color: '#10B981', backgroundColor: '#374151', padding: '2px 6px', borderRadius: '4px' }}>
      AIM-OS Connected
    </span>
  ) : (
    <span style={{ fontSize: '10px', color: '#9CA3AF', backgroundColor: '#374151', padding: '2px 6px', borderRadius: '4px' }}>
      Mock Mode
    </span>
  )

  const renderNode = (node: FileNode, level: number = 0): React.ReactNode => {
    const isExpanded = expanded.has(node.path)
    const isSelected = selected === node.path
    const hasContradictions = node.contradictions && node.contradictions.length > 0
    const hasWitnesses = node.witnesses && node.witnesses.length > 0
    const hasCMCAtoms = node.cmcAtoms && node.cmcAtoms.length > 0

    return (
      <div key={node.path}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            padding: '4px 8px',
            paddingLeft: `${level * 16 + 8}px`,
            cursor: 'pointer',
            backgroundColor: isSelected ? '#374151' : 'transparent',
            color: '#F9FAFB',
            fontSize: '13px',
          }}
          onClick={() => {
            if (node.type === 'directory') {
              toggleExpand(node.path)
            } else {
              setSelected(node.path)
            }
          }}
        >
          {node.type === 'directory' ? (
            isExpanded ? <FolderOpen size={16} style={{ marginRight: '8px' }} /> : <Folder size={16} style={{ marginRight: '8px' }} />
          ) : (
            <File size={16} style={{ marginRight: '8px' }} />
          )}
          <span>{node.name}</span>
          {hasContradictions && (
            <AlertTriangle size={12} style={{ marginLeft: '8px', color: '#EF4444' }} title="Contradictions detected" />
          )}
          {hasWitnesses && (
            <span style={{ marginLeft: '8px', fontSize: '10px', color: '#10B981' }} title="VIF witnesses">
              ✓
            </span>
          )}
          {hasCMCAtoms && (
            <span style={{ marginLeft: '8px', fontSize: '10px', color: '#3B82F6' }} title="CMC atoms">
              ●
            </span>
          )}
        </div>
        {node.type === 'directory' && isExpanded && node.children && (
          <div>{node.children.map((child) => renderNode(child, level + 1))}</div>
        )}
      </div>
    )
  }

  return (
    <BasePanel panel={panel} headerActions={headerActions} isLoading={isLoading} error={error || null}>
      <div style={{ padding: '8px 0' }}>{renderNode(mockFileTree)}</div>
    </BasePanel>
  )
}
