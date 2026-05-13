// Timeline Spiral Visualization
// Chronological spiral showing evolution cycles

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

interface TimelineSpiralProps {
  nodes: EvolutionNode[]
  selectedNode: string | null
  onNodeSelect: (nodeId: string | null) => void
  getNodeColor: (node: EvolutionNode) => string
  getNodeIcon: (node: EvolutionNode) => React.ReactNode
}

export const TimelineSpiral: React.FC<TimelineSpiralProps> = ({
  nodes,
  selectedNode,
  onNodeSelect,
  getNodeColor,
  getNodeIcon
}) => {
  const CENTER_X = 400
  const CENTER_Y = 400
  const BASE_RADIUS = 50
  const RADIUS_INCREMENT = 30
  const REVOLUTION_DAYS = 30 // Each revolution = 1 month

  // Calculate spiral positions
  const positionedNodes = useMemo(() => {
    const sortedNodes = [...nodes].sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    )

    const startDate = sortedNodes.length > 0 ? new Date(sortedNodes[0].timestamp) : new Date()

    return sortedNodes.map(node => {
      const nodeDate = new Date(node.timestamp)
      const daysSinceStart = Math.floor((nodeDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24))
      const revolution = Math.floor(daysSinceStart / REVOLUTION_DAYS)
      const dayInRevolution = daysSinceStart % REVOLUTION_DAYS
      const angle = (dayInRevolution / REVOLUTION_DAYS) * 2 * Math.PI
      const radius = BASE_RADIUS + revolution * RADIUS_INCREMENT

      return {
        ...node,
        x: CENTER_X + radius * Math.cos(angle),
        y: CENTER_Y + radius * Math.sin(angle),
        revolution,
        angle
      }
    })
  }, [nodes])

  return (
    <div className="relative w-full h-full overflow-auto bg-gray-900">
      <svg width="800" height="800" className="w-full h-full">
        {/* Draw spiral guide */}
        {Array.from({ length: 12 }).map((_, rev) => {
          const radius = BASE_RADIUS + rev * RADIUS_INCREMENT
          return (
            <circle
              key={rev}
              cx={CENTER_X}
              cy={CENTER_Y}
              r={radius}
              fill="none"
              stroke="#374151"
              strokeWidth="1"
              strokeDasharray="2,2"
              opacity="0.3"
            />
          )
        })}

        {/* Draw time period labels */}
        {Array.from({ length: 12 }).map((_, rev) => {
          const radius = BASE_RADIUS + rev * RADIUS_INCREMENT
          return (
            <text
              key={rev}
              x={CENTER_X + radius}
              y={CENTER_Y}
              fill="#6b7280"
              fontSize="10px"
              textAnchor="middle"
            >
              Month {rev + 1}
            </text>
          )
        })}

        {/* Draw nodes */}
        {positionedNodes.map(node => {
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
            <g key={node.id} onClick={() => onNodeSelect(isSelected ? null : node.id)} className="cursor-pointer">
              <circle
                cx={node.x}
                cy={node.y}
                r={isSelected ? 8 : 6}
                fill={fillColor}
                stroke={isSelected ? '#fff' : '#374151'}
                strokeWidth={isSelected ? 2 : 1}
                opacity={isSelected ? 1 : 0.7}
              />
              <text
                x={node.x + 12}
                y={node.y}
                fill="#e5e7eb"
                fontSize="9px"
                dominantBaseline="middle"
              >
                {node.label.length > 20 ? node.label.substring(0, 17) + '...' : node.label}
              </text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}

