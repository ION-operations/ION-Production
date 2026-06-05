"""Capsule Codex chat state and projection for the local ION cockpit.

The historical module name remains for import compatibility, but the product
shape is no longer "two chats." The primary surface is one user-facing Codex
Capsule chat. A secondary ION comms adapter keeps visibility into the existing
full ION Relay/Steward/workflow path without creating a second queue, second
agent system, or manual lane chore for the operator.

This module does not call an LLM directly, does not expose arbitrary shell, and
does not grant production or live execution authority. Bounded Codex work still
uses the existing ChatGPT-browser connector work-packet path and proof gates.
"""
from __future__ import annotations

import ast
import hashlib
import html
import json
import os
import re
import subprocess
from collections.abc import Mapping, MutableMapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ion_chatgpt_browser_mcp_connector_contract import call_chatgpt_connector_tool
from .ion_agent_invocation_broker import agent_queue, list_agents
from .ion_codex_queue_runner import build_codex_queue_runner_status, process_codex_queue_once
from .ion_codex_model_moves import (
    DEFAULT_ROUTING_POSTURE,
    apply_codex_model_override,
    build_codex_model_move_plan,
    build_stage_model_move_matrix,
    list_codex_model_profiles,
    summarize_model_move,
)
from .ion_codex_chat_app_ui import render_codex_chat_app_html
from .ion_cockpit_service_manager import build_service_console_model
from .ion_codex_chat_engine import (
    build_codex_chat_carrier_objective,
    build_codex_chat_engine_surface,
    build_codex_chat_engine_turn,
)
from .ion_codex_chat_memory_visualization import build_codex_chat_memory_visualization
from .ion_codex_chat_response_carrier import (
    RUNS_DIR as RESPONSE_RUNS_DIR,
    build_chat_response_carrier_status,
    run_codex_chat_response_carrier,
)
from .ion_codex_solo_context import (
    CAPSULE_PATH,
    CONTEXT_PACKAGES_PATH,
    HOT_CONTEXT_PATH,
    LONG_HORIZON_PATH,
    MINI_PATH,
    ROUTE_PATH,
    WITNESS_POLICY,
    build_codex_solo_context_model,
    record_codex_solo_machine_receipt,
)
from .ion_context_starter_capsule import REQUIRED_FILES as CONTEXT_STARTER_REQUIRED_FILES
from .ion_context_starter_capsule import create_context_starter_capsule
from .ion_skill_activation import build_ion_skill_activation, build_ion_skill_surface

SCHEMA_ID = "ion.codex_capsule_chat_model.v1"
STATE_SCHEMA_ID = "ion.codex_capsule_chat_state.v1"
BRANCH_DRAFT_SCHEMA_ID = "ion.codex_capsule_chat_branch_draft.v1"
CHAT_CONTEXT_BINDING_SCHEMA_ID = "ion.codex_chat_context_binding.v1"
IDE_CONTEXT_BRIDGE_SCHEMA_ID = "ion.codex_ide_context_bridge.v0_1"
READY_VERDICT = "ION_CODEX_CAPSULE_CHAT_READY"
WRITE_CONFIRMATION_TOKEN = "ION_BOUNDED_WRITE_CONFIRMED"

CURRENT = Path("ION/05_context/current")
STATE_DIR = CURRENT / "codex_capsule_chat"
STATE_PATH = STATE_DIR / "state.json"
MODEL_PATH = CURRENT / "ACTIVE_CODEX_CAPSULE_CHAT_MODEL.json"
CODEX_WORK_QUEUE_INDEX = CURRENT / "ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json"
CODEX_WORK_REQUESTS_DIR = CURRENT / "chatgpt_connector/codex_work_requests"
CODEX_QUEUE_RUNS_DIR = CURRENT / "chatgpt_connector/codex_queue_runs"
CODEX_TASK_RETURNS_DIR = CURRENT / "chatgpt_connector/task_returns"
CODEX_MEMORY_ENV = "ION_DUAL_CHAT_CODEX_MEMORY_PATH"
DEFAULT_CODEX_MEMORY_PATH = Path("/home/sev/.codex/memories/ion_codex_capsule_chat_memory.md")
CHAT_EXECUTION_MODE_ENV = "ION_CODEX_CAPSULE_CHAT_DEFAULT_EXECUTION_MODE"
CHAT_RUNNER_START_ENV = "ION_CODEX_CAPSULE_CHAT_ALLOW_RUNNER_START"
CHAT_CODEX_BINARY_ENV = "ION_CODEX_COCKPIT_CODEX_BINARY"
CHAT_RAW_CLI_TIMEOUT_ENV = "ION_CODEX_COCKPIT_RAW_CLI_TIMEOUT_SECONDS"
CHAT_RAW_CLI_SERVICE_TIER_ENV = "ION_CODEX_COCKPIT_RAW_CLI_SERVICE_TIER"
CHAT_EXECUTION_MODES = ("auto", "respond_only", "queue_for_codex", "queue_and_start")
DEFAULT_CHAT_EXECUTION_MODE = "auto"
CHAT_CODEX_SESSION_TRANSPORTS = ("raw_cli", "app_server", "auto")
DEFAULT_CHAT_CODEX_SESSION_TRANSPORT = "raw_cli"
RAW_CODEX_CLI_RUNS_DIR = STATE_DIR / "raw_cli_runs"
IDE_CONTEXT_BRIDGES_DIR = STATE_DIR / "ide_context_bridges"
DEFAULT_RAW_CODEX_CLI_TIMEOUT_SECONDS = 1800
DEFAULT_RAW_CLI_SERVICE_TIER = "fast"
PLAYWRIGHT_COCKPIT_SMOKE_RE = re.compile(r"^playwright-pending-smoke-\d+: reply exactly playwright-ok$")
PLAYWRIGHT_COCKPIT_SMOKE_PERSIST_ENV = "ION_COCKPIT_PLAYWRIGHT_SMOKE_PERSIST"
PLAYWRIGHT_COCKPIT_SMOKE_RESPONSE = "playwright-ok"
IDE_CONTEXT_BRANCHES = (
    ("ide.open_editors", "Open editors", "open_tabs", "selected_tab"),
    ("ide.current_worktree", "Current worktree", "worktree", "selected_tab"),
    ("ide.context_graph", "ION context graph", "context_surfaces", "context_systems"),
    ("ide.docs", "Docs", "docs", "selected_tab"),
    ("ide.media", "Media", "media", "selected_tab"),
    ("ide.diagnostics", "Diagnostics", "diagnostics", "problems"),
    ("ide.preview", "Preview", "preview", "active_view"),
    ("ide.tools", "IDE tools", "tool_capabilities", "active_drawer"),
    ("ide.agent_mounts", "Agent mounts", "agent_mounts", "context_systems"),
)

LANES = {
    "ion_system": {
        "label": "ION Comms Adapter",
        "purpose": "Secondary bridge to the existing full ION Relay/Steward/workflow surfaces. It is not the primary chat product.",
        "memory_policy": "ION state, proof-gated returns, receipts, and explicit promoted memory only.",
    },
    "codex_general": {
        "label": "Codex Chat",
        "purpose": "Primary user-facing Codex chat using Capsule as minimum context, Mini as lookup index, explicit repo context, and bounded receipts.",
        "memory_policy": "Codex solo Capsule is the minimum working context; Mini indexes receipts; long-horizon epochs and package selector decide older context; no hidden memory claims.",
    },
}

ION_PIPELINE_STAGES = (
    ("relay_ingress", "Relay ingress", "Translate operator text into a bounded semantic packet."),
    ("steward_route", "Steward route", "Classify authority, risk, and work legitimacy."),
    ("vizier_plan", "Vizier plan", "Set architecture, dependencies, and review posture."),
    ("mason_codex_work", "Mason/Codex work", "Execute bounded implementation through Codex queue and proof return."),
    ("vice_risk", "Vice risk pass", "Apply future-answerability and contradiction pressure."),
    ("nemesis_verify", "Nemesis verification", "Audit proof, regressions, and release sensitivity."),
    ("relay_return", "Relay return", "Package accepted state and receipts back to the front stage."),
    ("persona_response", "Persona response", "Present the user-facing response without claiming sovereign authority."),
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _safe_slug(value: str, *, max_length: int = 64) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")[:max_length] or "chat"


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _truthy_env(name: str) -> bool:
    return str(os.environ.get(name) or "").strip().lower() in {"1", "true", "yes", "on"}


def _is_ephemeral_playwright_smoke(
    text: str,
    *,
    lane_id: str,
    author: str,
    execution_mode: str,
) -> bool:
    if _truthy_env(PLAYWRIGHT_COCKPIT_SMOKE_PERSIST_ENV):
        return False
    return (
        lane_id == "codex_general"
        and author in {"operator", "user"}
        and execution_mode in {"auto", "respond_only"}
        and bool(PLAYWRIGHT_COCKPIT_SMOKE_RE.fullmatch(text))
    )


def _playwright_smoke_turn_result(
    root: str | Path | None,
    *,
    lane_id: str,
    message: str,
    author: str,
    execution_mode: str,
) -> dict[str, Any]:
    now = _now()
    turn = {
        "turn_id": f"smoke_{now.replace(':', '').replace('+', 'Z')}_{_safe_slug(message)}",
        "lane_id": lane_id,
        "author": author,
        "kind": "playwright_smoke_probe",
        "message": message,
        "message_sha256": _sha256_text(message),
        "created_at": now,
        "execution_mode": execution_mode,
        "persistence": "ephemeral_not_saved",
        "production_authority": False,
        "live_execution_authority": False,
    }
    assistant_turn = {
        "turn_id": f"smoke_assistant_{now.replace(':', '').replace('+', 'Z')}_{_safe_slug(message)}",
        "lane_id": lane_id,
        "author": "codex_chat_engine",
        "kind": "assistant_response",
        "message": PLAYWRIGHT_COCKPIT_SMOKE_RESPONSE,
        "message_sha256": _sha256_text(PLAYWRIGHT_COCKPIT_SMOKE_RESPONSE),
        "created_at": now,
        "context_refs": [],
        "execution_mode": execution_mode,
        "response_mode": "smoke_probe",
        "response_carrier": {"status": "BYPASSED_FOR_EPHEMERAL_PLAYWRIGHT_SMOKE"},
        "persistence": "ephemeral_not_saved",
        "production_authority": False,
        "live_execution_authority": False,
    }
    return {
        "ok": True,
        "turn": turn,
        "assistant_turn": assistant_turn,
        "execution_mode": execution_mode,
        "queue_result": None,
        "runner_result": None,
        "execution_status_turn": None,
        "pipeline_run": None,
        "smoke_probe": {
            "schema_id": "ion.codex_capsule_chat_playwright_smoke_probe.v1",
            "persistence": "ephemeral_not_saved",
            "production_state_mutated": False,
            "response_carrier_invoked": False,
            "persist_override_env": PLAYWRIGHT_COCKPIT_SMOKE_PERSIST_ENV,
        },
        "model": build_dual_codex_chat_model(root, write=False),
        "production_authority": False,
        "live_execution_authority": False,
    }


def _raw_cli_timeout_seconds() -> int:
    try:
        value = int(str(os.environ.get(CHAT_RAW_CLI_TIMEOUT_ENV) or DEFAULT_RAW_CODEX_CLI_TIMEOUT_SECONDS))
    except (TypeError, ValueError):
        value = DEFAULT_RAW_CODEX_CLI_TIMEOUT_SECONDS
    return min(max(value, 30), 7200)


def _raw_codex_cli_service_tier() -> str:
    configured = str(os.environ.get(CHAT_RAW_CLI_SERVICE_TIER_ENV) or "").strip().lower()
    if configured == "flex":
        return DEFAULT_RAW_CLI_SERVICE_TIER
    if configured == "auto":
        return "auto"
    return configured or DEFAULT_RAW_CLI_SERVICE_TIER


def _resolve_root(root: str | Path | None = None) -> Path:
    return Path(root or ".").expanduser().resolve()


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _trim(value: Any, *, limit: int = 12000) -> str:
    text = str(value or "").replace("\r\n", "\n").strip()
    return text[:limit]


def _safe_codex_session_id(value: Any) -> str:
    text = _trim(value, limit=180)
    if not text:
        return ""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{5,179}", text):
        return ""
    return text


def _short_message(value: Any, *, limit: int = 1400) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n..."


def _runner_start_enabled() -> bool:
    return str(os.environ.get(CHAT_RUNNER_START_ENV) or "").strip().lower() in {"1", "true", "yes", "on"}


def _resolve_chat_execution_mode(value: Any = None) -> str:
    requested = str(value or os.environ.get(CHAT_EXECUTION_MODE_ENV) or DEFAULT_CHAT_EXECUTION_MODE).strip()
    return requested if requested in CHAT_EXECUTION_MODES else DEFAULT_CHAT_EXECUTION_MODE


def _resolve_codex_session_transport(value: Any = None) -> str:
    requested = str(value or DEFAULT_CHAT_CODEX_SESSION_TRANSPORT).strip().lower().replace("-", "_")
    return requested if requested in CHAT_CODEX_SESSION_TRANSPORTS else DEFAULT_CHAT_CODEX_SESSION_TRANSPORT


def resolve_chat_model_override(value: Any = None, *, selected_model: Any = None, thinking_mode: Any = None) -> dict[str, Any] | None:
    override = dict(value) if isinstance(value, Mapping) else {}
    model = str(selected_model or override.get("selected_model") or override.get("model") or "").strip()
    effort = str(
        thinking_mode
        or override.get("selected_reasoning_effort")
        or override.get("reasoning_effort")
        or override.get("thinking_mode")
        or "",
    ).strip()
    if model.lower() in {"", "auto", "default", "codex default"}:
        model = ""
    if effort.lower() in {"", "auto", "default"}:
        effort = ""
    if not model and not effort:
        return None
    return {
        "selected_model": model,
        "selected_reasoning_effort": effort,
    }


def _chat_execution_config(root: str | Path | None = None) -> dict[str, Any]:
    default_mode = _resolve_chat_execution_mode(None)
    runner_start_enabled = _runner_start_enabled()
    response_carrier = build_chat_response_carrier_status(root)
    allowed_modes = ["auto", "respond_only", "queue_for_codex"]
    if runner_start_enabled:
        allowed_modes.append("queue_and_start")
    return {
        "schema_id": "ion.codex_capsule_chat_execution_bridge.v1",
        "default_mode": default_mode,
        "allowed_modes": allowed_modes,
        "runner_start_enabled": runner_start_enabled,
        "runner_start_env": CHAT_RUNNER_START_ENV,
        "default_mode_env": CHAT_EXECUTION_MODE_ENV,
        "response_carrier_enabled": response_carrier.get("enabled"),
        "response_carrier_enabled_env": response_carrier.get("enabled_env"),
        "response_carrier_timeout_seconds": response_carrier.get("timeout_seconds"),
        "queue_owner": "ION/04_packages/kernel/ion_codex_queue_runner.py",
        "work_request_owner": "ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py",
        "global_codex_context_injection": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _state_path(root: Path) -> Path:
    return root / STATE_PATH


def _default_state() -> dict[str, Any]:
    now = _now()
    return {
        "schema_id": STATE_SCHEMA_ID,
        "created_at": now,
        "updated_at": now,
        "lanes": {
            lane_id: {
                "lane_id": lane_id,
                **config,
                "turns": [],
                "queue_links": [],
            }
            for lane_id, config in LANES.items()
        },
        "pipeline_runs": [],
        "memory": {
            "pins": [],
            "codex_memory_path": str(Path(os.environ.get(CODEX_MEMORY_ENV) or DEFAULT_CODEX_MEMORY_PATH)),
            "policy": "explicit_source_linked_repo_and_codex_memory",
        },
        "product_mode": {
            "primary_lane_id": "codex_general",
            "ion_comms_lane_id": "ion_system",
            "dual_chat_infrastructure": False,
            "global_codex_context_injection": False,
            "default_chat_execution_mode": _resolve_chat_execution_mode(None),
            "runner_start_enabled": _runner_start_enabled(),
            "policy": "one Capsule Codex chat with bounded ION comms adapter",
        },
        "mini_auto_post": {
            "enabled": True,
            "lane_id": "codex_general",
            "last_mini_sha256": None,
            "last_turn_id": None,
            "policy": "post_mini_to_chat_when_capsule_summary_changes",
        },
        "production_authority": False,
        "live_execution_authority": False,
    }


def load_dual_chat_state(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    state = _read_json(_state_path(shell_root)) or _default_state()
    state.setdefault("lanes", {})
    for lane_id, config in LANES.items():
        state["lanes"].setdefault(lane_id, {"lane_id": lane_id, **config, "turns": [], "queue_links": []})
        state["lanes"][lane_id].setdefault("turns", [])
        state["lanes"][lane_id].setdefault("queue_links", [])
    state.setdefault("pipeline_runs", [])
    state.setdefault("chat_branches", [])
    state.setdefault("chat_context_bindings", {})
    state.setdefault("active_chat_context_id", "")
    state.setdefault("fresh_agent_capsule_chats", [])
    state.setdefault("ide_context_bridges", [])
    state.setdefault("memory", {"pins": [], "codex_memory_path": str(DEFAULT_CODEX_MEMORY_PATH)})
    state["memory"].setdefault("pins", [])
    state.setdefault("product_mode", {})
    state["product_mode"].setdefault("primary_lane_id", "codex_general")
    state["product_mode"].setdefault("ion_comms_lane_id", "ion_system")
    state["product_mode"].setdefault("dual_chat_infrastructure", False)
    state["product_mode"].setdefault("global_codex_context_injection", False)
    state["product_mode"]["default_chat_execution_mode"] = _resolve_chat_execution_mode(None)
    state["product_mode"]["runner_start_enabled"] = _runner_start_enabled()
    state["product_mode"].setdefault("policy", "one Capsule Codex chat with bounded ION comms adapter")
    state.setdefault("mini_auto_post", {})
    state["mini_auto_post"].setdefault("enabled", True)
    state["mini_auto_post"].setdefault("lane_id", "codex_general")
    state["mini_auto_post"].setdefault("last_mini_sha256", None)
    state["mini_auto_post"].setdefault("last_turn_id", None)
    state["mini_auto_post"].setdefault("policy", "post_mini_to_chat_when_capsule_summary_changes")
    state.setdefault("production_authority", False)
    state.setdefault("live_execution_authority", False)
    return state


def save_dual_chat_state(root: str | Path | None, state: Mapping[str, Any]) -> None:
    shell_root = _resolve_root(root)
    payload = dict(state)
    payload["schema_id"] = STATE_SCHEMA_ID
    payload["updated_at"] = _now()
    payload["production_authority"] = False
    payload["live_execution_authority"] = False
    _write_json(_state_path(shell_root), payload)


def _relpath(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _latest_json_files(root: Path, rel: str, *, limit: int = 5) -> list[dict[str, Any]]:
    base = root / rel
    if not base.exists():
        return []
    files = sorted((path for path in base.rglob("*.json") if path.is_file()), key=lambda p: p.stat().st_mtime, reverse=True)
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "name": path.name,
            "mtime": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat(),
        }
        for path in files[:limit]
    ]


def _safe_read_repo_json(root: Path, rel_path: Any) -> dict[str, Any] | None:
    text = str(rel_path or "").strip()
    if not text:
        return None
    rel = Path(text)
    if rel.is_absolute() or ".." in rel.parts:
        return None
    target = (root / rel).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        return None
    if not target.is_file():
        return None
    payload = _read_json(target)
    return payload if isinstance(payload, dict) else None


def _json_packet_records(root: Path, rel_dir: Path, *, pattern: str = "*.json", limit: int = 400) -> list[dict[str, Any]]:
    base = root / rel_dir
    if not base.exists():
        return []
    paths = sorted(
        (path for path in base.rglob(pattern) if path.is_file()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    records: list[dict[str, Any]] = []
    for path in paths[:limit]:
        payload = _read_json(path)
        if not isinstance(payload, dict):
            continue
        records.append({
            "path": path.relative_to(root).as_posix(),
            "mtime": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat(),
            "packet": payload,
        })
    return records


def _decode_codex_jsonl_records(path: Path, *, limit: int = 500) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    records: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        logical_lines = [line]
        if line.startswith(("b'", 'b"')):
            try:
                decoded = ast.literal_eval(line)
                if isinstance(decoded, bytes):
                    logical_lines = decoded.decode("utf-8", errors="replace").splitlines()
            except Exception:
                logical_lines = [line]
        for logical_line in logical_lines:
            if len(records) >= limit:
                return records
            try:
                payload = json.loads(logical_line)
            except Exception:
                continue
            if isinstance(payload, Mapping):
                records.append(dict(payload))
    return records


def _codex_event_file_summary(root: Path, events_path: Any) -> dict[str, Any]:
    rel = str(events_path or "").strip()
    if not rel:
        return {
            "event_count": 0,
            "event_type_counts": {},
            "item_type_counts": {},
            "usage": {},
            "reasoning_output_tokens": None,
            "thinking_text_event_count": 0,
            "thinking_capture_status": "not_captured",
        }
    candidate = Path(rel)
    if candidate.is_absolute() or ".." in candidate.parts:
        payloads: list[dict[str, Any]] = []
    else:
        payloads = _decode_codex_jsonl_records(root / candidate)
    event_counts: dict[str, int] = {}
    item_counts: dict[str, int] = {}
    usage: dict[str, Any] = {}
    thinking_text_event_count = 0
    for payload in payloads:
        event_type = str(payload.get("type") or payload.get("event_type") or "unknown")
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
        item = payload.get("item") if isinstance(payload.get("item"), Mapping) else {}
        if item:
            item_type = str(item.get("type") or "unknown")
            item_counts[item_type] = item_counts.get(item_type, 0) + 1
            joined = " ".join(str(item.get(key) or "") for key in ("type", "title", "label", "summary")).lower()
            if "thinking" in joined or "reasoning_summary" in joined:
                thinking_text_event_count += 1
        if event_type == "turn.completed" and isinstance(payload.get("usage"), Mapping):
            usage.update(dict(payload["usage"]))
    reasoning_tokens = usage.get("reasoning_output_tokens")
    if thinking_text_event_count:
        capture_status = "thinking_text_events"
    elif reasoning_tokens is not None:
        capture_status = "usage_tokens_available"
    elif payloads:
        capture_status = "status_events_available"
    else:
        capture_status = "not_captured"
    return {
        "event_count": len(payloads),
        "event_type_counts": event_counts,
        "item_type_counts": item_counts,
        "usage": usage,
        "reasoning_output_tokens": reasoning_tokens,
        "thinking_text_event_count": thinking_text_event_count,
        "thinking_capture_status": capture_status,
    }


def _index_records(records: list[dict[str, Any]], *field_names: str) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        payload = record.get("packet") if isinstance(record.get("packet"), Mapping) else {}
        for field in field_names:
            value = str(payload.get(field) or "").strip()
            if value:
                index.setdefault(value, []).append(record)
    return index


def _dedupe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for record in records:
        path = str(record.get("path") or "")
        if not path or path in seen:
            continue
        seen.add(path)
        deduped.append(record)
    return deduped


def _records_for_request(
    root: Path,
    request: Mapping[str, Any],
    *,
    run_index: Mapping[str, list[dict[str, Any]]],
    return_index: Mapping[str, list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    request_id = str(request.get("request_id") or "").strip()
    request_path = str(request.get("packet_path") or request.get("work_request_path") or "").strip()
    runs: list[dict[str, Any]] = []
    returns: list[dict[str, Any]] = []
    for key in (request_id, request_path):
        if key:
            runs.extend(run_index.get(key, []))
            returns.extend(return_index.get(key, []))
    for rel_path in request.get("codex_queue_runner_runs") or []:
        payload = _safe_read_repo_json(root, rel_path)
        if isinstance(payload, dict):
            runs.append({"path": str(rel_path), "packet": payload, "mtime": payload.get("updated_at") or payload.get("created_at")})
    for rel_path in request.get("return_packet_paths") or []:
        payload = _safe_read_repo_json(root, rel_path)
        if isinstance(payload, dict):
            returns.append({"path": str(rel_path), "packet": payload, "mtime": payload.get("created_at")})
    latest_return = str(request.get("latest_return_packet_path") or "").strip()
    if latest_return:
        payload = _safe_read_repo_json(root, latest_return)
        if isinstance(payload, dict):
            returns.append({"path": latest_return, "packet": payload, "mtime": payload.get("created_at")})
    return _dedupe_records(runs), _dedupe_records(returns)


def _proof_status(request: Mapping[str, Any], latest_return: Mapping[str, Any] | None) -> str:
    status = str(request.get("status") or "").upper()
    if latest_return:
        accepted = latest_return.get("accepted_for_carrier_intake")
        if accepted is True:
            return "accepted"
        if accepted is False:
            return "blocked"
    if request.get("latest_context_proof_accepted") is True and request.get("latest_template_action_proof_accepted") is True:
        return "accepted"
    if "BLOCKED" in status or "FAILED" in status or "REFUSED" in status:
        return "blocked"
    if "RETURN_RECORDED" in status:
        return "returned"
    if "RUNNING" in status or "CLAIMED" in status:
        return "running"
    return "pending"


def _trace_event(
    *,
    event_type: str,
    label: str,
    status: str,
    timestamp: Any = None,
    detail: Any = None,
    source_refs: list[str] | None = None,
    tool_name: str | None = None,
    model_move: Mapping[str, Any] | None = None,
    proof_status: str | None = None,
) -> dict[str, Any]:
    return {
        "event_type": event_type,
        "label": label,
        "status": status,
        "timestamp": timestamp,
        "detail": _short_message(detail, limit=420) if detail else "",
        "source_refs": [str(ref) for ref in source_refs or [] if ref],
        "tool_name": tool_name,
        "model_move": dict(model_move) if isinstance(model_move, Mapping) else None,
        "proof_status": proof_status,
        "raw_hidden_reasoning_exposed": False,
    }


def build_codex_capsule_turn_trace_model(
    state: Mapping[str, Any],
    *,
    codex_solo_context: Mapping[str, Any],
    codex_status: Mapping[str, Any],
    return_hydration: Mapping[str, Any],
) -> dict[str, Any]:
    lanes = state.get("lanes") if isinstance(state.get("lanes"), Mapping) else {}
    codex_lane = lanes.get("codex_general") if isinstance(lanes.get("codex_general"), Mapping) else {}
    turns = [turn for turn in codex_lane.get("turns", []) if isinstance(turn, Mapping)]
    return_records = [record for record in return_hydration.get("records", []) if isinstance(record, Mapping)]
    returns_by_source: dict[str, list[Mapping[str, Any]]] = {}
    for record in return_records:
        source_turn_id = str(record.get("source_turn_id") or "").strip()
        if source_turn_id:
            returns_by_source.setdefault(source_turn_id, []).append(record)
    capsule_refs = [
        CAPSULE_PATH.as_posix(),
        MINI_PATH.as_posix(),
        HOT_CONTEXT_PATH.as_posix(),
        LONG_HORIZON_PATH.as_posix(),
        CONTEXT_PACKAGES_PATH.as_posix(),
        ROUTE_PATH.as_posix(),
    ]
    trace_records: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_turn in turns:
        turn = dict(raw_turn)
        kind = str(turn.get("kind") or "chat_turn")
        author = str(turn.get("author") or "")
        if kind == "chat_turn" and author in {"operator", "user"}:
            current = {
                "schema_id": "ion.codex_capsule_chat_turn_trace.v1",
                "turn_id": turn.get("turn_id"),
                "created_at": turn.get("created_at"),
                "execution_mode": turn.get("execution_mode"),
                "events": [
                    _trace_event(
                        event_type="operator_message",
                        label="Message received",
                        status="received",
                        timestamp=turn.get("created_at"),
                        detail=turn.get("message"),
                    ),
                    _trace_event(
                        event_type="context_mount",
                        label="Capsule context mounted",
                        status="ready" if codex_solo_context.get("ok") else "blocked",
                        timestamp=turn.get("created_at"),
                        detail=codex_solo_context.get("verdict"),
                        source_refs=capsule_refs,
                    ),
                ],
                "policy": "transparent_events_with_thinking_status_capture",
                "raw_hidden_reasoning_exposed": False,
                "production_authority": False,
                "live_execution_authority": False,
            }
            trace_records.append(current)
            skill_activation = turn.get("skill_activation") if isinstance(turn.get("skill_activation"), Mapping) else None
            if skill_activation:
                current["events"].append(_trace_event(
                    event_type="skill_activation",
                    label="Skill activated",
                    status="ready" if skill_activation.get("ok") else "blocked",
                    timestamp=turn.get("created_at"),
                    detail=(
                        f"{skill_activation.get('display_name')} / {skill_activation.get('skill_id')}\n"
                        f"{skill_activation.get('selection_reason')}\n"
                        "Templates remain proof gates."
                    ),
                    source_refs=skill_activation.get("activates_templates") if isinstance(skill_activation.get("activates_templates"), list) else [],
                    model_move=skill_activation.get("model_route") if isinstance(skill_activation.get("model_route"), Mapping) else None,
                ))
            chat_engine = turn.get("chat_engine") if isinstance(turn.get("chat_engine"), Mapping) else None
            if chat_engine:
                native_lenses = chat_engine.get("native_lenses") if isinstance(chat_engine.get("native_lenses"), list) else []
                assistant_work_route = chat_engine.get("assistant_work_route") if isinstance(chat_engine.get("assistant_work_route"), Mapping) else {}
                model_move = chat_engine.get("model_move") if isinstance(chat_engine.get("model_move"), Mapping) else {}
                current["events"].append(_trace_event(
                    event_type="chat_engine",
                    label="Chat engine route",
                    status=str(chat_engine.get("response_mode") or "answer"),
                    timestamp=turn.get("created_at"),
                    detail=(
                        f"mode: {chat_engine.get('response_mode')}\n"
                        f"strategy: {(chat_engine.get('carrier_strategy') or {}).get('mode') if isinstance(chat_engine.get('carrier_strategy'), Mapping) else 'unknown'}\n"
                        f"native_lenses: {', '.join(str(lens.get('display_name')) for lens in native_lenses[:6] if isinstance(lens, Mapping))}"
                    ),
                    source_refs=(chat_engine.get("context_mount") or {}).get("context_refs") if isinstance(chat_engine.get("context_mount"), Mapping) else [],
                    model_move=model_move,
                ))
                if model_move:
                    selection_reason = model_move.get("selection_reason") if isinstance(model_move.get("selection_reason"), list) else []
                    current["events"].append(_trace_event(
                        event_type="thinking_status",
                        label="Thinking/status",
                        status=str(model_move.get("selected_reasoning_effort") or "unknown"),
                        timestamp=turn.get("created_at"),
                        detail=(
                            f"model: {model_move.get('selected_model') or 'unknown'}\n"
                            f"work_class: {model_move.get('work_class') or 'unknown'}\n"
                            f"stage: {model_move.get('ion_stage_id') or 'unknown'}\n"
                            f"usage_pool: {model_move.get('usage_pool_id') or 'unknown'} / {model_move.get('usage_pool_authority') or 'not_authoritative'}\n"
                            f"selection: {', '.join(str(item) for item in selection_reason[:6]) or 'not recorded'}\n"
                            "capture: visible Codex CLI status and usage telemetry when present"
                        ),
                        source_refs=[
                            "ION/02_architecture/CODEX_CARRIER_LIMITS_CONTEXT_PROTOCOL.md",
                            "ION/03_registry/codex_carrier_limits_registry.yaml",
                        ],
                        model_move=model_move,
                    ))
                if assistant_work_route:
                    current["events"].append(_trace_event(
                        event_type="assistant_work_route",
                        label="Assistant work route",
                        status=str(assistant_work_route.get("route_id") or assistant_work_route.get("verdict") or "candidate_unavailable"),
                        timestamp=turn.get("created_at"),
                        detail=(
                            f"route: {assistant_work_route.get('route_id') or 'unavailable'}\n"
                            f"basis: {assistant_work_route.get('selection_basis') or assistant_work_route.get('finding') or 'candidate'}\n"
                            f"domains: {', '.join(str(item) for item in (assistant_work_route.get('candidate_domains') or [])[:6])}\n"
                            f"agents: {', '.join(str(item) for item in (assistant_work_route.get('candidate_agents') or [])[:6])}"
                        ),
                        source_refs=[
                            "ION/05_context/current/ai_assistant_work/registries/AI_ASSISTANT_WORK_ROUTE_REGISTRY_CANDIDATE_V0_1.yaml",
                            "ION/05_context/current/ai_assistant_work/route_compiler",
                        ],
                    ))
            continue
        if current is None:
            continue
        if kind == "assistant_response":
            response_carrier = turn.get("response_carrier") if isinstance(turn.get("response_carrier"), Mapping) else None
            if response_carrier:
                run = response_carrier.get("run") if isinstance(response_carrier.get("run"), Mapping) else {}
                refs = [
                    str(run.get("run_packet_path") or ""),
                    str(run.get("latest_return_path") or ""),
                    str(run.get("events_path") or ""),
                ]
                current["events"].append(_trace_event(
                    event_type="codex_chat_response_carrier",
                    label="Response carrier",
                    status=str(response_carrier.get("status") or response_carrier.get("finding") or "unknown"),
                    timestamp=turn.get("created_at"),
                    detail=response_carrier.get("finding") or response_carrier.get("response_text") or "No carrier response captured.",
                    source_refs=[ref for ref in refs if ref],
                    tool_name="codex exec",
                    model_move=turn.get("codex_model_move") if isinstance(turn.get("codex_model_move"), Mapping) else None,
                ))
            current["events"].append(_trace_event(
                event_type="assistant_response",
                label="Assistant response",
                status="visible",
                timestamp=turn.get("created_at"),
                detail=turn.get("message"),
                source_refs=turn.get("context_refs") if isinstance(turn.get("context_refs"), list) else [],
                model_move=turn.get("codex_model_move") if isinstance(turn.get("codex_model_move"), Mapping) else None,
            ))
        elif kind == "execution_status":
            packet_path = str(turn.get("packet_path") or "")
            request_id = str(turn.get("request_id") or "")
            current["events"].append(_trace_event(
                event_type="tool_call",
                label="Codex queue request",
                status=str(turn.get("queue_status") or "requested"),
                timestamp=turn.get("created_at"),
                detail=f"{request_id}\n{packet_path}".strip(),
                source_refs=[packet_path] if packet_path else [],
                tool_name="ion_request_codex_work_packet",
            ))
            runner_result = turn.get("runner_result") if isinstance(turn.get("runner_result"), Mapping) else None
            if runner_result:
                current["events"].append(_trace_event(
                    event_type="runner",
                    label="Runner start request",
                    status=str(runner_result.get("result") or runner_result.get("finding") or "not_started"),
                    timestamp=turn.get("created_at"),
                    detail=runner_result.get("finding") or runner_result.get("result"),
                    tool_name="ion_codex_queue_process_once",
                ))
    for trace in trace_records:
        source_turn_id = str(trace.get("turn_id") or "")
        linked_returns = returns_by_source.get(source_turn_id, [])
        if not any(event.get("event_type") == "tool_call" for event in trace.get("events", [])):
            trace["events"].append(_trace_event(
                event_type="execution_bridge",
                label="Codex execution bridge",
                status="not_requested",
                timestamp=trace.get("created_at"),
                detail="Normal chat response only.",
            ))
        for record in linked_returns:
            refs = [ref for ref in record.get("path_refs", []) if ref] if isinstance(record.get("path_refs"), list) else []
            trace["events"].append(_trace_event(
                event_type="proof_return",
                label="Task return proof",
                status=str(record.get("status") or "returned"),
                timestamp=record.get("latest_return_path") or record.get("latest_run_path"),
                detail=record.get("task_output_preview") or record.get("latest_return_path"),
                source_refs=refs,
                tool_name="ion_submit_task_return",
                proof_status=str(record.get("proof_status") or "pending"),
            ))
        trace["event_count"] = len(trace.get("events", []))
    return {
        "schema_id": "ion.codex_capsule_chat_turn_trace_index.v1",
        "trace_count": len(trace_records),
        "traces": trace_records,
        "runner_active": codex_status.get("active_process_running", False),
        "queued_request_count": codex_status.get("queued_request_count", 0),
        "policy": "show_context_tool_queue_file_proof_and_thinking_status_events",
        "raw_hidden_reasoning_exposed": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def build_codex_capsule_agent_surface(root: Path) -> dict[str, Any]:
    try:
        roster = list_agents(root)
        queue = agent_queue(root, limit=12)
        agents = roster.get("agents") if isinstance(roster.get("agents"), list) else []
        invocations = queue.get("invocations") if isinstance(queue.get("invocations"), list) else []
        return {
            "schema_id": "ion.codex_capsule_chat_agent_surface.v1",
            "verdict": "ION_CODEX_CAPSULE_AGENT_SURFACE_READY",
            "agent_count": roster.get("agent_count", len(agents)),
            "available_agents": agents[:24],
            "invocation_count": queue.get("invocation_count", len(invocations)),
            "recent_invocations": invocations,
            "broker_owner": "ION/04_packages/kernel/ion_agent_invocation_broker.py",
            "creates_second_agent_system": False,
            "creates_second_queue": False,
            "policy": "read_only_projection_of_existing_ion_agent_invocation_broker",
            "production_authority": False,
            "live_execution_authority": False,
        }
    except Exception as exc:  # pragma: no cover - defensive UI projection
        return {
            "schema_id": "ion.codex_capsule_chat_agent_surface.v1",
            "verdict": "ION_CODEX_CAPSULE_AGENT_SURFACE_BLOCKED",
            "finding": str(exc),
            "agent_count": 0,
            "available_agents": [],
            "invocation_count": 0,
            "recent_invocations": [],
            "creates_second_agent_system": False,
            "creates_second_queue": False,
            "production_authority": False,
            "live_execution_authority": False,
        }


def build_codex_return_hydration(root: Path, state: Mapping[str, Any]) -> dict[str, Any]:
    lanes = state.get("lanes") if isinstance(state.get("lanes"), Mapping) else {}
    codex_lane = lanes.get("codex_general") if isinstance(lanes.get("codex_general"), Mapping) else {}
    turns = [turn for turn in codex_lane.get("turns", []) if isinstance(turn, Mapping)]
    queue_links = [link for link in codex_lane.get("queue_links", []) if isinstance(link, Mapping)]
    request_records = _json_packet_records(root, CODEX_WORK_REQUESTS_DIR)
    run_records = _json_packet_records(root, CODEX_QUEUE_RUNS_DIR, pattern="run.json")
    return_records = _json_packet_records(root, CODEX_TASK_RETURNS_DIR)
    request_index = _index_records(request_records, "request_id", "packet_path")
    run_index = _index_records(run_records, "request_id", "request_path")
    return_index = _index_records(return_records, "work_request_id", "work_request_path")
    sources: list[dict[str, Any]] = []
    seen_sources: set[tuple[str, str | None]] = set()
    for turn in turns:
        if turn.get("kind") != "execution_status":
            continue
        request_id = str(turn.get("request_id") or "").strip()
        packet_path = str(turn.get("packet_path") or "").strip()
        if not request_id and not packet_path:
            continue
        key = (request_id or packet_path, str(turn.get("source_turn_id") or ""))
        if key in seen_sources:
            continue
        seen_sources.add(key)
        sources.append({
            "request_id": request_id,
            "request_path": packet_path,
            "source_turn_id": turn.get("source_turn_id"),
            "execution_turn_id": turn.get("turn_id"),
            "queued_at": turn.get("created_at"),
            "queue_status": turn.get("queue_status"),
        })
    for link in queue_links:
        request_id = str(link.get("request_id") or "").strip()
        packet_path = str(link.get("packet_path") or "").strip()
        if not request_id and not packet_path:
            continue
        key = (request_id or packet_path, str(link.get("source_turn_id") or ""))
        if key in seen_sources:
            continue
        seen_sources.add(key)
        sources.append({
            "request_id": request_id,
            "request_path": packet_path,
            "source_turn_id": link.get("source_turn_id"),
            "execution_turn_id": None,
            "queued_at": link.get("created_at"),
            "queue_status": link.get("status"),
        })
    records: list[dict[str, Any]] = []
    for source in sources:
        request_id = str(source.get("request_id") or "").strip()
        request_path = str(source.get("request_path") or "").strip()
        matches: list[dict[str, Any]] = []
        for key in (request_id, request_path):
            if key:
                matches.extend(request_index.get(key, []))
        if request_path and not matches:
            payload = _safe_read_repo_json(root, request_path)
            if isinstance(payload, dict):
                matches.append({"path": request_path, "packet": payload, "mtime": payload.get("updated_at") or payload.get("created_at")})
        request_record = _dedupe_records(matches)[0] if matches else {"path": request_path, "packet": {}, "mtime": None}
        request = request_record.get("packet") if isinstance(request_record.get("packet"), Mapping) else {}
        runs, returns = _records_for_request(root, request, run_index=run_index, return_index=return_index) if request else ([], [])
        latest_run_record = runs[0] if runs else None
        latest_return_record = returns[0] if returns else None
        latest_run = latest_run_record.get("packet") if isinstance(latest_run_record, Mapping) and isinstance(latest_run_record.get("packet"), Mapping) else None
        latest_return = latest_return_record.get("packet") if isinstance(latest_return_record, Mapping) and isinstance(latest_return_record.get("packet"), Mapping) else None
        proof = _proof_status(request, latest_return)
        status = (
            request.get("status")
            or (latest_run or {}).get("status")
            or source.get("queue_status")
            or "QUEUED_FOR_CODEX_CARRIER"
        )
        template_result = latest_return.get("template_action_proof_result") if isinstance(latest_return, Mapping) and isinstance(latest_return.get("template_action_proof_result"), Mapping) else {}
        context_result = latest_return.get("context_proof_result") if isinstance(latest_return, Mapping) and isinstance(latest_return.get("context_proof_result"), Mapping) else {}
        path_refs = [
            request_record.get("path"),
            latest_run_record.get("path") if latest_run_record else None,
            latest_return_record.get("path") if latest_return_record else None,
        ]
        records.append({
            "schema_id": "ion.codex_capsule_chat_return_hydration_record.v1",
            "source_turn_id": source.get("source_turn_id"),
            "execution_turn_id": source.get("execution_turn_id"),
            "request_id": request.get("request_id") or request_id or None,
            "request_path": request_record.get("path") or request_path or None,
            "status": status,
            "proof_status": proof,
            "context_proof_accepted": context_result.get("accepted") if context_result else request.get("latest_context_proof_accepted"),
            "template_action_proof_accepted": template_result.get("accepted") if template_result else request.get("latest_template_action_proof_accepted"),
            "context_proof_findings": context_result.get("findings") or [],
            "template_action_proof_findings": template_result.get("findings") or [],
            "touched_paths": template_result.get("touched_paths") or [],
            "task_output_preview": _short_message((latest_return or {}).get("task_output_preview"), limit=900) if latest_return else "",
            "latest_run_path": latest_run_record.get("path") if latest_run_record else None,
            "latest_run_status": (latest_run or {}).get("status"),
            "latest_return_path": latest_return_record.get("path") if latest_return_record else None,
            "accepted_for_carrier_intake": (latest_return or {}).get("accepted_for_carrier_intake") if latest_return else None,
            "path_refs": [path for path in path_refs if path],
            "production_authority": False,
            "live_execution_authority": False,
        })
    return {
        "schema_id": "ion.codex_capsule_chat_return_hydration.v1",
        "record_count": len(records),
        "accepted_count": sum(1 for record in records if record.get("proof_status") == "accepted"),
        "blocked_count": sum(1 for record in records if record.get("proof_status") == "blocked"),
        "records": records,
        "policy": "read_only_projection_from_existing_codex_queue_runs_and_task_returns",
        "production_authority": False,
        "live_execution_authority": False,
    }


def build_codex_chat_response_run_surface(root: Path) -> dict[str, Any]:
    records = []
    for record in _json_packet_records(root, RESPONSE_RUNS_DIR, pattern="run.json", limit=24):
        packet = record.get("packet") if isinstance(record.get("packet"), Mapping) else {}
        unexpected = packet.get("unexpected_worktree_changes") if isinstance(packet.get("unexpected_worktree_changes"), list) else []
        event_summary = _codex_event_file_summary(root, packet.get("events_path"))
        records.append({
            "schema_id": "ion.codex_chat_response_run_record.v1",
            "path": record.get("path"),
            "mtime": record.get("mtime"),
            "run_id": packet.get("run_id"),
            "created_at": packet.get("created_at"),
            "updated_at": packet.get("updated_at"),
            "status": packet.get("status"),
            "ok": packet.get("ok"),
            "finding": packet.get("finding"),
            "selected_model": packet.get("selected_model"),
            "selected_reasoning_effort": packet.get("selected_reasoning_effort"),
            "prompt_path": packet.get("prompt_path"),
            "latest_return_path": packet.get("latest_return_path"),
            "events_path": packet.get("events_path"),
            "stdout_path": packet.get("stdout_path"),
            "stderr_path": packet.get("stderr_path"),
            "event_count": event_summary.get("event_count"),
            "event_type_counts": event_summary.get("event_type_counts"),
            "item_type_counts": event_summary.get("item_type_counts"),
            "usage": event_summary.get("usage"),
            "reasoning_output_tokens": event_summary.get("reasoning_output_tokens"),
            "thinking_text_event_count": event_summary.get("thinking_text_event_count"),
            "thinking_capture_status": event_summary.get("thinking_capture_status"),
            "response_sha256": packet.get("response_sha256"),
            "operator_message_sha256": packet.get("operator_message_sha256"),
            "unexpected_worktree_change_count": len(unexpected),
            "production_authority": False,
            "live_execution_authority": False,
        })
    return {
        "schema_id": "ion.codex_chat_response_run_surface.v1",
        "run_root": RESPONSE_RUNS_DIR.as_posix(),
        "record_count": len(records),
        "latest_status": records[0].get("status") if records else "none",
        "records": records,
        "policy": "read_only_response_carrier_run_prompt_return_event_projection",
        "production_authority": False,
        "live_execution_authority": False,
    }


def _turn_digest(turns: list[dict[str, Any]], *, limit: int = 4) -> list[dict[str, Any]]:
    digest = []
    for turn in turns[-limit:]:
        digest.append({
            "turn_id": turn.get("turn_id"),
            "author": turn.get("author"),
            "created_at": turn.get("created_at"),
            "summary": str(turn.get("message") or "")[:240],
        })
    return digest


def _build_shared_digest(state: Mapping[str, Any], codex_status: Mapping[str, Any]) -> dict[str, Any]:
    lanes = state.get("lanes") if isinstance(state.get("lanes"), Mapping) else {}
    ion_turns = list((lanes.get("ion_system") or {}).get("turns") or []) if isinstance(lanes.get("ion_system"), Mapping) else []
    codex_turns = list((lanes.get("codex_general") or {}).get("turns") or []) if isinstance(lanes.get("codex_general"), Mapping) else []
    latest_run = None
    latest_runs = codex_status.get("latest_runs") if isinstance(codex_status.get("latest_runs"), list) else []
    if latest_runs:
        latest_run = latest_runs[0]
    return {
        "schema_id": "ion.codex_capsule_chat_comms_digest.v1",
        "policy": "bounded_digest_not_full_transcript_by_default",
        "ion_comms_visible_to_capsule_codex": _turn_digest(ion_turns),
        "capsule_codex_visible_to_ion_comms": _turn_digest(codex_turns),
        "memory_pin_count": len((state.get("memory") or {}).get("pins") or []) if isinstance(state.get("memory"), Mapping) else 0,
        "codex_queue": {
            "queued_request_count": codex_status.get("queued_request_count", 0),
            "active_process_running": codex_status.get("active_process_running", False),
            "latest_run": latest_run,
        },
    }


def _mini_text(codex_solo_context: Mapping[str, Any]) -> str:
    mini = codex_solo_context.get("mini") if isinstance(codex_solo_context.get("mini"), Mapping) else {}
    return str(mini.get("text") or "").strip()


def _mini_auto_post_message(codex_solo_context: Mapping[str, Any], mini_sha: str) -> str:
    mini = _mini_text(codex_solo_context)
    capsule = codex_solo_context.get("capsule") if isinstance(codex_solo_context.get("capsule"), Mapping) else {}
    capsule_tail = capsule.get("tail") if isinstance(capsule.get("tail"), list) else []
    capsule_ref = CAPSULE_PATH.as_posix()
    latest_capsule_row = str(capsule_tail[-1]) if capsule_tail else "none"
    return "\n".join([
        "ION Mini capsule brief",
        f"mini_ref: {MINI_PATH.as_posix()}",
        f"capsule_ref: {capsule_ref}",
        f"mini_sha256: {mini_sha}",
        f"latest_capsule_row: {latest_capsule_row}",
        "",
        mini or "Mini not initialized.",
    ])


def _sync_mini_auto_post(
    state: dict[str, Any],
    codex_solo_context: Mapping[str, Any],
    *,
    reason: str,
) -> dict[str, Any]:
    config = state.setdefault("mini_auto_post", {})
    if config.get("enabled") is False:
        return {"ok": True, "posted": False, "finding": "mini_auto_post_disabled"}
    lane_id = str(config.get("lane_id") or "codex_general")
    if lane_id not in LANES:
        return {"ok": False, "posted": False, "finding": "mini_auto_post_lane_unknown", "lane_id": lane_id}
    mini = _mini_text(codex_solo_context)
    if not mini:
        return {"ok": False, "posted": False, "finding": "mini_text_missing"}
    mini_sha = _sha256_text(mini)
    if config.get("last_mini_sha256") == mini_sha:
        return {"ok": True, "posted": False, "finding": "mini_unchanged", "mini_sha256": mini_sha}
    now = _now()
    turn_id = f"mini_{now.replace(':', '').replace('+', 'Z')}_{mini_sha[:12]}"
    turn = {
        "turn_id": turn_id,
        "lane_id": lane_id,
        "author": "ion_context",
        "kind": "mini_auto_post",
        "message": _mini_auto_post_message(codex_solo_context, mini_sha),
        "message_sha256": _sha256_text(_mini_auto_post_message(codex_solo_context, mini_sha)),
        "created_at": now,
        "reason": reason,
        "mini_ref": MINI_PATH.as_posix(),
        "capsule_ref": CAPSULE_PATH.as_posix(),
        "mini_sha256": mini_sha,
        "production_authority": False,
        "live_execution_authority": False,
    }
    state["lanes"][lane_id].setdefault("turns", []).append(turn)
    config["last_mini_sha256"] = mini_sha
    config["last_turn_id"] = turn_id
    config["last_posted_at"] = now
    config["last_reason"] = reason
    return {"ok": True, "posted": True, "turn": turn, "mini_sha256": mini_sha}


def build_dual_codex_chat_model(root: str | Path | None = None, *, write: bool = False) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    state = load_dual_chat_state(shell_root)
    codex_status = build_codex_queue_runner_status(shell_root, reconcile=False)
    codex_solo_context = build_codex_solo_context_model(shell_root, write=write)
    mini_auto_post = _sync_mini_auto_post(state, codex_solo_context, reason="codex_capsule_chat_model_refresh") if write else {
        "ok": True,
        "posted": False,
        "finding": "write_not_requested",
        "mini_sha256": _sha256_text(_mini_text(codex_solo_context)) if _mini_text(codex_solo_context) else None,
    }
    if write and mini_auto_post.get("posted"):
        save_dual_chat_state(shell_root, state)
    lanes = json.loads(json.dumps(state.get("lanes", {})))
    if isinstance(lanes.get("codex_general"), dict):
        lanes["codex_general"]["context_substrate"] = {
            "schema_id": codex_solo_context.get("schema_id"),
            "verdict": codex_solo_context.get("verdict"),
            "active_context": codex_solo_context.get("active_context"),
            "paths": codex_solo_context.get("paths"),
            "witness_policy": codex_solo_context.get("witness_policy"),
        }
        lanes["codex_general"]["mini_auto_post"] = state.get("mini_auto_post")
    stage_model_moves = build_stage_model_move_matrix(ION_PIPELINE_STAGES, routing_posture=DEFAULT_ROUTING_POSTURE)
    return_hydration = build_codex_return_hydration(shell_root, state)
    response_runs = build_codex_chat_response_run_surface(shell_root)
    turn_traces = build_codex_capsule_turn_trace_model(
        state,
        codex_solo_context=codex_solo_context,
        codex_status=codex_status,
        return_hydration=return_hydration,
    )
    agent_surface = build_codex_capsule_agent_surface(shell_root)
    skill_surface = build_ion_skill_surface(
        shell_root,
        lane_id="codex_general",
        objective="model refresh",
        execution_mode=DEFAULT_CHAT_EXECUTION_MODE,
        codex_solo_context=codex_solo_context,
    )
    chat_engine_surface = build_codex_chat_engine_surface(shell_root)
    chat_response_carrier = build_chat_response_carrier_status(shell_root)
    memory_visualization = build_codex_chat_memory_visualization(
        state=state,
        codex_solo_context=codex_solo_context,
        turn_traces=turn_traces,
        return_hydration=return_hydration,
        codex_status=codex_status,
    )
    model = {
        "schema_id": SCHEMA_ID,
        "verdict": READY_VERDICT,
        "generated_at": _now(),
        "state_path": STATE_PATH.as_posix(),
        "model_path": MODEL_PATH.as_posix(),
        "product": {
            "name": "ION Codex Chat",
            "primary_lane_id": "codex_general",
            "ion_comms_lane_id": "ion_system",
            "dual_chat_infrastructure": False,
            "chat_first": True,
            "global_codex_context_injection": False,
            "acceptance_gate": "operator_message_produces_visible_assistant_response",
            "policy": "Build one Capsule-backed Codex chat and communicate with full ION through existing comms/receipts.",
        },
        "execution_bridge": _chat_execution_config(shell_root),
        "lanes": lanes,
        "pipeline_runs": list(state.get("pipeline_runs") or [])[-12:],
        "chat_branches": list(state.get("chat_branches") or [])[-80:],
        "fresh_agent_capsule_chats": list(state.get("fresh_agent_capsule_chats") or [])[-80:],
        "chat_context": _build_chat_context_surface(state),
        "ide_context_bridge": _build_ide_context_bridge_surface(state),
        "memory": state.get("memory", {}),
        "product_mode": state.get("product_mode", {}),
        "codex_solo_context": codex_solo_context,
        "mini_auto_post": {
            **(state.get("mini_auto_post") if isinstance(state.get("mini_auto_post"), Mapping) else {}),
            "sync_result": mini_auto_post,
        },
        "model_moves": {
            "schema_id": "ion.codex_capsule_chat_model_moves.v1",
            "routing_posture": DEFAULT_ROUTING_POSTURE,
            "usage_limits_authoritative": False,
            "stage_defaults": stage_model_moves,
            "profiles": list_codex_model_profiles(),
            "production_authority": False,
            "live_execution_authority": False,
        },
        "shared_digest": _build_shared_digest(state, codex_status),
        "ion_comms": {
            "schema_id": "ion.codex_capsule_chat_ion_comms_adapter.v1",
            "mode": "existing_ion_comms_adapter",
            "primary_chat_is": "codex_general",
            "ion_comms_lane_id": "ion_system",
            "uses_existing_ion_owners": True,
            "creates_second_queue": False,
            "creates_second_agent_system": False,
            "digest": _build_shared_digest(state, codex_status),
            "front_door_adapter": "ION/04_packages/kernel/front_door_chat_orchestration.py",
            "codex_queue_owner": "ION/04_packages/kernel/ion_codex_queue_runner.py",
            "production_authority": False,
            "live_execution_authority": False,
        },
        "codex_queue": {
            "runner": codex_status,
            "work_queue_path": CODEX_WORK_QUEUE_INDEX.as_posix(),
            "latest_work_requests": _latest_json_files(shell_root, "ION/05_context/current/chatgpt_connector/codex_work_requests", limit=5),
            "latest_task_returns": _latest_json_files(shell_root, "ION/05_context/current/chatgpt_connector/task_returns", limit=5),
            "return_hydration": return_hydration,
        },
        "raw_codex_cli": state.get("raw_codex_cli") if isinstance(state.get("raw_codex_cli"), Mapping) else {},
        "codex_app_server": state.get("codex_app_server") if isinstance(state.get("codex_app_server"), Mapping) else {},
        "response_runs": response_runs,
        "turn_traces": turn_traces,
        "memory_visualization": memory_visualization,
        "agents": agent_surface,
        "skills": skill_surface,
        "chat_engine": chat_engine_surface,
        "service_console": build_service_console_model(shell_root),
        "assistant_work_routes": chat_engine_surface.get("assistant_work_routes") if isinstance(chat_engine_surface.get("assistant_work_routes"), Mapping) else {},
        "chat_response_carrier": chat_response_carrier,
        "remote_access": {
            "public_cockpit_path": "https://ion.helixion.net/cockpit/chat",
            "requires_token_env": "ION_COCKPIT_PUBLIC_TOKEN",
            "enabled_by_model": bool(os.environ.get("ION_COCKPIT_PUBLIC_TOKEN")),
        },
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "arbitrary_shell": False,
            "git_push": False,
            "proof_gates_required": True,
        },
        "production_authority": False,
        "live_execution_authority": False,
    }
    model["ui"] = build_codex_capsule_chat_ui_model(model)
    if write:
        _write_json(shell_root / MODEL_PATH, model)
    return model


def _codex_solo_context_refs(solo_context: Mapping[str, Any]) -> list[str]:
    refs = [
        CAPSULE_PATH.as_posix(),
        HOT_CONTEXT_PATH.as_posix(),
        MINI_PATH.as_posix(),
        LONG_HORIZON_PATH.as_posix(),
        CONTEXT_PACKAGES_PATH.as_posix(),
        ROUTE_PATH.as_posix(),
    ]
    route = solo_context.get("route") if isinstance(solo_context.get("route"), Mapping) else {}
    entries = route.get("entries") if isinstance(route.get("entries"), list) else []
    for entry in entries:
        if isinstance(entry, Mapping) and entry.get("path"):
            ref = str(entry["path"])
            if ref not in refs:
                refs.append(ref)
    return refs


def _merge_context_refs(*groups: Any) -> list[str]:
    refs: list[str] = []
    seen: set[str] = set()
    for group in groups:
        if isinstance(group, str):
            values = [group]
        elif isinstance(group, list):
            values = group
        elif isinstance(group, tuple):
            values = list(group)
        else:
            values = []
        for value in values:
            ref = str(value or "").strip().lstrip("@")
            if not ref or ref.startswith("/") or "\x00" in ref or ".." in ref.split("/"):
                continue
            if ref in seen:
                continue
            refs.append(ref)
            seen.add(ref)
    return refs


def _ide_bridge_scalar(value: Any, *, limit: int = 360) -> str | int | float | bool | None:
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float)):
        return value
    text = str(value or "").replace("\r\n", "\n").strip()
    if not text:
        return ""
    return text[:limit]


def _ide_bridge_row(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        text = _ide_bridge_scalar(value, limit=420)
        return {"text": text} if text not in {"", None} else {}
    row: dict[str, Any] = {}
    for key in (
        "id",
        "label",
        "title",
        "path",
        "file_path",
        "relpath",
        "kind",
        "status",
        "severity",
        "source",
        "view",
        "meta",
        "detail",
        "summary",
        "route",
        "href",
        "value",
        "count",
        "line",
        "column",
    ):
        if key in value:
            scalar = _ide_bridge_scalar(value.get(key), limit=520 if key in {"detail", "summary"} else 220)
            if scalar not in {"", None}:
                row[key] = scalar
    return row


def _ide_bridge_rows(value: Any, *, limit: int = 24) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    rows: list[dict[str, Any]] = []
    for item in value[:limit]:
        row = _ide_bridge_row(item)
        if row:
            rows.append(row)
    return rows


def _ide_bridge_mapping(value: Any, *, allowed_keys: tuple[str, ...]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {}
    result: dict[str, Any] = {}
    for key in allowed_keys:
        if key not in value:
            continue
        scalar = _ide_bridge_scalar(value.get(key), limit=520)
        if scalar not in {"", None}:
            result[key] = scalar
    return result


def _ide_bridge_count(snapshot: Mapping[str, Any], key: str) -> int:
    value = snapshot.get(key)
    return len(value) if isinstance(value, list) else (1 if isinstance(value, Mapping) and value else 0)


def _build_ide_context_bridge_branches(snapshot: Mapping[str, Any], artifact_ref: str) -> list[dict[str, Any]]:
    branches: list[dict[str, Any]] = []
    for branch_id, label, primary_key, secondary_key in IDE_CONTEXT_BRANCHES:
        branches.append({
            "schema_id": "ion.codex_ide_context_branch.v0_1",
            "branch_id": branch_id,
            "label": label,
            "artifact_ref": artifact_ref,
            "context_refs": [artifact_ref],
            "read_first": [artifact_ref],
            "payload_summary": {
                "primary_key": primary_key,
                "primary_count": _ide_bridge_count(snapshot, primary_key),
                "secondary_key": secondary_key,
                "secondary_count": _ide_bridge_count(snapshot, secondary_key),
            },
            "lazy_load_policy": "read_bridge_artifact_first_then_open_specific_path_refs",
            "mount_action": {
                "kind": "context_ref",
                "ref": artifact_ref,
                "branch_key": primary_key,
            },
            "authority": {
                "read_only_projection": True,
                "filesystem_mutation_authority": False,
                "accepted_state_authority": False,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            },
        })
    return branches


def _build_ide_context_snapshot(payload: Mapping[str, Any]) -> dict[str, Any]:
    selected_tab = _ide_bridge_mapping(
        payload.get("selected_tab"),
        allowed_keys=("id", "label", "path", "kind", "status", "view", "meta", "detail"),
    )
    preview_payload = payload.get("preview") if isinstance(payload.get("preview"), Mapping) else {}
    return {
        "source": _trim(payload.get("source") or "codex_ide_workbench", limit=120),
        "active_view": _trim(payload.get("active_view"), limit=80),
        "active_drawer": _trim(payload.get("active_drawer"), limit=80),
        "drawer_open": bool(payload.get("drawer_open")),
        "bottom_panel": _trim(payload.get("bottom_panel"), limit=80),
        "bottom_open": bool(payload.get("bottom_open")),
        "selected_path": _trim(payload.get("selected_path") or selected_tab.get("path"), limit=420),
        "selected_tab": selected_tab,
        "open_tabs": _ide_bridge_rows(payload.get("open_tabs"), limit=18),
        "worktree": {
            "summary": _ide_bridge_mapping(
                payload.get("worktree"),
                allowed_keys=("file_count", "insertions", "deletions", "branch", "head", "status"),
            ),
            "file_edits": _ide_bridge_rows(payload.get("file_edits"), limit=28),
        },
        "context_surfaces": _ide_bridge_rows(payload.get("context_surfaces"), limit=24),
        "context_systems": _ide_bridge_rows(payload.get("context_systems"), limit=24),
        "docs": _ide_bridge_rows(payload.get("docs"), limit=18),
        "media": _ide_bridge_rows(payload.get("media"), limit=18),
        "problems": _ide_bridge_rows(payload.get("problems"), limit=24),
        "diagnostics": _ide_bridge_rows(payload.get("diagnostics"), limit=18),
        "output": _ide_bridge_rows(payload.get("output"), limit=14),
        "terminal": _ide_bridge_rows(payload.get("terminal"), limit=14),
        "ports": _ide_bridge_rows(payload.get("ports"), limit=14),
        "timeline": _ide_bridge_rows(payload.get("timeline"), limit=24),
        "agent_mounts": _ide_bridge_rows(payload.get("agent_mounts"), limit=18),
        "preview": {
            "route": _trim(preview_payload.get("route") or payload.get("preview_route"), limit=260),
            "ready": bool(preview_payload.get("ready") or payload.get("preview_ready")),
            "label": _trim(preview_payload.get("label"), limit=120),
        },
        "tool_capabilities": [
            {"tool_id": "ide.open_ref", "label": "Open file or artifact ref", "authority": "read_only"},
            {"tool_id": "ide.inspect_diff", "label": "Inspect selected worktree diff", "authority": "read_only"},
            {"tool_id": "ide.inspect_preview", "label": "Inspect active preview route", "authority": "read_only"},
            {"tool_id": "ide.inspect_diagnostics", "label": "Inspect bottom diagnostics branches", "authority": "read_only"},
        ],
    }


def _write_ide_context_bridge(
    root: Path,
    *,
    turn_id: str,
    created_at: str,
    payload: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    if not isinstance(payload, Mapping):
        return None
    snapshot = _build_ide_context_snapshot(payload)
    file_id = re.sub(r"[^A-Za-z0-9_.-]+", "_", turn_id).strip("_")[:180] or f"turn_{_safe_slug(created_at)}"
    bridge_path = root / IDE_CONTEXT_BRIDGES_DIR / f"{file_id}.json"
    artifact_ref = _relpath(bridge_path, root)
    branches = _build_ide_context_bridge_branches(snapshot, artifact_ref)
    summary = {
        "schema_id": IDE_CONTEXT_BRIDGE_SCHEMA_ID,
        "bridge_id": f"idebridge.{_sha256_text(json.dumps(snapshot, sort_keys=True))[:12]}",
        "created_at": created_at,
        "source_turn_id": turn_id,
        "artifact_ref": artifact_ref,
        "source": snapshot.get("source"),
        "active_view": snapshot.get("active_view"),
        "active_drawer": snapshot.get("active_drawer"),
        "bottom_panel": snapshot.get("bottom_panel"),
        "selected_path": snapshot.get("selected_path"),
        "selected_tab": snapshot.get("selected_tab"),
        "open_tab_count": _ide_bridge_count(snapshot, "open_tabs"),
        "problem_count": _ide_bridge_count(snapshot, "problems"),
        "branch_ids": [branch["branch_id"] for branch in branches],
        "branch_count": len(branches),
        "context_refs": [artifact_ref],
        "lazy_load_policy": "read_bridge_artifact_first_then_open_specific_path_refs",
        "authority": {
            "read_only_projection": True,
            "filesystem_mutation_authority": False,
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    }
    artifact = {
        **summary,
        "snapshot": snapshot,
        "lazy_context_branches": branches,
        "instructions": [
            "This bridge is a read-only IDE context projection for the originating chat turn.",
            "Use branch summaries to decide which workspace files or artifacts to read next.",
            "Do not treat this artifact as filesystem mutation, production, live execution, accepted-state, or secrets authority.",
        ],
    }
    _write_json(bridge_path, artifact)
    return summary


def _build_ide_context_bridge_surface(state: Mapping[str, Any]) -> dict[str, Any]:
    bridges = state.get("ide_context_bridges") if isinstance(state.get("ide_context_bridges"), list) else []
    ordered = [dict(item) for item in bridges if isinstance(item, Mapping)][-30:]
    latest = ordered[-1] if ordered else None
    return {
        "schema_id": "ion.codex_ide_context_bridge_surface.v0_1",
        "status": "ready" if latest else "empty",
        "latest_bridge": latest,
        "bridges": list(reversed(ordered)),
        "bridge_count": len(bridges),
        "branch_ids": latest.get("branch_ids") if isinstance(latest, Mapping) else [],
        "context_policy": {
            "ide_bridge_is_read_only_projection": True,
            "lazy_branches_require_artifact_read_first": True,
            "chat_turn_must_mount_bridge_explicitly": True,
        },
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def _raw_codex_cli_prompt_with_ide_context(operator_message: str, ide_context_bridge: Mapping[str, Any] | None) -> str:
    if not isinstance(ide_context_bridge, Mapping) or not ide_context_bridge.get("artifact_ref"):
        return operator_message
    branch_ids = [str(item) for item in ide_context_bridge.get("branch_ids", []) if str(item).strip()]
    branch_text = "\n".join(f"- {branch_id}" for branch_id in branch_ids[:18]) or "- No lazy branches supplied."
    return "\n".join([
        "ION Codex IDE chat turn.",
        "",
        "OPERATOR MESSAGE:",
        operator_message,
        "",
        "MOUNTED READ-ONLY IDE CONTEXT BRIDGE:",
        f"- artifact_ref: {ide_context_bridge.get('artifact_ref')}",
        f"- selected_path: {ide_context_bridge.get('selected_path') or 'none'}",
        f"- active_view: {ide_context_bridge.get('active_view') or 'unknown'}",
        f"- active_drawer: {ide_context_bridge.get('active_drawer') or 'unknown'}",
        f"- bottom_panel: {ide_context_bridge.get('bottom_panel') or 'unknown'}",
        "",
        "LAZY IDE CONTEXT BRANCHES:",
        branch_text,
        "",
        "IDE CONTEXT POLICY:",
        "- The IDE bridge is read-only context, not authority to mutate files.",
        "- Read the bridge artifact first when IDE state matters, then open specific file refs as needed.",
        "- No production, live execution, accepted-state, filesystem mutation, or secrets authority is granted by this bridge.",
        "",
        "Answer the operator message using the mounted IDE context when relevant.",
    ])


def _context_slug(value: Any, *, fallback: str = "context", limit: int = 48) -> str:
    slug = re.sub(r"[^a-z0-9_.-]+", "_", str(value or "").strip().lower()).strip("._-")
    return (slug or fallback)[:limit]


def _active_archive_attachment_refs(state: Mapping[str, Any], *, limit: int = 8) -> list[dict[str, Any]]:
    memory = state.get("memory") if isinstance(state.get("memory"), Mapping) else {}
    attachments = memory.get("archive_attachments") if isinstance(memory.get("archive_attachments"), list) else []
    refs: list[dict[str, Any]] = []
    for attachment in attachments[-limit:]:
        if not isinstance(attachment, Mapping) or attachment.get("status") != "active":
            continue
        session_id = _trim(attachment.get("session_id"), limit=180)
        if not session_id:
            continue
        refs.append({
            "session_id": session_id,
            "thread_name": _trim(attachment.get("thread_name"), limit=220),
            "packet_path": _trim(attachment.get("packet_path"), limit=360),
            "context_role": "historical_witness",
            "authority": "not_accepted_state",
        })
    return refs


def _chat_engine_primary_domain(chat_engine: Mapping[str, Any]) -> str:
    route = chat_engine.get("assistant_work_route") if isinstance(chat_engine.get("assistant_work_route"), Mapping) else {}
    domains = route.get("candidate_domains") if isinstance(route.get("candidate_domains"), list) else []
    for domain in domains:
        value = _trim(domain, limit=160)
        if value:
            return value
    selected_skill = chat_engine.get("selected_skill") if isinstance(chat_engine.get("selected_skill"), Mapping) else {}
    skill_id = _trim(selected_skill.get("skill_id"), limit=120)
    if skill_id:
        return f"domain.{_context_slug(skill_id)}"
    return "domain.codex_general"


def _chat_engine_primary_role(chat_engine: Mapping[str, Any]) -> str:
    route = chat_engine.get("assistant_work_route") if isinstance(chat_engine.get("assistant_work_route"), Mapping) else {}
    agents = route.get("candidate_agents") if isinstance(route.get("candidate_agents"), list) else []
    for agent in agents:
        value = _trim(agent, limit=160)
        if value:
            return value
    lenses = chat_engine.get("native_lenses") if isinstance(chat_engine.get("native_lenses"), list) else []
    for lens in lenses:
        if isinstance(lens, Mapping):
            role = _trim(lens.get("role_id"), limit=160)
            if role:
                return role
    selected_skill = chat_engine.get("selected_skill") if isinstance(chat_engine.get("selected_skill"), Mapping) else {}
    skill_id = _trim(selected_skill.get("skill_id"), limit=120)
    if skill_id:
        return f"role.{_context_slug(skill_id)}"
    return "role.codex_general"


def _chat_context_system_refs(chat_engine: Mapping[str, Any], skill_activation: Mapping[str, Any] | None) -> list[str]:
    refs: list[str] = []
    lenses = chat_engine.get("native_lenses") if isinstance(chat_engine.get("native_lenses"), list) else []
    for lens in lenses:
        if not isinstance(lens, Mapping):
            continue
        refs.extend(str(ref) for ref in lens.get("template_refs", []) if ref)
    if isinstance(skill_activation, Mapping):
        refs.extend(str(ref) for ref in skill_activation.get("activates_templates", []) if ref)
    refs.extend([
        "ION/03_registry/agent_context_system_registry.yaml",
        "ION/03_registry/ion_native_lens_registry.yaml",
        CONTEXT_PACKAGES_PATH.as_posix(),
    ])
    return _merge_context_refs(refs)


def _build_chat_context_binding(
    *,
    state: Mapping[str, Any],
    lane_id: str,
    source_turn_id: str,
    created_at: str,
    chat_engine: Mapping[str, Any],
    skill_activation: Mapping[str, Any] | None,
    mounted_context_refs: list[str],
    selected_context_refs: list[str],
    ide_context_bridge: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    domain_id = _chat_engine_primary_domain(chat_engine)
    role_id = _chat_engine_primary_role(chat_engine)
    attachments = _active_archive_attachment_refs(state)
    attachment_ids = [str(item.get("session_id")) for item in attachments if item.get("session_id")]
    branch_seed = json.dumps({
        "lane_id": lane_id,
        "domain_id": domain_id,
        "role_id": role_id,
        "source_turn_id": source_turn_id,
        "selected_context_refs": selected_context_refs,
        "attached_archive_session_ids": attachment_ids,
    }, sort_keys=True)
    branch_hash = _sha256_text(branch_seed)[:12]
    branch_id = f"branch.{_context_slug(domain_id)}.{branch_hash}"
    branch_title = f"{domain_id} / {role_id} / {branch_hash}"
    binding_id = f"chatctx.{_context_slug(lane_id)}.{_context_slug(domain_id)}.{branch_hash}"
    agent_instance_id = f"agent.{_context_slug(role_id)}.{branch_hash}"
    agent_true_name = f"{role_id}::{branch_hash}"
    existing = state.get("chat_context_bindings") if isinstance(state.get("chat_context_bindings"), Mapping) else {}
    same_domain_siblings = [
        str(binding.get("binding_id"))
        for binding in existing.values()
        if isinstance(binding, Mapping)
        and binding.get("binding_id") != binding_id
        and binding.get("domain_id") == domain_id
    ][-12:]
    context_floor_refs = [
        CAPSULE_PATH.as_posix(),
        HOT_CONTEXT_PATH.as_posix(),
        MINI_PATH.as_posix(),
        LONG_HORIZON_PATH.as_posix(),
        CONTEXT_PACKAGES_PATH.as_posix(),
        ROUTE_PATH.as_posix(),
    ]
    minimum_context = {
        "required": True,
        "floor": "codex_solo_capsule",
        "capsule_ref": CAPSULE_PATH.as_posix(),
        "hot_context_ref": HOT_CONTEXT_PATH.as_posix(),
        "mini_ref": MINI_PATH.as_posix(),
        "route_ref": ROUTE_PATH.as_posix(),
        "context_package_ref": CONTEXT_PACKAGES_PATH.as_posix(),
        "missing_required_refs": [],
    }
    context_version = _sha256_text(json.dumps({
        "binding_id": binding_id,
        "agent_instance_id": agent_instance_id,
        "source_turn_id": source_turn_id,
        "mounted_context_refs": mounted_context_refs,
        "selected_context_refs": selected_context_refs,
        "attached_archive_session_ids": attachment_ids,
        "ide_context_bridge_ref": ide_context_bridge.get("artifact_ref") if isinstance(ide_context_bridge, Mapping) else None,
    }, sort_keys=True))[:16]
    ide_bridge_summary = dict(ide_context_bridge) if isinstance(ide_context_bridge, Mapping) else None
    return {
        "schema_id": CHAT_CONTEXT_BINDING_SCHEMA_ID,
        "binding_id": binding_id,
        "context_version": context_version,
        "created_at": created_at,
        "updated_at": created_at,
        "lane_id": lane_id,
        "source_turn_id": source_turn_id,
        "domain_id": domain_id,
        "role_id": role_id,
        "branch_id": branch_id,
        "branch_title": branch_title,
        "agent_identity": {
            "agent_instance_id": agent_instance_id,
            "agent_true_name": agent_true_name,
            "role_id": role_id,
            "clone_of_role_id": role_id,
            "domain_id": domain_id,
            "branch_id": branch_id,
            "branch_title": branch_title,
            "identity_scope": "chat_context_branch",
            "parallel_clone_safe": True,
        },
        "minimum_context": minimum_context,
        "context_package_ref": CONTEXT_PACKAGES_PATH.as_posix(),
        "context_system_refs": _chat_context_system_refs(chat_engine, skill_activation),
        "context_floor_refs": context_floor_refs,
        "branch_context_refs": selected_context_refs,
        "mounted_context_refs": mounted_context_refs,
        "ide_context_bridge": ide_bridge_summary,
        "ide_context_branch_ids": ide_bridge_summary.get("branch_ids") if isinstance(ide_bridge_summary, Mapping) else [],
        "attached_archive_refs": attachments,
        "same_domain_sibling_binding_ids": same_domain_siblings,
        "context_policy": {
            "agent_must_have_capsule_floor": True,
            "agent_identity_is_instance_not_role_alias": True,
            "parallel_clones_must_use_unique_instance_id": True,
            "capsule_is_minimum_floor": True,
            "mini_is_lookup_index": True,
            "hot_context_is_boot_window": True,
            "branch_context_is_chat_identity": True,
            "archive_attachments_are_historical_witnesses": True,
            "same_domain_siblings_are_awareness_only": True,
            "ide_context_bridge_is_read_only_projection": bool(ide_bridge_summary),
            "ide_context_lazy_branches_require_artifact_read_first": bool(ide_bridge_summary),
            "shared_raw_context_between_chats": False,
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    }


def _record_chat_context_binding(state: MutableMapping[str, Any], binding: Mapping[str, Any]) -> None:
    binding_id = _trim(binding.get("binding_id"), limit=220)
    if not binding_id:
        return
    bindings = state.setdefault("chat_context_bindings", {})
    if not isinstance(bindings, dict):
        bindings = {}
        state["chat_context_bindings"] = bindings
    bindings[binding_id] = dict(binding)
    state["active_chat_context_id"] = binding_id


def _build_chat_context_surface(state: Mapping[str, Any]) -> dict[str, Any]:
    bindings = state.get("chat_context_bindings") if isinstance(state.get("chat_context_bindings"), Mapping) else {}
    ordered = sorted(
        [dict(binding) for binding in bindings.values() if isinstance(binding, Mapping)],
        key=lambda binding: str(binding.get("updated_at") or binding.get("created_at") or ""),
        reverse=True,
    )
    active_id = _trim(state.get("active_chat_context_id"), limit=220)
    active = next((binding for binding in ordered if binding.get("binding_id") == active_id), ordered[0] if ordered else None)
    domain_counts: dict[str, int] = {}
    for binding in ordered:
        domain_id = _trim(binding.get("domain_id"), limit=180) or "domain.unknown"
        domain_counts[domain_id] = domain_counts.get(domain_id, 0) + 1
    return {
        "schema_id": "ion.codex_chat_context_surface.v1",
        "status": "ready" if ordered else "empty",
        "active_binding_id": active_id,
        "active_binding": active,
        "bindings": ordered[:80],
        "binding_count": len(ordered),
        "domain_counts": domain_counts,
        "context_policy": {
            "capsule_mini_are_floor_not_chat_identity": True,
            "chat_context_binding_required_for_new_work": True,
            "same_domain_branch_awareness_only": True,
            "archive_attach_required_for_past_chat_context": True,
        },
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def _codex_general_queued_objective(
    objective: str,
    solo_context: Mapping[str, Any],
    model_move: Mapping[str, Any],
    skill_activation: Mapping[str, Any],
    chat_engine: Mapping[str, Any],
    context_refs: list[str] | None = None,
) -> str:
    refs = _merge_context_refs(context_refs or [], _codex_solo_context_refs(solo_context))
    ref_lines = "\n".join(f"- {ref}" for ref in refs[:32])
    template_lines = "\n".join(f"- {ref}" for ref in skill_activation.get("activates_templates", [])[:8]) if isinstance(skill_activation.get("activates_templates"), list) else "- none"
    native_lenses = chat_engine.get("native_lenses") if isinstance(chat_engine.get("native_lenses"), list) else []
    assistant_work_route = chat_engine.get("assistant_work_route") if isinstance(chat_engine.get("assistant_work_route"), Mapping) else {}
    output_contract = assistant_work_route.get("output_contract") if isinstance(assistant_work_route.get("output_contract"), Mapping) else {}
    lens_lines = "\n".join(
        f"- {lens.get('display_name')} ({lens.get('role_id')}): {lens.get('purpose')}"
        for lens in native_lenses[:8]
        if isinstance(lens, Mapping)
    ) or "- none"
    include_lines = ", ".join(str(item) for item in (output_contract.get("include") or [])[:6]) if isinstance(output_contract.get("include"), list) else ""
    forbid_lines = ", ".join(str(item) for item in (output_contract.get("forbid") or [])[:6]) if isinstance(output_contract.get("forbid"), list) else ""
    return "\n".join([
        "Codex solo chat work packet.",
        "",
        "Chat engine route:",
        f"- Response mode: {chat_engine.get('response_mode')}",
        f"- Carrier strategy: {(chat_engine.get('carrier_strategy') or {}).get('mode') if isinstance(chat_engine.get('carrier_strategy'), Mapping) else 'unknown'}",
        "- Native lenses:",
        lens_lines,
        "",
        "Candidate Assistant Work route:",
        f"- Route: {assistant_work_route.get('route_id') or 'unavailable'}",
        f"- Selection basis: {assistant_work_route.get('selection_basis') or assistant_work_route.get('finding') or 'candidate'}",
        f"- Candidate domains: {', '.join(str(item) for item in (assistant_work_route.get('candidate_domains') or [])[:8])}",
        f"- Candidate agents: {', '.join(str(item) for item in (assistant_work_route.get('candidate_agents') or [])[:8])}",
        f"- Include: {include_lines or 'none'}",
        f"- Forbid: {forbid_lines or 'none'}",
        "- Candidate route metadata does not promote assistant-work registries to ION law.",
        "",
        "Skill activation:",
        f"- Skill: {skill_activation.get('display_name')} ({skill_activation.get('skill_id')})",
        f"- Selection reason: {skill_activation.get('selection_reason')}",
        "- Skill activates workflow only; templates remain proof gates.",
        "Activated template refs:",
        template_lines,
        "",
        "Context policy:",
        f"- {WITNESS_POLICY}",
        f"- Minimum working context: load {CAPSULE_PATH.as_posix()} before doing the work.",
        f"- Mini role: {MINI_PATH.as_posix()} is lookup/receipt index only, not the main prompt surface.",
        f"- Long horizon: use {LONG_HORIZON_PATH.as_posix()} for older capsule epochs instead of stuffing all history into the prompt.",
        f"- Context package selector: use {CONTEXT_PACKAGES_PATH.as_posix()} to choose authority, mission, evidence, recovery, and route-depth packages.",
        "- Use the active ION_Developement root only.",
        "- Treat historical roots only as explicitly named witness material.",
        "- Do not claim production or live execution authority.",
        "",
        *_model_move_context_lines(model_move),
        "Required context refs:",
        ref_lines,
        "",
        "Operator objective:",
        objective,
    ])


def _active_archive_attachment_context(root: Path, state: Mapping[str, Any], *, limit: int = 3) -> str:
    memory = state.get("memory") if isinstance(state.get("memory"), Mapping) else {}
    attachments = memory.get("archive_attachments") if isinstance(memory.get("archive_attachments"), list) else []
    lines: list[str] = []
    for attachment in attachments[-limit:]:
        if not isinstance(attachment, Mapping) or attachment.get("status") != "active":
            continue
        packet_path = str(attachment.get("packet_path") or "")
        if not packet_path:
            continue
        try:
            payload = _read_json(root / packet_path) or {}
        except Exception:
            payload = {}
        text = _trim(payload.get("attachment_text") or "", limit=9000)
        if not text:
            continue
        lines.extend([
            f"## Attached past chat: {attachment.get('thread_name') or attachment.get('session_id')}",
            text,
            "",
        ])
    return "\n".join(lines).strip()


def _model_move_context_lines(model_move: Mapping[str, Any]) -> list[str]:
    return [
        "Codex requested dispatch profile:",
        f"- Requested model profile: {model_move.get('selected_model')}",
        f"- Reasoning effort: {model_move.get('selected_reasoning_effort')}",
        f"- Work class: {model_move.get('work_class')}",
        f"- ION stage: {model_move.get('ion_stage_id') or 'codex_general_work'}",
        f"- Usage pool label: {model_move.get('usage_pool_id')} ({model_move.get('usage_pool_authority')})",
        "- Model profile is dispatch metadata, not assistant self-identity.",
        "- Usage pool labels are operator-observed hints, not authoritative provider limits.",
        "",
    ]


def _codex_capsule_assistant_message(
    *,
    operator_text: str,
    execution_mode: str,
    codex_solo_context: Mapping[str, Any],
    codex_status: Mapping[str, Any],
    model_move: Mapping[str, Any],
    skill_activation: Mapping[str, Any],
) -> str:
    capsule = codex_solo_context.get("capsule") if isinstance(codex_solo_context.get("capsule"), Mapping) else {}
    recent_rows = capsule.get("recent_rows") if isinstance(capsule.get("recent_rows"), list) else []
    latest_row = recent_rows[-1] if recent_rows and isinstance(recent_rows[-1], Mapping) else {}
    latest_summary = latest_row.get("summary") or "No capsule receipt rows yet."
    queue_count = codex_status.get("queued_request_count", 0)
    active = codex_status.get("active_process_running", False)
    selected_model = model_move.get("selected_model") or "codex dispatch profile unavailable"
    effort = model_move.get("selected_reasoning_effort") or "unknown"
    skill_label = skill_activation.get("display_name") or "Skill unavailable"
    skill_id = skill_activation.get("skill_id") or "unknown"
    trimmed = _trim(operator_text, limit=360)
    return "\n".join([
        "Capsule context is mounted.",
        "",
        f"I received: {trimmed}",
        "",
        "Current working basis:",
        f"- minimum context: {CAPSULE_PATH.as_posix()}",
        f"- hot context: {HOT_CONTEXT_PATH.as_posix()}",
        f"- latest capsule receipt: {latest_summary}",
        f"- active skill: {skill_label} ({skill_id})",
        "- skill role: activates workflow; templates still gate proof and receipts",
        f"- Codex queue: {queue_count} queued, active={active}",
        f"- requested Codex dispatch profile for work from this chat: {selected_model} / {effort}",
        "- dispatch profile is not the assistant's self-identity",
        f"- execution mode: {execution_mode}",
        "",
        "This chat is isolated to the Capsule Codex profile. It does not make every Codex CLI instance inherit Capsule context, and ION workflow communication stays behind the existing ION queue/receipt owners.",
    ])


def _create_codex_capsule_assistant_turn(
    root: str | Path | None,
    *,
    operator_text: str,
    created_at: str,
    execution_mode: str,
    chat_engine: Mapping[str, Any] | None = None,
    codex_solo_context: Mapping[str, Any] | None = None,
    prior_turns: list[Mapping[str, Any]] | None = None,
    response_carrier_enabled: bool | None = None,
) -> dict[str, Any]:
    engine_turn = dict(chat_engine) if isinstance(chat_engine, Mapping) else build_codex_chat_engine_turn(
        root,
        lane_id="codex_general",
        message=operator_text,
        execution_mode=execution_mode,
        codex_solo_context=codex_solo_context,
    )
    message = str(engine_turn.get("assistant_response") or "").strip() or "I’m mounted on the Codex Chat Engine, but this turn did not produce a response contract."
    response_carrier = None
    assistant_author = "codex_chat_engine"
    response_mode = str(engine_turn.get("response_mode") or "").strip()
    carrier_eligible = execution_mode == "respond_only" or (execution_mode == "auto" and response_mode != "queue_work")
    if carrier_eligible:
        try:
            response_carrier = run_codex_chat_response_carrier(
                root,
                operator_message=operator_text,
                chat_engine_turn=engine_turn,
                codex_solo_context=codex_solo_context,
                prior_turns=prior_turns,
                enabled=response_carrier_enabled,
            )
        except Exception as exc:  # keep chat usable if the carrier fails before returning a packet
            response_carrier = {
                "schema_id": "ion.codex_chat_response_carrier_run.v1",
                "ok": False,
                "status": "CARRIER_EXCEPTION",
                "finding": exc.__class__.__name__,
                "response_text": "",
                "production_authority": False,
                "live_execution_authority": False,
                "provider_api_dispatch_authorized": False,
                "state_acceptance_granted": False,
            }
        carrier_text = str(response_carrier.get("response_text") or "").strip() if isinstance(response_carrier, Mapping) else ""
        if response_carrier.get("ok") and carrier_text:
            message = carrier_text
            assistant_author = "codex_cli"
    context_mount = engine_turn.get("context_mount") if isinstance(engine_turn.get("context_mount"), Mapping) else {}
    context_refs = context_mount.get("context_refs") if isinstance(context_mount.get("context_refs"), list) else [
        CAPSULE_PATH.as_posix(),
        HOT_CONTEXT_PATH.as_posix(),
        MINI_PATH.as_posix(),
        LONG_HORIZON_PATH.as_posix(),
        CONTEXT_PACKAGES_PATH.as_posix(),
        ROUTE_PATH.as_posix(),
    ]
    return {
        "turn_id": f"assistant_{created_at.replace(':', '').replace('+', 'Z')}_{_safe_slug(operator_text)}",
        "lane_id": "codex_general",
        "author": assistant_author,
        "kind": "assistant_response",
        "message": message,
        "message_sha256": _sha256_text(message),
        "created_at": _now(),
        "context_refs": [str(ref) for ref in context_refs],
        "execution_mode": execution_mode,
        "response_mode": engine_turn.get("response_mode"),
        "codex_model_move": engine_turn.get("model_move"),
        "skill_activation": engine_turn.get("skill_activation"),
        "native_lenses": engine_turn.get("native_lenses"),
        "response_contract": engine_turn.get("response_contract"),
        "chat_engine": engine_turn,
        "response_carrier": response_carrier,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _mark_pipeline_prompt_projection(pipeline_run: MutableMapping[str, Any]) -> None:
    now = _now()
    status_by_stage = {
        "relay_ingress": "complete",
        "steward_route": "complete",
        "vizier_plan": "complete",
        "mason_codex_work": "not_requested",
        "vice_risk": "waiting_for_work",
        "nemesis_verify": "waiting_for_work",
        "relay_return": "complete",
        "persona_response": "complete",
    }
    for raw_stage in pipeline_run.get("stages", []):
        if not isinstance(raw_stage, MutableMapping):
            continue
        stage_id = str(raw_stage.get("stage_id") or "")
        raw_stage["status"] = status_by_stage.get(stage_id, raw_stage.get("status") or "pending")
        raw_stage["updated_at"] = now
    pipeline_run["status"] = "PERSONA_RESPONSE_RECORDED_NO_CODEX_WORK_REQUESTED"
    pipeline_run["updated_at"] = now


def _create_ion_persona_assistant_turn(
    *,
    operator_text: str,
    created_at: str,
    execution_mode: str,
    chat_engine: Mapping[str, Any] | None = None,
    pipeline_run: Mapping[str, Any] | None = None,
    context_refs: list[str] | None = None,
    source_turn_id: str | None = None,
) -> dict[str, Any]:
    engine_turn = dict(chat_engine) if isinstance(chat_engine, Mapping) else {}
    run_id = str((pipeline_run or {}).get("run_id") or "").strip()
    stage_labels = [
        str(stage.get("label") or stage.get("stage_id") or "").strip()
        for stage in ((pipeline_run or {}).get("stages") or [])
        if isinstance(stage, Mapping)
    ]
    stage_summary = " -> ".join(label for label in stage_labels if label) or "Relay -> Steward -> Vizier -> Mason/Codex -> Vice -> Nemesis -> Relay return -> Persona"
    mode_label = "Prompt/Auto" if execution_mode == "auto" else "Respond only"
    message = "\n".join([
        "ION received this through the Persona interface.",
        "",
        "Current state:",
        "- Conversation turn recorded in the ION lane.",
        f"- Pipeline visible: {stage_summary}.",
        f"- {mode_label} recorded a Persona response without starting a Codex worker.",
        "",
        "Use Queue or Run when this should become bounded Codex work. This chat can still answer while the worker lane stays separate.",
    ])
    return {
        "turn_id": f"assistant_{created_at.replace(':', '').replace('+', 'Z')}_ion_persona_{_safe_slug(operator_text)}",
        "lane_id": "ion_system",
        "author": "ion_persona",
        "kind": "assistant_response",
        "message": message,
        "message_sha256": _sha256_text(message),
        "created_at": _now(),
        "context_refs": [str(ref) for ref in (context_refs or [])],
        "execution_mode": "ion_comms_projection",
        "requested_execution_mode": execution_mode,
        "response_mode": engine_turn.get("response_mode"),
        "source_turn_id": source_turn_id,
        "pipeline_run_id": run_id or None,
        "codex_model_move": engine_turn.get("model_move"),
        "skill_activation": engine_turn.get("skill_activation"),
        "native_lenses": engine_turn.get("native_lenses"),
        "response_contract": engine_turn.get("response_contract"),
        "chat_engine": engine_turn,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _raw_codex_cli_model_args(codex_model_override: Mapping[str, Any] | None) -> list[str]:
    if not isinstance(codex_model_override, Mapping):
        return []
    model = str(codex_model_override.get("selected_model") or "").strip()
    effort = str(codex_model_override.get("selected_reasoning_effort") or "").strip()
    service_tier = _raw_codex_cli_service_tier()
    args: list[str] = []
    if model and model != "auto":
        args.extend(["-m", model])
    if effort and effort != "auto":
        args.extend(["-c", f"model_reasoning_effort={effort}"])
    if service_tier and service_tier != "auto":
        args.extend(["-c", f"service_tier={service_tier}"])
    return args


def _extract_codex_thread_id(events_text: str) -> str:
    for line in events_text.splitlines():
        raw = line.strip()
        if raw.startswith("b'") and raw.endswith("'"):
            raw = raw[2:-1]
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, Mapping) and payload.get("type") == "thread.started":
            return str(payload.get("thread_id") or "").strip()
    return ""


def run_raw_codex_cli_chat_turn(
    root: str | Path | None,
    *,
    operator_message: str,
    created_at: str,
    codex_model_override: Mapping[str, Any] | None = None,
    active_thread_id: str = "",
    ide_context_bridge: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    run_id = f"raw_codex_cli_{created_at.replace(':', '').replace('+', 'Z')}_{_safe_slug(operator_message)}"
    run_dir = shell_root / RAW_CODEX_CLI_RUNS_DIR / run_id
    counter = 1
    while run_dir.exists():
        run_id = f"raw_codex_cli_{created_at.replace(':', '').replace('+', 'Z')}_{_safe_slug(operator_message)}_{counter}"
        run_dir = shell_root / RAW_CODEX_CLI_RUNS_DIR / run_id
        counter += 1
    run_dir.mkdir(parents=True, exist_ok=False)
    prompt_path = run_dir / "prompt.txt"
    latest_return_path = run_dir / "latest_return.md"
    stdout_path = run_dir / "stdout.jsonl"
    stderr_path = run_dir / "stderr.log"
    run_path = run_dir / "run.json"
    stdin_prompt = _raw_codex_cli_prompt_with_ide_context(operator_message, ide_context_bridge)
    prompt_path.write_text(stdin_prompt, encoding="utf-8")
    binary = str(os.environ.get(CHAT_CODEX_BINARY_ENV) or "codex")
    if active_thread_id:
        command = [
            binary,
            "exec",
            "resume",
            * _raw_codex_cli_model_args(codex_model_override),
            "--output-last-message",
            latest_return_path.as_posix(),
            "--json",
            active_thread_id,
            "-",
        ]
    else:
        command = [
            binary,
            "exec",
            * _raw_codex_cli_model_args(codex_model_override),
            "--cd",
            shell_root.as_posix(),
            "--output-last-message",
            latest_return_path.as_posix(),
            "--json",
            "-",
        ]
    started_at = _now()
    run = {
        "schema_id": "ion.codex_cockpit_raw_cli_run.v1",
        "run_id": run_id,
        "status": "CODEX_CLI_RUNNING",
        "created_at": created_at,
        "started_at": started_at,
        "operator_message_sha256": _sha256_text(operator_message),
        "stdin_prompt_sha256": _sha256_text(stdin_prompt),
        "active_thread_id_before": active_thread_id or None,
        "run_dir": _relpath(run_dir, shell_root),
        "run_packet_path": _relpath(run_path, shell_root),
        "prompt_path": _relpath(prompt_path, shell_root),
        "latest_return_path": _relpath(latest_return_path, shell_root),
        "stdout_path": _relpath(stdout_path, shell_root),
        "stderr_path": _relpath(stderr_path, shell_root),
        "codex_command": command,
        "wrapper_prompt_used": False,
        "operator_message_passed_as_stdin": True,
        "ide_context_bridge_prompt_injected": stdin_prompt != operator_message,
        "ide_context_bridge_ref": ide_context_bridge.get("artifact_ref") if isinstance(ide_context_bridge, Mapping) else None,
        "codex_cli_surface": "codex_exec" if not active_thread_id else "codex_exec_resume",
        "codex_model_override": dict(codex_model_override) if isinstance(codex_model_override, Mapping) else None,
        "production_authority": False,
        "live_execution_authority": False,
    }
    _write_json(run_path, run)
    try:
        completed = subprocess.run(
            command,
            cwd=shell_root,
            input=stdin_prompt,
            text=True,
            capture_output=True,
            timeout=_raw_cli_timeout_seconds(),
            check=False,
        )
        stdout_text = completed.stdout or ""
        stderr_text = completed.stderr or ""
        stdout_path.write_text(stdout_text, encoding="utf-8", errors="replace")
        stderr_path.write_text(stderr_text, encoding="utf-8", errors="replace")
        response_text = _trim(latest_return_path.read_text(encoding="utf-8", errors="replace") if latest_return_path.exists() else "", limit=60000)
        thread_id = _extract_codex_thread_id(stdout_text) or active_thread_id
        ok = completed.returncode == 0 and bool(response_text)
        status = "RETURN_CAPTURED" if ok else "CODEX_CLI_FAILED"
        finding = "" if ok else ("latest_return_missing_or_empty" if completed.returncode == 0 else "codex_cli_exit_nonzero")
        run.update({
            "status": status,
            "ok": ok,
            "finding": finding or None,
            "returncode": completed.returncode,
            "completed_at": _now(),
            "active_thread_id_after": thread_id or None,
            "response_sha256": _sha256_text(response_text) if response_text else None,
        })
        _write_json(run_path, run)
        return {
            "schema_id": "ion.codex_cockpit_raw_cli_result.v1",
            "ok": ok,
            "status": status,
            "finding": finding or None,
            "response_text": response_text or _trim(stderr_text or stdout_text, limit=12000),
            "active_thread_id": thread_id,
            "run": run,
            "production_authority": False,
            "live_execution_authority": False,
        }
    except subprocess.TimeoutExpired as exc:
        stdout_text = exc.stdout if isinstance(exc.stdout, str) else str(exc.stdout or "")
        stderr_text = exc.stderr if isinstance(exc.stderr, str) else str(exc.stderr or "codex cli timed out")
        stdout_path.write_text(stdout_text, encoding="utf-8", errors="replace")
        stderr_path.write_text(stderr_text, encoding="utf-8", errors="replace")
        run.update({
            "status": "CODEX_CLI_TIMEOUT",
            "ok": False,
            "finding": "codex_cli_timeout",
            "completed_at": _now(),
            "active_thread_id_after": _extract_codex_thread_id(stdout_text) or active_thread_id or None,
        })
        _write_json(run_path, run)
        return {
            "schema_id": "ion.codex_cockpit_raw_cli_result.v1",
            "ok": False,
            "status": "CODEX_CLI_TIMEOUT",
            "finding": "codex_cli_timeout",
            "response_text": _trim(stderr_text or stdout_text, limit=12000),
            "active_thread_id": str(run.get("active_thread_id_after") or ""),
            "run": run,
            "production_authority": False,
            "live_execution_authority": False,
        }


def _create_raw_codex_cli_assistant_turn(
    *,
    created_at: str,
    operator_text: str,
    execution_mode: str,
    raw_result: Mapping[str, Any],
    context_refs: list[str],
) -> dict[str, Any]:
    response_text = _trim(raw_result.get("response_text") or "", limit=60000)
    if not response_text:
        response_text = f"Codex CLI returned no visible response. Status: {raw_result.get('status') or 'unknown'}."
    return {
        "turn_id": f"assistant_{created_at.replace(':', '').replace('+', 'Z')}_{_safe_slug(operator_text)}",
        "lane_id": "codex_general",
        "author": "codex_cli",
        "kind": "assistant_response",
        "message": response_text,
        "message_sha256": _sha256_text(response_text),
        "created_at": _now(),
        "context_refs": context_refs,
        "execution_mode": execution_mode,
        "response_mode": "raw_codex_cli",
        "raw_codex_cli": dict(raw_result),
        "response_carrier": None,
        "wrapper_prompt_used": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _app_server_response_candidates(value: Any, *, operator_message: str, depth: int = 0) -> list[str]:
    if depth > 5:
        return []
    candidates: list[str] = []
    if isinstance(value, Mapping):
        priority_keys = (
            "response_text",
            "assistant_response",
            "output_text",
            "final_message",
            "message",
            "text",
            "summary",
            "content",
        )
        for key in priority_keys:
            item = value.get(key)
            if isinstance(item, str):
                text_value = _trim(item, limit=12000)
                if text_value and text_value != operator_message and len(text_value) > 8:
                    candidates.append(text_value)
        for item in value.values():
            candidates.extend(_app_server_response_candidates(item, operator_message=operator_message, depth=depth + 1))
    elif isinstance(value, list):
        for item in value:
            candidates.extend(_app_server_response_candidates(item, operator_message=operator_message, depth=depth + 1))
    return candidates


def _app_server_response_text(*, operator_message: str, start_result: Mapping[str, Any], turns_result: Mapping[str, Any] | None) -> str:
    candidates = _app_server_response_candidates(turns_result or {}, operator_message=operator_message)
    candidates.extend(_app_server_response_candidates(start_result, operator_message=operator_message))
    for candidate in reversed(candidates):
        normalized = candidate.strip()
        if normalized and normalized != operator_message:
            return _trim(normalized, limit=60000)
    return ""


def run_codex_app_server_chat_turn(
    root: str | Path | None,
    *,
    operator_message: str,
    created_at: str,
    target_session_id: str,
    client_id: str = "",
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    try:
        from .ion_codex_app_server_bridge import CONFIRMATION_TOKEN as APP_SERVER_CONFIRMATION_TOKEN
        from .ion_codex_app_server_bridge import invoke_codex_app_server_route
    except Exception as exc:
        return {
            "schema_id": "ion.codex_cockpit_app_server_result.v1",
            "ok": False,
            "status": "CODEX_APP_SERVER_BRIDGE_UNAVAILABLE",
            "finding": "codex_app_server_bridge_unavailable",
            "error": str(exc),
            "response_text": "",
            "active_thread_id": target_session_id,
            "production_authority": False,
            "live_execution_authority": False,
        }
    idempotency_source = client_id or f"{created_at}:{target_session_id}:{_sha256_text(operator_message)[:16]}"
    start_result = invoke_codex_app_server_route(
        shell_root,
        route_id="turn_start",
        args={
            "thread_id": target_session_id,
            "prompt": operator_message,
            "idempotency_key": f"cockpit-chat-{idempotency_source}",
            "confirmation": APP_SERVER_CONFIRMATION_TOKEN,
            "timeout_seconds": _raw_cli_timeout_seconds(),
        },
    )
    turns_result: dict[str, Any] | None = None
    if start_result.get("ok"):
        turns_probe = invoke_codex_app_server_route(
            shell_root,
            route_id="thread_turns_list",
            args={
                "thread_id": target_session_id,
                "limit": 8,
                "items_view": "summary",
                "timeout_seconds": 20,
                "max_bytes": 24000,
            },
        )
        if isinstance(turns_probe, Mapping):
            turns_result = dict(turns_probe)
    response_text = _app_server_response_text(
        operator_message=operator_message,
        start_result=start_result,
        turns_result=turns_result,
    )
    receipt_path = str(start_result.get("receipt_path") or "")
    latest_status_path = str(start_result.get("latest_status_path") or "")
    ok = bool(start_result.get("ok"))
    status = "CODEX_APP_SERVER_TURN_COMPLETED" if ok else "CODEX_APP_SERVER_TURN_FAILED"
    finding = str(start_result.get("finding") or "")
    if not response_text:
        response_text = (
            "Codex app-server turn completed for the selected saved session."
            if ok
            else f"Codex app-server turn did not complete. Finding: {finding or 'unknown'}."
        )
        if receipt_path:
            response_text += f"\n\nReceipt: {receipt_path}"
    run = {
        "schema_id": "ion.codex_cockpit_app_server_run.v1",
        "run_id": f"codex_app_server_{created_at.replace(':', '').replace('+', 'Z')}_{_safe_slug(operator_message)}",
        "status": status,
        "ok": ok,
        "finding": finding or None,
        "created_at": created_at,
        "completed_at": _now(),
        "active_thread_id_before": target_session_id,
        "active_thread_id_after": target_session_id,
        "run_packet_path": receipt_path,
        "receipt_path": receipt_path,
        "latest_status_path": latest_status_path,
        "codex_cli_surface": "codex_app_server_turn_start",
        "turn_completed_notification_seen": start_result.get("turn_completed_notification_seen"),
        "timed_out": start_result.get("timed_out"),
        "response_sha256": _sha256_text(response_text) if response_text else None,
        "production_authority": False,
        "live_execution_authority": False,
    }
    return {
        "schema_id": "ion.codex_cockpit_app_server_result.v1",
        "ok": ok,
        "status": status,
        "finding": finding or None,
        "response_text": response_text,
        "active_thread_id": target_session_id,
        "run": run,
        "turn_start": dict(start_result),
        "thread_turns": turns_result,
        "response_mode": "codex_app_server",
        "production_authority": False,
        "live_execution_authority": False,
    }


def _create_codex_app_server_assistant_turn(
    *,
    created_at: str,
    operator_text: str,
    execution_mode: str,
    app_server_result: Mapping[str, Any],
    context_refs: list[str],
) -> dict[str, Any]:
    response_text = _trim(app_server_result.get("response_text") or "", limit=60000)
    if not response_text:
        response_text = f"Codex app-server returned no visible response. Status: {app_server_result.get('status') or 'unknown'}."
    return {
        "turn_id": f"assistant_{created_at.replace(':', '').replace('+', 'Z')}_{_safe_slug(operator_text)}",
        "lane_id": "codex_general",
        "author": "codex_app_server",
        "kind": "assistant_response",
        "message": response_text,
        "message_sha256": _sha256_text(response_text),
        "created_at": _now(),
        "context_refs": context_refs,
        "execution_mode": execution_mode,
        "response_mode": "codex_app_server",
        "codex_app_server": dict(app_server_result),
        "raw_codex_cli": None,
        "response_carrier": None,
        "wrapper_prompt_used": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _execution_status_message(
    *,
    execution_mode: str,
    queue_result: Mapping[str, Any] | None,
    runner_result: Mapping[str, Any] | None,
) -> str:
    if not queue_result:
        return "Codex execution bridge was not requested for this turn."
    queue_link = queue_result.get("queue_link") if isinstance(queue_result.get("queue_link"), Mapping) else {}
    lines = [
        "Codex execution bridge status.",
        "",
        f"- execution mode: {execution_mode}",
        f"- queue result: {'queued' if queue_result.get('ok') else 'blocked'}",
        f"- request id: {queue_link.get('request_id') or 'none'}",
        f"- packet path: {queue_link.get('packet_path') or 'none'}",
        f"- status: {queue_link.get('status') or queue_result.get('finding') or 'unknown'}",
    ]
    if runner_result is not None:
        lines.extend([
            f"- runner result: {'started' if runner_result.get('ok') else 'not started'}",
            f"- runner finding/result: {runner_result.get('result') or runner_result.get('finding') or 'none'}",
        ])
    else:
        lines.append("- runner result: not requested")
    lines.extend([
        "",
        "The bridge uses the existing ION Codex queue owner. It does not create a second queue, does not globally inject Capsule into other Codex CLI instances, and does not grant production/live authority.",
    ])
    return "\n".join(str(line) for line in lines)


def _append_codex_execution_status_turn(
    root: str | Path | None,
    *,
    source_turn_id: str,
    execution_mode: str,
    queue_result: Mapping[str, Any] | None,
    runner_result: Mapping[str, Any] | None = None,
    lane_id: str = "codex_general",
) -> dict[str, Any]:
    state = load_dual_chat_state(root)
    now = _now()
    queue_link = queue_result.get("queue_link") if isinstance(queue_result, Mapping) and isinstance(queue_result.get("queue_link"), Mapping) else {}
    target_lane_id = lane_id if lane_id in LANES else "codex_general"
    message = _execution_status_message(
        execution_mode=execution_mode,
        queue_result=queue_result,
        runner_result=runner_result,
    )
    turn = {
        "turn_id": f"exec_{now.replace(':', '').replace('+', 'Z')}_{_safe_slug(source_turn_id)}",
        "lane_id": target_lane_id,
        "author": "codex_capsule",
        "kind": "execution_status",
        "message": message,
        "message_sha256": _sha256_text(message),
        "created_at": now,
        "source_turn_id": source_turn_id,
        "execution_mode": execution_mode,
        "request_id": queue_link.get("request_id"),
        "packet_path": queue_link.get("packet_path"),
        "queue_status": queue_link.get("status"),
        "runner_result": runner_result,
        "production_authority": False,
        "live_execution_authority": False,
    }
    state["lanes"].setdefault(target_lane_id, {"lane_id": target_lane_id, **LANES[target_lane_id], "turns": [], "queue_links": []})
    state["lanes"][target_lane_id].setdefault("turns", []).append(turn)
    save_dual_chat_state(root, state)
    return turn


def record_chat_turn(
    root: str | Path | None,
    *,
    lane_id: str,
    message: str,
    author: str = "operator",
    execution_mode: str | None = None,
    agent_mode: str | None = None,
    codex_model_override: Mapping[str, Any] | None = None,
    response_carrier_enabled: bool | None = None,
    raw_codex_cli_enabled: bool | None = None,
    client_id: str | None = None,
    target_session_id: str | None = None,
    new_codex_session: bool | None = None,
    codex_session_transport: str | None = None,
    context_refs: list[str] | None = None,
    ide_context_bridge: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if lane_id not in LANES:
        return {"ok": False, "finding": "unknown_lane_id", "allowed_lanes": sorted(LANES)}
    text = _trim(message)
    if not text:
        return {"ok": False, "finding": "message_required"}
    resolved_execution_mode = _resolve_chat_execution_mode(execution_mode)
    normalized_author = _trim(author, limit=80) or "operator"
    normalized_client_id = _trim(client_id, limit=180)
    target_session_raw = _trim(target_session_id, limit=180)
    normalized_target_session_id = _safe_codex_session_id(target_session_raw)
    new_codex_session_requested = bool(new_codex_session)
    requested_session_transport = _resolve_codex_session_transport(codex_session_transport)
    if target_session_raw and not normalized_target_session_id:
        return {
            "ok": False,
            "finding": "unsafe_target_session_id",
            "target_session_id": target_session_raw,
            "production_authority": False,
            "live_execution_authority": False,
        }
    if normalized_target_session_id and new_codex_session_requested:
        return {
            "ok": False,
            "finding": "incompatible_target_session_and_new_codex_session",
            "target_session_id": normalized_target_session_id,
            "production_authority": False,
            "live_execution_authority": False,
        }
    effective_session_transport = (
        "app_server"
        if requested_session_transport == "app_server" and normalized_target_session_id
        else "raw_cli"
    )
    if _is_ephemeral_playwright_smoke(
        text,
        lane_id=lane_id,
        author=normalized_author,
        execution_mode=resolved_execution_mode,
    ):
        return _playwright_smoke_turn_result(
            root,
            lane_id=lane_id,
            message=text,
            author=normalized_author,
            execution_mode=resolved_execution_mode,
        )
    shell_root = _resolve_root(root)
    state = load_dual_chat_state(shell_root)
    prior_turns = list(state["lanes"].get(lane_id, {}).get("turns", [])) if isinstance(state.get("lanes"), Mapping) else []
    now = _now()
    turn_id = f"turn_{now.replace(':', '').replace('+', 'Z')}_{_safe_slug(text)}"
    turn_ide_context_bridge = _write_ide_context_bridge(
        shell_root,
        turn_id=turn_id,
        created_at=now,
        payload=ide_context_bridge,
    )
    bridge_context_refs = turn_ide_context_bridge.get("context_refs") if isinstance(turn_ide_context_bridge, Mapping) else []
    user_context_refs = _merge_context_refs(context_refs or [], bridge_context_refs)
    turn_skill_context = build_codex_solo_context_model(root, write=True) if lane_id == "codex_general" else None
    turn_chat_engine = build_codex_chat_engine_turn(
        root,
        lane_id=lane_id,
        message=text,
        execution_mode=resolved_execution_mode if lane_id == "codex_general" else "ion_comms_projection",
        codex_solo_context=turn_skill_context,
        codex_model_override=codex_model_override if lane_id == "codex_general" else None,
        context_refs=user_context_refs if lane_id == "codex_general" else None,
    )
    turn_skill_activation = turn_chat_engine.get("skill_activation") if isinstance(turn_chat_engine.get("skill_activation"), Mapping) else build_ion_skill_activation(
        root,
        lane_id=lane_id,
        objective=text,
        execution_mode=resolved_execution_mode if lane_id == "codex_general" else "ion_comms_projection",
        codex_solo_context=turn_skill_context,
    )
    turn_context_mount = turn_chat_engine.get("context_mount") if isinstance(turn_chat_engine.get("context_mount"), Mapping) else {}
    mounted_context_refs = _merge_context_refs(
        turn_context_mount.get("context_refs") if isinstance(turn_context_mount.get("context_refs"), list) else [],
        user_context_refs,
    )
    turn_context_binding = _build_chat_context_binding(
        state=state,
        lane_id=lane_id,
        source_turn_id=turn_id,
        created_at=now,
        chat_engine=turn_chat_engine,
        skill_activation=turn_skill_activation,
        mounted_context_refs=mounted_context_refs,
        selected_context_refs=user_context_refs,
        ide_context_bridge=turn_ide_context_bridge,
    )
    turn = {
        "turn_id": turn_id,
        "lane_id": lane_id,
        "author": normalized_author,
        "kind": "chat_turn",
        "message": text,
        "message_sha256": _sha256_text(text),
        "client_id": normalized_client_id or None,
        "target_session_id": normalized_target_session_id or None,
        "new_codex_session": new_codex_session_requested,
        "codex_session_target_mode": "resume_selected_session" if normalized_target_session_id else "new_cockpit_session" if new_codex_session_requested else "cockpit_active_session",
        "codex_session_transport": effective_session_transport,
        "created_at": now,
        "execution_mode": resolved_execution_mode if lane_id == "codex_general" else "ion_comms_projection",
        "agent_mode": _trim(agent_mode, limit=80) or None,
        "codex_model_override": dict(codex_model_override) if isinstance(codex_model_override, Mapping) else None,
        "context_refs": mounted_context_refs,
        "selected_context_refs": user_context_refs,
        "ide_context_bridge": turn_ide_context_bridge,
        "skill_activation": turn_skill_activation,
        "chat_engine": turn_chat_engine,
        "chat_context_binding": turn_context_binding,
        "production_authority": False,
        "live_execution_authority": False,
    }
    if turn_ide_context_bridge:
        state.setdefault("ide_context_bridges", []).append(turn_ide_context_bridge)
    _record_chat_context_binding(state, turn_context_binding)
    state["lanes"][lane_id].setdefault("turns", []).append(turn)
    if lane_id == "codex_general" and turn["author"] in {"operator", "user"}:
        save_dual_chat_state(root, state)
    pipeline_run = None
    assistant_turn = None
    if lane_id == "ion_system":
        pipeline_run = _create_pipeline_run(turn)
        state.setdefault("pipeline_runs", []).append(pipeline_run)
        if turn["author"] in {"operator", "user"} and resolved_execution_mode in {"auto", "respond_only"}:
            _mark_pipeline_prompt_projection(pipeline_run)
            assistant_turn = _create_ion_persona_assistant_turn(
                operator_text=text,
                created_at=now,
                execution_mode=resolved_execution_mode,
                chat_engine=turn_chat_engine,
                pipeline_run=pipeline_run,
                context_refs=mounted_context_refs,
                source_turn_id=turn_id,
            )
            state["lanes"][lane_id].setdefault("turns", []).append(assistant_turn)
    if lane_id == "codex_general" and turn["author"] in {"operator", "user"}:
        raw_cli_requested = raw_codex_cli_enabled is True and resolved_execution_mode in {"auto", "respond_only"}
        if raw_cli_requested:
            if effective_session_transport == "app_server" and normalized_target_session_id:
                app_server_result = run_codex_app_server_chat_turn(
                    root,
                    operator_message=text,
                    created_at=now,
                    target_session_id=normalized_target_session_id,
                    client_id=normalized_client_id,
                )
                app_server_state = state.setdefault("codex_app_server", {})
                app_server_state["active_thread_id"] = normalized_target_session_id
                app_server_state["latest_run"] = (app_server_result.get("run") or {}).get("run_packet_path") if isinstance(app_server_result.get("run"), Mapping) else None
                app_server_state["latest_status"] = app_server_result.get("status")
                app_server_state["selected_target_session_id"] = normalized_target_session_id
                app_server_state["policy"] = "selected_saved_session_uses_codex_app_server_thread_api"
                assistant_turn = _create_codex_app_server_assistant_turn(
                    created_at=now,
                    operator_text=text,
                    execution_mode=resolved_execution_mode,
                    app_server_result=app_server_result,
                    context_refs=mounted_context_refs,
                )
            else:
                raw_cli_state = state.setdefault("raw_codex_cli", {})
                active_thread_id = normalized_target_session_id or ("" if new_codex_session_requested else str(raw_cli_state.get("active_thread_id") or ""))
                raw_result = run_raw_codex_cli_chat_turn(
                    root,
                    operator_message=text,
                    created_at=now,
                    codex_model_override=codex_model_override,
                    active_thread_id=active_thread_id,
                    **({"ide_context_bridge": turn_ide_context_bridge} if turn_ide_context_bridge else {}),
                )
                if raw_result.get("active_thread_id"):
                    raw_cli_state["active_thread_id"] = raw_result.get("active_thread_id")
                raw_cli_state["latest_run"] = (raw_result.get("run") or {}).get("run_packet_path") if isinstance(raw_result.get("run"), Mapping) else None
                raw_cli_state["latest_status"] = raw_result.get("status")
                raw_cli_state["wrapper_prompt_used"] = False
                raw_cli_state["ide_context_bridge_ref"] = turn_ide_context_bridge.get("artifact_ref") if isinstance(turn_ide_context_bridge, Mapping) else None
                raw_cli_state["selected_target_session_id"] = normalized_target_session_id or None
                raw_cli_state["active_thread_source"] = "selected_saved_session" if normalized_target_session_id else "new_cockpit_thread" if new_codex_session_requested else "cockpit_active_thread"
                raw_cli_state["policy"] = "cockpit_chat_uses_raw_codex_cli_not_ion_response_carrier"
                assistant_turn = _create_raw_codex_cli_assistant_turn(
                    created_at=now,
                    operator_text=text,
                    execution_mode=resolved_execution_mode,
                    raw_result=raw_result,
                    context_refs=mounted_context_refs,
                )
        elif resolved_execution_mode in {"auto", "respond_only"}:
            assistant_turn = _create_codex_capsule_assistant_turn(
                root,
                operator_text=text,
                created_at=now,
                execution_mode=resolved_execution_mode,
                chat_engine=turn_chat_engine,
                codex_solo_context=turn_skill_context,
                prior_turns=[turn for turn in prior_turns if isinstance(turn, Mapping)],
                response_carrier_enabled=response_carrier_enabled,
            )
        if assistant_turn:
            state["lanes"][lane_id].setdefault("turns", []).append(assistant_turn)
    save_dual_chat_state(root, state)
    queue_result = None
    runner_result = None
    execution_status_turn = None
    queue_recommendation = turn_chat_engine.get("queue_recommendation") if isinstance(turn_chat_engine.get("queue_recommendation"), Mapping) else {}
    queue_execution_mode = resolved_execution_mode
    if lane_id in {"codex_general", "ion_system"} and turn["author"] in {"operator", "user"} and queue_execution_mode in {"queue_for_codex", "queue_and_start"}:
        queue_result = queue_chat_codex_work_packet(
            root,
            lane_id=lane_id,
            objective=text,
            confirmation=WRITE_CONFIRMATION_TOKEN,
            source_turn_id=turn_id,
            codex_model_override=codex_model_override,
            context_refs=user_context_refs,
        )
        if queue_execution_mode == "queue_and_start":
            if queue_result.get("ok") and _runner_start_enabled():
                runner_result = process_codex_queue_once(root, start=True, background=True)
            else:
                runner_result = {
                    "schema_id": "ion.codex_capsule_chat_runner_start_refusal.v1",
                    "ok": False,
                    "finding": "runner_start_not_enabled" if queue_result.get("ok") else "queue_not_ready",
                    "required_env": CHAT_RUNNER_START_ENV,
                    "production_authority": False,
                    "live_execution_authority": False,
                }
        execution_status_turn = _append_codex_execution_status_turn(
            root,
            source_turn_id=turn_id,
            execution_mode=queue_execution_mode,
            queue_result=queue_result,
            runner_result=runner_result,
            lane_id=lane_id,
        )
    model = build_dual_codex_chat_model(root, write=True)
    return {
        "ok": True,
        "turn": turn,
        "assistant_turn": assistant_turn,
        "execution_mode": resolved_execution_mode,
        "queue_execution_mode": queue_execution_mode,
        "queue_result": queue_result,
        "runner_result": runner_result,
        "execution_status_turn": execution_status_turn,
        "pipeline_run": pipeline_run,
        "model": model,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _branch_prompt(
    *,
    parent_kind: str,
    title: str,
    objective: str,
    parent_role: str,
    parent_message: str,
    parent_turn_id: str,
    parent_session_id: str,
) -> str:
    lines = [
        "Create a bounded Codex chat branch from the selected cockpit context.",
        "",
        f"Branch title: {title}",
        f"Objective: {objective}",
        f"Parent kind: {parent_kind}",
    ]
    if parent_session_id:
        lines.append(f"Parent Codex session: {parent_session_id}")
    if parent_turn_id:
        lines.append(f"Parent turn: {parent_turn_id}")
    if parent_role:
        lines.append(f"Parent role: {parent_role}")
    if parent_message:
        lines.extend([
            "",
            "Parent context excerpt:",
            _short_message(parent_message, limit=6000),
        ])
    lines.extend([
        "",
        "Continue as candidate branch work only. Do not claim production, live execution, accepted state, or secrets authority.",
    ])
    return "\n".join(lines)


def create_chat_branch(
    root: str | Path | None,
    *,
    confirmation: str,
    parent_kind: str,
    lane_id: str = "codex_general",
    title: str = "",
    objective: str = "",
    prompt: str = "",
    parent_turn_id: str = "",
    parent_session_id: str = "",
    parent_role: str = "",
    parent_message: str = "",
    parent_message_sha256: str = "",
) -> dict[str, Any]:
    if confirmation != WRITE_CONFIRMATION_TOKEN:
        return {"ok": False, "finding": "bounded_write_confirmation_required", "required_confirmation": WRITE_CONFIRMATION_TOKEN}
    if lane_id not in LANES:
        return {"ok": False, "finding": "unknown_lane_id", "allowed_lanes": sorted(LANES)}
    normalized_kind = _trim(parent_kind, limit=80) or "current_turn"
    if normalized_kind not in {"current_turn", "archive_session"}:
        return {"ok": False, "finding": "unsupported_branch_parent_kind", "allowed_parent_kinds": ["current_turn", "archive_session"]}
    normalized_title = _trim(title, limit=180)
    normalized_objective = _trim(objective, limit=4000)
    normalized_message = _trim(parent_message, limit=12000)
    normalized_session_id = _trim(parent_session_id, limit=180)
    normalized_turn_id = _trim(parent_turn_id, limit=180)
    if not normalized_title:
        normalized_title = "Branch from past chat" if normalized_kind == "archive_session" else "Branch from message"
    if not normalized_objective:
        normalized_objective = normalized_message or normalized_title
    normalized_prompt = _trim(prompt, limit=12000) or _branch_prompt(
        parent_kind=normalized_kind,
        title=normalized_title,
        objective=normalized_objective,
        parent_role=_trim(parent_role, limit=80),
        parent_message=normalized_message,
        parent_turn_id=normalized_turn_id,
        parent_session_id=normalized_session_id,
    )
    now = _now()
    branch_id = f"branch_{now.replace(':', '').replace('+', 'Z')}_{_safe_slug(normalized_title)}"
    message_sha = _trim(parent_message_sha256, limit=128) or (_sha256_text(normalized_message) if normalized_message else "")
    branch = {
        "schema_id": BRANCH_DRAFT_SCHEMA_ID,
        "branch_id": branch_id,
        "created_at": now,
        "status": "draft",
        "title": normalized_title,
        "objective": normalized_objective,
        "prompt": normalized_prompt,
        "prompt_sha256": _sha256_text(normalized_prompt),
        "lane_id": lane_id,
        "parent": {
            "kind": normalized_kind,
            "turn_id": normalized_turn_id or None,
            "session_id": normalized_session_id or None,
            "role": _trim(parent_role, limit=80) or None,
            "message_sha256": message_sha or None,
        },
        "codex_fork": {
            "command": ["codex", "fork", normalized_session_id] if normalized_session_id else [],
            "command_text": f"codex fork {normalized_session_id}" if normalized_session_id else "",
            "interactive_terminal_required": bool(normalized_session_id),
            "cockpit_spawned_process": False,
        },
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }
    state = load_dual_chat_state(root)
    state.setdefault("chat_branches", []).append(branch)
    save_dual_chat_state(root, state)
    model = build_dual_codex_chat_model(root, write=True)
    return {
        "ok": True,
        "branch": branch,
        "model": model,
        "production_authority": False,
        "live_execution_authority": False,
    }


def create_fresh_agent_capsule_chat(
    root: str | Path | None,
    *,
    confirmation: str,
    title: str = "",
    domain_id: str = "",
    role_id: str = "",
    target_path: str = "",
) -> dict[str, Any]:
    if confirmation != WRITE_CONFIRMATION_TOKEN:
        return {"ok": False, "finding": "bounded_write_confirmation_required", "required_confirmation": WRITE_CONFIRMATION_TOKEN}
    shell_root = _resolve_root(root)
    normalized_title = _trim(title, limit=180) or "Fresh Codex capsule chat"
    normalized_domain = _trim(domain_id, limit=180) or "domain.codex_carrier_sync"
    normalized_role = _trim(role_id, limit=180) or "role.codex_cli"
    now = _now()
    fresh_id = f"fresh_{now.replace(':', '').replace('+', 'Z')}_{_safe_slug(normalized_title)}"
    conversation_tag = _context_slug(normalized_domain)
    agent_tag = _context_slug(normalized_role)
    task_tag = _context_slug(normalized_title)
    if target_path:
        requested = Path(target_path).expanduser()
        target = requested if requested.is_absolute() else shell_root / requested
        target = target.resolve()
        try:
            target.relative_to(shell_root)
        except ValueError:
            return {
                "ok": False,
                "finding": "target_path_outside_ion_root",
                "target_path": target.as_posix(),
                "ion_root": shell_root.as_posix(),
            }
    else:
        target = (shell_root / CURRENT / "agent_context_branches" / conversation_tag / agent_tag / fresh_id).resolve()
    result = create_context_starter_capsule(target, shell_root, force=False)
    if not result.get("ok"):
        return result
    target_rel = target.relative_to(shell_root).as_posix()
    agent_context_files = [
        ".ion/AGENT.yaml",
        ".ion/DOMAIN.yaml",
        ".ion/RELATIONSHIPS.yaml",
        ".ion/HOOKS_AND_SKILLS.md",
    ]
    starter_refs = [f"{target_rel}/{rel}" for rel in [*CONTEXT_STARTER_REQUIRED_FILES, *agent_context_files]]
    chat_engine = {
        "domain_id": normalized_domain,
        "primary_domain": normalized_domain,
        "native_lenses": [
            {
                "role_id": normalized_role,
                "display_name": normalized_role,
                "primary_domain": normalized_domain,
                "purpose": "fresh Capsule-backed Codex chat agent instance",
            }
        ],
        "selected_skill": {
            "skill_id": normalized_role,
            "source": "fresh_capsule_chat",
        },
    }
    state = load_dual_chat_state(shell_root)
    binding = _build_chat_context_binding(
        state=state,
        lane_id="codex_general",
        source_turn_id=fresh_id,
        created_at=now,
        chat_engine=chat_engine,
        skill_activation=None,
        mounted_context_refs=starter_refs,
        selected_context_refs=starter_refs,
    )
    binding["branch_title"] = normalized_title
    binding["context_package_ref"] = f"{target_rel}/.ion/ACTIVE_CONTEXT_PACKAGE.md"
    binding["context_floor_refs"] = starter_refs
    binding["branch_context_refs"] = starter_refs
    binding["mounted_context_refs"] = starter_refs
    binding["fresh_agent_context_capsule"] = {
        "schema_id": "ion.codex_chat_fresh_agent_context_capsule.v1",
        "fresh_chat_id": fresh_id,
        "target_path": target.as_posix(),
        "target_ref": target_rel,
        "launch_command": result.get("launch_command"),
        "starter_required_files": starter_refs,
        "starter_runtime_policy": result.get("runtime_policy"),
    }
    binding["minimum_context"] = {
        "required": True,
        "floor": "folder_bound_context_starter_capsule",
        "target_ref": target_rel,
        "capsule_ref": f"{target_rel}/.ion/ION_CONTEXT_CAPSULE.yaml",
        "agent_ref": f"{target_rel}/.ion/AGENT.yaml",
        "domain_ref": f"{target_rel}/.ion/DOMAIN.yaml",
        "relationships_ref": f"{target_rel}/.ion/RELATIONSHIPS.yaml",
        "hooks_and_skills_ref": f"{target_rel}/.ion/HOOKS_AND_SKILLS.md",
        "identity_card_ref": f"{target_rel}/.ion/IDENTITY_CARD.md",
        "active_context_ref": f"{target_rel}/.ion/ACTIVE_CONTEXT_PACKAGE.md",
        "hot_context_ref": f"{target_rel}/.ion/HOT_CONTEXT.md",
        "long_horizon_ref": f"{target_rel}/.ion/LONG_HORIZON.json",
        "context_packages_ref": f"{target_rel}/.ion/CONTEXT_PACKAGES.json",
        "loaded_refs_ref": f"{target_rel}/.ion/LOADED_REFS.json",
        "mini_ref": f"{target_rel}/.ion/MINI.md",
        "capsule_md_ref": f"{target_rel}/.ion/CAPSULE.md",
        "route_ref": f"{target_rel}/.ion/ROUTE.json",
        "status_ref": f"{target_rel}/.ion/STATUS.json",
        "missing_required_refs": [],
    }
    binding.setdefault("context_policy", {})["fresh_agent_capsule_created"] = True
    binding.setdefault("context_policy", {})["old_archives_not_converted"] = True
    agent_identity = binding.get("agent_identity") if isinstance(binding.get("agent_identity"), Mapping) else {}
    agent_instance_id = _trim(agent_identity.get("agent_instance_id"), limit=220) or f"agent.{_context_slug(normalized_role)}.{fresh_id[-12:]}"
    agent_true_name = _trim(agent_identity.get("agent_true_name"), limit=220) or f"{normalized_role}::{fresh_id[-12:]}"
    branch_id = _trim(binding.get("branch_id"), limit=220)
    branch_title = _trim(binding.get("branch_title"), limit=220) or normalized_title
    context_instance_id = f"ctx_{fresh_id}"
    launch_command = str(result.get("launch_command") or f"codex -C {target}")
    agent_yaml = f"""schema_id: ion.codex_chat_agent_identity.v1
created_at: {json.dumps(now)}
context_instance_id: {json.dumps(context_instance_id)}
agent_instance_id: {json.dumps(agent_instance_id)}
agent_true_name: {json.dumps(agent_true_name)}
role_id: {json.dumps(normalized_role)}
clone_of_role_id: {json.dumps(normalized_role)}
domain_id: {json.dumps(normalized_domain)}
branch_id: {json.dumps(branch_id)}
branch_title: {json.dumps(branch_title)}
branch_type: "agent"
agent_tag: {json.dumps(agent_tag)}
conversation_tag: {json.dumps(conversation_tag)}
task_tag: {json.dumps(task_tag)}
parent_context_id: "ctx_shared_codex_solo_current"
context_root: {json.dumps(target_rel)}
launch_command: {json.dumps(launch_command)}
capsule_floor_required: true
identity_scope: chat_context_branch
parallel_clone_safe: true
shared_context_write: false
settlement_required: true
authority:
  production_authority: false
  live_execution_authority: false
  accepted_state_authority: false
  secrets_authority: false
"""
    domain_yaml = f"""schema_id: ion.codex_chat_domain_binding.v1
created_at: {json.dumps(now)}
domain_id: {json.dumps(normalized_domain)}
domain_binding_kind: fresh_codex_chat_capsule
agent_instance_id: {json.dumps(agent_instance_id)}
agent_true_name: {json.dumps(agent_true_name)}
branch_id: {json.dumps(branch_id)}
branch_title: {json.dumps(branch_title)}
context_package_ref: ".ion/ACTIVE_CONTEXT_PACKAGE.md"
capsule_ref: ".ion/ION_CONTEXT_CAPSULE.yaml"
hot_context_ref: ".ion/HOT_CONTEXT.md"
long_horizon_ref: ".ion/LONG_HORIZON.json"
context_packages_ref: ".ion/CONTEXT_PACKAGES.json"
authority:
  production_authority: false
  live_execution_authority: false
  accepted_state_authority: false
  secrets_authority: false
"""
    relationships_yaml = f"""schema_id: ion.codex_chat_agent_relationships.v1
created_at: {json.dumps(now)}
agent_instance_id: {json.dumps(agent_instance_id)}
role_archetype_id: {json.dumps(normalized_role)}
domain_id: {json.dumps(normalized_domain)}
branch_id: {json.dumps(branch_id)}
context_instance_id: {json.dumps(context_instance_id)}
parent_context_id: ctx_shared_codex_solo_current
same_domain_sibling_policy: awareness_only
archive_chat_policy: witness_only_unless_explicitly_attached
parent_context:
  shared_codex_solo_capsule_ref: "ION/05_context/current/codex_solo/CAPSULE.md"
  shared_codex_solo_hot_context_ref: "ION/05_context/current/codex_solo/HOT_CONTEXT.md"
  shared_codex_solo_long_horizon_ref: "ION/05_context/current/codex_solo/LONG_HORIZON.json"
local_context:
  capsule_floor_ref: ".ion/ION_CONTEXT_CAPSULE.yaml"
  active_context_ref: ".ion/ACTIVE_CONTEXT_PACKAGE.md"
  hot_context_ref: ".ion/HOT_CONTEXT.md"
  long_horizon_ref: ".ion/LONG_HORIZON.json"
  context_packages_ref: ".ion/CONTEXT_PACKAGES.json"
  mini_ref: ".ion/MINI.md"
not_claimed:
  - production_authority
  - live_execution_authority
  - accepted_state_authority
  - secrets_authority
"""
    hooks_and_skills_md = f"""# Hooks and Skills for {agent_true_name}

## Identity

- agent_instance_id: `{agent_instance_id}`
- agent_true_name: `{agent_true_name}`
- role_id: `{normalized_role}`
- domain_id: `{normalized_domain}`
- branch_id: `{branch_id}`

## Codex boot order

1. Read `AGENTS.md`.
2. Read `.ion/ION_CONTEXT_CAPSULE.yaml`.
3. Read `.ion/AGENT.yaml`.
4. Read `.ion/DOMAIN.yaml`.
5. Read `.ion/RELATIONSHIPS.yaml`.
6. Read `.ion/ACTIVE_CONTEXT_PACKAGE.md`.
7. Read `.ion/ROUTE.json`.
8. Read `.ion/HOT_CONTEXT.md`.
9. Read `.ion/CONTEXT_PACKAGES.json`.

## Hook posture

This folder records hook and skill intent for a unique Codex agent instance.
It does not claim live hook execution unless Codex is launched from this folder
and a real hook runner/config proves the hook fired.

## Skill posture

Use skills that match the active domain and local `AGENTS.md` instructions.
Do not import another chat's raw context unless it is explicitly attached as
historical witness material.
"""
    for rel, content in {
        ".ion/AGENT.yaml": agent_yaml,
        ".ion/DOMAIN.yaml": domain_yaml,
        ".ion/RELATIONSHIPS.yaml": relationships_yaml,
        ".ion/HOOKS_AND_SKILLS.md": hooks_and_skills_md,
    }.items():
        (target / rel).write_text(content.rstrip() + "\n", encoding="utf-8")
    agents_path = target / "AGENTS.md"
    if agents_path.exists():
        agents_path.write_text(
            agents_path.read_text(encoding="utf-8").rstrip()
            + f"""

## Fresh Codex Agent Identity

- agent_instance_id: `{agent_instance_id}`
- agent_true_name: `{agent_true_name}`
- role_id: `{normalized_role}`
- domain_id: `{normalized_domain}`
- branch_id: `{branch_id}`
- branch_title: `{branch_title}`

Read `.ion/AGENT.yaml`, `.ion/DOMAIN.yaml`, `.ion/RELATIONSHIPS.yaml`, and `.ion/HOOKS_AND_SKILLS.md` before material work.
This folder is a unique Capsule-backed Codex agent instance. Do not collapse it into another chat with the same role display name.
"""
            + "\n",
            encoding="utf-8",
        )
    config_path = target / ".codex/config.toml"
    if config_path.exists():
        config_path.write_text(
            config_path.read_text(encoding="utf-8").rstrip()
            + f"""

[ion_agent_context]
agent_instance_id = {json.dumps(agent_instance_id)}
agent_true_name = {json.dumps(agent_true_name)}
role_id = {json.dumps(normalized_role)}
domain_id = {json.dumps(normalized_domain)}
branch_id = {json.dumps(branch_id)}
context_root = {json.dumps(target_rel)}
capsule_floor_required = true
"""
            + "\n",
            encoding="utf-8",
        )
    local_required_refs = [*CONTEXT_STARTER_REQUIRED_FILES, *agent_context_files]
    loaded_refs_payload = {
        "schema_id": "ion.agent_branch_loaded_refs.v1",
        "created_at": now,
        "context_instance_id": context_instance_id,
        "branch_id": branch_id,
        "parent_context_id": "ctx_shared_codex_solo_current",
        "loaded_refs": [
            {
                "path": rel,
                "required": True,
                "classification": "local_agent_branch_context",
            }
            for rel in local_required_refs
        ],
        "parent_refs": [
            "ION/05_context/current/codex_solo/CAPSULE.md",
            "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
            "ION/05_context/current/codex_solo/LONG_HORIZON.json",
            "ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json",
            "ION/05_context/current/codex_solo/ROUTE.json",
        ],
        "shared_context_write": False,
        "settlement_required": True,
        "production_authority": False,
        "live_execution_authority": False,
    }
    context_packages_payload = {
        "schema_id": "ion.agent_branch_context_packages.v1",
        "created_at": now,
        "context_instance_id": context_instance_id,
        "branch_id": branch_id,
        "selected_by_default": [
            "minimum_working_capsule",
            "agent_identity_package",
            "active_context_package",
            "hot_context",
        ],
        "packages": [
            {
                "package_id": "minimum_working_capsule",
                "context_type": "active_short_horizon",
                "load_policy": "always_inline_first",
                "path_refs": [".ion/ION_CONTEXT_CAPSULE.yaml", ".ion/CAPSULE.md"],
            },
            {
                "package_id": "agent_identity_package",
                "context_type": "agent_domain_branch_identity",
                "load_policy": "always_inline_first",
                "path_refs": [".ion/AGENT.yaml", ".ion/DOMAIN.yaml", ".ion/RELATIONSHIPS.yaml", ".ion/IDENTITY_CARD.md"],
            },
            {
                "package_id": "active_context_package",
                "context_type": "local_working_context",
                "load_policy": "always_inline_first",
                "path_refs": [".ion/ACTIVE_CONTEXT_PACKAGE.md"],
            },
            {
                "package_id": "hot_context",
                "context_type": "compiled_hot_context",
                "load_policy": "always_inline_first",
                "path_refs": [".ion/HOT_CONTEXT.md"],
            },
            {
                "package_id": "long_horizon_index",
                "context_type": "compressed_long_horizon",
                "load_policy": "load_when_older_continuity_or_prior_decisions_matter",
                "path_refs": [".ion/LONG_HORIZON.json"],
            },
            {
                "package_id": "parent_shared_codex_solo",
                "context_type": "parent_context_witness",
                "load_policy": "route_deeper_only_do_not_write",
                "path_refs": loaded_refs_payload["parent_refs"],
            },
        ],
        "production_authority": False,
        "live_execution_authority": False,
    }
    hot_context_md = f"""# Agent Branch Hot Context

generated_at: {now}
witness_policy: Capsule is the minimum working context. Mini is lookup only. Parent Codex Solo is witness/base context and must not be written by this branch.
production_authority: false
live_execution_authority: false

## IDENTITY CARD

AGENT_TAG: {agent_tag}
CONVERSATION_TAG: {conversation_tag}
TASK_TAG: {task_tag}
CONTEXT_INSTANCE: {context_instance_id}
BRANCH_ID: {branch_id}
PARENT_CONTEXT: ctx_shared_codex_solo_current
ROOT: {shell_root.as_posix()}
SHARED_CONTEXT_WRITE: false
SETTLEMENT_REQUIRED: true

## LOCAL CONTEXT FLOOR

- `.ion/ION_CONTEXT_CAPSULE.yaml`
- `.ion/CAPSULE.md`
- `.ion/MINI.md`
- `.ion/HOT_CONTEXT.md`
- `.ion/LONG_HORIZON.json`
- `.ion/CONTEXT_PACKAGES.json`
- `.ion/ROUTE.json`

## NEXT

Launch with `{launch_command}`. Inspect local files first. Use parent Codex Solo only as witness/base context unless explicit settlement is requested.
"""
    identity_card_md = f"""# Agent Branch Identity Card

AGENT_TAG: {agent_tag}
CONVERSATION_TAG: {conversation_tag}
TASK_TAG: {task_tag}
CONTEXT_INSTANCE: {context_instance_id}
BRANCH_ID: {branch_id}
PARENT_CONTEXT: ctx_shared_codex_solo_current
ROOT: {shell_root.as_posix()}
SHARED_CONTEXT_WRITE: false
SETTLEMENT_REQUIRED: true
"""
    status_payload = {
        "schema_id": "ion.agent_branch_status.v1",
        "ready": True,
        "created_at": now,
        "capsule_kind": "agent_branch_context_capsule",
        "context_instance_id": context_instance_id,
        "branch_id": branch_id,
        "agent_tag": agent_tag,
        "conversation_tag": conversation_tag,
        "task_tag": task_tag,
        "parent_context_id": "ctx_shared_codex_solo_current",
        "launch_command": launch_command,
        "minimum_context": {
            "capsule_ref": ".ion/ION_CONTEXT_CAPSULE.yaml",
            "hot_context_ref": ".ion/HOT_CONTEXT.md",
            "long_horizon_ref": ".ion/LONG_HORIZON.json",
            "context_packages_ref": ".ion/CONTEXT_PACKAGES.json",
            "route_ref": ".ion/ROUTE.json",
            "mini_ref": ".ion/MINI.md",
        },
        "shared_context_write": False,
        "settlement_required": True,
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
    }
    (target / ".ion/LOADED_REFS.json").write_text(json.dumps(loaded_refs_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (target / ".ion/CONTEXT_PACKAGES.json").write_text(json.dumps(context_packages_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (target / ".ion/HOT_CONTEXT.md").write_text(hot_context_md.rstrip() + "\n", encoding="utf-8")
    (target / ".ion/IDENTITY_CARD.md").write_text(identity_card_md.rstrip() + "\n", encoding="utf-8")
    (target / ".ion/STATUS.json").write_text(json.dumps(status_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    registry_path = shell_root / CURRENT / "agent_context_branches" / "BRANCH_CAPSULE_REGISTRY_V0_1.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else {}
    except json.JSONDecodeError:
        registry = {}
    if not isinstance(registry, dict):
        registry = {}
    branches = registry.get("branches") if isinstance(registry.get("branches"), list) else []
    branch_record = {
        "context_instance_id": context_instance_id,
        "branch_id": branch_id,
        "branch_type": "agent",
        "agent_tag": agent_tag,
        "conversation_tag": conversation_tag,
        "task_tag": task_tag,
        "parent_context_id": "ctx_shared_codex_solo_current",
        "root": shell_root.as_posix(),
        "path": target_rel,
        "loaded_refs_path": f"{target_rel}/.ion/LOADED_REFS.json",
        "status_path": f"{target_rel}/.ion/STATUS.json",
        "shared_context_write": False,
        "settlement_required": True,
    }
    branches = [item for item in branches if not isinstance(item, Mapping) or item.get("branch_id") != branch_id]
    branches.append(branch_record)
    registry.update({
        "schema_id": "ion.agent_branch_capsule_registry.v0_1",
        "updated_at": now,
        "branches": branches[-200:],
        "production_authority": False,
        "live_execution_authority": False,
    })
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _record_chat_context_binding(state, binding)
    fresh_record = {
        "schema_id": "ion.codex_chat_fresh_agent_capsule_record.v1",
        "fresh_chat_id": fresh_id,
        "created_at": now,
        "title": normalized_title,
        "domain_id": normalized_domain,
        "role_id": normalized_role,
        "target_ref": target_rel,
        "target_path": target.as_posix(),
        "launch_command": launch_command,
        "chat_context_binding": binding,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }
    state.setdefault("fresh_agent_capsule_chats", []).append(fresh_record)
    save_dual_chat_state(shell_root, state)
    model = build_dual_codex_chat_model(shell_root, write=True)
    return {
        "ok": True,
        "fresh_agent_capsule_chat": fresh_record,
        "chat_context_binding": binding,
        "model": model,
        "created_files": [*(result.get("created_files", []) if isinstance(result.get("created_files"), list) else []), *agent_context_files],
        "empty_context_dirs": result.get("empty_context_dirs", []),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def _create_pipeline_run(turn: Mapping[str, Any]) -> dict[str, Any]:
    run_id = f"ion_pipe_{str(turn.get('created_at')).replace(':', '').replace('+', 'Z')}_{_safe_slug(str(turn.get('turn_id') or 'turn'))}"
    stages = []
    for index, (stage_id, label, description) in enumerate(ION_PIPELINE_STAGES, start=1):
        model_move = build_codex_model_move_plan(
            lane_id="ion_system",
            stage_id=stage_id,
            objective=f"{label}: {description}",
        )
        stages.append({
            "index": index,
            "stage_id": stage_id,
            "label": label,
            "description": description,
            "status": "ready" if index == 1 else "pending",
            "model_move": model_move,
            "receipt_refs": [],
            "request_refs": [],
        })
    return {
        "schema_id": "ion.codex_capsule_chat_ion_comms_pipeline_projection.v1",
        "run_id": run_id,
        "source_turn_id": turn.get("turn_id"),
        "source_lane_id": turn.get("lane_id"),
        "status": "PIPELINE_PROJECTED_AWAITING_PROOF_GATED_WORK",
        "created_at": turn.get("created_at"),
        "stages": stages,
        "production_authority": False,
        "live_execution_authority": False,
    }


def queue_chat_codex_work_packet(
    root: str | Path | None,
    *,
    lane_id: str,
    objective: str,
    confirmation: str,
    source_turn_id: str | None = None,
    idempotency_key: str | None = None,
    client_request_id: str | None = None,
    codex_model_override: Mapping[str, Any] | None = None,
    context_refs: list[str] | None = None,
) -> dict[str, Any]:
    if confirmation != WRITE_CONFIRMATION_TOKEN:
        return {"ok": False, "finding": "bounded_write_confirmation_required", "required_confirmation": WRITE_CONFIRMATION_TOKEN}
    if lane_id not in LANES:
        return {"ok": False, "finding": "unknown_lane_id", "allowed_lanes": sorted(LANES)}
    text = _trim(objective)
    if not text:
        return {"ok": False, "finding": "objective_required"}
    state = load_dual_chat_state(root)
    queued_text = text
    user_context_refs = _merge_context_refs(context_refs or [])
    merged_context_refs: list[str] = []
    codex_solo_context: dict[str, Any] | None = None
    stage_id = "mason_codex_work" if lane_id == "ion_system" else "codex_general_work"
    model_move, model_override = apply_codex_model_override(
        build_codex_model_move_plan(root, lane_id=lane_id, stage_id=stage_id, objective=text),
        codex_model_override,
    )
    skill_activation: dict[str, Any] | None = None
    if lane_id == "codex_general":
        codex_solo_context = build_codex_solo_context_model(root, write=True)
        merged_context_refs = _merge_context_refs(_codex_solo_context_refs(codex_solo_context), user_context_refs)
        chat_engine_turn = build_codex_chat_engine_turn(
            root,
            lane_id=lane_id,
            message=text,
            execution_mode="queue_for_codex",
            codex_solo_context=codex_solo_context,
            codex_model_override=codex_model_override,
            context_refs=user_context_refs,
        )
        if isinstance(chat_engine_turn.get("model_move"), Mapping):
            model_move = dict(chat_engine_turn["model_move"])
        if isinstance(chat_engine_turn.get("model_override"), Mapping):
            model_override = dict(chat_engine_turn["model_override"])
        skill_activation = dict(chat_engine_turn.get("skill_activation")) if isinstance(chat_engine_turn.get("skill_activation"), Mapping) else build_ion_skill_activation(
            root,
            lane_id=lane_id,
            objective=text,
            execution_mode="queue_for_codex",
            codex_solo_context=codex_solo_context,
            model_move=model_move,
        )
        if not codex_solo_context.get("ok"):
            model = build_dual_codex_chat_model(root, write=True)
            return {
                "ok": False,
                "finding": "codex_solo_context_not_ready",
                "codex_solo_context": codex_solo_context,
                "model": model,
                "production_authority": False,
                "live_execution_authority": False,
            }
        queued_text = _codex_general_queued_objective(text, codex_solo_context, model_move, skill_activation, chat_engine_turn, merged_context_refs)
        archive_context = _active_archive_attachment_context(_resolve_root(root), state)
        if archive_context:
            queued_text = "\n".join([
                queued_text,
                "",
                "ATTACHED PAST CHAT CONTEXT:",
                archive_context,
                "",
                "Use attached past chat context only as explicit historical witness material. Do not treat it as accepted current state.",
            ])
    else:
        chat_engine_turn = build_codex_chat_engine_turn(
            root,
            lane_id=lane_id,
            message=text,
            execution_mode="ion_comms_projection",
            context_refs=user_context_refs,
        )
        merged_context_refs = user_context_refs
        skill_activation = build_ion_skill_activation(
            root,
            lane_id=lane_id,
            objective=text,
            execution_mode="ion_comms_projection",
            model_move=model_move,
        )
    stable_key = str(idempotency_key or "").strip()
    if not stable_key:
        source = str(source_turn_id or "").strip()
        key_seed = f"{lane_id}:{source or _sha256_text(queued_text)}"
        stable_key = f"dual_codex_chat:{_sha256_text(key_seed)}"
    chat_context_binding = _build_chat_context_binding(
        state=state,
        lane_id=lane_id,
        source_turn_id=str(source_turn_id or stable_key),
        created_at=_now(),
        chat_engine=chat_engine_turn,
        skill_activation=skill_activation,
        mounted_context_refs=merged_context_refs,
        selected_context_refs=user_context_refs,
    )
    _record_chat_context_binding(state, chat_context_binding)
    connector_args = {
        "objective": queued_text,
        "codex_model_move": model_move,
        "required_context_reads": [{"path": ref, "kind": "file", "required": True} for ref in merged_context_refs],
        "ion_skill_activation": skill_activation,
        "ion_chat_engine_turn": chat_engine_turn,
        "ion_chat_context_binding": chat_context_binding,
        "codex_model_override": model_override,
        "request_kind": (chat_engine_turn.get("carrier_strategy") or {}).get("request_kind") if isinstance(chat_engine_turn.get("carrier_strategy"), Mapping) else "codex_work",
        "idempotency_key": stable_key,
    }
    if client_request_id:
        connector_args["client_request_id"] = client_request_id
    result = call_chatgpt_connector_tool(
        root,
        "ion_request_codex_work_packet",
        connector_args,
    )
    data = result.get("data") if isinstance(result.get("data"), Mapping) else {}
    link = {
        "created_at": _now(),
        "lane_id": lane_id,
        "source_turn_id": source_turn_id,
        "objective": text,
        "queued_objective_sha256": _sha256_text(queued_text),
        "context_refs": merged_context_refs,
        "selected_context_refs": user_context_refs,
        "chat_context_binding": chat_context_binding,
        "codex_solo_context_verdict": (codex_solo_context or {}).get("verdict"),
        "skill_activation": skill_activation,
        "chat_engine": chat_engine_turn,
        "model_move": model_move,
        "model_override": model_override,
        "model_move_summary": summarize_model_move(model_move),
        "request_id": data.get("request_id"),
        "packet_path": data.get("packet_path"),
        "status": "QUEUED_FOR_CODEX_CARRIER" if result.get("ok") else "QUEUE_REQUEST_BLOCKED",
        "result": result,
    }
    state["lanes"][lane_id].setdefault("queue_links", []).append(link)
    if lane_id == "ion_system" and state.get("pipeline_runs"):
        latest = state["pipeline_runs"][-1]
        if isinstance(latest, dict):
            for stage in latest.get("stages", []):
                if stage.get("stage_id") == "mason_codex_work":
                    stage["status"] = "queued_for_codex_carrier" if result.get("ok") else "queue_blocked"
                    stage["model_move"] = model_move
                    stage.setdefault("request_refs", []).append(data.get("packet_path"))
            latest["status"] = "CODEX_WORK_PACKET_QUEUED" if result.get("ok") else "CODEX_WORK_PACKET_BLOCKED"
    save_dual_chat_state(root, state)
    solo_post = None
    if lane_id == "codex_general":
        evidence = [ref for ref in merged_context_refs if ref]
        if data.get("packet_path"):
            evidence.append(str(data.get("packet_path")))
        solo_post = record_codex_solo_machine_receipt(
            root,
            event_type="codex_work_packet_queued",
            source="kernel.ion_dual_codex_chat.queue_chat_codex_work_packet",
            summary=f"Queued Codex solo work packet: {text}",
            evidence_paths=evidence,
            status=link["status"],
            payload={"queue_link": link},
            next_action="Wait for Codex task return, then verify proof and update capsule route.",
        )
    model = build_dual_codex_chat_model(root, write=True)
    return {
        "ok": bool(result.get("ok")),
        "queue_link": link,
        "codex_solo_post": solo_post,
        "connector_result": result,
        "model": model,
        "production_authority": False,
        "live_execution_authority": False,
    }


def pin_dual_chat_memory(
    root: str | Path | None,
    *,
    lane_id: str,
    text: str,
    confirmation: str,
    source_turn_id: str | None = None,
    write_codex_memory: bool = True,
) -> dict[str, Any]:
    if confirmation != WRITE_CONFIRMATION_TOKEN:
        return {"ok": False, "finding": "bounded_write_confirmation_required", "required_confirmation": WRITE_CONFIRMATION_TOKEN}
    if lane_id not in LANES:
        return {"ok": False, "finding": "unknown_lane_id", "allowed_lanes": sorted(LANES)}
    memory_text = _trim(text, limit=4000)
    if not memory_text:
        return {"ok": False, "finding": "memory_text_required"}
    state = load_dual_chat_state(root)
    now = _now()
    pin = {
        "pin_id": f"mem_{now.replace(':', '').replace('+', 'Z')}_{_safe_slug(memory_text)}",
        "lane_id": lane_id,
        "source_turn_id": source_turn_id,
        "text": memory_text,
        "text_sha256": _sha256_text(memory_text),
        "created_at": now,
        "status": "active",
        "memory_scope": "repo_and_codex_memory",
        "production_authority": False,
        "live_execution_authority": False,
    }
    state.setdefault("memory", {}).setdefault("pins", []).append(pin)
    codex_memory_path = Path(str(state["memory"].get("codex_memory_path") or DEFAULT_CODEX_MEMORY_PATH)).expanduser()
    if write_codex_memory:
        codex_memory_path.parent.mkdir(parents=True, exist_ok=True)
        existing = codex_memory_path.read_text(encoding="utf-8", errors="replace") if codex_memory_path.exists() else "# ION Codex Chat Memory\n\n"
        entry = "\n".join([
            f"## {pin['pin_id']}",
            f"- created_at: {now}",
            f"- lane_id: {lane_id}",
            f"- source_turn_id: {source_turn_id or 'none'}",
            f"- text_sha256: {pin['text_sha256']}",
            "",
            memory_text,
            "",
        ])
        codex_memory_path.write_text(existing.rstrip() + "\n\n" + entry, encoding="utf-8")
    state["memory"]["codex_memory_path"] = str(codex_memory_path)
    save_dual_chat_state(root, state)
    solo_post = None
    if lane_id == "codex_general":
        solo_post = record_codex_solo_machine_receipt(
            root,
            event_type="codex_memory_pinned",
            source="kernel.ion_dual_codex_chat.pin_dual_chat_memory",
            summary=f"Pinned Codex solo memory: {memory_text}",
            evidence_paths=[str(codex_memory_path)],
            status="MEMORY_PINNED",
            payload={"pin": pin},
            next_action="Use pinned memory only as explicit witness context for later Codex work.",
        )
    model = build_dual_codex_chat_model(root, write=True)
    return {"ok": True, "pin": pin, "codex_memory_path": str(codex_memory_path), "codex_solo_post": solo_post, "model": model}


def _e(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def _chat_turn_groups(
    turns: list[Mapping[str, Any]],
    *,
    return_records: list[Mapping[str, Any]] | None = None,
    turn_traces: list[Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    returns_by_source: dict[str, list[dict[str, Any]]] = {}
    for raw_record in return_records or []:
        if not isinstance(raw_record, Mapping):
            continue
        source_turn_id = str(raw_record.get("source_turn_id") or "").strip()
        if source_turn_id:
            returns_by_source.setdefault(source_turn_id, []).append(dict(raw_record))
    traces_by_turn = {
        str(trace.get("turn_id")): dict(trace)
        for trace in turn_traces or []
        if isinstance(trace, Mapping) and trace.get("turn_id")
    }
    groups: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_turn in turns:
        turn = dict(raw_turn)
        kind = str(turn.get("kind") or "chat_turn")
        author = str(turn.get("author") or "")
        if kind == "chat_turn" and author in {"operator", "user"}:
            current = {
                "group_id": turn.get("turn_id"),
                "created_at": turn.get("created_at"),
                "user_turn": turn,
                "assistant_turns": [],
                "execution_turns": [],
                "return_records": returns_by_source.get(str(turn.get("turn_id") or ""), []),
                "turn_trace": traces_by_turn.get(str(turn.get("turn_id") or "")),
                "context_turns": [],
                "other_turns": [],
            }
            groups.append(current)
            continue
        if current is None:
            current = {
                "group_id": f"system_{len(groups) + 1}",
                "created_at": turn.get("created_at"),
                "user_turn": None,
                "assistant_turns": [],
                "execution_turns": [],
                "return_records": [],
                "turn_trace": None,
                "context_turns": [],
                "other_turns": [],
            }
            groups.append(current)
        if kind == "assistant_response":
            current["assistant_turns"].append(turn)
        elif kind == "execution_status":
            current["execution_turns"].append(turn)
        elif kind == "mini_auto_post":
            current["context_turns"].append(turn)
        else:
            current["other_turns"].append(turn)
    return groups


def build_codex_capsule_chat_ui_model(model: Mapping[str, Any]) -> dict[str, Any]:
    lanes = model.get("lanes") if isinstance(model.get("lanes"), Mapping) else {}
    codex_lane = lanes.get("codex_general") if isinstance(lanes.get("codex_general"), Mapping) else {}
    turns = [turn for turn in codex_lane.get("turns", []) if isinstance(turn, Mapping)]
    codex_solo = model.get("codex_solo_context") if isinstance(model.get("codex_solo_context"), Mapping) else {}
    capsule = codex_solo.get("capsule") if isinstance(codex_solo.get("capsule"), Mapping) else {}
    mini = codex_solo.get("mini") if isinstance(codex_solo.get("mini"), Mapping) else {}
    route = codex_solo.get("route") if isinstance(codex_solo.get("route"), Mapping) else {}
    long_horizon = codex_solo.get("long_horizon") if isinstance(codex_solo.get("long_horizon"), Mapping) else {}
    context_packages = codex_solo.get("context_packages") if isinstance(codex_solo.get("context_packages"), Mapping) else {}
    queue = model.get("codex_queue") if isinstance(model.get("codex_queue"), Mapping) else {}
    runner = queue.get("runner") if isinstance(queue.get("runner"), Mapping) else {}
    latest_work_requests = queue.get("latest_work_requests") if isinstance(queue.get("latest_work_requests"), list) else []
    latest_task_returns = queue.get("latest_task_returns") if isinstance(queue.get("latest_task_returns"), list) else []
    return_hydration = queue.get("return_hydration") if isinstance(queue.get("return_hydration"), Mapping) else {}
    hydrated_return_records = [
        record for record in return_hydration.get("records", []) if isinstance(record, Mapping)
    ]
    turn_trace_index = model.get("turn_traces") if isinstance(model.get("turn_traces"), Mapping) else {}
    turn_trace_records = [
        trace for trace in turn_trace_index.get("traces", []) if isinstance(trace, Mapping)
    ]
    agents = model.get("agents") if isinstance(model.get("agents"), Mapping) else {}
    skills = model.get("skills") if isinstance(model.get("skills"), Mapping) else {}
    chat_engine = model.get("chat_engine") if isinstance(model.get("chat_engine"), Mapping) else {}
    assistant_work_routes = model.get("assistant_work_routes") if isinstance(model.get("assistant_work_routes"), Mapping) else {}
    chat_response_carrier = model.get("chat_response_carrier") if isinstance(model.get("chat_response_carrier"), Mapping) else {}
    response_runs = model.get("response_runs") if isinstance(model.get("response_runs"), Mapping) else {}
    execution_bridge = model.get("execution_bridge") if isinstance(model.get("execution_bridge"), Mapping) else {}
    remote_access = model.get("remote_access") if isinstance(model.get("remote_access"), Mapping) else {}
    ion_comms = model.get("ion_comms") if isinstance(model.get("ion_comms"), Mapping) else {}
    memory = model.get("memory") if isinstance(model.get("memory"), Mapping) else {}
    route_entries = route.get("entries") if isinstance(route.get("entries"), list) else []
    missing_route = [
        entry.get("path")
        for entry in route_entries
        if isinstance(entry, Mapping) and not entry.get("exists")
    ]
    latest_capsule_rows = capsule.get("recent_rows") if isinstance(capsule.get("recent_rows"), list) else []
    latest_receipt = latest_capsule_rows[-1] if latest_capsule_rows else None
    current_skill = skills.get("current_activation") if isinstance(skills.get("current_activation"), Mapping) else {}
    conversation_summary = {
        "turn_count": len(turns),
        "user_turn_count": sum(1 for turn in turns if turn.get("kind", "chat_turn") == "chat_turn" and turn.get("author") in {"operator", "user"}),
        "assistant_turn_count": sum(1 for turn in turns if turn.get("kind") == "assistant_response"),
        "execution_status_count": sum(1 for turn in turns if turn.get("kind") == "execution_status"),
        "hydrated_return_count": len(hydrated_return_records),
        "turn_trace_count": len(turn_trace_records),
        "proof_accepted_count": sum(1 for record in hydrated_return_records if record.get("proof_status") == "accepted"),
        "proof_blocked_count": sum(1 for record in hydrated_return_records if record.get("proof_status") == "blocked"),
        "latest_receipt": latest_receipt,
    }
    activity = []
    if runner:
        activity.append({
            "kind": "runner",
            "status": "active" if runner.get("active_process_running") else "idle",
            "label": runner.get("verdict") or "Codex runner",
            "detail": runner.get("next_request_path") or "no queued request selected",
        })
    for item in latest_work_requests[:3]:
        if isinstance(item, Mapping):
            activity.append({
                "kind": "work_request",
                "status": "queued",
                "label": item.get("name") or "work request",
                "detail": item.get("path"),
            })
    for item in latest_task_returns[:3]:
        if isinstance(item, Mapping):
            activity.append({
                "kind": "task_return",
                "status": "returned",
                "label": item.get("name") or "task return",
                "detail": item.get("path"),
            })
    context_drawer = {
        "mini_text": mini.get("text") or "",
        "recent_rows": latest_capsule_rows,
        "route_ok": route.get("ok"),
        "missing_route": missing_route,
        "long_horizon": long_horizon,
        "selected_packages": context_packages.get("selected_by_default", []),
        "memory_visualization": model.get("memory_visualization") if isinstance(model.get("memory_visualization"), Mapping) else {},
    }
    return {
        "schema_id": "ion.codex_capsule_chat_ui_model.v1",
        "layout": {
            "mode": "joc_shell_chat_first",
            "zones": ["top_bar", "left_icon_rail", "left_drawer", "main_work_surface", "right_inspector", "right_icon_rail", "bottom_timeline"],
            "primary_surface": "main_chat",
            "default_page_id": "chat",
        },
        "top_bar": {
            "title": "ION Codex",
            "subtitle": "Chat",
            "page_tabs": [
                {"id": "chat", "label": "Chat"},
                {"id": "context", "label": "Context"},
                {"id": "runs", "label": "Runs"},
                {"id": "agents", "label": "Agents"},
                {"id": "receipts", "label": "Receipts"},
                {"id": "settings", "label": "Settings"},
            ],
            "status_chips": [
                {"label": "chat", "value": model.get("verdict"), "tone": "ready"},
                {"label": "context", "value": "Capsule" if codex_solo.get("ok") else codex_solo.get("verdict"), "tone": "ready" if codex_solo.get("ok") else "blocked"},
                {"label": "skill", "value": current_skill.get("display_name") or "none", "tone": "ready" if skills.get("ok") else "blocked"},
                {"label": "engine", "value": chat_engine.get("verdict") or "unknown", "tone": "ready" if chat_engine.get("ok") else "blocked"},
                {"label": "routes", "value": assistant_work_routes.get("route_count", 0), "tone": "ready" if assistant_work_routes.get("ok") else "watch"},
                {"label": "carrier", "value": "enabled" if chat_response_carrier.get("enabled") else "fallback", "tone": "ready" if chat_response_carrier.get("enabled") else "watch"},
                {"label": "queue", "value": runner.get("queued_request_count", 0), "tone": "watch"},
                {"label": "runner", "value": runner.get("active_process_running", False), "tone": "watch"},
                {"label": "public", "value": remote_access.get("enabled_by_model", False), "tone": "watch"},
            ],
        },
        "left_rail": [
            {"id": "composer", "label": "Composer", "icon": "chat"},
            {"id": "models", "label": "Models", "icon": "route"},
            {"id": "skills", "label": "Skills", "icon": "skills"},
            {"id": "context-lens", "label": "Context Lens", "icon": "graph"},
            {"id": "run-mode", "label": "Run Mode", "icon": "runs"},
        ],
        "left_drawer": {
            "active_panel_id": "composer",
            "panels": [
                {
                    "id": "composer",
                    "title": "Composer",
                    "summary": "Primary user-facing Codex chat composer.",
                    "items": [
                        {"label": "Default mode", "value": execution_bridge.get("default_mode")},
                        {"label": "Run mode", "value": "queue_for_codex"},
                        {"label": "Runner start", "value": execution_bridge.get("runner_start_enabled", False)},
                    ],
                },
                {
                    "id": "models",
                    "title": "Models",
                    "summary": "Current model move hints for this chat lane.",
                    "items": [
                        {"label": "Routing posture", "value": DEFAULT_ROUTING_POSTURE},
                        {"label": "Usage authority", "value": "operator_observed_hint"},
                        {"label": "Production", "value": False},
                    ],
                },
                {
                    "id": "skills",
                    "title": "Skills",
                    "summary": "Skills activate workflows; templates remain proof gates.",
                    "items": [
                        {"label": "Current", "value": current_skill.get("display_name") or "none"},
                        {"label": "Registered", "value": skills.get("skill_count", 0)},
                        {"label": "State gate", "value": current_skill.get("state_acceptance_granted", False)},
                    ],
                },
                {
                    "id": "context-lens",
                    "title": "Context Lens",
                    "summary": "Capsule is the minimum context; Mini is the lookup index.",
                    "items": [
                        {"label": "Route OK", "value": route.get("ok")},
                        {"label": "Packages", "value": context_packages.get("package_count", 0)},
                        {"label": "Missing routes", "value": len(missing_route)},
                    ],
                },
                {
                    "id": "run-mode",
                    "title": "Run Mode",
                    "summary": "State-changing work remains proof-gated through the existing Codex queue.",
                    "items": [
                        {"label": "Queued", "value": runner.get("queued_request_count", 0)},
                        {"label": "Runner active", "value": runner.get("active_process_running", False)},
                        {"label": "Live authority", "value": False},
                    ],
                },
            ],
        },
        "right_rail": [
            {"id": "assistant", "label": "Assistant", "icon": "chat"},
            {"id": "context", "label": "Context", "icon": "graph"},
            {"id": "evidence", "label": "Evidence", "icon": "receipts"},
            {"id": "system", "label": "System", "icon": "agents"},
            {"id": "settings", "label": "Settings", "icon": "settings"},
        ],
        "composer": {
            "action": "/chat/turn",
            "lane_id": "codex_general",
            "primary_mode": "auto",
            "primary_label": "Send",
            "run_mode": "queue_for_codex",
            "run_label": "Run task",
            "allowed_execution_modes": execution_bridge.get("allowed_modes", ["respond_only"]),
            "runner_start_enabled": execution_bridge.get("runner_start_enabled", False),
        },
        "conversation": {
            "summary": conversation_summary,
            "turn_groups": _chat_turn_groups(
                turns[-80:],
                return_records=hydrated_return_records,
                turn_traces=turn_trace_records,
            ),
            "empty_state": "Ask Codex.",
        },
        "pages": {
            "context": {
                "title": "Context",
                "summary": "Visual projection of Capsule, Mini, long-horizon, route, and carrier context.",
            },
            "runs": {
                "title": "Runs",
                "summary": "Read-only view of queue, response carrier, runner, and proof-return state.",
            },
            "agents": {
                "title": "Agents",
                "summary": "Read-only existing ION agent broker projection. No second agent system.",
            },
            "receipts": {
                "title": "Receipts",
                "summary": "Capsule, task-return, and proof evidence surfaces.",
            },
            "settings": {
                "title": "Settings",
                "summary": "Local execution, public access, and service posture.",
            },
        },
        "drawers": {
            "timeline": turn_trace_index,
            "skills": skills,
            "chat_engine": chat_engine,
            "assistant_work_routes": assistant_work_routes,
            "carrier": chat_response_carrier,
            "agents": agents,
            "context": context_drawer,
            "capsule": context_drawer,
            "runs": {
                "runner": runner,
                "latest_work_requests": latest_work_requests,
                "latest_task_returns": latest_task_returns,
                "return_hydration": return_hydration,
                "response_runs": response_runs,
            },
            "receipts": {
                "capsule_recent_rows": latest_capsule_rows,
                "history_path": "ION/05_context/current/codex_solo/history",
            },
            "ion": {
                "mode": ion_comms.get("mode"),
                "creates_second_queue": ion_comms.get("creates_second_queue"),
                "creates_second_agent_system": ion_comms.get("creates_second_agent_system"),
                "digest": ion_comms.get("digest"),
            },
            "settings": {
                "execution_bridge": execution_bridge,
                "response_carrier": chat_response_carrier,
                "memory_path": memory.get("codex_memory_path"),
                "remote_access": remote_access,
            },
        },
        "bottom_timeline": {
            "lanes": [
                {"id": "all", "label": "All", "count": len(activity)},
                {"id": "runner", "label": "Runner", "count": sum(1 for item in activity if item.get("kind") == "runner")},
                {"id": "work_request", "label": "Requests", "count": sum(1 for item in activity if item.get("kind") == "work_request")},
                {"id": "task_return", "label": "Returns", "count": sum(1 for item in activity if item.get("kind") == "task_return")},
            ],
            "items": activity[:8],
        },
        "activity": activity[:8],
        "production_authority": False,
        "live_execution_authority": False,
    }


def render_dual_codex_chat_html(model: Mapping[str, Any], *, base_path: str = "/chat", auth_token: str | None = None) -> str:
    return render_codex_chat_app_html(model, base_path=base_path, auth_token=auth_token)
