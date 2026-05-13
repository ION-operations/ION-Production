"""Tests for CAS Introspection Protocols component."""

import pytest
from datetime import datetime, UTC
from cas.introspection import (
    IntrospectionProtocol, IntrospectionResult, IntrospectionCheck,
    IntrospectionType, IntrospectionStatus
)


class TestIntrospectionProtocol:
    
    def test_initialization(self):
        """Test IntrospectionProtocol initialization."""
        protocol = IntrospectionProtocol("test_session")
        assert protocol.session_id == "test_session"
        assert len(protocol.introspection_history) == 0
        assert len(protocol.principle_violations) == 0
        assert len(protocol.protocol_usage) == 0
    
    def test_perform_hourly_check_optimal(self):
        """Test hourly check with optimal state."""
        protocol = IntrospectionProtocol("test_session")
        
        activation_state = {
            "CMC_bitemporal": 0.9,
            "VIF_provenance": 0.85,
            "SDF_quartet": 0.9,
            "APOE_orchestration": 0.8,
            "CAS_introspection": 0.9
        }
        
        attention_metrics = {
            "cognitive_load": 0.5,
            "focus_depth": 0.8,
            "attention_stability": 0.85,
            "error_rate": 0.05
        }
        
        result = protocol.perform_hourly_check(
            activation_state=activation_state,
            attention_metrics=attention_metrics,
            recent_failures=[],
            current_task="Test task"
        )
        
        assert isinstance(result, IntrospectionResult)
        assert result.session_id == "test_session"
        assert result.introspection_type == IntrospectionType.HOURLY_CHECK
        assert result.overall_status in [IntrospectionStatus.EXCELLENT, IntrospectionStatus.GOOD]
        assert result.overall_score > 0.7
        assert len(result.checks) > 0
        assert result.total_checks > 0
    
    def test_perform_hourly_check_degraded(self):
        """Test hourly check with degraded state."""
        protocol = IntrospectionProtocol("test_session")
        
        activation_state = {
            "CMC_bitemporal": 0.1,  # Cold
            "VIF_provenance": 0.15,  # Cold
            "SDF_quartet": 0.2,  # Cold
            "APOE_orchestration": 0.1,  # Cold
            "CAS_introspection": 0.9
        }
        
        attention_metrics = {
            "cognitive_load": 0.95,  # High load
            "focus_depth": 0.3,  # Low focus
            "attention_stability": 0.2,  # Unstable
            "error_rate": 0.6  # High error rate
        }
        
        result = protocol.perform_hourly_check(
            activation_state=activation_state,
            attention_metrics=attention_metrics,
            recent_failures=["categorization_error", "activation_gap"],
            current_task="Complex task"
        )
        
        assert isinstance(result, IntrospectionResult)
        assert result.overall_status in [IntrospectionStatus.FAIR, IntrospectionStatus.POOR, IntrospectionStatus.CRITICAL]
        assert result.overall_score < 0.6
        assert len(result.immediate_actions) > 0
    
    def test_perform_post_failure_analysis(self):
        """Test post-failure analysis."""
        protocol = IntrospectionProtocol("test_session")
        
        result = protocol.perform_post_failure_analysis(
            failure_description="Categorization error: task misclassified",
            failure_type="categorization_error",
            context="Updating memory files",
            error_rate=0.3
        )
        
        assert isinstance(result, IntrospectionResult)
        assert result.introspection_type == IntrospectionType.FAILURE_ANALYSIS
        assert len(result.checks) > 0
        assert len(result.immediate_actions) > 0
    
    def test_record_principle_violation(self):
        """Test recording principle violations."""
        protocol = IntrospectionProtocol("test_session")
        
        protocol.record_principle_violation(
            principle="CMC_bitemporal",
            violation_type="file_overwrite",
            context="Direct file modification without versioning"
        )
        
        assert len(protocol.principle_violations) == 1
        violation = protocol.principle_violations[0]
        assert violation[1] == "CMC_bitemporal"
        assert violation[2] == "Direct file modification without versioning"
    
    def test_should_escalate_no_escalation(self):
        """Test escalation check with no escalation needed."""
        protocol = IntrospectionProtocol("test_session")
        
        activation_state = {
            "CMC_bitemporal": 0.9,
            "VIF_provenance": 0.85
        }
        
        attention_metrics = {
            "cognitive_load": 0.5,
            "error_rate": 0.05
        }
        
        should_escalate = protocol.should_escalate(
            activation_state=activation_state,
            attention_metrics=attention_metrics,
            recent_failures=[]
        )
        
        assert should_escalate == False
    
    def test_should_escalate_critical_state(self):
        """Test escalation check with critical state."""
        protocol = IntrospectionProtocol("test_session")
        
        activation_state = {
            "CMC_bitemporal": 0.05,  # Very cold
            "VIF_provenance": 0.1  # Very cold
        }
        
        attention_metrics = {
            "cognitive_load": 0.98,  # Very high
            "error_rate": 0.8  # Very high
        }
        
        should_escalate = protocol.should_escalate(
            activation_state=activation_state,
            attention_metrics=attention_metrics,
            recent_failures=["critical_error", "multiple_failures"]
        )
        
        assert should_escalate == True
    
    def test_get_introspection_history(self):
        """Test retrieving introspection history."""
        protocol = IntrospectionProtocol("test_session")
        
        # Perform some introspections
        result1 = protocol.perform_hourly_check(
            activation_state={"CMC_bitemporal": 0.9},
            attention_metrics={"cognitive_load": 0.5},
            recent_failures=[]
        )
        
        result2 = protocol.perform_hourly_check(
            activation_state={"CMC_bitemporal": 0.8},
            attention_metrics={"cognitive_load": 0.6},
            recent_failures=[]
        )
        
        history = protocol.get_introspection_history(hours_back=24)
        
        assert len(history) >= 2
        assert any(r.introspection_id == result1.introspection_id for r in history)
        assert any(r.introspection_id == result2.introspection_id for r in history)


class TestIntrospectionResult:
    
    def test_initialization(self):
        """Test IntrospectionResult initialization."""
        result = IntrospectionResult(
            introspection_id="test_introspection_001",
            session_id="test_session",
            timestamp=datetime.now(UTC),
            introspection_type=IntrospectionType.HOURLY_CHECK,
            overall_status=IntrospectionStatus.EXCELLENT,
            overall_score=0.95
        )
        
        assert result.introspection_id == "test_introspection_001"
        assert result.session_id == "test_session"
        assert result.introspection_type == IntrospectionType.HOURLY_CHECK
        assert result.overall_status == IntrospectionStatus.EXCELLENT
        assert result.overall_score == 0.95
        assert len(result.checks) == 0
        assert result.total_checks == 0
    
    def test_is_healthy_excellent(self):
        """Test is_healthy with excellent status."""
        result = IntrospectionResult(
            introspection_id="test_001",
            session_id="test_session",
            timestamp=datetime.now(UTC),
            introspection_type=IntrospectionType.HOURLY_CHECK,
            overall_status=IntrospectionStatus.EXCELLENT,
            overall_score=0.95,
            critical_issues=0,
            immediate_actions=[]
        )
        
        assert result.is_healthy() == True
    
    def test_is_healthy_good(self):
        """Test is_healthy with good status."""
        result = IntrospectionResult(
            introspection_id="test_001",
            session_id="test_session",
            timestamp=datetime.now(UTC),
            introspection_type=IntrospectionType.HOURLY_CHECK,
            overall_status=IntrospectionStatus.GOOD,
            overall_score=0.8,
            critical_issues=0,
            immediate_actions=[]
        )
        
        assert result.is_healthy() == True
    
    def test_is_healthy_critical(self):
        """Test is_healthy with critical status."""
        result = IntrospectionResult(
            introspection_id="test_001",
            session_id="test_session",
            timestamp=datetime.now(UTC),
            introspection_type=IntrospectionType.HOURLY_CHECK,
            overall_status=IntrospectionStatus.CRITICAL,
            overall_score=0.2,
            critical_issues=2,
            immediate_actions=["Immediate action required"]
        )
        
        assert result.is_healthy() == False
    
    def test_is_healthy_with_actions(self):
        """Test is_healthy with immediate actions."""
        result = IntrospectionResult(
            introspection_id="test_001",
            session_id="test_session",
            timestamp=datetime.now(UTC),
            introspection_type=IntrospectionType.HOURLY_CHECK,
            overall_status=IntrospectionStatus.GOOD,
            overall_score=0.8,
            critical_issues=0,
            immediate_actions=["Action needed"]
        )
        
        assert result.is_healthy() == False


class TestIntrospectionCheck:
    
    def test_initialization(self):
        """Test IntrospectionCheck initialization."""
        check = IntrospectionCheck(
            check_name="Test Check",
            status=IntrospectionStatus.EXCELLENT,
            score=0.95,
            details="Test check details"
        )
        
        assert check.check_name == "Test Check"
        assert check.status == IntrospectionStatus.EXCELLENT
        assert check.score == 0.95
        assert check.details == "Test check details"
        assert len(check.recommendations) == 0
        assert len(check.evidence) == 0
    
    def test_with_recommendations(self):
        """Test IntrospectionCheck with recommendations."""
        check = IntrospectionCheck(
            check_name="Principle Activation",
            status=IntrospectionStatus.FAIR,
            score=0.6,
            details="Some principles cold",
            recommendations=["Activate CMC_bitemporal", "Review principle relevance"],
            evidence=["CMC_bitemporal activation: 0.2"]
        )
        
        assert len(check.recommendations) == 2
        assert len(check.evidence) == 1


class TestIntrospectionType:
    
    def test_introspection_type_enum(self):
        """Test IntrospectionType enum values."""
        assert IntrospectionType.HOURLY_CHECK == "hourly_check"
        assert IntrospectionType.TASK_COMPLETION == "task_completion"
        assert IntrospectionType.FAILURE_ANALYSIS == "failure_analysis"
        assert IntrospectionType.PRINCIPLE_REVIEW == "principle_review"
        assert IntrospectionType.PROTOCOL_VALIDATION == "protocol_validation"
        assert IntrospectionType.COGNITIVE_LOAD_ASSESSMENT == "cognitive_load_assessment"


class TestIntrospectionStatus:
    
    def test_introspection_status_enum(self):
        """Test IntrospectionStatus enum values."""
        assert IntrospectionStatus.EXCELLENT == "excellent"
        assert IntrospectionStatus.GOOD == "good"
        assert IntrospectionStatus.FAIR == "fair"
        assert IntrospectionStatus.POOR == "poor"
        assert IntrospectionStatus.CRITICAL == "critical"


class TestIntrospectionIntegration:
    
    def test_complete_introspection_workflow(self):
        """Test complete introspection workflow."""
        protocol = IntrospectionProtocol("integration_session")
        
        # Record some violations
        protocol.record_principle_violation(
            principle="CMC_bitemporal",
            violation_type="file_overwrite",
            context="Test violation"
        )
        
        # Perform hourly check
        result = protocol.perform_hourly_check(
            activation_state={
                "CMC_bitemporal": 0.85,
                "VIF_provenance": 0.8,
                "SDF_quartet": 0.9
            },
            attention_metrics={
                "cognitive_load": 0.6,
                "focus_depth": 0.75,
                "attention_stability": 0.8,
                "error_rate": 0.1
            },
            recent_failures=["minor_error"],
            current_task="Integration test task"
        )
        
        # Verify result
        assert isinstance(result, IntrospectionResult)
        assert result.session_id == "integration_session"
        assert result.introspection_type == IntrospectionType.HOURLY_CHECK
        assert len(result.checks) > 0
        assert result.total_checks > 0
        assert result.passed_checks + result.failed_checks == result.total_checks
        
        # Test escalation
        should_escalate = protocol.should_escalate(
            activation_state={"CMC_bitemporal": 0.85},
            attention_metrics={"cognitive_load": 0.6, "error_rate": 0.1},
            recent_failures=[]
        )
        assert isinstance(should_escalate, bool)
        
        # Test history retrieval
        history = protocol.get_introspection_history(hours_back=24)
        assert len(history) >= 1
        assert any(r.introspection_id == result.introspection_id for r in history)
        
        # Test post-failure analysis
        failure_result = protocol.perform_post_failure_analysis(
            failure_description="Test failure",
            failure_type="categorization_error",
            context="Test context",
            error_rate=0.2
        )
        
        assert isinstance(failure_result, IntrospectionResult)
        assert failure_result.introspection_type == IntrospectionType.FAILURE_ANALYSIS
        assert len(failure_result.immediate_actions) > 0

