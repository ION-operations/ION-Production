from pathlib import Path
import importlib.util
import json
import sys
import yaml

ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"

def read(rel: str) -> str:
    return (BASE / rel).read_text(encoding="utf-8")

def load_harness():
    path = BASE / "tools/ion_custom_gpt_sequence_harness.py"
    spec = importlib.util.spec_from_file_location("ion_custom_gpt_sequence_harness_v42", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def test_boot_template_contains_receipt_persona_and_ion():
    text = read("templates/ION_CUSTOM_GPT_BOOT_PERSONA_RESPONSE.template.md")
    assert "ion_boot_sequence_result" in text
    assert "ion_persona" in text
    assert "ION ::" in text
    assert "operator_visible_persona_signal_not_hidden_reasoning" in text


def test_persona_envelope_schema_requires_visible_fields_and_blocks_hidden_cot():
    schema = json.loads(read("schemas/ION_CUSTOM_GPT_PERSONA_VISIBLE_ENVELOPE.schema.json"))
    persona_required = schema["properties"]["ion_persona"]["properties"]["persona"]["required"]
    route_required = schema["properties"]["ion_persona"]["properties"]["route"]["required"]
    confidence_required = schema["properties"]["ion_persona"]["properties"]["confidence"]["required"]
    gesture_required = schema["properties"]["ion_persona"]["properties"]["gesture"]["required"]
    inner = schema["properties"]["ion_persona"]["properties"]["inner_monologue"]["properties"]
    boundaries = schema["properties"]["ion_persona"]["properties"]["boundaries"]["properties"]
    assert "visible_name" in persona_required
    assert "selected_profile" in persona_required
    assert "route_id" in route_required
    assert "candidate_domains" in route_required
    assert "candidate_agents" in route_required
    assert "level" in confidence_required
    assert "semantic" in confidence_required
    assert "gesture" in gesture_required
    assert "semantic" in gesture_required
    assert inner["type"]["const"] == "operator_visible_persona_signal_not_hidden_reasoning"
    assert boundaries["hidden_chain_of_thought_exposed"]["const"] is False


def test_harness_builds_visible_persona_without_hidden_reasoning():
    h = load_harness()
    envelope = h.build_persona_visible_envelope(
        route_id="BOOT_TO_PERSONA_INTERFACE_RESPONSE",
        profile_id="audit_repair",
        candidate_domains=["custom_gpt_action_release"],
        candidate_agents=["STEWARD", "RELAY", "PERSONA_INTERFACE"],
    )["ion_persona"]
    assert envelope["persona"]["selected_profile"] == "audit_repair"
    assert envelope["persona"]["role_ref"] == "role.persona_interface"
    assert envelope["route"]["candidate_domains"] == ["custom_gpt_action_release"]
    assert envelope["inner_monologue"]["type"] == "operator_visible_persona_signal_not_hidden_reasoning"
    assert "hidden_chain_of_thought" in envelope["inner_monologue"]["not_claimed"]
    assert envelope["boundaries"]["hidden_chain_of_thought_exposed"] is False
