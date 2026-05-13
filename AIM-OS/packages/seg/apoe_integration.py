"""
APOE (Autonomous Plan Orchestration Engine) → SEG (Shared Evidence Graph) Integration

Enables bidirectional integration between APOE execution traces and SEG evidence nodes.

This integration enables:
- Execution trace → Evidence storage (plan + step level)
- Plan effectiveness tracking (evidence-based metrics)
- Trace ↔ Evidence linking (bidirectional references)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from .models import Evidence
from .seg_graph import SEGraph

try:
    from packages.apoe.seg_integration import APOESEGIntegration
    from packages.apoe.models import ExecutionPlan, ExecutionResult
    APOE_AVAILABLE = True
except ImportError:
    APOE_AVAILABLE = False
    # Type stubs for when APOE is not available
    APOESEGIntegration = None  # type: ignore
    ExecutionPlan = None  # type: ignore
    ExecutionResult = None  # type: ignore


def store_execution_trace(
    trace: Dict[str, Any],
    graph: Optional[SEGraph] = None,
    execution_id: Optional[str] = None
) -> str:
    """
    Store APOE execution trace as SEG evidence node.
    
    Args:
        trace: Execution trace dictionary (from APOE)
        graph: Optional SEG graph instance (if None, creates standalone evidence)
        execution_id: Optional execution ID (if None, generates from trace)
    
    Returns:
        Evidence ID
    
    Raises:
        ImportError: If APOE is not available
        ValueError: If trace is invalid
    """
    if not APOE_AVAILABLE:
        raise ImportError("APOE service not available. Install apoe package.")
    
    if not trace:
        raise ValueError("Trace cannot be None or empty")
    
    # Extract trace data
    plan_name = trace.get("plan_name", trace.get("plan_id", "unknown"))
    execution_id = execution_id or trace.get("execution_id", f"exec_{datetime.now(timezone.utc).timestamp()}")
    status = trace.get("status", "unknown")
    success = trace.get("success", False)
    steps_completed = trace.get("steps_completed", trace.get("completed_steps", 0))
    total_steps = trace.get("total_steps", 0)
    duration = trace.get("duration_seconds", trace.get("total_duration_seconds", 0.0))
    
    # Create evidence from trace
    evidence = Evidence(
        content=f"APOE Execution Trace: {plan_name}",
        source=f"apoe.execution:{execution_id}",
        evidence_type="apoe_execution_trace",
        confidence=1.0 if success else 0.5,
        reliability=0.9,  # Execution traces are reliable
        metadata={
            "plan_name": plan_name,
            "execution_id": execution_id,
            "status": status,
            "success": success,
            "steps_completed": steps_completed,
            "total_steps": total_steps,
            "duration_seconds": duration,
            "trace_data": trace,  # Store full trace
        },
        tags=["apoe", "execution_trace", plan_name],
        vt_start=datetime.fromisoformat(trace["started_at"]) if trace.get("started_at") else datetime.now(timezone.utc),
    )
    
    # Add to graph if provided
    if graph:
        evidence = graph.add_evidence(evidence)
    
    return evidence.id


def get_plan_effectiveness(
    plan_id: str,
    graph: SEGraph,
    limit: int = 10
) -> float:
    """
    Get plan effectiveness score from SEG evidence.
    
    Args:
        plan_id: Plan identifier
        graph: SEG graph instance
        limit: Maximum number of executions to consider
    
    Returns:
        Average effectiveness score (0.0-1.0)
    
    Raises:
        ValueError: If plan not found
    """
    # Get all plan effectiveness evidence
    all_evidence = graph.list_evidence()
    
    # Filter for plan effectiveness
    effectiveness_evidence = [
        e for e in all_evidence
        if e.evidence_type == "apoe_plan_effectiveness"
        and e.metadata.get("plan_name") == plan_id
    ]
    
    # Sort by timestamp (most recent first)
    effectiveness_evidence.sort(
        key=lambda e: e.metadata.get("computed_at", ""),
        reverse=True
    )
    
    # Get limited results
    recent_effectiveness = effectiveness_evidence[:limit]
    
    if not recent_effectiveness:
        return 0.0
    
    # Calculate average effectiveness score
    scores = [
        e.metadata.get("effectiveness_score", e.confidence)
        for e in recent_effectiveness
    ]
    
    return sum(scores) / len(scores) if scores else 0.0


def link_trace_to_evidence(
    trace_id: str,
    evidence_id: str,
    graph: SEGraph
) -> None:
    """
    Link APOE execution trace to SEG evidence node.
    
    Args:
        trace_id: APOE trace ID (execution_id)
        evidence_id: SEG evidence ID
        graph: SEG graph instance
    
    Raises:
        ValueError: If trace or evidence not found
    """
    # Get evidence from graph
    evidence = graph.get_evidence(evidence_id)
    if not evidence:
        raise ValueError(f"Evidence {evidence_id} not found in graph")
    
    # Update evidence metadata with trace link
    if "apoe_traces" not in evidence.metadata:
        evidence.metadata["apoe_traces"] = []
    
    if trace_id not in evidence.metadata["apoe_traces"]:
        evidence.metadata["apoe_traces"].append(trace_id)
    
    # Update evidence by getting it, modifying, and re-adding
    existing_evidence = graph.get_evidence(evidence_id)
    if existing_evidence:
        # Update metadata with trace link
        if "apoe_traces" not in existing_evidence.metadata:
            existing_evidence.metadata["apoe_traces"] = []
        if trace_id not in existing_evidence.metadata["apoe_traces"]:
            existing_evidence.metadata["apoe_traces"].append(trace_id)
        # Re-add to update the graph
        graph.add_evidence(existing_evidence)
    else:
        raise ValueError(f"Evidence {evidence_id} not found in graph")

