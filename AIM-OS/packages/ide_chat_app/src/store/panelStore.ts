// Panel State Management Store (V2 Enhancement)
// Manages panel positions, sizes, visibility, grouping, and layout state
// Integrates with existing panelManagerStore and panelRegistry

import { create } from 'zustand'
import { PanelDefinition } from '../components/panelRegistry'

export interface PanelPosition {
  panelId: string
  zone: 'left' | 'right' | 'bottom' | 'main'
  order: number
  size?: number // Percentage or pixels
  collapsed: boolean
  visible: boolean
}

export interface PanelGroup {
  id: string
  name: string
  type: 'tabs' | 'accordion' | 'stack'
  panelIds: string[]
  collapsed: boolean
  size?: number
}

export interface SavedLayout {
  id: string
  name: string
  layout: LayoutState
  createdAt: Date
  updatedAt: Date
  isPreset: boolean
}

export interface LayoutState {
  panels: PanelPosition[]
  groups: PanelGroup[]
  zones: {
    left: { size: number; collapsed: boolean }
    right: { size: number; collapsed: boolean }
    bottom: { size: number; collapsed: boolean }
  }
}

interface PanelStore {
  // Panel state
  panels: PanelPosition[]
  groups: PanelGroup[]
  activePanels: string[]
  collapsedPanels: string[]
  
  // Layout state
  currentLayout: LayoutState
  savedLayouts: SavedLayout[]
  currentLayoutName: string | null
  
  // Actions
  registerPanel: (panel: PanelMetadata) => void
  unregisterPanel: (panelId: string) => void
  setPanelPosition: (panelId: string, zone: 'left' | 'right' | 'bottom' | 'main', order?: number) => void
  setPanelSize: (panelId: string, size: number) => void
  togglePanelCollapse: (panelId: string) => void
  togglePanelVisibility: (panelId: string) => void
  createGroup: (group: Omit<PanelGroup, 'id'>) => string
  addPanelToGroup: (groupId: string, panelId: string) => void
  removePanelFromGroup: (groupId: string, panelId: string) => void
  toggleGroupCollapse: (groupId: string) => void
  saveLayout: (name: string) => void
  loadLayout: (layoutId: string) => void
  deleteLayout: (layoutId: string) => void
  resetLayout: () => void
}

const defaultLayout: LayoutState = {
  panels: [],
  groups: [],
  zones: {
    left: { size: 300, collapsed: false },
    right: { size: 350, collapsed: false },
    bottom: { size: 250, collapsed: false }
  }
}

export const usePanelStore = create<PanelStore>((set, get) => ({
  // Initial state
  panels: [],
  groups: [],
  activePanels: [],
  collapsedPanels: [],
  currentLayout: defaultLayout,
  savedLayouts: [],
  currentLayoutName: null,

  // Register panel (works with PanelDefinition from components/panelRegistry)
  registerPanel: (panel: PanelDefinition) => {
    const existingPanel = get().panels.find(p => p.panelId === panel.id)
    if (!existingPanel) {
      set(state => ({
        panels: [...state.panels, {
          panelId: panel.id,
          zone: panel.defaultZone,
          order: state.panels.length,
          size: panel.defaultSize || 50,
          collapsed: false,
          visible: true
        }],
        activePanels: [...state.activePanels, panel.id]
      }))
    }
  },

  // Unregister panel
  unregisterPanel: (panelId: string) => {
    set(state => ({
      panels: state.panels.filter(p => p.panelId !== panelId),
      activePanels: state.activePanels.filter(id => id !== panelId),
      collapsedPanels: state.collapsedPanels.filter(id => id !== panelId),
      groups: state.groups.map(group => ({
        ...group,
        panelIds: group.panelIds.filter(id => id !== panelId)
      }))
    }))
  },

  // Set panel position
  setPanelPosition: (panelId: string, zone: 'left' | 'right' | 'bottom' | 'main', order?: number) => {
    set(state => ({
      panels: state.panels.map(p =>
        p.panelId === panelId
          ? { ...p, zone, order: order ?? p.order }
          : p
      )
    }))
  },

  // Set panel size
  setPanelSize: (panelId: string, size: number) => {
    set(state => ({
      panels: state.panels.map(p =>
        p.panelId === panelId ? { ...p, size } : p
      )
    }))
  },

  // Toggle panel collapse
  togglePanelCollapse: (panelId: string) => {
    set(state => {
      const isCollapsed = state.collapsedPanels.includes(panelId)
      return {
        collapsedPanels: isCollapsed
          ? state.collapsedPanels.filter(id => id !== panelId)
          : [...state.collapsedPanels, panelId]
      }
    })
  },

  // Toggle panel visibility
  togglePanelVisibility: (panelId: string) => {
    set(state => ({
      panels: state.panels.map(p =>
        p.panelId === panelId ? { ...p, visible: !p.visible } : p
      ),
      activePanels: state.activePanels.includes(panelId)
        ? state.activePanels.filter(id => id !== panelId)
        : [...state.activePanels, panelId]
    }))
  },

  // Create group
  createGroup: (group: Omit<PanelGroup, 'id'>) => {
    const groupId = `group-${Date.now()}`
    set(state => ({
      groups: [...state.groups, { ...group, id: groupId }]
    }))
    return groupId
  },

  // Add panel to group
  addPanelToGroup: (groupId: string, panelId: string) => {
    set(state => ({
      groups: state.groups.map(group =>
        group.id === groupId
          ? { ...group, panelIds: [...group.panelIds, panelId] }
          : group
      )
    }))
  },

  // Remove panel from group
  removePanelFromGroup: (groupId: string, panelId: string) => {
    set(state => ({
      groups: state.groups.map(group =>
        group.id === groupId
          ? { ...group, panelIds: group.panelIds.filter(id => id !== panelId) }
          : group
      )
    }))
  },

  // Toggle group collapse
  toggleGroupCollapse: (groupId: string) => {
    set(state => ({
      groups: state.groups.map(group =>
        group.id === groupId ? { ...group, collapsed: !group.collapsed } : group
      )
    }))
  },

  // Save layout
  saveLayout: (name: string) => {
    const layoutId = `layout-${Date.now()}`
    const savedLayout: SavedLayout = {
      id: layoutId,
      name,
      layout: get().currentLayout,
      createdAt: new Date(),
      updatedAt: new Date(),
      isPreset: false
    }
    set(state => ({
      savedLayouts: [...state.savedLayouts, savedLayout],
      currentLayoutName: name
    }))
    
    // Persist to localStorage
    try {
      const layouts = JSON.parse(localStorage.getItem('ide-layouts') || '[]')
      layouts.push(savedLayout)
      localStorage.setItem('ide-layouts', JSON.stringify(layouts))
    } catch (error) {
      console.warn('Failed to save layout to localStorage:', error)
    }
  },

  // Load layout
  loadLayout: (layoutId: string) => {
    const layout = get().savedLayouts.find(l => l.id === layoutId)
    if (layout) {
      set({
        currentLayout: layout.layout,
        currentLayoutName: layout.name,
        panels: layout.layout.panels,
        groups: layout.layout.groups
      })
    }
  },

  // Delete layout
  deleteLayout: (layoutId: string) => {
    set(state => ({
      savedLayouts: state.savedLayouts.filter(l => l.id !== layoutId)
    }))
    
    // Update localStorage
    try {
      const layouts = JSON.parse(localStorage.getItem('ide-layouts') || '[]')
      const updated = layouts.filter((l: SavedLayout) => l.id !== layoutId)
      localStorage.setItem('ide-layouts', JSON.stringify(updated))
    } catch (error) {
      console.warn('Failed to delete layout from localStorage:', error)
    }
  },

  // Reset layout
  resetLayout: () => {
    set({
      currentLayout: defaultLayout,
      currentLayoutName: null,
      panels: [],
      groups: [],
      activePanels: [],
      collapsedPanels: []
    })
  }
}))

// Load saved layouts from localStorage on initialization
if (typeof window !== 'undefined') {
  try {
    const savedLayouts = JSON.parse(localStorage.getItem('ide-layouts') || '[]')
    if (savedLayouts.length > 0) {
      usePanelStore.setState({ savedLayouts })
    }
  } catch (error) {
    console.warn('Failed to load layouts from localStorage:', error)
  }
}

