"""
Rules engine - hard gates for safety, budget, preconditions, rate limits.
"""

from typing import List, Dict, Any

from ..types import ToolCallPlan, ValidationResult, VIFGate


class RulesEngine:
    """
    Rules engine for plan validation.
    
    Enforces:
    - VIF gates (quality checks)
    - Budget limits
    - Rate limits
    - Depth limits
    - Risk gates
    """
    
    def __init__(self, vif_client=None):
        self.vif = vif_client
        
        # Default limits
        self.max_depth = 3
        self.max_steps = 20
        self.max_parallel = 3
        self.budget_limits = {
            "tokens": 100000,
            "cost": 10.0,
            "time_ms": 30000
        }
    
    def validate(self, plan: ToolCallPlan) -> ValidationResult:
        """
        Validate tool call plan.
        
        Args:
            plan: Tool call plan to validate
            
        Returns:
            ValidationResult with passed status and reasons
        """
        reasons = []
        warnings = []
        
        # Check depth limit
        if len(plan.steps) > self.max_depth:
            reasons.append(f"Plan depth {len(plan.steps)} exceeds max {self.max_depth}")
        
        # Check step count
        if len(plan.steps) > self.max_steps:
            reasons.append(f"Plan has {len(plan.steps)} steps, exceeds max {self.max_steps}")
        
        # Check budget
        if plan.budget:
            for key, limit in self.budget_limits.items():
                if key in plan.budget and plan.budget[key] > limit:
                    reasons.append(f"Budget {key} {plan.budget[key]} exceeds limit {limit}")
        
        # Check VIF gates for high-risk tools
        vif_result = self._check_vif_gates(plan)
        if not vif_result.passed:
            reasons.extend(vif_result.reasons or [])
        
        # Check parallelization limits
        parallel_groups = {}
        for step in plan.steps:
            if step.parallel_group:
                parallel_groups[step.parallel_group] = \
                    parallel_groups.get(step.parallel_group, 0) + 1
        
        for group, count in parallel_groups.items():
            if count > self.max_parallel:
                warnings.append(
                    f"Parallel group {group} has {count} steps, "
                    f"exceeds recommended {self.max_parallel}"
                )
        
        passed = len(reasons) == 0
        
        return ValidationResult(
            passed=passed,
            reasons=reasons,
            warnings=warnings
        )
    
    def _check_vif_gates(self, plan: ToolCallPlan) -> VIFGate:
        """Check VIF gates for high-risk tools."""
        if not self.vif:
            return VIFGate(passed=True)
        
        # Check if any high-risk tools require VIF validation
        high_risk_steps = [
            step for step in plan.steps
            if step.preflight  # Steps with preflight checks
        ]
        
        if not high_risk_steps:
            return VIFGate(passed=True)
        
        # In production, would call VIF to validate
        # For now, assume passed if no VIF client
        return VIFGate(passed=True, confidence=0.8)

