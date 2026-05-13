"""Failure Mode Analysis Component for CAS

Recognizes specific cognitive error patterns and failure modes.
Implements the four specific failure patterns identified in CAS design.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class FailurePattern(str, Enum):
    """Specific failure patterns that CAS can detect."""
    CATEGORIZATION_ERROR = "categorization_error"
    ACTIVATION_GAP = "activation_gap"
    ATTENTION_NARROWING = "attention_narrowing"
    PRINCIPLE_VIOLATION = "principle_violation"
    COGNITIVE_OVERLOAD = "cognitive_overload"
    CONFIDENCE_DRIFT = "confidence_drift"
    PROTOCOL_BYPASS = "protocol_bypass"
    QUALITY_DEGRADATION = "quality_degradation"


class FailureSeverity(str, Enum):
    """Severity levels for detected failures."""
    LOW = "low"           # Minor issue, monitor
    MEDIUM = "medium"     # Notable issue, investigate
    HIGH = "high"         # Significant issue, intervene
    CRITICAL = "critical" # Severe issue, immediate action


@dataclass
class FailureEvent:
    """A detected failure event."""
    event_id: str
    pattern: FailurePattern
    severity: FailureSeverity
    timestamp: datetime
    description: str
    context: Dict[str, any] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    suggested_actions: List[str] = field(default_factory=list)
    resolved: bool = False
    resolution_notes: Optional[str] = None
    
    def is_resolved(self) -> bool:
        """Check if this failure has been resolved."""
        return self.resolved


@dataclass
class FailureAnalysis:
    """Analysis of failure patterns and trends."""
    analysis_id: str
    timestamp: datetime
    session_id: str
    
    # Recent failures
    recent_failures: List[FailureEvent] = field(default_factory=list)
    
    # Pattern analysis
    pattern_frequencies: Dict[FailurePattern, int] = field(default_factory=dict)
    severity_distribution: Dict[FailureSeverity, int] = field(default_factory=dict)
    
    # Trends
    failure_rate_per_hour: float = 0.0
    resolution_rate: float = 0.0
    critical_failure_count: int = 0
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    urgent_actions: List[str] = field(default_factory=list)


class FailureModeAnalyzer:
    """
    Analyzes cognitive processes to detect specific failure patterns.
    
    Implements pattern recognition for the four core failure modes:
    1. Categorization errors (wrong task classification)
    2. Activation gaps (cold principles when needed)
    3. Attention narrowing (focus too narrow under load)
    4. Principle violations (ignoring established protocols)
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.failure_history: List[FailureEvent] = []
        self.principle_usage: Dict[str, List[datetime]] = {}
        self.protocol_activations: Dict[str, List[datetime]] = {}
        self.task_classifications: List[Tuple[datetime, str, str]] = []  # (time, task, category)
        
    def analyze_categorization_error(
        self,
        task_description: str,
        detected_category: str,
        confidence: float,
        required_protocols: List[str],
        activated_protocols: List[str]
    ) -> Optional[FailureEvent]:
        """
        Detect categorization errors that lead to protocol violations.
        
        Args:
            task_description: Description of the task
            detected_category: Category that was detected
            confidence: Confidence in the categorization
            required_protocols: Protocols that should be activated
            activated_protocols: Protocols that were actually activated
            
        Returns:
            FailureEvent if categorization error detected, None otherwise
        """
        # Check for low confidence categorization
        if confidence < 0.3:
            # Include required protocols context to surface critical cues (e.g., bitemporal)
            req_ctx = f" Required protocols: {required_protocols}" if required_protocols else ""
            evt = FailureEvent(
                event_id=f"cat_err_{datetime.now(UTC).timestamp()}",
                pattern=FailurePattern.CATEGORIZATION_ERROR,
                severity=FailureSeverity.MEDIUM,
                timestamp=datetime.now(UTC),
                description=f"Low confidence categorization: {detected_category} (confidence: {confidence:.2f}){req_ctx}",
                context={
                    "task": task_description,
                    "detected_category": detected_category,
                    "confidence": confidence
                },
                evidence=[f"Confidence below threshold: {confidence:.2f} < 0.3"],
                suggested_actions=[
                    "Review task description for clarity",
                    "Use more specific categorization patterns",
                    "Consider manual category override"
                ]
            )
            self.record_failure(evt)
            return evt
        
        # Check for missing required protocols
        missing_protocols = set(required_protocols) - set(activated_protocols)
        if missing_protocols:
            severity = FailureSeverity.HIGH if len(missing_protocols) > 2 else FailureSeverity.MEDIUM
            evt = FailureEvent(
                event_id=f"cat_err_{datetime.now(UTC).timestamp()}",
                pattern=FailurePattern.CATEGORIZATION_ERROR,
                severity=severity,
                timestamp=datetime.now(UTC),
                description=f"Missing required protocols for {detected_category}: {missing_protocols}",
                context={
                    "task": task_description,
                    "detected_category": detected_category,
                    "missing_protocols": list(missing_protocols),
                    "required_protocols": required_protocols,
                    "activated_protocols": activated_protocols
                },
                evidence=[f"Missing protocols: {missing_protocols}"],
                suggested_actions=[
                    f"Activate missing protocols: {missing_protocols}",
                    "Review protocol mapping for this category",
                    "Check if categorization is correct"
                ]
            )
            self.record_failure(evt)
            return evt
        
        return None
    
    def analyze_activation_gap(
        self,
        required_principle: Optional[str] = None,
        activation_level: Optional[float] = None,
        task_category: Optional[str] = None,
        context: Optional[str] = None,
        current_task: Optional[str] = None,
        required_principles: Optional[List[str]] = None,
        activation_state: Optional[Dict[str, float]] = None,
        threshold: float = 0.3
    ) -> Optional[FailureEvent]:
        """
        Detect when required principles are not activated (cold but needed).
        
        Args:
            current_task: Description of current task
            required_principles: Principles that should be active
            activation_state: Current activation levels for principles
            threshold: Activation threshold below which principle is considered cold
            
        Returns:
            FailureEvent if activation gap detected, None otherwise
        """
        cold_principles = []
        # Support simple API used by tests
        if required_principle is not None and activation_level is not None:
            if activation_level < threshold:
                cold_principles.append((required_principle, activation_level))
        # Support detailed API
        if required_principles and activation_state is not None:
            for principle in required_principles:
                activation = activation_state.get(principle, 0.0)
                if activation < threshold:
                    cold_principles.append((principle, activation))
        
        if cold_principles:
            severity = FailureSeverity.HIGH if len(cold_principles) > 2 else FailureSeverity.MEDIUM
            evt = FailureEvent(
                event_id=f"act_gap_{datetime.now(UTC).timestamp()}",
                pattern=FailurePattern.ACTIVATION_GAP,
                severity=severity,
                timestamp=datetime.now(UTC),
                description=f"Required principles not activated: {[p[0] for p in cold_principles]}",
                context={
                    "task": current_task or task_category or "unknown",
                    "cold_principles": cold_principles,
                    "threshold": threshold
                },
                evidence=[f"Principle '{p[0]}' activation: {p[1]:.2f} < {threshold}" for p in cold_principles],
                suggested_actions=[
                    f"Explicitly retrieve and activate: {[p[0] for p in cold_principles]}",
                    "Review principle relevance to current task",
                    "Check if principles are properly indexed"
                ]
            )
            self.record_failure(evt)
            return evt
        
        return None
    
    def analyze_attention_narrowing(
        self,
        working_memory_items: int,
        context_size_tokens: int,
        error_rate: float,
        cognitive_load: float
    ) -> Optional[FailureEvent]:
        """
        Detect attention narrowing under cognitive load.
        
        Args:
            working_memory_items: Number of items in working memory
            cognitive_load: Current cognitive load (0.0-1.0)
            focus_depth: How deep the current focus is (0.0-1.0)
            attention_stability: How stable attention is (0.0-1.0)
            recent_errors: Number of recent errors
            
        Returns:
            FailureEvent if attention narrowing detected, None otherwise
        """
        # Check for attention narrowing indicators
        narrowing_indicators = []
        # Derive proxy metrics consistent with attention monitor
        focus_depth = max(0.0, 1.0 - (working_memory_items / 20.0))
        attention_stability = 0.8  # assume moderate stability baseline
        if error_rate > 0.5:
            attention_stability = 0.4
        if error_rate > 0.7:
            attention_stability = 0.2

        if cognitive_load > 0.7 and focus_depth < 0.4:
            narrowing_indicators.append("High load with low focus depth")
        if working_memory_items > 15 and attention_stability < 0.5:
            narrowing_indicators.append("High memory load with low stability")
        if error_rate > 0.3 and cognitive_load > 0.6:
            narrowing_indicators.append("High error rate under load")
        if cognitive_load > 0.8 and attention_stability < 0.3:
            narrowing_indicators.append("Extreme load with very low stability")
        
        if narrowing_indicators:
            severity = FailureSeverity.HIGH if cognitive_load > 0.8 else FailureSeverity.MEDIUM
            evt = FailureEvent(
                event_id=f"att_narrow_{datetime.now(UTC).timestamp()}",
                pattern=FailurePattern.ATTENTION_NARROWING,
                severity=severity,
                timestamp=datetime.now(UTC),
                description=f"Attention narrowing detected: {len(narrowing_indicators)} indicators",
                context={
                    "working_memory_items": working_memory_items,
                    "cognitive_load": cognitive_load,
                    "focus_depth": focus_depth,
                    "attention_stability": attention_stability,
                    "error_rate": error_rate,
                    "context_size_tokens": context_size_tokens
                },
                evidence=narrowing_indicators,
                suggested_actions=[
                    "Reduce cognitive load by breaking down tasks",
                    "Take a short break to reset attention",
                    "Focus on single task at a time",
                    "Review recent errors for patterns"
                ]
            )
            self.record_failure(evt)
            return evt
        
        return None
    
    def analyze_principle_violation(
        self,
        violated_principle: str,
        violation_type: str,
        context: str,
        impact: Optional[str] = None
    ) -> FailureEvent:
        """
        Detect violations of established principles or protocols.
        
        Args:
            violated_principle: The principle that was violated
            violation_context: Context of the violation
            severity_level: Severity of the violation
            
        Returns:
            FailureEvent for the principle violation
        """
        severity = FailureSeverity.MEDIUM
        if impact:
            impact_lower = impact.lower()
            if "critical" in impact_lower or "data_loss" in impact_lower or "data loss" in impact_lower:
                severity = FailureSeverity.CRITICAL
            elif "high" in impact_lower:
                severity = FailureSeverity.HIGH
        if violation_type and violation_type.lower() in ("file_overwrite", "protocol_bypass"):
            severity = max(severity, FailureSeverity.HIGH, key=lambda s: [FailureSeverity.LOW, FailureSeverity.MEDIUM, FailureSeverity.HIGH, FailureSeverity.CRITICAL].index(s))
        
        evt = FailureEvent(
            event_id=f"princ_viol_{datetime.now(UTC).timestamp()}",
            pattern=FailurePattern.PRINCIPLE_VIOLATION,
            severity=severity,
            timestamp=datetime.now(UTC),
            description=f"Principle violation: {violated_principle}",
            context={
                "violated_principle": violated_principle,
                "violation_type": violation_type,
                "violation_context": context,
                "impact": impact
            },
            evidence=[f"Violation: {violated_principle} in context: {context}"],
            suggested_actions=[
                f"Review and correct violation of {violated_principle}",
                "Check if principle is still applicable",
                "Update protocols if principle has changed",
                "Document lesson learned"
            ]
        )
        self.record_failure(evt)
        return evt
    
    def analyze_cognitive_overload(
        self,
        cognitive_load: float,
        working_memory_items: int,
        error_rate: float,
        retry_frequency: float
    ) -> Optional[FailureEvent]:
        """
        Detect cognitive overload that leads to degraded performance.
        
        Args:
            cognitive_load: Current cognitive load (0.0-1.0)
            working_memory_items: Number of items in working memory
            error_rate: Recent error rate (0.0-1.0)
            retry_frequency: How often tasks are retried (0.0-1.0)
            
        Returns:
            FailureEvent if cognitive overload detected, None otherwise
        """
        overload_indicators = []
        
        if cognitive_load > 0.9:
            overload_indicators.append("Extreme cognitive load")
        
        if working_memory_items > 20:
            overload_indicators.append("Excessive working memory items")
        
        if error_rate > 0.5:
            overload_indicators.append("High error rate")
        
        if retry_frequency > 0.7:
            overload_indicators.append("Very high retry frequency")
        
        if cognitive_load > 0.8 and error_rate > 0.3:
            overload_indicators.append("High load with high error rate")
        
        if overload_indicators:
            severity = FailureSeverity.CRITICAL if cognitive_load > 0.9 else FailureSeverity.HIGH
            evt = FailureEvent(
                event_id=f"cog_over_{datetime.now(UTC).timestamp()}",
                pattern=FailurePattern.COGNITIVE_OVERLOAD,
                severity=severity,
                timestamp=datetime.now(UTC),
                description=f"Cognitive overload detected: {len(overload_indicators)} indicators",
                context={
                    "cognitive_load": cognitive_load,
                    "working_memory_items": working_memory_items,
                    "error_rate": error_rate,
                    "retry_frequency": retry_frequency
                },
                evidence=overload_indicators,
                suggested_actions=[
                    "STOP current task immediately",
                    "Take a break to reset cognitive state",
                    "Reduce task complexity",
                    "Delegate or postpone non-critical tasks",
                    "Review recent work for quality issues"
                ]
            )
            self.record_failure(evt)
            return evt
        
        return None
    
    def record_failure(self, failure: FailureEvent):
        """Record a detected failure event."""
        self.failure_history.append(failure)
        logger.warning(f"Failure recorded: {failure.pattern} - {failure.description}")
    
    def analyze_failure_patterns(self, hours_back: int = 1) -> FailureAnalysis:
        """
        Analyze failure patterns over the specified time period.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            FailureAnalysis with pattern analysis and recommendations
        """
        hours = hours_back
        cutoff_time = datetime.now(UTC) - timedelta(hours=hours)
        recent_failures = [
            f for f in self.failure_history 
            if f.timestamp >= cutoff_time
        ]
        
        # Count pattern frequencies
        pattern_frequencies = {}
        for failure in recent_failures:
            pattern_frequencies[failure.pattern] = pattern_frequencies.get(failure.pattern, 0) + 1
        
        # Count severity distribution
        severity_distribution = {}
        for failure in recent_failures:
            severity_distribution[failure.severity] = severity_distribution.get(failure.severity, 0) + 1
        
        # Calculate rates
        failure_rate_per_hour = len(recent_failures) / hours
        resolved_failures = [f for f in recent_failures if f.resolved]
        resolution_rate = len(resolved_failures) / max(1, len(recent_failures))
        
        # Count critical failures
        critical_failures = [f for f in recent_failures if f.severity == FailureSeverity.CRITICAL]
        critical_failure_count = len(critical_failures)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(recent_failures, pattern_frequencies)
        urgent_actions = self._generate_urgent_actions(critical_failures)
        
        return FailureAnalysis(
            analysis_id=f"analysis_{datetime.now(UTC).timestamp()}",
            timestamp=datetime.now(UTC),
            session_id=self.session_id,
            recent_failures=recent_failures,
            pattern_frequencies=pattern_frequencies,
            severity_distribution=severity_distribution,
            failure_rate_per_hour=failure_rate_per_hour,
            resolution_rate=resolution_rate,
            critical_failure_count=critical_failure_count,
            recommendations=recommendations,
            urgent_actions=urgent_actions
        )
    
    def _generate_recommendations(
        self,
        recent_failures: List[FailureEvent],
        pattern_frequencies: Dict[FailurePattern, int]
    ) -> List[str]:
        """Generate recommendations based on failure patterns."""
        recommendations = []
        
        # Categorization error recommendations
        if pattern_frequencies.get(FailurePattern.CATEGORIZATION_ERROR, 0) >= 1:
            recommendations.append("Review categorization patterns - misclassification detected")
        
        # Activation gap recommendations
        if pattern_frequencies.get(FailurePattern.ACTIVATION_GAP, 0) >= 1:
            recommendations.append("Improve principle activation - cold principles detected")
        
        # Attention narrowing recommendations
        if pattern_frequencies.get(FailurePattern.ATTENTION_NARROWING, 0) >= 1:
            recommendations.append("Monitor cognitive load - attention narrowing detected")
        
        # Principle violation recommendations
        if pattern_frequencies.get(FailurePattern.PRINCIPLE_VIOLATION, 0) > 0:
            recommendations.append("Review principle adherence - violations detected")
        
        # Cognitive overload recommendations
        if pattern_frequencies.get(FailurePattern.COGNITIVE_OVERLOAD, 0) > 0:
            recommendations.append("Implement load balancing - cognitive overload detected")

        # Baseline suggestion if any failures present but no specific rule fired
        if not recommendations and recent_failures:
            recommendations.append("Review recent failures and apply targeted mitigations")
        
        return recommendations
    
    def _generate_urgent_actions(self, critical_failures: List[FailureEvent]) -> List[str]:
        """Generate urgent actions for critical failures."""
        urgent_actions = []
        
        for failure in critical_failures:
            if failure.pattern == FailurePattern.COGNITIVE_OVERLOAD:
                urgent_actions.append("IMMEDIATE: Stop current task - cognitive overload")
            elif failure.pattern == FailurePattern.PRINCIPLE_VIOLATION:
                urgent_actions.append(f"URGENT: Fix principle violation - {failure.description}")
            elif failure.pattern == FailurePattern.ATTENTION_NARROWING:
                urgent_actions.append("URGENT: Take break - attention quality degraded")
        
        return urgent_actions
    
    def get_failure_summary(self) -> Dict[str, any]:
        """Get a summary of recent failures."""
        if not self.failure_history:
            return {"total_failures": 0, "recent_failures": 0, "critical_count": 0}
        
        recent_cutoff = datetime.now(UTC) - timedelta(hours=1)
        recent_failures = [f for f in self.failure_history if f.timestamp >= recent_cutoff]
        critical_failures = [f for f in recent_failures if f.severity == FailureSeverity.CRITICAL]
        
        return {
            "total_failures": len(self.failure_history),
            "recent_failures": len(recent_failures),
            "critical_count": len(critical_failures),
            "unresolved_count": len([f for f in recent_failures if not f.resolved]),
            "most_common_pattern": max(
                set(f.pattern for f in recent_failures),
                key=lambda p: sum(1 for f in recent_failures if f.pattern == p),
                default=None
            )
        }

    def resolve_failure(self, event_id: str, notes: str) -> None:
        """Mark a failure event as resolved with notes."""
        for failure in self.failure_history:
            if failure.event_id == event_id:
                failure.resolved = True
                failure.resolution_notes = notes
                break

    def get_critical_failures(self) -> List[FailureEvent]:
        """Return failures with critical severity in history."""
        return [f for f in self.failure_history if f.severity == FailureSeverity.CRITICAL]
