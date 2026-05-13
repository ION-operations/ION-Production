// Memory Browser Panel
import React, { useEffect } from 'react'
import { Panel } from '@/types'
import { useAIMOS } from '@/hooks/useAIMOS'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

export const MemoryBrowser: React.FC<{ panel: Panel }> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const { cmc, isLoading, error } = useAIMOS()
  const stats = cmc.getStats()

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
      <div style={{ marginBottom: '16px' }}>
        <div>Total Atoms: {stats.totalAtoms}</div>
        <div>Active Sessions: {stats.activeSessions}</div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {cmc.atoms.slice(0, 5).map((atom) => (
          <div key={atom.id} style={{ padding: '8px', backgroundColor: '#374151', borderRadius: '4px', fontSize: '12px' }}>
            <div style={{ fontWeight: 'bold' }}>{atom.id}</div>
            <div style={{ fontSize: '11px', color: '#9CA3AF', marginTop: '4px' }}>{atom.content}</div>
          </div>
        ))}
      </div>
    </BasePanel>
  )
}

