import time
import urllib.request
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from kernel.ion_project_launcher import (
    PROJECT_LOCAL_LAUNCH_CONFIRMATION,
    build_project_launcher_open_html,
    project_launch_metadata,
    project_launcher_diagnostics,
    project_launcher_start,
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
    finally:
        if launch.get("launch_id"):
            project_launcher_stop(
                tmp_path,
                {
                    "confirmation": PROJECT_LOCAL_LAUNCH_CONFIRMATION,
                    "launch_id": launch["launch_id"],
                },
            )
