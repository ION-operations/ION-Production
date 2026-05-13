// Panel Customization Component - V2 Layout System Enhancement
// Full panel customization UI for settings, sizes, visibility, and preferences

import React, { useState } from 'react'
import { usePanelStore, Panel, PanelType } from '../store/panelStore'
import { Settings, X, Eye, EyeOff, Pin, PinOff, Maximize2, Minimize2, Trash2, Plus } from 'lucide-react'

interface PanelCustomizationProps {
  onClose?: () => void
}

export const PanelCustomization: React.FC<PanelCustomizationProps> = ({ onClose }) => {
  const {
    panels,
    selectedPanel,
    setSelectedPanel,
    updatePanel,
    togglePanelVisibility,
    togglePanelPinned,
    resizePanel,
    deletePanel,
    addPanel,
  } = usePanelStore()
  
  const [activeTab, setActiveTab] = useState<'panels' | 'settings'>('panels')
  const [editingPanel, setEditingPanel] = useState<Panel | null>(null)
  
  const handlePanelClick = (panel: Panel) => {
    setSelectedPanel(panel)
    setEditingPanel(panel)
  }
  
  const handleUpdatePanel = (panelId: string, updates: Partial<Panel>) => {
    updatePanel(panelId, updates)
    if (editingPanel?.id === panelId) {
      setEditingPanel({ ...editingPanel, ...updates })
    }
  }
  
  const handleSizeChange = (panelId: string, size: number) => {
    resizePanel(panelId, size)
    if (editingPanel?.id === panelId) {
      setEditingPanel({ ...editingPanel, size })
    }
  }
  
  const handleAddPanel = () => {
    // Show panel type selector
    const panelTypes: PanelType[] = [
      'file-explorer',
      'memory-browser',
      'system-status',
      'context-web',
      'timeline-view',
      'outline',
      'code-editor',
      'terminal',
      'problems',
    ]
    
    const type = prompt('Select panel type:\n' + panelTypes.map((t, i) => `${i + 1}. ${t}`).join('\n'))
    if (!type) return
    
    const selectedType = panelTypes[parseInt(type) - 1]
    if (!selectedType) return
    
    const newPanel: Panel = {
      id: `panel-${selectedType}-${Date.now()}`,
      type: selectedType,
      zone: 'left',
      size: 30,
      minSize: 20,
      maxSize: 80,
      visible: true,
      expanded: true,
      pinned: false,
      order: panels.filter(p => p.zone === 'left').length,
      settings: {},
    }
    
    addPanel(newPanel)
    setSelectedPanel(newPanel)
    setEditingPanel(newPanel)
  }
  
  const getPanelsByZone = (zone: 'left' | 'right' | 'bottom') => {
    return panels.filter(p => p.zone === zone).sort((a, b) => a.order - b.order)
  }
  
  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
      <div className="bg-gray-800 border border-gray-700 rounded-lg w-full max-w-4xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-blue-400" />
            <h2 className="text-lg font-semibold text-gray-200">Panel Customization</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-gray-200"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        
        {/* Tabs */}
        <div className="flex border-b border-gray-700">
          <button
            onClick={() => setActiveTab('panels')}
            className={`px-4 py-2 text-sm font-medium ${
              activeTab === 'panels'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            Panels
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`px-4 py-2 text-sm font-medium ${
              activeTab === 'settings'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            Settings
          </button>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          {activeTab === 'panels' && (
            <div className="space-y-6">
              {/* Add Panel Button */}
              <div className="flex justify-end">
                <button
                  onClick={handleAddPanel}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-white text-sm font-medium flex items-center gap-2"
                >
                  <Plus className="w-4 h-4" />
                  Add Panel
                </button>
              </div>
              
              {/* Left Zone Panels */}
              <div>
                <h3 className="text-sm font-semibold text-gray-300 mb-2">Left Zone</h3>
                <div className="space-y-2">
                  {getPanelsByZone('left').map((panel) => (
                    <PanelItem
                      key={panel.id}
                      panel={panel}
                      isSelected={selectedPanel?.id === panel.id}
                      isEditing={editingPanel?.id === panel.id}
                      onClick={() => handlePanelClick(panel)}
                      onUpdate={(updates) => handleUpdatePanel(panel.id, updates)}
                      onSizeChange={(size) => handleSizeChange(panel.id, size)}
                      onToggleVisibility={() => togglePanelVisibility(panel.id)}
                      onTogglePinned={() => togglePanelPinned(panel.id)}
                      onDelete={() => deletePanel(panel.id)}
                    />
                  ))}
                  {getPanelsByZone('left').length === 0 && (
                    <div className="text-sm text-gray-500 py-4 text-center">
                      No panels in left zone
                    </div>
                  )}
                </div>
              </div>
              
              {/* Right Zone Panels */}
              <div>
                <h3 className="text-sm font-semibold text-gray-300 mb-2">Right Zone</h3>
                <div className="space-y-2">
                  {getPanelsByZone('right').map((panel) => (
                    <PanelItem
                      key={panel.id}
                      panel={panel}
                      isSelected={selectedPanel?.id === panel.id}
                      isEditing={editingPanel?.id === panel.id}
                      onClick={() => handlePanelClick(panel)}
                      onUpdate={(updates) => handleUpdatePanel(panel.id, updates)}
                      onSizeChange={(size) => handleSizeChange(panel.id, size)}
                      onToggleVisibility={() => togglePanelVisibility(panel.id)}
                      onTogglePinned={() => togglePanelPinned(panel.id)}
                      onDelete={() => deletePanel(panel.id)}
                    />
                  ))}
                  {getPanelsByZone('right').length === 0 && (
                    <div className="text-sm text-gray-500 py-4 text-center">
                      No panels in right zone
                    </div>
                  )}
                </div>
              </div>
              
              {/* Bottom Zone Panels */}
              <div>
                <h3 className="text-sm font-semibold text-gray-300 mb-2">Bottom Zone</h3>
                <div className="space-y-2">
                  {getPanelsByZone('bottom').map((panel) => (
                    <PanelItem
                      key={panel.id}
                      panel={panel}
                      isSelected={selectedPanel?.id === panel.id}
                      isEditing={editingPanel?.id === panel.id}
                      onClick={() => handlePanelClick(panel)}
                      onUpdate={(updates) => handleUpdatePanel(panel.id, updates)}
                      onSizeChange={(size) => handleSizeChange(panel.id, size)}
                      onToggleVisibility={() => togglePanelVisibility(panel.id)}
                      onTogglePinned={() => togglePanelPinned(panel.id)}
                      onDelete={() => deletePanel(panel.id)}
                    />
                  ))}
                  {getPanelsByZone('bottom').length === 0 && (
                    <div className="text-sm text-gray-500 py-4 text-center">
                      No panels in bottom zone
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'settings' && editingPanel && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-gray-300">Panel Settings: {editingPanel.type}</h3>
              
              {/* Size Settings */}
              <div className="space-y-2">
                <label className="text-sm text-gray-400">Size ({editingPanel.size}%)</label>
                <input
                  type="range"
                  min={editingPanel.minSize}
                  max={editingPanel.maxSize}
                  value={editingPanel.size}
                  onChange={(e) => handleSizeChange(editingPanel.id, parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Min: {editingPanel.minSize}%</span>
                  <span>Max: {editingPanel.maxSize}%</span>
                </div>
              </div>
              
              {/* Min/Max Size */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-gray-400 block mb-1">Min Size (%)</label>
                  <input
                    type="number"
                    value={editingPanel.minSize}
                    onChange={(e) => handleUpdatePanel(editingPanel.id, { minSize: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-gray-200"
                    min="0"
                    max="100"
                  />
                </div>
                <div>
                  <label className="text-sm text-gray-400 block mb-1">Max Size (%)</label>
                  <input
                    type="number"
                    value={editingPanel.maxSize}
                    onChange={(e) => handleUpdatePanel(editingPanel.id, { maxSize: parseInt(e.target.value) || 100 })}
                    className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-gray-200"
                    min="0"
                    max="100"
                  />
                </div>
              </div>
              
              {/* Order */}
              <div>
                <label className="text-sm text-gray-400 block mb-1">Order</label>
                <input
                  type="number"
                  value={editingPanel.order}
                  onChange={(e) => handleUpdatePanel(editingPanel.id, { order: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-gray-200"
                  min="0"
                />
              </div>
              
              {/* Custom Settings */}
              <div>
                <label className="text-sm text-gray-400 block mb-1">Custom Settings (JSON)</label>
                <textarea
                  value={JSON.stringify(editingPanel.settings, null, 2)}
                  onChange={(e) => {
                    try {
                      const settings = JSON.parse(e.target.value)
                      handleUpdatePanel(editingPanel.id, { settings })
                    } catch (err) {
                      // Invalid JSON, ignore
                    }
                  }}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-gray-200 font-mono text-xs"
                  rows={6}
                />
              </div>
            </div>
          )}
          
          {activeTab === 'settings' && !editingPanel && (
            <div className="text-sm text-gray-500 py-8 text-center">
              Select a panel to edit its settings
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

interface PanelItemProps {
  panel: Panel
  isSelected: boolean
  isEditing: boolean
  onClick: () => void
  onUpdate: (updates: Partial<Panel>) => void
  onSizeChange: (size: number) => void
  onToggleVisibility: () => void
  onTogglePinned: () => void
  onDelete: () => void
}

const PanelItem: React.FC<PanelItemProps> = ({
  panel,
  isSelected,
  isEditing,
  onClick,
  onToggleVisibility,
  onTogglePinned,
  onDelete,
}) => {
  return (
    <div
      onClick={onClick}
      className={`p-3 rounded border cursor-pointer transition-all ${
        isSelected
          ? 'border-blue-500 bg-blue-900/20'
          : 'border-gray-700 bg-gray-900 hover:border-gray-600'
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-200">{panel.type}</span>
            {panel.pinned && (
              <Pin className="w-3 h-3 text-yellow-400" />
            )}
            {!panel.visible && (
              <EyeOff className="w-3 h-3 text-gray-500" />
            )}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Zone: {panel.zone} • Size: {panel.size}% • Order: {panel.order}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation()
              onToggleVisibility()
            }}
            className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-gray-200"
            title={panel.visible ? 'Hide panel' : 'Show panel'}
          >
            {panel.visible ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onTogglePinned()
            }}
            className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-gray-200"
            title={panel.pinned ? 'Unpin panel' : 'Pin panel'}
          >
            {panel.pinned ? <Pin className="w-4 h-4 text-yellow-400" /> : <PinOff className="w-4 h-4" />}
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation()
              if (confirm('Delete this panel?')) {
                onDelete()
              }
            }}
            className="p-1 hover:bg-red-900/30 rounded text-gray-400 hover:text-red-400"
            title="Delete panel"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

