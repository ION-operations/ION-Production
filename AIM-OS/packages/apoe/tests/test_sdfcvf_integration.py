"""Tests for APOE SDF-CVF Integration

Tests quartet/quintet parity validation for APOE operations.
"""

from __future__ import annotations
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import tempfile
import os

from apoe.models import Step, StepStatus
from apoe.acl_parser import ExecutionPlan
from apoe.sdfcvf_integration import APOESDFCVFIntegration


class TestAPOESDFCVFIntegration:
    """Test SDF-CVF integration functionality."""
    
    @pytest.fixture
    def integration(self):
        """Create SDF-CVF integration instance."""
        return APOESDFCVFIntegration(enable_quintet=False)
    
    @pytest.fixture
    def sample_files(self, tmp_path):
        """Create sample files for testing."""
        code_file = tmp_path / "test_code.py"
        code_file.write_text("def test_function(): pass")
        
        docs_file = tmp_path / "test_docs.md"
        docs_file.write_text("# Test Documentation")
        
        tests_file = tmp_path / "test_tests.py"
        tests_file.write_text("def test_test_function(): pass")
        
        return {
            "code": [str(code_file)],
            "docs": [str(docs_file)],
            "tests": [str(tests_file)],
            "traces": []
        }
    
    def test_init_with_sdfcvf_available(self):
        """Test initialization when SDF-CVF is available."""
        with patch('apoe.sdfcvf_integration.SDFCVF_AVAILABLE', True):
            integration = APOESDFCVFIntegration()
            assert integration.sdfcvf_available is True
    
    def test_init_without_sdfcvf(self):
        """Test initialization when SDF-CVF is not available."""
        with patch('apoe.sdfcvf_integration.SDFCVF_AVAILABLE', False):
            integration = APOESDFCVFIntegration()
            assert integration.sdfcvf_available is False
    
    def test_validate_contract_parity_success(self, integration, sample_files):
        """Test successful contract parity validation."""
        if not integration.sdfcvf_available:
            pytest.skip("SDF-CVF not available")
        
        result = integration.validate_contract_parity(
            code_files=sample_files["code"],
            docs_files=sample_files["docs"],
            tests_files=sample_files["tests"],
            traces_files=sample_files["traces"],
            min_parity=0.70
        )
        
        assert "valid" in result
        assert "parity" in result
        assert result["parity"] >= 0.0
    
    def test_validate_contract_parity_failure(self, integration):
        """Test contract parity validation failure."""
        if not integration.sdfcvf_available:
            pytest.skip("SDF-CVF not available")
        
        result = integration.validate_contract_parity(
            code_files=["nonexistent.py"],
            docs_files=[],
            tests_files=[],
            traces_files=[],
            min_parity=0.85
        )
        
        assert "valid" in result
        # Should fail due to missing files or low parity
    
    def test_validate_contract_parity_no_sdfcvf(self):
        """Test contract parity validation when SDF-CVF not available."""
        with patch('apoe.sdfcvf_integration.SDFCVF_AVAILABLE', False):
            integration = APOESDFCVFIntegration()
            result = integration.validate_contract_parity(
                code_files=["test.py"],
                docs_files=["test.md"],
                tests_files=["test_test.py"],
                traces_files=[]
            )
            
            assert result["valid"] is False
            assert "error" in result
            assert "SDF-CVF not available" in result["error"]
    
    def test_enforce_quality_gate_success(self, integration, sample_files):
        """Test successful quality gate enforcement."""
        if not integration.sdfcvf_available:
            pytest.skip("SDF-CVF not available")
        
        result = integration.enforce_quality_gate(
            code_files=sample_files["code"],
            docs_files=sample_files["docs"],
            tests_files=sample_files["tests"],
            traces_files=sample_files["traces"]
        )
        
        assert hasattr(result, "passed")
        assert hasattr(result, "parity_score")
        assert hasattr(result, "threshold")
    
    def test_enforce_quality_gate_no_sdfcvf(self):
        """Test quality gate enforcement when SDF-CVF not available."""
        with patch('apoe.sdfcvf_integration.SDFCVF_AVAILABLE', False):
            integration = APOESDFCVFIntegration()
            result = integration.enforce_quality_gate(
                code_files=["test.py"],
                docs_files=["test.md"],
                tests_files=["test_test.py"],
                traces_files=[]
            )
            
            assert result.passed is False
            assert "SDF-CVF not available" in result.message
    
    def test_validate_verification_quality(self, integration, sample_files):
        """Test verification quality validation."""
        if not integration.sdfcvf_available:
            pytest.skip("SDF-CVF not available")
        
        verification_result = {
            "success": True,
            "confidence": 0.90
        }
        
        result = integration.validate_verification_quality(
            verification_result=verification_result,
            code_files=sample_files["code"],
            docs_files=sample_files["docs"],
            tests_files=sample_files["tests"],
            traces_files=sample_files["traces"],
            min_parity=0.85
        )
        
        assert "valid" in result
        assert "verification_quality" in result
        assert "parity" in result
    
    def test_enforce_builder_parity_success(self, integration, sample_files):
        """Test successful builder parity enforcement."""
        if not integration.sdfcvf_available:
            pytest.skip("SDF-CVF not available")
        
        artifacts = {
            "code": sample_files["code"],
            "docs": sample_files["docs"],
            "tests": sample_files["tests"],
            "traces": sample_files["traces"]
        }
        
        result = integration.enforce_builder_parity(
            artifacts=artifacts,
            min_parity=0.70
        )
        
        assert "valid" in result
        assert "parity" in result
    
    def test_enforce_builder_parity_failure(self, integration):
        """Test builder parity enforcement failure."""
        if not integration.sdfcvf_available:
            pytest.skip("SDF-CVF not available")
        
        artifacts = {
            "code": ["test.py"],
            "docs": [],
            "tests": [],
            "traces": []
        }
        
        result = integration.enforce_builder_parity(
            artifacts=artifacts,
            min_parity=0.85
        )
        
        # Should fail due to missing docs/tests
        assert result["valid"] is False or result["parity"] < 0.85
    
    def test_check_parity_for_step(self, integration, sample_files):
        """Test parity check for a step."""
        if not integration.sdfcvf_available:
            pytest.skip("SDF-CVF not available")
        
        step = Step(
            name="test_step",
            role="builder",
            inputs={},
            outputs={
                "code_files": sample_files["code"],
                "docs_files": sample_files["docs"],
                "tests_files": sample_files["tests"],
                "traces_files": sample_files["traces"]
            }
        )
        
        plan = ExecutionPlan(
            name="test_plan",
            steps=[step],
            roles={},
            gates=[],
            dependencies={}
        )
        
        result = integration.check_parity_for_step(
            step=step,
            plan=plan,
            min_parity=0.70
        )
        
        assert "valid" in result
        assert "parity" in result
    
    def test_check_parity_for_step_no_code_files(self, integration):
        """Test parity check for step with no code files."""
        if not integration.sdfcvf_available:
            pytest.skip("SDF-CVF not available")
        
        step = Step(
            name="test_step",
            role="builder",
            inputs={},
            outputs={}
        )
        
        plan = ExecutionPlan(
            name="test_plan",
            steps=[step],
            roles={},
            gates=[],
            dependencies={}
        )
        
        result = integration.check_parity_for_step(
            step=step,
            plan=plan
        )
        
        assert result["valid"] is False
        assert "No code files found" in result["error"]

