import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Panel, Zone, Layout } from '../types/Panel.types';
import type { CMCAtom, VIFWitness, SEGEntity, SEGRelation, TCSTimelineEntry, CASAttentionMetrics } from '../hooks/useAIMOS';

interface PanelStore {
  // Layouts
  layouts: Layout[];
  currentLayout: Layout | null;
  
  // Panels
  panels: Panel[];
  
  // Zones
  zones: Zone[];
  
  // Drag and Drop
  draggedPanel: Panel | null;
  dropTarget: Zone | null;
  
  // Selection
  selectedPanel: Panel | null;
  
  // AIM-OS State
  aimos: {
    cmc: {
      atoms: CMCAtom[];
      lastSync: string | null;
    };
    vif: {
      witnesses: VIFWitness[];
      lastSync: string | null;
    };
    seg: {
      entities: SEGEntity[];
      relations: SEGRelation[];
      lastSync: string | null;
    };
    tcs: {
      timelineEntries: TCSTimelineEntry[];
      lastSync: string | null;
    };
    cas: {
      metrics: CASAttentionMetrics | null;
      lastSync: string | null;
    };
  };
  
  // Actions
  setCurrentLayout: (layout: Layout) => void;
  addLayout: (layout: Layout) => void;
  updateLayout: (layoutId: string, updates: Partial<Layout>) => void;
  deleteLayout: (layoutId: string) => void;
  
  // Panel Actions
  addPanel: (panel: Panel) => void;
  updatePanel: (panelId: string, updates: Partial<Panel>) => void;
  deletePanel: (panelId: string) => void;
  movePanel: (panelId: string, targetZone: ZoneType) => void;
  resizePanel: (panelId: string, size: number) => void;
  
  // Zone Actions
  addZone: (zone: Zone) => void;
  updateZone: (zoneId: string, updates: Partial<Zone>) => void;
  deleteZone: (zoneId: string) => void;
  resizeZone: (zoneId: string, size: number) => void;
  
  // Drag and Drop Actions
  setDraggedPanel: (panel: Panel | null) => void;
  setDropTarget: (zone: Zone | null) => void;
  
  // Selection Actions
  setSelectedPanel: (panel: Panel | null) => void;
  
  // Layout Operations
  saveLayout: (name: string) => void;
  loadLayout: (layoutId: string) => void;
  resetLayout: () => void;
  
  // AIM-OS State Actions
  updateCMCAtoms: (atoms: CMCAtom[]) => void;
  updateVIFWitnesses: (witnesses: VIFWitness[]) => void;
  updateSEGEntities: (entities: SEGEntity[]) => void;
  updateSEGRelations: (relations: SEGRelation[]) => void;
  updateTCSTimeline: (entries: TCSTimelineEntry[]) => void;
  updateCASMetrics: (metrics: CASAttentionMetrics | null) => void;
}

import type { ZoneType } from '../types/Panel.types';

export const usePanelStore = create<PanelStore>()(
  persist(
    (set, get) => ({
      // Initial State
      layouts: [],
      currentLayout: null,
      panels: [],
      zones: [],
      draggedPanel: null,
      dropTarget: null,
      selectedPanel: null,
      
      // AIM-OS Initial State
      aimos: {
        cmc: {
          atoms: [],
          lastSync: null,
        },
        vif: {
          witnesses: [],
          lastSync: null,
        },
        seg: {
          entities: [],
          relations: [],
          lastSync: null,
        },
        tcs: {
          timelineEntries: [],
          lastSync: null,
        },
        cas: {
          metrics: null,
          lastSync: null,
        },
      },
  
  // Layout Actions
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
    })),
  
  deletePanel: (panelId) =>
    set((state) => ({
      panels: state.panels.filter((panel) => panel.id !== panelId),
    })),
  
  movePanel: (panelId, targetZone) =>
    set((state) => ({
      panels: state.panels.map((panel) =>
        panel.id === panelId ? { ...panel, zone: targetZone } : panel
      ),
    })),
  
  resizePanel: (panelId, size) =>
    set((state) => {
      const panel = state.panels.find((p) => p.id === panelId);
      if (!panel) return state;
      
      const constrainedSize = Math.max(
        panel.minSize,
        Math.min(panel.maxSize, size)
      );
      
      return {
        panels: state.panels.map((p) =>
          p.id === panelId ? { ...p, size: constrainedSize } : p
        ),
      };
    }),
  
  // Zone Actions
  addZone: (zone) =>
    set((state) => ({
      zones: [...state.zones, zone],
    })),
  
  updateZone: (zoneId, updates) =>
    set((state) => ({
      zones: state.zones.map((zone) =>
        zone.id === zoneId ? { ...zone, ...updates } : zone
      ),
    })),
  
  deleteZone: (zoneId) =>
    set((state) => ({
      zones: state.zones.filter((zone) => zone.id !== zoneId),
    })),
  
  resizeZone: (zoneId, size) =>
    set((state) => {
      const zone = state.zones.find((z) => z.id === zoneId);
      if (!zone) return state;
      
      const constrainedSize = Math.max(
        zone.minSize,
        Math.min(zone.maxSize, size)
      );
      
      return {
        zones: state.zones.map((z) =>
          z.id === zoneId ? { ...z, size: constrainedSize } : z
        ),
      };
    }),
  
  // Drag and Drop Actions
  setDraggedPanel: (panel) => set({ draggedPanel: panel }),
  
  setDropTarget: (zone) => set({ dropTarget: zone }),
  
  // Selection Actions
  setSelectedPanel: (panel) => set({ selectedPanel: panel }),
  
  // Layout Operations
  saveLayout: (name) => {
    const state = get();
    const layout: Layout = {
      id: `layout-${Date.now()}`,
      name,
      zones: state.zones,
      panels: state.panels,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    
    set({
      layouts: [...state.layouts, layout],
      currentLayout: layout,
    });
  },
  
  loadLayout: (layoutId) => {
    const state = get();
    const layout = state.layouts.find((l) => l.id === layoutId);
    if (layout) {
      set({
        currentLayout: layout,
        zones: layout.zones,
        panels: layout.panels,
      });
    }
  },
  
  resetLayout: () => {
    // Reset to default layout
    const defaultLayout = createDefaultLayout();
    set({
      currentLayout: defaultLayout,
      zones: defaultLayout.zones,
      panels: defaultLayout.panels,
    });
  },
  
  // AIM-OS State Actions
  updateCMCAtoms: (atoms) =>
    set((state) => ({
      aimos: {
        ...state.aimos,
        cmc: {
          atoms,
          lastSync: new Date().toISOString(),
        },
      },
    })),
  
  updateVIFWitnesses: (witnesses) =>
    set((state) => ({
      aimos: {
        ...state.aimos,
        vif: {
          witnesses,
          lastSync: new Date().toISOString(),
        },
      },
    })),
  
  updateSEGEntities: (entities) =>
    set((state) => ({
      aimos: {
        ...state.aimos,
        seg: {
          ...state.aimos.seg,
          entities,
          lastSync: new Date().toISOString(),
        },
      },
    })),
  
  updateSEGRelations: (relations) =>
    set((state) => ({
      aimos: {
        ...state.aimos,
        seg: {
          ...state.aimos.seg,
          relations,
          lastSync: new Date().toISOString(),
        },
      },
    })),
  
  updateTCSTimeline: (entries) =>
    set((state) => ({
      aimos: {
        ...state.aimos,
        tcs: {
          timelineEntries: entries,
          lastSync: new Date().toISOString(),
        },
      },
    })),
  
  updateCASMetrics: (metrics) =>
    set((state) => ({
      aimos: {
        ...state.aimos,
        cas: {
          metrics,
          lastSync: new Date().toISOString(),
        },
      },
    })),
    }),
    {
      name: 'max-ide-panel-store',
      partialize: (state) => ({
        layouts: state.layouts,
        currentLayout: state.currentLayout,
        panels: state.panels,
        zones: state.zones,
        aimos: state.aimos,
      }),
    }
  )
);

// Default Layout Factory - 5-Zone Layout (Top Bar, Left Drawer, Main Content, Right Drawer, Bottom Drawer)
function createDefaultLayout(): Layout {
  const zones: Zone[] = [
    {
      id: 'zone-top',
      type: 'top',
      size: 40,
      minSize: 40,
      maxSize: 40,
      visible: true,
      collapsible: false,
      resizable: false,
      panels: [],
    },
    {
      id: 'zone-left',
      type: 'left',
      size: 250,
      minSize: 150,
      maxSize: 600,
      visible: true,
      collapsible: true,
      resizable: true,
      panels: ['panel-file-explorer', 'panel-super-index', 'panel-master-index', 'panel-hierarchical-code-explorer'],
    },
    {
      id: 'zone-center',
      type: 'center',
      size: 50,
      minSize: 30,
      maxSize: 100,
      visible: true,
      collapsible: false,
      resizable: true,
      panels: ['panel-evolution-explorer'],
    },
    {
      id: 'zone-right',
      type: 'right',
      size: 350,
      minSize: 200,
      maxSize: 600,
      visible: true,
      collapsible: true,
      resizable: true,
      panels: ['panel-outline', 'panel-main-chat', 'panel-context-web', 'panel-file-version-history'],
    },
    {
      id: 'zone-bottom',
      type: 'bottom',
      size: 250,
      minSize: 150,
      maxSize: 500,
      visible: true,
      collapsible: true,
      resizable: true,
      panels: ['panel-terminal', 'panel-problems', 'panel-debug-console'],
    },
  ];
  
  const panels: Panel[] = [
    {
      id: 'panel-file-explorer',
      type: 'file-explorer',
      zone: 'left',
      size: 100,
      minSize: 150,
      maxSize: 600,
      visible: true,
      expanded: true,
      pinned: false,
      order: 0,
      settings: {},
    },
    {
      id: 'panel-super-index',
      type: 'super-index',
      zone: 'left',
      size: 50,
      minSize: 150,
      maxSize: 600,
      visible: false,
      expanded: true,
      pinned: false,
      order: 1,
      settings: {},
    },
    {
      id: 'panel-master-index',
      type: 'master-index',
      zone: 'left',
      size: 50,
      minSize: 150,
      maxSize: 600,
      visible: false,
      expanded: true,
      pinned: false,
      order: 2,
      settings: {},
    },
    {
      id: 'panel-system-map',
      type: 'system-map',
      zone: 'left',
      size: 50,
      minSize: 150,
      maxSize: 600,
      visible: false,
      expanded: true,
      pinned: false,
      order: 3,
      settings: {},
    },
    {
      id: 'panel-nl-tags',
      type: 'nl-tags',
      zone: 'left',
      size: 50,
      minSize: 150,
      maxSize: 600,
      visible: false,
      expanded: true,
      pinned: false,
      order: 4,
      settings: {},
    },
    {
      id: 'panel-documentation',
      type: 'documentation',
      zone: 'left',
      size: 50,
      minSize: 150,
      maxSize: 600,
      visible: false,
      expanded: true,
      pinned: false,
      order: 5,
      settings: {},
    },
    {
      id: 'panel-hierarchical-code-explorer',
      type: 'hierarchical-code-explorer',
      zone: 'left',
      size: 100,
      minSize: 200,
      maxSize: 600,
      visible: false,
      expanded: true,
      pinned: false,
      order: 3,
      settings: {},
    },
    {
      id: 'panel-evolution-explorer',
      type: 'evolution-explorer',
      zone: 'center',
      size: 100,
      minSize: 30,
      maxSize: 100,
      visible: false,
      expanded: true,
      pinned: false,
      order: 0,
      settings: {},
    },
    {
      id: 'panel-file-version-history',
      type: 'file-version-history',
      zone: 'right',
      size: 100,
      minSize: 200,
      maxSize: 600,
      visible: false,
      expanded: true,
      pinned: false,
      order: 4,
      settings: {},
    },
    {
      id: 'panel-outline',
      type: 'outline',
      zone: 'right',
      size: 50,
      minSize: 200,
      maxSize: 500,
      visible: true,
      expanded: true,
      pinned: false,
      order: 0,
      settings: {},
    },
    {
      id: 'panel-main-chat',
      type: 'main-chat',
      zone: 'right',
      size: 50,
      minSize: 250,
      maxSize: 600,
      visible: true,
      expanded: true,
      pinned: false,
      order: 1,
      settings: {},
    },
    {
      id: 'panel-context-web',
      type: 'context-web',
      zone: 'right',
      size: 50,
      minSize: 200,
      maxSize: 600,
      visible: false,
      expanded: true,
      pinned: false,
      order: 2,
      settings: {},
    },
    {
      id: 'panel-terminal',
      type: 'terminal',
      zone: 'bottom',
      size: 50,
      minSize: 150,
      maxSize: 500,
      visible: true,
      expanded: true,
      pinned: false,
      order: 0,
      settings: {},
    },
    {
      id: 'panel-debug-console',
      type: 'debug-console',
      zone: 'bottom',
      size: 33,
      minSize: 150,
      maxSize: 500,
      visible: true,
      expanded: true,
      pinned: false,
      order: 2,
      settings: {},
    },
  ];
  
  return {
    id: 'layout-default',
    name: 'Default Layout',
    zones,
    panels,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
}

