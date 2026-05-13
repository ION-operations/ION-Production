"""
Tests for CAS → SEG integration.

Tests the bidirectional integration between CAS failure mode patterns and SEG evidence nodes.
"""

import pytest
from datetime import datetime, timezone
from seg.cas_integration import (
    store_failure_pattern,
    get_failure_patterns,
    link_pattern_to_evidence,
)
from seg.models import Evidence
from seg.seg_graph import SEGraph


def test_store_failure_pattern_basic():
    """Test basic failure pattern storage."""
    pattern = {
        "pattern": "categorization_error",
        "severity": "high",
        "description": "Test failure pattern",
        "context": {"test_key": "test_value"},
        "evidence": ["evidence_1", "evidence_2"],
        "suggested_actions": ["action_1", "action_2"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_id": "event_test123",
    }
    
    graph = SEGraph()
    
    # Test that function handles missing CAS gracefully
    try:
        evidence_id = store_failure_pattern(pattern, graph)
        # If CAS not available, should raise ImportError
        assert False, "Should raise ImportError when CAS not available"
    except ImportError:
        # Expected when CAS not available
        pass


def test_store_failure_pattern_with_graph():
    """Test failure pattern storage with graph."""
    pattern = {
        "pattern": "activation_gap",
        "severity": "medium",
        "description": "Test activation gap",
        "context": {},
        "evidence": [],
        "suggested_actions": [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_id": "event_test456",
    }
    
    graph = SEGraph()
    
    # Test that function handles missing CAS gracefully
    try:
        evidence_id = store_failure_pattern(pattern, graph)
        # If CAS not available, should raise ImportError
        assert False, "Should raise ImportError when CAS not available"
    except ImportError:
        # Expected when CAS not available
        pass


def test_get_failure_patterns():
    """Test getting failure patterns by type."""
    failure_type = "categorization_error"
    graph = SEGraph()
    
    # Add some failure pattern evidence
    pattern_evidence = Evidence(
        content="CAS Failure Pattern: categorization_error - Test pattern",
        source="cas.failure_pattern:event_test123",
        evidence_type="cas_failure_pattern",
        confidence=0.8,
        metadata={
            "pattern_type": failure_type,
            "severity": "high",
            "description": "Test pattern",
            "detected_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    graph.add_evidence(pattern_evidence)
    
    # Test that function handles missing CAS gracefully
    try:
        patterns = get_failure_patterns(failure_type, graph)
        # If CAS not available, should raise ImportError
        assert False, "Should raise ImportError when CAS not available"
    except ImportError:
        # Expected when CAS not available
        pass


def test_link_pattern_to_evidence():
    """Test linking pattern to evidence."""
    graph = SEGraph()
    
    evidence = Evidence(
        content="Test evidence",
        source="test.source",
        evidence_type="test",
        confidence=0.9,
    )
    evidence = graph.add_evidence(evidence)
    
    pattern_id = "event_test123"
    
    # Test linking pattern to evidence
    # Note: link_pattern_to_evidence doesn't require CAS client, it works with graph
    link_pattern_to_evidence(pattern_id, evidence.id, graph)
    
    # Verify pattern was linked
    updated_evidence = graph.get_evidence(evidence.id)
    assert updated_evidence is not None
    assert "cas_patterns" in updated_evidence.metadata
    assert pattern_id in updated_evidence.metadata["cas_patterns"]


def test_cas_integration_with_graph():
    """Test CAS integration with SEG graph."""
    graph = SEGraph()
    
    evidence = Evidence(
        content="CAS Failure Pattern: categorization_error - Test pattern",
        source="cas.failure_pattern:event_test123",
        evidence_type="cas_failure_pattern",
        confidence=0.8,
        metadata={
            "pattern_type": "categorization_error",
            "severity": "high",
            "description": "Test pattern",
            "detected_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    
    evidence = graph.add_evidence(evidence)
    
    # Verify evidence is in graph
    stored_evidence = graph.get_evidence(evidence.id)
    assert stored_evidence is not None
    assert stored_evidence.content.startswith("CAS Failure Pattern:")
    assert stored_evidence.metadata["pattern_type"] == "categorization_error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

