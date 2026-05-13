// UI Editor Panel (Visual UI Builder)
import React, { useState, useEffect } from 'react'
import { Palette, Layers, Code, Eye } from 'lucide-react'
import { Panel } from '@/types'
import { useVIF } from '@/hooks/useAIMOS'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

interface UIEditorProps {
  panel: Panel
}

interface UIComponent {
  id: string
  name: string
  type: 'button' | 'input' | 'panel' | 'layout'
  props: Record<string, any>
  children?: UIComponent[]
}

const mockUIComponents: UIComponent[] = [
  {
    id: 'ui-1',
    name: 'Button',
    type: 'button',
    props: {
      label: 'Click Me',
      variant: 'primary',
      size: 'medium',
    },
  },
  {
    id: 'ui-2',
    name: 'Input',
    type: 'input',
    props: {
      placeholder: 'Enter text...',
      type: 'text',
    },
  },
  {
    id: 'ui-3',
    name: 'Panel',
    type: 'panel',
    props: {
      title: 'My Panel',
      size: 300,
    },
    children: [
      {
        id: 'ui-3-1',
        name: 'Button',
        type: 'button',
        props: {
          label: 'Action',
          variant: 'secondary',
        },
      },
    ],
  },
]

export const UIEditor: React.FC<UIEditorProps> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const [selectedComponent, setSelectedComponent] = useState<UIComponent | null>(null)
  const [viewMode, setViewMode] = useState<'design' | 'code'>('design')
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

  const headerActions = (
    <div style={{ display: 'flex', gap: '4px' }}>
      <button
        onClick={() => setViewMode('design')}
        style={{
          padding: '4px 8px',
          fontSize: '11px',
          backgroundColor: viewMode === 'design' ? '#374151' : 'transparent',
          border: '1px solid #374151',
          borderRadius: '4px',
          color: '#F9FAFB',
          cursor: 'pointer',
        }}
      >
        Design
      </button>
      <button
        onClick={() => setViewMode('code')}
        style={{
          padding: '4px 8px',
          fontSize: '11px',
          backgroundColor: viewMode === 'code' ? '#374151' : 'transparent',
          border: '1px solid #374151',
          borderRadius: '4px',
          color: '#F9FAFB',
          cursor: 'pointer',
        }}
      >
        Code
      </button>
    </div>
  )

  return (
    <BasePanel panel={panel} headerActions={headerActions}>
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Component Library */}
        <div style={{ width: '200px', borderRight: '1px solid #374151', overflow: 'auto', backgroundColor: '#111827', padding: '8px' }}>
          <div style={{ fontSize: '11px', color: '#9CA3AF', fontWeight: 'bold', marginBottom: '8px' }}>Components</div>
          {mockUIComponents.map((comp) => (
            <div
              key={comp.id}
              onClick={() => setSelectedComponent(comp)}
              style={{
                padding: '8px',
                backgroundColor: selectedComponent?.id === comp.id ? '#374151' : 'transparent',
                borderRadius: '4px',
                cursor: 'pointer',
                marginBottom: '4px',
                fontSize: '12px',
              }}
            >
              <div style={{ fontWeight: selectedComponent?.id === comp.id ? 'bold' : 'normal' }}>{comp.name}</div>
              <div style={{ fontSize: '10px', color: '#6B7280', textTransform: 'capitalize' }}>{comp.type}</div>
            </div>
          ))}
        </div>

      {/* Editor Area */}
      <div style={{ flex: 1, overflow: 'auto', padding: '16px' }}>
          {selectedComponent ? (
            <>
              <div style={{ marginBottom: '12px' }}>
                <div style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '4px' }}>{selectedComponent.name}</div>
                <div style={{ fontSize: '11px', color: '#9CA3AF', textTransform: 'capitalize' }}>{selectedComponent.type}</div>
              </div>
              {viewMode === 'design' ? (
                <div style={{ padding: '20px', backgroundColor: '#111827', borderRadius: '4px', border: '1px solid #374151' }}>
                  <div style={{ fontSize: '12px', color: '#9CA3AF', marginBottom: '12px' }}>Preview</div>
                  <div style={{ padding: '12px', backgroundColor: '#000', borderRadius: '4px' }}>
                    {selectedComponent.type === 'button' && (
                      <button
                        style={{
                          padding: '8px 16px',
                          backgroundColor: selectedComponent.props.variant === 'primary' ? '#3B82F6' : '#374151',
                          border: 'none',
                          borderRadius: '4px',
                          color: '#F9FAFB',
                          cursor: 'pointer',
                        }}
                      >
                        {selectedComponent.props.label}
                      </button>
                    )}
                    {selectedComponent.type === 'input' && (
                      <input
                        type={selectedComponent.props.type}
                        placeholder={selectedComponent.props.placeholder}
                        style={{
                          padding: '8px',
                          backgroundColor: '#374151',
                          border: '1px solid #4B5563',
                          borderRadius: '4px',
                          color: '#F9FAFB',
                          width: '100%',
                        }}
                      />
                    )}
                  </div>
                </div>
              ) : (
                <div style={{ fontFamily: 'monospace', fontSize: '12px', backgroundColor: '#000', padding: '12px', borderRadius: '4px', overflow: 'auto' }}>
                  {JSON.stringify(selectedComponent, null, 2)}
                </div>
              )}
            </>
          ) : (
            <div style={{ textAlign: 'center', color: '#9CA3AF', padding: '40px' }}>Select a component to edit</div>
          )}
        </div>
      </div>
    </BasePanel>
  )
}

