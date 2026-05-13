/**
 * AI Memory Panel Component
 * 
 * Phase 2.1: Left Drawer Panels
 * 
 * Browse AI memories and context.
 * Features:
 * - Memory search (HHNI semantic search)
 * - Memory filtering by modality
 * - Memory details view
 * - Memory tags
 * - AIM-OS integration (CMC storage, HHNI search, VIF confidence)
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react'
import { Database, Search, Filter, Tag, Clock, Eye, Brain, Code, FileText, Play, Star, AlertCircle, History, TrendingUp } from 'lucide-react'
import { MemoryBrowserEnhanced } from '../MemoryBrowserEnhanced'
import { useAIMOS } from '../../hooks/useAIMOS'
import { useDebounce } from '../../hooks/useDebounce'
import { ConsciousnessAwareness } from '../ConsciousnessAwareness'
import { ErrorBoundary } from '../ErrorBoundary'
import { LoadingState } from '../LoadingState'

interface Memory {
  id: string
  atom_id?: string
  content: string
  modality: 'language' | 'code' | 'memory' | 'plan' | 'execution'
  tags: string[]
  timestamp: string
  witnesses: number
  confidence?: number
}

export const AIMemoryPanel: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [activeFilter, setActiveFilter] = useState<'all' | Memory['modality']>('all')
  const [selectedMemory, setSelectedMemory] = useState<Memory | null>(null)
  const [memories, setMemories] = useState<Memory[]>([])
  const [showHistory, setShowHistory] = useState(false)
  const [historyVersions, setHistoryVersions] = useState<Memory[]>([])
  
  // Debounce search query for performance
  const debouncedSearchQuery = useDebounce(searchQuery, 300)
  
  // AIM-OS integration
  const { cmc, hhni, tcs, isConnected, useMockData, loading } = useAIMOS()

  // Load memories from AIM-OS (CMC + HHNI + TCS for timeline)
  useEffect(() => {
    const loadMemories = async () => {
      if (!useMockData && isConnected) {
        try {
          if (debouncedSearchQuery.trim()) {
            // Use HHNI search for semantic search
            const results = await hhni.search(debouncedSearchQuery, 50)
            const cmcAtoms = await Promise.all(
              results.map(async (result) => {
                try {
                  const atoms = await cmc.retrieve(result.node.content || '', 1)
                  return atoms[0] || null
                } catch {
                  return null
                }
              })
            )
            
            const loadedMemories: Memory[] = cmcAtoms
              .filter(atom => atom)
              .map(atom => ({
                id: atom.id,
                atom_id: atom.id,
                content: atom.content?.inline || atom.content || '',
                modality: atom.modality === 'text' ? 'language' : 
                         atom.modality === 'code' ? 'code' : 
                         atom.modality === 'event' ? 'execution' : 'memory',
                tags: Object.keys(atom.tags || {}),
                timestamp: atom.created_at,
                witnesses: atom.witness?.tool_ids?.length || 0,
                confidence: atom.witness?.uncertainty_band === 'green' ? 0.9 : 
                           atom.witness?.uncertainty_band === 'yellow' ? 0.7 : 0.5,
              }))
            
            setMemories(loadedMemories)
          } else {
            // Load recent memories from CMC
            const atoms = await cmc.retrieve('', 50)
            const loadedMemories: Memory[] = atoms.map(atom => ({
              id: atom.id,
              atom_id: atom.id,
              content: atom.content?.inline || atom.content || '',
              modality: atom.modality === 'text' ? 'language' : 
                       atom.modality === 'code' ? 'code' : 
                       atom.modality === 'event' ? 'execution' : 'memory',
              tags: Object.keys(atom.tags || {}),
              timestamp: atom.created_at,
              witnesses: atom.witness?.tool_ids?.length || 0,
              confidence: atom.witness?.uncertainty_band === 'green' ? 0.9 : 
                         atom.witness?.uncertainty_band === 'yellow' ? 0.7 : 0.5,
            }))
            setMemories(loadedMemories)
          }
        } catch (error) {
          console.warn('Failed to load memories from AIM-OS, using mock data', error)
          setMockMemories()
        }
      } else {
        setMockMemories()
      }
    }
    
    const loadHistory = async (memoryId: string) => {
      if (!useMockData && isConnected && memoryId) {
        try {
          // Use TCS to get timeline entries related to this memory
          const timelineEntries = await tcs.getTimelineEntries(20)
          const relatedEntries = timelineEntries.filter((entry: any) => 
            entry.context_state?.files_read?.includes(memoryId) ||
            entry.user_input?.toLowerCase().includes(memoryId.toLowerCase())
          )
          
          // Transform timeline entries to memory versions
          const versions: Memory[] = relatedEntries.map((entry: any, idx: number) => ({
            id: `${memoryId}-v${idx}`,
            atom_id: memoryId,
            content: entry.user_input || entry.context_state?.current_task || '',
            modality: 'execution',
            tags: ['timeline', 'history'],
            timestamp: entry.timestamp || new Date().toISOString(),
            witnesses: 0,
            confidence: 0.8,
          }))
          
          setHistoryVersions(versions)
        } catch (error) {
          console.warn('Failed to load memory history:', error)
          setHistoryVersions([])
        }
      }
    }
    
    loadMemories()
    
    if (selectedMemory?.atom_id) {
      loadHistory(selectedMemory.atom_id)
    } else {
      setHistoryVersions([])
    }
  }, [debouncedSearchQuery, cmc, hhni, tcs, isConnected, useMockData, selectedMemory])
    
    const setMockMemories = () => {
      // Mock data fallback
      setMemories([
      {
        id: 'mem-001',
        content: 'IDE development started with Code + Docs viewer implementation',
        modality: 'memory',
        tags: ['ide', 'development', 'feature'],
        timestamp: '2025-11-07 14:30',
        witnesses: 3,
        confidence: 0.95,
      },
      {
        id: 'mem-002',
        content: 'function calculateSum(a: number, b: number) { return a + b }',
        modality: 'code',
        tags: ['typescript', 'function'],
        timestamp: '2025-11-07 14:25',
        witnesses: 1,
        confidence: 0.98,
      },
      {
        id: 'mem-003',
        content: 'User requested dual AI chat system with cross-agent communication',
        modality: 'language',
        tags: ['user_request', 'feature', 'ai'],
        timestamp: '2025-11-07 14:20',
        witnesses: 2,
        confidence: 0.92,
      },
      {
        id: 'mem-004',
        content: 'Plan: Complete AIM-OS system visualizations',
        modality: 'plan',
        tags: ['plan', 'aimos', 'visualization'],
        timestamp: '2025-11-07 14:15',
        witnesses: 1,
        confidence: 0.88,
      },
      {
        id: 'mem-005',
        content: 'Executed: Created CodeDocsViewer component',
        modality: 'execution',
        tags: ['execution', 'component'],
        timestamp: '2025-11-07 14:10',
        witnesses: 0,
        confidence: 1.0,
      },
    ])
    }
    
    loadMemories()
  }, [debouncedSearchQuery, cmc, hhni])

  const filteredMemories = useMemo(() => {
    return memories.filter(mem => {
      const matchesSearch = mem.content.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
                           mem.tags.some(tag => tag.toLowerCase().includes(debouncedSearchQuery.toLowerCase()))
      const matchesFilter = activeFilter === 'all' || mem.modality === activeFilter
      return matchesSearch && matchesFilter
    })
  }, [memories, debouncedSearchQuery, activeFilter])

  const getModalityIcon = (modality: string) => {
    switch (modality) {
      case 'language': return <Brain className="w-4 h-4 text-blue-400" />
      case 'code': return <Code className="w-4 h-4 text-green-400" />
      case 'memory': return <Database className="w-4 h-4 text-purple-400" />
      case 'plan': return <Play className="w-4 h-4 text-yellow-400" />
      case 'execution': return <FileText className="w-4 h-4 text-orange-400" />
      default: return <Database className="w-4 h-4 text-gray-400" />
    }
  }

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-800" role="complementary" aria-label="AI Memory Panel">
        {loading.cmc || loading.hhni ? (
          <LoadingState message="Loading memories..." />
        ) : (
          <>
      {/* Header */}
      <div className="h-10 bg-gray-900 border-b border-gray-700 flex items-center px-3 shrink-0">
        <Database className="w-4 h-4 mr-2 text-gray-400" />
        <span className="text-sm font-semibold text-gray-300">AI Memory</span>
        <span className="ml-auto text-xs text-gray-500">{memories.length} memories</span>
        {/* Consciousness Awareness Compact */}
        <div className="ml-2">
          <ConsciousnessAwareness compact={true} showHealth={true} showMemory={false} showGoals={false} showCognitive={false} />
        </div>
      </div>

      {/* Search */}
      <div className="px-2 py-2 border-b border-gray-700 shrink-0">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search memories (HHNI semantic search)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-2 py-1.5 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-500"
            aria-label="Search memories"
          />
        </div>
      </div>

      {/* Filter */}
      <div className="px-2 py-2 border-b border-gray-700 shrink-0">
        <div className="flex gap-1 overflow-x-auto">
          {(['all', 'memory', 'code', 'language', 'plan', 'execution'] as const).map((filter) => (
            <button
              key={filter}
              onClick={() => setActiveFilter(filter)}
              className={`px-3 py-1 text-xs rounded whitespace-nowrap transition-colors ${
                activeFilter === filter
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {filter.charAt(0).toUpperCase() + filter.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Memory List */}
      <div className="flex-1 overflow-y-auto p-2">
        {filteredMemories.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm">
            <Database className="w-8 h-8 mb-2 opacity-50" />
            <p>No memories found</p>
          </div>
        ) : (
          <div className="space-y-1">
            {filteredMemories.map((memory) => (
              <div
                key={memory.id}
                onClick={() => setSelectedMemory(memory)}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  selectedMemory?.id === memory.id
                    ? 'bg-purple-500/20 border border-purple-500'
                    : 'bg-gray-700/50 hover:bg-gray-700 border border-transparent'
                }`}
                role="button"
                tabIndex={0}
                aria-label={`Memory ${memory.id}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {getModalityIcon(memory.modality)}
                    <span className="text-xs text-gray-400">{memory.id}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-400">
                    {memory.confidence !== undefined && (
                      <span className="text-green-400">{Math.round(memory.confidence * 100)}%</span>
                    )}
                    <Clock className="w-3 h-3" />
                    {memory.timestamp.split(' ')[1]}
                  </div>
                </div>

                <div className="text-sm text-gray-200 mb-2 line-clamp-2">
                  {memory.content}
                </div>

                <div className="flex flex-wrap gap-1">
                  {memory.tags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center gap-1 px-2 py-0.5 bg-purple-500/20 text-purple-300 text-xs rounded"
                    >
                      <Tag className="w-3 h-3" />
                      {tag}
                    </span>
                  ))}
                </div>

                <div className="flex items-center gap-1 mt-2 text-xs text-gray-400">
                  <Eye className="w-3 h-3" />
                  {memory.witnesses} witnesses
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Memory Details */}
      {selectedMemory && (
        <div className="h-64 bg-gray-900 border-t border-gray-700 p-3 overflow-y-auto shrink-0 flex flex-col">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-gray-300">{selectedMemory.id}</h3>
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="text-xs text-gray-400 hover:text-gray-300 flex items-center gap-1"
              title="Show bitemporal history"
            >
              <History className="w-3 h-3" />
              History
            </button>
          </div>
          
          {/* Consciousness Awareness Full */}
          <div className="mb-3">
            <ConsciousnessAwareness compact={false} showHealth={true} showMemory={true} showGoals={true} showCognitive={false} />
          </div>
          
          {showHistory && historyVersions.length > 0 ? (
            <div className="space-y-2 mb-2">
              <div className="text-xs text-gray-500 mb-1 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                Bitemporal History ({historyVersions.length} versions)
              </div>
              {historyVersions.map((version) => (
                <div key={version.id} className="p-2 bg-gray-800 rounded text-xs">
                  <div className="text-gray-400 mb-1">{version.timestamp}</div>
                  <div className="text-gray-300">{version.content.substring(0, 100)}...</div>
                </div>
              ))}
            </div>
          ) : (
            <>
              <p className="text-xs text-gray-300 mb-2 whitespace-pre-wrap">{selectedMemory.content}</p>
              <div className="text-xs text-gray-400 space-y-1">
                <div>Modality: <span className="text-gray-300">{selectedMemory.modality}</span></div>
                <div>Timestamp: <span className="text-gray-300">{selectedMemory.timestamp}</span></div>
                {selectedMemory.confidence !== undefined && (
                  <div>Confidence (VIF): <span className="text-green-400">{Math.round(selectedMemory.confidence * 100)}%</span></div>
                )}
                <div>Witnesses: <span className="text-gray-300">{selectedMemory.witnesses}</span></div>
                {selectedMemory.atom_id && (
                  <div className="text-gray-500 text-xs mt-2">Atom ID: {selectedMemory.atom_id}</div>
                )}
              </div>
            </>
          )}
        </div>
      )}
          </>
        )}
      </div>
    </ErrorBoundary>
  )
}

