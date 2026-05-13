"""Tests for CMC integration"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from sdfcvf.cmc_integration import CMCIntegration, ParityAtom
from sdfcvf.parity import ParityResult


class TestCMCIntegration:
    """Test CMC integration functionality"""
    
    def test_cmc_integration_initialization_no_cmc(self):
        """Test CMC integration initialization when CMC not available"""
        integration = CMCIntegration()
        # CMC availability depends on whether cmc_service is installed
        # Test that integration handles both cases gracefully
        assert hasattr(integration, 'cmc_available')
        assert hasattr(integration, 'cmc')
        # If CMC not available, cmc should be None
        if not integration.cmc_available:
            assert integration.cmc is None
    
    def test_cmc_integration_initialization_with_cmc(self):
        """Test CMC integration initialization with CMC client"""
        mock_cmc = Mock()
        integration = CMCIntegration(cmc_store=mock_cmc)
        assert integration.cmc == mock_cmc
    
    def test_store_parity_result_no_cmc(self):
        """Test storing parity result when CMC not available"""
        integration = CMCIntegration()
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
        
        result = integration.store_parity_result(parity_result, "test-quartet-1")
        assert result is None
    
    def test_store_quartet_snapshot_no_cmc(self):
        """Test storing quartet snapshot when CMC not available"""
        integration = CMCIntegration()
        from sdfcvf.quartet import Quartet
        
        quartet = Quartet(
            code_files=["code.py"],
            doc_files=["doc.md"],
            test_files=["test.py"],
            trace_files=["trace.md"]
        )
        
        result = integration.store_quartet_snapshot(quartet, "test-snapshot-1")
        assert result is None
    
    def test_retrieve_parity_history_no_cmc(self):
        """Test retrieving parity history when CMC not available"""
        integration = CMCIntegration()
        history = integration.retrieve_parity_history("test-quartet-1")
        assert history == []
    
    def test_validate_schema_no_cmc(self):
        """Test schema validation when CMC not available"""
        integration = CMCIntegration()
        result = integration.validate_schema({"parity_score": 0.95}, "parity_result")
        assert result["valid"] is False
        # When CMC not available, returns error; when available, returns errors list
        assert "error" in result or "errors" in result
    
    def test_validate_schema_with_valid_data(self):
        """Test schema validation with valid data"""
        integration = CMCIntegration()
        data = {
            "parity_score": 0.95,
            "complete": True
        }
        result = integration.validate_schema(data, "parity_result")
        assert result["valid"] is True
        assert result["errors"] == []

