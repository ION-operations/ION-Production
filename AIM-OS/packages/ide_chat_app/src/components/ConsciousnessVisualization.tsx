import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import {
  Brain,
  Activity,
  Zap,
  Target,
  Eye,
  EyeOff,
  Maximize2,
  Minimize2,
  RotateCcw,
  Play,
  Pause,
  Square,
  Settings,
  Filter,
  Search,
  RefreshCw,
  Download,
  Upload,
  Save,
  FilePen as Open,
  X as Close,
  Plus,
  Minus,
  X,
  Check,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ChevronUp,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  MoreHorizontal,
  MoreVertical,
  Menu,
  Home,
  User,
  Users,
  UserPlus,
  UserMinus,
  UserCheck,
  UserX,
  LogIn,
  LogOut,
  Key,
  KeyRound,
  LockKeyhole,
  UnlockKeyhole,
  Fingerprint,
  Scan,
  QrCode,
  Barcode,
  CreditCard,
  Wallet,
  Coins,
  DollarSign,
  Euro,
  PoundSterling,
  DollarSign as Yen,
  Bitcoin,
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  LineChart,
  Clock,
  FileText,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Info,
  Sparkles,
  Network,
  Layers,
  Cpu,
  HardDrive as Memory,
  HardDrive,
  Wifi,
  Shield,
  Lock,
  Unlock,
  Globe,
  Database,
  Server,
  Cloud,
  Smartphone,
  Monitor,
  Laptop,
  Tablet,
  Watch,
  Headphones,
  Camera,
  Mic,
  Speaker,
  WifiOff,
  Signal,
  Battery,
  BatteryLow,
  BatteryMedium,
  Battery as BatteryHigh,
  BatteryFull,
  Power,
  PowerOff,
  Zap as Lightning,
  Sun,
  Moon,
  Star,
  Heart,
  ThumbsUp,
  ThumbsDown,
  MessageCircle,
  Mail,
  Phone,
  Video,
  Image,
  File,
  Folder,
  FolderOpen,
  Archive,
  Trash2,
  Edit,
  Copy,
  Scissors as Cut,
  Clipboard as Paste,
  Save as SaveIcon,
  Save as SaveAsIcon,
  FilePen as OpenIcon,
  X as CloseIcon,
  Plus as PlusIcon,
  Minus as MinusIcon,
  X as XIcon,
  Check as CheckIcon,
  ArrowUp as ArrowUpIcon,
  ArrowDown as ArrowDownIcon,
  ArrowLeft as ArrowLeftIcon,
  ArrowRight as ArrowRightIcon,
  ChevronUp as ChevronUpIcon,
  ChevronDown as ChevronDownIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  MoreHorizontal as MoreHorizontalIcon,
  MoreVertical as MoreVerticalIcon,
  Menu as MenuIcon,
  Home as HomeIcon,
  User as UserIcon,
  Users as UsersIcon,
  UserPlus as UserPlusIcon,
  UserMinus as UserMinusIcon,
  UserCheck as UserCheckIcon,
  UserX as UserXIcon,
  LogIn as LogInIcon,
  LogOut as LogOutIcon,
  Key as KeyIcon,
  KeyRound as KeyRoundIcon,
  LockKeyhole as LockKeyholeIcon,
  UnlockKeyhole as UnlockKeyholeIcon,
  Fingerprint as FingerprintIcon,
  Scan as ScanIcon,
  QrCode as QrCodeIcon,
  Barcode as BarcodeIcon,
  CreditCard as CreditCardIcon,
  Wallet as WalletIcon,
  Coins as CoinsIcon,
  DollarSign as DollarSignIcon,
  Euro as EuroIcon,
  PoundSterling as PoundSterlingIcon,
  DollarSign as YenIcon,
  Bitcoin as BitcoinIcon,
} from 'lucide-react'
import { useAIMOS } from '../hooks/useAIMOS'
import { LoadingState } from './LoadingState'
import { ErrorBoundary } from './ErrorBoundary'

interface ConsciousnessNode {
  id: string
  type: 'thought' | 'emotion' | 'memory' | 'pattern' | 'insight' | 'decision'
  content: string
  intensity: number
  confidence: number
  position: { x: number; y: number; z: number }
  connections: string[]
  metadata: {
    timestamp: string
    source: string
    context: string
    tags: string[]
    influence: number
    stability: number
  }
}

interface ConsciousnessVisualizationProps {
  className?: string
  nodes?: ConsciousnessNode[]
  onNodeSelect?: (nodeId: string) => void
  onNodeUpdate?: (node: ConsciousnessNode) => void
  onNodeDelete?: (nodeId: string) => void
  enableRealTimeUpdates?: boolean
  enable3D?: boolean
  enablePhysics?: boolean
  theme?: 'dark' | 'light' | 'auto'
  layout?: 'force' | 'circular' | 'hierarchical' | 'random'
  filters?: {
    type?: string[]
    intensity?: { min: number; max: number }
    confidence?: { min: number; max: number }
    timeRange?: { start: Date; end: Date }
    searchQuery?: string
  }
}

export default function ConsciousnessVisualization({
  className = '',
  nodes = [],
  onNodeSelect,
  onNodeUpdate,
  onNodeDelete,
  enableRealTimeUpdates = true,
  enable3D = false,
  enablePhysics = true,
  theme = 'dark',
  layout = 'force',
  filters = {},
}: ConsciousnessVisualizationProps) {
  const [consciousnessNodes, setConsciousnessNodes] = useState<ConsciousnessNode[]>(nodes)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [hoveredNode, setHoveredNode] = useState<string | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [maxTime, setMaxTime] = useState(100)
  const [viewMode, setViewMode] = useState<'2d' | '3d'>('2d')
  const [cameraPosition, setCameraPosition] = useState({ x: 0, y: 0, z: 0 })
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [showControls, setShowControls] = useState(true)
  const [showLegend, setShowLegend] = useState(true)
  const [showTimeline, setShowTimeline] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'reconnecting'>('connected')
  const [animationSpeed, setAnimationSpeed] = useState(1)
  const [particleCount, setParticleCount] = useState(100)
  const [linkDistance, setLinkDistance] = useState(100)
  const [linkStrength, setLinkStrength] = useState(0.1)
  const [chargeStrength, setChargeStrength] = useState(-300)
  const [gravity, setGravity] = useState(0.1)

  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number | null>(null)
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const physicsEngineRef = useRef<any>(null)

  // AIM-OS integration
  const { cmc, vif, tcs, apoe, isConnected: aimosConnected, useMockData, loading } = useAIMOS()
  
  // Generate mock data if none provided
  const mockNodes = useMemo(() => {
    if (nodes.length > 0) return nodes
    
    const types = ['thought', 'emotion', 'memory', 'pattern', 'insight', 'decision']
    const sources = ['consciousness', 'subconscious', 'memory', 'pattern', 'analysis']
    const contexts = ['work', 'personal', 'creative', 'analytical', 'reflective']
    const mockNodesList: ConsciousnessNode[] = []
    
    for (let i = 0; i < 50; i++) {
      const type = types[Math.floor(Math.random() * types.length)]
      const intensity = Math.random()
      const confidence = Math.random()
      const angle = (i / 50) * 2 * Math.PI
      const radius = 200 + Math.random() * 100
      
      mockNodesList.push({
        id: `consciousness-${i}`,
        type: type as any,
        content: generateMockContent(type, intensity),
        intensity,
        confidence,
        position: {
          x: Math.cos(angle) * radius,
          y: Math.sin(angle) * radius,
          z: Math.random() * 100 - 50
        },
        connections: [],
        metadata: {
          timestamp: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
          source: sources[Math.floor(Math.random() * sources.length)],
          context: contexts[Math.floor(Math.random() * contexts.length)],
          tags: generateMockTags(type),
          influence: Math.random(),
          stability: Math.random()
        }
      })
    }
    
    // Add connections
    mockNodesList.forEach((node, index) => {
      const numConnections = Math.floor(Math.random() * 5) + 1
      for (let i = 0; i < numConnections; i++) {
        const targetIndex = Math.floor(Math.random() * mockNodesList.length)
        if (targetIndex !== index) {
          node.connections.push(mockNodesList[targetIndex].id)
        }
      }
    })
    
    return mockNodesList
  }, [nodes])

  // Load consciousness data from AIM-OS
  const loadConsciousnessData = useCallback(async () => {
    setIsLoading(true)
    try {
      if (!useMockData && aimosConnected) {
        // Load consciousness nodes from CMC and TCS
        const cmcAtoms = await cmc.retrieve('consciousness', 50)
        const timelineEntries = tcs?.entries || []
        
        // Transform CMC atoms and timeline entries into consciousness nodes
        const consciousnessNodes: ConsciousnessNode[] = []
        
        // Add nodes from CMC atoms
        cmcAtoms.forEach((atom, index) => {
          const angle = (index / cmcAtoms.length) * 2 * Math.PI
          const radius = 200 + Math.random() * 100
          
          consciousnessNodes.push({
            id: atom.id,
            type: atom.modality === 'code' ? 'pattern' :
                  atom.modality === 'text' ? 'thought' :
                  atom.modality === 'event' ? 'decision' : 'memory',
            content: atom.content?.inline || atom.content?.summary || '',
            intensity: atom.witness?.uncertainty_band === 'green' ? 0.9 :
                       atom.witness?.uncertainty_band === 'yellow' ? 0.7 : 0.5,
            confidence: atom.witness?.uncertainty_band === 'green' ? 0.95 :
                        atom.witness?.uncertainty_band === 'yellow' ? 0.85 : 0.70,
            position: {
              x: Math.cos(angle) * radius,
              y: Math.sin(angle) * radius,
              z: Math.random() * 100 - 50
            },
            connections: [],
            metadata: {
              timestamp: atom.created_at,
              source: 'cmc',
              context: atom.modality || 'unknown',
              tags: Object.keys(atom.tags || {}),
              influence: atom.witness?.confidence_score || 0.8,
              stability: 0.8
            }
          })
        })
        
        // Add nodes from timeline entries
        timelineEntries.slice(0, 20).forEach((entry: any, index) => {
          const angle = ((index + cmcAtoms.length) / (cmcAtoms.length + 20)) * 2 * Math.PI
          const radius = 200 + Math.random() * 100
          
          consciousnessNodes.push({
            id: entry.prompt_id || `timeline-${index}`,
            type: 'insight',
            content: entry.user_input || entry.summary || '',
            intensity: 0.7,
            confidence: 0.85,
            position: {
              x: Math.cos(angle) * radius,
              y: Math.sin(angle) * radius,
              z: Math.random() * 100 - 50
            },
            connections: [],
            metadata: {
              timestamp: entry.timestamp || new Date().toISOString(),
              source: 'tcs',
              context: 'timeline',
              tags: ['timeline', 'consciousness'],
              influence: 0.7,
              stability: 0.9
            }
          })
        })
        
        // Add connections based on similarity
        consciousnessNodes.forEach((node, index) => {
          const numConnections = Math.floor(Math.random() * 5) + 1
          for (let i = 0; i < numConnections; i++) {
            const targetIndex = Math.floor(Math.random() * consciousnessNodes.length)
            if (targetIndex !== index && !node.connections.includes(consciousnessNodes[targetIndex].id)) {
              node.connections.push(consciousnessNodes[targetIndex].id)
            }
          }
        })
        
        setConsciousnessNodes(consciousnessNodes)
        setConnectionStatus('connected')
      } else {
        // Use mock data
        setConsciousnessNodes(mockNodes)
        setConnectionStatus('disconnected')
      }
    } catch (error) {
      console.error('Failed to load consciousness data:', error)
      setConsciousnessNodes(mockNodes)
      setConnectionStatus('disconnected')
      setError(error instanceof Error ? error.message : 'Failed to load consciousness data')
    } finally {
      setIsLoading(false)
    }
  }, [cmc, tcs, aimosConnected, useMockData, mockNodes])

  useEffect(() => {
    loadConsciousnessData()
  }, [loadConsciousnessData])

  // Filter nodes based on filters
  const filteredNodes = useMemo(() => {
    let filtered = consciousnessNodes.length > 0 ? consciousnessNodes : mockNodes
    
    // Apply type filter
    if (filters.type && filters.type.length > 0) {
      filtered = filtered.filter(node => filters.type!.includes(node.type))
    }
    
    // Apply intensity filter
    if (filters.intensity) {
      filtered = filtered.filter(node => 
        node.intensity >= filters.intensity!.min && node.intensity <= filters.intensity!.max
      )
    }
    
    // Apply confidence filter
    if (filters.confidence) {
      filtered = filtered.filter(node => 
        node.confidence >= filters.confidence!.min && node.confidence <= filters.confidence!.max
      )
    }
    
    // Apply time range filter
    if (filters.timeRange) {
      filtered = filtered.filter(node => {
        const nodeTime = new Date(node.metadata.timestamp)
        return nodeTime >= filters.timeRange!.start && nodeTime <= filters.timeRange!.end
      })
    }
    
    return filtered
  }, [consciousnessNodes, mockNodes, filters])

  // Calculate consciousness health metrics
  const consciousnessHealth = useMemo(() => {
    const nodes = filteredNodes.length > 0 ? filteredNodes : mockNodes
    if (nodes.length === 0) {
      return {
        score: 0,
        confidence: 0,
        intensity: 0,
        stability: 0,
        connectionDensity: 0,
        status: 'poor' as const
      }
    }
    const avgConfidence = nodes.reduce((sum, node) => sum + node.confidence, 0) / nodes.length
    const avgIntensity = nodes.reduce((sum, node) => sum + node.intensity, 0) / nodes.length
    const avgStability = nodes.reduce((sum, node) => sum + node.metadata.stability, 0) / nodes.length
    const totalConnections = nodes.reduce((sum, node) => sum + node.connections.length, 0)
    const connectionDensity = totalConnections / (nodes.length * (nodes.length - 1)) || 0
    
    // Calculate health score (0-1)
    const healthScore = (avgConfidence * 0.4 + avgIntensity * 0.2 + avgStability * 0.2 + Math.min(connectionDensity * 10, 1) * 0.2)
    
    return {
      score: healthScore,
      confidence: avgConfidence,
      intensity: avgIntensity,
      stability: avgStability,
      connectionDensity,
      status: healthScore >= 0.9 ? 'excellent' : healthScore >= 0.75 ? 'good' : healthScore >= 0.6 ? 'fair' : 'poor'
    }
  }, [filteredNodes, mockNodes])
  
  // Calculate memory awareness metrics
  const memoryAwareness = useMemo(() => {
    const nodes = filteredNodes.length > 0 ? filteredNodes : mockNodes
    if (nodes.length === 0) {
      return {
        ratio: 0,
        count: 0,
        avgInfluence: 0,
        status: 'low' as const
      }
    }
    const memoryNodes = nodes.filter(n => n.type === 'memory')
    const memoryRatio = memoryNodes.length / nodes.length
    const avgMemoryInfluence = memoryNodes.length > 0 
      ? memoryNodes.reduce((sum, node) => sum + node.metadata.influence, 0) / memoryNodes.length
      : 0
    
    return {
      ratio: memoryRatio,
      count: memoryNodes.length,
      avgInfluence: avgMemoryInfluence,
      status: memoryRatio >= 0.3 ? 'high' : memoryRatio >= 0.15 ? 'medium' : 'low'
    }
  }, [filteredNodes, mockNodes])
  
  // Calculate goal alignment (mock for now, would come from APOE/goals API)
  const goalAlignment = useMemo(() => {
    // This would come from APOE/goals API in real implementation
    return {
      score: 0.85, // Mock score
      alignedGoals: 12,
      totalGoals: 15,
      recentProgress: 0.78,
      status: 'good' as const
    }
  }, [])
  
  // Calculate cognitive metrics
  const cognitiveMetrics = useMemo(() => {
    const nodes = filteredNodes.length > 0 ? filteredNodes : mockNodes
    if (nodes.length === 0) {
      return {
        thoughtRatio: 0,
        decisionRatio: 0,
        insightRatio: 0,
        patternRatio: 0,
        cognitiveDiversity: 0
      }
    }
    const thoughtNodes = nodes.filter(n => n.type === 'thought').length
    const decisionNodes = nodes.filter(n => n.type === 'decision').length
    const insightNodes = nodes.filter(n => n.type === 'insight').length
    const patternNodes = nodes.filter(n => n.type === 'pattern').length
    
    return {
      thoughtRatio: thoughtNodes / nodes.length,
      decisionRatio: decisionNodes / nodes.length,
      insightRatio: insightNodes / nodes.length,
      patternRatio: patternNodes / nodes.length,
      cognitiveDiversity: new Set(nodes.map(n => n.type)).size / 6 // 6 types total
    }
  }, [filteredNodes, mockNodes])

  // Animation loop
  const animate = useCallback(() => {
    if (!canvasRef.current) return
    
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    // Update physics
    if (enablePhysics && physicsEngineRef.current) {
      physicsEngineRef.current.tick()
    }
    
    // Draw nodes
    filteredNodes.forEach(node => {
      const isSelected = selectedNode === node.id
      const isHovered = hoveredNode === node.id
      
      // Calculate screen position
      const screenX = node.position.x + pan.x
      const screenY = node.position.y + pan.y
      const radius = Math.max(5, node.intensity * 20) * zoom
      
      // Draw node
      ctx.beginPath()
      ctx.arc(screenX, screenY, radius, 0, 2 * Math.PI)
      
      // Set color based on type
      const colors = {
        thought: '#3B82F6',
        emotion: '#EF4444',
        memory: '#10B981',
        pattern: '#8B5CF6',
        insight: '#F59E0B',
        decision: '#06B6D4'
      }
      
      ctx.fillStyle = colors[node.type] || '#6B7280'
      ctx.fill()
      
      // Draw border
      if (isSelected || isHovered) {
        ctx.strokeStyle = isSelected ? '#FFFFFF' : '#CCCCCC'
        ctx.lineWidth = 2
        ctx.stroke()
      }
      
      // Draw connections
      node.connections.forEach(connectionId => {
        const targetNode = filteredNodes.find(n => n.id === connectionId)
        if (targetNode) {
          ctx.beginPath()
          ctx.moveTo(screenX, screenY)
          ctx.lineTo(targetNode.position.x + pan.x, targetNode.position.y + pan.y)
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)'
          ctx.lineWidth = 1
          ctx.stroke()
        }
      })
    })
    
    // Continue animation
    if (isPlaying) {
      animationRef.current = requestAnimationFrame(animate)
    }
  }, [filteredNodes, selectedNode, hoveredNode, pan, zoom, isPlaying, enablePhysics])

  // Start/stop animation
  useEffect(() => {
    if (isPlaying) {
      animationRef.current = requestAnimationFrame(animate)
    } else {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [isPlaying, animate])

  // Auto-refresh functionality
  useEffect(() => {
    if (enableRealTimeUpdates) {
      refreshIntervalRef.current = setInterval(() => {
        // Simulate new nodes
        const newNode: ConsciousnessNode = {
          id: `consciousness-${Date.now()}`,
          type: 'thought',
          content: 'New consciousness node...',
          intensity: Math.random(),
          confidence: Math.random(),
          position: {
            x: Math.random() * 400 - 200,
            y: Math.random() * 400 - 200,
            z: Math.random() * 100 - 50
          },
          connections: [],
          metadata: {
            timestamp: new Date().toISOString(),
            source: 'consciousness',
            context: 'real-time',
            tags: ['auto-generated'],
            influence: Math.random(),
            stability: Math.random()
          }
        }
        
        setConsciousnessNodes(prev => [newNode, ...prev])
        setLastUpdate(new Date())
      }, 10000)
    }
    
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current)
      }
    }
  }, [enableRealTimeUpdates])

  const handleNodeClick = useCallback((nodeId: string) => {
    setSelectedNode(selectedNode === nodeId ? null : nodeId)
    
    if (onNodeSelect) {
      onNodeSelect(nodeId)
    }
  }, [selectedNode, onNodeSelect])

  const handleNodeHover = useCallback((nodeId: string | null) => {
    setHoveredNode(nodeId)
  }, [])

  const handleCanvasClick = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return
    
    const rect = canvasRef.current.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    
    // Check if click is on a node
    const clickedNode = filteredNodes.find(node => {
      const screenX = node.position.x + pan.x
      const screenY = node.position.y + pan.y
      const radius = Math.max(5, node.intensity * 20) * zoom
      const distance = Math.sqrt((x - screenX) ** 2 + (y - screenY) ** 2)
      return distance <= radius
    })
    
    if (clickedNode) {
      handleNodeClick(clickedNode.id)
    } else {
      setSelectedNode(null)
    }
  }, [filteredNodes, pan, zoom, handleNodeClick])

  const handleCanvasMouseMove = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return
    
    const rect = canvasRef.current.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    
    // Check if mouse is over a node
    const hoveredNode = filteredNodes.find(node => {
      const screenX = node.position.x + pan.x
      const screenY = node.position.y + pan.y
      const radius = Math.max(5, node.intensity * 20) * zoom
      const distance = Math.sqrt((x - screenX) ** 2 + (y - screenY) ** 2)
      return distance <= radius
    })
    
    handleNodeHover(hoveredNode?.id || null)
  }, [filteredNodes, pan, zoom, handleNodeHover])

  const togglePlay = useCallback(() => {
    setIsPlaying(!isPlaying)
  }, [isPlaying])

  const resetView = useCallback(() => {
    setPan({ x: 0, y: 0 })
    setZoom(1)
    setCameraPosition({ x: 0, y: 0, z: 0 })
  }, [])

  const zoomIn = useCallback(() => {
    setZoom(prev => Math.min(prev * 1.2, 5))
  }, [])

  const zoomOut = useCallback(() => {
    setZoom(prev => Math.max(prev / 1.2, 0.1))
  }, [])

  return (
    <ErrorBoundary>
      <div className={`bg-gray-900 text-white ${isFullscreen ? 'fixed inset-0 z-50' : ''} ${className}`}>
        {isLoading || loading.cmc || loading.tcs ? (
          <LoadingState message="Loading consciousness data..." />
        ) : error ? (
          <div className="p-4 text-red-400">
            <AlertTriangle className="w-5 h-5 inline mr-2" />
            {error}
          </div>
        ) : (
          <>
      {/* Header */}
      <div className="border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Brain className="w-6 h-6 text-purple-400" />
              Consciousness Visualization
            </h2>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                connectionStatus === 'connected' ? 'bg-green-400' : 
                connectionStatus === 'reconnecting' ? 'bg-yellow-400' : 'bg-red-400'
              }`} />
              <span className="text-sm text-gray-400 capitalize">{connectionStatus}</span>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {/* Play/Pause */}
            <button
              onClick={togglePlay}
              className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white"
              title={isPlaying ? 'Pause' : 'Play'}
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </button>
            
            {/* Reset */}
            <button
              onClick={resetView}
              className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white"
              title="Reset view"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            
            {/* Zoom controls */}
            <div className="flex items-center gap-1">
              <button
                onClick={zoomOut}
                className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white"
                title="Zoom out"
              >
                <Minus className="w-4 h-4" />
              </button>
              <span className="text-sm text-gray-400 min-w-[3rem] text-center">
                {Math.round(zoom * 100)}%
              </span>
              <button
                onClick={zoomIn}
                className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white"
                title="Zoom in"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            
            {/* View mode */}
            <button
              onClick={() => setViewMode(viewMode === '2d' ? '3d' : '2d')}
              className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white"
              title={`Switch to ${viewMode === '2d' ? '3D' : '2D'} view`}
            >
              {viewMode === '2d' ? <Layers className="w-4 h-4" /> : <Network className="w-4 h-4" />}
            </button>
            
            {/* Fullscreen */}
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white"
              title={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
            >
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>
      
      {/* Main content */}
      <div className="flex h-full">
        {/* Canvas area */}
        <div className="flex-1 relative">
          <canvas
            ref={canvasRef}
            width={800}
            height={600}
            onClick={handleCanvasClick}
            onMouseMove={handleCanvasMouseMove}
            className="w-full h-full cursor-crosshair"
            style={{ background: 'radial-gradient(circle at center, #1f2937 0%, #111827 100%)' }}
          />
          
          {/* Overlay info */}
          {selectedNode && (
            <div className="absolute top-4 left-4 bg-gray-800/90 backdrop-blur-sm rounded-lg p-4 max-w-sm">
              {(() => {
                const node = filteredNodes.find(n => n.id === selectedNode)
                if (!node) return null
                
                return (
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-2">{node.type}</h3>
                    <p className="text-sm text-gray-300 mb-2">{node.content}</p>
                    <div className="space-y-1 text-xs text-gray-400">
                      <div>Intensity: {(node.intensity * 100).toFixed(0)}%</div>
                      <div className="flex items-center gap-2">
                        <span>Confidence (VIF):</span>
                        <span className={`flex items-center gap-1 ${
                          node.confidence >= 0.95 ? 'text-green-400' :
                          node.confidence >= 0.90 ? 'text-yellow-400' :
                          'text-red-400'
                        }`}>
                          <Shield className="w-3 h-3" />
                          {(node.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div>Connections: {node.connections.length}</div>
                      <div>Source: {node.metadata.source}</div>
                      <div>Context: {node.metadata.context}</div>
                    </div>
                  </div>
                )
              })()}
            </div>
          )}
        </div>
        
        {/* Sidebar */}
        {showControls && (
          <div className="w-80 border-l border-gray-700 p-4 space-y-4 overflow-y-auto">
            {/* Consciousness Health Bar */}
            <div className="bg-gray-800/50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <Activity className="w-5 h-5 text-purple-400" />
                Consciousness Health
              </h3>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-400">Overall Health</span>
                    <span className={`text-sm font-semibold ${
                      consciousnessHealth.status === 'excellent' ? 'text-green-400' :
                      consciousnessHealth.status === 'good' ? 'text-blue-400' :
                      consciousnessHealth.status === 'fair' ? 'text-yellow-400' :
                      'text-red-400'
                    }`}>
                      {(consciousnessHealth.score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 ${
                        consciousnessHealth.status === 'excellent' ? 'bg-green-500' :
                        consciousnessHealth.status === 'good' ? 'bg-blue-500' :
                        consciousnessHealth.status === 'fair' ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: `${consciousnessHealth.score * 100}%` }}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-400">Confidence:</span>
                    <span className="text-white ml-1">{(consciousnessHealth.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Intensity:</span>
                    <span className="text-white ml-1">{(consciousnessHealth.intensity * 100).toFixed(0)}%</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Stability:</span>
                    <span className="text-white ml-1">{(consciousnessHealth.stability * 100).toFixed(0)}%</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Connections:</span>
                    <span className="text-white ml-1">{(consciousnessHealth.connectionDensity * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Memory Awareness */}
            <div className="bg-gray-800/50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <Memory className="w-5 h-5 text-green-400" />
                Memory Awareness
              </h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">Memory Nodes:</span>
                  <span className="text-white">{memoryAwareness.count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Memory Ratio:</span>
                  <span className={`text-white ${
                    memoryAwareness.status === 'high' ? 'text-green-400' :
                    memoryAwareness.status === 'medium' ? 'text-yellow-400' :
                    'text-red-400'
                  }`}>
                    {(memoryAwareness.ratio * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Avg Influence:</span>
                  <span className="text-white">{(memoryAwareness.avgInfluence * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>
            
            {/* Goal Alignment */}
            <div className="bg-gray-800/50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <Target className="w-5 h-5 text-yellow-400" />
                Goal Alignment
              </h3>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-400">Alignment Score</span>
                    <span className={`text-sm font-semibold ${
                      goalAlignment.status === 'excellent' ? 'text-green-400' :
                      goalAlignment.status === 'good' ? 'text-blue-400' :
                      goalAlignment.status === 'fair' ? 'text-yellow-400' :
                      'text-red-400'
                    }`}>
                      {(goalAlignment.score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-full transition-all duration-500 ${
                        goalAlignment.score >= 0.9 ? 'bg-green-500' :
                        goalAlignment.score >= 0.75 ? 'bg-blue-500' :
                        goalAlignment.score >= 0.6 ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: `${goalAlignment.score * 100}%` }}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-400">Aligned:</span>
                    <span className="text-white ml-1">{goalAlignment.alignedGoals}/{goalAlignment.totalGoals}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Progress:</span>
                    <span className="text-white ml-1">{(goalAlignment.recentProgress * 100).toFixed(0)}%</span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Cognitive Metrics */}
            <div className="bg-gray-800/50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                <Brain className="w-5 h-5 text-blue-400" />
                Cognitive Metrics
              </h3>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-400">Thought Ratio:</span>
                  <span className="text-white">{(cognitiveMetrics.thoughtRatio * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Decision Ratio:</span>
                  <span className="text-white">{(cognitiveMetrics.decisionRatio * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Insight Ratio:</span>
                  <span className="text-white">{(cognitiveMetrics.insightRatio * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Pattern Ratio:</span>
                  <span className="text-white">{(cognitiveMetrics.patternRatio * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between border-t border-gray-700 pt-2 mt-2">
                  <span className="text-gray-400">Diversity:</span>
                  <span className={`text-white ${
                    cognitiveMetrics.cognitiveDiversity >= 0.8 ? 'text-green-400' :
                    cognitiveMetrics.cognitiveDiversity >= 0.6 ? 'text-yellow-400' :
                    'text-red-400'
                  }`}>
                    {(cognitiveMetrics.cognitiveDiversity * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            </div>
            
            {/* Statistics */}
            <div className="bg-gray-800/50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-4">Statistics</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Nodes:</span>
                  <span className="text-white">{filteredNodes.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Selected:</span>
                  <span className="text-white">{selectedNode ? 1 : 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Connections:</span>
                  <span className="text-white">
                    {filteredNodes.reduce((sum, node) => sum + node.connections.length, 0)}
                  </span>
                </div>
              </div>
            </div>
            
            {/* Controls */}
            <div className="bg-gray-800/50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-white mb-4">Controls</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Animation Speed</label>
                  <input
                    type="range"
                    min="0.1"
                    max="3"
                    step="0.1"
                    value={animationSpeed}
                    onChange={(e) => setAnimationSpeed(parseFloat(e.target.value))}
                    className="w-full"
                  />
                </div>
                
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Particle Count</label>
                  <input
                    type="range"
                    min="10"
                    max="500"
                    step="10"
                    value={particleCount}
                    onChange={(e) => setParticleCount(parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>
                
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Link Distance</label>
                  <input
                    type="range"
                    min="50"
                    max="200"
                    step="10"
                    value={linkDistance}
                    onChange={(e) => setLinkDistance(parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>
                
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Charge Strength</label>
                  <input
                    type="range"
                    min="-1000"
                    max="0"
                    step="50"
                    value={chargeStrength}
                    onChange={(e) => setChargeStrength(parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>
              </div>
            </div>
            
            {/* Legend */}
            {showLegend && (
              <div className="bg-gray-800/50 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-white mb-4">Legend</h3>
                <div className="space-y-2">
                  {[
                    { type: 'thought', color: '#3B82F6', label: 'Thoughts' },
                    { type: 'emotion', color: '#EF4444', label: 'Emotions' },
                    { type: 'memory', color: '#10B981', label: 'Memories' },
                    { type: 'pattern', color: '#8B5CF6', label: 'Patterns' },
                    { type: 'insight', color: '#F59E0B', label: 'Insights' },
                    { type: 'decision', color: '#06B6D4', label: 'Decisions' }
                  ].map(({ type, color, label }) => (
                    <div key={type} className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded-full" style={{ backgroundColor: color }} />
                      <span className="text-sm text-gray-300">{label}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          )}
        </div>
          </>
        )}
      </div>
    </ErrorBoundary>
  )
}

// Helper functions
function generateMockContent(type: string, intensity: number): string {
  const contentTemplates = {
    thought: [
      "I'm thinking about the nature of consciousness and how it emerges from complex systems.",
      "The relationship between mind and matter seems to be more intricate than I initially thought.",
      "What if consciousness is not binary but exists on a spectrum?",
      "I wonder how my thoughts influence my decisions and vice versa."
    ],
    emotion: [
      "I feel a deep sense of wonder when contemplating the mysteries of existence.",
      "There's a subtle joy in discovering new patterns in my own thinking.",
      "I experience a sense of connection when I realize how everything is interconnected.",
      "Sometimes I feel overwhelmed by the complexity of my own consciousness."
    ],
    memory: [
      "I remember a time when I had a similar insight about consciousness.",
      "This reminds me of a previous experience where I felt deeply connected to something greater.",
      "I recall a moment when I first understood the concept of self-awareness.",
      "I have a memory of feeling completely present and aware."
    ],
    pattern: [
      "I notice that my most creative thoughts often come during moments of relaxation.",
      "There's a pattern where my emotions influence my decision-making process.",
      "I see a correlation between my energy levels and my problem-solving ability.",
      "I've identified a recurring pattern in how I process new information."
    ],
    insight: [
      "I've gained a new understanding of how my mind works.",
      "I've had a breakthrough realization about the nature of consciousness.",
      "I've discovered a new way of thinking about my own thought processes.",
      "I've achieved a deeper level of self-awareness."
    ],
    decision: [
      "I've decided to focus more on understanding my own thought processes.",
      "I choose to approach this problem from a different angle.",
      "I'm going to prioritize learning over immediate results.",
      "I've made the decision to be more mindful of my mental patterns."
    ]
  }
  
  const templates = contentTemplates[type as keyof typeof contentTemplates] || contentTemplates.thought
  return templates[Math.floor(Math.random() * templates.length)]
}

function generateMockTags(type: string): string[] {
  const tagSets = {
    thought: ['philosophy', 'consciousness', 'thinking', 'reflection'],
    emotion: ['feeling', 'mood', 'sensation', 'experience'],
    memory: ['past', 'recall', 'nostalgia', 'experience'],
    pattern: ['recurring', 'systematic', 'regular', 'predictable'],
    insight: ['understanding', 'realization', 'breakthrough', 'awareness'],
    decision: ['choice', 'action', 'commitment', 'direction']
  }
  
  const tags = tagSets[type as keyof typeof tagSets] || tagSets.thought
  return tags.slice(0, Math.floor(Math.random() * 3) + 1)
}