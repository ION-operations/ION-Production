#!/usr/bin/env python3
"""
Git Hooks for the Adaptive Nervous System

Provides automated scanning on git events:
    - post-commit: Incremental scan of changed files
    - pre-push: Safety gate (block push on critical findings)

Installation:
    python -m packages.adaptive_system.hooks install    # symlink hooks
    python -m packages.adaptive_system.hooks uninstall  # remove hooks
    
Manual trigger:
    python -m packages.adaptive_system.hooks post-commit
    python -m packages.adaptive_system.hooks pre-push
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional


def get_project_root() -> Path:
    """Find project root (nearest directory with .git)."""
    path = Path.cwd()
    while path != path.parent:
        if (path / ".git").exists():
            return path
        path = path.parent
    return Path.cwd()


def get_changed_files_in_commit() -> List[str]:
    """Get files changed in the most recent commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return []


def get_staged_files() -> List[str]:
    """Get files staged for the next commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return []


# ---------------------------------------------------------------
# Hook Implementations
# ---------------------------------------------------------------

def hook_post_commit():
    """Post-commit hook: run incremental daemon scan."""
    root = get_project_root()
    changed = get_changed_files_in_commit()
    
    if not changed:
        return 0
    
    # Filter to Python files (most relevant for adaptive scanning)
    py_files = [f for f in changed if f.endswith(".py")]
    
    if not py_files:
        return 0
    
    print(f"[adaptive] Post-commit: scanning {len(py_files)} changed file(s)...")
    
    # Run daemon in incremental dry-run (fast, non-blocking)
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "packages.adaptive_system",
                "daemon", "--incremental", "--dry-run",
            ],
            capture_output=True, text=True, timeout=60,
            cwd=str(root),
        )
        
        if result.returncode == 0:
            # Extract key metrics from output
            for line in result.stdout.split("\n"):
                if "Signals:" in line or "Proposals:" in line:
                    print(f"[adaptive] {line.strip()}")
    except subprocess.TimeoutExpired:
        print("[adaptive] Scan timed out (60s)")
    except Exception as e:
        print(f"[adaptive] Scan error: {e}")
    
    return 0


def hook_pre_push():
    """Pre-push hook: safety gate for critical findings."""
    root = get_project_root()
    
    print("[adaptive] Pre-push safety check...")
    
    # Run daemon dry-run and check for critical proposals
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "packages.adaptive_system",
                "daemon", "--dry-run",
            ],
            capture_output=True, text=True, timeout=120,
            cwd=str(root),
        )
        
        if result.returncode != 0:
            print("[adaptive] Pre-push scan failed, allowing push")
            return 0
        
        # Check for critical pending proposals
        proposals_dir = root / ".agent" / "adaptive" / "proposals" / "pending"
        if proposals_dir.exists():
            critical_count = 0
            for f in proposals_dir.glob("*.json"):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    if data.get("required_approval") in ("executive", "command"):
                        critical_count += 1
                        desc = data.get("description", f.stem)[:60]
                        print(f"[adaptive] CRITICAL: {desc}")
                except (json.JSONDecodeError, OSError):
                    pass
            
            if critical_count > 0:
                print(f"\n[adaptive] {critical_count} critical proposal(s) require review.")
                print("[adaptive] Run 'python -m packages.adaptive_system review' to inspect.")
                print("[adaptive] Use --no-verify to bypass this check.")
                return 1  # Block the push
        
        print("[adaptive] Pre-push check passed")
        
    except subprocess.TimeoutExpired:
        print("[adaptive] Pre-push scan timed out, allowing push")
    except Exception as e:
        print(f"[adaptive] Pre-push error: {e}")
    
    return 0


# ---------------------------------------------------------------
# Hook Installation
# ---------------------------------------------------------------

HOOK_TEMPLATE = '''#!/usr/bin/env python3
"""Auto-generated by AIM-OS Adaptive Nervous System."""
import subprocess
import sys
sys.exit(subprocess.run(
    [sys.executable, "-m", "packages.adaptive_system.hooks", "{hook_name}"],
    cwd=r"{project_root}",
).returncode)
'''


def install_hooks(root: Optional[Path] = None):
    """Install git hooks."""
    root = root or get_project_root()
    hooks_dir = root / ".git" / "hooks"
    
    if not hooks_dir.exists():
        print(f"No .git/hooks directory found at {hooks_dir}")
        return False
    
    hooks = {
        "post-commit": "post-commit",
        "pre-push": "pre-push",
    }
    
    for hook_file, hook_name in hooks.items():
        path = hooks_dir / hook_file
        content = HOOK_TEMPLATE.format(
            hook_name=hook_name,
            project_root=str(root),
        )
        path.write_text(content, encoding="utf-8")
        # Make executable on Unix
        try:
            path.chmod(0o755)
        except (OSError, AttributeError):
            pass
        print(f"Installed: {path}")
    
    return True


def uninstall_hooks(root: Optional[Path] = None):
    """Remove git hooks."""
    root = root or get_project_root()
    hooks_dir = root / ".git" / "hooks"
    
    for hook_name in ("post-commit", "pre-push"):
        path = hooks_dir / hook_name
        if path.exists():
            content = path.read_text(encoding="utf-8")
            if "AIM-OS Adaptive" in content:
                path.unlink()
                print(f"Removed: {path}")
            else:
                print(f"Skipped (not ours): {path}")


# ---------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Adaptive System Git Hooks")
    parser.add_argument(
        "action",
        choices=["install", "uninstall", "post-commit", "pre-push"],
        help="Action to perform",
    )
    args = parser.parse_args()
    
    if args.action == "install":
        install_hooks()
    elif args.action == "uninstall":
        uninstall_hooks()
    elif args.action == "post-commit":
        sys.exit(hook_post_commit())
    elif args.action == "pre-push":
        sys.exit(hook_pre_push())


if __name__ == "__main__":
    main()
