"""Candidate true-name and role-tier helpers for Domain Weaver workers.

This module is projection-only. It does not materialize registry state, start
workers, grant authority, or claim accepted state. It gives Domain Weaver a
small vocabulary for naming peer workers and deciding when a domain-owned repair
packet should exist before code changes proceed.
"""
from __future__ import annotations

import re
from typing import Any, Iterable, Mapping

SCHEMA_ID = "ion.domain_weaver.true_names.v0_1_candidate"
CANONICAL_ROLE_TIER_LADDER_ID = "ion.domain_weaver.role_phase_tier_ladder.v0_3_candidate"
ION_SETTLEMENT_RANK_LADDER_ID = "ion.rank_authority_context_ladder"

TRUE_NAME_DOMAIN_ID = "domain.domain_weaver_true_name_system"
TRUE_NAME_ROLE_ID = "role.true_name_steward"

ROLE_PHASE_TIERS: dict[str, dict[str, Any]] = {
    "R0_PERSONA_INTERFACE": {
        "role_phase": "PERSONA_INTERFACE",
        "responsibility": "operator-facing synthesis",
        "can_patch_source": False,
    },
    "R1_RELAY": {
        "role_phase": "RELAY",
        "responsibility": "packetization and transport",
        "can_patch_source": False,
    },
    "R2_SCRIBE": {
        "role_phase": "SCRIBE",
        "responsibility": "receipts, documentation, and lineage",
        "can_patch_source": False,
    },
    "R3_CARTOGRAPHER": {
        "role_phase": "CARTOGRAPHER",
        "responsibility": "read-only topology, source, queue, context, and domain mapping",
        "can_patch_source": False,
    },
    "R4_NEMESIS": {
        "role_phase": "NEMESIS",
        "responsibility": "adversarial review and veto recommendation",
        "can_patch_source": False,
    },
    "R5_MASON": {
        "role_phase": "MASON",
        "responsibility": "bounded implementation in owned files under explicit packet scope",
        "can_patch_source": True,
    },
    "R6_VIZIER": {
        "role_phase": "VIZIER",
        "responsibility": "architecture, dependency, and implication review",
        "can_patch_source": False,
    },
    "R7_STEWARD": {
        "role_phase": "STEWARD",
        "responsibility": "fanout/fanin synthesis, blocker preservation, and settlement proposal",
        "can_patch_source": False,
    },
    "R8_STEWARD_FINAL": {
        "role_phase": "STEWARD_FINAL",
        "responsibility": "final settlement into patch, next packet, blocker, or operator decision",
        "can_patch_source": True,
    },
}

ROLE_TIER_HINTS = (
    ("persona_interface", "R0_PERSONA_INTERFACE"),
    ("relay", "R1_RELAY"),
    ("scribe", "R2_SCRIBE"),
    ("cartographer", "R3_CARTOGRAPHER"),
    ("atlas", "R3_CARTOGRAPHER"),
    ("auditor", "R3_CARTOGRAPHER"),
    ("nemesis", "R4_NEMESIS"),
    ("vice", "R4_NEMESIS"),
    ("mason", "R5_MASON"),
    ("builder", "R5_MASON"),
    ("vizier", "R6_VIZIER"),
    ("architect", "R6_VIZIER"),
    ("steward", "R7_STEWARD"),
)

AUTHORITY_CEILING = {
    "accepted_state": False,
    "production": False,
    "live_execution": False,
    "secrets": False,
    "git_push": False,
    "registry_materialization": False,
}

LEAD_LOCAL_PATCH_EXCEPTIONS = (
    "hot_safety_gate",
    "false_proof_or_false_readiness",
    "worker_start_bypass",
    "mutation_without_lease",
    "context_capsule_identity_drift",
    "tooling_bootstrap_before_domain_exists",
)

RETURN_TO_DOMAIN_OWNED_REPAIR_GATES = (
    "context_freshness",
    "owner_binding",
    "worker_start_ready",
    "mutation_lease",
    "queue_route",
    "fanout_fanin",
    "coverage",
    "authority_nonclaim",
)

DOMAIN_AFFINITY_CALLSIGN_POOLS: dict[str, tuple[str, ...]] = {
    "stewardship": (
        "Confucius",
        "Ashoka",
        "Mandela",
        "Hammurabi",
        "Eleanor",
    ),
    "context": (
        "Goodall",
        "Linnaeus",
        "Humboldt",
        "Mendeleev",
        "Sappho",
    ),
    "proof_graph": (
        "Euclid",
        "Noether",
        "Godel",
        "Tarski",
        "Hypatia",
    ),
    "nemesis": (
        "Popper",
        "Sartre",
        "Arendt",
        "Diogenes",
        "Kierkegaard",
    ),
    "implementation": (
        "Archimedes",
        "Lovelace",
        "Turing",
        "Hamilton",
        "Hopper",
    ),
    "systems": (
        "Newton",
        "Lagrange",
        "Maxwell",
        "Curie",
        "Volta",
    ),
    "ethics": (
        "Parfit",
        "DuBois",
        "Nussbaum",
        "Sen",
        "hooks",
    ),
    "ecology": (
        "Darwin",
        "Carson",
        "Odum",
        "Lovelock",
        "Pasteur",
    ),
    "queue_fanin": (
        "Nash",
        "Erdos",
        "Shannon",
        "Knuth",
        "Dijkstra",
    ),
    "topology": (
        "Euler",
        "Riemann",
        "Cantor",
        "Poincare",
        "Noether",
    ),
    "visual_proof": (
        "Kandinsky",
        "Albers",
        "Tufte",
        "Bauhaus",
        "Miyazaki",
    ),
    "lease_governance": (
        "Hobbes",
        "Locke",
        "Bentham",
        "Ostrom",
        "Averroes",
    ),
}

NEUTRAL_CALLSIGN_POOL = (
    "Aster",
    "Beacon",
    "Cedar",
    "Delta",
    "Ember",
    "Forge",
    "Harbor",
    "Ion",
    "Juniper",
    "Keystone",
    "Lumen",
    "Northstar",
)

DOMAIN_AFFINITY_KEYWORDS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("steward", "settlement", "lead", "governance"), "stewardship"),
    (("context", "capsule", "resolver", "memory", "continuity"), "context"),
    (("proof", "receipt", "graph", "binding", "materialization"), "proof_graph"),
    (("nemesis", "audit", "red_team", "critique", "forgery"), "nemesis"),
    (("mason", "builder", "implementation", "patch", "source"), "implementation"),
    (("system", "kernel", "architecture", "control_plane"), "systems"),
    (("ethic", "authority", "boundary", "nonclaim"), "ethics"),
    (("ecology", "domain", "weaver", "evolution", "fission"), "ecology"),
    (("queue", "fanin", "fanout", "scheduler", "dedupe"), "queue_fanin"),
    (("topology", "map", "cartography", "graph"), "topology"),
    (("visual", "ui", "operator", "quality"), "visual_proof"),
    (("lease", "worker_shift", "lock", "handoff"), "lease_governance"),
)

TRUE_NAME_RELATION_EDGE_TYPES = (
    "reports_to",
    "reviews",
    "blocks",
    "hands_off_to",
    "depends_on",
    "settles",
    "supersedes",
    "lineage_parent",
)

CANONICAL_ROLE_TIER_SEQUENCE = tuple(ROLE_PHASE_TIERS.keys())

TRUE_NAME_BINDING_REQUIRED_FIELDS = (
    "true_name",
    "callsign",
    "domain_weaver_role_tier",
    "role_tier_ladder_id",
    "tier_scope",
    "role_id",
    "domain_id",
    "packet_id",
    "domain_affinity",
    "lane_ids",
    "authority_ceiling",
    "worker_return_posture",
)

CALLSIGN_TRUE_NAME_SEPARATION_POLICY = {
    "callsign_is_human_continuity_only": True,
    "callsign_is_never_binding_identity": True,
    "true_name_must_not_equal_callsign": True,
    "true_name_must_be_role_domain_packet_derived_or_explicitly_bound": True,
    "role_tier_never_grants_authority": True,
}

LEAD_STEWARD_SEPARATION_POLICY = {
    "lead_codex_is_current_settlement_carrier": True,
    "domain_steward_is_domain_owner_or_reviewer_when_spawned": True,
    "lead_can_settle_worker_returns": True,
    "worker_role_tier_does_not_override_lead_settlement": True,
    "lead_local_patch_exception_requires_receipt": True,
    "lead_local_patch_exception_requires_followup_nemesis_or_domain_review": True,
}

ROUTE_BEFORE_PATCH_EXECUTABILITY_POLICY = {
    "route_before_patch_is_target_protocol": True,
    "route_before_patch_is_not_claimed_executable_until_context_and_lease_gates_green": True,
    "bootstrap_safety_repairs_may_be_lead_local_with_receipt": True,
    "bootstrap_safety_repairs_do_not_prove_full_self_repair_autonomy": True,
}

TRUE_NAME_BINDING_READINESS_REQUIRED_FIELDS = (
    "folder_domain_id",
    "context_package_id",
    "allowed_path_scopes",
    "expected_receipts",
    "lifecycle_state",
)

CALLSIGN_THEME_POLICY = {
    "default_mode": "neutral_symbolic_id",
    "historical_person_callsigns_require_operator_theme_approval": True,
    "collision_policy_required": True,
    "retirement_policy_required": True,
    "cultural_bias_review_required": True,
    "callsign_is_never_authority_identity_or_endorsement": True,
}


def _clean_token(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = text.replace("role.", "").replace("domain.", "")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def _true_name(*parts: Any) -> str:
    tokens = [_clean_token(part) for part in parts if _clean_token(part)]
    return "_".join(tokens).upper() or "UNNAMED_DOMAIN_WEAVER_WORKER"


def role_tier_for_role(role_id: str, *, fallback: str = "R3_CARTOGRAPHER") -> str:
    role = _clean_token(role_id)
    for needle, role_tier in ROLE_TIER_HINTS:
        if needle in role:
            return role_tier
    return fallback


def domain_affinity_for_identity(*, domain_id: str = "", role_id: str = "", packet_id: str = "") -> str:
    text = " ".join(_clean_token(value) for value in (domain_id, role_id, packet_id))
    for needles, affinity in DOMAIN_AFFINITY_KEYWORDS:
        if any(needle in text for needle in needles):
            return affinity
    return "systems"


def callsign_pool_for_affinity(
    affinity: str,
    *,
    limit: int | None = None,
    historical_theme_approved: bool = False,
) -> list[str]:
    if historical_theme_approved:
        pool = list(DOMAIN_AFFINITY_CALLSIGN_POOLS.get(_clean_token(affinity), DOMAIN_AFFINITY_CALLSIGN_POOLS["systems"]))
    else:
        pool = list(NEUTRAL_CALLSIGN_POOL)
    if limit is not None and limit >= 0:
        return pool[:limit]
    return pool


def callsign_pool_for_identity(
    *,
    domain_id: str = "",
    role_id: str = "",
    packet_id: str = "",
    limit: int | None = None,
    historical_theme_approved: bool = False,
) -> dict[str, Any]:
    affinity = domain_affinity_for_identity(domain_id=domain_id, role_id=role_id, packet_id=packet_id)
    return {
        "schema_id": SCHEMA_ID,
        "affinity": affinity,
        "domain_id": domain_id,
        "role_id": role_id,
        "packet_id": packet_id,
        "candidate_callsigns": callsign_pool_for_affinity(
            affinity,
            limit=limit,
            historical_theme_approved=historical_theme_approved,
        ),
        "historical_theme_candidate_callsigns": callsign_pool_for_affinity(
            affinity,
            limit=limit,
            historical_theme_approved=True,
        ),
        "callsign_policy": {
            "callsign_is_human_continuity_only": True,
            "callsign_is_not_authority": True,
            "avoid_collision_in_active_peer_wave": True,
            "allow_retirement_and_aliases_with_receipt": True,
            "theme_policy": dict(CALLSIGN_THEME_POLICY),
            "bias_guardrail": "Prefer domain-relevant diversity over popularity; names do not imply endorsement, identity, or authority.",
        },
        "authority_ceiling": dict(AUTHORITY_CEILING),
    }


def build_relation_edge(
    *,
    edge_type: str,
    source_true_name: str,
    target_true_name: str,
    evidence_path: str = "",
) -> dict[str, Any]:
    clean_edge = _clean_token(edge_type)
    return {
        "edge_type": clean_edge if clean_edge in TRUE_NAME_RELATION_EDGE_TYPES else "depends_on",
        "source_true_name": str(source_true_name or "").strip(),
        "target_true_name": str(target_true_name or "").strip(),
        "evidence_path": str(evidence_path or "").strip(),
        "authority_ceiling": dict(AUTHORITY_CEILING),
    }


def build_true_name_binding(
    *,
    true_name: str,
    callsign: str | None,
    role_id: str,
    domain_id: str,
    role_tier: str = "",
    packet_id: str = "",
    lane_ids: Iterable[str] | None = None,
    domain_affinity: str = "",
    folder_domain_id: str = "",
    context_package_id: str = "",
    allowed_path_scopes: Iterable[str] | None = None,
    expected_receipts: Iterable[str] | None = None,
    lifecycle_state: str = "",
) -> dict[str, Any]:
    clean_true_name = str(true_name or "").strip()
    clean_callsign = str(callsign or "").strip()
    selected_role_tier = role_tier if role_tier in ROLE_PHASE_TIERS else role_tier_for_role(role_id)
    lanes = [str(lane).strip() for lane in (lane_ids or []) if str(lane).strip()]
    scopes = [str(scope).strip() for scope in (allowed_path_scopes or []) if str(scope).strip()]
    receipts = [str(receipt).strip() for receipt in (expected_receipts or []) if str(receipt).strip()]
    affinity = domain_affinity or domain_affinity_for_identity(
        domain_id=domain_id,
        role_id=role_id,
        packet_id=packet_id,
    )
    blockers: list[str] = []
    if not clean_true_name:
        blockers.append("true_name_required")
    if clean_callsign and _clean_token(clean_true_name) == _clean_token(clean_callsign):
        blockers.append("callsign_must_not_be_used_as_true_name")
    if selected_role_tier not in ROLE_PHASE_TIERS:
        blockers.append("role_tier_not_in_canonical_ladder")
    if not str(role_id or "").strip():
        blockers.append("role_id_required_for_true_name_binding")
    if not str(domain_id or "").strip():
        blockers.append("domain_id_required_for_true_name_binding")
    if not lanes:
        blockers.append("lane_ids_required_for_true_name_binding")
    binding_ready_blockers = []
    if not str(folder_domain_id or "").strip():
        binding_ready_blockers.append("folder_domain_id_required_for_ion_true_name_binding")
    if not str(context_package_id or "").strip():
        binding_ready_blockers.append("context_package_id_required_for_ion_true_name_binding")
    if not scopes:
        binding_ready_blockers.append("allowed_path_scopes_required_for_ion_true_name_binding")
    if not receipts:
        binding_ready_blockers.append("expected_receipts_required_for_ion_true_name_binding")
    if not str(lifecycle_state or "").strip():
        binding_ready_blockers.append("lifecycle_state_required_for_ion_true_name_binding")
    return {
        "schema_id": "ion.domain_weaver.candidate_identity_metadata.v0_2_candidate",
        "ok": not blockers,
        "binding_ready": False,
        "true_name": clean_true_name,
        "callsign": clean_callsign or None,
        "domain_weaver_role_tier": selected_role_tier,
        "role_phase_tier": selected_role_tier,
        "role_tier_ladder_id": CANONICAL_ROLE_TIER_LADDER_ID,
        "ion_settlement_rank": None,
        "ion_settlement_rank_ladder_id": ION_SETTLEMENT_RANK_LADDER_ID,
        "ion_settlement_rank_field_reserved": True,
        "tier_scope": "packet_and_domain_scoped_responsibility_tier",
        "role_id": role_id,
        "domain_id": domain_id,
        "packet_id": packet_id,
        "domain_affinity": affinity,
        "lane_ids": lanes,
        "folder_domain_id": str(folder_domain_id or "").strip() or None,
        "context_package_id": str(context_package_id or "").strip() or None,
        "allowed_path_scopes": scopes,
        "expected_receipts": receipts,
        "lifecycle_state": str(lifecycle_state or "").strip() or None,
        "authority_ceiling": dict(AUTHORITY_CEILING),
        "worker_return_posture": "carrier_intake_not_product_state",
        "required_fields": list(TRUE_NAME_BINDING_REQUIRED_FIELDS),
        "binding_ready_required_fields": list(TRUE_NAME_BINDING_READINESS_REQUIRED_FIELDS),
        "blockers": blockers,
        "binding_ready_blockers": binding_ready_blockers,
        "policies": {
            "callsign_true_name_separation": dict(CALLSIGN_TRUE_NAME_SEPARATION_POLICY),
            "lead_steward_separation": dict(LEAD_STEWARD_SEPARATION_POLICY),
            "route_before_patch_executability": dict(ROUTE_BEFORE_PATCH_EXECUTABILITY_POLICY),
            "callsign_theme": dict(CALLSIGN_THEME_POLICY),
        },
    }


def build_worker_identity(
    *,
    role_id: str,
    domain_id: str = "",
    lane_ids: Iterable[str] | None = None,
    callsign: str | None = None,
    domain_weaver_role_tier: str | None = None,
    true_name: str | None = None,
    packet_id: str = "",
    lineage: Iterable[str] | None = None,
    relation_edges: Iterable[Mapping[str, Any]] | None = None,
    historical_theme_approved: bool = False,
) -> dict[str, Any]:
    selected_role_tier = domain_weaver_role_tier if domain_weaver_role_tier in ROLE_PHASE_TIERS else role_tier_for_role(role_id)
    tier_record = ROLE_PHASE_TIERS[selected_role_tier]
    lanes = [str(lane).strip() for lane in (lane_ids or []) if str(lane).strip()]
    affinity = domain_affinity_for_identity(domain_id=domain_id, role_id=role_id, packet_id=packet_id)
    lineage_rows = [str(item).strip() for item in (lineage or []) if str(item).strip()]
    edges = [dict(edge) for edge in (relation_edges or []) if isinstance(edge, Mapping)]
    selected_true_name = true_name or _true_name(domain_id, role_id, tier_record["role_phase"])
    binding = build_true_name_binding(
        true_name=selected_true_name,
        callsign=callsign,
        role_tier=selected_role_tier,
        role_id=role_id,
        domain_id=domain_id,
        packet_id=packet_id,
        lane_ids=lanes,
        domain_affinity=affinity,
    )
    return {
        "schema_id": SCHEMA_ID,
        "true_name": selected_true_name,
        "callsign": callsign,
        "callsign_pool": callsign_pool_for_affinity(
            affinity,
            limit=5,
            historical_theme_approved=historical_theme_approved,
        ),
        "historical_theme_callsign_pool": callsign_pool_for_affinity(
            affinity,
            limit=5,
            historical_theme_approved=True,
        ),
        "domain_weaver_role_tier": selected_role_tier,
        "role_phase_tier": selected_role_tier,
        "role_tier_ladder_id": CANONICAL_ROLE_TIER_LADDER_ID,
        "canonical_role_tier_sequence": list(CANONICAL_ROLE_TIER_SEQUENCE),
        "ion_settlement_rank": None,
        "ion_settlement_rank_ladder_id": ION_SETTLEMENT_RANK_LADDER_ID,
        "ion_settlement_rank_field_reserved": True,
        "tier_scope": "packet_and_domain_scoped_responsibility_tier",
        "role_phase": tier_record["role_phase"],
        "role_id": role_id,
        "domain_id": domain_id,
        "packet_id": packet_id,
        "domain_affinity": affinity,
        "lane_ids": lanes,
        "lineage": lineage_rows,
        "relation_edges": edges,
        "responsibility": tier_record["responsibility"],
        "authority_ceiling": dict(AUTHORITY_CEILING),
        "candidate_identity_metadata": binding,
        "true_name_binding": binding,
        "binding_ready": False,
        "binding_blockers": list(binding.get("blockers") or []),
        "binding_ready_blockers": list(binding.get("binding_ready_blockers") or []),
        "role_tier_policy": {
            "domain_weaver_role_tier_is_not_model_quality": True,
            "domain_weaver_role_tier_never_grants_production_live_secrets_or_accepted_state": True,
            "domain_weaver_role_tier_only_limits_claims_and_required_review": True,
            "ion_settlement_rank_field_reserved": True,
            "canonical_role_tier_ladder_id": CANONICAL_ROLE_TIER_LADDER_ID,
        },
        "callsign_policy": dict(CALLSIGN_TRUE_NAME_SEPARATION_POLICY),
        "callsign_theme_policy": dict(CALLSIGN_THEME_POLICY),
        "lead_steward_separation_policy": dict(LEAD_STEWARD_SEPARATION_POLICY),
        "worker_return_posture": "carrier_intake_not_product_state",
        "source_patch_capability_class": "eligible_only_with_separate_packet_authority_and_lease"
        if tier_record["can_patch_source"]
        else "not_source_patch_capable",
    }


def build_domain_identity(
    *,
    domain_id: str,
    steward_role_id: str = "",
    lane_ids: Iterable[str] | None = None,
    true_name: str | None = None,
) -> dict[str, Any]:
    lanes = [str(lane).strip() for lane in (lane_ids or []) if str(lane).strip()]
    return {
        "schema_id": SCHEMA_ID,
        "true_name": true_name or _true_name(domain_id, "domain"),
        "domain_id": domain_id,
        "steward_role_id": steward_role_id,
        "lane_ids": lanes,
        "authority_ceiling": dict(AUTHORITY_CEILING),
        "materialization_posture": "candidate_projection_only",
    }


def true_name_candidate_domain_row() -> dict[str, Any]:
    return {
        "domain_id": TRUE_NAME_DOMAIN_ID,
        "display_name": "Domain Weaver True Name System",
        "purpose": "Assign stable true names, callsigns, role tiers, authority ceilings, and relationship posture to Domain Weaver peer workers before domain-owned repair.",
        "paths": [
            "ION/04_packages/kernel/ion_domain_weaver_true_names.py",
            "ION/05_context/current/domain_weaver/stewarded_autonomy/DOMAIN_WEAVER_TRUE_NAMES_AND_RANKS_CANDIDATE_ENVELOPE_20260603T211100Z.md",
        ],
        "parent": "domain.domain_weaver",
        "children": [],
        "sibling_dependency_edges": [
            "domain.context_active_resolver",
            "domain.worker_shift_presence",
            "domain.domain_weaver",
        ],
        "fact_posture": "candidate_projection_source_repair",
        "maturity_estimate": "candidate_projection_only",
        "suggested_steward_class": "TRUE_NAME_STEWARD",
        "local_read_first_files": [
            "ION/04_packages/kernel/ion_domain_weaver_true_names.py",
            "ION/05_context/current/domain_weaver/stewarded_autonomy/DOMAIN_WEAVER_TRUE_NAMES_AND_RANKS_CANDIDATE_ENVELOPE_20260603T211100Z.md",
        ],
        "blockers": [],
        "ready_for_future_steward_discovery_packet": False,
        "requires_split_merge_review": False,
        "source_registry": "ION/04_packages/kernel/ion_domain_weaver_true_names.py#true_name_candidate_domain_row",
        "lane_ids": ["context_lane", "architecture_lane", "settlement_lane"],
        "lane_metadata": [
            {"lane_id": "context_lane", "source": "domain_weaver_true_name_system"},
            {"lane_id": "architecture_lane", "source": "domain_weaver_true_name_system"},
            {"lane_id": "settlement_lane", "source": "domain_weaver_true_name_system"},
        ],
        "lane_metadata_policy": {
            "explicit_lane_metadata_only": True,
            "missing_lane_metadata_blocks_lane_bound_worker_start": True,
            "no_silent_fallback_to_domain_or_role_match": True,
        },
        "domain_identity": build_domain_identity(
            domain_id=TRUE_NAME_DOMAIN_ID,
            steward_role_id=TRUE_NAME_ROLE_ID,
            lane_ids=["context_lane", "architecture_lane", "settlement_lane"],
            true_name="DOMAIN_WEAVER_TRUE_NAME_SYSTEM",
        ),
    }


def true_name_candidate_agent_row() -> dict[str, Any]:
    identity = build_worker_identity(
        role_id=TRUE_NAME_ROLE_ID,
        domain_id=TRUE_NAME_DOMAIN_ID,
        lane_ids=["context_lane", "architecture_lane", "settlement_lane"],
        domain_weaver_role_tier="R7_STEWARD",
        true_name="DOMAIN_WEAVER_TRUE_NAME_STEWARD",
    )
    return {
        "agent_id": TRUE_NAME_ROLE_ID,
        "role_id": TRUE_NAME_ROLE_ID,
        "display_name": "True Name Steward",
        "invocable": False,
        "backend_carrier_id": "codex_cli",
        "context_system_card": "ION/05_context/current/domain_weaver/stewarded_autonomy/DOMAIN_WEAVER_TRUE_NAMES_AND_RANKS_CANDIDATE_ENVELOPE_20260603T211100Z.md",
        "context_system_status": "candidate_projection_source_repair",
        "package_strategy": "active_context_package",
        "default_active_package_class": "true_name_role_tier_doctrine",
        "registry_primary_domain": TRUE_NAME_DOMAIN_ID,
        "registry_secondary_domains": [],
        "lane_ids": list(identity["lane_ids"]),
        "lane_metadata": [
            {"lane_id": lane_id, "source": "domain_weaver_true_name_system"}
            for lane_id in identity["lane_ids"]
        ],
        "lane_metadata_policy": {
            "explicit_lane_metadata_only": True,
            "missing_lane_metadata_blocks_lane_bound_worker_start": True,
            "no_silent_fallback_to_domain_or_role_match": True,
        },
        "worker_identity": identity,
        "role_domain_label": "Domain Weaver True Name System",
        "continuity_home": "ION/05_context/current/domain_weaver/stewarded_autonomy",
        "default_mount_posture": "candidate_context_mount_only",
        "context_paths": [
            "ION/04_packages/kernel/ion_domain_weaver_true_names.py",
            "ION/05_context/current/domain_weaver/stewarded_autonomy/DOMAIN_WEAVER_TRUE_NAMES_AND_RANKS_CANDIDATE_ENVELOPE_20260603T211100Z.md",
        ],
        "missing_declared_context_paths": [],
        "missing_legacy_context_paths": [],
        "legacy_context_missing_is_blocking": False,
        "primary_templates": [],
        "write_posture": "read_only_projection",
        "default_read_zones": ["ION/05_context/current/domain_weaver"],
        "default_proof_obligations": ["true_name_role_tier_authority_ceiling_before_worker_start"],
        "recent_invocations": [],
        "actions": {
            "prepare": True,
            "start": False,
            "cancel": True,
            "open_result": True,
            "open_evidence": True,
            "copy_launch_packet": True,
        },
        "production_authority": False,
        "live_execution_authority": False,
    }


def self_repair_routing_decision(
    *,
    domain_id: str,
    change_paths: Iterable[str],
    risk_class: str = "normal",
    domain_worker_available: bool = False,
    return_gates: Mapping[str, bool] | None = None,
) -> dict[str, Any]:
    paths = [str(path).strip() for path in change_paths if str(path).strip()]
    hot_safety = risk_class in LEAD_LOCAL_PATCH_EXCEPTIONS
    gate_state = {
        gate: bool((return_gates or {}).get(gate))
        for gate in RETURN_TO_DOMAIN_OWNED_REPAIR_GATES
    }
    gates_green = all(gate_state.values())
    if hot_safety:
        decision = "lead_local_patch_allowed_with_receipt_and_nemesis_followup"
    elif domain_worker_available and gates_green:
        decision = "route_to_domain_true_name_worker_before_patch"
    elif domain_worker_available:
        decision = "block_domain_owned_repair_until_return_gates_green"
    else:
        decision = "create_domain_true_name_worker_packet_before_patch"
    return {
        "schema_id": SCHEMA_ID,
        "policy": "reject_universal_spawn_rule",
        "domain_id": domain_id,
        "change_paths": paths,
        "risk_class": risk_class,
        "domain_worker_available": domain_worker_available,
        "return_to_domain_owned_repair_gates": gate_state,
        "return_to_domain_owned_repair_ready": gates_green,
        "decision": decision,
        "lead_local_patch_exception": hot_safety,
        "lead_local_patch_exception_requires_followup": hot_safety,
        "authority_ceiling": dict(AUTHORITY_CEILING),
        "settlement_required": True,
    }
