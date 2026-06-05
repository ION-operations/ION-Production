import json
from pathlib import Path

from kernel.ion_agent_comms import send_agent_message
from kernel.ion_steward_dispatcher import (
    build_steward_dispatcher_projection,
    pause_steward_dispatcher,
    route_steward_dispatcher,
    run_steward_dispatcher_runner,
    tick_steward_dispatcher,
)


def _write(root: Path, rel: str, text: str = "x\n") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seed_root(root: Path) -> None:
    _write(root, "pyproject.toml", "[project]\nname = \"ion-dispatcher-test\"\n")
    _write(root, "ION/REPO_AUTHORITY.md", "# authority\n")


def test_steward_dispatcher_projection_reads_real_comms_runs_without_fake_agents(tmp_path: Path):
    _seed_root(tmp_path)
    run = {
        "run_id": "agent_run_dispatcher_smoke",
        "status": "active",
        "objective": "Dispatcher smoke",
        "target_roles": ["role.ionologist"],
        "completion_state": {"state": "pending_directive", "directive_state": {"pending_directive_count": 1}},
        "worker_runtime": {"has_active_worker": False, "active_worker_count": 0},
        "policy_gate": {"state": "within_limits"},
        "audit_gate": {"clean": False},
        "work_items": [{"agent_role_id": "role.ionologist", "workpack_path": "ION/workpack.json", "response_state": "queued"}],
        "message_paths": ["ION/message.json"],
        "task_return_count": 0,
        "agent_response_count": 0,
    }

    projection = build_steward_dispatcher_projection(
        tmp_path,
        agents=[
            {
                "role_id": "role.ionologist",
                "communication_profile": {"available_for_comms": True},
            }
        ],
        domains=[{"domain_id": "domain.ion_system_definition"}],
        communications={"team_comms": {"runs": {"runs": [run]}}},
        runs={"queued_agent_codex_work_request_count": 0},
        domain_weaver={"gaps": [{"scope": "domain", "id": "domain.missing", "gap": "needs_agent_binding"}]},
    )

    assert projection["schema_id"] == "ion.steward_dispatcher.v1"
    assert projection["dispatcher_state"] == "actionable"
    assert projection["summary"]["actionable_run_count"] == 1
    assert projection["summary"]["pending_directive_count"] == 1
    assert projection["summary"]["domain_gap_count"] == 1
    assert projection["queue"][0]["next_action"] == "pickup_directive"
    assert projection["queue"][0]["assigned_agents"] == ["role.ionologist"]
    assert projection["policy"].startswith("Steward Dispatcher routes")
    assert projection["production_authority"] is False
    assert projection["live_execution_authority"] is False
    assert projection["accepted_state_authority"] is False


def test_steward_dispatcher_route_creates_real_comms_run_and_receipt(tmp_path: Path):
    _seed_root(tmp_path)

    result = route_steward_dispatcher(
        tmp_path,
        {
            "objective": "Ask Ionologist for a bounded decision.",
            "body": "@ionologist inspect this route and return no-followup if complete.",
            "dispatch_mode": "comms_only",
            "max_directives": 2,
            "automation_prompt_limit": 3,
        },
    )

    assert result["ok"] is True
    assert result["routed"] is True
    assert result["route_plan"]["target_roles"] == ["role.ionologist"]
    assert result["run_id"].startswith("agent_run_")
    assert (tmp_path / result["run_path"]).is_file()
    assert (tmp_path / result["receipt_path"]).is_file()
    run = json.loads((tmp_path / result["run_path"]).read_text(encoding="utf-8"))
    assert run["initiated_by"] == "steward_dispatcher"
    assert run["target_roles"] == ["role.ionologist"]
    assert run["policy"].startswith("Run pickup only processes explicit")


def test_steward_dispatcher_tick_calls_bounded_continue_and_records_receipt(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    captured: dict[str, dict] = {}

    def fake_continue(_root, payload):
        captured["payload"] = dict(payload)
        return {"ok": True, "run_id": payload["run_id"], "worker_start_count": 1, "production_authority": False, "live_execution_authority": False}

    monkeypatch.setattr("kernel.ion_steward_dispatcher.continue_agent_comms_run", fake_continue)

    result = tick_steward_dispatcher(
        tmp_path,
        {"run_id": "agent_run_dispatcher_smoke", "max_directives": 2, "max_worker_starts": 1},
    )

    assert result["ok"] is True
    assert captured["payload"]["run_id"] == "agent_run_dispatcher_smoke"
    assert captured["payload"]["max_directives"] == 2
    assert captured["payload"]["max_worker_starts"] == 1
    assert (tmp_path / result["receipt_path"]).is_file()


def test_steward_dispatcher_pause_blocks_route_until_resumed(tmp_path: Path):
    _seed_root(tmp_path)
    paused = pause_steward_dispatcher(tmp_path, {"paused": True, "reason": "test pause"})

    blocked = route_steward_dispatcher(
        tmp_path,
        {"objective": "Blocked route", "body": "@steward hold.", "dispatch_mode": "comms_only"},
    )

    resumed = pause_steward_dispatcher(tmp_path, {"paused": False, "reason": "resume"})
    sent = send_agent_message(tmp_path, from_role="operator", to_roles=["role.steward"], body="resume smoke")

    assert paused["ok"] is True
    assert blocked["ok"] is False
    assert blocked["finding"] == "dispatcher_paused"
    assert resumed["ok"] is True
    assert sent["ok"] is True


def test_steward_dispatcher_runner_ticks_actionable_runs_and_records_receipt(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    run = {
        "run_id": "agent_run_dispatcher_runner",
        "status": "active",
        "objective": "Runner smoke",
        "target_roles": ["role.ionologist"],
        "completion_state": {"state": "pending_directive", "directive_state": {"pending_directive_count": 1}},
        "worker_runtime": {"has_active_worker": False, "active_worker_count": 0},
        "policy_gate": {"state": "within_limits"},
        "audit_gate": {"clean": False},
        "work_items": [],
        "message_paths": ["ION/message.json"],
        "task_return_count": 0,
        "agent_response_count": 0,
    }
    tick_payloads: list[dict] = []

    def fake_runs_projection(_root, limit=100):
        return {"schema_id": "ion.agent_comms.runs.projection.v1", "runs": [run], "run_count": 1}

    def fake_tick(_root, payload):
        tick_payloads.append(dict(payload))
        return {
            "ok": True,
            "run_id": payload["run_id"],
            "tick_result": {"ok": True, "processed_directive_count": 1, "worker_start_count": 0, "return_sync_count": 0},
            "receipt_path": f"ION/05_context/current/steward_dispatcher/receipts/tick_{len(tick_payloads)}.json",
            "production_authority": False,
            "live_execution_authority": False,
        }

    monkeypatch.setattr("kernel.ion_steward_dispatcher.build_agent_comms_runs_projection", fake_runs_projection)
    monkeypatch.setattr("kernel.ion_steward_dispatcher.tick_steward_dispatcher", fake_tick)

    result = run_steward_dispatcher_runner(
        tmp_path,
        {"max_ticks": 2, "max_processed_directives": 4, "max_worker_starts": 2, "max_worker_starts_per_tick": 0},
    )

    assert result["ok"] is True
    assert result["finding"] == "tick_limit_reached"
    assert result["tick_count"] == 2
    assert result["usage"]["processed_directive_count"] == 2
    assert [payload["run_id"] for payload in tick_payloads] == ["agent_run_dispatcher_runner", "agent_run_dispatcher_runner"]
    assert tick_payloads[0]["max_worker_starts"] == 0
    assert (tmp_path / result["receipt_path"]).is_file()


def test_steward_dispatcher_runner_stops_on_worker_limit(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    run = {
        "run_id": "agent_run_worker_limit",
        "status": "active",
        "objective": "Runner worker limit",
        "target_roles": ["role.ionologist"],
        "completion_state": {"state": "ready_to_start_worker", "directive_state": {"pending_directive_count": 0}},
        "worker_runtime": {"has_active_worker": False, "active_worker_count": 0},
        "policy_gate": {"state": "within_limits"},
        "audit_gate": {"clean": False},
        "work_items": [{"agent_role_id": "role.ionologist", "workpack_path": "ION/workpack.json"}],
        "task_return_count": 0,
        "agent_response_count": 0,
    }

    monkeypatch.setattr("kernel.ion_steward_dispatcher.build_agent_comms_runs_projection", lambda _root, limit=100: {"runs": [run], "run_count": 1})
    monkeypatch.setattr(
        "kernel.ion_steward_dispatcher.tick_steward_dispatcher",
        lambda _root, payload: {
            "ok": True,
            "run_id": payload["run_id"],
            "tick_result": {"ok": True, "processed_directive_count": 0, "worker_start_count": 1, "return_sync_count": 0},
            "receipt_path": "ION/05_context/current/steward_dispatcher/receipts/tick_worker.json",
            "production_authority": False,
            "live_execution_authority": False,
        },
    )

    result = run_steward_dispatcher_runner(tmp_path, {"max_ticks": 5, "max_worker_starts": 1})

    assert result["ok"] is True
    assert result["finding"] == "worker_start_limit_reached"
    assert result["tick_count"] == 1
    assert result["usage"]["worker_start_count"] == 1


def test_steward_dispatcher_runner_honors_pause(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    pause_steward_dispatcher(tmp_path, {"paused": True, "reason": "runner pause"})

    def fake_tick(*_args, **_kwargs):
        raise AssertionError("paused runner must not tick")

    monkeypatch.setattr("kernel.ion_steward_dispatcher.tick_steward_dispatcher", fake_tick)

    result = run_steward_dispatcher_runner(tmp_path, {"max_ticks": 2})

    assert result["ok"] is False
    assert result["finding"] == "dispatcher_paused"
    assert result["tick_count"] == 0
    assert (tmp_path / result["receipt_path"]).is_file()
