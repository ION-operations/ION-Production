from __future__ import annotations

from pathlib import Path

from kernel.ion_domain_weaver_route_gate_matrix import (
    HANDLER_CONTRACT_SCHEMA_ID,
    SCHEMA_ID,
    build_domain_weaver_route_gate_matrix,
    build_domain_weaver_route_handler_gate_contract,
)


def test_domain_weaver_route_gate_matrix_surfaces_mutation_gate_gaps() -> None:
    matrix = build_domain_weaver_route_gate_matrix(Path.cwd())

    assert matrix["schema_id"] == SCHEMA_ID
    assert matrix["policy"]["candidate_only"] is True
    assert matrix["policy"]["handler_parity_proven"] is False
    assert matrix["policy"]["systemic_mutation_route_coverage_proven"] is True
    assert matrix["summary"]["mutating_route_count"] > 0
    assert matrix["summary"]["domain_weaver_mutating_route_count"] >= 3
    assert matrix["summary"]["domain_weaver_gapped_mutating_route_count"] == 0
    assert matrix["summary"]["systemic_mutation_route_coverage_proven"] is True
    assert matrix["summary"]["systemic_mutation_route_gap_count"] == 0
    assert matrix["summary"]["candidate_declared_exception_gap_count"] == 0
    assert matrix["summary"]["real_route_declaration_gap_count"] == 0
    assert matrix["systemic_mutation_route_coverage"]["status"] == "declared_route_gates_complete_candidate"
    assert matrix["systemic_mutation_route_coverage"]["blocker"] is None

    rows = {
        (row["branch_id"], row["route_id"]): row
        for row in matrix["rows"]
    }
    start_plan = rows[("domain_weaver_agents", "spawn_dispatch_start_plan")]
    assert start_plan["mutates_state"] is False
    assert start_plan["gate_coverage_status"] == "read_only"
    quarantine = rows[("domain_weaver_agents", "spawn_dispatch_legacy_receipt_quarantine")]
    assert quarantine["mutates_state"] is False
    assert quarantine["gate_coverage_status"] == "read_only"
    pressure_plan = rows[("domain_weaver_agents", "pressure_wave_plan")]
    assert pressure_plan["mutates_state"] is False
    assert pressure_plan["gate_coverage_status"] == "read_only"

    pressure_seed = rows[("domain_weaver_agents", "pressure_wave_spawn_request_seed")]
    assert pressure_seed["mutates_state"] is True
    assert pressure_seed["declared_gates"]["confirmation"] is True
    assert pressure_seed["declared_gates"]["idempotency"] is True
    assert pressure_seed["declared_gates"]["agent_id"] is True
    assert pressure_seed["declared_gates"]["write_intent_lease"] is True
    assert pressure_seed["gate_gaps"] == []
    assert pressure_seed["gate_coverage_status"] == "strong"
    assert pressure_seed["severity"] == "none"

    for route_id in ("comms_send", "comms_pickup", "comms_dispatch_enqueue"):
        row = rows[("domain_weaver_agents", route_id)]
        assert row["mutates_state"] is True
        assert row["declared_gates"]["confirmation"] is True
        assert row["declared_gates"]["idempotency"] is True
        assert row["declared_gates"]["agent_id"] is True
        assert row["declared_gates"]["write_intent_lease"] is True
        assert row["gate_gaps"] == []
        assert row["gate_coverage_status"] == "strong"
        assert row["severity"] == "none"

    active_context_apply = rows[("domain_weaver_agents", "active_context_gated_refresh_apply")]
    assert active_context_apply["mutates_state"] is True
    assert active_context_apply["declared_gates"]["confirmation"] is True
    assert active_context_apply["declared_gates"]["idempotency"] is True
    assert active_context_apply["declared_gates"]["agent_id"] is True
    assert active_context_apply["declared_gates"]["edit_lease"] is True
    assert active_context_apply["gate_gaps"] == []
    assert active_context_apply["gate_coverage_status"] == "strong"
    assert active_context_apply["severity"] == "none"

    projection_apply = rows[("domain_weaver_agents", "projection_accepted_refresh_apply")]
    assert projection_apply["mutates_state"] is True
    assert projection_apply["declared_gates"]["confirmation"] is True
    assert projection_apply["declared_gates"]["idempotency"] is True
    assert projection_apply["declared_gates"]["agent_id"] is True
    assert projection_apply["declared_gates"]["edit_lease"] is True
    assert projection_apply["gate_gaps"] == []
    assert projection_apply["gate_coverage_status"] == "strong"
    assert projection_apply["severity"] == "none"

    semantic_alias_apply = rows[("domain_weaver_agents", "semantic_alias_projection_apply")]
    assert semantic_alias_apply["mutates_state"] is True
    assert semantic_alias_apply["declared_gates"]["confirmation"] is True
    assert semantic_alias_apply["declared_gates"]["idempotency"] is True
    assert semantic_alias_apply["declared_gates"]["agent_id"] is True
    assert semantic_alias_apply["declared_gates"]["edit_lease"] is True
    assert semantic_alias_apply["gate_gaps"] == []
    assert semantic_alias_apply["gate_coverage_status"] == "strong"
    assert semantic_alias_apply["severity"] == "none"

    semantic_alias_manifest_apply = rows[("domain_weaver_agents", "semantic_alias_mount_manifest_apply")]
    assert semantic_alias_manifest_apply["mutates_state"] is True
    assert semantic_alias_manifest_apply["declared_gates"]["confirmation"] is True
    assert semantic_alias_manifest_apply["declared_gates"]["idempotency"] is True
    assert semantic_alias_manifest_apply["declared_gates"]["agent_id"] is True
    assert semantic_alias_manifest_apply["declared_gates"]["edit_lease"] is True
    assert semantic_alias_manifest_apply["gate_gaps"] == []
    assert semantic_alias_manifest_apply["gate_coverage_status"] == "strong"
    assert semantic_alias_manifest_apply["severity"] == "none"

    codex_request = rows[("codex_queue", "request_work_packet")]
    assert codex_request["mutates_state"] is True
    assert codex_request["gate_coverage_status"] == "strong"
    assert codex_request["gate_gaps"] == []

    must_fix = {
        (row["branch_id"], row["route_id"])
        for row in matrix["must_fix_before_serious_self_evolution"]
    }
    assert ("domain_weaver_agents", "comms_send") not in must_fix
    assert ("domain_weaver_agents", "comms_pickup") not in must_fix
    assert ("domain_weaver_agents", "comms_dispatch_enqueue") not in must_fix
    assert ("domain_weaver_agents", "active_context_gated_refresh_apply") not in must_fix
    assert ("domain_weaver_agents", "projection_accepted_refresh_apply") not in must_fix
    assert ("domain_weaver_agents", "semantic_alias_projection_apply") not in must_fix
    assert ("domain_weaver_agents", "semantic_alias_mount_manifest_apply") not in must_fix
    assert ("domain_weaver_agents", "pressure_wave_spawn_request_seed") not in must_fix
    assert ("domain_weaver_agents", "spawn_dispatch_legacy_receipt_quarantine") not in must_fix

    assert matrix["systemic_mutation_route_coverage"]["remaining_gapped_mutating_routes"] == []
    for route_id in (
        "apply_create",
        "artifact_upload_init",
        "artifact_upload_chunk",
        "artifact_upload_commit",
    ):
        row = rows[("repo_ingest", route_id)]
        assert row["gate_coverage_status"] == "strong"
        assert row["declared_gates"]["idempotency"] is True
        assert row["gate_gaps"] == []
    assert rows[("agent_swarm", "invoke")]["gate_coverage_status"] == "strong"
    assert rows[("agent_swarm", "invoke")]["declared_gates"]["agent_id"] is True
    assert rows[("agent_swarm", "swarm_step")]["gate_coverage_status"] == "strong"
    assert rows[("agent_swarm", "swarm_step")]["declared_gates"]["agent_id"] is True


def test_domain_weaver_route_handler_gate_contract_aligns_declared_mutation_fields() -> None:
    contract = build_domain_weaver_route_handler_gate_contract(Path.cwd())

    assert contract["schema_id"] == HANDLER_CONTRACT_SCHEMA_ID
    assert contract["policy"]["candidate_only"] is True
    assert contract["policy"]["full_system_parity_proven"] is False
    assert contract["summary"]["mutating_route_count"] == 8
    assert contract["summary"]["aligned_mutating_route_count"] == 8
    assert contract["summary"]["contract_gap_count"] == 0
    rows = {row["route_id"]: row for row in contract["rows"]}

    for route_id in ("comms_send", "comms_pickup", "comms_dispatch_enqueue"):
        row = rows[route_id]
        assert row["contract_status"] == "aligned"
        assert row["handler_entrypoint_found"] is True
        assert row["missing_required_fields"] == []
        assert row["expected_required_fields"] == [
            "agent_id",
            "confirmation",
            "idempotency_key",
            "write_intent_lease_id",
        ]
        assert row["missing_required_target_roots"] == []
        assert row["branch_gateway_enforcement"] == "write_intent_lease_predelegation_gate"

    pressure_seed = rows["pressure_wave_spawn_request_seed"]
    assert pressure_seed["contract_status"] == "aligned"
    assert pressure_seed["handler_entrypoint_found"] is True
    assert pressure_seed["missing_required_fields"] == []
    assert pressure_seed["expected_required_fields"] == [
        "agent_id",
        "confirmation",
        "execute_write",
        "idempotency_key",
        "write_intent_lease_id",
    ]
    assert pressure_seed["missing_required_target_roots"] == []
    assert pressure_seed["branch_gateway_enforcement"] == "write_intent_lease_predelegation_gate"

    active_context_apply = rows["active_context_gated_refresh_apply"]
    assert active_context_apply["contract_status"] == "aligned"
    assert active_context_apply["handler_entrypoint_found"] is True
    assert active_context_apply["missing_required_fields"] == []
    assert active_context_apply["expected_required_fields"] == [
        "agent_id",
        "confirmation",
        "execute_write",
        "idempotency_key",
        "lease_id",
        "preflight_path",
    ]
    assert active_context_apply["branch_gateway_enforcement"] == "handler_dynamic_exclusive_write_lease_gate"

    projection_apply = rows["projection_accepted_refresh_apply"]
    assert projection_apply["contract_status"] == "aligned"
    assert projection_apply["handler_entrypoint_found"] is True
    assert projection_apply["missing_required_fields"] == []
    assert projection_apply["expected_required_fields"] == [
        "accepted_state_write_confirmation",
        "agent_id",
        "before_sha256",
        "confirmation",
        "execute_write",
        "idempotency_key",
        "lease_id",
        "replacement_body_sha256",
    ]
    assert projection_apply["expected_lease_target_path"] == (
        "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    )
    assert projection_apply["declared_lease_target_path"] == (
        "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    )
    assert projection_apply["lease_target_path_ok"] is True
    assert projection_apply["branch_gateway_enforcement"] == "static_exclusive_write_lease_predelegation_gate"

    semantic_alias_apply = rows["semantic_alias_projection_apply"]
    assert semantic_alias_apply["contract_status"] == "aligned"
    assert semantic_alias_apply["handler_entrypoint_found"] is True
    assert semantic_alias_apply["missing_required_fields"] == []
    assert semantic_alias_apply["expected_required_fields"] == [
        "agent_id",
        "before_sha256",
        "confirmation",
        "execute_write",
        "idempotency_key",
        "lease_id",
        "replacement_body_sha256",
        "semantic_alias_write_confirmation",
    ]
    assert semantic_alias_apply["expected_lease_target_path"] == (
        "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    )
    assert semantic_alias_apply["declared_lease_target_path"] == (
        "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    )
    assert semantic_alias_apply["lease_target_path_ok"] is True
    assert semantic_alias_apply["branch_gateway_enforcement"] == "static_exclusive_write_lease_predelegation_gate"

    semantic_alias_manifest_apply = rows["semantic_alias_mount_manifest_apply"]
    assert semantic_alias_manifest_apply["contract_status"] == "aligned"
    assert semantic_alias_manifest_apply["handler_entrypoint_found"] is True
    assert semantic_alias_manifest_apply["missing_required_fields"] == []
    assert semantic_alias_manifest_apply["expected_required_fields"] == [
        "agent_id",
        "before_sha256",
        "confirmation",
        "execute_write",
        "idempotency_key",
        "lease_id",
        "manifest_write_confirmation",
        "replacement_body_sha256",
    ]
    assert semantic_alias_manifest_apply["expected_lease_target_path"] == (
        "ION/05_context/current/codex_agent_mounts/"
        "role_atlas__ion_vnext_front_door/ION_AGENT_MOUNT_MANIFEST.json"
    )
    assert semantic_alias_manifest_apply["declared_lease_target_path"] == (
        "ION/05_context/current/codex_agent_mounts/"
        "role_atlas__ion_vnext_front_door/ION_AGENT_MOUNT_MANIFEST.json"
    )
    assert semantic_alias_manifest_apply["lease_target_path_ok"] is True
    assert semantic_alias_manifest_apply["branch_gateway_enforcement"] == "static_exclusive_write_lease_predelegation_gate"

    assert rows["spawn_dispatch_start_plan"]["mutates_state"] is False
    assert rows["spawn_dispatch_start_plan"]["contract_status"] == "aligned"
    assert rows["spawn_dispatch_legacy_receipt_quarantine"]["mutates_state"] is False
    assert rows["spawn_dispatch_legacy_receipt_quarantine"]["contract_status"] == "aligned"
    assert rows["pressure_wave_plan"]["mutates_state"] is False
    assert rows["pressure_wave_plan"]["contract_status"] == "aligned"
    assert rows["comms_autoreaction_proof"]["mutates_state"] is False
    assert rows["comms_dispatch_preview"]["mutates_state"] is False
