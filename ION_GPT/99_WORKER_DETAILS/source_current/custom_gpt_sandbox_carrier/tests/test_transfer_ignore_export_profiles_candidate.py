from pathlib import Path
import importlib.util
import sys
import yaml
import json

ROOT = Path(__file__).resolve().parents[5]
CARRIER = ROOT / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

def load_tool():
    path = CARRIER / "tools/ion_context_transfer_export.py"
    spec = importlib.util.spec_from_file_location("ion_context_transfer_export", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def test_transfer_ignore_law_files_and_profiles_exist():
    text = read("ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md")
    assert "ION_TRANSFER_IGNORE_AND_EXPORT_PROFILE_LAW" in text
    assert (ROOT / "ION_GPT/.ionignore").exists()
    data = yaml.safe_load(read("ION_GPT/ION_EXPORT_PROFILE.yaml"))
    for profile in ["minimal_continuity","working_handoff","full_reproducible","public_safe"]:
        assert profile in data["profiles"]
    assert "hidden_chain_of_thought" in data["non_exportable"]

def test_export_profile_schema_requires_non_exportable_boundary():
    schema = json.loads(read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/schemas/ION_CUSTOM_GPT_EXPORT_PROFILE.schema.json"))
    assert "non_exportable" in schema["required"]
    assert schema["properties"]["omission_manifest_required"]["const"] is True

def test_transfer_tool_never_exports_secrets_or_vault():
    tool = load_tool()
    result = tool.classify_paths(["src/main.py","ION_VAULT_LOCAL/key.txt",".env","notes/README.md","browser_session_data/cookies"])
    assert "src/main.py" in result["include"]
    omitted = {item["path"] for item in result["omit"]}
    assert "ION_VAULT_LOCAL/key.txt" in omitted
    assert ".env" in omitted
    assert "browser_session_data/cookies" in omitted
