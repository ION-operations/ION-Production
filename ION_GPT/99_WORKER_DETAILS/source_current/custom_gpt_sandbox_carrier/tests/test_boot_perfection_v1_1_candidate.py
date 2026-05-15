from pathlib import Path
import importlib.util
import json
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[5]
CARRIER = ROOT / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"
BUILDER = ROOT / "ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md"
WORKER = CARRIER / "instructions/ION_CUSTOM_GPT_MAIN_INSTRUCTIONS_8000.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(rel: str):
    return json.loads(read(CARRIER / rel))


def load_tool(name: str):
    path = CARRIER / "tools" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def fenced_yaml_blocks(text: str):
    return re.findall(r"```yaml\n(.*?)\n```", text, flags=re.DOTALL)


def test_compact_builder_instructions_harden_boot_laws_under_budget():
    builder = read(BUILDER)
    worker = read(WORKER)
    assert builder == worker
    assert len(builder.encode("utf-8")) < 8000
    for token in [
        "MACHINE_BLOCK_FENCE_LAW",
        "ACTION_SURFACE_DEDICATED_AUDIT_LAW",
        "SECRETS_VAULT_POSTURE_LAW",
        "FINAL_BOOT_ANSWER_START_LAW",
        "SCHEMA_STABILITY_LAW",
        "ion.boot_sequence_result.v1",
        "ion.boot_perfection_audit.v1",
        "ion.action_surface_audit.v1",
        "ion.persona_response_envelope.v0_1",
        "No validated release bundle, no GPT Builder change",
    ]:
        assert token in builder


def test_boot_template_starts_with_boot_and_uses_parseable_fenced_yaml_blocks():
    template = read(CARRIER / "templates/ION_CUSTOM_GPT_BOOT_PERSONA_RESPONSE.template.md")
    assert template.startswith("BOOT ::")
    blocks = fenced_yaml_blocks(template)
    assert len(blocks) == 4
    payloads = [yaml.safe_load(block) for block in blocks]
    keys = [next(iter(payload)) for payload in payloads]
    assert keys == [
        "ion_boot_sequence_result",
        "ion_boot_audit",
        "ion_action_surface_audit",
        "ion_persona",
    ]
    assert payloads[0]["ion_boot_sequence_result"]["schema_id"] == "ion.boot_sequence_result.v1"
    assert payloads[1]["ion_boot_audit"]["schema_id"] == "ion.boot_perfection_audit.v1"
    audit = payloads[2]["ion_action_surface_audit"]
    assert audit["schema_id"] == "ion.action_surface_audit.v1"
    assert audit["secrets_vaults_credentials"] == {
        "status": "not_inspected",
        "reason": "not_requested_or_not_authorized",
    }
    assert payloads[3]["ion_persona"]["schema_id"] == "ion.persona_response_envelope.v0_1"


def test_action_surface_audit_schema_is_dedicated_and_deep():
    schema = load_json("schemas/ION_CUSTOM_GPT_ACTION_SURFACE_AUDIT.schema.json")
    audit = schema["properties"]["ion_action_surface_audit"]
    assert audit["properties"]["schema_id"]["const"] == "ion.action_surface_audit.v1"
    for field in [
        "action_gateway",
        "action_schemas",
        "mcp_preview",
        "project_workbench",
        "browser_queue",
        "supabase_cockpit",
        "secrets_vaults_credentials",
        "non_claims",
    ]:
        assert field in audit["required"]
    gateway_required = set(audit["properties"]["action_gateway"]["required"])
    assert {"supported_mvp_intents_count", "allowed_get_paths_count", "allowed_post_paths_count", "refusal_classes_count"}.issubset(gateway_required)
    mcp_required = set(audit["properties"]["mcp_preview"]["required"])
    assert {"read_only_tools_count", "mutation_tools_count", "write_confirmation_token"}.issubset(mcp_required)


def test_boot_audit_and_persona_schemas_use_canonical_schema_ids():
    boot = load_json("schemas/ION_CUSTOM_GPT_BOOT_SEQUENCE_RESULT.schema.json")
    boot_props = boot["properties"]["ion_boot_sequence_result"]["properties"]
    assert boot_props["schema_id"]["const"] == "ion.boot_sequence_result.v1"
    assert boot_props["accepted_state_claim"]["const"] is False
    assert boot_props["production_authority"]["const"] is False
    assert boot_props["live_execution_authority"]["const"] is False

    audit = load_json("schemas/ION_CUSTOM_GPT_BOOT_PERFECTION_AUDIT.schema.json")
    assert audit["properties"]["ion_boot_audit"]["properties"]["schema_id"]["const"] == "ion.boot_perfection_audit.v1"

    persona = load_json("schemas/ION_CUSTOM_GPT_PERSONA_VISIBLE_ENVELOPE.schema.json")
    ion = persona["properties"]["ion_persona"]
    assert ion["properties"]["schema_id"]["const"] == "ion.persona_response_envelope.v0_1"
    assert "schema_id" in ion["required"]
    assert "schema" not in ion["required"]
    assert ion["properties"]["boundaries"]["properties"]["hidden_chain_of_thought_exposed"]["const"] is False


def test_persona_tool_emits_schema_id_not_legacy_schema():
    tool = load_tool("ion_custom_gpt_persona_envelope")
    envelope = tool.build_persona_envelope(route_id="BOOT_TO_PERSONA_INTERFACE_RESPONSE")
    ion = envelope["ion_persona"]
    assert ion["schema_id"] == "ion.persona_response_envelope.v0_1"
    assert "schema" not in ion
