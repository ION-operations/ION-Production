"""Tests for VIF-HHNI integration"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone

from vif.witness import VIF, ConfidenceBand, TaskCriticality
from vif.hhni_integration import (
    extract_rs_lift_metrics,
    store_rs_lift_in_witness,
    calculate_rs_lift_statistics,
    create_retrieval_witness,
    RSLiftMetrics,
    RSLiftStatistics,
)


# Mock RetrievalResult for testing
class MockRetrievalResult:
    def __init__(self, rs_lift=0.5, relevance_score=0.8, precision_at_k=None, efficiency=None):
        self.rs_lift = rs_lift
        self.relevance_score = relevance_score
        self.precision_at_k = precision_at_k
        self.efficiency = efficiency
        self.selected_items = []
        self.total_tokens = 100


def test_extract_rs_lift_metrics():
    """Test extracting RS-Lift metrics from HHNI RetrievalResult"""
    retrieval_result = MockRetrievalResult(rs_lift=0.5, relevance_score=0.8)
    
    metrics = extract_rs_lift_metrics(retrieval_result, "test query", "retrieval_123")
    
    assert isinstance(metrics, RSLiftMetrics)
    assert metrics.retrieval_id == "retrieval_123"
    assert metrics.query == "test query"
    assert metrics.rs_lift == 0.5
    assert metrics.dvns_relevance == 0.8
    assert metrics.baseline_relevance is not None


def test_extract_rs_lift_metrics_auto_id():
    """Test extracting RS-Lift metrics with auto-generated ID"""
    retrieval_result = MockRetrievalResult()
    
    metrics = extract_rs_lift_metrics(retrieval_result, "test query")
    
    assert metrics.retrieval_id is not None
    assert metrics.retrieval_id.startswith("retrieval_")


def test_extract_rs_lift_metrics_with_precision():
    """Test extracting RS-Lift metrics with precision_at_k"""
    retrieval_result = MockRetrievalResult(precision_at_k=0.9)
    
    metrics = extract_rs_lift_metrics(retrieval_result, "test query")
    
    assert metrics.precision_at_k == 0.9


def test_store_rs_lift_in_witness():
    """Test storing RS-Lift metrics in VIF witness"""
    vif = VIF(
        model_id="gpt-4-turbo",
        model_provider="openai",
        context_snapshot_id="snap_123",
        prompt_hash="hash1",
        prompt_tokens=10,
        confidence_score=0.95,
        confidence_band=ConfidenceBand.A,
        output_hash="hash2",
        output_tokens=5,
        total_tokens=15,
    )
    
    metrics = RSLiftMetrics(
        retrieval_id="retrieval_123",
        query="test query",
        rs_lift=0.5,
        dvns_relevance=0.8,
        baseline_relevance=0.53,
    )
    
    updated_vif = store_rs_lift_in_witness(vif, metrics)
    
    assert updated_vif.tool_parameters is not None
    assert "rs_lift_metrics" in updated_vif.tool_parameters
    stored_metrics = updated_vif.tool_parameters["rs_lift_metrics"]
    assert stored_metrics["retrieval_id"] == "retrieval_123"
    assert stored_metrics["rs_lift"] == 0.5


def test_calculate_rs_lift_statistics():
    """Test calculating RS-Lift statistics from VIF witnesses"""
    # Create mock VIFStore
    mock_store = Mock()
    
    # Create mock witnesses with RS-Lift metrics
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
            "rs_lift_metrics": {
                "retrieval_id": "retrieval_1",
                "rs_lift": 0.5,
                "dvns_relevance": 0.8,
            }
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
            "rs_lift_metrics": {
                "retrieval_id": "retrieval_2",
                "rs_lift": 0.7,
                "dvns_relevance": 0.9,
            }
        }
    )
    
    mock_store.query_witnesses = Mock(return_value=[witness1, witness2])
    
    stats = calculate_rs_lift_statistics(mock_store)
    
    assert isinstance(stats, RSLiftStatistics)
    assert stats.total_retrievals == 2
    assert stats.average_rs_lift == 0.6  # (0.5 + 0.7) / 2
    assert stats.min_rs_lift == 0.5
    assert stats.max_rs_lift == 0.7


def test_create_retrieval_witness():
    """Test creating VIF witness for HHNI retrieval operation"""
    retrieval_result = MockRetrievalResult(rs_lift=0.5, relevance_score=0.8)
    
    vif = create_retrieval_witness(
        retrieval_result=retrieval_result,
        context_snapshot_id="snap_123",
        confidence=0.95,
        query="test query",
    )
    
    assert isinstance(vif, VIF)
    assert vif.context_snapshot_id == "snap_123"
    assert vif.confidence_score == 0.95
    assert vif.tool_parameters is not None
    assert "rs_lift_metrics" in vif.tool_parameters
    assert vif.tool_parameters["rs_lift_metrics"]["rs_lift"] == 0.5


def test_create_retrieval_witness_default_confidence():
    """Test creating retrieval witness with default confidence"""
    retrieval_result = MockRetrievalResult()
    
    vif = create_retrieval_witness(
        retrieval_result=retrieval_result,
        context_snapshot_id="snap_123",
        query="test query",  # Query is required for RS-Lift extraction
    )
    
    assert vif.confidence_score == 0.95  # Default


def test_rs_lift_metrics_dataclass():
    """Test RSLiftMetrics dataclass"""
    metrics = RSLiftMetrics(
        retrieval_id="retrieval_123",
        query="test query",
        rs_lift=0.5,
        dvns_relevance=0.8,
        baseline_relevance=0.53,
        precision_at_k=0.9,
        efficiency=0.85,
    )
    
    assert metrics.retrieval_id == "retrieval_123"
    assert metrics.query == "test query"
    assert metrics.rs_lift == 0.5
    assert metrics.dvns_relevance == 0.8
    assert metrics.baseline_relevance == 0.53
    assert metrics.precision_at_k == 0.9
    assert metrics.efficiency == 0.85


def test_rs_lift_statistics_dataclass():
    """Test RSLiftStatistics dataclass"""
    stats = RSLiftStatistics(
        total_retrievals=10,
        average_rs_lift=0.6,
        median_rs_lift=0.65,
        min_rs_lift=0.3,
        max_rs_lift=0.9,
        positive_lift_count=8,
        negative_lift_count=1,
        zero_lift_count=1,
    )
    
    assert stats.total_retrievals == 10
    assert stats.average_rs_lift == 0.6
    assert stats.min_rs_lift == 0.3
    assert stats.max_rs_lift == 0.9
    assert stats.median_rs_lift == 0.65

