// NL Tags Explorer Panel - V2 Feature Implementation
// NL tag browser, validation, and coverage visualization

import React, { useState, useMemo, useCallback } from 'react'
import { BasePanel } from '../components/BasePanel'
import { Search, Tag, CheckCircle, XCircle, AlertCircle, FileText, Code, Hash } from 'lucide-react'
import { useHHNI } from '../hooks/useAIMOS'

interface NLTag {
  id: string
  tag: string
  system: string
  category: 'function' | 'component' | 'system' | 'protocol' | 'concept'
  file: string
  functionName: string
  description: string
  confidence: number
  validated: boolean
  issues?: string[]
  connections?: string[]
  intent?: string
  spec?: string
}

// Mock NL tag data (would be loaded from NL tag system or HHNI)
const mockNLTags: NLTag[] = [
  {
    id: 'vif-witness-001',
    tag: 'VIF-WITNESS-001',
    system: 'VIF',
    category: 'function',
    file: 'packages/vif/witness.py',
    functionName: 'create_witness',
    description: 'Create VIF witness envelope with complete provenance',
    confidence: 0.95,
    validated: true,
    connections: ['CMC-STORE-001'],
    intent: 'Enables deterministic replay',
    spec: 'witness_schema.json',
  },
  {
    id: 'cmc-store-001',
    tag: 'CMC-STORE-001',
    system: 'CMC',
    category: 'function',
    file: 'packages/cmc_service/store.py',
    functionName: 'store_atom',
    description: 'Store atom in CMC with bitemporal tracking',
    confidence: 0.92,
    validated: true,
    connections: ['VIF-WITNESS-001'],
    intent: 'Persistent memory storage',
    spec: 'atom_schema.json',
  },
  {
    id: 'seg-contradiction-001',
    tag: 'SEG-CONTRADICTION-001',
    system: 'SEG',
    category: 'function',
    file: 'packages/seg/contradiction.py',
    functionName: 'detect_contradictions',
    description: 'Detect contradictions in evidence graph',
    confidence: 0.88,
    validated: true,
    connections: ['SEG-EVIDENCE-001'],
    intent: 'Quality assurance',
    spec: 'contradiction_schema.json',
  },
  {
    id: 'hhni-search-001',
    tag: 'HHNI-SEARCH-001',
    system: 'HHNI',
    category: 'function',
    file: 'packages/hhni/search.py',
    functionName: 'search',
    description: 'Hierarchical search with confidence routing',
    confidence: 0.90,
    validated: false,
    issues: ['Missing intent tag', 'No spec reference'],
    connections: ['HHNI-RETRIEVE-001'],
  },
  {
    id: 'apoe-plan-001',
    tag: 'APOE-PLAN-001',
    system: 'APOE',
    category: 'function',
    file: 'packages/apoe_runner/plan.py',
    functionName: 'create_plan',
    description: 'Create execution plan with roles and gates',
    confidence: 0.87,
    validated: true,
    connections: ['APOE-EXECUTE-001'],
    intent: 'Orchestration',
    spec: 'plan_schema.json',
  },
]

export const NLTagsExplorerPanel: React.FC = () => {
  const { search } = useHHNI()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedSystem, setSelectedSystem] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [showValidatedOnly, setShowValidatedOnly] = useState(false)
  const [showIssuesOnly, setShowIssuesOnly] = useState(false)
  const [expandedTags, setExpandedTags] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Filter tags
  const filteredTags = useMemo(() => {
    let tags = mockNLTags
    
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      tags = tags.filter(tag =>
        tag.tag.toLowerCase().includes(query) ||
        tag.description.toLowerCase().includes(query) ||
        tag.functionName.toLowerCase().includes(query) ||
        tag.file.toLowerCase().includes(query)
      )
    }
    
    if (selectedSystem) {
      tags = tags.filter(tag => tag.system === selectedSystem)
    }
    
    if (selectedCategory) {
      tags = tags.filter(tag => tag.category === selectedCategory)
    }
    
    if (showValidatedOnly) {
      tags = tags.filter(tag => tag.validated)
    }
    
    if (showIssuesOnly) {
      tags = tags.filter(tag => tag.issues && tag.issues.length > 0)
    }
    
    return tags
  }, [searchQuery, selectedSystem, selectedCategory, showValidatedOnly, showIssuesOnly])
  
  // Get unique systems and categories
  const systems = useMemo(() => {
    return Array.from(new Set(mockNLTags.map(t => t.system))).sort()
  }, [])
  
  const categories = useMemo(() => {
    return Array.from(new Set(mockNLTags.map(t => t.category))).sort()
  }, [])
  
  // Calculate coverage metrics
  const coverageMetrics = useMemo(() => {
    const total = mockNLTags.length
    const validated = mockNLTags.filter(t => t.validated).length
    const withIssues = mockNLTags.filter(t => t.issues && t.issues.length > 0).length
    const coverage = total > 0 ? (validated / total) * 100 : 0
    
    return {
      total,
      validated,
      withIssues,
      coverage,
    }
  }, [])
  
  const toggleTag = useCallback((tagId: string) => {
    setExpandedTags(prev => {
      const next = new Set(prev)
      if (next.has(tagId)) {
        next.delete(tagId)
      } else {
        next.add(tagId)
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
    const avg = mockNLTags.reduce((sum, tag) => sum + tag.confidence, 0) / mockNLTags.length
    return avg
  }, [])
  
  const confidenceBand: 'A' | 'B' | 'C' = useMemo(() => {
    if (overallConfidence >= 0.90) return 'A'
    if (overallConfidence >= 0.70) return 'B'
    return 'C'
  }, [overallConfidence])
  
  return (
    <BasePanel
      id="nl-tags-explorer-panel"
      title="NL Tags Explorer"
      icon={Tag}
      description="NL tag browser, validation, and coverage visualization"
      loading={loading}
      error={error}
      empty={filteredTags.length === 0}
      emptyMessage={searchQuery ? `No tags found for "${searchQuery}"` : 'No tags available'}
      confidence={overallConfidence}
      confidenceBand={confidenceBand}
      atomCount={mockNLTags.length}
      footerContent={
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>{filteredTags.length} of {mockNLTags.length} tags</span>
          <span>{coverageMetrics.coverage.toFixed(0)}% coverage</span>
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
            placeholder="Search NL tags..."
            className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-700 rounded text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>
      
      {/* Coverage Summary */}
      <div className="mb-4 p-3 bg-gray-900 border border-gray-700 rounded">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-semibold text-gray-200">Coverage</span>
          <span className="text-xs text-gray-400">{coverageMetrics.coverage.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-800 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all"
            style={{ width: `${coverageMetrics.coverage}%` }}
          />
        </div>
        <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
          <span>{coverageMetrics.validated} validated</span>
          <span>{coverageMetrics.withIssues} with issues</span>
        </div>
      </div>
      
      {/* Filters */}
      <div className="mb-4 space-y-2">
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
        
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-2 py-1 text-xs rounded ${
              !selectedCategory
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            All Categories
          </button>
          {categories.map(category => (
            <button
              key={category}
              onClick={() => setSelectedCategory(selectedCategory === category ? null : category)}
              className={`px-2 py-1 text-xs rounded capitalize ${
                selectedCategory === category
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {category}
            </button>
          ))}
        </div>
        
        <div className="flex gap-2">
          <label className="flex items-center gap-2 text-xs text-gray-400 cursor-pointer">
            <input
              type="checkbox"
              checked={showValidatedOnly}
              onChange={(e) => setShowValidatedOnly(e.target.checked)}
              className="rounded"
            />
            Validated only
          </label>
          <label className="flex items-center gap-2 text-xs text-gray-400 cursor-pointer">
            <input
              type="checkbox"
              checked={showIssuesOnly}
              onChange={(e) => setShowIssuesOnly(e.target.checked)}
              className="rounded"
            />
            Issues only
          </label>
        </div>
      </div>
      
      {/* Tags List */}
      <div className="space-y-2 max-h-[calc(100vh-500px)] overflow-auto">
        {filteredTags.map(tag => {
          const isExpanded = expandedTags.has(tag.id)
          
          return (
            <div
              key={tag.id}
              className="bg-gray-900 border border-gray-700 rounded p-3 hover:border-gray-600 transition-colors"
            >
              <button
                onClick={() => toggleTag(tag.id)}
                className="w-full flex items-start gap-2 text-left"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-mono font-semibold text-blue-400">{tag.tag}</span>
                    {tag.validated ? (
                      <CheckCircle className="w-4 h-4 text-green-400" />
                    ) : (
                      <XCircle className="w-4 h-4 text-red-400" />
                    )}
                    {tag.issues && tag.issues.length > 0 && (
                      <AlertCircle className="w-4 h-4 text-yellow-400" />
                    )}
                  </div>
                  
                  <div className="text-xs text-gray-400 mb-1">
                    <span className="font-medium">{tag.functionName}</span> in{' '}
                    <span className="text-gray-500">{tag.file}</span>
                  </div>
                  
                  <div className="text-xs text-gray-300 mb-2">{tag.description}</div>
                  
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`px-1.5 py-0.5 text-xs rounded ${
                      tag.system === 'VIF' ? 'bg-blue-900/30 text-blue-300' :
                      tag.system === 'CMC' ? 'bg-green-900/30 text-green-300' :
                      tag.system === 'SEG' ? 'bg-purple-900/30 text-purple-300' :
                      tag.system === 'HHNI' ? 'bg-yellow-900/30 text-yellow-300' :
                      'bg-gray-700 text-gray-300'
                    }`}>
                      {tag.system}
                    </span>
                    <span className="px-1.5 py-0.5 text-xs rounded bg-gray-800 text-gray-400 capitalize">
                      {tag.category}
                    </span>
                    <span className="px-1.5 py-0.5 text-xs rounded bg-gray-800 text-gray-400">
                      {(tag.confidence * 100).toFixed(0)}% confidence
                    </span>
                  </div>
                  
                  {isExpanded && (
                    <div className="mt-3 space-y-2 pt-3 border-t border-gray-700">
                      {tag.intent && (
                        <div>
                          <div className="text-xs text-gray-400 mb-1">Intent:</div>
                          <div className="text-xs text-gray-300">{tag.intent}</div>
                        </div>
                      )}
                      
                      {tag.spec && (
                        <div>
                          <div className="text-xs text-gray-400 mb-1 flex items-center gap-1">
                            <FileText className="w-3 h-3" />
                            Spec:
                          </div>
                          <div className="text-xs text-blue-400">{tag.spec}</div>
                        </div>
                      )}
                      
                      {tag.connections && tag.connections.length > 0 && (
                        <div>
                          <div className="text-xs text-gray-400 mb-1 flex items-center gap-1">
                            <Hash className="w-3 h-3" />
                            Connections:
                          </div>
                          <div className="flex flex-wrap gap-1">
                            {tag.connections.map((conn, idx) => (
                              <span
                                key={idx}
                                className="px-2 py-0.5 bg-gray-800 text-gray-300 rounded text-xs cursor-pointer hover:bg-gray-700"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  setSearchQuery(conn)
                                }}
                              >
                                {conn}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {tag.issues && tag.issues.length > 0 && (
                        <div>
                          <div className="text-xs text-yellow-400 mb-1 flex items-center gap-1">
                            <AlertCircle className="w-3 h-3" />
                            Issues:
                          </div>
                          <ul className="list-disc list-inside text-xs text-gray-300 space-y-1">
                            {tag.issues.map((issue, idx) => (
                              <li key={idx}>{issue}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </button>
            </div>
          )
        })}
      </div>
    </BasePanel>
  )
}

