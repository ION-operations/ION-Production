"""
CMC Helper for TCS → SEG Integration

Provides helper functions for storing timeline entries in CMC
and returning atom_id for SEG ingestion.

This supports the Priority 1 gate unlocking workflow:
1. TCS creates timeline entry
2. CMC stores entry (this helper) → returns atom_id
3. SEG ingests timeline entry → returns evidence_id
4. Capture gate evidence tuple: (timeline_prompt_id, atom_id, evidence_id)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Any, Optional
import json

from .models import AtomCreate, AtomContent
from .memory_store import MemoryStore


def store_timeline_entry_for_seg(
    cmc_store: MemoryStore,
    timeline_entry: Dict[str, Any],
    context_snapshot_id: Optional[str] = None,
) -> str:
    """
    Store a TCS timeline entry in CMC and return atom_id for SEG ingestion.
    
    This function is designed for the Priority 1 gate unlocking workflow.
    It stores the timeline entry in CMC using the recommended schema from
    ATLAS_CMC_TCS_INTEGRATION.md and returns the atom_id for SEG ingestion.
    
    Args:
        cmc_store: CMC MemoryStore instance
        timeline_entry: TCS timeline entry dictionary (from TimelineEntry or API response)
        context_snapshot_id: Optional CMC snapshot ID for context (stored in metadata)
    
    Returns:
        atom_id: CMC atom ID for linking to SEG evidence node
    
    Example:
        >>> from cmc_service import MemoryStore
        >>> from cmc_service.tcs_seg_integration_helper import store_timeline_entry_for_seg
        >>> 
        >>> cmc_store = MemoryStore("./data")
        >>> timeline_entry = {
        ...     "prompt_id": "prompt_123",
        ...     "timestamp": "2025-01-27T18:05:32.114Z",
        ...     "summary": "Test timeline entry",
        ...     "context_index": {...},
        ...     "confidence_metrics": {"average_confidence": 0.85},
        ... }
        >>> 
        >>> atom_id = store_timeline_entry_for_seg(cmc_store, timeline_entry)
        >>> print(f"Stored in CMC as atom: {atom_id}")
    """
    # Extract timeline entry fields
    prompt_id = timeline_entry.get("prompt_id", timeline_entry.get("id", ""))
    summary = timeline_entry.get("summary", "")
    timestamp = timeline_entry.get("timestamp")
    context_index = timeline_entry.get("context_index", {})
    confidence_metrics = timeline_entry.get("confidence_metrics", {})
    
    # Convert timestamp to datetime if string
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            timestamp = datetime.now(timezone.utc)
    elif timestamp is None:
        timestamp = datetime.now(timezone.utc)
    
    # Build content (full timeline entry as JSON)
    content_dict = {
        "type": "tcs_timeline_entry",
        "prompt_id": prompt_id,
        "timestamp": timestamp.isoformat(),
        "summary": summary,
        "context_index": context_index,
        "confidence_metrics": confidence_metrics,
    }
    
    # Add any additional timeline entry fields
    for key in ["relevance_score", "executed_via_chain_id", "chain_execution_id", 
                "chain_node_id", "parent_chain_ids", "child_chain_ids", "evolution_path"]:
        if key in timeline_entry:
            content_dict[key] = timeline_entry[key]
    
    # Store context_snapshot_id in metadata if provided (for witness tracking)
    metadata = {
        "entry_id": timeline_entry.get("timeline_entry_id", prompt_id),
        "prompt_id": prompt_id,
        "timestamp": timestamp.isoformat(),
        "event_type": timeline_entry.get("event_type", "timeline_entry"),
        "title": summary[:100] if summary else "Timeline Entry",
        "description": summary,
        "context_data": context_index,
        "quality_metrics": {
            "confidence": confidence_metrics.get("average_confidence", 0.8),
            "relevance": timeline_entry.get("relevance_score", 0.0),
        },
        "valid_from": timestamp.isoformat(),
        "valid_to": None,  # Open-ended
    }
    
    # Add context_snapshot_id to metadata if provided
    if context_snapshot_id is not None:
        metadata["context_snapshot_id"] = context_snapshot_id
    
    # Create atom payload (following ATLAS_CMC_TCS_INTEGRATION.md schema)
    atom_payload = AtomCreate(
        modality="tcs_timeline",  # Recommended modality from integration guide
        content=AtomContent(
            inline=json.dumps(content_dict),
            media_type="application/json"
        ),
        tags={
            "timeline_context": 1.0,
            "prompt_tracking": 0.9,
            "tcs_entry": 1.0,
            "event_type": 0.7,  # Default weight
        },
        metadata=metadata,
    )
    
    # Store in CMC (witness stub is created automatically by MemoryStore)
    # Use prompt_id as correlation_id for traceability
    atom = cmc_store.create_atom(atom_payload, correlation_id=prompt_id)
    return atom.id


def create_test_timeline_entry_for_gate_evidence() -> Dict[str, Any]:
    """
    Create a test timeline entry for Priority 1 gate evidence capture.
    
    This creates a realistic timeline entry that can be used for testing
    the TCS → CMC → SEG integration workflow.
    
    Returns:
        timeline_entry: Dictionary representing a TCS timeline entry
    """
    return {
        "prompt_id": f"prompt_gate_evidence_{datetime.now(timezone.utc).timestamp()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": "Priority 1 gate evidence test - TCS → CMC → SEG integration workflow",
        "context_index": {
            "active_tasks": ["Priority 1 coordination", "Gate evidence capture"],
            "files_read": [
                "packages/seg/tcs_integration.py",
                "packages/timeline_context_system/prompt_context_tracker.py",
                "packages/cmc_service/models.py",
            ],
            "insights_gained": [
                "TCS timeline entries transform cleanly into SEG evidence nodes",
                "CMC atom_id provides the link between TCS and SEG",
                "Gate evidence tuple captures complete provenance chain",
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
            "high_confidence_areas": ["integration", "mapping", "gate_evidence"],
        },
        "relevance_score": 0.92,
    }

