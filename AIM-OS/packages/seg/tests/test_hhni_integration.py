"""
Tests for HHNI → SEG integration.

Tests the bidirectional integration between HHNI semantic search and SEG evidence nodes.
"""

import pytest
from datetime import datetime, timezone
from seg.hhni_integration import (
    synthesize_evidence,
    get_synthesis_context,
    index_evidence_for_hhni,
)
from seg.models import Evidence
from seg.seg_graph import SEGraph


def test_synthesize_evidence_basic():
    """Test basic evidence synthesis via HHNI."""
    graph = SEGraph()
    
    # Add some test evidence
    evidence1 = Evidence(
        content="Test evidence 1",
        source="test.source1",
        evidence_type="test",
        confidence=0.9,
    )
    evidence2 = Evidence(
        content="Test evidence 2",
        source="test.source2",
        evidence_type="test",
        confidence=0.85,
    )
    graph.add_evidence(evidence1)
    graph.add_evidence(evidence2)
    
    query = "test query"
    
    # Mock HHNI retriever (would be actual HHNI client in production)
    hhni_retriever = None  # Would be HHNIRetriever() in production
    
    # Test that function handles missing HHNI gracefully
    try:
        result = synthesize_evidence(query, graph, hhni_retriever)
        # If HHNI not available, should raise ImportError
        assert False, "Should raise ImportError when HHNI not available"
    except ImportError:
        # Expected when HHNI not available
        pass


def test_get_synthesis_context():
    """Test getting synthesis context."""
    evidence_ids = ["evidence_1", "evidence_2", "evidence_3"]
    
    # Mock HHNI retriever
    hhni_retriever = None
    
    # Test that function handles missing HHNI gracefully
    try:
        context = get_synthesis_context(evidence_ids, hhni_retriever)
        # If HHNI not available, should raise ImportError
        assert False, "Should raise ImportError when HHNI not available"
    except ImportError:
        # Expected when HHNI not available
        pass


def test_index_evidence_for_hhni():
    """Test indexing evidence for HHNI."""
    evidence = Evidence(
        content="Test evidence for indexing",
        source="test.source",
        evidence_type="test",
        confidence=0.9,
    )
    
    # Mock HHNI indexer (would be actual HHNI client in production)
    hhni_indexer = None  # Would be HHNIIndexer() in production
    
    # Test that function handles missing HHNI gracefully
    try:
        index_id = index_evidence_for_hhni(evidence, hhni_indexer)
        # If HHNI not available, should raise ImportError
        assert False, "Should raise ImportError when HHNI not available"
    except ImportError:
        # Expected when HHNI not available
        pass


def test_hhni_integration_with_graph():
    """Test HHNI integration with SEG graph."""
    graph = SEGraph()
    
    evidence = Evidence(
        content="Test evidence for HHNI",
        source="test.hhni",
        evidence_type="test",
        confidence=0.9,
        metadata={"test_key": "test_value"},
    )
    
    evidence = graph.add_evidence(evidence)
    
    # Verify evidence is in graph
    stored_evidence = graph.get_evidence(evidence.id)
    assert stored_evidence is not None
    assert stored_evidence.content == "Test evidence for HHNI"
    assert stored_evidence.metadata["test_key"] == "test_value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

