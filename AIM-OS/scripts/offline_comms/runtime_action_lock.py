#!/usr/bin/env python3
"""
File-based runtime action lock for multi-agent coordination.

Prevents concurrent start/stop commands across agents on the same machine.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_lock(lock_path: Path) -> Dict[str, Any] | None:
    if not lock_path.exists():
        return None
    try:
        return json.loads(lock_path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "owner": "unknown",
            "acquired_at": "unknown",
            "reason": "corrupt_lock_file",
            "raw": lock_path.read_text(encoding="utf-8", errors="replace"),
        }


def print_json(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def default_holder_id(owner: str) -> str:
    env_holder = os.getenv("AIMOS_LOCK_HOLDER_ID")
    if env_holder:
        return env_holder.strip()
    host = socket.gethostname()
    pid = os.getpid()
    owner_slug = owner.strip().replace(" ", "_")
    return f"{owner_slug}@{host}:{pid}"


def cmd_status(lock_path: Path) -> int:
    lock = read_lock(lock_path)
    if not lock:
        print_json({"success": True, "locked": False, "lock_path": str(lock_path)})
        return 0
    print_json({"success": True, "locked": True, "lock_path": str(lock_path), "lock": lock})
    return 0


def cmd_acquire(lock_path: Path, owner: str, holder_id: str, reason: str) -> int:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "owner": owner,
        "holder_id": holder_id,
        "reason": reason,
        "acquired_at": utc_now_iso(),
    }

    # Atomic create; fails if lock already exists.
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        fd = os.open(str(lock_path), flags)
    except FileExistsError:
        existing = read_lock(lock_path)
        existing_owner = existing.get("owner") if existing else None
        existing_holder = existing.get("holder_id") if existing else None

        if existing_owner == owner and existing_holder == holder_id:
            print_json({
                "success": True,
                "locked": True,
                "idempotent": True,
                "message": "Lock already held by requested owner",
                "lock_path": str(lock_path),
                "lock": existing,
            })
            return 0
        if existing_owner == owner and not existing_holder:
            print_json({
                "success": False,
                "locked": True,
                "message": "Legacy lock file without holder_id detected; release and reacquire with holder_id",
                "lock_path": str(lock_path),
                "lock": existing,
                "requested": {"owner": owner, "holder_id": holder_id},
            })
            return 3

        print_json({
            "success": False,
            "locked": True,
            "message": "Lock already held by another owner",
            "lock_path": str(lock_path),
            "lock": existing,
            "requested": {"owner": owner, "holder_id": holder_id},
        })
        return 2

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(payload, indent=2, ensure_ascii=False))
    except Exception:
        try:
            lock_path.unlink(missing_ok=True)
        except Exception:
            pass
        raise

    print_json({
        "success": True,
        "locked": True,
        "message": "Lock acquired",
        "lock_path": str(lock_path),
        "lock": payload,
    })
    return 0


def cmd_release(lock_path: Path, owner: str, holder_id: str, force: bool) -> int:
    if not lock_path.exists():
        print_json({
            "success": True,
            "locked": False,
            "message": "No lock file present",
            "lock_path": str(lock_path),
        })
        return 0

    existing = read_lock(lock_path)
    existing_owner = existing.get("owner") if existing else None
    existing_holder = existing.get("holder_id") if existing else None
    owner_match = existing_owner == owner
    holder_match = existing_holder == holder_id
    legacy_owner_only_match = owner_match and not existing_holder

    if not force and not ((owner_match and holder_match) or legacy_owner_only_match):
        print_json({
            "success": False,
            "locked": True,
            "message": "Lock held by another owner",
            "lock_path": str(lock_path),
            "lock": existing,
            "requested": {"owner": owner, "holder_id": holder_id},
        })
        return 2

    lock_path.unlink(missing_ok=True)
    print_json({
        "success": True,
        "locked": False,
        "message": "Lock released",
        "lock_path": str(lock_path),
        "released_by": owner,
        "released_holder_id": holder_id,
        "force": force,
    })
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Runtime action lock for offline multi-agent coordination")
    parser.add_argument(
        "--lock-path",
        default="docs/communications_mcp_down/agents/runtime_action_lock.json",
        help="Lock file path",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show lock status")

    acq = sub.add_parser("acquire", help="Acquire lock")
    acq.add_argument("--owner", required=True, help="Canonical owner ID")
    acq.add_argument("--holder-id", help="Unique runtime holder ID (defaults to owner@host:pid)")
    acq.add_argument("--reason", default="runtime_recovery", help="Reason for lock")

    rel = sub.add_parser("release", help="Release lock")
    rel.add_argument("--owner", required=True, help="Canonical owner ID")
    rel.add_argument("--holder-id", help="Unique runtime holder ID (defaults to owner@host:pid)")
    rel.add_argument("--force", action="store_true", help="Force release if owned by another owner")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    lock_path = Path(args.lock_path).resolve()

    if args.command == "status":
        return cmd_status(lock_path)
    if args.command == "acquire":
        holder_id = args.holder_id or default_holder_id(args.owner)
        return cmd_acquire(lock_path, args.owner, holder_id, args.reason)
    if args.command == "release":
        holder_id = args.holder_id or default_holder_id(args.owner)
        return cmd_release(lock_path, args.owner, holder_id, args.force)

    print_json({"success": False, "error": f"Unknown command: {args.command}"})
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
