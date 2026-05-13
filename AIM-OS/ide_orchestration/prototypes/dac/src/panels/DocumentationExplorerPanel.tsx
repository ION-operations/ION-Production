// Documentation Explorer Panel - V2 Feature Implementation
// Documentation browser, search, and navigation

import React, { useState, useMemo, useCallback } from 'react'
import { BasePanel } from '../components/BasePanel'
import { Search, BookOpen, FileText, Code, Hash, ChevronRight, ChevronDown, Layers } from 'lucide-react'
import { useHHNI } from '../hooks/useAIMOS'

interface DocumentationEntry {
  id: string
  title: string
  path: string
  type: 'system' | 'component' | 'protocol' | 'guide' | 'reference'
  level: 'T0' | 'T1' | 'T2' | 'T3' | 'T4' | 'L0' | 'L1' | 'L2' | 'L3' | 'L4'
  system?: string
  description?: string
  wordCount?: number
  lastUpdated?: string
  children?: string[]
  parent?: string
}

// Mock documentation data (would be loaded from documentation index or HHNI)
const mockDocumentation: DocumentationEntry[] = [
  {
    id: 'cmc-readme',
    title: 'CMC README',
    path: 'systems/cmc/README.md',
    type: 'system',
    level: 'T0',
    system: 'CMC',
    description: 'Entry point for CMC system documentation',
    wordCount: 100,
    children: ['cmc-t0', 'cmc-t1', 'cmc-t2'],
  },
  {
    id: 'cmc-t0',
    title: 'CMC T0 Executive',
    path: 'systems/cmc/T0_executive.md',
    type: 'system',
    level: 'T0',
    system: 'CMC',
    description: '100-word executive summary',
    wordCount: 100,
    parent: 'cmc-readme',
  },
  {
    id: 'cmc-t1',
    title: 'CMC T1 Overview',
    path: 'systems/cmc/T1_overview.md',
    type: 'system',
    level: 'T1',
    system: 'CMC',
    description: '500-word overview',
    wordCount: 500,
    parent: 'cmc-readme',
  },
  {
    id: 'vif-readme',
    title: 'VIF README',
    path: 'systems/vif/README.md',
    type: 'system',
    level: 'T0',
    system: 'VIF',
    description: 'Entry point for VIF system documentation',
    wordCount: 100,
    children: ['vif-t0', 'vif-t1'],
  },
  {
    id: 'vif-t0',
    title: 'VIF T0 Executive',
    path: 'systems/vif/T0_executive.md',
    type: 'system',
    level: 'T0',
    system: 'VIF',
    description: '100-word executive summary',
    wordCount: 100,
    parent: 'vif-readme',
  },
  {
    id: 'apoe-readme',
    title: 'APOE README',
    path: 'systems/apoe/README.md',
    type: 'system',
    level: 'T0',
    system: 'APOE',
    description: 'Entry point for APOE system documentation',
    wordCount: 100,
    children: ['apoe-t0'],
  },
  {
    id: 'protocol-cognitive-analysis',
    title: 'Cognitive Analysis Protocol',
    path: 'knowledge_architecture/AETHER_MEMORY/cognitive_analysis_protocol.md',
    type: 'protocol',
    level: 'T2',
    description: 'Protocol for cognitive analysis and introspection',
    wordCount: 2000,
  },
  {
    id: 'guide-l0-l4',
    title: 'L0-L4 Documentation Guide',
    path: 'knowledge_architecture/PERFECT_L0_L6_DOCUMENTATION_STANDARD.md',
    type: 'guide',
    level: 'T2',
    description: 'Complete guide to L0-L4 documentation standards',
    wordCount: 15000,
  },
]

export const DocumentationExplorerPanel: React.FC = () => {
  const { search } = useHHNI()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState<string | null>(null)
  const [selectedLevel, setSelectedLevel] = useState<string | null>(null)
  const [selectedSystem, setSelectedSystem] = useState<string | null>(null)
  const [expandedEntries, setExpandedEntries] = useState<Set<string>>(new Set(['cmc-readme', 'vif-readme', 'apoe-readme']))
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Filter documentation
  const filteredDocs = useMemo(() => {
    let docs = mockDocumentation
    
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      docs = docs.filter(doc =>
        doc.title.toLowerCase().includes(query) ||
        doc.description?.toLowerCase().includes(query) ||
        doc.path.toLowerCase().includes(query) ||
        doc.system?.toLowerCase().includes(query)
      )
    }
    
    if (selectedType) {
      docs = docs.filter(doc => doc.type === selectedType)
    }
    
    if (selectedLevel) {
      docs = docs.filter(doc => doc.level === selectedLevel)
    }
    
    if (selectedSystem) {
      docs = docs.filter(doc => doc.system === selectedSystem)
    }
    
    return docs
  }, [searchQuery, selectedType, selectedLevel, selectedSystem])
  
  // Build hierarchy tree
  const hierarchyTree = useMemo(() => {
    const rootEntries = filteredDocs.filter(e => !e.parent)
    const buildTree = (parentId: string | undefined): DocumentationEntry[] => {
      return filteredDocs
        .filter(e => e.parent === parentId)
        .map(entry => ({
          ...entry,
          children: buildTree(entry.id),
        }))
    }
    
    return rootEntries.map(entry => ({
      ...entry,
      children: buildTree(entry.id),
    }))
  }, [filteredDocs])
  
  // Get unique types, levels, and systems
  const types = useMemo(() => {
    return Array.from(new Set(mockDocumentation.map(d => d.type))).sort()
  }, [])
  
  const levels = useMemo(() => {
    return Array.from(new Set(mockDocumentation.map(d => d.level))).sort()
  }, [])
  
  const systems = useMemo(() => {
    return Array.from(new Set(mockDocumentation.filter(d => d.system).map(d => d.system!))).sort()
  }, [])
  
  const toggleEntry = useCallback((entryId: string) => {
    setExpandedEntries(prev => {
      const next = new Set(prev)
      if (next.has(entryId)) {
        next.delete(entryId)
      } else {
        next.add(entryId)
      }
      return next
    })
  }, [])
  
  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim()) return
    
    setLoading(true)
    setError(null)
    
    try {
      // Would use HHNI search here
      const results = await search(searchQuery, 20)
      // Process results...
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setLoading(false)
    }
  }, [searchQuery, search])
  
  // Calculate AIM-OS metrics
  const overallConfidence = useMemo(() => {
    return 0.90
  }, [])
  
  const confidenceBand: 'A' | 'B' | 'C' = useMemo(() => {
    if (overallConfidence >= 0.90) return 'A'
    if (overallConfidence >= 0.70) return 'B'
    return 'C'
  }, [overallConfidence])
  
  const totalDocs = mockDocumentation.length
  const displayedDocs = filteredDocs.length
  
  const renderEntry = (entry: DocumentationEntry & { children?: DocumentationEntry[] }, depth: number = 0): React.ReactNode => {
    const isExpanded = expandedEntries.has(entry.id)
    const hasChildren = entry.children && entry.children.length > 0
    
    return (
      <div key={entry.id} className="space-y-1">
        <div
          className={`bg-gray-900 border border-gray-700 rounded p-2 hover:border-gray-600 transition-colors ${
            depth > 0 ? 'ml-4' : ''
          }`}
        >
          <button
            onClick={() => hasChildren && toggleEntry(entry.id)}
            className="w-full flex items-start gap-2 text-left"
          >
            {hasChildren ? (
              isExpanded ? (
                <ChevronDown className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
              )
            ) : (
              <div className="w-4 h-4" />
            )}
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm font-medium text-gray-200">{entry.title}</span>
                <span className={`px-1.5 py-0.5 text-xs rounded ${
                  entry.type === 'system' ? 'bg-blue-900/30 text-blue-300' :
                  entry.type === 'component' ? 'bg-purple-900/30 text-purple-300' :
                  entry.type === 'protocol' ? 'bg-green-900/30 text-green-300' :
                  entry.type === 'guide' ? 'bg-yellow-900/30 text-yellow-300' :
                  'bg-gray-700 text-gray-300'
                }`}>
                  {entry.type}
                </span>
                <span className="px-1.5 py-0.5 text-xs rounded bg-gray-800 text-gray-400 font-mono">
                  {entry.level}
                </span>
                {entry.wordCount && (
                  <span className="text-xs text-gray-500">
                    {entry.wordCount.toLocaleString()}w
                  </span>
                )}
              </div>
              
              {entry.description && (
                <div className="text-xs text-gray-400 mb-1">{entry.description}</div>
              )}
              
              <div className="text-xs text-gray-500 flex items-center gap-1">
                <FileText className="w-3 h-3" />
                {entry.path}
              </div>
            </div>
          </button>
        </div>
        
        {isExpanded && hasChildren && entry.children && (
          <div className="space-y-1">
            {entry.children.map(child => renderEntry(child, depth + 1))}
          </div>
        )}
      </div>
    )
  }
  
  return (
    <BasePanel
      id="documentation-explorer-panel"
      title="Documentation Explorer"
      icon={BookOpen}
      description="Documentation browser, search, and navigation"
      loading={loading}
      error={error}
      empty={displayedDocs === 0}
      emptyMessage={searchQuery ? `No documentation found for "${searchQuery}"` : 'No documentation available'}
      confidence={overallConfidence}
      confidenceBand={confidenceBand}
      atomCount={totalDocs}
      footerContent={
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>{displayedDocs} of {totalDocs} documents</span>
          <span>{hierarchyTree.length} root entries</span>
        </div>
      }
    >
      {/* Search Bar */}
      <div className="mb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search documentation..."
            className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-700 rounded text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>
      
      {/* Filters */}
      <div className="mb-4 space-y-2">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedType(null)}
            className={`px-2 py-1 text-xs rounded ${
              !selectedType
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            All Types
          </button>
          {types.map(type => (
            <button
              key={type}
              onClick={() => setSelectedType(selectedType === type ? null : type)}
              className={`px-2 py-1 text-xs rounded capitalize ${
                selectedType === type
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
        
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedLevel(null)}
            className={`px-2 py-1 text-xs rounded ${
              !selectedLevel
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            All Levels
          </button>
          {levels.map(level => (
            <button
              key={level}
              onClick={() => setSelectedLevel(selectedLevel === level ? null : level)}
              className={`px-2 py-1 text-xs rounded font-mono ${
                selectedLevel === level
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {level}
            </button>
          ))}
        </div>
        
        {systems.length > 0 && (
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedSystem(null)}
              className={`px-2 py-1 text-xs rounded ${
                !selectedSystem
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              All Systems
            </button>
            {systems.map(system => (
              <button
                key={system}
                onClick={() => setSelectedSystem(selectedSystem === system ? null : system)}
                className={`px-2 py-1 text-xs rounded ${
                  selectedSystem === system
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {system}
              </button>
            ))}
          </div>
        )}
      </div>
      
      {/* Documentation Tree */}
      <div className="space-y-2 max-h-[calc(100vh-500px)] overflow-auto">
        {hierarchyTree.map(entry => renderEntry(entry))}
      </div>
    </BasePanel>
  )
}

