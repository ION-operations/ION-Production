"""VIF Integration for APOE

Creates VIF witnesses for APOE operations (plan execution, step execution).
Enhanced with full VIF objects and κ-gating support.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
import json

from .models import Step, RoleType
from .executor import ExecutionResult
from .acl_parser import ExecutionPlan

# VIF imports (optional - gracefully handle if VIF not available)
try:
    from packages.vif.witness import VIF, ConfidenceBand, TaskCriticality
    from packages.vif.kappa_gate import KappaGate
    from packages.vif.confidence_bands import determine_band
    from packages.vif.cmc_integration import VIFStore, create_witness_and_store
    from packages.cmc import get_memory_store
    VIF_AVAILABLE = True
except ImportError:
    VIF_AVAILABLE = False
    VIF = None
    ConfidenceBand = None
    TaskCriticality = None
    KappaGate = None
    determine_band = None
    VIFStore = None
    create_witness_and_store = None
    get_memory_store = None


# NL_TAG: VIF-INTEG-004 | Map APOE role to VIF task criticality. | map_role_to_criticality(role) | []
# NL_TAG_INTENT: VIF-INTENT-003 | Design decision: role-to-criticality mapping | map_role_to_criticality | [ADR-VIF-APOE]
def map_role_to_criticality(role: RoleType) -> TaskCriticality:
    """
    Map APOE role to VIF task criticality.
    
    Args:
        role: APOE role type
        
    Returns:
        VIF task criticality level
        
    Examples:
        >>> map_role_to_criticality(RoleType.VERIFIER)
        TaskCriticality.CRITICAL
        >>> map_role_to_criticality(RoleType.RETRIEVER)
        TaskCriticality.ROUTINE
    """
    if not VIF_AVAILABLE:
        # Fallback if VIF not available
        return None
    
    # Role-to-criticality mapping
    role_criticality_map = {
        RoleType.VERIFIER: TaskCriticality.CRITICAL,   # Verification is critical
        RoleType.WITNESS: TaskCriticality.CRITICAL,     # Witness operations are critical
        RoleType.PLANNER: TaskCriticality.IMPORTANT,    # Planning is important
        RoleType.REASONER: TaskCriticality.IMPORTANT,   # Reasoning is important
        RoleType.CRITIC: TaskCriticality.IMPORTANT,     # Criticism is important
        RoleType.RETRIEVER: TaskCriticality.ROUTINE,    # Retrieval is routine
        RoleType.BUILDER: TaskCriticality.ROUTINE,      # Building is routine
        RoleType.OPERATOR: TaskCriticality.ROUTINE,     # Operations are routine
    }
    
    return role_criticality_map.get(role, TaskCriticality.ROUTINE)


# NL_TAG: VIF-INTEG-005 | Create full VIF witness object for plan execution. | create_plan_witness_vif(plan, result, context_snapshot_id, confidence) | []
# NL_TAG_CONNECT: VIF-CMC-002 | Plan witness stored in CMC | create_plan_witness_vif → store_witness_in_cmc | [VIF-INTEG-005, CMC-STORE-001]
# NL_TAG_INTENT: VIF-INTENT-004 | Design decision: full VIF objects for provenance | create_plan_witness_vif | [ADR-VIF-APOE]
def create_plan_witness_vif(
    plan: ExecutionPlan,
    result: ExecutionResult,
    context_snapshot_id: str,
    confidence: float = 0.95,
    **kwargs
) -> VIF:
    """
    Create full VIF witness object for plan execution.
    
    Args:
        plan: Executed plan
        result: Execution result
        context_snapshot_id: CMC snapshot ID
        confidence: Confidence in execution (0.0-1.0)
        **kwargs: Additional VIF fields
        
    Returns:
        VIF witness object
        
    Examples:
        >>> vif = create_plan_witness_vif(plan, result, "snap_123", 0.95)
        >>> assert isinstance(vif, VIF)
        >>> assert vif.confidence_score == 0.95
    """
    if not VIF_AVAILABLE:
        raise ImportError("VIF package not available - cannot create VIF witness")
    
    # Prepare plan inputs and outputs
    plan_inputs = {
        "plan_name": plan.name,
        "total_steps": result.total_steps,
        "roles": list(plan.roles.keys()),
        "steps": [step.name for step in plan.steps],
    }
    plan_outputs = {
        "completed_steps": result.completed_steps,
        "failed_steps": result.failed_steps,
        "success": result.success,
        "duration_seconds": result.total_duration_seconds,
        "completion_rate": result.completion_rate(),
    }
    
    # Convert to strings for hashing
    prompt_text = json.dumps(plan_inputs, sort_keys=True)
    output_text = json.dumps(plan_outputs, sort_keys=True)
    
    # Estimate tokens (rough estimate)
    prompt_tokens = len(prompt_text.split())
    output_tokens = len(output_text.split())
    total_tokens = prompt_tokens + output_tokens
    
    # Determine task criticality (use highest from plan steps)
    task_criticality = TaskCriticality.ROUTINE
    if plan.steps:
        step_criticalities = [map_role_to_criticality(step.role) for step in plan.steps]
        # Use highest criticality
        if TaskCriticality.CRITICAL in step_criticalities:
            task_criticality = TaskCriticality.CRITICAL
        elif TaskCriticality.IMPORTANT in step_criticalities:
            task_criticality = TaskCriticality.IMPORTANT
    
    # Determine κ threshold from task criticality
    kappa_threshold = {
        TaskCriticality.CRITICAL: 0.95,
        TaskCriticality.IMPORTANT: 0.85,
        TaskCriticality.ROUTINE: 0.70,
        TaskCriticality.LOW_STAKES: 0.60,
    }.get(task_criticality, 0.70)
    
    # Check κ-gate
    kappa_gate_passed = confidence >= kappa_threshold
    
    # Create VIF witness
    vif = VIF(
        model_id=kwargs.pop("model_id", "apoe-executor-v1"),
        model_provider=kwargs.pop("model_provider", "aether"),
        context_snapshot_id=context_snapshot_id,
        prompt_hash=VIF.hash_text(prompt_text),
        prompt_tokens=prompt_tokens,
        confidence_score=confidence,
        confidence_band=determine_band(confidence),
        output_hash=VIF.hash_text(output_text),
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        task_criticality=task_criticality,
        kappa_threshold=kappa_threshold,
        kappa_gate_passed=kappa_gate_passed,
        execution_time_ms=result.total_duration_seconds * 1000.0,
        tool_ids=["apoe.execute_plan"],
        tool_parameters={
            "plan_name": plan.name,
            "roles": list(plan.roles.keys()),
            "steps_count": len(plan.steps),
            "completion_rate": result.completion_rate(),
            "plan_structure": {
                "steps": len(plan.steps),
                "roles": len(plan.roles),
                "gates": len(getattr(plan, 'gates', [])),
                "dependencies": len(getattr(plan, 'dependencies', [])),
            }
        },
        **kwargs  # Remaining kwargs
    )
    
    return vif


# NL_TAG: VIF-INTEG-001 | Create VIF witness for complete plan execution. | create_plan_witness(plan, result, confidence) | []
# NL_TAG_INTENT: VIF-INTENT-001 | Design decision: confidence | create_plan_witness | [ADR-TBD]
def create_plan_witness(
    plan: ExecutionPlan,
    result: ExecutionResult,
    confidence: float = 0.95
) -> Dict[str, Any]:
    """
    Create VIF witness for complete plan execution (legacy dictionary format).
    
    Args:
        plan: Executed plan
        result: Execution result
        confidence: Confidence in execution (0.0-1.0)
        
    Returns:
        VIF witness dictionary
        
    Note:
        This is a legacy function. Use create_plan_witness_vif for full VIF objects.
    """
    return {
        "operation": f"execute_plan:{plan.name}",
        "timestamp": datetime.utcnow().isoformat(),
        "inputs": {
            "plan_name": plan.name,
            "total_steps": result.total_steps,
            "roles": list(plan.roles.keys())
        },
        "outputs": {
            "completed_steps": result.completed_steps,
            "failed_steps": result.failed_steps,
            "success": result.success,
            "duration_seconds": result.total_duration_seconds
        },
        "confidence": confidence,
        "model_id": "apoe-executor-v1",
        "model_provider": "aether",
        "metadata": {
            "completion_rate": result.completion_rate(),
            "plan_structure": {
                "steps": len(plan.steps),
                "roles": len(plan.roles),
                "gates": len(getattr(plan, 'gates', [])),
                "dependencies": len(getattr(plan, 'dependencies', [])),
            }
        }
    }


# NL_TAG: VIF-INTEG-006 | Create full VIF witness object for step execution. | create_step_witness_vif(step, plan_name, context_snapshot_id, confidence) | []
# NL_TAG_CONNECT: VIF-CMC-003 | Step witness stored in CMC | create_step_witness_vif → store_witness_in_cmc | [VIF-INTEG-006, CMC-STORE-001]
# NL_TAG_INTENT: VIF-INTENT-005 | Design decision: full VIF objects for step provenance | create_step_witness_vif | [ADR-VIF-APOE]
def create_step_witness_vif(
    step: Step,
    plan_name: str,
    context_snapshot_id: str,
    confidence: Optional[float] = None,
    parent_vif_id: Optional[str] = None,
    **kwargs
) -> VIF:
    """
    Create full VIF witness object for step execution.
    
    Args:
        step: Executed step
        plan_name: Name of parent plan
        context_snapshot_id: CMC snapshot ID
        confidence: Confidence in step execution (if None, extracted from outputs)
        parent_vif_id: Optional parent witness ID (for witness chains)
        **kwargs: Additional VIF fields
        
    Returns:
        VIF witness object
        
    Examples:
        >>> vif = create_step_witness_vif(step, "plan_1", "snap_123", 0.95)
        >>> assert isinstance(vif, VIF)
        >>> assert vif.confidence_score == 0.95
    """
    if not VIF_AVAILABLE:
        raise ImportError("VIF package not available - cannot create VIF witness")
    
    # Extract confidence from outputs if not provided
    if confidence is None and step.outputs:
        confidence = step.outputs.get("confidence", 0.95)
    elif confidence is None:
        confidence = 0.95  # Default
    
    # Prepare step inputs and outputs
    step_inputs = {
        "step_name": step.name,
        "step_id": step.id,
        "role": step.role.value if step.role else None,
        "role_name": step.role_name,
        "description": step.description,
        "budget": {
            "tokens_limit": step.budget.tokens_limit if step.budget else None,
            "time_limit": step.budget.time_limit_seconds if step.budget else None,
        } if step.budget else None,
    }
    step_outputs = step.outputs or {}
    
    # Convert to strings for hashing
    prompt_text = json.dumps(step_inputs, sort_keys=True)
    output_text = json.dumps(step_outputs, sort_keys=True)
    
    # Estimate tokens (rough estimate)
    prompt_tokens = len(prompt_text.split())
    output_tokens = len(output_text.split())
    total_tokens = prompt_tokens + output_tokens
    
    # Map role to task criticality
    task_criticality = map_role_to_criticality(step.role) if step.role else TaskCriticality.ROUTINE
    
    # Determine κ threshold from task criticality or step.min_confidence
    if step.min_confidence is not None:
        kappa_threshold = step.min_confidence
    else:
        kappa_threshold = {
            TaskCriticality.CRITICAL: 0.95,
            TaskCriticality.IMPORTANT: 0.85,
            TaskCriticality.ROUTINE: 0.70,
            TaskCriticality.LOW_STAKES: 0.60,
        }.get(task_criticality, 0.70)
    
    # Check κ-gate
    kappa_gate_passed = confidence >= kappa_threshold
    
    # Calculate execution time
    execution_time_ms = 0.0
    if step.started_at and step.completed_at:
        duration = (step.completed_at - step.started_at).total_seconds()
        execution_time_ms = duration * 1000.0
    elif step.duration():
        execution_time_ms = step.duration() * 1000.0
    
    # Get tool IDs from step metadata or role
    tool_ids = kwargs.pop("tool_ids", [])
    if not tool_ids:
        tool_ids = [f"apoe.execute_step.{step.role.value}" if step.role else "apoe.execute_step"]
    
    # Create VIF witness
    vif = VIF(
        model_id=kwargs.pop("model_id", step.role.value if step.role else "apoe-executor-v1"),
        model_provider=kwargs.pop("model_provider", "apoe"),
        context_snapshot_id=context_snapshot_id,
        prompt_hash=VIF.hash_text(prompt_text),
        prompt_tokens=prompt_tokens,
        confidence_score=confidence,
        confidence_band=determine_band(confidence),
        output_hash=VIF.hash_text(output_text),
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        task_criticality=task_criticality,
        kappa_threshold=kappa_threshold,
        kappa_gate_passed=kappa_gate_passed,
        execution_time_ms=execution_time_ms,
        parent_vif_id=parent_vif_id,
        tool_ids=tool_ids,
        tool_parameters={
            "step_name": step.name,
            "step_id": step.id,
            "role": step.role.value if step.role else None,
            "plan_name": plan_name,
            "status": step.status.value if step.status else None,
            "duration_seconds": step.duration(),
            "gates_count": len(step.gates) if step.gates else 0,
            "error": step.error,
        },
        **kwargs  # Remaining kwargs
    )
    
    return vif


# NL_TAG: VIF-INTEG-007 | Store VIF witness in CMC. | store_witness_in_cmc(vif, operation_name, prompt, output) | []
# NL_TAG_CONNECT: VIF-CMC-004 | Witness stored in CMC via VIFStore | store_witness_in_cmc → VIFStore.store_witness | [VIF-INTEG-007, CMC-STORE-001]
# NL_TAG_INTENT: VIF-INTENT-006 | Design decision: CMC storage for persistence | store_witness_in_cmc | [ADR-VIF-CMC]
def store_witness_in_cmc(
    vif: VIF,
    operation_name: str,
    prompt: str,
    output: str,
    correlation_id: Optional[str] = None,
) -> Tuple[VIF, str]:
    """
    Store VIF witness in CMC.
    
    Args:
        vif: VIF witness object
        operation_name: Name of operation
        prompt: Prompt text (for context)
        output: Output text (for context)
        correlation_id: Optional correlation ID for tracking
        
    Returns:
        (vif_witness, cmc_atom_id)
        
    Examples:
        >>> vif, atom_id = store_witness_in_cmc(vif, "execute_step", "prompt", "output")
        >>> assert atom_id is not None
    """
    if not VIF_AVAILABLE:
        raise ImportError("VIF package not available - cannot store witness")
    
    try:
        # Get CMC store
        cmc_store = get_memory_store()
        
        # Create VIFStore
        vif_store = VIFStore(cmc_store)
        
        # Store witness
        atom_id = vif_store.store_witness(vif, correlation_id=correlation_id)
        
        return vif, atom_id
    except Exception as e:
        # If CMC not available, log warning but return witness without storage
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to store VIF witness in CMC: {e}")
        return vif, None


# NL_TAG: VIF-INTEG-002 | Create VIF witness for individual step execution. | create_step_witness(step, plan_name, confidence) | []
# NL_TAG_INTENT: VIF-INTENT-002 | Design decision: confidence | create_step_witness | [ADR-TBD]
def create_step_witness(
    step: Step,
    plan_name: str,
    confidence: Optional[float] = None
) -> Dict[str, Any]:
    """
    Create VIF witness for individual step execution (legacy dictionary format).
    
    Args:
        step: Executed step
        plan_name: Name of parent plan
        confidence: Confidence in step execution
        
    Returns:
        VIF witness dictionary
        
    Note:
        This is a legacy function. Use create_step_witness_vif for full VIF objects.
    """
    # Extract confidence from outputs if not provided
    if confidence is None and step.outputs:
        confidence = step.outputs.get("confidence", 0.95)
    elif confidence is None:
        confidence = 0.95  # Default
    
    return {
        "operation": f"execute_step:{plan_name}.{step.name}",
        "timestamp": (step.started_at or datetime.utcnow()).isoformat(),
        "inputs": {
            "step_name": step.name,
            "role": step.role.value if step.role else None,
            "description": step.description,
            "budget": {
                "tokens_limit": step.budget.tokens_limit if step.budget else None,
                "time_limit": step.budget.time_limit_seconds if step.budget else None
            } if step.budget else None
        },
        "outputs": step.outputs or {},
        "confidence": confidence,
        "model_id": step.role.value if step.role else "apoe-executor-v1",
        "model_provider": "apoe",
        "metadata": {
            "status": step.status.value if step.status else None,
            "duration_seconds": step.duration(),
            "gates_count": len(step.gates) if step.gates else 0,
            "error": step.error
        }
    }


# NL_TAG: VIF-INTEG-003 | Create complete witness set for plan execution. | create_witnesses_for_plan(plan, result) | []
def create_witnesses_for_plan(
    plan: ExecutionPlan,
    result: ExecutionResult
) -> Dict[str, Any]:
    """
    Create complete witness set for plan execution.
    
    Includes one witness for the plan and one for each executed step.
    
    Args:
        plan: Executed plan
        result: Execution result
        
    Returns:
        Dictionary with plan_witness and step_witnesses
    """
    # Plan-level witness
    plan_witness = create_plan_witness(plan, result)
    
    # Step-level witnesses
    step_witnesses = []
    for step in plan.steps:
        if step.status != "pending":  # Only for executed steps
            witness = create_step_witness(step, plan.name)
            step_witnesses.append(witness)
    
    return {
        "plan_witness": plan_witness,
        "step_witnesses": step_witnesses,
        "witness_count": 1 + len(step_witnesses)
    }

