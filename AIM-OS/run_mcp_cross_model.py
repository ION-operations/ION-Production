#!/usr/bin/env python3
"""
Compatibility entrypoint for legacy cross-model MCP imports.

Several tests and scripts import `CrossModelMCPServer` from this module.
The current implementation is maintained in `archive/run_mcp_cross_model.py`.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def _load_legacy_module() -> ModuleType:
    module_path = Path(__file__).resolve().parent / "archive" / "run_mcp_cross_model.py"
    if not module_path.exists():
        raise FileNotFoundError(f"Legacy cross-model server not found: {module_path}")

    spec = importlib.util.spec_from_file_location("archive_run_mcp_cross_model", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module spec for {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_legacy = _load_legacy_module()
CrossModelMCPServer = _legacy.CrossModelMCPServer

__all__ = ["CrossModelMCPServer"]


def main() -> None:
    server = CrossModelMCPServer()
    server.run()


if __name__ == "__main__":
    main()
