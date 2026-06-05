"""Unified ION agent/domain control-plane projection.

This module does not create a second agent system. It projects the existing
Agent Context Systems, Domain Weave candidate maps, invocation broker, and Codex
queue runner into one cockpit model.
"""
from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_agent_context_system_audit import audit_agent_context_systems
from .ion_agent_context_systems import runtime_context_system_summary
from .ion_agent_invocation_broker import (
    agent_queue,
    build_agent_broker_status,
    list_agents,
    pending_agent_relays,
    recent_agent_invocation_receipts,
)
from .ion_agent_comms import build_agent_comms_projection
from .ion_agent_comms_audit import audit_agent_comms_chain
from .ion_agent_comms_audit_gate import audit_gate_for_run
from .ion_agent_comms_chain_proof import prove_agent_comms_chain
from .ion_agent_spawn_templates import build_agent_roster_projection
from .ion_context_starter_capsule import build_context_starter_capsule_projection
from .ion_codex_agent_mount import PORTABLE_PACKAGE_ROOT, build_codex_agent_mounts_projection
from .ion_domain_weaver_true_names import (
    TRUE_NAME_DOMAIN_ID,
    TRUE_NAME_ROLE_ID,
    build_domain_identity,
    build_worker_identity,
    true_name_candidate_agent_row,
    true_name_candidate_domain_row,
)
from .ion_domain_weaver import build_domain_weaver_projection
from .ion_steward_dispatcher import build_steward_dispatcher_projection

SCHEMA_ID = "ion.agent_control_plane.v1"
READY_VERDICT = "ION_AGENT_CONTROL_PLANE_READY"

DOMAIN_WEAVE_ROOT = Path("ION_VNEXT/06_context/domain_weave")
DOMAIN_WEAVE_README = DOMAIN_WEAVE_ROOT / "README.md"
DOMAIN_WEAVE_MAP = DOMAIN_WEAVE_ROOT / "dry_runs/M103I_VNEXT_DOMAIN_WEAVE_MAP.candidate.yaml"
DOMAIN_WEAVE_REGISTRY = DOMAIN_WEAVE_ROOT / "dry_runs/M103I_VNEXT_DOMAIN_REGISTRY.candidate.yaml"
DOMAIN_WEAVE_ORG_CHART = DOMAIN_WEAVE_ROOT / "examples/integrated_agent_enterprise/AGENT_ORG_CHART.yaml"
DOMAIN_WEAVE_DRA_INDEX = DOMAIN_WEAVE_ROOT / "examples/integrated_agent_enterprise/DIRECT_RESPONSIBLE_AGENT_INDEX.yaml"
ACTIVE_DOMAIN_REGISTRY_DIR = Path("ION/03_registry/domains")
DOMAIN_WEAVER_CONTEXT_ACTIVE_RESOLVER_DOMAIN_ID = "domain.context_active_resolver"
DOMAIN_WEAVER_CONTEXT_ACTIVE_RESOLVER_ROLE_ID = "role.context_cartographer"
DOMAIN_WEAVER_REQUIRED_EXECUTABLE_LANE_IDS = (
    "architecture_lane",
    "implementation_lane",
    "audit_lane",
    "comms_lane",
    "browser_lane",
    "context_lane",
    "maintenance_lane",
    "approval_governance_lane",
    "settlement_lane",
)

CHAIN_STEPS = (
    {"step_id": "persona_ingress", "label": "PERSONA IN", "role_id": "role.persona_interface", "phase": "operator_intake", "direction": "inbound"},
    {"step_id": "relay_packetize", "label": "RELAY", "role_id": "role.relay", "phase": "packetize", "direction": "inbound"},
    {"step_id": "steward_route", "label": "STEWARD", "role_id": "role.steward", "phase": "route_and_integrate", "direction": "inbound"},
    {"step_id": "team_work", "label": "TEAM", "role_id": "role.mason", "phase": "specialist_work", "direction": "work"},
    {"step_id": "steward_final", "label": "STEWARD FINAL", "role_id": "role.steward", "phase": "proof_review", "direction": "outbound"},
    {"step_id": "relay_return", "label": "RELAY RETURN", "role_id": "role.relay", "phase": "return_packet", "direction": "outbound"},
    {"step_id": "persona_response", "label": "PERSONA OUT", "role_id": "role.persona_interface", "phase": "operator_response", "direction": "outbound"},
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    return candidate


def _read_text(path: Path, *, limit: int | None = None) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text if limit is None else text[:limit]


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _domain_weaver_required_lane_metadata() -> list[dict[str, str]]:
    return [
        {
            "lane_id": lane_id,
            "source": "domain.context_active_resolver.required_executable_lane",
        }
        for lane_id in DOMAIN_WEAVER_REQUIRED_EXECUTABLE_LANE_IDS
    ]


def _domain_weaver_context_active_resolver_domain_row() -> dict[str, Any]:
    return {
        "domain_id": DOMAIN_WEAVER_CONTEXT_ACTIVE_RESOLVER_DOMAIN_ID,
        "display_name": "Domain Context Active Resolver",
        "purpose": "Resolve fresh lane-bound Codex active-context packages before Domain Weaver worker starts.",
        "paths": [
            "ION/04_packages/kernel/ion_domain_weaver_context_active_resolver.py",
            "ION/04_packages/kernel/ion_domain_weaver_worker_start_readiness.py",
            "ION/05_context/current/codex_agent_mounts",
            "ION/05_context/current/chatgpt_connector/work_lanes/INDEX.json",
        ],
        "parent": "domain.domain_weaver",
        "children": [],
        "sibling_dependency_edges": [],
        "fact_posture": "candidate_projection_source_repair",
        "maturity_estimate": "candidate_projection_only",
        "suggested_steward_class": "CONTEXT_CARTOGRAPHER",
        "local_read_first_files": [
            "ION/04_packages/kernel/ion_domain_weaver_context_active_resolver.py",
            "ION/04_packages/kernel/ion_domain_weaver_worker_start_readiness.py",
        ],
        "blockers": [],
        "ready_for_future_steward_discovery_packet": False,
        "requires_split_merge_review": False,
        "source_registry": "ION/04_packages/kernel/ion_agent_control_plane.py#domain_context_active_resolver_candidate",
        "lane_ids": list(DOMAIN_WEAVER_REQUIRED_EXECUTABLE_LANE_IDS),
        "lane_metadata": _domain_weaver_required_lane_metadata(),
        "lane_metadata_policy": {
            "explicit_lane_metadata_only": True,
            "missing_lane_metadata_blocks_lane_bound_worker_start": True,
            "no_silent_fallback_to_domain_or_role_match": True,
        },
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _probe_path(root: Path, value: Any, *, excerpt_limit: int = 1400) -> dict[str, Any]:
    source = str(value or "").strip()
    if not source:
        return {"path": "", "exists": False, "kind": "missing"}
    path = Path(source)
    if not path.is_absolute():
        path = root / path
    try:
        relpath = path.relative_to(root).as_posix()
    except ValueError:
        relpath = path.as_posix()
    record: dict[str, Any] = {
        "path": source,
        "relpath": relpath,
        "abspath": path.as_posix(),
        "exists": path.exists(),
        "kind": "missing",
    }
    if path.is_dir():
        sample: list[str] = []
        for item in sorted(path.rglob("*")):
            if item.is_file():
                try:
                    sample.append(item.relative_to(root).as_posix())
                except ValueError:
                    sample.append(item.as_posix())
            if len(sample) >= 12:
                break
        record.update({"kind": "directory", "sample_files": sample})
        return record
    if not path.is_file():
        return record
    record.update(
        {
            "kind": "file",
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        }
    )
    if excerpt_limit <= 0 or path.suffix.lower() == ".zip":
        if path.suffix.lower() == ".zip":
            record["kind"] = "zip"
        return record
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        text = ""
    if text:
        record["excerpt"] = text[:excerpt_limit].strip()
    return record


def _probe_named_paths(root: Path, values: Mapping[str, Any], *, excerpt_limit: int = 1400) -> list[dict[str, Any]]:
    rows = []
    for label, value in values.items():
        row = _probe_path(root, value, excerpt_limit=excerpt_limit)
        row["label"] = label
        rows.append(row)
    return rows


def _portable_package_evidence(root: Path, mount: Mapping[str, Any]) -> dict[str, Any]:
    mount_id = str(mount.get("mount_id") or "").strip()
    if not mount_id:
        return {"exists": False, "reason": "missing_mount_id"}
    latest_path = root / PORTABLE_PACKAGE_ROOT / mount_id / "LATEST.json"
    latest = _read_json(latest_path)
    evidence: dict[str, Any] = {
        "exists": latest_path.is_file(),
        "latest_path": latest_path.relative_to(root).as_posix() if latest_path.is_absolute() else latest_path.as_posix(),
        "schema_id": latest.get("schema_id"),
        "package_id": latest.get("package_id"),
        "drop_in_ready": bool(latest.get("drop_in_ready")),
        "drop_in_path": latest.get("drop_in_path"),
        "launch_command": latest.get("launch_command"),
        "zip_path": latest.get("zip_path"),
        "zip_sha256": latest.get("zip_sha256"),
        "source_ref_copied_count": latest.get("source_ref_copied_count"),
        "source_ref_missing_count": latest.get("source_ref_missing_count"),
        "read_first": list(latest.get("read_first") or []),
        "authority": {
            "production_authority": bool(latest.get("production_authority")),
            "live_execution_authority": bool(latest.get("live_execution_authority")),
            "accepted_state_authority": bool(latest.get("accepted_state_authority")),
            "secrets_authority": bool(latest.get("secrets_authority")),
        },
    }
    if latest:
        drop_in = _probe_path(root, latest.get("drop_in_path"), excerpt_limit=0)
        zip_probe = _probe_path(root, latest.get("zip_path"), excerpt_limit=0)
        source_ref = latest.get("source_ref_manifest")
        if latest.get("drop_in_path") and source_ref:
            source_ref_path = Path(str(latest["drop_in_path"])) / str(source_ref)
            source_ref_probe = _probe_path(root, source_ref_path.as_posix(), excerpt_limit=900)
        else:
            source_ref_probe = {"path": "", "exists": False, "kind": "missing"}
        evidence["path_probes"] = [
            {**drop_in, "label": "drop_in_root"},
            {**zip_probe, "label": "zip_bundle"},
            {**source_ref_probe, "label": "source_ref_manifest"},
        ]
    else:
        evidence["path_probes"] = []
    return evidence


def _agent_page_evidence(root: Path, agent: Mapping[str, Any], domain: Mapping[str, Any] | None = None) -> dict[str, Any]:
    mount = _as_mapping(agent.get("native_codex_mount"))
    native_codex = _as_mapping(mount.get("native_codex"))
    context_card = _probe_path(root, agent.get("context_system_card"), excerpt_limit=2600)
    context_path_probes = [_probe_path(root, path, excerpt_limit=700) for path in agent.get("context_paths") or []]
    mount_files = _probe_named_paths(
        root,
        {
            "mount_root": mount.get("mount_path"),
            "mount_manifest": mount.get("manifest_path"),
            "agents_md": mount.get("agents_md_path"),
            "codex_config": mount.get("config_path"),
            "active_context_package_json": mount.get("active_context_package_path"),
            "active_context_package_md": mount.get("active_context_package_md_path"),
            "agent_system_card": mount.get("agent_system_card_path"),
            "domain_system_card": mount.get("domain_system_card_path"),
        },
        excerpt_limit=1200,
    )
    capsule_files = _probe_named_paths(
        root,
        {
            "portable_context_dir": mount.get("portable_context_dir"),
            "ion_context_capsule": mount.get("portable_context_manifest_path"),
            "mini": mount.get("portable_mini_path"),
            "capsule": mount.get("portable_capsule_path"),
            "long_horizon": mount.get("portable_long_horizon_path"),
            "route": mount.get("portable_route_path"),
            "agent": mount.get("portable_agent_path"),
            "domain": mount.get("portable_domain_path"),
            "relationships": mount.get("portable_relationships_path"),
            "communications": mount.get("portable_communications_path"),
            "address_book": mount.get("portable_address_book_path"),
            "active_context_package_json": mount.get("portable_active_context_package_path"),
            "active_context_package_md": mount.get("portable_active_context_package_md_path"),
        },
        excerpt_limit=1400,
    )
    address_book_probe = next((row for row in capsule_files if row.get("label") == "address_book"), {})
    address_book_payload = _read_json(Path(str(address_book_probe.get("abspath") or ""))) if address_book_probe.get("exists") else {}
    package = _portable_package_evidence(root, mount)
    is_ion_context_system = bool(context_card.get("exists") or agent.get("context_system_status"))
    is_capsule_agent = any(row.get("label") == "ion_context_capsule" and row.get("exists") for row in capsule_files)
    is_codex_native_mount = any(row.get("label") == "agents_md" and row.get("exists") for row in mount_files) and any(
        row.get("label") == "codex_config" and row.get("exists") for row in mount_files
    )
    is_portable_package_agent = bool(package.get("drop_in_ready"))
    agent_kind = "registry_only_candidate"
    if is_ion_context_system and is_capsule_agent and is_portable_package_agent:
        agent_kind = "ion_capsule_portable_codex_agent"
    elif is_ion_context_system and is_capsule_agent:
        agent_kind = "ion_capsule_codex_agent"
    elif is_ion_context_system:
        agent_kind = "ion_context_system_agent"
    elif is_capsule_agent:
        agent_kind = "folder_local_capsule_agent"
    checks = [
        {"label": "ION context card", "ok": bool(context_card.get("exists")), "path": context_card.get("relpath") or context_card.get("path")},
        {"label": "Codex AGENTS.md", "ok": bool(mount.get("agents_md_exists")), "path": mount.get("agents_md_path")},
        {"label": "Codex config.toml", "ok": bool(mount.get("config_exists")), "path": mount.get("config_path")},
        {"label": "active context package", "ok": bool(mount.get("active_context_package_md_exists")), "path": mount.get("active_context_package_md_path")},
        {"label": ".ion context capsule", "ok": bool(mount.get("portable_context_manifest_exists")), "path": mount.get("portable_context_manifest_path")},
        {"label": ".ion communications profile", "ok": bool(mount.get("portable_communications_exists")), "path": mount.get("portable_communications_path")},
        {"label": ".ion address book", "ok": bool(mount.get("portable_address_book_exists")), "path": mount.get("portable_address_book_path")},
        {"label": ".ion active package", "ok": bool(mount.get("portable_active_context_package_md_exists")), "path": mount.get("portable_active_context_package_md_path")},
        {"label": "portable drop-in package", "ok": bool(package.get("drop_in_ready")), "path": package.get("drop_in_path")},
    ]
    missing_critical = [str(check["label"]) for check in checks if not check.get("ok")]
    return {
        "schema_id": "ion.agent_page_evidence.v1",
        "generated_at": _now(),
        "identity": {
            "agent_id": agent.get("agent_id"),
            "role_id": agent.get("role_id"),
            "display_name": agent.get("display_name"),
            "backend_carrier_id": agent.get("backend_carrier_id"),
            "domain_id": mount.get("domain_id") or agent.get("registry_primary_domain") or (domain or {}).get("domain_id"),
            "registry_primary_domain": agent.get("registry_primary_domain"),
            "registry_secondary_domains": list(agent.get("registry_secondary_domains") or []),
            "role_domain_label": agent.get("role_domain_label"),
            "continuity_home": agent.get("continuity_home"),
            "agent_kind": agent_kind,
            "is_ion_context_system": is_ion_context_system,
            "is_capsule_agent": is_capsule_agent,
            "is_codex_native_mount": is_codex_native_mount,
            "is_portable_package_agent": is_portable_package_agent,
        },
        "authority": {
            "write_posture": agent.get("write_posture") or "none",
            "invocable": bool(agent.get("invocable")),
            "default_mount_posture": agent.get("default_mount_posture"),
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
        "context_system": {
            "status": agent.get("context_system_status"),
            "card": context_card,
            "package_strategy": agent.get("package_strategy"),
            "default_active_package_class": agent.get("default_active_package_class"),
            "context_paths": context_path_probes,
            "missing_declared_context_paths": list(agent.get("missing_declared_context_paths") or []),
            "missing_legacy_context_paths": list(agent.get("missing_legacy_context_paths") or []),
            "legacy_context_missing_is_blocking": False,
            "read_zones": list(agent.get("default_read_zones") or []),
            "proof_obligations": list(agent.get("default_proof_obligations") or []),
            "primary_templates": list(agent.get("primary_templates") or []),
        },
        "codex_mount": {
            "mount_id": mount.get("mount_id"),
            "materialized": bool(mount.get("materialized")),
            "hook_strategy": mount.get("hook_strategy"),
            "native_codex": native_codex,
            "command_preview": list(native_codex.get("command_preview") or []),
            "interactive_command_preview": list(native_codex.get("interactive_command_preview") or []),
            "prompt_visibility_probe": native_codex.get("prompt_visibility_probe"),
            "files": mount_files,
        },
        "capsule": {
            "is_capsule_agent": is_capsule_agent,
            "files": capsule_files,
            "read_first": [
                "AGENTS.md",
                ".ion/ION_CONTEXT_CAPSULE.yaml",
                ".ion/ACTIVE_CONTEXT_PACKAGE.md",
                ".ion/AGENT.yaml",
                ".ion/DOMAIN.yaml",
                ".ion/RELATIONSHIPS.yaml",
                ".ion/COMMUNICATIONS.json",
                ".ion/ADDRESS_BOOK.json",
            ],
        },
        "address_book": {
            "exists": bool(address_book_probe.get("exists")),
            "path": address_book_probe.get("relpath") or mount.get("portable_address_book_path"),
            "schema_id": address_book_payload.get("schema_id"),
            "summary": dict(address_book_payload.get("summary") or {}),
            "contact_groups": dict(address_book_payload.get("contact_groups") or {}),
            "routing_rules": list(address_book_payload.get("routing_rules") or []),
            "situation_map": dict(address_book_payload.get("situation_map") or {}),
        },
        "portable_package": package,
        "domain": {
            "domain_id": (domain or {}).get("domain_id") or mount.get("domain_id"),
            "purpose": (domain or {}).get("purpose"),
            "fact_posture": (domain or {}).get("fact_posture"),
            "maturity_estimate": (domain or {}).get("maturity_estimate"),
            "paths": list((domain or {}).get("paths") or []),
            "local_read_first_files": list((domain or {}).get("local_read_first_files") or []),
            "source_registry": (domain or {}).get("source_registry"),
        },
        "proof": {
            "checks": checks,
            "critical_ready": not missing_critical,
            "missing_critical": missing_critical,
            "source_model": "agent registry + context-system card + generated Codex mount + folder-local .ion capsule + portable package manifest",
        },
        "diagnostics": {
            "warnings": missing_critical,
            "missing_declared_context_path_count": len(agent.get("missing_declared_context_paths") or []),
            "missing_legacy_context_path_count": len(agent.get("missing_legacy_context_paths") or []),
        },
    }


def _coerce_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "yes", "1", "on"}


def _line_value(line: str) -> str:
    return line.split(":", 1)[1].strip().strip("\"'")


def _parse_yaml_list_blocks(path: Path, *, section: str, id_key: str) -> list[dict[str, Any]]:
    text = _read_text(path)
    if not text:
        return []
    rows: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    list_key: str | None = None
    active = False
    base_indent: int | None = None

    for raw in text.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        stripped = raw.strip()
        indent = len(raw) - len(raw.lstrip(" "))
        if indent == 0 and stripped.endswith(":"):
            if active and current:
                rows.append(current)
            active = stripped[:-1] == section
            base_indent = None
            current = None
            list_key = None
            continue
        if not active:
            continue
        if stripped.startswith(f"- {id_key}:"):
            if current:
                rows.append(current)
            current = {id_key: _line_value(stripped[2:])}
            base_indent = indent
            list_key = None
            continue
        if current is None:
            continue
        if base_indent is not None and indent <= base_indent and not stripped.startswith("- "):
            rows.append(current)
            current = None
            list_key = None
            continue
        if stripped.startswith("- ") and list_key:
            current.setdefault(list_key, []).append(stripped[2:].strip().strip("\"'"))
            continue
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            value = value.strip()
            if value == "":
                current[key] = []
                list_key = key
            elif value in {"[]", "{}"}:
                current[key] = []
                list_key = None
            elif value.lower() in {"true", "false"}:
                current[key] = _coerce_bool(value)
                list_key = None
            else:
                current[key] = value.strip("\"'")
                list_key = None
    if active and current:
        rows.append(current)
    return rows


def _parse_domain_registry(path: Path) -> list[dict[str, Any]]:
    text = _read_text(path)
    if not text:
        return []
    rows: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    list_key: str | None = None
    in_domains = False
    for raw in text.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        stripped = raw.strip()
        indent = len(raw) - len(raw.lstrip(" "))
        if indent == 0:
            if stripped == "domains:":
                in_domains = True
                continue
            if in_domains:
                break
        if not in_domains:
            continue
        if indent == 2 and stripped.endswith(":") and not stripped.startswith("- "):
            if current:
                rows.append(current)
            current = {"domain_id": stripped[:-1].strip("\"'")}
            list_key = None
            continue
        if current is None:
            continue
        if stripped.startswith("- ") and list_key:
            current.setdefault(list_key, []).append(stripped[2:].strip().strip("\"'"))
            continue
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            value = value.strip()
            if value == "":
                current[key] = []
                list_key = key
            elif value in {"[]", "{}"}:
                current[key] = []
                list_key = None
            elif value.lower() in {"true", "false"}:
                current[key] = _coerce_bool(value)
                list_key = None
            else:
                current[key] = value.strip("\"'")
                list_key = None
    if current:
        rows.append(current)
    return rows


def _parse_active_domain_file(path: Path) -> dict[str, Any]:
    text = _read_text(path)
    if not text:
        return {}
    row: dict[str, Any] = {"source_registry": path.as_posix()}
    list_key: str | None = None
    multiline_key: str | None = None
    multiline_indent: int | None = None
    multiline_parts: list[str] = []

    def flush_multiline() -> None:
        nonlocal multiline_key, multiline_indent, multiline_parts
        if multiline_key:
            row[multiline_key] = " ".join(part.strip() for part in multiline_parts if part.strip())
        multiline_key = None
        multiline_indent = None
        multiline_parts = []

    for raw in text.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        stripped = raw.strip()
        indent = len(raw) - len(raw.lstrip(" "))
        if multiline_key and multiline_indent is not None:
            if indent > multiline_indent:
                multiline_parts.append(stripped)
                continue
            flush_multiline()
        if indent == 0 and ":" in stripped:
            key, value = stripped.split(":", 1)
            value = value.strip()
            list_key = None
            if value in {">-", "|"}:
                multiline_key = key
                multiline_indent = indent
                multiline_parts = []
            elif value == "":
                row[key] = []
                list_key = key
            elif value.lower() in {"true", "false"}:
                row[key] = _coerce_bool(value)
            else:
                row[key] = value.strip("\"'")
            continue
        if indent == 2 and stripped.startswith("- ") and list_key:
            row.setdefault(list_key, []).append(stripped[2:].strip().strip("\"'"))
    flush_multiline()
    return row


def _active_domain_registry_rows(root: Path) -> list[dict[str, Any]]:
    base = root / ACTIVE_DOMAIN_REGISTRY_DIR
    rows: list[dict[str, Any]] = []
    if not base.exists():
        return rows
    for path in sorted(base.glob("domain.*.domain.yaml")):
        payload = _parse_active_domain_file(path)
        domain_id = str(payload.get("domain_id") or "").strip()
        if not domain_id:
            continue
        paths = list(payload.get("owned_or_stewarded_surfaces") or [])
        rows.append(
            {
                "domain_id": domain_id,
                "display_name": payload.get("display_name"),
                "purpose": payload.get("mission") or payload.get("purpose"),
                "paths": paths,
                "parent": None,
                "children": [],
                "sibling_dependency_edges": list(payload.get("open_edges") or []),
                "fact_posture": payload.get("status") or "active_registry",
                "maturity_estimate": payload.get("authority") or "active_domain_registry",
                "suggested_steward_class": next(iter(payload.get("primary_roles") or []), None),
                "local_read_first_files": [path.as_posix(), *paths[:5]],
                "blockers": list(payload.get("open_edges") or []),
                "lane_ids": list(payload.get("lane_ids") or []),
                "lane_metadata": list(payload.get("lane_metadata") or []),
                "lane_metadata_policy": dict(payload.get("lane_metadata_policy") or {}),
                "ready_for_future_steward_discovery_packet": True,
                "requires_split_merge_review": False,
                "source_registry": path.as_posix(),
            }
        )
    return rows


def _recent_run_index(queue: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = {}
    for row in queue.get("invocations") or []:
        if not isinstance(row, Mapping):
            continue
        role_id = str(row.get("agent_role_id") or "")
        if role_id:
            index.setdefault(role_id, []).append(dict(row))
    return index


def _agent_rows(root: Path, queue: Mapping[str, Any]) -> list[dict[str, Any]]:
    recent_by_role = _recent_run_index(queue)
    rows: list[dict[str, Any]] = []
    for agent in list_agents(root).get("agents") or []:
        if not isinstance(agent, Mapping):
            continue
        role_id = str(agent.get("role_id") or "")
        role_key = role_id.split(".")[-1] if role_id else str(agent.get("display_name") or "")
        context_summary = runtime_context_system_summary(root, role_key)
        missing_paths = list(agent.get("missing_declared_context_paths") or [])
        legacy_missing = [path for path in missing_paths if "/agents/" in path]
        authority = agent.get("default_authority_ceiling") if isinstance(agent.get("default_authority_ceiling"), Mapping) else {}
        registry_primary_domain = str(agent.get("registry_primary_domain") or "")
        if role_id == DOMAIN_WEAVER_CONTEXT_ACTIVE_RESOLVER_ROLE_ID:
            registry_primary_domain = DOMAIN_WEAVER_CONTEXT_ACTIVE_RESOLVER_DOMAIN_ID
        lane_ids = list(agent.get("lane_ids") or [])
        worker_identity = build_worker_identity(
            role_id=role_id,
            domain_id=registry_primary_domain,
            lane_ids=lane_ids,
            callsign=str(agent.get("callsign") or "").strip() or None,
        )
        rows.append(
            {
                "agent_id": agent.get("agent_id") or role_id,
                "role_id": role_id,
                "display_name": agent.get("display_name") or role_id,
                "invocable": bool(agent.get("invocable")),
                "backend_carrier_id": agent.get("backend_carrier_id"),
                "context_system_card": agent.get("context_system_card") or context_summary.get("context_system_card"),
                "context_system_status": context_summary.get("status"),
                "package_strategy": agent.get("package_strategy") or context_summary.get("package_strategy"),
                "default_active_package_class": agent.get("default_active_package_class") or context_summary.get("default_active_package_class"),
                "registry_primary_domain": registry_primary_domain or agent.get("registry_primary_domain"),
                "registry_secondary_domains": list(agent.get("registry_secondary_domains") or []),
                "lane_ids": lane_ids,
                "lane_metadata": list(agent.get("lane_metadata") or []),
                "lane_metadata_policy": dict(agent.get("lane_metadata_policy") or {}),
                "worker_identity": worker_identity,
                "role_domain_label": agent.get("role_domain_label"),
                "continuity_home": agent.get("continuity_home"),
                "default_mount_posture": agent.get("default_mount_posture"),
                "context_paths": list(agent.get("context_paths") or []),
                "missing_declared_context_paths": missing_paths,
                "missing_legacy_context_paths": legacy_missing,
                "legacy_context_missing_is_blocking": False,
                "primary_templates": list(agent.get("primary_templates") or []),
                "write_posture": agent.get("write_posture") or authority.get("local_write_authority"),
                "default_read_zones": list(agent.get("default_read_zones") or []),
                "default_proof_obligations": list(agent.get("default_proof_obligations") or []),
                "recent_invocations": recent_by_role.get(role_id, [])[:5],
                "actions": {
                    "prepare": True,
                    "start": bool(agent.get("invocable")),
                    "cancel": True,
                    "open_result": True,
                    "open_evidence": True,
                    "copy_launch_packet": True,
                },
                "production_authority": False,
                "live_execution_authority": False,
            }
        )
    if not any(str(row.get("role_id") or "") == TRUE_NAME_ROLE_ID for row in rows):
        rows.append(true_name_candidate_agent_row())
    if not any(str(row.get("role_id") or "") == DOMAIN_WEAVER_CONTEXT_ACTIVE_RESOLVER_ROLE_ID for row in rows):
        rows.append(
            {
                "agent_id": DOMAIN_WEAVER_CONTEXT_ACTIVE_RESOLVER_ROLE_ID,
                "role_id": DOMAIN_WEAVER_CONTEXT_ACTIVE_RESOLVER_ROLE_ID,
                "display_name": "Context Active Resolver",
                "invocable": False,
                "backend_carrier_id": "codex_cli",
                "context_system_card": "ION/05_context/current/agent_context_systems/RUNTIME_CARTOGRAPHER.context_system.md",
                "context_system_status": "candidate_projection_source_repair",
                "package_strategy": "active_context_package",
                "default_active_package_class": "context_active_resolver",
                "registry_primary_domain": DOMAIN_WEAVER_CONTEXT_ACTIVE_RESOLVER_DOMAIN_ID,
                "registry_secondary_domains": [],
                "lane_ids": list(DOMAIN_WEAVER_REQUIRED_EXECUTABLE_LANE_IDS),
                "lane_metadata": _domain_weaver_required_lane_metadata(),
                "lane_metadata_policy": {
                    "explicit_lane_metadata_only": True,
                    "missing_lane_metadata_blocks_lane_bound_worker_start": True,
                    "no_silent_fallback_to_domain_or_role_match": True,
                },
                "worker_identity": build_worker_identity(
                    role_id=DOMAIN_WEAVER_CONTEXT_ACTIVE_RESOLVER_ROLE_ID,
                    domain_id=DOMAIN_WEAVER_CONTEXT_ACTIVE_RESOLVER_DOMAIN_ID,
                    lane_ids=DOMAIN_WEAVER_REQUIRED_EXECUTABLE_LANE_IDS,
                    rank="R3_CARTOGRAPHER",
                    true_name="DOMAIN_CONTEXT_ACTIVE_RESOLVER_CARTOGRAPHER",
                ),
                "role_domain_label": "Domain Context Active Resolver",
                "continuity_home": None,
                "default_mount_posture": "candidate_context_mount_only",
                "context_paths": [
                    "ION/04_packages/kernel/ion_domain_weaver_context_active_resolver.py",
                    "ION/04_packages/kernel/ion_domain_weaver_worker_start_readiness.py",
                ],
                "missing_declared_context_paths": [],
                "missing_legacy_context_paths": [],
                "legacy_context_missing_is_blocking": False,
                "primary_templates": [],
                "write_posture": "read_only_projection",
                "default_read_zones": ["ION/05_context/current/codex_agent_mounts"],
                "default_proof_obligations": ["fresh_lane_bound_active_context_before_worker_start"],
                "recent_invocations": recent_by_role.get(DOMAIN_WEAVER_CONTEXT_ACTIVE_RESOLVER_ROLE_ID, [])[:5],
                "actions": {
                    "prepare": True,
                    "start": False,
                    "cancel": True,
                    "open_result": True,
                    "open_evidence": True,
                    "copy_launch_packet": True,
                },
                "production_authority": False,
                "live_execution_authority": False,
            }
        )
    return rows


def _domain_rows(root: Path) -> list[dict[str, Any]]:
    registry_rows = _parse_domain_registry(root / DOMAIN_WEAVE_REGISTRY)
    if not registry_rows:
        registry_rows = _parse_yaml_list_blocks(root / DOMAIN_WEAVE_MAP, section="domains", id_key="domain_id")
    active_registry_rows = _active_domain_registry_rows(root)
    combined_rows: list[dict[str, Any]] = []
    seen_domains: set[str] = set()
    for domain in [*active_registry_rows, *registry_rows]:
        domain_id = str(domain.get("domain_id") or "")
        if not domain_id or domain_id in seen_domains:
            continue
        combined_rows.append(domain)
        seen_domains.add(domain_id)
    if DOMAIN_WEAVER_CONTEXT_ACTIVE_RESOLVER_DOMAIN_ID not in seen_domains:
        combined_rows.append(_domain_weaver_context_active_resolver_domain_row())
        seen_domains.add(DOMAIN_WEAVER_CONTEXT_ACTIVE_RESOLVER_DOMAIN_ID)
    if TRUE_NAME_DOMAIN_ID not in seen_domains:
        combined_rows.append(true_name_candidate_domain_row())
        seen_domains.add(TRUE_NAME_DOMAIN_ID)
    org_rows = _parse_yaml_list_blocks(root / DOMAIN_WEAVE_ORG_CHART, section="agents", id_key="agent_id")
    dra_rows = _parse_yaml_list_blocks(root / DOMAIN_WEAVE_DRA_INDEX, section="direct_responsible_agents", id_key="artifact_class")
    agents_by_domain: dict[str, list[dict[str, Any]]] = {}
    for agent in org_rows:
        domain_id = str(agent.get("domain_id") or "")
        if domain_id:
            agents_by_domain.setdefault(domain_id, []).append(agent)
    artifact_by_domain: dict[str, list[dict[str, Any]]] = {}
    for row in dra_rows:
        domain_id = str(row.get("parent_domain") or "")
        if domain_id:
            artifact_by_domain.setdefault(domain_id, []).append(row)

    rows: list[dict[str, Any]] = []
    for domain in combined_rows:
        domain_id = str(domain.get("domain_id") or "")
        rows.append(
            {
                "domain_id": domain_id,
                "domain_identity": domain.get("domain_identity")
                or build_domain_identity(
                    domain_id=domain_id,
                    steward_role_id=str(domain.get("suggested_steward_class") or ""),
                    lane_ids=list(domain.get("lane_ids") or []),
                ),
                "purpose": domain.get("purpose"),
                "paths": list(domain.get("paths") or []),
                "parent": domain.get("parent"),
                "children": list(domain.get("children") or []),
                "sibling_dependency_edges": list(domain.get("sibling_dependency_edges") or []),
                "fact_posture": domain.get("fact_posture") or "inferred_candidate",
                "maturity_estimate": domain.get("maturity_estimate"),
                "suggested_steward_class": domain.get("suggested_steward_class"),
                "local_read_first_files": list(domain.get("local_read_first_files") or []),
                "blockers": list(domain.get("blockers") or []),
                "lane_ids": list(domain.get("lane_ids") or []),
                "lane_metadata": list(domain.get("lane_metadata") or []),
                "lane_metadata_policy": dict(domain.get("lane_metadata_policy") or {}),
                "ready_for_future_steward_discovery_packet": bool(domain.get("ready_for_future_steward_discovery_packet")),
                "requires_split_merge_review": bool(domain.get("requires_split_merge_review")),
                "source_registry": domain.get("source_registry")
                or (DOMAIN_WEAVE_REGISTRY.as_posix() if domain_id.startswith("ion_vnext_") else None),
                "domain_agents": agents_by_domain.get(domain_id, []),
                "owned_artifact_classes": artifact_by_domain.get(domain_id, []),
                "activation_posture": "candidate_request_only",
                "accepted_ion_state": False,
                "production_authority": False,
                "live_execution_authority": False,
            }
        )
    return rows


def _chain_projection(broker: Mapping[str, Any], agents: list[Mapping[str, Any]]) -> dict[str, Any]:
    agent_by_role = {str(agent.get("role_id") or ""): agent for agent in agents}
    steps = []
    for step in CHAIN_STEPS:
        role = agent_by_role.get(step["role_id"], {})
        steps.append(
            {
                **step,
                "agent_display_name": role.get("display_name") or step["label"],
                "context_system_card": role.get("context_system_card"),
                "invocable": bool(role.get("invocable")),
                "status": "ready" if role.get("invocable") else "context_only",
            }
        )
    active = broker.get("codex_queue_runner") if isinstance(broker.get("codex_queue_runner"), Mapping) else {}
    return {
        "schema_id": "ion.agent_control_plane.chain.v1",
        "steps": steps,
        "active_process_running": bool(active.get("active_process_running")),
        "active_run": active.get("active_run"),
        "return_path": "steward_final -> relay_return -> persona_response",
        "single_carrier_sequential": True,
    }


def _runs_projection(broker: Mapping[str, Any], queue: Mapping[str, Any]) -> dict[str, Any]:
    runner = broker.get("codex_queue_runner") if isinstance(broker.get("codex_queue_runner"), Mapping) else {}
    latest_state = broker.get("latest_state") if isinstance(broker.get("latest_state"), Mapping) else {}
    return {
        "schema_id": "ion.agent_control_plane.runs.v1",
        "active_process_running": bool(runner.get("active_process_running")),
        "active_run": runner.get("active_run"),
        "live_worker_telemetry": runner.get("live_worker_telemetry"),
        "latest_state": latest_state,
        "recent_invocations": list(queue.get("invocations") or [])[:20],
        "agent_invocation_count": queue.get("invocation_count"),
        "queued_agent_codex_work_request_count": broker.get("queued_agent_codex_work_request_count"),
        "next_agent_codex_work_request_path": broker.get("next_agent_codex_work_request_path"),
    }


def _communications_projection(
    root: Path,
    queue: Mapping[str, Any],
    agents: list[dict[str, Any]] | None = None,
    communication_directory: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    all_relays = pending_agent_relays(root, include_answered=True)
    pending_relays = pending_agent_relays(root, include_answered=False)
    receipts = recent_agent_invocation_receipts(root, limit=50)
    team_comms = build_agent_comms_projection(root, agents=agents or [], limit=100)
    team_comms_chain_audit = audit_agent_comms_chain(root, {"write_receipt": False})
    team_comms_chain_proof = prove_agent_comms_chain(root, {"write_receipt": False})
    team_comms_chain_gate = audit_gate_for_run(
        root,
        str(team_comms_chain_audit.get("run_id") or ""),
        run_path=str(team_comms_chain_audit.get("run_path") or ""),
    )
    invocation_rows = list(queue.get("invocations") or [])[:50]
    relay_rows = list(all_relays.get("relays") or [])[:100]
    receipt_rows = list(receipts.get("receipts") or [])[:50]
    timeline: list[dict[str, Any]] = []
    for row in invocation_rows:
        if not isinstance(row, Mapping):
            continue
        timeline.append(
            {
                "kind": "invocation",
                "timestamp": row.get("created_at") or row.get("updated_at"),
                "status": row.get("status"),
                "agent_role_id": row.get("agent_role_id"),
                "agent_display_name": row.get("agent_display_name"),
                "invocation_id": row.get("invocation_id"),
                "path": row.get("path"),
                "codex_work_request_path": row.get("codex_work_request_path"),
            }
        )
    for row in relay_rows:
        if not isinstance(row, Mapping):
            continue
        timeline.append(
            {
                "kind": "relay",
                "timestamp": row.get("created_at") or row.get("updated_at"),
                "status": row.get("status"),
                "from_agent": row.get("from_agent"),
                "to": row.get("to"),
                "question_type": row.get("question_type"),
                "question": row.get("question"),
                "relay_id": row.get("relay_id"),
                "invocation_id": row.get("invocation_id"),
                "path": row.get("path"),
            }
        )
    for row in receipt_rows:
        if not isinstance(row, Mapping):
            continue
        timeline.append(
            {
                "kind": "receipt",
                "timestamp": row.get("created_at"),
                "status": row.get("status"),
                "event": row.get("event"),
                "receipt_id": row.get("receipt_id"),
                "invocation_id": row.get("invocation_id"),
                "path": row.get("path"),
            }
        )
    timeline.sort(key=lambda item: str(item.get("timestamp") or ""), reverse=True)
    contact_contract = _as_mapping(_as_mapping(communication_directory).get("contact_contract"))
    contact_template_contracts = _as_mapping(contact_contract.get("template_contracts"))
    room_contract = _as_mapping(_as_mapping(communication_directory).get("room_contract"))
    room_contract_rooms = _as_mapping(room_contract.get("rooms_by_id"))
    room_projection = _as_mapping(team_comms.get("rooms"))
    return {
        "schema_id": "ion.agent_control_plane.communications.v1",
        "invocations": invocation_rows,
        "relays": relay_rows,
        "pending_relays": list(pending_relays.get("relays") or []),
        "receipts": receipt_rows,
        "timeline": timeline[:150],
        "contact_contract": {
            "schema_id": contact_contract.get("schema_id"),
            "routing_source_of_truth": contact_contract.get("routing_source_of_truth"),
            "agent_count": contact_contract.get("agent_count", 0),
            "available_agent_count": contact_contract.get("available_agent_count", 0),
            "contact_edge_count": contact_contract.get("contact_edge_count", 0),
            "routing_rule_count": len(list(contact_contract.get("routing_rules") or [])),
            "template_contract_count": len(contact_template_contracts),
            "alias_count": len(_as_mapping(contact_contract.get("aliases_by_token"))),
            "alias_conflict_count": len(_as_mapping(contact_contract.get("alias_conflicts"))),
        },
        "room_contract": {
            "schema_id": room_contract.get("schema_id"),
            "routing_source_of_truth": room_contract.get("routing_source_of_truth"),
            "owner_domain_id": room_contract.get("owner_domain_id"),
            "recommended_owner_role": room_contract.get("recommended_owner_role"),
            "room_count": room_contract.get("room_count", len(room_contract_rooms)),
            "room_kind_count": len(list(room_contract.get("room_kinds") or [])),
            "routing_rule_count": len(list(room_contract.get("routing_rules") or [])),
            "reporting_rule_count": len(list(room_contract.get("reporting_rules") or [])),
            "context_loading": _as_mapping(room_contract.get("context_loading")),
        },
        "team_comms": team_comms,
        "team_comms_chain_audit": team_comms_chain_audit,
        "team_comms_chain_proof": team_comms_chain_proof,
        "team_comms_chain_gate": team_comms_chain_gate,
        "summary": {
            "invocation_count": queue.get("invocation_count"),
            "relay_count": all_relays.get("relay_count"),
            "pending_relay_count": pending_relays.get("relay_count"),
            "receipt_count": receipts.get("receipt_count"),
            "team_thread_count": team_comms.get("summary", {}).get("thread_count"),
            "team_message_count": team_comms.get("summary", {}).get("message_count"),
            "team_room_count": room_projection.get("room_count", 0),
            "team_comms_chain_audit_state": team_comms_chain_audit.get("audit_state"),
            "team_comms_chain_audit_ok": team_comms_chain_audit.get("ok"),
            "team_comms_chain_proof_state": team_comms_chain_proof.get("proof_state"),
            "team_comms_chain_proof_ok": team_comms_chain_proof.get("ok"),
            "team_comms_chain_first_missing_link": team_comms_chain_proof.get("first_missing_link"),
            "team_comms_chain_clean_state": team_comms_chain_gate.get("state"),
            "team_comms_chain_clean": team_comms_chain_gate.get("clean"),
            "contact_contract_schema_id": contact_contract.get("schema_id"),
            "contact_contract_edge_count": contact_contract.get("contact_edge_count", 0),
            "contact_contract_template_count": len(contact_template_contracts),
            "room_contract_schema_id": room_contract.get("schema_id"),
            "room_contract_room_count": room_contract.get("room_count", len(room_contract_rooms)),
        },
        "policy": "Visible agent communication is durable packet/thread/inbox evidence plus invocation/relay/response/settlement evidence; not a fake live chat entity.",
        "production_authority": False,
        "live_execution_authority": False,
    }


def build_agent_control_plane_projection(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    broker = build_agent_broker_status(shell_root)
    queue = agent_queue(shell_root, limit=50)
    domain_rows = _domain_rows(shell_root)
    agent_rows = _agent_rows(shell_root, queue)
    codex_mounts = build_codex_agent_mounts_projection(shell_root, agent_rows, domain_rows)
    mounts_by_role = {
        str(mount.get("agent_role_id") or ""): mount
        for mount in codex_mounts.get("mounts") or []
        if isinstance(mount, Mapping)
    }
    domains_by_id = {str(domain.get("domain_id") or ""): domain for domain in domain_rows}
    for agent in agent_rows:
        mount = mounts_by_role.get(str(agent.get("role_id") or ""))
        agent["native_codex_mount"] = mount
        domain = domains_by_id.get(str(_as_mapping(mount).get("domain_id") or agent.get("registry_primary_domain") or ""))
        agent["agent_page_evidence"] = _agent_page_evidence(shell_root, agent, domain)
    roster = build_agent_roster_projection(shell_root, agents=agent_rows, domains=domain_rows)
    domain_weaver = build_domain_weaver_projection(
        shell_root,
        agents=agent_rows,
        domains=domain_rows,
        codex_mounts=codex_mounts,
        roster=roster,
    )
    context_audit = audit_agent_context_systems(shell_root).to_dict()
    starter_capsule = build_context_starter_capsule_projection(shell_root)
    domain_weave_validation = _read_json(shell_root / (DOMAIN_WEAVE_ROOT / "reports/M103B_VALIDATION_REPORT.json"))
    missing_legacy_refs = sorted({path for agent in agent_rows for path in agent.get("missing_legacy_context_paths", [])})
    diagnostics = {
        "schema_id": "ion.agent_control_plane.diagnostics.v1",
        "agent_context_system_audit": context_audit,
        "domain_weave_status": "present" if (shell_root / DOMAIN_WEAVE_README).exists() else "missing",
        "domain_weave_readme_excerpt": _read_text(shell_root / DOMAIN_WEAVE_README, limit=1200),
        "domain_weave_validation_status": domain_weave_validation.get("status") or domain_weave_validation.get("verdict"),
        "missing_legacy_context_ref_count": len(missing_legacy_refs),
        "missing_legacy_context_refs_sample": missing_legacy_refs[:25],
        "legacy_refs_are_witness_only": True,
        "codex_agent_mounts": {
            "mount_root": codex_mounts.get("mount_root"),
            "mount_count": codex_mounts.get("mount_count"),
            "materialized_count": codex_mounts.get("materialized_count"),
            "prompt_visibility_proven_count": codex_mounts.get("prompt_visibility_proven_count"),
        },
        "domain_weaver": {
            "weave_status": domain_weaver.get("weave_status"),
            "projection_path": domain_weaver.get("projection_path"),
            "usable_domain_count": domain_weaver.get("summary", {}).get("usable_domain_count")
            if isinstance(domain_weaver.get("summary"), Mapping)
            else 0,
            "gap_count": domain_weaver.get("summary", {}).get("gap_count")
            if isinstance(domain_weaver.get("summary"), Mapping)
            else 0,
        },
        "broker_findings": list(broker.get("findings") or []),
    }
    runs = _runs_projection(broker, queue)
    communication_directory = _as_mapping(roster.get("communication_directory"))
    contact_contract = _as_mapping(communication_directory.get("contact_contract"))
    room_contract = _as_mapping(communication_directory.get("room_contract"))
    communications = _communications_projection(shell_root, queue, agent_rows, communication_directory)
    dispatcher = build_steward_dispatcher_projection(
        shell_root,
        agents=agent_rows,
        domains=domain_rows,
        communications=communications,
        runs=runs,
        domain_weaver=domain_weaver,
    )
    dispatcher_summary = dispatcher.get("summary") if isinstance(dispatcher.get("summary"), Mapping) else {}
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "verdict": READY_VERDICT if broker.get("accepted") else "ION_AGENT_CONTROL_PLANE_PARTIAL",
        "ok": True,
        "shell_root": shell_root.as_posix(),
        "source_model": {
            "agent_context_systems": "primary_role_truth",
            "domain_weave": "candidate_domain_truth",
            "domain_weaver": "operational_registry_mount_comms_projection",
            "mini_capsule": "continuity_witness_only",
            "direct_codex": "existing_agent_broker_and_codex_queue_runner_start_true",
        },
        "summary": {
            "agent_count": len(agent_rows),
            "invocable_agent_count": sum(1 for agent in agent_rows if agent.get("invocable")),
            "domain_count": len(domain_rows),
            "active_process_running": bool((broker.get("codex_queue_runner") or {}).get("active_process_running"))
            if isinstance(broker.get("codex_queue_runner"), Mapping)
            else False,
            "queued_agent_codex_work_request_count": broker.get("queued_agent_codex_work_request_count", 0),
            "missing_legacy_context_ref_count": len(missing_legacy_refs),
            "codex_mount_count": codex_mounts.get("mount_count", 0),
            "materialized_codex_mount_count": codex_mounts.get("materialized_count", 0),
            "roster_capsule_agent_count": roster.get("capsule_agent_count", 0),
            "roster_domain_built_count": roster.get("domain_built_count", 0),
            "available_agent_comms_count": roster.get("communication_directory", {}).get("available_agent_count", 0)
            if isinstance(roster.get("communication_directory"), Mapping)
            else 0,
            "agent_contact_contract_edge_count": contact_contract.get("contact_edge_count", 0),
            "agent_contact_contract_template_count": len(_as_mapping(contact_contract.get("template_contracts"))),
            "agent_room_contract_room_count": room_contract.get("room_count", 0),
            "agent_room_contract_schema_id": room_contract.get("schema_id"),
            "domain_weaver_usable_domain_count": domain_weaver.get("summary", {}).get("usable_domain_count", 0)
            if isinstance(domain_weaver.get("summary"), Mapping)
            else 0,
            "active_domain_count": domain_weaver.get("summary", {}).get("active_domain_count", 0)
            if isinstance(domain_weaver.get("summary"), Mapping)
            else 0,
            "candidate_domain_count": domain_weaver.get("summary", {}).get("candidate_domain_count", 0)
            if isinstance(domain_weaver.get("summary"), Mapping)
            else 0,
            "candidate_covered_domain_count": domain_weaver.get("summary", {}).get("candidate_covered_domain_count", 0)
            if isinstance(domain_weaver.get("summary"), Mapping)
            else 0,
            "covered_domain_count": domain_weaver.get("summary", {}).get("covered_domain_count", 0)
            if isinstance(domain_weaver.get("summary"), Mapping)
            else 0,
            "domain_weaver_gap_count": domain_weaver.get("summary", {}).get("gap_count", 0)
            if isinstance(domain_weaver.get("summary"), Mapping)
            else 0,
            "domain_weaver_edge_count": domain_weaver.get("summary", {}).get("edge_count", 0)
            if isinstance(domain_weaver.get("summary"), Mapping)
            else 0,
            "dispatcher_actionable_run_count": dispatcher_summary.get("actionable_run_count", 0),
            "dispatcher_active_worker_count": dispatcher_summary.get("active_worker_count", 0),
            "dispatcher_pending_directive_count": dispatcher_summary.get("pending_directive_count", 0),
        },
        "chain": _chain_projection(broker, agent_rows),
        "roster": roster,
        "agents": agent_rows,
        "domains": domain_rows,
        "domain_weaver": domain_weaver,
        "codex_mounts": codex_mounts,
        "runs": runs,
        "communications": communications,
        "dispatcher": dispatcher,
        "starter_capsule": starter_capsule,
        "diagnostics": diagnostics,
        "settings": {
            "default_mode": "direct_codex",
            "prepare_endpoint": "/cockpit/agents/prepare",
            "start_endpoint": "/cockpit/agents/start",
            "cancel_endpoint": "/cockpit/agents/cancel",
            "result_endpoint": "/cockpit/agents/result",
            "status_endpoint": "/cockpit/agents/status",
            "default_target_root_id": "active_ion_control",
            "default_movement_class": "ION_KERNEL_CONTROL_MOVEMENT",
            "default_timeout_seconds": 1800,
            "proof_gate": "ion_submit_task_return context/template proof gates",
        },
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }
