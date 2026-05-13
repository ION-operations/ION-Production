// Panel Management Hooks - V2 Feature Implementation
// Hooks for panel initialization, active panel selection, and panel controls
// Inspired by Aether's usePanelManagement pattern, adapted for DAC's panelStore

import { useEffect, useRef, useMemo } from 'react'
import { usePanelStore } from '../store/panelStore'
import type { ZoneType, PanelType } from '../store/panelStore'

/**
 * Hook for initializing default panels in IDELayout
 * 
 * Ensures all default panels are registered in the panelStore
 * and provides helper functions for panel management
 */
export function usePanelInitialization() {
  const { panels, addPanel, getPanelsByZone } = usePanelStore()
  const initialized = useRef(false)

  // Default panel configurations by zone
  const defaultPanels: Record<ZoneType, PanelType[]> = {
    left: ['file-explorer', 'memory-browser', 'system-status'],
    right: ['outline', 'context-web', 'timeline-view'],
    bottom: ['terminal', 'problems'],
    top: [] // Top bar doesn't have panels
  }

  // Initialize default panels on mount (only once)
  useEffect(() => {
    if (initialized.current) return
    
    const store = usePanelStore.getState()
    const currentPanelIds = store.panels.map(p => p.id)
    
    // Add any missing default panels
    Object.entries(defaultPanels).forEach(([zone, panelTypes]) => {
      panelTypes.forEach((panelType, index) => {
        const panelId = `panel-${panelType}`
        if (!currentPanelIds.includes(panelId)) {
          store.addPanel({
            id: panelId,
            type: panelType,
            zone: zone as ZoneType,
            size: zone === 'bottom' ? 30 : zone === 'left' ? 25 : 30,
            minSize: zone === 'bottom' ? 20 : 15,
            maxSize: zone === 'bottom' ? 50 : 40,
            visible: true,
            expanded: true,
            pinned: false,
            order: index,
            settings: {}
          })
        }
      })
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
export function useActivePanel(zone: ZoneType): string | null {
  const { getPanelsByZone } = usePanelStore()
  const panels = getPanelsByZone(zone)
  
  // Sort panels by order (lowest first), then find first visible
  const sortedPanels = [...panels].sort((a, b) => a.order - b.order)
  const visiblePanel = sortedPanels.find(p => p.visible)
  
  if (visiblePanel) {
    return visiblePanel.id
  }
  
  // If no visible panels, return first panel by order (will be hidden)
  return sortedPanels.length > 0 ? sortedPanels[0].id : null
}

/**
 * Hook for panel controls (toggle, move, resize, etc.)
 */
export function usePanelControls() {
  const { 
    togglePanelVisibility,
    togglePanelExpanded,
    togglePanelPinned,
    movePanel,
    resizePanel,
    updatePanel
  } = usePanelStore()

  return {
    toggleVisibility: togglePanelVisibility,
    toggleExpanded: togglePanelExpanded,
    togglePinned: togglePanelPinned,
    move: movePanel,
    resize: resizePanel,
    update: updatePanel
  }
}

/**
 * Hook for getting panels by zone with memoization
 */
export function usePanelsByZone(zone: ZoneType) {
  const { getPanelsByZone } = usePanelStore()
  
  return useMemo(() => {
    return getPanelsByZone(zone)
  }, [zone, getPanelsByZone])
}

/**
 * Hook for checking if a panel exists and is visible
 */
export function usePanelStatus(panelId: string) {
  const { panels } = usePanelStore()
  
  return useMemo(() => {
    const panel = panels.find(p => p.id === panelId)
    return {
      exists: !!panel,
      visible: panel?.visible ?? false,
      expanded: panel?.expanded ?? false,
      pinned: panel?.pinned ?? false,
      panel
    }
  }, [panelId, panels])
}

