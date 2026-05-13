// File Tree Panel - V2 Enhanced with Color Coding & Smart Filters
// CMC-backed file operations with HHNI hierarchical paths, VIF witnesses, and SEG contradictions

import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { 
  File, Folder, Search, ChevronRight, ChevronDown, Shield, Brain, AlertTriangle, Database,
  Code, FileText, Settings, Database as DatabaseIcon, Package, Image, FileCode,
  ChevronsDown, ChevronsUp, Eye, EyeOff, X
} from 'lucide-react'
import { useCMC, useVIF, useSEG, useHHNI } from '../hooks/useAIMOS'
import type { CMCAtom, VIFWitness, SEGContradiction, HHNISearchResult } from '../hooks/useAIMOS'

interface FileNode {
  name: string
  path: string
  type: 'file' | 'folder'
  children?: FileNode[]
  
  // File type detection
  fileType?: 'code' | 'doc' | 'config' | 'data' | 'build' | 'image' | 'other'
  fileExtension?: string
  folderType?: 'src' | 'docs' | 'config' | 'data' | 'test' | 'build' | 'other'
  
  // Size and metrics
  size?: number  // Size in bytes
  lines?: number  // Line count
  words?: number  // Word count
  
  // AIM-OS Integration
  cmc_atoms?: CMCAtom[]
  vif_witnesses?: VIFWitness[]
  seg_contradictions?: SEGContradiction[]
  hhni_path?: string[]  // Hierarchical path (System→Subsystem→Component→File)
  
  // Aggregated metrics
  confidence?: number
  confidence_band?: 'A' | 'B' | 'C'
  atom_count?: number
  contradiction_count?: number
}

type FilterType = 'all' | 'code' | 'docs' | 'config' | 'data' | 'build'

// File type detection utilities
const getFileType = (filename: string): 'code' | 'doc' | 'config' | 'data' | 'build' | 'image' | 'other' => {
  const ext = filename.split('.').pop()?.toLowerCase() || ''
  
  // Code files
  if (['ts', 'tsx', 'js', 'jsx', 'py', 'java', 'cpp', 'c', 'cs', 'go', 'rs', 'rb', 'php', 'swift', 'kt'].includes(ext)) {
    return 'code'
  }
  
  // Documentation
  if (['md', 'txt', 'rst', 'docx', 'pdf'].includes(ext)) {
    return 'doc'
  }
  
  // Config files
  if (['json', 'yaml', 'yml', 'toml', 'xml', 'ini', 'cfg', 'conf', 'properties'].includes(ext)) {
    return 'config'
  }
  
  // Data files
  if (['csv', 'db', 'sqlite', 'sql', 'xlsx', 'xls'].includes(ext)) {
    return 'data'
  }
  
  // Build files
  if (ext === 'lock' || filename.includes('lock')) {
    return 'build'
  }
  
  // Images
  if (['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'ico'].includes(ext)) {
    return 'image'
  }
  
  return 'other'
}

const getFolderType = (folderName: string): 'src' | 'docs' | 'config' | 'data' | 'test' | 'build' | 'other' => {
  const lower = folderName.toLowerCase()
  
  if (['src', 'source', 'lib', 'libs', 'components', 'hooks', 'utils', 'services'].includes(lower)) {
    return 'src'
  }
  if (['docs', 'documentation', 'doc', 'readme'].includes(lower)) {
    return 'docs'
  }
  if (['config', 'configs', 'configuration', '.vscode', '.idea', 'settings'].includes(lower)) {
    return 'config'
  }
  if (['data', 'datasets', 'db', 'database'].includes(lower)) {
    return 'data'
  }
  if (['test', 'tests', 'spec', 'specs', '__tests__', '__pycache__'].includes(lower)) {
    return 'test'
  }
  if (['build', 'dist', 'out', 'target', 'bin'].includes(lower)) {
    return 'build'
  }
  
  return 'other'
}

const getFileTypeColor = (fileType: string): string => {
  switch (fileType) {
    case 'code': return 'text-blue-400'
    case 'doc': return 'text-green-400'
    case 'config': return 'text-yellow-400'
    case 'data': return 'text-purple-400'
    case 'build': return 'text-orange-400'
    case 'image': return 'text-pink-400'
    default: return 'text-gray-400'
  }
}

const getFolderTypeColor = (folderType: string): string => {
  switch (folderType) {
    case 'src': return 'text-blue-400'
    case 'docs': return 'text-green-400'
    case 'config': return 'text-yellow-400'
    case 'data': return 'text-purple-400'
    case 'test': return 'text-cyan-400'
    case 'build': return 'text-orange-400'
    default: return 'text-gray-400'
  }
}

const getFileTypeIcon = (fileType: string, extension: string): React.ComponentType<{ className?: string }> => {
  switch (fileType) {
    case 'code':
      if (['ts', 'tsx', 'js', 'jsx'].includes(extension)) return FileCode
      return Code
    case 'doc': return FileText
    case 'config': return Settings
    case 'data': return DatabaseIcon
    case 'build': return Package
    case 'image': return Image
    default: return File
  }
}

const getFolderTypeIcon = (folderType: string): React.ComponentType<{ className?: string }> => {
  switch (folderType) {
    case 'src': return Code
    case 'docs': return FileText
    case 'config': return Settings
    case 'data': return DatabaseIcon
    case 'test': return Shield
    case 'build': return Package
    default: return Folder
  }
}

// Format file size
const formatSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(i === 0 ? 0 : 1)} ${sizes[i]}`
}

// Format number with commas
const formatNumber = (num: number): string => {
  return num.toLocaleString()
}

// Count files recursively
const countFiles = (node: FileNode): number => {
  if (node.type === 'file') return 1
  if (!node.children) return 0
  return node.children.reduce((sum, child) => sum + countFiles(child), 0)
}

// Calculate folder size recursively
const calculateFolderSize = (node: FileNode): number => {
  if (node.type === 'file') {
    return node.size || 0
  }
  if (!node.children) return 0
  return node.children.reduce((sum, child) => sum + calculateFolderSize(child), 0)
}

// Calculate folder lines recursively
const calculateFolderLines = (node: FileNode): number => {
  if (node.type === 'file') {
    return node.lines || 0
  }
  if (!node.children) return 0
  return node.children.reduce((sum, child) => sum + calculateFolderLines(child), 0)
}

// Calculate folder words recursively
const calculateFolderWords = (node: FileNode): number => {
  if (node.type === 'file') {
    return node.words || 0
  }
  if (!node.children) return 0
  return node.children.reduce((sum, child) => sum + calculateFolderWords(child), 0)
}

const mockFileTree: FileNode[] = [
  {
    name: 'src',
    path: 'src',
    type: 'folder',
    folderType: 'src',
    hhni_path: ['IDE', 'Source'],
    children: [
      {
        name: 'components',
        path: 'src/components',
        type: 'folder',
        folderType: 'src',
        hhni_path: ['IDE', 'Source', 'Components'],
        children: [
          {
            name: 'IDELayout.tsx',
            path: 'src/components/IDELayout.tsx',
            type: 'file',
            fileType: 'code',
            fileExtension: 'tsx',
            size: 45280,
            lines: 985,
            words: 12450,
            hhni_path: ['IDE', 'Source', 'Components', 'IDELayout'],
            confidence: 0.92,
            confidence_band: 'A',
            atom_count: 5,
            contradiction_count: 0
          },
          {
            name: 'FileTree.tsx',
            path: 'src/components/FileTree.tsx',
            type: 'file',
            fileType: 'code',
            fileExtension: 'tsx',
            size: 32150,
            lines: 687,
            words: 8230,
            hhni_path: ['IDE', 'Source', 'Components', 'FileTree'],
            confidence: 0.88,
            confidence_band: 'B',
            atom_count: 3,
            contradiction_count: 1
          },
          {
            name: 'MemoryBrowser.tsx',
            path: 'src/components/MemoryBrowser.tsx',
            type: 'file',
            fileType: 'code',
            fileExtension: 'tsx',
            size: 28900,
            lines: 612,
            words: 7450,
            hhni_path: ['IDE', 'Source', 'Components', 'MemoryBrowser'],
            confidence: 0.95,
            confidence_band: 'A',
            atom_count: 8,
            contradiction_count: 0
          }
        ]
      },
      {
        name: 'hooks',
        path: 'src/hooks',
        type: 'folder',
        folderType: 'src',
        hhni_path: ['IDE', 'Source', 'Hooks'],
        children: [
          {
            name: 'useAIMOS.ts',
            path: 'src/hooks/useAIMOS.ts',
            type: 'file',
            fileType: 'code',
            fileExtension: 'ts',
            size: 15680,
            lines: 342,
            words: 4120,
            hhni_path: ['IDE', 'Source', 'Hooks', 'useAIMOS'],
            confidence: 0.90,
            confidence_band: 'A',
            atom_count: 12,
            contradiction_count: 0
          }
        ]
      },
      {
        name: 'panels',
        path: 'src/panels',
        type: 'folder',
        folderType: 'src',
        hhni_path: ['IDE', 'Source', 'Panels'],
        children: [
          {
            name: 'ContextWeb.tsx',
            path: 'src/panels/ContextWeb.tsx',
            type: 'file',
            fileType: 'code',
            fileExtension: 'tsx',
            size: 42100,
            lines: 892,
            words: 10850,
            hhni_path: ['IDE', 'Source', 'Panels', 'ContextWeb'],
            confidence: 0.87,
            confidence_band: 'B',
            atom_count: 6,
            contradiction_count: 0
          },
          {
            name: 'TimelineView.tsx',
            path: 'src/panels/TimelineView.tsx',
            type: 'file',
            fileType: 'code',
            fileExtension: 'tsx',
            size: 38900,
            lines: 587,
            words: 7120,
            hhni_path: ['IDE', 'Source', 'Panels', 'TimelineView'],
            confidence: 0.91,
            confidence_band: 'A',
            atom_count: 4,
            contradiction_count: 0
          }
        ]
      }
    ]
  },
  {
    name: 'docs',
    path: 'docs',
    type: 'folder',
    folderType: 'docs',
    children: [
      {
        name: 'README.md',
        path: 'docs/README.md',
        type: 'file',
        fileType: 'doc',
        fileExtension: 'md',
        size: 8200,
        lines: 145,
        words: 890
      },
      {
        name: 'API.md',
        path: 'docs/API.md',
        type: 'file',
        fileType: 'doc',
        fileExtension: 'md',
        size: 15200,
        lines: 267,
        words: 1650
      }
    ]
  },
  {
    name: 'data',
    path: 'data',
    type: 'folder',
    folderType: 'data',
    children: [
      {
        name: 'dataset.csv',
        path: 'data/dataset.csv',
        type: 'file',
        fileType: 'data',
        fileExtension: 'csv',
        size: 2450000,
        lines: 12500,
        words: 0
      },
      {
        name: 'cache.db',
        path: 'data/cache.db',
        type: 'file',
        fileType: 'data',
        fileExtension: 'db',
        size: 1840000,
        lines: 0,
        words: 0
      }
    ]
  },
  {
    name: 'package.json',
    path: 'package.json',
    type: 'file',
    fileType: 'config',
    fileExtension: 'json',
    size: 3200,
    lines: 45,
    words: 120,
    hhni_path: ['IDE', 'Configuration'],
    confidence: 0.95,
    confidence_band: 'A',
    atom_count: 2,
    contradiction_count: 0
  },
  {
    name: 'tsconfig.json',
    path: 'tsconfig.json',
    type: 'file',
    fileType: 'config',
    fileExtension: 'json',
    size: 1800,
    lines: 28,
    words: 85
  },
  {
    name: 'package-lock.json',
    path: 'package-lock.json',
    type: 'file',
    fileType: 'build',
    fileExtension: 'json',
    size: 2450000,
    lines: 0,
    words: 0
  }
]

export const FileTree: React.FC = () => {
  const { retrieveAtoms } = useCMC()
  const { getWitnesses } = useVIF()
  const { contradictions } = useSEG()
  const { search } = useHHNI()
  const [files, setFiles] = useState<FileNode[]>(mockFileTree)
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(['src', 'src/components', 'src/hooks', 'src/panels']))
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [searchResults, setSearchResults] = useState<HHNISearchResult[]>([])
  const [loading, setLoading] = useState(false) // Only for search, not for initial load
  const [error, setError] = useState<string | null>(null)
  const [enhancing, setEnhancing] = useState(false) // Track enhancement separately
  const [filter, setFilter] = useState<FilterType>('all')
  const [showHidden, setShowHidden] = useState(false)
  
  // Enhance files with file type detection
  useEffect(() => {
    const enhanceWithTypes = (nodes: FileNode[]): FileNode[] => {
      return nodes.map(node => {
        if (node.type === 'file') {
          const fileType = node.fileType || getFileType(node.name)
          const extension = node.fileExtension || node.name.split('.').pop()?.toLowerCase() || ''
          return {
            ...node,
            fileType,
            fileExtension: extension
          }
        } else if (node.type === 'folder') {
          const folderType = node.folderType || getFolderType(node.name)
          const enhancedChildren = node.children ? enhanceWithTypes(node.children) : undefined
          return {
            ...node,
            folderType,
            children: enhancedChildren
          }
        }
        return node
      })
    }
    
    setFiles(enhanceWithTypes(mockFileTree))
  }, [])
  
  // Enhance files with AIM-OS data (background enhancement, don't block UI)
  useEffect(() => {
    const enhanceFiles = async () => {
      try {
        // Don't set loading=true - show mock data immediately
        // Only enhance in background
        setEnhancing(true)
        setError(null)
        
        // Add timeout to prevent hanging
        const timeoutId = setTimeout(() => {
          console.warn('FileTree enhancement timed out, using mock data')
          setEnhancing(false)
        }, 5000)
        
        const enhanced = await Promise.all(
          files.map(async (file) => {
            if (file.type === 'file') {
              const atoms = await retrieveAtoms(`file:${file.path}`, 10)
              const witnesses = await getWitnesses(file.path)
              const fileContradictions = contradictions.filter(
                c => c.entity1_id.includes(file.path) || c.entity2_id.includes(file.path)
              )
              
              let aggregatedConfidence = 0.75
              let confidenceBand: 'A' | 'B' | 'C' = 'B'
              if (witnesses.length > 0) {
                const avgConfidence = witnesses.reduce((sum, w) => sum + w.confidence_score, 0) / witnesses.length
                aggregatedConfidence = avgConfidence
                
                if (avgConfidence >= 0.90) {
                  confidenceBand = 'A'
                } else if (avgConfidence >= 0.70) {
                  confidenceBand = 'B'
                } else {
                  confidenceBand = 'C'
                }
              }
              
              return {
                ...file,
                cmc_atoms: atoms,
                vif_witnesses: witnesses,
                seg_contradictions: fileContradictions,
                confidence: aggregatedConfidence,
                confidence_band: confidenceBand,
                atom_count: atoms.length,
                contradiction_count: fileContradictions.length
              }
            }
            
            if (file.children) {
              const enhancedChildren = await Promise.all(
                file.children.map(async (child) => {
                  if (child.type === 'file') {
                    const atoms = await retrieveAtoms(`file:${child.path}`, 10)
                    const witnesses = await getWitnesses(child.path)
                    const fileContradictions = contradictions.filter(
                      c => c.entity1_id.includes(child.path) || c.entity2_id.includes(child.path)
                    )
                    
                    let aggregatedConfidence = 0.75
                    let confidenceBand: 'A' | 'B' | 'C' = 'B'
                    if (witnesses.length > 0) {
                      const avgConfidence = witnesses.reduce((sum, w) => sum + w.confidence_score, 0) / witnesses.length
                      aggregatedConfidence = avgConfidence
                      
                      if (avgConfidence >= 0.90) {
                        confidenceBand = 'A'
                      } else if (avgConfidence >= 0.70) {
                        confidenceBand = 'B'
                      } else {
                        confidenceBand = 'C'
                      }
                    }
                    
                    return {
                      ...child,
                      cmc_atoms: atoms,
                      vif_witnesses: witnesses,
                      seg_contradictions: fileContradictions,
                      confidence: aggregatedConfidence,
                      confidence_band: confidenceBand,
                      atom_count: atoms.length,
                      contradiction_count: fileContradictions.length
                    }
                  }
                  return child
                })
              )
              return { ...file, children: enhancedChildren }
            }
            
            return file
          })
        )
        clearTimeout(timeoutId)
        setFiles(enhanced)
        setEnhancing(false)
      } catch (err) {
        // Don't show error - just keep using mock data
        // Enhancement is optional, mock data is the fallback
        console.warn('FileTree enhancement failed, using mock data:', err)
        setEnhancing(false)
        // Keep existing files (mock data) - don't clear them
      }
    }
    
    // Only enhance if we have real data available, otherwise just use mock
    enhanceFiles()
  }, [retrieveAtoms, getWitnesses, contradictions])
  
  // HHNI semantic search
  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim()) {
      setSearchResults([])
      return
    }
    
    try {
      setLoading(true)
      setError(null)
      const results = await search(searchQuery, 20)
      setSearchResults(results)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setLoading(false)
    }
  }, [searchQuery, search])
  
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      handleSearch()
    }, 300)
    return () => clearTimeout(timeoutId)
  }, [searchQuery, handleSearch])
  
  const toggleFolder = (path: string) => {
    setExpandedFolders(prev => {
      const next = new Set(prev)
      if (next.has(path)) {
        next.delete(path)
      } else {
        next.add(path)
      }
      return next
    })
  }
  
  const expandAll = () => {
    const allPaths = new Set<string>()
    const collectPaths = (nodes: FileNode[]) => {
      nodes.forEach(node => {
        if (node.type === 'folder') {
          allPaths.add(node.path)
          if (node.children) {
            collectPaths(node.children)
          }
        }
      })
    }
    collectPaths(files)
    setExpandedFolders(allPaths)
  }
  
  const collapseAll = () => {
    setExpandedFolders(new Set())
  }
  
  const getConfidenceBandColor = (band?: 'A' | 'B' | 'C') => {
    switch (band) {
      case 'A': return 'text-green-400 bg-green-900/30 border-green-700'
      case 'B': return 'text-yellow-400 bg-yellow-900/30 border-yellow-700'
      case 'C': return 'text-red-400 bg-red-900/30 border-red-700'
      default: return 'text-gray-400 bg-gray-900/30 border-gray-700'
    }
  }
  
  // Filter files based on filter type
  const shouldShowNode = (node: FileNode): boolean => {
    if (filter === 'all') return true
    
    if (node.type === 'file') {
      switch (filter) {
        case 'code': return node.fileType === 'code'
        case 'docs': return node.fileType === 'doc'
        case 'config': return node.fileType === 'config'
        case 'data': return node.fileType === 'data'
        case 'build': return node.fileType === 'build'
        default: return true
      }
    } else if (node.type === 'folder') {
      switch (filter) {
        case 'code': return node.folderType === 'src' || node.folderType === 'test'
        case 'docs': return node.folderType === 'docs'
        case 'config': return node.folderType === 'config'
        case 'data': return node.folderType === 'data'
        case 'build': return node.folderType === 'build'
        default: return true
      }
    }
    
    return true
  }
  
  // Recursively filter tree
  const filterTree = (nodes: FileNode[]): FileNode[] => {
    return nodes
      .filter(node => {
        if (!shouldShowNode(node)) return false
        if (node.type === 'folder' && node.children) {
          const filteredChildren = filterTree(node.children)
          return filteredChildren.length > 0
        }
        return true
      })
      .map(node => {
        if (node.type === 'folder' && node.children) {
          return {
            ...node,
            children: filterTree(node.children)
          }
        }
        return node
      })
  }
  
  const renderFileNode = (node: FileNode, level: number = 0): React.ReactNode => {
    const isExpanded = expandedFolders.has(node.path)
    const indent = level * 16
    const isSelected = selectedFile === node.path
    
    if (node.type === 'folder') {
      const FolderIcon = getFolderTypeIcon(node.folderType || 'other')
      const folderColor = getFolderTypeColor(node.folderType || 'other')
      const fileCount = countFiles(node)
      const folderSize = calculateFolderSize(node)
      const folderLines = calculateFolderLines(node)
      const folderWords = calculateFolderWords(node)
      
      return (
        <div key={node.path}>
          <div
            className="flex items-center gap-2 px-2 py-1 hover:bg-gray-700 cursor-pointer text-sm"
            style={{ paddingLeft: `${indent + 8}px` }}
            onClick={() => toggleFolder(node.path)}
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4 text-gray-400" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-400" />
            )}
            <FolderIcon className={`w-4 h-4 ${folderColor}`} />
            <span className={`flex-1 ${folderColor}`}>{node.name}</span>
            
            {/* Folder Metrics */}
            <div className="flex items-center gap-2 text-xs text-gray-500 flex-shrink-0">
              {folderSize > 0 && (
                <span title={`Total size: ${formatSize(folderSize)}`}>
                  {formatSize(folderSize)}
                </span>
              )}
              {folderLines > 0 && (
                <span title={`Total lines: ${formatNumber(folderLines)}`}>
                  {formatNumber(folderLines)} lines
                </span>
              )}
              {folderWords > 0 && (
                <span title={`Total words: ${formatNumber(folderWords)}`}>
                  {formatNumber(folderWords)} words
                </span>
              )}
              {fileCount > 0 && (
                <span title={`${fileCount} files`}>
                  {fileCount} files
                </span>
              )}
            </div>
            
            {/* HHNI Path Indicator */}
            {node.hhni_path && (
              <span className="text-xs text-gray-500" title={`HHNI Path: ${node.hhni_path.join(' → ')}`}>
                {node.hhni_path.length} levels
              </span>
            )}
          </div>
          {isExpanded && node.children && (
            <div>
              {node.children.map(child => renderFileNode(child, level + 1))}
            </div>
          )}
        </div>
      )
    }
    
    // File node with color coding and icons
    const FileIcon = getFileTypeIcon(node.fileType || 'other', node.fileExtension || '')
    const fileColor = getFileTypeColor(node.fileType || 'other')
    const confidenceBandColor = getConfidenceBandColor(node.confidence_band)
    const hasContradictions = node.contradiction_count && node.contradiction_count > 0
    
    return (
      <div
        key={node.path}
        className={`flex items-center gap-2 px-2 py-1 hover:bg-gray-700 cursor-pointer text-sm group ${
          isSelected ? 'bg-blue-900/30 border-l-2 border-blue-500' : ''
        }`}
        style={{ paddingLeft: `${indent + 8}px` }}
        onClick={() => setSelectedFile(node.path)}
      >
        <FileIcon className={`w-4 h-4 ${fileColor}`} />
        <span className={`flex-1 truncate ${fileColor}`}>{node.name}</span>
        
        {/* File Metrics */}
        <div className="flex items-center gap-2 text-xs text-gray-500 flex-shrink-0">
          {node.size !== undefined && node.size > 0 && (
            <span title={`Size: ${formatSize(node.size)}`}>
              {formatSize(node.size)}
            </span>
          )}
          {node.lines !== undefined && node.lines > 0 && (
            <span title={`Lines: ${formatNumber(node.lines)}`}>
              {formatNumber(node.lines)} lines
            </span>
          )}
          {node.words !== undefined && node.words > 0 && (
            <span title={`Words: ${formatNumber(node.words)}`}>
              {formatNumber(node.words)} words
            </span>
          )}
        </div>
        
        {/* AIM-OS Indicators */}
        <div className="flex items-center gap-1 flex-shrink-0">
          {/* Confidence Band */}
          {node.confidence_band && (
            <span
              className={`px-1.5 py-0.5 rounded text-xs border ${confidenceBandColor}`}
              title={`Confidence Band ${node.confidence_band}: ${node.confidence ? (node.confidence * 100).toFixed(0) + '%' : 'N/A'}`}
            >
              {node.confidence_band}
            </span>
          )}
          
          {/* CMC Atom Count */}
          {node.atom_count !== undefined && node.atom_count > 0 && (
            <span
              className="px-1.5 py-0.5 rounded text-xs bg-blue-900/30 text-blue-300 border border-blue-700 flex items-center gap-1"
              title={`${node.atom_count} CMC atoms`}
            >
              <Database className="w-3 h-3" />
              {node.atom_count}
            </span>
          )}
          
          {/* VIF Witnesses */}
          {node.vif_witnesses && node.vif_witnesses.length > 0 && (
            <span
              className="px-1.5 py-0.5 rounded text-xs bg-green-900/30 text-green-300 border border-green-700 flex items-center gap-1"
              title={`${node.vif_witnesses.length} VIF witnesses`}
            >
              <Shield className="w-3 h-3" />
              {node.vif_witnesses.length}
            </span>
          )}
          
          {/* SEG Contradictions */}
          {hasContradictions && (
            <span
              className="px-1.5 py-0.5 rounded text-xs bg-red-900/30 text-red-300 border border-red-700 flex items-center gap-1"
              title={`${node.contradiction_count} SEG contradictions`}
            >
              <Brain className="w-3 h-3" />
              <AlertTriangle className="w-3 h-3" />
              {node.contradiction_count}
            </span>
          )}
          
          {/* HHNI Path */}
          {node.hhni_path && (
            <span
              className="px-1.5 py-0.5 rounded text-xs bg-purple-900/30 text-purple-300 border border-purple-700"
              title={`HHNI Path: ${node.hhni_path.join(' → ')}`}
            >
              {node.hhni_path.length}
            </span>
          )}
        </div>
      </div>
    )
  }
  
  // Filter files by search results and filter type
  const filteredFiles = useMemo(() => {
    let result = files
    
    // Apply filter
    if (filter !== 'all') {
      result = filterTree(files)
    }
    
    // Apply search
    if (searchQuery.trim() && searchResults.length > 0) {
      result = result.filter(file => {
        return searchResults.some(result => 
          result.node.content.toLowerCase().includes(file.path.toLowerCase()) ||
          file.path.toLowerCase().includes(searchQuery.toLowerCase())
        )
      })
    }
    
    return result
  }, [files, filter, searchQuery, searchResults])
  
  // Calculate AIM-OS metrics
  const fileNodes = filteredFiles.filter(f => f.type === 'file')
  const overallConfidence = fileNodes.length > 0 && fileNodes[0].confidence !== undefined
    ? fileNodes.reduce((sum, file) => sum + (file.confidence || 0), 0) / fileNodes.length
    : undefined
  
  const confidenceBand = overallConfidence 
    ? (overallConfidence >= 0.90 ? 'A' : overallConfidence >= 0.70 ? 'B' : 'C')
    : undefined
  
  const totalAtomCount = fileNodes.reduce((sum, file) => sum + (file.atom_count || 0), 0)
  const totalContradictionCount = fileNodes.reduce((sum, file) => sum + (file.contradiction_count || 0), 0)
  
  const filterButtons: { id: FilterType; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
    { id: 'all', label: 'All', icon: File },
    { id: 'code', label: 'Code', icon: Code },
    { id: 'docs', label: 'Docs', icon: FileText },
    { id: 'config', label: 'Config', icon: Settings },
    { id: 'data', label: 'Data', icon: DatabaseIcon },
    { id: 'build', label: 'Build', icon: Package },
  ]
  
  return (
    <div className="h-full flex flex-col bg-gray-950">
      {/* Search Bar & Controls - Inline */}
      <div className="p-2 border-b border-gray-700 flex items-center gap-2">
        {/* Search Bar */}
        <div className="relative flex-1">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search files..."
            className="w-full pl-8 pr-2 py-1.5 bg-gray-800 border border-gray-700 rounded text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-300"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
        
        {/* Expand/Collapse/Hidden Icon Buttons */}
        <button
          onClick={expandAll}
          className="w-8 h-8 flex items-center justify-center rounded text-gray-400 hover:text-gray-300 hover:bg-gray-800 transition-colors"
          title="Expand All"
        >
          <ChevronsDown className="w-4 h-4" />
        </button>
        <button
          onClick={collapseAll}
          className="w-8 h-8 flex items-center justify-center rounded text-gray-400 hover:text-gray-300 hover:bg-gray-800 transition-colors"
          title="Collapse All"
        >
          <ChevronsUp className="w-4 h-4" />
        </button>
        <button
          onClick={() => setShowHidden(!showHidden)}
          className={`w-8 h-8 flex items-center justify-center rounded transition-colors ${
            showHidden 
              ? 'text-gray-300 bg-gray-800' 
              : 'text-gray-400 hover:text-gray-300 hover:bg-gray-800'
          }`}
          title={showHidden ? "Hide Hidden Files" : "Show Hidden Files"}
        >
          {showHidden ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
        </button>
      </div>
      
      {/* Filter Buttons */}
      <div className="px-2 py-1 border-b border-gray-700 flex items-center gap-1 flex-wrap">
        {filterButtons.map(btn => {
          const Icon = btn.icon
          const isActive = filter === btn.id
          return (
            <button
              key={btn.id}
              onClick={() => setFilter(btn.id)}
              className={`flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
              title={btn.label}
            >
              <Icon className="w-3 h-3" />
              <span>{btn.label}</span>
            </button>
          )
        })}
      </div>
      
      {/* File Tree */}
      <div className="flex-1 overflow-auto p-2">
        {/* Show mock data immediately - don't wait for enhancement */}
        {loading && searchQuery && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-950/80 z-10">
            <div className="text-gray-400 text-sm">Searching...</div>
          </div>
        )}
        {error && searchQuery && (
          <div className="mb-2 p-2 bg-red-900/20 border border-red-700 rounded text-red-400 text-sm">
            {error}
          </div>
        )}
        {!loading && filteredFiles.length === 0 && (
          <div className="h-full flex items-center justify-center">
            <div className="text-gray-500 text-sm">
              {searchQuery || filter !== 'all' ? "No files found matching your filter" : "No files available"}
            </div>
          </div>
        )}
        {filteredFiles.length > 0 && (
          <>
            {filteredFiles.map(node => renderFileNode(node))}
            {enhancing && (
              <div className="mt-2 text-xs text-gray-500 text-center">
                Enhancing with AIM-OS data...
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
