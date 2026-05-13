/**
 * Component Library Panel Component
 * 
 * Phase 2.1: Left Drawer Panels
 * 
 * Browse and manage reusable components.
 * Features:
 * - Component search
 * - Component categories
 * - Component preview
 * - Usage examples
 * - AIM-OS integration (CMC storage, HHNI search, SEG relationships)
 */

import React, { useState, useMemo, useEffect, useCallback } from 'react'
import { Package, Search, Code, FileText, Layers, Star, Copy, Eye, TrendingUp, Brain, Shield, ExternalLink, ChevronRight, ChevronDown, Zap } from 'lucide-react'
import { useAIMOS } from '../../hooks/useAIMOS'
import { useDebounce } from '../../hooks/useDebounce'
import { ErrorBoundary } from '../ErrorBoundary'
import { LoadingState } from '../LoadingState'

interface Component {
  id: string
  name: string
  category: 'ui' | 'layout' | 'form' | 'data' | 'navigation' | 'feedback' | 'aimos'
  description: string
  usage: string
  props?: Record<string, any>
  isFavorite?: boolean
  usageCount?: number
  lastUsed?: string
  dependencies?: string[]
  documentation?: string
  examples?: string[]
  cmcAtomId?: string // CMC integration
  hhniTags?: string[] // HHNI semantic tags
  vifConfidence?: number // VIF confidence for component quality
}

const mockComponents: Component[] = [
  {
    id: 'button',
    name: 'Button',
    category: 'ui',
    description: 'Primary button component with variants',
    usage: "import { Button } from '@/components/ui/Button'",
    props: { variant: 'primary | secondary', size: 'sm | md | lg' },
    usageCount: 156,
    lastUsed: '2025-11-07T10:30:00Z',
    dependencies: ['react', 'lucide-react'],
    documentation: '/docs/components/button',
    examples: ['<Button variant="primary">Click me</Button>'],
    hhniTags: ['button', 'ui', 'interaction'],
    vifConfidence: 0.98,
  },
  {
    id: 'card',
    name: 'Card',
    category: 'ui',
    description: 'Container component with shadow and padding',
    usage: "import { Card } from '@/components/ui/Card'",
    usageCount: 89,
    lastUsed: '2025-11-07T09:15:00Z',
    dependencies: ['react'],
    documentation: '/docs/components/card',
    hhniTags: ['card', 'container', 'layout'],
    vifConfidence: 0.95,
  },
  {
    id: 'input',
    name: 'Input',
    category: 'form',
    description: 'Text input with validation',
    usage: "import { Input } from '@/components/form/Input'",
    props: { type: 'text | email | password', placeholder: 'string' },
    usageCount: 124,
    lastUsed: '2025-11-07T11:00:00Z',
    dependencies: ['react'],
    documentation: '/docs/components/input',
    examples: ['<Input type="text" placeholder="Enter text" />'],
    hhniTags: ['input', 'form', 'validation'],
    vifConfidence: 0.97,
  },
  {
    id: 'panel',
    name: 'Panel',
    category: 'layout',
    description: 'Resizable panel component',
    usage: "import { Panel } from '@/components/layout/Panel'",
    props: { size: 'number', minSize: 'number', maxSize: 'number' },
    usageCount: 45,
    lastUsed: '2025-11-07T08:45:00Z',
    dependencies: ['react', 'react-resizable-panels'],
    documentation: '/docs/components/panel',
    hhniTags: ['panel', 'layout', 'resizable'],
    vifConfidence: 0.92,
    isFavorite: true,
  },
  {
    id: 'table',
    name: 'Table',
    category: 'data',
    description: 'Data table with sorting and filtering',
    usage: "import { Table } from '@/components/data/Table'",
    usageCount: 67,
    lastUsed: '2025-11-07T07:30:00Z',
    dependencies: ['react'],
    documentation: '/docs/components/table',
    hhniTags: ['table', 'data', 'grid'],
    vifConfidence: 0.94,
  },
  {
    id: 'context-web',
    name: 'Context Web',
    category: 'aimos',
    description: 'Revolutionary AIM-OS context visualization component',
    usage: "import { ContextWebPanel } from '@/components/panels/ContextWebPanel'",
    props: { nodeId: 'string', depth: 'number' },
    usageCount: 12,
    lastUsed: '2025-11-07T10:00:00Z',
    dependencies: ['react', 'react-flow', '@aimos/hhni'],
    documentation: '/docs/components/context-web',
    examples: ['<ContextWebPanel nodeId="current-task" depth={3} />'],
    cmcAtomId: 'cmc-component-001',
    hhniTags: ['context', 'visualization', 'aimos', 'revolutionary'],
    vifConfidence: 0.99,
    isFavorite: true,
  },
  {
    id: 'evolution-explorer',
    name: 'Evolution Explorer',
    category: 'aimos',
    description: 'Bidirectional graph visualization for work evolution',
    usage: "import { EvolutionExplorer } from '@/components/AgentManagementDashboard/EvolutionExplorer'",
    props: { taskId: 'string', showDependencies: 'boolean' },
    usageCount: 8,
    lastUsed: '2025-11-07T09:00:00Z',
    dependencies: ['react', 'react-flow', '@aimos/tcs'],
    documentation: '/docs/components/evolution-explorer',
    cmcAtomId: 'cmc-component-002',
    hhniTags: ['evolution', 'graph', 'aimos', 'timeline'],
    vifConfidence: 0.98,
    isFavorite: true,
  },
]

export const ComponentLibraryPanel: React.FC = () => {
  const [components, setComponents] = useState<Component[]>(mockComponents)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<'all' | Component['category']>('all')
  const [selectedComponent, setSelectedComponent] = useState<Component | null>(null)
  const [favoritesOnly, setFavoritesOnly] = useState(false)
  const [expandedComponent, setExpandedComponent] = useState<string | null>(null)
  const [showDetails, setShowDetails] = useState(false)

  // Debounce search query for performance
  const debouncedSearchQuery = useDebounce(searchQuery, 300)

  // AIM-OS integration
  const { cmc, hhni, vif, seg, isConnected, useMockData, loading } = useAIMOS()

  // Load components from AIM-OS and track VIF confidence
  useEffect(() => {
    const loadComponents = async () => {
      if (!useMockData && isConnected) {
        try {
          // Load components from CMC
          const atoms = await cmc.retrieve('component', 50)
          const loadedComponents: Component[] = atoms.map(atom => ({
            id: atom.id,
            name: atom.content?.inline?.name || atom.id,
            category: atom.tags?.category || 'ui',
            description: atom.content?.inline?.description || '',
            usage: atom.content?.inline?.usage || '',
            props: atom.content?.inline?.props,
            usageCount: atom.content?.inline?.usageCount || 0,
            lastUsed: atom.created_at,
            dependencies: atom.content?.inline?.dependencies || [],
            documentation: atom.content?.inline?.documentation,
            examples: atom.content?.inline?.examples || [],
            cmcAtomId: atom.id,
            hhniTags: Object.keys(atom.tags || {}),
            vifConfidence: atom.witness?.uncertainty_band === 'green' ? 0.95 :
                          atom.witness?.uncertainty_band === 'yellow' ? 0.85 : 0.75,
          }))
          
          if (loadedComponents.length > 0) {
            setComponents(loadedComponents)
          }
        } catch (error) {
          console.warn('Failed to load components from AIM-OS, using mock data', error)
        }
      }
    }
    
    loadComponents()
  }, [cmc, useMockData, isConnected])

  // Track VIF confidence for components
  useEffect(() => {
    const trackConfidences = async () => {
      if (!useMockData && isConnected) {
        for (const comp of components) {
          if (comp.vifConfidence === undefined) {
            try {
              await vif.trackConfidence(
                `Component: ${comp.name}`,
                0.90, // Default confidence
                `Component category: ${comp.category}, Usage count: ${comp.usageCount || 0}`
              )
            } catch (err) {
              console.warn(`Failed to track confidence for component ${comp.id}:`, err)
            }
          }
        }
      }
    }
    
    if (components.length > 0) {
      trackConfidences()
    }
  }, [components, vif, useMockData, isConnected])

  const filteredComponents = useMemo(() => {
    return components.filter(comp => {
      const matchesSearch = debouncedSearchQuery === '' ||
        comp.name.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
        comp.description.toLowerCase().includes(debouncedSearchQuery.toLowerCase()) ||
        comp.hhniTags?.some(tag => tag.toLowerCase().includes(debouncedSearchQuery.toLowerCase()))
      const matchesCategory = selectedCategory === 'all' || comp.category === selectedCategory
      const matchesFavorites = !favoritesOnly || comp.isFavorite
      return matchesSearch && matchesCategory && matchesFavorites
    })
  }, [components, debouncedSearchQuery, selectedCategory, favoritesOnly])

  const handleCopyUsage = useCallback((usage: string) => {
    navigator.clipboard.writeText(usage)
  }, [])

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-800" role="complementary" aria-label="Component Library">
        {loading.cmc || loading.hhni ? (
          <LoadingState message="Loading components..." />
        ) : (
          <>
      {/* Header */}
      <div className="h-10 bg-gray-900 border-b border-gray-700 flex items-center px-3 shrink-0">
        <Package className="w-4 h-4 mr-2 text-gray-400" />
        <span className="text-sm font-semibold text-gray-300">Component Library</span>
      </div>

      {/* Search */}
      <div className="px-2 py-2 border-b border-gray-700 shrink-0">
        <div className="relative">
          <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search components..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-2 py-1.5 bg-gray-900 border border-gray-700 rounded text-sm text-gray-300 placeholder-gray-500 focus:outline-none focus:border-blue-500"
            aria-label="Search components"
          />
        </div>
      </div>

      {/* Categories */}
      <div className="px-2 py-2 border-b border-gray-700 shrink-0">
        <div className="flex gap-1 overflow-x-auto">
          {(['all', 'ui', 'layout', 'form', 'data', 'navigation', 'feedback', 'aimos'] as const).map((cat) => {
            const count = cat === 'all' 
              ? components.length 
              : components.filter(c => c.category === cat).length
            return (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1 text-xs rounded whitespace-nowrap transition-colors flex items-center gap-1 ${
                  selectedCategory === cat
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {cat === 'aimos' && <Brain className="w-3 h-3" />}
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
                <span className="opacity-75">({count})</span>
              </button>
            )
          })}
        </div>
        <div className="flex items-center justify-between mt-2">
          <button
            onClick={() => setFavoritesOnly(!favoritesOnly)}
            className={`px-2 py-1 text-xs rounded flex items-center gap-1 ${
              favoritesOnly
                ? 'bg-yellow-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <Star className="w-3 h-3" />
            Favorites Only
          </button>
        </div>
      </div>

      {/* Component List */}
      <div className="flex-1 overflow-y-auto p-2">
        {filteredComponents.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-500 text-sm">
            <Package className="w-8 h-8 mb-2 opacity-50" />
            <p>No components found</p>
            {(searchQuery || selectedCategory !== 'all' || favoritesOnly) && (
              <button
                onClick={() => {
                  setSearchQuery('')
                  setSelectedCategory('all')
                  setFavoritesOnly(false)
                }}
                className="mt-2 px-3 py-1 text-xs bg-blue-600 hover:bg-blue-700 rounded text-white"
              >
                Clear Filters
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-1">
            {filteredComponents.map((comp) => {
              const isExpanded = expandedComponent === comp.id
              return (
                <div
                  key={comp.id}
                  className={`rounded cursor-pointer transition-colors border ${
                    selectedComponent?.id === comp.id
                      ? 'bg-blue-600/20 border-blue-500'
                      : 'bg-gray-700/50 hover:bg-gray-700 border-transparent'
                  }`}
                >
                  <div
                    className="p-2"
                    onClick={() => setSelectedComponent(comp)}
                    role="button"
                    tabIndex={0}
                    aria-label={`Component ${comp.name}`}
                  >
                    <div className="flex items-center gap-2">
                      {comp.category === 'aimos' ? (
                        <Brain className="w-4 h-4 text-purple-400" />
                      ) : (
                        <Code className="w-4 h-4 text-gray-400" />
                      )}
                      <span className="text-sm text-gray-300 font-medium flex-1">{comp.name}</span>
                      <div className="flex items-center gap-1">
                        {comp.isFavorite && (
                          <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                        )}
                        {comp.usageCount !== undefined && (
                          <span className="text-xs text-gray-500 flex items-center gap-0.5" title="Usage count">
                            <TrendingUp className="w-3 h-3" />
                            {comp.usageCount}
                          </span>
                        )}
                        {comp.vifConfidence !== undefined && (
                          <span className={`text-xs px-1 py-0.5 rounded ${
                            comp.vifConfidence >= 0.95 ? 'bg-green-600/20 text-green-400' :
                            comp.vifConfidence >= 0.90 ? 'bg-yellow-600/20 text-yellow-400' :
                            'bg-red-600/20 text-red-400'
                          }`} title="VIF Confidence">
                            <Shield className="w-3 h-3 inline mr-0.5" />
                            {(comp.vifConfidence * 100).toFixed(0)}%
                          </span>
                        )}
                        {comp.dependencies && comp.dependencies.length > 0 && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              setExpandedComponent(isExpanded ? null : comp.id)
                            }}
                            className="p-0.5 hover:bg-gray-600 rounded"
                          >
                            {isExpanded ? (
                              <ChevronDown className="w-3 h-3 text-gray-400" />
                            ) : (
                              <ChevronRight className="w-3 h-3 text-gray-400" />
                            )}
                          </button>
                        )}
                      </div>
                    </div>
                    <p className="text-xs text-gray-400 mt-1">{comp.description}</p>
                    {comp.hhniTags && comp.hhniTags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {comp.hhniTags.slice(0, 3).map(tag => (
                          <span key={tag} className="px-1 py-0.5 bg-gray-800 text-xs text-gray-500 rounded">
                            {tag}
                          </span>
                        ))}
                        {comp.hhniTags.length > 3 && (
                          <span className="text-xs text-gray-500">+{comp.hhniTags.length - 3}</span>
                        )}
                      </div>
                    )}
                  </div>
                  {isExpanded && comp.dependencies && (
                    <div className="px-2 pb-2 border-t border-gray-700">
                      <div className="text-xs text-gray-400 mb-1">Dependencies:</div>
                      <div className="flex flex-wrap gap-1">
                        {comp.dependencies.map(dep => (
                          <span key={dep} className="px-1.5 py-0.5 bg-gray-800 text-xs text-gray-400 rounded">
                            {dep}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Component Details */}
      {selectedComponent && (
        <div className={`bg-gray-900 border-t border-gray-700 flex flex-col shrink-0 ${showDetails ? 'h-96' : 'h-48'}`}>
          <div className="p-3 border-b border-gray-700 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold text-gray-300">{selectedComponent.name}</h3>
              {selectedComponent.isFavorite && (
                <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
              )}
              {selectedComponent.cmcAtomId && (
                <span className="text-xs text-purple-400 flex items-center gap-1" title="CMC Atom ID">
                  <Brain className="w-3 h-3" />
                  CMC
                </span>
              )}
              {selectedComponent.vifConfidence !== undefined && (
                <span className={`text-xs px-1.5 py-0.5 rounded ${
                  selectedComponent.vifConfidence >= 0.95 ? 'bg-green-600/20 text-green-400' :
                  selectedComponent.vifConfidence >= 0.90 ? 'bg-yellow-600/20 text-yellow-400' :
                  'bg-red-600/20 text-red-400'
                }`}>
                  VIF: {(selectedComponent.vifConfidence * 100).toFixed(0)}%
                </span>
              )}
            </div>
            <div className="flex items-center gap-1">
              {selectedComponent.documentation && (
                <a
                  href={selectedComponent.documentation}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-1 text-gray-400 hover:text-gray-300 hover:bg-gray-800 rounded"
                  title="View documentation"
                >
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
              <button
                onClick={() => setShowDetails(!showDetails)}
                className="p-1 text-gray-400 hover:text-gray-300 hover:bg-gray-800 rounded"
                title={showDetails ? 'Hide details' : 'Show details'}
              >
                {showDetails ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
              </button>
              <button
                onClick={() => handleCopyUsage(selectedComponent.usage)}
                className="p-1 text-gray-400 hover:text-gray-300 hover:bg-gray-800 rounded"
                aria-label="Copy usage code"
                title="Copy import"
              >
                <Copy className="w-4 h-4" />
              </button>
            </div>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-3">
            <p className="text-xs text-gray-400">{selectedComponent.description}</p>
            <div className="bg-gray-800 p-2 rounded text-xs font-mono text-gray-300">
              {selectedComponent.usage}
            </div>
            {selectedComponent.props && (
              <div className="text-xs">
                <div className="font-semibold text-gray-400 mb-1">Props:</div>
                <div className="bg-gray-800 rounded p-2 space-y-1">
                  {Object.entries(selectedComponent.props).map(([key, value]) => (
                    <div key={key} className="flex items-start gap-2">
                      <span className="text-blue-400 font-mono">{key}:</span>
                      <span className="text-gray-300">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {showDetails && (
              <>
                {selectedComponent.dependencies && selectedComponent.dependencies.length > 0 && (
                  <div className="text-xs">
                    <div className="font-semibold text-gray-400 mb-1">Dependencies:</div>
                    <div className="flex flex-wrap gap-1">
                      {selectedComponent.dependencies.map(dep => (
                        <span key={dep} className="px-2 py-0.5 bg-gray-800 text-gray-300 rounded">
                          {dep}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {selectedComponent.examples && selectedComponent.examples.length > 0 && (
                  <div className="text-xs">
                    <div className="font-semibold text-gray-400 mb-1">Examples:</div>
                    <div className="bg-gray-800 rounded p-2 space-y-1">
                      {selectedComponent.examples.map((example, idx) => (
                        <div key={idx} className="text-gray-300 font-mono text-xs">
                          {example}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {selectedComponent.usageCount !== undefined && (
                  <div className="text-xs text-gray-400">
                    Used <span className="text-gray-300 font-semibold">{selectedComponent.usageCount}</span> times
                  </div>
                )}
                {selectedComponent.lastUsed && (
                  <div className="text-xs text-gray-400">
                    Last used: <span className="text-gray-300">{new Date(selectedComponent.lastUsed).toLocaleDateString()}</span>
                  </div>
                )}
                {selectedComponent.hhniTags && selectedComponent.hhniTags.length > 0 && (
                  <div className="text-xs">
                    <div className="font-semibold text-gray-400 mb-1">HHNI Tags:</div>
                    <div className="flex flex-wrap gap-1">
                      {selectedComponent.hhniTags.map(tag => (
                        <span key={tag} className="px-1.5 py-0.5 bg-purple-600/20 text-purple-400 rounded text-xs">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </>
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

