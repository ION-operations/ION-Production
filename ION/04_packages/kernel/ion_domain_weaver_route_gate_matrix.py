"""Candidate route-gate matrix for Domain Weaver self-evolution readiness."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

import yaml


SCHEMA_ID = "ion.domain_weaver.route_gate_matrix.v0_1_candidate"
HANDLER_CONTRACT_SCHEMA_ID = "ion.domain_weaver.route_handler_write_set_contract.v0_1_candidate"
HANDLER_CONTRACT_WRITE_RESULT_SCHEMA_ID = "ion.domain_weaver.route_handler_write_set_contract.write_result.v0_1"
REGISTRY_RELATIVE_PATH = Path("ION/03_registry/ion_action_mcp_branch_leader_registry.yaml")
DEFAULT_CONTEXT_ROOT = Path("ION/05_context/current/domain_weaver")
DEFAULT_ROUTE_POLICY_DIR = DEFAULT_CONTEXT_ROOT / "route_policy"
DEFAULT_OPERATOR_ACTION_DIR = DEFAULT_CONTEXT_ROOT / "operator_actions"
HANDLER_CONTRACT_JSON_NAME = "DOMAIN_WEAVER_ACTION_ROUTE_HANDLER_WRITE_SET_CONTRACT.latest.candidate.json"
HANDLER_CONTRACT_REPORT_NAME = "DOMAIN_WEAVER_ACTION_ROUTE_HANDLER_WRITE_SET_CONTRACT.latest.md"
SYSTEMIC_MUTATION_ROUTE_COVERAGE_BLOCKER = "SYSTEMIC_MUTATION_ROUTE_COVERAGE_NOT_PROVEN"

ACTOR_REQUIRED_BRANCHES = {
    "codex_queue",
    "domain_weaver_agents",
    "agent_swarm",
}
WRITE_INTENT_REQUIRED_BRANCHES = {
    "codex_queue",
    "domain_weaver_agents",
}
DOMAIN_WEAVER_HANDLER_CONTRACT_SCOPE = {
    "spawn_dispatch_start_plan": {
        "mutates_state": False,
        "handler_function": "domain_weaver_spawn_dispatch_start_plan",
        "expected_write_set_class": "none",
    },
    "spawn_dispatch_legacy_receipt_quarantine": {
        "mutates_state": False,
        "handler_function": "domain_weaver_spawn_dispatch_legacy_receipt_quarantine",
        "expected_write_set_class": "none",
    },
    "pressure_wave_plan": {
        "mutates_state": False,
        "handler_function": "domain_weaver_pressure_wave_plan",
        "expected_write_set_class": "none",
    },
    "pressure_wave_spawn_request_seed": {
        "mutates_state": True,
        "handler_function": "domain_weaver_pressure_wave_spawn_request_seed",
        "expected_write_set_class": "domain_weaver_worker_local_spawn_request_rows",
        "required_fields": [
            "execute_write",
            "idempotency_key",
            "confirmation",
            "agent_id",
            "write_intent_lease_id",
        ],
        "required_target_roots": [
            "ION/05_context/current/domain_weaver/workers",
        ],
    },
    "comms_send": {
        "mutates_state": True,
        "handler_function": "domain_weaver_agents_comms_send",
        "expected_write_set_class": "agent_comms_message_thread_signal_receipt",
        "required_fields": ["idempotency_key", "confirmation", "agent_id", "write_intent_lease_id"],
        "required_target_roots": [
            "ION/05_context/current/agent_comms",
            "ION/05_context/current/runtime_services/receipts",
        ],
    },
    "comms_pickup": {
        "mutates_state": True,
        "handler_function": "domain_weaver_agents_comms_pickup",
        "expected_write_set_class": "agent_comms_inbox_pickup_receipt",
        "required_fields": ["idempotency_key", "confirmation", "agent_id", "write_intent_lease_id"],
        "required_target_roots": [
            "ION/05_context/current/agent_comms",
            "ION/05_context/current/runtime_services/receipts",
        ],
    },
    "comms_autoreaction_proof": {
        "mutates_state": False,
        "handler_function": "domain_weaver_agents_comms_autoreaction_proof",
        "expected_write_set_class": "none",
    },
    "comms_dispatch_preview": {
        "mutates_state": False,
        "handler_function": "domain_weaver_agents_comms_dispatch_preview",
        "expected_write_set_class": "none",
    },
    "comms_dispatch_enqueue": {
        "mutates_state": True,
        "handler_function": "domain_weaver_agents_comms_dispatch_enqueue",
        "expected_write_set_class": "queued_not_started_codex_request_and_agent_comms_receipt",
        "required_fields": ["idempotency_key", "confirmation", "agent_id", "write_intent_lease_id"],
        "required_target_roots": [
            "ION/05_context/current/agent_comms",
            "ION/05_context/current/chatgpt_connector",
            "ION/05_context/current/runtime_services/receipts",
        ],
    },
    "active_context_gated_refresh_apply": {
        "mutates_state": True,
        "handler_function": "domain_weaver_active_context_gated_refresh_apply",
        "expected_write_set_class": "active_context_package_files_and_apply_receipt",
        "required_fields": ["preflight_path", "execute_write", "idempotency_key", "confirmation", "agent_id", "lease_id"],
        "dynamic_exclusive_write_lease": True,
    },
    "projection_accepted_refresh_apply": {
        "mutates_state": True,
        "handler_function": "domain_weaver_projection_accepted_refresh_apply",
        "expected_write_set_class": "domain_weaver_projection_file_and_accepted_apply_receipt",
        "required_fields": [
            "execute_write",
            "before_sha256",
            "replacement_body_sha256",
            "accepted_state_write_confirmation",
            "idempotency_key",
            "confirmation",
            "agent_id",
            "lease_id",
        ],
        "static_exclusive_write_lease": True,
        "required_lease_target_path": "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json",
    },
    "semantic_alias_projection_apply": {
        "mutates_state": True,
        "handler_function": "domain_weaver_semantic_alias_projection_apply",
        "expected_write_set_class": "domain_weaver_projection_exact_semantic_alias_values_and_apply_receipt",
        "required_fields": [
            "execute_write",
            "before_sha256",
            "replacement_body_sha256",
            "semantic_alias_write_confirmation",
            "idempotency_key",
            "confirmation",
            "agent_id",
            "lease_id",
        ],
        "static_exclusive_write_lease": True,
        "required_lease_target_path": "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json",
    },
    "semantic_alias_mount_manifest_apply": {
        "mutates_state": True,
        "handler_function": "domain_weaver_semantic_alias_mount_manifest_apply",
        "expected_write_set_class": "domain_weaver_vnext_front_door_mount_manifest_and_apply_receipt",
        "required_fields": [
            "execute_write",
            "before_sha256",
            "replacement_body_sha256",
            "manifest_write_confirmation",
            "idempotency_key",
            "confirmation",
            "agent_id",
            "lease_id",
        ],
        "static_exclusive_write_lease": True,
        "required_lease_target_path": (
            "ION/05_context/current/codex_agent_mounts/"
            "role_atlas__ion_vnext_front_door/ION_AGENT_MOUNT_MANIFEST.json"
        ),
    },
}

SYSTEMIC_MUTATION_GAP_ASSESSMENTS = {
    ("repo_ingest", "apply_create"): {
        "assessment": "candidate_declared_exception_supported_by_handler_dedupe",
        "declared_exception_candidate": True,
        "evidence": [
            "registry_declares_idempotency_required_false",
            "ion_file_put_text_accepts_explicit_idempotency_key_or_client_request_id",
            "ion_file_put_text_falls_back_to_target_sha256_dedupe_ledger",
            "connector_tests_cover_idempotent_replay",
        ],
        "recommended_next": "settle_candidate_exception_or_require_explicit_idempotency_in_registry",
    },
    ("repo_ingest", "artifact_upload_init"): {
        "assessment": "declared_nonstandard_session_route_but_explicit_idempotency_unproven",
        "declared_exception_candidate": True,
        "evidence": [
            "registry_declares_idempotency_required_false",
            "handler_creates_upload_session_state",
            "no_explicit_idempotency_key_or_replay_ledger_proven_for_init",
        ],
        "recommended_next": "add_explicit_idempotency_or_formally_settle_upload_session_exception",
    },
    ("repo_ingest", "artifact_upload_chunk"): {
        "assessment": "declared_nonstandard_session_route_but_explicit_idempotency_unproven",
        "declared_exception_candidate": True,
        "evidence": [
            "registry_declares_idempotency_required_false",
            "handler_blocks_duplicate_chunk_index",
            "duplicate_chunk_block_is_fail_closed_not_idempotent_replay",
        ],
        "recommended_next": "add_explicit_idempotency_or_formally_settle_chunk_index_exception",
    },
    ("repo_ingest", "artifact_upload_commit"): {
        "assessment": "declared_nonstandard_session_route_but_explicit_idempotency_unproven",
        "declared_exception_candidate": True,
        "evidence": [
            "registry_declares_idempotency_required_false",
            "handler_closes_upload_session_after_commit",
            "commit_replay_returns_closed_session_not_idempotent_replay",
        ],
        "recommended_next": "add_explicit_idempotency_or_formally_settle_commit_exception",
    },
    ("agent_swarm", "invoke"): {
        "assessment": "real_actor_proof_route_declaration_gap",
        "declared_exception_candidate": False,
        "evidence": [
            "agent_swarm_is_actor_required_branch",
            "registry_route_lacks_agent_id_required",
            "branch_gateway_actor_proof_only_runs_when_declared",
        ],
        "recommended_next": "add_agent_id_required_and_agent_id_schema_gate_or_equivalent_actor_proof",
    },
    ("agent_swarm", "swarm_step"): {
        "assessment": "real_actor_proof_route_declaration_gap",
        "declared_exception_candidate": False,
        "evidence": [
            "agent_swarm_is_actor_required_branch",
            "registry_route_lacks_agent_id_required",
            "branch_gateway_actor_proof_only_runs_when_declared",
        ],
        "recommended_next": "add_agent_id_required_and_agent_id_schema_gate_or_equivalent_actor_proof",
    },
}


def build_domain_weaver_route_gate_matrix(root: str | Path | None) -> dict[str, Any]:
    """Return a registry-derived mutation gate matrix.

    The matrix is read-only and candidate-only. It reports declared route gates;
    it does not prove handler implementation parity.
    """

    shell_root = Path(root or ".").expanduser().resolve(strict=False)
    registry_path = shell_root / REGISTRY_RELATIVE_PATH
    registry = _load_yaml(registry_path)
    branches = registry.get("branches") if isinstance(registry.get("branches"), list) else []
    rows: list[dict[str, Any]] = []
    for branch in branches:
        if not isinstance(branch, Mapping):
            continue
        branch_id = str(branch.get("branch_id") or "").strip()
        family = str(branch.get("family") or "").strip()
        routes = branch.get("routes") if isinstance(branch.get("routes"), list) else []
        for route in routes:
            if not isinstance(route, Mapping):
                continue
            rows.append(_route_row(branch_id, family, route))

    mutating_rows = [row for row in rows if row["mutates_state"]]
    gapped_rows = [row for row in mutating_rows if row["gate_gaps"]]
    domain_weaver_rows = [
        row
        for row in rows
        if row["branch_id"] == "domain_weaver_agents"
        or str(row.get("family") or "").startswith("domain_weaver")
    ]
    domain_weaver_mutating_rows = [row for row in domain_weaver_rows if row["mutates_state"]]
    domain_weaver_gapped_rows = [row for row in domain_weaver_mutating_rows if row["gate_gaps"]]
    systemic_gap_rows = [_systemic_gap_summary(row) for row in gapped_rows]
    candidate_exception_rows = [
        row for row in gapped_rows if row.get("systemic_gap_assessment", {}).get("declared_exception_candidate")
    ]
    real_gap_rows = [
        row
        for row in gapped_rows
        if not row.get("systemic_gap_assessment", {}).get("declared_exception_candidate")
    ]
    systemic_coverage_proven = not systemic_gap_rows
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _utc_now(),
        "active_root": str(shell_root),
        "registry_path": REGISTRY_RELATIVE_PATH.as_posix(),
        "policy": {
            "candidate_only": True,
            "handler_parity_proven": False,
            "systemic_mutation_route_coverage_proven": systemic_coverage_proven,
            "actor_required_branches": sorted(ACTOR_REQUIRED_BRANCHES),
            "write_intent_required_branches": sorted(WRITE_INTENT_REQUIRED_BRANCHES),
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
        "summary": {
            "route_count": len(rows),
            "mutating_route_count": len(mutating_rows),
            "gapped_mutating_route_count": len(gapped_rows),
            "domain_weaver_route_count": len(domain_weaver_rows),
            "domain_weaver_mutating_route_count": len(domain_weaver_mutating_rows),
            "domain_weaver_gapped_mutating_route_count": len(domain_weaver_gapped_rows),
            "strong_mutating_route_count": sum(
                1 for row in mutating_rows if row["gate_coverage_status"] == "strong"
            ),
            "systemic_mutation_route_coverage_proven": systemic_coverage_proven,
            "systemic_mutation_route_gap_count": len(systemic_gap_rows),
            "candidate_declared_exception_gap_count": len(candidate_exception_rows),
            "real_route_declaration_gap_count": len(real_gap_rows),
        },
        "systemic_mutation_route_coverage": {
            "status": "not_proven" if systemic_gap_rows else "declared_route_gates_complete_candidate",
            "blocker": SYSTEMIC_MUTATION_ROUTE_COVERAGE_BLOCKER if systemic_gap_rows else None,
            "remaining_gapped_mutating_routes": systemic_gap_rows,
            "non_claims": [
                "candidate exceptions are not accepted exceptions",
                "handler-side replay evidence is not full handler parity",
                "registry-derived strong rows do not prove every runtime write path",
            ],
        },
        "must_fix_before_serious_self_evolution": [
            {
                "branch_id": row["branch_id"],
                "route_id": row["route_id"],
                "gate_gaps": row["gate_gaps"],
                "severity": row["severity"],
            }
            for row in domain_weaver_gapped_rows
        ],
        "must_settle_before_systemic_mutation_route_coverage": systemic_gap_rows,
        "rows": rows,
    }


def _route_row(branch_id: str, family: str, route: Mapping[str, Any]) -> dict[str, Any]:
    route_id = str(route.get("route_id") or "").strip()
    mutates = bool(route.get("mutates_state"))
    args_schema = route.get("args_schema") if isinstance(route.get("args_schema"), Mapping) else {}
    required_args = {
        str(item)
        for item in (args_schema.get("required") if isinstance(args_schema.get("required"), list) else [])
        if str(item or "").strip()
    }
    gates = {
        "confirmation": bool(route.get("confirmation_required")) or "confirmation" in required_args,
        "idempotency": bool(route.get("idempotency_required")) or "idempotency_key" in required_args,
        "agent_id": bool(route.get("agent_id_required")) or "agent_id" in required_args,
        "write_intent_lease": bool(route.get("write_intent_lease_required"))
        or bool(route.get("write_intent_lease_id_required"))
        or "write_intent_lease_id" in required_args,
        "edit_lease": bool(route.get("edit_lease_required"))
        or bool(route.get("lease_id_required"))
        or "lease_id" in required_args,
        "artifact_lease": bool(route.get("artifact_lease_required")),
    }
    gaps: list[str] = []
    if mutates:
        if not gates["confirmation"]:
            gaps.append("confirmation_gate_missing")
        if not gates["idempotency"]:
            gaps.append("idempotency_gate_missing")
        if branch_id in ACTOR_REQUIRED_BRANCHES and not gates["agent_id"]:
            gaps.append("agent_id_gate_missing")
        domain_weaver_edit_lease_route = (
            branch_id == "domain_weaver_agents"
            and route_id in {
                "active_context_gated_refresh_apply",
                "projection_accepted_refresh_apply",
                "semantic_alias_projection_apply",
                "semantic_alias_mount_manifest_apply",
            }
            and gates["edit_lease"]
        )
        if branch_id in WRITE_INTENT_REQUIRED_BRANCHES and not gates["write_intent_lease"] and not domain_weaver_edit_lease_route:
            gaps.append("write_intent_lease_gate_missing")
    if not mutates:
        status = "read_only"
    elif gaps:
        status = "gapped"
    else:
        status = "strong"
    return {
        "branch_id": branch_id,
        "family": family,
        "route_id": route_id,
        "title": route.get("title"),
        "mutates_state": mutates,
        "local_handler": route.get("local_handler"),
        "mcp_tool": route.get("mcp_tool"),
        "route_schema_version": route.get("route_schema_version"),
        "required_args": sorted(required_args),
        "declared_gates": gates,
        "gate_gaps": gaps,
        "gate_coverage_status": status,
        "systemic_gap_assessment": _systemic_gap_assessment(branch_id, route_id, gaps),
        "severity": _severity(branch_id, mutates, gaps),
        "handler_parity_proven": False,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def _systemic_gap_assessment(branch_id: str, route_id: str, gaps: list[str]) -> dict[str, Any]:
    if not gaps:
        return {
            "assessment": "none",
            "declared_exception_candidate": False,
            "coverage_effect": "route_level_declared_gates_strong",
            "evidence": [],
            "recommended_next": "none",
        }
    configured = SYSTEMIC_MUTATION_GAP_ASSESSMENTS.get((branch_id, route_id), {})
    declared_exception = bool(configured.get("declared_exception_candidate"))
    if configured:
        assessment = str(configured.get("assessment") or "unclassified_systemic_gap")
        evidence = [
            str(item)
            for item in configured.get("evidence", [])
            if str(item or "").strip()
        ]
        recommended_next = str(configured.get("recommended_next") or "settle_or_repair_route_gap")
    else:
        assessment = "unclassified_systemic_gap"
        evidence = ["no_route_specific_exception_or_repair_evidence_declared"]
        recommended_next = "classify_exception_or_repair_route_gate"
    return {
        "assessment": assessment,
        "declared_exception_candidate": declared_exception,
        "coverage_effect": (
            "requires_exception_settlement_before_systemic_coverage_claim"
            if declared_exception
            else "requires_route_gate_repair_before_systemic_coverage_claim"
        ),
        "evidence": evidence,
        "recommended_next": recommended_next,
    }


def _systemic_gap_summary(row: Mapping[str, Any]) -> dict[str, Any]:
    assessment = row.get("systemic_gap_assessment") if isinstance(row.get("systemic_gap_assessment"), Mapping) else {}
    return {
        "branch_id": row.get("branch_id"),
        "route_id": row.get("route_id"),
        "gate_gaps": list(row.get("gate_gaps") or []),
        "severity": row.get("severity"),
        "assessment": assessment.get("assessment"),
        "declared_exception_candidate": bool(assessment.get("declared_exception_candidate")),
        "coverage_effect": assessment.get("coverage_effect"),
        "evidence": list(assessment.get("evidence") or []),
        "recommended_next": assessment.get("recommended_next"),
    }


def render_domain_weaver_route_gate_matrix_report(payload: Mapping[str, Any]) -> str:
    summary = payload.get("summary") if isinstance(payload.get("summary"), Mapping) else {}
    systemic = (
        payload.get("systemic_mutation_route_coverage")
        if isinstance(payload.get("systemic_mutation_route_coverage"), Mapping)
        else {}
    )
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    domain_weaver_mutating = [
        row
        for row in rows
        if isinstance(row, Mapping)
        and row.get("branch_id") == "domain_weaver_agents"
        and row.get("mutates_state") is True
    ]
    gap_rows = systemic.get("remaining_gapped_mutating_routes")
    if not isinstance(gap_rows, list):
        gap_rows = []

    lines = [
        "# Domain Weaver Action Route Gate Matrix",
        "",
        "Authority: candidate-only. Registry-derived declaration matrix; no route invoked.",
        "",
        "## Summary",
        "",
        f"- routes: `{summary.get('route_count')}`",
        f"- mutating routes: `{summary.get('mutating_route_count')}`",
        f"- gapped mutating routes: `{summary.get('gapped_mutating_route_count')}`",
        f"- Domain Weaver routes: `{summary.get('domain_weaver_route_count')}`",
        f"- Domain Weaver mutating routes: `{summary.get('domain_weaver_mutating_route_count')}`",
        f"- Domain Weaver gapped mutating routes: `{summary.get('domain_weaver_gapped_mutating_route_count')}`",
        f"- systemic mutation-route coverage: `{systemic.get('status')}`",
        f"- candidate declared exception gaps: `{summary.get('candidate_declared_exception_gap_count')}`",
        f"- real route declaration gaps: `{summary.get('real_route_declaration_gap_count')}`",
        "",
        "## Domain Weaver Mutating Routes",
        "",
    ]
    if domain_weaver_mutating:
        for row in sorted(domain_weaver_mutating, key=lambda item: str(item.get("route_id") or "")):
            gates = row.get("declared_gates") if isinstance(row.get("declared_gates"), Mapping) else {}
            lease = (
                "write_intent"
                if gates.get("write_intent_lease")
                else "dynamic_edit"
                if gates.get("edit_lease")
                else "none"
            )
            lines.append(
                f"- `{row.get('route_id')}`: `{row.get('gate_coverage_status')}`, "
                f"lease `{lease}`, gaps `{len(row.get('gate_gaps') or [])}`"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Remaining Systemic Mutation Gaps", ""])
    if gap_rows:
        for row in gap_rows:
            if not isinstance(row, Mapping):
                continue
            gaps = ", ".join(str(item) for item in row.get("gate_gaps", [])) or "none"
            lines.append(
                f"- `{row.get('branch_id')}.{row.get('route_id')}`: gaps `{gaps}`; "
                f"assessment `{row.get('assessment')}`; next `{row.get('recommended_next')}`"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Must Fix Before Serious Self-Evolution", ""])
    must_fix = payload.get("must_fix_before_serious_self_evolution")
    if isinstance(must_fix, list) and must_fix:
        for row in must_fix:
            if isinstance(row, Mapping):
                lines.append(f"- `{row.get('branch_id')}.{row.get('route_id')}`: `{row.get('gate_gaps')}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Non-Claims", ""])
    non_claims = systemic.get("non_claims") if isinstance(systemic.get("non_claims"), list) else []
    for item in non_claims:
        lines.append(f"- {item}")
    lines.append("- This matrix does not grant accepted-state, production, live-execution, or secrets authority.")
    return "\n".join(lines) + "\n"


def build_domain_weaver_route_handler_gate_contract(root: str | Path | None) -> dict[str, Any]:
    """Build a scoped read-only handler/write-set contract proof.

    This is narrower than full handler parity. It proves that the named Domain
    Weaver routes have registry fields, Branch Gateway gate declarations, and
    runtime handler entrypoints aligned with the candidate write-set contract.
    """

    shell_root = Path(root or ".").expanduser().resolve(strict=False)
    registry = _load_yaml(shell_root / REGISTRY_RELATIVE_PATH)
    routes = _domain_weaver_route_map(registry)
    runtime_handlers = _runtime_handler_names()
    rows = [
        _handler_contract_row(route_id, routes.get(route_id), runtime_handlers)
        for route_id in DOMAIN_WEAVER_HANDLER_CONTRACT_SCOPE
    ]
    blockers = sorted({
        blocker
        for row in rows
        for blocker in row.get("blockers", [])
        if str(blocker or "").strip()
    })
    mutating_rows = [row for row in rows if row.get("mutates_state")]
    aligned_mutating_rows = [row for row in mutating_rows if row.get("contract_status") == "aligned"]
    return {
        "schema_id": HANDLER_CONTRACT_SCHEMA_ID,
        "generated_at": _utc_now(),
        "active_root": str(shell_root),
        "registry_path": REGISTRY_RELATIVE_PATH.as_posix(),
        "policy": {
            "candidate_only": True,
            "handler_contract_scope": "domain_weaver_named_routes_only",
            "full_system_parity_proven": False,
            "no_queue_processing": True,
            "no_worker_start": True,
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
        "summary": {
            "route_count": len(rows),
            "mutating_route_count": len(mutating_rows),
            "aligned_mutating_route_count": len(aligned_mutating_rows),
            "contract_gap_count": len([row for row in rows if row.get("blockers")]),
            "handler_entrypoints_found_count": len([row for row in rows if row.get("handler_entrypoint_found")]),
        },
        "rows": rows,
        "blockers": blockers,
        "non_claims": [
            "This contract is scoped to named Domain Weaver routes only.",
            "It does not prove every runtime write path in the system.",
            "It does not process queues, start workers, or prove autonomous reaction.",
            "It does not grant accepted-state, production, live-execution, or secrets authority.",
        ],
    }


def write_domain_weaver_route_handler_gate_contract(root: str | Path | None) -> dict[str, Any]:
    shell_root = Path(root or ".").expanduser().resolve(strict=False)
    payload = build_domain_weaver_route_handler_gate_contract(shell_root)
    stamp = _timestamp_for_filename(str(payload["generated_at"]))
    output_dir = shell_root / DEFAULT_ROUTE_POLICY_DIR
    receipt_dir = shell_root / DEFAULT_OPERATOR_ACTION_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    receipt_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / HANDLER_CONTRACT_JSON_NAME
    report_path = output_dir / HANDLER_CONTRACT_REPORT_NAME
    receipt_path = receipt_dir / f"{stamp}_domain_weaver_route_handler_write_set_contract.json"
    _write_json(json_path, payload)
    report_path.write_text(_render_handler_contract_report(payload), encoding="utf-8")
    receipt = {
        "schema_id": "ion.domain_weaver.operator_action_receipt.v0_1",
        "receipt_type": "domain_weaver_route_handler_write_set_contract",
        "generated_at": payload["generated_at"],
        "result": "handler_write_set_contract_written_candidate_only",
        "active_root": str(shell_root),
        "artifacts": {
            "contract_json": _rel(json_path, shell_root),
            "contract_report": _rel(report_path, shell_root),
        },
        "summary": payload["summary"],
        "blockers": payload["blockers"],
        "policy": payload["policy"],
        "validation": [],
    }
    _write_json(receipt_path, receipt)
    return {
        "schema_id": HANDLER_CONTRACT_WRITE_RESULT_SCHEMA_ID,
        "generated_at": payload["generated_at"],
        "json_path": _rel(json_path, shell_root),
        "report_path": _rel(report_path, shell_root),
        "operator_receipt_path": _rel(receipt_path, shell_root),
        "mutates_active_state": False,
        "accepted_state_moved": False,
    }


def _handler_contract_row(
    route_id: str,
    route: Mapping[str, Any] | None,
    runtime_handlers: set[str],
) -> dict[str, Any]:
    expected = DOMAIN_WEAVER_HANDLER_CONTRACT_SCOPE[route_id]
    route = route if isinstance(route, Mapping) else None
    required_args = set()
    if route is not None:
        args_schema = route.get("args_schema") if isinstance(route.get("args_schema"), Mapping) else {}
        required_args = {
            str(item)
            for item in (args_schema.get("required") if isinstance(args_schema.get("required"), list) else [])
            if str(item or "").strip()
        }
    expected_required = set(expected.get("required_fields") or [])
    declared_required = {
        field
        for field in expected_required
        if route is not None and (
            field in required_args
            or (field == "confirmation" and bool(route.get("confirmation_required")))
            or (field == "idempotency_key" and bool(route.get("idempotency_required")))
            or (field == "agent_id" and bool(route.get("agent_id_required")))
            or (field == "write_intent_lease_id" and bool(route.get("write_intent_lease_id_required")))
            or (field == "lease_id" and bool(route.get("lease_id_required")))
            or (field == "lease_id" and bool(route.get("edit_lease_required")))
        )
    }
    required_target_roots = list(expected.get("required_target_roots") or [])
    declared_target_roots = [
        str(item)
        for item in (route.get("write_intent_required_target_roots") if route is not None and isinstance(route.get("write_intent_required_target_roots"), list) else [])
        if str(item or "").strip()
    ]
    expected_lease_target_path = str(expected.get("required_lease_target_path") or "").strip()
    lease_gate = route.get("lease_gate") if route is not None and isinstance(route.get("lease_gate"), Mapping) else {}
    declared_lease_target_path = str(lease_gate.get("target_path") or "").strip()
    handler_name = str(expected.get("handler_function") or "")
    blockers: list[str] = []
    if route is None:
        blockers.append("route_missing_from_registry")
    elif bool(route.get("mutates_state")) != bool(expected.get("mutates_state")):
        blockers.append("mutates_state_declaration_mismatch")
    if route is not None and str(route.get("local_handler") or "") != "runtime_services":
        blockers.append("runtime_services_handler_not_declared")
    if handler_name not in runtime_handlers:
        blockers.append("runtime_handler_entrypoint_missing")
    missing_fields = sorted(expected_required - declared_required)
    if missing_fields:
        blockers.append("required_mutation_fields_missing")
    missing_target_roots = sorted(set(required_target_roots) - set(declared_target_roots))
    if missing_target_roots:
        blockers.append("required_write_intent_target_roots_missing")
    if expected_lease_target_path and declared_lease_target_path != expected_lease_target_path:
        blockers.append("required_static_lease_target_path_missing")
    return {
        "branch_id": "domain_weaver_agents",
        "route_id": route_id,
        "mutates_state": bool(route.get("mutates_state")) if route is not None else None,
        "expected_mutates_state": bool(expected.get("mutates_state")),
        "local_handler": route.get("local_handler") if route is not None else None,
        "handler_function": handler_name,
        "handler_entrypoint_found": handler_name in runtime_handlers,
        "expected_write_set_class": expected.get("expected_write_set_class"),
        "expected_required_fields": sorted(expected_required),
        "declared_required_fields": sorted(declared_required),
        "missing_required_fields": missing_fields,
        "expected_required_target_roots": required_target_roots,
        "declared_required_target_roots": declared_target_roots,
        "missing_required_target_roots": missing_target_roots,
        "expected_lease_target_path": expected_lease_target_path,
        "declared_lease_target_path": declared_lease_target_path,
        "lease_target_path_ok": (
            True if not expected_lease_target_path else declared_lease_target_path == expected_lease_target_path
        ),
        "branch_gateway_enforcement": (
            "handler_dynamic_exclusive_write_lease_gate"
            if bool(expected.get("dynamic_exclusive_write_lease"))
            else "static_exclusive_write_lease_predelegation_gate"
            if bool(expected.get("static_exclusive_write_lease"))
            else "write_intent_lease_predelegation_gate"
            if bool(expected.get("mutates_state"))
            else "read_only_no_mutation_gate_required"
        ),
        "contract_status": "aligned" if not blockers else "gapped",
        "blockers": blockers,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def _domain_weaver_route_map(registry: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    for branch in registry.get("branches") if isinstance(registry.get("branches"), list) else []:
        if not isinstance(branch, Mapping) or branch.get("branch_id") != "domain_weaver_agents":
            continue
        routes = branch.get("routes") if isinstance(branch.get("routes"), list) else []
        return {
            str(route.get("route_id") or ""): route
            for route in routes
            if isinstance(route, Mapping)
        }
    return {}


def _runtime_handler_names() -> set[str]:
    from . import ion_runtime_service_control

    return {
        str(name.get("handler_function") or "")
        for name in DOMAIN_WEAVER_HANDLER_CONTRACT_SCOPE.values()
        if hasattr(ion_runtime_service_control, str(name.get("handler_function") or ""))
    }


def _render_handler_contract_report(payload: Mapping[str, Any]) -> str:
    summary = payload.get("summary") if isinstance(payload.get("summary"), Mapping) else {}
    lines = [
        "# Domain Weaver Action Route Handler Write-Set Contract",
        "",
        f"Generated: `{payload.get('generated_at')}`",
        "",
        "Authority: candidate-only. This report does not process queues, start workers, or move accepted state.",
        "",
        "## Summary",
        "",
        f"- scoped routes: `{summary.get('route_count')}`",
        f"- mutating routes: `{summary.get('mutating_route_count')}`",
        f"- aligned mutating routes: `{summary.get('aligned_mutating_route_count')}`",
        f"- contract gaps: `{summary.get('contract_gap_count')}`",
        "",
        "## Routes",
        "",
    ]
    rows = payload.get("rows") if isinstance(payload.get("rows"), list) else []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        lines.append(
            f"- `{row.get('route_id')}`: `{row.get('contract_status')}`, "
            f"handler `{row.get('handler_function')}`, write-set `{row.get('expected_write_set_class')}`"
        )
    lines.extend(["", "## Blockers", ""])
    blockers = payload.get("blockers") if isinstance(payload.get("blockers"), list) else []
    if blockers:
        for blocker in blockers:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Non-Claims", ""])
    non_claims = payload.get("non_claims") if isinstance(payload.get("non_claims"), list) else []
    for item in non_claims:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _timestamp_for_filename(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        parsed = datetime.now(timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _severity(branch_id: str, mutates: bool, gaps: list[str]) -> str:
    if not mutates:
        return "none"
    if branch_id == "domain_weaver_agents" and gaps:
        return "high"
    if branch_id in {"codex_queue", "agent_swarm"} and gaps:
        return "high"
    if gaps:
        return "medium"
    return "none"


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return dict(payload) if isinstance(payload, Mapping) else {}
