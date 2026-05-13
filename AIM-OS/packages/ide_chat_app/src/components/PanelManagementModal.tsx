/**
 * Panel Management Modal
 * 
 * Phase 3.1: Panel Management Interface with Drag-and-Drop
 * 
 * Features:
 * - Drag-and-drop panel reordering
 * - Panel visibility management
 * - Zone assignment (left, right, bottom, main)
 * - Layout persistence
 */

import React, { useState, useMemo, useEffect, useRef } from 'react'
import { X, Settings, Layers, FolderTree } from 'lucide-react'
import { PanelDragDrop } from './PanelDragDrop'
import { LEFT_PANELS, RIGHT_PANELS, BOTTOM_PANELS, getPanelById, PANEL_GROUPS, getAllGroups } from './PanelRegistry'
import { LeftPanelType, RightPanelType, BottomPanelType } from './RevIDELayout'

interface PanelManagementModalProps {
  isOpen: boolean
  onClose: () => void
  leftTopPanel: LeftPanelType
  leftBottomPanel: LeftPanelType | null
  rightTopPanel: RightPanelType
  rightBottomPanel: RightPanelType | null
  bottomPanel: BottomPanelType | null
  onUpdatePanels: (panels: {
    leftTop: LeftPanelType
    leftBottom: LeftPanelType | null
    rightTop: RightPanelType
    rightBottom: RightPanelType | null
    bottom: BottomPanelType | null
  }) => void
}

export const PanelManagementModal: React.FC<PanelManagementModalProps> = ({
  isOpen,
  onClose,
  leftTopPanel,
  leftBottomPanel,
  rightTopPanel,
  rightBottomPanel,
  bottomPanel,
  onUpdatePanels
}) => {
  const [localLeftPanels, setLocalLeftPanels] = useState<LeftPanelType[]>([
    leftTopPanel,
    ...(leftBottomPanel ? [leftBottomPanel] : [])
  ].filter((p): p is LeftPanelType => p !== null))
  
  const [localRightPanels, setLocalRightPanels] = useState<RightPanelType[]>([
    rightTopPanel,
    ...(rightBottomPanel ? [rightBottomPanel] : [])
  ].filter((p): p is RightPanelType => p !== null))
  
  const [localBottomPanels, setLocalBottomPanels] = useState<BottomPanelType[]>(
    bottomPanel ? [bottomPanel] : []
  )
  
  const [showGroups, setShowGroups] = useState(false)
  const [selectedGroup, setSelectedGroup] = useState<string | null>(null)
  const groupsRef = useRef<HTMLDivElement>(null)

  // Close groups dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (groupsRef.current && !groupsRef.current.contains(event.target as Node)) {
        setShowGroups(false)
      }
    }

    if (showGroups) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showGroups])

  const leftPanelsData = useMemo(() => {
    return localLeftPanels.map(id => {
      const panel = getPanelById(id || '')
      return {
        id: id || '',
        label: panel?.name || id || '',
        icon: panel?.icon ? React.createElement(panel.icon, { className: 'w-4 h-4' }) : undefined
      }
    })
  }, [localLeftPanels])

  const rightPanelsData = useMemo(() => {
    return localRightPanels.map(id => {
      const panel = getPanelById(id || '')
      return {
        id: id || '',
        label: panel?.name || id || '',
        icon: panel?.icon ? React.createElement(panel.icon, { className: 'w-4 h-4' }) : undefined
      }
    })
  }, [localRightPanels])

  const bottomPanelsData = useMemo(() => {
    return localBottomPanels.map(id => {
      const panel = getPanelById(id || '')
      return {
        id: id || '',
        label: panel?.name || id || '',
        icon: panel?.icon ? React.createElement(panel.icon, { className: 'w-4 h-4' }) : undefined
      }
    })
  }, [localBottomPanels])

  const handleReorder = (
    source: { type: 'left' | 'right' | 'bottom'; index: number },
    destination: { type: 'left' | 'right' | 'bottom'; index: number }
  ) => {
    if (source.type === destination.type) {
      const sourceArray = source.type === 'left' ? localLeftPanels : source.type === 'right' ? localRightPanels : localBottomPanels
      const newArray = [...sourceArray]
      const [removed] = newArray.splice(source.index, 1)
      newArray.splice(destination.index, 0, removed)

      if (source.type === 'left') {
        setLocalLeftPanels(newArray as LeftPanelType[])
      } else if (source.type === 'right') {
        setLocalRightPanels(newArray as RightPanelType[])
      } else {
        setLocalBottomPanels(newArray as BottomPanelType[])
      }
    }
  }

  const handleMoveToZone = (
    panelId: string,
    sourceZone: 'left' | 'right' | 'bottom',
    targetZone: 'left' | 'right' | 'bottom' | 'main'
  ) => {
    // Remove from source zone
    if (sourceZone === 'left') {
      setLocalLeftPanels(localLeftPanels.filter(id => id !== panelId))
    } else if (sourceZone === 'right') {
      setLocalRightPanels(localRightPanels.filter(id => id !== panelId))
    } else {
      setLocalBottomPanels(localBottomPanels.filter(id => id !== panelId))
    }

    // Add to target zone
    if (targetZone === 'left') {
      setLocalLeftPanels([...localLeftPanels, panelId as LeftPanelType])
    } else if (targetZone === 'right') {
      setLocalRightPanels([...localRightPanels, panelId as RightPanelType])
    } else if (targetZone === 'bottom') {
      setLocalBottomPanels([...localBottomPanels, panelId as BottomPanelType])
    }
    // main zone is handled separately (would open panel in main content area)
  }

  const handleLoadGroup = (groupId: string) => {
    const group = PANEL_GROUPS[groupId as keyof typeof PANEL_GROUPS]
    if (!group) return
    
    // Add all panels from the group to appropriate zones
    const panelsToAdd = group.panels
    
    panelsToAdd.forEach(panelId => {
      const panel = getPanelById(panelId)
      if (!panel) return
      
      // Add to appropriate zone based on panel's default zone
      if (panel.defaultZone === 'left' && !localLeftPanels.includes(panelId as LeftPanelType)) {
        setLocalLeftPanels(prev => [...prev, panelId as LeftPanelType])
      } else if (panel.defaultZone === 'right' && !localRightPanels.includes(panelId as RightPanelType)) {
        setLocalRightPanels(prev => [...prev, panelId as RightPanelType])
      } else if (panel.defaultZone === 'bottom' && !localBottomPanels.includes(panelId as BottomPanelType)) {
        setLocalBottomPanels(prev => [...prev, panelId as BottomPanelType])
      }
    })
    
    setSelectedGroup(groupId)
  }

  const handleClosePanel = (panelId: string, zone: 'left' | 'right' | 'bottom') => {
    if (zone === 'left') {
      setLocalLeftPanels(localLeftPanels.filter(id => id !== panelId))
    } else if (zone === 'right') {
      setLocalRightPanels(localRightPanels.filter(id => id !== panelId))
    } else {
      setLocalBottomPanels(localBottomPanels.filter(id => id !== panelId))
    }
  }

  const handleSave = () => {
    onUpdatePanels({
      leftTop: localLeftPanels[0] || null,
      leftBottom: localLeftPanels[1] || null,
      rightTop: localRightPanels[0] || null,
      rightBottom: localRightPanels[1] || null,
      bottom: localBottomPanels[0] || null
    })
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-gray-800 rounded-lg border border-gray-700 w-[90vw] h-[90vh] max-w-6xl flex flex-col shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-gray-400" />
            <h2 className="text-lg font-semibold text-gray-300">Panel Management</h2>
          </div>
          <div className="flex items-center gap-2">
            {/* Panel Groups Button */}
            <div className="relative" ref={groupsRef}>
              <button
                onClick={() => setShowGroups(!showGroups)}
                className="px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors flex items-center gap-1"
                aria-label="Show panel groups"
                title="Panel Groups"
              >
                <FolderTree className="w-4 h-4" />
                Groups
              </button>
              
              {/* Groups Dropdown */}
              {showGroups && (
                <div className="absolute right-0 top-full mt-1 w-64 bg-gray-800 border border-gray-700 rounded shadow-lg z-50 max-h-96 overflow-y-auto">
                  <div className="p-2">
                    {getAllGroups().map(group => (
                      <button
                        key={group.id}
                        onClick={() => {
                          handleLoadGroup(group.id)
                          setShowGroups(false)
                        }}
                        className={`w-full text-left p-2 rounded transition-colors mb-1 ${
                          selectedGroup === group.id
                            ? 'bg-blue-600/20 border border-blue-500'
                            : 'hover:bg-gray-700 border border-transparent'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          {React.createElement(group.icon, { className: 'w-4 h-4 text-gray-400' })}
                          <div className="flex-1">
                            <div className="text-sm text-gray-300 font-medium">{group.name}</div>
                            <div className="text-xs text-gray-500">{group.description}</div>
                            <div className="text-xs text-gray-600 mt-1">
                              {group.panels.length} panel{group.panels.length !== 1 ? 's' : ''}
                            </div>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            <button
              onClick={onClose}
              className="p-1 text-gray-400 hover:text-gray-200 hover:bg-gray-700 rounded transition-colors"
              aria-label="Close panel management"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <PanelDragDrop
            leftPanels={leftPanelsData}
            rightPanels={rightPanelsData}
            bottomPanels={bottomPanelsData}
            onReorder={handleReorder}
            onMoveToZone={handleMoveToZone}
            onClosePanel={handleClosePanel}
          />
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 p-4 border-t border-gray-700">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-700 rounded transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Save Layout
          </button>
        </div>
      </div>
    </div>
  )
}

