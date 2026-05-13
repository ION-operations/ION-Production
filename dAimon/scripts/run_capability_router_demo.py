#!/usr/bin/env python3
"""Compatibility wrapper for the v1.0 capability-route demo."""
from __future__ import annotations

import runpy
from pathlib import Path

if __name__ == "__main__":
    raise SystemExit(runpy.run_path(str(Path(__file__).with_name("run_route_demo.py")), run_name="__main__"))
