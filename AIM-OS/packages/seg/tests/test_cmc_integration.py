"""
Tests for CMC → SEG integration.

Tests the bidirectional integration between CMC atoms and SEG evidence nodes.
"""

import pytest
from datetime import datetime, timezone
from seg.cmc_integration import (
    store_evidence_in_cmc,
    retrieve_evidence_from_cmc,
    link_evidence_to_cmc,
)
from seg.models import Evidence
from seg.seg_graph import SEGraph


def test_store_evidence_in_cmc_basic():
    """Test basic evidence storage in CMC."""
    evidence = Evidence(
        content="Test evidence",
        source="test.source",
        evidence_type="test",
        confidence=0.9,
        reliability=0.85,
    )
    
    # Mock CMC store (would be actual CMC client in production)
    cmc_store = None  # Would be CMCClient() in production
    
    # Test that function handles missing CMC gracefully
    try:
        atom_id = store_evidence_in_cmc(evidence, cmc_store)
        # If CMC not available, should raise ImportError
        assert False, "Should raise ImportError when CMC not available"
    except ImportError:
        # Expected when CMC not available
        pass


def test_retrieve_evidence_from_cmc_basic():
    """Test basic evidence retrieval from CMC."""
    atom_id = "atom_test123"
    
    # Mock CMC store
    cmc_store = None
    
    # Test that function handles missing CMC gracefully
    try:
        evidence = retrieve_evidence_from_cmc(atom_id, cmc_store)
        # If CMC not available, should raise ImportError
        assert False, "Should raise ImportError when CMC not available"
    except ImportError:
        # Expected when CMC not available
        pass


def test_link_evidence_to_cmc_basic():
    """Test linking evidence to CMC atom."""
    evidence = Evidence(
        content="Test evidence",
        source="test.source",
        evidence_type="test",
        confidence=0.9,
    )
    
    graph = SEGraph()
    evidence = graph.add_evidence(evidence)
    
    atom_id = "atom_test123"
    
    # Test linking (function doesn't require CMC store, just updates evidence)
    link_evidence_to_cmc(evidence.id, atom_id, graph)
    
    # Verify evidence was updated with atom_id
    updated_evidence = graph.get_evidence(evidence.id)
    assert updated_evidence is not None
    assert updated_evidence.atom_id == atom_id


def test_cmc_integration_with_graph():
    """Test CMC integration with SEG graph."""
    graph = SEGraph()
    
    evidence = Evidence(
        content="Test evidence for CMC",
        source="test.cmc",
        evidence_type="test",
        confidence=0.9,
        metadata={"test_key": "test_value"},
    )
    
    evidence = graph.add_evidence(evidence)
    
    # Verify evidence is in graph
    stored_evidence = graph.get_evidence(evidence.id)
    assert stored_evidence is not None
    assert stored_evidence.content == "Test evidence for CMC"
    assert stored_evidence.metadata["test_key"] == "test_value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

