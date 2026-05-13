// Error Propagation Map Visualization
// Shows how errors spread and what they affected

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

interface ErrorPropagationMapProps {
  nodes: EvolutionNode[]
  selectedNode: string | null
  onNodeSelect: (nodeId: string | null) => void
  getNodeColor: (node: EvolutionNode) => string
  getNodeIcon: (node: EvolutionNode) => React.ReactNode
}

export const ErrorPropagationMap: React.FC<ErrorPropagationMapProps> = ({
  nodes,
  selectedNode,
  onNodeSelect,
  getNodeColor,
  getNodeIcon
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const svgRef = useRef<SVGSVGElement>(null)

  // Filter to errors + affected nodes
  const errorNetwork = useMemo(() => {
    const errorNodes = nodes.filter(n => n.type === 'error' || n.status === 'error')
    const affectedNodes: EvolutionNode[] = []
    const recoveryNodes: EvolutionNode[] = []

    // Find nodes affected by errors (children, or related by parent)
    errorNodes.forEach(error => {
      const affected = nodes.filter(n => 
        n.parentId === error.id || 
        (error.parentId && n.parentId === error.parentId) ||
        n.origin?.includes(error.label)
      )
      affectedNodes.push(...affected)

      // Find recovery actions (nodes created after error)
      const errorDate = new Date(error.timestamp)
      const recovery = nodes.filter(n => {
        const nodeDate = new Date(n.timestamp)
        return nodeDate > errorDate && 
               (n.label.toLowerCase().includes('fix') || 
                n.label.toLowerCase().includes('recovery') ||
                n.description.toLowerCase().includes('recovery'))
      })
      recoveryNodes.push(...recovery)
    })

    return { errorNodes, affectedNodes, recoveryNodes }
  }, [nodes])

  // Calculate positions (errors at top, affected below, recovery at bottom)
  const nodePositions = useMemo(() => {
    const positions: Record<string, { x: number, y: number, type: 'error' | 'affected' | 'recovery' }> = {}
    const ERROR_Y = 50
    const AFFECTED_Y = 300
    const RECOVERY_Y = 550
    const SPACING = 200

    errorNetwork.errorNodes.forEach((error, idx) => {
      positions[error.id] = {
        x: 200 + idx * SPACING,
        y: ERROR_Y,
        type: 'error'
      }
    })

    errorNetwork.affectedNodes.forEach((node, idx) => {
      if (!positions[node.id]) {
        positions[node.id] = {
          x: 200 + (idx % 4) * SPACING,
          y: AFFECTED_Y + Math.floor(idx / 4) * 80,
          type: 'affected'
        }
      }
    })

    errorNetwork.recoveryNodes.forEach((node, idx) => {
      if (!positions[node.id]) {
        positions[node.id] = {
          x: 200 + idx * SPACING,
          y: RECOVERY_Y,
          type: 'recovery'
        }
      }
    })

    return positions
  }, [errorNetwork])

  // Draw propagation paths
  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return

    const svg = svgRef.current
    svg.innerHTML = ''

    errorNetwork.errorNodes.forEach(error => {
      const errorPos = nodePositions[error.id]
      if (!errorPos) return

      // Draw to affected nodes
      errorNetwork.affectedNodes.forEach(affected => {
        if (affected.parentId === error.id || (error.parentId && affected.parentId === error.parentId)) {
          const affectedPos = nodePositions[affected.id]
          if (!affectedPos) return

          const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
          const d = `M ${errorPos.x + 90} ${errorPos.y + 30}
                     L ${errorPos.x + 90} ${errorPos.y + 50}
                     L ${affectedPos.x + 90} ${errorPos.y + 50}
                     L ${affectedPos.x + 90} ${affectedPos.y}`
          path.setAttribute('d', d)
          path.setAttribute('stroke', '#ef4444')
          path.setAttribute('stroke-width', '2')
          path.setAttribute('fill', 'none')
          path.setAttribute('opacity', '0.5')
          svg.appendChild(path)
        }
      })

      // Draw to recovery nodes
      const errorDate = new Date(error.timestamp)
      errorNetwork.recoveryNodes.forEach(recovery => {
        const recoveryDate = new Date(recovery.timestamp)
        if (recoveryDate > errorDate) {
          const recoveryPos = nodePositions[recovery.id]
          if (!recoveryPos) return

          const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
          const d = `M ${errorPos.x + 90} ${errorPos.y + 30}
                     L ${recoveryPos.x + 90} ${recoveryPos.y}`
          path.setAttribute('d', d)
          path.setAttribute('stroke', '#10b981')
          path.setAttribute('stroke-width', '2')
          path.setAttribute('stroke-dasharray', '5,5')
          path.setAttribute('fill', 'none')
          path.setAttribute('opacity', '0.6')
          svg.appendChild(path)
        }
      })
    })
  }, [errorNetwork, nodePositions])

  const displayNodes = [...errorNetwork.errorNodes, ...errorNetwork.affectedNodes, ...errorNetwork.recoveryNodes]

  return (
    <div ref={containerRef} className="relative w-full h-full overflow-auto bg-gray-900">
      <svg ref={svgRef} className="absolute top-0 left-0 pointer-events-none" style={{ zIndex: 1, width: '1200px', height: '800px' }} />
      <div className="relative" style={{ zIndex: 2, minWidth: '1200px', minHeight: '800px' }}>
        {displayNodes.map(node => {
          const pos = nodePositions[node.id]
          if (!pos) return null

          const isSelected = selectedNode === node.id
          const isError = pos.type === 'error'
          const isRecovery = pos.type === 'recovery'

          return (
            <div
              key={node.id}
              onClick={() => onNodeSelect(isSelected ? null : node.id)}
              className={`absolute border rounded-lg p-2 cursor-pointer transition-all text-xs ${
                isError ? 'bg-red-900/40 border-red-600 text-red-300' :
                isRecovery ? 'bg-green-900/40 border-green-600 text-green-300' :
                getNodeColor(node)
              } ${isSelected ? 'ring-2 ring-blue-400' : ''}`}
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
                  {node.errorType && (
                    <div className="text-red-400 text-xs mt-1">Type: {node.errorType}</div>
                  )}
                  {isRecovery && (
                    <div className="text-green-400 text-xs mt-1">RECOVERY</div>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

