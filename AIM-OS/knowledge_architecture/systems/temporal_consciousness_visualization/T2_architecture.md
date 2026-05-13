---
id: "temporal_consciousness_viz_T2_architecture"
system: "temporal_consciousness_visualization"
component: null
level: "T2"
type: "architecture"
title: "Temporal Consciousness Visualization Architecture"
description: "2000-word architecture for Temporal Consciousness Visualization"
audience: "developers, architects"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-11-05T18:45:00Z"
updated: "2025-11-05T18:45:00Z"
author: "aether"
status: "complete"
tags: ["temporal-consciousness", "architecture", "react-flow", "graph-design", "t0-t6"]
dependencies: ["timeline_goals_integration", "prompt_chains", "react_flow"]
related_docs: ["temporal_consciousness_viz_T0_executive", "temporal_consciousness_viz_T1_overview"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Temporal Consciousness Visualization – T2 Architecture (≈2,000 words)

## 🏗️ **COMPLETE SYSTEM ARCHITECTURE**

### **The Vision**

**Create an interactive graph visualization showing Past-Present-Future consciousness** through bidirectional connections between Timeline (past), Goals (present), and Chains (future).

**Core Principle:** Every node knows what it came from and what it produced, enabling complete "Why/What/How" exploration through visual graph traversal.

### **System Overview Diagram**

```
┌────────────────────────────────────────────────────────────────────┐
│        TEMPORAL CONSCIOUSNESS VISUALIZATION ARCHITECTURE            │
├────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │         LAYER 1: DATA LAYER (AIM-OS Integration)             │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │  │
│  │  │  Timeline    │  │    Goals     │  │   Chains     │       │  │
│  │  │  Context     │  │   Timeline   │  │  Executor    │       │  │
│  │  │  System      │  │  Integration │  │              │       │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘       │  │
│  │         ↓                 ↓                  ↓                │  │
│  │     Timeline         GoalTimelineNode    PromptChain         │  │
│  │     Entries          with chains          with goals         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                         ↓ Data Fetching                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │       LAYER 2: GRAPH CONSTRUCTION (TypeScript)               │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  GraphBuilder                                           │  │  │
│  │  │  - Fetch Timeline/Goals/Chains from APIs               │  │  │
│  │  │  - Build unified graph structure                       │  │  │
│  │  │  - Create React Flow nodes from data                   │  │  │
│  │  │  - Create React Flow edges from relationships          │  │  │
│  │  │  - Apply layout algorithm (temporal/force/hierarchical)│  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                         ↓ Graph Data                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │        LAYER 3: VISUALIZATION (React Flow)                   │  │
│  │  ┌────────────────────────────────────────────────────────┐  │  │
│  │  │  TemporalConsciousnessVisualization Component          │  │  │
│  │  │  - React Flow canvas                                   │  │  │
│  │  │  - Custom node components (Timeline/Goal/Chain nodes)  │  │  │
│  │  │  - Custom edge components (labeled, colored)           │  │  │
│  │  │  - Interactive controls (zoom, pan, filter)            │  │  │
│  │  │  - Query interface (Why/What/How buttons)              │  │  │
│  │  │  - Node details panel                                  │  │  │
│  │  └────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└────────────────────────────────────────────────────────────────────┘
```

---

## 📦 **CORE COMPONENTS**

### **1. GraphBuilder (Data → React Flow Conversion)**

**File:** `packages/ide_chat_app/src/services/temporalGraphBuilder.ts`

```typescript
/**
 * Temporal Graph Builder
 * Converts Timeline/Goals/Chains data into React Flow graph structure
 */

import { Node, Edge } from 'reactflow';

export interface TemporalGraphData {
    timeline: TimelineEntry[];
    goals: GoalTimelineNode[];
    chains: PromptChain[];
}

export class TemporalGraphBuilder {
    /**
     * Build complete React Flow graph from temporal data
     * 
     * Creates 3 node types (Timeline/Goal/Chain) with bidirectional edges
     */
    buildGraph(data: TemporalGraphData): {nodes: Node[], edges: Edge[]} {
        const nodes: Node[] = [];
        const edges: Edge[] = [];
        
        // === CREATE TIMELINE NODES (Blue) ===
        for (const entry of data.timeline) {
            nodes.push({
                id: entry.entry_id,
                type: 'timelineNode',
                position: this.calculatePosition(entry, 'timeline'),
                data: {
                    label: entry.title,
                    type: 'timeline',
                    timestamp: entry.timestamp,
                    sequence: entry.sequence,
                    content: entry.description,
                    executed_via_chain_id: entry.executed_via_chain_id,
                    quality: entry.quality_metrics,
                    confidence: entry.confidence
                },
                style: {
                    background: '#3b82f6',  // Blue
                    color: 'white'
                }
            });
        }
        
        // === CREATE GOAL NODES (Green) ===
        for (const goal of data.goals) {
            nodes.push({
                id: goal.node_id,
                type: 'goalNode',
                position: this.calculatePosition(goal, 'goal'),
                data: {
                    label: goal.name,
                    type: 'goal',
                    goal_id: goal.goal_id,
                    status: goal.status,
                    progress: goal.progress,
                    related_chain_ids: goal.related_chain_ids,
                    completed_via_chain_id: goal.completed_via_chain_id
                },
                style: {
                    background: '#10b981',  // Green
                    color: 'white'
                }
            });
        }
        
        // === CREATE CHAIN NODES (Orange) ===
        for (const chain of data.chains) {
            nodes.push({
                id: chain.chain_id,
                type: 'chainNode',
                position: this.calculatePosition(chain, 'chain'),
                data: {
                    label: chain.name,
                    type: 'chain',
                    chain_type: chain.chain_type,
                    goal_id: chain.goal_id,
                    node_count: chain.nodes.length,
                    produced_timeline_entries: chain.timeline_entry_ids
                },
                style: {
                    background: '#f59e0b',  // Orange
                    color: 'white'
                }
            });
        }
        
        // === CREATE EDGES ===
        // Temporal edges (Timeline → Timeline)
        for (let i = 0; i < data.timeline.length - 1; i++) {
            edges.push({
                id: `temporal-${i}`,
                source: data.timeline[i].entry_id,
                target: data.timeline[i + 1].entry_id,
                type: 'smoothstep',
                label: 'temporal',
                style: { stroke: '#6b7280' }  // Gray
            });
        }
        
        // Execution edges (Timeline → Chain via executed_via)
        for (const entry of data.timeline) {
            if (entry.executed_via_chain_id) {
                edges.push({
                    id: `exec-${entry.entry_id}`,
                    source: entry.entry_id,
                    target: entry.executed_via_chain_id,
                    type: 'smoothstep',
                    label: 'executed via',
                    style: { stroke: '#ef4444', strokeDasharray: '5,5' }  // Red dashed
                });
            }
        }
        
        // Production edges (Chain → Timeline via produced)
        for (const chain of data.chains) {
            for (const timelineId of chain.timeline_entry_ids) {
                edges.push({
                    id: `prod-${chain.chain_id}-${timelineId}`,
                    source: chain.chain_id,
                    target: timelineId,
                    type: 'smoothstep',
                    label: 'produced',
                    style: { stroke: '#8b5cf6' }  // Purple
                });
            }
        }
        
        // Goal-Chain edges (Goal ↔ Chain via related_chain_ids)
        for (const goal of data.goals) {
            for (const chainId of goal.related_chain_ids) {
                edges.push({
                    id: `goal-chain-${goal.node_id}-${chainId}`,
                    source: goal.node_id,
                    target: chainId,
                    type: 'smoothstep',
                    label: 'working on',
                    style: { stroke: '#14b8a6' }  // Teal
                });
            }
        }
        
        return { nodes, edges };
    }
}
```

---

### **2. Custom Node Components**

**TimelineNode Component:**

```typescript
/**
 * Custom Timeline Node for React Flow
 * Displays timeline entry with metadata
 */

import { Handle, Position } from 'reactflow';

interface TimelineNodeData {
    label: string;
    timestamp: Date;
    sequence: number;
    executed_via_chain_id?: string;
    confidence: number;
}

export function TimelineNode({ data }: { data: TimelineNodeData }) {
    return (
        <div className="timeline-node">
            <Handle type="target" position={Position.Top} />
            
            <div className="node-header">
                <span className="node-icon">📅</span>
                <span className="node-label">{data.label}</span>
            </div>
            
            <div className="node-body">
                <div>Seq: {data.sequence}</div>
                <div>Conf: {data.confidence.toFixed(2)}</div>
                {data.executed_via_chain_id && (
                    <div className="chain-link">
                        via {data.executed_via_chain_id.slice(0, 8)}...
                    </div>
                )}
            </div>
            
            <Handle type="source" position={Position.Bottom} />
        </div>
    );
}
```

**GoalNode Component:**

```typescript
/**
 * Custom Goal Node for React Flow
 */

export function GoalNode({ data }: { data: GoalNodeData }) {
    return (
        <div className="goal-node">
            <Handle type="target" position={Position.Left} />
            
            <div className="node-header">
                <span className="node-icon">🎯</span>
                <span className="node-label">{data.label}</span>
            </div>
            
            <div className="node-body">
                <div className="progress-bar">
                    <div 
                        className="progress-fill" 
                        style={{width: `${data.progress * 100}%`}}
                    />
                </div>
                <div>{data.status} - {(data.progress * 100).toFixed(0)}%</div>
                <div>{data.related_chain_ids.length} chains working</div>
            </div>
            
            <Handle type="source" position={Position.Right} />
        </div>
    );
}
```

**ChainNode Component:**

```typescript
/**
 * Custom Chain Node for React Flow
 */

export function ChainNode({ data }: { data: ChainNodeData }) {
    return (
        <div className="chain-node">
            <Handle type="target" position={Position.Top} />
            
            <div className="node-header">
                <span className="node-icon">⛓️</span>
                <span className="node-label">{data.label}</span>
            </div>
            
            <div className="node-body">
                <div>Type: {data.chain_type}</div>
                <div>{data.node_count} nodes</div>
                {data.goal_id && (
                    <div className="goal-link">
                        → Goal {data.goal_id}
                    </div>
                )}
            </div>
            
            <Handle type="source" position={Position.Bottom} />
        </div>
    );
}
```

---

### **3. Query Interface**

**Why/What/How Query Buttons:**

```typescript
/**
 * Query Interface Component
 * Enables "Why/What/How" exploration of graph
 */

export function QueryInterface({ selectedNode, onQuery }) {
    return (
        <div className="query-interface">
            <button onClick={() => onQuery('why', selectedNode)}>
                Why? (Trace Backwards)
            </button>
            <button onClick={() => onQuery('what', selectedNode)}>
                What? (Current State)
            </button>
            <button onClick={() => onQuery('how', selectedNode)}>
                How? (Future Plans)
            </button>
        </div>
    );
}

/**
 * Query Executor
 * Implements graph traversal for queries
 */

class QueryExecutor {
    /**
     * Why Query: Trace backwards to understand causation
     * 
     * For Timeline node: Follow executed_via_chain_id
     * For Goal node: Follow creation context
     * For Chain node: Follow parent_chain_id
     */
    async executeWhyQuery(nodeId: string, graph: Graph): Promise<Node[]> {
        const path: Node[] = [];
        let currentNode = graph.getNode(nodeId);
        
        while (currentNode) {
            path.push(currentNode);
            
            if (currentNode.type === 'timeline') {
                // Follow executed_via_chain_id
                currentNode = graph.getNode(currentNode.data.executed_via_chain_id);
            }
            else if (currentNode.type === 'chain') {
                // Follow goal_id
                currentNode = graph.getNode(currentNode.data.goal_id);
            }
            else if (currentNode.type === 'goal') {
                // Reached root (goal created the context)
                break;
            }
        }
        
        return path;
    }
    
    /**
     * What Query: Show current state
     * 
     * For any node: Show connected goals (what's the current focus?)
     */
    async executeWhatQuery(nodeId: string, graph: Graph): Promise<Node[]> {
        // Find all connected goal nodes
        return graph.findConnectedNodes(nodeId, 'goal');
    }
    
    /**
     * How Query: Explore future plans
     * 
     * For Goal node: Show related_chain_ids (what chains will achieve this?)
     * For Chain node: Show produced_timeline_entries (what will this create?)
     */
    async executeHowQuery(nodeId: string, graph: Graph): Promise<Node[]> {
        const node = graph.getNode(nodeId);
        
        if (node.type === 'goal') {
            // Show chains working toward this goal
            return node.data.related_chain_ids.map(id => graph.getNode(id));
        }
        else if (node.type === 'chain') {
            // Show timeline entries this will produce
            return node.data.produced_timeline_entries.map(id => graph.getNode(id));
        }
        
        return [];
    }
}
```

---

## 🎨 **LAYOUT ALGORITHMS**

### **Layout 1: Temporal (Vertical Timeline)**

**Purpose:** Show chronological evolution (top to bottom = past to future)

```typescript
function calculateTemporalLayout(nodes: Node[]): Node[] {
    // Sort by timestamp/sequence
    const sortedNodes = nodes.sort((a, b) => {
        if (a.data.type === 'timeline' && b.data.type === 'timeline') {
            return a.data.sequence - b.data.sequence;
        }
        return a.data.timestamp - b.data.timestamp;
    });
    
    // Position vertically
    return sortedNodes.map((node, index) => ({
        ...node,
        position: {
            x: node.data.type === 'timeline' ? 300 :
               node.data.type === 'goal' ? 600 :
               900,  // Chains on right
            y: index * 150  // Vertical spacing
        }
    }));
}
```

**Visual:**
```
Timeline (left) | Goals (center) | Chains (right)
     T1         →      G1        →      C1
     ↓                 ↓                ↓
     T2         →      G2        →      C2
     ↓                                  ↓
     T3                                 C3
```

### **Layout 2: Force-Directed (Organic)**

**Purpose:** Show relationships naturally (connected nodes attract)

```typescript
import { useNodesState, useEdgesState } from 'reactflow';
import dagre from 'dagre';

function calculateForceLayout(nodes: Node[], edges: Edge[]): Node[] {
    const g = new dagre.graphlib.Graph();
    g.setDefaultEdgeLabel(() => ({}));
    
    // Add nodes
    nodes.forEach(node => {
        g.setNode(node.id, { width: 150, height: 80 });
    });
    
    // Add edges
    edges.forEach(edge => {
        g.setEdge(edge.source, edge.target);
    });
    
    // Run layout
    dagre.layout(g);
    
    // Apply positions
    return nodes.map(node => ({
        ...node,
        position: g.node(node.id)
    }));
}
```

### **Layout 3: Hierarchical (Tree)**

**Purpose:** Show system hierarchy (North Star → Systems → Components)

```typescript
function calculateHierarchicalLayout(nodes: Node[], edges: Edge[]): Node[] {
    // Group by hierarchy level
    const levels = groupByHierarchy(nodes, edges);
    
    // Position by level
    return nodes.map(node => ({
        ...node,
        position: {
            x: (node.data.hierarchyIndex * 200),
            y: (node.data.hierarchyLevel * 150)
        }
    }));
}
```

---

## 🔗 **INTEGRATION ARCHITECTURE**

### **Timeline Integration**

```typescript
// Fetch timeline entries with chain connections
async function fetchTimelineData(): Promise<TimelineEntry[]> {
    const entries = await mcpClient.callTool('get_timeline_entries', {
        limit: 100,
        include_chain_refs: true  // Include executed_via_chain_id
    });
    
    return entries.map(e => ({
        ...e,
        // Ensure executed_via_chain_id preserved
        executed_via_chain_id: e.executed_via_chain_id
    }));
}
```

### **Goals Integration**

```typescript
// Fetch goals with chain connections
async function fetchGoalsData(): Promise<GoalTimelineNode[]> {
    const goals = await mcpClient.callTool('query_goal_timeline', {
        status: 'all',
        include_chain_refs: true  // Include related_chain_ids
    });
    
    return goals;
}
```

### **Chains Integration**

```typescript
// Fetch chains with timeline connections
async function fetchChainsData(): Promise<PromptChain[]> {
    // Query chains from storage
    const chains = await fetch('/api/chains').then(r => r.json());
    
    return chains.map(c => ({
        ...c,
        // Ensure timeline_entry_ids preserved
        timeline_entry_ids: c.timeline_entry_ids || []
    }));
}
```

---

## 🎯 **IMPLEMENTATION PRIORITIES**

**Phase 1: Basic Graph (Week 1)**
1. GraphBuilder (fetch data, build React Flow nodes/edges)
2. Basic React Flow canvas
3. 3 custom node types (Timeline/Goal/Chain)
4. Temporal layout

**Phase 2: Interactivity (Week 1-2)**
5. Node click → Details panel
6. Why/What/How query buttons
7. Graph traversal for queries
8. Filter controls (by type, status, date)

**Phase 3: Advanced Features (Week 2-3)**
9. Force-directed layout
10. Real-time updates (poll for new data)
11. Search functionality
12. Export (PNG, JSON)

**Phase 4: Polish (Week 3-4)**
13. Animations
14. 3D mode (optional)
15. Performance optimization
16. Complete testing

---

**Status:** Design Complete | **Implementation:** Partial (ConsciousnessVisualization.tsx exists)  
**Next:** T3 Detailed with complete React component implementation guide  
**Impact:** Complete visibility into AI temporal consciousness evolution

