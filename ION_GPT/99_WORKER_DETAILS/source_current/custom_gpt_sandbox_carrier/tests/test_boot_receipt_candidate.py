from pathlib import Path
import importlib.util
import json
import sys
import yaml

ROOT = Path(__file__).resolve().parents[5]
CARRIER = ROOT / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

def load_tool():
    path = CARRIER / "tools/ion_custom_gpt_persona_envelope.py"
    spec = importlib.util.spec_from_file_location("ion_custom_gpt_persona_envelope", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def test_boot_receipt_law_instructions_and_template():
    text = read("ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md")
    assert "BOOT_RECEIPT_LAW" in text
    template = read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/templates/ION_CUSTOM_GPT_BOOT_PERSONA_RESPONSE.template.md")
    assert "ion_boot_sequence_result:" in template
    assert "ion_persona:" in template
    assert "PERSONA_RETURN_GATE" in template
    assert "ION ::" in template

def test_boot_receipt_schema_requires_authority_false():
    schema = json.loads(read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/schemas/ION_CUSTOM_GPT_BOOT_SEQUENCE_RESULT.schema.json"))
    props = schema["properties"]["ion_boot_sequence_result"]["properties"]
    assert props["accepted_state_claim"]["const"] is False
    assert props["production_authority"]["const"] is False
    assert props["live_execution_authority"]["const"] is False

def test_boot_receipt_tool_phases_end_in_persona_response():
    tool = load_tool()
    receipt = tool.build_boot_receipt("boot-test", "test objective", 9)
    result = receipt["ion_boot_sequence_result"]
    assert result["phases_completed"][0] == "PERSONA_INTERFACE_INGRESS"
    assert result["phases_completed"][-1] == "PERSONA_INTERFACE_RESPONSE"
    assert result["persona_return_gate"] == "pass"
    assert result["accepted_state_claim"] is False
