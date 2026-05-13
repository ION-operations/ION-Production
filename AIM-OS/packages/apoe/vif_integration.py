"""VIF Integration for APOE

Creates VIF witnesses for APOE operations (plan execution, step execution).
Uses full VIF schema with automatic CMC storage.
"""

from __future__ import annotations
from datetime import UTC, datetime
from typing import Dict, Any, Optional, Tuple, List
import hashlib

from .models import Step, RoleType
from .executor import ExecutionResult
from .acl_parser import ExecutionPlan

# VIF imports
try:
    from packages.vif.witness import VIF, ConfidenceBand, TaskCriticality
    from packages.vif.confidence_bands import determine_band
    from packages.vif.cmc_integration import create_witness_and_store
    from packages.vif.kappa_gate import DEFAULT_KAPPA_THRESHOLDS
    VIF_AVAILABLE = True
except ImportError:
    # Fallback for environments without VIF
    VIF_AVAILABLE = False
    VIF = None
    ConfidenceBand = None
    TaskCriticality = None
    determine_band = None
    create_witness_and_store = None
    DEFAULT_KAPPA_THRESHOLDS = None


def create_plan_witness(
    plan: ExecutionPlan,
    result: ExecutionResult,
    confidence: float = 0.95
) -> Dict[str, Any]:
    """
    Create VIF witness for complete plan execution.
    
    Args:
        plan: Executed plan
        result: Execution result
        confidence: Confidence in execution (0.0-1.0)
        
    Returns:
        VIF witness dictionary
    """
    return {
        "operation": f"execute_plan:{plan.name}",
        "timestamp": datetime.now(UTC).isoformat(),
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
                "gates": len(plan.gates),
                "dependencies": len(plan.dependencies)
            }
        }
    }


def create_step_witness(
    step: Step,
    plan_name: str,
    confidence: Optional[float] = None
) -> Dict[str, Any]:
    """
    Create VIF witness for individual step execution.
    
    Args:
        step: Executed step
        plan_name: Name of parent plan
        confidence: Confidence in step execution
        
    Returns:
        VIF witness dictionary
    """
    # Extract confidence from outputs if not provided
    if confidence is None and step.outputs:
        confidence = step.outputs.get("confidence", 0.95)
    elif confidence is None:
        confidence = 0.95  # Default
    
    return {
        "operation": f"execute_step:{plan_name}.{step.name}",
        "timestamp": (step.started_at or datetime.now(UTC)).isoformat(),
        "inputs": {
            "step_name": step.name,
            "role": step.role.value,
            "description": step.description,
            "budget": {
                "tokens_limit": step.budget.tokens_limit if step.budget else None,
                "time_limit": step.budget.time_limit_seconds if step.budget else None
            } if step.budget else None
        },
        "outputs": step.outputs or {},
        "confidence": confidence,
        "model_id": step.role.value,
        "model_provider": "apoe",
        "metadata": {
            "status": step.status.value,
            "duration_seconds": step.duration(),
            "gates_count": len(step.gates),
            "error": step.error
        }
    }


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


# ============================================================================
# NEW VIF INTEGRATION (Full Schema + CMC Storage)
# ============================================================================

def map_role_to_criticality(role: RoleType) -> TaskCriticality:
    """Map APOE role to task criticality level for κ-gating.
    
    Args:
        role: APOE role type
        
    Returns:
        Task criticality level
    """
    if not VIF_AVAILABLE:
        raise ImportError("VIF package not available")
    
    role_criticality_map = {
        RoleType.PLANNER: TaskCriticality.IMPORTANT,      # κ=0.85
        RoleType.RETRIEVER: TaskCriticality.ROUTINE,      # κ=0.70
        RoleType.REASONER: TaskCriticality.IMPORTANT,     # κ=0.85
        RoleType.VERIFIER: TaskCriticality.CRITICAL,      # κ=0.95
        RoleType.BUILDER: TaskCriticality.ROUTINE,         # κ=0.70
        RoleType.CRITIC: TaskCriticality.IMPORTANT,       # κ=0.85
        RoleType.OPERATOR: TaskCriticality.ROUTINE,       # κ=0.70
        RoleType.WITNESS: TaskCriticality.CRITICAL,       # κ=0.95
    }
    return role_criticality_map.get(role, TaskCriticality.ROUTINE)


def get_kappa_threshold_for_role(role: RoleType) -> float:
    """Get κ threshold for APOE role.
    
    Args:
        role: APOE role type
        
    Returns:
        κ threshold (0.0-1.0)
    """
    if not VIF_AVAILABLE:
        raise ImportError("VIF package not available")
    
    criticality = map_role_to_criticality(role)
    return DEFAULT_KAPPA_THRESHOLDS[criticality]


def create_step_witness_vif(
    step: Step,
    plan_name: str,
    context_snapshot_id: str,
    confidence: Optional[float] = None
) -> VIF:
    """Create full VIF witness for step execution using VIF schema.
    
    Args:
        step: Executed step
        plan_name: Name of parent plan
        context_snapshot_id: CMC snapshot ID
        confidence: Confidence in step execution (extracted from outputs if None)
        
    Returns:
        VIF witness object
    """
    if not VIF_AVAILABLE:
        raise ImportError("VIF package not available")
    
    # Extract confidence
    if confidence is None and step.outputs:
        confidence = step.outputs.get("confidence", 0.95)
    elif confidence is None:
        confidence = 0.95
    
    # Hash prompt and output
    prompt_text = step.description or ""
    output_text = str(step.outputs or {})
    
    prompt_hash = hashlib.sha256(prompt_text.encode()).hexdigest()
    output_hash = hashlib.sha256(output_text.encode()).hexdigest()
    
    # Estimate tokens (simple word count for now)
    prompt_tokens = len(prompt_text.split())
    output_tokens = len(output_text.split())
    
    # Determine task criticality from role
    task_criticality = map_role_to_criticality(step.role)
    kappa_threshold = get_kappa_threshold_for_role(step.role)
    
    # Create VIF witness
    vif = VIF(
        model_id=step.role.value,  # "planner", "reasoner", etc.
        model_provider="apoe",
        context_snapshot_id=context_snapshot_id,
        prompt_hash=prompt_hash,
        prompt_tokens=prompt_tokens,
        confidence_score=confidence,
        confidence_band=determine_band(confidence),
        output_hash=output_hash,
        output_tokens=output_tokens,
        total_tokens=prompt_tokens + output_tokens,
        task_criticality=task_criticality,
        kappa_threshold=kappa_threshold,
        kappa_gate_passed=(confidence >= kappa_threshold),
        execution_time_ms=step.duration() * 1000 if step.duration() else 0.0,
    )
    
    return vif


def create_plan_witness_vif(
    plan: ExecutionPlan,
    result: ExecutionResult,
    context_snapshot_id: str,
    confidence: float = 0.95
) -> VIF:
    """Create full VIF witness for plan execution using VIF schema.
    
    Args:
        plan: Executed plan
        result: Execution result
        context_snapshot_id: CMC snapshot ID
        confidence: Confidence in plan execution
        
    Returns:
        VIF witness object
    """
    if not VIF_AVAILABLE:
        raise ImportError("VIF package not available")
    
    # Hash plan inputs and outputs
    plan_inputs = {
        "plan_name": plan.name,
        "total_steps": result.total_steps,
        "roles": list(plan.roles.keys())
    }
    plan_outputs = {
        "completed_steps": result.completed_steps,
        "failed_steps": result.failed_steps,
        "success": result.success,
        "duration_seconds": result.total_duration_seconds
    }
    
    prompt_text = str(plan_inputs)
    output_text = str(plan_outputs)
    
    prompt_hash = hashlib.sha256(prompt_text.encode()).hexdigest()
    output_hash = hashlib.sha256(output_text.encode()).hexdigest()
    
    prompt_tokens = len(prompt_text.split())
    output_tokens = len(output_text.split())
    
    # Plan execution is ROUTINE by default
    task_criticality = TaskCriticality.ROUTINE
    kappa_threshold = DEFAULT_KAPPA_THRESHOLDS[task_criticality]
    
    vif = VIF(
        model_id="apoe-executor-v1",
        model_provider="aether",
        context_snapshot_id=context_snapshot_id,
        prompt_hash=prompt_hash,
        prompt_tokens=prompt_tokens,
        confidence_score=confidence,
        confidence_band=determine_band(confidence),
        output_hash=output_hash,
        output_tokens=output_tokens,
        total_tokens=prompt_tokens + output_tokens,
        task_criticality=task_criticality,
        kappa_threshold=kappa_threshold,
        kappa_gate_passed=(confidence >= kappa_threshold),
        execution_time_ms=result.total_duration_seconds * 1000 if result.total_duration_seconds else 0.0,
    )
    
    return vif


def store_witness_in_cmc(
    vif: VIF,
    operation_name: str,
    prompt: str,
    output: str,
    integration_tags: Optional[List[str]] = None,
) -> Tuple[VIF, str]:
    """Store VIF witness in CMC automatically.
    
    Args:
        vif: VIF witness object
        operation_name: Name of operation (e.g., "execute_step:plan.step")
        prompt: Prompt text
        output: Output text
        
    Returns:
        Tuple of (vif_witness, cmc_atom_id)
    """
    if not VIF_AVAILABLE:
        raise ImportError("VIF package not available")
    
    try:
        from packages.cmc import get_memory_store
        
        cmc_store = get_memory_store()
        vif, atom_id = create_witness_and_store(
            cmc_store=cmc_store,
            operation_name=operation_name,
            prompt=prompt,
            output=output,
            confidence=vif.confidence_score,
            context_snapshot_id=vif.context_snapshot_id,
            model_id=vif.model_id,
            model_provider=vif.model_provider,
            task_criticality=vif.task_criticality,
            kappa_threshold=vif.kappa_threshold,
            kappa_gate_passed=vif.kappa_gate_passed,
            execution_time_ms=vif.execution_time_ms,
            integration_tags=integration_tags,
        )
        return vif, atom_id
    except Exception as e:
        # Non-blocking: log error but don't fail execution
        import logging
        logging.warning(f"Failed to store VIF witness in CMC: {e}")
        return vif, None

