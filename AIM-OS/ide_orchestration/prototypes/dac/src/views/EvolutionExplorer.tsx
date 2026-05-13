// Evolution Explorer View - V2 Refactored with BasePanel
// Bidirectional Timeline ↔ Chain ↔ Goals visualization with ReactFlow

import React, { useState, useEffect, useCallback, useRef } from 'react'
import { BasePanel } from '../components/BasePanel'
import { useTCS, useAPOE } from '../hooks/useAIMOS'
import { GitBranch, Target, Clock, Network, Filter, Search, ZoomIn, ZoomOut, ArrowLeftRight, Maximize2 } from 'lucide-react'
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  NodeTypes,
  EdgeTypes,
  MarkerType,
  Position,
  ReactFlowProvider,
  useNodesState,
  useEdgesState
} from 'reactflow'
import 'reactflow/dist/style.css'
import * as d3 from 'd3'
import type { TimelineEntry } from '../hooks/useAIMOS'

// Extended Timeline Entry with chain/goal connections
interface EvolutionNode extends TimelineEntry {
  nodeType: 'timeline' | 'chain' | 'goal'
  chainId?: string
  chainExecutionId?: string
  chainNodeId?: string
  goalId?: string
  goalProgress?: number
  goalStatus?: 'planned' | 'in_progress' | 'completed' | 'blocked' | 'cancelled'
}

interface ChainExecution {
  id: string
  chainId: string
  chainName: string
  status: 'running' | 'completed' | 'failed' | 'paused'
  timelineEntryIds: string[]
  createdAt: string
  completedAt?: string
}

interface GoalNode {
  id: string
  goalId: string
  name: string
  description: string
  status: 'planned' | 'in_progress' | 'completed' | 'blocked' | 'cancelled'
  progress: number
  createdSequence: number
  currentSequence: number
  targetSequence: number
  linkedTimelineEntries: string[]
  linkedChains: string[]
}

export const EvolutionExplorer: React.FC = () => {
  const { getSummary, getTimelineGraph } = useTCS()
  const { createPlan, executePlan } = useAPOE()
  
  const [selectedView, setSelectedView] = useState<'timeline' | 'goals' | 'chains' | 'all'>('all')
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [filterStatus, setFilterStatus] = useState<Set<string>>(new Set(['in_progress', 'completed']))
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showBidirectional, setShowBidirectional] = useState(true)
  const [layout, setLayout] = useState<'force' | 'hierarchical' | 'timeline'>('force')
  const [highlightPath, setHighlightPath] = useState<string[]>([])
  const [temporalFilter, setTemporalFilter] = useState<'all' | 'past' | 'present' | 'future'>('all')
  const [timeRange, setTimeRange] = useState<{ start: Date | null; end: Date | null }>({ start: null, end: null })
  const reactFlowWrapperRef = useRef<HTMLDivElement>(null)
  
  // Layout algorithms
  const applyForceLayout = useCallback((nodes: Node[], edges: Edge[]) => {
    if (nodes.length === 0) return nodes
    
    const simulation = d3.forceSimulation(nodes as any)
      .force('link', d3.forceLink(edges).id((d: any) => d.id).distance(200))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(500, 400))
      .force('collision', d3.forceCollide().radius(100))
    
    simulation.tick(300)
    
    return nodes.map(node => ({
      ...node,
      position: {
        x: (node as any).x || node.position.x,
        y: (node as any).y || node.position.y
      }
    }))
  }, [])
  
  const applyHierarchicalLayout = useCallback((nodes: Node[]) => {
    if (nodes.length === 0) return nodes
    
    // Group by node type
    const timelineNodes = nodes.filter(n => n.data?.nodeType === 'timeline')
    const chainNodes = nodes.filter(n => n.data?.nodeType === 'chain')
    const goalNodes = nodes.filter(n => n.data?.nodeType === 'goal')
    
    const layoutedNodes: Node[] = []
    
    // Timeline nodes on left
    timelineNodes.forEach((node, index) => {
      layoutedNodes.push({
        ...node,
        position: { x: 100, y: 100 + index * 120 }
      })
    })
    
    // Chain nodes in middle
    chainNodes.forEach((node, index) => {
      layoutedNodes.push({
        ...node,
        position: { x: 500, y: 100 + index * 120 }
      })
    })
    
    // Goal nodes on right
    goalNodes.forEach((node, index) => {
      layoutedNodes.push({
        ...node,
        position: { x: 900, y: 100 + index * 120 }
      })
    })
    
    return layoutedNodes
  }, [])
  
  const applyTimelineLayout = useCallback((nodes: Node[]) => {
    if (nodes.length === 0) return nodes
    
    // Sort by timestamp
    const sortedNodes = [...nodes].sort((a, b) => {
      const timeA = new Date(a.data?.timestamp || 0).getTime()
      const timeB = new Date(b.data?.timestamp || 0).getTime()
      return timeA - timeB
    })
    
    return sortedNodes.map((node, index) => ({
      ...node,
      position: {
        x: 100 + (index % 4) * 250,
        y: 100 + Math.floor(index / 4) * 150
      }
    }))
  }, [])
  
  // Enhanced bidirectional path finding with BFS for shortest paths
  const findBidirectionalPath = useCallback((sourceId: string, targetId: string, edges: Edge[]) => {
    const adjList = new Map<string, string[]>()
    edges.forEach(edge => {
      const list = adjList.get(edge.source) || []
      list.push(edge.target)
      adjList.set(edge.source, list)
      
      // Bidirectional: also add reverse
      if (edge.data?.bidirectional || showBidirectional) {
        const reverseList = adjList.get(edge.target) || []
        reverseList.push(edge.source)
        adjList.set(edge.target, reverseList)
      }
    })
    
    // BFS for shortest path
    const queue: Array<{ node: string; path: string[] }> = [{ node: sourceId, path: [sourceId] }]
    const visited = new Set<string>([sourceId])
    
    while (queue.length > 0) {
      const { node, path } = queue.shift()!
      
      if (node === targetId) {
        return path
      }
      
      const neighbors = adjList.get(node) || []
      for (const neighbor of neighbors) {
        if (!visited.has(neighbor)) {
          visited.add(neighbor)
          queue.push({ node: neighbor, path: [...path, neighbor] })
        }
      }
    }
    
    return []
  }, [showBidirectional])
  
  // Temporal query: Find nodes within time range
  const queryTemporalRange = useCallback((startTime: Date, endTime: Date, nodes: Node[]) => {
    return nodes.filter(node => {
      const nodeTime = new Date(node.data?.timestamp || 0)
      return nodeTime >= startTime && nodeTime <= endTime
    })
  }, [])
  
  // Find past/present/future correlation
  const correlateTemporalNodes = useCallback((nodes: Node[]) => {
    const now = new Date()
    const past = nodes.filter(n => new Date(n.data?.timestamp || 0) < now)
    const present = nodes.filter(n => {
      const nodeTime = new Date(n.data?.timestamp || 0)
      const diff = Math.abs(now.getTime() - nodeTime.getTime())
      return diff < 3600000 // Within 1 hour
    })
    const future = nodes.filter(n => new Date(n.data?.timestamp || 0) > now)
    
    return { past, present, future }
  }, [])
  
  // Fetch evolution data
  useEffect(() => {
    const loadEvolutionData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Fetch timeline entries
        let timelineSummary: TimelineEntry[] = []
        try {
          timelineSummary = await getSummary(20)
        } catch (err) {
          console.warn('Failed to fetch timeline summary, using mock data', err)
          // Use mock timeline entries if API fails
          timelineSummary = [
            {
              entry_id: 'timeline_001',
              timestamp: new Date(Date.now() - 7200000).toISOString(),
              event_type: 'task_completion',
              title: 'IDE Prototype Foundation Complete',
              description: 'Completed foundation setup for IDE prototype',
              agent: 'Dac',
              confidence: 0.92,
              executed_via_chain_id: 'chain_ide_prototype',
              context_data: { goal_id: 'OBJ-01' }
            },
            {
              entry_id: 'timeline_002',
              timestamp: new Date(Date.now() - 3600000).toISOString(),
              event_type: 'panel_enhancement',
              title: 'Enhanced Context Web Panel',
              description: 'Added advanced graph visualization',
              agent: 'Dac',
              confidence: 0.88
            }
          ] as TimelineEntry[]
        }
        
        // Fetch timeline graph (includes connections)
        let timelineGraph: any = null
        try {
          timelineGraph = await getTimelineGraph()
        } catch (err) {
          console.warn('Failed to fetch timeline graph', err)
        }
      
      // Build nodes and edges
      const evolutionNodes: Node[] = []
      const evolutionEdges: Edge[] = []
      
      // Process timeline entries
      timelineSummary.forEach((entry, index) => {
        const nodeId = `timeline_${entry.entry_id}`
        
        // Determine node type based on entry
        let nodeType: 'timeline' | 'chain' | 'goal' = 'timeline'
        let label = entry.title || entry.event_type
        let color = '#3b82f6' // Blue for timeline
        
        if (entry.executed_via_chain_id) {
          nodeType = 'chain'
          label = `Chain: ${entry.executed_via_chain_id.substring(0, 12)}...`
          color = '#10b981' // Green for chains
        }
        
        if (entry.context_data?.goal_id) {
          nodeType = 'goal'
          label = `Goal: ${entry.context_data.goal_id}`
          color = '#f59e0b' // Amber for goals
        }
        
        evolutionNodes.push({
          id: nodeId,
          type: 'evolutionNode',
          position: {
            x: (index % 5) * 200,
            y: Math.floor(index / 5) * 150
          },
          data: {
            label,
            nodeType,
            entry,
            color,
            timestamp: entry.timestamp,
            agent: entry.agent || 'unknown',
            confidence: entry.confidence || 0.85,
            evidenceCount: entry.evidence_ids?.length || 0
          },
          style: {
            background: color,
            color: '#fff',
            border: '2px solid #1f2937',
            borderRadius: '8px',
            padding: '10px',
            minWidth: '150px',
            fontSize: '12px'
          }
        })
        
        // Add bidirectional edges for chain ↔ timeline connections
        if (entry.executed_via_chain_id) {
          const chainNodeId = `chain_${entry.executed_via_chain_id}`
          
          // Forward edge: Chain → Timeline
          evolutionEdges.push({
            id: `edge_chain_timeline_${entry.entry_id}`,
            source: chainNodeId,
            target: nodeId,
            type: 'smoothstep',
            animated: true,
            style: { stroke: '#10b981', strokeWidth: 2 },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: '#10b981',
              width: 20,
              height: 20
            },
            label: 'executes',
            data: { bidirectional: true }
          })
          
          // Reverse edge: Timeline → Chain (bidirectional)
          if (showBidirectional) {
            evolutionEdges.push({
              id: `edge_timeline_chain_${entry.entry_id}`,
              source: nodeId,
              target: chainNodeId,
              type: 'smoothstep',
              style: { stroke: '#10b981', strokeWidth: 1, strokeDasharray: '3,3', opacity: 0.5 },
              markerEnd: {
                type: MarkerType.ArrowClosed,
                color: '#10b981',
                width: 15,
                height: 15
              },
              label: 'part of',
              data: { bidirectional: true, reverse: true }
          })
          }
        }
        
        // Add edges for parent chains
        entry.parent_chain_ids?.forEach((parentChainId, idx) => {
          evolutionEdges.push({
            id: `edge_parent_${entry.entry_id}_${idx}`,
            source: `chain_${parentChainId}`,
            target: nodeId,
            type: 'smoothstep',
            style: { stroke: '#6b7280', strokeWidth: 1, strokeDasharray: '5,5' },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: '#6b7280'
            },
            label: 'parent'
          })
        })
        
        // Add edges for child chains
        entry.child_chain_ids?.forEach((childChainId, idx) => {
          evolutionEdges.push({
            id: `edge_child_${entry.entry_id}_${idx}`,
            source: nodeId,
            target: `chain_${childChainId}`,
            type: 'smoothstep',
            style: { stroke: '#3b82f6', strokeWidth: 1 },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: '#3b82f6'
            },
            label: 'spawned'
          })
        })
        
        // Add edges for evolution path
        if (entry.evolution_path && entry.evolution_path.length > 0) {
          entry.evolution_path.forEach((pathId, idx) => {
            if (idx > 0) {
              evolutionEdges.push({
                id: `edge_evolution_${entry.entry_id}_${idx}`,
                source: `timeline_${entry.evolution_path[idx - 1]}`,
                target: nodeId,
                type: 'smoothstep',
                style: { stroke: '#8b5cf6', strokeWidth: 1.5 },
                markerEnd: {
                  type: MarkerType.ArrowClosed,
                  color: '#8b5cf6'
                },
                label: 'evolution'
              })
            }
          })
        }
      })
      
      // Add mock chain executions
      const mockChains: ChainExecution[] = [
        {
          id: 'chain_exec_001',
          chainId: 'chain_ide_prototype',
          chainName: 'IDE Prototype Development',
          status: 'completed',
          timelineEntryIds: ['timeline_001', 'timeline_002', 'timeline_003'],
          createdAt: new Date(Date.now() - 7200000).toISOString(),
          completedAt: new Date(Date.now() - 3600000).toISOString()
        },
        {
          id: 'chain_exec_002',
          chainId: 'chain_panel_integration',
          chainName: 'Panel AIM-OS Integration',
          status: 'in_progress',
          timelineEntryIds: ['timeline_004', 'timeline_005'],
          createdAt: new Date(Date.now() - 1800000).toISOString()
        }
      ]
      
      mockChains.forEach((chain, index) => {
        const nodeId = `chain_${chain.chainId}`
        evolutionNodes.push({
          id: nodeId,
          type: 'evolutionNode',
          position: {
            x: 1000 + (index * 200),
            y: 200
          },
          data: {
            label: chain.chainName,
            nodeType: 'chain',
            chain,
            color: '#10b981',
            status: chain.status,
            createdAt: chain.createdAt
          },
          style: {
            background: '#10b981',
            color: '#fff',
            border: '2px solid #059669',
            borderRadius: '8px',
            padding: '10px',
            minWidth: '180px',
            fontSize: '12px'
          }
        })
      })
      
      // Add mock goals
      const mockGoals: GoalNode[] = [
        {
          id: 'goal_001',
          goalId: 'OBJ-07',
          name: 'MCP Tools Enhancement',
          description: 'Enhance MCP tools with real AIM-OS integrations',
          status: 'in_progress',
          progress: 0.15,
          createdSequence: 1,
          currentSequence: 5,
          targetSequence: 10,
          linkedTimelineEntries: ['timeline_001', 'timeline_002'],
          linkedChains: ['chain_ide_prototype']
        },
        {
          id: 'goal_002',
          goalId: 'OBJ-08',
          name: 'RAG MCP & Daemon Upgrades',
          description: 'Upgrade RAG MCP and daemon systems',
          status: 'in_progress',
          progress: 0.60,
          createdSequence: 2,
          currentSequence: 8,
          targetSequence: 12,
          linkedTimelineEntries: ['timeline_003'],
          linkedChains: ['chain_panel_integration']
        }
      ]
      
      mockGoals.forEach((goal, index) => {
        const nodeId = `goal_${goal.goalId}`
        evolutionNodes.push({
          id: nodeId,
          type: 'evolutionNode',
          position: {
            x: 1000 + (index * 250),
            y: 500
          },
          data: {
            label: `${goal.goalId}: ${goal.name}`,
            nodeType: 'goal',
            goal,
            color: '#f59e0b',
            status: goal.status,
            progress: goal.progress,
            createdSequence: goal.createdSequence,
            currentSequence: goal.currentSequence,
            targetSequence: goal.targetSequence
          },
          style: {
            background: '#f59e0b',
            color: '#fff',
            border: '2px solid #d97706',
            borderRadius: '8px',
            padding: '10px',
            minWidth: '200px',
            fontSize: '12px'
          }
        })
        
        // Add bidirectional edges from goals to timeline entries
        goal.linkedTimelineEntries.forEach((timelineId, idx) => {
          // Forward edge: Goal → Timeline
          evolutionEdges.push({
            id: `edge_goal_timeline_${goal.id}_${idx}`,
            source: nodeId,
            target: timelineId,
            type: 'smoothstep',
            style: { stroke: '#f59e0b', strokeWidth: 2 },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: '#f59e0b',
              width: 20,
              height: 20
            },
            label: 'progresses',
            data: { bidirectional: true }
          })
          
          // Reverse edge: Timeline → Goal (bidirectional)
          if (showBidirectional) {
            evolutionEdges.push({
              id: `edge_timeline_goal_${goal.id}_${idx}`,
              source: timelineId,
              target: nodeId,
              type: 'smoothstep',
              style: { stroke: '#f59e0b', strokeWidth: 1, strokeDasharray: '3,3', opacity: 0.5 },
              markerEnd: {
                type: MarkerType.ArrowClosed,
                color: '#f59e0b',
                width: 15,
                height: 15
              },
              label: 'contributes to',
              data: { bidirectional: true, reverse: true }
            })
          }
        })
        
        // Add bidirectional edges from goals to chains
        goal.linkedChains.forEach((chainId, idx) => {
          // Forward edge: Goal → Chain
          evolutionEdges.push({
            id: `edge_goal_chain_${goal.id}_${idx}`,
            source: nodeId,
            target: `chain_${chainId}`,
            type: 'smoothstep',
            style: { stroke: '#f59e0b', strokeWidth: 2 },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: '#f59e0b',
              width: 20,
              height: 20
            },
            label: 'orchestrates',
            data: { bidirectional: true }
          })
          
          // Reverse edge: Chain → Goal (bidirectional)
          if (showBidirectional) {
            evolutionEdges.push({
              id: `edge_chain_goal_${goal.id}_${idx}`,
              source: `chain_${chainId}`,
              target: nodeId,
              type: 'smoothstep',
              style: { stroke: '#f59e0b', strokeWidth: 1, strokeDasharray: '3,3', opacity: 0.5 },
              markerEnd: {
                type: MarkerType.ArrowClosed,
                color: '#f59e0b',
                width: 15,
                height: 15
              },
              label: 'serves',
              data: { bidirectional: true, reverse: true }
            })
          }
        })
      })
      
      // Filter nodes based on selected view
      let filteredNodes = evolutionNodes
      if (selectedView !== 'all') {
        filteredNodes = evolutionNodes.filter(node => {
          if (selectedView === 'timeline') return node.data.nodeType === 'timeline'
          if (selectedView === 'chains') return node.data.nodeType === 'chain'
          if (selectedView === 'goals') return node.data.nodeType === 'goal'
          return true
        })
      }
      
      // Apply temporal filter
      if (temporalFilter !== 'all') {
        const { past, present, future } = correlateTemporalNodes(filteredNodes)
        if (temporalFilter === 'past') filteredNodes = past
        else if (temporalFilter === 'present') filteredNodes = present
        else if (temporalFilter === 'future') filteredNodes = future
      }
      
      // Apply time range filter
      if (timeRange.start && timeRange.end) {
        filteredNodes = queryTemporalRange(timeRange.start, timeRange.end, filteredNodes)
      }
      
      // Filter edges to only include connections between visible nodes
      const visibleNodeIds = new Set(filteredNodes.map(n => n.id))
      const filteredEdges = evolutionEdges.filter(edge =>
        visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target)
      )
      
      // Apply layout algorithm
      let layoutedNodes = filteredNodes
      if (layout === 'force') {
        layoutedNodes = applyForceLayout(filteredNodes, filteredEdges)
      } else if (layout === 'hierarchical') {
        layoutedNodes = applyHierarchicalLayout(filteredNodes)
      } else if (layout === 'timeline') {
        layoutedNodes = applyTimelineLayout(filteredNodes)
      }
      
      // Highlight paths
      if (highlightPath.length > 0) {
        layoutedNodes = layoutedNodes.map(node => {
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
        
        filteredEdges.forEach(edge => {
          const sourceInPath = highlightPath.includes(edge.source)
          const targetInPath = highlightPath.includes(edge.target)
          const isInPath = sourceInPath && targetInPath
          
          if (isInPath) {
            edge.style = {
              ...edge.style,
              strokeWidth: 4,
              opacity: 1
            }
            edge.animated = true
          }
        })
      }
      
      setNodes(layoutedNodes)
      setEdges(filteredEdges)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load evolution data')
      } finally {
        setLoading(false)
      }
    }
    
    loadEvolutionData()
  }, [selectedView, getSummary, getTimelineGraph, showBidirectional, layout, highlightPath, temporalFilter, timeRange, applyForceLayout, applyHierarchicalLayout, applyTimelineLayout, findBidirectionalPath, queryTemporalRange, correlateTemporalNodes])
  
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node)
    
    // Find bidirectional paths from selected node
    if (nodes.length > 1 && showBidirectional) {
      const paths: string[] = []
      nodes.forEach(otherNode => {
        if (otherNode.id !== node.id) {
          const path = findBidirectionalPath(node.id, otherNode.id, edges)
          if (path.length > 0 && path.length <= 4) {
            paths.push(...path)
          }
        }
      })
      setHighlightPath([...new Set(paths)])
    }
  }, [nodes, edges, showBidirectional, findBidirectionalPath])
  
  const customNodeTypes: NodeTypes = {
    evolutionNode: ({ data }) => (
      <div
        className="px-3 py-2 rounded-lg shadow-lg border-2"
        style={{
          background: data.color,
          borderColor: data.color,
          color: '#fff',
          minWidth: '150px',
          maxWidth: '250px'
        }}
      >
        <div className="font-semibold text-sm mb-1">{data.label}</div>
        {data.nodeType === 'timeline' && (
          <div className="text-xs opacity-90">
            <div>Agent: {data.agent}</div>
            <div>Confidence: {(data.confidence * 100).toFixed(0)}%</div>
            <div>Evidence: {data.evidenceCount}</div>
          </div>
        )}
        {data.nodeType === 'chain' && (
          <div className="text-xs opacity-90">
            <div>Status: {data.status}</div>
            <div>Created: {new Date(data.createdAt).toLocaleTimeString()}</div>
          </div>
        )}
        {data.nodeType === 'goal' && (
          <div className="text-xs opacity-90">
            <div>Status: {data.status}</div>
            <div>Progress: {(data.progress * 100).toFixed(0)}%</div>
            <div>Sequence: {data.currentSequence}/{data.targetSequence}</div>
          </div>
        )}
      </div>
    )
  }
  
  // Calculate AIM-OS metrics
  const overallConfidence = nodes.length > 0 
    ? nodes.reduce((sum, node) => sum + (node.data.confidence || 0.85), 0) / nodes.length
    : undefined
  
  const confidenceBand = overallConfidence 
    ? (overallConfidence >= 0.90 ? 'A' : overallConfidence >= 0.70 ? 'B' : 'C')
    : undefined
  
  return (
    <BasePanel
      id="panel-evolution-explorer"
      title="Evolution Explorer"
      icon={GitBranch}
      description="Interactive visualization connecting Timeline ↔ Chain ↔ Goals with bidirectional edges"
      loading={loading}
      error={error}
      empty={!loading && !error && nodes.length === 0}
      emptyMessage="No evolution data available"
      confidence={overallConfidence}
      confidenceBand={confidenceBand}
      footerContent={
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>{nodes.length} nodes • {edges.length} edges</span>
          <span className="text-green-400">Bidirectional Graph Active</span>
        </div>
      }
      headerClassName="p-4"
    >
      {/* View Selector */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex gap-2 mb-3">
          <button
            onClick={() => setSelectedView('all')}
            className={`px-3 py-1 rounded text-sm flex items-center gap-2 ${
              selectedView === 'all' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <Network className="w-4 h-4" />
            All
          </button>
          <button
            onClick={() => setSelectedView('timeline')}
            className={`px-3 py-1 rounded text-sm flex items-center gap-2 ${
              selectedView === 'timeline' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <Clock className="w-4 h-4" />
            Timeline
          </button>
          <button
            onClick={() => setSelectedView('chains')}
            className={`px-3 py-1 rounded text-sm flex items-center gap-2 ${
              selectedView === 'chains' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <GitBranch className="w-4 h-4" />
            Chains
          </button>
          <button
            onClick={() => setSelectedView('goals')}
            className={`px-3 py-1 rounded text-sm flex items-center gap-2 ${
              selectedView === 'goals' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <Target className="w-4 h-4" />
            Goals
          </button>
        </div>
        
        {/* Search */}
        <div className="flex items-center gap-2 mb-3">
          <div className="flex-1 flex items-center gap-2 bg-gray-800 rounded px-2 py-1">
          <Search className="w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search nodes..."
            className="flex-1 bg-transparent text-gray-300 placeholder-gray-500 text-sm outline-none"
          />
          </div>
          
          {/* Layout Selector */}
          <div className="flex items-center gap-1">
            <span className="text-xs text-gray-400">Layout:</span>
            {(['force', 'hierarchical', 'timeline'] as const).map((layoutType) => (
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
          </div>
          
          {/* Bidirectional Toggle */}
          <button
            onClick={() => setShowBidirectional(!showBidirectional)}
            className={`px-2 py-0.5 rounded text-xs flex items-center gap-1 ${
              showBidirectional
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <ArrowLeftRight className="w-3 h-3" />
            Bidirectional
          </button>
          
          {/* Temporal Filter */}
          <div className="flex items-center gap-1">
            <span className="text-xs text-gray-400">Time:</span>
            {(['all', 'past', 'present', 'future'] as const).map((filter) => (
              <button
                key={filter}
                onClick={() => setTemporalFilter(filter)}
                className={`px-2 py-0.5 rounded text-xs ${
                  temporalFilter === filter
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {filter.charAt(0).toUpperCase() + filter.slice(1)}
              </button>
            ))}
          </div>
          
          {/* Fit View */}
          <button
            onClick={() => window.dispatchEvent(new Event('resize'))}
            className="px-2 py-0.5 rounded text-xs bg-gray-700 text-gray-300 hover:bg-gray-600 flex items-center gap-1"
          >
            <Maximize2 className="w-3 h-3" />
            Fit
          </button>
        </div>
      </div>
      
      {/* Graph Visualization */}
      <div className="flex-1 relative" ref={reactFlowWrapperRef}>
        <ReactFlowProvider>
        <ReactFlow
          nodes={nodes}
          edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
            onPaneClick={() => {
              setSelectedNode(null)
              setHighlightPath([])
            }}
          nodeTypes={customNodeTypes}
          fitView
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
        >
          <Background color="#374151" gap={16} />
          <Controls />
          <MiniMap
            nodeColor={(node) => {
              if (node.data?.nodeType === 'timeline') return '#3b82f6'
              if (node.data?.nodeType === 'chain') return '#10b981'
              if (node.data?.nodeType === 'goal') return '#f59e0b'
              return '#6b7280'
            }}
            maskColor="rgba(0, 0, 0, 0.6)"
          />
        </ReactFlow>
        </ReactFlowProvider>
      </div>
      
      {/* Selected Node Details */}
      {selectedNode && (
        <div className="p-4 border-t border-gray-700 bg-gray-800/50 max-h-48 overflow-auto">
          <div className="text-sm font-semibold text-gray-200 mb-2">
            {selectedNode.data.label}
          </div>
          <div className="text-xs text-gray-400 space-y-1">
            {selectedNode.data.nodeType === 'timeline' && (
              <>
                <div>Type: Timeline Entry</div>
                <div>Event: {selectedNode.data.entry.event_type}</div>
                <div>Agent: {selectedNode.data.agent}</div>
                <div>Confidence: {(selectedNode.data.confidence * 100).toFixed(0)}%</div>
                {selectedNode.data.entry.executed_via_chain_id && (
                  <div>Chain: {selectedNode.data.entry.executed_via_chain_id}</div>
                )}
                {selectedNode.data.entry.parent_chain_ids?.length > 0 && (
                  <div>Parent Chains: {selectedNode.data.entry.parent_chain_ids.length}</div>
                )}
                {selectedNode.data.entry.child_chain_ids?.length > 0 && (
                  <div>Child Chains: {selectedNode.data.entry.child_chain_ids.length}</div>
                )}
              </>
            )}
            {selectedNode.data.nodeType === 'chain' && (
              <>
                <div>Type: Chain Execution</div>
                <div>Status: {selectedNode.data.status}</div>
                <div>Timeline Entries: {selectedNode.data.chain.timelineEntryIds.length}</div>
              </>
            )}
            {selectedNode.data.nodeType === 'goal' && (
              <>
                <div>Type: Goal</div>
                <div>Status: {selectedNode.data.status}</div>
                <div>Progress: {(selectedNode.data.progress * 100).toFixed(0)}%</div>
                <div>Sequence: {selectedNode.data.currentSequence} → {selectedNode.data.targetSequence}</div>
              </>
            )}
          </div>
        </div>
      )}
      
      {/* Legend */}
      <div className="p-2 border-t border-gray-700 flex items-center gap-4 text-xs text-gray-400">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-500 rounded"></div>
          <span>Timeline Entry</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded"></div>
          <span>Chain Execution</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-amber-500 rounded"></div>
          <span>Goal</span>
        </div>
      </div>
    </BasePanel>
  )
}
