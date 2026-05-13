"""
Tests for CMC TCS → SEG Integration Helper

Tests the helper function for storing timeline entries in CMC
and returning atom_id for SEG ingestion.
"""

import pytest
from datetime import datetime, timezone
from cmc_service.memory_store import MemoryStore
from cmc_service.tcs_seg_integration_helper import (
    store_timeline_entry_for_seg,
    create_test_timeline_entry_for_gate_evidence,
)


@pytest.fixture
def cmc_store(tmp_path):
    """Create a temporary CMC store for testing"""
    store = MemoryStore(base_path=str(tmp_path / "cmc"))
    return store


def test_store_timeline_entry_for_seg_basic(cmc_store):
    """Test basic timeline entry storage"""
    timeline_entry = {
        "prompt_id": "prompt_test_123",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": "Test timeline entry",
        "context_index": {
            "active_tasks": ["Test task"],
            "files_read": ["test.py"],
        },
        "confidence_metrics": {
            "average_confidence": 0.85,
        },
    }
    
    atom_id = store_timeline_entry_for_seg(cmc_store, timeline_entry)
    
    # Verify atom_id is returned
    assert atom_id is not None
    assert isinstance(atom_id, str)
    assert len(atom_id) > 0
    
    # Verify atom can be retrieved
    atom = cmc_store.get_atom(atom_id)
    assert atom is not None
    assert atom.modality == "tcs_timeline"
    assert atom.metadata["prompt_id"] == "prompt_test_123"


def test_store_timeline_entry_for_seg_with_snapshot(cmc_store):
    """Test timeline entry storage with context snapshot ID"""
    timeline_entry = {
        "prompt_id": "prompt_test_456",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": "Test timeline entry with snapshot",
        "context_index": {},
        "confidence_metrics": {"average_confidence": 0.90},
    }
    
    context_snapshot_id = "snapshot_test_123"
    atom_id = store_timeline_entry_for_seg(
        cmc_store, 
        timeline_entry,
        context_snapshot_id=context_snapshot_id
    )
    
    # Verify atom has snapshot ID in metadata
    atom = cmc_store.get_atom(atom_id)
    assert atom.metadata.get("context_snapshot_id") == context_snapshot_id
    assert atom.metadata["prompt_id"] == "prompt_test_456"


def test_create_test_timeline_entry_for_gate_evidence():
    """Test test timeline entry creation"""
    timeline_entry = create_test_timeline_entry_for_gate_evidence()
    
    # Verify structure
    assert "prompt_id" in timeline_entry
    assert "timestamp" in timeline_entry
    assert "summary" in timeline_entry
    assert "context_index" in timeline_entry
    assert "confidence_metrics" in timeline_entry
    
    # Verify prompt_id format
    assert timeline_entry["prompt_id"].startswith("prompt_gate_evidence_")
    
    # Verify context_index structure
    assert "active_tasks" in timeline_entry["context_index"]
    assert "files_read" in timeline_entry["context_index"]
    assert "insights_gained" in timeline_entry["context_index"]
    assert "decisions_made" in timeline_entry["context_index"]


def test_end_to_end_tcs_cmc_seg_workflow(cmc_store):
    """
    Test end-to-end TCS → CMC → SEG workflow.
    
    This test simulates the Priority 1 gate unlocking workflow:
    1. TCS creates timeline entry
    2. CMC stores entry (this test) → returns atom_id
    3. SEG ingests timeline entry (would be done by Nexus) → returns evidence_id
    4. Gate evidence tuple: (timeline_prompt_id, atom_id, evidence_id)
    """
    # Step 1: Create test timeline entry
    timeline_entry = create_test_timeline_entry_for_gate_evidence()
    prompt_id = timeline_entry["prompt_id"]
    
    # Step 2: Store in CMC (CMC side - Atlas)
    atom_id = store_timeline_entry_for_seg(cmc_store, timeline_entry)
    
    # Verify atom_id is valid
    assert atom_id is not None
    assert isinstance(atom_id, str)
    
    # Verify atom can be retrieved
    atom = cmc_store.get_atom(atom_id)
    assert atom is not None
    assert atom.metadata["prompt_id"] == prompt_id
    
    # Step 3: Prepare for SEG ingestion (would be done by Nexus)
    # The atom_id is now ready to be passed to SEG's ingest_timeline_entry()
    # This would be done in coordination with Nexus
    
    # Return gate evidence components (evidence_id would come from SEG)
    gate_evidence_components = {
        "timeline_prompt_id": prompt_id,
        "atom_id": atom_id,
        # "evidence_id": evidence_id,  # Would be provided by SEG ingestion
    }
    
    # Verify components
    assert "timeline_prompt_id" in gate_evidence_components
    assert "atom_id" in gate_evidence_components
    assert gate_evidence_components["timeline_prompt_id"] == prompt_id
    assert gate_evidence_components["atom_id"] == atom_id
    
    return gate_evidence_components

