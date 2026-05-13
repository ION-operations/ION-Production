/**
 * Panel Registry
 * 
 * Phase 3.1: Central Panel Registry with Metadata
 * 
 * Features:
 * - Panel definitions with metadata
 * - Panel grouping support
 * - Panel categories
 * - Panel icons and descriptions
 */

import React from 'react'
import {
  FolderOpen,
  Code,
  Search,
  Settings,
  Terminal,
  Layers,
  Brain,
  Activity,
  Database,
  GitBranch,
  FileText,
  Target,
  Network,
  Shield,
  Package,
  Palette,
  List,
  AlertCircle,
  Output,
  Bug,
  Clock,
  FileDiff,
  Sparkles,
  Zap,
  Eye,
} from 'lucide-react'
import { LeftPanelType, RightPanelType, BottomPanelType } from './RevIDELayout'

export interface PanelMetadata {
  id: string
  name: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  category: 'development' | 'ai' | 'debugging' | 'exploration' | 'utilities'
  group?: string // Panel group ID for grouping
  tags: string[]
  defaultZone: 'left' | 'right' | 'bottom'
}

// Panel Groups
export const PANEL_GROUPS = {
  'file-management': {
    id: 'file-management',
    name: 'File Management',
    description: 'File and project navigation',
    icon: FolderOpen,
    panels: ['file-explorer', 'git', 'templates'] as const
  },
  'code-analysis': {
    id: 'code-analysis',
    name: 'Code Analysis',
    description: 'Code structure and navigation',
    icon: Code,
    panels: ['outline', 'layers', 'properties'] as const
  },
  'ai-tools': {
    id: 'ai-tools',
    name: 'AI Tools',
    description: 'AI consciousness and memory tools',
    icon: Brain,
    panels: ['ai-memory', 'context-web', 'consciousness-explorer', 'goal-planning'] as const
  },
  'debugging': {
    id: 'debugging',
    name: 'Debugging',
    description: 'Debugging and troubleshooting',
    icon: Bug,
    panels: ['debug-console', 'problems', 'output', 'file-changes'] as const
  },
  'development': {
    id: 'development',
    name: 'Development',
    description: 'Development tools and utilities',
    icon: Zap,
    panels: ['terminal', 'component-library', 'tool-selection', 'tool-quality'] as const
  },
  'orchestration': {
    id: 'orchestration',
    name: 'Orchestration',
    description: 'AI agent and workflow orchestration',
    icon: Network,
    panels: ['lucid-orchestrator', 'agent-management'] as const
  },
  'visualization': {
    id: 'visualization',
    name: 'Visualization',
    description: 'Data and evolution visualization',
    icon: Eye,
    panels: ['context-web', 'evolution-explorer', 'consciousness-visualization', 'timeline'] as const
  }
} as const

// Panel Metadata Registry
const PANEL_METADATA: Record<string, PanelMetadata> = {
  // Left Panels
  'file-explorer': {
    id: 'file-explorer',
    name: 'File Explorer',
    description: 'Browse project files and folders',
    icon: FolderOpen,
    category: 'development',
    group: 'file-management',
    tags: ['files', 'navigation', 'project'],
    defaultZone: 'left'
  },
  'component-library': {
    id: 'component-library',
    name: 'Component Library',
    description: 'Browse and search reusable components',
    icon: Package,
    category: 'development',
    group: 'development',
    tags: ['components', 'reusable', 'library'],
    defaultZone: 'left'
  },
  'ai-memory': {
    id: 'ai-memory',
    name: 'AI Memory',
    description: 'Browse and search AI memory (CMC/HHNI)',
    icon: Brain,
    category: 'ai',
    group: 'ai-tools',
    tags: ['memory', 'cmc', 'hhni', 'ai'],
    defaultZone: 'left'
  },
  'git': {
    id: 'git',
    name: 'Git',
    description: 'Git source control',
    icon: GitBranch,
    category: 'development',
    group: 'file-management',
    tags: ['git', 'version-control', 'scm'],
    defaultZone: 'left'
  },
  'templates': {
    id: 'templates',
    name: 'Templates',
    description: 'Code templates and snippets',
    icon: FileText,
    category: 'development',
    group: 'file-management',
    tags: ['templates', 'snippets', 'code'],
    defaultZone: 'left'
  },
  'lucid-orchestrator': {
    id: 'lucid-orchestrator',
    name: 'Lucid Orchestrator',
    description: 'AI agent orchestration and management',
    icon: Network,
    category: 'ai',
    group: 'orchestration',
    tags: ['orchestration', 'agents', 'workflow'],
    defaultZone: 'left'
  },
  'consciousness-explorer': {
    id: 'consciousness-explorer',
    name: 'Consciousness Explorer',
    description: 'Explore AI consciousness state',
    icon: Sparkles,
    category: 'ai',
    group: 'ai-tools',
    tags: ['consciousness', 'ai', 'exploration'],
    defaultZone: 'left'
  },
  'tool-quality': {
    id: 'tool-quality',
    name: 'Tool Quality',
    description: 'MCP tool quality metrics and monitoring',
    icon: Shield,
    category: 'utilities',
    group: 'development',
    tags: ['tools', 'quality', 'metrics', 'mcp'],
    defaultZone: 'left'
  },
  
  // Right Panels
  'outline': {
    id: 'outline',
    name: 'Outline',
    description: 'Code structure outline',
    icon: List,
    category: 'development',
    group: 'code-analysis',
    tags: ['outline', 'structure', 'navigation'],
    defaultZone: 'right'
  },
  'properties': {
    id: 'properties',
    name: 'Properties',
    description: 'Selected element properties',
    icon: Settings,
    category: 'development',
    group: 'code-analysis',
    tags: ['properties', 'settings', 'details'],
    defaultZone: 'right'
  },
  'layers': {
    id: 'layers',
    name: 'Layers',
    description: 'Visual layer management',
    icon: Layers,
    category: 'development',
    group: 'code-analysis',
    tags: ['layers', 'visual', 'ui'],
    defaultZone: 'right'
  },
  'assets': {
    id: 'assets',
    name: 'Assets',
    description: 'Project assets and resources',
    icon: Palette,
    category: 'development',
    group: 'development',
    tags: ['assets', 'resources', 'media'],
    defaultZone: 'right'
  },
  'settings': {
    id: 'settings',
    name: 'Settings',
    description: 'IDE settings and preferences',
    icon: Settings,
    category: 'utilities',
    tags: ['settings', 'preferences', 'config'],
    defaultZone: 'right'
  },
  'goal-planning': {
    id: 'goal-planning',
    name: 'Goal Planning',
    description: 'Goal management and planning (APOE)',
    icon: Target,
    category: 'ai',
    group: 'ai-tools',
    tags: ['goals', 'planning', 'apoe'],
    defaultZone: 'right'
  },
  'context-web': {
    id: 'context-web',
    name: 'Context Web',
    description: 'Visualize context relationships',
    icon: Network,
    category: 'ai',
    group: 'visualization',
    tags: ['context', 'visualization', 'graph'],
    defaultZone: 'right'
  },
  'nl-tag': {
    id: 'nl-tag',
    name: 'NL Tags',
    description: 'Natural language code tags',
    icon: FileText,
    category: 'utilities',
    tags: ['tags', 'nl', 'documentation'],
    defaultZone: 'right'
  },
  'tool-selection': {
    id: 'tool-selection',
    name: 'Tool Selection',
    description: 'MCP tool selection and metrics',
    icon: Zap,
    category: 'utilities',
    group: 'development',
    tags: ['tools', 'mcp', 'selection'],
    defaultZone: 'right'
  },
  
  // Bottom Panels
  'terminal': {
    id: 'terminal',
    name: 'Terminal',
    description: 'Integrated terminal',
    icon: Terminal,
    category: 'development',
    group: 'development',
    tags: ['terminal', 'shell', 'command'],
    defaultZone: 'bottom'
  },
  'problems': {
    id: 'problems',
    name: 'Problems',
    description: 'Code problems and diagnostics',
    icon: AlertCircle,
    category: 'debugging',
    group: 'debugging',
    tags: ['problems', 'errors', 'diagnostics'],
    defaultZone: 'bottom'
  },
  'output': {
    id: 'output',
    name: 'Output',
    description: 'Build and task output',
    icon: Output,
    category: 'debugging',
    group: 'debugging',
    tags: ['output', 'build', 'logs'],
    defaultZone: 'bottom'
  },
  'debug-console': {
    id: 'debug-console',
    name: 'Debug Console',
    description: 'Debug console and evaluation',
    icon: Bug,
    category: 'debugging',
    group: 'debugging',
    tags: ['debug', 'console', 'evaluation'],
    defaultZone: 'bottom'
  },
  'timeline': {
    id: 'timeline',
    name: 'Timeline',
    description: 'Bitemporal timeline with playback',
    icon: Clock,
    category: 'ai',
    group: 'visualization',
    tags: ['timeline', 'bitemporal', 'history'],
    defaultZone: 'bottom'
  },
  'file-changes': {
    id: 'file-changes',
    name: 'File Changes',
    description: 'Track file changes and diffs',
    icon: FileDiff,
    category: 'debugging',
    group: 'debugging',
    tags: ['changes', 'diff', 'git'],
    defaultZone: 'bottom'
  }
}

// Panel Lists by Zone
export const LEFT_PANELS: LeftPanelType[] = [
  'file-explorer',
  'component-library',
  'ai-memory',
  'git',
  'templates',
  'lucid-orchestrator',
  'consciousness-explorer',
  'tool-quality'
]

export const RIGHT_PANELS: RightPanelType[] = [
  'outline',
  'properties',
  'layers',
  'assets',
  'settings',
  'goal-planning',
  'context-web',
  'nl-tag',
  'tool-selection'
]

export const BOTTOM_PANELS: BottomPanelType[] = [
  'terminal',
  'problems',
  'output',
  'debug-console',
  'timeline',
  'file-changes'
]

// Helper Functions
export const getPanelById = (panelId: string): PanelMetadata | undefined => {
  return PANEL_METADATA[panelId]
}

export const getPanelsByGroup = (groupId: string): PanelMetadata[] => {
  return Object.values(PANEL_METADATA).filter(p => p.group === groupId)
}

export const getPanelsByCategory = (category: PanelMetadata['category']): PanelMetadata[] => {
  return Object.values(PANEL_METADATA).filter(p => p.category === category)
}

export const getGroupById = (groupId: string) => {
  return Object.values(PANEL_GROUPS).find(g => g.id === groupId)
}

export const getAllGroups = () => {
  return Object.values(PANEL_GROUPS)
}

export { PANEL_METADATA }

