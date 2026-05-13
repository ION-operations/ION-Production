// Context Web Panel (CMC + HHNI Visualization) - Enhanced with Real AIM-OS Integration
import React, { useEffect, useState, useRef } from 'react'
import { Network, Search, Filter, ZoomIn, ZoomOut } from 'lucide-react'
import { useAIMOS } from '@/hooks/useAIMOS'
import { Panel } from '@/types'
import { BasePanel } from './BasePanel'
import { useLayoutStore } from '@/store/layoutStore'

interface ContextWebProps {
  panel: Panel
}

interface GraphNode {
  id: string
  label: string
  content: string
  confidence: number
  x?: number
  y?: number
  type: 'atom' | 'search_result'
}

interface GraphEdge {
  source: string
  target: string
  strength: number
}

export const ContextWeb: React.FC<ContextWebProps> = ({ panel }) => {
  const { togglePanelVisibility } = useLayoutStore()
  const { cmc, hhni, isLoading, error, isConnected } = useAIMOS()
  const [searchQuery, setSearchQuery] = useState('')
  const [layoutMode, setLayoutMode] = useState<'force' | 'hierarchical'>('force')
  const [zoom, setZoom] = useState(1)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [nodes, setNodes] = useState<GraphNode[]>([])
  const [edges, setEdges] = useState<GraphEdge[]>([])

  useEffect(() => {
    const handleTogglePanel = (e: CustomEvent) => {
      if (e.detail.panelId === panel.id) {
        togglePanelVisibility(panel.id)
      }
    }
    window.addEventListener('togglePanel', handleTogglePanel as EventListener)
    return () => {
      window.removeEventListener('togglePanel', handleTogglePanel as EventListener)
    }
  }, [panel.id, togglePanelVisibility])

  // Initialize graph from CMC atoms
  useEffect(() => {
    if (cmc.atoms.length > 0) {
      const graphNodes: GraphNode[] = cmc.atoms.slice(0, 20).map((atom, index) => ({
        id: atom.id,
        label: atom.id.substring(0, 20),
        content: atom.content,
        confidence: atom.confidence,
        x: Math.random() * 400 + 100,
        y: Math.random() * 300 + 100,
        type: 'atom',
      }))

      // Create edges based on semantic relationships (simulated)
      const graphEdges: GraphEdge[] = []
      for (let i = 0; i < graphNodes.length; i++) {
        for (let j = i + 1; j < Math.min(i + 3, graphNodes.length); j++) {
          graphEdges.push({
            source: graphNodes[i].id,
            target: graphNodes[j].id,
            strength: Math.random() * 0.5 + 0.3,
          })
        }
      }

      setNodes(graphNodes)
      setEdges(graphEdges)
    }
  }, [cmc.atoms])

  // Handle search
  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    try {
      const results = await hhni.search(searchQuery)
      const searchNodes: GraphNode[] = results.atomIds.slice(0, 5).map((atomId, index) => ({
        id: `search_${atomId}`,
        label: `Search: ${atomId.substring(0, 15)}`,
        content: '',
        confidence: results.relevance[index],
        x: Math.random() * 400 + 100,
        y: Math.random() * 300 + 100,
        type: 'search_result',
      }))

      setNodes((prev) => [...prev, ...searchNodes])
    } catch (err) {
      console.error('Search failed:', err)
    }
  }

  // Render graph on canvas
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    canvas.width = canvas.offsetWidth
    canvas.height = canvas.offsetHeight

    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.save()
    ctx.scale(zoom, zoom)

    // Draw edges
    ctx.strokeStyle = '#4B5563'
    ctx.lineWidth = 1
    edges.forEach((edge) => {
      const sourceNode = nodes.find((n) => n.id === edge.source)
      const targetNode = nodes.find((n) => n.id === edge.target)
      if (sourceNode && targetNode && sourceNode.x && sourceNode.y && targetNode.x && targetNode.y) {
        ctx.beginPath()
        ctx.moveTo(sourceNode.x, sourceNode.y)
        ctx.lineTo(targetNode.x, targetNode.y)
        ctx.stroke()
      }
    })

    // Draw nodes
    nodes.forEach((node) => {
      if (!node.x || !node.y) return

      const isSelected = selectedNode === node.id
      const color = node.type === 'search_result' ? '#3B82F6' : '#10B981'
      const size = isSelected ? 12 : 8

      ctx.fillStyle = isSelected ? '#F59E0B' : color
      ctx.beginPath()
      ctx.arc(node.x, node.y, size, 0, Math.PI * 2)
      ctx.fill()

      // Draw label
      ctx.fillStyle = '#F9FAFB'
      ctx.font = '10px sans-serif'
      ctx.fillText(node.label.substring(0, 15), node.x + size + 4, node.y)
    })

    ctx.restore()
  }, [nodes, edges, zoom, selectedNode])

  const headerActions = (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      {isConnected && (
        <span style={{ fontSize: '10px', color: '#10B981', backgroundColor: '#374151', padding: '2px 6px', borderRadius: '4px' }}>
          AIM-OS
        </span>
      )}
      <button
        onClick={() => setLayoutMode(layoutMode === 'force' ? 'hierarchical' : 'force')}
        style={{
          padding: '4px 8px',
          fontSize: '11px',
          backgroundColor: '#374151',
          border: '1px solid #4B5563',
          borderRadius: '4px',
          color: '#F9FAFB',
          cursor: 'pointer',
        }}
        title="Toggle layout"
      >
        <Network size={12} />
      </button>
    </div>
  )

  const stats = cmc.getStats()

  return (
    <BasePanel panel={panel} headerActions={headerActions} isLoading={isLoading} error={error || null}>
      {/* Statistics */}
      <div style={{ marginBottom: '16px', padding: '12px', backgroundColor: '#111827', borderRadius: '4px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
          <div>
            <span style={{ color: '#9CA3AF' }}>Atoms: </span>
            <span style={{ color: '#F9FAFB', fontWeight: 'bold' }}>{stats.totalAtoms}</span>
          </div>
          <div>
            <span style={{ color: '#9CA3AF' }}>Nodes: </span>
            <span style={{ color: '#F9FAFB', fontWeight: 'bold' }}>{nodes.length}</span>
          </div>
          <div>
            <span style={{ color: '#9CA3AF' }}>Edges: </span>
            <span style={{ color: '#F9FAFB', fontWeight: 'bold' }}>{edges.length}</span>
          </div>
        </div>
      </div>

      {/* Search */}
      <div style={{ marginBottom: '16px', display: 'flex', gap: '8px' }}>
        <input
          type="text"
          placeholder="Search context web..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          style={{
            flex: 1,
            padding: '6px 12px',
            backgroundColor: '#111827',
            border: '1px solid #374151',
            borderRadius: '4px',
            color: '#F9FAFB',
            fontSize: '12px',
          }}
        />
        <button
          onClick={handleSearch}
          style={{
            padding: '6px 12px',
            backgroundColor: '#3B82F6',
            border: 'none',
            borderRadius: '4px',
            color: '#F9FAFB',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}
        >
          <Search size={14} />
        </button>
      </div>

      {/* Graph Visualization */}
      <div style={{ position: 'relative', flex: 1, minHeight: '400px', backgroundColor: '#111827', borderRadius: '4px', overflow: 'hidden' }}>
        <canvas
          ref={canvasRef}
          style={{ width: '100%', height: '100%', cursor: 'pointer' }}
          onClick={(e) => {
            const rect = canvasRef.current?.getBoundingClientRect()
            if (!rect) return
            const x = (e.clientX - rect.left) / zoom
            const y = (e.clientY - rect.top) / zoom

            // Find clicked node
            const clickedNode = nodes.find((node) => {
              if (!node.x || !node.y) return false
              const distance = Math.sqrt(Math.pow(node.x - x, 2) + Math.pow(node.y - y, 2))
              return distance < 15
            })

            setSelectedNode(clickedNode?.id || null)
          }}
        />
        {selectedNode && (
          <div
            style={{
              position: 'absolute',
              top: '12px',
              right: '12px',
              padding: '12px',
              backgroundColor: '#1F2937',
              border: '1px solid #374151',
              borderRadius: '4px',
              maxWidth: '300px',
              fontSize: '12px',
            }}
          >
            <div style={{ fontWeight: 'bold', marginBottom: '8px', color: '#F9FAFB' }}>
              {nodes.find((n) => n.id === selectedNode)?.label}
            </div>
            <div style={{ color: '#9CA3AF', fontSize: '11px', marginBottom: '4px' }}>
              {nodes.find((n) => n.id === selectedNode)?.content.substring(0, 100)}...
            </div>
            <div style={{ color: '#6B7280', fontSize: '10px' }}>
              Confidence: {(nodes.find((n) => n.id === selectedNode)?.confidence || 0) * 100}%
            </div>
          </div>
        )}

        {/* Zoom Controls */}
        <div style={{ position: 'absolute', bottom: '12px', right: '12px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <button
            onClick={() => setZoom(Math.min(zoom + 0.1, 2))}
            style={{
              padding: '4px',
              backgroundColor: '#374151',
              border: '1px solid #4B5563',
              borderRadius: '4px',
              color: '#F9FAFB',
              cursor: 'pointer',
            }}
          >
            <ZoomIn size={14} />
          </button>
          <button
            onClick={() => setZoom(Math.max(zoom - 0.1, 0.5))}
            style={{
              padding: '4px',
              backgroundColor: '#374151',
              border: '1px solid #4B5563',
              borderRadius: '4px',
              color: '#F9FAFB',
              cursor: 'pointer',
            }}
          >
            <ZoomOut size={14} />
          </button>
        </div>
      </div>
    </BasePanel>
  )
}

