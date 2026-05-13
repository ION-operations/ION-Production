// Core Layout Store (Zustand) with Persistence
import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { Panel, PanelZone, PanelType } from '@/types'

interface SavedLayout {
  panels: Panel[]
  name: string
  createdAt: string
  updatedAt: string
}

interface LayoutState {
  panels: Panel[]
  activeLayout: string | null
  savedLayouts: Record<string, SavedLayout>
  activePanels: Record<PanelZone, string | null> // Track active panel per zone
  addPanel: (panel: Panel) => void
  removePanel: (panelId: string) => void
  updatePanel: (panelId: string, updates: Partial<Panel>) => void
  movePanel: (panelId: string, zone: PanelZone, order: number) => void
  setActivePanel: (zone: PanelZone, panelId: string | null) => void // Set active panel for zone
  setActiveLayout: (layoutId: string | null) => void
  saveLayout: (layoutId: string, name: string) => void
  loadLayout: (layoutId: string) => void
  deleteLayout: (layoutId: string) => void
  getLayoutNames: () => Array<{ id: string; name: string }>
}

// Layout persistence key
const LAYOUT_STORAGE_KEY = 'lex-ide-layout-state'

const defaultPanels: Panel[] = [
  // Left Drawer
  {
    id: 'file-explorer',
    type: 'file-explorer',
    zone: 'left',
    title: 'File Explorer',
    visible: true, // Keep for backward compatibility, but all panels are always available
    size: 20,
    minSize: 15,
    maxSize: 30,
    order: 0,
  },
  {
    id: 'memory-browser',
    type: 'memory-browser',
    zone: 'left',
    title: 'AI Memory',
    visible: true,
    size: 20,
    minSize: 15,
    maxSize: 30,
    order: 1,
  },
  {
    id: 'search-panel',
    type: 'search-panel',
    zone: 'left',
    title: 'Search',
    visible: true,
    size: 20,
    minSize: 15,
    maxSize: 30,
    order: 2,
  },
  {
    id: 'outline-panel',
    type: 'outline-panel',
    zone: 'left',
    title: 'Outline',
    visible: true,
    size: 20,
    minSize: 15,
    maxSize: 30,
    order: 3,
  },
  {
    id: 'agent-management',
    type: 'agent-management',
    zone: 'left',
    title: 'Agents',
    visible: true,
    size: 20,
    minSize: 15,
    maxSize: 30,
    order: 4,
  },
  {
    id: 'system-monitor',
    type: 'system-monitor',
    zone: 'left',
    title: 'System Monitor',
    visible: true,
    size: 20,
    minSize: 15,
    maxSize: 30,
    order: 5,
  },
  // Main Area
  {
    id: 'code-editor',
    type: 'code-editor',
    zone: 'main',
    title: 'Code Editor',
    visible: true,
    size: 60,
    minSize: 40,
    maxSize: 80,
    order: 0,
  },
  {
    id: 'context-web',
    type: 'context-web',
    zone: 'main',
    title: 'Context Web',
    visible: true,
    size: 60,
    minSize: 40,
    maxSize: 80,
    order: 1,
  },
  {
    id: 'evolution-explorer',
    type: 'evolution-explorer',
    zone: 'main',
    title: 'Evolution Explorer',
    visible: true,
    size: 60,
    minSize: 40,
    maxSize: 80,
    order: 2,
  },
  {
    id: 'documentation-viewer',
    type: 'documentation-viewer',
    zone: 'main',
    title: 'Documentation',
    visible: true,
    size: 60,
    minSize: 40,
    maxSize: 80,
    order: 3,
  },
  {
    id: 'ui-editor',
    type: 'ui-editor',
    zone: 'main',
    title: 'UI Editor',
    visible: true,
    size: 60,
    minSize: 40,
    maxSize: 80,
    order: 4,
  },
  // Right Drawer
  {
    id: 'coding-chat',
    type: 'coding-chat',
    zone: 'right',
    title: 'Coding Chat',
    visible: true,
    size: 20,
    minSize: 15,
    maxSize: 30,
    order: 0,
  },
  {
    id: 'planning-chat',
    type: 'planning-chat',
    zone: 'right',
    title: 'Planning Chat',
    visible: true,
    size: 20,
    minSize: 15,
    maxSize: 30,
    order: 1,
  },
  {
    id: 'properties-panel',
    type: 'properties-panel',
    zone: 'right',
    title: 'Properties',
    visible: true,
    size: 20,
    minSize: 15,
    maxSize: 30,
    order: 2,
  },
  {
    id: 'component-library',
    type: 'component-library',
    zone: 'right',
    title: 'Components',
    visible: true,
    size: 20,
    minSize: 15,
    maxSize: 30,
    order: 3,
  },
  {
    id: 'git-panel',
    type: 'git-panel',
    zone: 'right',
    title: 'Git',
    visible: true,
    size: 20,
    minSize: 15,
    maxSize: 30,
    order: 4,
  },
  // Bottom Drawer
  {
    id: 'terminal',
    type: 'terminal',
    zone: 'bottom',
    title: 'Terminal',
    visible: true,
    size: 30,
    minSize: 20,
    maxSize: 50,
    order: 0,
  },
  {
    id: 'timeline',
    type: 'timeline',
    zone: 'bottom',
    title: 'Timeline',
    visible: true,
    size: 30,
    minSize: 20,
    maxSize: 50,
    order: 1,
  },
  {
    id: 'problems',
    type: 'problems',
    zone: 'bottom',
    title: 'Problems',
    visible: true,
    size: 30,
    minSize: 20,
    maxSize: 50,
    order: 2,
  },
  {
    id: 'debug-console',
    type: 'debug-console',
    zone: 'bottom',
    title: 'PDAS (Debug)',
    visible: true,
    size: 30,
    minSize: 20,
    maxSize: 50,
    order: 3,
  },
]

export const useLayoutStore = create<LayoutState>()(
  persist(
    (set, get) => ({
      panels: defaultPanels,
      activeLayout: null,
      savedLayouts: {},
      activePanels: {
        left: 'file-explorer',
        main: 'code-editor',
        right: 'coding-chat',
        bottom: 'debug-console',
      },
  addPanel: (panel) =>
    set((state) => ({
      panels: [...state.panels, panel],
    })),
  removePanel: (panelId) =>
    set((state) => ({
      panels: state.panels.filter((p) => p.id !== panelId),
    })),
  updatePanel: (panelId, updates) =>
    set((state) => ({
      panels: state.panels.map((p) =>
        p.id === panelId ? { ...p, ...updates } : p
      ),
    })),
  movePanel: (panelId, zone, order) =>
    set((state) => ({
      panels: state.panels.map((p) =>
        p.id === panelId ? { ...p, zone, order } : p
      ),
    })),
  setActivePanel: (zone, panelId) =>
    set((state) => ({
      activePanels: {
        ...state.activePanels,
        [zone]: panelId,
      },
    })),
  setActiveLayout: (layoutId) =>
    set(() => ({
      activeLayout: layoutId,
    })),
  saveLayout: (layoutId, name) =>
    set((state) => {
      const savedLayouts = {
        ...state.savedLayouts,
        [layoutId]: {
          panels: state.panels,
          name,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      }
      return {
        savedLayouts,
        activeLayout: layoutId,
      }
    }),
  loadLayout: (layoutId) =>
    set((state) => {
      const layout = state.savedLayouts[layoutId]
      if (layout) {
        // Restore active panels from first visible panel in each zone
        const activePanels: Record<PanelZone, string | null> = {
          left: null,
          main: null,
          right: null,
          bottom: null,
        }
        Object.keys(activePanels).forEach((zone) => {
          const firstPanel = layout.panels.find((p) => p.zone === zone)
          if (firstPanel) {
            activePanels[zone as PanelZone] = firstPanel.id
          }
        })
        
        return {
          panels: layout.panels,
          activeLayout: layoutId,
          activePanels,
        }
      }
      return state
    }),
  deleteLayout: (layoutId) =>
    set((state) => {
      const { [layoutId]: deleted, ...remainingLayouts } = state.savedLayouts
      return {
        savedLayouts: remainingLayouts,
        activeLayout: state.activeLayout === layoutId ? null : state.activeLayout,
      }
    }),
  getLayoutNames: () => {
    const state = get()
    return state.savedLayouts
      ? Object.entries(state.savedLayouts).map(([id, layout]) => ({
          id,
          name: layout.name || id,
        }))
      : []
  },
    }),
{
  name: LAYOUT_STORAGE_KEY,
  storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        panels: state.panels,
        activeLayout: state.activeLayout,
        savedLayouts: state.savedLayouts,
        activePanels: state.activePanels,
      }),
}
))

