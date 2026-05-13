// Coding Chat Panel
import React, { useEffect } from 'react'
import { Panel } from '@/types'
import { useAIMOS } from '@/hooks/useAIMOS'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

export const CodingChat: React.FC<{ panel: Panel }> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const { vif, isLoading, error, isConnected } = useAIMOS()

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

  const confidence = vif.getConfidence('CMC Integration')

  // Convert string error to Error object if needed
  const errorObj = error ? new Error(error) : null

  return (
    <BasePanel panel={panel} isLoading={isLoading} error={errorObj}>
      <div style={{ flex: 1, overflow: 'auto', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div style={{ padding: '12px', backgroundColor: '#374151', borderRadius: '4px' }}>
          <div style={{ fontSize: '12px', marginBottom: '8px', color: '#F9FAFB' }}>User: How do I integrate CMC?</div>
          <div style={{ fontSize: '12px', color: '#9CA3AF' }}>
            AI: Use the useAIMOS hook to retrieve atoms from CMC. The unified hook provides access to all AIM-OS systems.
          </div>
          {confidence && (
            <div style={{ fontSize: '11px', color: '#10B981', marginTop: '8px' }}>
              Confidence: {(confidence.confidence * 100).toFixed(0)}%
            </div>
          )}
        </div>
      </div>
      <div style={{ padding: '12px', borderTop: '1px solid #374151', marginTop: 'auto' }}>
        <input
          type="text"
          placeholder="Type a message..."
          style={{
            width: '100%',
            padding: '8px',
            backgroundColor: '#374151',
            border: '1px solid #4B5563',
            borderRadius: '4px',
            color: '#F9FAFB',
            fontSize: '12px',
          }}
        />
      </div>
    </BasePanel>
  )
}

