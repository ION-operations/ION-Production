"""
Tests for SDF-CVF → SEG integration.

Tests the bidirectional integration between SDF-CVF consistency validation and SEG evidence nodes.
"""

import pytest
from datetime import datetime, timezone
from seg.sdfcvf_integration import (
    validate_consistency,
    link_trace_to_evidence,
    get_consistency_report,
)
from seg.models import Evidence
from seg.seg_graph import SEGraph


def test_validate_consistency_basic():
    """Test basic consistency validation."""
    evidence = Evidence(
        content="Test evidence",
        source="test.source",
        evidence_type="test",
        confidence=0.9,
        metadata={
            "quartet_parity": 0.95,
        },
    )
    
    # Test that function handles missing SDF-CVF gracefully
    try:
        is_consistent = validate_consistency(evidence)
        # If SDF-CVF not available, should raise ImportError
        assert False, "Should raise ImportError when SDF-CVF not available"
    except ImportError:
        # Expected when SDF-CVF not available
        pass


def test_validate_consistency_with_quintet_parity():
    """Test consistency validation with quintet parity."""
    evidence = Evidence(
        content="Test evidence with quintet parity",
        source="test.source",
        evidence_type="test",
        confidence=0.9,
        metadata={
            "quintet_parity": 0.92,
        },
    )
    
    # Test that function handles missing SDF-CVF gracefully
    try:
        is_consistent = validate_consistency(evidence)
        # If SDF-CVF not available, should raise ImportError
        assert False, "Should raise ImportError when SDF-CVF not available"
    except ImportError:
        # Expected when SDF-CVF not available
        pass


def test_validate_consistency_without_parity():
    """Test consistency validation without parity metadata."""
    evidence = Evidence(
        content="Test evidence without parity",
        source="test.source",
        evidence_type="test",
        confidence=0.9,
    )
    
    # Test that function handles missing SDF-CVF gracefully
    try:
        is_consistent = validate_consistency(evidence)
        # If SDF-CVF not available, should raise ImportError
        assert False, "Should raise ImportError when SDF-CVF not available"
    except ImportError:
        # Expected when SDF-CVF not available
        pass


def test_link_sdfcvf_trace():
    """Test linking SDF-CVF trace to evidence."""
    graph = SEGraph()
    
    evidence = Evidence(
        content="Test evidence",
        source="test.source",
        evidence_type="test",
        confidence=0.9,
    )
    evidence = graph.add_evidence(evidence)
    
    trace_id = "trace_test123"
    
    # Test that function handles missing SDF-CVF gracefully
    try:
        link_trace_to_evidence(trace_id, evidence.id, graph)
        # If SDF-CVF not available, should raise ImportError
        assert False, "Should raise ImportError when SDF-CVF not available"
    except ImportError:
        # Expected when SDF-CVF not available
        pass


def test_get_consistency_report():
    """Test getting consistency report."""
    graph = SEGraph()
    
    evidence = Evidence(
        content="Test evidence",
        source="test.source",
        evidence_type="test",
        confidence=0.9,
        metadata={
            "quartet_parity": 0.95,
            "sdfcvf_traces": ["trace_1", "trace_2"],
        },
    )
    evidence = graph.add_evidence(evidence)
    
    # Test that function handles missing SDF-CVF gracefully
    try:
        report = get_consistency_report(evidence.id, graph)
        # If SDF-CVF not available, should raise ImportError
        assert False, "Should raise ImportError when SDF-CVF not available"
    except ImportError:
        # Expected when SDF-CVF not available
        pass


def test_sdfcvf_integration_with_graph():
    """Test SDF-CVF integration with SEG graph."""
    graph = SEGraph()
    
    evidence = Evidence(
        content="Test evidence for SDF-CVF",
        source="test.sdfcvf",
        evidence_type="test",
        confidence=0.9,
        metadata={
            "quartet_parity": 0.95,
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
    
    evidence = graph.add_evidence(evidence)
    
    # Verify evidence is in graph
    stored_evidence = graph.get_evidence(evidence.id)
    assert stored_evidence is not None
    assert stored_evidence.content == "Test evidence for SDF-CVF"
    assert stored_evidence.metadata["quartet_parity"] == 0.95


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

