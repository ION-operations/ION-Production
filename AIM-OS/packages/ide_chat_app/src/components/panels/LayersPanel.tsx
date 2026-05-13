/**
 * Layers Panel Component
 * 
 * Phase 2.2: Right Drawer Panels
 * 
 * Visual layer management (like Photoshop/Figma).
 * Features:
 * - Layer hierarchy
 * - Layer visibility toggle
 * - Layer locking
 * - Layer reordering
 * - Layer grouping
 * - AIM-OS integration (CMC storage, VIF confidence, SEG relationships)
 */

import React, { useState, useMemo, useCallback } from 'react'
import { Layers, Eye, EyeOff, Lock, Unlock, Folder, FolderOpen, Search, Plus, Trash2, Edit2, Copy, Move, GripVertical, Shield, Brain, ChevronRight, ChevronDown, X } from 'lucide-react'

interface Layer {
  id: string
  name: string
  type: 'component' | 'group' | 'element'
  visible: boolean
  locked: boolean
  opacity: number
  children?: Layer[]
  component?: string
  confidence?: number
  blendMode?: 'normal' | 'multiply' | 'screen' | 'overlay'
  cmcAtomId?: string // CMC integration
  vifConfidence?: number // VIF confidence
  createdAt?: string
  updatedAt?: string
}

const mockLayers: Layer[] = [
  {
    id: 'layer-1',
    name: 'RevIDELayout',
    type: 'component',
    visible: true,
    locked: false,
    opacity: 100,
    component: 'RevIDELayout',
    confidence: 0.98,
  },
  {
    id: 'group-1',
    name: 'Left Drawer',
    type: 'group',
    visible: true,
    locked: false,
    opacity: 100,
    children: [
      {
        id: 'layer-2',
        name: 'FileExplorerPanel',
        type: 'component',
        visible: true,
        locked: false,
        opacity: 100,
        component: 'FileExplorerPanel',
        confidence: 0.95,
      },
      {
        id: 'layer-3',
        name: 'ComponentLibraryPanel',
        type: 'component',
        visible: true,
        locked: false,
        opacity: 100,
        component: 'ComponentLibraryPanel',
        confidence: 0.94,
      },
      {
        id: 'layer-4',
        name: 'AIMemoryPanel',
        type: 'component',
        visible: true,
        locked: false,
        opacity: 100,
        component: 'AIMemoryPanel',
        confidence: 0.93,
      },
    ],
  },
  {
    id: 'group-2',
    name: 'Right Drawer',
    type: 'group',
    visible: true,
    locked: false,
    opacity: 100,
    children: [
      {
        id: 'layer-5',
        name: 'OutlinePanel',
        type: 'component',
        visible: true,
        locked: false,
        opacity: 100,
        component: 'OutlinePanel',
        confidence: 0.96,
      },
      {
        id: 'layer-6',
        name: 'PropertiesPanel',
        type: 'component',
        visible: true,
        locked: false,
        opacity: 100,
        component: 'PropertiesPanel',
        confidence: 0.95,
      },
    ],
  },
  {
    id: 'layer-7',
    name: 'MainContentArea',
    type: 'component',
    visible: true,
    locked: false,
    opacity: 100,
    component: 'MainContentArea',
    confidence: 0.97,
  },
]

export const LayersPanel: React.FC = () => {
  const [layers, setLayers] = useState<Layer[]>(mockLayers)
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set(['group-1', 'group-2']))
  const [selectedLayerId, setSelectedLayerId] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedLayer, setSelectedLayer] = useState<Layer | null>(null)
  const [draggedLayerId, setDraggedLayerId] = useState<string | null>(null)

  const toggleGroup = (groupId: string) => {
    const newExpanded = new Set(expandedGroups)
    if (newExpanded.has(groupId)) {
      newExpanded.delete(groupId)
    } else {
      newExpanded.add(groupId)
    }
    setExpandedGroups(newExpanded)
  }

  const toggleVisibility = (layerId: string) => {
    const updateLayer = (layer: Layer): Layer => {
      if (layer.id === layerId) {
        return { ...layer, visible: !layer.visible }
      }
      if (layer.children) {
        return { ...layer, children: layer.children.map(updateLayer) }
      }
      return layer
    }
    setLayers(layers.map(updateLayer))
  }

  const toggleLock = (layerId: string) => {
    const updateLayer = (layer: Layer): Layer => {
      if (layer.id === layerId) {
        return { ...layer, locked: !layer.locked }
      }
      if (layer.children) {
        return { ...layer, children: layer.children.map(updateLayer) }
      }
      return layer
    }
    setLayers(layers.map(updateLayer))
  }

  const filteredLayers = useMemo(() => {
    if (!searchQuery) return layers

    const filterLayer = (layer: Layer): Layer | null => {
      const matchesSearch = layer.name.toLowerCase().includes(searchQuery.toLowerCase())
      const filteredChildren = layer.children?.map(filterLayer).filter((l): l is Layer => l !== null)

      if (matchesSearch || (filteredChildren && filteredChildren.length > 0)) {
        return {
          ...layer,
          children: filteredChildren && filteredChildren.length > 0 ? filteredChildren : layer.children,
        }
      }
      return null
    }

    return layers.map(filterLayer).filter((l): l is Layer => l !== null)
  }, [layers, searchQuery])

  const handleDuplicateLayer = useCallback((layerId: string) => {
    const duplicateLayer = (layer: Layer): Layer => {
      if (layer.id === layerId) {
        return { ...layer, id: `${layer.id}-copy`, name: `${layer.name} Copy` }
      }
      if (layer.children) {
        return { ...layer, children: layer.children.map(duplicateLayer) }
      }
      return layer
    }
    setLayers(layers.map(duplicateLayer))
  }, [layers])

  const handleDeleteLayer = useCallback((layerId: string) => {
    const filterLayer = (layer: Layer): Layer | null => {
      if (layer.id === layerId) return null
      if (layer.children) {
        const filteredChildren = layer.children.map(filterLayer).filter((l): l is Layer => l !== null)
        return { ...layer, children: filteredChildren.length > 0 ? filteredChildren : undefined }
      }
      return layer
    }
    setLayers(layers.map(filterLayer).filter((l): l is Layer => l !== null))
  }, [layers])

  const handleChangeOpacity = useCallback((layerId: string, opacity: number) => {
    const updateLayer = (layer: Layer): Layer => {
      if (layer.id === layerId) {
        return { ...layer, opacity }
      }
      if (layer.children) {
        return { ...layer, children: layer.children.map(updateLayer) }
      }
      return layer
    }
    setLayers(layers.map(updateLayer))
  }, [layers])

  const renderLayer = (layer: Layer, depth: number = 0): React.ReactNode => {
    const isGroup = layer.type === 'group'
    const isExpanded = expandedGroups.has(layer.id)
    const isSelected = selectedLayerId === layer.id
    const isDragged = draggedLayerId === layer.id

    return (
      <div key={layer.id} className={isDragged ? 'opacity-50' : ''}>
        <div
          className={`flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer transition-colors group ${
            isSelected
              ? 'bg-blue-600/20 border border-blue-500'
              : 'hover:bg-gray-700 border border-transparent'
          }`}
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
          onClick={() => {
            setSelectedLayerId(layer.id)
            setSelectedLayer(layer)
          }}
          onDragStart={(e) => {
            setDraggedLayerId(layer.id)
            e.dataTransfer.effectAllowed = 'move'
          }}
          onDragEnd={() => setDraggedLayerId(null)}
          draggable={!layer.locked}
          role="button"
          tabIndex={0}
          aria-label={`Layer ${layer.name}`}
        >
          {isGroup && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                toggleGroup(layer.id)
              }}
              className="p-0.5 hover:bg-gray-600 rounded"
              aria-label={`${isExpanded ? 'Collapse' : 'Expand'} ${layer.name}`}
            >
              {isExpanded ? (
                <FolderOpen className="w-4 h-4 text-blue-400" />
              ) : (
                <Folder className="w-4 h-4 text-blue-400" />
              )}
            </button>
          )}
          {!isGroup && (
            <div className="w-4 h-4 flex items-center justify-center">
              <GripVertical className="w-3 h-3 text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
          )}

          <button
            onClick={(e) => {
              e.stopPropagation()
              toggleVisibility(layer.id)
            }}
            className="p-0.5 hover:bg-gray-600 rounded"
            aria-label={`${layer.visible ? 'Hide' : 'Show'} ${layer.name}`}
            title={layer.visible ? 'Hide' : 'Show'}
          >
            {layer.visible ? (
              <Eye className="w-4 h-4 text-gray-400" />
            ) : (
              <EyeOff className="w-4 h-4 text-gray-500" />
            )}
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation()
              toggleLock(layer.id)
            }}
            className="p-0.5 hover:bg-gray-600 rounded"
            aria-label={`${layer.locked ? 'Unlock' : 'Lock'} ${layer.name}`}
            title={layer.locked ? 'Unlock' : 'Lock'}
          >
            {layer.locked ? (
              <Lock className="w-4 h-4 text-yellow-400" />
            ) : (
              <Unlock className="w-4 h-4 text-gray-400" />
            )}
          </button>

          <span className="flex-1 text-sm text-gray-300 truncate" title={layer.name}>
            {layer.name}
          </span>

          <div className="flex items-center gap-1">
            {layer.vifConfidence !== undefined && (
              <span className="text-xs text-green-400 flex items-center gap-0.5" title="VIF Confidence">
                <Shield className="w-3 h-3" />
                {(layer.vifConfidence * 100).toFixed(0)}%
              </span>
            )}
            {layer.confidence !== undefined && (
              <span className="text-xs text-green-400">
                {Math.round(layer.confidence * 100)}%
              </span>
            )}
            {layer.opacity < 100 && (
              <span className="text-xs text-gray-500">
                {layer.opacity}%
              </span>
            )}
            {layer.cmcAtomId && (
              <span className="text-xs text-purple-400 flex items-center gap-0.5" title="CMC Atom ID">
                <Brain className="w-3 h-3" />
              </span>
            )}
          </div>
        </div>

        {isGroup && isExpanded && layer.children && (
          <div>
            {layer.children.map((child) => renderLayer(child, depth + 1))}
          </div>
        )}
      </div>
    )
  }

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-800" role="complementary" aria-label="Layers Panel">
        {loading.cmc ? (
          <LoadingState message="Loading layers..." />
        ) : (
          <>
      {/* Header */}
      <div className="h-10 bg-gray-900 border-b border-gray-700 flex items-center px-3 shrink-0">
        <Layers className="w-4 h-4 mr-2 text-gray-400" />
        <span className="text-sm font-semibold text-gray-300">Layers</span>
      </div>

      {/* Search */}
      <div className="px-2 py-2 border-b border-gray-700 shrink-0">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search layers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-2 py-1.5 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-500"
            aria-label="Search layers"
          />
        </div>
      </div>

      {/* Layers List */}
      <div className="flex-1 overflow-y-auto p-2">
        {filteredLayers.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm">
            <Layers className="w-8 h-8 mb-2 opacity-50" />
            <p>No layers found</p>
          </div>
        ) : (
          <div className="space-y-1">
            {filteredLayers.map((layer) => renderLayer(layer))}
          </div>
        )}
      </div>

      {/* Layer Detail */}
      {selectedLayer && (
        <div className="p-3 border-t border-gray-700 bg-gray-900 shrink-0 max-h-64 overflow-y-auto">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-white">{selectedLayer.name}</h3>
            <button
              onClick={() => setSelectedLayer(null)}
              className="text-gray-400 hover:text-gray-300"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className="space-y-2 text-xs text-gray-400">
            <div className="flex justify-between">
              <span>Type:</span>
              <span className="text-gray-300 capitalize">{selectedLayer.type}</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Opacity:</span>
              <div className="flex items-center gap-2">
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={selectedLayer.opacity}
                  onChange={(e) => handleChangeOpacity(selectedLayer.id, parseInt(e.target.value))}
                  className="w-20"
                />
                <span className="text-gray-300 w-10 text-right">{selectedLayer.opacity}%</span>
              </div>
            </div>
            {selectedLayer.blendMode && (
              <div className="flex justify-between">
                <span>Blend Mode:</span>
                <span className="text-gray-300 capitalize">{selectedLayer.blendMode}</span>
              </div>
            )}
            {selectedLayer.vifConfidence !== undefined && (
              <div className="flex justify-between">
                <span>VIF Confidence:</span>
                <span className="text-green-400">{(selectedLayer.vifConfidence * 100).toFixed(0)}%</span>
              </div>
            )}
            {selectedLayer.cmcAtomId && (
              <div className="flex justify-between">
                <span>CMC Atom:</span>
                <span className="text-purple-400 font-mono text-xs">{selectedLayer.cmcAtomId.substring(0, 12)}...</span>
              </div>
            )}
            <div className="flex gap-2 pt-2 border-t border-gray-700">
              <button
                onClick={() => handleDuplicateLayer(selectedLayer.id)}
                className="flex-1 px-2 py-1 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded text-xs flex items-center justify-center gap-1"
              >
                <Copy className="w-3 h-3" />
                Duplicate
              </button>
              <button
                onClick={() => handleDeleteLayer(selectedLayer.id)}
                className="flex-1 px-2 py-1 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded text-xs flex items-center justify-center gap-1"
              >
                <Trash2 className="w-3 h-3" />
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="h-10 bg-gray-900 border-t border-gray-700 flex items-center justify-between px-3 shrink-0">
        <button
          className="p-1.5 text-gray-400 hover:text-gray-300 hover:bg-gray-800 rounded transition-colors"
          aria-label="Add layer"
          title="Add layer"
        >
          <Plus className="w-4 h-4" />
        </button>
        <div className="flex gap-1">
          {selectedLayer && (
            <>
              <button
                onClick={() => handleDuplicateLayer(selectedLayer.id)}
                className="p-1.5 text-gray-400 hover:text-gray-300 hover:bg-gray-800 rounded transition-colors"
                aria-label="Duplicate layer"
                title="Duplicate"
              >
                <Copy className="w-4 h-4" />
              </button>
              <button
                className="p-1.5 text-gray-400 hover:text-gray-300 hover:bg-gray-800 rounded transition-colors"
                aria-label="Edit layer"
                title="Edit"
              >
                <Edit2 className="w-4 h-4" />
              </button>
              <button
                onClick={() => selectedLayer && handleDeleteLayer(selectedLayer.id)}
                className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded transition-colors"
                aria-label="Delete layer"
                title="Delete"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </>
          )}
        </div>
      </div>
          </>
        )}
      </div>
    </ErrorBoundary>
  )
}

