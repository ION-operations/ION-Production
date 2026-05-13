// Draggable Panel Component - V2 Layout System Enhancement
// HTML5 drag-and-drop wrapper for panels

import React, { useState } from 'react'
import { usePanelStore, Panel, ZoneType } from '../store/panelStore'
import { GripVertical } from 'lucide-react'

interface DraggablePanelProps {
  panel: Panel
  children: React.ReactNode
  className?: string
}

export const DraggablePanel: React.FC<DraggablePanelProps> = ({ panel, children, className = '' }) => {
  const { setDraggedPanel, movePanel, setDropTarget } = usePanelStore()
  const [isDragging, setIsDragging] = useState(false)
  
  const handleDragStart = (e: React.DragEvent) => {
    setIsDragging(true)
    setDraggedPanel(panel)
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', panel.id)
    
    // Set drag image
    if (e.dataTransfer.setDragImage) {
      const dragImage = document.createElement('div')
      dragImage.className = 'p-2 bg-blue-600 text-white rounded shadow-lg'
      dragImage.textContent = panel.type.replace('-', ' ')
      dragImage.style.position = 'absolute'
      dragImage.style.top = '-1000px'
      document.body.appendChild(dragImage)
      e.dataTransfer.setDragImage(dragImage, 0, 0)
      setTimeout(() => document.body.removeChild(dragImage), 0)
    }
  }
  
  const handleDragEnd = () => {
    setIsDragging(false)
    setDraggedPanel(null)
    setDropTarget(null)
  }
  
  return (
    <div
      draggable
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      className={`relative group ${isDragging ? 'opacity-50' : ''} ${className}`}
    >
      {/* Drag Handle */}
      <div className="absolute top-2 left-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity cursor-move">
        <GripVertical className="w-4 h-4 text-gray-500 hover:text-gray-300" />
      </div>
      
      {children}
    </div>
  )
}

// Drop Zone Component
interface DropZoneProps {
  zone: ZoneType
  children: React.ReactNode
  className?: string
}

export const DropZone: React.FC<DropZoneProps> = ({ zone, children, className = '' }) => {
  const { draggedPanel, setDropTarget, movePanel } = usePanelStore()
  const [isOver, setIsOver] = useState(false)
  
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    e.dataTransfer.dropEffect = 'move'
    
    if (draggedPanel && draggedPanel.zone !== zone) {
      setIsOver(true)
      // Set drop target zone
      const zoneData: any = {
        id: `zone-${zone}`,
        type: zone,
        panels: []
      }
      setDropTarget(zoneData)
    }
  }
  
  const handleDragLeave = () => {
    setIsOver(false)
    setDropTarget(null)
  }
  
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (draggedPanel && draggedPanel.zone !== zone) {
      movePanel(draggedPanel.id, zone)
    }
    
    setIsOver(false)
    setDropTarget(null)
  }
  
  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`${isOver ? 'ring-2 ring-blue-500 bg-blue-900/20' : ''} ${className}`}
    >
      {children}
    </div>
  )
}

