// Sankey Flow Diagram Visualization
// Shows flow of effort/data from seed through systems

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

interface SankeyFlowDiagramProps {
  nodes: EvolutionNode[]
  selectedNode: string | null
  onNodeSelect: (nodeId: string | null) => void
}

interface SankeyNode {
  id: string
  name: string
  layer: number
  value: number
}

interface SankeyLink {
  source: number
  target: number
  value: number
}

export const SankeyFlowDiagram: React.FC<SankeyFlowDiagramProps> = ({
  nodes,
  selectedNode,
  onNodeSelect
}) => {
  const svgRef = useRef<SVGSVGElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  // Build Sankey data structure
  const sankeyData = useMemo(() => {
    const sankeyNodes: SankeyNode[] = []
    const sankeyLinks: SankeyLink[] = []
    const nodeIndexMap = new Map<string, number>()

    // Layer 0: Seed
    const seed = nodes.find(n => n.type === 'milestone' && n.label.includes('Start'))
    if (seed) {
      nodeIndexMap.set(seed.id, 0)
      sankeyNodes.push({
        id: seed.id,
        name: seed.label,
        layer: 0,
        value: 100
      })
    }

    // Layer 1: Core Systems (Objectives)
    const objectives = nodes.filter(n => n.type === 'objective')
    objectives.forEach((obj, idx) => {
      const index = sankeyNodes.length
      nodeIndexMap.set(obj.id, index)
      sankeyNodes.push({
        id: obj.id,
        name: obj.label,
        layer: 1,
        value: obj.completion || 50
      })
      
      // Link from seed to objective
      if (seed) {
        sankeyLinks.push({
          source: 0,
          target: index,
          value: obj.completion || 50
        })
      }
    })

    // Layer 2: Key Results (Subsystems)
    const keyResults = nodes.filter(n => n.type === 'key_result')
    keyResults.forEach(kr => {
      const parentIndex = nodeIndexMap.get(kr.parentId || '')
      if (parentIndex !== undefined) {
        const index = sankeyNodes.length
        nodeIndexMap.set(kr.id, index)
        sankeyNodes.push({
          id: kr.id,
          name: kr.label,
          layer: 2,
          value: kr.completion || 30
        })
        
        sankeyLinks.push({
          source: parentIndex,
          target: index,
          value: kr.completion || 30
        })
      }
    })

    return { nodes: sankeyNodes, links: sankeyLinks }
  }, [nodes])

  useEffect(() => {
    if (!svgRef.current || !containerRef.current || sankeyData.nodes.length === 0) return

    const svg = d3.select(svgRef.current)
    const container = containerRef.current
    const width = container.clientWidth || 1200
    const height = container.clientHeight || 600
    const nodeWidth = 15
    const nodePadding = 10

    svg.selectAll('*').remove()
    svg.attr('width', width).attr('height', height)

    // Calculate layer positions
    const layers = [0, 1, 2]
    const layerWidth = width / (layers.length + 1)
    
    // Position nodes by layer
    const nodesByLayer = new Map<number, SankeyNode[]>()
    sankeyData.nodes.forEach(node => {
      if (!nodesByLayer.has(node.layer)) {
        nodesByLayer.set(node.layer, [])
      }
      nodesByLayer.get(node.layer)!.push(node)
    })

    // Calculate node positions
    const positionedNodes = sankeyData.nodes.map(node => {
      const layerNodes = nodesByLayer.get(node.layer) || []
      const nodeIndex = layerNodes.indexOf(node)
      const totalHeight = layerNodes.reduce((sum, n) => sum + n.value + nodePadding, 0)
      const startY = (height - totalHeight) / 2
      
      let y = startY
      for (let i = 0; i < nodeIndex; i++) {
        y += layerNodes[i].value + nodePadding
      }
      
      return {
        ...node,
        x: layerWidth * (node.layer + 1),
        y: y,
        width: nodeWidth,
        height: node.value
      }
    })

    // Draw links
    sankeyData.links.forEach(link => {
      const source = positionedNodes[link.source]
      const target = positionedNodes[link.target]
      
      if (!source || !target) return

      const path = d3.path()
      const sourceX = source.x + source.width
      const sourceY = source.y + source.height / 2
      const targetX = target.x
      const targetY = target.y + target.height / 2
      
      // Curved path
      path.moveTo(sourceX, sourceY)
      path.bezierCurveTo(
        sourceX + (targetX - sourceX) / 2, sourceY,
        sourceX + (targetX - sourceX) / 2, targetY,
        targetX, targetY
      )
      
      svg.append('path')
        .attr('d', path.toString())
        .attr('fill', 'none')
        .attr('stroke', '#6366f1')
        .attr('stroke-width', Math.max(1, link.value / 10))
        .attr('opacity', 0.4)
    })

    // Draw nodes
    positionedNodes.forEach(node => {
      const isSelected = selectedNode === node.id
      const g = svg.append('g')
        .attr('class', 'node')
        .attr('transform', `translate(${node.x}, ${node.y})`)
        .on('click', () => onNodeSelect(isSelected ? null : node.id))
        .style('cursor', 'pointer')

      g.append('rect')
        .attr('width', node.width)
        .attr('height', node.height)
        .attr('fill', node.layer === 0 ? '#eab308' : node.layer === 1 ? '#3b82f6' : '#8b5cf6')
        .attr('stroke', isSelected ? '#fff' : '#374151')
        .attr('stroke-width', isSelected ? 2 : 1)
        .attr('opacity', isSelected ? 1 : 0.8)

      g.append('text')
        .attr('x', node.width + 5)
        .attr('y', node.height / 2)
        .attr('dy', '0.35em')
        .attr('font-size', '10px')
        .attr('fill', '#e5e7eb')
        .text(node.name.length > 20 ? node.name.substring(0, 17) + '...' : node.name)
    })
  }, [sankeyData, selectedNode, onNodeSelect])

  return (
    <div ref={containerRef} className="w-full h-full overflow-auto bg-gray-900">
      <svg ref={svgRef} className="w-full h-full" />
    </div>
  )
}

