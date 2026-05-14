from pathlib import Path
import importlib.util
import sys
import yaml

ROOT = Path(__file__).resolve().parents[5]
CARRIER = ROOT / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"


def load_tool():
    path = CARRIER / "tools/ion_context_transfer_export.py"
    spec = importlib.util.spec_from_file_location("ion_context_transfer_export", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_export_profile_never_exports_secret_classes():
    tool = load_tool()
    result = tool.classify_paths([
        "ION_GPT/README.md",
        "ION_VAULT_LOCAL/token.txt",
        ".env",
        "browser_session/state.json",
        "notes/hidden_chain_of_thought.md",
    ])
    included = set(result["include"])
    omitted = {item["path"]: item["reason"] for item in result["omit"]}
    assert "ION_GPT/README.md" in included
    assert omitted["ION_VAULT_LOCAL/token.txt"] == "non_exportable_boundary"
    assert omitted[".env"] == "non_exportable_boundary"
    assert omitted["browser_session/state.json"] == "non_exportable_boundary"
    assert omitted["notes/hidden_chain_of_thought.md"] == "non_exportable_boundary"


def test_transfer_manifest_hashes_included_files_and_records_omits():
    tool = load_tool()
    manifest = tool.build_transfer_manifest(ROOT, profile_name="minimal_continuity", paths=[
        "ION_GPT/README.md",
        "ION_GPT/90_HISTORICAL_ZIPS/old.zip",
        "ION_VAULT_LOCAL/secret.txt",
    ])
    assert manifest["schema_id"] == "ion.transfer_manifest.v1"
    assert "ION_GPT/README.md" in manifest["included_files"]
    assert manifest["hashes"]["ION_GPT/README.md"]
    assert any(item["reason"] == "non_exportable_boundary" for item in manifest["omitted_files"])
    assert any(item["reason"] == "ignored_by_pattern" for item in manifest["omitted_files"])
