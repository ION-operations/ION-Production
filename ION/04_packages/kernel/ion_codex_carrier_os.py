"""Codex Carrier OS source-map projection for ION.

This module is the read-only/confirmation-gated operating-system map for the
Codex CLI carrier domain.  It composes the existing Codex carrier domain,
session registry, raw-context diagnostic lane, event ledger, cockpit projection,
Drive/context-mirror policy, and slash-command registry into one inspectable
runtime substrate.

It does not start Codex, execute shell commands, mutate Git, read raw Codex
memories/sessions, mirror files to Drive, or accept ION state.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .ion_codex_carrier_domain import (
    DOMAIN_READY_VERDICT,
    WRITE_CONFIRMATION_TOKEN as DOMAIN_WRITE_CONFIRMATION_TOKEN,
    build_codex_agent_registry,
    build_codex_carrier_cockpit_snapshot,
    build_codex_carrier_domain_registry,
    build_codex_carrier_event_ledger,
    build_codex_session_registry,
    emit_codex_carrier_event,
    initialize_codex_carrier_domain,
)
from .ion_codex_raw_context_sync import build_raw_context_sync_lane_status

SCHEMA_ID = "ion.codex_carrier_os_source_map.v1"
INIT_SCHEMA_ID = "ion.codex_carrier_os_initialization.v1"
READY_VERDICT = "ION_CODEX_CARRIER_OS_READY"
CANDIDATE_VERDICT = "ION_CODEX_CARRIER_OS_CANDIDATE"
BLOCKED_VERDICT = "ION_CODEX_CARRIER_OS_BLOCKED"
WRITE_CONFIRMATION_TOKEN = "ION_CODEX_CARRIER_OS_WRITE_CONFIRMED"

CONTENT_ROOT_NAME = "ION"
CODEX_CARRIER_DIR = Path("ION/05_context/current/codex_carrier")
SOURCE_MAP_PATH = CODEX_CARRIER_DIR / "CODEX_CARRIER_OS_SOURCE_MAP.json"
SLASH_COMMAND_REGISTRY_PATH = CODEX_CARRIER_DIR / "CODEX_SLASH_COMMAND_REGISTRY.json"
CONTEXT_MIRROR_POLICY_PATH = CODEX_CARRIER_DIR / "CODEX_CONTEXT_MIRROR_POLICY.json"
PROTOCOL_PATH = Path("ION/02_architecture/CODEX_CARRIER_OS_RUNTIME_PROTOCOL.md")

AUTHORITY_FALSE: dict[str, bool] = {
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "browser_control_authority": False,
    "github_push_authority": False,
    "drive_runtime_authority": False,
}

CONTROL_PLANES: tuple[dict[str, str], ...] = (
    {
        "plane_id": "codex_carrier_domain",
        "purpose": "carrier-domain registry, agents, required surfaces, authority boundary",
        "primary_ref": "ION/05_context/current/codex_carrier/CODEX_CARRIER_DOMAIN_REGISTRY.json",
    },
    {
        "plane_id": "codex_sessions",
        "purpose": "Codex session registry and branch-capsule binding",
        "primary_ref": "ION/05_context/current/codex_carrier/CODEX_SESSION_REGISTRY.json",
    },
    {
        "plane_id": "codex_agents",
        "purpose": "specialist/domain agent profile registry",
        "primary_ref": "ION/05_context/current/codex_carrier/CODEX_AGENT_REGISTRY.json",
    },
    {
        "plane_id": "raw_context_diagnostics",
        "purpose": "local-private raw Codex context manifests and redacted promotion path",
        "primary_ref": "ION/05_context/current/codex_carrier/CODEX_RAW_CONTEXT_SYNC_LANE_POLICY.md",
    },
    {
        "plane_id": "runtime_event_bus",
        "purpose": "public-safe event telemetry feeding cockpit/proof/drift displays",
        "primary_ref": "ION/05_context/current/codex_carrier/CODEX_CARRIER_EVENT_LEDGER.json",
    },
    {
        "plane_id": "cockpit_projection",
        "purpose": "operator-visible graph, drift, proof, services, and context truth projection",
        "primary_ref": "ION/05_context/current/codex_carrier/CODEX_CARRIER_COCKPIT_SNAPSHOT.json",
    },
    {
        "plane_id": "context_mirror",
        "purpose": "curated Google Drive/context mirror policy; never active working tree",
        "primary_ref": "ION/05_context/current/codex_carrier/CODEX_CONTEXT_MIRROR_POLICY.json",
    },
    {
        "plane_id": "slash_commands",
        "purpose": "deterministic Codex command wrappers for mount/status/proof/sync/handoff",
        "primary_ref": "ION/05_context/current/codex_carrier/CODEX_SLASH_COMMAND_REGISTRY.json",
    },
    {
        "plane_id": "commit_boundary_audit",
        "purpose": "path-level dirty-tree classification and candidate stage-manifest proposal; no git mutation",
        "primary_ref": "ION/05_context/current/codex_carrier/commit_boundary/CODEX_COMMIT_BOUNDARY_AUDIT.json",
    },
    {
        "plane_id": "source_bundle_stage_review",
        "purpose": "first safe source/protocol/schema/test stage proposal derived from commit-boundary audit; no git mutation",
        "primary_ref": "ION/05_context/current/codex_carrier/commit_boundary/CODEX_SOURCE_BUNDLE_STAGE_REVIEW.json",
    },
)

DEFAULT_SLASH_COMMANDS: tuple[dict[str, Any], ...] = (
    {"command": "/ion-mount", "mode": "read_only", "maps_to": "kernel.ion_carrier_onboard / carrier-domain status", "mutates": False},
    {"command": "/ion-identity", "mode": "read_only", "maps_to": "current carrier/session/branch identity card", "mutates": False},
    {"command": "/ion-packet", "mode": "read_only", "maps_to": "current packet + write scope + blockers", "mutates": False},
    {"command": "/ion-branch", "mode": "read_only", "maps_to": "branch capsule status and raw-context manifest ref", "mutates": False},
    {"command": "/ion-sync", "mode": "candidate_write", "maps_to": "rolling context + event append with confirmation", "mutates": True},
    {"command": "/ion-proof", "mode": "read_only_or_candidate_write", "maps_to": "proof ledger/status; candidate evidence refs only", "mutates": "confirmation_required"},
    {"command": "/ion-git-plan", "mode": "read_only", "maps_to": "git status/stage manifest proposal; no commit/push", "mutates": False},
    {"command": "/ion-commit-boundary", "mode": "read_only", "maps_to": "kernel.ion_codex_commit_boundary_audit path classification + candidate stage manifest", "mutates": False},
    {"command": "/ion-source-bundle", "mode": "read_only", "maps_to": "kernel.ion_codex_source_bundle_stage_review source/protocol/schema/test stage proposal", "mutates": False},
    {"command": "/ion-receipt", "mode": "candidate_write", "maps_to": "receipt proposal; acceptance remains Steward/operator gated", "mutates": "confirmation_required"},
    {"command": "/ion-settlement", "mode": "candidate_write", "maps_to": "settlement request package", "mutates": "confirmation_required"},
    {"command": "/ion-handoff", "mode": "candidate_write", "maps_to": "branch capsule handoff + event ledger", "mutates": "confirmation_required"},
)

RUNTIME_LOOP: tuple[str, ...] = (
    "operator_intent",
    "work_packet",
    "context_package",
    "carrier_mount_receipt",
    "codex_session_registration",
    "branch_capsule_binding",
    "local_codex_execution",
    "raw_context_manifest_optional",
    "proof_bearing_return",
    "runtime_event_emission",
    "cockpit_projection",
    "proof_gate",
    "settlement_request",
    "steward_or_operator_decision",
    "receipt",
    "next_context_inheritance",
)

NATIVE_CODEX_CAPABILITY_BINDINGS: tuple[dict[str, Any], ...] = (
    {"capability": "sessions_resume", "ion_binding": "CODEX_SESSION_REGISTRY + branch capsule", "authority": "orientation_only_until_receipt"},
    {"capability": "memories", "ion_binding": "memory policy + raw-context diagnostic lane", "authority": "diagnostic_continuity_only"},
    {"capability": "AGENTS.md", "ion_binding": "carrier instructions + ION mount contract", "authority": "role_context_not_state"},
    {"capability": "config.toml", "ion_binding": "sanitized local PC audit; values redacted", "authority": "configuration_evidence_only"},
    {"capability": "hooks", "ion_binding": "mount/session/sync/proof preflight hooks", "authority": "guardrail_not_acceptance"},
    {"capability": "slash_commands", "ion_binding": "CODEX_SLASH_COMMAND_REGISTRY", "authority": "deterministic_wrapper_only"},
    {"capability": "subagents", "ion_binding": "child branch capsules + parent settlement target", "authority": "candidate_subbranch_only"},
    {"capability": "MCP", "ion_binding": "read-only/dry-run local bridge projections", "authority": "transport_not_law"},
    {"capability": "app_server_remote_control", "ion_binding": "cockpit service map + explicit approval gates", "authority": "not_authorized_by_default"},
    {"capability": "git_review", "ion_binding": "stage/commit proposal evidence + human push gate", "authority": "proposal_not_merge"},
)

DEFAULT_CONTEXT_MIRROR_POLICY: dict[str, Any] = {
    "schema_id": "ion.codex_context_mirror_policy.v1",
    "mirror_role": "curated_context_visibility_lane",
    "live_repo_runs_from_drive": False,
    "drive_is_active_working_tree": False,
    "drive_may_carry_curated_context_package": True,
    "drive_may_carry_raw_codex_context_by_default": False,
    "drive_may_carry_secrets": False,
    "drive_may_carry_git_metadata": False,
    "default_include_refs": [
        "ION/REPO_AUTHORITY.md",
        "ION/02_architecture/ION_MOUNT_CONTRACT.md",
        "ION/02_architecture/CODEX_CARRIER_OS_RUNTIME_PROTOCOL.md",
        "ION/02_architecture/CODEX_COMMIT_BOUNDARY_AUDIT_PROTOCOL.md",
        "ION/02_architecture/CODEX_SOURCE_BUNDLE_STAGE_REVIEW_PROTOCOL.md",
        "ION/05_context/current/codex_carrier/CODEX_CARRIER_OS_SOURCE_MAP.json",
        "ION/05_context/current/codex_carrier/CODEX_CARRIER_COCKPIT_SNAPSHOT.json",
        "ION/05_context/current/codex_carrier/CODEX_SESSION_REGISTRY.json",
        "ION/05_context/current/codex_carrier/CODEX_CARRIER_EVENT_LEDGER.json",
        "ION/05_context/current/codex_carrier/commit_boundary/CODEX_COMMIT_BOUNDARY_AUDIT.json",
        "ION/05_context/current/codex_carrier/commit_boundary/CODEX_SOURCE_BUNDLE_STAGE_REVIEW.json",
    ],
    "default_exclude_globs": [
        ".git/**",
        ".ion_private/**",
        ".env*",
        "**/*token*",
        "**/*secret*",
        "**/*credential*",
        "ION/05_context/current/action_gateway/runtime/**",
        "ION/05_context/current/chatgpt_connector/runtime/**",
        "ION/05_context/current/codex_capsule_chat/response_runs/**",
    ],
    "mount_receipt_required": True,
    "freshness_proof_required": True,
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_shell_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    probes = [candidate, *candidate.parents]
    for path in probes:
        if (path / "pyproject.toml").is_file() and (path / "ION" / "REPO_AUTHORITY.md").is_file():
            return path
        if path.name == CONTENT_ROOT_NAME and (path / "REPO_AUTHORITY.md").is_file():
            parent = path.parent
            if (parent / "pyproject.toml").is_file():
                return parent
    raise FileNotFoundError("Could not resolve ION shell root; expected pyproject.toml and ION/REPO_AUTHORITY.md")


def _read_json(path: Path) -> Any | None:
    if not path.exists() or not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _surface_status(shell_root: Path, rel: str | Path) -> dict[str, Any]:
    path = shell_root / Path(rel)
    return {
        "path": Path(rel).as_posix(),
        "exists": path.exists(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
        "bytes": path.stat().st_size if path.exists() and path.is_file() else None,
    }


def _control_plane_status(shell_root: Path) -> list[dict[str, Any]]:
    planes: list[dict[str, Any]] = []
    for item in CONTROL_PLANES:
        primary = _surface_status(shell_root, item["primary_ref"])
        status = "READY" if primary["exists"] else "CANDIDATE"
        planes.append({**item, "status": status, "surface": primary})
    return planes


def _default_slash_command_registry(shell_root: Path) -> dict[str, Any]:
    return {
        "schema_id": "ion.codex_slash_command_registry.v1",
        "generated_at": _now(),
        "path": SLASH_COMMAND_REGISTRY_PATH.as_posix(),
        "command_count": len(DEFAULT_SLASH_COMMANDS),
        "commands": list(DEFAULT_SLASH_COMMANDS),
        "rule": "Slash commands are deterministic wrappers; they do not confer authority or accepted state.",
        **AUTHORITY_FALSE,
    }


def build_slash_command_registry(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    payload = _read_json(shell_root / SLASH_COMMAND_REGISTRY_PATH)
    if isinstance(payload, dict):
        payload = dict(payload)
        payload["command_count"] = len(payload.get("commands", [])) if isinstance(payload.get("commands"), list) else 0
        return payload
    return _default_slash_command_registry(shell_root)


def write_slash_command_registry(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    payload = _default_slash_command_registry(shell_root)
    _write_json(shell_root / SLASH_COMMAND_REGISTRY_PATH, payload)
    return payload


def build_context_mirror_policy(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    payload = _read_json(shell_root / CONTEXT_MIRROR_POLICY_PATH)
    if isinstance(payload, dict):
        merged = dict(DEFAULT_CONTEXT_MIRROR_POLICY)
        merged.update(payload)
        return merged
    return dict(DEFAULT_CONTEXT_MIRROR_POLICY)


def write_context_mirror_policy(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    payload = dict(DEFAULT_CONTEXT_MIRROR_POLICY)
    payload["generated_at"] = _now()
    payload["path"] = CONTEXT_MIRROR_POLICY_PATH.as_posix()
    _write_json(shell_root / CONTEXT_MIRROR_POLICY_PATH, payload)
    return payload


def _findings_for_source_map(shell_root: Path, domain: Mapping[str, Any], raw_context: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []
    if not (shell_root / PROTOCOL_PATH).exists():
        findings.append(f"missing_codex_carrier_os_runtime_protocol:{PROTOCOL_PATH.as_posix()}")
    if not domain.get("ok"):
        findings.extend(str(item) for item in domain.get("findings", []))
    if not raw_context.get("ok"):
        findings.extend(str(item) for item in raw_context.get("findings", []))
    mirror = build_context_mirror_policy(shell_root)
    if mirror.get("live_repo_runs_from_drive") or mirror.get("drive_is_active_working_tree"):
        findings.append("context_mirror_policy_allows_drive_as_active_worktree")
    return findings


def build_codex_carrier_os_source_map(root: str | Path | None = None) -> dict[str, Any]:
    """Return the full Codex Carrier OS source map without mutating state."""
    shell_root = _resolve_shell_root(root)
    domain = build_codex_carrier_domain_registry(shell_root)
    cockpit = build_codex_carrier_cockpit_snapshot(shell_root)
    sessions = build_codex_session_registry(shell_root)
    agents = build_codex_agent_registry(shell_root)
    raw_context = build_raw_context_sync_lane_status(shell_root)
    events = build_codex_carrier_event_ledger(shell_root)
    slash = build_slash_command_registry(shell_root)
    mirror = build_context_mirror_policy(shell_root)
    findings = _findings_for_source_map(shell_root, domain, raw_context)
    blocked = bool(domain.get("ok") is False)

    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "verdict": BLOCKED_VERDICT if blocked else (CANDIDATE_VERDICT if findings else READY_VERDICT),
        "ok": not blocked,
        "source_map_ready": not findings,
        "shell_root": str(shell_root),
        "content_root": str(shell_root / "ION"),
        "path": SOURCE_MAP_PATH.as_posix(),
        "protocol_ref": PROTOCOL_PATH.as_posix(),
        "packet_ref": "PCKT-ION-CODEX-CARRIER-OPERATING-SYSTEM-ORCHESTRATION-001",
        "role_split": {
            "ion": "law, receipts, branch capsules, settlement, continuity",
            "codex_cli": "bounded local implementation/build/test worker",
            "gpt001": "live carrier/MCP/Action coordinator and local-state verifier",
            "sev_gpt_pro": "architecture/Nemesis/orchestration review",
            "operator": "final operational authority",
        },
        "runtime_loop": list(RUNTIME_LOOP),
        "control_planes": _control_plane_status(shell_root),
        "codex_native_capability_bindings": list(NATIVE_CODEX_CAPABILITY_BINDINGS),
        "domain_registry": {
            "verdict": domain.get("verdict"),
            "ok": domain.get("ok"),
            "agent_count": len(domain.get("agents", [])) if isinstance(domain.get("agents"), list) else None,
            "mcp_read_only_tools": domain.get("mcp_read_only_tools", []),
        },
        "agent_registry": {
            "path": agents.get("path"),
            "agent_count": agents.get("agent_count"),
        },
        "session_registry": {
            "path": sessions.get("path"),
            "session_count": sessions.get("session_count"),
            "active_session_count": sessions.get("active_session_count"),
        },
        "raw_context_sync_lane": {
            "verdict": raw_context.get("verdict"),
            "ok": raw_context.get("ok"),
            "manifest_count": raw_context.get("manifest_count"),
            "raw_content_exported": raw_context.get("raw_content_exported"),
            "private_storage_ref": raw_context.get("private_storage_ref"),
        },
        "runtime_event_bus": {
            "path": events.get("path"),
            "event_count": events.get("event_count"),
            "events_dir": events.get("events_dir"),
            "recent_event_count": len(events.get("recent_events", [])) if isinstance(events.get("recent_events"), list) else 0,
        },
        "cockpit_projection": {
            "path": cockpit.get("path"),
            "drift_signal_count": len(cockpit.get("drift_signals", [])) if isinstance(cockpit.get("drift_signals"), list) else 0,
            "git_dirty": cockpit.get("project", {}).get("git", {}).get("dirty") if isinstance(cockpit.get("project"), dict) else None,
        },
        "slash_command_registry": slash,
        "context_mirror_policy": mirror,
        "non_claims": [
            "Codex Carrier OS source map does not start Codex or mutate local services.",
            "Source map is candidate/projection state until proof gates and settlement accept changes.",
            "Drive/context mirror is curated visibility, not an active repo or runtime authority.",
            "Raw Codex context remains local-private by default; manifests are not raw content.",
        ],
        "findings": findings,
        **AUTHORITY_FALSE,
    }


def write_codex_carrier_os_source_map(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    payload = build_codex_carrier_os_source_map(shell_root)
    _write_json(shell_root / SOURCE_MAP_PATH, payload)
    return payload


def initialize_codex_carrier_os(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    domain_init = initialize_codex_carrier_domain(shell_root)
    slash = write_slash_command_registry(shell_root)
    mirror = write_context_mirror_policy(shell_root)
    source_map = write_codex_carrier_os_source_map(shell_root)
    event = emit_codex_carrier_event(
        shell_root,
        event_type="codex.carrier_os.initialized",
        actor={"carrier": "gpt_5_5_pro_sandbox", "agent_tag": "ion_pro_sev"},
        packet_id="PCKT-ION-CODEX-CARRIER-OPERATING-SYSTEM-ORCHESTRATION-001",
        refs=[SOURCE_MAP_PATH.as_posix(), SLASH_COMMAND_REGISTRY_PATH.as_posix(), CONTEXT_MIRROR_POLICY_PATH.as_posix()],
        detail="Codex Carrier OS source-map/control-plane surfaces initialized as candidate state.",
    )
    # Refresh source map after event append so event_count reflects initialization.
    source_map = write_codex_carrier_os_source_map(shell_root)
    return {
        "schema_id": INIT_SCHEMA_ID,
        "generated_at": _now(),
        "verdict": source_map.get("verdict"),
        "ok": bool(source_map.get("ok")),
        "written_paths": [
            *domain_init.get("written_paths", []),
            SLASH_COMMAND_REGISTRY_PATH.as_posix(),
            CONTEXT_MIRROR_POLICY_PATH.as_posix(),
            SOURCE_MAP_PATH.as_posix(),
            event.get("path"),
        ],
        "domain_initialization": domain_init,
        "slash_command_registry": {"path": SLASH_COMMAND_REGISTRY_PATH.as_posix(), "command_count": slash.get("command_count")},
        "context_mirror_policy": {"path": CONTEXT_MIRROR_POLICY_PATH.as_posix(), "live_repo_runs_from_drive": mirror.get("live_repo_runs_from_drive")},
        "source_map": {"path": SOURCE_MAP_PATH.as_posix(), "source_map_ready": source_map.get("source_map_ready")},
        "event": {"event_id": event.get("event_id"), "path": event.get("path")},
        **AUTHORITY_FALSE,
    }


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _add_common_root_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--ion-root", default=argparse.SUPPRESS, help="Shell root or ION content root")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Project or initialize the ION Codex Carrier OS source map.")
    parser.add_argument("--ion-root", default=".", help="Shell root or ION content root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="Read-only Codex Carrier OS source map")
    _add_common_root_argument(status)
    status.add_argument("--json", action="store_true")

    write = subparsers.add_parser("write", help="Write current source map/slash/mirror projections")
    _add_common_root_argument(write)
    write.add_argument("--confirmation", required=True, help=f"Required token: {WRITE_CONFIRMATION_TOKEN}")
    write.add_argument("--json", action="store_true")

    init = subparsers.add_parser("init", help="Initialize Codex Carrier OS control-plane surfaces")
    _add_common_root_argument(init)
    init.add_argument("--confirmation", required=True, help=f"Required token: {WRITE_CONFIRMATION_TOKEN}")
    init.add_argument("--json", action="store_true")

    mirror = subparsers.add_parser("mirror-policy", help="Read-only Drive/context mirror policy")
    _add_common_root_argument(mirror)
    mirror.add_argument("--write", action="store_true")
    mirror.add_argument("--confirmation", default=None, help=f"Required with --write: {WRITE_CONFIRMATION_TOKEN}")
    mirror.add_argument("--json", action="store_true")

    slash = subparsers.add_parser("slash-commands", help="Read-only Codex slash command registry")
    _add_common_root_argument(slash)
    slash.add_argument("--write", action="store_true")
    slash.add_argument("--confirmation", default=None, help=f"Required with --write: {WRITE_CONFIRMATION_TOKEN}")
    slash.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "status":
            payload = build_codex_carrier_os_source_map(args.ion_root)
            if args.json:
                _print_json(payload)
            else:
                print(payload["verdict"])
                for finding in payload.get("findings", []):
                    print(f"- {finding}")
            return 0 if payload.get("ok") else 2

        if args.command == "write":
            if args.confirmation != WRITE_CONFIRMATION_TOKEN:
                payload = {
                    "ok": False,
                    "schema_id": "ion.codex_carrier_os_write_refusal.v1",
                    "refusal_class": "CONFIRMATION_REQUIRED",
                    "required_confirmation": WRITE_CONFIRMATION_TOKEN,
                    **AUTHORITY_FALSE,
                }
                if args.json:
                    _print_json(payload)
                else:
                    print(f"Refused: confirmation must be {WRITE_CONFIRMATION_TOKEN}", file=sys.stderr)
                return 3
            slash = write_slash_command_registry(args.ion_root)
            mirror = write_context_mirror_policy(args.ion_root)
            source = write_codex_carrier_os_source_map(args.ion_root)
            payload = {
                "schema_id": "ion.codex_carrier_os_write_result.v1",
                "generated_at": _now(),
                "ok": bool(source.get("ok")),
                "verdict": source.get("verdict"),
                "written_paths": [SLASH_COMMAND_REGISTRY_PATH.as_posix(), CONTEXT_MIRROR_POLICY_PATH.as_posix(), SOURCE_MAP_PATH.as_posix()],
                "slash_command_registry": {"command_count": slash.get("command_count")},
                "context_mirror_policy": {"live_repo_runs_from_drive": mirror.get("live_repo_runs_from_drive")},
                **AUTHORITY_FALSE,
            }
            if args.json:
                _print_json(payload)
            else:
                print(payload["verdict"])
            return 0 if payload.get("ok") else 2

        if args.command == "init":
            if args.confirmation != WRITE_CONFIRMATION_TOKEN:
                payload = {
                    "ok": False,
                    "schema_id": "ion.codex_carrier_os_init_refusal.v1",
                    "refusal_class": "CONFIRMATION_REQUIRED",
                    "required_confirmation": WRITE_CONFIRMATION_TOKEN,
                    **AUTHORITY_FALSE,
                }
                if args.json:
                    _print_json(payload)
                else:
                    print(f"Refused: confirmation must be {WRITE_CONFIRMATION_TOKEN}", file=sys.stderr)
                return 3
            payload = initialize_codex_carrier_os(args.ion_root)
            if args.json:
                _print_json(payload)
            else:
                print(payload["verdict"])
            return 0 if payload.get("ok") else 2

        if args.command == "mirror-policy":
            if args.write:
                if args.confirmation != WRITE_CONFIRMATION_TOKEN:
                    payload = {"ok": False, "refusal_class": "CONFIRMATION_REQUIRED", "required_confirmation": WRITE_CONFIRMATION_TOKEN, **AUTHORITY_FALSE}
                    if args.json:
                        _print_json(payload)
                    else:
                        print(f"Refused: confirmation must be {WRITE_CONFIRMATION_TOKEN}", file=sys.stderr)
                    return 3
                payload = write_context_mirror_policy(args.ion_root)
            else:
                payload = build_context_mirror_policy(args.ion_root)
            if args.json:
                _print_json(payload)
            else:
                print("CODEX_CONTEXT_MIRROR_POLICY")
            return 0

        if args.command == "slash-commands":
            if args.write:
                if args.confirmation != WRITE_CONFIRMATION_TOKEN:
                    payload = {"ok": False, "refusal_class": "CONFIRMATION_REQUIRED", "required_confirmation": WRITE_CONFIRMATION_TOKEN, **AUTHORITY_FALSE}
                    if args.json:
                        _print_json(payload)
                    else:
                        print(f"Refused: confirmation must be {WRITE_CONFIRMATION_TOKEN}", file=sys.stderr)
                    return 3
                payload = write_slash_command_registry(args.ion_root)
            else:
                payload = build_slash_command_registry(args.ion_root)
            if args.json:
                _print_json(payload)
            else:
                print(f"commands={payload.get('command_count')}")
            return 0
    except Exception as exc:
        payload = {
            "ok": False,
            "schema_id": "ion.codex_carrier_os_cli_error.v1",
            "error": str(exc),
            **AUTHORITY_FALSE,
        }
        if getattr(args, "json", False):
            _print_json(payload)
        else:
            print(json.dumps(payload, indent=2, sort_keys=True), file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
