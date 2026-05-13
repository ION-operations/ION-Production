// Outline Panel - V2 Refactored with BasePanel
// Symbol navigation with HHNI IndexNode hierarchical structure

import React, { useState, useEffect } from 'react'
import { useHHNI } from '../hooks/useAIMOS'
import { BasePanel } from '../components/BasePanel'
import { Code, ChevronRight, ChevronDown, Network, Search } from 'lucide-react'
import type { HHNISearchResult } from '../hooks/useAIMOS'

interface Symbol {
  id: string
  name: string
  type: 'function' | 'class' | 'interface' | 'variable' | 'type' | 'module' | 'namespace'
  line: number
  column?: number
  
  // HHNI Integration
  hhni_node?: {
    id: string
    level: 'document' | 'paragraph' | 'sentence'
    content: string
    summary?: string
    embeddings?: number[]
  }
  hhni_path?: string[]  // Hierarchical path
  semantic_score?: number
  
  children?: Symbol[]
}

const mockSymbols: Symbol[] = [
  {
    id: 'symbol_1',
    name: 'IDELayout',
    type: 'class',
    line: 1,
    column: 1,
    hhni_path: ['IDE', 'Components', 'Layout', 'IDELayout'],
    semantic_score: 0.95,
    children: [
      {
        id: 'symbol_1_1',
        name: 'render',
        type: 'function',
        line: 10,
        column: 5,
        hhni_path: ['IDE', 'Components', 'Layout', 'IDELayout', 'render'],
        semantic_score: 0.88
      },
      {
        id: 'symbol_1_2',
        name: 'handlePanelToggle',
        type: 'function',
        line: 25,
        column: 5,
        hhni_path: ['IDE', 'Components', 'Layout', 'IDELayout', 'handlePanelToggle'],
        semantic_score: 0.85
      },
      {
        id: 'symbol_1_3',
        name: 'state',
        type: 'variable',
        line: 5,
        column: 3,
        hhni_path: ['IDE', 'Components', 'Layout', 'IDELayout', 'state'],
        semantic_score: 0.80
      }
    ]
  },
  {
    id: 'symbol_2',
    name: 'useCMC',
    type: 'function',
    line: 50,
    column: 1,
    hhni_path: ['IDE', 'Hooks', 'AIMOS', 'useCMC'],
    semantic_score: 0.92,
    children: [
      {
        id: 'symbol_2_1',
        name: 'storeAtom',
        type: 'function',
        line: 55,
        column: 5,
        hhni_path: ['IDE', 'Hooks', 'AIMOS', 'useCMC', 'storeAtom'],
        semantic_score: 0.90
      },
      {
        id: 'symbol_2_2',
        name: 'retrieveAtoms',
        type: 'function',
        line: 70,
        column: 5,
        hhni_path: ['IDE', 'Hooks', 'AIMOS', 'useCMC', 'retrieveAtoms'],
        semantic_score: 0.88
      },
      {
        id: 'symbol_2_3',
        name: 'getStats',
        type: 'function',
        line: 85,
        column: 5,
        hhni_path: ['IDE', 'Hooks', 'AIMOS', 'useCMC', 'getStats'],
        semantic_score: 0.85
      }
    ]
  },
  {
    id: 'symbol_3',
    name: 'FileTree',
    type: 'class',
    line: 100,
    column: 1,
    hhni_path: ['IDE', 'Components', 'Panels', 'FileTree'],
    semantic_score: 0.89,
    children: [
      {
        id: 'symbol_3_1',
        name: 'renderFileNode',
        type: 'function',
        line: 110,
        column: 5,
        hhni_path: ['IDE', 'Components', 'Panels', 'FileTree', 'renderFileNode'],
        semantic_score: 0.87
      },
      {
        id: 'symbol_3_2',
        name: 'toggleFolder',
        type: 'function',
        line: 130,
        column: 5,
        hhni_path: ['IDE', 'Components', 'Panels', 'FileTree', 'toggleFolder'],
        semantic_score: 0.85
      }
    ]
  },
  {
    id: 'symbol_4',
    name: 'CMCAtom',
    type: 'interface',
    line: 200,
    column: 1,
    hhni_path: ['IDE', 'Types', 'AIMOS', 'CMCAtom'],
    semantic_score: 0.93
  },
  {
    id: 'symbol_5',
    name: 'VIFWitness',
    type: 'interface',
    line: 250,
    column: 1,
    hhni_path: ['IDE', 'Types', 'AIMOS', 'VIFWitness'],
    semantic_score: 0.91
  }
]

export const OutlinePanel: React.FC = () => {
  const { search } = useHHNI()
  const [symbols, setSymbols] = useState<Symbol[]>(mockSymbols)
  const [expanded, setExpanded] = useState<Set<string>>(new Set(['IDELayout', 'useCMC', 'FileTree']))
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<HHNISearchResult[]>([])
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    // Enhance symbols with HHNI search results
    const enhanceSymbols = async () => {
      if (searchQuery.trim()) {
        try {
          setLoading(true)
          setError(null)
          const results = await search(searchQuery, 20)
          setSearchResults(results)
          
          // Highlight matching symbols
          const enhanced = symbols.map(symbol => {
            const matchingResult = results.find(r => 
              r.node.content.toLowerCase().includes(symbol.name.toLowerCase()) ||
              symbol.hhni_path?.some(path => path.toLowerCase().includes(searchQuery.toLowerCase()))
            )
            
            return {
              ...symbol,
              hhni_node: matchingResult?.node,
              semantic_score: matchingResult?.score || symbol.semantic_score
            }
          })
          setSymbols(enhanced)
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Search failed')
        } finally {
          setLoading(false)
        }
      } else {
        setSearchResults([])
      }
    }
    
    enhanceSymbols()
  }, [searchQuery, search])
  
  const toggleExpand = (id: string) => {
    setExpanded(prev => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }
  
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'function': return 'text-blue-400'
      case 'class': return 'text-green-400'
      case 'interface': return 'text-yellow-400'
      case 'variable': return 'text-purple-400'
      case 'type': return 'text-cyan-400'
      case 'module': return 'text-pink-400'
      case 'namespace': return 'text-orange-400'
      default: return 'text-gray-300'
    }
  }
  
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'function': return 'ƒ'
      case 'class': return 'C'
      case 'interface': return 'I'
      case 'variable': return 'v'
      case 'type': return 'T'
      case 'module': return 'M'
      case 'namespace': return 'N'
      default: return '•'
    }
  }
  
  const getSemanticScoreColor = (score?: number) => {
    if (!score) return 'text-gray-400'
    if (score >= 0.85) return 'text-green-400'
    if (score >= 0.70) return 'text-yellow-400'
    return 'text-red-400'
  }
  
  const renderSymbol = (symbol: Symbol, level: number = 0) => {
    const isExpanded = expanded.has(symbol.id)
    const hasChildren = symbol.children && symbol.children.length > 0
    const isSelected = selectedSymbol === symbol.id
    const isHighlighted = searchResults.some(r => 
      r.node.content.toLowerCase().includes(symbol.name.toLowerCase())
    )
    
    return (
      <div key={symbol.id}>
        <div
          className={`flex items-center gap-2 px-2 py-1 hover:bg-gray-700 cursor-pointer text-sm ${
            isSelected ? 'bg-blue-900/30 border-l-2 border-blue-500' : ''
          } ${isHighlighted && searchQuery ? 'bg-yellow-900/20' : ''}`}
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => {
            if (hasChildren) {
              toggleExpand(symbol.id)
            }
            setSelectedSymbol(symbol.id)
          }}
        >
          {hasChildren ? (
            isExpanded ? (
              <ChevronDown className="w-4 h-4 text-gray-400" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-400" />
            )
          ) : (
            <div className="w-4 h-4" />
          )}
          
          {/* Type Icon */}
          <span className={`text-xs ${getTypeColor(symbol.type)}`}>
            {getTypeIcon(symbol.type)}
          </span>
          
          {/* Symbol Name */}
          <span className="text-gray-300 flex-1 truncate">{symbol.name}</span>
          
          {/* HHNI Path Indicator */}
          {symbol.hhni_path && symbol.hhni_path.length > 0 && (
            <span
              className="px-1.5 py-0.5 rounded text-xs bg-purple-900/30 text-purple-300 border border-purple-700 flex items-center gap-1"
              title={`HHNI Path: ${symbol.hhni_path.join(' → ')}`}
            >
              <Network className="w-3 h-3" />
              {symbol.hhni_path.length}
            </span>
          )}
          
          {/* Semantic Score */}
          {symbol.semantic_score !== undefined && (
            <span className={`text-xs ${getSemanticScoreColor(symbol.semantic_score)}`} title="Semantic Score">
              {(symbol.semantic_score * 100).toFixed(0)}%
            </span>
          )}
          
          {/* Line Number */}
          <span className="text-xs text-gray-500">{symbol.line}</span>
        </div>
        
        {/* HHNI Node Details (when expanded) */}
        {isExpanded && symbol.hhni_node && (
          <div className="ml-8 mb-1 p-2 bg-gray-800/50 rounded border border-gray-700 text-xs">
            <div className="text-gray-400 mb-1">HHNI Node:</div>
            <div className="text-gray-300 font-mono text-xs mb-1">
              {symbol.hhni_node.id.substring(0, 16)}...
            </div>
            <div className="text-gray-400">
              Level: <span className="text-gray-300 capitalize">{symbol.hhni_node.level}</span>
            </div>
            {symbol.hhni_node.summary && (
              <div className="text-gray-400 mt-1 line-clamp-2">
                {symbol.hhni_node.summary}
              </div>
            )}
          </div>
        )}
        
        {hasChildren && isExpanded && (
          <div>
            {symbol.children!.map(child => renderSymbol(child, level + 1))}
          </div>
        )}
      </div>
    )
  }
  
  // Filter symbols by search
  const filteredSymbols = searchQuery.trim() && searchResults.length > 0
    ? symbols.filter(symbol => {
        return searchResults.some(r => 
          r.node.content.toLowerCase().includes(symbol.name.toLowerCase()) ||
          symbol.hhni_path?.some(path => path.toLowerCase().includes(searchQuery.toLowerCase()))
        )
      })
    : symbols
  
  // Calculate AIM-OS metrics
  const overallConfidence = symbols.length > 0 && symbols[0].semantic_score !== undefined
    ? symbols.reduce((sum, symbol) => sum + (symbol.semantic_score || 0), 0) / symbols.length
    : undefined
  
  const confidenceBand = overallConfidence 
    ? (overallConfidence >= 0.85 ? 'A' : overallConfidence >= 0.70 ? 'B' : 'C')
    : undefined
  
  const symbolCount = symbols.filter(s => !s.children || s.children.length === 0).length
  
  return (
    <BasePanel
      id="panel-outline"
      title="Outline"
      icon={Code}
      description="Symbol navigation with HHNI hierarchical structure"
      loading={loading}
      error={error}
      empty={!loading && !error && filteredSymbols.length === 0}
      emptyMessage={searchQuery ? "No symbols found matching your search" : "No symbols available"}
      confidence={overallConfidence}
      confidenceBand={confidenceBand}
      atomCount={symbolCount}
      footerContent={
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>
            {symbolCount} symbols
            {searchQuery && searchResults.length > 0 && ` • ${searchResults.length} matches`}
          </span>
          <span className="text-green-400">HHNI Hierarchical Navigation Active</span>
        </div>
      }
      headerClassName="p-3"
    >
      {/* Search */}
      <div className="p-3 border-b border-gray-700">
        <div className="flex items-center gap-2 bg-gray-800 rounded px-2 py-1">
          <Search className="w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search symbols (HHNI semantic)..."
            className="flex-1 bg-transparent text-gray-300 placeholder-gray-500 text-sm outline-none"
          />
          {searchResults.length > 0 && (
            <span className="text-xs text-blue-400">
              {searchResults.length} results
            </span>
          )}
        </div>
      </div>
      
      {/* Symbol Tree */}
      <div className="flex-1 overflow-auto p-2">
        {filteredSymbols.map(symbol => renderSymbol(symbol))}
      </div>
      
      {/* Selected Symbol Details */}
      {selectedSymbol && (
        <div className="p-2 border-t border-gray-700 bg-gray-800/50">
          {(() => {
            const findSymbol = (symbols: Symbol[]): Symbol | null => {
              for (const symbol of symbols) {
                if (symbol.id === selectedSymbol) return symbol
                if (symbol.children) {
                  const found = findSymbol(symbol.children)
                  if (found) return found
                }
              }
              return null
            }
            const symbol = findSymbol(symbols)
            if (!symbol) return null
            
            return (
              <div className="space-y-2 text-xs">
                <div className="font-semibold text-gray-200">{symbol.name}</div>
                <div className="flex gap-4">
                  <div>
                    <span className="text-gray-500">Type:</span>
                    <span className={`ml-2 ${getTypeColor(symbol.type)} capitalize`}>
                      {symbol.type}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-500">Line:</span>
                    <span className="ml-2 text-gray-300">{symbol.line}</span>
                  </div>
                  {symbol.semantic_score !== undefined && (
                    <div>
                      <span className="text-gray-500">Score:</span>
                      <span className={`ml-2 ${getSemanticScoreColor(symbol.semantic_score)}`}>
                        {(symbol.semantic_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                </div>
                {symbol.hhni_path && (
                  <div>
                    <span className="text-gray-500">HHNI Path:</span>
                    <span className="ml-2 text-gray-300">{symbol.hhni_path.join(' → ')}</span>
                  </div>
                )}
              </div>
            )
          })()}
        </div>
      )}
    </BasePanel>
  )
}
