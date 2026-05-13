"""Attention Monitoring Component for CAS

Tracks cognitive load, attention breadth, and degradation signs.
Monitors where cognitive resources are allocated during operation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math
import logging

logger = logging.getLogger(__name__)


# NL_TAG: VIF-MODEL-001 | States of attention during operation. | class AttentionState | []
class AttentionState(str, Enum):
    """States of attention during operation."""
    FOCUSED = "focused"          # High attention on single task
    DISTRIBUTED = "distributed"   # Attention spread across multiple items
    OVERLOADED = "overloaded"     # Too many items competing for attention
    NARROWED = "narrowed"         # Attention narrowed due to load
    DEGRADED = "degraded"         # Attention quality degraded
    OPTIMAL = "optimal"           # Optimal attention allocation


# NL_TAG: VIF-MODEL-002 | Quality levels of attention. | class AttentionQuality | []
# NL_TAG_INTENT: VIF-INTENT-001 | Design decision: quality | AttentionQuality | [ADR-TBD]
class AttentionQuality(str, Enum):
    """Quality levels of attention."""
    EXCELLENT = "excellent"       # 0.9-1.0
    GOOD = "good"                 # 0.7-0.89
    FAIR = "fair"                 # 0.5-0.69
    POOR = "poor"                 # 0.3-0.49
    CRITICAL = "critical"         # 0.0-0.29


@dataclass
# NL_TAG: VIF-MODEL-003 | Metrics for attention monitoring. | class AttentionMetrics | []
class AttentionMetrics:
    """Metrics for attention monitoring."""
    timestamp: datetime
    session_id: str
    
    # Core metrics
    working_memory_items: int = 0
    context_size_tokens: int = 0
    attention_span_minutes: float = 0.0
    task_switches_per_hour: float = 0.0
    
    # Quality indicators
    focus_depth: float = 0.0      # 0.0-1.0, how deep the focus
    attention_stability: float = 0.0  # 0.0-1.0, how stable attention is
    cognitive_load: float = 0.0   # 0.0-1.0, estimated cognitive load
    
    # Degradation signs
    error_rate: float = 0.0       # 0.0-1.0, recent error rate
    retry_frequency: float = 0.0  # 0.0-1.0, how often tasks are retried
    confidence_drift: float = 0.0 # 0.0-1.0, how much confidence has drifted
    
    # Attention state
    current_state: AttentionState = AttentionState.OPTIMAL
    quality_level: AttentionQuality = AttentionQuality.EXCELLENT
    
    # Warnings and alerts
    warnings: List[str] = field(default_factory=list)
    alerts: List[str] = field(default_factory=list)
    
    def is_healthy(self) -> bool:
        """Check if attention is in a healthy state."""
        return (
            self.current_state != AttentionState.DEGRADED and
            self.quality_level not in [AttentionQuality.POOR, AttentionQuality.CRITICAL] and
            len(self.alerts) == 0
        )


# NL_TAG: VIF-MODEL-004 | Monitors attention allocation and cognitive load. | class AttentionMonitor | []
class AttentionMonitor:
    # NL_TAG: VIF-UTIL-001 | Check if attention is in a healthy state. | is_healthy(self) | []
    def is_healthy(self) -> bool:
        """Check if attention is in a healthy state."""
        return (
            self.current_state != AttentionState.DEGRADED and
            self.quality_level not in [AttentionQuality.POOR, AttentionQuality.CRITICAL] and
            len(self.alerts) == 0
        )


class AttentionMonitor:
    """
    Monitors attention allocation and cognitive load.
    
    Tracks where cognitive resources are allocated, detects attention
    narrowing, and predicts degradation before it causes failures.
    """
    
    # NL_TAG: VIF-UTIL-002 |   init   | __init__(self, session_id) | []
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.attention_history: List[AttentionMetrics] = []
        self.task_switches: List[datetime] = []
        self.error_events: List[datetime] = []
        self.retry_events: List[datetime] = []
        self.confidence_history: List[Tuple[datetime, float]] = []
        
    # NL_TAG: VIF-UTIL-003 | Record a task switch event. | record_task_switch(self, from_task, to_task) | []
    def record_task_switch(self, from_task: str, to_task: str):
        """Record a task switch event."""
        now = datetime.utcnow()
        self.task_switches.append(now)
        logger.debug(f"Task switch: {from_task} -> {to_task}")
    
    # NL_TAG: VIF-UTIL-004 | Record an error event. | record_error(self, error_type, context) | []
    def record_error(self, error_type: str, context: str = ""):
        """Record an error event."""
        now = datetime.utcnow()
        self.error_events.append(now)
        logger.warning(f"Error recorded: {error_type} - {context}")
    
    # NL_TAG: VIF-UTIL-005 | Record a retry event. | record_retry(self, task, reason) | []
    def record_retry(self, task: str, reason: str = ""):
        """Record a retry event."""
        now = datetime.utcnow()
        self.retry_events.append(now)
        logger.debug(f"Retry recorded: {task} - {reason}")
    
    # NL_TAG: VIF-CONF-001 | Record a confidence measurement. | record_confidence(self, confidence) | []
    # NL_TAG_INTENT: VIF-INTENT-002 | Design decision: confidence | record_confidence | [ADR-TBD]
    def record_confidence(self, confidence: float):
        """Record a confidence measurement."""
        now = datetime.utcnow()
        self.confidence_history.append((now, confidence))
        # Keep only recent history (last 100 measurements)
        if len(self.confidence_history) > 100:
            self.confidence_history = self.confidence_history[-100:]
    
    # NL_TAG: VIF-UTIL-006 | Calculate comprehensive attention metrics. | calculate_attention_metrics(self, working_memory_items, context_size_tokens, current_task) | []
    def calculate_attention_metrics(
        self,
        working_memory_items: int,
        context_size_tokens: int,
        current_task: Optional[str] = None
    ) -> AttentionMetrics:
        """
        Calculate comprehensive attention metrics.
        
        Args:
            working_memory_items: Number of items in working memory
            context_size_tokens: Size of current context in tokens
            current_task: Description of current task
            
        Returns:
            AttentionMetrics with all calculated values
        """
        now = datetime.utcnow()
        
        # Calculate attention span (time since last task switch)
        attention_span_minutes = 0.0
        if self.task_switches:
            last_switch = self.task_switches[-1]
            attention_span_minutes = (now - last_switch).total_seconds() / 60
        else:
            attention_span_minutes = 60.0  # Default if no switches recorded
        
        # Calculate task switches per hour
        recent_switches = [
            ts for ts in self.task_switches 
            if (now - ts).total_seconds() < 3600  # Last hour
        ]
        task_switches_per_hour = len(recent_switches)
        
        # Calculate focus depth (inverse of working memory items)
        max_items = 20  # Theoretical maximum
        focus_depth = max(0.0, 1.0 - (working_memory_items / max_items))
        
        # Calculate attention stability (based on recent task switches)
        stability_score = 1.0
        if task_switches_per_hour > 10:  # High switching
            stability_score = 0.3
        elif task_switches_per_hour > 5:  # Medium switching
            stability_score = 0.6
        elif task_switches_per_hour > 2:  # Low switching
            stability_score = 0.8
        
        # Calculate cognitive load
        cognitive_load = self._calculate_cognitive_load(
            working_memory_items, context_size_tokens, task_switches_per_hour
        )
        
        # Calculate error rate (recent errors)
        recent_errors = [
            err for err in self.error_events 
            if (now - err).total_seconds() < 3600  # Last hour
        ]
        error_rate = len(recent_errors) / max(1, task_switches_per_hour + 1)
        
        # Calculate retry frequency
        recent_retries = [
            retry for retry in self.retry_events 
            if (now - retry).total_seconds() < 3600  # Last hour
        ]
        retry_frequency = len(recent_retries) / max(1, task_switches_per_hour + 1)
        
        # Calculate confidence drift
        confidence_drift = self._calculate_confidence_drift()
        
        # Determine attention state
        current_state = self._determine_attention_state(
            working_memory_items, cognitive_load, focus_depth, stability_score
        )
        
        # Determine quality level
        quality_level = self._determine_quality_level(
            focus_depth, stability_score, error_rate, confidence_drift
        )
        
        # Generate warnings and alerts
        warnings, alerts = self._generate_warnings_and_alerts(
            working_memory_items, cognitive_load, error_rate, 
            retry_frequency, confidence_drift, current_state, quality_level
        )
        
        metrics = AttentionMetrics(
            timestamp=now,
            session_id=self.session_id,
            working_memory_items=working_memory_items,
            context_size_tokens=context_size_tokens,
            attention_span_minutes=attention_span_minutes,
            task_switches_per_hour=task_switches_per_hour,
            focus_depth=focus_depth,
            attention_stability=stability_score,
            cognitive_load=cognitive_load,
            error_rate=error_rate,
            retry_frequency=retry_frequency,
            confidence_drift=confidence_drift,
            current_state=current_state,
            quality_level=quality_level,
            warnings=warnings,
            alerts=alerts
        )
        
        # Store in history
        self.attention_history.append(metrics)
        if len(self.attention_history) > 100:  # Keep only recent history
            self.attention_history = self.attention_history[-100:]
        
        return metrics
    
    # NL_TAG: VIF-UTIL-007 | Calculate cognitive load based on various factors. | _calculate_cognitive_load(self, working_memory_items, context_size_tokens, task_switches_per_hour) | []
    def _calculate_cognitive_load(
        self,
        working_memory_items: int,
        context_size_tokens: int,
        task_switches_per_hour: float
    ) -> float:
        """Calculate cognitive load based on various factors."""
        # Base load from working memory (0.0-0.5)
        memory_load = min(0.5, working_memory_items / 20.0)
        
        # Load from context size (0.0-0.3)
        context_load = min(0.3, context_size_tokens / 100000.0)  # 100k tokens = max
        
        # Load from task switching (0.0-0.2)
        switch_load = min(0.2, task_switches_per_hour / 20.0)
        
        total_load = memory_load + context_load + switch_load
        return min(1.0, total_load)
    
    # NL_TAG: VIF-CONF-002 | Calculate how much confidence has drifted recently. | _calculate_confidence_drift(self) | []
    # NL_TAG_INTENT: VIF-INTENT-003 | Design decision: confidence | _calculate_confidence_drift | [ADR-TBD]
    def _calculate_confidence_drift(self) -> float:
        """Calculate how much confidence has drifted recently."""
        if len(self.confidence_history) < 2:
            return 0.0
        
        # Get recent confidence values (last 10)
        recent_confidences = [conf for _, conf in self.confidence_history[-10:]]
        
        if len(recent_confidences) < 2:
            return 0.0
        
        # Calculate standard deviation as drift measure
        mean_conf = sum(recent_confidences) / len(recent_confidences)
        variance = sum((conf - mean_conf) ** 2 for conf in recent_confidences) / len(recent_confidences)
        drift = math.sqrt(variance)
        
        return min(1.0, drift)
    
    # NL_TAG: VIF-UTIL-008 | Determine current attention state based on metrics. | _determine_attention_state(self, working_memory_items, cognitive_load, focus_depth, stability_score) | []
    def _determine_attention_state(
        self,
        working_memory_items: int,
        cognitive_load: float,
        focus_depth: float,
        stability_score: float
    ) -> AttentionState:
        """Determine current attention state based on metrics."""
        if cognitive_load > 0.8:
            return AttentionState.OVERLOADED
        elif working_memory_items > 15:
            return AttentionState.DISTRIBUTED
        elif focus_depth > 0.8 and stability_score > 0.7:
            return AttentionState.FOCUSED
        elif focus_depth < 0.3 or stability_score < 0.4:
            return AttentionState.NARROWED
        elif cognitive_load > 0.6 or stability_score < 0.5:
            return AttentionState.DEGRADED
        else:
            return AttentionState.OPTIMAL
    
    # NL_TAG: VIF-UTIL-009 | Determine attention quality level. | _determine_quality_level(self, focus_depth, stability_score, error_rate, confidence_drift) | []
    # NL_TAG_INTENT: VIF-INTENT-004 | Design decision: quality | _determine_quality_level | [ADR-TBD]
    def _determine_quality_level(
        self,
        focus_depth: float,
        stability_score: float,
        error_rate: float,
        confidence_drift: float
    ) -> AttentionQuality:
        """Determine attention quality level."""
        # Calculate composite quality score
        quality_score = (
            0.3 * focus_depth +
            0.3 * stability_score +
            0.2 * (1.0 - error_rate) +
            0.2 * (1.0 - confidence_drift)
        )
        
        if quality_score >= 0.9:
            return AttentionQuality.EXCELLENT
        elif quality_score >= 0.7:
            return AttentionQuality.GOOD
        elif quality_score >= 0.5:
            return AttentionQuality.FAIR
        elif quality_score >= 0.3:
            return AttentionQuality.POOR
        else:
            return AttentionQuality.CRITICAL
    
    # NL_TAG: VIF-UTIL-010 | Generate warnings and alerts based on metrics. | _generate_warnings_and_alerts(self, working_memory_items, cognitive_load, error_rate, retry_frequency, confidence_drift, current_state, quality_level) | []
    def _generate_warnings_and_alerts(
        self,
        working_memory_items: int,
        cognitive_load: float,
        error_rate: float,
        retry_frequency: float,
        confidence_drift: float,
        current_state: AttentionState,
        quality_level: AttentionQuality
    ) -> tuple[List[str], List[str]]:
        """Generate warnings and alerts based on metrics."""
        warnings = []
        alerts = []
        
        # Warnings (non-critical issues)
        if working_memory_items > 12:
            warnings.append(f"High working memory load: {working_memory_items} items")
        
        if cognitive_load > 0.7:
            warnings.append(f"High cognitive load: {cognitive_load:.2f}")
        
        if error_rate > 0.3:
            warnings.append(f"Elevated error rate: {error_rate:.2f}")
        
        if retry_frequency > 0.5:
            warnings.append(f"High retry frequency: {retry_frequency:.2f}")
        
        if confidence_drift > 0.3:
            warnings.append(f"High confidence drift: {confidence_drift:.2f}")
        
        # Alerts (critical issues)
        if current_state == AttentionState.DEGRADED:
            alerts.append("Attention quality degraded - consider taking a break")
        
        if quality_level == AttentionQuality.CRITICAL:
            alerts.append("Critical attention quality - immediate intervention needed")
        
        if cognitive_load > 0.9:
            alerts.append("Extreme cognitive overload - stop current task")
        
        if error_rate > 0.7:
            alerts.append("Very high error rate - review recent changes")
        
        return warnings, alerts
    
    # NL_TAG: VIF-UTIL-011 | Get attention trend over the specified time period. | get_attention_trend(self, hours) | []
    def get_attention_trend(self, hours: int = 1) -> Dict[str, float]:
        """Get attention trend over the specified time period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.attention_history 
            if m.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {}
        
        return {
            "avg_cognitive_load": sum(m.cognitive_load for m in recent_metrics) / len(recent_metrics),
            "avg_focus_depth": sum(m.focus_depth for m in recent_metrics) / len(recent_metrics),
            "avg_stability": sum(m.attention_stability for m in recent_metrics) / len(recent_metrics),
            "avg_error_rate": sum(m.error_rate for m in recent_metrics) / len(recent_metrics),
            "total_task_switches": sum(m.task_switches_per_hour for m in recent_metrics),
            "degraded_periods": sum(1 for m in recent_metrics if m.current_state == AttentionState.DEGRADED)
        }
    
    # NL_TAG: VIF-UTIL-012 | Determine if a break should be taken based on attention metrics. | should_take_break(self) | []
    def should_take_break(self) -> bool:
        """Determine if a break should be taken based on attention metrics."""
        if not self.attention_history:
            return False
        
        recent_metrics = self.attention_history[-5:]  # Last 5 measurements
        
        # Check for sustained high load
        high_load_count = sum(1 for m in recent_metrics if m.cognitive_load > 0.8)
        if high_load_count >= 3:
            return True
        
        # Check for degraded attention
        degraded_count = sum(1 for m in recent_metrics if m.current_state == AttentionState.DEGRADED)
        if degraded_count >= 2:
            return True
        
        # Check for critical quality
        critical_count = sum(1 for m in recent_metrics if m.quality_level == AttentionQuality.CRITICAL)
        if critical_count >= 1:
            return True
        
        return False
