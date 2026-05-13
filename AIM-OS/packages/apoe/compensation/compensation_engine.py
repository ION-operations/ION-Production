"""
Compensation Engine

Implements saga pattern for reversible operations.
Executes compensation steps in reverse topological order on failure.
"""

from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from datetime import UTC, datetime

from ..models import Step, ExecutionPlan, StepStatus


@dataclass
class CompensationResult:
    """Result of compensation execution"""
    success: bool
    compensated_steps: List[str]
    failed_compensations: List[Tuple[str, str]]  # (step_id, error)
    total_time_ms: float


class CompensationEngine:
    """
    Executes compensation steps in reverse order on failure.
    
    Saga Pattern:
    - Forward execution: step1 → step2 → step3
    - On failure at step3: compensate(step2) → compensate(step1)
    - Best effort: Continue compensating even if individual steps fail
    
    Key Properties:
    - Reverse topological order
    - Best-effort (individual failures don't stop compensation)
    - Complete logging for audit trail
    """
    
    def __init__(self, executor):
        """
        Initialize with executor instance.
        
        Args:
            executor: PlanExecutor instance (for executing compensation steps)
        """
        self.executor = executor
    
    def execute_with_compensation(
        self,
        plan: ExecutionPlan,
        initial_state: Dict[str, Any]
    ) -> Tuple[bool, List[Step], Optional[CompensationResult]]:
        """
        Execute plan with automatic compensation on failure.
        
        Args:
            plan: Execution plan
            initial_state: Initial state for execution
            
        Returns:
            Tuple of:
            - success (bool): Overall success
            - completed_steps (List[Step]): Steps that completed
            - compensation_result (Optional[CompensationResult]): Compensation details if triggered
        """
        completed_steps = []
        start_time = datetime.now(UTC)
        
        try:
            # Execute plan normally
            for step in self._get_execution_order(plan):
                result = self.executor._execute_step(step, plan)
                
                if result == "failed":
                    # Failure: trigger compensation
                    comp_result = self._compensate(completed_steps, plan)
                    return False, completed_steps, comp_result
                
                elif result == "completed":
                    completed_steps.append(step)
            
            # Success: no compensation needed
            return True, completed_steps, None
        
        except Exception as e:
            # Unexpected error: compensate what we can
            comp_result = self._compensate(completed_steps, plan)
            return False, completed_steps, comp_result
    
    def _compensate(
        self,
        completed_steps: List[Step],
        plan: ExecutionPlan
    ) -> CompensationResult:
        """
        Execute compensation in reverse topological order.
        
        Args:
            completed_steps: Steps that completed successfully
            plan: Original execution plan
            
        Returns:
            CompensationResult with details
            
        Algorithm:
        1. Reverse completed_steps list
        2. For each step with compensation:
           a. Create compensation step
           b. Execute compensation step
           c. Log result (success or failure)
        3. Return CompensationResult
        """
        start_time = datetime.now(UTC)
        compensated = []
        failed = []
        
        # Compensate in reverse order
        for step in reversed(completed_steps):
            if step.compensation is None:
                continue
            
            try:
                # Execute compensation step
                comp_step = self._create_compensation_step(step, plan)
                result = self.executor._execute_step(comp_step, plan)
                
                if result == "completed":
                    compensated.append(step.name)
                else:
                    failed.append((step.name, "Compensation failed"))
            
            except Exception as e:
                failed.append((step.name, str(e)))
        
        end_time = datetime.now(UTC)
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        return CompensationResult(
            success=len(failed) == 0,
            compensated_steps=compensated,
            failed_compensations=failed,
            total_time_ms=duration_ms
        )
    
    def _create_compensation_step(self, step: Step, plan: ExecutionPlan) -> Step:
        """
        Create compensation step from original step.
        
        Args:
            step: Original step that needs compensation
            plan: Execution plan
            
        Returns:
            New Step configured for compensation
        """
        if step.compensation is None:
            raise ValueError(f"Step {step.name} has no compensation defined")
        
        compensation_def = step.compensation
        
        return Step(
            id=f"compensate_{step.name}",
            name=f"compensate_{step.name}",
            role=step.role,
            role_name=step.role_name,
            description=f"Compensate: {compensation_def.action}",
            gates=[],
            budget=step.budget,  # Use same budget as original
            outputs={}
        )
    
    def _get_execution_order(self, plan: ExecutionPlan) -> List[Step]:
        """
        Get execution order (topologically sorted).
        
        Uses existing executor's dependency resolution.
        """
        return self.executor._resolve_dependencies(plan)

