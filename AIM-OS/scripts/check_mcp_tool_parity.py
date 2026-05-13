#!/usr/bin/env python3
"""
Fail-fast parity check for MCP tool contract surface.

Ensures tools exposed in `tools/list` exactly match callable tools in `tools/call`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.detect_source_of_truth import get_mcp_tool_surface


def main() -> None:
    surface: Dict[str, Any] = get_mcp_tool_surface()
    summary = {
        "listed_count": surface["listed_count"],
        "callable_count": surface["callable_count"],
        "parity_ok": surface["parity_ok"],
        "listed_not_callable": surface["listed_not_callable"],
        "callable_not_listed": surface["callable_not_listed"],
    }
    print(json.dumps(summary, indent=2))

    if not surface["parity_ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
