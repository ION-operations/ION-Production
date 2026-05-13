#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[5]

def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")

def load_yaml(rel: str):
    return yaml.safe_load(read(rel))

def load_json(rel: str):
    return json.loads(read(rel))

def load_harness():
    path = ROOT / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/tools/ion_custom_gpt_sequence_harness.py"
    spec = importlib.util.spec_from_file_location("ion_custom_gpt_sequence_harness", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def test_instructions_bind_product_contract():
    for rel in [
        "ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md",
        "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/instructions/ION_CUSTOM_GPT_MAIN_INSTRUCTIONS_8000.md",
    ]:
        text = read(rel)
        assert "FRONT_DOOR_CARRIER_PRODUCT_LAW" in text
        assert "Operator messages during an unfinished sequence are classified before response" in text
        assert "PERSONA_AS_PUBLIC_RENDERER_NOT_CHAT_BUDDY" in text
        assert "FINAL_ANSWER_GATE" in text
        assert "Do not spend the answer discord-ing with the operator" in text

def test_contract_file_states_product_behavior():
    text = read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/instructions/ION_CUSTOM_GPT_FRONT_DOOR_CARRIER_PRODUCT_CONTRACT.md")
    assert "The operator is not responsible for sequencing ION" in text
    assert "User messages during an unfinished active sequence are not route resets" in text
    assert "Persona is not Steward" in text
    assert "No substantive answer lands without a workflow object" in text
    assert "Structured continuation envelope" in text

def test_context_package_mounts_contract_and_keeps_steward_manager():
    data = load_yaml("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/context/ION_CUSTOM_GPT_SANDBOX_CARRIER_CONTEXT_PACKAGE.yaml")
    assert data["manager_agent"] == "STEWARD"
    assert data["presentation_agent"] == "PERSONA_INTERFACE"
    assert data["carrier_product_contract"]["operator_is_not_sequence_manager"] is True
    assert data["carrier_product_contract"]["machine_style_internal_persona_rendering_external"] is True
    assert data["final_answer_gate"]["telemetry_only_substantive_response_forbidden"] is True
    assert any("ION_CUSTOM_GPT_FRONT_DOOR_CARRIER_PRODUCT_CONTRACT.md" in item for item in data["root_nodes"])
    assert "schemas" in data["included_nodes"]
    assert "tools" in data["included_nodes"]

def test_route_has_turn_classifier_and_final_gate():
    data = load_yaml("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/routes/BOOT_TO_PERSONA_ROUTE.yaml")
    phases = [item["phase"] for item in data["internal_cycle"]]
    assert phases[-3:] == ["RELAY_RETURN_PACKAGE", "PERSONA_RETURN_GATE", "PERSONA_INTERFACE_RESPONSE"]
    assert data["product_contract"]["operator_is_not_sequence_manager"] is True
    assert data["product_contract"]["no_discord_with_operator"] is True
    assert data["operator_turn_classifier"]["while_active_sequence_unfinished"]["all_other_text"] == "PERSONA_INTERFACE_INGRESS_AND_RELAY_INPUT_FOR_SAME_WORKFLOW_OBJECT"
    assert "treat_unrelated_text_as_route_reset" in data["operator_turn_classifier"]["forbidden_classifications"]
    assert data["final_answer_gate"]["requires_workflow_object"] is True
    assert data["final_answer_gate"]["requires_terminal_persona_or_continuation_envelope"] is True
    assert data["completion_requirement"]["operator_turns_during_active_route_do_not_reset"] is True

def test_schemas_exist_and_require_authority_and_gate_fields():
    persona = load_json("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/schemas/ION_CUSTOM_GPT_PERSONA_RETURN_PACKAGE.schema.json")
    continuation = load_json("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/schemas/ION_CUSTOM_GPT_SEQUENCE_CONTINUATION_ENVELOPE.schema.json")
    assert "authority" in persona["required"]
    assert "final_answer_gate" in persona["required"]
    assert persona["properties"]["schema_id"]["const"] == "ion.custom_gpt.persona_return_package.v0_4"
    required_continuation = continuation["properties"]["ion_sequence_continuation"]["required"]
    for field in [
        "active_objective",
        "active_workflow_object",
        "current_phase",
        "completed_phases",
        "pending_phases",
        "next_phase",
        "blocker",
        "authority",
        "exact_continuation_route_or_prompt",
    ]:
        assert field in required_continuation

def test_harness_classifies_user_turns_without_route_reset():
    h = load_harness()
    assert h.classify_operator_turn("proceed", active_sequence_unfinished=True) == "continue_active_sequence"
    assert h.classify_operator_turn("this is completely wrong", active_sequence_unfinished=True) == "continue_active_sequence"
    assert h.classify_operator_turn("let's talk about something else", active_sequence_unfinished=True) == "continue_active_sequence"
    assert h.classify_operator_turn("STOP", active_sequence_unfinished=True) == "explicit_interrupt"
    assert h.classify_operator_turn("new package uploaded", active_sequence_unfinished=True, mentions_new_context_file=True) == "context_required_interrupt"

def test_harness_builds_valid_continuation_and_gate():
    h = load_harness()
    state = h.CarrierSequenceState(
        active_objective="complete boot route",
        active_workflow_object="BOOT_TO_PERSONA_INTERFACE_RESPONSE",
        current_phase="STEWARD_FINAL",
        completed_phases=("PERSONA_INTERFACE_INGRESS", "RELAY", "STEWARD", "VIZIER", "MASON", "SCRIBE", "STEWARD_FINAL"),
    )
    envelope = h.build_continuation_envelope(state, blocker="response budget")
    seq = envelope["ion_sequence_continuation"]
    assert seq["next_phase"] == "RELAY_RETURN_PACKAGE"
    assert seq["authority"] == "sandbox-candidate-write"
    assert "PERSONA_INTERFACE_RESPONSE" in seq["exact_continuation_route_or_prompt"]

    sample_package = {
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
        },
        "relay_return": {"meaning_preserved": True},
        "final_answer_gate": {
            "workflow_object_present": True,
            "terminal_or_continuation": True,
            "persona_return_gate_passed": True,
        },
    }
    assert h.persona_return_gate_passes(sample_package) is True

if __name__ == "__main__":
    test_instructions_bind_product_contract()
    test_contract_file_states_product_behavior()
    test_context_package_mounts_contract_and_keeps_steward_manager()
    test_route_has_turn_classifier_and_final_gate()
    test_schemas_exist_and_require_authority_and_gate_fields()
    test_harness_classifies_user_turns_without_route_reset()
    test_harness_builds_valid_continuation_and_gate()
    print("front door carrier product contract candidate regression: PASS")
