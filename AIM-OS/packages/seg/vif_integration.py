"""
VIF (Verifiable Intelligence Framework) → SEG (Shared Evidence Graph) Integration

Enables bidirectional integration between VIF witnesses and SEG entities/relations/evidence.

This integration enables:
- Entity/Relation/Evidence → VIF witness creation (provenance tracking)
- VIF witness → Entity/Relation/Evidence attachment (provenance linking)
- Witness provenance retrieval (trace entity lineage)
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any

from .models import Entity, Relation, Evidence
from .seg_graph import SEGraph

try:
    from vif.witness import VIF
    from vif.cmc_integration import VIFStore
    from cmc_service.memory_store import MemoryStore
    VIF_AVAILABLE = True
except ImportError:
    VIF_AVAILABLE = False
    # Type stubs for when VIF is not available
    VIF = None  # type: ignore
    VIFStore = None  # type: ignore
    MemoryStore = None  # type: ignore


def create_vif_witness(
    entity: Entity,
    cmc_store: MemoryStore,
    model_id: str = "seg",
    model_provider: str = "seg",
    context_snapshot_id: Optional[str] = None,
    correlation_id: Optional[str] = None
) -> str:
    """
    Create VIF witness for SEG entity and store in CMC.
    
    Args:
        entity: SEG Entity to create witness for
        cmc_store: CMC MemoryStore instance (for VIF storage)
        model_id: Model identifier (default: "seg")
        model_provider: Model provider (default: "seg")
        context_snapshot_id: Optional CMC snapshot ID
        correlation_id: Optional correlation ID for tracking
    
    Returns:
        VIF witness ID
    
    Raises:
        ImportError: If VIF is not available
        ValueError: If entity is invalid
    """
    # Treat missing VIF or missing backing store as unavailable in this context
    if not VIF_AVAILABLE or cmc_store is None:
        raise ImportError("VIF service not available. Install vif package or provide cmc_store.")
    
    if not entity:
        raise ValueError("Entity cannot be None")
    
    # Create VIF witness
    vif = VIF(
        model_id=model_id,
        model_provider=model_provider,
        context_snapshot_id=context_snapshot_id or "",
        prompt_hash=VIF.hash_text(f"{entity.type}:{entity.name}"),
        prompt_tokens=len(f"{entity.type}:{entity.name}".split()),
        confidence_score=entity.confidence,
        output_hash=VIF.hash_text(str(entity.attributes)),
        output_tokens=len(str(entity.attributes).split()),
        total_tokens=len(f"{entity.type}:{entity.name}".split()) + len(str(entity.attributes).split()),
        operation_name="seg_entity_create",
        inputs={"entity_type": entity.type, "entity_name": entity.name},
        outputs={"entity_id": entity.id},
    )
    
    # Store in CMC via VIFStore
    vif_store = VIFStore(cmc_store)
    atom_id = vif_store.store_witness(vif, correlation_id=correlation_id)
    
    return vif.id


def attach_witness_to_entity(
    entity_id: str,
    witness_id: str,
    graph: SEGraph
) -> None:
    """
    Attach VIF witness to existing SEG entity.
    
    Args:
        entity_id: SEG entity ID
        witness_id: VIF witness ID
        graph: SEG graph instance
    
    Raises:
        ValueError: If entity not found
    """
    # Get entity from graph
    entity = graph.get_entity(entity_id)
    if not entity:
        raise ValueError(f"Entity {entity_id} not found in graph")
    
    # Update entity with witness_id
    entity.witness_id = witness_id

    # Persist update to graph store if supported
    if hasattr(graph, "update_entity"):
        # SEGraph.update_entity expects (entity_id, updates_dict)
        graph.update_entity(entity_id, {"witness_id": witness_id})
    else:
        # Fallback: store mutated entity back via add/replace pattern if available
        # For current SEGraph, mutating the in-memory object is sufficient
        pass


def attach_witness_to_relation(
    relation_id: str,
    witness_id: str,
    graph: SEGraph
) -> None:
    """
    Attach VIF witness to existing SEG relation.
    
    Args:
        relation_id: SEG relation ID
        witness_id: VIF witness ID
        graph: SEG graph instance
    
    Raises:
        ValueError: If relation not found
    """
    # Get relation from graph
    relation = graph.get_relation(relation_id)
    if not relation:
        raise ValueError(f"Relation {relation_id} not found in graph")
    
    # Update relation with witness_id
    relation.witness_id = witness_id
    # For current SEGraph, mutating the in-memory relation object is sufficient


def attach_witness_to_evidence(
    evidence_id: str,
    witness_id: str,
    graph: SEGraph
) -> None:
    """
    Attach VIF witness to existing SEG evidence.
    
    Args:
        evidence_id: SEG evidence ID
        witness_id: VIF witness ID
        graph: SEG graph instance
    
    Raises:
        ValueError: If evidence not found
    """
    # Get evidence from graph
    evidence = graph.get_evidence(evidence_id)
    if not evidence:
        raise ValueError(f"Evidence {evidence_id} not found in graph")
    
    # Update evidence with witness_id
    evidence.witness_id = witness_id
    
    # Update evidence by getting it, modifying, and re-adding
    existing_evidence = graph.get_evidence(evidence_id)
    if existing_evidence:
        # Update witness_id field
        existing_evidence.witness_id = witness_id
        # Re-add to update the graph
        graph.add_evidence(existing_evidence)
    else:
        raise ValueError(f"Evidence {evidence_id} not found in graph")


def get_witness_provenance(
    entity_id: str,
    cmc_store: MemoryStore,
    graph: Optional[SEGraph] = None
) -> List[Dict[str, Any]]:
    """
    Get VIF witness provenance for SEG entity.
    
    Args:
        entity_id: SEG entity ID
        cmc_store: CMC MemoryStore instance (for VIF retrieval)
        graph: Optional SEG graph instance (to get entity)
    
    Returns:
        List of witness provenance dictionaries
    
    Raises:
        ImportError: If VIF is not available
        ValueError: If entity not found
    """
    # Require VIF library and a valid backing store for retrieval
    if not VIF_AVAILABLE or cmc_store is None:
        raise ImportError("VIF service not available. Install vif package or provide cmc_store.")
    
    # Get entity from graph if provided
    entity = None
    if graph:
        entity = graph.get_entity(entity_id)
        if not entity:
            raise ValueError(f"Entity {entity_id} not found in graph")
    
    # If entity has witness_id, retrieve witness
    provenance = []
    if entity and entity.witness_id:
        vif_store = VIFStore(cmc_store)
        witness = vif_store.get_witness(entity.witness_id)
        if witness:
            provenance.append({
                "witness_id": witness.id,
                "model_id": witness.model_id,
                "confidence_score": witness.confidence_score,
                "confidence_band": witness.confidence_band.value if hasattr(witness.confidence_band, "value") else str(witness.confidence_band),
                "operation_name": witness.operation_name if hasattr(witness, "operation_name") else None,
                "inputs": witness.inputs if hasattr(witness, "inputs") else {},
                "outputs": witness.outputs if hasattr(witness, "outputs") else {},
            })
    
    return provenance

