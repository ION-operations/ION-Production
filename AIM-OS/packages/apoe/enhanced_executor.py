"""
Enhanced APOE Executor

Extends PlanExecutor with PLIx capabilities:
- Compensation execution (saga pattern)
- Retry/fallback logic
- Purity validation
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass

from .executor import PlanExecutor, ExecutionResult
from .acl_parser import ExecutionPlan
from .models import Step
from .compensation.compensation_engine import CompensationEngine, CompensationResult
from .retry_fallback.retry_engine import RetryEngine, RetryResult, BackoffStrategy
from .purity_validation.runtime_validator import RuntimePurityValidator


@dataclass
class EnhancedExecutionResult(ExecutionResult):
    """Enhanced execution result with PLIx data"""
    compensation_result: Optional[CompensationResult] = None
    retry_results: Dict[str, RetryResult] = None
    execution_mode: str = "standard"  # "standard" | "compensation" | "retry"
    
    def __post_init__(self):
        if self.retry_results is None:
            self.retry_results = {}


class EnhancedAPOEExecutor(PlanExecutor):
    """
    Enhanced APOE executor with PLIx capabilities.
    
    Extends PlanExecutor with:
    - Automatic compensation on failure (saga pattern)
    - Retry with backoff and fallback
    - Runtime purity validation
    
    Backwards Compatible:
    - Plans without PLIx features execute with standard executor
    - Enhancement only activates when PLIx features detected
    """
    
    def __init__(self):
        super().__init__()
        self.compensation_engine = CompensationEngine(self)
        self.retry_engine = RetryEngine()
        self.purity_validator = RuntimePurityValidator()
    
    def execute(
        self,
        plan: ExecutionPlan,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> EnhancedExecutionResult:
        """
        Execute plan with enhancement detection.
        
        Automatically detects if plan needs enhancement:
        - Compensation: Has steps with compensation defined
        - Retry: Has steps with retry policies
        - If neither: Falls back to standard execution
        
        Args:
            plan: ACL execution plan
            initial_state: Initial state for execution
            
        Returns:
            EnhancedExecutionResult with outcome and metadata
        """
        # Detect enhancement needs
        has_compensation = self._has_compensation(plan)
        has_retry = self._has_retry(plan)
        
        if has_compensation:
            return self.execute_with_compensation(plan, initial_state)
        elif has_retry:
            return self.execute_with_retry(plan, initial_state)
        else:
            # No enhancement needed: use standard execution
            standard_result = super().execute(plan)
            return EnhancedExecutionResult(
                plan_name=standard_result.plan_name,
                failed_steps=standard_result.failed_steps,
                skipped_steps=standard_result.skipped_steps,
                total_duration_seconds=standard_result.total_duration_seconds,
                success=standard_result.success,
                completed_steps=standard_result.completed_steps,
                total_steps=standard_result.total_steps,
                error=standard_result.error,
                execution_mode="standard"
            )
    
    def execute_with_compensation(
        self,
        plan: ExecutionPlan,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> EnhancedExecutionResult:
        """
        Execute plan with automatic compensation on failure.
        
        Saga pattern:
        - Forward execution until failure
        - Reverse compensation of completed steps
        - Best-effort compensation (continues on individual failures)
        
        Returns:
            EnhancedExecutionResult with compensation_result field
        """
        success, completed_steps, comp_result = \
            self.compensation_engine.execute_with_compensation(plan, initial_state or {})

        failed_steps = 0 if success else 1
        skipped_steps = max(len(plan.steps) - len(completed_steps) - failed_steps, 0)
        duration_seconds = (comp_result.total_time_ms / 1000.0) if comp_result else 0.0
        
        return EnhancedExecutionResult(
            plan_name=plan.name,
            failed_steps=failed_steps,
            skipped_steps=skipped_steps,
            total_duration_seconds=duration_seconds,
            success=success,
            completed_steps=len(completed_steps),
            total_steps=len(plan.steps),
            error=None if success else "Execution failed",
            compensation_result=comp_result,
            execution_mode="compensation"
        )
    
    def execute_with_retry(
        self,
        plan: ExecutionPlan,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> EnhancedExecutionResult:
        """
        Execute plan with retry logic.
        
        For each step with retry policy:
        - Attempt execution
        - On failure: retry with backoff
        - On retry exhaustion: try fallback (if defined)
        - On complete failure: stop or continue based on step config
        
        Returns:
            EnhancedExecutionResult with retry_results field
        """
        completed_steps = []
        retry_results = {}
        
        for step in plan.steps:
            if step.retry_policy:
                # Execute with retry
                def step_fn():
                    result = self._execute_step(step, plan)
                    if result != "completed":
                        raise Exception(f"Step {step.name} failed")
                    return result
                
                def fallback_fn():
                    if step.fallback:
                        return self._execute_step(step.fallback, plan)
                    raise Exception("No fallback defined")
                
                retry_result = self.retry_engine.execute_with_retry(
                    step_fn,
                    max_attempts=step.retry_policy.max_attempts,
                    backoff_strategy=BackoffStrategy(step.retry_policy.backoff_strategy),
                    backoff_base=step.retry_policy.backoff_base,
                    max_backoff=step.retry_policy.max_backoff,
                    jitter=step.retry_policy.jitter,
                    fallback_fn=fallback_fn if step.fallback else None
                )
                
                retry_results[step.name] = retry_result
                
                if retry_result.success:
                    completed_steps.append(step)
                else:
                    break  # Stop on failure
            else:
                # No retry: execute normally
                result = self._execute_step(step, plan)
                if result == "completed":
                    completed_steps.append(step)
                else:
                    break

        success = len(completed_steps) == len(plan.steps)
        failed_steps = 0 if success else 1
        skipped_steps = max(len(plan.steps) - len(completed_steps) - failed_steps, 0)
        total_duration_seconds = sum(
            retry_result.total_time_ms for retry_result in retry_results.values()
        ) / 1000.0
        
        return EnhancedExecutionResult(
            plan_name=plan.name,
            failed_steps=failed_steps,
            skipped_steps=skipped_steps,
            total_duration_seconds=total_duration_seconds,
            success=success,
            completed_steps=len(completed_steps),
            total_steps=len(plan.steps),
            error=None if success else "Execution incomplete",
            retry_results=retry_results,
            execution_mode="retry"
        )
    
    def _has_compensation(self, plan: ExecutionPlan) -> bool:
        """Check if plan has compensation steps"""
        return any(
            step.compensation is not None
            for step in plan.steps
        )
    
    def _has_retry(self, plan: ExecutionPlan) -> bool:
        """Check if plan has retry policies"""
        return any(
            step.retry_policy is not None
            for step in plan.steps
        )

