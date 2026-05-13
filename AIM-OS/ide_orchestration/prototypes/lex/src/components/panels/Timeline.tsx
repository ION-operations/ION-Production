// Timeline Panel
import React, { useEffect } from 'react'
import { Panel } from '@/types'
import { useAIMOS } from '@/hooks/useAIMOS'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

export const Timeline: React.FC<{ panel: Panel }> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const { tcs, isLoading, error } = useAIMOS()
  const entries = tcs.getSummary(5)

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
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {entries.map((entry) => (
          <div key={entry.id} style={{ padding: '8px', backgroundColor: '#374151', borderRadius: '4px', fontSize: '12px' }}>
            <div style={{ fontWeight: 'bold' }}>{entry.user_input}</div>
            <div style={{ fontSize: '11px', color: '#9CA3AF', marginTop: '4px' }}>
              {new Date(entry.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
      </div>
    </BasePanel>
  )
}

