"""
Router API Server - Test Utilities

# NL_TAG: ROUTER-API-TEST-UTIL-001 | Test utilities for Router API server | test_utils.py | []
"""

from typing import Dict, Any, Optional
from unittest.mock import Mock, AsyncMock
import json


def create_mock_mcp_response(tool_name: str, result: Any = None) -> Dict[str, Any]:
    """Create mock MCP response."""
    return {
        "success": True,
        "result": result or {"test": "result"},
        "tool": tool_name
    }


def create_mock_tool_proposal(
    tool_name: str = "test_tool",
    confidence: float = 0.8,
    probability: float = 0.9
) -> Dict[str, Any]:
    """Create mock tool proposal."""
    return {
        "tool_name": tool_name,
        "rationale": f"Test tool: {tool_name}",
        "draft_arguments": {},
        "confidence": confidence,
        "probability": probability,
        "context_fit": 0.8,
        "success_rate": 0.85,
        "precondition_satisfied": True,
        "expected_info_gain": 0.7,
        "parallelizable": False
    }


def create_mock_scout_report(
    window_id: str = "test-window",
    severity: str = "medium",
    confidence: float = 0.8
) -> Dict[str, Any]:
    """Create mock Scout report."""
    return {
        "window_id": window_id,
        "summary": "Test Scout report",
        "confidence": confidence,
        "severity": severity,
        "tags": ["test", "scout"],
        "suggested_tools": ["test_tool"],
        "timestamp": "2025-01-27T00:00:00Z"
    }


def create_mock_forensics_report(
    window_id: str = "test-window",
    severity: str = "high",
    confidence: float = 0.9
) -> Dict[str, Any]:
    """Create mock Forensics report."""
    return {
        "window_id": window_id,
        "summary": "Test Forensics report",
        "confidence": confidence,
        "severity": severity,
        "tags": ["test", "forensics"],
        "suggested_tools": ["test_tool"],
        "timestamp": "2025-01-27T00:00:00Z",
        "root_cause": "Test root cause",
        "fix_suggestion": {
            "patch": "test patch",
            "steps": ["step1", "step2"]
        },
        "evidence": ["evidence1", "evidence2"],
        "gate": {
            "passed": True,
            "reasons": []
        }
    }

