#!/usr/bin/env python3
"""
Session-level identity lock manager for AIM-OS agents.

Purpose:
- bind canonical agent identity to a single active holder_id
- prevent cross-session identity impersonation in comms paths
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from identity_registry import resolve_identity


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_lock_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"updated_at": now_iso(), "locks": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"Failed to parse lock file: {path} ({exc})") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Lock file root must be object: {path}")
    locks = data.get("locks")
    if not isinstance(locks, dict):
        data["locks"] = {}
    return data


def save_lock_file(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = now_iso()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def cmd_status(args: argparse.Namespace) -> int:
    lock_path = Path(args.lock_file).resolve()
    data = load_lock_file(lock_path)
    print(json.dumps({"lock_file": str(lock_path), "data": data}, ensure_ascii=False, indent=2))
    return 0


def cmd_claim(args: argparse.Namespace) -> int:
    lock_path = Path(args.lock_file).resolve()
    identity = resolve_identity(args.agent, strict=True)
    canonical = identity["canonical_id"]
    route_key = identity["route_key"]
    holder_id = args.holder_id.strip()

    data = load_lock_file(lock_path)
    locks = data.setdefault("locks", {})
    existing = locks.get(canonical)
    if existing and not args.force:
        existing_holder = str(existing.get("holder_id", "")).strip()
        if existing_holder and existing_holder != holder_id:
            print(
                json.dumps(
                    {
                        "success": False,
                        "error": "identity_locked",
                        "agent": canonical,
                        "existing_holder_id": existing_holder,
                        "requested_holder_id": holder_id,
                        "lock_file": str(lock_path),
                    },
                    ensure_ascii=False,
                )
            )
            return 2

    locks[canonical] = {
        "route_key": route_key,
        "holder_id": holder_id,
        "claimed_at": now_iso(),
        "note": args.note or "",
    }
    save_lock_file(lock_path, data)
    print(
        json.dumps(
            {
                "success": True,
                "agent": canonical,
                "route_key": route_key,
                "holder_id": holder_id,
                "lock_file": str(lock_path),
            },
            ensure_ascii=False,
        )
    )
    return 0


def cmd_release(args: argparse.Namespace) -> int:
    lock_path = Path(args.lock_file).resolve()
    identity = resolve_identity(args.agent, strict=True)
    canonical = identity["canonical_id"]
    requested_holder = (args.holder_id or "").strip()

    data = load_lock_file(lock_path)
    locks = data.setdefault("locks", {})
    existing = locks.get(canonical)
    if not existing:
        print(
            json.dumps(
                {
                    "success": True,
                    "message": "no_lock",
                    "agent": canonical,
                    "lock_file": str(lock_path),
                },
                ensure_ascii=False,
            )
        )
        return 0

    existing_holder = str(existing.get("holder_id", "")).strip()
    if not args.force and requested_holder and existing_holder != requested_holder:
        print(
            json.dumps(
                {
                    "success": False,
                    "error": "holder_mismatch",
                    "agent": canonical,
                    "existing_holder_id": existing_holder,
                    "requested_holder_id": requested_holder,
                    "lock_file": str(lock_path),
                },
                ensure_ascii=False,
            )
        )
        return 2

    locks.pop(canonical, None)
    save_lock_file(lock_path, data)
    print(
        json.dumps(
            {
                "success": True,
                "released": canonical,
                "lock_file": str(lock_path),
            },
            ensure_ascii=False,
        )
    )
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Identity session lock manager")
    parser.add_argument(
        "--lock-file",
        default=".agent/comms/identity_session_locks.json",
        help="Path to identity session lock file",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Show lock state")
    p_status.set_defaults(func=cmd_status)

    p_claim = sub.add_parser("claim", help="Claim identity for holder")
    p_claim.add_argument("--agent", required=True, help="Canonical or alias agent identifier")
    p_claim.add_argument("--holder-id", required=True, help="Unique holder/session id")
    p_claim.add_argument("--note", help="Optional note")
    p_claim.add_argument("--force", action="store_true", help="Force overwrite existing lock")
    p_claim.set_defaults(func=cmd_claim)

    p_release = sub.add_parser("release", help="Release identity lock")
    p_release.add_argument("--agent", required=True, help="Canonical or alias agent identifier")
    p_release.add_argument("--holder-id", help="Holder id to verify before release")
    p_release.add_argument("--force", action="store_true", help="Release without holder match")
    p_release.set_defaults(func=cmd_release)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return args.func(args)
    except ValueError as exc:
        print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
