import json
from pathlib import Path

from kernel.ion_cockpit_view_model import (
    build_cockpit_view_model,
    build_worker_cockpit_view_model,
    write_cockpit_view_model,
)


def write_json(root: Path, rel: str, payload: dict):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def seed_runtime(root: Path):
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-cockpit-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").parent.mkdir(parents=True, exist_ok=True)
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")
    current = "ION/05_context/current"
    write_json(root, f"{current}/ACTIVE_CURSOR_HOOK_STATE.json", {"schema_id": "ion.cursor_hook_state.v1", "status": "ready"})
    write_json(root, f"{current}/ACTIVE_WORK_PACKET.json", {"carrier": "cursor", "objective": "test cockpit"})
    write_json(root, f"{current}/ACTIVE_ROLE_SPAWN_PLAN.json", {
        "role_spawn_plan": [
            {"index": 1, "role": "STEWARD", "spawn": True, "context_package_path": "pkg/steward.md", "context_load_receipt_path": "pkg/steward_receipt.json"},
            {"index": 2, "role": "MASON", "spawn": False, "context_package_path": "pkg/mason.md"},
        ]
    })
    write_json(root, f"{current}/ACTIVE_CARRIER_TURN_PACKET.json", {"carrier": "cursor", "objective": "test cockpit", "blocked_by_findings": False})
    write_json(root, f"{current}/ACTIVE_CARRIER_TASK_RETURN_LEDGER.json", {"records": [{"role": "STEWARD", "index": 1, "decision": "accepted", "task_output_path": "returns/steward.md"}]})
    write_json(root, f"{current}/ACTIVE_STEWARD_INTEGRATION_QUEUE.json", {"items": [{"role": "STEWARD", "path": "returns/steward.md"}]})
    write_json(root, f"{current}/ACTIVE_OPERATOR_MESSAGE_QUEUE.json", {"items": [{"id": "op1", "text": "continue", "status": "pending"}]})
    write_json(root, f"{current}/ACTIVE_HUMAN_GATE_QUEUE.json", {"gates": []})
    write_json(root, f"{current}/ACTIVE_FRONT_DOOR_PROOF_TRACE.json", {"schema_id": "ion.front_door_proof_trace.v1", "proof_complete": True, "verdict": "ION_FRONT_DOOR_PROOF_TRACE_READY"})
    write_json(root, f"{current}/ACTIVE_LANE_TIMELINE_VIEW_MODEL.json", {"schema_id": "ion.lane_timeline_view_model.v1", "events": []})
    write_json(root, f"{current}/ACTIVE_RECEIPT_HYDRATION_VIEW_MODEL.json", {"schema_id": "ion.receipt_hydration_view_model.v1", "records": []})
    write_json(root, f"{current}/ACTIVE_RUNTIME_DEBUG_OVERLAY.json", {"schema_id": "ion.runtime_debug_overlay.v1", "status": "degraded"})
    write_json(root, f"{current}/SAFE_FULL_PROJECT_PACKAGE_RESULT_V110.json", {
        "schema_id": "ion.safe_full_project_package_result.v1",
        "accepted": True,
        "zip_root_audit": {"verdict": "ZIP_ROOT_CONFIRMED", "archive_root_mode": "CANONICAL_ARCHIVE_ROOT"},
        "preservation_report": {"packaging_verdict": "PASS", "removed_files": 0, "protected_removed_files": 0, "unexpected_removed_files": 0},
    })
    write_json(root, f"{current}/V108_V72_MCP_DONOR_RECONCILIATION_AUDIT.json", {
        "schema_id": "ion.v72_mcp_donor_reconciliation_audit.v1",
        "reconciliation_verdict": "V72_MCP_DONOR_RECONCILIATION_PASS",
        "restored_donor_surface_count": 38,
        "missing_donor_surface_count": 0,
        "forbidden_runtime_file_count": 0,
        "production_authority": False,
        "live_execution_authority": False,
    })


def seed_worker_cockpit_runtime(root: Path) -> None:
    current = "ION/05_context/current"
    run_rel = "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_ui/run.json"
    run_dir = root / "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_ui"
    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        root,
        run_rel,
        {
            "schema_id": "ion.codex_queue_runner_run.v1",
            "run_id": "run_worker_ui",
            "request_id": "req_worker_ui",
            "request_path": "ION/05_context/current/chatgpt_connector/codex_work_requests/req_worker_ui.json",
            "run_packet_path": run_rel,
            "run_dir": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_ui",
            "prompt_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_ui/prompt.md",
            "context_receipt_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_ui/context_receipt.json",
            "worker_context_awareness_receipt_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_ui/worker_context_awareness_receipt.json",
            "stdout_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_ui/stdout.log",
            "stderr_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_ui/stderr.log",
            "last_message_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_ui/latest_return.md",
            "created_at": "2026-05-14T03:00:00+00:00",
            "started_at": "2026-05-14T03:00:01+00:00",
            "completed_at": "2026-05-14T03:00:25+00:00",
            "status": "RETURN_TEMPLATE_INVALID",
            "submit_result": {
                "context_proof_accepted": True,
                "template_action_proof_accepted": True,
                "return_template_valid": False,
                "workload_diff_required": True,
                "workload_diff_present": False,
                "workload_diff_accepted": False,
                "packet_path": "ION/05_context/current/chatgpt_connector/task_returns/return_worker_ui.json",
            },
            "codex_model_move_summary": "gpt-5.3-codex / high for code_patch (conserve_main_bank)",
            "codex_model_move": {
                "selected_model": "gpt-5.3-codex",
                "selected_reasoning_effort": "high",
                "usage_pool_id": "codex_primary_observed",
                "model_move_id": "move_worker_ui",
                "selection_reason": ["routing_posture:conserve_main_bank"],
            },
            "worker_lifecycle_events": [
                {"event": "worker_boot", "at": "2026-05-14T03:00:01+00:00"},
                {"event": "worker_terminal", "at": "2026-05-14T03:00:25+00:00", "terminal_state": "template_invalid"},
            ],
        },
    )
    (run_dir / "prompt.md").write_text("# prompt\n", encoding="utf-8")
    (run_dir / "context_receipt.json").write_text("{\"schema_id\":\"ion.context_load_receipt.v1\"}\n", encoding="utf-8")
    (run_dir / "stdout.log").write_text("stdout tail\n", encoding="utf-8")
    (run_dir / "stderr.log").write_text("stderr tail\n", encoding="utf-8")
    (run_dir / "worker_stdout.log").write_text("worker stdout tail\n", encoding="utf-8")
    (run_dir / "worker_stderr.log").write_text("worker stderr tail\n", encoding="utf-8")
    (run_dir / "latest_return.md").write_text("### RESULT\nworker return\n", encoding="utf-8")
    write_json(
        root,
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/run_worker_ui/worker_context_awareness_receipt.json",
        {
            "schema_id": "ion.worker_context_awareness_receipt.v1",
            "status": "WORKER_CONTEXT_ACKNOWLEDGED",
            "worker_authored": False,
            "required_context_reads": [
                {"path": "ION/04_packages/kernel/ion_cockpit_view_model.py", "required": True, "status": "READY"},
                {"path": "ION/04_packages/kernel/ion_chatgpt_browser_mcp_http_preview.py", "required": True, "status": "MISSING"},
            ],
            "missing_required_context_paths": ["ION/04_packages/kernel/ion_chatgpt_browser_mcp_http_preview.py"],
        },
    )
    write_json(
        root,
        f"{current}/chatgpt_connector/runtime/codex_queue_runner_state.json",
        {
            "schema_id": "ion.codex_queue_runner_state.v1",
            "active_run": None,
            "latest_run": run_rel,
            "updated_at": "2026-05-14T03:00:25+00:00",
        },
    )
    write_json(
        root,
        "ION/05_context/current/kernel_fanout_scheduler/carrier_dryrun/fanout_carrier_dryrun_result_20260514.json",
        {
            "schema_id": "ion.kernel_fanout_carrier_dryrun_result.v1",
            "queue_integrity": {"queue_mutation_detected": False},
            "scenarios": [
                {
                    "scenario": "forced_timeout",
                    "result_path": "ION/05_context/current/kernel_fanout_scheduler/carrier_dryrun/forced_timeout/result.json",
                    "parent_receipt_path": "ION/05_context/current/kernel_fanout_scheduler/carrier_dryrun/forced_timeout/parent_receipt.json",
                    "compact_summary": {
                        "scenario": "forced_timeout",
                        "settlement_verdict": "SMOKE_BLOCKED",
                        "blocked_children": ["timeout_child_1"],
                        "timeout_evidence": [{"code": "child_timeout", "severity": "blocked"}],
                    },
                },
            ],
        },
    )
    write_json(
        root,
        "ION/05_context/current/kernel_fanout_scheduler/carrier_dryrun/forced_timeout/parent_receipt.json",
        {
            "schema_id": "ion.kernel_fanout_carrier_dryrun_parent_receipt.v1",
            "child_receipt_paths": [
                {
                    "child_id": "timeout_child_1",
                    "lease_receipt_path": "child_receipts/timeout_child_1_lease.json",
                    "heartbeat_receipt_path": "child_receipts/timeout_child_1_heartbeat.json",
                    "worker_context_awareness_receipt_path": "child_receipts/timeout_child_1_signin.json",
                }
            ],
        },
    )
    write_json(
        root,
        "ION/05_context/current/kernel_fanout_scheduler/settlement/fanout_dryrun_readonly_mcp_exposure_settlement_20260514.json",
        {"status": "DEFERRED_ENVIRONMENT_BLOCKED"},
    )
    write_json(
        root,
        "ION/05_context/current/supabase_event_mirror/receipts/20260514_event.json",
        {
            "remote_result": {
                "event_id": "evt_worker_ui",
                "event_type": "worker_cockpit_joc_ui_upgrade_requirement_added",
                "packet_id": "PCKT-ION-WORKER-COCKPIT-JOC-LIVE-UI-UPGRADE-20260514",
            }
        },
    )


def test_build_cockpit_view_model_summarizes_v88_runtime(tmp_path):
    seed_runtime(tmp_path)
    model = build_cockpit_view_model(tmp_path)
    assert model["schema_id"] == "ion.cockpit_view_model.v1"
    assert model["runtime"]["status"] == "ready"
    assert model["top_bar"]["objective"] == "test cockpit"
    assert model["top_bar"]["spawn_count"] == 1
    assert model["top_bar"]["plan_spawn_count"] == 1
    assert model["top_bar"]["deferred_spawn_count"] == 0
    assert model["top_bar"]["spawn_rows_total"] == 2
    assert model["top_bar"]["return_counts"]["accepted"] == 1
    assert model["top_bar"]["operator_queue_pending"] == 1
    assert model["top_bar"]["sandbox_return_count"] == 0
    assert model["top_bar"]["local_service_count"] == 7
    assert model["local_services"]["schema_id"] == "ion.local_service_status.v1"
    assert model["local_services"]["install_authority"] is False
    assert model["service_console"]["schema_id"] == "ion.cockpit_service_console.v1"
    assert model["service_console"]["production_authority"] is False
    assert model["service_console"]["live_execution_authority"] is False
    assert model["top_bar"]["gate_count"] == 0
    assert model["agents"]["spawn_rows"][0]["role"] == "STEWARD"
    assert model["agents"]["spawn_rows"][0]["return_recorded"] is True
    assert model["agents"]["returns"][0]["authority_class"] == "ACCEPTED_TASK_RETURN"
    assert model["front_door_proof_trace"]["schema_id"] == "ion.front_door_proof_trace.v1"
    assert model["lane_timeline"]["schema_id"] == "ion.lane_timeline_view_model.v1"
    assert model["receipt_hydration"]["schema_id"] == "ion.receipt_hydration_view_model.v1"
    assert model["runtime_debug_overlay"]["schema_id"] == "ion.runtime_debug_overlay.v1"
    assert model["safe_full_project_package"]["zip_root_audit"]["verdict"] == "ZIP_ROOT_CONFIRMED"
    assert model["v72_mcp_donor_reconciliation"]["reconciliation_verdict"] == "V72_MCP_DONOR_RECONCILIATION_PASS"
    assert any(event["source"] == "safe_full_project_package" for event in model["timeline"])
    assert any(event["source"] == "v72_mcp_donor_reconciliation" for event in model["timeline"])


def test_human_gate_blocks_cockpit_runtime(tmp_path):
    seed_runtime(tmp_path)
    write_json(tmp_path, "ION/05_context/current/ACTIVE_HUMAN_GATE_QUEUE.json", {"gates": [{"id": "gate1", "status": "open", "reason": "operator approval"}]})
    model = build_cockpit_view_model(tmp_path)
    assert model["runtime"]["status"] == "blocked"
    assert model["top_bar"]["gate_count"] == 1


def test_cockpit_counts_boolean_accepted_task_returns(tmp_path):
    seed_runtime(tmp_path)
    write_json(tmp_path, "ION/05_context/current/ACTIVE_CARRIER_TASK_RETURN_LEDGER.json", {
        "records": [
            {"role": "STEWARD", "index": 1, "accepted": True, "task_output_path": "returns/steward.md"},
            {"role": "RELAY", "index": 2, "accepted": False, "task_output_path": "returns/relay.md"},
        ]
    })

    model = build_cockpit_view_model(tmp_path)

    assert model["top_bar"]["return_counts"]["accepted"] == 1
    assert model["top_bar"]["return_counts"]["rejected"] == 1
    assert model["top_bar"]["return_counts"]["pending"] == 0
    assert model["agents"]["returns"][0]["authority_class"] == "ACCEPTED_TASK_RETURN"
    assert model["agents"]["returns"][1]["authority_class"] == "REJECTED_TASK_RETURN"


def test_cockpit_spawn_count_uses_active_turn_spawn_queue_when_present(tmp_path):
    seed_runtime(tmp_path)
    write_json(tmp_path, "ION/05_context/current/ACTIVE_ROLE_SPAWN_PLAN.json", {
        "execution_bundle_materialized": False,
        "role_spawn_plan": [
            {"index": 1, "role": "STEWARD", "spawn_intent": True, "spawn": False, "spawn_deferral_reason": "deferred_by_spawn_row_limit"},
            {"index": 2, "role": "MASON", "spawn_intent": True, "spawn": False, "spawn_deferral_reason": "deferred_by_spawn_row_limit"},
        ],
    })
    write_json(tmp_path, "ION/05_context/current/ACTIVE_CARRIER_TURN_PACKET.json", {
        "carrier": "cursor",
        "objective": "plan only",
        "blocked_by_findings": False,
        "spawn_row_limit": 0,
        "spawn_queue": [],
    })

    model = build_cockpit_view_model(tmp_path)

    assert model["top_bar"]["spawn_count"] == 0
    assert model["top_bar"]["plan_spawn_count"] == 0
    assert model["top_bar"]["deferred_spawn_count"] == 2
    assert model["top_bar"]["spawn_rows_total"] == 2
    assert model["top_bar"]["execution_bundle_materialized"] is False


def test_write_cockpit_view_model(tmp_path):
    seed_runtime(tmp_path)
    model = write_cockpit_view_model(tmp_path)
    out = tmp_path / "ION/05_context/current/ACTIVE_COCKPIT_VIEW_MODEL.json"
    assert out.exists()
    loaded = json.loads(out.read_text())
    assert loaded["schema_id"] == model["schema_id"]


def test_cockpit_projects_chatgpt_browser_callsign(tmp_path):
    seed_runtime(tmp_path)
    (tmp_path / "ION/03_registry").mkdir(parents=True, exist_ok=True)
    (tmp_path / "ION/03_registry/chatgpt_browser_carrier_profile.yaml").write_text(
        "\n".join([
            "carrier_id: CHATGPT_BROWSER_CARRIER",
            "project_facing_callsign: Sev",
            "callsign_authority: carrier_continuity_label_only_not_ion_authority",
            "callsign_decision_receipt: ION/05_context/current/chatgpt_connector/decisions/decision.json",
            "",
        ]),
        encoding="utf-8",
    )
    write_json(tmp_path, "ION/05_context/current/CHATGPT_BROWSER_MCP_CONNECTOR_CONTRACT_V120.json", {
        "allowed_tools": ["ion_status", "ion_tool_manifest"],
        "verdict": "ION_CHATGPT_BROWSER_MCP_CONNECTOR_CONTRACT_READY",
    })

    model = build_cockpit_view_model(tmp_path)

    summary = model["chatgpt_browser_mcp"]
    assert summary["carrier_id"] == "CHATGPT_BROWSER_CARRIER"
    assert summary["project_facing_callsign"] == "Sev"
    assert summary["callsign_authority"] == "carrier_continuity_label_only_not_ion_authority"
    assert summary["codex_queue_runner"]["schema_id"] == "ion.codex_queue_runner.v1"
    assert summary["codex_queue_runner"]["reconciliation"]["write"] is False


def test_cockpit_projects_chatgpt_sandbox_returns(tmp_path):
    seed_runtime(tmp_path)
    return_root = tmp_path / "ION/05_context/inbox/chatgpt_sandbox_returns/sev-20260505-041500-chatops-ui-return"
    return_root.mkdir(parents=True)
    (return_root / "SANDBOX_RETURN_MANIFEST.json").write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_sandbox_return.v1",
                "return_id": "sev-20260505-041500-chatops-ui-return",
                "changed_paths": ["ION/09_integrations/browser_extension/ion_chatops_bridge/README.md"],
            }
        ),
        encoding="utf-8",
    )

    model = build_cockpit_view_model(tmp_path)

    assert model["top_bar"]["sandbox_return_count"] == 1
    assert model["chatgpt_sandbox_returns"]["return_count"] == 1
    assert model["chatgpt_sandbox_returns"]["direct_apply_authority"] is False


def test_worker_cockpit_view_model_projects_active_latest_proof_and_settlement(tmp_path):
    seed_runtime(tmp_path)
    seed_worker_cockpit_runtime(tmp_path)

    model = build_worker_cockpit_view_model(tmp_path)

    assert model["schema_id"] == "ion.worker_cockpit_view_model.v1"
    assert model["read_only"]["mutation_controls_enabled"] is False
    assert model["active_worker"]["status"] == "template-invalid"
    assert model["latest_worker_runs"][0]["status"] == "RETURN_TEMPLATE_INVALID"
    assert model["latest_worker_runs"][0]["selected_model"] == "gpt-5.3-codex"
    assert model["machine_sign_in"]["worker_authored"] is False
    assert model["machine_sign_in"]["required_context_reads_total"] == 2
    assert model["machine_sign_in"]["required_context_reads_missing"] == 1
    assert model["proof_gate"]["return_template_valid"] is False
    assert model["proof_gate"]["workload_diff_required"] is True
    assert model["proof_gate"]["workload_diff_accepted"] is False
    assert any(row["name"] == "stdout" and row["included"] is True for row in model["logs"])
    assert model["fanout"]["status"]["schema_id"] == "ion.kernel_fanout_carrier_dryrun_status.v1"
    assert model["fanout"]["status"]["timeout_fail_closed_summary"]["fail_closed"] is True
    assert model["fanout"]["parent_child_rows"][0]["child_id"] == "timeout_child_1"
    assert model["settlement"]["blockers"][0]["status"] == "DEFERRED_ENVIRONMENT_BLOCKED"
    assert model["event_links"]["supabase_receipts"][0]["event_type"] == "worker_cockpit_joc_ui_upgrade_requirement_added"
