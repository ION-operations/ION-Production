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
