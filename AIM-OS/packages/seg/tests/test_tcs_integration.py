"""
Tests for TCS → SEG timeline entry integration.

Tests the transformation of TCS timeline entries into SEG evidence nodes
according to CHRONOS_TCS_SEG_TIMELINE_MAPPING.md.
"""

import pytest
from datetime import datetime, timezone
from seg.tcs_integration import timeline_entry_to_evidence, ingest_timeline_entry
from seg.seg_graph import SEGraph


def test_timeline_entry_to_evidence_basic():
    """Test basic timeline entry transformation."""
    timeline_entry = {
        "prompt_id": "prompt_f3921c",
        "timestamp": "2025-01-27T18:05:32.114Z",
        "summary": "Verified SEG↔CMC witness flow, documented gate evidence.",
        "context_index": {
            "active_tasks": ["SEG consolidation"],
            "files_read": ["packages/seg/models.py"],
            "insights_gained": ["Timeline entries contain CMC atom references"],
            "decisions_made": [{"decision": "Create shared mapping doc"}],
        },
        "confidence_metrics": {
            "average_confidence": 0.87,
        },
        "relevance_score": 0.88,
    }
    
    atom_id = "atom_9ac12e74"
    
    evidence, evidence_id = timeline_entry_to_evidence(
        timeline_entry=timeline_entry,
        atom_id=atom_id
    )
    
    # Verify basic fields
    assert evidence.content == "Verified SEG↔CMC witness flow, documented gate evidence."
    assert evidence.source.startswith("tcs.timeline_entry:")
    assert evidence.evidence_type == "timeline_entry"
    assert evidence.confidence == 0.87
    assert evidence.reliability == 0.95
    assert evidence.atom_id == atom_id
    assert "timeline" in evidence.tags
    assert "tcs" in evidence.tags
    
    # Verify metadata
    assert evidence.metadata["timeline_prompt_id"] == "prompt_f3921c"
    assert "timeline_timestamp" in evidence.metadata
    assert evidence.metadata["relevance_score"] == 0.88
    assert evidence.metadata["active_task"] == ["SEG consolidation"]
    assert evidence.metadata["files_read"] == ["packages/seg/models.py"]
    assert len(evidence.metadata["insights_gained"]) == 1
    assert len(evidence.metadata["decisions_made"]) == 1


def test_timeline_entry_to_evidence_with_graph():
    """Test timeline entry transformation with graph storage."""
    graph = SEGraph()
    
    timeline_entry = {
        "prompt_id": "prompt_test123",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": "Test timeline entry",
        "context_index": {},
        "confidence_metrics": {"average_confidence": 0.9},
    }
    
    atom_id = "atom_test123"
    
    evidence, evidence_id = timeline_entry_to_evidence(
        timeline_entry=timeline_entry,
        atom_id=atom_id,
        graph=graph
    )
    
    # Verify evidence was added to graph
    stored_evidence = graph.get_evidence(evidence_id)
    assert stored_evidence is not None
    assert stored_evidence.id == evidence_id
    assert stored_evidence.content == "Test timeline entry"


def test_ingest_timeline_entry_gate_evidence():
    """Test ingest function returns gate evidence tuple."""
    timeline_entry = {
        "prompt_id": "prompt_gate_test",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": "Gate evidence test",
        "context_index": {},
        "confidence_metrics": {"average_confidence": 0.85},
    }
    
    atom_id = "atom_gate_test"
    witness_id = "witness_gate_test"
    
    gate_evidence = ingest_timeline_entry(
        timeline_entry=timeline_entry,
        atom_id=atom_id,
        witness_id=witness_id
    )
    
    # Verify gate evidence tuple
    assert gate_evidence["timeline_prompt_id"] == "prompt_gate_test"
    assert gate_evidence["atom_id"] == atom_id
    assert "evidence_id" in gate_evidence
    assert gate_evidence["evidence_id"].startswith("evidence_")


def test_timeline_entry_with_chain_metadata():
    """Test timeline entry with chain execution metadata."""
    timeline_entry = {
        "prompt_id": "prompt_chain_test",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": "Chain execution test",
        "context_index": {},
        "confidence_metrics": {"average_confidence": 0.8},
        "executed_via_chain_id": "chain_123",
        "chain_execution_id": "exec_456",
        "chain_node_id": "node_789",
    }
    
    atom_id = "atom_chain_test"
    
    evidence, evidence_id = timeline_entry_to_evidence(
        timeline_entry=timeline_entry,
        atom_id=atom_id
    )
    
    # Verify chain metadata
    assert "chain_ids" in evidence.metadata
    assert evidence.metadata["chain_ids"]["executed_via_chain_id"] == "chain_123"
    assert evidence.metadata["chain_ids"]["chain_execution_id"] == "exec_456"
    assert evidence.metadata["chain_ids"]["chain_node_id"] == "node_789"


def test_timeline_entry_with_high_confidence_areas():
    """Test timeline entry with high confidence areas."""
    timeline_entry = {
        "prompt_id": "prompt_confidence_test",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": "Confidence test",
        "context_index": {},
        "confidence_metrics": {
            "average_confidence": 0.9,
            "high_confidence_areas": ["segmentation", "mapping"],
        },
    }
    
    atom_id = "atom_confidence_test"
    
    evidence, evidence_id = timeline_entry_to_evidence(
        timeline_entry=timeline_entry,
        atom_id=atom_id
    )
    
    # Verify high confidence areas in metadata
    assert "high_confidence_spans" in evidence.metadata
    assert evidence.metadata["high_confidence_spans"] == ["segmentation", "mapping"]


def test_timeline_entry_default_confidence():
    """Test timeline entry without confidence metrics uses default."""
    timeline_entry = {
        "prompt_id": "prompt_no_confidence",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": "No confidence test",
        "context_index": {},
    }
    
    atom_id = "atom_no_confidence"
    
    evidence, evidence_id = timeline_entry_to_evidence(
        timeline_entry=timeline_entry,
        atom_id=atom_id
    )
    
    # Verify default confidence (0.8)
    assert evidence.confidence == 0.8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

