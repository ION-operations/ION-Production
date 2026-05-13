from pathlib import Path
import importlib.util
import sys
import yaml

ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"

def read(rel: str) -> str:
    return (BASE / rel).read_text(encoding="utf-8")

def load_harness():
    path = BASE / "tools/ion_custom_gpt_sequence_harness.py"
    spec = importlib.util.spec_from_file_location("ion_custom_gpt_sequence_harness_profile_v42", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def test_profile_registry_contains_required_profiles_as_presentation_only():
    reg = yaml.safe_load(read("registries/ION_CUSTOM_GPT_PERSONA_PROFILE_REGISTRY.yaml"))
    profiles = reg["profiles"]
    for key in ["ion_default", "technical_plain", "audit_repair", "recovered_3po", "recovered_connery_bond", "recovered_feynman_mex"]:
        assert key in profiles
    assert reg["authority_boundary"]["profiles_grant_authority"] is False
    assert profiles["recovered_3po"]["profile_status"] == "historical_evidence_candidate"
    assert profiles["recovered_connery_bond"]["profile_status"] == "historical_evidence_candidate"
    assert profiles["recovered_feynman_mex"]["profile_status"] == "historical_evidence_candidate"


def test_profile_selector_never_grants_authority():
    h = load_harness()
    selected = h.select_persona_profile("recovered_feynman_mex")
    assert selected["selected_profile"] == "recovered_feynman_mex"
    assert selected["profile_status"] == "historical_evidence_candidate"
    assert selected["profiles_grant_authority"] is False
    fallback = h.select_persona_profile("unknown")
    assert fallback["selected_profile"] == "ion_default"
    assert fallback["profiles_grant_authority"] is False


def test_proceed_continuation_preserves_receipt_and_persona_envelope_capability():
    h = load_harness()
    assert h.classify_operator_turn("proceed", active_sequence_unfinished=True) == "continue_active_sequence"
    receipt = h.build_boot_sequence_result(boot_id="proceed-test", objective="continue active boot route")
    envelope = h.build_persona_visible_envelope(route_id="BOOT_TO_PERSONA_INTERFACE_RESPONSE")
    assert "ion_boot_sequence_result" in receipt
    assert "ion_persona" in envelope
    assert envelope["ion_persona"]["boundaries"]["hidden_chain_of_thought_exposed"] is False
