"""Tests for SEG integration"""

import pytest

from sdfcvf.seg_integration import SEGIntegration


class TestSEGIntegration:
    """Test SEG integration functionality"""
    
    def test_seg_integration_initialization_no_seg(self):
        """Test SEG integration initialization when SEG not available"""
        integration = SEGIntegration()
        assert integration.seg_available is False
        assert integration.seg is None
    
    def test_link_trace_to_evidence_node_no_seg(self):
        """Test linking trace to evidence node when SEG not available"""
        integration = SEGIntegration()
        result = integration.link_trace_to_evidence_node("trace-1", "evidence-1")
        assert result is None
    
    def test_store_evolution_artifact_no_seg(self):
        """Test storing evolution artifact when SEG not available"""
        integration = SEGIntegration()
        result = integration.store_evolution_artifact(
            "parity_result",
            {"parity_score": 0.95},
            "test-quartet-1"
        )
        assert result is None
    
    def test_validate_consistency_no_seg(self):
        """Test validating consistency when SEG not available"""
        integration = SEGIntegration()
        result = integration.validate_consistency("test-quartet-1")
        assert result["valid"] is False
        assert "error" in result
    
    def test_generate_consistency_report_no_seg(self):
        """Test generating consistency report when SEG not available"""
        integration = SEGIntegration()
        result = integration.generate_consistency_report("test-quartet-1")
        assert result["valid"] is False
        assert "error" in result

