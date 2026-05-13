// Evolution Explorer Panel
// Visualizes evolution of ideas, code, and knowledge over time
// V2 Enhancement - Bidirectional Graph (Timeline ↔ Chain)

import React, { useState, useEffect, useCallback, useMemo } from 'react'
import {
  GitBranch,
  TrendingUp,
  Clock,
  Search,
  Filter,
  RefreshCw,
  ZoomIn,
  ZoomOut,
  Calendar,
  ArrowRight,
  Layers,
  Sparkles,
  Target,
  Network,
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
import { Shield } from 'lucide-react'

interface EvolutionNode {
  id: string
  label: string
  content: string
  timestamp: Date
  version: number
  confidence: number
  tags: string[]
  parentId?: string
  childrenIds: string[]
  evolutionType: 'refined' | 'expanded' | 'merged' | 'split' | 'replaced'
  nodeType: 'timeline' | 'chain' | 'goal' // Bidirectional graph support
  chainId?: string // If connected to a chain
  timelineEntryId?: string // If connected to timeline
  goalId?: string // If connected to a goal
}

interface EvolutionEdge {
  id: string
  source: string
  target: string
  type: 'evolved_into' | 'merged_from' | 'split_into' | 'replaced_by' | 'executed_via' | 'produced' | 'achieves'
  timestamp: Date
  strength: number
  bidirectional?: boolean // For Timeline ↔ Chain connections
}

interface EvolutionExplorerProps {
  onNodeClick?: (node: EvolutionNode) => void
  onNodeSelect?: (node: EvolutionNode | null) => void
}

export const EvolutionExplorer: React.FC<EvolutionExplorerProps> = React.memo(({
  onNodeClick,
  onNodeSelect
}) => {
  const [nodes, setNodes] = useState<EvolutionNode[]>([])
  const [edges, setEdges] = useState<EvolutionEdge[]>([])
  const [selectedNode, setSelectedNode] = useState<EvolutionNode | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<'all' | EvolutionNode['evolutionType']>('all')
  const [isLoading, setIsLoading] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [timeRange, setTimeRange] = useState<'all' | 'week' | 'month' | 'year'>('all')
  const [viewMode, setViewMode] = useState<'graph' | 'list'>('graph') // Graph or list view
  
  // React Flow state
  const [reactFlowNodes, setReactFlowNodes, onNodesChange] = useNodesState([])
  const [reactFlowEdges, setReactFlowEdges, onEdgesChange] = useEdgesState([])

  // AIM-OS integration
  const { tcs, vif, apoe, isConnected: aimosConnected, useMockData, loading } = useAIMOS()
  const timelineEntries = tcs?.entries || []
  
  // Load goals for bidirectional graph (Timeline ↔ Chain ↔ Goals)
  const goals = useMemo(() => {
    // This would come from APOE/goals API in real implementation
    return []
  }, [])

  // Load evolution data from AIM-OS
  const loadEvolutionData = useCallback(async () => {
    setIsLoading(true)
    try {
      if (timelineEntries && timelineEntries.length > 0) {
        // Build evolution graph from timeline entries
        const evolutionNodes: EvolutionNode[] = []
        const evolutionEdges: EvolutionEdge[] = []

        // Group timeline entries by topic/content similarity
        const groupedEntries = new Map<string, any[]>()
        
        timelineEntries.forEach((entry: any) => {
          const key = entry.user_input?.substring(0, 30) || entry.description?.substring(0, 30) || 'unknown'
          if (!groupedEntries.has(key)) {
            groupedEntries.set(key, [])
          }
          groupedEntries.get(key)!.push(entry)
        })

        // Create evolution nodes from grouped entries
        let nodeIndex = 0
        groupedEntries.forEach((entries, key) => {
          entries.sort((a, b) => {
            const timeA = new Date(a.timestamp || a.created_at || 0).getTime()
            const timeB = new Date(b.timestamp || b.created_at || 0).getTime()
            return timeA - timeB
          })

          entries.forEach((entry, idx) => {
            const timestamp = new Date(entry.timestamp || entry.created_at || Date.now())
            const node: EvolutionNode = {
              id: entry.prompt_id || entry.id || `evo-${nodeIndex++}`,
              label: entry.user_input?.substring(0, 50) || entry.description?.substring(0, 50) || `Evolution ${idx + 1}`,
              content: entry.user_input || entry.description || '',
              timestamp,
              version: idx + 1,
              confidence: entry.confidence || 0.8,
              tags: entry.tags || [],
              parentId: idx > 0 ? entries[idx - 1].prompt_id || entries[idx - 1].id : undefined,
              childrenIds: idx < entries.length - 1 ? [entries[idx + 1].prompt_id || entries[idx + 1].id] : [],
              evolutionType: idx === 0 ? 'refined' :
                           idx === entries.length - 1 ? 'expanded' :
                           Math.random() > 0.5 ? 'refined' : 'expanded',
              nodeType: entry.executed_via_chain_id ? 'timeline' : 'timeline', // Default to timeline, can be enhanced
              timelineEntryId: entry.prompt_id || entry.id,
              chainId: entry.executed_via_chain_id,
            }
            evolutionNodes.push(node)

            // Create edge from previous version
            if (idx > 0) {
              const prevEntry = entries[idx - 1]
              evolutionEdges.push({
                id: `edge-${prevEntry.prompt_id || prevEntry.id}-${node.id}`,
                source: prevEntry.prompt_id || prevEntry.id,
                target: node.id,
                type: 'evolved_into',
                timestamp,
                strength: 0.8
              })
            }
          })
        })

        setNodes(evolutionNodes)
        setEdges(evolutionEdges)
        setIsConnected(true)
      } else {
        // Fallback to mock data
        const mockData = generateMockEvolutionData()
        setNodes(mockData.nodes)
        setEdges(mockData.edges)
        setIsConnected(false)
      }
    } catch (error) {
      console.error('Failed to load evolution data:', error)
      const mockData = generateMockEvolutionData()
      setNodes(mockData.nodes)
      setEdges(mockData.edges)
      setIsConnected(false)
    } finally {
      setIsLoading(false)
    }
  }, [timelineEntries])

  useEffect(() => {
    loadEvolutionData()
  }, [loadEvolutionData])

  const filteredNodes = useMemo(() => {
    return nodes.filter(node => {
      const matchesSearch = searchTerm === '' ||
                            node.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            node.content.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesType = filterType === 'all' || node.evolutionType === filterType
      
      const now = Date.now()
      const nodeTime = node.timestamp.getTime()
      const matchesTimeRange = timeRange === 'all' ||
                              (timeRange === 'week' && (now - nodeTime) <= 7 * 24 * 60 * 60 * 1000) ||
                              (timeRange === 'month' && (now - nodeTime) <= 30 * 24 * 60 * 60 * 1000) ||
                              (timeRange === 'year' && (now - nodeTime) <= 365 * 24 * 60 * 60 * 1000)
      
      return matchesSearch && matchesType && matchesTimeRange
    })
  }, [nodes, searchTerm, filterType, timeRange])

  const filteredEdges = useMemo(() => {
    const filteredNodeIds = new Set(filteredNodes.map(n => n.id))
    return edges.filter(edge => 
      filteredNodeIds.has(edge.source) && filteredNodeIds.has(edge.target)
    )
  }, [edges, filteredNodes])

  const handleNodeClick = useCallback((node: EvolutionNode) => {
    setSelectedNode(node)
    onNodeClick?.(node)
    onNodeSelect?.(node)
  }, [onNodeClick, onNodeSelect])

  const getEvolutionColor = (type: EvolutionNode['evolutionType']) => {
    switch (type) {
      case 'refined': return 'bg-blue-500/20 border-blue-500'
      case 'expanded': return 'bg-green-500/20 border-green-500'
      case 'merged': return 'bg-purple-500/20 border-purple-500'
      case 'split': return 'bg-orange-500/20 border-orange-500'
      case 'replaced': return 'bg-red-500/20 border-red-500'
      default: return 'bg-gray-500/20 border-gray-500'
    }
  }

  const getEvolutionIcon = (type: EvolutionNode['evolutionType']) => {
    switch (type) {
      case 'refined': return <TrendingUp className="w-4 h-4 text-blue-400" />
      case 'expanded': return <Layers className="w-4 h-4 text-green-400" />
      case 'merged': return <Sparkles className="w-4 h-4 text-purple-400" />
      case 'split': return <GitBranch className="w-4 h-4 text-orange-400" />
      case 'replaced': return <ArrowRight className="w-4 h-4 text-red-400" />
      default: return <Clock className="w-4 h-4 text-gray-400" />
    }
  }

  // Custom Evolution Node Component for React Flow
  const EvolutionNodeComponent: React.FC<NodeProps> = ({ data, selected }) => {
    const node = data.node as EvolutionNode
    const EvolutionIcon = getEvolutionIcon(node.evolutionType)
    const nodeTypeColor = node.nodeType === 'timeline' ? 'border-blue-500' :
                         node.nodeType === 'chain' ? 'border-purple-500' :
                         'border-yellow-500'
    const nodeTypeBg = node.nodeType === 'timeline' ? 'bg-blue-500/10' :
                      node.nodeType === 'chain' ? 'bg-purple-500/10' :
                      'bg-yellow-500/10'
    
    return (
      <div
        className={`px-3 py-2 rounded-lg border-2 min-w-[160px] max-w-[200px] cursor-pointer transition-all ${
          selected
            ? 'bg-green-500/30 border-green-400 shadow-lg shadow-green-500/50'
            : `${getEvolutionColor(node.evolutionType)} ${nodeTypeBg} ${nodeTypeColor}`
        }`}
        style={{
          boxShadow: selected ? '0 0 20px rgba(34, 197, 94, 0.5)' : undefined,
        }}
      >
        <Handle type="target" position={Position.Top} className="w-2 h-2" />
        <div className="flex items-center gap-2 mb-1">
          {EvolutionIcon}
          <span className="text-xs font-semibold text-white truncate">
            {node.label.length > 25 ? node.label.substring(0, 22) + '...' : node.label}
          </span>
        </div>
        <div className="flex items-center justify-between text-xs text-gray-300 mb-1">
          <span className={`px-1 py-0.5 rounded text-[10px] ${nodeTypeBg}`}>
            {node.nodeType === 'timeline' ? '📅' : node.nodeType === 'chain' ? '🔗' : '🎯'}
          </span>
          <span className="text-gray-400">v{node.version}</span>
        </div>
        <div className="flex items-center justify-between text-xs text-gray-300 mb-1">
          <span>{node.timestamp.toLocaleDateString()}</span>
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
                className="px-1 py-0.5 bg-gray-700 text-gray-300 text-[10px] rounded"
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
    evolutionNode: EvolutionNodeComponent,
  }), [])

  // Convert EvolutionNodes/Edges to React Flow format
  useEffect(() => {
    if (filteredNodes.length === 0 || viewMode !== 'graph') {
      setReactFlowNodes([])
      setReactFlowEdges([])
      return
    }

    // Convert nodes to React Flow format with hierarchical layout
    // Timeline nodes on left, Chain nodes in middle, Goal nodes on right
    const timelineNodes = filteredNodes.filter(n => n.nodeType === 'timeline')
    const chainNodes = filteredNodes.filter(n => n.nodeType === 'chain')
    const goalNodes = filteredNodes.filter(n => n.nodeType === 'goal')
    
    const initialNodes: Node[] = []
    const spacing = 250
    const verticalSpacing = 150
    
    // Layout Timeline nodes (left column)
    timelineNodes.forEach((node, idx) => {
      initialNodes.push({
        id: node.id,
        type: 'evolutionNode',
        position: { x: 50, y: 50 + idx * verticalSpacing },
        data: { node },
        selected: selectedNode?.id === node.id,
      })
    })
    
    // Layout Chain nodes (middle column)
    chainNodes.forEach((node, idx) => {
      initialNodes.push({
        id: node.id,
        type: 'evolutionNode',
        position: { x: 50 + spacing, y: 50 + idx * verticalSpacing },
        data: { node },
        selected: selectedNode?.id === node.id,
      })
    })
    
    // Layout Goal nodes (right column)
    goalNodes.forEach((node, idx) => {
      initialNodes.push({
        id: node.id,
        type: 'evolutionNode',
        position: { x: 50 + spacing * 2, y: 50 + idx * verticalSpacing },
        data: { node },
        selected: selectedNode?.id === node.id,
      })
    })
    
    // Convert edges to React Flow format with bidirectional support
    const initialEdges: Edge[] = filteredEdges.map((edge) => {
      const edgeColor = getEdgeColorHex(edge.type)
      return {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        type: 'smoothstep',
        animated: edge.type === 'evolved_into' || edge.type === 'produced',
        style: {
          strokeWidth: edge.strength * 3,
          stroke: edgeColor,
          opacity: 0.7,
        },
        label: edge.type.replace('_', ' '),
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: edgeColor,
        },
        // Bidirectional edges show both directions
        ...(edge.bidirectional && {
          markerStart: {
            type: MarkerType.ArrowClosed,
            color: edgeColor,
          },
        }),
      }
    })

    setReactFlowNodes(initialNodes)
    setReactFlowEdges(initialEdges)
  }, [filteredNodes, filteredEdges, selectedNode, viewMode, setReactFlowNodes, setReactFlowEdges])

  const getEdgeColorHex = (type: EvolutionEdge['type']): string => {
    switch (type) {
      case 'evolved_into': return '#3b82f6' // blue-500
      case 'merged_from': return '#a78bfa' // purple-400
      case 'split_into': return '#f97316' // orange-500
      case 'replaced_by': return '#ef4444' // red-500
      case 'executed_via': return '#10b981' // green-500 (Timeline → Chain)
      case 'produced': return '#fbbf24' // yellow-400 (Chain → Timeline)
      case 'achieves': return '#f59e0b' // yellow-500 (Chain → Goal)
      default: return '#9ca3af' // gray-400
    }
  }

  const handleReactFlowNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    const evolutionNode = node.data.node as EvolutionNode
    handleNodeClick(evolutionNode)
  }, [handleNodeClick])

  // Render graph view with React Flow
  const renderGraphView = useCallback(() => {
    if (filteredNodes.length === 0) {
      return (
        <div className="flex items-center justify-center h-full text-gray-400">
          <div className="text-center">
            <GitBranch className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No evolution data found</p>
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
              const evolutionNode = node.data?.node as EvolutionNode
              if (!evolutionNode) return '#6b7280'
              switch (evolutionNode.nodeType) {
                case 'timeline': return '#3b82f6' // blue
                case 'chain': return '#a78bfa' // purple
                case 'goal': return '#fbbf24' // yellow
                default: return '#6b7280'
              }
            }}
            maskColor="rgba(0, 0, 0, 0.6)"
          />
        </ReactFlow>
      </ReactFlowProvider>
    )
  }, [filteredNodes, reactFlowNodes, reactFlowEdges, onNodesChange, onEdgesChange, handleReactFlowNodeClick, nodeTypes])

  // Render list view (original implementation)
  const renderListView = useCallback(() => {
    if (filteredNodes.length === 0) {
      return (
        <div className="flex items-center justify-center h-full text-gray-400">
          <div className="text-center">
            <GitBranch className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No evolution data found</p>
            <p className="text-xs mt-1">Try adjusting filters or search</p>
          </div>
        </div>
      )
    }

    return (
      <div className="space-y-4 p-4">
        {filteredNodes.map((node) => {
          const nodeEdges = filteredEdges.filter(e => e.target === node.id)
          const parentNode = nodeEdges.length > 0 
            ? filteredNodes.find(n => n.id === nodeEdges[0].source)
            : null

          return (
            <div
              key={node.id}
              onClick={() => handleNodeClick(node)}
              className={`p-4 rounded-lg border cursor-pointer transition-all ${
                selectedNode?.id === node.id
                  ? 'bg-green-500/20 border-green-500'
                  : 'bg-gray-800 border-gray-700 hover:bg-gray-750'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getEvolutionIcon(node.evolutionType)}
                  <span className="text-sm font-medium text-gray-300">{node.label}</span>
                  <span className={`text-xs px-2 py-1 rounded ${getEvolutionColor(node.evolutionType)}`}>
                    v{node.version}
                  </span>
                  <span className={`text-xs px-1 py-0.5 rounded ${
                    node.nodeType === 'timeline' ? 'bg-blue-500/20 text-blue-400' :
                    node.nodeType === 'chain' ? 'bg-purple-500/20 text-purple-400' :
                    'bg-yellow-500/20 text-yellow-400'
                  }`}>
                    {node.nodeType === 'timeline' ? '📅' : node.nodeType === 'chain' ? '🔗' : '🎯'}
                  </span>
                </div>
                <span className="text-xs text-gray-400">
                  {node.timestamp.toLocaleDateString()}
                </span>
              </div>

              {parentNode && (
                <div className="text-xs text-gray-400 mb-2 flex items-center gap-1">
                  <ArrowRight className="w-3 h-3" />
                  Evolved from: {parentNode.label.substring(0, 40)}...
                </div>
              )}

              <div className="text-xs text-gray-400 mb-2">
                {node.content.substring(0, 100)}...
              </div>

              <div className="flex items-center gap-2 mt-2">
                <span className={`text-xs flex items-center gap-1 ${
                  node.confidence >= 0.95 ? 'text-green-400' :
                  node.confidence >= 0.90 ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  <Shield className="w-3 h-3" />
                  {(node.confidence * 100).toFixed(0)}%
                </span>
                {node.tags.length > 0 && (
                  <div className="flex gap-1">
                    {node.tags.slice(0, 3).map(tag => (
                      <span key={tag} className="text-xs px-1 py-0.5 bg-gray-700 rounded text-gray-400">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    )
  }, [filteredNodes, filteredEdges, selectedNode, handleNodeClick])

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-900 text-gray-200">
        {isLoading || loading.tcs ? (
          <LoadingState message="Loading evolution data..." />
        ) : (
          <>
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 flex items-center gap-2 shrink-0">
        <GitBranch className="w-5 h-5 text-green-400" />
        <div>
          <div className="text-white text-sm font-semibold">Evolution Explorer ⭐</div>
          <div className="text-xs text-gray-500">Timeline & Evidence Integration</div>
        </div>
        <span
          className={`ml-auto px-2 py-1 rounded-full text-xs font-medium ${
            isConnected ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
          }`}
        >
          {isConnected ? 'Connected' : 'Mock Mode'}
        </span>
        <button
          onClick={() => setViewMode(viewMode === 'graph' ? 'list' : 'graph')}
          className="text-gray-400 hover:text-white p-1 rounded"
          title={`Switch to ${viewMode === 'graph' ? 'list' : 'graph'} view`}
        >
          {viewMode === 'graph' ? <Layers className="w-4 h-4" /> : <Network className="w-4 h-4" />}
        </button>
        <button onClick={loadEvolutionData} className="text-gray-400 hover:text-white p-1 rounded">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Search and Filters */}
      <div className="p-3 border-b border-gray-700 shrink-0 space-y-2">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search evolution..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-gray-800 text-white text-sm px-9 py-2 rounded focus:outline-none focus:ring-2 focus:ring-green-500 border border-gray-700"
          />
        </div>

        <div className="flex gap-2 overflow-x-auto pb-1">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value as any)}
            className="px-3 py-1 text-xs rounded bg-gray-700 text-gray-300 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="all">All Types</option>
            <option value="refined">Refined</option>
            <option value="expanded">Expanded</option>
            <option value="merged">Merged</option>
            <option value="split">Split</option>
            <option value="replaced">Replaced</option>
          </select>

          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as any)}
            className="px-3 py-1 text-xs rounded bg-gray-700 text-gray-300 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="all">All Time</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="year">This Year</option>
          </select>
        </div>
      </div>

      {/* Evolution Graph/List View */}
      <div className="flex-1 overflow-hidden">
        {viewMode === 'graph' ? renderGraphView() : renderListView()}
      </div>

      {/* Selected Node Details */}
      {selectedNode && (
        <div className="border-t border-gray-700 p-4 bg-gray-800 shrink-0 max-h-48 overflow-auto">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-semibold text-gray-300">Evolution Details</h4>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-gray-400 hover:text-gray-200"
            >
              ×
            </button>
          </div>
          <div className="text-xs text-gray-400 space-y-1">
            <div>ID: {selectedNode.id}</div>
            <div>Type: {selectedNode.evolutionType}</div>
            <div>Version: {selectedNode.version}</div>
            <div>Timestamp: {selectedNode.timestamp.toISOString()}</div>
            <div className="flex items-center gap-2">
              <span className="text-gray-400">Confidence (VIF):</span>
              <span className={`flex items-center gap-1 ${
                selectedNode.confidence >= 0.95 ? 'text-green-400' :
                selectedNode.confidence >= 0.90 ? 'text-yellow-400' :
                'text-red-400'
              }`}>
                <Shield className="w-3 h-3" />
                {(selectedNode.confidence * 100).toFixed(0)}%
              </span>
            </div>
            <div className="mt-2">
              <div className="font-medium text-gray-300 mb-1">Content:</div>
              <pre className="text-xs text-gray-400 whitespace-pre-wrap">{selectedNode.content}</pre>
            </div>
          </div>
        </div>
      )}
          </>
        )}
    </div>
    </ErrorBoundary>
  )
})

// Mock data generator
function generateMockEvolutionData(): { nodes: EvolutionNode[]; edges: EvolutionEdge[] } {
  const nodes: EvolutionNode[] = [
    {
      id: 'evo-001',
      label: 'Initial Concept',
      content: 'Initial idea for context web visualization',
      timestamp: new Date('2025-10-15'),
      version: 1,
      confidence: 0.7,
      tags: ['concept', 'visualization'],
      childrenIds: ['evo-002'],
      evolutionType: 'refined',
      nodeType: 'timeline',
    },
    {
      id: 'evo-002',
      label: 'Refined Concept',
      content: 'Enhanced concept with AIM-OS integration',
      timestamp: new Date('2025-10-20'),
      version: 2,
      confidence: 0.85,
      tags: ['concept', 'visualization', 'aimos'],
      parentId: 'evo-001',
      childrenIds: ['evo-003'],
      evolutionType: 'expanded',
      nodeType: 'chain',
      chainId: 'chain-001',
    },
    {
      id: 'evo-003',
      label: 'Implementation',
      content: 'Full implementation with real AIM-OS data',
      timestamp: new Date('2025-11-07'),
      version: 3,
      confidence: 0.95,
      tags: ['implementation', 'aimos', 'production'],
      parentId: 'evo-002',
      childrenIds: [],
      evolutionType: 'refined',
      nodeType: 'timeline',
      timelineEntryId: 'timeline-003',
    }
  ]

  const edges: EvolutionEdge[] = [
    {
      id: 'edge-001',
      source: 'evo-001',
      target: 'evo-002',
      type: 'evolved_into',
      timestamp: new Date('2025-10-20'),
      strength: 0.8
    },
    {
      id: 'edge-002',
      source: 'evo-002',
      target: 'evo-003',
      type: 'produced',
      timestamp: new Date('2025-11-07'),
      strength: 0.9,
      bidirectional: true
    }
  ]

  return { nodes, edges }
}

