from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
import time
from pathlib import Path

from kernel.ion_domain_weaver_projection_refresh_candidate import (
    ACCEPTED_REFRESH_APPLY_SCHEMA_ID,
    ACCEPTED_REFRESH_PLAN_SCHEMA_ID,
    ACCEPTED_STATE_WRITE_CONFIRMATION,
    APPLY_GATE_REBASELINE_DRYRUN_SCHEMA_ID,
    APPLY_GATE_REBASELINE_DRYRUN_WRITE_RESULT_SCHEMA_ID,
    BOUNDED_WRITE_CONFIRMATION,
    CONTEXT_DELTA_SCHEMA_ID,
    REPLACEMENT_BODY_CANDIDATE_SCHEMA_ID,
    SCHEMA_ID,
    apply_projection_accepted_refresh,
    build_projection_apply_gate_rebaseline_dryrun,
    build_projection_accepted_refresh_plan,
    build_projection_refresh_candidate,
    build_projection_replacement_body_candidate,
    json_write_text,
    write_projection_apply_gate_rebaseline_dryrun,
    write_projection_refresh_candidate,
)
from kernel.ion_domain_weaver_semantic_ids import VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID


def _write_json(root: Path, rel_path: str, payload: dict) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(root: Path, rel_path: str, text: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seed_codex_solo(root: Path) -> None:
    codex_solo = root / "ION/05_context/current/codex_solo"
    codex_solo.mkdir(parents=True, exist_ok=True)
    for name in ("CAPSULE.md", "MINI.md", "HOT_CONTEXT.md"):
        (codex_solo / name).write_text(f"# {name}\n", encoding="utf-8")
    _write_json(root, "ION/05_context/current/codex_solo/LONG_HORIZON.json", {"ok": True})
    _write_json(root, "ION/05_context/current/codex_solo/ROUTE.json", {"ok": True})
    _write_json(root, "ION/05_context/current/codex_solo/STATUS.json", {"ok": True})
    _write_json(
        root,
        "ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json",
        {
            "schema_id": "ion.codex_solo_context_packages.v1",
            "generated_at": "2099-01-01T00:00:00+00:00",
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
    )


def _seed_route_registry(root: Path) -> None:
    _write_text(
        root,
        "ION/03_registry/ion_action_mcp_branch_leader_registry.yaml",
        "\n".join(
            [
                "branches:",
                "  - branch_id: domain_weaver_agents",
                "    family: domain_weaver_agents",
                "    routes:",
                "      - route_id: comms_send",
                "        title: Comms Send",
                "        mutates_state: true",
                "        confirmation_required: true",
                "        idempotency_required: true",
                "        agent_id_required: true",
                "        write_intent_lease_required: true",
                "        args_schema:",
                "          required:",
                "            - confirmation",
                "            - idempotency_key",
                "            - agent_id",
                "            - write_intent_lease_id",
            ]
        )
        + "\n",
    )


def _seed_mount(root: Path) -> None:
    mount = root / "ION/05_context/current/codex_agent_mounts/role_context_cartographer__domain_context_active_resolver"
    ion_dir = mount / ".ion"
    ion_dir.mkdir(parents=True)
    _write_json(root, "ION/05_context/current/codex_agent_mounts/role_context_cartographer__domain_context_active_resolver/ION_AGENT_MOUNT_MANIFEST.json", {"role_id": "role.context_cartographer", "domain_id": "domain.context_active_resolver"})
    for name in (
        "ION_CONTEXT_CAPSULE.yaml",
        "AGENT.yaml",
        "DOMAIN.yaml",
        "RELATIONSHIPS.yaml",
        "COMMUNICATIONS.json",
        "ADDRESS_BOOK.json",
    ):
        (ion_dir / name).write_text(f"{name}\n", encoding="utf-8")
    (ion_dir / "ACTIVE_CONTEXT_PACKAGE.md").write_text("stale\n", encoding="utf-8")
    (ion_dir / "ACTIVE_CONTEXT_PACKAGE.json").write_text('{"lane_id":"stale"}\n', encoding="utf-8")
    stale = time.time() - 200_000
    os.utime(ion_dir / "ACTIVE_CONTEXT_PACKAGE.md", (stale, stale))
    os.utime(ion_dir / "ACTIVE_CONTEXT_PACKAGE.json", (stale, stale))


def _seed_manifest_only_alias_mount(root: Path) -> None:
    _write_json(
        root,
        "ION/05_context/current/codex_agent_mounts/role_atlas__ion_vnext_front_door/ION_AGENT_MOUNT_MANIFEST.json",
        {"domain_id": "ion_vnext_front_door"},
    )


def _seed_projection_inputs(root: Path) -> None:
    (root / "ION").mkdir(parents=True, exist_ok=True)
    _write_text(root, "pyproject.toml", "[project]\nname = 'ion-test'\n")
    _write_text(root, "ION/REPO_AUTHORITY.md", "authority\n")
    _seed_codex_solo(root)
    _seed_route_registry(root)
    _seed_mount(root)
    _seed_manifest_only_alias_mount(root)
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json",
        {
            "schema_id": "ion.domain_weaver.projection.v1",
            "generated_at": "2026-06-03T03:56:11+00:00",
            "weave_status": "candidate_coverage_ready",
            "summary": {
                "self_evolution_ready": False,
                "self_evolution_lattice_executable": False,
            },
        },
    )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/live_carrier_binding/ACTIVE_INVOKABLE_BINDING_PROOF_ROWS.candidate.json",
        {
            "summary": {
                "required_specialist_binding_count": 6,
                "exact_active_binding_proved_count": 6,
                "missing_exact_active_binding_count": 0,
                "materialization_ready": False,
            }
        },
    )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/operator_actions/20260604T054146Z_domain_weaver_comms_mutation_actor_write_intent_gates_validated.json",
        {"result": "validated"},
    )


def _seed_projection_apply_lease(
    root: Path,
    *,
    agent_id: str,
    lease_id: str,
    target_paths: list[str],
    lease_type: str = "exclusive_write",
) -> None:
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    board_path = root / "ION/05_context/current/worker_shift/ACTIVE_WORKER_SHIFT_BOARD.json"
    board_path.parent.mkdir(parents=True, exist_ok=True)
    board_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.worker_shift_board.v0_1",
                "updated_at": timestamp,
                "authority": {
                    "accepted_state_authority": False,
                    "production_authority": False,
                    "live_execution_authority": False,
                    "secrets_authority": False,
                },
                "active_shifts": [],
                "active_leases": [
                    {
                        "lease_id": lease_id,
                        "agent_id": agent_id,
                        "worker_id": agent_id,
                        "declared_true_name": agent_id,
                        "identity_binding_status": "BOUND_TRUE_NAME",
                        "worker_id_source": "declared_true_name",
                        "unbound_worker_id": False,
                        "mode": lease_type,
                        "lease_type": lease_type,
                        "lease_class": "projection_accepted_refresh_apply_lease",
                        "root_scope": "active_root",
                        "active_root": str(root),
                        "paths": target_paths,
                        "raw_paths": target_paths,
                        "resolved_paths": [
                            (root / target_path).resolve(strict=False).as_posix()
                            for target_path in target_paths
                        ],
                        "claimed_at": timestamp,
                        "last_heartbeat_at": timestamp,
                        "updated_at": timestamp,
                        "status": "ACTIVE",
                    }
                ],
                "stale_workers": [],
                "recent_signoffs": [],
                "recent_receipts": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def test_projection_refresh_candidate_reports_stale_projection_and_mount_blockers(tmp_path: Path) -> None:
    _seed_projection_inputs(tmp_path)

    payload = build_projection_refresh_candidate(
        tmp_path,
        generated_at="2026-06-04T05:45:19Z",
        max_context_age_seconds=60,
    )

    assert payload["schema_id"] == SCHEMA_ID
    assert payload["source_projection"]["stale_against_latest_receipts"] is True
    assert payload["mount_census"]["manifest_count"] == 2
    assert payload["mount_census"]["active_context_package_count"] == 1
    assert payload["mount_census"]["manifest_only_mount_count"] == 1
    alias_mount = payload["mount_census"]["semantic_alias_mounts"][0]
    assert alias_mount["raw_domain_id"] == ""
    assert alias_mount["manifest_domain_id"] == "ion_vnext_front_door"
    assert alias_mount["canonical_domain_id"] == VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID
    assert alias_mount["domain_alias_detected"] is True
    assert payload["active_context_reissue_preflight"]["target_mount_count"] == 2
    assert payload["active_context_reissue_preflight"]["mount_package_refs_requiring_reissue_count"] >= 2
    assert payload["route_gate_matrix"]["domain_weaver_gapped_mutating_route_count"] == 0
    blocker_codes = {row["code"] for row in payload["blockers"]}
    assert "DOMAIN_WEAVER_PROJECTION_STALE" in blocker_codes
    assert "ACTIVE_CONTEXT_REISSUE_REQUIRED" in blocker_codes
    assert "MANIFEST_ONLY_MOUNTS_NOT_WORKING_CAPSULES" in blocker_codes
    assert "HANDLER_WRITE_SET_PARITY_NOT_PROVEN" in blocker_codes
    deltas = payload["candidate_context_graph_deltas"]
    assert deltas["schema_id"] == CONTEXT_DELTA_SCHEMA_ID
    claim_ids = {row["id"] for row in deltas["upsert_claims"]}
    assert "domain_weaver.route_gate_matrix.domain_weaver_declared_gates" in claim_ids
    assert "domain_weaver.active_context_mounts.current_census" in claim_ids
    semantic_claim = [
        row for row in deltas["upsert_claims"]
        if row["id"] == "domain_weaver.semantic_branch_identity.vnext_front_door"
    ][0]
    assert semantic_claim["value"]["canonical"] == VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID


def test_write_projection_refresh_candidate_artifacts_and_receipt(tmp_path: Path) -> None:
    _seed_projection_inputs(tmp_path)

    result = write_projection_refresh_candidate(
        tmp_path,
        generated_at="2026-06-04T05:45:19Z",
        max_context_age_seconds=60,
    )

    json_path = tmp_path / result["json_path"]
    report_path = tmp_path / result["report_path"]
    delta_path = tmp_path / result["context_graph_delta_path"]
    preflight_path = tmp_path / result["active_context_reissue_preflight_json_path"]
    receipt_path = tmp_path / result["operator_receipt_path"]
    assert json_path.exists()
    assert report_path.exists()
    assert delta_path.exists()
    assert preflight_path.exists()
    assert receipt_path.exists()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert payload["verdict"] == "PROJECTION_REFRESH_CANDIDATE_WRITTEN_NOT_ACCEPTED_STATE"
    assert receipt["result"] == "candidate_projection_refresh_written_no_accepted_state"
    assert result["projection_overwrite_performed"] is False
    assert "Domain Weaver Projection Refresh Candidate" in report_path.read_text(encoding="utf-8")


def test_projection_replacement_body_candidate_preserves_false_invariants_and_hashes(tmp_path: Path) -> None:
    _seed_projection_inputs(tmp_path)
    source_path = tmp_path / "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    before_text = source_path.read_text(encoding="utf-8")

    candidate = build_projection_replacement_body_candidate(
        tmp_path,
        generated_at="2026-06-04T05:50:00Z",
        max_context_age_seconds=60,
    )

    assert candidate["schema_id"] == REPLACEMENT_BODY_CANDIDATE_SCHEMA_ID
    assert candidate["ok"] is True
    assert candidate["status"] == "projection_replacement_body_candidate_built"
    assert candidate["mutates_active_state"] is False
    assert candidate["projection_overwrite_performed"] is False
    assert candidate["accepted_state_claim"] is False
    assert candidate["apply_ready"] is False
    assert candidate["target"]["path"] == "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    assert candidate["target"]["before_sha256"]
    assert candidate["target"]["candidate_body_sha256"]
    assert candidate["target"]["write_performed"] is False
    assert candidate["invariants"]["ok"] is True
    assert candidate["invariants"]["failures"] == []

    body = candidate["candidate_body"]
    summary = body["summary"]
    authority = body["authority"]
    assert body["generated_at"] == "2026-06-04T05:50:00Z"
    assert body["accepted_state_authority"] is False
    assert body["production_authority"] is False
    assert body["live_execution_authority"] is False
    assert body["secrets_authority"] is False
    assert authority["accepted_state_authority"] is False
    assert authority["production_authority"] is False
    assert authority["live_execution_authority"] is False
    assert authority["secrets_authority"] is False
    assert summary["projection_replacement_body_candidate_ready"] is True
    assert summary["projection_accepted_apply_ready"] is False
    assert summary["projection_accepted_state_write_gate_granted"] is False
    assert summary["worker_start_general_queue_processing_allowed"] is False
    assert summary["semantic_alias_accepted_apply_gate_granted"] is False
    assert summary["serious_self_evolution_ready"] is False
    assert summary["autonomous_self_evolution_ready"] is False
    assert summary["production_ready"] is False
    assert summary["self_evolution_ready"] is False
    assert summary["self_evolution_lattice_executable"] is False
    assert body["accepted_refresh_replacement_candidate"]["write_performed"] is False
    assert body["accepted_refresh_replacement_candidate"]["accepted_state_claim"] is False
    assert source_path.read_text(encoding="utf-8") == before_text


def test_projection_replacement_body_candidate_blocks_when_source_missing(tmp_path: Path) -> None:
    (tmp_path / "ION").mkdir(parents=True, exist_ok=True)
    _write_text(tmp_path, "pyproject.toml", "[project]\nname = 'ion-test'\n")
    _write_text(tmp_path, "ION/REPO_AUTHORITY.md", "authority\n")

    candidate = build_projection_replacement_body_candidate(
        tmp_path,
        generated_at="2026-06-04T05:50:00Z",
        max_context_age_seconds=60,
    )

    assert candidate["schema_id"] == REPLACEMENT_BODY_CANDIDATE_SCHEMA_ID
    assert candidate["ok"] is False
    assert candidate["status"] == "source_projection_missing"
    assert candidate["candidate_body"] is None
    assert candidate["target"]["candidate_body_sha256"] is None
    assert candidate["mutates_active_state"] is False
    assert candidate["accepted_state_claim"] is False
    blocker_codes = {row["code"] for row in candidate["blockers"]}
    assert blocker_codes == {"source_projection_missing"}


def test_projection_accepted_refresh_plan_is_read_only_with_replacement_candidate_hash(tmp_path: Path) -> None:
    _seed_projection_inputs(tmp_path)

    plan = build_projection_accepted_refresh_plan(
        tmp_path,
        generated_at="2026-06-04T05:50:00Z",
        max_context_age_seconds=60,
    )

    assert plan["schema_id"] == ACCEPTED_REFRESH_PLAN_SCHEMA_ID
    assert plan["plan_ok"] is False
    assert plan["apply_ready"] is False
    assert plan["write_performed"] is False
    assert plan["projection_overwrite_performed"] is False
    assert plan["mutates_active_state"] is False
    assert plan["accepted_state_claim"] is False
    assert plan["target"]["path"] == "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    assert plan["target"]["exists"] is True
    assert plan["target"]["before_sha256"]
    assert plan["target"]["after_sha256"]
    assert plan["target"]["after_sha256_status"] == "candidate_replacement_body_available_not_applied"
    assert plan["candidate_evidence"]["sha256"]
    replacement = plan["replacement_body_candidate"]
    assert replacement["schema_id"] == REPLACEMENT_BODY_CANDIDATE_SCHEMA_ID
    assert replacement["ok"] is True
    assert replacement["target"]["candidate_body_sha256"] == plan["target"]["after_sha256"]
    assert replacement["invariants"]["ok"] is True
    assert replacement["body_omitted_from_plan"] is True
    assert plan["required_apply_gate"]["confirmation"] == "ION_BOUNDED_WRITE_CONFIRMED"
    assert plan["required_apply_gate"]["required_lease_targets"] == [
        "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    ]
    blocker_codes = {row["code"] for row in plan["blockers"]}
    assert "accepted_projection_replacement_body_not_built" not in blocker_codes
    assert "accepted_state_write_gate_not_granted" in blocker_codes
    assert "projection_refresh_candidate_has_open_blockers" in blocker_codes


def test_projection_apply_gate_rebaseline_dryrun_detects_stale_previous_plan_without_write(
    tmp_path: Path,
) -> None:
    _seed_projection_inputs(tmp_path)
    target_rel = "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    previous_plan_rel = (
        "ION/05_context/current/domain_weaver/projection_refresh/"
        "DOMAIN_WEAVER_PROJECTION_ACCEPTED_REFRESH_PLAN.latest.json"
    )
    target = tmp_path / target_rel

    previous_plan = build_projection_accepted_refresh_plan(
        tmp_path,
        generated_at="2026-06-04T05:50:00Z",
        max_context_age_seconds=60,
    )
    _write_json(tmp_path, previous_plan_rel, previous_plan)

    projection = json.loads(target.read_text(encoding="utf-8"))
    projection["generated_at"] = "2026-06-04T06:10:00Z"
    projection["summary"]["projection_apply_rebaseline_test_marker"] = "current"
    _write_json(tmp_path, target_rel, projection)
    current_text = target.read_text(encoding="utf-8")
    current_sha = hashlib.sha256(target.read_bytes()).hexdigest()

    dryrun = build_projection_apply_gate_rebaseline_dryrun(
        tmp_path,
        previous_plan_path=previous_plan_rel,
        generated_at="2026-06-04T06:11:00Z",
        max_context_age_seconds=60,
    )

    assert dryrun["schema_id"] == APPLY_GATE_REBASELINE_DRYRUN_SCHEMA_ID
    assert dryrun["ok"] is True
    assert dryrun["apply_ready"] is False
    assert dryrun["write_performed"] is False
    assert dryrun["projection_overwrite_performed"] is False
    assert dryrun["accepted_projection_write_performed"] is False
    assert dryrun["mutates_active_state"] is False
    assert dryrun["accepted_state_claim"] is False
    assert dryrun["target"]["current_before_sha256"] == current_sha
    assert dryrun["target"]["current_plan_target_current"] is True
    assert dryrun["previous_plan"]["before_sha256"] == previous_plan["target"]["before_sha256"]
    assert dryrun["previous_plan"]["stale_against_current_projection_sha"] is True
    assert dryrun["current_plan"]["target"]["before_sha256"] == current_sha
    assert dryrun["replacement_body_candidate"]["target"]["before_sha256"] == current_sha
    assert dryrun["replacement_body_candidate"]["candidate_body_omitted_from_dryrun"] is True
    blocker_codes = {row["code"] for row in dryrun["blockers"]}
    assert "accepted_state_write_gate_not_granted" in blocker_codes
    assert "projection_apply_previous_plan_stale_against_current_projection_sha" in blocker_codes
    assert "projection_apply_execute_write_not_requested" in blocker_codes
    assert target.read_text(encoding="utf-8") == current_text

    result = write_projection_apply_gate_rebaseline_dryrun(
        tmp_path,
        previous_plan_path=previous_plan_rel,
        generated_at="2026-06-04T06:12:00Z",
        max_context_age_seconds=60,
    )

    assert result["schema_id"] == APPLY_GATE_REBASELINE_DRYRUN_WRITE_RESULT_SCHEMA_ID
    assert result["previous_plan_stale_against_current_projection_sha"] is True
    assert result["current_plan_target_current"] is True
    assert result["projection_overwrite_performed"] is False
    assert result["accepted_projection_write_performed"] is False
    assert target.read_text(encoding="utf-8") == current_text

    dryrun_path = tmp_path / result["json_path"]
    plan_path = tmp_path / result["accepted_refresh_plan_path"]
    replacement_path = tmp_path / result["replacement_body_candidate_path"]
    receipt_path = tmp_path / result["operator_receipt_path"]
    assert dryrun_path.is_file()
    assert plan_path.is_file()
    assert replacement_path.is_file()
    assert receipt_path.is_file()
    written_dryrun = json.loads(dryrun_path.read_text(encoding="utf-8"))
    written_plan = json.loads(plan_path.read_text(encoding="utf-8"))
    written_replacement = json.loads(replacement_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert "_embedded_current_plan" not in written_dryrun
    assert "_embedded_replacement_body_candidate" not in written_dryrun
    assert written_plan["target"]["before_sha256"] == current_sha
    assert written_replacement["target"]["before_sha256"] == current_sha
    assert receipt["result"] == "projection_apply_gate_rebaseline_dryrun_written_no_accepted_state"
    assert receipt["target"]["current_before_sha256"] == current_sha


def test_projection_accepted_refresh_apply_requires_accepted_write_confirmation_and_execute(
    tmp_path: Path,
) -> None:
    _seed_projection_inputs(tmp_path)
    agent_id = "codex_cli:projection-apply-test"
    lease_id = "lease-projection-apply-test"
    target_rel = "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    _seed_projection_apply_lease(
        tmp_path,
        agent_id=agent_id,
        lease_id=lease_id,
        target_paths=[target_rel],
    )
    target = tmp_path / target_rel
    before_text = target.read_text(encoding="utf-8")
    replacement = build_projection_replacement_body_candidate(
        tmp_path,
        generated_at="2026-06-04T06:00:00Z",
        max_context_age_seconds=60,
    )

    result = apply_projection_accepted_refresh(
        tmp_path,
        confirmation=BOUNDED_WRITE_CONFIRMATION,
        accepted_state_write_confirmation="",
        idempotency_key="projection-apply-missing-accepted-confirmation",
        agent_id=agent_id,
        lease_id=lease_id,
        before_sha256=replacement["target"]["before_sha256"],
        replacement_body_sha256=replacement["target"]["candidate_body_sha256"],
        replacement_body=replacement["candidate_body"],
        execute_write=False,
        generated_at="2026-06-04T06:01:00Z",
    )

    assert result["schema_id"] == ACCEPTED_REFRESH_APPLY_SCHEMA_ID
    assert result["ok"] is False
    assert result["projection_overwrite_performed"] is False
    assert result["accepted_projection_write_performed"] is False
    assert result["mutates_active_state"] is False
    assert result["accepted_state_claim"] is False
    assert "projection_apply_accepted_state_write_confirmation_required" in result["blockers"]
    assert "projection_apply_execute_write_required" in result["blockers"]
    assert target.read_text(encoding="utf-8") == before_text


def test_projection_accepted_refresh_apply_rejects_hash_races_and_invariant_failure(tmp_path: Path) -> None:
    _seed_projection_inputs(tmp_path)
    agent_id = "codex_cli:projection-apply-test"
    lease_id = "lease-projection-apply-test"
    target_rel = "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    _seed_projection_apply_lease(
        tmp_path,
        agent_id=agent_id,
        lease_id=lease_id,
        target_paths=[target_rel],
    )
    target = tmp_path / target_rel
    before_text = target.read_text(encoding="utf-8")
    replacement = build_projection_replacement_body_candidate(
        tmp_path,
        generated_at="2026-06-04T06:00:00Z",
        max_context_age_seconds=60,
    )
    base_args = {
        "confirmation": BOUNDED_WRITE_CONFIRMATION,
        "accepted_state_write_confirmation": ACCEPTED_STATE_WRITE_CONFIRMATION,
        "idempotency_key": "projection-apply-rejects-races",
        "agent_id": agent_id,
        "lease_id": lease_id,
        "before_sha256": replacement["target"]["before_sha256"],
        "replacement_body_sha256": replacement["target"]["candidate_body_sha256"],
        "replacement_body": replacement["candidate_body"],
        "execute_write": True,
        "generated_at": "2026-06-04T06:01:00Z",
    }

    stale_before = apply_projection_accepted_refresh(
        tmp_path,
        **{**base_args, "before_sha256": "0" * 64, "idempotency_key": "projection-apply-stale-before"},
    )
    bad_replacement_hash = apply_projection_accepted_refresh(
        tmp_path,
        **{
            **base_args,
            "replacement_body_sha256": "1" * 64,
            "idempotency_key": "projection-apply-bad-replacement-hash",
        },
    )
    bad_body = json.loads(json.dumps(replacement["candidate_body"]))
    bad_body["summary"]["production_ready"] = True
    bad_body_sha = hashlib.sha256(json_write_text(bad_body).encode("utf-8")).hexdigest()
    bad_invariants = apply_projection_accepted_refresh(
        tmp_path,
        **{
            **base_args,
            "replacement_body": bad_body,
            "replacement_body_sha256": bad_body_sha,
            "idempotency_key": "projection-apply-bad-invariants",
        },
    )

    assert stale_before["ok"] is False
    assert "projection_apply_before_sha256_mismatch" in stale_before["blockers"]
    assert bad_replacement_hash["ok"] is False
    assert "projection_apply_replacement_body_sha256_mismatch" in bad_replacement_hash["blockers"]
    assert bad_invariants["ok"] is False
    assert "projection_apply_replacement_body_invariant_failure" in bad_invariants["blockers"]
    assert target.read_text(encoding="utf-8") == before_text


def test_projection_accepted_refresh_apply_writes_exact_projection_and_idempotent_receipt(
    tmp_path: Path,
) -> None:
    _seed_projection_inputs(tmp_path)
    agent_id = "codex_cli:projection-apply-test"
    lease_id = "lease-projection-apply-test"
    target_rel = "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    _seed_projection_apply_lease(
        tmp_path,
        agent_id=agent_id,
        lease_id=lease_id,
        target_paths=[target_rel],
    )
    replacement = build_projection_replacement_body_candidate(
        tmp_path,
        generated_at="2026-06-04T06:00:00Z",
        max_context_age_seconds=60,
    )
    apply_args = {
        "confirmation": BOUNDED_WRITE_CONFIRMATION,
        "accepted_state_write_confirmation": ACCEPTED_STATE_WRITE_CONFIRMATION,
        "idempotency_key": "projection-apply-happy-path",
        "agent_id": agent_id,
        "lease_id": lease_id,
        "before_sha256": replacement["target"]["before_sha256"],
        "replacement_body_sha256": replacement["target"]["candidate_body_sha256"],
        "replacement_body": replacement["candidate_body"],
        "execute_write": True,
        "generated_at": "2026-06-04T06:01:00Z",
    }

    applied = apply_projection_accepted_refresh(tmp_path, **apply_args)
    replayed = apply_projection_accepted_refresh(tmp_path, **{**apply_args, "generated_at": "2026-06-04T06:02:00Z"})
    conflict = apply_projection_accepted_refresh(
        tmp_path,
        **{**apply_args, "replacement_body_sha256": "2" * 64, "generated_at": "2026-06-04T06:03:00Z"},
    )

    target = tmp_path / target_rel
    assert applied["ok"] is True
    assert applied["status"] == "projection_accepted_refresh_applied"
    assert applied["projection_overwrite_performed"] is True
    assert applied["accepted_projection_write_performed"] is True
    assert applied["mutates_active_state"] is True
    assert applied["accepted_state_claim"] is True
    assert applied["production_authority"] is False
    assert applied["live_execution_authority"] is False
    assert applied["secrets_authority"] is False
    assert applied["materialization_authority"] is False
    assert applied["target"]["after_sha256"] == replacement["target"]["candidate_body_sha256"]
    assert target.read_text(encoding="utf-8") == json_write_text(replacement["candidate_body"])
    receipt_path = tmp_path / applied["receipt_path"]
    assert receipt_path.is_file()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["schema_id"] == "ion.domain_weaver.projection_accepted_refresh_apply_receipt.v0_1"
    assert receipt["target"]["path"] == target_rel
    assert receipt["target"]["after_sha256"] == replacement["target"]["candidate_body_sha256"]
    assert receipt["write_set"] == [target_rel, applied["receipt_path"]]
    assert receipt["production_authority"] is False
    assert receipt["live_execution_authority"] is False
    assert receipt["secrets_authority"] is False
    assert receipt["materialization_authority"] is False
    assert replayed["ok"] is True
    assert replayed["idempotent_replay"] is True
    assert replayed["mutates_active_state"] is False
    assert replayed["projection_overwrite_performed"] is False
    assert replayed["receipt_path"] == applied["receipt_path"]
    assert conflict["ok"] is False
    assert "projection_apply_idempotency_conflict" in conflict["blockers"]
