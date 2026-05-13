"""
Tests for APOE → SEG integration.

Tests the bidirectional integration between APOE execution traces and SEG evidence nodes.
"""

import pytest
from datetime import datetime, timezone
from seg.apoe_integration import (
    store_execution_trace,
    get_plan_effectiveness,
    link_trace_to_evidence,
)
from seg.models import Evidence
from seg.seg_graph import SEGraph


def test_store_execution_trace_basic():
    """Test basic execution trace storage."""
    trace = {
        "plan_name": "test_plan",
        "execution_id": "exec_test123",
        "status": "completed",
        "success": True,
        "steps_completed": 5,
        "total_steps": 5,
        "duration_seconds": 10.5,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    
    graph = SEGraph()
    
    # Test that function handles missing APOE gracefully
    try:
        evidence_id = store_execution_trace(trace, graph)
        # If APOE not available, should raise ImportError
        assert False, "Should raise ImportError when APOE not available"
    except ImportError:
        # Expected when APOE not available
        pass


def test_store_execution_trace_with_graph():
    """Test execution trace storage with graph."""
    trace = {
        "plan_name": "test_plan",
        "execution_id": "exec_test456",
        "status": "completed",
        "success": True,
        "steps_completed": 3,
        "total_steps": 3,
        "duration_seconds": 5.0,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }
    
    graph = SEGraph()
    
    # Test that function handles missing APOE gracefully
    try:
        evidence_id = store_execution_trace(trace, graph, "exec_test456")
        # If APOE not available, should raise ImportError
        assert False, "Should raise ImportError when APOE not available"
    except ImportError:
        # Expected when APOE not available
        pass


def test_get_plan_effectiveness():
    """Test getting plan effectiveness score."""
    plan_id = "test_plan"
    graph = SEGraph()
    
    # Add some effectiveness evidence
    effectiveness_evidence = Evidence(
        content="Plan Effectiveness: test_plan - Score: 0.85",
        source="apoe.effectiveness:exec_test123",
        evidence_type="apoe_plan_effectiveness",
        confidence=0.85,
        metadata={
            "plan_name": plan_id,
            "execution_id": "exec_test123",
            "effectiveness_score": 0.85,
            "computed_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    graph.add_evidence(effectiveness_evidence)
    
    # Test that function handles missing APOE gracefully
    # Note: get_plan_effectiveness doesn't require APOE client, it queries graph
    # So it should work even when APOE package is not installed
    effectiveness = get_plan_effectiveness(plan_id, graph)
    # Should return effectiveness score (float 0.0-1.0)
    assert isinstance(effectiveness, (int, float))
    assert 0.0 <= effectiveness <= 1.0
    assert effectiveness == 0.85  # From the evidence we added


def test_link_trace_to_evidence():
    """Test linking trace to evidence."""
    graph = SEGraph()
    
    evidence = Evidence(
        content="Test evidence",
        source="test.source",
        evidence_type="test",
        confidence=0.9,
    )
    evidence = graph.add_evidence(evidence)
    
    trace_id = "exec_test123"
    
    # Test linking trace to evidence
    # Note: link_trace_to_evidence doesn't require APOE client, it works with graph
    link_trace_to_evidence(trace_id, evidence.id, graph)
    
    # Verify trace was linked
    updated_evidence = graph.get_evidence(evidence.id)
    assert updated_evidence is not None
    assert "apoe_traces" in updated_evidence.metadata
    assert trace_id in updated_evidence.metadata["apoe_traces"]


def test_apoe_integration_with_graph():
    """Test APOE integration with SEG graph."""
    graph = SEGraph()
    
    evidence = Evidence(
        content="APOE Execution Trace: test_plan",
        source="apoe.execution:exec_test123",
        evidence_type="apoe_execution_trace",
        confidence=0.9,
        metadata={
            "plan_name": "test_plan",
            "execution_id": "exec_test123",
            "status": "completed",
            "success": True,
        },
    )
    
    evidence = graph.add_evidence(evidence)
    
    # Verify evidence is in graph
    stored_evidence = graph.get_evidence(evidence.id)
    assert stored_evidence is not None
    assert stored_evidence.content == "APOE Execution Trace: test_plan"
    assert stored_evidence.metadata["plan_name"] == "test_plan"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

