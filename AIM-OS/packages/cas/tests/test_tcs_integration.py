"""
Tests for CAS → TCS integration (timeline retrieval for analysis).
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Any, Dict

from cas.tcs_integration import get_timeline_entries_for_analysis


class _MockMCP:
    def __init__(self) -> None:
        self.last_tool: str | None = None
        self.last_args: Dict[str, Any] | None = None

    def call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        self.last_tool = name
        self.last_args = args
        # Mimic server response with two entries
        now = datetime.now(timezone.utc)
        return {
            "entries": [
                {"prompt_id": "p1", "timestamp": now.isoformat(), "timeline_entry": {"summary": "a"}},
                {"prompt_id": "p2", "timestamp": (now - timedelta(minutes=1)).isoformat(), "timeline_entry": {"summary": "b"}},
            ]
        }


def test_get_timeline_entries_for_analysis_calls_mcp_tool() -> None:
    mcp = _MockMCP()
    start = datetime.now(timezone.utc) - timedelta(hours=1)
    end = datetime.now(timezone.utc)
    entries = get_timeline_entries_for_analysis(
        mcp_client=mcp,
        start_time=start,
        end_time=end,
        limit=25,
    )
    assert mcp.last_tool == "mcp_lucid-mcp_get_timeline_entries"
    assert isinstance(mcp.last_args, dict)
    assert mcp.last_args["limit"] == 25
    assert "start_time" in mcp.last_args and "end_time" in mcp.last_args
    assert isinstance(entries, list)
    assert len(entries) == 2
    assert entries[0]["prompt_id"] == "p1"


def test_get_timeline_entries_for_analysis_graceful_without_mcp() -> None:
    entries = get_timeline_entries_for_analysis(
        mcp_client=None,
        start_time=None,
        end_time=None,
        limit=10,
    )
    assert entries == []


