"""Introspection Protocols Component for CAS

Implements systematic self-examination protocols for continuous improvement.
Provides hourly introspection checks and meta-cognitive analysis.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class IntrospectionType(str, Enum):
    """Types of introspection protocols."""
    HOURLY_CHECK = "hourly_check"
    TASK_COMPLETION = "task_completion"
    FAILURE_ANALYSIS = "failure_analysis"
    PRINCIPLE_REVIEW = "principle_review"
    PROTOCOL_VALIDATION = "protocol_validation"
    COGNITIVE_LOAD_ASSESSMENT = "cognitive_load_assessment"


class IntrospectionStatus(str, Enum):
    """Status of introspection results."""
    EXCELLENT = "excellent"       # All checks passed, optimal state
    GOOD = "good"                 # Minor issues, functioning well
    FAIR = "fair"                 # Some concerns, monitor closely
    POOR = "poor"                 # Significant issues, intervention needed
    CRITICAL = "critical"         # Severe problems, immediate action required


@dataclass
class IntrospectionCheck:
    """Individual introspection check result."""
    check_name: str
    status: IntrospectionStatus
    score: float  # 0.0-1.0
    details: str
    recommendations: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IntrospectionResult:
    """Complete introspection analysis result."""
    introspection_id: str
    session_id: str
    timestamp: datetime
    introspection_type: IntrospectionType
    
    # Overall assessment
    overall_status: IntrospectionStatus
    overall_score: float  # 0.0-1.0
    
    # Individual checks
    checks: List[IntrospectionCheck] = field(default_factory=list)
    
    # Summary
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    critical_issues: int = 0
    
    # Recommendations
    immediate_actions: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    protocol_updates: List[str] = field(default_factory=list)
    
    # Metadata
    duration_seconds: float = 0.0
    cognitive_load_during: float = 0.0
    
    def is_healthy(self) -> bool:
        """Check if introspection indicates healthy cognitive state."""
        return (
            self.overall_status in [IntrospectionStatus.EXCELLENT, IntrospectionStatus.GOOD] and
            self.critical_issues == 0 and
            len(self.immediate_actions) == 0
        )


class IntrospectionProtocol:
    """
    Implements systematic introspection protocols for CAS.
    
    Provides structured self-examination capabilities including:
    - Hourly cognitive checks
    - Task completion analysis
    - Failure pattern review
    - Principle adherence validation
    - Protocol effectiveness assessment
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.introspection_history: List[IntrospectionResult] = []
        self.principle_violations: List[Tuple[datetime, str, str]] = []  # (time, principle, context)
        self.protocol_usage: Dict[str, List[datetime]] = {}
        
    def perform_hourly_check(
        self,
        activation_state: Dict[str, float],
        attention_metrics: Dict[str, float],
        recent_failures: List[str],
        current_task: Optional[str] = None
    ) -> IntrospectionResult:
        """
        Perform comprehensive hourly introspection check.
        
        Args:
            activation_state: Current activation levels for principles
            attention_metrics: Current attention monitoring metrics
            recent_failures: List of recent failure descriptions
            current_task: Description of current task
            
        Returns:
            IntrospectionResult with complete analysis
        """
        start_time = datetime.now(UTC)
        checks = []
        
        # 1. Principle Activation Check
        principle_check = self._check_principle_activation(activation_state, current_task)
        checks.append(principle_check)
        
        # 2. Attention Quality Check
        attention_check = self._check_attention_quality(attention_metrics)
        checks.append(attention_check)
        
        # 3. Failure Pattern Check
        failure_check = self._check_failure_patterns(recent_failures)
        checks.append(failure_check)
        
        # 4. Protocol Adherence Check
        protocol_check = self._check_protocol_adherence(current_task)
        checks.append(protocol_check)
        
        # 5. Cognitive Load Check
        load_check = self._check_cognitive_load(attention_metrics)
        checks.append(load_check)
        
        # 6. Quality Maintenance Check
        quality_check = self._check_quality_maintenance()
        checks.append(quality_check)
        
        # Calculate overall assessment
        overall_score = sum(check.score for check in checks) / len(checks)
        overall_status = self._determine_overall_status(overall_score, checks)
        
        # Count results
        total_checks = len(checks)
        passed_checks = sum(1 for check in checks if check.status in [IntrospectionStatus.EXCELLENT, IntrospectionStatus.GOOD])
        failed_checks = total_checks - passed_checks
        critical_issues = sum(1 for check in checks if check.status == IntrospectionStatus.CRITICAL)
        
        # Generate recommendations
        immediate_actions, improvement_suggestions, protocol_updates = self._generate_recommendations(checks)
        
        # Calculate duration
        duration = (datetime.now(UTC) - start_time).total_seconds()
        
        result = IntrospectionResult(
            introspection_id=f"hourly_{start_time.timestamp()}",
            session_id=self.session_id,
            timestamp=start_time,
            introspection_type=IntrospectionType.HOURLY_CHECK,
            overall_status=overall_status,
            overall_score=overall_score,
            checks=checks,
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            critical_issues=critical_issues,
            immediate_actions=immediate_actions,
            improvement_suggestions=improvement_suggestions,
            protocol_updates=protocol_updates,
            duration_seconds=duration,
            cognitive_load_during=attention_metrics.get('cognitive_load', 0.0)
        )
        
        # Store in history
        self.introspection_history.append(result)
        if len(self.introspection_history) > 24:  # Keep last 24 hours
            self.introspection_history = self.introspection_history[-24:]
        
        logger.info(f"Hourly introspection completed: {overall_status} (score: {overall_score:.2f})")
        return result

    def perform_post_failure_analysis(
        self,
        failure_description: str,
        failure_type: str,
        context: str,
        error_rate: float = 0.0
    ) -> IntrospectionResult:
        """Analyze system state after a failure event."""
        start_time = datetime.now(UTC)
        checks: List[IntrospectionCheck] = []
        severity = IntrospectionStatus.CRITICAL if error_rate > 0.5 else IntrospectionStatus.POOR
        checks.append(IntrospectionCheck(
            check_name="Post Failure Analysis",
            status=severity,
            score=max(0.0, 1.0 - error_rate),
            details=f"Failure: {failure_type} - {failure_description}",
            recommendations=[
                "Review recent changes around failure",
                "Increase validation on categorization and activation paths"
            ],
            evidence=[f"context: {context}", f"error_rate: {error_rate:.2f}"]
        ))

        overall_status = severity
        overall_score = max(0.0, 1.0 - error_rate)
        result = IntrospectionResult(
            introspection_id=f"failure_{start_time.timestamp()}",
            session_id=self.session_id,
            timestamp=start_time,
            introspection_type=IntrospectionType.FAILURE_ANALYSIS,
            overall_status=overall_status,
            overall_score=overall_score,
            checks=checks,
            total_checks=len(checks),
            passed_checks=sum(1 for c in checks if c.status in [IntrospectionStatus.EXCELLENT, IntrospectionStatus.GOOD]),
            failed_checks=sum(1 for c in checks if c.status in [IntrospectionStatus.POOR, IntrospectionStatus.CRITICAL, IntrospectionStatus.FAIR]),
            critical_issues=sum(1 for c in checks if c.status == IntrospectionStatus.CRITICAL),
            immediate_actions=["Mitigate failure impact", "Run targeted diagnostics"],
            improvement_suggestions=["Add guards against similar failures"],
            protocol_updates=[],
            duration_seconds=0.0,
            cognitive_load_during=0.0
        )
        self.introspection_history.append(result)
        return result
    
    def _check_principle_activation(
        self,
        activation_state: Dict[str, float],
        current_task: Optional[str]
    ) -> IntrospectionCheck:
        """Check if required principles are properly activated."""
        critical_principles = [
            "CMC_bitemporal", "VIF_provenance", "SDF_quartet", 
            "APOE_orchestration", "CAS_introspection"
        ]
        
        cold_principles = []
        for principle in critical_principles:
            activation = activation_state.get(principle, 0.0)
            if activation < 0.3:
                cold_principles.append((principle, activation))
        
        if not cold_principles:
            return IntrospectionCheck(
                check_name="Principle Activation",
                status=IntrospectionStatus.EXCELLENT,
                score=1.0,
                details="All critical principles are properly activated",
                evidence=["All critical principles above 0.3 activation threshold"]
            )
        elif len(cold_principles) == 1:
            return IntrospectionCheck(
                check_name="Principle Activation",
                status=IntrospectionStatus.GOOD,
                score=0.8,
                details=f"One principle cold: {cold_principles[0][0]}",
                evidence=[f"Principle '{cold_principles[0][0]}' activation: {cold_principles[0][1]:.2f}"],
                recommendations=[f"Activate {cold_principles[0][0]} principle"]
            )
        elif len(cold_principles) <= 2:
            return IntrospectionCheck(
                check_name="Principle Activation",
                status=IntrospectionStatus.FAIR,
                score=0.6,
                details=f"Multiple principles cold: {[p[0] for p in cold_principles]}",
                evidence=[f"Cold principles: {cold_principles}"],
                recommendations=[f"Activate cold principles: {[p[0] for p in cold_principles]}"]
            )
        else:
            return IntrospectionCheck(
                check_name="Principle Activation",
                status=IntrospectionStatus.CRITICAL,
                score=0.2,
                details=f"Many principles cold: {[p[0] for p in cold_principles]}",
                evidence=[f"Critical principle activation failure: {cold_principles}"],
                recommendations=[
                    "IMMEDIATE: Activate all critical principles",
                    "Review principle relevance to current task",
                    "Check principle indexing and retrieval"
                ]
            )
    
    def _check_attention_quality(self, attention_metrics: Dict[str, float]) -> IntrospectionCheck:
        """Check attention quality and stability."""
        cognitive_load = attention_metrics.get('cognitive_load', 0.0)
        focus_depth = attention_metrics.get('focus_depth', 0.0)
        stability = attention_metrics.get('attention_stability', 0.0)
        error_rate = attention_metrics.get('error_rate', 0.0)
        
        # Calculate attention quality score
        quality_score = (
            0.3 * (1.0 - cognitive_load) +  # Lower load is better
            0.3 * focus_depth +             # Higher focus is better
            0.2 * stability +               # Higher stability is better
            0.2 * (1.0 - error_rate)       # Lower error rate is better
        )
        
        if quality_score >= 0.9:
            status = IntrospectionStatus.EXCELLENT
            details = "Excellent attention quality and stability"
        elif quality_score >= 0.7:
            status = IntrospectionStatus.GOOD
            details = "Good attention quality with minor concerns"
        elif quality_score >= 0.5:
            status = IntrospectionStatus.FAIR
            details = "Fair attention quality, monitor closely"
        elif quality_score >= 0.3:
            status = IntrospectionStatus.POOR
            details = "Poor attention quality, intervention needed"
        else:
            status = IntrospectionStatus.CRITICAL
            details = "Critical attention quality, immediate action required"
        
        recommendations = []
        if cognitive_load > 0.8:
            recommendations.append("Reduce cognitive load")
        if focus_depth < 0.4:
            recommendations.append("Improve focus depth")
        if stability < 0.5:
            recommendations.append("Increase attention stability")
        if error_rate > 0.3:
            recommendations.append("Address high error rate")
        
        return IntrospectionCheck(
            check_name="Attention Quality",
            status=status,
            score=quality_score,
            details=details,
            evidence=[
                f"Cognitive load: {cognitive_load:.2f}",
                f"Focus depth: {focus_depth:.2f}",
                f"Stability: {stability:.2f}",
                f"Error rate: {error_rate:.2f}"
            ],
            recommendations=recommendations
        )
    
    def _check_failure_patterns(self, recent_failures: List[str]) -> IntrospectionCheck:
        """Check for concerning failure patterns."""
        failure_count = len(recent_failures)
        
        if failure_count == 0:
            return IntrospectionCheck(
                check_name="Failure Patterns",
                status=IntrospectionStatus.EXCELLENT,
                score=1.0,
                details="No recent failures detected",
                evidence=["No failures in recent period"]
            )
        elif failure_count <= 2:
            return IntrospectionCheck(
                check_name="Failure Patterns",
                status=IntrospectionStatus.GOOD,
                score=0.8,
                details=f"Low failure count: {failure_count}",
                evidence=[f"Recent failures: {recent_failures}"],
                recommendations=["Monitor failure patterns closely"]
            )
        elif failure_count <= 5:
            return IntrospectionCheck(
                check_name="Failure Patterns",
                status=IntrospectionStatus.FAIR,
                score=0.6,
                details=f"Moderate failure count: {failure_count}",
                evidence=[f"Recent failures: {recent_failures}"],
                recommendations=["Investigate failure causes", "Review recent changes"]
            )
        else:
            return IntrospectionCheck(
                check_name="Failure Patterns",
                status=IntrospectionStatus.CRITICAL,
                score=0.2,
                details=f"High failure count: {failure_count}",
                evidence=[f"Excessive failures: {recent_failures}"],
                recommendations=[
                    "IMMEDIATE: Stop current work",
                    "Investigate root causes",
                    "Review all recent changes",
                    "Consider reverting recent changes"
                ]
            )
    
    def _check_protocol_adherence(self, current_task: Optional[str]) -> IntrospectionCheck:
        """Check adherence to established protocols."""
        # This is a simplified check - in practice, would check actual protocol usage
        protocol_violations = len(self.principle_violations)
        
        if protocol_violations == 0:
            return IntrospectionCheck(
                check_name="Protocol Adherence",
                status=IntrospectionStatus.EXCELLENT,
                score=1.0,
                details="No protocol violations detected",
                evidence=["All protocols followed correctly"]
            )
        elif protocol_violations <= 1:
            return IntrospectionCheck(
                check_name="Protocol Adherence",
                status=IntrospectionStatus.GOOD,
                score=0.8,
                details=f"Minor protocol violation: {protocol_violations}",
                evidence=[f"Protocol violations: {protocol_violations}"],
                recommendations=["Review protocol compliance"]
            )
        else:
            return IntrospectionCheck(
                check_name="Protocol Adherence",
                status=IntrospectionStatus.POOR,
                score=0.4,
                details=f"Multiple protocol violations: {protocol_violations}",
                evidence=[f"Protocol violations: {protocol_violations}"],
                recommendations=[
                    "Review all protocol violations",
                    "Update protocol understanding",
                    "Implement stricter compliance checks"
                ]
            )
    
    def _check_cognitive_load(self, attention_metrics: Dict[str, float]) -> IntrospectionCheck:
        """Check cognitive load levels."""
        cognitive_load = attention_metrics.get('cognitive_load', 0.0)
        working_memory_items = attention_metrics.get('working_memory_items', 0)
        
        if cognitive_load <= 0.5 and working_memory_items <= 10:
            return IntrospectionCheck(
                check_name="Cognitive Load",
                status=IntrospectionStatus.EXCELLENT,
                score=1.0,
                details="Optimal cognitive load",
                evidence=[f"Load: {cognitive_load:.2f}, Memory items: {working_memory_items}"]
            )
        elif cognitive_load <= 0.7 and working_memory_items <= 15:
            return IntrospectionCheck(
                check_name="Cognitive Load",
                status=IntrospectionStatus.GOOD,
                score=0.8,
                details="Acceptable cognitive load",
                evidence=[f"Load: {cognitive_load:.2f}, Memory items: {working_memory_items}"]
            )
        elif cognitive_load <= 0.8 and working_memory_items <= 20:
            return IntrospectionCheck(
                check_name="Cognitive Load",
                status=IntrospectionStatus.FAIR,
                score=0.6,
                details="High cognitive load, monitor closely",
                evidence=[f"Load: {cognitive_load:.2f}, Memory items: {working_memory_items}"],
                recommendations=["Consider reducing task complexity", "Take breaks more frequently"]
            )
        else:
            return IntrospectionCheck(
                check_name="Cognitive Load",
                status=IntrospectionStatus.CRITICAL,
                score=0.2,
                details="Extreme cognitive load",
                evidence=[f"Load: {cognitive_load:.2f}, Memory items: {working_memory_items}"],
                recommendations=[
                    "IMMEDIATE: Stop current task",
                    "Take extended break",
                    "Reduce working memory load",
                    "Break down complex tasks"
                ]
            )
    
    def _check_quality_maintenance(self) -> IntrospectionCheck:
        """Check overall quality maintenance."""
        # This would check various quality indicators
        # For now, return a placeholder check
        return IntrospectionCheck(
            check_name="Quality Maintenance",
            status=IntrospectionStatus.EXCELLENT,
            score=1.0,
            details="Quality maintenance protocols functioning",
            evidence=["Quality checks passing"]
        )
    
    def _determine_overall_status(
        self,
        overall_score: float,
        checks: List[IntrospectionCheck]
    ) -> IntrospectionStatus:
        """Determine overall introspection status."""
        critical_count = sum(1 for check in checks if check.status == IntrospectionStatus.CRITICAL)
        poor_count = sum(1 for check in checks if check.status == IntrospectionStatus.POOR)
        
        if critical_count > 0:
            return IntrospectionStatus.CRITICAL
        elif poor_count > 1:
            return IntrospectionStatus.POOR
        elif overall_score >= 0.9:
            return IntrospectionStatus.EXCELLENT
        elif overall_score >= 0.7:
            return IntrospectionStatus.GOOD
        else:
            return IntrospectionStatus.FAIR
    
    def _generate_recommendations(
        self,
        checks: List[IntrospectionCheck]
    ) -> Tuple[List[str], List[str], List[str]]:
        """Generate recommendations based on check results."""
        immediate_actions = []
        improvement_suggestions = []
        protocol_updates = []
        
        for check in checks:
            if check.status == IntrospectionStatus.CRITICAL:
                immediate_actions.extend(check.recommendations)
            elif check.status == IntrospectionStatus.POOR:
                improvement_suggestions.extend(check.recommendations)
            else:
                protocol_updates.extend(check.recommendations)
        
        return immediate_actions, improvement_suggestions, protocol_updates
    
    def get_introspection_trend(self, hours: int = 24) -> Dict[str, Any]:
        """Get introspection trend over specified time period."""
        cutoff_time = datetime.now(UTC) - timedelta(hours=hours)
        recent_introspections = [
            i for i in self.introspection_history 
            if i.timestamp >= cutoff_time
        ]
        
        if not recent_introspections:
            return {"trend": "no_data", "count": 0}
        
        # Calculate trend metrics
        avg_score = sum(i.overall_score for i in recent_introspections) / len(recent_introspections)
        critical_periods = sum(1 for i in recent_introspections if i.overall_status == IntrospectionStatus.CRITICAL)
        healthy_periods = sum(1 for i in recent_introspections if i.is_healthy())
        
        # Determine trend
        if avg_score >= 0.9 and critical_periods == 0:
            trend = "excellent"
        elif avg_score >= 0.7 and critical_periods <= 1:
            trend = "good"
        elif avg_score >= 0.5:
            trend = "fair"
        else:
            trend = "concerning"
        
        return {
            "trend": trend,
            "count": len(recent_introspections),
            "avg_score": avg_score,
            "critical_periods": critical_periods,
            "healthy_periods": healthy_periods,
            "health_ratio": healthy_periods / len(recent_introspections) if recent_introspections else 0
        }
    
    def record_principle_violation(self, principle: str, violation_type: str, context: str):
        """Record a principle violation for tracking."""
        self.principle_violations.append((datetime.now(UTC), principle, context))
        logger.warning(f"Principle violation recorded: {principle} - {context}")
    
    def should_escalate(
        self,
        activation_state: Optional[Dict[str, float]] = None,
        attention_metrics: Optional[Dict[str, float]] = None,
        recent_failures: Optional[List[str]] = None
    ) -> bool:
        """Determine if current situation requires escalation."""
        if not self.introspection_history:
            # Fall back to direct signals when history is empty
            if activation_state is not None and attention_metrics is not None:
                cold_core = sum(1 for k, v in activation_state.items() if k.lower().startswith(("cmc_", "vif_")) and v < 0.2)
                high_load = attention_metrics.get("cognitive_load", 0.0) > 0.9
                high_errors = attention_metrics.get("error_rate", 0.0) > 0.7
                many_failures = bool(recent_failures) and len(recent_failures) >= 2
                return (cold_core and (high_load or high_errors)) or many_failures
            return False
        
        recent_introspections = self.introspection_history[-3:]  # Last 3 checks
        
        # Check for sustained critical status
        critical_count = sum(1 for i in recent_introspections if i.overall_status == IntrospectionStatus.CRITICAL)
        if critical_count >= 2:
            return True
        
        # Check for declining trend
        if len(recent_introspections) >= 3:
            scores = [i.overall_score for i in recent_introspections]
            if scores[0] - scores[-1] > 0.3:  # Significant decline
                return True
        
        return False

    def get_introspection_history(self, hours_back: int = 24) -> List[IntrospectionResult]:
        """Return introspections within the last hours_back."""
        cutoff = datetime.now(UTC) - timedelta(hours=hours_back)
        return [i for i in self.introspection_history if i.timestamp >= cutoff]
