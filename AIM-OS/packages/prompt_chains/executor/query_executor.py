"""
Query Executor for Temporal Consciousness Graph
Implements Why/What/How graph traversal queries

Enables exploring Past-Present-Future through bidirectional connections.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class QueryResult:
    """Result of a Why/What/How query"""
    query_type: str  # "why" | "what" | "how"
    start_node_id: str
    result_nodes: List[Dict[str, Any]]  # Nodes found in traversal
    path: List[str]  # Path through graph (node IDs)
    explanation: str  # Human-readable explanation
    confidence: float = 1.0  # Confidence in result
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            'query_type': self.query_type,
            'start_node_id': self.start_node_id,
            'result_nodes': self.result_nodes,
            'path': self.path,
            'explanation': self.explanation,
            'confidence': self.confidence
        }


class QueryExecutor:
    """
    Executes Why/What/How queries on temporal consciousness graph
    
    Graph Structure:
    - Timeline nodes (past) connect to Chain nodes via executed_via_chain_id
    - Chain nodes (future) connect to Goal nodes via goal_id
    - Chain nodes connect to Timeline nodes via timeline_entry_ids (produced)
    - Goal nodes connect to Chain nodes via related_chain_ids
    """
    
    def __init__(self):
        """Initialize query executor"""
        pass
    
    async def execute_why_query(
        self,
        node_id: str,
        node_type: str,
        graph: Dict[str, Any]
    ) -> QueryResult:
        """
        Why Query: Trace backwards through causation chain
        
        For Timeline node: Follow executed_via_chain_id → Chain → goal_id → Goal
        For Goal node: Follow creation context
        For Chain node: Follow parent_chain_id or goal_id
        
        Returns: Path showing "why this happened" (what led to this)
        """
        path: List[str] = []
        result_nodes: List[Dict[str, Any]] = []
        visited = set()
        
        current_id = node_id
        current_type = node_type
        
        while current_id and current_id not in visited:
            visited.add(current_id)
            
            # Find node in graph
            node = self._find_node(current_id, current_type, graph)
            if not node:
                break
            
            path.append(current_id)
            result_nodes.append(node)
            
            # Determine backward edge
            if current_type == 'timeline':
                # Timeline → Chain (executed_via)
                next_id = node.get('executed_via_chain_id')
                next_type = 'chain' if next_id else None
            
            elif current_type == 'chain':
                # Chain → Goal (what goal was this serving)
                next_id = node.get('goal_id')
                next_type = 'goal' if next_id else None
            
            elif current_type == 'goal':
                # Goal → (root - no further backward)
                break
            
            else:
                break
            
            current_id = next_id
            current_type = next_type
        
        # Build explanation
        explanation = self._build_why_explanation(result_nodes)
        
        return QueryResult(
            query_type='why',
            start_node_id=node_id,
            result_nodes=result_nodes,
            path=path,
            explanation=explanation,
            confidence=1.0
        )
    
    async def execute_what_query(
        self,
        node_id: str,
        node_type: str,
        graph: Dict[str, Any]
    ) -> QueryResult:
        """
        What Query: Show current state (connected goals)
        
        For any node: Find all connected Goal nodes
        Shows "what is the current focus" related to this node
        
        Returns: All goals connected to this node
        """
        result_nodes: List[Dict[str, Any]] = []
        path: List[str] = [node_id]
        
        # Find starting node
        start_node = self._find_node(node_id, node_type, graph)
        if not start_node:
            return QueryResult(
                query_type='what',
                start_node_id=node_id,
                result_nodes=[],
                path=path,
                explanation="Node not found",
                confidence=0.0
            )
        
        # Find connected goals
        if node_type == 'timeline':
            # Timeline → Chain → Goal
            if start_node.get('executed_via_chain_id'):
                chain = self._find_node(start_node['executed_via_chain_id'], 'chain', graph)
            if chain and chain.get('goal_id'):
                goal = self._find_node(chain['goal_id'], 'goal', graph)
                if goal:
                    result_nodes.append(goal)
                    path.append(chain['chain_id'])
                    # Use node_id or goal_id (flexible)
                    path.append(goal.get('node_id') or goal.get('goal_id'))
        
        elif node_type == 'chain':
            # Chain → Goal (direct)
            if start_node.get('goal_id'):
                goal = self._find_node(start_node['goal_id'], 'goal', graph)
                if goal:
                    result_nodes.append(goal)
                    # Use node_id or goal_id (flexible)
                    path.append(goal.get('node_id') or goal.get('goal_id'))
        
        elif node_type == 'goal':
            # Goal → itself (current state)
            result_nodes.append(start_node)
        
        explanation = self._build_what_explanation(result_nodes)
        
        return QueryResult(
            query_type='what',
            start_node_id=node_id,
            result_nodes=result_nodes,
            path=path,
            explanation=explanation,
            confidence=1.0 if result_nodes else 0.5
        )
    
    async def execute_how_query(
        self,
        node_id: str,
        node_type: str,
        graph: Dict[str, Any]
    ) -> QueryResult:
        """
        How Query: Explore forward through planning chain
        
        For Goal node: Show related_chain_ids (what chains will achieve this)
        For Chain node: Show timeline_entry_ids (what did this produce)
        For Timeline node: Show child_chain_ids (what was spawned from this)
        
        Returns: Path showing "how this will/did happen" (what comes next)
        """
        result_nodes: List[Dict[str, Any]] = []
        path: List[str] = [node_id]
        
        # Find starting node
        start_node = self._find_node(node_id, node_type, graph)
        if not start_node:
            return QueryResult(
                query_type='how',
                start_node_id=node_id,
                result_nodes=[],
                path=path,
                explanation="Node not found",
                confidence=0.0
            )
        
        # Find forward connections
        if node_type == 'goal':
            # Goal → Chains (what will achieve this)
            for chain_id in start_node.get('related_chain_ids', []):
                chain = self._find_node(chain_id, 'chain', graph)
                if chain:
                    result_nodes.append(chain)
                    path.append(chain_id)
        
        elif node_type == 'chain':
            # Chain → Timeline entries (what did this produce)
            for entry_id in start_node.get('timeline_entry_ids', []):
                entry = self._find_node(entry_id, 'timeline', graph)
                if entry:
                    result_nodes.append(entry)
                    path.append(entry_id)
        
        elif node_type == 'timeline':
            # Timeline → Chains (what was spawned)
            for chain_id in start_node.get('child_chain_ids', []):
                chain = self._find_node(chain_id, 'chain', graph)
                if chain:
                    result_nodes.append(chain)
                    path.append(chain_id)
        
        explanation = self._build_how_explanation(result_nodes, node_type)
        
        return QueryResult(
            query_type='how',
            start_node_id=node_id,
            result_nodes=result_nodes,
            path=path,
            explanation=explanation,
            confidence=1.0 if result_nodes else 0.5
        )
    
    def _find_node(
        self,
        node_id: str,
        node_type: str,
        graph: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Find node in graph by ID and type"""
        if node_type == 'timeline':
            for entry in graph.get('timeline', []):
                if entry.get('entry_id') == node_id or entry.get('prompt_id') == node_id:
                    return entry
        
        elif node_type == 'goal':
            for goal in graph.get('goals', []):
                # Handle both node_id and goal_id (flexible)
                goal_node_id = goal.get('node_id') or goal.get('goal_id')
                if goal_node_id == node_id:
                    return goal
        
        elif node_type == 'chain':
            for chain in graph.get('chains', []):
                if chain.get('chain_id') == node_id:
                    return chain
        
        return None
    
    def _build_why_explanation(self, nodes: List[Dict[str, Any]]) -> str:
        """Build human-readable explanation for Why query"""
        if not nodes:
            return "No causation chain found"
        
        if len(nodes) == 1:
            return f"Root node (no prior cause)"
        
        # Build explanation from path
        explanation = "Causation chain:\n"
        for i, node in enumerate(nodes):
            node_type = self._get_node_type(node)
            node_label = node.get('name') or node.get('title') or node.get('chain_id') or node.get('goal_id')
            explanation += f"{i+1}. {node_type}: {node_label}\n"
        
        return explanation
    
    def _build_what_explanation(self, nodes: List[Dict[str, Any]]) -> str:
        """Build human-readable explanation for What query"""
        if not nodes:
            return "No goals connected to this node"
        
        goal_names = [g.get('name', g.get('goal_id', 'Unknown')) for g in nodes]
        return f"Current focus: {', '.join(goal_names)}"
    
    def _build_how_explanation(self, nodes: List[Dict[str, Any]], start_type: str) -> str:
        """Build human-readable explanation for How query"""
        if not nodes:
            return "No forward connections found"
        
        if start_type == 'goal':
            return f"Chains working toward this goal: {len(nodes)}"
        elif start_type == 'chain':
            return f"Timeline entries produced: {len(nodes)}"
        elif start_type == 'timeline':
            return f"Chains spawned from this: {len(nodes)}"
        
        return f"Found {len(nodes)} connected nodes"
    
    def _get_node_type(self, node: Dict[str, Any]) -> str:
        """Determine node type from node data"""
        if 'entry_id' in node or 'prompt_id' in node:
            return 'Timeline'
        elif 'chain_id' in node:
            return 'Chain'
        elif 'goal_id' in node or 'node_id' in node:
            return 'Goal'
        return 'Unknown'

