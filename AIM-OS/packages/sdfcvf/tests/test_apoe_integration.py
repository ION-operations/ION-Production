"""Tests for APOE integration"""

import pytest

from sdfcvf.apoe_integration import APOEIntegration
from sdfcvf.gates import GateResult
from sdfcvf.parity import ParityResult


class TestAPOEIntegration:
    """Test APOE integration functionality"""
    
    def test_apoe_integration_initialization_no_apoe(self):
        """Test APOE integration initialization when APOE not available"""
        integration = APOEIntegration()
        assert integration.apoe_available is False
        assert integration.apoe is None
    
    def test_report_quality_gate_status_no_apoe(self):
        """Test reporting quality gate status when APOE not available"""
        integration = APOEIntegration()
        gate_result = GateResult(
            passed=True,
            parity_score=0.95,
            threshold=0.90,
            reasons=["Gate passed"]
        )
        
        result = integration.report_quality_gate_status(gate_result)
        assert result["reported"] is False
        assert "error" in result
    
    def test_request_change_approval_no_apoe(self):
        """Test requesting change approval when APOE not available"""
        integration = APOEIntegration()
        parity_result = ParityResult(
            parity_score=0.95,
            code_docs_similarity=0.95,
            code_tests_similarity=0.95,
            code_traces_similarity=0.95,
            docs_tests_similarity=0.95,
            docs_traces_similarity=0.95,
            tests_traces_similarity=0.95,
            complete=True
        )
        
        result = integration.request_change_approval({}, parity_result)
        assert result["approved"] is False
        assert "error" in result
    
    def test_generate_evolution_recommendations_no_apoe(self):
        """Test generating evolution recommendations when APOE not available"""
        integration = APOEIntegration()
        parity_result = ParityResult(
            parity_score=0.95,
            code_docs_similarity=0.95,
            code_tests_similarity=0.95,
            code_traces_similarity=0.95,
            docs_tests_similarity=0.95,
            docs_traces_similarity=0.95,
            tests_traces_similarity=0.95,
            complete=True
        )
        
        result = integration.generate_evolution_recommendations(parity_result, "test-quartet-1")
        assert result == []
    
    def test_generate_compliance_report_no_apoe(self):
        """Test generating compliance report when APOE not available"""
        integration = APOEIntegration()
        parity_result = ParityResult(
            parity_score=0.95,
            code_docs_similarity=0.95,
            code_tests_similarity=0.95,
            code_traces_similarity=0.95,
            docs_tests_similarity=0.95,
            docs_traces_similarity=0.95,
            tests_traces_similarity=0.95,
            complete=True
        )
        
        result = integration.generate_compliance_report(parity_result, "test-quartet-1")
        assert result["compliant"] is False
        assert "error" in result

