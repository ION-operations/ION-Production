"""
Tests for SDF-CVF → TCS integration (timeline entry creation).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from sdfcvf.tcs_integration import create_parity_timeline_entry


class _MockMCP:
    def __init__(self) -> None:
        self.last_tool: str | None = None
        self.last_args: Dict[str, Any] | None = None

    def call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        self.last_tool = name
        self.last_args = args
        # Mimic server response
        return {
            "entry_id": "entry_sdfcvf_test",
            "atom_id": "atom_sdfcvf_test",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


def test_create_parity_timeline_entry_calls_mcp_tool() -> None:
    mcp = _MockMCP()
    result = create_parity_timeline_entry(
        mcp_client=mcp,
        change_id="sdfcvf-change-20250127-120000",
        parity_score=0.92,
        details={"inputs": {"code": 0.93, "docs": 0.91, "tests": 0.90, "traces": 0.94}},
    )

    assert result is not None
    assert mcp.last_tool == "mcp_lucid-mcp_add_timeline_entry"
    assert isinstance(mcp.last_args, dict)
    assert mcp.last_args["event_type"] == "sdfcvf_parity_evaluation"
    assert mcp.last_args["context_data"]["change_id"] == "sdfcvf-change-20250127-120000"
    assert mcp.last_args["context_data"]["parity_score"] == 0.92
    assert "parity_details" in mcp.last_args["context_data"]
    assert "sdfcvf" in mcp.last_args["tags"]
    assert "tcs" in mcp.last_args["tags"]


def test_create_parity_timeline_entry_graceful_without_mcp() -> None:
    result = create_parity_timeline_entry(
        mcp_client=None,
        change_id="any",
        parity_score=0.5,
        details={},
    )
    assert result is None

"""Tests for TCS integration"""

import pytest

from sdfcvf.tcs_integration import TCSIntegration


class TestTCSIntegration:
    """Test TCS integration functionality"""
    
    def test_tcs_integration_initialization_no_tcs(self):
        """Test TCS integration initialization when TCS not available"""
        integration = TCSIntegration()
        assert integration.tcs_available is False
        assert integration.tcs is None
    
    def test_record_timeline_entry_no_tcs(self):
        """Test recording timeline entry when TCS not available"""
        integration = TCSIntegration()
        result = integration.record_timeline_entry(
            "parity_calculation",
            {"parity_score": 0.95}
        )
        assert result is None
    
    def test_track_dora_metrics_no_tcs(self):
        """Test tracking DORA metrics when TCS not available"""
        integration = TCSIntegration()
        result = integration.track_dora_metrics({
            "deployment_frequency": 10,
            "lead_time": 2.5
        })
        assert result["tracked"] is False
        assert "error" in result
    
    def test_query_change_history_no_tcs(self):
        """Test querying change history when TCS not available"""
        integration = TCSIntegration()
        result = integration.query_change_history("test-quartet-1")
        assert result == []
    
    def test_analyze_timeline_patterns_no_tcs(self):
        """Test analyzing timeline patterns when TCS not available"""
        integration = TCSIntegration()
        result = integration.analyze_timeline_patterns("test-quartet-1")
        assert result["analysis_available"] is False
        assert "error" in result

