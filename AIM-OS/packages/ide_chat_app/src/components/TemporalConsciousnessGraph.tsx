/**
 * Temporal Consciousness Graph Component
 * Interactive Past-Present-Future visualization with Why/What/How queries
 * 
 * Implemented from Temporal Consciousness Visualization T3 Detailed
 */

import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, {
    Node,
    Edge,
    Controls,
    Background,
    MiniMap,
    useNodesState,
    useEdgesState
} from 'reactflow';
import 'reactflow/dist/style.css';

import { TemporalGraphBuilder } from '../services/temporalGraphBuilder';
import { QueryExecutor, QueryResult } from '../../../prompt_chains/executor/query_executor';

export interface TemporalGraphProps {
    enableRealTime?: boolean;
    refreshIntervalSeconds?: number;
    initialLayout?: 'temporal' | 'force' | 'hierarchical';
}

export function TemporalConsciousnessGraph({
    enableRealTime = true,
    refreshIntervalSeconds = 5,
    initialLayout = 'temporal'
}: TemporalGraphProps) {
    // React Flow state
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    
    // UI state
    const [selectedNode, setSelectedNode] = useState<Node | null>(null);
    const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    
    // Services
    const graphBuilder = new TemporalGraphBuilder();
    const queryExecutor = new QueryExecutor();
    
    /**
     * Load graph data from AIM-OS systems
     */
    const loadGraphData = useCallback(async () => {
        setIsLoading(true);
        
        try {
            // Fetch Timeline entries via MCP
            const timelineResponse = await fetch('http://localhost:5001/mcp/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tool: 'get_timeline_entries',
                    arguments: { limit: 100 }
                })
            });
            const timelineData = await timelineResponse.json();
            const timeline = timelineData.result || [];
            
            // Fetch Goals via MCP
            const goalsResponse = await fetch('http://localhost:5001/mcp/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tool: 'query_goal_timeline',
                    arguments: { status: 'all' }
                })
            });
            const goalsData = await goalsResponse.json();
            const goals = goalsData.result || [];
            
            // Fetch Chains (placeholder - would come from chain storage)
            const chains: any[] = [];  // TODO: Implement chain storage/retrieval
            
            // Build graph
            const graph = graphBuilder.buildGraph({ timeline, goals, chains });
            
            setNodes(graph.nodes);
            setEdges(graph.edges);
        } catch (error) {
            console.error('Error loading graph:', error);
        } finally {
            setIsLoading(false);
        }
    }, []);
    
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
    const handleQuery = useCallback(async (queryType: 'why' | 'what' | 'how') => {
        if (!selectedNode) return;
        
        const graph = { nodes, edges };
        let result: QueryResult | null = null;
        
        if (queryType === 'why') {
            result = await queryExecutor.execute_why_query(
                selectedNode.id,
                selectedNode.data.type,
                { timeline: [], goals: [], chains: [] }  // Would pass real graph data
            );
        }
        else if (queryType === 'what') {
            result = await queryExecutor.execute_what_query(
                selectedNode.id,
                selectedNode.data.type,
                { timeline: [], goals: [], chains: [] }
            );
        }
        else if (queryType === 'how') {
            result = await queryExecutor.execute_how_query(
                selectedNode.id,
                selectedNode.data.type,
                { timeline: [], goals: [], chains: [] }
            );
        }
        
        if (result) {
            setQueryResult(result);
            
            // Highlight result nodes
            setNodes(nodes => nodes.map(n => ({
                ...n,
                style: {
                    ...n.style,
                    opacity: result!.path.includes(n.id) ? 1.0 : 0.3
                }
            })));
        }
    }, [selectedNode, nodes, edges]);
    
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
        <div style={{ width: '100%', height: '100vh', position: 'relative' }}>
            {/* React Flow Canvas */}
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onNodeClick={onNodeClick}
                fitView
            >
                <Controls />
                <MiniMap />
                <Background />
            </ReactFlow>
            
            {/* Query Interface */}
            {selectedNode && (
                <div style={{
                    position: 'absolute',
                    top: 20,
                    right: 20,
                    background: 'white',
                    padding: 20,
                    borderRadius: 8,
                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
                }}>
                    <h3 style={{marginTop: 0}}>Query: {selectedNode.data.label}</h3>
                    <div style={{display: 'flex', gap: 10, marginBottom: 15}}>
                        <button onClick={() => handleQuery('why')} style={{flex: 1, padding: '8px 16px', cursor: 'pointer'}}>
                            Why?
                        </button>
                        <button onClick={() => handleQuery('what')} style={{flex: 1, padding: '8px 16px', cursor: 'pointer'}}>
                            What?
                        </button>
                        <button onClick={() => handleQuery('how')} style={{flex: 1, padding: '8px 16px', cursor: 'pointer'}}>
                            How?
                        </button>
                    </div>
                    
                    {/* Query Result */}
                    {queryResult && (
                        <div>
                            <h4>{queryResult.query_type.toUpperCase()} Query Result:</h4>
                            <p>{queryResult.explanation}</p>
                            <div>
                                <strong>Path:</strong>
                                <ul style={{margin: '5px 0', paddingLeft: 20}}>
                                    {queryResult.path.map((id, i) => (
                                        <li key={i}>{id}</li>
                                    ))}
                                </ul>
                            </div>
                            <div style={{marginTop: 10}}>
                                <strong>Nodes Found:</strong> {queryResult.result_nodes.length}
                            </div>
                        </div>
                    )}
                    
                    {/* Node Details */}
                    <div style={{marginTop: 15, paddingTop: 15, borderTop: '1px solid #ddd'}}>
                        <h4>Node Details:</h4>
                        <div><strong>Type:</strong> {selectedNode.data.type}</div>
                        {selectedNode.data.confidence !== undefined && (
                            <div><strong>Confidence:</strong> {selectedNode.data.confidence}</div>
                        )}
                        {selectedNode.data.progress !== undefined && (
                            <div><strong>Progress:</strong> {(selectedNode.data.progress * 100).toFixed(0)}%</div>
                        )}
                        {selectedNode.data.status && (
                            <div><strong>Status:</strong> {selectedNode.data.status}</div>
                        )}
                    </div>
                </div>
            )}
            
            {/* Loading Overlay */}
            {isLoading && (
                <div style={{
                    position: 'absolute',
                    top: 20,
                    left: 20,
                    background: 'rgba(0,0,0,0.7)',
                    color: 'white',
                    padding: '10px 20px',
                    borderRadius: 4
                }}>
                    Loading temporal consciousness...
                </div>
            )}
        </div>
    );
}

