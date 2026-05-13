"""
Tests for Prompt Chain Executor
Phase 1: Single Agent Dynamic Execution
"""

import pytest
from datetime import datetime
from prompt_chain_executor.executor import (
    ChainExecutor,
    ChainStatus,
    StepStatus,
    QualityGateStatus,
    StepResult,
    QualityGate,
    ChainExecutionState
)


class TestChainExecutor:
    """Test Chain Executor functionality"""
    
    def test_executor_initialization(self):
        """Test executor initialization"""
        executor = ChainExecutor()
        assert executor is not None
        assert executor.execution_states == {}
    
    def test_simple_sequential_chain(self):
        """Test simple sequential chain execution"""
        chain_definition = {
            "chain_id": "test_chain_1",
            "name": "Simple Sequential Chain",
            "description": "Test chain",
            "nodes": [
                {
                    "id": "start",
                    "type": "start",
                    "position": {"x": 100, "y": 100},
                    "label": "START"
                },
                {
                    "id": "step1",
                    "type": "prompt",
                    "position": {"x": 100, "y": 200},
                    "label": "Step 1",
                    "prompt": "Execute step 1"
                },
                {
                    "id": "end",
                    "type": "end",
                    "position": {"x": 100, "y": 300},
                    "label": "END"
                }
            ],
            "edges": [
                {
                    "id": "e1",
                    "source": "start",
                    "target": "step1",
                    "type": "sequential"
                },
                {
                    "id": "e2",
                    "source": "step1",
                    "target": "end",
                    "type": "sequential"
                }
            ],
            "executionType": "sequential",
            "entryPoint": "start"
        }
        
        executor = ChainExecutor()
        result = executor.execute_chain(
            chain_definition=chain_definition,
            inputs={},
            context={},
            agent_name="test_agent"
        )
        
        assert result.get("success") is True
        assert result.get("steps_completed") >= 1
    
    def test_quality_gate_chain(self):
        """Test chain with quality gates"""
        chain_definition = {
            "chain_id": "test_chain_2",
            "name": "Quality Gate Chain",
            "description": "Test chain with quality gates",
            "nodes": [
                {
                    "id": "start",
                    "type": "start",
                    "position": {"x": 100, "y": 100},
                    "label": "START"
                },
                {
                    "id": "step1",
                    "type": "prompt",
                    "position": {"x": 100, "y": 200},
                    "label": "Step 1",
                    "prompt": "Generate 100-word document",
                    "config": {
                        "quality_gates": [
                            {
                                "gate_id": "gate1",
                                "type": "document_size",
                                "field": "word_count",
                                "operator": ">=",
                                "value": 100,
                                "message": "Document must be at least 100 words"
                            }
                        ],
                        "maxRetries": 3
                    }
                },
                {
                    "id": "end",
                    "type": "end",
                    "position": {"x": 100, "y": 300},
                    "label": "END"
                }
            ],
            "edges": [
                {
                    "id": "e1",
                    "source": "start",
                    "target": "step1",
                    "type": "sequential"
                },
                {
                    "id": "e2",
                    "source": "step1",
                    "target": "end",
                    "type": "sequential"
                }
            ],
            "executionType": "sequential",
            "entryPoint": "start"
        }
        
        executor = ChainExecutor()
        
        # Test with word count meeting requirement
        result = executor.execute_chain(
            chain_definition=chain_definition,
            inputs={"content": "word " * 100},  # 100 words
            context={},
            agent_name="test_agent"
        )
        
        assert result.get("success") is True


class TestQualityGates:
    """Test quality gate evaluation"""
    
    def test_document_size_gate(self):
        """Test document size quality gate"""
        executor = ChainExecutor()
        
        step_result = StepResult(
            step_id="test_step",
            status=StepStatus.COMPLETED,
            word_count=150,
            quality_score=0.90,
            confidence=0.85
        )
        
        gate = QualityGate(
            gate_id="gate1",
            step_id="test_step",
            gate_type="document_size",
            field="word_count",
            operator=">=",
            value=100
        )
        
        passed = executor._evaluate_gate(gate, step_result, ChainExecutionState(
            chain_id="test",
            chain_instance_id="test_instance",
            status=ChainStatus.EXECUTING
        ))
        
        assert passed is True
    
    def test_quality_score_gate(self):
        """Test quality score gate"""
        executor = ChainExecutor()
        
        step_result = StepResult(
            step_id="test_step",
            status=StepStatus.COMPLETED,
            quality_score=0.95,
            confidence=0.85
        )
        
        gate = QualityGate(
            gate_id="gate1",
            step_id="test_step",
            gate_type="quality_score",
            field="quality_score",
            operator=">=",
            value=0.90
        )
        
        passed = executor._evaluate_gate(gate, step_result, ChainExecutionState(
            chain_id="test",
            chain_instance_id="test_instance",
            status=ChainStatus.EXECUTING
        ))
        
        assert passed is True
    
    def test_confidence_gate(self):
        """Test confidence gate"""
        executor = ChainExecutor()
        
        step_result = StepResult(
            step_id="test_step",
            status=StepStatus.COMPLETED,
            quality_score=0.90,
            confidence=0.75
        )
        
        gate = QualityGate(
            gate_id="gate1",
            step_id="test_step",
            gate_type="confidence",
            field="confidence",
            operator=">=",
            value=0.70
        )
        
        passed = executor._evaluate_gate(gate, step_result, ChainExecutionState(
            chain_id="test",
            chain_instance_id="test_instance",
            status=ChainStatus.EXECUTING
        ))
        
        assert passed is True
        
        # Test below threshold
        gate2 = QualityGate(
            gate_id="gate2",
            step_id="test_step",
            gate_type="confidence",
            field="confidence",
            operator=">=",
            value=0.80
        )
        
        passed2 = executor._evaluate_gate(gate2, step_result, ChainExecutionState(
            chain_id="test",
            chain_instance_id="test_instance",
            status=ChainStatus.EXECUTING
        ))
        
        assert passed2 is False


class TestConditionalBranching:
    """Test dynamic conditional branching"""
    
    def test_conditional_edge_evaluation(self):
        """Test conditional edge evaluation"""
        executor = ChainExecutor()
        
        execution_state = ChainExecutionState(
            chain_id="test",
            chain_instance_id="test_instance",
            status=ChainStatus.EXECUTING,
            chain_state={
                "quality_score": 0.95,
                "word_count": 2000
            }
        )
        
        step_result = StepResult(
            step_id="test_step",
            status=StepStatus.COMPLETED,
            quality_score=0.95,
            confidence=0.90,
            word_count=2000
        )
        
        edges = [
            {
                "id": "e1",
                "source": "test_step",
                "target": "next_step",
                "type": "conditional_true",
                "condition": "quality_score >= 0.90"
            }
        ]
        
        next_steps = executor._find_next_steps(edges, "test_step", step_result, execution_state)
        
        assert len(next_steps) == 1
        assert next_steps[0][0] == "next_step"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

