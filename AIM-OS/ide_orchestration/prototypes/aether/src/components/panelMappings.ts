// Panel ID to Panel Type Mappings
// Used for integrating panelStore with AetherIDELayout

export const PANEL_ID_MAP = {
  // Left Panel IDs
  'file-explorer': 'explorer',
  'components': 'components',
  'memory': 'memory',
  'goals': 'goals',
  'status': 'status',
  'super-index': 'super-index',
  'master-index': 'master-index',
  'system-map': 'system-map',
  'nl-tags-explorer': 'nl-tags-explorer',
  'docs-explorer': 'docs-explorer',
  'aimos-status': 'aimos-status',
  
  // Main Content IDs
  'code-editor': 'code',
  'evolution-explorer': 'evolution',
  'consciousness': 'consciousness',
  'agents': 'agents',
  'orchestrator': 'orchestrator',
  'hierarchical-code-v1': 'hierarchical-code-v1',
  'hierarchical-code-v2': 'hierarchical-code-v2',
  'hierarchical-code-v3': 'hierarchical-code-v3',
  
  // Right Panel IDs
  'context-web': 'context-web',
  'evidence': 'evidence',
  'timeline-view': 'timeline-view',
  'mcp-tools': 'mcp-tools',
  'confidence': 'confidence',
  'nl-tags': 'nl-tags',
  'version-history': 'version-history',
  'version-history-v2': 'version-history-v2',
  
  // Bottom Panel IDs
  'terminal': 'terminal',
  'problems': 'problems',
  'timeline': 'timeline',
  'file-changes': 'file-changes',
  'debug-console': 'debug-console'
} as const

export const REVERSE_PANEL_ID_MAP = Object.fromEntries(
  Object.entries(PANEL_ID_MAP).map(([id, type]) => [type, id])
) as Record<string, string>

// Default panel configurations for initialization
export const DEFAULT_PANEL_CONFIGS = {
  // Left panels
  'file-explorer': {
    id: 'file-explorer',
    zone: 'left' as const,
    size: 300,
    minSize: 200,
    maxSize: 400,
    visible: true,
    order: 0
  },
  'components': {
    id: 'components',
    zone: 'left' as const,
    size: 300,
    minSize: 200,
    maxSize: 400,
    visible: false,
    order: 1
  },
  'memory': {
    id: 'memory',
    zone: 'left' as const,
    size: 300,
    minSize: 200,
    maxSize: 400,
    visible: false,
    order: 2
  },
  'goals': {
    id: 'goals',
    zone: 'left' as const,
    size: 300,
    minSize: 200,
    maxSize: 400,
    visible: false,
    order: 3
  },
  'status': {
    id: 'status',
    zone: 'left' as const,
    size: 300,
    minSize: 200,
    maxSize: 400,
    visible: false,
    order: 4
  },
  'super-index': {
    id: 'super-index',
    zone: 'left' as const,
    size: 300,
    minSize: 200,
    maxSize: 400,
    visible: false,
    order: 5
  },
  'master-index': {
    id: 'master-index',
    zone: 'left' as const,
    size: 300,
    minSize: 200,
    maxSize: 400,
    visible: false,
    order: 6
  },
  'system-map': {
    id: 'system-map',
    zone: 'left' as const,
    size: 300,
    minSize: 200,
    maxSize: 400,
    visible: false,
    order: 7
  },
  'nl-tags-explorer': {
    id: 'nl-tags-explorer',
    zone: 'left' as const,
    size: 300,
    minSize: 200,
    maxSize: 400,
    visible: false,
    order: 8
  },
  'docs-explorer': {
    id: 'docs-explorer',
    zone: 'left' as const,
    size: 300,
    minSize: 200,
    maxSize: 400,
    visible: false,
    order: 9
  },
  'aimos-status': {
    id: 'aimos-status',
    zone: 'left' as const,
    size: 300,
    minSize: 200,
    maxSize: 400,
    visible: false,
    order: 10
  },
  
  // Main content panels
  'code-editor': {
    id: 'code-editor',
    zone: 'main' as const,
    size: 50,
    minSize: 30,
    visible: true,
    order: 0
  },
  'evolution-explorer': {
    id: 'evolution-explorer',
    zone: 'main' as const,
    size: 50,
    minSize: 30,
    visible: false,
    order: 1
  },
  'consciousness': {
    id: 'consciousness',
    zone: 'main' as const,
    size: 50,
    minSize: 30,
    visible: false,
    order: 2
  },
  'agents': {
    id: 'agents',
    zone: 'main' as const,
    size: 50,
    minSize: 30,
    visible: false,
    order: 3
  },
  'orchestrator': {
    id: 'orchestrator',
    zone: 'main' as const,
    size: 50,
    minSize: 30,
    visible: false,
    order: 4
  },
  'hierarchical-code-v1': {
    id: 'hierarchical-code-v1',
    zone: 'main' as const,
    size: 50,
    minSize: 30,
    visible: false,
    order: 5
  },
  'hierarchical-code-v2': {
    id: 'hierarchical-code-v2',
    zone: 'main' as const,
    size: 50,
    minSize: 30,
    visible: false,
    order: 6
  },
  'hierarchical-code-v3': {
    id: 'hierarchical-code-v3',
    zone: 'main' as const,
    size: 50,
    minSize: 30,
    visible: false,
    order: 7
  },
  
  // Right panels
  'context-web': {
    id: 'context-web',
    zone: 'right' as const,
    size: 350,
    minSize: 250,
    maxSize: 500,
    visible: true,
    order: 0
  },
  'evidence': {
    id: 'evidence',
    zone: 'right' as const,
    size: 350,
    minSize: 250,
    maxSize: 500,
    visible: false,
    order: 1
  },
  'timeline-view': {
    id: 'timeline-view',
    zone: 'right' as const,
    size: 350,
    minSize: 250,
    maxSize: 500,
    visible: false,
    order: 2
  },
  'mcp-tools': {
    id: 'mcp-tools',
    zone: 'right' as const,
    size: 350,
    minSize: 250,
    maxSize: 500,
    visible: false,
    order: 3
  },
  'confidence': {
    id: 'confidence',
    zone: 'right' as const,
    size: 350,
    minSize: 250,
    maxSize: 500,
    visible: false,
    order: 4
  },
  'nl-tags': {
    id: 'nl-tags',
    zone: 'right' as const,
    size: 350,
    minSize: 250,
    maxSize: 500,
    visible: false,
    order: 5
  },
  'version-history': {
    id: 'version-history',
    zone: 'right' as const,
    size: 350,
    minSize: 250,
    maxSize: 500,
    visible: false,
    order: 6
  },
  'version-history-v2': {
    id: 'version-history-v2',
    zone: 'right' as const,
    size: 350,
    minSize: 250,
    maxSize: 500,
    visible: false,
    order: 7
  },
  
  // Bottom panels
  'terminal': {
    id: 'terminal',
    zone: 'bottom' as const,
    size: 300,
    minSize: 200,
    maxSize: 600,
    visible: true,
    order: 0
  },
  'problems': {
    id: 'problems',
    zone: 'bottom' as const,
    size: 300,
    minSize: 200,
    maxSize: 600,
    visible: false,
    order: 1
  },
  'timeline': {
    id: 'timeline',
    zone: 'bottom' as const,
    size: 300,
    minSize: 200,
    maxSize: 600,
    visible: false,
    order: 2
  },
  'file-changes': {
    id: 'file-changes',
    zone: 'bottom' as const,
    size: 300,
    minSize: 200,
    maxSize: 600,
    visible: false,
    order: 3
  },
  'debug-console': {
    id: 'debug-console',
    zone: 'bottom' as const,
    size: 300,
    minSize: 200,
    maxSize: 600,
    visible: false,
    order: 4
  }
} as const

