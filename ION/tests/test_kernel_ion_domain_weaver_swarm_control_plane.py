from __future__ import annotations

import hashlib
import json
from pathlib import Path

from kernel.ion_domain_weaver_swarm_control_plane import (
    CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_SCHEMA_ID,
    CONTEXT_GATE_REISSUE_APPLY_CONFIRMATION,
    CONTROL_PLANE_SCHEMA_ID,
    EXACT_REISSUE_REQUEST_DISPATCH_READINESS_SCHEMA_ID,
    FLEET_PLAN_SCHEMA_ID,
    GLOBAL_QUEUE_HYGIENE_SCHEMA_ID,
    GLOBAL_QUEUE_REPAIR_PREVIEW_SCHEMA_ID,
    GENERATED_MOUNT_CREATION_SCHEMA_ID,
    QUEUE_METADATA_IDENTITY_ASSIGNMENT_SCHEMA_ID,
    QUEUE_METADATA_IDENTITY_REISSUE_APPLY_CONFIRMATION,
    QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_SCHEMA_ID,
    QUEUE_METADATA_SOURCE_SAFETY_REVIEW_SCHEMA_ID,
    QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_SCHEMA_ID,
    POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_SCHEMA_ID,
    STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_CONFIRMATION,
    STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_SCHEMA_ID,
    STALE_WAITING_RECONCILIATION_SETTLEMENT_CONFIRMATION,
    STALE_WAITING_RECONCILIATION_SETTLEMENT_SCHEMA_ID,
    STALE_WAITING_RECONCILIATION_REVIEW_SCHEMA_ID,
    SWARM_READINESS_SCHEMA_ID,
    WATCH_MATRIX_SCHEMA_ID,
    apply_context_gate_blocked_request_reissue,
    apply_queue_metadata_identity_reissue_apply_review,
    build_limited_watch_matrix_refresh,
    build_global_queue_backlog_context_identity_hygiene,
    build_global_queue_backlog_identity_repair_preview,
    build_context_gate_blocked_request_reissue,
    build_exact_reissue_request_dispatch_readiness,
    build_generated_mount_creation_for_metadata_reissue,
    build_queue_metadata_identity_assignment,
    build_queue_metadata_identity_reissue_apply_review,
    build_queue_metadata_source_safety_review,
    build_queue_request_metadata_identity_reissue,
    build_post_sidecar_global_queue_hygiene,
    build_stale_non_domain_queue_quarantine_settlement,
    build_stale_waiting_reconciliation_settlement,
    build_stale_waiting_reconciliation_review,
    build_swarm_control_plane,
    build_swarm_fleet_plan,
    build_swarm_readiness,
    build_swarm_watch_matrix,
    validate_current_proposal_wave,
    write_global_queue_backlog_context_identity_hygiene,
    write_global_queue_backlog_identity_repair_preview,
    write_context_gate_blocked_request_reissue,
    write_exact_reissue_request_dispatch_readiness,
    write_generated_mount_creation_for_metadata_reissue,
    write_queue_metadata_identity_assignment,
    write_queue_metadata_identity_reissue_apply_review,
    write_queue_metadata_source_safety_review,
    write_queue_request_metadata_identity_reissue,
    write_post_sidecar_global_queue_hygiene,
    write_stale_non_domain_queue_quarantine_settlement,
    write_stale_waiting_reconciliation_settlement,
    write_stale_waiting_reconciliation_review,
    write_limited_watch_matrix_refresh,
    write_swarm_control_plane,
)


def _active_root(tmp_path: Path) -> Path:
    root = tmp_path / "active"
    (root / "ION").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = 'ion-test'\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").write_text("authority\n", encoding="utf-8")
    codex_solo = root / "ION/05_context/current/codex_solo"
    codex_solo.mkdir(parents=True, exist_ok=True)
    (codex_solo / "CAPSULE.md").write_text("# capsule\n", encoding="utf-8")
    (codex_solo / "MINI.md").write_text("# mini\n", encoding="utf-8")
    (codex_solo / "HOT_CONTEXT.md").write_text("# hot\n", encoding="utf-8")
    _write_json(root, "ION/05_context/current/codex_solo/LONG_HORIZON.json", {"epoch_count": 1})
    _write_json(root, "ION/05_context/current/codex_solo/ROUTE.json", {"entries": []})
    _write_json(
        root,
        "ION/05_context/current/codex_solo/STATUS.json",
        {"authority": {"production_authority": False, "live_execution_authority": False}},
    )
    _write_json(
        root,
        "ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json",
        {
            "generated_at": "2026-06-04T17:00:00+00:00",
            "package_count": 3,
            "packages": [
                {"path_refs": ["ION/05_context/current/codex_solo/CAPSULE.md"]},
                {"path_refs": ["ION/05_context/current/codex_solo/MINI.md"]},
                {"path_refs": ["ION/05_context/current/codex_solo/HOT_CONTEXT.md"]},
            ],
        },
    )
    return root


def _write_json(root: Path, rel: str, payload: dict) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _mount(root: Path, mount_id: str, *, lane_id: str) -> Path:
    mount_root = root / "ION/05_context/current/codex_agent_mounts" / mount_id
    ion_dir = mount_root / ".ion"
    ion_dir.mkdir(parents=True, exist_ok=True)
    if "__domain_" in mount_id:
        role_fragment, domain_fragment = mount_id.split("__domain_", 1)
        role_id = "role." + role_fragment.removeprefix("role_")
        domain_id = "domain." + domain_fragment
    else:
        role_id = "role.test"
        domain_id = "domain.test"
    for name in (
        "ION_CONTEXT_CAPSULE.yaml",
        "AGENT.yaml",
        "DOMAIN.yaml",
        "RELATIONSHIPS.yaml",
        "COMMUNICATIONS.json",
        "ADDRESS_BOOK.json",
    ):
        (ion_dir / name).write_text(f"{name}\n", encoding="utf-8")
    (ion_dir / "ACTIVE_CONTEXT_PACKAGE.md").write_text("active\n", encoding="utf-8")
    _write_json(
        root,
        f"ION/05_context/current/codex_agent_mounts/{mount_id}/.ion/ACTIVE_CONTEXT_PACKAGE.json",
        {"lane_id": lane_id, "domain_id": domain_id, "role_id": role_id},
    )
    _write_json(
        root,
        f"ION/05_context/current/codex_agent_mounts/{mount_id}/.ion/CONTEXT_IDENTITY.json",
        {
            "mount_id": mount_id,
            "domain_id": domain_id,
            "role_id": role_id,
            "lane_id": lane_id,
        },
    )
    _write_json(
        root,
        f"ION/05_context/current/codex_agent_mounts/{mount_id}/ION_AGENT_MOUNT_MANIFEST.json",
        {
            "mount_id": mount_id,
            "mount_path": f"ION/05_context/current/codex_agent_mounts/{mount_id}",
            "domain_id": domain_id,
            "agent_role_id": role_id,
            "portable_active_context_package_md_path": (
                f"ION/05_context/current/codex_agent_mounts/{mount_id}/.ion/ACTIVE_CONTEXT_PACKAGE.md"
            ),
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
    )
    return ion_dir


def _mount_manifest(root: Path, mount_id: str, *, domain_id: str, role_id: str) -> None:
    _mount(root, mount_id, lane_id="test_lane")
    _write_json(
        root,
        f"ION/05_context/current/codex_agent_mounts/{mount_id}/ION_AGENT_MOUNT_MANIFEST.json",
        {
            "mount_id": mount_id,
            "mount_path": f"ION/05_context/current/codex_agent_mounts/{mount_id}",
            "domain_id": domain_id,
            "agent_role_id": role_id,
            "portable_active_context_package_md_path": (
                f"ION/05_context/current/codex_agent_mounts/{mount_id}/.ion/ACTIVE_CONTEXT_PACKAGE.md"
            ),
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
    )


def _working_capsule_identity(
    root: Path,
    *,
    mount_id: str,
    domain_id: str,
    role_id: str,
) -> dict[str, object]:
    from kernel.ion_working_capsule_identity import build_working_capsule_identity

    mount_root = root / "ION/05_context/current/codex_agent_mounts" / mount_id
    return build_working_capsule_identity(
        root=root,
        cwd=mount_root,
        domain_id=domain_id,
        role_id=role_id,
        carrier_instance_id="codex_session_swarm_queue_hygiene_test",
        codex_agent_mount=mount_root,
    ).to_dict()


def _write_work_request(root: Path, name: str, payload: dict) -> Path:
    path = root / "ION/05_context/current/chatgpt_connector/codex_work_requests" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    default = {
        "request_id": name.removesuffix(".json"),
        "path": path.relative_to(root).as_posix(),
        "status": "QUEUED_FOR_CODEX_CARRIER",
        "created_at": "2026-06-04T10:00:00+00:00",
        "updated_at": "2026-06-04T10:00:00+00:00",
        "objective": "Domain Weaver queue hygiene test",
        "dedupe_key": name,
        "objective_sha256": name,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }
    default.update(payload)
    path.write_text(json.dumps(default, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _seed_runtime_status(root: Path, *, updated_at: str) -> None:
    _write_json(
        root,
        "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json",
        {
            "schema_id": "ion.codex_queue_runner_state.v0_1",
            "updated_at": updated_at,
            "active_run": None,
            "active_runs": {},
            "concurrency": {
                "active_lane_count": 0,
                "active_lane_ids": [],
                "active_run_count": 0,
                "global_active_lock": False,
                "unknown_lane_active_run_count": 0,
            },
        },
    )


def _write_exact_reissue_request(
    root: Path,
    *,
    request_class: str = "metadata_identity_reissue",
    name: str = "codex_req_metadata_identity_reissue_test.json",
    lane_id: str = "architecture_lane",
    domain_id: str = "domain.codex_carrier_sync",
    role_id: str = "role.exact_active_binding_specialist",
    callsign: str = "EXACT_ACTIVE_BINDING_SPECIALIST",
    mount_id: str = "role_exact_active_binding_specialist__domain_codex_carrier_sync",
) -> Path:
    _mount_manifest(root, mount_id, domain_id=domain_id, role_id=role_id)
    request_id = name.removesuffix(".json")
    source = _write_work_request(
        root,
        f"{request_id}_source.json",
        {
            "request_id": f"{request_id}_source",
            "lane_id": lane_id,
            "domain_id": "",
            "role_id": role_id,
            "request_kind": "source_missing_metadata_identity",
            "working_capsule_identity": None,
        },
    )
    source_rel = source.relative_to(root).as_posix()
    request_path = (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/" + name
    )
    assignment = {
        "selected_mount_id": mount_id,
        "selected_mount_path": f"ION/05_context/current/codex_agent_mounts/{mount_id}",
        "active_context_package_path": (
            f"ION/05_context/current/codex_agent_mounts/{mount_id}/.ion/ACTIVE_CONTEXT_PACKAGE.md"
        ),
        "domain_id": domain_id,
        "lane_id": lane_id,
        "role_id": role_id,
        "callsign": callsign,
        "request_kind": "exact_reissue_test",
        "work_class": "exact_reissue_test",
    }
    reissue_body = {
        "schema_id": f"ion.domain_weaver.{request_class}_request_body.v0_1_candidate",
        "apply_review_only": True,
        "apply_performed": False,
        "generated_at": "2026-06-04T19:00:00Z",
        "assignment": assignment,
        "source_request_id": f"{request_id}_source",
        "source_request_path": source_rel,
        "source_request_sha256": _sha256_file(source),
        "replacement_request_id": request_id,
        "replacement_request_path": request_path,
    }
    body_key = (
        "context_gate_reissue"
        if request_class == "context_gate_reissue"
        else "metadata_identity_reissue"
    )
    payload = {
        "request_id": request_id,
        "path": request_path,
        "status": "QUEUED_FOR_CODEX_CARRIER",
        "request_kind": "exact_reissue_test",
        "active_context_check_status": (
            "context_gate_reissue_candidate_ready"
            if request_class == "context_gate_reissue"
            else "metadata_identity_reissue_apply_review_ready"
        ),
        "domain_id": domain_id,
        "lane_id": lane_id,
        "role_id": role_id,
        "callsign": callsign,
        "exact_request_path_required": True,
        "general_queue_processing_allowed": False,
        "working_capsule_identity": _working_capsule_identity(
            root,
            mount_id=mount_id,
            domain_id=domain_id,
            role_id=role_id,
        ),
        body_key: reissue_body,
    }
    return _write_work_request(root, name, payload)


def _seed_current_evidence(root: Path) -> None:
    _write_text(
        root,
        "ION/05_context/current/domain_weaver/.ion/ION_CONTEXT_CAPSULE.yaml",
        "\n".join(
            [
                "schema_id: ion.folder_local_context_capsule.v0_1",
                "context_id: domain_weaver_current_context",
                f"active_root: {root}",
                "shared_codex_solo_is_working_capsule: false",
                "last_refreshed_at: 2026-06-04T17:11:31Z",
                "materialization_ready: false",
            ]
        )
        + "\n",
    )
    _write_text(
        root,
        "ION/05_context/current/domain_weaver/lead_dev_self_context/LEAD_DEV_CODEX_OPERATING_PACKAGE.latest.md",
        "lead context\n",
    )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json",
        {
            "schema_id": "ion.domain_weaver.projection.v1",
            "summary": {
                "materialization_ready": False,
                "ui_operator_usable": False,
            },
        },
    )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/PROMOTION_GATE.json",
        {"gate_status": "candidate_only"},
    )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/self_evolution_readiness/DOMAIN_WEAVER_SELF_EVOLUTION_READINESS.latest.json",
        {
            "schema_id": "ion.domain_weaver.self_evolution_readiness.v0_1",
            "verdict": "NOT_READY_BLOCKED_BY_MATERIALIZATION_READY_FALSE",
            "blockers_ranked": [
                {
                    "code": "MATERIALIZATION_READY_FALSE",
                    "severity": "critical",
                    "detail": "materialization false",
                    "evidence": [
                        "ION/05_context/current/domain_weaver/.ion/ION_CONTEXT_CAPSULE.yaml"
                    ],
                },
                {
                    "code": "AUTOMATIC_ORIGINAL_AGENT_REACTION_NOT_PROVEN",
                    "severity": "critical",
                    "detail": "original reaction unproven",
                    "evidence": [
                        "ION/05_context/current/domain_weaver/comms_autoreaction/proof.json"
                    ],
                },
            ],
        },
    )
    _write_json(
        root,
        "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json",
        {"requests": []},
    )
    _write_json(
        root,
        "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json",
        {"active_run": None},
    )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/larger_fanout/DOMAIN_WEAVER_LARGER_FANOUT_CONTROL_READINESS.latest.json",
        {"readiness_ok": True, "max_candidate_lane_count": 3},
    )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/proposal_wave/DOMAIN_WEAVER_PROPOSAL_WRITE_SWARM_FANIN.latest.json",
        {
            "schema_id": "ion.domain_weaver.proposal_write_swarm_fanin.v0_1_candidate",
            "lanes": [
                {
                    "lane_id": "validator_ok",
                    "candidate_only": True,
                    "source_files_edited": False,
                    "patch_proposal_unapplied": True,
                    "files": {
                        "workspace": {
                            "path": "ION/05_context/current/domain_weaver/proposal_wave/test_wave/validator_ok/PROPOSAL_WORKSPACE.json"
                        },
                        "proposal_json": {
                            "path": "ION/05_context/current/domain_weaver/proposal_wave/test_wave/validator_ok/proposal.candidate.json"
                        },
                        "proposal_md": {
                            "path": "ION/05_context/current/domain_weaver/proposal_wave/test_wave/validator_ok/proposal.candidate.md"
                        },
                        "patch_proposal": {
                            "path": "ION/05_context/current/domain_weaver/proposal_wave/test_wave/validator_ok/patch_proposal.diff"
                        },
                    },
                }
            ],
        },
    )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/proposal_wave/test_wave/validator_ok/PROPOSAL_WORKSPACE.json",
        {
            "schema_id": "ion.domain_weaver.proposal_workspace.v0_1_candidate",
            "authority": {
                "raw_source_write_authority": False,
                "patch_apply_authority": False,
            },
        },
    )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/proposal_wave/test_wave/validator_ok/proposal.candidate.json",
        {"schema_id": "test.proposal", "candidate_only": True},
    )
    _write_text(
        root,
        "ION/05_context/current/domain_weaver/proposal_wave/test_wave/validator_ok/proposal.candidate.md",
        "proposal\n",
    )
    _write_text(
        root,
        "ION/05_context/current/domain_weaver/proposal_wave/test_wave/validator_ok/patch_proposal.diff",
        "diff --git a/example b/example\n",
    )


def test_swarm_watch_matrix_defines_real_watch_targets_without_starting_workers(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)

    matrix = build_swarm_watch_matrix(root, generated_at="2026-06-04T17:30:00Z")

    assert matrix["schema_id"] == WATCH_MATRIX_SCHEMA_ID
    assert matrix["coverage"]["target_count"] >= 16
    target_ids = {row["target_id"] for row in matrix["targets"]}
    assert "queue_state" in target_ids
    assert "worker_state" in target_ids
    assert "receipt_gaps" in target_ids
    assert "context_graph_deltas" in target_ids
    assert "accepted_state_confusion" in target_ids
    assert matrix["actual_watch_daemon_started"] is False
    assert matrix["worker_start_allowed"] is False
    assert matrix["accepted_state_claimed"] is False


def test_swarm_fleet_plan_composes_lifecycle_and_existing_wave_previews(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)

    plan = build_swarm_fleet_plan(root, generated_at="2026-06-04T17:30:00Z")

    assert plan["schema_id"] == FLEET_PLAN_SCHEMA_ID
    assert plan["lane_count"] >= 12
    lane_ids = {row["lane_id"] for row in plan["lanes"]}
    assert "root_steward_command" in lane_ids
    assert "fleet_spawn_lifecycle" in lane_ids
    assert "nemesis_vice_review" in lane_ids
    assert plan["pressure_wave_preview"]["actual_spawn_performed"] is False
    assert plan["proposal_wave_preview"]["codex_queue_run_started"] is False
    assert plan["caps"]["recursive_child_spawn_cap"] == 0
    assert plan["actual_spawn_performed"] is False
    assert plan["accepted_state_claimed"] is False


def test_proposal_wave_validator_accepts_boxed_candidate_returns(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)

    validation = validate_current_proposal_wave(root)

    assert validation["validator_available"] is True
    assert validation["ok"] is True
    assert validation["lane_count"] == 1
    assert validation["lane_results"][0]["ok"] is True
    assert validation["source_files_edited_by_workers"] is False
    assert validation["accepted_state_claimed"] is False


def test_swarm_readiness_separates_limited_watch_from_serious_self_evolution(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)

    readiness = build_swarm_readiness(root, generated_at="2026-06-04T17:30:00Z")

    assert readiness["schema_id"] == SWARM_READINESS_SCHEMA_ID
    assert readiness["root_proof"]["proof_ok"] is True
    assert readiness["verdict"] == "READY_FOR_LIMITED_SWARM_WATCH_AND_FANOUT"
    assert readiness["ready_for_limited_watch_and_fanout"] is True
    assert readiness["ready_for_supervised_candidate_wave"] is False
    blocker_codes = {row["code"] for row in readiness["blockers_ranked"]}
    assert "MATERIALIZATION_READY_FALSE" in blocker_codes
    assert "AUTOMATIC_ORIGINAL_AGENT_REACTION_NOT_PROVEN" in blocker_codes


def test_write_swarm_control_plane_artifacts_and_receipt(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)

    result = write_swarm_control_plane(root, generated_at="2026-06-04T17:30:00Z")

    assert result["verdict"] == "READY_FOR_LIMITED_SWARM_WATCH_AND_FANOUT"
    for key in [
        "report_path",
        "readiness_path",
        "watch_matrix_path",
        "fleet_plan_path",
        "context_graph_delta_path",
        "operator_receipt_path",
    ]:
        assert (root / result[key]).is_file()
    control_text = (root / result["report_path"]).read_text(encoding="utf-8")
    readiness = json.loads((root / result["readiness_path"]).read_text(encoding="utf-8"))
    control = build_swarm_control_plane(root, generated_at="2026-06-04T17:30:00Z")
    assert control["schema_id"] == CONTROL_PLANE_SCHEMA_ID
    assert "Domain Weaver Swarm Control Plane" in control_text
    assert readiness["verdict"] == "READY_FOR_LIMITED_SWARM_WATCH_AND_FANOUT"


def test_global_queue_hygiene_blocks_dirty_backlog_but_preserves_exact_path_candidates(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    mount_id = "role_wave_scheduler__domain_domain_weaver_fanout_control"
    _mount(root, mount_id, lane_id="architecture_lane")
    identity = _working_capsule_identity(
        root,
        mount_id=mount_id,
        domain_id="domain.domain_weaver_fanout_control",
        role_id="role.wave_scheduler",
    )
    exact_path = _write_work_request(
        root,
        "exact_spawn_dispatch.json",
        {
            "request_id": "codex_req_exact_spawn_dispatch",
            "lane_id": "architecture_lane",
            "domain_id": "domain.domain_weaver_fanout_control",
            "role_id": "role.wave_scheduler",
            "agent_role_id": "role.wave_scheduler",
            "role_tier": "specialist",
            "callsign": "Babbage",
            "work_class": "domain_weaver_spawn_dispatch",
            "request_kind": "domain_weaver_spawn_dispatch",
            "selected_mount_id": mount_id,
            "selected_mount_path": f"ION/05_context/current/codex_agent_mounts/{mount_id}",
            "working_capsule_identity": identity,
        },
    )
    _write_work_request(
        root,
        "dirty_missing_domain.json",
        {
            "request_id": "codex_req_dirty_missing_domain",
            "lane_id": "audit_lane",
            "domain_id": "",
            "role_id": "",
            "work_class": "legacy_queue_backlog",
            "request_kind": "legacy_queue_backlog",
            "working_capsule_identity": None,
        },
    )
    _write_work_request(
        root,
        "terminal_invalid.json",
        {
            "request_id": "codex_req_terminal_invalid",
            "status": "RETURN_TEMPLATE_INVALID",
            "created_at": "2026-06-01T10:00:00+00:00",
            "updated_at": "2026-06-01T10:00:00+00:00",
            "objective": "Audit template invalid return.",
            "dedupe_key": "terminal-invalid",
            "objective_sha256": "terminal-invalid",
        },
    )

    result = build_global_queue_backlog_context_identity_hygiene(
        root,
        generated_at="2026-06-04T17:40:00Z",
    )

    assert result["schema_id"] == GLOBAL_QUEUE_HYGIENE_SCHEMA_ID
    assert result["verdict"] == "GLOBAL_QUEUE_CONTEXT_IDENTITY_HYGIENE_BLOCKED_EXACT_PATH_ONLY"
    assert result["general_queue_processing_allowed"] is False
    assert result["codex_queue_run_started"] is False
    assert result["actual_spawn_performed"] is False
    assert result["candidate_exact_request_paths"] == [
        exact_path.relative_to(root).as_posix()
    ]
    blocker_codes = {row["code"] for row in result["blockers_ranked"]}
    assert "GLOBAL_QUEUE_BACKLOG_CONTEXT_IDENTITY_HYGIENE_NOT_CLEAN" in blocker_codes
    assert "QUEUEABLE_REQUESTS_MISSING_DOMAIN_ID" in blocker_codes
    assert result["summary"]["terminal_repair_request_count"] == 1
    assert any(
        packet["packet_id"]
        == "PCKT-DOMAIN-WEAVER-GLOBAL-QUEUE-BACKLOG-IDENTITY-REPAIR-PREVIEW-V0_1"
        for packet in result["repair_packets"]
    )
    assert result["candidate_context_graph_deltas"]["accepted_state_claimed"] is False


def test_write_global_queue_hygiene_artifacts_and_receipt(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _write_work_request(
        root,
        "dirty_missing_domain.json",
        {
            "request_id": "codex_req_dirty_missing_domain",
            "lane_id": "audit_lane",
            "domain_id": "",
            "work_class": "legacy_queue_backlog",
            "request_kind": "legacy_queue_backlog",
            "working_capsule_identity": None,
        },
    )

    result = write_global_queue_backlog_context_identity_hygiene(
        root,
        generated_at="2026-06-04T17:41:00Z",
    )

    assert result["schema_id"].endswith(".write_result.v0_1")
    assert result["verdict"] == "GLOBAL_QUEUE_CONTEXT_IDENTITY_HYGIENE_BLOCKED_EXACT_PATH_ONLY"
    for key in [
        "hygiene_path",
        "report_path",
        "context_graph_delta_path",
        "operator_receipt_path",
    ]:
        assert (root / result[key]).is_file()
    written = json.loads((root / result["hygiene_path"]).read_text(encoding="utf-8"))
    assert written["general_queue_processing_allowed"] is False
    assert written["accepted_state_claimed"] is False
    report_text = (root / result["report_path"]).read_text(encoding="utf-8")
    assert "Global Queue Backlog Context Identity Hygiene" in report_text


def test_post_sidecar_global_queue_hygiene_classifies_seven_queued_originals_without_broad_queue_authority(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    source_specs = [
        (
            "desktop_rescue.json",
            "codex_req_desktop_rescue",
            "desktop_rescue_execution",
            "desktop_rescue_execution_after_codex_gemini_webgpu_freeze",
            "maintenance_lane",
        ),
        (
            "incident_nemesis.json",
            "codex_req_context_capsule_identity_incident_nemesis",
            "incident_nemesis_review",
            "read_only_nemesis",
            "implementation_lane",
        ),
        (
            "receipt_pointer_lineage.json",
            "codex_req_domain_weaver_receipt_pointer_lineage_repair_20260603_attempt_001",
            "receipt_pointer_lineage_repair",
            "domain_weaver_receipt_pointer_lineage_repair",
            "audit_lane",
        ),
        (
            "monolith_decomposition.json",
            "codex_req_domain_weaver_stewarded_autonomy_trial_01_monolith_decomposition_cartographer_20260603_attempt_001",
            "monolith_decomposition_cartography",
            "domain_weaver_stewarded_autonomy_monolith_decomposition_cartography",
            "architecture_lane",
        ),
        (
            "exact_active_binding.json",
            "codex_req_domain_weaver_stewarded_autonomy_trial_02_exact_active_binding_specialist_20260603_attempt_001",
            "exact_active_binding_audit",
            "domain_weaver_stewarded_autonomy_exact_active_binding_audit",
            "architecture_lane",
        ),
        (
            "receipt_integrity_graph.json",
            "codex_req_domain_weaver_stewarded_autonomy_trial_03_receipt_integrity_proof_graph_steward_20260603_attempt_001",
            "receipt_integrity_proof_graph",
            "domain_weaver_stewarded_autonomy_receipt_integrity_proof_graph",
            "audit_lane",
        ),
        (
            "continuous_nemesis.json",
            "codex_req_domain_weaver_stewarded_autonomy_trial_04_continuous_nemesis_20260603_attempt_001",
            "continuous_nemesis_review",
            "domain_weaver_stewarded_autonomy_continuous_nemesis",
            "audit_lane",
        ),
    ]
    source_refs: dict[str, tuple[str, str]] = {}
    for filename, request_id, work_class, request_kind, lane_id in source_specs:
        path = _write_work_request(
            root,
            filename,
            {
                "request_id": request_id,
                "lane_id": lane_id,
                "domain_id": "",
                "role_id": "",
                "work_class": work_class,
                "request_kind": request_kind,
                "working_capsule_identity": None,
            },
        )
        source_refs[request_id] = (path.relative_to(root).as_posix(), _sha256_file(path))

    external_id = "codex_req_desktop_rescue"
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/queue_governance/DOMAIN_WEAVER_STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT.latest.json",
        {
            "schema_id": "ion.domain_weaver.stale_non_domain_queue_quarantine_settlement.v0_1_candidate",
            "verdict": "STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_WRITTEN",
            "settlement_rows": [
                {
                    "source_request_id": external_id,
                    "source_request_path": source_refs[external_id][0],
                    "source_request_sha256": source_refs[external_id][1],
                    "settlement_ready": True,
                    "settlement_decision": "quarantine_as_stale_external_non_domain",
                    "metadata_assignment_quarantine_may_clear": True,
                    "source_hash_matches_assignment": True,
                }
            ],
        },
    )
    stale_rows = []
    replacement_statuses = [
        "RETURN_RECORDED_PROOF_ACCEPTED",
        "RETURN_RECORDED_PROOF_ACCEPTED",
        "RETURN_RECORDED_PROOF_ACCEPTED",
        "CODEX_QUEUE_RUNNER_FAILED",
        "CODEX_QUEUE_RUNNER_FAILED",
        "CODEX_QUEUE_RUNNER_FAILED",
    ]
    for index, request_id in enumerate([spec[1] for spec in source_specs if spec[1] != external_id]):
        source_path, source_sha = source_refs[request_id]
        stale_rows.append(
            {
                "source_request_id": request_id,
                "source_request_path": source_path,
                "source_request_sha256": source_sha,
                "settlement_ready": True,
                "settlement_decision": "supersede_with_fresh_exact_request",
                "metadata_reissue_source_safety_may_clear": True,
                "source_hash_matches_review": True,
            }
        )
        replacement_id = f"codex_req_metadata_identity_reissue_20260604t184840z_{index}"
        replacement_path = (
            "ION/05_context/current/chatgpt_connector/codex_work_requests/"
            f"{replacement_id}.json"
        )
        _write_work_request(
            root,
            f"{replacement_id}.json",
            {
                "request_id": replacement_id,
                "status": replacement_statuses[index],
                "path": replacement_path,
                "domain_id": "domain.receipt_proof_graph",
                "lane_id": "audit_lane",
                "role_id": "role.receipt_integrity_proof_graph_steward",
                "exact_request_path_required": True,
                "general_queue_processing_allowed": False,
                "metadata_identity_reissue": {
                    "source_request_id": request_id,
                    "source_request_path": source_path,
                    "source_request_sha256": source_sha,
                    "replacement_request_id": replacement_id,
                    "replacement_request_path": replacement_path,
                },
            },
        )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/queue_governance/DOMAIN_WEAVER_STALE_WAITING_RECONCILIATION_SETTLEMENT.latest.json",
        {
            "schema_id": "ion.domain_weaver.stale_waiting_reconciliation_settlement.v0_2_candidate",
            "verdict": "STALE_WAITING_RECONCILIATION_SETTLEMENT_WRITTEN",
            "settlement_rows": stale_rows,
        },
    )
    before_sources = {
        path: (root / path).read_text(encoding="utf-8")
        for path, _sha in source_refs.values()
    }

    readback = build_post_sidecar_global_queue_hygiene(
        root,
        generated_at="2026-06-04T21:50:00Z",
    )

    assert readback["schema_id"] == POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_SCHEMA_ID
    assert (
        readback["verdict"]
        == "POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_CLASSIFIED_EXACT_PATH_ONLY_REPLACEMENT_FAILURES_PRESENT"
    )
    assert readback["general_queue_processing_allowed"] is False
    assert readback["codex_queue_run_started"] is False
    assert readback["actual_spawn_performed"] is False
    assert readback["source_request_files_mutated"] is False
    assert readback["replacement_request_files_written"] == 0
    assert readback["all_expected_source_originals_classified"] is True
    summary = readback["summary"]
    assert summary["queued_source_original_count"] == 7
    assert summary["quarantine_as_stale_external_non_domain_count"] == 1
    assert summary["supersede_with_fresh_exact_request_count"] == 6
    assert summary["replacement_request_found_count"] == 6
    assert summary["replacement_return_accepted_count"] == 3
    assert summary["replacement_failed_count"] == 3
    assert summary["replacement_current_status_counts"]["CODEX_QUEUE_RUNNER_FAILED"] == 3
    blocker_codes = {row["code"] for row in readback["blockers_ranked"]}
    assert "GLOBAL_QUEUE_BACKLOG_CONTEXT_IDENTITY_HYGIENE_NOT_CLEAN" in blocker_codes
    assert "POST_SIDECAR_REPLACEMENT_REQUEST_FAILURES_PRESENT" in blocker_codes
    rows_by_id = {row["source_request_id"]: row for row in readback["source_original_rows"]}
    assert rows_by_id[external_id]["candidate_classification"] == "quarantine_as_stale_external_non_domain"
    assert rows_by_id["codex_req_context_capsule_identity_incident_nemesis"][
        "candidate_classification"
    ] == "supersede_with_fresh_exact_request"

    result = write_post_sidecar_global_queue_hygiene(
        root,
        generated_at="2026-06-04T21:51:00Z",
    )

    for key in ["readback_path", "report_path", "context_graph_delta_path", "operator_receipt_path"]:
        assert (root / result[key]).is_file()
    written = json.loads((root / result["readback_path"]).read_text(encoding="utf-8"))
    assert written["general_queue_processing_allowed"] is False
    assert written["summary"]["queued_source_original_count"] == 7
    report_text = (root / result["report_path"]).read_text(encoding="utf-8")
    assert "Post-Sidecar Global Queue Hygiene" in report_text
    for path, text in before_sources.items():
        assert (root / path).read_text(encoding="utf-8") == text


def test_global_queue_repair_preview_emits_candidate_rows_without_mutation(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    mount_id = "role_wave_scheduler__domain_domain_weaver_fanout_control"
    _mount(root, mount_id, lane_id="architecture_lane")
    identity = _working_capsule_identity(
        root,
        mount_id=mount_id,
        domain_id="domain.domain_weaver_fanout_control",
        role_id="role.wave_scheduler",
    )
    exact_path = _write_work_request(
        root,
        "exact_spawn_dispatch.json",
        {
            "request_id": "codex_req_exact_spawn_dispatch",
            "lane_id": "architecture_lane",
            "domain_id": "domain.domain_weaver_fanout_control",
            "role_id": "role.wave_scheduler",
            "agent_role_id": "role.wave_scheduler",
            "role_tier": "specialist",
            "callsign": "Babbage",
            "work_class": "domain_weaver_spawn_dispatch",
            "request_kind": "domain_weaver_spawn_dispatch",
            "selected_mount_id": mount_id,
            "selected_mount_path": f"ION/05_context/current/codex_agent_mounts/{mount_id}",
            "working_capsule_identity": identity,
        },
    )
    _write_work_request(
        root,
        "dirty_missing_domain.json",
        {
            "request_id": "codex_req_dirty_missing_domain",
            "lane_id": "audit_lane",
            "domain_id": "",
            "role_id": "",
            "work_class": "legacy_queue_backlog",
            "request_kind": "legacy_queue_backlog",
            "working_capsule_identity": None,
        },
    )
    _write_work_request(
        root,
        "context_gate_blocked.json",
        {
            "request_id": "codex_req_context_gate_blocked",
            "status": "CODEX_QUEUE_RUNNER_BLOCKED_CONTEXT_GATE",
            "lane_id": "context_lane",
            "domain_id": "domain.agent_communication_systems",
            "role_id": "role.context_cartographer",
            "work_class": "domain_weaver_agent_comms_queue_runner_pickup_proof",
            "request_kind": "agent_context_gate_blocked",
            "context_gate": {
                "finding": "no_matching_active_context_mount_for_lane",
                "context_active_resolver": {
                    "blockers": ["no_matching_active_context_mount_for_lane"]
                },
            },
            "working_capsule_identity": None,
        },
    )
    _write_work_request(
        root,
        "terminal_invalid.json",
        {
            "request_id": "codex_req_terminal_invalid",
            "status": "RETURN_TEMPLATE_INVALID",
            "created_at": "2026-06-01T10:00:00+00:00",
            "updated_at": "2026-06-01T10:00:00+00:00",
            "objective": "Audit template invalid return.",
            "dedupe_key": "terminal-invalid",
            "objective_sha256": "terminal-invalid",
        },
    )

    preview = build_global_queue_backlog_identity_repair_preview(
        root,
        generated_at="2026-06-04T17:50:00Z",
    )

    assert preview["schema_id"] == GLOBAL_QUEUE_REPAIR_PREVIEW_SCHEMA_ID
    assert preview["verdict"] == "GLOBAL_QUEUE_REPAIR_PREVIEW_ROWS_READY_MUTATION_GATE_REQUIRED"
    assert preview["request_files_mutated"] is False
    assert preview["lifecycle_ledger_mutated"] is False
    assert preview["codex_queue_run_started"] is False
    assert preview["candidate_exact_request_paths"] == [
        exact_path.relative_to(root).as_posix()
    ]
    repair_classes = {row["repair_class"] for row in preview["queueable_repair_rows"]}
    assert "metadata_identity_reissue_required" in repair_classes
    assert "context_gate_reissue_required" in repair_classes
    assert preview["summary"]["lifecycle_preview_row_count"] == 1
    lifecycle_row = preview["lifecycle_preview_rows"][0]
    assert lifecycle_row["lifecycle_preview_metadata_status"] == "STALE_PREVIEW_NOT_CURRENT_ROUTE_IDENTITY"
    assert lifecycle_row["identity_scope"] == "historical_source_queue_lifecycle_preview"
    assert lifecycle_row["current_route_identity_authority"] is False
    assert lifecycle_row["current_mount_identity_authority"] is False
    assert preview["candidate_context_graph_deltas"]["accepted_state_claimed"] is False
    assert all(row["would_mutate_request_file"] is False for row in preview["queueable_repair_rows"])


def test_write_global_queue_repair_preview_artifacts_and_receipt(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _write_work_request(
        root,
        "dirty_missing_domain.json",
        {
            "request_id": "codex_req_dirty_missing_domain",
            "lane_id": "audit_lane",
            "domain_id": "",
            "work_class": "legacy_queue_backlog",
            "request_kind": "legacy_queue_backlog",
            "working_capsule_identity": None,
        },
    )

    result = write_global_queue_backlog_identity_repair_preview(
        root,
        generated_at="2026-06-04T17:51:00Z",
    )

    assert result["schema_id"].endswith(".write_result.v0_1")
    assert result["verdict"] == "GLOBAL_QUEUE_REPAIR_PREVIEW_ROWS_READY_MUTATION_GATE_REQUIRED"
    for key in [
        "preview_path",
        "report_path",
        "context_graph_delta_path",
        "operator_receipt_path",
    ]:
        assert (root / result[key]).is_file()
    written = json.loads((root / result["preview_path"]).read_text(encoding="utf-8"))
    assert written["request_files_mutated"] is False
    assert written["accepted_state_claimed"] is False
    report_text = (root / result["report_path"]).read_text(encoding="utf-8")
    assert "Global Queue Backlog Identity Repair Preview" in report_text


def test_metadata_identity_reissue_builds_blocked_worksheet_without_mutation(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _write_work_request(
        root,
        "dirty_missing_domain.json",
        {
            "request_id": "codex_req_dirty_missing_domain",
            "lane_id": "audit_lane",
            "domain_id": "",
            "role_id": "role.receipt_integrity_proof_graph_steward",
            "work_class": "legacy_queue_backlog",
            "request_kind": "legacy_queue_backlog",
            "working_capsule_identity": None,
        },
    )
    _write_work_request(
        root,
        "context_gate_blocked.json",
        {
            "request_id": "codex_req_context_gate_blocked",
            "status": "CODEX_QUEUE_RUNNER_BLOCKED_CONTEXT_GATE",
            "lane_id": "context_lane",
            "domain_id": "domain.agent_communication_systems",
            "role_id": "role.context_cartographer",
            "work_class": "domain_weaver_agent_comms_queue_runner_pickup_proof",
            "request_kind": "agent_context_gate_blocked",
            "context_gate": {
                "finding": "no_matching_active_context_mount_for_lane",
                "context_active_resolver": {
                    "blockers": ["no_matching_active_context_mount_for_lane"]
                },
            },
            "working_capsule_identity": None,
        },
    )

    worksheet = build_queue_request_metadata_identity_reissue(
        root,
        generated_at="2026-06-04T17:55:00Z",
    )

    assert worksheet["schema_id"] == QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_SCHEMA_ID
    assert worksheet["verdict"] == "QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_ASSIGNMENT_BLOCKED"
    assert worksheet["request_files_mutated"] is False
    assert worksheet["replacement_requests_written"] == 0
    assert worksheet["codex_queue_run_started"] is False
    assert worksheet["accepted_state_claimed"] is False
    assert worksheet["summary"]["worksheet_row_count"] == 1
    assert worksheet["summary"]["candidate_reissue_allowed_now_count"] == 0
    assert worksheet["summary"]["excluded_non_metadata_repair_row_count"] == 1
    row = worksheet["worksheet_rows"][0]
    assert row["source_request_id"] == "codex_req_dirty_missing_domain"
    assert row["domain_assignment_status"] == "requires_domain_steward_assignment"
    assert row["capsule_identity_status"] == "requires_unique_folder_local_mount_or_agent_mount_binding"
    assert row["candidate_reissue_allowed_now"] is False
    assert row["would_write_new_request"] is False
    assert row["would_mutate_source_request"] is False
    assert worksheet["candidate_context_graph_deltas"]["accepted_state_claimed"] is False


def test_write_metadata_identity_reissue_artifacts_and_receipt(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _write_work_request(
        root,
        "dirty_missing_domain.json",
        {
            "request_id": "codex_req_dirty_missing_domain",
            "lane_id": "audit_lane",
            "domain_id": "",
            "role_id": "role.receipt_integrity_proof_graph_steward",
            "work_class": "legacy_queue_backlog",
            "request_kind": "legacy_queue_backlog",
            "working_capsule_identity": None,
        },
    )
    write_global_queue_backlog_identity_repair_preview(
        root,
        generated_at="2026-06-04T17:54:00Z",
        write_receipt=False,
    )

    result = write_queue_request_metadata_identity_reissue(
        root,
        generated_at="2026-06-04T17:56:00Z",
    )

    assert result["schema_id"].endswith(".write_result.v0_1")
    assert result["verdict"] == "QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_ASSIGNMENT_BLOCKED"
    assert result["request_files_mutated"] is False
    assert result["replacement_requests_written"] == 0
    assert result["codex_queue_run_started"] is False
    for key in [
        "worksheet_path",
        "report_path",
        "context_graph_delta_path",
        "operator_receipt_path",
    ]:
        assert (root / result[key]).is_file()
    written = json.loads((root / result["worksheet_path"]).read_text(encoding="utf-8"))
    assert written["source_preview_is_latest_file"] is True
    assert written["summary"]["worksheet_row_count"] == 1
    assert written["summary"]["replacement_requests_written"] == 0
    report_text = (root / result["report_path"]).read_text(encoding="utf-8")
    assert "Queue Request Metadata Identity Reissue" in report_text


def test_metadata_identity_assignment_splits_existing_mounts_from_mount_generation(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _mount_manifest(
        root,
        "role_nemesis__domain_confidence_drift_review",
        domain_id="domain.confidence_drift_review",
        role_id="role.nemesis",
    )
    _mount_manifest(
        root,
        "role_context_cartographer__domain_agent_communication_systems",
        domain_id="domain.agent_communication_systems",
        role_id="role.context_cartographer",
    )
    _write_work_request(
        root,
        "desktop_rescue.json",
        {
            "request_id": "codex_req_urgent_desktop_rescue",
            "lane_id": "maintenance_lane",
            "domain_id": "",
            "role_id": "",
            "work_class": "desktop_rescue_execution",
            "request_kind": "desktop_rescue_execution_after_codex_gemini_webgpu_freeze",
            "working_capsule_identity": None,
        },
    )
    _write_work_request(
        root,
        "nemesis_incident.json",
        {
            "request_id": "codex_req_context_capsule_identity_incident",
            "lane_id": "implementation_lane",
            "domain_id": "",
            "role_id": "",
            "work_class": "incident_nemesis_review",
            "request_kind": "read_only_nemesis",
            "working_capsule_identity": None,
        },
    )
    _write_work_request(
        root,
        "context_cartographer.json",
        {
            "request_id": "codex_req_context_cartographer_agent_comms",
            "lane_id": "context_lane",
            "domain_id": "",
            "role_id": "role.context_cartographer",
            "work_class": "domain_weaver_agent_comms_queue_runner_pickup_proof",
            "request_kind": "agent_comms_pickup",
            "working_capsule_identity": None,
        },
    )
    _write_work_request(
        root,
        "receipt_graph.json",
        {
            "request_id": "codex_req_domain_weaver_receipt_graph",
            "lane_id": "audit_lane",
            "domain_id": "",
            "role_id": "role.receipt_integrity_proof_graph_steward",
            "work_class": "receipt_integrity_proof_graph",
            "request_kind": "receipt_integrity",
            "working_capsule_identity": None,
        },
    )
    write_queue_request_metadata_identity_reissue(
        root,
        generated_at="2026-06-04T17:57:00Z",
        write_receipt=False,
    )

    assignment = build_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T17:58:00Z",
    )

    assert assignment["schema_id"] == QUEUE_METADATA_IDENTITY_ASSIGNMENT_SCHEMA_ID
    assert assignment["verdict"] == "QUEUE_METADATA_IDENTITY_ASSIGNMENT_PARTIAL_APPLY_REVIEW_READY"
    assert assignment["summary"]["assignment_row_count"] == 4
    assert assignment["summary"]["existing_mount_assignment_ready_count"] == 2
    assert assignment["summary"]["apply_review_ready_count"] == 2
    assert assignment["summary"]["source_safety_blocked_count"] == 0
    assert assignment["summary"]["generated_mount_required_count"] == 1
    assert assignment["summary"]["supersede_or_quarantine_recommended_count"] == 1
    rows = {row["source_request_id"]: row for row in assignment["assignment_rows"]}
    assert rows["codex_req_context_capsule_identity_incident"][
        "candidate_reissue_apply_review_ready"
    ] is True
    assert rows["codex_req_context_cartographer_agent_comms"]["assigned_identity"][
        "selected_mount_id"
    ] == "role_context_cartographer__domain_agent_communication_systems"
    assert rows["codex_req_domain_weaver_receipt_graph"][
        "assignment_disposition"
    ] == "generated_mount_required"
    assert rows["codex_req_urgent_desktop_rescue"][
        "assignment_disposition"
    ] == "supersede_or_quarantine_recommended"
    assert assignment["request_files_mutated"] is False
    assert assignment["replacement_requests_written"] == 0
    assert assignment["mounts_created"] == 0
    assert assignment["candidate_context_graph_deltas"]["accepted_state_claimed"] is False


def test_stale_non_domain_queue_quarantine_settlement_clears_external_blocker(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    source_path = _write_work_request(
        root,
        "desktop_rescue.json",
        {
            "request_id": "codex_req_urgent_desktop_rescue",
            "lane_id": "maintenance_lane",
            "domain_id": "",
            "role_id": "",
            "work_class": "desktop_rescue_execution",
            "request_kind": "desktop_rescue_execution_after_codex_gemini_webgpu_freeze",
            "working_capsule_identity": None,
        },
    )
    source_before = json.loads(source_path.read_text(encoding="utf-8"))
    write_queue_request_metadata_identity_reissue(
        root,
        generated_at="2026-06-04T18:10:00Z",
        write_receipt=False,
    )
    initial_assignment = write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T18:11:00Z",
        write_receipt=False,
    )
    assert initial_assignment["verdict"] == "QUEUE_METADATA_IDENTITY_ASSIGNMENT_QUARANTINE_REVIEW_REQUIRED"
    assert initial_assignment["supersede_or_quarantine_recommended_count"] == 1

    blocked = write_stale_non_domain_queue_quarantine_settlement(
        root,
        confirmation="proceed",
        write_receipt=False,
    )
    assert blocked["ok"] is False
    assert blocked["verdict"] == "STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_CONFIRMATION_REQUIRED"
    assert blocked["candidate_quarantine_settlement_written"] is False

    settlement = build_stale_non_domain_queue_quarantine_settlement(
        root,
        generated_at="2026-06-04T18:12:00Z",
    )
    assert settlement["schema_id"] == STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_SCHEMA_ID
    assert settlement["verdict"] == "STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_READY"
    assert settlement["summary"]["settlement_row_count"] == 1
    assert settlement["settlement_rows"][0]["source_hash_matches_assignment"] is True

    result = write_stale_non_domain_queue_quarantine_settlement(
        root,
        generated_at="2026-06-04T18:13:00Z",
        confirmation=STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_CONFIRMATION,
        write_receipt=False,
    )
    assert result["ok"] is True
    assert result["verdict"] == "STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_WRITTEN"
    assert result["candidate_quarantine_settlement_written"] is True
    assert result["source_request_files_mutated"] is False
    assert result["codex_queue_run_started"] is False
    assert json.loads(source_path.read_text(encoding="utf-8")) == source_before
    written = json.loads((root / result["settlement_path"]).read_text(encoding="utf-8"))
    assert written["verdict"] == "STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_WRITTEN"

    refreshed_assignment = write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T18:14:00Z",
        write_receipt=False,
    )
    assert refreshed_assignment["verdict"] == "QUEUE_METADATA_IDENTITY_ASSIGNMENT_NO_ROWS_REQUIRED"
    assert refreshed_assignment["supersede_or_quarantine_recommended_count"] == 0
    assignment = json.loads((root / refreshed_assignment["assignment_path"]).read_text(encoding="utf-8"))
    row = assignment["assignment_rows"][0]
    assert row["assignment_disposition"] == "external_quarantine_settled"
    assert row["candidate_quarantine_already_satisfied"] is True
    assert row["would_start_worker"] is False


def test_write_metadata_identity_assignment_artifacts_and_receipt(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _mount_manifest(
        root,
        "role_context_cartographer__domain_agent_communication_systems",
        domain_id="domain.agent_communication_systems",
        role_id="role.context_cartographer",
    )
    _write_work_request(
        root,
        "context_cartographer.json",
        {
            "request_id": "codex_req_context_cartographer_agent_comms",
            "lane_id": "context_lane",
            "domain_id": "",
            "role_id": "role.context_cartographer",
            "work_class": "domain_weaver_agent_comms_queue_runner_pickup_proof",
            "request_kind": "agent_comms_pickup",
            "working_capsule_identity": None,
        },
    )
    write_queue_request_metadata_identity_reissue(
        root,
        generated_at="2026-06-04T17:57:00Z",
        write_receipt=False,
    )

    result = write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T17:58:00Z",
    )

    assert result["schema_id"].endswith(".write_result.v0_1")
    assert result["verdict"] == "QUEUE_METADATA_IDENTITY_ASSIGNMENT_APPLY_REVIEW_READY"
    assert result["existing_mount_assignment_ready_count"] == 1
    assert result["apply_review_ready_count"] == 1
    assert result["source_safety_blocked_count"] == 0
    assert result["request_files_mutated"] is False
    assert result["replacement_requests_written"] == 0
    assert result["mounts_created"] == 0
    for key in [
        "assignment_path",
        "report_path",
        "context_graph_delta_path",
        "operator_receipt_path",
    ]:
        assert (root / result[key]).is_file()
    written = json.loads((root / result["assignment_path"]).read_text(encoding="utf-8"))
    assert written["source_reissue_is_latest_file"] is True
    assert written["summary"]["existing_mount_assignment_ready_count"] == 1
    report_text = (root / result["report_path"]).read_text(encoding="utf-8")
    assert "Queue Metadata Identity Assignment" in report_text


def test_metadata_identity_reissue_apply_review_blocks_context_gate_source(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _mount_manifest(
        root,
        "role_context_cartographer__domain_agent_communication_systems",
        domain_id="domain.agent_communication_systems",
        role_id="role.context_cartographer",
    )
    source_path = _write_work_request(
        root,
        "context_cartographer.json",
        {
            "request_id": "codex_req_context_cartographer_agent_comms",
            "status": "CODEX_QUEUE_RUNNER_BLOCKED_CONTEXT_GATE",
            "lane_id": "context_lane",
            "domain_id": "",
            "role_id": "role.context_cartographer",
            "agent_role_id": "role.context_cartographer",
            "work_class": "domain_weaver_agent_comms_queue_runner_pickup_proof",
            "request_kind": "agent_comms_pickup",
            "context_gate": {"finding": "stale_context_gate"},
            "working_capsule_identity": None,
        },
    )
    source_before = json.loads(source_path.read_text(encoding="utf-8"))
    write_queue_request_metadata_identity_reissue(
        root,
        generated_at="2026-06-04T17:57:00Z",
        write_receipt=False,
    )
    write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T17:58:00Z",
        write_receipt=False,
    )

    assignment = build_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T17:58:00Z",
    )
    rows = {row["source_request_id"]: row for row in assignment["assignment_rows"]}
    assert rows["codex_req_context_cartographer_agent_comms"][
        "candidate_reissue_apply_review_ready"
    ] is False
    assert rows["codex_req_context_cartographer_agent_comms"]["source_safety"][
        "source_context_gate_present"
    ] is True
    assert rows["codex_req_context_cartographer_agent_comms"]["source_safety"][
        "safety_blockers"
    ][0]["code"] == "source_context_gate_requires_dedicated_reissue_packet"

    review = build_queue_metadata_identity_reissue_apply_review(
        root,
        generated_at="2026-06-04T17:59:00Z",
    )

    assert review["schema_id"] == QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_SCHEMA_ID
    assert review["verdict"] == "QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_NO_READY_ROWS"
    assert review["summary"]["apply_review_row_count"] == 0
    assert review["replacement_request_files_written"] == 0
    assert review["request_files_mutated"] is False
    assert review["excluded_assignment_rows"][0]["next_packet"] == (
        "PCKT-DOMAIN-WEAVER-SOURCE-SAFETY-BLOCKED-METADATA-REISSUE-REVIEW-V0_1"
    )
    assert json.loads(source_path.read_text(encoding="utf-8")) == source_before
    assert review["candidate_context_graph_deltas"]["accepted_state_claimed"] is False


def test_metadata_source_safety_review_separates_context_gate_and_stale_lifecycle(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _mount_manifest(
        root,
        "role_nemesis__domain_confidence_drift_review",
        domain_id="domain.confidence_drift_review",
        role_id="role.nemesis",
    )
    _mount_manifest(
        root,
        "role_context_cartographer__domain_agent_communication_systems",
        domain_id="domain.agent_communication_systems",
        role_id="role.context_cartographer",
    )
    _write_work_request(
        root,
        "nemesis_stale.json",
        {
            "request_id": "codex_req_nemesis_stale_context_capsule_identity_incident",
            "status": "QUEUED_FOR_CODEX_CARRIER",
            "created_at": "2026-06-01T10:00:00+00:00",
            "updated_at": "2026-06-01T10:00:00+00:00",
            "lane_id": "implementation_lane",
            "domain_id": "",
            "role_id": "",
            "work_class": "incident_nemesis_review",
            "request_kind": "read_only_nemesis",
            "working_capsule_identity": None,
        },
    )
    _write_work_request(
        root,
        "context_cartographer_gate.json",
        {
            "request_id": "codex_req_context_cartographer_agent_comms_gate",
            "status": "CODEX_QUEUE_RUNNER_BLOCKED_CONTEXT_GATE",
            "lane_id": "context_lane",
            "domain_id": "",
            "role_id": "role.context_cartographer",
            "agent_role_id": "role.context_cartographer",
            "work_class": "domain_weaver_agent_comms_queue_runner_pickup_proof",
            "request_kind": "agent_comms_pickup",
            "context_gate": {"finding": "target_request_domain_missing"},
            "working_capsule_identity": None,
        },
    )
    write_global_queue_backlog_identity_repair_preview(
        root,
        generated_at="2026-06-04T17:54:00Z",
        write_receipt=False,
    )
    write_queue_request_metadata_identity_reissue(
        root,
        generated_at="2026-06-04T17:55:00Z",
        write_receipt=False,
    )
    write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T17:56:00Z",
        write_receipt=False,
    )

    review = build_queue_metadata_source_safety_review(
        root,
        generated_at="2026-06-04T17:57:00Z",
    )

    assert review["schema_id"] == QUEUE_METADATA_SOURCE_SAFETY_REVIEW_SCHEMA_ID
    assert review["verdict"] == "QUEUE_METADATA_SOURCE_SAFETY_REVIEW_BLOCKERS_ACTIVE"
    assert review["summary"]["source_safety_review_row_count"] == 2
    assert review["summary"]["context_gate_blocked_count"] == 1
    assert review["summary"]["stale_lifecycle_blocked_count"] == 1
    assert review["summary"]["terminal_lifecycle_blocked_count"] == 0
    assert review["summary"]["apply_review_rows_unblocked"] == 0
    assert review["replacement_request_files_written"] == 0
    assert review["request_files_mutated"] is False
    assert review["codex_queue_run_started"] is False
    assert review["candidate_context_graph_deltas"]["accepted_state_claimed"] is False
    rows = {row["source_request_id"]: row for row in review["source_safety_review_rows"]}
    assert rows["codex_req_context_cartographer_agent_comms_gate"]["required_packets"] == [
        "PCKT-DOMAIN-WEAVER-CONTEXT-GATE-BLOCKED-REQUEST-REISSUE-V0_1"
    ]
    assert rows[
        "codex_req_nemesis_stale_context_capsule_identity_incident"
    ]["required_packets"] == [
        "PCKT-DOMAIN-WEAVER-STALE-WAITING-REQUEST-RECONCILIATION-V0_2"
    ]
    assert review["next_packet"] == (
        "PCKT-DOMAIN-WEAVER-CONTEXT-GATE-BLOCKED-REQUEST-REISSUE-V0_1"
    )


def test_write_metadata_source_safety_review_artifacts_and_receipt(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _mount_manifest(
        root,
        "role_context_cartographer__domain_agent_communication_systems",
        domain_id="domain.agent_communication_systems",
        role_id="role.context_cartographer",
    )
    _write_work_request(
        root,
        "context_cartographer_gate.json",
        {
            "request_id": "codex_req_context_cartographer_agent_comms_gate",
            "status": "CODEX_QUEUE_RUNNER_BLOCKED_CONTEXT_GATE",
            "lane_id": "context_lane",
            "domain_id": "",
            "role_id": "role.context_cartographer",
            "agent_role_id": "role.context_cartographer",
            "work_class": "domain_weaver_agent_comms_queue_runner_pickup_proof",
            "request_kind": "agent_comms_pickup",
            "context_gate": {"finding": "target_request_domain_missing"},
            "working_capsule_identity": None,
        },
    )
    write_queue_request_metadata_identity_reissue(
        root,
        generated_at="2026-06-04T17:55:00Z",
        write_receipt=False,
    )
    write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T17:56:00Z",
        write_receipt=False,
    )

    result = write_queue_metadata_source_safety_review(
        root,
        generated_at="2026-06-04T17:57:00Z",
    )

    assert result["schema_id"].endswith(".write_result.v0_1")
    assert result["verdict"] == "QUEUE_METADATA_SOURCE_SAFETY_REVIEW_BLOCKERS_ACTIVE"
    assert result["source_safety_review_row_count"] == 1
    assert result["context_gate_blocked_count"] == 1
    assert result["replacement_request_files_written"] == 0
    assert result["source_request_files_mutated"] is False
    assert result["codex_queue_run_started"] is False
    for key in [
        "review_path",
        "report_path",
        "context_graph_delta_path",
        "operator_receipt_path",
    ]:
        assert (root / result[key]).is_file()
    written = json.loads((root / result["review_path"]).read_text(encoding="utf-8"))
    assert written["summary"]["apply_review_rows_unblocked"] == 0
    report_text = (root / result["report_path"]).read_text(encoding="utf-8")
    assert "Queue Metadata Source-Safety Review" in report_text


def test_context_gate_blocked_request_reissue_builds_candidate_body_without_mutation(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _mount_manifest(
        root,
        "role_context_cartographer__domain_agent_communication_systems",
        domain_id="domain.agent_communication_systems",
        role_id="role.context_cartographer",
    )
    source_path = _write_work_request(
        root,
        "context_cartographer_gate.json",
        {
            "request_id": "codex_req_context_cartographer_agent_comms_gate",
            "status": "CODEX_QUEUE_RUNNER_BLOCKED_CONTEXT_GATE",
            "lane_id": "context_lane",
            "domain_id": "",
            "role_id": "role.context_cartographer",
            "agent_role_id": "role.context_cartographer",
            "work_class": "domain_weaver_agent_comms_queue_runner_pickup_proof",
            "request_kind": "agent_comms_pickup",
            "context_gate": {"finding": "target_request_domain_missing"},
            "working_capsule_identity": None,
        },
    )
    source_before = json.loads(source_path.read_text(encoding="utf-8"))
    write_queue_request_metadata_identity_reissue(
        root,
        generated_at="2026-06-04T17:55:00Z",
        write_receipt=False,
    )
    write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T17:56:00Z",
        write_receipt=False,
    )
    write_queue_metadata_source_safety_review(
        root,
        generated_at="2026-06-04T17:57:00Z",
        write_receipt=False,
    )

    review = build_context_gate_blocked_request_reissue(
        root,
        generated_at="2026-06-04T17:58:00Z",
    )

    assert review["schema_id"] == CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_SCHEMA_ID
    assert review["verdict"] == "CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_CANDIDATE_BODIES_READY"
    assert review["summary"]["context_gate_reissue_row_count"] == 1
    assert review["summary"]["candidate_body_ready_count"] == 1
    assert review["replacement_request_files_written"] == 0
    assert review["request_files_mutated"] is False
    assert review["codex_queue_run_started"] is False
    row = review["context_gate_reissue_rows"][0]
    body = row["candidate_replacement_body"]
    assert row["candidate_body_ready"] is True
    assert body["domain_id"] == "domain.agent_communication_systems"
    assert body["agent_role_id"] == "role.context_cartographer"
    assert body["selected_mount_id"] == "role_context_cartographer__domain_agent_communication_systems"
    assert body["active_context_ready"] is True
    assert body["working_capsule_identity"]
    assert "context_gate" not in body
    assert body["risk_level"] == "critical"
    assert body["route_metadata"]["explicit_fields"]["risk_level"] is True
    assert body["requested_model"] == "gpt-5.5"
    assert body["source_context_gate"]["finding"] == "target_request_domain_missing"
    assert body["general_queue_processing_allowed"] is False
    assert json.loads(source_path.read_text(encoding="utf-8")) == source_before
    assert review["candidate_context_graph_deltas"]["accepted_state_claimed"] is False


def test_write_context_gate_blocked_request_reissue_artifacts_and_body_files(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _mount_manifest(
        root,
        "role_context_cartographer__domain_agent_communication_systems",
        domain_id="domain.agent_communication_systems",
        role_id="role.context_cartographer",
    )
    _write_work_request(
        root,
        "context_cartographer_gate.json",
        {
            "request_id": "codex_req_context_cartographer_agent_comms_gate",
            "status": "CODEX_QUEUE_RUNNER_BLOCKED_CONTEXT_GATE",
            "lane_id": "context_lane",
            "domain_id": "",
            "role_id": "role.context_cartographer",
            "agent_role_id": "role.context_cartographer",
            "work_class": "domain_weaver_agent_comms_queue_runner_pickup_proof",
            "request_kind": "agent_comms_pickup",
            "context_gate": {"finding": "target_request_domain_missing"},
            "working_capsule_identity": None,
        },
    )
    write_queue_request_metadata_identity_reissue(
        root,
        generated_at="2026-06-04T17:55:00Z",
        write_receipt=False,
    )
    write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T17:56:00Z",
        write_receipt=False,
    )
    write_queue_metadata_source_safety_review(
        root,
        generated_at="2026-06-04T17:57:00Z",
        write_receipt=False,
    )

    result = write_context_gate_blocked_request_reissue(
        root,
        generated_at="2026-06-04T17:58:00Z",
    )

    assert result["schema_id"].endswith(".write_result.v0_1")
    assert result["verdict"] == "CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_CANDIDATE_BODIES_READY"
    assert result["context_gate_reissue_row_count"] == 1
    assert result["candidate_body_files_written"] == 1
    assert result["replacement_request_files_written"] == 0
    assert result["source_request_files_mutated"] is False
    assert result["codex_queue_run_started"] is False
    for key in [
        "review_path",
        "report_path",
        "context_graph_delta_path",
        "operator_receipt_path",
    ]:
        assert (root / result[key]).is_file()
    written = json.loads((root / result["review_path"]).read_text(encoding="utf-8"))
    body_path = root / written["context_gate_reissue_rows"][0]["candidate_replacement_body_path"]
    assert body_path.is_file()
    body = json.loads(body_path.read_text(encoding="utf-8"))
    assert body["domain_id"] == "domain.agent_communication_systems"
    assert body["context_gate_reissue"]["apply_review_only"] is True
    assert body["risk_level"] == "critical"
    assert body["route_metadata"]["explicit_fields"]["risk_level"] is True
    report_text = (root / result["report_path"]).read_text(encoding="utf-8")
    assert "Context-Gate Blocked Request Reissue" in report_text


def test_context_gate_reissue_apply_requires_explicit_confirmation(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _mount_manifest(
        root,
        "role_context_cartographer__domain_agent_communication_systems",
        domain_id="domain.agent_communication_systems",
        role_id="role.context_cartographer",
    )
    _write_work_request(
        root,
        "context_cartographer_gate.json",
        {
            "request_id": "codex_req_context_cartographer_agent_comms_gate",
            "status": "CODEX_QUEUE_RUNNER_BLOCKED_CONTEXT_GATE",
            "lane_id": "context_lane",
            "domain_id": "",
            "role_id": "role.context_cartographer",
            "agent_role_id": "role.context_cartographer",
            "work_class": "domain_weaver_agent_comms_queue_runner_pickup_proof",
            "request_kind": "agent_comms_pickup",
            "context_gate": {"finding": "target_request_domain_missing"},
            "working_capsule_identity": None,
        },
    )
    write_queue_request_metadata_identity_reissue(root, write_receipt=False)
    write_queue_metadata_identity_assignment(root, write_receipt=False)
    write_queue_metadata_source_safety_review(root, write_receipt=False)
    write_context_gate_blocked_request_reissue(root, write_receipt=False)

    result = apply_context_gate_blocked_request_reissue(
        root,
        confirmation="proceed",
    )

    assert result["ok"] is False
    assert result["result"] == "CONTEXT_GATE_REISSUE_APPLY_BLOCKED_CONFIRMATION_REQUIRED"
    assert result["replacement_request_files_written"] == 0
    review = json.loads(
        (
            root
            / "ION/05_context/current/domain_weaver/queue_governance/DOMAIN_WEAVER_CONTEXT_GATE_BLOCKED_REQUEST_REISSUE.latest.json"
        ).read_text(encoding="utf-8")
    )
    target = root / review["context_gate_reissue_rows"][0]["candidate_replacement_request_path"]
    assert not target.exists()


def test_context_gate_reissue_apply_writes_exact_request_without_source_mutation(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _mount_manifest(
        root,
        "role_context_cartographer__domain_agent_communication_systems",
        domain_id="domain.agent_communication_systems",
        role_id="role.context_cartographer",
    )
    source_path = _write_work_request(
        root,
        "context_cartographer_gate.json",
        {
            "request_id": "codex_req_context_cartographer_agent_comms_gate",
            "status": "CODEX_QUEUE_RUNNER_BLOCKED_CONTEXT_GATE",
            "lane_id": "context_lane",
            "domain_id": "",
            "role_id": "role.context_cartographer",
            "agent_role_id": "role.context_cartographer",
            "work_class": "domain_weaver_agent_comms_queue_runner_pickup_proof",
            "request_kind": "agent_comms_pickup",
            "context_gate": {"finding": "target_request_domain_missing"},
            "working_capsule_identity": None,
        },
    )
    source_before = json.loads(source_path.read_text(encoding="utf-8"))
    write_queue_request_metadata_identity_reissue(root, write_receipt=False)
    write_queue_metadata_identity_assignment(root, write_receipt=False)
    write_queue_metadata_source_safety_review(root, write_receipt=False)
    write_context_gate_blocked_request_reissue(root, write_receipt=False)

    result = apply_context_gate_blocked_request_reissue(
        root,
        confirmation=CONTEXT_GATE_REISSUE_APPLY_CONFIRMATION,
    )

    assert result["ok"] is True
    assert result["result"] == "CONTEXT_GATE_REISSUE_APPLY_WRITTEN"
    assert result["replacement_request_files_written"] == 1
    assert result["source_request_files_mutated"] is False
    assert result["codex_queue_run_started"] is False
    assert json.loads(source_path.read_text(encoding="utf-8")) == source_before
    written_path = root / result["writes"][0]["candidate_replacement_request_path"]
    assert written_path.is_file()
    written = json.loads(written_path.read_text(encoding="utf-8"))
    assert written["domain_id"] == "domain.agent_communication_systems"
    assert written["status"] == "QUEUED_FOR_CODEX_CARRIER"
    assert "context_gate" not in written

    refreshed_assignment = write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T18:01:00Z",
        write_receipt=False,
    )
    assert refreshed_assignment["source_safety_blocked_count"] == 0
    assignment = json.loads((root / refreshed_assignment["assignment_path"]).read_text(encoding="utf-8"))
    assert assignment["assignment_rows"][0]["source_safety"]["apply_source_safe"] is True
    assert assignment["assignment_rows"][0]["candidate_reissue_apply_review_ready"] is False
    assert assignment["assignment_rows"][0]["candidate_reissue_already_satisfied"] is True
    assert (
        assignment["assignment_rows"][0]["source_safety"][
            "source_context_gate_reissued_for_metadata_reissue"
        ]
        is True
    )
    refreshed_source_safety = write_queue_metadata_source_safety_review(
        root,
        generated_at="2026-06-04T18:02:00Z",
        write_receipt=False,
    )
    assert refreshed_source_safety["verdict"] == "QUEUE_METADATA_SOURCE_SAFETY_REVIEW_NO_BLOCKERS"
    assert refreshed_source_safety["source_safety_review_row_count"] == 0


def test_stale_waiting_reconciliation_review_builds_decision_matrix_without_mutation(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _mount_manifest(
        root,
        "role_nemesis__domain_confidence_drift_review",
        domain_id="domain.confidence_drift_review",
        role_id="role.nemesis",
    )
    source_path = _write_work_request(
        root,
        "nemesis_stale.json",
        {
            "request_id": "codex_req_nemesis_stale_context_capsule_identity_incident",
            "status": "QUEUED_FOR_CODEX_CARRIER",
            "created_at": "2026-06-01T10:00:00+00:00",
            "updated_at": "2026-06-01T10:00:00+00:00",
            "lane_id": "implementation_lane",
            "domain_id": "",
            "role_id": "",
            "work_class": "incident_nemesis_review",
            "request_kind": "read_only_nemesis",
            "working_capsule_identity": None,
        },
    )
    source_before = json.loads(source_path.read_text(encoding="utf-8"))
    write_global_queue_backlog_identity_repair_preview(
        root,
        generated_at="2026-06-04T17:54:00Z",
        write_receipt=False,
    )
    write_queue_request_metadata_identity_reissue(
        root,
        generated_at="2026-06-04T17:55:00Z",
        write_receipt=False,
    )
    write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T17:56:00Z",
        write_receipt=False,
    )
    write_queue_metadata_source_safety_review(
        root,
        generated_at="2026-06-04T17:57:00Z",
        write_receipt=False,
    )

    review = build_stale_waiting_reconciliation_review(
        root,
        generated_at="2026-06-04T17:58:00Z",
    )

    assert review["schema_id"] == STALE_WAITING_RECONCILIATION_REVIEW_SCHEMA_ID
    assert review["verdict"] == "STALE_WAITING_RECONCILIATION_REVIEW_DECISION_REQUIRED"
    assert review["summary"]["stale_reconciliation_row_count"] == 1
    assert review["summary"]["decision_required_count"] == 1
    assert review["lifecycle_ledger_mutated"] is False
    assert review["request_files_mutated"] is False
    assert review["codex_queue_run_started"] is False
    row = review["stale_reconciliation_rows"][0]
    assert row["decision_ready"] is False
    assert row["source_status"] == "QUEUED_FOR_CODEX_CARRIER"
    assert row["lifecycle_preview_row"]["repair_class"] == "stale_waiting_reconciliation_required"
    assert len(row["candidate_reconciliation_choices"]) == 3
    assert json.loads(source_path.read_text(encoding="utf-8")) == source_before
    assert review["candidate_context_graph_deltas"]["accepted_state_claimed"] is False


def test_write_stale_waiting_reconciliation_review_artifacts_and_receipt(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _mount_manifest(
        root,
        "role_nemesis__domain_confidence_drift_review",
        domain_id="domain.confidence_drift_review",
        role_id="role.nemesis",
    )
    _write_work_request(
        root,
        "nemesis_stale.json",
        {
            "request_id": "codex_req_nemesis_stale_context_capsule_identity_incident",
            "status": "QUEUED_FOR_CODEX_CARRIER",
            "created_at": "2026-06-01T10:00:00+00:00",
            "updated_at": "2026-06-01T10:00:00+00:00",
            "lane_id": "implementation_lane",
            "domain_id": "",
            "role_id": "",
            "work_class": "incident_nemesis_review",
            "request_kind": "read_only_nemesis",
            "working_capsule_identity": None,
        },
    )
    write_global_queue_backlog_identity_repair_preview(
        root,
        generated_at="2026-06-04T17:54:00Z",
        write_receipt=False,
    )
    write_queue_request_metadata_identity_reissue(
        root,
        generated_at="2026-06-04T17:55:00Z",
        write_receipt=False,
    )
    write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T17:56:00Z",
        write_receipt=False,
    )
    write_queue_metadata_source_safety_review(
        root,
        generated_at="2026-06-04T17:57:00Z",
        write_receipt=False,
    )

    result = write_stale_waiting_reconciliation_review(
        root,
        generated_at="2026-06-04T17:58:00Z",
    )

    assert result["schema_id"].endswith(".write_result.v0_1")
    assert result["verdict"] == "STALE_WAITING_RECONCILIATION_REVIEW_DECISION_REQUIRED"
    assert result["stale_reconciliation_row_count"] == 1
    assert result["decision_required_count"] == 1
    assert result["lifecycle_ledger_mutated"] is False
    assert result["request_files_mutated"] is False
    assert result["codex_queue_run_started"] is False
    for key in [
        "review_path",
        "report_path",
        "context_graph_delta_path",
        "operator_receipt_path",
    ]:
        assert (root / result[key]).is_file()
    written = json.loads((root / result["review_path"]).read_text(encoding="utf-8"))
    assert written["summary"]["decision_required_count"] == 1
    report_text = (root / result["report_path"]).read_text(encoding="utf-8")
    assert "Stale Waiting Reconciliation Review" in report_text


def test_stale_waiting_reconciliation_settlement_requires_confirmation(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)

    result = write_stale_waiting_reconciliation_settlement(
        root,
        confirmation="proceed",
        write_receipt=False,
    )

    assert result["ok"] is False
    assert result["verdict"] == "STALE_WAITING_RECONCILIATION_SETTLEMENT_CONFIRMATION_REQUIRED"
    assert result["candidate_lifecycle_settlement_written"] is False
    assert result["source_request_files_mutated"] is False
    assert result["codex_queue_run_started"] is False
    assert not (
        root
        / "ION/05_context/current/domain_weaver/queue_governance/DOMAIN_WEAVER_STALE_WAITING_RECONCILIATION_SETTLEMENT.latest.json"
    ).exists()


def test_stale_waiting_reconciliation_settlement_writes_hash_bound_candidate_ledger(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _mount_manifest(
        root,
        "role_nemesis__domain_confidence_drift_review",
        domain_id="domain.confidence_drift_review",
        role_id="role.nemesis",
    )
    source_path = _write_work_request(
        root,
        "nemesis_stale.json",
        {
            "request_id": "codex_req_nemesis_stale_context_capsule_identity_incident",
            "status": "QUEUED_FOR_CODEX_CARRIER",
            "created_at": "2026-06-01T10:00:00+00:00",
            "updated_at": "2026-06-01T10:00:00+00:00",
            "lane_id": "implementation_lane",
            "domain_id": "",
            "role_id": "",
            "work_class": "incident_nemesis_review",
            "request_kind": "read_only_nemesis",
            "working_capsule_identity": None,
        },
    )
    source_before = json.loads(source_path.read_text(encoding="utf-8"))
    write_global_queue_backlog_identity_repair_preview(
        root,
        generated_at="2026-06-04T17:54:00Z",
        write_receipt=False,
    )
    write_queue_request_metadata_identity_reissue(
        root,
        generated_at="2026-06-04T17:55:00Z",
        write_receipt=False,
    )
    write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T17:56:00Z",
        write_receipt=False,
    )
    write_queue_metadata_source_safety_review(
        root,
        generated_at="2026-06-04T17:57:00Z",
        write_receipt=False,
    )
    write_stale_waiting_reconciliation_review(
        root,
        generated_at="2026-06-04T17:58:00Z",
        write_receipt=False,
    )

    settlement = build_stale_waiting_reconciliation_settlement(
        root,
        generated_at="2026-06-04T17:59:00Z",
    )

    assert settlement["schema_id"] == STALE_WAITING_RECONCILIATION_SETTLEMENT_SCHEMA_ID
    assert settlement["verdict"] == "STALE_WAITING_RECONCILIATION_SETTLEMENT_READY"
    assert settlement["summary"]["settlement_row_count"] == 1
    assert settlement["summary"]["settlement_ready_count"] == 1
    row = settlement["settlement_rows"][0]
    assert row["settlement_decision"] == "supersede_with_fresh_exact_request"
    assert row["source_hash_matches_review"] is True
    assert row["metadata_reissue_source_safety_may_clear"] is True

    result = write_stale_waiting_reconciliation_settlement(
        root,
        generated_at="2026-06-04T18:00:00Z",
        confirmation=STALE_WAITING_RECONCILIATION_SETTLEMENT_CONFIRMATION,
    )

    assert result["ok"] is True
    assert result["verdict"] == "STALE_WAITING_RECONCILIATION_SETTLEMENT_WRITTEN"
    assert result["candidate_lifecycle_settlement_written"] is True
    assert result["accepted_lifecycle_ledger_mutated"] is False
    assert result["source_request_files_mutated"] is False
    assert result["replacement_request_files_written"] == 0
    assert result["codex_queue_run_started"] is False
    assert json.loads(source_path.read_text(encoding="utf-8")) == source_before
    written = json.loads((root / result["settlement_path"]).read_text(encoding="utf-8"))
    assert written["verdict"] == "STALE_WAITING_RECONCILIATION_SETTLEMENT_WRITTEN"
    assert written["summary"]["candidate_lifecycle_settlement_written"] is True
    assert written["settlement_rows"][0]["source_request_sha256"] == row["source_request_sha256"]

    refreshed_assignment = write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T18:01:00Z",
        write_receipt=False,
    )
    assert refreshed_assignment["verdict"] == "QUEUE_METADATA_IDENTITY_ASSIGNMENT_APPLY_REVIEW_READY"
    assignment = json.loads((root / refreshed_assignment["assignment_path"]).read_text(encoding="utf-8"))
    assignment_row = assignment["assignment_rows"][0]
    assert assignment_row["source_safety"]["apply_source_safe"] is True
    assert assignment_row["source_safety"]["source_lifecycle_settled_for_metadata_reissue"] is True
    assert assignment_row["candidate_reissue_apply_review_ready"] is True

    refreshed_source_safety = write_queue_metadata_source_safety_review(
        root,
        generated_at="2026-06-04T18:02:00Z",
        write_receipt=False,
    )
    assert refreshed_source_safety["verdict"] == "QUEUE_METADATA_SOURCE_SAFETY_REVIEW_NO_BLOCKERS"
    assert refreshed_source_safety["source_safety_review_row_count"] == 0


def test_metadata_identity_reissue_apply_writes_exact_replacement_request(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _mount_manifest(
        root,
        "role_nemesis__domain_confidence_drift_review",
        domain_id="domain.confidence_drift_review",
        role_id="role.nemesis",
    )
    source_path = _write_work_request(
        root,
        "nemesis_stale.json",
        {
            "request_id": "codex_req_nemesis_stale_context_capsule_identity_incident",
            "status": "QUEUED_FOR_CODEX_CARRIER",
            "created_at": "2026-06-01T10:00:00+00:00",
            "updated_at": "2026-06-01T10:00:00+00:00",
            "lane_id": "implementation_lane",
            "domain_id": "",
            "role_id": "",
            "work_class": "incident_nemesis_review",
            "request_kind": "read_only_nemesis",
            "working_capsule_identity": None,
        },
    )
    source_before = json.loads(source_path.read_text(encoding="utf-8"))
    write_global_queue_backlog_identity_repair_preview(
        root,
        generated_at="2026-06-04T17:54:00Z",
        write_receipt=False,
    )
    write_queue_request_metadata_identity_reissue(
        root,
        generated_at="2026-06-04T17:55:00Z",
        write_receipt=False,
    )
    write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T17:56:00Z",
        write_receipt=False,
    )
    write_queue_metadata_source_safety_review(
        root,
        generated_at="2026-06-04T17:57:00Z",
        write_receipt=False,
    )
    write_stale_waiting_reconciliation_review(
        root,
        generated_at="2026-06-04T17:58:00Z",
        write_receipt=False,
    )
    write_stale_waiting_reconciliation_settlement(
        root,
        generated_at="2026-06-04T17:59:00Z",
        confirmation=STALE_WAITING_RECONCILIATION_SETTLEMENT_CONFIRMATION,
        write_receipt=False,
    )
    write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T18:00:00Z",
        write_receipt=False,
    )
    review_result = write_queue_metadata_identity_reissue_apply_review(
        root,
        generated_at="2026-06-04T18:01:00Z",
        write_receipt=False,
    )
    review = json.loads((root / review_result["review_path"]).read_text(encoding="utf-8"))
    target_path = root / review["apply_review_rows"][0]["candidate_replacement_request_path"]
    assert not target_path.exists()

    blocked = apply_queue_metadata_identity_reissue_apply_review(
        root,
        confirmation="proceed",
        write_receipt=False,
    )

    assert blocked["ok"] is False
    assert blocked["result"] == "QUEUE_METADATA_IDENTITY_REISSUE_APPLY_BLOCKED_CONFIRMATION_REQUIRED"
    assert blocked["replacement_request_files_written"] == 0
    assert not target_path.exists()

    result = apply_queue_metadata_identity_reissue_apply_review(
        root,
        confirmation=QUEUE_METADATA_IDENTITY_REISSUE_APPLY_CONFIRMATION,
        write_receipt=False,
    )

    assert result["ok"] is True
    assert result["result"] == "QUEUE_METADATA_IDENTITY_REISSUE_APPLY_WRITTEN"
    assert result["replacement_request_files_written"] == 1
    assert result["source_request_files_mutated"] is False
    assert result["codex_queue_run_started"] is False
    assert json.loads(source_path.read_text(encoding="utf-8")) == source_before
    assert target_path.is_file()
    written = json.loads(target_path.read_text(encoding="utf-8"))
    assert written["status"] == "QUEUED_FOR_CODEX_CARRIER"
    assert written["domain_id"] == "domain.confidence_drift_review"
    assert written["source_request_id"] == source_before["request_id"]
    assert (
        written["source_lifecycle_preview_metadata_label"][
            "lifecycle_preview_metadata_status"
        ]
        == "STALE_PREVIEW_NOT_CURRENT_ROUTE_IDENTITY"
    )
    assert written["source_lifecycle_preview_metadata_label"]["current_route_identity_authority"] is False
    assert (
        written["source_safety"]["lifecycle_preview_row"][
            "lifecycle_preview_metadata_status"
        ]
        == "STALE_PREVIEW_NOT_CURRENT_ROUTE_IDENTITY"
    )
    assert written["source_safety"]["lifecycle_preview_row"]["preview_lane_id"] == "maintenance_lane"
    assert written["metadata_identity_reissue"]["apply_review_only"] is True
    assert (
        written["metadata_identity_reissue"]["source_lifecycle_preview_metadata_label"][
            "identity_scope"
        ]
        == "historical_source_queue_lifecycle_preview"
    )

    refreshed_assignment = write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T18:02:00Z",
        write_receipt=False,
    )
    assignment = json.loads((root / refreshed_assignment["assignment_path"]).read_text(encoding="utf-8"))
    assignment_row = assignment["assignment_rows"][0]
    assert assignment_row["candidate_reissue_apply_review_ready"] is False
    assert assignment_row["candidate_reissue_already_satisfied"] is True
    assert (
        assignment_row["source_safety"][
            "source_metadata_identity_reissued_for_metadata_reissue"
        ]
        is True
    )
    refreshed_review = write_queue_metadata_identity_reissue_apply_review(
        root,
        generated_at="2026-06-04T18:03:00Z",
        write_receipt=False,
    )
    assert refreshed_review["verdict"] == "QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_NO_READY_ROWS"
    assert refreshed_review["apply_review_row_count"] == 0


def _seed_generated_mount_required_requests(root: Path) -> None:
    requests = [
        (
            "receipt_pointer_lineage.json",
            {
                "request_id": "codex_req_domain_weaver_receipt_pointer_lineage_repair",
                "lane_id": "audit_lane",
                "domain_id": "",
                "role_id": "role.receipt_integrity_proof_graph_steward",
                "work_class": "receipt_pointer_lineage_repair",
                "request_kind": "domain_weaver_receipt_pointer_lineage_repair",
                "working_capsule_identity": None,
            },
        ),
        (
            "monolith_decomposition.json",
            {
                "request_id": "codex_req_domain_weaver_monolith_decomposition",
                "lane_id": "architecture_lane",
                "domain_id": "",
                "role_id": "role.monolith_decomposition_cartographer",
                "work_class": "monolith_decomposition_cartography",
                "request_kind": "domain_weaver_stewarded_autonomy_monolith_decomposition_cartography",
                "working_capsule_identity": None,
            },
        ),
        (
            "exact_active_binding.json",
            {
                "request_id": "codex_req_domain_weaver_exact_active_binding",
                "lane_id": "architecture_lane",
                "domain_id": "",
                "role_id": "role.exact_active_binding_specialist",
                "work_class": "exact_active_binding_audit",
                "request_kind": "domain_weaver_stewarded_autonomy_exact_active_binding_audit",
                "working_capsule_identity": None,
            },
        ),
        (
            "receipt_integrity_graph.json",
            {
                "request_id": "codex_req_domain_weaver_receipt_integrity_graph",
                "lane_id": "audit_lane",
                "domain_id": "",
                "role_id": "role.receipt_integrity_proof_graph_steward",
                "work_class": "receipt_integrity_proof_graph",
                "request_kind": "domain_weaver_stewarded_autonomy_receipt_integrity_proof_graph",
                "working_capsule_identity": None,
            },
        ),
        (
            "continuous_nemesis.json",
            {
                "request_id": "codex_req_domain_weaver_continuous_nemesis",
                "lane_id": "audit_lane",
                "domain_id": "",
                "role_id": "role.continuous_nemesis",
                "work_class": "continuous_nemesis_review",
                "request_kind": "domain_weaver_stewarded_autonomy_continuous_nemesis",
                "working_capsule_identity": None,
            },
        ),
    ]
    for name, payload in requests:
        _write_work_request(root, name, payload)


def test_generated_mount_creation_dedupes_assignment_rows_without_materializing(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _seed_generated_mount_required_requests(root)
    write_queue_request_metadata_identity_reissue(
        root,
        generated_at="2026-06-04T18:30:00Z",
        write_receipt=False,
    )
    write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T18:31:00Z",
        write_receipt=False,
    )

    review = build_generated_mount_creation_for_metadata_reissue(
        root,
        generated_at="2026-06-04T18:32:00Z",
    )

    assert review["schema_id"] == GENERATED_MOUNT_CREATION_SCHEMA_ID
    assert review["verdict"] == "GENERATED_MOUNT_CREATION_READY"
    assert review["summary"]["source_generated_mount_required_row_count"] == 5
    assert review["summary"]["unique_mount_candidate_count"] == 4
    assert review["summary"]["mounts_materialized"] == 0
    rows = {row["mount_id"]: row for row in review["generated_mount_creation_rows"]}
    receipt_row = rows["role_receipt_integrity_proof_graph_steward__domain_receipt_proof_graph"]
    assert receipt_row["source_request_count"] == 2
    assert len(receipt_row["source_request_ids"]) == 2
    assert review["request_files_mutated"] is False
    assert review["replacement_request_files_written"] == 0
    assert review["codex_queue_run_started"] is False
    assert review["candidate_context_graph_deltas"]["accepted_state_claimed"] is False


def test_write_generated_mount_creation_materializes_candidate_mounts_only(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _seed_generated_mount_required_requests(root)
    write_queue_request_metadata_identity_reissue(
        root,
        generated_at="2026-06-04T18:30:00Z",
        write_receipt=False,
    )
    write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T18:31:00Z",
        write_receipt=False,
    )

    result = write_generated_mount_creation_for_metadata_reissue(
        root,
        generated_at="2026-06-04T18:32:00Z",
    )

    assert result["schema_id"].endswith(".write_result.v0_1")
    assert result["verdict"] == "GENERATED_MOUNT_CREATION_MOUNTS_MATERIALIZED"
    assert result["source_generated_mount_required_row_count"] == 5
    assert result["unique_mount_candidate_count"] == 4
    assert result["mounts_materialized"] == 4
    assert result["source_request_files_mutated"] is False
    assert result["replacement_request_files_written"] == 0
    assert result["codex_queue_run_started"] is False
    for key in [
        "review_path",
        "report_path",
        "context_graph_delta_path",
        "operator_receipt_path",
    ]:
        assert (root / result[key]).is_file()
    written = json.loads((root / result["review_path"]).read_text(encoding="utf-8"))
    assert written["summary"]["missing_required_file_count"] == 0
    for row in written["generated_mount_creation_rows"]:
        manifest_path = root / row["mount_path"] / "ION_AGENT_MOUNT_MANIFEST.json"
        assert manifest_path.is_file()
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["source_policy"] == (
            "generated from Domain Weaver metadata-assignment candidate rows; "
            "not registry-backed accepted truth"
        )
        assert manifest["authority"]["candidate_mount_only"] is True
        assert manifest["authority"]["production_authority"] is False
        assert manifest["authority"]["live_execution_authority"] is False
        assert manifest["authority"]["accepted_state_authority"] is False
        assert (root / row["mount_path"] / ".ion/ION_CONTEXT_CAPSULE.yaml").is_file()
        assert (root / row["mount_path"] / ".ion/ACTIVE_CONTEXT_PACKAGE.md").is_file()
        active_package = json.loads(
            (root / row["mount_path"] / ".ion/ACTIVE_CONTEXT_PACKAGE.json").read_text(
                encoding="utf-8"
            )
        )
        assert active_package["lane_ids"]
        assert active_package["lane_metadata"]
        assert (root / row["mount_path"] / ".codex/config.toml").is_file()
    report_text = (root / result["report_path"]).read_text(encoding="utf-8")
    assert "Generated Mount Creation For Metadata Reissue" in report_text


def test_write_metadata_identity_reissue_apply_review_artifacts_and_body_files(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    _mount_manifest(
        root,
        "role_context_cartographer__domain_agent_communication_systems",
        domain_id="domain.agent_communication_systems",
        role_id="role.context_cartographer",
    )
    _write_work_request(
        root,
        "context_cartographer.json",
        {
            "request_id": "codex_req_context_cartographer_agent_comms",
            "lane_id": "context_lane",
            "domain_id": "",
            "role_id": "role.context_cartographer",
            "work_class": "domain_weaver_agent_comms_queue_runner_pickup_proof",
            "request_kind": "agent_comms_pickup",
            "working_capsule_identity": None,
        },
    )
    write_queue_request_metadata_identity_reissue(
        root,
        generated_at="2026-06-04T17:57:00Z",
        write_receipt=False,
    )
    write_queue_metadata_identity_assignment(
        root,
        generated_at="2026-06-04T17:58:00Z",
        write_receipt=False,
    )

    result = write_queue_metadata_identity_reissue_apply_review(
        root,
        generated_at="2026-06-04T17:59:00Z",
    )

    assert result["schema_id"].endswith(".write_result.v0_1")
    assert result["verdict"] == "QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_READY"
    assert result["candidate_body_files_written"] == 1
    assert result["replacement_request_files_written"] == 0
    assert result["source_request_files_mutated"] is False
    for key in [
        "review_path",
        "report_path",
        "context_graph_delta_path",
        "operator_receipt_path",
    ]:
        assert (root / result[key]).is_file()
    written = json.loads((root / result["review_path"]).read_text(encoding="utf-8"))
    body_path = root / written["apply_review_rows"][0]["candidate_replacement_body_path"]
    assert body_path.is_file()
    body = json.loads(body_path.read_text(encoding="utf-8"))
    assert body["domain_id"] == "domain.agent_communication_systems"
    assert body["risk_level"] == "critical"
    assert body["route_metadata"]["explicit_fields"]["risk_level"] is True
    assert body["requested_model"] == "gpt-5.5"
    assert body["codex_model_override"]["selected_reasoning_effort"] == "xhigh"
    report_text = (root / result["report_path"]).read_text(encoding="utf-8")
    assert "Queue Metadata Identity Reissue Apply Review" in report_text


def test_exact_reissue_request_dispatch_readiness_validates_exact_rows(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_runtime_status(root, updated_at="2026-06-04T19:00:00+00:00")
    first = _write_exact_reissue_request(root)
    second = _write_exact_reissue_request(
        root,
        request_class="context_gate_reissue",
        name="codex_req_context_gate_reissue_test.json",
        lane_id="context_lane",
        domain_id="domain.agent_communication_systems",
        role_id="role.context_cartographer",
        callsign="CONTEXT_CARTOGRAPHER",
        mount_id="role_context_cartographer__domain_agent_communication_systems",
    )

    readiness = build_exact_reissue_request_dispatch_readiness(
        root,
        request_paths=[
            first.relative_to(root).as_posix(),
            second.relative_to(root).as_posix(),
        ],
        generated_at="2026-06-04T19:00:30Z",
    )

    assert readiness["schema_id"] == EXACT_REISSUE_REQUEST_DISPATCH_READINESS_SCHEMA_ID
    assert readiness["verdict"] == "EXACT_REISSUE_REQUEST_DISPATCH_READY"
    assert readiness["summary"]["request_path_count"] == 2
    assert readiness["summary"]["dispatch_ready_count"] == 2
    assert readiness["summary"]["blocked_row_count"] == 0
    assert readiness["ready_for_immediate_exact_start"] is True
    assert readiness["codex_queue_run_started"] is False
    assert readiness["actual_spawn_performed"] is False
    assert readiness["candidate_context_graph_deltas"]["accepted_state_claimed"] is False
    assert len(readiness["start_commands"]) == 2
    assert all("--request-path" in command for command in readiness["start_commands"])
    request_classes = {row["request_class"] for row in readiness["readiness_rows"]}
    assert request_classes == {"metadata_identity_reissue", "context_gate_reissue"}
    assert readiness["dispatch_groups"][0]["same_lane_parallelism"] == 1


def test_exact_reissue_request_dispatch_readiness_blocks_broad_or_unmounted_rows(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_runtime_status(root, updated_at="2026-06-04T19:00:00+00:00")
    request = _write_exact_reissue_request(root)
    payload = json.loads(request.read_text(encoding="utf-8"))
    payload["general_queue_processing_allowed"] = True
    payload["metadata_identity_reissue"]["assignment"]["selected_mount_path"] = (
        "ION/05_context/current/codex_agent_mounts/missing_mount"
    )
    payload["metadata_identity_reissue"]["assignment"]["active_context_package_path"] = (
        "ION/05_context/current/codex_agent_mounts/missing_mount/.ion/ACTIVE_CONTEXT_PACKAGE.md"
    )
    payload["working_capsule_identity"]["codex_agent_mount"] = (
        str(root / "ION/05_context/current/codex_agent_mounts/missing_mount")
    )
    payload["working_capsule_identity"]["working_capsule_path"] = (
        str(root / "ION/05_context/current/codex_agent_mounts/missing_mount/.ion")
    )
    request.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    readiness = build_exact_reissue_request_dispatch_readiness(
        root,
        request_paths=[request.relative_to(root).as_posix()],
        generated_at="2026-06-04T19:00:30Z",
    )

    assert readiness["verdict"] == "EXACT_REISSUE_REQUEST_DISPATCH_BLOCKED_BY_REQUEST_PRECHECK"
    assert readiness["summary"]["dispatch_ready_count"] == 0
    assert readiness["summary"]["blocked_row_count"] == 1
    blockers = set(readiness["blocked_rows"][0]["dispatch_blockers"])
    assert "general_queue_processing_not_explicitly_false" in blockers
    assert "selected_mount_missing" in blockers
    assert "active_context_package_missing" in blockers
    assert readiness["ready_for_immediate_exact_start"] is False
    assert readiness["start_commands"] == []


def test_exact_reissue_request_dispatch_readiness_blocks_unlabeled_stale_lifecycle_preview_metadata(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_runtime_status(root, updated_at="2026-06-04T19:00:00+00:00")
    request = _write_exact_reissue_request(root)
    payload = json.loads(request.read_text(encoding="utf-8"))
    payload["metadata_identity_reissue"]["source_safety"] = {
        "apply_source_safe": True,
        "lifecycle_preview_row": {
            "request_id": payload["metadata_identity_reissue"]["source_request_id"],
            "lane_id": "maintenance_lane",
            "repair_class": "stale_waiting_reconciliation_required",
            "stale": True,
        },
    }
    request.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    blocked = build_exact_reissue_request_dispatch_readiness(
        root,
        request_paths=[request.relative_to(root).as_posix()],
        generated_at="2026-06-04T19:00:30Z",
    )

    assert blocked["verdict"] == "EXACT_REISSUE_REQUEST_DISPATCH_BLOCKED_BY_REQUEST_PRECHECK"
    blocked_row = blocked["blocked_rows"][0]
    assert "unlabeled_stale_lifecycle_preview_metadata" in blocked_row["dispatch_blockers"]
    assert (
        blocked_row["lifecycle_preview_metadata_rows"][0][
            "lifecycle_preview_metadata_status"
        ]
        == "STALE_PREVIEW_NOT_CURRENT_ROUTE_IDENTITY"
    )
    assert blocked["ready_for_immediate_exact_start"] is False

    payload["metadata_identity_reissue"]["source_safety"]["lifecycle_preview_row"].update(
        {
            "lifecycle_preview_metadata_status": "STALE_PREVIEW_NOT_CURRENT_ROUTE_IDENTITY",
            "identity_scope": "historical_source_queue_lifecycle_preview",
            "preview_lane_id": "maintenance_lane",
            "current_route_identity_authority": False,
            "current_mount_identity_authority": False,
            "current_worker_identity_authority": False,
            "current_route_identity_source": (
                "replacement_request_fields_or_metadata_identity_reissue.assignment"
            ),
        }
    )
    request.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    clean = build_exact_reissue_request_dispatch_readiness(
        root,
        request_paths=[request.relative_to(root).as_posix()],
        generated_at="2026-06-04T19:00:30Z",
    )

    assert clean["verdict"] == "EXACT_REISSUE_REQUEST_DISPATCH_READY"
    assert clean["summary"]["dispatch_ready_count"] == 1
    assert clean["readiness_rows"][0]["lifecycle_preview_metadata_rows"][0][
        "current_route_identity_authority"
    ] is False


def test_write_exact_reissue_request_dispatch_readiness_artifacts_and_receipt(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_runtime_status(root, updated_at="2026-06-04T18:55:00+00:00")
    request = _write_exact_reissue_request(root)

    result = write_exact_reissue_request_dispatch_readiness(
        root,
        request_paths=[request.relative_to(root).as_posix()],
        generated_at="2026-06-04T19:00:30Z",
    )

    assert result["schema_id"].endswith(".write_result.v0_1")
    assert result["verdict"] == "EXACT_REISSUE_REQUEST_DISPATCH_READY_AFTER_RUNTIME_STATUS_REFRESH"
    assert result["dispatch_ready_count"] == 1
    assert result["blocked_row_count"] == 0
    assert result["ready_for_staged_exact_dispatch_after_status_refresh"] is True
    assert result["ready_for_immediate_exact_start"] is False
    assert result["codex_queue_run_started"] is False
    for key in [
        "readiness_path",
        "report_path",
        "context_graph_delta_path",
        "operator_receipt_path",
    ]:
        assert (root / result[key]).is_file()
    written = json.loads((root / result["readiness_path"]).read_text(encoding="utf-8"))
    assert written["runtime_status"]["status_command_required_before_start"] is True
    report_text = (root / result["report_path"]).read_text(encoding="utf-8")
    assert "Exact Reissue Request Dispatch Readiness" in report_text


def test_exact_reissue_request_dispatch_readiness_accepts_status_snapshot(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_runtime_status(root, updated_at="2026-06-04T18:55:00+00:00")
    request = _write_exact_reissue_request(root)

    readiness = build_exact_reissue_request_dispatch_readiness(
        root,
        request_paths=[request.relative_to(root).as_posix()],
        generated_at="2026-06-04T19:00:30Z",
        source_runtime_status={
            "verdict": "ION_CODEX_QUEUE_RUNNER_READY",
            "active_process_running": False,
            "active_run_count": 0,
            "active_runs": [],
            "queued_request_count": 1,
            "runner_state_path": "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json",
            "manual_proceed_relay_required": False,
            "concurrency": {
                "active_lane_count": 0,
                "active_lane_ids": [],
                "active_run_count": 0,
                "global_active_lock": False,
                "unknown_lane_active_run_count": 0,
            },
        },
    )

    assert readiness["verdict"] == "EXACT_REISSUE_REQUEST_DISPATCH_READY"
    assert readiness["ready_for_immediate_exact_start"] is True
    assert readiness["runtime_status"]["source"] == "provided_read_only_status_snapshot"
    assert readiness["runtime_status"]["runtime_status_fresh_enough"] is True


def test_limited_watch_refresh_emits_alerts_and_response_packets(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    write_swarm_control_plane(root, generated_at="2026-06-04T17:30:00Z")

    refresh = build_limited_watch_matrix_refresh(root, generated_at="2026-06-04T17:45:00Z")

    assert refresh["status"] == "limited_watch_matrix_refresh_built"
    assert refresh["verdict"] == "WATCH_REFRESH_ALERTS_ACTIVE_LIMITED_FANOUT_ONLY"
    assert refresh["summary"]["target_count"] >= 16
    assert refresh["summary"]["alert_count"] >= 3
    assert refresh["summary"]["severity_counts"]["critical"] >= 1
    alert_codes = {row["code"] for row in refresh["alerts"]}
    assert "MATERIALIZATION_READY_FALSE" in alert_codes
    assert "ORIGINAL_AUTOREACTION_NOT_PROVEN" in alert_codes
    assert "PCKT-DOMAIN-WEAVER-COMMS-AUTOREACTION-PROOF-V0_2-ORIGINAL-WORKER-BOUND" in refresh["response_packets"]
    assert refresh["candidate_context_graph_deltas"]["write_performed"] is False
    assert refresh["actual_watch_daemon_started"] is False
    assert refresh["actual_spawn_performed"] is False
    assert refresh["codex_queue_run_started"] is False
    assert refresh["accepted_state_claimed"] is False


def test_write_limited_watch_refresh_artifacts_and_receipt(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    _seed_current_evidence(root)
    write_swarm_control_plane(root, generated_at="2026-06-04T17:30:00Z")

    result = write_limited_watch_matrix_refresh(
        root, generated_at="2026-06-04T17:45:00Z"
    )

    assert result["verdict"] == "WATCH_REFRESH_ALERTS_ACTIVE_LIMITED_FANOUT_ONLY"
    for key in ["refresh_path", "report_path", "alerts_path", "operator_receipt_path"]:
        assert (root / result[key]).is_file()
    refresh = json.loads((root / result["refresh_path"]).read_text(encoding="utf-8"))
    alerts = json.loads((root / result["alerts_path"]).read_text(encoding="utf-8"))
    report = (root / result["report_path"]).read_text(encoding="utf-8")
    assert refresh["summary"]["alert_count"] == result["alert_count"]
    assert alerts["candidate_context_graph_deltas"]["accepted_state_claimed"] is False
    assert "Domain Weaver Limited Watch Matrix Refresh" in report
