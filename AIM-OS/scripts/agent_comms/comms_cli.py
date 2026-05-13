#!/usr/bin/env python3
"""
Filesystem-first agent communications CLI.

Works without MCP. Uses .agent/comms as the source of truth.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from identity_registry import resolve_identity


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def now_iso() -> str:
    return now_utc().replace(microsecond=0).isoformat().replace("+00:00", "Z")


def date_stamp() -> str:
    return now_utc().strftime("%Y-%m-%d")


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9._-]+", "_", value.strip().lower())


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_text_arg(inline: str | None, file_path: str | None) -> str:
    if file_path:
        return Path(file_path).read_text(encoding="utf-8").strip()
    if inline:
        return inline.strip()
    raise ValueError("Provide --content or --content-file")


def write_markdown(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def get_comms_root(repo_root: Path) -> Path:
    return repo_root / ".agent" / "comms"


def load_identity_locks(repo_root: Path) -> Dict[str, Any]:
    lock_file = repo_root / ".agent" / "comms" / "identity_session_locks.json"
    if not lock_file.exists():
        return {"lock_file": str(lock_file), "locks": {}}
    data = json.loads(lock_file.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Identity lock file is invalid object: {lock_file}")
    locks = data.get("locks", {})
    if not isinstance(locks, dict):
        raise ValueError(f"Identity lock map is invalid: {lock_file}")
    return {"lock_file": str(lock_file), "locks": locks}


def current_holder_id(args: argparse.Namespace) -> str:
    if getattr(args, "holder_id", None):
        return str(args.holder_id).strip()
    return os.getenv("AIMOS_AGENT_HOLDER_ID", "").strip()


def enforce_identity_lock(repo_root: Path, canonical_id: str, holder_id: str) -> None:
    lock_data = load_identity_locks(repo_root)
    locks = lock_data.get("locks", {})
    lock = locks.get(canonical_id)
    if not lock:
        return
    expected_holder = str(lock.get("holder_id", "")).strip()
    if not expected_holder:
        return
    if holder_id == expected_holder:
        return
    lock_file = lock_data.get("lock_file")
    raise ValueError(
        f"Identity lock mismatch for '{canonical_id}'. "
        f"Provide matching --holder-id (or AIMOS_AGENT_HOLDER_ID). lock_file={lock_file}"
    )


def build_direct_message_md(
    sender: str,
    recipient: str,
    subject: str,
    priority: str,
    content: str,
) -> str:
    return (
        f"**From:** {sender}\n"
        f"**To:** {recipient}\n"
        f"**Date:** {date_stamp()}\n"
        f"**Priority:** {priority}\n"
        f"**Subject:** {subject}\n\n"
        f"---\n\n"
        f"{content}\n"
    )


def build_handoff_md(
    sender: str,
    recipient: str,
    subject: str,
    priority: str,
    context: str,
    task: str,
    files: List[str],
    current_state: str,
    blockers: List[str],
    suggested_approach: str,
) -> str:
    files_table = "| File | What's Relevant |\n|------|----------------|\n"
    for file_entry in files:
        files_table += f"| `{file_entry}` | referenced by handoff |\n"

    blocker_lines = "\n".join([f"- {b}" for b in blockers]) if blockers else "- None"
    return (
        f"**From:** {sender}\n"
        f"**To:** {recipient}\n"
        f"**Date:** {date_stamp()}\n"
        f"**Priority:** {priority}\n"
        f"**Subject:** {subject}\n\n"
        f"---\n\n"
        f"## Context\n\n{context}\n\n"
        f"## What Needs To Be Done\n\n{task}\n\n"
        f"## Files Involved\n\n{files_table}\n"
        f"## Current State\n\n{current_state}\n\n"
        f"## Blockers / Gotchas\n\n{blocker_lines}\n\n"
        f"## Suggested Approach\n\n{suggested_approach}\n\n"
        f"---\n\n"
        f"**Status:** PENDING\n"
        f"**Accepted by:** \n"
        f"**Completed:** \n"
    )


def build_status_md(
    agent: str,
    state: str,
    current_work: str,
    last_completed: str,
    blockers: List[str],
    needs: List[str],
    available_for: str,
) -> str:
    blockers_text = "\n".join([f"- {b}" for b in blockers]) if blockers else "- None"
    needs_table = "| Agent | What I Need |\n|-------|-------------|\n"
    if needs:
        for n in needs:
            if ":" in n:
                who, ask = n.split(":", 1)
                needs_table += f"| {who.strip()} | {ask.strip()} |\n"
            else:
                needs_table += f"| team | {n.strip()} |\n"
    else:
        needs_table += "| None | None |\n"

    return (
        f"**Agent:** {agent}\n"
        f"**Updated:** {now_utc().strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"**State:** {state}\n\n"
        f"## Current Work\n\n{current_work}\n\n"
        f"## Last Completed\n\n{last_completed}\n\n"
        f"## Blockers\n\n{blockers_text}\n\n"
        f"## Need From Other Agents\n\n{needs_table}\n"
        f"## Available For\n\n{available_for}\n"
    )


def cmd_send(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    comms = get_comms_root(repo_root)
    content = read_text_arg(args.content, args.content_file)
    sender = resolve_identity(args.sender, strict=args.strict_identity)
    recipient = resolve_identity(args.recipient, strict=args.strict_identity)
    holder_id = current_holder_id(args)
    enforce_identity_lock(repo_root, sender["canonical_id"], holder_id)
    subject_slug = slug(args.subject)
    sender_slug = sender["route_key"]
    recipient_slug = recipient["route_key"]
    file_name = f"{date_stamp()}_{sender_slug}_to_{recipient_slug}_{subject_slug}.md"

    inbox_path = comms / "inbox" / recipient_slug / file_name
    md = build_direct_message_md(
        sender["canonical_id"], recipient["canonical_id"], args.subject, args.priority, content
    )
    write_markdown(inbox_path, md)

    log_payload = {
        "timestamp": now_iso(),
        "kind": "direct",
        "from": sender["canonical_id"],
        "from_route": sender["route_key"],
        "to": recipient["canonical_id"],
        "to_route": recipient["route_key"],
        "priority": args.priority,
        "subject": args.subject,
        "identity_matched": {
            "sender": sender["matched"],
            "recipient": recipient["matched"],
        },
        "path": str(inbox_path.relative_to(repo_root)),
    }
    append_jsonl(comms / "logs" / "messages.jsonl", log_payload)

    print(f"ok: {inbox_path}")
    return 0


def cmd_broadcast(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    comms = get_comms_root(repo_root)
    content = read_text_arg(args.content, args.content_file)
    sender = resolve_identity(args.sender, strict=args.strict_identity)
    holder_id = current_holder_id(args)
    enforce_identity_lock(repo_root, sender["canonical_id"], holder_id)
    sender_slug = sender["route_key"]
    subject_slug = slug(args.subject)
    file_name = f"{date_stamp()}_{sender_slug}_{subject_slug}.md"

    out_path = comms / "broadcasts" / file_name
    md = (
        f"**From:** {sender['canonical_id']}\n"
        f"**Date:** {date_stamp()}\n"
        f"**Priority:** {args.priority}\n"
        f"**Subject:** {args.subject}\n\n"
        f"---\n\n"
        f"{content}\n"
    )
    write_markdown(out_path, md)

    log_payload = {
        "timestamp": now_iso(),
        "kind": "broadcast",
        "from": sender["canonical_id"],
        "from_route": sender["route_key"],
        "priority": args.priority,
        "subject": args.subject,
        "identity_matched": sender["matched"],
        "path": str(out_path.relative_to(repo_root)),
    }
    append_jsonl(comms / "logs" / "messages.jsonl", log_payload)
    print(f"ok: {out_path}")
    return 0


def cmd_handoff(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    comms = get_comms_root(repo_root)
    sender = resolve_identity(args.sender, strict=args.strict_identity)
    recipient = resolve_identity(args.recipient, strict=args.strict_identity)
    holder_id = current_holder_id(args)
    enforce_identity_lock(repo_root, sender["canonical_id"], holder_id)
    sender_slug = sender["route_key"]
    recipient_slug = recipient["route_key"]
    subject_slug = slug(args.subject)
    file_name = f"{date_stamp()}_{sender_slug}_to_{recipient_slug}_{subject_slug}.md"

    context = read_text_arg(args.context, args.context_file)
    task = read_text_arg(args.task, args.task_file)
    current_state = read_text_arg(args.current_state, args.current_state_file)
    suggested_approach = read_text_arg(args.suggested_approach, args.suggested_approach_file)
    files = args.file or []
    blockers = args.blocker or []

    handoff_md = build_handoff_md(
        sender=sender["canonical_id"],
        recipient=recipient["canonical_id"],
        subject=args.subject,
        priority=args.priority,
        context=context,
        task=task,
        files=files,
        current_state=current_state,
        blockers=blockers,
        suggested_approach=suggested_approach,
    )

    handoff_path = comms / "handoffs" / file_name
    inbox_path = comms / "inbox" / recipient_slug / file_name
    write_markdown(handoff_path, handoff_md)
    write_markdown(inbox_path, handoff_md)

    log_payload = {
        "timestamp": now_iso(),
        "kind": "handoff",
        "from": sender["canonical_id"],
        "from_route": sender["route_key"],
        "to": recipient["canonical_id"],
        "to_route": recipient["route_key"],
        "priority": args.priority,
        "subject": args.subject,
        "identity_matched": {
            "sender": sender["matched"],
            "recipient": recipient["matched"],
        },
        "handoff_path": str(handoff_path.relative_to(repo_root)),
        "inbox_copy": str(inbox_path.relative_to(repo_root)),
    }
    append_jsonl(comms / "logs" / "messages.jsonl", log_payload)
    print(f"ok: {handoff_path}")
    print(f"ok: {inbox_path}")
    return 0


def cmd_update_status(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    comms = get_comms_root(repo_root)
    agent = resolve_identity(args.agent, strict=args.strict_identity)
    holder_id = current_holder_id(args)
    enforce_identity_lock(repo_root, agent["canonical_id"], holder_id)
    agent_slug = agent["route_key"]
    status_path = comms / "status" / f"{agent_slug}.status.md"

    md = build_status_md(
        agent=agent["canonical_id"],
        state=args.state,
        current_work=args.current_work,
        last_completed=args.last_completed,
        blockers=args.blocker or [],
        needs=args.need or [],
        available_for=args.available_for,
    )
    write_markdown(status_path, md)

    log_payload = {
        "timestamp": now_iso(),
        "kind": "status",
        "agent": agent["canonical_id"],
        "agent_route": agent["route_key"],
        "identity_matched": agent["matched"],
        "state": args.state,
        "path": str(status_path.relative_to(repo_root)),
    }
    append_jsonl(comms / "logs" / "messages.jsonl", log_payload)
    print(f"ok: {status_path}")
    return 0


def cmd_list_inbox(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    comms = get_comms_root(repo_root)
    agent = resolve_identity(args.agent, strict=args.strict_identity)
    agent_slug = agent["route_key"]
    inbox = comms / "inbox" / agent_slug
    ensure_dir(inbox)

    items = sorted(
        [p for p in inbox.glob("*.md") if p.is_file()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not items:
        print("inbox-empty")
        return 0
    for p in items[: args.limit]:
        print(f"{p.name}")
    return 0


def cmd_resolve_identity(args: argparse.Namespace) -> int:
    resolved = resolve_identity(args.agent, strict=args.strict_identity)
    print(json.dumps(resolved, ensure_ascii=False))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Filesystem-first agent comms CLI")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument(
        "--holder-id",
        help="Session holder ID for identity lock enforcement (or use AIMOS_AGENT_HOLDER_ID)",
    )
    parser.add_argument(
        "--strict-identity",
        action="store_true",
        help="Fail on unknown/non-canonical agent identifiers",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    s1 = sub.add_parser("send", help="Send direct inbox message")
    s1.add_argument("--sender", required=True)
    s1.add_argument("--recipient", required=True)
    s1.add_argument("--subject", required=True)
    s1.add_argument("--priority", default="P2-Normal")
    s1.add_argument("--content")
    s1.add_argument("--content-file")
    s1.set_defaults(func=cmd_send)

    s2 = sub.add_parser("broadcast", help="Send broadcast message")
    s2.add_argument("--sender", required=True)
    s2.add_argument("--subject", required=True)
    s2.add_argument("--priority", default="P2-Normal")
    s2.add_argument("--content")
    s2.add_argument("--content-file")
    s2.set_defaults(func=cmd_broadcast)

    s3 = sub.add_parser("handoff", help="Create structured handoff + inbox copy")
    s3.add_argument("--sender", required=True)
    s3.add_argument("--recipient", required=True)
    s3.add_argument("--subject", required=True)
    s3.add_argument("--priority", default="P1-High")
    s3.add_argument("--context")
    s3.add_argument("--context-file")
    s3.add_argument("--task")
    s3.add_argument("--task-file")
    s3.add_argument("--current-state")
    s3.add_argument("--current-state-file")
    s3.add_argument("--suggested-approach")
    s3.add_argument("--suggested-approach-file")
    s3.add_argument("--file", action="append")
    s3.add_argument("--blocker", action="append")
    s3.set_defaults(func=cmd_handoff)

    s4 = sub.add_parser("update-status", help="Write agent status file")
    s4.add_argument("--agent", required=True)
    s4.add_argument("--state", required=True, choices=["active", "idle", "blocked", "offline"])
    s4.add_argument("--current-work", required=True)
    s4.add_argument("--last-completed", required=True)
    s4.add_argument("--available-for", required=True)
    s4.add_argument("--blocker", action="append")
    s4.add_argument("--need", action="append")
    s4.set_defaults(func=cmd_update_status)

    s5 = sub.add_parser("list-inbox", help="List inbox messages for an agent")
    s5.add_argument("--agent", required=True)
    s5.add_argument("--limit", type=int, default=20)
    s5.set_defaults(func=cmd_list_inbox)

    s6 = sub.add_parser("resolve-identity", help="Resolve canonical ID + route key")
    s6.add_argument("--agent", required=True)
    s6.set_defaults(func=cmd_resolve_identity)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return args.func(args)
    except ValueError as exc:
        print(f"error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
