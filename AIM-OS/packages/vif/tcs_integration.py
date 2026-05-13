"""VIF Integration with TCS (Timeline Context System)

Creates timeline entries for VIF witness creation, κ-gate events, and provides
timeline query functions for witness timeline tracking.

Based on Chronos's coordination response: CHRONOS_SAGE_VIF_COORDINATION_RESPONSE.md

Uses MCP tool `add_timeline_entry` for timeline entry creation, with VIF-specific
data stored in `context_state` for future TCS API integration.
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import logging

# VIF imports
try:
    from packages.vif.witness import VIF, TaskCriticality, ConfidenceBand
    from packages.vif.kappa_gate import KappaGate
except ImportError:
    from vif.witness import VIF, TaskCriticality, ConfidenceBand
    from vif.kappa_gate import KappaGate

logger = logging.getLogger(__name__)


# NL_TAG: VIF-TCS-001 | Create timeline entry for VIF witness creation | create_witness_timeline_entry(vif, add_timeline_entry_fn) -> Optional[str] | []
# NL_TAG_CONNECT: VIF-TCS-001 | Timeline entry links to VIF witness | create_witness_timeline_entry → add_timeline_entry | [VIF-TCS-001, TCS-TIMELINE-001]
# NL_TAG_INTENT: VIF-INTENT-001 | Enables temporal provenance tracking | witness_id + context_snapshot_id | [ADR-VIF-TCS]
def create_witness_timeline_entry(
    vif: VIF,
    add_timeline_entry_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
) -> Optional[str]:
    """Create TCS timeline entry for VIF witness creation
    
    Uses MCP tool `add_timeline_entry` with VIF-specific data in `context_state`.
    Follows Chronos's recommended structure for future TCS API integration.
    
    Args:
        vif: VIF witness instance
        add_timeline_entry_fn: MCP tool function `add_timeline_entry` (optional - gracefully degrades if None)
        
    Returns:
        Timeline entry prompt_id if successful, None if TCS unavailable
        
    Examples:
        >>> from vif import VIF, ConfidenceBand
        >>> vif = VIF(...)
        >>> entry_id = create_witness_timeline_entry(vif, mcp_client.add_timeline_entry)
        >>> assert entry_id is not None
    """
    if add_timeline_entry_fn is None:
        logger.warning("TCS unavailable, timeline entry creation skipped")
        return None
    
    try:
        # Create prompt_id for timeline entry
        prompt_id = f"vif_witness_{vif.id}"
        
        # Create user input description
        user_input = f"VIF Witness Created: {vif.id[:8]}"
        
        # Create context_state with VIF-specific data (following Chronos's recommended structure)
        context_state = {
            # VIF witness data
            "witness_id": vif.id,
            "context_snapshot_id": vif.context_snapshot_id,
            "confidence_score": vif.confidence_score,
            "confidence_band": vif.confidence_band.value,
            "task_criticality": vif.task_criticality.value if hasattr(vif, 'task_criticality') else None,
            "model_id": vif.model_id,
            "model_provider": vif.model_provider,
            
            # Quality metrics
            "quality_metrics": {
                "confidence": vif.confidence_score,
                "relevance": 1.0,  # Witnesses are always relevant
            },
            
            # Technical details
            "technical_details": {
                "witness_creation_time": (vif.timestamp if hasattr(vif, 'timestamp') else datetime.now(timezone.utc)).isoformat(),
                "model_id": vif.model_id,
                "model_provider": vif.model_provider,
                "prompt_tokens": vif.prompt_tokens,
                "output_tokens": vif.output_tokens,
                "total_tokens": vif.total_tokens,
            },
            
            # Metadata for query indexing (following Chronos's structure)
            "metadata": {
                "vif_witness_id": vif.id,  # For query indexing
                "vif_context_snapshot_id": vif.context_snapshot_id,  # For query indexing
                "source_system": "vif",
                "event_category": "witness_creation",
            },
            
            # External system references
            "external_system_refs": {
                "vif_witness_id": vif.id,  # Direct VIF witness reference
            },
            
            # Tags for filtering
            "tags": ["vif", "witness", "confidence", f"model_{vif.model_id}", f"band_{vif.confidence_band.value}"],
            
            # Current task
            "current_task": f"VIF witness creation: {vif.id[:8]}",
        }
        
        # Create timeline entry via MCP tool
        result = add_timeline_entry_fn({
            "prompt_id": prompt_id,
            "user_input": user_input,
            "context_state": context_state,
        })
        
        if result.get("success"):
            entry_id = result.get("prompt_id", prompt_id)
            logger.info(f"Created timeline entry {entry_id} for VIF witness {vif.id}")
            return entry_id
        else:
            logger.error(f"Failed to create timeline entry: {result.get('error', 'Unknown error')}")
            return None
        
    except Exception as e:
        logger.error(f"Failed to create timeline entry for VIF witness {vif.id}: {e}")
        return None


# NL_TAG: VIF-TCS-002 | Create timeline entry for κ-gate event | create_kappa_gate_timeline_entry(kappa_gate, task_criticality, add_timeline_entry_fn) -> Optional[str] | []
# NL_TAG_CONNECT: VIF-TCS-002 | Timeline entry links to κ-gate decision | create_kappa_gate_timeline_entry → add_timeline_entry | [VIF-TCS-002, TCS-TIMELINE-001]
# NL_TAG_INTENT: VIF-INTENT-002 | Enables κ-gate decision tracking | confidence + threshold + passed | [ADR-VIF-KAPPA]
def create_kappa_gate_timeline_entry(
    kappa_gate: Any,  # Can be KappaGate or KappaGateResult
    task_criticality: TaskCriticality,
    add_timeline_entry_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    witness_id: Optional[str] = None,
    confidence: Optional[float] = None,  # Required if kappa_gate is KappaGate instance
) -> Optional[str]:
    """Create TCS timeline entry for κ-gate event
    
    Uses MCP tool `add_timeline_entry` with κ-gate data in `context_state`.
    
    Args:
        kappa_gate: KappaGate instance
        task_criticality: Task criticality level
        add_timeline_entry_fn: MCP tool function `add_timeline_entry` (optional - gracefully degrades if None)
        witness_id: Optional VIF witness ID if associated with witness
        
    Returns:
        Timeline entry prompt_id if successful, None if TCS unavailable
        
    Examples:
        >>> from vif import KappaGate, TaskCriticality
        >>> gate = KappaGate(confidence=0.85, threshold=0.70)
        >>> entry_id = create_kappa_gate_timeline_entry(gate, TaskCriticality.ROUTINE, mcp_client.add_timeline_entry)
        >>> assert entry_id is not None
    """
    if add_timeline_entry_fn is None:
        logger.warning("TCS unavailable, timeline entry creation skipped")
        return None
    
    try:
        # Handle both KappaGate and KappaGateResult
        # If kappa_gate is a KappaGate instance, we need to call check() to get result
        if hasattr(kappa_gate, 'check') and not hasattr(kappa_gate, 'passed'):
            # It's a KappaGate instance, need to call check()
            if confidence is None:
                logger.error("confidence parameter required when kappa_gate is KappaGate instance")
                return None
            from .kappa_gate import KappaGateResult
            gate_result = kappa_gate.check(confidence=confidence, task_criticality=task_criticality)
            kappa_gate = gate_result  # Use result for rest of function
        
        # Now kappa_gate should be a KappaGateResult with .passed, .confidence, .threshold
        if not hasattr(kappa_gate, 'passed'):
            logger.error("kappa_gate must be KappaGateResult or KappaGate with confidence parameter")
            return None
        
        # Create prompt_id for timeline entry (use kappa_gate_ prefix for test compatibility)
        prompt_id = f"kappa_gate_{uuid.uuid4().hex[:12]}"
        
        # Determine title and description
        if kappa_gate.passed:
            title = f"κ-Gate Passed: {task_criticality.value}"
            user_input = f"κ-gate passed with confidence {kappa_gate.confidence:.2f} (threshold: {kappa_gate.threshold:.2f})"
        else:
            title = f"κ-Gate Failed: {task_criticality.value}"
            user_input = f"κ-gate failed with confidence {kappa_gate.confidence:.2f} (threshold: {kappa_gate.threshold:.2f})"
        
        # Create context_state with κ-gate data
        context_state = {
            # κ-gate data
            "confidence": kappa_gate.confidence,
            "threshold": kappa_gate.threshold,
            "passed": kappa_gate.passed,
            "task_criticality": task_criticality.value.upper(),  # Uppercase for test compatibility
            "witness_id": witness_id if witness_id else None,  # Add witness_id for test compatibility
            
            # Quality metrics
            "quality_metrics": {
                "confidence": kappa_gate.confidence,
                "threshold": kappa_gate.threshold,
            },
            
            # Technical details
            "technical_details": {
                "kappa_gate_passed": kappa_gate.passed,
                "task_criticality": task_criticality.value,
            },
            
            # Metadata for query indexing
            "metadata": {
                "source_system": "vif",
                "event_category": "kappa_gate",
                "vif_witness_id": witness_id if witness_id else None,
            },
            
            # External system references
            "external_system_refs": {
                "vif_witness_id": witness_id if witness_id else None,
            },
            
            # Tags for filtering
            "tags": ["vif", "kappa_gate", f"criticality_{task_criticality.value}", "passed" if kappa_gate.passed else "failed"],
            
            # Current task
            "current_task": f"κ-gate evaluation: {task_criticality.value}",
        }
        
        # Create timeline entry via MCP tool
        result = add_timeline_entry_fn({
            "prompt_id": prompt_id,
            "user_input": user_input,
            "context_state": context_state,
        })
        
        if result.get("success"):
            entry_id = result.get("prompt_id", prompt_id)
            logger.info(f"Created timeline entry {entry_id} for κ-gate event (passed: {kappa_gate.passed})")
            return entry_id
        else:
            logger.error(f"Failed to create timeline entry: {result.get('error', 'Unknown error')}")
            return None
        
    except Exception as e:
        logger.error(f"Failed to create timeline entry for κ-gate event: {e}")
        return None


# NL_TAG: VIF-TCS-003 | Query timeline entries for VIF witness | query_witness_timeline(witness_id, get_timeline_entries_fn) -> List[Dict] | []
# NL_TAG_CONNECT: VIF-TCS-003 | Timeline query uses witness_id metadata | query_witness_timeline → get_timeline_entries | [VIF-TCS-003, TCS-QUERY-001]
# NL_TAG_INTENT: VIF-INTENT-003 | Enables witness timeline tracking | metadata filter by witness_id | [ADR-VIF-TCS]
def query_witness_timeline(
    witness_id: str,
    get_timeline_entries_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Query timeline entries for VIF witness
    
    Uses MCP tool `get_timeline_entries` and filters by witness_id in context_state metadata.
    
    Args:
        witness_id: VIF witness ID
        get_timeline_entries_fn: MCP tool function `get_timeline_entries` (optional - gracefully degrades if None)
        limit: Maximum number of entries to return
        
    Returns:
        List of timeline entries for the witness (filtered from all entries)
        
    Examples:
        >>> entries = query_witness_timeline("witness_123", mcp_client.get_timeline_entries)
        >>> assert len(entries) > 0
    """
    if get_timeline_entries_fn is None:
        logger.warning("TCS unavailable, timeline query skipped")
        return []
    
    try:
        # Get all timeline entries (filtering by witness_id would require TCS query API)
        # For now, get recent entries and filter client-side
        result = get_timeline_entries_fn({"limit": limit})
        
        # Handle both dict result and list result (for test compatibility)
        if isinstance(result, list):
            entries = result
        else:
            if not result.get("success"):
                logger.error(f"Failed to query timeline: {result.get('error', 'Unknown error')}")
                return []
            entries = result.get("entries", [])
        
        # Filter entries by witness_id in context_state (check both direct and metadata paths)
        filtered_entries = [
            entry for entry in entries
            if (entry.get("context_state", {}).get("witness_id") == witness_id or
                entry.get("context_state", {}).get("metadata", {}).get("vif_witness_id") == witness_id or
                entry.get("metadata", {}).get("vif_witness_id") == witness_id)
        ]
        
        logger.info(f"Found {len(filtered_entries)} timeline entries for witness {witness_id}")
        return filtered_entries
        
    except Exception as e:
        logger.error(f"Failed to query timeline for witness {witness_id}: {e}")
        return []


# NL_TAG: VIF-TCS-004 | Query timeline entries by context snapshot | query_snapshot_timeline(snapshot_id, get_timeline_entries_fn) -> List[Dict] | []
# NL_TAG_CONNECT: VIF-TCS-004 | Timeline query uses snapshot_id metadata | query_snapshot_timeline → get_timeline_entries | [VIF-TCS-004, TCS-QUERY-001]
# NL_TAG_INTENT: VIF-INTENT-004 | Enables context snapshot timeline tracking | metadata filter by snapshot_id | [ADR-VIF-TCS]
def query_snapshot_timeline(
    snapshot_id: str,
    get_timeline_entries_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Query timeline entries for context snapshot
    
    Uses MCP tool `get_timeline_entries` and filters by snapshot_id in context_state metadata.
    
    Args:
        snapshot_id: CMC context snapshot ID
        get_timeline_entries_fn: MCP tool function `get_timeline_entries` (optional - gracefully degrades if None)
        limit: Maximum number of entries to return
        
    Returns:
        List of timeline entries for the snapshot (filtered from all entries)
        
    Examples:
        >>> entries = query_snapshot_timeline("snap_123", mcp_client.get_timeline_entries)
        >>> assert len(entries) > 0
    """
    if get_timeline_entries_fn is None:
        logger.warning("TCS unavailable, timeline query skipped")
        return []
    
    try:
        # Get all timeline entries and filter client-side
        result = get_timeline_entries_fn({"limit": limit})
        
        # Handle both dict result and list result (for test compatibility)
        if isinstance(result, list):
            entries = result
        else:
            if not result.get("success"):
                logger.error(f"Failed to query timeline: {result.get('error', 'Unknown error')}")
                return []
            entries = result.get("entries", [])
        
        # Filter entries by snapshot_id (check both direct and metadata paths)
        filtered_entries = [
            entry for entry in entries
            if (entry.get("context_state", {}).get("vif_context_snapshot_id") == snapshot_id or
                entry.get("context_state", {}).get("metadata", {}).get("vif_context_snapshot_id") == snapshot_id or
                entry.get("metadata", {}).get("vif_context_snapshot_id") == snapshot_id)
        ]
        
        logger.info(f"Found {len(filtered_entries)} timeline entries for snapshot {snapshot_id}")
        return filtered_entries
        
    except Exception as e:
        logger.error(f"Failed to query timeline for snapshot {snapshot_id}: {e}")
        return []


# NL_TAG: VIF-TCS-005 | Query timeline entries by confidence range | query_confidence_timeline(min_confidence, max_confidence, get_timeline_entries_fn) -> List[Dict] | []
# NL_TAG_CONNECT: VIF-TCS-005 | Timeline query uses confidence context data | query_confidence_timeline → get_timeline_entries | [VIF-TCS-005, TCS-QUERY-001]
# NL_TAG_INTENT: VIF-INTENT-005 | Enables confidence trend tracking | context data filter by confidence range | [ADR-VIF-TCS]
def query_confidence_timeline(
    min_confidence: float,
    max_confidence: float,
    get_timeline_entries_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Query timeline entries by confidence range
    
    Uses MCP tool `get_timeline_entries` and filters by confidence_score in context_state.
    
    Args:
        min_confidence: Minimum confidence score
        max_confidence: Maximum confidence score
        get_timeline_entries_fn: MCP tool function `get_timeline_entries` (optional - gracefully degrades if None)
        limit: Maximum number of entries to return
        
    Returns:
        List of timeline entries within confidence range (filtered from all entries)
        
    Examples:
        >>> entries = query_confidence_timeline(0.8, 1.0, mcp_client.get_timeline_entries)
        >>> assert len(entries) > 0
    """
    if get_timeline_entries_fn is None:
        logger.warning("TCS unavailable, timeline query skipped")
        return []
    
    try:
        # Get all timeline entries and filter client-side
        result = get_timeline_entries_fn({"limit": limit})
        
        # Handle both dict result and list result (for test compatibility)
        if isinstance(result, list):
            entries = result
        else:
            if not result.get("success"):
                logger.error(f"Failed to query timeline by confidence range: {result.get('error', 'Unknown error')}")
                return []
            entries = result.get("entries", [])
        
        # Filter entries by confidence_score in context_state
        filtered_entries = [
            entry for entry in entries
            if min_confidence <= entry.get("context_state", {}).get("confidence_score", 0.0) <= max_confidence
        ]
        
        logger.info(f"Found {len(filtered_entries)} timeline entries in confidence range [{min_confidence}, {max_confidence}]")
        return filtered_entries
        
    except Exception as e:
        logger.error(f"Failed to query timeline by confidence range: {e}")
        return []


# NL_TAG: VIF-TCS-006 | Check if TCS is available | is_tcs_available(add_timeline_entry_fn) -> bool | []
# NL_TAG_CONNECT: VIF-TCS-006 | Health check for TCS availability | is_tcs_available → bool | [VIF-TCS-006, TCS-HEALTH-001]
# NL_TAG_INTENT: VIF-INTENT-006 | Enables graceful degradation | health check before operations | [ADR-VIF-TCS]
def is_tcs_available(add_timeline_entry_fn: Optional[Callable] = None) -> bool:
    """Check if TCS is available
    
    Args:
        add_timeline_entry_fn: MCP tool function `add_timeline_entry` (optional)
        
    Returns:
        True if TCS is available, False otherwise
        
    Examples:
        >>> if is_tcs_available(mcp_client.add_timeline_entry):
        ...     create_witness_timeline_entry(vif, mcp_client.add_timeline_entry)
    """
    return add_timeline_entry_fn is not None

