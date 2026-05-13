// Outline Panel (Code Structure Navigation)
import React, { useState, useEffect } from 'react'
import { FileText, ChevronRight, ChevronDown, Code, FunctionSquare, Box } from 'lucide-react'
import { Panel } from '@/types'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

interface OutlinePanelProps {
  panel: Panel
}

interface OutlineNode {
  id: string
  name: string
  type: 'file' | 'function' | 'class' | 'interface' | 'variable'
  line: number
  children?: OutlineNode[]
}

const mockOutline: OutlineNode[] = [
  {
    id: 'file-1',
    name: 'IDELayout.tsx',
    type: 'file',
    line: 1,
    children: [
      {
        id: 'comp-1',
        name: 'IDELayout',
        type: 'class',
        line: 38,
        children: [
          {
            id: 'func-1',
            name: 'renderPanel',
            type: 'function',
            line: 45,
          },
          {
            id: 'func-2',
            name: 'handleClosePanel',
            type: 'function',
            line: 60,
          },
        ],
      },
    ],
  },
  {
    id: 'file-2',
    name: 'CodeEditor.tsx',
    type: 'file',
    line: 1,
    children: [
      {
        id: 'comp-2',
        name: 'CodeEditor',
        type: 'class',
        line: 36,
        children: [
          {
            id: 'func-3',
            name: 'handleEditorChange',
            type: 'function',
            line: 41,
          },
        ],
      },
    ],
  },
]

export const OutlinePanel: React.FC<OutlinePanelProps> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const [expanded, setExpanded] = useState<Set<string>>(new Set(['file-1', 'comp-1']))

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

  const toggleExpand = (id: string) => {
    const newExpanded = new Set(expanded)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpanded(newExpanded)
  }

  const getTypeIcon = (type: OutlineNode['type']) => {
    switch (type) {
      case 'file':
        return <FileText size={14} />
      case 'function':
        return <FunctionSquare size={14} />
      case 'class':
        return <Box size={14} />
      default:
        return <Code size={14} />
    }
  }

  const renderNode = (node: OutlineNode, level: number = 0): React.ReactNode => {
    const isExpanded = expanded.has(node.id)
    const hasChildren = node.children && node.children.length > 0

    return (
      <div key={node.id}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            padding: '4px 8px',
            paddingLeft: `${level * 16 + 8}px`,
            cursor: 'pointer',
            color: '#F9FAFB',
            fontSize: '12px',
          }}
          onClick={() => {
            if (hasChildren) {
              toggleExpand(node.id)
            }
          }}
        >
          {hasChildren ? (
            isExpanded ? (
              <ChevronDown size={14} style={{ marginRight: '4px' }} />
            ) : (
              <ChevronRight size={14} style={{ marginRight: '4px' }} />
            )
          ) : (
            <span style={{ width: '14px', marginRight: '4px' }} />
          )}
          <span style={{ marginRight: '6px', color: '#9CA3AF' }}>{getTypeIcon(node.type)}</span>
          <span style={{ flex: 1 }}>{node.name}</span>
          <span style={{ fontSize: '10px', color: '#6B7280' }}>{node.line}</span>
        </div>
        {hasChildren && isExpanded && (
          <div>{node.children!.map((child) => renderNode(child, level + 1))}</div>
        )}
      </div>
    )
  }

  return (
    <BasePanel panel={panel}>
      <div style={{ padding: '8px 0' }}>{mockOutline.map((node) => renderNode(node))}</div>
    </BasePanel>
  )
}

