"""Codex-native ION agent/domain mount projection.

ION owns the agent and domain truth. Codex CLI gets a generated working folder
that exposes that truth through native Codex surfaces: AGENTS.md,
.codex/config.toml, hooks, and local context cards.
"""
from __future__ import annotations

import json
import hashlib
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_agent_comms_directory import (
    CONTACT_CONTRACT_SCHEMA_ID,
    CONTACT_RELATIONSHIP_TAXONOMY,
    CONTACT_ROUTING_RULES,
    CONTACT_TEMPLATE_CONTRACTS,
    ROOM_CONTRACT_SCHEMA_ID,
    ROOM_REPORTING_RULES,
    ROOM_ROUTING_RULES,
    contact_groups_from_contacts,
    contact_relationship_tags,
)
from .ion_domain_weaver import (
    DOMAIN_WEAVER_PROJECTION_PATH,
    DOMAIN_WEAVER_PROMOTION_REVIEW_MD_PATH,
    DOMAIN_WEAVER_PROMOTION_REVIEW_PATH,
)

SCHEMA_ID = "ion.codex_agent_mount.v0_1"
MOUNTS_SCHEMA_ID = "ion.codex_agent_mounts.v0_1"
PORTABLE_CONTEXT_SCHEMA_ID = "ion.portable_agent_domain_context_capsule.v0_1"
PORTABLE_PACKAGE_SCHEMA_ID = "ion.portable_agent_domain_package.v0_1"
MOUNT_ROOT = Path("ION/05_context/current/codex_agent_mounts")
PORTABLE_PACKAGE_ROOT = Path("ION/05_context/current/portable_agent_domain_packages")
MOUNT_MANIFEST_NAME = "ION_AGENT_MOUNT_MANIFEST.json"
PORTABLE_PACKAGE_MANIFEST_NAME = "ION_PORTABLE_AGENT_PACKAGE.json"
ACTIVE_CONTEXT_PACKAGE_JSON = "ACTIVE_CONTEXT_PACKAGE.json"
ACTIVE_CONTEXT_PACKAGE_MD = "ACTIVE_CONTEXT_PACKAGE.md"
PORTABLE_CONTEXT_DIR = ".ion"
PORTABLE_CONTEXT_MANIFEST = "ION_CONTEXT_CAPSULE.yaml"
PORTABLE_MINI = "MINI.md"
PORTABLE_CAPSULE = "CAPSULE.md"
PORTABLE_LONG_HORIZON = "LONG_HORIZON.json"
PORTABLE_ROUTE = "ROUTE.json"
PORTABLE_DOMAIN = "DOMAIN.yaml"
PORTABLE_AGENT = "AGENT.yaml"
PORTABLE_RELATIONSHIPS = "RELATIONSHIPS.yaml"
PORTABLE_COMMUNICATIONS = "COMMUNICATIONS.json"
PORTABLE_ADDRESS_BOOK = "ADDRESS_BOOK.json"
MAX_CONTEXT_EXCERPT_CHARS = 1800
MAX_CONTEXT_DIR_SAMPLE = 16
MAX_CONTEXT_ZIP_SAMPLE = 20
MAX_PORTABLE_SOURCE_FILE_BYTES = 256_000
MAX_PORTABLE_SOURCE_DIR_FILES = 0
MAX_PORTABLE_SOURCE_DIR_SAMPLE = 24
DEFAULT_TASK_RUN_POLICY = {
    "schema_id": "ion.agent_comms.task_run_policy.v1",
    "default_limits": {
        "max_agents": 8,
        "max_workpacks": 8,
        "max_directives": 3,
        "max_pickups": 12,
        "max_graph_nodes": 180,
        "max_graph_edges": 260,
    },
    "observability": {
        "run_graph_schema_id": "ion.agent_comms.run_graph.v1",
        "policy_gate_schema_id": "ion.agent_comms.run_policy_gate.v1",
        "states": ["messages_delivered", "workpack_active", "response_observed", "blocked_by_policy", "limit_reached"],
        "evidence_chain": ["message", "directive", "workpack", "task_return", "synced_reply"],
    },
    "agent_decision_boundary": "Agents decide whether to communicate by writing visible messages or ion-agent-comms directive blocks. Automation only validates limits, routes packets, and projects evidence.",
    "production_authority": False,
    "live_execution_authority": False,
    "accepted_state_authority": False,
}

HOOKS = (
    ("SessionStart", "startup|resume", "ion_session_start_context.py", "Loading ION Codex agent mount context"),
    ("UserPromptSubmit", ".*", "ion_user_prompt_submit.py", "Syncing ION agent prompt route"),
    ("PreCompact", "manual|auto", "ion_precompact.py", "Checkpointing ION agent mount context"),
    ("PostCompact", "manual|auto", "ion_postcompact.py", "Verifying ION agent compact baton"),
    ("Stop", ".*", "ion_stop.py", "Recording ION agent turn receipt"),
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _safe_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")[:96] or "mount"


def _rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _resolve_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    return candidate


def _first_existing(root: Path, values: list[str]) -> str:
    for value in values:
        if value and (root / value).exists():
            return value
    return ""


def _domain_id(domain: Mapping[str, Any] | None) -> str:
    return str((domain or {}).get("domain_id") or "domain.unassigned").strip() or "domain.unassigned"


def _role_id(agent: Mapping[str, Any]) -> str:
    return str(agent.get("role_id") or agent.get("agent_id") or "role.unassigned").strip() or "role.unassigned"


def _display_name(agent: Mapping[str, Any]) -> str:
    return str(agent.get("display_name") or _role_id(agent).split(".")[-1]).strip() or "ION_AGENT"


def _primary_domain_for_agent(agent: Mapping[str, Any]) -> str:
    return str(agent.get("registry_primary_domain") or agent.get("primary_domain") or "").strip()


def _domain_candidates_for_agent(agent: Mapping[str, Any]) -> list[str]:
    candidates: list[str] = []
    primary = _primary_domain_for_agent(agent)
    if primary and not primary.startswith("NONE_DECLARED"):
        candidates.append(primary)
    for value in agent.get("registry_secondary_domains") or []:
        text = str(value or "").strip()
        if text and text not in candidates:
            candidates.append(text)
    if primary and primary not in candidates:
        candidates.append(primary)
    return candidates


def select_domain_for_agent(agent: Mapping[str, Any], domains: list[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    for primary in _domain_candidates_for_agent(agent):
        for domain in domains:
            if str(domain.get("domain_id") or "") == primary:
                return domain
    role_tokens = {
        str(agent.get("role_id") or "").split(".")[-1].upper(),
        str(agent.get("display_name") or "").replace(" ", "_").upper(),
    }
    for domain in domains:
        steward_class = str(domain.get("suggested_steward_class") or "").replace(" ", "_").upper()
        if steward_class and steward_class in role_tokens:
            return domain
    for domain in domains:
        if str(domain.get("domain_id") or "") != "domain.agent_communication_systems":
            return domain
    return domains[0] if domains else None


def build_codex_agent_mount_candidate(
    root: str | Path | None,
    agent: Mapping[str, Any],
    domain: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    role_id = _role_id(agent)
    domain_id = _domain_id(domain)
    mount_id = f"{_safe_slug(role_id)}__{_safe_slug(domain_id)}"
    mount_path = shell_root / MOUNT_ROOT / mount_id
    manifest_path = mount_path / MOUNT_MANIFEST_NAME
    agents_path = mount_path / "AGENTS.md"
    config_path = mount_path / ".codex" / "config.toml"
    portable_path = mount_path / PORTABLE_CONTEXT_DIR
    agent_card = _first_existing(shell_root, [str(agent.get("context_system_card") or ""), *[str(item) for item in agent.get("context_paths") or []]])
    domain_refs = [str(item) for item in (domain or {}).get("paths") or [] if str(item)]
    context_refs = []
    for value in [
        agent_card,
        *[str(item) for item in agent.get("context_paths") or []],
        *domain_refs,
        DOMAIN_WEAVER_PROJECTION_PATH.as_posix(),
        DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix(),
        DOMAIN_WEAVER_PROMOTION_REVIEW_MD_PATH.as_posix(),
    ]:
        if value and value not in context_refs:
            context_refs.append(value)
    command_preview = [
        "codex",
        "exec",
        "-C",
        mount_path.as_posix(),
        "--json",
        "--output-last-message",
        "<run>/final.md",
        "<objective>",
    ]
    return {
        "schema_id": SCHEMA_ID,
        "mount_id": mount_id,
        "agent_role_id": role_id,
        "agent_display_name": _display_name(agent),
        "domain_id": domain_id,
        "mount_root": MOUNT_ROOT.as_posix(),
        "mount_path": _rel(shell_root, mount_path),
        "mount_abspath": mount_path.as_posix(),
        "manifest_path": _rel(shell_root, manifest_path),
        "agents_md_path": _rel(shell_root, agents_path),
        "config_path": _rel(shell_root, config_path),
        "active_context_package_path": _rel(shell_root, mount_path / ACTIVE_CONTEXT_PACKAGE_JSON),
        "active_context_package_md_path": _rel(shell_root, mount_path / ACTIVE_CONTEXT_PACKAGE_MD),
        "portable_context_dir": _rel(shell_root, portable_path),
        "portable_context_manifest_path": _rel(shell_root, portable_path / PORTABLE_CONTEXT_MANIFEST),
        "portable_mini_path": _rel(shell_root, portable_path / PORTABLE_MINI),
        "portable_capsule_path": _rel(shell_root, portable_path / PORTABLE_CAPSULE),
        "portable_long_horizon_path": _rel(shell_root, portable_path / PORTABLE_LONG_HORIZON),
        "portable_route_path": _rel(shell_root, portable_path / PORTABLE_ROUTE),
        "portable_domain_path": _rel(shell_root, portable_path / PORTABLE_DOMAIN),
        "portable_agent_path": _rel(shell_root, portable_path / PORTABLE_AGENT),
        "portable_relationships_path": _rel(shell_root, portable_path / PORTABLE_RELATIONSHIPS),
        "portable_communications_path": _rel(shell_root, portable_path / PORTABLE_COMMUNICATIONS),
        "portable_address_book_path": _rel(shell_root, portable_path / PORTABLE_ADDRESS_BOOK),
        "portable_active_context_package_path": _rel(shell_root, portable_path / ACTIVE_CONTEXT_PACKAGE_JSON),
        "portable_active_context_package_md_path": _rel(shell_root, portable_path / ACTIVE_CONTEXT_PACKAGE_MD),
        "domain_weaver_projection_path": DOMAIN_WEAVER_PROJECTION_PATH.as_posix(),
        "domain_weaver_promotion_review_path": DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix(),
        "domain_weaver_promotion_review_markdown_path": DOMAIN_WEAVER_PROMOTION_REVIEW_MD_PATH.as_posix(),
        "agent_system_card_path": _rel(shell_root, mount_path / "AGENT_SYSTEM_CARD.md"),
        "domain_system_card_path": _rel(shell_root, mount_path / "DOMAIN_SYSTEM_CARD.md"),
        "agent_context_card": agent_card,
        "domain_refs": domain_refs,
        "context_refs": context_refs,
        "native_codex": {
            "launch_cwd": mount_path.as_posix(),
            "uses_project_agents_md": True,
            "uses_project_codex_config": True,
            "uses_portable_ion_context_capsule": True,
            "uses_shared_ion_hooks": True,
            "interactive_command_preview": ["codex", "-C", mount_path.as_posix()],
            "command_preview": command_preview,
            "prompt_visibility_probe": f"codex -C {json.dumps(mount_path.as_posix())} debug prompt-input '<probe>'",
        },
        "materialized": mount_path.is_dir(),
        "manifest_exists": manifest_path.is_file(),
        "agents_md_exists": agents_path.is_file(),
        "config_exists": config_path.is_file(),
        "active_context_package_exists": (mount_path / ACTIVE_CONTEXT_PACKAGE_JSON).is_file(),
        "active_context_package_md_exists": (mount_path / ACTIVE_CONTEXT_PACKAGE_MD).is_file(),
        "portable_context_exists": portable_path.is_dir(),
        "portable_context_manifest_exists": (portable_path / PORTABLE_CONTEXT_MANIFEST).is_file(),
        "portable_communications_exists": (portable_path / PORTABLE_COMMUNICATIONS).is_file(),
        "portable_address_book_exists": (portable_path / PORTABLE_ADDRESS_BOOK).is_file(),
        "portable_active_context_package_exists": (portable_path / ACTIVE_CONTEXT_PACKAGE_JSON).is_file(),
        "portable_active_context_package_md_exists": (portable_path / ACTIVE_CONTEXT_PACKAGE_MD).is_file(),
        "hook_strategy": "generated config calls shared active-root ION hooks with absolute paths",
        "authority": {
            "candidate_mount_only": True,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def build_codex_agent_mounts_projection(
    root: str | Path | None,
    agents: list[Mapping[str, Any]],
    domains: list[Mapping[str, Any]],
) -> dict[str, Any]:
    rows = [build_codex_agent_mount_candidate(root, agent, select_domain_for_agent(agent, domains)) for agent in agents]
    return {
        "schema_id": MOUNTS_SCHEMA_ID,
        "generated_at": _now(),
        "mount_count": len(rows),
        "materialized_count": sum(1 for row in rows if row.get("materialized")),
        "prompt_visibility_proven_count": 0,
        "mount_root": MOUNT_ROOT.as_posix(),
        "mounts": rows,
        "policy": "ION compiles agent/domain truth into Codex-native cwd/config/AGENTS surfaces; generated mounts are candidate runtime carriers only.",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def _toml_multiline(value: str) -> str:
    return '"""' + value.replace('"""', '\\"\\"\\"') + '"""'


def _config_text(root: Path, mount: Mapping[str, Any]) -> str:
    package_root = root / "ION/04_packages"
    developer_instructions = "\n".join(
        [
            "ION Codex agent/domain mount guidance:",
            f"- Agent: {mount.get('agent_display_name')} ({mount.get('agent_role_id')}).",
            f"- Domain: {mount.get('domain_id')}.",
            f"- Mount manifest: {mount.get('manifest_path')}.",
            f"- Active ION root: {root}.",
            "- This is a generated Codex-native mount; ION remains the control plane and source of authority.",
            "- Read ION_AGENT_MOUNT_MANIFEST.json, AGENTS.md, .ion/ION_CONTEXT_CAPSULE.yaml, .ion/ACTIVE_CONTEXT_PACKAGE.md, .ion/COMMUNICATIONS.json, .ion/ADDRESS_BOOK.json, AGENT_SYSTEM_CARD.md, and DOMAIN_SYSTEM_CARD.md before material work.",
            f"- Domain Weaver projection: {DOMAIN_WEAVER_PROJECTION_PATH.as_posix()}. Use it to see which domains have capsule/comms-backed agents and where gaps remain.",
            f"- Domain Weaver promotion review: {DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()}. Use it to see candidate domain registry drafts without treating them as accepted state.",
            "- Raw Codex output is candidate only until task-return proof, receipts, and settlement gates complete.",
            "- No production, live execution, accepted-state, secrets, deploy, push, or destructive authority is granted by this mount.",
        ]
    )
    hook_blocks = []
    for event, matcher, script, status in HOOKS:
        hook_path = root / ".codex" / "hooks" / script
        hook_blocks.append(
            "\n".join(
                [
                    f"[[hooks.{event}]]",
                    f'matcher = "{matcher}"',
                    "",
                    f"[[hooks.{event}.hooks]]",
                    'type = "command"',
                    f"command = 'python3 \"{hook_path.as_posix()}\"'",
                    "timeout = 10",
                    f'statusMessage = "{status}"',
                ]
            )
        )
    return "\n\n".join(
        [
            "# Generated ION Codex agent mount config. Do not store secrets here.",
            'sandbox_mode = "workspace-write"',
            'approval_policy = "on-request"',
            f"developer_instructions = {_toml_multiline(developer_instructions)}",
            "[features]\nhooks = true",
            "\n".join(
                [
                    "[sandbox_workspace_write]",
                    "network_access = false",
                    "writable_roots = [",
                    f'  "{root.as_posix()}",',
                    f'  "{(root / MOUNT_ROOT).as_posix()}",',
                    "]",
                ]
            ),
            "\n".join(
                [
                    "[mcp_servers.ion_local]",
                    "enabled = true",
                    "required = false",
                    'command = "python3"',
                    f'args = ["-S", "-m", "kernel.ion_mcp_local_bridge", "--ion-root", "{root.as_posix()}", "--stdio"]',
                    f'cwd = "{root.as_posix()}"',
                    "startup_timeout_sec = 10",
                    "tool_timeout_sec = 60",
                    'enabled_tools = ["ion.status", "ion.boot_packet", "ion.horizon.current", "ion.receipts.list", "ion.tools.list"]',
                    f'env = {{ PYTHONPATH = "{package_root.as_posix()}", PYTHONDONTWRITEBYTECODE = "1" }}',
                ]
            ),
            *hook_blocks,
            "",
        ]
    )


def _agents_md_text(mount: Mapping[str, Any]) -> str:
    refs = "\n".join(f"- {ref}" for ref in mount.get("context_refs") or []) or "- none"
    return "\n".join(
        [
            "# ION Codex Agent Mount",
            "",
            f"Agent: {mount.get('agent_display_name')} ({mount.get('agent_role_id')})",
            f"Domain: {mount.get('domain_id')}",
            f"Manifest: {MOUNT_MANIFEST_NAME}",
            "",
            "## Operating Rules",
            "",
            "- Operate only as the Codex carrier for this generated ION agent/domain mount.",
            "- Treat ION_AGENT_MOUNT_MANIFEST.json as the local mount index.",
            f"- Read {PORTABLE_CONTEXT_DIR}/{PORTABLE_CONTEXT_MANIFEST} first; it is the folder-local ION context capsule for this mount.",
            f"- Read {PORTABLE_CONTEXT_DIR}/{ACTIVE_CONTEXT_PACKAGE_MD} before material work; it is the mount's compiled working context package.",
            f"- Read {PORTABLE_CONTEXT_DIR}/{PORTABLE_AGENT}, {PORTABLE_CONTEXT_DIR}/{PORTABLE_DOMAIN}, and {PORTABLE_CONTEXT_DIR}/{PORTABLE_RELATIONSHIPS} to understand agent/domain relationships.",
            f"- Read {PORTABLE_CONTEXT_DIR}/{PORTABLE_COMMUNICATIONS} to see available agents, channels, and automation comms limits.",
            f"- Read {PORTABLE_CONTEXT_DIR}/{PORTABLE_ADDRESS_BOOK} to understand nearest peers, reviewers, escalation roles, relationship tags, and when each contact should be used.",
            f"- Consult the active-root Domain Weaver projection at `{DOMAIN_WEAVER_PROJECTION_PATH.as_posix()}` when deciding which domain/agent should receive a routed packet.",
            f"- Consult the active-root Domain Weaver promotion review at `{DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()}` before treating candidate domains as registry-promotion drafts.",
            "- Read AGENT_SYSTEM_CARD.md and DOMAIN_SYSTEM_CARD.md before material work.",
            "- Use the active ION root as authority; this folder is a native Codex launch surface, not a separate source of truth.",
            "- Raw output is candidate only until ION task-return proof, receipts, and settlement gates complete.",
            "- No production, live execution, accepted-state, secrets, deploy, push, or destructive authority is granted here.",
            "",
            "## Agent Communication",
            "",
            f"- Load {PORTABLE_CONTEXT_DIR}/{PORTABLE_COMMUNICATIONS} and {PORTABLE_CONTEXT_DIR}/{PORTABLE_ADDRESS_BOOK} before deciding whether another agent is needed.",
            "- Contact another agent with a visible @agent alias in Team Comms or by emitting an explicit fenced `ion-agent-comms` directive block.",
            "- Include source_refs that prove why the other agent is needed; do not request accepted state, production action, live execution, secrets, deploys, pushes, or destructive work.",
            "- Automation is only the courier/limiter: it validates task-run policy, prepares/routes workpacks, and projects return evidence into the run graph.",
            "- Watchable run evidence is message -> directive -> workpack -> task_return -> synced_reply; absence of a return means no agent response has been observed.",
            "",
            "## Context Refs",
            "",
            refs,
            "",
        ]
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _context_ref_record(root: Path, ref: str) -> dict[str, Any]:
    ref = str(ref or "").strip()
    record: dict[str, Any] = {
        "path": ref,
        "exists": False,
        "kind": "missing",
    }
    if not ref:
        return record
    rel = Path(ref)
    if rel.is_absolute() or ".." in rel.parts:
        record["kind"] = "unsafe_or_external"
        return record
    path = root / rel
    if path.is_dir():
        sample = []
        for item in sorted(path.rglob("*")):
            if item.is_file():
                sample.append(_rel(root, item))
            if len(sample) >= MAX_CONTEXT_DIR_SAMPLE:
                break
        record.update(
            {
                "exists": True,
                "kind": "directory",
                "sample_files": sample,
            }
        )
        return record
    if not path.is_file():
        return record
    record.update(
        {
            "exists": True,
            "kind": "file",
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        }
    )
    if path.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
            record["kind"] = "zip_witness"
            record["zip_entry_count"] = len(names)
            record["zip_entries_sample"] = names[:MAX_CONTEXT_ZIP_SAMPLE]
        except zipfile.BadZipFile:
            record["zip_error"] = "bad_zip_file"
        return record
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        text = ""
    record["excerpt"] = text[:MAX_CONTEXT_EXCERPT_CHARS].strip()
    return record


def _clean_lane_id(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return re.sub(r"[^a-zA-Z0-9_.:-]+", "_", text)


def _lane_rows_from_record(record: Mapping[str, Any], *, source: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    raw_values: list[Any] = [
        record.get("lane_id"),
        record.get("lane"),
        record.get("invocation_lane"),
        record.get("domain_weaver_lane_id"),
        record.get("queue_lane"),
        record.get("work_lane"),
    ]
    for key in ("lane_ids", "lanes", "invocation_lanes", "queue_lanes", "work_lanes"):
        value = record.get(key)
        if isinstance(value, list):
            raw_values.extend(value)
    for key in ("lane_metadata", "worker_lanes", "domain_weaver_lanes"):
        value = record.get(key)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, Mapping):
                    raw_values.extend([item.get("lane_id"), item.get("lane"), item.get("invocation_lane")])
                else:
                    raw_values.append(item)
    for value in raw_values:
        lane_id = _clean_lane_id(value)
        if lane_id:
            rows.append({"lane_id": lane_id, "source": source})
    return rows


def _active_context_lane_metadata(
    mount: Mapping[str, Any],
    agent: Mapping[str, Any],
    domain: Mapping[str, Any] | None,
) -> tuple[list[str], list[dict[str, str]]]:
    rows: list[dict[str, str]] = []
    rows.extend(_lane_rows_from_record(mount, source="mount"))
    rows.extend(_lane_rows_from_record(agent, source="agent"))
    if domain:
        rows.extend(_lane_rows_from_record(domain, source="domain"))
    lane_ids: list[str] = []
    metadata: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        lane_id = row["lane_id"]
        if lane_id in seen:
            continue
        seen.add(lane_id)
        lane_ids.append(lane_id)
        metadata.append(row)
    return lane_ids, metadata


def _active_context_package(
    root: Path,
    mount: Mapping[str, Any],
    agent: Mapping[str, Any],
    domain: Mapping[str, Any] | None,
) -> dict[str, Any]:
    refs = [str(ref) for ref in mount.get("context_refs") or []]
    records = [_context_ref_record(root, ref) for ref in refs]
    lane_ids, lane_metadata = _active_context_lane_metadata(mount, agent, domain)
    return {
        "schema_id": "ion.codex_agent_mount_active_context_package.v0_1",
        "generated_at": _now(),
        "mount_id": mount.get("mount_id"),
        "agent_role_id": mount.get("agent_role_id"),
        "agent_display_name": mount.get("agent_display_name"),
        "domain_id": mount.get("domain_id"),
        "context_system_card": mount.get("agent_context_card"),
        "package_strategy": agent.get("package_strategy"),
        "default_active_package_class": agent.get("default_active_package_class"),
        "write_posture": agent.get("write_posture") or "none",
        "domain_purpose": (domain or {}).get("purpose"),
        "domain_paths": list((domain or {}).get("paths") or []),
        "lane_ids": lane_ids,
        "lane_metadata": lane_metadata,
        "lane_metadata_policy": {
            "explicit_lane_metadata_only": True,
            "missing_lane_metadata_blocks_lane_bound_worker_start": True,
            "no_silent_fallback_to_domain_or_role_match": True,
        },
        "context_refs": records,
        "context_ref_count": len(records),
        "existing_context_ref_count": sum(1 for item in records if item.get("exists")),
        "missing_context_refs": [item["path"] for item in records if not item.get("exists")],
        "policy": {
            "active_package_is_working_context": True,
            "mini_capsule_are_witness_inputs_not_primary_authority": True,
            "raw_codex_output_is_candidate_until_receipts_and_settlement": True,
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


def _active_context_package_md(package: Mapping[str, Any]) -> str:
    lines = [
        "# Active Context Package",
        "",
        f"agent: {package.get('agent_display_name')} ({package.get('agent_role_id')})",
        f"domain: {package.get('domain_id')}",
        f"class: {package.get('default_active_package_class')}",
        f"write_posture: {package.get('write_posture')}",
        f"lane_ids: {', '.join(package.get('lane_ids') or []) if package.get('lane_ids') else '[]'}",
        "",
        "## Policy",
        "",
        "- This is the compiled working context package for the generated Codex agent mount.",
        "- MINI/CAPSULE are witness inputs, not primary context authority.",
        "- Raw Codex output is candidate until proof receipts and settlement gates complete.",
        "- No production, live execution, accepted-state, or secrets authority is granted.",
        "",
        "## Context Refs",
        "",
    ]
    for item in package.get("context_refs") or []:
        if not isinstance(item, Mapping):
            continue
        status = "present" if item.get("exists") else "missing"
        lines.append(f"### {item.get('path')}")
        lines.append("")
        lines.append(f"- status: {status}")
        lines.append(f"- kind: {item.get('kind')}")
        if item.get("sha256"):
            lines.append(f"- sha256: {item.get('sha256')}")
        if item.get("bytes") is not None:
            lines.append(f"- bytes: {item.get('bytes')}")
        if item.get("sample_files"):
            lines.append("- sample_files:")
            lines.extend(f"  - {value}" for value in item.get("sample_files") or [])
        if item.get("zip_entries_sample"):
            lines.append("- zip_entries_sample:")
            lines.extend(f"  - {value}" for value in item.get("zip_entries_sample") or [])
        excerpt = str(item.get("excerpt") or "").strip()
        if excerpt:
            lines.extend(["", "```text", excerpt, "```"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    return json.dumps(str(value))


def _yaml_list(key: str, values: list[Any], *, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if not values:
        return [f"{prefix}{key}: []"]
    lines = [f"{prefix}{key}:"]
    lines.extend(f"{prefix}  - {_yaml_scalar(value)}" for value in values)
    return lines


def _yaml_mapping(key: str, values: Mapping[str, Any], *, indent: int = 0) -> list[str]:
    prefix = " " * indent
    if not values:
        return [f"{prefix}{key}: {{}}"]
    lines = [f"{prefix}{key}:"]
    for item_key in sorted(values):
        value = values[item_key]
        if isinstance(value, list):
            lines.extend(_yaml_list(str(item_key), value, indent=indent + 2))
        elif isinstance(value, Mapping):
            lines.extend(_yaml_mapping(str(item_key), value, indent=indent + 2))
        else:
            lines.append(f"{prefix}  {item_key}: {_yaml_scalar(value)}")
    return lines


def _yaml_document(values: Mapping[str, Any]) -> str:
    lines: list[str] = []
    for item_key in sorted(values):
        value = values[item_key]
        if isinstance(value, list):
            lines.extend(_yaml_list(str(item_key), value))
        elif isinstance(value, Mapping):
            lines.extend(_yaml_mapping(str(item_key), value))
        else:
            lines.append(f"{item_key}: {_yaml_scalar(value)}")
    return "\n".join(lines).rstrip() + "\n"


def _clean_list(values: Any) -> list[str]:
    if not isinstance(values, list | tuple):
        return []
    cleaned: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _portable_local_paths(mount: Mapping[str, Any]) -> dict[str, str]:
    return {
        "manifest": str(mount.get("manifest_path") or ""),
        "agents_md": str(mount.get("agents_md_path") or ""),
        "codex_config": str(mount.get("config_path") or ""),
        "portable_context_manifest": str(mount.get("portable_context_manifest_path") or ""),
        "portable_mini": str(mount.get("portable_mini_path") or ""),
        "portable_capsule": str(mount.get("portable_capsule_path") or ""),
        "portable_long_horizon": str(mount.get("portable_long_horizon_path") or ""),
        "portable_route": str(mount.get("portable_route_path") or ""),
        "portable_domain": str(mount.get("portable_domain_path") or ""),
        "portable_agent": str(mount.get("portable_agent_path") or ""),
        "portable_relationships": str(mount.get("portable_relationships_path") or ""),
        "portable_communications": str(mount.get("portable_communications_path") or ""),
        "portable_address_book": str(mount.get("portable_address_book_path") or ""),
        "portable_active_context_package": str(mount.get("portable_active_context_package_path") or ""),
        "portable_active_context_package_md": str(mount.get("portable_active_context_package_md_path") or ""),
        "domain_weaver_projection": str(mount.get("domain_weaver_projection_path") or DOMAIN_WEAVER_PROJECTION_PATH.as_posix()),
        "domain_weaver_promotion_review": str(mount.get("domain_weaver_promotion_review_path") or DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()),
        "domain_weaver_promotion_review_markdown": str(
            mount.get("domain_weaver_promotion_review_markdown_path") or DOMAIN_WEAVER_PROMOTION_REVIEW_MD_PATH.as_posix()
        ),
    }


def _portable_relationships(agent: Mapping[str, Any], domain: Mapping[str, Any] | None) -> dict[str, Any]:
    domain = dict(domain or {})
    primary = _primary_domain_for_agent(agent) or str(domain.get("domain_id") or "domain.unassigned")
    secondary = _clean_list(agent.get("registry_secondary_domains"))
    return {
        "primary_domain": primary,
        "selected_mount_domain": str(domain.get("domain_id") or "domain.unassigned"),
        "secondary_domains": secondary,
        "template_bindings": _clean_list(agent.get("template_bindings") or agent.get("primary_templates")),
        "source_refs": _clean_list(agent.get("source_refs")),
        "domain_paths": _clean_list(domain.get("paths")),
        "domain_steward_class": domain.get("suggested_steward_class") or domain.get("steward_class") or "",
        "dependency_policy": "folder-local capsule declares relationships; ION registries remain authority.",
    }


def _profile_domain_ids(profile: Mapping[str, Any]) -> list[str]:
    values: list[str] = []
    primary = str(profile.get("primary_domain") or "").strip()
    if primary and primary not in values:
        values.append(primary)
    for value in profile.get("domain_ids") or []:
        text = str(value or "").strip()
        if text and text not in values:
            values.append(text)
    return values


def _portable_address_book(
    mount: Mapping[str, Any],
    agent: Mapping[str, Any],
    domain: Mapping[str, Any] | None,
    communication_directory: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    directory = dict(communication_directory or {})
    contact_contract = directory.get("contact_contract") if isinstance(directory.get("contact_contract"), Mapping) else {}
    room_contract = directory.get("room_contract") if isinstance(directory.get("room_contract"), Mapping) else {}
    role_id = str(mount.get("agent_role_id") or _role_id(agent))
    selected_domain = str(mount.get("domain_id") or (domain or {}).get("domain_id") or "")
    agents_by_role = directory.get("agents_by_role") if isinstance(directory.get("agents_by_role"), Mapping) else {}
    own_profile = dict(agents_by_role.get(role_id) or {}) if isinstance(agents_by_role, Mapping) else {}
    if not own_profile:
        own_profile = {
            "role_id": role_id,
            "display_name": mount.get("agent_display_name"),
            "mention": f"@{role_id}",
            "primary_domain": _primary_domain_for_agent(agent) or selected_domain,
            "domain_ids": [selected_domain] if selected_domain else [],
            "can_initiate_comms": True,
            "can_receive_workpacks": bool(agent.get("invocable")),
            "default_channels": ["team", "handoffs", "signals"],
        }
    own_domains = _profile_domain_ids(own_profile)
    for value in [selected_domain, *_clean_list(agent.get("registry_secondary_domains"))]:
        if value and value not in own_domains:
            own_domains.append(value)

    contacts_by_role = contact_contract.get("contacts_by_role") if isinstance(contact_contract.get("contacts_by_role"), Mapping) else {}
    contract_contacts = contacts_by_role.get(role_id) if isinstance(contacts_by_role, Mapping) else None
    if isinstance(contract_contacts, list):
        contacts = [dict(row) for row in contract_contacts if isinstance(row, Mapping)]
    else:
        contacts = []
        for row in directory.get("agents") or []:
            if not isinstance(row, Mapping) or not row.get("available_for_comms"):
                continue
            contact_role = str(row.get("role_id") or "")
            tags = contact_relationship_tags(role_id, row, own_domains=own_domains, selected_domain=selected_domain)
            if "self" in tags:
                continue
            contacts.append(
                {
                    "role_id": contact_role,
                    "display_name": row.get("display_name"),
                    "mention": row.get("mention") or f"@{contact_role}",
                    "aliases": list(row.get("aliases") or []),
                    "primary_domain": row.get("primary_domain"),
                    "domain_ids": _profile_domain_ids(row),
                    "relationship_tags": tags,
                    "default_channels": list(row.get("default_channels") or []),
                    "can_receive_workpacks": bool(row.get("can_receive_workpacks")),
                    "template_ids": list(row.get("start_comms_template_ids") or row.get("handoff_template_ids") or []),
                    "communication_contract": dict(row.get("communication_contract") or {}),
                }
            )

    contact_groups_by_role = contact_contract.get("contact_groups_by_role") if isinstance(contact_contract.get("contact_groups_by_role"), Mapping) else {}
    contract_groups = contact_groups_by_role.get(role_id) if isinstance(contact_groups_by_role, Mapping) else None
    contact_groups = dict(contract_groups) if isinstance(contract_groups, Mapping) else contact_groups_from_contacts(contacts)
    routing_rules = (
        list(contact_contract.get("routing_rules") or [])
        if isinstance(contact_contract.get("routing_rules"), list)
        else list(CONTACT_ROUTING_RULES)
    )
    relationship_taxonomy = (
        list(contact_contract.get("relationship_taxonomy") or [])
        if isinstance(contact_contract.get("relationship_taxonomy"), list)
        else list(CONTACT_RELATIONSHIP_TAXONOMY)
    )
    limits = dict((directory.get("automation_comms_policy") or {}).get("limits") or {})
    return {
        "schema_id": "ion.portable_agent_address_book.v0_1",
        "generated_at": _now(),
        "contact_contract_schema_id": contact_contract.get("schema_id") or CONTACT_CONTRACT_SCHEMA_ID,
        "contact_contract_ref": str(
            contact_contract.get("routing_source_of_truth")
            or f"{directory.get('directory_path') or 'ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json'}#contact_contract"
        ),
        "room_contract_schema_id": room_contract.get("schema_id") or ROOM_CONTRACT_SCHEMA_ID,
        "room_contract_ref": str(
            room_contract.get("routing_source_of_truth")
            or f"{directory.get('directory_path') or 'ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json'}#room_contract"
        ),
        "mount_id": mount.get("mount_id"),
        "agent_role_id": role_id,
        "agent_display_name": mount.get("agent_display_name"),
        "selected_domain_id": selected_domain,
        "own_profile": own_profile,
        "own_domain_ids": own_domains,
        "summary": {
            "contact_count": len(contacts),
            "selected_domain_peer_count": len(contact_groups["selected_domain_peers"]),
            "shared_domain_peer_count": len(contact_groups["shared_domain_peers"]),
            "review_contact_count": len(contact_groups["review"]),
            "implementation_runtime_contact_count": len(contact_groups["implementation_runtime"]),
            "context_continuity_contact_count": len(contact_groups["context_continuity"]),
            "room_contract_room_count": room_contract.get("room_count", 0),
        },
        "contacts": contacts,
        "contact_groups": contact_groups,
        "routing_rules": routing_rules,
        "situation_map": {
            "domain_weaver_projection_path": str(mount.get("domain_weaver_projection_path") or DOMAIN_WEAVER_PROJECTION_PATH.as_posix()),
            "domain_weaver_promotion_review_path": str(
                mount.get("domain_weaver_promotion_review_path") or DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()
            ),
            "shared_directory_path": str(directory.get("directory_path") or "ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json"),
            "contact_contract_schema_id": contact_contract.get("schema_id") or CONTACT_CONTRACT_SCHEMA_ID,
            "contact_contract_ref": str(
                contact_contract.get("routing_source_of_truth")
                or f"{directory.get('directory_path') or 'ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json'}#contact_contract"
            ),
            "room_contract_schema_id": room_contract.get("schema_id") or ROOM_CONTRACT_SCHEMA_ID,
            "room_contract_ref": str(
                room_contract.get("routing_source_of_truth")
                or f"{directory.get('directory_path') or 'ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json'}#room_contract"
            ),
            "current_domain_id": selected_domain,
            "relationship_taxonomy": relationship_taxonomy,
            "room_routing_rules": list(room_contract.get("routing_rules") or ROOM_ROUTING_RULES),
            "room_reporting_rules": list(room_contract.get("reporting_rules") or ROOM_REPORTING_RULES),
            "room_context_loading": dict(room_contract.get("context_loading") or {}),
            "proof_chain": ["message", "directive", "workpack", "task_return", "synced_reply"],
            "agent_decision_rule": "Use visible @mentions for ordinary coordination. Emit a fenced ion-agent-comms directive only when another agent should receive a routed workpack or make a specialist decision.",
            "automation_role": "Automation validates limits and carries packets; it does not decide which agent is needed.",
        },
        "limits": limits,
        "authority": {
            "candidate_mount_only": True,
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


def _portable_communications(
    mount: Mapping[str, Any],
    agent: Mapping[str, Any],
    domain: Mapping[str, Any] | None,
    communication_directory: Mapping[str, Any] | None = None,
    address_book: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    directory = dict(communication_directory or {})
    contact_contract = directory.get("contact_contract") if isinstance(directory.get("contact_contract"), Mapping) else {}
    room_contract = directory.get("room_contract") if isinstance(directory.get("room_contract"), Mapping) else {}
    role_id = str(mount.get("agent_role_id") or _role_id(agent))
    agents_by_role = directory.get("agents_by_role") if isinstance(directory.get("agents_by_role"), Mapping) else {}
    own_profile = dict(agents_by_role.get(role_id) or {}) if isinstance(agents_by_role, Mapping) else {}
    if not own_profile:
        own_profile = {
            "role_id": role_id,
            "display_name": mount.get("agent_display_name"),
            "available_for_comms": True,
            "primary_domain": _primary_domain_for_agent(agent) or str((domain or {}).get("domain_id") or ""),
            "domain_ids": [str((domain or {}).get("domain_id") or mount.get("domain_id") or "")],
            "inbox_path": f"ION/05_context/current/agent_comms/inbox/{role_id.replace('role.', 'role_')}",
            "outbox_path": f"ION/05_context/current/agent_comms/outbox/{role_id.replace('role.', 'role_')}",
            "default_channels": ["team", "handoffs", "signals"],
            "can_initiate_comms": True,
            "can_receive_workpacks": bool(agent.get("invocable")),
            "automation_comms_allowed": True,
        }
    available_agents = [
        {
            "role_id": row.get("role_id"),
            "display_name": row.get("display_name"),
            "aliases": list(row.get("aliases") or []),
            "mention": row.get("mention"),
            "available_for_comms": bool(row.get("available_for_comms")),
            "primary_domain": row.get("primary_domain"),
            "default_channels": list(row.get("default_channels") or []),
            "can_receive_workpacks": bool(row.get("can_receive_workpacks")),
            "communication_contract": dict(row.get("communication_contract") or {}),
        }
        for row in list(directory.get("agents") or [])
        if isinstance(row, Mapping) and row.get("available_for_comms")
    ]
    return {
        "schema_id": "ion.portable_agent_communications.v0_1",
        "generated_at": _now(),
        "mount_id": mount.get("mount_id"),
        "agent_role_id": role_id,
        "domain_id": mount.get("domain_id"),
        "own_profile": own_profile,
        "address_book_path": f"{PORTABLE_CONTEXT_DIR}/{PORTABLE_ADDRESS_BOOK}",
        "address_book_summary": dict((address_book or {}).get("summary") or {}),
        "contact_groups": dict((address_book or {}).get("contact_groups") or {}),
        "available_agents": available_agents,
        "available_agent_count": len(available_agents),
        "channels": list(directory.get("channels") or []),
        "contact_contract": {
            "schema_id": contact_contract.get("schema_id") or CONTACT_CONTRACT_SCHEMA_ID,
            "source_directory_path": contact_contract.get("source_directory_path")
            or str(directory.get("directory_path") or "ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json"),
            "routing_source_of_truth": contact_contract.get("routing_source_of_truth") or "COMMUNICATION_DIRECTORY.json#contact_contract",
            "agent_count": contact_contract.get("agent_count"),
            "available_agent_count": contact_contract.get("available_agent_count"),
            "contact_edge_count": contact_contract.get("contact_edge_count"),
            "routing_rule_count": len(list(contact_contract.get("routing_rules") or CONTACT_ROUTING_RULES)),
            "template_contract_count": len(dict(contact_contract.get("template_contracts") or CONTACT_TEMPLATE_CONTRACTS)),
            "agent_decision_boundary": contact_contract.get("agent_decision_boundary"),
        },
        "room_contract": {
            "schema_id": room_contract.get("schema_id") or ROOM_CONTRACT_SCHEMA_ID,
            "source_directory_path": room_contract.get("source_directory_path")
            or str(directory.get("directory_path") or "ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json"),
            "routing_source_of_truth": room_contract.get("routing_source_of_truth") or "COMMUNICATION_DIRECTORY.json#room_contract",
            "owner_domain_id": room_contract.get("owner_domain_id"),
            "recommended_owner_role": room_contract.get("recommended_owner_role"),
            "room_count": room_contract.get("room_count"),
            "room_kind_count": len(list(room_contract.get("room_kinds") or [])),
            "routing_rule_count": len(list(room_contract.get("routing_rules") or ROOM_ROUTING_RULES)),
            "reporting_rule_count": len(list(room_contract.get("reporting_rules") or ROOM_REPORTING_RULES)),
            "context_loading": dict(room_contract.get("context_loading") or {}),
            "agent_decision_boundary": room_contract.get("agent_decision_boundary"),
        },
        "routing_rules": list(contact_contract.get("routing_rules") or CONTACT_ROUTING_RULES),
        "template_contracts": dict(contact_contract.get("template_contracts") or CONTACT_TEMPLATE_CONTRACTS),
        "rooms_by_id": dict(room_contract.get("rooms_by_id") or {}),
        "room_routing_rules": list(room_contract.get("routing_rules") or ROOM_ROUTING_RULES),
        "room_reporting_rules": list(room_contract.get("reporting_rules") or ROOM_REPORTING_RULES),
        "automation_comms_policy": dict(directory.get("automation_comms_policy") or {}),
        "task_run_policy": dict(directory.get("task_run_policy") or DEFAULT_TASK_RUN_POLICY),
        "shared_directory_path": str(directory.get("directory_path") or "ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json"),
        "domain_weaver": {
            "projection_path": str(mount.get("domain_weaver_projection_path") or DOMAIN_WEAVER_PROJECTION_PATH.as_posix()),
            "promotion_review_path": str(mount.get("domain_weaver_promotion_review_path") or DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()),
            "promotion_review_markdown_path": str(
                mount.get("domain_weaver_promotion_review_markdown_path") or DOMAIN_WEAVER_PROMOTION_REVIEW_MD_PATH.as_posix()
            ),
            "agent_role_id": role_id,
            "domain_id": mount.get("domain_id"),
            "usage_rule": "Read the active-root projection before routing a specialist packet. Read the promotion review before treating candidate domains as registry-promotion drafts.",
            "invented_agent_policy": "Only agents present in the projection/communication directory are routable.",
            "promotion_authority_boundary": "Promotion review drafts are candidate-only and do not write active registry truth or accepted ION state.",
        },
        "start_comms": {
            "active_root_endpoint": "/cockpit/agents/spawn-template",
            "task_run_start_endpoint": "/cockpit/agents/comms/run/start",
            "task_run_pickup_endpoint": "/cockpit/agents/comms/run/pickup",
            "task_run_audit_endpoint": "/cockpit/agents/comms/run/audit",
            "automation_pickup_action": "agent_comms.process_directives",
            "directive_schema_id": "ion.agent_comms.directive.v1",
            "directive_fence": "ion-agent-comms",
            "supported_dispatch_modes": ["comms_only", "prepare_workpack", "queue_workpack", "start_workpack"],
            "packet_bus_root": "ION/05_context/current/agent_comms",
            "local_inbox": f"{PORTABLE_CONTEXT_DIR}/inbox",
            "local_outbox": f"{PORTABLE_CONTEXT_DIR}/outbox",
            "default_to_role": "role.steward",
            "required_packet_fields": ["from_role", "to_roles", "message_kind", "subject", "body", "source_refs"],
            "agent_initiated_rule": "The agent decides when to communicate by emitting an explicit ion-agent-comms directive block in its own output; automation only picks up that block and routes it through templates/broker.",
            "task_run_policy": "Task runs are operator-approved bounded wrappers around real comms and explicit directive pickup. They are watchable in Team Comms and do not simulate replies.",
            "run_graph_policy": "Every run is projected as evidence nodes/edges: message -> directive -> workpack -> task_return -> synced_reply. Only real return/message artifacts count as responses.",
            "domain_weaver_projection_path": str(mount.get("domain_weaver_projection_path") or DOMAIN_WEAVER_PROJECTION_PATH.as_posix()),
            "domain_weaver_promotion_review_path": str(
                mount.get("domain_weaver_promotion_review_path") or DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()
            ),
            "mention_syntax": "@agent_alias",
            "agent_to_agent_rule": "Use @aliases for normal visible comms; use a fenced ion-agent-comms directive only when a workpack or routed specialist decision is needed.",
            "example_directive": {
                "schema_id": "ion.agent_comms.directive.v1",
                "from_role": role_id,
                "agent": "role.ionologist",
                "template_id": "agent_workpack_decision",
                "dispatch_mode": "queue_workpack",
                "objective": "Review this workpack and return a bounded decision.",
                "body": "Use the attached context refs and answer through the required return contract.",
                "source_refs": [".ion/ACTIVE_CONTEXT_PACKAGE.md"],
            },
        },
        "policy": "Communication is durable packet exchange plus optional broker-prepared workpacks. This file is a routing directory and directive format guide, not a multi-agent runtime or independent decider.",
        "agent_decision_boundary": "This mounted agent decides when to ask another agent by writing visible comms or a directive. Automation validates policy and carries packets; it does not decide on the agent's behalf.",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def _portable_context_manifest_text(
    root: Path,
    mount: Mapping[str, Any],
    agent: Mapping[str, Any],
    domain: Mapping[str, Any] | None,
    context_package: Mapping[str, Any],
    communications: Mapping[str, Any],
) -> str:
    relationships = _portable_relationships(agent, domain)
    lines = [
        f"schema_id: {_yaml_scalar(PORTABLE_CONTEXT_SCHEMA_ID)}",
        f"generated_at: {_yaml_scalar(_now())}",
        'capsule_kind: "agent_domain_folder"',
        'folder_role: "codex_native_agent_domain_mount"',
        f"active_ion_root: {_yaml_scalar(root.as_posix())}",
        f"mount_id: {_yaml_scalar(mount.get('mount_id'))}",
        f"agent_role_id: {_yaml_scalar(mount.get('agent_role_id'))}",
        f"agent_display_name: {_yaml_scalar(mount.get('agent_display_name'))}",
        f"domain_id: {_yaml_scalar(mount.get('domain_id'))}",
        f"context_package_class: {_yaml_scalar(context_package.get('default_active_package_class'))}",
        f"context_ref_count: {_yaml_scalar(context_package.get('context_ref_count'))}",
        f"existing_context_ref_count: {_yaml_scalar(context_package.get('existing_context_ref_count'))}",
        "authority:",
        "  candidate_mount_only: true",
        "  production_authority: false",
        "  live_execution_authority: false",
        "  accepted_state_authority: false",
        "  secrets_authority: false",
        "codex_native_surfaces:",
        "  project_agents_md: true",
        "  project_codex_config: true",
        "  shared_ion_hooks: true",
        "  folder_local_context_capsule: true",
    ]
    lines.extend(_yaml_mapping("paths", _portable_local_paths(mount)))
    lines.extend(_yaml_list(
        "read_first",
        [
            "AGENTS.md",
            f"{PORTABLE_CONTEXT_DIR}/{PORTABLE_CONTEXT_MANIFEST}",
            f"{PORTABLE_CONTEXT_DIR}/{ACTIVE_CONTEXT_PACKAGE_MD}",
            f"{PORTABLE_CONTEXT_DIR}/{PORTABLE_AGENT}",
            f"{PORTABLE_CONTEXT_DIR}/{PORTABLE_DOMAIN}",
            f"{PORTABLE_CONTEXT_DIR}/{PORTABLE_RELATIONSHIPS}",
            f"{PORTABLE_CONTEXT_DIR}/{PORTABLE_COMMUNICATIONS}",
            f"{PORTABLE_CONTEXT_DIR}/{PORTABLE_ADDRESS_BOOK}",
            DOMAIN_WEAVER_PROJECTION_PATH.as_posix(),
            DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix(),
            DOMAIN_WEAVER_PROMOTION_REVIEW_MD_PATH.as_posix(),
        ],
    ))
    lines.extend(_yaml_mapping("relationships", relationships))
    lines.extend(
        [
            "communication:",
            f"  portable_profile: {_yaml_scalar(f'{PORTABLE_CONTEXT_DIR}/{PORTABLE_COMMUNICATIONS}')}",
            f"  address_book: {_yaml_scalar(f'{PORTABLE_CONTEXT_DIR}/{PORTABLE_ADDRESS_BOOK}')}",
            f"  shared_directory_path: {_yaml_scalar(communications.get('shared_directory_path'))}",
            f"  available_agent_count: {_yaml_scalar(communications.get('available_agent_count'))}",
            f"  contact_count: {_yaml_scalar(_as_mapping(communications.get('address_book_summary')).get('contact_count', 0))}",
            "  automation_limits_required: true",
            "  mention_syntax: \"@agent_alias\"",
            "  directive_fence: \"ion-agent-comms\"",
            "  run_graph_observable: true",
            f"domain_weaver_projection: {_yaml_scalar(mount.get('domain_weaver_projection_path') or DOMAIN_WEAVER_PROJECTION_PATH.as_posix())}",
            f"domain_weaver_promotion_review: {_yaml_scalar(mount.get('domain_weaver_promotion_review_path') or DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix())}",
        ]
    )
    lines.extend(_yaml_list("context_refs", [str(ref) for ref in mount.get("context_refs") or []]))
    lines.extend(
        [
            "bootstrap_steps:",
            '  - "Start Codex CLI from this folder or pass it as -C."',
            '  - "Load AGENTS.md and .ion/ION_CONTEXT_CAPSULE.yaml before material work."',
            '  - "Use .ion/ACTIVE_CONTEXT_PACKAGE.md as the immediate working context."',
            '  - "Load .ion/COMMUNICATIONS.json and .ion/ADDRESS_BOOK.json to see available roles, contact groups, routing rules, and automation limits."',
            '  - "When this agent needs another agent, emit an explicit ion-agent-comms directive block; automation pickup routes it through durable comms/templates/broker."',
            '  - "Use visible @agent aliases for normal team comms; use a directive only when a routed workpack/specialist decision is needed."',
            '  - "Check the Team Comms run graph/policy gate for message, workpack, return, and synced-reply evidence."',
            '  - "Emit receipts under .ion/receipts and ION codex_solo history for material work."',
            '  - "Treat every output as candidate until ION proof and settlement gates complete."',
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _portable_mini_md(mount: Mapping[str, Any], context_package: Mapping[str, Any]) -> str:
    lines = [
        "# ION Agent Domain Mini",
        "",
        "ROLE: folder-local lookup and boot index for a generated Codex agent/domain mount.",
        "POLICY: This Mini is not authority by itself; it points to the active package and portable capsule.",
        "",
        f"AGENT: {mount.get('agent_display_name')} ({mount.get('agent_role_id')})",
        f"DOMAIN: {mount.get('domain_id')}",
        f"MOUNT: {mount.get('mount_id')}",
        f"ACTIVE_CONTEXT_PACKAGE: {PORTABLE_CONTEXT_DIR}/{ACTIVE_CONTEXT_PACKAGE_MD}",
        f"COMMUNICATIONS: {PORTABLE_CONTEXT_DIR}/{PORTABLE_COMMUNICATIONS}",
        f"ADDRESS_BOOK: {PORTABLE_CONTEXT_DIR}/{PORTABLE_ADDRESS_BOOK}",
        f"DOMAIN_WEAVER: {mount.get('domain_weaver_projection_path') or DOMAIN_WEAVER_PROJECTION_PATH.as_posix()}",
        f"DOMAIN_WEAVER_PROMOTION_REVIEW: {mount.get('domain_weaver_promotion_review_path') or DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()}",
        f"CAPSULE: {PORTABLE_CONTEXT_DIR}/{PORTABLE_CAPSULE}",
        f"ROUTE: {PORTABLE_CONTEXT_DIR}/{PORTABLE_ROUTE}",
        "",
        "READ_FIRST:",
        "- AGENTS.md",
        f"- {PORTABLE_CONTEXT_DIR}/{PORTABLE_CONTEXT_MANIFEST}",
        f"- {PORTABLE_CONTEXT_DIR}/{ACTIVE_CONTEXT_PACKAGE_MD}",
        f"- {PORTABLE_CONTEXT_DIR}/{PORTABLE_COMMUNICATIONS}",
        f"- {PORTABLE_CONTEXT_DIR}/{PORTABLE_ADDRESS_BOOK}",
        f"- {mount.get('domain_weaver_projection_path') or DOMAIN_WEAVER_PROJECTION_PATH.as_posix()}",
        f"- {mount.get('domain_weaver_promotion_review_path') or DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()}",
        "",
        "CURRENT_CONTEXT:",
        f"- class: {context_package.get('default_active_package_class')}",
        f"- context_refs: {context_package.get('context_ref_count')}",
        f"- existing_context_refs: {context_package.get('existing_context_ref_count')}",
        "",
        "AUTHORITY: candidate mount only; no production, live execution, accepted-state, or secrets authority.",
        "",
    ]
    return "\n".join(lines)


def _portable_capsule_md(
    mount: Mapping[str, Any],
    agent: Mapping[str, Any],
    domain: Mapping[str, Any] | None,
    context_package: Mapping[str, Any],
) -> str:
    relationships = _portable_relationships(agent, domain)
    lines = [
        "# ION Agent Domain Capsule",
        "",
        "This is the folder-local minimum working context for a generated Codex agent/domain mount.",
        "It lets a Codex CLI started from this folder orient to the agent, domain, context package, relationships, and local comms lanes without depending on the parent chat transcript.",
        "",
        "## Identity",
        "",
        f"- agent: {mount.get('agent_display_name')} ({mount.get('agent_role_id')})",
        f"- domain: {mount.get('domain_id')}",
        f"- mount: {mount.get('mount_id')}",
        f"- package_class: {context_package.get('default_active_package_class')}",
        "",
        "## Boot Order",
        "",
        "- Read AGENTS.md.",
        f"- Read {PORTABLE_CONTEXT_DIR}/{PORTABLE_CONTEXT_MANIFEST}.",
        f"- Read {PORTABLE_CONTEXT_DIR}/{ACTIVE_CONTEXT_PACKAGE_MD}.",
        f"- Read {PORTABLE_CONTEXT_DIR}/{PORTABLE_AGENT}, {PORTABLE_CONTEXT_DIR}/{PORTABLE_DOMAIN}, and {PORTABLE_CONTEXT_DIR}/{PORTABLE_RELATIONSHIPS}.",
        f"- Read {PORTABLE_CONTEXT_DIR}/{PORTABLE_COMMUNICATIONS} for who is available, how this agent can initiate communication, and automation comms limits.",
        f"- Read {PORTABLE_CONTEXT_DIR}/{PORTABLE_ADDRESS_BOOK} for nearest peers, reviewers, escalation contacts, and routing rules.",
        f"- If the active ION root is available, read {mount.get('domain_weaver_projection_path') or DOMAIN_WEAVER_PROJECTION_PATH.as_posix()} to see the domain-agent weave, capsule readiness, and gaps.",
        f"- If the active ION root is available, read {mount.get('domain_weaver_promotion_review_path') or DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()} before acting on candidate domain promotion drafts.",
        "- Use the active ION root and registry files as authority.",
        "- Emit receipts for material work.",
        "",
        "## Relationships",
        "",
        f"- primary_domain: {relationships.get('primary_domain')}",
        f"- selected_mount_domain: {relationships.get('selected_mount_domain')}",
    ]
    secondary = relationships.get("secondary_domains") or []
    lines.append(f"- secondary_domains: {', '.join(secondary) if secondary else 'none'}")
    lines.extend(
        [
            "",
            "## Context Posture",
            "",
            "- Active context package is the operative working context.",
            "- Communications profile is the operative routing directory for agent-initiated packets.",
            "- Address book is the agent-native contact/situation map derived from the shared comms directory and selected domain.",
            "- Domain Weaver is the active-root projection that joins domains, capsule agents, mounts, portable packages, and comms availability.",
            "- Domain Weaver promotion review is candidate-only; it shows draft registry records without granting active registry or accepted-state authority.",
            "- Available agents include aliases and contact contracts in the communications profile.",
            "- Agent-to-agent communication is visible packet exchange; use @agent aliases for normal comms or a fenced ion-agent-comms directive for routed workpack decisions.",
            "- Task-run graphs expose the evidence chain from message to workpack to return to synced reply.",
            "- Mini/Capsule are local continuity and boot surfaces.",
            "- Missing legacy refs are evidence to report, not automatic blockers.",
            "- Raw Codex output is candidate until proof receipts and settlement gates complete.",
            "",
            "## Local Lanes",
            "",
            f"- inbox: {PORTABLE_CONTEXT_DIR}/inbox",
            f"- outbox: {PORTABLE_CONTEXT_DIR}/outbox",
            f"- receipts: {PORTABLE_CONTEXT_DIR}/receipts",
            f"- communications: {PORTABLE_CONTEXT_DIR}/{PORTABLE_COMMUNICATIONS}",
            f"- address_book: {PORTABLE_CONTEXT_DIR}/{PORTABLE_ADDRESS_BOOK}",
            f"- domain_weaver: {mount.get('domain_weaver_projection_path') or DOMAIN_WEAVER_PROJECTION_PATH.as_posix()}",
            f"- domain_weaver_promotion_review: {mount.get('domain_weaver_promotion_review_path') or DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()}",
            "",
            "## Boundaries",
            "",
            "- production_authority: false",
            "- live_execution_authority: false",
            "- accepted_state_authority: false",
            "- secrets_authority: false",
            "",
        ]
    )
    return "\n".join(lines)


def _portable_long_horizon(mount: Mapping[str, Any], context_package: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "ion.portable_agent_domain_long_horizon.v0_1",
        "generated_at": _now(),
        "mount_id": mount.get("mount_id"),
        "agent_role_id": mount.get("agent_role_id"),
        "domain_id": mount.get("domain_id"),
        "epochs": [
            {
                "epoch_id": "portable_mount_initial_epoch",
                "summary": "Generated folder-local ION capsule for Codex-native agent/domain launch.",
                "active_context_package": f"{PORTABLE_CONTEXT_DIR}/{ACTIVE_CONTEXT_PACKAGE_MD}",
                "context_ref_count": context_package.get("context_ref_count"),
                "existing_context_ref_count": context_package.get("existing_context_ref_count"),
            }
        ],
        "policy": "Long horizon is local continuity evidence. Parent ION context remains authority.",
    }


def _portable_route(mount: Mapping[str, Any], context_package: Mapping[str, Any]) -> dict[str, Any]:
    local_required = [
        "AGENTS.md",
        f"{PORTABLE_CONTEXT_DIR}/{PORTABLE_CONTEXT_MANIFEST}",
        f"{PORTABLE_CONTEXT_DIR}/{ACTIVE_CONTEXT_PACKAGE_MD}",
        f"{PORTABLE_CONTEXT_DIR}/{PORTABLE_AGENT}",
        f"{PORTABLE_CONTEXT_DIR}/{PORTABLE_DOMAIN}",
        f"{PORTABLE_CONTEXT_DIR}/{PORTABLE_RELATIONSHIPS}",
        f"{PORTABLE_CONTEXT_DIR}/{PORTABLE_COMMUNICATIONS}",
        f"{PORTABLE_CONTEXT_DIR}/{PORTABLE_ADDRESS_BOOK}",
        str(mount.get("domain_weaver_projection_path") or DOMAIN_WEAVER_PROJECTION_PATH.as_posix()),
        str(mount.get("domain_weaver_promotion_review_path") or DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()),
        str(mount.get("domain_weaver_promotion_review_markdown_path") or DOMAIN_WEAVER_PROMOTION_REVIEW_MD_PATH.as_posix()),
    ]
    return {
        "schema_id": "ion.portable_agent_domain_route.v0_1",
        "generated_at": _now(),
        "mount_id": mount.get("mount_id"),
        "agent_role_id": mount.get("agent_role_id"),
        "domain_id": mount.get("domain_id"),
        "local_required_refs": [{"path": path, "required": True} for path in local_required],
        "source_context_refs": context_package.get("context_refs") or [],
        "domain_weaver_projection_path": str(mount.get("domain_weaver_projection_path") or DOMAIN_WEAVER_PROJECTION_PATH.as_posix()),
        "domain_weaver_promotion_review_path": str(
            mount.get("domain_weaver_promotion_review_path") or DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()
        ),
        "domain_weaver_promotion_review_markdown_path": str(
            mount.get("domain_weaver_promotion_review_markdown_path") or DOMAIN_WEAVER_PROMOTION_REVIEW_MD_PATH.as_posix()
        ),
        "route_policy": "Load local required refs first, then consult source context refs under the active ION root.",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def _portable_agent_yaml(mount: Mapping[str, Any], agent: Mapping[str, Any]) -> str:
    values = {
        "schema_id": "ion.portable_agent_descriptor.v0_1",
        "generated_at": _now(),
        "role_id": mount.get("agent_role_id"),
        "display_name": mount.get("agent_display_name"),
        "context_system_card": mount.get("agent_context_card") or "",
        "package_strategy": agent.get("package_strategy") or "",
        "default_active_package_class": agent.get("default_active_package_class") or "",
        "write_posture": agent.get("write_posture") or "none",
        "registry_primary_domain": _primary_domain_for_agent(agent),
        "registry_secondary_domains": _clean_list(agent.get("registry_secondary_domains")),
        "template_bindings": _clean_list(agent.get("template_bindings") or agent.get("primary_templates")),
        "source_refs": _clean_list(agent.get("source_refs")),
        "communications_profile": f"{PORTABLE_CONTEXT_DIR}/{PORTABLE_COMMUNICATIONS}",
        "address_book": f"{PORTABLE_CONTEXT_DIR}/{PORTABLE_ADDRESS_BOOK}",
        "domain_weaver_projection": str(mount.get("domain_weaver_projection_path") or DOMAIN_WEAVER_PROJECTION_PATH.as_posix()),
        "domain_weaver_promotion_review": str(
            mount.get("domain_weaver_promotion_review_path") or DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()
        ),
        "can_initiate_comms": True,
        "comms_authority": "durable_packet_only_no_live_agent_presence",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }
    return _yaml_document(values)


def _portable_domain_yaml(mount: Mapping[str, Any], domain: Mapping[str, Any] | None) -> str:
    domain = dict(domain or {})
    values = {
        "schema_id": "ion.portable_domain_descriptor.v0_1",
        "generated_at": _now(),
        "domain_id": mount.get("domain_id"),
        "display_name": domain.get("display_name") or "",
        "purpose": domain.get("purpose") or domain.get("mission") or "unassigned",
        "status": domain.get("status") or "",
        "authority": domain.get("authority") or "",
        "fact_posture": domain.get("fact_posture") or "candidate",
        "maturity_estimate": domain.get("maturity_estimate") or "unknown",
        "paths": _clean_list(domain.get("paths")),
        "owned_or_stewarded_surfaces": _clean_list(domain.get("owned_or_stewarded_surfaces")),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }
    return _yaml_document(values)


def _portable_relationships_yaml(agent: Mapping[str, Any], domain: Mapping[str, Any] | None) -> str:
    values = {
        "schema_id": "ion.portable_agent_domain_relationships.v0_1",
        "generated_at": _now(),
        **_portable_relationships(agent, domain),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }
    return _yaml_document(values)


def _agent_card_text(mount: Mapping[str, Any], agent: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Agent System Card",
            "",
            f"role_id: {mount.get('agent_role_id')}",
            f"display_name: {mount.get('agent_display_name')}",
            f"context_system_card: {mount.get('agent_context_card') or 'missing'}",
            f"package_strategy: {agent.get('package_strategy') or 'unspecified'}",
            f"default_active_package_class: {agent.get('default_active_package_class') or 'unspecified'}",
            f"write_posture: {agent.get('write_posture') or 'none'}",
            "",
            "This file is a generated projection. The registry/context-system files remain authority.",
            "",
        ]
    )


def _domain_card_text(mount: Mapping[str, Any], domain: Mapping[str, Any] | None) -> str:
    domain = dict(domain or {})
    paths = "\n".join(f"- {path}" for path in domain.get("paths") or []) or "- none"
    return "\n".join(
        [
            "# Domain System Card",
            "",
            f"domain_id: {mount.get('domain_id')}",
            f"purpose: {domain.get('purpose') or 'unassigned'}",
            f"fact_posture: {domain.get('fact_posture') or 'candidate'}",
            f"maturity_estimate: {domain.get('maturity_estimate') or 'unknown'}",
            "",
            "## Domain Paths",
            "",
            paths,
            "",
            "This file is a generated projection. Domain registry/weave files remain authority.",
            "",
        ]
    )


def materialize_codex_agent_mount(
    root: str | Path | None,
    agent: Mapping[str, Any],
    domain: Mapping[str, Any] | None = None,
    *,
    communication_directory: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    mount = build_codex_agent_mount_candidate(shell_root, agent, domain)
    mount_path = shell_root / str(mount["mount_path"])
    mount_path.mkdir(parents=True, exist_ok=True)
    (mount_path / ".codex").mkdir(parents=True, exist_ok=True)
    portable_path = mount_path / PORTABLE_CONTEXT_DIR
    portable_path.mkdir(parents=True, exist_ok=True)
    for rel in ("inbox", "outbox", "runs", "receipts"):
        (mount_path / rel).mkdir(exist_ok=True)
        keep = mount_path / rel / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")
    for rel in ("inbox", "outbox", "receipts"):
        (portable_path / rel).mkdir(exist_ok=True)
        keep = portable_path / rel / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")
    manifest = {
        **mount,
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "generated_by": "kernel.ion_codex_agent_mount",
        "source_policy": str(
            agent.get("mount_source_policy")
            or (domain or {}).get("mount_source_policy")
            or "generated projection from ION agent/domain registries"
        ),
        "materialized": True,
        "manifest_exists": True,
        "agents_md_exists": True,
        "config_exists": True,
        "active_context_package_exists": True,
        "active_context_package_md_exists": True,
        "portable_context_exists": True,
        "portable_context_manifest_exists": True,
        "portable_communications_exists": True,
        "portable_address_book_exists": True,
        "portable_active_context_package_exists": True,
        "portable_active_context_package_md_exists": True,
    }
    (mount_path / MOUNT_MANIFEST_NAME).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (mount_path / "AGENTS.md").write_text(_agents_md_text(mount), encoding="utf-8")
    (mount_path / "AGENT_SYSTEM_CARD.md").write_text(_agent_card_text(mount, agent), encoding="utf-8")
    (mount_path / "DOMAIN_SYSTEM_CARD.md").write_text(_domain_card_text(mount, domain), encoding="utf-8")
    context_package = _active_context_package(shell_root, mount, agent, domain)
    address_book = _portable_address_book(mount, agent, domain, communication_directory)
    communications = _portable_communications(mount, agent, domain, communication_directory, address_book)
    (mount_path / ACTIVE_CONTEXT_PACKAGE_JSON).write_text(json.dumps(context_package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (mount_path / ACTIVE_CONTEXT_PACKAGE_MD).write_text(_active_context_package_md(context_package), encoding="utf-8")
    (portable_path / PORTABLE_CONTEXT_MANIFEST).write_text(_portable_context_manifest_text(shell_root, mount, agent, domain, context_package, communications), encoding="utf-8")
    (portable_path / PORTABLE_MINI).write_text(_portable_mini_md(mount, context_package), encoding="utf-8")
    (portable_path / PORTABLE_CAPSULE).write_text(_portable_capsule_md(mount, agent, domain, context_package), encoding="utf-8")
    (portable_path / PORTABLE_LONG_HORIZON).write_text(json.dumps(_portable_long_horizon(mount, context_package), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (portable_path / PORTABLE_ROUTE).write_text(json.dumps(_portable_route(mount, context_package), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (portable_path / PORTABLE_AGENT).write_text(_portable_agent_yaml(mount, agent), encoding="utf-8")
    (portable_path / PORTABLE_DOMAIN).write_text(_portable_domain_yaml(mount, domain), encoding="utf-8")
    (portable_path / PORTABLE_RELATIONSHIPS).write_text(_portable_relationships_yaml(agent, domain), encoding="utf-8")
    (portable_path / PORTABLE_ADDRESS_BOOK).write_text(json.dumps(address_book, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (portable_path / PORTABLE_COMMUNICATIONS).write_text(json.dumps(communications, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (portable_path / ACTIVE_CONTEXT_PACKAGE_JSON).write_text(json.dumps(context_package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (portable_path / ACTIVE_CONTEXT_PACKAGE_MD).write_text(_active_context_package_md(context_package), encoding="utf-8")
    (mount_path / ".codex" / "config.toml").write_text(_config_text(shell_root, mount), encoding="utf-8")
    refreshed = build_codex_agent_mount_candidate(shell_root, agent, domain)
    refreshed["materialization_result"] = "CODEX_AGENT_MOUNT_MATERIALIZED"
    refreshed["generated_at"] = manifest["generated_at"]
    return refreshed


def _portable_package_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _portable_package_config_text(mount: Mapping[str, Any]) -> str:
    developer_instructions = "\n".join(
        [
            "ION portable agent/domain package guidance:",
            f"- Agent: {mount.get('agent_display_name')} ({mount.get('agent_role_id')}).",
            f"- Domain: {mount.get('domain_id')}.",
            "- This folder is a drop-in Codex launch root.",
            f"- Read AGENTS.md first, then .ion/ION_CONTEXT_CAPSULE.yaml, .ion/ACTIVE_CONTEXT_PACKAGE.md, .ion/COMMUNICATIONS.json, .ion/ADDRESS_BOOK.json, .ion/AGENT.yaml, .ion/DOMAIN.yaml, .ion/RELATIONSHIPS.yaml, and the active-root Domain Weaver projection at {DOMAIN_WEAVER_PROJECTION_PATH.as_posix()} when available.",
            f"- Read the active-root Domain Weaver promotion review at {DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()} before treating candidate domains as registry-promotion drafts.",
            "- Use .ion/source_refs/SOURCE_REF_MANIFEST.json as a source-reference index when the active ION root is unavailable.",
            "- If an active ION root is available, treat it as authority and treat bundled source refs as evidence pointers.",
            "- Manage local work through .ion/inbox, .ion/outbox, .ion/receipts, and .ion/runs.",
            "- No production, live execution, accepted-state, secrets, deploy, push, or destructive authority is granted by this package.",
        ]
    )
    return "\n\n".join(
        [
            "# Generated ION portable agent/domain package config. Do not store secrets here.",
            'sandbox_mode = "workspace-write"',
            'approval_policy = "on-request"',
            f"developer_instructions = {_toml_multiline(developer_instructions)}",
            "[features]\nhooks = false",
            "\n".join(
                [
                    "[sandbox_workspace_write]",
                    "network_access = false",
                    "writable_roots = [",
                    '  ".",',
                    "]",
                ]
            ),
            "",
        ]
    )


def _portable_package_readme(mount: Mapping[str, Any]) -> str:
    command = f"codex -C \"$(pwd)\""
    return "\n".join(
        [
            "# ION Portable Agent Package",
            "",
            f"Agent: {mount.get('agent_display_name')} ({mount.get('agent_role_id')})",
            f"Domain: {mount.get('domain_id')}",
            "",
            "This folder is the drop-in package. Put these files in a new working folder, then start Codex from that folder.",
            "",
            "```bash",
            command,
            "```",
            "",
            "## Read Order",
            "",
            "1. `AGENTS.md`",
            "2. `.ion/ION_CONTEXT_CAPSULE.yaml`",
            "3. `.ion/ACTIVE_CONTEXT_PACKAGE.md`",
            "4. `.ion/COMMUNICATIONS.json`",
            "5. `.ion/ADDRESS_BOOK.json`",
            "6. `.ion/AGENT.yaml`",
            "7. `.ion/DOMAIN.yaml`",
            "8. `.ion/RELATIONSHIPS.yaml`",
            "9. `.ion/source_refs/SOURCE_REF_MANIFEST.json`",
            f"10. `{DOMAIN_WEAVER_PROJECTION_PATH.as_posix()}` when an active ION root is available",
            f"11. `{DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()}` when an active ION root is available",
            "",
            "## What Is Included",
            "",
            "- Native Codex launch files: `AGENTS.md` and `.codex/config.toml`.",
            "- Folder-local ION capsule: `.ion/ION_CONTEXT_CAPSULE.yaml`, Mini, Capsule, Route, Long Horizon, agent, domain, relationships, and active context package.",
            "- Agent comms directory: `.ion/COMMUNICATIONS.json` with available agents, channels, and automation prompt/time limits.",
            "- Agent address book: `.ion/ADDRESS_BOOK.json` with nearest peers, reviewers, escalation contacts, routing rules, and situation map.",
            f"- Domain Weaver pointer: `{DOMAIN_WEAVER_PROJECTION_PATH.as_posix()}` for the active-root domain/agent/capsule/comms projection.",
            f"- Domain Weaver promotion review pointer: `{DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()}` for candidate-only registry draft review.",
            "- Bounded source-reference evidence under `.ion/source_refs/`; file refs may be copied, directory refs are manifest-only by default.",
            "- Local lanes: `.ion/inbox`, `.ion/outbox`, `.ion/receipts`, `.ion/runs`.",
            "",
            "## Boundary",
            "",
            "This package is a candidate working carrier. It does not grant production, live execution, accepted-state, secrets, deploy, push, or destructive authority.",
            "",
        ]
    )


def _portable_package_agents_md(mount: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# ION Portable Agent Domain",
            "",
            f"Agent: {mount.get('agent_display_name')} ({mount.get('agent_role_id')})",
            f"Domain: {mount.get('domain_id')}",
            "",
            "## Boot Rule",
            "",
            "You are running from a portable ION agent/domain package.",
            "",
            "Read these local files before material work:",
            "",
            "- `.ion/ION_CONTEXT_CAPSULE.yaml`",
            "- `.ion/ACTIVE_CONTEXT_PACKAGE.md`",
            "- `.ion/COMMUNICATIONS.json`",
            "- `.ion/ADDRESS_BOOK.json`",
            "- `.ion/AGENT.yaml`",
            "- `.ion/DOMAIN.yaml`",
            "- `.ion/RELATIONSHIPS.yaml`",
            "- `.ion/source_refs/SOURCE_REF_MANIFEST.json`",
            f"- `{DOMAIN_WEAVER_PROJECTION_PATH.as_posix()}` when an active ION root is available",
            f"- `{DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()}` when an active ION root is available",
            "",
            "If the active ION root is present, it remains authority. If it is not present, use `.ion/source_refs/SOURCE_REF_MANIFEST.json` as a source-reference index and report that you are in portable/offline mode.",
            "",
            "Use `.ion/inbox`, `.ion/outbox`, `.ion/receipts`, and `.ion/runs` for local work records.",
            "",
            "No production, live execution, accepted-state, secrets, deploy, push, or destructive authority is granted by this folder.",
            "",
        ]
    )


def _portable_bootstrap_text(mount: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Bootstrap",
            "",
            "This package is meant to be copied or unzipped into a new folder.",
            "",
            "## Start",
            "",
            "From the folder containing this file:",
            "",
            "```bash",
            "codex -C \"$(pwd)\"",
            "```",
            "",
            "## Verify",
            "",
            "```bash",
            "python3 .ion/ion_bootstrap.py",
            "codex -C \"$(pwd)\" debug prompt-input \"probe: identify this ION portable agent package\"",
            "```",
            "",
            "## First Agent Instruction",
            "",
            f"You are `{mount.get('agent_display_name')}` for `{mount.get('domain_id')}`. Load the local `.ion` files, classify whether the active ION root is reachable, then either work against live ION authority or operate in portable snapshot mode.",
            "",
        ]
    )


def _portable_bootstrap_script() -> str:
    return "\n".join(
        [
            "#!/usr/bin/env python3",
            "from __future__ import annotations",
            "",
            "import json",
            "from pathlib import Path",
            "",
            "def find_portable_root(start: Path) -> Path:",
            "    for candidate in (start, *start.parents):",
            "        if (candidate / '.ion').is_dir() and (candidate / 'AGENTS.md').exists():",
            "            return candidate",
            "    raise RuntimeError('Unable to locate portable ION root markers.')",
            "",
            "",
            "ROOT = find_portable_root(Path(__file__).resolve())",
            "ION = ROOT / '.ion'",
            "REQUIRED = [",
            "    ROOT / 'AGENTS.md',",
            "    ROOT / '.codex' / 'config.toml',",
            "    ION / 'ION_CONTEXT_CAPSULE.yaml',",
            "    ION / 'ACTIVE_CONTEXT_PACKAGE.md',",
            "    ION / 'COMMUNICATIONS.json',",
            "    ION / 'ADDRESS_BOOK.json',",
            "    ION / 'AGENT.yaml',",
            "    ION / 'DOMAIN.yaml',",
            "    ION / 'RELATIONSHIPS.yaml',",
            "    ION / 'source_refs' / 'SOURCE_REF_MANIFEST.json',",
            "]",
            "",
            "def main() -> int:",
            "    for rel in ('inbox', 'outbox', 'receipts', 'runs'):",
            "        (ION / rel).mkdir(parents=True, exist_ok=True)",
            "    missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.exists()]",
            "    status = {",
            "        'schema_id': 'ion.portable_agent_domain_bootstrap_status.v0_1',",
            "        'root': str(ROOT),",
            "        'ready': not missing,",
            "        'missing': missing,",
            "        'launch_command': f'codex -C {ROOT}',",
            "        'authority': {",
            "            'production_authority': False,",
            "            'live_execution_authority': False,",
            "            'accepted_state_authority': False,",
            "            'secrets_authority': False,",
            "        },",
            "    }",
            "    (ION / 'STATUS.json').write_text(json.dumps(status, indent=2, sort_keys=True) + '\\n', encoding='utf-8')",
            "    print(json.dumps(status, indent=2, sort_keys=True))",
            "    return 0 if status['ready'] else 1",
            "",
            "if __name__ == '__main__':",
            "    raise SystemExit(main())",
            "",
        ]
    )


def _portable_copy_source_ref(root: Path, ref: str, source_root: Path) -> dict[str, Any]:
    record: dict[str, Any] = {
        "ref": ref,
        "exists": False,
        "copied": False,
        "kind": "missing",
        "copied_paths": [],
        "skipped_reason": "",
    }
    text = str(ref or "").strip()
    if not text:
        record["skipped_reason"] = "empty_ref"
        return record
    rel = Path(text)
    if rel.is_absolute() or ".." in rel.parts:
        record["kind"] = "unsafe_or_external"
        record["skipped_reason"] = "unsafe_or_external_ref"
        return record
    source = root / rel
    if not source.exists():
        return record
    record["exists"] = True
    destination = source_root / rel
    if source.is_file():
        record["kind"] = "file"
        record["bytes"] = source.stat().st_size
        if source.stat().st_size > MAX_PORTABLE_SOURCE_FILE_BYTES:
            record["skipped_reason"] = "file_too_large_for_portable_context_snapshot"
            return record
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied = destination.relative_to(source_root).as_posix()
        record["copied"] = True
        record["copied_paths"] = [copied]
        record["sha256"] = _sha256_file(destination)
        return record
    if source.is_dir():
        record["kind"] = "directory"
        sample_paths: list[str] = []
        skipped_count = 0
        for item in sorted(source.rglob("*")):
            if not item.is_file():
                continue
            relative = item.relative_to(root)
            if any(part in {".git", "__pycache__", ".pytest_cache", "node_modules", "dist", "build"} for part in relative.parts):
                skipped_count += 1
                continue
            if len(sample_paths) < MAX_PORTABLE_SOURCE_DIR_SAMPLE:
                sample_paths.append(relative.as_posix())
            else:
                skipped_count += 1
        record["copied"] = False
        record["copied_paths"] = []
        record["sample_paths"] = sample_paths
        record["sample_file_count"] = len(sample_paths)
        record["skipped_file_count"] = skipped_count
        record["skipped_reason"] = "directory_snapshot_disabled_manifest_only"
        return record
    record["kind"] = "other"
    record["skipped_reason"] = "unsupported_ref_kind"
    return record


def _zip_directory(source_dir: Path, zip_path: Path) -> str:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in sorted(source_dir.rglob("*")):
            if item.is_file():
                archive.write(item, item.relative_to(source_dir).as_posix())
    return _sha256_file(zip_path)


def export_portable_agent_domain_package(
    root: str | Path | None,
    agent: Mapping[str, Any],
    domain: Mapping[str, Any] | None = None,
    *,
    output_root: str | Path | None = None,
    communication_directory: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    mount = materialize_codex_agent_mount(shell_root, agent, domain, communication_directory=communication_directory)
    mount_path = shell_root / str(mount["mount_path"])
    stamp = _portable_package_stamp()
    package_root = shell_root / (Path(output_root) if output_root else PORTABLE_PACKAGE_ROOT) / str(mount["mount_id"])
    package_base = package_root / stamp
    drop_in = package_base / "drop_in"
    ion_dir = drop_in / ".ion"
    source_root = ion_dir / "source_refs"
    for rel in (".codex", ".ion", ".ion/inbox", ".ion/outbox", ".ion/receipts", ".ion/runs", ".ion/source_refs"):
        (drop_in / rel).mkdir(parents=True, exist_ok=True)

    (drop_in / "README.md").write_text(_portable_package_readme(mount), encoding="utf-8")
    (drop_in / "BOOTSTRAP.md").write_text(_portable_bootstrap_text(mount), encoding="utf-8")
    (drop_in / "AGENTS.md").write_text(_portable_package_agents_md(mount), encoding="utf-8")
    (drop_in / ".codex" / "config.toml").write_text(_portable_package_config_text(mount), encoding="utf-8")
    (ion_dir / "ion_bootstrap.py").write_text(_portable_bootstrap_script(), encoding="utf-8")

    for name in (
        PORTABLE_CONTEXT_MANIFEST,
        PORTABLE_MINI,
        PORTABLE_CAPSULE,
        PORTABLE_LONG_HORIZON,
        PORTABLE_ROUTE,
        PORTABLE_DOMAIN,
        PORTABLE_AGENT,
        PORTABLE_RELATIONSHIPS,
        PORTABLE_COMMUNICATIONS,
        PORTABLE_ADDRESS_BOOK,
        ACTIVE_CONTEXT_PACKAGE_JSON,
        ACTIVE_CONTEXT_PACKAGE_MD,
    ):
        source = mount_path / PORTABLE_CONTEXT_DIR / name
        if source.is_file():
            shutil.copy2(source, ion_dir / name)
    for name in (MOUNT_MANIFEST_NAME, "AGENT_SYSTEM_CARD.md", "DOMAIN_SYSTEM_CARD.md"):
        source = mount_path / name
        if source.is_file():
            shutil.copy2(source, drop_in / name)

    source_records = [_portable_copy_source_ref(shell_root, str(ref), source_root) for ref in mount.get("context_refs") or []]
    source_manifest = {
        "schema_id": "ion.portable_agent_domain_source_refs.v0_1",
        "generated_at": _now(),
        "source_ion_root": shell_root.as_posix(),
        "agent_role_id": mount.get("agent_role_id"),
        "domain_id": mount.get("domain_id"),
        "policy": "Source-reference index. File refs may be copied; directory refs are manifest-only by default. Use active ION root as authority when available.",
        "max_file_bytes": MAX_PORTABLE_SOURCE_FILE_BYTES,
        "max_dir_files": MAX_PORTABLE_SOURCE_DIR_FILES,
        "directory_snapshot_policy": "disabled_by_default",
        "records": source_records,
        "copied_ref_count": sum(1 for record in source_records if record.get("copied")),
        "missing_ref_count": sum(1 for record in source_records if not record.get("exists")),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }
    (source_root / "SOURCE_REF_MANIFEST.json").write_text(json.dumps(source_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    package_manifest = {
        "schema_id": PORTABLE_PACKAGE_SCHEMA_ID,
        "generated_at": _now(),
        "package_id": f"{mount['mount_id']}__{stamp}",
        "mount_id": mount.get("mount_id"),
        "agent_role_id": mount.get("agent_role_id"),
        "agent_display_name": mount.get("agent_display_name"),
        "domain_id": mount.get("domain_id"),
        "drop_in_path": drop_in.relative_to(shell_root).as_posix(),
        "read_first": [
            "AGENTS.md",
            ".ion/ION_CONTEXT_CAPSULE.yaml",
            ".ion/ACTIVE_CONTEXT_PACKAGE.md",
            ".ion/COMMUNICATIONS.json",
            ".ion/ADDRESS_BOOK.json",
            ".ion/AGENT.yaml",
            ".ion/DOMAIN.yaml",
            ".ion/RELATIONSHIPS.yaml",
            ".ion/source_refs/SOURCE_REF_MANIFEST.json",
            DOMAIN_WEAVER_PROJECTION_PATH.as_posix(),
            DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix(),
            DOMAIN_WEAVER_PROMOTION_REVIEW_MD_PATH.as_posix(),
        ],
        "domain_weaver_projection_path": DOMAIN_WEAVER_PROJECTION_PATH.as_posix(),
        "domain_weaver_promotion_review_path": DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix(),
        "domain_weaver_promotion_review_markdown_path": DOMAIN_WEAVER_PROMOTION_REVIEW_MD_PATH.as_posix(),
        "launch_command": f"codex -C {drop_in.as_posix()}",
        "zip_root_policy": "Zip entries are rooted at the drop-in folder contents; unzip into a new folder and run codex there.",
        "source_ref_manifest": ".ion/source_refs/SOURCE_REF_MANIFEST.json",
        "drop_in_ready": True,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }
    (drop_in / PORTABLE_PACKAGE_MANIFEST_NAME).write_text(json.dumps(package_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    zip_path = package_base / f"{mount['mount_id']}__drop_in.zip"
    zip_sha256 = _zip_directory(drop_in, zip_path)
    package_manifest.update(
        {
            "zip_path": zip_path.relative_to(shell_root).as_posix(),
            "zip_sha256": zip_sha256,
            "source_ref_copied_count": source_manifest["copied_ref_count"],
            "source_ref_missing_count": source_manifest["missing_ref_count"],
        }
    )
    (package_base / "LATEST.json").write_text(json.dumps(package_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (package_root / "LATEST.json").write_text(json.dumps(package_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return package_manifest
