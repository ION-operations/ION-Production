import base64
import hashlib
import json
from pathlib import Path

from kernel.ion_chatgpt_browser_mcp_connector_contract import (
    BOUNDED_QUEUE_RECEIPT_TOOLS,
    FORBIDDEN_CAPABILITIES,
    STATUS_READ_TOOLS,
    audit_chatgpt_browser_mcp_connector_contract,
    call_chatgpt_connector_tool,
    write_chatgpt_browser_mcp_connector_contract,
)
from kernel.ion_codex_queue_runner import build_codex_queue_runner_status, process_codex_queue_once
from kernel.ion_chatgpt_browser_mcp_http_preview import documented_launch_requests_serve, handle_mcp_jsonrpc
from kernel.ion_worker_shift_presence import request_edit_lease, sign_on


def _seed_root(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").parent.mkdir(parents=True)
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")
    (root / "ION_WORKSPACE_MANIFEST.yaml").write_text(
        "\n".join(
            [
                "schema_id: ion.workspace_manifest.v1",
                f'workspace_root: "{root.parent.as_posix()}"',
                f'active_repo_root: "{root.as_posix()}"',
                f'ion_content_root: "{(root / "ION").as_posix()}"',
                f'export_root: "{(root.parent / "ION_EXPORTS_LOCAL").as_posix()}"',
                f'vault_root: "{(root.parent / "ION_VAULT_LOCAL").as_posix()}"',
                "allowed_sibling_roots:",
                f'  - "{(root.parent / "ION_EXPORTS_LOCAL").as_posix()}"',
                f'  - "{(root.parent / "ION_VAULT_LOCAL").as_posix()}"',
                "forbidden_roots:",
                f'  - "{(root.parent / ".ssh").as_posix()}"',
                "path_policy:",
                "  forbid_parent_segments_for_write: true",
                "  canonicalize_all_leases: true",
                "  require_workspace_containment_for_artifacts: true",
                "  require_artifacts_outside_active_repo: false",
                "  require_human_override_for_external_paths: true",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _seed_edit_lease(
    root: Path,
    *,
    agent_id: str,
    lease_id: str,
    target_paths: list[str],
    lease_mode: str | None = None,
) -> dict[str, str]:
    sign_on(
        agent_id,
        "chatgpt_browser_connector_test",
        "connector mutation lease test",
        target_paths,
        root=root,
        display_callsign=agent_id,
    )
    request = {
        "agent_id": agent_id,
        "lease_id": lease_id,
        "target_paths": target_paths,
        "objective": "connector mutation lease test",
        "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
        "idempotency_key": lease_id,
    }
    if lease_mode:
        request["lease_mode"] = lease_mode
    result = request_edit_lease(
        root,
        request,
    )
    assert result["ok"] is True
    return {"agent_id": agent_id, "lease_id": lease_id}


def _seed_fanout_dryrun_status_artifacts(root: Path) -> None:
    base = root / "ION/05_context/current/kernel_fanout_scheduler/carrier_dryrun"
    (root / "ION/05_context/current/chatgpt_connector/task_returns").mkdir(parents=True, exist_ok=True)
    (
        root / "ION/05_context/current/chatgpt_connector/task_returns/2026-05-14T021628Z0000_task_return.json"
    ).write_text("{\"accepted_for_carrier_intake\": true}\n", encoding="utf-8")
    for scenario in (
        "success",
        "forced_timeout",
        "forced_conflict",
    ):
        scenario_dir = base / scenario
        scenario_dir.mkdir(parents=True, exist_ok=True)
        (scenario_dir / "result.json").write_text(
            json.dumps({"schema_id": "ion.kernel_fanout_true_parallel_smoke_result.v1", "scenario": scenario})
            + "\n",
            encoding="utf-8",
        )
        (scenario_dir / "parent_receipt.json").write_text(
            json.dumps({"schema_id": "ion.kernel_fanout_carrier_dryrun_parent_receipt.v1", "scenario": scenario})
            + "\n",
            encoding="utf-8",
        )
    payload = {
        "schema_id": "ion.kernel_fanout_carrier_dryrun_result.v1",
        "queue_integrity": {"queue_mutation_detected": False},
        "scenarios": [
            {
                "scenario": "success",
                "result_path": "ION/05_context/current/kernel_fanout_scheduler/carrier_dryrun/success/result.json",
                "parent_receipt_path": "ION/05_context/current/kernel_fanout_scheduler/carrier_dryrun/success/parent_receipt.json",
                "compact_summary": {
                    "scenario": "success",
                    "plan_verdict": "ION_KERNEL_FANOUT_PLAN_READY",
                    "settlement_verdict": "SMOKE_READY",
                    "blocked_children": [],
                    "conflict_deferral_events": 0,
                    "conflict_deferred_children": [],
                    "timeout_evidence": [],
                },
            },
            {
                "scenario": "forced_timeout",
                "result_path": "ION/05_context/current/kernel_fanout_scheduler/carrier_dryrun/forced_timeout/result.json",
                "parent_receipt_path": "ION/05_context/current/kernel_fanout_scheduler/carrier_dryrun/forced_timeout/parent_receipt.json",
                "compact_summary": {
                    "scenario": "forced_timeout",
                    "plan_verdict": "ION_KERNEL_FANOUT_PLAN_READY",
                    "settlement_verdict": "SMOKE_BLOCKED",
                    "blocked_children": ["timeout_child_1"],
                    "conflict_deferral_events": 0,
                    "conflict_deferred_children": [],
                    "timeout_evidence": [{"code": "child_timeout", "severity": "blocked"}],
                },
            },
            {
                "scenario": "forced_conflict",
                "result_path": "ION/05_context/current/kernel_fanout_scheduler/carrier_dryrun/forced_conflict/result.json",
                "parent_receipt_path": "ION/05_context/current/kernel_fanout_scheduler/carrier_dryrun/forced_conflict/parent_receipt.json",
                "compact_summary": {
                    "scenario": "forced_conflict",
                    "plan_verdict": "ION_KERNEL_FANOUT_PLAN_READY",
                    "settlement_verdict": "SMOKE_READY",
                    "blocked_children": [],
                    "conflict_deferral_events": 8,
                    "conflict_deferred_children": ["conflict_child_2"],
                    "max_parallel_observed": 1,
                    "timeout_evidence": [],
                },
            },
        ],
    }
    base.mkdir(parents=True, exist_ok=True)
    (base / "fanout_carrier_dryrun_result_20260514.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def test_v120_contract_policy_blocks_unsafe_tools():
    root = Path.cwd()
    result = audit_chatgpt_browser_mcp_connector_contract(root)

    assert result["schema_id"] == "ion.chatgpt_browser_mcp_connector_contract.v1"
    assert result["verdict"] == "ION_CHATGPT_BROWSER_MCP_CONNECTOR_CONTRACT_READY"
    assert "arbitrary_shell" in result["forbidden_tools"]
    assert not (set(result["allowed_tools"]) & set(result["forbidden_tools"]))
    assert set(result["status_read_tools"]) == STATUS_READ_TOOLS
    assert set(result["bounded_queue_receipt_tools"]) == BOUNDED_QUEUE_RECEIPT_TOOLS
    assert result["production_authority"] is False
    assert result["live_execution_authority"] is False


def test_status_and_current_packet_tools_read_without_shell_access():
    root = Path.cwd()

    status = call_chatgpt_connector_tool(root, "ion_status", {})
    packet = call_chatgpt_connector_tool(root, "ion_current_operating_packet", {})
    onboarding = call_chatgpt_connector_tool(root, "ion_carrier_onboarding_packet", {"carrier": "chatgpt_browser"})
    forbidden = call_chatgpt_connector_tool(root, "arbitrary_shell", {})
    browser_capture = call_chatgpt_connector_tool(root, "ion_project_browser_capture", {"project_id": "cosmos", "bookmark": "orbit"})
    timeline = call_chatgpt_connector_tool(root, "ion_project_workbench_timeline", {"project_id": "cosmos", "max_items": 3})

    assert status["ok"] is True
    assert status["data"]["schema_id"] == "ion.status.v1"
    assert packet["ok"] is True
    assert "ION Current Operating Packet" in packet["data"]["content"]["text"]
    assert onboarding["ok"] is True
    assert onboarding["data"]["schema_id"] == "ion.carrier_onboarding_packet.v1"
    assert onboarding["data"]["root_markdown_onboarding_authority"] is False
    assert onboarding["data"]["carrier_profile"]["path"] == "ION/03_registry/chatgpt_browser_carrier_profile.yaml"
    queue = call_chatgpt_connector_tool(root, "ion_codex_work_queue", {"limit": 10})
    manifest = call_chatgpt_connector_tool(root, "ion_tool_manifest", {})
    daemon = call_chatgpt_connector_tool(root, "ion_daemon_status", {})
    live_status = call_chatgpt_connector_tool(root, "ion_codex_worker_live_status", {})
    worker_trace = call_chatgpt_connector_tool(root, "ion_codex_worker_trace", {"max_preview_bytes": 256})
    agent_status = call_chatgpt_connector_tool(root, "ion_agent_status", {})
    assert queue["ok"] is True
    assert queue["data"]["schema_id"] == "ion.chatgpt_browser_connector_codex_work_queue.v1"
    assert manifest["ok"] is True
    assert "ion_file_read" in manifest["data"]["allowed_tools"]
    assert "ion_codex_queue_process_once" in manifest["data"]["allowed_tools"]
    assert "ion_codex_worker_trace" in manifest["data"]["allowed_tools"]
    assert "ion_agent_invoke" in manifest["data"]["allowed_tools"]
    assert daemon["ok"] is True
    assert daemon["data"]["schema_id"] == "ion.codex_queue_runner.v1"
    assert live_status["ok"] is True
    assert live_status["data"]["schema_id"] == "ion.codex_queue_runner.v1"
    assert live_status["data"]["live_worker_telemetry"]["schema_id"] == "ion.codex_worker_live_status.v1"
    assert worker_trace["ok"] is True
    assert worker_trace["mutates_active_state"] is False
    assert worker_trace["data"]["schema_id"] == "ion.codex_worker_observability_trace.v0"
    assert worker_trace["data"]["chain_of_thought_policy"]["hidden_model_chain_of_thought_exposed"] is False
    assert agent_status["ok"] is True
    assert browser_capture["ok"] is False
    assert browser_capture["finding"] == "confirmation_required"
    assert timeline["ok"] is True
    assert timeline["data"]["schema_id"] == "ion.project_workbench_timeline.v1"
    assert agent_status["data"]["schema_id"] == "ion.agent_invocation_broker.v1"
    assert forbidden["ok"] is False
    assert forbidden["finding"] == "forbidden_capability"


def test_fanout_dryrun_status_tool_is_read_only_and_compact(tmp_path):
    _seed_root(tmp_path)
    _seed_fanout_dryrun_status_artifacts(tmp_path)
    queue_path = tmp_path / "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json"
    message_path = tmp_path / "ION/05_context/current/ACTIVE_CARRIER_MESSAGE_QUEUE.json"
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text("{\"requests\":[]}\n", encoding="utf-8")
    message_path.write_text("{\"messages\":[]}\n", encoding="utf-8")
    queue_before = hashlib.sha256(queue_path.read_bytes()).hexdigest()
    message_before = hashlib.sha256(message_path.read_bytes()).hexdigest()

    tool = call_chatgpt_connector_tool(tmp_path, "ion_kernel_fanout_carrier_dryrun_status", {})

    assert "ion_kernel_fanout_carrier_dryrun_status" in STATUS_READ_TOOLS
    assert tool["ok"] is True
    assert tool["mutates_active_state"] is False
    status = tool["data"]
    assert status["schema_id"] == "ion.kernel_fanout_carrier_dryrun_status.v1"
    assert status["queue_mutation_detected"] is False
    assert status["timeout_fail_closed_summary"]["fail_closed"] is True
    assert status["conflict_lock_summary"]["conflict_deferral_events"] == 8
    verdicts = {row["scenario"]: row["settlement_verdict"] for row in status["scenario_verdicts"]}
    assert verdicts == {
        "success": "SMOKE_READY",
        "forced_timeout": "SMOKE_BLOCKED",
        "forced_conflict": "SMOKE_READY",
    }
    assert any(row["kind"] == "latest_dryrun_result" and row["sha256"] for row in status["receipt_artifacts"])
    assert hashlib.sha256(queue_path.read_bytes()).hexdigest() == queue_before
    assert hashlib.sha256(message_path.read_bytes()).hexdigest() == message_before


def test_codex_queue_parallel_plan_preview_tool_is_read_only(tmp_path):
    _seed_root(tmp_path)
    queue_path = tmp_path / "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json"
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text("{\"schema_id\":\"queue\",\"requests\":[]}\n", encoding="utf-8")
    queue_before = hashlib.sha256(queue_path.read_bytes()).hexdigest()

    result = call_chatgpt_connector_tool(
        tmp_path,
        "ion_codex_queue_parallel_plan_preview",
        {
            "proposed_request": {
                "objective": "Preview a read-only scheduler request.",
                "lane_request": "audit_lane",
                "read_set": ["ION/04_packages/kernel/ion_codex_queue_runner.py"],
                "write_set": [],
                "authority_class": "read_only",
            }
        },
    )

    assert "ion_codex_queue_parallel_plan_preview" in STATUS_READ_TOOLS
    assert result["ok"] is True
    assert result["mutates_active_state"] is False
    assert result["data"]["schema_id"] == "ion.codex_queue_parallel_plan_preview.v0_1"
    assert result["data"]["lane_resolved"] == "audit_lane"
    assert result["data"]["lease_decision"]["would_enqueue"] is False
    assert result["data"]["production_authority"] is False
    assert result["data"]["live_execution_authority"] is False
    assert result["data"]["accepted_state_claim"] is False
    assert hashlib.sha256(queue_path.read_bytes()).hexdigest() == queue_before


def test_live_status_preview_refuses_non_public_target(tmp_path):
    _seed_root(tmp_path)

    status = call_chatgpt_connector_tool(
        tmp_path,
        "ion_codex_worker_live_status",
        {"include_preview": True, "preview_target": ".env", "max_preview_bytes": 128},
    )

    assert status["ok"] is True
    preview = status["data"]["live_worker_telemetry"]["preview"]
    assert preview["requested"] is True
    assert preview["included"] is False
    assert preview["finding"] == "preview_target_not_allowed_public_log_only"


def test_queue_tool_writes_only_bounded_operator_queue(tmp_path):
    _seed_root(tmp_path)

    result = call_chatgpt_connector_tool(
        tmp_path,
        "ion_queue_operator_message",
        {"message": "V120 bounded connector queue test", "priority": 70},
    )

    queue_path = tmp_path / "ION/05_context/current/ACTIVE_OPERATOR_MESSAGE_QUEUE.json"
    assert result["ok"] is True
    assert result["mutates_active_state"] is True
    assert result["data"]["queue_path"] == "ION/05_context/current/ACTIVE_OPERATOR_MESSAGE_QUEUE.json"
    assert queue_path.exists()
    assert "chatgpt_browser_connector" in queue_path.read_text(encoding="utf-8")


def test_connector_project_workbench_accepts_ion_aliases(tmp_path):
    _seed_root(tmp_path)

    ion_alias = call_chatgpt_connector_tool(tmp_path, "ion_project_workspace_status", {"project_id": "ion"})
    active_alias = call_chatgpt_connector_tool(
        tmp_path,
        "ion_project_workspace_status",
        {"project_id": "active_ion_control"},
    )

    assert ion_alias["ok"] is True
    assert active_alias["ok"] is True
    assert ion_alias["data"]["project"]["project_id"] == "ion_dev"
    assert active_alias["data"]["project"]["project_id"] == "ion_dev"


def test_project_context_capsule_and_file_slice_read_tools(tmp_path, monkeypatch):
    _seed_root(tmp_path)
    cosmos = tmp_path / "cosmos"
    (cosmos / "src").mkdir(parents=True, exist_ok=True)
    (cosmos / "src/App.tsx").write_text("export const VALUE = 1;\n", encoding="utf-8")
    (cosmos / "package.json").write_text("{\"scripts\":{}}\n", encoding="utf-8")
    monkeypatch.setenv("ION_COSMOS_PROJECT_ROOT", cosmos.as_posix())

    capsule = call_chatgpt_connector_tool(tmp_path, "ion_project_context_capsule", {"project_id": "cosmos", "probe_preview": False})
    slice_read = call_chatgpt_connector_tool(
        tmp_path,
        "ion_project_file_slice_read",
        {"project_id": "cosmos", "path": "src/App.tsx", "start_byte": 0, "max_bytes": 64},
    )

    assert "ion_project_context_capsule" in STATUS_READ_TOOLS
    assert "ion_project_file_slice_read" in STATUS_READ_TOOLS
    assert capsule["ok"] is True
    assert capsule["data"]["schema_id"] == "ion.project_context_capsule.v1"
    assert slice_read["ok"] is True
    assert slice_read["data"]["schema_id"] == "ion.project_file_slice_read_result.v1"
    assert slice_read["data"]["is_final_chunk"] is True


def test_connector_timeout_policy_enforces_minimum_for_agent_invoke(tmp_path, monkeypatch):
    import kernel.ion_chatgpt_browser_mcp_connector_contract as contract

    _seed_root(tmp_path)
    captured: dict[str, int] = {}

    def fake_invoke_agent(_root, **kwargs):
        captured["timeout_seconds"] = int(kwargs["timeout_seconds"])
        return {"ok": True, "result": "QUEUED"}

    monkeypatch.setattr(contract, "invoke_agent", fake_invoke_agent)
    result = call_chatgpt_connector_tool(
        tmp_path,
        "ion_agent_invoke",
        {
            "agent": "context_cartographer",
            "objective": "cartography proof packet timeout policy smoke",
            "start": True,
            "timeout_seconds": 30,
        },
    )

    assert result["ok"] is True
    assert captured["timeout_seconds"] == 900


def test_connector_timeout_policy_enforces_minimum_for_cartography_queue_run(tmp_path, monkeypatch):
    import kernel.ion_chatgpt_browser_mcp_connector_contract as contract

    _seed_root(tmp_path)
    request_rel = "ION/05_context/current/chatgpt_connector/codex_work_requests/cartography_timeout_test.json"
    request_path = tmp_path / request_rel
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": "codex_req_cartography_timeout_test",
                "objective": "Runtime cartography proof run",
                "request_kind": "runtime_cartography",
                "status": "QUEUED_FOR_CODEX_CARRIER",
                "requested_by": "chatgpt_browser_connector",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    captured: dict[str, int] = {}

    def fake_process_codex_queue_once(_root, **kwargs):
        captured["timeout_seconds"] = int(kwargs["timeout_seconds"])
        captured["lane_id"] = kwargs.get("lane_id")
        return {"ok": True, "result": "PREPARED"}

    monkeypatch.setattr(contract, "process_codex_queue_once", fake_process_codex_queue_once)
    result = call_chatgpt_connector_tool(
        tmp_path,
        "ion_codex_queue_process_once",
        {"request_path": request_rel, "lane_id": "context_lane", "start": True, "timeout_seconds": 180},
    )

    assert result["ok"] is True
    assert captured["timeout_seconds"] == 900
    assert captured["lane_id"] == "context_lane"



def test_codex_queue_process_once_returns_compact_envelope_by_default(monkeypatch, tmp_path):
    import kernel.ion_chatgpt_browser_mcp_connector_contract as contract

    _seed_root(tmp_path)
    run_dir = tmp_path / "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_compact"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "stdout.log").write_text("stdout\n" + ("S" * 5000), encoding="utf-8")
    (run_dir / "stderr.log").write_text("stderr\n" + ("E" * 4000), encoding="utf-8")
    (run_dir / "worker_stdout.log").write_text("worker stdout\n", encoding="utf-8")
    (run_dir / "worker_stderr.log").write_text("worker stderr\n", encoding="utf-8")
    (run_dir / "last_message.md").write_text("result\n" + ("R" * 6000), encoding="utf-8")
    (run_dir / "task_return_body.md").write_text("### RESULT\ncompact test\n", encoding="utf-8")
    (run_dir / "context_receipt.json").write_text("{\"ok\":true}\n", encoding="utf-8")
    (run_dir / "run.json").write_text("{\"ok\":true}\n", encoding="utf-8")
    request_rel = "ION/05_context/current/chatgpt_connector/codex_work_requests/req_compact.json"
    request_path = tmp_path / request_rel
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_text("{\"request_id\":\"req_compact\"}\n", encoding="utf-8")

    def fake_process_codex_queue_once(_root, **_kwargs):
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "RETURN_RECORDED_PROOF_ACCEPTED",
            "run": {
                "run_id": "run_compact",
                "request_id": "req_compact",
                "request_path": request_rel,
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_compact/run.json",
                "run_dir": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_compact",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "stdout_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_compact/stdout.log",
                "stderr_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_compact/stderr.log",
                "last_message_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_compact/last_message.md",
                "task_return_body_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_compact/task_return_body.md",
                "context_receipt_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_compact/context_receipt.json",
                "changed_paths": [
                    "ION/04_packages/kernel/ion_codex_queue_runner.py",
                    "ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py",
                ],
                "worker_lifecycle_events": [{"event": "worker_terminal", "terminal_state": "accepted"}],
                "submit_result": {
                    "accepted_for_carrier_intake": True,
                    "packet_path": "ION/05_context/current/chatgpt_connector/task_returns/return_compact.json",
                },
                "raw_large_blob": "X" * 50000,
            },
        }

    monkeypatch.setattr(contract, "process_codex_queue_once", fake_process_codex_queue_once)
    result = call_chatgpt_connector_tool(tmp_path, "ion_codex_queue_process_once", {"start": True})

    assert result["ok"] is True
    data = result["data"]
    assert data["schema_id"] == "ion.codex_queue_process_once_compact.v1"
    assert data["run_id"] == "run_compact"
    assert data["request_id"] == "req_compact"
    assert data["changed_files"]["count"] == 2
    assert "run" not in data
    assert data["preview"]["included"] is True
    assert data["preview"]["target"] == "result"
    assert len(data["preview"]["text"].encode("utf-8")) <= 2048
    assert data["artifacts"]["stdout"]["bytes"] is not None
    assert data["artifacts"]["stdout"]["sha256"]
    assert data["receipts"]["task_return_packet_path"] == "ION/05_context/current/chatgpt_connector/task_returns/return_compact.json"


def test_codex_worker_live_status_defaults_to_compact_and_2048_preview(monkeypatch, tmp_path):
    import kernel.ion_chatgpt_browser_mcp_connector_contract as contract

    _seed_root(tmp_path)
    run_dir = tmp_path / "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_live_compact"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "stderr.log").write_text("stderr\n" + ("Z" * 4000), encoding="utf-8")
    (run_dir / "run.json").write_text("{\"run\":\"packet\"}\n", encoding="utf-8")
    captured = {}

    def fake_status(_root, **kwargs):
        captured.update(kwargs)
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "verdict": "ION_CODEX_QUEUE_RUNNER_READY",
            "runner_state_path": "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json",
            "queue_path": "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json",
            "queued_request_count": 1,
            "next_request_path": "ION/05_context/current/chatgpt_connector/codex_work_requests/req.json",
            "active_run": None,
            "active_process_running": False,
            "stale_active_run_detected": False,
            "reconciliation": {"action": "no_active_run"},
            "latest_runs": [],
            "failure_classes": [],
            "automation_surface": "ion_codex_queue_process_once",
            "autorun_loop_state": "NOT_STARTED_PROCESS_ONCE_AVAILABLE",
            "ai_movement_preflight_warning_map": {
                "schema_id": "ion.codex_queue_runner_ai_movement_warning_map.v1",
                "status": "READ_ONLY_PROJECTION",
                "preflight_count": 4,
                "accepted_count": 3,
                "blocked_count": 1,
                "warning_count": 1,
                "agent_cwd_boundary_missing_count": 0,
                "agent_cwd_boundary_blocked_count": 1,
                "agent_cwd_boundary_warning_count": 0,
                "operator_warning_count": 2,
                "latest_preflight": {"request_id": "req_live", "receipt_path": "ION/05_context/current/chatgpt_connector/codex_queue_preflights/preflight.json"},
                "latest_preflights": [{"huge": "Q" * 20000}],
                "warning_rows": [{"huge": "W" * 20000}],
            },
            "live_worker_telemetry": {
                "schema_id": "ion.codex_worker_live_status.v1",
                "phase_status": "template-invalid",
                "run_status": "RETURN_TEMPLATE_INVALID",
                "active_worker_pid": None,
                "active_run_id": "run_live",
                "request_id": "req_live",
                "request_path": "ION/05_context/current/chatgpt_connector/codex_work_requests/req.json",
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_live_compact/run.json",
                "worker_lifecycle_events": [{"event": "worker_terminal", "terminal_state": "template_invalid"}],
                "latest_worker_lifecycle_event": {"event": "worker_terminal", "terminal_state": "template_invalid"},
                "terminal_intake_result": {"state": "template_invalid", "accepted_for_carrier_intake": False},
                "proof_gate_preflight": {"determinable": True},
                "ai_movement_gate_preflight": {"accepted": True},
                "preview": {"requested": True, "included": True, "target": "stderr", "text": "T" * 3000},
                "preferred_preview": {"target": "stderr"},
                "artifacts": {
                    "run_packet": {"path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_live_compact/run.json", "exists": True},
                    "stderr": {"path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_live_compact/stderr.log", "exists": True},
                },
                "observability_trace": {"huge": "T" * 50000},
            },
        }

    monkeypatch.setattr(contract, "build_codex_queue_runner_status", fake_status)

    compact = call_chatgpt_connector_tool(tmp_path, "ion_codex_worker_live_status", {})
    assert compact["ok"] is True
    assert captured["include_preview"] is True
    assert captured["preview_max_bytes"] == 2048
    telemetry = compact["data"]["live_worker_telemetry"]
    assert "observability_trace" not in telemetry
    assert telemetry["preview"]["included"] is True
    assert compact["data"]["ai_movement_preflight_warning_map_summary"]["preflight_count"] == 4

    with_trace = call_chatgpt_connector_tool(
        tmp_path,
        "ion_codex_worker_live_status",
        {"include_observability_trace": True},
    )
    assert with_trace["ok"] is True
    assert "observability_trace" in with_trace["data"]["live_worker_telemetry"]


def test_codex_work_queue_supports_cursor_filter_and_compact_rows(tmp_path):
    _seed_root(tmp_path)
    request_root = tmp_path / "ION/05_context/current/chatgpt_connector/codex_work_requests"
    request_root.mkdir(parents=True, exist_ok=True)
    rows = [
        ("2026-05-30T000003Z_req3.json", "req3", "QUEUED_FOR_CODEX_CARRIER"),
        ("2026-05-30T000002Z_req2.json", "req2", "RETURN_RECORDED_PROOF_ACCEPTED"),
        ("2026-05-30T000001Z_req1.json", "req1", "QUEUED_FOR_CODEX_CARRIER"),
    ]
    for filename, request_id, status in rows:
        (request_root / filename).write_text(
            json.dumps(
                {
                    "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                    "request_id": request_id,
                    "objective": f"Objective {request_id}",
                    "status": status,
                    "created_at": "2026-05-30T00:00:00+00:00",
                    "updated_at": "2026-05-30T00:00:00+00:00",
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )

    first_page = call_chatgpt_connector_tool(
        tmp_path,
        "ion_codex_work_queue",
        {"limit": 1, "status_filter": "queued_for_codex_carrier"},
    )
    assert first_page["ok"] is True
    assert first_page["data"]["request_count"] == 1
    assert first_page["data"]["total_request_count"] == 2
    assert first_page["data"]["has_more"] is True
    assert first_page["data"]["next_cursor"]
    assert "latest_preflights" not in first_page["data"]["ai_movement_preflight_warning_map"]
    first_request = first_page["data"]["requests"][0]
    assert first_request["status"] == "QUEUED_FOR_CODEX_CARRIER"

    second_page = call_chatgpt_connector_tool(
        tmp_path,
        "ion_codex_work_queue",
        {
            "limit": 1,
            "status_filter": "queued_for_codex_carrier",
            "cursor": first_page["data"]["next_cursor"],
            "include_ai_movement_rows": True,
            "ai_movement_row_limit": 3,
        },
    )
    assert second_page["ok"] is True
    assert second_page["data"]["request_count"] == 1
    assert second_page["data"]["has_more"] is False
    assert second_page["data"]["cursor_found"] is True
    assert second_page["data"]["requests"][0]["request_id"] == "req1"
    compact_ai = second_page["data"]["ai_movement_preflight_warning_map"]
    assert compact_ai["row_limit"] == 3
    assert "latest_preflights" in compact_ai
    assert "warning_rows" in compact_ai


def test_codex_work_queue_projects_queue_lifecycle_decision(tmp_path):
    _seed_root(tmp_path)
    request_root = tmp_path / "ION/05_context/current/chatgpt_connector/codex_work_requests"
    request_root.mkdir(parents=True, exist_ok=True)
    (request_root / "classified.json").write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": "req_classified",
                "objective": "Classified terminal request",
                "status": "RETURN_TEMPLATE_INVALID",
                "created_at": "2026-05-30T00:00:00+00:00",
                "updated_at": "2026-05-30T00:00:00+00:00",
                "queue_lifecycle_decision": {
                    "schema_id": "ion.codex_work_request_queue_lifecycle_decision.v1",
                    "disposition": "repair_return_contract_from_linked_return",
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    queue = call_chatgpt_connector_tool(tmp_path, "ion_codex_work_queue", {"limit": 10})

    assert queue["ok"] is True
    request = queue["data"]["requests"][0]
    assert request["request_id"] == "req_classified"
    assert request["queue_lifecycle_decision"]["disposition"] == "repair_return_contract_from_linked_return"


def test_codex_work_queue_projects_lane_routes_and_materializes_lane_files(tmp_path):
    _seed_root(tmp_path)
    request_root = tmp_path / "ION/05_context/current/chatgpt_connector/codex_work_requests"
    request_root.mkdir(parents=True, exist_ok=True)
    rows = [
        ("2026-05-30T000000Z_legacy.json", "req_legacy", "Old orphan item with no route", {}),
        ("2026-05-30T000001Z_architecture.json", "req_arch", "Architecture proposal", {"work_class": "architecture"}),
        ("2026-05-30T000002Z_implementation.json", "req_impl", "Implementation patch", {"work_class": "implementation"}),
        (
            "2026-05-30T000002Z_approval.json",
            "req_approval",
            "Issue explicit accepted_state_movement_authority receipt",
            {"work_class": "domain_weaver_wave2_explicit_accepted_state_movement_authority_receipt_issuance"},
        ),
        (
            "2026-05-30T000003Z_comms.json",
            "req_comms",
            "ION agent invocation for COMMS_CARTOGRAPHER (role.comms_cartographer) with Steward membrane boilerplate",
            {"work_class": "agent_invocation"},
        ),
    ]
    for filename, request_id, objective, extra in rows:
        payload = {
            "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
            "request_id": request_id,
            "objective": objective,
            "status": "QUEUED_FOR_CODEX_CARRIER",
            "target_root_id": "active_ion_control",
            "movement_class": "ION_KERNEL_CONTROL_MOVEMENT",
            "created_at": "2026-05-30T00:00:00+00:00",
            "updated_at": "2026-05-30T00:00:00+00:00",
        }
        payload.update(extra)
        (request_root / filename).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    queue = call_chatgpt_connector_tool(tmp_path, "ion_codex_work_queue", {"limit": 10})
    assert queue["ok"] is True
    lanes_by_request = {row["request_id"]: row["lane_id"] for row in queue["data"]["requests"]}
    assert lanes_by_request["req_arch"] == "architecture_lane"
    assert lanes_by_request["req_impl"] == "implementation_lane"
    assert lanes_by_request["req_approval"] == "approval_governance_lane"
    assert lanes_by_request["req_comms"] == "comms_lane"
    assert lanes_by_request["req_legacy"] == "needs_triage"

    status = build_codex_queue_runner_status(tmp_path)
    assert status["lane_queue"]["lane_counts"]["architecture_lane"] == 1
    assert status["lane_queue"]["lane_counts"]["implementation_lane"] == 1
    assert status["lane_queue"]["lane_counts"]["approval_governance_lane"] == 1
    assert status["lane_queue"]["lane_counts"]["comms_lane"] == 1
    assert status["lane_queue"]["lane_counts"]["needs_triage"] == 1

    lane_dir = tmp_path / "ION/05_context/current/chatgpt_connector/work_lanes"
    implementation_lane = json.loads((lane_dir / "implementation_lane.json").read_text(encoding="utf-8"))
    needs_triage = json.loads((lane_dir / "needs_triage.json").read_text(encoding="utf-8"))
    assert implementation_lane["next_request_path"].endswith("2026-05-30T000002Z_implementation.json")
    assert needs_triage["requests"][0]["request_id"] == "req_legacy"


def test_codex_queue_process_once_lane_selector_bypasses_unclassified_global_head(tmp_path):
    _seed_root(tmp_path)
    request_root = tmp_path / "ION/05_context/current/chatgpt_connector/codex_work_requests"
    request_root.mkdir(parents=True, exist_ok=True)
    rows = [
        ("2026-05-30T000000Z_legacy.json", "req_legacy", "Old orphan item with no route", {}),
        ("2026-05-30T000001Z_architecture.json", "req_arch", "Architecture proposal", {"work_class": "architecture"}),
        ("2026-05-30T000002Z_implementation.json", "req_impl", "Implementation patch", {"work_class": "implementation"}),
        (
            "2026-05-30T000003Z_approval.json",
            "req_approval",
            "Approval governance authority receipt issuance",
            {"work_class": "domain_weaver_wave2_explicit_accepted_state_movement_authority_receipt_issuance"},
        ),
    ]
    for filename, request_id, objective, extra in rows:
        payload = {
            "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
            "request_id": request_id,
            "objective": objective,
            "status": "QUEUED_FOR_CODEX_CARRIER",
            "target_root_id": "active_ion_control",
            "movement_class": "ION_KERNEL_CONTROL_MOVEMENT",
            "created_at": "2026-05-30T00:00:00+00:00",
            "updated_at": "2026-05-30T00:00:00+00:00",
        }
        payload.update(extra)
        (request_root / filename).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    implementation = process_codex_queue_once(tmp_path, lane_id="implementation_lane", start=False, timeout_seconds=30)
    architecture = process_codex_queue_once(tmp_path, lane_id="architecture_lane", start=False, timeout_seconds=30)
    approval = process_codex_queue_once(tmp_path, lane_id="approval_governance_lane", start=False, timeout_seconds=30)

    assert implementation["ok"] is True
    assert implementation["run"]["request_id"] == "req_impl"
    assert implementation["run"]["lane_id"] == "implementation_lane"
    assert implementation["run"]["request_path"].endswith("2026-05-30T000002Z_implementation.json")
    assert architecture["ok"] is True
    assert architecture["run"]["request_id"] == "req_arch"
    assert architecture["run"]["lane_id"] == "architecture_lane"
    assert approval["ok"] is True
    assert approval["run"]["request_id"] == "req_approval"
    assert approval["run"]["lane_id"] == "approval_governance_lane"


def test_codex_worker_live_status_supports_latest_runs_cursor_filter_and_lifecycle_limit(monkeypatch, tmp_path):
    import kernel.ion_chatgpt_browser_mcp_connector_contract as contract

    _seed_root(tmp_path)
    run_dir = tmp_path / "ION/05_context/current/chatgpt_connector/codex_queue_runs/live_status_paging"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text("{\"ok\":true}\n", encoding="utf-8")

    def fake_status(_root, **_kwargs):
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "verdict": "ION_CODEX_QUEUE_RUNNER_READY",
            "runner_state_path": "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json",
            "queue_path": "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json",
            "queued_request_count": 0,
            "next_request_path": None,
            "active_run": None,
            "active_process_running": False,
            "stale_active_run_detected": False,
            "reconciliation": {"action": "no_active_run"},
            "latest_runs": [
                {
                    "run_id": "run3",
                    "request_id": "req3",
                    "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                    "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run3/run.json",
                    "worker_lifecycle_events": [{"event": "worker_terminal", "terminal_state": "accepted"}],
                },
                {
                    "run_id": "run2",
                    "request_id": "req2",
                    "status": "RETURN_TEMPLATE_INVALID",
                    "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run2/run.json",
                    "worker_lifecycle_events": [{"event": "worker_terminal", "terminal_state": "template_invalid"}],
                },
                {
                    "run_id": "run1",
                    "request_id": "req1",
                    "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                    "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run1/run.json",
                    "worker_lifecycle_events": [{"event": "worker_terminal", "terminal_state": "accepted"}],
                },
            ],
            "failure_classes": [],
            "automation_surface": "ion_codex_queue_process_once",
            "autorun_loop_state": "NOT_STARTED_PROCESS_ONCE_AVAILABLE",
            "ai_movement_preflight_warning_map": {
                "schema_id": "ion.codex_queue_runner_ai_movement_warning_map.v1",
                "status": "READ_ONLY_PROJECTION",
                "preflight_count": 0,
                "accepted_count": 0,
                "blocked_count": 0,
                "warning_count": 0,
                "operator_warning_count": 0,
                "agent_cwd_boundary_missing_count": 0,
                "agent_cwd_boundary_blocked_count": 0,
                "agent_cwd_boundary_warning_count": 0,
            },
            "live_worker_telemetry": {
                "schema_id": "ion.codex_worker_live_status.v1",
                "phase_status": "active",
                "run_status": "CODEX_CLI_RUNNING",
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/live_status_paging/run.json",
                "worker_lifecycle_events": [
                    {"event": "worker_boot", "at": "2026-05-30T00:00:00+00:00"},
                    {"event": "worker_stdout", "at": "2026-05-30T00:00:01+00:00"},
                    {"event": "worker_stderr", "at": "2026-05-30T00:00:02+00:00"},
                ],
                "latest_worker_lifecycle_event": {"event": "worker_stderr", "at": "2026-05-30T00:00:02+00:00"},
                "preview": {"requested": True, "included": False},
                "artifacts": {
                    "run_packet": {"path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/live_status_paging/run.json", "exists": True},
                },
            },
        }

    monkeypatch.setattr(contract, "build_codex_queue_runner_status", fake_status)

    first = call_chatgpt_connector_tool(
        tmp_path,
        "ion_codex_worker_live_status",
        {"latest_runs_limit": 1, "lifecycle_limit": 2, "latest_runs_status_filter": "return_recorded_proof_accepted"},
    )
    assert first["ok"] is True
    first_data = first["data"]
    first_telemetry = first_data["live_worker_telemetry"]
    assert first_telemetry["worker_lifecycle_limit"] == 2
    assert first_telemetry["worker_lifecycle_events_truncated"] is True
    assert len(first_telemetry["worker_lifecycle_events"]) == 2
    assert first_data["latest_runs_filtered_count"] == 2
    assert first_data["latest_runs_has_more"] is True
    assert len(first_data["latest_runs"]) == 1
    assert first_data["latest_runs"][0]["run_id"] == "run3"

    second = call_chatgpt_connector_tool(
        tmp_path,
        "ion_codex_worker_live_status",
        {
            "latest_runs_limit": 1,
            "lifecycle_limit": 2,
            "latest_runs_status_filter": "return_recorded_proof_accepted",
            "latest_runs_cursor": first_data["latest_runs_next_cursor"],
        },
    )
    assert second["ok"] is True
    second_data = second["data"]
    assert second_data["latest_runs_cursor_found"] is True
    assert second_data["latest_runs_has_more"] is False
    assert len(second_data["latest_runs"]) == 1
    assert second_data["latest_runs"][0]["run_id"] == "run1"


def test_codex_work_packet_request_is_idempotent_for_safe_retry(tmp_path):
    _seed_root(tmp_path)
    args = {
        "objective": "B00 duplicate no-receipt retry should not create another work packet",
        "idempotency_key": "b00-safe-retry-key",
    }

    first = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", args)
    second = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", args)
    queue = call_chatgpt_connector_tool(tmp_path, "ion_codex_work_queue", {"limit": 10})

    assert first["ok"] is True
    assert first["mutates_active_state"] is True
    assert second["ok"] is True
    assert second["mutates_active_state"] is False
    assert second["data"]["idempotent_replay"] is True
    assert second["data"]["duplicate_prevented"] is True
    assert second["data"]["request_id"] == first["data"]["request_id"]
    assert second["data"]["packet_path"] == first["data"]["packet_path"]
    assert len(list((tmp_path / "ION/05_context/current/chatgpt_connector/codex_work_requests").glob("*.json"))) == 1
    assert queue["data"]["request_count"] == 1


def test_codex_work_queue_projects_ai_movement_preflight_warnings(tmp_path):
    _seed_root(tmp_path)
    request = call_chatgpt_connector_tool(
        tmp_path,
        "ion_request_codex_work_packet",
        {"objective": "Preflight warning projection test", "idempotency_key": "preflight-warning-projection"},
    )
    packet_path = request["data"]["packet_path"]
    packet = json.loads((tmp_path / packet_path).read_text(encoding="utf-8"))
    receipt_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_preflights/"
        "2026-05-18T000000Z_codex_req_warning_ai_movement_preflight.json"
    )
    receipt_path = tmp_path / receipt_rel
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_ai_movement_preflight.v1",
                "generated_at": "2026-05-18T00:00:00+00:00",
                "accepted": False,
                "verdict": "BLOCKED",
                "finding": "ai_movement_gate_blocked",
                "request_id": packet["request_id"],
                "request_path": packet_path,
                "receipt_path": receipt_rel,
                "runner_start_allowed": False,
                "worker_process_started": False,
                "root_envelope": {
                    "target_root_id": "browser_extension",
                    "movement_class": "BROWSER_EXTENSION_MOVEMENT",
                    "root_relation": "sibling_project_root",
                    "target_project_root": str(tmp_path.parent / "browser_extension"),
                    "target_content_root": str(tmp_path.parent / "browser_extension"),
                    "agent_cwd_boundary": {
                        "schema_id": "ion.agent_cwd_boundary.v1",
                        "accepted": False,
                        "status": "AGENT_CWD_BLOCKED",
                        "workspace_root": str(tmp_path.parent),
                        "active_ion_root": str(tmp_path),
                        "control_plane_cwd": str(tmp_path),
                        "worker_launch_cwd": str(tmp_path),
                        "target_command_cwd": str(tmp_path),
                        "target_project_root": str(tmp_path.parent / "browser_extension"),
                        "target_content_root": str(tmp_path.parent / "browser_extension"),
                        "target_root_id": "browser_extension",
                        "target_root_class": "SIBLING_PROJECT_ROOT",
                        "target_root_relation": "sibling_project_root",
                        "blockers": [
                            {
                                "code": "WORKER_LAUNCH_CWD_TARGET_MISMATCH",
                                "detail": "sibling movement cannot launch from active ION root",
                            }
                        ],
                        "warnings": [],
                    },
                },
                "gate_decision": {
                    "schema_id": "ion.ai_movement_gate_decision.v1",
                    "accepted": False,
                    "verdict": "BLOCKED",
                    "target_root_id": "browser_extension",
                    "movement_class": "BROWSER_EXTENSION_MOVEMENT",
                    "blockers": [{"code": "SIBLING_ROOT_IMPLICIT_EDIT", "detail": "wrong sibling target"}],
                    "warnings": [],
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    queue = call_chatgpt_connector_tool(tmp_path, "ion_codex_work_queue", {"limit": 10})

    assert queue["ok"] is True
    warning_map = queue["data"]["ai_movement_preflight_warning_map"]
    assert warning_map["blocked_count"] == 1
    assert warning_map["operator_warning_count"] >= 1
    assert warning_map["agent_cwd_boundary_blocked_count"] == 1
    row = queue["data"]["requests"][0]
    assert row["ai_movement_preflight_projection"]["warning_level"] == "blocked"
    assert row["ai_movement_preflight_projection"]["target_root_id"] == "browser_extension"
    assert row["agent_cwd_boundary_projection"]["warning_level"] == "blocked"
    assert row["agent_cwd_boundary_projection"]["worker_launch_cwd"] == str(tmp_path)
    assert "WORKER_LAUNCH_CWD_TARGET_MISMATCH" in row["agent_cwd_boundary_projection"]["blocker_codes"]


def test_codex_work_queue_projects_target_binding_audit(tmp_path):
    _seed_root(tmp_path)
    current = call_chatgpt_connector_tool(
        tmp_path,
        "ion_request_codex_work_packet",
        {
            "objective": "Queue target binding audit current packet",
            "idempotency_key": "target-binding-audit-current",
            "target_root_id": "browser_extension",
            "target_project_subpath": "ion_chatops_bridge",
        },
    )
    request_root = tmp_path / "ION/05_context/current/chatgpt_connector/codex_work_requests"
    legacy_explicit_path = request_root / "legacy_explicit_target.json"
    legacy_explicit_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": "codex_req_legacy_explicit_target",
                "objective": "Legacy explicit target packet",
                "status": "QUEUED_FOR_CODEX_CARRIER",
                "target_root_id": "active_ion_control",
                "movement_class": "ION_KERNEL_CONTROL_MOVEMENT",
                "created_at": "2026-05-19T00:00:00+00:00",
                "updated_at": "2026-05-19T00:00:00+00:00",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    targetless_path = request_root / "legacy_targetless.json"
    targetless_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": "codex_req_legacy_targetless",
                "objective": "Legacy targetless packet",
                "status": "QUEUED_FOR_CODEX_CARRIER",
                "created_at": "2026-05-19T00:00:01+00:00",
                "updated_at": "2026-05-19T00:00:01+00:00",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    queue = call_chatgpt_connector_tool(tmp_path, "ion_codex_work_queue", {"limit": 10})

    assert current["ok"] is True
    assert queue["ok"] is True
    audit = queue["data"]["ai_movement_target_binding_audit"]
    assert audit["request_count"] == 3
    assert audit["accepted_count"] == 2
    assert audit["warning_count"] == 1
    assert audit["blocked_count"] == 1
    rows = {row["request_id"]: row for row in queue["data"]["requests"]}
    current_projection = rows[current["data"]["request_id"]]["ai_movement_target_binding_projection"]
    legacy_projection = rows["codex_req_legacy_explicit_target"]["ai_movement_target_binding_projection"]
    targetless_projection = rows["codex_req_legacy_targetless"]["ai_movement_target_binding_projection"]
    assert current_projection["status"] == "TARGET_BINDING_OK"
    assert current_projection["target_root_id"] == "browser_extension"
    assert legacy_projection["warning_level"] == "warning"
    assert legacy_projection["warning_codes"] == ["TARGET_BINDING_TEMPLATE_MISSING"]
    assert targetless_projection["warning_level"] == "blocked"
    assert targetless_projection["blocker_codes"] == ["TARGET_BINDING_MISSING"]


def test_codex_work_packet_request_persists_model_override_fields(tmp_path):
    _seed_root(tmp_path)
    args = {
        "objective": "Model override persistence test",
        "codex_model_override": {
            "selected_model": "gpt-5.5",
            "selected_reasoning_effort": "medium",
            "reason": "proof repair route",
        },
        "requested_model": "gpt-5.5",
        "requested_reasoning_effort": "medium",
        "model_override_reason": "fallback fields",
        "project_hash": "proj_hash_20260514_preview",
    }

    result = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", args)

    assert result["ok"] is True
    packet_path = tmp_path / result["data"]["packet_path"]
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    assert packet["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert packet["codex_model_override"]["selected_reasoning_effort"] == "medium"
    assert packet["codex_model_override"]["reason"] == "proof repair route"
    assert packet["requested_model"] == "gpt-5.5"
    assert packet["requested_reasoning_effort"] == "medium"
    assert packet["model_override_reason"] == "fallback fields"
    assert packet["project_hash"] == "proj_hash_20260514_preview"


def test_red_alert_work_packet_without_structured_route_is_rejected(tmp_path):
    _seed_root(tmp_path)

    result = call_chatgpt_connector_tool(
        tmp_path,
        "ion_request_codex_work_packet",
        {
            "objective": "RED ALERT: repair authority routing but omit structured fields",
            "idempotency_key": "red-alert-missing-override",
        },
    )

    assert result["ok"] is False
    assert result["finding"] == "structured_route_metadata_required_for_high_stakes_objective"
    assert result["data"]["prose_guardrail_triggered"] is True
    assert result["data"]["high_stakes"] is False


def test_red_alert_work_packet_requires_gpt55_high_or_xhigh_and_records_route_receipt(tmp_path):
    _seed_root(tmp_path)
    args = {
        "objective": "RED ALERT: route enforcement structured positive test",
        "idempotency_key": "red-alert-positive-001",
        "work_class": "red_alert",
        "risk_level": "red_alert",
        "route_family": "red_alert",
        "codex_model_override": {
            "selected_model": "gpt-5.5",
            "selected_reasoning_effort": "xhigh",
            "reason": "red alert route enforcement",
        },
        "requested_model": "gpt-5.5",
        "requested_reasoning_effort": "xhigh",
        "model_override_reason": "red alert route enforcement",
    }

    result = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", args)

    assert result["ok"] is True
    packet = json.loads((tmp_path / result["data"]["packet_path"]).read_text(encoding="utf-8"))
    receipt = packet["route_enforcement_receipt"]
    assert packet["work_class"] == "red_alert"
    assert packet["risk_level"] == "red_alert"
    assert packet["route_family"] == "red_alert"
    assert receipt["high_stakes"] is True
    assert receipt["model_override_receipt_required"] is True
    assert receipt["required_model_override"]["selected_model"] == "gpt-5.5"


def test_operator_release_packaging_work_packet_requires_artifact_hygiene_gate(tmp_path):
    _seed_root(tmp_path)
    args = {
        "objective": "Package final operator upload kit",
        "idempotency_key": "operator-release-packaging-001",
        "work_class": "operator_release_packaging",
        "risk_level": "critical",
        "route_family": "operator_release_packaging",
        "codex_model_override": {
            "selected_model": "gpt-5.5",
            "selected_reasoning_effort": "high",
            "reason": "operator release packaging gate",
        },
        "requested_model": "gpt-5.5",
        "requested_reasoning_effort": "high",
        "model_override_reason": "operator release packaging gate",
    }

    result = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", args)

    assert result["ok"] is True
    packet = json.loads((tmp_path / result["data"]["packet_path"]).read_text(encoding="utf-8"))
    assert packet["operator_artifact_hygiene_required"] is True
    assert "### OPERATOR ARTIFACT HYGIENE" in packet["return_contract_sections"]
    assert packet["route_enforcement_receipt"]["operator_artifact_hygiene_gate"]["checker"] == "ION/04_packages/kernel/ion_operator_artifact_hygiene_check.py"


def test_codex_work_packet_request_default_shape_unchanged_without_override(tmp_path):
    _seed_root(tmp_path)
    args = {
        "objective": "No override defaults stay unchanged",
    }

    result = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", args)

    assert result["ok"] is True
    packet_path = tmp_path / result["data"]["packet_path"]
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    assert "codex_model_override" not in packet
    assert "requested_model" not in packet
    assert "requested_reasoning_effort" not in packet
    assert "model_override_reason" not in packet
    assert packet["target_root_id"] == "active_ion_control"
    assert packet["movement_class"] == "ION_KERNEL_CONTROL_MOVEMENT"
    assert packet["ai_movement_request_template"]["schema_id"] == "ion.codex_work_request_target_binding.v1"
    assert packet["ai_movement_request_template"]["binding_source"] == "default.active_ion_control"


def test_codex_work_packet_request_preserves_explicit_ai_movement_target_binding(tmp_path):
    _seed_root(tmp_path)
    args = {
        "objective": "Patch browser extension queue panel warning surface.",
        "target_root_id": "browser_extension",
        "target_project_subpath": "ion_chatops_bridge",
        "planned_writes": ["src/content.ts"],
    }

    result = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", args)

    assert result["ok"] is True
    packet = json.loads((tmp_path / result["data"]["packet_path"]).read_text(encoding="utf-8"))
    binding = packet["ai_movement_request_template"]
    assert packet["target_root_id"] == "browser_extension"
    assert packet["movement_class"] == "BROWSER_EXTENSION_MOVEMENT"
    assert packet["target_project_subpath"] == "ion_chatops_bridge"
    assert packet["planned_writes"] == ["src/content.ts"]
    assert binding["template_ref"] == "ION/07_templates/ai_movement/ION_CODEX_WORK_REQUEST_TARGET_BINDING.template.yaml"
    assert binding["binding_source"] == "request.target_root_id"
    assert binding["target_project_subpath"] == "ion_chatops_bridge"
    assert result["data"]["ai_movement_target_binding"]["target_root_id"] == "browser_extension"


def test_request_codex_work_packet_preserves_domain_weaver_identity_fields(tmp_path):
    _seed_root(tmp_path)
    args = {
        "objective": "Domain Weaver spawn dispatch for context cartographer.",
        "idempotency_key": "domain-weaver-identity-preservation-001",
        "request_kind": "domain_weaver_spawn_dispatch",
        "work_class": "domain_weaver_spawn_dispatch",
        "route_family": "domain_weaver_larger_fanout_control_plane",
        "domain_id": "domain.agent_communication_systems",
        "agent_role_id": "role.context_cartographer",
        "agent_role": "role.context_cartographer",
        "role_tier": "specialist",
        "callsign": "Lovelace",
        "true_name": "Ada Lovelace",
        "domain_context_package": "ION/05_context/current/domain_weaver/.ion/ACTIVE_CONTEXT_PACKAGE.md",
        "planned_writes": [
            "ION/05_context/current/domain_weaver/workers/lovelace/context/candidates/result.candidate.json"
        ],
        "required_context_reads": [
            {
                "kind": "file",
                "path": "ION/05_context/current/domain_weaver/AGENTS.md",
                "required": True,
            }
        ],
        "domain_weaver_spawn_dispatch": {
            "source_spawn_request_path": "ION/05_context/current/domain_weaver/workers/babbage/context/spawn_requests/context.spawn_request.json",
            "worker_return_is_carrier_intake_only": True,
            "actual_spawn_performed": False,
            "codex_queue_run_started": False,
        },
    }

    result = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", args)

    assert result["ok"] is True
    packet = json.loads((tmp_path / result["data"]["packet_path"]).read_text(encoding="utf-8"))
    assert packet["domain_id"] == "domain.agent_communication_systems"
    assert packet["agent_role_id"] == "role.context_cartographer"
    assert packet["agent_role"] == "role.context_cartographer"
    assert packet["role_tier"] == "specialist"
    assert packet["callsign"] == "Lovelace"
    assert packet["true_name"] == "Ada Lovelace"
    assert packet["domain_context_package"] == (
        "ION/05_context/current/domain_weaver/.ion/ACTIVE_CONTEXT_PACKAGE.md"
    )
    assert packet["planned_writes"] == [
        "ION/05_context/current/domain_weaver/workers/lovelace/context/candidates/result.candidate.json"
    ]
    assert packet["required_context_reads"][0]["path"] == (
        "ION/05_context/current/domain_weaver/AGENTS.md"
    )
    assert packet["domain_weaver_spawn_dispatch"]["worker_return_is_carrier_intake_only"] is True
    assert packet["domain_weaver_spawn_dispatch"]["actual_spawn_performed"] is False
    assert packet["domain_weaver_spawn_dispatch"]["codex_queue_run_started"] is False


def test_codex_work_packet_request_infers_ai_movement_target_from_planned_path(tmp_path):
    _seed_root(tmp_path)
    args = {
        "objective": "Patch product projection docs.",
        "work_class": "general_codex_work",
        "risk_level": "low",
        "route_family": "general_codex_work",
        "planned_writes": ["ION_GPT/01_GPT_BUILDER_INPUTS/README.md"],
    }

    result = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", args)

    assert result["ok"] is True
    packet = json.loads((tmp_path / result["data"]["packet_path"]).read_text(encoding="utf-8"))
    assert packet["target_root_id"] == "ion_gpt"
    assert packet["movement_class"] == "CUSTOM_GPT_RELEASE_MOVEMENT"
    assert packet["ai_movement_request_template"]["binding_source"] == "request.planned_writes"


def test_codex_work_packet_request_implicit_objective_dedupe_catches_no_receipt_retry(tmp_path):
    _seed_root(tmp_path)
    args = {
        "objective": "Operator retries same objective after no receipt from carrier",
    }

    first = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", args)
    second = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", args)
    forced = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", {**args, "force_new": True})
    queue = call_chatgpt_connector_tool(tmp_path, "ion_codex_work_queue", {"limit": 10})

    assert first["ok"] is True
    assert first["data"]["implicit_idempotency_key"] is True
    assert second["ok"] is True
    assert second["mutates_active_state"] is False
    assert second["data"]["idempotent_replay"] is True
    assert second["data"]["packet_path"] == first["data"]["packet_path"]
    assert forced["ok"] is True
    assert forced["data"]["idempotent_replay"] is False
    assert forced["data"]["packet_path"] != first["data"]["packet_path"]
    assert queue["data"]["request_count"] == 2
    assert queue["data"]["duplicate_group_count"] == 1


def test_codex_queue_duplicate_audit_and_supersede_preserves_packets(tmp_path):
    _seed_root(tmp_path)
    args = {"objective": "B00 duplicated packet family for cleanup"}
    first = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", args)
    second = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", {**args, "force_new": True})
    third = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", {**args, "force_new": True})

    audit = call_chatgpt_connector_tool(tmp_path, "ion_codex_queue_duplicate_audit", {"limit": 10})

    assert first["ok"] is True
    assert second["ok"] is True
    assert third["ok"] is True
    assert audit["ok"] is True
    assert audit["data"]["duplicate_group_count"] == 1
    assert audit["data"]["duplicate_request_count"] == 2
    group = audit["data"]["groups"][0]
    assert group["canonical_request_id"] == first["data"]["request_id"]

    cleanup = call_chatgpt_connector_tool(
        tmp_path,
        "ion_codex_queue_supersede_duplicates",
        {
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key": "cleanup-b00-duplicates-001",
            "all_duplicates": True,
            "reason": "test duplicate cleanup",
        },
    )
    replay = call_chatgpt_connector_tool(
        tmp_path,
        "ion_codex_queue_supersede_duplicates",
        {
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key": "cleanup-b00-duplicates-001",
            "all_duplicates": True,
            "reason": "test duplicate cleanup",
        },
    )

    assert cleanup["ok"] is True
    assert cleanup["mutates_active_state"] is True
    assert cleanup["data"]["status"] == "DUPLICATES_SUPERSEDED_NOT_DELETED"
    assert cleanup["data"]["superseded_count"] == 2
    assert (tmp_path / cleanup["data"]["receipt_path"]).exists()
    assert replay["ok"] is True
    assert replay["mutates_active_state"] is False
    assert replay["data"]["idempotent_replay"] is True
    assert replay["data"]["duplicate_prevented"] is True
    assert replay["data"]["receipt_path"] == cleanup["data"]["receipt_path"]

    request_files = list((tmp_path / "ION/05_context/current/chatgpt_connector/codex_work_requests").glob("*.json"))
    assert len(request_files) == 3
    statuses = {json.loads(path.read_text(encoding="utf-8"))["request_id"]: json.loads(path.read_text(encoding="utf-8"))["status"] for path in request_files}
    assert statuses[first["data"]["request_id"]] == "QUEUED_FOR_CODEX_CARRIER"
    assert statuses[second["data"]["request_id"]] == "SUPERSEDED_DUPLICATE"
    assert statuses[third["data"]["request_id"]] == "SUPERSEDED_DUPLICATE"


def test_codex_queue_duplicate_audit_defaults_compact_and_full_is_opt_in(tmp_path):
    _seed_root(tmp_path)
    objective = "compact audit should suppress this objective text by default"
    args = {"objective": objective}
    first = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", args)
    second = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", {**args, "force_new": True})

    compact = call_chatgpt_connector_tool(tmp_path, "ion_codex_queue_duplicate_audit", {"limit": 10})
    assert first["ok"] is True
    assert second["ok"] is True
    assert compact["ok"] is True
    assert compact["data"]["response_mode"] == "compact"
    assert compact["data"]["include_duplicates"] is False
    compact_group = compact["data"]["groups"][0]
    assert compact_group["duplicate_count"] == 1
    assert compact_group["group_count"] == 2
    assert compact_group["canonical_request_id"] == first["data"]["request_id"]
    assert compact_group["duplicates_returned_count"] == 0
    assert compact_group["duplicates"] == []
    assert compact_group["duplicates_truncated"] is True
    assert "requests" not in compact_group
    canonical = compact_group["canonical_request"]
    assert isinstance(canonical["objective_sha256"], str)
    assert len(canonical["objective_sha256"]) == 64
    assert "objective" not in canonical
    assert "payload" not in canonical


def test_codex_queue_duplicate_audit_include_duplicates_respects_sample_bound(tmp_path):
    _seed_root(tmp_path)
    args = {"objective": "compact audit duplicate sample bound"}
    first = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", args)
    second = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", {**args, "force_new": True})
    third = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", {**args, "force_new": True})
    fourth = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", {**args, "force_new": True})
    assert all(result["ok"] is True for result in (first, second, third, fourth))

    compact_with_duplicates = call_chatgpt_connector_tool(
        tmp_path,
        "ion_codex_queue_duplicate_audit",
        {"limit": 10, "include_duplicates": True, "max_duplicates_per_group": 2},
    )

    assert compact_with_duplicates["ok"] is True
    assert compact_with_duplicates["data"]["response_mode"] == "compact"
    assert compact_with_duplicates["data"]["include_duplicates"] is True
    assert compact_with_duplicates["data"]["max_duplicates_per_group"] == 2
    group = compact_with_duplicates["data"]["groups"][0]
    assert group["group_count"] == 4
    assert group["duplicate_count"] == 3
    assert group["duplicates_returned_count"] == 2
    assert len(group["duplicates"]) == 2
    assert group["duplicates_truncated"] is True
    assert "requests" not in group
    for row in group["duplicates"]:
        assert row["duplicate_of_request_id"] == first["data"]["request_id"]
        assert row["request_id"] != first["data"]["request_id"]
        assert "objective" not in row
        assert "payload" not in row


def test_codex_queue_duplicate_audit_full_modes_respect_limit_and_only_return_canonical_request(tmp_path):
    _seed_root(tmp_path)
    args = {"objective": "full audit duplicate sample bound"}
    first = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", args)
    second = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", {**args, "force_new": True})
    third = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", {**args, "force_new": True})
    fourth = call_chatgpt_connector_tool(tmp_path, "ion_request_codex_work_packet", {**args, "force_new": True})
    assert all(result["ok"] is True for result in (first, second, third, fourth))

    full_args_variants = (
        {"limit": 10, "include_full": True, "max_duplicates_per_group": 2},
        {"limit": 10, "full": True, "max_duplicates_per_group": 2},
        {"limit": 10, "include_packets": True, "max_duplicates_per_group": 2},
    )
    for full_args in full_args_variants:
        full_response = call_chatgpt_connector_tool(
            tmp_path,
            "ion_codex_queue_duplicate_audit",
            full_args,
        )
        assert full_response["ok"] is True
        assert full_response["data"]["response_mode"] == "full"
        group = full_response["data"]["groups"][0]
        assert group["group_count"] == 4
        assert group["duplicate_count"] == 3
        assert group["duplicates_returned_count"] == 2
        assert len(group["duplicates"]) == 2
        assert group["duplicates_truncated"] is True
        assert len(group["requests"]) == 1
        assert group["requests"][0]["request_id"] == first["data"]["request_id"]
        assert group["requests"][0]["objective"] == args["objective"]
        assert all("payload" not in row for row in group["requests"])
        for row in group["duplicates"]:
            assert row["duplicate_of_request_id"] == first["data"]["request_id"]
            assert row["request_id"] != first["data"]["request_id"]
            assert row["objective"] == args["objective"]
            assert "payload" not in row


def test_codex_queue_supersede_duplicates_requires_confirmation_and_idempotency(tmp_path):
    _seed_root(tmp_path)
    no_confirmation = call_chatgpt_connector_tool(
        tmp_path,
        "ion_codex_queue_supersede_duplicates",
        {"idempotency_key": "missing-confirmation", "all_duplicates": True},
    )
    no_key = call_chatgpt_connector_tool(
        tmp_path,
        "ion_codex_queue_supersede_duplicates",
        {"confirmation": "ION_BOUNDED_WRITE_CONFIRMED", "all_duplicates": True},
    )

    assert no_confirmation["ok"] is False
    assert no_confirmation["finding"] == "confirmation_required"
    assert no_key["ok"] is False
    assert no_key["finding"] == "idempotency_key_required"


def test_task_return_requires_context_and_template_action_proof(tmp_path):
    _seed_root(tmp_path)
    receipt = {
        "schema_id": "ion.context_load_receipt.v1",
        "required_context_reads": [
            {"kind": "file", "path": "ION/REPO_AUTHORITY.md", "required": True}
        ],
    }
    missing_template = """### CONTEXT PROOF
- ION/REPO_AUTHORITY.md excerpt: authority line read.

### RESULT
No template proof.
"""
    valid = """### CONTEXT PROOF
path: ION/REPO_AUTHORITY.md
sha256: testhash
excerpt: "authority line read."

### TEMPLATE ACTION PROOF
template_id: ion.template.patch_proposal.v1
action_id: v120-chatgpt-connector-test
result: validated bounded connector return
touched_paths:
  - ION/docs/setup/CHATGPT_BROWSER_MCP_CONNECTOR_SETUP_V120.md

### VALIDATION
- unit test

### RESULT
Validated.

### WORKLOAD DIFF
- ION/docs/setup/CHATGPT_BROWSER_MCP_CONNECTOR_SETUP_V120.md

### BLOCKERS
- none

### RECOMMENDED NEXT PACKET
NEXT_PACKET_EXAMPLE
"""

    blocked = call_chatgpt_connector_tool(
        tmp_path,
        "ion_submit_task_return",
        {"task_output_text": missing_template, "context_receipt": receipt},
    )
    accepted = call_chatgpt_connector_tool(
        tmp_path,
        "ion_submit_task_return",
        {"task_output_text": valid, "context_receipt": receipt},
    )

    assert blocked["ok"] is True
    assert blocked["data"]["accepted_for_carrier_intake"] is False
    assert blocked["data"]["context_proof_accepted"] is True
    assert blocked["data"]["template_action_proof_accepted"] is False
    assert accepted["ok"] is True
    assert accepted["data"]["accepted_for_carrier_intake"] is True
    packet = tmp_path / accepted["data"]["packet_path"]
    assert packet.exists()
    assert "RECORDED_FOR_CARRIER_INTAKE" in packet.read_text(encoding="utf-8")


def test_task_return_separates_context_proof_failure_from_template_invalid(tmp_path):
    _seed_root(tmp_path)
    receipt = {
        "schema_id": "ion.context_load_receipt.v1",
        "required_context_reads": [
            {"kind": "file", "path": "ION/REPO_AUTHORITY.md", "required": True}
        ],
    }
    context_missing_but_template_valid = """### CONTEXT PROOF
Context was discussed, but this block intentionally omits the required path and machine evidence.

### TEMPLATE ACTION PROOF
template_id: ion.template.patch_proposal.v1
action_id: context-proof-separation-test
result: designed
touched_paths:
  - ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py

### VALIDATION
- not run

### RESULT
Useful design return content exists, but context proof is missing.

### WORKLOAD DIFF
- ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py

### BLOCKERS
- context proof omitted for regression coverage

### RECOMMENDED NEXT PACKET
Repair context proof only.
"""

    blocked = call_chatgpt_connector_tool(
        tmp_path,
        "ion_submit_task_return",
        {"task_output_text": context_missing_but_template_valid, "context_receipt": receipt},
    )

    assert blocked["ok"] is True
    assert blocked["data"]["accepted_for_carrier_intake"] is False
    assert blocked["data"]["return_template_valid"] is True
    assert blocked["data"]["context_proof_accepted"] is False
    assert blocked["data"]["template_action_proof_accepted"] is True
    assert blocked["data"]["carrier_intake_state"] == "template_action_proof_ok_context_failed"
    assert blocked["data"]["carrier_intake_only"] is True
    assert blocked["data"]["product_state_accepted"] is False
    packet = json.loads((tmp_path / blocked["data"]["packet_path"]).read_text(encoding="utf-8"))
    receipt_payload = json.loads((tmp_path / blocked["data"]["machine_receipt_path"]).read_text(encoding="utf-8"))
    assert packet["result"] == "BLOCKED_BY_PROOF_GATE"
    assert packet["carrier_intake_state"] == "template_action_proof_ok_context_failed"
    assert receipt_payload["carrier_intake_state"] == "template_action_proof_ok_context_failed"
    assert receipt_payload["product_state_accepted"] is False


def test_task_return_accepts_compact_receipt_table_context_evidence(tmp_path):
    _seed_root(tmp_path)
    hash_value = "a" * 64
    receipt = {
        "schema_id": "ion.context_load_receipt.v1",
        "required_context_reads": [
            {"kind": "file", "path": "ION/REPO_AUTHORITY.md", "required": True}
        ],
    }
    valid = f"""### CONTEXT PROOF
All required context paths were opened directly; receipt line evidence follows.
path | hash | excerpt
ION/REPO_AUTHORITY.md | {hash_value} | canonical root authority was opened from disk

### TEMPLATE ACTION PROOF
template_id: ion.template.patch_proposal.v1
action_id: compact-receipt-table-context-evidence-test
result: validated compact receipt table context evidence
touched_paths:
  - ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py

### VALIDATION
- unit test

### RESULT
Validated.

### WORKLOAD DIFF
- ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py

### BLOCKERS
- none

### RECOMMENDED NEXT PACKET
NEXT_PACKET_EXAMPLE
"""

    accepted = call_chatgpt_connector_tool(
        tmp_path,
        "ion_submit_task_return",
        {"task_output_text": valid, "context_receipt": receipt},
    )

    assert accepted["ok"] is True
    assert accepted["data"]["accepted_for_carrier_intake"] is True
    assert accepted["data"]["return_template_valid"] is True
    assert accepted["data"]["context_proof_accepted"] is True
    machine_receipt = json.loads((tmp_path / accepted["data"]["machine_receipt_path"]).read_text(encoding="utf-8"))
    packet = json.loads((tmp_path / accepted["data"]["packet_path"]).read_text(encoding="utf-8"))
    assert machine_receipt["receipt_source"] == "automation"
    assert machine_receipt["manual_ai_authored"] is False
    assert machine_receipt["diagnosis"]["classification"] == "carrier_intake_ready"
    assert packet["machine_receipt_path"] == accepted["data"]["machine_receipt_path"]
    assert packet["manual_ai_receipt_required"] is False


def test_alternate_worker_return_rejects_relay_or_bridge_identity(tmp_path):
    import hashlib

    _seed_root(tmp_path)
    request_rel = "ION/05_context/current/chatgpt_connector/codex_work_requests/alternate_worker_rejects_relay.json"
    request_path = tmp_path / request_rel
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": "codex_req_alternate_worker_rejects_relay",
                "objective": "Alternate worker return lane rejection smoke",
                "status": "RETURN_RECORDED_PROOF_BLOCKED",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    receipt = {
        "schema_id": "ion.context_load_receipt.v1",
        "required_context_reads": [
            {"kind": "file", "path": "ION/REPO_AUTHORITY.md", "required": True}
        ],
    }
    valid = """### CONTEXT PROOF
path: ION/REPO_AUTHORITY.md
sha256: testhash
excerpt: "authority line read."

### TEMPLATE ACTION PROOF
template_id: ion.template.autonomous_loop.local_worker.v1
action_id: alternate-worker-rejects-relay-test
result: validated relay identities cannot submit worker returns
touched_paths:
  - ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py

### VALIDATION
- unit test

### RESULT
Validated.

### WORKLOAD DIFF
- ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py

### BLOCKERS
- none

### RECOMMENDED NEXT PACKET
NEXT_PACKET_EXAMPLE
"""
    relay_identity = {
        "worker_id": "role.codex_carrier_steward",
        "worker_role": "parent_session_relay",
        "worker_runtime": "codex_parent_session",
        "origin": "parent_session_relay",
        "source_ref": "carrier_session_bridge:codex_carrier_bridge_demo",
    }
    provenance = {
        "source_kind": "multi_agent_v1",
        "source_ref": relay_identity["source_ref"],
        "observed_by": "lead_codex",
        "work_request_path": request_rel,
        "worker_id": relay_identity["worker_id"],
        "worker_output_sha256": hashlib.sha256(valid.encode("utf-8")).hexdigest(),
        "claim_boundary": "carrier_intake_not_product_state",
    }

    missing_confirmation = call_chatgpt_connector_tool(
        tmp_path,
        "ion_submit_alternate_worker_return",
        {
            "task_output_text": valid,
            "context_receipt": receipt,
            "work_request_path": request_rel,
            "alternate_worker_identity": relay_identity,
            "alternate_worker_provenance": provenance,
        },
    )
    forbidden_identity = call_chatgpt_connector_tool(
        tmp_path,
        "ion_submit_alternate_worker_return",
        {
            "task_output_text": valid,
            "context_receipt": receipt,
            "work_request_path": request_rel,
            "confirmation": "ION_ALTERNATE_WORKER_RETURN_CONFIRMED",
            "alternate_worker_identity": relay_identity,
            "alternate_worker_provenance": provenance,
        },
    )

    assert missing_confirmation["ok"] is False
    assert missing_confirmation["finding"] == "alternate_worker_return_confirmation_required"
    assert forbidden_identity["ok"] is False
    assert forbidden_identity["finding"].startswith("alternate_worker_identity_forbidden_source_class:")
    updated_request = json.loads(request_path.read_text(encoding="utf-8"))
    assert "latest_return_packet_path" not in updated_request


def test_alternate_worker_return_records_source_contract_without_product_state(tmp_path):
    import hashlib
    from kernel.ion_chatgpt_browser_mcp_connector_contract import tool_descriptors

    _seed_root(tmp_path)
    request_rel = "ION/05_context/current/chatgpt_connector/codex_work_requests/alternate_worker_records_source.json"
    request_path = tmp_path / request_rel
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": "codex_req_alternate_worker_records_source",
                "objective": "Alternate worker return lane accepted carrier intake smoke",
                "status": "RETURN_RECORDED_PROOF_BLOCKED",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    receipt = {
        "schema_id": "ion.context_load_receipt.v1",
        "required_context_reads": [
            {"kind": "file", "path": "ION/REPO_AUTHORITY.md", "required": True}
        ],
    }
    valid = """### CONTEXT PROOF
path: ION/REPO_AUTHORITY.md
sha256: testhash
excerpt: "authority line read."

### TEMPLATE ACTION PROOF
template_id: ion.template.autonomous_loop.local_worker.v1
action_id: alternate-worker-source-contract-test
result: validated alternate worker source contract
touched_paths:
  - ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py

### VALIDATION
- unit test

### RESULT
Validated.

### WORKLOAD DIFF
- ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py

### BLOCKERS
- none

### RECOMMENDED NEXT PACKET
NEXT_PACKET_EXAMPLE
"""
    worker_identity = {
        "worker_id": "agent.curie.alternate_return_lane_scout",
        "worker_role": "role.context_cartographer",
        "worker_runtime": "multi_agent_v1",
        "origin": "codex_subagent",
        "source_ref": "subagent:019e90b9-6a90-70b1-9a9f-554698898512",
        "domain_id": "domain.domain_weaver",
        "task_contract_id": "PCKT-DOMAIN-WEAVER-ALTERNATE-WORKER-RETURN-LANE-V0_1",
    }
    provenance = {
        "source_kind": "multi_agent_v1",
        "source_ref": worker_identity["source_ref"],
        "observed_by": "lead_codex",
        "work_request_path": request_rel,
        "worker_id": worker_identity["worker_id"],
        "worker_output_sha256": hashlib.sha256(valid.encode("utf-8")).hexdigest(),
        "claim_boundary": "carrier_intake_not_product_state",
    }
    native_transcript_receipt = call_chatgpt_connector_tool(
        tmp_path,
        "ion_record_native_subagent_transcript",
        {
            "confirmation": "ION_NATIVE_SUBAGENT_TRANSCRIPT_CONFIRMED",
            "idempotency_key": "alternate-worker-native-transcript-test",
            "subagent_id": "019e90b9-6a90-70b1-9a9f-554698898512",
            "worker_id": worker_identity["worker_id"],
            "source_ref": worker_identity["source_ref"],
            "work_request_path": request_rel,
            "status": "completed",
            "worker_output_text": valid,
            "observed_by": "lead_codex_test",
            "claim_boundary": "carrier_intake_not_product_state",
        },
    )
    provenance_receipt = call_chatgpt_connector_tool(
        tmp_path,
        "ion_record_alternate_worker_provenance",
        {
            "confirmation": "ION_ALTERNATE_WORKER_PROVENANCE_CONFIRMED",
            "idempotency_key": "alternate-worker-source-contract-test",
            "alternate_worker_identity": worker_identity,
            "alternate_worker_provenance": provenance,
            "worker_output_sha256": provenance["worker_output_sha256"],
            "native_subagent_transcript_receipt_path": native_transcript_receipt["data"]["receipt_path"],
        },
    )

    descriptor = next(row for row in tool_descriptors() if row["name"] == "ion_submit_alternate_worker_return")
    generic_blocked = call_chatgpt_connector_tool(
        tmp_path,
        "ion_submit_task_return",
        {
            "task_output_text": valid,
            "context_receipt": receipt,
            "work_request_path": request_rel,
            "alternate_worker_return": True,
            "confirmation": "ION_ALTERNATE_WORKER_RETURN_CONFIRMED",
            "alternate_worker_identity": worker_identity,
            "alternate_worker_provenance": provenance,
        },
    )
    bad_provenance = dict(provenance)
    bad_provenance["worker_output_sha256"] = "b" * 64
    provenance_blocked = call_chatgpt_connector_tool(
        tmp_path,
        "ion_submit_alternate_worker_return",
        {
            "task_output_text": valid,
            "context_receipt": receipt,
            "work_request_path": request_rel,
            "confirmation": "ION_ALTERNATE_WORKER_RETURN_CONFIRMED",
            "alternate_worker_identity": worker_identity,
            "alternate_worker_provenance": bad_provenance,
        },
    )
    missing_receipt_blocked = call_chatgpt_connector_tool(
        tmp_path,
        "ion_submit_alternate_worker_return",
        {
            "task_output_text": valid,
            "context_receipt": receipt,
            "work_request_path": request_rel,
            "confirmation": "ION_ALTERNATE_WORKER_RETURN_CONFIRMED",
            "alternate_worker_identity": worker_identity,
            "alternate_worker_provenance": provenance,
            "require_provenance_receipt": True,
        },
    )
    accepted = call_chatgpt_connector_tool(
        tmp_path,
        "ion_submit_alternate_worker_return",
        {
            "task_output_text": valid,
            "context_receipt": receipt,
            "work_request_path": request_rel,
            "confirmation": "ION_ALTERNATE_WORKER_RETURN_CONFIRMED",
            "alternate_worker_identity": worker_identity,
            "alternate_worker_provenance": provenance,
            "alternate_worker_provenance_receipt_path": provenance_receipt["data"]["receipt_path"],
            "require_provenance_receipt": True,
        },
    )
    duplicate = call_chatgpt_connector_tool(
        tmp_path,
        "ion_submit_alternate_worker_return",
        {
            "task_output_text": valid,
            "context_receipt": receipt,
            "work_request_path": request_rel,
            "confirmation": "ION_ALTERNATE_WORKER_RETURN_CONFIRMED",
            "alternate_worker_identity": worker_identity,
            "alternate_worker_provenance": provenance,
            "alternate_worker_provenance_receipt_path": provenance_receipt["data"]["receipt_path"],
            "require_provenance_receipt": True,
        },
    )
    other_identity = dict(worker_identity)
    other_identity["worker_id"] = "agent.lovelace.alternate_return_lane_peer"
    other_identity["source_ref"] = "subagent:019e90be-different"
    other_provenance = dict(provenance)
    other_provenance["worker_id"] = other_identity["worker_id"]
    other_provenance["source_ref"] = other_identity["source_ref"]
    other_provenance_receipt = call_chatgpt_connector_tool(
        tmp_path,
        "ion_record_alternate_worker_provenance",
        {
            "confirmation": "ION_ALTERNATE_WORKER_PROVENANCE_CONFIRMED",
            "idempotency_key": "alternate-worker-source-contract-test-other",
            "alternate_worker_identity": other_identity,
            "alternate_worker_provenance": other_provenance,
            "worker_output_sha256": other_provenance["worker_output_sha256"],
        },
    )
    other_accepted = call_chatgpt_connector_tool(
        tmp_path,
        "ion_submit_alternate_worker_return",
        {
            "task_output_text": valid,
            "context_receipt": receipt,
            "work_request_path": request_rel,
            "confirmation": "ION_ALTERNATE_WORKER_RETURN_CONFIRMED",
            "alternate_worker_identity": other_identity,
            "alternate_worker_provenance": other_provenance,
            "alternate_worker_provenance_receipt_path": other_provenance_receipt["data"]["receipt_path"],
            "require_provenance_receipt": True,
        },
    )

    assert provenance_receipt["ok"] is True
    assert native_transcript_receipt["ok"] is True
    assert native_transcript_receipt["data"]["native_subagent_transcript_verified"] is True
    assert provenance_receipt["data"]["verification_scope"] == "durable_parent_observed_subagent_provenance_receipt"
    assert provenance_receipt["data"]["native_subagent_transcript_verified"] is True
    assert descriptor["requires_context_proof"] is True
    assert descriptor["requires_template_action_proof"] is True
    assert generic_blocked["ok"] is False
    assert generic_blocked["finding"] == "alternate_worker_return_requires_dedicated_tool"
    assert provenance_blocked["ok"] is False
    assert provenance_blocked["finding"] == "alternate_worker_provenance_worker_output_sha256_mismatch"
    assert missing_receipt_blocked["ok"] is False
    assert missing_receipt_blocked["finding"] == "alternate_worker_provenance_receipt_required"
    assert accepted["ok"] is True
    assert accepted["data"]["accepted_for_carrier_intake"] is True
    assert accepted["data"]["carrier_intake_only"] is True
    assert accepted["data"]["product_state_accepted"] is False
    assert accepted["data"]["return_lane"] == "alternate_worker_return"
    assert accepted["data"]["alternate_worker_return"] is True
    assert duplicate["ok"] is True
    assert duplicate["data"]["deduped_existing_return"] is True
    assert other_accepted["ok"] is True
    assert other_accepted["data"]["packet_path"] != accepted["data"]["packet_path"]
    packet = json.loads((tmp_path / accepted["data"]["packet_path"]).read_text(encoding="utf-8"))
    machine_receipt = json.loads((tmp_path / accepted["data"]["machine_receipt_path"]).read_text(encoding="utf-8"))
    updated_request = json.loads(request_path.read_text(encoding="utf-8"))
    assert packet["return_source_contract"]["identity"]["worker_id"] == worker_identity["worker_id"]
    assert packet["return_source_contract"]["provenance"]["worker_output_sha256"] == provenance["worker_output_sha256"]
    assert packet["return_source_contract"]["provenance_verification_state"] == "durable_receipt_verified"
    assert packet["return_source_contract"]["native_subagent_transcript_verified"] is True
    assert packet["return_source_contract"]["native_subagent_transcript_receipt_path"] == native_transcript_receipt["data"]["receipt_path"]
    assert packet["worker_identity_sha256"] == accepted["data"]["worker_identity_sha256"]
    assert packet["parent_session_relay_is_worker_return"] is False
    assert packet["failed_cli_log_is_worker_return"] is False
    assert packet["carrier_session_bridge_is_worker_return"] is False
    assert machine_receipt["return_lane"] == "alternate_worker_return"
    assert machine_receipt["return_source_contract"]["identity_sha256"] == accepted["data"]["worker_identity_sha256"]
    assert updated_request["status"] == "RETURN_RECORDED_PROOF_ACCEPTED"
    assert updated_request["latest_task_return_lane"] == "alternate_worker_return"
    assert updated_request["latest_task_return_product_state_accepted"] is False
    assert updated_request["latest_task_return_source_contract"]["identity"]["source_ref"] == other_identity["source_ref"]


def test_accepted_task_return_clears_stale_failure_classification(tmp_path):
    _seed_root(tmp_path)
    request_rel = "ION/05_context/current/chatgpt_connector/codex_work_requests/stale_failure.json"
    request_path = tmp_path / request_rel
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": "codex_req_stale_failure",
                "objective": "Settle repaired task return",
                "status": "RETURN_TEMPLATE_INVALID",
                "failure_classification": "BACKEND_CODEX_FAILURE",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    receipt = {
        "schema_id": "ion.context_load_receipt.v1",
        "required_context_reads": [
            {"kind": "file", "path": "ION/REPO_AUTHORITY.md", "required": True}
        ],
    }
    valid = """### CONTEXT PROOF
path: ION/REPO_AUTHORITY.md
sha256: testhash
excerpt: "authority line read."

### TEMPLATE ACTION PROOF
template_id: ion.template.patch_proposal.v1
action_id: stale-failure-clear-test
result: validated accepted return clears stale failure metadata
touched_paths:
  - ION/05_context/current/chatgpt_connector/codex_work_requests/stale_failure.json

### VALIDATION
- unit test

### RESULT
Validated.

### WORKLOAD DIFF
- ION/05_context/current/chatgpt_connector/codex_work_requests/stale_failure.json

### BLOCKERS
- none

### RECOMMENDED NEXT PACKET
NEXT_PACKET_EXAMPLE
"""

    accepted = call_chatgpt_connector_tool(
        tmp_path,
        "ion_submit_task_return",
        {"task_output_text": valid, "context_receipt": receipt, "work_request_path": request_rel},
    )

    assert accepted["ok"] is True
    assert accepted["data"]["accepted_for_carrier_intake"] is True
    updated_request = json.loads(request_path.read_text(encoding="utf-8"))
    assert updated_request["status"] == "RETURN_RECORDED_PROOF_ACCEPTED"
    assert "failure_classification" not in updated_request


def test_accepted_task_return_updates_working_capsule_maintenance_after_proof(tmp_path):
    _seed_root(tmp_path)
    capsule_cwd = tmp_path / "ION/05_context/current/codex_agent_mounts/role_demo__domain_demo"
    request_rel = "ION/05_context/current/chatgpt_connector/codex_work_requests/working_capsule.json"
    request_path = tmp_path / request_rel
    request_path.parent.mkdir(parents=True, exist_ok=True)
    identity = {
        "instance_capsule_id": "wcaps_demo_task_return",
        "domain_id": "domain.demo",
        "role_id": "role.demo",
        "carrier_instance_id": "codex_session_demo",
        "parent_capsule_ref": "parent_wcaps_demo",
        "lineage_id": "lineage_demo",
        "cwd": capsule_cwd.as_posix(),
        "root": tmp_path.as_posix(),
        "working_capsule_path": (capsule_cwd / ".ion").as_posix(),
        "codex_agent_mount": capsule_cwd.as_posix(),
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
    }
    request_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": "codex_req_working_capsule",
                "objective": "Generated domain-agent instance capsule repair",
                "status": "QUEUED_FOR_CODEX_CARRIER",
                "work_class": "active_root_repair",
                "working_capsule_identity": identity,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    receipt = {
        "schema_id": "ion.context_load_receipt.v1",
        "required_context_reads": [
            {"kind": "file", "path": "ION/REPO_AUTHORITY.md", "required": True}
        ],
    }
    valid = """### CONTEXT PROOF
path: ION/REPO_AUTHORITY.md
sha256: testhash
excerpt: "authority line read."

### TEMPLATE ACTION PROOF
template_id: ion.template.patch_proposal.v1
action_id: working-capsule-maintenance-test
result: validated accepted return maintains local capsule
touched_paths:
  - ION/05_context/current/chatgpt_connector/codex_work_requests/working_capsule.json

### VALIDATION
- unit test

### RESULT
Validated.

### WORKLOAD DIFF
- ION/05_context/current/chatgpt_connector/codex_work_requests/working_capsule.json

### BLOCKERS
- none

### RECOMMENDED NEXT PACKET
NEXT_PACKET_EXAMPLE
"""

    accepted = call_chatgpt_connector_tool(
        tmp_path,
        "ion_submit_task_return",
        {"task_output_text": valid, "context_receipt": receipt, "work_request_path": request_rel},
    )

    assert accepted["ok"] is True
    assert accepted["data"]["accepted_for_carrier_intake"] is True
    assert accepted["data"]["working_capsule_update"]["maintenance_attempted"] is True
    updated_request = json.loads(request_path.read_text(encoding="utf-8"))
    assert updated_request["latest_working_capsule_preflight"]["classification"] == "identity_ready"
    maintenance = updated_request["latest_working_capsule_maintenance"]
    assert maintenance["ok"] is True
    assert (capsule_cwd / ".ion/CAPSULE.md").is_file()
    assert (capsule_cwd / ".ion/MINI.md").is_file()
    assert (capsule_cwd / ".ion/HOT_CONTEXT.md").is_file()
    assert (tmp_path / maintenance["receipt_path"]).is_file()


def test_task_return_requires_workload_diff_when_request_contract_declares_it(tmp_path):
    _seed_root(tmp_path)
    request_rel = "ION/05_context/current/chatgpt_connector/codex_work_requests/workload_diff_required.json"
    request_path = tmp_path / request_rel
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": "codex_req_workload_diff_required",
                "objective": "Agent cartography proof run",
                "requested_by": "ion_agent_invocation_broker",
                "status": "QUEUED_FOR_CODEX_CARRIER",
                "return_contract_sections": [
                    "### CONTEXT PROOF",
                    "### TEMPLATE ACTION PROOF",
                    "### VALIDATION",
                    "### RESULT",
                    "### WORKLOAD DIFF",
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    receipt = {
        "schema_id": "ion.context_load_receipt.v1",
        "required_context_reads": [
            {"kind": "file", "path": "ION/REPO_AUTHORITY.md", "required": True}
        ],
    }
    missing_workload_diff = """### CONTEXT PROOF
- ION/REPO_AUTHORITY.md excerpt: authority line read.

### TEMPLATE ACTION PROOF
template_id: ion.template.autonomous_loop.local_worker.v1
action_id: workload-diff-required-test
result: tested required workload diff contract
touched_paths:
  - ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py

### VALIDATION
commands_run:
  - pytest targeted

### RESULT
Missing workload diff section.
"""

    blocked = call_chatgpt_connector_tool(
        tmp_path,
        "ion_submit_task_return",
        {
            "task_output_text": missing_workload_diff,
            "context_receipt": receipt,
            "work_request_path": request_rel,
        },
    )

    assert blocked["ok"] is True
    assert blocked["data"]["accepted_for_carrier_intake"] is False
    assert blocked["data"]["workload_diff_required"] is True
    assert blocked["data"]["workload_diff_present"] is False
    assert "missing_required_section:### WORKLOAD DIFF" in blocked["data"]["findings"]
    machine_receipt = json.loads((tmp_path / blocked["data"]["machine_receipt_path"]).read_text(encoding="utf-8"))
    updated_request = json.loads(request_path.read_text(encoding="utf-8"))
    assert machine_receipt["receipt_source"] == "automation"
    assert machine_receipt["manual_ai_authored"] is False
    assert machine_receipt["diagnosis"]["classification"] == "workload_diff_gate_blocked"
    assert updated_request["latest_task_return_machine_receipt_path"] == blocked["data"]["machine_receipt_path"]
    queue = call_chatgpt_connector_tool(tmp_path, "ion_codex_work_queue", {"limit": 10})
    request_row = queue["data"]["requests"][0]
    assert request_row["settlement_relevant_machine_receipt_path"] == blocked["data"]["machine_receipt_path"]
    assert request_row["settlement_relevant_automation_diagnosis"]["classification"] == "workload_diff_gate_blocked"


def test_task_return_requires_ion_operational_posture_when_request_declares_it(tmp_path):
    _seed_root(tmp_path)
    request_rel = "ION/05_context/current/chatgpt_connector/codex_work_requests/operational_posture_required.json"
    request_path = tmp_path / request_rel
    request_path.parent.mkdir(parents=True, exist_ok=True)
    request_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": "codex_req_operational_posture_required",
                "objective": "Red alert Codex carrier mount repair",
                "status": "QUEUED_FOR_CODEX_CARRIER",
                "ion_operational_posture_required": True,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    receipt = {
        "schema_id": "ion.context_load_receipt.v1",
        "required_context_reads": [
            {"kind": "file", "path": "ION/REPO_AUTHORITY.md", "required": True}
        ],
    }
    base = """### CONTEXT PROOF
path: ION/REPO_AUTHORITY.md
sha256: testhash
excerpt: "authority line read."

### TEMPLATE ACTION PROOF
template_id: ion.template.patch_proposal.v1
action_id: operational-posture-required-test
result: validated bounded connector return
touched_paths:
  - ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py

### VALIDATION
- unit test

### RESULT
Validated.

### WORKLOAD DIFF
- ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py

### BLOCKERS
- none

### RECOMMENDED NEXT PACKET
NEXT_PACKET_EXAMPLE
"""
    with_posture = base + """
### ION OPERATIONAL POSTURE
ion_operational_state: `ION_CODEX_OPERATIONAL_READY`
mount_truth_state: `CODEX_CARRIER_LOCAL_MOUNT_READY`
role_phase_sequence: `PERSONA_INTERFACE_INGRESS -> RELAY -> STEWARD`
context_fallback: `Mini/Capsule are fallback witnesses only.`
non_claims: `no accepted-state claim`
"""

    blocked = call_chatgpt_connector_tool(
        tmp_path,
        "ion_submit_task_return",
        {"task_output_text": base, "context_receipt": receipt, "work_request_path": request_rel},
    )
    accepted = call_chatgpt_connector_tool(
        tmp_path,
        "ion_submit_task_return",
        {"task_output_text": with_posture, "context_receipt": receipt, "work_request_path": request_rel},
    )

    assert blocked["ok"] is True
    assert blocked["data"]["accepted_for_carrier_intake"] is False
    assert blocked["data"]["ion_operational_posture_required"] is True
    assert blocked["data"]["ion_operational_posture_accepted"] is False
    assert "missing_required_section:### ION OPERATIONAL POSTURE" in blocked["data"]["findings"]
    assert accepted["ok"] is True
    assert accepted["data"]["accepted_for_carrier_intake"] is True
    assert accepted["data"]["ion_operational_posture_accepted"] is True


def test_task_return_template_invalid_is_blocked_before_proof_intake_and_preserved(tmp_path):
    _seed_root(tmp_path)
    receipt = {
        "schema_id": "ion.context_load_receipt.v1",
        "required_context_reads": [
            {"kind": "file", "path": "ION/REPO_AUTHORITY.md", "required": True}
        ],
    }
    broken = """### RESULT
No required template headings.
"""

    blocked = call_chatgpt_connector_tool(
        tmp_path,
        "ion_submit_task_return",
        {"task_output_text": broken, "context_receipt": receipt},
    )

    assert blocked["ok"] is True
    assert blocked["data"]["accepted_for_carrier_intake"] is False
    assert blocked["data"]["return_template_valid"] is False
    assert blocked["data"]["blocked_but_preserved"] is True
    assert blocked["data"]["salvage_route"] == "ION/05_context/current/chatgpt_connector/task_returns"
    assert "missing_required_section:### CONTEXT PROOF" in blocked["data"]["findings"]
    machine_receipt = json.loads((tmp_path / blocked["data"]["machine_receipt_path"]).read_text(encoding="utf-8"))
    assert machine_receipt["receipt_source"] == "automation"
    assert machine_receipt["manual_ai_authored"] is False
    assert machine_receipt["diagnosis"]["classification"] == "return_template_missing_required_section"
    packet = json.loads((tmp_path / blocked["data"]["packet_path"]).read_text(encoding="utf-8"))
    assert packet["result"] == "RETURN_TEMPLATE_INVALID"


def test_codex_work_queue_prefers_accepted_return_for_settlement_projection(tmp_path):
    _seed_root(tmp_path)
    request_rel = "ION/05_context/current/chatgpt_connector/codex_work_requests/replay_family.json"
    request_path = tmp_path / request_rel
    request_path.parent.mkdir(parents=True, exist_ok=True)
    accepted_rel = "ION/05_context/current/chatgpt_connector/task_returns/2026-05-15T192506Z0000_task_return.json"
    invalid_rel = "ION/05_context/current/chatgpt_connector/task_returns/2026-05-15T192600Z0000_task_return.json"
    request_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": "codex_req_replay_family",
                "objective": "Replay family projection test",
                "status": "RETURN_TEMPLATE_INVALID",
                "latest_return_packet_path": invalid_rel,
                "return_packet_paths": [accepted_rel, invalid_rel],
                "created_at": "2026-05-15T19:18:07+00:00",
                "updated_at": "2026-05-15T19:26:01+00:00",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    returns_dir = tmp_path / "ION/05_context/current/chatgpt_connector/task_returns"
    returns_dir.mkdir(parents=True, exist_ok=True)
    (tmp_path / accepted_rel).write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_task_return_packet.v1",
                "work_request_id": "codex_req_replay_family",
                "work_request_path": request_rel,
                "accepted_for_carrier_intake": True,
                "result": "RECORDED_FOR_CARRIER_INTAKE",
                "created_at": "2026-05-15T19:25:06+00:00",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / invalid_rel).write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_task_return_packet.v1",
                "work_request_id": "codex_req_replay_family",
                "work_request_path": request_rel,
                "accepted_for_carrier_intake": False,
                "result": "RETURN_TEMPLATE_INVALID",
                "created_at": "2026-05-15T19:26:00+00:00",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    queue = call_chatgpt_connector_tool(tmp_path, "ion_codex_work_queue", {"limit": 10})
    assert queue["ok"] is True
    request_row = queue["data"]["requests"][0]
    assert request_row["latest_return_packet_path"] == accepted_rel
    assert request_row["latest_return_packet_path_raw"] == invalid_rel
    assert request_row["settlement_relevant_return_packet_path"] == accepted_rel
    assert request_row["settlement_relevant_source"] == "accepted_carrier_intake"
    assert invalid_rel in request_row["superseded_wrapper_return_packet_paths"]


def test_connector_requires_mounted_carrier_posture_with_gated_authority():
    result = audit_chatgpt_browser_mcp_connector_contract(Path.cwd())

    assert result["connector_id"] == "ION_CHATGPT_BROWSER_CONNECTOR"
    assert result["must_state_mounted_ion_carrier_posture"] is True
    assert result["role_authority_requires_phase_proof"] is True
    assert result["deployment_authority"] is False


def test_write_contract_report(tmp_path):
    root = Path.cwd()
    output = tmp_path / "CHATGPT_BROWSER_MCP_CONNECTOR_CONTRACT_V120.json"

    result = write_chatgpt_browser_mcp_connector_contract(root, output=output)

    assert output.exists()
    assert result["verdict"] == "ION_CHATGPT_BROWSER_MCP_CONNECTOR_CONTRACT_READY"
    assert not (set(result["allowed_tools"]) & FORBIDDEN_CAPABILITIES)


def test_http_preview_documented_host_port_launch_serves():
    assert documented_launch_requests_serve(["--ion-root", ".", "--host", "127.0.0.1", "--port", "8765"]) is True
    assert documented_launch_requests_serve([]) is False
    assert documented_launch_requests_serve(["--json", "--host", "127.0.0.1"]) is False


def test_file_put_text_stages_artifact_with_receipt(tmp_path):
    _seed_root(tmp_path)
    text = "browser-created planning artifact\n"
    expected = hashlib.sha256(text.encode("utf-8")).hexdigest()
    target_path = "ION/05_context/current/chatgpt_connector/artifacts/browser_note.md"
    lease = _seed_edit_lease(
        tmp_path,
        agent_id="agent.connector_artifact_test",
        lease_id="lease-connector-browser-note",
        target_paths=[target_path],
        lease_mode="artifact",
    )

    result = call_chatgpt_connector_tool(
        tmp_path,
        "ion_file_put_text",
        {
            "target_path": target_path,
            "text": text,
            "expected_sha256": expected,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            **lease,
        },
    )

    assert result["ok"] is True
    assert result["mutates_active_state"] is True
    assert result["data"]["sha256"] == expected
    assert (tmp_path / "ION/05_context/current/chatgpt_connector/artifacts/browser_note.md").read_text(encoding="utf-8") == text
    assert (tmp_path / result["data"]["receipt_path"]).exists()


def test_file_put_text_allows_safe_vnext_candidate_roots(tmp_path):
    _seed_root(tmp_path)
    targets = (
        "ION_VNEXT/06_context/demo.md",
        "ION_VNEXT/07_work/demo.md",
        "ION_VNEXT/09_references/demo.md",
    )

    for target_path in targets:
        text = f"content for {target_path}\n"
        lease = _seed_edit_lease(
            tmp_path,
            agent_id=f"agent.connector_safe_vnext_{target_path.split('/')[1]}",
            lease_id=f"lease-safe-vnext-{target_path.replace('/', '-').replace('.', '-')}",
            target_paths=[target_path],
            lease_mode="artifact",
        )
        result = call_chatgpt_connector_tool(
            tmp_path,
            "ion_file_put_text",
            {
                "target_path": target_path,
                "text": text,
                "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
                **lease,
            },
        )
        assert result["ok"] is True
        assert (tmp_path / target_path).read_text(encoding="utf-8") == text


def test_file_put_text_direct_ingest_preview_apply_and_idempotent_replay(tmp_path):
    _seed_root(tmp_path)
    target_path = "ION/02_architecture/ION_CONNECTOR_TRANSPORT_AND_LOD_ROUTING_PROTOCOL.md"
    text = "# Candidate protocol\n\nbounded direct ingest lane\n"
    expected = hashlib.sha256(text.encode("utf-8")).hexdigest()

    preview = call_chatgpt_connector_tool(
        tmp_path,
        "ion_file_put_text",
        {
            "target_path": target_path,
            "text": text,
            "expected_sha256": expected,
            "preview_only": True,
        },
    )
    missing_confirmation = call_chatgpt_connector_tool(
        tmp_path,
        "ion_file_put_text",
        {"target_path": target_path, "text": text, "expected_sha256": expected},
    )
    lease = _seed_edit_lease(
        tmp_path,
        agent_id="agent.connector_direct_ingest_test",
        lease_id="lease-direct-ingest-protocol-v1",
        target_paths=[target_path],
        lease_mode="artifact",
    )
    applied = call_chatgpt_connector_tool(
        tmp_path,
        "ion_file_put_text",
        {
            "target_path": target_path,
            "text": text,
            "expected_sha256": expected,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key": "direct-ingest-protocol-v1",
            **lease,
        },
    )
    replay = call_chatgpt_connector_tool(
        tmp_path,
        "ion_file_put_text",
        {
            "target_path": target_path,
            "text": text,
            "expected_sha256": expected,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key": "direct-ingest-protocol-v1",
            **lease,
        },
    )

    assert preview["ok"] is True
    assert preview["mutates_active_state"] is False
    assert preview["data"]["preview_only"] is True
    assert "ION_CONNECTOR_TRANSPORT_AND_LOD_ROUTING_PROTOCOL.md" in preview["data"]["unified_diff"]
    assert missing_confirmation["ok"] is False
    assert missing_confirmation["finding"] == "confirmation_required"
    assert applied["ok"] is True
    assert applied["mutates_active_state"] is True
    assert applied["data"]["idempotent_replay"] is False
    assert (tmp_path / target_path).read_text(encoding="utf-8") == text
    assert replay["ok"] is True
    assert replay["mutates_active_state"] is False
    assert replay["data"]["idempotent_replay"] is True
    assert replay["data"]["duplicate_prevented"] is True


def test_file_put_text_allows_active_onboarding_packet_with_confirmation(tmp_path):
    _seed_root(tmp_path)
    target_path = "ION/05_context/current/ACTIVE_CARRIER_ONBOARDING_PACKET.chatgpt_browser.json"
    text = "{\"carrier_id\":\"chatgpt_browser\"}\n"

    missing_confirmation = call_chatgpt_connector_tool(
        tmp_path,
        "ion_file_put_text",
        {"target_path": target_path, "text": text},
    )
    lease = _seed_edit_lease(
        tmp_path,
        agent_id="agent.connector_onboarding_packet_test",
        lease_id="lease-active-onboarding-packet",
        target_paths=[target_path],
        lease_mode="artifact",
    )
    with_confirmation = call_chatgpt_connector_tool(
        tmp_path,
        "ion_file_put_text",
        {
            "target_path": target_path,
            "text": text,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            **lease,
        },
    )

    assert missing_confirmation["ok"] is False
    assert missing_confirmation["finding"] == "confirmation_required"
    assert with_confirmation["ok"] is True
    assert (tmp_path / target_path).read_text(encoding="utf-8") == text


def test_file_put_text_blocks_private_and_secret_like_vnext_paths(tmp_path):
    _seed_root(tmp_path)
    private = call_chatgpt_connector_tool(
        tmp_path,
        "ion_file_put_text",
        {"target_path": "ION_VNEXT/99_private/demo.md", "text": "x\n", "confirmation": "ION_BOUNDED_WRITE_CONFIRMED"},
    )
    dotenv = call_chatgpt_connector_tool(
        tmp_path,
        "ion_file_put_text",
        {"target_path": "ION_VNEXT/06_context/.env", "text": "x\n", "confirmation": "ION_BOUNDED_WRITE_CONFIRMED"},
    )
    secret = call_chatgpt_connector_tool(
        tmp_path,
        "ion_file_put_text",
        {"target_path": "ION_VNEXT/07_work/secrets/demo.md", "text": "x\n", "confirmation": "ION_BOUNDED_WRITE_CONFIRMED"},
    )

    assert private["ok"] is False
    assert private["finding"] == "target_path_not_in_artifact_transfer_roots"
    assert dotenv["ok"] is False
    assert dotenv["finding"] == "target_path_forbidden_by_transfer_policy"
    assert secret["ok"] is False
    assert secret["finding"] == "target_path_forbidden_by_transfer_policy"


def test_file_put_text_blocks_path_escape_and_overwrite(tmp_path):
    _seed_root(tmp_path)
    target = tmp_path / "ION/05_context/current/chatgpt_connector/artifacts/existing.md"
    target.parent.mkdir(parents=True)
    target.write_text("existing\n", encoding="utf-8")

    escaped = call_chatgpt_connector_tool(
        tmp_path,
        "ion_file_put_text",
        {"target_path": "../outside.md", "text": "bad", "confirmation": "ION_BOUNDED_WRITE_CONFIRMED"},
    )
    lease = _seed_edit_lease(
        tmp_path,
        agent_id="agent.connector_overwrite_test",
        lease_id="lease-existing-artifact-overwrite",
        target_paths=["ION/05_context/current/chatgpt_connector/artifacts/existing.md"],
        lease_mode="artifact",
    )
    overwrite = call_chatgpt_connector_tool(
        tmp_path,
        "ion_file_put_text",
        {
            "target_path": "ION/05_context/current/chatgpt_connector/artifacts/existing.md",
            "text": "new",
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            **lease,
        },
    )

    assert escaped["ok"] is False
    assert escaped["finding"] == "target_path_must_be_repo_relative_without_escape"
    assert overwrite["ok"] is False
    assert overwrite["finding"] == "target_exists_requires_lifecycle_receipt"
    assert target.read_text(encoding="utf-8") == "existing\n"


def test_chunked_artifact_upload_commit_verifies_sha256(tmp_path):
    _seed_root(tmp_path)
    data = b"chunk-one::chunk-two"
    expected = hashlib.sha256(data).hexdigest()
    target_path = "ION/05_context/current/chatgpt_connector/artifacts/payload.bin"
    lease = _seed_edit_lease(
        tmp_path,
        agent_id="agent.connector_upload_artifact_test",
        lease_id="lease-upload-artifact-payload",
        target_paths=[target_path],
        lease_mode="artifact",
    )

    init = call_chatgpt_connector_tool(
        tmp_path,
        "ion_artifact_upload_init",
        {
            "artifact_name": "payload.bin",
            "target_path": target_path,
            "expected_sha256": expected,
            "total_bytes": len(data),
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            **lease,
        },
    )
    upload_id = init["data"]["upload_id"]
    chunk = call_chatgpt_connector_tool(
        tmp_path,
        "ion_artifact_upload_chunk",
        {
            "upload_id": upload_id,
            "chunk_index": 0,
            "data_base64": base64.b64encode(data).decode("ascii"),
            "chunk_sha256": expected,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            **lease,
        },
    )
    commit = call_chatgpt_connector_tool(
        tmp_path,
        "ion_artifact_upload_commit",
        {"upload_id": upload_id, "confirmation": "ION_BOUNDED_WRITE_CONFIRMED", **lease},
    )

    assert init["ok"] is True
    assert chunk["ok"] is True
    assert commit["ok"] is True
    assert commit["data"]["sha256"] == expected
    assert (tmp_path / "ION/05_context/current/chatgpt_connector/artifacts/payload.bin").read_bytes() == data


def test_artifact_upload_init_requires_confirmation_for_direct_ingest_roots(tmp_path):
    _seed_root(tmp_path)
    target_path = "ION/02_architecture/proto.md"
    data = b"# Proto\n"
    expected = hashlib.sha256(data).hexdigest()
    missing_confirmation = call_chatgpt_connector_tool(
        tmp_path,
        "ion_artifact_upload_init",
        {
            "artifact_name": "proto.md",
            "target_path": target_path,
        },
    )
    missing_lease = call_chatgpt_connector_tool(
        tmp_path,
        "ion_artifact_upload_init",
        {
            "artifact_name": "proto.md",
            "target_path": target_path,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
        },
    )
    lease = _seed_edit_lease(
        tmp_path,
        agent_id="agent.connector_upload_direct_ingest_test",
        lease_id="lease-upload-direct-ingest-proto",
        target_paths=[target_path],
        lease_mode="artifact",
    )
    with_confirmation = call_chatgpt_connector_tool(
        tmp_path,
        "ion_artifact_upload_init",
        {
            "artifact_name": "proto.md",
            "target_path": target_path,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "expected_sha256": expected,
            "total_bytes": len(data),
            **lease,
        },
    )
    upload_id = with_confirmation["data"]["upload_id"]
    chunk = call_chatgpt_connector_tool(
        tmp_path,
        "ion_artifact_upload_chunk",
        {
            "upload_id": upload_id,
            "chunk_index": 0,
            "data_base64": base64.b64encode(data).decode("ascii"),
            "chunk_sha256": expected,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            **lease,
        },
    )
    commit_missing_lease = call_chatgpt_connector_tool(
        tmp_path,
        "ion_artifact_upload_commit",
        {
            "upload_id": upload_id,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
        },
    )
    commit = call_chatgpt_connector_tool(
        tmp_path,
        "ion_artifact_upload_commit",
        {
            "upload_id": upload_id,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            **lease,
        },
    )

    assert missing_confirmation["ok"] is False
    assert missing_confirmation["finding"] == "confirmation_required"
    assert missing_lease["ok"] is False
    assert missing_lease["finding"] == "artifact_lease_required"
    assert with_confirmation["ok"] is True
    assert chunk["ok"] is True
    assert commit_missing_lease["ok"] is False
    assert commit_missing_lease["finding"] == "artifact_lease_required"
    assert commit["ok"] is True
    assert (tmp_path / target_path).read_bytes() == data


def test_artifact_upload_init_allows_active_onboarding_packet_with_confirmation(tmp_path):
    _seed_root(tmp_path)
    target_path = "ION/05_context/current/ACTIVE_CARRIER_ONBOARDING_PACKET.chatgpt_browser.json"

    missing_confirmation = call_chatgpt_connector_tool(
        tmp_path,
        "ion_artifact_upload_init",
        {
            "artifact_name": "ACTIVE_CARRIER_ONBOARDING_PACKET.chatgpt_browser.json",
            "target_path": target_path,
        },
    )
    lease = _seed_edit_lease(
        tmp_path,
        agent_id="agent.connector_upload_onboarding_packet_test",
        lease_id="lease-upload-active-onboarding-packet",
        target_paths=[target_path],
        lease_mode="artifact",
    )
    with_confirmation = call_chatgpt_connector_tool(
        tmp_path,
        "ion_artifact_upload_init",
        {
            "artifact_name": "ACTIVE_CARRIER_ONBOARDING_PACKET.chatgpt_browser.json",
            "target_path": target_path,
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            **lease,
        },
    )

    assert missing_confirmation["ok"] is False
    assert missing_confirmation["finding"] == "confirmation_required"
    assert with_confirmation["ok"] is True
    assert with_confirmation["data"]["target_path"] == target_path


def test_carrier_message_send_poll_ack_uses_active_queue(tmp_path):
    _seed_root(tmp_path)

    sent = call_chatgpt_connector_tool(
        tmp_path,
        "ion_carrier_message_send",
        {
            "sender_carrier_id": "CHATGPT_BROWSER_CARRIER",
            "recipient": "CODEX_CLI_CARRIER",
            "body": "handoff ready",
            "context_refs": ["ION/02_architecture/ION_FULL_CARRIER_MCP_PARITY_PROTOCOL.md"],
        },
    )
    message_id = sent["data"]["message_id"]
    polled = call_chatgpt_connector_tool(
        tmp_path,
        "ion_carrier_message_poll",
        {"recipient": "CODEX_CLI_CARRIER"},
    )
    acked = call_chatgpt_connector_tool(
        tmp_path,
        "ion_carrier_message_ack",
        {"message_id": message_id, "ack_by_carrier": "CODEX_CLI_CARRIER"},
    )

    assert sent["ok"] is True
    assert sent["mutates_active_state"] is True
    assert polled["ok"] is True
    assert polled["data"]["message_count"] == 1
    assert polled["data"]["messages"][0]["message_id"] == message_id
    assert acked["ok"] is True
    assert (tmp_path / "ION/05_context/current/ACTIVE_CARRIER_MESSAGE_QUEUE.json").exists()


def test_bounded_project_visibility_tools_read_search_and_tree(tmp_path):
    _seed_root(tmp_path)
    note = tmp_path / "ION/02_architecture/VISIBILITY_NOTE.md"
    note.parent.mkdir(parents=True)
    note.write_text("full carrier visibility token\n", encoding="utf-8")
    registry = tmp_path / "ION/03_registry/sample_registry.yaml"
    registry.parent.mkdir(parents=True)
    registry.write_text("schema_id: sample\n", encoding="utf-8")
    template = tmp_path / "ION/07_templates/sample_template.md"
    template.parent.mkdir(parents=True)
    template.write_text("# Template\n", encoding="utf-8")

    read = call_chatgpt_connector_tool(tmp_path, "ion_file_read", {"path": "ION/02_architecture/VISIBILITY_NOTE.md"})
    search = call_chatgpt_connector_tool(tmp_path, "ion_file_search", {"query": "visibility token", "roots": ["ION/02_architecture"]})
    tree = call_chatgpt_connector_tool(tmp_path, "ion_tree_list", {"path": "ION", "max_depth": 2})
    reg = call_chatgpt_connector_tool(tmp_path, "ion_registry_read", {"path": "ION/03_registry/sample_registry.yaml"})
    tmpl = call_chatgpt_connector_tool(tmp_path, "ion_template_read", {"path": "ION/07_templates/sample_template.md"})
    blocked = call_chatgpt_connector_tool(tmp_path, "ion_file_read", {"path": ".git/config"})

    assert read["ok"] is True
    assert "visibility token" in read["data"]["text"]
    assert search["ok"] is True
    assert search["data"]["match_count"] == 1
    assert tree["ok"] is True
    assert any(item["path"] == "ION/02_architecture/VISIBILITY_NOTE.md" for item in tree["data"]["entries"])
    assert reg["ok"] is True
    assert "schema_id: sample" in reg["data"]["text"]
    assert tmpl["ok"] is True
    assert "# Template" in tmpl["data"]["text"]
    assert blocked["ok"] is False
    assert blocked["finding"] == "path_forbidden_by_read_policy"


def test_context_compile_receipt_hydrate_and_onboarding_alias(tmp_path):
    _seed_root(tmp_path)
    required = [
        "ION/02_architecture/ION_MOUNT_CONTRACT.md",
        "ION/02_architecture/ION_FULL_CARRIER_MCP_PARITY_PROTOCOL.md",
        "ION/02_architecture/ION_CARRIER_TO_CARRIER_COMMUNICATION_PROTOCOL.md",
        "ION/03_registry/chatgpt_browser_carrier_profile.yaml",
        "ION/03_registry/carrier_capability_registry.yaml",
        "ION/03_registry/mcp_full_carrier_tool_registry.yaml",
        "ION/05_context/current/CHATGPT_BROWSER_MCP_CONNECTOR_CONTRACT_V120.json",
        "ION/05_context/current/CHATGPT_BROWSER_CLOUDFLARE_TUNNEL_V122.json",
        "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json",
        "ION/05_context/current/ACTIVE_CARRIER_MESSAGE_QUEUE.json",
    ]
    for rel in required:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n" if path.suffix == ".json" else "surface\n", encoding="utf-8")

    compiled = call_chatgpt_connector_tool(tmp_path, "ion_context_compile", {"profile": "full_carrier_mcp_parity"})
    hydrated = call_chatgpt_connector_tool(tmp_path, "ion_receipt_hydrate", {"limit": 5})
    onboarding = call_chatgpt_connector_tool(Path.cwd(), "ion_carrier_onboarding_packet", {"carrier": "full_carrier_mcp_parity"})

    assert compiled["ok"] is True
    assert compiled["data"]["profile"] == "full_carrier_mcp_parity"
    assert compiled["data"]["surface_count"] >= len(required)
    assert hydrated["ok"] is True
    assert hydrated["data"]["schema_id"] == "ion.receipt_hydration_view_model.v1"
    assert onboarding["ok"] is True
    assert onboarding["data"]["carrier_profile"]["path"] == "ION/03_registry/chatgpt_browser_carrier_profile.yaml"


def test_codex_runner_reconcile_tool_clears_terminal_stale_active_reference(tmp_path):
    _seed_root(tmp_path)
    run_rel = "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_test/run.json"
    run_path = tmp_path / run_rel
    run_path.parent.mkdir(parents=True, exist_ok=True)
    run_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_run.v1",
                "run_id": "run_test",
                "request_id": "req_test",
                "status": "CODEX_CLI_EXIT_NONZERO",
                "failure_classification": "CODEX_CLI_FAILURE",
                "run_packet_path": run_rel,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": {
                    "run_id": "run_test",
                    "pid": 999999999,
                    "run_packet_path": run_rel,
                    "request_path": "ION/05_context/current/chatgpt_connector/codex_work_requests/req_test.json",
                    "started_at": "2026-05-09T00:00:00+00:00",
                },
                "latest_run": run_rel,
                "production_authority": False,
                "live_execution_authority": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    reconciled = call_chatgpt_connector_tool(tmp_path, "ion_codex_runner_reconcile", {"write": True})

    updated_state = json.loads(state_path.read_text(encoding="utf-8"))
    assert reconciled["ok"] is True
    assert reconciled["mutates_active_state"] is True
    assert reconciled["data"]["reconciliation"]["action"] == "clear_terminal_active_reference"
    assert updated_state["active_run"] is None


def test_codex_worker_live_status_exposes_worker_lifecycle_events(tmp_path):
    _seed_root(tmp_path)
    run_rel = "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_lifecycle/run.json"
    run_path = tmp_path / run_rel
    run_path.parent.mkdir(parents=True, exist_ok=True)
    task_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/return_lifecycle.json"
    run_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_run.v1",
                "run_id": "run_lifecycle",
                "request_id": "req_lifecycle",
                "request_path": "ION/05_context/current/chatgpt_connector/codex_work_requests/req_lifecycle.json",
                "run_packet_path": run_rel,
                "run_dir": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_lifecycle",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "started_at": "2026-05-10T17:00:00+00:00",
                "completed_at": "2026-05-10T17:01:00+00:00",
                "submit_result": {
                    "accepted_for_carrier_intake": True,
                    "context_proof_accepted": True,
                    "template_action_proof_accepted": True,
                    "packet_path": task_return_rel,
                },
                "worker_lifecycle_events": [
                    {
                        "event": "worker_boot",
                        "at": "2026-05-10T17:00:01+00:00",
                        "run_id": "run_lifecycle",
                        "request_id": "req_lifecycle",
                        "status": "CODEX_CLI_RUNNING",
                        "pid": 123,
                        "production_authority": False,
                        "live_execution_authority": False,
                    },
                    {
                        "event": "worker_terminal",
                        "at": "2026-05-10T17:01:00+00:00",
                        "run_id": "run_lifecycle",
                        "request_id": "req_lifecycle",
                        "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                        "pid": 123,
                        "terminal_state": "accepted",
                        "task_return_packet_path": task_return_rel,
                        "context_proof_accepted": True,
                        "template_action_proof_accepted": True,
                        "production_authority": False,
                        "live_execution_authority": False,
                    },
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": None,
                "latest_run": run_rel,
                "production_authority": False,
                "live_execution_authority": False,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    status = call_chatgpt_connector_tool(tmp_path, "ion_codex_worker_live_status", {})

    telemetry = status["data"]["live_worker_telemetry"]
    assert status["ok"] is True
    assert telemetry["run_status"] == "RETURN_RECORDED_PROOF_ACCEPTED"
    assert telemetry["latest_worker_lifecycle_event"]["event"] == "worker_terminal"
    assert telemetry["latest_worker_lifecycle_event"]["terminal_state"] == "accepted"
    assert telemetry["worker_lifecycle_events"][0]["event"] == "worker_boot"
    assert telemetry["worker_lifecycle_events"][1]["task_return_packet_path"] == task_return_rel


def test_capsule_status_reads_paths_without_exposing_secret_text(tmp_path):
    _seed_root(tmp_path)
    for rel, text in {
        "ION/05_context/current/codex_solo/CAPSULE.md": "# Capsule\nsecret_token_should_not_leak\n",
        "ION/05_context/current/codex_solo/MINI.md": "mini index\nsecret_token_should_not_leak\n",
        "ION/05_context/current/codex_solo/HOT_CONTEXT.md": "hot context\nsecret_token_should_not_leak\n",
        "ION/05_context/current/codex_capsule_chat/state.json": "{\"lanes\": {\"codex_general\": {\"turns\": [], \"queue_links\": []}}}\n",
    }.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    status = call_chatgpt_connector_tool(tmp_path, "ion_codex_capsule_chat_status", {})

    status_text = json.dumps(status, sort_keys=True)
    assert status["ok"] is True
    assert status["data"]["paths"]["capsule"]["path"] == "ION/05_context/current/codex_solo/CAPSULE.md"
    assert status["data"]["paths"]["mini"]["path"] == "ION/05_context/current/codex_solo/MINI.md"
    assert status["data"]["paths"]["hot_context"]["path"] == "ION/05_context/current/codex_solo/HOT_CONTEXT.md"
    assert "secret_token_should_not_leak" not in status_text


def test_capsule_message_send_writes_bounded_state_and_packet_only(tmp_path):
    _seed_root(tmp_path)

    sent = call_chatgpt_connector_tool(
        tmp_path,
        "ion_codex_capsule_message_send",
        {"message": "Capsule bridge hello", "author": "user"},
    )
    polled = call_chatgpt_connector_tool(
        tmp_path,
        "ion_codex_capsule_message_poll",
        {"lane_id": "codex_general", "limit": 10},
    )

    state_path = tmp_path / "ION/05_context/current/codex_capsule_chat/state.json"
    queue_dir = tmp_path / "ION/05_context/current/chatgpt_connector/codex_work_requests"
    assert sent["ok"] is True
    assert sent["mutates_active_state"] is True
    assert state_path.exists()
    assert "Capsule bridge hello" in state_path.read_text(encoding="utf-8")
    assert (tmp_path / sent["data"]["packet_path"]).exists()
    assert polled["ok"] is True
    assert polled["data"]["message_count"] >= 1
    assert not queue_dir.exists() or not list(queue_dir.glob("*.json"))


def test_bounded_patch_preview_and_apply_with_receipt_and_replay(tmp_path):
    _seed_root(tmp_path)
    target = tmp_path / "ION/04_packages/kernel/sample_patch_target.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("VALUE = 1\n", encoding="utf-8")
    original_sha = hashlib.sha256(target.read_text(encoding="utf-8").encode("utf-8")).hexdigest()

    preview = call_chatgpt_connector_tool(
        tmp_path,
        "ion_bounded_patch_preview",
        {
            "operations": [
                {
                    "path": "ION/04_packages/kernel/sample_patch_target.py",
                    "old_text": "VALUE = 1\n",
                    "new_text": "VALUE = 2\n",
                    "expected_sha256": original_sha,
                }
            ]
        },
    )

    assert preview["ok"] is True
    assert preview["mutates_active_state"] is False
    assert preview["data"]["touched_paths"] == ["ION/04_packages/kernel/sample_patch_target.py"]
    assert "-VALUE = 1" in preview["data"]["previews"][0]["diff"]
    assert "+VALUE = 2" in preview["data"]["previews"][0]["diff"]

    lease = _seed_edit_lease(
        tmp_path,
        agent_id="agent.connector_bounded_patch_test",
        lease_id="lease-bounded-patch-sample-target",
        target_paths=["ION/04_packages/kernel/sample_patch_target.py"],
    )
    applied = call_chatgpt_connector_tool(
        tmp_path,
        "ion_bounded_patch_apply",
        {
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key": "patch-sample-target-001",
            **lease,
            "operations": [
                {
                    "path": "ION/04_packages/kernel/sample_patch_target.py",
                    "old_text": "VALUE = 1\n",
                    "new_text": "VALUE = 2\n",
                    "expected_sha256": original_sha,
                }
            ],
        },
    )
    replay = call_chatgpt_connector_tool(
        tmp_path,
        "ion_bounded_patch_apply",
        {
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key": "patch-sample-target-001",
            **lease,
            "operations": [
                {
                    "path": "ION/04_packages/kernel/sample_patch_target.py",
                    "old_text": "VALUE = 1\n",
                    "new_text": "VALUE = 2\n",
                    "expected_sha256": original_sha,
                }
            ],
        },
    )

    assert applied["ok"] is True
    assert applied["mutates_active_state"] is True
    assert applied["data"]["status"] == "CANDIDATE_PATCH_APPLIED"
    assert (tmp_path / applied["data"]["receipt_path"]).exists()
    assert target.read_text(encoding="utf-8") == "VALUE = 2\n"
    assert replay["ok"] is True
    assert replay["mutates_active_state"] is False
    assert replay["data"]["idempotent_replay"] is True
    assert replay["data"]["duplicate_prevented"] is True
    assert replay["data"]["receipt_path"] == applied["data"]["receipt_path"]


def test_http_mcp_bounded_patch_apply_preserves_confirmation(tmp_path):
    _seed_root(tmp_path)
    target = tmp_path / "ION/04_packages/kernel/http_patch_target.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("VALUE = 1\n", encoding="utf-8")
    original_sha = hashlib.sha256(target.read_text(encoding="utf-8").encode("utf-8")).hexdigest()

    blocked = handle_mcp_jsonrpc(
        tmp_path,
        {
            "jsonrpc": "2.0",
            "id": "missing-confirmation",
            "method": "tools/call",
            "params": {
                "name": "ion_bounded_patch_apply",
                "arguments": {
                    "idempotency_key": "http-patch-target-001",
                    "operations": [
                        {
                            "path": "ION/04_packages/kernel/http_patch_target.py",
                            "old_text": "VALUE = 1\n",
                            "new_text": "VALUE = 2\n",
                            "expected_sha256": original_sha,
                        }
                    ],
                },
            },
        },
    )
    blocked_content = blocked["result"]["structuredContent"]
    assert blocked["result"]["isError"] is True
    assert blocked_content["finding"] == "bounded_write_confirmation_required"

    lease = _seed_edit_lease(
        tmp_path,
        agent_id="agent.connector_http_patch_test",
        lease_id="lease-http-patch-target",
        target_paths=["ION/04_packages/kernel/http_patch_target.py"],
    )
    applied = handle_mcp_jsonrpc(
        tmp_path,
        {
            "jsonrpc": "2.0",
            "id": "with-confirmation",
            "method": "tools/call",
            "params": {
                "name": "ion_bounded_patch_apply",
                "arguments": {
                    "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
                    "idempotency_key": "http-patch-target-001",
                    **lease,
                    "operations": [
                        {
                            "path": "ION/04_packages/kernel/http_patch_target.py",
                            "old_text": "VALUE = 1\n",
                            "new_text": "VALUE = 2\n",
                            "expected_sha256": original_sha,
                        }
                    ],
                },
            },
        },
    )
    applied_content = applied["result"]["structuredContent"]
    assert applied["result"]["isError"] is False
    assert applied_content["ok"] is True
    assert applied_content["data"]["status"] == "CANDIDATE_PATCH_APPLIED"
    assert target.read_text(encoding="utf-8") == "VALUE = 2\n"

    replay = handle_mcp_jsonrpc(
        tmp_path,
        {
            "jsonrpc": "2.0",
            "id": "replay-confirmation",
            "method": "tools/call",
            "params": {
                "name": "ion_bounded_patch_apply",
                "arguments": {
                    "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
                    "idempotency_key": "http-patch-target-001",
                    **lease,
                    "operations": [
                        {
                            "path": "ION/04_packages/kernel/http_patch_target.py",
                            "old_text": "VALUE = 1\n",
                            "new_text": "VALUE = 2\n",
                            "expected_sha256": original_sha,
                        }
                    ],
                },
            },
        },
    )
    replay_content = replay["result"]["structuredContent"]
    assert replay["result"]["isError"] is False
    assert replay_content["ok"] is True
    assert replay_content["mutates_active_state"] is False
    assert replay_content["data"]["idempotent_replay"] is True
    assert replay_content["data"]["duplicate_prevented"] is True


def test_bounded_patch_blocks_protected_shared_context(tmp_path):
    _seed_root(tmp_path)
    target = tmp_path / "ION/05_context/current/codex_solo/CAPSULE.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# Capsule\n", encoding="utf-8")

    result = call_chatgpt_connector_tool(
        tmp_path,
        "ion_bounded_patch_apply",
        {
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "operations": [
                {
                    "path": "ION/05_context/current/codex_solo/CAPSULE.md",
                    "old_text": "# Capsule\n",
                    "new_text": "# Changed\n",
                }
            ],
        },
    )

    assert result["ok"] is False
    assert result["finding"] == "protected_shared_context_path_requires_settlement"
    assert target.read_text(encoding="utf-8") == "# Capsule\n"


def test_bounded_patch_blocks_non_allowlisted_path(tmp_path):
    _seed_root(tmp_path)
    target = tmp_path / "random.txt"
    target.write_text("x\n", encoding="utf-8")

    result = call_chatgpt_connector_tool(
        tmp_path,
        "ion_bounded_patch_preview",
        {
            "operations": [
                {
                    "path": "random.txt",
                    "old_text": "x\n",
                    "new_text": "y\n",
                }
            ],
        },
    )

    assert result["ok"] is False
    assert result["finding"] == "target_path_not_in_bounded_patch_roots"
    assert target.read_text(encoding="utf-8") == "x\n"


def test_bounded_patch_allows_safe_vnext_candidate_roots(tmp_path):
    _seed_root(tmp_path)
    for idx, target_path in enumerate(
        (
            "ION_VNEXT/06_context/patch_target.md",
            "ION_VNEXT/07_work/patch_target.md",
            "ION_VNEXT/09_references/patch_target.md",
        ),
        start=1,
    ):
        target = tmp_path / target_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("before\n", encoding="utf-8")
        result = call_chatgpt_connector_tool(
            tmp_path,
            "ion_bounded_patch_preview",
            {
                "operations": [
                    {
                        "path": target_path,
                        "old_text": "before\n",
                        "new_text": f"after-{idx}\n",
                    }
                ]
            },
        )
        assert result["ok"] is True
        assert result["data"]["schema_id"] == "ion.chatgpt_browser_connector_bounded_patch_preview.v1"
        assert target_path in result["data"]["touched_paths"]


def test_bounded_patch_blocks_private_and_secret_like_vnext_paths(tmp_path):
    _seed_root(tmp_path)
    private = call_chatgpt_connector_tool(
        tmp_path,
        "ion_bounded_patch_preview",
        {
            "operations": [
                {"path": "ION_VNEXT/99_private/demo.md", "old_text": "x\n", "new_text": "y\n"}
            ]
        },
    )
    dotenv = call_chatgpt_connector_tool(
        tmp_path,
        "ion_bounded_patch_preview",
        {
            "operations": [
                {"path": "ION_VNEXT/06_context/.env", "old_text": "x\n", "new_text": "y\n"}
            ]
        },
    )
    secret = call_chatgpt_connector_tool(
        tmp_path,
        "ion_bounded_patch_preview",
        {
            "operations": [
                {"path": "ION_VNEXT/07_work/vault/demo.md", "old_text": "x\n", "new_text": "y\n"}
            ]
        },
    )

    assert private["ok"] is False
    assert private["finding"] == "target_path_not_in_bounded_patch_roots"
    assert dotenv["ok"] is False
    assert dotenv["finding"] == "target_path_contains_forbidden_secret_word"
    assert secret["ok"] is False
    assert secret["finding"] == "target_path_contains_forbidden_secret_word"
