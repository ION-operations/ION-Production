"""
Temporal Consciousness MCP Tools

Exposes temporal consciousness graph queries via MCP tools for frontend integration.
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from .models import (
    TemporalGraph,
    EnhancedTimelineEntry,
    EnhancedGoalTimelineNode,
    EnhancedPromptChain
)
from .graph_traversal import (
    TemporalGraphTraverser,
    explain_timeline_entry,
    trace_chain_results,
    trace_evolution_path
)

logger = logging.getLogger(__name__)


class TemporalConsciousnessMCPTools:
    """
    MCP tools for temporal consciousness graph operations.
    
    Integrates with:
    - TCS: Get timeline entries
    - Goal Timeline System: Get goals
    - Prompt Chains: Get chains
    - CMC: Storage
    - HHNI: Semantic search
    - VIF: Confidence tracking
    """
    
    def __init__(
        self,
        tcs_client=None,
        goal_timeline_client=None,
        chain_client=None,
        cmc_client=None,
        hhni_client=None,
        vif_client=None
    ):
        """Initialize MCP tools with system clients"""
        self.tcs_client = tcs_client
        self.goal_timeline_client = goal_timeline_client
        self.chain_client = chain_client
        self.cmc_client = cmc_client
        self.hhni_client = hhni_client
        self.vif_client = vif_client
    
    async def get_temporal_graph(
        self,
        timeline_limit: int = 100,
        goal_status: Optional[str] = None,
        chain_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get complete temporal graph (Timeline + Goals + Chains).
        
        Returns graph data for frontend visualization.
        """
        try:
            # Get timeline entries from TCS
            timeline_entries = []
            if self.tcs_client:
                try:
                    # Use MCP tool to get timeline entries
                    # This would call mcp_lucid-mcp_get_timeline_entries
                    timeline_data = await self._get_timeline_entries_via_mcp(limit=timeline_limit)
                    timeline_entries = [
                        EnhancedTimelineEntry.from_dict(entry)
                        for entry in timeline_data
                    ]
                except Exception as e:
                    logger.warning(f"Error getting timeline entries: {e}")
            
            # Get goals from Goal Timeline System
            goals = []
            if self.goal_timeline_client:
                try:
                    # Use MCP tool to get goals
                    # This would call mcp_lucid-mcp_query_goal_timeline
                    goals_data = await self._get_goals_via_mcp(status=goal_status)
                    goals = [
                        EnhancedGoalTimelineNode.from_dict(goal)
                        for goal in goals_data
                    ]
                except Exception as e:
                    logger.warning(f"Error getting goals: {e}")
            
            # Get chains from Prompt Chain System
            chains = []
            if self.chain_client:
                try:
                    chains_data = await self._get_chains_via_client(chain_ids=chain_ids)
                    chains = [
                        EnhancedPromptChain.from_dict(chain)
                        for chain in chains_data
                    ]
                except Exception as e:
                    logger.warning(f"Error getting chains: {e}")
            
            # Build graph
            graph = TemporalGraph(
                timeline_entries=timeline_entries,
                goals=goals,
                chains=chains
            )
            
            return {
                "success": True,
                "graph": graph.to_dict(),
                "statistics": {
                    "timeline_count": len(timeline_entries),
                    "goals_count": len(goals),
                    "chains_count": len(chains)
                }
            }
            
        except Exception as e:
            logger.error(f"Error building temporal graph: {e}")
            return {
                "success": False,
                "error": str(e),
                "graph": {"timeline": [], "goals": [], "chains": []}
            }
    
    async def explain_timeline_entry(self, entry_id: str) -> Dict[str, Any]:
        """
        Explain why a timeline entry happened (Why query).
        
        Returns provenance chain showing:
        - Which chain executed it
        - Which goals it served
        - Parent entries that led to it
        """
        try:
            # Get graph data
            graph_data = await self.get_temporal_graph()
            if not graph_data.get("success"):
                return {
                    "success": False,
                    "error": "Failed to load graph data"
                }
            
            graph = TemporalGraph.from_dict(graph_data["graph"])
            traverser = TemporalGraphTraverser(graph)
            result = traverser.explain_timeline_entry(entry_id)
            
            return {
                "success": True,
                "query_type": result.query_type,
                "start_node_id": result.start_node_id,
                "result_nodes": result.result_nodes,
                "path": result.path,
                "explanation": result.explanation,
                "confidence": result.confidence
            }
            
        except Exception as e:
            logger.error(f"Error explaining timeline entry: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def trace_chain_results(self, chain_id: str) -> Dict[str, Any]:
        """
        Trace what a chain produced (What query).
        
        Returns:
        - All timeline entries created by chain
        - Goal progress impacted
        - Success/failure metrics
        """
        try:
            # Get graph data
            graph_data = await self.get_temporal_graph()
            if not graph_data.get("success"):
                return {
                    "success": False,
                    "error": "Failed to load graph data"
                }
            
            graph = TemporalGraph.from_dict(graph_data["graph"])
            traverser = TemporalGraphTraverser(graph)
            result = traverser.trace_chain_results(chain_id)
            
            return {
                "success": True,
                "query_type": result.query_type,
                "start_node_id": result.start_node_id,
                "result_nodes": result.result_nodes,
                "path": result.path,
                "explanation": result.explanation,
                "confidence": result.confidence
            }
            
        except Exception as e:
            logger.error(f"Error tracing chain results: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def trace_evolution_path(
        self,
        from_entry_id: str,
        to_entry_id: str
    ) -> Dict[str, Any]:
        """
        Trace evolution path from one entry to another (How query).
        
        Returns complete path showing how system evolved from A to B.
        """
        try:
            # Get graph data
            graph_data = await self.get_temporal_graph()
            if not graph_data.get("success"):
                return {
                    "success": False,
                    "error": "Failed to load graph data"
                }
            
            graph = TemporalGraph.from_dict(graph_data["graph"])
            traverser = TemporalGraphTraverser(graph)
            result = traverser.trace_evolution_path(from_entry_id, to_entry_id)
            
            return {
                "success": True,
                "query_type": result.query_type,
                "start_node_id": result.start_node_id,
                "result_nodes": result.result_nodes,
                "path": result.path,
                "explanation": result.explanation,
                "confidence": result.confidence
            }
            
        except Exception as e:
            logger.error(f"Error tracing evolution path: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Helper methods for getting data from systems
    async def _get_timeline_entries_via_mcp(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get timeline entries via MCP tool (stub - would call actual MCP tool)"""
        # In production, this would call:
        # mcp_lucid-mcp_get_timeline_entries with limit parameter
        # For now, return empty list (frontend will handle via direct MCP calls)
        return []
    
    async def _get_goals_via_mcp(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get goals via MCP tool (stub - would call actual MCP tool)"""
        # In production, this would call:
        # mcp_lucid-mcp_query_goal_timeline with status parameter
        # For now, return empty list (frontend will handle via direct MCP calls)
        return []
    
    async def _get_chains_via_client(self, chain_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get chains via chain client (stub - would call actual chain storage)"""
        # In production, this would query chain storage
        # For now, return empty list (frontend will handle via direct chain storage calls)
        return []

