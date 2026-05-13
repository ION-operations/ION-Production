/**
 * Canvas Editor Component
 * Living document editor with rich content support and AI integration
 */

import React, { useState, useCallback, useEffect } from 'react'
import { useCanvasStore } from '../store/canvasStore'
import { FilePreview } from '../components/FilePreview'
import {
  FileText, Edit3, Plus, Trash2, Move, Sparkles, History,
  GitBranch, Save, X, Check, ChevronDown, ChevronUp,
  MessageSquare, ExternalLink, Settings, MoreVertical
} from 'lucide-react'
import type { CanvasSection } from '../types/canvasTypes'

interface CanvasEditorProps {
  canvasId: string
  onClose?: () => void
}

export const CanvasEditor: React.FC<CanvasEditorProps> = ({ canvasId, onClose }) => {
  const canvas = useCanvasStore((state) => state.getCanvas(canvasId))
  const updateCanvas = useCanvasStore((state) => state.updateCanvas)
  const addSection = useCanvasStore((state) => state.addSection)
  const updateSection = useCanvasStore((state) => state.updateSection)
  const deleteSection = useCanvasStore((state) => state.deleteSection)
  const setSelectedSection = useCanvasStore((state) => state.setSelectedSection)
  const setEditingSection = useCanvasStore((state) => state.setEditingSection)
  const selectedSection = useCanvasStore((state) => state.selectedSection)
  const editingSection = useCanvasStore((state) => state.editingSection)
  const createVersion = useCanvasStore((state) => state.createVersion)
  
  const [showAddMenu, setShowAddMenu] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [showBranches, setShowBranches] = useState(false)
  
  if (!canvas) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900 text-gray-400">
        <div className="text-center">
          <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>Canvas not found</p>
        </div>
      </div>
    )
  }
  
  const handleAddSection = (type: CanvasSection['type']) => {
    const content = type === 'text' ? '' : type === 'code' ? '// Code here' : ''
    addSection(canvasId, {
      type,
      content,
      editable: true,
      metadata: {
        createdBy: 'user',
        editedBy: [],
        timestamp: new Date(),
        version: 1
      }
    })
    setShowAddMenu(false)
  }
  
  const handleUpdateSection = (sectionId: string, content: string) => {
    updateSection(canvasId, sectionId, { content })
  }
  
  const handleDeleteSection = (sectionId: string) => {
    if (confirm('Delete this section?')) {
      deleteSection(canvasId, sectionId)
      if (selectedSection === sectionId) {
        setSelectedSection(null)
      }
    }
  }
  
  const handleSave = () => {
    createVersion(canvasId)
  }
  
  return (
    <div className="h-full flex flex-col bg-gray-900 text-gray-100">
      {/* Header */}
      <div className="h-12 px-4 border-b border-gray-700 bg-gray-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileText className="w-4 h-4 text-blue-400" />
          <input
            type="text"
            value={canvas.title}
            onChange={(e) => updateCanvas(canvasId, { title: e.target.value })}
            className="bg-transparent border-none outline-none text-sm font-medium text-white"
            placeholder="Canvas Title"
          />
          <span className="text-xs text-gray-500 px-2 py-0.5 bg-gray-700 rounded">
            v{canvas.metadata.version}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowAddMenu(!showAddMenu)}
            className="px-2 py-1 text-xs text-gray-400 hover:text-gray-200 hover:bg-gray-700 rounded flex items-center gap-1.5"
            title="Add Section"
          >
            <Plus className="w-3 h-3" />
            <span>Add</span>
          </button>
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="px-2 py-1 text-xs text-gray-400 hover:text-gray-200 hover:bg-gray-700 rounded flex items-center gap-1.5"
            title="Version History"
          >
            <History className="w-3 h-3" />
          </button>
          <button
            onClick={() => setShowBranches(!showBranches)}
            className="px-2 py-1 text-xs text-gray-400 hover:text-gray-200 hover:bg-gray-700 rounded flex items-center gap-1.5"
            title="Branches"
          >
            <GitBranch className="w-3 h-3" />
          </button>
          <button
            onClick={handleSave}
            className="px-2 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded flex items-center gap-1.5"
            title="Save Version"
          >
            <Save className="w-3 h-3" />
            <span>Save</span>
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="px-2 py-1 text-xs text-gray-400 hover:text-gray-200 hover:bg-gray-700 rounded"
              title="Close"
            >
              <X className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>
      
      {/* Add Menu Dropdown */}
      {showAddMenu && (
        <div className="absolute top-12 right-4 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50 min-w-[200px]">
          <div className="p-2">
            <button
              onClick={() => handleAddSection('text')}
              className="w-full px-3 py-2 text-left text-sm text-gray-300 hover:bg-gray-700 rounded flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />
              <span>Text Section</span>
            </button>
            <button
              onClick={() => handleAddSection('code')}
              className="w-full px-3 py-2 text-left text-sm text-gray-300 hover:bg-gray-700 rounded flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />
              <span>Code Block</span>
            </button>
            <button
              onClick={() => handleAddSection('image')}
              className="w-full px-3 py-2 text-left text-sm text-gray-300 hover:bg-gray-700 rounded flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />
              <span>Image</span>
            </button>
          </div>
        </div>
      )}
      
      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto p-6">
          {canvas.content.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p className="mb-2">This canvas is empty</p>
              <button
                onClick={() => handleAddSection('text')}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm"
              >
                Add First Section
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {canvas.content.map((section, index) => (
                <CanvasSectionEditor
                  key={section.id}
                  section={section}
                  index={index}
                  isSelected={selectedSection === section.id}
                  isEditing={editingSection === section.id}
                  onSelect={() => setSelectedSection(section.id)}
                  onEdit={() => setEditingSection(section.id)}
                  onUpdate={(content) => handleUpdateSection(section.id, content)}
                  onDelete={() => handleDeleteSection(section.id)}
                  onDeselect={() => setSelectedSection(null)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
      
      {/* Footer - AIM-OS Metadata */}
      <div className="h-8 px-4 border-t border-gray-700 bg-gray-800 flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-4">
          <span>Confidence: {Math.round(canvas.aimos.confidence * 100)}%</span>
          <span>•</span>
          <span>{canvas.content.length} sections</span>
          <span>•</span>
          <span>{canvas.metadata.relatedMessages?.length || 0} related messages</span>
        </div>
        <div className="flex items-center gap-2">
          <span>Updated: {new Date(canvas.metadata.updatedAt).toLocaleString()}</span>
        </div>
      </div>
    </div>
  )
}

interface CanvasSectionEditorProps {
  section: CanvasSection
  index: number
  isSelected: boolean
  isEditing: boolean
  onSelect: () => void
  onEdit: () => void
  onUpdate: (content: string) => void
  onDelete: () => void
  onDeselect: () => void
}

const CanvasSectionEditor: React.FC<CanvasSectionEditorProps> = ({
  section,
  index,
  isSelected,
  isEditing,
  onSelect,
  onEdit,
  onUpdate,
  onDelete,
  onDeselect
}) => {
  const [localContent, setLocalContent] = useState(section.content)
  
  useEffect(() => {
    setLocalContent(section.content)
  }, [section.content])
  
  const handleSave = () => {
    onUpdate(localContent)
    onDeselect()
  }
  
  if (section.type === 'text') {
    return (
      <div
        className={`relative group border rounded-lg p-4 transition-all ${
          isSelected ? 'border-blue-500 bg-blue-900/20' : 'border-gray-700 bg-gray-800/50'
        }`}
        onClick={onSelect}
      >
        {isEditing ? (
          <div className="space-y-2">
            <textarea
              value={localContent}
              onChange={(e) => setLocalContent(e.target.value)}
              className="w-full h-32 p-3 bg-gray-950 text-gray-100 rounded border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm resize-none"
              placeholder="Enter markdown content..."
              autoFocus
            />
            <div className="flex items-center justify-end gap-2">
              <button
                onClick={onDeselect}
                className="px-3 py-1 text-xs text-gray-400 hover:text-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="px-3 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded"
              >
                Save
              </button>
            </div>
          </div>
        ) : (
          <>
            <div className="prose prose-invert prose-sm max-w-none">
              <FilePreview content={localContent} theme="vs-dark" />
            </div>
            {isSelected && (
              <div className="absolute top-2 right-2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    onEdit()
                  }}
                  className="p-1.5 bg-gray-700 hover:bg-gray-600 rounded text-gray-300"
                  title="Edit"
                >
                  <Edit3 className="w-3 h-3" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    onDelete()
                  }}
                  className="p-1.5 bg-gray-700 hover:bg-red-600 rounded text-gray-300"
                  title="Delete"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            )}
          </>
        )}
      </div>
    )
  }
  
  if (section.type === 'code') {
    return (
      <div
        className={`relative group border rounded-lg overflow-hidden transition-all ${
          isSelected ? 'border-blue-500' : 'border-gray-700'
        }`}
        onClick={onSelect}
      >
        {isEditing ? (
          <div className="p-4 bg-gray-950">
            <textarea
              value={localContent}
              onChange={(e) => setLocalContent(e.target.value)}
              className="w-full h-48 p-3 bg-gray-900 text-gray-100 rounded border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm resize-none"
              placeholder="Enter code..."
              autoFocus
            />
            <div className="flex items-center justify-end gap-2 mt-2">
              <button
                onClick={onDeselect}
                className="px-3 py-1 text-xs text-gray-400 hover:text-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="px-3 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded"
              >
                Save
              </button>
            </div>
          </div>
        ) : (
          <>
            <FilePreview content={`\`\`\`typescript\n${localContent}\n\`\`\``} theme="vs-dark" />
            {isSelected && (
              <div className="absolute top-2 right-2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    onEdit()
                  }}
                  className="p-1.5 bg-gray-700 hover:bg-gray-600 rounded text-gray-300"
                  title="Edit"
                >
                  <Edit3 className="w-3 h-3" />
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    onDelete()
                  }}
                  className="p-1.5 bg-gray-700 hover:bg-red-600 rounded text-gray-300"
                  title="Delete"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            )}
          </>
        )}
      </div>
    )
  }
  
  return (
    <div className="border border-gray-700 rounded-lg p-4 bg-gray-800/50">
      <p className="text-sm text-gray-400">Unsupported section type: {section.type}</p>
    </div>
  )
}

