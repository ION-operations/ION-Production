// System Index Browser Panel - V2 Feature Implementation
// Browse all system indexes with intent, architecture, integrations, and status
// Tree/Graph hybrid views with Obsidian-style force-directed graph

import React, { useState, useMemo, useRef, useEffect, useCallback } from 'react'
import { BasePanel } from '../components/BasePanel'
import { Search, Network, GitBranch, Layers, FileText, Settings, ChevronRight, ChevronDown, Filter } from 'lucide-react'
// import { useHHNI } from '../hooks/useAIMOS' // Not currently used

// ===== TYPE DEFINITIONS =====

interface SystemIndex {
  systemId: string
  humanName: string
  version: string
  status: 'production' | 'development' | 'testing' | 'deprecated' | 'planned'
  layer: number
  intent: {
    purpose: string
    must_not_regress: string[]
    why_it_exists: string
  }
  classification: {
    security_level: 'critical' | 'high' | 'medium' | 'low'
    perf_sensitivity: 'high' | 'medium' | 'low'
    ownership: 'core' | 'support' | 'integration' | 'meta'
    sideEffects: string[]
  }
  internalNodes: Array<{
    id: string
    responsibility: string
    must_never: string[]
    perf_budget_ms: number
    status: string
  }>
  integration_points: Array<{
    system: string
    protocol: string
    what_is_exchanged: string[]
  }>
  performance_summary: {
    avg_latency_ms?: number
    throughput?: number
    resource_usage?: Record<string, number>
  }
  documentation_status: {
    l0_complete: boolean
    l1_complete: boolean
    l2_complete: boolean
    l3_complete: boolean
    l4_complete: boolean
  }
  dependencies: string[]
  lineage?: {
    parentSystemId?: string | null
    childSystems?: string[]
    maturity?: string
  }
  connections?: Array<{
    viaPort?: string
    direction?: string
    connectsToSystemId?: string
    protocol?: string
    data?: string[]
    security_level?: string
  }>
  childSystems?: string[]
}

// ===== DATA LOADING HOOK =====

const useSystemIndexes = () => {
  const [systemIndexes, setSystemIndexes] = useState<SystemIndex[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadSystemIndexes = async () => {
      try {
        setLoading(true)
        setError(null)

        // Try to load from backend API
        let result: { success: boolean; indexes?: any[]; error?: string } = { success: false }
        
        try {
          const response = await fetch('/api/system-indexes', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
          })
          
          if (response.ok) {
            const data = await response.json()
            if (data.success && Array.isArray(data.indexes)) {
              result = { success: true, indexes: data.indexes }
            } else if (Array.isArray(data)) {
              result = { success: true, indexes: data }
            }
          }
        } catch (fetchError) {
          console.warn('API fetch failed, using mock data:', fetchError)
        }
        
        if (result.success && result.indexes) {
          // Transform backend data to match component interface
          // Handle both formats: systemId/humanName and system_id/system_name
          const transformedIndexes: SystemIndex[] = result.indexes.map((idx: any) => ({
            systemId: idx.systemId || idx.system_id || '',
            humanName: idx.humanName || idx.system_name || idx.humanName || '',
            version: idx.version || 'unknown',
            status: idx.status || 'unknown',
            layer: idx.layer || 1, // Default to layer 1 if not specified
            intent: idx.intent || { purpose: idx.purpose || '', must_not_regress: [], why_it_exists: '' },
            classification: idx.classification || {
              security_level: 'medium',
              perf_sensitivity: 'medium',
              ownership: 'support',
              sideEffects: []
            },
            internalNodes: idx.internalNodes || idx.system_map_excerpt?.core_components?.map((comp: string) => ({
              id: comp,
              responsibility: `Core component: ${comp}`,
              must_never: [],
              perf_budget_ms: 0,
              status: 'production'
            })) || [],
            integration_points: Array.isArray(idx.integration_points) 
              ? idx.integration_points 
              : (Array.isArray(idx.connections) 
                  ? idx.connections.map((conn: any) => ({
                      system: conn.connectsToSystemId || '',
                      protocol: conn.protocol || 'internal',
                      what_is_exchanged: Array.isArray(conn.data) ? conn.data : []
                    }))
                  : []),
            performance_summary: idx.performance_summary || {},
            documentation_status: idx.documentation_status || {
              l0_complete: false,
              l1_complete: false,
              l2_complete: false,
              l3_complete: false,
              l4_complete: false,
            },
            dependencies: idx.dependencies || [],
            // Store additional hierarchical data
            lineage: idx.lineage || {},
            connections: idx.connections || [],
            childSystems: Array.isArray(idx.lineage?.childSystems) 
              ? idx.lineage.childSystems.map((child: any) => typeof child === 'string' ? child : (child?.systemId || child?.id || String(child)))
              : (Array.isArray(idx.childSystems) 
                  ? idx.childSystems.map((child: any) => typeof child === 'string' ? child : (child?.systemId || child?.id || String(child)))
                  : []),
          }))
          
          setSystemIndexes(transformedIndexes)
        } else {
          // Fallback to mock data if API fails
          console.warn('API load failed, using mock data')
          const mockIndexes: SystemIndex[] = [
          {
            systemId: 'cmc.contextMemoryCore',
            humanName: 'Context Memory Core - Bitemporal Memory Substrate',
            version: 'v0.1',
            status: 'production',
            layer: 1,
            intent: {
              purpose: 'Provide persistent, bitemporal memory substrate for AIM-OS',
              must_not_regress: [
                'Must not lose data integrity',
                'Must not allow concurrent writes to same atom',
                'Must not modify atoms after creation',
              ],
              why_it_exists: 'Transforms ephemeral AI context into structured, queryable, reversible memory.',
            },
            classification: {
              security_level: 'critical',
              perf_sensitivity: 'high',
              ownership: 'core',
              sideEffects: [
                'Stores all AIM-OS memory permanently',
                'Provides time-travel query capabilities',
              ],
            },
            internalNodes: [
              {
                id: 'atomManager',
                responsibility: 'Manages fundamental memory units (atoms) with bitemporal tracking',
                must_never: [
                  'Allow concurrent writes to same atom',
                  'Delete atoms (only supersede)',
                ],
                perf_budget_ms: 10,
                status: 'production',
              },
            ],
            integration_points: [
              {
                system: 'hhni',
                protocol: 'internal_api',
                what_is_exchanged: ['atoms_for_indexing', 'retrieval_queries'],
              },
            ],
            performance_summary: {
              avg_latency_ms: 50,
            },
            documentation_status: {
              l0_complete: true,
              l1_complete: true,
              l2_complete: true,
              l3_complete: true,
              l4_complete: false,
            },
            dependencies: [],
          },
          {
            systemId: 'hhni.hierarchicalHypergraph',
            humanName: 'Hierarchical Hypergraph Neural Index',
            version: 'v0.1',
            status: 'production',
            layer: 2,
            intent: {
              purpose: 'Enable fast paragraph/sentence retrieval with safety and observability',
              must_not_regress: [
                'Must not exceed 100ms p99 latency',
                'Must not allow node explosion',
              ],
              why_it_exists: 'Provides physics-guided retrieval with hierarchical structure.',
            },
            classification: {
              security_level: 'high',
              perf_sensitivity: 'high',
              ownership: 'core',
              sideEffects: ['Enables semantic search', 'Provides context optimization'],
            },
            internalNodes: [
              {
                id: 'dvns',
                responsibility: 'Dynamic Vector Navigation System with 4 physics forces',
                must_never: ['Return inconsistent results', 'Exceed context budget'],
                perf_budget_ms: 100,
                status: 'production',
              },
            ],
            integration_points: [
              {
                system: 'cmc',
                protocol: 'internal_api',
                what_is_exchanged: ['atoms_for_indexing', 'hierarchical_paths'],
              },
            ],
            performance_summary: {
              avg_latency_ms: 75,
            },
            documentation_status: {
              l0_complete: true,
              l1_complete: true,
              l2_complete: true,
              l3_complete: true,
              l4_complete: true,
            },
            dependencies: ['cmc'],
          },
          {
            systemId: 'vif.verifiableIntelligence',
            humanName: 'Verifiable Intelligence Framework',
            version: 'v0.1',
            status: 'production',
            layer: 2,
            intent: {
              purpose: 'Provenance envelopes for every AI operation',
              must_not_regress: [
                'Must not lose witness integrity',
                'Must not allow confidence manipulation',
              ],
              why_it_exists: 'Enables deterministic replay and confidence tracking.',
            },
            classification: {
              security_level: 'critical',
              perf_sensitivity: 'medium',
              ownership: 'core',
              sideEffects: ['Tracks all AI operations', 'Provides confidence scores'],
            },
            internalNodes: [
              {
                id: 'witnessGenerator',
                responsibility: 'Creates cryptographic witness envelopes',
                must_never: ['Modify witnesses after creation', 'Allow hash collisions'],
                perf_budget_ms: 50,
                status: 'production',
              },
            ],
            integration_points: [
              {
                system: 'cmc',
                protocol: 'internal_api',
                what_is_exchanged: ['witness_storage', 'confidence_scores'],
              },
            ],
            performance_summary: {
              avg_latency_ms: 30,
            },
            documentation_status: {
              l0_complete: true,
              l1_complete: true,
              l2_complete: true,
              l3_complete: true,
              l4_complete: false,
            },
            dependencies: ['cmc'],
          },
          {
            systemId: 'seg.sharedEvidenceGraph',
            humanName: 'Shared Evidence Graph',
            version: 'v0.1',
            status: 'development',
            layer: 1,
            intent: {
              purpose: 'Time-sliced, contradiction-aware knowledge graph',
              must_not_regress: [
                'Must not lose graph integrity',
                'Must not allow contradiction suppression',
              ],
              why_it_exists: 'Synthesizes knowledge with contradiction detection.',
            },
            classification: {
              security_level: 'high',
              perf_sensitivity: 'medium',
              ownership: 'core',
              sideEffects: ['Stores knowledge graph', 'Detects contradictions'],
            },
            internalNodes: [],
            integration_points: [
              {
                system: 'cmc',
                protocol: 'internal_api',
                what_is_exchanged: ['provenance_edges', 'graph_nodes'],
              },
            ],
            performance_summary: {},
            documentation_status: {
              l0_complete: true,
              l1_complete: true,
              l2_complete: false,
              l3_complete: false,
              l4_complete: false,
            },
            dependencies: ['cmc', 'hhni', 'vif'],
          },
          {
            systemId: 'apoe.aiPoweredOrchestration',
            humanName: 'AI-Powered Orchestration Engine',
            version: 'v0.1',
            status: 'production',
            layer: 3,
            intent: {
              purpose: 'Compiles reasoning into executable plans (DAGs)',
              must_not_regress: [
                'Must not skip quality gates',
                'Must not allow plan corruption',
              ],
              why_it_exists: 'Enables autonomous task planning and execution.',
            },
            classification: {
              security_level: 'high',
              perf_sensitivity: 'medium',
              ownership: 'core',
              sideEffects: ['Creates execution plans', 'Orchestrates tasks'],
            },
            internalNodes: [
              {
                id: 'planCompiler',
                responsibility: 'Compiles reasoning into DAG execution plans',
                must_never: ['Create circular dependencies', 'Skip quality gates'],
                perf_budget_ms: 200,
                status: 'production',
              },
            ],
            integration_points: [
              {
                system: 'cmc',
                protocol: 'internal_api',
                what_is_exchanged: ['context_retrieval_requests', 'execution_traces'],
              },
            ],
            performance_summary: {
              avg_latency_ms: 150,
            },
            documentation_status: {
              l0_complete: true,
              l1_complete: true,
              l2_complete: true,
              l3_complete: true,
              l4_complete: false,
            },
            dependencies: ['vif', 'seg', 'tcs'],
          },
        ]
        
        setSystemIndexes(mockIndexes)
        // Don't set error for fallback - just log it
        }
      } catch (err) {
        console.error('Failed to load system indexes:', err)
        setError(err instanceof Error ? err.message : 'Failed to load system indexes')
      } finally {
        setLoading(false)
      }
    }

    loadSystemIndexes()
  }, [])

  return { systemIndexes, loading, error }
}

// ===== TREE VIEW COMPONENT =====

interface SystemTreeViewProps {
  systems: SystemIndex[] // All systems for lookups
  filteredSystems: SystemIndex[] // Filtered systems to display
  selectedSystem: string | null
  onSelect: (systemId: string) => void
  searchQuery: string
  layerFilter: number | null
  statusFilter: string | null
}

const SystemTreeView: React.FC<SystemTreeViewProps> = ({
  systems, // All systems for lookups
  filteredSystems, // Filtered systems to display
  selectedSystem,
  onSelect,
  searchQuery,
  layerFilter,
  statusFilter,
}) => {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set())
  const [viewMode, setViewMode] = useState<'intent' | 'architecture' | 'integration' | 'status'>('intent')

  const toggleNode = (nodeId: string) => {
    const newExpanded = new Set(expandedNodes)
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId)
    } else {
      newExpanded.add(nodeId)
    }
    setExpandedNodes(newExpanded)
  }

  // Use filteredSystems prop directly (already filtered by parent)

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'production': return 'text-green-400'
      case 'development': return 'text-yellow-400'
      case 'testing': return 'text-blue-400'
      case 'deprecated': return 'text-gray-400'
      case 'planned': return 'text-purple-400'
      default: return 'text-gray-400'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'production': return '✅'
      case 'development': return '⚠️'
      case 'testing': return '🧪'
      case 'deprecated': return '❌'
      case 'planned': return '📋'
      default: return '●'
    }
  }

  return (
    <div className="w-full h-full flex flex-col bg-gray-900 text-white">
      {/* View Mode Tabs */}
      <div className="flex border-b border-gray-700">
        {(['intent', 'architecture', 'integration', 'status'] as const).map(mode => (
          <button
            key={mode}
            onClick={() => setViewMode(mode)}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              viewMode === mode
                ? 'bg-gray-800 text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
            }`}
          >
            {mode.charAt(0).toUpperCase() + mode.slice(1)}
          </button>
        ))}
      </div>

      {/* Tree Content */}
      <div className="flex-1 overflow-auto p-4">
        {filteredSystems.map(system => (
          <div key={system.systemId} className="mb-3">
            <div
              className={`flex items-center gap-2 cursor-pointer hover:bg-gray-800 p-2 rounded ${
                selectedSystem === system.systemId ? 'bg-gray-800 border-l-2 border-blue-400' : ''
              }`}
              onClick={() => {
                toggleNode(system.systemId)
                onSelect(system.systemId)
              }}
            >
              <span className="text-xs">
                {expandedNodes.has(system.systemId) ? '▼' : '▶'}
              </span>
              <span className={`text-xs ${getStatusColor(system.status)}`}>
                {getStatusIcon(system.status)}
              </span>
              <span className="font-semibold text-sm">{system.humanName}</span>
              <span className="text-xs text-gray-400">(Layer {system.layer})</span>
              <span className={`text-xs ${getStatusColor(system.status)}`}>
                {system.status}
              </span>
            </div>

            {expandedNodes.has(system.systemId) && (
              <div className="ml-6 mt-2 space-y-2">
                {viewMode === 'intent' && (
                  <div className="text-sm text-gray-300 space-y-1">
                    <div><strong>Purpose:</strong> {system.intent.purpose}</div>
                    <div><strong>Why it exists:</strong> {system.intent.why_it_exists}</div>
                    <div className="mt-2">
                      <strong>Must not regress:</strong>
                      <ul className="list-disc list-inside ml-2 mt-1">
                        {system.intent.must_not_regress.map((item, idx) => (
                          <li key={idx} className="text-xs">{item}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {viewMode === 'architecture' && (
                  <div className="text-sm text-gray-300 space-y-2">
                    {/* Child Systems */}
                    {system.childSystems && system.childSystems.length > 0 && (
                      <div>
                        <strong>Child Systems ({system.childSystems.length}):</strong>
                        <ul className="list-disc list-inside ml-2 mt-1">
                          {system.childSystems.map((childId, idx) => {
                            const childSystem = systems.find(s => s.systemId === childId || s.systemId.includes(childId))
                            return (
                              <li key={idx} className="text-xs">
                                {childSystem ? childSystem.humanName : childId}
                              </li>
                            )
                          })}
                        </ul>
                      </div>
                    )}
                    
                    {/* Internal Nodes/Components */}
                    <div>
                      <strong>Internal Components ({system.internalNodes.length}):</strong>
                      {system.internalNodes.length > 0 ? (
                        <ul className="list-disc list-inside ml-2 mt-1">
                          {system.internalNodes.map(node => (
                            <li key={node.id} className="text-xs">
                              <strong>{node.id}:</strong> {node.responsibility}
                              {node.perf_budget_ms > 0 && <span className="text-gray-500"> ({node.perf_budget_ms}ms)</span>}
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <div className="text-xs text-gray-500 ml-2 mt-1">No internal components defined</div>
                      )}
                    </div>
                    
                    {/* Dependencies */}
                    <div className="mt-2">
                      <strong>Dependencies:</strong> {system.dependencies.length > 0 ? system.dependencies.join(', ') : 'None'}
                    </div>
                  </div>
                )}

                {viewMode === 'integration' && (
                  <div className="text-sm text-gray-300 space-y-1">
                    <div><strong>Integration Points:</strong> {Array.isArray(system.integration_points) ? system.integration_points.length : 0}</div>
                    {Array.isArray(system.integration_points) && system.integration_points.length > 0 ? (
                      system.integration_points.map((point, idx) => (
                        <div key={idx} className="ml-2 mt-1 text-xs">
                          <strong>{point.system || 'Unknown'}:</strong> {point.protocol || 'internal'}
                          {Array.isArray(point.what_is_exchanged) && point.what_is_exchanged.length > 0 && (
                            <ul className="list-disc list-inside ml-2">
                              {point.what_is_exchanged.map((item, i) => (
                                <li key={i}>{item}</li>
                              ))}
                            </ul>
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="text-xs text-gray-500 ml-2 mt-1">No integration points defined</div>
                    )}
                  </div>
                )}

                {viewMode === 'status' && (
                  <div className="text-sm text-gray-300 space-y-1">
                    <div><strong>Version:</strong> {system.version}</div>
                    <div><strong>Security Level:</strong> {system.classification.security_level}</div>
                    <div><strong>Performance Sensitivity:</strong> {system.classification.perf_sensitivity}</div>
                    {system.performance_summary.avg_latency_ms && (
                      <div><strong>Avg Latency:</strong> {system.performance_summary.avg_latency_ms}ms</div>
                    )}
                    <div className="mt-2">
                      <strong>Documentation:</strong>
                      <div className="ml-2 mt-1 text-xs">
                        L0: {system.documentation_status.l0_complete ? '✅' : '❌'} | 
                        L1: {system.documentation_status.l1_complete ? '✅' : '❌'} | 
                        L2: {system.documentation_status.l2_complete ? '✅' : '❌'} | 
                        L3: {system.documentation_status.l3_complete ? '✅' : '❌'} | 
                        L4: {system.documentation_status.l4_complete ? '✅' : '❌'}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

// ===== GRAPH VIEW COMPONENT =====

interface SystemGraphViewProps {
  systems: SystemIndex[]
  selectedSystem: string | null
  onSelect: (systemId: string) => void
  searchQuery: string
  layerFilter: number | null
  statusFilter: string | null
}

const SystemGraphView: React.FC<SystemGraphViewProps> = ({
  systems,
  selectedSystem,
  onSelect,
  searchQuery,
  layerFilter,
  statusFilter,
}) => {
  const graphRef = useRef<any>()
  const containerRef = useRef<HTMLDivElement>(null)
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 })
  const [ForceGraph2D, setForceGraph2D] = useState<any>(null)

  useEffect(() => {
    // Lazy load ForceGraph2D to avoid module loading issues
    import('react-force-graph-2d').then((module) => {
      setForceGraph2D(() => module.default)
    }).catch((err) => {
      console.error('Failed to load ForceGraph2D:', err)
    })
  }, [])

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect()
        setDimensions({ width: rect.width, height: rect.height })
      }
    }
    updateDimensions()
    window.addEventListener('resize', updateDimensions)
    return () => window.removeEventListener('resize', updateDimensions)
  }, [])

  const filteredSystems = useMemo(() => {
    return systems.filter(system => {
      const matchesSearch = searchQuery === '' || 
        system.humanName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        system.systemId.toLowerCase().includes(searchQuery.toLowerCase())
      
      const matchesLayer = layerFilter === null || system.layer === layerFilter
      const matchesStatus = statusFilter === null || system.status === statusFilter

      return matchesSearch && matchesLayer && matchesStatus
    })
  }, [systems, searchQuery, layerFilter, statusFilter])

  const graphData = useMemo(() => {
    const nodes: Array<{ id: string; name: string; group: number; size: number; system?: SystemIndex; type: 'system' | 'component' | 'child' }> = []
    const links: Array<{ source: string; target: string; value: number; type: string }> = []
    const allSystems = systems // Use all systems, not just filtered, for child system lookups

    // Add system nodes
    filteredSystems.forEach(system => {
      nodes.push({
        id: system.systemId,
        name: system.humanName,
        group: system.layer,
        size: 12 + Math.min(system.internalNodes.length / 2, 8),
        system,
        type: 'system',
      })

      // Add child system nodes (if they exist in the dataset)
      if (system.childSystems && system.childSystems.length > 0) {
        system.childSystems.forEach(childId => {
          // Handle both string and object formats
          const childIdStr = typeof childId === 'string' ? childId : (childId?.systemId || childId?.id || String(childId))
          if (!childIdStr) return
          
          const childSystem = allSystems.find(s => 
            s.systemId === childIdStr || 
            (typeof childIdStr === 'string' && s.systemId.includes(childIdStr.split('.')[0]))
          )
          if (childSystem && !nodes.find(n => n.id === childSystem.systemId)) {
            nodes.push({
              id: childSystem.systemId,
              name: childSystem.humanName,
              group: childSystem.layer,
              size: 8,
              system: childSystem,
              type: 'child',
            })
            // Link parent to child
            links.push({
              source: system.systemId,
              target: childSystem.systemId,
              value: 0.6,
              type: 'parent-child',
            })
          }
        })
      }

      // Add internal component nodes (optional - can be toggled)
      // For now, we'll show them as smaller nodes
      system.internalNodes.forEach((node, idx) => {
        const componentId = `${system.systemId}.${node.id}`
        nodes.push({
          id: componentId,
          name: node.id,
          group: system.layer + 0.5, // Slightly different group for visual distinction
          size: 6,
          type: 'component',
        })
        // Link system to component
        links.push({
          source: system.systemId,
          target: componentId,
          value: 0.3,
          type: 'has-component',
        })
      })

      // Add dependency links
      if (Array.isArray(system.dependencies)) {
        system.dependencies.forEach(depId => {
          if (depId) {
            const targetSystem = allSystems.find(s => s.systemId === depId || s.systemId.includes(depId))
            if (targetSystem) {
              links.push({
                source: system.systemId,
                target: targetSystem.systemId,
                value: 1.0,
                type: 'dependency',
              })
            }
          }
        })
      }

      // Add connection links (from connections array)
      if (Array.isArray(system.connections)) {
        system.connections.forEach(conn => {
          if (conn && conn.connectsToSystemId) {
            const targetSystem = allSystems.find(s => s.systemId === conn.connectsToSystemId || s.systemId.includes(conn.connectsToSystemId.split('.')[0]))
            if (targetSystem) {
              links.push({
                source: system.systemId,
                target: targetSystem.systemId,
                value: 0.8,
                type: 'connection',
              })
            }
          }
        })
      }

      // Add integration point links
      if (Array.isArray(system.integration_points)) {
        system.integration_points.forEach(point => {
          if (point && point.system) {
            const targetSystem = allSystems.find(s => s.systemId.includes(point.system) || point.system.includes(s.systemId.split('.')[0]))
            if (targetSystem && targetSystem.systemId !== system.systemId) {
              links.push({
                source: system.systemId,
                target: targetSystem.systemId,
                value: 0.7,
                type: 'integration',
              })
            }
          }
        })
      }
    })

    return { nodes, links }
  }, [filteredSystems, systems])

  const getNodeColor = (node: any) => {
    if (node.id === selectedSystem) return '#3b82f6' // Blue for selected
    if (node.type === 'component') return '#6b7280' // Gray for components
    if (node.type === 'child') return '#8b5cf6' // Purple for child systems
    if (node.group === 1) return '#10b981' // Green for Layer 1
    if (node.group === 2) return '#3b82f6' // Blue for Layer 2
    if (node.group === 3) return '#8b5cf6' // Purple for Layer 3
    if (node.group === 4) return '#f59e0b' // Orange for Layer 4
    return '#6b7280' // Gray default
  }

  const getLinkColor = (link: any) => {
    switch (link.type) {
      case 'dependency': return '#10b981' // Green
      case 'integration': return '#3b82f6' // Blue
      case 'connection': return '#8b5cf6' // Purple
      case 'parent-child': return '#f59e0b' // Orange
      case 'has-component': return '#6b7280' // Gray
      default: return '#6b7280' // Gray
    }
  }

  const getSystemIcon = (layer: number) => {
    switch (layer) {
      case 1: return '⚙️'
      case 2: return '🧠'
      case 3: return '📊'
      case 4: return '🔧'
      default: return '●'
    }
  }

  if (!ForceGraph2D) {
    return (
      <div className="w-full h-full bg-gray-900 rounded-lg overflow-hidden relative flex items-center justify-center">
        <div className="text-gray-400">Loading graph...</div>
      </div>
    )
  }

  const GraphComponent = ForceGraph2D

  return (
    <div ref={containerRef} className="w-full h-full bg-gray-900 rounded-lg overflow-hidden relative">
      <GraphComponent
        ref={graphRef}
        graphData={graphData}
        width={dimensions.width}
        height={dimensions.height}
        nodeLabel={(node: any) => {
          return `<div style="background: rgba(0,0,0,0.9); color: white; padding: 6px 10px; border-radius: 4px; font-size: 12px; font-weight: 500;">${node.name}</div>`
        }}
        nodeColor={getNodeColor}
        nodeVal={(node: any) => node.size}
        linkColor={getLinkColor}
        linkWidth={2}
        linkDirectionalArrowLength={6}
        linkDirectionalArrowRelPos={1}
        onNodeClick={(node: any) => {
          // Only select if it's a system node, not a component
          if (node.type === 'system' || node.type === 'child') {
            onSelect(node.system?.systemId || node.id)
          }
        }}
        onNodeHover={(node: any) => {
          if (node && graphRef.current) {
            graphRef.current.getGraph().setNodeHighlight(node.id, true)
          }
        }}
        cooldownTicks={100}
        onEngineStop={() => {
          if (graphRef.current) {
            graphRef.current.zoomToFit(400, 20)
          }
        }}
        nodeCanvasObjectMode={() => 'after'}
        nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
          // Draw circle background
          ctx.beginPath()
          ctx.arc(node.x, node.y, node.size, 0, 2 * Math.PI)
          ctx.fillStyle = getNodeColor(node)
          ctx.fill()

          // Draw border for selected nodes
          if (node.id === selectedSystem) {
            ctx.strokeStyle = '#ffffff'
            ctx.lineWidth = 2 / globalScale
            ctx.stroke()
          }

          // Draw system icon/emoji
          const icon = getSystemIcon(node.group)
          ctx.font = `${node.size * 1.2}px Arial`
          ctx.textAlign = 'center'
          ctx.textBaseline = 'middle'
          ctx.fillStyle = '#ffffff'
          ctx.fillText(icon, node.x, node.y)
        }}
      />

      {/* Legend */}
      <div className="absolute bottom-2 left-2 bg-gray-800/95 border border-gray-700 rounded-lg p-2 text-xs text-gray-300 z-10">
        <div className="font-semibold mb-1.5 text-xs">Legend</div>
        <div className="space-y-1">
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-green-500"></div>
            <span className="text-xs">Layer 1</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-blue-500"></div>
            <span className="text-xs">Layer 2</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-purple-500"></div>
            <span className="text-xs">Layer 3</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// ===== MAIN PANEL COMPONENT =====

export const SystemIndexBrowserPanel: React.FC = () => {
  const { systemIndexes, loading, error } = useSystemIndexes()
  // const { search } = useHHNI() // Not currently used
  const [viewMode, setViewMode] = useState<'tree' | 'graph'>('tree')
  const [selectedSystem, setSelectedSystem] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [layerFilter, setLayerFilter] = useState<number | null>(null)
  const [statusFilter, setStatusFilter] = useState<string | null>(null)
  const [showFilters, setShowFilters] = useState(false)

  const filteredSystems = useMemo(() => {
    return systemIndexes.filter(system => {
      const matchesSearch = searchQuery === '' || 
        system.humanName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        system.systemId.toLowerCase().includes(searchQuery.toLowerCase()) ||
        system.intent.purpose.toLowerCase().includes(searchQuery.toLowerCase())
      
      const matchesLayer = layerFilter === null || system.layer === layerFilter
      const matchesStatus = statusFilter === null || system.status === statusFilter

      return matchesSearch && matchesLayer && matchesStatus
    })
  }, [systemIndexes, searchQuery, layerFilter, statusFilter])

  return (
    <BasePanel
      id="system-index-browser"
      title="System Index Browser"
      icon={Layers}
      description="Browse all system indexes with intent, architecture, integrations, and status"
      loading={loading}
      error={error}
      empty={!loading && !error && filteredSystems.length === 0}
      emptyMessage="No systems found matching filters"
      showHeader={true}
      headerContent={
        <div className="space-y-2">
          {/* Search Bar */}
          <div className="flex items-center gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search systems..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-8 pr-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`p-1.5 rounded ${showFilters ? 'bg-gray-700' : 'bg-gray-800'} hover:bg-gray-700 transition-colors`}
              title="Toggle filters"
            >
              <Filter className="w-4 h-4 text-gray-400" />
            </button>
          </div>

          {/* Filters */}
          {showFilters && (
            <div className="flex items-center gap-4 text-xs">
              <div className="flex items-center gap-2">
                <span className="text-gray-400">Layer:</span>
                <select
                  value={layerFilter || ''}
                  onChange={(e) => setLayerFilter(e.target.value ? parseInt(e.target.value) : null)}
                  className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-white"
                >
                  <option value="">All</option>
                  <option value="1">Layer 1</option>
                  <option value="2">Layer 2</option>
                  <option value="3">Layer 3</option>
                  <option value="4">Layer 4</option>
                </select>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-gray-400">Status:</span>
                <select
                  value={statusFilter || ''}
                  onChange={(e) => setStatusFilter(e.target.value || null)}
                  className="bg-gray-800 border border-gray-700 rounded px-2 py-1 text-white"
                >
                  <option value="">All</option>
                  <option value="production">Production</option>
                  <option value="development">Development</option>
                  <option value="testing">Testing</option>
                  <option value="planned">Planned</option>
                </select>
              </div>
            </div>
          )}

          {/* View Toggle */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('tree')}
              className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                viewMode === 'tree'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:text-gray-200'
              }`}
            >
              <GitBranch className="w-3 h-3 inline mr-1" />
              Tree
            </button>
            <button
              onClick={() => setViewMode('graph')}
              className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                viewMode === 'graph'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:text-gray-200'
              }`}
            >
              <Network className="w-3 h-3 inline mr-1" />
              Graph
            </button>
          </div>
        </div>
      }
      showFooter={true}
      footerContent={
        <div className="flex items-center justify-between text-xs text-gray-400">
          <div>
            {filteredSystems.length} system{filteredSystems.length !== 1 ? 's' : ''} shown
          </div>
          <div>
            {selectedSystem && `Selected: ${systemIndexes.find(s => s.systemId === selectedSystem)?.humanName || selectedSystem}`}
          </div>
        </div>
      }
    >
      {viewMode === 'tree' ? (
        <SystemTreeView
          systems={systemIndexes}
          filteredSystems={filteredSystems}
          selectedSystem={selectedSystem}
          onSelect={setSelectedSystem}
          searchQuery={searchQuery}
          layerFilter={layerFilter}
          statusFilter={statusFilter}
        />
      ) : (
        <SystemGraphView
          systems={filteredSystems}
          selectedSystem={selectedSystem}
          onSelect={setSelectedSystem}
          searchQuery={searchQuery}
          layerFilter={layerFilter}
          statusFilter={statusFilter}
        />
      )}
    </BasePanel>
  )
}

