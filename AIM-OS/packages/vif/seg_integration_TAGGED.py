"""VIF Integration with SEG (Shared Evidence Graph)

Verifies VIF witness links in SEG entities, relations, and evidence.
Provides provenance chain tracking and evidence weighting verification.
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone

# SEG imports (optional - gracefully handle if SEG not available)
try:
    from seg import Entity, Relation, Evidence, SEGraph
    SEG_AVAILABLE = True
except ImportError:
    try:
        # Fallback to packages.seg if direct import fails
        from packages.seg.models import Entity, Relation, Evidence
        from packages.seg.seg_graph import SEGraph
        SEG_AVAILABLE = True
    except ImportError:
        SEG_AVAILABLE = False
        Entity = None
        Relation = None
        Evidence = None
        SEGraph = None

# VIF imports
try:
    from packages.vif.witness import VIF
    from packages.vif.cmc_integration import VIFStore
    from packages.cmc import get_memory_store
    VIF_AVAILABLE = True
except ImportError:
    VIF_AVAILABLE = False
    VIF = None
    VIFStore = None
    get_memory_store = None


@dataclass
class WitnessLinkVerification:
    """Result of verifying a witness_id link"""
    witness_id: str
    exists: bool
    witness_type: Optional[str] = None  # "vif" | "cmc_atom" | "unknown"
    confidence: Optional[float] = None
    task_criticality: Optional[str] = None
    kappa_gate_passed: Optional[bool] = None
    error: Optional[str] = None


@dataclass
class ProvenanceChainVerification:
    """Result of verifying a provenance chain"""
    entity_id: str
    chain_complete: bool
    witness_links_verified: int
    witness_links_total: int
    missing_witnesses: List[str]
    broken_links: List[Tuple[str, str]]  # (entity_id, witness_id) pairs
    confidence_scores: List[float]
    chain_confidence: float  # Weighted average confidence
    error: Optional[str] = None


@dataclass
class EvidenceWeightingResult:
    """Result of evidence weighting calculation"""
    evidence_id: str
    base_confidence: float
    vif_confidence: Optional[float]
    weighted_confidence: float
    weighting_method: str  # "vif_override" | "vif_boost" | "base_only"
    witness_id: Optional[str] = None
    error: Optional[str] = None


# NL_TAG: VIF-SEG-001 | Verify witness_id link exists in VIF/CMC. | verify_witness_link(witness_id) | []
# NL_TAG_CONNECT: VIF-SEG-001 | Witness link verified via VIFStore | verify_witness_link → VIFStore.get_witness | [VIF-SEG-001, CMC-STORE-001]
# NL_TAG_INTENT: VIF-INTENT-007 | Design decision: witness verification | verify_witness_link | [ADR-VIF-SEG]
def verify_witness_link(witness_id: str) -> WitnessLinkVerification:
    """
    Verify that a witness_id link exists in VIF/CMC.
    
    Args:
        witness_id: VIF witness ID to verify
        
    Returns:
        WitnessLinkVerification with verification results
        
    Examples:
        >>> result = verify_witness_link("vif_abc123")
        >>> assert result.exists == True
        >>> assert result.witness_type == "vif"
    """
    if not VIF_AVAILABLE:
        return WitnessLinkVerification(
            witness_id=witness_id,
            exists=False,
            error="VIF not available"
        )
    
    try:
        # Try to retrieve witness from CMC via VIFStore
        cmc_store = get_memory_store()
        vif_store = VIFStore(cmc_store)
        
        witness = vif_store.get_witness(witness_id)
        
        if witness:
            return WitnessLinkVerification(
                witness_id=witness_id,
                exists=True,
                witness_type="vif",
                confidence=witness.confidence_score,
                task_criticality=witness.task_criticality.value if witness.task_criticality else None,
                kappa_gate_passed=witness.kappa_gate_passed,
            )
        else:
            return WitnessLinkVerification(
                witness_id=witness_id,
                exists=False,
                error="Witness not found in CMC"
            )
    except Exception as e:
        return WitnessLinkVerification(
            witness_id=witness_id,
            exists=False,
            error=f"Error retrieving witness: {str(e)}"
        )


# NL_TAG: VIF-SEG-002 | Verify provenance chain with witness links. | verify_provenance_chain(graph, entity_id, max_depth) | []
# NL_TAG_CONNECT: VIF-SEG-002 | Provenance chain verified via SEG trace_provenance | verify_provenance_chain → SEGraph.trace_provenance | [VIF-SEG-002, SEG-PROV-001]
# NL_TAG_INTENT: VIF-INTENT-008 | Design decision: provenance verification | verify_provenance_chain | [ADR-VIF-SEG]
def verify_provenance_chain(
    graph: SEGraph,
    entity_id: str,
    max_depth: int = 5,
) -> ProvenanceChainVerification:
    """
    Verify provenance chain for an entity, checking all witness_id links.
    
    Args:
        graph: SEG graph instance
        entity_id: Entity ID to trace provenance for
        max_depth: Maximum depth to traverse
        
    Returns:
        ProvenanceChainVerification with verification results
        
    Examples:
        >>> graph = SEGraph()
        >>> entity = Entity(type="concept", name="ML", witness_id="vif_123")
        >>> graph.add_entity(entity)
        >>> result = verify_provenance_chain(graph, entity.id)
        >>> assert result.chain_complete == True
    """
    if not SEG_AVAILABLE:
        return ProvenanceChainVerification(
            entity_id=entity_id,
            chain_complete=False,
            witness_links_verified=0,
            witness_links_total=0,
            missing_witnesses=[],
            broken_links=[],
            confidence_scores=[],
            chain_confidence=0.0,
            error="SEG not available"
        )
    
    try:
        # Trace provenance chain
        provenance = graph.trace_provenance(entity_id, max_depth=max_depth)
        
        # Collect all witness IDs from provenance chain
        witness_ids = []
        missing_witnesses = []
        broken_links = []
        confidence_scores = []
        
        # Get starting entity
        entity = graph.get_entity(entity_id)
        if entity and entity.witness_id:
            witness_ids.append((entity_id, entity.witness_id))
        
        # Collect witness IDs from provenance chain
        for source_entity, relation in provenance:
            if source_entity.witness_id:
                witness_ids.append((source_entity.id, source_entity.witness_id))
            if relation.witness_id:
                witness_ids.append((relation.id, relation.witness_id))
        
        # Verify each witness link
        verified_count = 0
        for node_id, witness_id in witness_ids:
            verification = verify_witness_link(witness_id)
            if verification.exists:
                verified_count += 1
                if verification.confidence is not None:
                    confidence_scores.append(verification.confidence)
            else:
                missing_witnesses.append(witness_id)
                broken_links.append((node_id, witness_id))
        
        # Calculate chain confidence (weighted average)
        chain_confidence = 0.0
        if confidence_scores:
            chain_confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Chain is complete if all witness links are verified
        chain_complete = len(missing_witnesses) == 0
        
        return ProvenanceChainVerification(
            entity_id=entity_id,
            chain_complete=chain_complete,
            witness_links_verified=verified_count,
            witness_links_total=len(witness_ids),
            missing_witnesses=missing_witnesses,
            broken_links=broken_links,
            confidence_scores=confidence_scores,
            chain_confidence=chain_confidence,
        )
    except Exception as e:
        return ProvenanceChainVerification(
            entity_id=entity_id,
            chain_complete=False,
            witness_links_verified=0,
            witness_links_total=0,
            missing_witnesses=[],
            broken_links=[],
            confidence_scores=[],
            chain_confidence=0.0,
            error=f"Error verifying provenance chain: {str(e)}"
        )


# NL_TAG: VIF-SEG-003 | Calculate evidence weighting using VIF confidence. | calculate_evidence_weighting(evidence, witness_id) | []
# NL_TAG_CONNECT: VIF-SEG-003 | Evidence weighting uses VIF confidence | calculate_evidence_weighting → verify_witness_link | [VIF-SEG-003, VIF-SEG-001]
# NL_TAG_INTENT: VIF-INTENT-009 | Design decision: evidence weighting | calculate_evidence_weighting | [ADR-VIF-SEG]
def calculate_evidence_weighting(
    evidence: Evidence,
    witness_id: Optional[str] = None,
) -> EvidenceWeightingResult:
    """
    Calculate evidence weighting using VIF confidence.
    
    Evidence weighting rules:
    - If VIF witness exists and confidence > base_confidence: Use VIF confidence (vif_override)
    - If VIF witness exists and confidence <= base_confidence: Boost base by 10% (vif_boost)
    - If no VIF witness: Use base confidence only (base_only)
    
    Args:
        evidence: SEG Evidence instance
        witness_id: Optional witness ID (if not provided, uses evidence.witness_id)
        
    Returns:
        EvidenceWeightingResult with weighting calculation
        
    Examples:
        >>> evidence = Evidence(content="Fact", source="url", confidence=0.80)
        >>> result = calculate_evidence_weighting(evidence, "vif_123")
        >>> assert result.weighted_confidence >= 0.80
    """
    if not SEG_AVAILABLE:
        return EvidenceWeightingResult(
            evidence_id=evidence.id,
            base_confidence=evidence.confidence,
            vif_confidence=None,
            weighted_confidence=evidence.confidence,
            weighting_method="base_only",
            error="SEG not available"
        )
    
    # Use provided witness_id or evidence.witness_id
    actual_witness_id = witness_id or evidence.witness_id
    
    if not actual_witness_id or not VIF_AVAILABLE:
        # No witness ID - use base confidence only
        return EvidenceWeightingResult(
            evidence_id=evidence.id,
            base_confidence=evidence.confidence,
            vif_confidence=None,
            weighted_confidence=evidence.confidence,
            weighting_method="base_only",
        )
    
    # Verify witness link and get VIF confidence
    verification = verify_witness_link(actual_witness_id)
    
    if not verification.exists or verification.confidence is None:
        # Witness not found - use base confidence only
        return EvidenceWeightingResult(
            evidence_id=evidence.id,
            base_confidence=evidence.confidence,
            vif_confidence=None,
            weighted_confidence=evidence.confidence,
            weighting_method="base_only",
            witness_id=actual_witness_id,
        )
    
    vif_confidence = verification.confidence
    base_confidence = evidence.confidence
    
    # Apply weighting rules
    if vif_confidence > base_confidence:
        # VIF confidence is higher - use it (override)
        weighted_confidence = vif_confidence
        method = "vif_override"
    else:
        # VIF confidence is lower or equal - boost base by 10%
        weighted_confidence = min(1.0, base_confidence * 1.10)
        method = "vif_boost"
    
    return EvidenceWeightingResult(
        evidence_id=evidence.id,
        base_confidence=base_confidence,
        vif_confidence=vif_confidence,
        weighted_confidence=weighted_confidence,
        weighting_method=method,
        witness_id=actual_witness_id,
    )


# NL_TAG: VIF-SEG-004 | Verify all witness_id links in SEG graph. | verify_all_witness_links(graph) | []
# NL_TAG_CONNECT: VIF-SEG-004 | All witness links verified via verify_witness_link | verify_all_witness_links → verify_witness_link | [VIF-SEG-004, VIF-SEG-001]
# NL_TAG_INTENT: VIF-INTENT-010 | Design decision: comprehensive verification | verify_all_witness_links | [ADR-VIF-SEG]
def verify_all_witness_links(graph: SEGraph) -> Dict[str, Any]:
    """
    Verify all witness_id links in a SEG graph.
    
    Checks entities, relations, and evidence for valid witness_id links.
    
    Args:
        graph: SEG graph instance
        
    Returns:
        Dictionary with verification statistics
        
    Examples:
        >>> graph = SEGraph()
        >>> entity = Entity(type="concept", name="ML", witness_id="vif_123")
        >>> graph.add_entity(entity)
        >>> results = verify_all_witness_links(graph)
        >>> assert results["entities_verified"] == 1
    """
    if not SEG_AVAILABLE:
        return {
            "error": "SEG not available",
            "entities_verified": 0,
            "relations_verified": 0,
            "evidence_verified": 0,
            "total_verified": 0,
            "total_checked": 0,
            "missing_witnesses": [],
        }
    
    entities_verified = 0
    relations_verified = 0
    evidence_verified = 0
    missing_witnesses = []
    
    # Verify entity witness links
    for entity in graph.entities.values():
        if entity.witness_id:
            verification = verify_witness_link(entity.witness_id)
            if verification.exists:
                entities_verified += 1
            else:
                missing_witnesses.append(entity.witness_id)
    
    # Verify relation witness links
    for relation in graph.relations.values():
        if relation.witness_id:
            verification = verify_witness_link(relation.witness_id)
            if verification.exists:
                relations_verified += 1
            else:
                missing_witnesses.append(relation.witness_id)
    
    # Verify evidence witness links
    for evidence in graph.evidence.values():
        if evidence.witness_id:
            verification = verify_witness_link(evidence.witness_id)
            if verification.exists:
                evidence_verified += 1
            else:
                missing_witnesses.append(evidence.witness_id)
    
    total_verified = entities_verified + relations_verified + evidence_verified
    total_checked = (
        sum(1 for e in graph.entities.values() if e.witness_id) +
        sum(1 for r in graph.relations.values() if r.witness_id) +
        sum(1 for ev in graph.evidence.values() if ev.witness_id)
    )
    
    return {
        "entities_verified": entities_verified,
        "relations_verified": relations_verified,
        "evidence_verified": evidence_verified,
        "total_verified": total_verified,
        "total_checked": total_checked,
        "missing_witnesses": missing_witnesses,
        "verification_rate": total_verified / total_checked if total_checked > 0 else 0.0,
    }


# NL_TAG: VIF-SEG-005 | Get evidence weighting statistics for SEG graph. | get_evidence_weighting_stats(graph) | []
# NL_TAG_CONNECT: VIF-SEG-005 | Evidence weighting stats use calculate_evidence_weighting | get_evidence_weighting_stats → calculate_evidence_weighting | [VIF-SEG-005, VIF-SEG-003]
# NL_TAG_INTENT: VIF-INTENT-011 | Design decision: evidence weighting analytics | get_evidence_weighting_stats | [ADR-VIF-SEG]
def get_evidence_weighting_stats(graph: SEGraph) -> Dict[str, Any]:
    """
    Get evidence weighting statistics for a SEG graph.
    
    Calculates weighted confidence for all evidence and provides statistics.
    
    Args:
        graph: SEG graph instance
        
    Returns:
        Dictionary with weighting statistics
        
    Examples:
        >>> graph = SEGraph()
        >>> evidence = Evidence(content="Fact", source="url", confidence=0.80, witness_id="vif_123")
        >>> graph.add_evidence(evidence)
        >>> stats = get_evidence_weighting_stats(graph)
        >>> assert stats["total_evidence"] == 1
    """
    if not SEG_AVAILABLE:
        return {
            "error": "SEG not available",
            "total_evidence": 0,
            "evidence_with_witnesses": 0,
            "average_base_confidence": 0.0,
            "average_weighted_confidence": 0.0,
            "weighting_methods": {},
        }
    
    total_evidence = len(graph.evidence)
    evidence_with_witnesses = 0
    base_confidences = []
    weighted_confidences = []
    weighting_methods = {"vif_override": 0, "vif_boost": 0, "base_only": 0}
    
    for evidence in graph.evidence.values():
        if evidence.witness_id:
            evidence_with_witnesses += 1
        
        weighting = calculate_evidence_weighting(evidence)
        base_confidences.append(weighting.base_confidence)
        weighted_confidences.append(weighting.weighted_confidence)
        weighting_methods[weighting.weighting_method] += 1
    
    return {
        "total_evidence": total_evidence,
        "evidence_with_witnesses": evidence_with_witnesses,
        "evidence_without_witnesses": total_evidence - evidence_with_witnesses,
        "average_base_confidence": sum(base_confidences) / len(base_confidences) if base_confidences else 0.0,
        "average_weighted_confidence": sum(weighted_confidences) / len(weighted_confidences) if weighted_confidences else 0.0,
        "weighting_methods": weighting_methods,
        "confidence_improvement": (
            sum(weighted_confidences) / len(weighted_confidences) - sum(base_confidences) / len(base_confidences)
            if base_confidences and weighted_confidences else 0.0
        ),
    }

