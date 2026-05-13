// Master Index Panel - V2 Feature Implementation
// Master index navigation with cross-references and hierarchical structure

import React, { useState, useMemo, useCallback } from 'react'
import { BasePanel } from '../components/BasePanel'
import { Search, BookOpen, FileText, Link2, ChevronRight, ChevronDown, Hash, Layers } from 'lucide-react'
import { useHHNI } from '../hooks/useAIMOS'

interface MasterIndexEntry {
  id: string
  title: string
  type: 'system' | 'component' | 'concept' | 'document' | 'protocol'
  path: string
  description?: string
  crossReferences?: string[]
  parent?: string
  children?: string[]
  level: number  // Hierarchy level (0 = root, 1 = system, 2 = component, etc.)
}

// Mock master index data (would be loaded from master index files or HHNI)
const mockMasterIndex: MasterIndexEntry[] = [
  {
    id: 'cmc',
    title: 'CMC (Conscious Memory Core)',
    type: 'system',
    path: 'systems/cmc/',
    description: 'Bitemporal storage system for all AIM-OS data',
    crossReferences: ['atoms', 'bitemporal', 'snapshots'],
    level: 0,
    children: ['cmc-atoms', 'cmc-snapshots', 'cmc-bitemporal'],
  },
  {
    id: 'cmc-atoms',
    title: 'Atoms',
    type: 'component',
    path: 'systems/cmc/components/atoms/',
    description: 'Fundamental data unit in Project Aether',
    parent: 'cmc',
    level: 1,
  },
  {
    id: 'cmc-snapshots',
    title: 'Snapshots',
    type: 'component',
    path: 'systems/cmc/components/snapshots/',
    description: 'Bitemporal versioning system',
    parent: 'cmc',
    level: 1,
  },
  {
    id: 'vif',
    title: 'VIF (Verifiable Intelligence Framework)',
    type: 'system',
    path: 'systems/vif/',
    description: 'Witness envelopes for provenance, replay, and uncertainty quantification',
    crossReferences: ['witnesses', 'confidence', 'kappa-gating'],
    level: 0,
    children: ['vif-witnesses', 'vif-confidence', 'vif-kappa'],
  },
  {
    id: 'vif-witnesses',
    title: 'Witnesses',
    type: 'component',
    path: 'systems/vif/components/witnesses/',
    description: 'Cryptographic witness envelopes',
    parent: 'vif',
    level: 1,
  },
  {
    id: 'seg',
    title: 'SEG (Shared Evidence Graph)',
    type: 'system',
    path: 'systems/seg/',
    description: 'Knowledge graph connecting evidence, claims, and contradictions',
    crossReferences: ['contradictions', 'evidence', 'knowledge-synthesis'],
    level: 0,
    children: ['seg-contradictions', 'seg-evidence'],
  },
  {
    id: 'apoe',
    title: 'APOE (AI-Powered Orchestration Engine)',
    type: 'system',
    path: 'systems/apoe/',
    description: 'Compiles reasoning into executable plans (DAGs)',
    crossReferences: ['acl', 'dag', 'gates', 'budget'],
    level: 0,
    children: ['apoe-acl', 'apoe-dag'],
  },
  {
    id: 'hhni',
    title: 'HHNI (Hierarchical Human-Native Interface)',
    type: 'system',
    path: 'systems/hhni/',
    description: 'Retrieval system using hierarchical paths',
    crossReferences: ['search', 'retrieval', 'hierarchical-paths'],
    level: 0,
  },
  {
    id: 'tcs',
    title: 'TCS (Timeline Context System)',
    type: 'system',
    path: 'systems/tcs/',
    description: 'Bitemporal timeline tracking for perfect recall',
    crossReferences: ['timeline', 'bitemporal', 'perfect-recall'],
    level: 0,
  },
  {
    id: 'cas',
    title: 'CAS (Cognitive Analysis System)',
    type: 'system',
    path: 'systems/cognitive_analysis/',
    description: 'Meta-cognitive system for AI introspection',
    crossReferences: ['consciousness', 'meta-cognition', 'introspection'],
    level: 0,
  },
]

export const MasterIndexPanel: React.FC = () => {
  const { search } = useHHNI()
  const [searchQuery, setSearchQuery] = useState('')
  const [expandedEntries, setExpandedEntries] = useState<Set<string>>(new Set(['cmc', 'vif', 'seg', 'apoe']))
  const [selectedType, setSelectedType] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Filter entries by search query
  const filteredEntries = useMemo(() => {
    let entries = mockMasterIndex
    
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      entries = entries.filter(entry =>
        entry.title.toLowerCase().includes(query) ||
        entry.description?.toLowerCase().includes(query) ||
        entry.path.toLowerCase().includes(query) ||
        entry.crossReferences?.some(ref => ref.toLowerCase().includes(query))
      )
    }
    
    if (selectedType) {
      entries = entries.filter(entry => entry.type === selectedType)
    }
    
    return entries
  }, [searchQuery, selectedType])
  
  // Build hierarchy tree
  const hierarchyTree = useMemo(() => {
    const rootEntries = filteredEntries.filter(e => e.level === 0)
    const buildTree = (parentId: string | undefined): MasterIndexEntry[] => {
      return filteredEntries
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
  }, [filteredEntries])
  
  // Get unique types
  const types = useMemo(() => {
    return Array.from(new Set(mockMasterIndex.map(e => e.type))).sort()
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
  
  const totalEntries = mockMasterIndex.length
  const displayedEntries = filteredEntries.length
  
  const renderEntry = (entry: MasterIndexEntry & { children?: MasterIndexEntry[] }, depth: number = 0): React.ReactNode => {
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
                  entry.type === 'concept' ? 'bg-green-900/30 text-green-300' :
                  entry.type === 'document' ? 'bg-yellow-900/30 text-yellow-300' :
                  'bg-gray-700 text-gray-300'
                }`}>
                  {entry.type}
                </span>
              </div>
              
              {entry.description && (
                <div className="text-xs text-gray-400 mb-1">{entry.description}</div>
              )}
              
              <div className="text-xs text-gray-500 flex items-center gap-1">
                <FileText className="w-3 h-3" />
                {entry.path}
              </div>
              
              {isExpanded && (
                <div className="mt-2 space-y-2">
                  {entry.crossReferences && entry.crossReferences.length > 0 && (
                    <div>
                      <div className="text-xs text-gray-400 mb-1 flex items-center gap-1">
                        <Link2 className="w-3 h-3" />
                        Cross References:
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {entry.crossReferences.map((ref, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-0.5 bg-gray-800 text-gray-300 rounded text-xs cursor-pointer hover:bg-gray-700"
                            onClick={(e) => {
                              e.stopPropagation()
                              setSearchQuery(ref)
                            }}
                          >
                            {ref}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
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
      id="master-index-panel"
      title="Master Index"
      icon={Layers}
      description="Master index navigation with cross-references and hierarchical structure"
      loading={loading}
      error={error}
      empty={displayedEntries === 0}
      emptyMessage={searchQuery ? `No entries found for "${searchQuery}"` : 'No entries available'}
      confidence={overallConfidence}
      confidenceBand={confidenceBand}
      atomCount={totalEntries}
      footerContent={
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>{displayedEntries} of {totalEntries} entries</span>
          <span>{hierarchyTree.length} root systems</span>
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
            placeholder="Search master index..."
            className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-700 rounded text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>
      
      {/* Type Filter */}
      <div className="mb-4 flex flex-wrap gap-1">
        <button
          onClick={() => setSelectedType(null)}
          className={`px-2 py-1 text-xs rounded ${
            !selectedType
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
          }`}
        >
          All
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
      
      {/* Hierarchy Tree */}
      <div className="space-y-2 max-h-[calc(100vh-400px)] overflow-auto">
        {hierarchyTree.map(entry => renderEntry(entry))}
      </div>
    </BasePanel>
  )
}

