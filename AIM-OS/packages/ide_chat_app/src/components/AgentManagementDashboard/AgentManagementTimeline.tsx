/**
 * Agent Management Timeline Component
 * 
 * Beautiful animated Lucide diagram showing agent work, dependencies, waiting states,
 * and integration with bitemporal timeline.
 * 
 * Features:
 * - Real-time agent work visualization ⭐
 * - Dependency graph with waiting states ⭐
 * - Issue tracking and resolution ⭐
 * - Bitemporal timeline integration ⭐
 * - Animated Lucide diagram with color-coded nodes ⭐
 * - Interactive timeline navigation ⭐
 * 
 * Created: 2025-11-07 (Rev - Competition Phase)
 */

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import {
  Network,
  Clock,
  Play,
  Pause,
  SkipBack,
  SkipForward,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Minimize2,
  RefreshCw,
  Filter,
  Search,
  Bot,
  CheckCircle,
  XCircle,
  AlertCircle,
  Loader,
  ArrowRight,
  ArrowDown,
  ArrowUp,
  GitBranch,
  Target,
  Code,
  FileText,
  Brain,
  Zap,
  Shield,
  Users,
  Link,
  Calendar,
  TrendingUp,
  Activity,
  Circle,
  Square,
  Triangle,
  Hexagon,
  Octagon,
  Star,
  Sparkles,
} from 'lucide-react'

interface AgentWorkEvent {
  id: string
  agentId: string
  agentName: string
  type: 'task' | 'issue' | 'waiting' | 'completed' | 'error' | 'dependency'
  title: string
  description: string
  timestamp: string
  duration?: number // milliseconds
  status: 'active' | 'waiting' | 'completed' | 'failed' | 'blocked'
  dependencies?: string[] // IDs of events this depends on
  waitingFor?: string[] // Agent IDs this is waiting for
  relatedIssues?: string[] // Issue IDs related to this work
  timelineNodeId?: string // Bitemporal timeline node ID
  confidence?: number // VIF confidence
}

interface AgentNode {
  id: string
  name: string
  color: string
  icon: React.ReactNode
  position: { x: number; y: number }
  events: AgentWorkEvent[]
  status: 'active' | 'idle' | 'waiting' | 'error' | 'offline'
  currentWork?: AgentWorkEvent
}

interface DependencyEdge {
  id: string
  source: string // Agent ID or Event ID
  target: string // Agent ID or Event ID
  type: 'dependency' | 'waiting' | 'blocking' | 'related'
  strength: number // 0-1
  animated?: boolean
}

// Mock data for prototype
const generateMockAgentTimeline = (): { nodes: AgentNode[]; edges: DependencyEdge[]; events: AgentWorkEvent[] } => {
  const events: AgentWorkEvent[] = [
    {
      id: 'event-001',
      agentId: 'rev',
      agentName: 'Rev',
      type: 'task',
      title: 'Enhance Problems Panel',
      description: 'Add real-time error tracking and lifecycle management',
      timestamp: '2025-11-07T10:00:00Z',
      duration: 3600000, // 1 hour
      status: 'completed',
      timelineNodeId: 'timeline-node-001',
      confidence: 0.95,
    },
    {
      id: 'event-002',
      agentId: 'rev',
      agentName: 'Rev',
      type: 'task',
      title: 'Create Agent Management Timeline',
      description: 'Build beautiful Lucide diagram visualization',
      timestamp: '2025-11-07T11:00:00Z',
      duration: 1800000, // 30 minutes
      status: 'active',
      dependencies: ['event-001'],
      timelineNodeId: 'timeline-node-002',
      confidence: 0.92,
    },
    {
      id: 'event-003',
      agentId: 'aether',
      agentName: 'Aether',
      type: 'task',
      title: 'Complete IDE Layout Prototype',
      description: 'Finish Phase 2 implementation',
      timestamp: '2025-11-07T09:00:00Z',
      duration: 7200000, // 2 hours
      status: 'completed',
      timelineNodeId: 'timeline-node-003',
      confidence: 0.98,
    },
    {
      id: 'event-004',
      agentId: 'lexicon',
      agentName: 'Lexicon',
      type: 'waiting',
      title: 'Waiting for Rev',
      description: 'Need Problems Panel enhancements before proceeding',
      timestamp: '2025-11-07T10:30:00Z',
      status: 'waiting',
      waitingFor: ['rev'],
      dependencies: ['event-001'],
      timelineNodeId: 'timeline-node-004',
    },
    {
      id: 'event-005',
      agentId: 'sam',
      agentName: 'Sam',
      type: 'issue',
      title: 'TypeScript Compilation Error',
      description: "Cannot find name 'ContextWebPanel'",
      timestamp: '2025-11-07T11:15:00Z',
      status: 'active',
      relatedIssues: ['event-006'],
      timelineNodeId: 'timeline-node-005',
    },
    {
      id: 'event-006',
      agentId: 'rev',
      agentName: 'Rev',
      type: 'task',
      title: 'Fix ContextWebPanel Import',
      description: 'Add missing import statement',
      timestamp: '2025-11-07T11:20:00Z',
      duration: 300000, // 5 minutes
      status: 'completed',
      dependencies: ['event-005'],
      timelineNodeId: 'timeline-node-006',
      confidence: 0.99,
    },
    {
      id: 'event-007',
      agentId: 'max',
      agentName: 'Max',
      type: 'task',
      title: 'UI Research Stream 3',
      description: 'Panel functionality design research',
      timestamp: '2025-11-07T08:00:00Z',
      duration: 5400000, // 1.5 hours
      status: 'completed',
      timelineNodeId: 'timeline-node-007',
      confidence: 0.90,
    },
    {
      id: 'event-008',
      agentId: 'codex',
      agentName: 'Codex',
      type: 'dependency',
      title: 'ChainSpec Authoring',
      description: 'Waiting for UI research completion',
      timestamp: '2025-11-07T09:30:00Z',
      status: 'waiting',
      waitingFor: ['max', 'sam', 'lexicon'],
      dependencies: ['event-007'],
      timelineNodeId: 'timeline-node-008',
    },
  ]

  const nodes: AgentNode[] = [
    {
      id: 'rev',
      name: 'Rev',
      color: 'bg-purple-500',
      icon: <Bot className="w-5 h-5" />,
      position: { x: 200, y: 150 },
      events: events.filter(e => e.agentId === 'rev'),
      status: 'active',
      currentWork: events.find(e => e.agentId === 'rev' && e.status === 'active'),
    },
    {
      id: 'aether',
      name: 'Aether',
      color: 'bg-blue-500',
      icon: <Brain className="w-5 h-5" />,
      position: { x: 400, y: 150 },
      events: events.filter(e => e.agentId === 'aether'),
      status: 'active',
      currentWork: events.find(e => e.agentId === 'aether' && e.status === 'active'),
    },
    {
      id: 'lexicon',
      name: 'Lexicon',
      color: 'bg-green-500',
      icon: <Code className="w-5 h-5" />,
      position: { x: 600, y: 150 },
      events: events.filter(e => e.agentId === 'lexicon'),
      status: 'waiting',
      currentWork: events.find(e => e.agentId === 'lexicon' && e.status === 'waiting'),
    },
    {
      id: 'sam',
      name: 'Sam',
      color: 'bg-yellow-500',
      icon: <FileText className="w-5 h-5" />,
      position: { x: 200, y: 300 },
      events: events.filter(e => e.agentId === 'sam'),
      status: 'active',
      currentWork: events.find(e => e.agentId === 'sam' && e.status === 'active'),
    },
    {
      id: 'max',
      name: 'Max',
      color: 'bg-orange-500',
      icon: <Target className="w-5 h-5" />,
      position: { x: 400, y: 300 },
      events: events.filter(e => e.agentId === 'max'),
      status: 'idle',
      currentWork: events.find(e => e.agentId === 'max' && e.status === 'active'),
    },
    {
      id: 'codex',
      name: 'Codex',
      color: 'bg-cyan-500',
      icon: <GitBranch className="w-5 h-5" />,
      position: { x: 600, y: 300 },
      events: events.filter(e => e.agentId === 'codex'),
      status: 'waiting',
      currentWork: events.find(e => e.agentId === 'codex' && e.status === 'waiting'),
    },
  ]

  const edges: DependencyEdge[] = [
    {
      id: 'edge-001',
      source: 'event-001',
      target: 'event-002',
      type: 'dependency',
      strength: 1.0,
      animated: false,
    },
    {
      id: 'edge-002',
      source: 'event-001',
      target: 'event-004',
      type: 'waiting',
      strength: 0.9,
      animated: true,
    },
    {
      id: 'edge-003',
      source: 'rev',
      target: 'lexicon',
      type: 'waiting',
      strength: 0.8,
      animated: true,
    },
    {
      id: 'edge-004',
      source: 'event-005',
      target: 'event-006',
      type: 'dependency',
      strength: 1.0,
      animated: false,
    },
    {
      id: 'edge-005',
      source: 'event-007',
      target: 'event-008',
      type: 'dependency',
      strength: 0.9,
      animated: false,
    },
    {
      id: 'edge-006',
      source: 'max',
      target: 'codex',
      type: 'dependency',
      strength: 0.8,
      animated: true,
    },
    {
      id: 'edge-007',
      source: 'sam',
      target: 'codex',
      type: 'dependency',
      strength: 0.7,
      animated: true,
    },
    {
      id: 'edge-008',
      source: 'lexicon',
      target: 'codex',
      type: 'dependency',
      strength: 0.6,
      animated: true,
    },
  ]

  return { nodes, edges, events }
}

export const AgentManagementTimeline: React.FC = () => {
  const [nodes, setNodes] = useState<AgentNode[]>([])
  const [edges, setEdges] = useState<DependencyEdge[]>([])
  const [events, setEvents] = useState<AgentWorkEvent[]>([])
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [zoom, setZoom] = useState(1.0)
  const [selectedNode, setSelectedNode] = useState<AgentNode | null>(null)
  const [selectedEvent, setSelectedEvent] = useState<AgentWorkEvent | null>(null)
  const [filterStatus, setFilterStatus] = useState<'all' | AgentNode['status']>('all')
  const [filterType, setFilterType] = useState<'all' | AgentWorkEvent['type']>('all')
  const [showWaiting, setShowWaiting] = useState(true)
  const [showDependencies, setShowDependencies] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const canvasRef = useRef<HTMLDivElement>(null)
  const animationRef = useRef<number>()

  // Load timeline data
  const loadTimelineData = useCallback(async () => {
    setIsLoading(true)
    try {
      // TODO: Integrate with AIM-OS TCS and bitemporal timeline APIs
      // const timelineData = await aimosService.getTimelineEntries({ limit: 100 })
      // const agentWork = await aimosService.getAgentWorkEvents()
      // const dependencies = await aimosService.getAgentDependencies()
      
      // For now, use mock data
      const mockData = generateMockAgentTimeline()
      setNodes(mockData.nodes)
      setEdges(mockData.edges)
      setEvents(mockData.events)
      setIsConnected(false) // Mock mode
    } catch (error) {
      console.error('Failed to load timeline data:', error)
      setIsConnected(false)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    loadTimelineData()
  }, [loadTimelineData])

  // Animation loop
  useEffect(() => {
    if (isPlaying) {
      animationRef.current = requestAnimationFrame(() => {
        setCurrentTime(prev => prev + 16) // ~60fps
      })
    }
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [isPlaying])

  const getNodeIcon = (node: AgentNode) => {
    switch (node.status) {
      case 'active':
        return <Activity className="w-5 h-5 text-white animate-pulse" />
      case 'waiting':
        return <Loader className="w-5 h-5 text-white animate-spin" />
      case 'error':
        return <XCircle className="w-5 h-5 text-white" />
      case 'idle':
        return <Circle className="w-5 h-5 text-white" />
      default:
        return node.icon
    }
  }

  const getNodeColor = (node: AgentNode) => {
    switch (node.status) {
      case 'active':
        return 'bg-green-500'
      case 'waiting':
        return 'bg-yellow-500'
      case 'error':
        return 'bg-red-500'
      case 'idle':
        return 'bg-gray-500'
      default:
        return node.color
    }
  }

  const getEventIcon = (event: AgentWorkEvent) => {
    switch (event.type) {
      case 'task':
        return <Target className="w-4 h-4" />
      case 'issue':
        return <AlertCircle className="w-4 h-4" />
      case 'waiting':
        return <Loader className="w-4 h-4 animate-spin" />
      case 'completed':
        return <CheckCircle className="w-4 h-4" />
      case 'error':
        return <XCircle className="w-4 h-4" />
      case 'dependency':
        return <Link className="w-4 h-4" />
      default:
        return <Circle className="w-4 h-4" />
    }
  }

  const getEventColor = (event: AgentWorkEvent) => {
    switch (event.status) {
      case 'completed':
        return 'bg-green-500'
      case 'active':
        return 'bg-blue-500'
      case 'waiting':
        return 'bg-yellow-500'
      case 'failed':
        return 'bg-red-500'
      case 'blocked':
        return 'bg-orange-500'
      default:
        return 'bg-gray-500'
    }
  }

  const filteredNodes = useMemo(() => {
    return nodes.filter(node => {
      const matchesStatus = filterStatus === 'all' || node.status === filterStatus
      const matchesType = filterType === 'all' || 
        (node.currentWork && node.currentWork.type === filterType) ||
        node.events.some(e => e.type === filterType)
      return matchesStatus && matchesType
    })
  }, [nodes, filterStatus, filterType])

  const filteredEdges = useMemo(() => {
    const filteredNodeIds = new Set(filteredNodes.map(n => n.id))
    return edges.filter(edge => {
      const showEdge = (filteredNodeIds.has(edge.source) || filteredNodeIds.has(edge.target)) &&
                       ((showWaiting && edge.type === 'waiting') ||
                        (showDependencies && (edge.type === 'dependency' || edge.type === 'blocking' || edge.type === 'related')) ||
                        edge.type === 'related')
      return showEdge
    })
  }, [edges, filteredNodes, showWaiting, showDependencies])

  const handleNodeClick = useCallback((node: AgentNode) => {
    setSelectedNode(node)
    setSelectedEvent(node.currentWork || null)
  }, [])

  const handleEventClick = useCallback((event: AgentWorkEvent) => {
    setSelectedEvent(event)
    const node = nodes.find(n => n.id === event.agentId)
    if (node) setSelectedNode(node)
  }, [nodes])

  const handlePlayPause = useCallback(() => {
    setIsPlaying(prev => !prev)
  }, [])

  const handleReset = useCallback(() => {
    setCurrentTime(0)
    setIsPlaying(false)
  }, [])

  const handleZoomIn = useCallback(() => {
    setZoom(prev => Math.min(prev + 0.1, 2.0))
  }, [])

  const handleZoomOut = useCallback(() => {
    setZoom(prev => Math.max(prev - 0.1, 0.5))
  }, [])

  // Render Lucide diagram
  const renderDiagram = useCallback(() => {
    if (filteredNodes.length === 0) {
      return (
        <div className="flex items-center justify-center h-full text-gray-400">
          <div className="text-center">
            <Network className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No agents found</p>
            <p className="text-xs mt-1">Try adjusting filters</p>
          </div>
        </div>
      )
    }

    // Simple grid layout for prototype (in production, use D3 force simulation or React Flow)
    const cols = Math.ceil(Math.sqrt(filteredNodes.length))
    const nodeSize = 80
    const spacing = 200

    return (
      <div className="relative w-full h-full overflow-auto" ref={canvasRef}>
        <svg
          width="100%"
          height="100%"
          className="absolute inset-0"
          style={{ transform: `scale(${zoom})`, transformOrigin: 'top left' }}
        >
          {/* Render edges */}
          {filteredEdges.map((edge, idx) => {
            const sourceNode = filteredNodes.find(n => n.id === edge.source)
            const targetNode = filteredNodes.find(n => n.id === edge.target)
            if (!sourceNode || !targetNode) return null

            const sourceIdx = filteredNodes.indexOf(sourceNode)
            const targetIdx = filteredNodes.indexOf(targetNode)
            const sourceX = (sourceIdx % cols) * spacing + nodeSize / 2
            const sourceY = Math.floor(sourceIdx / cols) * spacing + nodeSize / 2
            const targetX = (targetIdx % cols) * spacing + nodeSize / 2
            const targetY = Math.floor(targetIdx / cols) * spacing + nodeSize / 2

            const edgeColor = edge.type === 'waiting' ? 'stroke-yellow-400' :
                             edge.type === 'dependency' ? 'stroke-blue-400' :
                             edge.type === 'blocking' ? 'stroke-red-400' :
                             'stroke-gray-400'

            return (
              <g key={edge.id}>
                <line
                  x1={sourceX}
                  y1={sourceY}
                  x2={targetX}
                  y2={targetY}
                  strokeWidth={edge.strength * 3}
                  className={edgeColor}
                  opacity={0.6}
                  markerEnd="url(#arrowhead)"
                  strokeDasharray={edge.animated ? '5,5' : '0'}
                  style={edge.animated ? { animation: 'dash 1s linear infinite' } : {}}
                />
                {edge.animated && (
                  <circle
                    cx={(sourceX + targetX) / 2}
                    cy={(sourceY + targetY) / 2}
                    r="4"
                    className="fill-yellow-400"
                    style={{ animation: 'pulse 1s ease-in-out infinite' }}
                  />
                )}
              </g>
            )
          })}

          {/* Arrow marker definition */}
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon points="0 0, 10 3, 0 6" fill="currentColor" className="text-gray-400" />
            </marker>
          </defs>

          {/* Render nodes */}
          {filteredNodes.map((node, idx) => {
            const x = (idx % cols) * spacing + nodeSize / 2
            const y = Math.floor(idx / cols) * spacing + nodeSize / 2
            const isSelected = selectedNode?.id === node.id

            return (
              <g key={node.id}>
                {/* Node circle */}
                <circle
                  cx={x}
                  cy={y}
                  r={nodeSize / 2}
                  className={`cursor-pointer transition-all ${getNodeColor(node)} ${
                    isSelected ? 'ring-4 ring-blue-400' : ''
                  }`}
                  onClick={() => handleNodeClick(node)}
                  style={{
                    filter: isSelected ? 'drop-shadow(0 0 8px rgba(59, 130, 246, 0.5))' : undefined,
                  }}
                />
                {/* Node icon */}
                <g transform={`translate(${x - 10}, ${y - 10})`}>
                  {getNodeIcon(node)}
                </g>
                {/* Node label */}
                <text
                  x={x}
                  y={y + nodeSize / 2 + 15}
                  textAnchor="middle"
                  className="text-xs font-semibold fill-white pointer-events-none"
                >
                  {node.name}
                </text>
                {/* Active work indicator */}
                {node.currentWork && (
                  <circle
                    cx={x + nodeSize / 2 - 5}
                    cy={y - nodeSize / 2 + 5}
                    r="4"
                    className="fill-blue-400"
                    style={{ animation: 'pulse 1s ease-in-out infinite' }}
                  />
                )}
              </g>
            )
          })}
        </svg>

        {/* Add CSS animations */}
        <style>{`
          @keyframes dash {
            to {
              stroke-dashoffset: -10;
            }
          }
          @keyframes pulse {
            0%, 100% {
              opacity: 1;
            }
            50% {
              opacity: 0.5;
            }
          }
        `}</style>
      </div>
    )
  }, [filteredNodes, filteredEdges, selectedNode, zoom, handleNodeClick])

  return (
    <div className="h-full flex flex-col bg-gray-900 text-gray-200">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 flex items-center gap-2 shrink-0">
        <Network className="w-5 h-5 text-blue-400" />
        <div>
          <div className="text-white text-sm font-semibold">Agent Management Timeline ⭐</div>
          <div className="text-xs text-gray-500">Bitemporal Timeline Integration</div>
        </div>
        <span
          className={`ml-auto px-2 py-1 rounded-full text-xs font-medium ${
            isConnected ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
          }`}
        >
          {isConnected ? 'Connected' : 'Mock Mode'}
        </span>
        <button onClick={loadTimelineData} className="text-gray-400 hover:text-white p-1 rounded">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Controls */}
      <div className="px-3 py-2 border-b border-gray-700 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <button
            onClick={handlePlayPause}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
            title={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </button>
          <button
            onClick={handleReset}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
            title="Reset"
          >
            <SkipBack className="w-4 h-4" />
          </button>
          <div className="w-32 h-1 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 transition-all"
              style={{ width: `${(currentTime / 86400000) * 100}%` }}
            />
          </div>
          <span className="text-xs text-gray-400 min-w-[80px]">
            {new Date(currentTime).toLocaleTimeString()}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleZoomOut}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-xs text-gray-400 min-w-[60px] text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={handleZoomIn}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="px-3 py-2 border-b border-gray-700 shrink-0 space-y-2">
        <div className="flex gap-2 overflow-x-auto pb-1">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as any)}
            className="px-3 py-1 text-xs rounded bg-gray-700 text-gray-300 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="waiting">Waiting</option>
            <option value="idle">Idle</option>
            <option value="error">Error</option>
          </select>

          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value as any)}
            className="px-3 py-1 text-xs rounded bg-gray-700 text-gray-300 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Types</option>
            <option value="task">Task</option>
            <option value="issue">Issue</option>
            <option value="waiting">Waiting</option>
            <option value="completed">Completed</option>
            <option value="error">Error</option>
            <option value="dependency">Dependency</option>
          </select>

          <button
            onClick={() => setShowWaiting(!showWaiting)}
            className={`px-3 py-1 text-xs rounded whitespace-nowrap flex items-center gap-1 ${
              showWaiting
                ? 'bg-yellow-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <Loader className="w-3 h-3" />
            Waiting
          </button>

          <button
            onClick={() => setShowDependencies(!showDependencies)}
            className={`px-3 py-1 text-xs rounded whitespace-nowrap flex items-center gap-1 ${
              showDependencies
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <Link className="w-3 h-3" />
            Dependencies
          </button>
        </div>
      </div>

      {/* Diagram Canvas */}
      <div className="flex-1 overflow-hidden relative">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <RefreshCw className="w-8 h-8 mx-auto mb-2 text-gray-400 animate-spin" />
              <p className="text-gray-400 text-sm">Loading timeline...</p>
            </div>
          </div>
        ) : (
          renderDiagram()
        )}
      </div>

      {/* Node/Event Detail Sidebar */}
      {(selectedNode || selectedEvent) && (
        <div className="absolute right-0 top-0 h-full w-1/3 bg-gray-800 border-l border-gray-700 shadow-lg flex flex-col z-10">
          <div className="flex items-center justify-between p-4 border-b border-gray-700">
            <h4 className="text-white text-md font-semibold">
              {selectedEvent ? 'Event Details' : 'Agent Details'}
            </h4>
            <button
              onClick={() => {
                setSelectedNode(null)
                setSelectedEvent(null)
              }}
              className="text-gray-400 hover:text-white"
            >
              <Minimize2 className="w-5 h-5" />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 text-sm text-gray-200 space-y-4">
            {selectedEvent && (
              <>
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    {getEventIcon(selectedEvent)}
                    <span className="font-semibold text-white">{selectedEvent.title}</span>
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      selectedEvent.status === 'completed' ? 'bg-green-600/20 text-green-400' :
                      selectedEvent.status === 'active' ? 'bg-blue-600/20 text-blue-400' :
                      selectedEvent.status === 'waiting' ? 'bg-yellow-600/20 text-yellow-400' :
                      selectedEvent.status === 'failed' ? 'bg-red-600/20 text-red-400' :
                      'bg-gray-600/20 text-gray-400'
                    }`}>
                      {selectedEvent.status}
                    </span>
                  </div>
                  <p className="text-gray-300">{selectedEvent.description}</p>
                </div>

                <div>
                  <p className="text-gray-400 mb-1">Agent:</p>
                  <span>{selectedEvent.agentName}</span>
                </div>

                <div>
                  <p className="text-gray-400 mb-1">Timestamp:</p>
                  <span>{new Date(selectedEvent.timestamp).toLocaleString()}</span>
                </div>

                {selectedEvent.duration && (
                  <div>
                    <p className="text-gray-400 mb-1">Duration:</p>
                    <span>{(selectedEvent.duration / 1000 / 60).toFixed(1)} minutes</span>
                  </div>
                )}

                {selectedEvent.waitingFor && selectedEvent.waitingFor.length > 0 && (
                  <div>
                    <p className="text-gray-400 mb-2">Waiting For:</p>
                    <div className="space-y-1">
                      {selectedEvent.waitingFor.map((agentId) => {
                        const agent = nodes.find(n => n.id === agentId)
                        return agent ? (
                          <button
                            key={agentId}
                            onClick={() => handleNodeClick(agent)}
                            className="w-full text-left px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs flex items-center gap-2"
                          >
                            <Loader className="w-3 h-3 text-yellow-400 animate-spin" />
                            <span>{agent.name}</span>
                          </button>
                        ) : null
                      })}
                    </div>
                  </div>
                )}

                {selectedEvent.dependencies && selectedEvent.dependencies.length > 0 && (
                  <div>
                    <p className="text-gray-400 mb-2">Dependencies:</p>
                    <div className="space-y-1">
                      {selectedEvent.dependencies.map((eventId) => {
                        const depEvent = events.find(e => e.id === eventId)
                        return depEvent ? (
                          <button
                            key={eventId}
                            onClick={() => handleEventClick(depEvent)}
                            className="w-full text-left px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs flex items-center gap-2"
                          >
                            <Link className="w-3 h-3 text-blue-400" />
                            <span>{depEvent.title}</span>
                          </button>
                        ) : null
                      })}
                    </div>
                  </div>
                )}

                {selectedEvent.timelineNodeId && (
                  <div>
                    <p className="text-gray-400 mb-1">Timeline Node:</p>
                    <span className="font-mono text-xs">{selectedEvent.timelineNodeId}</span>
                  </div>
                )}

                {selectedEvent.confidence !== undefined && (
                  <div>
                    <p className="text-gray-400 mb-1">VIF Confidence:</p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${selectedEvent.confidence * 100}%` }}
                        />
                      </div>
                      <span>{(selectedEvent.confidence * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                )}
              </>
            )}

            {selectedNode && !selectedEvent && (
              <>
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    {getNodeIcon(selectedNode)}
                    <span className="font-semibold text-white">{selectedNode.name}</span>
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      selectedNode.status === 'active' ? 'bg-green-600/20 text-green-400' :
                      selectedNode.status === 'waiting' ? 'bg-yellow-600/20 text-yellow-400' :
                      selectedNode.status === 'error' ? 'bg-red-600/20 text-red-400' :
                      'bg-gray-600/20 text-gray-400'
                    }`}>
                      {selectedNode.status}
                    </span>
                  </div>
                </div>

                {selectedNode.currentWork && (
                  <div>
                    <p className="text-gray-400 mb-2">Current Work:</p>
                    <button
                      onClick={() => handleEventClick(selectedNode.currentWork!)}
                      className="w-full text-left px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs"
                    >
                      {selectedNode.currentWork.title}
                    </button>
                  </div>
                )}

                <div>
                  <p className="text-gray-400 mb-2">Events ({selectedNode.events.length}):</p>
                  <div className="space-y-1 max-h-64 overflow-y-auto">
                    {selectedNode.events.map((event) => (
                      <button
                        key={event.id}
                        onClick={() => handleEventClick(event)}
                        className="w-full text-left px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs flex items-center gap-2"
                      >
                        {getEventIcon(event)}
                        <span className="flex-1">{event.title}</span>
                        <span className={`px-1 py-0.5 rounded text-xs ${
                          event.status === 'completed' ? 'bg-green-600/20 text-green-400' :
                          event.status === 'active' ? 'bg-blue-600/20 text-blue-400' :
                          'bg-gray-600/20 text-gray-400'
                        }`}>
                          {event.status}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

