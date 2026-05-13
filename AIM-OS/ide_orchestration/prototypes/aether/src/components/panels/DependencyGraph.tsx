// Dependency Graph Visualization
// Clear dependency visualization showing blocking relationships

import React, { useMemo, useRef, useEffect } from 'react'

interface EvolutionNode {
  id: string
  type: 'milestone' | 'north_star' | 'objective' | 'key_result' | 'error' | 'divergence' | 'new_goal'
  label: string
  description: string
  timestamp: string
  status?: 'completed' | 'in_progress' | 'planned' | 'paused' | 'error' | 'designed'
  completion?: number
  priority?: string
  parentId?: string
  children?: string[]
  origin?: string
  errorType?: 'repeated_error' | 'priority_change' | 'timeline_shift' | 'scope_change'
  divergenceReason?: string
}

interface DependencyGraphProps {
  nodes: EvolutionNode[]
  selectedNode: string | null
  onNodeSelect: (nodeId: string | null) => void
  getNodeColor: (node: EvolutionNode) => string
  getNodeIcon: (node: EvolutionNode) => React.ReactNode
}

export const DependencyGraph: React.FC<DependencyGraphProps> = ({
  nodes,
  selectedNode,
  onNodeSelect,
  getNodeColor,
  getNodeIcon
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const svgRef = useRef<SVGSVGElement>(null)

  // Build dependency structure
  const dependencyStructure = useMemo(() => {
    const nodeMap = new Map<string, EvolutionNode>()
    const rootNodes: EvolutionNode[] = []
    const blockingNodes: EvolutionNode[] = []

    nodes.forEach(node => {
      nodeMap.set(node.id, node)
      if (!node.parentId) {
        rootNodes.push(node)
      }
      if (node.status === 'paused' || node.status === 'error') {
        blockingNodes.push(node)
      }
    })

    // Calculate dependency depth
    const calculateDepth = (nodeId: string, visited = new Set<string>()): number => {
      if (visited.has(nodeId)) return 0
      visited.add(nodeId)
      const node = nodeMap.get(nodeId)
      if (!node || !node.parentId) return 0
      return 1 + calculateDepth(node.parentId, visited)
    }

    // Find critical path (longest dependency chain)
    const findCriticalPath = (): string[] => {
      let maxDepth = 0
      let criticalNode: EvolutionNode | null = null
      
      nodes.forEach(node => {
        const depth = calculateDepth(node.id)
        if (depth > maxDepth) {
          maxDepth = depth
          criticalNode = node
        }
      })

      const path: string[] = []
      let current: EvolutionNode | null = criticalNode
      while (current) {
        path.unshift(current.id)
        current = current.parentId ? nodeMap.get(current.parentId) || null : null
      }
      return path
    }

    const criticalPath = findCriticalPath()

    return { nodeMap, rootNodes, blockingNodes, criticalPath, calculateDepth }
  }, [nodes])

  // Calculate positions (hierarchical top-down)
  const nodePositions = useMemo(() => {
    const positions: Record<string, { x: number, y: number, depth: number }> = {}
    const NODE_WIDTH = 180
    const NODE_HEIGHT = 60
    const HORIZONTAL_SPACING = 220
    const VERTICAL_SPACING = 100

    const calculatePositions = (node: EvolutionNode, depth: number, x: number, startY: number): number => {
      const children = nodes.filter(n => n.parentId === node.id)
      
      if (children.length === 0) {
        positions[node.id] = { x, y: startY, depth }
        return startY + NODE_HEIGHT + VERTICAL_SPACING
      }

      let childX = x - ((children.length - 1) * HORIZONTAL_SPACING) / 2
      let maxY = startY

      children.forEach(child => {
        const childY = calculatePositions(child, depth + 1, childX, startY + NODE_HEIGHT + VERTICAL_SPACING)
        maxY = Math.max(maxY, childY)
        childX += HORIZONTAL_SPACING
      })

      const parentX = children.length > 0
        ? (Math.min(...children.map(c => positions[c.id]?.x || 0)) + 
           Math.max(...children.map(c => positions[c.id]?.x || 0))) / 2
        : x

      positions[node.id] = { x: parentX, y: startY, depth }
      return maxY
    }

    let currentY = 50
    dependencyStructure.rootNodes.forEach(root => {
      currentY = calculatePositions(root, 0, 400, currentY)
    })

    return positions
  }, [nodes, dependencyStructure])

  // Draw connections
  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return

    const svg = svgRef.current
    const container = containerRef.current
    svg.innerHTML = ''

    const maxX = Math.max(...Object.values(nodePositions).map(p => p.x), 1000)
    const maxY = Math.max(...Object.values(nodePositions).map(p => p.y), 2000)
    svg.setAttribute('width', maxX.toString())
    svg.setAttribute('height', maxY.toString())

    nodes.forEach(node => {
      if (!node.parentId) return

      const parentPos = nodePositions[node.parentId]
      const childPos = nodePositions[node.id]

      if (!parentPos || !childPos) return

      const isBlocking = dependencyStructure.blockingNodes.includes(node) || 
                         dependencyStructure.blockingNodes.some(b => b.id === node.parentId)
      const isCritical = dependencyStructure.criticalPath.includes(node.id)

      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
      const d = `M ${parentPos.x + 90} ${parentPos.y + 30}
                 L ${parentPos.x + 90} ${parentPos.y + 50}
                 L ${childPos.x + 90} ${parentPos.y + 50}
                 L ${childPos.x + 90} ${childPos.y}`
      path.setAttribute('d', d)
      path.setAttribute('stroke', isBlocking ? '#ef4444' : isCritical ? '#eab308' : '#6366f1')
      path.setAttribute('stroke-width', isBlocking || isCritical ? '2.5' : '1.5')
      path.setAttribute('fill', 'none')
      path.setAttribute('opacity', '0.6')
      svg.appendChild(path)
    })
  }, [nodes, nodePositions, dependencyStructure])

  return (
    <div ref={containerRef} className="relative w-full h-full overflow-auto bg-gray-900">
      <svg ref={svgRef} className="absolute top-0 left-0 pointer-events-none" style={{ zIndex: 1 }} />
      <div className="relative" style={{ zIndex: 2 }}>
        {nodes.map(node => {
          const pos = nodePositions[node.id]
          if (!pos) return null

          const isSelected = selectedNode === node.id
          const isBlocking = dependencyStructure.blockingNodes.includes(node)
          const isCritical = dependencyStructure.criticalPath.includes(node.id)

          return (
            <div
              key={node.id}
              onClick={() => onNodeSelect(isSelected ? null : node.id)}
              className={`absolute border rounded-lg p-2 cursor-pointer transition-all text-xs ${
                getNodeColor(node)
              } ${isSelected ? 'ring-2 ring-blue-400' : ''} ${isBlocking ? 'border-red-500 border-2' : ''} ${isCritical ? 'border-yellow-500 border-2' : ''}`}
              style={{
                left: `${pos.x}px`,
                top: `${pos.y}px`,
                width: '180px'
              }}
            >
              <div className="flex items-start gap-2">
                {getNodeIcon(node)}
                <div className="flex-1">
                  <div className="font-semibold">{node.label}</div>
                  {isBlocking && <div className="text-red-400 text-xs mt-1">BLOCKING</div>}
                  {isCritical && <div className="text-yellow-400 text-xs mt-1">CRITICAL PATH</div>}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

