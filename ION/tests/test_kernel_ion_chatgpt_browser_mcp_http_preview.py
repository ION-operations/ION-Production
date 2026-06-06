import json
import shutil
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
import urllib.error
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
    render_helixion_project_family_detail,
    render_ion_connector_landing,
    render_project_workbench_html,
    render_public_cockpit_login,
    wrap_helixion_site_shell,
    write_http_mcp_preview_audit,
)
from kernel.ion_dual_codex_chat import WRITE_CONFIRMATION_TOKEN

PUBLIC_ARCHIVE_SESSION_ID = "dddddddd-eeee-ffff-1111-222222222222"


def _seed_root(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").parent.mkdir(parents=True)
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")


def _seed_project_portfolio(root: Path) -> None:
    manifest = {
        "schema_id": "ion.project_portfolio.v1",
        "generated_at": "2026-06-02T00:00:00Z",
        "summary": {
            "project_root_count": 2,
            "family_count": 1,
            "canonical_domain_count": 1,
            "launchable_count": 1,
            "documentation_surface_count": 1,
            "project_os_ready_count": 1,
            "project_os_watch_count": 0,
            "project_os_blocked_count": 0,
        },
        "canonical_domains": [
            {
                "domain_id": "water-simulation",
                "label": "Water Simulation",
                "summary": "Ocean and water projects.",
                "sort_order": 1,
                "project_count": 1,
                "version_count": 2,
                "family_count": 1,
                "launchable_count": 1,
                "doc_count": 1,
                "diff_count": 1,
                "operating_system": {"posture": "ready", "average_readiness_score": 82, "ready_count": 1},
            }
        ],
        "families": [
            {
                "family_id": "cosmos:hyper-h2o",
                "domain_id": "water-simulation",
                "label": "Hyper H2O",
                "current_path": "/home/sev/ION - Production/ION_Developement/Cosmos/hyper-h2o-v002",
                "project_count": 2,
                "version_count": 2,
                "branch_count": 1,
                "diff_count": 1,
                "doc_count": 1,
                "launchable_count": 1,
                "source_ids": ["cosmos"],
                "lineage_status": "version_chain_ready",
                "operating_system": {
                    "posture": "ready",
                    "readiness_score": 82,
                    "maintenance_lanes": [
                        {
                            "lane_id": "quality_proof",
                            "label": "Quality Proof",
                            "objective": "Keep visual proof attached.",
                            "status": "watch",
                            "next_action": "/home/sev/ION - Production/ION_Developement/Cosmos/hyper-h2o-v002",
                        }
                    ],
                },
                "diffs": [
                    {
                        "diff_id": "001_v001_to_v002",
                        "manifest_path": "/home/sev/ION_PROJECTS_PROFESSIONAL_ORGANIZED_CANDIDATE/domains/water/hyper/DIFF_MANIFEST.json",
                        "from_project_id": "cosmos:hyper-h2o-v001",
                        "to_project_id": "cosmos:hyper-h2o-v002",
                        "from_label": "Hyper H2O v001",
                        "to_label": "Hyper H2O v002",
                        "status": "candidate_diff_manifest",
                        "file_diff": {
                            "added_count": 3,
                            "changed_count": 2,
                            "removed_count": 1,
                            "changed_sample": ["src/water.ts", "README.md"],
                        },
                    }
                ],
                "versions": [
                    {
                        "version_id": "001-v001",
                        "project_id": "cosmos:hyper-h2o-v001",
                        "display_label": "Hyper H2O v001",
                        "sequence_label": "v001",
                        "path": "/home/sev/ION - Production/ION_Developement/Cosmos/hyper-h2o-v001",
                        "stack": "vite",
                        "launchable": False,
                        "is_current": False,
                        "docs": {"docs": []},
                    },
                    {
                        "version_id": "002-v002",
                        "project_id": "cosmos:hyper-h2o-v002",
                        "display_label": "Hyper H2O v002",
                        "sequence_label": "v002",
                        "path": "/home/sev/ION - Production/ION_Developement/Cosmos/hyper-h2o-v002",
                        "stack": "vite",
                        "launchable": True,
                        "is_current": True,
                        "launch": {"framework": "vite", "mode": "managed_local_dev_server"},
                        "docs": {
                            "doc_count": 1,
                            "docs": [
                                {
                                    "title": "Hyper H2O README",
                                    "rel_path": "README.md",
                                    "path": "/home/sev/ION - Production/ION_Developement/Cosmos/hyper-h2o-v002/README.md",
                                    "kind": "readme",
                                    "extension": ".md",
                                    "primary": True,
                                }
                            ],
                        },
                    },
                ],
            }
        ],
    }
    path = root / "ION/05_context/current/project_portfolio/PROJECT_PORTFOLIO_MANIFEST.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _seed_branch_registry(root: Path) -> None:
    registry_source = Path.cwd() / "ION/03_registry/ion_action_mcp_branch_leader_registry.yaml"
    registry_target = root / "ION/03_registry/ion_action_mcp_branch_leader_registry.yaml"
    registry_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(registry_source, registry_target)
    (root / "ION/03_registry/boots").mkdir(parents=True, exist_ok=True)
    (root / "ION/04_packages/kernel").mkdir(parents=True, exist_ok=True)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def _seed_codex_home(root: Path) -> Path:
    codex_home = root / "codex-home"
    _write_jsonl(codex_home / "session_index.jsonl", [{"id": PUBLIC_ARCHIVE_SESSION_ID, "thread_name": "Public archive"}])
    _write_jsonl(codex_home / "history.jsonl", [{"session_id": PUBLIC_ARCHIVE_SESSION_ID, "text": "public archive smoke"}])
    _write_jsonl(
        codex_home / f"sessions/2026/05/23/rollout-{PUBLIC_ARCHIVE_SESSION_ID}.jsonl",
        [
            {"type": "session_meta", "timestamp": "2026-05-23T12:00:00+00:00", "payload": {"id": PUBLIC_ARCHIVE_SESSION_ID}},
            {"type": "event_msg", "timestamp": "2026-05-23T12:01:00+00:00", "payload": {"type": "user_message", "message": "public archive smoke"}},
        ],
    )
    return codex_home


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
    assert "ion_codex_worker_trace" in names
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
    project_patch_apply_schema = next(tool["inputSchema"] for tool in tools if tool["name"] == "ion_project_patch_apply")
    assert {"agent_id", "lease_id"}.issubset(set(project_patch_apply_schema["required"]))
    assert project_patch_apply_schema["properties"]["lease_id"]["type"] == "string"
    bounded_patch_apply_schema = next(tool["inputSchema"] for tool in tools if tool["name"] == "ion_bounded_patch_apply")
    assert {"confirmation", "agent_id", "lease_id"}.issubset(set(bounded_patch_apply_schema["required"]))
    assert bounded_patch_apply_schema["properties"]["agent_id"]["type"] == "string"
    file_put_text_schema = next(tool["inputSchema"] for tool in tools if tool["name"] == "ion_file_put_text")
    assert "agent_id" in file_put_text_schema["properties"]
    assert "lease_id" in file_put_text_schema["properties"]
    assert "agent_id" not in file_put_text_schema["required"]
    upload_init_schema = next(tool["inputSchema"] for tool in tools if tool["name"] == "ion_artifact_upload_init")
    assert "agent_id" in upload_init_schema["properties"]
    assert "lease_id" in upload_init_schema["properties"]
    upload_commit_schema = next(tool["inputSchema"] for tool in tools if tool["name"] == "ion_artifact_upload_commit")
    assert "agent_id" in upload_commit_schema["properties"]
    assert "lease_id" in upload_commit_schema["properties"]
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
    request_tool = next(tool for tool in tools if tool["name"] == "ion_request_codex_work_packet")
    request_properties = request_tool["inputSchema"]["properties"]
    assert "codex_model_override" in request_properties
    assert "requested_model" in request_properties
    assert "requested_reasoning_effort" in request_properties
    assert "model_override_reason" in request_properties
    assert "project_hash" in request_properties
    assert "selected_model" in request_properties["codex_model_override"]["properties"]
    assert "selected_reasoning_effort" in request_properties["codex_model_override"]["properties"]


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
    assert "Main ION Project System" in html
    assert "Project canon" in html
    assert "Project Curator" in html
    assert "Context Librarian" in html
    assert "Timeline Axes" in html
    assert "Future Lanes" in html
    assert "/projects/portfolio.json" in html
    assert "/projects/family/" in html
    assert "ion://workspace" in html
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


def test_projects_route_renders_main_helixion_app_not_cosmos_workbench(tmp_path):
    _seed_root(tmp_path)
    _seed_project_portfolio(tmp_path)
    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()

    try:
        base = f"http://127.0.0.1:{preview_server.server_address[1]}"
        with urllib.request.urlopen(f"{base}/projects", timeout=5) as response:
            html = response.read().decode("utf-8")

        assert "Main ION Project System" in html
        assert "Project canon" in html
        assert "/projects/family/cosmos%3Ahyper-h2o" in html
        assert "Helixion Projects - Cosmos Workbench" not in html
        assert 'src="/projects/cosmos/preview/"' not in html
        assert "/home/sev" not in html
    finally:
        preview_server.shutdown()
        preview_server.server_close()
        preview_thread.join(timeout=5)


def test_project_family_detail_renderer_redacts_paths(tmp_path):
    _seed_root(tmp_path)
    _seed_project_portfolio(tmp_path)

    html = render_helixion_project_family_detail(tmp_path, "cosmos:hyper-h2o", public_base_url="https://ion.example.test")

    assert "<title>Project Family - Hyper H2O</title>" in html
    assert "Advanced Preview" in html
    assert "Version Timeline" in html
    assert "Diff Evolution" in html
    assert "Proof Ladder" in html
    assert "Context Capsule" in html
    assert "managed_launch" in html
    assert "/cockpit#projects" in html
    assert "src/water.ts" in html
    assert "Helixion Projects - Cosmos Workbench" not in html
    assert "/home/sev" not in html


def test_project_family_detail_routes_html_and_json(tmp_path):
    _seed_root(tmp_path)
    _seed_project_portfolio(tmp_path)
    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()

    try:
        base = f"http://127.0.0.1:{preview_server.server_address[1]}"
        with urllib.request.urlopen(f"{base}/projects/family/cosmos%3Ahyper-h2o", timeout=5) as response:
            html = response.read().decode("utf-8")
        with urllib.request.urlopen(f"{base}/projects/family/cosmos%3Ahyper-h2o.json", timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert "Project Family command center" in html
        assert "Version Timeline" in html
        assert "Diff Evolution" in html
        assert "Helixion Projects - Cosmos Workbench" not in html
        assert "/home/sev" not in html
        assert payload["schema_id"] == "ion.helixion_project_family_detail.v0_1"
        assert payload["family"]["family_id"] == "cosmos:hyper-h2o"
        assert payload["preview_capability"]["capability"] == "managed_launch"
        assert payload["diffs"][0]["changed_count"] == 2
        assert "/home/sev" not in json.dumps(payload, sort_keys=True)
    finally:
        preview_server.shutdown()
        preview_server.server_close()
        preview_thread.join(timeout=5)


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
    assert 'href="/projects/cosmos/preview/projects"' in html
    assert 'href="/projects/cosmos/preview/projects/application-dev"' in html
    assert "Application Dev" in html
    assert "http://127.0.0.1:5199/" in html
    assert 'href="/projects/cosmos/preview/cosmos-review?bookmark=orbit&amp;panel=1"' in html
    assert 'href="/projects/cosmos/preview/cosmos-review?bookmark=cloud-terminator&amp;panel=1"' in html
    assert 'href="/projects/cosmos/preview/cosmos-review?bookmark=high-altitude&amp;panel=1"' in html
    assert "Browser capture orbit" in auth_html
    assert "public_token" not in auth_html
    assert "?token=" not in auth_html
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


def test_application_dev_catalog_route_proxies_local_launcher(monkeypatch, tmp_path):
    class FakeLauncherHandler(BaseHTTPRequestHandler):
        def log_message(self, _fmt, *_args):
            return None

        def do_GET(self):  # noqa: N802
            assert self.path == "/apps.json"
            body = b'{"summary":{"count":1,"launchable":1,"needsInstall":0,"byFamily":{"ProFlow":1}},"apps":[]}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    fake_server = ThreadingHTTPServer(("127.0.0.1", 0), FakeLauncherHandler)
    fake_port = fake_server.server_address[1]
    monkeypatch.setenv("ION_APPLICATION_DEV_LAUNCHER_URL", f"http://127.0.0.1:{fake_port}")
    fake_thread = Thread(target=fake_server.serve_forever, daemon=True)
    fake_thread.start()

    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        url = f"http://127.0.0.1:{preview_server.server_address[1]}/projects/application-dev/apps.json"
        with urllib.request.urlopen(url, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        assert payload["summary"]["count"] == 1
        assert payload["summary"]["byFamily"]["ProFlow"] == 1
    finally:
        preview_server.shutdown()
        fake_server.shutdown()


def test_public_mcp_requires_auth_and_accepts_bearer_token(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    monkeypatch.setenv("ION_COCKPIT_PUBLIC_TOKEN", "test-token")

    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        base = f"http://127.0.0.1:{preview_server.server_address[1]}"
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).encode("utf-8")
        denied = urllib.request.Request(
            f"{base}/mcp",
            data=body,
            headers={"Host": "ion.example.test", "Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(denied, timeout=5)
            raise AssertionError("unauthenticated public /mcp should not return 200")
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read().decode("utf-8"))
            assert exc.code == 401
            assert payload["finding"] == "public_cockpit_login_required"

        allowed = urllib.request.Request(
            f"{base}/mcp",
            data=body,
            headers={
                "Host": "ion.example.test",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer test-token",
            },
            method="POST",
        )
        with urllib.request.urlopen(allowed, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        assert payload["jsonrpc"] == "2.0"
        assert payload["result"]["tools"]

        query_token = urllib.request.Request(
            f"{base}/mcp?token=test-token",
            data=body,
            headers={"Host": "ion.example.test", "Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            urllib.request.urlopen(query_token, timeout=5)
            raise AssertionError("query token public /mcp should not return 200")
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read().decode("utf-8"))
            assert exc.code == 401
            assert payload["finding"] == "public_cockpit_login_required"
    finally:
        preview_server.shutdown()


def test_public_project_model_and_preview_require_auth_on_public_host(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    monkeypatch.setenv("ION_COCKPIT_PUBLIC_TOKEN", "test-token")

    from kernel import ion_chatgpt_browser_mcp_http_preview as preview
    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    monkeypatch.setattr(
        preview,
        "build_project_workspace_status",
        lambda root, project_id="cosmos", probe_preview=True: {
            "ok": True,
            "project_id": project_id,
            "probe_preview": probe_preview,
            "production_authority": False,
            "live_execution_authority": False,
        },
    )
    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        base = f"http://127.0.0.1:{preview_server.server_address[1]}"
        for path in ("/projects/cosmos/model.json", "/projects/cosmos/preview/cosmos-review?bookmark=orbit"):
            request = urllib.request.Request(
                f"{base}{path}",
                headers={"Host": "ion.example.test", "Accept": "application/json"},
            )
            try:
                urllib.request.urlopen(request, timeout=5)
                raise AssertionError(f"unauthenticated public {path} should not return 200")
            except urllib.error.HTTPError as exc:
                payload = json.loads(exc.read().decode("utf-8"))
                assert exc.code == 401
                assert payload["finding"] == "public_cockpit_login_required"

        allowed = urllib.request.Request(
            f"{base}/projects/cosmos/model.json",
            headers={"Host": "ion.example.test", "Accept": "application/json", "Authorization": "Bearer test-token"},
        )
        with urllib.request.urlopen(allowed, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        assert payload["ok"] is True
        assert payload["project_id"] == "cosmos"

        query_token = urllib.request.Request(
            f"{base}/projects/cosmos/model.json?token=test-token",
            headers={"Host": "ion.example.test", "Accept": "application/json"},
        )
        try:
            urllib.request.urlopen(query_token, timeout=5)
            raise AssertionError("query token public project model should not return 200")
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read().decode("utf-8"))
            assert exc.code == 401
            assert payload["finding"] == "public_cockpit_login_required"
    finally:
        preview_server.shutdown()


def test_public_preview_sessions_model_requires_auth_and_accepts_bearer(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    monkeypatch.setenv("ION_COCKPIT_PUBLIC_TOKEN", "test-token")

    from kernel import ion_chatgpt_browser_mcp_http_preview as preview
    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    expected_comparisons = [
        {
            "comparison_id": "cmp-public-local-remote-current",
            "pair_basis": "project",
            "baseline_preview_id": "public-local-current",
            "candidate_preview_id": "public-remote-current",
            "surface_pair": "local_host_to_remote_host",
            "route": "/cockpit/previews/compare/cmp-public-local-remote-current",
            "status": "registered_read_only",
        }
    ]
    expected_surface_matrix = {
        "schema_id": "ion.project_preview_surface_matrix.v0_1",
        "comparison_count": 1,
        "session_counts_by_location": {"local_host": 1, "remote_host": 1},
        "session_counts_by_provider": {"vite": 2},
    }

    monkeypatch.setattr(
        preview,
        "build_project_preview_sessions_model",
        lambda root: {
            "schema_id": "ion.project_preview_sessions.v0_1",
            "ok": True,
            "sessions": [
                {"preview_id": "public-local-current", "runner_location": "local_host", "provider": "vite"},
                {"preview_id": "public-remote-current", "runner_location": "remote_host", "provider": "vite"},
            ],
            "comparisons": expected_comparisons,
            "surface_matrix": expected_surface_matrix,
            "authority": {"preview_read": True, "preview_mutation": False},
        },
    )
    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        base = f"http://127.0.0.1:{preview_server.server_address[1]}"
        unauthenticated = urllib.request.Request(
            f"{base}/cockpit/previews/model.json",
            headers={"Host": "ion.example.test", "Accept": "application/json"},
        )
        try:
            urllib.request.urlopen(unauthenticated, timeout=5)
            raise AssertionError("unauthenticated preview sessions model should not return 200")
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read().decode("utf-8"))
            assert exc.code == 401
            assert payload["finding"] == "public_cockpit_login_required"

        allowed = urllib.request.Request(
            f"{base}/cockpit/previews/model.json",
            headers={"Host": "ion.example.test", "Accept": "application/json", "Authorization": "Bearer test-token"},
        )
        with urllib.request.urlopen(allowed, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert payload["schema_id"] == "ion.project_preview_sessions.v0_1"
        assert payload["ok"] is True
        assert payload["comparisons"] == expected_comparisons
        assert payload["surface_matrix"] == expected_surface_matrix
        assert payload["authority"]["preview_mutation"] is False

        query_token = urllib.request.Request(
            f"{base}/cockpit/previews/model.json?token=test-token",
            headers={"Host": "ion.example.test", "Accept": "application/json"},
        )
        try:
            urllib.request.urlopen(query_token, timeout=5)
            raise AssertionError("query token preview sessions model should not return 200")
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read().decode("utf-8"))
            assert exc.code == 401
            assert payload["finding"] == "public_cockpit_login_required"
    finally:
        preview_server.shutdown()


def test_public_mutation_routes_require_same_origin_evidence(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    monkeypatch.setenv("ION_COCKPIT_PUBLIC_TOKEN", "test-token")
    calls: list[dict] = []

    from kernel import ion_chatgpt_browser_mcp_http_preview as preview
    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    def fake_project_action_run(root: Path, payload: dict):
        calls.append({"root": Path(root), "payload": dict(payload)})
        return {
            "ok": True,
            "tool": "ion_project_action_run",
            "data": {"action_id": payload.get("action_id"), "returncode": 0},
            "production_authority": False,
            "live_execution_authority": False,
        }

    monkeypatch.setattr(preview, "project_action_run", fake_project_action_run)
    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        base = f"http://127.0.0.1:{preview_server.server_address[1]}"
        body = json.dumps({"confirmation": "ION_BOUNDED_PROJECT_WRITE_CONFIRMED", "action_id": "test"}).encode("utf-8")
        missing_origin = urllib.request.Request(
            f"{base}/projects/cosmos/actions/run",
            data=body,
            headers={
                "Host": "ion.example.test",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer test-token",
            },
            method="POST",
        )
        try:
            urllib.request.urlopen(missing_origin, timeout=5)
            raise AssertionError("missing-origin public mutation should not return 200")
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read().decode("utf-8"))
            assert exc.code == 403
            assert payload["finding"] == "same_origin_required"

        cross_origin = urllib.request.Request(
            f"{base}/projects/cosmos/actions/run",
            data=body,
            headers={
                "Host": "ion.example.test",
                "Origin": "https://attacker.example",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer test-token",
            },
            method="POST",
        )
        try:
            urllib.request.urlopen(cross_origin, timeout=5)
            raise AssertionError("cross-origin public mutation should not return 200")
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read().decode("utf-8"))
            assert exc.code == 403
            assert payload["finding"] == "origin_not_allowed"

        same_origin = urllib.request.Request(
            f"{base}/projects/cosmos/actions/run",
            data=body,
            headers={
                "Host": "ion.example.test",
                "Origin": "https://ion.example.test",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer test-token",
            },
            method="POST",
        )
        with urllib.request.urlopen(same_origin, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        assert payload["ok"] is True
        assert calls == [{"root": tmp_path, "payload": {"confirmation": "ION_BOUNDED_PROJECT_WRITE_CONFIRMED", "action_id": "test", "project_id": "cosmos"}}]
    finally:
        preview_server.shutdown()


def test_public_health_is_minimal_and_app_status_requires_auth(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    monkeypatch.setenv("ION_COCKPIT_PUBLIC_TOKEN", "test-token")

    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        base = f"http://127.0.0.1:{preview_server.server_address[1]}"
        health = urllib.request.Request(
            f"{base}/health",
            headers={"Host": "ion.example.test", "Accept": "application/json"},
        )
        with urllib.request.urlopen(health, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        assert payload["ok"] is True
        assert payload["status"] == "ready"
        assert "shell_root" not in payload
        assert "allowed_tools" not in payload

        status = urllib.request.Request(
            f"{base}/app/status.json",
            headers={"Host": "ion.example.test", "Accept": "application/json"},
        )
        try:
            urllib.request.urlopen(status, timeout=5)
            raise AssertionError("unauthenticated public /app/status.json should not return 200")
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read().decode("utf-8"))
            assert exc.code == 401
            assert payload["finding"] == "public_cockpit_login_required"
    finally:
        preview_server.shutdown()


def test_browser_gpt_screen_automation_routes_are_same_origin_cockpit_actions(monkeypatch, tmp_path):
    _seed_root(tmp_path)

    from kernel import ion_chatgpt_browser_mcp_http_preview as preview
    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    monkeypatch.setattr(preview, "build_screen_automation_status", lambda root: {
        "schema_id": "ion.browser_gpt_screen_automation_status.v1",
        "ok": True,
        "status": "ready",
        "root": Path(root).as_posix(),
    })
    monkeypatch.setattr(preview, "execute_extension_reload", lambda root, dry_run=True: {
        "schema_id": "ion.browser_gpt_screen_automation_status.v1",
        "ok": True,
        "finding": "extension_reload_executed" if not dry_run else "extension_reload_planned",
        "dry_run": dry_run,
    })

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        base = f"http://127.0.0.1:{preview_server.server_address[1]}"
        with urllib.request.urlopen(f"{base}/cockpit/browser-gpt/screen-automation/status", timeout=5) as response:
            status_payload = json.loads(response.read().decode("utf-8"))
        assert status_payload["status"] == "ready"

        request = urllib.request.Request(
            f"{base}/cockpit/browser-gpt/screen-automation/reload-extension",
            data=json.dumps({"execute": True}).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            reload_payload = json.loads(response.read().decode("utf-8"))
        assert reload_payload["finding"] == "extension_reload_executed"
        assert reload_payload["dry_run"] is False
    finally:
        preview_server.shutdown()


def test_public_cockpit_domain_weaver_action_endpoint_routes_to_action_helper(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    calls: list[dict] = []

    from kernel import ion_chatgpt_browser_mcp_http_preview as preview
    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    def fake_domain_weaver_action(root: Path, payload: dict):
        calls.append({"root": Path(root), "payload": dict(payload)})
        return {
            "schema_id": "ion.domain_weaver.operator_action_result.v0_1",
            "ok": True,
            "action": payload.get("action"),
            "operator_action_history_path": "ION/05_context/current/domain_weaver/operator_actions/ACTION_HISTORY.json",
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        }

    monkeypatch.setattr(preview, "execute_domain_weaver_action", fake_domain_weaver_action)
    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{preview_server.server_address[1]}/cockpit/weave/action",
            data=json.dumps(
                {
                    "action": "materialize_promotion_review",
                    "confirmation": WRITE_CONFIRMATION_TOKEN,
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert payload["ok"] is True
        assert payload["action"] == "materialize_promotion_review"
        assert payload["operator_action_history_path"].endswith("ACTION_HISTORY.json")
        assert payload["accepted_state_authority"] is False
        assert calls == [
            {
                "root": tmp_path,
                "payload": {"action": "materialize_promotion_review", "confirmation": WRITE_CONFIRMATION_TOKEN},
            }
        ]
    finally:
        preview_server.shutdown()


def test_public_cockpit_codex_archive_route_requires_token_and_returns_safe_index(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    codex_home = _seed_codex_home(tmp_path)
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())
    monkeypatch.setenv("ION_COCKPIT_PUBLIC_TOKEN", "test-token")

    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        url = (
            f"http://127.0.0.1:{preview_server.server_address[1]}"
            f"/cockpit/chat/archive.json?session_id={PUBLIC_ARCHIVE_SESSION_ID}"
        )
        archive_request = urllib.request.Request(
            url,
            headers={"Host": "ion.example.test", "Accept": "application/json", "Authorization": "Bearer test-token"},
        )
        with urllib.request.urlopen(archive_request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        assert payload["schema_id"] == "ion.codex_conversation_archive.v1"
        assert payload["sessions"][0]["session_id"] == PUBLIC_ARCHIVE_SESSION_ID
        assert payload["selected_session_excerpt"]["found"] is True
        assert payload["raw_transcript_exported"] is False
        request = urllib.request.Request(
            f"http://127.0.0.1:{preview_server.server_address[1]}/cockpit/chat/archive/attach",
            data=json.dumps({
                "public_token": "test-token",
                "session_id": PUBLIC_ARCHIVE_SESSION_ID,
                "confirmation": WRITE_CONFIRMATION_TOKEN,
            }).encode("utf-8"),
            headers={
                "Host": "ion.example.test",
                "Origin": "https://ion.example.test",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            attach_payload = json.loads(response.read().decode("utf-8"))
        assert attach_payload["ok"] is True
        assert attach_payload["packet"]["codex_resume"]["command"] == ["codex", "resume", PUBLIC_ARCHIVE_SESSION_ID]
        branch_request = urllib.request.Request(
            f"http://127.0.0.1:{preview_server.server_address[1]}/cockpit/chat/branch",
            data=json.dumps({
                "public_token": "test-token",
                "confirmation": WRITE_CONFIRMATION_TOKEN,
                "parent_kind": "archive_session",
                "parent_session_id": PUBLIC_ARCHIVE_SESSION_ID,
                "title": "Public branch",
                "objective": "Branch the public archive smoke.",
            }).encode("utf-8"),
            headers={
                "Host": "ion.example.test",
                "Origin": "https://ion.example.test",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(branch_request, timeout=5) as response:
            branch_payload = json.loads(response.read().decode("utf-8"))
        assert branch_payload["ok"] is True
        assert branch_payload["branch"]["codex_fork"]["command_text"] == f"codex fork {PUBLIC_ARCHIVE_SESSION_ID}"
        assert branch_payload["branch"]["codex_fork"]["cockpit_spawned_process"] is False
    finally:
        preview_server.shutdown()


def test_public_cockpit_chat_turn_uses_raw_codex_cli_flag(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    monkeypatch.setenv("ION_COCKPIT_PUBLIC_TOKEN", "test-token")
    captured: dict[str, object] = {}

    from kernel import ion_chatgpt_browser_mcp_http_preview as preview
    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    def fake_record_chat_turn(_root, **kwargs):
        captured.update(kwargs)
        return {
            "ok": True,
            "assistant_turn": {
                "author": "codex_cli",
                "message": f"Raw public Codex CLI reply: {kwargs.get('message')}",
                "response_mode": "raw_codex_cli",
                "response_carrier": None,
                "wrapper_prompt_used": False,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    monkeypatch.setattr(preview, "record_chat_turn", fake_record_chat_turn)
    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{preview_server.server_address[1]}/cockpit/chat/turn",
            data=json.dumps({
                "public_token": "test-token",
                "lane_id": "codex_general",
                "message": "hello from public cockpit",
                "author": "operator",
                "execution_mode": "respond_only",
                "target_session_id": "019e8b2b-c770-71d3-b2d8-e4c1c14eba0b",
                "codex_session_transport": "app_server",
                "ide_context_bridge": {
                    "source": "codex_ide_workbench",
                    "active_view": "diffs",
                    "selected_path": "ION/08_ui/joc_cockpit_shell/CodexIdeWorkbenchPanel.tsx",
                },
            }).encode("utf-8"),
            headers={
                "Host": "ion.example.test",
                "Origin": "https://ion.example.test",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert payload["ok"] is True
        assert captured["raw_codex_cli_enabled"] is True
        assert captured["target_session_id"] == "019e8b2b-c770-71d3-b2d8-e4c1c14eba0b"
        assert captured["codex_session_transport"] == "app_server"
        assert captured["ide_context_bridge"]["active_view"] == "diffs"
        assert captured["ide_context_bridge"]["selected_path"] == "ION/08_ui/joc_cockpit_shell/CodexIdeWorkbenchPanel.tsx"
        assert "response_carrier_enabled" not in captured
        assert payload["assistant_turn"]["response_mode"] == "raw_codex_cli"
        assert payload["assistant_turn"]["message"] == "Raw public Codex CLI reply: hello from public cockpit"
    finally:
        preview_server.shutdown()


def test_public_cockpit_serves_first_class_ide_model(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    monkeypatch.setenv("ION_COCKPIT_PUBLIC_TOKEN", "test-token")

    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{preview_server.server_address[1]}/cockpit/ide/model.json",
            headers={"Host": "ion.example.test", "Accept": "application/json", "Authorization": "Bearer test-token"},
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    finally:
        preview_server.shutdown()

    assert payload["surface"] == "ide"
    assert payload["codex_ide_workbench"]["schema_id"] == "ion.codex_ide_workbench_model.v0_1"
    assert payload["codex_ide_workbench"]["context_registry"]["status"] == "no_active_binding"
    assert payload["codex_ide_workbench"]["authority"]["production_authority"] is False


def test_public_cockpit_root_prefers_react_shell_and_keeps_legacy_route(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    dist = tmp_path / "ION/08_ui/joc_cockpit_shell/dist"
    dist.mkdir(parents=True, exist_ok=True)
    (dist / "index.html").write_text("<main id=\"root\">react joc shell</main>", encoding="utf-8")
    monkeypatch.setenv("ION_COCKPIT_PUBLIC_TOKEN", "test-token")

    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        base = f"http://127.0.0.1:{preview_server.server_address[1]}"
        cockpit_request = urllib.request.Request(
            f"{base}/cockpit",
            headers={"Host": "ion.example.test", "Authorization": "Bearer test-token"},
        )
        with urllib.request.urlopen(cockpit_request, timeout=5) as response:
            cockpit_html = response.read().decode("utf-8")
        legacy_request = urllib.request.Request(
            f"{base}/cockpit/legacy",
            headers={"Host": "ion.example.test", "Authorization": "Bearer test-token"},
        )
        with urllib.request.urlopen(legacy_request, timeout=5) as response:
            legacy_html = response.read().decode("utf-8")

        assert "react joc shell" in cockpit_html
        assert "ION LOCAL COCKPIT" not in cockpit_html
        assert "ION LOCAL COCKPIT" in legacy_html
        assert "?token=" not in cockpit_html
        assert "?token=" not in legacy_html
    finally:
        preview_server.shutdown()


def test_public_cockpit_serves_weave_surface_endpoint(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    monkeypatch.setenv("ION_COCKPIT_PUBLIC_TOKEN", "test-token")
    captured = {}

    def fake_surface_model(root: Path, *, surface: str):
        captured["root"] = root
        captured["surface"] = surface
        return {"schema_id": "ion.cockpit_surface_view_model.v1", "surface": surface}

    monkeypatch.setattr("kernel.ion_chatgpt_browser_mcp_http_preview.build_cockpit_surface_view_model", fake_surface_model)

    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        base = f"http://127.0.0.1:{preview_server.server_address[1]}"
        request = urllib.request.Request(
            f"{base}/cockpit/weave/model.json",
            headers={"Host": "ion.example.test", "Accept": "application/json", "Authorization": "Bearer test-token"},
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert payload["surface"] == "weave"
        assert captured["surface"] == "weave"
        assert captured["root"] == tmp_path
    finally:
        preview_server.shutdown()


def test_public_cockpit_session_access_requires_auth(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    monkeypatch.setenv("ION_COCKPIT_PUBLIC_TOKEN", "test-token")

    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{preview_server.server_address[1]}/cockpit/session/access.json",
            headers={"Host": "ion.example.test", "Accept": "application/json"},
        )
        try:
            urllib.request.urlopen(request, timeout=5)
            payload = {}
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read().decode("utf-8"))

        assert payload["finding"] == "public_cockpit_login_required"
        assert payload["session_cookie"] == "ion_cockpit_session"
    finally:
        preview_server.shutdown()
        preview_server.server_close()
        preview_thread.join(timeout=5)


def test_public_cockpit_session_access_projects_invite_without_raw_token(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    monkeypatch.setenv("ION_COCKPIT_INVITE_TOKENS", "friend=friend-token")

    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{preview_server.server_address[1]}/cockpit/session/access.json",
            headers={"Host": "ion.example.test", "Accept": "application/json", "Authorization": "Bearer friend-token"},
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        payload_text = json.dumps(payload, sort_keys=True)
        routes = payload["route_registry"]["routes"]
        assert payload["schema_id"] == "ion.helixion_cockpit_session_access_projection.v0_2"
        assert payload["principal_projection"]["subject"]["rank_ceiling"] == "viewer_client"
        assert payload["principal_projection"]["rank_is_permission"] is False
        assert payload["live_route_enforcement"] is False
        assert any(route["path_template"] == "/cockpit/collab/model.json" for route in routes)
        assert "friend-token" not in payload_text
        assert str(tmp_path) not in payload_text
    finally:
        preview_server.shutdown()
        preview_server.server_close()
        preview_thread.join(timeout=5)


def test_public_cockpit_serves_collab_surface_endpoint(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    monkeypatch.setenv("ION_COCKPIT_PUBLIC_TOKEN", "test-token")

    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        request = urllib.request.Request(
            f"http://127.0.0.1:{preview_server.server_address[1]}/cockpit/collab/model.json",
            headers={"Host": "ion.example.test", "Accept": "application/json", "Authorization": "Bearer test-token"},
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert payload["surface"] == "collab"
        assert payload["runtime"]["shell_root"] == "local_ion_root_redacted"
        assert payload["collab_cockpit"]["candidate_packet"] == "PCKT-COLLAB-001"
        assert payload["collab_cockpit"]["live_route_enforcement"] is False
        assert payload["collab_cockpit"]["session_access"]["subject"]["rank_ceiling"] == "founder_root_steward"
        assert str(tmp_path) not in json.dumps(payload, sort_keys=True)
    finally:
        preview_server.shutdown()
        preview_server.server_close()
        preview_thread.join(timeout=5)


def test_public_cockpit_serves_devsecops_surface_endpoint(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    monkeypatch.setenv("ION_COCKPIT_PUBLIC_TOKEN", "test-token")

    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        unauthenticated = urllib.request.Request(
            f"http://127.0.0.1:{preview_server.server_address[1]}/cockpit/devsecops/model.json",
            headers={"Host": "ion.example.test", "Accept": "application/json"},
        )
        try:
            urllib.request.urlopen(unauthenticated, timeout=5)
            blocked_payload = {}
        except urllib.error.HTTPError as exc:
            blocked_payload = json.loads(exc.read().decode("utf-8"))

        request = urllib.request.Request(
            f"http://127.0.0.1:{preview_server.server_address[1]}/cockpit/devsecops/model.json",
            headers={"Host": "ion.example.test", "Accept": "application/json", "Authorization": "Bearer test-token"},
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        payload_text = json.dumps(payload, sort_keys=True)
        assert blocked_payload["finding"] == "public_cockpit_login_required"
        assert payload["surface"] == "devsecops"
        assert payload["runtime"]["shell_root"] == "local_ion_root_redacted"
        assert payload["devsecops_cockpit"]["candidate_packet"] == "PCKT-DEVSECOPS-001"
        assert payload["devsecops_cockpit"]["summary"]["live_route_enforcement"] is False
        assert payload["devsecops_cockpit"]["read_only_projection"] is True
        assert "test-token" not in payload_text
        assert str(tmp_path) not in payload_text
    finally:
        preview_server.shutdown()
        preview_server.server_close()
        preview_thread.join(timeout=5)


def test_public_launch_post_proxy_requires_auth_and_same_origin(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    monkeypatch.setenv("ION_COCKPIT_PUBLIC_TOKEN", "test-token")
    captured = []

    def fake_proxy_fetch(root: Path, launch_id: str, proxy_path: str, **kwargs):
        captured.append({"root": root, "launch_id": launch_id, "proxy_path": proxy_path, **kwargs})
        return {
            "ok": True,
            "status": 200,
            "content_type": "application/json",
            "body": json.dumps({"ok": True, "relayed": True}).encode("utf-8"),
        }

    monkeypatch.setattr("kernel.ion_chatgpt_browser_mcp_http_preview.project_launcher_proxy_fetch", fake_proxy_fetch)

    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()

    def post_proxy(headers: dict[str, str]) -> tuple[int, dict]:
        request = urllib.request.Request(
            f"http://127.0.0.1:{preview_server.server_address[1]}/cockpit/projects/launch/proxy/demo-launch/api/echo?x=1",
            data=json.dumps({"hello": "world"}).encode("utf-8"),
            headers={
                "Host": "ion.example.test",
                "Accept": "application/json",
                "Content-Type": "application/json",
                **headers,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8"))

    try:
        unauth_status, unauth_payload = post_proxy({"Origin": "https://ion.example.test"})
        assert unauth_status == 401
        assert unauth_payload["finding"] == "public_cockpit_login_required"
        assert captured == []

        no_origin_status, no_origin_payload = post_proxy({"Authorization": "Bearer test-token"})
        assert no_origin_status == 403
        assert no_origin_payload["finding"] == "same_origin_required"
        assert captured == []

        ok_status, ok_payload = post_proxy({"Authorization": "Bearer test-token", "Origin": "https://ion.example.test"})
        assert ok_status == 200
        assert ok_payload["relayed"] is True
        assert captured[-1]["root"] == tmp_path
        assert captured[-1]["launch_id"] == "demo-launch"
        assert captured[-1]["proxy_path"] == "api/echo"
        assert captured[-1]["query"] == "x=1"
        assert captured[-1]["method"] == "POST"
        assert json.loads(captured[-1]["body"].decode("utf-8")) == {"hello": "world"}
    finally:
        preview_server.shutdown()


def test_public_cockpit_serves_system_diagnostics_endpoint(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    monkeypatch.setenv("ION_COCKPIT_PUBLIC_TOKEN", "test-token")
    captured = {}

    def fake_system_model(root: Path):
        captured["root"] = root
        return {
            "schema_id": "ion.system_diagnostics.v1",
            "summary": {"active_dev_server_count": 2},
            "dev_servers": [{"port": 5179}, {"port": 5190}],
            "data_quality": {"port_source": "ss -ltnp"},
        }

    monkeypatch.setattr("kernel.ion_chatgpt_browser_mcp_http_preview.build_system_diagnostics_model", fake_system_model)

    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        base = f"http://127.0.0.1:{preview_server.server_address[1]}"
        request = urllib.request.Request(
            f"{base}/cockpit/system/model.json",
            headers={"Host": "ion.example.test", "Accept": "application/json", "Authorization": "Bearer test-token"},
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert payload["schema_id"] == "ion.system_diagnostics.v1"
        assert payload["summary"]["active_dev_server_count"] == 2
        assert captured["root"] == tmp_path
    finally:
        preview_server.shutdown()


def test_public_cockpit_executes_system_diagnostics_action_route(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    monkeypatch.setenv("ION_COCKPIT_PUBLIC_TOKEN", "test-token")
    captured = {}

    def fake_execute(root: Path, action: dict):
        captured["root"] = root
        captured["action"] = action
        return {
            "timestamp": "2026-06-05T00:00:00+00:00",
            "action_type": "stop_process",
            "target": "port 5178",
            "status": "ok",
            "detail": "Stopped process group for 5178",
            "affected_pids": [6210],
            "affected_ports": [5178],
        }

    monkeypatch.setattr("kernel.ion_chatgpt_browser_mcp_http_preview.execute_system_diagnostic_action", fake_execute)

    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        base = f"http://127.0.0.1:{preview_server.server_address[1]}"
        request = urllib.request.Request(
            f"{base}/cockpit/system/execute_action",
            data=json.dumps(
                {
                    "action": {
                        "action_type": "stop_process",
                        "target_port": 5178,
                        "confirmation": "ION_SYSTEM_DIAGNOSTICS_STOP_CONFIRMED",
                    }
                }
            ).encode("utf-8"),
            headers={
                "Host": "ion.example.test",
                "Origin": "https://ion.example.test",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": "Bearer test-token",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))

        assert payload["ok"] is True
        assert payload["affected_ports"] == [5178]
        assert captured["root"] == tmp_path
        assert captured["action"]["target_port"] == 5178
    finally:
        preview_server.shutdown()


def test_public_cockpit_action_branch_invoke_endpoint_requires_auth_and_profiles_artifact(monkeypatch, tmp_path):
    _seed_root(tmp_path)
    _seed_branch_registry(tmp_path)
    monkeypatch.setenv("ION_COCKPIT_PUBLIC_TOKEN", "test-token")

    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        base = f"http://127.0.0.1:{preview_server.server_address[1]}"
        request = urllib.request.Request(
            f"{base}/cockpit/action-branch/invoke",
            data=json.dumps(
                {
                    "branch_id": "large_artifact_intelligence",
                    "route_id": "large_file_profile",
                    "args": {"path": "ION/REPO_AUTHORITY.md"},
                    "expected_route_schema_version": "v0",
                }
            ).encode("utf-8"),
            headers={
                "Host": "ion.example.test",
                "Origin": "https://ion.example.test",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": "Bearer test-token",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))

        delegated = payload["delegated_result"]
        assert payload["ok"] is True
        assert payload["branch_id"] == "large_artifact_intelligence"
        assert payload["route_id"] == "large_file_profile"
        assert payload["mutates_active_state"] is False
        assert delegated["content_returned"] == "metadata_only"
        assert delegated["path"] == "ION/REPO_AUTHORITY.md"
        assert delegated["production_authority"] is False
        assert delegated["live_execution_authority"] is False
        assert delegated["accepted_state_claim"] is False
    finally:
        preview_server.shutdown()


def test_codex_worker_live_status_page_is_bounded_polling_ui():
    html = render_codex_worker_live_status_html(Path.cwd(), auth_token="test-token")

    assert "<title>ION Codex Worker</title>" in html
    assert "Worker Command Center" in html
    assert "/cockpit/worker/model.json" in html
    assert "/cockpit/chat" in html
    assert "/cockpit" in html
    assert "?token=" not in html
    assert "public_token" not in html
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
    assert "latest_return" in html
    assert "next action" in html
    assert "DEFERRED_ENVIRONMENT_BLOCKED" in html
    assert "worker_cockpit_joc_ui_upgrade_requirement_added" in html
    assert "required context" in html
    assert "all statuses" in html
    assert "setInterval(poll, 5000)" in html


def test_helixion_site_bar_marks_active_without_query_token():
    html = render_helixion_site_bar("chat", auth_token="abc123")

    assert 'aria-label="HelixION site pages"' in html
    assert 'href="/projects"' in html
    assert 'href="/cockpit/chat"' in html
    assert 'href="/cockpit/worker"' in html
    assert "?token=" not in html
    assert 'aria-current="page"' in html


def test_wrap_helixion_site_shell_adds_bar_to_existing_page():
    html = wrap_helixion_site_shell(
        "<html><head><style>body{}</style></head><body><main>page</main></body></html>",
        "cockpit",
        auth_token="abc123",
    )

    assert "helix-sitebar" in html
    assert 'href="/projects"' in html
    assert 'href="/cockpit"' in html
    assert "?token=" not in html
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
