"""Read-only Codex CLI workbench model for the ION cockpit.

This projection is the clean first layer for a Codex-native workbench UI.  It
does not replace the existing Capsule Chat state machine; it makes the Codex
CLI carrier, context substrate, settings, hooks, skills, tools, and trace lanes
visible as one inspectable model.

The model deliberately avoids raw secrets, raw Codex memory/session content,
and private internal reasoning text.  It exposes paths, redacted configuration
shape, public tool/trace records, and copy-ready context excerpts.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from .ion_codex_carrier_os import build_codex_carrier_os_source_map
from .ion_codex_context_timeline import build_codex_context_timeline_model
from .ion_codex_local_pc_audit import build_codex_local_pc_audit
from .ion_codex_operational_posture import build_codex_operational_posture
from .ion_codex_solo_context import build_codex_solo_context_model

SCHEMA_ID = "ion.codex_cli_workbench_model.v1"
READY_VERDICT = "ION_CODEX_CLI_WORKBENCH_READY"
DEGRADED_VERDICT = "ION_CODEX_CLI_WORKBENCH_DEGRADED"
BLOCKED_VERDICT = "ION_CODEX_CLI_WORKBENCH_BLOCKED"

AUTHORITY_FALSE: dict[str, bool] = {
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "hidden_reasoning_exposed": False,
}

CURRENT = Path("ION/05_context/current")
ACTIVE_CHAT_MODEL = CURRENT / "ACTIVE_CODEX_CAPSULE_CHAT_MODEL.json"
CODEX_HOOK_RUNTIME_ROOT = CURRENT / "codex_cli/hooks/runtime"

CONTEXT_SURFACES: tuple[tuple[str, str, str, int, int], ...] = (
    ("capsule", "ION/05_context/current/codex_solo/CAPSULE.md", "minimum working context", 28, 5000),
    ("mini", "ION/05_context/current/codex_solo/MINI.md", "lookup and receipt index", 40, 5000),
    ("hot_context", "ION/05_context/current/codex_solo/HOT_CONTEXT.md", "compiled boot/work context", 42, 7000),
    ("long_horizon", "ION/05_context/current/codex_solo/LONG_HORIZON.json", "compressed long-horizon capsule index", 60, 9000),
    ("route", "ION/05_context/current/codex_solo/ROUTE.json", "context route and required refs", 60, 9000),
    ("context_packages", "ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json", "context package selector", 60, 9000),
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_shell_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").is_file() and (path / "ION" / "REPO_AUTHORITY.md").is_file():
            return path
        if path.name == "ION" and (path / "REPO_AUTHORITY.md").is_file() and (path.parent / "pyproject.toml").is_file():
            return path.parent
    raise FileNotFoundError("Could not resolve ION shell root; expected pyproject.toml and ION/REPO_AUTHORITY.md")


def _read_json(path: Path) -> Any | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_text(path: Path, *, max_chars: int) -> str:
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n...[truncated]"


def _safe_surface(label: str, func: Callable[..., Mapping[str, Any]], *args: Any, **kwargs: Any) -> tuple[dict[str, Any], dict[str, Any] | None]:
    try:
        payload = dict(func(*args, **kwargs))
        return payload, None
    except Exception as exc:  # keep cockpit model generation fail-soft
        return {}, {
            "surface": label,
            "error_class": exc.__class__.__name__,
            "error": str(exc),
        }


def _line_excerpt(text: str, *, max_lines: int) -> str:
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    return "\n".join(lines[:max_lines]).rstrip() + "\n...[truncated]"


def _context_surface(shell_root: Path, surface_id: str, rel: str, role: str, max_lines: int, max_chars: int) -> dict[str, Any]:
    path = shell_root / rel
    text = _read_text(path, max_chars=max_chars)
    return {
        "surface_id": surface_id,
        "path": rel,
        "role": role,
        "exists": path.is_file(),
        "bytes": path.stat().st_size if path.is_file() else None,
        "line_count": len(path.read_text(encoding="utf-8", errors="replace").splitlines()) if path.is_file() else 0,
        "excerpt": _line_excerpt(text, max_lines=max_lines),
        "copy_ready": path.is_file(),
        "full_text_path": rel,
    }


def _latest_files(root: Path, rel: str, *, limit: int = 8) -> list[dict[str, Any]]:
    directory = root / rel
    if not directory.is_dir():
        return []
    files = [path for path in directory.rglob("*") if path.is_file()]
    files.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    records: list[dict[str, Any]] = []
    for path in files[:limit]:
        try:
            relative = path.relative_to(root).as_posix()
        except ValueError:
            relative = path.as_posix()
        records.append({
            "name": path.name,
            "path": relative,
            "bytes": path.stat().st_size,
            "mtime": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat(),
        })
    return records


def _hook_runtime_summary(root: Path) -> dict[str, Any]:
    groups: list[dict[str, Any]] = []
    total = 0
    for directory in sorted((root / CODEX_HOOK_RUNTIME_ROOT).glob("*")) if (root / CODEX_HOOK_RUNTIME_ROOT).is_dir() else []:
        if not directory.is_dir():
            continue
        records = _latest_files(root, directory.relative_to(root).as_posix(), limit=5)
        total += len(records)
        groups.append({
            "hook": directory.name,
            "receipt_count_sampled": len(records),
            "latest_receipts": records,
        })
    return {
        "schema_id": "ion.codex_cli_workbench_hook_runtime_summary.v1",
        "runtime_root": CODEX_HOOK_RUNTIME_ROOT.as_posix(),
        "hook_group_count": len(groups),
        "sampled_receipt_count": total,
        "groups": groups,
    }


def _chat_summary(root: Path) -> dict[str, Any]:
    model = _read_json(root / ACTIVE_CHAT_MODEL)
    if not isinstance(model, Mapping):
        return {
            "model_path": ACTIVE_CHAT_MODEL.as_posix(),
            "model_present": False,
            "turn_count": 0,
            "response_run_count": 0,
            "trace_count": 0,
            "latest_runs": [],
            "latest_turns": [],
        }
    ui = model.get("ui") if isinstance(model.get("ui"), Mapping) else {}
    conversation = ui.get("conversation") if isinstance(ui.get("conversation"), Mapping) else {}
    convo_summary = conversation.get("summary") if isinstance(conversation.get("summary"), Mapping) else {}
    response_runs = model.get("response_runs") if isinstance(model.get("response_runs"), Mapping) else {}
    turn_traces = model.get("turn_traces") if isinstance(model.get("turn_traces"), Mapping) else {}
    lanes = model.get("lanes") if isinstance(model.get("lanes"), Mapping) else {}
    codex_lane = lanes.get("codex_general") if isinstance(lanes.get("codex_general"), Mapping) else {}
    turns = codex_lane.get("turns") if isinstance(codex_lane.get("turns"), list) else []
    return {
        "model_path": ACTIVE_CHAT_MODEL.as_posix(),
        "model_present": True,
        "generated_at": model.get("generated_at"),
        "verdict": model.get("verdict"),
        "turn_count": convo_summary.get("turn_count", len(turns)),
        "assistant_turn_count": convo_summary.get("assistant_turn_count"),
        "response_run_count": response_runs.get("record_count", 0),
        "trace_count": turn_traces.get("trace_count", 0),
        "latest_runs": response_runs.get("records", [])[:6] if isinstance(response_runs.get("records"), list) else [],
        "latest_turns": turns[-8:] if turns else [],
    }


def _tool_matrix(carrier_os: Mapping[str, Any], local_pc: Mapping[str, Any]) -> dict[str, Any]:
    domain = carrier_os.get("domain_registry") if isinstance(carrier_os.get("domain_registry"), Mapping) else {}
    slash = carrier_os.get("slash_command_registry") if isinstance(carrier_os.get("slash_command_registry"), Mapping) else {}
    project = local_pc.get("project_codex_config") if isinstance(local_pc.get("project_codex_config"), Mapping) else {}
    commands = slash.get("commands") if isinstance(slash.get("commands"), list) else []
    return {
        "schema_id": "ion.codex_cli_workbench_tool_matrix.v1",
        "mcp_read_only_tools": domain.get("mcp_read_only_tools", []),
        "mcp_read_only_tool_count": len(domain.get("mcp_read_only_tools", [])) if isinstance(domain.get("mcp_read_only_tools"), list) else 0,
        "slash_commands": commands,
        "slash_command_count": len(commands),
        "configured_mcp_servers": project.get("mcp_server_names", []),
        "configured_profile_names": project.get("profile_names", []),
        "mutation_authority_from_tools": False,
    }


def _settings_summary(local_pc: Mapping[str, Any]) -> dict[str, Any]:
    project = local_pc.get("project_codex_config") if isinstance(local_pc.get("project_codex_config"), Mapping) else {}
    home = local_pc.get("codex_home") if isinstance(local_pc.get("codex_home"), Mapping) else {}
    codex_cli = local_pc.get("codex_cli") if isinstance(local_pc.get("codex_cli"), Mapping) else {}
    return {
        "schema_id": "ion.codex_cli_workbench_settings_summary.v1",
        "codex_cli_available": codex_cli.get("available"),
        "codex_binary_ref": codex_cli.get("binary_ref"),
        "project_config": {
            "path_ref": project.get("path_ref"),
            "exists": project.get("exists"),
            "parse_ok": project.get("parse_ok"),
            "top_level_keys": project.get("top_level_keys", []),
            "mcp_server_names": project.get("mcp_server_names", []),
            "profile_names": project.get("profile_names", []),
            "redacted_shape": project.get("redacted_shape", {}),
            "raw_config_values_exported": False,
        },
        "codex_home": {
            "path_ref": home.get("path_ref"),
            "exists": home.get("exists"),
            "raw_memory_or_session_content_exported": False,
            "raw_file_names_exported": False,
            "directories": home.get("directories", {}),
        },
        "memory_policy": local_pc.get("memory_policy", {}),
    }


def _project_context_summary(root: Path, solo: Mapping[str, Any], carrier_os: Mapping[str, Any]) -> dict[str, Any]:
    context_packages = solo.get("context_packages") if isinstance(solo.get("context_packages"), Mapping) else {}
    route = solo.get("route") if isinstance(solo.get("route"), Mapping) else {}
    control_planes = carrier_os.get("control_planes") if isinstance(carrier_os.get("control_planes"), list) else []
    return {
        "schema_id": "ion.codex_cli_workbench_project_context.v1",
        "shell_root": root.as_posix(),
        "content_root": (root / "ION").as_posix(),
        "context_package_count": context_packages.get("package_count", 0),
        "selected_context_packages": context_packages.get("selected_by_default", []),
        "route_ok": route.get("ok"),
        "route_entry_count": len(route.get("entries", [])) if isinstance(route.get("entries"), list) else 0,
        "missing_required_route_refs": route.get("findings", []),
        "control_plane_count": len(control_planes),
        "control_planes": control_planes[:12],
    }


def build_codex_cli_workbench_model(root: str | Path | None = None) -> dict[str, Any]:
    """Build the read-only Codex CLI workbench model."""
    shell_root = _resolve_shell_root(root)
    errors: list[dict[str, Any]] = []

    posture, error = _safe_surface("operational_posture", build_codex_operational_posture, shell_root)
    if error:
        errors.append(error)
    carrier_os, error = _safe_surface("carrier_os", build_codex_carrier_os_source_map, shell_root)
    if error:
        errors.append(error)
    local_pc, error = _safe_surface("local_pc_audit", build_codex_local_pc_audit, shell_root, run_help=False)
    if error:
        errors.append(error)
    solo, error = _safe_surface("codex_solo_context", build_codex_solo_context_model, shell_root, write=False)
    if error:
        errors.append(error)

    context_surfaces = [
        _context_surface(shell_root, surface_id, rel, role, max_lines, max_chars)
        for surface_id, rel, role, max_lines, max_chars in CONTEXT_SURFACES
    ]
    context_timeline, error = _safe_surface("codex_context_timeline", build_codex_context_timeline_model, shell_root)
    if error:
        errors.append(error)
    chat = _chat_summary(shell_root)
    tools = _tool_matrix(carrier_os, local_pc)
    settings = _settings_summary(local_pc)
    hooks = {
        "required_refs": posture.get("hooks", {}),
        "runtime_receipts": _hook_runtime_summary(shell_root),
    }
    skills = posture.get("skills", {}) if isinstance(posture.get("skills"), Mapping) else {}
    project_context = _project_context_summary(shell_root, solo, carrier_os)

    operational_state = posture.get("ion_operational_state")
    blocked = operational_state == "ION_CODEX_OPERATIONAL_BLOCKED"
    ready = bool(posture.get("ok")) and bool(solo.get("ok")) and not errors
    verdict = READY_VERDICT if ready else BLOCKED_VERDICT if blocked else DEGRADED_VERDICT
    findings = [str(item) for item in posture.get("warnings", [])] if isinstance(posture.get("warnings"), list) else []

    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "verdict": verdict,
        "ok": verdict != BLOCKED_VERDICT,
        "workbench_ready": ready,
        "shell_root": shell_root.as_posix(),
        "content_root": (shell_root / "ION").as_posix(),
        "north_star": "A Codex-native cockpit that lets an operator see chat, context, settings, hooks, skills, tools, traces, and project posture as one inspectable work surface.",
        "summary": {
            "operational_state": operational_state,
            "mount_truth_state": (posture.get("mount_guard") or {}).get("mount_truth_state") if isinstance(posture.get("mount_guard"), Mapping) else None,
            "carrier_mode": (posture.get("carrier") or {}).get("carrier_mode") if isinstance(posture.get("carrier"), Mapping) else None,
            "capsule_entry_count": (solo.get("capsule") or {}).get("entry_count") if isinstance(solo.get("capsule"), Mapping) else None,
            "context_package_count": project_context.get("context_package_count"),
            "chat_turn_count": chat.get("turn_count"),
            "response_run_count": chat.get("response_run_count"),
            "mcp_read_only_tool_count": tools.get("mcp_read_only_tool_count"),
            "slash_command_count": tools.get("slash_command_count"),
            "hook_group_count": hooks["runtime_receipts"].get("hook_group_count"),
            "context_timeline_event_count": (context_timeline.get("summary") or {}).get("timeline_event_count", 0)
            if isinstance(context_timeline.get("summary"), Mapping)
            else 0,
            "context_diff_event_count": (context_timeline.get("summary") or {}).get("diff_event_count", 0)
            if isinstance(context_timeline.get("summary"), Mapping)
            else 0,
            "skill_count": skills.get("required_ref_count"),
            "native_skill_installed_count": (skills.get("native_codex_skill_installation") or {}).get("installed_count")
            if isinstance(skills.get("native_codex_skill_installation"), Mapping)
            else None,
        },
        "visibility_contract": {
            "visible": [
                "user-visible chat turns",
                "assistant responses",
                "tool calls and response-run records when captured",
                "Capsule/Mini/Hot/Long Horizon context surfaces",
                "redacted Codex CLI settings shape",
                "hook receipts",
                "skill and MCP/slash command inventories",
                "queue/task-return evidence",
            ],
            "not_visible": [
                "private internal reasoning text",
                "raw Codex memory or session transcript content from ~/.codex",
                "secret values or credentials",
                "accepted-state claims without receipts",
            ],
            **AUTHORITY_FALSE,
        },
        "chat": chat,
        "context": {
            "witness_policy": solo.get("witness_policy"),
            "active_context": solo.get("active_context", {}),
            "surfaces": context_surfaces,
            "long_horizon": solo.get("long_horizon", {}),
            "context_packages": solo.get("context_packages", {}),
            "timeline": context_timeline,
        },
        "settings": settings,
        "hooks": hooks,
        "skills": skills,
        "tools": tools,
        "agents_and_roles": {
            "role_phase_contract": posture.get("role_phase_contract", {}),
            "spawn_plan": posture.get("spawn_plan", {}),
            "agent_registry": carrier_os.get("agent_registry", {}),
            "session_registry": carrier_os.get("session_registry", {}),
        },
        "project_context": project_context,
        "carrier_os": {
            "verdict": carrier_os.get("verdict"),
            "source_map_ready": carrier_os.get("source_map_ready"),
            "runtime_loop": carrier_os.get("runtime_loop", []),
            "codex_native_capability_bindings": carrier_os.get("codex_native_capability_bindings", []),
            "non_claims": carrier_os.get("non_claims", []),
        },
        "findings": findings,
        "surface_errors": errors,
        **AUTHORITY_FALSE,
    }
