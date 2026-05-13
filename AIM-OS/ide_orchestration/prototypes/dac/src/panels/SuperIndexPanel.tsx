// Super Index Panel - V2 Feature Implementation
// Hierarchical navigation of AIM-OS concepts from SUPER_INDEX.md

import React, { useState, useMemo, useCallback, useEffect } from 'react'
import { BasePanel } from '../components/BasePanel'
import { Search, BookOpen, FileText, Code, Link, ChevronRight, ChevronDown, Hash, RefreshCw } from 'lucide-react'
import { superIndexService } from '../services/SuperIndexService'
import { useHHNI } from '../hooks/useAIMOS'

interface ConceptEntry {
  name: string
  what: string
  where: string[]
  code?: string[]
  related?: string[]
  letter: string
}

/**
 * Parse SUPER_INDEX.md content to extract concepts
 */
function parseSuperIndexContent(content: string): ConceptEntry[] {
  const concepts: ConceptEntry[] = []
  
  // Pattern: **Concept Name:** or **Concept Name (Additional Info):**
  const conceptPattern = /^\*\*([^*]+?):\*\*/gm
  const lines = content.split('\n')
  
  let currentConcept: Partial<ConceptEntry> | null = null
  let currentSection: 'what' | 'where' | 'code' | 'related' | null = null
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const trimmed = line.trim()
    
    // Check for new concept
    const conceptMatch = trimmed.match(/^\*\*([^*]+?):\*\*/)
    if (conceptMatch) {
      // Save previous concept
      if (currentConcept && currentConcept.name && currentConcept.what) {
        const letter = currentConcept.name.charAt(0).toUpperCase()
        concepts.push({
          name: currentConcept.name,
          what: currentConcept.what,
          where: currentConcept.where || [],
          code: currentConcept.code,
          related: currentConcept.related,
          letter: /[A-Z]/.test(letter) ? letter : '#'
        })
      }
      
      // Start new concept
      currentConcept = {
        name: conceptMatch[1].trim(),
        where: [],
        code: [],
        related: []
      }
      currentSection = null
      continue
    }
    
    // Check for section headers
    if (trimmed.startsWith('- **What:**')) {
      currentSection = 'what'
      currentConcept!.what = trimmed.replace('- **What:**', '').trim()
      continue
    } else if (trimmed.startsWith('- **Where:**')) {
      currentSection = 'where'
      continue
    } else if (trimmed.startsWith('- **Code:**')) {
      currentSection = 'code'
      const codeText = trimmed.replace('- **Code:**', '').trim()
      if (codeText) {
        currentConcept!.code = currentConcept!.code || []
        currentConcept!.code.push(codeText)
      }
      continue
    } else if (trimmed.startsWith('- **Related:**')) {
      currentSection = 'related'
      const relatedText = trimmed.replace('- **Related:**', '').trim()
      if (relatedText) {
        currentConcept!.related = currentConcept!.related || []
        currentConcept!.related.push(...relatedText.split(',').map(r => r.trim()))
      }
      continue
    }
    
    // Parse content based on current section
    if (currentSection === 'where' && trimmed.startsWith('- `')) {
      // Extract file path: - `path/to/file.md` (description)
      const match = trimmed.match(/- `([^`]+)`/)
      if (match) {
        currentConcept!.where = currentConcept!.where || []
        currentConcept!.where.push(match[1])
      }
    } else if (currentSection === 'code' && trimmed.startsWith('- `')) {
      // Extract code path: - `path/to/code/` (description)
      const match = trimmed.match(/- `([^`]+)`/)
      if (match) {
        currentConcept!.code = currentConcept!.code || []
        currentConcept!.code.push(match[1])
      }
    } else if (currentSection === 'related' && trimmed.includes(',')) {
      // Related concepts on same line
      const relatedItems = trimmed.split(',').map(r => r.trim())
      currentConcept!.related = currentConcept!.related || []
      currentConcept!.related.push(...relatedItems)
    }
  }
  
  // Save last concept
  if (currentConcept && currentConcept.name && currentConcept.what) {
    const letter = currentConcept.name.charAt(0).toUpperCase()
    concepts.push({
      name: currentConcept.name,
      what: currentConcept.what,
      where: currentConcept.where || [],
      code: currentConcept.code,
      related: currentConcept.related,
      letter: /[A-Z]/.test(letter) ? letter : '#'
    })
  }
  
  return concepts
}

// Fallback mock data (used if API fails)
const mockConcepts: ConceptEntry[] = [
  {
    name: 'APOE (AI-Powered Orchestration Engine)',
    what: 'Compiles reasoning into executable plans (DAGs) with roles, budgets, gates',
    where: [
      'systems/apoe/README.md',
      'systems/apoe/L1_overview.md',
      'systems/apoe/L2_architecture.md',
      'systems/apoe/L3_detailed.md',
    ],
    code: ['packages/apoe_runner/'],
    related: ['8 roles', 'ACL', 'DAG execution', 'gates', 'budget'],
    letter: 'A',
  },
  {
    name: 'CMC (Conscious Memory Core)',
    what: 'Bitemporal storage system for all AIM-OS data',
    where: [
      'systems/cmc/README.md',
      'systems/cmc/L1_overview.md',
      'systems/cmc/L2_architecture.md',
    ],
    code: ['packages/cmc_service/'],
    related: ['Atoms', 'Bitemporal', 'Snapshots', 'Modality'],
    letter: 'C',
  },
  {
    name: 'VIF (Verifiable Intelligence Framework)',
    what: 'Witness envelopes for provenance, replay, and uncertainty quantification',
    where: [
      'systems/vif/README.md',
      'systems/vif/L1_overview.md',
      'systems/vif/L2_architecture.md',
    ],
    code: ['packages/vif/'],
    related: ['Witnesses', 'Confidence', 'Kappa-gating', 'Calibration'],
    letter: 'V',
  },
  {
    name: 'SEG (Shared Evidence Graph)',
    what: 'Knowledge graph connecting evidence, claims, and contradictions',
    where: [
      'systems/seg/README.md',
      'systems/seg/L1_overview.md',
      'systems/seg/L2_architecture.md',
    ],
    code: ['packages/seg/'],
    related: ['Contradictions', 'Evidence', 'Knowledge synthesis'],
    letter: 'S',
  },
  {
    name: 'HHNI (Hierarchical Human-Native Interface)',
    what: 'Retrieval system using hierarchical paths for human-natural navigation',
    where: [
      'systems/hhni/README.md',
      'systems/hhni/L1_overview.md',
      'systems/hhni/L2_architecture.md',
    ],
    code: ['packages/hhni/'],
    related: ['Search', 'Retrieval', 'Hierarchical paths'],
    letter: 'H',
  },
  {
    name: 'TCS (Timeline Context System)',
    what: 'Bitemporal timeline tracking for perfect recall and replay',
    where: [
      'systems/tcs/README.md',
      'systems/tcs/L1_overview.md',
    ],
    code: ['packages/tcs/'],
    related: ['Timeline', 'Bitemporal', 'Perfect recall'],
    letter: 'T',
  },
  {
    name: 'CAS (Cognitive Analysis System)',
    what: 'Meta-cognitive system for AI to examine own cognitive processes',
    where: [
      'systems/cognitive_analysis/README.md',
      'systems/cognitive_analysis/L1_overview.md',
    ],
    code: ['packages/cas/'],
    related: ['Consciousness', 'Meta-cognition', 'Introspection'],
    letter: 'C',
  },
  {
    name: 'SDF-CVF (Semantic Data Flow - Contextual Validation Framework)',
    what: 'Quality validation framework with quartet parity',
    where: [
      'systems/sdfcvf/README.md',
      'systems/sdfcvf/L1_overview.md',
    ],
    code: ['packages/parity_policy/'],
    related: ['Quartet parity', 'Validation', 'Quality gates'],
    letter: 'S',
  },
]

export const SuperIndexPanel: React.FC = () => {
  const { search } = useHHNI()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedLetter, setSelectedLetter] = useState<string | null>(null)
  const [expandedConcepts, setExpandedConcepts] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [concepts, setConcepts] = useState<ConceptEntry[]>(mockConcepts)
  const [usingMockData, setUsingMockData] = useState(false)
  
  // Load SUPER_INDEX on mount
  useEffect(() => {
    let mounted = true
    
    async function loadSuperIndex() {
      setLoading(true)
      setError(null)
      
      try {
        const result = await superIndexService.loadSuperIndex()
        
        if (!mounted) return
        
        if (result.success && result.data) {
          // Parse content to extract concepts
          const parsedConcepts = parseSuperIndexContent(result.data.content)
          
          if (parsedConcepts.length > 0) {
            setConcepts(parsedConcepts)
            setUsingMockData(false)
          } else {
            // Fallback to mock if parsing fails
            setConcepts(mockConcepts)
            setUsingMockData(true)
            setError('Failed to parse SUPER_INDEX content, using mock data')
          }
        } else {
          // Fallback to mock data
          setConcepts(mockConcepts)
          setUsingMockData(true)
          setError(result.error || 'Failed to load SUPER_INDEX, using mock data')
        }
      } catch (err) {
        if (!mounted) return
        setConcepts(mockConcepts)
        setUsingMockData(true)
        setError(err instanceof Error ? err.message : 'Failed to load SUPER_INDEX, using mock data')
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    }
    
    loadSuperIndex()
    
    return () => {
      mounted = false
    }
  }, [])
  
  // Filter concepts by search query
  const filteredConcepts = useMemo(() => {
    if (!searchQuery.trim()) return concepts
    
    const query = searchQuery.toLowerCase()
    return concepts.filter(concept =>
      concept.name.toLowerCase().includes(query) ||
      concept.what.toLowerCase().includes(query) ||
      concept.related?.some(r => r.toLowerCase().includes(query))
    )
  }, [searchQuery, concepts])
  
  // Group concepts by letter
  const conceptsByLetter = useMemo(() => {
    const grouped: Record<string, ConceptEntry[]> = {}
    filteredConcepts.forEach(concept => {
      const letter = concept.letter
      if (!grouped[letter]) {
        grouped[letter] = []
      }
      grouped[letter].push(concept)
    })
    return grouped
  }, [filteredConcepts])
  
  // Get unique letters
  const letters = useMemo(() => {
    return Object.keys(conceptsByLetter).sort()
  }, [conceptsByLetter])
  
  const toggleConcept = useCallback((conceptName: string) => {
    setExpandedConcepts(prev => {
      const next = new Set(prev)
      if (next.has(conceptName)) {
        next.delete(conceptName)
      } else {
        next.add(conceptName)
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
    // Average confidence of concepts (mock)
    return 0.90
  }, [])
  
  const confidenceBand: 'A' | 'B' | 'C' = useMemo(() => {
    if (overallConfidence >= 0.90) return 'A'
    if (overallConfidence >= 0.70) return 'B'
    return 'C'
  }, [overallConfidence])
  
  const totalConcepts = concepts.length
  const displayedConcepts = filteredConcepts.length
  
  const handleRefresh = useCallback(async () => {
    superIndexService.clearCache()
    setLoading(true)
    setError(null)
    
    try {
      const result = await superIndexService.loadSuperIndex()
      if (result.success && result.data) {
        const parsedConcepts = parseSuperIndexContent(result.data.content)
        if (parsedConcepts.length > 0) {
          setConcepts(parsedConcepts)
          setUsingMockData(false)
          setError(null)
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Refresh failed')
    } finally {
      setLoading(false)
    }
  }, [])
  
  return (
    <BasePanel
      id="super-index-panel"
      title="Super Index"
      icon={BookOpen}
      description="Complete concept map for AIM-OS - Navigate all concepts and their documentation"
      loading={loading}
      error={error}
      empty={displayedConcepts === 0}
      emptyMessage={searchQuery ? `No concepts found for "${searchQuery}"` : 'No concepts available'}
      confidence={overallConfidence}
      confidenceBand={confidenceBand}
      atomCount={totalConcepts}
      footerContent={
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center gap-2">
            <span>{displayedConcepts} of {totalConcepts} concepts</span>
            {usingMockData && (
              <span className="text-yellow-500">(mock data)</span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <span>{letters.length} letters</span>
            <button
              onClick={handleRefresh}
              className="p-1 hover:bg-gray-700 rounded"
              title="Refresh data"
            >
              <RefreshCw className="w-3 h-3" />
            </button>
          </div>
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
            placeholder="Search concepts..."
            className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-700 rounded text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>
      
      {/* Letter Navigation */}
      {!searchQuery && (
        <div className="mb-4 flex flex-wrap gap-1">
          {letters.map(letter => (
            <button
              key={letter}
              onClick={() => setSelectedLetter(selectedLetter === letter ? null : letter)}
              className={`px-2 py-1 text-xs rounded ${
                selectedLetter === letter
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {letter}
            </button>
          ))}
        </div>
      )}
      
      {/* Concepts List */}
      <div className="space-y-2 max-h-[calc(100vh-300px)] overflow-auto">
        {Object.entries(conceptsByLetter)
          .filter(([letter]) => !selectedLetter || letter === selectedLetter)
          .map(([letter, concepts]) => (
            <div key={letter} className="space-y-2">
              {!selectedLetter && (
                <div className="sticky top-0 bg-gray-800 py-1 px-2 text-sm font-semibold text-gray-400 flex items-center gap-2">
                  <Hash className="w-4 h-4" />
                  {letter}
                </div>
              )}
              
              {concepts.map(concept => {
                const isExpanded = expandedConcepts.has(concept.name)
                
                return (
                  <div
                    key={concept.name}
                    className="bg-gray-900 border border-gray-700 rounded p-3 hover:border-gray-600 transition-colors"
                  >
                    <button
                      onClick={() => toggleConcept(concept.name)}
                      className="w-full flex items-start gap-2 text-left"
                    >
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-gray-200 mb-1">
                          {concept.name}
                        </div>
                        {isExpanded && (
                          <div className="mt-2 space-y-3 text-xs">
                            <div>
                              <div className="text-gray-400 mb-1">What:</div>
                              <div className="text-gray-300">{concept.what}</div>
                            </div>
                            
                            {concept.where && concept.where.length > 0 && (
                              <div>
                                <div className="text-gray-400 mb-1 flex items-center gap-1">
                                  <FileText className="w-3 h-3" />
                                  Where:
                                </div>
                                <div className="space-y-1">
                                  {concept.where.map((path, idx) => (
                                    <div
                                      key={idx}
                                      className="text-blue-400 hover:text-blue-300 cursor-pointer flex items-center gap-1"
                                      onClick={(e) => {
                                        e.stopPropagation()
                                        // Would open file in editor
                                        console.log('Open:', path)
                                      }}
                                    >
                                      <Link className="w-3 h-3" />
                                      {path}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                            
                            {concept.code && concept.code.length > 0 && (
                              <div>
                                <div className="text-gray-400 mb-1 flex items-center gap-1">
                                  <Code className="w-3 h-3" />
                                  Code:
                                </div>
                                <div className="space-y-1">
                                  {concept.code.map((path, idx) => (
                                    <div
                                      key={idx}
                                      className="text-purple-400 hover:text-purple-300 cursor-pointer flex items-center gap-1"
                                      onClick={(e) => {
                                        e.stopPropagation()
                                        // Would open code location
                                        console.log('Open code:', path)
                                      }}
                                    >
                                      <Code className="w-3 h-3" />
                                      {path}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                            
                            {concept.related && concept.related.length > 0 && (
                              <div>
                                <div className="text-gray-400 mb-1">Related:</div>
                                <div className="flex flex-wrap gap-1">
                                  {concept.related.map((rel, idx) => (
                                    <span
                                      key={idx}
                                      className="px-2 py-0.5 bg-gray-800 text-gray-300 rounded text-xs cursor-pointer hover:bg-gray-700"
                                      onClick={(e) => {
                                        e.stopPropagation()
                                        setSearchQuery(rel)
                                      }}
                                    >
                                      {rel}
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
                )
              })}
            </div>
          ))}
      </div>
    </BasePanel>
  )
}

