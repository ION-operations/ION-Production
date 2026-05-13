/**
 * Panel Presets System
 * 
 * Phase 3.1: Predefined Layout Presets
 * 
 * Features:
 * - Common IDE layout presets
 * - Workflow-specific presets
 * - Quick layout switching
 * - Preset descriptions
 */

import { LeftPanelType, RightPanelType, BottomPanelType, MainContentMode } from './RevIDELayout'
import { LayoutConfig } from '../hooks/useLayoutSaving'

export interface PanelPreset {
  id: string
  name: string
  description: string
  icon: string
  category: 'development' | 'debugging' | 'ai-work' | 'exploration' | 'custom'
  config: LayoutConfig['config']
}

export const PANEL_PRESETS: PanelPreset[] = [
  // Development Presets
  {
    id: 'preset-development',
    name: 'Development',
    description: 'Standard development layout with file explorer, outline, and terminal',
    icon: '💻',
    category: 'development',
    config: {
      leftTop: 'file-explorer',
      leftBottom: 'git',
      rightTop: 'outline',
      rightBottom: 'properties',
      bottom: 'terminal',
      mainContentMode: 'code-editor',
      leftDrawerWidth: 250,
      rightDrawerWidth: 300,
      bottomDrawerHeight: 200
    }
  },
  {
    id: 'preset-full-stack',
    name: 'Full Stack',
    description: 'Full-stack development with component library and API tools',
    icon: '🌐',
    category: 'development',
    config: {
      leftTop: 'file-explorer',
      leftBottom: 'component-library',
      rightTop: 'outline',
      rightBottom: 'properties',
      bottom: 'terminal',
      mainContentMode: 'code-editor',
      leftDrawerWidth: 280,
      rightDrawerWidth: 320,
      bottomDrawerHeight: 200
    }
  },
  
  // Debugging Presets
  {
    id: 'preset-debugging',
    name: 'Debugging',
    description: 'Debug-focused layout with debug console, problems, and output panels',
    icon: '🐛',
    category: 'debugging',
    config: {
      leftTop: 'file-explorer',
      leftBottom: null,
      rightTop: 'outline',
      rightBottom: 'properties',
      bottom: 'debug-console',
      mainContentMode: 'code-editor',
      leftDrawerWidth: 250,
      rightDrawerWidth: 300,
      bottomDrawerHeight: 300
    }
  },
  {
    id: 'preset-troubleshooting',
    name: 'Troubleshooting',
    description: 'Comprehensive debugging with problems, output, and timeline',
    icon: '🔍',
    category: 'debugging',
    config: {
      leftTop: 'file-explorer',
      leftBottom: null,
      rightTop: 'problems',
      rightBottom: 'properties',
      bottom: 'timeline',
      mainContentMode: 'code-editor',
      leftDrawerWidth: 250,
      rightDrawerWidth: 350,
      bottomDrawerHeight: 250
    }
  },
  
  // AI Work Presets
  {
    id: 'preset-ai-development',
    name: 'AI Development',
    description: 'AI-focused layout with memory, context web, and consciousness visualization',
    icon: '🧠',
    category: 'ai-work',
    config: {
      leftTop: 'ai-memory',
      leftBottom: 'file-explorer',
      rightTop: 'context-web',
      rightBottom: 'goal-planning',
      bottom: 'timeline',
      mainContentMode: 'code-editor',
      leftDrawerWidth: 300,
      rightDrawerWidth: 350,
      bottomDrawerHeight: 200
    }
  },
  {
    id: 'preset-consciousness-exploration',
    name: 'Consciousness Exploration',
    description: 'Explore consciousness with visualization, evolution explorer, and context web',
    icon: '🌟',
    category: 'ai-work',
    config: {
      leftTop: 'consciousness-explorer',
      leftBottom: 'ai-memory',
      rightTop: 'context-web',
      rightBottom: 'goal-planning',
      bottom: null,
      mainContentMode: 'consciousness-visualization',
      leftDrawerWidth: 300,
      rightDrawerWidth: 350,
      bottomDrawerHeight: 0
    }
  },
  {
    id: 'preset-agent-management',
    name: 'Agent Management',
    description: 'Manage AI agents with orchestrator, evolution explorer, and tool selection',
    icon: '🤖',
    category: 'ai-work',
    config: {
      leftTop: 'lucid-orchestrator',
      leftBottom: 'tool-quality',
      rightTop: 'tool-selection',
      rightBottom: 'goal-planning',
      bottom: 'timeline',
      mainContentMode: 'agent-management',
      leftDrawerWidth: 320,
      rightDrawerWidth: 350,
      bottomDrawerHeight: 200
    }
  },
  
  // Exploration Presets
  {
    id: 'preset-code-exploration',
    name: 'Code Exploration',
    description: 'Explore codebase with outline, component library, and layers',
    icon: '🔎',
    category: 'exploration',
    config: {
      leftTop: 'file-explorer',
      leftBottom: 'component-library',
      rightTop: 'outline',
      rightBottom: 'layers',
      bottom: null,
      mainContentMode: 'code-editor',
      leftDrawerWidth: 280,
      rightDrawerWidth: 350,
      bottomDrawerHeight: 0
    }
  },
  {
    id: 'preset-evolution-analysis',
    name: 'Evolution Analysis',
    description: 'Analyze evolution with timeline, context web, and evolution explorer',
    icon: '📊',
    category: 'exploration',
    config: {
      leftTop: 'file-explorer',
      leftBottom: null,
      rightTop: 'context-web',
      rightBottom: 'goal-planning',
      bottom: 'timeline',
      mainContentMode: 'evolution-explorer',
      leftDrawerWidth: 250,
      rightDrawerWidth: 350,
      bottomDrawerHeight: 250
    }
  },
  
  // Minimal Presets
  {
    id: 'preset-minimal',
    name: 'Minimal',
    description: 'Clean minimal layout with just essentials',
    icon: '✨',
    category: 'custom',
    config: {
      leftTop: 'file-explorer',
      leftBottom: null,
      rightTop: null,
      rightBottom: null,
      bottom: null,
      mainContentMode: 'code-editor',
      leftDrawerWidth: 200,
      rightDrawerWidth: 0,
      bottomDrawerHeight: 0
    }
  },
  {
    id: 'preset-focused-coding',
    name: 'Focused Coding',
    description: 'Distraction-free coding with minimal panels',
    icon: '🎯',
    category: 'custom',
    config: {
      leftTop: null,
      leftBottom: null,
      rightTop: 'outline',
      rightBottom: null,
      bottom: null,
      mainContentMode: 'code-editor',
      leftDrawerWidth: 0,
      rightDrawerWidth: 250,
      bottomDrawerHeight: 0
    }
  }
]

export const getPresetById = (presetId: string): PanelPreset | undefined => {
  return PANEL_PRESETS.find(p => p.id === presetId)
}

export const getPresetsByCategory = (category: PanelPreset['category']): PanelPreset[] => {
  return PANEL_PRESETS.filter(p => p.category === category)
}

export const createLayoutFromPreset = (preset: PanelPreset): LayoutConfig => {
  return {
    id: `layout-preset-${preset.id}-${Date.now()}`,
    name: preset.name,
    description: preset.description,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    config: preset.config,
    isDefault: false
  }
}

