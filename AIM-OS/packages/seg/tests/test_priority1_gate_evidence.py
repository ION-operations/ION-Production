"""
Priority 1 Gate Evidence Test

Tests the TCS → CMC → SEG integration workflow and captures
the gate evidence tuple: (timeline_prompt_id, atom_id, evidence_id)

This test is designed to be run with @Atlas coordination to capture
real gate evidence for gate_system_map_integrity and gate_dual_system.
"""

import pytest
from datetime import datetime, timezone
from seg.seg_graph import SEGraph
from seg.tcs_integration import ingest_timeline_entry


def _capture_priority1_gate_evidence():
    """
    Test Priority 1 gate evidence capture.
    
    This test simulates the TCS → CMC → SEG workflow:
    1. TCS creates timeline entry (simulated)
    2. CMC stores entry and returns atom_id (simulated - would come from Atlas)
    3. SEG ingests timeline entry and creates evidence node
    4. Capture gate evidence tuple: (timeline_prompt_id, atom_id, evidence_id)
    
    In real workflow, @Atlas would provide the actual atom_id from CMC.
    """
    # Initialize SEG graph
    graph = SEGraph()
    
    # Step 1: Simulate TCS timeline entry
    # (In real workflow, this would come from PromptContextTracker)
    timeline_entry = {
        "prompt_id": "prompt_priority1_test",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": "Priority 1 gate evidence test - TCS → CMC → SEG integration",
        "context_index": {
            "active_tasks": ["Priority 1 coordination"],
            "files_read": [
                "packages/seg/tcs_integration.py",
                "packages/timeline_context_system/prompt_context_tracker.py",
            ],
            "insights_gained": [
                "TCS timeline entries transform cleanly into SEG evidence nodes",
                "CMC atom_id provides the link between TCS and SEG",
            ],
            "decisions_made": [
                {
                    "decision": "Implement Priority 1 gate evidence capture",
                    "impact": "Unlock gate_system_map_integrity and gate_dual_system",
                }
            ],
        },
        "confidence_metrics": {
            "average_confidence": 0.95,
            "high_confidence_areas": ["integration", "mapping"],
        },
        "relevance_score": 0.92,
    }
    
    # Step 2: Simulate CMC atom storage
    # (In real workflow, this would come from Atlas's CMC create_atom())
    atom_id = "atom_priority1_test"  # Would be returned from CMC
    
    # Step 3: Optional VIF witness (if VIF observes timeline)
    witness_id = None  # Optional - would be provided if VIF observes
    
    # Step 4: Ingest timeline entry into SEG
    gate_evidence = ingest_timeline_entry(
        timeline_entry=timeline_entry,
        atom_id=atom_id,
        witness_id=witness_id,
        graph=graph,
    )
    
    # Step 5: Verify gate evidence tuple
    assert "timeline_prompt_id" in gate_evidence
    assert "atom_id" in gate_evidence
    assert "evidence_id" in gate_evidence
    
    assert gate_evidence["timeline_prompt_id"] == "prompt_priority1_test"
    assert gate_evidence["atom_id"] == atom_id
    assert gate_evidence["evidence_id"].startswith("evidence_")
    
    # Step 6: Verify evidence node in graph
    evidence = graph.get_evidence(gate_evidence["evidence_id"])
    assert evidence is not None
    assert evidence.content == "Priority 1 gate evidence test - TCS → CMC → SEG integration"
    assert evidence.atom_id == atom_id
    assert evidence.source.startswith("tcs.timeline_entry:")
    
    # Step 7: Return gate evidence tuple for script-mode journal storage
    return gate_evidence


def test_priority1_gate_evidence_capture():
    """Pytest wrapper: run gate evidence capture without returning values."""
    gate_evidence = _capture_priority1_gate_evidence()
    assert isinstance(gate_evidence, dict)


def test_priority1_gate_evidence_format():
    """
    Test that gate evidence tuple has correct format for gate registry.
    """
    graph = SEGraph()
    
    timeline_entry = {
        "prompt_id": "prompt_format_test",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": "Gate evidence format test",
        "context_index": {},
        "confidence_metrics": {"average_confidence": 0.9},
    }
    
    atom_id = "atom_format_test"
    
    gate_evidence = ingest_timeline_entry(
        timeline_entry=timeline_entry,
        atom_id=atom_id,
        graph=graph,
    )
    
    # Verify format matches gate registry requirements
    assert isinstance(gate_evidence, dict)
    assert len(gate_evidence) == 3
    assert all(key in gate_evidence for key in ["timeline_prompt_id", "atom_id", "evidence_id"])
    assert all(isinstance(value, str) for value in gate_evidence.values())


if __name__ == "__main__":
    # Run test and capture gate evidence
    gate_evidence = _capture_priority1_gate_evidence()
    print("\n✅ Priority 1 Gate Evidence Captured:")
    print(f"   timeline_prompt_id: {gate_evidence['timeline_prompt_id']}")
    print(f"   atom_id: {gate_evidence['atom_id']}")
    print(f"   evidence_id: {gate_evidence['evidence_id']}")
    print("\n📋 Gate Evidence Tuple (for journal):")
    print(f"   {gate_evidence}")

