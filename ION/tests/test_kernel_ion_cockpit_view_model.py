import json
from pathlib import Path

from kernel import ion_cockpit_view_model as cockpit_view_model_module
from kernel import ion_project_cockpit as project_cockpit_module
from kernel.ion_cockpit_view_model import (
    build_branch_gateway_consumer_model,
    build_cockpit_surface_view_model,
    build_cockpit_view_model,
    build_worker_cockpit_view_model,
    write_cockpit_view_model,
)

CODEX_ARCHIVE_SESSION_ID = "bbbbbbbb-cccc-dddd-eeee-ffffffffffff"


def write_json(root: Path, rel: str, payload: dict):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def seed_codex_archive_home(root: Path) -> Path:
    codex_home = root / "codex-home"
    write_jsonl(
        codex_home / "session_index.jsonl",
        [{"id": CODEX_ARCHIVE_SESSION_ID, "thread_name": "Cockpit archive", "updated_at": "2026-05-23T12:04:00+00:00"}],
    )
    write_jsonl(
        codex_home / "history.jsonl",
        [{"session_id": CODEX_ARCHIVE_SESSION_ID, "ts": "2026-05-23T12:05:00+00:00", "text": "cockpit archive smoke"}],
    )
    write_jsonl(
        codex_home / f"sessions/2026/05/23/rollout-{CODEX_ARCHIVE_SESSION_ID}.jsonl",
        [
            {"type": "session_meta", "timestamp": "2026-05-23T12:00:00+00:00", "payload": {"id": CODEX_ARCHIVE_SESSION_ID, "cwd": "/workspace/ion"}},
            {"type": "event_msg", "timestamp": "2026-05-23T12:01:00+00:00", "payload": {"type": "user_message", "message": "cockpit archive smoke"}},
        ],
    )
    return codex_home


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


def seed_branch_gateway_registry(root: Path) -> None:
    registry = root / "ION/03_registry/ion_action_mcp_branch_leader_registry.yaml"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        """
schema_id: ion.action_mcp_branch_leader_registry.v0
status: test
branches:
  - branch_id: worker_shift
    title: Worker Shift
    family: worker_shift_presence
    routes:
      - route_id: status_summary
        local_handler: worker_shift_presence
        mutates_state: false
        route_schema_version: v0
        args_schema:
          type: object
          properties: {}
          additionalProperties: false
      - route_id: active_workers
        local_handler: worker_shift_presence
        mutates_state: false
        route_schema_version: v0
        args_schema:
          type: object
          properties: {}
          additionalProperties: false
      - route_id: coordination_state
        local_handler: worker_shift_presence
        mutates_state: false
        route_schema_version: v0
        args_schema:
          type: object
          properties: {}
          additionalProperties: false
  - branch_id: runtime_services
    title: Runtime Services
    family: local_runtime_service_control
    routes:
      - route_id: service_status
        local_handler: runtime_services
        mutates_state: false
        route_schema_version: v0
        args_schema:
          type: object
          properties:
            service_id:
              type: string
            probe_health:
              type: boolean
          additionalProperties: false
      - route_id: service_reload_plan
        local_handler: runtime_services
        mutates_state: false
        route_schema_version: v0
        args_schema:
          type: object
          required:
            - service_id
          properties:
            service_id:
              type: string
          additionalProperties: false
      - route_id: restart_service
        local_handler: runtime_services
        mutates_state: true
        confirmation_required: ION_BOUNDED_WRITE_CONFIRMED
        idempotency_required: true
        route_schema_version: v0
        args_schema:
          type: object
          required:
            - service_id
          properties:
            service_id:
              type: string
            idempotency_key:
              type: string
            confirmation:
              type: string
          additionalProperties: false
      - route_id: retest_service
        local_handler: runtime_services
        mutates_state: false
        route_schema_version: v0
        args_schema:
          type: object
          required:
            - service_id
          properties:
            service_id:
              type: string
          additionalProperties: false
      - route_id: reload_and_retest
        local_handler: runtime_services
        mutates_state: true
        confirmation_required: ION_BOUNDED_WRITE_CONFIRMED
        idempotency_required: true
        route_schema_version: v0
        args_schema:
          type: object
          required:
            - service_id
          properties:
            service_id:
              type: string
            idempotency_key:
              type: string
            confirmation:
              type: string
          additionalProperties: false
""".lstrip(),
        encoding="utf-8",
    )
    write_json(
        root,
        "ION/05_context/current/worker_shift/ACTIVE_WORKER_SHIFT_BOARD.json",
        {
            "active_shifts": [
                {
                    "worker_id": "codex:test:20260515:001",
                    "identity": {"display_callsign": "Codex test"},
                    "status": "ACTIVE",
                    "packet_id": "PCKT-TEST",
                    "current_branch": "worker_shift",
                    "last_heartbeat_at": "2026-05-15T22:00:00+00:00",
                }
            ],
            "active_leases": [
                {
                    "lease_id": "lease:test",
                    "worker_id": "codex:test:20260515:001",
                    "lease_type": "read_interest",
                    "paths": ["ION/04_packages/kernel/ion_cockpit_view_model.py"],
                }
            ],
        },
    )


def seed_context_package_graph(root: Path) -> None:
    graph_root = "ION/05_context/current/context_package_graph_wave_001"
    write_json(
        root,
        f"{graph_root}/CONTEXT_PACKAGE_GRAPH_WAVE_001_REVIEW.json",
        {
            "schema_id": "ion.context_package_graph_wave_001_review.v1",
            "next_packet_id": "PCKT-ION-CONTEXT-PACKAGE-GRAPH-WAVE-002",
            "package_count": 1,
            "candidate_review_ready_count": 1,
            "blocked_count": 0,
            "packages": [
                {
                    "path": "ION/04_packages",
                    "package_type": "anchor",
                    "classification": "local_stub",
                    "candidate_capsule_path": "ION/04_packages/ION_CONTEXT_CAPSULE.candidate.yaml",
                    "candidate_valid": True,
                    "accepted_capsule_exists": False,
                    "accepted_capsule_path": "ION/04_packages/ION_CONTEXT_CAPSULE.yaml",
                    "promotion_readiness": "candidate_review_ready_with_gaps",
                    "gaps": ["readme_does_not_reference_context_capsule"],
                    "blockers": [],
                    "recommended_next": ["bind branch package record into cockpit context explorer"],
                    "surface_hints": {
                        "readme": ["ION/04_packages/README.md"],
                        "routes": ["ION/04_packages/kernel/ion_branch_delegate_router.py"],
                        "receipts": ["ION/04_packages/kernel/ion_carrier_mount_receipt.py"],
                    },
                }
            ],
        },
    )
    write_json(
        root,
        f"{graph_root}/CONTEXT_PACKAGE_GRAPH_WAVE_002_ENRICHMENT_MANIFEST.json",
        {
            "schema_id": "ion.context_package_graph_wave_002_enrichment_manifest.v1",
            "packet_id": "PCKT-ION-CONTEXT-PACKAGE-GRAPH-WAVE-002",
            "source_wave_id": "PCKT-ION-CONTEXT-PACKAGE-GRAPH-WAVE-001",
            "enriched_count": 1,
            "enriched": [
                {
                    "path": "ION/04_packages",
                    "candidate_capsule_path": "ION/04_packages/ION_CONTEXT_CAPSULE.candidate.yaml",
                    "candidate_capsule_sha256_after_wave_002": "abc123",
                    "readme_projection_candidate": f"{graph_root}/readme_projection_candidates/ion_04_packages_README_BRANCH_ENTRY_CANDIDATE.md",
                    "promotion_readiness": "candidate_review_ready_with_gaps",
                    "gaps": ["readme_does_not_reference_context_capsule"],
                }
            ],
        },
    )
    write_json(
        root,
        f"{graph_root}/COCKPIT_CONTEXT_EXPLORER_PROJECTION_SPEC.json",
        {
            "schema_id": "ion.cockpit_context_explorer_projection_spec.v1",
            "packet_id": "PCKT-ION-CONTEXT-PACKAGE-GRAPH-WAVE-002",
            "candidate_state_only": True,
            "accepted_state_claim": False,
            "allowed_operations": ["view_branch_context"],
            "forbidden_operations": ["accepted_state_promotion", "production_deploy"],
            "required_ui_fields": ["path", "candidate_capsule_path", "authority"],
            "branches": [
                {
                    "path": "ION/04_packages",
                    "package_type": "anchor",
                    "parent_ref": "ION/ION_CONTEXT_CAPSULE.yaml",
                    "maturity_level": "level_3_candidate",
                    "read_first": ["README.md", "ION_CONTEXT_CAPSULE.candidate.yaml"],
                    "candidate_capsule_path": "ION/04_packages/ION_CONTEXT_CAPSULE.candidate.yaml",
                    "promotion_readiness": "candidate_review_ready_with_gaps",
                    "gaps": ["readme_does_not_reference_context_capsule"],
                    "authority": {
                        "accepted_state_authority": False,
                        "production_authority": False,
                        "live_execution_authority": False,
                    },
                    "surface_hints": {
                        "readme": ["ION/04_packages/README.md"],
                        "routes": ["ION/04_packages/kernel/ion_branch_delegate_router.py"],
                        "receipts": ["ION/04_packages/kernel/ion_carrier_mount_receipt.py"],
                    },
                }
            ],
        },
    )


def seed_vnext_mission_control(root: Path) -> None:
    (root / "ION_VNEXT/00_front_door").mkdir(parents=True, exist_ok=True)
    (root / "ION_VNEXT/01_canon").mkdir(parents=True, exist_ok=True)
    (root / "ION_VNEXT/07_work").mkdir(parents=True, exist_ok=True)
    (root / "ION_VNEXT/08_releases/m102_production_authority_decision_packet_draft_20260522/OPERATOR_FINAL").mkdir(
        parents=True,
        exist_ok=True,
    )
    (root / "ION_VNEXT/00_front_door/AI_START_HERE.md").write_text("# AI start\n", encoding="utf-8")
    (root / "ION_VNEXT/00_front_door/HUMAN_START_HERE.md").write_text("# Human start\n", encoding="utf-8")
    (root / "ION_VNEXT/00_front_door/ROUTE_MAP.md").write_text("# Route map\n", encoding="utf-8")
    (root / "ION_VNEXT/00_front_door/AUTHORITY_BOUNDARIES.md").write_text("# Authority\n", encoding="utf-8")
    (root / "ION_VNEXT/01_canon/CONTROL_SURFACE_REGISTRY.yaml").write_text("status: ready\n", encoding="utf-8")
    (root / "ION_VNEXT/01_canon/STATE_LIFECYCLE.yaml").write_text("status: ready\n", encoding="utf-8")
    (root / "ION_VNEXT/01_canon/WORKSPACE_CANON.yaml").write_text(
        "\n".join(
            [
                "schema_id: ion.vnext_workspace_canon.v1_candidate",
                "status: candidate_m102_authority_decision_draft_ready_no_execution",
                "mission: Clean local-first ION vNext operating layer for Browser GPT, Codex, MCP, and Supabase.",
                "current_operating_model:",
                "  primary_build_and_test_loop: codex_cli_local_worker",
                "  human_facing_relay: browser_gpt_relay_persona",
                "  bridge_plane: actions_mcp_chatops",
                "  mirror_plane: supabase_mirror_cockpit_non_authoritative",
                "  source_truth: local_ion_files_receipts_context_packets",
                "  accepted_state_rule: proof_gate_receipt_then_steward_or_operator_acceptance",
                "deferred_by_default:",
                "- cursor_extension",
                "- daimon",
                "current_direct_rebuild_sequence:",
                "- M100_CUTOVER_EXECUTION_REHEARSAL_DRYRUN",
                "- M101_PRODUCTION_AUTHORITY_TRANSITION_PRECHECK",
                "- M102_PRODUCTION_AUTHORITY_DECISION_PACKET_DRAFT",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / "ION_VNEXT/07_work/M102_VNEXT_PRODUCTION_AUTHORITY_DECISION_PACKET_DRAFT.md").write_text(
        "# M102 vNext Production Authority Decision Packet Draft\n",
        encoding="utf-8",
    )
    write_json(
        root,
        "ION_VNEXT/07_work/m102_vnext_production_authority_decision_packet_draft_result_20260522.json",
        {
            "schema_id": "ion.vnext_production_authority_decision_packet_draft_result.v1",
            "packet_id": "PCKT-M102-VNEXT-PRODUCTION-AUTHORITY-DECISION-PACKET-DRAFT-20260522",
            "created_at": "2026-05-23T11:05:45Z",
            "verdict": "VNEXT_PRODUCTION_AUTHORITY_DECISION_PACKET_DRAFT_READY",
            "reviewed_gate_ids_by_m102": [
                "production_execution_authority_not_set",
                "live_supabase_mirror_smoke_not_run_if_claimed",
            ],
            "remaining_gate_ids_after_m102": [
                "production_execution_authority_not_set",
                "live_supabase_mirror_smoke_not_run_if_claimed",
            ],
            "blockers_closed_by_m102": [],
            "next_route": "NO_AUTOMATIC_NEXT_PACKET_AUTHORITY_TRANSITION_REQUIRES_SEPARATE_PROOF_PACKET",
            "next_route_condition": "Any future production authority transition requires a separate proof-gated packet.",
            "non_claims": [
                "no production execution authority set",
                "no authority decision recorded",
                "no Supabase mutation",
                "no accepted-state claim",
            ],
            "production_execution_authority_set": False,
            "production_cutover_authorized": False,
            "execution_authorized": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            "secrets_accessed": False,
            "supabase_mutated": False,
            "supabase_provider_api_call_attempted": False,
        },
    )
    (root / "ION_VNEXT/08_releases/m102_production_authority_decision_packet_draft_20260522/OPERATOR_FINAL/PRODUCTION_AUTHORITY_DECISION_PACKET_DRAFT.md").write_text(
        "# Draft\n",
        encoding="utf-8",
    )
    write_json(
        root,
        "ION/05_context/current/codex_solo/STATUS.json",
        {
            "capsule": {
                "recent_rows": [
                    {
                        "id": "C-191",
                        "date": "2026-05-23",
                        "summary": "M102 completed with no authority transition.",
                        "status": "COMPLETE",
                        "evidence": "ION_VNEXT/07_work/M102_VNEXT_PRODUCTION_AUTHORITY_DECISION_PACKET_DRAFT.md",
                    }
                ]
            }
        },
    )
    write_json(
        root,
        "ION/05_context/current/codex_solo/LONG_HORIZON.json",
        {
            "schema_id": "ion.codex_solo_long_horizon.v1",
            "capsule_entry_count": 194,
            "epoch_count": 2,
            "epochs": [
                {
                    "epoch_id": "E-019",
                    "date_start": "2026-05-23",
                    "date_end": "2026-05-23",
                    "row_start": "C-185",
                    "row_end": "C-190",
                    "row_count": 6,
                    "status_counts": {"COMPLETE": 6},
                    "evidence_refs": ["ION_VNEXT/07_work/M102_VNEXT_PRODUCTION_AUTHORITY_DECISION_PACKET_DRAFT.md"],
                    "summaries": [
                        {"id": "C-191", "summary": "vNext authority decision draft and cutover proof gates remained non-live."}
                    ],
                },
                {
                    "epoch_id": "E-020",
                    "date_start": "2026-05-23",
                    "date_end": "2026-05-23",
                    "row_start": "C-191",
                    "row_end": "C-194",
                    "row_count": 4,
                    "status_counts": {"COMPLETE": 4},
                    "evidence_refs": ["ION/08_ui/joc_cockpit_shell/VNextMissionControlPanel.tsx"],
                    "summaries": [
                        {"id": "C-194", "summary": "Codex cockpit UI mission control projection and context visualization."}
                    ],
                },
            ],
        },
    )
    write_json(
        root,
        "ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json",
        {
            "packages": [
                {
                    "package_id": "minimum_working_capsule",
                    "context_type": "active_short_horizon",
                    "load_policy": "always_inline_first",
                    "path_refs": ["ION/05_context/current/codex_solo/CAPSULE.md"],
                    "window": {"kind": "line_tail"},
                },
                {
                    "package_id": "helixion_joc_orchestration_package",
                    "context_type": "active_orchestration",
                    "load_policy": "use_for_helixion_joc_rebuild_work",
                    "path_refs": ["ION/02_architecture/HELIXION_JOC_ORCHESTRATION_WORKFLOW_PROTOCOL.md"],
                    "window": {"kind": "main_context_package"},
                },
            ]
        },
    )
    (root / "ION/02_architecture").mkdir(parents=True, exist_ok=True)
    (root / "ION/01_doctrine").mkdir(parents=True, exist_ok=True)
    (root / "ION/02_architecture/ION_MOUNT_CONTRACT.md").write_text(
        "---\ntype: protocol\nauthority: A2_OPERATIONAL\nstatus: ACTIVE\n---\n# ION mount contract\n",
        encoding="utf-8",
    )
    (root / "ION/02_architecture/HELIXION_JOC_ORCHESTRATION_WORKFLOW_PROTOCOL.md").write_text(
        "---\ntype: protocol\nauthority: A2_OPERATIONAL\nstatus: ACTIVE\n---\n# Helixion JOC orchestration workflow protocol\n",
        encoding="utf-8",
    )
    (root / "ION/01_doctrine/CANONICAL_WORKFLOW.md").write_text(
        "---\ntype: doctrine\nauthority: A1_CANONICAL\nstatus: ACTIVE\n---\n# Canonical workflow\n",
        encoding="utf-8",
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
    assert model["codex_cli_workbench"]["schema_id"] == "ion.codex_cli_workbench_model.v1"
    assert model["codex_cli_workbench"]["hidden_reasoning_exposed"] is False
    assert model["joc_comms"]["schema_id"] == "ion.joc_comms_projection.v1"
    assert model["joc_comms"]["read_only_projection"] is True
    assert model["joc_comms"]["authority"]["write_authority"] is False
    assert "operator_queue" in {row["channel_id"] for row in model["joc_comms"]["channels"]}
    assert any(event["source"] == "safe_full_project_package" for event in model["timeline"])
    assert any(event["source"] == "v72_mcp_donor_reconciliation" for event in model["timeline"])


def test_cockpit_projects_joc_comms_channels_from_queue_surfaces(tmp_path):
    seed_runtime(tmp_path)
    write_json(tmp_path, "ION/05_context/current/ACTIVE_CARRIER_MESSAGE_QUEUE.json", {
        "messages": [
            {
                "message_id": "carrier-msg-1",
                "channel": "full_carrier_mcp_parity_smoke",
                "from_carrier": "CHATGPT_BROWSER_CARRIER",
                "to_carrier": "CODEX_CLI_CARRIER",
                "body": "parity updated",
                "status": "pending",
                "created_at": "2026-05-30T00:00:00+00:00",
            }
        ]
    })
    write_json(tmp_path, "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json", {
        "request_count": 1,
        "requests": [
            {
                "request_id": "req_joc_comms",
                "request_path": "ION/05_context/current/chatgpt_connector/codex_work_requests/req_joc_comms.json",
                "objective": "Projection smoke",
                "status": "QUEUED_FOR_CODEX_CARRIER",
                "created_at": "2026-05-30T00:10:00+00:00",
                "updated_at": "2026-05-30T00:12:00+00:00",
            }
        ],
    })

    model = build_cockpit_view_model(tmp_path)
    projection = model["joc_comms"]
    channel_ids = {row["channel_id"] for row in projection["channels"]}
    assert "carrier_messages" in channel_ids
    assert "codex_queue" in channel_ids
    message_ids = {row["message_id"] for row in projection["messages"]}
    assert "carrier_message:carrier-msg-1" in message_ids
    assert "codex_request:req_joc_comms" in message_ids


def test_cockpit_projects_compact_agent_home_views_into_joc_comms(tmp_path):
    seed_runtime(tmp_path)
    write_json(
        tmp_path,
        "ION/05_context/current/agent_comms/projections/agent_home_view_role_scout.json",
        {
            "schema_id": "ion.agent_home_view.v0",
            "identity": {"assigned_role": "role.scout"},
            "updated_at": "2026-05-31T00:00:00+00:00",
            "source_surfaces": {
                "files": [
                    "ION/05_context/current/agent_comms/threads/team/thread_role_scout.json",
                ],
                "not_used_for_orientation": [
                    "ION/05_context/current/agent_comms/logs/messages.jsonl",
                    "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json",
                ],
            },
            "scout_context_card": {
                "schema_id": "ion.agent_home_view.scout_context_card.v0",
                "compact_defaults": {"inbox_scan_cap": 2, "thread_scan_cap": 2, "carrier_queue_scan_cap": 3},
                "context_read_order": [],
                "forbidden_default_surfaces": [
                    "ION/05_context/current/agent_comms/logs/messages.jsonl",
                    "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json",
                ],
            },
            "self_improvement_loop": {
                "schema_id": "ion.agent_home_view.self_improvement_loop.v0",
                "status": "active",
                "counts": {"total": 1},
                "items": [
                    {
                        "work_item_id": "scout_blocker_1",
                        "kind": "blocker",
                        "priority": "high",
                        "summary": "Projection smoke item",
                        "suggested_action": "Open packet and verify compact projection",
                        "proof_links": ["ION/05_context/current/agent_comms/projections/agent_home_view_role_scout.json"],
                        "source": "test_seed",
                    }
                ],
            },
        },
    )

    model = build_cockpit_view_model(tmp_path)
    team_home_views = model["agent_control_plane"]["communications"]["team_comms"]["agent_home_views"]
    assert len(team_home_views) == 1
    assert team_home_views[0]["role_id"] == "role.scout"

    joc_home_views = model["joc_comms"]["agent_home_views"]
    assert len(joc_home_views) == 1
    assert joc_home_views[0]["role_id"] == "role.scout"
    assert "messages.jsonl" not in json.dumps(joc_home_views[0]["source_surfaces"]["files"])
    assert "ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json" not in json.dumps(joc_home_views[0]["source_surfaces"]["files"])
    assert "messages.jsonl" in json.dumps(joc_home_views[0]["scout_context_card"]["forbidden_default_surfaces"])


def test_cockpit_projects_vnext_mission_control_read_only(tmp_path):
    seed_runtime(tmp_path)
    seed_vnext_mission_control(tmp_path)

    model = build_cockpit_view_model(tmp_path)

    vnext = model["vnext_mission_control"]
    assert vnext["schema_id"] == "ion.vnext_mission_control_projection.v1"
    assert vnext["status"] == "mission_map_ready"
    assert vnext["read_only"] is True
    assert vnext["authority"]["production_authority"] is False
    assert vnext["authority"]["live_execution_authority"] is False
    assert vnext["authority"]["accepted_state_authority"] is False
    assert vnext["authority"]["secrets_authority"] is False
    assert vnext["current_packet"]["token"] == "M102"
    assert vnext["current_packet"]["status"] == "result_recorded"
    assert vnext["latest_result"]["verdict"] == "VNEXT_PRODUCTION_AUTHORITY_DECISION_PACKET_DRAFT_READY"
    assert vnext["latest_receipt"]["id"] == "C-191"
    assert model["top_bar"]["vnext_current_packet"] == "M102"
    assert model["top_bar"]["vnext_open_gate_count"] == 2
    assert model["top_bar"]["vnext_packet_count"] == 3
    open_gates = {gate["gate_id"] for gate in vnext["gates"] if gate["status"] == "open"}
    assert open_gates == {
        "production_execution_authority_not_set",
        "live_supabase_mirror_smoke_not_run_if_claimed",
    }
    assert any(lane["lane_id"] == "supabase_mirror" and lane["status"] == "mirror_only" for lane in vnext["lanes"])
    assert vnext["next_safe_route"]["automatic"] is False
    assert vnext["long_horizon"]["epoch_count"] == 2
    assert len(vnext["long_horizon"]["latest_epochs"]) == 2
    assert vnext["context_packages"]["package_count"] == 2
    assert vnext["protocol_index"]["protocol_count"] >= 3
    assert vnext["documentation_surfaces"]["file_count"] >= 3
    family_ids = {family["family_id"] for family in vnext["mission_families"]}
    assert "vnext_direct_rebuild" in family_ids
    assert "codex_cockpit_carrier" in family_ids
    project = model["project_cockpit"]
    assert project["schema_id"] == "ion.project_cockpit_projection.v1"
    assert project["status"] == "project_cockpit_ready"
    assert project["selected_project_id"] == "ion_vnext"
    assert project["authority"]["candidate_state_write_authority"] is True
    assert project["authority"]["accepted_state_authority"] is False
    assert project["authority"]["production_authority"] is False
    assert project["authority"]["live_execution_authority"] is False
    assert project["authority"]["supabase_mutation_authority"] is False
    assert project["authority"]["codex_queue_dispatch_authority"] is False
    project_ids = {row["project_id"] for row in project["projects"]}
    assert {"application_dev", "cosmos", "ion_development", "ion_vnext"}.issubset(project_ids)
    application_dev = next(row for row in project["projects"] if row["project_id"] == "application_dev")
    assert application_dev["route_href"] == "/projects/application-dev"
    assert application_dev["app_catalog_url"] == "/projects/application-dev/apps.json"
    assert application_dev["launcher_url"].endswith(":5199/")
    assert project["summary"]["project_count"] >= 4
    assert project["summary"]["mission_count"] >= 2
    assert project["summary"]["derived_blocker_count"] == 2
    assert project["summary"]["open_blocker_count"] == 2
    assert project["summary"]["open_question_count"] == 0
    assert {blocker["source"] for blocker in project["blockers"]} == {"derived_vnext_gate"}
    assert any(event["event_type"] == "packet" for event in project["timeline_events"])
    assert any(event["event_type"] == "blocker" for event in project["timeline_events"])
    assert model["top_bar"]["project_cockpit_status"] == "project_cockpit_ready"
    assert model["top_bar"]["project_count"] >= 4
    assert model["top_bar"]["project_mission_count"] >= 2
    assert model["top_bar"]["project_open_blocker_count"] == 2
    assert model["top_bar"]["project_open_question_count"] == 0


def test_cockpit_view_model_exposes_safe_codex_conversation_archive(monkeypatch, tmp_path):
    seed_runtime(tmp_path)
    codex_home = seed_codex_archive_home(tmp_path)
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())

    model = build_cockpit_view_model(tmp_path)

    archive = model["codex_conversation_archive"]
    assert archive["schema_id"] == "ion.codex_conversation_archive.v1"
    assert archive["source_counts"]["session_files_total"] == 1
    assert archive["sessions"][0]["session_id"] == CODEX_ARCHIVE_SESSION_ID
    assert archive["raw_transcript_exported"] is False
    assert model["top_bar"]["codex_conversation_session_count"] == 1


def test_codex_surface_model_defers_full_agent_control_plane(monkeypatch, tmp_path):
    seed_runtime(tmp_path)
    codex_home = seed_codex_archive_home(tmp_path)
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())
    write_json(
        tmp_path,
        "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json",
        {
            "schema_id": "ion.domain_weaver_projection.v1",
            "weave_status": "ready",
            "summary": {"usable_domain_count": 1, "active_domain_count": 1, "gap_count": 0},
            "domains": [{"domain_id": "codex", "label": "Codex"}],
            "agents": [{"role_id": "role.codex_carrier_steward", "display_name": "Codex Steward"}],
        },
    )

    def fail_full_agent_control(*_args, **_kwargs):
        raise AssertionError("codex first-paint surface should not build the full agent control plane")

    def fail_full_rollback(*_args, **_kwargs):
        raise AssertionError("codex first-paint surface should not build the full rollback model")

    monkeypatch.setattr(cockpit_view_model_module, "build_agent_control_plane_projection", fail_full_agent_control)
    monkeypatch.setattr(cockpit_view_model_module, "build_codex_git_rollback_model", fail_full_rollback)

    model = build_cockpit_surface_view_model(tmp_path, surface="codex")

    assert model["surface"] == "codex"
    assert model["codex_conversation_archive"]["source_counts"]["session_files_total"] == 1
    assert model["agent_control_plane"]["schema_id"] == "ion.agent_control_plane.codex_surface.v0_1"
    assert model["agent_control_plane"]["diagnostics"]["full_agent_control_plane_deferred"] is True
    assert model["top_bar"]["agent_control_plane_agent_count"] == 1
    assert model["codex_git_rollback"]["verdict"] == "ION_CODEX_GIT_ROLLBACK_DEFERRED_FOR_SURFACE_BOOT"
    assert model["codex_git_rollback"]["surface_boot_deferred"] is True


def test_project_cockpit_reads_managed_blockers_questions_and_timeline(tmp_path):
    seed_runtime(tmp_path)
    seed_vnext_mission_control(tmp_path)
    write_json(
        tmp_path,
        "ION/05_context/current/project_cockpit/PROJECT_COCKPIT_LEDGER.json",
        {
            "schema_id": "ion.project_cockpit_ledger.v1",
            "created_at": "2026-05-23T00:00:00+00:00",
            "updated_at": "2026-05-23T01:00:00+00:00",
            "projects": [],
            "missions": [],
            "blockers": [
                {
                    "blocker_id": "blocker_ui_planning",
                    "project_id": "ion_vnext",
                    "title": "UI planning needs settlement",
                    "status": "open",
                    "severity": "high",
                    "required_next_action": "Record settlement evidence.",
                    "evidence_refs": ["ION_VNEXT/07_work"],
                }
            ],
            "questions": [
                {
                    "question_id": "question_route",
                    "project_id": "ion_vnext",
                    "question_text": "Which mission route is active?",
                    "status": "open",
                    "priority": "P1_HIGH",
                    "blocking": ["blocker_ui_planning"],
                }
            ],
            "timeline_events": [
                {
                    "event_id": "event_seed",
                    "project_id": "ion_vnext",
                    "event_type": "seed",
                    "status": "recorded",
                    "title": "seed event",
                }
            ],
        },
    )

    model = build_cockpit_view_model(tmp_path)

    project = model["project_cockpit"]
    assert project["summary"]["managed_blocker_count"] == 1
    assert project["summary"]["open_question_count"] == 1
    assert any(blocker["blocker_id"] == "blocker_ui_planning" for blocker in project["blockers"])
    assert any(question["question_id"] == "question_route" for question in project["questions"])
    assert any(event["event_id"] == "event_seed" for event in project["timeline_events"])
    assert model["top_bar"]["project_open_question_count"] == 1


def test_project_cockpit_uses_cached_project_portfolio_manifest(monkeypatch, tmp_path):
    seed_runtime(tmp_path)
    materialized_root = tmp_path / "organized-projects"
    materialized_root.mkdir()
    write_json(
        tmp_path,
        "ION/05_context/current/project_portfolio/PROJECT_PORTFOLIO_MANIFEST.json",
        {
            "schema_id": "ion.project_portfolio.v1",
            "status": "project_portfolio_ready",
            "generated_at": "2026-06-02T18:27:45+00:00",
            "summary": {
                "project_root_count": 199,
                "family_count": 45,
                "duplicate_cluster_count": 23,
                "legacy_copy_cluster_count": 23,
                "versioned_family_count": 13,
                "materialized_present": True,
            },
            "organizer": {
                "materialized_present": True,
                "materialized_root": materialized_root.as_posix(),
                "source_copy_policy": "current source copy only; historical roots become lineage pointers",
                "layout": "domains/<domain>/<project>/source/current plus lineage",
                "latest_materialization_receipt": {
                    "relpath": "ION/05_context/current/project_portfolio/receipts/test_project_portfolio_materialization_receipt.json",
                    "created_at": "2026-06-02T18:27:49+00:00",
                    "copy_count": 35,
                    "target": materialized_root.as_posix(),
                    "accepted_state_authority": False,
                    "production_authority": False,
                    "live_execution_authority": False,
                    "secrets_authority": False,
                },
            },
            "families": [
                {"family_id": "cosmos:earth-forge", "label": "Earth Forge", "diff_count": 17},
                {"family_id": "cosmos:hyper-h2o", "label": "Hyper H2O", "diffs": [{"diff_id": "d1"}, {"diff_id": "d2"}]},
            ],
        },
    )

    def fail_scan(*_args, **_kwargs):
        raise AssertionError("project portfolio scanner should not run when a valid manifest exists")

    monkeypatch.setattr(project_cockpit_module, "build_project_portfolio_model", fail_scan)

    model = build_cockpit_view_model(tmp_path)

    project = model["project_cockpit"]
    organization = project["organization_state"]
    assert project["portfolio_load_mode"] == "cached_manifest"
    assert project["portfolio"]["load_mode"] == "cached_manifest"
    assert project["summary"]["portfolio_load_mode"] == "cached_manifest"
    assert organization["status"] == "materialized"
    assert organization["materialized_root"] == materialized_root.as_posix()
    assert organization["copy_count"] == 35
    assert organization["project_root_count"] == 199
    assert organization["duplicate_cluster_count"] == 23
    assert organization["versioned_family_count"] == 13
    assert organization["diff_manifest_count"] == 19
    assert organization["accepted_state_authority"] is False
    assert organization["production_authority"] is False
    assert organization["live_execution_authority"] is False
    assert organization["secrets_authority"] is False


def test_projects_surface_model_skips_unrelated_heavy_hydration(monkeypatch, tmp_path):
    seed_runtime(tmp_path)
    write_json(
        tmp_path,
        "ION/05_context/current/project_portfolio/PROJECT_PORTFOLIO_MANIFEST.json",
        {
            "schema_id": "ion.project_portfolio.v1",
            "status": "project_portfolio_ready",
            "summary": {"project_root_count": 1, "family_count": 1, "materialized_present": True},
            "organizer": {"materialized_present": True},
            "families": [{"family_id": "cosmos:test", "label": "Test Project", "diff_count": 0}],
            "projects": [{"project_id": "test", "family_id": "cosmos:test", "label": "Test Project"}],
        },
    )

    def fail_unrelated_hydration(*_args, **_kwargs):
        raise AssertionError("projects surface should not hydrate unrelated cockpit models")

    monkeypatch.setattr(cockpit_view_model_module, "build_local_service_status", fail_unrelated_hydration)
    monkeypatch.setattr(cockpit_view_model_module, "build_service_console_model", fail_unrelated_hydration)
    monkeypatch.setattr(cockpit_view_model_module, "build_system_diagnostics_model", fail_unrelated_hydration)
    monkeypatch.setattr(cockpit_view_model_module, "_context_package_graph_projection", fail_unrelated_hydration)

    model = build_cockpit_surface_view_model(tmp_path, surface="projects")

    assert model["surface"] == "projects"
    assert model["runtime"]["version"] == "V90_SURFACE_BOOT_PROJECTS_FAST"
    assert model["project_cockpit"]["portfolio_load_mode"] == "cached_manifest"
    assert model["top_bar"]["project_cockpit_status"] == "project_cockpit_ready"
    assert model["local_services"]["status"] == "deferred"
    assert model["system_diagnostics"]["status"] == "deferred"


def test_branch_gateway_consumer_model_projects_worker_shift_and_runtime_services_without_restart(tmp_path):
    seed_runtime(tmp_path)
    seed_branch_gateway_registry(tmp_path)

    model = build_branch_gateway_consumer_model(tmp_path)

    worker = model["worker_shift"]
    status_summary = worker["status_summary"]["delegated_result"]
    assert status_summary["worker_shift_summary"]["active_worker_count"] == 1
    assert worker["active_workers"]["delegated_result"]["active_worker_count"] == 1
    assert "queue_coordination_state" in worker["coordination_state"]["delegated_result"]

    runtime_services = model["runtime_services"]
    assert runtime_services["service_status"]["delegated_result"]["service_count"] == 5
    assert runtime_services["service_reload_plans"]["mcp_preview"]["delegated_result"]["service_id"] == "mcp_preview"
    assert runtime_services["retest_service"]["route_id"] == "retest_service"
    assert runtime_services["mutation_gate"]["confirmation_required"] == "ION_BOUNDED_WRITE_CONFIRMED"
    assert runtime_services["mutation_gate"]["idempotency_key_required"] is True
    assert runtime_services["mutation_gate"]["plan_preview_required"] is True
    assert runtime_services["mutation_gate"]["post_action_receipt_handoff_required"] is True
    assert runtime_services["mutation_gate"]["cockpit_executes_mutation"] is False
    assert all(row["cockpit_executes_mutation"] is False for row in runtime_services["service_controls"])
    assert not (tmp_path / "ION/05_context/current/runtime_services/receipts").exists()


def test_cockpit_projects_context_package_graph_without_promotion(tmp_path):
    seed_runtime(tmp_path)
    seed_context_package_graph(tmp_path)

    model = build_cockpit_view_model(tmp_path)

    graph = model["context_package_graph"]
    assert graph["schema_id"] == "ion.cockpit_context_package_graph_projection.v1"
    assert graph["status"] == "visibility_projection_ready"
    assert graph["packet_id"] == "PCKT-ION-CONTEXT-PACKAGE-GRAPH-WAVE-002"
    assert graph["branch_count"] == 1
    assert graph["candidate_review_ready_count"] == 1
    assert graph["blocked_count"] == 0
    assert graph["accepted_state_claim"] is False
    assert graph["authority"]["accepted_state_authority"] is False
    assert graph["authority"]["production_authority"] is False
    assert graph["authority"]["live_execution_authority"] is False
    branch = graph["branches"][0]
    assert branch["path"] == "ION/04_packages"
    assert branch["candidate_capsule_path"] == "ION/04_packages/ION_CONTEXT_CAPSULE.candidate.yaml"
    assert branch["readme_projection_candidate"].endswith("ion_04_packages_README_BRANCH_ENTRY_CANDIDATE.md")
    assert branch["surface_counts"]["total"] == 3
    assert branch["authority"]["accepted_state_authority"] is False
    assert model["top_bar"]["branch_context_package_count"] == 1
    assert model["top_bar"]["branch_context_package_ready_count"] == 1
    assert model["top_bar"]["context_package_graph_status"] == "visibility_projection_ready"


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


def test_cockpit_browser_gpt_action_gateway_sync_projects_local_action_artifacts(tmp_path):
    seed_runtime(tmp_path)
    write_json(tmp_path, "ION/05_context/current/action_gateway/receipts/action_gateway_receipt_test.json", {
        "schema_id": "ion.custom_gpt_action_gateway_receipt.v1",
        "created_at": "2026-06-02T16:10:00+00:00",
        "operation": "actions_submit",
        "status": "accepted",
        "action_id": "test_action_gateway_sync",
        "intent": "write_file_draft",
        "idempotency_key": "test-action-gateway-sync",
        "result": {"ok": True, "receipt_path": "ION/05_context/current/action_gateway/receipts/action_gateway_receipt_test.json"},
    })
    write_json(tmp_path, "ION/05_context/current/chatops_bridge/actions/test_action_gateway_sync.json", {
        "ion_action": {"action_id": "test_action_gateway_sync", "intent": "write_file_draft"},
        "idempotency_key": "test-action-gateway-sync",
    })
    runtime_dir = tmp_path / "ION/05_context/current/action_gateway/runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    (runtime_dir / "action_gateway.pid").write_text("999999\n", encoding="utf-8")
    (runtime_dir / "action_gateway.log").write_text("gateway booted\naccepted test_action_gateway_sync\n", encoding="utf-8")
    write_json(tmp_path, "ION/05_context/current/action_gateway/runtime/browser_queue.json", {
        "schema_id": "ion.browser_queue.v1",
        "packets": [{"packet_id": "BQ-test", "state": "queued", "objective": "test action sync", "updated_at": "2026-06-02T16:10:01+00:00"}],
    })
    write_json(tmp_path, "ION/05_context/current/action_gateway/runtime/idempotency_ledger.json", {
        "schema_id": "ion.custom_gpt_action_gateway_idempotency_ledger.v1",
        "entries": {
            "test-action-gateway-sync": {
                "action_id": "test_action_gateway_sync",
                "intent": "write_file_draft",
                "ok": True,
                "recorded_at": "2026-06-02T16:10:02+00:00",
                "receipt_path": "ION/05_context/current/action_gateway/receipts/action_gateway_receipt_test.json",
            }
        },
    })
    write_json(tmp_path, "ION/05_context/current/runtime_services/test_run_receipts/test_action_gateway_sync_run.json", {
        "schema_id": "ion.runtime_focused_test_run_receipt.v0_1",
        "suite_id": "action_gateway_sync_smoke",
        "created_at": "2026-06-02T16:10:03+00:00",
        "payload": {"ok": True, "stdout_tail": "1 passed"},
    })

    model = build_cockpit_view_model(tmp_path)
    sync = model["extension_micro_shell"]["action_gateway_sync"]

    assert sync["schema_id"] == "ion.browser_gpt.action_gateway_sync.v1"
    assert sync["status"] == "ready"
    assert sync["summary"]["queued_packet_count"] == 1
    assert sync["summary"]["idempotency_entry_count"] == 1
    assert sync["recent_action_receipts"][0]["action_id"] == "test_action_gateway_sync"
    assert sync["recent_action_receipts"][0]["payload"]["result"]["ok"] is True
    assert sync["recent_action_packets"][0]["payload"]["ion_action"]["action_id"] == "test_action_gateway_sync"
    assert sync["idempotency_ledger"]["entries"][0]["receipt_path"].endswith("action_gateway_receipt_test.json")
    assert "accepted test_action_gateway_sync" in sync["runtime"]["log_tail"][-1]


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


def test_cockpit_projects_task_return_machine_receipts(tmp_path):
    seed_runtime(tmp_path)
    diagnosis = {
        "schema_id": "ion.chatgpt_browser_connector_task_return_automation_diagnosis.v1",
        "classification": "carrier_intake_ready",
        "summary": "All automated return gates accepted the submitted task return.",
        "next_action": "automation_may_project_return_as_carrier_intake_ready",
        "finding_count": 0,
        "findings": [],
        "manual_ai_receipt_required": False,
        "automation_must_report": True,
    }
    receipt_path = "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/receipt.json"
    return_path = "ION/05_context/current/chatgpt_connector/task_returns/return.json"
    write_json(tmp_path, receipt_path, {
        "schema_id": "ion.chatgpt_browser_connector_task_return_machine_receipt.v1",
        "receipt_source": "automation",
        "manual_ai_authored": False,
        "accepted_for_carrier_intake": True,
        "result": "RECORDED_FOR_CARRIER_INTAKE",
        "task_return_packet_path": return_path,
        "work_request_id": "req_machine_receipt",
        "diagnosis": diagnosis,
    })
    write_json(tmp_path, "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json", {
        "schema_id": "ion.chatgpt_browser_connector_codex_work_queue.v1",
        "request_count": 1,
        "requests": [
            {
                "request_id": "req_machine_receipt",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "settlement_relevant_machine_receipt_path": receipt_path,
                "settlement_relevant_return_packet_path": return_path,
                "settlement_relevant_automation_diagnosis": diagnosis,
            }
        ],
    })

    model = build_cockpit_view_model(tmp_path)

    browser_summary = model["chatgpt_browser_mcp"]
    assert browser_summary["latest_task_return_machine_receipts"][0]["receipt_source"] == "automation"
    assert browser_summary["latest_task_return_machine_receipts"][0]["manual_ai_authored"] is False
    assert browser_summary["latest_task_return_automation_diagnoses"][0]["classification"] == "carrier_intake_ready"
    assert browser_summary["latest_task_return_automation_diagnoses"][0]["manual_ai_receipt_required"] is False
    chat_summary = model["codex_capsule_chat"]
    assert chat_summary["latest_task_return_machine_receipts"][0]["path"] == receipt_path
    assert chat_summary["latest_task_return_automation_diagnoses"][0]["machine_receipt_path"] == receipt_path


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
