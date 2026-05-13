// Panel Registry System - Max V2
// Central registry for all panels with metadata and lifecycle management

import type { Panel, PanelType, ZoneType } from '../types/Panel.types'

export interface PanelConfig {
  id: string
  type: PanelType
  defaultZone: ZoneType
  defaultSize: number
  minSize: number
  maxSize: number
  defaultVisible: boolean
  defaultExpanded: boolean
  defaultPinned: boolean
  defaultOrder: number
  component: string // Component path/name
  category: 'navigation' | 'editing' | 'debugging' | 'communication' | 'structure' | 'revolutionary'
  description: string
  requiresAIMOS?: string[] // AIM-OS systems required (e.g., ['CMC', 'HHNI'])
  lazyLoad?: boolean
}

// Panel Registry - All available panels
export const PANEL_REGISTRY: Record<string, PanelConfig> = {
  // Navigation Panels
  'panel-file-explorer': {
    id: 'panel-file-explorer',
    type: 'file-explorer',
    defaultZone: 'left',
    defaultSize: 100,
    minSize: 150,
    maxSize: 600,
    defaultVisible: true,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 0,
    component: 'FileExplorerPanel',
    category: 'navigation',
    description: 'File tree with git status, expand/collapse, search',
    requiresAIMOS: ['CMC', 'VIF', 'SEG'],
  },
  'panel-outline': {
    id: 'panel-outline',
    type: 'outline',
    defaultZone: 'right',
    defaultSize: 50,
    minSize: 200,
    maxSize: 500,
    defaultVisible: true,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 0,
    component: 'OutlinePanel',
    category: 'navigation',
    description: 'Symbol navigation (functions, classes, interfaces)',
    requiresAIMOS: ['HHNI'],
  },
  'panel-hierarchical-code-explorer': {
    id: 'panel-hierarchical-code-explorer',
    type: 'hierarchical-code-explorer',
    defaultZone: 'left',
    defaultSize: 100,
    minSize: 200,
    maxSize: 600,
    defaultVisible: false,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 3,
    component: 'HierarchicalCodeExplorerPanel',
    category: 'navigation',
    description: 'HHNI-powered semantic code explorer',
    requiresAIMOS: ['HHNI'],
    lazyLoad: true,
  },
  
  // Structure Panels (AIM-OS)
  'panel-super-index': {
    id: 'panel-super-index',
    type: 'super-index',
    defaultZone: 'left',
    defaultSize: 50,
    minSize: 150,
    maxSize: 600,
    defaultVisible: false,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 1,
    component: 'SuperIndexPanel',
    category: 'structure',
    description: 'Master concept index navigation',
    requiresAIMOS: ['CMC', 'HHNI'],
    lazyLoad: true,
  },
  'panel-master-index': {
    id: 'panel-master-index',
    type: 'master-index',
    defaultZone: 'left',
    defaultSize: 50,
    minSize: 150,
    maxSize: 600,
    defaultVisible: false,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 2,
    component: 'MasterIndexPanel',
    category: 'structure',
    description: 'System-level navigation',
    requiresAIMOS: ['CMC', 'HHNI'],
    lazyLoad: true,
  },
  'panel-system-map': {
    id: 'panel-system-map',
    type: 'system-map',
    defaultZone: 'left',
    defaultSize: 50,
    minSize: 150,
    maxSize: 600,
    defaultVisible: false,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 3,
    component: 'SystemMapPanel',
    category: 'structure',
    description: 'Visual system relationships',
    requiresAIMOS: ['SEG'],
    lazyLoad: true,
  },
  'panel-nl-tags': {
    id: 'panel-nl-tags',
    type: 'nl-tags',
    defaultZone: 'left',
    defaultSize: 50,
    minSize: 150,
    maxSize: 600,
    defaultVisible: false,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 4,
    component: 'NLTagsExplorerPanel',
    category: 'structure',
    description: 'NL tag browser and validation',
    requiresAIMOS: ['CMC'],
    lazyLoad: true,
  },
  'panel-documentation': {
    id: 'panel-documentation',
    type: 'documentation',
    defaultZone: 'left',
    defaultSize: 50,
    minSize: 150,
    maxSize: 600,
    defaultVisible: false,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 5,
    component: 'DocumentationExplorerPanel',
    category: 'structure',
    description: 'Documentation navigation',
    requiresAIMOS: ['CMC', 'HHNI'],
    lazyLoad: true,
  },
  
  // Revolutionary Panels
  'panel-context-web': {
    id: 'panel-context-web',
    type: 'context-web',
    defaultZone: 'right',
    defaultSize: 50,
    minSize: 200,
    maxSize: 600,
    defaultVisible: false,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 2,
    component: 'ContextWebPanel',
    category: 'revolutionary',
    description: 'Interactive knowledge graph visualization',
    requiresAIMOS: ['HHNI', 'SEG'],
    lazyLoad: true,
  },
  'panel-evolution-explorer': {
    id: 'panel-evolution-explorer',
    type: 'evolution-explorer',
    defaultZone: 'center',
    defaultSize: 100,
    minSize: 30,
    maxSize: 100,
    defaultVisible: false,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 0,
    component: 'EvolutionExplorerPanel',
    category: 'revolutionary',
    description: 'Bidirectional Timeline ↔ Chain ↔ Goals visualization',
    requiresAIMOS: ['TCS', 'APOE'],
    lazyLoad: true,
  },
  'panel-file-version-history': {
    id: 'panel-file-version-history',
    type: 'file-version-history',
    defaultZone: 'right',
    defaultSize: 100,
    minSize: 200,
    maxSize: 600,
    defaultVisible: false,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 4,
    component: 'FileVersionHistoryPanel',
    category: 'revolutionary',
    description: 'Bitemporal versioning with AIM-OS metadata',
    requiresAIMOS: ['CMC', 'VIF'],
    lazyLoad: true,
  },
  
  // Communication Panels
  'panel-main-chat': {
    id: 'panel-main-chat',
    type: 'main-chat',
    defaultZone: 'right',
    defaultSize: 50,
    minSize: 250,
    maxSize: 600,
    defaultVisible: true,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 1,
    component: 'MainChatPanel',
    category: 'communication',
    description: 'Chat interface with message history, code blocks',
    requiresAIMOS: ['CMC', 'VIF'],
  },
  'panel-coding-agent': {
    id: 'panel-coding-agent',
    type: 'coding-agent',
    defaultZone: 'right',
    defaultSize: 50,
    minSize: 250,
    maxSize: 600,
    defaultVisible: false,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 5,
    component: 'CodingAgentPanel',
    category: 'communication',
    description: 'Code-focused chat agent',
    requiresAIMOS: ['CMC', 'VIF', 'APOE'],
    lazyLoad: true,
  },
  'panel-planning-agent': {
    id: 'panel-planning-agent',
    type: 'planning-agent',
    defaultZone: 'right',
    defaultSize: 50,
    minSize: 250,
    maxSize: 600,
    defaultVisible: false,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 6,
    component: 'PlanningAgentPanel',
    category: 'communication',
    description: 'Planning-focused chat agent',
    requiresAIMOS: ['CMC', 'VIF', 'APOE'],
    lazyLoad: true,
  },
  
  // Debugging Panels
  'panel-terminal': {
    id: 'panel-terminal',
    type: 'terminal',
    defaultZone: 'bottom',
    defaultSize: 50,
    minSize: 150,
    maxSize: 500,
    defaultVisible: true,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 0,
    component: 'TerminalPanel',
    category: 'debugging',
    description: 'Multiple terminals with tabs, command input, output',
    requiresAIMOS: ['CMC', 'VIF'],
  },
  'panel-problems': {
    id: 'panel-problems',
    type: 'problems',
    defaultZone: 'bottom',
    defaultSize: 50,
    minSize: 150,
    maxSize: 500,
    defaultVisible: true,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 1,
    component: 'ProblemsPanel',
    category: 'debugging',
    description: 'Error/warning/info display with file locations',
    requiresAIMOS: ['VIF', 'SEG'],
  },
  'panel-debug-console': {
    id: 'panel-debug-console',
    type: 'debug-console',
    defaultZone: 'bottom',
    defaultSize: 33,
    minSize: 150,
    maxSize: 500,
    defaultVisible: true,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 2,
    component: 'DebugConsolePanel',
    category: 'debugging',
    description: 'AIM-OS native debugging with bitemporal logs',
    requiresAIMOS: ['CMC', 'HHNI', 'VIF', 'SEG'],
    lazyLoad: true,
  },
  
  // Additional Panels (Planned)
  'panel-component-library': {
    id: 'panel-component-library',
    type: 'component-library',
    defaultZone: 'left',
    defaultSize: 50,
    minSize: 200,
    maxSize: 600,
    defaultVisible: false,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 6,
    component: 'ComponentLibraryPanel',
    category: 'navigation',
    description: 'Component browser with categories',
    requiresAIMOS: ['HHNI'],
    lazyLoad: true,
  },
  'panel-ai-memory': {
    id: 'panel-ai-memory',
    type: 'ai-memory',
    defaultZone: 'left',
    defaultSize: 50,
    minSize: 200,
    maxSize: 600,
    defaultVisible: false,
    defaultExpanded: true,
    defaultPinned: false,
    defaultOrder: 7,
    component: 'AIMemoryPanel',
    category: 'navigation',
    description: 'Hierarchical memory tree (HHNI)',
    requiresAIMOS: ['CMC', 'HHNI', 'VIF'],
    lazyLoad: true,
  },
}

// Panel Registry Helper Functions
export function getPanelConfig(panelId: string): PanelConfig | undefined {
  return PANEL_REGISTRY[panelId]
}

export function getAllPanelConfigs(): PanelConfig[] {
  return Object.values(PANEL_REGISTRY)
}

export function getPanelsByCategory(category: PanelConfig['category']): PanelConfig[] {
  return getAllPanelConfigs().filter((config) => config.category === category)
}

export function getPanelsByZone(zone: ZoneType): PanelConfig[] {
  return getAllPanelConfigs().filter((config) => config.defaultZone === zone)
}

export function getPanelsRequiringAIMOS(system: string): PanelConfig[] {
  return getAllPanelConfigs().filter(
    (config) => config.requiresAIMOS?.includes(system)
  )
}

export function createPanelFromConfig(config: PanelConfig, overrides?: Partial<Panel>): Panel {
  return {
    id: config.id,
    type: config.type,
    zone: config.defaultZone,
    size: config.defaultSize,
    minSize: config.minSize,
    maxSize: config.maxSize,
    visible: config.defaultVisible,
    expanded: config.defaultExpanded,
    pinned: config.defaultPinned,
    order: config.defaultOrder,
    settings: {},
    ...overrides,
  }
}

// Panel Lifecycle Management
export interface PanelLifecycle {
  mount: () => void
  unmount: () => void
  update: (updates: Partial<Panel>) => void
  isMounted: boolean
}

export class PanelLifecycleManager {
  private mountedPanels: Map<string, PanelLifecycle> = new Map()

  mount(panelId: string, lifecycle: PanelLifecycle): void {
    if (this.mountedPanels.has(panelId)) {
      console.warn(`[MAX] Panel ${panelId} is already mounted`)
      return
    }
    this.mountedPanels.set(panelId, lifecycle)
    lifecycle.mount()
  }

  unmount(panelId: string): void {
    const lifecycle = this.mountedPanels.get(panelId)
    if (lifecycle) {
      lifecycle.unmount()
      this.mountedPanels.delete(panelId)
    }
  }

  update(panelId: string, updates: Partial<Panel>): void {
    const lifecycle = this.mountedPanels.get(panelId)
    if (lifecycle) {
      lifecycle.update(updates)
    }
  }

  isMounted(panelId: string): boolean {
    return this.mountedPanels.has(panelId)
  }

  getAllMounted(): string[] {
    return Array.from(this.mountedPanels.keys())
  }

  unmountAll(): void {
    this.mountedPanels.forEach((lifecycle, panelId) => {
      lifecycle.unmount()
    })
    this.mountedPanels.clear()
  }
}

// Singleton instance
export const panelLifecycleManager = new PanelLifecycleManager()

