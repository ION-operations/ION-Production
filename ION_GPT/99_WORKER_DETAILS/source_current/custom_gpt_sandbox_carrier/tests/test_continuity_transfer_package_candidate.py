from pathlib import Path
import importlib.util
import sys
import zipfile
import yaml
import json

ROOT = Path(__file__).resolve().parents[5]
CARRIER = ROOT / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

def load_tool():
    path = CARRIER / "tools/ion_custom_gpt_continuity_exporter.py"
    spec = importlib.util.spec_from_file_location("ion_custom_gpt_continuity_exporter", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def test_continuity_law_and_template_require_remount_package():
    text = read("ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md")
    assert "CONTINUITY_EXPORT_PACKAGE_LAW" in text
    assert "REMOUNTABLE_CHAT_CONTINUITY_LAW" in text
    template = read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/templates/ION_CUSTOM_GPT_CONTINUITY_TRANSFER_PACKAGE.template.md")
    for item in ["ion_continuity_transfer_manifest.yaml", "ion_sequence_continuation.yaml", "ion_dynamic_domain_agent_expansion.yaml", "NEXT_CHAT_PROMPT.txt"]:
        assert item in template

def test_exporter_writes_required_files(tmp_path):
    tool = load_tool()
    zip_path = tool.build_package(tmp_path, "ION_CONTINUITY_TRANSFER_PACKAGE_TEST")
    assert zip_path.exists()
    with zipfile.ZipFile(zip_path) as z:
        names = set(z.namelist())
    for item in tool.REQUIRED_FILES:
        assert item in names
    manifest = yaml.safe_load((tmp_path / "ION_CONTINUITY_TRANSFER_PACKAGE_TEST/ion_continuity_transfer_manifest.yaml").read_text())
    assert manifest["remount_rule"] == "mount_before_substantive_answer"
    assert manifest["accepted_state_claim"] is False

def test_continuity_manifest_schema_names_required_files():
    schema = json.loads(read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/schemas/ION_CUSTOM_GPT_CONTINUITY_TRANSFER_PACKAGE.schema.json"))
    for field in ["schema_id", "continuity_files", "next_chat_prompt", "hashes"]:
        assert field in schema["required"]
