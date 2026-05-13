// Component Library Panel (Reusable Components)
import React, { useState, useEffect } from 'react'
import { Package, Code, FileText, Eye } from 'lucide-react'
import { Panel } from '@/types'
import { useVIF } from '@/hooks/useAIMOS'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

interface ComponentLibraryProps {
  panel: Panel
}

interface Component {
  id: string
  name: string
  category: 'layout' | 'panel' | 'ui' | 'hook'
  description: string
  usage: string
  confidence: number
  tags: string[]
}

const mockComponents: Component[] = [
  {
    id: 'comp-1',
    name: 'IDELayout',
    category: 'layout',
    description: 'Main IDE layout component with panel management',
    usage: 'import { IDELayout } from "@/components/Layout/IDELayout"',
    confidence: 0.95,
    tags: ['layout', 'panels', 'resizable'],
  },
  {
    id: 'comp-2',
    name: 'FileExplorer',
    category: 'panel',
    description: 'File explorer panel with CMC integration',
    usage: 'import { FileExplorer } from "@/components/panels/FileExplorer"',
    confidence: 0.92,
    tags: ['panel', 'file', 'cmc'],
  },
  {
    id: 'comp-3',
    name: 'useCMC',
    category: 'hook',
    description: 'Hook for accessing CMC atoms and statistics',
    usage: 'import { useCMC } from "@/hooks/useAIMOS"',
    confidence: 0.90,
    tags: ['hook', 'cmc', 'aimos'],
  },
  {
    id: 'comp-4',
    name: 'PDASPanel',
    category: 'panel',
    description: 'Proactive Debugging & Auditing System panel',
    usage: 'import { PDASPanel } from "@/components/panels/PDASPanel"',
    confidence: 0.88,
    tags: ['panel', 'debug', 'audit', 'pdas'],
  },
]

export const ComponentLibrary: React.FC<ComponentLibraryProps> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const [selectedCategory, setSelectedCategory] = useState<'all' | Component['category']>('all')
  const [searchQuery, setSearchQuery] = useState('')

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

  const filteredComponents = mockComponents.filter((comp) => {
    const matchesCategory = selectedCategory === 'all' || comp.category === selectedCategory
    const matchesSearch =
      comp.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      comp.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      comp.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    return matchesCategory && matchesSearch
  })

  return (
    <BasePanel panel={panel}>
      {/* Search and Filter */}
      <div style={{ padding: '12px', borderBottom: '1px solid #374151', display: 'flex', gap: '8px' }}>
        <input
          type="text"
          placeholder="Search components..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            flex: 1,
            padding: '6px 8px',
            backgroundColor: '#111827',
            border: '1px solid #374151',
            borderRadius: '4px',
            color: '#F9FAFB',
            fontSize: '12px',
          }}
        />
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value as any)}
          style={{
            padding: '6px 12px',
            backgroundColor: '#111827',
            border: '1px solid #374151',
            borderRadius: '4px',
            color: '#F9FAFB',
            fontSize: '12px',
          }}
        >
          <option value="all">All Categories</option>
          <option value="layout">Layout</option>
          <option value="panel">Panel</option>
          <option value="ui">UI</option>
          <option value="hook">Hook</option>
        </select>
      </div>

      {/* Components List */}
      <div style={{ flex: 1, overflow: 'auto', padding: '12px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {filteredComponents.map((comp) => (
            <div
              key={comp.id}
              style={{
                padding: '12px',
                backgroundColor: '#111827',
                border: '1px solid #374151',
                borderRadius: '4px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {comp.category === 'hook' ? <Code size={14} /> : comp.category === 'layout' ? <FileText size={14} /> : <Eye size={14} />}
                  <span style={{ fontWeight: 'bold', fontSize: '13px' }}>{comp.name}</span>
                  <span style={{ fontSize: '10px', color: '#6B7280', textTransform: 'capitalize' }}>{comp.category}</span>
                </div>
                <span
                  style={{
                    fontSize: '10px',
                    color: comp.confidence > 0.8 ? '#10B981' : comp.confidence > 0.6 ? '#F59E0B' : '#EF4444',
                  }}
                >
                  {(comp.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <div style={{ fontSize: '12px', color: '#D1D5DB', marginBottom: '6px' }}>{comp.description}</div>
              <div style={{ fontSize: '11px', fontFamily: 'monospace', color: '#9CA3AF', marginBottom: '6px', backgroundColor: '#000', padding: '4px 8px', borderRadius: '4px' }}>
                {comp.usage}
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                {comp.tags.map((tag) => (
                  <span
                    key={tag}
                    style={{
                      fontSize: '10px',
                      color: '#9CA3AF',
                      backgroundColor: '#374151',
                      padding: '2px 6px',
                      borderRadius: '4px',
                    }}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </BasePanel>
  )
}

