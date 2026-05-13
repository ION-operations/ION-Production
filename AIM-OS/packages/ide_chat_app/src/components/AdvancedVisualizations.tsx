// Advanced Visualizations for AIM-OS
// V2 Enhancement - Week 3 Integration
// Timeline graphs, evidence trails, and consciousness visualizations

import React, { useState, useEffect, useMemo } from 'react'
import { useTimeline, useGoals, useEvidence, useConsciousness } from '../hooks/useAIMOS'
import { usePerformanceMonitoring } from '../services/performanceMonitor'
import { Calendar, TrendingUp, Network, Activity, Brain, Target, Database, ArrowRight } from 'lucide-react'

/**
 * Timeline Graph Visualization
 */
interface TimelineGraphProps {
  className?: string
  limit?: number
}

export function TimelineGraph({ className = '', limit = 50 }: TimelineGraphProps) {
  const { entries, loading, error } = useTimeline(limit)
  const [selectedEntry, setSelectedEntry] = useState<any>(null)

  const timelineData = useMemo(() => {
    if (!entries || entries.length === 0) return []
    
    return entries.map((entry: any, index: number) => ({
      id: entry.prompt_id || entry.id || `entry-${index}`,
      timestamp: new Date(entry.timestamp || entry.created_at || Date.now()),
      type: entry.type || 'event',
      label: entry.user_input || entry.description || 'Timeline Entry',
      data: entry
    })).sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
  }, [entries])

  if (loading) {
    return (
      <div className={`flex items-center justify-center h-full ${className}`}>
        <Activity className="w-6 h-6 text-gray-400 animate-pulse" />
        <span className="ml-2 text-gray-400">Loading timeline...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`flex items-center justify-center h-full text-red-400 ${className}`}>
        <span>Failed to load timeline data</span>
      </div>
    )
  }

  return (
    <div className={`flex flex-col h-full bg-gray-900 ${className}`}>
      <div className="p-4 border-b border-gray-700">
        <h3 className="text-lg font-semibold text-gray-300 flex items-center gap-2">
          <Calendar className="w-5 h-5 text-blue-400" />
          Timeline Graph
        </h3>
        <p className="text-sm text-gray-400 mt-1">{timelineData.length} entries</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="relative">
          {/* Timeline Line */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-700" />

          {/* Timeline Entries */}
          <div className="space-y-4">
            {timelineData.map((entry, index) => (
              <div
                key={entry.id}
                className="relative flex items-start gap-4 cursor-pointer hover:bg-gray-800 rounded p-2 transition-colors"
                onClick={() => setSelectedEntry(entry)}
              >
                {/* Timeline Dot */}
                <div className="relative z-10 flex-shrink-0">
                  <div className={`w-4 h-4 rounded-full border-2 border-gray-700 bg-gray-800 ${
                    selectedEntry?.id === entry.id ? 'border-blue-500 bg-blue-500' : ''
                  } transition-all`} />
                </div>

                {/* Entry Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-300 truncate">
                      {entry.label}
                    </span>
                    <span className="text-xs text-gray-500 ml-2">
                      {entry.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="text-xs text-gray-400">
                    {entry.timestamp.toLocaleDateString()} • {entry.type}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Entry Details Panel */}
      {selectedEntry && (
        <div className="border-t border-gray-700 p-4 bg-gray-800">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-semibold text-gray-300">Entry Details</h4>
            <button
              onClick={() => setSelectedEntry(null)}
              className="text-gray-400 hover:text-gray-200"
            >
              ×
            </button>
          </div>
          <pre className="text-xs text-gray-400 overflow-auto max-h-32">
            {JSON.stringify(selectedEntry.data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

/**
 * Evidence Trail Visualization
 */
interface EvidenceTrailVisualizationProps {
  query?: string
  className?: string
}

export function EvidenceTrailVisualization({ query = '', className = '' }: EvidenceTrailVisualizationProps) {
  const { getEvidenceTrails } = useEvidence()
  const [trails, setTrails] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedTrail, setSelectedTrail] = useState<any>(null)
  const [filterStrength, setFilterStrength] = useState<'all' | 'high' | 'medium' | 'low'>('all')
  const [sortBy, setSortBy] = useState<'relevance' | 'timestamp' | 'strength'>('relevance')

  useEffect(() => {
    if (!query) {
      setTrails([])
      return
    }

    const fetchTrails = async () => {
      setLoading(true)
      try {
        const evidence = await getEvidenceTrails(query, 50) // Increased limit
        setTrails(evidence)
      } catch (error) {
        console.warn('Failed to fetch evidence trails:', error)
        setTrails([])
      } finally {
        setLoading(false)
      }
    }

    fetchTrails()
  }, [query, getEvidenceTrails])

  const filteredAndSortedTrails = useMemo(() => {
    let filtered = trails

    // Filter by strength
    if (filterStrength !== 'all') {
      filtered = filtered.filter((trail: any) => {
        const strength = trail.strength || trail.confidence || 0.5
        if (filterStrength === 'high') return strength >= 0.8
        if (filterStrength === 'medium') return strength >= 0.5 && strength < 0.8
        if (filterStrength === 'low') return strength < 0.5
        return true
      })
    }

    // Sort
    filtered = [...filtered].sort((a: any, b: any) => {
      if (sortBy === 'strength') {
        const aStrength = a.strength || a.confidence || 0.5
        const bStrength = b.strength || b.confidence || 0.5
        return bStrength - aStrength
      }
      if (sortBy === 'timestamp') {
        const aTime = new Date(a.created_at || a.timestamp || 0).getTime()
        const bTime = new Date(b.created_at || b.timestamp || 0).getTime()
        return bTime - aTime
      }
      // relevance (default) - keep original order
      return 0
    })

    return filtered
  }, [trails, filterStrength, sortBy])

  const trailGraph = useMemo(() => {
    if (filteredAndSortedTrails.length === 0) return null

    // Build graph structure from evidence trails
    const nodes = new Map<string, any>()
    const edges: Array<{ from: string; to: string; strength: number; type: string }> = []

    filteredAndSortedTrails.forEach((trail: any, index: number) => {
      const nodeId = trail.atom_id || trail.id || `node-${index}`
      const strength = trail.strength || trail.confidence || 0.5
      
      nodes.set(nodeId, {
        id: nodeId,
        label: trail.content?.substring(0, 50) || trail.summary?.substring(0, 50) || 'Evidence',
        type: trail.modality || 'evidence',
        strength,
        timestamp: trail.created_at || trail.timestamp,
        tags: trail.tags || []
      })

      // Create edges based on relationships
      if (trail.related_atoms && Array.isArray(trail.related_atoms)) {
        trail.related_atoms.forEach((relatedId: string) => {
          if (nodes.has(relatedId)) {
            edges.push({
              from: nodeId,
              to: relatedId,
              strength: 0.5,
              type: 'related'
            })
          }
        })
      }
    })

    return { nodes: Array.from(nodes.values()), edges }
  }, [filteredAndSortedTrails])

  if (loading) {
    return (
      <div className={`flex items-center justify-center h-full ${className}`}>
        <Activity className="w-6 h-6 text-gray-400 animate-pulse" />
        <span className="ml-2 text-gray-400">Loading evidence trails...</span>
      </div>
    )
  }

  return (
    <div className={`flex flex-col h-full bg-gray-900 ${className}`}>
      <div className="p-4 border-b border-gray-700">
        <h3 className="text-lg font-semibold text-gray-300 flex items-center gap-2">
          <Network className="w-5 h-5 text-purple-400" />
          Evidence Trail Visualization
        </h3>
        <p className="text-sm text-gray-400 mt-1">
          {filteredAndSortedTrails.length} of {trails.length} evidence item(s)
        </p>
      </div>

      {/* Filters */}
      <div className="p-3 border-b border-gray-700 flex gap-2">
        <select
          value={filterStrength}
          onChange={(e) => setFilterStrength(e.target.value as any)}
          className="px-3 py-1 text-xs rounded bg-gray-700 text-gray-300 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="all">All Strengths</option>
          <option value="high">High (≥80%)</option>
          <option value="medium">Medium (50-80%)</option>
          <option value="low">Low (&lt;50%)</option>
        </select>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as any)}
          className="px-3 py-1 text-xs rounded bg-gray-700 text-gray-300 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="relevance">Sort by Relevance</option>
          <option value="strength">Sort by Strength</option>
          <option value="timestamp">Sort by Time</option>
        </select>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {trailGraph ? (
          <div className="space-y-4">
            {/* Node List */}
            <div className="space-y-2">
              {trailGraph.nodes.map((node: any) => {
                const strength = node.strength || 0.5
                const strengthColor = strength >= 0.8 ? 'text-green-400' :
                                     strength >= 0.5 ? 'text-yellow-400' :
                                     'text-red-400'
                
                return (
                  <div
                    key={node.id}
                    onClick={() => setSelectedTrail(node)}
                    className={`p-3 bg-gray-800 border rounded cursor-pointer transition-all ${
                      selectedTrail?.id === node.id
                        ? 'border-purple-500 bg-purple-500/10'
                        : 'border-gray-700 hover:bg-gray-750'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <Database className="w-4 h-4 text-purple-400" />
                      <span className="text-sm font-medium text-gray-300 flex-1">{node.label}</span>
                      <span className={`text-xs font-bold ${strengthColor}`}>
                        {(strength * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="text-xs text-gray-400 mb-1">ID: {node.id}</div>
                    {node.timestamp && (
                      <div className="text-xs text-gray-500">
                        {new Date(node.timestamp).toLocaleDateString()}
                      </div>
                    )}
                    {node.tags && node.tags.length > 0 && (
                      <div className="flex gap-1 mt-2">
                        {node.tags.slice(0, 3).map((tag: string) => (
                          <span key={tag} className="text-xs px-1 py-0.5 bg-gray-700 rounded text-gray-400">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>

            {/* Edge Connections */}
            {trailGraph.edges.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-700">
                <h4 className="text-sm font-medium text-gray-300 mb-2">
                  Connections ({trailGraph.edges.length})
                </h4>
                <div className="space-y-1 max-h-32 overflow-y-auto">
                  {trailGraph.edges.map((edge, index) => {
                    const sourceNode = trailGraph.nodes.find((n: any) => n.id === edge.from)
                    const targetNode = trailGraph.nodes.find((n: any) => n.id === edge.to)
                    return (
                      <div key={index} className="text-xs text-gray-400 flex items-center gap-2">
                        <span className="text-purple-400">{sourceNode?.label.substring(0, 20)}...</span>
                        <ArrowRight className="w-3 h-3" />
                        <span className="text-purple-400">{targetNode?.label.substring(0, 20)}...</span>
                        <span className="text-gray-500">({(edge.strength * 100).toFixed(0)}%)</span>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center text-gray-400 py-8">
            {query ? 'No evidence trails found' : 'Enter a query to search evidence trails'}
          </div>
        )}
      </div>

      {/* Selected Trail Details */}
      {selectedTrail && (
        <div className="border-t border-gray-700 p-4 bg-gray-800 max-h-48 overflow-auto">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-semibold text-gray-300">Evidence Details</h4>
            <button
              onClick={() => setSelectedTrail(null)}
              className="text-gray-400 hover:text-gray-200"
            >
              ×
            </button>
          </div>
          <div className="text-xs text-gray-400 space-y-1">
            <div>ID: {selectedTrail.id}</div>
            <div>Strength: {(selectedTrail.strength * 100).toFixed(0)}%</div>
            {selectedTrail.timestamp && (
              <div>Timestamp: {new Date(selectedTrail.timestamp).toLocaleString()}</div>
            )}
            <div className="mt-2">
              <div className="font-medium text-gray-300 mb-1">Content:</div>
              <div className="text-gray-400">{selectedTrail.label}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * Goal Progress Visualization
 */
interface GoalProgressVisualizationProps {
  className?: string
}

export function GoalProgressVisualization({ className = '' }: GoalProgressVisualizationProps) {
  const { goals, loading, error } = useGoals('in_progress', 20)

  const goalsData = useMemo(() => {
    if (!goals || goals.length === 0) return []
    
    return goals.map((goal: any) => ({
      id: goal.goal_id || goal.id,
      name: goal.name || goal.description || 'Unknown Goal',
      progress: goal.progress || 0,
      status: goal.status || 'in_progress',
      priority: goal.priority || 'medium'
    })).sort((a, b) => {
      const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 }
      return (priorityOrder[a.priority as keyof typeof priorityOrder] || 2) - 
             (priorityOrder[b.priority as keyof typeof priorityOrder] || 2)
    })
  }, [goals])

  if (loading) {
    return (
      <div className={`flex items-center justify-center h-full ${className}`}>
        <Activity className="w-6 h-6 text-gray-400 animate-pulse" />
        <span className="ml-2 text-gray-400">Loading goals...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className={`flex items-center justify-center h-full text-red-400 ${className}`}>
        <span>Failed to load goals</span>
      </div>
    )
  }

  return (
    <div className={`flex flex-col h-full bg-gray-900 ${className}`}>
      <div className="p-4 border-b border-gray-700">
        <h3 className="text-lg font-semibold text-gray-300 flex items-center gap-2">
          <Target className="w-5 h-5 text-green-400" />
          Goal Progress Visualization
        </h3>
        <p className="text-sm text-gray-400 mt-1">{goalsData.length} active goal(s)</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {goalsData.map((goal) => (
          <div
            key={goal.id}
            className="bg-gray-800 border border-gray-700 rounded-lg p-4 hover:bg-gray-750 transition-colors"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-300">{goal.name}</span>
              <span className={`text-xs px-2 py-1 rounded ${
                goal.priority === 'critical' ? 'bg-red-900/20 text-red-400' :
                goal.priority === 'high' ? 'bg-orange-900/20 text-orange-400' :
                goal.priority === 'medium' ? 'bg-yellow-900/20 text-yellow-400' :
                'bg-blue-900/20 text-blue-400'
              }`}>
                {goal.priority}
              </span>
            </div>
            
            <div className="mb-2">
              <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                <span>Progress</span>
                <span>{(goal.progress * 100).toFixed(0)}%</span>
              </div>
              <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={`h-full ${
                    goal.progress >= 0.8 ? 'bg-green-500' :
                    goal.progress >= 0.5 ? 'bg-yellow-500' :
                    'bg-red-500'
                  } transition-all`}
                  style={{ width: `${goal.progress * 100}%` }}
                />
              </div>
            </div>

            <div className="text-xs text-gray-400">
              Status: <span className="text-gray-300">{goal.status}</span>
            </div>
          </div>
        ))}

        {goalsData.length === 0 && (
          <div className="text-center text-gray-400 py-8">
            No active goals
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * Performance Metrics Visualization
 */
interface PerformanceMetricsVisualizationProps {
  className?: string
}

export function PerformanceMetricsVisualization({ className = '' }: PerformanceMetricsVisualizationProps) {
  const { snapshot } = usePerformanceMonitoring()
  const { health, confidence } = useConsciousness()

  const metrics = useMemo(() => {
    if (!snapshot) return null

    return {
      renderTime: snapshot.summary.renderTime,
      memoryUsage: snapshot.summary.memoryUsage,
      networkRequests: snapshot.summary.networkRequests,
      consciousnessHealth: health,
      confidence: confidence * 100
    }
  }, [snapshot, health, confidence])

  if (!metrics) {
    return (
      <div className={`flex items-center justify-center h-full ${className}`}>
        <Activity className="w-6 h-6 text-gray-400 animate-pulse" />
        <span className="ml-2 text-gray-400">Collecting performance metrics...</span>
      </div>
    )
  }

  return (
    <div className={`flex flex-col h-full bg-gray-900 ${className}`}>
      <div className="p-4 border-b border-gray-700">
        <h3 className="text-lg font-semibold text-gray-300 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-blue-400" />
          Performance Metrics
        </h3>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Render Time */}
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-300">Render Time</span>
            <span className={`text-sm font-bold ${
              metrics.renderTime > 33.33 ? 'text-red-400' :
              metrics.renderTime > 16.67 ? 'text-yellow-400' :
              'text-green-400'
            }`}>
              {metrics.renderTime.toFixed(2)}ms
            </span>
          </div>
          <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className={`h-full ${
                metrics.renderTime > 33.33 ? 'bg-red-500' :
                metrics.renderTime > 16.67 ? 'bg-yellow-500' :
                'bg-green-500'
              }`}
              style={{ width: `${Math.min((metrics.renderTime / 33.33) * 100, 100)}%` }}
            />
          </div>
          <div className="text-xs text-gray-400 mt-1">
            Target: &lt;16.67ms (60fps)
          </div>
        </div>

        {/* Memory Usage */}
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-300">Memory Usage</span>
            <span className={`text-sm font-bold ${
              metrics.memoryUsage > 500 ? 'text-red-400' :
              metrics.memoryUsage > 300 ? 'text-yellow-400' :
              'text-green-400'
            }`}>
              {metrics.memoryUsage.toFixed(2)}MB
            </span>
          </div>
          <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className={`h-full ${
                metrics.memoryUsage > 500 ? 'bg-red-500' :
                metrics.memoryUsage > 300 ? 'bg-yellow-500' :
                'bg-green-500'
              }`}
              style={{ width: `${Math.min((metrics.memoryUsage / 1000) * 100, 100)}%` }}
            />
          </div>
        </div>

        {/* Network Requests */}
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-300">Network Requests</span>
            <span className="text-sm font-bold text-blue-400">
              {metrics.networkRequests}
            </span>
          </div>
        </div>

        {/* Consciousness Health */}
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-300">Consciousness Health</span>
            <span className={`text-sm font-bold ${
              metrics.consciousnessHealth >= 85 ? 'text-green-400' :
              metrics.consciousnessHealth >= 70 ? 'text-yellow-400' :
              'text-red-400'
            }`}>
              {metrics.consciousnessHealth.toFixed(0)}%
            </span>
          </div>
          <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className={`h-full ${
                metrics.consciousnessHealth >= 85 ? 'bg-green-500' :
                metrics.consciousnessHealth >= 70 ? 'bg-yellow-500' :
                'bg-red-500'
              }`}
              style={{ width: `${metrics.consciousnessHealth}%` }}
            />
          </div>
        </div>

        {/* Confidence */}
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-300">Confidence Level</span>
            <span className={`text-sm font-bold ${
              metrics.confidence >= 80 ? 'text-green-400' :
              metrics.confidence >= 60 ? 'text-yellow-400' :
              'text-red-400'
            }`}>
              {metrics.confidence.toFixed(0)}%
            </span>
          </div>
          <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className={`h-full ${
                metrics.confidence >= 80 ? 'bg-green-500' :
                metrics.confidence >= 60 ? 'bg-yellow-500' :
                'bg-red-500'
              }`}
              style={{ width: `${metrics.confidence}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

