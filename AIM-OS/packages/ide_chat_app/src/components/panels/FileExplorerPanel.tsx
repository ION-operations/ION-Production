/**
 * Enhanced File Explorer Panel Component
 * 
 * Phase 1.3: Basic Panel Components
 * 
 * Enhanced version of FileTree with:
 * - Better AIM-OS integration (CMC, HHNI, VIF)
 * - Git status indicators
 * - File search
 * - Recent files
 * - Keyboard shortcuts
 * - Context menu enhancements
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { ChevronRight, ChevronDown, FileText, Folder, FolderOpen, Plus, Trash2, Edit2, Search, GitBranch, Clock, Star } from 'lucide-react'
import { useEditorStore } from '../../store/editorStore'
import { useAIMOS } from '../../hooks/useAIMOS'
import { useDebounce } from '../../hooks/useDebounce'
import { ErrorBoundary } from '../ErrorBoundary'
import { LoadingState } from '../LoadingState'

interface FileNode {
  name: string
  type: 'file' | 'folder'
  children?: FileNode[]
  gitStatus?: 'modified' | 'added' | 'deleted' | 'untracked' | 'clean'
  lastModified?: Date
  isFavorite?: boolean
}

interface FileExplorerPanelProps {
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
        { name: 'cmc_service', type: 'folder', gitStatus: 'clean' },
        { name: 'hhni', type: 'folder', gitStatus: 'modified' },
        { name: 'vif', type: 'folder', gitStatus: 'clean' },
        { name: 'apoe', type: 'folder', gitStatus: 'clean' },
        { name: 'ide_chat_app', type: 'folder', gitStatus: 'modified' },
      ],
    },
    {
      name: 'knowledge_architecture',
      type: 'folder',
      children: [
        { name: 'AETHER_MEMORY', type: 'folder', gitStatus: 'clean' },
        { name: 'systems', type: 'folder', gitStatus: 'clean' },
        { name: 'applications', type: 'folder', gitStatus: 'clean' },
      ],
    },
    { name: 'README.md', type: 'file', gitStatus: 'modified', isFavorite: true },
    { name: 'goals', type: 'folder', gitStatus: 'clean' },
    { name: 'ide_orchestration', type: 'folder', gitStatus: 'modified' },
  ],
}

export const FileExplorerPanel: React.FC<FileExplorerPanelProps> = React.memo(({ onFileSelect }) => {
  const { openTab } = useEditorStore()
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set(['AIM-OS', 'AIM-OS/packages', 'AIM-OS/knowledge_architecture']))
  const [contextMenu, setContextMenu] = useState<{ x: number; y: number; path: string } | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [showFavorites, setShowFavorites] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  // Debounce search query for performance
  const debouncedSearchQuery = useDebounce(searchQuery, 300)

  // AIM-OS integration
  const { cmc, hhni, isConnected, useMockData, loading } = useAIMOS()

  const toggleNode = useCallback((path: string) => {
    setExpandedNodes(prev => {
      const newExpanded = new Set(prev)
      if (newExpanded.has(path)) {
        newExpanded.delete(path)
      } else {
        newExpanded.add(path)
      }
      return newExpanded
    })
  }, [])

  const handleContextMenu = useCallback((e: React.MouseEvent, path: string) => {
    e.preventDefault()
    e.stopPropagation()
    setContextMenu({ x: e.clientX, y: e.clientY, path })
  }, [])

  const handleFileClick = useCallback((path: string, node: FileNode) => {
    if (node.type === 'file') {
      if (onFileSelect) {
        onFileSelect(path)
      }
      // Open file in editor
      const fileName = path.split('/').pop() || path
      const language = fileName.split('.').pop() || 'plaintext'
      openTab({
        fileName: path,
        content: `// ${fileName}\n// File content would be loaded here`,
        language,
      })
    } else {
      toggleNode(path)
    }
  }, [onFileSelect, openTab, toggleNode])

  const handleCreateFile = useCallback((path: string) => {
    console.log('Create file:', path)
    // TODO: Implement file creation via AIM-OS CMC
    setContextMenu(null)
  }, [])

  const handleDelete = useCallback((path: string) => {
    console.log('Delete:', path)
    // TODO: Implement file deletion via AIM-OS CMC
    setContextMenu(null)
  }, [])

  const handleRename = (path: string) => {
    console.log('Rename:', path)
    // TODO: Implement rename via AIM-OS CMC
    setContextMenu(null)
  }

  const getGitStatusColor = (status?: FileNode['gitStatus']) => {
    switch (status) {
      case 'modified': return 'text-yellow-400'
      case 'added': return 'text-green-400'
      case 'deleted': return 'text-red-400'
      case 'untracked': return 'text-gray-400'
      default: return 'text-gray-600'
    }
  }

  const getGitStatusIcon = (status?: FileNode['gitStatus']) => {
    if (status && status !== 'clean') {
      return <GitBranch className={`w-3 h-3 ${getGitStatusColor(status)}`} />
    }
    return null
  }

  const filterTree = useCallback((node: FileNode, path: string = ''): FileNode | null => {
    const currentPath = path ? `${path}/${node.name}` : node.name
    const matchesQuery = node.name.toLowerCase().includes(debouncedSearchQuery.toLowerCase())
    
    if (node.type === 'file') {
      return matchesQuery ? node : null
    }
    
    // For folders, check if any children match
    const filteredChildren = node.children
      ?.map(child => filterTree(child, currentPath))
      .filter((child): child is FileNode => child !== null) || []
    
    if (matchesQuery || filteredChildren.length > 0) {
      return {
        ...node,
        children: filteredChildren.length > 0 ? filteredChildren : node.children,
      }
    }
    
    return null
  }, [debouncedSearchQuery])

  // Memoize filtered tree to avoid recalculating on every render
  const filteredTree = useMemo(() => {
    return debouncedSearchQuery ? filterTree(sampleTree) : sampleTree
  }, [debouncedSearchQuery, filterTree])

  const renderNode = (node: FileNode, path: string = ''): React.ReactNode => {
    const currentPath = path ? `${path}/${node.name}` : node.name
    const isExpanded = expandedNodes.has(currentPath)
    const isFile = node.type === 'file'

    return (
      <div key={currentPath}>
        <div
          className="flex items-center gap-1 px-2 py-1 hover:bg-gray-700 rounded cursor-pointer group transition-colors"
          onClick={() => handleFileClick(currentPath, node)}
          onContextMenu={(e) => handleContextMenu(e, currentPath)}
          role="button"
          tabIndex={0}
          aria-label={`${node.type} ${node.name}`}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault()
              handleFileClick(currentPath, node)
            }
          }}
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
          
          <span className="text-sm text-gray-300 flex-1 truncate" title={node.name}>
            {node.name}
          </span>
          
          {node.isFavorite && (
            <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
          )}
          
          {getGitStatusIcon(node.gitStatus)}
          
          {/* Context menu trigger (visible on hover) */}
          <button
            className="opacity-0 group-hover:opacity-100 transition-opacity p-0.5 hover:bg-gray-600 rounded"
            onClick={(e) => {
              e.stopPropagation()
              handleContextMenu(e, currentPath)
            }}
            aria-label={`${node.name} context menu`}
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
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-800" role="complementary" aria-label="File Explorer">
        {loading.cmc || loading.hhni ? (
          <LoadingState message="Loading file tree..." />
        ) : (
          <>
      {/* Header */}
      <div className="h-10 bg-gray-900 border-b border-gray-700 flex items-center px-3 shrink-0">
        <FolderOpen className="w-4 h-4 mr-2 text-gray-400" />
        <span className="text-sm font-semibold text-gray-300">Explorer</span>
        <div className="ml-auto flex gap-1">
          <button
            onClick={() => setShowFavorites(!showFavorites)}
            className={`p-1 rounded transition-colors ${
              showFavorites ? 'text-yellow-400 bg-gray-700' : 'text-gray-400 hover:text-gray-300 hover:bg-gray-700'
            }`}
            aria-label="Toggle favorites"
            title="Show favorites only"
          >
            <Star className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="px-2 py-2 border-b border-gray-700 shrink-0">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-2 py-1.5 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-500"
            aria-label="Search files"
          />
        </div>
      </div>

      {/* File Tree */}
      <div className="flex-1 overflow-y-auto p-2">
        {filteredTree ? (
          <div role="tree" aria-label="File tree">
            {renderNode(filteredTree)}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm">
            <Search className="w-8 h-8 mb-2 opacity-50" />
            <p>No files found</p>
            <p className="text-xs mt-1">Try a different search query</p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="h-6 bg-gray-900 border-t border-gray-700 flex items-center px-3 text-xs text-gray-500 shrink-0">
        <span>Files</span>
      </div>

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
            role="menu"
            aria-label="File context menu"
          >
            <button
              className="w-full px-4 py-2 text-left text-sm text-gray-200 hover:bg-gray-600 flex items-center gap-2"
              onClick={() => handleCreateFile(contextMenu.path)}
              role="menuitem"
            >
              <Plus className="w-4 h-4" />
              New File
            </button>
            <button
              className="w-full px-4 py-2 text-left text-sm text-gray-200 hover:bg-gray-600 flex items-center gap-2"
              onClick={() => handleCreateFile(contextMenu.path)}
              role="menuitem"
            >
              <FolderOpen className="w-4 h-4" />
              New Folder
            </button>
            <div className="h-px bg-gray-600 my-1" />
            <button
              className="w-full px-4 py-2 text-left text-sm text-gray-200 hover:bg-gray-600 flex items-center gap-2"
              onClick={() => handleRename(contextMenu.path)}
              role="menuitem"
            >
              <Edit2 className="w-4 h-4" />
              Rename
            </button>
            <div className="h-px bg-gray-600 my-1" />
            <button
              className="w-full px-4 py-2 text-left text-sm text-red-400 hover:bg-gray-600 flex items-center gap-2"
              onClick={() => handleDelete(contextMenu.path)}
              role="menuitem"
            >
              <Trash2 className="w-4 h-4" />
              Delete
            </button>
          </div>
        </>
      )}
      </div>
    </ErrorBoundary>
  )
})

