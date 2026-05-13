"""
CAS (Cognitive Analysis System) → SEG (Shared Evidence Graph) Integration

Enables bidirectional integration between CAS failure mode patterns and SEG evidence nodes.

This integration enables:
- Failure pattern → Evidence storage (pattern analysis)
- Failure pattern retrieval (query by failure type)
- Pattern ↔ Evidence linking (bidirectional references)
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Literal

from .models import Evidence
from .seg_graph import SEGraph

try:
    from packages.cas.failure_modes import FailurePattern, FailureEvent, FailureModeAnalyzer
    CAS_AVAILABLE = True
except ImportError:
    CAS_AVAILABLE = False
    # Type stubs for when CAS is not available
    FailurePattern = None  # type: ignore
    FailureEvent = None  # type: ignore
    FailureModeAnalyzer = None  # type: ignore


IntegrationMode = Literal["strict", "auto", "fallback", "mocked"]
_VALID_INTEGRATION_MODES = {"strict", "auto", "fallback", "mocked"}
_DEFAULT_INTEGRATION_MODE = os.getenv("AIMOS_SEG_CAS_MODE", "strict")


def _resolve_integration_mode(integration_mode: Optional[IntegrationMode]) -> str:
    mode = (integration_mode or _DEFAULT_INTEGRATION_MODE).strip().lower()
    if mode not in _VALID_INTEGRATION_MODES:
        valid = ", ".join(sorted(_VALID_INTEGRATION_MODES))
        raise ValueError(f"Invalid integration_mode '{mode}'. Expected one of: {valid}")
    return mode


def _ensure_cas_enabled(integration_mode: Optional[IntegrationMode]) -> None:
    mode = _resolve_integration_mode(integration_mode)
    if mode == "strict":
        raise ImportError("CAS integration is disabled in strict mode.")
    if mode in {"auto", "fallback"} and not CAS_AVAILABLE:
        raise ImportError("CAS service not available. Install cas package or use mocked mode.")


def store_failure_pattern(
    pattern: Dict[str, Any],
    graph: Optional[SEGraph] = None,
    integration_mode: Optional[IntegrationMode] = None,
) -> str:
    """
    Store CAS failure pattern as SEG evidence node.
    
    Args:
        pattern: Failure pattern dictionary (from CAS)
        graph: Optional SEG graph instance (if None, creates standalone evidence)
    
    Returns:
        Evidence ID
    
    Raises:
        ImportError: If CAS is not available
        ValueError: If pattern is invalid
    """
    _ensure_cas_enabled(integration_mode)
    
    if not pattern:
        raise ValueError("Pattern cannot be None or empty")
    
    # Extract pattern data
    pattern_type = pattern.get("pattern", pattern.get("failure_pattern", "unknown"))
    severity = pattern.get("severity", "medium")
    description = pattern.get("description", pattern.get("failure_description", ""))
    context = pattern.get("context", {})
    evidence_list = pattern.get("evidence", [])
    suggested_actions = pattern.get("suggested_actions", [])
    
    # Create evidence from pattern
    evidence = Evidence(
        content=f"CAS Failure Pattern: {pattern_type} - {description}",
        source=f"cas.failure_pattern:{pattern.get('event_id', 'unknown')}",
        evidence_type="cas_failure_pattern",
        confidence=0.8,  # Failure patterns are moderately reliable
        reliability=0.85,  # CAS analysis is reliable
        metadata={
            "pattern_type": pattern_type,
            "severity": severity,
            "description": description,
            "context": context,
            "evidence": evidence_list,
            "suggested_actions": suggested_actions,
            "detected_at": pattern.get("timestamp", datetime.now(timezone.utc).isoformat()),
            "resolved": pattern.get("resolved", False),
        },
        tags=["cas", "failure_pattern", pattern_type, severity],
        vt_start=datetime.fromisoformat(pattern["timestamp"]) if isinstance(pattern.get("timestamp"), str) else datetime.now(timezone.utc),
    )
    
    # Add to graph if provided
    if graph:
        evidence = graph.add_evidence(evidence)
    
    return evidence.id


def get_failure_patterns(
    failure_type: str,
    graph: SEGraph,
    limit: int = 10,
    integration_mode: Optional[IntegrationMode] = None,
) -> List[Evidence]:
    """
    Get CAS failure patterns from SEG evidence by failure type.
    
    Args:
        failure_type: Failure pattern type (e.g., "categorization_error")
        graph: SEG graph instance
        limit: Maximum number of patterns to return
    
    Returns:
        List of Evidence nodes matching failure type
    
    Raises:
        ImportError: If CAS is not available
    """
    _ensure_cas_enabled(integration_mode)
    
    # Get all CAS failure pattern evidence
    all_evidence = graph.list_evidence()
    
    # Filter for failure patterns of specified type
    failure_patterns = [
        e for e in all_evidence
        if e.evidence_type == "cas_failure_pattern"
        and e.metadata.get("pattern_type") == failure_type
    ]
    
    # Sort by timestamp (most recent first)
    failure_patterns.sort(
        key=lambda e: e.metadata.get("detected_at", ""),
        reverse=True
    )
    
    # Return limited results
    return failure_patterns[:limit]


def link_pattern_to_evidence(
    pattern_id: str,
    evidence_id: str,
    graph: SEGraph
) -> None:
    """
    Link CAS failure pattern to SEG evidence node.
    
    Args:
        pattern_id: CAS pattern ID (event_id)
        evidence_id: SEG evidence ID
        graph: SEG graph instance
    
    Raises:
        ValueError: If pattern or evidence not found
    """
    # Get evidence from graph
    evidence = graph.get_evidence(evidence_id)
    if not evidence:
        raise ValueError(f"Evidence {evidence_id} not found in graph")
    
    # Update evidence metadata with pattern link
    if "cas_patterns" not in evidence.metadata:
        evidence.metadata["cas_patterns"] = []
    
    if pattern_id not in evidence.metadata["cas_patterns"]:
        evidence.metadata["cas_patterns"].append(pattern_id)
    
    # Update evidence by getting it, modifying, and re-adding
    existing_evidence = graph.get_evidence(evidence_id)
    if existing_evidence:
        # Update metadata with pattern link
        if "cas_patterns" not in existing_evidence.metadata:
            existing_evidence.metadata["cas_patterns"] = []
        if pattern_id not in existing_evidence.metadata["cas_patterns"]:
            existing_evidence.metadata["cas_patterns"].append(pattern_id)
        # Re-add to update the graph
        graph.add_evidence(existing_evidence)
    else:
        raise ValueError(f"Evidence {evidence_id} not found in graph")

