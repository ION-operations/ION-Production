"""Tests for CAS Attention Monitoring component."""

import pytest
from datetime import datetime, timedelta, UTC
from cas.attention import (
    AttentionMonitor, AttentionMetrics, AttentionState, AttentionQuality
)


class TestAttentionMonitor:
    
    def test_initialization(self):
        """Test AttentionMonitor initialization."""
        monitor = AttentionMonitor("test_session")
        assert monitor.session_id == "test_session"
        assert len(monitor.attention_history) == 0
        assert len(monitor.task_switches) == 0
        assert len(monitor.error_events) == 0
        assert len(monitor.retry_events) == 0
        assert len(monitor.confidence_history) == 0
    
    def test_record_task_switch(self):
        """Test recording task switches."""
        monitor = AttentionMonitor("test_session")
        monitor.record_task_switch("task_a", "task_b")
        
        assert len(monitor.task_switches) == 1
        assert isinstance(monitor.task_switches[0], datetime)
    
    def test_record_error(self):
        """Test recording error events."""
        monitor = AttentionMonitor("test_session")
        monitor.record_error("categorization_error", "Task misclassified")
        
        assert len(monitor.error_events) == 1
        assert isinstance(monitor.error_events[0], datetime)
    
    def test_record_retry(self):
        """Test recording retry events."""
        monitor = AttentionMonitor("test_session")
        monitor.record_retry("task_retry")
        
        assert len(monitor.retry_events) == 1
        assert isinstance(monitor.retry_events[0], datetime)
    
    def test_record_confidence(self):
        """Test recording confidence levels."""
        monitor = AttentionMonitor("test_session")
        monitor.record_confidence(0.85)
        
        assert len(monitor.confidence_history) == 1
        assert monitor.confidence_history[0][1] == 0.85
        assert isinstance(monitor.confidence_history[0][0], datetime)
    
    def test_calculate_attention_metrics_empty(self):
        """Test calculating metrics with no history."""
        monitor = AttentionMonitor("test_session")
        metrics = monitor.calculate_attention_metrics()
        
        assert isinstance(metrics, AttentionMetrics)
        assert metrics.session_id == "test_session"
        assert metrics.working_memory_items == 0
        assert metrics.context_size_tokens == 0
        assert metrics.cognitive_load == 0.0
    
    def test_calculate_attention_metrics_with_data(self):
        """Test calculating metrics with recorded data."""
        monitor = AttentionMonitor("test_session")
        monitor.record_task_switch("task_a", "task_b")
        monitor.record_task_switch("task_b", "task_c")
        monitor.record_confidence(0.9)
        monitor.record_confidence(0.85)
        monitor.record_confidence(0.8)
        
        metrics = monitor.calculate_attention_metrics(
            working_memory_items=10,
            context_size_tokens=5000,
            error_rate=0.1
        )
        
        assert metrics.working_memory_items == 10
        assert metrics.context_size_tokens == 5000
        assert metrics.error_rate == 0.1
        assert metrics.task_switches_per_hour > 0
    
    def test_should_take_break_low_load(self):
        """Test break recommendation with low cognitive load."""
        monitor = AttentionMonitor("test_session")
        metrics = monitor.calculate_attention_metrics(
            working_memory_items=5,
            context_size_tokens=2000,
            error_rate=0.05
        )
        
        should_break = monitor.should_take_break(metrics)
        assert should_break == False
    
    def test_should_take_break_high_load(self):
        """Test break recommendation with high cognitive load."""
        monitor = AttentionMonitor("test_session")
        # Record many task switches and errors
        for i in range(10):
            monitor.record_task_switch(f"task_{i}", f"task_{i+1}")
        for i in range(5):
            monitor.record_error("error")
        
        metrics = monitor.calculate_attention_metrics(
            working_memory_items=20,
            context_size_tokens=15000,
            error_rate=0.5
        )
        
        should_break = monitor.should_take_break(metrics)
        assert should_break == True
    
    def test_get_warning_signs_no_warnings(self):
        """Test warning detection with healthy state."""
        monitor = AttentionMonitor("test_session")
        metrics = monitor.calculate_attention_metrics(
            working_memory_items=8,
            context_size_tokens=4000,
            error_rate=0.05
        )
        
        warnings = monitor.get_warning_signs(metrics)
        assert len(warnings) == 0 or all(not w.startswith("⚠️") for w in warnings)
    
    def test_get_warning_signs_with_warnings(self):
        """Test warning detection with degraded state."""
        monitor = AttentionMonitor("test_session")
        # Create high load scenario
        for i in range(15):
            monitor.record_task_switch(f"task_{i}", f"task_{i+1}")
        for i in range(10):
            monitor.record_error("error")
        
        metrics = monitor.calculate_attention_metrics(
            working_memory_items=25,
            context_size_tokens=20000,
            error_rate=0.8
        )
        
        warnings = monitor.get_warning_signs(metrics)
        assert len(warnings) > 0
        assert any("attention" in w.lower() or "load" in w.lower() for w in warnings)


class TestAttentionMetrics:
    
    def test_initialization(self):
        """Test AttentionMetrics initialization."""
        metrics = AttentionMetrics(
            timestamp=datetime.now(UTC),
            session_id="test_session"
        )
        
        assert metrics.session_id == "test_session"
        assert metrics.working_memory_items == 0
        assert metrics.context_size_tokens == 0
        assert metrics.cognitive_load == 0.0
        assert metrics.current_state == AttentionState.OPTIMAL
        assert metrics.quality_level == AttentionQuality.EXCELLENT
    
    def test_is_healthy_excellent(self):
        """Test healthy check with excellent quality."""
        metrics = AttentionMetrics(
            timestamp=datetime.now(UTC),
            session_id="test_session",
            current_state=AttentionState.OPTIMAL,
            quality_level=AttentionQuality.EXCELLENT,
            warnings=[],
            alerts=[]
        )
        
        assert metrics.is_healthy() == True
    
    def test_is_healthy_degraded(self):
        """Test healthy check with degraded state."""
        metrics = AttentionMetrics(
            timestamp=datetime.now(UTC),
            session_id="test_session",
            current_state=AttentionState.DEGRADED,
            quality_level=AttentionQuality.POOR,
            warnings=["High cognitive load"],
            alerts=["Critical attention narrowing"]
        )
        
        assert metrics.is_healthy() == False
    
    def test_is_healthy_with_alerts(self):
        """Test healthy check with alerts."""
        metrics = AttentionMetrics(
            timestamp=datetime.now(UTC),
            session_id="test_session",
            current_state=AttentionState.OPTIMAL,
            quality_level=AttentionQuality.GOOD,
            warnings=[],
            alerts=["Attention drift detected"]
        )
        
        assert metrics.is_healthy() == False
    
    def test_cognitive_load_calculation(self):
        """Test cognitive load calculation from metrics."""
        metrics = AttentionMetrics(
            timestamp=datetime.now(UTC),
            session_id="test_session",
            working_memory_items=15,
            context_size_tokens=10000,
            task_switches_per_hour=20.0,
            error_rate=0.3
        )
        
        # Cognitive load should be calculated based on these factors
        assert metrics.cognitive_load > 0.0
        assert metrics.cognitive_load <= 1.0


class TestAttentionState:
    
    def test_attention_state_enum(self):
        """Test AttentionState enum values."""
        assert AttentionState.FOCUSED == "focused"
        assert AttentionState.DISTRIBUTED == "distributed"
        assert AttentionState.OVERLOADED == "overloaded"
        assert AttentionState.NARROWED == "narrowed"
        assert AttentionState.DEGRADED == "degraded"
        assert AttentionState.OPTIMAL == "optimal"


class TestAttentionQuality:
    
    def test_attention_quality_enum(self):
        """Test AttentionQuality enum values."""
        assert AttentionQuality.EXCELLENT == "excellent"
        assert AttentionQuality.GOOD == "good"
        assert AttentionQuality.FAIR == "fair"
        assert AttentionQuality.POOR == "poor"
        assert AttentionQuality.CRITICAL == "critical"


class TestAttentionIntegration:
    
    def test_full_attention_tracking_cycle(self):
        """Test complete attention tracking workflow."""
        monitor = AttentionMonitor("integration_session")
        
        # Simulate a work session
        monitor.record_task_switch("planning", "coding")
        monitor.record_confidence(0.9)
        monitor.record_task_switch("coding", "testing")
        monitor.record_confidence(0.85)
        monitor.record_error("test_failure")
        monitor.record_retry("retry_test")
        monitor.record_confidence(0.8)
        
        # Calculate metrics
        metrics = monitor.calculate_attention_metrics(
            working_memory_items=12,
            context_size_tokens=8000,
            error_rate=0.15
        )
        
        # Verify metrics
        assert metrics.session_id == "integration_session"
        assert metrics.working_memory_items == 12
        assert metrics.context_size_tokens == 8000
        assert metrics.error_rate == 0.15
        assert metrics.task_switches_per_hour > 0
        
        # Check break recommendation
        should_break = monitor.should_take_break(metrics)
        assert isinstance(should_break, bool)
        
        # Check warnings
        warnings = monitor.get_warning_signs(metrics)
        assert isinstance(warnings, list)
        
        # Verify history tracking
        assert len(monitor.attention_history) == 1
        assert len(monitor.task_switches) == 2
        assert len(monitor.error_events) == 1
        assert len(monitor.retry_events) == 1
        assert len(monitor.confidence_history) == 3

