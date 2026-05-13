// Properties Panel (Component/Element Properties)
import React, { useState, useEffect } from 'react'
import { Settings, Code, FileText, AlertCircle } from 'lucide-react'
import { Panel } from '@/types'
import { useAIMOS } from '@/hooks/useAIMOS'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

interface PropertiesPanelProps {
  panel: Panel
}

interface Property {
  name: string
  value: string | number | boolean
  type: string
  description?: string
  confidence?: number
  contradictions?: string[]
}

const mockProperties: Property[] = [
  {
    name: 'id',
    value: 'code-editor-1',
    type: 'string',
    description: 'Unique panel identifier',
    confidence: 0.98,
  },
  {
    name: 'type',
    value: 'code-editor',
    type: 'PanelType',
    description: 'Panel type identifier',
    confidence: 0.95,
  },
  {
    name: 'zone',
    value: 'main',
    type: 'PanelZone',
    description: 'Panel zone location',
    confidence: 0.92,
  },
  {
    name: 'visible',
    value: true,
    type: 'boolean',
    description: 'Panel visibility state',
    confidence: 0.90,
  },
  {
    name: 'size',
    value: 60,
    type: 'number',
    description: 'Panel size percentage',
    confidence: 0.88,
  },
]

export const PropertiesPanel: React.FC<PropertiesPanelProps> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const [selectedProperty, setSelectedProperty] = useState<string | null>(null)
  const { vif, seg, isLoading, error } = useAIMOS()

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

  // Convert string error to Error object if needed
  const errorObj = error ? new Error(error) : null

  return (
    <BasePanel panel={panel} isLoading={isLoading} error={errorObj}>
      <div style={{ padding: '12px', overflow: 'auto' }}>
        <div style={{ fontSize: '12px', color: '#9CA3AF', marginBottom: '12px' }}>Selected: Code Editor Panel</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {mockProperties.map((prop) => {
            const contradictions = prop.contradictions || seg.detectContradictions(prop.value.toString())
            const confidence = prop.confidence || vif.getConfidence(`Property: ${prop.name}`)?.confidence || 0.85

            return (
              <div
                key={prop.name}
                onClick={() => setSelectedProperty(prop.name)}
                style={{
                  padding: '10px',
                  backgroundColor: selectedProperty === prop.name ? '#374151' : '#111827',
                  border: '1px solid #374151',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{ fontWeight: 'bold', fontSize: '13px' }}>{prop.name}</span>
                    <span style={{ fontSize: '10px', color: '#6B7280', fontFamily: 'monospace' }}>{prop.type}</span>
                  </div>
                  {contradictions.length > 0 && (
                    <AlertCircle size={14} style={{ color: '#EF4444' }} title={`Contradictions: ${contradictions.join(', ')}`} />
                  )}
                </div>
                <div style={{ fontSize: '12px', color: '#D1D5DB', marginBottom: '4px' }}>
                  <span style={{ fontFamily: 'monospace' }}>{String(prop.value)}</span>
                </div>
                {prop.description && (
                  <div style={{ fontSize: '11px', color: '#9CA3AF', marginBottom: '4px' }}>{prop.description}</div>
                )}
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
      </div>
    </BasePanel>
  )
}

