#!/usr/bin/env python3
"""
Backward-compatible wrapper for installing SDF-CVF hooks.

This now installs the policy-driven quintet gate hook:
- scripts/git/quintet_pre_commit_gate.py
- config/quintet_gate_policy.json
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    installer = repo_root / "scripts" / "git" / "install_quintet_hook.py"
    if not installer.exists():
        print(f"ERROR: installer not found: {installer}")
        return 1

    cmd = [sys.executable, str(installer)]
    return subprocess.run(cmd, cwd=str(repo_root)).returncode


if __name__ == "__main__":
    raise SystemExit(main())
