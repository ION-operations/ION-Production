#!/usr/bin/env python3
"""Candidate helper for v4.2 Persona visible envelope and boot receipt.

This helper is intentionally deterministic and side-effect free so tests can
validate the visible-envelope contract without invoking live services.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


BOOT_PHASES = [
    "PERSONA_INTERFACE_INGRESS",
    "RELAY",
    "STEWARD",
    "VIZIER",
    "MASON",
    "NEMESIS_OR_VICE_REVIEW",
    "SCRIBE",
    "STEWARD_FINAL",
    "RELAY_RETURN_PACKAGE",
    "PERSONA_RETURN_GATE",
    "PERSONA_INTERFACE_RESPONSE",
]

PROFILE_STATUSES = {
    "ion_default": "default",
    "technical_plain": "active_candidate",
    "audit_repair": "active_candidate",
    "recovered_3po": "historical_evidence_candidate",
    "recovered_connery_bond": "historical_evidence_candidate",
    "recovered_feynman_mex": "historical_evidence_candidate",
}


def build_boot_receipt(
    boot_id: str,
    objective: str,
    mounted_count: int,
    route_id: str = "BOOT_TO_PERSONA_INTERFACE_RESPONSE",
) -> Dict[str, Any]:
    return {
        "ion_boot_sequence_result": {
            "schema_id": "ion.boot_sequence_result.v1",
            "boot_id": boot_id,
            "route_id": route_id,
            "mounted_packages": {"count": mounted_count, "posture": "candidate_context"},
            "objective": objective,
            "active_workflow_object": route_id,
            "phases_completed": BOOT_PHASES,
            "persona_return_gate": "pass",
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "receipt_status": "candidate_boot_receipt",
        }
    }


def select_profile(operator_signal: str = "", requested_profile: str | None = None) -> str:
    if requested_profile in PROFILE_STATUSES:
        return requested_profile
    low = operator_signal.lower()
    if "audit" in low or "repair" in low or "defect" in low:
        return "audit_repair"
    if "simple" in low or "explain" in low or "feynman" in low:
        return "recovered_feynman_mex"
    if "protocol" in low or "polite" in low or "3po" in low:
        return "recovered_3po"
    if "mission" in low or "bond" in low or "connery" in low:
        return "recovered_connery_bond"
    if "plain" in low or "technical" in low:
        return "technical_plain"
    return "ion_default"


def build_persona_envelope(
    route_id: str,
    selected_profile: str = "ion_default",
    candidate_domains: Iterable[str] | None = None,
    candidate_agents: Iterable[str] | None = None,
    dynamic_domain_needed: bool = False,
    confidence_level: str = "scoped",
) -> Dict[str, Any]:
    candidate_domains = list(candidate_domains or [])
    candidate_agents = list(candidate_agents or [])
    profile_status = PROFILE_STATUSES.get(selected_profile, "recovered_candidate")
    return {
        "ion_persona": {
            "schema": "ion.persona_response_envelope.v0_1",
            "verdict": "ION_PERSONA_RESPONSE_ENVELOPE_READY",
            "persona": {
                "visible_name": "ION" if selected_profile == "ion_default" else selected_profile,
                "role_ref": "role.persona_interface",
                "selected_profile": selected_profile,
                "profile_status": profile_status,
                "persona_is_total_ion": False,
            },
            "route": {
                "route_id": route_id,
                "selection_basis": "mounted_route_operator_signal_and_profile_registry",
                "candidate_domains": candidate_domains,
                "candidate_agents": candidate_agents,
            },
            "dynamic_domain_signal": {
                "needed": bool(dynamic_domain_needed),
                "semantic": "candidate domain expansion present" if dynamic_domain_needed else "no new domain pressure detected",
            },
            "confidence": {
                "level": confidence_level,
                "semantic": "bounded to mounted context, candidate artifacts, and declared authority",
            },
            "gesture": {
                "gesture": "measured_forward_lean",
                "semantic": "Symbolic response posture, not a body claim.",
            },
            "inner_monologue": {
                "type": "operator_visible_persona_signal_not_hidden_reasoning",
                "text": "Persona can render the bounded result while preserving proof and authority boundaries.",
                "not_claimed": [
                    "hidden_chain_of_thought",
                    "private_reasoning_transcript",
                    "lived_human_emotion",
                    "personal_consciousness",
                ],
            },
            "boundaries": {
                "output_is_not_state": True,
                "candidate_until_receipted_or_accepted": True,
                "production_authority": False,
                "live_execution_authority": False,
                "hidden_chain_of_thought_exposed": False,
            },
        }
    }
