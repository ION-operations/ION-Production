import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import urllib.request

from kernel.ion_chatgpt_browser_mcp_http_preview import (
    BOUNDED_QUEUE_RECEIPT_TOOLS,
    APP_PATHS,
    READY_VERDICT,
    WRITE_CONFIRMATION_TOKEN,
    audit_http_mcp_preview,
    handle_mcp_jsonrpc,
    http_mcp_tool_list,
    render_codex_worker_live_status_html,
    render_helixion_site_bar,
    render_ion_connector_landing,
    render_project_workbench_html,
    render_public_cockpit_login,
    wrap_helixion_site_shell,
    write_http_mcp_preview_audit,
)


def _seed_root(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").parent.mkdir(parents=True)
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")


def _seed_fanout_dryrun_status_artifacts(root: Path) -> None:
    base = root / "ION/05_context/current/kernel_fanout_scheduler/carrier_dryrun"
    (root / "ION/05_context/current/chatgpt_connector/task_returns").mkdir(parents=True, exist_ok=True)
    (
        root / "ION/05_context/current/chatgpt_connector/task_returns/2026-05-14T021628Z0000_task_return.json"
    ).write_text("{\"accepted_for_carrier_intake\": true}\n", encoding="utf-8")
    for scenario in ("success", "forced_timeout", "forced_conflict"):
        scenario_dir = base / scenario
        scenario_dir.mkdir(parents=True, exist_ok=True)
        (scenario_dir / "result.json").write_text(
            '{"schema_id":"ion.kernel_fanout_true_parallel_smoke_result.v1"}\n',
            encoding="utf-8",
        )
        (scenario_dir / "parent_receipt.json").write_text(
            '{"schema_id":"ion.kernel_fanout_carrier_dryrun_parent_receipt.v1"}\n',
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
                    "conflict_deferral_events": 5,
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


def _seed_worker_cockpit_artifacts(root: Path) -> None:
    run_rel = "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_page/run.json"
    run_dir = root / "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_page"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "prompt.md").write_text("# worker prompt\n", encoding="utf-8")
    (run_dir / "stdout.log").write_text("stdout line\n", encoding="utf-8")
    (run_dir / "stderr.log").write_text("stderr line\n", encoding="utf-8")
    (run_dir / "worker_stdout.log").write_text("worker stdout line\n", encoding="utf-8")
    (run_dir / "worker_stderr.log").write_text("worker stderr line\n", encoding="utf-8")
    (run_dir / "latest_return.md").write_text("### RESULT\nreturn\n", encoding="utf-8")
    (run_dir / "context_receipt.json").write_text("{\"schema_id\":\"ion.context_load_receipt.v1\"}\n", encoding="utf-8")
    (run_dir / "worker_context_awareness_receipt.json").write_text(
        json.dumps(
            {
                "schema_id": "ion.worker_context_awareness_receipt.v1",
                "status": "WORKER_CONTEXT_ACKNOWLEDGED",
                "worker_authored": False,
                "required_context_reads": [
                    {"path": "ION/04_packages/kernel/ion_chatgpt_browser_mcp_http_preview.py", "status": "READY"},
                    {"path": "ION/04_packages/kernel/ion_cockpit_view_model.py", "status": "MISSING"},
                ],
                "missing_required_context_paths": ["ION/04_packages/kernel/ion_cockpit_view_model.py"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (root / run_rel).write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_run.v1",
                "run_id": "run_worker_page",
                "request_id": "req_worker_page",
                "request_path": "ION/05_context/current/chatgpt_connector/codex_work_requests/req_worker_page.json",
                "run_packet_path": run_rel,
                "run_dir": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_page",
                "prompt_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_page/prompt.md",
                "context_receipt_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_page/context_receipt.json",
                "worker_context_awareness_receipt_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_page/worker_context_awareness_receipt.json",
                "stdout_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_page/stdout.log",
                "stderr_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_page/stderr.log",
                "last_message_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_page/latest_return.md",
                "created_at": "2026-05-14T03:01:00+00:00",
                "started_at": "2026-05-14T03:01:05+00:00",
                "completed_at": "2026-05-14T03:01:40+00:00",
                "status": "RETURN_TEMPLATE_INVALID",
                "submit_result": {
                    "context_proof_accepted": True,
                    "template_action_proof_accepted": True,
                    "return_template_valid": False,
                    "workload_diff_required": True,
                    "workload_diff_present": False,
                    "workload_diff_accepted": False,
                    "packet_path": "ION/05_context/current/chatgpt_connector/task_returns/return_worker_page.json",
                },
                "codex_model_move_summary": "gpt-5.3-codex / high for code_patch (conserve_main_bank)",
                "codex_model_move": {
                    "selected_model": "gpt-5.3-codex",
                    "selected_reasoning_effort": "high",
                    "usage_pool_id": "codex_primary_observed",
                    "model_move_id": "move_worker_page",
                    "selection_reason": ["routing_posture:conserve_main_bank"],
                },
                "worker_lifecycle_events": [
                    {"event": "worker_boot", "at": "2026-05-14T03:01:05+00:00"},
                    {"event": "worker_terminal", "at": "2026-05-14T03:01:40+00:00", "terminal_state": "template_invalid"},
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    state_path = root / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": None,
                "latest_run": run_rel,
                "updated_at": "2026-05-14T03:01:41+00:00",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    _seed_fanout_dryrun_status_artifacts(root)
    settlement = root / "ION/05_context/current/kernel_fanout_scheduler/settlement/fanout_dryrun_readonly_mcp_exposure_settlement_20260514.json"
    settlement.parent.mkdir(parents=True, exist_ok=True)
    settlement.write_text(json.dumps({"status": "DEFERRED_ENVIRONMENT_BLOCKED"}) + "\n", encoding="utf-8")
    supa = root / "ION/05_context/current/supabase_event_mirror/receipts/20260514_worker_event.json"
    supa.parent.mkdir(parents=True, exist_ok=True)
    supa.write_text(
        json.dumps(
            {
                "remote_result": {
                    "event_type": "worker_cockpit_joc_ui_upgrade_requirement_added",
                    "packet_id": "PCKT-ION-WORKER-COCKPIT-JOC-LIVE-UI-UPGRADE-20260514",
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_http_preview_audit_ready_on_current_tree():
    result = audit_http_mcp_preview(Path.cwd())

    assert result["schema_id"] == "ion.chatgpt_browser_http_mcp_preview.v1"
    assert result["verdict"] == READY_VERDICT
    assert result["connector_state"] == "LOCAL_HTTP_PREVIEW_NOT_PUBLIC_CONNECTOR"
    assert result["write_confirmation_required"] is True
    assert result["production_authority"] is False
    assert result["live_execution_authority"] is False
    assert result["deployment_authority"] is False
    assert result["public_cockpit_auth"]["schema_id"] == "ion.public_cockpit_auth_status.v1"


def test_tools_list_exposes_only_v120_contract_tools():
    tools = http_mcp_tool_list()
    names = {tool["name"] for tool in tools}

    assert "ion_status" in names
    assert "ion_carrier_onboarding_packet" in names
    assert "ion_codex_work_queue" in names
    assert "ion_file_read" in names
    assert "ion_tool_manifest" in names
    assert "ion_daemon_status" in names
    assert "ion_codex_worker_live_status" in names
    assert "ion_codex_runner_reconcile" in names
    assert "ion_codex_capsule_chat_status" in names
    assert "ion_codex_capsule_message_send" in names
    assert "ion_codex_capsule_message_poll" in names
    assert "ion_codex_capsule_sync_to_queue" in names
    assert "ion_codex_queue_process_once" in names
    assert "ion_agent_list" in names
    assert "ion_agent_invoke" in names
    assert "ion_swarm_step_once" in names
    assert "ion_project_workspace_status" in names
    assert "ion_project_preview_status" in names
    assert "ion_project_workbench_timeline" in names
    assert "ion_project_file_read" in names
    assert "ion_project_patch_preview" in names
    assert "ion_kernel_fanout_carrier_dryrun_status" in names
    assert "ion_project_patch_apply" in names
    assert "ion_project_patch_revert" in names
    assert "ion_project_action_run" in names
    assert "ion_project_browser_capture" in names
    assert "ion_queue_operator_message" in names
    assert "arbitrary_shell" not in names
    for tool in tools:
        if tool["name"] in BOUNDED_QUEUE_RECEIPT_TOOLS:
            assert "confirmation" in tool["inputSchema"]["properties"]
            assert tool["annotations"]["readOnlyHint"] is False
            assert tool["annotations"]["destructiveHint"] is False
        if tool["name"] == "ion_kernel_fanout_carrier_dryrun_status":
            assert tool["annotations"]["readOnlyHint"] is True


def test_kernel_fanout_dryrun_status_tool_call_is_read_only(tmp_path):
    _seed_root(tmp_path)
    _seed_fanout_dryrun_status_artifacts(tmp_path)
    response = handle_mcp_jsonrpc(
        tmp_path,
        {
            "jsonrpc": "2.0",
            "id": 230,
            "method": "tools/call",
            "params": {"name": "ion_kernel_fanout_carrier_dryrun_status", "arguments": {}},
        },
    )

    result = response["result"]
    assert result["isError"] is False
    structured = result["structuredContent"]
    assert structured["ok"] is True
    assert structured["mutates_active_state"] is False
    data = structured["data"]
    assert data["schema_id"] == "ion.kernel_fanout_carrier_dryrun_status.v1"
    assert data["timeout_fail_closed_summary"]["fail_closed"] is True
    assert data["conflict_lock_summary"]["conflict_deferral_events"] == 5


def test_jsonrpc_tools_list_shape():
    response = handle_mcp_jsonrpc(Path.cwd(), {"jsonrpc": "2.0", "id": 1, "method": "tools/list"})

    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 1
    assert any(tool["name"] == "ion_status" for tool in response["result"]["tools"])


def test_status_tool_call_works_without_write_confirmation():
    response = handle_mcp_jsonrpc(
        Path.cwd(),
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "ion_status", "arguments": {}}},
    )

    result = response["result"]
    assert result["isError"] is False
    assert result["structuredContent"]["ok"] is True
    assert result["structuredContent"]["data"]["schema_id"] == "ion.status.v1"


def test_worker_live_status_tool_call_exposes_lifecycle_events(tmp_path):
    _seed_root(tmp_path)
    run_rel = "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_lifecycle/run.json"
    run_path = tmp_path / run_rel
    run_path.parent.mkdir(parents=True, exist_ok=True)
    run_path.write_text(
        """
{
  "schema_id": "ion.codex_queue_runner_run.v1",
  "run_id": "run_lifecycle",
  "request_id": "req_lifecycle",
  "request_path": "ION/05_context/current/chatgpt_connector/codex_work_requests/req_lifecycle.json",
  "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_lifecycle/run.json",
  "run_dir": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_lifecycle",
  "status": "RETURN_RECORDED_PROOF_ACCEPTED",
  "started_at": "2026-05-10T17:00:00+00:00",
  "completed_at": "2026-05-10T17:01:00+00:00",
  "submit_result": {
    "accepted_for_carrier_intake": true,
    "context_proof_accepted": true,
    "template_action_proof_accepted": true,
    "packet_path": "ION/05_context/current/chatgpt_connector/task_returns/return_lifecycle.json"
  },
  "worker_lifecycle_events": [
    {
      "event": "worker_boot",
      "at": "2026-05-10T17:00:01+00:00",
      "run_id": "run_lifecycle",
      "request_id": "req_lifecycle",
      "status": "CODEX_CLI_RUNNING",
      "pid": 123,
      "production_authority": false,
      "live_execution_authority": false
    },
    {
      "event": "worker_terminal",
      "at": "2026-05-10T17:01:00+00:00",
      "run_id": "run_lifecycle",
      "request_id": "req_lifecycle",
      "status": "RETURN_RECORDED_PROOF_ACCEPTED",
      "pid": 123,
      "terminal_state": "accepted",
      "context_proof_accepted": true,
      "template_action_proof_accepted": true,
      "production_authority": false,
      "live_execution_authority": false
    }
  ]
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        f'{{"schema_id":"ion.codex_queue_runner_state.v1","active_run":null,"latest_run":"{run_rel}","production_authority":false,"live_execution_authority":false}}\n',
        encoding="utf-8",
    )

    response = handle_mcp_jsonrpc(
        tmp_path,
        {
            "jsonrpc": "2.0",
            "id": 22,
            "method": "tools/call",
            "params": {"name": "ion_codex_worker_live_status", "arguments": {}},
        },
    )

    telemetry = response["result"]["structuredContent"]["data"]["live_worker_telemetry"]
    assert response["result"]["isError"] is False
    assert telemetry["latest_worker_lifecycle_event"]["event"] == "worker_terminal"
    assert telemetry["worker_lifecycle_events"][0]["event"] == "worker_boot"


def test_read_tool_call_works_without_write_confirmation(tmp_path):
    _seed_root(tmp_path)
    target = tmp_path / "ION/02_architecture/NOTE.md"
    target.parent.mkdir(parents=True)
    target.write_text("browser read smoke\n", encoding="utf-8")
    response = handle_mcp_jsonrpc(
        tmp_path,
        {
            "jsonrpc": "2.0",
            "id": 21,
            "method": "tools/call",
            "params": {"name": "ion_file_read", "arguments": {"path": "ION/02_architecture/NOTE.md"}},
        },
    )

    result = response["result"]
    assert result["isError"] is False
    assert result["structuredContent"]["ok"] is True
    assert "browser read smoke" in result["structuredContent"]["data"]["text"]


def test_carrier_onboarding_tool_call_works_without_write_confirmation():
    response = handle_mcp_jsonrpc(
        Path.cwd(),
        {
            "jsonrpc": "2.0",
            "id": 20,
            "method": "tools/call",
            "params": {"name": "ion_carrier_onboarding_packet", "arguments": {"carrier": "chatgpt_browser"}},
        },
    )

    result = response["result"]
    assert result["isError"] is False
    assert result["structuredContent"]["ok"] is True
    assert result["structuredContent"]["data"]["schema_id"] == "ion.carrier_onboarding_packet.v1"
    assert result["structuredContent"]["data"]["root_markdown_onboarding_authority"] is False


def test_bounded_write_tool_requires_confirmation(tmp_path):
    _seed_root(tmp_path)
    response = handle_mcp_jsonrpc(
        tmp_path,
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "ion_queue_operator_message", "arguments": {"message": "queue without confirmation"}},
        },
    )

    result = response["result"]
    assert result["isError"] is True
    assert result["structuredContent"]["finding"] == "bounded_write_confirmation_required"
    assert not (tmp_path / "ION/05_context/current/ACTIVE_OPERATOR_MESSAGE_QUEUE.json").exists()


def test_bounded_write_tool_with_confirmation_writes_only_queue(tmp_path):
    _seed_root(tmp_path)
    response = handle_mcp_jsonrpc(
        tmp_path,
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "ion_queue_operator_message",
                "arguments": {
                    "message": "queue with confirmation",
                    "priority": 60,
                    "confirmation": WRITE_CONFIRMATION_TOKEN,
                },
            },
        },
    )

    queue = tmp_path / "ION/05_context/current/ACTIVE_OPERATOR_MESSAGE_QUEUE.json"
    result = response["result"]
    assert result["isError"] is False
    assert result["structuredContent"]["ok"] is True
    assert queue.exists()
    assert "queue with confirmation" in queue.read_text(encoding="utf-8")


def test_forbidden_tool_is_blocked_even_with_confirmation():
    response = handle_mcp_jsonrpc(
        Path.cwd(),
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "arbitrary_shell", "arguments": {"confirmation": WRITE_CONFIRMATION_TOKEN}},
        },
    )

    result = response["result"]
    assert result["isError"] is True
    assert result["structuredContent"]["finding"] == "forbidden_capability"


def test_write_http_preview_audit(tmp_path):
    output = tmp_path / "CHATGPT_BROWSER_HTTP_MCP_PREVIEW_V121.json"

    result = write_http_mcp_preview_audit(Path.cwd(), output=output)

    assert output.exists()
    assert result["verdict"] == READY_VERDICT
    assert result["write_confirmation_required"] is True


def test_connector_landing_page_is_safe_human_ui():
    html = render_ion_connector_landing(Path.cwd(), public_base_url="https://ion.example.test")

    assert "<title>ION Connector</title>" in html
    assert "https://ion.example.test/mcp" in html
    assert "https://ion.example.test/cockpit" in html
    assert "https://ion.example.test/cockpit/chat" in html
    assert "https://ion.example.test/cockpit/worker" in html
    assert "https://ion.example.test/projects" in html
    assert "Projects Hub" in html
    assert "127.0.0.1:8788" in html
    assert "Cosmos Water World" in html
    assert "https://ion.example.test/projects/cosmos" in html
    assert "https://ion-operations.github.io/Cosmos/" not in html
    assert "https://ion.example.test/app/status.json" in html
    assert "HelixION route directory" in html
    assert "HELIXION" in html
    assert "ION_STATUS_READY" not in html
    assert "production_authority" not in html
    assert "Production authority" in html
    assert "ion_status" in html
    assert "arbitrary_shell" in html
    assert "/home/sev" not in html


def test_connector_landing_paths_include_root_app_ion_and_projects():
    assert {"/", "/app", "/ion", "/projects"} <= APP_PATHS


def test_project_workbench_renders_same_origin_cosmos_preview(monkeypatch, tmp_path):
    cosmos = tmp_path / "cosmos"
    cosmos.mkdir()
    (cosmos / "package.json").write_text('{"scripts":{"build":"vite build"}}\n', encoding="utf-8")
    monkeypatch.setenv("ION_COSMOS_PROJECT_ROOT", cosmos.as_posix())

    html = render_project_workbench_html(tmp_path, public_base_url="https://ion.example.test")
    auth_html = render_project_workbench_html(
        tmp_path,
        public_base_url="https://ion.example.test",
        authenticated=True,
        auth_token="test-token",
    )

    assert "<title>Helixion Projects - Cosmos Workbench</title>" in html
    assert 'src="/projects/cosmos/preview/"' in html
    assert 'href="/projects/cosmos/preview/cosmos-review?bookmark=orbit&amp;panel=1"' in html
    assert 'href="/projects/cosmos/preview/cosmos-review?bookmark=cloud-terminator&amp;panel=1"' in html
    assert 'href="/projects/cosmos/preview/cosmos-review?bookmark=high-altitude&amp;panel=1"' in html
    assert "Browser capture orbit" in auth_html
    assert "Browser Captures" in html
    assert "Login to run builds" in html
    assert "https://ion-operations.github.io/Cosmos/" not in html


def test_project_preview_route_proxies_local_cosmos_server(monkeypatch, tmp_path):
    class FakeCosmosHandler(BaseHTTPRequestHandler):
        def log_message(self, _fmt, *_args):
            return None

        def do_GET(self):  # noqa: N802
            body = f"cosmos-proxy:{self.path}".encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    cosmos = tmp_path / "cosmos"
    cosmos.mkdir()
    monkeypatch.setenv("ION_COSMOS_PROJECT_ROOT", cosmos.as_posix())
    fake_server = ThreadingHTTPServer(("127.0.0.1", 0), FakeCosmosHandler)
    fake_port = fake_server.server_address[1]
    monkeypatch.setenv("ION_COSMOS_PREVIEW_PORT", str(fake_port))
    fake_thread = Thread(target=fake_server.serve_forever, daemon=True)
    fake_thread.start()

    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        url = f"http://127.0.0.1:{preview_server.server_address[1]}/projects/cosmos/preview/cosmos-review?bookmark=orbit"
        with urllib.request.urlopen(url, timeout=5) as response:
            body = response.read().decode("utf-8")
        assert body == "cosmos-proxy:/projects/cosmos/preview/cosmos-review?bookmark=orbit"
    finally:
        preview_server.shutdown()
        fake_server.shutdown()


def test_codex_worker_live_status_page_is_bounded_polling_ui():
    html = render_codex_worker_live_status_html(Path.cwd(), auth_token="test-token")

    assert "<title>ION Codex Worker</title>" in html
    assert "Worker Command Center" in html
    assert "/cockpit/worker/model.json?token=test-token" in html
    assert "/cockpit/chat?token=test-token" in html
    assert "/cockpit?token=test-token" in html
    assert "setInterval(poll, 5000)" in html
    assert "Filter and Sort" in html
    assert "Active Worker" in html
    assert "Latest Worker Runs" in html
    assert "Machine Sign-In" in html
    assert "Receipt Chain Matrix" in html
    assert "Model Move Summary" in html
    assert "Proof Gate" in html
    assert "Fan-Out Telemetry" in html
    assert "Supabase Event Links" in html
    assert "Settlement Blockers" in html
    assert "Mutation controls disabled unless explicit bounded authority is present." in html
    assert "Queue Mutation (disabled)" in html
    assert "Worker Kill (disabled)" in html
    assert "Retry/Replay (disabled)" in html
    assert "model private reasoning" not in html
    assert "/home/sev" not in html


def test_codex_worker_live_status_page_renders_template_invalid_and_deferred_settlement(tmp_path):
    _seed_root(tmp_path)
    _seed_worker_cockpit_artifacts(tmp_path)

    html = render_codex_worker_live_status_html(tmp_path, auth_token="tok")

    assert "template-invalid" in html
    assert "RETURN_TEMPLATE_INVALID" in html
    assert "DEFERRED_ENVIRONMENT_BLOCKED" in html
    assert "worker_cockpit_joc_ui_upgrade_requirement_added" in html
    assert "required context" in html
    assert "all statuses" in html
    assert "setInterval(poll, 5000)" in html


def test_helixion_site_bar_marks_active_and_preserves_token():
    html = render_helixion_site_bar("chat", auth_token="abc123")

    assert 'aria-label="HelixION site pages"' in html
    assert 'href="/projects"' in html
    assert 'href="/cockpit/chat?token=abc123"' in html
    assert 'href="/cockpit/worker?token=abc123"' in html
    assert 'aria-current="page"' in html


def test_wrap_helixion_site_shell_adds_bar_to_existing_page():
    html = wrap_helixion_site_shell(
        "<html><head><style>body{}</style></head><body><main>page</main></body></html>",
        "cockpit",
        auth_token="abc123",
    )

    assert "helix-sitebar" in html
    assert 'href="/projects"' in html
    assert 'href="/cockpit?token=abc123"' in html
    assert "body{}" in html
    assert "<main>page</main>" in html


def test_public_cockpit_csp_allows_bundled_chat_script():
    class DummyHandler:
        headers = {}
        sent_headers: dict[str, str] = {}

        def send_response(self, _status):
            return None

        def send_header(self, key, value):
            self.sent_headers[key] = value

        def end_headers(self):
            return None

        @property
        def wfile(self):
            class Writer:
                def write(self, _body):
                    return None

            return Writer()

    handler = DummyHandler()
    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    IonChatGPTPreviewHandler._send_html(handler, 200, "<html></html>")

    csp = handler.sent_headers["Content-Security-Policy"]
    assert "script-src 'unsafe-inline'" in csp
    assert "connect-src 'self'" in csp
    assert "frame-src 'self'" in csp


def test_public_cockpit_login_renders_token_and_google_controls():
    html = render_public_cockpit_login(
        next_path="/cockpit/chat",
        env={
            "ION_COCKPIT_PUBLIC_TOKEN": "abc123-private-token",
            "ION_GOOGLE_OAUTH_CLIENT_ID": "client",
            "ION_GOOGLE_OAUTH_CLIENT_SECRET": "secret",
            "ION_COCKPIT_ALLOWED_GOOGLE_EMAILS": "sev@example.com",
        },
    )

    assert "<title>ION Cockpit Login</title>" in html
    assert "/cockpit/auth/token" in html
    assert "/cockpit/auth/google/start" in html
    assert "Continue with Google" in html
    assert "Allowed Google emails: 1" in html
    assert "ION_COCKPIT_ALLOWED_GOOGLE_EMAILS" in html
    assert "abc123-private-token" not in html


def test_public_cockpit_login_explains_google_oauth_setup_gap():
    html = render_public_cockpit_login(
        next_path="/cockpit/chat",
        env={
            "ION_COCKPIT_PUBLIC_TOKEN": "abc123-private-token",
            "ION_COCKPIT_ALLOWED_GOOGLE_EMAILS": "crinkedart@gmail.com",
        },
    )

    assert "Google OAuth setup needed" in html
    assert "Allowed Google emails already listed: 1" in html
    assert "crinkedart@gmail.com" not in html


def test_public_cockpit_login_translates_google_state_error():
    html = render_public_cockpit_login(
        next_path="/cockpit/chat",
        finding="google_oauth_state_missing_or_invalid",
        env={"ION_COCKPIT_PUBLIC_TOKEN": "abc123-private-token"},
    )

    assert "Google login is not enabled yet. Use the permission token for now." in html
    assert "google_oauth_state_missing_or_invalid" not in html
