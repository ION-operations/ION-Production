// Impact Map Visualization
// Size-based visualization showing visual prioritization

import React, { useMemo } from 'react'

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

interface ImpactMapProps {
  nodes: EvolutionNode[]
  selectedNode: string | null
  onNodeSelect: (nodeId: string | null) => void
  getNodeColor: (node: EvolutionNode) => string
  getNodeIcon: (node: EvolutionNode) => React.ReactNode
}

export const ImpactMap: React.FC<ImpactMapProps> = ({
  nodes,
  selectedNode,
  onNodeSelect,
  getNodeColor,
  getNodeIcon
}) => {
  const sizedNodes = useMemo(() => {
    return nodes.map(node => {
      let size = 40 // Default
      const priority = node.priority || ''
      
      if (priority.includes('S -')) {
        size = 80 + (node.completion || 0) * 0.3
      } else if (priority.includes('A -')) {
        size = 60 + (node.completion || 0) * 0.2
      } else if (priority.includes('B -')) {
        size = 40 + (node.completion || 0) * 0.1
      } else {
        // No priority, use completion or default
        size = 40 + (node.completion || 0) * 0.2
      }
      
      return { ...node, size: Math.max(30, Math.min(120, size)) }
    })
  }, [nodes])

  // Simple bubble layout (pack layout simulation)
  const positionedNodes = useMemo(() => {
    const width = 1200
    const height = 800
    const padding = 20
    
    const positions: Array<{ node: EvolutionNode & { size: number }, x: number, y: number }> = []
    const placed: Array<{ x: number, y: number, r: number }> = []
    
    sizedNodes.forEach((node) => {
      const r = node.size / 2
      let x = padding + r
      let y = padding + r
      let attempts = 0
      let placed = false
      
      while (!placed && attempts < 1000) {
        const collision = placed.some(p => {
          const dx = x - p.x
          const dy = y - p.y
          const distance = Math.sqrt(dx * dx + dy * dy)
          return distance < r + p.r + 10
        })
        
        if (!collision) {
          placed.push({ x, y, r })
          positions.push({ node, x, y })
          placed = true
        } else {
          x = padding + r + Math.random() * (width - 2 * padding - 2 * r)
          y = padding + r + Math.random() * (height - 2 * padding - 2 * r)
          attempts++
        }
      }
      
      if (!placed) {
        // Fallback: place at random
        x = padding + r + Math.random() * (width - 2 * padding - 2 * r)
        y = padding + r + Math.random() * (height - 2 * padding - 2 * r)
        positions.push({ node, x, y })
      }
    })
    
    return positions
  }, [sizedNodes])

  return (
    <div className="relative w-full h-full overflow-auto bg-gray-900">
      <svg width="1200" height="800" className="w-full h-full">
        {positionedNodes.map(({ node, x, y }) => {
          const isSelected = selectedNode === node.id
          const color = getNodeColor(node)
          let fillColor = '#6366f1'
          if (color.includes('blue')) fillColor = '#3b82f6'
          if (color.includes('green')) fillColor = '#10b981'
          if (color.includes('red')) fillColor = '#ef4444'
          if (color.includes('orange')) fillColor = '#f97316'
          if (color.includes('purple')) fillColor = '#8b5cf6'
          if (color.includes('yellow')) fillColor = '#eab308'
          
          return (
            <g
              key={node.id}
              onClick={() => onNodeSelect(isSelected ? null : node.id)}
              className="cursor-pointer"
            >
              <circle
                cx={x}
                cy={y}
                r={node.size / 2}
                fill={fillColor}
                fillOpacity={isSelected ? 0.8 : 0.5}
                stroke={isSelected ? '#fff' : '#374151'}
                strokeWidth={isSelected ? 3 : 1}
              />
              <text
                x={x}
                y={y}
                textAnchor="middle"
                dominantBaseline="middle"
                fill="#e5e7eb"
                fontSize="10px"
                fontWeight={isSelected ? 'bold' : 'normal'}
                pointerEvents="none"
              >
                {node.label.length > 15 ? node.label.substring(0, 12) + '...' : node.label}
              </text>
              {node.completion !== undefined && (
                <text
                  x={x}
                  y={y + node.size / 2 + 12}
                  textAnchor="middle"
                  fill="#9ca3af"
                  fontSize="8px"
                  pointerEvents="none"
                >
                  {node.completion}%
                </text>
              )}
            </g>
          )
        })}
      </svg>
    </div>
  )
}

