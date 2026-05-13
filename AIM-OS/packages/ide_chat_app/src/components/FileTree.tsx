import React, { useState } from 'react'
import { ChevronRight, ChevronDown, FileText, Folder, FolderOpen, Plus, Trash2, Edit2 } from 'lucide-react'

interface FileNode {
  name: string
  type: 'file' | 'folder'
  children?: FileNode[]
}

interface FileTreeProps {
  onFileSelect?: (path: string) => void
}

const sampleTree: FileNode = {
  name: 'AIM-OS',
  type: 'folder',
  children: [
    {
      name: 'packages',
      type: 'folder',
      children: [
        { name: 'cmc_service', type: 'folder' },
        { name: 'hhni', type: 'folder' },
        { name: 'vif', type: 'folder' },
        { name: 'apoe', type: 'folder' },
        { name: 'ide_chat_app', type: 'folder' }
      ]
    },
    {
      name: 'knowledge_architecture',
      type: 'folder',
      children: [
        { name: 'AETHER_MEMORY', type: 'folder' },
        { name: 'systems', type: 'folder' },
        { name: 'applications', type: 'folder' }
      ]
    },
    { name: 'README.md', type: 'file' },
    { name: 'goals', type: 'folder' }
  ]
}

export const FileTree: React.FC<FileTreeProps> = ({ onFileSelect }) => {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set(['AIM-OS', 'AIM-OS/packages', 'AIM-OS/knowledge_architecture']))
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; path: string } | null>(null)

  const toggleNode = (path: string) => {
    const newExpanded = new Set(expandedNodes)
    if (newExpanded.has(path)) {
      newExpanded.delete(path)
    } else {
      newExpanded.add(path)
    }
    setExpandedNodes(newExpanded)
  }

  const handleContextMenu = (e: React.MouseEvent, path: string) => {
    e.preventDefault()
    e.stopPropagation()
    setContextMenu({ x: e.clientX, y: e.clientY, path })
  }

  const handleCreateFile = (path: string) => {
    console.log('Create file:', path)
    // TODO: Implement file creation
    setContextMenu(null)
  }

  const handleDelete = (path: string) => {
    console.log('Delete:', path)
    // TODO: Implement file deletion
    setContextMenu(null)
  }

  const handleRename = (path: string) => {
    console.log('Rename:', path)
    // TODO: Implement rename
    setContextMenu(null)
  }

  const renderNode = (node: FileNode, path: string = ''): React.ReactNode => {
    const currentPath = path ? `${path}/${node.name}` : node.name
    const isExpanded = expandedNodes.has(currentPath)
    const isFile = node.type === 'file'

    return (
      <div key={currentPath}>
        <div
          className="flex items-center gap-1 px-2 py-1 hover:bg-gray-700 rounded cursor-pointer group"
          onClick={() => {
            if (!isFile) {
              toggleNode(currentPath)
            } else if (onFileSelect) {
              onFileSelect(currentPath)
            }
          }}
          onContextMenu={(e) => handleContextMenu(e, currentPath)}
        >
          {!isFile && (
            <div className="w-4 h-4 flex items-center justify-center">
              {isExpanded ? (
                <ChevronDown className="w-3 h-3 text-gray-400" />
              ) : (
                <ChevronRight className="w-3 h-3 text-gray-400" />
              )}
            </div>
          )}
          {isFile && <div className="w-4 h-4" />}
          
          {!isFile && (
            isExpanded ? (
              <FolderOpen className="w-4 h-4 text-blue-400" />
            ) : (
              <Folder className="w-4 h-4 text-blue-400" />
            )
          )}
          {isFile && <FileText className="w-4 h-4 text-gray-400" />}
          
          <span className="text-sm text-gray-300 flex-1">{node.name}</span>
          
          {/* Context menu trigger (visible on hover) */}
          <button
            className="opacity-0 group-hover:opacity-100 transition-opacity p-0.5 hover:bg-gray-600 rounded"
            onClick={(e) => {
              e.stopPropagation()
              handleContextMenu(e, currentPath)
            }}
          >
            <Plus className="w-3 h-3 text-gray-400" />
          </button>
        </div>
        
        {!isFile && isExpanded && node.children && (
          <div className="ml-4">
            {node.children.map((child) => renderNode(child, currentPath))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto bg-gray-800 p-2 relative">
      <div className="mb-2 px-2 py-1 text-xs font-semibold text-gray-400 uppercase tracking-wide">
        Explorer
      </div>
      {renderNode(sampleTree)}

      {/* Context Menu */}
      {contextMenu && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setContextMenu(null)}
          />
          
          {/* Menu */}
          <div
            className="fixed z-20 bg-gray-700 border border-gray-600 rounded shadow-lg py-1 min-w-[150px]"
            style={{ left: contextMenu.x, top: contextMenu.y }}
          >
            <button
              className="w-full px-4 py-2 text-left text-sm text-gray-200 hover:bg-gray-600 flex items-center gap-2"
              onClick={() => handleCreateFile(contextMenu.path)}
            >
              <Plus className="w-4 h-4" />
              New File
            </button>
            <button
              className="w-full px-4 py-2 text-left text-sm text-gray-200 hover:bg-gray-600 flex items-center gap-2"
              onClick={() => handleCreateFile(contextMenu.path)}
            >
              <FolderOpen className="w-4 h-4" />
              New Folder
            </button>
            <div className="h-px bg-gray-600 my-1" />
            <button
              className="w-full px-4 py-2 text-left text-sm text-gray-200 hover:bg-gray-600 flex items-center gap-2"
              onClick={() => handleRename(contextMenu.path)}
            >
              <Edit2 className="w-4 h-4" />
              Rename
            </button>
            <div className="h-px bg-gray-600 my-1" />
            <button
              className="w-full px-4 py-2 text-left text-sm text-red-400 hover:bg-gray-600 flex items-center gap-2"
              onClick={() => handleDelete(contextMenu.path)}
            >
              <Trash2 className="w-4 h-4" />
              Delete
            </button>
          </div>
        </>
      )}
    </div>
  )
}
