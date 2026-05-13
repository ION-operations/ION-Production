// Memory Browser Panel - V2 Refactored with BasePanel
// CMC memory exploration with real AIM-OS atom structure

import React, { useState, useEffect } from 'react'
import { useCMC, useHHNI, useVIF } from '../hooks/useAIMOS'
import { BasePanel } from '../components/BasePanel'
import { Brain, Search, Filter, FileText, Code, Zap, Settings, Archive, Clock } from 'lucide-react'
import type { CMCAtom } from '../hooks/useAIMOS'

export const MemoryBrowser: React.FC = () => {
  const { retrieveAtoms, atoms } = useCMC()
  const { search } = useHHNI()
  const { getWitnesses } = useVIF()
  const [memories, setMemories] = useState<CMCAtom[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [filterModality, setFilterModality] = useState<string>('all')
  const [sortBy, setSortBy] = useState<'recent' | 'confidence' | 'relevance'>('recent')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  useEffect(() => {
    loadMemories()
  }, [])
  
  const loadMemories = async () => {
    try {
      setLoading(true)
      setError(null)
      const results = await retrieveAtoms('', 50)
      const enhanced = await Promise.all(
        results.map(async (atom) => {
          // Get VIF witnesses for confidence
          const witnesses = await getWitnesses(atom.id)
          return atom
        })
      )
      setMemories(enhanced)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load memories')
    } finally {
      setLoading(false)
    }
  }
  
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadMemories()
      return
    }
    
    try {
      setLoading(true)
      setError(null)
      // Use HHNI semantic search
      const hhniResults = await search(searchQuery, 50)
      const atomIds = hhniResults.map(r => r.node.id)
      const results = await Promise.all(
        atomIds.map(async (id) => {
          const atoms = await retrieveAtoms(`atom_id:${id}`, 1)
          return atoms[0]
        })
      )
      setMemories(results.filter(Boolean))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setLoading(false)
    }
  }
  
  const filteredMemories = memories.filter(mem => {
    if (filterModality === 'all') return true
    return mem.modality === filterModality
  })
  
  // Sort memories
  const sortedMemories = [...filteredMemories].sort((a, b) => {
    switch (sortBy) {
      case 'recent':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      case 'confidence':
        const aConf = a.witness.uncertainty_band === 'green' ? 0.9 : a.witness.uncertainty_band === 'yellow' ? 0.7 : 0.5
        const bConf = b.witness.uncertainty_band === 'green' ? 0.9 : b.witness.uncertainty_band === 'yellow' ? 0.7 : 0.5
        return bConf - aConf
      case 'relevance':
        // Sort by tag weights (highest first)
        const aWeight = Math.max(...Object.values(a.tags))
        const bWeight = Math.max(...Object.values(b.tags))
        return bWeight - aWeight
      default:
        return 0
    }
  })
  
  const getModalityIcon = (modality: string) => {
    switch (modality) {
      case 'text': return <FileText className="w-4 h-4" />
      case 'code': return <Code className="w-4 h-4" />
      case 'event': return <Zap className="w-4 h-4" />
      case 'tool': return <Settings className="w-4 h-4" />
      default: return <FileText className="w-4 h-4" />
    }
  }
  
  const getModalityColor = (modality: string) => {
    switch (modality) {
      case 'text': return 'bg-blue-900/30 border-blue-700 text-blue-300'
      case 'code': return 'bg-green-900/30 border-green-700 text-green-300'
      case 'event': return 'bg-yellow-900/30 border-yellow-700 text-yellow-300'
      case 'tool': return 'bg-purple-900/30 border-purple-700 text-purple-300'
      default: return 'bg-gray-900/30 border-gray-700 text-gray-300'
    }
  }
  
  const getUncertaintyColor = (band: string) => {
    switch (band) {
      case 'green': return 'text-green-400'
      case 'yellow': return 'text-yellow-400'
      case 'red': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }
  
  const getUncertaintyBadge = (band: string) => {
    switch (band) {
      case 'green': return '🟢 High Confidence'
      case 'yellow': return '🟡 Medium Confidence'
      case 'red': return '🔴 Low Confidence'
      default: return '⚪ Unknown'
    }
  }
  
  // Calculate AIM-OS metrics
  const overallConfidence = memories.length > 0
    ? memories.reduce((sum, mem) => {
        const conf = mem.witness.uncertainty_band === 'green' ? 0.9 : 
                     mem.witness.uncertainty_band === 'yellow' ? 0.7 : 0.5
        return sum + conf
      }, 0) / memories.length
    : undefined
  
  const confidenceBand = overallConfidence 
    ? (overallConfidence >= 0.90 ? 'A' : overallConfidence >= 0.70 ? 'B' : 'C')
    : undefined
  
  const atomCount = sortedMemories.length
  
  return (
    <BasePanel
      id="panel-memory-browser"
      title="AI Memory Browser"
      icon={Brain}
      description="CMC memory exploration with HHNI semantic search"
      loading={loading}
      error={error}
      empty={!loading && !error && sortedMemories.length === 0}
      emptyMessage={searchQuery ? "No memories found matching your search" : "No memories available"}
      confidence={overallConfidence}
      confidenceBand={confidenceBand}
      atomCount={atomCount}
      footerContent={
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>
            {sortedMemories.length} memories
            {filterModality !== 'all' && ` (${filterModality})`}
          </span>
          <span className="text-green-400">CMC Integration Active</span>
        </div>
      }
      headerClassName="p-3"
    >
      {/* Search and Filters - Keep in content area for interactivity */}
      <div className="p-3 border-b border-gray-700 space-y-2">
        {/* Search */}
        <div className="flex gap-2">
          <div className="flex-1 flex items-center gap-2 bg-gray-800 rounded px-2 py-1">
            <Search className="w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search memories (HHNI semantic search)..."
              className="flex-1 bg-transparent text-gray-300 placeholder-gray-500 text-sm outline-none"
            />
          </div>
          <button
            onClick={handleSearch}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm text-white"
          >
            Search
          </button>
        </div>
        
        {/* Filters & Sort */}
        <div className="flex gap-2 flex-wrap">
          {/* Modality Filters */}
          <div className="flex gap-1">
            <button
              onClick={() => setFilterModality('all')}
              className={`px-2 py-1 rounded text-xs ${
                filterModality === 'all' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilterModality('text')}
              className={`px-2 py-1 rounded text-xs flex items-center gap-1 ${
                filterModality === 'text' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              <FileText className="w-3 h-3" />
              Text
            </button>
            <button
              onClick={() => setFilterModality('code')}
              className={`px-2 py-1 rounded text-xs flex items-center gap-1 ${
                filterModality === 'code' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              <Code className="w-3 h-3" />
              Code
            </button>
            <button
              onClick={() => setFilterModality('event')}
              className={`px-2 py-1 rounded text-xs flex items-center gap-1 ${
                filterModality === 'event' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              <Zap className="w-3 h-3" />
              Event
            </button>
            <button
              onClick={() => setFilterModality('tool')}
              className={`px-2 py-1 rounded text-xs flex items-center gap-1 ${
                filterModality === 'tool' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              <Settings className="w-3 h-3" />
              Tool
            </button>
          </div>
          
          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-2 py-1 rounded text-xs bg-gray-700 text-gray-300 border border-gray-600"
          >
            <option value="recent">Recent</option>
            <option value="confidence">Confidence</option>
            <option value="relevance">Relevance</option>
          </select>
        </div>
      </div>
      
      {/* Memory List */}
      <div className="flex-1 overflow-auto p-3 space-y-2">
        {sortedMemories.map((memory) => {
          const uncertaintyColor = getUncertaintyColor(memory.witness.uncertainty_band)
          const modalityColor = getModalityColor(memory.modality)
          const isArchived = memory.valid_to !== null
          const topTags = Object.entries(memory.tags)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 3)
          
          return (
            <div
              key={memory.id}
              className={`p-3 rounded border ${isArchived ? 'border-gray-800 opacity-60' : 'border-gray-700'} bg-gray-800 hover:bg-gray-750 cursor-pointer transition-all`}
            >
              {/* Header Row */}
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  {/* Modality Badge */}
                  <div className={`px-2 py-0.5 rounded text-xs flex items-center gap-1 ${modalityColor} flex-shrink-0`}>
                    {getModalityIcon(memory.modality)}
                    <span className="capitalize">{memory.modality}</span>
                  </div>
                  
                  {/* Atom ID */}
                  <span className="text-xs text-gray-500 font-mono truncate">
                    {memory.id.substring(0, 16)}...
                  </span>
                  
                  {/* Top Tags */}
                  {topTags.map(([tag, weight]) => (
                    <span
                      key={tag}
                      className="px-1.5 py-0.5 rounded text-xs bg-gray-700 text-gray-400 border border-gray-600"
                      title={`Weight: ${(weight * 100).toFixed(0)}%`}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                
                {/* VIF Witness Info */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  {memory.witness.model_id && (
                    <span className="text-xs text-gray-500" title="Model ID">
                      {memory.witness.model_id.split('-')[0]}
                    </span>
                  )}
                  <span className={`text-xs ${uncertaintyColor}`} title="Uncertainty Band">
                    {getUncertaintyBadge(memory.witness.uncertainty_band)}
                  </span>
                  {memory.witness.uncertainty_ece !== undefined && (
                    <span className="text-xs text-gray-500" title="Expected Calibration Error">
                      ECE: {(memory.witness.uncertainty_ece * 100).toFixed(1)}%
                    </span>
                  )}
                </div>
              </div>
              
              {/* Content Preview */}
              <div className="text-sm text-gray-300 mb-2 line-clamp-2">
                {memory.content.inline ? (
                  <>
                    {memory.content.inline.substring(0, 200)}
                    {memory.content.inline.length > 200 && '...'}
                  </>
                ) : (
                  <div className="flex items-center gap-2 text-gray-500">
                    <Archive className="w-4 h-4" />
                    <span>External content: {memory.content.uri}</span>
                  </div>
                )}
              </div>
              
              {/* Footer Row */}
              <div className="flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center gap-3">
                  {/* Bitemporal Info */}
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    <span>Created: {new Date(memory.created_at).toLocaleDateString()}</span>
                  </div>
                  <span>Valid: {new Date(memory.valid_from).toLocaleDateString()}</span>
                  {isArchived && (
                    <span className="text-red-400 flex items-center gap-1">
                      <Archive className="w-3 h-3" />
                      Archived {new Date(memory.valid_to!).toLocaleDateString()}
                    </span>
                  )}
                </div>
                
                {/* Metadata */}
                {Object.keys(memory.metadata).length > 0 && (
                  <div className="text-xs text-gray-600">
                    {Object.keys(memory.metadata).length} metadata fields
                  </div>
                )}
              </div>
              
              {/* Witness Tools */}
              {memory.witness.tool_ids.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-700">
                  <div className="text-xs text-gray-500 mb-1">Tools Used:</div>
                  <div className="flex flex-wrap gap-1">
                    {memory.witness.tool_ids.map((toolId, idx) => (
                      <span
                        key={idx}
                        className="px-1.5 py-0.5 rounded text-xs bg-purple-900/30 text-purple-300 border border-purple-700"
                      >
                        {toolId.replace('mcp_lucid-mcp_', '')}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </BasePanel>
  )
}
