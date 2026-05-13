"""Tests for APOE SEG Integration

Tests execution trace storage and plan effectiveness computation for SEG integration.
"""

from __future__ import annotations
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from apoe import ACLParser, PlanExecutor, StepStatus, Budget, RoleType
from apoe.models import Step
from apoe.seg_integration import APOESEGIntegration
from apoe.executor import ExecutionResult


class TestAPOESEGIntegration:
    """Test SEG integration functionality."""
    
    @pytest.fixture
    def mock_seg_graph(self):
        """Create mock SEG graph."""
        seg_graph = Mock()
        seg_graph.create_evidence = Mock(return_value="evidence_123")
        seg_graph.create_relation = Mock(return_value="relation_456")
        seg_graph.list_evidence = Mock(return_value=[])
        seg_graph.get_evidence = Mock(return_value=None)
        seg_graph.get_outgoing_relations = Mock(return_value=[])
        return seg_graph
    
    def test_init_with_seg_graph(self, mock_seg_graph):
        """Test initialization with SEG graph."""
        integration = APOESEGIntegration(seg_graph=mock_seg_graph)
        
        assert integration.seg == mock_seg_graph
        assert integration.seg_available is True
    
    def test_init_without_seg_graph(self):
        """Test initialization without SEG graph."""
        integration = APOESEGIntegration(seg_graph=None)
        
        assert integration.seg is None
        assert integration.seg_available is False
    
    def test_store_execution_trace_plan_level(self, mock_seg_graph):
        """Test storing plan-level execution trace."""
        integration = APOESEGIntegration(seg_graph=mock_seg_graph)
        
        parser = ACLParser()
        plan = parser.parse("""
        PLAN test_plan:
          ROLE worker: llm(model="gpt-4")
          STEP step1:
            ASSIGN worker: "Do work"
        """)
        
        result = ExecutionResult(
            plan_name="test_plan",
            total_steps=1,
            completed_steps=1,
            failed_steps=0,
            skipped_steps=0,
            total_duration_seconds=5.0,
            success=True
        )
        
        trace_result = integration.store_execution_trace(
            plan=plan,
            result=result,
            execution_id="exec_001",
            vif_witness_id="witness_123"
        )
        
        assert trace_result is not None
        assert "plan_evidence_id" in trace_result
        assert trace_result["plan_evidence_id"] == "evidence_123"
        mock_seg_graph.create_evidence.assert_called()
    
    def test_store_execution_trace_with_dependencies(self, mock_seg_graph):
        """Test storing execution trace with step dependencies."""
        # Mock evidence creation
        mock_evidence_plan = Mock()
        mock_evidence_plan.id = "evidence_plan"
        mock_evidence_step1 = Mock()
        mock_evidence_step1.id = "evidence_step1"
        mock_evidence_step2 = Mock()
        mock_evidence_step2.id = "evidence_step2"
        
        mock_seg_graph.add_evidence = Mock()
        mock_seg_graph.add_relation = Mock()
        
        integration = APOESEGIntegration(seg_graph=mock_seg_graph)
        
        # Mock the internal evidence creation
        with patch.object(integration, '_create_plan_evidence', return_value=mock_evidence_plan):
            with patch.object(integration, '_create_step_evidence', side_effect=[mock_evidence_step1, mock_evidence_step2]):
                parser = ACLParser()
                plan = parser.parse("""
                PLAN test_plan:
                  ROLE worker: llm(model="gpt-4")
                  STEP step1:
                    ASSIGN worker: "First"
                  STEP step2:
                    ASSIGN worker: "Second"
                    REQUIRES step1
                """)
                
                # Mark steps as completed
                plan.steps[0].status = StepStatus.COMPLETED
                plan.steps[1].status = StepStatus.COMPLETED
                
                result = ExecutionResult(
                    plan_name="test_plan",
                    total_steps=2,
                    completed_steps=2,
                    failed_steps=0,
                    skipped_steps=0,
                    total_duration_seconds=10.0,
                    success=True
                )
                
                trace_result = integration.store_execution_trace(plan, result, "exec_001")
                
                assert trace_result is not None
                assert "plan_evidence_id" in trace_result
                assert "step_evidence_ids" in trace_result
                assert len(trace_result["step_evidence_ids"]) == 2
                # Relations should be created internally
                assert mock_seg_graph.add_relation.called
    
    def test_compute_plan_effectiveness(self, mock_seg_graph):
        """Test computing plan effectiveness."""
        integration = APOESEGIntegration(seg_graph=mock_seg_graph)
        
        parser = ACLParser()
        plan = parser.parse("""
        PLAN test_plan:
          ROLE worker: llm(model="gpt-4")
          STEP step1:
            ASSIGN worker: "Do work"
        """)
        
        result = ExecutionResult(
            plan_name="test_plan",
            total_steps=1,
            completed_steps=1,
            failed_steps=0,
            skipped_steps=0,
            total_duration_seconds=5.0,
            success=True
        )
        
        effectiveness = integration.compute_plan_effectiveness(
            plan=plan,
            result=result,
            execution_id="exec_001"
        )
        
        assert effectiveness is not None
        assert "effectiveness_score" in effectiveness
        assert "metrics" in effectiveness
        assert effectiveness["effectiveness_score"] > 0.0
        assert effectiveness["metrics"]["completion_rate"] == 1.0
        assert effectiveness["metrics"]["success_rate"] == 1.0
    
    def test_store_plan_effectiveness(self, mock_seg_graph):
        """Test storing plan effectiveness."""
        mock_evidence = Mock()
        mock_evidence.id = "evidence_effectiveness"
        mock_plan_evidence = Mock()
        mock_plan_evidence.id = "evidence_plan"
        
        mock_seg_graph.add_evidence = Mock()
        mock_seg_graph.add_relation = Mock()
        mock_seg_graph.get_evidence = Mock(return_value=mock_plan_evidence)
        
        integration = APOESEGIntegration(seg_graph=mock_seg_graph)
        
        # Mock the Evidence creation
        with patch('apoe.seg_integration.Evidence', return_value=mock_evidence):
            effectiveness_id = integration.store_plan_effectiveness(
                plan_name="test_plan",
                execution_id="exec_001",
                effectiveness_score=0.95,
                metrics={"completion_rate": 1.0, "success_rate": 1.0},
                plan_evidence_id="evidence_plan"
            )
            
            assert effectiveness_id == "evidence_effectiveness"
            mock_seg_graph.add_evidence.assert_called_once()
    
    def test_query_execution_traces(self, mock_seg_graph):
        """Test querying execution traces."""
        mock_evidence = Mock()
        mock_evidence.id = "evidence_001"
        mock_evidence.evidence_type = "apoe_plan_execution"
        mock_evidence.tags = ["apoe", "test_plan"]
        mock_evidence.metadata = {"execution_id": "exec_001", "plan_name": "test_plan"}
        
        mock_seg_graph.list_evidence = Mock(return_value=[mock_evidence])
        
        integration = APOESEGIntegration(seg_graph=mock_seg_graph)
        
        traces = integration.query_execution_traces(
            plan_name="test_plan",
            execution_id="exec_001"
        )
        
        assert len(traces) == 1
        assert traces[0].id == "evidence_001"
    
    def test_integration_disabled_returns_none(self):
        """Test that integration returns None when disabled."""
        integration = APOESEGIntegration(seg_graph=None)
        
        parser = ACLParser()
        plan = parser.parse("""
        PLAN test:
          ROLE worker: llm(model="gpt-4")
          STEP step1:
            ASSIGN worker: "Do work"
        """)
        
        result = ExecutionResult(
            plan_name="test",
            total_steps=1,
            completed_steps=1,
            failed_steps=0,
            skipped_steps=0,
            total_duration_seconds=5.0,
            success=True
        )
        
        trace_result = integration.store_execution_trace(plan, result, "exec_001")
        assert trace_result is None
    
    def test_seg_error_handling(self, mock_seg_graph):
        """Test that SEG errors don't crash execution."""
        mock_seg_graph.create_evidence = Mock(side_effect=Exception("SEG error"))
        
        integration = APOESEGIntegration(seg_graph=mock_seg_graph)
        
        parser = ACLParser()
        plan = parser.parse("""
        PLAN test:
          ROLE worker: llm(model="gpt-4")
          STEP step1:
            ASSIGN worker: "Do work"
        """)
        
        result = ExecutionResult(
            plan_name="test",
            total_steps=1,
            completed_steps=1,
            failed_steps=0,
            skipped_steps=0,
            total_duration_seconds=5.0,
            success=True
        )
        
        # Should not raise exception
        trace_result = integration.store_execution_trace(plan, result, "exec_001")
        assert trace_result is None
