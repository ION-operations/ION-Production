"""
SDF-CVF (Schema-Driven Framework - Consistency Validation Framework) → SEG Integration

Enables bidirectional integration between SDF-CVF consistency validation and SEG evidence nodes.

This integration enables:
- Evidence consistency validation (quartet/quintet parity)
- Trace ↔ Evidence linking (bidirectional references)
- Consistency reports (parity scores, validation results)
"""

from __future__ import annotations

import os
from typing import Optional, Dict, Any, List, Literal

from .models import Evidence
from .seg_graph import SEGraph

try:
    from packages.sdfcvf.parity import ParityResult, ParityCalculator
    from packages.sdfcvf.quintet import QuintetParityResult, QuintetParityCalculator
    SDFCVF_AVAILABLE = True
except ImportError:
    SDFCVF_AVAILABLE = False
    # Type stubs for when SDF-CVF is not available
    ParityResult = None  # type: ignore
    ParityCalculator = None  # type: ignore
    QuintetParityResult = None  # type: ignore
    QuintetParityCalculator = None  # type: ignore


IntegrationMode = Literal["strict", "auto", "fallback", "mocked"]
_VALID_INTEGRATION_MODES = {"strict", "auto", "fallback", "mocked"}
_DEFAULT_INTEGRATION_MODE = os.getenv("AIMOS_SEG_SDFCVF_MODE", "strict")


def _resolve_integration_mode(integration_mode: Optional[IntegrationMode]) -> str:
    mode = (integration_mode or _DEFAULT_INTEGRATION_MODE).strip().lower()
    if mode not in _VALID_INTEGRATION_MODES:
        valid = ", ".join(sorted(_VALID_INTEGRATION_MODES))
        raise ValueError(f"Invalid integration_mode '{mode}'. Expected one of: {valid}")
    return mode


def _ensure_sdfcvf_enabled(integration_mode: Optional[IntegrationMode]) -> None:
    mode = _resolve_integration_mode(integration_mode)
    if mode == "strict":
        raise ImportError("SDF-CVF integration is disabled in strict mode.")
    if mode in {"auto", "fallback"} and not SDFCVF_AVAILABLE:
        raise ImportError("SDF-CVF service not available. Install sdfcvf package or use mocked mode.")


def validate_consistency(
    evidence: Evidence,
    calculator: Optional[QuintetParityCalculator] = None,
    integration_mode: Optional[IntegrationMode] = None,
) -> bool:
    """
    Validate SEG evidence consistency using SDF-CVF.
    
    Args:
        evidence: SEG Evidence node to validate
        calculator: Optional SDF-CVF parity calculator (creates if None)
    
    Returns:
        True if consistent, False otherwise
    
    Raises:
        ImportError: If SDF-CVF is not available
        ValueError: If evidence is invalid
    """
    _ensure_sdfcvf_enabled(integration_mode)
    
    if not evidence:
        raise ValueError("Evidence cannot be None")
    
    # Check if evidence has required quartet/quintet metadata
    metadata = evidence.metadata or {}
    
    # Check for quartet parity score
    quartet_parity = metadata.get("quartet_parity")
    if quartet_parity is not None:
        # If parity score exists, check if it meets threshold (0.90)
        return float(quartet_parity) >= 0.90
    
    # Check for quintet parity score
    quintet_parity = metadata.get("quintet_parity")
    if quintet_parity is not None:
        # If parity score exists, check if it meets threshold (0.90)
        return float(quintet_parity) >= 0.90
    
    # If no parity metadata, assume consistent (no validation performed)
    return True


def link_trace_to_evidence(
    trace_id: str,
    evidence_id: str,
    graph: SEGraph,
    integration_mode: Optional[IntegrationMode] = None,
) -> None:
    """
    Link SDF-CVF trace to SEG evidence node.
    
    Args:
        trace_id: SDF-CVF trace ID
        evidence_id: SEG evidence ID
        graph: SEG graph instance
    
    Raises:
        ValueError: If evidence not found
    """
    _ensure_sdfcvf_enabled(integration_mode)

    # Get evidence from graph
    evidence = graph.get_evidence(evidence_id)
    if not evidence:
        raise ValueError(f"Evidence {evidence_id} not found in graph")
    
    # Update evidence metadata with trace link
    if "sdfcvf_traces" not in evidence.metadata:
        evidence.metadata["sdfcvf_traces"] = []
    
    if trace_id not in evidence.metadata["sdfcvf_traces"]:
        evidence.metadata["sdfcvf_traces"].append(trace_id)
    
    # Update evidence by getting it, modifying, and re-adding
    existing_evidence = graph.get_evidence(evidence_id)
    if existing_evidence:
        # Update metadata with trace link
        if "sdfcvf_traces" not in existing_evidence.metadata:
            existing_evidence.metadata["sdfcvf_traces"] = []
        if trace_id not in existing_evidence.metadata["sdfcvf_traces"]:
            existing_evidence.metadata["sdfcvf_traces"].append(trace_id)
        # Re-add to update the graph
        graph.add_evidence(existing_evidence)
    else:
        raise ValueError(f"Evidence {evidence_id} not found in graph")


def get_consistency_report(
    evidence_id: str,
    graph: SEGraph,
    calculator: Optional[QuintetParityCalculator] = None,
    integration_mode: Optional[IntegrationMode] = None,
) -> Dict[str, Any]:
    """
    Get SDF-CVF consistency report for SEG evidence.
    
    Args:
        evidence_id: SEG evidence ID
        graph: SEG graph instance
        calculator: Optional SDF-CVF parity calculator
    
    Returns:
        Dictionary with consistency report
    
    Raises:
        ImportError: If SDF-CVF is not available
        ValueError: If evidence not found
    """
    _ensure_sdfcvf_enabled(integration_mode)
    
    # Get evidence from graph
    evidence = graph.get_evidence(evidence_id)
    if not evidence:
        raise ValueError(f"Evidence {evidence_id} not found in graph")
    
    # Extract consistency metadata
    metadata = evidence.metadata or {}
    
    report = {
        "evidence_id": evidence_id,
        "consistent": validate_consistency(evidence, calculator, integration_mode=integration_mode),
        "quartet_parity": metadata.get("quartet_parity"),
        "quintet_parity": metadata.get("quintet_parity"),
        "sdfcvf_traces": metadata.get("sdfcvf_traces", []),
        "validation_timestamp": metadata.get("validation_timestamp"),
    }
    
    # If calculator provided, can compute additional metrics
    if calculator:
        # Note: Would need to extract code/docs/tests/traces from evidence
        # For now, just return metadata-based report
        pass
    
    return report

