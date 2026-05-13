import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

// Panel State Types
export type PanelZone = 'left' | 'right' | 'top' | 'bottom' | 'main'
export type PanelId = string

export interface PanelConfig {
  id: PanelId
  zone: PanelZone
  size: number // Percentage or pixels
  minSize?: number
  maxSize?: number
  visible: boolean
  order: number
}

export interface LayoutState {
  panels: Record<PanelId, PanelConfig>
  activePanels: Record<PanelZone, PanelId[]>
  layoutPresets: Record<string, LayoutPreset>
  currentPreset?: string
}

export interface LayoutPreset {
  name: string
  description: string
  panels: Record<PanelId, PanelConfig>
  createdAt: string
}

// Panel Store Interface
interface PanelStore {
  // State
  panels: Record<PanelId, PanelConfig>
  activePanels: Record<PanelZone, PanelId[]>
  layoutPresets: Record<string, LayoutPreset>
  currentPreset?: string

  // Actions
  addPanel: (panel: PanelConfig) => void
  removePanel: (panelId: PanelId) => void
  updatePanel: (panelId: PanelId, updates: Partial<PanelConfig>) => void
  movePanel: (panelId: PanelId, targetZone: PanelZone, order?: number) => void
  togglePanel: (panelId: PanelId) => void
  setPanelSize: (panelId: PanelId, size: number) => void
  setPanelOrder: (panelId: PanelId, order: number) => void

  // Layout Presets
  saveLayoutPreset: (name: string, description: string) => void
  loadLayoutPreset: (presetName: string) => void
  deleteLayoutPreset: (presetName: string) => void
  getLayoutPreset: (presetName: string) => LayoutPreset | undefined

  // Utility
  getPanelsByZone: (zone: PanelZone) => PanelConfig[]
  getActivePanel: (zone: PanelZone) => PanelConfig | undefined
  resetLayout: () => void
  clearPersistedData: () => void
}

// Default panel configurations
const defaultPanels: Record<PanelId, PanelConfig> = {
  'file-explorer': {
    id: 'file-explorer',
    zone: 'left',
    size: 300,
    minSize: 200,
    maxSize: 400,
    visible: true,
    order: 0
  },
  'code-editor': {
    id: 'code-editor',
    zone: 'main',
    size: 50,
    minSize: 30,
    visible: true,
    order: 0
  },
  'context-web': {
    id: 'context-web',
    zone: 'right',
    size: 400,
    minSize: 300,
    maxSize: 600,
    visible: true,
    order: 0
  },
  'terminal': {
    id: 'terminal',
    zone: 'bottom',
    size: 300,
    minSize: 200,
    maxSize: 600,
    visible: true,
    order: 0
  }
}

const defaultActivePanels: Record<PanelZone, PanelId[]> = {
  left: ['file-explorer'],
  right: ['context-web'],
  top: [],
  bottom: ['terminal'],
  main: ['code-editor']
}

/**
 * Panel Store
 * 
 * Zustand store for managing panel state, layout, and presets
 * Supports drag-drop, resizing, and layout persistence
 */
export const usePanelStore = create<PanelStore>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        panels: defaultPanels,
        activePanels: defaultActivePanels,
        layoutPresets: {},
        currentPreset: undefined,

        // Add panel
        addPanel: (panel) => {
          set((state) => ({
            panels: { ...state.panels, [panel.id]: panel },
            activePanels: {
              ...state.activePanels,
              [panel.zone]: [...(state.activePanels[panel.zone] || []), panel.id]
            }
          }))
        },

        // Remove panel
        removePanel: (panelId) => {
          set((state) => {
            const panel = state.panels[panelId]
            if (!panel) return state

            const newPanels = { ...state.panels }
            delete newPanels[panelId]

            const newActivePanels = { ...state.activePanels }
            newActivePanels[panel.zone] = newActivePanels[panel.zone].filter(id => id !== panelId)

            return {
              panels: newPanels,
              activePanels: newActivePanels
            }
          })
        },

        // Update panel
        updatePanel: (panelId, updates) => {
          set((state) => {
            const panel = state.panels[panelId]
            if (!panel) return state

            return {
              panels: {
                ...state.panels,
                [panelId]: { ...panel, ...updates }
              }
            }
          })
        },

        // Move panel to different zone
        movePanel: (panelId, targetZone, order) => {
          set((state) => {
            const panel = state.panels[panelId]
            if (!panel) return state

            const oldZone = panel.zone
            const newOrder = order ?? state.activePanels[targetZone].length

            // Remove from old zone
            const newActivePanels = { ...state.activePanels }
            newActivePanels[oldZone] = newActivePanels[oldZone].filter(id => id !== panelId)

            // Add to new zone
            newActivePanels[targetZone] = [
              ...newActivePanels[targetZone].slice(0, newOrder),
              panelId,
              ...newActivePanels[targetZone].slice(newOrder)
            ]

            return {
              panels: {
                ...state.panels,
                [panelId]: { ...panel, zone: targetZone, order: newOrder }
              },
              activePanels: newActivePanels
            }
          })
        },

        // Toggle panel visibility
        togglePanel: (panelId) => {
          set((state) => {
            const panel = state.panels[panelId]
            if (!panel) return state

            return {
              panels: {
                ...state.panels,
                [panelId]: { ...panel, visible: !panel.visible }
              }
            }
          })
        },

        // Set panel size
        setPanelSize: (panelId, size) => {
          set((state) => {
            const panel = state.panels[panelId]
            if (!panel) return state

            const clampedSize = Math.max(
              panel.minSize || 0,
              Math.min(size, panel.maxSize || Infinity)
            )

            return {
              panels: {
                ...state.panels,
                [panelId]: { ...panel, size: clampedSize }
              }
            }
          })
        },

        // Set panel order
        setPanelOrder: (panelId, order) => {
          set((state) => {
            const panel = state.panels[panelId]
            if (!panel) return state

            const zone = panel.zone
            const currentPanels = [...state.activePanels[zone]]
            const currentIndex = currentPanels.indexOf(panelId)

            if (currentIndex === -1) return state

            // Remove from current position
            currentPanels.splice(currentIndex, 1)
            // Insert at new position
            currentPanels.splice(order, 0, panelId)

            return {
              panels: {
                ...state.panels,
                [panelId]: { ...panel, order }
              },
              activePanels: {
                ...state.activePanels,
                [zone]: currentPanels
              }
            }
          })
        },

        // Save layout preset
        saveLayoutPreset: (name, description) => {
          set((state) => {
            const preset: LayoutPreset = {
              name,
              description,
              panels: { ...state.panels },
              createdAt: new Date().toISOString()
            }

            return {
              layoutPresets: {
                ...state.layoutPresets,
                [name]: preset
              },
              currentPreset: name
            }
          })
        },

        // Load layout preset
        loadLayoutPreset: (presetName) => {
          const preset = get().layoutPresets[presetName]
          if (!preset) return

          set({
            panels: { ...preset.panels },
            activePanels: Object.values(preset.panels).reduce(
              (acc, panel) => {
                if (!acc[panel.zone]) acc[panel.zone] = []
                acc[panel.zone].push(panel.id)
                return acc
              },
              { left: [], right: [], top: [], bottom: [], main: [] } as Record<PanelZone, PanelId[]>
            ),
            currentPreset: presetName
          })
        },

        // Delete layout preset
        deleteLayoutPreset: (presetName) => {
          set((state) => {
            const newPresets = { ...state.layoutPresets }
            delete newPresets[presetName]

            return {
              layoutPresets: newPresets,
              currentPreset: state.currentPreset === presetName ? undefined : state.currentPreset
            }
          })
        },

        // Get layout preset
        getLayoutPreset: (presetName) => {
          return get().layoutPresets[presetName]
        },

        // Get panels by zone
        getPanelsByZone: (zone) => {
          const state = get()
          // Get all panels in this zone (from activePanels or from panels directly)
          const panelIds = state.activePanels[zone] || []
          const allPanelsInZone = Object.values(state.panels).filter(p => p.zone === zone)
          
          // Combine: panels from activePanels + any panels in zone not in activePanels
          const allPanelIds = new Set([...panelIds, ...allPanelsInZone.map(p => p.id)])
          
          return Array.from(allPanelIds)
            .map(id => state.panels[id])
            .filter(Boolean)
            .sort((a, b) => a.order - b.order)
        },

        // Get active panel for zone
        getActivePanel: (zone) => {
          const state = get()
          const panelIds = state.activePanels[zone]
          if (panelIds.length === 0) return undefined
          return state.panels[panelIds[0]]
        },

  // Reset layout
  resetLayout: () => {
    set({
      panels: defaultPanels,
      activePanels: defaultActivePanels,
      currentPreset: undefined
    })
  },

  // Clear all persisted data (for debugging)
  clearPersistedData: () => {
    localStorage.removeItem('aether-ide-panel-store')
    set({
      panels: defaultPanels,
      activePanels: defaultActivePanels,
      layoutPresets: {},
      currentPreset: undefined
    })
  }
      }),
      {
        name: 'aether-ide-panel-store',
        partialize: (state) => ({
          panels: state.panels,
          activePanels: state.activePanels,
          layoutPresets: state.layoutPresets,
          currentPreset: state.currentPreset
        })
      }
    ),
    { name: 'PanelStore' }
  )
)

