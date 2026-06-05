"""Pure Domain Weaver packet/template construction helpers.

This module is intentionally leaf-only. It builds in-memory dictionaries for
candidate packets and Codex work request templates without dispatching queues,
writing files, mutating registries, refreshing projections, or importing the
Domain Weaver monolith.
"""
from __future__ import annotations

import hashlib
from typing import Any, Mapping, Sequence

from .ion_domain_weaver_catalog import DOGFOOD_NEXT_PACKET_SCHEMA_ID
from .ion_domain_weaver_true_names import (
    AUTHORITY_CEILING as TRUE_NAME_AUTHORITY_CEILING,
    build_domain_identity,
    build_worker_identity,
    self_repair_routing_decision,
)


WORK_REQUEST_SCHEMA_ID = "ion.chatgpt_browser_connector_codex_work_request.v1"
SOURCE_SEAM_PACKET_SCHEMA_ID = "ion.domain_weaver.autonomous_source_seam_integrator_packet.v0_1_candidate"
SPECIALIST_DOMAIN_FORMATION_PACKET_SCHEMA_ID = "ion.domain_weaver.specialist_domain_formation_packet.v0_1_candidate"
DOMAIN_WEAVER_TARGET_ROOT_ID = "active_ion_control"
DOMAIN_WEAVER_MOVEMENT_CLASS = "ION_KERNEL_CONTROL_MOVEMENT"

DEFAULT_REQUESTED_AUTHORITY = {
    "source_edit_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "accepted_state_claim": False,
    "git_push_authority": False,
    "deletion_authority": False,
    "service_restart_authority": False,
}

DEFAULT_RETURN_CONTRACT_SECTIONS = (
    "### CONTEXT PROOF",
    "### TEMPLATE ACTION PROOF",
    "### VALIDATION",
    "### BLOCKERS",
    "### RECOMMENDED NEXT PACKET",
    "### ION OPERATIONAL POSTURE",
)

DEFAULT_FORBIDDEN_ACTIONS = (
    "queue dispatch/start execution",
    "materialization writes",
    "registry mutation",
    "operator action history mutation",
    "projection refresh/write functions",
    "live execution",
    "UI/topology movement",
    "secrets access",
    "production authority",
    "git push",
    "accepted-state claim",
    "worker return as product state",
)

DEFAULT_HOT_SAFETY_EXCEPTION_POLICY = {
    "policy": "reject_universal_spawn_rule",
    "domain_owned_repair_default_after_gates_green": True,
    "lead_local_patch_allowed_for_hot_safety": True,
    "lead_local_patch_requires_receipt": True,
    "lead_local_patch_requires_nemesis_followup": True,
    "worker_return_posture": "carrier_intake_not_product_state",
}

DEFAULT_SPECIALIST_DOMAIN_FORMATION_PROOF_REQUIREMENTS = (
    "active_root_proof_before_worker_start",
    "fresh_context_package_or_explicit_context_blocker",
    "true_name_role_tier_authority_ceiling_before_worker_start",
    "owned_path_scope_declared_before_write",
    "exclusive_write_or_artifact_lease_before_mutation",
    "worker_return_recorded_as_carrier_intake_not_product_state",
    "nemesis_review_before_materialization_or_registry_movement",
)


def _clean_string_list(values: Sequence[Any]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        cleaned.append(text)
        seen.add(text)
    return cleaned


def _jsonish_copy(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonish_copy(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonish_copy(item) for item in value]
    return value


def domain_weaver_objective_sha256(objective: str) -> str:
    """Return the stable objective hash used by Codex work request templates."""

    return hashlib.sha256(objective.encode("utf-8")).hexdigest()


def denied_domain_weaver_authority() -> dict[str, bool]:
    """Return the default no-production/no-live/no-accepted-state authority map."""

    return dict(DEFAULT_REQUESTED_AUTHORITY)


def domain_weaver_worker_identity(
    *,
    agent_role: str,
    domain_id: str,
    lane_id: str,
    callsign: str | None = None,
    domain_weaver_role_tier: str | None = None,
    rank: str | None = None,
) -> dict[str, Any]:
    """Build optional worker identity metadata for packet templates."""

    return build_worker_identity(
        role_id=agent_role,
        domain_id=domain_id,
        lane_ids=[lane_id] if lane_id else [],
        callsign=callsign,
        domain_weaver_role_tier=domain_weaver_role_tier or rank,
    )


def domain_weaver_domain_ownership(
    *,
    domain_id: str,
    owner_role: str,
    owned_paths: Sequence[Any] = (),
) -> dict[str, Any]:
    """Return candidate-only domain ownership metadata for packet templates."""

    return {
        "domain_id": domain_id,
        "owner_role": owner_role,
        "owned_paths": _clean_string_list(owned_paths),
        "ownership_posture": "candidate_domain_stewardship_metadata_not_registry_ownership",
        "canonical_state_owner": False,
        "authority_ceiling": dict(TRUE_NAME_AUTHORITY_CEILING),
    }


def domain_weaver_worker_relation_graph(
    *,
    packet_id: str,
    lane_id: str,
    domain_id: str,
    agent_role: str,
    fanin_target: str = "lead_codex",
    nemesis_required: bool = True,
) -> dict[str, Any]:
    """Return a minimal relation graph for a candidate Domain Weaver worker."""

    return {
        "packet_id": packet_id,
        "lane_id": lane_id,
        "domain_id": domain_id,
        "agent_role": agent_role,
        "edges": [
            {"from": "worker", "to": "packet", "relation": "executes_candidate_contract"},
            {"from": "worker", "to": "domain", "relation": "owns_candidate_discovery"},
            {"from": "worker", "to": "lane", "relation": "requires_fresh_active_context"},
            {"from": "worker", "to": fanin_target, "relation": "returns_to_fanin"},
        ],
        "nemesis_required": nemesis_required,
        "worker_return_posture": "carrier_intake_not_product_state",
    }


def domain_weaver_metadata_envelope(
    *,
    packet_id: str,
    lane_id: str,
    domain_id: str,
    agent_role: str,
    owned_paths: Sequence[Any] = (),
    callsign: str | None = None,
    domain_weaver_role_tier: str | None = None,
    rank: str | None = None,
    include_self_repair_routing: bool = False,
) -> dict[str, Any]:
    """Return optional candidate-only Domain Weaver identity metadata."""

    envelope = {
        "schema_id": "ion.domain_weaver.packet_identity_metadata.v0_1_candidate",
        "worker_identity": domain_weaver_worker_identity(
            agent_role=agent_role,
            domain_id=domain_id,
            lane_id=lane_id,
            callsign=callsign,
            domain_weaver_role_tier=domain_weaver_role_tier or rank,
        ),
        "domain_stewardship": domain_weaver_domain_ownership(
            domain_id=domain_id,
            owner_role=agent_role,
            owned_paths=owned_paths,
        ),
        "relation_graph": domain_weaver_worker_relation_graph(
            packet_id=packet_id,
            lane_id=lane_id,
            domain_id=domain_id,
            agent_role=agent_role,
        ),
        "lead_local_exception_policy": _jsonish_copy(DEFAULT_HOT_SAFETY_EXCEPTION_POLICY),
        "metadata_posture": "candidate_only_not_worker_start_gate",
    }
    if include_self_repair_routing:
        envelope["self_repair_routing"] = self_repair_routing_decision(
            domain_id=domain_id,
            change_paths=owned_paths,
            risk_class="normal",
            domain_worker_available=False,
        )
    return envelope


def build_specialist_domain_formation_packet_template(
    *,
    packet_id: str,
    created_at: str,
    domain_id: str,
    display_name: str,
    purpose: str,
    steward_role_id: str,
    lane_ids: Sequence[Any],
    required_context_reads: Sequence[Any],
    owned_paths: Sequence[Any] = (),
    candidate_worker_roles: Sequence[Any] = (),
    callsign: str | None = None,
    domain_weaver_role_tier: str = "R7_STEWARD",
    proof_requirements: Sequence[Any] = (),
    blockers: Sequence[Any] = (),
    forbidden_actions: Sequence[Any] = DEFAULT_FORBIDDEN_ACTIONS,
    include_self_repair_routing: bool = False,
    self_repair_return_gates: Mapping[str, bool] | None = None,
) -> dict[str, Any]:
    """Build a candidate-only packet for forming a specialist Domain Weaver domain.

    The packet is a planning/coordination artifact. It does not materialize a
    domain registry row, dispatch a worker, resume topology/UI, or claim
    accepted state.
    """

    lanes = _clean_string_list(lane_ids)
    paths = _clean_string_list(owned_paths)
    clean_blockers = _clean_string_list(blockers)
    all_proof_requirements = _clean_string_list(
        [*DEFAULT_SPECIALIST_DOMAIN_FORMATION_PROOF_REQUIREMENTS, *proof_requirements]
    )
    result: dict[str, Any] = {
        "schema_id": SPECIALIST_DOMAIN_FORMATION_PACKET_SCHEMA_ID,
        "packet_id": packet_id,
        "created_at": created_at,
        "domain_id": domain_id,
        "display_name": display_name,
        "purpose": purpose,
        "packet_posture": "candidate_only_not_registry_materialization",
        "status": "CANDIDATE_SPECIALIST_DOMAIN_FORMATION",
        "formation_ready": False,
        "binding_ready": False,
        "dispatch_ready": False,
        "materialization_ready": False,
        "registry_materialization_allowed": False,
        "topology_or_ui_resume_allowed": False,
        "authority_boundary": denied_domain_weaver_authority(),
        "lane_ids": lanes,
        "required_context_reads": _clean_string_list(required_context_reads),
        "owned_paths": paths,
        "candidate_worker_roles": _clean_string_list(candidate_worker_roles),
        "domain_identity": build_domain_identity(
            domain_id=domain_id,
            steward_role_id=steward_role_id,
            lane_ids=lanes,
        ),
        "steward_identity": domain_weaver_worker_identity(
            agent_role=steward_role_id,
            domain_id=domain_id,
            lane_id=lanes[0] if lanes else "",
            callsign=callsign,
            domain_weaver_role_tier=domain_weaver_role_tier,
        ),
        "domain_stewardship": domain_weaver_domain_ownership(
            domain_id=domain_id,
            owner_role=steward_role_id,
            owned_paths=paths,
        ),
        "required_proof_before_settlement": all_proof_requirements,
        "blockers": clean_blockers,
        "claim_precedence": [
            "source_code_and_receipts_before_worker_return",
            "lead_settlement_before_candidate_packet_claim",
            "operator_decision_before_registry_or_materialization_movement",
        ],
        "forbidden": _clean_string_list(forbidden_actions),
        "settlement_rule": "Fanin must settle to exactly one of active-root patch, next packet, blocker, or operator decision.",
        "worker_return_posture": "carrier_intake_not_product_state",
        "role_tier_policy": {
            "role_tier_is_not_rank": True,
            "role_tier_never_grants_production_live_secrets_or_accepted_state": True,
            "legacy_rank_input_is_compatibility_alias_only": True,
        },
    }
    if include_self_repair_routing:
        result["self_repair_routing"] = self_repair_routing_decision(
            domain_id=domain_id,
            change_paths=paths,
            risk_class="normal",
            domain_worker_available=False,
            return_gates=self_repair_return_gates,
        )
        result["self_repair_routing"]["included_only_by_explicit_request"] = True
    return result


def domain_weaver_root_envelope() -> dict[str, Any]:
    """Return the stable active-root movement envelope used by request templates."""

    return {
        "target_root_id": DOMAIN_WEAVER_TARGET_ROOT_ID,
        "movement_class": DOMAIN_WEAVER_MOVEMENT_CLASS,
        "root_relation": "active_ion_control_root",
        "requested_authority": denied_domain_weaver_authority(),
    }


def build_domain_weaver_codex_work_request_template(
    *,
    request_id: str,
    objective: str,
    requested_by: str,
    work_class: str,
    lane_id: str,
    route_family: str,
    request_kind: str,
    agent_role: str,
    required_context_reads: Sequence[Any],
    domain_id: str | None = None,
    callsign: str | None = None,
    rank: str | None = None,
    domain_weaver_role_tier: str | None = None,
    worker_identity: Mapping[str, Any] | None = None,
    domain_ownership: Mapping[str, Any] | None = None,
    relation_graph: Mapping[str, Any] | None = None,
    hot_safety_bypass_policy: Mapping[str, Any] | None = None,
    domain_weaver_metadata: Mapping[str, Any] | None = None,
    include_identity_metadata: bool = False,
    include_self_repair_routing: bool = False,
    supporting_roles: Sequence[Any] = (),
    return_contract_sections: Sequence[Any] = DEFAULT_RETURN_CONTRACT_SECTIONS,
    dedupe_key: str | None = None,
    idempotency_key: str | None = None,
    risk_level: str = "critical",
    requested_model: str = "gpt-5.5",
    requested_reasoning_effort: str = "xhigh",
    requested_service_tier: str = "fast",
    model_override_reason: str | None = None,
    payload_key: str | None = None,
    payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a deterministic candidate Codex work request template.

    The returned dictionary is a construction artifact only. It does not imply
    queue materialization, dispatch, live execution, or accepted-state movement.
    """

    override_reason = model_override_reason or f"{request_kind} requires high-integrity Domain Weaver review."
    owner_domain = str(domain_id or route_family or "").strip()
    result: dict[str, Any] = {
        "schema_id": WORK_REQUEST_SCHEMA_ID,
        "request_id": request_id,
        "objective": objective,
        "objective_sha256": domain_weaver_objective_sha256(objective),
        "dedupe_key": dedupe_key or f"domain_weaver:{request_kind}:{request_id}",
        "idempotency_key": idempotency_key or request_id.replace("_", "-"),
        "idempotency_source": "idempotency_key",
        "implicit_idempotency_key": False,
        "requested_by": requested_by,
        "status": "QUEUED_FOR_CODEX_CARRIER",
        "work_class": work_class,
        "lane_id": lane_id,
        "risk_level": risk_level,
        "route_family": route_family,
        "request_kind": request_kind,
        "agent_role": agent_role,
        "domain_id": owner_domain,
        "supporting_roles": _clean_string_list(supporting_roles),
        "target_root_id": DOMAIN_WEAVER_TARGET_ROOT_ID,
        "movement_class": DOMAIN_WEAVER_MOVEMENT_CLASS,
        "requested_model": requested_model,
        "requested_reasoning_effort": requested_reasoning_effort,
        "requested_service_tier": requested_service_tier,
        "codex_service_tier": requested_service_tier,
        "model_override_reason": override_reason,
        "codex_model_override": {
            "selected_model": requested_model,
            "selected_reasoning_effort": requested_reasoning_effort,
            "service_tier": requested_service_tier,
            "reason": override_reason,
        },
        "ai_movement_root_envelope": domain_weaver_root_envelope(),
        "requested_authority": denied_domain_weaver_authority(),
        "return_packet_paths": [],
        "latest_return_packet_path": None,
        "return_contract_sections": _clean_string_list(return_contract_sections),
        "required_context_reads": _clean_string_list(required_context_reads),
    }
    if include_identity_metadata or worker_identity or domain_ownership or relation_graph or hot_safety_bypass_policy or domain_weaver_metadata:
        metadata = _jsonish_copy(domain_weaver_metadata) if domain_weaver_metadata else domain_weaver_metadata_envelope(
            packet_id=request_id,
            lane_id=lane_id,
            domain_id=owner_domain,
            agent_role=agent_role,
            callsign=callsign,
            domain_weaver_role_tier=domain_weaver_role_tier or rank,
            include_self_repair_routing=include_self_repair_routing,
        )
        if worker_identity:
            metadata["worker_identity"] = _jsonish_copy(worker_identity)
        if domain_ownership:
            metadata["domain_stewardship"] = _jsonish_copy(domain_ownership)
        if relation_graph:
            metadata["relation_graph"] = _jsonish_copy(relation_graph)
        if hot_safety_bypass_policy:
            metadata["lead_local_exception_policy"] = _jsonish_copy(hot_safety_bypass_policy)
        result["domain_weaver_metadata"] = metadata
    if payload_key:
        result[payload_key] = _jsonish_copy(payload or {})
    return result


def build_domain_weaver_next_packet_candidate_template(
    *,
    packet_id: str,
    selected_domain: str,
    objective: str,
    why_this_next: str,
    required_context_reads: Sequence[Any],
    expected_changed_paths: Sequence[Any] = (),
    authority_boundary: Mapping[str, Any] | None = None,
    recommended_role: str = "role.steward",
    worker_identity: Mapping[str, Any] | None = None,
    domain_ownership: Mapping[str, Any] | None = None,
    relation_graph: Mapping[str, Any] | None = None,
    domain_weaver_metadata: Mapping[str, Any] | None = None,
    include_identity_metadata: bool = False,
) -> dict[str, Any]:
    """Build a deterministic candidate next-packet dictionary."""

    result = {
        "schema_id": DOGFOOD_NEXT_PACKET_SCHEMA_ID,
        "packet_id": packet_id,
        "selected_domain": selected_domain,
        "objective": objective,
        "why_this_next": why_this_next,
        "recommended_role": recommended_role,
        "required_context_reads": _clean_string_list(required_context_reads),
        "expected_changed_paths": _clean_string_list(expected_changed_paths),
        "authority_boundary": _jsonish_copy(authority_boundary or denied_domain_weaver_authority()),
    }
    if include_identity_metadata or worker_identity or domain_ownership or relation_graph or domain_weaver_metadata:
        metadata = _jsonish_copy(domain_weaver_metadata) if domain_weaver_metadata else domain_weaver_metadata_envelope(
            packet_id=packet_id,
            lane_id="",
            domain_id=selected_domain,
            agent_role=recommended_role,
            owned_paths=expected_changed_paths,
        )
        if worker_identity:
            metadata["worker_identity"] = _jsonish_copy(worker_identity)
        if domain_ownership:
            metadata["domain_stewardship"] = _jsonish_copy(domain_ownership)
        if relation_graph:
            metadata["relation_graph"] = _jsonish_copy(relation_graph)
        result["domain_weaver_metadata"] = metadata
    return result


def build_domain_weaver_source_seam_packet_template(
    *,
    packet_id: str,
    created_at: str,
    active_root: str,
    operator_lane: str,
    selected_domain: str,
    objective: str,
    why_this_next: str,
    candidate_worker_paths: Sequence[Any],
    allowed_actions: Sequence[Any],
    required_proof_before_settlement: Sequence[Any],
    lead_integrator_paths: Sequence[Any] = (),
    nemesis_paths: Sequence[Any] = (),
    forbidden_actions: Sequence[Any] = DEFAULT_FORBIDDEN_ACTIONS,
    settlement_rule: str = "Fanin must settle to exactly one of active-root patch, next packet, blocker, or operator decision.",
    worker_identity: Mapping[str, Any] | None = None,
    domain_ownership: Mapping[str, Any] | None = None,
    relation_graph: Mapping[str, Any] | None = None,
    hot_safety_bypass_policy: Mapping[str, Any] | None = None,
    domain_weaver_metadata: Mapping[str, Any] | None = None,
    include_identity_metadata: bool = False,
) -> dict[str, Any]:
    """Build a deterministic autonomous source-seam packet candidate."""

    result = {
        "schema_id": SOURCE_SEAM_PACKET_SCHEMA_ID,
        "packet_id": packet_id,
        "created_at": created_at,
        "active_root": active_root,
        "operator_lane": operator_lane,
        "selected_domain": selected_domain,
        "objective": objective,
        "why_this_next": why_this_next,
        "write_ownership": {
            "candidate_worker": _clean_string_list(candidate_worker_paths),
            "lead_integrator_after_fanin": _clean_string_list(lead_integrator_paths),
            "nemesis": _clean_string_list(nemesis_paths),
        },
        "allowed": _clean_string_list(allowed_actions),
        "forbidden": _clean_string_list(forbidden_actions),
        "required_proof_before_settlement": _clean_string_list(required_proof_before_settlement),
        "settlement_rule": settlement_rule,
    }
    if include_identity_metadata or worker_identity or domain_ownership or relation_graph or hot_safety_bypass_policy or domain_weaver_metadata:
        metadata = _jsonish_copy(domain_weaver_metadata) if domain_weaver_metadata else domain_weaver_metadata_envelope(
            packet_id=packet_id,
            lane_id=operator_lane,
            domain_id=selected_domain,
            agent_role="role.mason",
            owned_paths=candidate_worker_paths,
            domain_weaver_role_tier="R5_MASON",
        )
        if worker_identity:
            metadata["worker_identity"] = _jsonish_copy(worker_identity)
        if domain_ownership:
            metadata["domain_stewardship"] = _jsonish_copy(domain_ownership)
        if relation_graph:
            metadata["relation_graph"] = _jsonish_copy(relation_graph)
        if hot_safety_bypass_policy:
            metadata["lead_local_exception_policy"] = _jsonish_copy(hot_safety_bypass_policy)
        result["domain_weaver_metadata"] = metadata
    return result


__all__ = [
    "DEFAULT_FORBIDDEN_ACTIONS",
    "DEFAULT_HOT_SAFETY_EXCEPTION_POLICY",
    "DEFAULT_REQUESTED_AUTHORITY",
    "DEFAULT_RETURN_CONTRACT_SECTIONS",
    "DEFAULT_SPECIALIST_DOMAIN_FORMATION_PROOF_REQUIREMENTS",
    "DOMAIN_WEAVER_MOVEMENT_CLASS",
    "DOMAIN_WEAVER_TARGET_ROOT_ID",
    "SPECIALIST_DOMAIN_FORMATION_PACKET_SCHEMA_ID",
    "SOURCE_SEAM_PACKET_SCHEMA_ID",
    "WORK_REQUEST_SCHEMA_ID",
    "build_domain_weaver_codex_work_request_template",
    "build_domain_weaver_next_packet_candidate_template",
    "build_domain_weaver_source_seam_packet_template",
    "build_specialist_domain_formation_packet_template",
    "denied_domain_weaver_authority",
    "domain_weaver_domain_ownership",
    "domain_weaver_metadata_envelope",
    "domain_weaver_objective_sha256",
    "domain_weaver_root_envelope",
    "domain_weaver_worker_identity",
    "domain_weaver_worker_relation_graph",
]
