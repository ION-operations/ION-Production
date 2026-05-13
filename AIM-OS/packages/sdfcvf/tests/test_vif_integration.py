"""Tests for VIF integration"""

import pytest
from unittest.mock import Mock

from sdfcvf.vif_integration import VIFIntegration
from sdfcvf.parity import ParityResult


class TestVIFIntegration:
    """Test VIF integration functionality"""
    
    def test_vif_integration_initialization_no_vif(self):
        """Test VIF integration initialization when VIF not available"""
        integration = VIFIntegration()
        assert integration.vif_available is False
        assert integration.vif is None
    
    def test_create_trace_witness_no_vif(self):
        """Test creating trace witness when VIF not available"""
        integration = VIFIntegration()
        result = integration.create_trace_witness(
            "test_operation",
            {"input": "data"},
            {"output": "result"}
        )
        assert result is None
    
    def test_validate_change_request_no_vif(self):
        """Test validating change request when VIF not available"""
        integration = VIFIntegration()
        result = integration.validate_change_request({"confidence": 0.95})
        assert result["valid"] is False
        assert "error" in result
    
    def test_get_provenance_trace_no_vif(self):
        """Test getting provenance trace when VIF not available"""
        integration = VIFIntegration()
        result = integration.get_provenance_trace("test-quartet-1")
        assert result is None
    
    def test_generate_verification_report_no_vif(self):
        """Test generating verification report when VIF not available"""
        integration = VIFIntegration()
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
        
        result = integration.generate_verification_report(parity_result, "test-quartet-1")
        assert result["valid"] is False
        assert "error" in result

