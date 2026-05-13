#!/usr/bin/env python3
"""
Install policy-driven quintet pre-commit hook.
"""

from __future__ import annotations

from pathlib import Path


HOOK_TEMPLATE = """#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[2]
runner = repo_root / "scripts" / "git" / "quintet_pre_commit_gate.py"

if not runner.exists():
    print("WARNING: Quintet gate runner not found, skipping gate")
    sys.exit(0)

cmd = [sys.executable, str(runner), "--stage", "pre-commit"]
result = subprocess.run(cmd, cwd=str(repo_root))
sys.exit(result.returncode)
"""


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    hook_path = hooks_dir / "pre-commit"
    backup_path = hooks_dir / "pre-commit.backup.codexgit"

    if hook_path.exists():
        try:
            backup_path.write_text(hook_path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
            print(f"Backed up existing pre-commit hook to {backup_path}")
        except Exception as exc:
            print(f"Warning: failed to backup existing pre-commit hook: {exc}")

    hook_path.write_text(HOOK_TEMPLATE, encoding="utf-8")

    try:
        import stat
        hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
    except Exception:
        pass

    print(f"Installed policy-driven quintet hook: {hook_path}")
    print("Default mode is read from config/quintet_gate_policy.json")
    print("Override mode per shell with AIMOS_QUINTET_GATE_MODE=strict|balanced|advisory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
