"""Local project launch controls for the Projects cockpit.

This is a candidate local-machine control lane. It starts development servers
only for project roots already visible through the local project portfolio and
keeps stop/status receipts local to the cockpit runtime.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import socket
import subprocess
import sys
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from typing import Any, Mapping

from .ion_app_diagnostics_timeline import (
    APP_DIAGNOSTICS_CONFIRMATION,
    APP_DIAGNOSTICS_SNAPSHOT_CONFIRMATION,
    app_diagnostics_config_update,
    app_diagnostics_snapshot,
    app_diagnostics_timeline_model,
)


CURRENT = Path("ION/05_context/current")
PROJECT_LAUNCHER_DIR = CURRENT / "project_launcher"
PROJECT_LAUNCHER_LOG_DIR = PROJECT_LAUNCHER_DIR / "logs"
PROJECT_LAUNCHER_RECEIPTS_DIR = PROJECT_LAUNCHER_DIR / "receipts"
PROJECT_LAUNCHER_SCREENSHOTS_DIR = PROJECT_LAUNCHER_DIR / "screenshots"
APP_DIAGNOSTICS_CONFIG_PATH = PROJECT_LAUNCHER_DIR / "app_diagnostics" / "APP_DIAGNOSTICS_CONFIG.json"
APP_DIAGNOSTICS_MATRIX_DIR = PROJECT_LAUNCHER_DIR / "app_diagnostics" / "matrix_runs"
DIAGNOSTIC_SMOKE_APPS_DIR = PROJECT_LAUNCHER_DIR / "diagnostic_smoke_apps"
PROJECT_LOCAL_LAUNCH_CONFIRMATION = "ION_PROJECT_LOCAL_LAUNCH_CONFIRMED"
APP_DIAGNOSTICS_MATRIX_CONFIRMATION = "ION_APP_DIAGNOSTICS_MATRIX_CONFIRMED"
HOST = "127.0.0.1"
DEFAULT_PORT_BASE = 6320
MAX_PORT_SCAN = 240

_LOCK = threading.RLock()
_LAUNCHES: dict[str, "LaunchRecord"] = {}


@dataclass
class LaunchRecord:
    launch_id: str
    project_id: str
    version_id: str
    label: str
    path: str
    framework: str
    command: list[str]
    url: str
    port: int
    log_path: str
    stop_token: str
    process: subprocess.Popen[bytes] | None = None
    state: str = "starting"
    message: str = "starting"
    created_at: str = field(default_factory=lambda: utc_now())
    updated_at: str = field(default_factory=lambda: utc_now())
    exit_code: int | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def stamp_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


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
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def project_launch_metadata(path: str | Path, *, scripts: Mapping[str, Any] | None = None, markers: list[str] | tuple[str, ...] = ()) -> dict[str, Any]:
    root = Path(path).expanduser()
    package_json = read_json(root / "package.json")
    package_scripts = package_json.get("scripts") if isinstance(package_json.get("scripts"), Mapping) else {}
    script_map = dict(scripts or package_scripts)
    framework = _detect_framework(root, script_map, markers)
    launchable = framework in {"vite", "next", "static"} or bool(script_map.get("dev") or script_map.get("start"))
    return {
        "launchable": launchable,
        "framework": framework,
        "mode": "managed_local_dev_server" if launchable else "metadata_only",
        "action_path": "/cockpit/projects/launch/start",
        "stop_path": "/cockpit/projects/launch/stop",
        "status_path": "/cockpit/projects/launch/status",
        "diagnostics_path": "/cockpit/projects/launch/diagnostics",
        "requires_local_machine": True,
        "install_repair_on_launch": bool(package_json),
        "managed_window_stops_server": True,
        "host": HOST,
        "status": "ready" if launchable else "not_launchable",
    }


def build_project_launcher_status(root: str | Path = ".") -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    with _LOCK:
        records = [_record_payload(shell_root, record) for record in list(_LAUNCHES.values())]
    running = [item for item in records if item.get("running")]
    return {
        "schema_id": "ion.project_launcher_status.v1",
        "ok": True,
        "generated_at": utc_now(),
        "confirmation": PROJECT_LOCAL_LAUNCH_CONFIRMATION,
        "host": HOST,
        "running_count": len(running),
        "launch_count": len(records),
        "launches": records,
        "authority": {
            "candidate_local_runtime_control": True,
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    }


def project_launcher_start(root: str | Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    if compact(payload.get("confirmation")) != PROJECT_LOCAL_LAUNCH_CONFIRMATION:
        return {
            "ok": False,
            "finding": "launch_confirmation_required",
            "required_confirmation": PROJECT_LOCAL_LAUNCH_CONFIRMATION,
            "production_authority": False,
            "accepted_state_authority": False,
        }

    source_path = _authorized_project_path(shell_root, compact(payload.get("path")))
    if source_path is None:
        return {"ok": False, "finding": "project_launch_path_not_authorized", "path": compact(payload.get("path"))}
    metadata = project_launch_metadata(source_path)
    if not metadata.get("launchable"):
        return {"ok": False, "finding": "project_not_launchable", "path": source_path.as_posix(), "framework": metadata.get("framework")}

    project_id = compact(payload.get("project_id"), _hash_id(source_path.as_posix())[:12])
    version_id = compact(payload.get("version_id"), _hash_id(source_path.as_posix())[:12])
    label = compact(payload.get("label"), source_path.name)
    install_repair = payload.get("install_repair")
    if install_repair is None:
        install_repair = bool(metadata.get("install_repair_on_launch"))
    launch_key = _hash_id(source_path.as_posix())

    with _LOCK:
        for record in list(_LAUNCHES.values()):
            if record.path == source_path.as_posix() and _record_running(record):
                return {
                    "ok": True,
                    "reused": True,
                    "launch": _record_payload(shell_root, record),
                    "open_href": _open_href(record),
                    "url": record.url,
                    "managed_window_stops_server": True,
                }

        port = _next_free_port()
        command = _launch_command(source_path, metadata["framework"], port)
        if command is None:
            return {"ok": False, "finding": "project_launch_command_not_available", "path": source_path.as_posix()}
        launch_id = f"{launch_key[:14]}-{port}"
        log_path = shell_root / PROJECT_LAUNCHER_LOG_DIR / f"{launch_id}.log"
        stop_token = _hash_id(f"{launch_id}:{source_path}:{utc_now()}")[:24]
        record = LaunchRecord(
            launch_id=launch_id,
            project_id=project_id,
            version_id=version_id,
            label=label,
            path=source_path.as_posix(),
            framework=metadata["framework"],
            command=command,
            url=f"http://{HOST}:{port}/",
            port=port,
            log_path=log_path.as_posix(),
            stop_token=stop_token,
            state="installing" if install_repair and (source_path / "package.json").exists() else "starting",
            message="installing or repairing dependencies" if install_repair and (source_path / "package.json").exists() else "starting dev server",
        )
        _LAUNCHES[launch_id] = record
        log_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if install_repair and (source_path / "package.json").exists():
            _spawn_install_then_launch(record, source_path)
        else:
            _spawn_dev_server(record, source_path, command)
    except Exception as exc:
        with _LOCK:
            record.state = "failed"
            record.message = f"launch failed: {exc.__class__.__name__}"
            record.updated_at = utc_now()
        return {"ok": False, "finding": "project_launch_failed", "error": exc.__class__.__name__, "launch": _record_payload(shell_root, record)}

    _write_launch_receipt(shell_root, "start", record)
    return {
        "ok": True,
        "launch": _record_payload(shell_root, record),
        "open_href": _open_href(record),
        "url": record.url,
        "managed_window_stops_server": True,
        "production_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def project_launcher_stop(root: str | Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    launch_id = compact(payload.get("launch_id"))
    if not launch_id:
        return {"ok": False, "finding": "launch_id_required"}
    with _LOCK:
        record = _LAUNCHES.get(launch_id)
    if not record:
        return {"ok": False, "finding": "launch_not_found", "launch_id": launch_id}

    confirmation_ok = compact(payload.get("confirmation")) == PROJECT_LOCAL_LAUNCH_CONFIRMATION
    stop_token_ok = compact(payload.get("stop_token")) == record.stop_token
    if not confirmation_ok and not stop_token_ok:
        return {"ok": False, "finding": "launch_stop_confirmation_required", "required_confirmation": PROJECT_LOCAL_LAUNCH_CONFIRMATION}

    _terminate_record(record)
    _write_launch_receipt(shell_root, "stop", record)
    return {"ok": True, "launch": _record_payload(shell_root, record), "production_authority": False, "accepted_state_authority": False}


def project_launcher_status(root: str | Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    launch_id = compact(payload.get("launch_id"))
    with _LOCK:
        if launch_id:
            record = _LAUNCHES.get(launch_id)
            if not record:
                return {"ok": False, "finding": "launch_not_found", "launch_id": launch_id}
            return {"ok": True, "launch": _record_payload(shell_root, record)}
    return build_project_launcher_status(shell_root)


def project_launcher_diagnostics(root: str | Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    launch_id = compact(payload.get("launch_id"))
    if not launch_id:
        return {"ok": False, "finding": "launch_id_required"}
    with _LOCK:
        record = _LAUNCHES.get(launch_id)
    if not record:
        return {"ok": False, "finding": "launch_not_found", "launch_id": launch_id}
    confirmation_ok = compact(payload.get("confirmation")) == PROJECT_LOCAL_LAUNCH_CONFIRMATION
    stop_token_ok = compact(payload.get("stop_token")) == record.stop_token
    if not confirmation_ok and not stop_token_ok:
        return {
            "ok": False,
            "finding": "launch_diagnostics_confirmation_required",
            "required_confirmation": PROJECT_LOCAL_LAUNCH_CONFIRMATION,
            "requires_stop_token": True,
            "production_authority": False,
            "accepted_state_authority": False,
        }
    launch = _record_payload(shell_root, record)
    result: dict[str, Any] = {
        "ok": True,
        "schema_id": "ion.project_launcher_diagnostics.v1",
        "generated_at": utc_now(),
        "launch": launch,
        "diagnostics": {
            "url": record.url,
            "running": launch.get("running"),
            "state": launch.get("state"),
            "log_tail": launch.get("log_tail"),
            "process_exit_code": launch.get("exit_code"),
            "playwright_capture": bool(payload.get("capture")),
        },
        "production_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }
    if payload.get("capture"):
        screenshot = _capture_launch_screenshot(shell_root, record, payload)
        result["screenshot"] = screenshot
        result["diagnostics"]["screenshot_status"] = screenshot.get("status")
        if not screenshot.get("ok"):
            result["ok"] = False
            result["finding"] = screenshot.get("finding", "launch_screenshot_failed")
    _write_diagnostics_receipt(shell_root, record, result)
    return result


def project_launcher_diagnostics_matrix(root: str | Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    confirmation = compact(payload.get("confirmation"))
    if confirmation not in {APP_DIAGNOSTICS_MATRIX_CONFIRMATION, PROJECT_LOCAL_LAUNCH_CONFIRMATION}:
        return {
            "ok": False,
            "finding": "app_diagnostics_matrix_confirmation_required",
            "required_confirmation": APP_DIAGNOSTICS_MATRIX_CONFIRMATION,
            "production_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        }

    mode = compact(payload.get("mode"), "forensic").lower()
    if mode not in {"standard", "forensic", "exhaustive"}:
        return {"ok": False, "finding": "unsupported_app_diagnostics_matrix_mode", "mode": mode}
    include_framework = payload.get("include_framework") is not False
    stop_after = payload.get("stop_after") is not False
    timeout_seconds = max(8, min(_payload_int(payload, "timeout_seconds", 35), 120))
    base_url = compact(payload.get("base_url"), f"http://{HOST}:8765").rstrip("/")
    if not (base_url.startswith(f"http://{HOST}:") or base_url.startswith("http://localhost:")):
        return {"ok": False, "finding": "app_diagnostics_matrix_base_url_not_local", "base_url": base_url}

    config_result = app_diagnostics_config_update(
        shell_root,
        {
            "confirmation": APP_DIAGNOSTICS_CONFIRMATION,
            "enabled": True,
            "mode": mode,
            "adapter_options": {
                "react_devtools_commit_hook": False,
                "webgl_get_error_probe": False,
                "webgpu_request_patch": False,
            },
        },
    )
    if not config_result.get("ok"):
        return {"ok": False, "finding": "app_diagnostics_matrix_config_failed", "config_result": config_result}

    fixtures = _diagnostics_matrix_fixtures(shell_root, include_framework=include_framework)
    if not fixtures:
        return {"ok": False, "finding": "app_diagnostics_matrix_no_fixtures"}

    matrix_id = f"diagnostics_matrix_{stamp_now()}_{mode}"
    runs = [
        _run_diagnostics_matrix_fixture(
            shell_root,
            fixture,
            mode=mode,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            stop_after=stop_after,
        )
        for fixture in fixtures
    ]
    snapshot = app_diagnostics_snapshot(shell_root, {"confirmation": APP_DIAGNOSTICS_SNAPSHOT_CONFIRMATION, "limit": 1200})
    coverage = _diagnostics_matrix_coverage(runs)
    ok = all(run.get("ok") for run in runs) and bool(snapshot.get("ok"))
    result = {
        "ok": ok,
        "schema_id": "ion.app_diagnostics_matrix_run.v1",
        "matrix_id": matrix_id,
        "created_at": utc_now(),
        "mode": mode,
        "include_framework": include_framework,
        "stop_after": stop_after,
        "base_url": base_url,
        "config_receipt_path": config_result.get("receipt_path"),
        "coverage": coverage,
        "runs": runs,
        "snapshot_path": snapshot.get("snapshot_path"),
        "snapshot_receipt_path": snapshot.get("receipt_path"),
        "authority": {
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
            "git_push_authority": False,
            "deletion_authority": False,
        },
        "non_claims": [
            "candidate diagnostics matrix only",
            "no accepted state movement",
            "no production deployment",
            "no secrets authority",
            "no git push",
            "no deletion",
        ],
    }
    receipt_path = shell_root / APP_DIAGNOSTICS_MATRIX_DIR / f"{matrix_id}.candidate.json"
    write_json(receipt_path, result)
    result["receipt_path"] = receipt_path.as_posix()
    return result


def project_launcher_screenshot_file(root: str | Path, filename: str) -> Path | None:
    if "/" in filename or "\\" in filename or filename.startswith("."):
        return None
    shell_root = Path(root).expanduser().resolve()
    target = (shell_root / PROJECT_LAUNCHER_SCREENSHOTS_DIR / filename).resolve()
    try:
        target.relative_to((shell_root / PROJECT_LAUNCHER_SCREENSHOTS_DIR).resolve())
    except ValueError:
        return None
    if not target.exists() or not target.is_file() or target.suffix.lower() != ".png":
        return None
    return target


def _diagnostics_matrix_fixtures(shell_root: Path, *, include_framework: bool) -> list[dict[str, Any]]:
    specs = [
        {"app_id": "static_lifecycle", "label": "Diagnostics Static Lifecycle", "framework": "static", "install_repair": False},
        {"app_id": "network_trace", "label": "Diagnostics Network Trace", "framework": "static", "install_repair": False},
        {"app_id": "webgl_engine", "label": "Diagnostics WebGL Engine", "framework": "static", "install_repair": False},
    ]
    if include_framework:
        specs.append({"app_id": "vite_react_r3f", "label": "Diagnostics Vite React R3F", "framework": "vite", "install_repair": True})
    fixtures: list[dict[str, Any]] = []
    base = shell_root / DIAGNOSTIC_SMOKE_APPS_DIR
    for spec in specs:
        path = (base / spec["app_id"]).resolve()
        try:
            path.relative_to(shell_root)
        except ValueError:
            continue
        if path.exists() and path.is_dir():
            fixtures.append({**spec, "path": path.as_posix()})
    return fixtures


def _run_diagnostics_matrix_fixture(
    shell_root: Path,
    fixture: Mapping[str, Any],
    *,
    mode: str,
    base_url: str,
    timeout_seconds: int,
    stop_after: bool,
) -> dict[str, Any]:
    app_id = compact(fixture.get("app_id"), "fixture")
    start = project_launcher_start(
        shell_root,
        {
            "confirmation": PROJECT_LOCAL_LAUNCH_CONFIRMATION,
            "path": compact(fixture.get("path")),
            "project_id": f"diagnostics_matrix_{app_id}",
            "version_id": mode,
            "label": compact(fixture.get("label"), app_id),
            "install_repair": bool(fixture.get("install_repair")),
        },
    )
    launch = start.get("launch") if isinstance(start.get("launch"), Mapping) else {}
    launch_id = compact(launch.get("launch_id"))
    stop_token = compact(launch.get("stop_token"))
    before_events = _timeline_events(app_diagnostics_timeline_model(shell_root, {"launch_id": launch_id, "limit": 1600})) if launch_id else []
    before_event_keys = {_diagnostics_event_key(event) for event in before_events}
    statuses: list[dict[str, Any]] = []
    ready = False
    deadline = time.time() + timeout_seconds
    while launch_id and time.time() < deadline:
        time.sleep(0.75)
        status = project_launcher_status(shell_root, {"launch_id": launch_id})
        current = status.get("launch") if isinstance(status.get("launch"), Mapping) else status
        statuses.append(
            {
                "state": current.get("state"),
                "running": current.get("running"),
                "message": current.get("message"),
                "exit_code": current.get("exit_code"),
            }
        )
        if current.get("running") and current.get("state") == "running":
            ready = True
            break
        if current.get("state") == "failed":
            break

    proxy_url = f"{base_url}/cockpit/projects/launch/proxy/{launch_id}/" if launch_id else ""
    screenshot: dict[str, Any] = {}
    if ready and launch_id:
        screenshot_dir = shell_root / PROJECT_LAUNCHER_SCREENSHOTS_DIR
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = screenshot_dir / f"{stamp_now()}_{_safe_file_token(launch_id)}_matrix.png"
        screenshot = _capture_playwright(proxy_url, screenshot_path, width=1280, height=820, timeout_ms=25_000, wait_ms=3_200)
        if screenshot.get("ok"):
            screenshot["screenshot_path"] = screenshot_path.as_posix()
            screenshot["screenshot_href"] = f"/cockpit/projects/launch/screenshot/{screenshot_path.name}"
        time.sleep(0.8)

    timeline = app_diagnostics_timeline_model(shell_root, {"launch_id": launch_id, "limit": 1600}) if launch_id else {}
    stored_events = _timeline_events(timeline)
    events = [event for event in stored_events if _diagnostics_event_key(event) not in before_event_keys]
    event_counts = Counter(compact(event.get("event_type"), "unknown") for event in events)
    event_names = set(event_counts)
    event_text = json.dumps(events, sort_keys=True, default=str).lower()
    coverage = {
        "browser": any("probe_installed" == key or key.startswith("console_") or key.startswith("window_") for key in event_names),
        "performance": any(key.startswith("performance_") or key.startswith("web_vital_") or key == "slow_frame" for key in event_names),
        "network": any(key.startswith("fetch_") or key.startswith("xhr_") for key in event_names),
        "webgl": any(
            key
            in {
                "webgl_drawArrays",
                "webgl_drawElements",
                "webgl_texImage2D",
                "webgl_compileShader",
                "webgl_linkProgram",
                "webgl_context_lost",
                "webgl_context_restored",
            }
            for key in event_names
        ),
        "react": any(key in {"react_r3f_smoke_mounted", "react_profiler_commit"} for key in event_names),
        "r3f": any(key in {"r3f_smoke_canvas_ready", "r3f_adapter_observed", "react_r3f_smoke_mounted"} for key in event_names),
        "three": any(key in {"three_renderer_registered", "three_renderer_sample", "three_renderer_registration_attempt"} for key in event_names) or "three." in event_text,
    }
    stop: dict[str, Any] = {}
    if stop_after and launch_id:
        stop = project_launcher_stop(shell_root, {"launch_id": launch_id, "stop_token": stop_token, "confirmation": PROJECT_LOCAL_LAUNCH_CONFIRMATION})
    expected = {
        "static_lifecycle": ("browser", "performance"),
        "network_trace": ("network", "performance"),
        "webgl_engine": ("webgl", "performance"),
        "vite_react_r3f": ("react", "r3f", "three", "webgl"),
    }.get(app_id, ("browser",))
    expected_met = all(coverage.get(key) for key in expected)
    return {
        "ok": bool(start.get("ok")) and ready and bool(screenshot.get("ok")) and expected_met,
        "app_id": app_id,
        "path": compact(fixture.get("path")),
        "framework": compact(fixture.get("framework"), "static"),
        "start_ok": bool(start.get("ok")),
        "reused": bool(start.get("reused")),
        "launch_id": launch_id,
        "ready": ready,
        "statuses_tail": statuses[-8:],
        "proxy_url": proxy_url,
        "playwright_ok": bool(screenshot.get("ok")),
        "screenshot_path": screenshot.get("screenshot_path"),
        "screenshot_href": screenshot.get("screenshot_href"),
        "console_tail": screenshot.get("console", [])[-10:] if isinstance(screenshot.get("console"), list) else [],
        "timeline_ok": bool(timeline.get("ok")),
        "stored_event_count": len(stored_events),
        "timeline_event_count": len(events),
        "baseline_event_count": len(before_events),
        "event_type_counts": dict(event_counts.most_common(32)),
        "coverage": coverage,
        "expected_coverage": list(expected),
        "expected_coverage_met": expected_met,
        "stop_ok": bool(stop.get("ok")) if stop_after else None,
        "finding": None if expected_met else "expected_diagnostics_coverage_missing",
    }


def _timeline_events(timeline: Mapping[str, Any]) -> list[dict[str, Any]]:
    if isinstance(timeline.get("events"), list):
        return [event for event in timeline["events"] if isinstance(event, dict)]
    events: list[dict[str, Any]] = []
    lanes = timeline.get("lanes")
    if isinstance(lanes, list):
        for lane in lanes:
            if isinstance(lane, Mapping) and isinstance(lane.get("events"), list):
                events.extend(event for event in lane["events"] if isinstance(event, dict))
    return events


def _diagnostics_event_key(event: Mapping[str, Any]) -> str:
    for key in ("event_id", "span_id", "trace_id"):
        value = compact(event.get(key))
        if value:
            return f"{key}:{value}"
    return hashlib.sha256(json.dumps(dict(event), sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _diagnostics_matrix_coverage(runs: list[dict[str, Any]]) -> dict[str, Any]:
    keys = ("browser", "performance", "network", "webgl", "react", "r3f", "three")
    return {
        "run_count": len(runs),
        "passed_count": sum(1 for run in runs if run.get("ok")),
        "failed_count": sum(1 for run in runs if not run.get("ok")),
        **{key: any((run.get("coverage") or {}).get(key) for run in runs) for key in keys},
    }


def _safe_file_token(value: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in value)[:160] or "launch"


def build_project_launcher_open_html(root: str | Path, launch_id: str, stop_token: str = "") -> str:
    shell_root = Path(root).expanduser().resolve()
    with _LOCK:
        record = _LAUNCHES.get(launch_id)
    if not record:
        title = "Launch not found"
        body = "<main><h1>Launch not found</h1><p>The dev server record is not active in this cockpit process.</p></main>"
        return _launcher_html(title, body)
    token = compact(stop_token) or record.stop_token
    launch = _record_payload(shell_root, record)
    launch_state = json.dumps(
        {
            "launch_id": launch_id,
            "stop_token": token,
            "url": record.url,
            "label": record.label,
            "path": record.path,
            "framework": record.framework,
            "state": launch.get("state"),
            "message": launch.get("message"),
            "log_tail": launch.get("log_tail"),
            "stop_path": launch.get("stop_path", "/cockpit/projects/launch/stop"),
            "status_path": launch.get("status_path", "/cockpit/projects/launch/status"),
            "diagnostics_path": launch.get("diagnostics_path", "/cockpit/projects/launch/diagnostics"),
        }
    ).replace("</", "<\\/")
    body = f"""
<main class="ion-preview-shell">
  <header class="ion-preview-topbar">
    <div>
      <span>managed local launch</span>
      <h1>{_html(record.label)}</h1>
      <p id="launch-message">{_html(compact(launch.get("message"), "local app preview ready"))}</p>
    </div>
    <nav class="ion-preview-top-actions" aria-label="Preview actions">
      <a href="{_html(record.url)}" target="_blank" rel="noreferrer">Direct</a>
      <a href="/cockpit#projects" target="_blank" rel="noreferrer">Projects</a>
      <button id="refresh-frame" type="button">Refresh</button>
      <button id="stop" type="button">Stop</button>
    </nav>
  </header>
  <section class="ion-preview-stage" aria-label="Running app preview">
    <div class="ion-preview-viewport-bar" aria-label="Preview viewport controls">
      <button class="is-active" data-preview-viewport="fill" type="button">Fill</button>
      <button data-preview-viewport="desktop" type="button">Desktop</button>
      <button data-preview-viewport="tablet" type="button">Tablet</button>
      <button data-preview-viewport="mobile" type="button">Mobile</button>
      <button id="rotate-viewport" type="button">Rotate</button>
      <span id="viewport-readout">Fill viewport</span>
    </div>
    <div id="frame-shell" class="ion-preview-frame-shell is-fill">
      <iframe id="app-frame" src="{_html(record.url)}" title="{_html(record.label)}"></iframe>
    </div>
  </section>
  <button id="ion-ai-drawer-toggle" class="ion-preview-drawer-toggle" type="button" aria-label="Open AI preview drawer" title="Open AI preview drawer">
    <span>AI</span>
  </button>
  <aside id="ion-ai-drawer" class="ion-preview-ai-drawer" aria-label="AI preview drawer" aria-hidden="true">
    <div class="ion-preview-drawer-head">
      <div>
        <span>preview workbench</span>
        <b>AI + diagnostics</b>
      </div>
      <button id="drawer-close" type="button" aria-label="Close preview drawer">Close</button>
    </div>
    <div class="ion-preview-drawer-tabs" role="tablist" aria-label="Preview drawer tools">
      <button class="is-active" data-preview-tab="ai" type="button">AI</button>
      <button data-preview-tab="capture" type="button">Capture</button>
      <button data-preview-tab="launch" type="button">Launch</button>
      <button data-preview-tab="logs" type="button">Logs</button>
    </div>
    <section class="ion-preview-drawer-panel is-active" data-preview-panel="ai">
      <div class="ion-preview-panel-title">
        <span>sidecar chat access</span>
        <b>open beside or use this drawer</b>
        <p>Keep this preview URL loaded for the app while opening Codex, Browser GPT, or Projects in adjacent browser panes.</p>
      </div>
      <div class="ion-preview-link-grid">
        <a href="/cockpit#codex" target="_blank" rel="noreferrer">Codex Workbench</a>
        <a href="/cockpit#browser-gpt" target="_blank" rel="noreferrer">GPT Browser</a>
        <a href="/cockpit#chatgpt-dom-twin" target="_blank" rel="noreferrer">DOM Twin</a>
        <a href="/cockpit#projects" target="_blank" rel="noreferrer">Projects OS</a>
      </div>
      <div class="ion-preview-action-grid">
        <button id="copy-preview-url" type="button">Copy Preview URL</button>
        <button id="copy-app-url" type="button">Copy App URL</button>
        <button id="open-side-by-side" type="button">Open App + Codex</button>
      </div>
      <div class="ion-preview-path-box">
        <span>project path</span>
        <code>{_html(record.path)}</code>
      </div>
    </section>
    <section class="ion-preview-drawer-panel" data-preview-panel="capture">
      <div class="ion-preview-panel-title">
        <span>screenshot and proof</span>
        <b id="capture-status">ready</b>
        <p>Capture the running app through Playwright and preserve a local diagnostics receipt.</p>
      </div>
      <div class="ion-preview-action-grid">
        <button id="capture-screen" type="button">Screenshot</button>
        <button id="refresh-status" type="button">Refresh Status</button>
      </div>
      <div class="ion-preview-path-box">
        <span>capture viewport</span>
        <code id="capture-viewport">Fill viewport</code>
      </div>
      <img id="capture-image" alt="Latest app screenshot" hidden />
      <div class="ion-preview-path-box">
        <span>screenshot path</span>
        <code id="capture-path">no screenshot captured yet</code>
      </div>
      <pre id="capture-console" class="ion-preview-log"></pre>
    </section>
    <section class="ion-preview-drawer-panel" data-preview-panel="launch">
      <div class="ion-preview-panel-title">
        <span>local server control</span>
        <b id="launch-state">{_html(compact(launch.get("state"), "starting"))}</b>
        <p>{_html(record.url)}</p>
      </div>
      <div class="ion-preview-action-grid">
        <a href="{_html(record.url)}" target="_blank" rel="noreferrer">Open Direct App</a>
        <button id="reload-frame" type="button">Reload Frame</button>
        <button id="stop-drawer" type="button">Stop Server</button>
      </div>
      <div class="ion-preview-status-grid">
        <div><span>framework</span><b>{_html(record.framework)}</b></div>
        <div><span>port</span><b>{_html(record.port)}</b></div>
        <div><span>launch id</span><b>{_html(record.launch_id)}</b></div>
      </div>
    </section>
    <section class="ion-preview-drawer-panel" data-preview-panel="logs">
      <div class="ion-preview-panel-title">
        <span>server output</span>
        <b>tail</b>
      </div>
      <pre id="launch-log" class="ion-preview-log">{_html(compact(launch.get("log_tail")))}</pre>
    </section>
  </aside>
</main>
<script>
const launch = {launch_state};
let stopped = false;
const drawer = document.getElementById('ion-ai-drawer');
const drawerToggle = document.getElementById('ion-ai-drawer-toggle');
const frame = document.getElementById('app-frame');
const frameShell = document.getElementById('frame-shell');
const viewportReadout = document.getElementById('viewport-readout');
const captureViewport = document.getElementById('capture-viewport');
const previewViewports = {{
  fill: null,
  desktop: {{width: 1440, height: 900, label: 'Desktop 1440 x 900'}},
  tablet: {{width: 834, height: 1112, label: 'Tablet 834 x 1112'}},
  mobile: {{width: 390, height: 844, label: 'Mobile 390 x 844'}}
}};
let activeViewport = 'fill';
let viewportRotated = false;
function setDrawer(open) {{
  drawer.classList.toggle('is-open', open);
  drawer.setAttribute('aria-hidden', open ? 'false' : 'true');
}}
function selectedViewportSize() {{
  const selected = previewViewports[activeViewport];
  if (!selected) {{
    return {{
      width: Math.max(900, Math.min(window.innerWidth, 1800)),
      height: Math.max(700, Math.min(window.innerHeight, 1200)),
      label: 'Fill viewport'
    }};
  }}
  const width = viewportRotated ? selected.height : selected.width;
  const height = viewportRotated ? selected.width : selected.height;
  const label = `${{selected.label}}${{viewportRotated ? ' rotated' : ''}}`;
  return {{width, height, label}};
}}
function applyViewport(mode) {{
  activeViewport = mode in previewViewports ? mode : 'fill';
  const size = selectedViewportSize();
  document.querySelectorAll('[data-preview-viewport]').forEach((button) => button.classList.toggle('is-active', button.getAttribute('data-preview-viewport') === activeViewport));
  frameShell.classList.toggle('is-fill', activeViewport === 'fill');
  if (activeViewport === 'fill') {{
    frameShell.style.width = '';
    frameShell.style.height = '';
  }} else {{
    frameShell.style.width = `${{size.width}}px`;
    frameShell.style.height = `${{size.height}}px`;
    const stage = document.querySelector('.ion-preview-stage');
    const availableWidth = Math.max(260, stage.clientWidth - 24);
    const availableHeight = Math.max(320, stage.clientHeight - 56);
    const scale = Math.min(1, availableWidth / size.width, availableHeight / size.height);
    frameShell.style.transform = `scale(${{scale}})`;
  }}
  if (activeViewport === 'fill') frameShell.style.transform = '';
  viewportReadout.textContent = size.label;
  captureViewport.textContent = size.label;
}}
document.querySelectorAll('[data-preview-viewport]').forEach((button) => {{
  button.addEventListener('click', () => applyViewport(button.getAttribute('data-preview-viewport')));
}});
document.getElementById('rotate-viewport').addEventListener('click', () => {{
  viewportRotated = !viewportRotated;
  applyViewport(activeViewport);
}});
window.addEventListener('resize', () => {{
  if (activeViewport === 'fill') applyViewport('fill');
}});
drawerToggle.addEventListener('click', () => setDrawer(!drawer.classList.contains('is-open')));
document.getElementById('drawer-close').addEventListener('click', () => setDrawer(false));
document.querySelectorAll('[data-preview-tab]').forEach((button) => {{
  button.addEventListener('click', () => {{
    const tab = button.getAttribute('data-preview-tab');
    document.querySelectorAll('[data-preview-tab]').forEach((item) => item.classList.toggle('is-active', item === button));
    document.querySelectorAll('[data-preview-panel]').forEach((panel) => panel.classList.toggle('is-active', panel.getAttribute('data-preview-panel') === tab));
  }});
}});
async function postJson(path, payload) {{
  const response = await fetch(path, {{
    method: 'POST',
    headers: {{'Accept': 'application/json', 'Content-Type': 'application/json'}},
    body: JSON.stringify(payload),
    keepalive: false
  }});
  const text = await response.text();
  let result = {{}};
  try {{ result = text ? JSON.parse(text) : {{}}; }} catch (_error) {{ result = {{ok: false, finding: 'json_parse_failed', body: text}}; }}
  if (!response.ok && result.ok !== false) result.ok = false;
  return result;
}}
function stopServer() {{
  if (stopped) return;
  stopped = true;
  const body = JSON.stringify({{launch_id: launch.launch_id, stop_token: launch.stop_token}});
  if (navigator.sendBeacon) {{
    navigator.sendBeacon('/cockpit/projects/launch/stop', new Blob([body], {{type: 'application/json'}}));
  }} else {{
    fetch(launch.stop_path || '/cockpit/projects/launch/stop', {{method: 'POST', headers: {{'Content-Type': 'application/json'}}, body, keepalive: true}});
  }}
}}
function updateLaunch(result) {{
  const item = result.launch || result;
  if (!item) return;
  document.getElementById('launch-state').textContent = item.state || 'unknown';
  document.getElementById('launch-message').textContent = item.message || launch.message || '';
  document.getElementById('launch-log').textContent = item.log_tail || '';
}}
async function refreshStatus() {{
  const result = await postJson(launch.status_path || '/cockpit/projects/launch/status', {{launch_id: launch.launch_id}});
  updateLaunch(result);
  return result;
}}
async function captureScreen() {{
  const status = document.getElementById('capture-status');
  const size = selectedViewportSize();
  status.textContent = 'capturing';
  const result = await postJson(launch.diagnostics_path || '/cockpit/projects/launch/diagnostics', {{
    launch_id: launch.launch_id,
    stop_token: launch.stop_token,
    capture: true,
    width: size.width,
    height: size.height
  }});
  updateLaunch(result);
  const screenshot = result.screenshot || {{}};
  status.textContent = result.ok ? 'captured' : (result.finding || screenshot.finding || 'capture failed');
  document.getElementById('capture-path').textContent = screenshot.screenshot_path || 'no screenshot path returned';
  const image = document.getElementById('capture-image');
  if (screenshot.screenshot_href) {{
    image.hidden = false;
    image.src = screenshot.screenshot_href + '?t=' + Date.now();
  }}
  const consoleRows = screenshot.console || [];
  document.getElementById('capture-console').textContent = consoleRows.map((row) => `[${{row.type || 'log'}}] ${{row.text || ''}}`).join('\\n');
}}
function copyText(value) {{
  if (navigator.clipboard) navigator.clipboard.writeText(value);
}}
document.getElementById('stop').addEventListener('click', () => {{
  stopServer();
  window.close();
}});
document.getElementById('stop-drawer').addEventListener('click', () => {{
  stopServer();
  window.close();
}});
document.getElementById('refresh-frame').addEventListener('click', () => {{ frame.src = launch.url + (launch.url.includes('?') ? '&' : '?') + 'ionPreviewReload=' + Date.now(); }});
document.getElementById('reload-frame').addEventListener('click', () => {{ frame.src = launch.url + (launch.url.includes('?') ? '&' : '?') + 'ionPreviewReload=' + Date.now(); }});
document.getElementById('refresh-status').addEventListener('click', refreshStatus);
document.getElementById('capture-screen').addEventListener('click', captureScreen);
document.getElementById('copy-preview-url').addEventListener('click', () => copyText(window.location.href));
document.getElementById('copy-app-url').addEventListener('click', () => copyText(launch.url));
document.getElementById('open-side-by-side').addEventListener('click', () => {{
  window.open(launch.url, '_blank', 'noopener,noreferrer');
  window.open('/cockpit#codex', '_blank', 'noopener,noreferrer');
}});
window.addEventListener('pagehide', stopServer);
window.__ION_PROJECT_LAUNCH = launch;
applyViewport('fill');
</script>
"""
    return _launcher_html(f"{record.label} - ION Project Launch", body)


def _launcher_html(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{_html(title)}</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #050505;
      --panel: #0b0d0c;
      --panel-2: #101211;
      --line: #26342b;
      --line-strong: rgba(102, 204, 153, .62);
      --ok: #66cc99;
      --blue: #6699cc;
      --text: #eef4ef;
      --muted: #8e978e;
      --soft: #b8c2ba;
      --danger: #ff6c5c;
      background: var(--bg);
      color: var(--text);
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-height: 100vh; overflow: hidden; background: var(--bg); }}
    .ion-preview-shell {{
      position: relative;
      display: grid;
      grid-template-rows: 48px minmax(0, 1fr);
      height: 100vh;
      min-width: 0;
      overflow: hidden;
      background: #050505;
    }}
    .ion-preview-topbar {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      min-width: 0;
      border-bottom: 1px solid var(--line);
      background:
        linear-gradient(120deg, rgba(102, 204, 153, .10), transparent 34%),
        #090b0a;
      padding: 0 10px;
    }}
    .ion-preview-topbar > div {{ min-width: 0; }}
    h1 {{
      margin: 0;
      color: var(--text);
      font-size: 13px;
      line-height: 1.15;
      overflow: hidden;
      text-overflow: ellipsis;
      text-transform: uppercase;
      white-space: nowrap;
    }}
    span {{
      color: var(--muted);
      font-size: 8px;
      font-weight: 800;
      line-height: 1.25;
      text-transform: uppercase;
    }}
    b {{
      display: block;
      color: var(--text);
      font-size: 12px;
      line-height: 1.2;
      overflow-wrap: anywhere;
      text-transform: uppercase;
    }}
    p {{
      margin: 2px 0 0;
      color: var(--soft);
      font-size: 9px;
      line-height: 1.35;
      overflow-wrap: anywhere;
      text-transform: uppercase;
    }}
    .ion-preview-top-actions,
    .ion-preview-action-grid,
    .ion-preview-link-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      min-width: 0;
    }}
    a,
    button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 30px;
      border: 1px solid var(--line);
      background: #0a0a0a;
      color: var(--soft);
      cursor: pointer;
      font: inherit;
      font-size: 8px;
      font-weight: 800;
      letter-spacing: 0;
      padding: 0 10px;
      text-decoration: none;
      text-transform: uppercase;
    }}
    a:hover,
    button:hover,
    button.is-active {{
      border-color: var(--line-strong);
      color: var(--ok);
      box-shadow: 0 0 16px rgba(102, 204, 153, .14);
    }}
    .ion-preview-stage {{
      position: relative;
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
      gap: 8px;
      min-width: 0;
      min-height: 0;
      overflow: hidden;
      background: #050505;
      padding: 8px;
    }}
    .ion-preview-viewport-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      align-items: center;
      min-width: 0;
      border: 1px solid rgba(102, 204, 153, .18);
      background: #080a09;
      padding: 5px;
    }}
    .ion-preview-viewport-bar span {{
      margin-left: auto;
      color: var(--soft);
      font-size: 8px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .ion-preview-frame-shell {{
      justify-self: center;
      align-self: center;
      width: min(100%, 1440px);
      height: min(100%, 900px);
      max-width: 100%;
      max-height: 100%;
      min-width: 260px;
      min-height: 420px;
      overflow: hidden;
      border: 1px solid rgba(102, 153, 204, .30);
      background: #050505;
      box-shadow: 0 0 0 1px rgba(102, 153, 204, .10), 0 18px 60px rgba(0, 0, 0, .40);
    }}
    .ion-preview-frame-shell.is-fill {{
      width: 100%;
      height: 100%;
      min-width: 0;
      min-height: 0;
      border-color: transparent;
      box-shadow: none;
    }}
    .ion-preview-frame-shell:not(.is-fill) {{
      transform-origin: center center;
    }}
    iframe {{
      display: block;
      width: 100%;
      height: 100%;
      border: 0;
      background: #050505;
    }}
    .ion-preview-drawer-toggle {{
      position: fixed;
      z-index: 80;
      right: 14px;
      top: 62px;
      display: grid;
      place-items: center;
      width: 42px;
      height: 42px;
      min-height: 42px;
      border: 1px solid rgba(102, 204, 153, .50);
      background:
        radial-gradient(circle at 50% 30%, rgba(102, 204, 153, .22), transparent 58%),
        #080b09;
      color: var(--ok);
      box-shadow: 0 0 0 1px rgba(102, 204, 153, .12), 0 0 26px rgba(102, 204, 153, .16);
      padding: 0;
    }}
    .ion-preview-drawer-toggle span {{
      color: var(--ok);
      font-size: 11px;
    }}
    .ion-preview-drawer-toggle:hover {{
      color: #fff;
      border-color: rgba(255, 255, 255, .72);
      box-shadow: 0 0 0 1px rgba(102, 204, 153, .28), 0 0 34px rgba(102, 204, 153, .30);
    }}
    .ion-preview-ai-drawer {{
      position: fixed;
      z-index: 70;
      top: 48px;
      right: 0;
      display: grid;
      grid-template-rows: auto auto minmax(0, 1fr);
      gap: 8px;
      width: min(430px, calc(100vw - 18px));
      height: calc(100vh - 48px);
      min-width: 0;
      border-left: 1px solid rgba(102, 204, 153, .34);
      background:
        linear-gradient(160deg, rgba(102, 204, 153, .10), transparent 34%),
        #080a09;
      box-shadow: -28px 0 44px rgba(0, 0, 0, .46);
      padding: 9px;
      transform: translateX(calc(100% + 12px));
      transition: transform .16s ease;
    }}
    .ion-preview-ai-drawer.is-open {{ transform: translateX(0); }}
    .ion-preview-drawer-head {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 8px;
      align-items: center;
      min-width: 0;
    }}
    .ion-preview-drawer-tabs {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 4px;
      min-width: 0;
      border: 1px solid var(--line);
      background: #050505;
      padding: 4px;
    }}
    .ion-preview-drawer-tabs button {{ min-width: 0; padding: 0 5px; }}
    .ion-preview-drawer-panel {{
      display: none;
      align-content: start;
      gap: 8px;
      min-width: 0;
      overflow: auto;
    }}
    .ion-preview-drawer-panel.is-active {{ display: grid; }}
    .ion-preview-panel-title,
    .ion-preview-path-box,
    .ion-preview-status-grid > div {{
      display: grid;
      gap: 5px;
      min-width: 0;
      border: 1px solid var(--line);
      background: var(--panel-2);
      padding: 8px;
    }}
    .ion-preview-path-box:hover,
    .ion-preview-status-grid > div:hover,
    .ion-preview-panel-title:hover {{
      border-color: rgba(102, 204, 153, .44);
    }}
    .ion-preview-link-grid,
    .ion-preview-action-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
    .ion-preview-link-grid a,
    .ion-preview-action-grid a,
    .ion-preview-action-grid button {{ width: 100%; min-width: 0; }}
    .ion-preview-status-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 6px;
      min-width: 0;
    }}
    code {{
      color: var(--muted);
      font-size: 8px;
      line-height: 1.35;
      overflow-wrap: anywhere;
      white-space: pre-wrap;
    }}
    #capture-image {{
      width: 100%;
      aspect-ratio: 16 / 10;
      border: 1px solid rgba(102, 153, 204, .34);
      background: #050505;
      object-fit: cover;
    }}
    .ion-preview-log {{
      min-height: 108px;
      max-height: 38vh;
      margin: 0;
      overflow: auto;
      border: 1px solid var(--line);
      background: #040504;
      color: var(--soft);
      font: inherit;
      font-size: 8px;
      line-height: 1.45;
      padding: 8px;
      white-space: pre-wrap;
    }}
    @media (max-width: 720px) {{
      .ion-preview-topbar {{ grid-template-columns: 1fr; height: auto; min-height: 78px; align-content: center; }}
      .ion-preview-shell {{ grid-template-rows: minmax(78px, auto) minmax(0, 1fr); }}
      .ion-preview-ai-drawer {{ top: 78px; height: calc(100vh - 78px); }}
      .ion-preview-drawer-toggle {{ top: 92px; right: 10px; }}
      .ion-preview-status-grid,
      .ion-preview-link-grid,
      .ion-preview-action-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
{body}
</body>
</html>"""


def _authorized_project_path(shell_root: Path, raw_path: str) -> Path | None:
    if not raw_path:
        return None
    try:
        path = Path(raw_path).expanduser().resolve()
    except Exception:
        return None
    if not path.exists() or not path.is_dir():
        return None
    roots = [
        shell_root,
        _env_path("ION_COSMOS_ROOT"),
        _env_path("ION_COSMOS_WORKSPACE_ROOT"),
        _env_path("ION_APPLICATION_DEV_ROOT"),
        shell_root / "Cosmos",
        shell_root.parent / "Cosmos",
        Path.home() / "Cosmos",
        shell_root.parent / "Application_Dev",
        Path.home() / "Application_Dev",
        Path.home() / "ION_PROJECTS_PROFESSIONAL_ORGANIZED_CANDIDATE",
    ]
    for root in roots:
        if not root:
            continue
        try:
            path.relative_to(root.expanduser().resolve())
            return path
        except Exception:
            continue
    return None


def _env_path(name: str) -> Path | None:
    value = os.environ.get(name)
    return Path(value).expanduser() if value else None


def _detect_framework(path: Path, scripts: Mapping[str, Any], markers: list[str] | tuple[str, ...] = ()) -> str:
    marker_set = set(markers)
    script_text = " ".join(compact(value).lower() for value in scripts.values())
    if any(name in marker_set for name in ("next.config.js", "next.config.mjs", "next.config.ts")) or any((path / name).exists() for name in ("next.config.js", "next.config.mjs", "next.config.ts")) or "next" in script_text:
        return "next"
    if any(name.startswith("vite.config") for name in marker_set) or any((path / name).exists() for name in ("vite.config.js", "vite.config.mjs", "vite.config.ts")) or "vite" in script_text:
        return "vite"
    if (path / "index.html").exists():
        return "static"
    if (path / "app").is_dir() and any(child.suffix.lower() in {".html", ".htm"} for child in (path / "app").glob("*.html")):
        return "static"
    if scripts.get("serve") and "http.server" in compact(scripts.get("serve")).lower():
        return "static"
    if scripts.get("dev") or scripts.get("start"):
        return "node"
    return "metadata"


def _launch_command(path: Path, framework: str, port: int) -> list[str] | None:
    package_json = read_json(path / "package.json")
    scripts = package_json.get("scripts") if isinstance(package_json.get("scripts"), Mapping) else {}
    if framework == "next":
        next_bin = path / "node_modules/next/dist/bin/next"
        if next_bin.exists():
            return ["node", next_bin.as_posix(), "dev", "--hostname", HOST, "--port", str(port)]
        if scripts.get("dev"):
            return ["npm", "run", "dev", "--", "--hostname", HOST, "--port", str(port)]
        return ["npx", "next", "dev", "--hostname", HOST, "--port", str(port)]
    if framework == "vite" and (path / "package.json").exists():
        if scripts.get("dev"):
            return ["npm", "run", "dev", "--", "--host", HOST, "--port", str(port)]
        return ["npx", "vite", "--host", HOST, "--port", str(port)]
    if framework == "static":
        app_dir = path / "app"
        if app_dir.exists() and app_dir.is_dir():
            return ["python3", "-m", "http.server", str(port), "--bind", HOST, "--directory", "app"]
        if (path / "index.html").exists():
            return ["python3", "-m", "http.server", str(port), "--bind", HOST]
        if scripts.get("serve"):
            return ["npm", "run", "serve"]
        return ["python3", "-m", "http.server", str(port), "--bind", HOST]
    if scripts.get("dev"):
        return ["npm", "run", "dev"]
    if scripts.get("start"):
        return ["npm", "start"]
    return None


def _spawn_install_then_launch(record: LaunchRecord, path: Path) -> None:
    log = Path(record.log_path)
    stream = log.open("ab")
    installer = subprocess.Popen(
        ["npm", "install"],
        cwd=path,
        env={**os.environ, "BROWSER": "none", "PORT": str(record.port), "HOST": HOST},
        stdout=stream,
        stderr=stream,
        start_new_session=True,
    )
    record.process = installer
    record.state = "installing"
    record.message = "installing or repairing dependencies"
    record.updated_at = utc_now()

    def waiter() -> None:
        code = installer.wait()
        stream.flush()
        stream.close()
        if code != 0:
            with _LOCK:
                record.state = "install_failed"
                record.message = f"npm install failed with exit code {code}"
                record.exit_code = code
                record.updated_at = utc_now()
            return
        _spawn_dev_server(record, path, record.command)

    threading.Thread(target=waiter, name=f"ion-project-install-{record.launch_id}", daemon=True).start()


def _spawn_dev_server(record: LaunchRecord, path: Path, command: list[str]) -> None:
    log = Path(record.log_path)
    stream = log.open("ab")
    process = subprocess.Popen(
        command,
        cwd=path,
        env={**os.environ, "BROWSER": "none", "PORT": str(record.port), "HOST": HOST},
        stdout=stream,
        stderr=stream,
        start_new_session=True,
    )
    with _LOCK:
        record.process = process
        record.state = "running"
        record.message = f"{record.label} is running at {record.url}"
        record.updated_at = utc_now()

    def waiter() -> None:
        code = process.wait()
        stream.flush()
        stream.close()
        with _LOCK:
            record.exit_code = code
            record.state = "stopped"
            record.message = f"{record.label} stopped with exit code {code}"
            record.updated_at = utc_now()

    threading.Thread(target=waiter, name=f"ion-project-dev-{record.launch_id}", daemon=True).start()


def _terminate_record(record: LaunchRecord) -> None:
    process = record.process
    if process and process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except Exception:
            process.terminate()
        try:
            process.wait(timeout=4)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except Exception:
                process.kill()
    with _LOCK:
        record.state = "stopped"
        record.message = f"{record.label} stopped"
        record.exit_code = process.poll() if process else record.exit_code
        record.updated_at = utc_now()


def _record_running(record: LaunchRecord) -> bool:
    process = record.process
    if not process:
        return record.state in {"installing", "starting", "running"}
    poll = process.poll()
    if poll is None:
        return True
    if record.state not in {"stopped", "install_failed", "failed"}:
        record.state = "stopped"
        record.exit_code = poll
        record.message = f"{record.label} stopped with exit code {poll}"
        record.updated_at = utc_now()
    return False


def _record_payload(shell_root: Path, record: LaunchRecord) -> dict[str, Any]:
    running = _record_running(record)
    return {
        "launch_id": record.launch_id,
        "project_id": record.project_id,
        "version_id": record.version_id,
        "label": record.label,
        "path": record.path,
        "framework": record.framework,
        "command": record.command,
        "url": record.url,
        "open_href": _open_href(record),
        "port": record.port,
        "state": record.state,
        "message": record.message,
        "running": running,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
        "exit_code": record.exit_code,
        "log_path": record.log_path,
        "log_tail": _tail(record.log_path),
        "managed_window_stops_server": True,
        "stop_path": "/cockpit/projects/launch/stop",
        "status_path": "/cockpit/projects/launch/status",
        "diagnostics_path": "/cockpit/projects/launch/diagnostics",
        "diagnostics_event_path": "/cockpit/projects/launch/diagnostics/event",
        "instrumented_open_href": f"/cockpit/projects/launch/proxy/{record.launch_id}/",
    }


def project_launcher_proxy_fetch(root: str | Path, launch_id: str, proxy_path: str, query: str = "", method: str = "GET", body: bytes = b"", headers: Mapping[str, str] | None = None) -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    safe_launch_id = compact(launch_id)
    with _LOCK:
        record = _LAUNCHES.get(safe_launch_id)
    if not record:
        return {"ok": False, "status": 404, "content_type": "application/json", "body": json.dumps({"ok": False, "finding": "launch_not_found"}).encode("utf-8")}
    if not _record_running(record):
        return {"ok": False, "status": 409, "content_type": "application/json", "body": json.dumps({"ok": False, "finding": "launch_not_running"}).encode("utf-8")}

    target_path = proxy_path.lstrip("/")
    target = urljoin(record.url.rstrip("/") + "/", target_path)
    if query:
        target = target + ("&" if "?" in target else "?") + query
    parsed = urlparse(target)
    if parsed.hostname not in {HOST, "localhost", "127.0.0.1"}:
        return {"ok": False, "status": 403, "content_type": "application/json", "body": json.dumps({"ok": False, "finding": "proxy_target_not_local"}).encode("utf-8")}

    request_headers = {
        "User-Agent": "ION-App-Diagnostics-Proxy/1.0",
        "Accept": compact((headers or {}).get("Accept"), "*/*"),
    }
    content_type = compact((headers or {}).get("Content-Type"))
    if content_type:
        request_headers["Content-Type"] = content_type
    try:
        req = Request(target, data=body if method.upper() not in {"GET", "HEAD"} else None, headers=request_headers, method=method.upper())
        with urlopen(req, timeout=20) as response:  # noqa: S310 - local loopback proxy only, target is constrained above.
            raw = response.read()
            response_type = compact(response.headers.get("Content-Type"), "application/octet-stream")
            status = int(getattr(response, "status", 200))
    except HTTPError as exc:
        raw = exc.read()
        response_type = compact(exc.headers.get("Content-Type"), "text/plain")
        status = int(exc.code)
    except URLError as exc:
        return {"ok": False, "status": 502, "content_type": "application/json", "body": json.dumps({"ok": False, "finding": "proxy_fetch_failed", "error": exc.__class__.__name__}).encode("utf-8")}

    response_type_lower = response_type.lower()
    if "text/html" in response_type_lower:
        text = raw.decode("utf-8", errors="replace")
        text = _rewrite_html_for_diagnostics_proxy(shell_root, text, record)
        raw = text.encode("utf-8")
        response_type = "text/html; charset=utf-8"
    elif "javascript" in response_type_lower or proxy_path.endswith(".js") or proxy_path.endswith(".mjs") or proxy_path.startswith("@vite/"):
        text = raw.decode("utf-8", errors="replace")
        text = _rewrite_javascript_for_diagnostics_proxy(text, record)
        raw = text.encode("utf-8")
        if not response_type:
            response_type = "application/javascript; charset=utf-8"
    return {"ok": 200 <= status < 400, "status": status, "content_type": response_type, "body": raw, "record": _record_payload(shell_root, record)}


def _rewrite_html_for_diagnostics_proxy(shell_root: Path, html: str, record: LaunchRecord) -> str:
    base = f"/cockpit/projects/launch/proxy/{record.launch_id}/"
    script = _browser_probe_script(shell_root, record)
    rewritten = html.replace('src="/', f'src="{base}', 200).replace("src='/", f"src='{base}", 200)
    rewritten = rewritten.replace('href="/', f'href="{base}', 200).replace("href='/", f"href='{base}", 200)
    rewritten = rewritten.replace('action="/', f'action="{base}', 100).replace("action='/", f"action='{base}", 100)
    injection = f'<base href="{base}"><script>{script}</script>'
    lower = rewritten.lower()
    head_index = lower.find("<head")
    if head_index >= 0:
        close = lower.find(">", head_index)
        if close >= 0:
            return rewritten[: close + 1] + injection + rewritten[close + 1 :]
    body_index = lower.find("<body")
    if body_index >= 0:
        close = lower.find(">", body_index)
        if close >= 0:
            return rewritten[: close + 1] + injection + rewritten[close + 1 :]
    return injection + rewritten


def _rewrite_javascript_for_diagnostics_proxy(source: str, record: LaunchRecord) -> str:
    base = f"/cockpit/projects/launch/proxy/{record.launch_id}/"
    rewritten = source
    replacements = (
        ('from "/', f'from "{base}'),
        ("from '/", f"from '{base}"),
        ('import "/', f'import "{base}'),
        ("import '/", f"import '{base}"),
        ('import("/', f'import("{base}'),
        ("import('/", f"import('{base}"),
        ('__vite__injectQuery("/', f'__vite__injectQuery("{base}'),
        ("__vite__injectQuery('/", f"__vite__injectQuery('{base}"),
    )
    for needle, replacement in replacements:
        rewritten = rewritten.replace(needle, replacement)
    return rewritten


def _browser_probe_script(shell_root: Path, record: LaunchRecord) -> str:
    diagnostics_config = read_json(shell_root / APP_DIAGNOSTICS_CONFIG_PATH)
    adapter_options = diagnostics_config.get("adapter_options") if isinstance(diagnostics_config.get("adapter_options"), Mapping) else {}
    feature_flags = {
        "reactDevtoolsCommitHook": bool(adapter_options.get("react_devtools_commit_hook")),
        "webglGetErrorProbe": bool(adapter_options.get("webgl_get_error_probe")),
        "webgpuRequestPatch": bool(adapter_options.get("webgpu_request_patch")),
    }
    return f"""
(() => {{
  if (window.__ION_APP_DIAG_INSTALLED__) return;
  window.__ION_APP_DIAG_INSTALLED__ = true;
  const launchId = {json.dumps(record.launch_id)};
  const eventUrl = '/cockpit/projects/launch/diagnostics/event';
  const config = {{ schema: 'ion.browser_diagnostics_probe.v2', maxEvents: 2600, maxString: 1400, resourceBuffer: 1800 }};
  const featureFlags = {json.dumps(feature_flags, sort_keys=True)};
  let seq = 0;
  let dropped = 0;
  let lastEmitSecond = 0;
  let emitsThisSecond = 0;
  const deny = /token|secret|password|authorization|bearer|cookie|session|api[_-]?key|credential|jwt/i;
  const sanitizeUrl = (value) => {{
    try {{
      const url = new URL(String(value), location.href);
      return {{ origin: url.origin, path: url.pathname, url: url.origin + url.pathname, redacted_query: Boolean(url.search), redacted_hash: Boolean(url.hash) }};
    }} catch (_error) {{
      return {{ origin: '', path: String(value || '').slice(0, 160), url: '[unparseable-url]' }};
    }}
  }};
  const safe = (value, depth = 0) => {{
    if (depth > 3) return '[depth-limit]';
    if (value == null || typeof value === 'number' || typeof value === 'boolean') return value;
    if (typeof value === 'string') {{
      if (deny.test(value.slice(0, 160))) return '[REDACTED]';
      return value.length > config.maxString ? value.slice(0, config.maxString) + ' ...[truncated]' : value;
    }}
    if (Array.isArray(value)) return value.slice(0, 40).map((item) => safe(item, depth + 1));
    if (typeof value === 'object') {{
      const out = {{}};
      for (const [key, item] of Object.entries(value).slice(0, 80)) {{
        out[key] = deny.test(key) ? '[REDACTED]' : safe(item, depth + 1);
      }}
      return out;
    }}
    return String(value);
  }};
  const emit = (eventType, detail = {{}}, severity = 'info', summary = '') => {{
    try {{
      const nowSecond = Math.floor(Date.now() / 1000);
      if (nowSecond !== lastEmitSecond) {{ lastEmitSecond = nowSecond; emitsThisSecond = 0; }}
      emitsThisSecond += 1;
      if (seq >= config.maxEvents || emitsThisSecond > 80) {{
        dropped += 1;
        return;
      }}
      const locationBits = sanitizeUrl(location.href);
      const payload = {{
        launch_id: launchId,
        event_type: eventType,
        severity,
        summary: summary || eventType,
        detail,
        url: locationBits.url,
        path: locationBits.path,
        source_kind: 'browser',
        seq: ++seq,
        timestamp_ms: Math.round(performance.now()),
        time_origin_ms: Math.round(performance.timeOrigin || 0),
        dropped_events: dropped,
        probe_version: config.schema
      }};
      const body = JSON.stringify(safe(payload));
      if (navigator.sendBeacon) {{
        const ok = navigator.sendBeacon(eventUrl, new Blob([body], {{ type: 'application/json' }}));
        if (ok) return;
      }}
      fetch(eventUrl, {{ method: 'POST', headers: {{ 'Content-Type': 'application/json' }}, body, keepalive: true }}).catch(() => undefined);
    }} catch (_error) {{}}
  }};
  const disposers = [];
  window.__ION_APP_DIAG__ = {{ emit, launchId, mode: config.schema, sanitizeUrl, disposers, dispose: () => {{ while (disposers.length) {{ try {{ disposers.pop()(); }} catch (_error) {{}} }} emit('probe_disposed', {{ disposed: true }}); }} }};

  emit('probe_installed', {{ userAgent: navigator.userAgent, viewport: [innerWidth, innerHeight], href: sanitizeUrl(location.href), supported: {{ performanceObserver: 'PerformanceObserver' in window, reportingObserver: 'ReportingObserver' in window, sendBeacon: 'sendBeacon' in navigator }}, feature_flags: featureFlags }});

  try {{
    if (performance.setResourceTimingBufferSize) performance.setResourceTimingBufferSize(config.resourceBuffer);
    addEventListener('resourcetimingbufferfull', () => {{
      emit('resource_timing_buffer_full', {{ configured_size: config.resourceBuffer }}, 'warn');
      try {{ performance.clearResourceTimings(); }} catch (_error) {{}}
    }});
  }} catch (_error) {{}}

  const originalConsole = {{}};
  for (const level of ['log', 'info', 'warn', 'error', 'debug']) {{
    originalConsole[level] = console[level];
    console[level] = (...args) => {{
      emit('console_' + level, {{ args: args.map((arg) => typeof arg === 'string' ? arg : safe(arg)), arg_count: args.length }}, level === 'error' ? 'error' : level === 'warn' ? 'warn' : 'info');
      return originalConsole[level].apply(console, args);
    }};
  }}

  addEventListener('error', (event) => emit('window_error', {{ message: event.message, filename: sanitizeUrl(event.filename || '').url, lineno: event.lineno, colno: event.colno }}, 'error', event.message));
  addEventListener('unhandledrejection', (event) => emit('unhandled_rejection', {{ reason: safe(event.reason) }}, 'error'));
  addEventListener('visibilitychange', () => {{ emit('visibility_change', {{ state: document.visibilityState }}); flushVitals('visibility_change'); }});
  addEventListener('focus', () => emit('window_focus', {{ focused: true }}));
  addEventListener('blur', () => emit('window_blur', {{ focused: false }}));
  addEventListener('pagehide', () => flushVitals('pagehide'));
  addEventListener('beforeunload', () => {{ flushVitals('before_unload'); emit('before_unload', {{ href: sanitizeUrl(location.href) }}); }});

  const requestInfo = (input, init) => {{
    const raw = typeof input === 'string' ? input : input && input.url ? input.url : String(input);
    const method = (init && init.method) || (input && input.method) || 'GET';
    const target = sanitizeUrl(raw);
    return {{ method: String(method).toUpperCase(), target, mode: init && init.mode, credentials: init && init.credentials }};
  }};
  const originalFetch = window.fetch;
  window.fetch = async (...args) => {{
    const started = performance.now();
    const info = requestInfo(args[0], args[1] || {{}});
    emit('fetch_start', {{ method: info.method, target: info.target, mode: info.mode, credentials: info.credentials }});
    try {{
      const response = await originalFetch.apply(window, args);
      emit('fetch_end', {{ method: info.method, target: info.target, status: response.status, ok: response.ok, duration_ms: Math.round(performance.now() - started), type: response.type, redirected: response.redirected }}, response.ok ? 'info' : 'warn');
      return response;
    }} catch (error) {{
      emit('fetch_error', {{ method: info.method, target: info.target, error: String(error), duration_ms: Math.round(performance.now() - started) }}, 'error');
      throw error;
    }}
  }};

  const OriginalXHR = window.XMLHttpRequest;
  window.XMLHttpRequest = function IonDiagXHR() {{
    const xhr = new OriginalXHR();
    let method = 'GET';
    let target = {{ url: '', path: '', origin: '' }};
    let started = 0;
    const open = xhr.open;
    xhr.open = function patchedOpen(m, u, ...rest) {{ method = String(m || 'GET').toUpperCase(); target = sanitizeUrl(u); return open.call(xhr, m, u, ...rest); }};
    const send = xhr.send;
    xhr.send = function patchedSend(...args) {{
      started = performance.now();
      emit('xhr_start', {{ target, method }});
      xhr.addEventListener('loadend', () => emit('xhr_end', {{ target, method, status: xhr.status, duration_ms: Math.round(performance.now() - started) }}, xhr.status >= 400 ? 'warn' : 'info'));
      xhr.addEventListener('error', () => emit('xhr_error', {{ target, method, duration_ms: Math.round(performance.now() - started) }}, 'error'));
      xhr.addEventListener('abort', () => emit('xhr_abort', {{ target, method, duration_ms: Math.round(performance.now() - started) }}, 'warn'));
      return send.apply(xhr, args);
    }};
    return xhr;
  }};

  const vitals = {{ lcp: null, cls: 0, inp: null, fid: null }};
  const flushVitals = (reason) => {{
    if (vitals.lcp) emit('web_vital_lcp', {{ value: Math.round(vitals.lcp.startTime), element: vitals.lcp.element ? vitals.lcp.element.tagName : undefined, reason }}, 'info');
    emit('web_vital_cls', {{ value: Number(vitals.cls.toFixed(4)), reason }}, vitals.cls > 0.1 ? 'warn' : 'info');
    if (vitals.inp) emit('web_vital_inp_candidate', {{ value: Math.round(vitals.inp.duration), name: vitals.inp.name, startTime: Math.round(vitals.inp.startTime), reason }}, vitals.inp.duration > 200 ? 'warn' : 'info');
    if (vitals.fid) emit('web_vital_fid', {{ value: Math.round(vitals.fid.processingStart - vitals.fid.startTime), reason }}, 'info');
  }};

  const observePerformance = (type, handler, options = {{ type, buffered: true }}) => {{
    if (!('PerformanceObserver' in window)) return;
    try {{ new PerformanceObserver((list) => handler(list.getEntries())).observe(options); }} catch (_error) {{}}
  }};
  observePerformance('largest-contentful-paint', (entries) => {{
    const entry = entries[entries.length - 1];
    if (!entry) return;
    vitals.lcp = entry;
    emit('web_vital_lcp_candidate', {{ value: Math.round(entry.startTime), size: entry.size, url: entry.url ? sanitizeUrl(entry.url) : undefined }});
  }});
  observePerformance('layout-shift', (entries) => {{
    for (const entry of entries) {{ if (!entry.hadRecentInput) vitals.cls += entry.value || 0; }}
    emit('web_vital_cls_candidate', {{ value: Number(vitals.cls.toFixed(4)) }}, vitals.cls > 0.1 ? 'warn' : 'info');
  }});
  observePerformance('event', (entries) => {{
    for (const entry of entries) {{
      if (!vitals.inp || (entry.duration || 0) > vitals.inp.duration) vitals.inp = entry;
    }}
    if (vitals.inp) emit('web_vital_inp_candidate', {{ value: Math.round(vitals.inp.duration || 0), name: vitals.inp.name, interactionId: vitals.inp.interactionId || 0 }}, (vitals.inp.duration || 0) > 200 ? 'warn' : 'info');
  }}, {{ type: 'event', buffered: true, durationThreshold: 40 }});
  observePerformance('first-input', (entries) => {{ const entry = entries[0]; if (entry) vitals.fid = entry; }});

  for (const type of ['longtask', 'long-animation-frame', 'resource', 'navigation', 'paint', 'mark', 'measure']) {{
    observePerformance(type, (entries) => {{
      for (const entry of entries.slice(-25)) {{
        const nameBits = type === 'resource' ? sanitizeUrl(entry.name) : {{ url: safe(entry.name) }};
        emit('performance_' + type.replace(/-/g, '_'), {{ name: nameBits, entryType: entry.entryType, startTime: Math.round(entry.startTime || 0), duration: Math.round(entry.duration || 0), initiatorType: entry.initiatorType, transferSize: entry.transferSize, decodedBodySize: entry.decodedBodySize }});
      }}
    }});
  }}

  if ('ReportingObserver' in window) {{
    try {{
      const observer = new ReportingObserver((reports) => {{
        for (const report of reports) emit('browser_report_' + report.type, {{ type: report.type, url: report.url ? sanitizeUrl(report.url) : undefined, body: safe(report.body) }}, report.type === 'crash' ? 'error' : 'warn');
      }}, {{ buffered: true }});
      observer.observe();
      emit('reporting_observer_installed', {{ buffered: true }});
    }} catch (_error) {{}}
  }} else {{
    emit('reporting_observer_unavailable', {{ supported: false }});
  }}

  let mutationCount = 0;
  try {{
    new MutationObserver((mutations) => {{
      mutationCount += mutations.length;
      if (mutationCount % 100 < mutations.length) emit('dom_mutation_batch', {{ mutation_count: mutationCount, latest_batch: mutations.length }});
    }}).observe(document.documentElement, {{ childList: true, subtree: true, attributes: true }});
  }} catch (_error) {{}}

  let lastFrame = performance.now();
  let slowFrames = 0;
  const raf = () => {{
    const now = performance.now();
    const delta = now - lastFrame;
    if (delta > 80) {{
      slowFrames += 1;
      emit('slow_frame', {{ delta_ms: Math.round(delta), slow_frame_count: slowFrames }}, delta > 250 ? 'warn' : 'info');
    }}
    lastFrame = now;
    requestAnimationFrame(raf);
  }};
  requestAnimationFrame(raf);

  const patchWebGL = (name) => {{
    const proto = window[name] && window[name].prototype;
    if (!proto || proto.__ION_DIAG_PATCHED__) return;
    proto.__ION_DIAG_PATCHED__ = true;
    for (const method of ['drawArrays', 'drawElements', 'texImage2D', 'compileShader', 'linkProgram']) {{
      const original = proto[method];
      if (typeof original !== 'function') continue;
      let count = 0;
      proto[method] = function patchedWebGL(...args) {{
        count += 1;
        if (count <= 20 || count % 120 === 0) emit('webgl_' + method, {{ args_count: args.length, sample_count: count }});
        return original.apply(this, args);
      }};
    }}
    const getError = proto.getError;
    if (featureFlags.webglGetErrorProbe && typeof getError === 'function') {{
      proto.getError = function patchedGetError(...args) {{
        const code = getError.apply(this, args);
        if (code) emit('webgl_error', {{ code }}, 'warn');
        return code;
      }};
    }} else {{
      emit('webgl_get_error_probe_disabled', {{ context: name, reason: 'destructive_probe_requires_explicit_adapter_option' }});
    }}
  }};
  const installReactAdapter = () => {{
    const hook = window.__REACT_DEVTOOLS_GLOBAL_HOOK__;
    if (!hook || hook.__ION_DIAG_PATCHED__) {{
      emit('react_adapter_unavailable', {{ reason: hook ? 'already_patched' : 'react_devtools_hook_missing' }});
      return;
    }}
    if (!featureFlags.reactDevtoolsCommitHook) {{
      emit('react_adapter_observed', {{ hook: 'react_devtools_global_hook', mode: 'passive_presence_only', commit_hook_patch: false }});
      return;
    }}
    hook.__ION_DIAG_PATCHED__ = true;
    const originalCommit = hook.onCommitFiberRoot;
    hook.onCommitFiberRoot = function ionCommitFiberRoot(rendererId, root, ...rest) {{
      try {{
        const current = root && root.current;
        emit('react_profiler_commit', {{ renderer_id: String(rendererId), root_tag: current && current.tag, child_tag: current && current.child && current.child.tag, pending_lanes: root && root.pendingLanes }}, 'info');
      }} catch (_error) {{}}
      return typeof originalCommit === 'function' ? originalCommit.call(this, rendererId, root, ...rest) : undefined;
    }};
    emit('react_adapter_installed', {{ hook: 'react_devtools_global_hook' }});
  }};
  installReactAdapter();

  const installThreeAdapter = () => {{
    const observed = new WeakSet();
    window.__ION_APP_DIAG__.registerThreeRenderer = (renderer, label = 'registered') => {{
      try {{
        if (!renderer || observed.has(renderer)) return false;
        observed.add(renderer);
        let sampleCount = 0;
        const sample = () => {{
          if (sampleCount > 300) return;
          sampleCount += 1;
          const info = renderer.info || {{}};
          emit('three_renderer_sample', {{ label: safe(label), sample_count: sampleCount, render: safe(info.render || {{}}), memory: safe(info.memory || {{}}), programs: info.programs ? info.programs.length : undefined, pixel_ratio: renderer.getPixelRatio ? renderer.getPixelRatio() : undefined, size: renderer.getSize ? safe(renderer.getSize({{}})) : undefined }}, 'info');
        }};
        sample();
        const timer = setInterval(sample, 1000);
        if (window.__ION_APP_DIAG__.disposers) window.__ION_APP_DIAG__.disposers.push(() => clearInterval(timer));
        emit('three_renderer_registered', {{ label: safe(label) }});
        return true;
      }} catch (error) {{
        emit('three_renderer_register_failed', {{ error: String(error) }}, 'warn');
        return false;
      }}
    }};
    emit('three_adapter_ready', {{ mode: 'explicit_register_renderer_only', global_three_present: Boolean(window.THREE) }});
  }};
  installThreeAdapter();

  const installR3FAdapter = () => {{
    const roots = window.__r3f || window.__REACT_THREE_FIBER__;
    if (!roots) {{
      emit('r3f_adapter_unavailable', {{ reason: 'no_known_global_r3f_root' }});
      return;
    }}
    emit('r3f_adapter_observed', {{ root_type: typeof roots, keys: roots && typeof roots === 'object' ? Object.keys(roots).slice(0, 20) : [] }});
  }};
  installR3FAdapter();

  const installWebGPUAdapter = () => {{
    if (!navigator.gpu || navigator.gpu.__ION_DIAG_PATCHED__) {{
      emit('webgpu_adapter_unavailable', {{ reason: navigator.gpu ? 'already_patched' : 'navigator_gpu_missing' }});
      return;
    }}
    if (!featureFlags.webgpuRequestPatch) {{
      emit('webgpu_adapter_observed', {{ available: true, mode: 'passive_presence_only', request_patch: false }});
      return;
    }}
    navigator.gpu.__ION_DIAG_PATCHED__ = true;
    const originalRequestAdapter = navigator.gpu.requestAdapter && navigator.gpu.requestAdapter.bind(navigator.gpu);
    if (!originalRequestAdapter) return;
    navigator.gpu.requestAdapter = async (...args) => {{
      emit('webgpu_request_adapter', {{ args_count: args.length }});
      const adapter = await originalRequestAdapter(...args);
      if (adapter && adapter.requestDevice && !adapter.__ION_DIAG_PATCHED__) {{
        adapter.__ION_DIAG_PATCHED__ = true;
        const originalRequestDevice = adapter.requestDevice.bind(adapter);
        adapter.requestDevice = async (...deviceArgs) => {{
          emit('webgpu_request_device', {{ args_count: deviceArgs.length, features: adapter.features ? Array.from(adapter.features).slice(0, 30) : [] }});
          const device = await originalRequestDevice(...deviceArgs);
          try {{
            device.lost && device.lost.then((info) => emit('webgpu_device_lost', {{ reason: info && info.reason, message: info && info.message }}, 'error'));
            device.addEventListener && device.addEventListener('uncapturederror', (event) => emit('webgpu_uncaptured_error', {{ error: safe(event.error) }}, 'error'));
          }} catch (_error) {{}}
          return device;
        }};
      }}
      return adapter;
    }};
    emit('webgpu_adapter_installed', {{ available: true, mode: 'request_and_device_observation_only' }});
  }};
  installWebGPUAdapter();

  patchWebGL('WebGLRenderingContext');
  patchWebGL('WebGL2RenderingContext');
  addEventListener('webglcontextlost', (event) => emit('webgl_context_lost', {{ target: event.target?.tagName }}, 'error'));
  addEventListener('webglcontextrestored', (event) => emit('webgl_context_restored', {{ target: event.target?.tagName }}, 'info'));
}})();
"""


def _capture_launch_screenshot(shell_root: Path, record: LaunchRecord, payload: Mapping[str, Any]) -> dict[str, Any]:
    if not _record_running(record):
        return {"ok": False, "status": "not_running", "finding": "launch_not_running"}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_launch_id = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in record.launch_id)
    screenshot_dir = shell_root / PROJECT_LAUNCHER_SCREENSHOTS_DIR
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = screenshot_dir / f"{stamp}_{safe_launch_id}.png"
    width = _payload_int(payload, "width", 1365)
    height = _payload_int(payload, "height", 900)
    timeout_ms = _payload_int(payload, "timeout_ms", 15_000)
    capture = _capture_playwright(record.url, screenshot_path, width=width, height=height, timeout_ms=timeout_ms)
    if not capture.get("ok"):
        return {
            "ok": False,
            "status": "capture_failed",
            "finding": capture.get("finding", "playwright_capture_failed"),
            "error": capture.get("error"),
            "screenshot_path": screenshot_path.as_posix(),
        }
    return {
        "ok": True,
        "status": "captured",
        "url": record.url,
        "screenshot_path": screenshot_path.as_posix(),
        "screenshot_href": f"/cockpit/projects/launch/screenshot/{screenshot_path.name}",
        "viewport": {"width": width, "height": height},
        "page_status": capture.get("page_status"),
        "console": capture.get("console", []),
    }


def _payload_int(payload: Mapping[str, Any], key: str, default: int) -> int:
    try:
        value = int(payload.get(key) or default)
    except (TypeError, ValueError):
        return default
    return max(1, min(value, 10_000))


def _capture_playwright(url: str, screenshot_path: Path, *, width: int, height: int, timeout_ms: int, wait_ms: int = 500) -> dict[str, Any]:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            console: list[dict[str, str]] = []
            page.on("console", lambda message: console.append({"type": message.type, "text": message.text[:500]}))
            response = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            page.wait_for_timeout(wait_ms)
            page.screenshot(path=screenshot_path.as_posix(), full_page=True)
            browser.close()
        return {
            "ok": True,
            "page_status": getattr(response, "status", None) if response else None,
            "console": console[-20:],
        }
    except Exception as exc:
        fallback = _capture_playwright_subprocess(url, screenshot_path, width=width, height=height, timeout_ms=timeout_ms, wait_ms=wait_ms)
        if fallback.get("ok"):
            return fallback
        return {
            "ok": False,
            "finding": fallback.get("finding", "playwright_capture_failed"),
            "error": fallback.get("error") or exc.__class__.__name__,
        }


def _capture_playwright_subprocess(url: str, screenshot_path: Path, *, width: int, height: int, timeout_ms: int, wait_ms: int = 500) -> dict[str, Any]:
    script = r"""
import json
import sys
url, path, width, height, timeout, wait_ms = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
        console = []
        page.on("console", lambda message: console.append({"type": message.type, "text": message.text[:500]}))
        response = page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        page.wait_for_timeout(wait_ms)
        page.screenshot(path=path, full_page=True)
        browser.close()
    print(json.dumps({"ok": True, "page_status": getattr(response, "status", None) if response else None, "console": console[-20:]}))
except Exception as exc:
    print(json.dumps({"ok": False, "finding": "playwright_subprocess_capture_failed", "error": exc.__class__.__name__}))
"""
    candidates = [
        sys.executable,
        shutil.which("python3") or "",
        "/home/sev/miniconda/bin/python3",
        "/usr/bin/python3",
    ]
    seen: set[str] = set()
    last_payload: dict[str, Any] = {"ok": False, "finding": "playwright_subprocess_unavailable"}
    for candidate in candidates:
        if not candidate or candidate in seen or not Path(candidate).exists():
            continue
        seen.add(candidate)
        try:
            completed = subprocess.run(
                [candidate, "-c", script, url, screenshot_path.as_posix(), str(width), str(height), str(timeout_ms), str(wait_ms)],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=max(5, int(timeout_ms / 1000) + 10),
                text=True,
            )
        except Exception as exc:
            last_payload = {"ok": False, "finding": "playwright_subprocess_unavailable", "error": exc.__class__.__name__, "python": candidate}
            continue
        try:
            payload = json.loads((completed.stdout or "{}").strip().splitlines()[-1])
        except Exception:
            payload = {"ok": False, "finding": "playwright_subprocess_output_invalid"}
        if completed.returncode != 0 and not payload.get("ok"):
            payload.setdefault("error", (completed.stderr or "").strip()[:400] or f"exit_{completed.returncode}")
        if isinstance(payload, dict):
            payload["python"] = candidate
            if payload.get("ok"):
                return payload
            last_payload = payload
    return last_payload


def _open_href(record: LaunchRecord) -> str:
    return f"/cockpit/projects/launch/open/{record.launch_id}?stop_token={record.stop_token}"


def _tail(path: str, limit: int = 3000) -> str:
    try:
        file_path = Path(path)
        if not file_path.exists():
            return ""
        with file_path.open("rb") as handle:
            handle.seek(0, os.SEEK_END)
            size = handle.tell()
            handle.seek(max(0, size - limit))
            return handle.read().decode("utf-8", errors="replace")
    except Exception:
        return ""


def _next_free_port() -> int:
    base = int(os.environ.get("ION_PROJECT_LAUNCH_PORT_BASE", str(DEFAULT_PORT_BASE)))
    used = {record.port for record in _LAUNCHES.values() if _record_running(record)}
    for offset in range(MAX_PORT_SCAN):
        port = base + offset
        if port in used:
            continue
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((HOST, port))
            except OSError:
                continue
            return port
    raise RuntimeError("no_free_project_launch_port")


def _write_launch_receipt(shell_root: Path, action: str, record: LaunchRecord) -> None:
    receipt = {
        "schema_id": "ion.project_launcher_receipt.v1",
        "created_at": utc_now(),
        "action": action,
        "launch": _record_payload(shell_root, record),
        "authority": {
            "candidate_local_runtime_control": True,
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    write_json(shell_root / PROJECT_LAUNCHER_RECEIPTS_DIR / f"{stamp}_{record.launch_id}_{action}.json", receipt)


def _write_diagnostics_receipt(shell_root: Path, record: LaunchRecord, result: Mapping[str, Any]) -> None:
    receipt = {
        "schema_id": "ion.project_launcher_diagnostics_receipt.v1",
        "created_at": utc_now(),
        "action": "diagnostics",
        "launch_id": record.launch_id,
        "project_id": record.project_id,
        "version_id": record.version_id,
        "ok": bool(result.get("ok")),
        "finding": result.get("finding"),
        "screenshot": result.get("screenshot") if isinstance(result.get("screenshot"), Mapping) else {},
        "authority": {
            "candidate_local_runtime_control": True,
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    write_json(shell_root / PROJECT_LAUNCHER_RECEIPTS_DIR / f"{stamp}_{record.launch_id}_diagnostics.json", receipt)


def _hash_id(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()


def _html(value: Any) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
