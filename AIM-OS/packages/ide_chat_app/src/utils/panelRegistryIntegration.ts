// Panel Registry Integration Helper
// Integrates panel registry with IDELayout
// V2 Enhancement - Week 1 Foundation

import { useState, useEffect } from 'react'
import { PanelDefinition, ALL_PANELS, getPanelById } from '../components/panelRegistry'
import { panelRegistry } from '../store/panelRegistry'

/**
 * Initialize panel registry with all panels from components/panelRegistry
 */
export function initializePanelRegistry(): void {
  ALL_PANELS.forEach(panel => {
    // Convert PanelDefinition to PanelMetadata format
    panelRegistry.register({
      id: panel.id,
      name: panel.name,
      description: panel.description,
      component: panel.component || (() => null), // Will be set by component
      defaultZone: panel.defaultZone,
      defaultSize: panel.defaultSize ? { width: panel.defaultSize } : undefined,
      minSize: panel.minSize ? { width: panel.minSize } : undefined,
      maxSize: panel.maxSize ? { width: panel.maxSize } : undefined,
      resizable: true,
      collapsible: true,
      icon: panel.icon?.name || undefined,
      category: panel.category,
      tags: []
    })
  })
}

/**
 * Get panel component by ID
 */
export function getPanelComponent(panelId: string): React.ComponentType<any> | null {
  const panelDef = getPanelById(panelId)
  return panelDef?.component || null
}

/**
 * Hook to get available panels for a zone
 */
export function usePanelsForZone(zone: 'left' | 'right' | 'bottom' | 'main'): PanelDefinition[] {
  const [panels, setPanels] = useState<PanelDefinition[]>([])

  useEffect(() => {
    const zonePanels = ALL_PANELS.filter(panel => panel.defaultZone === zone)
    setPanels(zonePanels)
  }, [zone])

  return panels
}

/**
 * Hook to get registered panels from registry
 */
export function useRegisteredPanels() {
  const [panels, setPanels] = useState<any[]>([])

  useEffect(() => {
    const registered = panelRegistry.getAllPanels()
    setPanels(registered)
  }, [])

  return panels
}

