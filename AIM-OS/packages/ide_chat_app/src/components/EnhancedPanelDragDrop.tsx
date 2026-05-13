// Enhanced Drag-and-Drop Panel System
// V2 Enhancement - Week 2 Foundation
// Integrates with new panelStore for state management

import React, { useState, useCallback } from 'react'
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd'
import { usePanelStore } from '../store/panelStore'
import { panelRegistry } from '../store/panelRegistry'
import { GripVertical } from 'lucide-react'

export interface PanelDragItem {
  id: string
  panelId: string
  label: string
  icon?: React.ReactNode
  zone: 'left' | 'right' | 'bottom' | 'main'
  order: number
}

interface EnhancedPanelDragDropProps {
  zone: 'left' | 'right' | 'bottom' | 'main'
  onPanelMove?: (panelId: string, fromZone: string, toZone: string, newOrder: number) => void
  className?: string
}

export const EnhancedPanelDragDrop: React.FC<EnhancedPanelDragDropProps> = ({
  zone,
  onPanelMove,
  className = ''
}) => {
  const { panels, setPanelPosition, setPanelOrder } = usePanelStore()
  const [draggedPanel, setDraggedPanel] = useState<PanelDragItem | null>(null)
  const [dropZoneHover, setDropZoneHover] = useState<'left' | 'right' | 'bottom' | 'main' | null>(null)

  // Get panels for this zone
  const zonePanels = panels
    .filter(p => p.zone === zone)
    .sort((a, b) => a.order - b.order)
    .map(panel => {
      const metadata = panelRegistry.getPanel(panel.panelId)
      return {
        id: panel.panelId,
        panelId: panel.panelId,
        label: metadata?.name || panel.panelId,
        icon: metadata?.icon ? <span>{metadata.icon}</span> : undefined,
        zone: panel.zone,
        order: panel.order
      }
    })

  const handleDragStart = useCallback((start: { draggableId: string; type: string }) => {
    const panel = zonePanels.find(p => p.id === start.draggableId)
    if (panel) {
      setDraggedPanel(panel)
    }
  }, [zonePanels])

  const handleDragEnd = useCallback((result: DropResult) => {
    setDraggedPanel(null)
    setDropZoneHover(null)

    if (!result.destination) return

    const sourceZone = result.source.droppableId as 'left' | 'right' | 'bottom' | 'main'
    const destZone = result.destination.droppableId as 'left' | 'right' | 'bottom' | 'main'
    const panelId = result.draggableId

    if (sourceZone === destZone) {
      // Reordering within same zone
      const newOrder = result.destination.index
      setPanelOrder(panelId, newOrder)
      
      // Update order for all affected panels
      const affectedPanels = zonePanels.filter(p => p.zone === sourceZone)
      affectedPanels.forEach((panel, index) => {
        if (index !== newOrder && panel.order !== index) {
          setPanelOrder(panel.id, index)
        }
      })
    } else {
      // Moving to different zone
      const newOrder = result.destination.index
      setPanelPosition(panelId, destZone, newOrder)
      
      if (onPanelMove) {
        onPanelMove(panelId, sourceZone, destZone, newOrder)
      }
    }
  }, [zonePanels, setPanelPosition, setPanelOrder, onPanelMove])

  const handleDragUpdate = useCallback((update: { destination?: { droppableId: string } | null }) => {
    if (update.destination) {
      const zone = update.destination.droppableId as 'left' | 'right' | 'bottom' | 'main'
      setDropZoneHover(zone)
    } else {
      setDropZoneHover(null)
    }
  }, [])

  return (
    <DragDropContext
      onDragStart={handleDragStart}
      onDragUpdate={handleDragUpdate}
      onDragEnd={handleDragEnd}
    >
      <div className={className}>
        <Droppable droppableId={zone} direction={zone === 'bottom' ? 'horizontal' : 'vertical'}>
          {(provided, snapshot) => (
            <div
              {...provided.droppableProps}
              ref={provided.innerRef}
              className={`min-h-[100px] ${
                snapshot.isDraggingOver
                  ? 'bg-blue-500/20 border-2 border-blue-500 border-dashed'
                  : dropZoneHover === zone
                  ? 'bg-gray-700/50 border border-gray-600'
                  : ''
              } transition-colors rounded p-2`}
            >
              {zonePanels.length === 0 ? (
                <div className="text-center text-gray-500 text-sm py-8">
                  Drop panels here
                </div>
              ) : (
                zonePanels.map((panel, index) => (
                  <Draggable
                    key={panel.id}
                    draggableId={panel.id}
                    index={index}
                  >
                    {(provided, snapshot) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        className={`mb-2 bg-gray-800 border border-gray-700 rounded p-3 ${
                          snapshot.isDragging
                            ? 'opacity-50 shadow-lg'
                            : 'hover:bg-gray-750'
                        } transition-all`}
                      >
                        <div className="flex items-center gap-2">
                          <div
                            {...provided.dragHandleProps}
                            className="cursor-grab active:cursor-grabbing text-gray-500 hover:text-gray-300"
                          >
                            <GripVertical className="w-4 h-4" />
                          </div>
                          {panel.icon && <div className="w-4 h-4">{panel.icon}</div>}
                          <span className="text-sm text-gray-300 flex-1">{panel.label}</span>
                          <span className="text-xs text-gray-500">#{panel.order}</span>
                        </div>
                      </div>
                    )}
                  </Draggable>
                ))
              )}
              {provided.placeholder}
            </div>
          )}
        </Droppable>

        {/* Drag Preview */}
        {draggedPanel && (
          <div className="fixed top-4 right-4 bg-gray-800 border border-gray-700 rounded-lg shadow-xl p-3 z-50 pointer-events-none">
            <div className="flex items-center gap-2">
              {draggedPanel.icon && <div className="w-4 h-4">{draggedPanel.icon}</div>}
              <span className="text-sm text-gray-300">{draggedPanel.label}</span>
            </div>
          </div>
        )}
      </div>
    </DragDropContext>
  )
}

