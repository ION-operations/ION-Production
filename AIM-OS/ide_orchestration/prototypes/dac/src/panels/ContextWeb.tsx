// Context Web Panel - V2 Enhanced
// Revolutionary UX - Interactive SEG knowledge graph visualization with topic evolution tracking

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import ReactFlow, { 
  Node, 
  Edge, 
  Background, 
  Controls, 
  MiniMap, 
  ConnectionMode, 
  useNodesState, 
  useEdgesState,
  ReactFlowProvider,
  MarkerType
} from 'reactflow'
import 'reactflow/dist/style.css'
import * as d3 from 'd3'
import { BasePanel } from '../components/BasePanel'
import { useContextWeb, useSEG, useHHNI, useTCS } from '../hooks/useAIMOS'
import { Network, Search, Zap, Brain, AlertTriangle, GitBranch, TrendingUp, Clock, Filter, Maximize2 } from 'lucide-react'
import type { SEGEntity, SEGRelation, SEGContradiction } from '../hooks/useAIMOS'

export const ContextWeb: React.FC = () => {
  const { buildContextWeb } = useContextWeb()
  const { entities, relations, contradictions } = useSEG()
  const { search } = useHHNI()
  const { getSummary } = useTCS()
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [query, setQuery] = useState('IDE prototype AIM-OS integration')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<any>(null)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [layout, setLayout] = useState<'force' | 'hierarchical' | 'circular'>('force')
  const [showTopicEvolution, setShowTopicEvolution] = useState(false)
  const [topicHistory, setTopicHistory] = useState<Map<string, number[]>>(new Map())
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d' | 'all'>('24h')
  const [filterType, setFilterType] = useState<Set<string>>(new Set(['claim', 'source', 'derivation', 'agent']))
  const [nodeClusterMode, setNodeClusterMode] = useState<'none' | 'type' | 'confidence' | 'topic' | 'community'>('type')
  const [expandedClusters, setExpandedClusters] = useState<Set<string>>(new Set())
  const [focusedNode, setFocusedNode] = useState<string | null>(null)
  const [zoomLevel, setZoomLevel] = useState(1)
  const [showNodeLabels, setShowNodeLabels] = useState(true)
  const [highlightPath, setHighlightPath] = useState<string[]>([])
  const [searchHighlight, setSearchHighlight] = useState<string>('')
  const reactFlowWrapperRef = useRef<HTMLDivElement>(null)
  
  // Helper functions (must be defined before useCallback)
  const getEntityColor = (type: string) => {
    switch (type) {
      case 'claim': return '#3b82f6'  // Blue
      case 'source': return '#10b981'  // Green
      case 'derivation': return '#f59e0b'  // Yellow
      case 'agent': return '#8b5cf6'  // Purple
      default: return '#6b7280'  // Gray
    }
  }
  
  const getRelationColor = (type: string) => {
    switch (type) {
      case 'SUPPORTS': return '#10b981'  // Green
      case 'CONTRADICTS': return '#ef4444'  // Red
      case 'DERIVES_FROM': return '#3b82f6'  // Blue
      case 'REFERENCES': return '#f59e0b'  // Yellow
      case 'RELATES_TO': return '#8b5cf6'  // Purple
      default: return '#6b7280'  // Gray
    }
  }
  
  // Enhanced D3 force simulation with better physics
  const applyForceLayout = useCallback((nodes: Node[], edges: Edge[]) => {
    if (nodes.length === 0) return nodes
    
    // Enhanced D3 force simulation with adaptive parameters
    const nodeCount = nodes.length
    const edgeCount = edges.length
    const density = edgeCount / (nodeCount * nodeCount)
    
    // Adaptive force parameters based on graph density
    const linkDistance = density > 0.1 ? 120 : 180
    const chargeStrength = density > 0.1 ? -400 : -250
    const collisionRadius = 90
    
    const simulation = d3.forceSimulation(nodes as any)
      .force('link', d3.forceLink(edges)
        .id((d: any) => d.id)
        .distance(linkDistance)
        .strength(0.5))
      .force('charge', d3.forceManyBody()
        .strength(chargeStrength)
        .distanceMax(500))
      .force('center', d3.forceCenter(500, 400))
      .force('collision', d3.forceCollide().radius(collisionRadius))
      .force('x', d3.forceX(500).strength(0.1))
      .force('y', d3.forceY(400).strength(0.1))
    
    // Run simulation with more iterations for better convergence
    simulation.tick(400)
    
    // Alpha decay for smoother animation
    simulation.alphaDecay(0.02)
    
    return nodes.map(node => ({
      ...node,
      position: {
        x: (node as any).x || node.position.x,
        y: (node as any).y || node.position.y
      }
    }))
  }, [])
  
  const applyHierarchicalLayout = useCallback((nodes: Node[], edges: Edge[]) => {
    if (nodes.length === 0) return nodes
    
    // Build adjacency list
    const adjList = new Map<string, string[]>()
    nodes.forEach(node => adjList.set(node.id, []))
    edges.forEach(edge => {
      const sourceList = adjList.get(edge.source) || []
      sourceList.push(edge.target)
      adjList.set(edge.source, sourceList)
    })
    
    // Topological sort for hierarchical positioning
    const levels = new Map<string, number>()
    const visited = new Set<string>()
    
    const dfs = (nodeId: string, level: number) => {
      if (visited.has(nodeId)) return
      visited.add(nodeId)
      levels.set(nodeId, Math.max(levels.get(nodeId) || 0, level))
      const neighbors = adjList.get(nodeId) || []
      neighbors.forEach(neighbor => dfs(neighbor, level + 1))
    }
    
    nodes.forEach(node => {
      if (!visited.has(node.id)) {
        dfs(node.id, 0)
      }
    })
    
    // Position nodes by level
    const levelGroups = new Map<number, Node[]>()
    nodes.forEach(node => {
      const level = levels.get(node.id) || 0
      const group = levelGroups.get(level) || []
      group.push(node)
      levelGroups.set(level, group)
    })
    
    const maxLevel = Math.max(...Array.from(levelGroups.keys()))
    const levelHeight = 400 / Math.max(1, maxLevel + 1)
    
    return nodes.map(node => {
      const level = levels.get(node.id) || 0
      const levelNodes = levelGroups.get(level) || []
      const indexInLevel = levelNodes.indexOf(node)
      const nodesInLevel = levelNodes.length
      const levelWidth = 800
      const nodeSpacing = levelWidth / Math.max(1, nodesInLevel + 1)
      
      return {
        ...node,
        position: {
          x: nodeSpacing * (indexInLevel + 1),
          y: level * levelHeight + 100
        }
      }
    })
  }, [])
  
  const applyCircularLayout = useCallback((nodes: Node[]) => {
    if (nodes.length === 0) return nodes
    
    const centerX = 400
    const centerY = 300
    const radius = Math.min(300, Math.max(150, nodes.length * 15))
    const angleStep = (2 * Math.PI) / nodes.length
    
    return nodes.map((node, index) => ({
      ...node,
      position: {
        x: centerX + radius * Math.cos(index * angleStep),
        y: centerY + radius * Math.sin(index * angleStep)
      }
    }))
  }, [])
  
  // Enhanced node clustering with community detection
  const clusterNodes = useCallback((nodes: Node[], edges: Edge[], mode: 'none' | 'type' | 'confidence' | 'topic' | 'community') => {
    if (mode === 'none') return nodes
    
    const clusters = new Map<string, Node[]>()
    
    // Community detection using simple label propagation
    if (mode === 'community') {
      const nodeCommunities = new Map<string, string>()
      nodes.forEach(node => nodeCommunities.set(node.id, node.id))
      
      // Iterative label propagation
      for (let iter = 0; iter < 10; iter++) {
        const newCommunities = new Map<string, Map<string, number>>()
        
        edges.forEach(edge => {
          const sourceComm = nodeCommunities.get(edge.source)!
          const targetComm = nodeCommunities.get(edge.target)!
          
          if (!newCommunities.has(sourceComm)) {
            newCommunities.set(sourceComm, new Map())
          }
          if (!newCommunities.has(targetComm)) {
            newCommunities.set(targetComm, new Map())
          }
          
          newCommunities.get(sourceComm)!.set(targetComm, (newCommunities.get(sourceComm)!.get(targetComm) || 0) + 1)
          newCommunities.get(targetComm)!.set(sourceComm, (newCommunities.get(targetComm)!.get(sourceComm) || 0) + 1)
        })
        
        // Update communities based on neighbors
        nodes.forEach(node => {
          const neighborComms = new Map<string, number>()
          edges.forEach(edge => {
            if (edge.source === node.id) {
              const comm = nodeCommunities.get(edge.target)!
              neighborComms.set(comm, (neighborComms.get(comm) || 0) + 1)
            }
            if (edge.target === node.id) {
              const comm = nodeCommunities.get(edge.source)!
              neighborComms.set(comm, (neighborComms.get(comm) || 0) + 1)
            }
          })
          
          if (neighborComms.size > 0) {
            const maxComm = Array.from(neighborComms.entries())
              .sort((a, b) => b[1] - a[1])[0][0]
            nodeCommunities.set(node.id, maxComm)
          }
        })
      }
      
      // Group nodes by community
      nodeCommunities.forEach((comm, nodeId) => {
        const node = nodes.find(n => n.id === nodeId)
        if (node) {
          const cluster = clusters.get(comm) || []
          cluster.push(node)
          clusters.set(comm, cluster)
        }
      })
    } else {
      // Standard clustering modes
      nodes.forEach(node => {
        let clusterKey = 'default'
        
        if (mode === 'type') {
          clusterKey = node.data?.type || 'unknown'
        } else if (mode === 'confidence') {
          const conf = node.data?.confidence || 0.75
          clusterKey = conf >= 0.90 ? 'high' : conf >= 0.70 ? 'medium' : 'low'
        } else if (mode === 'topic') {
          clusterKey = node.data?.topic || 'general'
        }
        
        const cluster = clusters.get(clusterKey) || []
        cluster.push(node)
        clusters.set(clusterKey, cluster)
      })
    }
    
    // Position nodes within clusters with improved layout
    const clusteredNodes: Node[] = []
    let clusterIndex = 0
    const clusterCount = clusters.size
    const cols = Math.ceil(Math.sqrt(clusterCount))
    
    clusters.forEach((clusterNodes, clusterKey) => {
      const col = clusterIndex % cols
      const row = Math.floor(clusterIndex / cols)
      const clusterCenterX = 300 + col * 500
      const clusterCenterY = 250 + row * 400
      
      // Use force-directed layout within cluster
      if (clusterNodes.length > 1) {
        const clusterEdges = edges.filter(e => 
          clusterNodes.some(n => n.id === e.source || n.id === e.target)
        )
        
        const clusterSim = d3.forceSimulation(clusterNodes as any)
          .force('link', d3.forceLink(clusterEdges).id((d: any) => d.id).distance(80))
          .force('charge', d3.forceManyBody().strength(-100))
          .force('center', d3.forceCenter(clusterCenterX, clusterCenterY))
          .force('collision', d3.forceCollide().radius(50))
        
        clusterSim.tick(100)
      }
      
      clusterNodes.forEach((node, nodeIndex) => {
        if (clusterNodes.length === 1) {
          clusteredNodes.push({
            ...node,
            position: { x: clusterCenterX, y: clusterCenterY },
            data: { ...node.data, cluster: clusterKey }
          })
        } else {
          clusteredNodes.push({
            ...node,
            position: {
              x: (node as any).x || clusterCenterX,
              y: (node as any).y || clusterCenterY
            },
            data: { ...node.data, cluster: clusterKey }
          })
        }
      })
      
      clusterIndex++
    })
    
    return clusteredNodes
  }, [])
  
  // Find paths between nodes
  const findPath = useCallback((sourceId: string, targetId: string, edges: Edge[]) => {
    const adjList = new Map<string, string[]>()
    edges.forEach(edge => {
      const list = adjList.get(edge.source) || []
      list.push(edge.target)
      adjList.set(edge.source, list)
    })
    
    const visited = new Set<string>()
    const path: string[] = []
    
    const dfs = (current: string, target: string): boolean => {
      if (current === target) {
        path.push(current)
        return true
      }
      
      if (visited.has(current)) return false
      visited.add(current)
      path.push(current)
      
      const neighbors = adjList.get(current) || []
      for (const neighbor of neighbors) {
        if (dfs(neighbor, target)) {
          return true
        }
      }
      
      path.pop()
      return false
    }
    
    if (dfs(sourceId, targetId)) {
      return path
    }
    
    return []
  }, [])
  
  // Track topic evolution over time
  const trackTopicEvolution = useCallback(async () => {
    if (!showTopicEvolution) return
    
    try {
      const timelineSummary = await getSummary(100)
      const topicCounts = new Map<string, number[]>()
      
      // Group timeline entries by time windows
      const windows = {
        '1h': Date.now() - 3600000,
        '6h': Date.now() - 21600000,
        '24h': Date.now() - 86400000,
        '7d': Date.now() - 604800000,
      }
      
      const cutoff = windows[timeRange] || 0
      
      timelineSummary
        .filter(entry => new Date(entry.timestamp).getTime() >= cutoff)
        .forEach(entry => {
          // Extract topics from entry
          const topics = entry.tags || []
          topics.forEach(topic => {
            if (!topicCounts.has(topic)) {
              topicCounts.set(topic, [])
            }
            const counts = topicCounts.get(topic)!
            counts.push(entry.entry_id)
          })
        })
      
      setTopicHistory(topicCounts)
    } catch (err) {
      console.error('Topic evolution tracking error:', err)
    }
  }, [showTopicEvolution, timeRange, getSummary])
  
  useEffect(() => {
    if (showTopicEvolution) {
      trackTopicEvolution()
      const interval = setInterval(trackTopicEvolution, 30000) // Update every 30s
      return () => clearInterval(interval)
    }
  }, [showTopicEvolution, trackTopicEvolution])
  
  const loadContextWeb = useCallback(async () => {
    setLoading(true)
    try {
      // Build context web from query
      const result = await buildContextWeb(query)
      
      // Enhance with SEG entities and relations
      const segNodes: Node[] = []
      const segEdges: Edge[] = []
      
      // Add SEG entities as nodes
      const entityMap = new Map<string, Node>()
      entities.forEach((entity, index) => {
        const nodeId = `entity_${entity.id}`
        const node: Node = {
          id: nodeId,
          type: 'default',
          position: {
            x: (index % 5) * 200 + Math.random() * 50,
            y: Math.floor(index / 5) * 150 + Math.random() * 50
          },
          data: {
            label: entity.name,
            type: entity.type,
            entity: entity,
            confidence: 0.85
          },
          style: {
            background: getEntityColor(entity.type),
            color: '#fff',
            border: '2px solid #1f2937',
            borderRadius: '8px',
            padding: '12px',
            minWidth: '180px',
            fontSize: '12px'
          }
        }
        entityMap.set(entity.id, node)
        segNodes.push(node)
      })
      
      // Add SEG relations as edges
      relations.forEach((relation, index) => {
        const sourceNode = entityMap.get(relation.source_id)
        const targetNode = entityMap.get(relation.target_id)
        
        if (sourceNode && targetNode) {
          const edge: Edge = {
            id: `edge_${relation.id}`,
            source: sourceNode.id,
            target: targetNode.id,
            type: 'smoothstep',
            animated: relation.relation_type === 'CONTRADICTS',
            style: {
              stroke: getRelationColor(relation.relation_type),
              strokeWidth: Math.max(2, relation.confidence * 4),
              opacity: relation.confidence
            },
            label: `${relation.relation_type} (${(relation.confidence * 100).toFixed(0)}%)`,
            labelStyle: { fill: '#9ca3af', fontSize: 10 },
            data: {
              relation: relation,
              confidence: relation.confidence
            }
          }
          segEdges.push(edge)
        }
      })
      
      // Add contradiction highlights
      contradictions.forEach((contradiction) => {
        const sourceNode = entityMap.get(contradiction.entity1_id)
        const targetNode = entityMap.get(contradiction.entity2_id)
        
        if (sourceNode && targetNode) {
          // Find existing edge or create new one
          const existingEdge = segEdges.find(
            e => (e.source === sourceNode.id && e.target === targetNode.id) ||
                 (e.source === targetNode.id && e.target === sourceNode.id)
          )
          
          if (existingEdge) {
            existingEdge.style = {
              ...existingEdge.style,
              stroke: '#ef4444',
              strokeWidth: 4,
              strokeDasharray: '5,5',
              animation: 'pulse 2s infinite'
            }
            existingEdge.animated = true
            existingEdge.label = `CONTRADICTS (${(contradiction.confidence * 100).toFixed(0)}%)`
          }
        }
      })
      
      // Merge with HHNI search results
      const hhniResults = await search(query, 10)
      hhniResults.forEach((result, index) => {
        const nodeId = `hhni_${result.node.id}`
        const node: Node = {
          id: nodeId,
          type: 'default',
          position: {
            x: 800 + (index % 3) * 200,
            y: Math.floor(index / 3) * 150
          },
          data: {
            label: result.node.content.substring(0, 50),
            type: 'hhni_result',
            score: result.score,
            confidence: result.confidence
          },
          style: {
            background: result.confidence >= 0.85 ? '#10b981' : 
                       result.confidence >= 0.70 ? '#f59e0b' : '#ef4444',
            color: '#fff',
            border: '2px solid #1f2937',
            borderRadius: '8px',
            padding: '10px',
            minWidth: '150px',
            fontSize: '11px'
          }
        }
        segNodes.push(node)
      })
      
      // Filter nodes by type
      let filteredNodes = segNodes.filter(node => {
        const nodeType = node.data?.type
        return !nodeType || filterType.has(nodeType)
      })
      
      // Apply clustering with edges for community detection
      filteredNodes = clusterNodes(filteredNodes, segEdges, nodeClusterMode)
      
      // Apply layout algorithm
      if (layout === 'force') {
        filteredNodes = applyForceLayout(filteredNodes, segEdges)
      } else if (layout === 'hierarchical') {
        filteredNodes = applyHierarchicalLayout(filteredNodes, segEdges)
      } else if (layout === 'circular') {
        filteredNodes = applyCircularLayout(filteredNodes)
      }
      
      // Highlight search matches
      if (searchHighlight) {
        filteredNodes = filteredNodes.map(node => {
          const label = node.data?.label || ''
          const matches = label.toLowerCase().includes(searchHighlight.toLowerCase())
          return {
            ...node,
            style: {
              ...node.style,
              border: matches ? '3px solid #3b82f6' : node.style?.border,
              boxShadow: matches ? '0 0 10px rgba(59, 130, 246, 0.5)' : undefined
            }
          }
        })
      }
      
      // Highlight paths
      if (highlightPath.length > 0) {
        filteredNodes = filteredNodes.map(node => {
          const isInPath = highlightPath.includes(node.id)
          return {
            ...node,
            style: {
              ...node.style,
              border: isInPath ? '3px solid #10b981' : node.style?.border,
              boxShadow: isInPath ? '0 0 15px rgba(16, 185, 129, 0.6)' : node.style?.boxShadow
            }
          }
        })
        
        segEdges = segEdges.map(edge => {
          const sourceInPath = highlightPath.includes(edge.source)
          const targetInPath = highlightPath.includes(edge.target)
          const isInPath = sourceInPath && targetInPath
          
          return {
            ...edge,
            style: {
              ...edge.style,
              strokeWidth: isInPath ? 4 : edge.style?.strokeWidth,
              opacity: isInPath ? 1 : (edge.style?.opacity || 0.5)
            },
            animated: isInPath || edge.animated
          }
        })
      }
      
      setNodes(filteredNodes)
      setEdges(segEdges)
      setStats({
        entities: entities.length,
        relations: relations.length,
        contradictions: contradictions.length,
        hhni_results: hhniResults.length,
        total_nodes: segNodes.length,
        total_edges: segEdges.length
      })
    } catch (error) {
      console.error('Context Web load error:', error)
      setError(error instanceof Error ? error.message : 'Failed to load context web')
    } finally {
      setLoading(false)
    }
  }, [query, entities, relations, contradictions, buildContextWeb, search, filterType, nodeClusterMode, layout, searchHighlight, highlightPath, clusterNodes, applyForceLayout, applyHierarchicalLayout, applyCircularLayout])
  
  // Load context web when entities/relations are available
  useEffect(() => {
    // Only load when entities and relations are available
    if (entities.length > 0 || relations.length > 0) {
      loadContextWeb()
    }
  }, [loadContextWeb, entities.length, relations.length]) // Trigger when data is available
  
  const selectedNodeData = nodes.find(n => n.id === selectedNode)?.data
  
  // Calculate AIM-OS metrics
  const overallConfidence = nodes.length > 0
    ? nodes.reduce((sum, node) => sum + (node.data?.confidence || 0.75), 0) / nodes.length
    : undefined
  
  const confidenceBand = overallConfidence 
    ? (overallConfidence >= 0.90 ? 'A' : overallConfidence >= 0.70 ? 'B' : 'C')
    : undefined
  
  return (
    <BasePanel
      id="panel-context-web"
      title="Context Web"
      icon={Network}
      description="Interactive SEG knowledge graph visualization with HHNI integration and topic evolution tracking"
      loading={loading}
      error={error}
      empty={!loading && !error && nodes.length === 0}
      emptyMessage="Enter a query to build the context web graph"
      confidence={overallConfidence}
      confidenceBand={confidenceBand}
      contradictionCount={contradictions.length}
      footerContent={
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>
            {nodes.length} nodes, {edges.length} relationships
            {contradictions.length > 0 && `, ${contradictions.length} contradictions`}
          </span>
          <span className="text-green-400">SEG + HHNI Integration Active</span>
        </div>
      }
      headerClassName="p-3"
    >
      {/* Query Interface */}
      <div className="p-3 border-b border-gray-700 space-y-2">
        <div className="flex gap-2">
          <div className="flex-1 flex items-center gap-2 bg-gray-800 rounded px-2 py-1">
            <Search className="w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && loadContextWeb()}
              placeholder="Query context (Why? What? How?)..."
              className="flex-1 bg-transparent text-gray-300 placeholder-gray-500 text-sm outline-none"
            />
          </div>
          <button
            onClick={loadContextWeb}
            disabled={loading}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm text-white flex items-center gap-1 disabled:opacity-50"
          >
            <Zap className="w-4 h-4" />
            {loading ? 'Loading...' : 'Load'}
          </button>
        </div>
        
        {/* Layout Selector */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs text-gray-400">Layout:</span>
          {(['force', 'hierarchical', 'circular'] as const).map((layoutType) => (
            <button
              key={layoutType}
              onClick={() => setLayout(layoutType)}
              className={`px-2 py-0.5 rounded text-xs ${
                layout === layoutType
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {layoutType.charAt(0).toUpperCase() + layoutType.slice(1)}
            </button>
          ))}
          
          {/* Topic Evolution Toggle */}
          <button
            onClick={() => setShowTopicEvolution(!showTopicEvolution)}
            className={`px-2 py-0.5 rounded text-xs flex items-center gap-1 ${
              showTopicEvolution
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <TrendingUp className="w-3 h-3" />
            Evolution
          </button>
          
          {/* Time Range Selector */}
          {showTopicEvolution && (
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value as any)}
              className="px-2 py-0.5 rounded text-xs bg-gray-700 text-gray-300 border border-gray-600"
            >
              <option value="1h">Last Hour</option>
              <option value="6h">Last 6 Hours</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="all">All Time</option>
            </select>
          )}
          
          {/* Type Filter */}
          <div className="flex items-center gap-1">
            <Filter className="w-3 h-3 text-gray-400" />
            {['claim', 'source', 'derivation', 'agent'].map(type => (
              <button
                key={type}
                onClick={() => {
                  const newFilter = new Set(filterType)
                  if (newFilter.has(type)) {
                    newFilter.delete(type)
                  } else {
                    newFilter.add(type)
                  }
                  setFilterType(newFilter)
                }}
                className={`px-1.5 py-0.5 rounded text-xs ${
                  filterType.has(type)
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
          
          {/* Clustering Mode */}
          <div className="flex items-center gap-1">
            <span className="text-xs text-gray-400">Cluster:</span>
            {(['none', 'type', 'confidence', 'topic', 'community'] as const).map((mode) => (
              <button
                key={mode}
                onClick={() => setNodeClusterMode(mode)}
                className={`px-1.5 py-0.5 rounded text-xs ${
                  nodeClusterMode === mode
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {mode.charAt(0).toUpperCase() + mode.slice(1)}
              </button>
            ))}
          </div>
          
          {/* View Controls */}
          <div className="flex items-center gap-1">
            <button
              onClick={() => setShowNodeLabels(!showNodeLabels)}
              className={`px-2 py-0.5 rounded text-xs ${
                showNodeLabels
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              Labels
            </button>
            <button
              onClick={() => {
                // Fit view will be handled by ReactFlow's fitView prop
                window.dispatchEvent(new Event('resize'))
              }}
              className="px-2 py-0.5 rounded text-xs bg-gray-700 text-gray-300 hover:bg-gray-600 flex items-center gap-1"
            >
              <Maximize2 className="w-3 h-3" />
              Fit View
            </button>
          </div>
        </div>
        
        {/* Search Highlight */}
        <div className="flex items-center gap-2">
          <div className="flex-1 flex items-center gap-2 bg-gray-800 rounded px-2 py-1">
            <Search className="w-3 h-3 text-gray-400" />
            <input
              type="text"
              value={searchHighlight}
              onChange={(e) => setSearchHighlight(e.target.value)}
              placeholder="Highlight nodes..."
              className="flex-1 bg-transparent text-gray-300 placeholder-gray-500 text-xs outline-none"
            />
          </div>
          {searchHighlight && (
            <button
              onClick={() => setSearchHighlight('')}
              className="px-2 py-0.5 rounded text-xs bg-gray-700 text-gray-300 hover:bg-gray-600"
            >
              Clear
            </button>
          )}
        </div>
        
        {/* Topic Evolution Stats */}
        {showTopicEvolution && topicHistory.size > 0 && (
          <div className="flex gap-4 text-xs text-gray-400 flex-wrap">
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {topicHistory.size} topics tracked
            </span>
            {Array.from(topicHistory.entries())
              .sort((a, b) => b[1].length - a[1].length)
              .slice(0, 5)
              .map(([topic, counts]) => (
                <span key={topic} className="text-blue-400">
                  {topic}: {counts.length} mentions
                </span>
              ))}
          </div>
        )}
        
        {/* Stats */}
        {stats && (
          <div className="flex gap-4 text-xs text-gray-400 flex-wrap">
            <span className="flex items-center gap-1">
              <Brain className="w-3 h-3" />
              {stats.entities} entities
            </span>
            <span className="flex items-center gap-1">
              <GitBranch className="w-3 h-3" />
              {stats.relations} relations
            </span>
            {stats.contradictions > 0 && (
              <span className="flex items-center gap-1 text-red-400">
                <AlertTriangle className="w-3 h-3" />
                {stats.contradictions} contradictions
              </span>
            )}
            <span>{stats.hhni_results} HHNI results</span>
            <span>{stats.total_nodes} nodes, {stats.total_edges} edges</span>
          </div>
        )}
      </div>
      
      {/* Graph Visualization */}
      <div className="flex-1 relative" ref={reactFlowWrapperRef}>
        {nodes.length > 0 && (
          <ReactFlowProvider>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={(event, node) => {
                setSelectedNode(node.id)
                setFocusedNode(node.id)
                
                // Zoom to node
                if (reactFlowWrapperRef.current) {
                  const reactFlowInstance = (reactFlowWrapperRef.current as any).getReactFlowInstance?.()
                  if (reactFlowInstance) {
                    reactFlowInstance.fitView({ 
                      nodes: [{ id: node.id }],
                      padding: 0.2,
                      duration: 500
                    })
                  }
                }
                
                // Find paths from selected node to other nodes
                if (nodes.length > 1) {
                  const paths: string[] = []
                  nodes.forEach(otherNode => {
                    if (otherNode.id !== node.id) {
                      const path = findPath(node.id, otherNode.id, edges)
                      if (path.length > 0 && path.length <= 3) {
                        paths.push(...path)
                      }
                    }
                  })
                  setHighlightPath([...new Set(paths)])
                }
                
                // Expand cluster if node is in a cluster
                if (node.data?.cluster) {
                  const newExpanded = new Set(expandedClusters)
                  newExpanded.add(node.data.cluster)
                  setExpandedClusters(newExpanded)
                }
              }}
              onPaneClick={() => {
                setSelectedNode(null)
                setHighlightPath([])
              }}
              onMove={(event, viewport) => setZoomLevel(viewport.zoom)}
              fitView
              connectionMode={ConnectionMode.Loose}
              attributionPosition="bottom-left"
              minZoom={0.1}
              maxZoom={2}
              defaultEdgeOptions={{
                type: 'smoothstep',
                markerEnd: {
                  type: MarkerType.ArrowClosed,
                  width: 20,
                  height: 20
                }
              }}
              nodeTypes={{
                default: ({ data, selected }) => (
                  <div
                    className={`px-3 py-2 rounded-lg shadow-lg transition-all ${
                      selected ? 'ring-2 ring-blue-500' : ''
                    }`}
                    style={{
                      background: data.style?.background || '#6b7280',
                      color: data.style?.color || '#fff',
                      border: data.style?.border || '2px solid #1f2937',
                      minWidth: data.style?.minWidth || '120px',
                      fontSize: data.style?.fontSize || '12px',
                      boxShadow: data.style?.boxShadow
                    }}
                  >
                    {showNodeLabels && (
                      <div className="font-semibold mb-1">{data.label}</div>
                    )}
                    {data.confidence !== undefined && (
                      <div className="text-xs opacity-75">
                        {(data.confidence * 100).toFixed(0)}%
                      </div>
                    )}
                    {data.cluster && (
                      <div className="text-xs opacity-50 mt-1">
                        {data.cluster}
                      </div>
                    )}
                  </div>
                )
              }}
            >
              <Background color="#374151" gap={16} />
              <Controls />
              <MiniMap 
                nodeColor={(node) => {
                  if (node.data?.type === 'hhni_result') {
                    const confidence = node.data?.confidence || 0.70
                    return confidence >= 0.85 ? '#10b981' : 
                           confidence >= 0.70 ? '#f59e0b' : '#ef4444'
                  }
                  return getEntityColor(node.data?.type || 'default')
                }}
                style={{ backgroundColor: '#1f2937' }}
                pannable
                zoomable
              />
            </ReactFlow>
          </ReactFlowProvider>
        )}
        
        {/* Node Details Panel */}
            {selectedNodeData && (
              <div className="absolute top-4 right-4 w-64 bg-gray-800 border border-gray-700 rounded-lg p-3 shadow-xl">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-semibold text-gray-200">Node Details</h4>
                  <button
                    onClick={() => setSelectedNode(null)}
                    className="text-gray-400 hover:text-gray-200"
                  >
                    ×
                  </button>
                </div>
                <div className="space-y-2 text-xs">
                  <div>
                    <span className="text-gray-500">Type:</span>
                    <span className="ml-2 text-gray-300 capitalize">{selectedNodeData.type}</span>
                  </div>
                  {selectedNodeData.confidence !== undefined && (
                    <div>
                      <span className="text-gray-500">Confidence:</span>
                      <span className={`ml-2 ${
                        selectedNodeData.confidence >= 0.85 ? 'text-green-400' :
                        selectedNodeData.confidence >= 0.70 ? 'text-yellow-400' : 'text-red-400'
                      }`}>
                        {(selectedNodeData.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                  {selectedNodeData.score !== undefined && (
                    <div>
                      <span className="text-gray-500">Score:</span>
                      <span className="ml-2 text-gray-300">{(selectedNodeData.score * 100).toFixed(0)}%</span>
                    </div>
                  )}
                  {selectedNodeData.entity && (
                    <div className="pt-2 border-t border-gray-700">
                      <div className="text-gray-500 mb-1">Entity:</div>
                      <div className="text-gray-300 font-mono text-xs">
                        {selectedNodeData.entity.id}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
      </div>
    </BasePanel>
  )
}
