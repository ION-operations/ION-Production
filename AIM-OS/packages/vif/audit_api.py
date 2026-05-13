"""VIF External Audit API

Provides read-only API for external auditing systems to query VIF witnesses,
provenance chains, and verification results. All endpoints are read-only for
security and immutability.

Based on system map: externalAudit port connects to audit.external with
secure_api protocol, exchanging audit_reports, compliance_data, verification_results.
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import logging

# VIF imports
try:
    from packages.vif.witness import VIF, ConfidenceBand, TaskCriticality
    from packages.vif.cmc_integration import VIFStore
    from packages.vif.seg_integration import verify_provenance_chain, ProvenanceChainVerification
    try:
        from packages.cmc import get_memory_store
    except ImportError:
        get_memory_store = None
except ImportError:
    from vif.witness import VIF, ConfidenceBand, TaskCriticality
    from vif.cmc_integration import VIFStore
    from vif.seg_integration import verify_provenance_chain, ProvenanceChainVerification
    try:
        from packages.cmc import get_memory_store
    except ImportError:
        get_memory_store = None

logger = logging.getLogger(__name__)


class AuditFormat(str, Enum):
    """Audit output formats"""
    JSON = "json"  # Standard JSON format
    JSON_LD = "json_ld"  # JSON-LD for linked data
    COMPACT = "compact"  # Compact format (minimal fields)
    EXPANDED = "expanded"  # Expanded format (all fields)


@dataclass
class AuditReport:
    """Audit report for external systems"""
    report_id: str
    timestamp: datetime
    witness_id: Optional[str] = None
    run_id: Optional[str] = None
    artifact_id: Optional[str] = None
    format: AuditFormat = AuditFormat.JSON
    data: Dict[str, Any] = field(default_factory=dict)
    compliance_data: Dict[str, Any] = field(default_factory=dict)
    verification_results: Dict[str, Any] = field(default_factory=dict)
    security_alerts: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AuditQuery:
    """Query parameters for audit API"""
    witness_id: Optional[str] = None
    run_id: Optional[str] = None
    artifact_id: Optional[str] = None
    model_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    confidence_min: Optional[float] = None
    confidence_max: Optional[float] = None
    task_criticality: Optional[TaskCriticality] = None
    limit: int = 100
    offset: int = 0
    format: AuditFormat = AuditFormat.JSON


# NL_TAG: VIF-AUDIT-001 | Get VIF witness for audit | get_witness_for_audit(witness_id, format) -> AuditReport | []
# NL_TAG_CONNECT: VIF-AUDIT-001 | Audit report uses VIF witness data | get_witness_for_audit → VIFStore | [VIF-AUDIT-001, VIF-STORE-001]
# NL_TAG_INTENT: VIF-INTENT-001 | Enables external audit access | read-only witness export | [ADR-VIF-AUDIT]
def get_witness_for_audit(
    witness_id: str,
    format: AuditFormat = AuditFormat.JSON,
    vif_store: Optional[VIFStore] = None,
) -> Optional[AuditReport]:
    """Get VIF witness for external audit
    
    Provides read-only access to VIF witness data for external auditing systems.
    All audit endpoints are read-only for security and immutability.
    
    Args:
        witness_id: VIF witness ID
        format: Output format (JSON, JSON_LD, COMPACT, EXPANDED)
        vif_store: VIFStore instance (optional - uses get_memory_store if None)
        
    Returns:
        AuditReport with witness data, None if witness not found
        
    Examples:
        >>> report = get_witness_for_audit("witness_123", AuditFormat.JSON)
        >>> assert report.witness_id == "witness_123"
    """
    try:
        # Get VIF store
        if vif_store is None:
            vif_store = get_memory_store()
        
        if vif_store is None:
            logger.error("VIFStore not available for audit")
            return None
        
        # Retrieve witness (VIFStore.get_witness takes atom_id, but we can search by witness_id)
        # For now, try to get by witness_id directly (assuming atom_id == witness_id)
        # In production, would use CMC tag query: {"vif_id": witness_id}
        try:
            witness = vif_store.get_witness(witness_id)
        except Exception:
            # If direct lookup fails, witness might not exist or atom_id != witness_id
            logger.warning(f"Witness {witness_id} not found for audit")
            return None
        
        if witness is None:
            logger.warning(f"Witness {witness_id} not found for audit")
            return None
        
        # Format witness data based on format
        if format == AuditFormat.COMPACT:
            data = _format_witness_compact(witness)
        elif format == AuditFormat.EXPANDED:
            data = _format_witness_expanded(witness)
        elif format == AuditFormat.JSON_LD:
            data = _format_witness_json_ld(witness)
        else:  # JSON (default)
            data = _format_witness_json(witness)
        
        # Extract compliance data
        compliance_data = _extract_compliance_data(witness)
        
        # Extract verification results
        verification_results = _extract_verification_results(witness)
        
        # Check for security alerts
        security_alerts = _check_security_alerts(witness)
        
        # Create audit report
        report = AuditReport(
            report_id=f"audit_{witness_id}_{datetime.now(timezone.utc).isoformat()}",
            timestamp=datetime.now(timezone.utc),
            witness_id=witness_id,
            format=format,
            data=data,
            compliance_data=compliance_data,
            verification_results=verification_results,
            security_alerts=security_alerts,
        )
        
        logger.info(f"Generated audit report for witness {witness_id}")
        return report
        
    except Exception as e:
        logger.error(f"Failed to get witness for audit {witness_id}: {e}")
        return None


# NL_TAG: VIF-AUDIT-002 | Query witnesses for audit | query_witnesses_for_audit(query) -> List[AuditReport] | []
# NL_TAG_CONNECT: VIF-AUDIT-002 | Audit query uses VIFStore | query_witnesses_for_audit → VIFStore | [VIF-AUDIT-002, VIF-STORE-001]
# NL_TAG_INTENT: VIF-INTENT-002 | Enables batch audit queries | filtered witness export | [ADR-VIF-AUDIT]
def query_witnesses_for_audit(
    query: AuditQuery,
    vif_store: Optional[VIFStore] = None,
) -> List[AuditReport]:
    """Query witnesses for external audit
    
    Provides filtered, paginated access to VIF witnesses for external auditing.
    Supports filtering by time range, confidence, model, task criticality, etc.
    
    Args:
        query: AuditQuery with filter parameters
        vif_store: VIFStore instance (optional - uses get_memory_store if None)
        
    Returns:
        List of AuditReport instances matching query
        
    Examples:
        >>> query = AuditQuery(
        ...     start_time=datetime(2025, 1, 1),
        ...     confidence_min=0.8,
        ...     limit=50
        ... )
        >>> reports = query_witnesses_for_audit(query)
        >>> assert len(reports) <= 50
    """
    try:
        # Get VIF store
        if vif_store is None:
            vif_store = get_memory_store()
        
        if vif_store is None:
            logger.error("VIFStore not available for audit")
            return []
        
        # Query witnesses (implementation depends on VIFStore query capabilities)
        # For now, use query_witnesses if available, otherwise return empty list
        try:
            all_witnesses = vif_store.query_witnesses(
                model_id=query.model_id,
                min_confidence=query.confidence_min,
                max_confidence=query.confidence_max,
                task_criticality=query.task_criticality.value if query.task_criticality else None,
                limit=query.limit + query.offset,
            )
        except NotImplementedError:
            logger.warning("VIFStore.query_witnesses not implemented, returning empty list")
            return []
        
        # Apply filters
        filtered_witnesses = []
        for witness in all_witnesses:
            # Filter by witness_id
            if query.witness_id and witness.id != query.witness_id:
                continue
            
            # Filter by model_id
            if query.model_id and witness.model_id != query.model_id:
                continue
            
            # Filter by time range
            if query.start_time and witness.created_at < query.start_time:
                continue
            if query.end_time and witness.created_at > query.end_time:
                continue
            
            # Filter by confidence range
            if query.confidence_min and witness.confidence_score < query.confidence_min:
                continue
            if query.confidence_max and witness.confidence_score > query.confidence_max:
                continue
            
            # Filter by task criticality
            if query.task_criticality and witness.task_criticality != query.task_criticality:
                continue
            
            filtered_witnesses.append(witness)
        
        # Apply pagination
        paginated_witnesses = filtered_witnesses[query.offset:query.offset + query.limit]
        
        # Generate audit reports
        reports = []
        for witness in paginated_witnesses:
            report = get_witness_for_audit(witness.id, query.format, vif_store)
            if report:
                reports.append(report)
        
        logger.info(f"Generated {len(reports)} audit reports for query")
        return reports
        
    except Exception as e:
        logger.error(f"Failed to query witnesses for audit: {e}")
        return []


# NL_TAG: VIF-AUDIT-003 | Get provenance chain for audit | get_provenance_chain_for_audit(witness_id, max_depth) -> AuditReport | []
# NL_TAG_CONNECT: VIF-AUDIT-003 | Provenance chain uses SEG integration | get_provenance_chain_for_audit → verify_provenance_chain | [VIF-AUDIT-003, VIF-SEG-002]
# NL_TAG_INTENT: VIF-INTENT-003 | Enables provenance audit | lineage tracing for compliance | [ADR-VIF-AUDIT]
def get_provenance_chain_for_audit(
    witness_id: str,
    max_depth: int = 5,
    format: AuditFormat = AuditFormat.JSON,
    vif_store: Optional[VIFStore] = None,
) -> Optional[AuditReport]:
    """Get provenance chain for external audit
    
    Traces the complete provenance chain for a witness, including parent witnesses
    and child witnesses, for compliance and audit purposes.
    
    Args:
        witness_id: VIF witness ID
        max_depth: Maximum depth to trace (default: 5)
        format: Output format
        vif_store: VIFStore instance (optional)
        
    Returns:
        AuditReport with provenance chain data, None if witness not found
        
    Examples:
        >>> report = get_provenance_chain_for_audit("witness_123", max_depth=10)
        >>> assert "provenance_chain" in report.data
    """
    try:
        # Get witness first
        witness_report = get_witness_for_audit(witness_id, format, vif_store)
        if witness_report is None:
            return None
        
        # Get VIF store
        if vif_store is None:
            vif_store = get_memory_store()
        
        if vif_store is None:
            logger.error("VIFStore not available for audit")
            return None
        
        # Trace provenance chain
        provenance_chain = []
        current_witness_id = witness_id
        depth = 0
        
        # Trace parent chain
        while current_witness_id and depth < max_depth:
            try:
                witness = vif_store.get_witness(current_witness_id)
            except Exception:
                break
            
            if witness is None:
                break
            
            provenance_chain.insert(0, {
                "witness_id": witness.id,
                "timestamp": witness.created_at.isoformat() if hasattr(witness, 'created_at') else None,
                "confidence": witness.confidence_score,
                "model_id": witness.model_id,
            })
            
            # Get parent witness
            if hasattr(witness, 'parent_vif_id') and witness.parent_vif_id:
                current_witness_id = witness.parent_vif_id
                depth += 1
            else:
                break
        
        # Add provenance chain to report
        witness_report.data["provenance_chain"] = provenance_chain
        witness_report.data["provenance_depth"] = len(provenance_chain)
        
        logger.info(f"Generated provenance chain audit report for witness {witness_id} (depth: {len(provenance_chain)})")
        return witness_report
        
    except Exception as e:
        logger.error(f"Failed to get provenance chain for audit {witness_id}: {e}")
        return None


# NL_TAG: VIF-AUDIT-004 | Get run witnesses for audit | get_run_witnesses_for_audit(run_id, format) -> List[AuditReport] | []
# NL_TAG_CONNECT: VIF-AUDIT-004 | Run witnesses queried from VIFStore | get_run_witnesses_for_audit → VIFStore | [VIF-AUDIT-004, VIF-STORE-001]
# NL_TAG_INTENT: VIF-INTENT-004 | Enables run-level audit | complete operation audit trail | [ADR-VIF-AUDIT]
def get_run_witnesses_for_audit(
    run_id: str,
    format: AuditFormat = AuditFormat.JSON,
    vif_store: Optional[VIFStore] = None,
) -> List[AuditReport]:
    """Get all witnesses for a run for external audit
    
    Provides read-only access to all witnesses associated with a run/operation
    for complete audit trail of the operation.
    
    Args:
        run_id: Run/operation ID
        format: Output format
        vif_store: VIFStore instance (optional)
        
    Returns:
        List of AuditReport instances for all witnesses in the run
        
    Examples:
        >>> reports = get_run_witnesses_for_audit("run_123", AuditFormat.JSON)
        >>> assert len(reports) > 0
    """
    try:
        # Query witnesses by run_id (stored in tool_parameters or metadata)
        query = AuditQuery(
            run_id=run_id,
            format=format,
            limit=1000,  # Large limit for run-level audit
        )
        
        reports = query_witnesses_for_audit(query, vif_store)
        
        # Filter by run_id in tool_parameters or metadata
        filtered_reports = []
        for report in reports:
            if report.data.get("tool_parameters", {}).get("run_id") == run_id:
                filtered_reports.append(report)
        
        logger.info(f"Generated {len(filtered_reports)} audit reports for run {run_id}")
        return filtered_reports
        
    except Exception as e:
        logger.error(f"Failed to get run witnesses for audit {run_id}: {e}")
        return []


# Helper functions for formatting

def _format_witness_json(witness: VIF) -> Dict[str, Any]:
    """Format witness as standard JSON"""
    return {
        "witness_id": witness.id,
        "version": witness.version,
        "model_id": witness.model_id,
        "model_provider": witness.model_provider,
        "confidence_score": witness.confidence_score,
        "confidence_band": witness.confidence_band.value,
        "task_criticality": witness.task_criticality.value if hasattr(witness, 'task_criticality') else None,
        "kappa_gate_passed": witness.kappa_gate_passed if hasattr(witness, 'kappa_gate_passed') else None,
        "created_at": witness.created_at.isoformat() if hasattr(witness, 'created_at') else None,
        "context_snapshot_id": witness.context_snapshot_id,
        "prompt_hash": witness.prompt_hash,
        "output_hash": witness.output_hash,
        "tool_ids": witness.tool_ids,
        "tool_parameters": witness.tool_parameters,
    }


def _format_witness_compact(witness: VIF) -> Dict[str, Any]:
    """Format witness as compact JSON (minimal fields)"""
    return {
        "witness_id": witness.id,
        "model_id": witness.model_id,
        "confidence_score": witness.confidence_score,
        "confidence_band": witness.confidence_band.value,
        "created_at": witness.created_at.isoformat() if hasattr(witness, 'created_at') else None,
    }


def _format_witness_expanded(witness: VIF) -> Dict[str, Any]:
    """Format witness as expanded JSON (all fields)"""
    data = _format_witness_json(witness)
    # Add all additional fields
    data.update({
        "weights_hash": witness.weights_hash,
        "context_atom_ids": witness.context_atom_ids,
        "prompt_template": witness.prompt_template,
        "prompt_tokens": witness.prompt_tokens,
        "retrieved_atom_ids": witness.retrieved_atom_ids,
        "tool_results_hash": witness.tool_results_hash,
        "ece_score": witness.ece_score,
        "entropy": witness.entropy,
        "top_k_probs": witness.top_k_probs,
        "replay_seed": witness.replay_seed,
        "temperature": witness.temperature,
        "top_p": witness.top_p,
        "top_k": witness.top_k,
        "max_tokens": witness.max_tokens,
        "other_params": witness.other_params,
        "output_tokens": witness.output_tokens,
        "total_tokens": witness.total_tokens,
        "writer": witness.writer,
        "kappa_threshold": witness.kappa_threshold if hasattr(witness, 'kappa_threshold') else None,
        "parent_vif_id": witness.parent_vif_id if hasattr(witness, 'parent_vif_id') else None,
        "execution_time_ms": witness.execution_time_ms if hasattr(witness, 'execution_time_ms') else None,
    })
    return data


def _format_witness_json_ld(witness: VIF) -> Dict[str, Any]:
    """Format witness as JSON-LD for linked data"""
    base_data = _format_witness_json(witness)
    # Add JSON-LD context
    base_data["@context"] = {
        "@vocab": "https://aim-os.org/vif/",
        "witness": "https://aim-os.org/vif/witness",
        "model": "https://aim-os.org/vif/model",
        "confidence": "https://aim-os.org/vif/confidence",
    }
    base_data["@type"] = "VIFWitness"
    base_data["@id"] = f"https://aim-os.org/vif/witness/{witness.id}"
    return base_data


def _extract_compliance_data(witness: VIF) -> Dict[str, Any]:
    """Extract compliance data from witness"""
    return {
        "confidence_band": witness.confidence_band.value,
        "task_criticality": witness.task_criticality.value if hasattr(witness, 'task_criticality') else None,
        "kappa_gate_passed": witness.kappa_gate_passed if hasattr(witness, 'kappa_gate_passed') else None,
        "model_id": witness.model_id,
        "model_provider": witness.model_provider,
        "created_at": witness.created_at.isoformat() if hasattr(witness, 'created_at') else None,
        "version": witness.version,
    }


def _extract_verification_results(witness: VIF) -> Dict[str, Any]:
    """Extract verification results from witness"""
    return {
        "confidence_score": witness.confidence_score,
        "confidence_band": witness.confidence_band.value,
        "ece_score": witness.ece_score,
        "kappa_gate_passed": witness.kappa_gate_passed if hasattr(witness, 'kappa_gate_passed') else None,
        "prompt_hash": witness.prompt_hash,
        "output_hash": witness.output_hash,
        "context_snapshot_id": witness.context_snapshot_id,
    }


def _check_security_alerts(witness: VIF) -> List[Dict[str, Any]]:
    """Check for security alerts in witness"""
    alerts = []
    
    # Check for low confidence on critical tasks
    if hasattr(witness, 'task_criticality') and witness.task_criticality == TaskCriticality.CRITICAL:
        if witness.confidence_score < 0.70:
            alerts.append({
                "type": "low_confidence_critical_task",
                "severity": "high",
                "message": f"Low confidence ({witness.confidence_score:.2f}) on critical task",
                "witness_id": witness.id,
            })
    
    # Check for κ-gate failure
    if hasattr(witness, 'kappa_gate_passed') and not witness.kappa_gate_passed:
        alerts.append({
            "type": "kappa_gate_failed",
            "severity": "critical",
            "message": "κ-gate failed - operation should not have proceeded",
            "witness_id": witness.id,
        })
    
    # Check for high ECE (calibration error)
    if witness.ece_score and witness.ece_score > 0.10:
        alerts.append({
            "type": "high_calibration_error",
            "severity": "medium",
            "message": f"High ECE score ({witness.ece_score:.3f}) indicates calibration issues",
            "witness_id": witness.id,
        })
    
    return alerts

