"""Tests for APOE CMC Integration v1"""

from __future__ import annotations
import pytest
from datetime import UTC, datetime
from unittest.mock import Mock

from apoe.cmc_integration_v1 import (
    APOECMC,
    PlanExecution,
    MemoryAwareExecutor,
)


def test_store_plan_start():
    """Test storing plan execution start."""
    store = APOECMC()
    
    exec_id = store.store_plan_start(
        plan_name="test_plan",
        execution_id="exec_001",
        total_steps=5,
        metadata={"user": "test"}
    )
    
    assert exec_id == "exec_001"
    assert "exec_001" in store._cache
    
    memory = store._cache["exec_001"]
    assert memory.plan_name == "test_plan"
    assert memory.status == "partial"
    assert memory.steps_completed == 0
    assert memory.total_steps == 5


def test_update_plan_progress():
    """Test updating plan execution progress."""
    store = APOECMC()
    
    store.store_plan_start("test_plan", "exec_001", total_steps=5)
    
    store.update_plan_progress(
        execution_id="exec_001",
        steps_completed=2,
        current_outputs={"step1": "done", "step2": "done"}
    )
    
    memory = store._cache["exec_001"]
    assert memory.steps_completed == 2
    assert "step1" in memory.outputs
    assert memory.status == "partial"


def test_store_plan_complete_success():
    """Test storing successful plan completion."""
    store = APOECMC()
    
    store.store_plan_start("test_plan", "exec_001", total_steps=3)
    
    store.store_plan_complete(
        execution_id="exec_001",
        final_outputs={"result": "success"},
        success=True
    )
    
    memory = store._cache["exec_001"]
    assert memory.status == "success"
    assert memory.completed_at is not None
    assert memory.outputs["result"] == "success"


def test_store_plan_complete_failure():
    """Test storing failed plan completion."""
    store = APOECMC()
    
    store.store_plan_start("test_plan", "exec_001", total_steps=3)
    
    store.store_plan_complete(
        execution_id="exec_001",
        final_outputs={"error": "Something failed"},
        success=False
    )
    
    memory = store._cache["exec_001"]
    assert memory.status == "failed"


def test_retrieve_plan_history():
    """Test retrieving plan execution history."""
    store = APOECMC()
    
    # Store multiple executions
    for i in range(3):
        exec_id = f"exec_00{i}"
        store.store_plan_start("test_plan", exec_id, total_steps=5)
        store.store_plan_complete(exec_id, {}, success=True)
    
    history = store.retrieve_plan_history("test_plan")
    
    assert len(history) == 3
    # Should be sorted by most recent first
    assert history[0].execution_id == "exec_002"


def test_retrieve_plan_history_with_limit():
    """Test retrieving plan history with limit."""
    store = APOECMC()
    
    # Store 15 executions
    for i in range(15):
        exec_id = f"exec_{i:03d}"
        store.store_plan_start("test_plan", exec_id, total_steps=3)
    
    history = store.retrieve_plan_history("test_plan", limit=10)
    
    assert len(history) == 10


def test_get_plan_statistics_no_history():
    """Test statistics for plan with no history."""
    store = APOECMC()
    
    stats = store.get_plan_statistics("nonexistent_plan")
    
    assert stats["total_executions"] == 0
    assert stats["success_rate"] == 0.0


def test_get_plan_statistics_with_history():
    """Test statistics calculation from history."""
    store = APOECMC()
    
    # 3 successes, 1 failure
    for i in range(4):
        exec_id = f"exec_00{i}"
        store.store_plan_start("test_plan", exec_id, total_steps=3)
        store.store_plan_complete(exec_id, {}, success=(i < 3))
    
    stats = store.get_plan_statistics("test_plan")
    
    assert stats["total_executions"] == 4
    assert stats["success_rate"] == 0.75  # 3/4
    assert stats["avg_steps"] == 3.0


def test_memory_aware_executor_stores_execution():
    """Test that memory-aware executor stores execution."""
    store = APOECMC()
    executor = MemoryAwareExecutor(store)
    
    # Mock plan
    class MockPlan:
        steps = [1, 2, 3]
    
    result = executor.execute_with_memory(
        plan_name="test_plan",
        plan=MockPlan(),
        execution_id="exec_001"
    )
    
    assert result["execution_id"] == "exec_001"
    assert result["success"]
    
    # Should be stored in CMC
    assert "exec_001" in store._cache


def test_should_retry_based_on_high_success_rate():
    """Test retry recommendation with high success rate."""
    store = APOECMC()
    executor = MemoryAwareExecutor(store)
    
    # Create history with high success rate
    for i in range(10):
        exec_id = f"exec_00{i}"
        store.store_plan_start("test_plan", exec_id, total_steps=3)
        store.store_plan_complete(exec_id, {}, success=(i < 8))  # 80% success
    
    should_retry = executor.should_retry_based_on_history(
        "test_plan",
        "Some error"
    )
    
    assert should_retry


def test_should_not_retry_based_on_low_success_rate():
    """Test no retry recommendation with low success rate."""
    store = APOECMC()
    executor = MemoryAwareExecutor(store)
    
    # Create history with low success rate
    for i in range(10):
        exec_id = f"exec_00{i}"
        store.store_plan_start("test_plan", exec_id, total_steps=3)
        store.store_plan_complete(exec_id, {}, success=(i < 3))  # 30% success
    
    should_retry = executor.should_retry_based_on_history(
        "test_plan",
        "Some error"
    )
    
    assert not should_retry


def test_should_not_retry_with_no_history():
    """Test no retry recommendation with no history."""
    store = APOECMC()
    executor = MemoryAwareExecutor(store)
    
    should_retry = executor.should_retry_based_on_history(
        "nonexistent_plan",
        "Some error"
    )
    
    assert not should_retry


def test_get_plan_recommendations():
    """Test getting plan recommendations from history."""
    store = APOECMC()
    executor = MemoryAwareExecutor(store)
    
    # Create good history
    for i in range(10):
        exec_id = f"exec_00{i}"
        store.store_plan_start("test_plan", exec_id, total_steps=3)
        store.store_plan_complete(exec_id, {}, success=True)
    
    recommendations = executor.get_plan_recommendations("test_plan")
    
    assert recommendations["confidence"] == 1.0  # 100% success
    assert recommendations["recommended_retries"] == 2  # High success rate
    assert len(recommendations["warnings"]) == 0


def test_recommendations_with_warnings():
    """Test recommendations include warnings for problematic plans."""
    store = APOECMC()
    executor = MemoryAwareExecutor(store)
    
    # Create history with low success
    for i in range(10):
        exec_id = f"exec_00{i}"
        store.store_plan_start("test_plan", exec_id, total_steps=3)
        store.store_plan_complete(exec_id, {}, success=(i < 3))  # 30% success
    
    recommendations = executor.get_plan_recommendations("test_plan")
    
    assert recommendations["confidence"] == 0.3
    assert recommendations["recommended_retries"] == 0
    assert len(recommendations["warnings"]) > 0
    assert "Low historical success rate" in recommendations["warnings"][0]


def test_store_to_cmc_calls_client_create_atom():
    """Ensure CMC client create_atom is called with expected payload (both AtomCreate and legacy paths)."""
    mock_client = Mock()
    mock_client.create_atom = Mock(return_value="atom_123")

    store = APOECMC(cmc_client=mock_client)
    exec_id = "exec_123"
    store.store_plan_start(
        plan_name="plan_xyz",
        execution_id=exec_id,
        total_steps=4,
        metadata={"origin": "unit_test"}
    )
    # Progress update should also call create_atom
    store.update_plan_progress(exec_id, steps_completed=2, current_outputs={"k": "v"})
    # Complete to exercise completed_at and duration
    store.store_plan_complete(exec_id, final_outputs={"result": "ok"}, success=True)

    # At least one call at start and one at progress and one at completion
    assert mock_client.create_atom.called
    calls = mock_client.create_atom.call_args_list
    
    # Check the last call (completion) - it may use AtomCreate payload or legacy kwargs
    last_call = calls[-1]
    
    # Try AtomCreate payload path first (modern path)
    if len(last_call.args) > 0 and hasattr(last_call.args[0], 'modality'):
        # AtomCreate payload path
        payload = last_call.args[0]
        assert payload.modality == "plan_execution"
        assert isinstance(payload.content.inline, str)  # JSON string
        tags = payload.tags
        metadata = payload.metadata
    else:
        # Legacy kwargs path
        _, kwargs = last_call
        assert kwargs["modality"] == "plan_execution"
        assert isinstance(kwargs["content"], str)  # JSON string
        tags = kwargs["tags"]
        metadata = kwargs["metadata"]
    
    # Verify all 5 required tags per spec
    assert "apoe" in tags
    assert "plan" in tags
    assert "execution" in tags  # Required by spec
    assert any(t.startswith("plan_name:") for t in tags)  # Pattern match
    assert any(t.startswith("status:") for t in tags)  # Pattern match
    
    # Verify metadata fields
    assert metadata["execution_id"] == exec_id
    assert "steps_completed" in metadata
    assert "total_steps" in metadata

def test_plan_execution_dataclass():
    """Test PlanExecution dataclass creation."""
    memory = PlanExecution(
        plan_name="test",
        execution_id="exec_001",
        started_at=datetime.now(UTC),
        completed_at=None,
        status="partial",
        steps_completed=2,
        total_steps=5,
        outputs={"step1": "done"}
    )
    
    assert memory.plan_name == "test"
    assert memory.status == "partial"  # Initial status is "partial" per spec
    assert memory.steps_completed == 2


def test_update_nonexistent_plan_raises_error():
    """Test updating nonexistent plan raises error."""
    store = APOECMC()
    
    with pytest.raises(ValueError, match="not found"):
        store.update_plan_progress("nonexistent", 1, {})


def test_complete_nonexistent_plan_raises_error():
    """Test completing nonexistent plan raises error."""
    store = APOECMC()
    
    with pytest.raises(ValueError, match="not found"):
        store.store_plan_complete("nonexistent", {}, True)
