import hashlib
import json
import os
import zipfile
from pathlib import Path

from kernel.ion_agent_control_plane import build_agent_control_plane_projection
from kernel.ion_context_starter_capsule import create_context_starter_capsule, materialize_context_starter_capsule
from kernel.ion_automation_control_plane import CONFIRMATION, build_automation_control_plane, execute_automation_action
from kernel.ion_codex_agent_mount import PORTABLE_ADDRESS_BOOK, export_portable_agent_domain_package, materialize_codex_agent_mount
from kernel.ion_domain_weaver import (
    DOMAIN_WEAVER_DOGFOOD_CONTEXT_CAPSULE_PATH,
    DOMAIN_WEAVER_DOGFOOD_NEXT_PACKET_PATH,
    DOMAIN_WEAVER_EXACT_REISSUE_REQUEST_DISPATCH_FANIN_PATH,
    DOMAIN_WEAVER_ACTION_HISTORY_VISUAL_SMOKE_RECEIPT_PATH,
    DOMAIN_WEAVER_APPROVAL_DECISION_LEDGER_PATH,
    DOMAIN_WEAVER_APPROVAL_GOVERNOR_POLICY_PATH,
    DOMAIN_WEAVER_ACTIVATION_LEDGER_PATH,
    DOMAIN_WEAVER_ACTIVATION_DECISION_SCHEMA_PATH,
    DOMAIN_WEAVER_ACTIVATION_REQUEST_SCHEMA_PATH,
    DOMAIN_WEAVER_FISSION_DRYRUN_PROPOSAL_PATH,
    DOMAIN_WEAVER_FISSION_TEMPLATE_LIBRARY_PATH,
    DOMAIN_WEAVER_TOPOLOGY_AUDIT_PATH,
    DOMAIN_WEAVER_TOPOLOGY_CONTROL_POLICY_PATH,
    DOMAIN_WEAVER_DYNAMIC_SWARM_OPERATION_PLAN_PATH,
    DOMAIN_WEAVER_DYNAMIC_SWARM_CANDIDATE_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_DYNAMIC_SWARM_FRESH_CONTEXT_RECONCILIATION_PATH,
    DOMAIN_WEAVER_DYNAMIC_SWARM_FANIN_REISSUE_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_DYNAMIC_SWARM_SEMANTIC_BLOCKER_READINESS_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_DYNAMIC_SWARM_SEMANTIC_BLOCKER_READINESS_PACKET_ID,
    DOMAIN_WEAVER_DYNAMIC_SWARM_CONTEXT_DUPLICATE_LIFECYCLE_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_DYNAMIC_SWARM_CONTEXT_DUPLICATE_LIFECYCLE_PACKET_ID,
    DOMAIN_WEAVER_DYNAMIC_SWARM_FRESH_CURRENT_LIFECYCLE_SETTLEMENT_PATH,
    DOMAIN_WEAVER_DYNAMIC_SWARM_FRESH_CURRENT_LIFECYCLE_PACKET_ID,
    DOMAIN_WEAVER_TOPOLOGY_EVOLUTION_READINESS_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_TOPOLOGY_EVOLUTION_READINESS_PACKET_ID,
    DOMAIN_WEAVER_TOPOLOGY_CHILD_OWNERSHIP_PREFLIGHT_PATH,
    DOMAIN_WEAVER_TOPOLOGY_CHILD_OWNERSHIP_PREFLIGHT_PACKET_ID,
    DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_AUDIT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_AUDIT_PACKET_ID,
    DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_CYCLE2_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_CYCLE2_PACKET_ID,
    DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_CYCLE3_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_CYCLE3_PACKET_ID,
    DOMAIN_WEAVER_POST_FISSION_OBSERVATION_FANIN_MATERIALIZATION_STOP_PATH,
    DOMAIN_WEAVER_POST_FISSION_OBSERVATION_FANIN_MATERIALIZATION_STOP_PACKET_ID,
    DOMAIN_WEAVER_FANOUT_FANIN_SETTLEMENT_PATH,
    DOMAIN_WEAVER_FOUNDING_ASSEMBLY_PATH,
    DOMAIN_WEAVER_FOUNDING_ASSEMBLY_MD_PATH,
    DOMAIN_WEAVER_FOUNDING_ASSEMBLY_NEMESIS_AUDIT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_FOUNDATION_WAVE0_FANIN_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_FOUNDATION_WAVE0_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_FOUNDATION_WAVE0_REBASELINE_PLAN_PATH,
    DOMAIN_WEAVER_FOUNDATION_WAVE0_REISSUE_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE1_BOUNDED_DRAFT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE1_CANDIDATE_FANOUT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE1_CANDIDATE_FANOUT_WORKER_START_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE1_CANDIDATE_FANIN_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE1_STEWARD_DECISION_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE2_DRAFT_GATE_DECISION_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE2_TRACK_FANOUT_MATERIALIZATION_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE2_CANDIDATE_TRACK_FANOUT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE2_CANDIDATE_TRACK_FANIN_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE2_CANDIDATE_TRACK_WORKER_START_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE2_SCHEDULER_LIFECYCLE_REISSUE_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE2_CANDIDATE_TRACK_FANIN_RETRY_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_PREVIEW_PATH,
    DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_ROLLBACK_MATRIX_PATH,
    DOMAIN_WEAVER_WAVE2_APPROVAL_AND_LIMITS_LEDGER_SCHEMA_PATH,
    DOMAIN_WEAVER_WAVE2_SOURCE_PATCH_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_PREVIEW_SETTLEMENT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE2_CANDIDATE_SOURCE_PATCH_SETTLEMENT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE2_SOURCE_PATCH_MERGE_NEXT_READINESS_GATE_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE2_ACCEPTED_STATE_SETTLEMENT_GATE_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE2_ACCEPTED_STATE_MOVEMENT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE2_AUTHORITY_RECEIPT_REPAIR_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_WAVE2_AUTHORITY_RECEIPT_ISSUANCE_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_LIVE_CARRIER_BINDING_PLAN_PATH,
    DOMAIN_WEAVER_LIVE_CARRIER_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_LIVE_FANIN_20260601B_CONTEXT_REBASELINE_PLAN_PATH,
    DOMAIN_WEAVER_LIVE_FANIN_20260601B_DYNAMIC_REFERENCE_REISSUE_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_LIVE_FANIN_20260601B_REISSUE_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_LIVE_FANIN_SETTLEMENT_PATH,
    DOMAIN_WEAVER_LIVE_FANIN_SEMANTIC_REPIN_PLAN_PATH,
    DOMAIN_WEAVER_LIVE_FANIN_SEMANTIC_SETTLEMENT_PATH,
    DOMAIN_WEAVER_LIVE_RETURN_MONITOR_PATH,
    DOMAIN_WEAVER_ARCHITECTURE_BREACH_AUDIT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_NATIVE_UI_DEVELOPMENT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_UI_SPECIALIST_ROUTE_FANOUT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_UI_SPECIALIST_FANIN_RETRY_GATE_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_UI_IMPLEMENTATION_RETRY_GATE_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_UI_VISUAL_PROOF_STEWARDSHIP_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_UI_SEMANTIC_REDESIGN_FANOUT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_OPERATOR_REJECTION_QUALITY_REDESIGN_FANOUT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_OPERATOR_REJECTION_QUALITY_REDESIGN_FANIN_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_OPERATOR_REJECTION_ACTIVITY_CITY_STATIC_MOCK_PROOF_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_OPERATOR_REJECTION_ACTIVITY_CITY_IMPLEMENTATION_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_OPERATOR_REJECTION_ACTIVITY_CITY_SERVED_ROUTE_PROOF_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_OPERATOR_REJECTION_ACTIVITY_CITY_QUALITY_REPAIR_FANOUT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_OPERATOR_REJECTION_ACTIVITY_CITY_QUALITY_REPAIR_STATIC_MOCKUP_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_UI_SEMANTIC_REDESIGN_FANIN_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_UI_SEMANTIC_REDESIGN_MOCK_PROOF_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_UI_SEMANTIC_REDESIGN_IMPLEMENTATION_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_UI_ACTIVITY_CITY_CANDIDATE_PATCH_RECOVERY_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_UI_ACTIVITY_CITY_VISUAL_PROOF_RECOVERY_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_UI_ACTIVITY_CITY_RESPONSIVE_REPAIR_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_UI_ACTIVITY_CITY_OPERATOR_REVIEW_HYDRATION_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_VISUAL_PROOF_LIVE_HYDRATION_OPERATOR_REJECTION_SETTLEMENT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_VISUAL_PROOF_LIVE_HYDRATION_OPERATOR_REJECTION_SETTLEMENT_RESULT_PATH,
    DOMAIN_WEAVER_ROUTE_EXECUTION_GATE_PATH,
    DOMAIN_WEAVER_ROUTE_EXECUTION_HARD_GATE_REAUDIT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_PHASE_CLOSURE_REVIEW_PATH,
    DOMAIN_WEAVER_PROJECTION_PATH,
    DOMAIN_WEAVER_RECURSIVE_CYCLE_READINESS_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_RECURSIVE_CYCLE_READINESS_RESULT_PATH,
    DOMAIN_WEAVER_RECURSIVE_LIVE_FANOUT_CHAIN_SELECTION_PATH,
    DOMAIN_WEAVER_RECURSIVE_LIVE_FANOUT_CHAIN_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_FISSION_REFLEX_BINDING_TEMPLATE_MATERIALIZATION_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_FISSION_REFLEX_BINDING_FANOUT_WORKER_START_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_FISSION_REFLEX_BINDING_FANIN_SETTLEMENT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_FISSION_REFLEX_BINDING_FANIN_SETTLEMENT_RESULT_PATH,
    DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_MATERIALIZATION_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_WORKER_START_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_FANIN_SETTLEMENT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_FANIN_SETTLEMENT_RESULT_PATH,
    DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_UI_CANON_REISSUE_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_UI_CANON_REISSUE_FANIN_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_UI_CANON_REISSUE_FANIN_RESULT_PATH,
    DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_ACTIVE_BINDING_READINESS_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_ACTIVE_BINDING_READINESS_RESULT_PATH,
    DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_EXACT_ACTIVE_BINDING_REMEDIATION_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_EXACT_ACTIVE_BINDING_REMEDIATION_RESULT_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_PROOF_MATRIX_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_PROOF_MATRIX_RESULT_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_AUTHORITY_SETTLEMENT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_AUTHORITY_SETTLEMENT_RESULT_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_MATERIALIZATION_GATE_REPAIR_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_MATERIALIZATION_GATE_REPAIR_RESULT_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_ACTIVATION_OR_DELEGATED_SUBSTITUTION_REPAIR_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_ACTIVATION_OR_DELEGATED_SUBSTITUTION_REPAIR_RESULT_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_ACTIVATION_GATE_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_ACTIVATION_GATE_RESULT_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_REQUEST_MATERIALIZATION_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_REQUEST_MATERIALIZATION_RESULT_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_WORKER_START_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_RETURN_MONITOR_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_FANIN_SETTLEMENT_RESULT_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_FANIN_BLOCKER_REPAIR_PLAN_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_FANIN_BLOCKER_REPAIR_PACKET_ID,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANOUT_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANOUT_PACKET_ID,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_CONTEXT_REISSUE_QUEUE_LEDGER_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_CONTEXT_REISSUE_PACKET_ID,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_RETURN_MONITOR_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANIN_SETTLEMENT_RESULT_PATH,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANIN_PACKET_ID,
    DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_STRUCTURED_GATE_SOURCE_PATCH_PACKET_ID,
    DOMAIN_WEAVER_CHAIN_SEQUENCE_REBASELINE_LEDGER_PATH,
    DOMAIN_WEAVER_STALE_WAITING_RECONCILIATION_LEDGER_PATH,
    DOMAIN_WEAVER_WAITING_ACCEPTED_SUCCESSOR_RECONCILIATION_LEDGER_PATH,
    DOMAIN_WEAVER_UI_OPERATOR_FEEDBACK_PATH,
    DOMAIN_WEAVER_OPERATOR_ACTION_HISTORY_PATH,
    DOMAIN_WEAVER_PROMOTION_GATE_PATH,
    DOMAIN_WEAVER_PROMOTION_REVIEW_PATH,
    DOMAIN_WEAVER_STEWARD_READY_REVIEW_PATH,
    DOMAIN_WEAVER_UI_CANON_CONTEXT_PATHS,
    build_domain_weaver_projection,
    execute_domain_weaver_action,
    materialize_domain_weaver_founding_domain_assembly,
    materialize_domain_weaver_dogfood_context_capsule,
    materialize_domain_weaver_promotion_gate,
    materialize_domain_weaver_projection,
    materialize_domain_weaver_promotion_review,
    materialize_domain_weaver_phase_closure_review,
    materialize_domain_weaver_steward_ready_review,
    _domain_weaver_five_specialist_exact_active_binding_request_materialization_templates,
    _domain_weaver_latest_pointer_lineage_summary,
    _domain_weaver_bind_latest_pointer_self_lineage,
    _domain_weaver_latest_pointer_self_lineage_summary,
    _domain_weaver_latest_exact_active_specialist_binding_kernel_repair_fanin_settlement_result,
    _domain_weaver_materialize_latest_with_snapshot,
)
from kernel.ion_queue_governor import build_queue_governor_dogfood_projection, build_queue_governor_projection


def _write(root: Path, rel: str, text: str = "x\n") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_domain_weaver_latest_pointer_lineage_summary_enforces_strict_current_action(tmp_path: Path):
    latest_path = Path("ION/05_context/current/domain_weaver/live_carrier_binding/TEST.latest.json")
    payload = {"schema_id": "test.latest", "value": 1}

    lineage = _domain_weaver_materialize_latest_with_snapshot(
        tmp_path,
        latest_path=latest_path,
        payload=payload,
        artifact_role="test_latest",
        source_action_id="test_action",
        source_packet_id="test_packet",
    )

    clean = _domain_weaver_latest_pointer_lineage_summary(
        {"test": lineage},
        root=tmp_path,
        expected_source_action_id="test_action",
        expected_source_packet_id="test_packet",
        require_current_action_lineage=True,
    )
    assert clean["lineage_status"] == "reconciled"
    assert clean["strict_latest_pointer_lineage_gate_clean"] is True
    assert clean["operator_action_latest_pointer_unreconciled"] is False

    mismatched_packet = _domain_weaver_latest_pointer_lineage_summary(
        {"test": lineage},
        root=tmp_path,
        expected_source_action_id="test_action",
        expected_source_packet_id="other_packet",
        require_current_action_lineage=True,
    )
    assert mismatched_packet["lineage_status"] == "unreconciled"
    assert "test_source_packet_id_mismatch" in set(mismatched_packet["lineage_blockers"])

    latest_file = tmp_path / latest_path
    changed = json.loads(latest_file.read_text(encoding="utf-8"))
    changed["value"] = 2
    latest_file.write_text(json.dumps(changed, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    drift = _domain_weaver_latest_pointer_lineage_summary(
        {"test": lineage},
        root=tmp_path,
        expected_source_action_id="test_action",
        expected_source_packet_id="test_packet",
        require_current_action_lineage=True,
    )
    blockers = set(drift["lineage_blockers"])
    assert drift["lineage_status"] == "unreconciled"
    assert drift["operator_action_latest_pointer_unreconciled"] is True
    assert "test_current_latest_full_sha256_mismatch" in blockers
    assert "test_current_latest_payload_sha256_mismatch" in blockers


def test_domain_weaver_latest_pointer_lineage_summary_blocks_missing_hashes_and_path_escape(tmp_path: Path):
    latest_path = Path("ION/05_context/current/domain_weaver/live_carrier_binding/TEST.latest.json")
    lineage = _domain_weaver_materialize_latest_with_snapshot(
        tmp_path,
        latest_path=latest_path,
        payload={"schema_id": "test.latest", "value": 1},
        artifact_role="test_latest",
        source_action_id="test_action",
        source_packet_id="test_packet",
    )

    missing_hashes = dict(lineage)
    for key in (
        "latest_full_sha256_at_action",
        "current_latest_full_sha256_at_action",
        "latest_sha256",
        "restored_latest_sha256",
        "preserved_latest_sha256",
        "latest_payload_sha256_at_action",
        "latest_payload_sha256",
        "snapshot_payload_sha256",
    ):
        missing_hashes.pop(key, None)
    missing_summary = _domain_weaver_latest_pointer_lineage_summary(
        {"test": missing_hashes},
        root=tmp_path,
        expected_source_action_id="test_action",
        expected_source_packet_id="test_packet",
        require_current_action_lineage=True,
    )
    missing_blockers = set(missing_summary["lineage_blockers"])
    assert "test_latest_full_sha256_expected_missing" in missing_blockers
    assert "test_latest_payload_sha256_expected_missing" in missing_blockers
    assert "test_snapshot_payload_sha256_expected_missing" in missing_blockers

    escaped = dict(lineage)
    escaped["latest_path"] = "../outside.json"
    escaped_summary = _domain_weaver_latest_pointer_lineage_summary(
        {"test": escaped},
        root=tmp_path,
        expected_source_action_id="test_action",
        expected_source_packet_id="test_packet",
        require_current_action_lineage=True,
    )
    assert "test_latest_path_outside_root" in set(escaped_summary["lineage_blockers"])


def test_domain_weaver_latest_pointer_readback_blocks_volatile_preserved_and_restored_lineage(tmp_path: Path):
    latest_path = Path("ION/05_context/current/domain_weaver/live_carrier_binding/TEST.latest.json")
    action_lineage = _domain_weaver_materialize_latest_with_snapshot(
        tmp_path,
        latest_path=latest_path,
        payload={"schema_id": "test.latest", "value": 1},
        artifact_role="test_latest",
        source_action_id="test_action",
        source_packet_id="test_packet",
    )

    preserved_lineage = _domain_weaver_materialize_latest_with_snapshot(
        tmp_path,
        latest_path=latest_path,
        payload={"schema_id": "test.latest", "value": 2},
        artifact_role="test_latest",
    )
    latest_payload = json.loads((tmp_path / latest_path).read_text(encoding="utf-8"))
    assert latest_payload["value"] == 1
    assert preserved_lineage["lineage_status"] == "snapshot_only_preserved_action_sourced_latest"
    preserved_summary = _domain_weaver_latest_pointer_lineage_summary(
        {"preserved": preserved_lineage},
        root=tmp_path,
        expected_source_action_id="test_action",
        expected_source_packet_id="test_packet",
        require_current_action_lineage=True,
    )
    preserved_blockers = set(preserved_summary["lineage_blockers"])
    assert "preserved_lineage_status_not_reconciled" in preserved_blockers
    assert "preserved_latest_write_suppressed" in preserved_blockers
    assert "preserved_latest_write_decision_not_written" in preserved_blockers

    clean_action = _domain_weaver_latest_pointer_lineage_summary(
        {"action": action_lineage},
        root=tmp_path,
        expected_source_action_id="test_action",
        expected_source_packet_id="test_packet",
        require_current_action_lineage=True,
    )
    assert clean_action["strict_latest_pointer_lineage_gate_clean"] is True

    (tmp_path / latest_path).write_text(
        json.dumps({"schema_id": "test.latest", "value": 99}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    restored_lineage = _domain_weaver_materialize_latest_with_snapshot(
        tmp_path,
        latest_path=latest_path,
        payload={"schema_id": "test.latest", "value": 3},
        artifact_role="test_latest",
    )
    latest_payload = json.loads((tmp_path / latest_path).read_text(encoding="utf-8"))
    assert latest_payload["value"] == 1
    assert restored_lineage["lineage_status"] == "snapshot_only_restored_action_sourced_latest"
    restored_summary = _domain_weaver_latest_pointer_lineage_summary(
        {"restored": restored_lineage},
        root=tmp_path,
        expected_source_action_id="test_action",
        expected_source_packet_id="test_packet",
        require_current_action_lineage=True,
    )
    restored_blockers = set(restored_summary["lineage_blockers"])
    assert "restored_lineage_status_not_reconciled" in restored_blockers
    assert "restored_latest_write_suppressed" in restored_blockers
    assert "restored_latest_write_decision_not_written" in restored_blockers


def test_domain_weaver_latest_pointer_self_lineage_binds_sidecar_and_detects_mutation(tmp_path: Path):
    latest_path = Path("ION/05_context/current/domain_weaver/queue_governance/TEST_FANIN.latest.json")
    _write(
        tmp_path,
        latest_path.as_posix(),
        json.dumps(
            {
                "schema_id": "test.fanin",
                "status": "candidate_current_sha_fields_reconciled_not_self_lineaged",
                "verdict": "READY_FOR_LIMITED_SWARM_WATCH_AND_FANOUT",
                "ready_for_limited_exact_path_swarm": True,
                "ready_for_broader_swarm": False,
                "ready_for_production": False,
                "receipt_integrity_readback": {
                    "strict_self_lineage_bound": False,
                    "advance_to_limited_swarm_allowed_by_this_readback": False,
                    "readback_blockers": [
                        "final_fanin_latest_not_latest_pointer_self_lineaged",
                        "historical_broader_overclaim_test_fails_before_strict_lineage_assertions",
                    ],
                },
                "accepted_state_claimed": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    result = _domain_weaver_bind_latest_pointer_self_lineage(
        tmp_path,
        latest_path=latest_path,
        artifact_role="test_fanin",
        source_action_id="bind_final_fanin_latest_pointer_self_lineage",
        source_packet_id="test_packet",
    )

    assert result["ok"] is True
    assert result["lineage_status"] == "reconciled"
    assert (tmp_path / result["sidecar_receipt_path"]).is_file()
    latest_payload = json.loads((tmp_path / latest_path).read_text(encoding="utf-8"))
    integrity = latest_payload["receipt_integrity_readback"]
    assert integrity["strict_self_lineage_bound"] is True
    assert "final_fanin_latest_not_latest_pointer_self_lineaged" not in integrity["readback_blockers"]
    assert latest_payload["ready_for_limited_exact_path_swarm"] is False
    lineage = latest_payload["latest_pointer_self_lineage"]
    assert lineage["lineage_status"] == "bound_external_sidecar"
    assert "latest_full_sha256" not in lineage

    clean = _domain_weaver_latest_pointer_self_lineage_summary(
        tmp_path,
        latest_path=latest_path,
        expected_source_action_id="bind_final_fanin_latest_pointer_self_lineage",
        expected_source_packet_id="test_packet",
    )
    assert clean["strict_self_lineage_gate_clean"] is True

    latest_payload["status"] = "mutated_after_sidecar"
    (tmp_path / latest_path).write_text(
        json.dumps(latest_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    drift = _domain_weaver_latest_pointer_self_lineage_summary(
        tmp_path,
        latest_path=latest_path,
        expected_source_action_id="bind_final_fanin_latest_pointer_self_lineage",
        expected_source_packet_id="test_packet",
    )
    blockers = set(drift["lineage_blockers"])
    assert drift["lineage_status"] == "unreconciled"
    assert "canonical_payload_sha256_mismatch" in blockers
    assert "sidecar_latest_full_sha256_mismatch" in blockers


def test_domain_weaver_exact_active_fanin_summary_separates_dynamic_reference_drift(tmp_path: Path):
    rows = []
    for index, role in enumerate(("role.steward", "role.codex_carrier_steward", "role.nemesis", "role.scribe"), start=1):
        request_rel = f"ION/05_context/current/chatgpt_connector/codex_work_requests/test_exact_dynamic_{index}.json"
        return_rel = f"ION/05_context/current/chatgpt_connector/task_returns/test_exact_dynamic_{index}.json"
        body_rel = f"ION/05_context/current/chatgpt_connector/codex_queue_runs/test_exact_dynamic_{index}/task_return_body.md"
        _write(
            tmp_path,
            request_rel,
            json.dumps(
                {
                    "request_id": f"test_exact_dynamic_{index}",
                    "requested_authority": {
                        "accepted_state_claim": False,
                        "production_authority": False,
                        "live_execution_authority": False,
                    },
                    "accepted_state_claim": False,
                    "production_authority": False,
                    "live_execution_authority": False,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "accepted_for_carrier_intake": True,
                    "accepted_state_claim": False,
                    "production_authority": False,
                    "live_execution_authority": False,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        _write(
            tmp_path,
            body_rel,
            "### RESULT\ncandidate repair delta only\nno source mutation\nsource files were not mutated\n",
        )
        rows.append(
            {
                "request_id": f"test_exact_dynamic_{index}",
                "request_path": request_rel,
                "agent_role": role,
                "accepted_return": True,
                "carrier_clean": True,
                "context_proof_accepted": True,
                "template_action_proof_accepted": True,
                "workload_diff_accepted": True,
                "machine_gate_clean": True,
                "worker_context_awareness_receipt_path": (
                    f"ION/05_context/current/chatgpt_connector/codex_queue_runs/"
                    f"test_exact_dynamic_{index}/worker_context_awareness_receipt.json"
                ),
                "task_return_body_path": body_rel,
                "latest_return_packet_path": return_rel,
                "context_hash_drift_count": 0,
                "context_hash_drift_paths": [],
                "dynamic_context_reference_drift_count": 2,
                "dynamic_context_reference_drift_paths": [
                    "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json",
                    "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json",
                ],
                "required_output_presence": {"proof_graph": True},
            }
        )

    settlement = _domain_weaver_latest_exact_active_specialist_binding_kernel_repair_fanin_settlement_result(
        tmp_path,
        return_monitor={
            "summary": {"expected_return_count": 4},
            "observed_returns": rows,
        },
    )

    assert settlement["summary"]["machine_gate_clean"] is True
    assert settlement["summary"]["semantic_blocker_count"] == 0
    assert settlement["summary"]["blocking_context_drift_count"] == 0
    assert settlement["summary"]["dynamic_context_drift_count"] == 8
    assert settlement["summary"]["dynamic_context_reference_drift_return_count"] == 4
    assert settlement["summary"]["dynamic_context_reference_drift_path_count"] == 8


def _write_worker_awareness_for_request(root: Path, request: dict) -> None:
    request_id = request["request_id"]
    request_path = request["packet_path"]
    run_dir = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"fake_run_{request_id}"
    )
    run_path = f"{run_dir}/run.json"
    awareness_path = f"{run_dir}/worker_context_awareness_receipt.json"
    reads = [
        {
            "path": path,
            "required": True,
            "status": "READY",
            "sha256": "0" * 64,
            "excerpt": "test context",
        }
        for path in request.get("required_context_reads", [])
    ]
    _write(
        root,
        awareness_path,
        json.dumps(
            {
                "schema_id": "ion.worker_context_awareness_receipt.v1",
                "status": "WORKER_CONTEXT_ACKNOWLEDGED",
                "request_id": request_id,
                "selected_model": request["requested_model"],
                "selected_reasoning_effort": request["requested_reasoning_effort"],
                "required_context_reads": reads,
                "missing_required_context_paths": [],
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        root,
        run_path,
        json.dumps(
            {
                "schema_id": "ion.codex_queue_run.v1",
                "status": request["status"],
                "request_id": request_id,
                "request_path": request_path,
                "worker_context_awareness_receipt_path": awareness_path,
            },
            indent=2,
        )
        + "\n",
    )


def _seed_root(root: Path) -> None:
    _write(root, "pyproject.toml", "[project]\nname = \"ion-agent-control-test\"\n")
    _write(root, "ION/REPO_AUTHORITY.md", "# authority\n")
    for rel in DOMAIN_WEAVER_UI_CANON_CONTEXT_PATHS:
        _write(root, rel.as_posix(), f"# {rel.stem}\n")
    for rel in [
        "ION/03_registry/codex_cli_carrier_profile.yaml",
        "ION/07_templates/carriers/CODEX_CLI_EXECUTION_PACKET.md",
        "ION/02_architecture/ION_FULL_CARRIER_MCP_PARITY_PROTOCOL.md",
        "ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py",
        "ION/04_packages/kernel/ion_codex_queue_runner.py",
        "ION/04_packages/kernel/ion_agent_invocation_broker.py",
    ]:
        _write(root, rel)
    _write(
        root,
        "ION/03_registry/agent_context_system_registry.yaml",
        "\n".join(
            [
                "registry_id: ion.agent_context_system_registry.v1",
                "legacy_surfaces_policy:",
                "  required_package_phrase: MINI/CAPSULE are witness inputs, not primary context authority. The active package is the operative context for this run.",
                "agents:",
                "  - role_id: role.mason",
                "    display_name: MASON",
                "    context_system_card: ION/05_context/current/agent_context_systems/MASON.context_system.md",
                "    base_sources:",
                "      - ION/agents/mason/MINI.md",
                "    package_strategy: bounded implementation package",
                "    primary_templates:",
                "      - ION/07_templates/bindings/MASON__CODE.md",
                "context_specialists:",
                "  - role_id: role.context_cartographer",
                "    context_system_card: ION/05_context/current/agent_context_systems/CONTEXT_CARTOGRAPHER.context_system.md",
                "",
            ]
        ),
    )
    _write(root, "ION/03_registry/agent_roster_registry.yaml", "registry_id: current_phase.agent_roster_registry\n")
    for rel in [
        "ION/05_context/current/agent_context_systems/MASON.context_system.md",
        "ION/05_context/current/agent_context_systems/CONTEXT_CARTOGRAPHER.context_system.md",
        "ION/07_templates/bindings/MASON__CODE.md",
    ]:
        _write(root, rel, f"# {Path(rel).stem}\nAgent Context System\none-file-per-step\n")
    _write(
        root,
        "ION_VNEXT/06_context/domain_weave/dry_runs/M103I_VNEXT_DOMAIN_REGISTRY.candidate.yaml",
        "\n".join(
            [
                "schema_id: ion.domain_weave.vnext_domain_registry.v0_1_candidate",
                "domains:",
                "  ion_vnext_context:",
                "    paths:",
                "      - ION_VNEXT/06_context",
                "    purpose: Context and Domain Weave substrate.",
                "    fact_posture: inferred_candidate",
                "    suggested_steward_class: steward.context_continuity",
                "    maturity_estimate: W3_candidate_context_substrate",
                "    ready_for_future_steward_discovery_packet: true",
                "    requires_split_merge_review: true",
                "",
            ]
        ),
    )
    _write(root, "ION_VNEXT/06_context/domain_weave/README.md", "Status: candidate\n")


def _seed_clean_codex_queue(root: Path) -> None:
    _write(
        root,
        "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json",
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_queue.v1",
                "request_count": 0,
                "total_request_count": 0,
                "duplicate_group_count": 0,
                "requests": [],
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        root,
        "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json",
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": None,
                "active_runs": {},
                "active_lane_locks": {
                    "schema_id": "ion.codex_lane_lock_index.v0_1",
                    "same_lane_parallelism": 1,
                    "active_run_count": 0,
                },
                "concurrency": {
                    "schema_id": "ion.codex_worker_concurrency.v0_1",
                    "mode": "bounded_per_lane_workers",
                    "global_active_lock": False,
                    "same_lane_parallelism": 1,
                    "active_run_count": 0,
                },
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        root,
        "ION/05_context/current/chatgpt_connector/work_lanes/INDEX.json",
        json.dumps(
            {
                "schema_id": "ion.codex_work_lane_index.v0_1",
                "queued_request_count": 0,
                "executable_waiting_request_count": 0,
                "needs_triage_count": 0,
                "lane_counts": {
                    "architecture_lane": 0,
                    "audit_lane": 0,
                    "browser_lane": 0,
                    "comms_lane": 0,
                    "context_lane": 0,
                    "implementation_lane": 0,
                    "maintenance_lane": 0,
                    "needs_triage": 0,
                    "settlement_lane": 0,
                },
                "next_request_by_lane": {},
            },
            indent=2,
        )
        + "\n",
    )


def _seed_codex_solo_context(root: Path) -> None:
    codex_solo = root / "ION/05_context/current/codex_solo"
    codex_solo.mkdir(parents=True, exist_ok=True)
    _write(root, "ION/05_context/current/codex_solo/CAPSULE.md", "# capsule\n")
    _write(root, "ION/05_context/current/codex_solo/MINI.md", "# mini\n")
    _write(root, "ION/05_context/current/codex_solo/HOT_CONTEXT.md", "# hot\n")
    _write(root, "ION/05_context/current/codex_solo/LONG_HORIZON.json", json.dumps({"epoch_count": 1}) + "\n")
    _write(root, "ION/05_context/current/codex_solo/ROUTE.json", json.dumps({"entries": []}) + "\n")
    _write(
        root,
        "ION/05_context/current/codex_solo/STATUS.json",
        json.dumps(
            {
                "active_context": {
                    "context_packages_path": "ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json",
                    "minimum_context_path": "ION/05_context/current/codex_solo/CAPSULE.md",
                    "hot_context_path": "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
                    "long_horizon_path": "ION/05_context/current/codex_solo/LONG_HORIZON.json",
                },
                "authority": {
                    "production_authority": False,
                    "live_execution_authority": False,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        root,
        "ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json",
        json.dumps(
            {
                "schema_id": "ion.codex_solo_context_packages.v1",
                "generated_at": "2099-01-01T00:00:00+00:00",
                "production_authority": False,
                "live_execution_authority": False,
                "package_count": 3,
                "selected_by_default": [
                    "minimum_working_capsule",
                    "mini_lookup_index",
                    "mission_active_package",
                ],
                "packages": [
                    {
                        "package_id": "minimum_working_capsule",
                        "context_type": "active_short_horizon",
                        "load_policy": "always_inline_first",
                        "path_refs": ["ION/05_context/current/codex_solo/CAPSULE.md"],
                    },
                    {
                        "package_id": "mini_lookup_index",
                        "context_type": "receipt_lookup",
                        "load_policy": "index_only_not_primary_prompt",
                        "path_refs": ["ION/05_context/current/codex_solo/MINI.md"],
                    },
                    {
                        "package_id": "mission_active_package",
                        "context_type": "current_objective",
                        "load_policy": "injected_per_queue_or_chat_turn",
                        "path_refs": ["ION/05_context/current/codex_solo/HOT_CONTEXT.md"],
                    },
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def _seed_worker_start_context_mount(root: Path, lane_id: str) -> None:
    _seed_codex_solo_context(root)
    mount_id = f"role_context_cartographer__domain_context_active_resolver__{lane_id}"
    mount_root = root / "ION/05_context/current/codex_agent_mounts" / mount_id
    ion_dir = mount_root / ".ion"
    ion_dir.mkdir(parents=True, exist_ok=True)
    _write(
        root,
        f"ION/05_context/current/codex_agent_mounts/{mount_id}/ION_AGENT_MOUNT_MANIFEST.json",
        json.dumps(
            {
                "role_id": "role.context_cartographer",
                "domain_id": "domain.context_active_resolver",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    for name in (
        "ION_CONTEXT_CAPSULE.yaml",
        "AGENT.yaml",
        "DOMAIN.yaml",
        "RELATIONSHIPS.yaml",
        "COMMUNICATIONS.json",
        "ADDRESS_BOOK.json",
    ):
        _write(root, f"ION/05_context/current/codex_agent_mounts/{mount_id}/.ion/{name}", f"{name}\n")
    _write(root, f"ION/05_context/current/codex_agent_mounts/{mount_id}/.ion/ACTIVE_CONTEXT_PACKAGE.md", "active\n")
    _write(
        root,
        f"ION/05_context/current/codex_agent_mounts/{mount_id}/.ion/ACTIVE_CONTEXT_PACKAGE.json",
        json.dumps({"lane_id": lane_id}, indent=2, sort_keys=True) + "\n",
    )


def _seed_codex_carrier_steward(root: Path) -> None:
    registry_path = root / "ION/03_registry/agent_context_system_registry.yaml"
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            "context_specialists:",
            "\n".join(
                [
                    "  - role_id: role.codex_carrier_steward",
                    "    display_name: CODEX_CARRIER_STEWARD",
                    "    context_system_card: ION/05_context/current/agent_context_systems/CODEX_CARRIER_STEWARD.context_system.md",
                    "    base_sources:",
                    "      - ION/03_registry/boots/CODEX_CARRIER_STEWARD.boot.md",
                    "      - ION/03_registry/semantic_identities/CODEX_CARRIER_STEWARD.semantic.yaml",
                    "      - ION/03_registry/domains/domain.codex_carrier_sync.domain.yaml",
                    "      - ION/05_context/current/codex_carrier/README.md",
                    "      - ION/05_context/current/codex_skills_v0/MANIFEST.json",
                    "    package_strategy: Codex carrier substrate package with CLI/config/hook/skill/MCP/sandbox/session/mount proof",
                    "    default_active_package_class: CARRIER_CONTEXT_PACKAGE",
                    "    primary_templates:",
                    "      - ION/07_templates/carriers/CODEX_CLI_EXECUTION_PACKET.md",
                    "      - ION/07_templates/bindings/STEWARD__STATUS_REPORT.md",
                    "      - ION/07_templates/context/AGENT_CONTEXT_BUILD_STEP.md",
                    "context_specialists:",
                ]
            ),
        ),
        encoding="utf-8",
    )
    _write(
        root,
        "ION/03_registry/agent_roster_registry.yaml",
        "\n".join(
            [
                "registry_id: current_phase.agent_roster_registry",
                "roster_records:",
                "  - entity_id: role.codex_carrier_steward",
                "    display_name: Codex Carrier Steward",
                "    live_status: ACTIVE_FIRST_PASS",
                "    registry_primary_domain: domain.codex_carrier_sync",
                "    registry_secondary_domains:",
                "      - domain.current_phase_orchestration_management",
                "    default_mount_posture: CODEX_NATIVE_CARRIER_SUBSTRATE_CHASSIS",
                "    template_bindings:",
                "      - ION/07_templates/carriers/CODEX_CLI_EXECUTION_PACKET.md",
                "      - ION/07_templates/bindings/STEWARD__STATUS_REPORT.md",
                "    source_refs:",
                "      - ION/03_registry/boots/CODEX_CARRIER_STEWARD.boot.md",
                "      - ION/03_registry/semantic_identities/CODEX_CARRIER_STEWARD.semantic.yaml",
                "      - ION/03_registry/domains/domain.codex_carrier_sync.domain.yaml",
                "",
            ]
        ),
    )
    _write(
        root,
        "ION/03_registry/domains/domain.codex_carrier_sync.domain.yaml",
        "\n".join(
            [
                "domain_id: domain.codex_carrier_sync",
                "display_name: Codex Carrier Synchronization",
                "status: ACTIVE_FIRST_PASS",
                "authority: A3_OPERATIONAL",
                "mission: Codex CLI carrier substrate proof.",
                "primary_roles:",
                "  - CODEX_CARRIER_STEWARD",
                "owned_or_stewarded_surfaces:",
                "  - .codex/",
                "  - ION/04_packages/kernel/ion_codex_agent_mount.py",
                "  - ION/05_context/current/codex_agent_mounts/",
                "",
            ]
        ),
    )
    for rel in [
        "ION/03_registry/boots/CODEX_CARRIER_STEWARD.boot.md",
        "ION/03_registry/semantic_identities/CODEX_CARRIER_STEWARD.semantic.yaml",
        "ION/05_context/current/agent_context_systems/CODEX_CARRIER_STEWARD.context_system.md",
        "ION/05_context/current/codex_carrier/README.md",
        "ION/05_context/current/codex_skills_v0/MANIFEST.json",
        "ION/07_templates/bindings/STEWARD__STATUS_REPORT.md",
    ]:
        _write(root, rel, f"# {Path(rel).stem}\nAgent Context System\none-file-per-step\n")


def _seed_browser_dom_cartographer(root: Path) -> None:
    registry_path = root / "ION/03_registry/agent_context_system_registry.yaml"
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            "context_specialists:",
            "\n".join(
                [
                    "  - role_id: role.browser_dom_cartographer",
                    "    display_name: BROWSER_DOM_CARTOGRAPHER",
                    "    context_system_card: ION/05_context/current/agent_context_systems/BROWSER_DOM_CARTOGRAPHER.context_system.md",
                    "    base_sources:",
                    "      - ION/03_registry/boots/BROWSER_DOM_CARTOGRAPHER.boot.md",
                    "      - ION/03_registry/semantic_identities/BROWSER_DOM_CARTOGRAPHER.semantic.yaml",
                    "      - ION/03_registry/domains/domain.browser_dom_perception.domain.yaml",
                    "      - ION/05_context/current/browser_dom_perception_specialist/RESEARCH_BRIEF_20260526.md",
                    "      - ION/05_context/current/browser_gpt_dom_profiles/latest.selector_profile.json",
                    "      - ION/04_packages/kernel/ion_browser_gpt_dom_calibration.py",
                    "    package_strategy: Browser DOM perception package with selector profiles, probe snapshots, extension runtime posture, Playwright/screen automation proof, permission posture, and JOC DOM twin evidence",
                    "    default_active_package_class: BROWSER_DOM_PERCEPTION_CONTEXT_PACKAGE",
                    "    primary_templates:",
                    "      - ION/07_templates/carriers/CODEX_CLI_EXECUTION_PACKET.md",
                    "      - ION/07_templates/bindings/STEWARD__STATUS_REPORT.md",
                    "      - ION/07_templates/context/AGENT_CONTEXT_BUILD_STEP.md",
                    "context_specialists:",
                ]
            ),
        ),
        encoding="utf-8",
    )
    _write(
        root,
        "ION/03_registry/agent_roster_registry.yaml",
        "\n".join(
            [
                "registry_id: current_phase.agent_roster_registry",
                "roster_records:",
                "  - entity_id: role.browser_dom_cartographer",
                "    display_name: Browser DOM Cartographer",
                "    live_status: ACTIVE_FIRST_PASS",
                "    registry_primary_domain: domain.browser_dom_perception",
                "    registry_secondary_domains:",
                "      - domain.codex_carrier_sync",
                "      - domain.continuity_context_resumability",
                "    default_mount_posture: CODEX_NATIVE_BROWSER_DOM_PERCEPTION_CHASSIS",
                "    template_bindings:",
                "      - ION/07_templates/carriers/CODEX_CLI_EXECUTION_PACKET.md",
                "      - ION/07_templates/bindings/STEWARD__STATUS_REPORT.md",
                "    source_refs:",
                "      - ION/03_registry/boots/BROWSER_DOM_CARTOGRAPHER.boot.md",
                "      - ION/03_registry/semantic_identities/BROWSER_DOM_CARTOGRAPHER.semantic.yaml",
                "      - ION/03_registry/domains/domain.browser_dom_perception.domain.yaml",
                "",
            ]
        ),
    )
    _write(
        root,
        "ION/03_registry/domains/domain.browser_dom_perception.domain.yaml",
        "\n".join(
            [
                "domain_id: domain.browser_dom_perception",
                "display_name: Browser DOM Perception",
                "status: ACTIVE_FIRST_PASS",
                "authority: A3_OPERATIONAL",
                "mission: Browser GPT DOM perception proof.",
                "primary_roles:",
                "  - BROWSER_DOM_CARTOGRAPHER",
                "owned_or_stewarded_surfaces:",
                "  - ION/04_packages/kernel/ion_browser_gpt_dom_calibration.py",
                "  - ION/05_context/current/browser_gpt_dom_profiles/",
                "  - browser_extension/ion_chatops_bridge/",
                "",
            ]
        ),
    )
    for rel in [
        "ION/03_registry/boots/BROWSER_DOM_CARTOGRAPHER.boot.md",
        "ION/03_registry/semantic_identities/BROWSER_DOM_CARTOGRAPHER.semantic.yaml",
        "ION/05_context/current/agent_context_systems/BROWSER_DOM_CARTOGRAPHER.context_system.md",
        "ION/05_context/current/browser_dom_perception_specialist/RESEARCH_BRIEF_20260526.md",
        "ION/05_context/current/browser_gpt_dom_profiles/latest.selector_profile.json",
        "ION/04_packages/kernel/ion_browser_gpt_dom_calibration.py",
        "ION/04_packages/kernel/ion_browser_gpt_screen_automation.py",
        "ION/08_ui/joc_cockpit_shell/BrowserGptDomTwinPanel.tsx",
        "browser_extension/ion_chatops_bridge/README.md",
        "browser_extension/ion_chatops_bridge/manifest.json",
        "ION/07_templates/bindings/STEWARD__STATUS_REPORT.md",
    ]:
        _write(root, rel, f"# {Path(rel).stem}\nAgent Context System\none-file-per-step\n")


def _seed_ionologist(root: Path) -> None:
    registry_path = root / "ION/03_registry/agent_context_system_registry.yaml"
    registry_text = registry_path.read_text(encoding="utf-8")
    registry_path.write_text(
        registry_text.replace(
            "context_specialists:",
            "\n".join(
                [
                    "  - role_id: role.ionologist",
                    "    display_name: IONOLOGIST",
                    "    context_system_card: ION/05_context/current/agent_context_systems/IONOLOGIST.context_system.md",
                    "    base_sources:",
                    "      - ION/03_registry/boots/IONOLOGIST.boot.md",
                    "      - ION/03_registry/semantic_identities/IONOLOGIST.semantic.yaml",
                    "      - ION/03_registry/domains/domain.ion_system_definition.domain.yaml",
                    "      - ION/03_registry/ion_context_authority_team_registry.yaml",
                    "      - ION/02_architecture/ION_CONTEXT_AUTHORITY_TEAM_PROTOCOL.md",
                    "    package_strategy: ION definition and operational-truth explanation package",
                    "    default_active_package_class: CONTEXT_AUTHORITY_PACKAGE",
                    "    primary_templates:",
                    "      - ION/07_templates/context/AGENT_CONTEXT_BUILD_STEP.md",
                    "      - ION/07_templates/context/AGENT_CONTEXT_PACKAGE.md",
                    "context_specialists:",
                ]
            ),
        ),
        encoding="utf-8",
    )
    _write(
        root,
        "ION/03_registry/agent_roster_registry.yaml",
        "\n".join(
            [
                "registry_id: current_phase.agent_roster_registry",
                "roster_records:",
                "  - entity_id: role.ionologist",
                "    display_name: Ionologist",
                "    live_status: ACTIVE_CURRENT_PHASE",
                "    registry_primary_domain: domain.ion_system_definition",
                "    registry_secondary_domains:",
                "      - domain.continuity_context_resumability",
                "    default_mount_posture: CODEX_NATIVE_CONTEXT_AUTHORITY_SPECIALIST_CHASSIS",
                "    template_bindings:",
                "      - ION/07_templates/context/AGENT_CONTEXT_BUILD_STEP.md",
                "      - ION/07_templates/context/AGENT_CONTEXT_PACKAGE.md",
                "    source_refs:",
                "      - ION/03_registry/boots/IONOLOGIST.boot.md",
                "      - ION/03_registry/semantic_identities/IONOLOGIST.semantic.yaml",
                "      - ION/03_registry/domains/domain.ion_system_definition.domain.yaml",
                "",
            ]
        ),
    )
    _write(
        root,
        "ION/03_registry/domains/domain.ion_system_definition.domain.yaml",
        "\n".join(
            [
                "domain_id: domain.ion_system_definition",
                "display_name: ION System Definition and Operational Truth",
                "status: ACTIVE_FIRST_PASS",
                "authority: A3_OPERATIONAL",
                "mission: Explain ION with proof boundaries.",
                "primary_roles:",
                "  - IONOLOGIST",
                "owned_or_stewarded_surfaces:",
                "  - ION/docs/encyclopedia/",
                "  - ION/02_architecture/ION_CONTEXT_AUTHORITY_TEAM_PROTOCOL.md",
                "  - ION/05_context/current/agent_context_systems/IONOLOGIST.context_system.md",
                "",
            ]
        ),
    )
    for rel in [
        "ION/03_registry/boots/IONOLOGIST.boot.md",
        "ION/03_registry/semantic_identities/IONOLOGIST.semantic.yaml",
        "ION/05_context/current/agent_context_systems/IONOLOGIST.context_system.md",
        "ION/03_registry/ion_context_authority_team_registry.yaml",
        "ION/02_architecture/ION_CONTEXT_AUTHORITY_TEAM_PROTOCOL.md",
        "ION/07_templates/context/AGENT_CONTEXT_PACKAGE.md",
    ]:
        _write(root, rel, f"# {Path(rel).stem}\nAgent Context System\none-file-per-step\n")


def test_agent_control_plane_unifies_agents_domains_and_runs(tmp_path: Path):
    _seed_root(tmp_path)

    model = build_agent_control_plane_projection(tmp_path)

    assert model["schema_id"] == "ion.agent_control_plane.v1"
    assert model["source_model"]["agent_context_systems"] == "primary_role_truth"
    assert model["source_model"]["domain_weave"] == "candidate_domain_truth"
    assert model["source_model"]["mini_capsule"] == "continuity_witness_only"
    assert model["summary"]["agent_count"] >= 2
    assert model["summary"]["domain_count"] == 1
    assert model["summary"]["codex_mount_count"] >= 2
    assert model["summary"]["domain_weaver_edge_count"] >= 1
    assert model["summary"]["domain_weaver_gap_count"] >= 1
    assert model["roster"]["schema_id"] == "ion.agent_roster.projection.v1"
    assert model["roster"]["agent_count"] >= 2
    assert len(model["roster"]["spawn_templates"]) >= 4
    assert model["roster"]["communication_directory"]["schema_id"] == "ion.agent_communication_directory.v1"
    assert model["roster"]["communication_directory"]["available_agent_count"] >= 2
    assert model["roster"]["communication_directory"]["automation_comms_policy"]["limits"]["default_prompt_limit"] == 12
    contact_contract = model["roster"]["communication_directory"]["contact_contract"]
    assert contact_contract["schema_id"] == "ion.agent_contact_contract.v1"
    assert contact_contract["contact_edge_count"] >= 2
    assert contact_contract["template_contracts"]["agent_workpack_decision"]["directive_schema_id"] == "ion.agent_comms.directive.v1"
    assert model["summary"]["agent_contact_contract_edge_count"] == contact_contract["contact_edge_count"]
    room_contract = model["roster"]["communication_directory"]["room_contract"]
    assert room_contract["schema_id"] == "ion.agent_room_contract.v1"
    assert room_contract["recommended_owner_role"] == "role.comms_cartographer"
    assert room_contract["rooms_by_id"]["room.main.team"]["room_kind"] == "main"
    assert room_contract["context_loading"]["first_read"] == "room_capsule"
    assert model["summary"]["agent_room_contract_room_count"] == room_contract["room_count"]
    assert [step["step_id"] for step in model["chain"]["steps"]][:3] == [
        "persona_ingress",
        "relay_packetize",
        "steward_route",
    ]
    assert any(agent["role_id"] == "role.mason" for agent in model["agents"])
    mason = next(agent for agent in model["agents"] if agent["role_id"] == "role.mason")
    assert mason["native_codex_mount"]["agent_role_id"] == "role.mason"
    assert mason["native_codex_mount"]["domain_id"] == "ion_vnext_context"
    assert "codex" in mason["native_codex_mount"]["native_codex"]["command_preview"]
    assert mason["native_codex_mount"]["native_codex"]["prompt_visibility_probe"].startswith("codex -C ")
    assert mason["agent_page_evidence"]["schema_id"] == "ion.agent_page_evidence.v1"
    assert mason["agent_page_evidence"]["identity"]["agent_kind"] == "ion_context_system_agent"
    assert mason["agent_page_evidence"]["identity"]["is_ion_context_system"] is True
    assert mason["agent_page_evidence"]["context_system"]["card"]["exists"] is True
    roster_mason = next(agent for agent in model["roster"]["agents"] if agent["role_id"] == "role.mason")
    assert "ion_vnext_context" in roster_mason["domain_ids"]
    assert roster_mason["spawn_supported"] is True
    assert roster_mason["available_for_comms"] is True
    assert roster_mason["communication_profile"]["can_initiate_comms"] is True
    assert model["domains"][0]["domain_id"] == "ion_vnext_context"
    assert model["roster"]["domains"][0]["domain_id"] == "ion_vnext_context"
    assert model["codex_mounts"]["mount_count"] >= 2
    assert model["domain_weaver"]["schema_id"] == "ion.domain_weaver.projection.v1"
    assert model["domain_weaver"]["projection_path"] == DOMAIN_WEAVER_PROJECTION_PATH.as_posix()
    assert model["domain_weaver"]["summary"]["domain_count"] == model["summary"]["domain_count"]
    assert model["domain_weaver"]["summary"]["agent_count"] == model["summary"]["agent_count"]
    assert model["domain_weaver"]["ui_development"]["schema_id"] == "ion.domain_weaver.ui_development_projection.v0_1"
    assert model["domain_weaver"]["ui_development"]["page_route"] == "/cockpit#weave"
    assert any(edge["edge_type"].startswith("agent_") for edge in model["domain_weaver"]["edges"])
    assert model["communications"]["schema_id"] == "ion.agent_control_plane.communications.v1"
    assert model["communications"]["contact_contract"]["schema_id"] == "ion.agent_contact_contract.v1"
    assert model["communications"]["room_contract"]["schema_id"] == "ion.agent_room_contract.v1"
    assert model["communications"]["room_contract"]["room_count"] == room_contract["room_count"]
    assert model["communications"]["summary"]["contact_contract_edge_count"] == contact_contract["contact_edge_count"]
    assert model["communications"]["summary"]["contact_contract_template_count"] >= 4
    assert model["communications"]["summary"]["room_contract_room_count"] == room_contract["room_count"]
    assert model["communications"]["summary"]["pending_relay_count"] == 0
    assert model["communications"]["team_comms"]["schema_id"] == "ion.agent_comms.projection.v1"
    assert model["communications"]["team_comms"]["rooms"]["schema_id"] == "ion.agent_comms.rooms.projection.v1"
    assert model["communications"]["team_comms"]["source_model"]["agent_comms"] == "durable_packet_bus"
    assert model["communications"]["team_comms_chain_audit"]["schema_id"] == "ion.agent_comms.chain_audit.v1"
    assert model["communications"]["team_comms_chain_audit"]["audit_state"] == "FAIL"
    assert "run_not_found" in model["communications"]["team_comms_chain_audit"]["findings"]
    assert model["communications"]["team_comms_chain_proof"]["schema_id"] == "ion.agent_comms.chain_proof.v1"
    assert model["communications"]["team_comms_chain_proof"]["proof_state"] == "blocked_at_run_observed"
    assert model["communications"]["team_comms_chain_proof"]["first_missing_link"] == "run_observed"
    assert model["communications"]["team_comms_chain_gate"]["schema_id"] == "ion.agent_comms.audit_gate.v1"
    assert model["communications"]["team_comms_chain_gate"]["state"] == "run_id_required"
    assert model["communications"]["summary"]["team_thread_count"] == 0
    assert model["communications"]["summary"]["team_comms_chain_audit_state"] == "FAIL"
    assert model["communications"]["summary"]["team_comms_chain_audit_ok"] is False
    assert model["communications"]["summary"]["team_comms_chain_proof_state"] == "blocked_at_run_observed"
    assert model["communications"]["summary"]["team_comms_chain_proof_ok"] is False
    assert model["communications"]["summary"]["team_comms_chain_first_missing_link"] == "run_observed"
    assert model["communications"]["summary"]["team_comms_chain_clean_state"] == "run_id_required"
    assert model["communications"]["summary"]["team_comms_chain_clean"] is False
    assert model["dispatcher"]["schema_id"] == "ion.steward_dispatcher.v1"
    assert model["dispatcher"]["controls"]["route_endpoint"] == "/cockpit/agents/dispatcher/route"
    assert model["dispatcher"]["summary"]["agent_count"] == model["summary"]["agent_count"]
    assert model["dispatcher"]["summary"]["domain_count"] == model["summary"]["domain_count"]
    assert model["summary"]["dispatcher_actionable_run_count"] == model["dispatcher"]["summary"]["actionable_run_count"]
    assert model["dispatcher"]["production_authority"] is False
    assert model["dispatcher"]["live_execution_authority"] is False
    assert model["dispatcher"]["accepted_state_authority"] is False
    assert model["production_authority"] is False
    assert model["live_execution_authority"] is False
    assert model["accepted_state_authority"] is False


def test_agent_control_plane_marks_legacy_agent_refs_as_nonblocking_witnesses(tmp_path: Path):
    _seed_root(tmp_path)

    model = build_agent_control_plane_projection(tmp_path)
    mason = next(agent for agent in model["agents"] if agent["role_id"] == "role.mason")

    assert "ION/agents/mason/MINI.md" in mason["missing_legacy_context_paths"]
    assert mason["legacy_context_missing_is_blocking"] is False
    assert model["diagnostics"]["legacy_refs_are_witness_only"] is True


def test_codex_agent_mount_materializes_native_codex_surfaces(tmp_path: Path):
    _seed_root(tmp_path)
    model = build_agent_control_plane_projection(tmp_path)
    mason = next(agent for agent in model["agents"] if agent["role_id"] == "role.mason")
    domain = model["domains"][0]

    mount = materialize_codex_agent_mount(tmp_path, mason, domain, communication_directory=model["roster"]["communication_directory"])

    assert mount["materialization_result"] == "CODEX_AGENT_MOUNT_MATERIALIZED"
    assert mount["materialized"] is True
    assert mount["native_codex"]["interactive_command_preview"][:2] == ["codex", "-C"]
    assert mount["native_codex"]["prompt_visibility_probe"].startswith("codex -C ")
    assert (tmp_path / mount["manifest_path"]).is_file()
    assert (tmp_path / mount["agents_md_path"]).read_text(encoding="utf-8").startswith("# ION Codex Agent Mount")
    config_text = (tmp_path / mount["config_path"]).read_text(encoding="utf-8")
    assert "developer_instructions" in config_text
    assert "ion_session_start_context.py" in config_text
    assert (tmp_path / mount["active_context_package_path"]).is_file()
    assert (tmp_path / mount["active_context_package_md_path"]).is_file()
    assert (tmp_path / mount["portable_context_manifest_path"]).is_file()
    assert (tmp_path / mount["portable_communications_path"]).is_file()
    assert (tmp_path / mount["portable_address_book_path"]).is_file()
    assert (tmp_path / mount["portable_active_context_package_md_path"]).is_file()
    agents_text = (tmp_path / mount["agents_md_path"]).read_text(encoding="utf-8")
    assert ".ion/ION_CONTEXT_CAPSULE.yaml" in agents_text
    assert ".ion/COMMUNICATIONS.json" in agents_text
    assert ".ion/ADDRESS_BOOK.json" in agents_text
    assert "Agent Communication" in agents_text
    assert "ion-agent-comms" in agents_text
    assert "@agent alias" in agents_text
    assert DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix() in agents_text
    manifest_text = (tmp_path / mount["portable_context_manifest_path"]).read_text(encoding="utf-8")
    assert 'folder_role: "codex_native_agent_domain_mount"' in manifest_text
    assert "available_agent_count" in manifest_text
    assert "address_book" in manifest_text
    assert 'mention_syntax: "@agent_alias"' in manifest_text
    assert "run_graph_observable: true" in manifest_text
    assert DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix() in manifest_text
    assert "production_authority: false" in manifest_text
    comms = json.loads((tmp_path / mount["portable_communications_path"]).read_text(encoding="utf-8"))
    assert comms["schema_id"] == "ion.portable_agent_communications.v0_1"
    assert comms["address_book_path"] == f".ion/{PORTABLE_ADDRESS_BOOK}"
    assert comms["contact_contract"]["schema_id"] == "ion.agent_contact_contract.v1"
    assert comms["contact_contract"]["routing_source_of_truth"] == "COMMUNICATION_DIRECTORY.json#contact_contract"
    assert comms["contact_contract"]["contact_edge_count"] >= 2
    assert comms["room_contract"]["schema_id"] == "ion.agent_room_contract.v1"
    assert comms["room_contract"]["routing_source_of_truth"] == "COMMUNICATION_DIRECTORY.json#room_contract"
    assert comms["room_contract"]["context_loading"]["first_read"] == "room_capsule"
    assert comms["room_routing_rules"][0]["room_kind"] == "main"
    assert comms["template_contracts"]["agent_workpack_decision"]["directive_schema_id"] == "ion.agent_comms.directive.v1"
    assert comms["domain_weaver"]["projection_path"] == DOMAIN_WEAVER_PROJECTION_PATH.as_posix()
    assert comms["domain_weaver"]["promotion_review_path"] == DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()
    assert comms["start_comms"]["domain_weaver_projection_path"] == DOMAIN_WEAVER_PROJECTION_PATH.as_posix()
    assert comms["start_comms"]["domain_weaver_promotion_review_path"] == DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()
    assert comms["start_comms"]["default_to_role"] == "role.steward"
    assert comms["start_comms"]["automation_pickup_action"] == "agent_comms.process_directives"
    assert comms["start_comms"]["directive_schema_id"] == "ion.agent_comms.directive.v1"
    assert comms["start_comms"]["task_run_start_endpoint"] == "/cockpit/agents/comms/run/start"
    assert comms["start_comms"]["task_run_pickup_endpoint"] == "/cockpit/agents/comms/run/pickup"
    assert comms["start_comms"]["task_run_audit_endpoint"] == "/cockpit/agents/comms/run/audit"
    assert "start_workpack" in comms["start_comms"]["supported_dispatch_modes"]
    assert comms["start_comms"]["agent_initiated_rule"].startswith("The agent decides when to communicate")
    assert comms["start_comms"]["mention_syntax"] == "@agent_alias"
    assert comms["start_comms"]["agent_to_agent_rule"].startswith("Use @aliases")
    assert "message -> directive -> workpack" in comms["start_comms"]["run_graph_policy"]
    assert comms["agent_decision_boundary"].startswith("This mounted agent decides")
    assert comms["task_run_policy"]["observability"]["run_graph_schema_id"] == "ion.agent_comms.run_graph.v1"
    address_book = json.loads((tmp_path / mount["portable_address_book_path"]).read_text(encoding="utf-8"))
    assert address_book["schema_id"] == "ion.portable_agent_address_book.v0_1"
    assert address_book["agent_role_id"] == "role.mason"
    assert address_book["contact_contract_schema_id"] == "ion.agent_contact_contract.v1"
    assert address_book["contact_contract_ref"] == "COMMUNICATION_DIRECTORY.json#contact_contract"
    assert address_book["room_contract_schema_id"] == "ion.agent_room_contract.v1"
    assert address_book["room_contract_ref"] == "COMMUNICATION_DIRECTORY.json#room_contract"
    assert address_book["routing_rules"][0]["contact_group"] == "orchestration"
    assert address_book["situation_map"]["proof_chain"] == ["message", "directive", "workpack", "task_return", "synced_reply"]
    assert address_book["situation_map"]["contact_contract_schema_id"] == "ion.agent_contact_contract.v1"
    assert address_book["situation_map"]["room_contract_schema_id"] == "ion.agent_room_contract.v1"
    assert address_book["situation_map"]["room_context_loading"]["first_read"] == "room_capsule"
    assert "implementation_or_runtime" in address_book["situation_map"]["relationship_taxonomy"]
    assert address_book["authority"]["candidate_mount_only"] is True


def test_codex_carrier_steward_projects_as_ion_agent_domain_and_mount(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)

    model = build_agent_control_plane_projection(tmp_path)

    agent = next(agent for agent in model["agents"] if agent["role_id"] == "role.codex_carrier_steward")
    domain = next(domain for domain in model["domains"] if domain["domain_id"] == "domain.codex_carrier_sync")
    assert agent["display_name"] == "CODEX_CARRIER_STEWARD"
    assert agent["write_posture"] == "gated"
    assert "codex_cli_probe" in agent["default_proof_obligations"]
    assert agent["registry_primary_domain"] == "domain.codex_carrier_sync"
    assert ".codex/" in domain["paths"]
    assert agent["native_codex_mount"]["domain_id"] == "domain.codex_carrier_sync"
    assert "ION/05_context/current/agent_context_systems/CODEX_CARRIER_STEWARD.context_system.md" in agent["native_codex_mount"]["context_refs"]

    agent = {**agent, "lane_ids": ["maintenance_lane"]}
    mount = materialize_codex_agent_mount(tmp_path, agent, domain)

    assert mount["materialization_result"] == "CODEX_AGENT_MOUNT_MATERIALIZED"
    assert mount["agent_role_id"] == "role.codex_carrier_steward"
    assert mount["domain_id"] == "domain.codex_carrier_sync"
    assert (tmp_path / mount["manifest_path"]).is_file()
    assert (tmp_path / mount["active_context_package_path"]).is_file()
    assert (tmp_path / mount["portable_context_manifest_path"]).is_file()
    assert (tmp_path / mount["portable_agent_path"]).is_file()
    assert (tmp_path / mount["portable_domain_path"]).is_file()
    assert (tmp_path / mount["portable_relationships_path"]).is_file()
    assert (tmp_path / mount["portable_communications_path"]).is_file()
    assert (tmp_path / mount["portable_address_book_path"]).is_file()
    portable_manifest = (tmp_path / mount["portable_context_manifest_path"]).read_text(encoding="utf-8")
    active_package = json.loads((tmp_path / mount["active_context_package_path"]).read_text(encoding="utf-8"))
    portable_active_package = json.loads(
        (tmp_path / mount["portable_active_context_package_path"]).read_text(encoding="utf-8")
    )
    assert "role.codex_carrier_steward" in portable_manifest
    assert "domain.codex_carrier_sync" in portable_manifest
    assert active_package["lane_ids"] == ["maintenance_lane"]
    assert portable_active_package["lane_ids"] == ["maintenance_lane"]
    assert active_package["lane_metadata_policy"]["missing_lane_metadata_blocks_lane_bound_worker_start"] is True
    assert DOMAIN_WEAVER_PROJECTION_PATH.as_posix() in portable_manifest
    assert DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix() in portable_manifest

    refreshed = build_agent_control_plane_projection(tmp_path)
    refreshed_agent = next(agent for agent in refreshed["agents"] if agent["role_id"] == "role.codex_carrier_steward")
    assert refreshed_agent["native_codex_mount"]["portable_context_manifest_exists"] is True
    evidence = refreshed_agent["agent_page_evidence"]
    assert evidence["identity"]["agent_kind"] == "ion_capsule_codex_agent"
    assert evidence["identity"]["is_capsule_agent"] is True
    assert evidence["codex_mount"]["materialized"] is True
    assert evidence["address_book"]["exists"] is True
    assert evidence["address_book"]["schema_id"] == "ion.portable_agent_address_book.v0_1"
    assert any(item["label"] == "ion_context_capsule" and item["exists"] for item in evidence["capsule"]["files"])
    assert any(item["label"] == "address_book" and item["exists"] for item in evidence["capsule"]["files"])


def test_browser_dom_cartographer_projects_as_ion_agent_domain_and_mount(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_browser_dom_cartographer(tmp_path)

    model = build_agent_control_plane_projection(tmp_path)

    agent = next(agent for agent in model["agents"] if agent["role_id"] == "role.browser_dom_cartographer")
    domain = next(domain for domain in model["domains"] if domain["domain_id"] == "domain.browser_dom_perception")
    assert agent["display_name"] == "BROWSER_DOM_CARTOGRAPHER"
    assert agent["write_posture"] == "gated"
    assert "selector_profile_receipt" in agent["default_proof_obligations"]
    assert "extension_runtime_probe" in agent["default_proof_obligations"]
    assert agent["registry_primary_domain"] == "domain.browser_dom_perception"
    assert "ION/04_packages/kernel/ion_browser_gpt_dom_calibration.py" in domain["paths"]
    assert agent["native_codex_mount"]["domain_id"] == "domain.browser_dom_perception"
    assert "ION/05_context/current/agent_context_systems/BROWSER_DOM_CARTOGRAPHER.context_system.md" in agent["native_codex_mount"]["context_refs"]
    roster_agent = next(agent for agent in model["roster"]["agents"] if agent["role_id"] == "role.browser_dom_cartographer")
    assert roster_agent["registry_primary_domain"] == "domain.browser_dom_perception"
    assert roster_agent["spawn_supported"] is True
    assert roster_agent["available_for_comms"] is True

    mount = materialize_codex_agent_mount(tmp_path, agent, domain)

    assert mount["materialization_result"] == "CODEX_AGENT_MOUNT_MATERIALIZED"
    assert mount["agent_role_id"] == "role.browser_dom_cartographer"
    assert mount["domain_id"] == "domain.browser_dom_perception"
    assert (tmp_path / mount["manifest_path"]).is_file()
    assert (tmp_path / mount["agents_md_path"]).is_file()
    assert (tmp_path / mount["config_path"]).is_file()
    assert (tmp_path / mount["active_context_package_path"]).is_file()
    assert (tmp_path / mount["portable_context_manifest_path"]).is_file()
    assert (tmp_path / mount["portable_agent_path"]).is_file()
    assert (tmp_path / mount["portable_domain_path"]).is_file()
    assert (tmp_path / mount["portable_communications_path"]).is_file()
    portable_manifest = (tmp_path / mount["portable_context_manifest_path"]).read_text(encoding="utf-8")
    assert "role.browser_dom_cartographer" in portable_manifest
    assert "domain.browser_dom_perception" in portable_manifest


def test_ionologist_projects_as_ion_specialist_domain_and_mount(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_ionologist(tmp_path)

    model = build_agent_control_plane_projection(tmp_path)

    agent = next(agent for agent in model["agents"] if agent["role_id"] == "role.ionologist")
    domain = next(domain for domain in model["domains"] if domain["domain_id"] == "domain.ion_system_definition")
    assert agent["display_name"] == "IONOLOGIST"
    assert agent["write_posture"] == "none"
    assert "claim_classification" in agent["default_proof_obligations"]
    assert agent["registry_primary_domain"] == "domain.ion_system_definition"
    assert "ION/docs/encyclopedia/" in domain["paths"]
    assert agent["native_codex_mount"]["domain_id"] == "domain.ion_system_definition"

    mount = materialize_codex_agent_mount(tmp_path, agent, domain)

    assert mount["materialization_result"] == "CODEX_AGENT_MOUNT_MATERIALIZED"
    assert mount["agent_role_id"] == "role.ionologist"
    assert mount["domain_id"] == "domain.ion_system_definition"
    assert (tmp_path / mount["manifest_path"]).is_file()
    assert (tmp_path / mount["active_context_package_md_path"]).read_text(encoding="utf-8").startswith("# Active Context Package")
    assert (tmp_path / mount["portable_capsule_path"]).read_text(encoding="utf-8").startswith("# ION Agent Domain Capsule")
    assert DOMAIN_WEAVER_PROJECTION_PATH.as_posix() in (tmp_path / mount["portable_capsule_path"]).read_text(encoding="utf-8")
    assert DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix() in (tmp_path / mount["portable_capsule_path"]).read_text(encoding="utf-8")


def test_domain_weaver_materializes_projection_receipt(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)

    model = build_agent_control_plane_projection(tmp_path)
    result = materialize_domain_weaver_projection(tmp_path, model["domain_weaver"])

    assert result["schema_id"] == "ion.domain_weaver.materialization.v1"
    assert result["ok"] is True
    assert result["projection_path"] == DOMAIN_WEAVER_PROJECTION_PATH.as_posix()
    assert len(result["projection_sha256"]) == 64
    projection_path = tmp_path / result["projection_path"]
    receipt_path = tmp_path / result["receipt_path"]
    assert projection_path.is_file()
    assert receipt_path.is_file()
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    assert projection["schema_id"] == "ion.domain_weaver.projection.v1"
    assert projection["summary"]["agent_count"] == model["summary"]["agent_count"]
    assert projection["capsule_exports"]["projection_path"] == DOMAIN_WEAVER_PROJECTION_PATH.as_posix()
    assert projection["promotion_review"]["schema_id"] == "ion.domain_weaver.promotion_review.v1"
    assert projection["promotion_gate"]["schema_id"] == "ion.domain_weaver.promotion_gate.v1"
    assert projection["queue_governance"]["schema_id"] == "ion.domain_weaver.queue_governance.v0_1"
    assert projection["live_carrier_binding"]["schema_id"] == "ion.domain_weaver.live_carrier_binding_plan.v0_1_candidate"

    refreshed = materialize_domain_weaver_projection(tmp_path)
    refreshed_projection = json.loads(projection_path.read_text(encoding="utf-8"))
    assert refreshed["ok"] is True
    assert refreshed_projection["summary"]["agent_count"] == model["summary"]["agent_count"]
    assert refreshed_projection["summary"]["domain_count"] == model["summary"]["domain_count"]
    assert refreshed_projection["queue_governance"]["schema_id"] == "ion.domain_weaver.queue_governance.v0_1"


def test_domain_weaver_projects_original_plan_compliance_blockers(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    projection = build_domain_weaver_projection(tmp_path)
    compliance = projection["original_plan_compliance"]
    founding = projection["founding_domain_assembly"]
    blockers = {row["code"] for row in compliance["blockers"]}

    assert projection["summary"]["current_capability_class"] == "approval_governed_live_queue_plan_ready"
    assert projection["summary"]["full_domain_weaver_ready"] is False
    assert projection["summary"]["self_evolution_ready"] is False
    assert projection["summary"]["founding_assembly_contract_ready"] is True
    assert projection["summary"]["founding_domain_count"] == 20
    assert projection["summary"]["self_evolution_lattice_contract_ready"] is True
    assert projection["summary"]["self_evolution_lattice_executable"] is False
    assert founding["schema_id"] == "ion.domain_weaver.founding_domain_assembly.v0_1_candidate"
    assert founding["status"] == "founding_assembly_candidate_contract_ready"
    assert founding["summary"]["founding_domain_count"] == 20
    assert founding["summary"]["active_execution_count"] == 0
    assert founding["next_packet"]["packet_id"] == (
        "PCKT-DOMAIN-WEAVER-FOUNDING-ASSEMBLY-NEMESIS-AUDIT-20260601"
    )
    assert compliance["status"] == "full_domain_weaver_blocked"
    assert compliance["full_domain_weaver_ready"] is False
    assert compliance["self_evolution_ready"] is False
    assert compliance["summary"]["founding_assembly_contract_ready"] is True
    assert compliance["summary"]["self_evolution_lattice_contract_ready"] is True
    assert "NO_EXECUTABLE_DOMAIN_FISSION_ENGINE" in blockers
    assert "NO_EXECUTABLE_AGENT_ACTIVATION_PLANE" in blockers
    assert "NO_EXECUTABLE_RECURSIVE_FANOUT_FANIN_SETTLEMENT" in blockers
    assert "LIVE_EXECUTION_QUEUE_NOT_MATERIALIZED" in blockers
    assert "FOUNDING_ASSEMBLY_CONTRACT_ONLY_NOT_EXECUTED" in blockers
    assert "LIVE_RETURN_MONITOR_MISSING" not in blockers
    assert "LIVE_FANOUT_RETURNS_INCOMPLETE" not in blockers
    assert compliance["summary"]["activation_records_ready"] is True
    assert compliance["summary"]["fission_dryrun_ready"] is True
    assert compliance["summary"]["fanout_fanin_settlement_dryrun_ready"] is True
    assert compliance["summary"]["approval_governor_ready"] is True
    assert compliance["summary"]["semi_autonomous_approval_ready"] is True
    assert compliance["summary"]["live_execution_carrier_binding_ready"] is False
    assert compliance["summary"]["live_carrier_queue_binding_plan_ready"] is True
    assert compliance["summary"]["live_carrier_work_request_template_count"] > 0
    assert compliance["summary"]["live_carrier_queued_request_count"] == 0
    assert compliance["summary"]["live_return_monitor_ready"] is True
    assert compliance["summary"]["live_return_expected_count"] > 0
    assert compliance["summary"]["live_return_accepted_count"] == 0
    assert compliance["summary"]["live_return_complete"] is False
    assert compliance["summary"]["active_ui_specialist_agent_count"] == 0


def test_domain_weaver_materializes_founding_domain_assembly(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    result = materialize_domain_weaver_founding_domain_assembly(tmp_path)

    assert result["schema_id"] == "ion.domain_weaver.founding_domain_assembly_materialization.v0_1"
    assert result["ok"] is True
    assert result["assembly_path"] == DOMAIN_WEAVER_FOUNDING_ASSEMBLY_PATH.as_posix()
    assert result["assembly_markdown_path"] == DOMAIN_WEAVER_FOUNDING_ASSEMBLY_MD_PATH.as_posix()
    assert result["summary"]["founding_domain_count"] == 20
    assert result["summary"]["activation_wave_count"] == 4
    assert result["summary"]["self_evolution_lattice_contract_ready"] is True
    assert result["summary"]["self_evolution_lattice_executable"] is False
    assert result["next_packet"]["packet_id"] == "PCKT-DOMAIN-WEAVER-FOUNDING-ASSEMBLY-NEMESIS-AUDIT-20260601"
    assert result["production_authority"] is False
    assert result["live_execution_authority"] is False
    assert result["accepted_state_authority"] is False

    assembly = json.loads((tmp_path / DOMAIN_WEAVER_FOUNDING_ASSEMBLY_PATH).read_text(encoding="utf-8"))
    domain_ids = {row["domain_id"] for row in assembly["domain_rows"]}

    assert "self_evolution_domain" in domain_ids
    assert "ui_canon_historian_domain" in domain_ids
    assert "interaction_map_systems_domain" in domain_ids
    assert "carrier_scheduler_engineering_domain" in domain_ids
    assert all(row["candidate_only"] is True for row in assembly["domain_rows"])
    assert all(row["worker_return_required_before_credit"] is True for row in assembly["domain_rows"])


def test_domain_weaver_operator_action_materializes_founding_assembly(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_founding_domain_assembly",
            "packet_id": "PCKT-DOMAIN-WEAVER-FOUNDING-DOMAIN-ASSEMBLY-AND-SELF-EVOLUTION-LATTICE-20260601",
            "confirmation": CONFIRMATION,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["founding_domain_count"] == 20
    assert result["summary"]["self_evolution_lattice_contract_ready"] is True
    assert result["summary"]["self_evolution_lattice_executable"] is False
    assert result["summary"]["worker_started_count"] == 0
    assert result["summary"]["next_packet_id"] == "PCKT-DOMAIN-WEAVER-FOUNDING-ASSEMBLY-NEMESIS-AUDIT-20260601"
    assert result["operator_action_history_path"] == DOMAIN_WEAVER_OPERATOR_ACTION_HISTORY_PATH.as_posix()
    assert (tmp_path / result["summary"]["assembly_path"]).is_file()
    assert (tmp_path / result["summary"]["assembly_markdown_path"]).is_file()


def test_domain_weaver_operator_action_queues_founding_assembly_nemesis_audit(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_founding_assembly_nemesis_audit",
            "packet_id": "PCKT-DOMAIN-WEAVER-FOUNDING-ASSEMBLY-NEMESIS-AUDIT-20260601",
            "confirmation": CONFIRMATION,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["founding_assembly_next_packet_ready"] is True
    assert result["summary"]["founding_domain_count"] == 20
    assert result["summary"]["activation_wave_count"] == 4
    assert result["summary"]["self_evolution_lattice_contract_ready"] is True
    assert result["summary"]["self_evolution_lattice_executable"] is False
    assert result["summary"]["worker_started_count"] == 0
    assert result["summary"]["worker_start_status"] == "not_started_queue_only_default"

    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_FOUNDING_ASSEMBLY_NEMESIS_AUDIT_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    assert ledger["schema_id"] == "ion.domain_weaver.founding_assembly_nemesis_audit_queue_ledger.v0_1_candidate"
    assert ledger["queue_action"] == "queue_founding_assembly_nemesis_audit"
    assert ledger["summary"]["queued_request_count"] == 1
    request_path = tmp_path / ledger["queued_requests"][0]["packet_path"]
    request = json.loads(request_path.read_text(encoding="utf-8"))

    assert request["request_kind"] == "domain_weaver_founding_assembly_nemesis_audit"
    assert request["agent_role"] == "role.nemesis"
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert request["domain_weaver_founding_assembly_audit"]["founding_domain_count"] == 20
    assert request["domain_weaver_founding_assembly_audit"]["active_execution_count"] == 0
    assert request["domain_weaver_founding_assembly_audit"]["single_worker_substitution_must_remain_blocked"] is True
    assert "ui_development_implementation" in request["domain_weaver_founding_assembly_audit"]["blocked_work_classes"]
    assert DOMAIN_WEAVER_FOUNDING_ASSEMBLY_PATH.as_posix() in request["required_context_reads"]
    assert "Needs_Routed/ION_DOMAIN_WEAVE_FULL_ION_MASTER_PLAN_v0_1.md" in request["required_context_reads"]
    assert request["requested_authority"]["production_authority"] is False
    assert request["requested_authority"]["live_execution_authority"] is False


def test_domain_weaver_operator_action_queues_foundation_wave0_after_accepted_audit(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    materialize_domain_weaver_founding_domain_assembly(tmp_path)

    audit_request_path = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_founding_assembly_nemesis_audit_20260601_attempt_001.json"
    )
    audit_return_path = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-01T040102Z0000_task_return.json"
    audit_receipt_path = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        "2026-06-01T040102Z0000_task_return_machine_receipt.json"
    )
    audit_run_path = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_2026-06-01T035216Z0000_codex_req_domain_weaver_founding_assembly_nemesis_audit_20260601_attempt_001/"
        "run.json"
    )
    audit_body_path = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_2026-06-01T035216Z0000_codex_req_domain_weaver_founding_assembly_nemesis_audit_20260601_attempt_001/"
        "task_return_body.md"
    )
    _write(
        tmp_path,
        audit_request_path,
        json.dumps(
            {
                "request_id": "codex_req_domain_weaver_founding_assembly_nemesis_audit_20260601_attempt_001",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "latest_return_packet_path": audit_return_path,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        audit_return_path,
        json.dumps({"machine_receipt_path": audit_receipt_path}, indent=2) + "\n",
    )
    _write(tmp_path, audit_receipt_path, "{}\n")
    _write(
        tmp_path,
        audit_run_path,
        json.dumps(
            {
                "request_id": "codex_req_domain_weaver_founding_assembly_nemesis_audit_20260601_attempt_001",
                "task_return_body_path": audit_body_path,
            },
            indent=2,
        )
        + "\n",
    )
    _write(tmp_path, audit_body_path, "### RECOMMENDED NEXT PACKET\nPCKT-DOMAIN-WEAVER-FOUNDATION-WAVE0-INDEPENDENT-RETURNS-20260601\n")

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_foundation_wave0_independent_returns",
            "packet_id": "PCKT-DOMAIN-WEAVER-FOUNDATION-WAVE0-INDEPENDENT-RETURNS-20260601",
            "confirmation": CONFIRMATION,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["founding_audit_accepted"] is True
    assert result["summary"]["wave0_domain_count"] == 6
    assert result["summary"]["queued_request_count"] == 6
    assert result["summary"]["worker_started_count"] == 0

    ledger = json.loads((tmp_path / DOMAIN_WEAVER_FOUNDATION_WAVE0_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    assert ledger["schema_id"] == "ion.domain_weaver.foundation_wave0_independent_returns_queue_ledger.v0_1_candidate"
    assert ledger["queue_action"] == "queue_foundation_wave0_independent_returns"
    assert ledger["summary"]["queued_request_count"] == 6
    assert ledger["summary"]["worker_start_status"] == "not_started_queue_only_default"
    request_paths = [row["packet_path"] for row in ledger["queued_requests"]]
    requests = [json.loads((tmp_path / path).read_text(encoding="utf-8")) for path in request_paths]

    assert {request["domain_weaver_foundation_wave0"]["domain_id"] for request in requests} == {
        "original_plan_steward_domain",
        "context_cartography_domain",
        "template_protocol_engineering_domain",
        "queue_hygiene_governance_domain",
        "nemesis_architecture_audit_domain",
        "roadmap_scribe_domain",
    }
    assert all(request["request_kind"] == "domain_weaver_foundation_wave0_independent_return" for request in requests)
    assert all(request["requested_model"] == "gpt-5.5" for request in requests)
    assert all(request["requested_reasoning_effort"] == "xhigh" for request in requests)
    assert all(request["domain_weaver_foundation_wave0"]["proof_only"] is True for request in requests)
    assert all(request["requested_authority"]["production_authority"] is False for request in requests)
    assert all(request["requested_authority"]["live_execution_authority"] is False for request in requests)
    assert all(audit_return_path in request["required_context_reads"] for request in requests)
    assert all(audit_body_path in request["required_context_reads"] for request in requests)
    assert all(DOMAIN_WEAVER_FOUNDING_ASSEMBLY_PATH.as_posix() in request["required_context_reads"] for request in requests)


def test_domain_weaver_operator_action_queues_foundation_wave0_fanin_after_terminal_returns(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    materialize_domain_weaver_founding_domain_assembly(tmp_path)

    audit_request_path = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_founding_assembly_nemesis_audit_20260601_attempt_001.json"
    )
    audit_return_path = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-01T040102Z0000_task_return.json"
    audit_receipt_path = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        "2026-06-01T040102Z0000_task_return_machine_receipt.json"
    )
    audit_run_path = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_2026-06-01T035216Z0000_codex_req_domain_weaver_founding_assembly_nemesis_audit_20260601_attempt_001/"
        "run.json"
    )
    audit_body_path = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_2026-06-01T035216Z0000_codex_req_domain_weaver_founding_assembly_nemesis_audit_20260601_attempt_001/"
        "task_return_body.md"
    )
    _write(
        tmp_path,
        audit_request_path,
        json.dumps(
            {
                "request_id": "codex_req_domain_weaver_founding_assembly_nemesis_audit_20260601_attempt_001",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "latest_return_packet_path": audit_return_path,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        audit_return_path,
        json.dumps({"accepted_for_carrier_intake": True, "machine_receipt_path": audit_receipt_path}, indent=2)
        + "\n",
    )
    _write(tmp_path, audit_receipt_path, "{}\n")
    _write(
        tmp_path,
        audit_run_path,
        json.dumps(
            {
                "request_id": "codex_req_domain_weaver_founding_assembly_nemesis_audit_20260601_attempt_001",
                "task_return_body_path": audit_body_path,
            },
            indent=2,
        )
        + "\n",
    )
    _write(tmp_path, audit_body_path, "### RECOMMENDED NEXT PACKET\nPCKT-DOMAIN-WEAVER-FOUNDATION-WAVE0-INDEPENDENT-RETURNS-20260601\n")

    queue_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_foundation_wave0_independent_returns",
            "packet_id": "PCKT-DOMAIN-WEAVER-FOUNDATION-WAVE0-INDEPENDENT-RETURNS-20260601",
            "confirmation": CONFIRMATION,
        },
    )
    assert queue_result["ok"] is True

    ledger = json.loads((tmp_path / DOMAIN_WEAVER_FOUNDATION_WAVE0_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    blocked_domains = {"context_cartography_domain", "queue_hygiene_governance_domain"}
    return_paths: list[str] = []
    for row in ledger["queued_requests"]:
        request_path = row["packet_path"]
        request = json.loads((tmp_path / request_path).read_text(encoding="utf-8"))
        domain_id = request["domain_weaver_foundation_wave0"]["domain_id"]
        blocked = domain_id in blocked_domains
        status = "RETURN_RECORDED_PROOF_BLOCKED" if blocked else "RETURN_RECORDED_PROOF_ACCEPTED"
        return_path = (
            "ION/05_context/current/chatgpt_connector/task_returns/"
            f"2026-06-01T042000Z_{domain_id}_task_return.json"
        )
        receipt_path = (
            "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
            f"2026-06-01T042000Z_{domain_id}_task_return_machine_receipt.json"
        )
        run_path = (
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
            f"codex_run_wave0_{domain_id}/run.json"
        )
        body_path = (
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
            f"codex_run_wave0_{domain_id}/task_return_body.md"
        )
        latest_return_md_path = (
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
            f"codex_run_wave0_{domain_id}/latest_return.md"
        )
        return_paths.append(return_path)
        request["status"] = status
        request["latest_return_packet_path"] = return_path
        request["return_packet_paths"] = [return_path]
        _write(tmp_path, request_path, json.dumps(request, indent=2, sort_keys=True) + "\n")
        _write(
            tmp_path,
            return_path,
            json.dumps(
                {
                    "accepted_for_carrier_intake": not blocked,
                    "return_template_valid": True,
                    "context_proof_result": {"accepted": not blocked},
                    "template_action_proof_result": {"accepted": True},
                    "workload_diff_accepted": True,
                    "machine_receipt_path": receipt_path,
                    "work_request_id": request["request_id"],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        _write(tmp_path, receipt_path, json.dumps({"accepted_for_carrier_intake": not blocked}, indent=2) + "\n")
        _write(
            tmp_path,
            run_path,
            json.dumps(
                {
                    "request_id": request["request_id"],
                    "request_path": request_path,
                    "status": status,
                    "latest_return_packet_path": return_path,
                    "task_return_body_path": body_path,
                    "last_message_path": latest_return_md_path,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        if domain_id == "queue_hygiene_governance_domain":
            _write(tmp_path, latest_return_md_path, "### CONTEXT PROOF\n### TEMPLATE ACTION PROOF\n### RESULT\n")
        else:
            _write(tmp_path, body_path, "### CONTEXT PROOF\n### TEMPLATE ACTION PROOF\n### RESULT\n")

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_foundation_wave0_fanin_settlement",
            "packet_id": "PCKT-DOMAIN-WEAVER-FOUNDATION-WAVE0-FANIN-SETTLEMENT-AND-NEMESIS-OVERCLAIM-AUDIT-20260601",
            "confirmation": CONFIRMATION,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["wave0_returns_terminal"] is True
    assert result["summary"]["expected_return_count"] == 6
    assert result["summary"]["accepted_return_count"] == 4
    assert result["summary"]["explicit_blocked_receipt_count"] == 2
    assert result["summary"]["queued_request_count"] == 1
    assert result["summary"]["worker_started_count"] == 0

    fanin_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_FOUNDATION_WAVE0_FANIN_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    assert fanin_ledger["schema_id"] == "ion.domain_weaver.foundation_wave0_fanin_settlement_queue_ledger.v0_1_candidate"
    fanin_request = json.loads((tmp_path / fanin_ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8"))
    assert fanin_request["request_kind"] == "domain_weaver_foundation_wave0_fanin_settlement"
    assert fanin_request["agent_role"] == "role.nemesis"
    assert fanin_request["supporting_roles"] == ["role.scribe"]
    assert fanin_request["requested_model"] == "gpt-5.5"
    assert fanin_request["requested_reasoning_effort"] == "xhigh"
    assert fanin_request["domain_weaver_foundation_wave0_fanin"]["terminal_return_count"] == 6
    assert fanin_request["domain_weaver_foundation_wave0_fanin"]["accepted_return_count"] == 4
    assert fanin_request["domain_weaver_foundation_wave0_fanin"]["explicit_blocked_receipt_count"] == 2
    assert all(path in fanin_request["required_context_reads"] for path in return_paths)
    assert (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_wave0_queue_hygiene_governance_domain/latest_return.md"
    ) in fanin_request["required_context_reads"]
    assert (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_wave0_queue_hygiene_governance_domain/task_return_body.md"
    ) not in fanin_request["required_context_reads"]
    assert fanin_request["requested_authority"]["production_authority"] is False
    assert fanin_request["requested_authority"]["live_execution_authority"] is False


def _seed_domain_weaver_wave0_fanin_blocked_settlement(tmp_path: Path) -> None:
    materialize_domain_weaver_founding_domain_assembly(tmp_path)
    for rel in [
        "Needs_Routed/ION_DOMAIN_WEAVE_FULL_ION_MASTER_PLAN_v0_1.md",
        "Needs_Routed/M103_DOMAIN_WEAVE_INTEGRATED_SUBSTRATE_PLAN.md",
        "ION/05_context/current/domain_weaver/audits/20260531T224531Z_domain_weaver_architecture_breach_report.json",
        "ION/05_context/current/domain_weaver/audits/20260531T224439Z_domain_weaver_role_simulation_stop_the_line.json",
        "ION/05_context/current/domain_weaver/live_carrier_binding/DOMAIN_WEAVER_ROUTE_EXECUTION_GATE.candidate.json",
        "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
        "ION/04_packages/kernel/ion_domain_weaver.py",
        "ION/04_packages/kernel/ion_cockpit_view_model.py",
        "ION/04_packages/kernel/ion_codex_queue_runner.py",
        "ION/04_packages/kernel/ion_carrier_task_return.py",
        "ION/tests/test_kernel_ion_agent_control_plane.py",
        "ION/05_context/current/ACTIVE_CARRIER_MESSAGE_QUEUE.json",
    ]:
        _write(tmp_path, rel, "{}\n" if rel.endswith(".json") else f"# {Path(rel).name}\n")

    audit_request_path = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_founding_assembly_nemesis_audit_20260601_attempt_001.json"
    )
    audit_return_path = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-01T040102Z0000_task_return.json"
    audit_receipt_path = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        "2026-06-01T040102Z0000_task_return_machine_receipt.json"
    )
    audit_body_path = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_2026-06-01T035216Z0000_codex_req_domain_weaver_founding_assembly_nemesis_audit_20260601_attempt_001/"
        "task_return_body.md"
    )
    _write(
        tmp_path,
        audit_request_path,
        json.dumps(
            {
                "request_id": "codex_req_domain_weaver_founding_assembly_nemesis_audit_20260601_attempt_001",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "latest_return_packet_path": audit_return_path,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        audit_return_path,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": audit_receipt_path,
                "template_action_proof_result": {"touched_paths": [audit_body_path]},
            },
            indent=2,
        )
        + "\n",
    )
    _write(tmp_path, audit_receipt_path, "{}\n")
    _write(tmp_path, audit_body_path, "### RECOMMENDED NEXT PACKET\nPCKT-DOMAIN-WEAVER-FOUNDATION-WAVE0-INDEPENDENT-RETURNS-20260601\n")

    queued = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_foundation_wave0_independent_returns",
            "packet_id": "PCKT-DOMAIN-WEAVER-FOUNDATION-WAVE0-INDEPENDENT-RETURNS-20260601",
            "confirmation": CONFIRMATION,
        },
    )
    assert queued["ok"] is True
    ledger = json.loads((tmp_path / DOMAIN_WEAVER_FOUNDATION_WAVE0_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    blocked_domains = {"context_cartography_domain", "queue_hygiene_governance_domain"}
    for row in ledger["queued_requests"]:
        request_path = row["packet_path"]
        request = json.loads((tmp_path / request_path).read_text(encoding="utf-8"))
        domain_id = request["domain_weaver_foundation_wave0"]["domain_id"]
        blocked = domain_id in blocked_domains
        return_path = (
            "ION/05_context/current/chatgpt_connector/task_returns/"
            f"2026-06-01T042000Z_{domain_id}_task_return.json"
        )
        receipt_path = (
            "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
            f"2026-06-01T042000Z_{domain_id}_task_return_machine_receipt.json"
        )
        run_path = (
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
            f"codex_run_wave0_{domain_id}/run.json"
        )
        body_path = (
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
            f"codex_run_wave0_{domain_id}/task_return_body.md"
        )
        latest_return_md_path = (
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
            f"codex_run_wave0_{domain_id}/latest_return.md"
        )
        request["status"] = "RETURN_RECORDED_PROOF_BLOCKED" if blocked else "RETURN_RECORDED_PROOF_ACCEPTED"
        request["latest_return_packet_path"] = return_path
        request["return_packet_paths"] = [return_path]
        _write(tmp_path, request_path, json.dumps(request, indent=2, sort_keys=True) + "\n")
        _write(
            tmp_path,
            return_path,
            json.dumps(
                {
                    "accepted_for_carrier_intake": not blocked,
                    "return_template_valid": True,
                    "context_proof_result": {"accepted": not blocked},
                    "template_action_proof_result": {"accepted": True},
                    "workload_diff_accepted": True,
                    "machine_receipt_path": receipt_path,
                    "work_request_id": request["request_id"],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        _write(tmp_path, receipt_path, json.dumps({"accepted_for_carrier_intake": not blocked}, indent=2) + "\n")
        _write(
            tmp_path,
            run_path,
            json.dumps(
                {
                    "request_id": request["request_id"],
                    "request_path": request_path,
                    "status": request["status"],
                    "latest_return_packet_path": return_path,
                    "task_return_body_path": body_path,
                    "last_message_path": latest_return_md_path,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        _write(tmp_path, body_path, "### CONTEXT PROOF\n### TEMPLATE ACTION PROOF\n### RESULT\n")
        _write(tmp_path, latest_return_md_path, "latest return\n")

    fanin = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_foundation_wave0_fanin_settlement",
            "packet_id": "PCKT-DOMAIN-WEAVER-FOUNDATION-WAVE0-FANIN-SETTLEMENT-AND-NEMESIS-OVERCLAIM-AUDIT-20260601",
            "confirmation": CONFIRMATION,
        },
    )
    assert fanin["ok"] is True
    fanin_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_FOUNDATION_WAVE0_FANIN_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    fanin_request_path = fanin_ledger["queued_requests"][0]["packet_path"]
    fanin_request = json.loads((tmp_path / fanin_request_path).read_text(encoding="utf-8"))
    fanin_return_path = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-01T045119Z0000_task_return.json"
    fanin_receipt_path = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        "2026-06-01T045119Z0000_task_return_machine_receipt.json"
    )
    fanin_body_path = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/codex_run_wave0_fanin/"
        "task_return_body.md"
    )
    fanin_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    fanin_request["latest_return_packet_path"] = fanin_return_path
    fanin_request["return_packet_paths"] = [fanin_return_path]
    _write(tmp_path, fanin_request_path, json.dumps(fanin_request, indent=2, sort_keys=True) + "\n")
    _write(
        tmp_path,
        fanin_return_path,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {"accepted": True, "touched_paths": [fanin_body_path]},
                "workload_diff_accepted": True,
                "machine_receipt_path": fanin_receipt_path,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(tmp_path, fanin_receipt_path, json.dumps({"accepted_for_carrier_intake": True}, indent=2) + "\n")
    _write(
        tmp_path,
        fanin_body_path,
        "### WAVE 0 FAN-IN VERDICT\nWAVE0_FANIN_BLOCKED_REBASELINE_AND_REISSUE_REQUIRED\n"
        "### RECOMMENDED NEXT PACKET\n"
        "PCKT-DOMAIN-WEAVER-FOUNDATION-WAVE0-REBASELINE-REISSUE-CONTEXT-AND-QUEUE-HYGIENE-20260601\n",
    )


def test_domain_weaver_wave0_rebaseline_reissue_action_queues_two_blocked_domains(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_wave0_fanin_blocked_settlement(tmp_path)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_foundation_wave0_rebaseline_reissue_context_and_queue_hygiene",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-FOUNDATION-WAVE0-REBASELINE-REISSUE-CONTEXT-AND-QUEUE-HYGIENE-20260601"
            ),
            "confirmation": CONFIRMATION,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["foundation_wave0_rebaseline_ready"] is True
    assert result["summary"]["accepted_return_count"] == 4
    assert result["summary"]["reissue_required_count"] == 2
    assert result["summary"]["queued_request_count"] == 2
    assert result["summary"]["worker_started_count"] == 0
    assert (tmp_path / DOMAIN_WEAVER_FOUNDATION_WAVE0_REBASELINE_PLAN_PATH).is_file()
    assert (tmp_path / DOMAIN_WEAVER_FOUNDATION_WAVE0_REISSUE_QUEUE_LEDGER_PATH).is_file()
    plan = json.loads((tmp_path / DOMAIN_WEAVER_FOUNDATION_WAVE0_REBASELINE_PLAN_PATH).read_text(encoding="utf-8"))
    assert plan["summary"]["source_fanin_accepted"] is True
    assert plan["summary"]["reissue_required_count"] == 2
    assert {row["source_domain_id"] for row in plan["reissue_records"]} == {
        "context_cartography_domain",
        "queue_hygiene_governance_domain",
    }

    queued_domains = set()
    for rel in result["summary"]["work_request_paths"]:
        request = json.loads((tmp_path / rel).read_text(encoding="utf-8"))
        reissue = request["domain_weaver_foundation_wave0_reissue"]
        queued_domains.add(reissue["domain_id"])
        assert request["status"] == "QUEUED_FOR_CODEX_CARRIER"
        assert request["request_kind"] == "domain_weaver_foundation_wave0_reissue"
        assert request["requested_by"] == "domain_weaver_foundation_wave0_rebaseline_reissue"
        assert request["requested_model"] == "gpt-5.5"
        assert request["requested_reasoning_effort"] == "xhigh"
        assert DOMAIN_WEAVER_FOUNDATION_WAVE0_REBASELINE_PLAN_PATH.as_posix() in request["required_context_reads"]
        assert "ION/04_packages/kernel/ion_cockpit_view_model.py" in request["required_context_reads"]
        assert request["production_authority"] is False
        assert request["live_execution_authority"] is False
        assert request["accepted_state_authority"] is False
        assert request["secrets_authority"] is False
        if reissue["domain_id"] == "queue_hygiene_governance_domain":
            assert reissue["role_phase_sequence"].startswith("PERSONA_INTERFACE_INGRESS")
            assert "role_phase_sequence" in request["objective"]
    assert queued_domains == {"context_cartography_domain", "queue_hygiene_governance_domain"}

    for rel in result["summary"]["work_request_paths"]:
        request = json.loads((tmp_path / rel).read_text(encoding="utf-8"))
        domain_id = request["domain_weaver_foundation_wave0_reissue"]["domain_id"]
        return_path = (
            "ION/05_context/current/chatgpt_connector/task_returns/"
            f"2026-06-01T050000Z_{domain_id}_attempt_002_task_return.json"
        )
        receipt_path = (
            "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
            f"2026-06-01T050000Z_{domain_id}_attempt_002_task_return_machine_receipt.json"
        )
        run_path = (
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
            f"codex_run_wave0_{domain_id}_attempt_002/run.json"
        )
        body_path = (
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
            f"codex_run_wave0_{domain_id}_attempt_002/task_return_body.md"
        )
        request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        request["latest_return_packet_path"] = return_path
        request["return_packet_paths"] = [return_path]
        _write(tmp_path, rel, json.dumps(request, indent=2, sort_keys=True) + "\n")
        _write(
            tmp_path,
            return_path,
            json.dumps(
                {
                    "accepted_for_carrier_intake": True,
                    "return_template_valid": True,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {"accepted": True, "touched_paths": [body_path]},
                    "workload_diff_accepted": True,
                    "machine_receipt_path": receipt_path,
                    "work_request_id": request["request_id"],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        _write(tmp_path, receipt_path, json.dumps({"accepted_for_carrier_intake": True}, indent=2) + "\n")
        _write(
            tmp_path,
            run_path,
            json.dumps(
                {
                    "request_id": request["request_id"],
                    "request_path": rel,
                    "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                    "latest_return_packet_path": return_path,
                    "task_return_body_path": body_path,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        _write(tmp_path, body_path, "### CONTEXT PROOF\n### ION OPERATIONAL POSTURE\n")

    fanin = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_foundation_wave0_fanin_settlement",
            "packet_id": "PCKT-DOMAIN-WEAVER-FOUNDATION-WAVE0-FANIN-SETTLEMENT-AND-NEMESIS-OVERCLAIM-AUDIT-20260601",
            "confirmation": CONFIRMATION,
        },
    )
    assert fanin["ok"] is True
    assert fanin["summary"]["accepted_return_count"] == 6
    assert fanin["summary"]["explicit_blocked_receipt_count"] == 0
    assert fanin["summary"]["worker_started_count"] == 0
    fanin_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_FOUNDATION_WAVE0_FANIN_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    fanin_request = json.loads((tmp_path / fanin_ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8"))
    latest_by_domain = {
        row["domain_id"]: row["request_id"]
        for row in fanin_request["domain_weaver_foundation_wave0_fanin"]["return_records"]
    }
    assert latest_by_domain["context_cartography_domain"].endswith("attempt_002")
    assert latest_by_domain["queue_hygiene_governance_domain"].endswith("attempt_002")


def test_domain_weaver_wave0_reissue_start_without_magic_blocks_until_rebaseline_ready(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_codex_carrier_steward(tmp_path)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_foundation_wave0_rebaseline_reissue_context_and_queue_hygiene",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-FOUNDATION-WAVE0-REBASELINE-REISSUE-CONTEXT-AND-QUEUE-HYGIENE-20260601"
            ),
            "start_workers": True,
        },
    )

    assert result["ok"] is False
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["foundation_wave0_rebaseline_ready"] is False
    assert result["summary"]["worker_started_count"] == 0


def test_domain_weaver_wave1_bounded_draft_queues_after_clean_wave0_fanin(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_wave0_fanin_blocked_settlement(tmp_path)

    reissue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_foundation_wave0_rebaseline_reissue_context_and_queue_hygiene",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-FOUNDATION-WAVE0-REBASELINE-REISSUE-CONTEXT-AND-QUEUE-HYGIENE-20260601"
            ),
            "confirmation": CONFIRMATION,
        },
    )
    assert reissue["ok"] is True

    for rel in reissue["summary"]["work_request_paths"]:
        request = json.loads((tmp_path / rel).read_text(encoding="utf-8"))
        domain_id = request["domain_weaver_foundation_wave0_reissue"]["domain_id"]
        return_path = (
            "ION/05_context/current/chatgpt_connector/task_returns/"
            f"2026-06-01T113000Z_{domain_id}_attempt_002_task_return.json"
        )
        receipt_path = (
            "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
            f"2026-06-01T113000Z_{domain_id}_attempt_002_task_return_machine_receipt.json"
        )
        run_path = (
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
            f"codex_run_wave0_{domain_id}_attempt_002/run.json"
        )
        body_path = (
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
            f"codex_run_wave0_{domain_id}_attempt_002/task_return_body.md"
        )
        request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        request["latest_return_packet_path"] = return_path
        request["return_packet_paths"] = [return_path]
        _write(tmp_path, rel, json.dumps(request, indent=2, sort_keys=True) + "\n")
        _write(
            tmp_path,
            return_path,
            json.dumps(
                {
                    "accepted_for_carrier_intake": True,
                    "return_template_valid": True,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {"accepted": True, "touched_paths": [body_path]},
                    "workload_diff_accepted": True,
                    "machine_receipt_path": receipt_path,
                    "work_request_id": request["request_id"],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        _write(tmp_path, receipt_path, json.dumps({"accepted_for_carrier_intake": True}, indent=2) + "\n")
        _write(
            tmp_path,
            run_path,
            json.dumps(
                {
                    "request_id": request["request_id"],
                    "request_path": rel,
                    "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                    "latest_return_packet_path": return_path,
                    "task_return_body_path": body_path,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        _write(tmp_path, body_path, "### CONTEXT PROOF\n### ION OPERATIONAL POSTURE\n")

    fanin = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_foundation_wave0_fanin_settlement",
            "packet_id": "PCKT-DOMAIN-WEAVER-FOUNDATION-WAVE0-FANIN-SETTLEMENT-AND-NEMESIS-OVERCLAIM-AUDIT-20260601",
            "confirmation": CONFIRMATION,
        },
    )
    assert fanin["ok"] is True
    assert fanin["summary"]["accepted_return_count"] == 6
    assert fanin["summary"]["explicit_blocked_receipt_count"] == 0

    fanin_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_FOUNDATION_WAVE0_FANIN_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    fanin_request_path = fanin_ledger["queued_requests"][0]["packet_path"]
    fanin_request = json.loads((tmp_path / fanin_request_path).read_text(encoding="utf-8"))
    fanin_return_path = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-01T115641Z0000_task_return.json"
    fanin_receipt_path = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        "2026-06-01T115641Z0000_task_return_machine_receipt.json"
    )
    fanin_body_path = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/codex_run_wave0_fanin_attempt_002/"
        "task_return_body.md"
    )
    fanin_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    fanin_request["latest_return_packet_path"] = fanin_return_path
    fanin_request["return_packet_paths"] = [fanin_return_path]
    _write(tmp_path, fanin_request_path, json.dumps(fanin_request, indent=2, sort_keys=True) + "\n")
    _write(
        tmp_path,
        fanin_return_path,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {"accepted": True, "touched_paths": [fanin_body_path]},
                "workload_diff_accepted": True,
                "machine_receipt_path": fanin_receipt_path,
                "work_request_id": fanin_request["request_id"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(tmp_path, fanin_receipt_path, json.dumps({"accepted_for_carrier_intake": True}, indent=2) + "\n")
    _write(
        tmp_path,
        fanin_body_path,
        "### WAVE 0 FAN-IN VERDICT\n"
        "verdict: WAVE0_FANIN_SETTLED_FOR_BOUNDED_WAVE1_PACKET_DRAFTING_ONLY\n"
        "### RECOMMENDED NEXT PACKET\n"
        "PCKT-DOMAIN-WEAVER-WAVE1-BOUNDED-DRAFT-ACTIVATION-FISSION-SCHEDULER-AND-SELF-EVOLUTION-PREP-20260601\n",
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave1_bounded_draft_activation_fission_scheduler_and_self_evolution_prep",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-WAVE1-BOUNDED-DRAFT-ACTIVATION-FISSION-SCHEDULER-AND-SELF-EVOLUTION-PREP-20260601"
            ),
            "confirmation": CONFIRMATION,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["wave1_draft_ready"] is True
    assert result["summary"]["queued_request_count"] == 1
    assert result["summary"]["worker_started_count"] == 0
    ledger = json.loads((tmp_path / DOMAIN_WEAVER_WAVE1_BOUNDED_DRAFT_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    assert ledger["schema_id"] == "ion.domain_weaver.wave1_bounded_draft_queue_ledger.v0_1_candidate"
    assert ledger["queue_action"] == "queue_wave1_bounded_draft_activation_fission_scheduler_and_self_evolution_prep"
    request = json.loads((tmp_path / ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8"))
    assert request["request_kind"] == "domain_weaver_wave1_bounded_draft"
    assert request["agent_role"] == "role.steward"
    assert request["supporting_roles"] == ["role.nemesis", "role.scribe"]
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["domain_weaver_wave1_bounded_draft"]["candidate_only"] is True
    assert request["domain_weaver_wave1_bounded_draft"]["draft_only"] is True
    assert "start_workers" in request["domain_weaver_wave1_bounded_draft"]["forbidden_actions"]
    assert fanin_return_path in request["required_context_reads"]
    assert fanin_body_path in request["required_context_reads"]
    assert DOMAIN_WEAVER_FOUNDATION_WAVE0_REISSUE_QUEUE_LEDGER_PATH.as_posix() in request["required_context_reads"]
    assert request["requested_authority"]["production_authority"] is False
    assert request["requested_authority"]["live_execution_authority"] is False


def _seed_domain_weaver_accepted_wave1_draft(tmp_path: Path) -> dict[str, str]:
    request_id = (
        "codex_req_domain_weaver_wave1_bounded_draft_activation_fission_scheduler_"
        "self_evolution_prep_20260601_attempt_001"
    )
    request_path = f"ION/05_context/current/chatgpt_connector/codex_work_requests/{request_id}.json"
    return_path = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-01T121812Z0000_task_return.json"
    receipt_path = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        "2026-06-01T121812Z0000_task_return_machine_receipt.json"
    )
    run_path = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_wave1_bounded_draft/run.json"
    )
    body_path = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_wave1_bounded_draft/task_return_body.md"
    )
    _write(
        tmp_path,
        DOMAIN_WEAVER_WAVE1_BOUNDED_DRAFT_QUEUE_LEDGER_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.wave1_bounded_draft_queue_ledger.v0_1_candidate",
                "status": "queued_without_worker_start",
                "queued_requests": [
                    {
                        "request_id": request_id,
                        "packet_path": request_path,
                        "dedupe_key": "domain_weaver:wave1_bounded_draft:001",
                        "lane_id": "settlement_lane",
                        "request_status": "RETURN_RECORDED_PROOF_ACCEPTED",
                        "return_accepted": True,
                    }
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        request_path,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": request_id,
                "packet_path": request_path,
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "latest_return_packet_path": return_path,
                "return_packet_paths": [return_path],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        return_path,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {"accepted": True, "touched_paths": [body_path]},
                "workload_diff_accepted": True,
                "machine_receipt_path": receipt_path,
                "work_request_id": request_id,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(tmp_path, receipt_path, json.dumps({"accepted_for_carrier_intake": True}, indent=2) + "\n")
    _write(
        tmp_path,
        run_path,
        json.dumps(
            {
                "request_id": request_id,
                "request_path": request_path,
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "latest_return_packet_path": return_path,
                "task_return_body_path": body_path,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        body_path,
        "### RESULT\n"
        "success_verdict_for_this_packet: CANDIDATE_WAVE1_DRAFT_PACKET_READY_FOR_CARRIER_INTAKE\n"
        "### RECOMMENDED NEXT PACKET\n"
        "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANOUT-REQUESTS-NO-START-20260601\n",
    )
    return {
        "request_path": request_path,
        "return_path": return_path,
        "receipt_path": receipt_path,
        "run_path": run_path,
        "body_path": body_path,
    }


def test_domain_weaver_wave1_candidate_fanout_no_start_queues_seven_domains(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    refs = _seed_domain_weaver_accepted_wave1_draft(tmp_path)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave1_candidate_fanout_requests_no_start",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANOUT-REQUESTS-NO-START-20260601",
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["required_confirmation"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["wave1_fanout_ready"] is True
    assert result["summary"]["queued_request_count"] == 7
    assert result["summary"]["worker_started_count"] == 0
    assert result["summary"]["start_workers_requested"] is False
    assert result["summary"]["worker_start_status"] == "not_started_queue_only_default"
    ledger = json.loads((tmp_path / DOMAIN_WEAVER_WAVE1_CANDIDATE_FANOUT_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    assert ledger["schema_id"] == "ion.domain_weaver.wave1_candidate_fanout_no_start_queue_ledger.v0_1_candidate"
    assert ledger["queue_action"] == "queue_wave1_candidate_fanout_requests_no_start"
    assert ledger["summary"]["queued_request_count"] == 7
    assert ledger["summary"]["worker_started_count"] == 0

    requests = [
        json.loads((tmp_path / rel).read_text(encoding="utf-8"))
        for rel in result["summary"]["work_request_paths"]
    ]
    assert {request["domain_weaver_wave1_candidate_fanout"]["domain_id"] for request in requests} == {
        "domain_fission_architecture_domain",
        "activation_plane_governance_domain",
        "carrier_scheduler_engineering_domain",
        "approval_governance_domain",
        "fanout_fanin_settlement_domain",
        "self_evolution_domain",
        "limits_token_governance_domain",
    }
    assert all(request["request_kind"] == "domain_weaver_wave1_candidate_domain_return" for request in requests)
    assert all(request["requested_model"] == "gpt-5.5" for request in requests)
    assert all(request["requested_reasoning_effort"] == "xhigh" for request in requests)
    assert all(request["production_authority"] is False for request in requests)
    assert all(request["live_execution_authority"] is False for request in requests)
    assert all(request["accepted_state_authority"] is False for request in requests)
    assert all(request["secrets_authority"] is False for request in requests)
    assert all(
        request["domain_weaver_wave1_candidate_fanout"]["candidate_only"] is True
        and request["domain_weaver_wave1_candidate_fanout"]["no_start_materialization_only"] is True
        and request["domain_weaver_wave1_candidate_fanout"]["worker_start_authorized"] is False
        for request in requests
    )
    assert all(refs["body_path"] in request["required_context_reads"] for request in requests)
    assert all(
        DOMAIN_WEAVER_WAVE1_BOUNDED_DRAFT_QUEUE_LEDGER_PATH.as_posix() in request["required_context_reads"]
        for request in requests
    )
    assert all("ION/03_registry/codex_cli_carrier_profile.yaml" in request["required_context_reads"] for request in requests)


def test_domain_weaver_wave1_candidate_fanout_rejects_worker_start(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_accepted_wave1_draft(tmp_path)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave1_candidate_fanout_requests_no_start",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANOUT-REQUESTS-NO-START-20260601",
            "start_workers": True,
            "live_execution_confirmation": "ION_DOMAIN_WEAVER_LIVE_EXECUTION_CONFIRMED",
            "confirmation": CONFIRMATION,
        },
    )

    assert result["ok"] is False
    assert result["finding"] == "no_start_packet_rejects_worker_start"
    assert result["worker_started_count"] == 0


def test_domain_weaver_wave1_candidate_fanout_start_without_magic_blocks_until_queue_ready(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "start_wave1_candidate_fanout_workers",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANOUT-WORKER-START-20260601",
            "start_workers": True,
        },
    )

    assert result["ok"] is False
    assert result["summary"]["blocked_reason"] == "wave1_candidate_fanout_no_start_queue_not_ready"
    assert result["summary"]["worker_started_count"] == 0


def test_domain_weaver_wave1_candidate_fanout_worker_start_uses_lane_limits(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_accepted_wave1_draft(tmp_path)
    queue_only = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave1_candidate_fanout_requests_no_start",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANOUT-REQUESTS-NO-START-20260601",
            "confirmation": CONFIRMATION,
        },
    )
    assert queue_only["ok"] is True

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": f"ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_wave1_{len(calls)}",
                "pid": 9200 + len(calls),
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "start_wave1_candidate_fanout_workers",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANOUT-WORKER-START-20260601",
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["queued_request_count"] == 7
    assert result["summary"]["approval_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["approval_governor_max_parallel_live_workers"] == 3
    assert result["summary"]["worker_started_count"] == 3
    assert result["summary"]["remaining_queueable_start_request_count"] == 4
    assert len(calls) == 3
    assert all(call["start"] is True for call in calls)
    assert all(call["background"] is True for call in calls)
    start_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_WAVE1_CANDIDATE_FANOUT_WORKER_START_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert start_ledger["schema_id"] == "ion.domain_weaver.wave1_candidate_fanout_worker_start_queue_ledger.v0_1_candidate"
    assert start_ledger["queue_action"] == "start_wave1_candidate_fanout_workers"
    assert start_ledger["source_plan_path"] == DOMAIN_WEAVER_WAVE1_CANDIDATE_FANOUT_QUEUE_LEDGER_PATH.as_posix()
    started_rows = [row for row in start_ledger["queued_requests"] if row["worker_started"]]
    assert len(started_rows) == 3
    assert {row["lane_id"] for row in started_rows} == {
        "architecture_lane",
        "settlement_lane",
        "maintenance_lane",
    }
    no_start_ledger = json.loads((tmp_path / DOMAIN_WEAVER_WAVE1_CANDIDATE_FANOUT_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    assert no_start_ledger["summary"]["worker_started_count"] == 0


def test_domain_weaver_wave1_candidate_fanout_worker_start_skips_accepted_domains(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_accepted_wave1_draft(tmp_path)
    queue_only = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave1_candidate_fanout_requests_no_start",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANOUT-REQUESTS-NO-START-20260601",
            "confirmation": CONFIRMATION,
        },
    )
    assert queue_only["ok"] is True
    accepted_domains = {
        "domain_fission_architecture_domain",
        "activation_plane_governance_domain",
        "carrier_scheduler_engineering_domain",
    }
    ledger = json.loads((tmp_path / DOMAIN_WEAVER_WAVE1_CANDIDATE_FANOUT_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    accepted_paths = set()
    for row in ledger["queued_requests"]:
        request_path = tmp_path / row["packet_path"]
        request = json.loads(request_path.read_text(encoding="utf-8"))
        domain_id = request["domain_weaver_wave1_candidate_fanout"]["domain_id"]
        if domain_id not in accepted_domains:
            continue
        return_path = (
            "ION/05_context/current/chatgpt_connector/task_returns/"
            f"2026-06-01T130000Z_{domain_id}_task_return.json"
        )
        request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        request["latest_return_packet_path"] = return_path
        request["return_packet_paths"] = [return_path]
        request_path.write_text(json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        accepted_paths.add(row["packet_path"])
        _write(
            tmp_path,
            return_path,
            json.dumps(
                {
                    "accepted_for_carrier_intake": True,
                    "return_template_valid": True,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {"accepted": True},
                    "workload_diff_accepted": True,
                    "work_request_id": request["request_id"],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": f"ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_wave1_skip_{len(calls)}",
                "pid": 9300 + len(calls),
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "start_wave1_candidate_fanout_workers",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANOUT-WORKER-START-20260601",
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["worker_started_count"] == 3
    assert calls
    assert all(call["request_path"] not in accepted_paths for call in calls)
    for domain_id in accepted_domains:
        duplicate = (
            tmp_path
            / "ION/05_context/current/chatgpt_connector/codex_work_requests"
            / f"codex_req_domain_weaver_wave1_{domain_id}_20260601_attempt_002.json"
        )
        assert not duplicate.exists()


def test_domain_weaver_wave1_candidate_fanin_queues_after_all_domain_returns_terminal(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_accepted_wave1_draft(tmp_path)
    queue_only = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave1_candidate_fanout_requests_no_start",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANOUT-REQUESTS-NO-START-20260601",
        },
    )
    assert queue_only["ok"] is True

    for rel in queue_only["summary"]["work_request_paths"]:
        request_path = tmp_path / rel
        request = json.loads(request_path.read_text(encoding="utf-8"))
        fanout = request["domain_weaver_wave1_candidate_fanout"]
        domain_id = fanout["domain_id"]
        return_path = (
            "ION/05_context/current/chatgpt_connector/task_returns/"
            f"2026-06-01T140000Z_{domain_id}_task_return.json"
        )
        request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        request["latest_return_packet_path"] = return_path
        request["return_packet_paths"] = [return_path]
        request_path.write_text(json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        _write(
            tmp_path,
            return_path,
            json.dumps(
                {
                    "accepted_for_carrier_intake": True,
                    "return_template_valid": True,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {"accepted": True},
                    "workload_diff_accepted": True,
                    "work_request_id": request["request_id"],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_wave1_fanin/run.json",
                "pid": 9501,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave1_candidate_fanin_settlement_and_nemesis_review",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANIN-SETTLEMENT-AND-NEMESIS-REVIEW-20260601",
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["wave1_returns_terminal"] is True
    assert result["summary"]["expected_return_count"] == 7
    assert result["summary"]["terminal_return_count"] == 7
    assert result["summary"]["accepted_return_count"] == 7
    assert result["summary"]["worker_started_count"] == 1
    assert calls == [
        {
            "request_path": result["summary"]["work_request_paths"][0],
            "start": True,
            "background": True,
        }
    ]
    ledger = json.loads((tmp_path / DOMAIN_WEAVER_WAVE1_CANDIDATE_FANIN_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    assert ledger["schema_id"] == "ion.domain_weaver.wave1_candidate_fanin_settlement_queue_ledger.v0_1_candidate"
    fanin_request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    assert fanin_request["requested_model"] == "gpt-5.5"
    assert fanin_request["requested_reasoning_effort"] == "xhigh"
    assert fanin_request["domain_weaver_wave1_candidate_fanin"]["expected_return_count"] == 7
    assert len(fanin_request["domain_weaver_wave1_candidate_fanin"]["return_records"]) == 7
    assert all(
        row["selection_policy"] == "latest_attempt_per_declared_domain"
        for row in fanin_request["domain_weaver_wave1_candidate_fanin"]["return_records"]
    )


def test_domain_weaver_wave1_steward_decision_queues_after_fanin_acceptance(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_accepted_wave1_draft(tmp_path)
    queue_only = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave1_candidate_fanout_requests_no_start",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANOUT-REQUESTS-NO-START-20260601",
        },
    )
    assert queue_only["ok"] is True
    for rel in queue_only["summary"]["work_request_paths"]:
        request_path = tmp_path / rel
        request = json.loads(request_path.read_text(encoding="utf-8"))
        domain_id = request["domain_weaver_wave1_candidate_fanout"]["domain_id"]
        return_path = (
            "ION/05_context/current/chatgpt_connector/task_returns/"
            f"2026-06-01T141000Z_{domain_id}_task_return.json"
        )
        request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        request["latest_return_packet_path"] = return_path
        request["return_packet_paths"] = [return_path]
        request_path.write_text(json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        _write(
            tmp_path,
            return_path,
            json.dumps(
                {
                    "accepted_for_carrier_intake": True,
                    "return_template_valid": True,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {"accepted": True},
                    "workload_diff_accepted": True,
                    "work_request_id": request["request_id"],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )

    fanin = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave1_candidate_fanin_settlement_and_nemesis_review",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANIN-SETTLEMENT-AND-NEMESIS-REVIEW-20260601",
        },
    )
    assert fanin["ok"] is True
    fanin_request_rel = fanin["summary"]["work_request_paths"][0]
    fanin_request_path = tmp_path / fanin_request_rel
    fanin_request = json.loads(fanin_request_path.read_text(encoding="utf-8"))
    fanin_return_path = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-01T142000Z_wave1_fanin_return.json"
    fanin_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    fanin_request["latest_return_packet_path"] = fanin_return_path
    fanin_request["return_packet_paths"] = [fanin_return_path]
    fanin_request_path.write_text(json.dumps(fanin_request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write(
        tmp_path,
        fanin_return_path,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {"accepted": True},
                "workload_diff_accepted": True,
                "work_request_id": fanin_request["request_id"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_wave1_steward/run.json",
                "pid": 9502,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave1_candidate_fanin_steward_decision_scribe_receipt_and_wave2_draft_gate",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANIN-STEWARD-DECISION-SCRIBE-RECEIPT-"
                "AND-WAVE2-DRAFT-GATE-20260601"
            ),
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["wave1_fanin_accepted"] is True
    assert result["summary"]["accepted_return_count"] == 7
    assert result["summary"]["worker_started_count"] == 1
    assert len(calls) == 1
    ledger = json.loads((tmp_path / DOMAIN_WEAVER_WAVE1_STEWARD_DECISION_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    assert ledger["schema_id"] == "ion.domain_weaver.wave1_steward_decision_wave2_gate_queue_ledger.v0_1_candidate"
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["domain_weaver_wave1_steward_decision"]["source_fanin_return_path"] == fanin_return_path
    assert len(request["domain_weaver_wave1_steward_decision"]["return_records"]) == 7


def test_domain_weaver_wave2_draft_gate_decision_queues_after_steward_acceptance(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_accepted_wave1_draft(tmp_path)
    queue_only = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave1_candidate_fanout_requests_no_start",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANOUT-REQUESTS-NO-START-20260601",
        },
    )
    assert queue_only["ok"] is True
    for rel in queue_only["summary"]["work_request_paths"]:
        request_path = tmp_path / rel
        request = json.loads(request_path.read_text(encoding="utf-8"))
        domain_id = request["domain_weaver_wave1_candidate_fanout"]["domain_id"]
        return_path = (
            "ION/05_context/current/chatgpt_connector/task_returns/"
            f"2026-06-01T143000Z_{domain_id}_task_return.json"
        )
        request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        request["latest_return_packet_path"] = return_path
        request["return_packet_paths"] = [return_path]
        request_path.write_text(json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        _write(
            tmp_path,
            return_path,
            json.dumps(
                {
                    "accepted_for_carrier_intake": True,
                    "return_template_valid": True,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {"accepted": True},
                    "workload_diff_accepted": True,
                    "work_request_id": request["request_id"],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )

    fanin = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave1_candidate_fanin_settlement_and_nemesis_review",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANIN-SETTLEMENT-AND-NEMESIS-REVIEW-20260601",
        },
    )
    assert fanin["ok"] is True
    fanin_request_rel = fanin["summary"]["work_request_paths"][0]
    fanin_request_path = tmp_path / fanin_request_rel
    fanin_request = json.loads(fanin_request_path.read_text(encoding="utf-8"))
    fanin_return_path = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-01T144000Z_wave1_fanin_return.json"
    fanin_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    fanin_request["latest_return_packet_path"] = fanin_return_path
    fanin_request["return_packet_paths"] = [fanin_return_path]
    fanin_request_path.write_text(json.dumps(fanin_request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write(
        tmp_path,
        fanin_return_path,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {"accepted": True},
                "workload_diff_accepted": True,
                "work_request_id": fanin_request["request_id"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    steward = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave1_candidate_fanin_steward_decision_scribe_receipt_and_wave2_draft_gate",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANIN-STEWARD-DECISION-SCRIBE-RECEIPT-"
                "AND-WAVE2-DRAFT-GATE-20260601"
            ),
        },
    )
    assert steward["ok"] is True
    steward_request_rel = steward["summary"]["work_request_paths"][0]
    steward_request_path = tmp_path / steward_request_rel
    steward_request = json.loads(steward_request_path.read_text(encoding="utf-8"))
    steward_return_path = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-01T145000Z_wave1_steward_return.json"
    steward_body_path = "ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_wave1_steward/task_return_body.md"
    steward_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    steward_request["latest_return_packet_path"] = steward_return_path
    steward_request["return_packet_paths"] = [steward_return_path]
    steward_request_path.write_text(json.dumps(steward_request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write(tmp_path, steward_body_path, "### WAVE 2 DRAFT GATE\ncandidate tracks ready\n")
    _write(
        tmp_path,
        steward_return_path,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [steward_body_path],
                },
                "workload_diff_accepted": True,
                "work_request_id": steward_request["request_id"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_wave2_gate/run.json",
                "pid": 9503,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave2_draft_gate_carrier_intake_and_track_fanout_decision",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-DRAFT-GATE-CARRIER-INTAKE-AND-TRACK-FANOUT-DECISION-20260601",
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["wave1_steward_decision_accepted"] is True
    assert result["summary"]["accepted_return_count"] == 7
    assert result["summary"]["worker_started_count"] == 1
    assert calls == [
        {
            "request_path": result["summary"]["work_request_paths"][0],
            "start": True,
            "background": True,
        }
    ]
    ledger = json.loads((tmp_path / DOMAIN_WEAVER_WAVE2_DRAFT_GATE_DECISION_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    assert ledger["schema_id"] == "ion.domain_weaver.wave2_draft_gate_decision_queue_ledger.v0_1_candidate"
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["domain_weaver_wave2_draft_gate_decision"]["source_steward_return_path"] == steward_return_path
    assert request["domain_weaver_wave2_draft_gate_decision"]["source_steward_task_return_body_path"] == steward_body_path
    assert len(request["domain_weaver_wave2_draft_gate_decision"]["tracks"]) == 5


def test_domain_weaver_wave2_track_fanout_materialization_queues_after_decision_acceptance(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_accepted_wave1_draft(tmp_path)
    queue_only = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave1_candidate_fanout_requests_no_start",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANOUT-REQUESTS-NO-START-20260601",
        },
    )
    assert queue_only["ok"] is True

    def accept_request(request_rel: str, return_rel: str, *, body_rel: str | None = None) -> None:
        request_path = tmp_path / request_rel
        request = json.loads(request_path.read_text(encoding="utf-8"))
        request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        request["latest_return_packet_path"] = return_rel
        request["return_packet_paths"] = [return_rel]
        request_path.write_text(json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        touched_paths = [body_rel] if body_rel else []
        if body_rel:
            _write(tmp_path, body_rel, "### RESULT\naccepted candidate body\n")
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "accepted_for_carrier_intake": True,
                    "return_template_valid": True,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {
                        "accepted": True,
                        "touched_paths": touched_paths,
                    },
                    "workload_diff_accepted": True,
                    "work_request_id": request["request_id"],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )

    for rel in queue_only["summary"]["work_request_paths"]:
        request = json.loads((tmp_path / rel).read_text(encoding="utf-8"))
        domain_id = request["domain_weaver_wave1_candidate_fanout"]["domain_id"]
        accept_request(
            rel,
            "ION/05_context/current/chatgpt_connector/task_returns/"
            f"2026-06-01T150000Z_{domain_id}_task_return.json",
        )

    fanin = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave1_candidate_fanin_settlement_and_nemesis_review",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANIN-SETTLEMENT-AND-NEMESIS-REVIEW-20260601",
        },
    )
    assert fanin["ok"] is True
    fanin_return_path = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-01T151000Z_wave1_fanin_return.json"
    accept_request(fanin["summary"]["work_request_paths"][0], fanin_return_path)

    steward = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave1_candidate_fanin_steward_decision_scribe_receipt_and_wave2_draft_gate",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-WAVE1-CANDIDATE-FANIN-STEWARD-DECISION-SCRIBE-RECEIPT-"
                "AND-WAVE2-DRAFT-GATE-20260601"
            ),
        },
    )
    assert steward["ok"] is True
    steward_return_path = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-01T152000Z_wave1_steward_return.json"
    steward_body_path = "ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_wave1_steward/task_return_body.md"
    accept_request(steward["summary"]["work_request_paths"][0], steward_return_path, body_rel=steward_body_path)

    wave2 = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave2_draft_gate_carrier_intake_and_track_fanout_decision",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-DRAFT-GATE-CARRIER-INTAKE-AND-TRACK-FANOUT-DECISION-20260601",
        },
    )
    assert wave2["ok"] is True
    wave2_return_path = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-01T153000Z_wave2_decision_return.json"
    wave2_body_path = "ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_wave2_decision/task_return_body.md"
    accept_request(wave2["summary"]["work_request_paths"][0], wave2_return_path, body_rel=wave2_body_path)

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_wave2_materialization/run.json",
                "pid": 9504,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave2_candidate_track_fanout_queue_materialization",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-CANDIDATE-TRACK-FANOUT-QUEUE-MATERIALIZATION-20260601",
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["wave2_draft_gate_decision_accepted"] is True
    assert result["summary"]["accepted_return_count"] == 7
    assert result["summary"]["worker_started_count"] == 1
    assert calls == [
        {
            "request_path": result["summary"]["work_request_paths"][0],
            "start": True,
            "background": True,
        }
    ]
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_WAVE2_TRACK_FANOUT_MATERIALIZATION_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    assert ledger["schema_id"] == "ion.domain_weaver.wave2_track_fanout_materialization_queue_ledger.v0_1_candidate"
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    materialization = request["domain_weaver_wave2_track_fanout_materialization"]
    assert materialization["source_wave2_decision_return_path"] == wave2_return_path
    assert materialization["source_wave2_decision_task_return_body_path"] == wave2_body_path
    assert materialization["start_track_workers"] is False
    assert len(materialization["track_packet_specs"]) == 5


def test_domain_weaver_wave2_candidate_track_worker_start_uses_no_magic_gate(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    materialization_request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_wave2_candidate_track_fanout_queue_materialization_20260601_attempt_001.json"
    )
    materialization_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "2026-06-01T160000Z_wave2_materialization_return.json"
    )
    materialization_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "fake_wave2_materialization/task_return_body.md"
    )
    _write(
        tmp_path,
        materialization_request_rel,
        json.dumps(
            {
                "request_id": "codex_req_domain_weaver_wave2_candidate_track_fanout_queue_materialization_20260601_attempt_001",
                "dedupe_key": "domain_weaver:wave2_track_fanout_materialization:001",
                "packet_path": materialization_request_rel,
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "latest_return_packet_path": materialization_return_rel,
                "return_packet_paths": [materialization_return_rel],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(tmp_path, materialization_body_rel, "### RESULT\nmaterialized\n")
    _write(
        tmp_path,
        materialization_return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [materialization_body_rel],
                },
                "workload_diff_accepted": True,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    track_rows = [
        ("fission_reflex_implementation_candidates", "architecture_lane"),
        ("activation_executor_and_bindings", "settlement_lane"),
        ("scheduler_lifecycle_hardening", "maintenance_lane"),
        ("approval_and_limits_ledgers", "audit_lane"),
        ("self_evolution_recursive_reaudit", "architecture_lane"),
    ]
    queued_requests = []
    for index, (track_id, lane_id) in enumerate(track_rows, start=1):
        request_id = f"codex_req_domain_weaver_wave2_{track_id}_20260601_attempt_001"
        request_rel = f"ION/05_context/current/chatgpt_connector/codex_work_requests/{request_id}.json"
        payload = {
            "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
            "request_id": request_id,
            "dedupe_key": f"domain_weaver:wave2_candidate_track:{track_id}:001",
            "idempotency_key": f"domain-weaver-wave2-{track_id}-20260601-attempt-001",
            "packet_path": request_rel,
            "status": "QUEUED_FOR_CODEX_CARRIER",
            "lane_id": lane_id,
            "work_class": f"domain_weaver_wave2_{track_id}_candidate_packet",
            "route_family": "domain_weaver_wave2_candidate_track_fanout",
            "request_kind": f"domain_weaver_wave2_{track_id}_candidate_packet",
            "agent_role": "role.steward",
            "requested_model": "gpt-5.5",
            "requested_reasoning_effort": "xhigh",
            "requested_authority": {
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_claim": False,
                "git_push_authority": False,
                "deletion_authority": False,
                "service_restart_authority": False,
            },
            "domain_weaver_wave2_candidate_track": {
                "track_id": track_id,
                "candidate_only": True,
                "proof_only": True,
                "source_materialization_request_path": materialization_request_rel,
            },
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        }
        _write(tmp_path, request_rel, json.dumps(payload, indent=2, sort_keys=True) + "\n")
        queued_requests.append(
            {
                "request_id": request_id,
                "packet_path": request_rel,
                "dedupe_key": payload["dedupe_key"],
                "lane_id": lane_id,
                "status": "queued",
                "request_status": "QUEUED_FOR_CODEX_CARRIER",
                "worker_started": False,
            }
        )

    _write(
        tmp_path,
        DOMAIN_WEAVER_WAVE2_CANDIDATE_TRACK_FANOUT_QUEUE_LEDGER_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.wave2_candidate_track_fanout_no_start_queue_ledger.v0_1_candidate",
                "status": "queued_without_worker_start",
                "queued_requests": queued_requests,
                "summary": {
                    "queued_request_count": 5,
                    "queueable_start_request_count": 5,
                    "worker_started_count": 0,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": f"ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_wave2_track_{len(calls)}/run.json",
                "pid": 9600 + len(calls),
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "start_wave2_candidate_track_workers",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-CANDIDATE-TRACK-WORKER-START-GATE-20260601",
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["wave2_track_fanout_materialization_accepted"] is True
    assert result["summary"]["worker_started_count"] == len(calls)
    assert result["summary"]["worker_started_count"] >= 1
    assert all(call["start"] is True and call["background"] is True for call in calls)
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_WAVE2_CANDIDATE_TRACK_WORKER_START_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    assert ledger["schema_id"] == "ion.domain_weaver.wave2_candidate_track_worker_start_queue_ledger.v0_1_candidate"


def test_domain_weaver_wave2_candidate_track_fanin_queues_with_template_invalid_track(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    wave2_decision_request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_wave2_draft_gate_carrier_intake_track_fanout_decision_20260601_attempt_001.json"
    )
    wave2_decision_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "2026-06-01T155000Z_wave2_decision_return.json"
    )
    materialization_request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_wave2_candidate_track_fanout_queue_materialization_20260601_attempt_001.json"
    )
    materialization_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "2026-06-01T160000Z_wave2_materialization_return.json"
    )

    def write_accepted_request(request_rel: str, request_id: str, return_rel: str) -> None:
        _write(
            tmp_path,
            request_rel,
            json.dumps(
                {
                    "request_id": request_id,
                    "packet_path": request_rel,
                    "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                    "latest_return_packet_path": return_rel,
                    "return_packet_paths": [return_rel],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "accepted_for_carrier_intake": True,
                    "return_template_valid": True,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {"accepted": True},
                    "workload_diff_accepted": True,
                    "work_request_id": request_id,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )

    write_accepted_request(
        wave2_decision_request_rel,
        "codex_req_domain_weaver_wave2_draft_gate_carrier_intake_track_fanout_decision_20260601_attempt_001",
        wave2_decision_return_rel,
    )
    write_accepted_request(
        materialization_request_rel,
        "codex_req_domain_weaver_wave2_candidate_track_fanout_queue_materialization_20260601_attempt_001",
        materialization_return_rel,
    )

    track_rows = [
        ("fission_reflex_implementation_candidates", "architecture_lane", "RETURN_RECORDED_PROOF_ACCEPTED", True),
        ("activation_executor_and_bindings", "settlement_lane", "RETURN_RECORDED_PROOF_ACCEPTED", True),
        ("scheduler_lifecycle_hardening", "maintenance_lane", "RETURN_TEMPLATE_INVALID", False),
        ("approval_and_limits_ledgers", "audit_lane", "RETURN_RECORDED_PROOF_ACCEPTED", True),
        ("self_evolution_recursive_reaudit", "architecture_lane", "RETURN_RECORDED_PROOF_ACCEPTED", True),
    ]
    queued_requests = []
    started_requests = []
    for index, (track_id, lane_id, status, accepted) in enumerate(track_rows, start=1):
        request_id = f"codex_req_domain_weaver_wave2_{track_id}_20260601_attempt_001"
        request_rel = f"ION/05_context/current/chatgpt_connector/codex_work_requests/{request_id}.json"
        return_rel = (
            "ION/05_context/current/chatgpt_connector/task_returns/"
            f"2026-06-01T160{index:02d}00Z_{track_id}_return.json"
        )
        payload = {
            "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
            "request_id": request_id,
            "dedupe_key": f"domain_weaver:wave2_candidate_track:{track_id}:001",
            "idempotency_key": f"domain-weaver-wave2-{track_id}-20260601-attempt-001",
            "packet_path": request_rel,
            "status": status,
            "latest_return_packet_path": return_rel,
            "return_packet_paths": [return_rel],
            "lane_id": lane_id,
            "work_class": f"domain_weaver_wave2_{track_id}_candidate_packet",
            "route_family": "domain_weaver_wave2_candidate_track_fanout",
            "request_kind": f"domain_weaver_wave2_{track_id}_candidate_packet",
            "agent_role": "role.steward",
            "requested_model": "gpt-5.5",
            "requested_reasoning_effort": "xhigh",
            "domain_weaver_wave2_candidate_track": {
                "track_id": track_id,
                "candidate_only": True,
                "proof_only": True,
                "source_materialization_request_path": materialization_request_rel,
            },
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        }
        _write(tmp_path, request_rel, json.dumps(payload, indent=2, sort_keys=True) + "\n")
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "accepted_for_carrier_intake": accepted,
                    "return_template_valid": accepted,
                    "context_proof_result": {"accepted": accepted},
                    "template_action_proof_result": {"accepted": True},
                    "workload_diff_accepted": True,
                    "work_request_id": request_id,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        queued_requests.append(
            {
                "request_id": request_id,
                "packet_path": request_rel,
                "dedupe_key": payload["dedupe_key"],
                "lane_id": lane_id,
                "status": "queued",
                "request_status": "QUEUED_FOR_CODEX_CARRIER",
                "worker_started": False,
            }
        )
        started_requests.append(
            {
                "request_id": request_id,
                "packet_path": request_rel,
                "dedupe_key": payload["dedupe_key"],
                "lane_id": lane_id,
                "status": "queued",
                "request_status": status,
                "worker_started": True,
                "worker_pid": 9700 + index,
            }
        )

    _write(
        tmp_path,
        DOMAIN_WEAVER_WAVE2_CANDIDATE_TRACK_FANOUT_QUEUE_LEDGER_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.wave2_candidate_track_fanout_no_start_queue_ledger.v0_1_candidate",
                "status": "queued_without_worker_start",
                "queued_requests": queued_requests,
                "summary": {"queued_request_count": 5},
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        DOMAIN_WEAVER_WAVE2_CANDIDATE_TRACK_WORKER_START_QUEUE_LEDGER_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.wave2_candidate_track_worker_start_queue_ledger.v0_1_candidate",
                "status": "worker_start_succeeded",
                "queued_requests": started_requests,
                "summary": {"worker_started_count": 5},
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": (
                    "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
                    f"fake_wave2_queue_{len(calls)}/run.json"
                ),
                "pid": 9800,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave2_candidate_track_fanin_owner_nemesis_settlement",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-CANDIDATE-TRACK-FANIN-OWNER-NEMESIS-SETTLEMENT-20260601",
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["accepted_return_count"] == 4
    assert result["summary"]["template_invalid_return_count"] == 1
    assert result["summary"]["wave2_track_returns_terminal"] is True
    assert result["summary"]["worker_started_count"] == 1
    assert calls == [
        {
            "request_path": result["summary"]["work_request_paths"][0],
            "start": True,
            "background": True,
        }
    ]
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_WAVE2_CANDIDATE_TRACK_FANIN_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    assert ledger["schema_id"] == "ion.domain_weaver.wave2_candidate_track_fanin_queue_ledger.v0_1_candidate"
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    fanin = request["domain_weaver_wave2_candidate_track_fanin"]
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert fanin["accepted_return_count"] == 4
    assert fanin["template_invalid_return_count"] == 1
    assert fanin["implementation_authority"] is False

    fanin_request_rel = result["summary"]["work_request_paths"][0]
    fanin_request_path = tmp_path / fanin_request_rel
    fanin_request = json.loads(fanin_request_path.read_text(encoding="utf-8"))
    fanin_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-01T161000Z_wave2_fanin_return.json"
    fanin_body_rel = "ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_wave2_fanin/task_return_body.md"
    fanin_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    fanin_request["latest_return_packet_path"] = fanin_return_rel
    fanin_request["return_packet_paths"] = [fanin_return_rel]
    fanin_request_path.write_text(json.dumps(fanin_request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write(tmp_path, fanin_body_rel, "### RESULT\nscheduler reissue required\n")
    _write(
        tmp_path,
        fanin_return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [fanin_body_rel],
                },
                "workload_diff_accepted": True,
                "work_request_id": fanin_request["request_id"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    reissue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave2_scheduler_lifecycle_hardening_return_reissue",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-SCHEDULER-LIFECYCLE-HARDENING-RETURN-REISSUE-20260601",
            "start_workers": True,
        },
    )

    assert reissue["ok"] is True
    assert reissue["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert reissue["summary"]["wave2_candidate_track_fanin_accepted"] is True
    assert reissue["summary"]["scheduler_template_invalid"] is True
    assert reissue["summary"]["worker_started_count"] == 1
    assert calls[-1] == {
        "request_path": reissue["summary"]["work_request_paths"][0],
        "start": True,
        "background": True,
    }
    reissue_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_WAVE2_SCHEDULER_LIFECYCLE_REISSUE_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    assert reissue_ledger["schema_id"] == "ion.domain_weaver.wave2_scheduler_lifecycle_reissue_queue_ledger.v0_1_candidate"
    reissue_request = json.loads((tmp_path / reissue["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    scheduler_reissue = reissue_request["domain_weaver_wave2_scheduler_lifecycle_reissue"]
    assert reissue_request["requested_model"] == "gpt-5.5"
    assert reissue_request["requested_reasoning_effort"] == "xhigh"
    assert scheduler_reissue["source_fanin_return_path"] == fanin_return_rel
    assert scheduler_reissue["source_scheduler_template_invalid"] is True
    assert scheduler_reissue["implementation_authority"] is False

    reissue_request_rel = reissue["summary"]["work_request_paths"][0]
    reissue_request_path = tmp_path / reissue_request_rel
    reissue_request = json.loads(reissue_request_path.read_text(encoding="utf-8"))
    reissue_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-01T162000Z_scheduler_reissue_return.json"
    reissue_body_rel = "ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_scheduler_reissue/task_return_body.md"
    reissue_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    reissue_request["latest_return_packet_path"] = reissue_return_rel
    reissue_request["return_packet_paths"] = [reissue_return_rel]
    reissue_request_path.write_text(json.dumps(reissue_request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write(tmp_path, reissue_body_rel, "### RESULT\nscheduler evidence repaired\n")
    _write(
        tmp_path,
        reissue_return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [reissue_body_rel],
                },
                "workload_diff_accepted": True,
                "work_request_id": reissue_request["request_id"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    retry = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave2_candidate_track_fanin_owner_nemesis_settlement_retry",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-CANDIDATE-TRACK-FANIN-OWNER-NEMESIS-SETTLEMENT-RETRY-20260601",
            "start_workers": True,
        },
    )

    assert retry["ok"] is True
    assert retry["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert retry["summary"]["prior_fanin_accepted"] is True
    assert retry["summary"]["scheduler_reissue_accepted"] is True
    assert retry["summary"]["effective_accepted_return_count"] == 5
    assert retry["summary"]["worker_started_count"] == 1
    retry_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_WAVE2_CANDIDATE_TRACK_FANIN_RETRY_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    assert retry_ledger["schema_id"] == "ion.domain_weaver.wave2_candidate_track_fanin_retry_queue_ledger.v0_1_candidate"
    retry_request = json.loads((tmp_path / retry["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    fanin_retry = retry_request["domain_weaver_wave2_candidate_track_fanin_retry"]
    assert retry_request["requested_model"] == "gpt-5.5"
    assert retry_request["requested_reasoning_effort"] == "xhigh"
    assert fanin_retry["source_scheduler_reissue_return_path"] == reissue_return_rel
    assert fanin_retry["effective_accepted_return_count"] == 5
    assert fanin_retry["implementation_authority"] is False

    retry_request_rel = retry["summary"]["work_request_paths"][0]
    retry_request_path = tmp_path / retry_request_rel
    retry_request = json.loads(retry_request_path.read_text(encoding="utf-8"))
    retry_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-01T163000Z_fanin_retry_return.json"
    retry_body_rel = "ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_fanin_retry/task_return_body.md"
    retry_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    retry_request["latest_return_packet_path"] = retry_return_rel
    retry_request["return_packet_paths"] = [retry_return_rel]
    retry_request_path.write_text(json.dumps(retry_request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write(tmp_path, retry_body_rel, "### RESULT\n5 of 5 effective tracks accepted\n")
    _write(
        tmp_path,
        retry_return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [retry_body_rel],
                },
                "workload_diff_accepted": True,
                "work_request_id": retry_request["request_id"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    gate = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave2_bounded_implementation_gate_repin_diff_preview",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-BOUNDED-IMPLEMENTATION-GATE-REPIN-DIFF-PREVIEW-20260601",
            "start_workers": True,
        },
    )

    assert gate["ok"] is True
    assert gate["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert gate["summary"]["fanin_retry_accepted"] is True
    assert gate["summary"]["scheduler_reissue_accepted"] is True
    assert gate["summary"]["effective_accepted_return_count"] == 5
    assert gate["summary"]["source_edit_authority"] is False
    assert gate["summary"]["worker_started_count"] == 1
    gate_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    assert gate_ledger["schema_id"] == "ion.domain_weaver.wave2_implementation_gate_queue_ledger.v0_1_candidate"
    gate_request = json.loads((tmp_path / gate["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    implementation_gate = gate_request["domain_weaver_wave2_implementation_gate"]
    assert gate_request["requested_model"] == "gpt-5.5"
    assert gate_request["requested_reasoning_effort"] == "xhigh"
    assert implementation_gate["source_fanin_retry_return_path"] == retry_return_rel
    assert implementation_gate["source_edit_authority"] is False
    assert implementation_gate["implementation_authority"] is False

    gate_request_rel = gate["summary"]["work_request_paths"][0]
    gate_request_path = tmp_path / gate_request_rel
    gate_request = json.loads(gate_request_path.read_text(encoding="utf-8"))
    gate_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-01T164000Z_implementation_gate_return.json"
    gate_body_rel = "ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_implementation_gate/task_return_body.md"
    gate_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    gate_request["latest_return_packet_path"] = gate_return_rel
    gate_request["return_packet_paths"] = [gate_return_rel]
    gate_request_path.write_text(json.dumps(gate_request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write(tmp_path, gate_body_rel, "### RESULT\nsource patch candidate authorized\n")
    _write(
        tmp_path,
        gate_return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [gate_body_rel],
                },
                "workload_diff_accepted": True,
                "work_request_id": gate_request["request_id"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    source_patch = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave2_bounded_implementation_source_patch_candidate",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-BOUNDED-IMPLEMENTATION-SOURCE-PATCH-CANDIDATE-20260601",
            "start_workers": True,
        },
    )

    assert source_patch["ok"] is True
    assert source_patch["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert source_patch["summary"]["implementation_gate_accepted"] is True
    assert source_patch["summary"]["source_edit_authority"] is True
    assert source_patch["summary"]["worker_started_count"] == 1
    source_patch_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_WAVE2_SOURCE_PATCH_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    assert source_patch_ledger["schema_id"] == "ion.domain_weaver.wave2_source_patch_candidate_queue_ledger.v0_1_candidate"
    source_patch_request = json.loads(
        (tmp_path / source_patch["summary"]["work_request_paths"][0]).read_text(encoding="utf-8")
    )
    source_patch_payload = source_patch_request["domain_weaver_wave2_source_patch_candidate"]
    assert source_patch_request["requested_model"] == "gpt-5.5"
    assert source_patch_request["requested_reasoning_effort"] == "xhigh"
    assert source_patch_payload["source_implementation_gate_return_path"] == gate_return_rel
    assert source_patch_payload["source_edit_authority"] is True
    assert source_patch_payload["production_authority"] is False


def _seed_domain_weaver_wave2_implementation_preview_fixture(
    tmp_path: Path,
    *,
    accept_scheduler_reissue: bool,
) -> dict[str, str]:
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _write(
        tmp_path,
        DOMAIN_WEAVER_WAVE2_APPROVAL_AND_LIMITS_LEDGER_SCHEMA_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.wave2_approval_and_limits_ledger_schema.v0_1_candidate",
                "status": "candidate_schema_ready_for_wave2_fanin_review",
                "limits_token_ledger": {
                    "schema_id": "ion.domain_weaver.limits_token_ledger_record.v0_1_candidate",
                    "limits": {
                        "max_chain_sequence_depth": 8,
                        "max_chain_sequence_depth_without_operator_reapproval": 4,
                        "max_estimated_tokens_per_chain": 240000,
                        "max_estimated_tokens_per_worker": 60000,
                        "max_parallel_live_workers": 3,
                        "same_lane_parallelism": 1,
                        "worker_warning_threshold_tokens": 48000,
                    },
                    "hard_stop_when_any_true": [
                        "token_budget_exceeded",
                        "chain_sequence_threshold_exceeded",
                        "active_parallel_live_workers_exceeds_3",
                        "same_lane_parallelism_exceeded",
                        "unknown_lane_active_run_present",
                        "context_receipt_missing_or_stale_without_repin",
                        "required_return_proof_missing",
                        "worker_error_or_timeout",
                    ],
                    "fanin_or_reapproval_when_any_true": [
                        "chain_depth_reaches_4_without_reapproval",
                        "token_warning_threshold_crossed",
                    ],
                },
                "operator_reapproval_gates": [
                    "token_budget_exceeded_or_warning_threshold_requires_fanin",
                    "chain_depth_exceeds_4_without_reapproval",
                    "fanout_or_worker_count_limit_exceeded",
                ],
                "protected_action_stop_matrix": {
                    "stop_immediately_on": [
                        "AUTH_INVALID",
                        "gateway_token_invalid",
                        "unexpected_AUTH_MISSING",
                        "missing_approval_context",
                        "missing_limits_context",
                    ],
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    def write_returned_request(
        request_rel: str,
        request_id: str,
        return_rel: str,
        *,
        status: str = "RETURN_RECORDED_PROOF_ACCEPTED",
        accepted: bool = True,
        extra_request: dict | None = None,
    ) -> None:
        request_payload = {
            "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
            "request_id": request_id,
            "packet_path": request_rel,
            "status": status,
            "latest_return_packet_path": return_rel,
            "return_packet_paths": [return_rel],
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        }
        request_payload.update(extra_request or {})
        _write(tmp_path, request_rel, json.dumps(request_payload, indent=2, sort_keys=True) + "\n")
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "accepted_for_carrier_intake": accepted,
                    "return_template_valid": accepted,
                    "context_proof_result": {"accepted": accepted},
                    "template_action_proof_result": {
                        "accepted": True,
                        "touched_paths": [
                            "ION/05_context/current/chatgpt_connector/codex_queue_runs/fake/task_return_body.md"
                        ],
                    },
                    "workload_diff_accepted": True,
                    "work_request_id": request_id,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )

    track_rows = [
        ("fission_reflex_implementation_candidates", "architecture_lane", "RETURN_RECORDED_PROOF_ACCEPTED", True),
        ("activation_executor_and_bindings", "settlement_lane", "RETURN_RECORDED_PROOF_ACCEPTED", True),
        ("scheduler_lifecycle_hardening", "maintenance_lane", "RETURN_TEMPLATE_INVALID", False),
        ("approval_and_limits_ledgers", "audit_lane", "RETURN_RECORDED_PROOF_ACCEPTED", True),
        ("self_evolution_recursive_reaudit", "architecture_lane", "RETURN_RECORDED_PROOF_ACCEPTED", True),
    ]
    queued_requests = []
    started_requests = []
    scheduler_original_return_rel = ""
    for index, (track_id, lane_id, status, accepted) in enumerate(track_rows, start=1):
        request_id = f"codex_req_domain_weaver_wave2_{track_id}_20260601_attempt_001"
        request_rel = f"ION/05_context/current/chatgpt_connector/codex_work_requests/{request_id}.json"
        return_rel = (
            "ION/05_context/current/chatgpt_connector/task_returns/"
            f"2026-06-01T160{index:02d}00Z_{track_id}_return.json"
        )
        if track_id == "scheduler_lifecycle_hardening":
            scheduler_original_return_rel = return_rel
        write_returned_request(
            request_rel,
            request_id,
            return_rel,
            status=status,
            accepted=accepted,
            extra_request={
                "lane_id": lane_id,
                "work_class": f"domain_weaver_wave2_{track_id}_candidate_packet",
                "route_family": "domain_weaver_wave2_candidate_track_fanout",
                "request_kind": f"domain_weaver_wave2_{track_id}_candidate_packet",
                "agent_role": "role.steward",
                "domain_weaver_wave2_candidate_track": {
                    "track_id": track_id,
                    "candidate_only": True,
                    "proof_only": True,
                },
            },
        )
        queued_requests.append(
            {
                "request_id": request_id,
                "packet_path": request_rel,
                "dedupe_key": f"domain_weaver:wave2_candidate_track:{track_id}:001",
                "lane_id": lane_id,
                "status": "queued",
                "request_status": "QUEUED_FOR_CODEX_CARRIER",
                "worker_started": False,
            }
        )
        started_requests.append(
            {
                "request_id": request_id,
                "packet_path": request_rel,
                "dedupe_key": f"domain_weaver:wave2_candidate_track:{track_id}:001",
                "lane_id": lane_id,
                "status": "already_queued",
                "request_status": status,
                "worker_started": True,
                "worker_pid": 9900 + index,
            }
        )

    _write(
        tmp_path,
        DOMAIN_WEAVER_WAVE2_CANDIDATE_TRACK_FANOUT_QUEUE_LEDGER_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.wave2_candidate_track_fanout_no_start_queue_ledger.v0_1_candidate",
                "status": "queued_without_worker_start",
                "queued_requests": queued_requests,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        DOMAIN_WEAVER_WAVE2_CANDIDATE_TRACK_WORKER_START_QUEUE_LEDGER_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.wave2_candidate_track_worker_start_queue_ledger.v0_1_candidate",
                "status": "worker_start_succeeded",
                "queued_requests": started_requests,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    scheduler_reissue_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "2026-06-01T162000Z_scheduler_reissue_return.json"
    )
    if accept_scheduler_reissue:
        scheduler_reissue_request_rel = (
            "ION/05_context/current/chatgpt_connector/codex_work_requests/"
            "codex_req_domain_weaver_wave2_scheduler_lifecycle_hardening_return_reissue_20260601_attempt_001.json"
        )
        write_returned_request(
            scheduler_reissue_request_rel,
            "codex_req_domain_weaver_wave2_scheduler_lifecycle_hardening_return_reissue_20260601_attempt_001",
            scheduler_reissue_return_rel,
            extra_request={
                "domain_weaver_wave2_scheduler_lifecycle_reissue": {
                    "source_scheduler_return_path": scheduler_original_return_rel,
                },
            },
        )

    retry_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "2026-06-01T163000Z_fanin_retry_return.json"
    )
    write_returned_request(
        (
            "ION/05_context/current/chatgpt_connector/codex_work_requests/"
            "codex_req_domain_weaver_wave2_candidate_track_fanin_owner_nemesis_settlement_retry_"
            "20260601_attempt_001.json"
        ),
        "codex_req_domain_weaver_wave2_candidate_track_fanin_owner_nemesis_settlement_retry_20260601_attempt_001",
        retry_return_rel,
        extra_request={
            "domain_weaver_wave2_candidate_track_fanin_retry": {
                "effective_accepted_return_count": 5,
                "source_scheduler_reissue_return_path": scheduler_reissue_return_rel,
            },
        },
    )

    gate_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "2026-06-01T164000Z_implementation_gate_return.json"
    )
    write_returned_request(
        (
            "ION/05_context/current/chatgpt_connector/codex_work_requests/"
            "codex_req_domain_weaver_wave2_bounded_implementation_gate_repin_diff_preview_"
            "20260601_attempt_001.json"
        ),
        "codex_req_domain_weaver_wave2_bounded_implementation_gate_repin_diff_preview_20260601_attempt_001",
        gate_return_rel,
        extra_request={
            "domain_weaver_wave2_implementation_gate": {
                "source_fanin_retry_return_path": retry_return_rel,
                "source_scheduler_reissue_return_path": scheduler_reissue_return_rel,
            },
        },
    )

    source_patch_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "2026-06-01T165000Z_source_patch_return.json"
    )
    write_returned_request(
        (
            "ION/05_context/current/chatgpt_connector/codex_work_requests/"
            "codex_req_domain_weaver_wave2_bounded_implementation_source_patch_candidate_"
            "20260601_attempt_001.json"
        ),
        "codex_req_domain_weaver_wave2_bounded_implementation_source_patch_candidate_20260601_attempt_001",
        source_patch_return_rel,
        extra_request={
            "domain_weaver_wave2_source_patch_candidate": {
                "source_implementation_gate_return_path": gate_return_rel,
                "source_fanin_retry_return_path": retry_return_rel,
                "source_scheduler_reissue_return_path": scheduler_reissue_return_rel,
            },
        },
    )

    return {
        "scheduler_original_return_rel": scheduler_original_return_rel,
        "scheduler_reissue_return_rel": scheduler_reissue_return_rel,
        "retry_return_rel": retry_return_rel,
        "gate_return_rel": gate_return_rel,
        "source_patch_return_rel": source_patch_return_rel,
    }


def test_domain_weaver_wave2_bounded_implementation_preview_materializes_effective_5_of_5(
    tmp_path: Path,
):
    fixture = _seed_domain_weaver_wave2_implementation_preview_fixture(
        tmp_path,
        accept_scheduler_reissue=True,
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_wave2_bounded_implementation_preview",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-BOUNDED-IMPLEMENTATION-SOURCE-PATCH-CANDIDATE-20260601",
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["preview_status"] == "patch_ready_candidate"
    assert result["summary"]["effective_accepted_return_count"] == 5
    assert result["summary"]["original_scheduler_invalid_preserved"] is True
    preview = json.loads((tmp_path / DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_PREVIEW_PATH).read_text(encoding="utf-8"))
    rollback = json.loads(
        (tmp_path / DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_ROLLBACK_MATRIX_PATH).read_text(encoding="utf-8")
    )
    assert preview["generated_artifact_authority"]["accepted_state_authority"] is False
    assert rollback["rollback_authority"]["destructive_delete_authority"] is False
    scheduler_record = [
        row
        for row in preview["effective_track_records"]["return_records"]
        if row["track_id"] == "scheduler_lifecycle_hardening"
    ][0]
    assert scheduler_record["effective_return_packet_path"] == fixture["scheduler_reissue_return_rel"]
    assert scheduler_record["original_return_packet_path"] == fixture["scheduler_original_return_rel"]
    assert scheduler_record["original_return_preserved_as"] == "template_invalid_witness"


def test_domain_weaver_wave2_bounded_implementation_preview_blocks_without_scheduler_reissue(
    tmp_path: Path,
):
    _seed_domain_weaver_wave2_implementation_preview_fixture(
        tmp_path,
        accept_scheduler_reissue=False,
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_wave2_bounded_implementation_preview",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-BOUNDED-IMPLEMENTATION-SOURCE-PATCH-CANDIDATE-20260601",
        },
    )

    assert result["ok"] is False
    assert result["summary"]["preview_status"] == "blocked"
    assert "scheduler_lifecycle_reissue_not_accepted" in result["summary"]["blockers"]
    assert "effective_wave2_fanin_not_5_of_5" in result["summary"]["blockers"]
    assert result["summary"]["original_scheduler_invalid_preserved"] is True
    preview = json.loads((tmp_path / DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_PREVIEW_PATH).read_text(encoding="utf-8"))
    effective_summary = preview["effective_track_records"]["summary"]
    assert effective_summary["effective_accepted_return_count"] == 4
    assert effective_summary["original_scheduler_invalid_preserved"] is True


def test_domain_weaver_wave2_bounded_implementation_preview_encodes_authority_constraints(
    tmp_path: Path,
):
    _seed_domain_weaver_wave2_implementation_preview_fixture(
        tmp_path,
        accept_scheduler_reissue=True,
    )

    execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_wave2_bounded_implementation_preview",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-BOUNDED-IMPLEMENTATION-SOURCE-PATCH-CANDIDATE-20260601",
        },
    )

    preview = json.loads((tmp_path / DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_PREVIEW_PATH).read_text(encoding="utf-8"))
    rollback = json.loads(
        (tmp_path / DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_ROLLBACK_MATRIX_PATH).read_text(encoding="utf-8")
    )
    assert preview["activation_lifecycle_separation"]["carrier_intake_is_not_domain_settlement"] is True
    assert preview["activation_lifecycle_separation"]["worker_start_is_not_settlement"] is True
    assert preview["approval_limits_schema_binding"]["path"] == (
        DOMAIN_WEAVER_WAVE2_APPROVAL_AND_LIMITS_LEDGER_SCHEMA_PATH.as_posix()
    )
    assert preview["approval_limits_schema_binding"]["exists"] is True
    assert preview["approval_limits_schema_binding"]["parsed"] is True
    assert preview["approval_limits_schema_binding"]["sha256"]
    assert preview["approval_limits_schema_binding"]["limits"]["max_parallel_live_workers"] == 3
    assert "AUTH_INVALID" in preview["approval_limits_stop_conditions"]
    assert "gateway_token_invalid" in preview["approval_limits_stop_conditions"]
    assert "settlement_overclaim" in preview["approval_limits_stop_conditions"]
    assert "token_budget_exceeded" in preview["approval_limits_stop_conditions"]
    assert "token_warning_threshold_crossed" in preview["approval_limits_stop_conditions"]
    assert "chain_sequence_threshold_exceeded" in preview["approval_limits_stop_conditions"]
    assert "active_parallel_live_workers_exceeds_3" in preview["approval_limits_stop_conditions"]
    assert "same_lane_parallelism_exceeded" in preview["approval_limits_stop_conditions"]
    assert preview["approval_limits_budget_stop_condition_coverage"]["status"] == "complete"
    assert preview["approval_limits_budget_stop_condition_coverage"]["missing_from_schema"] == []
    assert preview["approval_limits_budget_stop_condition_coverage"]["missing_from_preview"] == []
    assert preview["fission_reflex_candidate_settlement"]["candidate_only"] is True
    assert preview["fission_reflex_candidate_settlement"]["active_registry_write"] is False
    assert preview["self_evolution_rollback_constraints"]["domain_lattice_mutation"] is False
    assert preview["self_evolution_rollback_constraints"]["post_patch_reaudit_required"] is True
    assert {row["scope_id"] for row in rollback["rollback_records"]} == {
        "source_patch_candidate",
        "candidate_preview_artifacts",
        "self_evolution_constraints",
    }


def test_domain_weaver_wave2_implementation_preview_settlement_queues_no_magic(
    tmp_path: Path,
    monkeypatch,
):
    fixture = _seed_domain_weaver_wave2_implementation_preview_fixture(
        tmp_path,
        accept_scheduler_reissue=True,
    )
    preview_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_wave2_bounded_implementation_preview",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-BOUNDED-IMPLEMENTATION-SOURCE-PATCH-CANDIDATE-20260601",
        },
    )
    assert preview_result["ok"] is True

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/wave2_preview_settlement_1",
                "pid": 9911,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave2_implementation_preview_owner_nemesis_settlement",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-IMPLEMENTATION-PREVIEW-OWNER-NEMESIS-SETTLEMENT-20260601",
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["source_patch_accepted"] is True
    assert result["summary"]["preview_refreshed"] is True
    assert result["summary"]["preview_status"] == "patch_ready_candidate"
    assert result["summary"]["effective_accepted_return_count"] == 5
    assert result["summary"]["original_scheduler_invalid_preserved"] is True
    assert result["summary"]["source_edit_authority"] is False
    assert result["summary"]["worker_started_count"] == 1
    assert len(calls) == 1
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_PREVIEW_SETTLEMENT_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert ledger["schema_id"] == "ion.domain_weaver.wave2_implementation_preview_settlement_queue_ledger.v0_1_candidate"
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    payload = request["domain_weaver_wave2_implementation_preview_settlement"]
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert payload["source_patch_return_path"] == fixture["source_patch_return_rel"]
    assert payload["preview_path"] == DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_PREVIEW_PATH.as_posix()
    assert payload["rollback_matrix_path"] == DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_ROLLBACK_MATRIX_PATH.as_posix()
    assert payload["approval_limits_schema_path"] == (
        DOMAIN_WEAVER_WAVE2_APPROVAL_AND_LIMITS_LEDGER_SCHEMA_PATH.as_posix()
    )
    assert payload["accepted_state_authority"] is False
    assert payload["live_execution_authority"] is False
    assert DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_PREVIEW_PATH.as_posix() in request["required_context_reads"]
    assert DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_ROLLBACK_MATRIX_PATH.as_posix() in request["required_context_reads"]
    assert DOMAIN_WEAVER_WAVE2_APPROVAL_AND_LIMITS_LEDGER_SCHEMA_PATH.as_posix() in request["required_context_reads"]


def test_domain_weaver_wave2_candidate_source_patch_settlement_queues_no_magic(
    tmp_path: Path,
    monkeypatch,
):
    fixture = _seed_domain_weaver_wave2_implementation_preview_fixture(
        tmp_path,
        accept_scheduler_reissue=True,
    )
    preview_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_wave2_bounded_implementation_preview",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-BOUNDED-IMPLEMENTATION-SOURCE-PATCH-CANDIDATE-20260601",
        },
    )
    assert preview_result["ok"] is True

    preview_settlement_request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_wave2_implementation_preview_owner_nemesis_settlement_20260601_attempt_001.json"
    )
    preview_settlement_request_id = (
        "codex_req_domain_weaver_wave2_implementation_preview_owner_nemesis_settlement_20260601_attempt_001"
    )
    preview_settlement_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "2026-06-01T170000Z_preview_settlement_return.json"
    )
    preview_settlement_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "fake_preview_settlement/task_return_body.md"
    )
    _write(
        tmp_path,
        preview_settlement_request_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": preview_settlement_request_id,
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "latest_return_packet_path": preview_settlement_return_rel,
                "return_packet_paths": [preview_settlement_return_rel],
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
                "domain_weaver_wave2_implementation_preview_settlement": {
                    "preview_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_PREVIEW_PATH.as_posix(),
                    "rollback_matrix_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_ROLLBACK_MATRIX_PATH.as_posix(),
                    "approval_limits_schema_path": DOMAIN_WEAVER_WAVE2_APPROVAL_AND_LIMITS_LEDGER_SCHEMA_PATH.as_posix(),
                    "effective_accepted_return_count": 5,
                    "original_scheduler_invalid_preserved": True,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(tmp_path, preview_settlement_body_rel, "### RESULT\nverdict: ACCEPT_CANDIDATE_PREVIEW\n")
    _write(
        tmp_path,
        preview_settlement_return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [preview_settlement_body_rel],
                },
                "workload_diff_accepted": True,
                "work_request_id": preview_settlement_request_id,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/wave2_source_settlement_1",
                "pid": 9921,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave2_candidate_source_patch_steward_nemesis_settlement",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-CANDIDATE-SOURCE-PATCH-STEWARD-NEMESIS-SETTLEMENT-20260601",
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["source_patch_accepted"] is True
    assert result["summary"]["preview_settlement_accepted"] is True
    assert result["summary"]["approval_limits_budget_stop_coverage_status"] == "complete"
    assert result["summary"]["source_edit_authority"] is False
    assert result["summary"]["worker_started_count"] == 1
    assert len(calls) == 1
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_WAVE2_CANDIDATE_SOURCE_PATCH_SETTLEMENT_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert ledger["schema_id"] == "ion.domain_weaver.wave2_candidate_source_patch_settlement_queue_ledger.v0_1_candidate"
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    payload = request["domain_weaver_wave2_candidate_source_patch_settlement"]
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert payload["source_patch_return_path"] == fixture["source_patch_return_rel"]
    assert payload["source_preview_settlement_return_path"] == preview_settlement_return_rel
    assert payload["preview_path"] == DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_PREVIEW_PATH.as_posix()
    assert payload["rollback_matrix_path"] == DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_ROLLBACK_MATRIX_PATH.as_posix()
    assert payload["approval_limits_schema_path"] == DOMAIN_WEAVER_WAVE2_APPROVAL_AND_LIMITS_LEDGER_SCHEMA_PATH.as_posix()
    assert payload["source_edit_authority"] is False
    assert payload["accepted_state_authority"] is False
    assert payload["live_execution_authority"] is False
    assert DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_PREVIEW_PATH.as_posix() in request["required_context_reads"]
    assert DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_ROLLBACK_MATRIX_PATH.as_posix() in request["required_context_reads"]
    assert DOMAIN_WEAVER_WAVE2_APPROVAL_AND_LIMITS_LEDGER_SCHEMA_PATH.as_posix() in request["required_context_reads"]
    assert preview_settlement_body_rel in request["required_context_reads"]


def test_domain_weaver_wave2_source_patch_merge_next_readiness_gate_queues_no_magic(
    tmp_path: Path,
    monkeypatch,
):
    fixture = _seed_domain_weaver_wave2_implementation_preview_fixture(
        tmp_path,
        accept_scheduler_reissue=True,
    )
    preview_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_wave2_bounded_implementation_preview",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-BOUNDED-IMPLEMENTATION-SOURCE-PATCH-CANDIDATE-20260601",
        },
    )
    assert preview_result["ok"] is True

    preview_settlement_request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_wave2_implementation_preview_owner_nemesis_settlement_20260601_attempt_001.json"
    )
    preview_settlement_request_id = (
        "codex_req_domain_weaver_wave2_implementation_preview_owner_nemesis_settlement_20260601_attempt_001"
    )
    preview_settlement_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "2026-06-01T170000Z_preview_settlement_return.json"
    )
    preview_settlement_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "fake_preview_settlement/task_return_body.md"
    )
    _write(tmp_path, preview_settlement_body_rel, "### RESULT\nverdict: ACCEPT_CANDIDATE_PREVIEW\n")
    _write(
        tmp_path,
        preview_settlement_request_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": preview_settlement_request_id,
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "latest_return_packet_path": preview_settlement_return_rel,
                "return_packet_paths": [preview_settlement_return_rel],
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
                "domain_weaver_wave2_implementation_preview_settlement": {
                    "preview_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_PREVIEW_PATH.as_posix(),
                    "rollback_matrix_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_ROLLBACK_MATRIX_PATH.as_posix(),
                    "approval_limits_schema_path": DOMAIN_WEAVER_WAVE2_APPROVAL_AND_LIMITS_LEDGER_SCHEMA_PATH.as_posix(),
                    "effective_accepted_return_count": 5,
                    "original_scheduler_invalid_preserved": True,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        preview_settlement_return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [preview_settlement_body_rel],
                },
                "workload_diff_accepted": True,
                "work_request_id": preview_settlement_request_id,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    source_settlement_request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_wave2_candidate_source_patch_steward_nemesis_settlement_20260601_attempt_001.json"
    )
    source_settlement_request_id = (
        "codex_req_domain_weaver_wave2_candidate_source_patch_steward_nemesis_settlement_20260601_attempt_001"
    )
    source_settlement_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "2026-06-01T171000Z_source_patch_settlement_return.json"
    )
    source_settlement_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "fake_source_patch_settlement/task_return_body.md"
    )
    _write(
        tmp_path,
        source_settlement_body_rel,
        "### SOURCE PATCH SETTLEMENT VERDICT\nverdict: MERGE_NEXT_CANDIDATE_SOURCE_PATCH\n",
    )
    _write(
        tmp_path,
        source_settlement_request_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": source_settlement_request_id,
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "latest_return_packet_path": source_settlement_return_rel,
                "return_packet_paths": [source_settlement_return_rel],
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
                "domain_weaver_wave2_candidate_source_patch_settlement": {
                    "source_patch_return_path": fixture["source_patch_return_rel"],
                    "source_preview_settlement_return_path": preview_settlement_return_rel,
                    "preview_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_PREVIEW_PATH.as_posix(),
                    "rollback_matrix_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_ROLLBACK_MATRIX_PATH.as_posix(),
                    "approval_limits_schema_path": DOMAIN_WEAVER_WAVE2_APPROVAL_AND_LIMITS_LEDGER_SCHEMA_PATH.as_posix(),
                    "effective_accepted_return_count": 5,
                    "original_scheduler_invalid_preserved": True,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        source_settlement_return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [source_settlement_body_rel],
                },
                "workload_diff_accepted": True,
                "work_request_id": source_settlement_request_id,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/wave2_readiness_gate_1",
                "pid": 9931,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave2_source_patch_merge_next_post_patch_readiness_gate",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-SOURCE-PATCH-MERGE-NEXT-POST-PATCH-READINESS-GATE-20260601",
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["source_patch_accepted"] is True
    assert result["summary"]["preview_settlement_accepted"] is True
    assert result["summary"]["source_patch_settlement_accepted"] is True
    assert result["summary"]["source_patch_settlement_verdict"] == "MERGE_NEXT_CANDIDATE_SOURCE_PATCH"
    assert result["summary"]["approval_limits_budget_stop_coverage_status"] == "complete"
    assert result["summary"]["source_edit_authority"] is False
    assert result["summary"]["worker_started_count"] == 1
    assert len(calls) == 1
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_WAVE2_SOURCE_PATCH_MERGE_NEXT_READINESS_GATE_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert ledger["schema_id"] == "ion.domain_weaver.wave2_source_patch_merge_next_readiness_gate_queue_ledger.v0_1_candidate"
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    payload = request["domain_weaver_wave2_source_patch_merge_next_readiness_gate"]
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert payload["source_patch_return_path"] == fixture["source_patch_return_rel"]
    assert payload["source_preview_settlement_return_path"] == preview_settlement_return_rel
    assert payload["source_patch_settlement_return_path"] == source_settlement_return_rel
    assert payload["source_patch_settlement_verdict"] == "MERGE_NEXT_CANDIDATE_SOURCE_PATCH"
    assert payload["source_edit_authority"] is False
    assert payload["accepted_state_authority"] is False
    assert payload["live_execution_authority"] is False
    assert DOMAIN_WEAVER_WAVE2_CANDIDATE_SOURCE_PATCH_SETTLEMENT_QUEUE_LEDGER_PATH.as_posix() in request[
        "required_context_reads"
    ]
    assert source_settlement_body_rel in request["required_context_reads"]


def test_domain_weaver_wave2_accepted_state_settlement_gate_queues_no_magic_without_state_authority(
    tmp_path: Path,
    monkeypatch,
):
    fixture = _seed_domain_weaver_wave2_implementation_preview_fixture(
        tmp_path,
        accept_scheduler_reissue=True,
    )
    preview_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_wave2_bounded_implementation_preview",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-BOUNDED-IMPLEMENTATION-SOURCE-PATCH-CANDIDATE-20260601",
        },
    )
    assert preview_result["ok"] is True

    source_settlement_request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_wave2_candidate_source_patch_steward_nemesis_settlement_20260601_attempt_001.json"
    )
    source_settlement_request_id = (
        "codex_req_domain_weaver_wave2_candidate_source_patch_steward_nemesis_settlement_20260601_attempt_001"
    )
    source_settlement_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "2026-06-01T171000Z_source_patch_settlement_return.json"
    )
    source_settlement_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "fake_source_patch_settlement/task_return_body.md"
    )
    _write(
        tmp_path,
        source_settlement_body_rel,
        "### SOURCE PATCH SETTLEMENT VERDICT\nverdict: MERGE_NEXT_CANDIDATE_SOURCE_PATCH\n",
    )
    _write(
        tmp_path,
        source_settlement_request_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": source_settlement_request_id,
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "latest_return_packet_path": source_settlement_return_rel,
                "return_packet_paths": [source_settlement_return_rel],
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
                "domain_weaver_wave2_candidate_source_patch_settlement": {
                    "source_patch_return_path": fixture["source_patch_return_rel"],
                    "preview_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_PREVIEW_PATH.as_posix(),
                    "rollback_matrix_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_ROLLBACK_MATRIX_PATH.as_posix(),
                    "approval_limits_schema_path": DOMAIN_WEAVER_WAVE2_APPROVAL_AND_LIMITS_LEDGER_SCHEMA_PATH.as_posix(),
                    "effective_accepted_return_count": 5,
                    "original_scheduler_invalid_preserved": True,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        source_settlement_return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [source_settlement_body_rel],
                },
                "workload_diff_accepted": True,
                "work_request_id": source_settlement_request_id,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    readiness_request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_wave2_source_patch_merge_next_post_patch_readiness_gate_20260601_attempt_001.json"
    )
    readiness_request_id = (
        "codex_req_domain_weaver_wave2_source_patch_merge_next_post_patch_readiness_gate_20260601_attempt_001"
    )
    readiness_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "2026-06-01T172000Z_readiness_gate_return.json"
    )
    readiness_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "fake_readiness_gate/task_return_body.md"
    )
    _write(
        tmp_path,
        readiness_body_rel,
        "### POST PATCH READINESS VERDICT\nverdict: READINESS_ACCEPT_NEXT_SETTLEMENT_PACKET_CANDIDATE_ONLY\n",
    )
    _write(
        tmp_path,
        readiness_request_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": readiness_request_id,
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "latest_return_packet_path": readiness_return_rel,
                "return_packet_paths": [readiness_return_rel],
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
                "domain_weaver_wave2_source_patch_merge_next_readiness_gate": {
                    "source_patch_return_path": fixture["source_patch_return_rel"],
                    "source_patch_settlement_return_path": source_settlement_return_rel,
                    "preview_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_PREVIEW_PATH.as_posix(),
                    "rollback_matrix_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_ROLLBACK_MATRIX_PATH.as_posix(),
                    "approval_limits_schema_path": DOMAIN_WEAVER_WAVE2_APPROVAL_AND_LIMITS_LEDGER_SCHEMA_PATH.as_posix(),
                    "effective_accepted_return_count": 5,
                    "original_scheduler_invalid_preserved": True,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        readiness_return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [readiness_body_rel],
                },
                "workload_diff_accepted": True,
                "work_request_id": readiness_request_id,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/wave2_accepted_state_gate_1",
                "pid": 9941,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave2_candidate_source_patch_accepted_state_settlement_gate",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-CANDIDATE-SOURCE-PATCH-ACCEPTED-STATE-SETTLEMENT-GATE-20260601",
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["source_patch_accepted"] is True
    assert result["summary"]["source_patch_settlement_accepted"] is True
    assert result["summary"]["readiness_gate_accepted"] is True
    assert result["summary"]["readiness_gate_verdict"] == "READINESS_ACCEPT_NEXT_SETTLEMENT_PACKET_CANDIDATE_ONLY"
    assert result["summary"]["accepted_state_settlement_gate"] is True
    assert result["summary"]["accepted_state_authority"] is False
    assert result["summary"]["worker_started_count"] == 1
    assert len(calls) == 1
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_WAVE2_ACCEPTED_STATE_SETTLEMENT_GATE_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert ledger["schema_id"] == (
        "ion.domain_weaver.wave2_candidate_source_patch_accepted_state_settlement_gate_queue_ledger.v0_1_candidate"
    )
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    payload = request["domain_weaver_wave2_candidate_source_patch_accepted_state_settlement_gate"]
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert payload["accepted_state_settlement_gate"] is True
    assert payload["accepted_state_authority"] is False
    assert payload["accepted_state_mutation_authority"] is False
    assert payload["source_patch_return_path"] == fixture["source_patch_return_rel"]
    assert payload["source_patch_settlement_return_path"] == source_settlement_return_rel
    assert payload["readiness_gate_return_path"] == readiness_return_rel
    assert payload["readiness_gate_verdict"] == "READINESS_ACCEPT_NEXT_SETTLEMENT_PACKET_CANDIDATE_ONLY"
    assert readiness_body_rel in request["required_context_reads"]


def test_domain_weaver_wave2_accepted_state_movement_queues_no_magic_as_authority_gate(
    tmp_path: Path,
    monkeypatch,
):
    fixture = _seed_domain_weaver_wave2_implementation_preview_fixture(
        tmp_path,
        accept_scheduler_reissue=True,
    )
    preview_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_wave2_bounded_implementation_preview",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-BOUNDED-IMPLEMENTATION-SOURCE-PATCH-CANDIDATE-20260601",
        },
    )
    assert preview_result["ok"] is True

    def write_returned_request(
        request_rel: str,
        request_id: str,
        return_rel: str,
        body_rel: str,
        body_text: str,
        *,
        extra_request: dict,
    ) -> None:
        _write(tmp_path, body_rel, body_text)
        _write(
            tmp_path,
            request_rel,
            json.dumps(
                {
                    "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                    "request_id": request_id,
                    "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                    "latest_return_packet_path": return_rel,
                    "return_packet_paths": [return_rel],
                    "production_authority": False,
                    "live_execution_authority": False,
                    "accepted_state_authority": False,
                    "secrets_authority": False,
                    **extra_request,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "accepted_for_carrier_intake": True,
                    "return_template_valid": True,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {
                        "accepted": True,
                        "touched_paths": [body_rel],
                    },
                    "workload_diff_accepted": True,
                    "work_request_id": request_id,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )

    source_settlement_request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_wave2_candidate_source_patch_steward_nemesis_settlement_20260601_attempt_001.json"
    )
    source_settlement_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "2026-06-01T171000Z_source_patch_settlement_return.json"
    )
    source_settlement_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "fake_source_patch_settlement/task_return_body.md"
    )
    write_returned_request(
        source_settlement_request_rel,
        "codex_req_domain_weaver_wave2_candidate_source_patch_steward_nemesis_settlement_20260601_attempt_001",
        source_settlement_return_rel,
        source_settlement_body_rel,
        "### SOURCE PATCH SETTLEMENT VERDICT\nverdict: MERGE_NEXT_CANDIDATE_SOURCE_PATCH\n",
        extra_request={
            "domain_weaver_wave2_candidate_source_patch_settlement": {
                "source_patch_return_path": fixture["source_patch_return_rel"],
                "preview_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_PREVIEW_PATH.as_posix(),
                "rollback_matrix_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_ROLLBACK_MATRIX_PATH.as_posix(),
                "approval_limits_schema_path": DOMAIN_WEAVER_WAVE2_APPROVAL_AND_LIMITS_LEDGER_SCHEMA_PATH.as_posix(),
                "effective_accepted_return_count": 5,
                "original_scheduler_invalid_preserved": True,
            },
        },
    )

    readiness_request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_wave2_source_patch_merge_next_post_patch_readiness_gate_20260601_attempt_001.json"
    )
    readiness_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "2026-06-01T172000Z_readiness_gate_return.json"
    )
    readiness_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "fake_readiness_gate/task_return_body.md"
    )
    write_returned_request(
        readiness_request_rel,
        "codex_req_domain_weaver_wave2_source_patch_merge_next_post_patch_readiness_gate_20260601_attempt_001",
        readiness_return_rel,
        readiness_body_rel,
        "### POST PATCH READINESS VERDICT\nverdict: READINESS_ACCEPT_NEXT_SETTLEMENT_PACKET_CANDIDATE_ONLY\n",
        extra_request={
            "domain_weaver_wave2_source_patch_merge_next_readiness_gate": {
                "source_patch_return_path": fixture["source_patch_return_rel"],
                "source_patch_settlement_return_path": source_settlement_return_rel,
                "preview_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_PREVIEW_PATH.as_posix(),
                "rollback_matrix_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_ROLLBACK_MATRIX_PATH.as_posix(),
                "approval_limits_schema_path": DOMAIN_WEAVER_WAVE2_APPROVAL_AND_LIMITS_LEDGER_SCHEMA_PATH.as_posix(),
                "effective_accepted_return_count": 5,
                "original_scheduler_invalid_preserved": True,
            },
        },
    )

    accepted_state_gate_request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_wave2_candidate_source_patch_accepted_state_settlement_gate_"
        "20260601_attempt_001.json"
    )
    accepted_state_gate_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "2026-06-01T173000Z_accepted_state_settlement_gate_return.json"
    )
    accepted_state_gate_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "fake_accepted_state_gate/task_return_body.md"
    )
    write_returned_request(
        accepted_state_gate_request_rel,
        "codex_req_domain_weaver_wave2_candidate_source_patch_accepted_state_settlement_gate_20260601_attempt_001",
        accepted_state_gate_return_rel,
        accepted_state_gate_body_rel,
        (
            "### ACCEPTED STATE SETTLEMENT GATE VERDICT\n"
            "verdict: ACCEPT_ROUTE_TO_FUTURE_BOUNDED_ACCEPTED_STATE_MOVEMENT\n"
        ),
        extra_request={
            "domain_weaver_wave2_candidate_source_patch_accepted_state_settlement_gate": {
                "source_patch_return_path": fixture["source_patch_return_rel"],
                "source_patch_settlement_return_path": source_settlement_return_rel,
                "readiness_gate_return_path": readiness_return_rel,
                "preview_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_PREVIEW_PATH.as_posix(),
                "rollback_matrix_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_ROLLBACK_MATRIX_PATH.as_posix(),
                "approval_limits_schema_path": DOMAIN_WEAVER_WAVE2_APPROVAL_AND_LIMITS_LEDGER_SCHEMA_PATH.as_posix(),
                "effective_accepted_return_count": 5,
                "original_scheduler_invalid_preserved": True,
                "accepted_state_authority": False,
                "accepted_state_mutation_authority": False,
            },
        },
    )

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/wave2_accepted_state_movement_1",
                "pid": 9942,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave2_candidate_source_patch_accepted_state_movement",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-CANDIDATE-SOURCE-PATCH-ACCEPTED-STATE-MOVEMENT-20260601",
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["accepted_state_settlement_gate_accepted"] is True
    assert result["summary"]["accepted_state_settlement_gate_verdict"] == (
        "ACCEPT_ROUTE_TO_FUTURE_BOUNDED_ACCEPTED_STATE_MOVEMENT"
    )
    assert result["summary"]["accepted_state_movement_requested"] is True
    assert result["summary"]["operator_magic_string_required"] is False
    assert result["summary"]["expected_noop_without_authority_receipt"] is True
    assert result["summary"]["accepted_state_authority"] is False
    assert result["summary"]["accepted_state_mutation_authority"] is False
    assert result["summary"]["worker_started_count"] == 1
    assert len(calls) == 1
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_WAVE2_ACCEPTED_STATE_MOVEMENT_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert ledger["schema_id"] == (
        "ion.domain_weaver.wave2_candidate_source_patch_accepted_state_movement_queue_ledger.v0_1_candidate"
    )
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    payload = request["domain_weaver_wave2_candidate_source_patch_accepted_state_movement"]
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert payload["accepted_state_movement_requested"] is True
    assert payload["operator_magic_string_required"] is False
    assert payload["accepted_state_authority"] is False
    assert payload["accepted_state_mutation_authority"] is False
    assert payload["expected_noop_without_authority_receipt"] is True
    assert payload["accepted_state_settlement_gate_return_path"] == accepted_state_gate_return_rel
    assert accepted_state_gate_body_rel in request["required_context_reads"]
    assert "do not ask the operator for an incantation" in request["objective"]


def test_domain_weaver_wave2_authority_receipt_repair_queues_no_magic_from_noop_movement(
    tmp_path: Path,
    monkeypatch,
):
    fixture = _seed_domain_weaver_wave2_implementation_preview_fixture(
        tmp_path,
        accept_scheduler_reissue=True,
    )
    preview_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_wave2_bounded_implementation_preview",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-BOUNDED-IMPLEMENTATION-SOURCE-PATCH-CANDIDATE-20260601",
        },
    )
    assert preview_result["ok"] is True

    movement_request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_wave2_candidate_source_patch_accepted_state_movement_20260601_attempt_001.json"
    )
    movement_request_id = "codex_req_domain_weaver_wave2_candidate_source_patch_accepted_state_movement_20260601_attempt_001"
    movement_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "2026-06-01T180000Z_accepted_state_movement_return.json"
    )
    movement_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "fake_accepted_state_movement/task_return_body.md"
    )
    _write(
        tmp_path,
        movement_body_rel,
        (
            "### ACCEPTED STATE MOVEMENT VERDICT\n"
            "verdict: NO_OP_BLOCKED_MISSING_EXPLICIT_ACCEPTED_STATE_MOVEMENT_AUTHORITY_RECEIPT\n"
        ),
    )
    _write(
        tmp_path,
        movement_request_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": movement_request_id,
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "latest_return_packet_path": movement_return_rel,
                "return_packet_paths": [movement_return_rel],
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
                "domain_weaver_wave2_candidate_source_patch_accepted_state_movement": {
                    "source_patch_return_path": fixture["source_patch_return_rel"],
                    "source_patch_settlement_return_path": (
                        "ION/05_context/current/chatgpt_connector/task_returns/"
                        "2026-06-01T171000Z_source_patch_settlement_return.json"
                    ),
                    "readiness_gate_return_path": (
                        "ION/05_context/current/chatgpt_connector/task_returns/"
                        "2026-06-01T172000Z_readiness_gate_return.json"
                    ),
                    "accepted_state_settlement_gate_return_path": (
                        "ION/05_context/current/chatgpt_connector/task_returns/"
                        "2026-06-01T173000Z_accepted_state_settlement_gate_return.json"
                    ),
                    "preview_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_PREVIEW_PATH.as_posix(),
                    "rollback_matrix_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_ROLLBACK_MATRIX_PATH.as_posix(),
                    "approval_limits_schema_path": DOMAIN_WEAVER_WAVE2_APPROVAL_AND_LIMITS_LEDGER_SCHEMA_PATH.as_posix(),
                    "accepted_state_authority_receipt_required": True,
                    "expected_noop_without_authority_receipt": True,
                    "accepted_state_authority": False,
                    "accepted_state_mutation_authority": False,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        movement_return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [movement_body_rel],
                },
                "workload_diff_accepted": True,
                "work_request_id": movement_request_id,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/wave2_authority_receipt_repair_1",
                "pid": 9943,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave2_accepted_state_movement_authority_receipt_repair",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-ACCEPTED-STATE-MOVEMENT-AUTHORITY-RECEIPT-REPAIR-20260601",
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["movement_accepted"] is True
    assert result["summary"]["movement_verdict"] == (
        "NO_OP_BLOCKED_MISSING_EXPLICIT_ACCEPTED_STATE_MOVEMENT_AUTHORITY_RECEIPT"
    )
    assert result["summary"]["authority_receipt_repair_gate"] is True
    assert result["summary"]["operator_magic_string_required"] is False
    assert result["summary"]["expected_blocked_absent_receipt"] is True
    assert result["summary"]["accepted_state_authority"] is False
    assert result["summary"]["accepted_state_mutation_authority"] is False
    assert result["summary"]["worker_started_count"] == 1
    assert len(calls) == 1
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_WAVE2_AUTHORITY_RECEIPT_REPAIR_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert ledger["schema_id"] == (
        "ion.domain_weaver.wave2_accepted_state_movement_authority_receipt_repair_queue_ledger.v0_1_candidate"
    )
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    payload = request["domain_weaver_wave2_accepted_state_movement_authority_receipt_repair"]
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert payload["repair_gate_only"] is True
    assert payload["operator_magic_string_required"] is False
    assert payload["accepted_state_authority"] is False
    assert payload["accepted_state_mutation_authority"] is False
    assert payload["source_movement_return_path"] == movement_return_rel
    assert movement_body_rel in request["required_context_reads"]
    assert "without asking the operator for a magic string" in request["objective"]


def test_domain_weaver_wave2_authority_receipt_issuance_queues_no_magic_from_absent_repair(
    tmp_path: Path,
    monkeypatch,
):
    fixture = _seed_domain_weaver_wave2_implementation_preview_fixture(
        tmp_path,
        accept_scheduler_reissue=True,
    )
    preview_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_wave2_bounded_implementation_preview",
            "packet_id": "PCKT-DOMAIN-WEAVER-WAVE2-BOUNDED-IMPLEMENTATION-SOURCE-PATCH-CANDIDATE-20260601",
        },
    )
    assert preview_result["ok"] is True

    movement_request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_wave2_candidate_source_patch_accepted_state_movement_20260601_attempt_001.json"
    )
    movement_request_id = "codex_req_domain_weaver_wave2_candidate_source_patch_accepted_state_movement_20260601_attempt_001"
    movement_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "2026-06-01T180000Z_accepted_state_movement_return.json"
    )
    movement_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "fake_accepted_state_movement/task_return_body.md"
    )
    _write(
        tmp_path,
        movement_body_rel,
        (
            "### ACCEPTED STATE MOVEMENT VERDICT\n"
            "verdict: NO_OP_BLOCKED_MISSING_EXPLICIT_ACCEPTED_STATE_MOVEMENT_AUTHORITY_RECEIPT\n"
        ),
    )
    _write(
        tmp_path,
        movement_request_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": movement_request_id,
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "latest_return_packet_path": movement_return_rel,
                "return_packet_paths": [movement_return_rel],
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
                "domain_weaver_wave2_candidate_source_patch_accepted_state_movement": {
                    "source_patch_return_path": fixture["source_patch_return_rel"],
                    "source_patch_settlement_return_path": (
                        "ION/05_context/current/chatgpt_connector/task_returns/"
                        "2026-06-01T171000Z_source_patch_settlement_return.json"
                    ),
                    "readiness_gate_return_path": (
                        "ION/05_context/current/chatgpt_connector/task_returns/"
                        "2026-06-01T172000Z_readiness_gate_return.json"
                    ),
                    "accepted_state_settlement_gate_return_path": (
                        "ION/05_context/current/chatgpt_connector/task_returns/"
                        "2026-06-01T173000Z_accepted_state_settlement_gate_return.json"
                    ),
                    "preview_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_GATE_PREVIEW_PATH.as_posix(),
                    "rollback_matrix_path": DOMAIN_WEAVER_WAVE2_IMPLEMENTATION_ROLLBACK_MATRIX_PATH.as_posix(),
                    "approval_limits_schema_path": DOMAIN_WEAVER_WAVE2_APPROVAL_AND_LIMITS_LEDGER_SCHEMA_PATH.as_posix(),
                    "accepted_state_authority_receipt_required": True,
                    "expected_noop_without_authority_receipt": True,
                    "accepted_state_authority": False,
                    "accepted_state_mutation_authority": False,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        movement_return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [movement_body_rel],
                },
                "workload_diff_accepted": True,
                "work_request_id": movement_request_id,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    repair_request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_wave2_accepted_state_movement_authority_receipt_repair_"
        "20260601_attempt_001.json"
    )
    repair_request_id = (
        "codex_req_domain_weaver_wave2_accepted_state_movement_authority_receipt_repair_20260601_attempt_001"
    )
    repair_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "2026-06-01T182956Z_authority_receipt_repair_return.json"
    )
    repair_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "fake_authority_receipt_repair/task_return_body.md"
    )
    _write(
        tmp_path,
        repair_body_rel,
        "### AUTHORITY RECEIPT REPAIR VERDICT\nverdict: BLOCKED_AUTHORITY_RECEIPT_ABSENT\n",
    )
    _write(
        tmp_path,
        repair_request_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": repair_request_id,
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "latest_return_packet_path": repair_return_rel,
                "return_packet_paths": [repair_return_rel],
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
                "domain_weaver_wave2_accepted_state_movement_authority_receipt_repair": {
                    "source_movement_request_path": movement_request_rel,
                    "source_movement_return_path": movement_return_rel,
                    "source_movement_task_return_body_path": movement_body_rel,
                    "source_movement_verdict": (
                        "NO_OP_BLOCKED_MISSING_EXPLICIT_ACCEPTED_STATE_MOVEMENT_AUTHORITY_RECEIPT"
                    ),
                    "expected_blocked_absent_receipt": True,
                    "accepted_state_authority": False,
                    "accepted_state_mutation_authority": False,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        repair_return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [repair_body_rel],
                },
                "workload_diff_accepted": True,
                "work_request_id": repair_request_id,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": (
                    "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
                    "wave2_authority_receipt_issuance_1"
                ),
                "pid": 9944,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_wave2_explicit_accepted_state_movement_authority_receipt_issuance",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-WAVE2-EXPLICIT-ACCEPTED-STATE-MOVEMENT-AUTHORITY-RECEIPT-ISSUANCE-20260601"
            ),
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["movement_accepted"] is True
    assert result["summary"]["authority_receipt_repair_accepted"] is True
    assert result["summary"]["authority_receipt_repair_verdict"] == "BLOCKED_AUTHORITY_RECEIPT_ABSENT"
    assert result["summary"]["authority_receipt_issuance_gate"] is True
    assert result["summary"]["operator_magic_string_required"] is False
    assert result["summary"]["accepted_state_write_authority"] is False
    assert result["summary"]["accepted_state_mutation_authority"] is False
    assert result["summary"]["worker_started_count"] == 1
    assert len(calls) == 1
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_WAVE2_AUTHORITY_RECEIPT_ISSUANCE_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert ledger["schema_id"] == (
        "ion.domain_weaver.wave2_explicit_accepted_state_movement_authority_receipt_issuance_queue_ledger.v0_1_candidate"
    )
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    payload = request["domain_weaver_wave2_explicit_accepted_state_movement_authority_receipt_issuance"]
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert payload["accepted_state_receipt_issuance_gate"] is True
    assert payload["operator_magic_string_required"] is False
    assert payload["may_issue_single_use_receipt"] is True
    assert payload["accepted_state_write_authority"] is False
    assert payload["accepted_state_mutation_authority"] is False
    assert payload["source_repair_return_path"] == repair_return_rel
    assert payload["source_movement_return_path"] == movement_return_rel
    assert repair_body_rel in request["required_context_reads"]
    assert movement_body_rel in request["required_context_reads"]
    assert "Do not ask the operator for a magic string" in request["objective"]


def test_domain_weaver_policy_governed_refresh_does_not_require_magic_confirmation(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "refresh_queue_governor",
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["required_confirmation"] == "policy_governed_no_magic_operator_string"


def test_domain_weaver_policy_governed_actions_still_block_high_risk_authority(tmp_path: Path):
    _seed_root(tmp_path)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "refresh_queue_governor",
            "production_authority": True,
        },
    )

    assert result["ok"] is False
    assert result["finding"] == "high_risk_authority_requires_explicit_gate"
    assert result["high_risk_authority_requests"] == ["production_authority"]


def test_domain_weaver_materialization_emits_activation_plane_candidate_schemas(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    result = materialize_domain_weaver_projection(tmp_path)

    assert result["ok"] is True
    assert (tmp_path / DOMAIN_WEAVER_FOUNDING_ASSEMBLY_PATH).is_file()
    request_path = tmp_path / DOMAIN_WEAVER_ACTIVATION_REQUEST_SCHEMA_PATH
    decision_path = tmp_path / DOMAIN_WEAVER_ACTIVATION_DECISION_SCHEMA_PATH
    ledger_path = tmp_path / DOMAIN_WEAVER_ACTIVATION_LEDGER_PATH
    fission_path = tmp_path / DOMAIN_WEAVER_FISSION_DRYRUN_PROPOSAL_PATH
    topology_audit_path = tmp_path / DOMAIN_WEAVER_TOPOLOGY_AUDIT_PATH
    topology_control_policy_path = tmp_path / DOMAIN_WEAVER_TOPOLOGY_CONTROL_POLICY_PATH
    fission_template_library_path = tmp_path / DOMAIN_WEAVER_FISSION_TEMPLATE_LIBRARY_PATH
    dynamic_swarm_plan_path = tmp_path / DOMAIN_WEAVER_DYNAMIC_SWARM_OPERATION_PLAN_PATH
    settlement_path = tmp_path / DOMAIN_WEAVER_FANOUT_FANIN_SETTLEMENT_PATH
    approval_policy_path = tmp_path / DOMAIN_WEAVER_APPROVAL_GOVERNOR_POLICY_PATH
    approval_ledger_path = tmp_path / DOMAIN_WEAVER_APPROVAL_DECISION_LEDGER_PATH
    live_binding_path = tmp_path / DOMAIN_WEAVER_LIVE_CARRIER_BINDING_PLAN_PATH
    live_return_monitor_path = tmp_path / DOMAIN_WEAVER_LIVE_RETURN_MONITOR_PATH
    live_fanin_settlement_path = tmp_path / DOMAIN_WEAVER_LIVE_FANIN_SETTLEMENT_PATH
    live_fanin_semantic_settlement_path = tmp_path / DOMAIN_WEAVER_LIVE_FANIN_SEMANTIC_SETTLEMENT_PATH
    live_fanin_semantic_repin_plan_path = tmp_path / DOMAIN_WEAVER_LIVE_FANIN_SEMANTIC_REPIN_PLAN_PATH
    assert request_path.is_file()
    assert decision_path.is_file()
    assert ledger_path.is_file()
    assert fission_path.is_file()
    assert topology_audit_path.is_file()
    assert topology_control_policy_path.is_file()
    assert fission_template_library_path.is_file()
    assert dynamic_swarm_plan_path.is_file()
    assert settlement_path.is_file()
    assert approval_policy_path.is_file()
    assert approval_ledger_path.is_file()
    assert live_binding_path.is_file()
    assert live_return_monitor_path.is_file()
    assert live_fanin_settlement_path.is_file()
    assert live_fanin_semantic_settlement_path.is_file()
    assert live_fanin_semantic_repin_plan_path.is_file()
    request_schema = json.loads(request_path.read_text(encoding="utf-8"))
    decision_schema = json.loads(decision_path.read_text(encoding="utf-8"))
    activation_ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    fission_proposal = json.loads(fission_path.read_text(encoding="utf-8"))
    topology_audit = json.loads(topology_audit_path.read_text(encoding="utf-8"))
    topology_control_policy = json.loads(topology_control_policy_path.read_text(encoding="utf-8"))
    fission_template_library = json.loads(fission_template_library_path.read_text(encoding="utf-8"))
    dynamic_swarm_plan = json.loads(dynamic_swarm_plan_path.read_text(encoding="utf-8"))
    settlement_dryrun = json.loads(settlement_path.read_text(encoding="utf-8"))
    approval_policy = json.loads(approval_policy_path.read_text(encoding="utf-8"))
    approval_ledger = json.loads(approval_ledger_path.read_text(encoding="utf-8"))
    live_binding = json.loads(live_binding_path.read_text(encoding="utf-8"))
    live_return_monitor = json.loads(live_return_monitor_path.read_text(encoding="utf-8"))
    live_fanin_settlement = json.loads(live_fanin_settlement_path.read_text(encoding="utf-8"))
    live_fanin_semantic_settlement = json.loads(
        live_fanin_semantic_settlement_path.read_text(encoding="utf-8")
    )
    live_fanin_semantic_repin_plan = json.loads(
        live_fanin_semantic_repin_plan_path.read_text(encoding="utf-8")
    )
    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    assert request_schema["schema_id"] == "ion.domain_weaver.agent_activation_request.schema.v0_1_candidate"
    assert "requested_agent" in request_schema["required"]
    assert decision_schema["schema_id"] == "ion.domain_weaver.agent_activation_decision.schema.v0_1_candidate"
    assert "activate_now" in decision_schema["properties"]["decision"]["enum"]
    assert activation_ledger["schema_id"] == "ion.domain_weaver.activation_ledger.v0_1_candidate"
    assert activation_ledger["summary"]["activation_request_count"] > 0
    assert fission_proposal["schema_id"] == "ion.domain_weaver.domain_fission_dryrun.v0_1_candidate"
    assert fission_proposal["dry_run_ready"] is True
    assert topology_audit["schema_id"] == "ion.domain_weaver.topology_audit.v0_1_candidate"
    assert topology_audit["topology_audit_ready"] is True
    assert topology_audit["relationship_matrix"]["weighted_edge_count"] > 0
    assert topology_audit["summary"]["adaptive_control_policy_ready"] is True
    assert topology_audit["summary"]["fixed_domain_count_target"] is False
    assert topology_audit["summary"]["fixed_specialist_binding_limit"] is False
    assert topology_audit["summary"]["operator_parallelism_reference_is_target"] is False
    assert topology_audit["summary"]["selected_adaptive_coupling_threshold"] > 0
    assert topology_audit["summary"]["selected_adaptive_specialist_binding_budget"] > 0
    assert topology_audit["summary"]["breached_domain_count"] > 0
    assert topology_audit["summary"]["selected_domain_id"]
    assert topology_audit["summary"]["selected_template_id"] in {
        "surface_bucket_split_v1",
        "specialist_binding_recursion_v1",
        "context_ref_decoupling_v1",
        "relationship_matrix_decoupling_v1",
    }
    assert topology_audit["gates"]["pre_fission_integrity_gate"]["passed"] is True
    assert topology_audit["gates"]["authority_gate"]["passed"] is True
    assert topology_audit["gates"]["authority_gate"]["adaptive_specialist_binding_budget"] > 0
    assert topology_audit["gates"]["auto_fission_governance"]["worker_start_authority"] is False
    assert topology_audit["gates"]["auto_fission_governance"]["accepted_state_authority"] is False
    assert topology_control_policy["schema_id"] == "ion.domain_weaver.topology_adaptive_control_policy.v0_1_candidate"
    assert topology_control_policy["summary"]["adaptive_controls_ready"] is True
    assert topology_control_policy["summary"]["fixed_domain_count_target"] is False
    assert topology_control_policy["summary"]["fixed_specialist_binding_limit"] is False
    assert fission_template_library["schema_id"] == "ion.domain_weaver.fission_template_library.v0_1_candidate"
    assert {row["template_id"] for row in fission_template_library["templates"]} >= {
        "surface_bucket_split_v1",
        "specialist_binding_recursion_v1",
        "context_ref_decoupling_v1",
    }
    assert dynamic_swarm_plan["schema_id"] == "ion.domain_weaver.dynamic_swarm_operation_plan.v0_1_candidate"
    assert dynamic_swarm_plan["summary"]["dynamic_swarm_plan_ready"] is True
    assert dynamic_swarm_plan["summary"]["primary_mission"] == (
        "ion_vnext_production_spec_with_production_grade_domain_weaver_integration"
    )
    assert dynamic_swarm_plan["summary"]["fixed_domain_count_target"] is False
    assert dynamic_swarm_plan["summary"]["vnext_productization_lane_count"] > 0
    assert any(
        lane["domain_id"] == "domain.ion_vnext_domain_weaver_integration"
        for lane in dynamic_swarm_plan["candidate_lanes"]
    )
    assert settlement_dryrun["schema_id"] == "ion.domain_weaver.fanout_fanin_settlement_dryrun.v0_1_candidate"
    assert settlement_dryrun["dry_run_ready"] is True
    assert settlement_dryrun["summary"]["fanout_count"] > 0
    assert approval_policy["schema_id"] == "ion.domain_weaver.live_execution_approval_governor_policy.v0_1_candidate"
    assert approval_policy["budgets"]["max_chain_sequence_depth"] == 8
    assert approval_policy["budgets"]["max_estimated_tokens_per_chain"] == 240000
    assert approval_ledger["schema_id"] == "ion.domain_weaver.live_execution_approval_decision_ledger.v0_1_candidate"
    assert approval_ledger["summary"]["decision_count"] == settlement_dryrun["summary"]["fanout_count"]
    assert approval_ledger["summary"]["worker_started_count"] == 0
    assert live_binding["schema_id"] == "ion.domain_weaver.live_carrier_binding_plan.v0_1_candidate"
    assert live_binding["summary"]["queue_binding_plan_ready"] is True
    assert live_binding["summary"]["work_request_template_count"] == approval_ledger["summary"]["semi_auto_approved_count"]
    assert live_binding["summary"]["queued_request_count"] == 0
    assert live_return_monitor["schema_id"] == "ion.domain_weaver.live_return_monitor.v0_1_candidate"
    assert live_return_monitor["live_return_monitor_ready"] is True
    assert live_return_monitor["summary"]["expected_return_count"] == live_binding["summary"]["work_request_template_count"]
    assert live_return_monitor["summary"]["accepted_return_count"] == 0
    assert live_return_monitor["summary"]["return_complete"] is False
    assert live_fanin_settlement["schema_id"] == "ion.domain_weaver.live_fanin_settlement.v0_1_candidate"
    assert live_fanin_settlement["summary"]["live_fanin_settlement_ready"] is True
    assert live_fanin_settlement["summary"]["settlement_complete"] is False
    assert live_fanin_settlement["summary"]["missing_return_count"] == live_return_monitor["summary"]["expected_return_count"]
    assert (
        live_fanin_semantic_settlement["schema_id"]
        == "ion.domain_weaver.live_fanin_semantic_settlement.v0_1_candidate"
    )
    assert live_fanin_semantic_settlement["summary"]["semantic_settlement_ready"] is True
    assert live_fanin_semantic_settlement["summary"]["semantic_settlement_complete"] is False
    assert (
        live_fanin_semantic_repin_plan["schema_id"]
        == "ion.domain_weaver.live_fanin_semantic_repin_plan.v0_1_candidate"
    )
    assert live_fanin_semantic_repin_plan["summary"]["semantic_repin_plan_ready"] is True
    assert live_fanin_semantic_repin_plan["summary"]["repin_record_count"] == 0
    assert projection["activation_plane"]["summary"]["schema_ready_count"] == 3
    assert projection["activation_plane"]["summary"]["activation_records_ready"] is True
    assert projection["activation_plane"]["summary"]["activation_decision_store_ready"] is True
    assert projection["activation_plane"]["activation_plane_ready"] is False
    assert projection["fission_dryrun"]["dry_run_ready"] is True
    assert projection["topology_audit"]["topology_audit_ready"] is True
    assert projection["summary"]["topology_audit_ready"] is True
    assert projection["summary"]["topology_adaptive_control_policy_ready"] is True
    assert projection["summary"]["topology_fixed_domain_count_target"] is False
    assert projection["summary"]["topology_fixed_specialist_binding_limit"] is False
    assert projection["summary"]["topology_breached_domain_count"] > 0
    assert projection["summary"]["topology_candidate_auto_dispatch_ready"] is True
    assert projection["dynamic_swarm_operation_plan"]["summary"]["dynamic_swarm_plan_ready"] is True
    assert projection["summary"]["dynamic_swarm_plan_ready"] is True
    assert projection["summary"]["dynamic_swarm_primary_mission"] == (
        "ion_vnext_production_spec_with_production_grade_domain_weaver_integration"
    )
    assert projection["summary"]["dynamic_swarm_fixed_domain_count_target"] is False
    assert projection["summary"]["dynamic_swarm_vnext_productization_lane_count"] > 0
    assert projection["settlement_dryrun"]["dry_run_ready"] is True
    assert projection["approval_governor"]["semi_autonomous_approval_ready"] is True
    assert projection["approval_governor"]["summary"]["live_execution_carrier_binding_ready"] is False
    assert (
        projection["live_carrier_binding"]["summary"]["work_request_template_count"]
        == approval_ledger["summary"]["semi_auto_approved_count"]
    )
    assert projection["live_return_monitor"]["summary"]["live_return_monitor_ready"] is True
    assert projection["live_fanin_settlement"]["summary"]["live_fanin_settlement_ready"] is True
    assert projection["live_fanin_semantic_settlement"]["summary"]["semantic_settlement_ready"] is True
    assert projection["live_fanin_semantic_repin_plan"]["summary"]["semantic_repin_plan_ready"] is True
    assert projection["summary"]["live_return_monitor_ready"] is True
    assert projection["summary"]["live_fanin_settlement_ready"] is True
    assert projection["summary"]["live_fanin_semantic_settlement_ready"] is True
    assert projection["summary"]["live_fanin_semantic_repin_plan_ready"] is True
    assert projection["summary"]["current_capability_class"] == "approval_governed_live_queue_plan_ready"


def test_domain_weaver_materializes_dynamic_swarm_candidate_work_requests(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    materialize_domain_weaver_projection(tmp_path)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_dynamic_swarm_candidate_work_requests",
        },
    )

    assert result["ok"] is True
    assert result["required_confirmation"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["dynamic_swarm_plan_ready"] is True
    assert result["summary"]["fixed_domain_count_target"] is False
    assert result["summary"]["fixed_specialist_binding_limit"] is False
    assert result["summary"]["operator_parallelism_reference_is_target"] is False
    assert result["summary"]["worker_started_count"] == 0
    assert result["summary"]["worker_start_status"] == "not_started_queue_only_default"
    assert result["summary"]["queue_ledger_path"] == DOMAIN_WEAVER_DYNAMIC_SWARM_CANDIDATE_QUEUE_LEDGER_PATH.as_posix()
    plan = json.loads((tmp_path / DOMAIN_WEAVER_DYNAMIC_SWARM_OPERATION_PLAN_PATH).read_text(encoding="utf-8"))
    assert result["summary"]["candidate_lane_count"] == len(plan["candidate_lanes"])
    assert result["summary"]["queued_request_count"] == len(plan["candidate_lanes"])
    assert result["summary"]["vnext_productization_lane_count"] > 0

    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_DYNAMIC_SWARM_CANDIDATE_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    assert ledger["schema_id"] == "ion.domain_weaver.dynamic_swarm_candidate_queue_ledger.v0_1_candidate"
    assert ledger["summary"]["queued_request_count"] == len(plan["candidate_lanes"])
    assert ledger["summary"]["worker_started_count"] == 0
    assert ledger["authority"]["candidate_queue_binding_only"] is True
    assert ledger["authority"]["production_authority"] is False
    assert ledger["authority"]["live_execution_authority"] is False
    assert ledger["authority"]["accepted_state_authority"] is False

    request_payloads = [
        json.loads((tmp_path / row["packet_path"]).read_text(encoding="utf-8"))
        for row in ledger["queued_requests"]
    ]
    assert {
        payload["domain_weaver_dynamic_swarm_candidate_lane"]["lane_ordinal"]
        for payload in request_payloads
    } == {lane["ordinal"] for lane in plan["candidate_lanes"]}
    assert any(
        payload["domain_weaver_dynamic_swarm_candidate_lane"]["domain_id"]
        == "domain.ion_vnext_domain_weaver_integration"
        for payload in request_payloads
    )
    lane_ids_by_domain = {
        payload["domain_weaver_dynamic_swarm_candidate_lane"]["domain_id"]: payload["lane_id"]
        for payload in request_payloads
    }
    if "domain.construction_routing_integration" in lane_ids_by_domain:
        assert lane_ids_by_domain["domain.construction_routing_integration"] == "implementation_lane"
    if "domain.confidence_drift_review" in lane_ids_by_domain:
        assert lane_ids_by_domain["domain.confidence_drift_review"] == "audit_lane"
    if "domain.ion_vnext_canon_control_surface" in lane_ids_by_domain:
        assert lane_ids_by_domain["domain.ion_vnext_canon_control_surface"] == "context_lane"
    if "domain.ion_vnext_domain_weaver_integration" in lane_ids_by_domain:
        assert lane_ids_by_domain["domain.ion_vnext_domain_weaver_integration"] == "implementation_lane"
    if "domain.ion_vnext_release_cutover" in lane_ids_by_domain:
        assert lane_ids_by_domain["domain.ion_vnext_release_cutover"] == "maintenance_lane"
    assert len(set(lane_ids_by_domain.values())) >= 3
    for payload in request_payloads:
        lane_payload = payload["domain_weaver_dynamic_swarm_candidate_lane"]
        assert payload["requested_model"] == "gpt-5.5"
        assert payload["requested_reasoning_effort"] == "xhigh"
        assert payload["requested_service_tier"] == "fast"
        assert payload["codex_service_tier"] == "fast"
        assert payload["codex_model_override"]["selected_model"] == "gpt-5.5"
        assert payload["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
        assert payload["codex_model_override"]["service_tier"] == "fast"
        assert payload["requested_authority"]["source_edit_authority"] is False
        assert payload["requested_authority"]["production_authority"] is False
        assert payload["requested_authority"]["live_execution_authority"] is False
        assert payload["requested_authority"]["accepted_state_claim"] is False
        assert lane_payload["worker_start_authority"] is False
        assert lane_payload["requested_service_tier"] == "fast"
        assert lane_payload["fixed_domain_count_target"] is False
        assert lane_payload["operator_parallelism_reference_is_target"] is False
        assert "do_not_replace_adaptive_sizing_with_fixed_worker_count" in lane_payload["forbidden_actions"]
        assert DOMAIN_WEAVER_DYNAMIC_SWARM_OPERATION_PLAN_PATH.as_posix() in payload["required_context_reads"]
        assert "ION_VNEXT/01_canon/QUALITY_STANDARD.yaml" in payload["required_context_reads"]


def test_domain_weaver_dynamic_swarm_materialization_rejects_worker_start(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_dynamic_swarm_candidate_work_requests",
            "start_workers": True,
            "live_execution_confirmation": "ION_DOMAIN_WEAVER_LIVE_EXECUTION_CONFIRMED",
        },
    )

    assert result["ok"] is False
    assert result["summary"]["blocked_reason"] == "materialization_gate_does_not_start_workers"
    assert result["summary"]["required_next_gate"] == "start_only_queue_governor_allowed_window"
    assert result["summary"]["worker_started_count"] == 0


def test_domain_weaver_dynamic_swarm_fast_tier_repair_does_not_rewrite_terminal_requests(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_dynamic_swarm_candidate_work_requests",
        },
    )
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_DYNAMIC_SWARM_CANDIDATE_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    accepted_rel = ledger["queued_requests"][0]["packet_path"]
    queued_rel = ledger["queued_requests"][1]["packet_path"]
    accepted_path = tmp_path / accepted_rel
    queued_path = tmp_path / queued_rel
    accepted_payload = json.loads(accepted_path.read_text(encoding="utf-8"))
    queued_payload = json.loads(queued_path.read_text(encoding="utf-8"))
    for payload in (accepted_payload, queued_payload):
        payload.pop("requested_service_tier", None)
        payload.pop("codex_service_tier", None)
        payload["codex_model_override"].pop("service_tier", None)
        payload["domain_weaver_dynamic_swarm_candidate_lane"].pop("requested_service_tier", None)
    accepted_payload["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    accepted_path.write_text(json.dumps(accepted_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    queued_path.write_text(json.dumps(queued_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_dynamic_swarm_candidate_work_requests",
        },
    )

    assert result["ok"] is True
    accepted_after = json.loads(accepted_path.read_text(encoding="utf-8"))
    queued_after = json.loads(queued_path.read_text(encoding="utf-8"))
    assert "requested_service_tier" not in accepted_after
    assert "codex_service_tier" not in accepted_after
    assert "service_tier" not in accepted_after["codex_model_override"]
    assert "requested_service_tier" not in accepted_after["domain_weaver_dynamic_swarm_candidate_lane"]
    assert queued_after["requested_service_tier"] == "fast"
    assert queued_after["codex_service_tier"] == "fast"
    assert queued_after["codex_model_override"]["service_tier"] == "fast"
    assert queued_after["domain_weaver_dynamic_swarm_candidate_lane"]["requested_service_tier"] == "fast"


def test_domain_weaver_reconciles_dynamic_swarm_fresh_context_return_monitor(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_dynamic_swarm_candidate_work_requests",
        },
    )
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_DYNAMIC_SWARM_CANDIDATE_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    first_request_path = tmp_path / ledger["queued_requests"][0]["packet_path"]
    first_request = json.loads(first_request_path.read_text(encoding="utf-8"))
    first_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    first_request["return_packet_paths"] = [
        "ION/05_context/current/chatgpt_connector/task_returns/test_dynamic_swarm_lane_01_task_return.json"
    ]
    first_request["latest_return_packet_path"] = first_request["return_packet_paths"][0]
    first_request_path.write_text(json.dumps(first_request, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "reconcile_dynamic_swarm_fresh_context_return_monitor_stranded_runs",
        },
    )

    assert result["ok"] is True
    assert result["summary"]["reconciliation_path"] == (
        DOMAIN_WEAVER_DYNAMIC_SWARM_FRESH_CONTEXT_RECONCILIATION_PATH.as_posix()
    )
    assert result["summary"]["expected_lane_count"] == len(ledger["queued_requests"])
    assert result["summary"]["accepted_return_count"] == 1
    assert result["summary"]["queueable_start_request_count"] == len(ledger["queued_requests"]) - 1
    assert result["summary"]["running_lane_count"] == 0
    assert result["summary"]["stranded_lane_count"] == 0
    assert result["summary"]["queued_fast_service_tier_ready_count"] == len(ledger["queued_requests"]) - 1
    assert result["summary"]["next_lawful_action"] == "start_dynamic_swarm_candidate_workers"
    assert result["summary"]["worker_started_count"] == 0
    assert result["summary"]["live_execution_authority"] is False
    artifact = json.loads(
        (tmp_path / DOMAIN_WEAVER_DYNAMIC_SWARM_FRESH_CONTEXT_RECONCILIATION_PATH).read_text(encoding="utf-8")
    )
    assert artifact["summary"]["all_lanes_resolved_for_fanin"] is False
    assert artifact["lane_records"][0]["lane_state"] == "accepted"
    assert artifact["lane_records"][1]["lane_state"] == "queueable"
    assert artifact["lane_records"][1]["queued_fast_service_tier_ready"] is True


def test_domain_weaver_queues_dynamic_swarm_fanin_reissue_after_all_lanes_accepted(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_dynamic_swarm_candidate_work_requests",
        },
    )
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_DYNAMIC_SWARM_CANDIDATE_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    for index, row in enumerate(ledger["queued_requests"], start=1):
        request_path = tmp_path / row["packet_path"]
        request = json.loads(request_path.read_text(encoding="utf-8"))
        request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        request["return_packet_paths"] = [
            f"ION/05_context/current/chatgpt_connector/task_returns/test_dynamic_swarm_lane_{index:02d}_task_return.json"
        ]
        request["latest_return_packet_path"] = request["return_packet_paths"][0]
        request_path.write_text(json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_dynamic_swarm_fanin_settlement_reissue",
        },
    )

    assert result["ok"] is True
    assert result["summary"]["all_lanes_resolved_for_fanin"] is True
    assert result["summary"]["accepted_return_count"] == len(ledger["queued_requests"])
    assert result["summary"]["queue_ledger_path"] == DOMAIN_WEAVER_DYNAMIC_SWARM_FANIN_REISSUE_QUEUE_LEDGER_PATH.as_posix()
    assert result["summary"]["queued_request_count"] == 1
    assert result["summary"]["worker_started_count"] == 0
    fanin_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_DYNAMIC_SWARM_FANIN_REISSUE_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    fanin_request = json.loads((tmp_path / fanin_ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8"))
    assert fanin_request["lane_id"] == "settlement_lane"
    assert fanin_request["requested_service_tier"] == "fast"
    assert fanin_request["domain_weaver_dynamic_swarm_fanin_reissue"]["all_lanes_resolved_for_fanin"] is True


def test_domain_weaver_queues_dynamic_swarm_semantic_blocker_readiness_gate_after_fanin(
    tmp_path: Path,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_dynamic_swarm_candidate_work_requests",
        },
    )
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_DYNAMIC_SWARM_CANDIDATE_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    for index, row in enumerate(ledger["queued_requests"], start=1):
        request_path = tmp_path / row["packet_path"]
        request = json.loads(request_path.read_text(encoding="utf-8"))
        request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        request["return_packet_paths"] = [
            f"ION/05_context/current/chatgpt_connector/task_returns/test_dynamic_swarm_lane_{index:02d}_task_return.json"
        ]
        request["latest_return_packet_path"] = request["return_packet_paths"][0]
        request_path.write_text(json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    fanin_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_dynamic_swarm_fanin_settlement_reissue",
        },
    )
    assert fanin_queue["ok"] is True
    fanin_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_DYNAMIC_SWARM_FANIN_REISSUE_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    fanin_request_path = tmp_path / fanin_ledger["queued_requests"][0]["packet_path"]
    fanin_request = json.loads(fanin_request_path.read_text(encoding="utf-8"))
    fanin_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"test_{fanin_request['request_id']}/task_return_body.md"
    )
    fanin_run_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"test_{fanin_request['request_id']}/run.json"
    )
    fanin_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"test_{fanin_request['request_id']}_accepted_return.json"
    )
    fanin_machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"test_{fanin_request['request_id']}_machine_receipt.json"
    )
    _write(
        tmp_path,
        fanin_body_rel,
        "### SEMANTIC SETTLEMENT\n"
        "settlement_verdict: CANDIDATE_FANIN_EVIDENCE_SETTLED_WITH_PRODUCTION_SPEC_AND_DOMAIN_EVOLUTION_BLOCKERS\n"
        "### RECOMMENDED NEXT PACKET\n"
        f"packet_id: {DOMAIN_WEAVER_DYNAMIC_SWARM_SEMANTIC_BLOCKER_READINESS_PACKET_ID}\n"
        "### RESULT\n",
    )
    _write(
        tmp_path,
        fanin_run_rel,
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_run.v1",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "request_id": fanin_request["request_id"],
                "request_path": fanin_request["packet_path"],
                "task_return_body_path": fanin_body_rel,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        fanin_machine_rel,
        json.dumps({"accepted_for_carrier_intake": True}, indent=2) + "\n",
    )
    _write(
        tmp_path,
        fanin_return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": fanin_machine_rel,
                "template_action_proof_result": {"touched_paths": [fanin_body_rel]},
            },
            indent=2,
        )
        + "\n",
    )
    fanin_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    fanin_request["latest_return_packet_path"] = fanin_return_rel
    fanin_request["latest_task_return_machine_receipt_path"] = fanin_machine_rel
    fanin_request["return_packet_paths"] = [fanin_return_rel]
    fanin_request_path.write_text(json.dumps(fanin_request, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_dynamic_swarm_semantic_blocker_resolution_readiness_gate",
            "packet_id": DOMAIN_WEAVER_DYNAMIC_SWARM_SEMANTIC_BLOCKER_READINESS_PACKET_ID,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["packet_id"] == DOMAIN_WEAVER_DYNAMIC_SWARM_SEMANTIC_BLOCKER_READINESS_PACKET_ID
    assert result["summary"]["fanin_readiness_gate_ready"] is True
    assert result["summary"]["queued_request_count"] == 1
    assert result["summary"]["worker_started_count"] == 0
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_DYNAMIC_SWARM_SEMANTIC_BLOCKER_READINESS_QUEUE_LEDGER_PATH.as_posix()
    )
    readiness_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_DYNAMIC_SWARM_SEMANTIC_BLOCKER_READINESS_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    readiness_request = json.loads(
        (tmp_path / readiness_ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8")
    )
    assert readiness_request["request_kind"] == (
        "domain_weaver_dynamic_swarm_semantic_blocker_resolution_and_production_spec_readiness_gate"
    )
    assert readiness_request["lane_id"] == "settlement_lane"
    assert readiness_request["requested_model"] == "gpt-5.5"
    assert readiness_request["requested_reasoning_effort"] == "xhigh"
    assert readiness_request["requested_service_tier"] == "fast"
    assert readiness_request["requested_authority"]["source_edit_authority"] is False
    assert readiness_request["requested_authority"]["production_authority"] is False
    assert readiness_request["requested_authority"]["live_execution_authority"] is False
    assert readiness_request["requested_authority"]["accepted_state_claim"] is False
    assert fanin_body_rel in readiness_request["required_context_reads"]
    assert fanin_return_rel in readiness_request["required_context_reads"]
    assert readiness_request["domain_weaver_dynamic_swarm_semantic_blocker_readiness_gate"][
        "source_fanin_task_return_body_path"
    ] == fanin_body_rel
    assert readiness_request["domain_weaver_dynamic_swarm_semantic_blocker_readiness_gate"][
        "required_verdict"
    ] == "semantic_blocker_resolution_and_production_spec_readiness_gate_or_explicit_blocker"


def test_domain_weaver_queues_dynamic_swarm_context_duplicate_lifecycle_gate_after_readiness(
    tmp_path: Path,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_dynamic_swarm_candidate_work_requests",
        },
    )
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_DYNAMIC_SWARM_CANDIDATE_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    for index, row in enumerate(ledger["queued_requests"], start=1):
        request_path = tmp_path / row["packet_path"]
        request = json.loads(request_path.read_text(encoding="utf-8"))
        request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        request["return_packet_paths"] = [
            f"ION/05_context/current/chatgpt_connector/task_returns/test_dynamic_swarm_lane_{index:02d}_task_return.json"
        ]
        request["latest_return_packet_path"] = request["return_packet_paths"][0]
        request_path.write_text(json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    readiness_request_id = "codex_req_domain_weaver_dynamic_swarm_semantic_blocker_readiness_gate_20260602_attempt_001"
    readiness_request_rel = f"ION/05_context/current/chatgpt_connector/codex_work_requests/{readiness_request_id}.json"
    readiness_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"test_{readiness_request_id}/task_return_body.md"
    )
    readiness_run_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"test_{readiness_request_id}/run.json"
    )
    readiness_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"test_{readiness_request_id}_accepted_return.json"
    )
    readiness_machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"test_{readiness_request_id}_machine_receipt.json"
    )
    _write(
        tmp_path,
        readiness_request_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": readiness_request_id,
                "packet_path": readiness_request_rel,
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "latest_return_packet_path": readiness_return_rel,
                "latest_task_return_machine_receipt_path": readiness_machine_rel,
                "return_packet_paths": [readiness_return_rel],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        readiness_body_rel,
        "### RESULT\n"
        "Exact lawful next work is candidate-only context/duplicate lineage classification before any stronger packet.\n"
        "### RECOMMENDED NEXT PACKET\n"
        f"packet_id: {DOMAIN_WEAVER_DYNAMIC_SWARM_CONTEXT_DUPLICATE_LIFECYCLE_PACKET_ID}\n",
    )
    _write(
        tmp_path,
        readiness_run_rel,
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_run.v1",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "request_id": readiness_request_id,
                "request_path": readiness_request_rel,
                "task_return_body_path": readiness_body_rel,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        readiness_machine_rel,
        json.dumps({"accepted_for_carrier_intake": True}, indent=2) + "\n",
    )
    _write(
        tmp_path,
        readiness_return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": readiness_machine_rel,
                "template_action_proof_result": {"touched_paths": [readiness_body_rel]},
            },
            indent=2,
        )
        + "\n",
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_dynamic_swarm_context_duplicate_lineage_lifecycle_gate",
            "packet_id": DOMAIN_WEAVER_DYNAMIC_SWARM_CONTEXT_DUPLICATE_LIFECYCLE_PACKET_ID,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["packet_id"] == DOMAIN_WEAVER_DYNAMIC_SWARM_CONTEXT_DUPLICATE_LIFECYCLE_PACKET_ID
    assert result["summary"]["lifecycle_gate_ready"] is True
    assert result["summary"]["queued_request_count"] == 1
    assert result["summary"]["worker_started_count"] == 0
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_DYNAMIC_SWARM_CONTEXT_DUPLICATE_LIFECYCLE_QUEUE_LEDGER_PATH.as_posix()
    )
    lifecycle_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_DYNAMIC_SWARM_CONTEXT_DUPLICATE_LIFECYCLE_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    lifecycle_request = json.loads(
        (tmp_path / lifecycle_ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8")
    )
    assert lifecycle_request["request_kind"] == (
        "domain_weaver_dynamic_swarm_context_drift_duplicate_lineage_lifecycle_gate"
    )
    assert lifecycle_request["lane_id"] == "settlement_lane"
    assert lifecycle_request["requested_model"] == "gpt-5.5"
    assert lifecycle_request["requested_reasoning_effort"] == "xhigh"
    assert lifecycle_request["requested_service_tier"] == "fast"
    assert lifecycle_request["requested_authority"]["source_edit_authority"] is False
    assert lifecycle_request["requested_authority"]["production_authority"] is False
    assert lifecycle_request["requested_authority"]["live_execution_authority"] is False
    assert lifecycle_request["requested_authority"]["accepted_state_claim"] is False
    assert readiness_body_rel in lifecycle_request["required_context_reads"]
    assert readiness_return_rel in lifecycle_request["required_context_reads"]
    assert lifecycle_request["domain_weaver_dynamic_swarm_context_duplicate_lifecycle_gate"][
        "source_readiness_task_return_body_path"
    ] == readiness_body_rel
    assert lifecycle_request["domain_weaver_dynamic_swarm_context_duplicate_lifecycle_gate"][
        "required_verdict"
    ] == "context_duplicate_lifecycle_matrix_or_explicit_blocker"


def test_domain_weaver_materializes_dynamic_swarm_fresh_current_lifecycle_settlement(
    tmp_path: Path,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    lifecycle_request_id = "codex_req_domain_weaver_dynamic_swarm_context_duplicate_lifecycle_gate_20260602_attempt_001"
    lifecycle_request_rel = f"ION/05_context/current/chatgpt_connector/codex_work_requests/{lifecycle_request_id}.json"
    lifecycle_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"test_{lifecycle_request_id}/task_return_body.md"
    )
    lifecycle_run_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"test_{lifecycle_request_id}/run.json"
    )
    lifecycle_receipt_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"test_{lifecycle_request_id}/context_receipt.json"
    )
    lifecycle_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"test_{lifecycle_request_id}_accepted_return.json"
    )
    lifecycle_machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"test_{lifecycle_request_id}_machine_receipt.json"
    )
    lane_return_rels = [
        "ION/05_context/current/chatgpt_connector/task_returns/test_lifecycle_lane_01_old.json",
        "ION/05_context/current/chatgpt_connector/task_returns/test_lifecycle_lane_01_latest.json",
        "ION/05_context/current/chatgpt_connector/task_returns/test_lifecycle_lane_02_old_a.json",
        "ION/05_context/current/chatgpt_connector/task_returns/test_lifecycle_lane_02_old_b.json",
        "ION/05_context/current/chatgpt_connector/task_returns/test_lifecycle_lane_02_latest.json",
    ]
    for rel in lane_return_rels:
        _write(
            tmp_path,
            rel,
            json.dumps(
                {
                    "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                    "accepted_for_carrier_intake": True,
                },
                indent=2,
            )
            + "\n",
        )
    lifecycle_payload = {
        "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
        "request_id": lifecycle_request_id,
        "packet_path": lifecycle_request_rel,
        "status": "RETURN_RECORDED_PROOF_ACCEPTED",
        "latest_return_packet_path": lifecycle_return_rel,
        "latest_task_return_machine_receipt_path": lifecycle_machine_rel,
        "return_packet_paths": [lifecycle_return_rel],
        "required_context_reads": [*lane_return_rels],
        "domain_weaver_dynamic_swarm_context_duplicate_lifecycle_gate": {
            "expected_lane_count": 2,
            "duplicate_return_lane_count": 2,
            "context_hash_drift_lane_count": 2,
            "context_hash_drift_record_count": 4,
            "lane_records": [
                {
                    "lane_ordinal": 1,
                    "domain_id": "domain.one",
                    "latest_return_packet_path": lane_return_rels[1],
                    "return_packet_paths": lane_return_rels[:2],
                    "context_hash_drift_count": 2,
                },
                {
                    "lane_ordinal": 2,
                    "domain_id": "domain.two",
                    "latest_return_packet_path": lane_return_rels[4],
                    "return_packet_paths": lane_return_rels[2:],
                    "context_hash_drift_count": 2,
                },
            ],
        },
    }
    _write(tmp_path, lifecycle_request_rel, json.dumps(lifecycle_payload, indent=2, sort_keys=True) + "\n")
    _write(
        tmp_path,
        lifecycle_body_rel,
        "### RESULT\n"
        "Run the recommended fresh-current lifecycle settlement and control-plane drift reconciliation packet only.\n"
        "### RECOMMENDED NEXT PACKET\n"
        f"packet_id: {DOMAIN_WEAVER_DYNAMIC_SWARM_FRESH_CURRENT_LIFECYCLE_PACKET_ID}\n",
    )
    _write(
        tmp_path,
        lifecycle_receipt_rel,
        json.dumps(
            {
                "schema_id": "ion.context_receipt.v1",
                "required_context_reads": [
                    {"kind": "file", "path": lifecycle_request_rel, "sha256": ""},
                    {"kind": "file", "path": lifecycle_body_rel, "sha256": ""},
                    {"kind": "file", "path": lane_return_rels[1], "sha256": ""},
                    {"kind": "file", "path": lane_return_rels[4], "sha256": ""},
                ],
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        lifecycle_run_rel,
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_run.v1",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "request_id": lifecycle_request_id,
                "request_path": lifecycle_request_rel,
                "context_receipt_path": lifecycle_receipt_rel,
                "task_return_body_path": lifecycle_body_rel,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        lifecycle_machine_rel,
        json.dumps({"accepted_for_carrier_intake": True}, indent=2) + "\n",
    )
    _write(
        tmp_path,
        lifecycle_return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": lifecycle_machine_rel,
                "template_action_proof_result": {"touched_paths": [lifecycle_body_rel]},
            },
            indent=2,
        )
        + "\n",
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_dynamic_swarm_fresh_current_lifecycle_settlement",
        },
    )

    assert result["ok"] is True
    assert result["summary"]["fresh_current_settlement_ready"] is True
    assert result["summary"]["settlement_path"] == (
        DOMAIN_WEAVER_DYNAMIC_SWARM_FRESH_CURRENT_LIFECYCLE_SETTLEMENT_PATH.as_posix()
    )
    assert result["summary"]["selected_latest_binding_count"] == 2
    assert result["summary"]["duplicate_return_record_count"] == 3
    assert result["summary"]["next_lawful_action"] == "queue_topology_evolution_materialization_readiness_proof_gate"
    settlement = json.loads(
        (tmp_path / DOMAIN_WEAVER_DYNAMIC_SWARM_FRESH_CURRENT_LIFECYCLE_SETTLEMENT_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert settlement["packet_id"] == DOMAIN_WEAVER_DYNAMIC_SWARM_FRESH_CURRENT_LIFECYCLE_PACKET_ID
    assert settlement["inheritance_decision"]["candidate_evidence_binding_allowed"] is True
    assert settlement["inheritance_decision"]["duplicate_return_policy"] == (
        "preserve_all_duplicate_returns_as_lineage_evidence"
    )
    assert settlement["authority"]["production_authority"] is False
    assert settlement["authority"]["live_execution_authority"] is False


def test_domain_weaver_queues_topology_evolution_readiness_gate_from_fresh_settlement(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    topology_rows = [
        {
            "lane_ordinal": index,
            "domain_id": domain_id,
            "latest_return_packet_path": (
                f"ION/05_context/current/chatgpt_connector/task_returns/test_topology_lane_{index:02d}.json"
            ),
            "duplicate_return_count": 1,
            "context_hash_drift_count": 2,
        }
        for index, domain_id in enumerate(
            [
                "domain.continuity_context_resumability",
                "domain.current_phase_orchestration_management",
                "domain.archaeology_drift_watch",
                "domain.construction_routing_integration",
                "domain.confidence_drift_review",
            ],
            start=1,
        )
    ]
    fake_settlement = {
        "schema_id": "ion.domain_weaver.dynamic_swarm_fresh_current_lifecycle_settlement.v0_1_candidate",
        "summary": {
            "fresh_current_settlement_ready": True,
            "selected_latest_binding_count": 5,
        },
        "source_lifecycle_request_path": "ION/05_context/current/chatgpt_connector/codex_work_requests/test_lifecycle.json",
        "source_lifecycle_return_path": "ION/05_context/current/chatgpt_connector/task_returns/test_lifecycle.json",
        "source_lifecycle_task_return_body_path": (
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/test_lifecycle/task_return_body.md"
        ),
        "selected_latest_return_bindings": topology_rows,
    }

    from kernel import ion_domain_weaver as domain_weaver_module

    monkeypatch.setattr(
        domain_weaver_module,
        "_domain_weaver_dynamic_swarm_fresh_current_lifecycle_settlement",
        lambda *_args, **_kwargs: fake_settlement,
    )
    _write(
        tmp_path,
        DOMAIN_WEAVER_DYNAMIC_SWARM_FRESH_CONTEXT_RECONCILIATION_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "test",
                "lane_records": [
                    {
                        "domain_id": row["domain_id"],
                        "request_path": (
                            "ION/05_context/current/chatgpt_connector/codex_work_requests/"
                            f"test_topology_lane_{row['lane_ordinal']:02d}.json"
                        ),
                        "latest_run_task_return_body_path": (
                            "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
                            f"test_topology_lane_{row['lane_ordinal']:02d}/task_return_body.md"
                        ),
                    }
                    for row in topology_rows
                ],
            },
            indent=2,
        )
        + "\n",
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_topology_evolution_materialization_readiness_proof_gate",
            "packet_id": DOMAIN_WEAVER_TOPOLOGY_EVOLUTION_READINESS_PACKET_ID,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["packet_id"] == DOMAIN_WEAVER_TOPOLOGY_EVOLUTION_READINESS_PACKET_ID
    assert result["summary"]["fresh_current_settlement_ready"] is True
    assert result["summary"]["queued_request_count"] == 1
    assert result["summary"]["worker_started_count"] == 0
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_TOPOLOGY_EVOLUTION_READINESS_QUEUE_LEDGER_PATH.as_posix()
    )
    topology_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_TOPOLOGY_EVOLUTION_READINESS_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    topology_request = json.loads(
        (tmp_path / topology_ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8")
    )
    assert topology_request["request_kind"] == "domain_weaver_topology_evolution_materialization_readiness_proof_gate"
    assert topology_request["agent_role"] == "role.nemesis"
    assert topology_request["requested_model"] == "gpt-5.5"
    assert topology_request["requested_reasoning_effort"] == "xhigh"
    assert topology_request["requested_service_tier"] == "fast"
    assert topology_request["requested_authority"]["source_edit_authority"] is False
    assert topology_request["requested_authority"]["production_authority"] is False
    assert topology_request["requested_authority"]["live_execution_authority"] is False
    assert topology_request["requested_authority"]["accepted_state_claim"] is False
    assert topology_request["domain_weaver_topology_evolution_readiness_gate"]["topology_lane_count"] == 5
    assert topology_request["domain_weaver_topology_evolution_readiness_gate"]["required_verdict"] == (
        "topology_materialization_readiness_matrix_or_explicit_blocker"
    )


def test_domain_weaver_materializes_topology_child_ownership_post_fission_preflight(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    topology_domains = [
        "domain.continuity_context_resumability",
        "domain.current_phase_orchestration_management",
        "domain.archaeology_drift_watch",
        "domain.construction_routing_integration",
        "domain.confidence_drift_review",
    ]
    selected_rows = [
        {
            "lane_ordinal": index,
            "domain_id": domain_id,
            "latest_return_packet_path": (
                f"ION/05_context/current/chatgpt_connector/task_returns/test_topology_lane_{index:02d}.json"
            ),
            "latest_return_exists": True,
            "latest_return_accepted_for_carrier_intake": True,
            "return_packet_paths": [
                f"ION/05_context/current/chatgpt_connector/task_returns/test_topology_lane_{index:02d}.json"
            ],
            "duplicate_return_count": 0,
            "context_hash_drift_count": 0,
        }
        for index, domain_id in enumerate(topology_domains, start=1)
    ]
    _write(
        tmp_path,
        DOMAIN_WEAVER_DYNAMIC_SWARM_FRESH_CURRENT_LIFECYCLE_SETTLEMENT_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.dynamic_swarm_fresh_current_lifecycle_settlement.v0_1_candidate",
                "summary": {
                    "fresh_current_settlement_ready": True,
                    "selected_latest_binding_count": 5,
                    "selected_latest_missing_count": 0,
                    "selected_latest_not_accepted_count": 0,
                },
                "selected_latest_return_bindings": selected_rows,
            },
            indent=2,
        )
        + "\n",
    )
    lane_child_lines = {
        "domain.current_phase_orchestration_management": [
            "domain.current_phase_orchestration_management.queue_governor_lane_locks_candidate",
            "domain.current_phase_orchestration_management.phase_gate_settlement_sequence_candidate",
        ],
        "domain.archaeology_drift_watch": [
            "domain.archaeology_drift_watch.provenance_and_stale_authority_candidate",
            "domain.archaeology_drift_watch.archive_canon_reference_boundary_candidate",
            "domain.archaeology_drift_watch.review_reflex_and_escalation_candidate",
        ],
        "domain.construction_routing_integration": [
            "domain.construction_routing_integration.kernel_runtime_packetization_candidate",
            "domain.construction_routing_integration.context_template_handoff_candidate",
        ],
        "domain.confidence_drift_review": [
            "domain.confidence_drift_review.review_reflex_topology_candidate",
            "domain.confidence_drift_review.context_boundary_topology_candidate",
        ],
    }
    lane_records = []
    for index, domain_id in enumerate(topology_domains, start=1):
        body_rel = (
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
            f"test_topology_lane_{index:02d}/task_return_body.md"
        )
        request_rel = (
            "ION/05_context/current/chatgpt_connector/codex_work_requests/"
            f"test_topology_lane_{index:02d}.json"
        )
        return_rel = (
            f"ION/05_context/current/chatgpt_connector/task_returns/test_topology_lane_{index:02d}.json"
        )
        body_lines = ["### DOMAIN WEAVER EVOLUTION REVIEW"]
        for child_id in lane_child_lines.get(domain_id, []):
            body_lines.append(f"- `{child_id}`: candidate child domain.")
        _write(tmp_path, body_rel, "\n".join(body_lines) + "\n")
        _write(tmp_path, request_rel, json.dumps({"request_id": f"test_topology_lane_{index:02d}"}) + "\n")
        _write(
            tmp_path,
            return_rel,
            json.dumps({"accepted_for_carrier_intake": True, "task_return_body_path": body_rel}) + "\n",
        )
        lane_records.append(
            {
                "domain_id": domain_id,
                "request_path": request_rel,
                "latest_run_task_return_body_path": body_rel,
            }
        )
    _write(
        tmp_path,
        DOMAIN_WEAVER_DYNAMIC_SWARM_FRESH_CONTEXT_RECONCILIATION_PATH.as_posix(),
        json.dumps({"schema_id": "test", "lane_records": lane_records}, indent=2) + "\n",
    )
    _write(
        tmp_path,
        DOMAIN_WEAVER_TOPOLOGY_AUDIT_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.topology_audit.v0_1_candidate",
                "domain_rows": [
                    {
                        "domain_id": domain_id,
                        "mitosis_score": 80 - index,
                        "coupling_coefficient": 0.5,
                        "adaptive_coupling_threshold": 0.1,
                        "specialist_binding_count": 6,
                        "adaptive_specialist_binding_budget": 3,
                        "dominant_couplings": [{"domain_id": "domain.codex_carrier_sync", "weight": 1.0}],
                        "path_bucket_counts": {"kernel_runtime": 1},
                        "adaptive_controls": {"recommended_child_domain_count": 2 if index != 3 else 3},
                    }
                    for index, domain_id in enumerate(topology_domains, start=1)
                ],
                "proposed_child_domains": [
                    {
                        "domain_id": "domain.continuity_context_resumability_primary_specialists_topology_candidate",
                        "source_domain_id": "domain.continuity_context_resumability",
                        "fission_axis": "primary_specialists",
                        "role_ids": ["role.vizier"],
                        "projected_specialist_binding_count": 1,
                    },
                    {
                        "domain_id": "domain.continuity_context_resumability_secondary_couplings_1_topology_candidate",
                        "source_domain_id": "domain.continuity_context_resumability",
                        "fission_axis": "secondary_couplings_1",
                        "role_ids": ["role.browser_dom_cartographer"],
                        "projected_specialist_binding_count": 3,
                    },
                    {
                        "domain_id": "domain.continuity_context_resumability_secondary_couplings_2_topology_candidate",
                        "source_domain_id": "domain.continuity_context_resumability",
                        "fission_axis": "secondary_couplings_2",
                        "role_ids": ["role.vestige"],
                        "projected_specialist_binding_count": 2,
                    },
                    {
                        "domain_id": "domain.continuity_context_resumability_review_reflex_topology_candidate",
                        "source_domain_id": "domain.continuity_context_resumability",
                        "fission_axis": "review_reflex",
                        "role_ids": ["role.nemesis"],
                        "projected_specialist_binding_count": 2,
                    },
                ],
                "gates": {"post_fission_audit_gate": {"passed": False, "required_observation_cycles": 3}},
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        DOMAIN_WEAVER_TOPOLOGY_CONTROL_POLICY_PATH.as_posix(),
        json.dumps({"schema_id": "ion.domain_weaver.topology_adaptive_control_policy.v0_1_candidate"}) + "\n",
    )
    _write(
        tmp_path,
        DOMAIN_WEAVER_FISSION_TEMPLATE_LIBRARY_PATH.as_posix(),
        json.dumps({"schema_id": "ion.domain_weaver.fission_template_library.v0_1_candidate"}) + "\n",
    )
    _write(
        tmp_path,
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_PROOF_MATRIX_RESULT_PATH.as_posix(),
        json.dumps({"schema_id": "ion.domain_weaver.exact_active_specialist_binding_proof_matrix_result.v0_1_candidate"})
        + "\n",
    )
    readiness_request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_topology_evolution_readiness_proof_gate_20260602_attempt_001.json"
    )
    readiness_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/test_topology_readiness_return.json"
    readiness_machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        "test_topology_readiness_machine_receipt.json"
    )
    readiness_run_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/test_topology_readiness/run.json"
    )
    readiness_context_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/test_topology_readiness/context_receipt.json"
    )
    readiness_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/test_topology_readiness/task_return_body.md"
    )
    _write(
        tmp_path,
        readiness_body_rel,
        (
            "### RECOMMENDED NEXT PACKET\n\n"
            f"{DOMAIN_WEAVER_TOPOLOGY_CHILD_OWNERSHIP_PREFLIGHT_PACKET_ID}\n"
        ),
    )
    _write(
        tmp_path,
        readiness_run_rel,
        json.dumps(
            {
                "request_path": readiness_request_rel,
                "task_return_body_path": readiness_body_rel,
                "context_receipt_path": readiness_context_rel,
            }
        )
        + "\n",
    )
    _write(tmp_path, readiness_context_rel, json.dumps({"required_context_reads": []}) + "\n")
    _write(tmp_path, readiness_machine_rel, json.dumps({"ok": True}) + "\n")
    _write(
        tmp_path,
        readiness_return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": readiness_machine_rel,
                "task_return_body_path": readiness_body_rel,
            }
        )
        + "\n",
    )
    _write(
        tmp_path,
        readiness_request_rel,
        json.dumps(
            {
                "request_id": "codex_req_domain_weaver_topology_evolution_readiness_proof_gate_20260602_attempt_001",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "latest_return_packet_path": readiness_return_rel,
                "latest_task_return_machine_receipt_path": readiness_machine_rel,
            }
        )
        + "\n",
    )

    from kernel import ion_domain_weaver as domain_weaver_module

    _write(
        tmp_path,
        DOMAIN_WEAVER_PROJECTION_PATH.as_posix(),
        json.dumps({"schema_id": "ion.domain_weaver.projection.v0_1", "summary": {"exact_active_specialist_binding_count": 0}})
        + "\n",
    )
    monkeypatch.setattr(
        domain_weaver_module,
        "materialize_domain_weaver_projection",
        lambda *_args, **_kwargs: {"ok": True, "summary": {"exact_active_specialist_binding_count": 0}},
    )
    monkeypatch.setattr(
        domain_weaver_module,
        "_domain_weaver_latest_exact_active_specialist_binding_proof_matrix_result",
        lambda *_args, **_kwargs: {
            "summary": {
                "result_ready": True,
                "exact_active_specialist_binding_matrix_ready": False,
                "stop_classified_missing_exact_active_bindings": True,
                "exact_active_binding_count": 0,
                "candidate_boot_only_count": 5,
                "delegated_binding_not_exact": True,
                "delegated_substitution_settled": False,
            }
        },
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_topology_evolution_child_domain_ownership_post_fission_observation_preflight",
            "packet_id": DOMAIN_WEAVER_TOPOLOGY_CHILD_OWNERSHIP_PREFLIGHT_PACKET_ID,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["packet_id"] == DOMAIN_WEAVER_TOPOLOGY_CHILD_OWNERSHIP_PREFLIGHT_PACKET_ID
    assert result["summary"]["preflight_ready"] is True
    assert result["summary"]["child_rows_from_topology_audit"] == 4
    assert result["summary"]["child_rows_from_lane_bodies"] == 9
    assert result["summary"]["child_domain_owner_row_count"] == 13
    assert result["summary"]["required_observation_cycle_count"] == 3
    assert result["summary"]["completed_observation_cycle_count"] == 0
    assert result["summary"]["exact_active_binding_ready"] is False
    assert result["summary"]["topology_materialization_allowed"] is False
    preflight = json.loads((tmp_path / DOMAIN_WEAVER_TOPOLOGY_CHILD_OWNERSHIP_PREFLIGHT_PATH).read_text())
    child_ids = {
        child["child_domain_id"]
        for row in preflight["child_domain_owner_rows"]
        for child in row["child_domains"]
    }
    assert "domain.current_phase_orchestration_management.queue_governor_lane_locks_candidate" in child_ids
    assert "domain.archaeology_drift_watch.archive_canon_reference_boundary_candidate" in child_ids
    assert "domain.construction_routing_integration.kernel_runtime_packetization_candidate" in child_ids
    assert "domain.confidence_drift_review.context_boundary_topology_candidate" in child_ids
    assert preflight["exact_active_specialist_binding_matrix_recheck"]["exact_active_binding_count"] == 0
    assert len(preflight["post_fission_observation_plan"]["cycles"]) == 3
    assert preflight["authority"]["production_authority"] is False
    assert preflight["authority"]["live_execution_authority"] is False
    assert preflight["authority"]["accepted_state_authority"] is False


def test_domain_weaver_queues_topology_child_observation_cycle_audit(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    child_request_rel = "ION/05_context/current/chatgpt_connector/codex_work_requests/test_child_lane.json"
    child_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/test_child_lane_return.json"
    child_body_rel = "ION/05_context/current/chatgpt_connector/codex_queue_runs/test_child_lane/task_return_body.md"
    for rel in [child_request_rel, child_return_rel, child_body_rel]:
        _write(tmp_path, rel, "{}\n")
    fake_preflight = {
        "schema_id": "ion.domain_weaver.topology_child_domain_ownership_post_fission_observation_preflight.v0_1_candidate",
        "summary": {
            "preflight_ready": True,
            "topology_lane_count": 5,
            "child_domain_owner_row_count": 13,
            "required_observation_cycle_count": 3,
            "completed_observation_cycle_count": 0,
            "exact_active_binding_ready": False,
        },
        "child_domain_owner_rows": [
            {
                "source_domain_id": "domain.current_phase_orchestration_management",
                "source_request_path": child_request_rel,
                "source_return_packet_path": child_return_rel,
                "source_task_return_body_path": child_body_rel,
                "child_domains": [
                    {
                        "child_domain_id": (
                            "domain.current_phase_orchestration_management.queue_governor_lane_locks_candidate"
                        )
                    }
                ],
            }
        ],
    }

    from kernel import ion_domain_weaver as domain_weaver_module

    _write(
        tmp_path,
        DOMAIN_WEAVER_PROJECTION_PATH.as_posix(),
        json.dumps({"schema_id": "ion.domain_weaver.projection.v0_1", "summary": {}}) + "\n",
    )
    monkeypatch.setattr(
        domain_weaver_module,
        "materialize_domain_weaver_projection",
        lambda *_args, **_kwargs: {"ok": True, "summary": {}},
    )
    monkeypatch.setattr(
        domain_weaver_module,
        "_domain_weaver_topology_child_ownership_preflight",
        lambda *_args, **_kwargs: fake_preflight,
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_topology_child_ownership_observation_cycle_audit",
            "packet_id": DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_AUDIT_PACKET_ID,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["packet_id"] == DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_AUDIT_PACKET_ID
    assert result["summary"]["preflight_ready"] is True
    assert result["summary"]["queued_request_count"] == 1
    assert result["summary"]["worker_started_count"] == 0
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_AUDIT_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    request = json.loads((tmp_path / ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8"))
    assert request["request_kind"] == "domain_weaver_topology_child_ownership_observation_cycle_audit"
    assert request["agent_role"] == "role.nemesis"
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["requested_service_tier"] == "fast"
    assert request["requested_authority"]["source_edit_authority"] is False
    assert request["requested_authority"]["production_authority"] is False
    assert request["requested_authority"]["live_execution_authority"] is False
    assert request["requested_authority"]["accepted_state_claim"] is False
    assert DOMAIN_WEAVER_TOPOLOGY_CHILD_OWNERSHIP_PREFLIGHT_PATH.as_posix() in request["required_context_reads"]
    assert child_body_rel in request["required_context_reads"]
    audit = request["domain_weaver_topology_child_observation_audit"]
    assert audit["required_verdict"] == "observation_cycle_1_audit_or_explicit_blocker"
    assert audit["exact_active_binding_ready"] is False
    assert "do_not_start_child_workers" in audit["forbidden_actions"]


def test_domain_weaver_queues_topology_child_owner_matrix_stability_cycle_2(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    child_request_rel = "ION/05_context/current/chatgpt_connector/codex_work_requests/test_child_lane.json"
    child_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/test_child_lane_return.json"
    child_body_rel = "ION/05_context/current/chatgpt_connector/codex_queue_runs/test_child_lane/task_return_body.md"
    cycle1_request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_topology_child_observation_cycle_audit_20260602_attempt_001.json"
    )
    cycle1_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/test_cycle_1_return.json"
    cycle1_body_rel = "ION/05_context/current/chatgpt_connector/codex_queue_runs/test_cycle_1/task_return_body.md"
    for rel in [child_request_rel, child_return_rel, child_body_rel, cycle1_request_rel, cycle1_return_rel, cycle1_body_rel]:
        _write(tmp_path, rel, "{}\n")
    fake_preflight = {
        "schema_id": "ion.domain_weaver.topology_child_domain_ownership_post_fission_observation_preflight.v0_1_candidate",
        "summary": {
            "preflight_ready": True,
            "topology_lane_count": 5,
            "child_domain_owner_row_count": 13,
            "required_observation_cycle_count": 3,
            "exact_active_binding_ready": False,
        },
        "child_domain_owner_rows": [
            {
                "source_domain_id": "domain.confidence_drift_review",
                "source_request_path": child_request_rel,
                "source_return_packet_path": child_return_rel,
                "source_task_return_body_path": child_body_rel,
                "child_domains": [
                    {"child_domain_id": "domain.confidence_drift_review.context_boundary_topology_candidate"}
                ],
            }
        ],
    }
    fake_cycle1 = {
        "accepted": True,
        "result_ready": True,
        "request_path": cycle1_request_rel,
        "return_path": cycle1_return_rel,
        "task_return_body_path": cycle1_body_rel,
        "recommended_next_packet_id": DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_CYCLE2_PACKET_ID,
    }

    from kernel import ion_domain_weaver as domain_weaver_module

    _write(
        tmp_path,
        DOMAIN_WEAVER_PROJECTION_PATH.as_posix(),
        json.dumps({"schema_id": "ion.domain_weaver.projection.v0_1", "summary": {}}) + "\n",
    )
    monkeypatch.setattr(
        domain_weaver_module,
        "materialize_domain_weaver_projection",
        lambda *_args, **_kwargs: {"ok": True, "summary": {}},
    )
    monkeypatch.setattr(
        domain_weaver_module,
        "_domain_weaver_topology_child_ownership_preflight",
        lambda *_args, **_kwargs: fake_preflight,
    )
    monkeypatch.setattr(
        domain_weaver_module,
        "_domain_weaver_latest_topology_child_observation_audit_refs",
        lambda *_args, **_kwargs: fake_cycle1,
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_topology_child_owner_matrix_stability_observation_cycle_2",
            "packet_id": DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_CYCLE2_PACKET_ID,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["packet_id"] == DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_CYCLE2_PACKET_ID
    assert result["summary"]["preflight_ready"] is True
    assert result["summary"]["cycle_1_result_ready"] is True
    assert result["summary"]["queued_request_count"] == 1
    assert result["summary"]["worker_started_count"] == 0
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_CYCLE2_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    request = json.loads((tmp_path / ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8"))
    assert request["request_kind"] == "domain_weaver_topology_child_owner_matrix_stability_observation_cycle_2"
    assert request["agent_role"] == "role.nemesis"
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["requested_service_tier"] == "fast"
    assert request["requested_authority"]["source_edit_authority"] is False
    assert request["requested_authority"]["production_authority"] is False
    assert request["requested_authority"]["live_execution_authority"] is False
    assert request["requested_authority"]["accepted_state_claim"] is False
    assert cycle1_body_rel in request["required_context_reads"]
    assert child_body_rel in request["required_context_reads"]
    cycle2 = request["domain_weaver_topology_child_owner_matrix_stability_cycle_2"]
    assert cycle2["source_cycle_1_return_path"] == cycle1_return_rel
    assert cycle2["required_verdict"] == "observation_cycle_2_stability_audit_or_explicit_blocker"
    assert "do_not_collapse_duplicate_lineage" in cycle2["forbidden_actions"]


def test_domain_weaver_queues_topology_coupling_exact_binding_recheck_cycle_3(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    cycle2_request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_topology_child_owner_matrix_stability_cycle_2_20260602_attempt_001.json"
    )
    cycle2_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/test_cycle_2_latest_return.json"
    cycle2_old_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/test_cycle_2_old_return.json"
    cycle2_body_rel = "ION/05_context/current/chatgpt_connector/codex_queue_runs/test_cycle_2/task_return_body.md"
    for rel in [cycle2_request_rel, cycle2_return_rel, cycle2_old_return_rel, cycle2_body_rel]:
        _write(tmp_path, rel, "{}\n")
    fake_preflight = {
        "schema_id": "ion.domain_weaver.topology_child_domain_ownership_post_fission_observation_preflight.v0_1_candidate",
        "summary": {
            "preflight_ready": True,
            "topology_lane_count": 5,
            "child_domain_owner_row_count": 13,
            "required_observation_cycle_count": 3,
            "exact_active_binding_ready": False,
        },
    }
    fake_cycle2 = {
        "accepted": True,
        "result_ready": True,
        "request_path": cycle2_request_rel,
        "return_path": cycle2_return_rel,
        "return_packet_paths": [cycle2_old_return_rel, cycle2_return_rel],
        "task_return_body_path": cycle2_body_rel,
        "recommended_next_packet_id": DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_CYCLE3_PACKET_ID,
    }

    from kernel import ion_domain_weaver as domain_weaver_module

    _write(
        tmp_path,
        DOMAIN_WEAVER_PROJECTION_PATH.as_posix(),
        json.dumps({"schema_id": "ion.domain_weaver.projection.v0_1", "summary": {}}) + "\n",
    )
    monkeypatch.setattr(
        domain_weaver_module,
        "materialize_domain_weaver_projection",
        lambda *_args, **_kwargs: {"ok": True, "summary": {}},
    )
    monkeypatch.setattr(
        domain_weaver_module,
        "_domain_weaver_topology_child_ownership_preflight",
        lambda *_args, **_kwargs: fake_preflight,
    )
    monkeypatch.setattr(
        domain_weaver_module,
        "_domain_weaver_latest_topology_child_observation_cycle2_refs",
        lambda *_args, **_kwargs: fake_cycle2,
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_topology_coupling_reduction_exact_binding_recheck_cycle_3",
            "packet_id": DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_CYCLE3_PACKET_ID,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["packet_id"] == DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_CYCLE3_PACKET_ID
    assert result["summary"]["preflight_ready"] is True
    assert result["summary"]["cycle_2_result_ready"] is True
    assert result["summary"]["queued_request_count"] == 1
    assert result["summary"]["worker_started_count"] == 0
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_CYCLE3_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    request = json.loads((tmp_path / ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8"))
    assert request["request_kind"] == "domain_weaver_topology_coupling_reduction_exact_binding_recheck_cycle_3"
    assert request["agent_role"] == "role.nemesis"
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["requested_service_tier"] == "fast"
    assert request["requested_authority"]["source_edit_authority"] is False
    assert request["requested_authority"]["production_authority"] is False
    assert request["requested_authority"]["live_execution_authority"] is False
    assert request["requested_authority"]["accepted_state_claim"] is False
    assert cycle2_old_return_rel in request["required_context_reads"]
    assert cycle2_return_rel in request["required_context_reads"]
    assert cycle2_body_rel in request["required_context_reads"]
    cycle3 = request["domain_weaver_topology_coupling_reduction_exact_binding_recheck_cycle_3"]
    assert cycle3["source_cycle_2_return_packet_paths"] == [cycle2_old_return_rel, cycle2_return_rel]
    assert (
        cycle3["required_verdict"]
        == "observation_cycle_3_coupling_exact_binding_recheck_or_explicit_blocker"
    )
    assert "do_not_collapse_duplicate_lineage" in cycle3["forbidden_actions"]


def test_domain_weaver_materializes_post_fission_observation_fanin_materialization_stop(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    cycle1_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/test_cycle_1_return.json"
    cycle2_old_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/test_cycle_2_old_return.json"
    cycle2_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/test_cycle_2_latest_return.json"
    cycle3_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/test_cycle_3_return.json"
    for rel in [cycle1_return_rel, cycle2_old_return_rel, cycle2_return_rel, cycle3_return_rel]:
        _write(tmp_path, rel, json.dumps({"accepted_for_carrier_intake": True}) + "\n")
    _write(
        tmp_path,
        DOMAIN_WEAVER_TOPOLOGY_CHILD_OWNERSHIP_PREFLIGHT_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": (
                    "ion.domain_weaver.topology_child_domain_ownership_post_fission_observation_preflight."
                    "v0_1_candidate"
                ),
                "summary": {
                    "preflight_ready": True,
                    "topology_lane_count": 5,
                    "child_domain_owner_row_count": 13,
                    "required_observation_cycle_count": 3,
                    "completed_observation_cycle_count": 0,
                    "exact_active_binding_ready": False,
                    "exact_active_binding_count": 0,
                    "topology_materialization_allowed": False,
                },
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        DOMAIN_WEAVER_TOPOLOGY_AUDIT_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.topology_audit.v0_1_candidate",
                "topology_audit_ready": True,
                "selected_domain_id": "domain.continuity_context_resumability",
                "coupling_coefficient": 0.382,
                "adaptive_coupling_threshold": 0.111,
                "gates": {
                    "pre_fission_integrity_gate": {"passed": True},
                    "post_fission_audit_gate": {"passed": False, "required_observation_cycles": 3},
                },
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_PROOF_MATRIX_RESULT_PATH.as_posix(),
        json.dumps({"schema_id": "test", "summary": {"exact_active_binding_count": 0}}) + "\n",
    )
    _write(
        tmp_path,
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_ACTIVATION_GATE_RESULT_PATH.as_posix(),
        json.dumps({"schema_id": "test", "summary": {"result_ready": True}}) + "\n",
    )
    fake_cycle1 = {
        "accepted": True,
        "result_ready": True,
        "request_path": "ION/05_context/current/chatgpt_connector/codex_work_requests/test_cycle_1.json",
        "return_path": cycle1_return_rel,
        "task_return_body_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/test_cycle_1/task_return_body.md",
        "recommended_next_packet_id": DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_CYCLE2_PACKET_ID,
        "body_sha256": "cycle1",
    }
    fake_cycle2 = {
        "accepted": True,
        "result_ready": True,
        "request_path": "ION/05_context/current/chatgpt_connector/codex_work_requests/test_cycle_2.json",
        "return_path": cycle2_return_rel,
        "return_packet_paths": [cycle2_old_return_rel, cycle2_return_rel],
        "task_return_body_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/test_cycle_2/task_return_body.md",
        "recommended_next_packet_id": DOMAIN_WEAVER_TOPOLOGY_CHILD_OBSERVATION_CYCLE3_PACKET_ID,
        "body_sha256": "cycle2",
    }
    fake_cycle3 = {
        "accepted": True,
        "result_ready": True,
        "request_path": "ION/05_context/current/chatgpt_connector/codex_work_requests/test_cycle_3.json",
        "return_path": cycle3_return_rel,
        "task_return_body_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/test_cycle_3/task_return_body.md",
        "recommended_next_packet_id": DOMAIN_WEAVER_POST_FISSION_OBSERVATION_FANIN_MATERIALIZATION_STOP_PACKET_ID,
        "body_sha256": "cycle3",
    }

    from kernel import ion_domain_weaver as domain_weaver_module

    _write(
        tmp_path,
        DOMAIN_WEAVER_PROJECTION_PATH.as_posix(),
        json.dumps({"schema_id": "ion.domain_weaver.projection.v0_1", "summary": {}}) + "\n",
    )
    monkeypatch.setattr(
        domain_weaver_module,
        "materialize_domain_weaver_projection",
        lambda *_args, **_kwargs: {"ok": True, "summary": {}},
    )
    monkeypatch.setattr(
        domain_weaver_module,
        "_domain_weaver_latest_topology_child_observation_audit_refs",
        lambda *_args, **_kwargs: fake_cycle1,
    )
    monkeypatch.setattr(
        domain_weaver_module,
        "_domain_weaver_latest_topology_child_observation_cycle2_refs",
        lambda *_args, **_kwargs: fake_cycle2,
    )
    monkeypatch.setattr(
        domain_weaver_module,
        "_domain_weaver_latest_topology_child_observation_cycle3_refs",
        lambda *_args, **_kwargs: fake_cycle3,
    )
    monkeypatch.setattr(
        domain_weaver_module,
        "_domain_weaver_latest_exact_active_specialist_binding_proof_matrix_result",
        lambda *_args, **_kwargs: {
            "summary": {
                "result_ready": True,
                "exact_active_specialist_binding_matrix_ready": False,
                "exact_active_binding_count": 0,
                "candidate_boot_only_count": 5,
                "delegated_binding_not_exact": True,
                "delegated_substitution_settled": False,
            }
        },
    )
    monkeypatch.setattr(
        domain_weaver_module,
        "_domain_weaver_latest_exact_active_specialist_binding_activation_or_delegated_substitution_repair_result",
        lambda *_args, **_kwargs: {
            "summary": {
                "result_ready": True,
                "delegated_substitution_settled": True,
                "recommended_next_packet_id": (
                    "PCKT-DOMAIN-WEAVER-EXACT-ACTIVE-SPECIALIST-BINDING-FIVE-SPECIALIST-"
                    "ACTIVATION-GATE-20260602-ATTEMPT-001"
                ),
            }
        },
    )
    monkeypatch.setattr(
        domain_weaver_module,
        "_domain_weaver_latest_exact_active_specialist_binding_five_specialist_activation_gate_result",
        lambda *_args, **_kwargs: {
            "summary": {
                "result_ready": True,
                "materialization_ready": False,
                "stop_classified_missing_exact_active_bindings": True,
                "recommended_next_packet_id": (
                    "PCKT-DOMAIN-WEAVER-FIVE-SPECIALIST-EXACT-ACTIVE-BINDING-"
                    "REQUEST-MATERIALIZATION-NO-START-20260602-ATTEMPT-001"
                ),
            }
        },
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": (
                "materialize_post_fission_observation_fanin_settlement_and_exact_binding_materialization_stop"
            ),
            "packet_id": DOMAIN_WEAVER_POST_FISSION_OBSERVATION_FANIN_MATERIALIZATION_STOP_PACKET_ID,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["packet_id"] == DOMAIN_WEAVER_POST_FISSION_OBSERVATION_FANIN_MATERIALIZATION_STOP_PACKET_ID
    assert result["summary"]["observation_fanin_settlement_ready"] is True
    assert result["summary"]["completed_observation_cycle_count"] == 3
    assert result["summary"]["source_preflight_completed_observation_cycle_count"] == 0
    assert result["summary"]["source_counter_mutation_performed"] is False
    assert result["summary"]["materialization_decision"] == "MATERIALIZATION_STOP_EXACT_ACTIVE_BINDING_BLOCKER"
    assert result["summary"]["topology_materialization_allowed"] is False
    assert result["summary"]["exact_active_binding_count"] == 0
    assert result["summary"]["delegated_substitution_settled"] is True
    assert result["summary"]["duplicate_return_lineage_preserved"] is True
    assert (
        result["summary"]["next_lawful_action"]
        == "queue_five_specialist_exact_active_binding_request_materialization_no_start"
    )
    assert result["summary"]["worker_started_count"] == 0
    settlement = json.loads(
        (tmp_path / DOMAIN_WEAVER_POST_FISSION_OBSERVATION_FANIN_MATERIALIZATION_STOP_PATH).read_text()
    )
    assert settlement["source_counter_reconciliation"]["source_counter_mutation_performed"] is False
    assert settlement["topology_materialization_stop"]["active_registry_write_performed"] is False
    assert settlement["topology_materialization_stop"]["accepted_state_claim"] is False
    assert settlement["authority"]["worker_start_authority"] is False
    assert settlement["observation_cycle_rows"][1]["return_packet_paths"] == [
        cycle2_old_return_rel,
        cycle2_return_rel,
    ]
    assert (
        settlement["exact_active_binding_repair_pointer"]["source_result_path"]
        == DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_ACTIVATION_GATE_RESULT_PATH.as_posix()
    )


def test_domain_weaver_dynamic_swarm_worker_start_uses_computed_window(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": f"ION/05_context/current/chatgpt_connector/codex_queue_runs/{Path(request_path).stem}/run.json",
                "pid": 42000 + len(calls),
            },
        }

    from kernel import ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "start_dynamic_swarm_candidate_workers",
        },
    )

    assert result["ok"] is True
    assert result["required_confirmation"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["dynamic_start_window"] == 3
    assert result["summary"]["max_worker_starts"] == 3
    assert result["summary"]["worker_start_attempt_count"] == 3
    assert result["summary"]["worker_started_count"] == 3
    assert result["summary"]["worker_start_failure_count"] == 0
    assert result["summary"]["worker_start_status"] == "worker_start_succeeded"
    assert result["summary"]["fixed_domain_count_target"] is False
    assert result["summary"]["operator_parallelism_reference_is_target"] is False
    assert len(calls) == 3
    assert all(call["start"] is True and call["background"] is True for call in calls)
    started_lane_ids = {
        json.loads((tmp_path / call["request_path"]).read_text(encoding="utf-8"))["lane_id"]
        for call in calls
    }
    assert len(started_lane_ids) == 3
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_DYNAMIC_SWARM_CANDIDATE_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    assert ledger["summary"]["max_worker_starts"] == 3
    assert ledger["summary"]["worker_started_count"] == 3
    assert ledger["authority"]["production_authority"] is False
    assert ledger["authority"]["live_execution_authority"] is False


def test_domain_weaver_operator_action_queues_approval_governed_live_fanout(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    result = execute_domain_weaver_action(
        tmp_path,
        {"action": "queue_approval_governed_live_fanout", "confirmation": CONFIRMATION},
    )

    assert result["schema_id"] == "ion.domain_weaver.operator_action_result.v0_1"
    assert result["ok"] is True
    assert result["action"] == "queue_approval_governed_live_fanout"
    assert result["summary"]["queued_request_count"] > 0
    assert result["summary"]["worker_started_count"] == 0
    ledger_path = tmp_path / DOMAIN_WEAVER_LIVE_CARRIER_QUEUE_LEDGER_PATH
    assert ledger_path.is_file()
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert ledger["schema_id"] == "ion.domain_weaver.live_carrier_queue_ledger.v0_1_candidate"
    assert ledger["summary"]["queued_request_count"] == result["summary"]["queued_request_count"]
    assert ledger["summary"]["worker_started_count"] == 0
    work_request_paths = result["results"]["live_carrier_queue"]["work_request_paths"]
    assert len(work_request_paths) == result["summary"]["queued_request_count"]
    for rel in work_request_paths:
        payload = json.loads((tmp_path / rel).read_text(encoding="utf-8"))
        assert payload["schema_id"] == "ion.chatgpt_browser_connector_codex_work_request.v1"
        assert payload["status"] == "QUEUED_FOR_CODEX_CARRIER"
        assert payload["requested_by"] == "domain_weaver_approval_governor"
        assert payload["target_root_id"] == "active_ion_control"
        assert payload["movement_class"] == "ION_KERNEL_CONTROL_MOVEMENT"
        assert payload["ai_movement_root_envelope"]["target_root_id"] == "active_ion_control"
        assert payload["requested_authority"]["live_execution_authority"] is False
        assert payload["domain_weaver_live_binding"]["within_token_budget"] is True
        assert payload["production_authority"] is False
        assert payload["live_execution_authority"] is False
        assert payload["accepted_state_authority"] is False
        assert payload["secrets_authority"] is False
    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    blockers = {row["code"] for row in projection["original_plan_compliance"]["blockers"]}
    assert projection["summary"]["current_capability_class"] == "approval_governed_live_carrier_queue_bound"
    assert projection["summary"]["live_carrier_queued_request_count"] == result["summary"]["queued_request_count"]
    assert "LIVE_WORKER_START_NOT_EXECUTED" in blockers


def test_domain_weaver_live_fanout_worker_start_is_policy_governed_without_extra_confirmation(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_worker_start_context_mount(tmp_path, "audit_lane")
    _seed_worker_start_context_mount(tmp_path, "architecture_lane")

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": f"ION/05_context/current/chatgpt_connector/codex_queue_runs/no_magic_{len(calls)}",
                "pid": 8900 + len(calls),
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_approval_governed_live_fanout",
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["worker_started_count"] == 2
    assert len(calls) == 2


def test_domain_weaver_live_fanout_worker_start_uses_parallel_budget(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_worker_start_context_mount(tmp_path, "audit_lane")
    _seed_worker_start_context_mount(tmp_path, "architecture_lane")

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": f"ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_{len(calls)}",
                "pid": 9000 + len(calls),
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_approval_governed_live_fanout",
            "confirmation": CONFIRMATION,
            "start_workers": True,
            "live_execution_confirmation": "ION_DOMAIN_WEAVER_LIVE_EXECUTION_CONFIRMED",
        },
    )

    assert result["ok"] is True
    assert len(calls) == 2
    assert all(call["start"] is True for call in calls)
    assert all(call["background"] is True for call in calls)
    assert result["summary"]["worker_started_count"] == 2
    ledger = json.loads((tmp_path / DOMAIN_WEAVER_LIVE_CARRIER_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    assert ledger["summary"]["worker_start_attempt_count"] == 2
    assert ledger["summary"]["worker_started_count"] == 2
    assert sum(1 for row in ledger["queued_requests"] if row["worker_started"]) == 2
    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    assert projection["summary"]["live_carrier_worker_started_count"] == 2


def test_domain_weaver_live_fanout_worker_start_skips_accepted_returns(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    queue_only = execute_domain_weaver_action(
        tmp_path,
        {"action": "queue_approval_governed_live_fanout", "confirmation": CONFIRMATION},
    )
    assert queue_only["ok"] is True
    ledger = json.loads((tmp_path / DOMAIN_WEAVER_LIVE_CARRIER_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    accepted_lane = ledger["queued_requests"][0]["lane_id"]
    accepted_paths = {
        row["packet_path"]
        for row in ledger["queued_requests"]
        if row["lane_id"] == accepted_lane
    }
    assert accepted_paths

    for rel in accepted_paths:
        request_path = tmp_path / rel
        payload = json.loads(request_path.read_text(encoding="utf-8"))
        return_rel = f"ION/05_context/current/chatgpt_connector/task_returns/{payload['request_id']}_return.json"
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                    "created_at": "2026-05-31T00:00:00+00:00",
                    "request_id": payload["request_id"],
                    "accepted_for_carrier_intake": True,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {"accepted": True},
                    "workload_diff_accepted": True,
                },
                indent=2,
            )
            + "\n",
        )
        payload["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        payload["return_packet_paths"] = [return_rel]
        payload["latest_return_packet_path"] = return_rel
        request_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": f"ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_{len(calls)}",
                "pid": 9100 + len(calls),
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_approval_governed_live_fanout",
            "confirmation": CONFIRMATION,
            "start_workers": True,
            "live_execution_confirmation": "ION_DOMAIN_WEAVER_LIVE_EXECUTION_CONFIRMED",
        },
    )

    assert result["ok"] is True
    assert calls
    assert all(call["request_path"] not in accepted_paths for call in calls)
    refreshed_ledger = json.loads((tmp_path / DOMAIN_WEAVER_LIVE_CARRIER_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    assert sum(1 for row in refreshed_ledger["queued_requests"] if row["return_accepted"]) == len(accepted_paths)
    assert refreshed_ledger["summary"]["accepted_return_count"] == len(accepted_paths)
    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    assert projection["live_return_monitor"]["summary"]["accepted_return_count"] == len(accepted_paths)


def test_domain_weaver_live_fanin_settlement_completes_after_all_returns_accepted(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    queue_only = execute_domain_weaver_action(
        tmp_path,
        {"action": "queue_approval_governed_live_fanout", "confirmation": CONFIRMATION},
    )
    assert queue_only["ok"] is True
    ledger = json.loads((tmp_path / DOMAIN_WEAVER_LIVE_CARRIER_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    queued_paths = [row["packet_path"] for row in ledger["queued_requests"]]
    assert queued_paths

    for rel in queued_paths:
        request_path = tmp_path / rel
        payload = json.loads(request_path.read_text(encoding="utf-8"))
        return_rel = f"ION/05_context/current/chatgpt_connector/task_returns/{payload['request_id']}_return.json"
        run_rel = f"ION/05_context/current/chatgpt_connector/codex_queue_runs/{payload['request_id']}"
        context_receipt_rel = f"{run_rel}/context_receipt.json"
        body_rel = f"{run_rel}/task_return_body.md"
        _write(
            tmp_path,
            context_receipt_rel,
            json.dumps(
                {
                    "schema_id": "ion.context_load_receipt.v1",
                    "required_context_reads": [],
                },
                indent=2,
            )
            + "\n",
        )
        _write(
            tmp_path,
            body_rel,
            "\n".join(
                [
                    "### CONTEXT PROOF",
                    "all required context present",
                    "",
                    "### TEMPLATE ACTION PROOF",
                    "result: complete",
                    "",
                    "### VALIDATION",
                    "semantic return body clean",
                    "",
                    "### RESULT",
                    "Candidate-bounded worker return completed without semantic blockers.",
                    "",
                ]
            ),
        )
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                    "created_at": "2026-05-31T00:00:00+00:00",
                    "request_id": payload["request_id"],
                    "accepted_for_carrier_intake": True,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {
                        "accepted": True,
                        "touched_paths": [context_receipt_rel, body_rel],
                    },
                    "workload_diff_accepted": True,
                },
                indent=2,
            )
            + "\n",
        )
        payload["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        payload["return_packet_paths"] = [return_rel]
        payload["latest_return_packet_path"] = return_rel
        request_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = materialize_domain_weaver_projection(tmp_path)

    assert result["ok"] is True
    settlement_path = tmp_path / DOMAIN_WEAVER_LIVE_FANIN_SETTLEMENT_PATH
    assert settlement_path.is_file()
    settlement = json.loads(settlement_path.read_text(encoding="utf-8"))
    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    assert settlement["schema_id"] == "ion.domain_weaver.live_fanin_settlement.v0_1_candidate"
    assert settlement["status"] == "live_fanin_settlement_complete"
    assert settlement["summary"]["expected_return_count"] == len(queued_paths)
    assert settlement["summary"]["accepted_return_count"] == len(queued_paths)
    assert settlement["summary"]["missing_return_count"] == 0
    assert settlement["summary"]["settlement_complete"] is True
    assert all(row["accepted_return"] for row in settlement["return_records"])
    assert projection["summary"]["live_return_complete"] is True
    assert projection["summary"]["live_fanin_settlement_complete"] is True
    assert projection["summary"]["live_fanin_semantic_settlement_complete"] is True
    assert (
        projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"]
        == "PCKT-DOMAIN-WEAVER-RECURSIVE-LIVE-FANOUT-CHAIN-MVP-20260601"
    )


def test_domain_weaver_semantic_settlement_blocks_recursive_fanout_on_stale_return(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    queue_only = execute_domain_weaver_action(
        tmp_path,
        {"action": "queue_approval_governed_live_fanout", "confirmation": CONFIRMATION},
    )
    assert queue_only["ok"] is True
    ledger = json.loads((tmp_path / DOMAIN_WEAVER_LIVE_CARRIER_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    queued_paths = [row["packet_path"] for row in ledger["queued_requests"]]
    assert queued_paths

    for index, rel in enumerate(queued_paths):
        request_path = tmp_path / rel
        payload = json.loads(request_path.read_text(encoding="utf-8"))
        return_rel = f"ION/05_context/current/chatgpt_connector/task_returns/{payload['request_id']}_return.json"
        run_rel = f"ION/05_context/current/chatgpt_connector/codex_queue_runs/{payload['request_id']}"
        context_receipt_rel = f"{run_rel}/context_receipt.json"
        body_rel = f"{run_rel}/task_return_body.md"
        stale = index == 0
        required_context_reads = (
            [
                {
                    "path": "ION/03_registry/domains/domain.codex_carrier_sync.domain.yaml",
                    "sha256": "0" * 64,
                }
            ]
            if stale
            else []
        )
        _write(
            tmp_path,
            context_receipt_rel,
            json.dumps(
                {
                    "schema_id": "ion.context_load_receipt.v1",
                    "required_context_reads": required_context_reads,
                },
                indent=2,
            )
            + "\n",
        )
        _write(
            tmp_path,
            body_rel,
            "\n".join(
                [
                    "### CONTEXT PROOF",
                    "sha256_expected: 0000" if stale else "context current",
                    "sha256_observed: changed" if stale else "no drift",
                    "",
                    "### TEMPLATE ACTION PROOF",
                    "result: blocked" if stale else "result: complete",
                    "",
                    "### VALIDATION",
                    "context_receipt_missing_or_stale" if stale else "semantic return body clean",
                    "",
                    "### RESULT",
                    "Work is blocked by stale context hash drift."
                    if stale
                    else "Candidate-bounded worker return completed without semantic blockers.",
                    "",
                ]
            ),
        )
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                    "created_at": "2026-05-31T00:00:00+00:00",
                    "request_id": payload["request_id"],
                    "accepted_for_carrier_intake": True,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {
                        "accepted": True,
                        "touched_paths": [context_receipt_rel, body_rel],
                    },
                    "workload_diff_accepted": True,
                },
                indent=2,
            )
            + "\n",
        )
        payload["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        payload["return_packet_paths"] = [return_rel]
        payload["latest_return_packet_path"] = return_rel
        request_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = materialize_domain_weaver_projection(tmp_path)

    assert result["ok"] is True
    semantic_path = tmp_path / DOMAIN_WEAVER_LIVE_FANIN_SEMANTIC_SETTLEMENT_PATH
    repin_path = tmp_path / DOMAIN_WEAVER_LIVE_FANIN_SEMANTIC_REPIN_PLAN_PATH
    assert semantic_path.is_file()
    assert repin_path.is_file()
    semantic_settlement = json.loads(semantic_path.read_text(encoding="utf-8"))
    repin_plan = json.loads(repin_path.read_text(encoding="utf-8"))
    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    blockers = {row["code"] for row in projection["original_plan_compliance"]["blockers"]}
    assert semantic_settlement["summary"]["semantic_settlement_complete"] is False
    assert semantic_settlement["summary"]["semantic_blocked_return_count"] == 1
    assert semantic_settlement["summary"]["stale_context_return_count"] == 1
    assert semantic_settlement["summary"]["context_hash_drift_path_count"] == 1
    assert semantic_settlement["summary"]["context_repin_required"] is True
    assert repin_plan["summary"]["semantic_repin_plan_ready"] is True
    assert repin_plan["summary"]["repin_record_count"] == 1
    assert repin_plan["summary"]["current_drifted_pin_count"] == 1
    assert repin_plan["summary"]["blocked_return_reaudit_count"] == 1
    assert "LIVE_FANIN_SEMANTIC_SETTLEMENT_BLOCKED" in blockers
    assert "LIVE_FANIN_REPINNED_REAUDIT_REQUIRED" in blockers
    assert projection["summary"]["current_capability_class"] == (
        "approval_governed_live_fanin_semantic_settlement_blocked"
    )
    assert (
        projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"]
        == "PCKT-DOMAIN-WEAVER-LIVE-FANIN-REPINNED-NEMESIS-REAUDIT-20260601"
    )


def test_domain_weaver_semantic_settlement_excludes_dynamic_operational_reference_drift(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    queue_only = execute_domain_weaver_action(
        tmp_path,
        {"action": "queue_approval_governed_live_fanout", "confirmation": CONFIRMATION},
    )
    assert queue_only["ok"] is True
    ledger = json.loads((tmp_path / DOMAIN_WEAVER_LIVE_CARRIER_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    queued_paths = [row["packet_path"] for row in ledger["queued_requests"]]
    assert queued_paths

    for index, rel in enumerate(queued_paths):
        request_path = tmp_path / rel
        payload = json.loads(request_path.read_text(encoding="utf-8"))
        return_rel = f"ION/05_context/current/chatgpt_connector/task_returns/{payload['request_id']}_return.json"
        run_rel = f"ION/05_context/current/chatgpt_connector/codex_queue_runs/{payload['request_id']}"
        context_receipt_rel = f"{run_rel}/context_receipt.json"
        body_rel = f"{run_rel}/task_return_body.md"
        required_context_reads = (
            [
                {"path": rel, "sha256": "0" * 64},
                {"path": DOMAIN_WEAVER_PROJECTION_PATH.as_posix(), "sha256": "0" * 64},
                {"path": DOMAIN_WEAVER_LIVE_RETURN_MONITOR_PATH.as_posix(), "sha256": "0" * 64},
                {"path": DOMAIN_WEAVER_LIVE_FANIN_SETTLEMENT_PATH.as_posix(), "sha256": "0" * 64},
                {"path": DOMAIN_WEAVER_LIVE_FANIN_SEMANTIC_SETTLEMENT_PATH.as_posix(), "sha256": "0" * 64},
                {"path": DOMAIN_WEAVER_LIVE_FANIN_SEMANTIC_REPIN_PLAN_PATH.as_posix(), "sha256": "0" * 64},
                {"path": "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json", "sha256": "0" * 64},
            ]
            if index == 0
            else []
        )
        _write(
            tmp_path,
            context_receipt_rel,
            json.dumps(
                {
                    "schema_id": "ion.context_load_receipt.v1",
                    "required_context_reads": required_context_reads,
                },
                indent=2,
            )
            + "\n",
        )
        _write(
            tmp_path,
            body_rel,
            "\n".join(
                [
                    "### CONTEXT PROOF",
                    "dynamic operational evidence read",
                    "",
                    "### TEMPLATE ACTION PROOF",
                    "result: complete",
                    "",
                    "### VALIDATION",
                    "semantic return body clean",
                    "",
                    "### RESULT",
                    "Candidate-bounded worker return completed without semantic blockers.",
                    "",
                ]
            ),
        )
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                    "created_at": "2026-05-31T00:00:00+00:00",
                    "request_id": payload["request_id"],
                    "accepted_for_carrier_intake": True,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {
                        "accepted": True,
                        "touched_paths": [context_receipt_rel, body_rel],
                    },
                    "workload_diff_accepted": True,
                },
                indent=2,
            )
            + "\n",
        )
        payload["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        payload["return_packet_paths"] = [return_rel]
        payload["latest_return_packet_path"] = return_rel
        request_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = materialize_domain_weaver_projection(tmp_path)

    assert result["ok"] is True
    semantic_settlement = json.loads(
        (tmp_path / DOMAIN_WEAVER_LIVE_FANIN_SEMANTIC_SETTLEMENT_PATH).read_text(encoding="utf-8")
    )
    repin_plan = json.loads(
        (tmp_path / DOMAIN_WEAVER_LIVE_FANIN_SEMANTIC_REPIN_PLAN_PATH).read_text(encoding="utf-8")
    )
    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    compliance = projection["original_plan_compliance"]
    blockers = {row["code"] for row in compliance["blockers"]}
    capabilities = {row["capability"]: row for row in compliance["capabilities"]}
    first_record = semantic_settlement["semantic_return_records"][0]
    assert semantic_settlement["summary"]["semantic_settlement_complete"] is True
    assert semantic_settlement["summary"]["semantic_clean_return_count"] == len(queued_paths)
    assert semantic_settlement["summary"]["stale_context_return_count"] == 0
    assert semantic_settlement["summary"]["context_hash_drift_path_count"] == 0
    assert semantic_settlement["summary"]["dynamic_context_reference_drift_path_count"] == 7
    assert first_record["context_hash_drift_count"] == 0
    assert first_record["dynamic_context_reference_drift_count"] == 7
    assert repin_plan["summary"]["repin_record_count"] == 0
    assert "NO_EXECUTABLE_AGENT_ACTIVATION_PLANE" not in blockers
    assert "NO_EXECUTABLE_RECURSIVE_FANOUT_FANIN_SETTLEMENT" not in blockers
    assert "FOUNDING_ASSEMBLY_PARTIAL_EXECUTION_NOT_FULL_LATTICE" in blockers
    assert compliance["summary"]["approval_governed_activation_execution_proved"] is True
    assert compliance["summary"]["approval_governed_recursive_fanin_executable"] is True
    assert compliance["summary"]["founding_active_execution_count"] == len(queued_paths)
    assert capabilities["agent_activation_plane"]["status"] == "approval_governed_live_execution_proved"
    assert capabilities["recursive_fanout_fanin_settlement"]["status"] == (
        "approval_governed_live_semantic_settlement_complete"
    )


def _seed_domain_weaver_clean_live_fanin(tmp_path: Path) -> list[str]:
    queue_only = execute_domain_weaver_action(
        tmp_path,
        {"action": "queue_approval_governed_live_fanout", "confirmation": CONFIRMATION},
    )
    assert queue_only["ok"] is True
    ledger = json.loads((tmp_path / DOMAIN_WEAVER_LIVE_CARRIER_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    queued_paths = [row["packet_path"] for row in ledger["queued_requests"]]
    assert queued_paths
    for rel in queued_paths:
        request_path = tmp_path / rel
        payload = json.loads(request_path.read_text(encoding="utf-8"))
        return_rel = f"ION/05_context/current/chatgpt_connector/task_returns/{payload['request_id']}_return.json"
        run_rel = f"ION/05_context/current/chatgpt_connector/codex_queue_runs/{payload['request_id']}"
        body_rel = f"{run_rel}/task_return_body.md"
        _write(
            tmp_path,
            body_rel,
            "\n".join(
                [
                    "### CONTEXT PROOF",
                    "context current",
                    "",
                    "### TEMPLATE ACTION PROOF",
                    "result: complete",
                    "",
                    "### VALIDATION",
                    "semantic return body clean",
                    "",
                    "### RESULT",
                    "Candidate-bounded worker return completed without semantic blockers.",
                    "",
                ]
            ),
        )
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                    "created_at": "2026-06-01T00:00:00+00:00",
                    "request_id": payload["request_id"],
                    "accepted_for_carrier_intake": True,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {
                        "accepted": True,
                        "touched_paths": [body_rel],
                    },
                    "workload_diff_accepted": True,
                },
                indent=2,
            )
            + "\n",
        )
        payload["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        payload["return_packet_paths"] = [return_rel]
        payload["latest_return_packet_path"] = return_rel
        request_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    materialize_domain_weaver_projection(tmp_path)
    return queued_paths


def _seed_domain_weaver_recursive_chain_selection_return(tmp_path: Path) -> str:
    queue_result = execute_domain_weaver_action(
        tmp_path,
        {"action": "queue_recursive_live_fanout_chain_mvp"},
    )
    request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_recursive_live_fanout_chain_mvp_20260601.json"
    )
    request_path = tmp_path / request_rel
    if queue_result["ok"] is not True:
        blockers = set(queue_result.get("summary", {}).get("blockers") or [])
        assert "recursive_chain_not_current_recommended_next_packet" in blockers
        _write(
            tmp_path,
            request_rel,
            json.dumps(
                {
                    "schema_id": "ion.domain_weaver.codex_work_request.v0_1_candidate",
                    "request_id": "codex_req_domain_weaver_recursive_live_fanout_chain_mvp_20260601",
                    "path": request_rel,
                    "status": "QUEUED_FOR_CODEX_CARRIER",
                    "created_at": "2026-06-02T00:00:00+00:00",
                    "updated_at": "2026-06-02T00:00:00+00:00",
                    "lane_id": "architecture_lane",
                    "domain_id": "domain.current_phase_orchestration_management",
                    "role_id": "role.domain_weaver_root_steward",
                    "request_kind": "domain_weaver_recursive_live_fanout_chain_mvp",
                    "requested_model": "gpt-5.5",
                    "requested_reasoning_effort": "xhigh",
                    "domain_weaver_recursive_live_fanout_chain": {
                        "approval_governed_recursive_fanin_executable": True,
                        "candidate_only": True,
                    },
                    "production_authority": False,
                    "live_execution_authority": False,
                    "accepted_state_authority": False,
                    "secrets_authority": False,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
    else:
        assert queue_result["ok"] is True
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    run_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_2026-06-02T000000Z0000_codex_req_domain_weaver_recursive_live_fanout_chain_mvp_20260601"
    )
    body_rel = f"{run_rel}/task_return_body.md"
    return_rel = "ION/05_context/current/chatgpt_connector/task_returns/recursive_chain_selection_return.json"
    selected_packet = (
        "PCKT-DOMAIN-WEAVER-RECURSIVE-CYCLE-FISSION-REFLEX-BINDING-READINESS-20260602-ATTEMPT-001"
    )
    _write(
        tmp_path,
        body_rel,
        "\n".join(
            [
                "### CONTEXT PROOF",
                "context current",
                "",
                "### TEMPLATE ACTION PROOF",
                "template_id: ion.template.autonomous_loop.local_worker.v1",
                "action_id: codex_queue_runner_process_once",
                "result: candidate recursive cycle selected with live-start stop conditions",
                "touched_paths:",
                f"  - {body_rel}",
                "",
                "### VALIDATION",
                "semantic fan-in clean",
                "",
                "### RECURSIVE CHAIN SELECTION",
                f"packet_id: {selected_packet}",
                "verdict: candidate_next_recursive_cycle_selected_with_live_start_blocked",
                "",
                "### LIMITS AND STOP CONDITIONS",
                "chain_sequence_threshold: STOP_FOR_LIVE_START. Rebaseline required at policy ceiling.",
                "active_lane_locks: STOP_FOR_LIVE_START.",
                "",
                "### RECOMMENDED NEXT PACKET",
                selected_packet,
                "",
                "### RESULT",
                "UI quality is a separate nonblocking workstream.",
                "",
            ]
        ),
    )
    _write(
        tmp_path,
        f"{run_rel}/run.json",
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_run.v1",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "request_id": payload["request_id"],
                "request_path": request_rel,
                "run_packet_path": f"{run_rel}/run.json",
                "task_return_body_path": body_rel,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "created_at": "2026-06-02T00:00:00+00:00",
                "request_id": payload["request_id"],
                "accepted_for_carrier_intake": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [body_rel],
                },
                "workload_diff_accepted": True,
            },
            indent=2,
        )
        + "\n",
    )
    payload["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    payload["return_packet_paths"] = [return_rel]
    payload["latest_return_packet_path"] = return_rel
    request_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return selected_packet


def _seed_domain_weaver_recursive_cycle_readiness_return(tmp_path: Path) -> str:
    selected_packet = (
        "PCKT-DOMAIN-WEAVER-RECURSIVE-CYCLE-FISSION-REFLEX-BINDING-READINESS-20260602-ATTEMPT-001"
    )
    queue_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_recursive_cycle_fission_reflex_binding_readiness",
            "packet_id": selected_packet,
        },
    )
    request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_recursive_cycle_fission_reflex_binding_readiness_20260602_attempt_001.json"
    )
    request_path = tmp_path / request_rel
    if queue_result["ok"] is not True:
        blockers = set(queue_result.get("summary", {}).get("blockers") or [])
        assert "recursive_readiness_not_current_recommended_next_packet" in blockers
        _write(
            tmp_path,
            request_rel,
            json.dumps(
                {
                    "schema_id": "ion.domain_weaver.codex_work_request.v0_1_candidate",
                    "request_id": (
                        "codex_req_domain_weaver_recursive_cycle_fission_reflex_binding_readiness_"
                        "20260602_attempt_001"
                    ),
                    "path": request_rel,
                    "status": "QUEUED_FOR_CODEX_CARRIER",
                    "created_at": "2026-06-02T00:10:00+00:00",
                    "updated_at": "2026-06-02T00:10:00+00:00",
                    "lane_id": "architecture_lane",
                    "domain_id": "domain.current_phase_orchestration_management",
                    "role_id": "role.domain_weaver_root_steward",
                    "request_kind": "domain_weaver_recursive_cycle_fission_reflex_binding_readiness",
                    "requested_model": "gpt-5.5",
                    "requested_reasoning_effort": "xhigh",
                    "domain_weaver_recursive_cycle_readiness": {
                        "packet_id": selected_packet,
                        "later_live_fanout_worker_start_allowed": False,
                        "candidate_only": True,
                    },
                    "production_authority": False,
                    "live_execution_authority": False,
                    "accepted_state_authority": False,
                    "secrets_authority": False,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
    else:
        assert queue_result["ok"] is True
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    run_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_2026-06-02T001000Z0000_codex_req_domain_weaver_recursive_cycle_fission_reflex_binding_readiness_2026060"
    )
    body_rel = f"{run_rel}/task_return_body.md"
    return_rel = "ION/05_context/current/chatgpt_connector/task_returns/recursive_cycle_readiness_return.json"
    next_packet = (
        "PCKT-DOMAIN-WEAVER-FISSION-REFLEX-BINDING-FANOUT-TEMPLATE-MATERIALIZATION-20260602-ATTEMPT-001"
    )
    _write(
        tmp_path,
        body_rel,
        "\n".join(
            [
                "### CONTEXT PROOF",
                "context current",
                "",
                "### TEMPLATE ACTION PROOF",
                "template_id: ion.template.audit_observation.v1",
                "action_id: codex_queue_runner_process_once",
                "result: candidate readiness plan and fanout template set authored",
                "touched_paths:",
                f"  - {body_rel}",
                "",
                "### VALIDATION",
                "readiness plan ready",
                "",
                "### FANOUT TEMPLATE SET",
                "Template 1:",
                "  packet_id: PCKT-DOMAIN-WEAVER-FISSION-EXECUTION-GATES-20260602-ATTEMPT-001",
                "Template 2:",
                "  packet_id: PCKT-DOMAIN-WEAVER-DOMAIN-REFLEX-NETWORK-RULESET-20260602-ATTEMPT-001",
                "Template 3:",
                "  packet_id: PCKT-DOMAIN-WEAVER-SPECIALIST-BINDING-MATRIX-20260602-ATTEMPT-001",
                "",
                "### BLOCKERS",
                "- LIVE_START_BLOCKED_BY_PACKET",
                "",
                "### RECOMMENDED NEXT PACKET",
                next_packet,
                "No live workers started. Do not start workers from inside the materialization packet.",
                "",
                "### RESULT",
                "candidate_readiness_plan_ready_with_live_start_blocked",
                "",
            ]
        ),
    )
    _write(
        tmp_path,
        f"{run_rel}/run.json",
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_run.v1",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "request_id": payload["request_id"],
                "request_path": request_rel,
                "run_packet_path": f"{run_rel}/run.json",
                "task_return_body_path": body_rel,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "created_at": "2026-06-02T00:10:00+00:00",
                "request_id": payload["request_id"],
                "accepted_for_carrier_intake": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [body_rel],
                },
                "workload_diff_accepted": True,
            },
            indent=2,
        )
        + "\n",
    )
    payload["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    payload["return_packet_paths"] = [return_rel]
    payload["latest_return_packet_path"] = return_rel
    request_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return next_packet


def _seed_domain_weaver_fission_reflex_binding_accepted_returns(tmp_path: Path) -> str:
    _seed_domain_weaver_recursive_chain_selection_return(tmp_path)
    materialization_packet = _seed_domain_weaver_recursive_cycle_readiness_return(tmp_path)
    materialize_domain_weaver_projection(tmp_path)
    materialization = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_fission_reflex_binding_fanout_template_materialization",
            "packet_id": materialization_packet,
        },
    )
    assert materialization["ok"] is True
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_FISSION_REFLEX_BINDING_TEMPLATE_MATERIALIZATION_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    fanin_packet = "PCKT-DOMAIN-WEAVER-FISSION-REFLEX-BINDING-FANIN-SETTLEMENT-20260602-ATTEMPT-001"
    for row in ledger["queued_requests"]:
        request_path = tmp_path / row["packet_path"]
        payload = json.loads(request_path.read_text(encoding="utf-8"))
        run_rel = f"ION/05_context/current/chatgpt_connector/codex_queue_runs/{payload['request_id']}_accepted"
        body_rel = f"{run_rel}/task_return_body.md"
        return_rel = f"ION/05_context/current/chatgpt_connector/task_returns/{payload['request_id']}_accepted_return.json"
        _write(
            tmp_path,
            body_rel,
            "\n".join(
                [
                    "### CONTEXT PROOF",
                    "context current",
                    "",
                    "### TEMPLATE ACTION PROOF",
                    "template_id: ion.template.audit_observation.v1",
                    "action_id: codex_queue_runner_process_once",
                    "result: candidate fission/reflex/binding return accepted",
                    "touched_paths:",
                    f"  - {body_rel}",
                    "",
                    "### VALIDATION",
                    "return accepted",
                    "",
                    "### RESULT",
                    "candidate return ready for fan-in settlement",
                    "",
                    "### RECOMMENDED NEXT PACKET",
                    fanin_packet,
                    "",
                    "### ION OPERATIONAL POSTURE",
                    "production_authority: false",
                    "live_execution_authority: false",
                    "accepted_state_authority: false",
                    "secrets_authority: false",
                    "",
                ]
            ),
        )
        _write(
            tmp_path,
            f"{run_rel}/run.json",
            json.dumps(
                {
                    "schema_id": "ion.codex_queue_runner_run.v1",
                    "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                    "request_id": payload["request_id"],
                    "request_path": row["packet_path"],
                    "run_packet_path": f"{run_rel}/run.json",
                    "task_return_body_path": body_rel,
                },
                indent=2,
            )
            + "\n",
        )
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                    "created_at": "2026-06-02T02:00:00+00:00",
                    "request_id": payload["request_id"],
                    "accepted_for_carrier_intake": True,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {
                        "accepted": True,
                        "touched_paths": [body_rel],
                    },
                    "workload_diff_accepted": True,
                },
                indent=2,
            )
            + "\n",
        )
        payload["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        payload["return_packet_paths"] = [return_rel]
        payload["latest_return_packet_path"] = return_rel
        request_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return fanin_packet


def _seed_domain_weaver_fission_reflex_binding_fanin_settlement_return(tmp_path: Path) -> str:
    fanin_packet = _seed_domain_weaver_fission_reflex_binding_accepted_returns(tmp_path)
    materialize_domain_weaver_projection(tmp_path)
    queue_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_fission_reflex_binding_fanin_settlement",
            "packet_id": fanin_packet,
        },
    )
    assert queue_result["ok"] is True
    request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_fission_reflex_binding_fanin_settlement_20260602_attempt_001.json"
    )
    request_path = tmp_path / request_rel
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    run_rel = "ION/05_context/current/chatgpt_connector/codex_queue_runs/fission_reflex_binding_fanin_seed"
    body_rel = f"{run_rel}/task_return_body.md"
    return_rel = "ION/05_context/current/chatgpt_connector/task_returns/fission_reflex_binding_fanin_seed_return.json"
    next_packet = (
        "PCKT-DOMAIN-WEAVER-CHILD-DOMAIN-AND-SPECIALIST-BINDING-REPAIR-MATERIALIZATION-"
        "20260602-ATTEMPT-001"
    )
    _write(
        tmp_path,
        body_rel,
        "\n".join(
            [
                "### CONTEXT PROOF",
                "context current",
                "",
                "### TEMPLATE ACTION PROOF",
                "template_id: ion.template.autonomous_loop.local_worker.v1",
                "action_id: codex_queue_runner_process_once",
                "result: candidate fan-in settlement accepted",
                "touched_paths:",
                f"  - {body_rel}",
                "",
                "### VALIDATION",
                "fission/reflex/binding returns accepted",
                "",
                "### RESULT",
                "verdict: candidate_fanin_settlement_accept_design_returns_implementation_blocked",
                "",
                "### FANIN SETTLEMENT",
                "accepted_track_return_count: 3",
                "implementation_ready_now: false",
                "",
                "### RECOMMENDED NEXT PACKET",
                next_packet,
                "",
                "### ION OPERATIONAL POSTURE",
                "production_authority: false",
                "live_execution_authority: false",
                "accepted_state_authority: false",
                "secrets_authority: false",
                "",
            ]
        ),
    )
    _write(
        tmp_path,
        f"{run_rel}/run.json",
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_run.v1",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "request_id": payload["request_id"],
                "request_path": request_rel,
                "run_packet_path": f"{run_rel}/run.json",
                "task_return_body_path": body_rel,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "created_at": "2026-06-02T02:20:00+00:00",
                "request_id": payload["request_id"],
                "accepted_for_carrier_intake": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [body_rel],
                },
                "workload_diff_accepted": True,
            },
            indent=2,
        )
        + "\n",
    )
    payload["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    payload["return_packet_paths"] = [return_rel]
    payload["latest_return_packet_path"] = return_rel
    request_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return next_packet


def test_domain_weaver_recursive_live_fanout_chain_action_queues_and_starts_worker(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    queue_only = execute_domain_weaver_action(
        tmp_path,
        {"action": "queue_approval_governed_live_fanout", "confirmation": CONFIRMATION},
    )
    assert queue_only["ok"] is True
    ledger = json.loads((tmp_path / DOMAIN_WEAVER_LIVE_CARRIER_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    queued_paths = [row["packet_path"] for row in ledger["queued_requests"]]
    assert queued_paths
    for rel in queued_paths:
        request_path = tmp_path / rel
        payload = json.loads(request_path.read_text(encoding="utf-8"))
        return_rel = f"ION/05_context/current/chatgpt_connector/task_returns/{payload['request_id']}_return.json"
        run_rel = f"ION/05_context/current/chatgpt_connector/codex_queue_runs/{payload['request_id']}"
        body_rel = f"{run_rel}/task_return_body.md"
        _write(
            tmp_path,
            body_rel,
            "\n".join(
                [
                    "### CONTEXT PROOF",
                    "context current",
                    "",
                    "### TEMPLATE ACTION PROOF",
                    "result: complete",
                    "",
                    "### VALIDATION",
                    "semantic return body clean",
                    "",
                    "### RESULT",
                    "Candidate-bounded worker return completed without semantic blockers.",
                    "",
                ]
            ),
        )
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                    "created_at": "2026-06-01T00:00:00+00:00",
                    "request_id": payload["request_id"],
                    "accepted_for_carrier_intake": True,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {
                        "accepted": True,
                        "touched_paths": [body_rel],
                    },
                    "workload_diff_accepted": True,
                },
                indent=2,
            )
            + "\n",
        )
        payload["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        payload["return_packet_paths"] = [return_rel]
        payload["latest_return_packet_path"] = return_rel
        request_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    materialize_domain_weaver_projection(tmp_path)

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_recursive_chain/run.json",
                "pid": 9601,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_recursive_live_fanout_chain_mvp",
            "packet_id": "PCKT-DOMAIN-WEAVER-RECURSIVE-LIVE-FANOUT-CHAIN-MVP-20260601",
            "start_workers": True,
        },
    )

    expected_request_path = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_recursive_live_fanout_chain_mvp_20260601.json"
    )
    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["worker_started_count"] == 1
    assert result["summary"]["queue_ledger_path"] == DOMAIN_WEAVER_RECURSIVE_LIVE_FANOUT_CHAIN_QUEUE_LEDGER_PATH.as_posix()
    assert calls == [{"request_path": expected_request_path, "start": True, "background": True}]

    request = json.loads((tmp_path / expected_request_path).read_text(encoding="utf-8"))
    assert request["request_kind"] == "domain_weaver_recursive_live_fanout_chain_mvp"
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert DOMAIN_WEAVER_LIVE_FANIN_SEMANTIC_SETTLEMENT_PATH.as_posix() in request["required_context_reads"]
    assert request["domain_weaver_recursive_live_fanout_chain"]["approval_governed_recursive_fanin_executable"] is True
    assert request["production_authority"] is False
    assert request["live_execution_authority"] is False
    assert request["accepted_state_authority"] is False
    assert request["secrets_authority"] is False


def test_domain_weaver_accepted_recursive_chain_selection_advances_next_packet(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_clean_live_fanin(tmp_path)
    selected_packet = _seed_domain_weaver_recursive_chain_selection_return(tmp_path)

    materialize_domain_weaver_projection(tmp_path)
    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    compliance = projection["original_plan_compliance"]
    summary = compliance["summary"]
    selection = projection["recursive_live_fanout_chain_selection"]

    assert selection["selection_ready"] is True
    assert (tmp_path / DOMAIN_WEAVER_RECURSIVE_LIVE_FANOUT_CHAIN_SELECTION_PATH).is_file()
    assert compliance["recommended_next_packet"]["packet_id"] == selected_packet
    assert compliance["recommended_next_packet"]["lane_id"] == "architecture_lane"
    assert summary["recursive_chain_selection_ready"] is True
    assert summary["recursive_chain_selected_packet_id"] == selected_packet
    assert summary["recursive_chain_rebaseline_required"] is True
    assert projection["summary"]["current_capability_class"] == "approval_governed_recursive_cycle_selected"


def test_domain_weaver_recursive_cycle_readiness_action_queues_and_starts_worker(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_clean_live_fanin(tmp_path)
    selected_packet = _seed_domain_weaver_recursive_chain_selection_return(tmp_path)
    materialize_domain_weaver_projection(tmp_path)

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_recursive_readiness/run.json",
                "pid": 9701,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_recursive_cycle_fission_reflex_binding_readiness",
            "packet_id": selected_packet,
            "start_workers": True,
        },
    )

    expected_request_path = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_recursive_cycle_fission_reflex_binding_readiness_20260602_attempt_001.json"
    )
    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["chain_sequence_rebaseline_ledger_path"] == (
        DOMAIN_WEAVER_CHAIN_SEQUENCE_REBASELINE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["queue_ledger_path"] == DOMAIN_WEAVER_RECURSIVE_CYCLE_READINESS_QUEUE_LEDGER_PATH.as_posix()
    assert result["summary"]["worker_started_count"] == 1
    assert calls == [{"request_path": expected_request_path, "start": True, "background": True}]

    request = json.loads((tmp_path / expected_request_path).read_text(encoding="utf-8"))
    assert request["request_kind"] == "domain_weaver_recursive_cycle_fission_reflex_binding_readiness"
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert request["domain_weaver_recursive_cycle_readiness"]["packet_id"] == selected_packet
    assert request["domain_weaver_recursive_cycle_readiness"]["later_live_fanout_worker_start_allowed"] is False
    assert DOMAIN_WEAVER_RECURSIVE_LIVE_FANOUT_CHAIN_SELECTION_PATH.as_posix() in request["required_context_reads"]
    assert DOMAIN_WEAVER_CHAIN_SEQUENCE_REBASELINE_LEDGER_PATH.as_posix() in request["required_context_reads"]
    assert request["production_authority"] is False
    assert request["live_execution_authority"] is False
    assert request["accepted_state_authority"] is False
    assert request["secrets_authority"] is False


def test_domain_weaver_accepted_recursive_cycle_readiness_advances_to_template_materialization(
    tmp_path: Path,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_clean_live_fanin(tmp_path)
    _seed_domain_weaver_recursive_chain_selection_return(tmp_path)
    next_packet = _seed_domain_weaver_recursive_cycle_readiness_return(tmp_path)

    materialize_domain_weaver_projection(tmp_path)
    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    compliance = projection["original_plan_compliance"]
    summary = compliance["summary"]
    readiness = projection["recursive_cycle_readiness_result"]

    assert readiness["result_ready"] is True
    assert (tmp_path / DOMAIN_WEAVER_RECURSIVE_CYCLE_READINESS_RESULT_PATH).is_file()
    assert compliance["recommended_next_packet"]["packet_id"] == next_packet
    assert compliance["recommended_next_packet"]["work_class"] == "queue_materialization"
    assert summary["recursive_cycle_readiness_ready"] is True
    assert summary["recursive_cycle_readiness_next_packet_id"] == next_packet
    assert projection["summary"]["current_capability_class"] == "approval_governed_recursive_cycle_readiness_ready"


def test_domain_weaver_fission_reflex_binding_template_materialization_queues_without_start(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_clean_live_fanin(tmp_path)
    _seed_domain_weaver_recursive_chain_selection_return(tmp_path)
    next_packet = _seed_domain_weaver_recursive_cycle_readiness_return(tmp_path)
    materialize_domain_weaver_projection(tmp_path)

    calls = []

    def fake_process_once(*_args, **_kwargs):
        calls.append(_kwargs)
        return {"ok": False, "result": "should_not_start"}

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_fission_reflex_binding_fanout_template_materialization",
            "packet_id": next_packet,
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_FISSION_REFLEX_BINDING_TEMPLATE_MATERIALIZATION_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["queued_request_count"] == 3
    assert result["summary"]["worker_start_forced_off_by_readiness_stop_condition"] is True
    assert result["summary"]["worker_started_count"] == 0
    assert calls == []

    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_FISSION_REFLEX_BINDING_TEMPLATE_MATERIALIZATION_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    paths = [row["packet_path"] for row in ledger["queued_requests"]]
    assert len(paths) == 3
    for rel in paths:
        request = json.loads((tmp_path / rel).read_text(encoding="utf-8"))
        assert request["status"] == "QUEUED_FOR_CODEX_CARRIER"
        assert request["requested_model"] == "gpt-5.5"
        assert request["requested_reasoning_effort"] == "xhigh"
        assert request["domain_weaver_fission_reflex_binding_template"]["queue_only_materialization"] is True
        assert request["domain_weaver_fission_reflex_binding_template"]["worker_start_allowed_by_this_packet"] is False
        assert request["production_authority"] is False
        assert request["live_execution_authority"] is False
        assert request["accepted_state_authority"] is False
        assert request["secrets_authority"] is False


def test_domain_weaver_fission_reflex_binding_worker_start_gate_starts_lane_distinct_workers(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_clean_live_fanin(tmp_path)
    _seed_domain_weaver_recursive_chain_selection_return(tmp_path)
    next_packet = _seed_domain_weaver_recursive_cycle_readiness_return(tmp_path)
    materialize_domain_weaver_projection(tmp_path)

    materialization = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_fission_reflex_binding_fanout_template_materialization",
            "packet_id": next_packet,
            "start_workers": True,
        },
    )
    assert materialization["ok"] is True

    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    start_packet = "PCKT-DOMAIN-WEAVER-FISSION-REFLEX-BINDING-FANOUT-WORKER-START-20260602-ATTEMPT-001"
    assert projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"] == start_packet
    assert projection["summary"]["fission_reflex_binding_templates_queued"] is True
    assert projection["summary"]["fission_reflex_binding_queueable_start_request_count"] == 3

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": f"ION/05_context/current/chatgpt_connector/codex_queue_runs/{Path(request_path).stem}/run.json",
                "pid": 9800 + len(calls),
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "start_fission_reflex_binding_fanout_workers",
            "packet_id": start_packet,
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_FISSION_REFLEX_BINDING_FANOUT_WORKER_START_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["source_queue_ledger_path"] == (
        DOMAIN_WEAVER_FISSION_REFLEX_BINDING_TEMPLATE_MATERIALIZATION_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["source_queued_request_count"] == 3
    assert result["summary"]["source_queueable_start_request_count"] == 3
    assert result["summary"]["queued_request_count"] == 3
    assert result["summary"]["queueable_start_request_count"] == 3
    assert result["summary"]["worker_start_attempt_count"] == 2
    assert result["summary"]["worker_started_count"] == 2
    assert result["summary"]["remaining_queueable_start_request_count"] == 1
    assert len(result["summary"]["work_request_paths"]) == 3
    assert len(calls) == 2

    started_lanes = []
    for call in calls:
        assert call["start"] is True
        assert call["background"] is True
        request = json.loads((tmp_path / call["request_path"]).read_text(encoding="utf-8"))
        started_lanes.append(request["lane_id"])
        assert request["requested_model"] == "gpt-5.5"
        assert request["requested_reasoning_effort"] == "xhigh"
        assert request["domain_weaver_fission_reflex_binding_template"]["queue_only_materialization"] is True
        assert request["domain_weaver_fission_reflex_binding_template"]["worker_start_allowed_by_this_packet"] is False
        assert request["production_authority"] is False
        assert request["live_execution_authority"] is False
        assert request["accepted_state_authority"] is False
        assert request["secrets_authority"] is False

    assert sorted(started_lanes) == ["approval_governance_lane", "architecture_lane"]

    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_FISSION_REFLEX_BINDING_FANOUT_WORKER_START_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert ledger["queue_action"] == "start_fission_reflex_binding_fanout_workers"
    assert ledger["summary"]["worker_started_count"] == 2
    assert ledger["summary"]["worker_start_attempt_count"] == 2
    assert ledger["authority"]["production_authority"] is False
    assert ledger["authority"]["live_execution_authority"] is False
    assert ledger["authority"]["accepted_state_authority"] is False
    assert ledger["authority"]["secrets_authority"] is False


def test_domain_weaver_accepted_fission_reflex_binding_fanout_advances_to_fanin_settlement(
    tmp_path: Path,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_clean_live_fanin(tmp_path)
    fanin_packet = _seed_domain_weaver_fission_reflex_binding_accepted_returns(tmp_path)

    materialize_domain_weaver_projection(tmp_path)
    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    compliance = projection["original_plan_compliance"]
    summary = compliance["summary"]
    materialization = projection["fission_reflex_binding_materialization"]

    assert materialization["fanout_returns_complete"] is True
    assert materialization["summary"]["accepted_return_count"] == 3
    assert compliance["recommended_next_packet"]["packet_id"] == fanin_packet
    assert compliance["recommended_next_packet"]["work_class"] == "settlement"
    assert projection["summary"]["current_capability_class"] == (
        "approval_governed_fission_reflex_binding_fanout_returns_complete"
    )
    assert summary["fission_reflex_binding_fanout_returns_complete"] is True
    assert summary["fission_reflex_binding_accepted_return_count"] == 3


def test_domain_weaver_fission_reflex_binding_fanin_settlement_queues_and_starts_worker(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_clean_live_fanin(tmp_path)
    fanin_packet = _seed_domain_weaver_fission_reflex_binding_accepted_returns(tmp_path)
    materialize_domain_weaver_projection(tmp_path)

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_fanin/run.json",
                "pid": 9901,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_fission_reflex_binding_fanin_settlement",
            "packet_id": fanin_packet,
            "start_workers": True,
        },
    )

    expected_request_path = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_fission_reflex_binding_fanin_settlement_20260602_attempt_001.json"
    )
    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_FISSION_REFLEX_BINDING_FANIN_SETTLEMENT_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["accepted_return_count"] == 3
    assert result["summary"]["fanout_returns_complete"] is True
    assert result["summary"]["queued_request_count"] == 1
    assert result["summary"]["worker_start_attempt_count"] == 1
    assert result["summary"]["worker_started_count"] == 1
    assert calls == [{"request_path": expected_request_path, "start": True, "background": True}]

    request = json.loads((tmp_path / expected_request_path).read_text(encoding="utf-8"))
    assert request["request_kind"] == "domain_weaver_fission_reflex_binding_fanin_settlement"
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    settlement = request["domain_weaver_fission_reflex_binding_fanin_settlement"]
    assert settlement["accepted_return_count"] == 3
    assert len(settlement["accepted_returns"]) == 3
    for record in settlement["accepted_returns"]:
        assert record["request_path"] in request["required_context_reads"]
        assert record["return_path"] in request["required_context_reads"]
        assert record["task_return_body_path"] in request["required_context_reads"]
    assert request["production_authority"] is False
    assert request["live_execution_authority"] is False
    assert request["accepted_state_authority"] is False
    assert request["secrets_authority"] is False


def test_domain_weaver_accepted_fission_reflex_binding_fanin_advances_to_repair_materialization(
    tmp_path: Path,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_clean_live_fanin(tmp_path)
    next_packet = _seed_domain_weaver_fission_reflex_binding_fanin_settlement_return(tmp_path)

    materialize_domain_weaver_projection(tmp_path)
    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    compliance = projection["original_plan_compliance"]
    summary = compliance["summary"]

    assert (tmp_path / DOMAIN_WEAVER_FISSION_REFLEX_BINDING_FANIN_SETTLEMENT_RESULT_PATH).is_file()
    assert projection["fission_reflex_binding_fanin_settlement"]["result_ready"] is True
    assert compliance["recommended_next_packet"]["packet_id"] == next_packet
    assert compliance["recommended_next_packet"]["work_class"] == "queue_materialization"
    assert projection["summary"]["current_capability_class"] == (
        "approval_governed_child_domain_specialist_binding_repair_materialization_ready"
    )
    assert summary["fission_reflex_binding_fanin_settlement_ready"] is True
    assert summary["fission_reflex_binding_fanin_next_packet_id"] == next_packet


def test_domain_weaver_child_domain_specialist_binding_repair_materialization_queues_without_start(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_clean_live_fanin(tmp_path)
    next_packet = _seed_domain_weaver_fission_reflex_binding_fanin_settlement_return(tmp_path)
    materialize_domain_weaver_projection(tmp_path)

    calls = []

    def fake_process_once(*_args, **_kwargs):
        calls.append(_kwargs)
        return {"ok": False, "result": "should_not_start"}

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_child_domain_and_specialist_binding_repair_materialization",
            "packet_id": next_packet,
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_MATERIALIZATION_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["queued_request_count"] == 8
    assert result["summary"]["queueable_start_request_count"] == 8
    assert result["summary"]["worker_start_forced_off_by_materialization_stop_condition"] is True
    assert result["summary"]["worker_started_count"] == 0
    assert calls == []

    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    start_packet = (
        "PCKT-DOMAIN-WEAVER-CHILD-DOMAIN-SPECIALIST-BINDING-REPAIR-WORKER-START-"
        "20260602-ATTEMPT-001"
    )
    assert projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"] == start_packet
    assert projection["summary"]["child_domain_specialist_binding_repair_requests_queued"] is True
    assert projection["summary"]["child_domain_specialist_binding_repair_queueable_start_request_count"] == 8

    ledger = json.loads(
        (
            tmp_path
            / DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_MATERIALIZATION_QUEUE_LEDGER_PATH
        ).read_text(encoding="utf-8")
    )
    assert len(ledger["queued_requests"]) == 8
    lanes = sorted({row["lane_id"] for row in ledger["queued_requests"]})
    assert lanes == ["approval_governance_lane", "architecture_lane"]
    required_ui_canon = {path.as_posix() for path in DOMAIN_WEAVER_UI_CANON_CONTEXT_PATHS}
    for row in ledger["queued_requests"]:
        request = json.loads((tmp_path / row["packet_path"]).read_text(encoding="utf-8"))
        assert request["status"] == "QUEUED_FOR_CODEX_CARRIER"
        assert request["requested_model"] == "gpt-5.5"
        assert request["requested_reasoning_effort"] == "xhigh"
        assert required_ui_canon.issubset(set(request["required_context_reads"]))
        assert request["domain_weaver_child_domain_specialist_binding_repair_template"]["queue_only_materialization"] is True
        assert request["domain_weaver_child_domain_specialist_binding_repair_template"]["worker_start_allowed_by_this_packet"] is False
        assert request["production_authority"] is False
        assert request["live_execution_authority"] is False
        assert request["accepted_state_authority"] is False
        assert request["secrets_authority"] is False


def test_domain_weaver_child_domain_specialist_binding_repair_worker_start_gate_starts_lane_distinct_workers(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_clean_live_fanin(tmp_path)
    next_packet = _seed_domain_weaver_fission_reflex_binding_fanin_settlement_return(tmp_path)
    materialize_domain_weaver_projection(tmp_path)

    materialization = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_child_domain_and_specialist_binding_repair_materialization",
            "packet_id": next_packet,
            "start_workers": True,
        },
    )
    assert materialization["ok"] is True

    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    start_packet = (
        "PCKT-DOMAIN-WEAVER-CHILD-DOMAIN-SPECIALIST-BINDING-REPAIR-WORKER-START-"
        "20260602-ATTEMPT-001"
    )
    assert projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"] == start_packet
    assert projection["summary"]["child_domain_specialist_binding_repair_requests_queued"] is True
    assert projection["summary"]["child_domain_specialist_binding_repair_queueable_start_request_count"] == 8

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": (
                    "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
                    f"{Path(request_path).stem}/run.json"
                ),
                "pid": 9900 + len(calls),
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "start_child_domain_and_specialist_binding_repair_workers",
            "packet_id": start_packet,
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_WORKER_START_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["source_queue_ledger_path"] == (
        DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_MATERIALIZATION_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["source_queued_request_count"] == 8
    assert result["summary"]["source_queueable_start_request_count"] == 8
    assert result["summary"]["queued_request_count"] == 8
    assert result["summary"]["queueable_start_request_count"] == 8
    assert result["summary"]["worker_start_attempt_count"] == 2
    assert result["summary"]["worker_started_count"] == 2
    assert result["summary"]["remaining_queueable_start_request_count"] == 6
    assert len(result["summary"]["work_request_paths"]) == 8
    assert len(calls) == 2

    started_lanes = []
    required_ui_canon = {path.as_posix() for path in DOMAIN_WEAVER_UI_CANON_CONTEXT_PATHS}
    for call in calls:
        assert call["start"] is True
        assert call["background"] is True
        request = json.loads((tmp_path / call["request_path"]).read_text(encoding="utf-8"))
        started_lanes.append(request["lane_id"])
        assert request["requested_model"] == "gpt-5.5"
        assert request["requested_reasoning_effort"] == "xhigh"
        assert required_ui_canon.issubset(set(request["required_context_reads"]))
        assert request["domain_weaver_child_domain_specialist_binding_repair_template"]["queue_only_materialization"] is True
        assert request["domain_weaver_child_domain_specialist_binding_repair_template"]["worker_start_allowed_by_this_packet"] is False
        assert request["production_authority"] is False
        assert request["live_execution_authority"] is False
        assert request["accepted_state_authority"] is False
        assert request["secrets_authority"] is False

    assert sorted(started_lanes) == ["approval_governance_lane", "architecture_lane"]

    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_WORKER_START_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert ledger["queue_action"] == "start_child_domain_and_specialist_binding_repair_workers"
    assert ledger["summary"]["worker_started_count"] == 2
    assert ledger["summary"]["worker_start_attempt_count"] == 2
    assert ledger["authority"]["production_authority"] is False
    assert ledger["authority"]["live_execution_authority"] is False
    assert ledger["authority"]["accepted_state_authority"] is False
    assert ledger["authority"]["secrets_authority"] is False


def _seed_domain_weaver_child_domain_specialist_binding_repair_accepted_returns(
    tmp_path: Path,
    *,
    missing_ui_canon_targets: set[str] | None = None,
) -> str:
    missing_ui_canon_targets = missing_ui_canon_targets or set()
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_clean_live_fanin(tmp_path)
    next_packet = _seed_domain_weaver_fission_reflex_binding_fanin_settlement_return(tmp_path)
    materialize_domain_weaver_projection(tmp_path)
    materialization = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_child_domain_and_specialist_binding_repair_materialization",
            "packet_id": next_packet,
            "start_workers": False,
        },
    )
    assert materialization["ok"] is True
    ledger = json.loads(
        (
            tmp_path
            / DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_MATERIALIZATION_QUEUE_LEDGER_PATH
        ).read_text(encoding="utf-8")
    )
    required_ui_canon = {path.as_posix() for path in DOMAIN_WEAVER_UI_CANON_CONTEXT_PATHS}
    for row in ledger["queued_requests"]:
        request_path = row["packet_path"]
        request = json.loads((tmp_path / request_path).read_text(encoding="utf-8"))
        meta = request["domain_weaver_child_domain_specialist_binding_repair_template"]
        target_id = meta["target_id"]
        if target_id in missing_ui_canon_targets:
            request["required_context_reads"] = [
                path for path in request["required_context_reads"] if path not in required_ui_canon
            ]
        body_rel = (
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
            f"fake_child_binding_{request['request_id']}/task_return_body.md"
        )
        return_rel = (
            "ION/05_context/current/chatgpt_connector/task_returns/"
            f"{request['request_id']}_accepted_return.json"
        )
        machine_rel = (
            "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
            f"{request['request_id']}_machine_receipt.json"
        )
        _write(
            tmp_path,
            body_rel,
            (
                "### RESULT\n"
                f"verdict: accepted_candidate_repair_review_for_{target_id}\n"
                "### ION OPERATIONAL POSTURE\nproduction_authority: false\nlive_execution_authority: false\n"
            ),
        )
        _write(
            tmp_path,
            machine_rel,
            json.dumps({"accepted_for_carrier_intake": True}, indent=2, sort_keys=True) + "\n",
        )
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "accepted_for_carrier_intake": True,
                    "machine_receipt_path": machine_rel,
                    "template_action_proof_result": {"touched_paths": [body_rel]},
                    "work_request_id": request["request_id"],
                    "work_request_path": request_path,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        request["latest_return_packet_path"] = return_rel
        request["latest_task_return_machine_receipt_path"] = machine_rel
        request["return_packet_paths"] = [return_rel]
        _write(tmp_path, request_path, json.dumps(request, indent=2, sort_keys=True) + "\n")
    materialize_domain_weaver_projection(tmp_path)
    return "PCKT-DOMAIN-WEAVER-CHILD-DOMAIN-SPECIALIST-BINDING-REPAIR-FANIN-SETTLEMENT-20260602-ATTEMPT-001"


def test_domain_weaver_child_domain_specialist_binding_repair_fanin_queues_after_all_returns(
    tmp_path: Path,
):
    fanin_packet = _seed_domain_weaver_child_domain_specialist_binding_repair_accepted_returns(tmp_path)

    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    assert projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"] == fanin_packet
    assert projection["summary"]["child_domain_specialist_binding_repair_returns_complete"] is True
    assert projection["summary"]["child_domain_specialist_binding_repair_accepted_return_count"] == 8

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_child_domain_specialist_binding_repair_fanin_settlement",
            "packet_id": fanin_packet,
            "start_workers": False,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_FANIN_SETTLEMENT_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["accepted_return_count"] == 8
    assert result["summary"]["ui_canon_context_complete_count"] == 8
    assert result["summary"]["missing_ui_canon_context_request_count"] == 0
    assert result["summary"]["worker_started_count"] == 0

    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_FANIN_SETTLEMENT_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    request = json.loads((tmp_path / ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8"))
    required_ui_canon = {path.as_posix() for path in DOMAIN_WEAVER_UI_CANON_CONTEXT_PATHS}
    assert request["request_kind"] == "domain_weaver_child_domain_specialist_binding_repair_fanin_settlement"
    assert request["agent_role"] == "role.nemesis"
    assert request["supporting_roles"] == ["role.steward", "role.scribe", "affected_domain_owners"]
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert required_ui_canon.issubset(set(request["required_context_reads"]))
    settlement = request["domain_weaver_child_domain_specialist_binding_repair_fanin_settlement"]
    assert settlement["expected_return_count"] == 8
    assert settlement["accepted_return_count"] == 8
    assert settlement["ui_canon_context_complete_count"] == 8
    assert settlement["missing_ui_canon_context_request_count"] == 0
    assert len(settlement["accepted_returns"]) == 8
    for record in settlement["accepted_returns"]:
        assert record["request_path"] in request["required_context_reads"]
        assert record["return_path"] in request["required_context_reads"]
        assert record["task_return_body_path"] in request["required_context_reads"]
        assert record["ui_canon_context_complete"] is True
    assert request["production_authority"] is False
    assert request["live_execution_authority"] is False
    assert request["accepted_state_authority"] is False
    assert request["secrets_authority"] is False


def test_domain_weaver_child_domain_specialist_binding_repair_fanin_flags_prepatch_ui_canon_gaps(
    tmp_path: Path,
):
    missing_targets = {"domain.archaeology_drift_watch_canon_registry_candidate", "JOC_UI_CANON_STEWARD"}
    fanin_packet = _seed_domain_weaver_child_domain_specialist_binding_repair_accepted_returns(
        tmp_path,
        missing_ui_canon_targets=missing_targets,
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_child_domain_specialist_binding_repair_fanin_settlement",
            "packet_id": fanin_packet,
            "start_workers": False,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["accepted_return_count"] == 8
    assert result["summary"]["ui_canon_context_complete_count"] == 6
    assert result["summary"]["missing_ui_canon_context_request_count"] == 2
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    settlement = request["domain_weaver_child_domain_specialist_binding_repair_fanin_settlement"]
    missing_records = settlement["missing_ui_canon_context_records"]
    assert {row["target_id"] for row in missing_records} == missing_targets
    assert settlement["missing_ui_canon_context_request_count"] == 2
    assert len(settlement["missing_ui_canon_context_request_ids"]) == 2
    assert settlement["required_verdict"] == "binding_repair_fanin_settlement_or_reissue_stop_condition"
    assert all(row["missing_ui_canon_context_count"] == len(DOMAIN_WEAVER_UI_CANON_CONTEXT_PATHS) for row in missing_records)
    for record in settlement["accepted_returns"]:
        if record["target_id"] in missing_targets:
            assert record["ui_canon_context_complete"] is False
            assert record["missing_ui_canon_context_count"] == len(DOMAIN_WEAVER_UI_CANON_CONTEXT_PATHS)
        else:
            assert record["ui_canon_context_complete"] is True


def _seed_domain_weaver_child_domain_specialist_binding_repair_fanin_settlement_return(
    tmp_path: Path,
) -> str:
    missing_targets = {"domain.archaeology_drift_watch_canon_registry_candidate", "JOC_UI_CANON_STEWARD"}
    fanin_packet = _seed_domain_weaver_child_domain_specialist_binding_repair_accepted_returns(
        tmp_path,
        missing_ui_canon_targets=missing_targets,
    )
    fanin_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_child_domain_specialist_binding_repair_fanin_settlement",
            "packet_id": fanin_packet,
            "start_workers": False,
        },
    )
    assert fanin_queue["ok"] is True
    request_path = fanin_queue["summary"]["work_request_paths"][0]
    request = json.loads((tmp_path / request_path).read_text(encoding="utf-8"))
    body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "fake_child_domain_specialist_binding_repair_fanin/task_return_body.md"
    )
    return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        "child_domain_specialist_binding_repair_fanin_return.json"
    )
    machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        "child_domain_specialist_binding_repair_fanin_machine_receipt.json"
    )
    reissue_packet = (
        "PCKT-DOMAIN-WEAVER-CHILD-DOMAIN-SPECIALIST-BINDING-REPAIR-UI-CANON-CONTEXT-REISSUE-"
        "20260602-ATTEMPT-001"
    )
    _write(
        tmp_path,
        body_rel,
        (
            "### RESULT\n"
            "verdict: candidate_fanin_settlement_complete_collection_not_implementation_ready_reissue_required\n"
            "implementation_ready_now: false\n"
            "### RECOMMENDED NEXT PACKET\n"
            f"{reissue_packet}\n"
            "Required verdict: ui_canon_context_debt_repaired_or_explicit_stop_condition_preserved\n"
            "### ION OPERATIONAL POSTURE\nproduction_authority: false\nlive_execution_authority: false\n"
        ),
    )
    _write(
        tmp_path,
        machine_rel,
        json.dumps({"accepted_for_carrier_intake": True}, indent=2, sort_keys=True) + "\n",
    )
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": machine_rel,
                "template_action_proof_result": {"touched_paths": [body_rel]},
                "work_request_id": request["request_id"],
                "work_request_path": request_path,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    request["latest_return_packet_path"] = return_rel
    request["latest_task_return_machine_receipt_path"] = machine_rel
    request["return_packet_paths"] = [return_rel]
    _write(tmp_path, request_path, json.dumps(request, indent=2, sort_keys=True) + "\n")
    materialize_domain_weaver_projection(tmp_path)
    return reissue_packet


def test_domain_weaver_child_domain_specialist_binding_repair_fanin_result_projects_ui_canon_reissue(
    tmp_path: Path,
):
    reissue_packet = _seed_domain_weaver_child_domain_specialist_binding_repair_fanin_settlement_return(tmp_path)

    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    assert (tmp_path / DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_FANIN_SETTLEMENT_RESULT_PATH).is_file()
    assert projection["summary"]["current_capability_class"] == (
        "approval_governed_child_domain_specialist_binding_repair_ui_canon_reissue_ready"
    )
    assert projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"] == reissue_packet
    assert projection["summary"]["child_domain_specialist_binding_repair_fanin_settlement_ready"] is True
    assert projection["summary"]["child_domain_specialist_binding_repair_ui_canon_reissue_required"] is True
    assert projection["summary"]["child_domain_specialist_binding_repair_missing_ui_canon_context_request_count"] == 2


def test_domain_weaver_child_domain_specialist_binding_repair_ui_canon_reissue_queues_and_starts(
    tmp_path: Path,
    monkeypatch,
):
    reissue_packet = _seed_domain_weaver_child_domain_specialist_binding_repair_fanin_settlement_return(tmp_path)

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": (
                    "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
                    f"{Path(request_path).stem}/run.json"
                ),
                "pid": 10000 + len(calls),
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_child_domain_specialist_binding_repair_ui_canon_context_reissue",
            "packet_id": reissue_packet,
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_UI_CANON_REISSUE_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["missing_ui_canon_context_request_count"] == 2
    assert result["summary"]["reissue_template_count"] == 2
    assert result["summary"]["queued_request_count"] == 2
    assert result["summary"]["queueable_start_request_count"] == 2
    assert result["summary"]["worker_start_attempt_count"] == 2
    assert result["summary"]["worker_started_count"] == 2
    assert len(calls) == 2

    required_ui_canon = {path.as_posix() for path in DOMAIN_WEAVER_UI_CANON_CONTEXT_PATHS}
    started_lanes = []
    for call in calls:
        assert call["start"] is True
        assert call["background"] is True
        request = json.loads((tmp_path / call["request_path"]).read_text(encoding="utf-8"))
        started_lanes.append(request["lane_id"])
        assert request["request_kind"] == "domain_weaver_child_domain_specialist_binding_repair_ui_canon_reissue"
        assert request["requested_model"] == "gpt-5.5"
        assert request["requested_reasoning_effort"] == "xhigh"
        assert required_ui_canon.issubset(set(request["required_context_reads"]))
        assert DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_FANIN_SETTLEMENT_RESULT_PATH.as_posix() in request[
            "required_context_reads"
        ]
        reissue = request["domain_weaver_child_domain_specialist_binding_repair_ui_canon_reissue"]
        assert reissue["missing_ui_canon_context_count"] == len(DOMAIN_WEAVER_UI_CANON_CONTEXT_PATHS)
        assert reissue["required_verdict"] == "ui_canon_context_debt_repaired_or_explicit_stop_condition_preserved"
        assert request["production_authority"] is False
        assert request["live_execution_authority"] is False
        assert request["accepted_state_authority"] is False
        assert request["secrets_authority"] is False

    assert sorted(started_lanes) == ["approval_governance_lane", "architecture_lane"]

    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_UI_CANON_REISSUE_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert ledger["queue_action"] == "queue_child_domain_specialist_binding_repair_ui_canon_context_reissue"
    assert ledger["summary"]["worker_started_count"] == 2
    assert ledger["authority"]["production_authority"] is False
    assert ledger["authority"]["live_execution_authority"] is False
    assert ledger["authority"]["accepted_state_authority"] is False
    assert ledger["authority"]["secrets_authority"] is False


def _seed_domain_weaver_child_domain_specialist_binding_repair_ui_canon_reissue_accepted_returns(
    tmp_path: Path,
) -> str:
    reissue_packet = _seed_domain_weaver_child_domain_specialist_binding_repair_fanin_settlement_return(tmp_path)
    reissue_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_child_domain_specialist_binding_repair_ui_canon_context_reissue",
            "packet_id": reissue_packet,
            "start_workers": False,
        },
    )
    assert reissue_queue["ok"] is True
    next_packet = (
        "PCKT-DOMAIN-WEAVER-CHILD-DOMAIN-SPECIALIST-BINDING-REPAIR-UI-CANON-REISSUE-FANIN-SETTLEMENT-"
        "20260602-ATTEMPT-001"
    )
    for request_path in reissue_queue["summary"]["work_request_paths"]:
        request = json.loads((tmp_path / request_path).read_text(encoding="utf-8"))
        body_rel = (
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
            f"fake_{request['request_id']}/task_return_body.md"
        )
        return_rel = (
            "ION/05_context/current/chatgpt_connector/task_returns/"
            f"{request['request_id']}_accepted_return.json"
        )
        machine_rel = (
            "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
            f"{request['request_id']}_machine_receipt.json"
        )
        _write(
            tmp_path,
            body_rel,
            (
                "### RESULT\n"
                "verdict: ui_canon_context_debt_repaired_for_candidate_evidence_only\n"
                "implementation_ready_now: false\n"
                "### RECOMMENDED NEXT PACKET\n"
                f"{next_packet}\n"
                "### ION OPERATIONAL POSTURE\nproduction_authority: false\nlive_execution_authority: false\n"
            ),
        )
        _write(
            tmp_path,
            machine_rel,
            json.dumps({"accepted_for_carrier_intake": True}, indent=2, sort_keys=True) + "\n",
        )
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "accepted_for_carrier_intake": True,
                    "machine_receipt_path": machine_rel,
                    "template_action_proof_result": {"touched_paths": [body_rel]},
                    "work_request_id": request["request_id"],
                    "work_request_path": request_path,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        request["latest_return_packet_path"] = return_rel
        request["latest_task_return_machine_receipt_path"] = machine_rel
        request["return_packet_paths"] = [return_rel]
        _write(tmp_path, request_path, json.dumps(request, indent=2, sort_keys=True) + "\n")
    materialize_domain_weaver_projection(tmp_path)
    return next_packet


def test_domain_weaver_child_domain_specialist_binding_repair_ui_canon_reissue_fanin_queues(
    tmp_path: Path,
):
    next_packet = _seed_domain_weaver_child_domain_specialist_binding_repair_ui_canon_reissue_accepted_returns(
        tmp_path
    )

    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    assert projection["summary"]["current_capability_class"] == (
        "approval_governed_child_domain_specialist_binding_repair_ui_canon_reissue_returns_complete"
    )
    assert projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"] == next_packet
    assert projection["summary"]["child_domain_specialist_binding_repair_ui_canon_reissue_returns_complete"] is True
    assert projection["summary"]["child_domain_specialist_binding_repair_ui_canon_reissue_accepted_return_count"] == 2

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_child_domain_specialist_binding_repair_ui_canon_reissue_fanin_settlement",
            "packet_id": next_packet,
            "start_workers": False,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_UI_CANON_REISSUE_FANIN_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["accepted_return_count"] == 2
    assert result["summary"]["settlement_accepted_return_count"] == 2
    assert result["summary"]["worker_started_count"] == 0
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    assert request["request_kind"] == "domain_weaver_child_domain_specialist_binding_repair_ui_canon_reissue_fanin_settlement"
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    settlement = request["domain_weaver_child_domain_specialist_binding_repair_ui_canon_reissue_fanin_settlement"]
    assert settlement["expected_return_count"] == 2
    assert settlement["accepted_return_count"] == 2
    assert len(settlement["accepted_returns"]) == 2
    assert request["production_authority"] is False
    assert request["live_execution_authority"] is False
    assert request["accepted_state_authority"] is False
    assert request["secrets_authority"] is False


def _seed_domain_weaver_child_domain_specialist_binding_repair_ui_canon_reissue_fanin_return(
    tmp_path: Path,
) -> str:
    fanin_packet = _seed_domain_weaver_child_domain_specialist_binding_repair_ui_canon_reissue_accepted_returns(
        tmp_path
    )
    queue_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_child_domain_specialist_binding_repair_ui_canon_reissue_fanin_settlement",
            "packet_id": fanin_packet,
            "start_workers": False,
        },
    )
    assert queue_result["ok"] is True
    request_path = queue_result["summary"]["work_request_paths"][0]
    request = json.loads((tmp_path / request_path).read_text(encoding="utf-8"))
    next_packet = (
        "PCKT-DOMAIN-WEAVER-CHILD-DOMAIN-SPECIALIST-BINDING-REPAIR-ACTIVE-BINDING-READINESS-GATE-"
        "20260602-ATTEMPT-001"
    )
    body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"fake_{request['request_id']}/task_return_body.md"
    )
    return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{request['request_id']}_accepted_return.json"
    )
    machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"{request['request_id']}_machine_receipt.json"
    )
    _write(
        tmp_path,
        body_rel,
        (
            "### RESULT\n"
            "verdict: ui_canon_reissue_fanin_settlement_complete_context_debt_repaired_candidate_only_implementation_not_ready\n"
            "The prior UI-canon context debt is repaired for candidate evidence.\n"
            "### IMPLEMENTATION READINESS GATE\n"
            "implementation_ready_now: false\n"
            "- Exact active specialist binding: fail. Activation ledger reports `exact_active_binding_count=0`.\n"
            "### BLOCKERS\n"
            "- EXACT_ACTIVE_BINDING_MISSING\n"
            "### RECOMMENDED NEXT PACKET\n"
            f"{next_packet}\n"
            "Required verdict: `exact_active_binding_ready_for_candidate_materialization_or_stop_classified`.\n"
            "### ION OPERATIONAL POSTURE\nproduction_authority: false\nlive_execution_authority: false\n"
        ),
    )
    _write(
        tmp_path,
        machine_rel,
        json.dumps({"accepted_for_carrier_intake": True}, indent=2, sort_keys=True) + "\n",
    )
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": machine_rel,
                "template_action_proof_result": {"touched_paths": [body_rel]},
                "work_request_id": request["request_id"],
                "work_request_path": request_path,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    request["latest_return_packet_path"] = return_rel
    request["latest_task_return_machine_receipt_path"] = machine_rel
    request["return_packet_paths"] = [return_rel]
    _write(tmp_path, request_path, json.dumps(request, indent=2, sort_keys=True) + "\n")
    materialize_domain_weaver_projection(tmp_path)
    return next_packet


def test_domain_weaver_child_domain_specialist_binding_repair_ui_canon_reissue_fanin_result_advances_projection(
    tmp_path: Path,
):
    next_packet = _seed_domain_weaver_child_domain_specialist_binding_repair_ui_canon_reissue_fanin_return(
        tmp_path
    )

    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    assert projection["summary"]["current_capability_class"] == (
        "approval_governed_child_domain_specialist_binding_repair_active_binding_readiness_gate_ready"
    )
    assert projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"] == next_packet
    assert projection["summary"]["child_domain_specialist_binding_repair_ui_canon_reissue_fanin_settled"] is True
    assert projection["summary"]["child_domain_specialist_binding_repair_ui_canon_reissue_fanin_next_packet_id"] == (
        next_packet
    )
    assert projection["summary"]["child_domain_specialist_binding_repair_implementation_ready_now"] is False
    assert projection["summary"]["child_domain_specialist_binding_repair_exact_active_binding_ready"] is False
    fanin_result = projection["child_domain_specialist_binding_repair_ui_canon_reissue_fanin"]
    assert fanin_result["status"] == "child_domain_specialist_binding_repair_ui_canon_reissue_fanin_settled"
    assert fanin_result["summary"]["accepted_return_count"] == 2
    assert fanin_result["summary"]["ui_canon_context_debt_repaired"] is True
    assert fanin_result["summary"]["recommended_next_packet_id"] == next_packet
    assert (
        tmp_path / DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_UI_CANON_REISSUE_FANIN_RESULT_PATH
    ).is_file()


def test_domain_weaver_child_domain_specialist_binding_repair_active_binding_readiness_gate_queues(
    tmp_path: Path,
):
    next_packet = _seed_domain_weaver_child_domain_specialist_binding_repair_ui_canon_reissue_fanin_return(
        tmp_path
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_child_domain_specialist_binding_repair_active_binding_readiness_gate",
            "packet_id": next_packet,
            "start_workers": False,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_ACTIVE_BINDING_READINESS_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["reissue_fanin_ready"] is True
    assert result["summary"]["implementation_ready_now"] is False
    assert result["summary"]["exact_active_binding_ready"] is False
    assert result["summary"]["worker_started_count"] == 0
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    assert request["request_kind"] == (
        "domain_weaver_child_domain_specialist_binding_repair_active_binding_readiness_gate"
    )
    assert request["agent_role"] == "role.steward"
    assert request["supporting_roles"] == ["role.nemesis", "role.scribe"]
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    gate = request["domain_weaver_child_domain_specialist_binding_repair_active_binding_readiness_gate"]
    assert gate["required_verdict"] == "exact_active_binding_ready_for_candidate_materialization_or_stop_classified"
    assert gate["implementation_authority"] is False
    assert request["production_authority"] is False
    assert request["live_execution_authority"] is False
    assert request["accepted_state_authority"] is False
    assert request["secrets_authority"] is False


def _seed_domain_weaver_child_domain_specialist_binding_repair_active_binding_readiness_return(
    tmp_path: Path,
) -> str:
    readiness_packet = (
        _seed_domain_weaver_child_domain_specialist_binding_repair_ui_canon_reissue_fanin_return(tmp_path)
    )
    queue_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_child_domain_specialist_binding_repair_active_binding_readiness_gate",
            "packet_id": readiness_packet,
            "start_workers": False,
        },
    )
    assert queue_result["ok"] is True
    request_path = queue_result["summary"]["work_request_paths"][0]
    request = json.loads((tmp_path / request_path).read_text(encoding="utf-8"))
    next_packet = (
        "PCKT-DOMAIN-WEAVER-CHILD-DOMAIN-SPECIALIST-BINDING-REPAIR-EXACT-ACTIVE-BINDING-REMEDIATION-"
        "20260602-ATTEMPT-001"
    )
    body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"fake_{request['request_id']}/task_return_body.md"
    )
    return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{request['request_id']}_accepted_return.json"
    )
    machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"{request['request_id']}_machine_receipt.json"
    )
    _write(
        tmp_path,
        body_rel,
        (
            "### RESULT\n"
            "verdict: exact_active_binding_not_ready_stop_classified\n"
            "### ACTIVE BINDING READINESS GATE\n"
            "gate_verdict: stop_classified_missing_exact_active_specialist_bindings\n"
            "candidate_active_binding_materialization_ready: false\n"
            "implementation_ready_now: false\n"
            "exact_active_binding_count: 0\n"
            "delegated_active_binding_count: 1\n"
            "candidate_boot_only_count: 5\n"
            "### RECOMMENDED NEXT PACKET\n"
            f"{next_packet}\n"
            "### ION OPERATIONAL POSTURE\nproduction_authority: false\nlive_execution_authority: false\n"
        ),
    )
    _write(
        tmp_path,
        machine_rel,
        json.dumps({"accepted_for_carrier_intake": True}, indent=2, sort_keys=True) + "\n",
    )
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": machine_rel,
                "template_action_proof_result": {"touched_paths": [body_rel]},
                "work_request_id": request["request_id"],
                "work_request_path": request_path,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    request["latest_return_packet_path"] = return_rel
    request["latest_task_return_machine_receipt_path"] = machine_rel
    request["return_packet_paths"] = [return_rel]
    _write(tmp_path, request_path, json.dumps(request, indent=2, sort_keys=True) + "\n")
    materialize_domain_weaver_projection(tmp_path)
    return next_packet


def test_domain_weaver_child_domain_specialist_binding_repair_active_binding_readiness_result_advances_projection(
    tmp_path: Path,
):
    next_packet = _seed_domain_weaver_child_domain_specialist_binding_repair_active_binding_readiness_return(
        tmp_path
    )

    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    assert projection["summary"]["current_capability_class"] == (
        "approval_governed_child_domain_specialist_binding_repair_exact_active_binding_remediation_ready"
    )
    assert projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"] == next_packet
    assert projection["summary"]["child_domain_specialist_binding_repair_active_binding_readiness_settled"] is True
    assert projection["summary"]["child_domain_specialist_binding_repair_active_binding_readiness_next_packet_id"] == (
        next_packet
    )
    assert projection["summary"]["child_domain_specialist_binding_repair_active_binding_materialization_ready"] is False
    assert (
        projection["summary"]["child_domain_specialist_binding_repair_stop_classified_missing_exact_active_bindings"]
        is True
    )
    result = projection["child_domain_specialist_binding_repair_active_binding_readiness"]
    assert result["summary"]["exact_active_binding_count"] == 0
    assert result["summary"]["delegated_active_binding_count"] == 1
    assert result["summary"]["candidate_boot_only_count"] == 5
    assert (
        tmp_path / DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_ACTIVE_BINDING_READINESS_RESULT_PATH
    ).is_file()


def test_domain_weaver_child_domain_specialist_binding_repair_exact_active_binding_remediation_queues(
    tmp_path: Path,
):
    next_packet = _seed_domain_weaver_child_domain_specialist_binding_repair_active_binding_readiness_return(
        tmp_path
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_child_domain_specialist_binding_repair_exact_active_binding_remediation",
            "packet_id": next_packet,
            "start_workers": False,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_EXACT_ACTIVE_BINDING_REMEDIATION_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["active_binding_readiness_ready"] is True
    assert result["summary"]["candidate_active_binding_materialization_ready"] is False
    assert result["summary"]["stop_classified_missing_exact_active_bindings"] is True
    assert result["summary"]["worker_started_count"] == 0
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    assert request["request_kind"] == (
        "domain_weaver_child_domain_specialist_binding_repair_exact_active_binding_remediation"
    )
    assert request["agent_role"] == "role.steward"
    assert request["supporting_roles"] == ["role.nemesis", "role.scribe"]
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    remediation = request["domain_weaver_child_domain_specialist_binding_repair_exact_active_binding_remediation"]
    assert remediation["required_verdict"] == "exact_active_binding_remediation_plan_or_materialization_stop_condition"
    assert remediation["exact_active_binding_count"] == 0
    assert remediation["delegated_active_binding_count"] == 1
    assert remediation["candidate_boot_only_count"] == 5
    assert remediation["implementation_authority"] is False
    assert request["production_authority"] is False
    assert request["live_execution_authority"] is False
    assert request["accepted_state_authority"] is False
    assert request["secrets_authority"] is False


def _seed_domain_weaver_child_domain_specialist_binding_repair_exact_active_binding_remediation_return(
    tmp_path: Path,
) -> str:
    remediation_packet = (
        _seed_domain_weaver_child_domain_specialist_binding_repair_active_binding_readiness_return(tmp_path)
    )
    queue_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_child_domain_specialist_binding_repair_exact_active_binding_remediation",
            "packet_id": remediation_packet,
            "start_workers": False,
        },
    )
    assert queue_result["ok"] is True
    request_path = queue_result["summary"]["work_request_paths"][0]
    request = json.loads((tmp_path / request_path).read_text(encoding="utf-8"))
    next_packet = "PCKT-DOMAIN-WEAVER-EXACT-ACTIVE-SPECIALIST-BINDING-PROOF-MATRIX-20260602-ATTEMPT-001"
    body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"fake_{request['request_id']}/task_return_body.md"
    )
    return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{request['request_id']}_accepted_return.json"
    )
    machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"{request['request_id']}_machine_receipt.json"
    )
    _write(
        tmp_path,
        body_rel,
        (
            "### RESULT\n"
            "verdict: stop_current_materialization_and_prepare_exact_active_binding_proof_matrix\n"
            "### EXACT ACTIVE BINDING REMEDIATION\n"
            "decision: stop_condition_with_candidate_remediation_plan\n"
            "candidate_materialization_plan_ready_now: false\n"
            "reissue_required_now: false\n"
            "stop_condition: missing_exact_active_child_domain_specialist_bindings\n"
            "### RECOMMENDED NEXT PACKET\n"
            f"{next_packet}\n"
            "### ION OPERATIONAL POSTURE\nproduction_authority: false\nlive_execution_authority: false\n"
        ),
    )
    _write(
        tmp_path,
        machine_rel,
        json.dumps({"accepted_for_carrier_intake": True}, indent=2, sort_keys=True) + "\n",
    )
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": machine_rel,
                "template_action_proof_result": {"touched_paths": [body_rel]},
                "work_request_id": request["request_id"],
                "work_request_path": request_path,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    request["latest_return_packet_path"] = return_rel
    request["latest_task_return_machine_receipt_path"] = machine_rel
    request["return_packet_paths"] = [return_rel]
    _write(tmp_path, request_path, json.dumps(request, indent=2, sort_keys=True) + "\n")
    materialize_domain_weaver_projection(tmp_path)
    return next_packet


def test_domain_weaver_child_domain_specialist_binding_repair_exact_active_binding_remediation_result_advances_projection(
    tmp_path: Path,
):
    next_packet = _seed_domain_weaver_child_domain_specialist_binding_repair_exact_active_binding_remediation_return(
        tmp_path
    )

    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    assert projection["summary"]["current_capability_class"] == (
        "approval_governed_exact_active_specialist_binding_proof_matrix_ready"
    )
    assert projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"] == next_packet
    assert projection["summary"]["child_domain_specialist_binding_repair_exact_active_binding_remediation_settled"] is True
    assert (
        projection["summary"]["child_domain_specialist_binding_repair_exact_active_binding_remediation_next_packet_id"]
        == next_packet
    )
    assert projection["summary"]["child_domain_specialist_binding_repair_candidate_materialization_plan_ready_now"] is False
    assert projection["summary"]["child_domain_specialist_binding_repair_exact_binding_stop_condition_active"] is True
    result = projection["child_domain_specialist_binding_repair_exact_active_binding_remediation"]
    assert result["summary"]["recommended_next_packet_id"] == next_packet
    assert result["summary"]["stop_condition_active"] is True
    assert (
        tmp_path / DOMAIN_WEAVER_CHILD_DOMAIN_SPECIALIST_BINDING_REPAIR_EXACT_ACTIVE_BINDING_REMEDIATION_RESULT_PATH
    ).is_file()


def test_domain_weaver_exact_active_specialist_binding_proof_matrix_queues(
    tmp_path: Path,
):
    next_packet = _seed_domain_weaver_child_domain_specialist_binding_repair_exact_active_binding_remediation_return(
        tmp_path
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_exact_active_specialist_binding_proof_matrix",
            "packet_id": next_packet,
            "start_workers": False,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_PROOF_MATRIX_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["remediation_result_ready"] is True
    assert result["summary"]["candidate_materialization_plan_ready_now"] is False
    assert result["summary"]["stop_condition_active"] is True
    assert result["summary"]["worker_started_count"] == 0
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    assert request["request_kind"] == "domain_weaver_exact_active_specialist_binding_proof_matrix"
    assert request["agent_role"] == "role.steward"
    assert request["supporting_roles"] == ["role.nemesis", "role.scribe"]
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    proof_matrix = request["domain_weaver_exact_active_specialist_binding_proof_matrix"]
    assert proof_matrix["required_verdict"] == "exact_active_specialist_binding_matrix_ready_or_stop_classified"
    assert len(proof_matrix["required_specialist_ids"]) == 6
    assert "COMPONENT_BUILDER" in proof_matrix["required_specialist_ids"]
    assert proof_matrix["implementation_authority"] is False
    assert proof_matrix["worker_start_allowed_by_this_packet"] is False
    assert request["production_authority"] is False
    assert request["live_execution_authority"] is False
    assert request["accepted_state_authority"] is False
    assert request["secrets_authority"] is False


def _seed_domain_weaver_exact_active_specialist_binding_proof_matrix_return(
    tmp_path: Path,
) -> str:
    proof_matrix_packet = _seed_domain_weaver_child_domain_specialist_binding_repair_exact_active_binding_remediation_return(
        tmp_path
    )
    queue_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_exact_active_specialist_binding_proof_matrix",
            "packet_id": proof_matrix_packet,
            "start_workers": False,
        },
    )
    assert queue_result["ok"] is True
    request_path = queue_result["summary"]["work_request_paths"][0]
    request = json.loads((tmp_path / request_path).read_text(encoding="utf-8"))
    next_packet = (
        "PCKT-DOMAIN-WEAVER-EXACT-ACTIVE-SPECIALIST-BINDING-AUTHORITY-SETTLEMENT-"
        "20260602-ATTEMPT-001"
    )
    body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"fake_{request['request_id']}/task_return_body.md"
    )
    return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{request['request_id']}_accepted_return.json"
    )
    machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"{request['request_id']}_machine_receipt.json"
    )
    _write(
        tmp_path,
        body_rel,
        (
            "### CONTEXT PROOF\ncontext ready\n"
            "### TEMPLATE ACTION PROOF\n"
            "template_id: ion.template.autonomous_loop.local_worker.v1\n"
            "action_id: codex_queue_runner_process_once\n"
            "result: stop_classified_candidate_exact_active_specialist_binding_matrix_ready\n"
            "touched_paths:\n  - fake\n"
            "### VALIDATION\nvalidated\n"
            "### RESULT\n"
            "verdict: stop_classified_exact_active_specialist_binding_matrix_ready\n"
            "exact_active_specialist_binding_matrix_ready: false\n"
            "candidate_materialization_ready: false\n"
            "implementation_ready_now: false\n"
            "### EXACT ACTIVE SPECIALIST BINDING PROOF MATRIX\n"
            "Matrix verdict: STOP_CLASSIFIED_MISSING_EXACT_ACTIVE_SPECIALIST_BINDINGS\n"
            "five candidate-boot-only rows remain. exact_active_binding_count=0.\n"
            "COMPONENT_BUILDER is delegated through role.mason, not exact active.\n"
            "### BLOCKERS\n"
            "- EXACT_ACTIVE_BINDING_MISSING\n"
            "- DELEGATED_BINDING_NOT_EXACT\n"
            "- DELEGATED_SUBSTITUTION_NOT_SETTLED\n"
            "### RECOMMENDED NEXT PACKET\n"
            f"{next_packet}\n"
            "### ION OPERATIONAL POSTURE\nproduction_authority: false\nlive_execution_authority: false\n"
            "### WORKLOAD DIFF\nNo source files changed.\n"
        ),
    )
    _write(
        tmp_path,
        machine_rel,
        json.dumps({"accepted_for_carrier_intake": True}, indent=2, sort_keys=True) + "\n",
    )
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": machine_rel,
                "template_action_proof_result": {"touched_paths": [body_rel]},
                "work_request_id": request["request_id"],
                "work_request_path": request_path,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    request["latest_return_packet_path"] = return_rel
    request["latest_task_return_machine_receipt_path"] = machine_rel
    request["return_packet_paths"] = [return_rel]
    _write(tmp_path, request_path, json.dumps(request, indent=2, sort_keys=True) + "\n")
    materialize_domain_weaver_projection(tmp_path)
    return next_packet


def test_domain_weaver_exact_active_specialist_binding_proof_matrix_result_advances_projection(
    tmp_path: Path,
):
    next_packet = _seed_domain_weaver_exact_active_specialist_binding_proof_matrix_return(tmp_path)

    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    assert projection["summary"]["current_capability_class"] == (
        "approval_governed_exact_active_specialist_binding_authority_settlement_ready"
    )
    assert projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"] == next_packet
    assert projection["summary"]["exact_active_specialist_binding_proof_matrix_settled"] is True
    assert projection["summary"]["exact_active_specialist_binding_proof_matrix_next_packet_id"] == next_packet
    assert projection["summary"]["exact_active_specialist_binding_matrix_ready"] is False
    assert projection["summary"]["exact_active_specialist_binding_stop_classified"] is True
    assert projection["summary"]["exact_active_specialist_binding_count"] == 0
    assert projection["summary"]["exact_active_specialist_binding_delegated_substitution_settled"] is False
    result = projection["exact_active_specialist_binding_proof_matrix"]
    assert result["summary"]["recommended_next_packet_id"] == next_packet
    assert result["summary"]["delegated_binding_not_exact"] is True
    assert (
        tmp_path / DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_PROOF_MATRIX_RESULT_PATH
    ).is_file()


def test_domain_weaver_exact_active_specialist_binding_authority_settlement_queues(
    tmp_path: Path,
):
    next_packet = _seed_domain_weaver_exact_active_specialist_binding_proof_matrix_return(tmp_path)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_exact_active_specialist_binding_authority_settlement",
            "packet_id": next_packet,
            "start_workers": False,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_AUTHORITY_SETTLEMENT_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["proof_matrix_result_ready"] is True
    assert result["summary"]["exact_active_specialist_binding_matrix_ready"] is False
    assert result["summary"]["stop_classified_missing_exact_active_bindings"] is True
    assert result["summary"]["delegated_substitution_settled"] is False
    assert result["summary"]["worker_started_count"] == 0
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    assert request["request_kind"] == "domain_weaver_exact_active_specialist_binding_authority_settlement"
    assert request["agent_role"] == "role.steward"
    assert request["supporting_roles"] == ["role.nemesis", "role.scribe"]
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    settlement = request["domain_weaver_exact_active_specialist_binding_authority_settlement"]
    assert settlement["required_verdict"] == "exact_active_binding_authority_settlement_or_stop_condition"
    assert len(settlement["required_specialist_ids"]) == 6
    assert settlement["active_registry_write_authority"] is False
    assert settlement["implementation_authority"] is False
    assert settlement["worker_start_allowed_by_this_packet"] is False
    assert request["production_authority"] is False
    assert request["live_execution_authority"] is False
    assert request["accepted_state_authority"] is False
    assert request["secrets_authority"] is False


def _seed_domain_weaver_exact_active_specialist_binding_authority_settlement_return(
    tmp_path: Path,
) -> str:
    settlement_packet = _seed_domain_weaver_exact_active_specialist_binding_proof_matrix_return(tmp_path)
    queue_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_exact_active_specialist_binding_authority_settlement",
            "packet_id": settlement_packet,
            "start_workers": False,
        },
    )
    assert queue_result["ok"] is True
    request_path = queue_result["summary"]["work_request_paths"][0]
    request = json.loads((tmp_path / request_path).read_text(encoding="utf-8"))
    next_packet = (
        "PCKT-DOMAIN-WEAVER-EXACT-ACTIVE-SPECIALIST-BINDING-MATERIALIZATION-GATE-REPAIR-"
        "20260602-ATTEMPT-001"
    )
    body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"fake_{request['request_id']}/task_return_body.md"
    )
    return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{request['request_id']}_accepted_return.json"
    )
    machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"{request['request_id']}_machine_receipt.json"
    )
    _write(
        tmp_path,
        body_rel,
        (
            "### CONTEXT PROOF\ncontext ready\n"
            "### TEMPLATE ACTION PROOF\n"
            "template_id: ion.template.autonomous_loop.local_worker.v1\n"
            "action_id: codex_queue_runner_process_once\n"
            "result: stop_classified_exact_active_binding_authority_settlement\n"
            "touched_paths:\n  - fake\n"
            "### VALIDATION\nvalidated\n"
            "### RESULT\n"
            "verdict: STOP_CLASSIFIED_MISSING_EXACT_ACTIVE_SPECIALIST_BINDINGS\n"
            "exact_active_binding_authority_settlement_ready: false\n"
            "candidate_materialization_ready: false\n"
            "implementation_ready_now: false\n"
            "### EXACT ACTIVE SPECIALIST BINDING AUTHORITY SETTLEMENT\n"
            "Authority settlement verdict: STOP_CLASSIFIED_MISSING_EXACT_ACTIVE_SPECIALIST_BINDINGS\n"
            "exact_active_binding_count=0\n"
            "### DELEGATED SUBSTITUTION SETTLEMENT\n"
            "delegated_substitution_settled: false\n"
            "delegated_substitution_verdict: DELEGATED_SUBSTITUTION_NOT_ACCEPTED_FOR_THIS_MATERIALIZATION_GATE\n"
            "### BLOCKERS\n"
            "- EXACT_ACTIVE_BINDING_MISSING\n"
            "- DELEGATED_SUBSTITUTION_NOT_SETTLED\n"
            "### RECOMMENDED NEXT PACKET\n"
            f"{next_packet}\n"
            "### ION OPERATIONAL POSTURE\nproduction_authority: false\nlive_execution_authority: false\n"
            "### WORKLOAD DIFF\nNo source files changed.\n"
        ),
    )
    _write(
        tmp_path,
        machine_rel,
        json.dumps({"accepted_for_carrier_intake": True}, indent=2, sort_keys=True) + "\n",
    )
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": machine_rel,
                "template_action_proof_result": {"touched_paths": [body_rel]},
                "work_request_id": request["request_id"],
                "work_request_path": request_path,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    request["latest_return_packet_path"] = return_rel
    request["latest_task_return_machine_receipt_path"] = machine_rel
    request["return_packet_paths"] = [return_rel]
    _write(tmp_path, request_path, json.dumps(request, indent=2, sort_keys=True) + "\n")
    materialize_domain_weaver_projection(tmp_path)
    return next_packet


def test_domain_weaver_exact_active_specialist_binding_authority_settlement_result_advances_projection(
    tmp_path: Path,
):
    next_packet = _seed_domain_weaver_exact_active_specialist_binding_authority_settlement_return(
        tmp_path
    )

    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    assert projection["summary"]["current_capability_class"] == (
        "approval_governed_exact_active_specialist_binding_materialization_gate_repair_ready"
    )
    assert projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"] == next_packet
    assert projection["summary"]["exact_active_specialist_binding_authority_settlement_settled"] is True
    assert (
        projection["summary"]["exact_active_specialist_binding_materialization_gate_repair_next_packet_id"]
        == next_packet
    )
    assert projection["summary"]["exact_active_binding_authority_settlement_ready"] is False
    assert projection["summary"]["exact_active_binding_authority_settlement_stop_classified"] is True
    assert projection["summary"]["exact_active_binding_authority_settlement_delegated_substitution_settled"] is False
    result = projection["exact_active_specialist_binding_authority_settlement"]
    assert result["summary"]["recommended_next_packet_id"] == next_packet
    assert result["summary"]["delegated_substitution_not_accepted"] is True
    assert (
        tmp_path / DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_AUTHORITY_SETTLEMENT_RESULT_PATH
    ).is_file()


def test_domain_weaver_exact_active_specialist_binding_materialization_gate_repair_queues(
    tmp_path: Path,
):
    next_packet = _seed_domain_weaver_exact_active_specialist_binding_authority_settlement_return(
        tmp_path
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_exact_active_specialist_binding_materialization_gate_repair",
            "packet_id": next_packet,
            "start_workers": False,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_MATERIALIZATION_GATE_REPAIR_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["authority_settlement_result_ready"] is True
    assert result["summary"]["exact_active_binding_authority_settlement_ready"] is False
    assert result["summary"]["stop_classified_missing_exact_active_bindings"] is True
    assert result["summary"]["delegated_substitution_settled"] is False
    assert result["summary"]["worker_started_count"] == 0
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    assert request["request_kind"] == "domain_weaver_exact_active_specialist_binding_materialization_gate_repair"
    assert request["agent_role"] == "role.steward"
    assert request["supporting_roles"] == ["role.nemesis", "role.scribe"]
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    repair = request["domain_weaver_exact_active_specialist_binding_materialization_gate_repair"]
    assert repair["required_verdict"] == "materialization_gate_repair_plan_or_exact_active_binding_proof"
    assert len(repair["required_specialist_ids"]) == 6
    assert repair["active_registry_write_authority"] is False
    assert repair["implementation_authority"] is False
    assert repair["worker_start_allowed_by_this_packet"] is False
    assert request["production_authority"] is False
    assert request["live_execution_authority"] is False
    assert request["accepted_state_authority"] is False
    assert request["secrets_authority"] is False


def _seed_domain_weaver_exact_active_specialist_binding_materialization_gate_repair_return(
    tmp_path: Path,
) -> str:
    repair_packet = _seed_domain_weaver_exact_active_specialist_binding_authority_settlement_return(
        tmp_path
    )
    queue_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_exact_active_specialist_binding_materialization_gate_repair",
            "packet_id": repair_packet,
            "start_workers": False,
        },
    )
    assert queue_result["ok"] is True
    request_path = queue_result["summary"]["work_request_paths"][0]
    request = json.loads((tmp_path / request_path).read_text(encoding="utf-8"))
    next_packet = (
        "PCKT-DOMAIN-WEAVER-EXACT-ACTIVE-SPECIALIST-BINDING-"
        "ACTIVATION-OR-DELEGATED-SUBSTITUTION-REPAIR-20260602-ATTEMPT-001"
    )
    body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"fake_{request['request_id']}/task_return_body.md"
    )
    return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{request['request_id']}_accepted_return.json"
    )
    machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"{request['request_id']}_machine_receipt.json"
    )
    _write(
        tmp_path,
        body_rel,
        (
            "### CONTEXT PROOF\ncontext ready\n"
            "### TEMPLATE ACTION PROOF\n"
            "template_id: ion.template.autonomous_loop.local_worker.v1\n"
            "action_id: codex_queue_runner_process_once\n"
            "result: stop_classified_exact_active_binding_materialization_gate_repair\n"
            "touched_paths:\n  - fake\n"
            "### VALIDATION\nvalidated\n"
            "### RESULT\n"
            "verdict: STOP_CLASSIFIED_MISSING_EXACT_ACTIVE_SPECIALIST_BINDINGS\n"
            "candidate_only: true\n"
            "materialization_gate_repaired: true\n"
            "materialization_ready: false\n"
            "exact_active_binding_count: 0\n"
            "candidate_boot_only_count: 5\n"
            "delegated_active_binding_count: 1\n"
            "delegated_substitution_settled: false\n"
            "### MATERIALIZATION GATE REPAIR\n"
            "candidate_boot_only is not active binding proof. next_packet_required: true\n"
            "### EXACT ACTIVE BINDING REPAIR PLAN\n"
            "All five UI specialists remain candidate boot only; COMPONENT_BUILDER is delegated but not exact.\n"
            "### DELEGATED SUBSTITUTION GATE\n"
            "delegated_substitution_verdict: DELEGATED_SUBSTITUTION_NOT_ACCEPTED_FOR_THIS_MATERIALIZATION_GATE\n"
            "### BLOCKERS\n"
            "- EXACT_ACTIVE_BINDING_MISSING\n"
            "- CANDIDATE_BOOT_ONLY_NOT_ACTIVE_BINDING\n"
            "- DELEGATED_BINDING_NOT_EXACT\n"
            "- DELEGATED_SUBSTITUTION_NOT_SETTLED\n"
            "### RECOMMENDED NEXT PACKET\n"
            f"{next_packet}\n"
            "### ION OPERATIONAL POSTURE\nproduction_authority: false\nlive_execution_authority: false\n"
            "### WORKLOAD DIFF\nNo source files changed.\n"
        ),
    )
    _write(
        tmp_path,
        machine_rel,
        json.dumps({"accepted_for_carrier_intake": True}, indent=2, sort_keys=True) + "\n",
    )
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": machine_rel,
                "template_action_proof_result": {"touched_paths": [body_rel]},
                "work_request_id": request["request_id"],
                "work_request_path": request_path,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    request["latest_return_packet_path"] = return_rel
    request["latest_task_return_machine_receipt_path"] = machine_rel
    request["return_packet_paths"] = [return_rel]
    _write(tmp_path, request_path, json.dumps(request, indent=2, sort_keys=True) + "\n")
    materialize_domain_weaver_projection(tmp_path)
    return next_packet


def test_domain_weaver_exact_active_specialist_binding_materialization_gate_repair_result_advances_projection(
    tmp_path: Path,
):
    next_packet = _seed_domain_weaver_exact_active_specialist_binding_materialization_gate_repair_return(
        tmp_path
    )

    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    assert projection["summary"]["current_capability_class"] == (
        "approval_governed_exact_active_specialist_binding_activation_or_delegated_substitution_repair_ready"
    )
    assert projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"] == next_packet
    assert projection["summary"]["exact_active_specialist_binding_materialization_gate_repair_settled"] is True
    assert (
        projection["summary"][
            "exact_active_specialist_binding_activation_or_delegated_substitution_repair_next_packet_id"
        ]
        == next_packet
    )
    assert projection["summary"]["exact_active_binding_materialization_gate_repaired"] is True
    assert projection["summary"]["exact_active_binding_materialization_ready"] is False
    assert projection["summary"]["exact_active_binding_activation_or_delegated_substitution_repair_required"] is True
    assert projection["summary"]["exact_active_binding_materialization_gate_repair_stop_classified"] is True
    assert projection["summary"]["exact_active_binding_materialization_gate_repair_delegated_substitution_settled"] is False
    result = projection["exact_active_specialist_binding_materialization_gate_repair"]
    assert result["summary"]["recommended_next_packet_id"] == next_packet
    assert result["summary"]["exact_active_binding_count"] == 0
    assert result["summary"]["candidate_boot_only_count"] == 5
    assert result["summary"]["delegated_active_binding_count"] == 1
    assert result["summary"]["candidate_boot_only_not_active_binding"] is True
    assert result["summary"]["delegated_binding_not_exact"] is True
    assert (
        tmp_path / DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_MATERIALIZATION_GATE_REPAIR_RESULT_PATH
    ).is_file()


def test_domain_weaver_exact_active_specialist_binding_activation_or_delegated_substitution_repair_queues(
    tmp_path: Path,
):
    next_packet = _seed_domain_weaver_exact_active_specialist_binding_materialization_gate_repair_return(
        tmp_path
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_exact_active_specialist_binding_activation_or_delegated_substitution_repair",
            "packet_id": next_packet,
            "start_workers": False,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_ACTIVATION_OR_DELEGATED_SUBSTITUTION_REPAIR_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["materialization_gate_repair_result_ready"] is True
    assert result["summary"]["materialization_gate_repaired"] is True
    assert result["summary"]["materialization_ready"] is False
    assert result["summary"]["activation_or_delegated_substitution_repair_required"] is True
    assert result["summary"]["exact_active_binding_count"] == 0
    assert result["summary"]["delegated_substitution_settled"] is False
    assert result["summary"]["worker_started_count"] == 0
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    assert request["request_kind"] == (
        "domain_weaver_exact_active_specialist_binding_activation_or_delegated_substitution_repair"
    )
    assert request["agent_role"] == "role.steward"
    assert request["supporting_roles"] == ["role.nemesis", "role.scribe"]
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    repair = request[
        "domain_weaver_exact_active_specialist_binding_activation_or_delegated_substitution_repair"
    ]
    assert repair["required_verdict"] == "activation_or_delegated_substitution_repair_or_stop_condition"
    assert len(repair["required_specialist_ids"]) == 6
    assert repair["active_registry_write_authority"] is False
    assert repair["implementation_authority"] is False
    assert repair["worker_start_allowed_by_this_packet"] is False
    assert repair["queue_fanout_authority"] is False
    assert request["production_authority"] is False
    assert request["live_execution_authority"] is False
    assert request["accepted_state_authority"] is False
    assert request["secrets_authority"] is False


def _seed_domain_weaver_exact_active_specialist_binding_activation_or_delegated_substitution_repair_return(
    tmp_path: Path,
) -> str:
    activation_packet = _seed_domain_weaver_exact_active_specialist_binding_materialization_gate_repair_return(
        tmp_path
    )
    queue_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_exact_active_specialist_binding_activation_or_delegated_substitution_repair",
            "packet_id": activation_packet,
            "start_workers": False,
        },
    )
    assert queue_result["ok"] is True
    request_path = queue_result["summary"]["work_request_paths"][0]
    request = json.loads((tmp_path / request_path).read_text(encoding="utf-8"))
    next_packet = (
        "PCKT-DOMAIN-WEAVER-EXACT-ACTIVE-SPECIALIST-BINDING-"
        "CANDIDATE-MATERIALIZATION-PLAN-20260602-ATTEMPT-001"
    )
    body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"fake_{request['request_id']}/task_return_body.md"
    )
    return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{request['request_id']}_accepted_return.json"
    )
    machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"{request['request_id']}_machine_receipt.json"
    )
    _write(
        tmp_path,
        body_rel,
        (
            "### CONTEXT PROOF\ncontext ready\n"
            "### TEMPLATE ACTION PROOF\n"
            "template_id: ion.template.autonomous_loop.local_worker.v1\n"
            "action_id: codex_queue_runner_process_once\n"
            "result: exact_active_binding_activation_repair_settled\n"
            "touched_paths:\n  - fake\n"
            "### VALIDATION\nvalidated\n"
            "### RESULT\n"
            "verdict: ACTIVATION_REPAIR_SETTLED\n"
            "candidate_only: true\n"
            "all_required_specialists_bound: true\n"
            "materialization_ready: true\n"
            "candidate_materialization_ready: true\n"
            "implementation_ready_now: false\n"
            "exact_active_binding_count: 5\n"
            "candidate_boot_only_count: 0\n"
            "delegated_active_binding_count: 1\n"
            "delegated_substitution_settled: true\n"
            "### ACTIVATION OR DELEGATED SUBSTITUTION REPAIR\n"
            "Five UI specialists have exact active invocable bindings; COMPONENT_BUILDER delegates to role.mason.\n"
            "### PER SPECIALIST EXACT ACTIVE BINDING MATRIX\n"
            "- JOC_UI_CANON_STEWARD exact active binding proof present.\n"
            "- FRONTEND_WORK_SURFACE_ARCHITECT exact active binding proof present.\n"
            "- INTERACTION_STATE_WEAVER exact active binding proof present.\n"
            "- CONTEXT_VISUALIZATION_CARTOGRAPHER exact active binding proof present.\n"
            "- VISUAL_PROOF_AUDITOR exact active binding proof present.\n"
            "- COMPONENT_BUILDER delegated to role.mason by accepted gate.\n"
            "### DELEGATED SUBSTITUTION DECISION\n"
            "delegated_substitution_verdict: DELEGATED_SUBSTITUTION_ACCEPTED\n"
            "delegated_substitution_accepted: true\n"
            "### BLOCKERS\n"
            "- none for exact active binding materialization gate\n"
            "### RECOMMENDED NEXT PACKET\n"
            f"{next_packet}\n"
            "### ION OPERATIONAL POSTURE\nproduction_authority: false\nlive_execution_authority: false\n"
            "### WORKLOAD DIFF\nNo source files changed.\n"
        ),
    )
    _write(
        tmp_path,
        machine_rel,
        json.dumps({"accepted_for_carrier_intake": True}, indent=2, sort_keys=True) + "\n",
    )
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": machine_rel,
                "template_action_proof_result": {"touched_paths": [body_rel]},
                "work_request_id": request["request_id"],
                "work_request_path": request_path,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    request["latest_return_packet_path"] = return_rel
    request["latest_task_return_machine_receipt_path"] = machine_rel
    request["return_packet_paths"] = [return_rel]
    _write(tmp_path, request_path, json.dumps(request, indent=2, sort_keys=True) + "\n")
    materialize_domain_weaver_projection(tmp_path)
    return next_packet


def test_domain_weaver_exact_active_specialist_binding_activation_or_delegated_substitution_result_advances_projection(
    tmp_path: Path,
):
    next_packet = (
        _seed_domain_weaver_exact_active_specialist_binding_activation_or_delegated_substitution_repair_return(
            tmp_path
        )
    )

    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    assert projection["summary"]["current_capability_class"] == (
        "approval_governed_exact_active_specialist_binding_materialization_ready"
    )
    assert projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"] == next_packet
    assert (
        projection["summary"][
            "exact_active_specialist_binding_activation_or_delegated_substitution_repair_settled"
        ]
        is True
    )
    assert (
        projection["summary"][
            "exact_active_specialist_binding_activation_or_delegated_substitution_repair_followup_next_packet_id"
        ]
        == next_packet
    )
    assert projection["summary"]["exact_active_binding_activation_repair_materialization_ready"] is True
    assert projection["summary"]["exact_active_binding_activation_repair_all_required_specialists_bound"] is True
    assert projection["summary"]["exact_active_binding_activation_repair_stop_classified"] is False
    assert projection["summary"]["exact_active_binding_activation_repair_delegated_substitution_settled"] is True
    assert projection["summary"]["exact_active_binding_activation_repair_exact_active_binding_count"] == 5
    assert projection["summary"]["exact_active_binding_activation_repair_candidate_boot_only_count"] == 0
    assert projection["summary"]["exact_active_binding_activation_repair_delegated_active_binding_count"] == 1
    result = projection["exact_active_specialist_binding_activation_or_delegated_substitution_repair"]
    assert result["summary"]["recommended_next_packet_id"] == next_packet
    assert result["summary"]["delegated_substitution_settled"] is True
    assert result["summary"]["materialization_ready"] is True
    assert (
        tmp_path / DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_ACTIVATION_OR_DELEGATED_SUBSTITUTION_REPAIR_RESULT_PATH
    ).is_file()


def _seed_domain_weaver_exact_active_specialist_binding_activation_stop_classified_return(
    tmp_path: Path,
) -> str:
    activation_packet = _seed_domain_weaver_exact_active_specialist_binding_materialization_gate_repair_return(
        tmp_path
    )
    queue_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_exact_active_specialist_binding_activation_or_delegated_substitution_repair",
            "packet_id": activation_packet,
            "start_workers": False,
        },
    )
    assert queue_result["ok"] is True
    request_path = queue_result["summary"]["work_request_paths"][0]
    request = json.loads((tmp_path / request_path).read_text(encoding="utf-8"))
    next_packet = (
        "PCKT-DOMAIN-WEAVER-EXACT-ACTIVE-SPECIALIST-BINDING-"
        "FIVE-SPECIALIST-ACTIVATION-GATE-20260602-ATTEMPT-001"
    )
    body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"fake_{request['request_id']}/task_return_body.md"
    )
    return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{request['request_id']}_stop_accepted_return.json"
    )
    machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"{request['request_id']}_stop_machine_receipt.json"
    )
    _write(
        tmp_path,
        body_rel,
        (
            "### CONTEXT PROOF\ncontext ready\n"
            "### TEMPLATE ACTION PROOF\n"
            "template_id: ion.template.autonomous_loop.local_worker.v1\n"
            "action_id: codex_queue_runner_process_once\n"
            "result: stop_classified_activation_delegated_substitution_repair\n"
            "touched_paths:\n  - fake\n"
            "### VALIDATION\nvalidated\n"
            "### RESULT\n"
            "verdict: STOP_CLASSIFIED_MISSING_EXACT_ACTIVE_SPECIALIST_BINDINGS\n"
            "candidate_only: true\n"
            "activation_repair_settled: true\n"
            "all_required_specialists_bound: false\n"
            "materialization_ready: false\n"
            "candidate_materialization_ready: false\n"
            "implementation_ready_now: false\n"
            "exact_active_binding_count: 0\n"
            "candidate_boot_only_count: 5\n"
            "delegated_active_binding_count: 1\n"
            "delegated_substitution_settled: true\n"
            "### ACTIVATION OR DELEGATED SUBSTITUTION REPAIR\n"
            "Five UI specialists remain CANDIDATE_BOOT_ONLY_NOT_ACTIVE_BINDING. COMPONENT_BUILDER delegates to role.mason.\n"
            "### PER SPECIALIST EXACT ACTIVE BINDING MATRIX\n"
            "- JOC_UI_CANON_STEWARD missing exact active binding.\n"
            "- FRONTEND_WORK_SURFACE_ARCHITECT missing exact active binding.\n"
            "- INTERACTION_STATE_WEAVER missing exact active binding.\n"
            "- CONTEXT_VISUALIZATION_CARTOGRAPHER missing exact active binding.\n"
            "- VISUAL_PROOF_AUDITOR missing exact active binding.\n"
            "- COMPONENT_BUILDER delegated to role.mason by accepted gate.\n"
            "### DELEGATED SUBSTITUTION DECISION\n"
            "delegated_substitution_verdict: DELEGATED_SUBSTITUTION_ACCEPTED_CANDIDATE_ONLY_BLOCKED_BY_MISSING_EXACT_BINDINGS\n"
            "delegated_substitution_accepted: true\n"
            "DELEGATED_BINDING_NOT_EXACT: true\n"
            "### BLOCKERS\n"
            "- missing exact active specialist bindings\n"
            "### RECOMMENDED NEXT PACKET\n"
            f"{next_packet}\n"
            "### ION OPERATIONAL POSTURE\nproduction_authority: false\nlive_execution_authority: false\n"
            "### WORKLOAD DIFF\nNo source files changed.\n"
        ),
    )
    _write(
        tmp_path,
        machine_rel,
        json.dumps({"accepted_for_carrier_intake": True}, indent=2, sort_keys=True) + "\n",
    )
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": machine_rel,
                "template_action_proof_result": {"touched_paths": [body_rel]},
                "work_request_id": request["request_id"],
                "work_request_path": request_path,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    request["latest_return_packet_path"] = return_rel
    request["latest_task_return_machine_receipt_path"] = machine_rel
    request["return_packet_paths"] = [return_rel]
    _write(tmp_path, request_path, json.dumps(request, indent=2, sort_keys=True) + "\n")
    materialize_domain_weaver_projection(tmp_path)
    return next_packet


def test_domain_weaver_exact_active_specialist_binding_five_specialist_activation_gate_queues(
    tmp_path: Path,
):
    next_packet = _seed_domain_weaver_exact_active_specialist_binding_activation_stop_classified_return(
        tmp_path
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_exact_active_specialist_binding_five_specialist_activation_gate",
            "packet_id": next_packet,
            "start_workers": False,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_ACTIVATION_GATE_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["activation_or_delegated_substitution_repair_result_ready"] is True
    assert result["summary"]["delegated_substitution_settled"] is True
    assert result["summary"]["stop_classified_missing_exact_active_bindings"] is True
    assert result["summary"]["exact_active_binding_count"] == 0
    assert result["summary"]["candidate_boot_only_count"] == 5
    assert result["summary"]["delegated_active_binding_count"] == 1
    assert result["summary"]["worker_started_count"] == 0
    request = json.loads((tmp_path / result["summary"]["work_request_paths"][0]).read_text(encoding="utf-8"))
    assert request["request_kind"] == "domain_weaver_exact_active_specialist_binding_five_specialist_activation_gate"
    assert request["agent_role"] == "role.steward"
    assert request["supporting_roles"] == ["role.nemesis", "role.scribe"]
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    gate = request["domain_weaver_exact_active_specialist_binding_five_specialist_activation_gate"]
    assert len(gate["required_specialist_ids"]) == 5
    assert gate["delegated_component_substitution"]["delegated_role"] == "role.mason"
    assert gate["delegated_component_substitution"]["exact_binding"] is False
    assert gate["active_registry_write_authority"] is False
    assert gate["implementation_authority"] is False
    assert gate["worker_start_allowed_by_this_packet"] is False
    assert gate["queue_fanout_authority"] is False
    assert request["production_authority"] is False
    assert request["live_execution_authority"] is False
    assert request["accepted_state_authority"] is False
    assert request["secrets_authority"] is False


def _seed_domain_weaver_exact_active_specialist_binding_five_specialist_activation_gate_return(
    tmp_path: Path,
) -> str:
    gate_packet = _seed_domain_weaver_exact_active_specialist_binding_activation_stop_classified_return(
        tmp_path
    )
    queue_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_exact_active_specialist_binding_five_specialist_activation_gate",
            "packet_id": gate_packet,
            "start_workers": False,
        },
    )
    assert queue_result["ok"] is True
    request_path = queue_result["summary"]["work_request_paths"][0]
    request = json.loads((tmp_path / request_path).read_text(encoding="utf-8"))
    next_packet = (
        "PCKT-DOMAIN-WEAVER-EXACT-ACTIVE-SPECIALIST-BINDING-"
        "MATERIALIZATION-READINESS-20260602-ATTEMPT-001"
    )
    body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"fake_{request['request_id']}/task_return_body.md"
    )
    return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{request['request_id']}_accepted_return.json"
    )
    machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"{request['request_id']}_machine_receipt.json"
    )
    _write(
        tmp_path,
        body_rel,
        (
            "### CONTEXT PROOF\ncontext ready\n"
            "### TEMPLATE ACTION PROOF\n"
            "template_id: ion.template.autonomous_loop.local_worker.v1\n"
            "action_id: codex_queue_runner_process_once\n"
            "result: five_specialist_activation_gate_settled\n"
            "touched_paths:\n  - fake\n"
            "### VALIDATION\nvalidated\n"
            "### FIVE SPECIALIST ACTIVATION GATE\n"
            "verdict: FIVE_SPECIALIST_EXACT_ACTIVE_BINDINGS_READY\n"
            "five_specialist_exact_active_bindings_ready: true\n"
            "five_specialist_activation_ready: true\n"
            "materialization_ready: true\n"
            "exact_active_binding_count: 5\n"
            "five_specialist_exact_active_binding_count: 5\n"
            "missing_exact_active_binding_count: 0\n"
            "candidate_boot_only_count: 0\n"
            "delegated_active_binding_count: 1\n"
            "delegated_substitution_settled: true\n"
            "delegated_component_substitution_preserved: true\n"
            "JOC_UI_CANON_STEWARD -> exact active binding\n"
            "FRONTEND_WORK_SURFACE_ARCHITECT -> exact active binding\n"
            "INTERACTION_STATE_WEAVER -> exact active binding\n"
            "CONTEXT_VISUALIZATION_CARTOGRAPHER -> exact active binding\n"
            "VISUAL_PROOF_AUDITOR -> exact active binding\n"
            "COMPONENT_BUILDER -> role.mason candidate delegated substitution preserved\n"
            "### RECOMMENDED NEXT PACKET\n"
            f"{next_packet}\n"
            "### ION OPERATIONAL POSTURE\nproduction_authority: false\nlive_execution_authority: false\n"
            "### WORKLOAD DIFF\nNo source files changed.\n"
        ),
    )
    _write(
        tmp_path,
        machine_rel,
        json.dumps({"accepted_for_carrier_intake": True}, indent=2, sort_keys=True) + "\n",
    )
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": machine_rel,
                "template_action_proof_result": {"touched_paths": [body_rel]},
                "work_request_id": request["request_id"],
                "work_request_path": request_path,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    request["latest_return_packet_path"] = return_rel
    request["latest_task_return_machine_receipt_path"] = machine_rel
    request["return_packet_paths"] = [return_rel]
    _write(tmp_path, request_path, json.dumps(request, indent=2, sort_keys=True) + "\n")
    materialize_domain_weaver_projection(tmp_path)
    return next_packet


def test_domain_weaver_exact_active_specialist_binding_five_specialist_activation_result_advances_projection(
    tmp_path: Path,
):
    next_packet = _seed_domain_weaver_exact_active_specialist_binding_five_specialist_activation_gate_return(
        tmp_path
    )

    projection = build_domain_weaver_projection(tmp_path)

    assert (
        projection["summary"]["current_capability_class"]
        == "approval_governed_exact_active_specialist_binding_five_specialist_activation_materialization_ready"
    )
    assert (
        projection["summary"]["exact_active_specialist_binding_five_specialist_activation_gate_settled"]
        is True
    )
    assert (
        projection["summary"]["exact_active_specialist_binding_five_specialist_activation_gate_next_packet_id"]
        == next_packet
    )
    assert projection["summary"]["exact_active_binding_five_specialist_materialization_ready"] is True
    assert projection["summary"]["exact_active_binding_five_specialist_bindings_ready"] is True
    assert projection["summary"]["exact_active_binding_five_specialist_stop_classified"] is False
    assert projection["summary"]["exact_active_binding_five_specialist_exact_active_binding_count"] == 5
    assert projection["summary"]["exact_active_binding_five_specialist_missing_exact_active_binding_count"] == 0
    result = projection["exact_active_specialist_binding_five_specialist_activation_gate"]
    assert result["summary"]["five_specialist_activation_gate_settled"] is True
    assert result["summary"]["delegated_component_substitution_preserved"] is True
    assert (tmp_path / DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_ACTIVATION_GATE_RESULT_PATH).is_file()
    assert projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"] == next_packet


def _seed_domain_weaver_exact_active_specialist_binding_five_specialist_activation_gate_stop_return(
    tmp_path: Path,
) -> str:
    gate_packet = _seed_domain_weaver_exact_active_specialist_binding_activation_stop_classified_return(
        tmp_path
    )
    queue_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_exact_active_specialist_binding_five_specialist_activation_gate",
            "packet_id": gate_packet,
            "start_workers": False,
        },
    )
    assert queue_result["ok"] is True
    request_path = queue_result["summary"]["work_request_paths"][0]
    request = json.loads((tmp_path / request_path).read_text(encoding="utf-8"))
    next_packet = (
        "PCKT-DOMAIN-WEAVER-FIVE-SPECIALIST-EXACT-ACTIVE-BINDING-"
        "REQUEST-MATERIALIZATION-NO-START-20260602-ATTEMPT-001"
    )
    body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"fake_{request['request_id']}/task_return_body.md"
    )
    return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{request['request_id']}_stop_accepted_return.json"
    )
    machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"{request['request_id']}_stop_machine_receipt.json"
    )
    _write(
        tmp_path,
        body_rel,
        (
            "### CONTEXT PROOF\ncontext ready\n"
            "### TEMPLATE ACTION PROOF\n"
            "template_id: ion.template.autonomous_loop.local_worker.v1\n"
            "action_id: codex_queue_runner_process_once\n"
            "result: stop_classified_missing_exact_active_specialist_bindings\n"
            "touched_paths:\n  - fake\n"
            "### VALIDATION\nvalidated\n"
            "### FIVE SPECIALIST ACTIVATION GATE\n"
            "verdict: STOP_CLASSIFIED_MISSING_EXACT_ACTIVE_SPECIALIST_BINDINGS\n"
            "gate_verdict: STOP_CLASSIFIED_MISSING_EXACT_ACTIVE_SPECIALIST_BINDINGS\n"
            "gate_ready: false\n"
            "five_specialist_exact_active_bindings_ready: false\n"
            "materialization_ready: false\n"
            "exact_active_binding_count: 0\n"
            "missing_exact_active_binding_count: 5\n"
            "candidate_boot_only_count: 5\n"
            "delegated_active_binding_count: 1\n"
            "delegated_substitution_settled: true\n"
            "delegated_component_substitution_preserved: true\n"
            "COMPONENT_BUILDER -> role.mason candidate delegated substitution preserved\n"
            "### BLOCKERS\n"
            "- five specialists candidate boot only\n"
            "- activation decisions not invocable\n"
            "- materialization not ready\n"
            "### RECOMMENDED NEXT PACKET\n"
            f"{next_packet}\n"
            "### ION OPERATIONAL POSTURE\nproduction_authority: false\nlive_execution_authority: false\n"
            "### WORKLOAD DIFF\nNo source files changed.\n"
        ),
    )
    _write(
        tmp_path,
        machine_rel,
        json.dumps({"accepted_for_carrier_intake": True}, indent=2, sort_keys=True) + "\n",
    )
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": machine_rel,
                "template_action_proof_result": {"touched_paths": [body_rel]},
                "work_request_id": request["request_id"],
                "work_request_path": request_path,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    request["latest_return_packet_path"] = return_rel
    request["latest_task_return_machine_receipt_path"] = machine_rel
    request["return_packet_paths"] = [return_rel]
    _write(tmp_path, request_path, json.dumps(request, indent=2, sort_keys=True) + "\n")
    materialize_domain_weaver_projection(tmp_path)
    return next_packet


def test_domain_weaver_five_specialist_exact_active_binding_request_materialization_no_start_queues(
    tmp_path: Path,
):
    next_packet = _seed_domain_weaver_exact_active_specialist_binding_five_specialist_activation_gate_stop_return(
        tmp_path
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_five_specialist_exact_active_binding_request_materialization_no_start",
            "packet_id": next_packet,
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_REQUEST_MATERIALIZATION_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["queued_request_count"] == 5
    assert result["summary"]["request_materialization_ready"] is True
    assert result["summary"]["selected_active_role_count"] == 5
    assert result["summary"]["pending_context_receipt_count"] == 5
    assert result["summary"]["start_workers_requested_by_operator"] is True
    assert result["summary"]["start_workers_effective"] is False
    assert result["summary"]["worker_started_count"] == 0
    assert result["summary"]["next_worker_start_packet_id"] == (
        "PCKT-DOMAIN-WEAVER-FIVE-SPECIALIST-EXACT-ACTIVE-BINDING-WORKER-START-GATE-"
        "20260602-ATTEMPT-001"
    )
    assert (tmp_path / DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_REQUEST_MATERIALIZATION_RESULT_PATH).is_file()
    request_paths = result["summary"]["work_request_paths"]
    assert len(request_paths) == 5
    for rel in request_paths:
        request = json.loads((tmp_path / rel).read_text(encoding="utf-8"))
        binding = request["domain_weaver_five_specialist_exact_active_binding_request"]
        assert request["request_kind"] == "domain_weaver_five_specialist_exact_active_binding_worker_request"
        assert request["requested_model"] == "gpt-5.5"
        assert request["requested_reasoning_effort"] == "xhigh"
        assert request["agent_role"] == binding["selected_active_role"]
        assert binding["selected_carrier"] == "codex_cli_carrier"
        assert binding["work_request_path"] == rel
        assert binding["active_worker_context_receipt_status"] == "pending_worker_start"
        assert binding["exact_active_binding_proved"] is False
        assert binding["worker_start_allowed_by_materialization_packet"] is False
        assert request["production_authority"] is False
        assert request["live_execution_authority"] is False
        assert request["accepted_state_authority"] is False
        assert request["secrets_authority"] is False
    projection = build_domain_weaver_projection(tmp_path)
    assert (
        projection["summary"]["current_capability_class"]
        == "approval_governed_exact_active_specialist_binding_five_specialist_request_materialization_no_start_ready"
    )
    assert projection["summary"]["exact_active_binding_five_specialist_request_materialization_ready"] is True
    assert projection["summary"]["exact_active_binding_five_specialist_materialized_request_count"] == 5
    assert projection["summary"]["exact_active_binding_five_specialist_pending_context_receipt_count"] == 5
    assert projection["summary"]["exact_active_binding_five_specialist_worker_start_required"] is True
    assert (
        projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"]
        == result["summary"]["next_worker_start_packet_id"]
    )


def test_domain_weaver_five_specialist_exact_active_binding_worker_start_gate_starts_bounded_workers(
    tmp_path: Path,
    monkeypatch,
):
    next_packet = _seed_domain_weaver_exact_active_specialist_binding_five_specialist_activation_gate_stop_return(
        tmp_path
    )
    materialization = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_five_specialist_exact_active_binding_request_materialization_no_start",
            "packet_id": next_packet,
            "start_workers": False,
        },
    )
    assert materialization["ok"] is True
    start_packet = materialization["summary"]["next_worker_start_packet_id"]

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": f"ION/05_context/current/chatgpt_connector/codex_queue_runs/{Path(request_path).stem}/run.json",
                "pid": 9900 + len(calls),
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "start_five_specialist_exact_active_binding_workers",
            "packet_id": start_packet,
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_WORKER_START_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["source_queue_ledger_path"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_REQUEST_MATERIALIZATION_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["source_queued_request_count"] == 5
    assert result["summary"]["source_queueable_request_payload_count"] == 5
    assert result["summary"]["queueable_start_request_count"] == 5
    assert result["summary"]["start_workers_requested"] is True
    assert result["summary"]["worker_start_attempt_count"] == result["summary"]["max_worker_starts"]
    assert result["summary"]["worker_started_count"] == result["summary"]["max_worker_starts"]
    assert result["summary"]["remaining_queueable_start_request_count"] == (
        5 - result["summary"]["max_worker_starts"]
    )
    expected_next_packet = (
        start_packet
        if result["summary"]["remaining_queueable_start_request_count"]
        else (
            "PCKT-DOMAIN-WEAVER-FIVE-SPECIALIST-EXACT-ACTIVE-BINDING-RETURN-MONITOR-"
            "20260602-ATTEMPT-001"
        )
    )
    assert result["summary"]["next_recommended_packet_id"] == expected_next_packet
    assert result["summary"]["next_return_monitor_packet_id"] == (
        expected_next_packet if "RETURN-MONITOR" in expected_next_packet else ""
    )
    assert len(calls) == result["summary"]["max_worker_starts"]
    started_lanes = []
    for call in calls:
        assert call["start"] is True
        assert call["background"] is True
        request = json.loads((tmp_path / call["request_path"]).read_text(encoding="utf-8"))
        started_lanes.append(request["lane_id"])
        assert request["requested_model"] == "gpt-5.5"
        assert request["requested_reasoning_effort"] == "xhigh"
        assert request["domain_weaver_five_specialist_exact_active_binding_request"][
            "active_worker_context_receipt_status"
        ] == "pending_worker_start"
        assert request["production_authority"] is False
        assert request["live_execution_authority"] is False
        assert request["accepted_state_authority"] is False
        assert request["secrets_authority"] is False
    assert len(set(started_lanes)) == len(started_lanes)
    projection = build_domain_weaver_projection(tmp_path)
    assert (
        projection["summary"]["current_capability_class"]
        == "approval_governed_exact_active_specialist_binding_five_specialist_worker_start_in_progress"
    )
    assert projection["summary"]["exact_active_binding_five_specialist_worker_start_in_progress"] is True
    assert (
        projection["summary"]["exact_active_binding_five_specialist_worker_started_count"]
        == result["summary"]["max_worker_starts"]
    )
    assert (
        projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"]
        == expected_next_packet
    )


def _seed_domain_weaver_five_specialist_exact_active_binding_accepted_returns(
    tmp_path: Path,
) -> list[str]:
    historical_activation_result = {
        "recommended_next_packet": {
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-FIVE-SPECIALIST-EXACT-ACTIVE-BINDING-"
                "REQUEST-MATERIALIZATION-NO-START-20260602-ATTEMPT-001"
            )
        },
        "source_request_path": (
            "ION/05_context/current/chatgpt_connector/codex_work_requests/"
            "codex_req_domain_weaver_five_specialist_exact_active_binding_activation_gate_20260602_attempt_001.json"
        ),
        "source_return_packet_path": (
            "ION/05_context/current/chatgpt_connector/task_returns/"
            "codex_req_domain_weaver_five_specialist_exact_active_binding_activation_gate_accepted_return.json"
        ),
        "source_run_packet_path": (
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
            "fake_five_specialist_activation_gate/run.json"
        ),
        "source_task_return_body_path": (
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
            "fake_five_specialist_activation_gate/task_return_body.md"
        ),
        "source_machine_receipt_path": (
            "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
            "codex_req_domain_weaver_five_specialist_exact_active_binding_activation_gate_machine_receipt.json"
        ),
    }
    request_templates = _domain_weaver_five_specialist_exact_active_binding_request_materialization_templates(
        tmp_path,
        five_specialist_activation_gate_result=historical_activation_result,
    )
    request_paths = []
    queued_requests = []
    for request in request_templates:
        rel = request["packet_path"]
        request_paths.append(rel)
        queued_requests.append(
            {
                "request_id": request["request_id"],
                "packet_path": rel,
                "lane_id": request["lane_id"],
                "worker_started": False,
            }
        )
        _write(tmp_path, rel, json.dumps(request, indent=2, sort_keys=True) + "\n")
    _write(
        tmp_path,
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_REQUEST_MATERIALIZATION_QUEUE_LEDGER_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": (
                    "ion.domain_weaver.exact_active_specialist_binding_five_specialist_request_materialization_"
                    "ledger.v0_1_candidate"
                ),
                "blocked_templates": [],
                "queued_requests": queued_requests,
                "summary": {
                    "queued_request_count": 5,
                    "request_file_count": 5,
                    "queueable_start_request_count": 5,
                    "worker_start_attempt_count": 0,
                    "worker_started_count": 0,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    worker_rows = []
    for index, rel in enumerate(request_paths, start=1):
        request_path = tmp_path / rel
        request = json.loads(request_path.read_text(encoding="utf-8"))
        binding = request["domain_weaver_five_specialist_exact_active_binding_request"]
        request_id = request["request_id"]
        run_dir = f"ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_{request_id}"
        run_rel = f"{run_dir}/run.json"
        body_rel = f"{run_dir}/task_return_body.md"
        context_receipt_rel = f"{run_dir}/context_receipt.json"
        worker_awareness_rel = f"{run_dir}/worker_context_awareness_receipt.json"
        return_rel = f"ION/05_context/current/chatgpt_connector/task_returns/{request_id}_accepted_return.json"
        machine_rel = (
            "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
            f"{request_id}_machine_receipt.json"
        )
        visual_blocker_text = (
            "live_model_hydration_unproved: true\noperator_rejection_still_active: true\n"
            if binding["specialist_id"] == "VISUAL_PROOF_AUDITOR"
            else ""
        )
        _write(
            tmp_path,
            body_rel,
            (
                "### CONTEXT PROOF\ncontext ready\n"
                "### TEMPLATE ACTION PROOF\n"
                "template_id: ion.template.autonomous_loop.local_worker.v1\n"
                "action_id: codex_queue_runner_process_once\n"
                "result: exact_active_binding_specialist_return\n"
                f"touched_paths:\n  - {body_rel}\n  - {context_receipt_rel}\n"
                "### VALIDATION\nvalidated\n"
                "### RESULT\naccepted candidate return\n"
                "### EXACT ACTIVE SPECIALIST BINDING\n"
                f"selected_active_role: {binding['selected_active_role']}\n"
                f"selected_carrier: {binding['selected_carrier']}\n"
                f"invocation_lane: {binding['invocation_lane']}\n"
                "exact_active_binding_proved: false\n"
                "candidate_only: true\n"
                "### DOMAIN-SPECIFIC OUTPUT\n"
                f"specialist_id: {binding['specialist_id']}\n"
                + (
                    "source files were not mutated; live queue/control-plane files changed during runner activity.\n"
                    if binding["specialist_id"] == "FRONTEND_WORK_SURFACE_ARCHITECT"
                    else ""
                )
                + f"{visual_blocker_text}"
                "### BLOCKERS\nexact_active_binding_not_accepted_state\n"
                "### RECOMMENDED NEXT PACKET\n"
                "PCKT-DOMAIN-WEAVER-FIVE-SPECIALIST-EXACT-ACTIVE-BINDING-RETURN-MONITOR-20260602-ATTEMPT-001\n"
                "### ION OPERATIONAL POSTURE\nproduction_authority: false\nlive_execution_authority: false\n"
                "### WORKLOAD DIFF\nNo source files changed.\n"
            ),
        )
        _write(
            tmp_path,
            context_receipt_rel,
            json.dumps(
                {
                    "all_required_context_present": True,
                    "required_context_reads": [{"path": rel, "sha256": "a" * 64}],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        _write(
            tmp_path,
            worker_awareness_rel,
            json.dumps(
                {
                    "worker_context_awareness_status": "WORKER_CONTEXT_ACKNOWLEDGED",
                    "request_id": request_id,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        _write(
            tmp_path,
            run_rel,
            json.dumps(
                {
                    "schema_id": "ion.codex_queue_runner_run.v1",
                    "run_id": f"fake_{request_id}",
                    "request_path": rel,
                    "run_packet_path": run_rel,
                    "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                    "completed_at": "2026-06-02T00:00:00+00:00",
                    "worker_context_awareness_receipt_path": worker_awareness_rel,
                    "worker_lifecycle_events": [
                        {
                            "event": "worker_terminal",
                            "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                            "task_return_packet_path": return_rel,
                        }
                    ],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        _write(
            tmp_path,
            machine_rel,
            json.dumps({"accepted_for_carrier_intake": True}, indent=2, sort_keys=True) + "\n",
        )
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "accepted_for_carrier_intake": True,
                    "machine_receipt_path": machine_rel,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {
                        "accepted": True,
                        "touched_paths": [body_rel, context_receipt_rel],
                    },
                    "workload_diff_accepted": True,
                    "work_request_id": request_id,
                    "work_request_path": rel,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        request["latest_return_packet_path"] = return_rel
        request["latest_task_return_machine_receipt_path"] = machine_rel
        request["return_packet_paths"] = [return_rel]
        request_path.write_text(json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        worker_rows.append(
            {
                "request_id": request_id,
                "request_path": rel,
                "packet_path": rel,
                "lane_id": request["lane_id"],
                "ok": True,
                "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
                "run_packet_path": run_rel,
                "pid": 9900 + index,
            }
        )
    _write(
        tmp_path,
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_WORKER_START_QUEUE_LEDGER_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.exact_active_specialist_binding_five_specialist_worker_start_ledger.v0_1_candidate",
                "queued_requests": [
                    {
                        "request_id": row["request_id"],
                        "packet_path": row["packet_path"],
                        "lane_id": row["lane_id"],
                        "worker_started": True,
                    }
                    for row in worker_rows
                ],
                "worker_start_results": worker_rows,
                "summary": {
                    "queueable_start_request_count": 5,
                    "queued_request_count": 5,
                    "worker_start_attempt_count": 5,
                    "worker_started_count": 5,
                    "worker_start_failure_count": 0,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    materialize_domain_weaver_projection(tmp_path)
    return request_paths


def test_domain_weaver_five_specialist_exact_active_binding_return_monitor_fanin_blocks_overclaim(
    tmp_path: Path,
):
    _seed_domain_weaver_five_specialist_exact_active_binding_accepted_returns(tmp_path)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "settle_five_specialist_exact_active_binding_return_monitor",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-FIVE-SPECIALIST-EXACT-ACTIVE-BINDING-RETURN-MONITOR-"
                "20260602-ATTEMPT-001"
            ),
        },
    )

    assert result["ok"] is False
    assert result["summary"]["blocked_reason"] == "five_specialist_return_monitor_not_current_recommended_next_packet"
    assert "five_specialist_return_monitor_not_current_recommended_next_packet" in result["summary"]["blockers"]
    assert result["summary"]["expected_return_count"] == 5
    assert result["summary"]["accepted_return_count"] == 5
    assert result["summary"]["worker_context_awareness_receipt_count"] == 5
    assert result["summary"]["carrier_return_complete"] is True
    assert result["summary"]["exact_active_binding_settlement_complete"] is False
    assert result["summary"]["semantic_blocker_count"] >= 5
    assert result["summary"]["visual_proof_live_hydration_blocked"] is True
    assert result["summary"]["operator_rejection_active"] is True
    fanin = json.loads(
        (tmp_path / DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_FANIN_SETTLEMENT_RESULT_PATH).read_text(
            encoding="utf-8"
        )
    )
    blocker_codes = {row["code"] for row in fanin["semantic_blockers"]}
    assert "unexpected_source_mutation_claim" not in blocker_codes
    assert "exact_active_binding_not_accepted_state" in blocker_codes
    assert "visual_proof_live_hydration_unproved" in blocker_codes
    assert "operator_rejection_still_active" in blocker_codes
    assert result["summary"]["next_recommended_packet_id"] == (
        "PCKT-DOMAIN-WEAVER-VISUAL-PROOF-LIVE-HYDRATION-OPERATOR-REJECTION-SETTLEMENT-"
        "20260602-ATTEMPT-001"
    )
    assert result["summary"]["recommended_next_packet_id"] != result["summary"]["next_recommended_packet_id"]
    assert result["results"]["five_specialist_fanin_settlement"]["result_ready"] is True
    assert (tmp_path / DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_RETURN_MONITOR_PATH).is_file()
    assert (
        tmp_path / DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_FANIN_SETTLEMENT_RESULT_PATH
    ).is_file()
    projection = build_domain_weaver_projection(tmp_path)
    assert (
        projection["summary"]["current_capability_class"]
        == "approval_governed_exact_active_specialist_binding_five_specialist_fanin_settled_with_blockers"
    )
    assert projection["summary"]["exact_active_binding_five_specialist_accepted_return_count"] == 5
    assert projection["summary"]["exact_active_binding_five_specialist_worker_context_awareness_receipt_count"] == 5
    assert projection["summary"]["exact_active_binding_five_specialist_carrier_return_complete"] is True
    assert (
        projection["summary"]["exact_active_binding_five_specialist_exact_binding_settlement_complete"]
        is False
    )
    assert projection["summary"]["exact_active_binding_five_specialist_visual_hydration_blocked"] is True
    assert (
        projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"]
        == result["summary"]["recommended_next_packet_id"]
    )


def _seed_domain_weaver_exact_active_binding_kernel_repair_accepted_returns(
    tmp_path: Path,
    *,
    ledger_path: Path = DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANOUT_QUEUE_LEDGER_PATH,
) -> None:
    ledger = json.loads(
        (tmp_path / ledger_path).read_text(encoding="utf-8")
    )
    for index, row in enumerate(ledger["queued_requests"], start=1):
        request_path = tmp_path / row["packet_path"]
        request = json.loads(request_path.read_text(encoding="utf-8"))
        request_id = request["request_id"]
        run_dir = f"ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_kernel_{request_id}"
        run_rel = f"{run_dir}/run.json"
        body_rel = f"{run_dir}/task_return_body.md"
        context_receipt_rel = f"{run_dir}/context_receipt.json"
        awareness_rel = f"{run_dir}/worker_context_awareness_receipt.json"
        return_rel = (
            "ION/05_context/current/chatgpt_connector/task_returns/"
            f"{request_id}_accepted_kernel_repair_return.json"
        )
        machine_rel = (
            "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
            f"{request_id}_kernel_repair_machine_receipt.json"
        )
        lane = request["domain_weaver_exact_active_binding_kernel_repair_lane"]
        required_outputs = " ".join(lane["required_outputs"])
        _write(
            tmp_path,
            body_rel,
            (
                "### CONTEXT PROOF\n"
                "context ready\n"
                "### TEMPLATE ACTION PROOF\n"
                "template_id: ion.template.autonomous_loop.local_worker.v1\n"
                "action_id: codex_queue_runner_process_once\n"
                "result: exact_active_binding_kernel_repair_delta\n"
                f"touched_paths:\n  - {body_rel}\n  - {context_receipt_rel}\n"
                "### VALIDATION\n"
                "carrier currentness and context receipt checks passed\n"
                "### RESULT\n"
                "candidate repair delta only\n"
                "### EXACT ACTIVE BINDING REPAIR DELTA\n"
                f"agent_role: {request['agent_role']}\n"
                f"required_outputs: {required_outputs}\n"
                "exact_active_binding_contract: reject candidate boot labels, delegated substitutions, "
                "carrier intake only, stale context receipts, and visual proof as substitutes\n"
                "structured_binding_receipt_gate: required\n"
                "carrier_currentness_gate: required\n"
                "no source mutation\n"
                "source files were not mutated\n"
                "### BLOCKERS\nnone\n"
                "### RECOMMENDED NEXT PACKET\n"
                f"{DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANIN_PACKET_ID}\n"
                "### WORKLOAD DIFF\n"
                "No source files changed.\n"
                "### ION OPERATIONAL POSTURE\n"
                "production_authority: false\n"
                "live_execution_authority: false\n"
                "accepted_state_claim: false\n"
                "secrets_authority: false\n"
            ),
        )
        context_reads = []
        for rel in request.get("required_context_reads", []):
            path = tmp_path / rel
            if path.is_file():
                context_reads.append(
                    {
                        "path": rel,
                        "required": True,
                        "status": "READY",
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    }
                )
        _write(
            tmp_path,
            context_receipt_rel,
            json.dumps(
                {
                    "all_required_context_present": True,
                    "required_context_reads": context_reads,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        _write(
            tmp_path,
            awareness_rel,
            json.dumps(
                {
                    "schema_id": "ion.worker_context_awareness_receipt.v1",
                    "worker_context_awareness_status": "WORKER_CONTEXT_ACKNOWLEDGED",
                    "request_id": request_id,
                    "selected_model": request["requested_model"],
                    "selected_reasoning_effort": request["requested_reasoning_effort"],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        _write(
            tmp_path,
            machine_rel,
            json.dumps(
                {
                    "accepted_for_carrier_intake": True,
                    "accepted_state_claim": False,
                    "gate_results": {
                        "context_proof_accepted": True,
                        "template_action_proof_accepted": True,
                        "workload_diff_accepted": True,
                    },
                    "production_authority": False,
                    "live_execution_authority": False,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "accepted_for_carrier_intake": True,
                    "machine_receipt_path": machine_rel,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {
                        "accepted": True,
                        "touched_paths": [body_rel, context_receipt_rel],
                    },
                    "workload_diff_accepted": True,
                    "work_request_id": request_id,
                    "work_request_path": request["packet_path"],
                    "production_authority": False,
                    "live_execution_authority": False,
                    "accepted_state_claim": False,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        _write(
            tmp_path,
            run_rel,
            json.dumps(
                {
                    "schema_id": "ion.codex_queue_runner_run.v1",
                    "run_id": f"fake_kernel_{request_id}",
                    "request_path": request["packet_path"],
                    "run_packet_path": run_rel,
                    "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                    "completed_at": "2026-06-02T00:00:00+00:00",
                    "context_receipt_path": context_receipt_rel,
                    "task_return_body_path": body_rel,
                    "worker_context_awareness_receipt_path": awareness_rel,
                    "submit_result": {"packet_path": return_rel},
                    "worker_lifecycle_events": [
                        {
                            "event": "worker_terminal",
                            "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                            "task_return_packet_path": return_rel,
                        }
                    ],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        request["latest_return_packet_path"] = return_rel
        request["latest_task_return_machine_receipt_path"] = machine_rel
        request["return_packet_paths"] = [return_rel]
        request["test_worker_pid"] = 9910 + index
        request_path.write_text(json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_domain_weaver_queues_visual_proof_live_hydration_operator_rejection_settlement_from_fanin(
    tmp_path: Path,
):
    _seed_domain_weaver_five_specialist_exact_active_binding_accepted_returns(tmp_path)
    fanin = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "settle_five_specialist_exact_active_binding_return_monitor",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-FIVE-SPECIALIST-EXACT-ACTIVE-BINDING-RETURN-MONITOR-"
                "20260602-ATTEMPT-001"
            ),
        },
    )
    assert fanin["ok"] is True

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_visual_proof_live_hydration_operator_rejection_settlement",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-VISUAL-PROOF-LIVE-HYDRATION-OPERATOR-REJECTION-SETTLEMENT-"
                "20260602-ATTEMPT-001"
            ),
            "start_workers": False,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_VISUAL_PROOF_LIVE_HYDRATION_OPERATOR_REJECTION_SETTLEMENT_QUEUE_LEDGER_PATH.as_posix()
    )
    assert result["summary"]["queued_request_count"] == 1
    assert result["summary"]["worker_started_count"] == 0
    assert result["summary"]["visual_proof_live_hydration_blocked"] is True
    assert result["summary"]["operator_rejection_active"] is True
    assert result["summary"]["source_visual_proof_task_return_body_path"]
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_VISUAL_PROOF_LIVE_HYDRATION_OPERATOR_REJECTION_SETTLEMENT_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert len(ledger["queued_requests"]) == 1
    request = json.loads((tmp_path / ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8"))
    assert request["request_kind"] == "domain_weaver_visual_proof_live_hydration_operator_rejection_settlement"
    assert request["agent_role"] == "VISUAL_PROOF_AUDITOR"
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["requested_authority"]["production_authority"] is False
    assert request["requested_authority"]["live_execution_authority"] is False
    assert request["requested_authority"]["accepted_state_claim"] is False
    assert request["requested_authority"]["service_restart_authority"] is False
    context = request["domain_weaver_visual_proof_live_hydration_operator_rejection_settlement"]
    assert context["source_fanin_settlement_path"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_FANIN_SETTLEMENT_RESULT_PATH.as_posix()
    )
    assert context["source_return_monitor_path"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_RETURN_MONITOR_PATH.as_posix()
    )
    assert context["visual_proof_live_hydration_blocked"] is True
    assert context["operator_rejection_active"] is True
    assert context["required_verdict"] == (
        "live_model_hydration_proof_and_operator_rejection_settlement_or_explicit_blocker"
    )
    assert "do_not_restart_services" in context["forbidden_actions"]
    assert "do_not_mutate_ui_or_source" in context["forbidden_actions"]
    assert context["source_fanin_settlement_path"] in request["required_context_reads"]
    assert context["source_return_monitor_path"] in request["required_context_reads"]
    assert context["source_visual_proof_task_return_body_path"] in request["required_context_reads"]

    request_path = tmp_path / request["packet_path"]
    request_id = request["request_id"]
    run_dir = f"ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_{request_id}"
    body_rel = f"{run_dir}/task_return_body.md"
    context_receipt_rel = f"{run_dir}/context_receipt.json"
    awareness_rel = f"{run_dir}/worker_context_awareness_receipt.json"
    return_rel = f"ION/05_context/current/chatgpt_connector/task_returns/{request_id}_accepted_return.json"
    machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"{request_id}_machine_receipt.json"
    )
    run_rel = f"{run_dir}/run.json"
    _write(
        tmp_path,
        body_rel,
        (
            "### CONTEXT PROOF\ncontext ready\n"
            "### TEMPLATE ACTION PROOF\n"
            "template_id: ion.template.autonomous_loop.local_worker.v1\n"
            "action_id: codex_queue_runner_process_once\n"
            "result: blocked_live_hydration_operator_rejection_remains_active\n"
            f"touched_paths:\n  - {body_rel}\n"
            "### VALIDATION\n"
            "Reviewed fan-in settlement summary: accepted_return_count: 5, semantic_blocker_count: 7.\n"
            "### RESULT\n"
            "live_model_hydration_proved: `false`\n"
            "operator_rejection_superseded: `false`\n"
            "operator rejection remains active\n"
            "exact_active_binding_settlement_complete: false\n"
            "### LIVE MODEL HYDRATION PROOF\n"
            "`/cockpit/model.json` timed out after 15 seconds.\n"
            "model_endpoint_live_hydration_blocked: `true`\n"
            "### OPERATOR REJECTION SETTLEMENT\noperator_rejection_superseded: `false`\n"
            "### BLOCKERS\nlive_model_hydration_unproved\n"
            "fresh_live_browser_screenshot_uncaptured\n"
            "### RECOMMENDED NEXT PACKET\n"
            "PCKT-DOMAIN-WEAVER-LIVE-MODEL-HYDRATION-ENDPOINT-HANG-REPAIR-AND-REPROOF-20260602-ATTEMPT-001\n"
            "### WORKLOAD DIFF\nno_source_ui_registry_or_production_mutation: true\n"
            "### ION OPERATIONAL POSTURE\nproduction_authority: false\nlive_execution_authority: false\n"
        ),
    )
    _write(
        tmp_path,
        context_receipt_rel,
        json.dumps({"all_required_context_present": True, "required_context_reads": []}, indent=2) + "\n",
    )
    _write(
        tmp_path,
        awareness_rel,
        json.dumps({"worker_context_awareness_status": "WORKER_CONTEXT_ACKNOWLEDGED"}, indent=2) + "\n",
    )
    _write(
        tmp_path,
        run_rel,
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_run.v1",
                "run_id": f"fake_{request_id}",
                "request_path": request["packet_path"],
                "run_packet_path": run_rel,
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "task_return_body_path": body_rel,
                "worker_context_awareness_receipt_path": awareness_rel,
                "worker_lifecycle_events": [
                    {
                        "event": "worker_terminal",
                        "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                        "task_return_packet_path": return_rel,
                    }
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(tmp_path, machine_rel, json.dumps({"accepted_for_carrier_intake": True}, indent=2) + "\n")
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": machine_rel,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {"accepted": True, "touched_paths": [body_rel]},
                "work_request_id": request_id,
                "work_request_path": request["packet_path"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    request["latest_return_packet_path"] = return_rel
    request["latest_task_return_machine_receipt_path"] = machine_rel
    request["return_packet_paths"] = [return_rel]
    request_path.write_text(json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    projection_result = materialize_domain_weaver_projection(tmp_path)
    assert projection_result["ok"] is True
    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    visual_result = projection["visual_proof_live_hydration_operator_rejection_settlement"]
    assert visual_result["result_ready"] is True
    assert visual_result["summary"]["live_model_hydration_blocked"] is True
    assert visual_result["summary"]["operator_rejection_active"] is True
    assert (tmp_path / DOMAIN_WEAVER_VISUAL_PROOF_LIVE_HYDRATION_OPERATOR_REJECTION_SETTLEMENT_RESULT_PATH).is_file()
    assert (
        projection["summary"]["current_capability_class"]
        == "approval_governed_exact_active_specialist_binding_five_specialist_fanin_settled_with_blockers"
    )
    assert projection["summary"]["exact_active_binding_five_specialist_fanin_blocker_active"] is True
    assert projection["summary"]["exact_active_binding_five_specialist_fanin_blocker_repair_required"] is False
    assert projection["summary"]["visual_proof_live_hydration_endpoint_blocked"] is True
    assert projection["summary"]["visual_proof_operator_rejection_active"] is True
    assert projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"] == (
        "PCKT-DOMAIN-WEAVER-LIVE-MODEL-HYDRATION-ENDPOINT-HANG-REPAIR-AND-REPROOF-20260602-ATTEMPT-001"
    )

    reproof_dir = (
        "ION/05_context/current/domain_weaver/visual_smoke/"
        "20260602T155210Z_live_model_hydration_reproof_attempt_001"
    )
    reproof_rel = f"{reproof_dir}/live_model_hydration_endpoint_reproof.json"
    reproof_model_rel = f"{reproof_dir}/cockpit_weave_model.json"
    reproof_screenshot_rel = f"{reproof_dir}/domain_weaver_live_weave_1440x1000.png"
    _write(tmp_path, reproof_screenshot_rel, "png placeholder\n")
    _write(tmp_path, reproof_model_rel, json.dumps({"surface": "weave"}, indent=2) + "\n")
    _write(
        tmp_path,
        reproof_rel,
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.live_model_hydration_endpoint_reproof.v1",
                "packet_id": (
                    "PCKT-DOMAIN-WEAVER-LIVE-MODEL-HYDRATION-ENDPOINT-HANG-REPAIR-AND-REPROOF-"
                    "20260602-ATTEMPT-001"
                ),
                "http_status": 200,
                "surface": "weave",
                "model_endpoint_live_hydration_proved": True,
                "fresh_live_browser_screenshot_captured": True,
                "operator_rejection_superseded": False,
                "operator_rejection_still_active": True,
                "model_path": reproof_model_rel,
                "screenshot_path": reproof_screenshot_rel,
                "response_seconds": 0.47,
                "response_bytes": 1428689,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    materialize_domain_weaver_projection(tmp_path)
    reproof_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    reproof_summary = reproof_projection["summary"]
    assert (
        reproof_summary["current_capability_class"]
        == "approval_governed_exact_active_specialist_binding_five_specialist_fanin_settled_with_blockers"
    )
    assert reproof_summary["visual_proof_live_hydration_reproof_ready"] is True
    assert reproof_summary["visual_proof_live_hydration_reproof_path"] == reproof_rel
    assert reproof_summary["visual_proof_live_hydration_endpoint_blocked"] is False
    assert reproof_summary["visual_proof_operator_rejection_active"] is True
    assert reproof_summary["exact_active_binding_five_specialist_fanin_blocker_active"] is True
    assert reproof_summary["exact_active_binding_five_specialist_fanin_blocker_repair_required"] is True
    assert reproof_summary["exact_active_binding_five_specialist_exact_active_binding_proved_count"] == 0
    assert reproof_summary["exact_active_binding_five_specialist_ui_redesign_allowed"] is False
    assert reproof_projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_FANIN_BLOCKER_REPAIR_PACKET_ID
    )
    assert reproof_projection["recommended_next_packet"]["packet_id"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_FANIN_BLOCKER_REPAIR_PACKET_ID
    )
    assert reproof_projection["ui_development"]["next_packet"]["packet_id"] == (
        "PCKT-DOMAIN-WEAVER-OPERATOR-REJECTION-PRESERVED-QUALITY-REDESIGN-FANOUT-20260602-ATTEMPT-001"
    )
    assert reproof_projection["ui_development"]["summary"]["ui_visual_model_endpoint_blocked"] is False
    assert reproof_projection["ui_development"]["summary"]["ui_visual_live_hydration_reproof_ready"] is True

    redesign_blocked = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_operator_rejection_preserved_quality_redesign_fanout",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-OPERATOR-REJECTION-PRESERVED-QUALITY-REDESIGN-FANOUT-"
                "20260602-ATTEMPT-001"
            ),
            "start_workers": False,
        },
    )
    assert redesign_blocked["ok"] is False
    assert redesign_blocked["summary"]["blocked_reason"] == (
        "domain_weaver_core_next_packet_mismatch"
    )

    blocker_plan = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "materialize_five_specialist_exact_active_binding_fanin_blocker_repair_plan",
            "packet_id": DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_FANIN_BLOCKER_REPAIR_PACKET_ID,
            "start_workers": False,
        },
    )
    assert blocker_plan["ok"] is True
    assert blocker_plan["summary"]["exact_active_binding_proved_count"] == 0
    assert blocker_plan["summary"]["ui_implementation_allowed"] is False
    assert blocker_plan["summary"]["ui_redesign_fanout_allowed"] is False
    assert blocker_plan["summary"]["topology_materialization_allowed"] is False
    assert blocker_plan["summary"]["next_lawful_action"] == (
        "queue_exact_active_specialist_binding_kernel_repair_fanout"
    )
    assert (tmp_path / DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_FANIN_BLOCKER_REPAIR_PLAN_PATH).is_file()

    post_plan_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    assert post_plan_projection["summary"]["exact_active_binding_fanin_blocker_repair_plan_ready"] is True
    assert post_plan_projection["summary"]["exact_active_binding_kernel_repair_fanout_next_packet_id"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANOUT_PACKET_ID
    )
    assert post_plan_projection["recommended_next_packet"]["packet_id"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANOUT_PACKET_ID
    )

    kernel_repair_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_exact_active_specialist_binding_kernel_repair_fanout",
            "packet_id": DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANOUT_PACKET_ID,
            "start_workers": False,
        },
    )
    assert kernel_repair_queue["ok"] is True
    assert kernel_repair_queue["summary"]["queued_request_count"] == 4
    assert kernel_repair_queue["summary"]["worker_started_count"] == 0
    assert kernel_repair_queue["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANOUT_QUEUE_LEDGER_PATH.as_posix()
    )
    kernel_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANOUT_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert len(kernel_ledger["queued_requests"]) == 4
    kernel_roles = []
    for row in kernel_ledger["queued_requests"]:
        request = json.loads((tmp_path / row["packet_path"]).read_text(encoding="utf-8"))
        kernel_roles.append(request["agent_role"])
        assert request["request_kind"] == "domain_weaver_exact_active_binding_kernel_repair_lane"
        if request["agent_role"] == "role.codex_carrier_steward":
            assert request["lane_id"] == "maintenance_lane"
        assert request["requested_model"] == "gpt-5.5"
        assert request["requested_reasoning_effort"] == "xhigh"
        assert request["requested_service_tier"] == "fast"
        assert request["codex_model_override"]["selected_model"] == "gpt-5.5"
        assert request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
        assert request["codex_model_override"]["service_tier"] == "fast"
        assert request["requested_authority"]["source_edit_authority"] is False
        assert request["requested_authority"]["production_authority"] is False
        assert request["requested_authority"]["live_execution_authority"] is False
        assert request["requested_authority"]["accepted_state_claim"] is False
        context = request["domain_weaver_exact_active_binding_kernel_repair_lane"]
        assert context["exact_active_binding_proved_count"] == 0
        assert context["ui_implementation_allowed"] is False
        assert context["ui_redesign_fanout_allowed"] is False
        assert context["topology_materialization_allowed"] is False
        assert DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_FIVE_SPECIALIST_FANIN_BLOCKER_REPAIR_PLAN_PATH.as_posix() in (
            request["required_context_reads"]
        )
    assert set(kernel_roles) == {"role.steward", "role.codex_carrier_steward", "role.nemesis", "role.scribe"}

    _seed_domain_weaver_exact_active_binding_kernel_repair_accepted_returns(tmp_path)
    _write(tmp_path, "ION/04_packages/kernel/ion_codex_queue_runner.py", "changed after stale receipts\n")
    stale_kernel_fanin = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "settle_exact_active_specialist_binding_kernel_repair_fanin",
            "packet_id": DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANIN_PACKET_ID,
            "start_workers": False,
        },
    )
    assert stale_kernel_fanin["ok"] is False
    assert stale_kernel_fanin["summary"]["accepted_return_count"] == 4
    assert stale_kernel_fanin["summary"]["semantic_blocker_count"] == 4
    assert stale_kernel_fanin["summary"]["next_recommended_packet_id"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_CONTEXT_REISSUE_PACKET_ID
    )
    stale_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    assert stale_projection["summary"]["exact_active_binding_kernel_repair_context_reissue_required"] is True
    assert stale_projection["recommended_next_packet"]["packet_id"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_CONTEXT_REISSUE_PACKET_ID
    )

    reissue_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_exact_active_specialist_binding_kernel_repair_context_reissue",
            "packet_id": DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_CONTEXT_REISSUE_PACKET_ID,
            "start_workers": False,
        },
    )
    assert reissue_queue["ok"] is True
    assert reissue_queue["summary"]["queued_request_count"] == 4
    assert reissue_queue["summary"]["attempt_index"] == 2
    assert reissue_queue["summary"]["worker_started_count"] == 0
    assert reissue_queue["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_CONTEXT_REISSUE_QUEUE_LEDGER_PATH.as_posix()
    )
    reissue_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_CONTEXT_REISSUE_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert len(reissue_ledger["queued_requests"]) == 4
    for row in reissue_ledger["queued_requests"]:
        request = json.loads((tmp_path / row["packet_path"]).read_text(encoding="utf-8"))
        context = request["domain_weaver_exact_active_binding_kernel_repair_lane"]
        assert request["request_kind"] == "domain_weaver_exact_active_binding_kernel_repair_lane"
        assert request["requested_model"] == "gpt-5.5"
        assert request["requested_reasoning_effort"] == "xhigh"
        assert request["requested_service_tier"] == "fast"
        assert context["context_reissue"] is True
        assert context["attempt_index"] == 2
        assert context["source_fanin_settlement_path"] == (
            DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANIN_SETTLEMENT_RESULT_PATH.as_posix()
        )
        assert DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANIN_SETTLEMENT_RESULT_PATH.as_posix() in (
            request["required_context_reads"]
        )

    _seed_domain_weaver_exact_active_binding_kernel_repair_accepted_returns(
        tmp_path,
        ledger_path=DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_CONTEXT_REISSUE_QUEUE_LEDGER_PATH,
    )
    kernel_fanin = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "settle_exact_active_specialist_binding_kernel_repair_fanin",
            "packet_id": DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANIN_PACKET_ID,
            "start_workers": False,
        },
    )
    assert kernel_fanin["ok"] is True
    assert kernel_fanin["summary"]["expected_return_count"] == 4
    assert kernel_fanin["summary"]["accepted_return_count"] == 4
    assert kernel_fanin["summary"]["carrier_clean_return_count"] == 4
    assert kernel_fanin["summary"]["semantic_blocker_count"] == 0
    assert kernel_fanin["summary"]["latest_pointer_lineage_status"] == "reconciled"
    assert kernel_fanin["summary"]["strict_latest_pointer_lineage_gate_clean"] is True
    assert kernel_fanin["summary"]["operator_action_latest_pointer_unreconciled"] is False
    assert kernel_fanin["summary"]["blocking_context_drift_count"] == 0
    assert kernel_fanin["summary"]["dynamic_context_drift_count"] == 0
    assert kernel_fanin["summary"]["machine_gate_clean"] is True
    assert kernel_fanin["summary"]["structured_gate_source_patch_ready"] is True
    assert kernel_fanin["summary"]["ui_implementation_allowed"] is False
    assert kernel_fanin["summary"]["ui_redesign_fanout_allowed"] is False
    assert kernel_fanin["summary"]["topology_materialization_allowed"] is False
    assert kernel_fanin["summary"]["next_recommended_packet_id"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_STRUCTURED_GATE_SOURCE_PATCH_PACKET_ID
    )
    assert kernel_fanin["summary"]["return_monitor_path"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_RETURN_MONITOR_PATH.as_posix()
    )
    assert (tmp_path / DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_RETURN_MONITOR_PATH).is_file()
    assert (
        tmp_path / DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANIN_SETTLEMENT_RESULT_PATH
    ).is_file()
    monitor = json.loads(
        (tmp_path / DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_RETURN_MONITOR_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert monitor["summary"]["source_queue_ledger_path"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_CONTEXT_REISSUE_QUEUE_LEDGER_PATH.as_posix()
    )
    fanin_settlement = json.loads(
        (tmp_path / DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_FANIN_SETTLEMENT_RESULT_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert fanin_settlement["summary"]["blocking_context_drift_count"] == 0
    assert fanin_settlement["summary"]["dynamic_context_drift_count"] == 0
    assert fanin_settlement["summary"]["dynamic_context_reference_drift_path_count"] == 0
    settled_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    assert settled_projection["summary"]["exact_active_binding_kernel_repair_return_complete"] is True
    assert settled_projection["summary"]["exact_active_binding_kernel_repair_fanin_settled"] is True
    assert settled_projection["summary"]["exact_active_binding_kernel_repair_structured_gate_source_patch_ready"] is True
    assert settled_projection["summary"]["exact_active_binding_structured_gate_source_patch_next_packet_id"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_STRUCTURED_GATE_SOURCE_PATCH_PACKET_ID
    )
    assert settled_projection["recommended_next_packet"]["packet_id"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_STRUCTURED_GATE_SOURCE_PATCH_PACKET_ID
    )
    assert settled_projection["original_plan_compliance"]["recommended_next_packet"]["packet_id"] == (
        DOMAIN_WEAVER_EXACT_ACTIVE_SPECIALIST_BINDING_STRUCTURED_GATE_SOURCE_PATCH_PACKET_ID
    )
    return

    redesign_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_operator_rejection_preserved_quality_redesign_fanout",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-OPERATOR-REJECTION-PRESERVED-QUALITY-REDESIGN-FANOUT-"
                "20260602-ATTEMPT-001"
            ),
            "start_workers": False,
        },
    )
    assert redesign_queue["ok"] is True
    assert redesign_queue["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_OPERATOR_REJECTION_QUALITY_REDESIGN_FANOUT_QUEUE_LEDGER_PATH.as_posix()
    )
    assert redesign_queue["summary"]["queued_request_count"] == 7
    assert redesign_queue["summary"]["worker_started_count"] == 0
    redesign_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_OPERATOR_REJECTION_QUALITY_REDESIGN_FANOUT_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    redesign_roles = []
    for row in redesign_ledger["queued_requests"]:
        request = json.loads((tmp_path / row["packet_path"]).read_text(encoding="utf-8"))
        redesign_roles.append(request["agent_role"])
        assert request["requested_model"] == "gpt-5.5"
        assert request["requested_reasoning_effort"] == "xhigh"
        assert request["codex_model_override"]["selected_model"] == "gpt-5.5"
        assert request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
        assert request["requested_authority"]["production_authority"] is False
        assert request["requested_authority"]["live_execution_authority"] is False
        assert request["requested_authority"]["accepted_state_claim"] is False
        redesign_context = request["domain_weaver_operator_rejection_preserved_quality_redesign_fanout"]
        assert redesign_context["operator_rejection_active"] is True
        assert redesign_context["live_model_hydration_reproof_ready"] is True
        assert reproof_rel in request["required_context_reads"]
        assert DOMAIN_WEAVER_UI_OPERATOR_FEEDBACK_PATH.as_posix() in request["required_context_reads"]
    assert set(redesign_roles) == {
        "JOC_UI_CANON_STEWARD",
        "COMMS_ACTIVITY_SURFACE_ARCHITECT",
        "FRONTEND_WORK_SURFACE_ARCHITECT",
        "INTERACTION_STATE_WEAVER",
        "CONTEXT_VISUALIZATION_CARTOGRAPHER",
        "VISUAL_PROOF_AUDITOR",
        "role.nemesis",
    }

    accepted_return_paths = []
    accepted_body_paths = []
    for row in redesign_ledger["queued_requests"]:
        request_path = tmp_path / row["packet_path"]
        request = json.loads(request_path.read_text(encoding="utf-8"))
        body_rel = (
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
            f"test_{request['request_id']}/task_return_body.md"
        )
        return_rel = (
            "ION/05_context/current/chatgpt_connector/task_returns/"
            f"{request['request_id']}_accepted_return.json"
        )
        machine_rel = (
            "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
            f"{request['request_id']}_machine_receipt.json"
        )
        _write(
            tmp_path,
            body_rel,
            (
                "### CONTEXT PROOF\n"
                "context current\n"
                "### TEMPLATE ACTION PROOF\n"
                "result: no-code redesign contract ready\n"
                "### VALIDATION\n"
                "operator rejection preserved\n"
                "### RESULT\n"
                "NO_CODE_REDESIGN_CONTRACT_READY_OPERATOR_REJECTION_PRESERVED\n"
                "### REDESIGN CONTRACT\n"
                "Activity City, comms, timeline, rail/drawer, inspector, mobile, and proof overlay contract.\n"
                "### OPERATOR REJECTION PRESERVATION\n"
                "operator_rejection_superseded=false\n"
                "### BLOCKERS\n"
                "operator rejection remains active\n"
                "### RECOMMENDED NEXT PACKET\n"
                "PCKT-DOMAIN-WEAVER-OPERATOR-REJECTION-PRESERVED-QUALITY-REDESIGN-FANIN-STEWARDSHIP-NEMESIS-MOCK-PROOF-20260602-ATTEMPT-001\n"
                "### ION OPERATIONAL POSTURE\n"
                "production_authority=false live_execution_authority=false accepted_state_authority=false\n"
            ),
        )
        _write(
            tmp_path,
            machine_rel,
            json.dumps(
                {
                    "schema_id": "ion.chatgpt_connector.task_return_machine_receipt.v1",
                    "accepted_for_carrier_intake": True,
                },
                indent=2,
            )
            + "\n",
        )
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                    "accepted_for_carrier_intake": True,
                    "machine_receipt_path": machine_rel,
                    "template_action_proof_result": {"accepted": True, "touched_paths": [body_rel]},
                    "work_request_id": request["request_id"],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        request["latest_return_packet_path"] = return_rel
        request["latest_task_return_machine_receipt_path"] = machine_rel
        request["return_packet_paths"] = [return_rel]
        request_path.write_text(json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        accepted_return_paths.append(return_rel)
        accepted_body_paths.append(body_rel)

    materialize_domain_weaver_projection(tmp_path)
    quality_fanin_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    quality_ui = quality_fanin_projection["ui_development"]
    quality_next_packet = quality_ui["next_packet"]

    assert quality_ui["operator_rejection_quality_redesign_fanout"]["fanout_complete"] is True
    assert quality_ui["operator_rejection_quality_redesign_fanout"]["accepted_return_count"] == 7
    assert quality_ui["summary"]["operator_rejection_quality_redesign_fanout_complete"] is True
    assert quality_next_packet["packet_id"] == (
        "PCKT-DOMAIN-WEAVER-OPERATOR-REJECTION-PRESERVED-QUALITY-REDESIGN-FANIN-STEWARDSHIP-NEMESIS-MOCK-PROOF-20260602-ATTEMPT-001"
    )
    assert quality_next_packet["work_class"] == "operator_rejection_quality_redesign_fanin_settlement"

    fanin_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_operator_rejection_preserved_quality_redesign_fanin_settlement",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-OPERATOR-REJECTION-PRESERVED-QUALITY-REDESIGN-FANIN-STEWARDSHIP-"
                "NEMESIS-MOCK-PROOF-20260602-ATTEMPT-001"
            ),
            "start_workers": False,
        },
    )
    assert fanin_queue["ok"] is True
    assert fanin_queue["summary"]["accepted_return_count"] == 7
    assert fanin_queue["summary"]["worker_started_count"] == 0
    assert fanin_queue["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_OPERATOR_REJECTION_QUALITY_REDESIGN_FANIN_QUEUE_LEDGER_PATH.as_posix()
    )
    fanin_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_OPERATOR_REJECTION_QUALITY_REDESIGN_FANIN_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert len(fanin_ledger["queued_requests"]) == 1
    fanin_request_path = tmp_path / fanin_ledger["queued_requests"][0]["packet_path"]
    fanin_request = json.loads(fanin_request_path.read_text(encoding="utf-8"))
    assert fanin_request["request_kind"] == "domain_weaver_operator_rejection_quality_redesign_fanin_settlement"
    assert fanin_request["agent_role"] == "role.steward"
    assert fanin_request["supporting_roles"] == ["JOC_UI_CANON_STEWARD", "VISUAL_PROOF_AUDITOR", "role.nemesis"]
    assert fanin_request["requested_model"] == "gpt-5.5"
    assert fanin_request["requested_reasoning_effort"] == "xhigh"
    assert fanin_request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert fanin_request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert fanin_request["requested_authority"]["production_authority"] is False
    assert fanin_request["requested_authority"]["live_execution_authority"] is False
    assert fanin_request["requested_authority"]["accepted_state_claim"] is False
    fanin_context = fanin_request["domain_weaver_operator_rejection_quality_redesign_fanin"]
    assert fanin_context["accepted_return_count"] == 7
    assert fanin_context["operator_rejection_active"] is True
    assert fanin_context["live_model_hydration_reproof_ready"] is True
    assert fanin_context["required_verdict"] == (
        "quality_redesign_fanin_stewardship_nemesis_mock_proof_contract_or_explicit_blocker"
    )
    assert all(path in fanin_request["required_context_reads"] for path in accepted_return_paths)
    assert all(path in fanin_request["required_context_reads"] for path in accepted_body_paths)

    static_mock_packet_id = (
        "PCKT-DOMAIN-WEAVER-OPERATOR-REJECTION-PRESERVED-ACTIVITY-CITY-STATIC-MOCK-PROOF-"
        "AND-IMPLEMENTATION-PREVIEW-GATE-20260602-ATTEMPT-001"
    )
    fanin_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_test_operator_rejection_quality_fanin/task_return_body.md"
    )
    fanin_machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        "2026-06-02T170000Z0000_task_return_machine_receipt.json"
    )
    fanin_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-02T170000Z0000_task_return.json"
    _write(
        tmp_path,
        fanin_body_rel,
        (
            "### CONTEXT PROOF\n"
            "context current\n"
            "### TEMPLATE ACTION PROOF\n"
            "result: fan-in accepted\n"
            "### VALIDATION\n"
            "operator_rejection_superseded=false\n"
            "### RESULT\n"
            "QUALITY_REDIGN_FANIN_ACCEPTED_STATIC_MOCK_REQUIRED\n"
            "### OPERATOR REJECTION FAN-IN\n"
            "Seven returns synthesized; endpoint hydration is not acceptance.\n"
            "### FINAL DESIGN CONTRACT\n"
            "Activity City, comms/events, rail/drawer, inspector, timeline, proof overlay, mobile sheets.\n"
            "### STATIC MOCK PROOF PLAN\n"
            "Desktop/tablet/mobile static mock proof is required before code.\n"
            "### IMPLEMENTATION GATE\n"
            "Implementation remains blocked until static mock proof passes.\n"
            "### BLOCKERS\n"
            "operator rejection remains active\n"
            "### RECOMMENDED NEXT PACKET\n"
            f"{static_mock_packet_id}\n"
            "### ION OPERATIONAL POSTURE\n"
            "production_authority=false live_execution_authority=false accepted_state_authority=false\n"
        ),
    )
    _write(
        tmp_path,
        fanin_machine_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_connector.task_return_machine_receipt.v1",
                "accepted_for_carrier_intake": True,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        fanin_return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": fanin_machine_rel,
                "template_action_proof_result": {"accepted": True, "touched_paths": [fanin_body_rel]},
                "work_request_id": fanin_request["request_id"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    fanin_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    fanin_request["latest_return_packet_path"] = fanin_return_rel
    fanin_request["latest_task_return_machine_receipt_path"] = fanin_machine_rel
    fanin_request["return_packet_paths"] = [fanin_return_rel]
    fanin_request_path.write_text(json.dumps(fanin_request, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    materialize_domain_weaver_projection(tmp_path)
    static_mock_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    static_mock_ui = static_mock_projection["ui_development"]
    static_mock_next_packet = static_mock_ui["next_packet"]
    assert static_mock_ui["operator_rejection_quality_redesign_fanin"]["accepted"] is True
    assert static_mock_ui["operator_rejection_quality_redesign_fanin"]["recommended_next_packet_id"] == static_mock_packet_id
    assert static_mock_ui["operator_rejection_activity_city_static_mock_proof"]["accepted"] is False
    assert static_mock_next_packet["packet_id"] == static_mock_packet_id
    assert static_mock_next_packet["work_class"] == "operator_rejection_activity_city_static_mock_proof_gate"
    assert static_mock_projection["recommended_next_packet"]["packet_id"] == static_mock_packet_id

    static_mock_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": (
                "queue_operator_rejection_preserved_activity_city_static_mock_proof_and_implementation_preview_gate"
            ),
            "packet_id": static_mock_packet_id,
            "start_workers": False,
        },
    )
    assert static_mock_queue["ok"] is True
    assert static_mock_queue["summary"]["quality_fanin_accepted"] is True
    assert static_mock_queue["summary"]["worker_started_count"] == 0
    assert static_mock_queue["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_OPERATOR_REJECTION_ACTIVITY_CITY_STATIC_MOCK_PROOF_QUEUE_LEDGER_PATH.as_posix()
    )
    static_mock_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_OPERATOR_REJECTION_ACTIVITY_CITY_STATIC_MOCK_PROOF_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert len(static_mock_ledger["queued_requests"]) == 1
    static_mock_request_path = tmp_path / static_mock_ledger["queued_requests"][0]["packet_path"]
    static_mock_request = json.loads(static_mock_request_path.read_text(encoding="utf-8"))
    assert static_mock_request["request_kind"] == "domain_weaver_operator_rejection_activity_city_static_mock_proof_gate"
    assert static_mock_request["agent_role"] == "role.mason"
    assert static_mock_request["requested_model"] == "gpt-5.5"
    assert static_mock_request["requested_reasoning_effort"] == "xhigh"
    assert static_mock_request["requested_authority"]["production_authority"] is False
    assert static_mock_request["requested_authority"]["live_execution_authority"] is False
    assert static_mock_request["requested_authority"]["accepted_state_claim"] is False
    static_mock_context = static_mock_request["domain_weaver_operator_rejection_activity_city_static_mock_proof"]
    assert static_mock_context["source_fanin_return_path"] == fanin_return_rel
    assert static_mock_context["operator_rejection_active"] is True
    assert static_mock_context["endpoint_hydration_is_acceptance"] is False
    assert "do_not_edit_cockpit_ui" in static_mock_context["forbidden_actions"]
    assert fanin_body_rel in static_mock_request["required_context_reads"]

    implementation_packet_id = (
        "PCKT-DOMAIN-WEAVER-OPERATOR-REJECTION-PRESERVED-ACTIVITY-CITY-BOUNDED-CANDIDATE-"
        "IMPLEMENTATION-PREVIEW-20260602-ATTEMPT-001"
    )
    static_mock_proof_dir_rel = (
        "ION/05_context/current/domain_weaver/visual_smoke/"
        "20260602T170500Z_activity_city_static_mock_proof_attempt_001"
    )
    static_mock_html_rel = f"{static_mock_proof_dir_rel}/activity-city-static-mock-proof.html"
    static_mock_review_rel = f"{static_mock_proof_dir_rel}/ACTIVITY_CITY_STATIC_MOCK_REVIEW.candidate.json"
    static_mock_visual_rel = f"{static_mock_proof_dir_rel}/activity_city_static_mock_visual_proof.json"
    _write(tmp_path, static_mock_html_rel, "<main data-domain-weaver-static-mock>Activity City</main>\n")
    _write(
        tmp_path,
        static_mock_review_rel,
        json.dumps({"verdict": "PASS_STATIC_MOCK_GATE_ONLY"}, indent=2, sort_keys=True) + "\n",
    )
    _write(
        tmp_path,
        static_mock_visual_rel,
        json.dumps({"viewports": ["1440x1000", "1024x900", "390x844", "360x800"]}, indent=2, sort_keys=True)
        + "\n",
    )
    static_mock_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_test_operator_rejection_static_mock/task_return_body.md"
    )
    static_mock_machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        "2026-06-02T170500Z0000_task_return_machine_receipt.json"
    )
    static_mock_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-02T170500Z0000_task_return.json"
    _write(
        tmp_path,
        static_mock_body_rel,
        (
            "### CONTEXT PROOF\n"
            "context current\n"
            "### TEMPLATE ACTION PROOF\n"
            "result: static mock proof accepted\n"
            "### VALIDATION\n"
            "operator rejection preserved; endpoint hydration is not acceptance\n"
            "### RESULT\n"
            "PASS_STATIC_MOCK_GATE_ONLY\n"
            "### STATIC MOCK PROOF\n"
            f"- `{static_mock_proof_dir_rel}/`\n"
            f"- `{static_mock_html_rel}`\n"
            f"- `{static_mock_review_rel}`\n"
            f"- `{static_mock_visual_rel}`\n"
            "### ACTIVITY CITY STORYBOARD\n"
            "Git branches, city-map lanes, team comms, left drawer, right inspector, proof overlay, blockers, and mobile sheets.\n"
            "### STEWARDSHIP REVIEW\n"
            "STATIC_MOCK_PROOF_ACCEPTED_FOR_BOUNDED_IMPLEMENTATION_PACKET_ONLY\n"
            "### NEMESIS REVIEW\n"
            "IMPLEMENTATION_ALLOWED_ONLY_AS_CANDIDATE_PREVIEW_WITH_FRESH_PROOF\n"
            "### VISUAL PROOF REVIEW\n"
            "PASS_STATIC_MOCK_PROOF_ONLY\n"
            "### IMPLEMENTATION GATE\n"
            "STATIC_MOCK_PROOF_ACCEPTED_FOR_BOUNDED_IMPLEMENTATION_PACKET_ONLY\n"
            "IMPLEMENTATION_ALLOWED_ONLY_AS_CANDIDATE_PREVIEW_WITH_FRESH_PROOF\n"
            "### BLOCKERS\n"
            "operator rejection remains active and unsuperseded\n"
            "### RECOMMENDED NEXT PACKET\n"
            f"{implementation_packet_id}\n"
            "### ION OPERATIONAL POSTURE\n"
            "production_authority=false live_execution_authority=false accepted_state_authority=false\n"
        ),
    )
    _write(
        tmp_path,
        static_mock_machine_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_connector.task_return_machine_receipt.v1",
                "accepted_for_carrier_intake": True,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        static_mock_return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": static_mock_machine_rel,
                "template_action_proof_result": {"accepted": True, "touched_paths": [static_mock_body_rel]},
                "work_request_id": static_mock_request["request_id"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    static_mock_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    static_mock_request["latest_return_packet_path"] = static_mock_return_rel
    static_mock_request["latest_task_return_machine_receipt_path"] = static_mock_machine_rel
    static_mock_request["return_packet_paths"] = [static_mock_return_rel]
    static_mock_request_path.write_text(
        json.dumps(static_mock_request, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    materialize_domain_weaver_projection(tmp_path)
    implementation_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    implementation_ui = implementation_projection["ui_development"]
    implementation_next_packet = implementation_ui["next_packet"]
    assert implementation_ui["operator_rejection_activity_city_static_mock_proof"]["accepted"] is True
    assert implementation_ui["operator_rejection_activity_city_static_mock_proof"]["implementation_allowed"] is True
    assert (
        implementation_ui["operator_rejection_activity_city_static_mock_proof"]["recommended_next_packet_id"]
        == implementation_packet_id
    )
    assert implementation_next_packet["packet_id"] == implementation_packet_id
    assert (
        implementation_next_packet["work_class"]
        == "operator_rejection_activity_city_bounded_candidate_implementation_preview"
    )
    assert implementation_projection["recommended_next_packet"]["packet_id"] == implementation_packet_id

    implementation_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_operator_rejection_preserved_activity_city_bounded_candidate_implementation_preview",
            "packet_id": implementation_packet_id,
            "start_workers": False,
        },
    )
    assert implementation_queue["ok"] is True
    assert implementation_queue["summary"]["static_mock_accepted"] is True
    assert implementation_queue["summary"]["static_mock_implementation_allowed"] is True
    assert implementation_queue["summary"]["source_static_mock_return_path"] == static_mock_return_rel
    assert implementation_queue["summary"]["worker_started_count"] == 0
    assert implementation_queue["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_OPERATOR_REJECTION_ACTIVITY_CITY_IMPLEMENTATION_QUEUE_LEDGER_PATH.as_posix()
    )
    implementation_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_OPERATOR_REJECTION_ACTIVITY_CITY_IMPLEMENTATION_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert len(implementation_ledger["queued_requests"]) == 1
    implementation_request_path = tmp_path / implementation_ledger["queued_requests"][0]["packet_path"]
    implementation_request = json.loads(implementation_request_path.read_text(encoding="utf-8"))
    assert (
        implementation_request["request_kind"]
        == "domain_weaver_operator_rejection_activity_city_bounded_candidate_implementation_preview"
    )
    assert implementation_request["agent_role"] == "FRONTEND_WORK_SURFACE_ARCHITECT"
    assert "JOC_UI_CANON_STEWARD" in implementation_request["supporting_roles"]
    assert "role.nemesis" in implementation_request["supporting_roles"]
    assert implementation_request["requested_model"] == "gpt-5.5"
    assert implementation_request["requested_reasoning_effort"] == "xhigh"
    assert implementation_request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert implementation_request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert implementation_request["requested_authority"]["production_authority"] is False
    assert implementation_request["requested_authority"]["live_execution_authority"] is False
    assert implementation_request["requested_authority"]["accepted_state_claim"] is False
    implementation_context = implementation_request[
        "domain_weaver_operator_rejection_activity_city_candidate_implementation"
    ]
    assert implementation_context["source_static_mock_return_path"] == static_mock_return_rel
    assert implementation_context["operator_rejected_current_ui"] is True
    assert implementation_context["operator_rejection_superseded"] is False
    assert (
        implementation_context["required_visual_model"]
        == "activity_city_git_branch_timeline_for_autonomous_agent_team"
    )
    assert "do_not_supersede_operator_rejection" in implementation_context["forbidden_actions"]
    assert static_mock_body_rel in implementation_request["required_context_reads"]
    assert static_mock_return_rel in implementation_request["required_context_reads"]
    assert static_mock_machine_rel in implementation_request["required_context_reads"]
    assert static_mock_html_rel in implementation_request["required_context_reads"]
    assert static_mock_review_rel in implementation_request["required_context_reads"]
    assert static_mock_visual_rel in implementation_request["required_context_reads"]
    assert f"{static_mock_proof_dir_rel}/" not in implementation_request["required_context_reads"]

    served_route_packet_id = "PCKT-DOMAIN-WEAVER-ACTIVITY-CITY-SERVED-ROUTE-PROOF-AND-OPERATOR-REVIEW-20260602"
    implementation_proof_dir_rel = (
        "ION/05_context/current/domain_weaver/visual_smoke/"
        "20260602T173009Z_activity_city_bounded_candidate_preview_attempt_001"
    )
    implementation_preview_html_rel = f"{implementation_proof_dir_rel}/activity-city-bounded-candidate-preview.html"
    implementation_visual_rel = f"{implementation_proof_dir_rel}/activity_city_bounded_candidate_preview_visual_proof.json"
    implementation_manifest_rel = f"{implementation_proof_dir_rel}/ARTIFACT_MANIFEST.json"
    implementation_desktop_rel = (
        f"{implementation_proof_dir_rel}/domain-weaver-activity-city-bounded-preview-desktop-1440x1000.png"
    )
    implementation_tablet_rel = (
        f"{implementation_proof_dir_rel}/domain-weaver-activity-city-bounded-preview-tablet-1024x900.png"
    )
    implementation_mobile_390_rel = (
        f"{implementation_proof_dir_rel}/domain-weaver-activity-city-bounded-preview-mobile-390x844.png"
    )
    implementation_mobile_360_rel = (
        f"{implementation_proof_dir_rel}/domain-weaver-activity-city-bounded-preview-mobile-360x800.png"
    )
    implementation_stale_js_rel = "ION/08_ui/joc_cockpit_shell/dist/assets/index-stale-hash.js"
    _write(tmp_path, implementation_preview_html_rel, "<main>Activity City bounded candidate preview</main>\n")
    for rel in (
        implementation_desktop_rel,
        implementation_tablet_rel,
        implementation_mobile_390_rel,
        implementation_mobile_360_rel,
    ):
        _write(tmp_path, rel, "png placeholder\n")
    _write(
        tmp_path,
        implementation_visual_rel,
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.activity_city_bounded_candidate_preview_visual_proof.v1",
                "implementation_source_paths": [
                    "ION/08_ui/joc_cockpit_shell/DomainWeaverCockpitPanel.tsx",
                    "ION/08_ui/joc_cockpit_shell/ion-runtime-cockpit.css",
                    "ION/08_ui/joc_cockpit_shell/dist/index.html",
                    implementation_stale_js_rel,
                ],
                "artifacts": {
                    "static_preview_html": {"path": implementation_preview_html_rel},
                    "desktop_1440x1000": {"path": implementation_desktop_rel},
                    "tablet_1024x900": {"path": implementation_tablet_rel},
                    "mobile_390x844": {"path": implementation_mobile_390_rel},
                    "mobile_360x800": {"path": implementation_mobile_360_rel},
                },
                "contract_checks": {
                    "operator_rejection_visible": True,
                    "operator_rejection_superseded": False,
                    "endpoint_hydration_separate_from_acceptance": True,
                    "mobile_sheet_cues_visible": True,
                },
                "authority_non_claims": {
                    "operator_acceptance_claim": False,
                    "accepted_state_claim": False,
                    "production_authority": False,
                    "live_execution_authority": False,
                    "secrets_authority": False,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        implementation_manifest_rel,
        json.dumps({"schema_id": "ion.domain_weaver.activity_city_bounded_candidate_manifest.v1"}, indent=2)
        + "\n",
    )
    implementation_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_test_operator_rejection_activity_city_candidate_implementation/task_return_body.md"
    )
    implementation_machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        "2026-06-02T174629Z0000_task_return_machine_receipt.json"
    )
    implementation_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/2026-06-02T174629Z0000_task_return.json"
    )
    _write(
        tmp_path,
        implementation_body_rel,
        (
            "### CONTEXT PROOF\n"
            "context current\n"
            "### TEMPLATE ACTION PROOF\n"
            "result: implemented bounded candidate Activity City preview\n"
            "### VALIDATION\n"
            "npm run build passed; focused tests passed\n"
            "### RESULT\n"
            "bounded candidate implementation; operator rejection remains active; endpoint hydration evidence only\n"
            "### UI IMPLEMENTATION\n"
            "left drawer and right inspector separated; selected worker/event sync visible\n"
            "### VISUAL PROOF\n"
            f"proof_json: `{implementation_visual_rel}`\n"
            f"artifact_manifest: `{implementation_manifest_rel}`\n"
            f"- `{implementation_desktop_rel}`\n"
            f"- `{implementation_tablet_rel}`\n"
            f"- `{implementation_mobile_390_rel}`\n"
            f"- `{implementation_mobile_360_rel}`\n"
            "visual proof limit: static built-CSS proof only; live served route proof blocked by socket PermissionError and preview ports.\n"
            "### STEWARDSHIP REVIEW\n"
            "PASS_BOUNDED_CANDIDATE_IMPLEMENTATION_PREVIEW_WITH_PROOF_LIMIT\n"
            "### NEMESIS REVIEW\n"
            "PASS_WITH_EXPLICIT_LIVE_ROUTE_PROOF_BLOCKER\n"
            "### BLOCKERS\n"
            "Live served /cockpit#weave visual proof was blocked by socket PermissionError and unavailable preview ports.\n"
            "Operator rejection remains active and unsuperseded.\n"
            "### RECOMMENDED NEXT PACKET\n"
            f"{served_route_packet_id}\n"
            "### WORKLOAD DIFF\n"
            "- ION/08_ui/joc_cockpit_shell/DomainWeaverCockpitPanel.tsx\n"
            "- ION/08_ui/joc_cockpit_shell/ion-runtime-cockpit.css\n"
            "### ION OPERATIONAL POSTURE\n"
            "production_authority=false live_execution_authority=false accepted_state_authority=false\n"
        ),
    )
    _write(
        tmp_path,
        implementation_machine_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_connector.task_return_machine_receipt.v1",
                "accepted_for_carrier_intake": True,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        implementation_return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": implementation_machine_rel,
                "template_action_proof_result": {"accepted": True, "touched_paths": [implementation_body_rel]},
                "work_request_id": implementation_request["request_id"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    implementation_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    implementation_request["latest_return_packet_path"] = implementation_return_rel
    implementation_request["latest_task_return_machine_receipt_path"] = implementation_machine_rel
    implementation_request["return_packet_paths"] = [implementation_return_rel]
    implementation_request_path.write_text(
        json.dumps(implementation_request, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    materialize_domain_weaver_projection(tmp_path)
    served_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    served_ui = served_projection["ui_development"]
    served_next_packet = served_ui["next_packet"]
    accepted_impl = served_ui["operator_rejection_activity_city_candidate_implementation"]
    assert accepted_impl["accepted"] is True
    assert accepted_impl["served_route_proof_blocked"] is True
    assert accepted_impl["recommended_next_packet_id"] == served_route_packet_id
    assert accepted_impl["visual_proof_path"] == implementation_visual_rel
    assert implementation_mobile_360_rel in accepted_impl["screenshot_paths"]
    assert served_next_packet["packet_id"] == served_route_packet_id
    assert served_next_packet["work_class"] == "activity_city_served_route_proof_and_operator_review"
    assert served_next_packet["lane_id"] == "proof_lane"
    assert served_projection["recommended_next_packet"]["packet_id"] == served_route_packet_id

    served_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_operator_rejection_preserved_activity_city_served_route_proof_and_operator_review",
            "packet_id": served_route_packet_id,
            "confirmation": CONFIRMATION,
        },
    )
    assert served_queue["ok"] is True
    assert served_queue["summary"]["worker_started_count"] == 0
    assert served_queue["summary"]["candidate_implementation_accepted"] is True
    assert served_queue["summary"]["candidate_served_route_proof_blocked"] is True
    assert served_queue["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_OPERATOR_REJECTION_ACTIVITY_CITY_SERVED_ROUTE_PROOF_QUEUE_LEDGER_PATH.as_posix()
    )
    served_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_OPERATOR_REJECTION_ACTIVITY_CITY_SERVED_ROUTE_PROOF_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert len(served_ledger["queued_requests"]) == 1
    served_request_path = tmp_path / served_ledger["queued_requests"][0]["packet_path"]
    served_request = json.loads(served_request_path.read_text(encoding="utf-8"))
    assert (
        served_request["request_kind"]
        == "domain_weaver_operator_rejection_activity_city_served_route_proof_and_operator_review"
    )
    assert served_request["agent_role"] == "VISUAL_PROOF_AUDITOR"
    assert served_request["supporting_roles"] == [
        "JOC_UI_CANON_STEWARD",
        "FRONTEND_WORK_SURFACE_ARCHITECT",
        "role.nemesis",
        "role.steward",
    ]
    assert served_request["requested_model"] == "gpt-5.5"
    assert served_request["requested_reasoning_effort"] == "xhigh"
    assert served_request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert served_request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert served_request["requested_authority"]["production_authority"] is False
    assert served_request["requested_authority"]["live_execution_authority"] is False
    assert served_request["requested_authority"]["accepted_state_claim"] is False
    assert served_request["requested_authority"]["service_restart_authority"] is False
    served_context = served_request["domain_weaver_operator_rejection_activity_city_served_route_proof"]
    assert served_context["proof_only"] is True
    assert served_context["operator_rejection_superseded"] is False
    assert served_context["source_candidate_return_path"] == implementation_return_rel
    assert served_context["source_candidate_visual_proof_path"] == implementation_visual_rel
    assert served_context["source_candidate_artifact_manifest_path"] == implementation_manifest_rel
    assert (
        served_context["required_verdict"]
        == "served_route_visual_proof_operator_review_or_explicit_blocker"
    )
    assert "do_not_edit_cockpit_ui" in served_context["forbidden_actions"]
    assert "do_not_claim_static_html_as_served_route_proof" in served_context["forbidden_actions"]
    assert implementation_body_rel in served_request["required_context_reads"]
    assert implementation_return_rel in served_request["required_context_reads"]
    assert implementation_visual_rel in served_request["required_context_reads"]
    assert implementation_manifest_rel in served_request["required_context_reads"]
    assert implementation_stale_js_rel not in served_request["required_context_reads"]
    for screenshot_rel in (
        implementation_desktop_rel,
        implementation_tablet_rel,
        implementation_mobile_390_rel,
        implementation_mobile_360_rel,
    ):
        assert screenshot_rel in served_request["required_context_reads"]
    assert DOMAIN_WEAVER_OPERATOR_REJECTION_ACTIVITY_CITY_SERVED_ROUTE_PROOF_QUEUE_LEDGER_PATH.as_posix() not in (
        served_request["required_context_reads"]
    )

    authorized_preview_reproof_packet_id = (
        "PCKT-DOMAIN-WEAVER-ACTIVITY-CITY-AUTHORIZED-PREVIEW-LANE-SERVED-ROUTE-REPROOF-20260602"
    )
    served_proof_dir_rel = (
        "ION/05_context/current/domain_weaver/visual_smoke/"
        "20260602T180645Z_activity_city_served_route_proof_attempt_001"
    )
    served_proof_blocker_rel = f"{served_proof_dir_rel}/activity_city_served_route_proof_blocker.json"
    served_proof_manifest_rel = f"{served_proof_dir_rel}/ARTIFACT_MANIFEST.json"
    _write(
        tmp_path,
        served_proof_blocker_rel,
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.activity_city_served_route_proof_blocker.v1",
                "target_route": "/cockpit#weave",
                "served_route_available": False,
                "served_screenshots_captured": False,
                "blocker_code": "NO_SERVED_SCREENSHOTS",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        served_proof_manifest_rel,
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.activity_city_served_route_proof_manifest.v1",
                "proof_blocker_path": served_proof_blocker_rel,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    served_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_test_operator_rejection_activity_city_served_route_proof/task_return_body.md"
    )
    served_run_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_test_operator_rejection_activity_city_served_route_proof/run.json"
    )
    served_machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        "2026-06-02T181135Z0000_task_return_machine_receipt.json"
    )
    served_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-02T181135Z0000_task_return.json"
    _write(
        tmp_path,
        served_body_rel,
        (
            "### CONTEXT PROOF\n"
            "context current\n"
            "### TEMPLATE ACTION PROOF\n"
            "result: served route proof attempted; blocker artifact recorded\n"
            "### VALIDATION\n"
            "proof-only worker completed without UI edits\n"
            "### SERVED ROUTE PROOF\n"
            "served_route_available: false\n"
            "served_screenshots_captured: false\n"
            f"proof_blocker_artifact: `{served_proof_blocker_rel}`\n"
            "served /cockpit#weave proof is blocked in the current worker namespace\n"
            "### VISUAL PROOF\n"
            "served_visual_proof_verdict: blocked_no_served_route_available\n"
            f"static_baseline_manifest: `{served_proof_manifest_rel}`\n"
            "### SELECTOR STATE\n"
            "NO_SERVED_SCREENSHOTS\n"
            "### OPERATOR REVIEW\n"
            "operator_rejection_superseded: false\n"
            "operator_acceptance_claim: false\n"
            "operator rejection preserved\n"
            "### STATIC VS SERVED DIVERGENCE\n"
            "served route unavailable; static baseline cannot be promoted to served proof\n"
            "### BLOCKERS\n"
            "NO_SERVED_SCREENSHOTS\n"
            "### RECOMMENDED NEXT PACKET\n"
            f"{authorized_preview_reproof_packet_id}\n"
            "Authorized preview lane served-route reproof is required.\n"
            "### WORKLOAD DIFF\n"
            f"- {served_proof_blocker_rel}\n"
            f"- {served_proof_manifest_rel}\n"
            "### ION OPERATIONAL POSTURE\n"
            "production_authority=false live_execution_authority=false accepted_state_authority=false\n"
        ),
    )
    _write(
        tmp_path,
        served_run_rel,
        json.dumps(
            {
                "schema_id": "ion.codex_queue_run.v1",
                "run_id": "codex_run_test_operator_rejection_activity_city_served_route_proof",
                "request_path": served_ledger["queued_requests"][0]["packet_path"],
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "task_return_body_path": served_body_rel,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        served_machine_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_connector.task_return_machine_receipt.v1",
                "accepted_for_carrier_intake": True,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        served_return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": served_machine_rel,
                "task_return_body_path": served_body_rel,
                "template_action_proof_result": {"accepted": True, "touched_paths": [served_body_rel]},
                "work_request_id": served_request["request_id"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    served_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    served_request["latest_return_packet_path"] = served_return_rel
    served_request["latest_task_return_machine_receipt_path"] = served_machine_rel
    served_request["return_packet_paths"] = [served_return_rel]
    served_request_path.write_text(json.dumps(served_request, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    materialize_domain_weaver_projection(tmp_path)
    authorized_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    authorized_ui = authorized_projection["ui_development"]
    authorized_next_packet = authorized_ui["next_packet"]
    served_proof = authorized_ui["operator_rejection_activity_city_served_route_proof"]
    assert served_proof["accepted"] is True
    assert served_proof["served_route_blocked"] is True
    assert served_proof["authorized_preview_reproof_ready"] is True
    assert served_proof["recommended_next_packet_id"] == authorized_preview_reproof_packet_id
    assert served_proof["proof_blocker_path"] == served_proof_blocker_rel
    assert served_proof["artifact_manifest_path"] == served_proof_manifest_rel
    assert served_proof["operator_rejection_preserved"] is True
    assert served_proof["operator_acceptance_claim"] is False
    assert authorized_next_packet["packet_id"] == authorized_preview_reproof_packet_id
    assert authorized_next_packet["work_class"] == "activity_city_authorized_preview_lane_served_route_reproof"
    assert authorized_next_packet["recommended_worker"] == "VISUAL_PROOF_AUDITOR"
    assert authorized_next_packet["source_operator_rejection_activity_city_served_route_proof"][
        "return_path"
    ] == served_return_rel
    assert authorized_projection["recommended_next_packet"]["packet_id"] == authorized_preview_reproof_packet_id

    served_quality_packet_id = (
        "PCKT-DOMAIN-WEAVER-ACTIVITY-CITY-SERVED-ROUTE-QUALITY-REPAIR-FANOUT-20260602"
    )
    authorized_proof_dir_rel = (
        "ION/05_context/current/domain_weaver/visual_smoke/"
        "20260602T182156Z_activity_city_authorized_preview_reproof_attempt_001"
    )
    authorized_proof_rel = (
        f"{authorized_proof_dir_rel}/activity_city_authorized_preview_served_route_reproof.json"
    )
    authorized_manifest_rel = f"{authorized_proof_dir_rel}/ARTIFACT_MANIFEST.json"
    authorized_receipt_rel = (
        "ION/05_context/history/local_browser_execution_run_receipts/"
        "v53-local-browser-execution-run-test.local_browser_execution_run_receipt.json"
    )
    authorized_screenshot_rels = [
        f"{authorized_proof_dir_rel}/domain-weaver-activity-city-authorized-preview-desktop-1440x1000.png",
        f"{authorized_proof_dir_rel}/domain-weaver-activity-city-authorized-preview-tablet-1024x900.png",
        f"{authorized_proof_dir_rel}/domain-weaver-activity-city-authorized-preview-mobile-390x844.png",
        f"{authorized_proof_dir_rel}/domain-weaver-activity-city-authorized-preview-mobile-360x800.png",
    ]
    for rel in authorized_screenshot_rels:
        _write(tmp_path, rel, "png placeholder\n")
    _write(
        tmp_path,
        authorized_receipt_rel,
        json.dumps(
            {
                "schema_id": "ion.local_browser_execution_run_receipt.v1",
                "run_verdict": "LOCAL_BROWSER_EXECUTION_RUN_NEEDS_REVIEW",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        authorized_proof_rel,
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.activity_city_authorized_preview_served_route_reproof.v1",
                "packet_id": authorized_preview_reproof_packet_id,
                "target_route": "/cockpit#weave",
                "served_route_available": True,
                "served_screenshots_captured": True,
                "captures": [{"id": "desktop-1440x1000", "screenshot_path": authorized_screenshot_rels[0]}],
                "selector_checks": {
                    "activity_city_proof": True,
                    "event_stream": False,
                    "left_rail": True,
                    "right_rail": True,
                },
                "viewport_visibility_checks": {
                    "left_rail": True,
                    "right_rail": True,
                    "proof_overlay": False,
                },
                "acceptance_checks": {
                    "served_route_available": True,
                    "screenshots_nonzero_png": True,
                    "activity_city_selector_ready": True,
                    "left_and_right_rails_visible": True,
                    "comms_or_activity_visible": False,
                    "operator_rejection_preserved": True,
                    "operator_acceptance_claim": False,
                    "accepted_state_claim": False,
                    "production_authority": False,
                    "live_execution_authority": False,
                },
                "proof_verdict": "REVIEW_REQUIRED_AUTHORIZED_PREVIEW_SERVED_ROUTE_REPROOF",
                "operator_rejection_superseded": False,
                "operator_acceptance_claim": False,
                "accepted_state_claim": False,
                "local_browser_execution_run_receipt_path": authorized_receipt_rel,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        tmp_path,
        authorized_manifest_rel,
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.activity_city_authorized_preview_reproof_manifest.v1",
                "proof_path": authorized_proof_rel,
                "screenshot_paths": authorized_screenshot_rels,
                "local_browser_execution_run_receipt_path": authorized_receipt_rel,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    materialize_domain_weaver_projection(tmp_path)
    quality_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    quality_ui = quality_projection["ui_development"]
    quality_next_packet = quality_ui["next_packet"]
    authorized_reproof = quality_ui["operator_rejection_activity_city_authorized_preview_reproof"]
    assert authorized_reproof["recorded"] is True
    assert authorized_reproof["review_required"] is True
    assert authorized_reproof["proof_verdict"] == "REVIEW_REQUIRED_AUTHORIZED_PREVIEW_SERVED_ROUTE_REPROOF"
    assert "comms_event_stream_selector_absent" in authorized_reproof["quality_blockers"]
    assert "proof_overlay_not_visible_in_all_viewports" in authorized_reproof["quality_blockers"]
    assert authorized_reproof["operator_acceptance_claim"] is False
    assert quality_next_packet["packet_id"] == served_quality_packet_id
    assert quality_next_packet["work_class"] == "activity_city_served_route_quality_repair_fanout"
    assert quality_next_packet["recommended_worker"] == "JOC_UI_CANON_STEWARD"
    assert quality_next_packet["authority"]["source_edit_authority"] is False
    assert authorized_proof_rel in quality_next_packet["context_refs"]
    assert authorized_receipt_rel in quality_next_packet["context_refs"]
    assert quality_projection["recommended_next_packet"]["packet_id"] == served_quality_packet_id

    quality_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_operator_rejection_preserved_activity_city_quality_repair_fanout",
            "packet_id": served_quality_packet_id,
            "confirmation": CONFIRMATION,
        },
    )
    assert quality_queue["ok"] is True
    assert quality_queue["summary"]["worker_started_count"] == 0
    assert quality_queue["summary"]["authorized_reproof_recorded"] is True
    assert quality_queue["summary"]["authorized_reproof_review_required"] is True
    assert quality_queue["summary"]["source_edit_authority"] is False
    assert quality_queue["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_OPERATOR_REJECTION_ACTIVITY_CITY_QUALITY_REPAIR_FANOUT_QUEUE_LEDGER_PATH.as_posix()
    )
    quality_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_OPERATOR_REJECTION_ACTIVITY_CITY_QUALITY_REPAIR_FANOUT_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert len(quality_ledger["queued_requests"]) == 1
    quality_request = json.loads(
        (tmp_path / quality_ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8")
    )
    assert (
        quality_request["request_kind"]
        == "domain_weaver_operator_rejection_activity_city_served_route_quality_repair_fanout"
    )
    assert quality_request["agent_role"] == "JOC_UI_CANON_STEWARD"
    assert quality_request["requested_model"] == "gpt-5.5"
    assert quality_request["requested_reasoning_effort"] == "xhigh"
    assert quality_request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert quality_request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert quality_request["requested_authority"]["source_edit_authority"] is False
    assert quality_request["requested_authority"]["production_authority"] is False
    assert quality_request["requested_authority"]["live_execution_authority"] is False
    quality_context = quality_request["domain_weaver_operator_rejection_activity_city_quality_repair_fanout"]
    assert quality_context["source_authorized_reproof_path"] == authorized_proof_rel
    assert quality_context["source_local_browser_receipt_path"] == authorized_receipt_rel
    assert quality_context["operator_acceptance_claim"] is False
    assert quality_context["source_edit_authority"] is False
    assert "do_not_edit_cockpit_ui_source" in quality_context["forbidden_actions"]
    assert "image_or_mockup_proposal_artifacts" in quality_context["required_outputs"]
    assert authorized_proof_rel in quality_request["required_context_reads"]
    assert authorized_manifest_rel in quality_request["required_context_reads"]
    assert authorized_receipt_rel in quality_request["required_context_reads"]
    assert DOMAIN_WEAVER_OPERATOR_REJECTION_ACTIVITY_CITY_QUALITY_REPAIR_FANOUT_QUEUE_LEDGER_PATH.as_posix() not in (
        quality_request["required_context_reads"]
    )
    for rel in authorized_screenshot_rels:
        assert rel in quality_request["required_context_reads"]

    static_mockup_packet_id = (
        "PCKT-DOMAIN-WEAVER-ACTIVITY-CITY-QUALITY-REPAIR-STATIC-MOCKUP-PROOF-GATE-"
        "20260602-ATTEMPT-001"
    )
    quality_fanout_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_test_operator_rejection_activity_city_quality_repair_fanout/task_return_body.md"
    )
    quality_fanout_machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        "2026-06-02T184247Z0000_task_return_machine_receipt.json"
    )
    quality_fanout_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-02T184247Z0000_task_return.json"
    _write(
        tmp_path,
        quality_fanout_body_rel,
        (
            "### CONTEXT PROOF\n"
            "context current\n"
            "### TEMPLATE ACTION PROOF\n"
            "no source edits performed\n"
            "### VALIDATION\n"
            "served screenshots reviewed\n"
            "### SERVED PROOF REVIEW\n"
            "event_stream false and proof overlay below mobile viewport\n"
            "### UI QUALITY ROOT CAUSE\n"
            "rail and drawer misuse; missing comms activity stream\n"
            "### IMAGE PROPOSALS\n"
            "Activity Command Bridge, mobile one-sheet state, event stream first, proof chips first viewport\n"
            "### ROLE REPAIR CONTRACTS\n"
            "JOC steward, visual proof auditor, comms architect, interaction state weaver\n"
            "### NEMESIS REVIEW\n"
            "operator rejection remains active; manifest hash hygiene blocker present\n"
            "### BLOCKERS\n"
            "artifact manifest hash mismatch; no source edit authority\n"
            "### RECOMMENDED NEXT PACKET\n"
            f"{static_mockup_packet_id}\n"
            "Produce static mockup proof with no source edit before implementation.\n"
            "### WORKLOAD DIFF\n"
            f"- {quality_fanout_body_rel}\n"
            "### ION OPERATIONAL POSTURE\n"
            "production_authority=false live_execution_authority=false accepted_state_authority=false\n"
        ),
    )
    _write(
        tmp_path,
        quality_fanout_machine_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_connector.task_return_machine_receipt.v1",
                "accepted_for_carrier_intake": True,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        quality_fanout_return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": quality_fanout_machine_rel,
                "task_return_body_path": quality_fanout_body_rel,
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [quality_fanout_body_rel],
                },
                "work_request_id": quality_request["request_id"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    quality_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    quality_request["latest_return_packet_path"] = quality_fanout_return_rel
    quality_request["latest_task_return_machine_receipt_path"] = quality_fanout_machine_rel
    quality_request["return_packet_paths"] = [quality_fanout_return_rel]
    (tmp_path / quality_ledger["queued_requests"][0]["packet_path"]).write_text(
        json.dumps(quality_request, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    materialize_domain_weaver_projection(tmp_path)
    static_mockup_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    static_mockup_ui = static_mockup_projection["ui_development"]
    static_mockup_next_packet = static_mockup_ui["next_packet"]
    quality_fanout_ref = static_mockup_ui["operator_rejection_activity_city_quality_repair_fanout"]
    assert quality_fanout_ref["accepted"] is True
    assert quality_fanout_ref["static_mockup_proof_gate_ready"] is True
    assert quality_fanout_ref["recommended_next_packet_id"] == static_mockup_packet_id
    assert quality_fanout_ref["operator_acceptance_claim"] is False
    assert static_mockup_next_packet["packet_id"] == static_mockup_packet_id
    assert static_mockup_next_packet["work_class"] == "activity_city_quality_repair_static_mockup_proof_gate"
    assert static_mockup_next_packet["authority"]["source_edit_authority"] is False
    assert quality_fanout_body_rel in static_mockup_next_packet["context_refs"]
    assert static_mockup_projection["recommended_next_packet"]["packet_id"] == static_mockup_packet_id

    static_mockup_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_operator_rejection_preserved_activity_city_quality_repair_static_mockup_proof_gate",
            "packet_id": static_mockup_packet_id,
            "confirmation": CONFIRMATION,
        },
    )
    assert static_mockup_queue["ok"] is True
    assert static_mockup_queue["summary"]["worker_started_count"] == 0
    assert static_mockup_queue["summary"]["quality_fanout_accepted"] is True
    assert static_mockup_queue["summary"]["source_edit_authority"] is False
    assert static_mockup_queue["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_OPERATOR_REJECTION_ACTIVITY_CITY_QUALITY_REPAIR_STATIC_MOCKUP_QUEUE_LEDGER_PATH.as_posix()
    )
    static_mockup_ledger = json.loads(
        (
            tmp_path
            / DOMAIN_WEAVER_OPERATOR_REJECTION_ACTIVITY_CITY_QUALITY_REPAIR_STATIC_MOCKUP_QUEUE_LEDGER_PATH
        ).read_text(encoding="utf-8")
    )
    assert len(static_mockup_ledger["queued_requests"]) == 1
    static_mockup_request = json.loads(
        (tmp_path / static_mockup_ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8")
    )
    assert static_mockup_request["request_kind"] == (
        "domain_weaver_activity_city_quality_repair_static_mockup_proof_gate"
    )
    assert static_mockup_request["requested_model"] == "gpt-5.5"
    assert static_mockup_request["requested_reasoning_effort"] == "xhigh"
    assert static_mockup_request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert static_mockup_request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert static_mockup_request["requested_authority"]["source_edit_authority"] is False
    assert static_mockup_request["requested_authority"]["production_authority"] is False
    assert static_mockup_request["requested_authority"]["live_execution_authority"] is False
    static_mockup_context = static_mockup_request["domain_weaver_activity_city_quality_repair_static_mockup"]
    assert static_mockup_context["source_quality_fanout_task_return_body_path"] == quality_fanout_body_rel
    assert static_mockup_context["operator_acceptance_claim"] is False
    assert "four_static_mockup_screenshots" in static_mockup_context["required_outputs"]
    assert "do_not_edit_cockpit_ui_source" in static_mockup_context["forbidden_actions"]
    assert quality_fanout_body_rel in static_mockup_request["required_context_reads"]
    assert authorized_proof_rel in static_mockup_request["required_context_reads"]
    assert DOMAIN_WEAVER_OPERATOR_REJECTION_ACTIVITY_CITY_QUALITY_REPAIR_STATIC_MOCKUP_QUEUE_LEDGER_PATH.as_posix() not in (
        static_mockup_request["required_context_reads"]
    )

    implementation_packet_id = (
        "PCKT-DOMAIN-WEAVER-ACTIVITY-CITY-QUALITY-REPAIR-BOUNDED-IMPLEMENTATION-FROM-"
        "STATIC-MOCKUP-20260602-ATTEMPT-001"
    )
    static_mockup_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_test_activity_city_quality_repair_static_mockup/task_return_body.md"
    )
    static_mockup_machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        "2026-06-02T190145Z0000_task_return_machine_receipt.json"
    )
    static_mockup_return_rel = "ION/05_context/current/chatgpt_connector/task_returns/2026-06-02T190145Z0000_task_return.json"
    _write(
        tmp_path,
        static_mockup_body_rel,
        (
            "### CONTEXT PROOF\n"
            "context current\n"
            "### TEMPLATE ACTION PROOF\n"
            "No cockpit source or dist files were edited. Source hashes remained unchanged.\n"
            "### VALIDATION\n"
            "manifest hash verification passed\n"
            "### STATIC MOCKUP PROOF\n"
            "four static mockup screenshots captured\n"
            "### EVENT STREAM FIRST VIEW\n"
            "Event stream visible in first viewport for desktop, tablet, and mobile.\n"
            "### PROOF BOUNDARY REVIEW\n"
            "Proof boundary visible in first viewport for every screenshot.\n"
            "### VISUAL PROOF REVIEW\n"
            "static proof only; served proof still required\n"
            "### NEMESIS REVIEW\n"
            "operator rejection remains active and unsuperseded; no operator acceptance claim\n"
            "### BLOCKERS\n"
            "served implementation proof still required\n"
            "### RECOMMENDED NEXT PACKET\n"
            f"{implementation_packet_id}\n"
            "### WORKLOAD DIFF\n"
            f"- {static_mockup_body_rel}\n"
            "### ION OPERATIONAL POSTURE\n"
            "production_authority=false live_execution_authority=false accepted_state_authority=false\n"
        ),
    )
    _write(
        tmp_path,
        static_mockup_machine_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_connector.task_return_machine_receipt.v1",
                "accepted_for_carrier_intake": True,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        static_mockup_return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": static_mockup_machine_rel,
                "task_return_body_path": static_mockup_body_rel,
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [static_mockup_body_rel],
                },
                "work_request_id": static_mockup_request["request_id"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    static_mockup_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    static_mockup_request["latest_return_packet_path"] = static_mockup_return_rel
    static_mockup_request["latest_task_return_machine_receipt_path"] = static_mockup_machine_rel
    static_mockup_request["return_packet_paths"] = [static_mockup_return_rel]
    (tmp_path / static_mockup_ledger["queued_requests"][0]["packet_path"]).write_text(
        json.dumps(static_mockup_request, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    materialize_domain_weaver_projection(tmp_path)
    implementation_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    implementation_ui = implementation_projection["ui_development"]
    static_mockup_ref = implementation_ui["operator_rejection_activity_city_quality_repair_static_mockup"]
    implementation_next_packet = implementation_ui["next_packet"]
    assert static_mockup_ref["accepted"] is True
    assert static_mockup_ref["implementation_ready"] is True
    assert static_mockup_ref["recommended_next_packet_id"] == implementation_packet_id
    assert static_mockup_ref["operator_acceptance_claim"] is False
    assert implementation_next_packet["packet_id"] == implementation_packet_id
    assert implementation_next_packet["work_class"] == (
        "activity_city_quality_repair_bounded_implementation_from_static_mockup"
    )
    assert implementation_next_packet["authority"]["candidate_implementation_packet_only"] is True
    assert implementation_next_packet["authority"]["source_edit_authority"] is False
    assert static_mockup_body_rel in implementation_next_packet["context_refs"]
    assert implementation_projection["recommended_next_packet"]["packet_id"] == implementation_packet_id

    blocker_codes = {
        row["code"]
        for row in reproof_projection["original_plan_compliance"]["blockers"]
        if isinstance(row, dict)
    }
    assert "LIVE_MODEL_HYDRATION_ENDPOINT_HANG_REPAIR_REQUIRED" not in blocker_codes
    assert "VISUAL_PROOF_OPERATOR_REJECTION_STILL_ACTIVE" in blocker_codes


def _seed_domain_weaver_repin_required_returns(tmp_path: Path) -> None:
    queue_only = execute_domain_weaver_action(
        tmp_path,
        {"action": "queue_approval_governed_live_fanout", "confirmation": CONFIRMATION},
    )
    assert queue_only["ok"] is True
    ledger = json.loads((tmp_path / DOMAIN_WEAVER_LIVE_CARRIER_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    queued_paths = [row["packet_path"] for row in ledger["queued_requests"]]
    assert queued_paths

    for index, rel in enumerate(queued_paths):
        request_path = tmp_path / rel
        payload = json.loads(request_path.read_text(encoding="utf-8"))
        return_rel = f"ION/05_context/current/chatgpt_connector/task_returns/{payload['request_id']}_return.json"
        run_rel = f"ION/05_context/current/chatgpt_connector/codex_queue_runs/{payload['request_id']}"
        context_receipt_rel = f"{run_rel}/context_receipt.json"
        body_rel = f"{run_rel}/task_return_body.md"
        stale = index == 0
        required_context_reads = (
            [
                {"path": "ION/03_registry/domains/domain.codex_carrier_sync.domain.yaml", "sha256": "0" * 64},
                {"path": DOMAIN_WEAVER_PROJECTION_PATH.as_posix(), "sha256": "0" * 64},
            ]
            if stale
            else []
        )
        _write(
            tmp_path,
            context_receipt_rel,
            json.dumps(
                {
                    "schema_id": "ion.context_load_receipt.v1",
                    "required_context_reads": required_context_reads,
                },
                indent=2,
            )
            + "\n",
        )
        _write(
            tmp_path,
            body_rel,
            "\n".join(
                [
                    "### CONTEXT PROOF",
                    "sha256_expected: 0000" if stale else "context current",
                    "sha256_observed: changed" if stale else "no drift",
                    "",
                    "### TEMPLATE ACTION PROOF",
                    "result: blocked" if stale else "result: complete",
                    "",
                    "### VALIDATION",
                    "context_receipt_missing_or_stale" if stale else "semantic return body clean",
                    "",
                    "### RESULT",
                    "Work is blocked by stale context hash drift."
                    if stale
                    else "Candidate-bounded worker return completed without semantic blockers.",
                    "",
                ]
            ),
        )
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                    "created_at": "2026-05-31T00:00:00+00:00",
                    "request_id": payload["request_id"],
                    "accepted_for_carrier_intake": True,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {
                        "accepted": True,
                        "touched_paths": [context_receipt_rel, body_rel],
                    },
                    "workload_diff_accepted": True,
                },
                indent=2,
            )
            + "\n",
        )
        payload["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        payload["return_packet_paths"] = [return_rel]
        payload["latest_return_packet_path"] = return_rel
        request_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = materialize_domain_weaver_projection(tmp_path)
    assert result["ok"] is True
    repin_plan = json.loads(
        (tmp_path / DOMAIN_WEAVER_LIVE_FANIN_SEMANTIC_REPIN_PLAN_PATH).read_text(encoding="utf-8")
    )
    assert repin_plan["summary"]["repin_record_count"] == 1
    record = repin_plan["repin_records"][0]
    assert DOMAIN_WEAVER_PROJECTION_PATH.as_posix() not in {
        row["path"] for row in record["current_context_pins"]
    }
    assert DOMAIN_WEAVER_PROJECTION_PATH.as_posix() in {
        row["path"] for row in record["dynamic_context_references"]
    }
    assert repin_plan["summary"]["dynamic_context_reference_count"] == 1


def test_domain_weaver_repinned_nemesis_reaudit_without_magic_blocks_when_not_required(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "start_repin_plan_nemesis_reaudit",
            "packet_id": "PCKT-DOMAIN-WEAVER-LIVE-FANIN-REPINNED-NEMESIS-REAUDIT-20260601",
        },
    )

    assert result["ok"] is False
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["finding"] == "semantic_repin_plan_reaudit_not_required"
    assert result["worker_started_count"] == 0


def test_domain_weaver_operator_action_starts_repinned_nemesis_reaudit(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_repin_required_returns(tmp_path)

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_repinned_nemesis/run.json",
                "pid": 9301,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "start_repin_plan_nemesis_reaudit",
            "confirmation": CONFIRMATION,
            "packet_id": "PCKT-DOMAIN-WEAVER-LIVE-FANIN-REPINNED-NEMESIS-REAUDIT-20260601",
            "live_execution_confirmation": "ION_DOMAIN_WEAVER_LIVE_EXECUTION_CONFIRMED",
        },
    )

    expected_request_path = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_live_fanin_repinned_nemesis_reaudit_20260601.json"
    )
    assert result["ok"] is True
    assert result["summary"]["worker_started_count"] == 1
    assert result["summary"]["request_path"] == expected_request_path
    assert result["summary"]["run_packet_path"].endswith("fake_repinned_nemesis/run.json")
    assert result["summary"]["worker_pid"] == 9301
    assert calls == [{"request_path": expected_request_path, "start": True, "background": True}]

    request = json.loads((tmp_path / expected_request_path).read_text(encoding="utf-8"))
    assert request["request_kind"] == "domain_weaver_live_fanin_repinned_nemesis_reaudit"
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert DOMAIN_WEAVER_LIVE_FANIN_SEMANTIC_REPIN_PLAN_PATH.as_posix() in request["required_context_reads"]
    assert request["domain_weaver_repin_reaudit"]["repin_record_count"] == 1
    assert request["production_authority"] is False
    assert request["live_execution_authority"] is False
    assert request["accepted_state_authority"] is False
    assert request["secrets_authority"] is False


def test_domain_weaver_operator_action_starts_stabilized_projection_reaudit_packet(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_repin_required_returns(tmp_path)

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_stabilized_reaudit/run.json",
                "pid": 9302,
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "start_repin_plan_nemesis_reaudit",
            "confirmation": CONFIRMATION,
            "packet_id": "PCKT-DOMAIN-WEAVER-LIVE-FANIN-REPIN-PLAN-STABILIZE-PROJECTION-AND-REAUDIT-20260601B",
            "live_execution_confirmation": "ION_DOMAIN_WEAVER_LIVE_EXECUTION_CONFIRMED",
        },
    )

    expected_request_path = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_live_fanin_repin_plan_stabilize_projection_and_reaudit_20260601b.json"
    )
    assert result["ok"] is True
    assert result["summary"]["packet_id"] == (
        "PCKT-DOMAIN-WEAVER-LIVE-FANIN-REPIN-PLAN-STABILIZE-PROJECTION-AND-REAUDIT-20260601B"
    )
    assert result["summary"]["request_path"] == expected_request_path
    assert calls == [{"request_path": expected_request_path, "start": True, "background": True}]

    request = json.loads((tmp_path / expected_request_path).read_text(encoding="utf-8"))
    assert request["domain_weaver_repin_reaudit"]["packet_id"] == (
        "PCKT-DOMAIN-WEAVER-LIVE-FANIN-REPIN-PLAN-STABILIZE-PROJECTION-AND-REAUDIT-20260601B"
    )
    assert request["domain_weaver_repin_reaudit"]["dynamic_context_reference_count"] == 1
    assert "dynamic_context_reference_policy" in request["objective"]
    assert request["production_authority"] is False
    assert request["live_execution_authority"] is False


def _seed_domain_weaver_20260601b_reaudit_return(tmp_path: Path) -> None:
    _seed_domain_weaver_repin_required_returns(tmp_path)
    for rel in [
        "ION/05_context/current/ACTIVE_CARRIER_MESSAGE_QUEUE.json",
        "ION/04_packages/kernel/ion_domain_weaver.py",
        "ION/04_packages/kernel/ion_carrier_task_return.py",
    ]:
        _write(tmp_path, rel, "{}\n")
    request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_live_fanin_repin_plan_stabilize_projection_and_reaudit_20260601b.json"
    )
    run_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        "codex_run_test_domain_weaver_20260601b_reaudit"
    )
    body_rel = f"{run_rel}/task_return_body.md"
    return_rel = "ION/05_context/current/chatgpt_connector/task_returns/20260601b_reaudit_return.json"
    _write(
        tmp_path,
        body_rel,
        "\n".join(
            [
                "### CONTEXT PROOF",
                "context current",
                "",
                "### TEMPLATE ACTION PROOF",
                "result: blocked",
                "",
                "### VALIDATION",
                "classification table ready",
                "",
                "### RESULT",
                "| request_id | classification | proof |",
                "|---|---|---|",
                "| codex_req_domain_weaver_approval_fanout_act_req_joc_ui_canon_steward | semantic_clean_after_repin | clean |",
                "| codex_req_domain_weaver_approval_fanout_act_req_frontend_work_surface_architect | reissue_required | reissue |",
                "| codex_req_domain_weaver_approval_fanout_fission_domain_codex_carrier_sync_context_state_candidate | reissue_required | reissue |",
                "classification_counts:",
                "  semantic_clean_after_repin: 1",
                "  reissue_required: 2",
                "  supersede_required: 0",
                "  still_blocked: 0",
                "",
                "### WORKLOAD DIFF",
                "- created task_return_body.md",
                "",
                "### BLOCKERS",
                "- two reissues required",
                "",
                "### RECOMMENDED NEXT PACKET",
                "PCKT-DOMAIN-WEAVER-LIVE-FANIN-20260601B-CONTEXT-REBASELINE-AND-TWO-REISSUE",
                "",
                "### ION OPERATIONAL POSTURE",
                "production_authority: false",
                "live_execution_authority: false",
                "accepted_state_authority: false",
                "secrets_authority: false",
                "",
            ]
        ),
    )
    _write(
        tmp_path,
        return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_task_return_packet.v1",
                "created_at": "2026-05-31T20:10:44+00:00",
                "accepted_for_carrier_intake": True,
                "return_template_valid": True,
                "context_proof_result": {"accepted": True},
                "template_action_proof_result": {
                    "accepted": True,
                    "touched_paths": [request_rel, body_rel],
                },
                "workload_diff_accepted": True,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        request_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": "codex_req_domain_weaver_live_fanin_repin_plan_stabilize_projection_and_reaudit_20260601b",
                "dedupe_key": "domain_weaver:live_fanin_repin_plan_stabilize_projection_and_reaudit:20260601b",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "latest_return_packet_path": return_rel,
                "return_packet_paths": [return_rel],
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
            },
            indent=2,
        )
        + "\n",
    )


def test_domain_weaver_20260601b_reissue_start_is_policy_governed_without_live_magic(
    tmp_path: Path,
    monkeypatch,
):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_20260601b_reaudit_return(tmp_path)

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": f"ION/05_context/current/chatgpt_connector/codex_queue_runs/reissue_no_magic_{len(calls)}",
                "pid": 9400 + len(calls),
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_20260601b_context_rebaseline_and_two_reissue",
            "packet_id": "PCKT-DOMAIN-WEAVER-LIVE-FANIN-20260601B-CONTEXT-REBASELINE-AND-TWO-REISSUE",
            "start_workers": True,
        },
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["worker_started_count"] == 2
    assert len(calls) == 2


def test_domain_weaver_20260601b_reissue_action_queues_without_starting_workers(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_20260601b_reaudit_return(tmp_path)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_20260601b_context_rebaseline_and_two_reissue",
            "confirmation": CONFIRMATION,
            "packet_id": "PCKT-DOMAIN-WEAVER-LIVE-FANIN-20260601B-CONTEXT-REBASELINE-AND-TWO-REISSUE",
        },
    )

    assert result["ok"] is True
    assert result["summary"]["context_rebaseline_ready"] is True
    assert result["summary"]["queued_request_count"] == 2
    assert result["summary"]["worker_started_count"] == 0
    assert (tmp_path / DOMAIN_WEAVER_LIVE_FANIN_20260601B_CONTEXT_REBASELINE_PLAN_PATH).is_file()
    assert (tmp_path / DOMAIN_WEAVER_LIVE_FANIN_20260601B_REISSUE_QUEUE_LEDGER_PATH).is_file()
    plan = json.loads(
        (tmp_path / DOMAIN_WEAVER_LIVE_FANIN_20260601B_CONTEXT_REBASELINE_PLAN_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert plan["summary"]["source_reaudit_accepted"] is True
    assert plan["summary"]["reissue_required_count"] == 2
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_LIVE_FANIN_20260601B_REISSUE_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert ledger["summary"]["queued_request_count"] == 2
    for rel in result["summary"]["work_request_paths"]:
        request = json.loads((tmp_path / rel).read_text(encoding="utf-8"))
        assert request["status"] == "QUEUED_FOR_CODEX_CARRIER"
        assert request["requested_by"] == "domain_weaver_20260601b_context_rebaseline"
        assert request["request_kind"] == "domain_weaver_20260601b_reissue"
        assert request["route_family"] == "settlement"
        assert request["requested_model"] == "gpt-5.5"
        assert request["requested_reasoning_effort"] == "xhigh"
        assert DOMAIN_WEAVER_LIVE_FANIN_20260601B_CONTEXT_REBASELINE_PLAN_PATH.as_posix() in request[
            "required_context_reads"
        ]
        assert request["production_authority"] is False
        assert request["live_execution_authority"] is False
        assert request["accepted_state_authority"] is False
        assert request["secrets_authority"] is False
    source_request = json.loads(
        (
            tmp_path
            / "ION/05_context/current/chatgpt_connector/codex_work_requests/"
            "codex_req_domain_weaver_approval_fanout_act_req_frontend_work_surface_architect.json"
        ).read_text(encoding="utf-8")
    )
    assert source_request["status"] == "RETURN_RECORDED_PROOF_ACCEPTED"


def test_domain_weaver_20260601b_dynamic_reference_reissue_queues_new_requests(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_20260601b_reaudit_return(tmp_path)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_20260601b_dynamic_reference_policy_reissue",
            "confirmation": CONFIRMATION,
            "packet_id": "PCKT-DOMAIN-WEAVER-20260601B-DYNAMIC-REFERENCE-POLICY-REISSUE",
        },
    )

    assert result["ok"] is True
    assert result["summary"]["queued_request_count"] == 2
    assert result["summary"]["worker_started_count"] == 0
    assert (tmp_path / DOMAIN_WEAVER_LIVE_FANIN_20260601B_DYNAMIC_REFERENCE_REISSUE_QUEUE_LEDGER_PATH).is_file()
    assert result["summary"]["queue_ledger_path"] == (
        DOMAIN_WEAVER_LIVE_FANIN_20260601B_DYNAMIC_REFERENCE_REISSUE_QUEUE_LEDGER_PATH.as_posix()
    )
    for rel in result["summary"]["work_request_paths"]:
        request = json.loads((tmp_path / rel).read_text(encoding="utf-8"))
        assert request["status"] == "QUEUED_FOR_CODEX_CARRIER"
        assert request["request_kind"] == "domain_weaver_20260601b_dynamic_reference_reissue"
        assert request["requested_by"] == "domain_weaver_20260601b_dynamic_reference_policy_repair"
        assert request["route_family"] == "settlement"
        assert request["requested_model"] == "gpt-5.5"
        assert request["requested_reasoning_effort"] == "xhigh"
        assert request["domain_weaver_reissue"]["repair_policy"] == (
            "dynamic_operational_references_are_evidence_not_immutable_semantic_pins"
        )
        assert request["domain_weaver_reissue"]["prior_reissue_request_path"] in request["required_context_reads"]


def test_domain_weaver_20260601b_reissue_action_starts_two_workers_when_confirmed(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_domain_weaver_20260601b_reaudit_return(tmp_path)

    calls = []

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": f"ION/05_context/current/chatgpt_connector/codex_queue_runs/reissue_{len(calls)}/run.json",
                "pid": 9400 + len(calls),
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_20260601b_context_rebaseline_and_two_reissue",
            "confirmation": CONFIRMATION,
            "packet_id": "PCKT-DOMAIN-WEAVER-LIVE-FANIN-20260601B-CONTEXT-REBASELINE-AND-TWO-REISSUE",
            "start_workers": True,
            "live_execution_confirmation": "ION_DOMAIN_WEAVER_LIVE_EXECUTION_CONFIRMED",
        },
    )

    assert result["ok"] is True
    assert result["summary"]["queued_request_count"] == 2
    assert result["summary"]["worker_started_count"] == 2
    assert len(calls) == 2
    assert all(call["start"] is True for call in calls)
    assert all(call["background"] is True for call in calls)


def test_queue_governor_projects_clean_queue_without_domain_weaver_wrapper(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    projection = build_queue_governor_projection(tmp_path)

    assert projection["schema_id"] == "ion.queue_governor.projection.v0_1"
    assert projection["status"] == "queue_governor_ready"
    assert projection["summary"]["waiting_request_count"] == 0
    assert projection["summary"]["stale_waiting_request_count"] == 0
    assert projection["summary"]["terminal_repair_request_count"] == 0
    assert projection["summary"]["active_run_count"] == 0
    assert projection["summary"]["work_lane_projection_ready"] is True
    assert projection["summary"]["worker_concurrency_ready"] is True
    assert projection["authority"]["queue_mutation_authority"] is False
    assert projection["authority"]["accepted_state_authority"] is False


def test_queue_governor_dogfood_covers_queue_churn_without_mutating_queue():
    projection = build_queue_governor_dogfood_projection()
    covered = set(projection["summary"]["covered_behaviors"])

    assert projection["schema_id"] == "ion.queue_governor.dogfood_projection.v0_1"
    assert projection["status"] == "queue_governor_dogfood_ready"
    assert projection["summary"]["failed_scenario_count"] == 0
    assert projection["summary"]["scenario_count"] >= 5
    assert {
        "stale_waiting_request",
        "terminal_return_contract_repair",
        "actionable_duplicate_group",
        "classified_terminal_backlog",
        "active_run_present",
        "needs_triage_lane",
        "bounded_worker_concurrency",
    }.issubset(covered)
    assert projection["authority"]["synthetic_scenarios_only"] is True
    assert projection["authority"]["queue_mutation_authority"] is False
    assert projection["authority"]["accepted_state_authority"] is False


def test_domain_weaver_direct_projection_self_hydrates_registry_inputs(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_codex_carrier_steward(tmp_path)

    projection = build_domain_weaver_projection(tmp_path)

    assert projection["input_hydration"]["mode"] == "self_hydrated"
    assert projection["summary"]["domain_count"] >= 1
    assert projection["summary"]["agent_count"] >= 1
    assert projection["summary"]["covered_domain_count"] >= 1
    assert projection["queue_governance"]["status"] == "queue_governance_ready"
    assert projection["queue_governance"]["queue_governor"]["schema_id"] == "ion.queue_governor.projection.v0_1"
    assert projection["queue_governance"]["queue_governor_dogfood"]["status"] == "queue_governor_dogfood_ready"
    assert projection["queue_governance"]["summary"]["queue_governor_dogfood_scenario_count"] >= 5
    assert projection["authority"]["accepted_state_authority"] is False


def test_domain_weaver_projects_queue_governance_for_stale_and_repair_work(tmp_path: Path):
    _seed_root(tmp_path)
    queue_path = tmp_path / "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json"
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_queue.v1",
                "request_count": 3,
                "total_request_count": 3,
                "duplicate_group_count": 1,
                "requests": [
                    {
                        "request_id": "codex_req_stale_queue_reconciliation",
                        "path": "ION/05_context/current/chatgpt_connector/codex_work_requests/stale.json",
                        "status": "QUEUED_FOR_CODEX_CARRIER",
                        "created_at": "2026-01-01T00:00:00+00:00",
                        "updated_at": "2026-01-01T00:00:00+00:00",
                        "objective": "Reconcile stale queue currentness and runner state.",
                        "objective_sha256": "duplicate-actionable-group",
                        "linked_return_count": 0,
                        "accepted_return_count": 0,
                    },
                    {
                        "request_id": "codex_req_template_invalid_audit",
                        "path": "ION/05_context/current/chatgpt_connector/codex_work_requests/template_invalid.json",
                        "status": "RETURN_TEMPLATE_INVALID",
                        "created_at": "2026-01-02T00:00:00+00:00",
                        "updated_at": "2026-01-02T00:05:00+00:00",
                        "objective": "Audit template invalid evidence for Domain Weaver.",
                        "objective_sha256": "duplicate-actionable-group",
                        "linked_return_count": 1,
                        "accepted_return_count": 0,
                        "settlement_relevant_automation_diagnosis": {
                            "classification": "return_template_missing_required_read_path",
                            "finding_count": 2,
                        },
                    },
                    {
                        "request_id": "codex_req_accepted",
                        "path": "ION/05_context/current/chatgpt_connector/codex_work_requests/accepted.json",
                        "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                        "created_at": "2026-01-03T00:00:00+00:00",
                        "updated_at": "2026-01-03T00:05:00+00:00",
                        "objective": "Accepted completed work.",
                        "linked_return_count": 1,
                        "accepted_return_count": 1,
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps({"schema_id": "ion.codex_queue_runner_state.v1", "active_run": None}, indent=2) + "\n",
        encoding="utf-8",
    )

    projection = build_domain_weaver_projection(tmp_path)
    governance = projection["queue_governance"]

    assert governance["status"] == "queue_governance_needs_consolidation"
    assert governance["summary"]["request_count"] == 3
    assert governance["summary"]["stale_waiting_request_count"] == 1
    assert governance["summary"]["terminal_repair_request_count"] == 1
    assert governance["summary"]["duplicate_group_count"] == 1
    assert governance["summary"]["actionable_duplicate_group_count"] == 1
    assert governance["authority"]["queue_mutation_authority"] is False
    assert any(finding["code"] == "STALE_WAITING_REQUESTS" for finding in governance["findings"])
    assert any(finding["code"] == "ACTIONABLE_DUPLICATE_QUEUE_GROUPS_PRESENT" for finding in governance["findings"])
    assert any(packet["packet_id"] == "PCKT-DOMAIN-WEAVER-QUEUE-CURRENTNESS-RECONCILIATION-20260531" for packet in governance["next_packets"])
    assert any(packet["packet_id"] == "PCKT-ION-MULTI-LANE-WORKER-QUEUE-MVP-20260530" for packet in governance["next_packets"])
    assert projection["summary"]["queue_stale_waiting_request_count"] == 1
    assert projection["operating_loop"]["summary"]["queue_governance_status"] == "queue_governance_needs_consolidation"


def test_domain_weaver_does_not_reflag_classified_terminal_queue_backlog(tmp_path: Path):
    _seed_root(tmp_path)
    queue_path = tmp_path / "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json"
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_queue.v1",
                "request_count": 1,
                "total_request_count": 1,
                "duplicate_group_count": 0,
                "requests": [
                    {
                        "request_id": "codex_req_classified_template_invalid",
                        "path": "ION/05_context/current/chatgpt_connector/codex_work_requests/classified.json",
                        "status": "RETURN_TEMPLATE_INVALID",
                        "created_at": "2026-01-02T00:00:00+00:00",
                        "updated_at": "2026-01-02T00:05:00+00:00",
                        "objective": "Classified template invalid evidence for Domain Weaver.",
                        "linked_return_count": 1,
                        "accepted_return_count": 0,
                        "payload": {
                            "queue_lifecycle_decision": {
                                "schema_id": "ion.codex_work_request_queue_lifecycle_decision.v1",
                                "disposition": "repair_return_contract_from_linked_return",
                                "request_file_mutation": "lifecycle_metadata_only",
                                "superseded": False,
                            }
                        },
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps({"schema_id": "ion.codex_queue_runner_state.v1", "active_run": None}, indent=2) + "\n",
        encoding="utf-8",
    )

    projection = build_domain_weaver_projection(tmp_path)
    governance = projection["queue_governance"]

    assert governance["status"] == "queue_governance_ready"
    assert governance["summary"]["terminal_repair_request_count"] == 0
    assert governance["summary"]["classified_terminal_backlog_count"] == 1
    assert not governance["findings"]


def test_domain_weaver_stops_recommending_multi_lane_when_lane_projection_ready(tmp_path: Path):
    _seed_root(tmp_path)
    queue_path = tmp_path / "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json"
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    request_path = "ION/05_context/current/chatgpt_connector/codex_work_requests/comms.json"
    queue_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_queue.v1",
                "request_count": 1,
                "total_request_count": 1,
                "duplicate_group_count": 0,
                "requests": [
                    {
                        "request_id": "codex_req_comms",
                        "path": request_path,
                        "status": "QUEUED_FOR_CODEX_CARRIER",
                        "lane_id": "comms_lane",
                        "work_class": "agent_invocation",
                        "created_at": "2099-01-01T00:00:00+00:00",
                        "updated_at": "2099-01-01T00:00:00+00:00",
                        "objective": "ION agent invocation for COMMS_CARTOGRAPHER (role.comms_cartographer).",
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    state_path = tmp_path / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_state.v1",
                "active_run": None,
                "active_runs": {},
                "active_lane_locks": {
                    "schema_id": "ion.codex_lane_lock_index.v0_1",
                    "same_lane_parallelism": 1,
                    "active_run_count": 0,
                },
                "concurrency": {
                    "schema_id": "ion.codex_worker_concurrency.v0_1",
                    "mode": "bounded_per_lane_workers",
                    "global_active_lock": False,
                    "same_lane_parallelism": 1,
                    "active_run_count": 0,
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    lane_index_path = tmp_path / "ION/05_context/current/chatgpt_connector/work_lanes/INDEX.json"
    lane_index_path.parent.mkdir(parents=True, exist_ok=True)
    lane_index_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.codex_work_lane_index.v0_1",
                "queued_request_count": 1,
                "executable_waiting_request_count": 1,
                "needs_triage_count": 0,
                "lane_counts": {"comms_lane": 1, "needs_triage": 0},
                "next_request_by_lane": {"comms_lane": request_path},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    projection = build_domain_weaver_projection(tmp_path)
    governance = projection["queue_governance"]
    governance_packets = [packet["packet_id"] for packet in governance["next_packets"]]
    loop_packets = [packet["packet_id"] for packet in projection["operating_loop"]["next_packets"]]

    assert governance["status"] == "queue_governance_ready"
    assert governance["summary"]["work_lane_projection_ready"] is True
    assert governance["summary"]["worker_concurrency_ready"] is True
    assert "PCKT-ION-MULTI-LANE-WORKER-QUEUE-MVP-20260530" not in governance_packets
    assert "PCKT-ION-MULTI-LANE-WORKER-QUEUE-MVP-20260530" not in loop_packets
    assert "PCKT-ION-MULTI-LANE-WORKER-CONCURRENCY-MVP-20260531" not in loop_packets


def test_domain_weaver_materializes_dogfood_context_capsule_and_advances_loop(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)

    materialize_domain_weaver_projection(tmp_path)
    result = materialize_domain_weaver_dogfood_context_capsule(tmp_path)

    assert result["schema_id"] == "ion.domain_weaver.dogfood_context_capsule_materialization.v1"
    assert result["ok"] is True
    assert result["capsule_path"] == DOMAIN_WEAVER_DOGFOOD_CONTEXT_CAPSULE_PATH.as_posix()
    assert result["next_packet_path"] == DOMAIN_WEAVER_DOGFOOD_NEXT_PACKET_PATH.as_posix()
    assert result["selected_packet_id"] in {
        "PCKT-DOMAIN-WEAVE-BLOCKER-BURN-DOWN-20260530",
        "PCKT-DOMAIN-WEAVE-COCKPIT-PANEL-MVP-20260530",
    }
    assert result["production_authority"] is False
    assert result["accepted_state_authority"] is False

    capsule = json.loads((tmp_path / DOMAIN_WEAVER_DOGFOOD_CONTEXT_CAPSULE_PATH).read_text(encoding="utf-8"))
    next_packet = json.loads((tmp_path / DOMAIN_WEAVER_DOGFOOD_NEXT_PACKET_PATH).read_text(encoding="utf-8"))
    ref_paths = {row["path"] for row in capsule["read_refs"]}

    assert capsule["schema_id"] == "ion.domain_weaver.dogfood_context_capsule.v1"
    assert capsule["status"] in {"DOGFOOD_CONTEXT_READY", "DOGFOOD_CONTEXT_NEEDS_ATTENTION"}
    assert capsule["summary"]["waiting_request_count"] == 0
    assert capsule["summary"]["work_lane_projection_ready"] is True
    assert "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json" in ref_paths
    assert "ION/05_context/current/chatgpt_connector/work_lanes/INDEX.json" in ref_paths
    assert next_packet["schema_id"] == "ion.domain_weaver.dogfood_next_packet_candidate.v1"
    assert next_packet["packet_id"] == result["selected_packet_id"]
    assert next_packet["recommended_worker"] in {"role.comms_cartographer", "role.nemesis"}

    refreshed = build_domain_weaver_projection(tmp_path)
    loop_packets = [packet["packet_id"] for packet in refreshed["operating_loop"]["next_packets"]]

    assert "PCKT-DOMAIN-WEAVE-DOGFOOD-LOOP-MVP-20260530" not in loop_packets
    assert "PCKT-DOMAIN-WEAVE-COCKPIT-PANEL-MVP-20260530" in loop_packets
    assert refreshed["operating_loop"]["summary"]["dogfood_context_materialized"] is True


def test_domain_weaver_stops_recommending_cockpit_packet_when_panel_is_ready(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/AgentControlPlanePanel.tsx",
        "\n".join(
            [
                "function DomainWeaverOpsView() {",
                "  return 'Domain Weaver operating loop QUEUE GOVERNANCE SELF-DOGFOOD STEPS NEXT BOUNDED PACKETS PROMOTION / RECEIPT PROOF';",
                "}",
                "",
            ]
        ),
    )
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/DomainWeaverCockpitPanel.tsx",
        "\n".join(
            [
                "export function DomainWeaverCockpitPanel() {",
                "  return 'Domain Weaver cockpit workbench DOMAIN WEAVER WORKBENCH QUEUE GOVERNANCE UI DEVELOPMENT NEXT BOUNDED PACKETS PROMOTION / RECEIPT PROOF';",
                "}",
                "",
            ]
        ),
    )
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/JocCockpitShell.tsx",
        "\n".join(
            [
                "import { DomainWeaverCockpitPanel } from './DomainWeaverCockpitPanel';",
                "type LivePageId = 'weave';",
                "const route = '#weave';",
                "const title = 'Domain Weaver';",
                "",
            ]
        ),
    )

    materialize_domain_weaver_projection(tmp_path)
    materialize_domain_weaver_dogfood_context_capsule(tmp_path)
    projection = build_domain_weaver_projection(tmp_path)
    loop_packets = [packet["packet_id"] for packet in projection["operating_loop"]["next_packets"]]

    assert "PCKT-DOMAIN-WEAVE-DOGFOOD-LOOP-MVP-20260530" not in loop_packets
    assert "PCKT-DOMAIN-WEAVE-COCKPIT-PANEL-MVP-20260530" not in loop_packets
    assert "PCKT-DOMAIN-WEAVE-UI-DEVELOPMENT-WORKBENCH-20260531" not in loop_packets
    assert "PCKT-DOMAIN-WEAVER-NATIVE-UI-DEVELOPMENT-WORKSURFACE-20260531" in loop_packets
    assert projection["operating_loop"]["summary"]["dogfood_context_materialized"] is True
    assert projection["operating_loop"]["summary"]["cockpit_panel_ready"] is True
    assert projection["operating_loop"]["summary"]["ui_development_ready"] is False
    assert projection["operating_loop"]["summary"]["ui_operator_usable"] is False
    assert projection["ui_development"]["summary"]["source_ready"] is True
    assert projection["ui_development"]["summary"]["operator_usable"] is False
    assert projection["ui_development"]["status"] == "ui_development_needs_native_domain_route"


def test_domain_weaver_projects_native_ui_route_before_operator_usable(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    for rel in [
        "ION/05_context/current/ai_assistant_work/protocols/UI_FRONTEND_EXCELLENCE_DOMAIN_PROTOCOL_V0_1.md",
        "ION/05_context/current/ai_assistant_work/domains/ui_frontend_excellence_domain.domain_packet.yaml",
        "ION/05_context/current/ai_assistant_work/template_specs/joc_work_surface_ui_packet.template_spec.yaml",
        "ION/03_registry/ion_skill_registry.yaml",
        "ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_UI_ROUTE_RECOVERY_RECEIPT_20260511.json",
        "ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_ORCHESTRATION_CONTEXT_PACKAGE.json",
        "ION/02_architecture/HELIXION_JOC_ORCHESTRATION_WORKFLOW_PROTOCOL.md",
        "ION/02_architecture/HELIXION_JOC_DAIMON_WISDOMNET_MASTER_EVOLUTION_PLAN.md",
        "ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_ORCHESTRATION_CONTEXT_PACKAGE.md",
        "ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_UI_WORKFLOW_GATE_RECEIPT_20260511.json",
        "ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_UI_RECOVERY_003_ANCHORED_PAGES_AND_DRAWER_CANON_RECEIPT_20260511.json",
        "ION/05_context/current/ai_assistant_work/agent_boots/JOC_UI_CANON_STEWARD.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/FRONTEND_WORK_SURFACE_ARCHITECT.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/INTERACTION_STATE_WEAVER.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/CONTEXT_VISUALIZATION_CARTOGRAPHER.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/VISUAL_PROOF_AUDITOR.agent_boot.yaml",
        "ION/08_ui/joc_cockpit_shell/CodexWorkbenchShell.tsx",
        "ION/08_ui/joc_cockpit_shell/CodexCapsuleChatWorkbenchPanel.tsx",
        "ION/08_ui/joc_cockpit_shell/ScopeCockpitPanel.tsx",
        "ION/08_ui/joc_cockpit_shell/ion-runtime-cockpit.css",
        "ION/08_ui/joc_cockpit_shell/joc-cockpit.css",
    ]:
        _write(tmp_path, rel)
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/AgentControlPlanePanel.tsx",
        "\n".join(
            [
                "function DomainWeaverOpsView() {",
                "  return 'Domain Weaver operating loop QUEUE GOVERNANCE SELF-DOGFOOD STEPS NEXT BOUNDED PACKETS PROMOTION / RECEIPT PROOF';",
                "}",
                "",
            ]
        ),
    )
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/DomainWeaverCockpitPanel.tsx",
        "\n".join(
            [
                "export function DomainWeaverCockpitPanel() {",
                "  return 'Domain Weaver cockpit workbench DOMAIN WEAVER WORKBENCH QUEUE GOVERNANCE UI DEVELOPMENT NEXT BOUNDED PACKETS PROMOTION / RECEIPT PROOF';",
                "}",
                "",
            ]
        ),
    )
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/JocCockpitShell.tsx",
        "\n".join(
            [
                "import { DomainWeaverCockpitPanel } from './DomainWeaverCockpitPanel';",
                "type LivePageId = 'weave';",
                "const route = '#weave';",
                "const title = 'Domain Weaver';",
                "",
            ]
        ),
    )
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/dist/assets/index-test.js",
        "Domain Weaver cockpit workbench DOMAIN WEAVER WORKBENCH\n",
    )

    projection = build_domain_weaver_projection(tmp_path)
    loop_packets = [packet["packet_id"] for packet in projection["operating_loop"]["next_packets"]]
    ui = projection["ui_development"]

    assert ui["status"] == "ui_development_route_execution_gate_blocked"
    assert ui["summary"]["source_ready"] is True
    assert ui["summary"]["native_ui_domain_route_ready"] is True
    assert ui["summary"]["declared_route_execution_ready"] is False
    assert ui["summary"]["domain_quality_settlement_ready"] is False
    assert ui["summary"]["build_ready"] is True
    assert ui["summary"]["operator_usable"] is False
    assert ui["native_ui_development"]["domain_id"] == "ui_frontend_excellence_domain"
    assert ui["route_execution_gate"]["summary"]["candidate_boot_counts_as_execution"] is False
    assert ui["surface_quality"]["summary"]["known_good_surface_available_count"] == 3
    assert "PCKT-DOMAIN-WEAVER-NATIVE-UI-DEVELOPMENT-WORKSURFACE-20260531" in loop_packets

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_native_ui_development_worksurface",
            "packet_id": "PCKT-DOMAIN-WEAVER-NATIVE-UI-DEVELOPMENT-WORKSURFACE-20260531",
            "confirmation": CONFIRMATION,
        },
    )

    assert result["ok"] is False
    assert result["summary"]["route_execution_gate_ready"] is False
    assert result["summary"]["blocked_reason"] == "declared_route_execution_proof_missing"
    assert result["summary"]["worker_started_count"] == 0


def test_domain_weaver_operator_feedback_rejection_blocks_ui_readiness(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    for rel in [
        "ION/05_context/current/ai_assistant_work/protocols/UI_FRONTEND_EXCELLENCE_DOMAIN_PROTOCOL_V0_1.md",
        "ION/05_context/current/ai_assistant_work/domains/ui_frontend_excellence_domain.domain_packet.yaml",
        "ION/05_context/current/ai_assistant_work/template_specs/joc_work_surface_ui_packet.template_spec.yaml",
        "ION/03_registry/ion_skill_registry.yaml",
        "ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_UI_ROUTE_RECOVERY_RECEIPT_20260511.json",
        "ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_ORCHESTRATION_CONTEXT_PACKAGE.json",
        "ION/05_context/current/ai_assistant_work/agent_boots/JOC_UI_CANON_STEWARD.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/FRONTEND_WORK_SURFACE_ARCHITECT.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/INTERACTION_STATE_WEAVER.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/CONTEXT_VISUALIZATION_CARTOGRAPHER.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/VISUAL_PROOF_AUDITOR.agent_boot.yaml",
        "ION/08_ui/joc_cockpit_shell/CodexWorkbenchShell.tsx",
        "ION/08_ui/joc_cockpit_shell/CodexCapsuleChatWorkbenchPanel.tsx",
        "ION/08_ui/joc_cockpit_shell/ScopeCockpitPanel.tsx",
    ]:
        _write(tmp_path, rel)
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/AgentControlPlanePanel.tsx",
        "\n".join(
            [
                "function DomainWeaverOpsView() {",
                "  return 'Domain Weaver operating loop QUEUE GOVERNANCE SELF-DOGFOOD STEPS NEXT BOUNDED PACKETS PROMOTION / RECEIPT PROOF';",
                "}",
                "",
            ]
        ),
    )
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/DomainWeaverCockpitPanel.tsx",
        "\n".join(
            [
                "export function DomainWeaverCockpitPanel() {",
                "  return 'Domain Weaver cockpit workbench DOMAIN WEAVER WORKBENCH QUEUE GOVERNANCE UI DEVELOPMENT NEXT BOUNDED PACKETS PROMOTION / RECEIPT PROOF TOP_BAR LEFT_ICON_RAIL LEFT_DRAWER MAIN_WORK_SURFACE RIGHT_INSPECTOR RIGHT_ICON_RAIL BOTTOM_TIMELINE';",
                "}",
                "",
            ]
        ),
    )
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/JocCockpitShell.tsx",
        "\n".join(
            [
                "import { DomainWeaverCockpitPanel } from './DomainWeaverCockpitPanel';",
                "type LivePageId = 'weave';",
                "const route = '#weave';",
                "const title = 'Domain Weaver';",
                "",
            ]
        ),
    )
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/dist/assets/index-test.js",
        "Domain Weaver cockpit workbench DOMAIN WEAVER WORKBENCH\n",
    )
    _write(
        tmp_path,
        DOMAIN_WEAVER_ACTION_HISTORY_VISUAL_SMOKE_RECEIPT_PATH.as_posix(),
        json.dumps({"schema_id": "ion.playwright_domain_weaver_action_history_smoke.v0_1", "ok": True}, indent=2)
        + "\n",
    )
    _write(
        tmp_path,
        DOMAIN_WEAVER_UI_OPERATOR_FEEDBACK_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.ui_operator_feedback.v0_1_candidate",
                "status": "operator_rejected_current_ui",
                "operator_rejected_current_ui": True,
                "operator_accepted_current_ui": False,
                "reason": "Operator rejected the current Domain Weaver UI as unusable and semantically misleading.",
                "authority": {
                    "candidate_feedback_only": True,
                    "production_authority": False,
                    "live_execution_authority": False,
                    "accepted_state_authority": False,
                    "secrets_authority": False,
                },
            },
            indent=2,
        )
        + "\n",
    )

    projection = build_domain_weaver_projection(tmp_path)
    ui = projection["ui_development"]
    blockers = {row["code"] for row in projection["original_plan_compliance"]["blockers"]}

    assert ui["summary"]["source_ready"] is True
    assert ui["summary"]["work_surface_architecture_ready"] is True
    assert ui["summary"]["visual_proof_ready"] is True
    assert ui["summary"]["operator_rejected_current_ui"] is True
    assert ui["summary"]["operator_rejection_blocks_domain_weaver_evolution"] is True
    assert ui["summary"]["semantic_operator_proof_ready"] is False
    assert ui["summary"]["operator_usable"] is False
    assert ui["status"] == "ui_development_operator_rejected"
    assert projection["summary"]["ui_development_ready"] is False
    assert projection["summary"]["ui_operator_usable"] is False
    assert "OPERATOR_REJECTED_CURRENT_UI" in blockers
    assert "SEMANTIC_UI_PROOF_MISSING" in blockers


def test_domain_weaver_operator_rejection_can_be_nonblocking_for_core_evolution(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    for rel in [
        "ION/05_context/current/ai_assistant_work/protocols/UI_FRONTEND_EXCELLENCE_DOMAIN_PROTOCOL_V0_1.md",
        "ION/05_context/current/ai_assistant_work/domains/ui_frontend_excellence_domain.domain_packet.yaml",
        "ION/05_context/current/ai_assistant_work/template_specs/joc_work_surface_ui_packet.template_spec.yaml",
        "ION/03_registry/ion_skill_registry.yaml",
        "ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_UI_ROUTE_RECOVERY_RECEIPT_20260511.json",
        "ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_ORCHESTRATION_CONTEXT_PACKAGE.json",
        "ION/05_context/current/ai_assistant_work/agent_boots/JOC_UI_CANON_STEWARD.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/FRONTEND_WORK_SURFACE_ARCHITECT.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/INTERACTION_STATE_WEAVER.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/CONTEXT_VISUALIZATION_CARTOGRAPHER.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/VISUAL_PROOF_AUDITOR.agent_boot.yaml",
        "ION/08_ui/joc_cockpit_shell/CodexWorkbenchShell.tsx",
        "ION/08_ui/joc_cockpit_shell/CodexCapsuleChatWorkbenchPanel.tsx",
        "ION/08_ui/joc_cockpit_shell/ScopeCockpitPanel.tsx",
    ]:
        _write(tmp_path, rel)
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/AgentControlPlanePanel.tsx",
        "function DomainWeaverOpsView() { return 'Domain Weaver operating loop QUEUE GOVERNANCE SELF-DOGFOOD STEPS NEXT BOUNDED PACKETS PROMOTION / RECEIPT PROOF'; }\n",
    )
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/DomainWeaverCockpitPanel.tsx",
        "export function DomainWeaverCockpitPanel() { return 'Domain Weaver cockpit workbench DOMAIN WEAVER WORKBENCH QUEUE GOVERNANCE UI DEVELOPMENT NEXT BOUNDED PACKETS PROMOTION / RECEIPT PROOF TOP_BAR LEFT_ICON_RAIL LEFT_DRAWER MAIN_WORK_SURFACE RIGHT_INSPECTOR RIGHT_ICON_RAIL BOTTOM_TIMELINE'; }\n",
    )
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/JocCockpitShell.tsx",
        "import { DomainWeaverCockpitPanel } from './DomainWeaverCockpitPanel';\ntype LivePageId = 'weave';\nconst route = '#weave';\nconst title = 'Domain Weaver';\n",
    )
    _write(tmp_path, "ION/08_ui/joc_cockpit_shell/dist/assets/index-test.js", "Domain Weaver cockpit workbench DOMAIN WEAVER WORKBENCH\n")
    _write(
        tmp_path,
        DOMAIN_WEAVER_ACTION_HISTORY_VISUAL_SMOKE_RECEIPT_PATH.as_posix(),
        json.dumps({"schema_id": "ion.playwright_domain_weaver_action_history_smoke.v0_1", "ok": True}, indent=2)
        + "\n",
    )
    _write(
        tmp_path,
        DOMAIN_WEAVER_UI_OPERATOR_FEEDBACK_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.ui_operator_feedback.v0_1_candidate",
                "status": "operator_rejected_current_ui_evolution_unblocked",
                "operator_rejected_current_ui": True,
                "operator_accepted_current_ui": False,
                "operator_rejection_blocks_domain_weaver_evolution": False,
                "reason": "Operator rejected the current UI, but removed it as a core evolution blocker.",
                "authority": {
                    "candidate_feedback_only": True,
                    "production_authority": False,
                    "live_execution_authority": False,
                    "accepted_state_authority": False,
                    "secrets_authority": False,
                },
            },
            indent=2,
        )
        + "\n",
    )

    projection = build_domain_weaver_projection(tmp_path)
    ui = projection["ui_development"]
    blockers = {row["code"] for row in projection["original_plan_compliance"]["blockers"]}

    assert ui["summary"]["operator_rejected_current_ui"] is True
    assert ui["summary"]["operator_rejection_blocks_domain_weaver_evolution"] is False
    assert ui["summary"]["semantic_operator_proof_ready"] is False
    assert ui["summary"]["operator_usable"] is False
    assert ui["status"] != "ui_development_operator_rejected"
    assert projection["summary"]["ui_operator_usable"] is False
    assert "OPERATOR_REJECTED_CURRENT_UI" not in blockers
    assert "SEMANTIC_UI_PROOF_MISSING" in blockers


def test_domain_weaver_stale_visual_smoke_does_not_prove_new_ui(tmp_path: Path):
    _seed_root(tmp_path)
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/AgentControlPlanePanel.tsx",
        "\n".join(
            [
                "function DomainWeaverOpsView() {",
                "  return 'Domain Weaver operating loop QUEUE GOVERNANCE SELF-DOGFOOD STEPS NEXT BOUNDED PACKETS PROMOTION / RECEIPT PROOF';",
                "}",
                "",
            ]
        ),
    )
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/DomainWeaverCockpitPanel.tsx",
        "\n".join(
            [
                "export function DomainWeaverCockpitPanel() {",
                "  return 'Domain Weaver cockpit workbench Autonomous team map TEAM FAN-IN UI DEVELOPMENT NEXT BOUNDED PACKETS PROMOTION / RECEIPT PROOF TOP_BAR LEFT_ICON_RAIL LEFT_DRAWER MAIN_WORK_SURFACE RIGHT_INSPECTOR RIGHT_ICON_RAIL BOTTOM_TIMELINE';",
                "}",
                "",
            ]
        ),
    )
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/JocCockpitShell.tsx",
        "\n".join(
            [
                "import { DomainWeaverCockpitPanel } from './DomainWeaverCockpitPanel';",
                "type LivePageId = 'weave';",
                "const route = '#weave';",
                "const title = 'Domain Weaver';",
                "",
            ]
        ),
    )
    _write(tmp_path, "ION/08_ui/joc_cockpit_shell/ion-runtime-cockpit.css", ".ion-domain-weaver-city-map {}\n")
    _write(tmp_path, "ION/08_ui/joc_cockpit_shell/dist/index.html", "Domain Weaver cockpit workbench\n")
    _write(
        tmp_path,
        DOMAIN_WEAVER_ACTION_HISTORY_VISUAL_SMOKE_RECEIPT_PATH.as_posix(),
        json.dumps({"schema_id": "ion.playwright_domain_weaver_action_history_smoke.v0_1", "ok": True}, indent=2)
        + "\n",
    )
    os.utime(tmp_path / DOMAIN_WEAVER_ACTION_HISTORY_VISUAL_SMOKE_RECEIPT_PATH, (1000.0, 1000.0))
    for rel in [
        "ION/08_ui/joc_cockpit_shell/DomainWeaverCockpitPanel.tsx",
        "ION/08_ui/joc_cockpit_shell/JocCockpitShell.tsx",
        "ION/08_ui/joc_cockpit_shell/ion-runtime-cockpit.css",
        "ION/08_ui/joc_cockpit_shell/dist/index.html",
    ]:
        os.utime(tmp_path / rel, (2000.0, 2000.0))

    projection = build_domain_weaver_projection(tmp_path)
    ui = projection["ui_development"]
    quality_summary = ui["surface_quality"]["summary"]

    assert ui["summary"]["source_ready"] is True
    assert ui["summary"]["visual_proof_ready"] is False
    assert quality_summary["visual_smoke_raw_ok"] is True
    assert quality_summary["visual_smoke_fresh"] is False
    assert quality_summary["visual_smoke_ok"] is False
    assert quality_summary["visual_smoke_mtime_epoch_seconds"] == 1000.0
    assert quality_summary["visual_source_mtime_epoch_seconds"] == 2000.0


def test_domain_weaver_operator_rejection_routes_architecture_breach_audit_instead_of_single_ui_worker(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    for rel in [
        "ION/05_context/current/ai_assistant_work/protocols/UI_FRONTEND_EXCELLENCE_DOMAIN_PROTOCOL_V0_1.md",
        "ION/05_context/current/ai_assistant_work/domains/ui_frontend_excellence_domain.domain_packet.yaml",
        "ION/05_context/current/ai_assistant_work/template_specs/joc_work_surface_ui_packet.template_spec.yaml",
        "ION/03_registry/ion_skill_registry.yaml",
        "ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_UI_ROUTE_RECOVERY_RECEIPT_20260511.json",
        "ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_ORCHESTRATION_CONTEXT_PACKAGE.json",
        "ION/05_context/current/ai_assistant_work/agent_boots/JOC_UI_CANON_STEWARD.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/FRONTEND_WORK_SURFACE_ARCHITECT.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/INTERACTION_STATE_WEAVER.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/CONTEXT_VISUALIZATION_CARTOGRAPHER.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/VISUAL_PROOF_AUDITOR.agent_boot.yaml",
        "ION/08_ui/joc_cockpit_shell/CodexWorkbenchShell.tsx",
        "ION/08_ui/joc_cockpit_shell/CodexCapsuleChatWorkbenchPanel.tsx",
        "ION/08_ui/joc_cockpit_shell/ScopeCockpitPanel.tsx",
    ]:
        _write(tmp_path, rel)
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/AgentControlPlanePanel.tsx",
        "function DomainWeaverOpsView() { return 'Domain Weaver operating loop QUEUE GOVERNANCE SELF-DOGFOOD STEPS NEXT BOUNDED PACKETS PROMOTION / RECEIPT PROOF'; }\n",
    )
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/DomainWeaverCockpitPanel.tsx",
        "export function DomainWeaverCockpitPanel() { return 'Domain Weaver cockpit workbench DOMAIN WEAVER WORKBENCH QUEUE GOVERNANCE UI DEVELOPMENT NEXT BOUNDED PACKETS PROMOTION / RECEIPT PROOF TOP_BAR LEFT_ICON_RAIL LEFT_DRAWER MAIN_WORK_SURFACE RIGHT_INSPECTOR RIGHT_ICON_RAIL BOTTOM_TIMELINE'; }\n",
    )
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/JocCockpitShell.tsx",
        "import { DomainWeaverCockpitPanel } from './DomainWeaverCockpitPanel'; type LivePageId = 'weave'; const route = '#weave'; const title = 'Domain Weaver';\n",
    )
    _write(tmp_path, "ION/08_ui/joc_cockpit_shell/dist/assets/index-test.js", "Domain Weaver cockpit workbench\n")
    _write(
        tmp_path,
        DOMAIN_WEAVER_UI_OPERATOR_FEEDBACK_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.ui_operator_feedback.v0_1_candidate",
                "status": "operator_rejected_current_ui",
                "operator_rejected_current_ui": True,
                "operator_accepted_current_ui": False,
            },
            indent=2,
        )
        + "\n",
    )
    projection = build_domain_weaver_projection(tmp_path)
    next_packet = projection["ui_development"]["next_packet"]

    assert next_packet["packet_id"] == "PCKT-DOMAIN-WEAVER-ARCHITECTURE-BREACH-ROOT-CAUSE-AUDIT-20260531"
    assert next_packet["recommended_worker"] == "role.nemesis"
    assert "Do not start another Domain Weaver UI implementation worker." in next_packet["blocked_until_audit"]

    blocked_ui_result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_native_ui_development_worksurface",
            "packet_id": "PCKT-DOMAIN-WEAVER-NATIVE-UI-DEVELOPMENT-WORKSURFACE-20260531",
            "confirmation": CONFIRMATION,
        },
    )

    assert blocked_ui_result["ok"] is False
    assert blocked_ui_result["summary"]["ui_next_packet_ready"] is False
    assert blocked_ui_result["summary"]["worker_started_count"] == 0

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_architecture_breach_root_cause_audit",
            "packet_id": "PCKT-DOMAIN-WEAVER-ARCHITECTURE-BREACH-ROOT-CAUSE-AUDIT-20260531",
            "confirmation": CONFIRMATION,
        },
    )

    assert result["ok"] is True
    assert result["summary"]["worker_started_count"] == 0
    assert result["summary"]["architecture_breach_next_packet_ready"] is True
    ledger = json.loads((tmp_path / DOMAIN_WEAVER_ARCHITECTURE_BREACH_AUDIT_QUEUE_LEDGER_PATH).read_text(encoding="utf-8"))
    assert ledger["schema_id"] == "ion.domain_weaver.architecture_breach_root_cause_audit_queue_ledger.v0_1_candidate"
    assert ledger["queue_action"] == "queue_architecture_breach_root_cause_audit"
    request_path = tmp_path / ledger["queued_requests"][0]["packet_path"]
    request = json.loads(request_path.read_text(encoding="utf-8"))
    assert request["request_kind"] == "domain_weaver_architecture_breach_root_cause_audit"
    assert request["agent_role"] == "role.nemesis"
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["domain_weaver_architecture_breach"]["required_verdict"] == "fundamental_architecture_repair_plan_before_ui_work"
    assert request["requested_authority"]["production_authority"] is False
    assert "Needs_Routed/ION_DOMAIN_WEAVE_FULL_ION_MASTER_PLAN_v0_1.md" in request["required_context_reads"]


def test_domain_weaver_carrier_intake_does_not_settle_declared_ui_route(tmp_path: Path, monkeypatch):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    for rel in [
        "ION/05_context/current/ai_assistant_work/protocols/UI_FRONTEND_EXCELLENCE_DOMAIN_PROTOCOL_V0_1.md",
        "ION/05_context/current/ai_assistant_work/domains/ui_frontend_excellence_domain.domain_packet.yaml",
        "ION/05_context/current/ai_assistant_work/template_specs/joc_work_surface_ui_packet.template_spec.yaml",
        "ION/03_registry/ion_skill_registry.yaml",
        "ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_UI_ROUTE_RECOVERY_RECEIPT_20260511.json",
        "ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_ORCHESTRATION_CONTEXT_PACKAGE.json",
        "ION/02_architecture/HELIXION_JOC_ORCHESTRATION_WORKFLOW_PROTOCOL.md",
        "ION/02_architecture/HELIXION_JOC_DAIMON_WISDOMNET_MASTER_EVOLUTION_PLAN.md",
        "ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_ORCHESTRATION_CONTEXT_PACKAGE.md",
        "ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_UI_WORKFLOW_GATE_RECEIPT_20260511.json",
        "ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_UI_RECOVERY_003_ANCHORED_PAGES_AND_DRAWER_CANON_RECEIPT_20260511.json",
        "ION/05_context/current/ai_assistant_work/agent_boots/JOC_UI_CANON_STEWARD.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/FRONTEND_WORK_SURFACE_ARCHITECT.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/INTERACTION_STATE_WEAVER.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/CONTEXT_VISUALIZATION_CARTOGRAPHER.agent_boot.yaml",
        "ION/05_context/current/ai_assistant_work/agent_boots/VISUAL_PROOF_AUDITOR.agent_boot.yaml",
        "ION/08_ui/joc_cockpit_shell/CodexWorkbenchShell.tsx",
        "ION/08_ui/joc_cockpit_shell/CodexCapsuleChatWorkbenchPanel.tsx",
        "ION/08_ui/joc_cockpit_shell/ScopeCockpitPanel.tsx",
        "ION/08_ui/joc_cockpit_shell/ion-runtime-cockpit.css",
        "ION/08_ui/joc_cockpit_shell/joc-cockpit.css",
    ]:
        _write(tmp_path, rel)
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/AgentControlPlanePanel.tsx",
        "function DomainWeaverOpsView() { return 'Domain Weaver operating loop QUEUE GOVERNANCE SELF-DOGFOOD STEPS NEXT BOUNDED PACKETS PROMOTION / RECEIPT PROOF'; }\n",
    )
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/DomainWeaverCockpitPanel.tsx",
        "export function DomainWeaverCockpitPanel() { return 'Domain Weaver cockpit workbench DOMAIN WEAVER WORKBENCH QUEUE GOVERNANCE UI DEVELOPMENT NEXT BOUNDED PACKETS PROMOTION / RECEIPT PROOF TOP_BAR LEFT_ICON_RAIL LEFT_DRAWER MAIN_WORK_SURFACE RIGHT_INSPECTOR RIGHT_ICON_RAIL BOTTOM_TIMELINE'; }\n",
    )
    _write(
        tmp_path,
        "ION/08_ui/joc_cockpit_shell/JocCockpitShell.tsx",
        "import { DomainWeaverCockpitPanel } from './DomainWeaverCockpitPanel'; type LivePageId = 'weave'; const route = '#weave'; const title = 'Domain Weaver';\n",
    )
    _write(tmp_path, "ION/08_ui/joc_cockpit_shell/dist/assets/index-test.js", "Domain Weaver cockpit workbench\n")
    route = [
        "JOC_UI_CANON_STEWARD",
        "FRONTEND_WORK_SURFACE_ARCHITECT",
        "INTERACTION_STATE_WEAVER",
        "CONTEXT_VISUALIZATION_CARTOGRAPHER",
        "COMPONENT_BUILDER",
        "VISUAL_PROOF_AUDITOR",
    ]
    request_rel = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_native_ui_development_worksurface_20260531_attempt_001.json"
    )
    return_rel = "ION/05_context/current/chatgpt_connector/task_returns/2026-05-31T214747Z0000_task_return.json"
    _write(
        tmp_path,
        return_rel,
        json.dumps({"schema_id": "ion.task_return.v1", "accepted_for_carrier_intake": True}, indent=2) + "\n",
    )
    _write(
        tmp_path,
        request_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": "codex_req_domain_weaver_native_ui_development_worksurface_20260531_attempt_001",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "request_kind": "domain_weaver_native_ui_development_worksurface",
                "agent_role": "FRONTEND_WORK_SURFACE_ARCHITECT",
                "latest_return_packet_path": return_rel,
                "return_packet_paths": [return_rel],
                "domain_weaver_ui_development": {
                    "packet_id": "PCKT-DOMAIN-WEAVER-NATIVE-UI-DEVELOPMENT-WORKSURFACE-20260531",
                    "recommended_route": route,
                },
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        DOMAIN_WEAVER_NATIVE_UI_DEVELOPMENT_QUEUE_LEDGER_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.native_ui_development_worksurface_queue_ledger.v0_1_candidate",
                "queue_action": "queue_native_ui_development_worksurface",
                "queued_requests": [
                    {
                        "request_id": "codex_req_domain_weaver_native_ui_development_worksurface_20260531_attempt_001",
                        "packet_path": request_rel,
                        "lane_id": "implementation_lane",
                        "worker_started": True,
                    }
                ],
                "summary": {
                    "work_request_template_count": 1,
                    "queued_request_count": 1,
                    "worker_started_count": 1,
                    "max_worker_starts": 1,
                },
            },
            indent=2,
        )
        + "\n",
    )

    projection = build_domain_weaver_projection(tmp_path)
    ui = projection["ui_development"]
    gate = ui["route_execution_gate"]
    gate_summary = gate["summary"]
    blocker_codes = {row["code"] for row in projection["original_plan_compliance"]["blockers"]}

    assert gate["status"] == "critical_architecture_breach_single_worker_substitution"
    assert gate_summary["declared_route_count"] == 6
    assert gate_summary["carrier_intake_accepted_count"] == 1
    assert gate_summary["independent_worker_return_count"] == 0
    assert gate_summary["stale_context_worker_return_count"] == 1
    assert gate_summary["proof_complete_count"] == 0
    assert gate_summary["single_worker_substitution_blocked"] is True
    assert gate_summary["route_execution_ready"] is False
    assert ui["summary"]["carrier_intake_ready"] is True
    assert ui["summary"]["carrier_intake_ready_not_domain_settled"] is True
    assert ui["summary"]["domain_quality_settlement_ready"] is False
    assert ui["domain_quality_settlement"]["status"] == "carrier_intake_ready_not_domain_settled"
    assert "SINGLE_WORKER_SUBSTITUTION_BLOCKED" in blocker_codes
    assert "CARRIER_INTAKE_NOT_DOMAIN_QUALITY_SETTLEMENT" in blocker_codes

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_native_ui_development_worksurface",
            "packet_id": "PCKT-DOMAIN-WEAVER-NATIVE-UI-DEVELOPMENT-WORKSURFACE-20260531",
            "confirmation": CONFIRMATION,
        },
    )

    assert result["ok"] is False
    assert result["summary"]["blocked_reason"] == "single_worker_substitution_blocked"
    assert result["summary"]["worker_started_count"] == 0

    materialize_domain_weaver_projection(tmp_path, projection)
    route_gate_file = json.loads((tmp_path / DOMAIN_WEAVER_ROUTE_EXECUTION_GATE_PATH).read_text(encoding="utf-8"))
    assert route_gate_file["status"] == "critical_architecture_breach_single_worker_substitution"

    reaudited = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_route_execution_hard_gate_nemesis_reaudit",
            "packet_id": "PCKT-DOMAIN-WEAVER-ROUTE-EXECUTION-HARD-GATE-NEMESIS-REAUDIT-20260531",
            "confirmation": CONFIRMATION,
        },
    )

    assert reaudited["ok"] is True
    assert reaudited["summary"]["worker_started_count"] == 0
    assert reaudited["summary"]["route_execution_gate_ready_for_reaudit"] is True
    ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_ROUTE_EXECUTION_HARD_GATE_REAUDIT_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    request_path = tmp_path / ledger["queued_requests"][0]["packet_path"]
    request = json.loads(request_path.read_text(encoding="utf-8"))
    assert request["request_kind"] == "domain_weaver_route_execution_hard_gate_nemesis_reaudit"
    assert request["agent_role"] == "role.nemesis"
    assert request["requested_model"] == "gpt-5.5"
    assert request["requested_reasoning_effort"] == "xhigh"
    assert request["domain_weaver_route_execution_hard_gate_reaudit"]["single_worker_substitution_blocked"] is True
    assert DOMAIN_WEAVER_ROUTE_EXECUTION_GATE_PATH.as_posix() in request["required_context_reads"]

    calls = []
    mutable_fanout_ledger = DOMAIN_WEAVER_UI_SPECIALIST_ROUTE_FANOUT_QUEUE_LEDGER_PATH.as_posix()

    def fake_process_once(root, *, request_path=None, start=False, background=True, **_kwargs):
        calls.append({"request_path": request_path, "start": start, "background": background})
        payload = json.loads((root / request_path).read_text(encoding="utf-8"))
        if (
            mutable_fanout_ledger in payload.get("required_context_reads", [])
            and not (root / mutable_fanout_ledger).exists()
        ):
            return {
                "schema_id": "ion.codex_queue_runner.v1",
                "ok": False,
                "result": "WORKER_CONTEXT_MOUNT_INVALID",
                "finding": "required_context_missing_or_unhashed",
                "run": {"run_packet_path": "ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_failed/run.json"},
                "production_authority": False,
                "live_execution_authority": False,
            }
        return {
            "schema_id": "ion.codex_queue_runner.v1",
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": {
                "run_packet_path": f"ION/05_context/current/chatgpt_connector/codex_queue_runs/fake_ui_specialist_{len(calls)}",
                "pid": 9400 + len(calls),
            },
            "production_authority": False,
            "live_execution_authority": False,
        }

    import kernel.ion_codex_queue_runner as queue_runner

    monkeypatch.setattr(queue_runner, "process_codex_queue_once", fake_process_once)

    fanout = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_ui_specialist_route_fanout_preimplementation_review",
            "packet_id": "PCKT-DOMAIN-WEAVER-UI-SPECIALIST-ROUTE-FANOUT-AND-PREIMPLEMENTATION-REVIEW-20260531",
            "confirmation": CONFIRMATION,
            "start_workers": True,
            "live_execution_confirmation": "ION_DOMAIN_WEAVER_LIVE_EXECUTION_CONFIRMED",
        },
    )

    assert fanout["ok"] is True
    assert fanout["summary"]["missing_specialist_template_count"] == 5
    assert fanout["summary"]["worker_start_status"] == "worker_start_succeeded"
    assert fanout["summary"]["worker_started_count"] == 4
    assert fanout["summary"]["worker_start_failure_count"] == 0
    assert len(calls) == 4
    assert fanout["summary"]["queued_specialists"] == [
        "JOC_UI_CANON_STEWARD",
        "FRONTEND_WORK_SURFACE_ARCHITECT",
        "INTERACTION_STATE_WEAVER",
        "CONTEXT_VISUALIZATION_CARTOGRAPHER",
        "VISUAL_PROOF_AUDITOR",
    ]
    fanout_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_UI_SPECIALIST_ROUTE_FANOUT_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    fanout_requests = [
        json.loads((tmp_path / row["packet_path"]).read_text(encoding="utf-8"))
        for row in fanout_ledger["queued_requests"]
    ]
    assert {request["request_kind"] for request in fanout_requests} == {
        "domain_weaver_ui_specialist_preimplementation_review"
    }
    assert {request["agent_role"] for request in fanout_requests} == set(fanout["summary"]["queued_specialists"])
    required_ui_canon = {path.as_posix() for path in DOMAIN_WEAVER_UI_CANON_CONTEXT_PATHS}
    assert all(request["requested_model"] == "gpt-5.5" for request in fanout_requests)
    assert all(request["requested_reasoning_effort"] == "xhigh" for request in fanout_requests)
    assert all(
        request["codex_model_override"]["selected_model"] == "gpt-5.5"
        and request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
        for request in fanout_requests
    )
    assert all(required_ui_canon.issubset(set(request["required_context_reads"])) for request in fanout_requests)
    assert mutable_fanout_ledger not in {
        path for request in fanout_requests for path in request["required_context_reads"]
    }
    assert all(
        request["domain_weaver_ui_specialist_route_fanout"]["fanout_queue_ledger_required_context"] is False
        for request in fanout_requests
    )
    assert all(
        request["domain_weaver_ui_specialist_route_fanout"]["required_verdict"]
        == "independent_preimplementation_specialist_return_or_explicit_blocked_receipt"
        for request in fanout_requests
    )

    accepted_return_paths = []
    for request in fanout_requests:
        return_rel = (
            "ION/05_context/current/chatgpt_connector/task_returns/"
            f"{request['request_id']}_accepted_return.json"
        )
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                    "accepted_for_carrier_intake": True,
                    "context_proof_result": {"accepted": True},
                    "template_action_proof_result": {"accepted": True},
                    "workload_diff_accepted": True,
                },
                indent=2,
            )
            + "\n",
        )
        accepted_return_paths.append(return_rel)
        request_path = tmp_path / request["packet_path"]
        request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        request["latest_return_packet_path"] = return_rel
        request["return_packet_paths"] = [return_rel]
        request_path.write_text(json.dumps(request, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        _write_worker_awareness_for_request(tmp_path, request)

    activation_ledger = json.loads((tmp_path / DOMAIN_WEAVER_ACTIVATION_LEDGER_PATH).read_text(encoding="utf-8"))
    activation_ledger.setdefault("decision_records", []).append(
        {
            "request_id": "act_req_component_builder",
            "decision": "route_to_existing_agent",
            "selected_agent": "FRONTEND_WORK_SURFACE_ARCHITECT",
            "settlement_target": DOMAIN_WEAVER_ACTIVATION_LEDGER_PATH.as_posix(),
        }
    )
    (tmp_path / DOMAIN_WEAVER_ACTIVATION_LEDGER_PATH).write_text(
        json.dumps(activation_ledger, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write(
        tmp_path,
        DOMAIN_WEAVER_UI_OPERATOR_FEEDBACK_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.ui_operator_feedback.v0_1_candidate",
                "operator_rejected_current_ui": True,
                "semantic_operator_proof_ready": False,
                "feedback": "Current UI is rejected; route-ready proof must fan in to a no-code retry gate before implementation.",
            },
            indent=2,
        )
        + "\n",
    )

    materialize_domain_weaver_projection(tmp_path)
    refreshed_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    refreshed_gate = refreshed_projection["ui_development"]["route_execution_gate"]
    assert refreshed_gate["summary"]["route_execution_ready"] is True
    assert refreshed_projection["ui_development"]["next_packet"]["packet_id"] == (
        "PCKT-DOMAIN-WEAVER-UI-SPECIALIST-FANIN-AND-RETRY-GATE-20260531"
    )

    fanin = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_ui_specialist_fanin_and_retry_gate",
            "packet_id": "PCKT-DOMAIN-WEAVER-UI-SPECIALIST-FANIN-AND-RETRY-GATE-20260531",
            "confirmation": CONFIRMATION,
        },
    )

    assert fanin["ok"] is True
    assert fanin["summary"]["worker_started_count"] == 0
    assert fanin["summary"]["proof_complete_count"] == 6
    fanin_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_UI_SPECIALIST_FANIN_RETRY_GATE_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    fanin_request = json.loads((tmp_path / fanin_ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8"))
    assert fanin_request["request_kind"] == "domain_weaver_ui_specialist_fanin_retry_gate"
    assert fanin_request["agent_role"] == "role.steward"
    assert fanin_request["requested_model"] == "gpt-5.5"
    assert fanin_request["requested_reasoning_effort"] == "xhigh"
    assert fanin_request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert fanin_request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert fanin_request["domain_weaver_ui_specialist_fanin_retry_gate"]["route_execution_ready"] is True
    assert fanin_request["domain_weaver_ui_specialist_fanin_retry_gate"]["required_output"] == (
        "no_code_visual_proposal_and_retry_gate"
    )
    assert required_ui_canon.issubset(set(fanin_request["required_context_reads"]))
    assert all(path in fanin_request["required_context_reads"] for path in accepted_return_paths)
    assert all(request["packet_path"] in fanin_request["required_context_reads"] for request in fanout_requests)

    fanin_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"fake_run_{fanin_request['request_id']}/task_return_body.md"
    )
    fanin_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{fanin_request['request_id']}_accepted_return.json"
    )
    _write(
        tmp_path,
        fanin_body_rel,
        "\n".join(
            [
                "### RESULT",
                "Fan-in verdict: READY_FOR_NO_CODE_STEWARD_RETRY_GATE_REVIEW.",
                "",
                "### RECOMMENDED NEXT PACKET",
                "`PCKT-DOMAIN-WEAVER-UI-IMPLEMENTATION-RETRY-GATED-20260601-ATTEMPT-003`",
                "",
            ]
        ),
    )
    _write(
        tmp_path,
        fanin_return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": (
                    "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
                    f"{fanin_request['request_id']}_machine_receipt.json"
                ),
                "template_action_proof_result": {"touched_paths": [fanin_body_rel]},
            },
            indent=2,
        )
        + "\n",
    )
    fanin_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    fanin_request["latest_return_packet_path"] = fanin_return_rel
    fanin_request["return_packet_paths"] = [fanin_return_rel]
    (tmp_path / fanin_request["packet_path"]).write_text(
        json.dumps(fanin_request, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_worker_awareness_for_request(tmp_path, fanin_request)

    materialize_domain_weaver_projection(tmp_path)
    after_fanin_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    after_fanin_ui = after_fanin_projection["ui_development"]
    after_fanin_next_packet = after_fanin_ui["next_packet"]

    assert after_fanin_ui["ui_specialist_fanin_retry_gate"]["accepted"] is True
    assert after_fanin_ui["ui_specialist_fanin_retry_gate"]["retry_gate_ready"] is True
    assert after_fanin_ui["summary"]["ui_specialist_fanin_retry_gate_ready"] is True
    assert after_fanin_next_packet["packet_id"] == (
        "PCKT-DOMAIN-WEAVER-UI-IMPLEMENTATION-RETRY-GATED-20260601-ATTEMPT-003"
    )
    assert after_fanin_next_packet["work_class"] == "ui_development_implementation_retry_candidate"
    assert after_fanin_next_packet["source_fanin_retry_gate"]["request_path"] == fanin_request["packet_path"]
    assert "Do not restart the old UI fan-in packet; it is already accepted and proof-gated." in (
        after_fanin_next_packet["blocked_until_implementation_packet"]
    )

    retry_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_ui_implementation_retry_gated",
            "packet_id": "PCKT-DOMAIN-WEAVER-UI-IMPLEMENTATION-RETRY-GATED-20260601-ATTEMPT-003",
            "confirmation": CONFIRMATION,
        },
    )

    assert retry_queue["ok"] is True
    assert retry_queue["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert retry_queue["summary"]["worker_started_count"] == 0
    assert retry_queue["summary"]["fanin_retry_gate_ready"] is True
    assert retry_queue["summary"]["source_fanin_return_path"] == fanin_return_rel
    retry_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_UI_IMPLEMENTATION_RETRY_GATE_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    retry_request = json.loads((tmp_path / retry_ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8"))
    assert retry_request["request_kind"] == "domain_weaver_ui_implementation_retry_gated"
    assert retry_request["agent_role"] == "FRONTEND_WORK_SURFACE_ARCHITECT"
    assert retry_request["requested_model"] == "gpt-5.5"
    assert retry_request["requested_reasoning_effort"] == "xhigh"
    assert retry_request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert retry_request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert retry_request["domain_weaver_ui_implementation_retry_gate"]["source_fanin_return_path"] == fanin_return_rel
    assert retry_request["domain_weaver_ui_implementation_retry_gate"]["route_execution_ready"] is True
    assert retry_request["domain_weaver_ui_implementation_retry_gate"]["required_verdict"] == (
        "bounded_ui_retry_with_fresh_visual_proof_or_explicit_blocker"
    )
    assert retry_request["requested_authority"]["production_authority"] is False
    assert retry_request["requested_authority"]["accepted_state_claim"] is False
    assert fanin_body_rel in retry_request["required_context_reads"]
    assert DOMAIN_WEAVER_UI_OPERATOR_FEEDBACK_PATH.as_posix() in retry_request["required_context_reads"]
    assert set(after_fanin_next_packet["target_surfaces"]).issubset(set(retry_request["required_context_reads"]))

    retry_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"fake_run_{retry_request['request_id']}/task_return_body.md"
    )
    retry_visual_blocked_rel = (
        "ION/05_context/current/domain_weaver/visual_smoke/"
        "DOMAIN_WEAVER_UI_RETRY_20260601_VISUAL_PROOF_BLOCKED.json"
    )
    retry_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{retry_request['request_id']}_accepted_return.json"
    )
    retry_machine_receipt_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"{retry_request['request_id']}_machine_receipt.json"
    )
    _write(
        tmp_path,
        retry_visual_blocked_rel,
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.visual_proof_blocked.v1",
                "ok": False,
                "result": "blocked",
                "fresh_visual_proof_captured": False,
                "operator_rejection_preserved": True,
                "target_route": "/cockpit#weave",
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        retry_body_rel,
        "\n".join(
            [
                "### RESULT",
                "Implemented bounded /cockpit#weave recovery UI patch; fresh visual proof blocked.",
                "",
                "### VISUAL PROOF",
                f"Visual proof receipt: {retry_visual_blocked_rel}",
                "Fresh desktop/tablet/mobile screenshots were not captured.",
                "",
                "### RECOMMENDED NEXT PACKET",
                "PCKT-DOMAIN-WEAVER-UI-VISUAL-PROOF-AND-STEWARDSHIP-REVIEW-20260601-ATTEMPT-001",
                "",
            ]
        ),
    )
    _write(
        tmp_path,
        retry_return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": retry_machine_receipt_rel,
                "template_action_proof_result": {"touched_paths": [retry_body_rel]},
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        retry_machine_receipt_rel,
        json.dumps({"accepted_for_carrier_intake": True}, indent=2) + "\n",
    )
    retry_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    retry_request["latest_return_packet_path"] = retry_return_rel
    retry_request["return_packet_paths"] = [retry_return_rel]
    (tmp_path / retry_request["packet_path"]).write_text(
        json.dumps(retry_request, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    materialize_domain_weaver_projection(tmp_path)
    after_retry_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    after_retry_ui = after_retry_projection["ui_development"]
    after_retry_next_packet = after_retry_ui["next_packet"]

    assert after_retry_ui["ui_implementation_retry_gate"]["accepted"] is True
    assert after_retry_ui["ui_implementation_retry_gate"]["visual_review_ready"] is True
    assert after_retry_ui["ui_implementation_retry_gate"]["visual_proof_blocked"] is True
    assert after_retry_ui["summary"]["ui_implementation_retry_gate_accepted"] is True
    assert after_retry_ui["summary"]["ui_implementation_retry_visual_proof_blocked"] is True
    assert after_retry_next_packet["packet_id"] == (
        "PCKT-DOMAIN-WEAVER-UI-VISUAL-PROOF-AND-STEWARDSHIP-REVIEW-20260601-ATTEMPT-001"
    )
    assert after_retry_next_packet["work_class"] == "ui_visual_proof_and_stewardship_review"
    assert after_retry_next_packet["source_implementation_retry_gate"]["request_path"] == retry_request["packet_path"]
    assert retry_visual_blocked_rel in after_retry_next_packet["context_refs"]
    assert "Do not restart the already accepted UI implementation retry packet." in (
        after_retry_next_packet["blocked_until_visual_review"]
    )

    visual_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_ui_visual_proof_and_stewardship_review",
            "packet_id": "PCKT-DOMAIN-WEAVER-UI-VISUAL-PROOF-AND-STEWARDSHIP-REVIEW-20260601-ATTEMPT-001",
            "confirmation": CONFIRMATION,
        },
    )

    assert visual_queue["ok"] is True
    assert visual_queue["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert visual_queue["summary"]["worker_started_count"] == 0
    assert visual_queue["summary"]["implementation_retry_accepted"] is True
    assert visual_queue["summary"]["implementation_visual_review_ready"] is True
    assert visual_queue["summary"]["source_implementation_return_path"] == retry_return_rel
    assert visual_queue["summary"]["source_visual_proof_blocked_receipt_path"] == retry_visual_blocked_rel
    visual_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_UI_VISUAL_PROOF_STEWARDSHIP_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    visual_request = json.loads(
        (tmp_path / visual_ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8")
    )
    assert visual_request["request_kind"] == "domain_weaver_ui_visual_proof_and_stewardship_review"
    assert visual_request["lane_id"] == "browser_lane"
    assert visual_request["work_class"] == "browser_probe"
    assert visual_request["agent_role"] == "VISUAL_PROOF_AUDITOR"
    assert visual_request["supporting_roles"] == ["role.steward", "role.nemesis"]
    assert visual_request["requested_model"] == "gpt-5.5"
    assert visual_request["requested_reasoning_effort"] == "xhigh"
    assert visual_request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert visual_request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert visual_request["domain_weaver_ui_visual_proof_stewardship_review"][
        "source_implementation_return_path"
    ] == retry_return_rel
    assert visual_request["domain_weaver_ui_visual_proof_stewardship_review"][
        "source_visual_proof_blocked_receipt_path"
    ] == retry_visual_blocked_rel
    assert visual_request["domain_weaver_ui_visual_proof_stewardship_review"]["required_verdict"] == (
        "fresh_visual_proof_and_stewardship_verdict_or_explicit_blocker"
    )
    assert "do_not_edit_cockpit_ui" in visual_request["domain_weaver_ui_visual_proof_stewardship_review"][
        "forbidden_actions"
    ]
    assert visual_request["requested_authority"]["production_authority"] is False
    assert visual_request["requested_authority"]["accepted_state_claim"] is False
    assert retry_body_rel in visual_request["required_context_reads"]
    assert retry_visual_blocked_rel in visual_request["required_context_reads"]
    assert retry_return_rel in visual_request["required_context_reads"]
    assert set(after_retry_next_packet["target_surfaces"]).issubset(set(visual_request["required_context_reads"]))

    local_visual_proof_rel = (
        "ION/05_context/current/domain_weaver/visual_smoke/"
        "DOMAIN_WEAVER_UI_VISUAL_PROOF_20260601_LOCAL_PLAYWRIGHT.json"
    )
    model_endpoint_blocker_rel = (
        "ION/05_context/current/domain_weaver/visual_smoke/"
        "DOMAIN_WEAVER_UI_MODEL_ENDPOINT_HANG_20260601_LOCAL.json"
    )
    visual_review_rel = (
        "ION/05_context/current/domain_weaver/visual_smoke/"
        "DOMAIN_WEAVER_UI_VISUAL_STEWARDSHIP_REVIEW_20260601_LOCAL.json"
    )
    _write(
        tmp_path,
        local_visual_proof_rel,
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.visual_proof.local_playwright.v1",
                "ok": True,
                "viewports": [
                    {"name": "desktop", "horizontal_overflow": False},
                    {"name": "tablet", "horizontal_overflow": False},
                    {"name": "mobile", "horizontal_overflow": False},
                ],
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        model_endpoint_blocker_rel,
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.cockpit_model_endpoint_hang.v1",
                "finding": "cockpit_model_json_endpoint_timed_out_after_20s_zero_bytes",
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        visual_review_rel,
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.ui_visual_stewardship_review.v1",
                "source_visual_proof_path": local_visual_proof_rel,
                "fresh_visual_proof_captured": True,
                "stewardship_verdict": "fresh_visual_proof_captured_but_operator_quality_not_settled",
                "operator_rejection_superseded": False,
                "domain_quality_settlement_ready": False,
                "required_next_packet": (
                    "PCKT-DOMAIN-WEAVER-UI-SEMANTIC-REDESIGN-FANOUT-AND-COMMS-ACTIVITY-MAP-"
                    "20260601-ATTEMPT-001"
                ),
                "findings": [
                    {"code": "VISIBLE_COMMS_SURFACE_ABSENT", "severity": "blocker"},
                    {"code": "MOBILE_WORKSURFACE_NOT_INTUITIVE", "severity": "blocker"},
                ],
            },
            indent=2,
        )
        + "\n",
    )

    materialize_domain_weaver_projection(tmp_path)
    after_visual_review_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    after_visual_review_ui = after_visual_review_projection["ui_development"]
    semantic_next_packet = after_visual_review_ui["next_packet"]

    assert after_visual_review_ui["ui_visual_stewardship_review"]["review_ready"] is True
    assert after_visual_review_ui["ui_visual_stewardship_review"]["operator_rejection_superseded"] is False
    assert after_visual_review_ui["summary"]["ui_visual_stewardship_review_ready"] is True
    assert after_visual_review_ui["summary"]["ui_visual_domain_quality_settlement_ready"] is False
    assert semantic_next_packet["packet_id"] == (
        "PCKT-DOMAIN-WEAVER-UI-SEMANTIC-REDESIGN-FANOUT-AND-COMMS-ACTIVITY-MAP-20260601-ATTEMPT-001"
    )
    assert semantic_next_packet["work_class"] == "ui_semantic_redesign_fanout_gate"
    assert semantic_next_packet["source_visual_stewardship_review"]["review_path"] == visual_review_rel
    assert visual_review_rel in semantic_next_packet["context_refs"]
    assert local_visual_proof_rel in semantic_next_packet["context_refs"]
    assert model_endpoint_blocker_rel in semantic_next_packet["context_refs"]
    assert "Do not claim operator rejection is superseded by screenshots alone." in (
        semantic_next_packet["blocked_until_semantic_redesign"]
    )

    semantic_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_ui_semantic_redesign_fanout_and_comms_activity_map",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-UI-SEMANTIC-REDESIGN-FANOUT-AND-COMMS-ACTIVITY-MAP-"
                "20260601-ATTEMPT-001"
            ),
            "confirmation": CONFIRMATION,
        },
    )

    assert semantic_queue["ok"] is True
    assert semantic_queue["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert semantic_queue["summary"]["worker_started_count"] == 0
    assert semantic_queue["summary"]["route_member_count"] == 6
    assert semantic_queue["summary"]["visual_stewardship_review_ready"] is True
    semantic_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_UI_SEMANTIC_REDESIGN_FANOUT_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    semantic_requests = [
        json.loads((tmp_path / row["packet_path"]).read_text(encoding="utf-8"))
        for row in semantic_ledger["queued_requests"]
    ]
    assert {request["request_kind"] for request in semantic_requests} == {
        "domain_weaver_ui_semantic_redesign_specialist_review"
    }
    assert {request["agent_role"] for request in semantic_requests} == {
        "JOC_UI_CANON_STEWARD",
        "COMMS_ACTIVITY_SURFACE_ARCHITECT",
        "CONTEXT_VISUALIZATION_CARTOGRAPHER",
        "INTERACTION_STATE_WEAVER",
        "VISUAL_PROOF_AUDITOR",
        "role.nemesis",
    }
    assert {request["lane_id"] for request in semantic_requests} == {
        "architecture_lane",
        "comms_lane",
        "context_lane",
        "browser_lane",
        "audit_lane",
    }
    assert all(request["requested_model"] == "gpt-5.5" for request in semantic_requests)
    assert all(request["requested_reasoning_effort"] == "xhigh" for request in semantic_requests)
    assert all(
        request["codex_model_override"]["selected_model"] == "gpt-5.5"
        and request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
        for request in semantic_requests
    )
    assert all(
        request["domain_weaver_ui_semantic_redesign_fanout"]["required_verdict"]
        == "no_code_semantic_redesign_contract_or_explicit_blocker"
        for request in semantic_requests
    )
    assert all(
        "do_not_edit_cockpit_ui" in request["domain_weaver_ui_semantic_redesign_fanout"]["forbidden_actions"]
        for request in semantic_requests
    )
    assert all(request["requested_authority"]["production_authority"] is False for request in semantic_requests)
    assert all(request["requested_authority"]["accepted_state_claim"] is False for request in semantic_requests)
    assert all(visual_review_rel in request["required_context_reads"] for request in semantic_requests)
    assert all(local_visual_proof_rel in request["required_context_reads"] for request in semantic_requests)
    assert all(model_endpoint_blocker_rel in request["required_context_reads"] for request in semantic_requests)

    joc_semantic_request = next(
        request for request in semantic_requests if request["agent_role"] == "JOC_UI_CANON_STEWARD"
    )
    joc_semantic_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{joc_semantic_request['request_id']}_accepted_return.json"
    )
    _write(
        tmp_path,
        joc_semantic_return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "accepted_for_carrier_intake": True,
                "template_action_proof_result": {"touched_paths": []},
            },
            indent=2,
        )
        + "\n",
    )
    joc_semantic_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    joc_semantic_request["latest_return_packet_path"] = joc_semantic_return_rel
    joc_semantic_request["return_packet_paths"] = [joc_semantic_return_rel]
    (tmp_path / joc_semantic_request["packet_path"]).write_text(
        json.dumps(joc_semantic_request, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    semantic_requeue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_ui_semantic_redesign_fanout_and_comms_activity_map",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-UI-SEMANTIC-REDESIGN-FANOUT-AND-COMMS-ACTIVITY-MAP-"
                "20260601-ATTEMPT-001"
            ),
            "confirmation": CONFIRMATION,
        },
    )

    assert semantic_requeue["ok"] is True
    assert semantic_requeue["summary"]["route_member_count"] == 5
    assert not (
        tmp_path
        / "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_ui_semantic_redesign_joc_ui_canon_steward_20260601_attempt_002.json"
    ).exists()

    for request in semantic_requests:
        request_path = tmp_path / request["packet_path"]
        current_request = json.loads(request_path.read_text(encoding="utf-8"))
        if current_request["status"] == "RETURN_RECORDED_PROOF_ACCEPTED":
            continue
        body_rel = (
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
            f"test_{current_request['request_id']}/task_return_body.md"
        )
        return_rel = (
            "ION/05_context/current/chatgpt_connector/task_returns/"
            f"{current_request['request_id']}_accepted_return.json"
        )
        machine_rel = (
            "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
            f"{current_request['request_id']}_machine_receipt.json"
        )
        _write(
            tmp_path,
            body_rel,
            (
                "### RESULT\n"
                "verdict: NO_CODE_SEMANTIC_REDESIGN_CONTRACT\n"
                "### RECOMMENDED NEXT PACKET\n"
                "PCKT-DOMAIN-WEAVER-UI-SEMANTIC-REDESIGN-FANIN-SETTLEMENT-20260601-ATTEMPT-001\n"
            ),
        )
        _write(
            tmp_path,
            machine_rel,
            json.dumps(
                {
                    "schema_id": "ion.chatgpt_connector.task_return_machine_receipt.v1",
                    "accepted_for_carrier_intake": True,
                },
                indent=2,
            )
            + "\n",
        )
        _write(
            tmp_path,
            return_rel,
            json.dumps(
                {
                    "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                    "accepted_for_carrier_intake": True,
                    "machine_receipt_path": machine_rel,
                    "template_action_proof_result": {"touched_paths": [body_rel]},
                },
                indent=2,
            )
            + "\n",
        )
        current_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
        current_request["latest_return_packet_path"] = return_rel
        current_request["latest_task_return_machine_receipt_path"] = machine_rel
        current_request["return_packet_paths"] = [return_rel]
        request_path.write_text(json.dumps(current_request, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    visual_duplicate_path = (
        tmp_path
        / "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_ui_semantic_redesign_visual_proof_auditor_20260601_attempt_002.json"
    )
    visual_duplicate = dict(next(request for request in semantic_requests if request["agent_role"] == "VISUAL_PROOF_AUDITOR"))
    visual_duplicate["request_id"] = (
        "codex_req_domain_weaver_ui_semantic_redesign_visual_proof_auditor_20260601_attempt_002"
    )
    visual_duplicate["packet_path"] = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/"
        "codex_req_domain_weaver_ui_semantic_redesign_visual_proof_auditor_20260601_attempt_002.json"
    )
    visual_duplicate["status"] = "QUEUED_FOR_CODEX_CARRIER"
    visual_duplicate["latest_return_packet_path"] = None
    visual_duplicate["return_packet_paths"] = []
    visual_duplicate_path.write_text(
        json.dumps(visual_duplicate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    materialize_domain_weaver_projection(tmp_path)
    fanin_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    fanin_ui = fanin_projection["ui_development"]
    fanin_next_packet = fanin_ui["next_packet"]

    assert fanin_ui["ui_semantic_redesign_fanout"]["fanout_complete"] is True
    assert fanin_ui["ui_semantic_redesign_fanout"]["accepted_return_count"] == 6
    assert fanin_ui["summary"]["ui_semantic_redesign_fanout_complete"] is True
    assert fanin_next_packet["packet_id"] == (
        "PCKT-DOMAIN-WEAVER-UI-SEMANTIC-REDESIGN-FANIN-SETTLEMENT-20260601-ATTEMPT-001"
    )
    assert fanin_next_packet["work_class"] == "ui_semantic_redesign_fanin_settlement"
    assert len(fanin_next_packet["source_semantic_redesign_fanout"]["accepted_route_returns"]) == 6

    fanin_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_ui_semantic_redesign_fanin_settlement",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-UI-SEMANTIC-REDESIGN-FANIN-SETTLEMENT-"
                "20260601-ATTEMPT-001"
            ),
            "confirmation": CONFIRMATION,
        },
    )

    assert fanin_queue["ok"] is True
    assert fanin_queue["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert fanin_queue["summary"]["worker_started_count"] == 0
    assert fanin_queue["summary"]["accepted_return_count"] == 6
    assert fanin_queue["summary"]["duplicate_superseded_count"] == 1
    fanin_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_UI_SEMANTIC_REDESIGN_FANIN_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    assert len(fanin_ledger["queued_requests"]) == 1
    fanin_request = json.loads(
        (tmp_path / fanin_ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8")
    )
    assert fanin_request["request_kind"] == "domain_weaver_ui_semantic_redesign_fanin_settlement"
    assert fanin_request["agent_role"] == "role.steward"
    assert fanin_request["supporting_roles"] == ["role.nemesis"]
    assert fanin_request["risk_level"] == "critical"
    assert fanin_request["requested_model"] == "gpt-5.5"
    assert fanin_request["requested_reasoning_effort"] == "xhigh"
    assert fanin_request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert fanin_request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert fanin_request["requested_authority"]["production_authority"] is False
    assert fanin_request["requested_authority"]["live_execution_authority"] is False
    assert fanin_request["requested_authority"]["accepted_state_claim"] is False
    assert fanin_request["domain_weaver_ui_semantic_redesign_fanin"]["accepted_return_count"] == 6
    assert (
        fanin_request["domain_weaver_ui_semantic_redesign_fanin"]["required_verdict"]
        == "semantic_redesign_settlement_contract_or_explicit_blocker"
    )
    assert "do_not_edit_cockpit_ui" in fanin_request["domain_weaver_ui_semantic_redesign_fanin"]["forbidden_actions"]
    assert all(
        request["latest_return_packet_path"] in fanin_request["required_context_reads"]
        for request in [
            json.loads((tmp_path / row["packet_path"]).read_text(encoding="utf-8"))
            for row in semantic_ledger["queued_requests"]
        ]
    )
    superseded_duplicate = json.loads(visual_duplicate_path.read_text(encoding="utf-8"))
    assert superseded_duplicate["status"] == "SUPERSEDED_DUPLICATE_AFTER_ACCEPTED_ROLE_RETURN"
    assert superseded_duplicate["queue_lifecycle_decision"]["effective_replacement_accepted"] is True

    fanin_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"test_{fanin_request['request_id']}/task_return_body.md"
    )
    fanin_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{fanin_request['request_id']}_accepted_return.json"
    )
    fanin_machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"{fanin_request['request_id']}_machine_receipt.json"
    )
    _write(
        tmp_path,
        fanin_body_rel,
        (
            "### CONTEXT PROOF\n"
            "### TEMPLATE ACTION PROOF\n"
            "### VALIDATION\n"
            "### RESULT\n"
            "### SEMANTIC FAN-IN\n"
            "### FINAL DESIGN CONTRACT\n"
            "### VISUAL PROPOSAL\n"
            "### IMPLEMENTATION GATE\n"
            "NOT_IMPLEMENTATION_READY\n"
            "### BLOCKERS\n"
            "### RECOMMENDED NEXT PACKET\n"
            "`PCKT-DOMAIN-WEAVER-UI-SEMANTIC-REDESIGN-MOCK-PROOF-STEWARDSHIP-NEMESIS-GATE-20260601-ATTEMPT-001`\n"
            "### WORKLOAD DIFF\n"
            "### ION OPERATIONAL POSTURE\n"
            "operator_rejection_superseded=false\n"
        ),
    )
    _write(
        tmp_path,
        fanin_machine_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_connector.task_return_machine_receipt.v1",
                "accepted_for_carrier_intake": True,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        fanin_return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": fanin_machine_rel,
                "template_action_proof_result": {"touched_paths": [fanin_body_rel]},
            },
            indent=2,
        )
        + "\n",
    )
    fanin_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    fanin_request["latest_return_packet_path"] = fanin_return_rel
    fanin_request["latest_task_return_machine_receipt_path"] = fanin_machine_rel
    fanin_request["return_packet_paths"] = [fanin_return_rel]
    (tmp_path / fanin_request["packet_path"]).write_text(
        json.dumps(fanin_request, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    materialize_domain_weaver_projection(tmp_path)
    mock_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    mock_ui = mock_projection["ui_development"]
    mock_next_packet = mock_ui["next_packet"]

    assert mock_ui["ui_semantic_redesign_fanin"]["accepted"] is True
    assert mock_ui["summary"]["ui_semantic_redesign_fanin_accepted"] is True
    assert mock_next_packet["packet_id"] == (
        "PCKT-DOMAIN-WEAVER-UI-SEMANTIC-REDESIGN-MOCK-PROOF-STEWARDSHIP-NEMESIS-GATE-"
        "20260601-ATTEMPT-001"
    )
    assert mock_next_packet["work_class"] == "ui_semantic_redesign_mock_proof_stewardship_nemesis_gate"
    assert mock_next_packet["source_semantic_redesign_fanin"]["return_path"] == fanin_return_rel

    mock_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_ui_semantic_redesign_mock_proof_stewardship_nemesis_gate",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-UI-SEMANTIC-REDESIGN-MOCK-PROOF-STEWARDSHIP-NEMESIS-GATE-"
                "20260601-ATTEMPT-001"
            ),
            "confirmation": CONFIRMATION,
        },
    )

    assert mock_queue["ok"] is True
    assert mock_queue["summary"]["worker_started_count"] == 0
    assert mock_queue["summary"]["semantic_fanin_accepted"] is True
    mock_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_UI_SEMANTIC_REDESIGN_MOCK_PROOF_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    assert len(mock_ledger["queued_requests"]) == 1
    mock_request = json.loads((tmp_path / mock_ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8"))
    assert mock_request["request_kind"] == "domain_weaver_ui_semantic_redesign_mock_proof_stewardship_gate"
    assert mock_request["agent_role"] == "JOC_UI_CANON_STEWARD"
    assert mock_request["supporting_roles"] == ["VISUAL_PROOF_AUDITOR", "role.nemesis"]
    assert mock_request["risk_level"] == "critical"
    assert mock_request["requested_model"] == "gpt-5.5"
    assert mock_request["requested_reasoning_effort"] == "xhigh"
    assert mock_request["domain_weaver_ui_semantic_redesign_mock_proof"]["source_fanin_return_path"] == fanin_return_rel
    assert (
        mock_request["domain_weaver_ui_semantic_redesign_mock_proof"]["required_verdict"]
        == "mock_proof_stewardship_nemesis_gate_or_explicit_blocker"
    )
    assert "do_not_edit_cockpit_ui" in mock_request["domain_weaver_ui_semantic_redesign_mock_proof"]["forbidden_actions"]
    assert fanin_body_rel in mock_request["required_context_reads"]
    assert fanin_return_rel in mock_request["required_context_reads"]

    mock_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"test_{mock_request['request_id']}/task_return_body.md"
    )
    mock_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{mock_request['request_id']}_accepted_return.json"
    )
    mock_machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"{mock_request['request_id']}_machine_receipt.json"
    )
    _write(
        tmp_path,
        mock_body_rel,
        (
            "### CONTEXT PROOF\n"
            "### TEMPLATE ACTION PROOF\n"
            "### VALIDATION\n"
            "### RESULT\n"
            "### VISUAL PROPOSAL\n"
            "### STEWARDSHIP REVIEW\n"
            "MOCK_PROOF_GATE_ACCEPTED_FOR_BOUNDED_IMPLEMENTATION_PACKET_ONLY\n"
            "### NEMESIS REVIEW\n"
            "IMPLEMENTATION_ALLOWED_ONLY_AS_CANDIDATE_PATCH_WITH_FRESH_PROOF\n"
            "### IMPLEMENTATION GATE\n"
            "NEXT_PACKET_REQUIRED\n"
            "fresh visual proof required; model endpoint degraded state must be visible; operator rejection preserved\n"
            "### BLOCKERS\n"
            "### RECOMMENDED NEXT PACKET\n"
            "PCKT-DOMAIN-WEAVER-UI-SEMANTIC-REDESIGN-CANDIDATE-IMPLEMENTATION-ACTIVITY-CITY-MAP-20260601-ATTEMPT-001\n"
            "### WORKLOAD DIFF\n"
            "### ION OPERATIONAL POSTURE\n"
        ),
    )
    _write(
        tmp_path,
        mock_machine_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_connector.task_return_machine_receipt.v1",
                "accepted_for_carrier_intake": True,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        mock_return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": mock_machine_rel,
                "template_action_proof_result": {"touched_paths": [mock_body_rel]},
            },
            indent=2,
        )
        + "\n",
    )
    mock_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    mock_request["latest_return_packet_path"] = mock_return_rel
    mock_request["latest_task_return_machine_receipt_path"] = mock_machine_rel
    mock_request["return_packet_paths"] = [mock_return_rel]
    (tmp_path / mock_request["packet_path"]).write_text(
        json.dumps(mock_request, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    materialize_domain_weaver_projection(tmp_path)
    implementation_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    implementation_ui = implementation_projection["ui_development"]
    implementation_next_packet = implementation_ui["next_packet"]

    assert implementation_ui["ui_semantic_redesign_mock_proof"]["accepted"] is True
    assert implementation_ui["ui_semantic_redesign_mock_proof"]["implementation_allowed"] is True
    assert implementation_ui["summary"]["ui_semantic_redesign_mock_proof_accepted"] is True
    assert implementation_ui["summary"]["ui_semantic_redesign_mock_proof_implementation_allowed"] is True
    assert implementation_next_packet["packet_id"] == (
        "PCKT-DOMAIN-WEAVER-UI-SEMANTIC-REDESIGN-CANDIDATE-IMPLEMENTATION-ACTIVITY-CITY-MAP-"
        "20260601-ATTEMPT-001"
    )
    assert implementation_next_packet["work_class"] == (
        "ui_semantic_redesign_candidate_implementation_activity_city_map"
    )
    assert implementation_next_packet["source_semantic_redesign_mock_proof"]["return_path"] == mock_return_rel
    assert "FRONTEND_WORK_SURFACE_ARCHITECT" in implementation_next_packet["recommended_route"]
    assert "VISUAL_PROOF_AUDITOR" in implementation_next_packet["recommended_route"]
    assert "role.nemesis" in implementation_next_packet["recommended_route"]
    assert "ION/08_ui/joc_cockpit_shell/ion-runtime-cockpit.css" in implementation_next_packet["target_surfaces"]

    implementation_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_ui_semantic_redesign_candidate_implementation_activity_city_map",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-UI-SEMANTIC-REDESIGN-CANDIDATE-IMPLEMENTATION-ACTIVITY-CITY-MAP-"
                "20260601-ATTEMPT-001"
            ),
            "confirmation": CONFIRMATION,
        },
    )

    assert implementation_queue["ok"] is True
    assert implementation_queue["summary"]["worker_started_count"] == 0
    assert implementation_queue["summary"]["mock_proof_accepted"] is True
    assert implementation_queue["summary"]["mock_proof_implementation_allowed"] is True
    implementation_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_UI_SEMANTIC_REDESIGN_IMPLEMENTATION_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    assert len(implementation_ledger["queued_requests"]) == 1
    implementation_request = json.loads(
        (tmp_path / implementation_ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8")
    )
    assert implementation_request["request_kind"] == (
        "domain_weaver_ui_semantic_redesign_candidate_implementation_activity_city_map"
    )
    assert implementation_request["agent_role"] == "FRONTEND_WORK_SURFACE_ARCHITECT"
    assert implementation_request["supporting_roles"] == [
        "JOC_UI_CANON_STEWARD",
        "COMMS_ACTIVITY_SURFACE_ARCHITECT",
        "CONTEXT_VISUALIZATION_CARTOGRAPHER",
        "INTERACTION_STATE_WEAVER",
        "VISUAL_PROOF_AUDITOR",
        "role.nemesis",
    ]
    assert implementation_request["risk_level"] == "critical"
    assert implementation_request["requested_model"] == "gpt-5.5"
    assert implementation_request["requested_reasoning_effort"] == "xhigh"
    assert implementation_request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert implementation_request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert implementation_request["requested_authority"]["production_authority"] is False
    assert implementation_request["requested_authority"]["live_execution_authority"] is False
    assert implementation_request["requested_authority"]["accepted_state_claim"] is False
    assert implementation_request["requested_authority"]["service_restart_authority"] is False
    assert implementation_request["domain_weaver_ui_semantic_redesign_candidate_implementation"][
        "source_mock_proof_return_path"
    ] == mock_return_rel
    assert implementation_request["domain_weaver_ui_semantic_redesign_candidate_implementation"][
        "source_fanin_return_path"
    ] == fanin_return_rel
    assert (
        implementation_request["domain_weaver_ui_semantic_redesign_candidate_implementation"]["required_verdict"]
        == "candidate_activity_city_implementation_with_fresh_visual_proof_or_explicit_blocker"
    )
    assert "do_not_supersede_operator_rejection" in implementation_request[
        "domain_weaver_ui_semantic_redesign_candidate_implementation"
    ]["forbidden_actions"]
    assert mock_body_rel in implementation_request["required_context_reads"]
    assert mock_return_rel in implementation_request["required_context_reads"]
    assert fanin_body_rel in implementation_request["required_context_reads"]
    assert "ION/08_ui/joc_cockpit_shell/ion-runtime-cockpit.css" in implementation_request["required_context_reads"]

    candidate_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"test_{implementation_request['request_id']}/task_return_body.md"
    )
    candidate_run_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"test_{implementation_request['request_id']}/run.json"
    )
    candidate_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{implementation_request['request_id']}_accepted_return.json"
    )
    candidate_machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"{implementation_request['request_id']}_machine_receipt.json"
    )
    screenshot_proof_rel = (
        "ION/05_context/current/domain_weaver/visual_smoke/"
        "20260601T_activity_city_candidate_attempt_001/activity_city_firefox_screenshot_proof.json"
    )
    harness_manifest_rel = (
        "ION/05_context/current/domain_weaver/visual_smoke/"
        "20260601T_activity_city_candidate_attempt_001/activity_city_firefox_harness_manifest.json"
    )
    harness_html_rel = (
        "ION/05_context/current/domain_weaver/visual_smoke/"
        "20260601T_activity_city_candidate_attempt_001/activity-city-default.html"
    )
    dist_js_rel = "ION/08_ui/joc_cockpit_shell/dist/assets/index-candidate.js"
    dist_css_rel = "ION/08_ui/joc_cockpit_shell/dist/assets/index-candidate.css"
    _write(tmp_path, dist_js_rel, "Domain Weaver Activity City candidate bundle\n")
    _write(tmp_path, dist_css_rel, ".domain-weaver-activity-city { display: grid; }\n")
    _write(tmp_path, "ION/08_ui/joc_cockpit_shell/dist/index.html", "index-candidate.js index-candidate.css\n")
    _write(tmp_path, screenshot_proof_rel, json.dumps({"pass": False, "screenshots": []}, indent=2) + "\n")
    _write(tmp_path, harness_manifest_rel, json.dumps({"schema_id": "test.harness"}, indent=2) + "\n")
    _write(tmp_path, harness_html_rel, "<main>Activity City harness</main>\n")
    _write(
        tmp_path,
        candidate_body_rel,
        (
            "### RESULT\n"
            "result: BLOCKED_BUT_PRESERVED\n"
            "The candidate patch was produced but is not accepted as UI quality settlement; operator rejection remains active.\n"
            "### UI IMPLEMENTATION\n"
            f"- Built JS asset: `{dist_js_rel}`\n"
            f"- Built CSS asset: `{dist_css_rel}`\n"
            "### VISUAL PROOF\n"
            "visual_proof_verdict: BLOCKED\n"
            f"- Harness manifest: `{harness_manifest_rel}`\n"
            f"- Screenshot proof: `{screenshot_proof_rel}`\n"
            f"- Harness HTML: `{harness_html_rel}`\n"
            "### STEWARDSHIP REVIEW\n"
            "stewardship_verdict: DO_NOT_SETTLE_UI_QUALITY\n"
            "### NEMESIS REVIEW\n"
            "nemesis_verdict: REJECT_ACCEPTED_STATE_AND_OPERATOR_USABILITY_CLAIMS\n"
            "### BLOCKERS\n"
            "CODEX_CLI_TIMEOUT after 1800 seconds; model endpoint timeout degraded state persists.\n"
            "### RECOMMENDED NEXT PACKET\n"
            "PCKT-DOMAIN-WEAVER-UI-ACTIVITY-CITY-CANDIDATE-PATCH-FANIN-STEWARDSHIP-NEMESIS-VISUAL-PROOF-RECOVERY-20260601-ATTEMPT-001\n"
            "### WORKLOAD DIFF\n"
            "### ION OPERATIONAL POSTURE\n"
        ),
    )
    _write(
        tmp_path,
        candidate_run_rel,
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_run.v1",
                "status": "CODEX_CLI_TIMEOUT",
                "failure_classification": "CODEX_CLI_FAILURE",
                "request_id": implementation_request["request_id"],
                "request_path": implementation_request["packet_path"],
                "task_return_body_path": candidate_body_rel,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        candidate_machine_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_connector.task_return_machine_receipt.v1",
                "accepted_for_carrier_intake": True,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        candidate_return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": candidate_machine_rel,
                "template_action_proof_result": {"touched_paths": [candidate_body_rel]},
            },
            indent=2,
        )
        + "\n",
    )
    implementation_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    implementation_request["latest_return_packet_path"] = candidate_return_rel
    implementation_request["latest_task_return_machine_receipt_path"] = candidate_machine_rel
    implementation_request["return_packet_paths"] = [candidate_return_rel]
    (tmp_path / implementation_request["packet_path"]).write_text(
        json.dumps(implementation_request, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    materialize_domain_weaver_projection(tmp_path)
    recovery_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    recovery_ui = recovery_projection["ui_development"]
    recovery_next_packet = recovery_ui["next_packet"]

    assert recovery_ui["ui_activity_city_candidate_implementation"]["accepted"] is True
    assert recovery_ui["ui_activity_city_candidate_implementation"]["visual_proof_blocked"] is True
    assert recovery_ui["ui_activity_city_candidate_implementation"]["proof_recovery_ready"] is True
    assert recovery_ui["summary"]["ui_activity_city_candidate_implementation_accepted"] is True
    assert recovery_ui["summary"]["ui_activity_city_candidate_visual_proof_blocked"] is True
    assert recovery_ui["summary"]["ui_activity_city_candidate_proof_recovery_ready"] is True
    assert recovery_next_packet["packet_id"] == (
        "PCKT-DOMAIN-WEAVER-UI-ACTIVITY-CITY-CANDIDATE-PATCH-FANIN-STEWARDSHIP-NEMESIS-"
        "VISUAL-PROOF-RECOVERY-20260601-ATTEMPT-001"
    )
    assert recovery_next_packet["work_class"] == (
        "ui_activity_city_candidate_patch_fanin_stewardship_nemesis_visual_proof_recovery"
    )
    assert recovery_next_packet["source_activity_city_candidate_implementation"]["return_path"] == candidate_return_rel

    recovery_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_ui_activity_city_candidate_patch_fanin_stewardship_nemesis_visual_proof_recovery",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-UI-ACTIVITY-CITY-CANDIDATE-PATCH-FANIN-STEWARDSHIP-NEMESIS-"
                "VISUAL-PROOF-RECOVERY-20260601-ATTEMPT-001"
            ),
            "confirmation": CONFIRMATION,
        },
    )

    assert recovery_queue["ok"] is True
    assert recovery_queue["summary"]["worker_started_count"] == 0
    assert recovery_queue["summary"]["candidate_implementation_accepted"] is True
    assert recovery_queue["summary"]["candidate_proof_recovery_ready"] is True
    assert recovery_queue["summary"]["candidate_visual_proof_blocked"] is True
    recovery_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_UI_ACTIVITY_CITY_CANDIDATE_PATCH_RECOVERY_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert len(recovery_ledger["queued_requests"]) == 1
    recovery_request = json.loads(
        (tmp_path / recovery_ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8")
    )
    assert recovery_request["request_kind"] == (
        "domain_weaver_ui_activity_city_candidate_patch_fanin_stewardship_nemesis_visual_proof_recovery"
    )
    assert recovery_request["agent_role"] == "role.steward"
    assert recovery_request["supporting_roles"] == ["VISUAL_PROOF_AUDITOR", "JOC_UI_CANON_STEWARD", "role.nemesis"]
    assert recovery_request["risk_level"] == "critical"
    assert recovery_request["requested_model"] == "gpt-5.5"
    assert recovery_request["requested_reasoning_effort"] == "xhigh"
    assert recovery_request["codex_model_override"]["selected_model"] == "gpt-5.5"
    assert recovery_request["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    assert recovery_request["requested_authority"]["production_authority"] is False
    assert recovery_request["requested_authority"]["live_execution_authority"] is False
    assert recovery_request["requested_authority"]["accepted_state_claim"] is False
    assert recovery_request["requested_authority"]["service_restart_authority"] is False
    assert recovery_request["domain_weaver_ui_activity_city_candidate_patch_recovery"][
        "source_candidate_return_path"
    ] == candidate_return_rel
    assert recovery_request["domain_weaver_ui_activity_city_candidate_patch_recovery"]["visual_proof_blocked"] is True
    assert recovery_request["domain_weaver_ui_activity_city_candidate_patch_recovery"]["timeout_recovered"] is True
    assert (
        recovery_request["domain_weaver_ui_activity_city_candidate_patch_recovery"]["required_verdict"]
        == "candidate_patch_recovery_decision_and_visual_proof_recovery_packet_or_explicit_blocker"
    )
    assert "do_not_edit_cockpit_ui" in recovery_request[
        "domain_weaver_ui_activity_city_candidate_patch_recovery"
    ]["forbidden_actions"]
    assert candidate_body_rel in recovery_request["required_context_reads"]
    assert candidate_return_rel in recovery_request["required_context_reads"]
    assert candidate_run_rel in recovery_request["required_context_reads"]
    assert screenshot_proof_rel in recovery_request["required_context_reads"]
    assert harness_manifest_rel in recovery_request["required_context_reads"]
    assert DOMAIN_WEAVER_UI_ACTIVITY_CITY_CANDIDATE_PATCH_RECOVERY_QUEUE_LEDGER_PATH.as_posix() not in recovery_request[
        "required_context_reads"
    ]

    visual_recovery_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"test_{recovery_request['request_id']}/task_return_body.md"
    )
    visual_recovery_run_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"test_{recovery_request['request_id']}/run.json"
    )
    visual_recovery_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{recovery_request['request_id']}_accepted_return.json"
    )
    visual_recovery_machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"{recovery_request['request_id']}_machine_receipt.json"
    )
    _write(
        tmp_path,
        visual_recovery_body_rel,
        (
            "### RESULT\n"
            "result: REVISE_CANDIDATE_PATCH_AS_EVIDENCE_ONLY\n"
            "### CANDIDATE PATCH FAN-IN\n"
            "patch_classification: `revise_candidate_patch`\n"
            "### VISUAL PROOF RECOVERY\n"
            "candidate_source_preserved_quality_unsettled; use Chromium because Firefox zero-byte screenshots failed.\n"
            "Required selectors include `data-activity-city-proof`, left rail/drawer, right rail/inspector, bottom timeline, "
            "operator rejection banner, and model endpoint degraded banner.\n"
            "### STEWARDSHIP REVIEW\n"
            "candidate_source_preserved_quality_unsettled\n"
            "### NEMESIS REVIEW\n"
            "reject Firefox zero-byte proof\n"
            "### BLOCKERS\n"
            "operator rejection remains active\n"
            "### RECOMMENDED NEXT PACKET\n"
            "PCKT-DOMAIN-WEAVER-UI-ACTIVITY-CITY-VISUAL-PROOF-RECOVERY-CHROMIUM-ONLY-20260601-ATTEMPT-001\n"
            "### WORKLOAD DIFF\n"
            "### ION OPERATIONAL POSTURE\n"
        ),
    )
    _write(
        tmp_path,
        visual_recovery_run_rel,
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_run.v1",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "request_id": recovery_request["request_id"],
                "request_path": recovery_request["packet_path"],
                "task_return_body_path": visual_recovery_body_rel,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        visual_recovery_machine_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_connector.task_return_machine_receipt.v1",
                "accepted_for_carrier_intake": True,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        visual_recovery_return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": visual_recovery_machine_rel,
                "template_action_proof_result": {"touched_paths": [visual_recovery_body_rel]},
            },
            indent=2,
        )
        + "\n",
    )
    recovery_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    recovery_request["latest_return_packet_path"] = visual_recovery_return_rel
    recovery_request["latest_task_return_machine_receipt_path"] = visual_recovery_machine_rel
    recovery_request["return_packet_paths"] = [visual_recovery_return_rel]
    (tmp_path / recovery_request["packet_path"]).write_text(
        json.dumps(recovery_request, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    materialize_domain_weaver_projection(tmp_path)
    visual_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    visual_ui = visual_projection["ui_development"]
    visual_next_packet = visual_ui["next_packet"]

    assert visual_ui["ui_activity_city_candidate_patch_recovery"]["accepted"] is True
    assert visual_ui["ui_activity_city_candidate_patch_recovery"]["visual_proof_recovery_ready"] is True
    assert visual_ui["summary"]["ui_activity_city_candidate_patch_recovery_accepted"] is True
    assert visual_ui["summary"]["ui_activity_city_visual_proof_recovery_ready"] is True
    assert visual_next_packet["packet_id"] == (
        "PCKT-DOMAIN-WEAVER-UI-ACTIVITY-CITY-VISUAL-PROOF-RECOVERY-CHROMIUM-ONLY-"
        "20260601-ATTEMPT-001"
    )
    assert visual_next_packet["work_class"] == "ui_activity_city_visual_proof_recovery_chromium_only"
    assert visual_next_packet["recommended_worker"] == "VISUAL_PROOF_AUDITOR"

    visual_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_ui_activity_city_visual_proof_recovery_chromium_only",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-UI-ACTIVITY-CITY-VISUAL-PROOF-RECOVERY-CHROMIUM-ONLY-"
                "20260601-ATTEMPT-001"
            ),
            "confirmation": CONFIRMATION,
        },
    )

    assert visual_queue["ok"] is True
    assert visual_queue["summary"]["worker_started_count"] == 0
    assert visual_queue["summary"]["patch_recovery_accepted"] is True
    assert visual_queue["summary"]["visual_proof_recovery_ready"] is True
    visual_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_UI_ACTIVITY_CITY_VISUAL_PROOF_RECOVERY_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert len(visual_ledger["queued_requests"]) == 1
    visual_request = json.loads(
        (tmp_path / visual_ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8")
    )
    assert visual_request["request_kind"] == "domain_weaver_ui_activity_city_visual_proof_recovery_chromium_only"
    assert visual_request["agent_role"] == "VISUAL_PROOF_AUDITOR"
    assert visual_request["supporting_roles"] == ["JOC_UI_CANON_STEWARD", "role.nemesis"]
    assert visual_request["lane_id"] == "browser_lane"
    assert visual_request["requested_model"] == "gpt-5.5"
    assert visual_request["requested_reasoning_effort"] == "xhigh"
    assert visual_request["requested_authority"]["production_authority"] is False
    assert visual_request["requested_authority"]["live_execution_authority"] is False
    assert visual_request["requested_authority"]["accepted_state_claim"] is False
    assert visual_request["requested_authority"]["service_restart_authority"] is False
    assert visual_request["domain_weaver_ui_activity_city_visual_proof_recovery"]["proof_only"] is True
    assert (
        visual_request["domain_weaver_ui_activity_city_visual_proof_recovery"]["required_verdict"]
        == "chromium_visual_proof_triage_keep_revise_or_revert_or_explicit_blocker"
    )
    assert "do_not_edit_cockpit_ui" in visual_request[
        "domain_weaver_ui_activity_city_visual_proof_recovery"
    ]["forbidden_actions"]
    assert visual_recovery_body_rel in visual_request["required_context_reads"]
    assert visual_recovery_return_rel in visual_request["required_context_reads"]
    assert candidate_body_rel in visual_request["required_context_reads"]
    assert screenshot_proof_rel in visual_request["required_context_reads"]
    assert harness_manifest_rel in visual_request["required_context_reads"]
    assert harness_html_rel not in visual_request["required_context_reads"]
    assert DOMAIN_WEAVER_UI_ACTIVITY_CITY_VISUAL_PROOF_RECOVERY_QUEUE_LEDGER_PATH.as_posix() not in visual_request[
        "required_context_reads"
    ]

    chromium_proof_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"test_{visual_request['request_id']}/task_return_body.md"
    )
    chromium_proof_run_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"test_{visual_request['request_id']}/run.json"
    )
    chromium_proof_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{visual_request['request_id']}_accepted_return.json"
    )
    chromium_proof_machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"{visual_request['request_id']}_machine_receipt.json"
    )
    chromium_proof_dir_rel = (
        "ION/05_context/current/domain_weaver/visual_smoke/"
        "20260601T230254Z_activity_city_chromium_recovery_attempt_001"
    )
    chromium_manifest_rel = f"{chromium_proof_dir_rel}/activity_city_chromium_visual_proof.json"
    chromium_context_audit_rel = f"{chromium_proof_dir_rel}/activity_city_chromium_context_path_audit.json"
    chromium_screenshot_rels = [
        f"{chromium_proof_dir_rel}/domain-weaver-activity-city-chromium-desktop-1440x1000.png",
        f"{chromium_proof_dir_rel}/domain-weaver-activity-city-chromium-tablet-1024x900.png",
        f"{chromium_proof_dir_rel}/domain-weaver-activity-city-chromium-mobile-390x844.png",
        f"{chromium_proof_dir_rel}/domain-weaver-activity-city-chromium-mobile-360x800.png",
    ]
    for screenshot_rel in chromium_screenshot_rels:
        _write(tmp_path, screenshot_rel, "not a real png but nonzero proof fixture\n")
    _write(
        tmp_path,
        chromium_manifest_rel,
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.activity_city.chromium_visual_proof.v1",
                "summary": {
                    "all_requested_viewports_captured": True,
                    "zero_byte_screenshot_count": 0,
                    "selector_visibility_by_viewport": {
                        "tablet-1024x900": {"main_activity_surface": {"viewportVisibleCount": 0}},
                        "mobile-390x844": {"right_inspector": {"viewportVisibleCount": 0}},
                    },
                },
                "captures": [
                    {
                        "id": "desktop-1440x1000",
                        "screenshot_path": chromium_screenshot_rels[0],
                        "screenshot_size_bytes": 42,
                    },
                    {
                        "id": "tablet-1024x900",
                        "screenshot_path": chromium_screenshot_rels[1],
                        "screenshot_size_bytes": 42,
                    },
                    {
                        "id": "mobile-390x844",
                        "screenshot_path": chromium_screenshot_rels[2],
                        "screenshot_size_bytes": 42,
                    },
                    {
                        "id": "mobile-360x800",
                        "screenshot_path": chromium_screenshot_rels[3],
                        "screenshot_size_bytes": 42,
                    },
                ],
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        chromium_context_audit_rel,
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.activity_city.context_path_audit.v1",
                "all_context_receipt_paths_read": True,
                "drifted_path_count": 0,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        chromium_proof_body_rel,
        (
            "### RESULT\n"
            "verdict: `revise_required_candidate_not_operator_usable`\n"
            "keep_revise_revert: `revise`\n"
            "### VISUAL PROOF\n"
            "all_requested_viewports_captured: `True`\n"
            "zero_byte_screenshot_count: `0`\n"
            f"proof_manifest: `{chromium_manifest_rel}`\n"
            f"context_path_audit: `{chromium_context_audit_rel}`\n"
            + "".join(f"screenshot: `{rel}`\n" for rel in chromium_screenshot_rels)
            + "tablet/mobile viewport visibility failed for main surface, drawers, inspector, comms, and timeline.\n"
            "### TRIAGE\n"
            "The candidate is not operator usable; operator rejection remains active and is not superseded.\n"
            "Model endpoint degraded state remains visible.\n"
            "### RECOMMENDED NEXT PACKET\n"
            "PCKT-DOMAIN-WEAVER-UI-ACTIVITY-CITY-RESPONSIVE-VISIBILITY-AND-MODEL-ENDPOINT-REPAIR-20260601-ATTEMPT-001\n"
            "### WORKLOAD DIFF\n"
            "### ION OPERATIONAL POSTURE\n"
        ),
    )
    _write(
        tmp_path,
        chromium_proof_run_rel,
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_run.v1",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "request_id": visual_request["request_id"],
                "request_path": visual_request["packet_path"],
                "task_return_body_path": chromium_proof_body_rel,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        chromium_proof_machine_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_connector.task_return_machine_receipt.v1",
                "accepted_for_carrier_intake": True,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        chromium_proof_return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": chromium_proof_machine_rel,
                "template_action_proof_result": {"touched_paths": [chromium_proof_body_rel]},
            },
            indent=2,
        )
        + "\n",
    )
    visual_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    visual_request["latest_return_packet_path"] = chromium_proof_return_rel
    visual_request["latest_task_return_machine_receipt_path"] = chromium_proof_machine_rel
    visual_request["return_packet_paths"] = [chromium_proof_return_rel]
    (tmp_path / visual_request["packet_path"]).write_text(
        json.dumps(visual_request, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    materialize_domain_weaver_projection(tmp_path)
    responsive_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    responsive_ui = responsive_projection["ui_development"]
    responsive_next_packet = responsive_ui["next_packet"]

    assert responsive_ui["ui_activity_city_visual_proof_recovery"]["accepted"] is True
    assert responsive_ui["ui_activity_city_visual_proof_recovery"]["ui_revision_required"] is True
    assert responsive_ui["ui_activity_city_visual_proof_recovery"]["visual_artifacts_captured"] is True
    assert responsive_ui["summary"]["ui_activity_city_visual_proof_recovery_accepted"] is True
    assert responsive_ui["summary"]["ui_activity_city_responsive_repair_required"] is True
    assert responsive_next_packet["packet_id"] == (
        "PCKT-DOMAIN-WEAVER-UI-ACTIVITY-CITY-RESPONSIVE-VISIBILITY-AND-MODEL-ENDPOINT-"
        "REPAIR-20260601-ATTEMPT-001"
    )
    assert responsive_next_packet["work_class"] == "ui_activity_city_responsive_visibility_and_model_endpoint_repair"
    assert responsive_next_packet["recommended_worker"] == "FRONTEND_WORK_SURFACE_ARCHITECT"
    assert "VISUAL_PROOF_AUDITOR" in responsive_next_packet["recommended_route"]

    responsive_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_ui_activity_city_responsive_visibility_and_model_endpoint_repair",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-UI-ACTIVITY-CITY-RESPONSIVE-VISIBILITY-AND-MODEL-ENDPOINT-"
                "REPAIR-20260601-ATTEMPT-001"
            ),
            "confirmation": CONFIRMATION,
        },
    )

    assert responsive_queue["ok"] is True
    assert responsive_queue["summary"]["worker_started_count"] == 0
    assert responsive_queue["summary"]["visual_proof_recovery_accepted"] is True
    assert responsive_queue["summary"]["ui_revision_required"] is True
    assert responsive_queue["summary"]["visual_artifacts_captured"] is True
    responsive_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_UI_ACTIVITY_CITY_RESPONSIVE_REPAIR_QUEUE_LEDGER_PATH).read_text(encoding="utf-8")
    )
    assert len(responsive_ledger["queued_requests"]) == 1
    responsive_request = json.loads(
        (tmp_path / responsive_ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8")
    )
    assert responsive_request["request_kind"] == (
        "domain_weaver_ui_activity_city_responsive_visibility_and_model_endpoint_repair"
    )
    assert responsive_request["agent_role"] == "FRONTEND_WORK_SURFACE_ARCHITECT"
    assert responsive_request["supporting_roles"] == [
        "JOC_UI_CANON_STEWARD",
        "INTERACTION_STATE_WEAVER",
        "VISUAL_PROOF_AUDITOR",
        "role.nemesis",
    ]
    assert responsive_request["lane_id"] == "implementation_lane"
    assert responsive_request["requested_model"] == "gpt-5.5"
    assert responsive_request["requested_reasoning_effort"] == "xhigh"
    assert responsive_request["requested_authority"]["production_authority"] is False
    assert responsive_request["requested_authority"]["live_execution_authority"] is False
    assert responsive_request["requested_authority"]["accepted_state_claim"] is False
    assert responsive_request["requested_authority"]["service_restart_authority"] is False
    assert responsive_request["domain_weaver_ui_activity_city_responsive_repair"][
        "source_proof_manifest_path"
    ] == chromium_manifest_rel
    assert responsive_request["domain_weaver_ui_activity_city_responsive_repair"][
        "source_context_path_audit_path"
    ] == chromium_context_audit_rel
    assert responsive_request["domain_weaver_ui_activity_city_responsive_repair"][
        "source_screenshot_paths"
    ] == chromium_screenshot_rels
    assert (
        responsive_request["domain_weaver_ui_activity_city_responsive_repair"]["required_verdict"]
        == "bounded_responsive_model_endpoint_candidate_patch_with_chromium_reproof_or_explicit_blocker"
    )
    assert "do_not_claim_operator_usability" in responsive_request[
        "domain_weaver_ui_activity_city_responsive_repair"
    ]["forbidden_actions"]
    assert "do_not_supersede_operator_rejection" in responsive_request[
        "domain_weaver_ui_activity_city_responsive_repair"
    ]["forbidden_actions"]
    assert chromium_proof_body_rel in responsive_request["required_context_reads"]
    assert chromium_proof_return_rel in responsive_request["required_context_reads"]
    assert chromium_proof_run_rel in responsive_request["required_context_reads"]
    assert chromium_manifest_rel in responsive_request["required_context_reads"]
    assert chromium_context_audit_rel in responsive_request["required_context_reads"]
    for screenshot_rel in chromium_screenshot_rels:
        assert screenshot_rel in responsive_request["required_context_reads"]
    assert harness_html_rel not in responsive_request["required_context_reads"]
    assert DOMAIN_WEAVER_UI_ACTIVITY_CITY_RESPONSIVE_REPAIR_QUEUE_LEDGER_PATH.as_posix() not in responsive_request[
        "required_context_reads"
    ]

    responsive_body_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"test_{responsive_request['request_id']}/task_return_body.md"
    )
    responsive_run_rel = (
        "ION/05_context/current/chatgpt_connector/codex_queue_runs/"
        f"test_{responsive_request['request_id']}/run.json"
    )
    responsive_return_rel = (
        "ION/05_context/current/chatgpt_connector/task_returns/"
        f"{responsive_request['request_id']}_accepted_return.json"
    )
    responsive_machine_rel = (
        "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
        f"{responsive_request['request_id']}_machine_receipt.json"
    )
    responsive_proof_dir_rel = (
        "ION/05_context/current/domain_weaver/visual_smoke/"
        "20260601T232726Z_activity_city_responsive_repair_attempt_001"
    )
    responsive_manifest_rel = f"{responsive_proof_dir_rel}/activity_city_responsive_repair_chromium_visual_proof.json"
    responsive_screenshot_rels = [
        f"{responsive_proof_dir_rel}/domain-weaver-activity-city-responsive-desktop-1440x1000.png",
        f"{responsive_proof_dir_rel}/domain-weaver-activity-city-responsive-tablet-1024x900.png",
        f"{responsive_proof_dir_rel}/domain-weaver-activity-city-responsive-mobile-390x844.png",
        f"{responsive_proof_dir_rel}/domain-weaver-activity-city-responsive-mobile-360x800.png",
    ]
    for screenshot_rel in responsive_screenshot_rels:
        _write(tmp_path, screenshot_rel, "nonzero responsive png fixture\n")
    _write(
        tmp_path,
        responsive_manifest_rel,
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.activity_city.responsive_repair_chromium_visual_proof.v1",
                "summary": {
                    "all_requested_viewports_captured": True,
                    "zero_byte_screenshot_count": 0,
                    "missing_viewport_selector_count": 0,
                },
                "captures": [
                    {"id": "desktop-1440x1000", "screenshot_path": responsive_screenshot_rels[0]},
                    {"id": "tablet-1024x900", "screenshot_path": responsive_screenshot_rels[1]},
                    {"id": "mobile-390x844", "screenshot_path": responsive_screenshot_rels[2]},
                    {"id": "mobile-360x800", "screenshot_path": responsive_screenshot_rels[3]},
                ],
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        responsive_body_rel,
        (
            "### RESULT\n"
            "Implemented bounded candidate repair; not accepted-state settlement.\n"
            "### VISUAL PROOF\n"
            "triage=`keep_candidate_reproof_passed_model_mock_gated`\n"
            "missing_viewport_selectors=`none`\n"
            "zero_byte_screenshot_count=`0`\n"
            f"manifest_path: `{responsive_manifest_rel}`\n"
            + "".join(f"screenshot: `{rel}`\n" for rel in responsive_screenshot_rels)
            + "model_endpoint_live_hydration_proved: `false`\n"
            "model endpoint mock-gated; operator rejection preserved and remains active.\n"
            "### TRIAGE\n"
            "verdict: `keep_candidate_reproof_passed_model_mock_gated`\n"
            "keep_revise_revert: `keep_candidate_for_next_review_not_accepted_state`\n"
            "### BLOCKERS\n"
            "accepted-state, live hydration parity, and operator settlement remain blocked.\n"
            "### RECOMMENDED NEXT PACKET\n"
            "PCKT-DOMAIN-WEAVER-UI-ACTIVITY-CITY-OPERATOR-REVIEW-AND-LIVE-MODEL-HYDRATION-PROOF-20260601-ATTEMPT-001\n"
            "### WORKLOAD DIFF\n"
            "### ION OPERATIONAL POSTURE\n"
        ),
    )
    _write(
        tmp_path,
        responsive_run_rel,
        json.dumps(
            {
                "schema_id": "ion.codex_queue_runner_run.v1",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "request_id": responsive_request["request_id"],
                "request_path": responsive_request["packet_path"],
                "task_return_body_path": responsive_body_rel,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        responsive_machine_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_connector.task_return_machine_receipt.v1",
                "accepted_for_carrier_intake": True,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        responsive_return_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_task_return.v1",
                "accepted_for_carrier_intake": True,
                "machine_receipt_path": responsive_machine_rel,
                "template_action_proof_result": {"touched_paths": [responsive_body_rel]},
            },
            indent=2,
        )
        + "\n",
    )
    responsive_request["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
    responsive_request["latest_return_packet_path"] = responsive_return_rel
    responsive_request["latest_task_return_machine_receipt_path"] = responsive_machine_rel
    responsive_request["return_packet_paths"] = [responsive_return_rel]
    (tmp_path / responsive_request["packet_path"]).write_text(
        json.dumps(responsive_request, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    materialize_domain_weaver_projection(tmp_path)
    operator_review_projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    operator_review_ui = operator_review_projection["ui_development"]
    operator_review_next_packet = operator_review_ui["next_packet"]

    assert operator_review_ui["ui_activity_city_responsive_repair"]["accepted"] is True
    assert operator_review_ui["ui_activity_city_responsive_repair"]["operator_review_ready"] is True
    assert operator_review_ui["ui_activity_city_responsive_repair"]["visual_reproof_passed"] is True
    assert operator_review_ui["summary"]["ui_activity_city_responsive_repair_accepted"] is True
    assert operator_review_ui["summary"]["ui_activity_city_operator_review_ready"] is True
    assert operator_review_next_packet["packet_id"] == (
        "PCKT-DOMAIN-WEAVER-UI-ACTIVITY-CITY-OPERATOR-REVIEW-AND-LIVE-MODEL-HYDRATION-"
        "PROOF-20260601-ATTEMPT-001"
    )
    assert (
        operator_review_next_packet["work_class"]
        == "ui_activity_city_operator_review_and_live_model_hydration_proof"
    )
    assert operator_review_next_packet["recommended_worker"] == "VISUAL_PROOF_AUDITOR"
    assert "role.nemesis" in operator_review_next_packet["recommended_route"]

    operator_review_queue = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "queue_ui_activity_city_operator_review_and_live_model_hydration_proof",
            "packet_id": (
                "PCKT-DOMAIN-WEAVER-UI-ACTIVITY-CITY-OPERATOR-REVIEW-AND-LIVE-MODEL-HYDRATION-"
                "PROOF-20260601-ATTEMPT-001"
            ),
            "confirmation": CONFIRMATION,
        },
    )

    assert operator_review_queue["ok"] is True
    assert operator_review_queue["summary"]["worker_started_count"] == 0
    assert operator_review_queue["summary"]["responsive_repair_accepted"] is True
    assert operator_review_queue["summary"]["operator_review_ready"] is True
    operator_review_ledger = json.loads(
        (tmp_path / DOMAIN_WEAVER_UI_ACTIVITY_CITY_OPERATOR_REVIEW_HYDRATION_QUEUE_LEDGER_PATH).read_text(
            encoding="utf-8"
        )
    )
    assert len(operator_review_ledger["queued_requests"]) == 1
    operator_review_request = json.loads(
        (tmp_path / operator_review_ledger["queued_requests"][0]["packet_path"]).read_text(encoding="utf-8")
    )
    assert operator_review_request["request_kind"] == (
        "domain_weaver_ui_activity_city_operator_review_and_live_model_hydration_proof"
    )
    assert operator_review_request["agent_role"] == "VISUAL_PROOF_AUDITOR"
    assert operator_review_request["supporting_roles"] == ["role.steward", "JOC_UI_CANON_STEWARD", "role.nemesis"]
    assert operator_review_request["requested_model"] == "gpt-5.5"
    assert operator_review_request["requested_reasoning_effort"] == "xhigh"
    assert operator_review_request["requested_authority"]["production_authority"] is False
    assert operator_review_request["requested_authority"]["live_execution_authority"] is False
    assert operator_review_request["requested_authority"]["accepted_state_claim"] is False
    assert operator_review_request["requested_authority"]["service_restart_authority"] is False
    assert operator_review_request["domain_weaver_ui_activity_city_operator_review_hydration"][
        "source_proof_manifest_path"
    ] == responsive_manifest_rel
    assert operator_review_request["domain_weaver_ui_activity_city_operator_review_hydration"][
        "source_screenshot_paths"
    ] == responsive_screenshot_rels
    assert (
        operator_review_request["domain_weaver_ui_activity_city_operator_review_hydration"]["required_verdict"]
        == "operator_review_live_model_hydration_proof_or_explicit_blocker"
    )
    assert "do_not_restart_services" in operator_review_request[
        "domain_weaver_ui_activity_city_operator_review_hydration"
    ]["forbidden_actions"]
    assert "do_not_supersede_operator_rejection_without_operator_settlement_receipt" in operator_review_request[
        "domain_weaver_ui_activity_city_operator_review_hydration"
    ]["forbidden_actions"]
    assert responsive_body_rel in operator_review_request["required_context_reads"]
    assert responsive_return_rel in operator_review_request["required_context_reads"]
    assert responsive_manifest_rel in operator_review_request["required_context_reads"]
    for screenshot_rel in responsive_screenshot_rels:
        assert screenshot_rel in operator_review_request["required_context_reads"]


def test_domain_weaver_materializes_steward_ready_review_for_phase_closure_candidate(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _write(
        tmp_path,
        DOMAIN_WEAVER_DOGFOOD_NEXT_PACKET_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.dogfood_next_packet_candidate.v1",
                "packet_id": "PCKT-DOMAIN-WEAVE-STEWARD-READY-REVIEW-20260531",
                "lane_id": "settlement_lane",
                "authority": {
                    "production_authority": False,
                    "live_execution_authority": False,
                    "accepted_state_authority": False,
                    "secrets_authority": False,
                },
            },
            indent=2,
        )
        + "\n",
    )
    projection = {
        "schema_id": "ion.domain_weaver.projection.v1",
        "weave_status": "candidate_coverage_ready",
        "operating_loop": {
            "summary": {
                "cockpit_panel_ready": True,
                "dogfood_context_materialized": True,
                "next_packet_count": 0,
            }
        },
        "queue_governance": {
            "status": "queue_governance_ready",
                "summary": {
                    "queue_governor_dogfood_status": "queue_governor_dogfood_ready",
                    "queue_governor_dogfood_scenario_count": 5,
                    "queue_governor_dogfood_passed_scenario_count": 5,
                    "waiting_request_count": 0,
                    "work_lane_waiting_request_count": 0,
                "stale_waiting_request_count": 0,
                "terminal_repair_request_count": 0,
                "work_lane_needs_triage_count": 0,
                "worker_concurrency_ready": True,
                "active_run_count": 0,
            },
        },
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
    }
    capsule = {
        "schema_id": "ion.domain_weaver.dogfood_context_capsule.v1",
        "status": "DOGFOOD_CONTEXT_READY",
        "summary": {
            "queue_governance_status": "queue_governance_ready",
            "waiting_request_count": 0,
            "work_lane_waiting_request_count": 0,
        },
        "next_packet": {
            "packet_id": "PCKT-DOMAIN-WEAVE-STEWARD-READY-REVIEW-20260531",
            "lane_id": "settlement_lane",
        },
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
    }

    result = materialize_domain_weaver_steward_ready_review(tmp_path, projection, capsule)

    assert result["schema_id"] == "ion.domain_weaver.steward_ready_review_materialization.v1"
    assert result["ok"] is True
    assert result["review_path"] == DOMAIN_WEAVER_STEWARD_READY_REVIEW_PATH.as_posix()
    assert result["decision"] == "candidate_close_domain_weaver_queue_hygiene_phase"
    assert result["blocker_count"] == 0
    assert result["accepted_state_authority"] is False

    review = json.loads((tmp_path / DOMAIN_WEAVER_STEWARD_READY_REVIEW_PATH).read_text(encoding="utf-8"))
    criteria = {criterion["code"]: criterion["passed"] for criterion in review["criteria"]}

    assert review["review_status"] == "ready_for_phase_closure_candidate"
    assert review["phase_closure_candidate"]["accepted_state_claim"] is False
    assert all(criteria.values())
    assert review["summary"]["waiting_request_count"] == 0
    assert review["summary"]["operating_loop_next_packet_count"] == 0
    assert review["summary"]["current_capability_class"] == "projection_router_ready"
    assert review["summary"]["full_domain_weaver_ready"] is False
    assert review["summary"]["self_evolution_ready"] is False
    assert review["summary"]["original_plan_blocker_count"] > 0
    assert review["phase_closure_candidate"]["recommended_status"] == "projection_router_ready"
    assert {candidate["packet_id"] for candidate in review["next_evolution_candidates"]} == {
        "PCKT-DOMAIN-WEAVER-ACTIVATION-EXECUTOR-AND-FISSION-DRYRUN-MVP-20260601",
        "PCKT-DOMAIN-WEAVER-REUSABLE-QUEUE-GOVERNOR-20260531",
    }


def test_domain_weaver_materializes_phase_closure_review_after_visual_smoke(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _write(
        tmp_path,
        DOMAIN_WEAVER_DOGFOOD_NEXT_PACKET_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.dogfood_next_packet_candidate.v1",
                "packet_id": "PCKT-DOMAIN-WEAVE-STEWARD-READY-REVIEW-20260531",
                "lane_id": "settlement_lane",
                "work_class": "settlement",
                "objective": "Review the Domain Weaver dogfood capsule and ready projection receipts.",
                "recommended_worker": "role.steward",
                "authority": {
                    "production_authority": False,
                    "live_execution_authority": False,
                    "accepted_state_authority": False,
                    "secrets_authority": False,
                },
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
            },
            indent=2,
        )
        + "\n",
    )
    projection = {
        "schema_id": "ion.domain_weaver.projection.v1",
        "weave_status": "candidate_coverage_ready",
        "operating_loop": {
            "summary": {
                "cockpit_panel_ready": True,
                "dogfood_context_materialized": True,
                "next_packet_count": 0,
            }
        },
        "queue_governance": {
            "status": "queue_governance_ready",
            "summary": {
                "queue_governor_dogfood_status": "queue_governor_dogfood_ready",
                "queue_governor_dogfood_scenario_count": 5,
                "queue_governor_dogfood_passed_scenario_count": 5,
                "waiting_request_count": 0,
                "work_lane_waiting_request_count": 0,
                "stale_waiting_request_count": 0,
                "terminal_repair_request_count": 0,
                "work_lane_needs_triage_count": 0,
                "worker_concurrency_ready": True,
                "active_run_count": 0,
            },
        },
        "ui_development": {"status": "ui_development_ready"},
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
    }
    capsule = {
        "schema_id": "ion.domain_weaver.dogfood_context_capsule.v1",
        "status": "DOGFOOD_CONTEXT_READY",
        "summary": {
            "queue_governance_status": "queue_governance_ready",
            "waiting_request_count": 0,
            "work_lane_waiting_request_count": 0,
        },
        "next_packet": {
            "packet_id": "PCKT-DOMAIN-WEAVE-STEWARD-READY-REVIEW-20260531",
            "lane_id": "settlement_lane",
        },
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
    }
    steward_result = materialize_domain_weaver_steward_ready_review(tmp_path, projection, capsule)
    assert steward_result["decision"] == "candidate_close_domain_weaver_queue_hygiene_phase"
    _write(
        tmp_path,
        DOMAIN_WEAVER_OPERATOR_ACTION_HISTORY_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.operator_action_history.v0_1",
                "generated_at": "2026-05-31T00:00:00+00:00",
                "history_path": DOMAIN_WEAVER_OPERATOR_ACTION_HISTORY_PATH.as_posix(),
                "record_count": 3,
                "records": [
                    {
                        "schema_id": "ion.domain_weaver.operator_action_record.v0_1",
                        "record_id": "refresh-2",
                        "created_at": "2026-05-31T00:00:03+00:00",
                        "action": "refresh_queue_governor",
                        "ok": True,
                        "record_path": "ION/05_context/current/domain_weaver/operator_actions/refresh-2.json",
                    },
                    {
                        "schema_id": "ion.domain_weaver.operator_action_record.v0_1",
                        "record_id": "promotion-1",
                        "created_at": "2026-05-31T00:00:02+00:00",
                        "action": "materialize_promotion_review",
                        "ok": True,
                        "record_path": "ION/05_context/current/domain_weaver/operator_actions/promotion-1.json",
                    },
                    {
                        "schema_id": "ion.domain_weaver.operator_action_record.v0_1",
                        "record_id": "refresh-1",
                        "created_at": "2026-05-31T00:00:01+00:00",
                        "action": "refresh_queue_governor",
                        "ok": True,
                        "record_path": "ION/05_context/current/domain_weaver/operator_actions/refresh-1.json",
                    },
                ],
                "summary": {
                    "record_count": 3,
                    "returned_record_count": 3,
                    "failed_record_count": 0,
                    "latest_action": "refresh_queue_governor",
                    "latest_ok": True,
                    "refresh_queue_governor_count": 2,
                    "materialize_promotion_review_count": 1,
                },
                "authority": {
                    "candidate_action_history_only": True,
                    "production_authority": False,
                    "live_execution_authority": False,
                    "accepted_state_authority": False,
                    "secrets_authority": False,
                },
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
            },
            indent=2,
        )
        + "\n",
    )

    screenshot_path = DOMAIN_WEAVER_ACTION_HISTORY_VISUAL_SMOKE_RECEIPT_PATH.with_name(
        "DOMAIN_WEAVER_ACTION_HISTORY_COCKPIT.png"
    )
    _write(tmp_path, screenshot_path.as_posix(), "png\n")
    _write(
        tmp_path,
        DOMAIN_WEAVER_ACTION_HISTORY_VISUAL_SMOKE_RECEIPT_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.playwright_domain_weaver_action_history_smoke.v0_1",
                "ok": True,
                "hash_route": "#weave",
                "screenshot_path": screenshot_path.as_posix(),
                "receipt_path": DOMAIN_WEAVER_ACTION_HISTORY_VISUAL_SMOKE_RECEIPT_PATH.as_posix(),
                "action_history_row_count": 3,
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
            },
            indent=2,
        )
        + "\n",
    )

    result = materialize_domain_weaver_phase_closure_review(tmp_path)

    assert result["schema_id"] == "ion.domain_weaver.phase_closure_review_materialization.v0_1"
    assert result["ok"] is True
    assert result["review_path"] == DOMAIN_WEAVER_PHASE_CLOSURE_REVIEW_PATH.as_posix()
    assert result["decision"] == "candidate_route_steward_phase_closure_review"
    assert result["blocker_count"] == 0
    assert result["reviewed_packet_id"] == "PCKT-DOMAIN-WEAVE-STEWARD-READY-REVIEW-20260531"
    assert result["accepted_state_authority"] is False
    assert (tmp_path / result["receipt_path"]).is_file()

    review = json.loads((tmp_path / DOMAIN_WEAVER_PHASE_CLOSURE_REVIEW_PATH).read_text(encoding="utf-8"))
    criteria = {criterion["code"]: criterion["passed"] for criterion in review["criteria"]}

    assert review["review_status"] == "phase_closure_candidate_ready"
    assert review["phase_closure_candidate"]["accepted_state_claim"] is False
    assert review["recommended_next_packet"]["recommended_worker"] == "role.steward"
    assert review["summary"]["visual_smoke_ok"] is True
    assert review["summary"]["action_history_record_count"] == 3
    assert all(criteria.values())


def test_domain_weaver_marks_vnext_candidate_domains_as_covered_not_accepted(tmp_path: Path):
    _write(tmp_path, "pyproject.toml", "[project]\nname = \"ion-domain-weaver-test\"\n")
    _write(tmp_path, "ION/REPO_AUTHORITY.md", "# authority\n")
    mount = {
        "mount_id": "role_context_cartographer__domain_continuity_context_resumability",
        "agent_role_id": "role.context_cartographer",
        "domain_id": "domain.continuity_context_resumability",
        "mount_path": "ION/05_context/current/codex_agent_mounts/context_cartographer",
        "materialized": True,
        "agents_md_exists": True,
        "config_exists": True,
        "portable_context_manifest_exists": True,
        "portable_communications_exists": True,
        "portable_address_book_exists": True,
        "portable_active_context_package_md_exists": True,
    }

    projection = build_domain_weaver_projection(
        tmp_path,
        agents=[
            {
                "role_id": "role.context_cartographer",
                "display_name": "CONTEXT_CARTOGRAPHER",
                "registry_primary_domain": None,
                "registry_secondary_domains": [],
            }
        ],
        domains=[
            {
                "domain_id": "ion_vnext_context",
                "fact_posture": "inferred_candidate",
                "source_registry": "ION_VNEXT/06_context/domain_weave/dry_runs/M103I_VNEXT_DOMAIN_REGISTRY.candidate.yaml",
                "paths": ["ION_VNEXT/06_context"],
                "local_read_first_files": ["ION_VNEXT/06_context/README.md"],
            }
        ],
        codex_mounts={"mounts": [mount]},
        roster={
            "communication_directory": {
                "agents_by_role": {
                    "role.context_cartographer": {
                        "role_id": "role.context_cartographer",
                        "available_for_comms": True,
                        "can_initiate_comms": True,
                    }
                }
            }
        },
    )

    domain = projection["domains"][0]
    assert projection["weave_status"] == "candidate_coverage_ready"
    assert projection["summary"]["candidate_covered_domain_count"] == 1
    assert projection["summary"]["gap_count"] == 0
    assert domain["status"] == "candidate_covered"
    assert domain["candidate_domain"] is True
    assert domain["accepted_ion_state"] is False
    assert domain["candidate_coverage_roles"][0]["role_id"] == "role.context_cartographer"
    assert any(edge["edge_type"] == "agent_candidate_covers_domain" for edge in projection["edges"])


def test_domain_weaver_materializes_candidate_promotion_review_without_active_registry_write(tmp_path: Path):
    _seed_root(tmp_path)

    model = build_agent_control_plane_projection(tmp_path)
    result = materialize_domain_weaver_promotion_review(tmp_path, model["domain_weaver"])

    assert result["schema_id"] == "ion.domain_weaver.promotion_materialization.v1"
    assert result["ok"] is True
    assert result["review_path"] == DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()
    assert result["active_registry_write_count"] == 0
    assert result["accepted_state_count"] == 0
    assert (tmp_path / result["review_path"]).is_file()
    assert (tmp_path / result["review_markdown_path"]).is_file()
    review = json.loads((tmp_path / result["review_path"]).read_text(encoding="utf-8"))
    assert review["summary"]["candidate_domain_count"] >= 1
    assert review["summary"]["active_registry_write_count"] == 0
    assert review["summary"]["accepted_state_count"] == 0
    assert all("ION/03_registry/domains/" in decision["proposed_active_registry_target"] for decision in review["decisions"])
    for draft_path in result["candidate_draft_paths"]:
        draft = (tmp_path / draft_path).read_text(encoding="utf-8")
        assert "CANDIDATE_DRAFT_NOT_ACTIVE_REGISTRY" in draft
        assert "accepted_ion_state: false" in draft


def test_domain_weaver_materializes_candidate_promotion_gate_without_active_registry_write(tmp_path: Path):
    _seed_root(tmp_path)

    model = build_agent_control_plane_projection(tmp_path)
    projection = model["domain_weaver"]
    for domain in projection["domains"]:
        if domain.get("candidate_domain"):
            domain["read_first"] = domain.get("read_first") or ["ION_VNEXT/06_context/README.md"]
    materialize_domain_weaver_promotion_review(tmp_path, projection)
    result = materialize_domain_weaver_promotion_gate(tmp_path, projection=projection)

    assert result["schema_id"] == "ion.domain_weaver.promotion_gate_materialization.v1"
    assert result["ok"] is True
    assert result["gate_path"] == DOMAIN_WEAVER_PROMOTION_GATE_PATH.as_posix()
    assert result["active_registry_write_count"] == 0
    assert result["accepted_state_count"] == 0
    assert result["needs_materialization_count"] == 0
    assert result["target_collision_count"] == 0
    assert (tmp_path / result["gate_path"]).is_file()
    assert (tmp_path / result["gate_markdown_path"]).is_file()
    gate = json.loads((tmp_path / result["gate_path"]).read_text(encoding="utf-8"))
    assert gate["schema_id"] == "ion.domain_weaver.promotion_gate.v1"
    assert gate["summary"]["candidate_domain_count"] >= 1
    assert gate["summary"]["clean_count"] == gate["summary"]["candidate_domain_count"]
    assert gate["summary"]["active_registry_write_count"] == 0
    assert gate["summary"]["accepted_state_count"] == 0
    assert all(decision["gate_state"] == "ready_for_operator_review" for decision in gate["decisions"])
    assert all(not (tmp_path / decision["proposed_active_registry_target"]).exists() for decision in gate["decisions"])


def test_domain_weaver_operator_action_uses_policy_governed_confirmation_mode(tmp_path: Path):
    _seed_root(tmp_path)

    result = execute_domain_weaver_action(tmp_path, {"action": "refresh_queue_governor"})

    assert result["schema_id"] == "ion.domain_weaver.operator_action_result.v0_1"
    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["required_confirmation"] == "policy_governed_no_magic_operator_string"
    assert result["production_authority"] is False
    assert result["live_execution_authority"] is False
    assert result["accepted_state_authority"] is False
    assert result["authority"]["queue_mutation_authority"] is False
    assert result["authority"]["active_registry_write_authority"] is False


def test_domain_weaver_operator_action_refreshes_queue_governor_receipts(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_codex_carrier_steward(tmp_path)

    result = execute_domain_weaver_action(
        tmp_path,
        {"action": "refresh_queue_governor", "confirmation": CONFIRMATION},
    )

    assert result["ok"] is True
    assert result["action"] == "refresh_queue_governor"
    assert result["summary"]["queue_governance_status"] == "queue_governance_ready"
    assert result["summary"]["queue_governor_dogfood_status"] == "queue_governor_dogfood_ready"
    assert result["results"]["projection"]["ok"] is True
    assert result["results"]["dogfood_context_capsule"]["accepted_state_authority"] is False
    assert result["results"]["steward_ready_review"]["accepted_state_authority"] is False
    assert len(result["receipt_paths"]) == 3
    assert result["operator_action_history_path"] == DOMAIN_WEAVER_OPERATOR_ACTION_HISTORY_PATH.as_posix()
    assert (tmp_path / result["operator_action_record_path"]).is_file()
    assert (tmp_path / result["operator_action_history_path"]).is_file()
    for path in result["evidence_paths"]:
        assert (tmp_path / path).is_file()
    assert (tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).is_file()
    assert (tmp_path / DOMAIN_WEAVER_DOGFOOD_CONTEXT_CAPSULE_PATH).is_file()
    assert (tmp_path / DOMAIN_WEAVER_STEWARD_READY_REVIEW_PATH).is_file()


def test_domain_weaver_refresh_rebuilds_paginated_queue_from_request_files(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_codex_carrier_steward(tmp_path)

    requests_root = "ION/05_context/current/chatgpt_connector/codex_work_requests"
    for index in range(60):
        _write(
            tmp_path,
            f"{requests_root}/zz_terminal_{index:02d}.json",
            json.dumps(
                {
                    "request_id": f"codex_req_terminal_{index:02d}",
                    "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                    "created_at": "2026-06-01T00:00:00+00:00",
                    "updated_at": "2026-06-01T00:01:00+00:00",
                    "objective": f"Accepted terminal request {index:02d}.",
                    "objective_sha256": f"terminal-{index:02d}",
                },
                indent=2,
            )
            + "\n",
        )
    queued_rel = f"{requests_root}/aa_queued_authority_receipt.json"
    _write(
        tmp_path,
        queued_rel,
        json.dumps(
            {
                "request_id": "codex_req_queued_authority_receipt",
                "status": "QUEUED_FOR_CODEX_CARRIER",
                "work_class": "domain_weaver_wave2_explicit_accepted_state_movement_authority_receipt_issuance",
                "created_at": "2099-01-01T00:00:00+00:00",
                "updated_at": "2099-01-01T00:00:00+00:00",
                "objective": "Issue a bounded accepted_state_movement_authority receipt from proof gates.",
            },
            indent=2,
        )
        + "\n",
    )

    result = execute_domain_weaver_action(tmp_path, {"action": "refresh_queue_governor"})

    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    governance = projection["queue_governance"]
    governance_summary = governance["summary"]
    lane_index = json.loads(
        (tmp_path / "ION/05_context/current/chatgpt_connector/work_lanes/INDEX.json").read_text(encoding="utf-8")
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["results"]["projection"]["queue_projection_refresh"]["ok"] is True
    assert governance_summary["request_source"] == "work_request_files"
    assert governance_summary["request_file_count"] == 61
    assert governance_summary["queue_projection_paginated"] is True
    assert governance_summary["waiting_request_count"] == 1
    assert governance_summary["work_lane_waiting_request_count"] == 1
    assert governance_summary["work_lane_projection_ready"] is True
    assert "approval_governance_lane" in lane_index["lane_ids"]
    assert lane_index["lane_counts"]["approval_governance_lane"] == 1


def test_domain_weaver_reconciles_stale_waiting_requests_by_currentness_policy(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_codex_carrier_steward(tmp_path)

    stale_rel = "ION/05_context/current/chatgpt_connector/codex_work_requests/stale_solo_chat_packet.json"
    _write(
        tmp_path,
        stale_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": "codex_req_stale_solo_chat_packet",
                "status": "QUEUED_FOR_CODEX_CARRIER",
                "created_at": "2026-01-01T00:00:00+00:00",
                "updated_at": "2026-01-01T00:00:00+00:00",
                "lane_id": "maintenance_lane",
                "objective": "Codex solo chat work packet with stale route evidence.",
                "return_packet_paths": [],
                "latest_return_packet_path": None,
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
            },
            indent=2,
        )
        + "\n",
    )

    before = build_domain_weaver_projection(tmp_path)
    assert before["queue_governance"]["summary"]["stale_waiting_request_count"] == 1

    result = execute_domain_weaver_action(
        tmp_path,
        {"action": "reconcile_stale_waiting_requests_by_currentness_policy"},
    )

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["reconciled_count"] == 1
    assert result["summary"]["before_stale_waiting_request_count"] == 1
    assert result["summary"]["after_stale_waiting_request_count"] == 0
    assert result["summary"]["stale_waiting_request_count"] == 0
    assert result["authority"]["queue_mutation_authority"] is False
    assert result["authority"]["active_registry_write_authority"] is False
    assert (tmp_path / DOMAIN_WEAVER_STALE_WAITING_RECONCILIATION_LEDGER_PATH).is_file()

    request = json.loads((tmp_path / stale_rel).read_text(encoding="utf-8"))
    lifecycle = request["queue_lifecycle_decision"]
    assert request["status"] == "SUPERSEDED_STALE_WAITING_BY_DOMAIN_WEAVER_CURRENTNESS_POLICY"
    assert lifecycle["decision"] == "supersede_stale_waiting_request"
    assert lifecycle["queue_deletion"] is False
    assert lifecycle["accepted_state_authority"] is False

    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    assert projection["queue_governance"]["summary"]["stale_waiting_request_count"] == 0


def test_domain_weaver_reconciles_waiting_request_with_accepted_successor(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_codex_carrier_steward(tmp_path)

    requests_root = "ION/05_context/current/chatgpt_connector/codex_work_requests"
    waiting_rel = f"{requests_root}/native_ide_validation_waiting.json"
    accepted_rel = f"{requests_root}/native_ide_validation_action_native_accepted.json"
    _write(
        tmp_path,
        waiting_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": (
                    "codex_req_2026-06-02T124144829106Z_"
                    "pckt_native_ide_v4_alias_pytest_validation_20260602_attempt_001_act_as_role_stew"
                ),
                "status": "QUEUED_FOR_CODEX_CARRIER",
                "created_at": "2026-06-02T12:41:44+00:00",
                "updated_at": "2026-06-02T12:41:44+00:00",
                "lane_id": "architecture_lane",
                "request_kind": "codex_validation_packet",
                "idempotency_key": "pckt-native-ide-v4-alias-pytest-validation-20260602-attempt-001",
                "dedupe_key": "idempotency_key:pckt-native-ide-v4-alias-pytest-validation-20260602-attempt-001",
                "objective": "PCKT-NATIVE-IDE-V4-ALIAS-PYTEST-VALIDATION-20260602-ATTEMPT-001.",
                "return_packet_paths": [],
                "latest_return_packet_path": None,
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        accepted_rel,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": (
                    "codex_req_2026-06-02T124209846575Z_"
                    "pckt_native_ide_v4_alias_pytest_validation_action_native_lane_20260602_attempt_0"
                ),
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "created_at": "2026-06-02T12:42:09+00:00",
                "updated_at": "2026-06-02T12:46:09+00:00",
                "lane_id": "implementation_lane",
                "request_kind": "codex_validation_packet",
                "idempotency_key": (
                    "pckt-native-ide-v4-alias-pytest-validation-action-native-lane-20260602-attempt-001"
                ),
                "dedupe_key": (
                    "idempotency_key:pckt-native-ide-v4-alias-pytest-validation-action-native-lane-"
                    "20260602-attempt-001"
                ),
                "objective": (
                    "PCKT-NATIVE-IDE-V4-ALIAS-PYTEST-VALIDATION-ACTION-NATIVE-LANE-"
                    "20260602-ATTEMPT-001."
                ),
                "latest_return_packet_path": (
                    "ION/05_context/current/chatgpt_connector/task_returns/native_ide_accepted.json"
                ),
                "latest_task_return_machine_receipt_path": (
                    "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/native_ide_accepted.json"
                ),
                "return_packet_paths": [
                    "ION/05_context/current/chatgpt_connector/task_returns/native_ide_accepted.json"
                ],
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
            },
            indent=2,
        )
        + "\n",
    )

    before = build_domain_weaver_projection(tmp_path)
    assert before["queue_governance"]["summary"]["waiting_request_count"] == 1

    result = execute_domain_weaver_action(
        tmp_path,
        {"action": "reconcile_waiting_requests_with_accepted_successors"},
    )

    waiting = json.loads((tmp_path / waiting_rel).read_text(encoding="utf-8"))
    lifecycle = waiting["queue_lifecycle_decision"]
    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["reconciled_count"] == 1
    assert result["summary"]["before_waiting_request_count"] == 1
    assert result["summary"]["after_waiting_request_count"] == 0
    assert result["authority"]["queue_mutation_authority"] is False
    assert result["authority"]["active_registry_write_authority"] is False
    assert (tmp_path / DOMAIN_WEAVER_WAITING_ACCEPTED_SUCCESSOR_RECONCILIATION_LEDGER_PATH).is_file()
    assert waiting["status"] == "SUPERSEDED_WAITING_BY_ACCEPTED_SUCCESSOR"
    assert lifecycle["decision"] == "supersede_waiting_request_with_accepted_successor"
    assert lifecycle["replacement_request_id"].endswith(
        "pckt_native_ide_v4_alias_pytest_validation_action_native_lane_20260602_attempt_0"
    )
    assert lifecycle["queue_deletion"] is False
    assert lifecycle["accepted_state_authority"] is False
    assert projection["queue_governance"]["summary"]["waiting_request_count"] == 0


def test_domain_weaver_classifies_terminal_backlog_from_accepted_reissue(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_codex_carrier_steward(tmp_path)

    requests_root = "ION/05_context/current/chatgpt_connector/codex_work_requests"
    blocked_path = f"{requests_root}/codex_req_domain_weaver_example_20260601_attempt_001.json"
    accepted_path = f"{requests_root}/codex_req_domain_weaver_example_20260601_attempt_002.json"
    _write(
        tmp_path,
        blocked_path,
        json.dumps(
            {
                "request_id": "codex_req_domain_weaver_example_20260601_attempt_001",
                "status": "RETURN_RECORDED_PROOF_BLOCKED",
                "dedupe_key": "domain_weaver:example:001",
                "created_at": "2026-06-01T00:00:00+00:00",
                "updated_at": "2026-06-01T00:10:00+00:00",
                "objective": "Blocked Domain Weaver example attempt.",
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        accepted_path,
        json.dumps(
            {
                "request_id": "codex_req_domain_weaver_example_20260601_attempt_002",
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "dedupe_key": "domain_weaver:example:002",
                "created_at": "2026-06-01T00:20:00+00:00",
                "updated_at": "2026-06-01T00:30:00+00:00",
                "objective": "Accepted Domain Weaver example reissue.",
                "latest_return_packet_path": "ION/05_context/current/chatgpt_connector/task_returns/example.json",
                "latest_task_return_machine_receipt_path": (
                    "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/example.json"
                ),
            },
            indent=2,
        )
        + "\n",
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {"action": "classify_queue_terminal_repair_backlog_from_accepted_reissues"},
    )

    blocked = json.loads((tmp_path / blocked_path).read_text(encoding="utf-8"))
    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))
    lifecycle = blocked["queue_lifecycle_decision"]

    assert result["ok"] is True
    assert result["operator_confirmation_mode"] == "policy_governed_no_magic_operator_string"
    assert result["summary"]["classified_count"] == 1
    assert result["summary"]["before_terminal_repair_request_count"] == 1
    assert result["summary"]["after_terminal_repair_request_count"] == 0
    assert lifecycle["request_file_mutation"] == "lifecycle_metadata_only"
    assert lifecycle["replacement_request_id"] == "codex_req_domain_weaver_example_20260601_attempt_002"
    assert lifecycle["accepted_state_authority"] is False
    assert projection["queue_governance"]["summary"]["terminal_repair_request_count"] == 0
    assert projection["queue_governance"]["summary"]["classified_terminal_backlog_count"] == 1


def test_domain_weaver_classifies_native_ide_alias_terminal_from_accepted_successor(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_codex_carrier_steward(tmp_path)

    requests_root = "ION/05_context/current/chatgpt_connector/codex_work_requests"
    failed_path = f"{requests_root}/native_ide_alias_parity_failed.json"
    accepted_path = f"{requests_root}/native_ide_alias_validation_accepted.json"
    _write(
        tmp_path,
        failed_path,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": (
                    "codex_req_2026-06-02T021949598177Z_"
                    "pckt_action_native_ide_dist_status_alias_parity_repair_20260602_attempt_001_act_"
                ),
                "status": "CODEX_QUEUE_RUNNER_FAILED",
                "failure_classification": "CODEX_CLI_FAILURE",
                "created_at": "2026-06-02T02:19:49+00:00",
                "updated_at": "2026-06-02T02:20:06+00:00",
                "lane_id": "architecture_lane",
                "dedupe_key": (
                    "idempotency_key:pckt-action-native-ide-dist-status-alias-parity-repair-"
                    "20260602-attempt-001"
                ),
                "objective": "PCKT-ACTION-NATIVE-IDE-DIST-STATUS-ALIAS-PARITY-REPAIR-20260602-ATTEMPT-001.",
            },
            indent=2,
        )
        + "\n",
    )
    _write(
        tmp_path,
        accepted_path,
        json.dumps(
            {
                "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
                "request_id": (
                    "codex_req_2026-06-02T124209846575Z_"
                    "pckt_native_ide_v4_alias_pytest_validation_action_native_lane_20260602_attempt_0"
                ),
                "status": "RETURN_RECORDED_PROOF_ACCEPTED",
                "created_at": "2026-06-02T12:42:09+00:00",
                "updated_at": "2026-06-02T12:46:09+00:00",
                "lane_id": "implementation_lane",
                "dedupe_key": (
                    "idempotency_key:pckt-native-ide-v4-alias-pytest-validation-action-native-lane-"
                    "20260602-attempt-001"
                ),
                "objective": (
                    "PCKT-NATIVE-IDE-V4-ALIAS-PYTEST-VALIDATION-ACTION-NATIVE-LANE-"
                    "20260602-ATTEMPT-001."
                ),
                "latest_return_packet_path": (
                    "ION/05_context/current/chatgpt_connector/task_returns/native_ide_alias_accepted.json"
                ),
                "latest_task_return_machine_receipt_path": (
                    "ION/05_context/current/chatgpt_connector/task_return_machine_receipts/"
                    "native_ide_alias_accepted.json"
                ),
            },
            indent=2,
        )
        + "\n",
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {"action": "classify_queue_terminal_repair_backlog_from_accepted_reissues"},
    )

    failed = json.loads((tmp_path / failed_path).read_text(encoding="utf-8"))
    lifecycle = failed["queue_lifecycle_decision"]
    projection = json.loads((tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).read_text(encoding="utf-8"))

    assert result["ok"] is True
    assert result["summary"]["classified_count"] == 1
    assert result["summary"]["before_terminal_repair_request_count"] == 1
    assert result["summary"]["after_terminal_repair_request_count"] == 0
    assert lifecycle["request_file_mutation"] == "lifecycle_metadata_only"
    assert lifecycle["effective_replacement_accepted"] is True
    assert lifecycle["replacement_request_id"].endswith(
        "pckt_native_ide_v4_alias_pytest_validation_action_native_lane_20260602_attempt_0"
    )
    assert lifecycle["accepted_state_authority"] is False
    assert projection["queue_governance"]["summary"]["terminal_repair_request_count"] == 0


def test_domain_weaver_operator_action_materializes_candidate_promotion_review(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_codex_carrier_steward(tmp_path)

    result = execute_domain_weaver_action(
        tmp_path,
        {"action": "materialize_promotion_review", "confirmation": CONFIRMATION},
    )

    assert result["ok"] is True
    assert result["action"] == "materialize_promotion_review"
    assert result["summary"]["candidate_domain_count"] >= 1
    assert result["summary"]["active_registry_write_count"] == 0
    assert result["summary"]["accepted_state_count"] == 0
    assert result["results"]["promotion_review"]["active_registry_write_count"] == 0
    assert result["results"]["promotion_review"]["accepted_state_authority"] is False
    assert result["results"]["promotion_gate"]["active_registry_write_count"] == 0
    assert result["results"]["promotion_gate"]["accepted_state_authority"] is False
    assert (tmp_path / DOMAIN_WEAVER_PROMOTION_REVIEW_PATH).is_file()
    assert (tmp_path / DOMAIN_WEAVER_PROMOTION_GATE_PATH).is_file()
    assert all(not str(path).startswith("ION/03_registry/domains/") for path in result["evidence_paths"])


def test_domain_weaver_operator_action_binds_final_fanin_latest_pointer_self_lineage(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_codex_carrier_steward(tmp_path)
    _write(
        tmp_path,
        DOMAIN_WEAVER_EXACT_REISSUE_REQUEST_DISPATCH_FANIN_PATH.as_posix(),
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.exact_reissue_request_dispatch_fanin.v0_1_candidate",
                "status": "candidate_current_sha_fields_reconciled_not_self_lineaged",
                "verdict": "READY_FOR_LIMITED_SWARM_WATCH_AND_FANOUT",
                "ready_for_limited_exact_path_swarm": True,
                "ready_for_broader_swarm": False,
                "ready_for_production": False,
                "receipt_integrity_readback": {
                    "strict_self_lineage_bound": False,
                    "advance_to_limited_swarm_allowed_by_this_readback": False,
                    "readback_blockers": [
                        "final_fanin_latest_not_latest_pointer_self_lineaged",
                        "stale_lifecycle_preview_metadata_hygiene_required",
                    ],
                },
                "accepted_state_claimed": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )

    result = execute_domain_weaver_action(
        tmp_path,
        {
            "action": "bind_final_fanin_latest_pointer_self_lineage",
            "confirmation": CONFIRMATION,
            "packet_id": "test_packet",
        },
    )

    assert result["ok"] is True
    assert result["action"] == "bind_final_fanin_latest_pointer_self_lineage"
    assert result["summary"]["strict_self_lineage_gate_clean"] is True
    assert result["summary"]["readiness_advanced_to_limited_watch"] is False
    assert result["summary"]["ready_for_production"] is False
    assert result["summary"]["sidecar_receipt_path"] in result["evidence_paths"]
    latest_payload = json.loads(
        (tmp_path / DOMAIN_WEAVER_EXACT_REISSUE_REQUEST_DISPATCH_FANIN_PATH).read_text(
            encoding="utf-8"
        )
    )
    integrity = latest_payload["receipt_integrity_readback"]
    assert integrity["strict_self_lineage_bound"] is True
    assert "final_fanin_latest_not_latest_pointer_self_lineaged" not in integrity["readback_blockers"]
    assert "stale_lifecycle_preview_metadata_hygiene_required" in integrity["readback_blockers"]
    assert latest_payload["ready_for_limited_exact_path_swarm"] is False
    assert result["operator_action_record_path"] in result["evidence_paths"]


def test_domain_weaver_operator_action_history_projects_latest_records(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_clean_codex_queue(tmp_path)
    _seed_codex_carrier_steward(tmp_path)

    first = execute_domain_weaver_action(
        tmp_path,
        {"action": "refresh_queue_governor", "confirmation": CONFIRMATION},
    )
    second = execute_domain_weaver_action(
        tmp_path,
        {"action": "materialize_promotion_review", "confirmation": CONFIRMATION},
    )

    assert first["ok"] is True
    assert second["ok"] is True
    history_path = tmp_path / DOMAIN_WEAVER_OPERATOR_ACTION_HISTORY_PATH
    assert history_path.is_file()
    history = json.loads(history_path.read_text(encoding="utf-8"))
    assert history["schema_id"] == "ion.domain_weaver.operator_action_history.v0_1"
    assert history["summary"]["record_count"] == 2
    assert history["summary"]["refresh_queue_governor_count"] == 1
    assert history["summary"]["materialize_promotion_review_count"] == 1
    assert history["summary"]["latest_action"] == "materialize_promotion_review"
    assert history["authority"]["accepted_state_authority"] is False
    assert all((tmp_path / record["record_path"]).is_file() for record in history["records"])

    projection = build_domain_weaver_projection(tmp_path)
    projected_history = projection["operator_action_history"]
    assert projected_history["summary"]["record_count"] == 2
    assert projection["summary"]["operator_action_record_count"] == 2
    assert projection["summary"]["operator_action_latest_action"] == "materialize_promotion_review"
    assert projection["summary"]["operator_action_latest_ok"] is True


def test_portable_agent_domain_package_exports_drop_in_codex_root(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)

    model = build_agent_control_plane_projection(tmp_path)
    agent = next(agent for agent in model["agents"] if agent["role_id"] == "role.codex_carrier_steward")
    domain = next(domain for domain in model["domains"] if domain["domain_id"] == "domain.codex_carrier_sync")

    package = export_portable_agent_domain_package(tmp_path, agent, domain)
    drop_in = tmp_path / package["drop_in_path"]

    assert package["schema_id"] == "ion.portable_agent_domain_package.v0_1"
    assert package["drop_in_ready"] is True
    assert package["domain_weaver_promotion_review_path"] == DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()
    assert (drop_in / "AGENTS.md").is_file()
    assert (drop_in / "BOOTSTRAP.md").read_text(encoding="utf-8").count("codex -C")
    assert (drop_in / ".codex/config.toml").is_file()
    assert (drop_in / ".ion/ION_CONTEXT_CAPSULE.yaml").is_file()
    assert (drop_in / ".ion/ACTIVE_CONTEXT_PACKAGE.md").is_file()
    assert (drop_in / ".ion/COMMUNICATIONS.json").is_file()
    assert (drop_in / ".ion/ADDRESS_BOOK.json").is_file()
    assert (drop_in / ".ion/AGENT.yaml").is_file()
    assert (drop_in / ".ion/DOMAIN.yaml").is_file()
    assert (drop_in / ".ion/RELATIONSHIPS.yaml").is_file()
    assert (drop_in / ".ion/source_refs/SOURCE_REF_MANIFEST.json").is_file()
    source_manifest = json.loads((drop_in / ".ion/source_refs/SOURCE_REF_MANIFEST.json").read_text(encoding="utf-8"))
    assert source_manifest["copied_ref_count"] >= 1
    assert source_manifest["directory_snapshot_policy"] == "disabled_by_default"
    assert any(
        record["kind"] == "directory" and record["copied"] is False and record["skipped_reason"] == "directory_snapshot_disabled_manifest_only"
        for record in source_manifest["records"]
    )
    assert (drop_in / ".ion/source_refs/ION/05_context/current/agent_context_systems/CODEX_CARRIER_STEWARD.context_system.md").is_file()

    zip_path = tmp_path / package["zip_path"]
    assert zip_path.is_file()
    stable_latest = tmp_path / "ION/05_context/current/portable_agent_domain_packages/role_codex_carrier_steward__domain_codex_carrier_sync/LATEST.json"
    assert stable_latest.is_file()
    assert json.loads(stable_latest.read_text(encoding="utf-8"))["zip_path"] == package["zip_path"]
    assert len(package["zip_sha256"]) == 64
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
    assert "AGENTS.md" in names
    assert ".codex/config.toml" in names
    assert ".ion/ION_CONTEXT_CAPSULE.yaml" in names
    assert ".ion/COMMUNICATIONS.json" in names
    assert ".ion/ADDRESS_BOOK.json" in names
    assert ".ion/source_refs/SOURCE_REF_MANIFEST.json" in names
    package_manifest = json.loads((drop_in / "ION_PORTABLE_AGENT_PACKAGE.json").read_text(encoding="utf-8"))
    assert DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix() in package_manifest["read_first"]
    assert ".ion/ADDRESS_BOOK.json" in package_manifest["read_first"]

    refreshed = build_agent_control_plane_projection(tmp_path)
    refreshed_agent = next(agent for agent in refreshed["agents"] if agent["role_id"] == "role.codex_carrier_steward")
    evidence = refreshed_agent["agent_page_evidence"]
    assert evidence["identity"]["agent_kind"] == "ion_capsule_portable_codex_agent"
    assert evidence["portable_package"]["drop_in_ready"] is True
    assert evidence["portable_package"]["zip_sha256"] == package["zip_sha256"]
    assert any(item["label"] == "source_ref_manifest" and item["exists"] for item in evidence["portable_package"]["path_probes"])


def test_context_starter_capsule_materializes_clean_operator_folder(tmp_path: Path):
    _seed_root(tmp_path)

    starter = materialize_context_starter_capsule(tmp_path)

    assert starter["schema_id"] == "ion.context_starter_capsule.v1"
    assert starter["ready"] is True
    final = tmp_path / starter["operator_final_path"]
    assert (final / "AGENTS.md").is_file()
    assert (final / ".codex/config.toml").is_file()
    assert (final / ".ion/ION_CONTEXT_CAPSULE.yaml").is_file()
    assert (final / ".ion/ACTIVE_CONTEXT_PACKAGE.md").is_file()
    assert (final / ".ion/ROUTE.json").is_file()
    assert (final / ".ion/LONG_HORIZON.json").is_file()
    assert (final / ".ion/MINI.md").is_file()
    assert (final / ".ion/CAPSULE.md").is_file()
    assert not (final / ".ion/AGENT.yaml").exists()
    assert not (final / ".ion/DOMAIN.yaml").exists()
    assert not (final / ".ion/RELATIONSHIPS.yaml").exists()
    assert not (final / ".ion/source_refs").exists()
    assert "not a multi-agent runtime" in (final / "README.md").read_text(encoding="utf-8")
    assert "Do not create invented agents" in (final / "AGENTS.md").read_text(encoding="utf-8")
    capsule_text = (final / ".ion/ION_CONTEXT_CAPSULE.yaml").read_text(encoding="utf-8")
    assert "multi_agent_runtime: false" in capsule_text
    assert "live_agent_dispatch_proven: false" in capsule_text
    forbidden = ("STEWARD", "MASON", "NEMESIS", "IONOLOGIST", "CONTEXT_CARTOGRAPHER", "RELAY")
    for path in final.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            assert not any(term in text for term in forbidden), path

    model = build_agent_control_plane_projection(tmp_path)
    assert model["starter_capsule"]["ready"] is True
    assert model["starter_capsule"]["source_snapshot_policy"] == "disabled_by_default"
    assert model["starter_capsule"]["runtime_policy"] == "single_session_context_only_registry_backed_context"


def test_context_starter_capsule_create_new_folder(tmp_path: Path):
    _seed_root(tmp_path)

    target = tmp_path / "new_context"
    result = create_context_starter_capsule(target, tmp_path)

    assert result["ok"] is True
    assert result["launch_command"] == f"codex -C {target.resolve()}"
    assert (target / "AGENTS.md").is_file()
    assert (target / ".ion/ION_CONTEXT_CAPSULE.yaml").is_file()
    assert (target / ".ion/STATUS.json").is_file()
    assert not (target / ".ion/AGENT.yaml").exists()
    assert sorted(path.name for path in (target / ".ion/inbox").iterdir()) == [".gitkeep"]
    blocked = create_context_starter_capsule(target, tmp_path)
    assert blocked["ok"] is False
    assert blocked["finding"] == "target_not_empty"
    (target / ".ion/outbox/fake_role_message.md").write_text("fake", encoding="utf-8")
    (target / ".ion/AGENT.yaml").write_text("legacy", encoding="utf-8")
    forced = create_context_starter_capsule(target, tmp_path, force=True)
    assert forced["ok"] is True
    assert not (target / ".ion/AGENT.yaml").exists()
    assert sorted(path.name for path in (target / ".ion/outbox").iterdir()) == [".gitkeep"]


def test_automation_control_plane_runs_bounded_capsule_actions(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_codex_carrier_steward(tmp_path)

    model = build_automation_control_plane(tmp_path)

    assert model["schema_id"] == "ion.automation_control_plane.v0_1"
    assert model["summary"]["action_count"] >= 4
    assert model["summary"]["available_agent_comms_count"] >= 1
    assert model["agent_comms"]["automation_comms_policy"]["limits"]["default_window_minutes"] == 60
    assert any(action["action_id"] == "starter_capsule.materialize" for action in model["actions"])
    assert any(action["action_id"] == "agent_comms.directory_materialize" for action in model["actions"])
    assert any(action["action_id"] == "agent_comms.process_directives" for action in model["actions"])
    assert any(action["action_id"] == "domain_weaver.materialize_projection" for action in model["actions"])
    assert any(action["action_id"] == "domain_weaver.materialize_promotion_review" for action in model["actions"])
    assert any(action["action_id"] == "domain_weaver.materialize_promotion_gate" for action in model["actions"])
    assert any(action["action_id"] == "domain_weaver.materialize_dogfood_context_capsule" for action in model["actions"])
    assert any(action["action_id"] == "domain_weaver.materialize_steward_ready_review" for action in model["actions"])
    assert model["summary"]["agent_comms_directive_pickup"] is True
    assert model["summary"]["domain_weaver_projection_exists"] is False
    assert model["summary"]["domain_weaver_dogfood_capsule_exists"] is False
    assert model["summary"]["domain_weaver_steward_ready_review_exists"] is False
    assert model["summary"]["directive_processed_count"] == 0
    assert model["agent_comms_directive_pickup"]["schema_id"] == "ion.agent_comms.directive_pickup.projection.v1"
    assert model["agent_comms_directive_pickup"]["action_id"] == "agent_comms.process_directives"
    assert model["agent_comms_directive_pickup"]["directive_schema_id"] == "ion.agent_comms.directive.v1"
    assert model["agent_comms_directive_pickup"]["directive_fence"] == "ion-agent-comms"

    pickup = execute_automation_action(
        tmp_path,
        {"action_id": "agent_comms.process_directives", "text": "no directive in this message"},
    )
    assert pickup["ok"] is True
    assert pickup["result"]["processed_directive_count"] == 0
    assert (tmp_path / pickup["receipt_path"]).is_file()

    blocked = execute_automation_action(tmp_path, {"action_id": "starter_capsule.materialize"})
    assert blocked["ok"] is False
    assert blocked["finding"] == "confirmation_required"

    starter = execute_automation_action(
        tmp_path,
        {"action_id": "starter_capsule.materialize", "confirmation": CONFIRMATION},
    )
    assert starter["ok"] is True
    assert (tmp_path / "ION/05_context/current/context_starter_capsule/OPERATOR_FINAL/.ion/ION_CONTEXT_CAPSULE.yaml").is_file()
    assert (tmp_path / starter["receipt_path"]).is_file()

    packages = execute_automation_action(
        tmp_path,
        {"action_id": "portable_packages.regenerate_lean", "confirmation": CONFIRMATION},
    )
    assert packages["ok"] is True
    assert packages["result"]["communication_directory"]["available_agent_count"] >= 1
    assert packages["result"]["regenerated_package_count"] >= 1
    latest = tmp_path / "ION/05_context/current/portable_agent_domain_packages/role_codex_carrier_steward__domain_codex_carrier_sync/LATEST.json"
    assert latest.is_file()
    package = json.loads(latest.read_text(encoding="utf-8"))
    manifest = json.loads((tmp_path / package["drop_in_path"] / ".ion/source_refs/SOURCE_REF_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["directory_snapshot_policy"] == "disabled_by_default"

    weave = execute_automation_action(
        tmp_path,
        {"action_id": "domain_weaver.materialize_projection", "confirmation": CONFIRMATION},
    )
    assert weave["ok"] is True
    assert weave["result"]["projection_path"] == DOMAIN_WEAVER_PROJECTION_PATH.as_posix()
    assert (tmp_path / DOMAIN_WEAVER_PROJECTION_PATH).is_file()

    promotion = execute_automation_action(
        tmp_path,
        {"action_id": "domain_weaver.materialize_promotion_review", "confirmation": CONFIRMATION},
    )
    assert promotion["ok"] is True
    assert promotion["result"]["review_path"] == DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix()
    assert promotion["result"]["active_registry_write_count"] == 0

    gate = execute_automation_action(
        tmp_path,
        {"action_id": "domain_weaver.materialize_promotion_gate", "confirmation": CONFIRMATION},
    )
    assert gate["ok"] is True
    assert gate["result"]["gate_path"] == DOMAIN_WEAVER_PROMOTION_GATE_PATH.as_posix()
    assert gate["result"]["active_registry_write_count"] == 0
    assert gate["result"]["accepted_state_count"] == 0

    dogfood = execute_automation_action(
        tmp_path,
        {"action_id": "domain_weaver.materialize_dogfood_context_capsule", "confirmation": CONFIRMATION},
    )
    assert dogfood["ok"] is True
    assert dogfood["result"]["capsule_path"] == DOMAIN_WEAVER_DOGFOOD_CONTEXT_CAPSULE_PATH.as_posix()
    assert dogfood["result"]["accepted_state_authority"] is False
    assert (tmp_path / DOMAIN_WEAVER_DOGFOOD_CONTEXT_CAPSULE_PATH).is_file()

    steward_review = execute_automation_action(
        tmp_path,
        {"action_id": "domain_weaver.materialize_steward_ready_review", "confirmation": CONFIRMATION},
    )
    assert steward_review["ok"] is True
    assert steward_review["result"]["review_path"] == DOMAIN_WEAVER_STEWARD_READY_REVIEW_PATH.as_posix()
    assert steward_review["result"]["accepted_state_authority"] is False
    assert (tmp_path / DOMAIN_WEAVER_STEWARD_READY_REVIEW_PATH).is_file()


def test_automation_control_plane_processes_agent_comms_directive_with_cockpit_evidence(tmp_path: Path):
    _seed_root(tmp_path)
    _seed_ionologist(tmp_path)
    directive_body = """Need IONOLOGIST backend review.

```ion-agent-comms
{
  "schema_id": "ion.agent_comms.directive.v1",
  "from_role": "role.codex_carrier_steward",
  "agent": "role.ionologist",
  "template_id": "agent_workpack_decision",
  "dispatch_mode": "queue_workpack",
  "objective": "Review the durable comms directive pickup evidence fields.",
  "body": "Return a bounded decision with proof sections."
}
```
"""

    action = execute_automation_action(
        tmp_path,
        {
            "action_id": "agent_comms.process_directives",
            "text": directive_body,
            "source_ref": "agent_chat://control-plane/1",
            "source_message_id": "msg_agent_control_1",
            "from_role": "role.codex_carrier_steward",
        },
    )

    assert action["ok"] is True
    assert action["production_authority"] is False
    assert action["live_execution_authority"] is False
    assert action["accepted_state_authority"] is False
    assert action["result"]["processed_directive_count"] == 1
    record = action["result"]["results"][0]["ledger_record"]
    assert record["source_message_id"] == "msg_agent_control_1"
    assert record["spawned_comms_message_id"].startswith("msg_")
    assert record["target_agent"] == "role.ionologist"
    assert record["dispatch_mode"] == "queue_workpack"
    assert record["workpack_path"].startswith("ION/05_context/current/chatgpt_connector/codex_work_requests/")
    assert record["workpack_status"] == "QUEUED_FOR_CODEX_CARRIER"
    assert record["live_external_agent_execution_proven"] is False
    assert record["production_authority"] is False
    assert record["live_execution_authority"] is False
    assert record["accepted_state_authority"] is False

    model = build_automation_control_plane(tmp_path)
    pickup = model["agent_comms_directive_pickup"]
    assert pickup["processed_count"] == 1
    assert "source_message_id" in pickup["evidence_fields"]
    assert "spawned_comms_message_id" in pickup["evidence_fields"]
    assert "target_agent" in pickup["evidence_fields"]
    projected = pickup["recent_processed"][0]
    assert projected["source_message_id"] == "msg_agent_control_1"
    assert projected["spawned_comms_message_id"] == record["spawned_comms_message_id"]
    assert projected["target_agent"] == "role.ionologist"
    assert projected["dispatch_mode"] == "queue_workpack"
    assert projected["workpack_path"] == record["workpack_path"]
    assert projected["production_authority"] is False
    assert projected["live_execution_authority"] is False
    assert projected["accepted_state_authority"] is False
