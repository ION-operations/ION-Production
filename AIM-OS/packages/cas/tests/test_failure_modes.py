"""Tests for CAS Failure Mode Analysis component."""

import pytest
from datetime import datetime, UTC
from cas.failure_modes import (
    FailureModeAnalyzer, FailureEvent, FailureAnalysis,
    FailurePattern, FailureSeverity
)


class TestFailureModeAnalyzer:
    
    def test_initialization(self):
        """Test FailureModeAnalyzer initialization."""
        analyzer = FailureModeAnalyzer("test_session")
        assert analyzer.session_id == "test_session"
        assert len(analyzer.failure_history) == 0
        assert len(analyzer.principle_usage) == 0
        assert len(analyzer.protocol_activations) == 0
        assert len(analyzer.task_classifications) == 0
    
    def test_analyze_categorization_error(self):
        """Test categorization error analysis."""
        analyzer = FailureModeAnalyzer("test_session")
        
        event = analyzer.analyze_categorization_error(
            task_description="Update AETHER_MEMORY current_priorities.md",
            detected_category="routine_maintenance",
            confidence=0.2,
            required_protocols=["bitemporal_versioning"],
            activated_protocols=[]
        )
        
        assert isinstance(event, FailureEvent)
        assert event.pattern == FailurePattern.CATEGORIZATION_ERROR
        assert event.severity in [FailureSeverity.MEDIUM, FailureSeverity.HIGH, FailureSeverity.CRITICAL]
        assert len(event.evidence) > 0
        assert len(event.suggested_actions) > 0
        assert "CMC_bitemporal" in event.description or "bitemporal" in event.description.lower()
    
    def test_analyze_activation_gap(self):
        """Test activation gap analysis."""
        analyzer = FailureModeAnalyzer("test_session")
        
        event = analyzer.analyze_activation_gap(
            required_principle="CMC_bitemporal",
            activation_level=0.1,
            task_category="critical_memory_modification",
            context="Updating memory files"
        )
        
        assert isinstance(event, FailureEvent)
        assert event.pattern == FailurePattern.ACTIVATION_GAP
        assert event.severity in [FailureSeverity.MEDIUM, FailureSeverity.HIGH, FailureSeverity.CRITICAL]
        assert "CMC_bitemporal" in event.description
        assert len(event.suggested_actions) > 0
    
    def test_analyze_attention_narrowing(self):
        """Test attention narrowing analysis."""
        analyzer = FailureModeAnalyzer("test_session")
        
        event = analyzer.analyze_attention_narrowing(
            working_memory_items=25,
            context_size_tokens=20000,
            error_rate=0.5,
            cognitive_load=0.9
        )
        
        assert isinstance(event, FailureEvent)
        assert event.pattern == FailurePattern.ATTENTION_NARROWING
        assert event.severity in [FailureSeverity.MEDIUM, FailureSeverity.HIGH, FailureSeverity.CRITICAL]
        assert len(event.evidence) > 0
        assert len(event.suggested_actions) > 0
    
    def test_analyze_principle_violation(self):
        """Test principle violation analysis."""
        analyzer = FailureModeAnalyzer("test_session")
        
        event = analyzer.analyze_principle_violation(
            violated_principle="CMC_bitemporal",
            violation_type="file_overwrite",
            context="Direct modification without versioning",
            impact="potential_data_loss"
        )
        
        assert isinstance(event, FailureEvent)
        assert event.pattern == FailurePattern.PRINCIPLE_VIOLATION
        assert event.severity in [FailureSeverity.HIGH, FailureSeverity.CRITICAL]
        assert "CMC_bitemporal" in event.description or "bitemporal" in event.description.lower()
        assert len(event.suggested_actions) > 0
    
    def test_analyze_failure_patterns_empty(self):
        """Test failure pattern analysis with no failures."""
        analyzer = FailureModeAnalyzer("test_session")
        
        analysis = analyzer.analyze_failure_patterns(hours_back=24)
        
        assert isinstance(analysis, FailureAnalysis)
        assert analysis.session_id == "test_session"
        assert len(analysis.recent_failures) == 0
        assert analysis.failure_rate_per_hour == 0.0
        assert analysis.critical_failure_count == 0
    
    def test_analyze_failure_patterns_with_failures(self):
        """Test failure pattern analysis with recorded failures."""
        analyzer = FailureModeAnalyzer("test_session")
        
        # Record some failures
        event1 = analyzer.analyze_categorization_error(
            task_description="Test task 1",
            detected_category="routine_maintenance",
            confidence=0.2,
            required_protocols=["bitemporal_versioning"],
            activated_protocols=[]
        )
        
        event2 = analyzer.analyze_activation_gap(
            required_principle="VIF_provenance",
            activation_level=0.15,
            task_category="system_implementation",
            context="Implementing new feature"
        )
        
        analysis = analyzer.analyze_failure_patterns(hours_back=24)
        
        assert len(analysis.recent_failures) >= 2
        assert analysis.failure_rate_per_hour > 0.0
        assert FailurePattern.CATEGORIZATION_ERROR in analysis.pattern_frequencies
        assert len(analysis.recommendations) > 0
    
    def test_get_critical_failures(self):
        """Test retrieving critical failures."""
        analyzer = FailureModeAnalyzer("test_session")
        
        # Create critical failure
        event = analyzer.analyze_principle_violation(
            violated_principle="CMC_bitemporal",
            violation_type="file_overwrite",
            context="Critical memory file overwritten",
            impact="data_loss_risk"
        )
        
        critical = analyzer.get_critical_failures()
        
        assert len(critical) > 0
        assert any(f.pattern == FailurePattern.PRINCIPLE_VIOLATION for f in critical)
    
    def test_resolve_failure(self):
        """Test resolving a failure event."""
        analyzer = FailureModeAnalyzer("test_session")
        
        event = analyzer.analyze_categorization_error(
            task_description="Test task",
            detected_category="routine_maintenance",
            confidence=0.2,
            required_protocols=["bitemporal_versioning"],
            activated_protocols=[]
        )
        
        assert event.resolved == False
        
        analyzer.resolve_failure(event.event_id, "Fixed categorization logic")
        
        # Find the resolved event
        resolved_events = [f for f in analyzer.failure_history if f.event_id == event.event_id]
        assert len(resolved_events) > 0
        assert resolved_events[0].resolved == True
        assert resolved_events[0].resolution_notes == "Fixed categorization logic"


class TestFailureEvent:
    
    def test_initialization(self):
        """Test FailureEvent initialization."""
        event = FailureEvent(
            event_id="test_event_001",
            pattern=FailurePattern.CATEGORIZATION_ERROR,
            severity=FailureSeverity.MEDIUM,
            timestamp=datetime.now(UTC),
            description="Test failure description"
        )
        
        assert event.event_id == "test_event_001"
        assert event.pattern == FailurePattern.CATEGORIZATION_ERROR
        assert event.severity == FailureSeverity.MEDIUM
        assert event.resolved == False
        assert event.resolution_notes is None
    
    def test_is_resolved(self):
        """Test is_resolved method."""
        event = FailureEvent(
            event_id="test_event_001",
            pattern=FailurePattern.CATEGORIZATION_ERROR,
            severity=FailureSeverity.MEDIUM,
            timestamp=datetime.now(UTC),
            description="Test failure"
        )
        
        assert event.is_resolved() == False
        
        event.resolved = True
        assert event.is_resolved() == True


class TestFailureAnalysis:
    
    def test_initialization(self):
        """Test FailureAnalysis initialization."""
        analysis = FailureAnalysis(
            analysis_id="analysis_001",
            timestamp=datetime.now(UTC),
            session_id="test_session"
        )
        
        assert analysis.analysis_id == "analysis_001"
        assert analysis.session_id == "test_session"
        assert len(analysis.recent_failures) == 0
        assert len(analysis.pattern_frequencies) == 0
        assert analysis.failure_rate_per_hour == 0.0
    
    def test_with_failures(self):
        """Test FailureAnalysis with recorded failures."""
        event1 = FailureEvent(
            event_id="event_001",
            pattern=FailurePattern.CATEGORIZATION_ERROR,
            severity=FailureSeverity.MEDIUM,
            timestamp=datetime.now(UTC),
            description="Categorization error"
        )
        
        event2 = FailureEvent(
            event_id="event_002",
            pattern=FailurePattern.ACTIVATION_GAP,
            severity=FailureSeverity.HIGH,
            timestamp=datetime.now(UTC),
            description="Activation gap"
        )
        
        analysis = FailureAnalysis(
            analysis_id="analysis_001",
            timestamp=datetime.now(UTC),
            session_id="test_session",
            recent_failures=[event1, event2],
            pattern_frequencies={
                FailurePattern.CATEGORIZATION_ERROR: 1,
                FailurePattern.ACTIVATION_GAP: 1
            },
            failure_rate_per_hour=2.0
        )
        
        assert len(analysis.recent_failures) == 2
        assert analysis.failure_rate_per_hour == 2.0
        assert FailurePattern.CATEGORIZATION_ERROR in analysis.pattern_frequencies


class TestFailurePattern:
    
    def test_failure_pattern_enum(self):
        """Test FailurePattern enum values."""
        assert FailurePattern.CATEGORIZATION_ERROR == "categorization_error"
        assert FailurePattern.ACTIVATION_GAP == "activation_gap"
        assert FailurePattern.ATTENTION_NARROWING == "attention_narrowing"
        assert FailurePattern.PRINCIPLE_VIOLATION == "principle_violation"


class TestFailureSeverity:
    
    def test_failure_severity_enum(self):
        """Test FailureSeverity enum values."""
        assert FailureSeverity.LOW == "low"
        assert FailureSeverity.MEDIUM == "medium"
        assert FailureSeverity.HIGH == "high"
        assert FailureSeverity.CRITICAL == "critical"


class TestFailureModeIntegration:
    
    def test_complete_failure_analysis_workflow(self):
        """Test complete failure mode analysis workflow."""
        analyzer = FailureModeAnalyzer("integration_session")
        
        # Record various failure types
        cat_error = analyzer.analyze_categorization_error(
            task_description="Update memory file",
            detected_category="routine_maintenance",
            confidence=0.15,
            required_protocols=["bitemporal_versioning"],
            activated_protocols=[]
        )
        
        act_gap = analyzer.analyze_activation_gap(
            required_principle="CMC_bitemporal",
            activation_level=0.1,
            task_category="critical_memory_modification",
            context="Memory update"
        )
        
        att_narrow = analyzer.analyze_attention_narrowing(
            working_memory_items=30,
            context_size_tokens=25000,
            error_rate=0.6,
            cognitive_load=0.95
        )
        
        # Analyze patterns
        analysis = analyzer.analyze_failure_patterns(hours_back=24)
        
        # Verify analysis
        assert len(analysis.recent_failures) >= 3
        assert analysis.failure_rate_per_hour > 0.0
        assert len(analysis.pattern_frequencies) >= 3
        assert len(analysis.recommendations) > 0
        
        # Test critical failures
        critical = analyzer.get_critical_failures()
        assert isinstance(critical, list)
        
        # Test resolution
        if len(analyzer.failure_history) > 0:
            first_event = analyzer.failure_history[0]
            analyzer.resolve_failure(first_event.event_id, "Resolved in test")
            
            resolved = [f for f in analyzer.failure_history if f.event_id == first_event.event_id]
            assert len(resolved) > 0
            assert resolved[0].resolved == True

