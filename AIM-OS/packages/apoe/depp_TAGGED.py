"""DEPP: Dynamic Execution Plan Processor

Enables plans to modify themselves during execution based on results.
Self-improving, adaptive orchestration.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from copy import deepcopy

from apoe.models import Step, Budget, Gate
from apoe.roles import RoleType


@dataclass
# NL_TAG: VIF-MODEL-001 | Represents a modification to execution plan. | class PlanModification | []
class PlanModification:
    """Represents a modification to execution plan."""
    modification_id: str
    modification_type: str  # "add_step", "remove_step", "modify_step", "add_gate"
    target_step_id: Optional[str]
    new_data: Dict[str, Any]
    reason: str
    confidence: float


# NL_TAG: VIF-MODEL-002 | Execution plan that can modify itself during execution. | class SelfModifyingPlan | []
class SelfModifyingPlan:
    """Execution plan that can modify itself during execution."""
    
    def __init__(self, base_plan):
        """
        Initialize with base plan.
        
        Args:
            base_plan: Original ExecutionPlan
        """
        self.base_plan = base_plan
        self.current_plan = deepcopy(base_plan)
        self.modifications: List[PlanModification] = []
        self._modification_counter = 0
    
    def add_step_dynamically(
        self,
        step: Step,
        after_step_id: Optional[str] = None,
        reason: str = "Dynamic addition",
        confidence: float = 0.80
    ) -> str:
        """Add step to plan during execution."""
        modification = PlanModification(
            modification_id=f"mod_{self._modification_counter:04d}",
            modification_type="add_step",
            target_step_id=after_step_id,
            new_data={"step": step},
            reason=reason,
            confidence=confidence
        )
        
        self._modification_counter += 1
        self.modifications.append(modification)
        
        # Add to current plan
        if after_step_id:
            # Find insertion point
            idx = next(
                (i for i, s in enumerate(self.current_plan.steps) if s.id == after_step_id),
                len(self.current_plan.steps)
            )
            self.current_plan.steps.insert(idx + 1, step)
        else:
            # Add to end
            self.current_plan.steps.append(step)
        
        return modification.modification_id
    
    def modify_step_budget(
        self,
        step_id: str,
        new_budget: Budget,
        reason: str = "Budget adjustment",
        confidence: float = 0.85
    ) -> str:
        """Modify step budget during execution."""
        modification = PlanModification(
            modification_id=f"mod_{self._modification_counter:04d}",
            modification_type="modify_step",
            target_step_id=step_id,
            new_data={"budget": new_budget},
            reason=reason,
            confidence=confidence
        )
        
        self._modification_counter += 1
        self.modifications.append(modification)
        
        # Apply modification
        for step in self.current_plan.steps:
            if step.id == step_id:
                step.budget = new_budget
                break
        
        return modification.modification_id
    
    def add_gate_to_step(
        self,
        step_id: str,
        gate: Gate,
        reason: str = "Additional quality check",
        confidence: float = 0.90
    ) -> str:
        """Add gate to step during execution."""
        modification = PlanModification(
            modification_id=f"mod_{self._modification_counter:04d}",
            modification_type="add_gate",
            target_step_id=step_id,
            new_data={"gate": gate},
            reason=reason,
            confidence=confidence
        )
        
        self._modification_counter += 1
        self.modifications.append(modification)
        
        # Apply modification
        for step in self.current_plan.steps:
            if step.id == step_id:
                step.gates.append(gate)
                break
        
        return modification.modification_id
    
    def remove_step(
        self,
        step_id: str,
        reason: str = "No longer needed",
        confidence: float = 0.75
    ) -> str:
        """Remove step from plan during execution."""
        modification = PlanModification(
            modification_id=f"mod_{self._modification_counter:04d}",
            modification_type="remove_step",
            target_step_id=step_id,
            new_data={},
            reason=reason,
            confidence=confidence
        )
        
        self._modification_counter += 1
        self.modifications.append(modification)
        
        # Remove from current plan
        self.current_plan.steps = [
            s for s in self.current_plan.steps
            if s.id != step_id
        ]
        
        return modification.modification_id
    
    def get_modification_history(self) -> List[PlanModification]:
        """Get complete modification history."""
        return self.modifications.copy()
    
    def has_been_modified(self) -> bool:
        """Check if plan has been modified from base."""
        return len(self.modifications) > 0


# NL_TAG: VIF-MODEL-003 | Controls dynamic plan modification based on execution results. | class DEPPController | []
class DEPPController:
    """Controls dynamic plan modification based on execution results."""
    
    def __init__(self):
        self.modification_rules: List[Callable] = []
    
    def register_modification_rule(self, rule: Callable):
        """
        Register rule for plan modification.
        
        Rule signature: (plan, step_results) -> List[PlanModification]
        """
        self.modification_rules.append(rule)
    
    def evaluate_modifications(
        self,
        plan: SelfModifyingPlan,
        step_results: Dict[str, Any]
    ) -> List[PlanModification]:
        """Evaluate if plan should be modified based on results."""
        proposed_modifications = []
        
        for rule in self.modification_rules:
            try:
                mods = rule(plan, step_results)
                if mods:
                    proposed_modifications.extend(mods)
            except Exception:
                # Rule failed, skip it
                pass
        
        return proposed_modifications
    
    def apply_modifications(
        self,
        plan: SelfModifyingPlan,
        modifications: List[PlanModification]
    ):
        """Apply approved modifications to plan."""
        for mod in modifications:
            if mod.modification_type == "add_step":
                step = mod.new_data.get("step")
                if step:
                    plan.add_step_dynamically(
                        step=step,
                        after_step_id=mod.target_step_id,
                        reason=mod.reason,
                        confidence=mod.confidence
                    )
            
            elif mod.modification_type == "modify_step":
                budget = mod.new_data.get("budget")
                if budget and mod.target_step_id:
                    plan.modify_step_budget(
                        step_id=mod.target_step_id,
                        new_budget=budget,
                        reason=mod.reason,
                        confidence=mod.confidence
                    )
            
            elif mod.modification_type == "add_gate":
                gate = mod.new_data.get("gate")
                if gate and mod.target_step_id:
                    plan.add_gate_to_step(
                        step_id=mod.target_step_id,
                        gate=gate,
                        reason=mod.reason,
                        confidence=mod.confidence
                    )
            
            elif mod.modification_type == "remove_step":
                if mod.target_step_id:
                    plan.remove_step(
                        step_id=mod.target_step_id,
                        reason=mod.reason,
                        confidence=mod.confidence
                    )


# Example modification rules

# NL_TAG: VIF-CONF-001 | If step has low confidence, add verification step. | low_confidence_adds_verification(plan, step_results) | []
# NL_TAG_INTENT: VIF-INTENT-001 | Design decision: confidence | low_confidence_adds_verification | [ADR-TBD]
def low_confidence_adds_verification(
    plan: SelfModifyingPlan,
    step_results: Dict[str, Any]
) -> List[PlanModification]:
    """If step has low confidence, add verification step."""
    modifications = []
    
    # Check last step's confidence
    if "confidence" in step_results and step_results["confidence"] < 0.75:
        # Add verification step
        modifications.append(PlanModification(
            modification_id="auto_verify",
            modification_type="add_step",
            target_step_id=None,  # Add after current
            new_data={
                "step": Step(
                    id="verify_low_conf",
                    name="Verify Low Confidence Result",
                    role=RoleType.VERIFIER,
                    role_name="verifier",
                    description="Verify previous step due to low confidence",
                    budget=Budget(tokens_limit=1000, time_limit_seconds=10)
                )
            },
            reason=f"Low confidence detected ({step_results['confidence']:.2f})",
            confidence=0.90
        ))
    
    return modifications


# NL_TAG: VIF-UTIL-001 | If step times out, increase time budget. | timeout_increases_budget(plan, step_results) | []
def timeout_increases_budget(
    # NL_TAG: VIF-UTIL-002 | Initialize with base plan. | __init__(self, base_plan) | []
    def __init__(self, base_plan):
        """
        Initialize with base plan.
        
        Args:
            base_plan: Original ExecutionPlan
        """
        self.base_plan = base_plan
        self.current_plan = deepcopy(base_plan)
        self.modifications: List[PlanModification] = []
        self._modification_counter = 0
    
    # NL_TAG: VIF-UTIL-003 | Add step to plan during execution. | add_step_dynamically(self, step, after_step_id, reason, confidence) | []
    def add_step_dynamically(
        self,
        step: Step,
        after_step_id: Optional[str] = None,
        reason: str = "Dynamic addition",
        confidence: float = 0.80
    ) -> str:
        """Add step to plan during execution."""
        modification = PlanModification(
            modification_id=f"mod_{self._modification_counter:04d}",
            modification_type="add_step",
            target_step_id=after_step_id,
            new_data={"step": step},
            reason=reason,
            confidence=confidence
        )
        
        self._modification_counter += 1
        self.modifications.append(modification)
        
        # Add to current plan
        if after_step_id:
            # Find insertion point
            idx = next(
                (i for i, s in enumerate(self.current_plan.steps) if s.id == after_step_id),
                len(self.current_plan.steps)
            )
            self.current_plan.steps.insert(idx + 1, step)
        else:
            # Add to end
            self.current_plan.steps.append(step)
        
        return modification.modification_id
    
    # NL_TAG: VIF-UTIL-004 | Modify step budget during execution. | modify_step_budget(self, step_id, new_budget, reason, confidence) | []
    def modify_step_budget(
        self,
        step_id: str,
        new_budget: Budget,
        reason: str = "Budget adjustment",
        confidence: float = 0.85
    ) -> str:
        """Modify step budget during execution."""
        modification = PlanModification(
            modification_id=f"mod_{self._modification_counter:04d}",
            modification_type="modify_step",
            target_step_id=step_id,
            new_data={"budget": new_budget},
            reason=reason,
            confidence=confidence
        )
        
        self._modification_counter += 1
        self.modifications.append(modification)
        
        # Apply modification
        for step in self.current_plan.steps:
            if step.id == step_id:
                step.budget = new_budget
                break
        
        return modification.modification_id
    
    # NL_TAG: VIF-GATE-001 | Add gate to step during execution. | add_gate_to_step(self, step_id, gate, reason, confidence) | []
    # NL_TAG_INTENT: VIF-INTENT-002 | Design decision: gate | add_gate_to_step | [ADR-TBD]
    def add_gate_to_step(
        self,
        step_id: str,
        gate: Gate,
        reason: str = "Additional quality check",
        confidence: float = 0.90
    ) -> str:
        """Add gate to step during execution."""
        modification = PlanModification(
            modification_id=f"mod_{self._modification_counter:04d}",
            modification_type="add_gate",
            target_step_id=step_id,
            new_data={"gate": gate},
            reason=reason,
            confidence=confidence
        )
        
        self._modification_counter += 1
        self.modifications.append(modification)
        
        # Apply modification
        for step in self.current_plan.steps:
            if step.id == step_id:
                step.gates.append(gate)
                break
        
        return modification.modification_id
    
    # NL_TAG: VIF-UTIL-005 | Remove step from plan during execution. | remove_step(self, step_id, reason, confidence) | []
    def remove_step(
        self,
        step_id: str,
        reason: str = "No longer needed",
        confidence: float = 0.75
    ) -> str:
        """Remove step from plan during execution."""
        modification = PlanModification(
            modification_id=f"mod_{self._modification_counter:04d}",
            modification_type="remove_step",
            target_step_id=step_id,
            new_data={},
            reason=reason,
            confidence=confidence
        )
        
        self._modification_counter += 1
        self.modifications.append(modification)
        
        # Remove from current plan
        self.current_plan.steps = [
            s for s in self.current_plan.steps
            if s.id != step_id
        ]
        
        return modification.modification_id
    
    # NL_TAG: VIF-UTIL-006 | Get complete modification history. | get_modification_history(self) | []
    def get_modification_history(self) -> List[PlanModification]:
        """Get complete modification history."""
        return self.modifications.copy()
    
    # NL_TAG: VIF-UTIL-007 | Check if plan has been modified from base. | has_been_modified(self) | []
    def has_been_modified(self) -> bool:
        """Check if plan has been modified from base."""
        return len(self.modifications) > 0


class DEPPController:
    """Controls dynamic plan modification based on execution results."""
    
    # NL_TAG: VIF-UTIL-008 |   init   | __init__(self) | []
    def __init__(self):
        self.modification_rules: List[Callable] = []
    
    # NL_TAG: VIF-UTIL-009 | Register rule for plan modification. | register_modification_rule(self, rule) | []
    def register_modification_rule(self, rule: Callable):
        """
        Register rule for plan modification.
        
        Rule signature: (plan, step_results) -> List[PlanModification]
        """
        self.modification_rules.append(rule)
    
    # NL_TAG: VIF-UTIL-010 | Evaluate if plan should be modified based on results. | evaluate_modifications(self, plan, step_results) | []
    def evaluate_modifications(
        self,
        plan: SelfModifyingPlan,
        step_results: Dict[str, Any]
    ) -> List[PlanModification]:
        """Evaluate if plan should be modified based on results."""
        proposed_modifications = []
        
        for rule in self.modification_rules:
            try:
                mods = rule(plan, step_results)
                if mods:
                    proposed_modifications.extend(mods)
            except Exception:
                # Rule failed, skip it
                pass
        
        return proposed_modifications
    
    # NL_TAG: VIF-UTIL-011 | Apply approved modifications to plan. | apply_modifications(self, plan, modifications) | []
    def apply_modifications(
        self,
        plan: SelfModifyingPlan,
        modifications: List[PlanModification]
    ):
        """Apply approved modifications to plan."""
        for mod in modifications:
            if mod.modification_type == "add_step":
                step = mod.new_data.get("step")
                if step:
                    plan.add_step_dynamically(
                        step=step,
                        after_step_id=mod.target_step_id,
                        reason=mod.reason,
                        confidence=mod.confidence
                    )
            
            elif mod.modification_type == "modify_step":
                budget = mod.new_data.get("budget")
                if budget and mod.target_step_id:
                    plan.modify_step_budget(
                        step_id=mod.target_step_id,
                        new_budget=budget,
                        reason=mod.reason,
                        confidence=mod.confidence
                    )
            
            elif mod.modification_type == "add_gate":
                gate = mod.new_data.get("gate")
                if gate and mod.target_step_id:
                    plan.add_gate_to_step(
                        step_id=mod.target_step_id,
                        gate=gate,
                        reason=mod.reason,
                        confidence=mod.confidence
                    )
            
            elif mod.modification_type == "remove_step":
                if mod.target_step_id:
                    plan.remove_step(
                        step_id=mod.target_step_id,
                        reason=mod.reason,
                        confidence=mod.confidence
                    )


# Example modification rules

def low_confidence_adds_verification(
    plan: SelfModifyingPlan,
    step_results: Dict[str, Any]
) -> List[PlanModification]:
    """If step has low confidence, add verification step."""
    modifications = []
    
    # Check last step's confidence
    if "confidence" in step_results and step_results["confidence"] < 0.75:
        # Add verification step
        modifications.append(PlanModification(
            modification_id="auto_verify",
            modification_type="add_step",
            target_step_id=None,  # Add after current
            new_data={
                "step": Step(
                    id="verify_low_conf",
                    name="Verify Low Confidence Result",
                    role=RoleType.VERIFIER,
                    role_name="verifier",
                    description="Verify previous step due to low confidence",
                    budget=Budget(tokens_limit=1000, time_limit_seconds=10)
                )
            },
            reason=f"Low confidence detected ({step_results['confidence']:.2f})",
            confidence=0.90
        ))
    
    return modifications


def timeout_increases_budget(
    plan: SelfModifyingPlan,
    step_results: Dict[str, Any]
) -> List[PlanModification]:
    """If step times out, increase time budget."""
    modifications = []
    
    if step_results.get("timeout"):
        current_step_id = step_results.get("step_id")
        if current_step_id:
            # Double the time budget
            new_budget = Budget(
                tokens_limit=10000,  # Keep same
                time_limit_seconds=60  # Increased
            )
            
            modifications.append(PlanModification(
                modification_id="increase_time",
                modification_type="modify_step",
                target_step_id=current_step_id,
                new_data={"budget": new_budget},
                reason="Step timed out, increasing time budget",
                confidence=0.85
            ))
    
    return modifications

