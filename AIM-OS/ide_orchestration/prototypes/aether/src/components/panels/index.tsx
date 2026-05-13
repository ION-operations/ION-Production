// Enhanced Evolution Explorer
// Visualizes project evolution: goals, errors, divergences, and evolution paths

import React, { useState, useMemo, useRef, useEffect } from 'react'
import { 
  Target, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  GitBranch, 
  Clock, 
  Zap,
  TrendingUp,
  ArrowRight,
  Star
} from 'lucide-react'
import { ForceDirectedGraph } from './ForceDirectedGraph'
import { ImpactMap } from './ImpactMap'
import { AgentCollaborationNetwork } from './AgentCollaborationNetwork'
import { SankeyFlowDiagram } from './SankeyFlowDiagram'
import { DependencyGraph } from './DependencyGraph'
import { ErrorPropagationMap } from './ErrorPropagationMap'
import { TimelineSpiral } from './TimelineSpiral'

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
  origin?: string // Where this goal came from
  errorType?: 'repeated_error' | 'priority_change' | 'timeline_shift' | 'scope_change'
  divergenceReason?: string
}

// Build evolution timeline from GOAL_TREE.yaml and project history
const buildEvolutionTimeline = (): EvolutionNode[] => {
  return [
    // Project Start
    {
      id: 'milestone-001',
      type: 'milestone',
      label: 'Project Start',
      description: 'AIM-OS project initiated',
      timestamp: '2025-10-01',
      status: 'completed'
    },
    
    // North Star Setting
    {
      id: 'north-star-001',
      type: 'north_star',
      label: 'North Star Set',
      description: 'Ship AIM-OS v0.3 (CMC + HHNI + MCP Tools + Daemon) to internal dog-food users by 2025-11-30',
      timestamp: '2025-10-05',
      status: 'in_progress',
      completion: 45
    },
    
    // Core Systems Planning
    {
      id: 'milestone-002',
      type: 'milestone',
      label: 'Core Systems Identified',
      description: 'CMC, HHNI, VIF, SEG, APOE, TCS, CAS, IIS, SDF-CVF',
      timestamp: '2025-10-10',
      status: 'completed',
      parentId: 'north-star-001'
    },
    
    // Initial Objectives (Tier S - Ship Critical)
    {
      id: 'obj-01',
      type: 'objective',
      label: 'OBJ-01: Reliable Memory Storage (CMC)',
      description: 'Ensure deterministic atoms/snapshots, no data loss, and auditability',
      timestamp: '2025-10-12',
      status: 'in_progress',
      completion: 70,
      priority: 'S - SHIP-CRITICAL',
      parentId: 'north-star-001',
      children: ['kr-1.1', 'kr-1.2', 'kr-1.3']
    },
    {
      id: 'obj-02',
      type: 'objective',
      label: 'OBJ-02: Hierarchical Indexing (HHNI)',
      description: 'Enable fast paragraph/sentence retrieval with safety and observability',
      timestamp: '2025-10-12',
      status: 'completed',
      completion: 100,
      priority: 'S - SHIP-CRITICAL',
      parentId: 'north-star-001',
      children: ['kr-2.1', 'kr-2.2', 'kr-2.3']
    },
    
    // Key Results for OBJ-01
    {
      id: 'kr-1.1',
      type: 'key_result',
      label: 'KR-1.1: Snapshot determinism',
      description: '100% test pass rate',
      timestamp: '2025-10-15',
      status: 'in_progress',
      completion: 85,
      parentId: 'obj-01'
    },
    {
      id: 'kr-1.2',
      type: 'key_result',
      label: 'KR-1.2: Write-error rate',
      description: '<0.1% over 10k writes',
      timestamp: '2025-10-15',
      status: 'in_progress',
      completion: 70,
      parentId: 'obj-01'
    },
    {
      id: 'kr-1.3',
      type: 'key_result',
      label: 'KR-1.3: Journal corruption',
      description: '0 incidents in production',
      timestamp: '2025-10-15',
      status: 'in_progress',
      completion: 90,
      parentId: 'obj-01'
    },
    
    // Key Results for OBJ-02 (Completed)
    {
      id: 'kr-2.1',
      type: 'key_result',
      label: 'KR-2.1: Query latency',
      description: '<100 ms p99 latency',
      timestamp: '2025-10-20',
      status: 'completed',
      completion: 100,
      parentId: 'obj-02'
    },
    {
      id: 'kr-2.2',
      type: 'key_result',
      label: 'KR-2.2: Node explosion',
      description: '0 incidents',
      timestamp: '2025-10-20',
      status: 'completed',
      completion: 100,
      parentId: 'obj-02'
    },
    {
      id: 'kr-2.3',
      type: 'key_result',
      label: 'KR-2.3: Build success rate',
      description: '>=99% across 1k atoms',
      timestamp: '2025-10-20',
      status: 'completed',
      completion: 100,
      parentId: 'obj-02'
    },
    
    // Error: Repeated Failures
    {
      id: 'error-001',
      type: 'error',
      label: 'Repeated Error Pattern',
      description: '200+ repeated failures identified - escalation protocol created',
      timestamp: '2025-10-22',
      status: 'error',
      errorType: 'repeated_error',
      parentId: 'obj-01'
    },
    
    // Divergence: Infrastructure Priority Change
    {
      id: 'divergence-001',
      type: 'divergence',
      label: 'Priority Elevation: OBJ-07, OBJ-08',
      description: 'Infrastructure goals elevated to TIER S - CRITICAL (2025-11-04). Originally planned as secondary, but identified as THE INTERFACE to core systems.',
      timestamp: '2025-11-04',
      status: 'completed',
      divergenceReason: 'Realized MCP tools + daemon are ship-blocking, not optional',
      parentId: 'north-star-001'
    },
    
    // New Goals Added Along the Way
    {
      id: 'obj-07',
      type: 'objective',
      label: 'OBJ-07: MCP Tools Real Integrations',
      description: 'Replace ALL placeholders with real CMC/HHNI/VIF/APOE integrations',
      timestamp: '2025-11-04',
      status: 'in_progress',
      completion: 5,
      priority: 'S - SHIP-CRITICAL',
      parentId: 'divergence-001',
      origin: 'Priority elevation from divergence-001'
    },
    {
      id: 'obj-08',
      type: 'objective',
      label: 'OBJ-08: Daemon/RAG System',
      description: 'Intelligent tool selection daemon for 40-tool limit management',
      timestamp: '2025-11-04',
      status: 'in_progress',
      completion: 75,
      priority: 'S - SHIP-CRITICAL',
      parentId: 'divergence-001',
      origin: 'Priority elevation from divergence-001'
    },
    
    // New Goal: OBJ-12 (Protocols Enforcement)
    {
      id: 'obj-12',
      type: 'objective',
      label: 'OBJ-12: Protocols & Standards Enforcement',
      description: 'Meta-goal: Ensure ALL work follows protocols (A-H, L0-L6, Quintet Parity)',
      timestamp: '2025-11-05',
      status: 'in_progress',
      completion: 60,
      priority: 'S - SHIP-CRITICAL',
      parentId: 'north-star-001',
      origin: 'Identified need for meta-enforcement after protocol violations'
    },
    
    // New Goal: OBJ-13 (Packaging)
    {
      id: 'obj-13',
      type: 'objective',
      label: 'OBJ-13: Automated Packaging & Distribution',
      description: 'Professional automated packaging system',
      timestamp: '2025-11-05',
      status: 'designed',
      completion: 10,
      priority: 'B - MEDIUM',
      parentId: 'north-star-001',
      origin: 'Gap identified in goal tree audit'
    },
    
    // New Goal: OBJ-14 (NL Tags)
    {
      id: 'obj-14',
      type: 'objective',
      label: 'OBJ-14: Universal NL Tag Registry',
      description: 'Complete universal registry for NL tags with P >= 0.90 quintet parity',
      timestamp: '2025-11-05',
      status: 'in_progress',
      completion: 70,
      priority: 'A - HIGH',
      parentId: 'north-star-001',
      origin: 'Formalized historical GOAL 5'
    },
    
    // Error: Protocol Violations
    {
      id: 'error-002',
      type: 'error',
      label: 'Protocol Violations Detected',
      description: '40+ files dumped in ROOT, protocols skipped, standards violated',
      timestamp: '2025-11-05',
      status: 'error',
      errorType: 'scope_change',
      parentId: 'obj-12'
    },
    
    // Current Status
    {
      id: 'milestone-current',
      type: 'milestone',
      label: 'Current State',
      description: '14 objectives active, 1 completed (OBJ-02), 13 in progress',
      timestamp: '2025-11-08',
      status: 'in_progress',
      parentId: 'north-star-001'
    }
  ]
}

// LUCID Diagram Tree Component - Visual hierarchical tree with connecting lines
interface LucidDiagramTreeProps {
  nodes: EvolutionNode[]
  selectedNode: string | null
  onNodeSelect: (nodeId: string | null) => void
  getNodeColor: (node: EvolutionNode) => string
  getNodeIcon: (node: EvolutionNode) => React.ReactNode
}

const LucidDiagramTree: React.FC<LucidDiagramTreeProps> = ({
  nodes,
  selectedNode,
  onNodeSelect,
  getNodeColor,
  getNodeIcon
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const nodeRefs = useRef<Record<string, HTMLDivElement | null>>({})
  const svgRef = useRef<SVGSVGElement>(null)
  
  // Build tree structure
  const treeStructure = useMemo(() => {
    const nodeMap = new Map<string, EvolutionNode>()
    const rootNodes: EvolutionNode[] = []
    
    nodes.forEach(node => {
      nodeMap.set(node.id, node)
    })
    
    nodes.forEach(node => {
      if (!node.parentId) {
        rootNodes.push(node)
      }
    })
    
    return { nodeMap, rootNodes }
  }, [nodes])
  
  // Calculate node positions (hierarchical layout)
  const nodePositions = useMemo(() => {
    const positions: Record<string, { x: number, y: number, width: number, height: number }> = {}
    const NODE_WIDTH = 200
    const NODE_HEIGHT = 80
    const HORIZONTAL_SPACING = 250
    const VERTICAL_SPACING = 120
    
    let currentY = 50
    let maxDepth = 0
    
    const calculatePositions = (node: EvolutionNode, depth: number, x: number) => {
      maxDepth = Math.max(maxDepth, depth)
      const children = nodes.filter(n => n.parentId === node.id)
      
      if (children.length === 0) {
        positions[node.id] = { x, y: currentY, width: NODE_WIDTH, height: NODE_HEIGHT }
        currentY += NODE_HEIGHT + VERTICAL_SPACING
        return x
      }
      
      // Calculate children positions first
      let childX = x - ((children.length - 1) * HORIZONTAL_SPACING) / 2
      const childXs: number[] = []
      
      children.forEach(child => {
        const childPos = calculatePositions(child, depth + 1, childX)
        childXs.push(childPos)
        childX += HORIZONTAL_SPACING
      })
      
      // Position parent centered above children
      const parentX = children.length > 0 
        ? (Math.min(...childXs) + Math.max(...childXs)) / 2
        : x
      
      positions[node.id] = { x: parentX, y: currentY, width: NODE_WIDTH, height: NODE_HEIGHT }
      currentY += NODE_HEIGHT + VERTICAL_SPACING
      
      return parentX
    }
    
    treeStructure.rootNodes.forEach((root, idx) => {
      calculatePositions(root, 0, 400 + idx * HORIZONTAL_SPACING)
    })
    
    return positions
  }, [nodes, treeStructure])
  
  // Draw connecting lines
  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return
    
    const svg = svgRef.current
    const container = containerRef.current
    
    // Update SVG size
    const maxX = Math.max(...Object.values(nodePositions).map(p => p.x + p.width), 1000)
    const maxY = Math.max(...Object.values(nodePositions).map(p => p.y + p.height), 2000)
    svg.setAttribute('width', maxX.toString())
    svg.setAttribute('height', maxY.toString())
    
    // Clear previous lines
    svg.innerHTML = ''
    
    // Draw lines for parent-child relationships
    nodes.forEach(node => {
      if (!node.parentId) return
      
      const parentPos = nodePositions[node.parentId]
      const childPos = nodePositions[node.id]
      
      if (!parentPos || !childPos) return
      
      // Get actual element positions
      const parentEl = nodeRefs.current[node.parentId]
      const childEl = nodeRefs.current[node.id]
      
      if (!parentEl || !childEl) return
      
      const parentRect = parentEl.getBoundingClientRect()
      const childRect = childEl.getBoundingClientRect()
      const containerRect = container.getBoundingClientRect()
      
      const parentX = parentRect.left - containerRect.left + parentRect.width / 2 + container.scrollLeft
      const parentY = parentRect.top - containerRect.top + parentRect.height + container.scrollTop
      const childX = childRect.left - containerRect.left + childRect.width / 2 + container.scrollLeft
      const childY = childRect.top - containerRect.top + container.scrollTop
      
      // Draw line: vertical from parent → horizontal → vertical to child
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
      const midY = parentY + (childY - parentY) / 2
      const d = `M ${parentX} ${parentY} 
                 L ${parentX} ${midY} 
                 L ${childX} ${midY} 
                 L ${childX} ${childY}`
      path.setAttribute('d', d)
      path.setAttribute('stroke', node.type === 'error' ? '#ef4444' : node.type === 'divergence' ? '#f97316' : '#6366f1')
      path.setAttribute('stroke-width', '2')
      path.setAttribute('fill', 'none')
      path.setAttribute('opacity', '0.5')
      svg.appendChild(path)
    })
    
    // Update on scroll
    const updateLines = () => {
      svg.innerHTML = ''
      nodes.forEach(node => {
        if (!node.parentId) return
        
        const parentEl = nodeRefs.current[node.parentId]
        const childEl = nodeRefs.current[node.id]
        
        if (!parentEl || !childEl) return
        
        const parentRect = parentEl.getBoundingClientRect()
        const childRect = childEl.getBoundingClientRect()
        const containerRect = container.getBoundingClientRect()
        
        const parentX = parentRect.left - containerRect.left + parentRect.width / 2 + container.scrollLeft
        const parentY = parentRect.top - containerRect.top + parentRect.height + container.scrollTop
        const childX = childRect.left - containerRect.left + childRect.width / 2 + container.scrollLeft
        const childY = childRect.top - containerRect.top + container.scrollTop
        
        const midY = parentY + (childY - parentY) / 2
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
        const d = `M ${parentX} ${parentY} 
                   L ${parentX} ${midY} 
                   L ${childX} ${midY} 
                   L ${childX} ${childY}`
        path.setAttribute('d', d)
        path.setAttribute('stroke', node.type === 'error' ? '#ef4444' : node.type === 'divergence' ? '#f97316' : '#6366f1')
        path.setAttribute('stroke-width', '2')
        path.setAttribute('fill', 'none')
        path.setAttribute('opacity', '0.5')
        svg.appendChild(path)
      })
    }
    
    container.addEventListener('scroll', updateLines)
    window.addEventListener('resize', updateLines)
    
    return () => {
      container.removeEventListener('scroll', updateLines)
      window.removeEventListener('resize', updateLines)
    }
  }, [nodes, nodePositions])
  
  const renderNode = (node: EvolutionNode): React.ReactNode => {
    const pos = nodePositions[node.id]
    if (!pos) return null
    
    const isSelected = selectedNode === node.id
    
    return (
      <div
        key={node.id}
        ref={(el) => { nodeRefs.current[node.id] = el }}
        className="absolute"
        style={{
          left: `${pos.x}px`,
          top: `${pos.y}px`,
          width: `${pos.width}px`
        }}
      >
        <div
          onClick={() => onNodeSelect(isSelected ? null : node.id)}
          className={`border rounded-lg p-3 cursor-pointer transition-all ${
            getNodeColor(node)
          } ${isSelected ? 'ring-2 ring-blue-400 shadow-lg' : ''}`}
        >
          <div className="flex items-start gap-2">
            <div className="mt-0.5">{getNodeIcon(node)}</div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-semibold mb-1 truncate">{node.label}</div>
              <div className="text-xs text-gray-400 mb-2 line-clamp-2">{node.description}</div>
              <div className="flex items-center gap-2 flex-wrap">
                {node.completion !== undefined && (
                  <div className="flex items-center gap-1">
                    <div className="w-12 bg-gray-700 rounded-full h-1">
                      <div
                        className={`h-1 rounded-full ${
                          node.status === 'completed' ? 'bg-green-500' : 'bg-blue-500'
                        }`}
                        style={{ width: `${node.completion}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-400">{node.completion}%</span>
                  </div>
                )}
                {node.priority && (
                  <span className="text-xs px-1.5 py-0.5 bg-gray-700 rounded">
                    {node.priority.split(' - ')[0]}
                  </span>
                )}
                <span className="text-xs text-gray-500">{node.timestamp}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
  
  return (
    <div ref={containerRef} className="relative w-full h-full overflow-auto">
      <svg
        ref={svgRef}
        className="absolute top-0 left-0 pointer-events-none"
        style={{ zIndex: 1 }}
      />
      <div className="relative" style={{ zIndex: 2 }}>
        {nodes.map(node => renderNode(node))}
      </div>
    </div>
  )
}

// Seed Growth Visualization - Radial organic growth from seed
interface SeedGrowthVisualizationProps {
  nodes: EvolutionNode[]
  selectedNode: string | null
  onNodeSelect: (nodeId: string | null) => void
  getNodeColor: (node: EvolutionNode) => string
  getNodeIcon: (node: EvolutionNode) => React.ReactNode
}

const SeedGrowthVisualization: React.FC<SeedGrowthVisualizationProps> = ({
  nodes,
  selectedNode,
  onNodeSelect,
  getNodeColor,
  getNodeIcon
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const nodeRefs = useRef<Record<string, HTMLDivElement | null>>({})
  const svgRef = useRef<SVGSVGElement>(null)
  
  // Build comprehensive seed-to-system structure
  const seedStructure = useMemo(() => {
    // THE SEED - Original idea
    const seed = {
      id: 'seed-001',
      type: 'milestone' as const,
      label: '🌱 The Seed',
      description: 'Memory-native AI that doesn\'t forget',
      timestamp: '2025-10-15',
      status: 'completed' as const,
      layer: 0,
      angle: 0,
      radius: 0
    }
    
    // Layer 1: Core Systems (Ring 1)
    const coreSystems = [
      { id: 'obj-01', label: 'CMC', description: 'Reliable Memory Storage', angle: 0 },
      { id: 'obj-02', label: 'HHNI', description: 'Hierarchical Indexing', angle: 40 },
      { id: 'vif', label: 'VIF', description: 'Verifiable Intelligence', angle: 80 },
      { id: 'seg', label: 'SEG', description: 'Shared Evidence Graph', angle: 120 },
      { id: 'apoe', label: 'APOE', description: 'AI-Powered Orchestration', angle: 160 },
      { id: 'sdf-cvf', label: 'SDF-CVF', description: 'Atomic Evolution', angle: 200 },
      { id: 'tcs', label: 'TCS', description: 'Timeline Context', angle: 240 },
      { id: 'cas', label: 'CAS', description: 'Cognitive Analysis', angle: 280 },
      { id: 'iis', label: 'IIS', description: 'Intuitive Intelligence', angle: 320 }
    ]
    
    // Layer 2: Subsystems (Ring 2)
    const subsystems = [
      // CMC subsystems
      { id: 'cmc-atoms', label: 'Atoms', parent: 'obj-01', angle: -20 },
      { id: 'cmc-snapshots', label: 'Snapshots', parent: 'obj-01', angle: 20 },
      { id: 'cmc-journal', label: 'Journal', parent: 'obj-01', angle: 0 },
      
      // HHNI subsystems
      { id: 'hhni-dvns', label: 'DVNS', parent: 'obj-02', angle: -15 },
      { id: 'hhni-index', label: '6-Level Index', parent: 'obj-02', angle: 15 },
      
      // VIF subsystems
      { id: 'vif-witness', label: 'Witnesses', parent: 'vif', angle: -10 },
      { id: 'vif-kappa', label: 'κ-Gating', parent: 'vif', angle: 10 },
      
      // MCP Tools
      { id: 'mcp-tools', label: 'MCP Tools', parent: 'apoe', angle: -30 },
      { id: 'mcp-daemon', label: 'RAG Daemon', parent: 'apoe', angle: 30 },
      
      // Documentation
      { id: 'docs-t0-t6', label: 'T0-T6 Docs', parent: 'sdf-cvf', angle: -20 },
      { id: 'docs-l0-l6', label: 'L0-L6 Specs', parent: 'sdf-cvf', angle: 20 },
      
      // Organization
      { id: 'org-system-maps', label: 'System Maps', parent: 'seg', angle: -15 },
      { id: 'org-indexes', label: 'Indexes', parent: 'seg', angle: 15 },
      { id: 'org-super-index', label: 'Super Index', parent: 'seg', angle: 0 }
    ]
    
    // Layer 3: Details (Ring 3) - Agents, Tools, Docs, Maps, Indexes
    const details: Array<{ id: string, label: string, parent: string, angle: number, type?: 'agent' | 'tool' | 'doc' | 'map' | 'index' | 'detail' }> = [
      // Agent communication (from APOE)
      { id: 'agents-aether', label: 'Aether', parent: 'apoe', angle: -50, type: 'agent' },
      { id: 'agents-max', label: 'Max', parent: 'apoe', angle: -30, type: 'agent' },
      { id: 'agents-lex', label: 'Lex', parent: 'apoe', angle: -10, type: 'agent' },
      { id: 'agents-codex', label: 'Codex', parent: 'apoe', angle: 10, type: 'agent' },
      { id: 'agents-dac', label: 'Dac', parent: 'apoe', angle: 30, type: 'agent' },
      { id: 'agents-rev', label: 'Rev', parent: 'apoe', angle: 50, type: 'agent' },
      
      // Tool calls (from MCP Tools)
      { id: 'tools-mcp-store', label: 'store_memory', parent: 'mcp-tools', angle: -20, type: 'tool' },
      { id: 'tools-mcp-retrieve', label: 'retrieve_memory', parent: 'mcp-tools', angle: 0, type: 'tool' },
      { id: 'tools-mcp-track', label: 'track_confidence', parent: 'mcp-tools', angle: 20, type: 'tool' },
      
      // RAG Daemon
      { id: 'tools-rag-query', label: 'RAG Query', parent: 'mcp-daemon', angle: -15, type: 'tool' },
      { id: 'tools-rag-select', label: 'Tool Select', parent: 'mcp-daemon', angle: 15, type: 'tool' },
      
      // Documentation details (from T0-T6)
      { id: 'docs-t0', label: 'T0 Exec', parent: 'docs-t0-t6', angle: -40, type: 'doc' },
      { id: 'docs-t1', label: 'T1 Overview', parent: 'docs-t0-t6', angle: -20, type: 'doc' },
      { id: 'docs-t2', label: 'T2 Arch', parent: 'docs-t0-t6', angle: 0, type: 'doc' },
      { id: 'docs-t3', label: 'T3 Detailed', parent: 'docs-t0-t6', angle: 20, type: 'doc' },
      { id: 'docs-t4', label: 'T4 Complete', parent: 'docs-t0-t6', angle: 40, type: 'doc' },
      
      // L0-L6 Specs
      { id: 'docs-l0', label: 'L0 Exec', parent: 'docs-l0-l6', angle: -30, type: 'doc' },
      { id: 'docs-l1', label: 'L1 Overview', parent: 'docs-l0-l6', angle: -10, type: 'doc' },
      { id: 'docs-l2', label: 'L2 Arch', parent: 'docs-l0-l6', angle: 10, type: 'doc' },
      { id: 'docs-l3', label: 'L3 Detailed', parent: 'docs-l0-l6', angle: 30, type: 'doc' },
      
      // System maps (from Organization)
      { id: 'map-cmc', label: 'CMC Map', parent: 'org-system-maps', angle: -20, type: 'map' },
      { id: 'map-hhni', label: 'HHNI Map', parent: 'org-system-maps', angle: 0, type: 'map' },
      { id: 'map-vif', label: 'VIF Map', parent: 'org-system-maps', angle: 20, type: 'map' },
      
      // Indexes
      { id: 'idx-super', label: 'Super Index', parent: 'org-super-index', angle: -15, type: 'index' },
      { id: 'idx-hierarchical', label: 'HHNI Index', parent: 'org-indexes', angle: 15, type: 'index' },
      { id: 'idx-global', label: 'Global Atlas', parent: 'org-super-index', angle: 0, type: 'index' },
      
      // CMC Details
      { id: 'cmc-atom-structure', label: 'Atom Struct', parent: 'cmc-atoms', angle: -10, type: 'detail' },
      { id: 'cmc-snapshot-system', label: 'Snapshot Sys', parent: 'cmc-snapshots', angle: 10, type: 'detail' },
      
      // HHNI Details
      { id: 'hhni-physics', label: 'DVNS Physics', parent: 'hhni-dvns', angle: -10, type: 'detail' },
      { id: 'hhni-levels', label: '6 Levels', parent: 'hhni-index', angle: 10, type: 'detail' }
    ]
    
    // Calculate positions
    const CENTER_X = 600
    const CENTER_Y = 400
    const RING_1_RADIUS = 150
    const RING_2_RADIUS = 280
    const RING_3_RADIUS = 420
    
    const positionedNodes: Array<EvolutionNode & { x: number, y: number, layer: number }> = []
    
    // Seed at center
    positionedNodes.push({
      ...seed,
      x: CENTER_X,
      y: CENTER_Y,
      layer: 0
    })
    
    // Layer 1: Core Systems
    coreSystems.forEach(sys => {
      const angleRad = (sys.angle * Math.PI) / 180
      positionedNodes.push({
        id: sys.id,
        type: 'objective',
        label: sys.label,
        description: sys.description,
        timestamp: '2025-10-20',
        status: 'in_progress',
        completion: 70,
        x: CENTER_X + RING_1_RADIUS * Math.cos(angleRad),
        y: CENTER_Y + RING_1_RADIUS * Math.sin(angleRad),
        layer: 1,
        parentId: 'seed-001'
      })
    })
    
    // Layer 2: Subsystems
    subsystems.forEach(sub => {
      const parent = positionedNodes.find(n => n.id === sub.parent)
      if (!parent) return
      
      const parentAngle = Math.atan2(parent.y - CENTER_Y, parent.x - CENTER_X)
      const angleRad = parentAngle + (sub.angle * Math.PI) / 180
      
      positionedNodes.push({
        id: sub.id,
        type: 'key_result',
        label: sub.label,
        description: `${sub.label} subsystem`,
        timestamp: '2025-10-25',
        status: 'in_progress',
        x: CENTER_X + RING_2_RADIUS * Math.cos(angleRad),
        y: CENTER_Y + RING_2_RADIUS * Math.sin(angleRad),
        layer: 2,
        parentId: sub.parent
      })
    })
    
    // Layer 3: Details
    details.forEach(detail => {
      const parent = positionedNodes.find(n => n.id === detail.parent)
      if (!parent) return
      
      const parentAngle = Math.atan2(parent.y - CENTER_Y, parent.x - CENTER_X)
      const angleRad = parentAngle + (detail.angle * Math.PI) / 180
      
      positionedNodes.push({
        id: detail.id,
        type: detail.type === 'agent' ? 'milestone' : detail.type === 'tool' ? 'key_result' : 'milestone',
        label: detail.label,
        description: detail.type === 'agent' ? 'AI Agent' : detail.type === 'tool' ? 'MCP Tool Call' : `${detail.label} detail`,
        timestamp: '2025-11-01',
        status: 'in_progress',
        x: CENTER_X + RING_3_RADIUS * Math.cos(angleRad),
        y: CENTER_Y + RING_3_RADIUS * Math.sin(angleRad),
        layer: 3,
        parentId: detail.parent
      })
    })
    
    return positionedNodes
  }, [])
  
  // Draw organic growth lines
  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return
    
    const svg = svgRef.current
    const container = containerRef.current
    
    svg.setAttribute('width', '2000')
    svg.setAttribute('height', '2000')
    svg.innerHTML = ''
    
    seedStructure.forEach(node => {
      if (!node.parentId) return
      
      const parent = seedStructure.find(n => n.id === node.parentId)
      if (!parent) return
      
      const parentEl = nodeRefs.current[node.parentId]
      const childEl = nodeRefs.current[node.id]
      
      if (!parentEl || !childEl) return
      
      const parentRect = parentEl.getBoundingClientRect()
      const childRect = childEl.getBoundingClientRect()
      const containerRect = container.getBoundingClientRect()
      
      const parentX = parentRect.left - containerRect.left + parentRect.width / 2 + container.scrollLeft
      const parentY = parentRect.top - containerRect.top + parentRect.height / 2 + container.scrollTop
      const childX = childRect.left - containerRect.left + childRect.width / 2 + container.scrollLeft
      const childY = childRect.top - containerRect.top + childRect.height / 2 + container.scrollTop
      
      // Organic curved line
      const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
      const midX = (parentX + childX) / 2
      const midY = (parentY + childY) / 2
      const curveOffset = node.layer === 1 ? 30 : node.layer === 2 ? 20 : 10
      
      const d = `M ${parentX} ${parentY} 
                 Q ${midX + curveOffset} ${midY - curveOffset} ${childX} ${childY}`
      path.setAttribute('d', d)
      path.setAttribute('stroke', node.layer === 1 ? '#3b82f6' : node.layer === 2 ? '#8b5cf6' : '#a855f7')
      path.setAttribute('stroke-width', node.layer === 1 ? '2.5' : node.layer === 2 ? '2' : '1.5')
      path.setAttribute('fill', 'none')
      path.setAttribute('opacity', '0.4')
      svg.appendChild(path)
    })
    
    const updateLines = () => {
      svg.innerHTML = ''
      seedStructure.forEach(node => {
        if (!node.parentId) return
        
        const parentEl = nodeRefs.current[node.parentId]
        const childEl = nodeRefs.current[node.id]
        
        if (!parentEl || !childEl) return
        
        const parentRect = parentEl.getBoundingClientRect()
        const childRect = childEl.getBoundingClientRect()
        const containerRect = container.getBoundingClientRect()
        
        const parentX = parentRect.left - containerRect.left + parentRect.width / 2 + container.scrollLeft
        const parentY = parentRect.top - containerRect.top + parentRect.height / 2 + container.scrollTop
        const childX = childRect.left - containerRect.left + childRect.width / 2 + container.scrollLeft
        const childY = childRect.top - containerRect.top + childRect.height / 2 + container.scrollTop
        
        const midX = (parentX + childX) / 2
        const midY = (parentY + childY) / 2
        const curveOffset = node.layer === 1 ? 30 : node.layer === 2 ? 20 : 10
        
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path')
        const d = `M ${parentX} ${parentY} 
                   Q ${midX + curveOffset} ${midY - curveOffset} ${childX} ${childY}`
        path.setAttribute('d', d)
        path.setAttribute('stroke', node.layer === 1 ? '#3b82f6' : node.layer === 2 ? '#8b5cf6' : '#a855f7')
        path.setAttribute('stroke-width', node.layer === 1 ? '2.5' : node.layer === 2 ? '2' : '1.5')
        path.setAttribute('fill', 'none')
        path.setAttribute('opacity', '0.4')
        svg.appendChild(path)
      })
    }
    
    container.addEventListener('scroll', updateLines)
    window.addEventListener('resize', updateLines)
    
    return () => {
      container.removeEventListener('scroll', updateLines)
      window.removeEventListener('resize', updateLines)
    }
  }, [seedStructure])
  
  return (
    <div ref={containerRef} className="relative w-full h-full overflow-auto bg-gradient-to-br from-gray-900 via-purple-900/10 to-blue-900/10">
      <svg
        ref={svgRef}
        className="absolute top-0 left-0 pointer-events-none"
        style={{ zIndex: 1 }}
      />
      <div className="relative" style={{ zIndex: 2, minWidth: '2000px', minHeight: '2000px' }}>
        {seedStructure.map(node => {
          const isSelected = selectedNode === node.id
          const nodeFromTimeline = nodes.find(n => n.id === node.id)
          const displayNode = nodeFromTimeline || node
          
          return (
            <div
              key={node.id}
              ref={(el) => { nodeRefs.current[node.id] = el }}
              className="absolute"
              style={{
                left: `${node.x}px`,
                top: `${node.y}px`,
                transform: 'translate(-50%, -50%)'
              }}
            >
              <div
                onClick={() => onNodeSelect(isSelected ? null : node.id)}
                className={`border rounded-lg p-2 cursor-pointer transition-all ${
                  node.layer === 0 
                    ? 'bg-yellow-900/40 border-yellow-600 text-yellow-300 text-lg font-bold w-32'
                    : node.layer === 1
                    ? 'bg-blue-900/40 border-blue-600 text-blue-300 w-28'
                    : node.layer === 2
                    ? 'bg-purple-900/40 border-purple-600 text-purple-300 w-24 text-xs'
                    : getNodeColor(displayNode) + ' w-20 text-xs'
                } ${isSelected ? 'ring-2 ring-white shadow-xl scale-110' : ''}`}
              >
                <div className="flex flex-col items-center gap-1">
                  {node.layer === 0 ? (
                    <>
                      <div className="text-2xl">🌱</div>
                      <div className="text-xs font-semibold">{node.label}</div>
                    </>
                  ) : (
                    <>
                      {getNodeIcon(displayNode)}
                      <div className="text-xs font-semibold text-center">{node.label}</div>
                      {node.layer <= 2 && (
                        <div className="text-xs text-gray-400 text-center line-clamp-1">{node.description}</div>
                      )}
                    </>
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

export const EvolutionExplorerPanel: React.FC = () => {
  const timeline = useMemo(() => buildEvolutionTimeline(), [])
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [filter, setFilter] = useState<'all' | 'completed' | 'in_progress' | 'errors' | 'divergences'>('all')
  const [viewMode, setViewMode] = useState<'timeline' | 'graph' | 'tree' | 'seed' | 'force' | 'sankey' | 'spiral' | 'network' | 'impact' | 'agents' | 'errors' | 'dependencies'>('seed')
  
  const filteredTimeline = useMemo(() => {
    if (filter === 'all') return timeline
    if (filter === 'completed') return timeline.filter(n => n.status === 'completed')
    if (filter === 'in_progress') return timeline.filter(n => n.status === 'in_progress')
    if (filter === 'errors') return timeline.filter(n => n.type === 'error')
    if (filter === 'divergences') return timeline.filter(n => n.type === 'divergence' || n.type === 'new_goal')
    return timeline
  }, [timeline, filter])
  
  const selectedNodeData = selectedNode ? timeline.find(n => n.id === selectedNode) : null
  
  const getNodeColor = (node: EvolutionNode) => {
    if (node.type === 'north_star') return 'text-yellow-400 bg-yellow-900/30 border-yellow-700'
    if (node.type === 'error') return 'text-red-400 bg-red-900/30 border-red-700'
    if (node.type === 'divergence') return 'text-orange-400 bg-orange-900/30 border-orange-700'
    if (node.type === 'new_goal') return 'text-purple-400 bg-purple-900/30 border-purple-700'
    if (node.status === 'completed') return 'text-green-400 bg-green-900/30 border-green-700'
    if (node.status === 'in_progress') return 'text-blue-400 bg-blue-900/30 border-blue-700'
    if (node.status === 'error') return 'text-red-400 bg-red-900/30 border-red-700'
    return 'text-gray-400 bg-gray-800 border-gray-700'
  }
  
  const getNodeIcon = (node: EvolutionNode) => {
    if (node.type === 'north_star') return <Star className="w-4 h-4" />
    if (node.type === 'error') return <XCircle className="w-4 h-4" />
    if (node.type === 'divergence') return <GitBranch className="w-4 h-4" />
    if (node.type === 'new_goal') return <Zap className="w-4 h-4" />
    if (node.status === 'completed') return <CheckCircle className="w-4 h-4" />
    if (node.type === 'objective') return <Target className="w-4 h-4" />
    if (node.type === 'key_result') return <TrendingUp className="w-4 h-4" />
    return <Clock className="w-4 h-4" />
  }
  
  return (
    <div className="h-full flex flex-col bg-gray-900">
      <div className="p-3 border-b border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <div>
            <div className="text-xs font-semibold text-purple-400 mb-1">Evolution Explorer</div>
            <div className="text-xs text-gray-500">Goal Evolution • Errors • Divergences • Timeline</div>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value as any)}
              className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded border border-gray-600"
            >
              <option value="all">All</option>
              <option value="completed">Completed</option>
              <option value="in_progress">In Progress</option>
              <option value="errors">Errors</option>
              <option value="divergences">Divergences</option>
            </select>
            <select
              value={viewMode}
              onChange={(e) => setViewMode(e.target.value as any)}
              className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded border border-gray-600"
            >
              <option value="timeline">Timeline</option>
              <option value="graph">Graph</option>
              <option value="tree">Tree</option>
              <option value="seed">Seed Growth</option>
              <option value="force">Force-Directed</option>
              <option value="sankey">Sankey Flow</option>
              <option value="spiral">Timeline Spiral</option>
              <option value="network">Network Graph</option>
              <option value="impact">Impact Map</option>
              <option value="agents">Agent Network</option>
              <option value="errors">Error Propagation</option>
              <option value="dependencies">Dependency Graph</option>
            </select>
          </div>
        </div>
      </div>
      
      <div className="flex-1 overflow-auto p-4">
        {viewMode === 'timeline' && (
          <div className="space-y-3">
            {filteredTimeline.map((node) => {
              const isSelected = selectedNode === node.id
              const hasChildren = node.children && node.children.length > 0
              
              return (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(isSelected ? null : node.id)}
                  className={`border rounded p-3 cursor-pointer transition-all ${
                    getNodeColor(node)
                  } ${isSelected ? 'ring-2 ring-blue-400' : ''}`}
                >
                  <div className="flex items-start gap-2">
                    <div className="mt-0.5">{getNodeIcon(node)}</div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-semibold">{node.label}</span>
                        <span className="text-xs text-gray-500">{node.timestamp}</span>
                        {node.priority && (
                          <span className="text-xs px-1.5 py-0.5 bg-gray-700 rounded">
                            {node.priority}
                          </span>
                        )}
                        {node.completion !== undefined && (
                          <div className="ml-auto flex items-center gap-2">
                            <div className="w-16 bg-gray-700 rounded-full h-1.5">
                              <div
                                className={`h-1.5 rounded-full ${
                                  node.status === 'completed' ? 'bg-green-500' : 'bg-blue-500'
                                }`}
                                style={{ width: `${node.completion}%` }}
                              />
                            </div>
                            <span className="text-xs text-gray-400">{node.completion}%</span>
                          </div>
                        )}
                      </div>
                      <div className="text-xs text-gray-400 mb-2">{node.description}</div>
                      
                      {node.origin && (
                        <div className="text-xs text-purple-300 mb-1">
                          <ArrowRight className="w-3 h-3 inline mr-1" />
                          Origin: {node.origin}
                        </div>
                      )}
                      
                      {node.errorType && (
                        <div className="text-xs text-red-300 mb-1">
                          <AlertTriangle className="w-3 h-3 inline mr-1" />
                          Error Type: {node.errorType.replace('_', ' ')}
                        </div>
                      )}
                      
                      {node.divergenceReason && (
                        <div className="text-xs text-orange-300 mb-1">
                          <GitBranch className="w-3 h-3 inline mr-1" />
                          Reason: {node.divergenceReason}
                        </div>
                      )}
                      
                      {hasChildren && isSelected && (
                        <div className="mt-2 ml-4 border-l-2 border-gray-600 pl-3 space-y-2">
                          {node.children!.map(childId => {
                            const child = timeline.find(n => n.id === childId)
                            if (!child) return null
                            return (
                              <div
                                key={childId}
                                className={`text-xs p-2 rounded border ${getNodeColor(child)}`}
                              >
                                <div className="font-medium">{child.label}</div>
                                <div className="text-gray-400 mt-1">{child.description}</div>
                                {child.completion !== undefined && (
                                  <div className="mt-1 text-gray-500">
                                    {child.completion}% complete
                                  </div>
                                )}
                              </div>
                            )
                          })}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
        
        {viewMode === 'graph' && (
          <div className="text-xs text-gray-400 text-center py-8">
            Graph visualization coming soon...
            <div className="mt-4 text-gray-500">
              Will show nodes connected by evolution edges
            </div>
          </div>
        )}
        
        {viewMode === 'tree' && (
          <div className="relative w-full h-full overflow-auto">
            <LucidDiagramTree 
              nodes={filteredTimeline}
              selectedNode={selectedNode}
              onNodeSelect={setSelectedNode}
              getNodeColor={getNodeColor}
              getNodeIcon={getNodeIcon}
            />
          </div>
        )}
        
        {viewMode === 'seed' && (
          <div className="relative w-full h-full overflow-auto">
            <SeedGrowthVisualization 
              nodes={filteredTimeline}
              selectedNode={selectedNode}
              onNodeSelect={setSelectedNode}
              getNodeColor={getNodeColor}
              getNodeIcon={getNodeIcon}
            />
          </div>
        )}
        
        {viewMode === 'force' && (
          <div className="relative w-full h-full overflow-auto">
            <ForceDirectedGraph 
              nodes={filteredTimeline}
              selectedNode={selectedNode}
              onNodeSelect={setSelectedNode}
              getNodeColor={getNodeColor}
              getNodeIcon={getNodeIcon}
            />
          </div>
        )}
        
        {/* Additional visualization modes - Placeholders for future implementation */}
        
        {viewMode === 'sankey' && (
          <div className="relative w-full h-full overflow-auto">
            <SankeyFlowDiagram 
              nodes={filteredTimeline}
              selectedNode={selectedNode}
              onNodeSelect={setSelectedNode}
            />
          </div>
        )}
        
        {viewMode === 'errors' && (
          <div className="relative w-full h-full overflow-auto">
            <ErrorPropagationMap 
              nodes={filteredTimeline}
              selectedNode={selectedNode}
              onNodeSelect={setSelectedNode}
              getNodeColor={getNodeColor}
              getNodeIcon={getNodeIcon}
            />
          </div>
        )}
        
        {viewMode === 'spiral' && (
          <div className="relative w-full h-full overflow-auto">
            <TimelineSpiral 
              nodes={filteredTimeline}
              selectedNode={selectedNode}
              onNodeSelect={setSelectedNode}
              getNodeColor={getNodeColor}
              getNodeIcon={getNodeIcon}
            />
          </div>
        )}
        
        {viewMode === 'network' && (
          <div className="text-xs text-gray-400 text-center py-8">
            <div className="text-lg font-semibold text-orange-400 mb-2">Network Graph</div>
            <div className="text-gray-500 mb-4">
              All bidirectional connections • Interactive • Shows complete relationship web
            </div>
            <div className="text-xs text-gray-400">
              Every connection visible • Click nodes to highlight paths
            </div>
          </div>
        )}
        
        {viewMode === 'impact' && (
          <div className="relative w-full h-full overflow-auto">
            <ImpactMap 
              nodes={filteredTimeline}
              selectedNode={selectedNode}
              onNodeSelect={setSelectedNode}
              getNodeColor={getNodeColor}
              getNodeIcon={getNodeIcon}
            />
          </div>
        )}
        
        {viewMode === 'agents' && (
          <div className="relative w-full h-full overflow-auto">
            <AgentCollaborationNetwork 
              nodes={filteredTimeline}
              selectedNode={selectedNode}
              onNodeSelect={setSelectedNode}
              getNodeColor={getNodeColor}
              getNodeIcon={getNodeIcon}
            />
          </div>
        )}
        
        {viewMode === 'errors' && (
          <div className="relative w-full h-full overflow-auto">
            <ErrorPropagationMap 
              nodes={filteredTimeline}
              selectedNode={selectedNode}
              onNodeSelect={setSelectedNode}
              getNodeColor={getNodeColor}
              getNodeIcon={getNodeIcon}
            />
          </div>
        )}
        
        {viewMode === 'dependencies' && (
          <div className="relative w-full h-full overflow-auto">
            <DependencyGraph 
              nodes={filteredTimeline}
              selectedNode={selectedNode}
              onNodeSelect={setSelectedNode}
              getNodeColor={getNodeColor}
              getNodeIcon={getNodeIcon}
            />
          </div>
        )}
      </div>
      
      {selectedNodeData && (
        <div className="border-t border-gray-700 p-3 bg-gray-800">
          <div className="text-xs font-semibold text-blue-400 mb-2">Node Details</div>
          <div className="space-y-1 text-xs text-gray-300">
            <div><span className="text-gray-500">Type:</span> {selectedNodeData.type}</div>
            <div><span className="text-gray-500">Status:</span> {selectedNodeData.status}</div>
            <div><span className="text-gray-500">Timestamp:</span> {selectedNodeData.timestamp}</div>
            {selectedNodeData.priority && (
              <div><span className="text-gray-500">Priority:</span> {selectedNodeData.priority}</div>
            )}
            {selectedNodeData.completion !== undefined && (
              <div><span className="text-gray-500">Completion:</span> {selectedNodeData.completion}%</div>
            )}
            {selectedNodeData.origin && (
              <div><span className="text-gray-500">Origin:</span> {selectedNodeData.origin}</div>
            )}
            {selectedNodeData.errorType && (
              <div><span className="text-gray-500">Error Type:</span> {selectedNodeData.errorType}</div>
            )}
            {selectedNodeData.divergenceReason && (
              <div><span className="text-gray-500">Divergence:</span> {selectedNodeData.divergenceReason}</div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export { EvolutionExplorerPanel }
export { AIMOSStatusPanel } from './AIMOSStatusPanel'
