/**
 * Panel Manager Store - Zustand Store for Panel State Management
 * 
 * Phase 1.2: Panel Management System
 * 
 * This store manages:
 * - Panel visibility state
 * - Panel positions (left/right/bottom/main)
 * - Panel sizes
 * - Panel ordering
 * - Layout persistence (localStorage)
 * - Panel configuration
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { PanelDefinition, PanelZone, getPanelById } from './panelRegistry'

export interface PanelState {
  id: string
  zone: PanelZone
  position: number // Order in zone (0 = first)
  size: number // Percentage (0-100)
  isVisible: boolean
  isCollapsed: boolean
  isPinned?: boolean
}

export interface PanelManagerState {
  // Panel states by panel ID
  panels: Record<string, PanelState>
  
  // Zone configurations
  zones: {
    left: { visible: boolean; width: number }
    right: { visible: boolean; width: number }
    bottom: { visible: boolean; height: number }
    main: { mode: string }
  }
  
  // Layout management
  currentLayout: string | null
  savedLayouts: Record<string, {
    name: string
    description?: string
    panels: Record<string, PanelState>
    zones: PanelManagerState['zones']
    createdAt: string
    updatedAt: string
  }>
  
  // Actions
  setPanelVisible: (panelId: string, visible: boolean) => void
  setPanelZone: (panelId: string, zone: PanelZone, position?: number) => void
  setPanelSize: (panelId: string, size: number) => void
  togglePanelCollapsed: (panelId: string) => void
  togglePanelPinned: (panelId: string) => void
  setZoneVisible: (zone: PanelZone, visible: boolean) => void
  setZoneSize: (zone: PanelZone, size: number) => void
  setMainMode: (mode: string) => void
  saveLayout: (name: string, description?: string) => string
  loadLayout: (layoutId: string) => void
  deleteLayout: (layoutId: string) => void
  resetToDefault: () => void
  getPanelState: (panelId: string) => PanelState | undefined
  getVisiblePanels: (zone: PanelZone) => PanelState[]
  getPanelOrder: (zone: PanelZone) => string[]
}

const DEFAULT_ZONES = {
  left: { visible: true, width: 300 },
  right: { visible: true, width: 350 },
  bottom: { visible: false, height: 250 },
  main: { mode: 'code-editor' },
}

// Initialize default panel states from registry
function initializePanelStates(): Record<string, PanelState> {
  const states: Record<string, PanelState> = {}
  
  // Import panels dynamically to avoid circular dependency
  // For now, we'll initialize common panels
  const defaultPanels = [
    { id: 'file-explorer', zone: 'left' as PanelZone, position: 0 },
    { id: 'outline', zone: 'right' as PanelZone, position: 0 },
    { id: 'terminal', zone: 'bottom' as PanelZone, position: 0 },
  ]
  
  defaultPanels.forEach((panel, index) => {
    const panelDef = getPanelById(panel.id)
    if (panelDef) {
      states[panel.id] = {
        id: panel.id,
        zone: panel.zone,
        position: panel.position,
        size: panelDef.defaultSize || 50,
        isVisible: true,
        isCollapsed: false,
        isPinned: false,
      }
    }
  })
  
  return states
}

export const usePanelManagerStore = create<PanelManagerState>()(
  persist(
    (set, get) => ({
      panels: initializePanelStates(),
      zones: DEFAULT_ZONES,
      currentLayout: null,
      savedLayouts: {},

      setPanelVisible: (panelId, visible) => {
        set((state) => {
          const panel = state.panels[panelId]
          if (!panel) {
            // Create new panel state if it doesn't exist
            const panelDef = getPanelById(panelId)
            if (panelDef) {
              return {
                panels: {
                  ...state.panels,
                  [panelId]: {
                    id: panelId,
                    zone: panelDef.defaultZone,
                    position: 0,
                    size: panelDef.defaultSize || 50,
                    isVisible: visible,
                    isCollapsed: false,
                    isPinned: false,
                  },
                },
              }
            }
            return state
          }
          
          return {
            panels: {
              ...state.panels,
              [panelId]: {
                ...panel,
                isVisible: visible,
              },
            },
          }
        })
      },

      setPanelZone: (panelId, zone, position) => {
        set((state) => {
          const panel = state.panels[panelId]
          if (!panel) return state
          
          // Calculate position if not provided
          const newPosition = position ?? get().getVisiblePanels(zone).length
          
          return {
            panels: {
              ...state.panels,
              [panelId]: {
                ...panel,
                zone,
                position: newPosition,
              },
            },
          }
        })
      },

      setPanelSize: (panelId, size) => {
        set((state) => {
          const panel = state.panels[panelId]
          if (!panel) return state
          
          const panelDef = getPanelById(panelId)
          const minSize = panelDef?.minSize || 10
          const maxSize = panelDef?.maxSize || 90
          const clampedSize = Math.max(minSize, Math.min(maxSize, size))
          
          return {
            panels: {
              ...state.panels,
              [panelId]: {
                ...panel,
                size: clampedSize,
              },
            },
          }
        })
      },

      togglePanelCollapsed: (panelId) => {
        set((state) => {
          const panel = state.panels[panelId]
          if (!panel) return state
          
          return {
            panels: {
              ...state.panels,
              [panelId]: {
                ...panel,
                isCollapsed: !panel.isCollapsed,
              },
            },
          }
        })
      },

      togglePanelPinned: (panelId) => {
        set((state) => {
          const panel = state.panels[panelId]
          if (!panel) return state
          
          return {
            panels: {
              ...state.panels,
              [panelId]: {
                ...panel,
                isPinned: !panel.isPinned,
              },
            },
          }
        })
      },

      setZoneVisible: (zone, visible) => {
        set((state) => {
          if (zone === 'left') {
            return {
              zones: {
                ...state.zones,
                left: { ...state.zones.left, visible },
              },
            }
          }
          if (zone === 'right') {
            return {
              zones: {
                ...state.zones,
                right: { ...state.zones.right, visible },
              },
            }
          }
          if (zone === 'bottom') {
            return {
              zones: {
                ...state.zones,
                bottom: { ...state.zones.bottom, visible },
              },
            }
          }
          return state
        })
      },

      setZoneSize: (zone, size) => {
        set((state) => {
          if (zone === 'left') {
            return {
              zones: {
                ...state.zones,
                left: { ...state.zones.left, width: size },
              },
            }
          }
          if (zone === 'right') {
            return {
              zones: {
                ...state.zones,
                right: { ...state.zones.right, width: size },
              },
            }
          }
          if (zone === 'bottom') {
            return {
              zones: {
                ...state.zones,
                bottom: { ...state.zones.bottom, height: size },
              },
            }
          }
          return state
        })
      },

      setMainMode: (mode) => {
        set((state) => ({
          zones: {
            ...state.zones,
            main: { mode },
          },
        }))
      },

      saveLayout: (name, description) => {
        const layoutId = `layout_${Date.now()}`
        const now = new Date().toISOString()
        
        set((state) => ({
          currentLayout: layoutId,
          savedLayouts: {
            ...state.savedLayouts,
            [layoutId]: {
              name,
              description,
              panels: { ...state.panels },
              zones: { ...state.zones },
              createdAt: now,
              updatedAt: now,
            },
          },
        }))
        
        return layoutId
      },

      loadLayout: (layoutId) => {
        set((state) => {
          const layout = state.savedLayouts[layoutId]
          if (!layout) return state
          
          return {
            currentLayout: layoutId,
            panels: { ...layout.panels },
            zones: { ...layout.zones },
          }
        })
      },

      deleteLayout: (layoutId) => {
        set((state) => {
          const newLayouts = { ...state.savedLayouts }
          delete newLayouts[layoutId]
          
          return {
            savedLayouts: newLayouts,
            currentLayout: state.currentLayout === layoutId ? null : state.currentLayout,
          }
        })
      },

      resetToDefault: () => {
        set({
          panels: initializePanelStates(),
          zones: DEFAULT_ZONES,
          currentLayout: null,
        })
      },

      getPanelState: (panelId) => {
        return get().panels[panelId]
      },

      getVisiblePanels: (zone) => {
        const state = get()
        return Object.values(state.panels)
          .filter(panel => panel.zone === zone && panel.isVisible)
          .sort((a, b) => a.position - b.position)
      },

      getPanelOrder: (zone) => {
        return get().getVisiblePanels(zone).map(panel => panel.id)
      },
    }),
    {
      name: 'rev-ide-panel-manager', // localStorage key
      partialize: (state) => ({
        panels: state.panels,
        zones: state.zones,
        currentLayout: state.currentLayout,
        savedLayouts: state.savedLayouts,
      }),
    }
  )
)

