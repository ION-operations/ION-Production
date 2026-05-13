"""Tests for APOE TCS Integration

Tests timeline entry creation and query methods for TCS integration.
"""

from __future__ import annotations
import pytest
from datetime import UTC, datetime
from unittest.mock import Mock, MagicMock, patch

from apoe import ACLParser, PlanExecutor, StepStatus, Budget, RoleType
from apoe.models import Step, Gate
from apoe.tcs_integration import APOETCSIntegration
from apoe.executor import ExecutionResult


class TestAPOETCSIntegration:
    """Test TCS integration functionality."""
    
    def test_init_with_mcp_client(self):
        """Test initialization with MCP client."""
        mcp_client = Mock()
        integration = APOETCSIntegration(mcp_client=mcp_client)
        
        assert integration.mcp_client == mcp_client
        assert integration.enabled is True
    
    def test_init_without_mcp_client(self):
        """Test initialization without MCP client."""
        integration = APOETCSIntegration(mcp_client=None)
        
        assert integration.mcp_client is None
        assert integration.enabled is False
    
    def test_create_plan_start_entry(self):
        """Test creating plan start timeline entry."""
        mcp_client = Mock()
        mcp_client.call_tool = Mock(return_value={
            "entry_id": "entry_123",
            "atom_id": "atom_456",
            "timestamp": "2025-01-27T12:00:00Z"
        })
        
        integration = APOETCSIntegration(mcp_client=mcp_client)
        
        parser = ACLParser()
        plan = parser.parse("""
        PLAN test_plan:
          ROLE worker: llm(model="gpt-4")
          STEP step1:
            ASSIGN worker: "Do work"
        """)
        
        result = integration.create_plan_start_entry(plan, "exec_001")
        
        assert result is not None
        assert result["entry_id"] == "entry_123"
        mcp_client.call_tool.assert_called_once()
        call_args = mcp_client.call_tool.call_args
        assert call_args[0][0] == "mcp_lucid-mcp_add_timeline_entry"
        assert call_args[0][1]["event_type"] == "apoe_plan_start"
        assert call_args[0][1]["context_data"]["plan_name"] == "test_plan"
        assert call_args[0][1]["context_data"]["execution_id"] == "exec_001"
    
    def test_create_plan_complete_entry(self):
        """Test creating plan complete timeline entry."""
        mcp_client = Mock()
        mcp_client.call_tool = Mock(return_value={
            "entry_id": "entry_123",
            "atom_id": "atom_456",
            "timestamp": "2025-01-27T12:00:00Z"
        })
        
        integration = APOETCSIntegration(mcp_client=mcp_client)
        
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
        
        timeline_result = integration.create_plan_complete_entry(plan, "exec_001", result)
        
        assert timeline_result is not None
        mcp_client.call_tool.assert_called_once()
        call_args = mcp_client.call_tool.call_args
        assert call_args[0][1]["event_type"] == "apoe_plan_complete"
        assert call_args[0][1]["context_data"]["success"] is True
        assert call_args[0][1]["context_data"]["completed_steps"] == 1
    
    def test_create_step_start_entry(self):
        """Test creating step start timeline entry."""
        mcp_client = Mock()
        mcp_client.call_tool = Mock(return_value={
            "entry_id": "entry_123",
            "atom_id": "atom_456",
            "timestamp": "2025-01-27T12:00:00Z"
        })
        
        integration = APOETCSIntegration(mcp_client=mcp_client)
        
        step = Step(
            id="step_001",
            name="test_step",
            role=RoleType.PLANNER,
            description="Test step",
            budget=Budget(tokens_limit=1000, time_limit_seconds=10.0)
        )
        
        result = integration.create_step_start_entry(step, "test_plan", "exec_001")
        
        assert result is not None
        mcp_client.call_tool.assert_called_once()
        call_args = mcp_client.call_tool.call_args
        assert call_args[0][1]["event_type"] == "apoe_step_start"
        assert call_args[0][1]["context_data"]["step_id"] == "step_001"
        assert call_args[0][1]["context_data"]["role"] == "planner"
    
    def test_create_step_complete_entry(self):
        """Test creating step complete timeline entry."""
        mcp_client = Mock()
        mcp_client.call_tool = Mock(return_value={
            "entry_id": "entry_123",
            "atom_id": "atom_456",
            "timestamp": "2025-01-27T12:00:00Z"
        })
        
        integration = APOETCSIntegration(mcp_client=mcp_client)
        
        step = Step(
            id="step_001",
            name="test_step",
            role=RoleType.PLANNER,
            description="Test step",
            status=StepStatus.COMPLETED,
            outputs={"result": "success", "confidence": 0.95}
        )
        step.started_at = datetime.now(UTC)
        step.completed_at = datetime.now(UTC)
        
        result = integration.create_step_complete_entry(step, "test_plan", "exec_001")
        
        assert result is not None
        mcp_client.call_tool.assert_called_once()
        call_args = mcp_client.call_tool.call_args
        assert call_args[0][1]["event_type"] == "apoe_step_complete"
        assert call_args[0][1]["context_data"]["status"] == "completed"
        assert call_args[0][1]["context_data"]["confidence"] == 0.95
    
    def test_create_gate_evaluation_entry(self):
        """Test creating gate evaluation timeline entry."""
        mcp_client = Mock()
        mcp_client.call_tool = Mock(return_value={
            "entry_id": "entry_123",
            "atom_id": "atom_456",
            "timestamp": "2025-01-27T12:00:00Z"
        })
        
        integration = APOETCSIntegration(mcp_client=mcp_client)
        
        gate = Gate(
            id="gate_001",
            name="quality_gate",
            gate_type="quality",
            condition="output.confidence >= 0.95"
        )
        
        step = Step(
            id="step_001",
            name="test_step",
            role=RoleType.PLANNER,
            description="Test step"
        )
        
        result = integration.create_gate_evaluation_entry(
            gate=gate,
            step=step,
            plan_name="test_plan",
            execution_id="exec_001",
            passed=True,
            context={"output": type('obj', (object,), {"confidence": 0.96})()}
        )
        
        assert result is not None
        mcp_client.call_tool.assert_called_once()
        call_args = mcp_client.call_tool.call_args
        assert call_args[0][1]["event_type"] == "apoe_gate_evaluation"
        assert call_args[0][1]["context_data"]["result"] == "passed"
        assert call_args[0][1]["context_data"]["gate_id"] == "gate_001"
    
    def test_create_budget_milestone_entry(self):
        """Test creating budget milestone timeline entry."""
        mcp_client = Mock()
        mcp_client.call_tool = Mock(return_value={
            "entry_id": "entry_123",
            "atom_id": "atom_456",
            "timestamp": "2025-01-27T12:00:00Z"
        })
        
        integration = APOETCSIntegration(mcp_client=mcp_client)
        
        budget_data = {
            "tokens_limit": 10000,
            "tokens_consumed": 5000,
            "tokens_remaining": 5000,
            "time_limit": 300.0,
            "time_elapsed": 150.0,
            "time_remaining": 150.0
        }
        
        result = integration.create_budget_milestone_entry(
            plan_name="test_plan",
            execution_id="exec_001",
            milestone_type="50%_tokens_consumed",
            budget_data=budget_data,
            step_id="step_001"
        )
        
        assert result is not None
        mcp_client.call_tool.assert_called_once()
        call_args = mcp_client.call_tool.call_args
        assert call_args[0][1]["event_type"] == "apoe_budget_milestone"
        assert call_args[0][1]["context_data"]["milestone_type"] == "50%_tokens_consumed"
    
    def test_create_error_entry(self):
        """Test creating error timeline entry."""
        mcp_client = Mock()
        mcp_client.call_tool = Mock(return_value={
            "entry_id": "entry_123",
            "atom_id": "atom_456",
            "timestamp": "2025-01-27T12:00:00Z"
        })
        
        integration = APOETCSIntegration(mcp_client=mcp_client)
        
        result = integration.create_error_entry(
            error_type="execution_error",
            error_message="Test error",
            plan_name="test_plan",
            execution_id="exec_001",
            step_id="step_001",
            context={"additional": "context"}
        )
        
        assert result is not None
        mcp_client.call_tool.assert_called_once()
        call_args = mcp_client.call_tool.call_args
        assert call_args[0][1]["event_type"] == "apoe_error"
        assert call_args[0][1]["context_data"]["error_type"] == "execution_error"
        assert call_args[0][1]["context_data"]["error_message"] == "Test error"
    
    def test_query_execution_history(self):
        """Test querying execution history."""
        mcp_client = Mock()
        mcp_client.call_tool = Mock(return_value={
            "entries": [
                {"entry_id": "entry_1", "event_type": "apoe_plan_start"},
                {"entry_id": "entry_2", "event_type": "apoe_step_start"}
            ]
        })
        
        integration = APOETCSIntegration(mcp_client=mcp_client)
        
        entries = integration.query_execution_history("exec_001")
        
        assert len(entries) == 2
        mcp_client.call_tool.assert_called_once()
        call_args = mcp_client.call_tool.call_args
        assert call_args[0][0] == "mcp_lucid-mcp_get_timeline_entries"
        assert call_args[0][1]["metadata_filter"]["execution_id"] == "exec_001"
    
    def test_query_plan_history(self):
        """Test querying plan history."""
        mcp_client = Mock()
        mcp_client.call_tool = Mock(return_value={
            "entries": [
                {"entry_id": "entry_1", "event_type": "apoe_plan_start"}
            ]
        })
        
        integration = APOETCSIntegration(mcp_client=mcp_client)
        
        entries = integration.query_plan_history("plan_001", limit=10)
        
        assert len(entries) == 1
        mcp_client.call_tool.assert_called_once()
        call_args = mcp_client.call_tool.call_args
        assert call_args[0][1]["metadata_filter"]["plan_id"] == "plan_001"
        assert call_args[0][1]["limit"] == 10
    
    def test_restore_execution_state(self):
        """Test restoring execution state from timeline entries."""
        mcp_client = Mock()
        mcp_client.call_tool = Mock(return_value={
            "entries": [
                {
                    "entry_id": "entry_1",
                    "event_type": "apoe_plan_start",
                    "timestamp": "2025-01-27T12:00:00Z",
                    "context_data": {
                        "plan_id": "plan_001",
                        "plan_name": "test_plan",
                        "total_steps": 2
                    }
                },
                {
                    "entry_id": "entry_2",
                    "event_type": "apoe_step_start",
                    "timestamp": "2025-01-27T12:00:01Z",
                    "context_data": {
                        "step_id": "step_001",
                        "step_name": "test_step",
                        "role": "planner"
                    }
                },
                {
                    "entry_id": "entry_3",
                    "event_type": "apoe_step_complete",
                    "timestamp": "2025-01-27T12:00:05Z",
                    "context_data": {
                        "step_id": "step_001",
                        "status": "completed",
                        "confidence": 0.95,
                        "duration_seconds": 4.0
                    }
                },
                {
                    "entry_id": "entry_4",
                    "event_type": "apoe_plan_complete",
                    "timestamp": "2025-01-27T12:00:10Z",
                    "context_data": {
                        "success": True,
                        "completed_steps": 1,
                        "failed_steps": 0,
                        "total_duration_seconds": 10.0
                    }
                }
            ]
        })
        
        integration = APOETCSIntegration(mcp_client=mcp_client)
        
        state = integration.restore_execution_state("exec_001")
        
        assert state["execution_id"] == "exec_001"
        assert state["plan_id"] == "plan_001"
        assert state["plan_name"] == "test_plan"
        assert state["total_steps"] == 2
        assert state["completed_steps"] == 1
        assert state["success"] is True
        assert "step_001" in state["steps"]
        assert state["steps"]["step_001"]["status"] == "completed"
    
    def test_analyze_execution_performance(self):
        """Test analyzing execution performance."""
        mcp_client = Mock()
        mcp_client.call_tool = Mock(return_value={
            "entries": [
                {
                    "entry_id": "entry_1",
                    "event_type": "apoe_step_complete",
                    "context_data": {
                        "step_id": "step_001",
                        "step_name": "test_step",
                        "role": "planner",
                        "duration_seconds": 5.0,
                        "status": "completed"
                    }
                },
                {
                    "entry_id": "entry_2",
                    "event_type": "apoe_gate_evaluation",
                    "context_data": {
                        "gate_id": "gate_001",
                        "result": "passed",
                        "step_id": "step_001"
                    }
                },
                {
                    "entry_id": "entry_3",
                    "event_type": "apoe_error",
                    "context_data": {
                        "error_type": "execution_error",
                        "error_message": "Test error"
                    }
                }
            ]
        })
        
        integration = APOETCSIntegration(mcp_client=mcp_client)
        
        performance = integration.analyze_execution_performance("exec_001")
        
        assert performance["execution_id"] == "exec_001"
        assert performance["step_count"] == 1
        assert performance["total_duration_seconds"] == 5.0
        assert performance["gate_evaluations"] == 1
        assert performance["gate_pass_rate"] == 1.0
        assert performance["errors"] == 1
        assert len(performance["step_durations"]) == 1
        assert len(performance["gate_evaluations_details"]) == 1
        assert len(performance["errors_details"]) == 1
    
    def test_integration_disabled_returns_none(self):
        """Test that integration returns None when disabled."""
        integration = APOETCSIntegration(mcp_client=None)
        
        parser = ACLParser()
        plan = parser.parse("""
        PLAN test:
          ROLE worker: llm(model="gpt-4")
          STEP step1:
            ASSIGN worker: "Do work"
        """)
        
        result = integration.create_plan_start_entry(plan, "exec_001")
        assert result is None
    
    def test_mcp_client_error_handling(self):
        """Test that MCP client errors don't crash execution."""
        mcp_client = Mock()
        mcp_client.call_tool = Mock(side_effect=Exception("MCP error"))
        
        integration = APOETCSIntegration(mcp_client=mcp_client)
        
        parser = ACLParser()
        plan = parser.parse("""
        PLAN test:
          ROLE worker: llm(model="gpt-4")
          STEP step1:
            ASSIGN worker: "Do work"
        """)
        
        # Should not raise exception
        result = integration.create_plan_start_entry(plan, "exec_001")
        assert result is None


