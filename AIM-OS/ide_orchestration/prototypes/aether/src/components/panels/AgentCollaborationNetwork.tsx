// Agent Collaboration Network Visualization
// Focus on agent communication and collaboration patterns

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

interface AgentCollaborationNetworkProps {
  nodes: EvolutionNode[]
  selectedNode: string | null
  onNodeSelect: (nodeId: string | null) => void
  getNodeColor: (node: EvolutionNode) => string
  getNodeIcon: (node: EvolutionNode) => React.ReactNode
}

const AGENTS = ['Aether', 'Max', 'Lex', 'Codex', 'Dac', 'Rev', 'Sam']

export const AgentCollaborationNetwork: React.FC<AgentCollaborationNetworkProps> = ({
  nodes,
  selectedNode,
  onNodeSelect,
  getNodeColor,
  getNodeIcon
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const svgRef = useRef<SVGSVGElement>(null)

  // Filter to agent-related nodes
  const agentNetwork = useMemo(() => {
    const agentNodes: Array<{ id: string, label: string, type: 'agent', x: number, y: number }> = []
    const goalNodes: Array<EvolutionNode & { agent?: string, x: number, y: number }> = []
    const connections: Array<{ from: string, to: string, type: 'works_on' | 'communicates' }> = []

    // Create agent nodes (positioned in circle)
    const centerX = 400
    const centerY = 300
    const radius = 200
    AGENTS.forEach((agent, idx) => {
      const angle = (idx * 2 * Math.PI) / AGENTS.length
      agentNodes.push({
        id: `agent-${agent.toLowerCase()}`,
        label: agent,
        type: 'agent',
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      })
    })

    // Find goals worked on by agents (from origin field or label)
    nodes.forEach(node => {
      const agentMatch = AGENTS.find(agent => 
        node.origin?.includes(agent) || 
        node.label.includes(agent) ||
        node.description.includes(agent)
      )
      
      if (agentMatch || node.type === 'objective' || node.type === 'key_result') {
        const agentId = agentMatch ? `agent-${agentMatch.toLowerCase()}` : null
        goalNodes.push({
          ...node,
          agent: agentMatch,
          x: agentId ? centerX + (radius + 100) * Math.cos(AGENTS.indexOf(agentMatch) * 2 * Math.PI / AGENTS.length) : centerX + Math.random() * 200 - 100,
          y: agentId ? centerY + (radius + 100) * Math.sin(AGENTS.indexOf(agentMatch) * 2 * Math.PI / AGENTS.length) : centerY + Math.random() * 200 - 100
        })
        
        if (agentId) {
          connections.push({ from: agentId, to: node.id, type: 'works_on' })
        }
      }
    })

    return { agentNodes, goalNodes, connections }
  }, [nodes])

  // Draw connections
  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return

    const svg = svgRef.current
    svg.innerHTML = ''

    agentNetwork.connections.forEach(conn => {
      const fromNode = agentNetwork.agentNodes.find(n => n.id === conn.from) || 
                       agentNetwork.goalNodes.find(n => n.id === conn.from)
      const toNode = agentNetwork.goalNodes.find(n => n.id === conn.to) ||
                     agentNetwork.agentNodes.find(n => n.id === conn.to)

      if (!fromNode || !toNode) return

      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line')
      line.setAttribute('x1', fromNode.x.toString())
      line.setAttribute('y1', fromNode.y.toString())
      line.setAttribute('x2', toNode.x.toString())
      line.setAttribute('y2', toNode.y.toString())
      line.setAttribute('stroke', conn.type === 'works_on' ? '#3b82f6' : '#8b5cf6')
      line.setAttribute('stroke-width', '1.5')
      line.setAttribute('opacity', '0.4')
      svg.appendChild(line)
    })
  }, [agentNetwork])

  return (
    <div ref={containerRef} className="relative w-full h-full overflow-auto bg-gray-900">
      <svg ref={svgRef} className="absolute top-0 left-0 w-full h-full pointer-events-none" />
      <div className="relative" style={{ minWidth: '800px', minHeight: '600px' }}>
        {/* Agent nodes */}
        {agentNetwork.agentNodes.map(agent => (
          <div
            key={agent.id}
            onClick={() => onNodeSelect(selectedNode === agent.id ? null : agent.id)}
            className="absolute border-2 border-cyan-400 bg-cyan-900/40 rounded-full p-4 cursor-pointer transition-all hover:scale-110"
            style={{
              left: `${agent.x}px`,
              top: `${agent.y}px`,
              transform: 'translate(-50%, -50%)',
              width: '80px',
              height: '80px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <div className="text-xs font-semibold text-cyan-300 text-center">{agent.label}</div>
          </div>
        ))}
        
        {/* Goal nodes */}
        {agentNetwork.goalNodes.map(goal => {
          const isSelected = selectedNode === goal.id
          return (
            <div
              key={goal.id}
              onClick={() => onNodeSelect(isSelected ? null : goal.id)}
              className={`absolute border rounded-lg p-2 cursor-pointer transition-all text-xs ${
                getNodeColor(goal)
              } ${isSelected ? 'ring-2 ring-blue-400' : ''}`}
              style={{
                left: `${goal.x}px`,
                top: `${goal.y}px`,
                transform: 'translate(-50%, -50%)',
                maxWidth: '120px'
              }}
            >
              <div className="font-semibold text-center">{goal.label.length > 15 ? goal.label.substring(0, 12) + '...' : goal.label}</div>
              {goal.agent && (
                <div className="text-xs text-gray-400 text-center mt-1">by {goal.agent}</div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

