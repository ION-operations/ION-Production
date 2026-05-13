/**
 * Outline Panel Component
 * 
 * Phase 1.3: Basic Panel Components
 * 
 * Displays file structure and symbol navigation for the active file.
 * Features:
 * - Symbol tree (classes, functions, variables, etc.)
 * - Quick navigation to symbols
 * - Symbol search/filter
 * - Keyboard shortcuts
 * - AIM-OS integration (HHNI for symbol navigation, CMC for outline cache)
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react'
import { ChevronRight, ChevronDown, Search, Code, FileText, Zap, Circle, Square, Triangle, Layers } from 'lucide-react'
import { useEditorStore } from '../../store/editorStore'
import { useAIMOS } from '../../hooks/useAIMOS'
import { useDebounce } from '../../hooks/useDebounce'
import { ErrorBoundary } from '../ErrorBoundary'
import { LoadingState } from '../LoadingState'

export interface SymbolNode {
  id: string
  name: string
  kind: 'file' | 'class' | 'function' | 'variable' | 'interface' | 'type' | 'enum' | 'namespace' | 'method' | 'property'
  line: number
  column: number
  children?: SymbolNode[]
  icon?: React.ReactNode
}

interface OutlinePanelProps {
  onSymbolClick?: (symbol: SymbolNode) => void
}

// Mock symbol data for prototype
const generateMockSymbols = (fileName: string): SymbolNode[] => {
  if (fileName.endsWith('.tsx') || fileName.endsWith('.ts')) {
    return [
      {
        id: '1',
        name: 'RevIDELayout',
        kind: 'class',
        line: 1,
        column: 1,
        icon: <Square className="w-3 h-3 text-blue-400" />,
        children: [
          {
            id: '1-1',
            name: 'renderLeftPanel',
            kind: 'function',
            line: 110,
            column: 1,
            icon: <Zap className="w-3 h-3 text-green-400" />,
          },
          {
            id: '1-2',
            name: 'renderRightPanel',
            kind: 'function',
            line: 200,
            column: 1,
            icon: <Zap className="w-3 h-3 text-green-400" />,
          },
          {
            id: '1-3',
            name: 'renderMainContent',
            kind: 'function',
            line: 300,
            column: 1,
            icon: <Zap className="w-3 h-3 text-green-400" />,
          },
        ],
      },
      {
        id: '2',
        name: 'PanelDefinition',
        kind: 'interface',
        line: 50,
        column: 1,
        icon: <Circle className="w-3 h-3 text-purple-400" />,
      },
      {
        id: '3',
        name: 'usePanelManagerStore',
        kind: 'function',
        line: 400,
        column: 1,
        icon: <Zap className="w-3 h-3 text-green-400" />,
      },
    ]
  }
  
  return [
    {
      id: '1',
      name: 'main',
      kind: 'function',
      line: 1,
      column: 1,
      icon: <Zap className="w-3 h-3 text-green-400" />,
    },
  ]
}

const getSymbolIcon = (kind: SymbolNode['kind']) => {
  switch (kind) {
    case 'class':
      return <Square className="w-3 h-3 text-blue-400" />
    case 'function':
    case 'method':
      return <Zap className="w-3 h-3 text-green-400" />
    case 'interface':
    case 'type':
      return <Circle className="w-3 h-3 text-purple-400" />
    case 'variable':
    case 'property':
      return <Triangle className="w-3 h-3 text-yellow-400" />
    case 'enum':
      return <Code className="w-3 h-3 text-orange-400" />
    case 'namespace':
      return <FileText className="w-3 h-3 text-gray-400" />
    default:
      return <FileText className="w-3 h-3 text-gray-400" />
  }
}

export const OutlinePanel: React.FC<OutlinePanelProps> = React.memo(({ onSymbolClick }) => {
  const { activeTabId, tabs } = useEditorStore()
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set())
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedSymbolId, setSelectedSymbolId] = useState<string | null>(null)

  // Debounce search query for performance
  const debouncedSearchQuery = useDebounce(searchQuery, 300)

  // AIM-OS integration
  const { hhni, isConnected, useMockData, loading } = useAIMOS()

  const activeTab = tabs.find(t => t.id === activeTabId)

  // Generate mock symbols based on active file
  const symbols = useMemo(() => {
    if (!activeTab) return []
    return generateMockSymbols(activeTab.fileName)
  }, [activeTab])

  // Filter symbols based on debounced search query
  const filteredSymbols = useMemo(() => {
    if (!debouncedSearchQuery) return symbols
    
    const query = debouncedSearchQuery.toLowerCase()
    const filterSymbols = (nodes: SymbolNode[]): SymbolNode[] => {
      return nodes
        .map(node => {
          const matches = node.name.toLowerCase().includes(query)
          const filteredChildren = node.children ? filterSymbols(node.children) : []
          
          if (matches || filteredChildren.length > 0) {
            return {
              ...node,
              children: filteredChildren.length > 0 ? filteredChildren : node.children,
            }
          }
          return null
        })
        .filter((node): node is SymbolNode => node !== null)
    }
    
    return filterSymbols(symbols)
  }, [symbols, debouncedSearchQuery])

  const toggleNode = useCallback((nodeId: string) => {
    setExpandedNodes(prev => {
      const newExpanded = new Set(prev)
      if (newExpanded.has(nodeId)) {
        newExpanded.delete(nodeId)
      } else {
        newExpanded.add(nodeId)
      }
      return newExpanded
    })
  }, [])

  const handleSymbolClick = useCallback((symbol: SymbolNode) => {
    setSelectedSymbolId(symbol.id)
    if (onSymbolClick) {
      onSymbolClick(symbol)
    }
    // TODO: Navigate to symbol in editor (Monaco editor API)
  }, [onSymbolClick])

  const renderSymbol = (symbol: SymbolNode, depth: number = 0): React.ReactNode => {
    const hasChildren = symbol.children && symbol.children.length > 0
    const isExpanded = expandedNodes.has(symbol.id)
    const isSelected = selectedSymbolId === symbol.id

    return (
      <div key={symbol.id}>
        <div
          className={`flex items-center gap-1 px-2 py-1 hover:bg-gray-700 rounded cursor-pointer transition-colors ${
            isSelected ? 'bg-gray-700' : ''
          }`}
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
          onClick={() => {
            if (hasChildren) {
              toggleNode(symbol.id)
            }
            handleSymbolClick(symbol)
          }}
          role="button"
          tabIndex={0}
          aria-label={`${symbol.kind} ${symbol.name} at line ${symbol.line}`}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault()
              if (hasChildren) {
                toggleNode(symbol.id)
              }
              handleSymbolClick(symbol)
            }
          }}
        >
          {hasChildren && (
            <div className="w-4 h-4 flex items-center justify-center">
              {isExpanded ? (
                <ChevronDown className="w-3 h-3 text-gray-400" />
              ) : (
                <ChevronRight className="w-3 h-3 text-gray-400" />
              )}
            </div>
          )}
          {!hasChildren && <div className="w-4 h-4" />}
          
          {symbol.icon || getSymbolIcon(symbol.kind)}
          
          <span className="text-sm text-gray-300 flex-1 truncate" title={symbol.name}>
            {symbol.name}
          </span>
          
          <span className="text-xs text-gray-500 ml-2">
            {symbol.line}
          </span>
        </div>
        
        {hasChildren && isExpanded && symbol.children && (
          <div>
            {symbol.children.map(child => renderSymbol(child, depth + 1))}
          </div>
        )}
      </div>
    )
  }

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-800" role="complementary" aria-label="Outline Panel">
        {loading.hhni ? (
          <LoadingState message="Loading outline..." />
        ) : (
          <>
      {/* Header */}
      <div className="h-10 bg-gray-900 border-b border-gray-700 flex items-center px-3 shrink-0">
        <Layers className="w-4 h-4 mr-2 text-gray-400" />
        <span className="text-sm font-semibold text-gray-300">Outline</span>
        {activeTab && (
          <span className="ml-auto text-xs text-gray-500 truncate max-w-[150px]" title={activeTab.fileName}>
            {activeTab.fileName.split('/').pop()}
          </span>
        )}
      </div>

      {/* Search */}
      <div className="px-2 py-2 border-b border-gray-700 shrink-0">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search symbols..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-2 py-1.5 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-500"
            aria-label="Search symbols"
          />
        </div>
      </div>

      {/* Symbol Tree */}
      <div className="flex-1 overflow-y-auto p-2">
        {!activeTab ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm">
            <FileText className="w-8 h-8 mb-2 opacity-50" />
            <p>No file open</p>
            <p className="text-xs mt-1">Open a file to see its outline</p>
          </div>
        ) : filteredSymbols.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm">
            <Search className="w-8 h-8 mb-2 opacity-50" />
            <p>No symbols found</p>
            {searchQuery && (
              <p className="text-xs mt-1">Try a different search query</p>
            )}
          </div>
        ) : (
          <div role="tree" aria-label="File outline">
            {filteredSymbols.map(symbol => renderSymbol(symbol))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="h-6 bg-gray-900 border-t border-gray-700 flex items-center px-3 text-xs text-gray-500 shrink-0">
        {activeTab && filteredSymbols.length > 0 && (
          <span>{filteredSymbols.length} symbol{filteredSymbols.length !== 1 ? 's' : ''}</span>
        )}
      </div>
          </>
        )}
      </div>
    </ErrorBoundary>
  )
})

