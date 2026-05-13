import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import {
  Network,
  Search,
  Filter,
  RefreshCw,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Minimize2,
  Clock,
  Link,
  Brain,
  Sparkles,
  TrendingUp,
  Info,
  Eye,
  EyeOff,
  Layers,
  GitBranch,
  Calendar,
  Target,
  Zap,
  Shield,
  Database,
} from 'lucide-react'
import {
  ReactFlow,
  ReactFlowProvider,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  Background,
  Controls,
  MiniMap,
  MarkerType,
  NodeProps,
  Handle,
  Position,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { useAIMOS } from '../../hooks/useAIMOS'
import { LoadingState } from '../LoadingState'
import { ErrorBoundary } from '../ErrorBoundary'

interface ContextNode {
  id: string
  label: string
  content: string
  timestamp: string
  modality: 'language' | 'code' | 'memory' | 'plan' | 'execution' | 'system'
  confidence: number // VIF confidence score
  recency: number // Days ago (0 = today)
  strength: number // Connection strength (0-1)
  tags: string[]
  source?: string // Source conversation/context ID
  evolution?: string[] // IDs of related contexts showing evolution
}

interface ContextEdge {
  id: string
  source: string
  target: string
  type: 'evolved_into' | 'related_to' | 'depends_on' | 'contradicts' | 'supports'
  strength: number // 0-1
  timestamp: string
  label?: string
}

interface ContextWebPanelProps {
  onNodeClick?: (node: ContextNode) => void
  onNodeSelect?: (node: ContextNode | null) => void
}

// Mock data for prototype
const generateMockContextWeb = (): { nodes: ContextNode[]; edges: ContextEdge[] } => {
  const nodes: ContextNode[] = [
    {
      id: 'ctx-001',
      label: 'Ferrari Engines Discussion',
      content: 'Initial conversation about Ferrari engine architecture and performance characteristics',
      timestamp: '2025-10-15T10:00:00Z',
      modality: 'language',
      confidence: 0.92,
      recency: 23,
      strength: 0.85,
      tags: ['ferrari', 'engines', 'performance'],
      source: 'conversation-2025-10-15',
      evolution: ['ctx-002', 'ctx-003'],
    },
    {
      id: 'ctx-002',
      label: 'Performance Tuning Deep Dive',
      content: 'Deep dive into Ferrari engine performance tuning techniques and optimization strategies',
      timestamp: '2025-10-20T14:30:00Z',
      modality: 'language',
      confidence: 0.88,
      recency: 18,
      strength: 0.90,
      tags: ['ferrari', 'performance', 'tuning'],
      source: 'conversation-2025-10-20',
      evolution: ['ctx-003'],
    },
    {
      id: 'ctx-003',
      label: 'Current Project Application',
      content: 'Applying Ferrari engine concepts to current project architecture and design patterns',
      timestamp: '2025-11-07T09:00:00Z',
      modality: 'plan',
      confidence: 0.95,
      recency: 0,
      strength: 1.0,
      tags: ['ferrari', 'project', 'architecture'],
      source: 'conversation-2025-11-07',
    },
    {
      id: 'ctx-004',
      label: 'Italian Engineering Principles',
      content: 'Discussion about Italian engineering philosophy and design principles',
      timestamp: '2025-10-12T11:00:00Z',
      modality: 'language',
      confidence: 0.85,
      recency: 26,
      strength: 0.75,
      tags: ['italian', 'engineering', 'design'],
      source: 'conversation-2025-10-12',
      evolution: ['ctx-001'],
    },
    {
      id: 'ctx-005',
      label: 'Racing History Context',
      content: 'Historical context about Ferrari racing achievements and legacy',
      timestamp: '2025-10-08T16:00:00Z',
      modality: 'memory',
      confidence: 0.90,
      recency: 30,
      strength: 0.70,
      tags: ['ferrari', 'racing', 'history'],
      source: 'research-2025-10-08',
      evolution: ['ctx-001'],
    },
    {
      id: 'ctx-006',
      label: 'IDE Orchestration System',
      content: 'Current work on IDE orchestration and multi-agent coordination',
      timestamp: '2025-11-05T10:00:00Z',
      modality: 'plan',
      confidence: 0.93,
      recency: 2,
      strength: 0.80,
      tags: ['ide', 'orchestration', 'agents'],
      source: 'conversation-2025-11-05',
    },
    {
      id: 'ctx-007',
      label: 'Context Web Visualization',
      content: 'Design and implementation of Context Web panel for IDE',
      timestamp: '2025-11-07T14:00:00Z',
      modality: 'code',
      confidence: 0.97,
      recency: 0,
      strength: 0.95,
      tags: ['context-web', 'ui', 'visualization'],
      source: 'conversation-2025-11-07',
      evolution: ['ctx-003', 'ctx-006'],
    },
  ]

  const edges: ContextEdge[] = [
    {
      id: 'edge-001',
      source: 'ctx-001',
      target: 'ctx-002',
      type: 'evolved_into',
      strength: 0.85,
      timestamp: '2025-10-20T14:30:00Z',
      label: 'Evolved Into',
    },
    {
      id: 'edge-002',
      source: 'ctx-002',
      target: 'ctx-003',
      type: 'evolved_into',
      strength: 0.90,
      timestamp: '2025-11-07T09:00:00Z',
      label: 'Evolved Into',
    },
    {
      id: 'edge-003',
      source: 'ctx-004',
      target: 'ctx-001',
      type: 'related_to',
      strength: 0.75,
      timestamp: '2025-10-15T10:00:00Z',
      label: 'Related To',
    },
    {
      id: 'edge-004',
      source: 'ctx-005',
      target: 'ctx-001',
      type: 'related_to',
      strength: 0.70,
      timestamp: '2025-10-15T10:00:00Z',
      label: 'Related To',
    },
    {
      id: 'edge-005',
      source: 'ctx-003',
      target: 'ctx-007',
      type: 'depends_on',
      strength: 0.80,
      timestamp: '2025-11-07T14:00:00Z',
      label: 'Depends On',
    },
    {
      id: 'edge-006',
      source: 'ctx-006',
      target: 'ctx-007',
      type: 'related_to',
      strength: 0.75,
      timestamp: '2025-11-07T14:00:00Z',
      label: 'Related To',
    },
  ]

  return { nodes, edges }
}

export const ContextWebPanel: React.FC<ContextWebPanelProps> = React.memo(({ onNodeClick, onNodeSelect }) => {
  const [nodes, setNodes] = useState<ContextNode[]>([])
  const [edges, setEdges] = useState<ContextEdge[]>([])
  const [selectedNode, setSelectedNode] = useState<ContextNode | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterModality, setFilterModality] = useState<'all' | ContextNode['modality']>('all')
  const [filterRecency, setFilterRecency] = useState<'all' | 'today' | 'week' | 'month' | 'older'>('all')
  const [isLoading, setIsLoading] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [showEvolution, setShowEvolution] = useState(true)
  const [showRelated, setShowRelated] = useState(true)
  
  // React Flow state
  const [reactFlowNodes, setReactFlowNodes, onNodesChange] = useNodesState([])
  const [reactFlowEdges, setReactFlowEdges, onEdgesChange] = useEdgesState([])

  // AIM-OS integration
  const { hhni, seg, cmc, vif, isConnected: aimosConnected, useMockData, loading } = useAIMOS()

  // Load context web data from AIM-OS (HHNI + SEG + CMC)
  const loadContextWeb = useCallback(async () => {
    setIsLoading(true)
    try {
      if (!useMockData && aimosConnected) {
        // Use HHNI for semantic search
        const hhniResults = await hhni.search(searchTerm || '*', 50)
        
        // Get CMC atoms for full context and timestamps
        const cmcAtoms = await Promise.all(
          hhniResults.slice(0, 50).map(async (result) => {
            try {
              const atoms = await cmc.retrieve(result.node.content || '', 1)
              return atoms[0] || null
            } catch {
              return null
            }
          })
        )
        
        // Use SEG synthesis to discover relationships between contexts
        const topics = hhniResults.slice(0, 10).map(r => r.node.content || r.node.summary || '').filter(Boolean)
        let segRelationships: any[] = []
        if (topics.length > 0) {
          try {
            const synthesis = await seg.synthesizeKnowledge(topics)
            // Extract relationships from synthesis result
            if (synthesis && synthesis.entities) {
              segRelationships = synthesis.entities || []
            }
          } catch (err) {
            console.warn('SEG synthesis failed, continuing without relationships:', err)
          }
        }
        
        // Transform HHNI + CMC results to ContextNodes
        const contextNodes: ContextNode[] = hhniResults.map((result, index) => {
          const atom = cmcAtoms[index]
          const now = new Date()
          const createdAt = atom ? new Date(atom.created_at) : now
          const daysAgo = Math.floor((now.getTime() - createdAt.getTime()) / (1000 * 60 * 60 * 24))
          
          return {
            id: atom?.id || result.node.id || `ctx-${index}`,
            label: result.node.summary || result.node.content?.substring(0, 50) || `Context ${index + 1}`,
            content: atom?.content?.inline || result.node.content || '',
            timestamp: atom?.created_at || createdAt.toISOString(),
            modality: atom?.modality === 'code' ? 'code' : 
                     atom?.modality === 'text' ? 'language' : 
                     atom?.modality === 'event' ? 'execution' : 'memory',
            confidence: atom?.witness?.uncertainty_band === 'green' ? 0.9 :
                       atom?.witness?.uncertainty_band === 'yellow' ? 0.7 : 0.5,
            recency: daysAgo,
            strength: result.score || 0.8,
            tags: Object.keys(atom?.tags || {}),
            source: atom?.id,
          }
        })
        
        // Create edges from SEG relationships and semantic similarity
        const contextEdges: ContextEdge[] = []
        
        // Add edges based on SEG synthesis
        segRelationships.forEach((rel, idx) => {
          if (rel.source_id && rel.target_id) {
            const sourceNode = contextNodes.find(n => n.id === rel.source_id)
            const targetNode = contextNodes.find(n => n.id === rel.target_id)
            if (sourceNode && targetNode) {
              contextEdges.push({
                id: `seg-${idx}`,
                source: sourceNode.id,
                target: targetNode.id,
                type: rel.relation_type === 'SUPPORTS' ? 'supports' :
                      rel.relation_type === 'CONTRADICTS' ? 'contradicts' :
                      rel.relation_type === 'DERIVES_FROM' ? 'depends_on' : 'related_to',
                strength: rel.confidence || 0.7,
                timestamp: rel.vt_start || new Date().toISOString(),
                label: rel.relation_type,
              })
            }
          }
        })
        
        // Add edges based on semantic similarity (high similarity = related_to)
        for (let i = 0; i < contextNodes.length; i++) {
          for (let j = i + 1; j < contextNodes.length; j++) {
            const similarity = hhniResults[i]?.score && hhniResults[j]?.score 
              ? Math.min(hhniResults[i].score, hhniResults[j].score) 
              : 0.5
            if (similarity > 0.7) {
              contextEdges.push({
                id: `sim-${i}-${j}`,
                source: contextNodes[i].id,
                target: contextNodes[j].id,
                type: 'related_to',
                strength: similarity,
                timestamp: new Date().toISOString(),
              })
            }
          }
        }
        
        setNodes(contextNodes)
        setEdges(contextEdges)
        setIsConnected(true)
      } else {
        // Fallback to mock data
        const mockData = generateMockContextWeb()
        setNodes(mockData.nodes)
        setEdges(mockData.edges)
        setIsConnected(false)
      }
    } catch (error) {
      console.error('Failed to load context web:', error)
      // Fallback to mock data
      const mockData = generateMockContextWeb()
      setNodes(mockData.nodes)
      setEdges(mockData.edges)
      setIsConnected(false)
    } finally {
      setIsLoading(false)
    }
  }, [searchTerm, hhni, seg, cmc, aimosConnected, useMockData])

  useEffect(() => {
    loadContextWeb()
  }, [loadContextWeb])

  const getModalityIcon = (modality: ContextNode['modality']) => {
    switch (modality) {
      case 'language':
        return <Brain className="w-4 h-4 text-blue-400" />
      case 'code':
        return <Zap className="w-4 h-4 text-green-400" />
      case 'memory':
        return <Database className="w-4 h-4 text-purple-400" />
      case 'plan':
        return <Target className="w-4 h-4 text-yellow-400" />
      case 'execution':
        return <GitBranch className="w-4 h-4 text-orange-400" />
      case 'system':
        return <Shield className="w-4 h-4 text-red-400" />
      default:
        return <Network className="w-4 h-4 text-gray-400" />
    }
  }

  const getModalityColor = (modality: ContextNode['modality']) => {
    switch (modality) {
      case 'language':
        return 'bg-blue-500/20 border-blue-500'
      case 'code':
        return 'bg-green-500/20 border-green-500'
      case 'memory':
        return 'bg-purple-500/20 border-purple-500'
      case 'plan':
        return 'bg-yellow-500/20 border-yellow-500'
      case 'execution':
        return 'bg-orange-500/20 border-orange-500'
      case 'system':
        return 'bg-red-500/20 border-red-500'
      default:
        return 'bg-gray-500/20 border-gray-500'
    }
  }

  const getEdgeColor = (type: ContextEdge['type']) => {
    switch (type) {
      case 'evolved_into':
        return 'stroke-yellow-400'
      case 'related_to':
        return 'stroke-blue-400'
      case 'depends_on':
        return 'stroke-green-400'
      case 'contradicts':
        return 'stroke-red-400'
      case 'supports':
        return 'stroke-purple-400'
      default:
        return 'stroke-gray-400'
    }
  }

  const filteredNodes = useMemo(() => {
    return nodes.filter(node => {
      const matchesSearch = searchTerm === '' ||
                            node.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            node.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            node.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
      
      const matchesModality = filterModality === 'all' || node.modality === filterModality
      
      const matchesRecency = filterRecency === 'all' ||
                            (filterRecency === 'today' && node.recency === 0) ||
                            (filterRecency === 'week' && node.recency <= 7) ||
                            (filterRecency === 'month' && node.recency <= 30) ||
                            (filterRecency === 'older' && node.recency > 30)
      
      return matchesSearch && matchesModality && matchesRecency
    })
  }, [nodes, searchTerm, filterModality, filterRecency])

  const filteredEdges = useMemo(() => {
    const filteredNodeIds = new Set(filteredNodes.map(n => n.id))
    return edges.filter(edge => {
      const showEdge = filteredNodeIds.has(edge.source) && filteredNodeIds.has(edge.target) &&
                       ((showEvolution && edge.type === 'evolved_into') ||
                        (showRelated && (edge.type === 'related_to' || edge.type === 'depends_on' || edge.type === 'supports')) ||
                        edge.type === 'contradicts')
      return showEdge
    })
  }, [edges, filteredNodes, showEvolution, showRelated])

  const handleNodeClick = useCallback((node: ContextNode) => {
    setSelectedNode(node)
    onNodeClick?.(node)
    onNodeSelect?.(node)
  }, [onNodeClick, onNodeSelect])

  const handleReactFlowNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    const contextNode = node.data.node as ContextNode
    handleNodeClick(contextNode)
  }, [handleNodeClick])

  // Custom Context Node Component for React Flow
  const ContextNodeComponent: React.FC<NodeProps> = ({ data, selected }) => {
    const node = data.node as ContextNode
    const ModalityIconElement = getModalityIcon(node.modality)
    
    return (
      <div
        className={`px-3 py-2 rounded-lg border-2 min-w-[140px] max-w-[180px] cursor-pointer transition-all ${
          selected
            ? 'bg-blue-600/30 border-blue-400 shadow-lg shadow-blue-500/50'
            : getModalityColor(node.modality)
        }`}
        style={{
          boxShadow: selected ? '0 0 20px rgba(59, 130, 246, 0.5)' : undefined,
        }}
      >
        <Handle type="target" position={Position.Top} className="w-2 h-2" />
        <div className="flex items-center gap-2 mb-1">
          {ModalityIconElement}
          <span className="text-xs font-semibold text-white truncate">
            {node.label.length > 20 ? node.label.substring(0, 17) + '...' : node.label}
          </span>
        </div>
        <div className="flex items-center justify-between text-xs text-gray-300 mb-1">
          <span>{node.recency === 0 ? 'Today' : `${node.recency}d ago`}</span>
          <div className="flex items-center gap-1">
            <Shield className={`w-3 h-3 ${
              node.confidence >= 0.95 ? 'text-green-400' :
              node.confidence >= 0.90 ? 'text-yellow-400' :
              'text-red-400'
            }`} />
            <span className={`
              ${node.confidence >= 0.95 ? 'text-green-400' :
                node.confidence >= 0.90 ? 'text-yellow-400' :
                'text-red-400'}
            `}>
              {(node.confidence * 100).toFixed(0)}%
            </span>
          </div>
        </div>
        {node.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-1">
            {node.tags.slice(0, 2).map((tag) => (
              <span
                key={tag}
                className="px-1 py-0.5 bg-purple-500/20 text-purple-300 text-[10px] rounded"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
        <Handle type="source" position={Position.Bottom} className="w-2 h-2" />
      </div>
    )
  }

  const nodeTypes = useMemo(() => ({
    contextNode: ContextNodeComponent,
  }), [])

  // Convert ContextNodes/Edges to React Flow format
  useEffect(() => {
    if (filteredNodes.length === 0) {
      setReactFlowNodes([])
      setReactFlowEdges([])
      return
    }

    // Convert nodes to React Flow format with initial positions
    const cols = Math.ceil(Math.sqrt(filteredNodes.length))
    const spacing = 200
    const initialNodes: Node[] = filteredNodes.map((node, idx) => {
      const x = (idx % cols) * spacing + 100
      const y = Math.floor(idx / cols) * spacing + 100
      
      return {
        id: node.id,
        type: 'contextNode',
        position: { x, y },
        data: { node },
        selected: selectedNode?.id === node.id,
      }
    })

    // Convert edges to React Flow format
    const initialEdges: Edge[] = filteredEdges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: 'smoothstep',
      animated: edge.type === 'evolved_into',
      style: {
        strokeWidth: edge.strength * 3,
        stroke: getEdgeColorHex(edge.type),
        opacity: 0.6,
      },
      label: edge.label || edge.type.replace('_', ' '),
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: getEdgeColorHex(edge.type),
      },
    }))

    setReactFlowNodes(initialNodes)
    setReactFlowEdges(initialEdges)
  }, [filteredNodes, filteredEdges, selectedNode, setReactFlowNodes, setReactFlowEdges])

  const getEdgeColorHex = (type: ContextEdge['type']): string => {
    switch (type) {
      case 'evolved_into':
        return '#fbbf24' // yellow-400
      case 'related_to':
        return '#60a5fa' // blue-400
      case 'depends_on':
        return '#34d399' // green-400
      case 'contradicts':
        return '#f87171' // red-400
      case 'supports':
        return '#a78bfa' // purple-400
      default:
        return '#9ca3af' // gray-400
    }
  }

  const handleNodeClick = useCallback((node: ContextNode) => {
    setSelectedNode(node)
    onNodeClick?.(node)
    onNodeSelect?.(node)
  }, [onNodeClick, onNodeSelect])

  const handleReactFlowNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    const contextNode = node.data.node as ContextNode
    handleNodeClick(contextNode)
  }, [handleNodeClick])

  // React Flow graph rendering
  const renderGraph = useCallback(() => {
    if (filteredNodes.length === 0) {
      return (
        <div className="flex items-center justify-center h-full text-gray-400">
          <div className="text-center">
            <Network className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No contexts found</p>
            <p className="text-xs mt-1">Try adjusting filters or search</p>
          </div>
        </div>
      )
    }

    return (
      <ReactFlowProvider>
        <ReactFlow
          nodes={reactFlowNodes}
          edges={reactFlowEdges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={handleReactFlowNodeClick}
          nodeTypes={nodeTypes}
          fitView
          className="bg-gray-900"
          minZoom={0.2}
          maxZoom={2}
          defaultEdgeOptions={{
            type: 'smoothstep',
            animated: false,
          }}
        >
          <Background color="#374151" gap={16} />
          <Controls className="bg-gray-800 border-gray-700" />
          <MiniMap
            className="bg-gray-800 border-gray-700"
            nodeColor={(node) => {
              const contextNode = node.data?.node as ContextNode
              if (!contextNode) return '#6b7280'
              switch (contextNode.modality) {
                case 'language': return '#3b82f6'
                case 'code': return '#10b981'
                case 'memory': return '#a78bfa'
                case 'plan': return '#fbbf24'
                case 'execution': return '#f97316'
                case 'system': return '#ef4444'
                default: return '#6b7280'
              }
            }}
            maskColor="rgba(0, 0, 0, 0.6)"
          />
        </ReactFlow>
      </ReactFlowProvider>
    )
  }, [filteredNodes, reactFlowNodes, reactFlowEdges, onNodesChange, onEdgesChange, handleReactFlowNodeClick, nodeTypes])

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-900 text-gray-200">
        {loading.hhni || loading.seg || loading.cmc ? (
          <LoadingState message="Loading context web..." />
        ) : (
          <>
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 flex items-center gap-2 shrink-0">
        <Network className="w-5 h-5 text-purple-400" />
        <div>
          <div className="text-white text-sm font-semibold">Context Web ⭐</div>
          <div className="text-xs text-gray-500">HHNI & SEG Integration</div>
        </div>
        <span
          className={`ml-auto px-2 py-1 rounded-full text-xs font-medium ${
            isConnected ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
          }`}
        >
          {isConnected ? 'Connected' : 'Mock Mode'}
        </span>
        <button onClick={loadContextWeb} className="text-gray-400 hover:text-white p-1 rounded">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Search and Filters */}
      <div className="p-3 border-b border-gray-700 shrink-0 space-y-2">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search contexts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-gray-800 text-white text-sm px-9 py-2 rounded focus:outline-none focus:ring-2 focus:ring-purple-500 border border-gray-700"
          />
        </div>

        <div className="flex gap-2 overflow-x-auto pb-1">
          {/* Modality Filter */}
          <select
            value={filterModality}
            onChange={(e) => setFilterModality(e.target.value as any)}
            className="px-3 py-1 text-xs rounded bg-gray-700 text-gray-300 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="all">All Modalities</option>
            <option value="language">Language</option>
            <option value="code">Code</option>
            <option value="memory">Memory</option>
            <option value="plan">Plan</option>
            <option value="execution">Execution</option>
            <option value="system">System</option>
          </select>

          {/* Recency Filter */}
          <select
            value={filterRecency}
            onChange={(e) => setFilterRecency(e.target.value as any)}
            className="px-3 py-1 text-xs rounded bg-gray-700 text-gray-300 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="all">All Time</option>
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="older">Older</option>
          </select>

          {/* Toggle Evolution */}
          <button
            onClick={() => setShowEvolution(!showEvolution)}
            className={`px-3 py-1 text-xs rounded whitespace-nowrap flex items-center gap-1 ${
              showEvolution
                ? 'bg-yellow-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {showEvolution ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
            Evolution
          </button>

          {/* Toggle Related */}
          <button
            onClick={() => setShowRelated(!showRelated)}
            className={`px-3 py-1 text-xs rounded whitespace-nowrap flex items-center gap-1 ${
              showRelated
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {showRelated ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
            Related
          </button>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="px-3 py-2 border-b border-gray-700 flex items-center justify-between shrink-0">
        <div className="text-xs text-gray-500">
          {filteredNodes.length} contexts, {filteredEdges.length} connections
        </div>
        <div className="text-xs text-gray-500">
          Drag nodes • Zoom with mouse wheel • Use controls for navigation
        </div>
      </div>

      {/* Graph Canvas */}
      <div className="flex-1 overflow-hidden relative">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <RefreshCw className="w-8 h-8 mx-auto mb-2 text-gray-400 animate-spin" />
              <p className="text-gray-400 text-sm">Loading context web...</p>
            </div>
          </div>
        ) : (
          renderGraph()
        )}
      </div>

      {/* Node Detail Sidebar */}
      {selectedNode && (
        <div className="absolute right-0 top-0 h-full w-1/3 bg-gray-800 border-l border-gray-700 shadow-lg flex flex-col z-10">
          <div className="flex items-center justify-between p-4 border-b border-gray-700">
            <h4 className="text-white text-md font-semibold">Context Details</h4>
            <button
              onClick={() => {
                setSelectedNode(null)
                onNodeSelect?.(null)
              }}
              className="text-gray-400 hover:text-white"
            >
              <Minimize2 className="w-5 h-5" />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 text-sm text-gray-200 space-y-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                {getModalityIcon(selectedNode.modality)}
                <span className="font-semibold text-white">{selectedNode.label}</span>
              </div>
              <p className="text-gray-300">{selectedNode.content}</p>
            </div>

            <div>
              <p className="text-gray-400 mb-1">Modality:</p>
              <span className="capitalize">{selectedNode.modality}</span>
            </div>

            <div>
              <p className="text-gray-400 mb-1">Confidence (VIF):</p>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      selectedNode.confidence >= 0.95 ? 'bg-green-500' :
                      selectedNode.confidence >= 0.90 ? 'bg-yellow-500' :
                      'bg-red-500'
                    }`}
                    style={{ width: `${selectedNode.confidence * 100}%` }}
                  />
                </div>
                <span className={`flex items-center gap-1 ${
                  selectedNode.confidence >= 0.95 ? 'text-green-400' :
                  selectedNode.confidence >= 0.90 ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  <Shield className="w-3 h-3" />
                  {(selectedNode.confidence * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            <div>
              <p className="text-gray-400 mb-1">Recency:</p>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-gray-400" />
                <span>
                  {selectedNode.recency === 0
                    ? 'Today'
                    : selectedNode.recency === 1
                    ? '1 day ago'
                    : `${selectedNode.recency} days ago`}
                </span>
              </div>
            </div>

            <div>
              <p className="text-gray-400 mb-1">Timestamp:</p>
              <span>{new Date(selectedNode.timestamp).toLocaleString()}</span>
            </div>

            {selectedNode.source && (
              <div>
                <p className="text-gray-400 mb-1">Source:</p>
                <span className="font-mono text-xs">{selectedNode.source}</span>
              </div>
            )}

            {selectedNode.tags.length > 0 && (
              <div>
                <p className="text-gray-400 mb-2">Tags:</p>
                <div className="flex flex-wrap gap-1">
                  {selectedNode.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-1 bg-purple-500/20 text-purple-300 text-xs rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {selectedNode.evolution && selectedNode.evolution.length > 0 && (
              <div>
                <p className="text-gray-400 mb-2">Evolution:</p>
                <div className="space-y-1">
                  {selectedNode.evolution.map((evolId) => {
                    const evolNode = nodes.find((n) => n.id === evolId)
                    if (!evolNode) return null
                    return (
                      <button
                        key={evolId}
                        onClick={() => handleNodeClick(evolNode)}
                        className="w-full text-left px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs flex items-center gap-2"
                      >
                        <TrendingUp className="w-3 h-3 text-yellow-400" />
                        <span>{evolNode.label}</span>
                      </button>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Related contexts */}
            {edges
              .filter((e) => e.source === selectedNode.id || e.target === selectedNode.id)
              .map((edge) => {
                const relatedNode =
                  edge.source === selectedNode.id
                    ? nodes.find((n) => n.id === edge.target)
                    : nodes.find((n) => n.id === edge.source)
                if (!relatedNode) return null
                return (
                  <div key={edge.id} className="border-t border-gray-700 pt-2">
                    <button
                      onClick={() => handleNodeClick(relatedNode)}
                      className="w-full text-left px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs flex items-center gap-2"
                    >
                      <Link className="w-3 h-3 text-blue-400" />
                      <span>{relatedNode.label}</span>
                      <span className="ml-auto text-gray-500 capitalize">{edge.type.replace('_', ' ')}</span>
                    </button>
                  </div>
                )
              })}
          </div>
        </div>
      )}
        </>
      )}
    </div>
    </ErrorBoundary>
  )
})

