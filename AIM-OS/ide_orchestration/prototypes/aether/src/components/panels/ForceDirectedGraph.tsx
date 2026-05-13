// Force-Directed Graph Visualization
// Interactive physics-based layout showing natural clustering

import React, { useRef, useEffect, useMemo } from 'react'
import * as d3 from 'd3'

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

interface ForceDirectedGraphProps {
  nodes: EvolutionNode[]
  selectedNode: string | null
  onNodeSelect: (nodeId: string | null) => void
  getNodeColor: (node: EvolutionNode) => string
  getNodeIcon: (node: EvolutionNode) => React.ReactNode
}

interface D3Node extends d3.SimulationNodeDatum {
  id: string
  data: EvolutionNode
  x?: number
  y?: number
  fx?: number | null
  fy?: number | null
}

interface D3Link extends d3.SimulationLinkDatum<D3Node> {
  source: D3Node | string
  target: D3Node | string
}

export const ForceDirectedGraph: React.FC<ForceDirectedGraphProps> = ({
  nodes,
  selectedNode,
  onNodeSelect,
  getNodeColor,
  getNodeIcon
}) => {
  const svgRef = useRef<SVGSVGElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const simulationRef = useRef<d3.Simulation<D3Node, D3Link> | null>(null)

  // Build graph structure
  const { d3Nodes, d3Links } = useMemo(() => {
    const nodeMap = new Map<string, D3Node>()
    const links: D3Link[] = []

    // Create nodes
    nodes.forEach(node => {
      nodeMap.set(node.id, {
        id: node.id,
        data: node,
        x: undefined,
        y: undefined
      })
    })

    // Create links from parent-child relationships
    nodes.forEach(node => {
      if (node.parentId && nodeMap.has(node.parentId)) {
        links.push({
          source: node.parentId,
          target: node.id
        })
      }
    })

    return {
      d3Nodes: Array.from(nodeMap.values()),
      d3Links
    }
  }, [nodes])

  useEffect(() => {
    if (!svgRef.current || !containerRef.current || d3Nodes.length === 0) return

    const svg = d3.select(svgRef.current)
    const container = containerRef.current
    const width = container.clientWidth || 1200
    const height = container.clientHeight || 800

    // Clear previous content
    svg.selectAll('*').remove()

    // Set SVG dimensions
    svg.attr('width', width).attr('height', height)

    // Create zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform)
      })

    svg.call(zoom)

    // Create container group for zoom
    const g = svg.append('g')

    // Initialize force simulation
    const simulation = d3.forceSimulation<D3Node>(d3Nodes)
      .force('link', d3.forceLink<D3Node, D3Link>(d3Links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30))

    simulationRef.current = simulation

    // Create links
    const link = g.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(d3Links)
      .enter()
      .append('line')
      .attr('stroke', '#6366f1')
      .attr('stroke-opacity', 0.4)
      .attr('stroke-width', 1.5)

    // Create nodes
    const node = g.append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(d3Nodes)
      .enter()
      .append('g')
      .attr('class', 'node')
      .call(d3.drag<SVGGElement, D3Node>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart()
          d.fx = d.x
          d.fy = d.y
        })
        .on('drag', (event, d) => {
          d.fx = event.x
          d.fy = event.y
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0)
          d.fx = null
          d.fy = null
        })
      )
      .on('click', (event, d) => {
        event.stopPropagation()
        onNodeSelect(selectedNode === d.id ? null : d.id)
      })

    // Add circles for nodes
    node.append('circle')
      .attr('r', d => {
        const priority = d.data.priority || ''
        if (priority.includes('S -')) return 12
        if (priority.includes('A -')) return 10
        return 8
      })
      .attr('fill', d => {
        const color = getNodeColor(d.data)
        // Extract color from className or use default
        if (color.includes('blue')) return '#3b82f6'
        if (color.includes('green')) return '#10b981'
        if (color.includes('red')) return '#ef4444'
        if (color.includes('orange')) return '#f97316'
        if (color.includes('purple')) return '#8b5cf6'
        return '#6366f1'
      })
      .attr('stroke', d => selectedNode === d.id ? '#fff' : '#374151')
      .attr('stroke-width', d => selectedNode === d.id ? 3 : 1)
      .attr('opacity', d => selectedNode === d.id ? 1 : 0.8)

    // Add labels
    node.append('text')
      .text(d => d.data.label)
      .attr('dx', 15)
      .attr('dy', 4)
      .attr('font-size', '10px')
      .attr('fill', '#e5e7eb')
      .attr('pointer-events', 'none')

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => (d.source as D3Node).x!)
        .attr('y1', d => (d.source as D3Node).y!)
        .attr('x2', d => (d.target as D3Node).x!)
        .attr('y2', d => (d.target as D3Node).y!)

      node.attr('transform', d => `translate(${d.x},${d.y})`)
    })

    // Cleanup
    return () => {
      simulation.stop()
    }
  }, [d3Nodes, d3Links, selectedNode, onNodeSelect, getNodeColor])

  return (
    <div ref={containerRef} className="w-full h-full overflow-hidden bg-gray-900">
      <svg ref={svgRef} className="w-full h-full" />
    </div>
  )
}

