"""Tests for VIF-SDF-CVF integration"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
import tempfile
import json

from vif.witness import VIF, ConfidenceBand, TaskCriticality
from vif.sdfcvf_integration import (
    vif_witness_to_trace_text,
    collect_witnesses_for_file,
    create_trace_file_from_witnesses,
    calculate_parity_with_vif_traces,
    combine_confidence_and_parity,
    get_nl_tags_from_witnesses,
    ParityQualityResult,
)


def test_vif_witness_to_trace_text():
    """Test converting VIF witness to trace text"""
    vif = VIF(
        model_id="gpt-4-turbo",
        model_provider="openai",
        context_snapshot_id="snap_123",
        prompt_hash="hash1234567890abcdef",
        prompt_tokens=10,
        confidence_score=0.95,
        confidence_band=ConfidenceBand.A,
        output_hash="hash0987654321fedcba",
        output_tokens=5,
        total_tokens=15,
        task_criticality=TaskCriticality.CRITICAL,
        kappa_gate_passed=True,
        kappa_threshold=0.95,
    )
    
    trace_text = vif_witness_to_trace_text(vif)
    
    assert isinstance(trace_text, str)
    assert vif.id in trace_text
    assert "gpt-4-turbo" in trace_text
    assert "openai" in trace_text
    assert "0.95" in trace_text
    assert "A" in trace_text
    assert "CRITICAL" in trace_text
    assert "PASSED" in trace_text


def test_vif_witness_to_trace_text_with_tools():
    """Test trace text includes tool information"""
    vif = VIF(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap_123",
        prompt_hash="hash1",
        prompt_tokens=10,
        confidence_score=0.95,
        confidence_band=ConfidenceBand.A,
        output_hash="hash2",
        output_tokens=5,
        total_tokens=15,
        tool_ids=["tool1", "tool2"],
    )
    
    trace_text = vif_witness_to_trace_text(vif)
    
    assert "tool1" in trace_text
    assert "tool2" in trace_text


def test_vif_witness_to_trace_text_with_ece():
    """Test trace text includes ECE score"""
    vif = VIF(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap_123",
        prompt_hash="hash1",
        prompt_tokens=10,
        confidence_score=0.95,
        confidence_band=ConfidenceBand.A,
        output_hash="hash2",
        output_tokens=5,
        total_tokens=15,
        ece_score=0.05,
    )
    
    trace_text = vif_witness_to_trace_text(vif)
    
    assert "ECE" in trace_text
    assert "0.05" in trace_text


def test_collect_witnesses_for_file():
    """Test collecting witnesses for a file"""
    # Create mock VIFStore
    mock_store = Mock()
    
    witness1 = VIF(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap_1",
        prompt_hash="hash1",
        prompt_tokens=10,
        confidence_score=0.95,
        confidence_band=ConfidenceBand.A,
        output_hash="hash2",
        output_tokens=5,
        total_tokens=15,
    )
    
    witness2 = VIF(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap_2",
        prompt_hash="hash3",
        prompt_tokens=10,
        confidence_score=0.90,
        confidence_band=ConfidenceBand.A,
        output_hash="hash4",
        output_tokens=5,
        total_tokens=15,
    )
    
    mock_store.query_witnesses = Mock(return_value=[witness1, witness2])
    
    witnesses = collect_witnesses_for_file("test_file.py", vif_store=mock_store, limit=10)
    
    assert len(witnesses) == 2
    assert witness1 in witnesses
    assert witness2 in witnesses
    mock_store.query_witnesses.assert_called_once()


def test_create_trace_file_from_witnesses():
    """Test creating trace file from witnesses"""
    witness1 = VIF(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap_1",
        prompt_hash="hash1",
        prompt_tokens=10,
        confidence_score=0.95,
        confidence_band=ConfidenceBand.A,
        output_hash="hash2",
        output_tokens=5,
        total_tokens=15,
    )
    
    witness2 = VIF(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap_2",
        prompt_hash="hash3",
        prompt_tokens=10,
        confidence_score=0.90,
        confidence_band=ConfidenceBand.A,
        output_hash="hash4",
        output_tokens=5,
        total_tokens=15,
    )
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        trace_file = create_trace_file_from_witnesses(
            witnesses=[witness1, witness2],
            output_dir=output_dir,
            file_name="test_trace.txt"
        )
        
        assert trace_file.exists()
        assert trace_file.name == "test_trace.txt"
        
        # Read and verify content
        content = trace_file.read_text()
        assert witness1.id in content
        assert witness2.id in content


def test_calculate_parity_with_vif_traces():
    """Test calculating parity with VIF traces"""
    # Create mock ParityCalculator
    mock_calculator = Mock()
    mock_calculator.calculate_parity = Mock(return_value=Mock(
        code_doc_similarity=0.85,
        code_test_similarity=0.80,
        doc_test_similarity=0.75,
        overall_parity=0.80,
    ))
    
    with tempfile.TemporaryDirectory() as tmpdir:
        code_file = Path(tmpdir) / "code.py"
        doc_file = Path(tmpdir) / "doc.md"
        test_file = Path(tmpdir) / "test.py"
        trace_file = Path(tmpdir) / "trace.txt"
        
        # Create dummy files
        code_file.write_text("def test(): pass")
        doc_file.write_text("# Test function")
        test_file.write_text("def test_test(): pass")
        trace_file.write_text("VIF Witness: test_id")
        
        result = calculate_parity_with_vif_traces(
            code_file=code_file,
            doc_file=doc_file,
            test_file=test_file,
            trace_files=[trace_file],
            parity_calculator=mock_calculator,
        )
        
        assert result is not None
        assert result.overall_parity == 0.80
        mock_calculator.calculate_parity.assert_called_once()


def test_combine_confidence_and_parity():
    """Test combining VIF confidence with parity score"""
    result = combine_confidence_and_parity(
        vif_confidence=0.95,
        parity_score=0.80,
        confidence_weight=0.4,
    )
    
    assert isinstance(result, ParityQualityResult)
    assert result.vif_confidence == 0.95
    assert result.parity_score == 0.80
    assert result.combined_score is not None
    assert 0.0 <= result.combined_score <= 1.0


def test_combine_confidence_and_parity_default_weight():
    """Test combining with default confidence weight"""
    result = combine_confidence_and_parity(
        vif_confidence=0.90,
        parity_score=0.85,
    )
    
    assert result.combined_score is not None


def test_get_nl_tags_from_witnesses():
    """Test extracting NL tags from witnesses"""
    witness1 = VIF(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap_1",
        prompt_hash="hash1",
        prompt_tokens=10,
        confidence_score=0.95,
        confidence_band=ConfidenceBand.A,
        output_hash="hash2",
        output_tokens=5,
        total_tokens=15,
        tool_parameters={
            "nl_tags": ["VIF-WITNESS-001", "VIF-CMC-002"]
        }
    )
    
    witness2 = VIF(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap_2",
        prompt_hash="hash3",
        prompt_tokens=10,
        confidence_score=0.90,
        confidence_band=ConfidenceBand.A,
        output_hash="hash4",
        output_tokens=5,
        total_tokens=15,
        tool_parameters={
            "nl_tags": ["VIF-HHNI-001", "VIF-SEG-002"]
        }
    )
    
    tags = get_nl_tags_from_witnesses([witness1, witness2])
    
    assert len(tags) == 4
    assert "VIF-WITNESS-001" in tags
    assert "VIF-CMC-002" in tags
    assert "VIF-HHNI-001" in tags
    assert "VIF-SEG-002" in tags


def test_get_nl_tags_from_witnesses_no_tags():
    """Test extracting NL tags when witnesses have no tags"""
    witness = VIF(
        model_id="gpt-4",
        model_provider="openai",
        context_snapshot_id="snap_1",
        prompt_hash="hash1",
        prompt_tokens=10,
        confidence_score=0.95,
        confidence_band=ConfidenceBand.A,
        output_hash="hash2",
        output_tokens=5,
        total_tokens=15,
    )
    
    tags = get_nl_tags_from_witnesses([witness])
    
    assert len(tags) == 0


def test_parity_quality_result_dataclass():
    """Test ParityQualityResult dataclass"""
    result = ParityQualityResult(
        vif_confidence=0.95,
        parity_score=0.80,
        combined_score=0.86,
    )
    
    assert result.vif_confidence == 0.95
    assert result.parity_score == 0.80
    assert result.combined_score == 0.86

