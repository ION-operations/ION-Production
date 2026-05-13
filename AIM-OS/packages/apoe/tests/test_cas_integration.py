"""Tests for APOE CAS Integration

Tests cognitive analysis and introspection for APOE operations.
"""

from __future__ import annotations
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from apoe.models import Step, StepStatus, Budget
from apoe.acl_parser import ExecutionPlan
from apoe.cas_integration import APOECASIntegration


class TestAPOECASIntegration:
    """Test CAS integration functionality."""
    
    @pytest.fixture
    def integration(self):
        """Create CAS integration instance."""
        return APOECASIntegration(session_id="test_session")
    
    @pytest.fixture
    def sample_plan(self):
        """Create sample execution plan."""
        step = Step(
            name="test_step",
            role="planner",
            inputs={},
            outputs={}
        )
        
        return ExecutionPlan(
            name="test_plan",
            steps=[step],
            roles={},
            gates=[],
            dependencies={}
        )
    
    def test_init_with_cas_available(self):
        """Test initialization when CAS is available."""
        with patch('apoe.cas_integration.CAS_AVAILABLE', True):
            integration = APOECASIntegration()
            assert integration.cas_available is True
    
    def test_init_without_cas(self):
        """Test initialization when CAS is not available."""
        with patch('apoe.cas_integration.CAS_AVAILABLE', False):
            integration = APOECASIntegration()
            assert integration.cas_available is False
    
    def test_introspect_safety_decision_success(self, integration):
        """Test successful safety decision introspection."""
        if not integration.cas_available:
            pytest.skip("CAS not available")
        
        result = integration.introspect_safety_decision(
            decision_context={"risk": "medium"},
            safety_level="medium",
            risk_assessment={"level": "medium"}
        )
        
        assert "introspected" in result
        assert "healthy" in result
        assert "recommendation" in result
    
    def test_introspect_safety_decision_high_risk(self, integration):
        """Test safety decision introspection for high risk."""
        if not integration.cas_available:
            pytest.skip("CAS not available")
        
        result = integration.introspect_safety_decision(
            decision_context={"risk": "high"},
            safety_level="high",
            risk_assessment={"level": "high"}
        )
        
        assert "introspected" in result
        assert "failure_analysis" in result
    
    def test_introspect_safety_decision_no_cas(self):
        """Test safety decision introspection when CAS not available."""
        with patch('apoe.cas_integration.CAS_AVAILABLE', False):
            integration = APOECASIntegration()
            result = integration.introspect_safety_decision(
                decision_context={},
                safety_level="low",
                risk_assessment={}
            )
            
            assert result["introspected"] is False
            assert "CAS not available" in result["error"]
    
    def test_introspect_policy_decision_success(self, integration):
        """Test successful policy decision introspection."""
        if not integration.cas_available:
            pytest.skip("CAS not available")
        
        result = integration.introspect_policy_decision(
            decision_context={"policy": "compliance"},
            policy_type="compliance",
            compliance_status="compliant"
        )
        
        assert "introspected" in result
        assert "healthy" in result
        assert "recommendation" in result
    
    def test_introspect_policy_decision_non_compliant(self, integration):
        """Test policy decision introspection for non-compliant status."""
        if not integration.cas_available:
            pytest.skip("CAS not available")
        
        result = integration.introspect_policy_decision(
            decision_context={"policy": "compliance"},
            policy_type="compliance",
            compliance_status="non-compliant"
        )
        
        assert "introspected" in result
        assert "failure_analysis" in result
    
    def test_analyze_planning_decision(self, integration, sample_plan):
        """Test planning decision analysis."""
        if not integration.cas_available:
            pytest.skip("CAS not available")
        
        result = integration.analyze_planning_decision(
            plan=sample_plan,
            planning_strategy={"approach": "sequential"},
            alternatives=[{"approach": "parallel"}, {"approach": "sequential"}]
        )
        
        assert "analyzed" in result
        assert "healthy" in result
        assert "category" in result
        assert "decision_quality" in result
        assert "recommendation" in result
    
    def test_introspect_critique_decision(self, integration):
        """Test critique decision introspection."""
        if not integration.cas_available:
            pytest.skip("CAS not available")
        
        result = integration.introspect_critique_decision(
            critique_context={"target": "code"},
            critique_result={"quality": "good"}
        )
        
        assert "introspected" in result
        assert "healthy" in result
        assert "recommendation" in result
    
    def test_analyze_operational_decision(self, integration):
        """Test operational decision analysis."""
        if not integration.cas_available:
            pytest.skip("CAS not available")
        
        result = integration.analyze_operational_decision(
            operation_context={"description": "deploy_service"},
            operation_result={"success": True}
        )
        
        assert "analyzed" in result
        assert "healthy" in result
        assert "category" in result
        assert "recommendation" in result
    
    def test_analyze_resource_patterns(self, integration):
        """Test resource pattern analysis."""
        if not integration.cas_available:
            pytest.skip("CAS not available")
        
        budget_history = [
            Budget(tokens=1000, time=10.0, tools=1),
            Budget(tokens=2000, time=20.0, tools=2),
            Budget(tokens=1500, time=15.0, tools=1)
        ]
        
        resource_usage = {
            "token_limit": 10000,
            "time_limit": 100.0
        }
        
        result = integration.analyze_resource_patterns(
            budget_history=budget_history,
            resource_usage=resource_usage
        )
        
        assert "analyzed" in result
        assert "patterns" in result
        assert "recommendation" in result
    
    def test_analyze_resource_patterns_empty_history(self, integration):
        """Test resource pattern analysis with empty history."""
        if not integration.cas_available:
            pytest.skip("CAS not available")
        
        result = integration.analyze_resource_patterns(
            budget_history=[],
            resource_usage={}
        )
        
        assert "analyzed" in result
        assert result["patterns"]["needs_optimization"] is False
    
    def test_error_handling(self, integration):
        """Test error handling in integration methods."""
        if not integration.cas_available:
            pytest.skip("CAS not available")
        
        # Test with invalid inputs that might cause errors
        result = integration.introspect_safety_decision(
            decision_context=None,  # Invalid input
            safety_level="invalid",
            risk_assessment=None
        )
        
        # Should handle gracefully
        assert "introspected" in result
        # Either successful with warnings or failed with error

