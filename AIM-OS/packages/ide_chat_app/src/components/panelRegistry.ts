/**
 * Panel Registry - Centralized Panel Definitions
 * 
 * Phase 1.2: Panel Management System
 * 
 * This file defines all panels available in Rev's IDE Layout Prototype.
 * Each panel has:
 * - Unique ID
 * - Display name
 * - Icon
 * - Default zone (left/right/bottom/main)
 * - Keyboard shortcut
 * - AIM-OS integration points
 * - Panel-specific configuration
 */

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
  Package,
  Target,
  Tag,
  Wrench,
  AlertTriangle,
  Output,
  Bug,
  Calendar,
  FileDiff,
  BarChart3,
  Network,
  Sparkles,
  Users,
  Workflow,
  BookOpen,
  Eye,
  Zap
} from 'lucide-react'
import { LucideIcon } from 'lucide-react'

export type PanelZone = 'left' | 'right' | 'bottom' | 'main' | 'floating'
export type PanelCategory = 'file' | 'code' | 'ai' | 'system' | 'visualization' | 'tool' | 'revolutionary'

export interface PanelDefinition {
  id: string
  name: string
  description: string
  icon: LucideIcon
  category: PanelCategory
  defaultZone: PanelZone
  defaultSize?: number // Percentage (0-100)
  minSize?: number // Percentage
  maxSize?: number // Percentage
  keyboardShortcut?: string // e.g., "Ctrl+Shift+E"
  aimosIntegration?: {
    cmc?: boolean // Context Memory Core
    hhni?: boolean // Hierarchical Hypergraph Neural Index
    vif?: boolean // Verifiable Intelligence Framework
    seg?: boolean // Synthesis & Evidence Graph
    apoe?: boolean // AI-Powered Orchestration Engine
    sdfCvf?: boolean // Self-Directed Feedback
    cas?: boolean // Consciousness Analysis System
    tcs?: boolean // Timeline Context System
  }
  isRevolutionary?: boolean // ⭐ Revolutionary feature
  component?: React.ComponentType<any> // Component to render
  mockData?: any // Mock data for prototype
}

/**
 * Left Drawer Panels (8 panels)
 */
export const LEFT_PANELS: PanelDefinition[] = [
  {
    id: 'file-explorer',
    name: 'File Explorer',
    description: 'Browse project files and folders',
    icon: FolderOpen,
    category: 'file',
    defaultZone: 'left',
    defaultSize: 50,
    minSize: 20,
    maxSize: 80,
    keyboardShortcut: 'Ctrl+Shift+E',
    aimosIntegration: {
      cmc: true, // File operations
      hhni: true, // Semantic search
      vif: true, // File confidence
    },
  },
  {
    id: 'component-library',
    name: 'Component Library',
    description: 'Browse and manage reusable components',
    icon: Package,
    category: 'code',
    defaultZone: 'left',
    defaultSize: 50,
    minSize: 20,
    maxSize: 80,
    keyboardShortcut: 'Ctrl+Shift+L',
    aimosIntegration: {
      cmc: true, // Component storage
      hhni: true, // Component search
      seg: true, // Component relationships
    },
  },
  {
    id: 'ai-memory',
    name: 'AI Memory',
    description: 'Browse AI memories and context',
    icon: Database,
    category: 'ai',
    defaultZone: 'left',
    defaultSize: 50,
    minSize: 20,
    maxSize: 80,
    keyboardShortcut: 'Ctrl+Shift+M',
    aimosIntegration: {
      cmc: true, // Memory storage
      hhni: true, // Memory search
      vif: true, // Memory confidence
    },
  },
  {
    id: 'git',
    name: 'Git',
    description: 'Git version control operations',
    icon: GitBranch,
    category: 'file',
    defaultZone: 'left',
    defaultSize: 50,
    minSize: 20,
    maxSize: 80,
    keyboardShortcut: 'Ctrl+Shift+G',
    aimosIntegration: {
      cmc: true, // Git history
      vif: true, // Change confidence
      seg: true, // Change evidence
    },
  },
  {
    id: 'templates',
    name: 'Templates',
    description: 'Browse and use code templates',
    icon: FileText,
    category: 'code',
    defaultZone: 'left',
    defaultSize: 50,
    minSize: 20,
    maxSize: 80,
    keyboardShortcut: 'Ctrl+Shift+T',
    aimosIntegration: {
      cmc: true, // Template storage
      hhni: true, // Template search
    },
  },
  {
    id: 'lucid-orchestrator',
    name: 'Lucid Orchestrator',
    description: 'Visual blueprint editor and orchestration',
    icon: Brain,
    category: 'system',
    defaultZone: 'left',
    defaultSize: 50,
    minSize: 20,
    maxSize: 80,
    keyboardShortcut: 'Ctrl+Shift+B',
    aimosIntegration: {
      apoe: true, // Orchestration
      vif: true, // Validation
      cmc: true, // Blueprint storage
    },
  },
  {
    id: 'consciousness-explorer',
    name: 'Consciousness Explorer',
    description: 'Explore AI consciousness patterns',
    icon: Brain,
    category: 'visualization',
    defaultZone: 'left',
    defaultSize: 50,
    minSize: 20,
    maxSize: 80,
    keyboardShortcut: 'Ctrl+Shift+C',
    aimosIntegration: {
      cas: true, // Consciousness analysis
      seg: true, // Consciousness evidence
      vif: true, // Consciousness confidence
    },
  },
  {
    id: 'tool-quality',
    name: 'Tool Quality Dashboard',
    description: 'Monitor tool quality and performance',
    icon: BarChart3,
    category: 'tool',
    defaultZone: 'left',
    defaultSize: 50,
    minSize: 20,
    maxSize: 80,
    keyboardShortcut: 'Ctrl+Shift+Q',
    aimosIntegration: {
      vif: true, // Tool confidence
      seg: true, // Tool evidence
    },
  },
]

/**
 * Right Drawer Panels (9 panels)
 */
export const RIGHT_PANELS: PanelDefinition[] = [
  {
    id: 'outline',
    name: 'Outline',
    description: 'File structure and symbol navigation',
    icon: Layers,
    category: 'code',
    defaultZone: 'right',
    defaultSize: 50,
    minSize: 20,
    maxSize: 80,
    keyboardShortcut: 'Ctrl+Shift+O',
    aimosIntegration: {
      hhni: true, // Symbol navigation
      cmc: true, // Outline cache
    },
  },
  {
    id: 'properties',
    name: 'Properties',
    description: 'Edit selected element properties',
    icon: Settings,
    category: 'code',
    defaultZone: 'right',
    defaultSize: 50,
    minSize: 20,
    maxSize: 80,
    keyboardShortcut: 'Ctrl+Shift+P',
    aimosIntegration: {
      vif: true, // Property validation
      seg: true, // Property relationships
    },
  },
  {
    id: 'layers',
    name: 'Layers',
    description: 'Z-index and layer management',
    icon: Layers,
    category: 'code',
    defaultZone: 'right',
    defaultSize: 50,
    minSize: 20,
    maxSize: 80,
    keyboardShortcut: 'Ctrl+Shift+L',
    aimosIntegration: {
      cmc: true, // Layer storage
      vif: true, // Layer validation
    },
  },
  {
    id: 'assets',
    name: 'Assets',
    description: 'Image, font, and icon library',
    icon: FileText,
    category: 'file',
    defaultZone: 'right',
    defaultSize: 50,
    minSize: 20,
    maxSize: 80,
    keyboardShortcut: 'Ctrl+Shift+A',
    aimosIntegration: {
      cmc: true, // Asset storage
      hhni: true, // Asset search
    },
  },
  {
    id: 'settings',
    name: 'Settings',
    description: 'IDE settings and preferences',
    icon: Settings,
    category: 'system',
    defaultZone: 'right',
    defaultSize: 50,
    minSize: 20,
    maxSize: 80,
    keyboardShortcut: 'Ctrl+,',
    aimosIntegration: {
      cmc: true, // Settings storage
      vif: true, // Settings validation
    },
  },
  {
    id: 'goal-planning',
    name: 'Goal Planning',
    description: 'Track goals and key results',
    icon: Target,
    category: 'system',
    defaultZone: 'right',
    defaultSize: 50,
    minSize: 20,
    maxSize: 80,
    keyboardShortcut: 'Ctrl+Shift+G',
    aimosIntegration: {
      tcs: true, // Goal Timeline
      vif: true, // Goal confidence
    },
  },
  {
    id: 'context-web',
    name: 'Context Web',
    description: 'Interactive context graph visualization',
    icon: Network,
    category: 'revolutionary',
    defaultZone: 'right',
    defaultSize: 50,
    minSize: 20,
    maxSize: 80,
    keyboardShortcut: 'Ctrl+Shift+W',
    isRevolutionary: true, // ⭐
    aimosIntegration: {
      hhni: true, // Context retrieval
      seg: true, // Context relationships
      vif: true, // Context accuracy
    },
  },
  {
    id: 'nl-tag',
    name: 'NL Tag',
    description: 'Natural language tag management',
    icon: Tag,
    category: 'tool',
    defaultZone: 'right',
    defaultSize: 50,
    minSize: 20,
    maxSize: 80,
    keyboardShortcut: 'Ctrl+Shift+N',
    aimosIntegration: {
      sdfCvf: true, // Tag validation
      cmc: true, // Tag storage
      vif: true, // Tag confidence
    },
  },
  {
    id: 'tool-selection',
    name: 'Tool Selection',
    description: 'Select and configure MCP tools',
    icon: Wrench,
    category: 'tool',
    defaultZone: 'right',
    defaultSize: 50,
    minSize: 20,
    maxSize: 80,
    keyboardShortcut: 'Ctrl+Shift+K',
    aimosIntegration: {
      vif: true, // Tool confidence
      apoe: true, // Tool routing
    },
  },
]

/**
 * Bottom Drawer Panels (6 panels)
 */
export const BOTTOM_PANELS: PanelDefinition[] = [
  {
    id: 'terminal',
    name: 'Terminal',
    description: 'Command line terminal',
    icon: Terminal,
    category: 'tool',
    defaultZone: 'bottom',
    defaultSize: 30,
    minSize: 15,
    maxSize: 70,
    keyboardShortcut: 'Ctrl+`',
    aimosIntegration: {
      cmc: true, // Command history
      vif: true, // Command validation
    },
  },
  {
    id: 'problems',
    name: 'Problems',
    description: 'Errors, warnings, and info messages',
    icon: AlertTriangle,
    category: 'code',
    defaultZone: 'bottom',
    defaultSize: 30,
    minSize: 15,
    maxSize: 70,
    keyboardShortcut: 'Ctrl+Shift+M',
    aimosIntegration: {
      sdfCvf: true, // Quartet violations
      vif: true, // Problem confidence
      seg: true, // Problem evidence
    },
  },
  {
    id: 'output',
    name: 'Output',
    description: 'Build logs and execution output',
    icon: Output,
    category: 'tool',
    defaultZone: 'bottom',
    defaultSize: 30,
    minSize: 15,
    maxSize: 70,
    keyboardShortcut: 'Ctrl+Shift+U',
    aimosIntegration: {
      cmc: true, // Output storage
      vif: true, // Output validation
    },
  },
  {
    id: 'debug-console',
    name: 'Debug Console',
    description: 'Debug console and watch expressions',
    icon: Bug,
    category: 'code',
    defaultZone: 'bottom',
    defaultSize: 30,
    minSize: 15,
    maxSize: 70,
    keyboardShortcut: 'Ctrl+Shift+Y',
    aimosIntegration: {
      vif: true, // Debug confidence
      cmc: true, // Debug history
    },
  },
  {
    id: 'timeline',
    name: 'Bitemporal Timeline',
    description: 'Sequential timeline with playback controls',
    icon: Calendar,
    category: 'revolutionary',
    defaultZone: 'bottom',
    defaultSize: 30,
    minSize: 15,
    maxSize: 70,
    keyboardShortcut: 'Ctrl+Shift+T',
    isRevolutionary: true, // ⭐
    aimosIntegration: {
      tcs: true, // Timeline entries
      vif: true, // Timeline confidence
    },
  },
  {
    id: 'file-changes',
    name: 'File Changes Viewer',
    description: 'View file change history and diffs',
    icon: FileDiff,
    category: 'file',
    defaultZone: 'bottom',
    defaultSize: 30,
    minSize: 15,
    maxSize: 70,
    keyboardShortcut: 'Ctrl+Shift+D',
    aimosIntegration: {
      cmc: true, // Change history
      vif: true, // Change confidence
      seg: true, // Change evidence
    },
  },
]

/**
 * Main Content Modes (6 modes)
 */
export const MAIN_MODES: PanelDefinition[] = [
  {
    id: 'code-editor',
    name: 'Code Editor',
    description: 'Monaco editor with AIM-OS integration',
    icon: Code,
    category: 'code',
    defaultZone: 'main',
    defaultSize: 100,
    keyboardShortcut: 'Ctrl+1',
    aimosIntegration: {
      cmc: true, // Code storage
      hhni: true, // Code search
      vif: true, // Code confidence
    },
  },
  {
    id: 'animforge',
    name: 'AnimForge',
    description: 'Revolutionary 2D animation system with AI auto-rigging and motion capture',
    icon: Sparkles,
    category: 'revolutionary',
    defaultZone: 'main',
    defaultSize: 100,
    keyboardShortcut: 'Ctrl+6',
    isRevolutionary: true, // ⭐
    aimosIntegration: {
      cmc: true, // Animation storage
      hhni: true, // Character consistency
      vif: true, // Quality confidence
      tcs: true, // Timeline tracking
      apoe: true, // AI orchestration
    },
  },
  {
    id: 'evolution-explorer',
    name: 'Evolution Explorer',
    description: 'Bidirectional graph: Timeline ↔ Chain ↔ Goals',
    icon: Network,
    category: 'revolutionary',
    defaultZone: 'main',
    defaultSize: 100,
    keyboardShortcut: 'Ctrl+2',
    isRevolutionary: true, // ⭐
    aimosIntegration: {
      tcs: true, // Timeline data
      seg: true, // Chain data
      vif: true, // Goal data
    },
  },
  {
    id: 'agent-management',
    name: 'Agent Management Dashboard',
    description: 'Multi-agent coordination and management',
    icon: Users,
    category: 'ai',
    defaultZone: 'main',
    defaultSize: 100,
    keyboardShortcut: 'Ctrl+3',
    aimosIntegration: {
      apoe: true, // Agent orchestration
      cas: true, // Agent consciousness
      vif: true, // Agent confidence
    },
  },
  {
    id: 'consciousness-visualization',
    name: 'Consciousness Visualization',
    description: 'Interactive consciousness state visualization',
    icon: Brain,
    category: 'revolutionary',
    defaultZone: 'main',
    defaultSize: 100,
    keyboardShortcut: 'Ctrl+4',
    isRevolutionary: true, // ⭐
    aimosIntegration: {
      cas: true, // Consciousness analysis
      seg: true, // Consciousness evidence
      vif: true, // Consciousness confidence
    },
  },
  {
    id: 'lucid-orchestrator',
    name: 'Lucid Orchestrator',
    description: 'Main orchestrator interface',
    icon: Zap,
    category: 'system',
    defaultZone: 'main',
    defaultSize: 100,
    keyboardShortcut: 'Ctrl+5',
    aimosIntegration: {
      apoe: true, // Orchestration
      vif: true, // Validation
      cmc: true, // Blueprint storage
    },
  },
]

/**
 * All Panels Registry
 */
export const ALL_PANELS: PanelDefinition[] = [
  ...LEFT_PANELS,
  ...RIGHT_PANELS,
  ...BOTTOM_PANELS,
  ...MAIN_MODES,
]

/**
 * Get panel by ID
 */
export function getPanelById(id: string): PanelDefinition | undefined {
  return ALL_PANELS.find(panel => panel.id === id)
}

/**
 * Get panels by zone
 */
export function getPanelsByZone(zone: PanelZone): PanelDefinition[] {
  return ALL_PANELS.filter(panel => panel.defaultZone === zone)
}

/**
 * Get panels by category
 */
export function getPanelsByCategory(category: PanelCategory): PanelDefinition[] {
  return ALL_PANELS.filter(panel => panel.category === category)
}

/**
 * Get revolutionary panels
 */
export function getRevolutionaryPanels(): PanelDefinition[] {
  return ALL_PANELS.filter(panel => panel.isRevolutionary === true)
}

/**
 * Panel Registry Statistics
 */
export const PANEL_STATS = {
  total: ALL_PANELS.length,
  left: LEFT_PANELS.length,
  right: RIGHT_PANELS.length,
  bottom: BOTTOM_PANELS.length,
  main: MAIN_MODES.length,
  revolutionary: getRevolutionaryPanels().length,
  byCategory: {
    file: getPanelsByCategory('file').length,
    code: getPanelsByCategory('code').length,
    ai: getPanelsByCategory('ai').length,
    system: getPanelsByCategory('system').length,
    visualization: getPanelsByCategory('visualization').length,
    tool: getPanelsByCategory('tool').length,
    revolutionary: getPanelsByCategory('revolutionary').length,
  },
}

