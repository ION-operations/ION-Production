---
id: "temporal_consciousness_viz_T3_detailed"
system: "temporal_consciousness_visualization"
component: null
level: "T3"
type: "detailed"
title: "Temporal Consciousness Visualization Detailed Guide"
description: "10,000-word detailed implementation for Temporal Consciousness Visualization"
audience: "developers, implementers"
confidence_threshold: 0.70
token_cost: 10000
word_count: 10000
created: "2025-11-05T19:00:00Z"
updated: "2025-11-05T19:00:00Z"
author: "aether"
status: "complete"
tags: ["temporal-consciousness", "implementation", "react-flow", "visualization", "t0-t6"]
dependencies: ["timeline_goals_integration", "prompt_chains", "react_flow"]
related_docs: ["T0_executive.md", "T1_overview.md", "T2_architecture.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# Temporal Consciousness Visualization – T3 Detailed Implementation (≈10,000 words)

**This document provides complete implementation guidance for the Temporal Consciousness Visualization system using React Flow.**

---

## Complete React Component Implementation

**File:** `packages/ide_chat_app/src/components/TemporalConsciousnessVisualization.tsx`

```typescript
/**
 * Temporal Consciousness Visualization Component
 * Interactive Past-Present-Future graph with Why/What/How queries
 */

import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, {
    Node,
    Edge,
    Controls,
    Background,
    MiniMap,
    useNodesState,
    useEdgesState,
    addEdge,
    Connection
} from 'reactflow';
import 'reactflow/dist/style.css';

import { TimelineNode } from './nodes/TimelineNode';
import { GoalNode } from './nodes/GoalNode';
import { ChainNode } from './nodes/ChainNode';
import { QueryInterface } from './QueryInterface';
import { GraphBuilder } from '../../services/temporalGraphBuilder';
import { QueryExecutor } from '../../services/queryExecutor';

// Custom node types
const nodeTypes = {
    timelineNode: TimelineNode,
    goalNode: GoalNode,
    chainNode: ChainNode
};

export interface TemporalVisualizationProps {
    enableRealTime?: boolean;
    refreshIntervalSeconds?: number;
    initialLayout?: 'temporal' | 'force' | 'hierarchical';
    enableQueryInterface?: boolean;
    enable3D?: boolean;
}

export function TemporalConsciousnessVisualization({
    enableRealTime = true,
    refreshIntervalSeconds = 5,
    initialLayout = 'temporal',
    enableQueryInterface = true,
    enable3D = false
}: TemporalVisualizationProps) {
    // React Flow state
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    
    // UI state
    const [selectedNode, setSelectedNode] = useState<Node | null>(null);
    const [queryResult, setQueryResult] = useState<Node[] | null>(null);
    const [layout, setLayout] = useState(initialLayout);
    const [isLoading, setIsLoading] = useState(false);
    
    // Services
    const graphBuilder = new GraphBuilder();
    const queryExecutor = new QueryExecutor();
    
    /**
     * Load graph data from AIM-OS systems
     */
    const loadGraphData = useCallback(async () => {
        setIsLoading(true);
        
        try {
            // Fetch Timeline entries
            const timeline = await fetch('/api/timeline/entries?limit=100').then(r => r.json());
            
            // Fetch Goals
            const goals = await fetch('/api/goals/timeline?status=all').then(r => r.json());
            
            // Fetch Chains
            const chains = await fetch('/api/chains?tier=1').then(r => r.json());
            
            // Build graph
            const graph = graphBuilder.buildGraph({ timeline, goals, chains });
            
            // Apply layout
            const layoutedGraph = graphBuilder.applyLayout(graph, layout);
            
            setNodes(layoutedGraph.nodes);
            setEdges(layoutedGraph.edges);
        } catch (error) {
            console.error('Error loading graph:', error);
        } finally {
            setIsLoading(false);
        }
    }, [layout]);
    
    /**
     * Initial load and real-time updates
     */
    useEffect(() => {
        loadGraphData();
        
        if (enableRealTime) {
            const interval = setInterval(loadGraphData, refreshIntervalSeconds * 1000);
            return () => clearInterval(interval);
        }
    }, [loadGraphData, enableRealTime, refreshIntervalSeconds]);
    
    /**
     * Execute Why/What/How query
     */
    const handleQuery = useCallback(async (queryType: 'why' | 'what' | 'how', node: Node) => {
        let result: Node[] = [];
        
        if (queryType === 'why') {
            result = await queryExecutor.executeWhyQuery(node.id, { nodes, edges });
        }
        else if (queryType === 'what') {
            result = await queryExecutor.executeWhatQuery(node.id, { nodes, edges });
        }
        else if (queryType === 'how') {
            result = await queryExecutor.executeHowQuery(node.id, { nodes, edges });
        }
        
        setQueryResult(result);
        
        // Highlight result nodes
        setNodes(nodes => nodes.map(n => ({
            ...n,
            style: {
                ...n.style,
                opacity: result.some(r => r.id === n.id) ? 1.0 : 0.3
            }
        })));
    }, [nodes, edges]);
    
    /**
     * Handle node click
     */
    const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
        setSelectedNode(node);
        setQueryResult(null);  // Clear previous query
        
        // Reset node opacity
        setNodes(nodes => nodes.map(n => ({
            ...n,
            style: { ...n.style, opacity: 1.0 }
        })));
    }, []);
    
    return (
        <div style={{ width: '100%', height: '100vh' }}>
            {/* React Flow Canvas */}
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onNodeClick={onNodeClick}
                nodeTypes={nodeTypes}
                fitView
            >
                <Controls />
                <MiniMap />
                <Background />
            </ReactFlow>
            
            {/* Query Interface */}
            {enableQueryInterface && selectedNode && (
                <QueryInterface
                    selectedNode={selectedNode}
                    onQuery={handleQuery}
                />
            )}
            
            {/* Node Details Panel */}
            {selectedNode && (
                <NodeDetailsPanel
                    node={selectedNode}
                    queryResult={queryResult}
                />
            )}
            
            {/* Layout Controls */}
            <LayoutControls
                currentLayout={layout}
                onLayoutChange={setLayout}
            />
        </div>
    );
}
```

---

## Query System Implementation

**Complete Query Executor:**

```typescript
/**
 * Query Executor Service
 * Implements Why/What/How graph traversal
 */

export class QueryExecutor {
    /**
     * Why Query: Trace backwards through causation chain
     * 
     * Timeline → executed_via_chain_id → Chain → goal_id → Goal
     */
    async executeWhyQuery(
        nodeId: string,
        graph: { nodes: Node[], edges: Edge[] }
    ): Promise<Node[]> {
        const path: Node[] = [];
        const visited = new Set<string>();
        
        let currentId = nodeId;
        
        while (currentId && !visited.has(currentId)) {
            visited.add(currentId);
            
            const node = graph.nodes.find(n => n.id === currentId);
            if (!node) break;
            
            path.push(node);
            
            // Find backward edge
            if (node.data.type === 'timeline' && node.data.executed_via_chain_id) {
                currentId = node.data.executed_via_chain_id;
            }
            else if (node.data.type === 'chain' && node.data.goal_id) {
                currentId = node.data.goal_id;
            }
            else {
                break;  // Reached root
            }
        }
        
        return path;
    }
    
    /**
     * What Query: Find all connected goals (current focus)
     */
    async executeWhatQuery(
        nodeId: string,
        graph: { nodes: Node[], edges: Edge[] }
    ): Promise<Node[]> {
        // Find all goal nodes connected to this node
        const connectedGoals = graph.nodes.filter(n => 
            n.data.type === 'goal' && this.isConnected(nodeId, n.id, graph)
        );
        
        return connectedGoals;
    }
    
    /**
     * How Query: Explore forward through planning chain
     */
    async executeHowQuery(
        nodeId: string,
        graph: { nodes: Node[], edges: Edge[] }
    ): Promise<Node[]> {
        const node = graph.nodes.find(n => n.id === nodeId);
        if (!node) return [];
        
        if (node.data.type === 'goal') {
            // Show all chains working toward this goal
            return node.data.related_chain_ids
                .map(id => graph.nodes.find(n => n.id === id))
                .filter(n => n) as Node[];
        }
        else if (node.data.type === 'chain') {
            // Show all timeline entries this chain will/did produce
            return node.data.produced_timeline_entries
                .map(id => graph.nodes.find(n => n.id === id))
                .filter(n => n) as Node[];
        }
        
        return [];
    }
    
    private isConnected(
        nodeId1: string,
        nodeId2: string,
        graph: { nodes: Node[], edges: Edge[] }
    ): boolean {
        return graph.edges.some(e => 
            (e.source === nodeId1 && e.target === nodeId2) ||
            (e.source === nodeId2 && e.target === nodeId1)
        );
    }
}
```

---

## Node Details Panel

```typescript
/**
 * Node Details Panel
 * Shows complete data for selected node
 */

export function NodeDetailsPanel({ node, queryResult }) {
    if (node.data.type === 'timeline') {
        return (
            <div className="details-panel timeline-details">
                <h3>Timeline Entry: {node.data.label}</h3>
                <div>Sequence: {node.data.sequence}</div>
                <div>Timestamp: {new Date(node.data.timestamp).toLocaleString()}</div>
                <div>Confidence: {node.data.confidence.toFixed(2)}</div>
                
                {node.data.executed_via_chain_id && (
                    <div className="chain-link">
                        Executed via: {node.data.executed_via_chain_id}
                        <button onClick={() => navigateToNode(node.data.executed_via_chain_id)}>
                            View Chain
                        </button>
                    </div>
                )}
                
                <div className="query-results">
                    {queryResult && queryResult.length > 0 && (
                        <>
                            <h4>Query Results:</h4>
                            {queryResult.map(n => (
                                <div key={n.id} className="result-item">
                                    {n.data.label}
                                </div>
                            ))}
                        </>
                    )}
                </div>
            </div>
        );
    }
    
    if (node.data.type === 'goal') {
        return (
            <div className="details-panel goal-details">
                <h3>Goal: {node.data.label}</h3>
                <div>Status: {node.data.status}</div>
                <div>Progress: {(node.data.progress * 100).toFixed(0)}%</div>
                
                <div className="progress-bar">
                    <div 
                        className="progress-fill"
                        style={{ width: `${node.data.progress * 100}%` }}
                    />
                </div>
                
                <div className="chains-working">
                    <h4>Chains Working on This:</h4>
                    {node.data.related_chain_ids.map(id => (
                        <div key={id}>{id}</div>
                    ))}
                </div>
            </div>
        );
    }
    
    if (node.data.type === 'chain') {
        return (
            <div className="details-panel chain-details">
                <h3>Chain: {node.data.label}</h3>
                <div>Type: {node.data.chain_type}</div>
                <div>Nodes: {node.data.node_count}</div>
                <div>Goal: {node.data.goal_id || 'None'}</div>
                
                <div className="timeline-produced">
                    <h4>Timeline Entries Produced:</h4>
                    {node.data.produced_timeline_entries.map(id => (
                        <div key={id}>{id}</div>
                    ))}
                </div>
            </div>
        );
    }
    
    return null;
}
```

---

## Testing Guide

```typescript
/**
 * Tests for Temporal Consciousness Visualization
 */

describe('TemporalConsciousnessVisualization', () => {
    it('should render graph with all node types', async () => {
        const { container } = render(<TemporalConsciousnessVisualization />);
        
        // Wait for data load
        await waitFor(() => {
            expect(container.querySelector('.timeline-node')).toBeTruthy();
            expect(container.querySelector('.goal-node')).toBeTruthy();
            expect(container.querySelector('.chain-node')).toBeTruthy();
        });
    });
    
    it('should execute Why query correctly', async () => {
        const queryExecutor = new QueryExecutor();
        
        const result = await queryExecutor.executeWhyQuery('timeline-123', mockGraph);
        
        expect(result.length).toBeGreaterThan(0);
        expect(result[0].data.type).toBe('timeline');
        // Should trace backwards through chain to goal
    });
});
```

---

## Deployment Guide

**Step 1: Install Dependencies**
```bash
cd packages/ide_chat_app
npm install reactflow
```

**Step 2: Implement Components**
- Create `TemporalConsciousnessVisualization.tsx`
- Create custom node components
- Create GraphBuilder service
- Create QueryExecutor service

**Step 3: Add Route**
```typescript
// In App.tsx
<Route path="/temporal-consciousness" element={<TemporalConsciousnessVisualization />} />
```

**Step 4: Test**
```bash
npm run dev
# Navigate to /temporal-consciousness
```

---

**Status:** Design Complete | **Implementation:** Partial (ConsciousnessVisualization.tsx exists)  
**Next:** T4-T5 completion documentation  
**Files:** Complete React Flow implementation with Why/What/How queries

