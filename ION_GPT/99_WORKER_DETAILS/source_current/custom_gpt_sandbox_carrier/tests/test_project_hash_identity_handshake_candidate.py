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
    path = CARRIER / "tools/ion_project_hash_identity.py"
    spec = importlib.util.spec_from_file_location("ion_project_hash_identity", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_project_hash_law_in_instructions_under_budget():
    text = read("ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md")
    assert "PROJECT_HASH_IDENTITY_HANDSHAKE_LAW" in text
    assert "public project identity/locator" in text
    assert "not a password" in text
    assert len(text) < 8000


def test_project_hash_identity_files_exist():
    assert (CARRIER / "instructions/ION_CUSTOM_GPT_PROJECT_HASH_IDENTITY_HANDSHAKE.md").exists()
    assert (CARRIER / "schemas/ION_PROJECT_IDENTITY.schema.json").exists()
    assert (CARRIER / "schemas/ION_HASH_BRANCH_REGISTRY.schema.json").exists()
    assert (CARRIER / "schemas/ION_HELIXION_HASH_HANDSHAKE.schema.json").exists()
    assert (CARRIER / "schemas/ION_HASH_CAPABILITY_GRANT.schema.json").exists()
    assert (CARRIER / "registries/ION_PROJECT_HASH_CAPABILITY_LEVELS.yaml").exists()
    assert (CARRIER / "templates/ION_PROJECT_IDENTITY.template.yaml").exists()
    assert (CARRIER / "templates/ION_HASH_BRANCHES.template.yaml").exists()
    assert (CARRIER / "templates/ION_HELIXION_HASH_HANDSHAKE.template.yaml").exists()
    assert (CARRIER / "tools/ion_project_hash_identity.py").exists()


def test_identity_schema_declares_hash_not_secret_or_auth():
    schema = json.loads((CARRIER / "schemas/ION_PROJECT_IDENTITY.schema.json").read_text(encoding="utf-8"))
    props = schema["properties"]
    assert props["hash_role"]["enum"] == ["public_identity_locator"]
    assert props["identity_is_secret"]["const"] is False
    security = props["security_model"]["properties"]
    assert security["hash_grants_access"]["const"] is False
    assert security["authorization_lives_at"]["const"] == "helixion"
    assert security["secrets_in_folder"]["const"] is False


def test_key_branches_are_non_secret_pointers():
    template = yaml.safe_load((CARRIER / "templates/ION_HASH_BRANCHES.template.yaml").read_text(encoding="utf-8"))
    assert template["schema_id"] == "ion.hash_branch_registry.v1"
    assert template["secrets_present"] is False
    assert template["branches"]
    assert all(branch["secret"] is False for branch in template["branches"])
    assert any(branch["branch_id"] == "action_capability" for branch in template["branches"])
    action_branch = next(branch for branch in template["branches"] if branch["branch_id"] == "action_capability")
    assert "does not contain capability secret" in action_branch["validation_role"]


def test_handshake_schema_prevents_hash_only_access():
    schema = json.loads((CARRIER / "schemas/ION_HELIXION_HASH_HANDSHAKE.schema.json").read_text(encoding="utf-8"))
    auth = schema["properties"]["authorization_boundary"]["properties"]
    assert auth["hash_grants_access"]["const"] is False
    assert auth["capability_token_exportable"]["const"] is False
    decision = schema["properties"]["server_decision"]["properties"]["status"]["enum"]
    assert "requires_claim_or_forbidden" in decision


def test_tool_generates_public_identity_and_no_secrets():
    tool = load_tool()
    project_hash = tool.new_project_hash("demo")
    assert project_hash.startswith("ionproj_")
    identity = tool.build_project_identity(project_hash, "demo")
    assert identity["identity_is_secret"] is False
    assert identity["security_model"]["hash_grants_access"] is False
    assert identity["security_model"]["authorization_lives_at"] == "helixion"
    assert tool.manifest_contains_no_secrets(identity)

    branches = tool.build_hash_branches(project_hash)
    assert branches["secrets_present"] is False
    assert all(branch["secret"] is False for branch in branches["branches"])

    handshake = tool.build_claim_handshake(project_hash, "carrier", "nonce")
    assert handshake["authorization_boundary"]["hash_grants_access"] is False
    assert handshake["authorization_boundary"]["capability_token_exportable"] is False
    assert handshake["server_decision"]["private_metadata_returned"] is False


def test_capability_levels_do_not_export_tokens():
    registry = yaml.safe_load((CARRIER / "registries/ION_PROJECT_HASH_CAPABILITY_LEVELS.yaml").read_text(encoding="utf-8"))
    assert "capability_token" in registry["non_exportable"]
    assert registry["levels"]["public_probe"]["private_metadata_returned"] is False
    assert registry["levels"]["context_read"]["export_capability_token"] is False
