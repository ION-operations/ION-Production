import json
import time
import urllib.request
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from kernel import ion_project_launcher as launcher
from kernel.ion_project_launcher import (
    PROJECT_LOCAL_LAUNCH_CONFIRMATION,
    build_project_launcher_open_html,
    build_project_launcher_status,
    project_launch_metadata,
    project_launcher_diagnostics,
    project_launcher_start,
    project_launcher_status,
    project_launcher_stop,
)


def _wait_for_url(url: str) -> str:
    last_error = ""
    for _attempt in range(40):
        try:
            with urllib.request.urlopen(url, timeout=0.25) as response:
                return response.read().decode("utf-8", errors="replace")
        except Exception as exc:  # pragma: no cover - diagnostic retained in assertion
            last_error = exc.__class__.__name__
            time.sleep(0.05)
    raise AssertionError(f"launcher url did not respond: {url} ({last_error})")


def test_project_launcher_status_empty_reconciles_without_crash(tmp_path: Path):
    status = build_project_launcher_status(tmp_path)

    assert status["ok"] is True
    assert status["launch_count"] == 0
    assert status["durable_state"]["enabled"] is True
    assert status["durable_state"]["state_file_count"] == 0


def test_static_project_launcher_requires_confirmation_and_stops(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("ION_PROJECT_LAUNCH_PORT_BASE", "6630")
    app = tmp_path / "demo-static-app"
    app.mkdir()
    (app / "index.html").write_text("<!doctype html><title>demo static app</title><main>ION static launch proof</main>\n", encoding="utf-8")

    metadata = project_launch_metadata(app)

    assert metadata["launchable"] is True
    assert metadata["framework"] == "static"
    blocked = project_launcher_start(tmp_path, {"path": app.as_posix()})
    assert blocked["ok"] is False
    assert blocked["finding"] == "launch_confirmation_required"

    result = project_launcher_start(
        tmp_path,
        {
            "confirmation": PROJECT_LOCAL_LAUNCH_CONFIRMATION,
            "path": app.as_posix(),
            "project_id": "test:demo-static-app",
            "version_id": "v001",
            "label": "Demo Static App",
            "install_repair": False,
        },
    )
    launch = result.get("launch") or {}
    try:
        assert result["ok"] is True
        assert launch["running"] is True
        assert launch["framework"] == "static"
        assert "stop_token=" not in launch["open_href"]
        assert "stop_token=" in result["open_href"]
        state_path = tmp_path / "ION/05_context/current/project_launcher/state/launches" / f"{launch['launch_id']}.json"
        assert state_path.exists()
        state = json.loads(state_path.read_text(encoding="utf-8"))
        assert state["schema_id"] == "ion.project_launcher_durable_state.v0_1"
        assert state["launch"]["launch_id"] == launch["launch_id"]
        assert state["launch"]["state"] == "running"
        assert state["launch"]["stop_token_sha256"]
        assert state["launch"]["process_attached"] is True
        assert "ION static launch proof" in _wait_for_url(result["url"])

        wrapper = build_project_launcher_open_html(tmp_path, launch["launch_id"])
        assert "navigator.sendBeacon('/cockpit/projects/launch/stop'" in wrapper
        assert 'id="ion-ai-drawer-toggle"' in wrapper
        assert "Codex Workbench" in wrapper
        assert "GPT Browser" in wrapper
        assert "capture-screen" in wrapper
        assert 'data-preview-viewport="desktop"' in wrapper
        assert 'data-preview-viewport="tablet"' in wrapper
        assert 'data-preview-viewport="mobile"' in wrapper
        assert 'id="capture-viewport"' in wrapper
        assert "selectedViewportSize" in wrapper
        assert f'src="{result["url"]}"' in wrapper

        missing_auth_diagnostics = project_launcher_diagnostics(
            tmp_path,
            {
                "launch_id": launch["launch_id"],
                "capture": False,
            },
        )
        assert missing_auth_diagnostics["ok"] is False
        assert missing_auth_diagnostics["finding"] == "launch_diagnostics_confirmation_required"

        stop_token = parse_qs(urlparse(result["open_href"]).query)["stop_token"][0]
        token_diagnostics = project_launcher_diagnostics(
            tmp_path,
            {
                "stop_token": stop_token,
                "launch_id": launch["launch_id"],
                "capture": False,
            },
        )
        assert token_diagnostics["ok"] is True

        diagnostics = project_launcher_diagnostics(
            tmp_path,
            {
                "confirmation": PROJECT_LOCAL_LAUNCH_CONFIRMATION,
                "launch_id": launch["launch_id"],
                "capture": True,
                "width": 640,
                "height": 420,
            },
        )
        assert diagnostics["ok"] is True
        assert diagnostics["screenshot"]["status"] == "captured"
        assert (tmp_path / diagnostics["screenshot"]["screenshot_path"]).exists() or Path(diagnostics["screenshot"]["screenshot_path"]).exists()

        stop_result = project_launcher_stop(
            tmp_path,
            {
                "confirmation": PROJECT_LOCAL_LAUNCH_CONFIRMATION,
                "launch_id": launch["launch_id"],
            },
        )
        assert stop_result["ok"] is True
        assert stop_result["launch"]["running"] is False
        stopped_state = json.loads(state_path.read_text(encoding="utf-8"))
        assert stopped_state["launch"]["state"] == "stopped"
    finally:
        if launch.get("launch_id"):
            project_launcher_stop(
                tmp_path,
                {
                    "confirmation": PROJECT_LOCAL_LAUNCH_CONFIRMATION,
                    "launch_id": launch["launch_id"],
                },
            )


def test_project_launcher_restart_recovers_detached_record_and_stop_is_mark_only(tmp_path: Path):
    app = tmp_path / "detached-static-app"
    app.mkdir()
    (app / "index.html").write_text("<!doctype html><title>detached</title>\n", encoding="utf-8")
    launch_id = "detached-launch"
    log_path = tmp_path / "ION/05_context/current/project_launcher/logs/detached-launch.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("detached launch log\n", encoding="utf-8")
    state_path = tmp_path / "ION/05_context/current/project_launcher/state/launches/detached-launch.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.project_launcher_durable_state.v0_1",
                "reason": "running",
                "launch": {
                    "launch_id": launch_id,
                    "project_id": "test:detached",
                    "version_id": "v001",
                    "label": "Detached Static App",
                    "path": app.as_posix(),
                    "framework": "static",
                    "command": ["python3", "-m", "http.server", "6670", "--bind", "127.0.0.1"],
                    "url": "http://127.0.0.1:6670/",
                    "port": 6670,
                    "log_path": log_path.as_posix(),
                    "stop_token": "detached-stop-token",
                    "state": "running",
                    "message": "was running before restart",
                    "created_at": "2026-06-05T00:00:00+00:00",
                    "updated_at": "2026-06-05T00:00:00+00:00",
                    "exit_code": None,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    with launcher._LOCK:
        launcher._LAUNCHES.pop(launch_id, None)

    status = project_launcher_status(tmp_path, {"launch_id": launch_id})
    launch = status["launch"]

    assert status["ok"] is True
    assert launch["state"] == "detached"
    assert launch["detached"] is True
    assert launch["last_known_state"] == "running"
    assert launch["running"] is False
    assert launch["actual_process_control"] is False
    assert launch["stop_available"] is False
    assert "stop_token=" not in launch["open_href"]

    summary = build_project_launcher_status(tmp_path)
    assert summary["detached_count"] == 1
    assert summary["durable_state"]["state_file_count"] == 1

    denied = project_launcher_stop(tmp_path, {"launch_id": launch_id, "stop_token": "wrong"})
    assert denied["ok"] is False
    assert denied["finding"] == "launch_stop_confirmation_required"

    stopped = project_launcher_stop(tmp_path, {"launch_id": launch_id, "stop_token": "detached-stop-token"})
    assert stopped["ok"] is True
    assert stopped["finding"] == "launch_process_detached_marked_stopped"
    assert stopped["actual_process_stopped"] is False
    assert stopped["launch"]["state"] == "stopped"
