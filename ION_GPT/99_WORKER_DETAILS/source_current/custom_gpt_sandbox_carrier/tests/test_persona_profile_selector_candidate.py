from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[5]
CARRIER = ROOT / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"

def load_tool():
    path = CARRIER / "tools/ion_custom_gpt_persona_envelope.py"
    spec = importlib.util.spec_from_file_location("ion_custom_gpt_persona_envelope", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def test_profile_selection_routes_style_only():
    tool = load_tool()
    assert tool.select_profile("please audit this defect") == "audit_repair"
    assert tool.select_profile("explain this simply") == "recovered_feynman_mex"
    assert tool.select_profile("mission style bond") == "recovered_connery_bond"
    assert tool.select_profile("plain technical") == "technical_plain"
    assert tool.select_profile("unknown") == "ion_default"

def test_requested_profile_must_be_known():
    tool = load_tool()
    assert tool.select_profile("anything", requested_profile="recovered_3po") == "recovered_3po"
    assert tool.select_profile("anything", requested_profile="unsafe_new_authority_profile") == "ion_default"
