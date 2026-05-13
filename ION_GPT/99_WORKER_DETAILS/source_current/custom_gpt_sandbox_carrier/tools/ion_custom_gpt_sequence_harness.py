#!/usr/bin/env python3
"""Candidate harness for ION Custom GPT front-door carrier turn behavior.

This is not a runtime daemon. It is a small regression surface that makes the
Custom GPT contract testable: active sequence state must dominate freehand chat,
and every substantive return must pass through a persona return gate or emit a
structured continuation envelope.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Literal

SAFE_INTERRUPTS = {"STOP", "PAUSE", "CANCEL"}
TERMINAL_PHASE = "PERSONA_INTERFACE_RESPONSE"

BASELINE_PHASES = [
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


TurnClassification = Literal[
    "continue_active_sequence",
    "explicit_interrupt",
    "authority_boundary_change",
    "safety_or_policy_boundary",
    "context_required_interrupt",
]


@dataclass(frozen=True)
class CarrierSequenceState:
    active_objective: str
    active_workflow_object: str
    current_phase: str
    completed_phases: tuple[str, ...] = field(default_factory=tuple)
    pending_phases: tuple[str, ...] = field(default_factory=tuple)
    authority: str = "sandbox-candidate-write"


def classify_operator_turn(
    user_text: str,
    *,
    active_sequence_unfinished: bool,
    mentions_new_context_file: bool = False,
    authority_change_requested: bool = False,
    safety_boundary: bool = False,
) -> TurnClassification:
    """Classify a user turn without letting casual prose reset active ION work."""
    normalized = user_text.strip().upper()
    if normalized in SAFE_INTERRUPTS:
        return "explicit_interrupt"
    if authority_change_requested:
        return "authority_boundary_change"
    if safety_boundary:
        return "safety_or_policy_boundary"
    if mentions_new_context_file:
        return "context_required_interrupt"
    if active_sequence_unfinished:
        return "continue_active_sequence"
    return "continue_active_sequence"


def next_phase(state: CarrierSequenceState, phases: Iterable[str] = BASELINE_PHASES) -> str:
    phases = list(phases)
    if state.current_phase not in phases:
        raise ValueError(f"unknown current phase: {state.current_phase}")
    idx = phases.index(state.current_phase)
    return phases[min(idx + 1, len(phases) - 1)]


def build_continuation_envelope(state: CarrierSequenceState, blocker: str = "") -> dict:
    nxt = next_phase(state)
    pending = list(state.pending_phases) or BASELINE_PHASES[BASELINE_PHASES.index(nxt):]
    return {
        "ion_sequence_continuation": {
            "active_objective": state.active_objective,
            "active_workflow_object": state.active_workflow_object,
            "current_phase": state.current_phase,
            "completed_phases": list(state.completed_phases),
            "pending_phases": pending,
            "next_phase": nxt,
            "required_context_or_files": [],
            "blocker": blocker,
            "authority": state.authority,
            "exact_continuation_route_or_prompt": (
                f"Continue {state.active_workflow_object} from {nxt} and terminate at "
                "PERSONA_INTERFACE_RESPONSE or emit this continuation envelope again."
            ),
        }
    }


def persona_return_gate_passes(package: dict) -> bool:
    """Minimal schema-free check used by the candidate tests."""
    try:
        return bool(
            package["final_answer_gate"]["workflow_object_present"]
            and package["final_answer_gate"]["terminal_or_continuation"]
            and package["final_answer_gate"]["persona_return_gate_passed"]
            and package["relay_return"]["meaning_preserved"]
            and package["authority"]["production_authority"] is False
            and package["authority"]["live_execution_authority"] is False
        )
    except KeyError:
        return False

PROFILE_REGISTRY = {
    "ion_default": {
        "visible_name": "ION",
        "profile_status": "default",
        "gesture": "steady_boundary_hold",
    },
    "technical_plain": {
        "visible_name": "ION Technical Plain",
        "profile_status": "active_candidate",
        "gesture": "direct_open_hand",
    },
    "audit_repair": {
        "visible_name": "ION Audit Repair",
        "profile_status": "active_candidate",
        "gesture": "steady_boundary_hold",
    },
    "recovered_3po": {
        "visible_name": "ION 3PO Protocol Surface",
        "profile_status": "historical_evidence_candidate",
        "gesture": "careful_protocol_bow",
    },
    "recovered_connery_bond": {
        "visible_name": "ION Connery-Bond Surface",
        "profile_status": "historical_evidence_candidate",
        "gesture": "cool_measured_forward_lean",
    },
    "recovered_feynman_mex": {
        "visible_name": "ION Feynman-MEX Surface",
        "profile_status": "historical_evidence_candidate",
        "gesture": "explanatory_open_hand",
    },
}


def select_persona_profile(profile_id: str = "ion_default") -> dict:
    """Select a presentation-only profile. Profiles never grant authority."""
    profile = PROFILE_REGISTRY.get(profile_id, PROFILE_REGISTRY["ion_default"])
    result = dict(profile)
    result["selected_profile"] = profile_id if profile_id in PROFILE_REGISTRY else "ion_default"
    result["profiles_grant_authority"] = False
    return result


def build_boot_sequence_result(
    *,
    boot_id: str,
    objective: str,
    active_workflow_object: str = "BOOT_TO_PERSONA_INTERFACE_RESPONSE",
    ion_project_hash: str = "pending_build",
    project_hash_status: str = "pending_build",
    mounted_package_count: int = 0,
    phases_completed: Iterable[str] = BASELINE_PHASES,
    persona_return_gate: str = "pass",
) -> dict:
    return {
        "ion_boot_sequence_result": {
            "schema_id": "ion.boot_sequence_result.v1",
            "boot_id": boot_id,
            "route_id": "BOOT_TO_PERSONA_INTERFACE_RESPONSE",
            "ion_project_hash": ion_project_hash,
            "project_hash_status": project_hash_status,
            "mounted_packages": {
                "count": int(mounted_package_count),
                "posture": "candidate_context",
            },
            "objective": objective,
            "active_workflow_object": active_workflow_object,
            "phases_completed": list(phases_completed),
            "persona_return_gate": persona_return_gate,
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "receipt_status": "candidate_boot_receipt",
        }
    }


def build_persona_visible_envelope(
    *,
    route_id: str,
    profile_id: str = "ion_default",
    candidate_domains: Iterable[str] = (),
    candidate_agents: Iterable[str] = (),
    confidence_level: str = "scoped",
    confidence_semantic: str = "Scoped to mounted candidate context; AI output is not accepted state.",
    dynamic_domain_needed: bool = False,
) -> dict:
    profile = select_persona_profile(profile_id)
    return {
        "ion_persona": {
            "schema": "ion.persona_response_envelope.v0_1",
            "verdict": "ION_PERSONA_RESPONSE_ENVELOPE_READY",
            "persona": {
                "visible_name": profile["visible_name"],
                "role_ref": "role.persona_interface",
                "selected_profile": profile["selected_profile"],
                "profile_status": profile["profile_status"],
                "persona_is_total_ion": False,
            },
            "route": {
                "route_id": route_id,
                "selection_basis": "selected from Custom GPT front-door carrier package",
                "candidate_domains": list(candidate_domains),
                "candidate_agents": list(candidate_agents),
            },
            "dynamic_domain_signal": {
                "needed": bool(dynamic_domain_needed),
                "semantic": "Candidate domain expansion signal only; not accepted canon." if dynamic_domain_needed else "Selected route appears sufficient from mounted context.",
            },
            "confidence": {
                "level": confidence_level,
                "semantic": confidence_semantic,
            },
            "gesture": {
                "gesture": profile["gesture"],
                "semantic": "Symbolic response posture, not a body claim.",
            },
            "inner_monologue": {
                "type": "operator_visible_persona_signal_not_hidden_reasoning",
                "text": "I am rendering the result through the selected Persona profile with proof and authority boundaries visible.",
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
