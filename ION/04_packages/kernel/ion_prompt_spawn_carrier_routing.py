"""Resolve prompt-spawn execution carrier with unified CLI/model selection."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .ion_cli_model_selection import (
    ROUTING_RELATIVE_PATH,
    load_unified_routing,
    resolve_execution_selection,
    selection_status,
)

DEFAULT_LEADER_DOMAINS = frozenset(
    {
        "domain.runtime_carrier_and_action_admission",
        "domain.model_routing_and_reasoning_economics",
        "domain.domain_weaver_living_self_model",
        "domain.swarm_scale_scheduling_and_workload_economics",
        "domain.context_systems",
        "domain.durable_apply_and_substrate_custody",
        "domain.state_rank_and_receipt_truth",
        "domain.artifact_provenance_and_gate_legitimacy",
        "domain.agent_communication_and_settlement",
        "domain.honest_agency_validation",
    }
)


def load_carrier_routing(shell_root: Path) -> dict[str, Any]:
    return load_unified_routing(shell_root)


def resolve_carrier_for_domain(
    shell_root: Path,
    *,
    domain_id: str | None,
    carrier: str | None = None,
    requested_model: str | None = None,
    work_class: str | None = None,
    posture: str | None = None,
    execution_surface: str | None = "prompt_spawn",
) -> dict[str, Any]:
    """Return carrier_id, model, and fallback chain for a domain spawn."""

    selection = resolve_execution_selection(
        shell_root,
        domain_id=domain_id,
        carrier=carrier,
        requested_model=requested_model,
        work_class=work_class,
        posture=posture,
        execution_surface=execution_surface,
    )
    return {
        "schema_id": "ion.prompt_spawn_carrier_resolution.v2",
        "carrier_id": selection.get("carrier_id"),
        "reason": selection.get("reason"),
        "selection_reason": selection.get("selection_reason"),
        "domain_id": selection.get("domain_id"),
        "work_class": selection.get("work_class"),
        "requested_model": selection.get("requested_model"),
        "experimental_model": selection.get("experimental_model"),
        "experimental_model_explicit_only": selection.get(
            "experimental_model_explicit_only"
        ),
        "is_domain_leader": selection.get("is_domain_leader"),
        "model_tier": selection.get("model_tier"),
        "source_model_tier": selection.get("source_model_tier"),
        "model_tier_label": selection.get("model_tier_label"),
        "routing_path": ROUTING_RELATIVE_PATH.as_posix(),
        "routing_source_path": selection.get("routing_source_path"),
        "routing_source_sha256": selection.get("routing_source_sha256"),
        "routing_source_parity_ok": selection.get("routing_source_parity_ok"),
        "routing_decision_id": selection.get("routing_decision_id"),
        "routing_decision_sha256": selection.get("routing_decision_sha256"),
        "routing_request_basis": selection.get("routing_request_basis"),
        "routing_decision_basis": selection.get("routing_decision_basis"),
        "binary": selection.get("binary"),
        "default_model": selection.get("default_model"),
        "model": selection.get("model"),
        "model_env": selection.get("model_env"),
        "reasoning_effort": selection.get("reasoning_effort"),
        "selection_posture": selection.get("selection_posture"),
        "available": selection.get("available"),
        "policy_blocked": selection.get("policy_blocked"),
        "finding": selection.get("finding"),
        "tier_allowed_carriers": selection.get("tier_allowed_carriers"),
        "caller_allowed_carriers": selection.get("caller_allowed_carriers"),
        "effective_allowed_carriers": selection.get("effective_allowed_carriers"),
        "fallback_chain": selection.get("fallback_chain"),
        "ranked_candidates": selection.get("ranked_candidates"),
        "carrier_settings_pause": selection.get("carrier_settings_pause"),
        "carrier_settings_finding": selection.get("carrier_settings_finding"),
        "unified_selection": selection,
        "production_authority": False,
    }


def routing_status(shell_root: Path) -> dict[str, Any]:
    return selection_status(shell_root)
