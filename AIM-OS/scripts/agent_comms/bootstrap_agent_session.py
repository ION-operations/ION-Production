#!/usr/bin/env python3
"""
Session bootstrap helper for filesystem-first agent operations.

Reads genome + inbox/broadcast/handoff/status summaries and optionally updates status.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from identity_registry import resolve_identity


def read_preview(path: Path, max_chars: int = 220) -> str:
    text = path.read_text(encoding="utf-8", errors="replace").strip().replace("\r\n", "\n")
    text = text.replace("\ufeff", "")
    text = " ".join(text.split())
    return text[:max_chars] + ("..." if len(text) > max_chars else "")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Bootstrap agent session from filesystem-first comms")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--agent", required=True, help="Agent name (e.g. Codex, Agent Aether)")
    parser.add_argument("--limit", type=int, default=10, help="Max items per section")
    parser.add_argument(
        "--strict-identity",
        action="store_true",
        help="Fail if agent identity is not canonical/known",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    identity = resolve_identity(args.agent, strict=args.strict_identity)
    agent_slug = identity["route_key"]
    comms = repo_root / ".agent" / "comms"
    genomes = repo_root / ".agent" / "genomes"

    genome_candidates = [
        genomes / f"{agent_slug}.genome.md",
        genomes / f"{identity['canonical_id'].lower().replace(' ', '_')}.genome.md",
        genomes / f"{identity['canonical_id'].lower().replace(' ', '')}.genome.md",
    ]
    genome_path = next((p for p in genome_candidates if p.exists()), None)

    print(f"agent_input={args.agent}")
    print(f"agent_canonical={identity['canonical_id']}")
    print(f"agent_route={identity['route_key']}")
    print(f"identity_matched={identity['matched']}")
    print(f"repo_root={repo_root}")
    print("")

    print("== Genome ==")
    if genome_path:
        print(f"path={genome_path.relative_to(repo_root)}")
        print(f"preview={read_preview(genome_path)}")
    else:
        print("path=missing")
    print("")

    inbox_dir = comms / "inbox" / agent_slug
    broadcasts_dir = comms / "broadcasts"
    handoffs_dir = comms / "handoffs"
    status_dir = comms / "status"

    for name, folder in [
        ("Inbox", inbox_dir),
        ("Broadcasts", broadcasts_dir),
        ("Handoffs", handoffs_dir),
    ]:
        print(f"== {name} ==")
        if not folder.exists():
            print("missing")
            print("")
            continue
        files = sorted([p for p in folder.glob("*.md") if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)
        if not files:
            print("empty")
            print("")
            continue
        for p in files[: args.limit]:
            print(f"{p.name} :: {read_preview(p)}")
        print("")

    print("== Status Board ==")
    if not status_dir.exists():
        print("missing")
        return 0
    status_files = sorted([p for p in status_dir.glob("*.status.md") if p.is_file()])
    if not status_files:
        print("empty")
        return 0
    for p in status_files[: args.limit]:
        print(f"{p.name} :: {read_preview(p)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
