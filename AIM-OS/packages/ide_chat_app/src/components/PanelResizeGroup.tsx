// Panel Resize and Group System
// V2 Enhancement - Week 2 Foundation
// Enables panel resizing and grouping functionality

import React, { useState, useRef, useCallback } from 'react'
import { usePanelStore, PanelGroup } from '../store/panelStore'
import { panelRegistry } from '../store/panelRegistry'
import { GripVertical, ChevronDown, ChevronRight, X, Plus, Layout } from 'lucide-react'

interface PanelResizeHandleProps {
  panelId: string
  direction: 'horizontal' | 'vertical'
  onResize?: (newSize: number) => void
  minSize?: number
  maxSize?: number
  className?: string
}

/**
 * Resize Handle Component
 */
export function PanelResizeHandle({
  panelId,
  direction,
  onResize,
  minSize = 100,
  maxSize = 1000,
  className = ''
}: PanelResizeHandleProps) {
  const { setPanelSize } = usePanelStore()
  const [isResizing, setIsResizing] = useState(false)
  const [startPos, setStartPos] = useState(0)
  const [startSize, setStartSize] = useState(0)
  const handleRef = useRef<HTMLDivElement>(null)

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    setIsResizing(true)
    
    const panel = usePanelStore.getState().panels.find(p => p.panelId === panelId)
    const currentSize = panel?.size || 300
    
    if (direction === 'horizontal') {
      setStartPos(e.clientX)
    } else {
      setStartPos(e.clientY)
    }
    setStartSize(currentSize)

    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return

      const delta = direction === 'horizontal' 
        ? e.clientX - startPos 
        : e.clientY - startPos
      
      const newSize = Math.max(minSize, Math.min(maxSize, startSize + delta))
      setPanelSize(panelId, newSize)
      
      if (onResize) {
        onResize(newSize)
      }
    }

    const handleMouseUp = () => {
      setIsResizing(false)
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
  }, [panelId, direction, minSize, maxSize, setPanelSize, onResize, startPos, startSize, isResizing])

  return (
    <div
      ref={handleRef}
      onMouseDown={handleMouseDown}
      className={`${className} ${
        direction === 'horizontal'
          ? 'cursor-col-resize w-1 hover:w-2 hover:bg-blue-500'
          : 'cursor-row-resize h-1 hover:h-2 hover:bg-blue-500'
      } bg-gray-700 hover:bg-blue-500 transition-all ${
        isResizing ? 'bg-blue-500' : ''
      }`}
    />
  )
}

/**
 * Panel Group Component
 */
interface PanelGroupComponentProps {
  group: PanelGroup
  onToggleCollapse?: (groupId: string) => void
  onRemovePanel?: (groupId: string, panelId: string) => void
  onAddPanel?: (groupId: string) => void
  className?: string
}

export function PanelGroupComponent({
  group,
  onToggleCollapse,
  onRemovePanel,
  onAddPanel,
  className = ''
}: PanelGroupComponentProps) {
  const { panels, toggleGroupCollapse, removePanelFromGroup } = usePanelStore()

  const handleToggleCollapse = useCallback(() => {
    toggleGroupCollapse(group.id)
    if (onToggleCollapse) {
      onToggleCollapse(group.id)
    }
  }, [group.id, toggleGroupCollapse, onToggleCollapse])

  const handleRemovePanel = useCallback((panelId: string) => {
    removePanelFromGroup(group.id, panelId)
    if (onRemovePanel) {
      onRemovePanel(group.id, panelId)
    }
  }, [group.id, removePanelFromGroup, onRemovePanel])

  const groupPanels = panels.filter(p => group.panelIds.includes(p.panelId))

  return (
    <div className={`border border-gray-700 rounded-lg bg-gray-800 ${className}`}>
      {/* Group Header */}
      <div
        className="flex items-center justify-between p-2 bg-gray-750 border-b border-gray-700 cursor-pointer hover:bg-gray-700 transition-colors"
        onClick={handleToggleCollapse}
      >
        <div className="flex items-center gap-2">
          {group.collapsed ? (
            <ChevronRight className="w-4 h-4 text-gray-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-gray-400" />
          )}
          <Layout className="w-4 h-4 text-gray-400" />
          <span className="text-sm font-medium text-gray-300">{group.name}</span>
          <span className="text-xs text-gray-500">({group.type})</span>
        </div>
        <div className="flex items-center gap-1">
          {onAddPanel && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                onAddPanel(group.id)
              }}
              className="p-1 text-gray-400 hover:text-gray-200 hover:bg-gray-600 rounded transition-colors"
              aria-label="Add panel to group"
            >
              <Plus className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* Group Content */}
      {!group.collapsed && (
        <div className="p-2 space-y-1">
          {groupPanels.map((panel) => {
            const metadata = panelRegistry.getPanel(panel.panelId)
            return (
              <div
                key={panel.panelId}
                className="flex items-center justify-between p-2 bg-gray-750 rounded hover:bg-gray-700 transition-colors"
              >
                <div className="flex items-center gap-2 flex-1">
                  <GripVertical className="w-3 h-3 text-gray-500" />
                  {metadata?.icon && <span className="w-4 h-4">{metadata.icon}</span>}
                  <span className="text-sm text-gray-300">{metadata?.name || panel.panelId}</span>
                </div>
                {onRemovePanel && (
                  <button
                    onClick={() => handleRemovePanel(panel.panelId)}
                    className="p-1 text-gray-400 hover:text-red-400 hover:bg-gray-600 rounded transition-colors"
                    aria-label={`Remove ${metadata?.name || panel.panelId}`}
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </div>
            )
          })}
          {groupPanels.length === 0 && (
            <div className="text-xs text-gray-500 text-center py-2">
              No panels in group
            </div>
          )}
        </div>
      )}
    </div>
  )
}

/**
 * Panel Group Manager Component
 */
interface PanelGroupManagerProps {
  className?: string
}

export function PanelGroupManager({ className = '' }: PanelGroupManagerProps) {
  const { groups, createGroup, addPanelToGroup } = usePanelStore()
  const [showCreateGroup, setShowCreateGroup] = useState(false)
  const [newGroupName, setNewGroupName] = useState('')
  const [newGroupType, setNewGroupType] = useState<'tabs' | 'accordion' | 'stack'>('tabs')

  const handleCreateGroup = useCallback(() => {
    if (!newGroupName.trim()) return

    const groupId = createGroup({
      name: newGroupName,
      type: newGroupType,
      panelIds: [],
      collapsed: false
    })

    setNewGroupName('')
    setNewGroupType('tabs')
    setShowCreateGroup(false)
  }, [newGroupName, newGroupType, createGroup])

  return (
    <div className={className}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-300">Panel Groups</h3>
        <button
          onClick={() => setShowCreateGroup(!showCreateGroup)}
          className="px-3 py-1 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Create Group
        </button>
      </div>

      {showCreateGroup && (
        <div className="mb-4 p-3 bg-gray-800 border border-gray-700 rounded-lg">
          <input
            type="text"
            value={newGroupName}
            onChange={(e) => setNewGroupName(e.target.value)}
            placeholder="Group name"
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-gray-300 mb-2"
          />
          <select
            value={newGroupType}
            onChange={(e) => setNewGroupType(e.target.value as 'tabs' | 'accordion' | 'stack')}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-gray-300 mb-2"
          >
            <option value="tabs">Tabs</option>
            <option value="accordion">Accordion</option>
            <option value="stack">Stack</option>
          </select>
          <div className="flex gap-2">
            <button
              onClick={handleCreateGroup}
              className="px-3 py-1 text-sm bg-green-600 hover:bg-green-700 text-white rounded transition-colors"
            >
              Create
            </button>
            <button
              onClick={() => {
                setShowCreateGroup(false)
                setNewGroupName('')
              }}
              className="px-3 py-1 text-sm bg-gray-600 hover:bg-gray-700 text-white rounded transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="space-y-2">
        {groups.map((group) => (
          <PanelGroupComponent
            key={group.id}
            group={group}
            onAddPanel={(groupId) => {
              // TODO: Show panel picker
              console.log('Add panel to group:', groupId)
            }}
          />
        ))}
        {groups.length === 0 && (
          <div className="text-sm text-gray-500 text-center py-8">
            No groups created yet
          </div>
        )}
      </div>
    </div>
  )
}

