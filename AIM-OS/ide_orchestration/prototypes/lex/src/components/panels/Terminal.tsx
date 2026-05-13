// Terminal Panel
import React, { useEffect } from 'react'
import { Panel } from '@/types'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

export const Terminal: React.FC<{ panel: Panel }> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()

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

  return (
    <BasePanel panel={panel} className="terminal-panel">
      <div style={{ fontFamily: 'monospace', fontSize: '12px', color: '#10B981' }}>
        <div>$ npm install</div>
        <div>Installing dependencies...</div>
        <div>$ npm run dev</div>
        <div>Starting development server...</div>
        <div style={{ marginTop: '8px' }}>$</div>
      </div>
    </BasePanel>
  )
}

