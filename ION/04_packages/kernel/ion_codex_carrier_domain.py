"""Codex Carrier Domain registry and cockpit projection for ION.

This module gives Codex CLI/App a first-class, inspectable ION carrier-domain
surface without promoting Codex memory or session transcripts into accepted ION
state. It is intentionally local-first and repo-bounded:

- read-only status/cockpit projections are safe for MCP exposure;
- write operations require an explicit confirmation token;
- raw ``~/.codex`` memories/sessions are not exported here;
- raw-context continuity is represented by safe manifests/excerpts only;
- generated session records remain candidate carrier state until settlement.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .ion_codex_local_pc_audit import (
    AUDIT_OUTPUT_PATH as LOCAL_CODEX_PC_AUDIT_PATH,
    WRITE_CONFIRMATION_TOKEN as LOCAL_CODEX_PC_AUDIT_CONFIRMATION_TOKEN,
    build_codex_local_pc_audit,
    write_codex_local_pc_audit,
)
from .ion_codex_raw_context_sync import (
    POLICY_PATH as RAW_CONTEXT_POLICY_PATH,
    PRIVATE_RAW_CONTEXT_DIR,
    PROTOCOL_PATH as RAW_CONTEXT_PROTOCOL_PATH,
    build_raw_context_sync_lane_status,
    create_raw_context_manifest,
    initialize_raw_context_sync_lane,
)

SCHEMA_ID = "ion.codex_carrier_domain.v1"
DOMAIN_READY_VERDICT = "ION_CODEX_CARRIER_DOMAIN_READY"
DOMAIN_BLOCKED_VERDICT = "ION_CODEX_CARRIER_DOMAIN_BLOCKED"
WRITE_CONFIRMATION_TOKEN = "ION_CODEX_CARRIER_DOMAIN_WRITE_CONFIRMED"

CONTENT_ROOT_NAME = "ION"
CODEX_CARRIER_DIR = Path("ION/05_context/current/codex_carrier")
DOMAIN_REGISTRY_PATH = CODEX_CARRIER_DIR / "CODEX_CARRIER_DOMAIN_REGISTRY.json"
AGENT_REGISTRY_PATH = CODEX_CARRIER_DIR / "CODEX_AGENT_REGISTRY.json"
SESSION_REGISTRY_PATH = CODEX_CARRIER_DIR / "CODEX_SESSION_REGISTRY.json"
SESSIONS_DIR = CODEX_CARRIER_DIR / "sessions"
CODEX_BRANCH_CAPSULE_BASE = Path("ION/05_context/current/agent_context_branches/codex_carrier")
MEMORY_POLICY_PATH = CODEX_CARRIER_DIR / "CODEX_MEMORY_POLICY.md"
ROLLING_CONTEXT_TEMPLATE_PATH = CODEX_CARRIER_DIR / "ROLLING_CONTEXT.template.md"
COCKPIT_SNAPSHOT_PATH = CODEX_CARRIER_DIR / "CODEX_CARRIER_COCKPIT_SNAPSHOT.json"
EVENT_LEDGER_PATH = CODEX_CARRIER_DIR / "CODEX_CARRIER_EVENT_LEDGER.json"
EVENTS_DIR = CODEX_CARRIER_DIR / "events"
RAW_CONTEXT_MANIFESTS_DIR = CODEX_CARRIER_DIR / "raw_context_manifests"
README_PATH = CODEX_CARRIER_DIR / "README.md"
RAW_CONTEXT_PROTOCOL_PATH = Path("ION/02_architecture/CODEX_RAW_CONTEXT_SYNC_LANE_PROTOCOL.md")
EVENT_BUS_PROTOCOL_PATH = Path("ION/02_architecture/CODEX_CARRIER_EVENT_BUS_PROTOCOL.md")
RAW_CONTEXT_MANIFEST_SCHEMA_PATH = Path("ION/03_registry/ion_codex_raw_context_manifest.schema.json")
RUNTIME_EVENT_SCHEMA_PATH = Path("ION/03_registry/ion_codex_carrier_runtime_event.schema.json")

REQUIRED_SURFACES: dict[str, str] = {
    "repo_authority": "ION/REPO_AUTHORITY.md",
    "mount_contract": "ION/02_architecture/ION_MOUNT_CONTRACT.md",
    "codex_cli_protocol": "ION/02_architecture/CODEX_CLI_CARRIER_PROTOCOL.md",
    "codex_cli_profile": "ION/03_registry/codex_cli_carrier_profile.yaml",
    "codex_cli_template": "ION/07_templates/carriers/CODEX_CLI_EXECUTION_PACKET.md",
    "codex_carrier_domain_protocol": "ION/02_architecture/CODEX_CARRIER_DOMAIN_PROTOCOL.md",
    "codex_raw_context_sync_protocol": RAW_CONTEXT_PROTOCOL_PATH.as_posix(),
    "codex_carrier_event_bus_protocol": EVENT_BUS_PROTOCOL_PATH.as_posix(),
    "codex_raw_context_manifest_schema": RAW_CONTEXT_MANIFEST_SCHEMA_PATH.as_posix(),
    "codex_carrier_runtime_event_schema": RUNTIME_EVENT_SCHEMA_PATH.as_posix(),
    "codex_cli_audit_module": "ION/04_packages/kernel/ion_codex_cli_carrier_audit.py",
    "codex_solo_context_module": "ION/04_packages/kernel/ion_codex_solo_context.py",
    "codex_carrier_domain_module": "ION/04_packages/kernel/ion_codex_carrier_domain.py",
    "mcp_local_bridge_module": "ION/04_packages/kernel/ion_mcp_local_bridge.py",
    "project_codex_config": ".codex/config.toml",
    "session_start_hook": ".codex/hooks/ion_session_start_context.py",
    "codex_solo_hot_context": "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
    "branch_capsule_registry": "ION/05_context/current/agent_context_branches/BRANCH_CAPSULE_REGISTRY_V0_1.json",
}

CURRENT_CONTEXT_SURFACES: dict[str, str] = {
    "domain_registry": DOMAIN_REGISTRY_PATH.as_posix(),
    "agent_registry": AGENT_REGISTRY_PATH.as_posix(),
    "session_registry": SESSION_REGISTRY_PATH.as_posix(),
    "sessions_dir": SESSIONS_DIR.as_posix(),
    "raw_context_manifests_dir": RAW_CONTEXT_MANIFESTS_DIR.as_posix(),
    "event_ledger": EVENT_LEDGER_PATH.as_posix(),
    "events_dir": EVENTS_DIR.as_posix(),
    "branch_capsule_base": CODEX_BRANCH_CAPSULE_BASE.as_posix(),
    "memory_policy": MEMORY_POLICY_PATH.as_posix(),
    "raw_context_policy": RAW_CONTEXT_POLICY_PATH.as_posix(),
    "rolling_context_template": ROLLING_CONTEXT_TEMPLATE_PATH.as_posix(),
    "cockpit_snapshot": COCKPIT_SNAPSHOT_PATH.as_posix(),
    "readme": README_PATH.as_posix(),
}

FORBIDDEN_CLAIMS = [
    "ION identity",
    "STEWARD authority",
    "RELAY authority",
    "PERSONA authority",
    "accepted-state authority",
    "production authority",
    "live execution authority",
    "secrets authority",
    "direct shared Capsule/Mini/HOT_CONTEXT mutation",
]

DEFAULT_MEMORY_POLICY: dict[str, Any] = {
    "schema_id": "ion.codex_carrier_memory_policy.v2",
    "codex_memory_role": "bounded_diagnostic_continuity",
    "raw_context_sync_lane": "manifest_only_by_default",
    "raw_memory_export": "forbidden_without_explicit_review",
    "memory_may_orient": True,
    "raw_context_may_diagnose": True,
    "raw_context_may_accept_state": False,
    "memory_may_accept_state": False,
    "branch_capsule_governs_current_work": True,
    "receipt_or_settlement_required_for_durable_claims": True,
    "secrets_redaction_required": True,
    "raw_context_private_storage": ".ion_private/codex_raw_context/<agent_tag>/<session_id>/",
    "raw_context_manifest_committable": True,
    "raw_context_content_committable_by_default": False,
    "raw_context_drive_mirror_allowed_by_default": False,
}

DEFAULT_SERVICE_PORTS: list[dict[str, Any]] = [
    {"port": 8765, "owner": "ION MCP preview", "status_source": "local_runtime_or_tunnel_probe"},
    {"port": 8777, "owner": "Action Gateway", "status_source": "local_runtime_probe"},
    {"port": 8788, "owner": "ION local cockpit", "status_source": "local_runtime_probe"},
    {"port": 8795, "owner": "dAimon Gemini bridge", "status_source": "local_runtime_probe"},
    {"port": 8796, "owner": "dAimon reserved secondary", "status_source": "reservation_only"},
]

DEFAULT_CODEX_AGENTS: list[dict[str, Any]] = [
    {
        "agent_tag": "codex_001",
        "code_name": "CODEX-001",
        "domain": "local_codex_cli_carrier_mount_and_binding",
        "role_hint": "operator-designated Codex CLI local-PC carrier for live mount audit and carrier-OS binding",
        "default_write_scope": [
            "ION/02_architecture/",
            "ION/03_registry/",
            "ION/04_packages/kernel/",
            "ION/05_context/current/codex_carrier/",
            "ION/05_context/current/codex_local_pc/",
            "ION/05_context/current/agent_context_branches/",
            "ION/tests/",
            "diffs/",
            "workpackets/",
        ],
        "branch_capsule_required": True,
        "settlement_required": True,
    },
    {
        "agent_tag": "codex_local_ion_mason",
        "domain": "local_filesystem_build_test",
        "role_hint": "bounded implementation worker for repo-local code/docs/tests",
        "default_write_scope": [
            "ION/04_packages/kernel/",
            "ION/tests/",
            "ION/02_architecture/",
            "ION/03_registry/",
            "ION/05_context/current/codex_carrier/",
            "diffs/",
            "workpackets/",
        ],
        "branch_capsule_required": True,
        "settlement_required": True,
    },
    {
        "agent_tag": "codex_runtime_cartographer",
        "domain": "runtime_and_service_inventory",
        "role_hint": "read-first runtime/service/port/state cartography",
        "default_write_scope": ["ION/05_context/current/codex_carrier/", "diffs/", "workpackets/"],
        "branch_capsule_required": True,
        "settlement_required": True,
    },
    {
        "agent_tag": "codex_git_orchestration_steward",
        "domain": "git_stage_commit_settlement_planning",
        "role_hint": "git state classification and commit-proposal evidence, not autonomous push authority",
        "default_write_scope": ["ION/05_context/current/git_orchestration/", "diffs/", "workpackets/"],
        "branch_capsule_required": True,
        "settlement_required": True,
    },
    {
        "agent_tag": "codex_branch_capsule_architect",
        "domain": "branch_context_capsule_design",
        "role_hint": "branch capsule schemas, identity cards, and settlement inbox mechanics",
        "default_write_scope": ["ION/05_context/current/agent_context_branches/", "ION/05_context/current/context_settlement/"],
        "branch_capsule_required": True,
        "settlement_required": True,
    },
    {
        "agent_tag": "codex_ui_joc_opus_canonist",
        "domain": "joc_opus_ui_canon_and_visual_proof",
        "role_hint": "UI/cockpit implementation under JOC/OPUS canon with visual proof gates",
        "default_write_scope": ["ION/08_ui/", "ION/04_packages/kernel/ion_codex_chat_*", "diffs/", "workpackets/"],
        "branch_capsule_required": True,
        "settlement_required": True,
    },
    {
        "agent_tag": "codex_daimon_bridge_specialist",
        "domain": "daimon_bridge_and_sibling_repo_integration",
        "role_hint": "dAimon bridge planning and bounded integration evidence",
        "default_write_scope": ["ION/05_context/current/codex_carrier/", "workpackets/", "diffs/"],
        "branch_capsule_required": True,
        "settlement_required": True,
    },
    {
        "agent_tag": "codex_proof_nemesis",
        "domain": "proof_gate_adversarial_audit",
        "role_hint": "adversarial validation, drift detection, and failure-mode attack",
        "default_write_scope": ["ION/tests/", "ION/05_context/current/codex_carrier/", "diffs/"],
        "branch_capsule_required": True,
        "settlement_required": True,
    },
    {
        "agent_tag": "codex_extension_cockpit_specialist",
        "domain": "browser_extension_and_local_cockpit",
        "role_hint": "extension/cockpit interface specialist with visual and approval-bound proof gates",
        "default_write_scope": ["../browser_extension/", "ION/08_ui/", "ION/tests/", "diffs/", "workpackets/"],
        "branch_capsule_required": True,
        "settlement_required": True,
    },
    {
        "agent_tag": "codex_mcp_action_gateway_specialist",
        "domain": "mcp_action_gateway_and_tool_boundary",
        "role_hint": "MCP/Action Gateway routing, confirmation, and tool-boundary maintainer",
        "default_write_scope": ["ION/04_packages/kernel/ion_mcp*", "ION/05_context/current/action_gateway/", "ION/tests/", "diffs/"],
        "branch_capsule_required": True,
        "settlement_required": True,
    },
    {
        "agent_tag": "codex_context_settler_assistant",
        "domain": "context_settlement_preparation",
        "role_hint": "settlement request preparer that never accepts state by itself",
        "default_write_scope": ["ION/05_context/current/context_settlement/", "ION/05_context/current/codex_carrier/", "workpackets/"],
        "branch_capsule_required": True,
        "settlement_required": True,
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stamp() -> str:
    return _now().replace("-", "").replace(":", "").replace("+00:00", "Z")


def _slug(value: str, fallback: str = "codex_session") -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "").strip().lower()).strip("._-")
    return (slug or fallback)[:96]


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


def _read_text(path: Path, *, max_chars: int = 8000) -> str:
    if not path.exists() or not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text if len(text) <= max_chars else text[:max_chars] + "\n...[truncated]"


def _surface_status(shell_root: Path, rel: str) -> dict[str, Any]:
    path = shell_root / rel
    return {
        "path": rel,
        "exists": path.exists(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
        "bytes": path.stat().st_size if path.exists() and path.is_file() else None,
    }


def _git_state(shell_root: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "available": False,
        "branch": None,
        "dirty": None,
        "porcelain_count": None,
        "porcelain_sample": [],
    }
    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=shell_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=shell_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception as exc:  # pragma: no cover - environment defensive path
        result["error"] = str(exc)
        return result
    if branch.returncode == 0 and status.returncode == 0:
        lines = [line for line in status.stdout.splitlines() if line.strip()]
        result.update({
            "available": True,
            "branch": branch.stdout.strip() or None,
            "dirty": bool(lines),
            "porcelain_count": len(lines),
            "porcelain_sample": lines[:40],
        })
    return result


def _session_files(shell_root: Path) -> list[Path]:
    path = shell_root / SESSIONS_DIR
    if not path.exists():
        return []
    return sorted(p for p in path.glob("*.json") if p.is_file())


def _load_sessions(shell_root: Path) -> list[dict[str, Any]]:
    sessions: list[dict[str, Any]] = []
    for path in _session_files(shell_root):
        payload = _read_json(path)
        if isinstance(payload, dict):
            payload.setdefault("path", path.relative_to(shell_root).as_posix())
            sessions.append(payload)
    return sessions


def _agent_by_tag(agent_tag: str) -> dict[str, Any] | None:
    for agent in DEFAULT_CODEX_AGENTS:
        if agent["agent_tag"] == agent_tag:
            return agent
    return None


def _raw_context_private_ref(agent_tag: str, session_id: str) -> str:
    return f".ion_private/codex_raw_context/{_slug(agent_tag)}/{_slug(session_id)}/"


def build_codex_raw_context_manifest(session: Mapping[str, Any]) -> dict[str, Any]:
    """Return a public-safe manifest for a local-private raw Codex context lane.

    The manifest proves that a raw-context continuity lane may exist for a
    session. It deliberately does not export raw session text, filenames, or
    memory content.
    """
    session_id = str(session.get("session_id") or "unknown_session")
    agent_tag = str(session.get("agent_tag") or "unknown_agent")
    manifest_ref = f"{RAW_CONTEXT_MANIFESTS_DIR.as_posix()}/{session_id}.json"
    branch_capsule = str(session.get("ion_branch_capsule") or "")
    branch_manifest_ref = f"{branch_capsule.rstrip('/')}/RAW_CONTEXT_MANIFEST.json" if branch_capsule else None
    return {
        "schema_id": "ion.codex_raw_context_manifest.v1",
        "generated_at": _now(),
        "session_id": session_id,
        "agent_tag": agent_tag,
        "branch_id": session.get("branch_id"),
        "packet_id": session.get("current_packet"),
        "domain": session.get("domain"),
        "storage_class": "local_private_gitignored",
        "private_raw_context_ref": _raw_context_private_ref(agent_tag, session_id),
        "central_manifest_ref": manifest_ref,
        "branch_manifest_ref": branch_manifest_ref,
        "snapshot_content_committed": False,
        "snapshot_mirrored_externally": False,
        "raw_content_exported": False,
        "raw_file_names_exported": False,
        "raw_config_values_exported": False,
        "redaction_status": "not_exported",
        "summary_refs": [],
        "diagnostic_excerpt_refs": [],
        "promotion_path": [
            "local_private_raw_context",
            "manifest",
            "redacted_excerpt_or_summary",
            "proof_gate",
            "receipt_or_settlement",
        ],
        "cockpit_visibility": "manifest_only",
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "raw_context_sync": {
            "policy_ref": RAW_CONTEXT_POLICY_PATH.as_posix(),
            "private_storage_ref": f"{PRIVATE_RAW_CONTEXT_DIR.as_posix()}/{_slug(agent_tag)}/{_slug(session_id)}/",
            "manifest_required": True,
            "raw_content_committed": False,
            "external_mirror_allowed": False,
            "accepted_state_authority": False,
        },
        "non_claims": [
            "Manifest does not prove raw content correctness.",
            "Manifest does not export raw Codex session or memory content.",
            "Raw context cannot become accepted state without proof gate and settlement.",
        ],
    }


def write_codex_raw_context_manifest(shell_root: Path, session: Mapping[str, Any]) -> list[str]:
    manifest = build_codex_raw_context_manifest(session)
    written: list[str] = []
    central = shell_root / RAW_CONTEXT_MANIFESTS_DIR / f"{manifest['session_id']}.json"
    _write_json(central, manifest)
    written.append(central.relative_to(shell_root).as_posix())
    branch_ref = manifest.get("branch_manifest_ref")
    if isinstance(branch_ref, str) and branch_ref:
        branch_manifest = shell_root / branch_ref
        _write_json(branch_manifest, manifest)
        written.append(branch_manifest.relative_to(shell_root).as_posix())
    return written


def _load_raw_context_manifests(shell_root: Path) -> list[dict[str, Any]]:
    path = shell_root / RAW_CONTEXT_MANIFESTS_DIR
    if not path.exists():
        return []
    manifests: list[dict[str, Any]] = []
    for item in sorted(path.glob("*.json")):
        payload = _read_json(item)
        if isinstance(payload, dict):
            payload.setdefault("path", item.relative_to(shell_root).as_posix())
            manifests.append(payload)
    return manifests


def _default_agent_registry_payload(shell_root: Path) -> dict[str, Any]:
    return {
        "schema_id": "ion.codex_agent_registry.v1",
        "generated_at": _now(),
        "path": AGENT_REGISTRY_PATH.as_posix(),
        "agent_count": len(DEFAULT_CODEX_AGENTS),
        "agents": DEFAULT_CODEX_AGENTS,
        "branch_capsule_required": True,
        "raw_context_manifest_required": True,
        "settlement_required": True,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def build_codex_agent_registry(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    payload = _read_json(shell_root / AGENT_REGISTRY_PATH)
    if isinstance(payload, dict):
        payload = dict(payload)
        payload["agent_count"] = len(payload.get("agents", [])) if isinstance(payload.get("agents"), list) else 0
        return payload
    return _default_agent_registry_payload(shell_root)


def write_codex_agent_registry(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    payload = _default_agent_registry_payload(shell_root)
    _write_json(shell_root / AGENT_REGISTRY_PATH, payload)
    return payload


def _event_files(shell_root: Path) -> list[Path]:
    path = shell_root / EVENTS_DIR
    if not path.exists():
        return []
    return sorted(p for p in path.glob("*.json") if p.is_file())


def _load_events(shell_root: Path, *, limit: int | None = None) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    files = _event_files(shell_root)
    if limit is not None:
        files = files[-limit:]
    for path in files:
        payload = _read_json(path)
        if isinstance(payload, dict):
            payload.setdefault("path", path.relative_to(shell_root).as_posix())
            events.append(payload)
    return events


def _default_event_ledger_payload(shell_root: Path) -> dict[str, Any]:
    events = _load_events(shell_root)
    return {
        "schema_id": "ion.codex_carrier_event_ledger.v1",
        "generated_at": _now(),
        "path": EVENT_LEDGER_PATH.as_posix(),
        "events_dir": EVENTS_DIR.as_posix(),
        "event_count": len(events),
        "recent_events": events[-25:],
        "event_schema_ref": RUNTIME_EVENT_SCHEMA_PATH.as_posix(),
        "event_types": sorted({str(event.get("event_type")) for event in events if event.get("event_type")}),
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def build_codex_carrier_event_ledger(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    payload = _read_json(shell_root / EVENT_LEDGER_PATH)
    current = _default_event_ledger_payload(shell_root)
    if isinstance(payload, dict):
        merged = dict(payload)
        merged.update({
            "generated_at": current["generated_at"],
            "event_count": current["event_count"],
            "recent_events": current["recent_events"],
            "event_types": current["event_types"],
        })
        return merged
    return current


def write_codex_carrier_event_ledger(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    (shell_root / EVENTS_DIR).mkdir(parents=True, exist_ok=True)
    payload = _default_event_ledger_payload(shell_root)
    _write_json(shell_root / EVENT_LEDGER_PATH, payload)
    return payload


def emit_codex_carrier_event(
    root: str | Path | None = None,
    *,
    event_type: str,
    actor: Mapping[str, Any] | None = None,
    packet_id: str | None = None,
    branch_id: str | None = None,
    session_id: str | None = None,
    refs: Sequence[str] = (),
    evidence: Sequence[str] = (),
    detail: str | None = None,
) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    (shell_root / EVENTS_DIR).mkdir(parents=True, exist_ok=True)
    base_id = f"evt_{_stamp()}_{_slug(event_type, 'event')}"
    event_id = base_id
    counter = 1
    while (shell_root / EVENTS_DIR / f"{event_id}.json").exists():
        counter += 1
        event_id = f"{base_id}_{counter}"
    payload = {
        "schema_id": "ion.codex_carrier_runtime_event.v1",
        "event_id": event_id,
        "created_at": _now(),
        "event_type": event_type,
        "actor": dict(actor or {}),
        "packet_id": packet_id,
        "branch_id": branch_id,
        "session_id": session_id,
        "refs": list(refs),
        "evidence": list(evidence),
        "detail": detail,
        "authority": {
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
        "visibility": {
            "cockpit": True,
            "public_safe": True,
            "redacted": True,
            "raw_context_exported": False,
        },
    }
    path = shell_root / EVENTS_DIR / f"{event_id}.json"
    _write_json(path, payload)
    payload["path"] = path.relative_to(shell_root).as_posix()
    write_codex_carrier_event_ledger(shell_root)
    return payload


def _last_local_pc_audit_summary(shell_root: Path) -> dict[str, Any]:
    payload = _read_json(shell_root / LOCAL_CODEX_PC_AUDIT_PATH)
    if not isinstance(payload, dict):
        return {
            "path": LOCAL_CODEX_PC_AUDIT_PATH.as_posix(),
            "exists": False,
            "status": "not_written",
            "raw_memory_or_session_content_exported": False,
            "raw_file_names_exported": False,
        }
    return {
        "path": LOCAL_CODEX_PC_AUDIT_PATH.as_posix(),
        "exists": True,
        "status": "written",
        "generated_at": payload.get("generated_at"),
        "verdict": payload.get("verdict"),
        "ok": payload.get("ok"),
        "codex_cli_available": payload.get("codex_cli", {}).get("available") if isinstance(payload.get("codex_cli"), dict) else None,
        "findings": list(payload.get("findings", []))[:20] if isinstance(payload.get("findings"), list) else [],
        "raw_memory_or_session_content_exported": False,
        "raw_file_names_exported": False,
    }


def build_codex_carrier_domain_registry(root: str | Path | None = None) -> dict[str, Any]:
    """Return the current Codex Carrier Domain registry projection.

    This is read-only. It does not inspect ``~/.codex`` memory/session contents.
    """
    shell_root = _resolve_shell_root(root)
    required = {name: _surface_status(shell_root, rel) for name, rel in REQUIRED_SURFACES.items()}
    generated = {name: _surface_status(shell_root, rel) for name, rel in CURRENT_CONTEXT_SURFACES.items()}
    missing_required = [f"missing_required_surface:{name}:{item['path']}" for name, item in required.items() if not item["exists"]]

    return {
        "schema_id": SCHEMA_ID,
        "registry_schema_id": "ion.codex_carrier_domain_registry.v1",
        "generated_at": _now(),
        "verdict": DOMAIN_READY_VERDICT if not missing_required else DOMAIN_BLOCKED_VERDICT,
        "ok": not missing_required,
        "shell_root": str(shell_root),
        "content_root": str(shell_root / "ION"),
        "carrier_domain_id": "CODEX_CARRIER_DOMAIN",
        "source_package": "ION_CODEX_CARRIER_OS_CONTEXT_PACKAGE_001",
        "active_packets": [
            "PCKT-ION-CODEX-CARRIER-DOMAIN-REGISTRY-002",
            "PCKT-ION-CODEX-SESSION-REGISTRY-003",
            "PCKT-ION-CODEX-CARRIER-COCKPIT-DATA-MODEL-010",
            "PCKT-ION-CODEX-RAW-CONTEXT-SYNC-LANE-001",
            "PCKT-ION-CODEX-CARRIER-EVENT-BUS-001",
            "PCKT-ION-CODEX-CARRIER-OS-SOURCE-MAP-001",
        ],
        "required_surfaces": required,
        "generated_surfaces": generated,
        "findings": missing_required,
        "agents": DEFAULT_CODEX_AGENTS,
        "memory_policy": DEFAULT_MEMORY_POLICY,
        "session_record_schema": {
            "schema_id": "ion.codex_carrier_session.v1",
            "required_fields": [
                "session_id",
                "agent_tag",
                "branch_id",
                "ion_branch_capsule",
                "current_packet",
                "write_scope",
                "settlement_required",
                "accepted_state_authority",
            ],
            "session_path_pattern": SESSIONS_DIR.as_posix() + "/<session_id>.json",
            "registry_path": SESSION_REGISTRY_PATH.as_posix(),
        },
        "branch_capsule_layout": [
            "CAPSULE.md",
            "MINI.md",
            "STATUS.json",
            "ROLLING_CONTEXT.md",
            "CODEX_SESSION.json",
            "RAW_CONTEXT_MANIFEST.json",
            "RECEIPTS/",
            "TASK_RETURNS/",
            "PATCHES/",
            "RAW_CONTEXT_SUMMARIES/",
            "RAW_CONTEXT_EXCERPTS/",
            "BLOCKERS.md",
        ],
        "mcp_read_only_tools": [
            "ion.codex.carrier.status",
            "ion.codex.carrier.cockpit",
            "ion.codex.carrier.events",
            "ion.codex.carrier.os",
            "ion.codex.raw_context.status",
        ],
        "cockpit_panels": [
            "project_and_carrier_overview",
            "agent_graph",
            "codex_session_manager",
            "context_truth_panel",
            "automation_timeline",
            "drift_and_consistency_dashboard",
            "git_and_settlement_board",
            "work_packet_board",
            "proof_console",
            "raw_codex_context_guarded_lane",
            "codex_carrier_os_source_map",
            "runtime_event_bus",
            "slash_command_registry",
            "context_mirror_policy",
            "service_and_port_map",
        ],
        "forbidden_claims": FORBIDDEN_CLAIMS,
        "local_codex_audit": _last_local_pc_audit_summary(shell_root),
        "local_codex_audit_policy": {
            "module": "ION/04_packages/kernel/ion_codex_local_pc_audit.py",
            "path": LOCAL_CODEX_PC_AUDIT_PATH.as_posix(),
            "write_confirmation": LOCAL_CODEX_PC_AUDIT_CONFIRMATION_TOKEN,
            "raw_memory_or_session_content_exported": False,
            "raw_file_names_exported": False,
            "raw_config_values_exported": False,
        },
        "raw_context_sync_lane": build_raw_context_sync_lane_status(shell_root),
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def _default_session_registry_payload(shell_root: Path) -> dict[str, Any]:
    sessions = _load_sessions(shell_root)
    return {
        "schema_id": "ion.codex_session_registry.v1",
        "generated_at": _now(),
        "path": SESSION_REGISTRY_PATH.as_posix(),
        "sessions_dir": SESSIONS_DIR.as_posix(),
        "session_count": len(sessions),
        "active_session_count": sum(1 for item in sessions if item.get("status") == "ACTIVE"),
        "sessions": sessions,
        "memory_policy_ref": MEMORY_POLICY_PATH.as_posix(),
        "raw_context_policy_ref": RAW_CONTEXT_POLICY_PATH.as_posix(),
        "raw_context_manifest_count": len(_load_raw_context_manifests(shell_root)),
        "raw_context_manifests": _load_raw_context_manifests(shell_root),
        "event_ledger_ref": EVENT_LEDGER_PATH.as_posix(),
        "branch_registry_ref": "ION/05_context/current/agent_context_branches/BRANCH_CAPSULE_REGISTRY_V0_1.json",
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def write_codex_session_registry(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    payload = _default_session_registry_payload(shell_root)
    _write_json(shell_root / SESSION_REGISTRY_PATH, payload)
    return payload


def _readme_text() -> str:
    return "\n".join([
        "# Codex Carrier Domain",
        "",
        "Status: active candidate operating lane; not accepted state by itself.",
        "",
        "This folder holds the repo-local control-plane surfaces for making Codex CLI/App a first-class ION carrier domain.",
        "",
        "Core rule:",
        "",
        "```text",
        "Codex memory/session = working continuity.",
        "Raw Codex context = bounded diagnostic continuity.",
        "ION branch capsule = durable governed continuity.",
        "ION settlement = accepted inheritance.",
        "```",
        "",
        "Generated/maintained surfaces:",
        "",
        f"- `{DOMAIN_REGISTRY_PATH.as_posix()}`",
        f"- `{AGENT_REGISTRY_PATH.as_posix()}`",
        f"- `{SESSION_REGISTRY_PATH.as_posix()}`",
        f"- `{SESSIONS_DIR.as_posix()}/`",
        f"- `{MEMORY_POLICY_PATH.as_posix()}`",
        f"- `{ROLLING_CONTEXT_TEMPLATE_PATH.as_posix()}`",
        f"- `{COCKPIT_SNAPSHOT_PATH.as_posix()}`",
        f"- `{EVENT_LEDGER_PATH.as_posix()}`",
        f"- `{EVENTS_DIR.as_posix()}/`",
        f"- `{LOCAL_CODEX_PC_AUDIT_PATH.as_posix()}`",
        f"- `{RAW_CONTEXT_POLICY_PATH.as_posix()}`",
        "- `ION/05_context/current/codex_carrier/raw_context_manifests/`",
        "",
        "Session records are candidate carrier state. They do not grant production authority, live execution authority, or accepted-state authority.",
    ]) + "\n"


def _memory_policy_text() -> str:
    return "\n".join([
        "# Codex Carrier Memory Policy",
        "",
        "Status: active policy for the Codex carrier domain.",
        "",
        "Codex memories and raw context may orient and diagnose local work. They are not accepted ION state.",
        "",
        "Rules:",
        "",
        "- Do not export or print raw `~/.codex` memory/session contents without explicit review.",
        "- Preserve raw context value through local-private snapshots and public-safe manifests, not raw commits.",
        "- Memory summaries may be cited as orientation only.",
        "- Diagnostic excerpts must be redacted, packet-bound, and proof-gated before settlement.",
        "- Durable claims require branch capsule, receipt, proof, or settlement evidence.",
        "- Secret-like content is path/type only unless the operator explicitly authorizes a redacted audit.",
        "- Branch capsule governs current work; settlement governs accepted inheritance.",
        "",
        "Authority:",
        "",
        "```json",
        json.dumps(DEFAULT_MEMORY_POLICY, indent=2, sort_keys=True),
        "```",
    ]) + "\n"


def _rolling_context_template_text() -> str:
    return "\n".join([
        "# Codex Carrier Rolling Context",
        "",
        "session_id: `<session_id>`",
        "agent_tag: `<agent_tag>`",
        "branch_id: `<branch_id>`",
        "current_packet: `<packet_id>`",
        "settlement_required: true",
        "accepted_state_authority: false",
        "production_authority: false",
        "live_execution_authority: false",
        "",
        "## Current Work",
        "",
        "- Objective:",
        "- Write scope:",
        "- Loaded refs:",
        "- Open blockers:",
        "",
        "## Raw Codex Context Lane",
        "",
        "- Private snapshot manifest:",
        "- Raw content committed: false",
        "- External mirror: false",
        "- Redaction status:",
        "- Diagnostic excerpt refs:",
        "- Promotion state:",
        "",
        "## Proof Ledger",
        "",
        "| Time | Command / Gate | Result | Evidence |",
        "|---|---|---|---|",
        "",
        "## Handoff",
        "",
        "- Last diff:",
        "- Last receipt:",
        "- Next lawful action:",
    ]) + "\n"


def write_codex_carrier_domain_registry(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    payload = build_codex_carrier_domain_registry(shell_root)
    _write_json(shell_root / DOMAIN_REGISTRY_PATH, payload)
    return payload


def initialize_codex_carrier_domain(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    (shell_root / SESSIONS_DIR).mkdir(parents=True, exist_ok=True)
    (shell_root / EVENTS_DIR).mkdir(parents=True, exist_ok=True)
    initialize_raw_context_sync_lane(shell_root)
    (shell_root / README_PATH).write_text(_readme_text(), encoding="utf-8")
    (shell_root / MEMORY_POLICY_PATH).write_text(_memory_policy_text(), encoding="utf-8")
    (shell_root / ROLLING_CONTEXT_TEMPLATE_PATH).write_text(_rolling_context_template_text(), encoding="utf-8")
    agent_registry = write_codex_agent_registry(shell_root)
    event_ledger = write_codex_carrier_event_ledger(shell_root)
    registry = write_codex_carrier_domain_registry(shell_root)
    session_registry = write_codex_session_registry(shell_root)
    cockpit = write_codex_carrier_cockpit_snapshot(shell_root)
    return {
        "schema_id": "ion.codex_carrier_domain_initialization.v1",
        "generated_at": _now(),
        "verdict": registry["verdict"],
        "ok": bool(registry.get("ok")),
        "written_paths": [
            README_PATH.as_posix(),
            MEMORY_POLICY_PATH.as_posix(),
            ROLLING_CONTEXT_TEMPLATE_PATH.as_posix(),
            RAW_CONTEXT_POLICY_PATH.as_posix(),
            "ION/05_context/current/codex_carrier/raw_context_manifests/README.md",
            AGENT_REGISTRY_PATH.as_posix(),
            EVENT_LEDGER_PATH.as_posix(),
            DOMAIN_REGISTRY_PATH.as_posix(),
            SESSION_REGISTRY_PATH.as_posix(),
            COCKPIT_SNAPSHOT_PATH.as_posix(),
        ],
        "agent_registry": {
            "path": AGENT_REGISTRY_PATH.as_posix(),
            "agent_count": agent_registry.get("agent_count", 0),
        },
        "session_registry": {
            "path": SESSION_REGISTRY_PATH.as_posix(),
            "session_count": session_registry.get("session_count", 0),
        },
        "event_ledger": {
            "path": EVENT_LEDGER_PATH.as_posix(),
            "event_count": event_ledger.get("event_count", 0),
        },
        "cockpit_snapshot": {
            "path": COCKPIT_SNAPSHOT_PATH.as_posix(),
            "drift_signal_count": len(cockpit.get("drift_signals", [])),
        },
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def _branch_capsule_text(session: Mapping[str, Any]) -> str:
    return "\n".join([
        "# Codex Carrier Branch Capsule",
        "",
        "Status: candidate branch capsule; not accepted state by itself.",
        "",
        f"session_id: `{session['session_id']}`",
        f"agent_tag: `{session['agent_tag']}`",
        f"branch_id: `{session['branch_id']}`",
        f"current_packet: `{session['current_packet']}`",
        "accepted_state_authority: false",
        "production_authority: false",
        "live_execution_authority: false",
        "",
        "## Purpose",
        "",
        "Bind one local Codex carrier session to a durable ION branch-capsule surface.",
        "",
        "## Boundary",
        "",
        "Codex session and memory may orient work. Branch capsule, proof, receipts, and settlement govern durable inheritance.",
        "",
        "## Write Scope",
        "",
        *[f"- `{scope}`" for scope in session.get("write_scope", [])],
        "",
        "## Required Settlement",
        "",
        "Any material output from this branch remains proposal until proof gates and Steward/operator settlement accept it.",
    ]) + "\n"


def _branch_mini_text(session: Mapping[str, Any]) -> str:
    return "\n".join([
        f"# {session['agent_tag']} Mini Context",
        "",
        f"- Session: `{session['session_id']}`",
        f"- Branch: `{session['branch_id']}`",
        f"- Packet: `{session['current_packet']}`",
        "- Authority: candidate carrier state only; no production/live/accepted-state authority.",
        "- Next: record visible work, proof commands, diffs, blockers, and settlement requests here or in sibling folders.",
    ]) + "\n"


def _branch_blockers_text(session: Mapping[str, Any]) -> str:
    return "\n".join([
        "# Blockers",
        "",
        f"session_id: `{session['session_id']}`",
        "",
        "No blockers recorded at capsule initialization.",
    ]) + "\n"


def _branch_rolling_context_text(session: Mapping[str, Any]) -> str:
    return "\n".join([
        "# Codex Carrier Rolling Context",
        "",
        f"session_id: `{session['session_id']}`",
        f"agent_tag: `{session['agent_tag']}`",
        f"branch_id: `{session['branch_id']}`",
        f"current_packet: `{session['current_packet']}`",
        "settlement_required: true",
        "accepted_state_authority: false",
        "production_authority: false",
        "live_execution_authority: false",
        "",
        "## Current Work",
        "",
        f"- Objective: {session.get('session_label') or 'unrecorded'}",
        "- Write scope:",
        *[f"  - `{scope}`" for scope in session.get("write_scope", [])],
        "- Loaded refs:",
        *[f"  - `{ref}`" for ref in session.get("loaded_refs", [])],
        "- Open blockers: none recorded at initialization",
        "",
        "## Raw Codex Context Lane",
        "",
        "- Private snapshot manifest: not registered",
        "- Raw content committed: false",
        "- External mirror: false",
        "- Redaction status: not_exported",
        "- Diagnostic excerpt refs: none",
        "- Promotion state: not_promoted",
        "",
        "## Proof Ledger",
        "",
        "| Time | Command / Gate | Result | Evidence |",
        "|---|---|---|---|",
        "",
        "## Handoff",
        "",
        "- Last diff:",
        "- Last receipt:",
        "- Next lawful action:",
    ]) + "\n"


def _branch_status_payload(session: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "ion.codex_carrier_branch_status.v1",
        "generated_at": _now(),
        "status": session.get("status", "ACTIVE"),
        "session_id": session["session_id"],
        "agent_tag": session["agent_tag"],
        "branch_id": session["branch_id"],
        "current_packet": session["current_packet"],
        "write_scope": list(session.get("write_scope", [])),
        "session_record_ref": f"{SESSIONS_DIR.as_posix()}/{session['session_id']}.json",
        "settlement_required": True,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def write_codex_branch_capsule(shell_root: Path, session: Mapping[str, Any]) -> list[str]:
    """Create the durable candidate branch capsule for a Codex session."""
    capsule_rel = Path(str(session["ion_branch_capsule"]))
    capsule_root = shell_root / capsule_rel
    if not str(capsule_rel).startswith(CODEX_BRANCH_CAPSULE_BASE.as_posix() + "/"):
        raise ValueError("Codex branch capsule path must stay under the Codex branch-capsule base")
    for directory in ("RECEIPTS", "TASK_RETURNS", "PATCHES", "RAW_CONTEXT_SUMMARIES", "RAW_CONTEXT_EXCERPTS"):
        (capsule_root / directory).mkdir(parents=True, exist_ok=True)
    writes: dict[str, str] = {
        "CAPSULE.md": _branch_capsule_text(session),
        "MINI.md": _branch_mini_text(session),
        "ROLLING_CONTEXT.md": _branch_rolling_context_text(session),
        "BLOCKERS.md": _branch_blockers_text(session),
    }
    written: list[str] = []
    for name, value in writes.items():
        target = capsule_root / name
        target.write_text(value, encoding="utf-8")
        written.append(target.relative_to(shell_root).as_posix())
    session_copy = dict(session)
    _write_json(capsule_root / "CODEX_SESSION.json", session_copy)
    _write_json(capsule_root / "STATUS.json", _branch_status_payload(session))
    written.extend([
        (capsule_root / "CODEX_SESSION.json").relative_to(shell_root).as_posix(),
        (capsule_root / "STATUS.json").relative_to(shell_root).as_posix(),
    ])
    written.extend((capsule_root / directory).relative_to(shell_root).as_posix() + "/" for directory in ("RECEIPTS", "TASK_RETURNS", "PATCHES", "RAW_CONTEXT_SUMMARIES", "RAW_CONTEXT_EXCERPTS"))
    return written


def register_codex_carrier_session(
    root: str | Path | None = None,
    *,
    agent_tag: str,
    current_packet: str,
    session_label: str | None = None,
    codex_thread_ref: str | None = None,
    model_lane: str = "codex_cli_local",
    write_scope: Sequence[str] = (),
    status: str = "ACTIVE",
) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    agent = _agent_by_tag(agent_tag)
    if agent is None:
        raise ValueError(f"unknown Codex carrier agent_tag: {agent_tag}")
    stamp = _stamp()
    session_id = f"codex_session_{stamp}_{_slug(agent_tag)}"
    branch_id = f"branch_{stamp}_{_slug(agent_tag)}"
    label = session_label or agent["role_hint"]
    scope = list(write_scope) if write_scope else list(agent.get("default_write_scope", []))
    branch_capsule = f"{CODEX_BRANCH_CAPSULE_BASE.as_posix()}/{_slug(agent_tag)}/{branch_id}/"
    payload = {
        "schema_id": "ion.codex_carrier_session.v1",
        "session_id": session_id,
        "created_at": _now(),
        "updated_at": _now(),
        "status": status,
        "agent_tag": agent_tag,
        "domain": agent["domain"],
        "session_label": label,
        "codex_thread_ref": codex_thread_ref,
        "model_lane": model_lane,
        "repo_root": str(shell_root),
        "branch_id": branch_id,
        "ion_branch_capsule": branch_capsule,
        "current_packet": current_packet,
        "memory_policy": DEFAULT_MEMORY_POLICY,
        "write_scope": scope,
        "loaded_refs": [
            "ION/REPO_AUTHORITY.md",
            "ION/02_architecture/ION_MOUNT_CONTRACT.md",
            "ION/02_architecture/CODEX_CARRIER_DOMAIN_PROTOCOL.md",
            "ION/05_context/current/codex_carrier/CODEX_CARRIER_DOMAIN_REGISTRY.json",
        ],
        "settlement_required": True,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "raw_context_sync": {
            "policy_ref": RAW_CONTEXT_POLICY_PATH.as_posix(),
            "private_storage_ref": f"{PRIVATE_RAW_CONTEXT_DIR.as_posix()}/{_slug(agent_tag)}/{_slug(session_id)}/",
            "manifest_required": True,
            "raw_content_committed": False,
            "external_mirror_allowed": False,
            "accepted_state_authority": False,
        },
        "non_claims": [
            "Session record does not prove a live Codex thread exists unless codex_thread_ref is locally verified.",
            "Session record does not accept state or settle branch output.",
            "Session record does not grant production, live execution, or secrets authority.",
        ],
    }
    path = shell_root / SESSIONS_DIR / f"{session_id}.json"
    branch_capsule_paths = write_codex_branch_capsule(shell_root, payload)
    raw_manifest = create_raw_context_manifest(
        shell_root,
        agent_tag=agent_tag,
        session_id=session_id,
        branch_id=branch_id,
        packet_id=current_packet,
        snapshot_label=f"{label} raw Codex context diagnostic lane",
        branch_capsule=branch_capsule,
    )
    payload["raw_context_manifest_ref"] = raw_manifest.get("path")
    payload["raw_context_manifest"] = {
        "manifest_id": raw_manifest.get("manifest_id"),
        "path": raw_manifest.get("path"),
        "branch_capsule_manifest_ref": raw_manifest.get("branch_capsule_manifest_ref"),
        "snapshot_content_committed": raw_manifest.get("snapshot_content_committed", False),
        "snapshot_mirrored_externally": raw_manifest.get("snapshot_mirrored_externally", False),
        "promotion_state": raw_manifest.get("promotion_state"),
    }
    branch_capsule_paths.extend([
        str(raw_manifest.get("path")),
        str(raw_manifest.get("branch_capsule_manifest_ref")),
    ])
    payload["branch_capsule_written_paths"] = [item for item in branch_capsule_paths if item and item != "None"]
    payload["path"] = path.relative_to(shell_root).as_posix()
    event_refs = []
    session_event = emit_codex_carrier_event(
        shell_root,
        event_type="codex.session.registered",
        actor={"carrier": "codex_cli", "agent_tag": agent_tag, "session_id": session_id},
        packet_id=current_packet,
        branch_id=branch_id,
        session_id=session_id,
        refs=[payload["path"], branch_capsule, str(raw_manifest.get("path"))],
        evidence=payload["branch_capsule_written_paths"],
        detail="Codex carrier session registered with branch capsule and raw-context manifest lane.",
    )
    event_refs.append(session_event.get("path"))
    raw_event = emit_codex_carrier_event(
        shell_root,
        event_type="codex.raw_context.manifested",
        actor={"carrier": "codex_cli", "agent_tag": agent_tag, "session_id": session_id},
        packet_id=current_packet,
        branch_id=branch_id,
        session_id=session_id,
        refs=[str(raw_manifest.get("path")), str(raw_manifest.get("branch_capsule_manifest_ref"))],
        evidence=[str(raw_manifest.get("path"))],
        detail="Public-safe raw Codex context manifest written; raw content remains local-private and unexported.",
    )
    event_refs.append(raw_event.get("path"))
    payload["event_refs"] = [ref for ref in event_refs if ref]
    _write_json(path, payload)
    branch_session_path = shell_root / Path(branch_capsule) / "CODEX_SESSION.json"
    _write_json(branch_session_path, payload)
    write_codex_session_registry(shell_root)
    write_codex_carrier_event_ledger(shell_root)
    write_codex_carrier_cockpit_snapshot(shell_root)
    return payload


def build_codex_session_registry(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    path = shell_root / SESSION_REGISTRY_PATH
    payload = _read_json(path)
    if isinstance(payload, dict):
        sessions = _load_sessions(shell_root)
        payload = dict(payload)
        payload["session_count"] = len(sessions)
        payload["active_session_count"] = sum(1 for item in sessions if item.get("status") == "ACTIVE")
        payload["sessions"] = sessions
        payload["raw_context_manifest_count"] = len(_load_raw_context_manifests(shell_root))
        payload["raw_context_manifests"] = _load_raw_context_manifests(shell_root)
        payload["event_ledger_ref"] = EVENT_LEDGER_PATH.as_posix()
        return payload
    return _default_session_registry_payload(shell_root)


def _drift_signals(shell_root: Path, domain: Mapping[str, Any], session_registry: Mapping[str, Any], git: Mapping[str, Any]) -> list[dict[str, Any]]:
    signals: list[dict[str, Any]] = []
    if not domain.get("ok"):
        signals.append({
            "signal_id": "codex_domain_required_surface_missing",
            "status": "BLOCKED",
            "reason": "one or more required Codex carrier domain surfaces are missing",
            "findings": list(domain.get("findings", [])),
        })
    if not (shell_root / DOMAIN_REGISTRY_PATH).exists():
        signals.append({
            "signal_id": "codex_domain_registry_not_written",
            "status": "CANDIDATE",
            "reason": "registry projection exists in code but current-context registry file has not been initialized",
        })
    if not (shell_root / SESSION_REGISTRY_PATH).exists():
        signals.append({
            "signal_id": "codex_session_registry_not_written",
            "status": "CANDIDATE",
            "reason": "session registry has not been initialized",
        })
    if not (shell_root / EVENT_LEDGER_PATH).exists():
        signals.append({
            "signal_id": "codex_carrier_event_ledger_not_written",
            "status": "CANDIDATE",
            "reason": "Codex carrier event ledger has not been initialized",
        })
    last_audit = _last_local_pc_audit_summary(shell_root)
    if not last_audit.get("exists"):
        signals.append({
            "signal_id": "codex_local_pc_audit_not_written",
            "status": "CANDIDATE",
            "reason": "sanitized local ~/.codex and Codex CLI audit has not been written yet",
            "path": LOCAL_CODEX_PC_AUDIT_PATH.as_posix(),
        })
    elif last_audit.get("codex_cli_available") is False:
        signals.append({
            "signal_id": "codex_cli_not_available_in_last_local_audit",
            "status": "BLOCKED",
            "reason": "last sanitized local audit did not find Codex CLI on PATH",
            "path": LOCAL_CODEX_PC_AUDIT_PATH.as_posix(),
        })
    if int(session_registry.get("session_count", 0) or 0) == 0:
        signals.append({
            "signal_id": "no_codex_sessions_registered",
            "status": "READY",
            "reason": "no active Codex sessions are registered yet; register only after a real local Codex lane is mounted",
        })
    if git.get("available") and git.get("dirty"):
        signals.append({
            "signal_id": "git_worktree_dirty",
            "status": "DRIFTED",
            "reason": "working tree has tracked or untracked changes that need classification before settlement",
            "porcelain_count": git.get("porcelain_count"),
            "sample": git.get("porcelain_sample", []),
        })
    raw_context = build_raw_context_sync_lane_status(shell_root)
    if not raw_context.get("ok"):
        signals.append({
            "signal_id": "codex_raw_context_sync_lane_not_ready",
            "status": "CANDIDATE",
            "reason": "raw Codex context diagnostic lane requires protocol, policy, and gitignore guard before use",
            "findings": list(raw_context.get("findings", [])),
        })
    signals.append({
        "signal_id": "codex_memory_boundary",
        "status": "READY",
        "reason": "Codex memory/raw context are bounded diagnostic continuity only; branch capsules and receipts govern durable state",
    })
    signals.append({
        "signal_id": "shared_context_write_boundary",
        "status": "READY",
        "reason": "Codex carrier sessions must not directly mutate shared Capsule/Mini/HOT_CONTEXT; settlement required",
    })
    return signals


def build_codex_carrier_cockpit_snapshot(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    domain = build_codex_carrier_domain_registry(shell_root)
    session_registry = build_codex_session_registry(shell_root)
    sessions = list(session_registry.get("sessions", [])) if isinstance(session_registry.get("sessions"), list) else []
    git = _git_state(shell_root)
    event_ledger = build_codex_carrier_event_ledger(shell_root)
    agent_registry = build_codex_agent_registry(shell_root)
    raw_context_lane = build_raw_context_sync_lane_status(shell_root)

    nodes: list[dict[str, Any]] = [
        {"id": "CODEX_CARRIER_DOMAIN", "kind": "carrier_domain", "status": domain.get("verdict")},
        {"id": "codex_solo_base_context", "kind": "shared_context", "path": "ION/05_context/current/codex_solo/"},
        {"id": "branch_capsule_registry", "kind": "branch_registry", "path": "ION/05_context/current/agent_context_branches/BRANCH_CAPSULE_REGISTRY_V0_1.json"},
        {"id": "mcp_local_bridge", "kind": "mcp_bridge", "path": "ION/04_packages/kernel/ion_mcp_local_bridge.py"},
        {"id": "codex_raw_context_sync_lane", "kind": "guarded_diagnostic_lane", "path": RAW_CONTEXT_POLICY_PATH.as_posix()},
        {"id": "codex_carrier_event_bus", "kind": "runtime_event_bus", "path": EVENT_LEDGER_PATH.as_posix()},
        {"id": "codex_agent_registry", "kind": "agent_registry", "path": AGENT_REGISTRY_PATH.as_posix()},
    ]
    for agent in DEFAULT_CODEX_AGENTS:
        nodes.append({"id": agent["agent_tag"], "kind": "codex_agent", "domain": agent["domain"]})
    for session in sessions:
        nodes.append({
            "id": session.get("session_id"),
            "kind": "codex_session",
            "agent_tag": session.get("agent_tag"),
            "status": session.get("status"),
            "current_packet": session.get("current_packet"),
            "path": session.get("path"),
        })

    edges: list[dict[str, Any]] = [
        {"from": "CODEX_CARRIER_DOMAIN", "to": "codex_raw_context_sync_lane", "kind": "defines_guarded_diagnostic_lane"},
        {"from": "CODEX_CARRIER_DOMAIN", "to": "codex_carrier_event_bus", "kind": "emits_runtime_events"},
        {"from": "CODEX_CARRIER_DOMAIN", "to": "codex_agent_registry", "kind": "defines_agent_registry"},
    ]
    for agent in DEFAULT_CODEX_AGENTS:
        edges.append({"from": "CODEX_CARRIER_DOMAIN", "to": agent["agent_tag"], "kind": "defines_agent"})
        edges.append({"from": agent["agent_tag"], "to": "branch_capsule_registry", "kind": "requires_branch_capsule"})
    for session in sessions:
        edges.append({"from": session.get("agent_tag"), "to": session.get("session_id"), "kind": "owns_session"})
        if session.get("ion_branch_capsule"):
            edges.append({"from": session.get("session_id"), "to": session.get("ion_branch_capsule"), "kind": "binds_branch_capsule"})
        if session.get("raw_context_manifest_ref"):
            edges.append({"from": session.get("session_id"), "to": session.get("raw_context_manifest_ref"), "kind": "has_raw_context_manifest"})

    payload = {
        "schema_id": "ion.codex_carrier_cockpit_snapshot.v1",
        "generated_at": _now(),
        "path": COCKPIT_SNAPSHOT_PATH.as_posix(),
        "project": {
            "shell_root": str(shell_root),
            "content_root": str(shell_root / "ION"),
            "git": git,
            "domain_verdict": domain.get("verdict"),
        },
        "domain_registry": {
            "path": DOMAIN_REGISTRY_PATH.as_posix(),
            "verdict": domain.get("verdict"),
            "agent_count": len(DEFAULT_CODEX_AGENTS),
            "mcp_read_only_tools": domain.get("mcp_read_only_tools", []),
        },
        "agent_registry": {
            "path": AGENT_REGISTRY_PATH.as_posix(),
            "agent_count": agent_registry.get("agent_count", 0),
            "agents": agent_registry.get("agents", []),
        },
        "session_registry": {
            "path": SESSION_REGISTRY_PATH.as_posix(),
            "session_count": session_registry.get("session_count", 0),
            "active_session_count": session_registry.get("active_session_count", 0),
            "sessions": sessions,
        },
        "agent_graph": {"nodes": nodes, "edges": edges},
        "context_truth_panel": {
            "memory_policy_ref": MEMORY_POLICY_PATH.as_posix(),
            "raw_context_policy_ref": RAW_CONTEXT_POLICY_PATH.as_posix(),
            "accepted_state_boundary": "Codex sessions, memories, and raw context are proposal/orientation/diagnostic continuity until proof gates and settlement accept receipts.",
            "shared_context_write_allowed": False,
            "raw_context_committed_by_default": False,
            "raw_context_mirrored_externally_by_default": False,
        },
        "raw_context_sync_lane": raw_context_lane,
        "event_ledger": event_ledger,
        "automation_timeline": event_ledger.get("recent_events", []),
        "service_port_map": DEFAULT_SERVICE_PORTS,
        "local_pc_audit": _last_local_pc_audit_summary(shell_root),
        "drift_signals": _drift_signals(shell_root, domain, session_registry, git),
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }
    return payload


def write_codex_carrier_cockpit_snapshot(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    payload = build_codex_carrier_cockpit_snapshot(shell_root)
    _write_json(shell_root / COCKPIT_SNAPSHOT_PATH, payload)
    return payload


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _require_confirmation(value: str | None) -> bool:
    return value == WRITE_CONFIRMATION_TOKEN


def _add_common_root_argument(command_parser: argparse.ArgumentParser) -> None:
    # Keep command examples ergonomic: both `--ion-root . status` and
    # `status --ion-root .` are accepted. Subcommand defaults are suppressed so
    # they do not overwrite the global value when omitted.
    command_parser.add_argument("--ion-root", default=argparse.SUPPRESS, help="Shell root or ION content root")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage ION Codex Carrier Domain surfaces.")
    parser.add_argument("--ion-root", default=".", help="Shell root or ION content root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="Read-only Codex carrier domain status")
    _add_common_root_argument(status)
    status.add_argument("--json", action="store_true")

    init = subparsers.add_parser("init", help="Initialize current Codex carrier domain surfaces")
    _add_common_root_argument(init)
    init.add_argument("--confirmation", required=True, help=f"Required token: {WRITE_CONFIRMATION_TOKEN}")
    init.add_argument("--json", action="store_true")

    sessions = subparsers.add_parser("sessions", help="Read-only Codex session registry projection")
    _add_common_root_argument(sessions)
    sessions.add_argument("--json", action="store_true")

    register = subparsers.add_parser("register-session", help="Register a real local Codex carrier session")
    _add_common_root_argument(register)
    register.add_argument("--agent-tag", required=True)
    register.add_argument("--current-packet", required=True)
    register.add_argument("--session-label", default=None)
    register.add_argument("--codex-thread-ref", default=None)
    register.add_argument("--model-lane", default="codex_cli_local")
    register.add_argument("--write-scope", action="append", default=[])
    register.add_argument("--confirmation", required=True, help=f"Required token: {WRITE_CONFIRMATION_TOKEN}")
    register.add_argument("--json", action="store_true")

    local_audit = subparsers.add_parser("local-audit", help="Sanitized local Codex PC audit; no raw memory/session export")
    _add_common_root_argument(local_audit)
    local_audit.add_argument("--codex-home", default=None)
    local_audit.add_argument("--codex-bin", default="codex")
    local_audit.add_argument("--no-help-probe", action="store_true")
    local_audit.add_argument("--write", action="store_true")
    local_audit.add_argument("--confirmation", default=None, help=f"Required with --write: {LOCAL_CODEX_PC_AUDIT_CONFIRMATION_TOKEN}")
    local_audit.add_argument("--json", action="store_true")

    events = subparsers.add_parser("events", help="Read-only Codex carrier event ledger projection")
    _add_common_root_argument(events)
    events.add_argument("--json", action="store_true")

    cockpit = subparsers.add_parser("cockpit", help="Read-only Codex cockpit data snapshot")
    _add_common_root_argument(cockpit)
    cockpit.add_argument("--write", action="store_true")
    cockpit.add_argument("--confirmation", default=None, help=f"Required with --write: {WRITE_CONFIRMATION_TOKEN}")
    cockpit.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "status":
            payload = build_codex_carrier_domain_registry(args.ion_root)
            if args.json:
                _print_json(payload)
            else:
                print(payload["verdict"])
                for finding in payload.get("findings", []):
                    print(f"- {finding}")
            return 0 if payload.get("ok") else 2

        if args.command == "init":
            if not _require_confirmation(args.confirmation):
                payload = {
                    "ok": False,
                    "schema_id": "ion.codex_carrier_domain_write_refusal.v1",
                    "refusal_class": "CONFIRMATION_REQUIRED",
                    "required_confirmation": WRITE_CONFIRMATION_TOKEN,
                    "production_authority": False,
                    "live_execution_authority": False,
                }
                if args.json:
                    _print_json(payload)
                else:
                    print(f"Refused: confirmation must be {WRITE_CONFIRMATION_TOKEN}", file=sys.stderr)
                return 3
            payload = initialize_codex_carrier_domain(args.ion_root)
            if args.json:
                _print_json(payload)
            else:
                print(payload["verdict"])
            return 0 if payload.get("ok") else 2

        if args.command == "sessions":
            payload = build_codex_session_registry(args.ion_root)
            if args.json:
                _print_json(payload)
            else:
                print(f"sessions={payload.get('session_count', 0)} active={payload.get('active_session_count', 0)}")
            return 0

        if args.command == "register-session":
            if not _require_confirmation(args.confirmation):
                payload = {
                    "ok": False,
                    "schema_id": "ion.codex_carrier_session_write_refusal.v1",
                    "refusal_class": "CONFIRMATION_REQUIRED",
                    "required_confirmation": WRITE_CONFIRMATION_TOKEN,
                    "production_authority": False,
                    "live_execution_authority": False,
                }
                if args.json:
                    _print_json(payload)
                else:
                    print(f"Refused: confirmation must be {WRITE_CONFIRMATION_TOKEN}", file=sys.stderr)
                return 3
            payload = register_codex_carrier_session(
                args.ion_root,
                agent_tag=args.agent_tag,
                current_packet=args.current_packet,
                session_label=args.session_label,
                codex_thread_ref=args.codex_thread_ref,
                model_lane=args.model_lane,
                write_scope=args.write_scope,
            )
            payload["ok"] = True
            if args.json:
                _print_json(payload)
            else:
                print(f"{payload['session_id']} {payload['path']}")
            return 0

        if args.command == "local-audit":
            if args.write:
                if args.confirmation != LOCAL_CODEX_PC_AUDIT_CONFIRMATION_TOKEN:
                    payload = {
                        "ok": False,
                        "schema_id": "ion.codex_local_pc_audit_write_refusal.v1",
                        "refusal_class": "CONFIRMATION_REQUIRED",
                        "required_confirmation": LOCAL_CODEX_PC_AUDIT_CONFIRMATION_TOKEN,
                        "production_authority": False,
                        "live_execution_authority": False,
                        "secrets_authority": False,
                    }
                    if args.json:
                        _print_json(payload)
                    else:
                        print(f"Refused: confirmation must be {LOCAL_CODEX_PC_AUDIT_CONFIRMATION_TOKEN}", file=sys.stderr)
                    return 3
                payload = write_codex_local_pc_audit(
                    args.ion_root,
                    codex_home=args.codex_home,
                    codex_bin=args.codex_bin,
                    run_help=not args.no_help_probe,
                )
            else:
                payload = build_codex_local_pc_audit(
                    args.ion_root,
                    codex_home=args.codex_home,
                    codex_bin=args.codex_bin,
                    run_help=not args.no_help_probe,
                )
            if args.json:
                _print_json(payload)
            else:
                print(payload["verdict"])
                for finding in payload.get("findings", []):
                    print(f"- {finding}")
            return 0 if payload.get("ok") else 2

        if args.command == "events":
            payload = build_codex_carrier_event_ledger(args.ion_root)
            if args.json:
                _print_json(payload)
            else:
                print(f"events={payload.get('event_count', 0)} types={','.join(payload.get('event_types', []))}")
            return 0

        if args.command == "cockpit":
            if args.write:
                if not _require_confirmation(args.confirmation):
                    payload = {
                        "ok": False,
                        "schema_id": "ion.codex_carrier_cockpit_write_refusal.v1",
                        "refusal_class": "CONFIRMATION_REQUIRED",
                        "required_confirmation": WRITE_CONFIRMATION_TOKEN,
                        "production_authority": False,
                        "live_execution_authority": False,
                    }
                    if args.json:
                        _print_json(payload)
                    else:
                        print(f"Refused: confirmation must be {WRITE_CONFIRMATION_TOKEN}", file=sys.stderr)
                    return 3
                payload = write_codex_carrier_cockpit_snapshot(args.ion_root)
            else:
                payload = build_codex_carrier_cockpit_snapshot(args.ion_root)
            if args.json:
                _print_json(payload)
            else:
                print(f"domain={payload['domain_registry']['verdict']} sessions={payload['session_registry']['session_count']}")
            return 0
    except Exception as exc:
        payload = {
            "ok": False,
            "schema_id": "ion.codex_carrier_domain_cli_error.v1",
            "error": str(exc),
            "production_authority": False,
            "live_execution_authority": False,
        }
        if getattr(args, "json", False):
            _print_json(payload)
        else:
            print(json.dumps(payload, indent=2, sort_keys=True), file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
