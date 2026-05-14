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


def test_context_package_index_and_packages_are_candidate_only():
    index = yaml.safe_load((CARRIER / "context_packages/ION_CONTEXT_PACKAGE_INDEX.yaml").read_text())
    assert index["schema_id"] == "ion.context_package_index.v1"
    assert index["authority"]["accepted_state_claim"] is False
    assert len(index["packages"]) >= 3
    for item in index["packages"]:
        pkg = yaml.safe_load((CARRIER / "context_packages" / item["path"]).read_text())
        assert pkg["schema_id"] == "ion.context_package.v1"
        assert pkg["posture"] == "sandbox-candidate"
        assert pkg["authority"]["production_authority"] is False
        assert pkg["authority"]["live_execution_authority"] is False


def test_context_package_builder_outputs_required_state(tmp_path):
    mesh_tool = load_tool("ion_context_mesh_builder")
    pkg_tool = load_tool("ion_context_package_builder")
    mesh = mesh_tool.build_context_mesh(ROOT)
    pkg = pkg_tool.build_context_package("ion.test.context_package", mesh)
    out = tmp_path / "ion_context_package.yaml"
    pkg_tool.write_context_package(pkg, out)
    data = yaml.safe_load(out.read_text())
    assert data["workflow_state"]["active_route"] == "DOGFOOD_CONTEXT_PACKAGE_BUILD_ROUTE"
    assert data["persona_state"]["hidden_chain_of_thought_exposed"] is False
    assert data["domain_agent_state"]["registry_boundary"]["mutates_accepted_registry"] is False
    assert data["continuity_export"]["mount_before_substantive_answer"] is True
