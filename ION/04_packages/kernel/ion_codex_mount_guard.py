"""Codex carrier mount guard for ION.

This module turns the ION Codex carrier mount into a local, repeatable status
check.  It affirms the mounted carrier surface while keeping role authority,
live execution, production authority, secrets, and accepted state gated.  Hooks
may include the rendered block to reassert posture every turn.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_ID = "ion.codex_mount_guard.v0_1"
READY_STATE = "CODEX_CARRIER_LOCAL_MOUNT_READY"
PARTIAL_STATE = "CODEX_CARRIER_LOCAL_MOUNT_PARTIAL"
BLOCKED_STATE = "CODEX_CARRIER_LOCAL_MOUNT_BLOCKED"
DEFAULT_CURRENT_STATUS_PATH = "ION/05_context/current/codex_cli/mount_guard/CURRENT_CODEX_CARRIER_MOUNT.json"

REQUIRED_REFS: tuple[tuple[str, str], ...] = (
    ("pyproject.toml", "shell_root_package_authority"),
    ("ION/REPO_AUTHORITY.md", "repo_authority"),
    ("ION/02_architecture/ION_MOUNT_CONTRACT.md", "mount_contract"),
    ("ION/02_architecture/CODEX_CLI_CARRIER_PROTOCOL.md", "codex_cli_carrier_protocol"),
    ("ION/03_registry/codex_cli_carrier_profile.yaml", "codex_cli_carrier_profile"),
    ("ION/07_templates/carriers/CODEX_CLI_EXECUTION_PACKET.md", "codex_cli_execution_packet_template"),
    ("ION/05_context/current/codex_solo/CAPSULE.md", "minimum_working_capsule"),
    ("ION/05_context/current/codex_solo/MINI.md", "lookup_receipt_index"),
    ("ION/05_context/current/codex_solo/HOT_CONTEXT.md", "hot_context"),
    ("ION/05_context/current/codex_solo/STATUS.json", "codex_solo_status"),
    ("ION/04_packages/kernel/ion_codex_carrier_sync.py", "carrier_sync_adapter"),
    ("ION/04_packages/kernel/ion_carrier_mount_receipt.py", "mount_receipt_helper"),
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _ref_status(root: Path, rel_path: str, purpose: str) -> dict[str, Any]:
    path = root / rel_path
    exists = path.is_file()
    return {
        "path": rel_path,
        "purpose": purpose,
        "exists": exists,
        "size": path.stat().st_size if exists else None,
        "sha256": _sha256_file(path) if exists else None,
    }


def build_codex_mount_status(
    root: str | Path,
    *,
    required_refs: Sequence[tuple[str, str]] = REQUIRED_REFS,
) -> dict[str, Any]:
    """Return the current Codex carrier mount status from local repo evidence."""

    root_path = Path(root).expanduser().resolve()
    root_proof = {
        "pyproject": (root_path / "pyproject.toml").is_file(),
        "repo_authority": (root_path / "ION/REPO_AUTHORITY.md").is_file(),
    }
    refs = [_ref_status(root_path, rel_path, purpose) for rel_path, purpose in required_refs]
    missing = [ref["path"] for ref in refs if not ref["exists"]]
    blockers: list[str] = []
    if not root_proof["pyproject"] or not root_proof["repo_authority"]:
        blockers.append("root_proof_missing")
    if missing:
        blockers.append("required_mount_refs_missing")

    if "root_proof_missing" in blockers:
        state = BLOCKED_STATE
    elif missing:
        state = PARTIAL_STATE
    else:
        state = READY_STATE

    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "active_root": root_path.as_posix(),
        "mount_truth_state": state,
        "ok": state == READY_STATE,
        "carrier": "codex_cli",
        "carrier_identity_posture": "ION_MOUNTED_CODEX_CARRIER",
        "root_proof": root_proof,
        "required_ref_count": len(refs),
        "required_refs_present": len(refs) - len(missing),
        "required_refs": refs,
        "missing_required_refs": missing,
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
        "source_order": [
            "operator",
            "active_repo_authority",
            "mount_contract",
            "codex_carrier_profile",
            "codex_execution_packet_template",
            "codex_solo_capsule",
            "receipts_and_tests",
            "approved_live_tools_only_after_local_posture",
        ],
        "blockers": blockers,
        "claims": [
            "mounted_ion_codex_carrier",
        ],
        "non_claims": [
            "steward_relay_or_persona_authority_requires_role_phase_proof",
            "no_production_authority",
            "no_live_execution_authority",
            "no_accepted_state_claim",
            "no_secrets_authority",
        ],
    }


def render_mount_guard_block(status: Mapping[str, Any]) -> str:
    """Render a compact hook-safe block for startup and prompt-submit context."""

    blockers = status.get("blockers") or []
    missing = status.get("missing_required_refs") or []
    return "\n".join(
        [
            "ION Codex Mount Guard v0.1",
            f"mount_truth_state: {status.get('mount_truth_state')}",
            f"active_root: {status.get('active_root')}",
            f"carrier: {status.get('carrier')}",
            f"carrier_identity_posture: {status.get('carrier_identity_posture')}",
            f"required_refs: {status.get('required_refs_present')}/{status.get('required_ref_count')}",
            (
                "authority: ION Codex carrier mounted; no production, no live execution, "
                "no accepted-state, no secrets"
            ),
            f"blockers: {', '.join(blockers) if blockers else 'none'}",
            f"missing_required_refs: {', '.join(missing[:6]) if missing else 'none'}",
            "mount_rule: re-prove local mount before serious ION work; block or stay receipt-only if partial.",
        ]
    )


def write_current_mount_status(
    root: str | Path,
    status: Mapping[str, Any],
    *,
    output_path: str | Path = DEFAULT_CURRENT_STATUS_PATH,
) -> dict[str, Any]:
    root_path = Path(root).expanduser().resolve()
    path = root_path / output_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(status), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "ok": bool(status.get("ok")),
        "path": _rel(path, root_path),
        "mount_truth_state": status.get("mount_truth_state"),
    }


def _status_command(args: argparse.Namespace) -> dict[str, Any]:
    status = build_codex_mount_status(args.ion_root)
    payload: dict[str, Any] = {"status": status, "block": render_mount_guard_block(status)}
    if args.write_current:
        payload["write_current"] = write_current_mount_status(args.ion_root, status)
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ION Codex carrier mount guard")
    parser.add_argument("--ion-root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)
    status = sub.add_parser("status")
    status.add_argument("--json", action="store_true")
    status.add_argument("--write-current", action="store_true")
    status.set_defaults(func=_status_command)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = args.func(args)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload["block"])
    return 0 if payload["status"].get("mount_truth_state") != BLOCKED_STATE else 2


if __name__ == "__main__":
    raise SystemExit(main())
