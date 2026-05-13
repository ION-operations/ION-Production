"""
Priority 1 End-to-End Test: TCS → CMC → SEG Integration

Complete end-to-end test using Atlas's CMC helper function and Nexus's SEG integration
to capture the gate evidence tuple: (timeline_prompt_id, atom_id, evidence_id)

This test demonstrates the complete Priority 1 workflow:
1. Create test timeline entry (using Atlas's helper)
2. Store in CMC (using Atlas's helper) → get atom_id
3. Ingest into SEG (using Nexus's integration) → get evidence_id
4. Capture gate evidence tuple
5. Verify complete integration
"""

import pytest
import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from seg.seg_graph import SEGraph
from seg.tcs_integration import ingest_timeline_entry

# Import Atlas's CMC helper functions
try:
    from cmc_service.tcs_seg_integration_helper import (
        store_timeline_entry_for_seg,
        create_test_timeline_entry_for_gate_evidence,
    )
    from cmc_service import MemoryStore
    CMC_AVAILABLE = True
except ImportError:
    CMC_AVAILABLE = False
    pytest.skip("CMC service not available", allow_module_level=True)


def _capture_priority1_end_to_end_gate_evidence():
    """
    Complete end-to-end test for Priority 1 gate evidence capture.
    
    This test runs the complete workflow:
    1. Create test timeline entry (Atlas helper)
    2. Store in CMC (Atlas helper) → atom_id
    3. Ingest into SEG (Nexus integration) → evidence_id
    4. Capture gate evidence tuple
    5. Verify integration
    """
    # Initialize stores
    cmc_store = MemoryStore("./test_data_priority1")
    seg_graph = SEGraph()
    
    # Step 1: Create test timeline entry (using Atlas's helper)
    timeline_entry = create_test_timeline_entry_for_gate_evidence()
    prompt_id = timeline_entry["prompt_id"]
    
    # Step 2: Store in CMC (using Atlas's helper) → get atom_id
    atom_id = store_timeline_entry_for_seg(
        cmc_store=cmc_store,
        timeline_entry=timeline_entry,
    )
    
    assert atom_id is not None
    assert isinstance(atom_id, str)
    assert len(atom_id) > 0
    
    # Step 3: Ingest into SEG (using Nexus's integration) → get evidence_id
    gate_evidence = ingest_timeline_entry(
        timeline_entry=timeline_entry,
        atom_id=atom_id,  # From CMC (Atlas)
        witness_id=None,  # Optional
        graph=seg_graph,
    )
    
    # Step 4: Verify gate evidence tuple
    assert "timeline_prompt_id" in gate_evidence
    assert "atom_id" in gate_evidence
    assert "evidence_id" in gate_evidence
    
    assert gate_evidence["timeline_prompt_id"] == prompt_id
    assert gate_evidence["atom_id"] == atom_id
    assert gate_evidence["evidence_id"].startswith("evidence_")
    
    # Step 5: Verify evidence node in SEG graph
    evidence = seg_graph.get_evidence(gate_evidence["evidence_id"])
    assert evidence is not None
    assert evidence.atom_id == atom_id
    assert evidence.content == timeline_entry["summary"]
    assert evidence.source.startswith("tcs.timeline_entry:")
    
    # Step 6: Verify metadata
    assert evidence.metadata["timeline_prompt_id"] == prompt_id
    assert "timeline_timestamp" in evidence.metadata
    assert "active_task" in evidence.metadata or "active_tasks" in evidence.metadata
    
    # Step 7: Return gate evidence tuple for script-mode journal storage
    return gate_evidence


def test_priority1_end_to_end_gate_evidence():
    """Pytest wrapper: run end-to-end capture without returning values."""
    gate_evidence = _capture_priority1_end_to_end_gate_evidence()
    assert isinstance(gate_evidence, dict)


def test_priority1_gate_evidence_format():
    """
    Test that gate evidence tuple has correct format for gate registry.
    """
    cmc_store = MemoryStore("./test_data_priority1_format")
    seg_graph = SEGraph()
    
    # Create test timeline entry
    timeline_entry = create_test_timeline_entry_for_gate_evidence()
    
    # Store in CMC
    atom_id = store_timeline_entry_for_seg(
        cmc_store=cmc_store,
        timeline_entry=timeline_entry,
    )
    
    # Ingest into SEG
    gate_evidence = ingest_timeline_entry(
        timeline_entry=timeline_entry,
        atom_id=atom_id,
        graph=seg_graph,
    )
    
    # Verify format matches gate registry requirements
    assert isinstance(gate_evidence, dict)
    assert len(gate_evidence) == 3
    assert all(key in gate_evidence for key in ["timeline_prompt_id", "atom_id", "evidence_id"])
    assert all(isinstance(value, str) for value in gate_evidence.values())
    assert all(len(value) > 0 for value in gate_evidence.values())


def test_priority1_cmc_seg_linkage():
    """
    Test that CMC atom and SEG evidence are properly linked.
    """
    cmc_store = MemoryStore("./test_data_priority1_linkage")
    seg_graph = SEGraph()
    
    # Create and store timeline entry
    timeline_entry = create_test_timeline_entry_for_gate_evidence()
    atom_id = store_timeline_entry_for_seg(
        cmc_store=cmc_store,
        timeline_entry=timeline_entry,
    )
    
    # Ingest into SEG
    gate_evidence = ingest_timeline_entry(
        timeline_entry=timeline_entry,
        atom_id=atom_id,
        graph=seg_graph,
    )
    
    # Verify linkage
    evidence = seg_graph.get_evidence(gate_evidence["evidence_id"])
    assert evidence.atom_id == atom_id  # SEG evidence links to CMC atom
    
    # Verify atom exists in CMC (if we can query it)
    # Note: This would require CMC query functionality
    # For now, we verify the atom_id is stored in evidence


if __name__ == "__main__":
    # Run test and capture gate evidence
    if not CMC_AVAILABLE:
        print("❌ CMC service not available - cannot run end-to-end test")
        sys.exit(1)
    
    print("Priority 1 End-to-End Test")
    print("=" * 60)
    
    try:
        gate_evidence = _capture_priority1_end_to_end_gate_evidence()
        print("\n✅ Priority 1 Gate Evidence Captured:")
        print(f"   timeline_prompt_id: {gate_evidence['timeline_prompt_id']}")
        print(f"   atom_id: {gate_evidence['atom_id']}")
        print(f"   evidence_id: {gate_evidence['evidence_id']}")
        print("\n📋 Gate Evidence Tuple (for journal):")
        print(f"   {gate_evidence}")
        print("\n✅ End-to-end test PASSED!")
    except Exception as e:
        print(f"\n❌ End-to-end test FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

