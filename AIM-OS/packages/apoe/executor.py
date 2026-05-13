"""APOE Execution Engine

Executes ExecutionPlans by running steps in dependency order.
Integrates with VIF for provenance tracking and κ-gating.
"""

from __future__ import annotations
from datetime import UTC, datetime
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import logging

from .models import Step, StepStatus, Budget, Gate, RoleType
from .acl_parser import ExecutionPlan
from .integration_tags import (
    IntegrationTagContext,
    IntegrationSystem,
    build_integration_tags,
    merge_integration_context,
)

# VIF imports (optional)
try:
    from packages.vif.kappa_gate import KappaGate, TaskCriticality
    from packages.apoe.vif_integration import (
        map_role_to_criticality,
        create_step_witness_vif,
        create_plan_witness_vif,
        store_witness_in_cmc,
        VIF_AVAILABLE
    )
    VIF_ENABLED = VIF_AVAILABLE
except ImportError:
    VIF_ENABLED = False
    KappaGate = None
    TaskCriticality = None
    map_role_to_criticality = None
    create_step_witness_vif = None
    create_plan_witness_vif = None
    store_witness_in_cmc = None

# Role dispatcher (optional)
try:
    from packages.apoe.role_dispatcher import RoleDispatcher
    ROLE_DISPATCHER_AVAILABLE = True
except ImportError:
    ROLE_DISPATCHER_AVAILABLE = False
    RoleDispatcher = None

# SEG integration (optional)
try:
    from packages.apoe.seg_integration import APOESEGIntegration
    SEG_AVAILABLE = True
except ImportError:
    SEG_AVAILABLE = False
    APOESEGIntegration = None

# TCS integration (optional)
try:
    from packages.apoe.tcs_integration import APOETCSIntegration
    TCS_AVAILABLE = True
except ImportError:
    TCS_AVAILABLE = False
    APOETCSIntegration = None

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of executing a plan."""
    plan_name: str
    total_steps: int
    completed_steps: int
    failed_steps: int
    skipped_steps: int
    total_duration_seconds: float
    success: bool
    error: Optional[str] = None
    
    def completion_rate(self) -> float:
        """Calculate completion rate (0.0-1.0)."""
        if self.total_steps == 0:
            return 0.0
        return self.completed_steps / self.total_steps


class PlanExecutor:
    """
    Execute ExecutionPlans with dependency resolution and gate validation.
    
    Runs steps in topological order, respecting dependencies,
    tracking budgets, and validating gates.
    
    Integrates with VIF for:
    - κ-gating (confidence-based abstention)
    - Witness generation (provenance tracking)
    - CMC storage (persistent memory)
    """
    
    def __init__(
        self,
        enable_vif: bool = True,
        enable_hhni: bool = True,
        enable_seg: bool = True,
        enable_tcs: bool = True,
        mcp_client: Optional[Any] = None,
        integration_context: Optional[IntegrationTagContext] = None,
    ):
        """
        Initialize executor.
        
        Args:
            enable_vif: Enable VIF integration (κ-gating, witnesses)
            enable_hhni: Enable HHNI integration for Retriever role
            enable_seg: Enable SEG integration for execution traces
            enable_tcs: Enable TCS integration for timeline entries
            mcp_client: Optional MCP client for TCS timeline operations
        """
        self.role_handlers: Dict[str, Callable] = {}
        self.enable_vif = enable_vif and VIF_ENABLED
        self.enable_hhni = enable_hhni and ROLE_DISPATCHER_AVAILABLE
        self.enable_seg = enable_seg and SEG_AVAILABLE
        self.enable_tcs = enable_tcs and TCS_AVAILABLE
        self.integration_context = integration_context or IntegrationTagContext(
            system=IntegrationSystem(name="apoe", priority="p0"),
            integration_type="plan_execution",
            connection="chat->apoe",
            modality="text+code",
            action="plan_execution",
            extras=["chat_ide"],
        )
        
        # Initialize κ-gate if VIF enabled
        if self.enable_vif:
            self.kappa_gate = KappaGate()
        else:
            self.kappa_gate = None
        
        # Initialize role dispatcher if HHNI enabled
        if self.enable_hhni and RoleDispatcher:
            self.role_dispatcher = RoleDispatcher(enable_hhni=enable_hhni)
        else:
            self.role_dispatcher = None
        
        # Initialize SEG integration if enabled
        if self.enable_seg and APOESEGIntegration:
            self.seg_integration = APOESEGIntegration()
        else:
            self.seg_integration = None
        
        # Initialize TCS integration if enabled
        if self.enable_tcs and APOETCSIntegration:
            self.tcs_integration = APOETCSIntegration(mcp_client=mcp_client)
        else:
            self.tcs_integration = None

    def _resolve_integration_context(
        self,
        override: Optional[IntegrationTagContext] = None,
    ) -> IntegrationTagContext:
        """Merge executor-level integration context with overrides."""
        return merge_integration_context(self.integration_context, override)

    def register_role_handler(
        self,
        role_name: str,
        handler: Callable[[str, Dict], Dict[str, Any]]
    ):
        """
        Register a handler function for a role.
        
        Args:
            role_name: Name of role (from plan.roles)
            handler: Function(description, params) -> outputs
        """
        self.role_handlers[role_name] = handler
    
    def execute(self, plan: ExecutionPlan) -> ExecutionResult:
        """
        Execute a plan to completion (or failure).
        
        Args:
            plan: ExecutionPlan to execute
            
        Returns:
            ExecutionResult with metrics
        """
        start_time = datetime.now(UTC)
        execution_id = f"{plan.name}_{start_time.isoformat()}"
        completed = 0
        failed = 0
        skipped = 0
        
        # Create plan start timeline entry if TCS enabled
        if self.enable_tcs and self.tcs_integration:
            self.tcs_integration.create_plan_start_entry(plan, execution_id)
        
        # Execute until no more ready steps
        while True:
            ready_steps = plan.get_ready_steps()
            
            if not ready_steps:
                # No more ready steps - either done or blocked
                break
            
            # Execute each ready step
            for step in ready_steps:
                result = self._execute_step(step, plan, execution_id)
                
                if result == "completed":
                    completed += 1
                elif result == "failed":
                    failed += 1
                    # Fail fast - stop on error
                    break
                elif result == "skipped":
                    skipped += 1
            
            # If any step failed, abort execution
            if failed > 0:
                break
        
        end_time = datetime.now(UTC)
        duration = (end_time - start_time).total_seconds()
        
        # Check if all steps completed successfully
        success = (completed == len(plan.steps) and failed == 0)
        error = None if success else "Execution failed or incomplete"
        
        result = ExecutionResult(
            plan_name=plan.name,
            total_steps=len(plan.steps),
            completed_steps=completed,
            failed_steps=failed,
            skipped_steps=skipped,
            total_duration_seconds=duration,
            success=success,
            error=error
        )
        
        # Create plan-level VIF witness if enabled
        if self.enable_vif:
            self._create_plan_witness(plan, result)
        
        # Store execution trace in SEG if enabled
        if self.enable_seg and self.seg_integration:
            vif_witness_id = None
            if hasattr(plan, 'metadata') and plan.metadata:
                vif_witness_id = plan.metadata.get("vif_witness_id")
            
            trace_result = self.seg_integration.store_execution_trace(
                plan=plan,
                result=result,
                execution_id=execution_id,
                vif_witness_id=vif_witness_id
            )
            
            # Compute and store plan effectiveness
            effectiveness_result = self.seg_integration.compute_plan_effectiveness(
                plan=plan,
                result=result,
                execution_id=execution_id
            )
            
            # Store trace and effectiveness results in plan metadata
            if not hasattr(plan, 'metadata') or plan.metadata is None:
                plan.metadata = {}
            plan.metadata["seg_trace"] = trace_result
            plan.metadata["effectiveness"] = effectiveness_result
        
        # Create plan complete timeline entry if TCS enabled
        if self.enable_tcs and self.tcs_integration:
            self.tcs_integration.create_plan_complete_entry(plan, execution_id, result)
        
        return result
    
    def _execute_step(
        self,
        step: Step,
        plan: ExecutionPlan,
        execution_id: Optional[str] = None
    ) -> str:
        """
        Execute a single step with VIF integration.
        
        Args:
            step: Step to execute
            plan: Execution plan
            execution_id: Execution identifier for correlation
            
        Returns:
            "completed" | "failed" | "skipped" | "abstained"
        """
        if execution_id is None:
            execution_id = f"{plan.name}_adhoc"

        # Mark as running
        step.status = StepStatus.RUNNING
        step.started_at = datetime.now(UTC)
        
        # Create step start timeline entry if TCS enabled
        if self.enable_tcs and self.tcs_integration:
            self.tcs_integration.create_step_start_entry(step, plan.name, execution_id)
        
        # Create context snapshot before execution (for VIF)
        context_snapshot_id = None
        if self.enable_vif:
            context_snapshot_id = self._create_context_snapshot(step, plan)
        
        try:
            # κ-Gate check before execution (if VIF enabled)
            if self.enable_vif and self.kappa_gate:
                gate_result = self._check_kappa_gate(step, plan)
                if not gate_result.passed:
                    # κ-gate failed - abstain
                    step.status = StepStatus.ABSTAINED
                    step.error = gate_result.escalation_reason
                    step.completed_at = datetime.now(UTC)
                    
                    # Create step complete timeline entry if TCS enabled
                    if self.enable_tcs and self.tcs_integration:
                        self.tcs_integration.create_step_complete_entry(step, plan.name, execution_id)
                    
                    # Escalate if needed
                    if gate_result.should_escalate:
                        self._escalate_to_human(step, gate_result)
                    
                    return "abstained"
            
            # Get role handler using step's assigned role_name
            if not step.role_name:
                raise ValueError(f"Step {step.name} has no role assigned")
            
            role_config = plan.roles.get(step.role_name)
            if not role_config:
                raise ValueError(f"Role '{step.role_name}' not defined in plan")
            
            # Execute step via role handler
            # Check if this is a Retriever role and use HHNI if available
            if (step.role == RoleType.RETRIEVER and 
                self.enable_hhni and 
                self.role_dispatcher and 
                self.role_dispatcher.retriever_role):
                # Use HHNI RetrieverRole
                inputs = {
                    "query": step.description or "",
                    **role_config.params  # Include params like k, modality, enable_dvns, etc.
                }
                result = self.role_dispatcher.dispatch_retriever(
                    step=step,
                    inputs=inputs,
                    budget=step.budget
                )
                # Convert HHNI result to standard output format
                outputs = {
                    "context": result.get("context", []),
                    "total_tokens": result.get("total_tokens", 0),
                    "relevance_scores": result.get("relevance_scores", []),
                    "confidence": result.get("metrics", {}).get("relevance_score", 0.85),
                    "modality": result.get("modality", "code"),
                    "k": result.get("k", 0),
                    "dvns_enabled": result.get("dvns_enabled", False),
                    "error": result.get("error")
                }
            elif step.role_name in self.role_handlers:
                handler = self.role_handlers[step.role_name]
                outputs = handler(step.description or "", role_config.params)
            else:
                # Mock execution for testing
                outputs = {"status": "success", "confidence": 0.95}
            
            step.outputs = outputs
            
            # Validate gates
            for gate in step.gates:
                context = {"output": type('obj', (object,), outputs)()}
                gate_passed = gate.evaluate(context)
                
                # Create gate evaluation timeline entry if TCS enabled
                if self.enable_tcs and self.tcs_integration:
                    self.tcs_integration.create_gate_evaluation_entry(
                        gate=gate,
                        step=step,
                        plan_name=plan.name,
                        execution_id=execution_id,
                        passed=gate_passed,
                        context=context
                    )
                
                if not gate_passed:
                    step.status = StepStatus.FAILED
                    step.error = f"Gate '{gate.name}' failed: {gate.condition}"
                    step.completed_at = datetime.now(UTC)
                    
                    # Create error timeline entry if TCS enabled
                    if self.enable_tcs and self.tcs_integration:
                        self.tcs_integration.create_error_entry(
                            error_type="gate_failure",
                            error_message=f"Gate '{gate.name}' failed: {gate.condition}",
                            plan_name=plan.name,
                            execution_id=execution_id,
                            step_id=step.id,
                            context={"gate_id": gate.id, "gate_name": gate.name, "condition": gate.condition}
                        )
                    
                    # Create step complete timeline entry if TCS enabled
                    if self.enable_tcs and self.tcs_integration:
                        self.tcs_integration.create_step_complete_entry(step, plan.name, execution_id)
                    
                    return "failed"
            
            # Success - create VIF witness if enabled
            if self.enable_vif and context_snapshot_id:
                self._create_step_witness(step, plan.name, context_snapshot_id)
            
            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.now(UTC)
            
            # Create step complete timeline entry if TCS enabled
            if self.enable_tcs and self.tcs_integration:
                self.tcs_integration.create_step_complete_entry(step, plan.name, execution_id)
            
            return "completed"
        
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.now(UTC)
            
            # Create error timeline entry if TCS enabled
            if self.enable_tcs and self.tcs_integration:
                self.tcs_integration.create_error_entry(
                    error_type="execution_error",
                    error_message=str(e),
                    plan_name=plan.name,
                    execution_id=execution_id,
                    step_id=step.id,
                    context={"step_name": step.name, "role": step.role.value if step.role else None}
                )
            
            # Create step complete timeline entry if TCS enabled
            if self.enable_tcs and self.tcs_integration:
                self.tcs_integration.create_step_complete_entry(step, plan.name, execution_id)
            
            return "failed"
    
    def _check_kappa_gate(self, step: Step, plan: ExecutionPlan) -> Any:
        """Check κ-gate before step execution.
        
        Args:
            step: Step to check
            plan: Execution plan
            
        Returns:
            KappaGateResult
        """
        if not self.enable_vif or not self.kappa_gate:
            # Return dummy passed result if VIF disabled
            from dataclasses import dataclass
            @dataclass
            class DummyResult:
                passed = True
                should_escalate = False
                escalation_reason = None
            return DummyResult()
        
        # Get custom threshold if provided
        custom_threshold = None
        if hasattr(step, 'min_confidence') and step.min_confidence:
            custom_threshold = step.min_confidence
        
        # Get task criticality from role
        task_criticality = map_role_to_criticality(step.role)
        
        # Predict confidence
        predicted_confidence = self._predict_step_confidence(step, plan)
        
        # Check κ-gate
        gate_result = self.kappa_gate.check(
            confidence=predicted_confidence,
            task_criticality=task_criticality,
            custom_threshold=custom_threshold
        )
        
        return gate_result
    
    def _predict_step_confidence(self, step: Step, plan: ExecutionPlan) -> float:
        """Predict confidence for step execution.
        
        Args:
            step: Step to predict confidence for
            plan: Execution plan
            
        Returns:
            Predicted confidence (0.0-1.0)
        """
        # Use historical confidence if available
        if hasattr(step, 'metadata') and step.metadata and "historical_confidence" in step.metadata:
            return step.metadata["historical_confidence"]
        
        # Use role default confidence
        role_defaults = {
            RoleType.VERIFIER: 0.95,
            RoleType.WITNESS: 0.95,
            RoleType.PLANNER: 0.85,
            RoleType.REASONER: 0.85,
            RoleType.CRITIC: 0.85,
            RoleType.RETRIEVER: 0.70,
            RoleType.BUILDER: 0.70,
            RoleType.OPERATOR: 0.70,
        }
        return role_defaults.get(step.role, 0.70)
    
    def _create_context_snapshot(self, step: Step, plan: ExecutionPlan) -> Optional[str]:
        """Create CMC context snapshot before execution.
        
        Args:
            step: Step being executed
            plan: Execution plan
            
        Returns:
            Snapshot ID or None if CMC unavailable
        """
        if not self.enable_vif:
            return None
        
        try:
            from packages.cmc import get_memory_store
            cmc_store = get_memory_store()
            
            # Create snapshot (if CMC supports it)
            # For now, return a placeholder ID
            # TODO: Implement actual snapshot creation when CMC API is available
            snapshot_id = f"snap_{step.id}_{datetime.now(UTC).isoformat()}"
            return snapshot_id
        except Exception as e:
            logger.warning(f"Failed to create context snapshot: {e}")
            return None
    
    def _create_step_witness(self, step: Step, plan_name: str, context_snapshot_id: str) -> None:
        """Create and store VIF witness for step execution.
        
        Args:
            step: Executed step
            plan_name: Name of parent plan
            context_snapshot_id: CMC snapshot ID
        """
        if not self.enable_vif:
            return
        
        try:
            step_context = self._resolve_integration_context(
                IntegrationTagContext(
                    system=IntegrationSystem(name="vif", priority="critical"),
                    integration_type="witness",
                    connection="apoe->vif",
                    modality="witness",
                    action=f"execute_step:{plan_name}.{step.name}",
                    mode=(step.metadata or {}).get("thinking_mode") if getattr(step, "metadata", None) else None,
                    agent=step.role.value,
                    extras=["step_witness"],
                )
            )
            integration_tags = build_integration_tags(step_context)

            # Create VIF witness
            vif = create_step_witness_vif(
                step=step,
                plan_name=plan_name,
                context_snapshot_id=context_snapshot_id,
                confidence=step.outputs.get("confidence", 0.95) if step.outputs else 0.95
            )
            
            # Store in CMC
            prompt_text = step.description or ""
            output_text = str(step.outputs or {})
            operation_name = f"execute_step:{plan_name}.{step.name}"
            
            vif, atom_id = store_witness_in_cmc(
                vif=vif,
                operation_name=operation_name,
                prompt=prompt_text,
                output=output_text,
                integration_tags=integration_tags,
            )
            
            # Store witness ID in step metadata
            if not hasattr(step, 'metadata') or step.metadata is None:
                step.metadata = {}
            step.metadata["vif_witness_id"] = vif.id
            if atom_id:
                step.metadata["vif_atom_id"] = atom_id
            step.metadata["integration_tags"] = integration_tags
            
        except Exception as e:
            # Non-blocking: log error but don't fail execution
            logger.warning(f"Failed to create VIF witness for step {step.name}: {e}")
    
    def _escalate_to_human(self, step: Step, gate_result: Any) -> None:
        """Escalate step to human review.
        
        Args:
            step: Step that failed κ-gate
            gate_result: κ-gate result
        """
        try:
            from packages.apoe.hitl_escalation import HITLManager
            
            hitl_manager = HITLManager()
            priority = "high" if gate_result.task_criticality in [TaskCriticality.CRITICAL, TaskCriticality.IMPORTANT] else "medium"
            
            hitl_manager.create_escalation(
                step_id=step.id,
                reason=gate_result.escalation_reason,
                priority=priority,
                context={
                    "confidence": gate_result.confidence,
                    "threshold": gate_result.threshold,
                    "gap": gate_result.gap,
                    "task_criticality": gate_result.task_criticality.value if hasattr(gate_result.task_criticality, 'value') else str(gate_result.task_criticality)
                }
            )
        except Exception as e:
            logger.warning(f"Failed to escalate step {step.name} to human: {e}")
    
    def _create_plan_witness(self, plan: ExecutionPlan, result: ExecutionResult) -> None:
        """Create and store VIF witness for plan execution.
        
        Args:
            plan: Executed plan
            result: Execution result
        """
        if not self.enable_vif:
            return
        
        try:
            # Create context snapshot for plan
            context_snapshot_id = None
            try:
                from packages.cmc import get_memory_store
                cmc_store = get_memory_store()
                # TODO: Implement actual snapshot creation when CMC API is available
                context_snapshot_id = f"snap_plan_{plan.name}_{datetime.now(UTC).isoformat()}"
            except Exception as e:
                logger.warning(f"Failed to create plan context snapshot: {e}")
            
            if not context_snapshot_id:
                return
            
            # Calculate plan confidence from step results
            plan_confidence = 0.95 if result.success else 0.70
            
            # Create VIF witness
            vif = create_plan_witness_vif(
                plan=plan,
                result=result,
                context_snapshot_id=context_snapshot_id,
                confidence=plan_confidence
            )

            plan_context = self._resolve_integration_context(
                IntegrationTagContext(
                    system=IntegrationSystem(name="vif", priority="critical"),
                    integration_type="witness",
                    connection="apoe->vif",
                    modality="witness",
                    action=f"execute_plan:{plan.name}",
                    extras=["plan_witness"],
                )
            )
            integration_tags = build_integration_tags(plan_context)
            
            # Store in CMC
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
            operation_name = f"execute_plan:{plan.name}"
            
            vif, atom_id = store_witness_in_cmc(
                vif=vif,
                operation_name=operation_name,
                prompt=prompt_text,
                output=output_text,
                integration_tags=integration_tags,
            )
            
            # Store witness ID in plan metadata (if available)
            if hasattr(plan, 'metadata') and plan.metadata is not None:
                plan.metadata["vif_witness_id"] = vif.id
                if atom_id:
                    plan.metadata["vif_atom_id"] = atom_id
                plan.metadata["integration_tags"] = integration_tags
            
        except Exception as e:
            # Non-blocking: log error but don't fail execution
            logger.warning(f"Failed to create VIF witness for plan {plan.name}: {e}")
    
    def execute_step_with_budget(
        self,
        step: Step,
        plan: ExecutionPlan,
        global_budget: Optional[Budget] = None,
        execution_id: Optional[str] = None
    ) -> str:
        """
        Execute step with budget tracking.
        
        Args:
            step: Step to execute
            plan: Full execution plan
            global_budget: Optional global budget (in addition to step budget)
            execution_id: Optional execution identifier for correlation
            
        Returns:
            "completed" | "failed" | "skipped"
        """
        # Generate execution_id if not provided
        if not execution_id:
            execution_id = f"{plan.name}_{datetime.now(UTC).isoformat()}"
        
        # Check budget before execution
        if global_budget and step.budget:
            if not global_budget.check_tokens(step.budget.tokens_limit):
                step.status = StepStatus.SKIPPED
                step.error = "Insufficient global budget tokens"
                step.completed_at = datetime.now(UTC)
                
                # Create step complete timeline entry if TCS enabled
                if self.enable_tcs and self.tcs_integration:
                    self.tcs_integration.create_step_complete_entry(step, plan.name, execution_id)
                
                return "skipped"
            
            if not global_budget.check_time(step.budget.time_limit_seconds):
                step.status = StepStatus.SKIPPED
                step.error = "Insufficient global budget time"
                step.completed_at = datetime.now(UTC)
                
                # Create step complete timeline entry if TCS enabled
                if self.enable_tcs and self.tcs_integration:
                    self.tcs_integration.create_step_complete_entry(step, plan.name, execution_id)
                
                return "skipped"
        
        # Execute step
        result = self._execute_step(step, plan, execution_id)
        
        # Consume budget if successful
        if result == "completed" and step.budget:
            # Estimate consumption (in production, measure actual)
            tokens_used = int(step.budget.tokens_limit * 0.8)  # Assume 80% of limit
            time_used = step.duration() or step.budget.time_limit_seconds
            
            if global_budget:
                global_budget.consume_tokens(tokens_used)
                global_budget.consume_time(time_used)
                
                # Check for budget milestones and create timeline entries
                if self.enable_tcs and self.tcs_integration:
                    # Check for 50% consumed milestone
                    tokens_percent = (global_budget.tokens_consumed / global_budget.tokens_limit) * 100 if global_budget.tokens_limit > 0 else 0
                    time_percent = (global_budget.time_elapsed_seconds / global_budget.time_limit_seconds) * 100 if global_budget.time_limit_seconds > 0 else 0
                    
                    # Create milestone entries for significant thresholds
                    if tokens_percent >= 50 and tokens_percent < 60:  # Only log once around 50%
                        self.tcs_integration.create_budget_milestone_entry(
                            plan_name=plan.name,
                            execution_id=execution_id,
                            milestone_type="50%_tokens_consumed",
                            budget_data={
                                "tokens_limit": global_budget.tokens_limit,
                                "tokens_consumed": global_budget.tokens_consumed,
                                "tokens_remaining": global_budget.remaining_tokens(),
                                "time_limit": global_budget.time_limit_seconds,
                                "time_elapsed": global_budget.time_elapsed_seconds,
                                "time_remaining": global_budget.remaining_time()
                            },
                            step_id=step.id
                        )
                    
                    if time_percent >= 50 and time_percent < 60:  # Only log once around 50%
                        self.tcs_integration.create_budget_milestone_entry(
                            plan_name=plan.name,
                            execution_id=execution_id,
                            milestone_type="50%_time_consumed",
                            budget_data={
                                "tokens_limit": global_budget.tokens_limit,
                                "tokens_consumed": global_budget.tokens_consumed,
                                "tokens_remaining": global_budget.remaining_tokens(),
                                "time_limit": global_budget.time_limit_seconds,
                                "time_elapsed": global_budget.time_elapsed_seconds,
                                "time_remaining": global_budget.remaining_time()
                            },
                            step_id=step.id
                        )
                    
                    # Check for budget exceeded
                    if global_budget.tokens_consumed >= global_budget.tokens_limit:
                        self.tcs_integration.create_budget_milestone_entry(
                            plan_name=plan.name,
                            execution_id=execution_id,
                            milestone_type="budget_exceeded",
                            budget_data={
                                "tokens_limit": global_budget.tokens_limit,
                                "tokens_consumed": global_budget.tokens_consumed,
                                "tokens_remaining": global_budget.remaining_tokens(),
                                "time_limit": global_budget.time_limit_seconds,
                                "time_elapsed": global_budget.time_elapsed_seconds,
                                "time_remaining": global_budget.remaining_time()
                            },
                            step_id=step.id
                        )
        
        return result

