import io
import json
import os
from pathlib import Path

from kernel import ion_codex_app_server_bridge as bridge
from kernel.ion_action_mcp_branch_leaders import action_branch_describe, action_branch_invoke
from kernel.ion_codex_app_server_bridge import CONFIRMATION_TOKEN, invoke_codex_app_server_route


THREAD_ID = "019e8b2b-c770-71d3-b2d8-e4c1c14eba0b"


def _seed_root(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname='ion-test'\n", encoding="utf-8")
    authority = root / "ION/REPO_AUTHORITY.md"
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("# authority\n", encoding="utf-8")


def _seed_root_with_registry(root: Path) -> None:
    _seed_root(root)
    source = Path.cwd() / "ION/03_registry/ion_action_mcp_branch_leader_registry.yaml"
    target = root / "ION/03_registry/ion_action_mcp_branch_leader_registry.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def _fake_rpc_for_read(requests, *, timeout_seconds=12, wait_for_methods=None):
    response_by_id = {
        "initialize": {
            "id": "initialize",
            "result": {
                "userAgent": "ion-test/0.136.0",
                "codexHome": "/home/sev/.codex",
                "platformFamily": "unix",
                "platformOs": "linux",
            },
        },
        "thread_list": {
            "id": "thread_list",
            "result": {
                "data": [
                    {
                        "id": THREAD_ID,
                        "sessionId": THREAD_ID,
                        "cwd": "/home/sev/ION - Production",
                        "status": {"type": "idle"},
                        "updatedAt": 1780451362,
                    }
                ]
            },
        },
        "resume": {
            "id": "resume",
            "result": {
                "thread": {
                    "id": THREAD_ID,
                    "sessionId": THREAD_ID,
                    "cwd": "/home/sev/ION - Production",
                    "status": {"type": "idle"},
                    "updatedAt": 1780451362,
                },
                "model": "gpt-5.5",
                "modelProvider": "openai",
                "cwd": "/home/sev/ION - Production",
                "sandbox": {"type": "workspaceWrite", "writableRoots": [], "networkAccess": False},
                "initialTurnsPage": {"data": [{"id": "turn-1", "status": "completed", "items": []}]},
            },
        },
        "turns": {"id": "turns", "result": {"data": [{"id": "turn-1", "status": "completed", "items": []}]}},
        "loaded": {"id": "loaded", "result": {"data": []}},
    }
    selected = {}
    responses = []
    for request in requests:
        request_id = request.get("id")
        if request_id in response_by_id:
            selected[request_id] = response_by_id[request_id]
            responses.append(response_by_id[request_id])
    return {
        "ok": True,
        "command_argv": ["codex", "app-server", "--listen", "stdio://"],
        "responses": responses,
        "response_by_id": selected,
        "notifications": [{"method": "remoteControl/status/changed", "params": {"status": "disabled"}}],
        "pending_request_ids": [],
        "stderr_lines": [],
        "timed_out": False,
    }


def _touch_executable(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\n", encoding="utf-8")
    path.chmod(0o755)


def _write_fake_codex_app_server(path: Path, *, turn_id: str = "real-turn-complete", turn_status: str = "completed") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        f"TURN_ID = {turn_id!r}\n"
        f"TURN_STATUS = {turn_status!r}\n"
        "def emit(payload):\n"
        "    print(json.dumps(payload, separators=(',', ':')), flush=True)\n"
        "for line in sys.stdin:\n"
        "    req = json.loads(line)\n"
        "    rid = req.get('id')\n"
        "    if rid == 'initialize':\n"
        "        emit({'id': rid, 'result': {'userAgent': 'ion-test/fake-app-server'}})\n"
        "    elif rid == 'resume':\n"
        "        emit({'id': rid, 'result': {'thread': {'id': req['params']['threadId'], 'status': {'type': 'idle'}}}})\n"
        "    elif rid == 'turn_start':\n"
        "        emit({'id': rid, 'result': {'turn': {'id': TURN_ID, 'status': 'inProgress'}}})\n"
        "        emit({'method': 'item/completed', 'params': {'turnId': TURN_ID}})\n"
        "        emit({'method': 'turn/completed', 'params': {'turnId': TURN_ID}})\n"
        "        emit({'method': 'thread/status/changed', 'params': {'status': {'type': 'idle'}}})\n"
        "    elif rid == 'turns':\n"
        "        emit({'id': rid, 'result': {'data': [{'id': TURN_ID, 'status': TURN_STATUS, 'items': []}]}})\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


class _FakeJsonrpcProcess:
    def __init__(self, stdout_messages: list[dict], *, stderr: str = "") -> None:
        self.stdin = io.StringIO()
        self.stdout = io.StringIO("".join(json.dumps(message, separators=(",", ":")) + "\n" for message in stdout_messages))
        self.stderr = io.StringIO(stderr)
        self.returncode = None

    def poll(self):
        return self.returncode

    def terminate(self) -> None:
        self.returncode = 0

    def wait(self, timeout=None):
        self.returncode = 0 if self.returncode is None else self.returncode
        return self.returncode

    def kill(self) -> None:
        self.returncode = -9


def _fake_process_factory(stdout_messages: list[dict], *, stderr: str = ""):
    def factory(*_args, **_kwargs):
        return _FakeJsonrpcProcess(stdout_messages, stderr=stderr)

    return factory


def _stage1_real_runner_helper(
    root: Path,
    *,
    carrier_id: str,
    stdout_messages: list[dict] | None = None,
    process_factory=None,
    timeout_seconds: int = 5,
    wait_for_completion: bool = False,
) -> dict:
    _seed_root(root)
    prompt = f"stage1 helper {carrier_id}"
    args = {
        "thread_id": THREAD_ID,
        "carrier_id": carrier_id,
        "prompt": prompt,
        "cwd": root.as_posix(),
        "timeout_seconds": timeout_seconds,
        "wait_for_completion": wait_for_completion,
        "_command_argv": ["fake-codex", "app-server", "--listen", "stdio://"],
        "_process_factory": process_factory or _fake_process_factory(stdout_messages or []),
    }
    carrier_identity = bridge._resolve_persistent_carrier_identity(root, THREAD_ID, args)
    carrier_key = str(carrier_identity["canonical_carrier_id"])
    idempotency_key_safe = bridge._safe_idempotency_key(carrier_id)
    sandbox, writable_root_resolution = bridge._sandbox_policy_details(args, root=root)
    return bridge._persistent_carrier_start_real_runner(
        root,
        args,
        thread_id=THREAD_ID,
        prompt_raw=prompt,
        prompt=bridge._redact(prompt, limit=8_000),
        carrier_identity=carrier_identity,
        carrier_key=carrier_key,
        idempotency_key_safe=idempotency_key_safe,
        prompt_hash=bridge._prompt_sha256(prompt),
        sandbox=sandbox,
        writable_root_resolution=writable_root_resolution,
        paths=bridge._persistent_carrier_paths(root, THREAD_ID, carrier_key),
        stale_after_seconds=180,
        heartbeat_interval_seconds=15,
    )


def _stage1_base_messages(turn_id: str = "stage1-turn", *, turn_status: str = "completed") -> list[dict]:
    return [
        {"id": "initialize", "result": {"userAgent": "ion-test/fake-process"}},
        {"id": "resume", "result": {"thread": {"id": THREAD_ID, "status": {"type": "idle"}}}},
        {"id": "turn_start", "result": {"turn": {"id": turn_id, "status": "inProgress"}}},
        {"id": "turns", "result": {"data": [{"id": turn_id, "status": turn_status, "items": []}]}},
    ]


def _write_turn_receipt(root: Path, key: str, turn_id: str, *, timestamp: int) -> dict:
    paths = bridge._run_paths(root, THREAD_ID, key)
    paths["receipt"].parent.mkdir(parents=True, exist_ok=True)
    paths["receipt"].write_text(
        json.dumps(
            {
                "created_at": f"2026-06-04T20:{timestamp % 60:02d}:00+00:00",
                "updated_at": f"2026-06-04T20:{timestamp % 60:02d}:10+00:00",
                "submit_state": "submitted",
                "submitted": True,
                "turn_id": turn_id,
                "turn_start_error": None,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    os.utime(paths["receipt"], (timestamp, timestamp))
    return paths


def test_codex_app_server_command_uses_listen_stdio(monkeypatch):
    monkeypatch.setattr(bridge, "_codex_binary", lambda: "/tmp/current-codex")

    assert bridge._app_server_command() == ["/tmp/current-codex", "app-server", "--listen", "stdio://"]


def test_codex_app_server_binary_honors_env_override(tmp_path: Path, monkeypatch):
    env_codex = tmp_path / "bin/codex-env"
    _touch_executable(env_codex)
    monkeypatch.setenv(bridge.CODEX_APP_SERVER_BINARY_ENV, env_codex.as_posix())
    monkeypatch.setattr(bridge, "_codex_binary_supports_app_server_stdio", lambda candidate: True)

    assert bridge._codex_binary() == env_codex.as_posix()


def test_codex_app_server_binary_prefers_npm_global_before_path(tmp_path: Path, monkeypatch):
    home = tmp_path / "home"
    npm_codex = home / ".npm-global/bin/codex"
    path_codex = tmp_path / "usr/local/bin/codex"
    _touch_executable(npm_codex)
    _touch_executable(path_codex)
    monkeypatch.delenv(bridge.CODEX_APP_SERVER_BINARY_ENV, raising=False)
    monkeypatch.setattr(bridge.Path, "home", staticmethod(lambda: home))
    monkeypatch.setattr(bridge.shutil, "which", lambda name: path_codex.as_posix() if name == "codex" else None)
    monkeypatch.setattr(bridge, "_codex_binary_supports_app_server_stdio", lambda candidate: True)

    assert bridge._codex_binary() == npm_codex.as_posix()


def test_codex_app_server_routes_visible_through_action_branch_describe():
    described = action_branch_describe(Path.cwd(), branch_id="codex_app_server", depth="full")

    assert described["ok"] is True
    routes = {route["route_id"]: route for route in described["branch"]["routes"]}
    assert {
        "app_server_status",
        "thread_list",
        "thread_loaded_list",
        "thread_resume_preview",
        "thread_resume",
        "thread_read",
        "thread_turns_list",
        "thread_turn_read_by_id",
        "turn_start_preview",
        "turn_start",
        "turn_poll",
        "turn_status",
        "persistent_carrier_preview",
        "persistent_carrier_start_preview",
        "persistent_carrier_start",
        "persistent_carrier_status",
        "persistent_carrier_stop",
    } <= set(routes)
    assert routes["thread_resume"]["mutates_state"] is False
    assert routes["thread_turn_read_by_id"]["mutates_state"] is False
    assert routes["turn_start_preview"]["mutates_state"] is False
    assert routes["turn_start"]["mutates_state"] is True
    assert routes["turn_poll"]["mutates_state"] is False
    assert routes["persistent_carrier_preview"]["mutates_state"] is False
    assert routes["persistent_carrier_start_preview"]["mutates_state"] is False
    assert routes["persistent_carrier_start"]["mutates_state"] is True
    assert routes["persistent_carrier_status"]["mutates_state"] is False
    assert routes["persistent_carrier_stop"]["mutates_state"] is True
    assert routes["turn_start"]["confirmation_required"] == CONFIRMATION_TOKEN
    assert routes["turn_start"]["idempotency_required"] is True
    assert routes["persistent_carrier_start"]["confirmation_required"] == CONFIRMATION_TOKEN
    assert routes["persistent_carrier_start"]["idempotency_required"] is True
    assert routes["persistent_carrier_stop"]["confirmation_required"] == CONFIRMATION_TOKEN
    assert routes["persistent_carrier_stop"]["idempotency_required"] is True
    assert "wait_until_visible" in routes["turn_start"]["args_schema"]["properties"]
    assert "writable_roots" in routes["turn_start"]["args_schema"]["properties"]
    assert "writableRoots" in routes["turn_start"]["args_schema"]["properties"]
    assert "mock_app_server" in routes["persistent_carrier_start"]["args_schema"]["properties"]
    assert "dry_run" in routes["persistent_carrier_start"]["args_schema"]["properties"]
    assert "allow_real_app_server" in routes["persistent_carrier_start"]["args_schema"]["properties"]
    assert "fake_app_server_runner" in routes["persistent_carrier_start"]["args_schema"]["properties"]
    assert "fake_turn_visible" in routes["persistent_carrier_start"]["args_schema"]["properties"]


def test_codex_app_server_thread_list_dispatch_is_read_only(monkeypatch):
    monkeypatch.setattr(bridge, "_run_app_server_jsonrpc", _fake_rpc_for_read)

    result = action_branch_invoke(
        Path.cwd(),
        branch_id="codex_app_server",
        route_id="thread_list",
        args={"limit": 5},
        expected_route_schema_version="v0",
    )

    assert result["ok"] is True
    assert result["mutates_active_state"] is False
    delegated = result["delegated_result"]
    assert delegated["thread_count"] == 1
    assert delegated["threads"][0]["thread_id"] == THREAD_ID
    assert delegated["production_authority"] is False


def test_codex_app_server_persistent_carrier_preview_is_read_only_and_normalizes_roots(tmp_path: Path):
    _seed_root(tmp_path)
    relative_root = "ION/05_context/current/domain_weaver/swarm_expansion/wave0_batch_a/returns"

    result = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_preview",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": "wave0a-action-gateway-steward",
            "prompt": "execute packet",
            "cwd": tmp_path.as_posix(),
            "sandbox": "workspace-write",
            "writable_roots": [relative_root],
            "heartbeat_interval_seconds": 10,
            "stale_after_seconds": 60,
        },
    )

    expected_root = (tmp_path / relative_root).resolve(strict=False).as_posix()
    assert result["ok"] is True
    assert result["persistent_carrier_not_started"] is True
    assert result["would_start_process"] is False
    assert result["mutates_active_state"] is False
    assert result["chosen_lane"] == "persistent_app_server_supervisor_first"
    assert result["sandbox_policy"]["writableRoots"] == [expected_root]
    assert result["writable_root_resolution"][0]["resolved"] == expected_root
    assert result["lifecycle_contract"]["lock_required"] is True
    assert result["lifecycle_contract"]["heartbeat_interval_seconds"] == 10
    assert "carrier.lock.json" in result["lifecycle_paths"]["lock"]
    assert not (tmp_path / "ION/05_context/current/chatgpt_connector/codex_app_server_persistent_carriers").exists()


def test_codex_app_server_persistent_carrier_preview_action_branch_invoke_parity():
    relative_root = "ION/05_context/current/domain_weaver/swarm_expansion/wave0_batch_a/returns"

    result = action_branch_invoke(
        Path.cwd(),
        branch_id="codex_app_server",
        route_id="persistent_carrier_preview",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": "wave0a-action-gateway-steward",
            "prompt": "preview only",
            "cwd": Path.cwd().as_posix(),
            "sandbox": "workspace-write",
            "writable_roots": [relative_root],
            "heartbeat_interval_seconds": 10,
            "stale_after_seconds": 60,
        },
        expected_route_schema_version="v0",
    )

    expected_root = (Path.cwd() / relative_root).resolve(strict=False).as_posix()
    assert result["ok"] is True
    assert result["mutates_active_state"] is False
    delegated = result["delegated_result"]
    assert delegated["ok"] is True
    assert delegated["route_id"] == "persistent_carrier_preview"
    assert delegated["persistent_carrier_not_started"] is True
    assert delegated["would_start_process"] is False
    assert delegated["mutates_active_state"] is False
    assert delegated["sandbox_policy"]["writableRoots"] == [expected_root]
    assert delegated["lifecycle_contract"]["lock_required"] is True


def test_codex_app_server_persistent_carrier_start_requires_gate_and_mock_mode(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    base_args = {
        "thread_id": THREAD_ID,
        "carrier_id": "mock-carrier",
        "prompt": "preview only",
        "mock_app_server": True,
    }

    no_idempotency = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_start",
        args={**base_args, "confirmation": CONFIRMATION_TOKEN},
    )
    no_confirmation = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_start",
        args={**base_args, "idempotency_key": "missing-confirmation"},
    )
    real_start_blocked = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_start",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": "mock-carrier",
            "prompt": "real start not enabled",
            "idempotency_key": "real-start-blocked",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )

    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert no_confirmation["ok"] is False
    assert no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"
    assert real_start_blocked["ok"] is False
    assert real_start_blocked["refusal_class"] == "LIVE_EXECUTION_NOT_ENABLED"
    assert real_start_blocked["allow_real_app_server_required"] is True
    assert real_start_blocked["mock_app_server_required"] is True

    route_messages = _stage1_base_messages("route-real-turn", turn_status="completed")
    real_start_without_fake_runner = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_start",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": "real-without-fake",
            "prompt": "real start gated but no fake runner",
            "allow_real_app_server": True,
            "idempotency_key": "real-without-fake",
            "confirmation": CONFIRMATION_TOKEN,
            "timeout_seconds": 5,
            "wait_for_completion": True,
            "_command_argv": ["fake-codex", "app-server", "--listen", "stdio://"],
            "_process_factory": _fake_process_factory(
                [
                    *route_messages[:3],
                    {"method": "item/completed", "params": {"turnId": "route-real-turn"}},
                    route_messages[3],
                ]
            ),
        },
    )
    assert real_start_without_fake_runner["ok"] is True
    assert real_start_without_fake_runner.get("refusal_class") != "REAL_PROCESS_SMOKE_NOT_ATTEMPTED"
    assert real_start_without_fake_runner["allow_real_app_server"] is True
    assert real_start_without_fake_runner["fake_app_server_runner"] is False
    assert real_start_without_fake_runner["real_process_runner_implemented"] is True
    assert real_start_without_fake_runner["real_app_server_process_started"] is True
    assert real_start_without_fake_runner["turn_submitted_to_real_codex"] is True
    assert real_start_without_fake_runner["completed"] is True
    assert real_start_without_fake_runner["durably_visible"] is True
    assert "mock_app_server_required" not in real_start_without_fake_runner


def test_codex_app_server_persistent_carrier_mock_start_writes_lifecycle_artifacts(tmp_path: Path):
    _seed_root(tmp_path)
    relative_root = "ION/05_context/current/domain_weaver/swarm_expansion/wave0_batch_a/returns"

    result = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_start",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": "mock-carrier",
            "prompt": "mock carrier start",
            "sandbox": "workspace-write",
            "writable_roots": [relative_root],
            "mock_app_server": True,
            "mock_turn_id": "mock-turn-start",
            "idempotency_key": "mock-start",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )

    assert result["ok"] is True
    assert result["mutates_active_state"] is True
    assert result["mock_app_server"] is True
    assert result["dry_run"] is True
    assert result["accepted_by_app_server"] is True
    assert result["completed"] is True
    assert result["durably_visible"] is True
    assert result["authority"]["accepted_state_claim"] is False
    assert result["authority"]["production_authority"] is False
    receipt = json.loads((tmp_path / result["receipt_path"]).read_text(encoding="utf-8"))
    lock = json.loads((tmp_path / result["lock_path"]).read_text(encoding="utf-8"))
    heartbeat = json.loads((tmp_path / result["heartbeat_path"]).read_text(encoding="utf-8"))
    final_status = json.loads((tmp_path / result["final_status_path"]).read_text(encoding="utf-8"))
    stdout_jsonl = (tmp_path / result["status"]["paths"]["stdout_jsonl"]).read_text(encoding="utf-8")
    assert receipt["mock_app_server"] is True
    assert receipt["accepted_state_claim"] is False
    assert receipt["materialization_claim"] is False
    assert lock["state"] == "completed"
    assert heartbeat["state"] == "completed"
    assert final_status["state"] == "completed"
    assert "turn_start" in stdout_jsonl
    assert result["status"]["classification"] == "terminal"

    status = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_status",
        args={"thread_id": THREAD_ID, "carrier_id": "mock-carrier"},
    )
    assert status["ok"] is True
    assert status["classification"] == "terminal"
    assert status["run_receipt"]["turn_id"] == "mock-turn-start"


def test_codex_app_server_persistent_carrier_real_process_helper_uses_injected_fake_process(tmp_path: Path):
    result = _stage1_real_runner_helper(
        tmp_path,
        carrier_id="real-process-complete",
        stdout_messages=[
            *_stage1_base_messages("real-turn-complete", turn_status="completed")[:3],
            {"method": "item/completed", "params": {"turnId": "real-turn-complete"}},
            _stage1_base_messages("real-turn-complete", turn_status="completed")[3],
        ],
        wait_for_completion=True,
    )

    assert result["ok"] is True
    assert result["real_process_runner_implemented"] is True
    assert result["allow_real_app_server"] is True
    assert result["fake_app_server_runner"] is False
    assert result["mock_app_server"] is False
    assert result["real_app_server_process_started"] is True
    assert result["turn_submitted_to_real_codex"] is True
    assert result["accepted_by_app_server"] is True
    assert result["durably_visible"] is True
    assert result["completed"] is True
    assert result["state"] == "completed"
    assert [phase["phase"] for phase in result["lifecycle_phases"]] == ["starting", "submitted", "visible", "completed"]
    receipt = json.loads((tmp_path / result["receipt_path"]).read_text(encoding="utf-8"))
    final_status = json.loads((tmp_path / result["final_status_path"]).read_text(encoding="utf-8"))
    stdout_jsonl = (tmp_path / result["stdout_jsonl_path"]).read_text(encoding="utf-8")
    stderr_log = (tmp_path / result["stderr_log_path"]).read_text(encoding="utf-8")
    assert receipt["schema_id"] == "ion.codex_app_server_persistent_carrier_real_process_runner_receipt.v0_1_candidate"
    assert receipt["real_app_server_process_started"] is True
    assert receipt["turn_submitted_to_real_codex"] is True
    assert receipt["accepted_state_claim"] is False
    assert receipt["materialization_claim"] is False
    assert final_status["state"] == "completed"
    assert "jsonrpc_response" in stdout_jsonl
    assert stderr_log == ""
    assert result["status"]["classification"] == "terminal"


def test_codex_app_server_persistent_carrier_real_process_helper_classifies_nonterminal_states(tmp_path: Path):
    visible = _stage1_real_runner_helper(
        tmp_path,
        carrier_id="real-process-visible",
        stdout_messages=_stage1_base_messages("real-turn-visible", turn_status="inProgress"),
    )
    interrupted = _stage1_real_runner_helper(
        tmp_path,
        carrier_id="real-process-interrupted",
        stdout_messages=_stage1_base_messages("real-turn-interrupted", turn_status="interrupted"),
    )
    usage = _stage1_real_runner_helper(
        tmp_path,
        carrier_id="real-process-usage",
        stdout_messages=[
            {"id": "initialize", "result": {"userAgent": "ion-test/fake-process"}},
            {"id": "resume", "result": {"thread": {"id": THREAD_ID}}},
            {"id": "turn_start", "error": {"code": "usageLimitExceeded", "message": "usage limit"}},
            {"id": "turns", "result": {"data": []}},
        ],
    )

    assert visible["ok"] is False
    assert visible["finding"] == "persistent_carrier_visible_not_completed"
    assert visible["state"] == "visible_not_completed"
    assert visible["durably_visible"] is True
    assert visible["completed"] is False
    assert interrupted["ok"] is False
    assert interrupted["finding"] == "persistent_carrier_terminal_non_completed"
    assert interrupted["state"] == "interrupted"
    assert usage["ok"] is False
    assert usage["finding"] == "persistent_carrier_usage_limit"
    assert usage["state"] == "usage_limited"
    assert usage["usage_limited"] is True
    assert usage["real_app_server_process_started"] is True
    assert usage["status"]["classification"] == "terminal"

    timeout = _stage1_real_runner_helper(
        tmp_path,
        carrier_id="real-process-timeout",
        stdout_messages=[
            {"id": "initialize", "result": {"userAgent": "ion-test/fake-process"}},
            {"id": "resume", "result": {"thread": {"id": THREAD_ID}}},
            {"id": "turn_start", "result": {"turn": {"id": "real-turn-timeout", "status": "inProgress"}}},
        ],
        timeout_seconds=1,
    )
    start_failed = _stage1_real_runner_helper(
        tmp_path,
        carrier_id="real-process-start-failed",
        process_factory=lambda *_args, **_kwargs: (_ for _ in ()).throw(FileNotFoundError("fake process missing")),
    )

    assert timeout["ok"] is False
    assert timeout["finding"] == "persistent_carrier_timeout"
    assert timeout["state"] == "timeout"
    assert timeout["timed_out"] is True
    assert timeout["status"]["classification"] == "terminal"
    assert start_failed["ok"] is False
    assert start_failed["finding"] == "persistent_carrier_process_start_failed"
    assert start_failed["state"] == "process_start_failed"
    assert start_failed["real_app_server_process_started"] is False


def test_codex_app_server_persistent_carrier_fake_real_runner_records_completed_lifecycle(tmp_path: Path):
    _seed_root(tmp_path)
    result = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_start",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": "fake-real-complete",
            "prompt": "fake real runner complete",
            "allow_real_app_server": True,
            "fake_app_server_runner": True,
            "fake_turn_id": "fake-turn-complete",
            "idempotency_key": "fake-real-complete",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )

    assert result["ok"] is True
    assert result["allow_real_app_server"] is True
    assert result["fake_app_server_runner"] is True
    assert result["mock_app_server"] is False
    assert result["real_app_server_process_started"] is False
    assert result["turn_submitted_to_real_codex"] is False
    assert result["accepted_by_app_server"] is True
    assert result["durably_visible"] is True
    assert result["completed"] is True
    assert [phase["phase"] for phase in result["lifecycle_phases"]] == ["starting", "submitted", "visible", "completed"]
    assert result["authority"]["accepted_state_claim"] is False
    assert result["authority"]["materialization_claim"] is False
    assert result["authority"]["production_authority"] is False
    assert result["authority"]["secrets_authority"] is False
    assert result["authority"]["git_push_authority"] is False
    assert result["authority"]["deletion_authority"] is False
    receipt = json.loads((tmp_path / result["receipt_path"]).read_text(encoding="utf-8"))
    final_status = json.loads((tmp_path / result["final_status_path"]).read_text(encoding="utf-8"))
    assert receipt["fake_app_server_runner"] is True
    assert receipt["real_app_server_process_started"] is False
    assert receipt["turn_submitted_to_real_codex"] is False
    assert receipt["accepted_state_claim"] is False
    assert receipt["materialization_claim"] is False
    assert final_status["state"] == "completed"
    assert final_status["durably_visible"] is True
    assert result["status"]["classification"] == "terminal"


def test_codex_app_server_persistent_carrier_fake_real_runner_exact_turn_not_visible(tmp_path: Path):
    _seed_root(tmp_path)
    result = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_start",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": "fake-real-not-visible",
            "prompt": "fake real runner not visible",
            "allow_real_app_server": True,
            "fake_app_server_runner": True,
            "fake_turn_id": "fake-turn-not-visible",
            "fake_turn_visible": False,
            "idempotency_key": "fake-real-not-visible",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )

    assert result["ok"] is False
    assert result["finding"] == "persistent_carrier_exact_turn_not_visible"
    assert result["durably_visible"] is False
    assert result["completed"] is False
    assert result["real_app_server_process_started"] is False
    assert [phase["phase"] for phase in result["lifecycle_phases"]] == ["starting", "submitted", "completed"]
    receipt = json.loads((tmp_path / result["receipt_path"]).read_text(encoding="utf-8"))
    assert receipt["durably_visible"] is False
    assert receipt["completed"] is False
    assert receipt["accepted_state_claim"] is False


def test_codex_app_server_persistent_carrier_fake_real_runner_usage_limit_classification(tmp_path: Path):
    _seed_root(tmp_path)
    result = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_start",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": "fake-real-usage",
            "prompt": "fake real runner usage",
            "allow_real_app_server": True,
            "fake_app_server_runner": True,
            "fake_turn_id": "fake-turn-usage",
            "fake_stdout_contains": "usageLimitExceeded",
            "idempotency_key": "fake-real-usage",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )

    assert result["ok"] is False
    assert result["finding"] == "persistent_carrier_usage_limit"
    assert result["state"] == "usage_limited"
    assert result["usage_limited"] is True
    assert result["timed_out"] is False
    assert result["durably_visible"] is False
    assert result["accepted_by_app_server"] is False


def test_codex_app_server_persistent_carrier_fake_real_runner_timeout_classification(tmp_path: Path):
    _seed_root(tmp_path)
    result = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_start",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": "fake-real-timeout",
            "prompt": "fake real runner timeout",
            "allow_real_app_server": True,
            "fake_app_server_runner": True,
            "fake_turn_id": "fake-turn-timeout",
            "fake_timeout": True,
            "idempotency_key": "fake-real-timeout",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )

    assert result["ok"] is False
    assert result["finding"] == "persistent_carrier_timeout"
    assert result["state"] == "timeout"
    assert result["timed_out"] is True
    assert result["usage_limited"] is False
    assert result["durably_visible"] is False
    assert result["status"]["classification"] == "terminal"


def test_codex_app_server_persistent_carrier_fake_real_duplicate_live_lock_blocks(tmp_path: Path):
    _seed_root(tmp_path)
    first = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_start",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": "fake-real-live",
            "prompt": "fake real leave running",
            "allow_real_app_server": True,
            "fake_app_server_runner": True,
            "fake_leave_running": True,
            "idempotency_key": "fake-real-live-first",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )
    duplicate = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_start",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": "fake-real-live",
            "prompt": "fake real duplicate",
            "allow_real_app_server": True,
            "fake_app_server_runner": True,
            "idempotency_key": "fake-real-live-second",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )

    assert first["ok"] is True
    assert first["state"] == "running"
    assert first["status"]["classification"] == "live"
    assert duplicate["ok"] is False
    assert duplicate["finding"] == "persistent_carrier_live_lock_exists"
    assert duplicate["refusal_class"] == "LOCK_HELD"


def test_codex_app_server_persistent_carrier_action_branch_invoke_parity():
    start_status = action_branch_invoke(
        Path.cwd(),
        branch_id="codex_app_server",
        route_id="persistent_carrier_status",
        args={"thread_id": THREAD_ID, "carrier_id": "mock-parity"},
        expected_route_schema_version="v0",
    )

    assert start_status["ok"] is True
    assert start_status["mutates_active_state"] is False
    assert start_status["delegated_result"]["route_id"] == "persistent_carrier_status"
    assert start_status["delegated_result"]["classification"] in {"missing", "terminal", "live", "stale_heartbeat", "stale_no_heartbeat"}


def test_codex_app_server_persistent_carrier_start_status_stop_action_branch_invoke_parity(tmp_path: Path):
    _seed_root_with_registry(tmp_path)

    start = action_branch_invoke(
        tmp_path,
        branch_id="codex_app_server",
        route_id="persistent_carrier_start",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": "branch-parity-carrier",
            "prompt": "mock branch parity",
            "mock_app_server": True,
            "mock_leave_running": True,
            "idempotency_key": "branch-parity-start",
            "confirmation": CONFIRMATION_TOKEN,
        },
        expected_route_schema_version="v0",
    )
    status = action_branch_invoke(
        tmp_path,
        branch_id="codex_app_server",
        route_id="persistent_carrier_status",
        args={"thread_id": THREAD_ID, "carrier_id": "branch-parity-carrier"},
        expected_route_schema_version="v0",
    )
    stop = action_branch_invoke(
        tmp_path,
        branch_id="codex_app_server",
        route_id="persistent_carrier_stop",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": "branch-parity-carrier",
            "reason": "branch parity stop",
            "idempotency_key": "branch-parity-stop",
            "confirmation": CONFIRMATION_TOKEN,
        },
        expected_route_schema_version="v0",
    )

    assert start["ok"] is True
    assert start["mutates_active_state"] is True
    assert start["delegated_result"]["route_id"] == "persistent_carrier_start"
    assert start["delegated_result"]["mock_app_server"] is True
    assert status["ok"] is True
    assert status["mutates_active_state"] is False
    assert status["delegated_result"]["classification"] == "live"
    assert stop["ok"] is True
    assert stop["mutates_active_state"] is True
    assert stop["delegated_result"]["route_id"] == "persistent_carrier_stop"
    assert stop["delegated_result"]["status"]["classification"] == "terminal"


def test_codex_app_server_persistent_carrier_duplicate_live_lock_blocks(tmp_path: Path):
    _seed_root(tmp_path)
    first = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_start",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": "live-carrier",
            "prompt": "leave running",
            "mock_app_server": True,
            "mock_leave_running": True,
            "idempotency_key": "live-first",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )
    duplicate = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_start",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": "live-carrier",
            "prompt": "different duplicate",
            "mock_app_server": True,
            "idempotency_key": "live-second",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )

    assert first["ok"] is True
    assert first["state"] == "running"
    assert first["status"]["classification"] == "live"
    assert duplicate["ok"] is False
    assert duplicate["finding"] == "persistent_carrier_live_lock_exists"
    assert duplicate["refusal_class"] == "LOCK_HELD"


def test_codex_app_server_persistent_carrier_status_classifies_stale_heartbeat(tmp_path: Path):
    _seed_root(tmp_path)
    carrier_key = bridge._persistent_carrier_key(THREAD_ID, {"carrier_id": "stale-carrier"})
    paths = bridge._persistent_carrier_paths(tmp_path, THREAD_ID, carrier_key)
    bridge._write_json(
        paths["lock"],
        {
            "schema_id": "ion.codex_app_server_persistent_carrier_lock.v0_1_candidate",
            "thread_id": THREAD_ID,
            "carrier_id": carrier_key,
            "stale_after_seconds": 30,
        },
    )
    bridge._write_json(
        paths["heartbeat"],
        {
            "schema_id": "ion.codex_app_server_persistent_carrier_heartbeat.v0_1_candidate",
            "updated_at": "2000-01-01T00:00:00+00:00",
            "thread_id": THREAD_ID,
            "carrier_id": carrier_key,
            "state": "running",
            "stale_after_seconds": 30,
        },
    )

    status = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_status",
        args={"thread_id": THREAD_ID, "carrier_id": "stale-carrier", "stale_after_seconds": 30},
    )

    assert status["ok"] is True
    assert status["classification"] == "stale_heartbeat"


def test_codex_app_server_persistent_carrier_stop_writes_stop_and_final_receipts(tmp_path: Path):
    _seed_root(tmp_path)
    started = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_start",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": "stop-carrier",
            "prompt": "leave running for stop",
            "mock_app_server": True,
            "mock_leave_running": True,
            "mock_turn_id": "mock-turn-stop",
            "idempotency_key": "stop-start",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )
    stopped = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_stop",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": "stop-carrier",
            "reason": "test stop",
            "idempotency_key": "stop-request",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )

    assert started["status"]["classification"] == "live"
    assert stopped["ok"] is True
    assert stopped["mutates_active_state"] is True
    assert stopped["stopped"] is True
    stop_receipt = json.loads((tmp_path / stopped["stop_receipt_path"]).read_text(encoding="utf-8"))
    final_status = json.loads((tmp_path / stopped["final_status_path"]).read_text(encoding="utf-8"))
    assert stop_receipt["accepted_state_claim"] is False
    assert stop_receipt["materialization_claim"] is False
    assert final_status["state"] == "stopped"
    assert stopped["status"]["classification"] == "terminal"


def test_codex_app_server_persistent_carrier_accepts_original_and_canonical_carrier_id(tmp_path: Path):
    _seed_root(tmp_path)
    base_carrier_id = "canonicalization-carrier"
    started = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_start",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": base_carrier_id,
            "prompt": "leave running for canonical id test",
            "mock_app_server": True,
            "mock_leave_running": True,
            "mock_turn_id": "mock-turn-canonical",
            "idempotency_key": "canonical-start",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )
    canonical_carrier_id = started["canonical_carrier_id"]

    status_original = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_status",
        args={"thread_id": THREAD_ID, "carrier_id": base_carrier_id},
    )
    status_canonical = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_status",
        args={"thread_id": THREAD_ID, "carrier_id": canonical_carrier_id},
    )
    stopped_canonical = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_stop",
        args={
            "thread_id": THREAD_ID,
            "carrier_id": canonical_carrier_id,
            "reason": "canonical stop",
            "idempotency_key": "canonical-stop",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )
    final_original = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_status",
        args={"thread_id": THREAD_ID, "carrier_id": base_carrier_id},
    )
    final_canonical = invoke_codex_app_server_route(
        tmp_path,
        route_id="persistent_carrier_status",
        args={"thread_id": THREAD_ID, "carrier_id": canonical_carrier_id},
    )

    assert started["input_carrier_id"] == base_carrier_id
    assert canonical_carrier_id == started["carrier_id"]
    assert canonical_carrier_id != base_carrier_id
    assert status_original["canonical_carrier_id"] == canonical_carrier_id
    assert status_original["classification"] == "live"
    assert status_canonical["canonical_carrier_id"] == canonical_carrier_id
    assert status_canonical["carrier_id_resolution"]["method"] == "existing_folder_exact"
    assert status_canonical["classification"] == "live"
    assert status_canonical["paths"]["carrier_root"] == status_original["paths"]["carrier_root"]
    assert stopped_canonical["ok"] is True
    assert stopped_canonical["canonical_carrier_id"] == canonical_carrier_id
    assert stopped_canonical["status"]["classification"] == "terminal"
    assert final_original["classification"] == "terminal"
    assert final_canonical["classification"] == "terminal"
    assert final_canonical["canonical_carrier_id"] == canonical_carrier_id
    assert final_canonical["accepted_state_claim"] is False
    assert final_canonical["materialization_claim"] is False


def test_codex_app_server_rejects_unsafe_thread_id(tmp_path: Path):
    _seed_root(tmp_path)

    result = invoke_codex_app_server_route(tmp_path, route_id="thread_resume", args={"thread_id": "../bad"})

    assert result["ok"] is False
    assert result["refusal_class"] == "SCHEMA_INVALID"
    assert result["finding"] == "unsafe_thread_id"


def test_codex_app_server_thread_resume_returns_bounded_metadata(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    monkeypatch.setattr(bridge, "_run_app_server_jsonrpc", _fake_rpc_for_read)

    result = invoke_codex_app_server_route(
        tmp_path,
        route_id="thread_resume",
        args={"thread_id": THREAD_ID, "turn_limit": 1, "sandbox_mode": "workspace-write"},
    )

    assert result["ok"] is True
    assert result["thread"]["thread_id"] == THREAD_ID
    assert result["model"] == "gpt-5.5"
    assert result["sandbox"]["type"] == "workspaceWrite"
    assert result["initial_turns_count"] == 1
    assert result["accepted_state_claim"] is False


def test_codex_app_server_thread_turn_read_by_id_exact_match_and_not_found(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)

    monkeypatch.setattr(
        bridge,
        "_thread_turns_list",
        lambda args: {
            "ok": True,
            "thread_id": args["thread_id"],
            "turn_count": 2,
            "turns": [
                {"id": "older-turn", "status": "completed", "items": []},
                {"id": "target-turn", "status": "inProgress", "items": [{"type": "message"}]},
            ],
        },
    )

    matched = invoke_codex_app_server_route(
        tmp_path,
        route_id="thread_turn_read_by_id",
        args={"thread_id": THREAD_ID, "turn_id": "target-turn"},
    )
    missing = invoke_codex_app_server_route(
        tmp_path,
        route_id="thread_turn_read_by_id",
        args={"thread_id": THREAD_ID, "turn_id": "missing-turn"},
    )

    assert matched["ok"] is True
    assert matched["matched"] is True
    assert matched["matched_turn"]["id"] == "target-turn"
    assert matched["matched_turn_status"] == "inProgress"
    assert missing["ok"] is False
    assert missing["finding"] == "turn_not_found"
    assert missing["refusal_class"] == "NOT_FOUND"
    assert "older-turn" in missing["scanned_turn_ids"]


def test_codex_app_server_turn_start_preview_is_read_only(tmp_path: Path):
    _seed_root(tmp_path)

    result = invoke_codex_app_server_route(
        tmp_path,
        route_id="turn_start_preview",
        args={"thread_id": THREAD_ID, "prompt": "continue", "sandbox_mode": "workspace-write"},
    )

    assert result["ok"] is True
    assert result["mutates_active_state"] is False
    assert result["turn_start_not_executed"] is True
    assert result["jsonrpc_sequence"][1]["method"] == "turn/start"
    assert result["jsonrpc_sequence"][1]["params"]["sandboxPolicy"]["type"] == "workspaceWrite"


def test_codex_app_server_turn_start_requires_confirmation_and_idempotency(tmp_path: Path):
    _seed_root(tmp_path)

    no_idempotency = invoke_codex_app_server_route(
        tmp_path,
        route_id="turn_start",
        args={"thread_id": THREAD_ID, "prompt": "continue", "confirmation": CONFIRMATION_TOKEN},
    )
    no_confirmation = invoke_codex_app_server_route(
        tmp_path,
        route_id="turn_start",
        args={"thread_id": THREAD_ID, "prompt": "continue", "idempotency_key": "missing-confirmation"},
    )

    assert no_idempotency["ok"] is False
    assert no_idempotency["refusal_class"] == "IDEMPOTENCY_KEY_REQUIRED"
    assert no_confirmation["ok"] is False
    assert no_confirmation["refusal_class"] == "CONFIRMATION_REQUIRED"


def test_codex_app_server_workspace_write_normalizes_relative_writable_roots(tmp_path: Path):
    _seed_root(tmp_path)
    relative_root = "ION/05_context/current/domain_weaver/swarm_expansion/wave0_batch_a/returns"

    policy, notes = bridge._sandbox_policy_details(
        {"sandbox": "workspace-write", "writable_roots": [relative_root]},
        root=tmp_path,
    )

    expected = (tmp_path / relative_root).resolve(strict=False).as_posix()
    assert policy == {"type": "workspaceWrite", "writableRoots": [expected], "networkAccess": False}
    assert notes == [{"input": relative_root, "resolved": expected, "base": tmp_path.resolve().as_posix()}]


def test_codex_app_server_workspace_write_rejects_unsafe_writable_roots(tmp_path: Path):
    _seed_root(tmp_path)

    outside = invoke_codex_app_server_route(
        tmp_path,
        route_id="turn_start",
        args={
            "thread_id": THREAD_ID,
            "prompt": "continue",
            "sandbox": "workspace-write",
            "writable_roots": ["../outside"],
            "idempotency_key": "unsafe-root-outside",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )
    codex_private = invoke_codex_app_server_route(
        tmp_path,
        route_id="turn_start",
        args={
            "thread_id": THREAD_ID,
            "prompt": "continue",
            "sandbox": "workspace-write",
            "writable_roots": [".codex/sessions"],
            "idempotency_key": "unsafe-root-codex",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )

    assert outside["ok"] is False
    assert outside["finding"] == "writable_root_outside_active_root"
    assert codex_private["ok"] is False
    assert codex_private["finding"] == "forbidden_writable_root"


def test_codex_app_server_turn_start_writes_receipt_and_redacts_prompt(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    secret = "sk-testsecret1234567890"
    observed_call = {}

    def fake_rpc(requests, *, timeout_seconds=12, wait_for_methods=None):
        observed_call["timeout_seconds"] = timeout_seconds
        observed_call["wait_for_methods"] = wait_for_methods
        response_by_id = {
            "initialize": {"id": "initialize", "result": {"userAgent": "ion-test"}},
            "resume": {"id": "resume", "result": {"thread": {"id": THREAD_ID, "sessionId": THREAD_ID}}},
            "turn_start": {"id": "turn_start", "result": {"turn": {"id": "turn-2", "status": "running"}}},
        }
        return {
            "ok": True,
            "command_argv": ["codex", "app-server", "--listen", "stdio://"],
            "responses": list(response_by_id.values()),
            "response_by_id": response_by_id,
            "notifications": [{"method": "turn/completed", "params": {"threadId": THREAD_ID, "turnId": "turn-2"}}],
            "pending_request_ids": [],
            "stderr_lines": [],
            "timed_out": False,
        }

    monkeypatch.setattr(bridge, "_run_app_server_jsonrpc", fake_rpc)

    result = invoke_codex_app_server_route(
        tmp_path,
        route_id="turn_start",
        args={
            "thread_id": THREAD_ID,
            "prompt": f"continue TOKEN={secret}",
            "sandbox_mode": "workspace-write",
            "idempotency_key": "turn-start-test",
            "confirmation": CONFIRMATION_TOKEN,
            "timeout_seconds": 180,
        },
    )

    assert result["ok"] is True
    assert result["mutates_active_state"] is True
    assert result["submitted"] is True
    assert result["accepted_by_app_server"] is True
    assert result["durably_visible"] is False
    assert result["turn_id"] == "turn-2"
    assert result["completion_wait_requested"] is False
    assert result["completion_poll_recommended"] is True
    assert observed_call["wait_for_methods"] is None
    assert observed_call["timeout_seconds"] == 60
    receipt_path = tmp_path / result["receipt_path"]
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt_text = json.dumps(receipt, sort_keys=True)
    assert receipt["submit_state"] == "submitted"
    assert receipt["submitted"] is True
    assert receipt["accepted_by_app_server"] is True
    assert receipt["durably_visible"] is False
    assert receipt["turn_id"] == "turn-2"
    assert receipt["turn_completed_notification_seen"] is True
    assert secret not in receipt_text
    assert "***REDACTED***" in receipt_text

    replay = invoke_codex_app_server_route(
        tmp_path,
        route_id="turn_start",
        args={
            "thread_id": THREAD_ID,
            "prompt": "continue",
            "idempotency_key": "turn-start-test",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )
    assert replay["ok"] is True
    assert replay["idempotent_replay"] is True


def test_codex_app_server_turn_start_sends_absolute_writable_roots(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    relative_root = "ION/05_context/current/domain_weaver/swarm_expansion/wave0_batch_a/returns"
    observed = {}

    def fake_rpc(requests, *, timeout_seconds=12, wait_for_methods=None):
        for request in requests:
            if request.get("id") == "turn_start":
                observed["turn_params"] = request["params"]
        response_by_id = {
            "initialize": {"id": "initialize", "result": {"userAgent": "ion-test"}},
            "resume": {"id": "resume", "result": {"thread": {"id": THREAD_ID, "sessionId": THREAD_ID}}},
            "turn_start": {"id": "turn_start", "result": {"turn": {"id": "turn-with-root", "status": "inProgress"}}},
        }
        return {
            "ok": True,
            "command_argv": ["codex", "app-server", "--listen", "stdio://"],
            "responses": list(response_by_id.values()),
            "response_by_id": response_by_id,
            "notifications": [],
            "pending_request_ids": [],
            "stderr_lines": [],
            "timed_out": False,
        }

    monkeypatch.setattr(bridge, "_run_app_server_jsonrpc", fake_rpc)

    result = invoke_codex_app_server_route(
        tmp_path,
        route_id="turn_start",
        args={
            "thread_id": THREAD_ID,
            "prompt": "continue",
            "sandbox": "workspace-write",
            "writable_roots": [relative_root],
            "idempotency_key": "absolute-writable-root",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )

    expected = (tmp_path / relative_root).resolve(strict=False).as_posix()
    assert result["ok"] is True
    assert observed["turn_params"]["sandboxPolicy"]["writableRoots"] == [expected]
    assert Path(observed["turn_params"]["sandboxPolicy"]["writableRoots"][0]).is_absolute()
    assert result["writable_root_resolution"][0]["resolved"] == expected


def test_codex_app_server_turn_start_wait_until_visible_does_not_report_disappeared_turn_as_durable(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)

    def fake_rpc(requests, *, timeout_seconds=12, wait_for_methods=None):
        response_by_id = {
            "initialize": {"id": "initialize", "result": {"userAgent": "ion-test"}},
            "resume": {"id": "resume", "result": {"thread": {"id": THREAD_ID, "sessionId": THREAD_ID}}},
            "turn_start": {"id": "turn_start", "result": {"turn": {"id": "transient-turn", "status": "inProgress", "items": []}}},
        }
        return {
            "ok": True,
            "command_argv": ["codex", "app-server", "--listen", "stdio://"],
            "responses": list(response_by_id.values()),
            "response_by_id": response_by_id,
            "notifications": [
                {"method": "thread/status/changed", "params": {"threadId": THREAD_ID, "status": {"type": "busy"}}},
                {"method": "thread/goal/updated", "params": {"threadId": THREAD_ID}},
            ],
            "pending_request_ids": [],
            "stderr_lines": [],
            "timed_out": False,
        }

    monkeypatch.setattr(bridge, "_run_app_server_jsonrpc", fake_rpc)
    monkeypatch.setattr(
        bridge,
        "_thread_turn_read_by_id",
        lambda args: {
            "ok": False,
            "thread_id": args["thread_id"],
            "turn_id": args["turn_id"],
            "matched": False,
            "finding": "turn_not_found",
            "refusal_class": "NOT_FOUND",
            "scanned_turn_ids": ["older-turn"],
        },
    )

    result = invoke_codex_app_server_route(
        tmp_path,
        route_id="turn_start",
        args={
            "thread_id": THREAD_ID,
            "prompt": "continue",
            "idempotency_key": "transient-turn-test",
            "confirmation": CONFIRMATION_TOKEN,
            "wait_until_visible": True,
        },
    )

    assert result["ok"] is False
    assert result["finding"] == "codex_app_server_turn_start_not_durably_visible"
    assert result["accepted_by_app_server"] is True
    assert result["submitted"] is True
    assert result["durably_visible"] is False
    assert result["completed"] is False
    assert result["durable_submit_state"] == "accepted_but_not_durably_visible"
    assert result["post_submit_visibility_probe"]["finding"] == "turn_not_found"
    receipt = json.loads((tmp_path / result["receipt_path"]).read_text(encoding="utf-8"))
    assert receipt["accepted_by_app_server"] is True
    assert receipt["durably_visible"] is False
    assert receipt["completed"] is False


def test_codex_app_server_turn_status_probes_recent_thread_turns(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)

    def fake_rpc(requests, *, timeout_seconds=12, wait_for_methods=None):
        response_by_id = {
            "initialize": {"id": "initialize", "result": {"userAgent": "ion-test"}},
            "resume": {"id": "resume", "result": {"thread": {"id": THREAD_ID, "sessionId": THREAD_ID}}},
            "turn_start": {"id": "turn_start", "result": {"turn": {"id": "turn-2", "status": "inProgress"}}},
        }
        return {
            "ok": True,
            "command_argv": ["codex", "app-server", "--listen", "stdio://"],
            "responses": list(response_by_id.values()),
            "response_by_id": response_by_id,
            "notifications": [],
            "pending_request_ids": [],
            "stderr_lines": [],
            "timed_out": False,
        }

    monkeypatch.setattr(bridge, "_run_app_server_jsonrpc", fake_rpc)
    started = invoke_codex_app_server_route(
        tmp_path,
        route_id="turn_start",
        args={
            "thread_id": THREAD_ID,
            "prompt": "continue",
            "idempotency_key": "turn-status-probe",
            "confirmation": CONFIRMATION_TOKEN,
        },
    )
    assert started["ok"] is True

    monkeypatch.setattr(
        bridge,
        "_thread_turns_list",
        lambda args: {
            "ok": True,
            "thread_id": args["thread_id"],
            "turn_count": 1,
            "turns": [{"id": "turn-2", "status": "completed", "items": []}],
        },
    )
    status = invoke_codex_app_server_route(tmp_path, route_id="turn_status", args={"thread_id": THREAD_ID})

    assert status["ok"] is True
    assert status["run_count"] == 1
    assert status["latest_run"]["submit_state"] == "submitted"
    assert status["latest_run"]["turn_id"] == "turn-2"
    assert status["thread_turns_probe"]["ok"] is True
    assert status["target_turn_id"] == "turn-2"
    assert status["target_turn_match_state"] == "matched"
    assert status["target_matched_turn"]["id"] == "turn-2"
    assert status["matched_turns"][0]["status"] == "completed"


def test_codex_app_server_turn_status_extracts_legacy_receipt_turn_id(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    paths = bridge._run_paths(tmp_path, THREAD_ID, "legacy-turn-receipt")
    paths["receipt"].parent.mkdir(parents=True, exist_ok=True)
    paths["receipt"].write_text(
        json.dumps(
            {
                "created_at": "2026-06-04T20:06:04+00:00",
                "turn_start_result": {"turn": {"id": "legacy-turn", "status": "inProgress"}},
                "turn_start_error": None,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        bridge,
        "_thread_turns_list",
        lambda args: {
            "ok": True,
            "thread_id": args["thread_id"],
            "turn_count": 1,
            "turns": [{"id": "legacy-turn", "status": "completed", "items": []}],
        },
    )

    status = invoke_codex_app_server_route(tmp_path, route_id="turn_status", args={"thread_id": THREAD_ID})

    assert status["latest_run"]["submit_state"] == "submitted"
    assert status["latest_run"]["submitted"] is True
    assert status["latest_run"]["turn_id"] == "legacy-turn"
    assert status["target_turn_id"] == "legacy-turn"
    assert status["target_turn_match_state"] == "matched"
    assert status["matched_turns"][0]["status"] == "completed"


def test_codex_app_server_turn_status_does_not_false_positive_older_turn_for_latest(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    _write_turn_receipt(tmp_path, "old-worker", "older-turn", timestamp=100)
    latest_paths = _write_turn_receipt(tmp_path, "new-worker", "latest-turn", timestamp=200)
    monkeypatch.setattr(
        bridge,
        "_thread_turns_list",
        lambda args: {
            "ok": True,
            "thread_id": args["thread_id"],
            "turn_count": 1,
            "turns": [{"id": "older-turn", "status": "completed", "items": []}],
        },
    )

    status = invoke_codex_app_server_route(tmp_path, route_id="turn_status", args={"thread_id": THREAD_ID})

    assert status["latest_run"]["receipt_path"] == latest_paths["receipt"].relative_to(tmp_path).as_posix()
    assert status["latest_run"]["turn_id"] == "latest-turn"
    assert status["target_turn_id"] == "latest-turn"
    assert status["target_turn_match_state"] == "not_found"
    assert status["target_matched_turn"] is None
    assert [turn["id"] for turn in status["matched_turns"]] == ["older-turn"]


def test_codex_app_server_turn_poll_latest_uses_latest_receipt_exact_turn(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    _write_turn_receipt(tmp_path, "old-poll", "older-turn", timestamp=100)
    latest_paths = _write_turn_receipt(tmp_path, "new-poll", "latest-turn", timestamp=200)
    observed = {}

    def fake_read_by_id(args):
        observed["turn_id"] = args["turn_id"]
        return {
            "ok": True,
            "thread_id": args["thread_id"],
            "turn_id": args["turn_id"],
            "matched": True,
            "matched_turn_status": "completed",
            "matched_turn": {"id": args["turn_id"], "status": "completed", "items": []},
        }

    monkeypatch.setattr(bridge, "_thread_turn_read_by_id", fake_read_by_id)

    result = invoke_codex_app_server_route(
        tmp_path,
        route_id="turn_poll",
        args={"thread_id": THREAD_ID, "latest": True, "timeout_seconds": 1, "poll_interval": 0.25},
    )

    assert result["ok"] is True
    assert result["poll_state"] == "completed"
    assert result["turn_id"] == "latest-turn"
    assert observed["turn_id"] == "latest-turn"
    assert result["receipt_path"] == latest_paths["receipt"].relative_to(tmp_path).as_posix()
