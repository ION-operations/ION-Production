"""Tests for HHNI integration"""

import pytest

from sdfcvf.hhni_integration import HHNIIntegration


class TestHHNIIntegration:
    """Test HHNI integration functionality"""
    
    def test_hhni_integration_initialization_no_hhni(self):
        """Test HHNI integration initialization when HHNI not available"""
        integration = HHNIIntegration()
        assert integration.hhni_available is False
        assert integration.hhni is None
    
    def test_get_change_context_no_hhni(self):
        """Test getting change context when HHNI not available"""
        integration = HHNIIntegration()
        result = integration.get_change_context(["file1.py", "file2.py"])
        assert result["context_available"] is False
        assert "error" in result
    
    def test_query_impact_analysis_no_hhni(self):
        """Test querying impact analysis when HHNI not available"""
        integration = HHNIIntegration()
        result = integration.query_impact_analysis(["file1.py"])
        assert result["analysis_available"] is False
        assert "error" in result
    
    def test_detect_evolution_patterns_no_hhni(self):
        """Test detecting evolution patterns when HHNI not available"""
        integration = HHNIIntegration()
        result = integration.detect_evolution_patterns("test-quartet-1")
        assert result == []
    
    def test_check_consistency_no_hhni(self):
        """Test checking consistency when HHNI not available"""
        integration = HHNIIntegration()
        result = integration.check_consistency("test-quartet-1")
        assert result["consistent"] is False
        assert "error" in result

