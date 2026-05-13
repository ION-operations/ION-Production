"""
CMC (Context Memory Core) → SEG (Shared Evidence Graph) Integration

Enables bidirectional integration between CMC atoms and SEG evidence nodes.

This integration enables:
- Evidence → CMC atom storage (persistent storage)
- CMC atom → Evidence retrieval (graph reconstruction)
- Evidence ↔ CMC atom linking (bidirectional references)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Dict, Any

from .models import Evidence
from .seg_graph import SEGraph

try:
    from cmc_service.models import AtomCreate, AtomContent, Atom
    from cmc_service.memory_store import MemoryStore
    CMC_AVAILABLE = True
except ImportError:
    CMC_AVAILABLE = False
    # Type stubs for when CMC is not available
    AtomCreate = None  # type: ignore
    AtomContent = None  # type: ignore
    Atom = None  # type: ignore
    MemoryStore = None  # type: ignore


def store_evidence_in_cmc(
    evidence: Evidence,
    cmc_store: MemoryStore,
    correlation_id: Optional[str] = None
) -> str:
    """
    Store SEG evidence node in CMC as an atom.
    
    Args:
        evidence: SEG Evidence node to store
        cmc_store: CMC MemoryStore instance
        correlation_id: Optional correlation ID for tracking
    
    Returns:
        CMC atom ID
    
    Raises:
        ImportError: If CMC is not available
        ValueError: If evidence is invalid
    """
    if not CMC_AVAILABLE:
        raise ImportError("CMC service not available. Install cmc_service package.")
    
    if not evidence:
        raise ValueError("Evidence cannot be None")
    
    # Create atom content from evidence
    atom_content = AtomContent(
        inline=evidence.content,
        media_type="text/plain"
    )
    
    # Create atom with evidence metadata
    atom_create = AtomCreate(
        modality="seg_evidence",
        content=atom_content,
        tags={
            "evidence_id": evidence.id,
            "evidence_type": evidence.evidence_type,
            "confidence": str(evidence.confidence),
            "reliability": str(evidence.reliability),
        },
        metadata={
            "seg_evidence_id": evidence.id,
            "source": evidence.source,
            "evidence_type": evidence.evidence_type,
            "confidence": evidence.confidence,
            "reliability": evidence.reliability,
            "tags": evidence.tags,
            "metadata": evidence.metadata,
            "vt_start": evidence.vt_start.isoformat() if evidence.vt_start else None,
            "vt_end": evidence.vt_end.isoformat() if evidence.vt_end else None,
        }
    )
    
    # Store in CMC
    if cmc_store is None:
        raise ImportError("CMC service not available. Install cmc_service package.")
    
    atom = cmc_store.create_atom(atom_create, correlation_id=correlation_id)
    
    return atom.id


def retrieve_evidence_from_cmc(
    atom_id: str,
    cmc_store: MemoryStore,
    graph: Optional[SEGraph] = None
) -> Evidence:
    """
    Retrieve SEG evidence node from CMC atom.
    
    Args:
        atom_id: CMC atom ID
        cmc_store: CMC MemoryStore instance
        graph: Optional SEG graph instance (if None, creates standalone evidence)
    
    Returns:
        SEG Evidence node reconstructed from CMC atom
    
    Raises:
        ImportError: If CMC is not available
        ValueError: If atom not found or invalid
    """
    if not CMC_AVAILABLE:
        raise ImportError("CMC service not available. Install cmc_service package.")
    
    # Retrieve atom from CMC
    if cmc_store is None:
        raise ImportError("CMC service not available. Install cmc_service package.")
    
    atom = cmc_store.get_atom(atom_id)
    if not atom:
        raise ValueError(f"Atom {atom_id} not found in CMC")
    
    # Extract evidence data from atom
    content = atom.content.inline if isinstance(atom.content.inline, str) else str(atom.content.inline)
    metadata = atom.metadata or {}
    
    # Reconstruct evidence
    evidence = Evidence(
        id=metadata.get("seg_evidence_id", f"evidence_{atom_id}"),
        content=content,
        source=metadata.get("source", f"cmc.atom:{atom_id}"),
        evidence_type=metadata.get("evidence_type", "text"),
        confidence=float(metadata.get("confidence", 1.0)),
        reliability=float(metadata.get("reliability", 1.0)),
        atom_id=atom_id,  # Link back to CMC
        tags=metadata.get("tags", []),
        metadata=metadata.get("metadata", {}),
        vt_start=datetime.fromisoformat(metadata["vt_start"]) if metadata.get("vt_start") else datetime.now(timezone.utc),
        vt_end=datetime.fromisoformat(metadata["vt_end"]) if metadata.get("vt_end") else None,
        tt_start=atom.created_at if hasattr(atom, "created_at") else datetime.now(timezone.utc),
    )
    
    # Add to graph if provided
    if graph:
        evidence = graph.add_evidence(evidence)
    
    return evidence


def link_evidence_to_cmc(
    evidence_id: str,
    atom_id: str,
    graph: SEGraph
) -> None:
    """
    Link existing SEG evidence node to CMC atom.
    
    Args:
        evidence_id: SEG evidence ID
        atom_id: CMC atom ID
        graph: SEG graph instance
    
    Raises:
        ValueError: If evidence not found
    """
    # Get evidence from graph
    evidence = graph.get_evidence(evidence_id)
    if not evidence:
        raise ValueError(f"Evidence {evidence_id} not found in graph")
    
    # Update evidence with atom_id
    evidence.atom_id = atom_id
    
    # Update in graph (if graph supports updates)
    # Update evidence by getting it, modifying, and re-adding
    existing_evidence = graph.get_evidence(evidence_id)
    if existing_evidence:
        # Update the atom_id field
        existing_evidence.atom_id = atom_id
        # Re-add to update the graph
        graph.add_evidence(existing_evidence)
    else:
        # If evidence doesn't exist, just add it
        evidence.atom_id = atom_id
        graph.add_evidence(evidence)

