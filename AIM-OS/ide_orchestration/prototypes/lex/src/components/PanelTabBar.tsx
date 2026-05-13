// Panel Tab Bar Component - Standard IDE Pattern
// Horizontal tab bar for main/bottom areas
import React from 'react'
import { Panel, PanelZone } from '@/types'
import { useLayoutStore } from '@/store/layoutStore'

interface PanelTabBarProps {
  zone: 'main' | 'bottom'
  panels: Panel[]
}

export const PanelTabBar: React.FC<PanelTabBarProps> = ({ zone, panels }) => {
  const { activePanels, setActivePanel } = useLayoutStore()
  const activePanelId = activePanels[zone]
  const visiblePanels = panels.sort((a, b) => a.order - b.order)

  // Initialize active panel if none selected
  React.useEffect(() => {
    if (!activePanelId && visiblePanels.length > 0) {
      setActivePanel(zone, visiblePanels[0].id)
    }
  }, [activePanelId, visiblePanels.length, zone, setActivePanel])

  if (visiblePanels.length === 0) return null

  return (
    <div
      style={{
        height: zone === 'main' ? '36px' : '32px',
        backgroundColor: '#111827',
        borderBottom: '1px solid #374151',
        display: 'flex',
        alignItems: 'center',
        padding: '0 8px',
        gap: '2px',
        overflowX: 'auto',
      }}
    >
      {visiblePanels.map((panel) => {
        const isActive = activePanelId === panel.id

        return (
          <button
            key={panel.id}
            onClick={() => setActivePanel(zone, panel.id)}
            style={{
              height: zone === 'main' ? '32px' : '28px',
              padding: '0 12px',
              display: 'flex',
              alignItems: 'center',
              backgroundColor: isActive ? '#1F2937' : 'transparent',
              border: 'none',
              borderTopLeftRadius: '4px',
              borderTopRightRadius: '4px',
              borderBottom: isActive ? '2px solid #3B82F6' : '2px solid transparent',
              cursor: 'pointer',
              color: isActive ? '#F9FAFB' : '#9CA3AF',
              fontSize: zone === 'main' ? '13px' : '12px',
              fontWeight: isActive ? 500 : 400,
              whiteSpace: 'nowrap',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              if (!isActive) {
                e.currentTarget.style.backgroundColor = '#1F2937'
                e.currentTarget.style.color = '#F9FAFB'
              }
            }}
            onMouseLeave={(e) => {
              if (!isActive) {
                e.currentTarget.style.backgroundColor = 'transparent'
                e.currentTarget.style.color = '#9CA3AF'
              }
            }}
          >
            {panel.title}
          </button>
        )
      })}
    </div>
  )
}

