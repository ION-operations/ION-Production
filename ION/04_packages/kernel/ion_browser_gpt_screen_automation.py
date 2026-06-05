"""Reusable local screen automation memory for Browser GPT cockpit work.

This module keeps the xdotool lane explicit and receipted. It does not infer
authority from screen access, does not read cookies, and does not send ChatGPT
messages. Its job is to remember stable browser geometry and tab order so
known-good desktop actions do not need a fresh screenshot calibration every
time the Chrome window has not moved.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import time
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_SCHEMA_ID = "ion.browser_gpt_screen_automation_state.v1"
STATUS_SCHEMA_ID = "ion.browser_gpt_screen_automation_status.v1"
RECEIPT_SCHEMA_ID = "ion.browser_gpt_screen_automation_receipt.v1"

BASE_DIR = Path("ION/05_context/current/browser_gpt_dom_profiles/screen_automation")
RECEIPTS_DIR = BASE_DIR / "receipts"
LATEST_STATE_PATH = BASE_DIR / "latest_state.json"

DEFAULT_GEOMETRY_TOLERANCE_PX = 12
DEFAULT_MAX_STATE_AGE_SECONDS = 12 * 60 * 60

DEFAULT_TAB_ORDER: tuple[dict[str, Any], ...] = (
    {
        "role": "extension_manager",
        "index": 1,
        "title_contains_any": ["Extensions", "ION ChatOps"],
        "description": "chrome://extensions tab for reloading the unpacked bridge",
    },
    {
        "role": "cockpit",
        "index": 2,
        "title_contains_any": ["Helixion JOC Cockpit", "127.0.0.1:8765"],
        "description": "JOC cockpit Browser GPT page",
    },
    {
        "role": "chatgpt",
        "index": 3,
        "title_contains_any": ["ChatGPT"],
        "description": "logged-in ChatGPT tab running the content script",
    },
)

DEFAULT_CONTROL_POINTS: dict[str, dict[str, Any]] = {
    "extension_reload_button": {
        "relative_to": "chrome_window_outer_top_left",
        "x": 787,
        "y": 239,
        "description": "Reload button on chrome://extensions extension details page at 980x1050 Chrome geometry.",
    },
    "cockpit_upload_button": {
        "relative_to": "chrome_window_outer_top_left",
        "x": 91,
        "y": 854,
        "description": "Browser GPT Upload control in the cockpit at the current compact layout.",
    },
}


CommandRunner = Callable[[Sequence[str]], dict[str, Any]]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _resolve_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    return candidate


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return payload if isinstance(payload, dict) else None


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _repo_rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _run(args: Sequence[str], *, timeout: float = 3.0) -> dict[str, Any]:
    try:
        completed = subprocess.run(list(args), capture_output=True, text=True, timeout=timeout, check=False)
    except Exception as exc:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "command": Path(str(args[0])).name if args else "",
        }
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "command": Path(str(args[0])).name if args else "",
    }


def _tool_paths() -> dict[str, str | None]:
    return {name: shutil.which(name) for name in ("xdotool", "import")}


def parse_xdotool_window_geometry_shell(output: str) -> dict[str, int]:
    values: dict[str, int] = {}
    for raw_line in output.splitlines():
        if "=" not in raw_line:
            continue
        key, value = raw_line.split("=", 1)
        key = key.strip().lower()
        if key not in {"window", "x", "y", "width", "height", "screen"}:
            continue
        try:
            values[key] = int(float(value.strip()))
        except ValueError:
            continue
    required = {"window", "x", "y", "width", "height"}
    missing = sorted(required - set(values))
    if missing:
        raise ValueError(f"missing xdotool geometry fields: {', '.join(missing)}")
    return values


def parse_display_geometry(output: str) -> dict[str, Any]:
    parts = output.split()
    if len(parts) < 2:
        return {"ok": False, "finding": "display_geometry_parse_failed", "raw": output}
    try:
        return {"ok": True, "width": int(float(parts[0])), "height": int(float(parts[1]))}
    except ValueError:
        return {"ok": False, "finding": "display_geometry_parse_failed", "raw": output}


def _command_runner(
    runner: Callable[..., dict[str, Any]],
    args: Sequence[str],
    *,
    timeout: float = 3.0,
) -> dict[str, Any]:
    try:
        return runner(args, timeout=timeout)
    except TypeError:
        return runner(args)


def current_chrome_window_projection(
    root: str | Path | None = None,
    *,
    window_id: str | int | None = None,
    runner: Callable[..., dict[str, Any]] = _run,
) -> dict[str, Any]:
    _resolve_root(root)
    tools = _tool_paths()
    xdotool = tools.get("xdotool")
    if not xdotool:
        return {
            "ok": False,
            "finding": "xdotool_missing",
            "tools": tools,
        }

    if window_id is None:
        active = _command_runner(runner, [xdotool, "getactivewindow"], timeout=1.0)
        if not active.get("ok") or not str(active.get("stdout") or "").strip():
            return {"ok": False, "finding": "active_window_unavailable", "active_window": active, "tools": tools}
        window_id = str(active["stdout"]).strip()

    geometry_result = _command_runner(runner, [xdotool, "getwindowgeometry", "--shell", str(window_id)], timeout=1.0)
    if not geometry_result.get("ok"):
        return {"ok": False, "finding": "window_geometry_unavailable", "geometry_result": geometry_result, "tools": tools}
    try:
        geometry = parse_xdotool_window_geometry_shell(str(geometry_result.get("stdout") or ""))
    except ValueError as exc:
        return {"ok": False, "finding": "window_geometry_parse_failed", "error": str(exc), "geometry_result": geometry_result, "tools": tools}

    title_result = _command_runner(runner, [xdotool, "getwindowname", str(window_id)], timeout=1.0)
    display_result = _command_runner(runner, [xdotool, "getdisplaygeometry"], timeout=1.0)
    display = parse_display_geometry(str(display_result.get("stdout") or "")) if display_result.get("ok") else {"ok": False, "finding": "display_geometry_unavailable"}
    title = str(title_result.get("stdout") or "").strip() if title_result.get("ok") else ""

    return {
        "ok": True,
        "schema_id": "ion.browser_gpt_screen_window_projection.v1",
        "window_id": str(window_id),
        "title": title,
        "geometry": {
            "x": geometry["x"],
            "y": geometry["y"],
            "width": geometry["width"],
            "height": geometry["height"],
            "screen": geometry.get("screen", 0),
        },
        "display_geometry": display,
        "tools": tools,
        "captured_at": _now(),
    }


def screen_point(window: Mapping[str, Any], point: Mapping[str, Any]) -> dict[str, int]:
    geometry = window.get("geometry") if isinstance(window.get("geometry"), Mapping) else {}
    return {
        "x": int(round(float(geometry.get("x") or 0) + float(point.get("x") or 0))),
        "y": int(round(float(geometry.get("y") or 0) + float(point.get("y") or 0))),
    }


def _infer_active_tab_role(title: str) -> str | None:
    lowered = title.lower()
    if "extensions" in lowered or "ion chatops" in lowered:
        return "extension_manager"
    if "helixion joc cockpit" in lowered or "127.0.0.1:8765" in lowered:
        return "cockpit"
    if "chatgpt" in lowered:
        return "chatgpt"
    return None


def browser_gpt_window_title_is_acceptable(title: str) -> bool:
    lowered = title.lower()
    return bool(
        "google chrome" in lowered
        or "chromium" in lowered
        or "chatgpt" in lowered
        or "helixion joc cockpit" in lowered
        or "extensions" in lowered
    )


def _tab_index_for_role(role: str | None) -> int | None:
    for row in DEFAULT_TAB_ORDER:
        if row["role"] == role:
            return int(row["index"])
    return None


def _control_points_with_capture(window: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    controls: dict[str, dict[str, Any]] = {}
    for key, point in DEFAULT_CONTROL_POINTS.items():
        screen = screen_point(window, point)
        controls[key] = {
            **point,
            "screen_x_at_capture": screen["x"],
            "screen_y_at_capture": screen["y"],
        }
    return controls


def learn_screen_automation_state(
    root: str | Path | None = None,
    *,
    window_id: str | int | None = None,
    probe_tabs: bool = False,
    restore_tab: bool = True,
    write: bool = True,
    runner: Callable[..., dict[str, Any]] = _run,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    window = current_chrome_window_projection(shell_root, window_id=window_id, runner=runner)
    if not window.get("ok"):
        result = {
            "schema_id": STATUS_SCHEMA_ID,
            "ok": False,
            "finding": str(window.get("finding") or "window_projection_failed"),
            "window": window,
            "state_path": _repo_rel(shell_root, shell_root / LATEST_STATE_PATH),
        }
        if write:
            result["receipt_path"] = write_screen_automation_receipt(shell_root, "learn", result, status="failed")
        return result
    if not browser_gpt_window_title_is_acceptable(str(window.get("title") or "")):
        result = {
            "schema_id": STATUS_SCHEMA_ID,
            "ok": False,
            "finding": "active_window_not_browser_gpt_surface",
            "window": window,
            "state_path": _repo_rel(shell_root, shell_root / LATEST_STATE_PATH),
            "write_skipped": True,
        }
        if write:
            result["receipt_path"] = write_screen_automation_receipt(shell_root, "learn", result, status="blocked")
        return result

    tools = window.get("tools") if isinstance(window.get("tools"), Mapping) else {}
    xdotool = str(tools.get("xdotool") or "xdotool")
    original_role = _infer_active_tab_role(str(window.get("title") or ""))
    original_tab_index = _tab_index_for_role(original_role)
    observed_tabs: list[dict[str, Any]] = []

    if probe_tabs:
        _command_runner(runner, [xdotool, "windowactivate", "--sync", str(window["window_id"])], timeout=2.0)
        for tab in DEFAULT_TAB_ORDER:
            index = int(tab["index"])
            _command_runner(runner, [xdotool, "key", "--clearmodifiers", f"Ctrl+{index}"], timeout=2.0)
            time.sleep(0.25)
            title_result = _command_runner(runner, [xdotool, "getwindowname", str(window["window_id"])], timeout=1.0)
            title = str(title_result.get("stdout") or "").strip() if title_result.get("ok") else ""
            expected = [str(item) for item in tab.get("title_contains_any", [])]
            observed_tabs.append(
                {
                    **tab,
                    "observed_title": title,
                    "title_match": any(item.lower() in title.lower() for item in expected),
                    "probe_ok": bool(title_result.get("ok")),
                }
            )
        if restore_tab and original_tab_index:
            _command_runner(runner, [xdotool, "key", "--clearmodifiers", f"Ctrl+{original_tab_index}"], timeout=2.0)

    state = {
        "schema_id": STATE_SCHEMA_ID,
        "state_status": "learned",
        "captured_at": _now(),
        "source": "kernel.ion_browser_gpt_screen_automation.learn_screen_automation_state",
        "window": window,
        "tab_order": observed_tabs if observed_tabs else [dict(row) for row in DEFAULT_TAB_ORDER],
        "control_points": _control_points_with_capture(window),
        "reuse_policy": {
            "max_age_seconds": DEFAULT_MAX_STATE_AGE_SECONDS,
            "geometry_tolerance_px": DEFAULT_GEOMETRY_TOLERANCE_PX,
            "requires_same_window_id": True,
            "requires_same_display_geometry": True,
        },
        "authority": _authority(),
    }
    state_path = shell_root / LATEST_STATE_PATH
    result = {
        "schema_id": STATUS_SCHEMA_ID,
        "ok": True,
        "finding": "screen_automation_state_learned",
        "state": state,
        "state_path": _repo_rel(shell_root, state_path),
        "probe_tabs": probe_tabs,
    }
    if write:
        _write_json(state_path, state)
        result["receipt_path"] = write_screen_automation_receipt(shell_root, "learn", result, status="completed")
    return result


def latest_screen_automation_state(root: str | Path | None = None) -> dict[str, Any] | None:
    shell_root = _resolve_root(root)
    return _read_json(shell_root / LATEST_STATE_PATH)


def _parse_iso(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _seconds_since(value: str, now: datetime | None = None) -> float | None:
    parsed = _parse_iso(value)
    if not parsed:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return abs(((now or datetime.now(timezone.utc)) - parsed).total_seconds())


def assess_screen_automation_reuse(
    root: str | Path | None = None,
    *,
    state: Mapping[str, Any] | None = None,
    window_id: str | int | None = None,
    runner: Callable[..., dict[str, Any]] = _run,
    now: datetime | None = None,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    state_payload = dict(state or latest_screen_automation_state(shell_root) or {})
    findings: list[str] = []
    if not state_payload:
        findings.append("state_missing")
        return {
            "schema_id": STATUS_SCHEMA_ID,
            "ok": True,
            "can_reuse": False,
            "findings": findings,
            "recommended_action": "learn_screen_automation_state",
            "state_path": _repo_rel(shell_root, shell_root / LATEST_STATE_PATH),
        }
    if state_payload.get("schema_id") != STATE_SCHEMA_ID:
        findings.append("state_schema_unrecognized")

    policy = state_payload.get("reuse_policy") if isinstance(state_payload.get("reuse_policy"), Mapping) else {}
    tolerance = int(policy.get("geometry_tolerance_px") or DEFAULT_GEOMETRY_TOLERANCE_PX)
    max_age = int(policy.get("max_age_seconds") or DEFAULT_MAX_STATE_AGE_SECONDS)
    age_seconds = _seconds_since(str(state_payload.get("captured_at") or ""), now=now)
    if age_seconds is None:
        findings.append("state_timestamp_missing")
    elif age_seconds > max_age:
        findings.append("state_stale")

    state_window = state_payload.get("window") if isinstance(state_payload.get("window"), Mapping) else {}
    target_window_id = window_id or state_window.get("window_id")
    current = current_chrome_window_projection(shell_root, window_id=target_window_id, runner=runner)
    if not current.get("ok"):
        findings.append(str(current.get("finding") or "current_window_projection_failed"))
    else:
        if policy.get("requires_same_window_id", True) and str(current.get("window_id")) != str(state_window.get("window_id")):
            findings.append("window_id_changed")
        state_geometry = state_window.get("geometry") if isinstance(state_window.get("geometry"), Mapping) else {}
        current_geometry = current.get("geometry") if isinstance(current.get("geometry"), Mapping) else {}
        for key in ("x", "y", "width", "height"):
            try:
                before = float(state_geometry.get(key))
                after = float(current_geometry.get(key))
            except (TypeError, ValueError):
                findings.append(f"window_geometry_{key}_missing")
                continue
            if abs(after - before) > tolerance:
                findings.append(f"window_geometry_{key}_changed")
        if policy.get("requires_same_display_geometry", True):
            state_display = state_window.get("display_geometry") if isinstance(state_window.get("display_geometry"), Mapping) else {}
            current_display = current.get("display_geometry") if isinstance(current.get("display_geometry"), Mapping) else {}
            if state_display.get("ok") and current_display.get("ok"):
                if state_display.get("width") != current_display.get("width") or state_display.get("height") != current_display.get("height"):
                    findings.append("display_geometry_changed")
        if "chrome" not in str(current.get("title") or "").lower() and "chatgpt" not in str(current.get("title") or "").lower():
            findings.append("window_title_not_browser_like")

    control_points: dict[str, Any] = {}
    for key, point in (state_payload.get("control_points") if isinstance(state_payload.get("control_points"), Mapping) else {}).items():
        if isinstance(point, Mapping) and current.get("ok"):
            control_points[key] = {**dict(point), "current_screen_point": screen_point(current, point)}

    can_reuse = not findings
    return {
        "schema_id": STATUS_SCHEMA_ID,
        "ok": True,
        "can_reuse": can_reuse,
        "findings": findings,
        "recommended_action": "reuse_known_screen_automation_state" if can_reuse else "learn_screen_automation_state",
        "age_seconds": age_seconds,
        "state_path": _repo_rel(shell_root, shell_root / LATEST_STATE_PATH),
        "state": state_payload,
        "current_window": current,
        "control_points": control_points,
    }


def _planned_key_sequence_for_tab(role: str, state: Mapping[str, Any]) -> dict[str, Any] | None:
    for tab in state.get("tab_order", []) if isinstance(state.get("tab_order"), list) else []:
        if isinstance(tab, Mapping) and tab.get("role") == role:
            return {"role": role, "index": int(tab.get("index") or 0), "key": f"Ctrl+{int(tab.get('index') or 0)}"}
    return None


def planned_extension_reload_sequence(assessment: Mapping[str, Any]) -> list[dict[str, Any]]:
    state = assessment.get("state") if isinstance(assessment.get("state"), Mapping) else {}
    current_window = assessment.get("current_window") if isinstance(assessment.get("current_window"), Mapping) else {}
    controls = assessment.get("control_points") if isinstance(assessment.get("control_points"), Mapping) else {}
    reload_point = controls.get("extension_reload_button") if isinstance(controls.get("extension_reload_button"), Mapping) else None
    extension_tab = _planned_key_sequence_for_tab("extension_manager", state)
    if not current_window or not reload_point or not extension_tab:
        return []
    point = reload_point.get("current_screen_point") if isinstance(reload_point.get("current_screen_point"), Mapping) else {}
    return [
        {"action": "windowactivate", "window_id": current_window.get("window_id")},
        {"action": "switch_tab", **extension_tab},
        {"action": "click", "target": "extension_reload_button", "x": point.get("x"), "y": point.get("y")},
    ]


def execute_extension_reload(
    root: str | Path | None = None,
    *,
    dry_run: bool = True,
    runner: Callable[..., dict[str, Any]] = _run,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    assessment = assess_screen_automation_reuse(shell_root, runner=runner)
    sequence = planned_extension_reload_sequence(assessment)
    if not assessment.get("can_reuse") or not sequence:
        result = {
            "schema_id": STATUS_SCHEMA_ID,
            "ok": False,
            "finding": "screen_automation_state_not_reusable",
            "dry_run": dry_run,
            "assessment": assessment,
            "planned_sequence": sequence,
        }
        result["receipt_path"] = write_screen_automation_receipt(shell_root, "reload_extension", result, status="blocked")
        return result

    tools = _tool_paths()
    xdotool = str(tools.get("xdotool") or "xdotool")
    command_results: list[dict[str, Any]] = []
    if not dry_run:
        window_id = str((assessment.get("current_window") or {}).get("window_id"))
        point = sequence[2]
        command_results.append(_command_runner(runner, [xdotool, "windowactivate", "--sync", window_id], timeout=2.0))
        command_results.append(_command_runner(runner, [xdotool, "key", "--clearmodifiers", str(sequence[1]["key"])], timeout=2.0))
        time.sleep(0.5)
        command_results.append(_command_runner(runner, [xdotool, "mousemove", str(point["x"]), str(point["y"]), "click", "1"], timeout=3.0))
        time.sleep(1.2)
    ok = dry_run or all(item.get("ok") for item in command_results)
    result = {
        "schema_id": STATUS_SCHEMA_ID,
        "ok": ok,
        "finding": "extension_reload_planned" if dry_run else ("extension_reload_executed" if ok else "extension_reload_failed"),
        "dry_run": dry_run,
        "assessment": assessment,
        "planned_sequence": sequence,
        "command_results": command_results,
        "authority": _authority(),
    }
    result["receipt_path"] = write_screen_automation_receipt(shell_root, "reload_extension", result, status="completed" if ok else "failed")
    return result


def execute_tab_refresh(
    root: str | Path | None = None,
    *,
    roles: Sequence[str] = ("chatgpt", "cockpit"),
    dry_run: bool = True,
    runner: Callable[..., dict[str, Any]] = _run,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    assessment = assess_screen_automation_reuse(shell_root, runner=runner)
    if not assessment.get("can_reuse"):
        result = {
            "schema_id": STATUS_SCHEMA_ID,
            "ok": False,
            "finding": "screen_automation_state_not_reusable",
            "dry_run": dry_run,
            "assessment": assessment,
        }
        result["receipt_path"] = write_screen_automation_receipt(shell_root, "refresh_tabs", result, status="blocked")
        return result

    state = assessment.get("state") if isinstance(assessment.get("state"), Mapping) else {}
    current_window = assessment.get("current_window") if isinstance(assessment.get("current_window"), Mapping) else {}
    sequence: list[dict[str, Any]] = [{"action": "windowactivate", "window_id": current_window.get("window_id")}]
    for role in roles:
        tab = _planned_key_sequence_for_tab(role, state)
        if tab:
            sequence.append({"action": "switch_tab", **tab})
            sequence.append({"action": "key", "key": "Ctrl+r", "role": role})

    tools = _tool_paths()
    xdotool = str(tools.get("xdotool") or "xdotool")
    command_results: list[dict[str, Any]] = []
    if not dry_run:
        window_id = str(current_window.get("window_id"))
        command_results.append(_command_runner(runner, [xdotool, "windowactivate", "--sync", window_id], timeout=2.0))
        for item in sequence[1:]:
            if item["action"] == "switch_tab":
                command_results.append(_command_runner(runner, [xdotool, "key", "--clearmodifiers", str(item["key"])], timeout=2.0))
                time.sleep(0.2)
            elif item["action"] == "key":
                command_results.append(_command_runner(runner, [xdotool, "key", "--clearmodifiers", str(item["key"])], timeout=2.0))
                time.sleep(1.0)
    ok = dry_run or all(item.get("ok") for item in command_results)
    result = {
        "schema_id": STATUS_SCHEMA_ID,
        "ok": ok,
        "finding": "tab_refresh_planned" if dry_run else ("tab_refresh_executed" if ok else "tab_refresh_failed"),
        "dry_run": dry_run,
        "roles": list(roles),
        "assessment": assessment,
        "planned_sequence": sequence,
        "command_results": command_results,
        "authority": _authority(),
    }
    result["receipt_path"] = write_screen_automation_receipt(shell_root, "refresh_tabs", result, status="completed" if ok else "failed")
    return result


def planned_cockpit_upload_sequence(assessment: Mapping[str, Any], file_path: Path) -> list[dict[str, Any]]:
    state = assessment.get("state") if isinstance(assessment.get("state"), Mapping) else {}
    current_window = assessment.get("current_window") if isinstance(assessment.get("current_window"), Mapping) else {}
    controls = assessment.get("control_points") if isinstance(assessment.get("control_points"), Mapping) else {}
    upload_point = controls.get("cockpit_upload_button") if isinstance(controls.get("cockpit_upload_button"), Mapping) else None
    cockpit_tab = _planned_key_sequence_for_tab("cockpit", state)
    if not current_window or not upload_point or not cockpit_tab:
        return []
    point = upload_point.get("current_screen_point") if isinstance(upload_point.get("current_screen_point"), Mapping) else {}
    return [
        {"action": "windowactivate", "window_id": current_window.get("window_id")},
        {"action": "switch_tab", **cockpit_tab},
        {"action": "click", "target": "cockpit_upload_button", "x": point.get("x"), "y": point.get("y")},
        {"action": "file_picker_select", "path": file_path.as_posix()},
    ]


def execute_cockpit_upload_file(
    root: str | Path | None = None,
    *,
    file_path: str | Path,
    dry_run: bool = True,
    wait_seconds: float = 22.0,
    runner: Callable[..., dict[str, Any]] = _run,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    resolved_file = Path(file_path).expanduser().resolve()
    if not resolved_file.exists() or not resolved_file.is_file():
        result = {
            "schema_id": STATUS_SCHEMA_ID,
            "ok": False,
            "finding": "upload_file_missing",
            "file_path": resolved_file.as_posix(),
            "dry_run": dry_run,
        }
        result["receipt_path"] = write_screen_automation_receipt(shell_root, "cockpit_upload_file", result, status="blocked")
        return result

    assessment = assess_screen_automation_reuse(shell_root, runner=runner)
    sequence = planned_cockpit_upload_sequence(assessment, resolved_file)
    if not assessment.get("can_reuse") or not sequence:
        result = {
            "schema_id": STATUS_SCHEMA_ID,
            "ok": False,
            "finding": "screen_automation_state_not_reusable",
            "dry_run": dry_run,
            "file_path": resolved_file.as_posix(),
            "assessment": assessment,
            "planned_sequence": sequence,
        }
        result["receipt_path"] = write_screen_automation_receipt(shell_root, "cockpit_upload_file", result, status="blocked")
        return result

    tools = _tool_paths()
    xdotool = str(tools.get("xdotool") or "xdotool")
    command_results: list[dict[str, Any]] = []
    picker_title = ""
    if not dry_run:
        window_id = str((assessment.get("current_window") or {}).get("window_id"))
        point = sequence[2]
        command_results.append(_command_runner(runner, [xdotool, "windowactivate", "--sync", window_id], timeout=2.0))
        command_results.append(_command_runner(runner, [xdotool, "key", "--clearmodifiers", str(sequence[1]["key"])], timeout=2.0))
        time.sleep(0.25)
        command_results.append(_command_runner(runner, [xdotool, "mousemove", str(point["x"]), str(point["y"]), "click", "1"], timeout=3.0))
        time.sleep(0.75)
        active_result = _command_runner(runner, [xdotool, "getactivewindow"], timeout=1.0)
        title_result = (
            _command_runner(runner, [xdotool, "getwindowname", str(active_result.get("stdout") or "").strip()], timeout=1.0)
            if active_result.get("ok")
            else {"ok": False, "stdout": ""}
        )
        picker_title = str(title_result.get("stdout") or "").strip() if title_result.get("ok") else ""
        if not re.search(r"open|file|select|choose|upload", picker_title, flags=re.I):
            result = {
                "schema_id": STATUS_SCHEMA_ID,
                "ok": False,
                "finding": "file_picker_not_detected",
                "dry_run": dry_run,
                "file_path": resolved_file.as_posix(),
                "picker_title": picker_title,
                "assessment": assessment,
                "planned_sequence": sequence,
                "command_results": command_results,
                "authority": _authority(),
            }
            result["receipt_path"] = write_screen_automation_receipt(shell_root, "cockpit_upload_file", result, status="failed")
            return result
        command_results.append(_command_runner(runner, [xdotool, "key", "--clearmodifiers", "Ctrl+l"], timeout=2.0))
        command_results.append(_command_runner(runner, [xdotool, "type", "--delay", "1", "--clearmodifiers", resolved_file.as_posix()], timeout=5.0))
        command_results.append(_command_runner(runner, [xdotool, "key", "--clearmodifiers", "Return"], timeout=2.0))
        time.sleep(max(0.0, wait_seconds))

    ok = dry_run or all(item.get("ok") for item in command_results)
    result = {
        "schema_id": STATUS_SCHEMA_ID,
        "ok": ok,
        "finding": "cockpit_upload_file_planned" if dry_run else ("cockpit_upload_file_executed" if ok else "cockpit_upload_file_failed"),
        "dry_run": dry_run,
        "file_path": resolved_file.as_posix(),
        "file_size_bytes": resolved_file.stat().st_size,
        "picker_title": picker_title,
        "assessment": assessment,
        "planned_sequence": sequence,
        "command_results": command_results,
        "no_send_click_performed": True,
        "authority": _authority(),
    }
    result["receipt_path"] = write_screen_automation_receipt(shell_root, "cockpit_upload_file", result, status="completed" if ok else "failed")
    return result


def build_screen_automation_status(root: str | Path | None = None, *, runner: Callable[..., dict[str, Any]] = _run) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    assessment = assess_screen_automation_reuse(shell_root, runner=runner)
    return {
        "schema_id": STATUS_SCHEMA_ID,
        "ok": True,
        "status": "ready" if assessment.get("can_reuse") else "needs_learning",
        "state_path": _repo_rel(shell_root, shell_root / LATEST_STATE_PATH),
        "latest_state_exists": (shell_root / LATEST_STATE_PATH).exists(),
        "reuse_assessment": assessment,
        "tools": _tool_paths(),
        "authority": _authority(),
    }


def write_screen_automation_receipt(
    root: str | Path | None,
    operation: str,
    result: Mapping[str, Any],
    *,
    status: str,
) -> str:
    shell_root = _resolve_root(root)
    safe_operation = re.sub(r"[^0-9A-Za-z_]+", "_", operation).strip("_") or "operation"
    receipt = {
        "schema_id": RECEIPT_SCHEMA_ID,
        "operation": operation,
        "status": status,
        "created_at": _now(),
        "result": dict(result),
        "authority": _authority(),
    }
    receipt_path = shell_root / RECEIPTS_DIR / f"{_stamp()}_{safe_operation}.json"
    _write_json(receipt_path, receipt)
    return _repo_rel(shell_root, receipt_path)


def _authority() -> dict[str, bool]:
    return {
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
        "cookie_read_authority": False,
        "credential_extraction_authority": False,
        "silent_send_authority": False,
        "send_click_authority": False,
    }


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(dict(payload), indent=2, sort_keys=True))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Browser GPT screen automation memory and execution helper.")
    parser.add_argument("--ion-root", default=".", help="ION root. Defaults to current directory or nearest authority root.")
    parser.add_argument("--json", action="store_true", help="Print JSON. Human output is not currently expanded; JSON is always safe.")
    subparsers = parser.add_subparsers(dest="command")

    learn = subparsers.add_parser("learn", help="Learn current Chrome window geometry and Browser GPT tab order.")
    learn.add_argument("--window-id", default=None)
    learn.add_argument("--probe-tabs", action="store_true")
    learn.add_argument("--no-write", action="store_true")

    status = subparsers.add_parser("status", help="Assess whether the latest screen automation state is reusable.")
    status.add_argument("--window-id", default=None)

    reload_parser = subparsers.add_parser("reload-extension", help="Reload the unpacked extension from learned geometry.")
    reload_parser.add_argument("--execute", action="store_true", help="Actually move/click. Without this, only writes a dry-run receipt.")

    refresh = subparsers.add_parser("refresh-tabs", help="Refresh learned Browser GPT tabs.")
    refresh.add_argument("--roles", default="chatgpt,cockpit", help="Comma-separated roles from tab_order.")
    refresh.add_argument("--execute", action="store_true", help="Actually press the tab refresh keys.")

    upload = subparsers.add_parser("upload-file", help="Use learned cockpit geometry to select a local file for Browser GPT upload.")
    upload.add_argument("--path", required=True, help="Local file path to select in the cockpit upload picker.")
    upload.add_argument("--execute", action="store_true", help="Actually click Upload and select the file. Without this, writes a dry-run receipt.")
    upload.add_argument("--wait-seconds", type=float, default=22.0)

    args = parser.parse_args(list(argv) if argv is not None else None)
    command = args.command or "status"
    if command == "learn":
        payload = learn_screen_automation_state(
            args.ion_root,
            window_id=args.window_id,
            probe_tabs=bool(args.probe_tabs),
            write=not bool(args.no_write),
        )
    elif command == "reload-extension":
        payload = execute_extension_reload(args.ion_root, dry_run=not bool(args.execute))
    elif command == "refresh-tabs":
        roles = tuple(role.strip() for role in str(args.roles).split(",") if role.strip())
        payload = execute_tab_refresh(args.ion_root, roles=roles, dry_run=not bool(args.execute))
    elif command == "upload-file":
        payload = execute_cockpit_upload_file(args.ion_root, file_path=args.path, dry_run=not bool(args.execute), wait_seconds=float(args.wait_seconds))
    else:
        payload = build_screen_automation_status(args.ion_root)
    _print_json(payload)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
