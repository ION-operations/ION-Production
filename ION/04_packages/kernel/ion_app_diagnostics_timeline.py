"""Mode-controlled app diagnostics event timeline for Helixion previews.

This is a local candidate diagnostics surface. It can intentionally add
overhead when enabled, but defaults to off and keeps every event authority-bound.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping


CURRENT = Path("ION/05_context/current")
DIAGNOSTICS_ROOT = CURRENT / "project_launcher" / "app_diagnostics"
CONFIG_PATH = DIAGNOSTICS_ROOT / "APP_DIAGNOSTICS_CONFIG.json"
EVENTS_DIR = DIAGNOSTICS_ROOT / "events"
RECEIPTS_DIR = DIAGNOSTICS_ROOT / "receipts"
SNAPSHOTS_DIR = DIAGNOSTICS_ROOT / "snapshots"
APP_DIAGNOSTICS_CONFIRMATION = "ION_APP_DIAGNOSTICS_CONFIG_CONFIRMED"
APP_DIAGNOSTICS_SNAPSHOT_CONFIRMATION = "ION_APP_DIAGNOSTICS_SNAPSHOT_CONFIRMED"
PROJECT_LOCAL_LAUNCH_CONFIRMATION = "ION_PROJECT_LOCAL_LAUNCH_CONFIRMED"
SCHEMA_ID = "ion.app_diagnostics_timeline.v1"
EVENT_SCHEMA_ID = "ion.helixion_diagnostics_event.v1"
LEGACY_EVENT_SCHEMA_ID = "ion.app_diagnostics_event.v1"

LANE_REGISTRY: dict[str, dict[str, Any]] = {
    "control": {"label": "Capture control", "order": 10, "description": "Mode, policy, receipts, and launch lifecycle."},
    "browser": {"label": "Browser runtime", "order": 20, "description": "Console, errors, lifecycle, and probe events."},
    "performance": {"label": "Performance", "order": 30, "description": "Web Vitals, timing entries, long tasks, and frame pacing."},
    "network": {"label": "Network", "order": 40, "description": "Fetch, XHR, proxy, status, and resource waterfall evidence."},
    "visual": {"label": "Visual artifacts", "order": 50, "description": "Screenshots, DOM/replay artifacts, layout shifts, and captures."},
    "react": {"label": "React", "order": 60, "description": "Profiler commits, scheduler phases, and component milestones."},
    "engine": {"label": "3D engine", "order": 70, "description": "R3F, Three.js, WebGL, WebGPU, physics, assets, and frames."},
    "backend": {"label": "Backend trace", "order": 80, "description": "OpenTelemetry-style spans, queues, DB/cache, logs, and workers."},
    "receipt": {"label": "Receipts", "order": 90, "description": "Candidate receipts and durable evidence pointers."},
    "unknown": {"label": "Unknown", "order": 999, "description": "Events that have not yet been classified."},
}

EXPECTED_SOURCES = (
    "app_diagnostics",
    "cockpit_http",
    "browser_probe",
    "project_launcher_receipt",
    "preview_proxy",
    "react_adapter",
    "r3f_adapter",
    "three_adapter",
    "webgl_adapter",
    "webgpu_adapter",
    "otel_backend",
)

EVENT_TYPE_HINTS: dict[str, dict[str, str]] = {
    "diagnostics_config_update": {"lane": "control", "signal": "diagnostic_policy", "kind": "instant"},
    "launch_start": {"lane": "control", "signal": "runtime_control", "kind": "span"},
    "launch_stop": {"lane": "control", "signal": "runtime_control", "kind": "span"},
    "launch_status": {"lane": "network", "signal": "http", "kind": "instant"},
    "launch_http_event": {"lane": "network", "signal": "http", "kind": "instant"},
    "launch_diagnostics_capture": {"lane": "visual", "signal": "artifact", "kind": "span"},
    "probe_installed": {"lane": "browser", "signal": "lifecycle", "kind": "instant"},
    "console": {"lane": "browser", "signal": "log", "kind": "instant"},
    "window_error": {"lane": "browser", "signal": "error", "kind": "instant"},
    "unhandled_rejection": {"lane": "browser", "signal": "error", "kind": "instant"},
    "fetch": {"lane": "network", "signal": "http", "kind": "span"},
    "xhr": {"lane": "network", "signal": "http", "kind": "span"},
    "performance": {"lane": "performance", "signal": "metric", "kind": "span"},
    "longtask": {"lane": "performance", "signal": "metric", "kind": "span"},
    "web_vital": {"lane": "performance", "signal": "metric", "kind": "instant"},
    "dom_mutation": {"lane": "visual", "signal": "dom", "kind": "instant"},
    "layout_shift": {"lane": "visual", "signal": "metric", "kind": "instant"},
    "react": {"lane": "react", "signal": "component", "kind": "span"},
    "r3f": {"lane": "engine", "signal": "engine", "kind": "span"},
    "three": {"lane": "engine", "signal": "engine", "kind": "span"},
    "webgl": {"lane": "engine", "signal": "gpu", "kind": "instant"},
    "webgpu": {"lane": "engine", "signal": "gpu", "kind": "instant"},
    "gpu": {"lane": "engine", "signal": "gpu", "kind": "span"},
    "otel": {"lane": "backend", "signal": "trace", "kind": "span"},
    "span": {"lane": "backend", "signal": "trace", "kind": "span"},
    "receipt": {"lane": "receipt", "signal": "receipt", "kind": "instant"},
}

_SAFE_ID_RE = re.compile(r"[^a-zA-Z0-9_.:-]+")
_SECRET_KEY_RE = re.compile(r"(api[_-]?key|token|secret|password|authorization|bearer|cookie|session)", re.IGNORECASE)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def compact(value: Any, fallback: str = "") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, (int, float, bool)):
        return str(value)
    return fallback


def read_json(path: Path) -> dict[str, Any]:
    try:
        if not path.exists():
            return {}
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def default_config() -> dict[str, Any]:
    return {
        "schema_id": "ion.app_diagnostics_config.v1",
        "enabled": False,
        "mode": "off",
        "max_events": 600,
        "max_detail_chars": 1200,
        "include_payloads": False,
        "include_results": False,
        "include_log_tail": False,
        "include_screenshot_refs": True,
        "sample_status_polls": False,
        "slowdown_intentional": False,
        "adapter_options": {
            "react_devtools_commit_hook": False,
            "webgl_get_error_probe": False,
            "webgpu_request_patch": False,
        },
        "updated_at": None,
        "authority": _authority(),
        "non_claims": _non_claims(),
    }


def load_app_diagnostics_config(root: str | Path = ".") -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    loaded = read_json(shell_root / CONFIG_PATH)
    config = default_config()
    for key, value in loaded.items():
        if key in config:
            config[key] = value
    config["authority"] = _authority()
    config["non_claims"] = _non_claims()
    return config


def app_diagnostics_config_update(root: str | Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    confirmation = compact(payload.get("confirmation"))
    if confirmation not in {APP_DIAGNOSTICS_CONFIRMATION, PROJECT_LOCAL_LAUNCH_CONFIRMATION}:
        return {
            "ok": False,
            "finding": "app_diagnostics_confirmation_required",
            "required_confirmation": APP_DIAGNOSTICS_CONFIRMATION,
            "authority": _authority(),
        }

    requested_mode = compact(payload.get("mode"), "off").lower()
    if requested_mode not in {"off", "standard", "forensic", "exhaustive"}:
        return {"ok": False, "finding": "unsupported_app_diagnostics_mode", "mode": requested_mode, "authority": _authority()}

    enabled = bool(payload.get("enabled")) and requested_mode != "off"
    if requested_mode == "off":
        enabled = False

    presets = {
        "off": {
            "max_events": 300,
            "max_detail_chars": 400,
            "include_payloads": False,
            "include_results": False,
            "include_log_tail": False,
            "sample_status_polls": False,
            "slowdown_intentional": False,
        },
        "standard": {
            "max_events": 600,
            "max_detail_chars": 1200,
            "include_payloads": False,
            "include_results": False,
            "include_log_tail": True,
            "sample_status_polls": False,
            "slowdown_intentional": False,
        },
        "forensic": {
            "max_events": 1600,
            "max_detail_chars": 5000,
            "include_payloads": True,
            "include_results": True,
            "include_log_tail": True,
            "sample_status_polls": True,
            "slowdown_intentional": True,
        },
        "exhaustive": {
            "max_events": 5000,
            "max_detail_chars": 20000,
            "include_payloads": True,
            "include_results": True,
            "include_log_tail": True,
            "sample_status_polls": True,
            "slowdown_intentional": True,
        },
    }
    adapter_options = dict(default_config().get("adapter_options") or {})
    requested_adapter_options = payload.get("adapter_options")
    if isinstance(requested_adapter_options, Mapping):
        for key in tuple(adapter_options):
            if key in requested_adapter_options:
                adapter_options[key] = bool(requested_adapter_options.get(key))

    config = {
        **default_config(),
        **presets[requested_mode],
        "enabled": enabled,
        "mode": requested_mode,
        "adapter_options": adapter_options,
        "updated_at": utc_now(),
    }
    write_json(shell_root / CONFIG_PATH, config)
    receipt = {
        "schema_id": "ion.app_diagnostics_config_receipt.v1",
        "created_at": utc_now(),
        "action": "config_update",
        "config": config,
        "authority": _authority(),
    }
    receipt_path = shell_root / RECEIPTS_DIR / f"{_stamp()}_config_update.json"
    write_json(receipt_path, receipt)
    _append_event(
        shell_root,
        "global",
        {
            "event_type": "diagnostics_config_update",
            "source": "app_diagnostics",
            "severity": "info",
            "summary": f"App diagnostics mode set to {requested_mode}",
            "detail": f"enabled={enabled}; slowdown_intentional={config['slowdown_intentional']}",
            "config": _compact_config(config),
        },
        config={**config, "enabled": True},
    )
    return {"ok": True, "config": config, "receipt_path": receipt_path.as_posix(), "authority": _authority()}


def app_diagnostics_record_http_event(
    root: str | Path,
    *,
    route: str,
    payload: Mapping[str, Any],
    result: Mapping[str, Any],
    source: str = "cockpit_http",
) -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    config = load_app_diagnostics_config(shell_root)
    if not config.get("enabled") or config.get("mode") == "off":
        return {"ok": True, "recorded": False, "reason": "app_diagnostics_disabled"}
    if route.endswith("/status") and not config.get("sample_status_polls"):
        return {"ok": True, "recorded": False, "reason": "status_poll_sampling_disabled"}

    launch = result.get("launch") if isinstance(result.get("launch"), Mapping) else {}
    launch_id = compact(payload.get("launch_id")) or compact(launch.get("launch_id")) or "unbound"
    event_type = _event_type_for_route(route, result)
    event = {
        "event_type": event_type,
        "source": source,
        "severity": "info" if result.get("ok") else "error",
        "summary": compact(result.get("finding"), event_type) if not result.get("ok") else event_type,
        "detail": _detail_from_result(result, config),
        "route": route,
        "project_id": launch.get("project_id") or payload.get("project_id"),
        "version_id": launch.get("version_id") or payload.get("version_id"),
        "path": launch.get("path") or payload.get("path"),
        "url": launch.get("url") or result.get("url"),
        "port": launch.get("port"),
        "state": launch.get("state"),
        "running": launch.get("running"),
        "mode": config.get("mode"),
        "payload": _redact(payload, max_chars=int(config.get("max_detail_chars") or 1200)) if config.get("include_payloads") else {},
        "result": _redact(result, max_chars=int(config.get("max_detail_chars") or 1200)) if config.get("include_results") else {},
        "log_tail": _trim(compact(launch.get("log_tail")), int(config.get("max_detail_chars") or 1200)) if config.get("include_log_tail") else "",
    }
    path = _append_event(shell_root, launch_id, event, config=config)
    return {"ok": True, "recorded": True, "event_path": path.as_posix(), "launch_id": launch_id}


def app_diagnostics_record_browser_event(root: str | Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    config = load_app_diagnostics_config(shell_root)
    if not config.get("enabled") or config.get("mode") == "off":
        return {"ok": True, "recorded": False, "reason": "app_diagnostics_disabled"}
    launch_id = _safe_id(compact(payload.get("launch_id"), "browser"))
    event_type = compact(payload.get("event_type"), "browser_event")
    severity = compact(payload.get("severity"), "info")
    raw_detail = payload.get("detail") if isinstance(payload.get("detail"), Mapping) else {}
    event = {
        "event_type": event_type,
        "source": "browser_probe",
        "severity": severity if severity in {"info", "warn", "error"} else "info",
        "summary": compact(payload.get("summary"), event_type),
        "detail": _trim(compact(payload.get("message") or payload.get("detail_text")), int(config.get("max_detail_chars") or 1200)),
        "browser_seq": payload.get("seq"),
        "browser_timestamp_ms": payload.get("timestamp_ms"),
        "url": payload.get("url"),
        "path": payload.get("path"),
        "mode": config.get("mode"),
        "probe": _redact(raw_detail, max_chars=int(config.get("max_detail_chars") or 1200)),
    }
    path = _append_event(shell_root, launch_id, event, config=config)
    return {"ok": True, "recorded": True, "event_path": path.as_posix(), "launch_id": launch_id}


def app_diagnostics_timeline_model(root: str | Path, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    shell_root = Path(root).expanduser().resolve()
    config = load_app_diagnostics_config(shell_root)
    limit = _int(payload.get("limit"), int(config.get("max_events") or 600))
    limit = max(1, min(limit, int(config.get("max_events") or 600), 5000))
    launch_id = _safe_id(compact(payload.get("launch_id")))
    events = _read_events(shell_root, launch_id=launch_id, limit=limit)
    synthetic_events = _receipt_events(shell_root, launch_id=launch_id, limit=max(25, min(limit, 200)), config=config)
    merged = sorted([*events, *synthetic_events], key=lambda row: compact(row.get("created_at")))
    if len(merged) > limit:
        merged = merged[-limit:]
    lanes = _timeline_lanes(merged)
    source_health = _source_health(merged)
    return {
        "ok": True,
        "schema_id": SCHEMA_ID,
        "event_schema_id": EVENT_SCHEMA_ID,
        "generated_at": utc_now(),
        "launch_id": launch_id,
        "config": _compact_config(config),
        "summary": {
            "event_count": len(merged),
            "stored_event_count": len(events),
            "receipt_event_count": len(synthetic_events),
            "lane_count": len([row for row in lanes if row.get("event_count")]),
            "source_count": len([row for row in source_health if row.get("event_count")]),
            "mode": config.get("mode"),
            "enabled": bool(config.get("enabled")),
            "slowdown_intentional": bool(config.get("slowdown_intentional")),
        },
        "lanes": lanes,
        "source_health": source_health,
        "event_type_registry": [
            {"match": match, "lane": meta["lane"], "signal": meta["signal"], "kind": meta["kind"]}
            for match, meta in sorted(EVENT_TYPE_HINTS.items())
        ],
        "events": merged,
        "paths": {
            "config": (shell_root / CONFIG_PATH).as_posix(),
            "events_dir": (shell_root / EVENTS_DIR).as_posix(),
            "receipts_dir": (shell_root / RECEIPTS_DIR).as_posix(),
        },
        "authority": _authority(),
        "non_claims": _non_claims(),
    }


def app_diagnostics_snapshot(root: str | Path, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    shell_root = Path(root).expanduser().resolve()
    confirmation = compact(payload.get("confirmation"))
    if confirmation not in {APP_DIAGNOSTICS_SNAPSHOT_CONFIRMATION, PROJECT_LOCAL_LAUNCH_CONFIRMATION}:
        return {
            "ok": False,
            "finding": "app_diagnostics_snapshot_confirmation_required",
            "required_confirmation": APP_DIAGNOSTICS_SNAPSHOT_CONFIRMATION,
            "authority": _authority(),
        }
    model = app_diagnostics_timeline_model(shell_root, payload)
    snapshot_id = f"diagnostics_snapshot_{_stamp()}_{_safe_id(compact(payload.get('launch_id'), 'all')) or 'all'}"
    snapshot = {
        "schema_id": "ion.app_diagnostics_snapshot.v1",
        "snapshot_id": snapshot_id,
        "created_at": utc_now(),
        "filters": {
            "launch_id": compact(payload.get("launch_id")),
            "limit": payload.get("limit"),
            "lane": payload.get("lane"),
            "source": payload.get("source"),
            "severity": payload.get("severity"),
            "query": payload.get("query"),
        },
        "timeline": model,
        "authority": _authority(),
        "non_claims": _non_claims(),
    }
    path = shell_root / SNAPSHOTS_DIR / f"{snapshot_id}.candidate.json"
    write_json(path, snapshot)
    receipt = {
        "schema_id": "ion.app_diagnostics_snapshot_receipt.v1",
        "created_at": utc_now(),
        "snapshot_id": snapshot_id,
        "snapshot_path": path.as_posix(),
        "event_count": model.get("summary", {}).get("event_count") if isinstance(model.get("summary"), Mapping) else None,
        "authority": _authority(),
        "non_claims": _non_claims(),
    }
    receipt_path = shell_root / RECEIPTS_DIR / f"{_stamp()}_{snapshot_id}_snapshot.json"
    write_json(receipt_path, receipt)
    return {
        "ok": True,
        "snapshot_id": snapshot_id,
        "snapshot_path": path.as_posix(),
        "receipt_path": receipt_path.as_posix(),
        "summary": model.get("summary"),
        "authority": _authority(),
        "non_claims": _non_claims(),
    }


def _append_event(shell_root: Path, launch_id: str, event: Mapping[str, Any], *, config: Mapping[str, Any]) -> Path:
    EVENTS_DIR_ABS = shell_root / EVENTS_DIR
    EVENTS_DIR_ABS.mkdir(parents=True, exist_ok=True)
    safe_launch_id = _safe_id(launch_id) or "unbound"
    path = EVENTS_DIR_ABS / f"{safe_launch_id}.jsonl"
    payload = _normalize_event(safe_launch_id, event, config=config, previous_hash=_latest_event_hash(path))
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
    all_path = EVENTS_DIR_ABS / "_all.jsonl"
    with all_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")
    return path


def _read_events(shell_root: Path, *, launch_id: str, limit: int) -> list[dict[str, Any]]:
    path = shell_root / EVENTS_DIR / (f"{launch_id}.jsonl" if launch_id else "_all.jsonl")
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]:
            if not line.strip():
                continue
            value = json.loads(line)
            if isinstance(value, dict):
                rows.append(value)
    except Exception:
        return rows
    return rows


def _receipt_events(shell_root: Path, *, launch_id: str, limit: int, config: Mapping[str, Any]) -> list[dict[str, Any]]:
    receipt_dir = shell_root / CURRENT / "project_launcher" / "receipts"
    if not receipt_dir.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(receipt_dir.glob("*.json"), key=lambda item: item.stat().st_mtime)[-limit:]:
        receipt = read_json(path)
        launch = receipt.get("launch") if isinstance(receipt.get("launch"), Mapping) else {}
        current_launch_id = compact(launch.get("launch_id")) or compact(receipt.get("launch_id"))
        if launch_id and current_launch_id != launch_id:
            continue
        rows.append(
            _normalize_event(
                current_launch_id or "unbound",
                {
                    "schema_id": EVENT_SCHEMA_ID,
                    "event_id": f"receipt-{path.stem}",
                    "created_at": compact(receipt.get("created_at")),
                    "event_type": f"receipt_{compact(receipt.get('action'), 'event')}",
                    "source": "project_launcher_receipt",
                    "severity": "info" if receipt.get("ok", True) else "error",
                    "summary": f"receipt {compact(receipt.get('action'), 'event')}",
                    "detail": path.as_posix(),
                    "path": launch.get("path"),
                    "url": launch.get("url"),
                    "port": launch.get("port"),
                    "state": launch.get("state"),
                    "running": launch.get("running"),
                    "receipt_path": path.as_posix(),
                },
                config=config,
                previous_hash=None,
                synthetic=True,
            )
        )
    return rows


def _event_type_for_route(route: str, result: Mapping[str, Any]) -> str:
    if route.endswith("/start"):
        return "launch_start_reused" if result.get("reused") else "launch_start"
    if route.endswith("/stop"):
        return "launch_stop"
    if route.endswith("/status"):
        return "launch_status"
    if route.endswith("/diagnostics"):
        return "launch_diagnostics_capture"
    return "launch_http_event"


def _normalize_event(
    launch_id: str,
    event: Mapping[str, Any],
    *,
    config: Mapping[str, Any],
    previous_hash: str | None,
    synthetic: bool = False,
) -> dict[str, Any]:
    event_type = compact(event.get("event_type"), "diagnostic_event")
    source = compact(event.get("source"), "unknown")
    severity = compact(event.get("severity"), "info").lower()
    if severity not in {"debug", "info", "warn", "error", "critical"}:
        severity = "info"
    safe_launch_id = _safe_id(launch_id) or "unbound"
    lane = compact(event.get("lane")) or _lane_for_event(event_type, source)
    mode = compact(event.get("mode") or config.get("mode"), "off")
    created_at = compact(event.get("created_at")) or utc_now()
    event_id = compact(event.get("event_id")) or f"diag-{_stamp()}-{safe_launch_id}"
    url_sanitized = _sanitize_url(compact(event.get("url")))
    payload = {
        "schema_id": EVENT_SCHEMA_ID,
        "legacy_schema_id": LEGACY_EVENT_SCHEMA_ID,
        "event_id": event_id,
        "event_type": event_type,
        "event_kind": _event_kind_for(event_type),
        "signal": _signal_for(event_type),
        "created_at": created_at,
        "observed_at": utc_now(),
        "time_origin_ms": event.get("time_origin_ms"),
        "monotonic_ms": event.get("browser_timestamp_ms") or event.get("monotonic_ms"),
        "duration_ms": event.get("duration_ms") or event.get("duration"),
        "sequence": event.get("browser_seq") or event.get("sequence"),
        "launch_id": safe_launch_id,
        "run_id": compact(event.get("run_id"), safe_launch_id),
        "preview_id": compact(event.get("preview_id"), safe_launch_id),
        "app_id": compact(event.get("project_id") or event.get("path"), "unknown"),
        "source": source,
        "source_id": source,
        "source_kind": compact(event.get("source_kind")) or _source_kind_for(source, event_type),
        "lane": lane,
        "lane_label": LANE_REGISTRY.get(lane, LANE_REGISTRY["unknown"])["label"],
        "diagnostics_mode": mode,
        "mode": mode,
        "slowdown_intentional": bool(config.get("slowdown_intentional")),
        "severity": severity,
        "summary": compact(event.get("summary"), event_type),
        "detail": compact(event.get("detail")),
        "trace_id": compact(event.get("trace_id")) or _trace_id_for(safe_launch_id),
        "span_id": compact(event.get("span_id")) or _span_id_for(event_id),
        "parent_span_id": compact(event.get("parent_span_id")) or None,
        "correlation_ids": _correlation_ids(event, safe_launch_id),
        "route_pattern": compact(event.get("route")) or None,
        "url": url_sanitized,
        "url_sanitized": url_sanitized or None,
        "path": event.get("path"),
        "receipt_path": event.get("receipt_path"),
        "port": event.get("port"),
        "state": event.get("state"),
        "running": event.get("running"),
        "attributes": _event_attributes(event),
        "payload": _event_payload(event),
        "artifact_refs": _artifact_refs(event),
        "edge_refs": [],
        "source_of_truth_classification": "durable_ion_receipt" if synthetic or lane == "receipt" else "carrier_intake_evidence",
        "redaction": {
            "policy_id": "ion.app_diagnostics.redaction.v1",
            "applied": True,
            "truncated": _payload_truncated(event),
            "dropped_fields": ["authorization", "cookie", "token", "secret", "password", "api_key"],
        },
        "limits": {
            "max_detail_chars": _int(config.get("max_detail_chars"), 1200),
            "max_events": _int(config.get("max_events"), 600),
            "event_bytes": 0,
            "hard_limit_bytes": 65536,
        },
        "integrity": {
            "previous_event_hash": previous_hash,
            "event_hash": None,
            "hash_algorithm": "sha256",
        },
        "authority": _authority(),
        "non_claims": _non_claims(),
    }
    payload["limits"]["event_bytes"] = len(json.dumps(payload, sort_keys=True, default=str).encode("utf-8"))
    payload["integrity"]["event_hash"] = _event_hash(payload)
    return payload


def _event_attributes(event: Mapping[str, Any]) -> dict[str, Any]:
    keys = ("project_id", "version_id", "route", "state", "running", "port", "browser_seq", "browser_timestamp_ms", "mode")
    return {key: event.get(key) for key in keys if event.get(key) is not None}


def _event_payload(event: Mapping[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key in ("payload", "result", "probe", "log_tail"):
        if event.get(key) not in (None, "", {}, []):
            payload[key] = event.get(key)
    return payload


def _artifact_refs(event: Mapping[str, Any]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for key in ("receipt_path", "screenshot_path", "path"):
        value = compact(event.get(key))
        if value and ("/" in value or value.endswith(".json") or value.endswith(".png")):
            refs.append({"kind": key, "path": value})
    return refs


def _timeline_lanes(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {
        lane_id: {
            "lane_id": lane_id,
            "label": meta["label"],
            "order": meta["order"],
            "description": meta["description"],
            "event_count": 0,
            "error_count": 0,
            "latest_at": None,
            "sources": [],
        }
        for lane_id, meta in LANE_REGISTRY.items()
    }
    for event in events:
        lane_id = compact(event.get("lane"), "unknown")
        if lane_id not in rows:
            lane_id = "unknown"
        row = rows[lane_id]
        row["event_count"] += 1
        if compact(event.get("severity")).lower() in {"error", "critical"}:
            row["error_count"] += 1
        created_at = compact(event.get("created_at"))
        if created_at and (not row.get("latest_at") or created_at > str(row.get("latest_at"))):
            row["latest_at"] = created_at
        source = compact(event.get("source"))
        if source and source not in row["sources"]:
            row["sources"].append(source)
    return sorted(rows.values(), key=lambda row: int(row.get("order") or 999))


def _source_health(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {
        source: {
            "source_id": source,
            "source_kind": _source_kind_for(source, ""),
            "status": "unavailable",
            "event_count": 0,
            "error_count": 0,
            "latest_at": None,
            "lanes": [],
        }
        for source in EXPECTED_SOURCES
    }
    for event in events:
        source = compact(event.get("source"), "unknown")
        row = rows.setdefault(
            source,
            {
                "source_id": source,
                "source_kind": compact(event.get("source_kind"), "unknown"),
                "status": "unavailable",
                "event_count": 0,
                "error_count": 0,
                "latest_at": None,
                "lanes": [],
            },
        )
        row["event_count"] += 1
        row["status"] = "active"
        if compact(event.get("severity")).lower() in {"error", "critical"}:
            row["error_count"] += 1
            row["status"] = "error"
        created_at = compact(event.get("created_at"))
        if created_at and (not row.get("latest_at") or created_at > str(row.get("latest_at"))):
            row["latest_at"] = created_at
        lane = compact(event.get("lane"))
        if lane and lane not in row["lanes"]:
            row["lanes"].append(lane)
    return sorted(rows.values(), key=lambda row: (0 if row.get("event_count") else 1, str(row.get("source_id"))))


def _lane_for_event(event_type: str, source: str) -> str:
    lowered = f"{event_type} {source}".lower()
    for hint, meta in EVENT_TYPE_HINTS.items():
        if hint in lowered:
            return meta["lane"]
    return "unknown"


def _signal_for(event_type: str) -> str:
    lowered = event_type.lower()
    for hint, meta in EVENT_TYPE_HINTS.items():
        if hint in lowered:
            return meta["signal"]
    return "event"


def _event_kind_for(event_type: str) -> str:
    lowered = event_type.lower()
    for hint, meta in EVENT_TYPE_HINTS.items():
        if hint in lowered:
            return meta["kind"]
    return "instant"


def _source_kind_for(source: str, event_type: str) -> str:
    lowered = f"{source} {event_type}".lower()
    if "browser" in lowered or "console" in lowered or "window" in lowered:
        return "browser"
    if "webgl" in lowered or "webgpu" in lowered or "three" in lowered or "r3f" in lowered or "gpu" in lowered:
        return "engine"
    if "react" in lowered:
        return "react"
    if "receipt" in lowered:
        return "receipt"
    if "http" in lowered or "fetch" in lowered or "xhr" in lowered or "network" in lowered or "proxy" in lowered:
        return "network"
    if "otel" in lowered or "span" in lowered or "backend" in lowered or "queue" in lowered:
        return "backend"
    if "diagnostic" in lowered or "launcher" in lowered:
        return "control"
    return "unknown"


def _correlation_ids(event: Mapping[str, Any], launch_id: str) -> list[str]:
    ids = [launch_id]
    for key in ("trace_id", "span_id", "request_id", "project_id", "version_id", "browser_seq"):
        value = compact(event.get(key))
        if value and value not in ids:
            ids.append(value)
    return ids


def _sanitize_url(value: str) -> str:
    if not value:
        return ""
    return value.split("?", 1)[0].split("#", 1)[0]


def _payload_truncated(event: Mapping[str, Any]) -> bool:
    return "...[truncated]" in json.dumps(dict(event), sort_keys=True, default=str)


def _event_hash(payload: Mapping[str, Any]) -> str:
    clone = json.loads(json.dumps(dict(payload), sort_keys=True, default=str))
    if isinstance(clone.get("integrity"), dict):
        clone["integrity"]["event_hash"] = None
    return hashlib.sha256(json.dumps(clone, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _trace_id_for(value: str) -> str:
    return hashlib.sha256(f"ion-diagnostics-trace:{value}".encode("utf-8")).hexdigest()[:32]


def _span_id_for(value: str) -> str:
    return hashlib.sha256(f"ion-diagnostics-span:{value}".encode("utf-8")).hexdigest()[:16]


def _latest_event_hash(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        last = ""
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.strip():
                last = line
        if not last:
            return None
        value = json.loads(last)
        integrity = value.get("integrity") if isinstance(value, Mapping) else {}
        event_hash = integrity.get("event_hash") if isinstance(integrity, Mapping) else None
        return compact(event_hash) or hashlib.sha256(last.encode("utf-8")).hexdigest()
    except Exception:
        return None


def _detail_from_result(result: Mapping[str, Any], config: Mapping[str, Any]) -> str:
    launch = result.get("launch") if isinstance(result.get("launch"), Mapping) else {}
    parts = [
        f"ok={bool(result.get('ok'))}",
        f"state={compact(launch.get('state'), 'unknown')}",
        f"running={bool(launch.get('running'))}",
        f"url={compact(launch.get('url') or result.get('url'))}",
    ]
    if result.get("finding"):
        parts.append(f"finding={compact(result.get('finding'))}")
    return _trim("; ".join(parts), int(config.get("max_detail_chars") or 1200))


def _compact_config(config: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "enabled": bool(config.get("enabled")),
        "mode": compact(config.get("mode"), "off"),
        "max_events": _int(config.get("max_events"), 600),
        "max_detail_chars": _int(config.get("max_detail_chars"), 1200),
        "include_payloads": bool(config.get("include_payloads")),
        "include_results": bool(config.get("include_results")),
        "include_log_tail": bool(config.get("include_log_tail")),
        "include_screenshot_refs": bool(config.get("include_screenshot_refs")),
        "sample_status_polls": bool(config.get("sample_status_polls")),
        "slowdown_intentional": bool(config.get("slowdown_intentional")),
        "adapter_options": dict(config.get("adapter_options") or {}),
        "updated_at": config.get("updated_at"),
    }


def _redact(value: Any, *, max_chars: int) -> Any:
    if isinstance(value, Mapping):
        result: dict[str, Any] = {}
        for key, item in value.items():
            key_str = str(key)
            if _SECRET_KEY_RE.search(key_str):
                result[key_str] = "[REDACTED]"
            else:
                result[key_str] = _redact(item, max_chars=max_chars)
        return result
    if isinstance(value, list):
        return [_redact(item, max_chars=max_chars) for item in value[:100]]
    if isinstance(value, str):
        if _SECRET_KEY_RE.search(value[:120]):
            return "[REDACTED]"
        return _trim(value, max_chars)
    return value


def _trim(value: str, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    return value[: max(0, max_chars - 20)].rstrip() + " ...[truncated]"


def _safe_id(value: str) -> str:
    return _SAFE_ID_RE.sub("_", value.strip())[:180]


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _int(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except Exception:
        return fallback


def _authority() -> dict[str, bool]:
    return {
        "candidate_local_runtime_control": True,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "git_push_authority": False,
        "deletion_authority": False,
    }


def _non_claims() -> list[str]:
    return [
        "diagnostics timeline is local candidate evidence only",
        "events are not accepted state",
        "timeline capture does not grant production or secrets authority",
        "forensic and exhaustive modes may intentionally slow the app/server",
    ]
