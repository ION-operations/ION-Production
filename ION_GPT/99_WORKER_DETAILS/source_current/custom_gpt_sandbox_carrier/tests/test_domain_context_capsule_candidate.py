from pathlib import Path
import importlib.util
import sys
import yaml
import json

ROOT = Path(__file__).resolve().parents[5]
CARRIER = ROOT / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

def load_linter():
    path = CARRIER / "tools/ion_folder_context_capsule_lint.py"
    spec = importlib.util.spec_from_file_location("ion_folder_context_capsule_lint", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def test_domain_context_capsule_law_and_files_exist():
    text = read("ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md")
    assert "DOMAIN_CONTEXT_CAPSULE_README_LAW" in text
    assert (ROOT / "ION_GPT/ION_CONTEXT_CAPSULE.yaml").exists()
    assert (CARRIER / "ION_CONTEXT_CAPSULE.yaml").exists()
    assert (CARRIER / "README.md").exists()

def test_capsule_schema_requires_authority_and_continuity():
    schema = json.loads(read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/schemas/ION_CUSTOM_GPT_DOMAIN_CONTEXT_CAPSULE.schema.json"))
    assert "authority" in schema["required"]
    assert "continuity_export" in schema["required"]
    assert "freshness" in schema["required"]

def test_capsule_linter_accepts_pilot_capsules():
    linter = load_linter()
    for rel in ["ION_GPT/ION_CONTEXT_CAPSULE.yaml", "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/ION_CONTEXT_CAPSULE.yaml"]:
        errors = linter.lint_capsule(ROOT / rel)
        assert errors == []
