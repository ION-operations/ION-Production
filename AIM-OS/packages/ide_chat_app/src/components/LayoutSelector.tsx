/**
 * Layout Selector Component
 * 
 * Phase 3.3: Layout Management UI
 * 
 * Features:
 * - Quick layout switching
 * - Save current layout
 * - Delete layouts
 * - Set default layout
 */

import React, { useState, useEffect, useRef } from 'react'
import { Save, Trash2, Star, Copy, X, Check, Sparkles } from 'lucide-react'
import { useLayoutSaving, LayoutConfig } from '../hooks/useLayoutSaving'
import { LeftPanelType, RightPanelType, BottomPanelType, MainContentMode } from './RevIDELayout'
import { PANEL_PRESETS, PanelPreset, createLayoutFromPreset } from './PanelPresets'

interface LayoutSelectorProps {
  currentConfig: {
    leftTop: LeftPanelType
    leftBottom: LeftPanelType | null
    rightTop: RightPanelType
    rightBottom: RightPanelType | null
    bottom: BottomPanelType | null
    mainContentMode: MainContentMode
  }
  onLoadLayout: (config: LayoutConfig['config']) => void
}

export const LayoutSelector: React.FC<LayoutSelectorProps> = ({
  currentConfig,
  onLoadLayout
}) => {
  const {
    layouts,
    currentLayoutId,
    saveLayout,
    deleteLayout,
    loadLayout,
    setDefaultLayout,
    duplicateLayout
  } = useLayoutSaving()

  const [showSaveDialog, setShowSaveDialog] = useState(false)
  const [showPresets, setShowPresets] = useState(false)
  const [layoutName, setLayoutName] = useState('')
  const [layoutDescription, setLayoutDescription] = useState('')
  const [selectedLayoutId, setSelectedLayoutId] = useState<string | null>(currentLayoutId)
  const presetsRef = useRef<HTMLDivElement>(null)

  // Close presets dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (presetsRef.current && !presetsRef.current.contains(event.target as Node)) {
        setShowPresets(false)
      }
    }

    if (showPresets) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showPresets])

  const handleSave = async () => {
    if (!layoutName.trim()) return

    await saveLayout(
      layoutName,
      currentConfig,
      layoutDescription || undefined
    )
    setShowSaveDialog(false)
    setLayoutName('')
    setLayoutDescription('')
  }

  const handleLoadPreset = (preset: PanelPreset) => {
    const layout = createLayoutFromPreset(preset)
    onLoadLayout(layout.config)
    setShowPresets(false)
  }

  const handleLoad = (layoutId: string) => {
    const layout = loadLayout(layoutId)
    if (layout) {
      onLoadLayout(layout.config)
      setSelectedLayoutId(layoutId)
    }
  }

  const handleDelete = async (layoutId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (confirm('Are you sure you want to delete this layout?')) {
      await deleteLayout(layoutId)
      if (selectedLayoutId === layoutId) {
        setSelectedLayoutId(null)
      }
    }
  }

  const handleSetDefault = async (layoutId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    await setDefaultLayout(layoutId)
  }

  const handleDuplicate = async (layoutId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    const layout = layouts.find(l => l.id === layoutId)
    if (layout) {
      const newName = `${layout.name} (Copy)`
      await duplicateLayout(layoutId, newName)
    }
  }

  return (
    <div className="flex items-center gap-2">
      {/* Presets Button */}
      <div className="relative group" ref={presetsRef}>
        <button
          onClick={() => setShowPresets(!showPresets)}
          className="px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors flex items-center gap-1"
          aria-label="Show layout presets"
          title="Layout Presets"
        >
          <Sparkles className="w-4 h-4" />
          Presets
        </button>
        
        {/* Presets Dropdown */}
        {showPresets && (
          <div className="absolute left-0 top-full mt-1 w-80 bg-gray-800 border border-gray-700 rounded shadow-lg z-50 max-h-96 overflow-y-auto">
            <div className="p-2">
              {/* Development Presets */}
              <div className="mb-3">
                <div className="text-xs font-semibold text-gray-500 uppercase mb-2 px-2">Development</div>
                {PANEL_PRESETS.filter(p => p.category === 'development').map(preset => (
                  <button
                    key={preset.id}
                    onClick={() => handleLoadPreset(preset)}
                    className="w-full text-left p-2 rounded hover:bg-gray-700 transition-colors mb-1"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{preset.icon}</span>
                      <div className="flex-1">
                        <div className="text-sm text-gray-300 font-medium">{preset.name}</div>
                        <div className="text-xs text-gray-500">{preset.description}</div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
              
              {/* Debugging Presets */}
              <div className="mb-3">
                <div className="text-xs font-semibold text-gray-500 uppercase mb-2 px-2">Debugging</div>
                {PANEL_PRESETS.filter(p => p.category === 'debugging').map(preset => (
                  <button
                    key={preset.id}
                    onClick={() => handleLoadPreset(preset)}
                    className="w-full text-left p-2 rounded hover:bg-gray-700 transition-colors mb-1"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{preset.icon}</span>
                      <div className="flex-1">
                        <div className="text-sm text-gray-300 font-medium">{preset.name}</div>
                        <div className="text-xs text-gray-500">{preset.description}</div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
              
              {/* AI Work Presets */}
              <div className="mb-3">
                <div className="text-xs font-semibold text-gray-500 uppercase mb-2 px-2">AI Work</div>
                {PANEL_PRESETS.filter(p => p.category === 'ai-work').map(preset => (
                  <button
                    key={preset.id}
                    onClick={() => handleLoadPreset(preset)}
                    className="w-full text-left p-2 rounded hover:bg-gray-700 transition-colors mb-1"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{preset.icon}</span>
                      <div className="flex-1">
                        <div className="text-sm text-gray-300 font-medium">{preset.name}</div>
                        <div className="text-xs text-gray-500">{preset.description}</div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
              
              {/* Exploration Presets */}
              <div className="mb-3">
                <div className="text-xs font-semibold text-gray-500 uppercase mb-2 px-2">Exploration</div>
                {PANEL_PRESETS.filter(p => p.category === 'exploration').map(preset => (
                  <button
                    key={preset.id}
                    onClick={() => handleLoadPreset(preset)}
                    className="w-full text-left p-2 rounded hover:bg-gray-700 transition-colors mb-1"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{preset.icon}</span>
                      <div className="flex-1">
                        <div className="text-sm text-gray-300 font-medium">{preset.name}</div>
                        <div className="text-xs text-gray-500">{preset.description}</div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
              
              {/* Custom Presets */}
              <div className="mb-3">
                <div className="text-xs font-semibold text-gray-500 uppercase mb-2 px-2">Custom</div>
                {PANEL_PRESETS.filter(p => p.category === 'custom').map(preset => (
                  <button
                    key={preset.id}
                    onClick={() => handleLoadPreset(preset)}
                    className="w-full text-left p-2 rounded hover:bg-gray-700 transition-colors mb-1"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{preset.icon}</span>
                      <div className="flex-1">
                        <div className="text-sm text-gray-300 font-medium">{preset.name}</div>
                        <div className="text-xs text-gray-500">{preset.description}</div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Layout Selector */}
      <select
        value={selectedLayoutId || ''}
        onChange={(e) => {
          const layoutId = e.target.value
          if (layoutId) {
            handleLoad(layoutId)
          } else {
            setSelectedLayoutId(null)
          }
        }}
        className="px-3 py-1.5 text-sm bg-gray-800 border border-gray-700 rounded text-gray-300 hover:bg-gray-700 focus:outline-none focus:border-blue-500"
        aria-label="Select layout"
      >
        <option value="">Default Layout</option>
        {layouts.map(layout => (
          <option key={layout.id} value={layout.id}>
            {layout.name} {layout.isDefault && '⭐'}
          </option>
        ))}
      </select>

      {/* Save Button */}
      <button
        onClick={() => setShowSaveDialog(true)}
        className="px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors flex items-center gap-1"
        aria-label="Save current layout"
        title="Save Layout"
      >
        <Save className="w-4 h-4" />
        Save
      </button>

      {/* Save Dialog */}
      {showSaveDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowSaveDialog(false)}>
          <div
            className="bg-gray-800 rounded-lg border border-gray-700 p-4 w-96 max-w-full"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-300">Save Layout</h3>
              <button
                onClick={() => setShowSaveDialog(false)}
                className="text-gray-400 hover:text-gray-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Layout Name</label>
                <input
                  type="text"
                  value={layoutName}
                  onChange={(e) => setLayoutName(e.target.value)}
                  placeholder="My Layout"
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  autoFocus
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleSave()
                    }
                  }}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Description (Optional)</label>
                <textarea
                  value={layoutDescription}
                  onChange={(e) => setLayoutDescription(e.target.value)}
                  placeholder="Layout description..."
                  rows={2}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none"
                />
              </div>
              <div className="flex gap-2 pt-2">
                <button
                  onClick={() => setShowSaveDialog(false)}
                  className="flex-1 px-4 py-2 text-sm bg-gray-700 text-gray-300 rounded hover:bg-gray-600 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  disabled={!layoutName.trim()}
                  className={`flex-1 px-4 py-2 text-sm rounded transition-colors flex items-center justify-center gap-1 ${
                    layoutName.trim()
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-700 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  <Save className="w-4 h-4" />
                  Save
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Layout List (for management) */}
      {layouts.length > 0 && (
        <div className="relative group">
          <button
            className="px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
            aria-label="Manage layouts"
            title="Manage Layouts"
          >
            {layouts.length} Layout{layouts.length !== 1 ? 's' : ''}
          </button>
          <div className="absolute right-0 top-full mt-1 w-64 bg-gray-800 border border-gray-700 rounded shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
            <div className="p-2 max-h-64 overflow-y-auto">
              {layouts.map(layout => (
                <div
                  key={layout.id}
                  className={`p-2 rounded cursor-pointer transition-colors mb-1 ${
                    selectedLayoutId === layout.id
                      ? 'bg-blue-600/20 border border-blue-500'
                      : 'bg-gray-700/50 hover:bg-gray-700 border border-transparent'
                  }`}
                  onClick={() => handleLoad(layout.id)}
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-1">
                      <span className="text-sm text-gray-300 font-medium">{layout.name}</span>
                      {layout.isDefault && <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />}
                    </div>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={(e) => handleDuplicate(layout.id, e)}
                        className="p-1 text-gray-400 hover:text-gray-300 hover:bg-gray-600 rounded"
                        title="Duplicate"
                      >
                        <Copy className="w-3 h-3" />
                      </button>
                      {!layout.isDefault && (
                        <button
                          onClick={(e) => handleSetDefault(layout.id, e)}
                          className="p-1 text-gray-400 hover:text-yellow-400 hover:bg-gray-600 rounded"
                          title="Set as default"
                        >
                          <Star className="w-3 h-3" />
                        </button>
                      )}
                      <button
                        onClick={(e) => handleDelete(layout.id, e)}
                        className="p-1 text-gray-400 hover:text-red-400 hover:bg-gray-600 rounded"
                        title="Delete"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                  {layout.description && (
                    <p className="text-xs text-gray-500 line-clamp-1">{layout.description}</p>
                  )}
                  <p className="text-xs text-gray-600 mt-1">
                    {new Date(layout.updatedAt).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

