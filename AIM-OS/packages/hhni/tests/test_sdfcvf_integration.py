"""Tests for HHNI ↔ SDF-CVF integration"""

import pytest
import os
from pathlib import Path

from packages.hhni.sdfcvf_integration import (
    validate_retrieval_parity,
    filter_by_parity,
    add_parity_metadata_to_result,
    QuartetParityInfo
)


class TestSDFCVFIntegration:
    """Test SDF-CVF integration functionality"""
    
    def test_validate_retrieval_parity_no_sdfcvf(self, monkeypatch):
        """Test validation when SDF-CVF not available"""
        # Mock SDF-CVF as unavailable
        import packages.hhni.sdfcvf_integration as mod
        original = mod.SDFCVF_AVAILABLE
        mod.SDFCVF_AVAILABLE = False
        
        try:
            result = validate_retrieval_parity(["test_file.py"])
            assert len(result) == 1
            assert "test_file.py" in result
            assert result["test_file.py"].validation_error == "SDF-CVF not available"
        finally:
            mod.SDFCVF_AVAILABLE = original
    
    def test_validate_retrieval_parity_with_sdfcvf(self):
        """Test validation when SDF-CVF is available"""
        # Only run if SDF-CVF is available
        try:
            from packages.sdfcvf.quartet import QuartetDetector
            from packages.sdfcvf.parity import ParityCalculator
        except ImportError:
            pytest.skip("SDF-CVF not available")
        
        # Test with a real file (if available)
        test_file = "packages/hhni/retrieval.py"
        if Path(test_file).exists():
            result = validate_retrieval_parity([test_file])
            assert len(result) == 1
            assert test_file in result
            # Result may have validation_error if quartet incomplete (expected)
            assert isinstance(result[test_file], QuartetParityInfo)
    
    def test_filter_by_parity(self):
        """Test filtering by parity threshold"""
        parity_info = {
            "file1.py": QuartetParityInfo(
                file_path="file1.py",
                parity_score=0.95,
                passes_gate=True
            ),
            "file2.py": QuartetParityInfo(
                file_path="file2.py",
                parity_score=0.85,
                passes_gate=False
            ),
            "file3.py": QuartetParityInfo(
                file_path="file3.py",
                parity_score=0.92,
                passes_gate=True
            ),
        }
        
        files = ["file1.py", "file2.py", "file3.py"]
        filtered = filter_by_parity(files, parity_info, parity_threshold=0.90)
        
        # Should include file1 and file3 (pass gate), exclude file2
        assert "file1.py" in filtered
        assert "file3.py" in filtered
        assert "file2.py" not in filtered
    
    def test_add_parity_metadata_to_result(self):
        """Test adding parity metadata to retrieval result"""
        # Create mock RetrievalResult
        from dataclasses import dataclass, field
        from typing import Dict
        
        @dataclass
        class MockRetrievalResult:
            audit_trail: Dict[str, str] = field(default_factory=dict)
        
        result = MockRetrievalResult()
        
        parity_info = {
            "file1.py": QuartetParityInfo(
                file_path="file1.py",
                parity_score=0.95,
                passes_gate=True
            ),
            "file2.py": QuartetParityInfo(
                file_path="file2.py",
                parity_score=0.92,
                passes_gate=True
            ),
        }
        
        # Mock ParityResult
        try:
            from packages.sdfcvf.parity import ParityResult
            parity_info["file1.py"].parity_result = ParityResult(
                parity_score=0.95,
                code_docs_similarity=0.95,
                code_tests_similarity=0.95,
                code_traces_similarity=0.95,
                docs_tests_similarity=0.95,
                docs_traces_similarity=0.95,
                tests_traces_similarity=0.95,
                complete=True
            )
            parity_info["file2.py"].parity_result = ParityResult(
                parity_score=0.92,
                code_docs_similarity=0.92,
                code_tests_similarity=0.92,
                code_traces_similarity=0.92,
                docs_tests_similarity=0.92,
                docs_traces_similarity=0.92,
                tests_traces_similarity=0.92,
                complete=True
            )
        except ImportError:
            pytest.skip("SDF-CVF not available")
        
        add_parity_metadata_to_result(result, parity_info)
        
        assert "sdfcvf_parity_validation" in result.audit_trail
        assert result.audit_trail["sdfcvf_parity_validation"] == "enabled"
        assert "sdfcvf_avg_parity" in result.audit_trail
        assert "sdfcvf_passing_count" in result.audit_trail

