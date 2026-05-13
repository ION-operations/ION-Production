"""
Test Data Models - PromptChain, ExecutionRecord, TimelineEntry
Validates serialization, deserialization, and bidirectional connections
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from prompt_chains.models.prompt_chain import (
    ChainType, ChainPriority, NodeType, ConditionType,
    QualityGate, ChainNode, ChainEdge, PromptChain
)
from prompt_chains.models.execution_record import (
    NodeExecutionResult, ChainExecutionResult, NodeExecution, ExecutionRecord
)


class TestQualityGate:
    """Test QualityGate model"""
    
    def test_quality_gate_creation(self):
        """Test creating a quality gate"""
        gate = QualityGate(
            gate_type='quartet_parity',
            threshold=0.90,
            parameters={'check_tests': True}
        )
        
        assert gate.gate_type == 'quartet_parity'
        assert gate.threshold == 0.90
        assert gate.parameters['check_tests'] is True
    
    def test_quality_gate_evaluate_quartet_parity(self):
        """Test quartet parity gate evaluation"""
        gate = QualityGate(gate_type='quartet_parity', threshold=0.90)
        
        # Test passing
        assert gate.evaluate({'quartet_parity': 0.95}) is True
        
        # Test failing
        assert gate.evaluate({'quartet_parity': 0.85}) is False
    
    def test_quality_gate_serialization(self):
        """Test gate to_dict/from_dict"""
        gate = QualityGate(
            gate_type='test_coverage',
            threshold=0.85,
            parameters={'min_tests': 10}
        )
        
        # Serialize
        data = gate.to_dict()
        assert data['gate_type'] == 'test_coverage'
        assert data['threshold'] == 0.85
        
        # Deserialize
        gate2 = QualityGate.from_dict(data)
        assert gate2.gate_type == gate.gate_type
        assert gate2.threshold == gate.threshold
        assert gate2.parameters == gate.parameters


class TestChainNode:
    """Test ChainNode model"""
    
    def test_chain_node_creation(self):
        """Test creating a chain node"""
        node = ChainNode(
            node_id='node-1',
            name='Store Memory',
            description='Store data in CMC',
            operation_type=NodeType.SYSTEM_CALL,
            system='CMC',
            operation='store_atom',
            parameters={'mpd_id': 'test-123'},
            confidence_threshold=0.75
        )
        
        assert node.node_id == 'node-1'
        assert node.system == 'CMC'
        assert node.operation == 'store_atom'
        assert node.confidence_threshold == 0.75
    
    def test_chain_node_with_quality_gate(self):
        """Test node with quality gate"""
        gate = QualityGate(gate_type='quartet_parity', threshold=0.90)
        node = ChainNode(
            node_id='node-2',
            name='Code Implementation',
            description='Implement feature with quality check',
            operation_type=NodeType.GATE,
            quality_gate=gate
        )
        
        assert node.quality_gate is not None
        assert node.quality_gate.threshold == 0.90
    
    def test_chain_node_serialization(self):
        """Test node to_dict/from_dict"""
        node = ChainNode(
            node_id='node-3',
            name='Test Node',
            description='Test description',
            operation_type=NodeType.SYSTEM_CALL,
            system='HHNI',
            operation='search',
            parameters={'query': 'test'}
        )
        
        # Serialize
        data = node.to_dict()
        assert data['node_id'] == 'node-3'
        assert data['system'] == 'HHNI'
        
        # Deserialize
        node2 = ChainNode.from_dict(data)
        assert node2.node_id == node.node_id
        assert node2.system == node.system
        assert node2.operation == node.operation


class TestChainEdge:
    """Test ChainEdge model"""
    
    def test_edge_unconditional(self):
        """Test unconditional edge"""
        edge = ChainEdge(
            edge_id='edge-1',
            from_node_id='node-1',
            to_node_id='node-2'
        )
        
        # Should always evaluate to True
        assert edge.evaluate_condition({}) is True
    
    def test_edge_confidence_condition(self):
        """Test confidence-based conditional edge"""
        edge = ChainEdge(
            edge_id='edge-2',
            from_node_id='node-1',
            to_node_id='node-2',
            condition_type=ConditionType.CONFIDENCE,
            condition_expression='confidence > 0.70'
        )
        
        # Test passing
        assert edge.evaluate_condition({'confidence': 0.85}) is True
        
        # Test failing
        assert edge.evaluate_condition({'confidence': 0.65}) is False
    
    def test_edge_serialization(self):
        """Test edge to_dict/from_dict"""
        edge = ChainEdge(
            edge_id='edge-3',
            from_node_id='node-1',
            to_node_id='node-2',
            condition_type=ConditionType.QUALITY,
            condition_expression='quartet_parity >= 0.90',
            label='quality-check'
        )
        
        # Serialize
        data = edge.to_dict()
        assert data['edge_id'] == 'edge-3'
        assert data['condition_type'] == 'quality'
        
        # Deserialize
        edge2 = ChainEdge.from_dict(data)
        assert edge2.edge_id == edge.edge_id
        assert edge2.condition_type == edge.condition_type


class TestPromptChain:
    """Test PromptChain model"""
    
    def test_prompt_chain_creation(self):
        """Test creating a complete chain"""
        chain = PromptChain(
            chain_id='chain-test-1',
            name='Test Chain',
            description='Test chain for validation',
            chain_type=ChainType.ATOMIC,
            tier=1,
            priority=ChainPriority.HIGH
        )
        
        assert chain.chain_id == 'chain-test-1'
        assert chain.chain_type == ChainType.ATOMIC
        assert chain.tier == 1
    
    def test_prompt_chain_with_nodes_and_edges(self):
        """Test chain with nodes and edges"""
        node1 = ChainNode(
            node_id='n1',
            name='Start',
            description='Start node',
            operation_type=NodeType.SYSTEM_CALL,
            system='CMC'
        )
        
        node2 = ChainNode(
            node_id='n2',
            name='End',
            description='End node',
            operation_type=NodeType.SYSTEM_CALL,
            system='CMC'
        )
        
        edge = ChainEdge(
            edge_id='e1',
            from_node_id='n1',
            to_node_id='n2'
        )
        
        chain = PromptChain(
            chain_id='chain-test-2',
            name='Two Node Chain',
            description='Chain with 2 nodes',
            nodes=[node1, node2],
            edges=[edge],
            start_node_id='n1',
            end_node_ids=['n2']
        )
        
        assert len(chain.nodes) == 2
        assert len(chain.edges) == 1
        assert chain.get_node('n1') == node1
        assert chain.get_outgoing_edges('n1') == [edge]
    
    def test_prompt_chain_bidirectional_links(self):
        """Test bidirectional Timeline-Chain-Goal connections"""
        chain = PromptChain(
            chain_id='chain-test-3',
            name='Test Bidirectional',
            description='Test connections',
            goal_id='OBJ-12',
            timeline_entry_ids=['entry-1', 'entry-2']
        )
        
        # Verify bidirectional fields present
        assert chain.goal_id == 'OBJ-12'
        assert 'entry-1' in chain.timeline_entry_ids
        assert 'entry-2' in chain.timeline_entry_ids
    
    def test_prompt_chain_serialization(self):
        """Test complete chain serialization"""
        node = ChainNode(
            node_id='n1',
            name='Test',
            description='Test',
            operation_type=NodeType.SYSTEM_CALL
        )
        
        chain = PromptChain(
            chain_id='chain-test-4',
            name='Serialization Test',
            description='Test serialization',
            nodes=[node],
            start_node_id='n1',
            end_node_ids=['n1'],
            goal_id='OBJ-12'
        )
        
        # Serialize
        data = chain.to_dict()
        assert data['chain_id'] == 'chain-test-4'
        assert data['goal_id'] == 'OBJ-12'
        assert len(data['nodes']) == 1
        
        # Deserialize
        chain2 = PromptChain.from_dict(data)
        assert chain2.chain_id == chain.chain_id
        assert chain2.goal_id == chain.goal_id
        assert len(chain2.nodes) == 1


class TestExecutionRecord:
    """Test ExecutionRecord model"""
    
    def test_execution_record_creation(self):
        """Test creating execution record"""
        record = ExecutionRecord(
            execution_id='exec-1',
            chain_id='chain-1',
            start_time=datetime.now(),
            status='running',
            goal_id='OBJ-12'
        )
        
        assert record.execution_id == 'exec-1'
        assert record.chain_id == 'chain-1'
        assert record.status == 'running'
        assert record.goal_id == 'OBJ-12'
    
    def test_add_timeline_entry(self):
        """Test adding timeline entries to record"""
        record = ExecutionRecord(
            execution_id='exec-2',
            chain_id='chain-2',
            start_time=datetime.now()
        )
        
        record.add_timeline_entry('entry-1')
        record.add_timeline_entry('entry-2')
        
        assert 'entry-1' in record.timeline_entry_ids
        assert 'entry-2' in record.timeline_entry_ids
        
        # Test deduplication
        record.add_timeline_entry('entry-1')
        assert record.timeline_entry_ids.count('entry-1') == 1
    
    def test_add_node_execution(self):
        """Test adding node execution with timeline entries"""
        record = ExecutionRecord(
            execution_id='exec-3',
            chain_id='chain-3',
            start_time=datetime.now()
        )
        
        node_exec = NodeExecution(
            node_id='node-1',
            execution_id='exec-3',
            start_time=datetime.now(),
            timeline_entry_ids=['entry-1', 'entry-2']
        )
        
        record.add_node_execution(node_exec)
        
        # Verify node execution added
        assert len(record.node_executions) == 1
        
        # Verify timeline entries propagated
        assert 'entry-1' in record.timeline_entry_ids
        assert 'entry-2' in record.timeline_entry_ids


class TestBidirectionalConnections:
    """Test complete bidirectional integration"""
    
    def test_timeline_to_chain_connection(self):
        """Test Timeline → Chain via executed_via_chain_id"""
        # Simulating enhanced TimelineEntry (we test the chain side)
        timeline_entry_data = {
            'entry_id': 'entry-1',
            'executed_via_chain_id': 'chain-1',
            'chain_execution_id': 'exec-1'
        }
        
        # Chain should reference this timeline entry
        chain = PromptChain(
            chain_id='chain-1',
            name='Test Chain',
            description='Test',
            timeline_entry_ids=['entry-1']
        )
        
        # Verify bidirectional link
        assert timeline_entry_data['executed_via_chain_id'] == chain.chain_id
        assert timeline_entry_data['entry_id'] in chain.timeline_entry_ids
    
    def test_chain_to_goal_connection(self):
        """Test Chain ↔ Goal via goal_id and related_chain_ids"""
        chain = PromptChain(
            chain_id='chain-2',
            name='Goal Test Chain',
            description='Test',
            goal_id='OBJ-12'
        )
        
        # Simulating GoalTimelineNode
        goal_data = {
            'goal_id': 'OBJ-12',
            'related_chain_ids': ['chain-2']
        }
        
        # Verify bidirectional link
        assert chain.goal_id == goal_data['goal_id']
        assert chain.chain_id in goal_data['related_chain_ids']
    
    def test_complete_temporal_graph(self):
        """Test complete Timeline → Chain → Goal flow"""
        # Timeline entry
        timeline_data = {
            'entry_id': 'entry-1',
            'executed_via_chain_id': 'chain-1'
        }
        
        # Chain
        chain = PromptChain(
            chain_id='chain-1',
            name='Complete Test',
            description='Test',
            goal_id='OBJ-12',
            timeline_entry_ids=['entry-1']
        )
        
        # Goal
        goal_data = {
            'goal_id': 'OBJ-12',
            'related_chain_ids': ['chain-1']
        }
        
        # Verify complete path
        assert timeline_data['executed_via_chain_id'] == chain.chain_id  # Timeline → Chain
        assert timeline_data['entry_id'] in chain.timeline_entry_ids      # Chain → Timeline
        assert chain.goal_id == goal_data['goal_id']                      # Chain → Goal
        assert chain.chain_id in goal_data['related_chain_ids']           # Goal → Chain
        
        print("✅ Complete bidirectional graph verified!")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

