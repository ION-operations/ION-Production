"""
Test QueryExecutor - Why/What/How Graph Traversal
Validates graph traversal queries work correctly
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from prompt_chains.executor.query_executor import QueryExecutor, QueryResult


class TestWhyQuery:
    """Test Why query (backward causation)"""
    
    @pytest.mark.asyncio
    async def test_why_from_timeline_to_chain_to_goal(self):
        """Test: Timeline → Chain → Goal (why did this happen)"""
        executor = QueryExecutor()
        
        # Mock graph
        graph = {
            'timeline': [{
                'entry_id': 'entry-1',
                'title': 'Documentation Complete',
                'executed_via_chain_id': 'chain-1'
            }],
            'chains': [{
                'chain_id': 'chain-1',
                'name': 'Autonomous Documentation',
                'goal_id': 'OBJ-12'
            }],
            'goals': [{
                'goal_id': 'OBJ-12',
                'name': 'Complete Documentation Standards'
            }]
        }
        
        # Execute Why query from timeline
        result = await executor.execute_why_query('entry-1', 'timeline', graph)
        
        # Verify result
        assert result.query_type == 'why'
        assert result.start_node_id == 'entry-1'
        assert len(result.result_nodes) == 3  # Timeline + Chain + Goal
        assert result.path == ['entry-1', 'chain-1', 'OBJ-12']
        assert result.confidence > 0
        
        print(f"✅ Why query traced: {result.explanation}")
    
    @pytest.mark.asyncio
    async def test_why_from_chain_to_goal(self):
        """Test: Chain → Goal (why was this chain created)"""
        executor = QueryExecutor()
        
        graph = {
            'timeline': [],
            'chains': [{
                'chain_id': 'chain-2',
                'name': 'Test Chain',
                'goal_id': 'OBJ-13'
            }],
            'goals': [{
                'goal_id': 'OBJ-13',
                'name': 'Test Goal'
            }]
        }
        
        result = await executor.execute_why_query('chain-2', 'chain', graph)
        
        assert result.query_type == 'why'
        assert len(result.result_nodes) == 2  # Chain + Goal
        assert 'OBJ-13' in result.path


class TestWhatQuery:
    """Test What query (current focus)"""
    
    @pytest.mark.asyncio
    async def test_what_from_timeline(self):
        """Test: Timeline → Chain → Goal (what was the focus)"""
        executor = QueryExecutor()
        
        graph = {
            'timeline': [{
                'entry_id': 'entry-1',
                'executed_via_chain_id': 'chain-1'
            }],
            'chains': [{
                'chain_id': 'chain-1',
                'goal_id': 'OBJ-12'
            }],
            'goals': [{
                'goal_id': 'OBJ-12',
                'name': 'Documentation Standards'
            }]
        }
        
        result = await executor.execute_what_query('entry-1', 'timeline', graph)
        
        assert result.query_type == 'what'
        assert len(result.result_nodes) == 1  # The goal
        assert result.result_nodes[0]['goal_id'] == 'OBJ-12'
        assert result.confidence > 0
        
        print(f"✅ What query found: {result.explanation}")
    
    @pytest.mark.asyncio
    async def test_what_from_chain(self):
        """Test: Chain → Goal (direct connection)"""
        executor = QueryExecutor()
        
        graph = {
            'timeline': [],
            'chains': [{
                'chain_id': 'chain-1',
                'goal_id': 'OBJ-12'
            }],
            'goals': [{
                'goal_id': 'OBJ-12',
                'name': 'Test Goal'
            }]
        }
        
        result = await executor.execute_what_query('chain-1', 'chain', graph)
        
        assert result.query_type == 'what'
        assert len(result.result_nodes) == 1
        assert result.result_nodes[0]['goal_id'] == 'OBJ-12'


class TestHowQuery:
    """Test How query (forward planning)"""
    
    @pytest.mark.asyncio
    async def test_how_from_goal(self):
        """Test: Goal → Chains (how will this be achieved)"""
        executor = QueryExecutor()
        
        graph = {
            'timeline': [],
            'chains': [
                {'chain_id': 'chain-1', 'name': 'Chain 1'},
                {'chain_id': 'chain-2', 'name': 'Chain 2'}
            ],
            'goals': [{
                'goal_id': 'OBJ-12',
                'related_chain_ids': ['chain-1', 'chain-2']
            }]
        }
        
        result = await executor.execute_how_query('OBJ-12', 'goal', graph)
        
        assert result.query_type == 'how'
        assert len(result.result_nodes) == 2  # Both chains
        assert 'chain-1' in result.path
        assert 'chain-2' in result.path
        assert result.confidence > 0
        
        print(f"✅ How query found: {result.explanation}")
    
    @pytest.mark.asyncio
    async def test_how_from_chain(self):
        """Test: Chain → Timeline (what did this produce)"""
        executor = QueryExecutor()
        
        graph = {
            'timeline': [
                {'entry_id': 'entry-1', 'title': 'Entry 1'},
                {'entry_id': 'entry-2', 'title': 'Entry 2'}
            ],
            'chains': [{
                'chain_id': 'chain-1',
                'timeline_entry_ids': ['entry-1', 'entry-2']
            }],
            'goals': []
        }
        
        result = await executor.execute_how_query('chain-1', 'chain', graph)
        
        assert result.query_type == 'how'
        assert len(result.result_nodes) == 2  # Both timeline entries
        assert 'entry-1' in result.path
        assert 'entry-2' in result.path


class TestCompleteGraph:
    """Test complete graph queries"""
    
    @pytest.mark.asyncio
    async def test_complete_temporal_consciousness_graph(self):
        """Test complete Past-Present-Future graph traversal"""
        executor = QueryExecutor()
        
        # Complete graph with all 3 node types
        graph = {
            'timeline': [
                {
                    'entry_id': 'entry-1',
                    'title': 'Work Started',
                    'executed_via_chain_id': 'chain-1'
                },
                {
                    'entry_id': 'entry-2',
                    'title': 'Work Complete',
                    'executed_via_chain_id': 'chain-1'
                }
            ],
            'chains': [{
                'chain_id': 'chain-1',
                'name': 'Documentation Chain',
                'goal_id': 'OBJ-12',
                'timeline_entry_ids': ['entry-1', 'entry-2']
            }],
            'goals': [{
                'goal_id': 'OBJ-12',
                'name': 'Complete Docs',
                'related_chain_ids': ['chain-1']
            }]
        }
        
        # Test Why from timeline entry
        why_result = await executor.execute_why_query('entry-1', 'timeline', graph)
        assert 'OBJ-12' in why_result.path  # Should trace to goal
        
        # Test What from timeline entry
        what_result = await executor.execute_what_query('entry-1', 'timeline', graph)
        assert len(what_result.result_nodes) > 0  # Should find goal
        
        # Test How from goal
        how_result = await executor.execute_how_query('OBJ-12', 'goal', graph)
        assert 'chain-1' in how_result.path  # Should find chain
        
        print("✅ Complete temporal graph queries working!")
        print(f"   - Why: {why_result.explanation}")
        print(f"   - What: {what_result.explanation}")
        print(f"   - How: {how_result.explanation}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

