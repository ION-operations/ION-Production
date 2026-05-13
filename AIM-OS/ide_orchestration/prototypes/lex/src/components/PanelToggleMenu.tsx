// Panel Toggle Menu Component
import React, { useState } from 'react'
import { Menu, X } from 'lucide-react'
import { useLayoutStore } from '@/store/layoutStore'

export const PanelToggleMenu: React.FC = () => {
  const { panels, togglePanelVisibility } = useLayoutStore()
  const [isOpen, setIsOpen] = useState(false)

  const panelsByZone = {
    left: panels.filter((p) => p.zone === 'left'),
    main: panels.filter((p) => p.zone === 'main'),
    right: panels.filter((p) => p.zone === 'right'),
    bottom: panels.filter((p) => p.zone === 'bottom'),
  }

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        style={{
          position: 'fixed',
          top: '50px',
          left: '20px',
          padding: '8px 12px',
          backgroundColor: '#3B82F6',
          color: '#F9FAFB',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          fontSize: '13px',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
        }}
        title="Toggle Panels"
      >
        <Menu size={16} />
        Panels
      </button>
    )
  }

  return (
    <div
      style={{
        position: 'fixed',
        top: '50px',
        left: '20px',
        width: '280px',
        maxHeight: '80vh',
        backgroundColor: '#1F2937',
        border: '1px solid #374151',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
        zIndex: 1001,
        padding: '16px',
        overflowY: 'auto',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ color: '#F9FAFB', fontSize: '16px', fontWeight: 'bold', margin: 0 }}>Toggle Panels</h3>
        <button
          onClick={() => setIsOpen(false)}
          style={{
            background: 'none',
            border: 'none',
            color: '#9CA3AF',
            cursor: 'pointer',
            padding: '4px',
          }}
          aria-label="Close"
        >
          <X size={18} />
        </button>
      </div>

      {Object.entries(panelsByZone).map(([zone, zonePanels]) => (
        <div key={zone} style={{ marginBottom: '20px' }}>
          <div
            style={{
              color: '#9CA3AF',
              fontSize: '12px',
              fontWeight: 'bold',
              textTransform: 'uppercase',
              marginBottom: '8px',
              paddingBottom: '4px',
              borderBottom: '1px solid #374151',
            }}
          >
            {zone}
          </div>
          {zonePanels.map((panel) => (
            <label
              key={panel.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                padding: '8px',
                marginBottom: '4px',
                cursor: 'pointer',
                borderRadius: '4px',
                backgroundColor: panel.visible ? '#374151' : 'transparent',
              }}
              onMouseEnter={(e) => {
                if (!panel.visible) {
                  e.currentTarget.style.backgroundColor = '#111827'
                }
              }}
              onMouseLeave={(e) => {
                if (!panel.visible) {
                  e.currentTarget.style.backgroundColor = 'transparent'
                }
              }}
            >
              <input
                type="checkbox"
                checked={panel.visible}
                onChange={() => togglePanelVisibility(panel.id)}
                style={{
                  marginRight: '8px',
                  cursor: 'pointer',
                }}
              />
              <span style={{ color: '#F9FAFB', fontSize: '13px' }}>{panel.title}</span>
            </label>
          ))}
        </div>
      ))}
    </div>
  )
}

