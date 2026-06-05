from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[2]


def load_router():
    path = ROOT / "ION/04_packages/kernel/ion_branch_delegate_router.py"
    spec = importlib.util.spec_from_file_location("ion_branch_delegate_router", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["ion_branch_delegate_router"] = module
    spec.loader.exec_module(module)
    return module


def make_repo(tmp_path):
    root = tmp_path / "repo"
    branch = root / "ION/09_integrations/browser_extension"
    branch.mkdir(parents=True)
    (root / "README.md").write_text("root readme")
    (branch / "README.md").write_text("browser branch")
    (branch / "AGENTS.md").write_text("codex branch specialist")
    (branch / "ION_CONTEXT_CAPSULE.yaml").write_text("schema_id: ion.context_capsule.branch.v0_1\n")
    return root


def test_extract_branch_refs_finds_ion_paths():
    router = load_router()
    refs = router.extract_branch_refs("Ask ION/09_integrations/browser_extension and ION/04_packages/kernel")
    assert "ION/09_integrations/browser_extension" in refs
    assert "ION/04_packages/kernel" in refs


def test_build_delegation_request_resolves_branch_node(tmp_path):
    router = load_router()
    repo = make_repo(tmp_path)
    request = router.build_delegation_request(
        repo,
        "Ask ION/09_integrations/browser_extension for context",
        targets=["ION/09_integrations/browser_extension"],
    )
    assert request["schema_id"] == "ion.branch_delegation_request.v0_1"
    assert request["status"] == "candidate"
    target = request["targets"][0]
    assert target["nearest_branch_node"] == "ION/09_integrations/browser_extension"
    assert "ION/09_integrations/browser_extension/ION_CONTEXT_CAPSULE.yaml" in target["context_files"]


def test_router_rejects_path_traversal(tmp_path):
    router = load_router()
    repo = make_repo(tmp_path)
    request = router.build_delegation_request(repo, "bad", targets=["../../etc/passwd"])
    assert request["status"] == "blocked"
    assert request["targets"][0]["kind"] == "invalid"
    assert "escapes repo root" in request["targets"][0]["blockers"][0]


def test_request_does_not_claim_delegate_invocation(tmp_path):
    router = load_router()
    repo = make_repo(tmp_path)
    request = router.build_delegation_request(repo, "Ask ION/09_integrations/browser_extension")
    assert "did_not_invoke_subagent" in request["did_not_do"]
    assert "no_delegate_invocation_receipt" in request["missing_proof"]
    assert request["authority"]["production_authority"] is False
    assert request["authority"]["live_execution_authority"] is False


def test_delegate_return_stub_is_blocked_without_proof():
    router = load_router()
    stub = router.build_delegate_return_stub("ION/09_integrations/browser_extension")
    assert stub["schema_id"] == "ion.branch_delegate_return.v0_1"
    assert stub["status"] == "blocked"
    assert "delegate_invocation_receipt" in stub["receipt_fragment"]["missing_proof"]
