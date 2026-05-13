"""
TCS (Timeline Context System) → SEG (Shared Evidence Graph) Integration

Transforms TCS timeline entries into SEG evidence nodes according to the
field-by-field mapping defined in CHRONOS_TCS_SEG_TIMELINE_MAPPING.md.

This integration enables:
- Timeline entries → SEG evidence nodes
- Complete provenance tracking (atom_id, witness_id)
- Bitemporal support (transaction time + valid time)
- Gate evidence capture (timeline_prompt_id, atom_id, evidence_id)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
import hashlib

from .models import Evidence
from .seg_graph import SEGraph


def timeline_entry_to_evidence(
    timeline_entry: Dict[str, Any],
    atom_id: str,
    witness_id: Optional[str] = None,
    graph: Optional[SEGraph] = None
) -> Tuple[Evidence, str]:
    """
    Transform a TCS timeline entry into a SEG evidence node.
    
    Args:
        timeline_entry: TCS timeline entry dictionary (from TimelineEntry or API response)
        atom_id: CMC atom ID (from TimelineMemoryStore.create_atom())
        witness_id: Optional VIF witness ID (if VIF observes timeline)
        graph: Optional SEG graph instance (if None, creates standalone evidence)
    
    Returns:
        Tuple of (Evidence node, evidence_id) for gate evidence capture
    
    Mapping (from CHRONOS_TCS_SEG_TIMELINE_MAPPING.md):
    - summary → content
    - prompt_id → metadata.timeline_prompt_id
    - timestamp → metadata.timeline_timestamp + vt_start
    - confidence_metrics.average_confidence → confidence
    - context_index.* → metadata.*
    - timeline_entry_id → source (tcs.timeline_entry:{id})
    - atom_id → atom_id
    - witness_id → witness_id
    """
    # Extract timeline entry fields
    prompt_id = timeline_entry.get("prompt_id", timeline_entry.get("id", ""))
    summary = timeline_entry.get("summary", "")
    timestamp = timeline_entry.get("timestamp")
    context_index = timeline_entry.get("context_index", {})
    confidence_metrics = timeline_entry.get("confidence_metrics", {})
    relevance_score = timeline_entry.get("relevance_score", 0.0)
    
    # Convert timestamp to datetime if string
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            timestamp = datetime.now(timezone.utc)
    elif timestamp is None:
        timestamp = datetime.now(timezone.utc)
    
    # Generate timeline_entry_id (hash of timestamp+prompt_id if not provided)
    timeline_entry_id = timeline_entry.get("timeline_entry_id")
    if not timeline_entry_id:
        hash_input = f"{timestamp.isoformat()}:{prompt_id}"
        timeline_entry_id = hashlib.sha256(hash_input.encode()).hexdigest()[:12]
    
    # Extract confidence (default to 0.8 if not available)
    confidence = confidence_metrics.get("average_confidence", 0.8)
    if confidence is None:
        confidence = 0.8
    
    # Build metadata dictionary
    metadata: Dict[str, Any] = {
        "timeline_prompt_id": prompt_id,
        "timeline_timestamp": timestamp.isoformat(),
        "relevance_score": relevance_score,
    }
    
    # Add context_index fields to metadata
    if context_index:
        if "active_tasks" in context_index:
            metadata["active_task"] = context_index.get("active_tasks", [])
        if "files_read" in context_index:
            metadata["files_read"] = context_index.get("files_read", [])
        if "insights_gained" in context_index:
            metadata["insights_gained"] = context_index.get("insights_gained", [])
        if "decisions_made" in context_index:
            metadata["decisions_made"] = context_index.get("decisions_made", [])
    
    # Add chain execution metadata
    if "executed_via_chain_id" in timeline_entry:
        metadata["chain_ids"] = {
            "executed_via_chain_id": timeline_entry.get("executed_via_chain_id"),
            "chain_execution_id": timeline_entry.get("chain_execution_id"),
            "chain_node_id": timeline_entry.get("chain_node_id"),
        }
    
    # Add confidence metrics
    if "high_confidence_areas" in confidence_metrics:
        metadata["high_confidence_spans"] = confidence_metrics.get("high_confidence_areas")
    
    # Add context evolution if present
    if "context_evolution" in timeline_entry:
        metadata["context_evolution"] = timeline_entry.get("context_evolution")
    
    # Create SEG Evidence node
    evidence = Evidence(
        content=summary,
        source=f"tcs.timeline_entry:{timeline_entry_id}",
        evidence_type="timeline_entry",
        confidence=float(confidence),
        reliability=0.95,  # Timeline entries are highly reliable
        atom_id=atom_id,
        witness_id=witness_id,
        tags=["timeline", "tcs", "evidence"],
        metadata=metadata,
        vt_start=timestamp,  # Valid time = when the event occurred
        tt_start=datetime.now(timezone.utc),  # Transaction time = when recorded
    )
    
    # Add to graph if provided
    if graph:
        evidence = graph.add_evidence(evidence)
    
    return (evidence, evidence.id)


def ingest_timeline_entry(
    timeline_entry: Dict[str, Any],
    atom_id: str,
    witness_id: Optional[str] = None,
    graph: Optional[SEGraph] = None
) -> Dict[str, str]:
    """
    Ingest a TCS timeline entry into SEG and return gate evidence tuple.
    
    This is the main entry point for Priority 1 gate unlocking.
    Returns the (timeline_prompt_id, atom_id, evidence_id) tuple required
    for gate_system_map_integrity and gate_dual_system.
    
    Args:
        timeline_entry: TCS timeline entry dictionary
        atom_id: CMC atom ID (from TimelineMemoryStore.create_atom())
        witness_id: Optional VIF witness ID
        graph: Optional SEG graph instance
    
    Returns:
        Dictionary with gate evidence tuple:
        {
            "timeline_prompt_id": "...",
            "atom_id": "...",
            "evidence_id": "..."
        }
    """
    evidence, evidence_id = timeline_entry_to_evidence(
        timeline_entry=timeline_entry,
        atom_id=atom_id,
        witness_id=witness_id,
        graph=graph
    )
    
    prompt_id = timeline_entry.get("prompt_id", timeline_entry.get("id", ""))
    
    return {
        "timeline_prompt_id": prompt_id,
        "atom_id": atom_id,
        "evidence_id": evidence_id,
    }

