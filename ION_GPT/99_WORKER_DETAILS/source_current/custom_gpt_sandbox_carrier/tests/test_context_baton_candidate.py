from pathlib import Path
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[5]
CARRIER = ROOT / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

def load_tool():
    path = CARRIER / "tools/ion_custom_gpt_ordered_context_fanout.py"
    spec = importlib.util.spec_from_file_location("ion_custom_gpt_ordered_context_fanout", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def test_context_baton_schema_contains_required_sections():
    schema = json.loads(read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/schemas/ION_CUSTOM_GPT_CONTEXT_BATON.schema.json"))
    required = schema["properties"]["ion_context_baton"]["required"]
    for field in ["source_anchors","tags","definitions","entities","claims","dependency_edges","downstream_alerts","unresolved_questions","upstream_reopen_alerts","confidence"]:
        assert field in required

def test_baton_tool_generates_required_payload():
    tool = load_tool()
    baton = tool.make_baton("agent_a", "first_third", "dense summary")
    payload = baton["ion_context_baton"]
    assert payload["schema_id"] == "ion.context_baton.v1"
    assert payload["branch_id"] == "agent_a"
    for field in ["source_anchors","definitions","claims","downstream_alerts","upstream_reopen_alerts"]:
        assert field in payload
