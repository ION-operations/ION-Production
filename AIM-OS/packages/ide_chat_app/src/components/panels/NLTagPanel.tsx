/**
 * NL Tag Panel Component
 * 
 * Phase 2.2: Right Drawer Panels
 * 
 * Natural Language Tag management and visualization.
 * Features:
 * - Tag browser
 * - Tag search/filter
 * - Tag relationships
 * - Tag validation
 * - AIM-OS integration (NL Tag System, VIF validation, SEG relationships)
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react'
import { Tag, Search, CheckCircle2, AlertCircle, Link, FileCode, Zap, Database, Filter, Shield, TrendingUp, BarChart3, X, ExternalLink, ChevronRight, ChevronDown, Brain } from 'lucide-react'
import { useAIMOS } from '../../hooks/useAIMOS'
import { useDebounce } from '../../hooks/useDebounce'
import { LoadingState } from '../LoadingState'
import { ErrorBoundary } from '../ErrorBoundary'

interface NLTag {
  id: string
  tagId: string // e.g., "VIF-WITNESS-001"
  name: string
  description: string
  type: 'primary' | 'connect' | 'intent' | 'spec'
  system: string // e.g., "VIF", "CMC", "HHNI"
  filePath: string
  functionName: string
  confidence: number
  validated: boolean
  connections: string[] // Connected tag IDs
  quintetParity?: number // Quintet parity score (0-1)
  validationIssues?: string[]
  createdAt?: string
  updatedAt?: string
  cmcAtomId?: string // CMC integration
}

const mockTags: NLTag[] = [
  {
    id: 'tag-1',
    tagId: 'VIF-WITNESS-001',
    name: 'Create VIF witness envelope',
    description: 'Create VIF witness envelope with complete provenance for deterministic replay',
    type: 'primary',
    system: 'VIF',
    filePath: 'packages/vif/witness.py',
    functionName: 'create_witness',
    confidence: 0.95,
    validated: true,
    connections: ['VIF-CMC-001', 'VIF-DESIGN-003'],
    quintetParity: 0.96,
    createdAt: '2025-11-07T08:00:00Z',
    updatedAt: '2025-11-07T10:00:00Z',
    cmcAtomId: 'cmc-tag-001',
  },
  {
    id: 'tag-2',
    tagId: 'VIF-CMC-001',
    name: 'Witness stored in CMC',
    description: 'Witness stored in CMC for bitemporal tracking',
    type: 'connect',
    system: 'VIF',
    filePath: 'packages/vif/witness.py',
    functionName: 'create_witness',
    confidence: 0.98,
    validated: true,
    connections: ['VIF-WITNESS-001'],
    quintetParity: 0.98,
    createdAt: '2025-11-07T08:00:00Z',
    updatedAt: '2025-11-07T10:00:00Z',
    cmcAtomId: 'cmc-tag-002',
  },
  {
    id: 'tag-3',
    tagId: 'CMC-STORE-001',
    name: 'Store atom in CMC',
    description: 'Store atom in Context Memory Core with bitemporal versioning',
    type: 'primary',
    system: 'CMC',
    filePath: 'packages/cmc/store.py',
    functionName: 'store_atom',
    confidence: 0.99,
    validated: true,
    connections: ['CMC-HHNI-001'],
    quintetParity: 0.99,
    createdAt: '2025-11-07T07:00:00Z',
    updatedAt: '2025-11-07T09:30:00Z',
    cmcAtomId: 'cmc-tag-003',
  },
  {
    id: 'tag-4',
    tagId: 'HHNI-INDEX-001',
    name: 'Index atom in HHNI',
    description: 'Index atom in Hierarchical Hypergraph Neural Index',
    type: 'primary',
    system: 'HHNI',
    filePath: 'packages/hhni/index.py',
    functionName: 'index_atom',
    confidence: 0.97,
    validated: false,
    connections: ['CMC-STORE-001'],
    quintetParity: 0.85,
    validationIssues: ['Missing NL_TAG_INTENT', 'Low quintet parity'],
    createdAt: '2025-11-07T09:00:00Z',
    updatedAt: '2025-11-07T09:00:00Z',
  },
  {
    id: 'tag-5',
    tagId: 'VIF-DESIGN-003',
    name: 'Enables deterministic replay',
    description: 'Enables deterministic replay through cryptographic hash + snapshot',
    type: 'intent',
    system: 'VIF',
    filePath: 'packages/vif/witness.py',
    functionName: 'create_witness',
    confidence: 0.94,
    validated: true,
    connections: ['VIF-WITNESS-001'],
    quintetParity: 0.92,
    createdAt: '2025-11-07T08:00:00Z',
    updatedAt: '2025-11-07T10:00:00Z',
    cmcAtomId: 'cmc-tag-004',
  },
]

export const NLTagPanel: React.FC = () => {
  const [tags, setTags] = useState<NLTag[]>(mockTags)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedSystem, setSelectedSystem] = useState<'all' | string>('all')
  const [selectedType, setSelectedType] = useState<'all' | NLTag['type']>('all')
  const [selectedTag, setSelectedTag] = useState<NLTag | null>(null)
  const [showValidationOnly, setShowValidationOnly] = useState(false)
  const [expandedTag, setExpandedTag] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'list' | 'coverage'>('list')

  // Debounce search query for performance
  const debouncedSearchQuery = useDebounce(searchQuery, 300)

  const systems = ['all', ...Array.from(new Set(tags.map((tag) => tag.system)))]

  // Calculate coverage statistics
  const coverageStats = useMemo(() => {
    const total = tags.length
    const validated = tags.filter(t => t.validated).length
    const avgQuintetParity = tags.reduce((sum, t) => sum + (t.quintetParity || 0), 0) / total
    const avgConfidence = tags.reduce((sum, t) => sum + t.confidence, 0) / total
    const bySystem = systems.slice(1).map(system => ({
      system,
      total: tags.filter(t => t.system === system).length,
      validated: tags.filter(t => t.system === system && t.validated).length,
      avgParity: tags.filter(t => t.system === system).reduce((sum, t) => sum + (t.quintetParity || 0), 0) / tags.filter(t => t.system === system).length || 0,
    }))
    return { total, validated, avgQuintetParity, avgConfidence, bySystem }
  }, [tags, systems])

  const filteredTags = useMemo(() => {
    return tags.filter((tag) => {
      const matchesSearch =
        tag.tagId.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
        tag.name.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
        tag.description.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
        tag.filePath.toLowerCase().includes(debouncedSearchQuery.toLowerCase())
      const matchesSystem = selectedSystem === 'all' || tag.system === selectedSystem
      const matchesType = selectedType === 'all' || tag.type === selectedType
      const matchesValidation = !showValidationOnly || !tag.validated
      return matchesSearch && matchesSystem && matchesType && matchesValidation
    })
  }, [tags, debouncedSearchQuery, selectedSystem, selectedType, showValidationOnly])

  const getTypeIcon = (type: NLTag['type']) => {
    switch (type) {
      case 'primary':
        return <Tag className="w-4 h-4 text-blue-400" />
      case 'connect':
        return <Link className="w-4 h-4 text-green-400" />
      case 'intent':
        return <Zap className="w-4 h-4 text-purple-400" />
      case 'spec':
        return <Database className="w-4 h-4 text-yellow-400" />
      default:
        return <Tag className="w-4 h-4 text-gray-400" />
    }
  }

  const getSystemColor = (system: string) => {
    switch (system) {
      case 'VIF':
        return 'text-blue-400'
      case 'CMC':
        return 'text-green-400'
      case 'HHNI':
        return 'text-purple-400'
      case 'APOE':
        return 'text-yellow-400'
      default:
        return 'text-gray-400'
    }
  }

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-800" role="complementary" aria-label="NL Tag Panel">
        {loading.cmc || loading.hhni ? (
          <LoadingState message="Loading NL tags..." />
        ) : (
          <>
      {/* Header */}
      <div className="h-10 bg-gray-900 border-b border-gray-700 flex items-center justify-between px-3 shrink-0">
        <div className="flex items-center">
          <Tag className="w-4 h-4 mr-2 text-gray-400" />
          <span className="text-sm font-semibold text-gray-300">NL Tags</span>
          <span className="ml-2 px-2 py-0.5 bg-gray-700 text-gray-400 text-xs rounded">
            {filteredTags.length} {filteredTags.length === 1 ? 'tag' : 'tags'}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setViewMode(viewMode === 'list' ? 'coverage' : 'list')}
            className="p-1 text-gray-400 hover:text-gray-300 transition-colors"
            title={viewMode === 'list' ? 'Show Coverage' : 'Show List'}
          >
            {viewMode === 'list' ? <BarChart3 className="w-4 h-4" /> : <Tag className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="p-2 border-b border-gray-700 space-y-2 shrink-0">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search tags..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-2 py-1.5 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-500"
            aria-label="Search tags"
          />
        </div>
        <div className="flex gap-1 overflow-x-auto">
          {systems.map((system) => {
            const count = system === 'all' 
              ? tags.length 
              : tags.filter(t => t.system === system).length
            return (
              <button
                key={system}
                onClick={() => setSelectedSystem(system)}
                className={`px-2 py-1 text-xs rounded whitespace-nowrap flex items-center gap-1 ${
                  selectedSystem === system
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {system}
                <span className="opacity-75">({count})</span>
              </button>
            )
          })}
        </div>
        <div className="flex gap-1 overflow-x-auto">
          {['all', 'primary', 'connect', 'intent', 'spec'].map((type) => (
            <button
              key={type}
              onClick={() => setSelectedType(type as any)}
              className={`px-2 py-1 text-xs rounded whitespace-nowrap ${
                selectedType === type
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {type}
            </button>
          ))}
          <button
            onClick={() => setShowValidationOnly(!showValidationOnly)}
            className={`px-2 py-1 text-xs rounded whitespace-nowrap flex items-center gap-1 ${
              showValidationOnly
                ? 'bg-yellow-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <AlertCircle className="w-3 h-3" />
            Issues Only
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-2">
        {viewMode === 'coverage' ? (
          <div className="space-y-4">
            {/* Overall Statistics */}
            <div className="bg-gray-700/50 rounded p-3 border border-gray-700">
              <h3 className="text-sm font-semibold text-gray-300 mb-3">Overall Coverage</h3>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <div className="text-gray-400 mb-1">Total Tags</div>
                  <div className="text-2xl font-bold text-gray-300">{coverageStats.total}</div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Validated</div>
                  <div className="text-2xl font-bold text-green-400">{coverageStats.validated}</div>
                  <div className="text-gray-500">
                    {Math.round((coverageStats.validated / coverageStats.total) * 100)}%
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Avg Quintet Parity</div>
                  <div className="text-2xl font-bold text-purple-400">
                    {(coverageStats.avgQuintetParity * 100).toFixed(1)}%
                  </div>
                </div>
                <div>
                  <div className="text-gray-400 mb-1">Avg Confidence</div>
                  <div className="text-2xl font-bold text-blue-400">
                    {(coverageStats.avgConfidence * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>

            {/* By System */}
            <div className="bg-gray-700/50 rounded p-3 border border-gray-700">
              <h3 className="text-sm font-semibold text-gray-300 mb-3">Coverage by System</h3>
              <div className="space-y-2">
                {coverageStats.bySystem.map((stat) => (
                  <div key={stat.system}>
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-sm font-medium ${getSystemColor(stat.system)}`}>
                        {stat.system}
                      </span>
                      <span className="text-xs text-gray-400">
                        {stat.validated}/{stat.total} validated
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full"
                        style={{ width: `${(stat.validated / stat.total) * 100}%` }}
                      />
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      Quintet Parity: {(stat.avgParity * 100).toFixed(1)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : filteredTags.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm">
            <Tag className="w-8 h-8 mb-2 opacity-50" />
            <p>No tags found</p>
            {(searchQuery || selectedSystem !== 'all' || selectedType !== 'all' || showValidationOnly) && (
              <button
                onClick={() => {
                  setSearchQuery('')
                  setSelectedSystem('all')
                  setSelectedType('all')
                  setShowValidationOnly(false)
                }}
                className="mt-2 px-3 py-1 text-xs bg-blue-600 hover:bg-blue-700 rounded text-white"
              >
                Clear Filters
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-1">
            {filteredTags.map((tag) => {
              const isExpanded = expandedTag === tag.id
              return (
                <div
                  key={tag.id}
                  className={`rounded cursor-pointer transition-colors border ${
                    selectedTag?.id === tag.id
                      ? 'bg-blue-600/20 border-blue-500'
                      : 'bg-gray-700 hover:bg-gray-600 border-transparent'
                  }`}
                >
                  <div
                    className="p-2"
                    onClick={() => setSelectedTag(tag)}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      {getTypeIcon(tag.type)}
                      <span className="text-xs font-mono text-gray-400">{tag.tagId}</span>
                      {tag.validated ? (
                        <CheckCircle2 className="w-3 h-3 text-green-400" />
                      ) : (
                        <AlertCircle className="w-3 h-3 text-yellow-400" />
                      )}
                      {tag.quintetParity !== undefined && (
                        <span className={`text-xs px-1 py-0.5 rounded ${
                          tag.quintetParity >= 0.90 ? 'bg-green-600/20 text-green-400' :
                          tag.quintetParity >= 0.80 ? 'bg-yellow-600/20 text-yellow-400' :
                          'bg-red-600/20 text-red-400'
                        }`} title="Quintet Parity">
                          <Shield className="w-3 h-3 inline mr-0.5" />
                          {(tag.quintetParity * 100).toFixed(0)}%
                        </span>
                      )}
                      {tag.cmcAtomId && (
                        <span className="text-xs text-purple-400 flex items-center gap-0.5" title="CMC Atom ID">
                          <Brain className="w-3 h-3" />
                          CMC
                        </span>
                      )}
                      {tag.connections.length > 0 && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setExpandedTag(isExpanded ? null : tag.id)
                          }}
                          className="p-0.5 hover:bg-gray-600 rounded ml-auto"
                        >
                          {isExpanded ? (
                            <ChevronDown className="w-3 h-3 text-gray-400" />
                          ) : (
                            <ChevronRight className="w-3 h-3 text-gray-400" />
                          )}
                        </button>
                      )}
                    </div>
                    <div className="text-sm text-gray-300 mb-1">{tag.name}</div>
                    <div className="flex items-center gap-2 text-xs">
                      <span className={getSystemColor(tag.system)}>{tag.system}</span>
                      <span className="text-gray-500">•</span>
                      <span className="text-gray-500">{tag.functionName}</span>
                      <span className="text-gray-500">•</span>
                      <span className="text-green-400">{Math.round(tag.confidence * 100)}%</span>
                    </div>
                    {tag.validationIssues && tag.validationIssues.length > 0 && (
                      <div className="mt-1 text-xs text-yellow-400 flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" />
                        {tag.validationIssues.length} issue{tag.validationIssues.length !== 1 ? 's' : ''}
                      </div>
                    )}
                  </div>
                  {isExpanded && tag.connections.length > 0 && (
                    <div className="px-2 pb-2 border-t border-gray-700">
                      <div className="text-xs text-gray-400 mb-1 flex items-center gap-1">
                        <Link className="w-3 h-3" />
                        Connections ({tag.connections.length})
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {tag.connections.map(connId => {
                          const connTag = tags.find(t => t.tagId === connId)
                          return (
                            <button
                              key={connId}
                              onClick={(e) => {
                                e.stopPropagation()
                                const found = tags.find(t => t.tagId === connId)
                                if (found) setSelectedTag(found)
                              }}
                              className="px-1.5 py-0.5 bg-blue-600/20 text-blue-300 rounded text-xs hover:bg-blue-600/30"
                            >
                              {connId}
                            </button>
                          )
                        })}
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Tag Detail */}
      {selectedTag && (
        <div className="p-3 border-t border-gray-700 bg-gray-900 shrink-0 max-h-96 overflow-y-auto">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              {getTypeIcon(selectedTag.type)}
              <span className="text-sm font-mono text-white">{selectedTag.tagId}</span>
              {selectedTag.validated ? (
                <CheckCircle2 className="w-4 h-4 text-green-400" />
              ) : (
                <AlertCircle className="w-4 h-4 text-yellow-400" />
              )}
            </div>
            <div className="flex items-center gap-1">
              {selectedTag.filePath && (
                <a
                  href={`#${selectedTag.filePath}`}
                  className="p-1 text-gray-400 hover:text-gray-300 hover:bg-gray-800 rounded"
                  title="Go to file"
                >
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
              <button
                onClick={() => setSelectedTag(null)}
                className="text-gray-400 hover:text-gray-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
          <h3 className="text-sm font-semibold text-white mb-1">{selectedTag.name}</h3>
          <p className="text-xs text-gray-400 mb-2">{selectedTag.description}</p>
          <div className="space-y-1 text-xs text-gray-400">
            <div className="flex justify-between">
              <span>System:</span>
              <span className={getSystemColor(selectedTag.system)}>{selectedTag.system}</span>
            </div>
            <div className="flex justify-between">
              <span>Type:</span>
              <span className="text-gray-300 capitalize">{selectedTag.type}</span>
            </div>
            <div className="flex justify-between">
              <span>File:</span>
              <span className="text-gray-300 truncate max-w-[200px] font-mono" title={selectedTag.filePath}>
                {selectedTag.filePath}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Function:</span>
              <span className="text-gray-300 font-mono">{selectedTag.functionName}</span>
            </div>
            <div className="flex justify-between">
              <span>Confidence:</span>
              <span className="text-green-400">{Math.round(selectedTag.confidence * 100)}%</span>
            </div>
            {selectedTag.quintetParity !== undefined && (
              <div className="flex justify-between">
                <span>Quintet Parity:</span>
                <span className={`${
                  selectedTag.quintetParity >= 0.90 ? 'text-green-400' :
                  selectedTag.quintetParity >= 0.80 ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {(selectedTag.quintetParity * 100).toFixed(1)}%
                </span>
              </div>
            )}
            <div className="flex justify-between">
              <span>Validated:</span>
              <span className={selectedTag.validated ? 'text-green-400' : 'text-yellow-400'}>
                {selectedTag.validated ? 'Yes' : 'No'}
              </span>
            </div>
            {selectedTag.cmcAtomId && (
              <div className="flex justify-between">
                <span>CMC Atom:</span>
                <span className="text-purple-400 font-mono text-xs">{selectedTag.cmcAtomId.substring(0, 12)}...</span>
              </div>
            )}
            {selectedTag.createdAt && (
              <div className="flex justify-between">
                <span>Created:</span>
                <span className="text-gray-300">{new Date(selectedTag.createdAt).toLocaleDateString()}</span>
              </div>
            )}
            {selectedTag.validationIssues && selectedTag.validationIssues.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-700">
                <div className="font-semibold mb-1 text-yellow-400 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  Validation Issues:
                </div>
                <ul className="list-disc list-inside space-y-0.5">
                  {selectedTag.validationIssues.map((issue, idx) => (
                    <li key={idx} className="text-yellow-400">{issue}</li>
                  ))}
                </ul>
              </div>
            )}
            {selectedTag.connections.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-700">
                <div className="font-semibold mb-1 flex items-center gap-1">
                  <Link className="w-3 h-3" />
                  Connections ({selectedTag.connections.length}):
                </div>
                <div className="flex flex-wrap gap-1">
                  {selectedTag.connections.map((connId) => {
                    const connTag = tags.find(t => t.tagId === connId)
                    return (
                      <button
                        key={connId}
                        onClick={() => {
                          if (connTag) setSelectedTag(connTag)
                        }}
                        className="px-2 py-0.5 bg-blue-600/20 text-blue-300 rounded text-xs hover:bg-blue-600/30 transition-colors"
                      >
                        {connId}
                      </button>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
          </>
        )}
      </div>
    </ErrorBoundary>
  )
}

