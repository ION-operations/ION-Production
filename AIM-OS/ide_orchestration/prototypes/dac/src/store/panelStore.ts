// Panel Store - Zustand State Management
// V2 Foundation Enhancement: Centralized panel and layout state management

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// ===== TYPE DEFINITIONS =====

export type ZoneType = 'left' | 'right' | 'bottom' | 'top'

export type PanelType =
  | 'file-explorer'
  | 'memory-browser'
  | 'system-status'
  | 'context-web'
  | 'timeline-view'
  | 'outline'
  | 'code-editor'
  | 'terminal'
  | 'problems'
  | 'evolution-explorer'
  | 'consciousness-visualization'
  | 'aimos-orchestration'
  | 'super-index'
  | 'master-index'
  | 'system-map'
  | 'nl-tags'
  | 'documentation-explorer'
  | 'tool-quality-dashboard'
  | 'properties'
  | 'evidence-graph'
  | 'evidence-panel'
  | 'mcp-tools'
  | 'confidence-calibration'
  | 'file-version-history'
  | 'file-changes'
  | 'debug-console'
  | 'browser-automation'
  | 'lucid-chat'

export interface Panel {
  id: string
  type: PanelType
  zone: ZoneType
  size: number  // Percentage (0-100)
  minSize: number
  maxSize: number
  visible: boolean
  expanded: boolean
  pinned: boolean
  order: number  // Order within zone
  settings: Record<string, any>
}

export interface Zone {
  id: string
  type: ZoneType
  size: number  // Percentage (0-100)
  minSize: number
  maxSize: number
  visible: boolean
  collapsible: boolean
  resizable: boolean
  panels: string[]  // Panel IDs
}

export interface Layout {
  id: string
  name: string
  zones: Zone[]
  panels: Panel[]
  createdAt: string
  updatedAt: string
  mainView?: 'code' | 'evolution' | 'consciousness' | 'orchestration' | 'app-preview' | 'file-preview' | 'canvas' | 'manager-ai-chat' // Associated main view
  locked?: boolean // If true, this layout is locked to its main view
  panelVisibility?: {
    leftPanelOpen: boolean
    rightPanelOpen: boolean
    bottomPanelOpen: boolean
  }
  panelSizes?: {
    leftPanelSize: number
    rightPanelSize: number
    bottomPanelSize: number
  }
  panelConfiguration?: {
    leftTopPanel: string | null
    leftBottomPanel: string | null
    rightTopPanel: string | null
    rightBottomPanel: string | null
    bottomLeftPanel: string | null
    bottomRightPanel: string | null
  }
}

export interface PanelStore {
  // Panels
  panels: Panel[]
  selectedPanel: Panel | null
  
  // Layout
  layouts: Layout[]
  currentLayout: Layout | null
  
  // Current Panel Configuration (for visualization)
  currentPanelConfiguration: {
    leftTopPanel: string | null
    leftBottomPanel: string | null
    rightTopPanel: string | null
    rightBottomPanel: string | null
    bottomLeftPanel: string | null
    bottomRightPanel: string | null
    leftPanelOpen: boolean
    rightPanelOpen: boolean
    bottomPanelOpen: boolean
  }
  
  // Drag and Drop
  draggedPanel: Panel | null
  dropTarget: Zone | null
  
  // Main View
  mainView: 'code' | 'evolution' | 'consciousness' | 'orchestration' | 'app-preview' | 'file-preview' | 'canvas' | 'manager-ai-chat'
  
  // Actions
  // Panel Actions
  addPanel: (panel: Panel) => void
  updatePanel: (panelId: string, updates: Partial<Panel>) => void
  deletePanel: (panelId: string) => void
  movePanel: (panelId: string, targetZone: ZoneType) => void
  resizePanel: (panelId: string, size: number) => void
  togglePanelVisibility: (panelId: string) => void
  togglePanelExpanded: (panelId: string) => void
  togglePanelPinned: (panelId: string) => void
  
  // Selection
  setSelectedPanel: (panel: Panel | null) => void
  
  // Layout Operations
  setCurrentLayout: (layout: Layout) => void
  addLayout: (layout: Layout) => void
  updateLayout: (layoutId: string, updates: Partial<Layout>) => void
  deleteLayout: (layoutId: string) => void
  saveLayout: (name: string) => void
  loadLayout: (layoutId: string) => void
  resetLayout: () => void
  createDefaultLayout: () => Layout
  applyPreset: (presetId: 'developer' | 'debug' | 'research' | 'minimal' | 'full') => void
  
  // Drag and Drop Actions
  setDraggedPanel: (panel: Panel | null) => void
  setDropTarget: (zone: Zone | null) => void
  
  // Main View Actions
  setMainView: (view: 'code' | 'evolution' | 'consciousness' | 'orchestration' | 'app-preview' | 'file-preview' | 'canvas' | 'manager-ai-chat') => void
  
  // Current Panel Configuration Actions
  updateCurrentPanelConfiguration: (config: Partial<PanelStore['currentPanelConfiguration']>) => void
  
  // View-Specific Layout Operations
  saveLayoutForView: (
    view: 'code' | 'evolution' | 'consciousness' | 'orchestration' | 'app-preview' | 'file-preview' | 'canvas' | 'manager-ai-chat',
    name?: string,
    panelState?: {
      panelVisibility?: { leftPanelOpen: boolean; rightPanelOpen: boolean; bottomPanelOpen: boolean }
      panelSizes?: { leftPanelSize: number; rightPanelSize: number; bottomPanelSize: number }
      panelConfiguration?: {
        leftTopPanel: string | null
        leftBottomPanel: string | null
        rightTopPanel: string | null
        rightBottomPanel: string | null
        bottomLeftPanel: string | null
        bottomRightPanel: string | null
      }
    }
  ) => void
  loadLayoutForView: (view: 'code' | 'evolution' | 'consciousness' | 'orchestration' | 'app-preview' | 'file-preview' | 'canvas' | 'manager-ai-chat') => {
    layout: Layout | null
    panelState: {
      panelVisibility?: { leftPanelOpen: boolean; rightPanelOpen: boolean; bottomPanelOpen: boolean }
      panelSizes?: { leftPanelSize: number; rightPanelSize: number; bottomPanelSize: number }
      panelConfiguration?: {
        leftTopPanel: string | null
        leftBottomPanel: string | null
        rightTopPanel: string | null
        rightBottomPanel: string | null
        bottomLeftPanel: string | null
        bottomRightPanel: string | null
      }
    } | null
  }
  lockLayoutToView: (view: 'code' | 'evolution' | 'consciousness' | 'orchestration' | 'app-preview' | 'file-preview' | 'canvas' | 'manager-ai-chat', layoutId: string) => void
  unlockLayoutFromView: (view: 'code' | 'evolution' | 'consciousness' | 'orchestration' | 'app-preview' | 'file-preview' | 'canvas' | 'manager-ai-chat') => void
  getLayoutForView: (view: 'code' | 'evolution' | 'consciousness' | 'orchestration' | 'app-preview' | 'file-preview' | 'canvas' | 'manager-ai-chat') => Layout | null
  captureCurrentLayout: () => Layout
  
  // Utility
  getPanelsByZone: (zone: ZoneType) => Panel[]
  getPanelById: (panelId: string) => Panel | undefined
}

// ===== DEFAULT LAYOUT FACTORY =====

function createDefaultLayout(): Layout {
  const zones: Zone[] = [
    {
      id: 'zone-left',
      type: 'left',
      size: 20,  // 20% of width
      minSize: 15,
      maxSize: 40,
      visible: true,
      collapsible: true,
      resizable: true,
      panels: ['panel-file-explorer', 'panel-memory-browser', 'panel-system-status'],
    },
    {
      id: 'zone-right',
      type: 'right',
      size: 25,  // 25% of width
      minSize: 15,
      maxSize: 40,
      visible: true,
      collapsible: true,
      resizable: true,
      panels: ['panel-context-web', 'panel-outline', 'panel-timeline-view'],
    },
    {
      id: 'zone-bottom',
      type: 'bottom',
      size: 30,  // 30% of height
      minSize: 15,
      maxSize: 50,
      visible: true,
      collapsible: true,
      resizable: true,
      panels: ['panel-terminal', 'panel-problems'],
    },
  ]
  
  const panels: Panel[] = [
    // Left Drawer Panels
    {
      id: 'panel-file-explorer',
      type: 'file-explorer',
      zone: 'left',
      size: 40,  // 40% of left drawer height
      minSize: 20,
      maxSize: 80,
      visible: true,
      expanded: true,
      pinned: false,
      order: 0,
      settings: {},
    },
    {
      id: 'panel-memory-browser',
      type: 'memory-browser',
      zone: 'left',
      size: 30,  // 30% of left drawer height
      minSize: 20,
      maxSize: 80,
      visible: true,
      expanded: true,
      pinned: false,
      order: 1,
      settings: {},
    },
    {
      id: 'panel-system-status',
      type: 'system-status',
      zone: 'left',
      size: 30,  // 30% of left drawer height
      minSize: 20,
      maxSize: 80,
      visible: true,
      expanded: true,
      pinned: false,
      order: 2,
      settings: {},
    },
    // Right Drawer Panels
    {
      id: 'panel-context-web',
      type: 'context-web',
      zone: 'right',
      size: 40,  // 40% of right drawer height
      minSize: 20,
      maxSize: 80,
      visible: true,
      expanded: true,
      pinned: false,
      order: 0,
      settings: {},
    },
    {
      id: 'panel-outline',
      type: 'outline',
      zone: 'right',
      size: 30,  // 30% of right drawer height
      minSize: 20,
      maxSize: 80,
      visible: true,
      expanded: true,
      pinned: false,
      order: 1,
      settings: {},
    },
    {
      id: 'panel-timeline-view',
      type: 'timeline-view',
      zone: 'right',
      size: 30,  // 30% of right drawer height
      minSize: 20,
      maxSize: 80,
      visible: true,
      expanded: true,
      pinned: false,
      order: 2,
      settings: {},
    },
    // Bottom Drawer Panels
    {
      id: 'panel-terminal',
      type: 'terminal',
      zone: 'bottom',
      size: 50,  // 50% of bottom drawer width
      minSize: 30,
      maxSize: 70,
      visible: true,
      expanded: true,
      pinned: false,
      order: 0,
      settings: {},
    },
    {
      id: 'panel-problems',
      type: 'problems',
      zone: 'bottom',
      size: 50,  // 50% of bottom drawer width
      minSize: 30,
      maxSize: 70,
      visible: true,
      expanded: true,
      pinned: false,
      order: 1,
      settings: {},
    },
  ]
  
  return {
    id: 'layout-default',
    name: 'Default Layout',
    zones,
    panels,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }
}

// ===== ZUSTAND STORE =====

export const usePanelStore = create<PanelStore>()(
  persist(
    (set, get) => ({
      // Initial State
      panels: createDefaultLayout().panels,
      selectedPanel: null,
      layouts: [createDefaultLayout()],
      currentLayout: createDefaultLayout(),
      draggedPanel: null,
      dropTarget: null,
      mainView: 'code',
      currentPanelConfiguration: {
        leftTopPanel: null,
        leftBottomPanel: null,
        rightTopPanel: null,
        rightBottomPanel: null,
        bottomLeftPanel: null,
        bottomRightPanel: null,
        leftPanelOpen: true,
        rightPanelOpen: true,
        bottomPanelOpen: true,
      },
      
      // Panel Actions
      addPanel: (panel) =>
        set((state) => ({
          panels: [...state.panels, panel],
        })),
      
      updatePanel: (panelId, updates) =>
        set((state) => ({
          panels: state.panels.map((panel) =>
            panel.id === panelId ? { ...panel, ...updates } : panel
          ),
          selectedPanel:
            state.selectedPanel?.id === panelId
              ? { ...state.selectedPanel, ...updates }
              : state.selectedPanel,
        })),
      
      deletePanel: (panelId) =>
        set((state) => ({
          panels: state.panels.filter((panel) => panel.id !== panelId),
          selectedPanel:
            state.selectedPanel?.id === panelId ? null : state.selectedPanel,
        })),
      
      movePanel: (panelId, targetZone) =>
        set((state) => ({
          panels: state.panels.map((panel) =>
            panel.id === panelId ? { ...panel, zone: targetZone } : panel
          ),
        })),
      
      resizePanel: (panelId, size) =>
        set((state) => {
          const panel = state.panels.find((p) => p.id === panelId)
          if (!panel) return state
          
          const constrainedSize = Math.max(
            panel.minSize,
            Math.min(panel.maxSize, size)
          )
          
          return {
            panels: state.panels.map((p) =>
              p.id === panelId ? { ...p, size: constrainedSize } : p
            ),
          }
        }),
      
      togglePanelVisibility: (panelId) =>
        set((state) => ({
          panels: state.panels.map((panel) =>
            panel.id === panelId
              ? { ...panel, visible: !panel.visible }
              : panel
          ),
        })),
      
      togglePanelExpanded: (panelId) =>
        set((state) => ({
          panels: state.panels.map((panel) =>
            panel.id === panelId
              ? { ...panel, expanded: !panel.expanded }
              : panel
          ),
        })),
      
      togglePanelPinned: (panelId) =>
        set((state) => ({
          panels: state.panels.map((panel) =>
            panel.id === panelId
              ? { ...panel, pinned: !panel.pinned }
              : panel
          ),
        })),
      
      // Selection Actions
      setSelectedPanel: (panel) => set({ selectedPanel: panel }),
      
      // Layout Operations
      setCurrentLayout: (layout) => set({ currentLayout: layout }),
      
      addLayout: (layout) =>
        set((state) => ({
          layouts: [...state.layouts, layout],
        })),
      
      updateLayout: (layoutId, updates) =>
        set((state) => ({
          layouts: state.layouts.map((layout) =>
            layout.id === layoutId ? { ...layout, ...updates } : layout
          ),
          currentLayout:
            state.currentLayout?.id === layoutId
              ? { ...state.currentLayout, ...updates }
              : state.currentLayout,
        })),
      
      deleteLayout: (layoutId) =>
        set((state) => ({
          layouts: state.layouts.filter((layout) => layout.id !== layoutId),
          currentLayout:
            state.currentLayout?.id === layoutId ? null : state.currentLayout,
        })),
      
      saveLayout: (name) => {
        const state = get()
        const layout: Layout = {
          id: `layout-${Date.now()}`,
          name,
          zones: state.currentLayout?.zones || [],
          panels: state.panels,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        }
        
        set({
          layouts: [...state.layouts, layout],
          currentLayout: layout,
        })
      },
      
      loadLayout: (layoutId) => {
        const state = get()
        const layout = state.layouts.find((l) => l.id === layoutId)
        if (layout) {
          set({
            currentLayout: layout,
            panels: layout.panels,
          })
        }
      },
      
      resetLayout: () => {
        const defaultLayout = createDefaultLayout()
        set({
          currentLayout: defaultLayout,
          panels: defaultLayout.panels,
        })
      },
      
      createDefaultLayout: () => createDefaultLayout(),
      
      applyPreset: (presetId) => {
        const state = get()
        
        // Preset configurations
        const presets: Record<string, { left: PanelType[]; right: PanelType[]; bottom: PanelType[] }> = {
          developer: {
            left: ['file-explorer', 'memory-browser'],
            right: ['outline', 'context-web'],
            bottom: ['terminal', 'problems']
          },
          debug: {
            left: ['file-explorer', 'system-status'],
            right: ['problems', 'context-web'],
            bottom: ['terminal', 'debug-console']
          },
          research: {
            left: ['memory-browser', 'system-status'],
            right: ['context-web', 'evolution-explorer'],
            bottom: ['timeline-view', 'consciousness-visualization']
          },
          minimal: {
            left: [],
            right: [],
            bottom: []
          },
          full: {
            left: ['file-explorer', 'memory-browser', 'system-status'],
            right: ['context-web', 'timeline-view', 'outline', 'problems'],
            bottom: ['terminal', 'evolution-explorer', 'consciousness-visualization', 'aimos-orchestration']
          }
        }
        
        const preset = presets[presetId]
        if (!preset) return
        
        // Create new panels based on preset
        const newPanels: Panel[] = []
        let order = 0
        
        // Left panels
        preset.left.forEach((type, index) => {
          const existingPanel = state.panels.find(p => p.type === type)
          if (existingPanel) {
            newPanels.push({
              ...existingPanel,
              zone: 'left',
              visible: true,
              order: order++
            })
          } else {
            newPanels.push({
              id: `panel-${type}`,
              type,
              zone: 'left',
              size: 100 / preset.left.length,
              minSize: 20,
              maxSize: 80,
              visible: true,
              expanded: true,
              pinned: false,
              order: order++,
              settings: {}
            })
          }
        })
        
        // Right panels
        preset.right.forEach((type, index) => {
          const existingPanel = state.panels.find(p => p.type === type)
          if (existingPanel) {
            newPanels.push({
              ...existingPanel,
              zone: 'right',
              visible: true,
              order: order++
            })
          } else {
            newPanels.push({
              id: `panel-${type}`,
              type,
              zone: 'right',
              size: 100 / preset.right.length,
              minSize: 20,
              maxSize: 80,
              visible: true,
              expanded: true,
              pinned: false,
              order: order++,
              settings: {}
            })
          }
        })
        
        // Bottom panels
        preset.bottom.forEach((type, index) => {
          const existingPanel = state.panels.find(p => p.type === type)
          if (existingPanel) {
            newPanels.push({
              ...existingPanel,
              zone: 'bottom',
              visible: true,
              order: order++
            })
          } else {
            newPanels.push({
              id: `panel-${type}`,
              type,
              zone: 'bottom',
              size: 100 / preset.bottom.length,
              minSize: 30,
              maxSize: 70,
              visible: true,
              expanded: true,
              pinned: false,
              order: order++,
              settings: {}
            })
          }
        })
        
        // Hide panels not in preset
        const presetPanelTypes = new Set([...preset.left, ...preset.right, ...preset.bottom])
        const hiddenPanels = state.panels
          .filter(p => !presetPanelTypes.has(p.type))
          .map(p => ({ ...p, visible: false }))
        
        set({
          panels: [...newPanels, ...hiddenPanels],
          currentLayout: {
            ...state.currentLayout!,
            panels: [...newPanels, ...hiddenPanels],
            updatedAt: new Date().toISOString()
          }
        })
      },
      
      // Drag and Drop Actions
      setDraggedPanel: (panel) => set({ draggedPanel: panel }),
      
      setDropTarget: (zone) => set({ dropTarget: zone }),
      
      // Main View Actions
      setMainView: (view) => {
        const state = get()
        // Check if there's a locked layout for this view
        const lockedLayout = state.layouts.find(
          l => l.mainView === view && l.locked === true
        )
        
        if (lockedLayout) {
          // Restore the locked layout
          set({
            mainView: view,
            currentLayout: lockedLayout,
            panels: lockedLayout.panels,
          })
        } else {
          // Just change the view
          set({ mainView: view })
        }
      },
      
      updateCurrentPanelConfiguration: (config) =>
        set((state) => ({
          currentPanelConfiguration: {
            ...state.currentPanelConfiguration,
            ...config,
          },
        })),
      
      // View-Specific Layout Operations
      captureCurrentLayout: () => {
        const state = get()
        return {
          id: state.currentLayout?.id || `layout-${Date.now()}`,
          name: state.currentLayout?.name || 'Current Layout',
          zones: state.currentLayout?.zones || [],
          panels: state.panels,
          createdAt: state.currentLayout?.createdAt || new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        }
      },
      
      saveLayoutForView: (view, name, panelState) => {
        const state = get()
        const layoutName = name || `${view.charAt(0).toUpperCase() + view.slice(1)} Layout`
        
        // Check if layout already exists for this view
        const existingLayout = state.layouts.find(
          l => l.mainView === view && l.name === layoutName
        )
        
        const layout: Layout = {
          id: existingLayout?.id || `layout-${Date.now()}`,
          name: layoutName,
          zones: state.currentLayout?.zones || [],
          panels: state.panels,
          createdAt: existingLayout?.createdAt || new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          mainView: view,
          locked: existingLayout?.locked || false,
          panelVisibility: panelState?.panelVisibility,
          panelSizes: panelState?.panelSizes,
          panelConfiguration: panelState?.panelConfiguration,
        }
        
        if (existingLayout) {
          // Update existing layout
          set({
            layouts: state.layouts.map(l =>
              l.id === existingLayout.id ? layout : l
            ),
            currentLayout: layout,
          })
        } else {
          // Add new layout
          set({
            layouts: [...state.layouts, layout],
            currentLayout: layout,
          })
        }
      },
      
      loadLayoutForView: (view) => {
        const state = get()
        const layout = state.layouts.find(
          l => l.mainView === view && l.locked === true
        ) || state.layouts.find(l => l.mainView === view)
        
        if (layout) {
          return {
            layout,
            panelState: {
              panelVisibility: layout.panelVisibility,
              panelSizes: layout.panelSizes,
              panelConfiguration: layout.panelConfiguration,
            }
          }
        }
        
        return { layout: null, panelState: null }
      },
      
      lockLayoutToView: (view, layoutId) => {
        const state = get()
        // Unlock any other layouts for this view
        const updatedLayouts = state.layouts.map(layout => {
          if (layout.mainView === view && layout.locked) {
            return { ...layout, locked: false }
          }
          if (layout.id === layoutId) {
            return { ...layout, mainView: view, locked: true }
          }
          return layout
        })
        
        set({ layouts: updatedLayouts })
      },
      
      unlockLayoutFromView: (view) => {
        const state = get()
        const updatedLayouts = state.layouts.map(layout => {
          if (layout.mainView === view && layout.locked) {
            return { ...layout, locked: false }
          }
          return layout
        })
        
        set({ layouts: updatedLayouts })
      },
      
      getLayoutForView: (view) => {
        const state = get()
        return state.layouts.find(
          l => l.mainView === view && l.locked === true
        ) || state.layouts.find(l => l.mainView === view) || null
      },
      
      // Utility
      getPanelsByZone: (zone) => {
        const state = get()
        return state.panels
          .filter((panel) => panel.zone === zone && panel.visible)
          .sort((a, b) => a.order - b.order)
      },
      
      getPanelById: (panelId) => {
        const state = get()
        return state.panels.find((panel) => panel.id === panelId)
      },
    }),
    {
      name: 'dac-ide-panel-store',  // LocalStorage key
      partialize: (state) => ({
        panels: state.panels,
        layouts: state.layouts,
        currentLayout: state.currentLayout,
        mainView: state.mainView,
      }),
    }
  )
)

