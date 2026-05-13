from pathlib import Path
import importlib.util
import json
import sys
import yaml

ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"

def read(rel: str) -> str:
    return (BASE / rel).read_text(encoding="utf-8")

def load_harness():
    path = BASE / "tools/ion_custom_gpt_sequence_harness.py"
    spec = importlib.util.spec_from_file_location("ion_custom_gpt_sequence_harness_boot_v42", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def test_route_requires_boot_receipt_and_persona_envelope():
    route = yaml.safe_load(read("routes/BOOT_TO_PERSONA_ROUTE.yaml"))
    assert route["boot_receipt"]["required_for_boot_sequence"] is True
    assert route["persona_visible_envelope"]["required_for_serious_ion_work"] is True
    assert route["persona_return_gate"]["required_for_substantive_final_answer"] is True
    assert route["final_answer_gate"]["requires_boot_or_work_receipt_when_state_bearing"] is True
    assert route["final_answer_gate"]["requires_persona_visible_envelope"] is True


def test_boot_receipt_schema_requires_authority_false_and_candidate_receipt():
    schema = json.loads(read("schemas/ION_CUSTOM_GPT_BOOT_SEQUENCE_RESULT.schema.json"))
    props = schema["properties"]["ion_boot_sequence_result"]["properties"]
    required = schema["properties"]["ion_boot_sequence_result"]["required"]
    assert "boot_id" in required
    assert "ion_project_hash" in required
    assert "project_hash_status" in required
    assert "phases_completed" in required
    assert props["accepted_state_claim"]["const"] is False
    assert props["production_authority"]["const"] is False
    assert props["live_execution_authority"]["const"] is False
    assert props["receipt_status"]["const"] == "candidate_boot_receipt"


def test_harness_builds_boot_receipt_with_full_route():
    h = load_harness()
    receipt = h.build_boot_sequence_result(
        boot_id="boot-test",
        objective="boot ION-through-this-ChatGPT-carrier",
        mounted_package_count=9,
    )["ion_boot_sequence_result"]
    assert receipt["schema_id"] == "ion.boot_sequence_result.v1"
    assert receipt["route_id"] == "BOOT_TO_PERSONA_INTERFACE_RESPONSE"
    assert receipt["ion_project_hash"] == "pending_build"
    assert receipt["project_hash_status"] == "pending_build"
    assert receipt["phases_completed"][-1] == "PERSONA_INTERFACE_RESPONSE"
    assert receipt["persona_return_gate"] == "pass"
    assert receipt["accepted_state_claim"] is False
    assert receipt["production_authority"] is False
    assert receipt["live_execution_authority"] is False
