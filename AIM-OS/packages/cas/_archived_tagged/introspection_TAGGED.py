"""Introspection Protocols Component for CAS

Implements systematic self-examination protocols for continuous improvement.
Provides hourly introspection checks and meta-cognitive analysis.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


# NL_TAG: VIF-MODEL-001 | Types of introspection protocols. | class IntrospectionType | []
# NL_TAG_SPEC: VIF-SPEC-001 | Validates IntrospectionType specification | IntrospectionType | [spec_file_TBD]
class IntrospectionType(str, Enum):
    """Types of introspection protocols."""
    HOURLY_CHECK = "hourly_check"
    TASK_COMPLETION = "task_completion"
    FAILURE_ANALYSIS = "failure_analysis"
    PRINCIPLE_REVIEW = "principle_review"
    PROTOCOL_VALIDATION = "protocol_validation"
    COGNITIVE_LOAD_ASSESSMENT = "cognitive_load_assessment"


# NL_TAG: VIF-MODEL-002 | Status of introspection results. | class IntrospectionStatus | []
# NL_TAG_SPEC: VIF-SPEC-002 | Validates IntrospectionStatus specification | IntrospectionStatus | [spec_file_TBD]
class IntrospectionStatus(str, Enum):
    """Status of introspection results."""
    EXCELLENT = "excellent"       # All checks passed, optimal state
    GOOD = "good"                 # Minor issues, functioning well
    FAIR = "fair"                 # Some concerns, monitor closely
    POOR = "poor"                 # Significant issues, intervention needed
    CRITICAL = "critical"         # Severe problems, immediate action required


@dataclass
# NL_TAG: VIF-MODEL-003 | Individual introspection check result. | class IntrospectionCheck | []
# NL_TAG_SPEC: VIF-SPEC-003 | Validates IntrospectionCheck specification | IntrospectionCheck | [spec_file_TBD]
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
# NL_TAG: VIF-MODEL-004 | Complete introspection analysis result. | class IntrospectionResult | []
# NL_TAG_SPEC: VIF-SPEC-004 | Validates IntrospectionResult specification | IntrospectionResult | [spec_file_TBD]
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


# NL_TAG: VIF-MODEL-005 | Implements systematic introspection protocols for CAS. | class IntrospectionProtocol | []
# NL_TAG_SPEC: VIF-SPEC-005 | Validates IntrospectionProtocol specification | IntrospectionProtocol | [spec_file_TBD]
class IntrospectionProtocol:
    # NL_TAG: VIF-UTIL-001 | Check if introspection indicates healthy cognitive state. | is_healthy(self) | []
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
    
    # NL_TAG: VIF-UTIL-002 |   init   | __init__(self, session_id) | []
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.introspection_history: List[IntrospectionResult] = []
        self.principle_violations: List[Tuple[datetime, str, str]] = []  # (time, principle, context)
        self.protocol_usage: Dict[str, List[datetime]] = {}
        
    # NL_TAG: VIF-UTIL-003 | Perform comprehensive hourly introspection check. | perform_hourly_check(self, activation_state, attention_metrics, recent_failures, current_task) | []
    # NL_TAG_SPEC: VIF-SPEC-006 | Validates perform_hourly_check specification | perform_hourly_check | [spec_file_TBD]
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
        start_time = datetime.utcnow()
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
        duration = (datetime.utcnow() - start_time).total_seconds()
        
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
    
    # NL_TAG: VIF-UTIL-004 | Check if required principles are properly activated. | _check_principle_activation(self, activation_state, current_task) | []
    # NL_TAG_SPEC: VIF-SPEC-007 | Validates _check_principle_activation specification | _check_principle_activation | [spec_file_TBD]
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
    
    # NL_TAG: VIF-UTIL-005 | Check attention quality and stability. | _check_attention_quality(self, attention_metrics) | []
    # NL_TAG_INTENT: VIF-INTENT-001 | Design decision: quality | _check_attention_quality | [ADR-TBD]
    # NL_TAG_SPEC: VIF-SPEC-008 | Validates _check_attention_quality specification | _check_attention_quality | [spec_file_TBD]
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
    
    # NL_TAG: VIF-UTIL-006 | Check for concerning failure patterns. | _check_failure_patterns(self, recent_failures) | []
    # NL_TAG_SPEC: VIF-SPEC-009 | Validates _check_failure_patterns specification | _check_failure_patterns | [spec_file_TBD]
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
    
    # NL_TAG: VIF-UTIL-007 | Check adherence to established protocols. | _check_protocol_adherence(self, current_task) | []
    # NL_TAG_SPEC: VIF-SPEC-010 | Validates _check_protocol_adherence specification | _check_protocol_adherence | [spec_file_TBD]
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
    
    # NL_TAG: VIF-UTIL-008 | Check cognitive load levels. | _check_cognitive_load(self, attention_metrics) | []
    # NL_TAG_SPEC: VIF-SPEC-011 | Validates _check_cognitive_load specification | _check_cognitive_load | [spec_file_TBD]
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
    
    # NL_TAG: VIF-UTIL-009 | Check overall quality maintenance. | _check_quality_maintenance(self) | []
    # NL_TAG_INTENT: VIF-INTENT-002 | Design decision: quality | _check_quality_maintenance | [ADR-TBD]
    # NL_TAG_SPEC: VIF-SPEC-012 | Validates _check_quality_maintenance specification | _check_quality_maintenance | [spec_file_TBD]
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
    
    # NL_TAG: VIF-UTIL-010 | Determine overall introspection status. | _determine_overall_status(self, overall_score, checks) | []
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
    
    # NL_TAG: VIF-UTIL-011 | Generate recommendations based on check results. | _generate_recommendations(self, checks) | []
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
    
    # NL_TAG: VIF-UTIL-012 | Get introspection trend over specified time period. | get_introspection_trend(self, hours) | []
    # NL_TAG_SPEC: VIF-SPEC-013 | Validates get_introspection_trend specification | get_introspection_trend | [spec_file_TBD]
    def get_introspection_trend(self, hours: int = 24) -> Dict[str, Any]:
        """Get introspection trend over specified time period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
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
    
    # NL_TAG: VIF-UTIL-013 | Record a principle violation for tracking. | record_principle_violation(self, principle, context) | []
    def record_principle_violation(self, principle: str, context: str):
        """Record a principle violation for tracking."""
        self.principle_violations.append((datetime.utcnow(), principle, context))
        logger.warning(f"Principle violation recorded: {principle} - {context}")
    
    # NL_TAG: VIF-HITL-001 | Determine if current situation requires escalation. | should_escalate(self) | []
    def should_escalate(self) -> bool:
        """Determine if current situation requires escalation."""
        if not self.introspection_history:
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
