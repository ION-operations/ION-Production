import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest


EXTENSION_ROOT = Path(__file__).resolve().parents[1] / "ion-helixion-control@helixion.net"
SPEC = importlib.util.spec_from_file_location("ion_startup_connections_control", EXTENSION_ROOT / "control.py")
assert SPEC and SPEC.loader
CONTROL = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CONTROL
SPEC.loader.exec_module(CONTROL)


def _unit(*, active: bool, enabled: bool, pid: int) -> dict:
    return {
        "available": True,
        "identity_ok": True,
        "active": active,
        "enabled": enabled,
        "main_pid": pid,
    }


def _probe(ready: bool) -> dict:
    return {"ready": ready, "http_status": 200 if ready else None, "schema_ok": ready}


def _inventory(**overrides) -> dict:
    result = {
        "preview": [],
        "action_gateway": [],
        "chatops": [],
        "ion_browser_tunnel": [],
        "ion_actions_tunnel": [],
        "ion_browser_expected_origin": [],
        "ion_actions_expected_origin": [],
        "cloudflared_tunnels": [],
    }
    result.update(overrides)
    return result


def _listener(port: int, *, listening: bool, pid: int = 0, loopback_only: bool = True) -> dict:
    return {
        "port": port,
        "listening": listening,
        "loopback_only": loopback_only if listening else False,
        "owner_pids": [pid] if listening and pid else [],
        "finding": "ok",
    }


def test_metadata_targets_gnome_42_and_v2():
    metadata = json.loads((EXTENSION_ROOT / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["uuid"] == "ion-helixion-control@helixion.net"
    assert metadata["shell-version"] == ["42"]
    assert metadata["version"] == 2


def test_helixion_open_url_targets_local_cockpit():
    assert CONTROL.COCKPIT_LOCAL_URL == "http://127.0.0.1:8765/cockpit#system"
    assert CONTROL.GROUPS["helixion"].open_url == CONTROL.COCKPIT_LOCAL_URL


def test_fixed_group_scope_and_dependency_order():
    assert CONTROL.GROUPS["helixion"].start_order == (
        "ion-mcp-preview.service",
        "ion-mcp-tunnel.service",
    )
    assert CONTROL.GROUPS["helixion"].stop_order == tuple(reversed(CONTROL.GROUPS["helixion"].start_order))
    assert CONTROL.GROUPS["actions"].start_order == (
        "ion-action-gateway.service",
        "ion-action-tunnel.service",
    )
    assert CONTROL.GROUPS["actions"].stop_order == tuple(reversed(CONTROL.GROUPS["actions"].start_order))
    assert CONTROL.GROUPS["chatops"].start_order == ("ion-chatops.service",)
    assert CONTROL.ALLOWED_UNITS == {
        "ion-mcp-preview.service",
        "ion-mcp-tunnel.service",
        "ion-action-gateway.service",
        "ion-action-tunnel.service",
        "ion-chatops.service",
        CONTROL.DRAIN_TIMER_UNIT,
        CONTROL.LOOP_TIMER_UNIT,
    }


def test_actions_health_accepts_draft_status_with_exact_ready_verdict():
    spec = CONTROL.GROUPS["actions"].probes[0]
    payload = {
        "schema_id": "ion.custom_gpt_action_gateway_health.v1",
        "ok": True,
        "verdict": "ION_CUSTOM_GPT_ACTION_GATEWAY_READY",
        "status": "draft_non_production",
    }
    assert CONTROL._health_payload_ready(payload, spec, 200) is True
    payload["verdict"] = "WRONG"
    assert CONTROL._health_payload_ready(payload, spec, 200) is False


def test_chatops_health_requires_exact_verdict():
    spec = CONTROL.GROUPS["chatops"].probes[0]
    assert CONTROL._health_payload_ready(
        {
            "schema_id": "ion.chatops_bridge.v1",
            "ok": True,
            "verdict": "ION_CHATOPS_BRIDGE_READY",
        },
        spec,
        200,
    ) is True


def test_actions_healthy_requires_exact_pair_listener_and_probes():
    spec = CONTROL.GROUPS["actions"]
    result = CONTROL._classify_group(
        spec,
        {
            CONTROL.ACTION_LOCAL_UNIT: _unit(active=True, enabled=True, pid=101),
            CONTROL.ACTION_TUNNEL_UNIT: _unit(active=True, enabled=True, pid=202),
        },
        {"local": _probe(True), "public": _probe(True)},
        _inventory(
            action_gateway=[101],
            ion_actions_tunnel=[202],
            ion_actions_expected_origin=[202],
            cloudflared_tunnels=[202],
        ),
        {8777: _listener(8777, listening=True, pid=101)},
    )
    assert result["overall"] == "healthy"
    assert result["running"] is True
    assert result["startup_enabled"] is True
    assert result["controllable"] is True
    assert result["conflicts"] == []


def test_active_but_disabled_group_is_degraded():
    spec = CONTROL.GROUPS["chatops"]
    result = CONTROL._classify_group(
        spec,
        {CONTROL.CHATOPS_UNIT: _unit(active=True, enabled=False, pid=303)},
        {"local": _probe(True)},
        _inventory(chatops=[303]),
        {8767: _listener(8767, listening=True, pid=303)},
    )
    assert result["overall"] == "degraded"
    assert result["toggle_on"] is True
    assert result["startup_enabled"] is False


def test_duplicate_action_tunnel_is_conflict():
    spec = CONTROL.GROUPS["actions"]
    result = CONTROL._classify_group(
        spec,
        {
            CONTROL.ACTION_LOCAL_UNIT: _unit(active=True, enabled=True, pid=101),
            CONTROL.ACTION_TUNNEL_UNIT: _unit(active=True, enabled=True, pid=202),
        },
        {"local": _probe(True), "public": _probe(True)},
        _inventory(
            action_gateway=[101],
            ion_actions_tunnel=[202, 203],
            ion_actions_expected_origin=[202],
            cloudflared_tunnels=[202, 203],
        ),
        {8777: _listener(8777, listening=True, pid=101)},
    )
    assert result["overall"] == "conflict"
    assert "duplicate_ion_actions_tunnel_process" in result["conflicts"]


def test_non_loopback_or_wrong_listener_owner_is_conflict():
    spec = CONTROL.GROUPS["chatops"]
    result = CONTROL._classify_group(
        spec,
        {CONTROL.CHATOPS_UNIT: _unit(active=True, enabled=True, pid=303)},
        {"local": _probe(True)},
        _inventory(chatops=[303]),
        {8767: _listener(8767, listening=True, pid=999, loopback_only=False)},
    )
    assert result["overall"] == "conflict"
    assert "non_loopback_8767_listener" in result["conflicts"]
    assert "unmanaged_8767_listener" in result["conflicts"]


def test_public_ready_while_managed_tunnel_inactive_is_conflict():
    spec = CONTROL.GROUPS["helixion"]
    result = CONTROL._classify_group(
        spec,
        {
            CONTROL.HELIXION_LOCAL_UNIT: _unit(active=False, enabled=False, pid=0),
            CONTROL.HELIXION_TUNNEL_UNIT: _unit(active=False, enabled=False, pid=0),
        },
        {"local": _probe(False), "public": _probe(True)},
        _inventory(),
        {8765: _listener(8765, listening=False)},
    )
    assert result["overall"] == "conflict"
    assert "public_endpoint_live_while_tunnel_inactive" in result["conflicts"]


def test_global_mixed_healthy_and_intentionally_off_is_healthy():
    result = CONTROL._classify_global(
        {
            "helixion": {"overall": "off", "toggle_on": False, "conflicts": []},
            "actions": {"overall": "healthy", "toggle_on": True, "conflicts": []},
            "chatops": {"overall": "healthy", "toggle_on": True, "conflicts": []},
        }
    )
    assert result["overall"] == "healthy"
    assert result["on_group_count"] == 2
    assert result["off_group_count"] == 1


def test_missing_unit_is_conflict_and_not_controllable():
    spec = CONTROL.GROUPS["chatops"]
    missing = _unit(active=False, enabled=False, pid=0)
    missing["available"] = False
    result = CONTROL._classify_group(
        spec,
        {CONTROL.CHATOPS_UNIT: missing},
        {"local": _probe(False)},
        _inventory(),
        {8767: _listener(8767, listening=False)},
    )
    assert result["overall"] == "conflict"
    assert result["controllable"] is False
    assert "chatops_unit_unavailable" in result["conflicts"]


def test_listener_inspection_failure_or_missing_listener_is_degraded():
    spec = CONTROL.GROUPS["chatops"]
    units = {CONTROL.CHATOPS_UNIT: _unit(active=True, enabled=True, pid=303)}
    inventory = _inventory(chatops=[303])
    failed_listener = _listener(8767, listening=False)
    failed_listener["finding"] = "listener_query_failed"
    failed = CONTROL._classify_group(
        spec,
        units,
        {"local": _probe(True)},
        inventory,
        {8767: failed_listener},
    )
    missing = CONTROL._classify_group(
        spec,
        units,
        {"local": _probe(True)},
        inventory,
        {8767: _listener(8767, listening=False)},
    )
    assert failed["overall"] == "degraded"
    assert "listener_8767_inspection_failed" in failed["findings"]
    assert missing["overall"] == "degraded"
    assert "listener_8767_missing" in missing["findings"]


def test_partial_pair_reports_login_partial():
    spec = CONTROL.GROUPS["actions"]
    result = CONTROL._classify_group(
        spec,
        {
            CONTROL.ACTION_LOCAL_UNIT: _unit(active=False, enabled=True, pid=0),
            CONTROL.ACTION_TUNNEL_UNIT: _unit(active=False, enabled=False, pid=0),
        },
        {"local": _probe(False), "public": _probe(False)},
        _inventory(),
        {8777: _listener(8777, listening=False)},
    )
    assert result["overall"] == "degraded"
    assert result["startup_enabled"] is False
    assert result["startup_state"] == "partial"


def test_linked_or_runtime_enabled_unit_is_not_persistent_login_enabled():
    for state in ("linked", "linked-runtime", "enabled-runtime"):
        completed = SimpleNamespace(
            returncode=0,
            stdout=(
                f"Id={CONTROL.CHATOPS_UNIT}\n"
                "LoadState=loaded\nActiveState=inactive\nSubState=dead\n"
                f"UnitFileState={state}\nMainPID=0\nNRestarts=0\n"
            ),
            stderr="",
        )
        with patch.object(CONTROL.subprocess, "run", return_value=completed):
            assert CONTROL._unit_status(CONTROL.CHATOPS_UNIT)["enabled"] is False


def test_masked_or_unloaded_unit_is_unavailable():
    completed = SimpleNamespace(
        returncode=0,
        stdout=(
            f"Id={CONTROL.CHATOPS_UNIT}\n"
            "LoadState=masked\nActiveState=inactive\nSubState=dead\n"
            "UnitFileState=masked\nMainPID=0\nNRestarts=0\n"
        ),
        stderr="",
    )
    with patch.object(CONTROL.subprocess, "run", return_value=completed):
        result = CONTROL._unit_status(CONTROL.CHATOPS_UNIT)
    assert result["available"] is False
    assert result["finding"] == "unit_identity_unavailable"


def test_named_tunnel_duplicates_count_even_when_one_uses_config_ingress():
    inventory = _inventory()
    CONTROL._record_process(
        inventory,
        201,
        [
            "/home/sev/.local/bin/cloudflared",
            "--no-autoupdate",
            "tunnel",
            "run",
            "--url",
            "http://127.0.0.1:8777",
            "ion-actions",
        ],
    )
    CONTROL._record_process(
        inventory,
        202,
        ["/home/sev/.local/bin/cloudflared", "tunnel", "run", "ion-actions"],
    )
    assert inventory["ion_actions_tunnel"] == [201, 202]
    assert inventory["ion_actions_expected_origin"] == [201]


def test_apply_action_does_not_start_tunnel_when_managed_origin_gate_fails():
    calls = []
    before = {"groups": {"actions": {}}}
    after = {
        "groups": {
            "actions": {
                "running": False,
                "startup_enabled": False,
                "toggle_on": True,
                "overall": "degraded",
            }
        }
    }

    def fake_systemctl(action, unit):
        calls.append((action, unit))
        return {"ok": True, "returncode": 0, "finding": "ok", "diagnostic": ""}

    with (
        patch.object(CONTROL, "build_status", side_effect=[before, after]),
        patch.object(CONTROL, "_systemctl", side_effect=fake_systemctl),
        patch.object(CONTROL, "_wait_until", return_value=False),
        patch.object(CONTROL, "_write_receipt", return_value="receipt.json"),
    ):
        result = CONTROL.apply_action("actions", "on")

    assert calls == [("enable_now", CONTROL.ACTION_LOCAL_UNIT)]
    assert result["ok"] is False
    assert result["health_ok"] is False


def test_apply_action_uses_pair_start_and_stop_order():
    calls = []
    before = {"groups": {"actions": {}}}
    on_after = {
        "groups": {
            "actions": {
                "running": True,
                "startup_enabled": True,
                "toggle_on": True,
                "overall": "healthy",
            }
        }
    }
    off_after = {
        "groups": {
            "actions": {
                "running": False,
                "startup_enabled": False,
                "toggle_on": False,
                "overall": "off",
            }
        }
    }

    def fake_systemctl(action, unit):
        calls.append((action, unit))
        return {"ok": True, "returncode": 0, "finding": "ok", "diagnostic": ""}

    with (
        patch.object(CONTROL, "build_status", side_effect=[before, on_after, before, off_after]),
        patch.object(CONTROL, "_systemctl", side_effect=fake_systemctl),
        patch.object(CONTROL, "_wait_until", return_value=True),
        patch.object(CONTROL, "_write_receipt", return_value="receipt.json"),
    ):
        on_result = CONTROL.apply_action("actions", "on")
        off_result = CONTROL.apply_action("actions", "off")

    assert calls == [
        ("enable_now", CONTROL.ACTION_LOCAL_UNIT),
        ("enable_now", CONTROL.ACTION_TUNNEL_UNIT),
        ("disable_now", CONTROL.ACTION_TUNNEL_UNIT),
        ("disable_now", CONTROL.ACTION_LOCAL_UNIT),
    ]
    assert on_result["ok"] is True and on_result["health_ok"] is True
    assert off_result["ok"] is True and off_result["health_ok"] is True


def test_global_precedence_for_all_off_degraded_and_conflict():
    all_off = {
        group_id: {"overall": "off", "toggle_on": False, "conflicts": [], "startup_state": "disabled"}
        for group_id in CONTROL.GROUPS
    }
    assert CONTROL._classify_global(all_off)["overall"] == "off"
    degraded = dict(all_off)
    degraded["actions"] = {"overall": "degraded", "toggle_on": True, "conflicts": []}
    assert CONTROL._classify_global(degraded)["overall"] == "degraded"
    conflict = dict(degraded)
    conflict["chatops"] = {"overall": "conflict", "toggle_on": True, "conflicts": ["bad"]}
    assert CONTROL._classify_global(conflict)["overall"] == "conflict"


def test_arbitrary_unit_and_port_are_rejected():
    with pytest.raises(ValueError, match="control_not_allowed"):
        CONTROL._systemctl("enable_now", "arbitrary.service")
    with pytest.raises(ValueError, match="port_not_allowed"):
        CONTROL._listener_status(9999)


def test_action_parser_is_fixed_and_preserves_helixion_aliases():
    assert CONTROL._parse_action("on") == ("group", "helixion", "on")
    assert CONTROL._parse_action("actions-off") == ("group", "actions", "off")
    assert CONTROL._parse_action("chatops-on") == ("group", "chatops", "on")
    assert CONTROL._parse_action("queue-on") == ("timer", "queue", "on")
    assert CONTROL._parse_action("loop-off") == ("timer", "loop", "off")
    with pytest.raises(ValueError, match="action_not_allowed"):
        CONTROL._parse_action("arbitrary.service-on")


def test_control_uses_fixed_non_shell_argv_and_pair_order():
    calls = []

    def fake_run(argv, *, timeout=15.0):
        calls.append((argv, timeout))
        return {"ok": True, "returncode": 0, "finding": "ok", "diagnostic": ""}

    with patch.object(CONTROL, "_run", side_effect=fake_run):
        for unit in CONTROL.GROUPS["actions"].stop_order:
            CONTROL._systemctl("disable_now", unit)
        for unit in CONTROL.GROUPS["actions"].start_order:
            CONTROL._systemctl("enable_now", unit)
        CONTROL._systemctl("disable_now", CONTROL.CHATOPS_UNIT)

    assert [call[0] for call in calls] == [
        ["systemctl", "--user", "disable", "--now", "ion-action-tunnel.service"],
        ["systemctl", "--user", "disable", "--now", "ion-action-gateway.service"],
        ["systemctl", "--user", "enable", "--now", "ion-action-gateway.service"],
        ["systemctl", "--user", "enable", "--now", "ion-action-tunnel.service"],
        ["systemctl", "--user", "disable", "--now", "ion-chatops.service"],
    ]


def test_receipts_are_group_scoped_and_unique(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    first = CONTROL._write_receipt("actions", "off", {}, {}, {"ok": True})
    second = CONTROL._write_receipt("chatops", "off", {}, {}, {"ok": True})
    assert first != second
    assert "actions_off" in Path(first).name
    assert "chatops_off" in Path(second).name
    assert Path(first).stat().st_mode & 0o777 == 0o600


def test_extension_has_three_fixed_async_switches_and_no_shell_spawn():
    source = (EXTENSION_ROOT / "extension.js").read_text(encoding="utf-8")
    assert "GROUP_IDS = ['helixion', 'actions', 'chatops']" in source
    assert "`${groupId}-${state ? 'on' : 'off'}`" in source
    assert "Gio.Subprocess.new" in source
    assert "spawn_command_line" not in source
    assert "Util.spawn" not in source
    assert "this._generation++" in source
    assert "login partial" in source
    assert "GLib.source_remove" in source


def test_queue_section_counts_from_fixture_rows(tmp_path, monkeypatch):
    queue_path = tmp_path / "queue.json"
    queue_path.write_text(
        json.dumps(
            {
                "rows": [
                    {"status": "pending"},
                    {"status": "executed"},
                    {"status": "quarantined"},
                    {"status": "executed"},
                ]
            }
        ),
        encoding="utf-8",
    )
    tick_path = tmp_path / "tick.json"
    tick_path.write_text(
        json.dumps(
            {
                "verdict": "TEST_VERDICT",
                "tick_at": "2026-08-08T00:00:00Z",
                "absence_alerts": ["alert_one"],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(CONTROL, "DURABLE_SPAWN_QUEUE_PATH", queue_path)
    monkeypatch.setattr(CONTROL, "LAST_DURABLE_DRAIN_TICK_PATH", tick_path)
    monkeypatch.setattr(CONTROL, "PROMPT_SPAWN_RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(CONTROL, "WORKER_SHIFT_BOARD_PATH", tmp_path / "missing_board.json")
    monkeypatch.setattr(CONTROL, "HUMAN_GATE_QUEUE_PATH", tmp_path / "missing_gate.json")
    monkeypatch.setattr(CONTROL, "RUNTIME_ABSENCE_SURFACE_PATH", tmp_path / "missing_absence.json")
    monkeypatch.setattr(CONTROL, "LAST_AUTONOMOUS_LOOP_RESULT_PATH", tmp_path / "missing_loop.json")
    monkeypatch.setattr(CONTROL, "SCHEDULER_LAST_TICK_PATH", tmp_path / "missing_tick.json")

    with (
        patch.object(CONTROL, "_unit_status", return_value={"active": True, "enabled": True}),
        patch.object(CONTROL, "_read_process_inventory", return_value=_inventory()),
        patch.object(CONTROL, "_listener_status", side_effect=lambda port: _listener(port, listening=False)),
        patch.object(CONTROL, "_probe", return_value=_probe(False)),
    ):
        status = CONTROL.build_status()

    queue = status["queue"]
    assert queue["pending_count"] == 1
    assert queue["executed_count"] == 2
    assert queue["quarantined_count"] == 1
    assert queue["last_drain_verdict"] == "TEST_VERDICT"
    assert queue["absence_alerts"] == ["alert_one"]
    assert queue["drain_timer"]["unit"] == CONTROL.DRAIN_TIMER_UNIT


def test_in_flight_vs_finished_run_detection(tmp_path, monkeypatch):
    runs_root = tmp_path / "runs"
    in_flight = runs_root / "prompt_spawn_2026-08-08T120000+0000_a"
    finished = runs_root / "prompt_spawn_2026-08-08T110000+0000_b"
    in_flight.mkdir(parents=True)
    finished.mkdir(parents=True)
    (in_flight / "spawn_admission.json").write_text(
        json.dumps({"domain_id": "domain.a", "work_class": "code_implementation"}),
        encoding="utf-8",
    )
    (finished / "spawn_admission.json").write_text(
        json.dumps({"domain_id": "domain.b", "work_class": "audit_observation"}),
        encoding="utf-8",
    )
    (finished / "task_return.json").write_text("{}", encoding="utf-8")

    monkeypatch.setattr(CONTROL, "PROMPT_SPAWN_RUNS_DIR", runs_root)
    agents = CONTROL._scan_prompt_spawn_runs()
    assert agents["in_flight_count"] == 1
    by_id = {row["run_id"]: row for row in agents["recent_runs"]}
    assert by_id[in_flight.name]["finished"] is False
    assert by_id[finished.name]["finished"] is True


def test_timer_actions_map_to_compiled_units_only():
    calls = []

    def fake_systemctl(action, unit):
        calls.append((action, unit))
        return {"ok": True, "returncode": 0, "finding": "ok", "diagnostic": ""}

    before = {"queue": {"drain_timer": {"enabled": False}, "loop_timer": {"enabled": True}}}
    after_on = {
        "queue": {
            "drain_timer": {"enabled": True},
            "loop_timer": {"enabled": True},
        }
    }
    after_off = {
        "queue": {
            "drain_timer": {"enabled": True},
            "loop_timer": {"enabled": False},
        }
    }

    with (
        patch.object(CONTROL, "build_status", side_effect=[before, after_on, before, after_off]),
        patch.object(CONTROL, "_systemctl", side_effect=fake_systemctl),
        patch.object(CONTROL, "_write_receipt", return_value="receipt.json"),
    ):
        on_result = CONTROL.apply_timer_action("queue", "on")
        off_result = CONTROL.apply_timer_action("loop", "off")

    assert calls == [
        ("enable_now", CONTROL.DRAIN_TIMER_UNIT),
        ("disable_now", CONTROL.LOOP_TIMER_UNIT),
    ]
    assert on_result["ok"] is True
    assert off_result["ok"] is True
    with pytest.raises(ValueError, match="action_not_allowed"):
        CONTROL.apply_timer_action("helixion", "on")


def test_open_latest_run_view_without_terminal_emulator(tmp_path, monkeypatch):
    runs_root = tmp_path / "runs"
    run_dir = runs_root / "prompt_spawn_2026-08-08T120000+0000_z"
    run_dir.mkdir(parents=True)
    (run_dir / "output.md").write_text("hello", encoding="utf-8")
    monkeypatch.setattr(CONTROL, "PROMPT_SPAWN_RUNS_DIR", runs_root)
    with patch.object(CONTROL.shutil, "which", return_value=None):
        result = CONTROL.open_latest_run_view()
    assert result == {"ok": False, "reason": "no_terminal_emulator"}


def test_corrupt_json_degrades_only_its_section(tmp_path, monkeypatch):
    queue_path = tmp_path / "queue.json"
    queue_path.write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(CONTROL, "DURABLE_SPAWN_QUEUE_PATH", queue_path)
    monkeypatch.setattr(CONTROL, "LAST_DURABLE_DRAIN_TICK_PATH", tmp_path / "missing.json")
    monkeypatch.setattr(CONTROL, "PROMPT_SPAWN_RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(CONTROL, "WORKER_SHIFT_BOARD_PATH", tmp_path / "missing_board.json")
    section = CONTROL._build_queue_section()
    assert "error" in section
    assert "pending_count" not in section
