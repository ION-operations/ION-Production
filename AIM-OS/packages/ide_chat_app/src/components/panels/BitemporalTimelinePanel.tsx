/**
 * Bitemporal Timeline Panel Component
 * 
 * Phase 2.3: Bottom Drawer Panels
 * 
 * Sequential timeline with playback controls and bitemporal history.
 * Features:
 * - Timeline visualization with playback controls
 * - Bitemporal history tracking (CMC)
 * - VIF confidence visualization
 * - TCS timeline entries integration
 * - State restoration
 * - Change visualization
 * - AIM-OS integration (TCS, CMC, VIF)
 */

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import {
  Calendar,
  Play,
  Pause,
  Square,
  RotateCcw,
  SkipBack,
  SkipForward,
  Clock,
  Activity,
  Zap,
  Target,
  Eye,
  EyeOff,
  Maximize2,
  Minimize2,
  Settings,
  Shield,
  History,
  RefreshCw,
  Filter,
  Search,
} from 'lucide-react'
import { useAIMOS } from '../../hooks/useAIMOS'
import { LoadingState } from '../LoadingState'
import { ErrorBoundary } from '../ErrorBoundary'

interface TimelineEvent {
  id: string
  nodeId: string
  timestamp: number
  type: 'execution' | 'error' | 'test' | 'modification' | 'focus' | 'drift' | 'memory' | 'decision'
  duration: number
  status: 'success' | 'error' | 'warning' | 'info'
  message: string
  nodeName: string
  filePath?: string
  line?: number
  vifConfidence?: number
  cmcAtomId?: string
  bitemporalHistory?: Array<{
    validFrom: string
    validTo?: string
    content: string
    agent?: string
  }>
}

interface TimelineNode {
  id: string
  name: string
  type: 'function' | 'component' | 'class' | 'interface' | 'test' | 'memory' | 'decision'
  color: string
  events: TimelineEvent[]
}

export const BitemporalTimelinePanel: React.FC = () => {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [maxTime, setMaxTime] = useState(1000)
  const [zoom, setZoom] = useState(1)
  const [selectedEvent, setSelectedEvent] = useState<TimelineEvent | null>(null)
  const [showGrid, setShowGrid] = useState(true)
  const [showLabels, setShowLabels] = useState(true)
  const [playbackSpeed, setPlaybackSpeed] = useState(1)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<'all' | TimelineEvent['type']>('all')
  const [showBitemporal, setShowBitemporal] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  
  const timelineRef = useRef<HTMLDivElement>(null)
  const animationRef = useRef<number>()

  // AIM-OS integration
  const { tcs, cmc, vif, isConnected: aimosConnected, useMockData, loading } = useAIMOS()

  // Load timeline data from AIM-OS
  const loadTimelineData = useCallback(async () => {
    setIsLoading(true)
    try {
      if (!useMockData && aimosConnected) {
        // Load timeline entries from TCS
        const timelineEntries = tcs?.entries || []
        
        // Transform TCS entries into timeline nodes and events
        const timelineNodes: TimelineNode[] = []
        const nodeMap = new Map<string, TimelineNode>()
        
        timelineEntries.forEach((entry: any, index: number) => {
          const nodeId = entry.prompt_id || `node-${index}`
          const eventId = `event-${index}`
          
          // Determine event type from entry
          const eventType: TimelineEvent['type'] = 
            entry.user_input?.includes('error') ? 'error' :
            entry.user_input?.includes('test') ? 'test' :
            entry.user_input?.includes('memory') ? 'memory' :
            entry.user_input?.includes('decision') ? 'decision' :
            'execution'
          
          // Determine status
          const status: TimelineEvent['status'] = 
            entry.context_state?.error ? 'error' :
            entry.context_state?.warning ? 'warning' :
            'success'
          
          // Get VIF confidence from entry or calculate
          const vifConfidence = entry.confidence || 
            (entry.context_state?.confidence || 0.85)
          
          // Create or get node
          if (!nodeMap.has(nodeId)) {
            const node: TimelineNode = {
              id: nodeId,
              name: entry.user_input?.substring(0, 30) || `Entry ${index + 1}`,
              type: eventType === 'memory' ? 'memory' :
                    eventType === 'decision' ? 'decision' :
                    'function',
              color: status === 'error' ? 'bg-red-500' :
                     status === 'warning' ? 'bg-yellow-500' :
                     status === 'success' ? 'bg-green-500' :
                     'bg-blue-500',
              events: []
            }
            nodeMap.set(nodeId, node)
            timelineNodes.push(node)
          }
          
          const node = nodeMap.get(nodeId)!
          
          // Create event
          const timestamp = entry.timestamp ? new Date(entry.timestamp).getTime() : Date.now() - (timelineEntries.length - index) * 1000
          const event: TimelineEvent = {
            id: eventId,
            nodeId,
            timestamp,
            type: eventType,
            duration: 100,
            status,
            message: entry.user_input || entry.summary || '',
            nodeName: node.name,
            vifConfidence,
            cmcAtomId: entry.atom_id,
          }
          
          node.events.push(event)
        })
        
        // Sort events by timestamp
        timelineNodes.forEach(node => {
          node.events.sort((a, b) => a.timestamp - b.timestamp)
        })
        
        // Calculate max time
        const allEvents = timelineNodes.flatMap(node => node.events)
        const maxEventTime = allEvents.length > 0 
          ? Math.max(...allEvents.map(e => e.timestamp + e.duration))
          : 1000
        
        setMaxTime(Math.max(maxEventTime, 1000))
        setTimelineNodes(timelineNodes)
      } else {
        // Use mock data
        const mockNodes: TimelineNode[] = [
          {
            id: 'node-1',
            name: 'processUserData',
            type: 'function',
            color: 'bg-blue-500',
            events: [
              {
                id: 'event-1',
                nodeId: 'node-1',
                timestamp: 0,
                type: 'execution',
                duration: 150,
                status: 'success',
                message: 'processUserData executed successfully',
                nodeName: 'processUserData',
                filePath: 'src/utils/user.ts',
                line: 45,
                vifConfidence: 0.95,
              },
            ]
          },
        ]
        setTimelineNodes(mockNodes)
        setMaxTime(1000)
      }
    } catch (error) {
      console.error('Failed to load timeline data:', error)
      setError(error instanceof Error ? error.message : 'Failed to load timeline data')
    } finally {
      setIsLoading(false)
    }
  }, [tcs, cmc, vif, aimosConnected, useMockData])

  const [timelineNodes, setTimelineNodes] = useState<TimelineNode[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadTimelineData()
  }, [loadTimelineData])

  // Calculate max time from all events
  useEffect(() => {
    const allEvents = timelineNodes.flatMap(node => node.events)
    const maxEventTime = allEvents.length > 0
      ? Math.max(...allEvents.map(e => e.timestamp + e.duration))
      : 1000
    setMaxTime(Math.max(maxEventTime, 1000))
  }, [timelineNodes])

  // Animation loop
  useEffect(() => {
    if (isPlaying) {
      const animate = () => {
        setCurrentTime(prev => {
          const newTime = prev + (0.1 * playbackSpeed)
          if (newTime >= maxTime) {
            setIsPlaying(false)
            return 0
          }
          return newTime
        })
        animationRef.current = requestAnimationFrame(animate)
      }
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
  }, [isPlaying, maxTime, playbackSpeed])

  const getEventStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'bg-green-500'
      case 'error': return 'bg-red-500'
      case 'warning': return 'bg-yellow-500'
      case 'info': return 'bg-blue-500'
      default: return 'bg-gray-500'
    }
  }

  const getEventTypeIcon = (type: string) => {
    switch (type) {
      case 'execution': return <Activity className="w-3 h-3" />
      case 'error': return <Target className="w-3 h-3" />
      case 'test': return <Zap className="w-3 h-3" />
      case 'modification': return <Settings className="w-3 h-3" />
      case 'focus': return <Eye className="w-3 h-3" />
      case 'drift': return <Clock className="w-3 h-3" />
      case 'memory': return <History className="w-3 h-3" />
      case 'decision': return <Target className="w-3 h-3" />
      default: return <Activity className="w-3 h-3" />
    }
  }

  const formatTime = (time: number) => {
    const seconds = Math.floor(time / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)
    if (hours > 0) {
      return `${hours}:${String(minutes % 60).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`
    }
    return `${minutes}:${String(seconds % 60).padStart(2, '0')}`
  }

  const filteredNodes = useMemo(() => {
    return timelineNodes.filter(node => {
      const matchesSearch = searchTerm === '' ||
        node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        node.events.some(e => e.message.toLowerCase().includes(searchTerm.toLowerCase()))
      
      const matchesType = filterType === 'all' ||
        node.events.some(e => e.type === filterType)
      
      return matchesSearch && matchesType
    })
  }, [timelineNodes, searchTerm, filterType])

  const filteredEvents = useMemo(() => {
    return filteredNodes.flatMap(node => node.events)
      .filter(event => {
        const matchesType = filterType === 'all' || event.type === filterType
        return matchesType
      })
      .sort((a, b) => a.timestamp - b.timestamp)
  }, [filteredNodes, filterType])

  const handleEventClick = useCallback(async (event: TimelineEvent) => {
    setSelectedEvent(event)
    
    // Load bitemporal history if CMC atom ID exists
    if (event.cmcAtomId && !useMockData && aimosConnected) {
      try {
        const atoms = await cmc.retrieve(event.cmcAtomId, 10)
        if (atoms.length > 0) {
          const atom = atoms[0]
          // Transform CMC atom history to bitemporal history
          const history = atom.metadata?.bitemporalHistory || []
          setSelectedEvent(prev => prev ? { ...prev, bitemporalHistory: history } : null)
        }
      } catch (error) {
        console.error('Failed to load bitemporal history:', error)
      }
    }
  }, [cmc, aimosConnected, useMockData])

  return (
    <ErrorBoundary>
      <div className="h-full flex flex-col bg-gray-900 text-gray-200">
        {isLoading || loading.tcs || loading.cmc ? (
          <LoadingState message="Loading timeline data..." />
        ) : (
          <>
            {/* Header */}
            <div className="px-4 py-3 border-b border-gray-700 flex items-center gap-2 shrink-0">
              <Calendar className="w-5 h-5 text-purple-400" />
              <div>
                <div className="text-white text-sm font-semibold">Bitemporal Timeline ⭐</div>
                <div className="text-xs text-gray-500">TCS & CMC Integration</div>
              </div>
              <span
                className={`ml-auto px-2 py-1 rounded-full text-xs font-medium ${
                  aimosConnected ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                }`}
              >
                {aimosConnected ? 'Connected' : 'Mock Mode'}
              </span>
              <button onClick={loadTimelineData} className="text-gray-400 hover:text-white p-1 rounded">
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>

            {/* Search and Filters */}
            <div className="p-3 border-b border-gray-700 shrink-0 space-y-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search timeline..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full bg-gray-800 text-white text-sm px-9 py-2 rounded focus:outline-none focus:ring-2 focus:ring-purple-500 border border-gray-700"
                />
              </div>

              <div className="flex gap-2 overflow-x-auto pb-1">
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value as any)}
                  className="px-3 py-1 text-xs rounded bg-gray-700 text-gray-300 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="all">All Types</option>
                  <option value="execution">Execution</option>
                  <option value="error">Error</option>
                  <option value="test">Test</option>
                  <option value="modification">Modification</option>
                  <option value="memory">Memory</option>
                  <option value="decision">Decision</option>
                </select>
              </div>
            </div>

            {/* Playback Controls */}
            <div className="px-4 py-2 border-b border-gray-700 flex items-center gap-2 shrink-0">
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white"
                title={isPlaying ? 'Pause' : 'Play'}
              >
                {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              </button>
              <button
                onClick={() => setCurrentTime(0)}
                className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white"
                title="Reset"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
              <button
                onClick={() => setCurrentTime(Math.max(0, currentTime - 1000))}
                className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white"
                title="Skip Back"
              >
                <SkipBack className="w-4 h-4" />
              </button>
              <button
                onClick={() => setCurrentTime(Math.min(maxTime, currentTime + 1000))}
                className="p-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white"
                title="Skip Forward"
              >
                <SkipForward className="w-4 h-4" />
              </button>
              <div className="flex-1 mx-4">
                <input
                  type="range"
                  min="0"
                  max={maxTime}
                  value={currentTime}
                  onChange={(e) => setCurrentTime(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>
              <span className="text-xs text-gray-400 min-w-[80px] text-right">
                {formatTime(currentTime)} / {formatTime(maxTime)}
              </span>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400">Speed:</span>
                <input
                  type="range"
                  min="0.1"
                  max="3"
                  step="0.1"
                  value={playbackSpeed}
                  onChange={(e) => setPlaybackSpeed(parseFloat(e.target.value))}
                  className="w-20"
                />
                <span className="text-xs text-gray-400 min-w-[40px]">{playbackSpeed}x</span>
              </div>
            </div>

            {/* Timeline Canvas */}
            <div className="flex-1 overflow-auto p-4" ref={timelineRef}>
              {filteredNodes.length === 0 ? (
                <div className="flex items-center justify-center h-full text-gray-400">
                  <div className="text-center">
                    <Calendar className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No timeline data found</p>
                    <p className="text-xs mt-1">Try adjusting filters or search</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredNodes.map((node) => (
                    <div key={node.id} className="border border-gray-700 rounded-lg p-4 bg-gray-800/50">
                      <div className="flex items-center gap-2 mb-3">
                        <div className={`w-3 h-3 rounded-full ${node.color}`} />
                        <span className="font-semibold text-white">{node.name}</span>
                        <span className="text-xs text-gray-400 capitalize">{node.type}</span>
                      </div>
                      <div className="space-y-2">
                        {node.events
                          .filter(event => filterType === 'all' || event.type === filterType)
                          .map((event) => {
                            const isPast = event.timestamp <= currentTime
                            const isActive = event.timestamp <= currentTime && 
                                           (event.timestamp + event.duration) >= currentTime
                            const isSelected = selectedEvent?.id === event.id
                            
                            return (
                              <div
                                key={event.id}
                                onClick={() => handleEventClick(event)}
                                className={`p-3 rounded border cursor-pointer transition-all ${
                                  isSelected
                                    ? 'bg-purple-500/20 border-purple-500'
                                    : isActive
                                    ? 'bg-blue-500/20 border-blue-500'
                                    : isPast
                                    ? 'bg-gray-700/50 border-gray-600'
                                    : 'bg-gray-800/50 border-gray-700 opacity-50'
                                }`}
                              >
                                <div className="flex items-start justify-between mb-2">
                                  <div className="flex items-center gap-2">
                                    {getEventTypeIcon(event.type)}
                                    <span className="text-sm text-gray-300">{event.message}</span>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    {event.vifConfidence !== undefined && (
                                      <span className={`text-xs flex items-center gap-1 ${
                                        event.vifConfidence >= 0.95 ? 'text-green-400' :
                                        event.vifConfidence >= 0.90 ? 'text-yellow-400' :
                                        'text-red-400'
                                      }`}>
                                        <Shield className="w-3 h-3" />
                                        {(event.vifConfidence * 100).toFixed(0)}%
                                      </span>
                                    )}
                                    <span className="text-xs text-gray-400">
                                      {formatTime(event.timestamp)}
                                    </span>
                                  </div>
                                </div>
                                <div className="flex items-center gap-4 text-xs text-gray-500">
                                  <span className={`px-2 py-1 rounded ${getEventStatusColor(event.status)}`}>
                                    {event.status}
                                  </span>
                                  {event.filePath && (
                                    <span>{event.filePath}:{event.line}</span>
                                  )}
                                  {event.cmcAtomId && (
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation()
                                        setShowBitemporal(!showBitemporal)
                                      }}
                                      className="flex items-center gap-1 text-purple-400 hover:text-purple-300"
                                    >
                                      <History className="w-3 h-3" />
                                      History
                                    </button>
                                  )}
                                </div>
                              </div>
                            )
                          })}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Selected Event Details */}
            {selectedEvent && (
              <div className="border-t border-gray-700 p-4 bg-gray-800 shrink-0 max-h-64 overflow-auto">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-semibold text-gray-300">Event Details</h4>
                  <button
                    onClick={() => setSelectedEvent(null)}
                    className="text-gray-400 hover:text-gray-200"
                  >
                    ×
                  </button>
                </div>
                <div className="text-xs text-gray-400 space-y-1">
                  <div>ID: {selectedEvent.id}</div>
                  <div>Type: {selectedEvent.type}</div>
                  <div>Status: {selectedEvent.status}</div>
                  <div>Timestamp: {formatTime(selectedEvent.timestamp)}</div>
                  <div>Duration: {formatTime(selectedEvent.duration)}</div>
                  {selectedEvent.vifConfidence !== undefined && (
                    <div className="flex items-center gap-2">
                      <span>Confidence (VIF):</span>
                      <span className={`flex items-center gap-1 ${
                        selectedEvent.vifConfidence >= 0.95 ? 'text-green-400' :
                        selectedEvent.vifConfidence >= 0.90 ? 'text-yellow-400' :
                        'text-red-400'
                      }`}>
                        <Shield className="w-3 h-3" />
                        {(selectedEvent.vifConfidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}
                  <div className="mt-2">
                    <div className="font-medium text-gray-300 mb-1">Message:</div>
                    <pre className="text-xs text-gray-400 whitespace-pre-wrap">{selectedEvent.message}</pre>
                  </div>
                  
                  {/* Bitemporal History */}
                  {selectedEvent.bitemporalHistory && selectedEvent.bitemporalHistory.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-700">
                      <div className="font-medium text-gray-300 mb-2 flex items-center gap-2">
                        <History className="w-4 h-4" />
                        Bitemporal History ({selectedEvent.bitemporalHistory.length} versions)
                      </div>
                      <div className="space-y-2">
                        {selectedEvent.bitemporalHistory.map((entry, idx) => (
                          <div key={idx} className="p-2 bg-gray-700/50 rounded text-xs">
                            <div className="text-gray-400 mb-1">
                              {entry.validFrom} {entry.validTo ? `→ ${entry.validTo}` : '(current)'}
                            </div>
                            <div className="text-gray-300">{entry.content}</div>
                            {entry.agent && (
                              <div className="text-gray-500 mt-1">Agent: {entry.agent}</div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
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

