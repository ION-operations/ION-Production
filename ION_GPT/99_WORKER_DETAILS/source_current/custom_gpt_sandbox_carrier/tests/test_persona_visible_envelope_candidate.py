from pathlib import Path
import importlib.util
import json
import sys
import yaml

ROOT = Path(__file__).resolve().parents[5]
CARRIER = ROOT / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

def load_tool(name):
    path = CARRIER / "tools" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def test_persona_visible_envelope_law_instructions_and_template():
    for rel in [
        "ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md",
        "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/instructions/ION_CUSTOM_GPT_PERSONA_VISIBLE_ENVELOPE.md",
    ]:
        text = read(rel)
        assert "PERSONA_VISIBLE_ENVELOPE_LAW" in text or "Persona Visible Envelope" in text
        assert "operator_visible_persona_signal_not_hidden_reasoning" in text
        assert "hidden_chain_of_thought" in text
    template = read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/templates/ION_CUSTOM_GPT_PERSONA_INTERFACE_RESPONSE.template.md")
    assert "ion_persona:" in template
    assert "gesture:" in template
    assert "inner_monologue:" in template
    assert "ION ::" in template

def test_persona_schema_requires_visible_fields():
    schema = json.loads(read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/schemas/ION_CUSTOM_GPT_PERSONA_VISIBLE_ENVELOPE.schema.json"))
    required = schema["properties"]["ion_persona"]["required"]
    for field in ["persona", "route", "confidence", "gesture", "inner_monologue", "boundaries"]:
        assert field in required
    boundaries = schema["properties"]["ion_persona"]["properties"]["boundaries"]["properties"]
    assert boundaries["hidden_chain_of_thought_exposed"]["const"] is False

def test_profile_registry_has_recovered_profiles_as_candidates():
    data = yaml.safe_load(read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/registries/ION_CUSTOM_GPT_PERSONA_PROFILE_REGISTRY.yaml"))
    profiles = {item["profile_id"]: item for item in data["profiles"]}
    for key in ["ion_default", "technical_plain", "audit_repair", "recovered_3po", "recovered_connery_bond", "recovered_feynman_mex"]:
        assert key in profiles
    assert profiles["recovered_3po"]["status"] == "historical_evidence_candidate"
    assert profiles["recovered_connery_bond"]["authority_role"] is False
    assert data["boundary"]["profiles_are_presentation_calibration_only"] is True

def test_persona_tool_builds_safe_visible_envelope():
    tool = load_tool("ion_custom_gpt_persona_envelope")
    envelope = tool.build_persona_envelope(
        route_id="BOOT_TO_PERSONA_INTERFACE_RESPONSE",
        selected_profile="audit_repair",
        candidate_domains=["persona_visible_envelope"],
        candidate_agents=["persona_profile_selector"],
        dynamic_domain_needed=True,
    )
    ion = envelope["ion_persona"]
    assert ion["persona"]["selected_profile"] == "audit_repair"
    assert ion["route"]["candidate_domains"] == ["persona_visible_envelope"]
    assert ion["inner_monologue"]["type"] == "operator_visible_persona_signal_not_hidden_reasoning"
    assert ion["boundaries"]["hidden_chain_of_thought_exposed"] is False
