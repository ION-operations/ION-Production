import React, { useRef, useEffect, useState } from 'react'
import { GitBranch, ArrowRight, AlertTriangle, CheckCircle, XCircle, Zap } from 'lucide-react'

interface GraphNode {
  id: string
  name: string
  kind: string
  status: string
  security_level?: string
  x?: number
  y?: number
}

interface GraphEdge {
  from: string
  to: string
  type: string
  status: string
}

interface LucidGraphVisualizationProps {
  centerNode: GraphNode
  incoming: GraphNode[]
  outgoing: GraphNode[]
  onNodeClick?: (nodeId: string) => void
  width?: number
  height?: number
}

export const LucidGraphVisualization: React.FC<LucidGraphVisualizationProps> = ({
  centerNode,
  incoming,
  outgoing,
  onNodeClick,
  width = 400,
  height = 300
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [hoveredNode, setHoveredNode] = useState<string | null>(null)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  // Calculate node positions
  const calculatePositions = () => {
    const centerX = width / 2
    const centerY = height / 2
    const radius = Math.min(width, height) * 0.3

    const nodes: GraphNode[] = [
      { ...centerNode, x: centerX, y: centerY },
      ...incoming.map((node, index) => ({
        ...node,
        x: centerX - radius * Math.cos((index * Math.PI * 2) / incoming.length),
        y: centerY - radius * Math.sin((index * Math.PI * 2) / incoming.length)
      })),
      ...outgoing.map((node, index) => ({
        ...node,
        x: centerX + radius * Math.cos((index * Math.PI * 2) / outgoing.length),
        y: centerY + radius * Math.sin((index * Math.PI * 2) / outgoing.length)
      }))
    ]

    return nodes
  }

  const getNodeColor = (node: GraphNode) => {
    if (node.id === centerNode.id) return '#3B82F6' // Blue for center
    if (node.status === 'clean') return '#10B981' // Green
    if (node.status === 'drift') return '#F59E0B' // Yellow
    if (node.status === 'violation') return '#EF4444' // Red
    return '#6B7280' // Gray
  }

  const getNodeIcon = (node: GraphNode) => {
    if (node.status === 'clean') return CheckCircle
    if (node.status === 'drift') return AlertTriangle
    if (node.status === 'violation') return XCircle
    return Zap
  }

  const getEdgeColor = (edge: GraphEdge) => {
    if (edge.status === 'clean') return '#10B981'
    if (edge.status === 'drift') return '#F59E0B'
    if (edge.status === 'violation') return '#EF4444'
    return '#6B7280'
  }

  const drawGraph = () => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Clear canvas
    ctx.clearRect(0, 0, width, height)

    const nodes = calculatePositions()

    // Draw edges
    nodes.forEach(node => {
      if (node.id !== centerNode.id) {
        const centerNodePos = nodes.find(n => n.id === centerNode.id)
        if (centerNodePos) {
          ctx.beginPath()
          ctx.moveTo(centerNodePos.x!, centerNodePos.y!)
          ctx.lineTo(node.x!, node.y!)
          ctx.strokeStyle = '#374151'
          ctx.lineWidth = 2
          ctx.stroke()

          // Draw arrow
          const angle = Math.atan2(node.y! - centerNodePos.y!, node.x! - centerNodePos.x!)
          const arrowLength = 10
          const arrowX = node.x! - arrowLength * Math.cos(angle)
          const arrowY = node.y! - arrowLength * Math.sin(angle)

          ctx.beginPath()
          ctx.moveTo(arrowX, arrowY)
          ctx.lineTo(arrowX - arrowLength * Math.cos(angle - Math.PI / 6), arrowY - arrowLength * Math.sin(angle - Math.PI / 6))
          ctx.moveTo(arrowX, arrowY)
          ctx.lineTo(arrowX - arrowLength * Math.cos(angle + Math.PI / 6), arrowY - arrowLength * Math.sin(angle + Math.PI / 6))
          ctx.strokeStyle = '#374151'
          ctx.lineWidth = 2
          ctx.stroke()
        }
      }
    })

    // Draw nodes
    nodes.forEach(node => {
      const isHovered = hoveredNode === node.id
      const isSelected = selectedNode === node.id
      const isCenter = node.id === centerNode.id

      // Node circle
      ctx.beginPath()
      ctx.arc(node.x!, node.y!, isCenter ? 20 : 15, 0, 2 * Math.PI)
      ctx.fillStyle = getNodeColor(node)
      ctx.fill()

      if (isHovered || isSelected) {
        ctx.strokeStyle = '#FBBF24'
        ctx.lineWidth = 3
        ctx.stroke()
      }

      // Node icon
      const Icon = getNodeIcon(node)
      // Note: In a real implementation, you'd draw the icon using canvas methods
      // For now, we'll use a simple circle indicator
      ctx.beginPath()
      ctx.arc(node.x!, node.y!, 5, 0, 2 * Math.PI)
      ctx.fillStyle = '#FFFFFF'
      ctx.fill()

      // Node label
      ctx.fillStyle = '#FFFFFF'
      ctx.font = '12px Arial'
      ctx.textAlign = 'center'
      ctx.fillText(node.name, node.x!, node.y! + 30)
    })
  }

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    const nodes = calculatePositions()
    const clickedNode = nodes.find(node => {
      const distance = Math.sqrt((x - node.x!) ** 2 + (y - node.y!) ** 2)
      return distance <= 20
    })

    if (clickedNode) {
      setSelectedNode(clickedNode.id)
      if (onNodeClick) {
        onNodeClick(clickedNode.id)
      }
    }
  }

  const handleCanvasMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    const nodes = calculatePositions()
    const hovered = nodes.find(node => {
      const distance = Math.sqrt((x - node.x!) ** 2 + (y - node.y!) ** 2)
      return distance <= 20
    })

    setHoveredNode(hovered?.id || null)
  }

  useEffect(() => {
    drawGraph()
  }, [centerNode, incoming, outgoing, hoveredNode, selectedNode])

  return (
    <div className="relative">
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="border border-gray-700 rounded cursor-pointer"
        onClick={handleCanvasClick}
        onMouseMove={handleCanvasMouseMove}
      />
      
      {/* Legend */}
      <div className="absolute top-2 right-2 bg-gray-800 rounded p-2 text-xs">
        <div className="flex items-center gap-2 mb-1">
          <div className="w-3 h-3 bg-blue-500 rounded-full" />
          <span className="text-gray-300">Center</span>
        </div>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-3 h-3 bg-green-500 rounded-full" />
          <span className="text-gray-300">Clean</span>
        </div>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-3 h-3 bg-yellow-500 rounded-full" />
          <span className="text-gray-300">Drift</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-red-500 rounded-full" />
          <span className="text-gray-300">Violation</span>
        </div>
      </div>

      {/* Node Details */}
      {hoveredNode && (
        <div className="absolute bottom-2 left-2 bg-gray-800 rounded p-2 text-xs max-w-48">
          {(() => {
            const nodes = calculatePositions()
            const node = nodes.find(n => n.id === hoveredNode)
            if (!node) return null

            return (
              <div>
                <div className="font-semibold text-white">{node.name}</div>
                <div className="text-gray-400">{node.kind}</div>
                <div className={`capitalize ${
                  node.status === 'clean' ? 'text-green-400' :
                  node.status === 'drift' ? 'text-yellow-400' :
                  'text-red-400'
                }`}>
                  {node.status}
                </div>
                {node.security_level && (
                  <div className="text-yellow-400">
                    Security: {node.security_level}
                  </div>
                )}
              </div>
            )
          })()}
        </div>
      )}
    </div>
  )
}
