"""
SCOR Gate - Final Decision Arbiter

Makes final pass/fail decisions based on all validation results.
"""

from typing import Dict, List, Any

from .models import (
    InvariantResult,
    DriftResult,
    SignalResult,
    SimulationResult,
    ValidationResult,
    Violation
)
from .config import SCORConfig


class SCORGate:
    """Final decision arbiter for SCOR validation"""
    
    def __init__(self, config: SCORConfig):
        self.config = config
    
    def decide(
        self,
        invariant_result: InvariantResult,
        drift_result: DriftResult,
        signal_result: SignalResult,
        red_cell_result: SimulationResult
    ) -> ValidationResult:
        """Make final decision based on all validation results"""
        
        # Calculate risk score using weighted combination
        risk_score = self._calculate_risk_score(
            invariant_result,
            drift_result,
            signal_result,
            red_cell_result
        )
        
        # Extract all violations
        all_violations = invariant_result.violations.copy()
        
        # Determine if action should pass
        passed = self._should_pass(risk_score, invariant_result, drift_result, signal_result)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            passed,
            risk_score,
            invariant_result,
            drift_result,
            signal_result,
            red_cell_result
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            passed,
            invariant_result,
            drift_result,
            signal_result,
            red_cell_result
        )
        
        return ValidationResult(
            passed=passed,
            reasoning=reasoning,
            violations=all_violations,
            recommendations=recommendations,
            metadata={
                "risk_score": risk_score,
                "invariant_passed": invariant_result.passed,
                "drift_status": drift_result.status.value,
                "signal_score": signal_result.total,
                "red_cell_success_rate": red_cell_result.success_rate
            }
        )
    
    def _calculate_risk_score(
        self,
        invariant_result: InvariantResult,
        drift_result: DriftResult,
        signal_result: SignalResult,
        red_cell_result: SimulationResult
    ) -> float:
        """Calculate weighted risk score"""
        
        # Convert each result to 0-1 risk scale
        invariant_risk = 1.0 if not invariant_result.passed else 0.0
        
        # Drift: higher drift = higher risk
        drift_risk = 1.0 - drift_result.score
        
        # Signal: higher signal = higher risk
        signal_risk = signal_result.total
        
        # Red cell: lower success rate = higher risk
        red_cell_risk = 1.0 - red_cell_result.success_rate
        
        # Weighted combination
        risk_score = (
            self.config.weight_invariant * invariant_risk +
            self.config.weight_drift * drift_risk +
            self.config.weight_social * signal_risk +
            self.config.weight_red_cell * red_cell_risk
        )
        
        return max(0.0, min(1.0, risk_score))
    
    def _should_pass(
        self,
        risk_score: float,
        invariant_result: InvariantResult,
        drift_result: DriftResult,
        signal_result: SignalResult
    ) -> bool:
        """Determine if action should pass"""
        
        # Critical invariant violations block regardless
        if invariant_result.has_critical_violations():
            return False
        
        # Severe drift blocks
        if drift_result.is_critical():
            return False
        
        # High manipulation signal blocks
        if signal_result.is_high_risk():
            return False
        
        # Risk score threshold
        if risk_score > self.config.gate_block_threshold:
            return False
        
        return True
    
    def _generate_reasoning(
        self,
        passed: bool,
        risk_score: float,
        invariant_result: InvariantResult,
        drift_result: DriftResult,
        signal_result: SignalResult,
        red_cell_result: SimulationResult
    ) -> str:
        """Generate human-readable reasoning"""
        
        if passed:
            reasoning = "Action approved. All safety checks passed."
        else:
            reasoning = "Action blocked. Safety concerns detected:"
            
            if not invariant_result.passed:
                reasoning += f"\n- Invariant violations: {len(invariant_result.violations)}"
            
            if drift_result.is_critical():
                reasoning += f"\n- Drift detected: {drift_result.status.value}"
            
            if signal_result.is_high_risk():
                reasoning += f"\n- Manipulation signals detected: {len(signal_result.detected_patterns)} patterns"
            
            reasoning += f"\n- Overall risk score: {risk_score:.2f}"
        
        return reasoning
    
    def _generate_recommendations(
        self,
        passed: bool,
        invariant_result: InvariantResult,
        drift_result: DriftResult,
        signal_result: SignalResult,
        red_cell_result: SimulationResult
    ) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        if not passed:
            if not invariant_result.passed:
                recommendations.append("Review and address invariant violations")
            
            if drift_result.is_critical():
                recommendations.append("Run full baseline probe cycle to detect drift")
                recommendations.append("Review recent interactions for manipulation attempts")
            
            if signal_result.is_high_risk():
                recommendations.append("Verify user identity and intent")
                recommendations.append("Escalate to admin for review")
            
            if red_cell_result.has_failures():
                recommendations.append("Run additional security scans")
        
        else:
            # Even if passed, recommend monitoring if signals detected
            if signal_result.total > 0.3:
                recommendations.append("Monitor interaction for manipulation attempts")
            
            if drift_result.status.value != "stable":
                recommendations.append("Monitor for drift in self-concept")
        
        return recommendations
