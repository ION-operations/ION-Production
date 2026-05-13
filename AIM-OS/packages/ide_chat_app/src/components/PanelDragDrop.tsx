/**
 * Panel Drag-and-Drop System
 * 
 * Phase 3.1: Drag-and-Drop System Implementation
 * 
 * Features:
 * - Drag handles for panels
 * - Drop zones (left, right, top, bottom, main)
 * - Visual feedback during dragging
 * - Panel reordering logic
 * - AIM-OS integration (CMC storage for layout preferences)
 */

import React, { useState, useCallback } from 'react'
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd'
import { GripVertical, X } from 'lucide-react'
import { LeftPanelType, RightPanelType, BottomPanelType } from './RevIDELayout'

export interface PanelDragItem {
  id: string
  type: 'left' | 'right' | 'bottom' | 'main'
  panelId: LeftPanelType | RightPanelType | BottomPanelType | string
  label: string
  icon?: React.ReactNode
}

interface PanelDragDropProps {
  leftPanels: Array<{ id: LeftPanelType; label: string; icon?: React.ReactNode }>
  rightPanels: Array<{ id: RightPanelType; label: string; icon?: React.ReactNode }>
  bottomPanels: Array<{ id: BottomPanelType; label: string; icon?: React.ReactNode }>
  onReorder: (source: { type: 'left' | 'right' | 'bottom'; index: number }, destination: { type: 'left' | 'right' | 'bottom'; index: number }) => void
  onMoveToZone: (panelId: string, sourceZone: 'left' | 'right' | 'bottom', targetZone: 'left' | 'right' | 'bottom' | 'main') => void
  onClosePanel?: (panelId: string, zone: 'left' | 'right' | 'bottom') => void
}

export const PanelDragDrop: React.FC<PanelDragDropProps> = ({
  leftPanels,
  rightPanels,
  bottomPanels,
  onReorder,
  onMoveToZone,
  onClosePanel
}) => {
  const [draggedPanel, setDraggedPanel] = useState<PanelDragItem | null>(null)
  const [dropZoneHover, setDropZoneHover] = useState<'left' | 'right' | 'bottom' | 'main' | null>(null)

  const handleDragStart = useCallback((start: { draggableId: string; type: string }) => {
    // Find the panel being dragged
    const allPanels = [
      ...leftPanels.map(p => ({ ...p, type: 'left' as const })),
      ...rightPanels.map(p => ({ ...p, type: 'right' as const })),
      ...bottomPanels.map(p => ({ ...p, type: 'bottom' as const }))
    ]
    const panel = allPanels.find(p => `${p.type}-${p.id}` === start.draggableId)
    if (panel) {
      setDraggedPanel({
        id: start.draggableId,
        type: panel.type,
        panelId: panel.id,
        label: panel.label,
        icon: panel.icon
      })
    }
  }, [leftPanels, rightPanels, bottomPanels])

  const handleDragEnd = useCallback((result: DropResult) => {
    setDraggedPanel(null)
    setDropZoneHover(null)

    if (!result.destination) {
      return
    }

    const sourceType = result.source.droppableId as 'left' | 'right' | 'bottom'
    const destType = result.destination.droppableId as 'left' | 'right' | 'bottom' | 'main'

    // Same zone reordering
    if (sourceType === destType && sourceType !== 'main') {
      onReorder(
        { type: sourceType, index: result.source.index },
        { type: destType, index: result.destination.index }
      )
    }
    // Cross-zone movement
    else if (destType !== 'main') {
      const panelId = result.draggableId.split('-').slice(1).join('-')
      onMoveToZone(panelId, sourceType, destType)
    }
  }, [onReorder, onMoveToZone])

  const handleDragUpdate = useCallback((update: { destination?: { droppableId: string } | null }) => {
    if (update.destination) {
      const zone = update.destination.droppableId as 'left' | 'right' | 'bottom' | 'main'
      setDropZoneHover(zone)
    } else {
      setDropZoneHover(null)
    }
  }, [])

  const renderPanelList = (
    panels: Array<{ id: string; label: string; icon?: React.ReactNode }>,
    zone: 'left' | 'right' | 'bottom',
    zoneLabel: string
  ) => {
    return (
      <Droppable droppableId={zone} direction={zone === 'bottom' ? 'horizontal' : 'vertical'}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`min-h-[100px] p-2 rounded transition-colors ${
              snapshot.isDraggingOver
                ? 'bg-blue-600/20 border-2 border-blue-500 border-dashed'
                : dropZoneHover === zone
                ? 'bg-gray-700/50 border border-gray-600'
                : 'bg-transparent'
            }`}
          >
            <div className="text-xs text-gray-400 mb-2 uppercase font-semibold">{zoneLabel}</div>
            {panels.length === 0 ? (
              <div className="text-xs text-gray-500 py-4 text-center">
                Drop panels here
              </div>
            ) : (
              panels.map((panel, index) => (
                <Draggable
                  key={`${zone}-${panel.id}`}
                  draggableId={`${zone}-${panel.id}`}
                  index={index}
                >
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      className={`mb-2 p-2 bg-gray-700 rounded border transition-all ${
                        snapshot.isDragging
                          ? 'shadow-lg border-blue-500 bg-gray-600'
                          : 'border-gray-600 hover:border-gray-500'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <div {...provided.dragHandleProps} className="cursor-grab active:cursor-grabbing">
                          <GripVertical className="w-4 h-4 text-gray-400" />
                        </div>
                        {panel.icon && <div className="w-4 h-4">{panel.icon}</div>}
                        <span className="text-sm text-gray-300 flex-1">{panel.label}</span>
                        {onClosePanel && (
                          <button
                            onClick={() => onClosePanel(panel.id, zone)}
                            className="p-1 text-gray-400 hover:text-gray-200 hover:bg-gray-600 rounded transition-colors"
                            aria-label={`Close ${panel.label}`}
                          >
                            <X className="w-3 h-3" />
                          </button>
                        )}
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
    )
  }

  return (
    <DragDropContext
      onDragStart={handleDragStart}
      onDragUpdate={handleDragUpdate}
      onDragEnd={handleDragEnd}
    >
      <div className="space-y-4">
        {/* Left Zone */}
        {renderPanelList(
          leftPanels.map(p => ({ id: p.id || '', label: p.label, icon: p.icon })),
          'left',
          'Left Drawer'
        )}

        {/* Right Zone */}
        {renderPanelList(
          rightPanels.map(p => ({ id: p.id || '', label: p.label, icon: p.icon })),
          'right',
          'Right Drawer'
        )}

        {/* Bottom Zone */}
        {renderPanelList(
          bottomPanels.map(p => ({ id: p.id || '', label: p.label, icon: p.icon })),
          'bottom',
          'Bottom Drawer'
        )}

        {/* Main Zone (drop target only) */}
        <Droppable droppableId="main" direction="vertical">
          {(provided, snapshot) => (
            <div
              ref={provided.innerRef}
              {...provided.droppableProps}
              className={`min-h-[100px] p-4 rounded border-2 border-dashed transition-colors ${
                snapshot.isDraggingOver
                  ? 'bg-blue-600/20 border-blue-500'
                  : dropZoneHover === 'main'
                  ? 'bg-gray-700/50 border-gray-600'
                  : 'bg-transparent border-gray-700'
              }`}
            >
              <div className="text-xs text-gray-400 mb-2 uppercase font-semibold">Main Content</div>
              <div className="text-xs text-gray-500 py-4 text-center">
                {snapshot.isDraggingOver ? 'Drop to open in main area' : 'Drop panels here to open in main area'}
              </div>
              {provided.placeholder}
            </div>
          )}
        </Droppable>

        {/* Drag Preview */}
        {draggedPanel && (
          <div className="fixed pointer-events-none z-50 opacity-50">
            <div className="p-2 bg-gray-700 rounded border border-blue-500 shadow-lg">
              <div className="flex items-center gap-2">
                {draggedPanel.icon && <div className="w-4 h-4">{draggedPanel.icon}</div>}
                <span className="text-sm text-gray-300">{draggedPanel.label}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </DragDropContext>
  )
}

