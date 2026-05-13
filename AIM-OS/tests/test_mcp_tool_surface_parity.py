"""
MCP tool contract parity checks.

These tests guard against drift between advertised and callable MCP tools.
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from detect_source_of_truth import get_mcp_tool_surface


def test_tools_list_matches_tools_call_surface() -> None:
    surface = get_mcp_tool_surface()
    assert surface["parity_ok"], (
        "MCP tools/list and tools/call are out of parity. "
        f"listed_not_callable={surface['listed_not_callable']} "
        f"callable_not_listed={surface['callable_not_listed']}"
    )


def test_mcp_tool_surface_non_empty() -> None:
    surface = get_mcp_tool_surface()
    assert surface["listed_count"] > 0
    assert surface["callable_count"] > 0
