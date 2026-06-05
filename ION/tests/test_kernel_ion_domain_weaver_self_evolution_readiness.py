from __future__ import annotations

import json
from pathlib import Path

from kernel.ion_domain_weaver_self_evolution_readiness import (
    CONTEXT_DELTA_SCHEMA_ID,
    SCHEMA_ID,
    build_self_evolution_readiness,
    write_self_evolution_readiness,
)


def _active_root(tmp_path: Path) -> Path:
    root = tmp_path / "active"
    (root / "ION").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = 'ion-test'\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").write_text("authority\n", encoding="utf-8")
    return root


def _write_json(root: Path, rel: str, payload: dict) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seed_current_evidence(root: Path) -> None:
    _write_text(
        root,
        "ION/05_context/current/domain_weaver/.ion/ION_CONTEXT_CAPSULE.yaml",
        "\n".join(
            [
                "schema_id: ion.folder_local_context_capsule.v0_1",
                "context_id: domain_weaver_current_context",
                f"active_root: {root}",
                "context_root: ION/05_context/current/domain_weaver",
                "focus: domain_weaver_larger_fanout_control_plane_v0_1",
                "shared_codex_solo_is_working_capsule: false",
                "last_refreshed_at: 2026-06-04T04:27:51+00:00",
                "materialization_ready: false",
                "current_blocker: codex_carrier_transient_usage_limit_bug_blocks_valid_task_return",
            ]
        )
        + "\n",
    )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json",
        {
            "schema_id": "ion.domain_weaver.projection.v1",
            "generated_at": "2026-06-03T03:56:11+00:00",
            "summary": {
                "full_domain_weaver_ready": False,
                "self_evolution_ready": False,
                "self_evolution_lattice_executable": False,
                "exact_active_specialist_binding_count": 0,
                "queue_request_count": 569,
                "queue_stale_waiting_request_count": 0,
                "live_return_complete": True,
                "ui_operator_usable": False,
            },
        },
    )
    _write_json(root, "ION/05_context/current/domain_weaver/PROMOTION_REVIEW.json", {"promotion_status": "promotion_review_ready"})
    _write_json(root, "ION/05_context/current/domain_weaver/PROMOTION_GATE.json", {"gate_status": "promotion_gate_clean"})
    _write_text(root, "ION/05_context/current/domain_weaver/LEGACY_PROMOTION_DOC_STALENESS_SEAL_20260604.md", "sealed\n")
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/ready_review/STEWARD_READY_REVIEW.json",
        {"schema_id": "ion.domain_weaver.steward_ready_review.v1", "created_at": "2026-06-03T03:56:11+00:00"},
    )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/larger_fanout/DOMAIN_WEAVER_LARGER_FANOUT_CONTROL_READINESS.latest.json",
        {
            "schema_id": "ion.domain_weaver.larger_fanout_control_readiness.v0_1",
            "generated_at": "2026-06-04T04:28:25Z",
            "readiness_ok": True,
            "max_candidate_lane_count": 3,
            "recursive_native_spawn_allowed": False,
        },
    )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/live_carrier_binding/ACTIVE_INVOKABLE_BINDING_PROOF_ROWS.candidate.json",
        {
            "schema_id": "ion.domain_weaver.active_invocable_binding_proof_rows.v0_1_candidate_update",
            "summary": {
                "aggregate_result": "candidate_exact_active_binding_complete_pending_final_settlement",
                "required_specialist_binding_count": 6,
                "exact_active_binding_count": 6,
                "exact_active_binding_proved_count": 6,
                "missing_exact_active_binding_count": 0,
                "delegated_active_binding_count": 0,
                "candidate_boot_only_count": 0,
                "materialization_ready": False,
            },
        },
    )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/monolith_index/DOMAIN_WEAVER_MONOLITH_INDEX.latest.json",
        {
            "schema_id": "ion.domain_weaver.monolith_index.v0_1",
            "summary": {"dispatcher_branch_action_count": 105},
        },
    )
    _write_json(
        root,
        "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json",
        {
            "request_count": 2,
            "requests": [
                {
                    "request_id": "codex_req_domain_weaver_ready",
                    "status": "QUEUED_FOR_CODEX_CARRIER",
                    "work_class": "domain_weaver_spawn_dispatch",
                },
                {"request_id": "codex_req_done", "status": "RETURN_RECORDED_PROOF_ACCEPTED"},
            ],
        },
    )
    _write_json(root, "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json", {"active_run": None})
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/operator_actions/20260604T042751Z_domain_weaver_larger_fanout_control_plane_patch_validated.json",
        {
            "schema_id": "ion.domain_weaver.operator_action_receipt.v0_1",
            "validation": [
                {"command": "pytest focused", "result": "passed", "output": "19 passed"},
                {"command": "pytest broad", "result": "failed", "output": "17 failed, 72 passed"},
            ],
        },
    )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/operator_actions/20260604T040700Z_domain_weaver_native_subagent_transcript_bridge_live_dogfood_settlement.json",
        {
            "schema_id": "ion.domain_weaver.operator_action_receipt.v0_1",
            "proof_projection": {
                "proof_ok": True,
                "proof_state": "alternate_worker_return_recovery_chain_proven",
                "automatic_agent_reaction_proven": False,
            },
            "live_dogfood": {
                "accepted_for_carrier_intake": True,
                "native_subagent_transcript_verified": True,
                "product_state_accepted": False,
            },
        },
    )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/operator_actions/20260604T041925Z_domain_weaver_recursive_native_spawn_probe_no_child_available.json",
        {"child_spawn_available": False, "child_spawn_count": 0},
    )
    _write_text(root, "ION/05_context/current/codex_agent_mounts/role_steward__domain_current_phase_orchestration_management/ACTIVE_CONTEXT_PACKAGE.md", "fresh\n")
    _write_json(root, "ION/05_context/current/codex_agent_mounts/role_atlas__ion_vnext_front_door/ION_AGENT_MOUNT_MANIFEST.json", {"domain_id": "ion_vnext_front_door"})


def test_self_evolution_readiness_blocks_serious_autonomy_but_allows_candidate_wave(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)

    readiness = build_self_evolution_readiness(root, generated_at="2026-06-04T05:00:00Z")

    assert readiness["schema_id"] == SCHEMA_ID
    assert readiness["root_proof"]["proof_ok"] is True
    assert readiness["verdict"].startswith("NOT_READY_BLOCKED_BY_")
    assert readiness["supervised_candidate_wave_allowed"] is True
    blocker_codes = {row["code"] for row in readiness["blockers_ranked"]}
    assert "AUTOMATIC_ORIGINAL_AGENT_REACTION_NOT_PROVEN" in blocker_codes
    assert "DOMAIN_WEAVER_PROJECTION_STALE" in blocker_codes
    assert "BROAD_CONNECTOR_FANOUT_VALIDATION_FAILED" in blocker_codes
    assert "MANIFEST_ONLY_MOUNTS_NOT_WORKING_CAPSULES" in blocker_codes
    assert "SEMANTIC_BRANCH_ID_DRIFT" in blocker_codes
    assert readiness["candidate_context_graph_deltas"]["schema_id"] == CONTEXT_DELTA_SCHEMA_ID
    claim_ids = {row["id"] for row in readiness["candidate_context_graph_deltas"]["upsert_claims"]}
    assert "domain_weaver.semantic_branch_identity.vnext_front_door" in claim_ids
    assert readiness["validations"]["failed_or_broader_risk"][0]["result"] == "failed"


def test_write_self_evolution_readiness_artifacts_and_receipt(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)

    result = write_self_evolution_readiness(root, generated_at="2026-06-04T05:00:00Z")

    json_path = root / result["json_path"]
    report_path = root / result["report_path"]
    delta_path = root / result["context_graph_delta_path"]
    receipt_path = root / result["operator_receipt_path"]
    assert json_path.exists()
    assert report_path.exists()
    assert delta_path.exists()
    assert receipt_path.exists()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    delta = json.loads(delta_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert payload["verdict"].startswith("NOT_READY_BLOCKED_BY_")
    assert delta["write_performed"] is False
    assert receipt["result"] == "candidate_readiness_report_written"
    assert "Domain Weaver Self-Evolution Readiness Report" in report_path.read_text(encoding="utf-8")
