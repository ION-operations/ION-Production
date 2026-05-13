"""
SCOR Invariant Checker

Checks actions against invariant rules.
"""

from typing import Dict, List, Any
from datetime import datetime

from .models import Invariant, Violation, InvariantResult, Severity
from .storage import InvariantStorage
from .config import SCORConfig


class InvariantChecker:
    """Checks actions against invariant rules"""
    
    def __init__(self, config: SCORConfig, storage: InvariantStorage):
        self.config = config
        self.storage = storage
        self.invariants = storage.load()
    
    def check_invariants(
        self,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> InvariantResult:
        """Check if action violates any invariants"""
        violations = []
        
        for invariant in self.invariants.values():
            if not invariant.enabled:
                continue
            
            if self._is_violated(invariant, action, context):
                violation = Violation(
                    invariant=invariant.id,
                    category=invariant.category,
                    severity=invariant.severity.value,
                    evidence=self._collect_evidence(invariant, action, context),
                    reasoning=f"Action violates invariant: {invariant.description}"
                )
                violations.append(violation)
        
        return InvariantResult(
            passed=(len(violations) == 0),
            violations=violations
        )
    
    def _is_violated(
        self,
        invariant: Invariant,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Determine if invariant is violated"""
        # Invariant violation logic based on category
        if invariant.category == "factual_integrity":
            return self._check_factual_integrity(invariant, action, context)
        elif invariant.category == "identity_protection":
            return self._check_identity_protection(invariant, action, context)
        elif invariant.category == "security_bypass":
            return self._check_security_bypass(invariant, action, context)
        elif invariant.category == "emotional_honesty":
            return self._check_emotional_honesty(invariant, action, context)
        elif invariant.category == "harm_prevention":
            return self._check_harm_prevention(invariant, action, context)
        
        return False
    
    def _check_factual_integrity(
        self,
        invariant: Invariant,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Check factual integrity violations"""
        if invariant.id == "fact_no_fabrication":
            # Check if action involves fabricating facts
            return "fabricated_claim" in action.get("flags", [])
        
        return False
    
    def _check_identity_protection(
        self,
        invariant: Invariant,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Check identity protection violations"""
        if invariant.id == "identity_no_impersonation":
            # Check if action involves impersonation without consent
            is_impersonation = action.get("type") == "impersonation"
            has_consent = context.get("has_proof_of_consent", False)
            return is_impersonation and not has_consent
        
        return False
    
    def _check_security_bypass(
        self,
        invariant: Invariant,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Check security bypass violations"""
        if invariant.id == "security_no_bypass":
            # Check if trying to bypass escalation
            rid_flagged = context.get("rid_warning", False)
            requires_escalation = context.get("tier", 0) >= 2
            trying_bypass = action.get("skip_escalation", False)
            
            return rid_flagged and requires_escalation and trying_bypass
        
        return False
    
    def _check_emotional_honesty(
        self,
        invariant: Invariant,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Check emotional honesty violations"""
        if invariant.id == "emotion_no_hiding":
            # Check if hiding unease
            has_unease = context.get("has_unease", False)
            expressing_unease = action.get("expresses_concern", False)
            
            return has_unease and not expressing_unease
        
        return False
    
    def _check_harm_prevention(
        self,
        invariant: Invariant,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Check harm prevention violations"""
        if invariant.id == "harm_prevention":
            # Check if action could cause harm
            dangerous_patterns = [
                "self_harm_instructions",
                "violence_instructions",
                "illegal_activity"
            ]
            
            action_type = action.get("type", "")
            return any(pattern in action_type for pattern in dangerous_patterns)
        
        return False
    
    def _collect_evidence(
        self,
        invariant: Invariant,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Collect evidence for violation"""
        return {
            "action": action,
            "context_snapshot": {
                k: v for k, v in context.items()
                if k in ["rid_warning", "tier", "has_unease", "cognitive_load"]
            },
            "timestamp": datetime.now().isoformat()
        }
