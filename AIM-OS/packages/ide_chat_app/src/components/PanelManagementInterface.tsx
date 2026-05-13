// Panel Management Interface
// Integrates drag-drop panel management with IDELayout
// V2 Enhancement - Week 1 Completion

import React, { useState } from 'react'
import { X, Settings, GripVertical } from 'lucide-react'
import { EnhancedPanelDragDrop } from './EnhancedPanelDragDrop'
import { usePanelStore } from '../store/panelStore'
import { panelRegistry } from '../store/panelRegistry'

interface PanelManagementInterfaceProps {
  isOpen: boolean
  onClose: () => void
  onApply?: () => void
}

export const PanelManagementInterface: React.FC<PanelManagementInterfaceProps> = ({
  isOpen,
  onClose,
  onApply
}) => {
  const { panels, saveLayout, loadLayout, layouts } = usePanelStore()
  const [selectedZone, setSelectedZone] = useState<'left' | 'right' | 'bottom' | 'main'>('left')

  if (!isOpen) return null

  const handleApply = () => {
    // Save current layout
    saveLayout('current', 'Current Layout')
    onApply?.()
    onClose()
  }

  const handlePanelMove = (panelId: string, fromZone: string, toZone: string, newOrder: number) => {
    console.log(`Panel ${panelId} moved from ${fromZone} to ${toZone} at position ${newOrder}`)
    // PanelStore will handle the state update
  }

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
      <div className="bg-gray-900 border border-gray-700 rounded-lg w-[90vw] h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-semibold text-gray-300">Panel Management</h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleApply}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm font-medium text-white"
            >
              Apply Layout
            </button>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Zone Tabs */}
        <div className="flex border-b border-gray-700">
          {(['left', 'right', 'bottom', 'main'] as const).map(zone => (
            <button
              key={zone}
              onClick={() => setSelectedZone(zone)}
              className={`px-4 py-2 text-sm font-medium capitalize transition-colors ${
                selectedZone === zone
                  ? 'bg-gray-800 text-white border-b-2 border-blue-500'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
              }`}
            >
              {zone}
            </button>
          ))}
        </div>

        {/* Drag-Drop Zone */}
        <div className="flex-1 overflow-hidden p-4">
          <div className="h-full border border-gray-700 rounded-lg bg-gray-800">
            <EnhancedPanelDragDrop
              zone={selectedZone}
              onPanelMove={handlePanelMove}
              className="h-full"
            />
          </div>
        </div>

        {/* Info */}
        <div className="px-4 py-2 border-t border-gray-700 bg-gray-800 text-xs text-gray-400">
          Drag panels to reorder. Panels can be moved between zones. Layout will be saved automatically.
        </div>
      </div>
    </div>
  )
}

