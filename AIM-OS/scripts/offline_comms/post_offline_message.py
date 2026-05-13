#!/usr/bin/env python3
"""
Post an offline coordination message when MCP transport is unavailable.

Writes:
- docs/communications_mcp_down/threads/THREAD_<thread_id>.md
- docs/communications_mcp_down/logs/messages.jsonl
- docs/communications_mcp_down/threads/INDEX.md (append row)
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())


def read_content(content: Optional[str], content_file: Optional[str]) -> str:
    if content_file:
        return Path(content_file).read_text(encoding="utf-8")
    if content:
        return content
    raise ValueError("Either --content or --content-file is required")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def append_thread_entry(
    thread_path: Path,
    *,
    timestamp: str,
    message_id: str,
    from_ai: str,
    to_ai: str,
    message_type: str,
    priority: str,
    content: str,
) -> None:
    if not thread_path.exists():
        header = (
            f"# Offline Thread - {thread_path.stem.replace('THREAD_', '', 1)}\n\n"
            f"Created: {timestamp}\n\n"
            "---\n\n"
        )
        thread_path.write_text(header, encoding="utf-8")

    entry = (
        f"## {timestamp} | {from_ai} -> {to_ai} | {message_type} | {priority}\n\n"
        f"**Message ID:** `{message_id}`\n\n"
        f"{content.strip()}\n\n"
        "---\n\n"
    )
    with thread_path.open("a", encoding="utf-8") as f:
        f.write(entry)


def append_log(log_path: Path, payload: dict) -> None:
    ensure_parent(log_path)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def append_index(index_path: Path, thread_id: str, thread_file: str, timestamp: str) -> None:
    ensure_parent(index_path)
    if not index_path.exists():
        index_path.write_text(
            "# Offline Thread Index\n\n"
            "| Thread ID | File | Last Update (UTC) | Status |\n"
            "|---|---|---|---|\n",
            encoding="utf-8",
        )

    row = f"| {thread_id} | `{thread_file}` | {timestamp} | active |\n"
    text = index_path.read_text(encoding="utf-8")
    if "| *(none yet)* | - | - | - |" in text:
        text = text.replace("| *(none yet)* | - | - | - |\n", "")
        index_path.write_text(text, encoding="utf-8")
    with index_path.open("a", encoding="utf-8") as f:
        f.write(row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Post offline message to MCP-down communications area")
    parser.add_argument("--from", dest="from_ai", required=True, help="Sender agent name")
    parser.add_argument("--to", dest="to_ai", required=True, help="Recipient agent name")
    parser.add_argument("--thread", required=True, help="Thread id")
    parser.add_argument("--type", dest="message_type", default="status_update")
    parser.add_argument("--priority", default="medium")
    parser.add_argument("--content", help="Inline message content")
    parser.add_argument("--content-file", help="Path to file containing message content")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[2]), help="Repo root path")
    parser.add_argument("--dry-run", action="store_true", help="Print payload without writing files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    content = read_content(args.content, args.content_file)
    timestamp = utc_now_iso()
    message_id = f"offline_msg_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{slug(args.from_ai)}"

    repo_root = Path(args.repo_root).resolve()
    comms_root = repo_root / "docs" / "communications_mcp_down"
    thread_file = f"THREAD_{slug(args.thread)}.md"
    thread_path = comms_root / "threads" / thread_file
    log_path = comms_root / "logs" / "messages.jsonl"
    index_path = comms_root / "threads" / "INDEX.md"

    payload = {
        "message_id": message_id,
        "timestamp": timestamp,
        "from_ai": args.from_ai,
        "to_ai": args.to_ai,
        "thread_id": args.thread,
        "message_type": args.message_type,
        "priority": args.priority,
        "content": content,
        "transport": "offline_file",
    }

    if args.dry_run:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print(f"thread_path={thread_path}")
        print(f"log_path={log_path}")
        return 0

    append_thread_entry(
        thread_path,
        timestamp=timestamp,
        message_id=message_id,
        from_ai=args.from_ai,
        to_ai=args.to_ai,
        message_type=args.message_type,
        priority=args.priority,
        content=content,
    )
    append_log(log_path, payload)
    append_index(index_path, args.thread, thread_file, timestamp)

    print(f"offline_message_written={message_id}")
    print(f"thread={thread_path}")
    print(f"log={log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

