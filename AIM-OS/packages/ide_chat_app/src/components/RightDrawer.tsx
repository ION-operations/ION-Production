/**
 * Right Drawer Panel Component
 * Icon button bar with drawer panels for advanced details
 */

import React, { useState, useEffect } from 'react'
import { 
  ChevronLeft, 
  ChevronRight, 
  Activity,
  Terminal,
  FileSearch,
  GitBranch,
  AlertCircle,
  BarChart3,
  Info,
  X
} from 'lucide-react'

interface DrawerPanel {
  id: string
  icon: React.ComponentType<{ className?: string }>
  label: string
  content: React.ReactNode
  badge?: number
}

interface RightDrawerProps {
  panels?: DrawerPanel[]
  defaultOpen?: boolean
  activePanel?: string | null
  onPanelChange?: (panelId: string | null) => void
}

export const RightDrawer: React.FC<RightDrawerProps> = ({ 
  panels = [], 
  defaultOpen = false,
  activePanel: externalActivePanel,
  onPanelChange 
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen)
  const [activePanel, setActivePanel] = useState<string | null>(null)

  // Sync with external activePanel prop
  useEffect(() => {
    if (externalActivePanel !== undefined) {
      setActivePanel(externalActivePanel)
      if (externalActivePanel) {
        setIsOpen(true)
      } else {
        setIsOpen(false)
      }
    }
  }, [externalActivePanel])

  useEffect(() => {
    console.log('[RightDrawer] ✅ Component mounted')
    console.log('[RightDrawer] DOM element:', document.querySelector('[data-right-drawer]'))
  }, [])

  const handlePanelClick = (panelId: string) => {
    if (activePanel === panelId) {
      // Clicking the same icon closes the drawer
      setActivePanel(null)
      setIsOpen(false)
      onPanelChange?.(null)
    } else {
      // Clicking a different icon opens it and sets active panel
      setActivePanel(panelId)
      setIsOpen(true)
      onPanelChange?.(panelId)
    }
  }

  const activePanelContent = panels.find(p => p.id === activePanel)?.content

  // Remove the old auto-open effect since we're syncing with external prop

  return (
    <div data-right-drawer="true" className="flex h-full shrink-0 relative z-20 flex-row-reverse" style={{ display: 'flex' }}>
      {/* Icon Button Bar - Always visible on the right */}
      <div className="w-12 bg-cursor-sidebar border-l border-cursor-border flex flex-col items-center py-1 gap-0.5 shrink-0" style={{ backgroundColor: '#252526', borderLeft: '1px solid #454545', width: '48px', minWidth: '48px' }}>
        {/* Toggle Button */}
        <button
          onClick={() => {
            setIsOpen(!isOpen)
            if (!isOpen && activePanel) {
              // If opening and there's an active panel, keep it
            } else if (!isOpen) {
              // If opening but no active panel, close
              setActivePanel(null)
              onPanelChange?.(null)
            }
          }}
          className="w-8 h-8 flex items-center justify-center text-cursor-text-secondary hover:text-cursor-text hover:bg-cursor-hover transition-colors"
          title={isOpen ? 'Hide drawer' : 'Show drawer'}
        >
          {isOpen ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
        <div className="flex-1" />
        
        {panels.length > 0 ? (
          panels.map((panel) => {
            const Icon = panel.icon
            const isActive = activePanel === panel.id
            return (
            <button
              key={panel.id}
              onClick={() => handlePanelClick(panel.id)}
              className={`w-8 h-8 flex items-center justify-center transition-colors relative ${
                isActive 
                  ? 'bg-cursor-selected text-cursor-text' 
                  : 'text-cursor-text-secondary hover:text-cursor-text hover:bg-cursor-hover'
              }`}
              style={{
                fontSize: '13px'
              }}
              title={panel.label}
            >
              <Icon className="w-4 h-4" />
              {panel.badge && panel.badge > 0 && (
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-red-500 text-white text-[10px] rounded-full flex items-center justify-center" style={{ fontSize: '10px' }}>
                  {panel.badge > 9 ? '9+' : panel.badge}
                </span>
              )}
            </button>
            )
          })
        ) : (
          <div className="w-8 h-8 flex items-center justify-center text-cursor-text-secondary text-[10px] border border-cursor-border bg-cursor-sidebar font-medium">
            R
          </div>
        )}
      </div>

      {/* Drawer Panel - Opens inline to the left of icon bar */}
      {isOpen && activePanelContent && (
        <div className="w-80 bg-cursor-sidebar border-l border-cursor-border flex flex-col shrink-0 cursor-scrollbar">
          {/* Panel Header */}
          <div className="h-8 px-3 border-b border-cursor-border flex items-center justify-between">
            <div className="font-medium text-sm text-cursor-text" style={{ fontSize: '13px' }}>
              {panels.find(p => p.id === activePanel)?.label}
            </div>
            <button
              onClick={() => {
                setActivePanel(null)
                setIsOpen(false)
                onPanelChange?.(null)
              }}
              className="text-cursor-text-secondary hover:text-cursor-text cursor-button"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
          
          {/* Panel Content */}
          <div className="flex-1 overflow-auto cursor-scrollbar">
            {activePanelContent}
          </div>
        </div>
      )}
    </div>
  )
}

