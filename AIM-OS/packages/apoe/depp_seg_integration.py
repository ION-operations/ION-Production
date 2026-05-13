"""DEPP-SEG Integration: Evidence-Based Plan Modifications

Enhances DEPP with SEG evidence queries for intelligent plan modifications.
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List
import logging

from .depp import DEPPController, PlanModification, SelfModifyingPlan
from .models import Step, Budget, Gate, RoleType
from .acl_parser import ExecutionPlan

# TCS integration (optional)
try:
    from packages.apoe.tcs_integration import APOETCSIntegration
    TCS_AVAILABLE = True
except ImportError:
    TCS_AVAILABLE = False
    APOETCSIntegration = None

logger = logging.getLogger(__name__)

# SEG imports (optional)
try:
    from packages.seg.seg_graph import SEGraph
    from packages.seg.models import RelationType
    SEG_AVAILABLE = True
except ImportError:
    SEG_AVAILABLE = False
    SEGraph = None
    RelationType = None


class EvidenceBasedDEPPController(DEPPController):
    """DEPP controller enhanced with SEG evidence queries.
    
    Uses SEG to query historical plan patterns and inform modifications.
    """
    
    def __init__(
        self,
        seg_graph: Optional[SEGraph] = None,
        tcs_integration: Optional[APOETCSIntegration] = None
    ):
        """
        Initialize evidence-based DEPP controller.
        
        Args:
            seg_graph: SEG graph instance (optional)
            tcs_integration: TCS integration instance for timeline entries (optional)
        """
        super().__init__()
        self.seg_available = SEG_AVAILABLE and seg_graph is not None
        self.seg = seg_graph
        self.tcs_integration = tcs_integration
        
        if self.seg_available:
            # Register evidence-based modification rules
            self.register_modification_rule(self._rule_low_success_rate_adds_verification)
            self.register_modification_rule(self._rule_budget_inefficiency_adjusts_budget)
            self.register_modification_rule(self._rule_gate_failures_adds_gates)
            self.register_modification_rule(self._rule_similar_plans_suggests_steps)
    
    def query_plan_effectiveness_patterns(
        self,
        plan_name: str,
        role: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Query SEG for similar plan effectiveness patterns.
        
        Args:
            plan_name: Name of plan
            role: Filter by role (optional)
            
        Returns:
            List of effectiveness patterns
        """
        if not self.seg_available or not self.seg:
            return []
        
        try:
            # Get all plan effectiveness evidence for this plan
            all_evidence = self.seg.list_evidence()
            
            # Filter for plan effectiveness
            effectiveness_evidence = [
                e for e in all_evidence
                if e.evidence_type == "apoe_plan_effectiveness"
                and e.metadata.get("plan_name") == plan_name
            ]
            
            # Get related step effectiveness
            step_effectiveness = []
            for eff_ev in effectiveness_evidence:
                # Find related step evidence
                relations = self.seg.get_outgoing_relations(eff_ev.id)
                for rel in relations:
                    if rel.relation_type == RelationType.RELATES_TO:
                        step_ev = self.seg.get_evidence(rel.target_id)
                        if step_ev and step_ev.evidence_type == "apoe_step_execution":
                            step_role = step_ev.metadata.get("role")
                            if not role or step_role == role:
                                step_effectiveness.append({
                                    "step_name": step_ev.metadata.get("step_name"),
                                    "role": step_role,
                                    "status": step_ev.metadata.get("status"),
                                    "confidence": step_ev.confidence
                                })
            
            return step_effectiveness
        except Exception as e:
            logger.error(f"Failed to query plan effectiveness patterns: {e}", exc_info=True)
            return []
    
    def query_step_success_patterns(
        self,
        role: str,
        min_success_rate: float = 0.8
    ) -> List[Dict[str, Any]]:
        """Query for steps with high success rates.
        
        Args:
            role: Role to query
            min_success_rate: Minimum success rate threshold
            
        Returns:
            List of successful step patterns
        """
        if not self.seg_available or not self.seg:
            return []
        
        try:
            all_evidence = self.seg.list_evidence()
            
            successful_steps = []
            for ev in all_evidence:
                if (ev.evidence_type == "apoe_step_execution" and
                    ev.metadata.get("role") == role):
                    # Check confidence (proxy for success rate)
                    if ev.confidence >= min_success_rate:
                        successful_steps.append({
                            "step_name": ev.metadata.get("step_name"),
                            "role": role,
                            "confidence": ev.confidence,
                            "duration": ev.metadata.get("duration_seconds", 0.0)
                        })
            
            return successful_steps
        except Exception as e:
            logger.error(f"Failed to query step success patterns: {e}", exc_info=True)
            return []
    
    def get_plan_effectiveness_history(
        self,
        plan_name: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get historical plan effectiveness data.
        
        Args:
            plan_name: Name of plan
            limit: Maximum number of results
            
        Returns:
            List of effectiveness records
        """
        if not self.seg_available or not self.seg:
            return []
        
        try:
            all_evidence = self.seg.list_evidence()
            
            # Filter for plan effectiveness
            effectiveness_evidence = [
                e for e in all_evidence
                if (e.evidence_type == "apoe_plan_effectiveness" and
                    e.metadata.get("plan_name") == plan_name)
            ]
            
            # Sort by timestamp (most recent first)
            effectiveness_evidence.sort(
                key=lambda e: e.metadata.get("computed_at", ""),
                reverse=True
            )
            
            # Return limited results
            return [
                {
                    "execution_id": e.metadata.get("execution_id"),
                    "effectiveness_score": e.metadata.get("effectiveness_score"),
                    "metrics": e.metadata.get("metrics", {}),
                    "timestamp": e.vt_start.isoformat() if hasattr(e.vt_start, 'isoformat') else str(e.vt_start)
                }
                for e in effectiveness_evidence[:limit]
            ]
        except Exception as e:
            logger.error(f"Failed to get plan effectiveness history: {e}", exc_info=True)
            return []
    
    def _rule_low_success_rate_adds_verification(
        self,
        plan: SelfModifyingPlan,
        step_results: Dict[str, Any]
    ) -> List[PlanModification]:
        """Rule: If step has low success rate historically, add verification step.
        
        Args:
            plan: Self-modifying plan
            step_results: Current step execution results
            
        Returns:
            List of proposed modifications
        """
        if not self.seg_available:
            return []
        
        modifications = []
        
        # Check each completed step
        for step_id, result in step_results.items():
            if result.get("status") != "completed":
                continue
            
            # Query SEG for this step's historical success rate
            step = next((s for s in plan.current_plan.steps if s.id == step_id), None)
            if not step:
                continue
            
            role = step.role.value if hasattr(step.role, 'value') else str(step.role)
            patterns = self.query_step_success_patterns(role, min_success_rate=0.8)
            
            # If this step type has low historical success, add verification
            if not patterns or len(patterns) < 3:  # Not enough successful examples
                # Add verification step after this step
                verification_step = Step(
                    id=f"{step_id}_verify",
                    name=f"Verify {step.name}",
                    role=RoleType.VERIFIER,
                    description=f"Verify results of {step.name}",
                    budget=Budget(tokens_limit=1000, time_limit_seconds=10)
                )
                
                modifications.append(PlanModification(
                    modification_id=f"mod_verify_{step_id}",
                    modification_type="add_step",
                    target_step_id=step_id,
                    new_data={"step": verification_step},
                    reason=f"Low historical success rate for {role} steps - adding verification",
                    confidence=0.75
                ))
        
        return modifications
    
    def _rule_budget_inefficiency_adjusts_budget(
        self,
        plan: SelfModifyingPlan,
        step_results: Dict[str, Any]
    ) -> List[PlanModification]:
        """Rule: If step consistently uses less budget, reduce budget allocation.
        
        Args:
            plan: Self-modifying plan
            step_results: Current step execution results
            
        Returns:
            List of proposed modifications
        """
        if not self.seg_available:
            return []
        
        modifications = []
        
        # Check each completed step
        for step_id, result in step_results.items():
            if result.get("status") != "completed":
                continue
            
            step = next((s for s in plan.current_plan.steps if s.id == step_id), None)
            if not step or not step.budget:
                continue
            
            # Query SEG for this step's historical budget usage
            role = step.role.value if hasattr(step.role, 'value') else str(step.role)
            patterns = self.query_step_success_patterns(role, min_success_rate=0.7)
            
            # If this step consistently uses less budget, reduce allocation
            if patterns:
                avg_duration = sum(p.get("duration", 0.0) for p in patterns) / len(patterns)
                current_duration = result.get("duration_seconds", 0.0)
                
                if current_duration < avg_duration * 0.7:  # Using 30% less time
                    # Reduce budget by 20%
                    new_budget = Budget(
                        tokens_limit=int(step.budget.tokens_limit * 0.8),
                        time_limit_seconds=step.budget.time_limit_seconds * 0.8
                    )
                    
                    modifications.append(PlanModification(
                        modification_id=f"mod_budget_{step_id}",
                        modification_type="modify_step",
                        target_step_id=step_id,
                        new_data={"budget": new_budget},
                        reason=f"Step consistently uses less budget - reducing allocation",
                        confidence=0.80
                    ))
        
        return modifications
    
    def _rule_gate_failures_adds_gates(
        self,
        plan: SelfModifyingPlan,
        step_results: Dict[str, Any]
    ) -> List[PlanModification]:
        """Rule: If step fails gates historically, add quality gates.
        
        Args:
            plan: Self-modifying plan
            step_results: Current step execution results
            
        Returns:
            List of proposed modifications
        """
        if not self.seg_available:
            return []
        
        modifications = []
        
        # Check each step that failed gates
        for step_id, result in step_results.items():
            if result.get("gate_failures", 0) == 0:
                continue
            
            step = next((s for s in plan.current_plan.steps if s.id == step_id), None)
            if not step:
                continue
            
            # Query SEG for this step's historical gate failures
            role = step.role.value if hasattr(step.role, 'value') else str(step.role)
            patterns = self.query_step_success_patterns(role, min_success_rate=0.5)
            
            # If this step type has frequent gate failures, add quality gate
            if not patterns or len(patterns) < 5:  # Not enough successful examples
                # Add confidence gate
                confidence_gate = Gate(
                    name=f"confidence_check_{step_id}",
                    condition="output.confidence >= 0.80",
                    description="Ensure step confidence meets threshold"
                )
                
                modifications.append(PlanModification(
                    modification_id=f"mod_gate_{step_id}",
                    modification_type="add_gate",
                    target_step_id=step_id,
                    new_data={"gate": confidence_gate},
                    reason=f"Frequent gate failures for {role} steps - adding quality gate",
                    confidence=0.70
                ))
        
        return modifications
    
    def _rule_similar_plans_suggests_steps(
        self,
        plan: SelfModifyingPlan,
        step_results: Dict[str, Any]
    ) -> List[PlanModification]:
        """Rule: Query similar plans and suggest missing steps.
        
        Args:
            plan: Self-modifying plan
            step_results: Current step execution results
            
        Returns:
            List of proposed modifications
        """
        if not self.seg_available:
            return []
        
        modifications = []
        
        # Query for similar plan patterns
        patterns = self.query_plan_effectiveness_patterns(plan.current_plan.name)
        
        # If similar plans have additional steps, suggest adding them
        if patterns:
            # Get unique roles from patterns
            pattern_roles = set(p.get("role") for p in patterns if p.get("role"))
            current_roles = set(
                s.role.value if hasattr(s.role, 'value') else str(s.role)
                for s in plan.current_plan.steps
            )
            
            # Find missing roles
            missing_roles = pattern_roles - current_roles
            
            # Suggest adding steps for missing roles
            for role in missing_roles:
                if role == "verifier":  # Common missing role
                    verification_step = Step(
                        id=f"verify_{len(plan.current_plan.steps)}",
                        name="Final Verification",
                        role=RoleType.VERIFIER,
                        description="Verify all plan results",
                        budget=Budget(tokens_limit=2000, time_limit_seconds=15)
                    )
                    
                    modifications.append(PlanModification(
                        modification_id=f"mod_suggest_{role}",
                        modification_type="add_step",
                        target_step_id=None,  # Add at end
                        new_data={"step": verification_step},
                        reason=f"Similar plans include {role} step - suggesting addition",
                        confidence=0.65
                    ))
        
        return modifications
    
    def apply_modifications(
        self,
        plan: SelfModifyingPlan,
        modifications: List[PlanModification],
        execution_id: Optional[str] = None,
        plan_name: Optional[str] = None
    ):
        """
        Apply approved modifications to plan and create timeline entries.
        
        Args:
            plan: Self-modifying plan
            modifications: List of approved modifications
            execution_id: Optional execution identifier for timeline correlation
            plan_name: Optional plan name for timeline correlation
        """
        # Get plan name from plan if not provided
        if not plan_name and hasattr(plan, 'current_plan'):
            plan_name = plan.current_plan.name if hasattr(plan.current_plan, 'name') else "unknown"
        elif not plan_name:
            plan_name = "unknown"
        
        # Generate execution_id if not provided
        if not execution_id:
            from datetime import datetime
            execution_id = f"{plan_name}_{datetime.utcnow().isoformat()}"
        
        # Apply modifications via parent class
        super().apply_modifications(plan, modifications)
        
        # Create timeline entries for each modification if TCS enabled
        if self.tcs_integration and TCS_AVAILABLE:
            for mod in modifications:
                self.tcs_integration.create_depp_modification_entry(
                    modification=mod,
                    plan_name=plan_name,
                    execution_id=execution_id,
                    reason=mod.reason,
                    confidence=mod.confidence
                )

