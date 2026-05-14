from pathlib import Path
import importlib.util
import sys
import yaml

ROOT = Path(__file__).resolve().parents[5]
CARRIER = ROOT / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"


def load_tool(name):
    path = CARRIER / "tools" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_context_mesh_discovers_root_and_carrier_capsules():
    tool = load_tool("ion_context_mesh_builder")
    mesh = tool.build_context_mesh(ROOT)
    ids = {c["capsule_id"] for c in mesh["capsules"]}
    assert ids & {"ion_production_workspace_root", "ion.folder.root.ion_gpt_candidate_workspace"}
    assert "ION - Production" not in ids
    assert "ion.folder.ion_gpt" in ids
    assert "ion.folder.ion_gpt.custom_gpt_sandbox_carrier" in ids
    assert mesh["authority"]["accepted_state_claim"] is False
    assert mesh["authority"]["production_authority"] is False


def test_context_mesh_has_inheritance_edges_and_relevant_selection():
    tool = load_tool("ion_context_mesh_builder")
    mesh = tool.build_context_mesh(ROOT, changed_paths=[
        "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier/tools/ion_context_mesh_builder.py"
    ])
    assert mesh["inheritance_edges"]
    assert any("custom_gpt_sandbox_carrier/ION_CONTEXT_CAPSULE.yaml" in p for p in mesh["relevant_capsule_paths"])
    assert any(p == "ION_GPT/ION_CONTEXT_CAPSULE.yaml" for p in mesh["relevant_capsule_paths"])
