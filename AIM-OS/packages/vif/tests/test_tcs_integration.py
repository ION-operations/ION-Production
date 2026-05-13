"""Tests for VIF-TCS integration"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone

from vif.witness import VIF, ConfidenceBand, TaskCriticality
from vif.kappa_gate import KappaGate, KappaGateResult
from vif.tcs_integration import (
    create_witness_timeline_entry,
    create_kappa_gate_timeline_entry,
    query_witness_timeline,
    query_snapshot_timeline,
    query_confidence_timeline,
    is_tcs_available,
)


def test_create_witness_timeline_entry():
    """Test creating timeline entry for VIF witness"""
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
        task_criticality=TaskCriticality.CRITICAL,
    )
    
    # Mock MCP tool function
    mock_add_entry = Mock(return_value={
        "success": True,
        "prompt_id": "vif_witness_test_id",
    })
    
    entry_id = create_witness_timeline_entry(vif, mock_add_entry)
    
    assert entry_id == "vif_witness_test_id"
    mock_add_entry.assert_called_once()
    
    # Verify call arguments
    call_args = mock_add_entry.call_args[0][0]
    assert call_args["prompt_id"].startswith("vif_witness_")
    assert call_args["context_state"]["witness_id"] == vif.id
    assert call_args["context_state"]["confidence_score"] == 0.95
    assert call_args["context_state"]["confidence_band"] == "A"


def test_create_witness_timeline_entry_no_tcs():
    """Test graceful degradation when TCS unavailable"""
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
    )
    
    entry_id = create_witness_timeline_entry(vif, None)
    
    assert entry_id is None


def test_create_kappa_gate_timeline_entry():
    """Test creating timeline entry for κ-gate event"""
    kappa_gate = KappaGate()
    gate_result = kappa_gate.check(
        confidence=0.90,
        task_criticality=TaskCriticality.CRITICAL,
    )
    
    # Mock MCP tool function
    mock_add_entry = Mock(return_value={
        "success": True,
        "prompt_id": "kappa_gate_test_id",
    })
    
    entry_id = create_kappa_gate_timeline_entry(
        kappa_gate=gate_result,  # Pass the result, not the gate instance
        task_criticality=TaskCriticality.CRITICAL,
        add_timeline_entry_fn=mock_add_entry,
        witness_id="witness_123",
    )
    
    assert entry_id == "kappa_gate_test_id"
    mock_add_entry.assert_called_once()
    
    # Verify call arguments
    call_args = mock_add_entry.call_args[0][0]
    assert call_args["prompt_id"].startswith("kappa_gate_")
    assert call_args["context_state"]["task_criticality"] == "CRITICAL"
    assert call_args["context_state"]["witness_id"] == "witness_123"


def test_create_kappa_gate_timeline_entry_no_tcs():
    """Test graceful degradation when TCS unavailable"""
    kappa_gate = KappaGate()
    
    entry_id = create_kappa_gate_timeline_entry(
        kappa_gate=kappa_gate,
        task_criticality=TaskCriticality.CRITICAL,
        add_timeline_entry_fn=None,
    )
    
    assert entry_id is None


def test_query_witness_timeline():
    """Test querying timeline for witness"""
    # Mock MCP tool function
    mock_get_entries = Mock(return_value=[
        {
            "prompt_id": "entry_1",
            "context_state": {
                "witness_id": "witness_123",
                "confidence_score": 0.95,
            },
            "metadata": {
                "vif_witness_id": "witness_123",
            }
        },
        {
            "prompt_id": "entry_2",
            "context_state": {
                "witness_id": "witness_456",
                "confidence_score": 0.90,
            },
            "metadata": {
                "vif_witness_id": "witness_456",
            }
        },
    ])
    
    entries = query_witness_timeline("witness_123", mock_get_entries, limit=10)
    
    assert len(entries) == 1
    assert entries[0]["context_state"]["witness_id"] == "witness_123"
    mock_get_entries.assert_called_once()


def test_query_witness_timeline_no_tcs():
    """Test graceful degradation when TCS unavailable"""
    entries = query_witness_timeline("witness_123", None)
    
    assert entries == []


def test_query_snapshot_timeline():
    """Test querying timeline for snapshot"""
    # Mock MCP tool function
    mock_get_entries = Mock(return_value=[
        {
            "prompt_id": "entry_1",
            "context_state": {
                "vif_context_snapshot_id": "snap_123",
                "confidence_score": 0.95,
            },
            "metadata": {
                "vif_context_snapshot_id": "snap_123",
            }
        },
    ])
    
    entries = query_snapshot_timeline("snap_123", mock_get_entries, limit=10)
    
    assert len(entries) == 1
    assert entries[0]["context_state"]["vif_context_snapshot_id"] == "snap_123"
    mock_get_entries.assert_called_once()


def test_query_snapshot_timeline_no_tcs():
    """Test graceful degradation when TCS unavailable"""
    entries = query_snapshot_timeline("snap_123", None)
    
    assert entries == []


def test_query_confidence_timeline():
    """Test querying timeline for confidence range"""
    # Mock MCP tool function
    mock_get_entries = Mock(return_value=[
        {
            "prompt_id": "entry_1",
            "context_state": {
                "confidence_score": 0.85,
            },
        },
        {
            "prompt_id": "entry_2",
            "context_state": {
                "confidence_score": 0.90,
            },
        },
    ])
    
    entries = query_confidence_timeline(0.80, 0.95, mock_get_entries, limit=10)
    
    assert len(entries) == 2
    assert all(0.80 <= e["context_state"]["confidence_score"] <= 0.95 for e in entries)
    mock_get_entries.assert_called_once()


def test_query_confidence_timeline_no_tcs():
    """Test graceful degradation when TCS unavailable"""
    entries = query_confidence_timeline(0.80, 0.95, None)
    
    assert entries == []


def test_is_tcs_available():
    """Test checking TCS availability"""
    mock_add_entry = Mock()
    
    assert is_tcs_available(mock_add_entry) is True
    assert is_tcs_available(None) is False


def test_create_witness_timeline_entry_with_metadata():
    """Test timeline entry includes proper metadata for indexing"""
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
    )
    
    mock_add_entry = Mock(return_value={"success": True, "prompt_id": "test_id"})
    
    create_witness_timeline_entry(vif, mock_add_entry)
    
    call_args = mock_add_entry.call_args[0][0]
    metadata = call_args["context_state"]["metadata"]
    
    assert metadata["vif_witness_id"] == vif.id
    assert metadata["vif_context_snapshot_id"] == vif.context_snapshot_id
    assert metadata["source_system"] == "vif"
    assert metadata["event_category"] == "witness_creation"

