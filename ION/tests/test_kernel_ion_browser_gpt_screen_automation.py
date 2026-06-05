import json
from datetime import datetime, timezone
from pathlib import Path

import kernel.ion_browser_gpt_screen_automation as screen


def seed_root(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").parent.mkdir(parents=True, exist_ok=True)
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")


class FakeXdotool:
    def __init__(
        self,
        *,
        window_id: str = "8390237",
        x: int = -8,
        y: int = 54,
        width: int = 980,
        height: int = 1050,
        title: str = "ChatGPT - Google Chrome",
    ):
        self.window_id = window_id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.title = title
        self.active_tab = 3 if "ChatGPT" in title else 2
        self.calls: list[list[str]] = []

    def __call__(self, args, timeout=3.0):
        command = [Path(str(args[0])).name, *[str(item) for item in args[1:]]]
        self.calls.append(command)
        if "getactivewindow" in command:
            return {"ok": True, "returncode": 0, "stdout": self.window_id, "stderr": "", "command": "xdotool"}
        if "getwindowgeometry" in command:
            return {
                "ok": True,
                "returncode": 0,
                "stdout": f"WINDOW={self.window_id}\nX={self.x}\nY={self.y}\nWIDTH={self.width}\nHEIGHT={self.height}\nSCREEN=0",
                "stderr": "",
                "command": "xdotool",
            }
        if "getdisplaygeometry" in command:
            return {"ok": True, "returncode": 0, "stdout": "1920 1080", "stderr": "", "command": "xdotool"}
        if "getwindowname" in command:
            titles = {
                1: "Extensions - ION ChatOps Bridge - Google Chrome",
                2: "Helixion JOC Cockpit - Google Chrome",
                3: "ChatGPT - Google Chrome",
            }
            return {"ok": True, "returncode": 0, "stdout": titles.get(self.active_tab, self.title), "stderr": "", "command": "xdotool"}
        if "key" in command:
            key = command[-1]
            if key.startswith("Ctrl+"):
                self.active_tab = int(key.split("+", 1)[1])
            return {"ok": True, "returncode": 0, "stdout": "", "stderr": "", "command": "xdotool"}
        if "windowactivate" in command or "mousemove" in command:
            return {"ok": True, "returncode": 0, "stdout": "", "stderr": "", "command": "xdotool"}
        return {"ok": False, "returncode": 1, "stdout": "", "stderr": "unexpected command", "command": "xdotool"}


def patch_tools(monkeypatch):
    monkeypatch.setattr(screen, "_tool_paths", lambda: {"xdotool": "xdotool", "import": "import"})


def test_parse_xdotool_window_geometry_shell():
    parsed = screen.parse_xdotool_window_geometry_shell("WINDOW=8390237\nX=-8\nY=54\nWIDTH=980\nHEIGHT=1050\nSCREEN=0\n")

    assert parsed["window"] == 8390237
    assert parsed["x"] == -8
    assert parsed["height"] == 1050


def test_learn_state_records_tab_order_and_relative_reload_point(tmp_path: Path, monkeypatch):
    seed_root(tmp_path)
    patch_tools(monkeypatch)
    runner = FakeXdotool()

    result = screen.learn_screen_automation_state(tmp_path, window_id="8390237", probe_tabs=True, runner=runner)

    assert result["ok"] is True
    state_path = tmp_path / result["state_path"]
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["schema_id"] == screen.STATE_SCHEMA_ID
    assert state["control_points"]["extension_reload_button"]["screen_x_at_capture"] == 779
    assert state["control_points"]["extension_reload_button"]["screen_y_at_capture"] == 293
    assert [row["role"] for row in state["tab_order"]] == ["extension_manager", "cockpit", "chatgpt"]
    assert all(row["title_match"] for row in state["tab_order"])
    assert runner.active_tab == 3


def test_learn_state_rejects_non_browser_window_without_overwriting_state(tmp_path: Path, monkeypatch):
    seed_root(tmp_path)
    patch_tools(monkeypatch)
    prior_state_path = tmp_path / screen.LATEST_STATE_PATH
    prior_state_path.parent.mkdir(parents=True)
    prior_state_path.write_text(json.dumps({"schema_id": screen.STATE_SCHEMA_ID, "sentinel": "keep"}), encoding="utf-8")

    runner = FakeXdotool(window_id="999", title="ION - Production")
    runner.active_tab = 0
    result = screen.learn_screen_automation_state(tmp_path, window_id="999", runner=runner)

    assert result["ok"] is False
    assert result["finding"] == "active_window_not_browser_gpt_surface"
    assert json.loads(prior_state_path.read_text(encoding="utf-8"))["sentinel"] == "keep"


def test_assess_reuses_state_when_window_geometry_matches(tmp_path: Path, monkeypatch):
    seed_root(tmp_path)
    patch_tools(monkeypatch)
    runner = FakeXdotool()
    screen.learn_screen_automation_state(tmp_path, window_id="8390237", runner=runner)

    assessment = screen.assess_screen_automation_reuse(tmp_path, runner=FakeXdotool(), now=datetime.now(timezone.utc))

    assert assessment["can_reuse"] is True
    assert assessment["findings"] == []
    assert assessment["control_points"]["extension_reload_button"]["current_screen_point"] == {"x": 779, "y": 293}


def test_assess_rejects_state_when_window_moved(tmp_path: Path, monkeypatch):
    seed_root(tmp_path)
    patch_tools(monkeypatch)
    screen.learn_screen_automation_state(tmp_path, window_id="8390237", runner=FakeXdotool())

    assessment = screen.assess_screen_automation_reuse(tmp_path, runner=FakeXdotool(x=40))

    assert assessment["can_reuse"] is False
    assert "window_geometry_x_changed" in assessment["findings"]
    assert assessment["recommended_action"] == "learn_screen_automation_state"


def test_reload_extension_dry_run_uses_learned_point_without_clicking(tmp_path: Path, monkeypatch):
    seed_root(tmp_path)
    patch_tools(monkeypatch)
    screen.learn_screen_automation_state(tmp_path, window_id="8390237", runner=FakeXdotool())
    runner = FakeXdotool()

    result = screen.execute_extension_reload(tmp_path, dry_run=True, runner=runner)

    assert result["ok"] is True
    assert result["finding"] == "extension_reload_planned"
    assert result["planned_sequence"][2] == {"action": "click", "target": "extension_reload_button", "x": 779, "y": 293}
    assert not any("mousemove" in call for call in runner.calls)


def test_reload_extension_blocks_when_state_is_missing(tmp_path: Path, monkeypatch):
    seed_root(tmp_path)
    patch_tools(monkeypatch)

    result = screen.execute_extension_reload(tmp_path, dry_run=True, runner=FakeXdotool())

    assert result["ok"] is False
    assert result["finding"] == "screen_automation_state_not_reusable"
    assert result["assessment"]["findings"] == ["state_missing"]


def test_cockpit_upload_dry_run_uses_learned_upload_button(tmp_path: Path, monkeypatch):
    seed_root(tmp_path)
    patch_tools(monkeypatch)
    upload_file = tmp_path / "smoke.txt"
    upload_file.write_text("hello\n", encoding="utf-8")
    screen.learn_screen_automation_state(tmp_path, window_id="8390237", runner=FakeXdotool())
    runner = FakeXdotool()

    result = screen.execute_cockpit_upload_file(tmp_path, file_path=upload_file, dry_run=True, runner=runner)

    assert result["ok"] is True
    assert result["finding"] == "cockpit_upload_file_planned"
    assert result["planned_sequence"][2] == {"action": "click", "target": "cockpit_upload_button", "x": 83, "y": 908}
    assert result["planned_sequence"][3] == {"action": "file_picker_select", "path": upload_file.as_posix()}
    assert result["no_send_click_performed"] is True
