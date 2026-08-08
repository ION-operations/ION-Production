#!/usr/bin/python3
"""Strict health and startup control for PC-backed ION connections.

Only three compiled-in groups are accepted: Helixion, Actions, and ChatOps.
Callers cannot supply unit names, URLs, or shell text. Persistent mutations use
fixed systemd user units and emit sanitized local receipts.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

SCHEMA_ID = "ion.startup_connections_desktop_control.v2"
RECEIPT_SCHEMA_ID = "ion.startup_connections_desktop_control_receipt.v2"
PROBE_TIMEOUT_SECONDS = 2.5
ACTION_WAIT_SECONDS = 8.0
MAX_DIAGNOSTIC_CHARS = 600

COCKPIT_LOCAL_URL = "http://127.0.0.1:8765/cockpit#system"
HELIXION_LOCAL_UNIT = "ion-mcp-preview.service"
HELIXION_TUNNEL_UNIT = "ion-mcp-tunnel.service"
ACTION_LOCAL_UNIT = "ion-action-gateway.service"
ACTION_TUNNEL_UNIT = "ion-action-tunnel.service"
CHATOPS_UNIT = "ion-chatops.service"
ION_ROOT = Path("/home/sev/ION - Production/ION_Developement")
DRAIN_TIMER_UNIT = "ion-durable-sos-spawn-queue-drain.timer"
LOOP_TIMER_UNIT = "ion-autonomous-loop-local-worker.timer"
DURABLE_SPAWN_QUEUE_PATH = (
    ION_ROOT / "ION/05_context/current/domain_weaver/inter_domain_work_queue/DURABLE_SOS_DOMAIN_SPAWN_QUEUE.json"
)
LAST_DURABLE_DRAIN_TICK_PATH = (
    ION_ROOT
    / "ION/05_context/current/domain_weaver/inter_domain_work_queue/LAST_DURABLE_SOS_DRAIN_TICK.candidate.json"
)
PROMPT_SPAWN_RUNS_DIR = ION_ROOT / "ION/05_context/current/cursor_connector/prompt_spawn_runs"
WORKER_SHIFT_BOARD_PATH = ION_ROOT / "ION/05_context/current/worker_shift/ACTIVE_WORKER_SHIFT_BOARD.json"
HUMAN_GATE_QUEUE_PATH = ION_ROOT / "ION/05_context/current/ACTIVE_HUMAN_GATE_QUEUE.json"
RUNTIME_ABSENCE_SURFACE_PATH = (
    ION_ROOT / "ION/05_context/current/runtime_carrier/ION_RUNTIME_ABSENCE_SURFACE.candidate.json"
)
LAST_AUTONOMOUS_LOOP_RESULT_PATH = ION_ROOT / "ION/05_context/current/LAST_ION_AUTONOMOUS_LOOP_RESULT.json"
SCHEDULER_LAST_TICK_PATH = (
    ION_ROOT / "ION/05_context/current/autonomous_goals/scheduler/last_tick.candidate.json"
)
TIMER_ACTION_UNITS = {
    "queue": DRAIN_TIMER_UNIT,
    "loop": LOOP_TIMER_UNIT,
}


@dataclass(frozen=True)
class ProbeSpec:
    probe_id: str
    url: str
    schema_id: str
    verdict: str | None = None
    status: str | None = None
    public: bool = False


@dataclass(frozen=True)
class UnitBinding:
    unit: str
    process_key: str
    listener_port: int | None = None


@dataclass(frozen=True)
class GroupSpec:
    group_id: str
    label: str
    bindings: tuple[UnitBinding, ...]
    start_order: tuple[str, ...]
    stop_order: tuple[str, ...]
    probes: tuple[ProbeSpec, ...]
    local_probe_id: str
    public_probe_id: str | None = None
    open_url: str | None = None


GROUPS: dict[str, GroupSpec] = {
    "helixion": GroupSpec(
        group_id="helixion",
        label="Helixion",
        bindings=(
            UnitBinding(HELIXION_LOCAL_UNIT, "preview", 8765),
            UnitBinding(HELIXION_TUNNEL_UNIT, "ion_browser_tunnel"),
        ),
        start_order=(HELIXION_LOCAL_UNIT, HELIXION_TUNNEL_UNIT),
        stop_order=(HELIXION_TUNNEL_UNIT, HELIXION_LOCAL_UNIT),
        probes=(
            ProbeSpec(
                "local",
                "http://127.0.0.1:8765/health",
                "ion.chatgpt_browser_http_mcp_preview.health.v1",
                status="ready",
            ),
            ProbeSpec(
                "public",
                "https://ion.helixion.net/health",
                "ion.chatgpt_browser_http_mcp_preview.health.v1",
                status="ready",
                public=True,
            ),
        ),
        local_probe_id="local",
        public_probe_id="public",
        open_url=COCKPIT_LOCAL_URL,
    ),
    "actions": GroupSpec(
        group_id="actions",
        label="GPT Actions",
        bindings=(
            UnitBinding(ACTION_LOCAL_UNIT, "action_gateway", 8777),
            UnitBinding(ACTION_TUNNEL_UNIT, "ion_actions_tunnel"),
        ),
        start_order=(ACTION_LOCAL_UNIT, ACTION_TUNNEL_UNIT),
        stop_order=(ACTION_TUNNEL_UNIT, ACTION_LOCAL_UNIT),
        probes=(
            ProbeSpec(
                "local",
                "http://127.0.0.1:8777/health",
                "ion.custom_gpt_action_gateway_health.v1",
                verdict="ION_CUSTOM_GPT_ACTION_GATEWAY_READY",
            ),
            ProbeSpec(
                "public",
                "https://ion-actions.helixion.net/health",
                "ion.custom_gpt_action_gateway_health.v1",
                verdict="ION_CUSTOM_GPT_ACTION_GATEWAY_READY",
                public=True,
            ),
        ),
        local_probe_id="local",
        public_probe_id="public",
        open_url="https://ion-actions.helixion.net/health",
    ),
    "chatops": GroupSpec(
        group_id="chatops",
        label="ChatOps",
        bindings=(UnitBinding(CHATOPS_UNIT, "chatops", 8767),),
        start_order=(CHATOPS_UNIT,),
        stop_order=(CHATOPS_UNIT,),
        probes=(
            ProbeSpec(
                "local",
                "http://127.0.0.1:8767/health",
                "ion.chatops_bridge.v1",
                verdict="ION_CHATOPS_BRIDGE_READY",
            ),
        ),
        local_probe_id="local",
    ),
}

ALLOWED_UNITS = {
    binding.unit
    for group in GROUPS.values()
    for binding in group.bindings
} | {DRAIN_TIMER_UNIT, LOOP_TIMER_UNIT}
ALLOWED_PORTS = {8765, 8767, 8777}
EXPECTED_TUNNEL_ORIGIN_KEYS = {
    "ion_browser_tunnel": "ion_browser_expected_origin",
    "ion_actions_tunnel": "ion_actions_expected_origin",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _bounded(value: str | None) -> str:
    return (value or "").strip().replace("\x00", "")[:MAX_DIAGNOSTIC_CHARS]


def _read_json_file(path: Path) -> tuple[dict[str, Any] | list[Any] | None, str | None]:
    try:
        raw = path.read_text(encoding="utf-8")
        return json.loads(raw), None
    except FileNotFoundError:
        return None, "file_not_found"
    except (OSError, json.JSONDecodeError, UnicodeError) as exc:
        return None, _bounded(exc.__class__.__name__)


def _queue_rows_from_payload(payload: dict[str, Any] | list[Any] | None) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        rows = payload.get("rows")
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def _count_queue_statuses(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"pending_count": 0, "executed_count": 0, "quarantined_count": 0}
    for row in rows:
        status = row.get("status")
        if status == "pending":
            counts["pending_count"] += 1
        elif status == "executed":
            counts["executed_count"] += 1
        elif status == "quarantined":
            counts["quarantined_count"] += 1
    return counts


def _timer_summary(unit: str) -> dict[str, Any]:
    status = _unit_status(unit)
    return {
        "unit": unit,
        "active": bool(status.get("active")),
        "enabled": bool(status.get("enabled")),
    }


def _build_queue_section() -> dict[str, Any]:
    section: dict[str, Any] = {}
    payload, error = _read_json_file(DURABLE_SPAWN_QUEUE_PATH)
    if error:
        section["error"] = error
    else:
        section.update(_count_queue_statuses(_queue_rows_from_payload(payload)))

    tick_payload, tick_error = _read_json_file(LAST_DURABLE_DRAIN_TICK_PATH)
    if tick_error:
        section["last_drain_error"] = tick_error
    elif isinstance(tick_payload, dict):
        section["last_drain_verdict"] = _bounded(
            tick_payload.get("verdict") if isinstance(tick_payload.get("verdict"), str) else None
        )
        section["last_drain_at"] = _bounded(
            tick_payload.get("tick_at") if isinstance(tick_payload.get("tick_at"), str) else None
        )
        alerts = tick_payload.get("absence_alerts")
        section["absence_alerts"] = alerts if isinstance(alerts, list) else []

    try:
        section["drain_timer"] = _timer_summary(DRAIN_TIMER_UNIT)
        section["loop_timer"] = _timer_summary(LOOP_TIMER_UNIT)
    except ValueError as exc:
        section["timer_error"] = _bounded(str(exc))

    return section


def _spawn_run_started_at(run_dir_name: str) -> str:
    match = re.search(r"prompt_spawn_(\d{4}-\d{2}-\d{2}T\d{6}\+\d{4})", run_dir_name)
    if not match:
        return _bounded(run_dir_name)
    return _bounded(match.group(1))


def _scan_prompt_spawn_runs() -> dict[str, Any]:
    section: dict[str, Any] = {"in_flight_count": 0, "recent_runs": []}
    if not PROMPT_SPAWN_RUNS_DIR.is_dir():
        section["error"] = "runs_dir_missing"
        return section
    try:
        names = sorted(
            (entry.name for entry in PROMPT_SPAWN_RUNS_DIR.iterdir() if entry.is_dir()),
            reverse=True,
        )
    except OSError as exc:
        section["error"] = _bounded(exc.__class__.__name__)
        return section

    examined: list[dict[str, Any]] = []
    in_flight = 0
    for name in names[:8]:
        run_dir = PROMPT_SPAWN_RUNS_DIR / name
        admission_path = run_dir / "spawn_admission.json"
        task_return_path = run_dir / "task_return.json"
        has_admission = admission_path.is_file()
        has_return = task_return_path.is_file()
        if has_admission and not has_return:
            in_flight += 1
        finished = has_return
        domain_id = ""
        work_class = ""
        if has_admission:
            admission, admission_error = _read_json_file(admission_path)
            if admission_error:
                domain_id = admission_error
            elif isinstance(admission, dict):
                domain_id = _bounded(
                    admission.get("domain_id") if isinstance(admission.get("domain_id"), str) else None
                )
                work_class = _bounded(
                    admission.get("work_class") if isinstance(admission.get("work_class"), str) else None
                )
        examined.append(
            {
                "run_id": _bounded(name),
                "domain_id": domain_id,
                "work_class": work_class,
                "finished": finished,
                "started_at": _spawn_run_started_at(name),
            }
        )
    section["in_flight_count"] = in_flight
    section["recent_runs"] = examined[:5]
    return section


def _count_carrier_processes() -> dict[str, int]:
    counts = {"cursor_agent": 0, "claude": 0, "codex": 0}
    token_map = {"cursor-agent": "cursor_agent", "claude": "claude", "codex": "codex"}
    try:
        entries: Iterable[Path] = Path("/proc").iterdir()
    except OSError:
        return counts
    for entry in entries:
        if not entry.name.isdigit():
            continue
        try:
            tokens = [
                token.decode("utf-8", errors="replace")
                for token in (entry / "cmdline").read_bytes().split(b"\x00")
                if token
            ]
        except (OSError, PermissionError):
            continue
        if not tokens:
            continue
        matched = {field for token in tokens if (field := token_map.get(token))}
        for field in matched:
            counts[field] += 1
    return counts


def _summarize_worker_shift() -> dict[str, Any]:
    payload, error = _read_json_file(WORKER_SHIFT_BOARD_PATH)
    if error:
        return {"error": error}
    if not isinstance(payload, dict):
        return {"error": "unexpected_shape"}
    leases = payload.get("active_leases")
    lease_count = len(leases) if isinstance(leases, list) else 0
    heartbeats = payload.get("heartbeats")
    heartbeat_count = len(heartbeats) if isinstance(heartbeats, list) else 0
    return {
        "active_lease_count": lease_count,
        "heartbeat_count": heartbeat_count,
    }


def _build_agents_section() -> dict[str, Any]:
    agents = _scan_prompt_spawn_runs()
    agents["worker_shift"] = _summarize_worker_shift()
    agents["carrier_processes"] = _count_carrier_processes()
    return agents


def _walk_absence_check_nodes(node: Any, flagged: list[int], total: list[int]) -> None:
    if isinstance(node, dict):
        if "check_id" in node and "status" in node:
            total[0] += 1
            if node.get("status") not in {"ok", "clear"}:
                flagged[0] += 1
        for value in node.values():
            _walk_absence_check_nodes(value, flagged, total)
    elif isinstance(node, list):
        for item in node:
            _walk_absence_check_nodes(item, flagged, total)


def _summarize_absence_surface() -> dict[str, Any]:
    payload, error = _read_json_file(RUNTIME_ABSENCE_SURFACE_PATH)
    if error:
        return {"error": error}
    if not isinstance(payload, dict):
        return {"error": "unexpected_shape"}
    flagged = [0]
    total = [0]
    _walk_absence_check_nodes(payload.get("checks"), flagged, total)
    _walk_absence_check_nodes(payload.get("surface"), flagged, total)
    return {
        "absence_verdict": _bounded(payload.get("verdict") if isinstance(payload.get("verdict"), str) else None),
        "absence_findings_count": flagged[0],
        "checks_total": total[0],
        "checks_flagged": flagged[0],
    }


def _build_attention_section() -> dict[str, Any]:
    attention: dict[str, Any] = {}
    gate_payload, gate_error = _read_json_file(HUMAN_GATE_QUEUE_PATH)
    if gate_error:
        attention["human_gate_error"] = gate_error
    elif isinstance(gate_payload, dict):
        gates = gate_payload.get("gates")
        attention["open_gate_count"] = len(gates) if isinstance(gates, list) else 0
        non_blocking = gate_payload.get("non_blocking")
        attention["non_blocking"] = non_blocking if isinstance(non_blocking, bool) else None

    attention.update(_summarize_absence_surface())

    loop_payload, loop_error = _read_json_file(LAST_AUTONOMOUS_LOOP_RESULT_PATH)
    if loop_error:
        attention["loop_error"] = loop_error
    elif isinstance(loop_payload, dict):
        attention["loop_status"] = _bounded(
            loop_payload.get("status") if isinstance(loop_payload.get("status"), str) else None
        )
        stop_reason = loop_payload.get("stop_reason")
        if isinstance(stop_reason, str):
            attention["loop_stop_reason"] = _bounded(stop_reason)
        attention["loop_at"] = _bounded(
            loop_payload.get("created_at") if isinstance(loop_payload.get("created_at"), str) else None
        )

    tick_payload, tick_error = _read_json_file(SCHEDULER_LAST_TICK_PATH)
    if tick_error:
        attention["wakeup_error"] = tick_error
    elif isinstance(tick_payload, dict):
        gate = tick_payload.get("activation_gate")
        scheduler = tick_payload.get("scheduler_status")
        verdict = None
        evaluated_at = None
        if isinstance(gate, dict):
            if isinstance(gate.get("verdict"), str):
                verdict = gate.get("verdict")
            if isinstance(gate.get("evaluated_at"), str):
                evaluated_at = gate.get("evaluated_at")
        if verdict is None and isinstance(scheduler, dict) and isinstance(scheduler.get("verdict"), str):
            verdict = scheduler.get("verdict")
        if evaluated_at is None and isinstance(scheduler, dict) and isinstance(scheduler.get("last_tick_at"), str):
            evaluated_at = scheduler.get("last_tick_at")
        if evaluated_at is None and isinstance(tick_payload.get("created_at"), str):
            evaluated_at = tick_payload.get("created_at")
        attention["wakeup_verdict"] = _bounded(verdict if isinstance(verdict, str) else None)
        attention["wakeup_at"] = _bounded(evaluated_at if isinstance(evaluated_at, str) else None)

    return attention


def _run(argv: list[str], *, timeout: float = 15.0) -> dict[str, Any]:
    """Run fixed argv without a shell and return bounded diagnostics."""
    try:
        completed = subprocess.run(
            argv,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except Exception as exc:
        return {
            "ok": False,
            "returncode": None,
            "finding": exc.__class__.__name__,
            "diagnostic": "",
        }
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "finding": "ok" if completed.returncode == 0 else "command_failed",
        "diagnostic": _bounded(completed.stderr or completed.stdout),
    }


def _parse_properties(text: str) -> dict[str, str]:
    properties: dict[str, str] = {}
    for line in text.splitlines():
        key, separator, value = line.partition("=")
        if separator:
            properties[key] = value
    return properties


def _unit_status(unit: str) -> dict[str, Any]:
    if unit not in ALLOWED_UNITS:
        raise ValueError("unit_not_allowed")
    try:
        completed = subprocess.run(
            [
                "systemctl",
                "--user",
                "show",
                unit,
                "--property=Id,LoadState,ActiveState,SubState,UnitFileState,MainPID,NRestarts",
                "--no-pager",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=5.0,
        )
    except Exception as exc:
        return {
            "unit": unit,
            "available": False,
            "identity_ok": False,
            "active": False,
            "enabled": False,
            "load_state": "unknown",
            "active_state": "unknown",
            "sub_state": "unknown",
            "unit_file_state": "unknown",
            "main_pid": 0,
            "restart_count": 0,
            "finding": exc.__class__.__name__,
        }
    values = _parse_properties(completed.stdout or "")
    identity_ok = values.get("Id") == unit
    unit_file_state = values.get("UnitFileState", "unknown")
    # This panel promises persistence at the next login. Only a persistent
    # systemctl enable state satisfies that claim.
    enabled = unit_file_state == "enabled"
    try:
        main_pid = int(values.get("MainPID", "0") or 0)
    except ValueError:
        main_pid = 0
    try:
        restart_count = int(values.get("NRestarts", "0") or 0)
    except ValueError:
        restart_count = 0
    available = completed.returncode == 0 and values.get("LoadState") == "loaded"
    return {
        "unit": unit,
        "available": available,
        "identity_ok": identity_ok,
        "active": values.get("ActiveState") == "active" and values.get("SubState") == "running",
        "enabled": enabled,
        "load_state": values.get("LoadState", "unknown"),
        "active_state": values.get("ActiveState", "unknown"),
        "sub_state": values.get("SubState", "unknown"),
        "unit_file_state": unit_file_state,
        "main_pid": main_pid,
        "restart_count": restart_count,
        "finding": "ok" if available and identity_ok else "unit_identity_unavailable",
    }


def _health_payload_ready(payload: dict[str, Any], spec: ProbeSpec, status_code: int) -> bool:
    return bool(
        200 <= status_code < 300
        and payload.get("schema_id") == spec.schema_id
        and payload.get("ok") is True
        and (spec.verdict is None or payload.get("verdict") == spec.verdict)
        and (spec.status is None or payload.get("status") == spec.status)
    )


def _probe(spec: ProbeSpec, *, timeout: float = PROBE_TIMEOUT_SECONDS) -> dict[str, Any]:
    started = time.monotonic()
    try:
        request = urllib.request.Request(
            spec.url,
            headers={"Accept": "application/json", "User-Agent": "ION-Startup-Connections/2"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status_code = int(getattr(response, "status", 0) or 0)
            raw = response.read(8192)
        try:
            payload = json.loads(raw.decode("utf-8", errors="replace"))
        except (json.JSONDecodeError, UnicodeError):
            payload = {}
        schema_ok = payload.get("schema_id") == spec.schema_id
        verdict_ok = spec.verdict is None or payload.get("verdict") == spec.verdict
        status_ok = spec.status is None or payload.get("status") == spec.status
        ready = _health_payload_ready(payload, spec, status_code)
        return {
            "ready": ready,
            "http_status": status_code,
            "schema_ok": schema_ok,
            "verdict_ok": verdict_ok,
            "status_ok": status_ok,
            "reported_status": payload.get("status") if isinstance(payload.get("status"), str) else None,
            "latency_ms": round((time.monotonic() - started) * 1000),
            "finding": "ready" if ready else "unexpected_health_response",
        }
    except urllib.error.HTTPError as exc:
        return {
            "ready": False,
            "http_status": int(exc.code),
            "schema_ok": False,
            "verdict_ok": False,
            "status_ok": False,
            "reported_status": None,
            "latency_ms": round((time.monotonic() - started) * 1000),
            "finding": "http_error",
        }
    except Exception as exc:
        return {
            "ready": False,
            "http_status": None,
            "schema_ok": False,
            "verdict_ok": False,
            "status_ok": False,
            "reported_status": None,
            "latency_ms": round((time.monotonic() - started) * 1000),
            "finding": exc.__class__.__name__,
        }


def _read_process_inventory() -> dict[str, list[int]]:
    inventory: dict[str, list[int]] = {
        "preview": [],
        "action_gateway": [],
        "chatops": [],
        "ion_browser_tunnel": [],
        "ion_actions_tunnel": [],
        "ion_browser_expected_origin": [],
        "ion_actions_expected_origin": [],
        "cloudflared_tunnels": [],
    }
    try:
        entries: Iterable[Path] = Path("/proc").iterdir()
    except OSError:
        return inventory
    for entry in entries:
        if not entry.name.isdigit():
            continue
        try:
            tokens = [
                token.decode("utf-8", errors="replace")
                for token in (entry / "cmdline").read_bytes().split(b"\x00")
                if token
            ]
        except (OSError, PermissionError):
            continue
        if not tokens:
            continue
        _record_process(inventory, int(entry.name), tokens)
    for pids in inventory.values():
        pids.sort()
    return inventory


def _record_process(inventory: dict[str, list[int]], pid: int, tokens: list[str]) -> None:
    def has_flag(flag: str, value: str) -> bool:
        return any(
            token == flag and index + 1 < len(tokens) and tokens[index + 1] == value
            for index, token in enumerate(tokens)
        )

    if "kernel.ion_chatgpt_browser_mcp_http_preview" in tokens and has_flag("--port", "8765"):
        inventory["preview"].append(pid)
    if "kernel.ion_custom_gpt_action_gateway" in tokens and has_flag("--port", "8777"):
        inventory["action_gateway"].append(pid)
    if "kernel.ion_chatops_bridge" in tokens and has_flag("--port", "8767"):
        inventory["chatops"].append(pid)
    if Path(tokens[0]).name == "cloudflared" and "tunnel" in tokens and "run" in tokens:
        inventory["cloudflared_tunnels"].append(pid)
        if "ion-browser" in tokens:
            inventory["ion_browser_tunnel"].append(pid)
            if "http://127.0.0.1:8765" in tokens:
                inventory["ion_browser_expected_origin"].append(pid)
        if "ion-actions" in tokens:
            inventory["ion_actions_tunnel"].append(pid)
            if "http://127.0.0.1:8777" in tokens:
                inventory["ion_actions_expected_origin"].append(pid)


def _listener_status(port: int) -> dict[str, Any]:
    if port not in ALLOWED_PORTS:
        raise ValueError("port_not_allowed")
    try:
        completed = subprocess.run(
            ["ss", "-H", "-ltnp", "sport", "=", f":{port}"],
            check=False,
            capture_output=True,
            text=True,
            timeout=3.0,
        )
    except Exception as exc:
        return {"port": port, "listening": False, "owner_pids": [], "finding": exc.__class__.__name__}
    lines = [line for line in (completed.stdout or "").splitlines() if line.strip()]
    owner_pids = sorted({int(value) for value in re.findall(r"pid=(\d+)", "\n".join(lines))})
    loopback_only = bool(lines) and all(f"127.0.0.1:{port}" in line for line in lines)
    return {
        "port": port,
        "listening": bool(lines),
        "loopback_only": loopback_only,
        "owner_pids": owner_pids,
        "finding": "ok" if completed.returncode == 0 else "listener_query_failed",
    }


def _classify_group(
    spec: GroupSpec,
    units: dict[str, dict[str, Any]],
    probes: dict[str, dict[str, Any]],
    inventory: dict[str, list[int]],
    listeners: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    conflicts: list[str] = []
    findings: list[str] = []
    group_units = {binding.unit: units[binding.unit] for binding in spec.bindings}
    instance_rows: dict[str, dict[str, Any]] = {}

    for binding in spec.bindings:
        unit = units[binding.unit]
        pids = inventory.get(binding.process_key, [])
        instance_rows[binding.process_key] = {"count": len(pids), "pids": pids}
        if not unit.get("available"):
            conflicts.append(f"{binding.process_key}_unit_unavailable")
        elif not unit.get("identity_ok"):
            conflicts.append(f"{binding.process_key}_unit_identity_mismatch")
        if len(pids) > 1:
            conflicts.append(f"duplicate_{binding.process_key}_process")
        if unit.get("active") and unit.get("main_pid") not in pids:
            conflicts.append(f"{binding.process_key}_main_pid_mismatch")
        expected_origin_key = EXPECTED_TUNNEL_ORIGIN_KEYS.get(binding.process_key)
        if (
            expected_origin_key
            and unit.get("active")
            and unit.get("main_pid") not in inventory.get(expected_origin_key, [])
        ):
            conflicts.append(f"{binding.process_key}_origin_mismatch")
        if not unit.get("active") and pids:
            conflicts.append(f"orphan_{binding.process_key}_process")
        if binding.listener_port is not None:
            listener = listeners[binding.listener_port]
            if listener.get("finding") != "ok":
                findings.append(f"listener_{binding.listener_port}_inspection_failed")
            elif unit.get("active") and not listener.get("listening"):
                findings.append(f"listener_{binding.listener_port}_missing")
            if listener.get("listening") and not listener.get("loopback_only"):
                conflicts.append(f"non_loopback_{binding.listener_port}_listener")
            if listener.get("listening") and unit.get("main_pid") not in listener.get("owner_pids", []):
                conflicts.append(f"unmanaged_{binding.listener_port}_listener")

    all_active = all(unit.get("active") for unit in group_units.values())
    all_enabled = all(unit.get("enabled") for unit in group_units.values())
    any_enabled = any(unit.get("enabled") for unit in group_units.values())
    startup_state = "enabled" if all_enabled else ("partial" if any_enabled else "disabled")
    exact_instances = all(row["count"] == 1 for row in instance_rows.values())
    listeners_present = any(
        listeners[binding.listener_port].get("listening")
        for binding in spec.bindings
        if binding.listener_port is not None
    )
    fully_quiet = not any(
        [
            any(unit.get("active") for unit in group_units.values()),
            any(unit.get("enabled") for unit in group_units.values()),
            any(row["count"] for row in instance_rows.values()),
            listeners_present,
        ]
    )
    if spec.public_probe_id and probes[spec.public_probe_id].get("ready"):
        tunnel_active = units[spec.start_order[-1]].get("active")
        if not tunnel_active:
            conflicts.append("public_endpoint_live_while_tunnel_inactive")

    probes_ready = all(probes[probe.probe_id].get("ready") for probe in spec.probes)
    if conflicts:
        overall = "conflict"
        summary = f"{spec.label} has conflicting state"
    elif findings:
        overall = "degraded"
        summary = f"{spec.label} health could not be fully verified"
    elif fully_quiet:
        overall = "off"
        summary = f"{spec.label} is off"
    elif all_active and all_enabled and exact_instances and probes_ready:
        overall = "healthy"
        summary = f"{spec.label} is healthy"
    else:
        overall = "degraded"
        summary = f"{spec.label} is partially running or degraded"

    return {
        "group_id": spec.group_id,
        "label": spec.label,
        "overall": overall,
        "summary": summary,
        "running": all_active,
        "startup_enabled": all_enabled,
        "startup_state": startup_state,
        "toggle_on": not fully_quiet,
        "controllable": all(
            unit.get("available") and unit.get("identity_ok")
            for unit in group_units.values()
        ),
        "conflicts": conflicts,
        "findings": findings,
        "services": group_units,
        "probes": probes,
        "instances": instance_rows,
        "listeners": {
            str(binding.listener_port): listeners[binding.listener_port]
            for binding in spec.bindings
            if binding.listener_port is not None
        },
        "scope": list(spec.start_order),
        "open_url": spec.open_url,
    }


def _classify_global(groups: dict[str, dict[str, Any]]) -> dict[str, Any]:
    group_count = len(groups)
    on_count = sum(1 for group in groups.values() if group.get("toggle_on"))
    conflicts = [
        f"{group_id}:{finding}"
        for group_id, group in groups.items()
        for finding in group.get("conflicts", [])
    ]
    if conflicts:
        overall = "conflict"
        summary = f"ION connection conflict · {on_count}/{group_count} on"
    elif any(group.get("overall") == "degraded" for group in groups.values()):
        overall = "degraded"
        summary = f"ION connections need attention · {on_count}/{group_count} on"
    elif on_count == 0:
        overall = "off"
        summary = "All PC-backed ION connections are off"
    else:
        overall = "healthy"
        summary = f"Enabled ION connections are healthy · {on_count}/{group_count} on"
    return {
        "overall": overall,
        "summary": summary,
        "group_count": group_count,
        "on_group_count": on_count,
        "startup_enabled_group_count": sum(
            1 for group in groups.values() if group.get("startup_state") == "enabled"
        ),
        "healthy_group_count": sum(1 for group in groups.values() if group.get("overall") == "healthy"),
        "off_group_count": sum(1 for group in groups.values() if group.get("overall") == "off"),
        "conflicts": conflicts,
    }


def build_status() -> dict[str, Any]:
    units = {unit: _unit_status(unit) for unit in sorted(ALLOWED_UNITS)}
    inventory = _read_process_inventory()
    listener_ports = sorted(
        binding.listener_port
        for group in GROUPS.values()
        for binding in group.bindings
        if binding.listener_port is not None
    )
    listeners = {port: _listener_status(port) for port in listener_ports}
    probe_specs = {
        (group.group_id, probe.probe_id): probe
        for group in GROUPS.values()
        for probe in group.probes
    }
    probe_results: dict[tuple[str, str], dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(probe_specs)) as executor:
        futures = {
            executor.submit(_probe, probe, timeout=PROBE_TIMEOUT_SECONDS): key
            for key, probe in probe_specs.items()
        }
        for future in concurrent.futures.as_completed(futures):
            key = futures[future]
            probe_results[key] = future.result()

    groups: dict[str, dict[str, Any]] = {}
    for group_id, spec in GROUPS.items():
        group_probes = {
            probe.probe_id: probe_results[(group_id, probe.probe_id)]
            for probe in spec.probes
        }
        groups[group_id] = _classify_group(spec, units, group_probes, inventory, listeners)

    global_status = _classify_global(groups)
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _utc_now(),
        **global_status,
        "groups": groups,
        "queue": _build_queue_section(),
        "agents": _build_agents_section(),
        "attention": _build_attention_section(),
        "instances": {
            "local_process_count": sum(len(inventory[key]) for key in ("preview", "action_gateway", "chatops")),
            "cloudflared_tunnel_count": len(inventory["cloudflared_tunnels"]),
        },
        "scope": sorted(ALLOWED_UNITS),
        "production_authority": False,
        "accepted_state_claim": False,
    }


def _wait_until(predicate: Callable[[], bool], *, timeout: float = ACTION_WAIT_SECONDS) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.35)
    return predicate()


def _systemctl(action: str, unit: str) -> dict[str, Any]:
    if action not in {"enable_now", "disable_now"} or unit not in ALLOWED_UNITS:
        raise ValueError("control_not_allowed")
    verb = "enable" if action == "enable_now" else "disable"
    return _run(["systemctl", "--user", verb, "--now", unit], timeout=30.0)


def _write_receipt(
    group_id: str,
    requested_state: str,
    before: dict[str, Any],
    after: dict[str, Any],
    result: dict[str, Any],
) -> str:
    state_home = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state"))
    receipt_dir = state_home / "ion-helixion-control" / "receipts"
    receipt_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    receipt_path = receipt_dir / f"{stamp}_{group_id}_{requested_state}.json"
    if group_id in GROUPS:
        scope = list(GROUPS[group_id].start_order)
    elif group_id in TIMER_ACTION_UNITS:
        scope = [TIMER_ACTION_UNITS[group_id]]
    else:
        scope = []
    payload = {
        "schema_id": RECEIPT_SCHEMA_ID,
        "created_at": _utc_now(),
        "group_id": group_id,
        "requested_state": requested_state,
        "before": before,
        "after": after,
        "result": result,
        "scope": scope,
        "production_authority": False,
        "accepted_state_claim": False,
    }
    receipt_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipt_path.chmod(0o600)
    return str(receipt_path)


def _probe_by_id(spec: GroupSpec, probe_id: str, *, timeout: float) -> dict[str, Any]:
    probe = next(probe for probe in spec.probes if probe.probe_id == probe_id)
    return _probe(probe, timeout=timeout)


def _binding_runtime_ready(binding: UnitBinding) -> bool:
    unit = _unit_status(binding.unit)
    inventory = _read_process_inventory()
    pids = inventory.get(binding.process_key, [])
    if not (
        unit.get("available")
        and unit.get("identity_ok")
        and unit.get("active")
        and len(pids) == 1
        and unit.get("main_pid") in pids
    ):
        return False
    expected_origin_key = EXPECTED_TUNNEL_ORIGIN_KEYS.get(binding.process_key)
    if expected_origin_key and unit.get("main_pid") not in inventory.get(expected_origin_key, []):
        return False
    if binding.listener_port is not None:
        listener = _listener_status(binding.listener_port)
        if not (
            listener.get("finding") == "ok"
            and listener.get("listening")
            and listener.get("loopback_only")
            and unit.get("main_pid") in listener.get("owner_pids", [])
        ):
            return False
    return True


def _local_origin_ready(spec: GroupSpec) -> bool:
    return bool(
        _binding_runtime_ready(spec.bindings[0])
        and _probe_by_id(spec, spec.local_probe_id, timeout=0.7).get("ready", False)
    )


def apply_action(group_id: str, requested_state: str) -> dict[str, Any]:
    if group_id not in GROUPS or requested_state not in {"on", "off"}:
        raise ValueError("action_not_allowed")
    spec = GROUPS[group_id]
    before = build_status()
    steps: list[dict[str, Any]] = []

    if requested_state == "on":
        for index, unit in enumerate(spec.start_order):
            step = _systemctl("enable_now", unit)
            steps.append({"step": f"enable_start_{unit}", **step})
            if not step["ok"]:
                break
            binding = next(binding for binding in spec.bindings if binding.unit == unit)
            runtime_ready = _wait_until(
                lambda: _local_origin_ready(spec) if index == 0 else _binding_runtime_ready(binding)
            )
            if not runtime_ready:
                steps.append(
                    {
                        "step": "verify_managed_runtime",
                        "ok": False,
                        "returncode": None,
                        "finding": "managed_runtime_not_ready",
                        "diagnostic": "",
                    }
                )
                break
        if all(step.get("ok") for step in steps) and spec.public_probe_id:
            _wait_until(
                lambda: _probe_by_id(spec, spec.public_probe_id or "", timeout=0.9).get("ready", False)
            )
    else:
        for unit in spec.stop_order:
            step = _systemctl("disable_now", unit)
            steps.append({"step": f"stop_disable_{unit}", **step})
        _wait_until(
            lambda: all(not _unit_status(unit).get("active", False) for unit in spec.stop_order)
        )

    after = build_status()
    group_after = after["groups"][group_id]
    command_ok = all(step.get("ok") for step in steps)
    reached = (
        group_after.get("running") and group_after.get("startup_enabled")
        if requested_state == "on"
        else not group_after.get("toggle_on")
    )
    result = {
        "ok": bool(command_ok and reached),
        "health_ok": group_after.get("overall") == ("healthy" if requested_state == "on" else "off"),
        "group_id": group_id,
        "requested_state": requested_state,
        "finding": "requested_state_reached" if command_ok and reached else "requested_state_not_reached",
        "steps": steps,
    }
    receipt_path = _write_receipt(group_id, requested_state, before, after, result)
    return {
        "schema_id": SCHEMA_ID,
        "ok": result["ok"],
        "group_id": group_id,
        "requested_state": requested_state,
        "finding": result["finding"],
        "health_ok": result["health_ok"],
        "status": after,
        "receipt_path": receipt_path,
    }


def apply_timer_action(kind: str, requested_state: str) -> dict[str, Any]:
    if kind not in TIMER_ACTION_UNITS or requested_state not in {"on", "off"}:
        raise ValueError("action_not_allowed")
    unit = TIMER_ACTION_UNITS[kind]
    before = build_status()
    step = _systemctl("enable_now" if requested_state == "on" else "disable_now", unit)
    after = build_status()
    timer_key = "drain_timer" if kind == "queue" else "loop_timer"
    timer_after = after.get("queue", {}).get(timer_key, {})
    reached = bool(timer_after.get("enabled")) == (requested_state == "on")
    result = {
        "ok": bool(step.get("ok") and reached),
        "health_ok": reached,
        "group_id": kind,
        "requested_state": requested_state,
        "finding": "requested_state_reached" if step.get("ok") and reached else "requested_state_not_reached",
        "steps": [{"step": f"{'enable' if requested_state == 'on' else 'disable'}_{unit}", **step}],
    }
    receipt_path = _write_receipt(kind, requested_state, before, after, result)
    return {
        "schema_id": SCHEMA_ID,
        "ok": result["ok"],
        "group_id": kind,
        "requested_state": requested_state,
        "finding": result["finding"],
        "health_ok": result["health_ok"],
        "status": after,
        "receipt_path": receipt_path,
    }


def open_latest_run_view() -> dict[str, Any]:
    if not PROMPT_SPAWN_RUNS_DIR.is_dir():
        return {"ok": False, "reason": "runs_dir_missing"}
    try:
        names = sorted(
            (entry.name for entry in PROMPT_SPAWN_RUNS_DIR.iterdir() if entry.is_dir()),
            reverse=True,
        )
    except OSError as exc:
        return {"ok": False, "reason": _bounded(exc.__class__.__name__)}

    chosen: Path | None = None
    for name in names:
        candidate = PROMPT_SPAWN_RUNS_DIR / name
        if (candidate / "output.md").is_file():
            chosen = candidate
            break
    if chosen is None and names:
        chosen = PROMPT_SPAWN_RUNS_DIR / names[0]
    if chosen is None:
        return {"ok": False, "reason": "no_runs"}

    output_path = chosen / "output.md"
    if not output_path.is_file():
        return {"ok": False, "reason": "no_output_md", "run_id": _bounded(chosen.name)}

    path_str = str(output_path)
    viewer: str | None = None
    argv: list[str] | None = None
    if shutil.which("gnome-terminal"):
        viewer = "gnome-terminal"
        argv = ["gnome-terminal", "--", "tail", "-n", "200", "-f", path_str]
    elif shutil.which("x-terminal-emulator"):
        viewer = "x-terminal-emulator"
        argv = ["x-terminal-emulator", "-e", "tail", "-n", "200", "-f", path_str]
    else:
        return {"ok": False, "reason": "no_terminal_emulator"}

    subprocess.Popen(
        argv,
        start_new_session=True,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return {"ok": True, "run_id": _bounded(chosen.name), "viewer": viewer}


def _parse_action(action: str) -> tuple[str, ...] | None:
    if action == "status":
        return None
    if action == "open-latest-run-view":
        return ("open_latest_run_view",)
    if action in {"on", "off"}:
        return ("group", "helixion", action)
    for kind in TIMER_ACTION_UNITS:
        for state in ("on", "off"):
            if action == f"{kind}-{state}":
                return ("timer", kind, state)
    group_id, separator, requested_state = action.rpartition("-")
    if separator and group_id in GROUPS and requested_state in {"on", "off"}:
        return ("group", group_id, requested_state)
    raise ValueError("action_not_allowed")


def main(argv: list[str] | None = None) -> int:
    choices = ["status", "on", "off", "open-latest-run-view"] + [
        f"{group_id}-{state}"
        for group_id in GROUPS
        for state in ("on", "off")
    ] + [f"{kind}-{state}" for kind in TIMER_ACTION_UNITS for state in ("on", "off")]
    parser = argparse.ArgumentParser(description="ION startup connection health and fixed group control")
    parser.add_argument("action", choices=choices, nargs="?", default="status")
    args = parser.parse_args(argv)
    parsed = _parse_action(args.action)
    if parsed is None:
        payload: dict[str, Any] = build_status()
    elif parsed[0] == "group":
        payload = apply_action(parsed[1], parsed[2])
    elif parsed[0] == "timer":
        payload = apply_timer_action(parsed[1], parsed[2])
    else:
        payload = open_latest_run_view()
    print(json.dumps(payload, separators=(",", ":"), sort_keys=True))
    return 0 if payload.get("ok", True) is not False else 1


if __name__ == "__main__":
    raise SystemExit(main())
