import { useEffect, useRef } from 'react'
import { usePanelStore } from '../../store/panelStore'

/**
 * Hook for initializing and managing panels
 * 
 * Ensures all default panels are registered in the panelStore
 * and provides helper functions for panel management
 */
export function usePanelManagement() {
  const { panels, addPanel, getPanelsByZone } = usePanelStore()
  const initialized = useRef(false)

  // Initialize default panels on mount (only once)
  useEffect(() => {
    if (initialized.current) return
    
    // Panel initialization logic can go here
    // For now, just mark as initialized
    initialized.current = true
  }, [])

  return {
    panels,
    getPanelsByZone,
    isInitialized: initialized.current
  }
}

/**
 * Get the active panel ID for a zone
 * Returns the first visible panel, or the first panel if none are visible
 */
export function useActivePanel(zone: 'left' | 'right' | 'bottom' | 'main'): string | null {
  const { getPanelsByZone } = usePanelStore()
  const panels = getPanelsByZone(zone)
  
  // Find first visible panel
  const visiblePanel = panels.find(p => p.visible)
  if (visiblePanel) return visiblePanel.panelId
  
  // Return first panel if none are visible
  return panels.length > 0 ? panels[0].panelId : null
}

/**
 * Hook for panel visibility management
 */
export function usePanelVisibility(panelId: string) {
  const { panels, togglePanelVisibility } = usePanelStore()
  const panel = panels.find(p => p.panelId === panelId)
  
  return {
    visible: panel?.visible ?? false,
    toggle: () => togglePanelVisibility(panelId)
  }
}

