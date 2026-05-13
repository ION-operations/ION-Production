"""
Temporal Consciousness Graph Traversal

Implements Why/What/How queries for exploring Past-Present-Future through bidirectional connections.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

from .models import (
    EnhancedTimelineEntry,
    EnhancedGoalTimelineNode,
    EnhancedPromptChain,
    TemporalGraph
)

logger = logging.getLogger(__name__)


@dataclass
class ProvenanceResult:
    """Result of a provenance query"""
    query_type: str  # "why" | "what" | "how"
    start_node_id: str
    result_nodes: List[Dict[str, Any]]
    path: List[str]
    explanation: str
    confidence: float = 1.0


class TemporalGraphTraverser:
    """
    Traverses temporal consciousness graph to answer Why/What/How queries.
    
    Graph Structure:
    - Timeline nodes (past) connect to Chain nodes via executed_via_chain_id
    - Chain nodes (future) connect to Goal nodes via related_goal_ids
    - Chain nodes connect to Timeline nodes via timeline_entry_ids (produced)
    - Goal nodes connect to Chain nodes via planned_chain_ids / executed_chain_ids
    """
    
    def __init__(self, graph: TemporalGraph):
        """Initialize traverser with graph data"""
        self.graph = graph
        
        # Build lookup maps for fast access
        self.timeline_map: Dict[str, EnhancedTimelineEntry] = {
            entry.entry_id: entry for entry in graph.timeline_entries
        }
        self.goal_map: Dict[str, EnhancedGoalTimelineNode] = {
            goal.goal_id: goal for goal in graph.goals
        }
        self.chain_map: Dict[str, EnhancedPromptChain] = {
            chain.chain_id: chain for chain in graph.chains
        }
    
    def explain_timeline_entry(self, entry_id: str) -> ProvenanceResult:
        """
        Answers: "Why did this happen?"
        
        Returns:
        - Which chain executed it
        - Which goals it served
        - Parent entries that led to it
        - Complete provenance chain
        """
        entry = self.timeline_map.get(entry_id)
        if not entry:
            return ProvenanceResult(
                query_type="why",
                start_node_id=entry_id,
                result_nodes=[],
                path=[],
                explanation=f"Timeline entry {entry_id} not found",
                confidence=0.0
            )
        
        result_nodes: List[Dict[str, Any]] = []
        path: List[str] = [entry_id]
        
        # Get chain that executed it
        chain = None
        if entry.executed_via_chain_id:
            chain = self.chain_map.get(entry.executed_via_chain_id)
            if chain:
                result_nodes.append({
                    "type": "chain",
                    "id": chain.chain_id,
                    "name": chain.name,
                    "description": chain.description
                })
                path.append(chain.chain_id)
        
        # Get goals it serves
        goals = []
        for goal_id in entry.related_goal_ids:
            goal = self.goal_map.get(goal_id)
            if goal:
                goals.append(goal)
                result_nodes.append({
                    "type": "goal",
                    "id": goal.goal_id,
                    "name": goal.name,
                    "status": goal.status.value,
                    "progress": goal.progress_percentage
                })
                path.append(goal_id)
        
        # Get parent entries (recursive)
        parent_chain = []
        for parent_id in entry.parent_entry_ids:
            parent_entry = self.timeline_map.get(parent_id)
            if parent_entry:
                parent_chain.append(parent_entry)
                result_nodes.append({
                    "type": "timeline",
                    "id": parent_entry.entry_id,
                    "content": parent_entry.content[:100],
                    "timestamp": parent_entry.timestamp.isoformat()
                })
                path.append(parent_id)
        
        # Generate explanation
        explanation_parts = [f"Timeline entry '{entry.content[:50]}...'"]
        if chain:
            explanation_parts.append(f"was executed by chain '{chain.name}'")
        if goals:
            goal_names = [g.name for g in goals]
            explanation_parts.append(f"serves goals: {', '.join(goal_names)}")
        if parent_chain:
            explanation_parts.append(f"was preceded by {len(parent_chain)} parent entries")
        
        explanation = ". ".join(explanation_parts) + "."
        
        return ProvenanceResult(
            query_type="why",
            start_node_id=entry_id,
            result_nodes=result_nodes,
            path=path,
            explanation=explanation,
            confidence=0.9 if chain or goals else 0.5
        )
    
    def trace_chain_results(self, chain_id: str) -> ProvenanceResult:
        """
        Answers: "What did this produce?"
        
        Returns:
        - All timeline entries created by chain
        - Goal progress impacted
        - Success/failure metrics
        - Quality scores
        """
        chain = self.chain_map.get(chain_id)
        if not chain:
            return ProvenanceResult(
                query_type="what",
                start_node_id=chain_id,
                result_nodes=[],
                path=[],
                explanation=f"Chain {chain_id} not found",
                confidence=0.0
            )
        
        result_nodes: List[Dict[str, Any]] = []
        path: List[str] = [chain_id]
        
        # Get all entries produced
        entries = []
        for entry_id in chain.timeline_entry_ids:
            entry = self.timeline_map.get(entry_id)
            if entry:
                entries.append(entry)
                result_nodes.append({
                    "type": "timeline",
                    "id": entry.entry_id,
                    "content": entry.content[:100],
                    "timestamp": entry.timestamp.isoformat()
                })
                path.append(entry_id)
        
        # Get goal impacts
        goal_impacts = []
        for goal_id in chain.related_goal_ids:
            goal = self.goal_map.get(goal_id)
            if goal:
                contribution = chain.goal_contributions.get(goal_id, 0.0)
                goal_impacts.append({
                    "goal": goal,
                    "contribution": contribution
                })
                result_nodes.append({
                    "type": "goal",
                    "id": goal.goal_id,
                    "name": goal.name,
                    "progress_contribution": contribution
                })
                path.append(goal_id)
        
        # Compute metrics
        metrics = {
            "execution_count": chain.execution_count,
            "success_count": chain.success_count,
            "failure_count": chain.failure_count,
            "success_rate": chain.success_count / chain.execution_count if chain.execution_count > 0 else 0.0,
            "average_quality_score": chain.average_quality_score,
            "average_execution_time": chain.average_execution_time
        }
        
        # Generate explanation
        explanation_parts = [f"Chain '{chain.name}'"]
        explanation_parts.append(f"produced {len(entries)} timeline entries")
        if goal_impacts:
            goal_names = [gi["goal"].name for gi in goal_impacts]
            explanation_parts.append(f"impacted goals: {', '.join(goal_names)}")
        explanation_parts.append(f"with {metrics['success_rate']:.1%} success rate")
        explanation_parts.append(f"and {metrics['average_quality_score']:.2f} average quality")
        
        explanation = ". ".join(explanation_parts) + "."
        
        return ProvenanceResult(
            query_type="what",
            start_node_id=chain_id,
            result_nodes=result_nodes,
            path=path,
            explanation=explanation,
            confidence=0.9 if entries else 0.5
        )
    
    def trace_evolution_path(self, from_entry_id: str, to_entry_id: str) -> ProvenanceResult:
        """
        Answers: "How did we get from A to B?"
        
        Returns:
        - Complete path of timeline entries
        - Chains involved
        - Goals served
        - Decision points
        """
        from_entry = self.timeline_map.get(from_entry_id)
        to_entry = self.timeline_map.get(to_entry_id)
        
        if not from_entry or not to_entry:
            return ProvenanceResult(
                query_type="how",
                start_node_id=from_entry_id,
                result_nodes=[],
                path=[],
                explanation=f"One or both timeline entries not found",
                confidence=0.0
            )
        
        # Simple path finding: follow child_entry_ids from start to end
        # In a full implementation, this would use BFS/DFS graph traversal
        path: List[str] = []
        result_nodes: List[Dict[str, Any]] = []
        visited = set()
        
        current_id = from_entry_id
        while current_id and current_id not in visited:
            visited.add(current_id)
            entry = self.timeline_map.get(current_id)
            if not entry:
                break
            
            path.append(current_id)
            result_nodes.append({
                "type": "timeline",
                "id": entry.entry_id,
                "content": entry.content[:100],
                "timestamp": entry.timestamp.isoformat()
            })
            
            # Check if we reached the target
            if current_id == to_entry_id:
                break
            
            # Follow child entries (simple linear path)
            # In full implementation, would use graph traversal algorithm
            if entry.child_entry_ids:
                current_id = entry.child_entry_ids[0]  # Take first child
            else:
                # No direct path found, try to find via chains
                if entry.executed_via_chain_id:
                    chain = self.chain_map.get(entry.executed_via_chain_id)
                    if chain and chain.timeline_entry_ids:
                        # Find next entry in chain's timeline entries
                        try:
                            current_idx = chain.timeline_entry_ids.index(current_id)
                            if current_idx + 1 < len(chain.timeline_entry_ids):
                                next_id = chain.timeline_entry_ids[current_idx + 1]
                                if next_id in self.timeline_map:
                                    current_id = next_id
                                    continue
                        except ValueError:
                            pass
                
                # No path found
                break
        
        # Generate explanation
        if current_id == to_entry_id:
            explanation = f"Evolution path from '{from_entry.content[:50]}...' to '{to_entry.content[:50]}...' consists of {len(path)} steps through timeline entries."
        else:
            explanation = f"Could not find complete evolution path from '{from_entry_id}' to '{to_entry_id}'. Found partial path with {len(path)} entries."
        
        return ProvenanceResult(
            query_type="how",
            start_node_id=from_entry_id,
            result_nodes=result_nodes,
            path=path,
            explanation=explanation,
            confidence=1.0 if current_id == to_entry_id else 0.6
        )


# Convenience functions
def explain_timeline_entry(graph: TemporalGraph, entry_id: str) -> ProvenanceResult:
    """Convenience function for explaining a timeline entry"""
    traverser = TemporalGraphTraverser(graph)
    return traverser.explain_timeline_entry(entry_id)


def trace_chain_results(graph: TemporalGraph, chain_id: str) -> ProvenanceResult:
    """Convenience function for tracing chain results"""
    traverser = TemporalGraphTraverser(graph)
    return traverser.trace_chain_results(chain_id)


def trace_evolution_path(graph: TemporalGraph, from_entry_id: str, to_entry_id: str) -> ProvenanceResult:
    """Convenience function for tracing evolution path"""
    traverser = TemporalGraphTraverser(graph)
    return traverser.trace_evolution_path(from_entry_id, to_entry_id)

