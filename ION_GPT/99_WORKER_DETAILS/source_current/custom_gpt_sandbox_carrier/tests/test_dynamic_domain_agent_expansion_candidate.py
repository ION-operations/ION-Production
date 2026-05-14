from pathlib import Path
import json
import yaml

ROOT = Path(__file__).resolve().parents[5]

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

def test_dynamic_domain_law_and_registry_are_candidate_only():
    text = read("ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md")
    assert "DYNAMIC_DOMAIN_AGENT_EXPANSION_LAW" in text
    data = yaml.safe_load(read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/registries/ION_CUSTOM_GPT_DYNAMIC_DOMAIN_AGENT_REGISTRY_CANDIDATE.yaml"))
    assert data["registry_boundary"]["mutates_accepted_registry"] is False
    assert data["registry_boundary"]["requires_human_acceptance_to_land"] is True
    assert any(d["domain_id"] == "continuity_transfer" for d in data["candidate_domains"])

def test_dynamic_domain_schema_requires_registry_boundary():
    schema = json.loads(read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/schemas/ION_CUSTOM_GPT_DYNAMIC_DOMAIN_AGENT_EXPANSION.schema.json"))
    required = schema["properties"]["ion_dynamic_domain_agent_expansion"]["required"]
    assert "candidate_domains" in required
    assert "candidate_agents" in required
    assert "registry_boundary" in required
    assert schema["properties"]["ion_dynamic_domain_agent_expansion"]["properties"]["registry_boundary"]["properties"]["mutates_accepted_registry"]["const"] is False
