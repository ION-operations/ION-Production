// Layout Manager Component - V2 Layout System Enhancement
// Drag-and-drop, layout save/load, panel presets, and view-specific layouts

import React, { useState, useRef, useEffect } from 'react'
import { usePanelStore, Layout } from '../store/panelStore'
import { Save, Layout as LayoutIcon, X, Plus, Trash2, Lock, Unlock, Code, GitBranch, Brain, Network, Globe, FileText, Eye, MessageSquare } from 'lucide-react'

type MainViewType = 'code' | 'evolution' | 'consciousness' | 'orchestration' | 'app-preview' | 'file-preview' | 'canvas' | 'manager-ai-chat'

const VIEW_ICONS: Record<MainViewType, React.ComponentType<{ className?: string }>> = {
  'code': Code,
  'evolution': GitBranch,
  'consciousness': Brain,
  'orchestration': Network,
  'app-preview': Globe,
  'file-preview': Eye,
  'canvas': FileText,
  'manager-ai-chat': MessageSquare,
}

const VIEW_LABELS: Record<MainViewType, string> = {
  'code': 'Code',
  'evolution': 'Evolution',
  'consciousness': 'Consciousness',
  'orchestration': 'Orchestration',
  'app-preview': 'App Preview',
  'file-preview': 'File Preview',
  'canvas': 'Canvas',
  'manager-ai-chat': 'Manager AI Chat',
}

// Layout Thumbnail Component
const LayoutThumbnail: React.FC<{ layout: Layout }> = ({ layout }) => {
  const { panelVisibility, panelSizes } = layout
  
  const leftOpen = panelVisibility?.leftPanelOpen ?? false
  const rightOpen = panelVisibility?.rightPanelOpen ?? false
  const bottomOpen = panelVisibility?.bottomPanelOpen ?? false
  
  const leftSize = panelSizes?.leftPanelSize ?? 20
  const rightSize = panelSizes?.rightPanelSize ?? 25
  const bottomSize = panelSizes?.bottomPanelSize ?? 25
  
  return (
    <div className="w-full h-16 bg-gray-900 rounded border border-gray-700 relative overflow-hidden">
      {/* Left Panel */}
      {leftOpen && (
        <div 
          className="absolute left-0 top-0 bottom-0 bg-blue-600/30 border-r border-blue-500/50"
          style={{ width: `${leftSize}%` }}
        />
      )}
      
      {/* Right Panel */}
      {rightOpen && (
        <div 
          className="absolute right-0 top-0 bottom-0 bg-green-600/30 border-l border-green-500/50"
          style={{ width: `${rightSize}%` }}
        />
      )}
      
      {/* Bottom Panel */}
      {bottomOpen && (
        <div 
          className="absolute left-0 right-0 bottom-0 bg-purple-600/30 border-t border-purple-500/50"
          style={{ height: `${bottomSize}%` }}
        />
      )}
      
      {/* Main Content Area */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-[8px] text-gray-500 font-medium">
          {layout.panels.length} panels
        </div>
      </div>
      
      {/* Lock indicator */}
      {layout.locked && (
        <div className="absolute top-1 right-1">
          <Lock className="w-2 h-2 text-green-400" />
        </div>
      )}
    </div>
  )
}

interface LayoutManagerProps {
  currentView: MainViewType
  onSaveLayout?: (view: MainViewType, name?: string) => void
  onRestoreLayout?: (panelState: any) => void
}

export const LayoutManager: React.FC<LayoutManagerProps> = ({ currentView, onSaveLayout, onRestoreLayout }) => {
  const {
    layouts,
    currentLayout,
    saveLayoutForView,
    loadLayoutForView,
    lockLayoutToView,
    unlockLayoutFromView,
    getLayoutForView,
    deleteLayout,
  } = usePanelStore()
  
  const [isOpen, setIsOpen] = useState(false)
  const [layoutName, setLayoutName] = useState('')
  const [showSaveDialog, setShowSaveDialog] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  
  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])
  
  const handleSaveCurrentLayout = () => {
    const name = layoutName.trim() || undefined
    if (onSaveLayout) {
      onSaveLayout(currentView, name)
    } else {
      saveLayoutForView(currentView, name)
    }
    setLayoutName('')
    setShowSaveDialog(false)
  }
  
  const handleLoadLayout = (layout: Layout) => {
    loadLayoutForView(layout.mainView || currentView)
    if (onRestoreLayout && layout.panelVisibility && layout.panelSizes && layout.panelConfiguration) {
      onRestoreLayout({
        panelVisibility: layout.panelVisibility,
        panelSizes: layout.panelSizes,
        panelConfiguration: layout.panelConfiguration,
      })
    }
    setIsOpen(false)
  }
  
  const handleLockLayout = (layout: Layout, e: React.MouseEvent) => {
    e.stopPropagation()
    if (layout.mainView) {
      lockLayoutToView(layout.mainView, layout.id)
    }
  }
  
  const handleUnlockLayout = (layout: Layout, e: React.MouseEvent) => {
    e.stopPropagation()
    if (layout.mainView) {
      unlockLayoutFromView(layout.mainView)
    }
  }
  
  const handleDeleteLayout = (layoutId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (confirm('Delete this layout?')) {
      deleteLayout(layoutId)
    }
  }
  
  // Group layouts by view
  const layoutsByView = layouts.reduce((acc, layout) => {
    const view = layout.mainView || 'code'
    if (!acc[view]) acc[view] = []
    acc[view].push(layout)
    return acc
  }, {} as Record<MainViewType, Layout[]>)
  
  const currentViewLayout = getLayoutForView(currentView)
  
  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 hover:bg-gray-700 rounded text-gray-400 hover:text-gray-200 relative"
        title="Layout Manager"
      >
        <LayoutIcon className="w-4 h-4" />
        {currentViewLayout?.locked && (
          <Lock className="w-2 h-2 absolute top-1 right-1 text-blue-400" />
        )}
      </button>
      
      {isOpen && (
        <div className="absolute top-full right-0 mt-1 z-50 w-96 max-h-[80vh] bg-gray-800 border border-gray-700 rounded-lg shadow-xl flex flex-col">
          {/* Header */}
          <div className="p-3 border-b border-gray-700 flex items-center justify-between flex-shrink-0">
            <div className="flex items-center gap-2">
              <LayoutIcon className="w-4 h-4 text-blue-400" />
              <h2 className="text-sm font-semibold text-gray-200">Layout Manager</h2>
              {currentViewLayout?.locked && (
                <span className="text-xs px-1.5 py-0.5 bg-blue-600 rounded text-white flex items-center gap-1">
                  <Lock className="w-2.5 h-2.5" />
                  {VIEW_LABELS[currentView]} Locked
                </span>
              )}
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-gray-200"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
          
          {/* Content */}
          <div className="flex-1 overflow-auto p-3 space-y-3">
            {/* Save Current Layout for Current View */}
            <div className="space-y-2">
              <h3 className="text-xs font-semibold text-gray-300 flex items-center gap-2">
                <Save className="w-3 h-3" />
                Save Layout for {VIEW_LABELS[currentView]}
              </h3>
              {showSaveDialog ? (
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={layoutName}
                    onChange={(e) => setLayoutName(e.target.value)}
                    placeholder={`${VIEW_LABELS[currentView]} Layout`}
                    className="flex-1 px-2 py-1.5 text-xs bg-gray-900 border border-gray-700 rounded text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleSaveCurrentLayout()
                      if (e.key === 'Escape') {
                        setShowSaveDialog(false)
                        setLayoutName('')
                      }
                    }}
                    autoFocus
                  />
                  <button
                    onClick={handleSaveCurrentLayout}
                    className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 rounded text-white text-xs font-medium"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => {
                      setShowSaveDialog(false)
                      setLayoutName('')
                    }}
                    className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-gray-200 text-xs"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <div className="flex gap-2">
                  <button
                    onClick={() => setShowSaveDialog(true)}
                    className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded text-gray-200 text-xs flex items-center gap-1.5"
                  >
                    <Plus className="w-3 h-3" />
                    Save Current
                  </button>
                  {currentViewLayout && (
                    <>
                      {currentViewLayout.locked ? (
                        <button
                          onClick={(e) => handleUnlockLayout(currentViewLayout, e)}
                          className="px-3 py-1.5 bg-yellow-600 hover:bg-yellow-700 rounded text-white text-xs flex items-center gap-1.5"
                        >
                          <Unlock className="w-3 h-3" />
                          Unlock
                        </button>
                      ) : (
                        <button
                          onClick={(e) => handleLockLayout(currentViewLayout, e)}
                          className="px-3 py-1.5 bg-green-600 hover:bg-green-700 rounded text-white text-xs flex items-center gap-1.5"
                        >
                          <Lock className="w-3 h-3" />
                          Lock
                        </button>
                      )}
                    </>
                  )}
                </div>
              )}
            </div>
            
            {/* Layouts by View */}
            <div className="space-y-3">
              {(Object.keys(layoutsByView) as MainViewType[]).map((view) => {
                const ViewIcon = VIEW_ICONS[view]
                const viewLayouts = layoutsByView[view]
                const lockedLayout = viewLayouts.find(l => l.locked)
                
                return (
                  <div key={view} className="space-y-2">
                    <h3 className="text-xs font-semibold text-gray-300 flex items-center gap-2">
                      <ViewIcon className="w-3 h-3" />
                      {VIEW_LABELS[view]}
                      {lockedLayout && (
                        <span className="text-xs px-1.5 py-0.5 bg-green-600 rounded text-white flex items-center gap-1">
                          <Lock className="w-2 h-2" />
                          Locked
                        </span>
                      )}
                    </h3>
                    <div className="space-y-2 ml-5">
                      {viewLayouts.map((layout) => (
                        <div
                          key={layout.id}
                          onClick={() => handleLoadLayout(layout)}
                          className={`p-2 rounded border cursor-pointer transition-all ${
                            currentLayout?.id === layout.id
                              ? 'border-blue-500 bg-blue-900/20'
                              : 'border-gray-700 bg-gray-900 hover:border-gray-600'
                          }`}
                        >
                          {/* Thumbnail */}
                          <LayoutThumbnail layout={layout} />
                          
                          {/* Layout Info */}
                          <div className="flex items-center justify-between mt-2">
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-1.5">
                                <div className="text-xs font-medium text-gray-200 truncate">{layout.name}</div>
                                {layout.locked && (
                                  <Lock className="w-2.5 h-2.5 text-green-400 flex-shrink-0" />
                                )}
                              </div>
                              <div className="text-[10px] text-gray-500 mt-0.5">
                                {new Date(layout.updatedAt).toLocaleDateString()} • {layout.panels.length} panels
                              </div>
                            </div>
                            <div className="flex items-center gap-1">
                              {currentLayout?.id === layout.id && (
                                <span className="text-[10px] px-1.5 py-0.5 bg-blue-600 rounded text-white">
                                  Active
                                </span>
                              )}
                              {layout.locked ? (
                                <button
                                  onClick={(e) => handleUnlockLayout(layout, e)}
                                  className="p-1 hover:bg-yellow-900/30 rounded text-gray-400 hover:text-yellow-400"
                                  title="Unlock layout"
                                >
                                  <Unlock className="w-3 h-3" />
                                </button>
                              ) : (
                                <button
                                  onClick={(e) => handleLockLayout(layout, e)}
                                  className="p-1 hover:bg-green-900/30 rounded text-gray-400 hover:text-green-400"
                                  title="Lock layout to view"
                                >
                                  <Lock className="w-3 h-3" />
                                </button>
                              )}
                              <button
                                onClick={(e) => handleDeleteLayout(layout.id, e)}
                                className="p-1 hover:bg-red-900/30 rounded text-gray-400 hover:text-red-400"
                                title="Delete layout"
                              >
                                <Trash2 className="w-3 h-3" />
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
            
            {layouts.length === 0 && (
              <div className="text-xs text-gray-500 py-4 text-center">
                No saved layouts yet. Save your current layout to get started!
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
