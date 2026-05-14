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
    path = CARRIER / "tools/ion_custom_gpt_ordered_context_fanout.py"
    spec = importlib.util.spec_from_file_location("ion_custom_gpt_ordered_context_fanout", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def test_ordered_context_fanout_law_states_soft_overlap_not_enough():
    text = read("ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md")
    assert "ORDERED_CONTEXT_FANOUT_LAW" in text
    detail = read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/instructions/ION_CUSTOM_GPT_ORDERED_CONTEXT_FANOUT.md")
    assert "Soft overlap" in detail
    assert "never sufficient" in detail

def test_route_requires_b_before_a_baton_and_c_before_a_b_batons():
    data = yaml.safe_load(read("ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/routes/ORDERED_CONTEXT_FANOUT_ROUTE.yaml"))
    assert data["soft_overlap_alone_sufficient"] is False
    assert data["branch_requirements"]["agent_b"]["upstream_batons_required"] == ["agent_a"]
    assert data["branch_requirements"]["agent_c"]["upstream_batons_required"] == ["agent_a", "agent_b"]
    assert data["fan_in"]["merge_order"] == "source_order"

def test_tool_enforces_required_batons_and_source_order_merge():
    tool = load_tool()
    required = {"agent_b": ["agent_a"], "agent_c": ["agent_a", "agent_b"]}
    assert tool.can_finalize("agent_b", {"agent_a"}, required) is True
    assert tool.can_finalize("agent_b", set(), required) is False
    assert tool.can_finalize("agent_c", {"agent_a"}, required) is False
    merged = tool.source_ordered_merge([{"branch":"c","source_order":3},{"branch":"a","source_order":1},{"branch":"b","source_order":2}])
    assert [m["branch"] for m in merged] == ["a","b","c"]
