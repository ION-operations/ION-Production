// System Monitor Panel
import React, { useEffect } from 'react'
import { Panel } from '@/types'
import { useAIMOS } from '@/hooks/useAIMOS'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

export const SystemMonitor: React.FC<{ panel: Panel }> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const { vif, isLoading, error } = useAIMOS()

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
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {vif.confidences.map((conf) => (
          <div key={conf.task} style={{ padding: '8px', backgroundColor: '#374151', borderRadius: '4px' }}>
            <div style={{ fontWeight: 'bold', fontSize: '14px' }}>{conf.task}</div>
            <div style={{ fontSize: '12px', color: conf.confidence > 0.8 ? '#10B981' : conf.confidence > 0.6 ? '#F59E0B' : '#EF4444' }}>
              Confidence: {(conf.confidence * 100).toFixed(0)}%
            </div>
          </div>
        ))}
      </div>
    </BasePanel>
  )
}

