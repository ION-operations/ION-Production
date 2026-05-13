"""SEG Integration for APOE Execution Traces

Stores APOE execution traces in SEG (Shared Evidence Graph) for:
- Execution trace storage (plan + step level)
- Plan effectiveness tracking
- DEPP evidence gathering
- Synthesis integration
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import logging

from .models import Step, StepStatus
from .executor import ExecutionResult
from .acl_parser import ExecutionPlan

logger = logging.getLogger(__name__)

# SEG imports (optional)
try:
    from packages.seg.seg_graph import SEGraph
    from packages.seg.models import Evidence, Relation, RelationType
    SEG_AVAILABLE = True
except ImportError:
    SEG_AVAILABLE = False
    SEGraph = None
    Evidence = None
    Relation = None
    RelationType = None


class APOESEGIntegration:
    """Integrates APOE execution traces with SEG.
    
    Stores execution traces as Evidence nodes with proper relations
    for time-travel queries and provenance tracing.
    """
    
    def __init__(self, seg_graph: Optional[SEGraph] = None):
        """
        Initialize SEG integration.
        
        Args:
            seg_graph: SEG graph instance (optional, will create if None)
        """
        # Explicit dependency injection: if no graph is provided, run disabled.
        self.seg = seg_graph
        self.seg_available = self.seg is not None
        if not self.seg_available:
            logger.warning("SEG not available - execution traces will not be stored")

    def _store_evidence(self, evidence: Evidence) -> Optional[str]:
        """Store evidence using either legacy create_* or current add_* API."""
        if not self.seg:
            return None
        if hasattr(self.seg, "create_evidence"):
            evidence_id = self.seg.create_evidence(evidence)
            if isinstance(evidence_id, str):
                evidence.id = evidence_id
                return evidence_id
        if hasattr(self.seg, "add_evidence"):
            stored = self.seg.add_evidence(evidence)
            return stored.id if hasattr(stored, "id") else evidence.id
        return None

    def _store_relation(self, relation: Relation) -> Optional[str]:
        """Store relation using whichever SEG API is available."""
        if not self.seg:
            return None
        if hasattr(self.seg, "add_relation"):
            stored = self.seg.add_relation(relation)
            return stored.id if hasattr(stored, "id") else getattr(relation, "id", None)
        if hasattr(self.seg, "create_relation"):
            relation_id = self.seg.create_relation(relation)
            if isinstance(relation_id, str):
                relation.id = relation_id
                return relation_id
        return None
    
    def store_execution_trace(
        self,
        plan: ExecutionPlan,
        result: ExecutionResult,
        execution_id: str,
        vif_witness_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Store complete execution trace in SEG.
        
        Args:
            plan: Executed plan
            result: Execution result
            execution_id: Unique execution identifier
            vif_witness_id: VIF witness ID for plan execution (optional)
            
        Returns:
            Dictionary with evidence IDs and relations
        """
        if not self.seg_available or not self.seg:
            return None
        
        try:
            # Create plan execution evidence
            plan_evidence = self._create_plan_evidence(
                plan=plan,
                result=result,
                execution_id=execution_id,
                vif_witness_id=vif_witness_id
            )
            plan_evidence_id = self._store_evidence(plan_evidence)
            if not plan_evidence_id:
                return None
            
            # Create step execution evidence nodes
            step_evidence_ids = {}
            step_relations = []
            
            for step in plan.steps:
                if step.status != StepStatus.PENDING:
                    # Create step evidence
                    step_evidence = self._create_step_evidence(
                        step=step,
                        plan_name=plan.name,
                        execution_id=execution_id,
                        vif_witness_id=step.metadata.get("vif_witness_id") if step.metadata else None
                    )
                    step_evidence_id = self._store_evidence(step_evidence)
                    if not step_evidence_id:
                        continue
                    step_evidence_ids[step.id] = step_evidence_id
                    
                    # Link step to plan via DERIVES_FROM
                    step_relation = Relation(
                        source_id=plan_evidence_id,
                        target_id=step_evidence_id,
                        relation_type=RelationType.DERIVES_FROM,
                        confidence=1.0,
                        source="apoe.execution",
                        tags=["apoe", "plan_step_link"]
                    )
                    relation_id = self._store_relation(step_relation)
                    if relation_id:
                        step_relations.append(step_relation)
                    
                    # Link step dependencies
                    if hasattr(plan, 'dependencies') and plan.dependencies:
                        for dep_step_id in plan.dependencies.get(step.id, []):
                            if dep_step_id in step_evidence_ids:
                                dep_relation = Relation(
                                    source_id=step_evidence.id,
                                    target_id=step_evidence_ids[dep_step_id],
                                    relation_type=RelationType.DERIVES_FROM,
                                    confidence=1.0,
                                    source="apoe.execution",
                                    tags=["apoe", "step_dependency"]
                                )
                                relation_id = self._store_relation(dep_relation)
                                if relation_id:
                                    step_relations.append(dep_relation)
            
            return {
                "plan_evidence_id": plan_evidence_id,
                "step_evidence_ids": step_evidence_ids,
                "relations": [r.id for r in step_relations],
                "execution_id": execution_id
            }
        except Exception as e:
            logger.error(f"Failed to store execution trace in SEG: {e}", exc_info=True)
            return None
    
    def store_plan_effectiveness(
        self,
        plan_name: str,
        execution_id: str,
        effectiveness_score: float,
        metrics: Dict[str, Any],
        plan_evidence_id: Optional[str] = None
    ) -> Optional[str]:
        """Store plan effectiveness as Evidence node.
        
        Args:
            plan_name: Name of plan
            execution_id: Execution identifier
            effectiveness_score: Effectiveness score (0.0-1.0)
            metrics: Effectiveness metrics dictionary
            plan_evidence_id: Link to plan execution evidence (optional)
            
        Returns:
            Evidence ID or None if failed
        """
        if not self.seg_available or not self.seg:
            return None
        
        try:
            effectiveness_evidence = Evidence(
                content=f"Plan Effectiveness: {plan_name} - Score: {effectiveness_score:.3f}",
                source=f"apoe.effectiveness:{execution_id}",
                evidence_type="apoe_plan_effectiveness",
                confidence=effectiveness_score,
                reliability=0.9,  # High reliability for computed metrics
                metadata={
                    "plan_name": plan_name,
                    "execution_id": execution_id,
                    "effectiveness_score": effectiveness_score,
                    "metrics": metrics,
                    "computed_at": datetime.now(timezone.utc).isoformat()
                },
                tags=["apoe", "plan_effectiveness", plan_name]
            )
            
            if hasattr(self.seg, "add_evidence"):
                self.seg.add_evidence(effectiveness_evidence)
                effectiveness_id = effectiveness_evidence.id
            else:
                effectiveness_id = self._store_evidence(effectiveness_evidence)
                if not effectiveness_id:
                    return None
            
            # Link to plan execution if provided
            if plan_evidence_id:
                relation = Relation(
                    source_id=plan_evidence_id,
                    target_id=effectiveness_id,
                    relation_type=RelationType.SUPPORTS,
                    confidence=1.0,
                    source="apoe.execution",
                    tags=["apoe", "effectiveness_link"]
                )
                self._store_relation(relation)
            
            return effectiveness_id
        except Exception as e:
            logger.error(f"Failed to store plan effectiveness in SEG: {e}", exc_info=True)
            return None
    
    def query_execution_traces(
        self,
        plan_name: Optional[str] = None,
        execution_id: Optional[str] = None,
        as_of: Optional[datetime] = None
    ) -> List[Evidence]:
        """Query execution traces from SEG.
        
        Args:
            plan_name: Filter by plan name (optional)
            execution_id: Filter by execution ID (optional)
            as_of: Time-travel query (optional)
            
        Returns:
            List of Evidence nodes
        """
        if not self.seg_available or not self.seg:
            return []
        
        try:
            # Get all APOE evidence
            all_evidence = self.seg.list_evidence(as_of=as_of)
            
            # Filter by APOE tags
            apoe_evidence = [
                e for e in all_evidence
                if "apoe" in e.tags
            ]
            
            # Filter by plan name if provided
            if plan_name:
                apoe_evidence = [
                    e for e in apoe_evidence
                    if plan_name in e.tags or e.metadata.get("plan_name") == plan_name
                ]
            
            # Filter by execution ID if provided
            if execution_id:
                apoe_evidence = [
                    e for e in apoe_evidence
                    if e.metadata.get("execution_id") == execution_id
                ]
            
            return apoe_evidence
        except Exception as e:
            logger.error(f"Failed to query execution traces from SEG: {e}", exc_info=True)
            return []
    
    def compute_plan_effectiveness(
        self,
        plan: ExecutionPlan,
        result: ExecutionResult,
        execution_id: str
    ) -> Dict[str, Any]:
        """Compute plan effectiveness metrics.
        
        Args:
            plan: Executed plan
            result: Execution result
            execution_id: Execution identifier
            
        Returns:
            Dictionary with effectiveness metrics
        """
        # Compute basic metrics
        completion_rate = result.completion_rate()
        success_rate = 1.0 if result.success else 0.0
        average_duration = result.total_duration_seconds / result.total_steps if result.total_steps > 0 else 0.0
        
        # Budget efficiency (placeholder - would need actual budget tracking)
        budget_efficiency = 0.85  # Default
        
        # Gate pass rate (placeholder - would need gate tracking)
        gate_pass_rate = 1.0 if result.success else 0.0
        
        # Error rate
        error_rate = result.failed_steps / result.total_steps if result.total_steps > 0 else 0.0
        
        # Overall effectiveness score (weighted average)
        effectiveness_score = (
            0.30 * completion_rate +
            0.30 * success_rate +
            0.20 * (1.0 - error_rate) +
            0.10 * budget_efficiency +
            0.10 * gate_pass_rate
        )
        
        metrics = {
            "completion_rate": completion_rate,
            "success_rate": success_rate,
            "average_duration": average_duration,
            "budget_efficiency": budget_efficiency,
            "gate_pass_rate": gate_pass_rate,
            "error_rate": error_rate
        }
        
        # Store effectiveness in SEG
        effectiveness_id = self.store_plan_effectiveness(
            plan_name=plan.name,
            execution_id=execution_id,
            effectiveness_score=effectiveness_score,
            metrics=metrics
        )
        
        return {
            "effectiveness_score": effectiveness_score,
            "metrics": metrics,
            "effectiveness_id": effectiveness_id
        }
    
    def _create_plan_evidence(
        self,
        plan: ExecutionPlan,
        result: ExecutionResult,
        execution_id: str,
        vif_witness_id: Optional[str] = None
    ) -> Evidence:
        """Create Evidence node for plan execution.
        
        Args:
            plan: Executed plan
            result: Execution result
            execution_id: Execution identifier
            vif_witness_id: VIF witness ID (optional)
            
        Returns:
            Evidence node
        """
        started_at = datetime.now(timezone.utc)  # TODO: Get actual start time from result
        completed_at = datetime.now(timezone.utc)  # TODO: Get actual completion time from result
        
        return Evidence(
            content=f"APOE Plan Execution: {plan.name}",
            source=f"apoe.execution:{execution_id}",
            evidence_type="apoe_plan_execution",
            confidence=1.0 if result.success else 0.5,
            metadata={
                "plan_id": plan.name,  # Use plan name as ID
                "plan_name": plan.name,
                "execution_id": execution_id,
                "started_at": started_at.isoformat(),
                "completed_at": completed_at.isoformat(),
                "total_steps": result.total_steps,
                "completed_steps": result.completed_steps,
                "failed_steps": result.failed_steps,
                "success": result.success,
                "total_duration_seconds": result.total_duration_seconds,
                "plan_structure": {
                    "roles": list(plan.roles.keys()),
                    "dependencies": len(plan.dependencies) if hasattr(plan, 'dependencies') else 0,
                    "gates": len(plan.gates) if hasattr(plan, 'gates') else 0
                }
            },
            tags=["apoe", "plan_execution", plan.name],
            witness_id=vif_witness_id
        )
    
    def _create_step_evidence(
        self,
        step: Step,
        plan_name: str,
        execution_id: str,
        vif_witness_id: Optional[str] = None
    ) -> Evidence:
        """Create Evidence node for step execution.
        
        Args:
            step: Executed step
            plan_name: Name of parent plan
            execution_id: Execution identifier
            vif_witness_id: VIF witness ID (optional)
            
        Returns:
            Evidence node
        """
        started_at = step.started_at or datetime.now(timezone.utc)
        completed_at = step.completed_at or datetime.now(timezone.utc)
        duration_seconds = step.duration() if step.duration() else 0.0
        
        return Evidence(
            content=f"APOE Step Execution: {step.name}",
            source=f"apoe.step:{step.id}",
            evidence_type="apoe_step_execution",
            confidence=1.0 if step.status == StepStatus.COMPLETED else 0.3,
            metadata={
                "step_id": step.id,
                "step_name": step.name,
                "role": step.role.value if hasattr(step.role, 'value') else str(step.role),
                "role_name": step.role_name,
                "status": step.status.value if hasattr(step.status, 'value') else str(step.status),
                "started_at": started_at.isoformat() if isinstance(started_at, datetime) else str(started_at),
                "completed_at": completed_at.isoformat() if isinstance(completed_at, datetime) else str(completed_at),
                "duration_seconds": duration_seconds,
                "inputs": {"description": step.description} if step.description else {},
                "outputs": step.outputs or {},
                "budget_consumed": {
                    "tokens": step.budget.tokens_limit if step.budget else None,
                    "time": step.budget.time_limit_seconds if step.budget else None
                } if step.budget else None,
                "gates_evaluated": len(step.gates),
                "error": step.error
            },
            tags=["apoe", "step_execution", step.role.value if hasattr(step.role, 'value') else str(step.role), step.status.value if hasattr(step.status, 'value') else str(step.status)],
            witness_id=vif_witness_id
        )

