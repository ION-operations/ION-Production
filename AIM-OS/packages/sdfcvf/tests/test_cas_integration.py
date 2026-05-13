"""Tests for CAS integration"""

import pytest

from sdfcvf.cas_integration import CASIntegration


class TestCASIntegration:
    """Test CAS integration functionality"""
    
    def test_cas_integration_initialization_no_cas(self):
        """Test CAS integration initialization when CAS not available"""
        integration = CASIntegration()
        assert integration.cas_available is False
        assert integration.cas is None
    
    def test_report_quality_metrics_no_cas(self):
        """Test reporting quality metrics when CAS not available"""
        integration = CASIntegration()
        result = integration.report_quality_metrics({"parity_score": 0.95})
        assert result["reported"] is False
        assert "error" in result
    
    def test_analyze_failure_patterns_no_cas(self):
        """Test analyzing failure patterns when CAS not available"""
        integration = CASIntegration()
        result = integration.analyze_failure_patterns({"failure": "data"})
        assert result["analysis_available"] is False
        assert "error" in result
    
    def test_detect_cognitive_drift_no_cas(self):
        """Test detecting cognitive drift when CAS not available"""
        integration = CASIntegration()
        result = integration.detect_cognitive_drift({"parity_score": 0.95})
        assert result["drift_detected"] is False
        assert "error" in result
    
    def test_get_introspection_analysis_no_cas(self):
        """Test getting introspection analysis when CAS not available"""
        integration = CASIntegration()
        result = integration.get_introspection_analysis("test_operation")
        assert result["analysis_available"] is False
        assert "error" in result

