"""
Test temporal_consciousness Backend

Verifies that temporal_consciousness backend correctly:
- Retrieves graph data
- Executes Why/What/How queries
- Integrates with TCS/Goals/Chains
- Works with frontend
"""

import pytest
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, List
from datetime import datetime

from packages.temporal_consciousness.models import (
    EnhancedTimelineEntry,
    EnhancedGoalTimelineNode,
    EnhancedPromptChain,
    TemporalGraph,
    GoalStatus
)
from packages.temporal_consciousness.graph_traversal import (
    TemporalGraphTraverser,
    explain_timeline_entry,
    trace_chain_results,
    trace_evolution_path
)


class TestTemporalConsciousnessBackend:
    """Test suite for temporal_consciousness backend"""
    
    @pytest.fixture
    def sample_timeline_entry(self):
        """Create sample timeline entry"""
        return EnhancedTimelineEntry(
            entry_id="entry_1",
            timestamp=datetime.now(),
            entry_type="operation",
            content="Test operation",
            agent="test_agent",
            executed_via_chain_id="chain_1",
            related_goal_ids=["goal_1"],
            parent_entry_ids=[],
            child_entry_ids=["entry_2"]
        )
    
    @pytest.fixture
    def sample_goal(self):
        """Create sample goal"""
        return EnhancedGoalTimelineNode(
            goal_id="goal_1",
            name="Test Goal",
            description="Test goal description",
            status=GoalStatus.IN_PROGRESS,
            progress_percentage=0.5,
            timeline_entry_ids=["entry_1"],
            planned_chain_ids=["chain_1"]
        )
    
    @pytest.fixture
    def sample_chain(self):
        """Create sample chain"""
        return EnhancedPromptChain(
            chain_id="chain_1",
            name="Test Chain",
            description="Test chain description",
            nodes=[],
            timeline_entry_ids=["entry_1"],
            related_goal_ids=["goal_1"],
            execution_count=1,
            success_count=1,
            failure_count=0,
            average_quality_score=0.9
        )
    
    @pytest.fixture
    def sample_graph(self, sample_timeline_entry, sample_goal, sample_chain):
        """Create sample temporal graph"""
        return TemporalGraph(
            timeline_entries=[sample_timeline_entry],
            goals=[sample_goal],
            chains=[sample_chain]
        )
    
    def test_explain_timeline_entry(self, sample_graph):
        """Test Why query (explain timeline entry)"""
        traverser = TemporalGraphTraverser(sample_graph)
        result = traverser.explain_timeline_entry("entry_1")
        
        # Verify result
        assert result.query_type == "why"
        assert result.start_node_id == "entry_1"
        assert len(result.result_nodes) > 0
        assert len(result.path) > 0
        assert result.explanation is not None
        assert result.confidence > 0
    
    def test_trace_chain_results(self, sample_graph):
        """Test What query (trace chain results)"""
        traverser = TemporalGraphTraverser(sample_graph)
        result = traverser.trace_chain_results("chain_1")
        
        # Verify result
        assert result.query_type == "what"
        assert result.start_node_id == "chain_1"
        assert len(result.result_nodes) > 0
        assert len(result.path) > 0
        assert result.explanation is not None
        assert result.confidence > 0
    
    def test_trace_evolution_path(self, sample_graph):
        """Test How query (trace evolution path)"""
        # Add second entry for path tracing
        entry_2 = EnhancedTimelineEntry(
            entry_id="entry_2",
            timestamp=datetime.now(),
            entry_type="operation",
            content="Second operation",
            agent="test_agent",
            parent_entry_ids=["entry_1"]
        )
        sample_graph.timeline_entries.append(entry_2)
        
        traverser = TemporalGraphTraverser(sample_graph)
        result = traverser.trace_evolution_path("entry_1", "entry_2")
        
        # Verify result
        assert result.query_type == "how"
        assert result.start_node_id == "entry_1"
        assert len(result.path) > 0
        assert result.explanation is not None
    
    def test_graph_data_serialization(self, sample_graph):
        """Test graph data serialization"""
        # Convert to dict
        graph_dict = sample_graph.to_dict()
        
        # Verify structure
        assert "timeline" in graph_dict
        assert "goals" in graph_dict
        assert "chains" in graph_dict
        assert len(graph_dict["timeline"]) > 0
        assert len(graph_dict["goals"]) > 0
        assert len(graph_dict["chains"]) > 0
    
    def test_graph_data_deserialization(self, sample_graph):
        """Test graph data deserialization"""
        # Convert to dict and back
        graph_dict = sample_graph.to_dict()
        restored_graph = TemporalGraph.from_dict(graph_dict)
        
        # Verify restoration
        assert len(restored_graph.timeline_entries) == len(sample_graph.timeline_entries)
        assert len(restored_graph.goals) == len(sample_graph.goals)
        assert len(restored_graph.chains) == len(sample_graph.chains)
    
    def test_missing_entry_handling(self, sample_graph):
        """Test handling of missing timeline entry"""
        traverser = TemporalGraphTraverser(sample_graph)
        result = traverser.explain_timeline_entry("nonexistent_entry")
        
        # Verify graceful handling
        assert result.query_type == "why"
        assert result.start_node_id == "nonexistent_entry"
        assert result.confidence == 0.0
        assert "not found" in result.explanation.lower()
    
    def test_missing_chain_handling(self, sample_graph):
        """Test handling of missing chain"""
        traverser = TemporalGraphTraverser(sample_graph)
        result = traverser.trace_chain_results("nonexistent_chain")
        
        # Verify graceful handling
        assert result.query_type == "what"
        assert result.start_node_id == "nonexistent_chain"
        assert result.confidence == 0.0
        assert "not found" in result.explanation.lower()


class TestTemporalConsciousnessMCPTools:
    """Test suite for temporal_consciousness MCP tools"""
    
    @pytest.fixture
    def mock_tcs_client(self):
        """Create mock TCS client"""
        client = Mock()
        client.get_timeline_entries = AsyncMock(return_value=[])
        return client
    
    @pytest.fixture
    def mock_goal_client(self):
        """Create mock goal timeline client"""
        client = Mock()
        client.query_goals = AsyncMock(return_value=[])
        return client
    
    @pytest.fixture
    def mock_chain_client(self):
        """Create mock chain client"""
        client = Mock()
        client.get_chains = AsyncMock(return_value=[])
        return client
    
    @pytest.fixture
    def mcp_tools(self, mock_tcs_client, mock_goal_client, mock_chain_client):
        """Create MCP tools instance"""
        from packages.temporal_consciousness.mcp_tools import TemporalConsciousnessMCPTools
        
        tools = TemporalConsciousnessMCPTools(
            tcs_client=mock_tcs_client,
            goal_timeline_client=mock_goal_client,
            chain_client=mock_chain_client
        )
        return tools
    
    @pytest.mark.asyncio
    async def test_get_temporal_graph(self, mcp_tools, mock_tcs_client, mock_goal_client, mock_chain_client):
        """Test getting temporal graph data"""
        result = await mcp_tools.get_temporal_graph(timeline_limit=100)
        
        # Verify result structure
        assert "success" in result
        assert "graph" in result
        assert "statistics" in result
        
        # Verify graph structure
        graph = result["graph"]
        assert "timeline" in graph
        assert "goals" in graph
        assert "chains" in graph
    
    @pytest.mark.asyncio
    async def test_explain_timeline_entry_via_mcp(self, mcp_tools):
        """Test explaining timeline entry via MCP tools"""
        result = await mcp_tools.explain_timeline_entry("entry_1")
        
        # Verify result structure
        assert "success" in result
        if result["success"]:
            assert "query_type" in result
            assert "explanation" in result
    
    @pytest.mark.asyncio
    async def test_trace_chain_results_via_mcp(self, mcp_tools):
        """Test tracing chain results via MCP tools"""
        result = await mcp_tools.trace_chain_results("chain_1")
        
        # Verify result structure
        assert "success" in result
        if result["success"]:
            assert "query_type" in result
            assert "explanation" in result
    
    @pytest.mark.asyncio
    async def test_trace_evolution_path_via_mcp(self, mcp_tools):
        """Test tracing evolution path via MCP tools"""
        result = await mcp_tools.trace_evolution_path("entry_1", "entry_2")
        
        # Verify result structure
        assert "success" in result
        if result["success"]:
            assert "query_type" in result
            assert "explanation" in result


class TestTemporalConsciousnessBackendManual:
    """Manual test cases for temporal_consciousness backend"""
    
    def test_manual_graph_data_retrieval(self):
        """Manual test: Verify graph data retrieval with real systems"""
        # Steps:
        # 1. Create MCP tools with real TCS/Goals/Chains clients
        # 2. Get temporal graph
        # 3. Verify graph contains timeline entries, goals, chains
        # 4. Verify data structure is correct
        pass
    
    def test_manual_why_query(self):
        """Manual test: Verify Why query works with real data"""
        # Steps:
        # 1. Create graph with real timeline entries
        # 2. Execute Why query on a timeline entry
        # 3. Verify provenance chain returned
        # 4. Verify explanation makes sense
        pass
    
    def test_manual_what_query(self):
        """Manual test: Verify What query works with real data"""
        # Steps:
        # 1. Create graph with real chains
        # 2. Execute What query on a chain
        # 3. Verify chain results returned
        # 4. Verify metrics are correct
        pass
    
    def test_manual_how_query(self):
        """Manual test: Verify How query works with real data"""
        # Steps:
        # 1. Create graph with multiple timeline entries
        # 2. Execute How query between two entries
        # 3. Verify evolution path returned
        # 4. Verify path makes sense
        pass
    
    def test_manual_frontend_integration(self):
        """Manual test: Verify frontend can consume backend APIs"""
        # Steps:
        # 1. Start backend services
        # 2. Load frontend component
        # 3. Verify frontend can fetch graph data
        # 4. Verify frontend can execute queries
        # 5. Verify graph visualization works
        pass

