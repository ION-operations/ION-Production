from pathlib import Path
import importlib.util
import sys
import yaml
import zipfile

ROOT = Path(__file__).resolve().parents[5]
CARRIER = ROOT / "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"


def load_tool():
    path = CARRIER / "tools/ion_dogfood_evolution_builder.py"
    spec = importlib.util.spec_from_file_location("ion_dogfood_evolution_builder", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_dogfood_builder_creates_remountable_context_package(tmp_path):
    tool = load_tool()
    out = tmp_path / "dogfood_context_package"
    report = tool.build_dogfood_package(ROOT, out)
    assert report["schema_id"] == "ion.custom_gpt.dogfood_build_report.v1"
    assert report["authority"]["accepted_state_claim"] is False
    assert report["results"]["remount_simulation"] == "pass"
    assert (out / "ion_context_package.yaml").exists()
    assert (out / "ion_context_mesh_manifest.yaml").exists()
    assert (out / "ION_TRANSFER_MANIFEST.yaml").exists()
    assert (out / "NEXT_CHAT_PROMPT.txt").exists()
    with zipfile.ZipFile(out.with_suffix(".zip")) as zf:
        names = set(zf.namelist())
    assert "ion_context_package.yaml" in names
    assert "ion_context_mesh_manifest.yaml" in names
    assert "NEXT_CHAT_PROMPT.txt" in names


def test_dogfood_package_remounts_active_route(tmp_path):
    tool = load_tool()
    out = tmp_path / "dogfood_context_package"
    tool.build_dogfood_package(ROOT, out)
    pkg = yaml.safe_load((out / "ion_context_package.yaml").read_text())
    mesh = yaml.safe_load((out / "ion_context_mesh_manifest.yaml").read_text())
    prompt = (out / "NEXT_CHAT_PROMPT.txt").read_text()
    assert pkg["workflow_state"]["active_route"] == "DOGFOOD_CONTEXT_PACKAGE_BUILD_ROUTE"
    assert pkg["authority"]["production_authority"] is False
    assert len(mesh["capsules"]) >= 3
    assert "Mount the attached ION context package" in prompt
