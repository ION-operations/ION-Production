// Panel Registry System
// Manages all panels in the IDE with registration, discovery, and metadata

export interface PanelMetadata {
  id: string
  name: string
  description: string
  component: React.ComponentType<any>
  defaultZone: 'left' | 'right' | 'bottom' | 'main'
  defaultSize?: { width?: number; height?: number }
  minSize?: { width?: number; height?: number }
  maxSize?: { width?: number; height?: number }
  resizable: boolean
  collapsible: boolean
  icon?: string
  category?: string
  tags?: string[]
}

export class PanelRegistry {
  private panels: Map<string, PanelMetadata> = new Map()
  private static instance: PanelRegistry | null = null

  private constructor() {
    // Private constructor for singleton
  }

  static getInstance(): PanelRegistry {
    if (!PanelRegistry.instance) {
      PanelRegistry.instance = new PanelRegistry()
    }
    return PanelRegistry.instance
  }

  register(panel: PanelMetadata): void {
    if (this.panels.has(panel.id)) {
      console.warn(`Panel ${panel.id} is already registered. Overwriting...`)
    }
    this.panels.set(panel.id, panel)
  }

  unregister(panelId: string): void {
    if (!this.panels.has(panelId)) {
      console.warn(`Panel ${panelId} is not registered.`)
      return
    }
    this.panels.delete(panelId)
  }

  getPanel(panelId: string): PanelMetadata | null {
    return this.panels.get(panelId) || null
  }

  getAllPanels(): PanelMetadata[] {
    return Array.from(this.panels.values())
  }

  getPanelsByZone(zone: 'left' | 'right' | 'bottom' | 'main'): PanelMetadata[] {
    return this.getAllPanels().filter(panel => panel.defaultZone === zone)
  }

  getPanelsByCategory(category: string): PanelMetadata[] {
    return this.getAllPanels().filter(panel => panel.category === category)
  }

  searchPanels(query: string): PanelMetadata[] {
    const lowerQuery = query.toLowerCase()
    return this.getAllPanels().filter(panel =>
      panel.name.toLowerCase().includes(lowerQuery) ||
      panel.description.toLowerCase().includes(lowerQuery) ||
      panel.tags?.some(tag => tag.toLowerCase().includes(lowerQuery))
    )
  }

  getPanelCount(): number {
    return this.panels.size
  }
}

// Export singleton instance
export const panelRegistry = PanelRegistry.getInstance()

