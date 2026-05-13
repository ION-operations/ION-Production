import json
import subprocess
from pathlib import Path

from kernel.ion_codex_commit_boundary_audit import (
    BLOCKED_VERDICT,
    PARTIAL_VERDICT,
    READY_VERDICT,
    WRITE_CONFIRMATION_TOKEN,
    build_codex_commit_boundary_audit,
    main,
    write_codex_commit_boundary_audit,
)
from kernel.ion_mcp_local_bridge import IonMcpExecutionResolution, IonMcpLocalBridge


def _run(command, cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)


def _seed_repo(tmp_path: Path) -> Path:
    root = tmp_path / "ion-shell"
    (root / "ION").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").parent.mkdir(parents=True, exist_ok=True)
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")
    (root / "ION/02_architecture").mkdir(parents=True)
    (root / "ION/04_packages/kernel").mkdir(parents=True)
    (root / "ION/tests").mkdir(parents=True)
    _run(["git", "init"], root)
    _run(["git", "config", "user.email", "ion@example.invalid"], root)
    _run(["git", "config", "user.name", "ION Test"], root)
    _run(["git", "add", "pyproject.toml", "ION/REPO_AUTHORITY.md"], root)
    _run(["git", "commit", "-m", "seed"], root)
    return root


def test_commit_boundary_audit_classifies_dirty_tree_without_git_mutation(tmp_path: Path) -> None:
    root = _seed_repo(tmp_path)
    (root / "ION/04_packages/kernel/new_kernel.py").write_text("print('candidate')\n", encoding="utf-8")
    (root / "ION/tests/test_new_kernel.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    (root / "ION/05_context/current/codex_carrier/CODEX_SESSION_REGISTRY.json").parent.mkdir(parents=True, exist_ok=True)
    (root / "ION/05_context/current/codex_carrier/CODEX_SESSION_REGISTRY.json").write_text("{}\n", encoding="utf-8")
    (root / "ION/05_context/current/chatgpt_connector/runtime/state.json").parent.mkdir(parents=True, exist_ok=True)
    (root / "ION/05_context/current/chatgpt_connector/runtime/state.json").write_text("{}\n", encoding="utf-8")

    result = build_codex_commit_boundary_audit(root)

    assert result["verdict"] in {READY_VERDICT, PARTIAL_VERDICT}
    assert result["ok"] is True
    assert result["git_mutation_performed"] is False
    assert result["git"]["dirty"] is True
    assert result["path_counts"]["source_protocol_schema_tests"] == 2
    assert result["path_counts"]["generated_projection_or_local_evidence"] == 1
    assert result["path_counts"]["runtime_residue_exclude"] == 1
    source_bundle = next(bundle for bundle in result["bundles"] if bundle["bundle_id"] == "source_protocol_schema_tests")
    assert "ION/04_packages/kernel/new_kernel.py" in source_bundle["paths"]
    manifest_groups = result["candidate_stage_manifest"]["stage_groups"]
    assert any(group["bundle_id"] == "source_protocol_schema_tests" for group in manifest_groups)

    status_after = subprocess.run(["git", "status", "--porcelain=v1", "-uall"], cwd=root, check=True, capture_output=True, text=True)
    assert "ION/04_packages/kernel/new_kernel.py" in status_after.stdout


def test_commit_boundary_audit_blocks_secretish_paths(tmp_path: Path) -> None:
    root = _seed_repo(tmp_path)
    (root / ".env.local").write_text("TOKEN=redacted-test-fixture\n", encoding="utf-8")

    result = build_codex_commit_boundary_audit(root)

    assert result["verdict"] == BLOCKED_VERDICT
    assert result["ok"] is False
    assert result["path_counts"]["private_or_secret_risk_exclude"] == 1
    assert "private_or_secret_risk_paths_present" in result["blocking_findings"]


def test_commit_boundary_write_requires_confirmation_and_writes_candidate_manifest(tmp_path: Path, capsys) -> None:
    root = _seed_repo(tmp_path)
    (root / "ION/02_architecture/CODEX_TEST_PROTOCOL.md").write_text("# protocol\n", encoding="utf-8")

    assert main(["--ion-root", str(root), "--write", "--confirmation", "WRONG", "--json"]) == 3
    refused = capsys.readouterr().out
    assert "CONFIRMATION_REQUIRED" in refused

    result = write_codex_commit_boundary_audit(root)
    assert result["written_paths"] == [
        "ION/05_context/current/codex_carrier/commit_boundary/CODEX_COMMIT_BOUNDARY_AUDIT.json",
        "ION/05_context/current/codex_carrier/commit_boundary/CODEX_COMMIT_STAGE_MANIFEST.candidate.json",
    ]
    audit_path = root / result["written_paths"][0]
    manifest_path = root / result["written_paths"][1]
    assert audit_path.exists()
    assert manifest_path.exists()
    assert json.loads(audit_path.read_text())["schema_id"] == "ion.codex_commit_boundary_audit.v1"
    assert json.loads(manifest_path.read_text())["schema_id"] == "ion.codex_commit_stage_manifest.v1"

    assert main(["--ion-root", str(root), "--write", "--confirmation", WRITE_CONFIRMATION_TOKEN, "--json"]) == 0
    accepted = capsys.readouterr().out
    assert "ION_CODEX_COMMIT_BOUNDARY_AUDIT" in accepted


def test_mcp_commit_boundary_audit_is_read_only_projection(tmp_path: Path) -> None:
    root = _seed_repo(tmp_path)
    (root / "ION/04_packages/kernel/new_kernel.py").write_text("print('candidate')\n", encoding="utf-8")
    bridge = IonMcpLocalBridge(root / "ION", tmp_path / "bridge-state")

    result = bridge.call_tool("ion.codex.commit_boundary.audit", {})

    assert result.execution_resolution == IonMcpExecutionResolution.READ_ONLY
    assert result.kernel_truth_mutated is False
    assert result.live_execution_authorized is False
    assert result.payload["schema_id"] == "ion.codex_commit_boundary_audit.v1"
    assert result.payload["git_mutation_performed"] is False
