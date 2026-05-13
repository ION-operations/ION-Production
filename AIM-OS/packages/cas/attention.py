"""Attention Monitoring Component for CAS

Tracks cognitive load, attention breadth, and degradation signs.
Monitors where cognitive resources are allocated during operation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math
import logging

logger = logging.getLogger(__name__)


class AttentionState(str, Enum):
    """States of attention during operation."""
    FOCUSED = "focused"          # High attention on single task
    DISTRIBUTED = "distributed"   # Attention spread across multiple items
    OVERLOADED = "overloaded"     # Too many items competing for attention
    NARROWED = "narrowed"         # Attention narrowed due to load
    DEGRADED = "degraded"         # Attention quality degraded
    OPTIMAL = "optimal"           # Optimal attention allocation


class AttentionQuality(str, Enum):
    """Quality levels of attention."""
    EXCELLENT = "excellent"       # 0.9-1.0
    GOOD = "good"                 # 0.7-0.89
    FAIR = "fair"                 # 0.5-0.69
    POOR = "poor"                 # 0.3-0.49
    CRITICAL = "critical"         # 0.0-0.29


@dataclass
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

    def __post_init__(self):
        """
        Auto-calculate cognitive load when constructed directly in tests.
        Uses the same bounded components as monitor calculation when values provided.
        """
        if self.cognitive_load == 0.0:
            memory_load = min(0.5, self.working_memory_items / 20.0)
            context_load = min(0.3, self.context_size_tokens / 100000.0)
            switch_load = min(0.2, self.task_switches_per_hour / 20.0)
            total_load = memory_load + context_load + switch_load
            self.cognitive_load = min(1.0, total_load)
    
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
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.attention_history: List[AttentionMetrics] = []
        self.task_switches: List[datetime] = []
        self.error_events: List[datetime] = []
        self.retry_events: List[datetime] = []
        self.confidence_history: List[Tuple[datetime, float]] = []
        
    def record_task_switch(self, from_task: str, to_task: str):
        """Record a task switch event."""
        now = datetime.now(UTC)
        self.task_switches.append(now)
        logger.debug(f"Task switch: {from_task} -> {to_task}")
    
    def record_error(self, error_type: str, context: str = ""):
        """Record an error event."""
        now = datetime.now(UTC)
        self.error_events.append(now)
        logger.warning(f"Error recorded: {error_type} - {context}")
    
    def record_retry(self, task: str, reason: str = ""):
        """Record a retry event."""
        now = datetime.now(UTC)
        self.retry_events.append(now)
        logger.debug(f"Retry recorded: {task} - {reason}")
    
    def record_confidence(self, confidence: float):
        """Record a confidence measurement."""
        now = datetime.now(UTC)
        self.confidence_history.append((now, confidence))
        # Keep only recent history (last 100 measurements)
        if len(self.confidence_history) > 100:
            self.confidence_history = self.confidence_history[-100:]
    
    def calculate_attention_metrics(
        self,
        working_memory_items: int = 0,
        context_size_tokens: int = 0,
        current_task: Optional[str] = None,
        error_rate: Optional[float] = None
    ) -> AttentionMetrics:
        """
        Calculate comprehensive attention metrics.
        
        Args:
            working_memory_items: Number of items in working memory
            context_size_tokens: Size of current context in tokens
            current_task: Description of current task
            error_rate: Optional override for computed error rate
            
        Returns:
            AttentionMetrics with all calculated values
        """
        now = datetime.now(UTC)
        
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
        computed_error_rate = len(recent_errors) / max(1, task_switches_per_hour + 1)
        if error_rate is None:
            error_rate = computed_error_rate
        
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
    
    def get_attention_trend(self, hours: int = 1) -> Dict[str, float]:
        """Get attention trend over the specified time period."""
        cutoff_time = datetime.now(UTC) - timedelta(hours=hours)
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
    
    def should_take_break(self, metrics: Optional[AttentionMetrics] = None) -> bool:
        """Determine if a break should be taken based on attention metrics."""
        if metrics is not None:
            # Immediate decision on provided metrics
            if (
                metrics.cognitive_load > 0.8 or
                metrics.quality_level == AttentionQuality.CRITICAL or
                metrics.current_state == AttentionState.DEGRADED or
                metrics.error_rate > 0.7
            ):
                return True
            sample = [metrics]
        else:
            if not self.attention_history:
                return False
            sample = self.attention_history[-5:]  # Last 5 measurements
        
        # Check for sustained high load
        high_load_count = sum(1 for m in sample if m.cognitive_load > 0.8)
        if high_load_count >= 3:
            return True
        
        # Check for degraded attention
        degraded_count = sum(1 for m in sample if m.current_state == AttentionState.DEGRADED)
        if degraded_count >= 2:
            return True
        
        # Check for critical quality
        critical_count = sum(1 for m in sample if m.quality_level == AttentionQuality.CRITICAL)
        if critical_count >= 1:
            return True
        
        return False

    def get_warning_signs(self, metrics: AttentionMetrics) -> List[str]:
        """Return the list of warnings derived from provided metrics."""
        warnings, _ = self._generate_warnings_and_alerts(
            metrics.working_memory_items,
            metrics.cognitive_load,
            metrics.error_rate,
            metrics.retry_frequency,
            metrics.confidence_drift,
            metrics.current_state,
            metrics.quality_level
        )
        return warnings
