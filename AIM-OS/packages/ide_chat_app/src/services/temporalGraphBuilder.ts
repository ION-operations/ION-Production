/**
 * Temporal Graph Builder
 * Converts Timeline/Goals/Chains data into React Flow graph structure
 * 
 * Implemented from Temporal Consciousness Visualization T3 Detailed
 */

import { Node, Edge } from 'reactflow';

export interface TemporalGraphData {
    timeline: any[];
    goals: any[];
    chains: any[];
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
                id: entry.entry_id || entry.prompt_id,
                type: 'timelineNode',
                position: this.calculateTemporalPosition(entry, 'timeline', data.timeline.indexOf(entry)),
                data: {
                    label: entry.title || entry.summary || 'Timeline Entry',
                    type: 'timeline',
                    timestamp: entry.timestamp,
                    sequence: entry.sequence || data.timeline.indexOf(entry),
                    content: entry.description || entry.summary,
                    executed_via_chain_id: entry.executed_via_chain_id,
                    quality: entry.quality_metrics || {},
                    confidence: entry.confidence || entry.confidence_metrics || {}
                },
                style: {
                    background: '#3b82f6',  // Blue
                    color: 'white',
                    padding: 10
                }
            });
        }
        
        // === CREATE GOAL NODES (Green) ===
        for (const goal of data.goals) {
            nodes.push({
                id: goal.node_id || goal.goal_id,
                type: 'goalNode',
                position: this.calculateTemporalPosition(goal, 'goal', data.goals.indexOf(goal)),
                data: {
                    label: goal.name || goal.title,
                    type: 'goal',
                    goal_id: goal.goal_id,
                    status: goal.status,
                    progress: goal.progress || 0,
                    related_chain_ids: goal.related_chain_ids || [],
                    completed_via_chain_id: goal.completed_via_chain_id
                },
                style: {
                    background: '#10b981',  // Green
                    color: 'white',
                    padding: 10
                }
            });
        }
        
        // === CREATE CHAIN NODES (Orange) ===
        for (const chain of data.chains) {
            nodes.push({
                id: chain.chain_id,
                type: 'chainNode',
                position: this.calculateTemporalPosition(chain, 'chain', data.chains.indexOf(chain)),
                data: {
                    label: chain.name,
                    type: 'chain',
                    chain_type: chain.chain_type,
                    goal_id: chain.goal_id,
                    node_count: chain.nodes ? chain.nodes.length : 0,
                    produced_timeline_entries: chain.timeline_entry_ids || []
                },
                style: {
                    background: '#f59e0b',  // Orange
                    color: 'white',
                    padding: 10
                }
            });
        }
        
        // === CREATE EDGES ===
        
        // Temporal edges (Timeline → Timeline)
        for (let i = 0; i < data.timeline.length - 1; i++) {
            const currentId = data.timeline[i].entry_id || data.timeline[i].prompt_id;
            const nextId = data.timeline[i + 1].entry_id || data.timeline[i + 1].prompt_id;
            
            edges.push({
                id: `temporal-${i}`,
                source: currentId,
                target: nextId,
                type: 'smoothstep',
                label: 'temporal',
                style: { stroke: '#6b7280', strokeWidth: 2 }  // Gray
            });
        }
        
        // Execution edges (Timeline → Chain via executed_via)
        for (const entry of data.timeline) {
            if (entry.executed_via_chain_id) {
                edges.push({
                    id: `exec-${entry.entry_id || entry.prompt_id}`,
                    source: entry.entry_id || entry.prompt_id,
                    target: entry.executed_via_chain_id,
                    type: 'smoothstep',
                    label: 'executed via',
                    style: { stroke: '#ef4444', strokeDasharray: '5,5', strokeWidth: 2 }  // Red dashed
                });
            }
        }
        
        // Production edges (Chain → Timeline via produced)
        for (const chain of data.chains) {
            for (const timelineId of chain.timeline_entry_ids || []) {
                edges.push({
                    id: `prod-${chain.chain_id}-${timelineId}`,
                    source: chain.chain_id,
                    target: timelineId,
                    type: 'smoothstep',
                    label: 'produced',
                    style: { stroke: '#8b5cf6', strokeWidth: 2 }  // Purple
                });
            }
        }
        
        // Goal-Chain edges (Goal ↔ Chain via related_chain_ids)
        for (const goal of data.goals) {
            for (const chainId of goal.related_chain_ids || []) {
                edges.push({
                    id: `goal-chain-${goal.node_id || goal.goal_id}-${chainId}`,
                    source: goal.node_id || goal.goal_id,
                    target: chainId,
                    type: 'smoothstep',
                    label: 'working on',
                    style: { stroke: '#14b8a6', strokeWidth: 2 }  // Teal
                });
            }
        }
        
        return { nodes, edges };
    }
    
    /**
     * Calculate temporal position (vertical timeline layout)
     */
    private calculateTemporalPosition(item: any, type: 'timeline' | 'goal' | 'chain', index: number): {x: number, y: number} {
        // Vertical layout: Top to bottom = past to future
        // Left column: Timeline
        // Center column: Goals
        // Right column: Chains
        
        const xPositions = {
            timeline: 100,
            goal: 500,
            chain: 900
        };
        
        return {
            x: xPositions[type],
            y: index * 150  // Vertical spacing
        };
    }
}

