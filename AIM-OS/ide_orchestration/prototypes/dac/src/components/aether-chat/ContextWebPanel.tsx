/**
 * Context Web Panel Component
 * Interactive visualization of Context Web graph
 * 
 * Phase 2 Week 7-8: Context Web Visualization
 */

import React, { useState, useCallback, useMemo, useEffect } from 'react'
import { Network, Search, Clock, Link2, X, Maximize2, Minimize2, GitBranch, Users, TrendingUp, Filter } from 'lucide-react'
import type { ContextWeb, ContextNode, ContextEdge, ContextWebPanelData } from '../../types/aetherChatTypes'

export interface ContextWebPanelProps {
  contextWeb: ContextWeb
  panelData?: ContextWebPanelData
  onNodeClick?: (node: ContextNode) => void
  onEdgeClick?: (edge: ContextEdge) => void
  onSearch?: (query: string) => Promise<ContextNode[]>
  className?: string
  isExpanded?: boolean
  onToggleExpand?: () => void
}

/**
 * Context Web Panel Component
 * Displays interactive graph visualization of context relationships
 */
export const ContextWebPanel: React.FC<ContextWebPanelProps> = ({
  contextWeb,
  panelData,
  onNodeClick,
  onEdgeClick,
  onSearch,
  className = '',
  isExpanded = false,
  onToggleExpand
}) => {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedNode, setSelectedNode] = useState<ContextNode | null>(null)
  const [highlightedNodes, setHighlightedNodes] = useState<Set<string>>(new Set())
  const [highlightedEdges, setHighlightedEdges] = useState<Set<string>>(new Set())
  const [ForceGraph2D, setForceGraph2D] = useState<any>(null)
  const [viewMode, setViewMode] = useState<'graph' | 'timeline' | 'causation' | 'commonality'>('graph')
  const [causationNodeId, setCausationNodeId] = useState<string | null>(null)
  const [commonalityNodeIds, setCommonalityNodeIds] = useState<Set<string>>(new Set())
  const [timelineTopicId, setTimelineTopicId] = useState<string | null>(null)

  // Lazy load ForceGraph2D to avoid module loading issues
  useEffect(() => {
    import('react-force-graph-2d').then((module) => {
      setForceGraph2D(() => module.default)
    }).catch((err) => {
      console.error('Failed to load ForceGraph2D:', err)
    })
  }, [])

  // Prepare graph data for react-force-graph
  const graphData = useMemo(() => {
    return {
      nodes: contextWeb.nodes.map(node => ({
        id: node.id,
        label: node.label,
        type: node.type,
        importance: node.importance,
        recency: node.recency,
        relevance: node.relevance || 0,
        size: node.size || (node.importance * 10),
        color: node.color || getDefaultColor(node.type),
        glow: node.glow || 0,
        context: node.context
      })),
      links: contextWeb.edges.map(edge => ({
        id: `${edge.from}-${edge.to}`,
        source: edge.from,
        target: edge.to,
        relation: edge.relation,
        strength: edge.strength,
        thickness: edge.thickness || (edge.strength * 3),
        color: edge.color || getDefaultEdgeColor(edge.relation)
      }))
    }
  }, [contextWeb])

  // Handle node click
  const handleNodeClick = useCallback((node: any) => {
    const contextNode = contextWeb.nodes.find(n => n.id === node.id)
    if (contextNode) {
      setSelectedNode(contextNode)
      if (onNodeClick) {
        onNodeClick(contextNode)
      }
      
      // Toggle commonality selection (Ctrl/Cmd + Click)
      // For now, just add to commonality set if in commonality mode
      if (viewMode === 'commonality') {
        setCommonalityNodeIds(prev => {
          const next = new Set(prev)
          if (next.has(node.id)) {
            next.delete(node.id)
          } else {
            next.add(node.id)
          }
          return next
        })
      }
      
      // Highlight connected nodes
      const connectedNodeIds = new Set<string>([node.id])
      contextWeb.edges.forEach(edge => {
        if (edge.from === node.id) connectedNodeIds.add(edge.to)
        if (edge.to === node.id) connectedNodeIds.add(edge.from)
      })
      setHighlightedNodes(connectedNodeIds)
      
      // Highlight connected edges
      const connectedEdgeIds = new Set<string>()
      contextWeb.edges.forEach(edge => {
        if (edge.from === node.id || edge.to === node.id) {
          connectedEdgeIds.add(`${edge.from}-${edge.to}`)
        }
      })
      setHighlightedEdges(connectedEdgeIds)
    }
  }, [contextWeb, onNodeClick, viewMode])

  // Handle edge click
  const handleLinkClick = useCallback((link: any) => {
    const contextEdge = contextWeb.edges.find(
      e => e.from === link.source.id && e.to === link.target.id
    )
    if (contextEdge && onEdgeClick) {
      onEdgeClick(contextEdge)
    }
  }, [contextWeb, onEdgeClick])

  // Handle search
  const handleSearch = useCallback(async (query: string) => {
    setSearchQuery(query)
    if (!query.trim()) {
      setHighlightedNodes(new Set())
      return
    }

    if (onSearch) {
      const results = await onSearch(query)
      setHighlightedNodes(new Set(results.map(n => n.id)))
    } else {
      // Fallback: simple text search
      const matching = contextWeb.nodes.filter(node =>
        node.label.toLowerCase().includes(query.toLowerCase()) ||
        node.context?.toLowerCase().includes(query.toLowerCase())
      )
      setHighlightedNodes(new Set(matching.map(n => n.id)))
    }
  }, [contextWeb, onSearch])

  // Node color based on highlight state
  const getNodeColor = useCallback((node: any) => {
    if (highlightedNodes.has(node.id)) {
      return '#fbbf24' // Highlighted: yellow
    }
    if (selectedNode?.id === node.id) {
      return '#3b82f6' // Selected: blue
    }
    return node.color || getDefaultColor(node.type)
  }, [highlightedNodes, selectedNode])

  // Edge color based on highlight state
  const getLinkColor = useCallback((link: any) => {
    const linkId = `${link.source.id}-${link.target.id}`
    if (highlightedEdges.has(linkId)) {
      return '#fbbf24' // Highlighted: yellow
    }
    return link.color || '#6366f1'
  }, [highlightedEdges])

  if (contextWeb.nodes.length === 0) {
    return (
      <div className={`bg-gray-900/50 border border-gray-700 rounded-lg p-4 ${className}`}>
        <div className="flex items-center gap-2 text-gray-400">
          <Network className="w-5 h-5" />
          <span className="text-sm">No context available</span>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-gray-900/50 border border-gray-700 rounded-lg overflow-hidden ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <Network className="w-5 h-5 text-blue-400" />
          <h3 className="text-sm font-semibold text-gray-200">
            Context Web ({contextWeb.nodes.length} nodes, {contextWeb.edges.length} edges)
          </h3>
        </div>
        <div className="flex items-center gap-2">
          {/* View Mode Toggle */}
          <div className="flex items-center gap-1 bg-gray-800 rounded p-1">
            <button
              onClick={() => setViewMode('graph')}
              className={`px-2 py-1 rounded text-xs transition-colors ${
                viewMode === 'graph' 
                  ? 'bg-blue-500 text-white' 
                  : 'text-gray-400 hover:text-gray-200'
              }`}
              title="Graph View"
            >
              <Network className="w-3 h-3" />
            </button>
            <button
              onClick={() => {
                if (selectedNode) {
                  handleTimelineView(selectedNode.id)
                } else {
                  setViewMode('timeline')
                }
              }}
              className={`px-2 py-1 rounded text-xs transition-colors ${
                viewMode === 'timeline' 
                  ? 'bg-blue-500 text-white' 
                  : 'text-gray-400 hover:text-gray-200'
              }`}
              title="Timeline View"
              disabled={!selectedNode}
            >
              <TrendingUp className="w-3 h-3" />
            </button>
            <button
              onClick={() => {
                if (selectedNode) {
                  handleCausationChain(selectedNode.id)
                } else {
                  setViewMode('causation')
                }
              }}
              className={`px-2 py-1 rounded text-xs transition-colors ${
                viewMode === 'causation' 
                  ? 'bg-blue-500 text-white' 
                  : 'text-gray-400 hover:text-gray-200'
              }`}
              title="Causation Chain"
              disabled={!selectedNode}
            >
              <GitBranch className="w-3 h-3" />
            </button>
            <button
              onClick={() => {
                if (commonalityNodeIds.size >= 2) {
                  handleFindCommonality(Array.from(commonalityNodeIds))
                } else {
                  setViewMode('commonality')
                }
              }}
              className={`px-2 py-1 rounded text-xs transition-colors ${
                viewMode === 'commonality' 
                  ? 'bg-blue-500 text-white' 
                  : 'text-gray-400 hover:text-gray-200'
              }`}
              title="Find Commonality"
              disabled={commonalityNodeIds.size < 2}
            >
              <Users className="w-3 h-3" />
            </button>
          </div>
          {onToggleExpand && (
            <button
              onClick={onToggleExpand}
              className="p-1.5 rounded hover:bg-gray-700 transition-colors"
              title={isExpanded ? 'Minimize' : 'Maximize'}
            >
              {isExpanded ? (
                <Minimize2 className="w-4 h-4 text-gray-400" />
              ) : (
                <Maximize2 className="w-4 h-4 text-gray-400" />
              )}
            </button>
          )}
        </div>
      </div>

      {/* Search Bar */}
      {onSearch && (
        <div className="p-3 border-b border-gray-700">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search context..."
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-blue-500"
            />
          </div>
        </div>
      )}

      {/* Graph Visualization */}
      <div className={`relative ${isExpanded ? 'h-[600px]' : 'h-[400px]'}`}>
        {!ForceGraph2D ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <Network className="w-8 h-8 text-gray-500 mx-auto mb-2 animate-pulse" />
              <p className="text-sm text-gray-400">Loading graph visualization...</p>
            </div>
          </div>
        ) : (
          <ForceGraph2D
          graphData={graphData}
          nodeLabel={(node: any) => `
            <div style="background: rgba(0,0,0,0.8); padding: 8px; border-radius: 4px; max-width: 200px;">
              <div style="font-weight: bold; color: ${node.color || '#fff'}; margin-bottom: 4px;">
                ${node.label}
              </div>
              <div style="font-size: 11px; color: #9ca3af;">
                Type: ${node.type}<br/>
                Relevance: ${((node.relevance || 0) * 100).toFixed(0)}%<br/>
                ${node.context ? `Context: ${node.context.substring(0, 100)}...` : ''}
              </div>
            </div>
          `}
          nodeColor={getNodeColor}
          nodeVal={(node: any) => node.size || 5}
          linkLabel={(link: any) => link.relation || 'related'}
          linkColor={getLinkColor}
          linkWidth={(link: any) => link.thickness || 2}
          onNodeClick={handleNodeClick}
          onLinkClick={handleLinkClick}
          nodeCanvasObjectMode={() => 'after'}
          nodeCanvasObject={(node: any, ctx: CanvasRenderingContext2D) => {
            // Add glow effect for highlighted nodes
            if (highlightedNodes.has(node.id) || selectedNode?.id === node.id) {
              ctx.shadowBlur = 15
              ctx.shadowColor = getNodeColor(node)
            }
          }}
          cooldownTicks={100}
          onEngineStop={() => {
            // Graph layout stabilized
          }}
        />
        )}
      </div>

      {/* Node Details Panel */}
      {selectedNode && (
        <div className="p-3 border-t border-gray-700 bg-gray-800/50">
          <div className="flex items-start justify-between mb-2">
            <div>
              <h4 className="text-sm font-semibold text-gray-200">{selectedNode.label}</h4>
              <div className="flex items-center gap-2 mt-1">
                <span className={`text-xs px-2 py-0.5 rounded ${getTypeColorClass(selectedNode.type)}`}>
                  {selectedNode.type}
                </span>
                {selectedNode.relevance !== undefined && (
                  <span className="text-xs text-gray-400">
                    {(selectedNode.relevance * 100).toFixed(0)}% relevant
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="p-1 rounded hover:bg-gray-700 transition-colors"
            >
              <X className="w-4 h-4 text-gray-400" />
            </button>
          </div>
          {selectedNode.context && (
            <p className="text-xs text-gray-400 mt-2 line-clamp-3">
              {selectedNode.context}
            </p>
          )}
          {selectedNode.timestamp && (
            <div className="flex items-center gap-1 mt-2 text-xs text-gray-500">
              <Clock className="w-3 h-3" />
              <span>{new Date(selectedNode.timestamp).toLocaleString()}</span>
            </div>
          )}
          
          {/* Action Buttons (Phase 2 Week 8) */}
          <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-700">
            <button
              onClick={() => handleCausationChain(selectedNode.id)}
              className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded transition-colors"
            >
              <GitBranch className="w-3 h-3" />
              <span>Show Causation Chain</span>
            </button>
            <button
              onClick={() => handleTimelineView(selectedNode.id)}
              className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 rounded transition-colors"
            >
              <TrendingUp className="w-3 h-3" />
              <span>View Timeline</span>
            </button>
            <button
              onClick={() => {
                setCommonalityNodeIds(prev => {
                  const next = new Set(prev)
                  if (next.has(selectedNode.id)) {
                    next.delete(selectedNode.id)
                  } else {
                    next.add(selectedNode.id)
                  }
                  return next
                })
                if (commonalityNodeIds.size >= 1) {
                  setViewMode('commonality')
                }
              }}
              className={`flex items-center gap-1 px-2 py-1 text-xs rounded transition-colors ${
                commonalityNodeIds.has(selectedNode.id)
                  ? 'bg-blue-500 hover:bg-blue-600'
                  : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              <Users className="w-3 h-3" />
              <span>{commonalityNodeIds.has(selectedNode.id) ? 'Remove from' : 'Add to'} Commonality</span>
            </button>
          </div>
        </div>
      )}

      {/* View Mode Info (Phase 2 Week 8) */}
      {viewMode !== 'graph' && (
        <div className="p-3 border-t border-gray-700 bg-gray-800/30">
          {viewMode === 'causation' && causationNodeId && (
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <GitBranch className="w-3 h-3" />
              <span>Showing causation chain for: {contextWeb.nodes.find(n => n.id === causationNodeId)?.label}</span>
              <button
                onClick={() => {
                  setViewMode('graph')
                  setCausationNodeId(null)
                  setHighlightedNodes(new Set())
                }}
                className="ml-auto text-blue-400 hover:text-blue-300"
              >
                Reset
              </button>
            </div>
          )}
          {viewMode === 'timeline' && timelineTopicId && (
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <TrendingUp className="w-3 h-3" />
              <span>Showing timeline for: {contextWeb.nodes.find(n => n.id === timelineTopicId)?.label}</span>
              <button
                onClick={() => {
                  setViewMode('graph')
                  setTimelineTopicId(null)
                }}
                className="ml-auto text-blue-400 hover:text-blue-300"
              >
                Reset
              </button>
            </div>
          )}
          {viewMode === 'commonality' && commonalityNodeIds.size > 0 && (
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <Users className="w-3 h-3" />
              <span>Comparing {commonalityNodeIds.size} nodes for commonality</span>
              <button
                onClick={() => {
                  setViewMode('graph')
                  setCommonalityNodeIds(new Set())
                }}
                className="ml-auto text-blue-400 hover:text-blue-300"
              >
                Reset
              </button>
            </div>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="p-3 border-t border-gray-700 bg-gray-800/30">
        <div className="flex items-center gap-4 text-xs text-gray-400">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span>File</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span>Document</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-purple-500"></div>
            <span>Message</span>
          </div>
          <div className="flex items-center gap-1">
            <Link2 className="w-3 h-3" />
            <span>Relationship</span>
          </div>
        </div>
      </div>
    </div>
  )
}

/**
 * Get default color for node type
 */
function getDefaultColor(type: ContextNode['type']): string {
  switch (type) {
    case 'file':
      return '#3b82f6' // blue
    case 'doc':
      return '#10b981' // green
    case 'msg':
      return '#8b5cf6' // purple
    case 'mige':
      return '#f59e0b' // amber
    case 'event':
      return '#ef4444' // red
    default:
      return '#6b7280' // gray
  }
}

/**
 * Get default edge color for relation type
 */
function getDefaultEdgeColor(relation: ContextEdge['relation']): string {
  switch (relation) {
    case 'refers_to':
      return '#6366f1' // indigo
    case 'explains':
      return '#10b981' // green
    case 'extends':
      return '#3b82f6' // blue
    case 'contradicts':
      return '#ef4444' // red
    case 'depends_on':
      return '#f59e0b' // amber
    default:
      return '#6b7280' // gray
  }
}

/**
 * Get CSS class for type badge
 */
function getTypeColorClass(type: ContextNode['type']): string {
  switch (type) {
    case 'file':
      return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
    case 'doc':
      return 'bg-green-500/20 text-green-400 border-green-500/30'
    case 'msg':
      return 'bg-purple-500/20 text-purple-400 border-purple-500/30'
    case 'mige':
      return 'bg-amber-500/20 text-amber-400 border-amber-500/30'
    case 'event':
      return 'bg-red-500/20 text-red-400 border-red-500/30'
    default:
      return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
  }
}

