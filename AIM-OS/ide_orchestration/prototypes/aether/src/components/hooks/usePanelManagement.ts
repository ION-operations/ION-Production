import { useEffect, useRef } from 'react'
import { usePanelStore } from '../../stores/panelStore'
import { DEFAULT_PANEL_CONFIGS } from '../panelMappings'
import type { PanelZone, PanelId } from '../../stores/panelStore'

/**
 * Hook for initializing and managing panels in AetherIDELayout
 * 
 * Ensures all default panels are registered in the panelStore
 * and provides helper functions for panel management
 */
export function usePanelInitialization() {
  const { panels, addPanel, getPanelsByZone } = usePanelStore()
  const initialized = useRef(false)

  // Initialize default panels on mount (only once)
  useEffect(() => {
    if (initialized.current) return
    
    const store = usePanelStore.getState()
    const currentPanels = Object.keys(store.panels)
    const defaultPanelIds = Object.keys(DEFAULT_PANEL_CONFIGS)

    // Add any missing default panels
    defaultPanelIds.forEach(panelId => {
      if (!currentPanels.includes(panelId)) {
        const config = DEFAULT_PANEL_CONFIGS[panelId as keyof typeof DEFAULT_PANEL_CONFIGS]
        if (config) {
          store.addPanel(config)
        }
      }
    })
    
    initialized.current = true
  }, []) // Only run once on mount

  return {
    getPanelsByZone,
    panels
  }
}

/**
 * Get the active panel ID for a zone
 * Returns the first visible panel sorted by order (lowest order first), or the first panel if none are visible
 */
export function useActivePanel(zone: PanelZone): PanelId | null {
  const { getPanelsByZone } = usePanelStore()
  const panels = getPanelsByZone(zone)
  
  // Sort panels by order (lowest first), then find first visible
  const sortedPanels = [...panels].sort((a, b) => a.order - b.order)
  const visiblePanel = sortedPanels.find(p => p.visible)
  
  if (visiblePanel) {
    console.log(`[AETHER] useActivePanel(${zone}) returning visible (order ${visiblePanel.order}):`, visiblePanel.id)
    return visiblePanel.id
  }
  
  // If no visible panels, return first panel by order (will be hidden)
  const firstPanel = sortedPanels.length > 0 ? sortedPanels[0].id : null
  console.log(`[AETHER] useActivePanel(${zone}) returning first (hidden, order ${sortedPanels[0]?.order}):`, firstPanel)
  return firstPanel
}

/**
 * Hook for panel controls (toggle, move, etc.)
 */
export function usePanelControls() {
  const { togglePanel, movePanel, setPanelSize, updatePanel } = usePanelStore()

  return {
    togglePanel,
    movePanel,
    setPanelSize,
    updatePanel
  }
}

