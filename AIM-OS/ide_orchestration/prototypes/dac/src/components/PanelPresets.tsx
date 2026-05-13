// Panel Presets Component - V2 Layout System Enhancement
// Quick layout presets for different workflows

import React from 'react'
import { usePanelStore } from '../store/panelStore'
import { Code, Bug, Search, Settings, X } from 'lucide-react'

export type PresetType = 'developer' | 'debug' | 'research' | 'minimal' | 'full'

interface Preset {
  id: PresetType
  name: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  panels: {
    left: string[]
    right: string[]
    bottom: string[]
  }
  thumbnail: {
    leftOpen: boolean
    rightOpen: boolean
    bottomOpen: boolean
    leftSize: number
    rightSize: number
    bottomSize: number
  }
}

const PRESETS: Preset[] = [
  {
    id: 'developer',
    name: 'Developer',
    description: 'Code editor focused with file explorer and terminal',
    icon: Code,
    panels: {
      left: ['file-explorer', 'memory-browser'],
      right: ['outline', 'context-web'],
      bottom: ['terminal', 'problems']
    },
    thumbnail: {
      leftOpen: true,
      rightOpen: true,
      bottomOpen: true,
      leftSize: 20,
      rightSize: 25,
      bottomSize: 25
    }
  },
  {
    id: 'debug',
    name: 'Debug',
    description: 'Debugging focused with problems panel and system status',
    icon: Bug,
    panels: {
      left: ['file-explorer', 'system-status'],
      right: ['problems', 'context-web'],
      bottom: ['terminal', 'debug-console']
    },
    thumbnail: {
      leftOpen: true,
      rightOpen: true,
      bottomOpen: true,
      leftSize: 20,
      rightSize: 30,
      bottomSize: 30
    }
  },
  {
    id: 'research',
    name: 'Research',
    description: 'Research focused with context web and evolution explorer',
    icon: Search,
    panels: {
      left: ['memory-browser', 'system-status'],
      right: ['context-web', 'evolution-explorer'],
      bottom: ['timeline-view', 'consciousness-visualization']
    },
    thumbnail: {
      leftOpen: true,
      rightOpen: true,
      bottomOpen: true,
      leftSize: 25,
      rightSize: 30,
      bottomSize: 30
    }
  },
  {
    id: 'minimal',
    name: 'Minimal',
    description: 'Minimal layout with just code editor',
    icon: Settings,
    panels: {
      left: [],
      right: [],
      bottom: []
    },
    thumbnail: {
      leftOpen: false,
      rightOpen: false,
      bottomOpen: false,
      leftSize: 0,
      rightSize: 0,
      bottomSize: 0
    }
  },
  {
    id: 'full',
    name: 'Full',
    description: 'All panels visible for comprehensive view',
    icon: Settings,
    panels: {
      left: ['file-explorer', 'memory-browser', 'system-status'],
      right: ['context-web', 'timeline-view', 'outline', 'problems'],
      bottom: ['terminal', 'evolution-explorer', 'consciousness-visualization', 'aimos-orchestration']
    },
    thumbnail: {
      leftOpen: true,
      rightOpen: true,
      bottomOpen: true,
      leftSize: 25,
      rightSize: 30,
      bottomSize: 30
    }
  }
]

// Preset Thumbnail Component
const PresetThumbnail: React.FC<{ preset: Preset }> = ({ preset }) => {
  const { thumbnail } = preset
  
  return (
    <div className="w-full h-16 bg-gray-900 rounded border border-gray-700 relative overflow-hidden">
      {/* Left Panel */}
      {thumbnail.leftOpen && (
        <div 
          className="absolute left-0 top-0 bottom-0 bg-blue-600/30 border-r border-blue-500/50"
          style={{ width: `${thumbnail.leftSize}%` }}
        />
      )}
      
      {/* Right Panel */}
      {thumbnail.rightOpen && (
        <div 
          className="absolute right-0 top-0 bottom-0 bg-green-600/30 border-l border-green-500/50"
          style={{ width: `${thumbnail.rightSize}%` }}
        />
      )}
      
      {/* Bottom Panel */}
      {thumbnail.bottomOpen && (
        <div 
          className="absolute left-0 right-0 bottom-0 bg-purple-600/30 border-t border-purple-500/50"
          style={{ height: `${thumbnail.bottomSize}%` }}
        />
      )}
      
      {/* Main Content Area */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-[8px] text-gray-500 font-medium">
          {preset.panels.left.length + preset.panels.right.length + preset.panels.bottom.length} panels
        </div>
      </div>
    </div>
  )
}

export const PanelPresets: React.FC<{ onClose?: () => void }> = ({ onClose }) => {
  const { applyPreset } = usePanelStore()
  
  const handleApplyPreset = (preset: Preset) => {
    applyPreset(preset.id)
    onClose?.()
  }
  
  return (
    <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-300">Panel Presets</h3>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-gray-200"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
      
      <div className="grid grid-cols-1 gap-2">
        {PRESETS.map((preset) => {
          const Icon = preset.icon
          return (
            <button
              key={preset.id}
              onClick={() => handleApplyPreset(preset)}
              className="p-3 rounded border border-gray-700 bg-gray-900 hover:border-blue-500 hover:bg-blue-900/20 transition-all text-left"
            >
              {/* Thumbnail */}
              <PresetThumbnail preset={preset} />
              
              <div className="flex items-start gap-3 mt-3">
                <Icon className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-200">{preset.name}</div>
                  <div className="text-xs text-gray-500 mt-1">{preset.description}</div>
                  <div className="text-xs text-gray-600 mt-2">
                    {preset.panels.left.length + preset.panels.right.length + preset.panels.bottom.length} panels
                  </div>
                </div>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}

