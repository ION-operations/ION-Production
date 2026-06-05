import json
from pathlib import Path

import kernel.ion_status as ion_status_module
from kernel.ion_status import build_ion_status


def write_json(root: Path, rel: str, payload: dict):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def seed_ready_status(root: Path, *, active_created_at: str, queue_items: list[dict]):
    current = "ION/05_context/current"
    write_json(root, f"{current}/ACTIVE_CURSOR_HOOK_STATE.json", {"status": "projected_not_connected"})
    write_json(root, f"{current}/ACTIVE_WORK_PACKET.json", {"objective": "queue freshness", "created_at": active_created_at})
    write_json(
        root,
        f"{current}/ACTIVE_ROLE_SPAWN_PLAN.json",
        {"created_at": active_created_at, "execution_bundle_materialized": False, "role_spawn_plan": []},
    )
    write_json(
        root,
        f"{current}/ACTIVE_CARRIER_TURN_PACKET.json",
        {"objective": "queue freshness", "created_at": active_created_at, "spawn_queue": []},
    )
    write_json(root, f"{current}/ACTIVE_CARRIER_TASK_RETURN_LEDGER.json", {"records": []})
    write_json(root, f"{current}/ACTIVE_STEWARD_INTEGRATION_QUEUE.json", {"items": []})
    write_json(root, f"{current}/ACTIVE_OPERATOR_MESSAGE_QUEUE.json", {"items": queue_items})
    write_json(root, f"{current}/ACTIVE_HUMAN_GATE_QUEUE.json", {"gates": []})
    write_json(
        root,
        f"{current}/V108_V72_MCP_DONOR_RECONCILIATION_AUDIT.json",
        {
            "reconciliation_verdict": "V72_MCP_DONOR_RECONCILIATION_PASS",
            "missing_donor_surface_count": 0,
            "forbidden_runtime_file_count": 0,
            "production_authority": False,
            "live_execution_authority": False,
        },
    )
    (root / "pyproject.toml").write_text("[project]\nname='mount-test'\n", encoding="utf-8")
    (root / "ION/03_registry/boots").mkdir(parents=True, exist_ok=True)
    (root / "ION/04_packages/kernel").mkdir(parents=True, exist_ok=True)
    authority = root / "ION/REPO_AUTHORITY.md"
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("authority\n", encoding="utf-8")


def test_current_status_surfaces_v108_preservation_and_mcp_donor_reconciliation():
    repo = Path(__file__).resolve().parents[2]
    status = build_ion_status(repo)

    assert status["schema_id"] == "ion.status.v1"
    assert status["production_authority"] is False
    assert status["live_execution_authority"] is False
    package = status["safe_full_project_package"]
    assert package["path_pattern"] == "ION/05_context/current/SAFE_FULL_PROJECT_PACKAGE_RESULT_V*.json"
    if package["present"]:
        assert package["accepted"] is True
        assert package["zip_root_verdict"] == "ZIP_ROOT_CONFIRMED"
    else:
        assert package["path"] is None
        assert package["accepted"] is None
        assert package["zip_root_verdict"] is None
    assert status["v72_mcp_donor_reconciliation"]["verdict"] == "V72_MCP_DONOR_RECONCILIATION_PASS"
    assert status["v72_mcp_donor_reconciliation"]["missing_donor_surface_count"] == 0
    assert status["v72_mcp_donor_reconciliation"]["forbidden_runtime_file_count"] == 0
    assert status["v72_mcp_donor_reconciliation"]["production_authority"] is False


def test_status_does_not_make_older_pending_operator_message_the_next_action(tmp_path):
    seed_ready_status(
        tmp_path,
        active_created_at="2026-05-16T20:00:00+00:00",
        queue_items=[
            {
                "id": "old_pending",
                "message": "old queued packet",
                "status": "pending",
                "created_at": "2026-05-13T20:00:00+00:00",
            }
        ],
    )

    status = build_ion_status(tmp_path)

    assert status["operator_queue_counts"]["pending"] == 1
    assert status["operator_queue_pending"]["pending_count"] == 1
    assert status["operator_queue_pending"]["stale_count"] == 1
    assert status["operator_queue_pending"]["actionable_count"] == 0
    assert status["operator_queue_pending"]["stale_item_ids"] == ["old_pending"]
    assert status["next_lawful_action"] == "continue_or_queue_new_work"


def test_status_keeps_newer_pending_operator_message_actionable(tmp_path):
    seed_ready_status(
        tmp_path,
        active_created_at="2026-05-16T20:00:00+00:00",
        queue_items=[
            {
                "id": "new_pending",
                "message": "new queued packet",
                "status": "pending",
                "created_at": "2026-05-16T20:05:00+00:00",
            }
        ],
    )

    status = build_ion_status(tmp_path)

    assert status["operator_queue_pending"]["pending_count"] == 1
    assert status["operator_queue_pending"]["stale_count"] == 0
    assert status["operator_queue_pending"]["actionable_count"] == 1
    assert status["next_lawful_action"] == "run_ion_carrier_continue_with_consume_operator_queue"


def test_ion_status_security_boundary_blocks_secret_bearing_file_without_emitting_values(tmp_path):
    seed_ready_status(tmp_path, active_created_at="2026-05-16T20:00:00+00:00", queue_items=[])
    secret_value = "status-dummy-value-must-not-appear"
    (tmp_path / ".env.supabase.local").write_text(f"SUPABASE_PASSWORD={secret_value}\n", encoding="utf-8")

    status = build_ion_status(tmp_path)
    rendered = json.dumps(status, sort_keys=True)

    assert status["legacy_verdict_without_truth_gates"] == "ION_STATUS_READY"
    assert status["verdict"] == "ION_STATUS_SECURITY_BLOCKED"
    assert status["next_lawful_action"] == "repair_truth_gate_blockers"
    assert status["truth_gates"]["security_boundary"]["blocker_count"] == 1
    assert status["truth_gates"]["blockers"][0]["path"] == ".env.supabase.local"
    assert status["truth_gates"]["secret_values_emitted"] is False
    assert secret_value not in rendered


def test_ion_status_clean_single_carrier_sandbox_returns_sandbox_ready_verdict(tmp_path):
    seed_ready_status(tmp_path, active_created_at="2026-05-16T20:00:00+00:00", queue_items=[])

    status = build_ion_status(tmp_path)

    assert status["legacy_verdict_without_truth_gates"] == "ION_STATUS_READY"
    assert status["verdict"] == "ION_STATUS_SINGLE_CARRIER_READY"
    assert status["verdict"] != "ION_STATUS_READY"
    assert status["profile_id"] == "single_carrier_sandbox"
    assert status["status_ceiling"] == "LOCAL_SANDBOX_READY_ONLY"
    assert status["truth_gates"]["package_profile"]["profile_id"] == "single_carrier_sandbox"
    assert status["truth_gates"]["package_profile"]["status_ceiling"] == "LOCAL_SANDBOX_READY_ONLY"
    assert status["truth_gates"]["package_profile"]["ready_verdict"] == "ION_STATUS_SINGLE_CARRIER_READY"
    assert status["truth_gates"]["package_profile"]["full_readiness_proven"] is False
    assert status["production_authority"] is False
    assert status["live_execution_authority"] is False


def test_ion_status_profile_missing_blocks_final_verdict(tmp_path):
    seed_ready_status(tmp_path, active_created_at="2026-05-16T20:00:00+00:00", queue_items=[])
    write_json(tmp_path, "ION/05_context/current/ION_PACKAGE_PROFILE.json", {"profile_id": "missing_profile"})

    status = build_ion_status(tmp_path)

    assert status["legacy_verdict_without_truth_gates"] == "ION_STATUS_READY"
    assert status["verdict"] == "ION_STATUS_PROFILE_BLOCKED"
    assert status["truth_gates"]["package_profile"]["status"] == "PACKAGE_PROFILE_BLOCKED"
    assert status["truth_gates"]["package_profile"]["blockers"][0]["category"] == "profile_missing"


def test_ion_status_dependency_truth_gate_can_block_readiness(tmp_path):
    seed_ready_status(tmp_path, active_created_at="2026-05-16T20:00:00+00:00", queue_items=[])
    write_json(tmp_path, "ION/05_context/current/ION_TRUTH_GATE_STATE.json", {"dependencies": {"status": "missing"}})

    status = build_ion_status(tmp_path)

    assert status["legacy_verdict_without_truth_gates"] == "ION_STATUS_READY"
    assert status["verdict"] == "ION_STATUS_DEPENDENCY_BLOCKED"
    assert status["truth_gates"]["dependency_gate"]["status"] == "DEPENDENCY_BLOCKED"


def test_ion_status_red_tests_truth_gate_can_block_readiness(tmp_path):
    seed_ready_status(tmp_path, active_created_at="2026-05-16T20:00:00+00:00", queue_items=[])
    write_json(tmp_path, "ION/05_context/current/ION_TRUTH_GATE_STATE.json", {"tests": {"status": "red"}})

    status = build_ion_status(tmp_path)

    assert status["legacy_verdict_without_truth_gates"] == "ION_STATUS_READY"
    assert status["verdict"] == "ION_STATUS_TEST_BLOCKED"
    assert status["truth_gates"]["test_gate"]["status"] == "TEST_BLOCKED"


def test_ion_status_stale_currentness_truth_gate_can_block_readiness(tmp_path):
    seed_ready_status(tmp_path, active_created_at="2026-05-16T20:00:00+00:00", queue_items=[])
    write_json(tmp_path, "ION/05_context/current/ION_TRUTH_GATE_STATE.json", {"currentness": {"status": "stale"}})

    status = build_ion_status(tmp_path)

    assert status["legacy_verdict_without_truth_gates"] == "ION_STATUS_READY"
    assert status["verdict"] == "ION_STATUS_CURRENTNESS_BLOCKED"
    assert status["truth_gates"]["currentness_gate"]["status"] == "CURRENTNESS_BLOCKED"


def test_status_does_not_require_generated_package_sidecar_evidence_for_mount_ready(tmp_path):
    current = "ION/05_context/current"
    write_json(tmp_path, f"{current}/ACTIVE_CURSOR_HOOK_STATE.json", {"status": "projected_not_connected"})
    write_json(tmp_path, f"{current}/ACTIVE_WORK_PACKET.json", {"objective": "fresh package mount"})
    write_json(tmp_path, f"{current}/ACTIVE_ROLE_SPAWN_PLAN.json", {
        "execution_bundle_materialized": False,
        "role_spawn_plan": [
            {"role": "STEWARD", "spawn_intent": True, "spawn": False, "spawn_deferral_reason": "deferred_by_spawn_row_limit"},
        ],
    })
    write_json(tmp_path, f"{current}/ACTIVE_CARRIER_TURN_PACKET.json", {"objective": "fresh package mount"})
    write_json(tmp_path, f"{current}/ACTIVE_CARRIER_TASK_RETURN_LEDGER.json", {"records": []})
    write_json(tmp_path, f"{current}/ACTIVE_STEWARD_INTEGRATION_QUEUE.json", {"items": []})
    write_json(tmp_path, f"{current}/ACTIVE_OPERATOR_MESSAGE_QUEUE.json", {"items": []})
    write_json(tmp_path, f"{current}/ACTIVE_HUMAN_GATE_QUEUE.json", {"gates": []})
    write_json(tmp_path, f"{current}/V108_V72_MCP_DONOR_RECONCILIATION_AUDIT.json", {
        "reconciliation_verdict": "V72_MCP_DONOR_RECONCILIATION_PASS",
        "restored_donor_surface_count": 38,
        "missing_donor_surface_count": 0,
        "forbidden_runtime_file_count": 0,
        "cursor_bridge_preserved": True,
        "donor_runtime_receipts_restored": False,
        "production_authority": False,
        "live_execution_authority": False,
    })
    (tmp_path / "pyproject.toml").write_text("[project]\nname='mount-test'\n", encoding="utf-8")
    (tmp_path / "ION/03_registry/boots").mkdir(parents=True, exist_ok=True)
    (tmp_path / "ION/04_packages/kernel").mkdir(parents=True, exist_ok=True)
    authority = tmp_path / "ION/REPO_AUTHORITY.md"
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("authority\n", encoding="utf-8")

    status = build_ion_status(tmp_path)

    assert status["verdict"] == "ION_STATUS_SINGLE_CARRIER_READY"
    assert status["missing_state_surfaces"] == []
    assert status["trunk_preservation"]["present"] is False
    assert status["safe_full_project_package"]["present"] is False
    assert status["spawn_queue_count"] == 0
    assert status["plan_spawn_count"] == 0
    assert status["deferred_spawn_count"] == 1
    assert status["execution_bundle_materialized"] is False
    assert status["safe_full_project_package"]["path"] is None
    assert status["safe_full_project_package"]["path_pattern"] == "ION/05_context/current/SAFE_FULL_PROJECT_PACKAGE_RESULT_V*.json"
    assert "trunk_preservation_report" in status["optional_evidence_paths"]
    assert status["optional_evidence_paths"]["safe_full_project_package_result"] == "ION/05_context/current/SAFE_FULL_PROJECT_PACKAGE_RESULT_V*.json"


def test_status_surfaces_rejected_steward_integration_as_next_action(tmp_path):
    current = "ION/05_context/current"
    write_json(tmp_path, f"{current}/ACTIVE_CURSOR_HOOK_STATE.json", {"status": "projected_not_connected"})
    write_json(tmp_path, f"{current}/ACTIVE_WORK_PACKET.json", {"objective": "rejected steward repair"})
    write_json(tmp_path, f"{current}/ACTIVE_ROLE_SPAWN_PLAN.json", {"role_spawn_plan": []})
    write_json(tmp_path, f"{current}/ACTIVE_CARRIER_TURN_PACKET.json", {"objective": "rejected steward repair", "spawn_queue": []})
    write_json(tmp_path, f"{current}/ACTIVE_CARRIER_TASK_RETURN_LEDGER.json", {"records": []})
    write_json(
        tmp_path,
        f"{current}/ACTIVE_STEWARD_INTEGRATION_QUEUE.json",
        {
            "items": [
                {
                    "index": 1,
                    "role": "steward",
                    "status": "STEWARD_INTEGRATION_REJECTED",
                    "steward_gate_findings": ["missing_template_action_proof_heading"],
                }
            ]
        },
    )
    write_json(tmp_path, f"{current}/ACTIVE_OPERATOR_MESSAGE_QUEUE.json", {"items": []})
    write_json(tmp_path, f"{current}/ACTIVE_HUMAN_GATE_QUEUE.json", {"gates": []})
    write_json(
        tmp_path,
        f"{current}/V108_V72_MCP_DONOR_RECONCILIATION_AUDIT.json",
        {
            "reconciliation_verdict": "V72_MCP_DONOR_RECONCILIATION_PASS",
            "missing_donor_surface_count": 0,
            "forbidden_runtime_file_count": 0,
            "production_authority": False,
            "live_execution_authority": False,
        },
    )
    (tmp_path / "pyproject.toml").write_text("[project]\nname='mount-test'\n", encoding="utf-8")
    (tmp_path / "ION/03_registry/boots").mkdir(parents=True, exist_ok=True)
    (tmp_path / "ION/04_packages/kernel").mkdir(parents=True, exist_ok=True)
    authority = tmp_path / "ION/REPO_AUTHORITY.md"
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("authority\n", encoding="utf-8")

    status = build_ion_status(tmp_path)

    assert status["verdict"] == "ION_STATUS_SINGLE_CARRIER_READY"
    assert status["steward_queue_rejected_count"] == 1
    assert status["next_lawful_action"] == "repair_rejected_steward_integration"


def test_status_treats_later_integrated_steward_item_as_superseding_rejection(tmp_path):
    current = "ION/05_context/current"
    write_json(tmp_path, f"{current}/ACTIVE_CURSOR_HOOK_STATE.json", {"status": "projected_not_connected"})
    write_json(tmp_path, f"{current}/ACTIVE_WORK_PACKET.json", {"objective": "repaired steward return"})
    write_json(tmp_path, f"{current}/ACTIVE_ROLE_SPAWN_PLAN.json", {"role_spawn_plan": []})
    write_json(tmp_path, f"{current}/ACTIVE_CARRIER_TURN_PACKET.json", {"objective": "repaired steward return", "spawn_queue": []})
    write_json(tmp_path, f"{current}/ACTIVE_CARRIER_TASK_RETURN_LEDGER.json", {"records": []})
    write_json(
        tmp_path,
        f"{current}/ACTIVE_STEWARD_INTEGRATION_QUEUE.json",
        {
            "items": [
                {"index": 1, "role": "steward", "status": "STEWARD_INTEGRATION_REJECTED"},
                {"index": 1, "role": "steward", "status": "STEWARD_INTEGRATED", "accepted": True},
            ]
        },
    )
    write_json(tmp_path, f"{current}/ACTIVE_OPERATOR_MESSAGE_QUEUE.json", {"items": []})
    write_json(tmp_path, f"{current}/ACTIVE_HUMAN_GATE_QUEUE.json", {"gates": []})
    write_json(
        tmp_path,
        f"{current}/V108_V72_MCP_DONOR_RECONCILIATION_AUDIT.json",
        {
            "reconciliation_verdict": "V72_MCP_DONOR_RECONCILIATION_PASS",
            "missing_donor_surface_count": 0,
            "forbidden_runtime_file_count": 0,
            "production_authority": False,
            "live_execution_authority": False,
        },
    )
    (tmp_path / "pyproject.toml").write_text("[project]\nname='mount-test'\n", encoding="utf-8")
    (tmp_path / "ION/03_registry/boots").mkdir(parents=True, exist_ok=True)
    (tmp_path / "ION/04_packages/kernel").mkdir(parents=True, exist_ok=True)
    authority = tmp_path / "ION/REPO_AUTHORITY.md"
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("authority\n", encoding="utf-8")

    status = build_ion_status(tmp_path)

    assert status["steward_queue_rejected_count"] == 0
    assert status["next_lawful_action"] == "continue_or_queue_new_work"


def test_status_does_not_count_completed_role_as_deferred(tmp_path):
    current = "ION/05_context/current"
    write_json(tmp_path, f"{current}/ACTIVE_CURSOR_HOOK_STATE.json", {"status": "projected_not_connected"})
    write_json(tmp_path, f"{current}/ACTIVE_WORK_PACKET.json", {"objective": "completed role projection"})
    write_json(
        tmp_path,
        f"{current}/ACTIVE_ROLE_SPAWN_PLAN.json",
        {
            "execution_bundle_materialized": True,
            "role_spawn_plan": [
                {"index": 1, "role": "steward", "spawn": False, "spawn_intent": True, "completion_status": "ALREADY_INTEGRATED"},
                {"index": 2, "role": "vizier", "spawn": True, "spawn_intent": True},
                {"index": 3, "role": "mason", "spawn": False, "spawn_intent": True, "spawn_deferral_reason": "deferred_by_spawn_row_limit"},
            ],
        },
    )
    write_json(
        tmp_path,
        f"{current}/ACTIVE_CARRIER_TURN_PACKET.json",
        {"objective": "completed role projection", "spawn_queue": [{"index": 2, "role": "vizier"}]},
    )
    write_json(tmp_path, f"{current}/ACTIVE_CARRIER_TASK_RETURN_LEDGER.json", {"records": []})
    write_json(tmp_path, f"{current}/ACTIVE_STEWARD_INTEGRATION_QUEUE.json", {"items": []})
    write_json(tmp_path, f"{current}/ACTIVE_OPERATOR_MESSAGE_QUEUE.json", {"items": []})
    write_json(tmp_path, f"{current}/ACTIVE_HUMAN_GATE_QUEUE.json", {"gates": []})
    write_json(
        tmp_path,
        f"{current}/V108_V72_MCP_DONOR_RECONCILIATION_AUDIT.json",
        {
            "reconciliation_verdict": "V72_MCP_DONOR_RECONCILIATION_PASS",
            "missing_donor_surface_count": 0,
            "forbidden_runtime_file_count": 0,
            "production_authority": False,
            "live_execution_authority": False,
        },
    )
    (tmp_path / "pyproject.toml").write_text("[project]\nname='mount-test'\n", encoding="utf-8")
    (tmp_path / "ION/03_registry/boots").mkdir(parents=True, exist_ok=True)
    (tmp_path / "ION/04_packages/kernel").mkdir(parents=True, exist_ok=True)
    authority = tmp_path / "ION/REPO_AUTHORITY.md"
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("authority\n", encoding="utf-8")

    status = build_ion_status(tmp_path)

    assert status["completed_role_count"] == 1
    assert status["plan_spawn_count"] == 1
    assert status["deferred_spawn_count"] == 1
    assert status["next_lawful_action"] == "execute_spawn_rows_and_run_task_return_intake"


def test_ion_status_full_readiness_is_not_inferred_from_absence_of_blockers(tmp_path, monkeypatch):
    seed_ready_status(tmp_path, active_created_at="2026-05-16T20:00:00+00:00", queue_items=[])

    def accepted_but_unproved_full_profile(root):
        return {
            "schema_id": "ion.truth_gates.v1",
            "status": "TRUTH_GATES_READY",
            "verdict": "ION_STATUS_TRUTH_GATES_READY",
            "accepted": True,
            "blocker_count": 0,
            "blockers": [],
            "security_boundary": {"accepted": True, "blocker_count": 0, "findings": []},
            "package_profile": {
                "accepted": True,
                "profile_id": "future_full_profile",
                "status": "PACKAGE_PROFILE_READY",
                "status_ceiling": "FULL_READY_ONLY",
                "blocker_count": 0,
                "blockers": [],
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
            },
            "dependency_gate": {"accepted": True, "blocker_count": 0, "blockers": []},
            "test_gate": {"accepted": True, "blocker_count": 0, "blockers": []},
            "currentness_gate": {"accepted": True, "blocker_count": 0, "blockers": []},
            "secret_values_emitted": False,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }

    monkeypatch.setattr(ion_status_module, "evaluate_truth_gates", accepted_but_unproved_full_profile)

    status = build_ion_status(tmp_path)

    assert status["legacy_verdict_without_truth_gates"] == "ION_STATUS_READY"
    assert status["verdict"] == "ION_STATUS_PROFILE_SCOPE_BLOCKED"
    assert status["verdict"] != "ION_STATUS_READY"
    assert status["profile_id"] == "future_full_profile"
    assert status["status_ceiling"] == "FULL_READY_ONLY"
    assert status["next_lawful_action"] == "repair_profile_readiness_scope"
