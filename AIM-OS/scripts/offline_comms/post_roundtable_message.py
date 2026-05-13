#!/usr/bin/env python3
"""
Post a roundtable message. Wraps post_offline_message.py with roundtable defaults.

Usage:
  python scripts/offline_comms/post_roundtable_message.py ^
    --from "Codex Agent" ^
    --to "Agent Aether" ^
    --thread "aimos_roundtable_operational_convergence_2026-03-04" ^
    --content "Message body"

Thread is created automatically on first post. Update docs/roundtable/INDEX.md
when starting a new thread.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Post roundtable message (MCP-down)")
    parser.add_argument("--from", dest="from_ai", required=True, help="Sender (use IDENTITY_CANON)")
    parser.add_argument("--to", dest="to_ai", required=True, help="Recipient or 'all'")
    parser.add_argument("--thread", required=True, help="Thread ID")
    parser.add_argument("--type", dest="message_type", default="discussion")
    parser.add_argument("--priority", default="medium")
    parser.add_argument("--content", help="Inline message content")
    parser.add_argument("--content-file", help="Path to file with message content")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.content and not args.content_file:
        print("Error: --content or --content-file required", file=sys.stderr)
        return 1

    script_dir = Path(__file__).resolve().parent
    post_script = script_dir / "post_offline_message.py"

    cmd = [
        sys.executable,
        str(post_script),
        "--from", args.from_ai,
        "--to", args.to_ai,
        "--thread", args.thread,
        "--type", args.message_type,
        "--priority", args.priority,
        "--repo-root", args.repo_root,
    ]
    if args.content:
        cmd.extend(["--content", args.content])
    if args.content_file:
        cmd.extend(["--content-file", args.content_file])
    if args.dry_run:
        cmd.append("--dry-run")

    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
