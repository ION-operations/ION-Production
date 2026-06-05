import json
import subprocess
from pathlib import Path

from kernel.ion_codex_source_bundle_stage_review import (
    BLOCKED_VERDICT,
    PARTIAL_VERDICT,
    WRITE_CONFIRMATION_TOKEN,
    build_codex_source_bundle_stage_review,
    main,
    write_codex_source_bundle_stage_review,
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
    (root / "ION/03_registry").mkdir(parents=True)
    (root / "ION/04_packages/kernel").mkdir(parents=True)
    (root / "ION/tests").mkdir(parents=True)
    _run(["git", "init"], root)
    _run(["git", "config", "user.email", "ion@example.invalid"], root)
    _run(["git", "config", "user.name", "ION Test"], root)
    _run(["git", "add", "pyproject.toml", "ION/REPO_AUTHORITY.md"], root)
    _run(["git", "commit", "-m", "seed"], root)
    return root


def test_source_bundle_stage_review_isolates_source_paths_without_git_mutation(tmp_path: Path) -> None:
    root = _seed_repo(tmp_path)
    (root / "ION/04_packages/kernel/new_kernel.py").write_text("print('candidate')\n", encoding="utf-8")
    (root / "ION/tests/test_new_kernel.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    (root / "ION/02_architecture/CODEX_TEST_PROTOCOL.md").write_text("# protocol\n", encoding="utf-8")
    (root / "ION/05_context/current/codex_carrier/CODEX_SESSION_REGISTRY.json").parent.mkdir(parents=True, exist_ok=True)
    (root / "ION/05_context/current/codex_carrier/CODEX_SESSION_REGISTRY.json").write_text("{}\n", encoding="utf-8")
    (root / "ION/05_context/current/chatgpt_connector/runtime/state.json").parent.mkdir(parents=True, exist_ok=True)
    (root / "ION/05_context/current/chatgpt_connector/runtime/state.json").write_text("{}\n", encoding="utf-8")
    (root / "notes.tmp").write_text("unknown owner\n", encoding="utf-8")

    result = build_codex_source_bundle_stage_review(root)

    assert result["verdict"] == PARTIAL_VERDICT
    assert result["ok"] is True
    assert result["source_bundle_stage_ready"] is True
    assert result["git_mutation_performed"] is False
    assert result["source_bundle"]["path_count"] == 3
    assert "ION/04_packages/kernel/new_kernel.py" in result["source_bundle"]["paths"]
    assert "ION/05_context/current/codex_carrier/CODEX_SESSION_REGISTRY.json" not in result["source_bundle"]["paths"]
    assert any(item["bundle_id"] == "generated_projection_or_local_evidence" for item in result["excluded_bundles"])
    assert any(item["bundle_id"] == "runtime_residue_exclude" for item in result["excluded_bundles"])
    assert any(item["bundle_id"] == "untracked_review_required" for item in result["excluded_bundles"])
    assert result["candidate_stage_manifest"]["source_path_count"] == 3
    assert result["candidate_stage_manifest"]["git_mutation_performed"] is False
    assert result["candidate_stage_manifest"]["candidate_git_add_chunks"]

    status_after = subprocess.run(["git", "status", "--porcelain=v1", "-uall"], cwd=root, check=True, capture_output=True, text=True)
    assert "ION/04_packages/kernel/new_kernel.py" in status_after.stdout


def test_source_bundle_stage_review_blocks_when_boundary_audit_blocks(tmp_path: Path) -> None:
    root = _seed_repo(tmp_path)
    (root / ".env.local").write_text("TOKEN=redacted-test-fixture\n", encoding="utf-8")
    (root / "ION/04_packages/kernel/new_kernel.py").write_text("print('candidate')\n", encoding="utf-8")

    result = build_codex_source_bundle_stage_review(root)

    assert result["verdict"] == BLOCKED_VERDICT
    assert result["ok"] is False
    assert result["source_bundle_stage_ready"] is False
    assert "commit_boundary_audit_not_ok" in result["blocking_findings"]
    assert "private_or_secret_risk_paths_present" in result["blocking_findings"]


def test_source_bundle_stage_review_write_requires_confirmation_and_writes_candidate_manifest(tmp_path: Path, capsys) -> None:
    root = _seed_repo(tmp_path)
    (root / "ION/04_packages/kernel/new_kernel.py").write_text("print('candidate')\n", encoding="utf-8")

    assert main(["--ion-root", str(root), "--write", "--confirmation", "WRONG", "--json"]) == 3
    refused = capsys.readouterr().out
    assert "CONFIRMATION_REQUIRED" in refused

    result = write_codex_source_bundle_stage_review(root)
    assert result["written_paths"] == [
        "ION/05_context/current/codex_carrier/commit_boundary/CODEX_SOURCE_BUNDLE_STAGE_REVIEW.json",
        "ION/05_context/current/codex_carrier/commit_boundary/CODEX_SOURCE_BUNDLE_STAGE_MANIFEST.candidate.json",
    ]
    review_path = root / result["written_paths"][0]
    manifest_path = root / result["written_paths"][1]
    assert review_path.exists()
    assert manifest_path.exists()
    assert json.loads(review_path.read_text())["schema_id"] == "ion.codex_source_bundle_stage_review.v1"
    assert json.loads(manifest_path.read_text())["schema_id"] == "ion.codex_source_bundle_stage_manifest.v1"

    assert main(["--ion-root", str(root), "--write", "--confirmation", WRITE_CONFIRMATION_TOKEN, "--json"]) == 0
    accepted = capsys.readouterr().out
    assert "ION_CODEX_SOURCE_BUNDLE_STAGE_REVIEW" in accepted


def test_mcp_source_bundle_stage_review_is_read_only_projection(tmp_path: Path) -> None:
    root = _seed_repo(tmp_path)
    (root / "ION/04_packages/kernel/new_kernel.py").write_text("print('candidate')\n", encoding="utf-8")
    bridge = IonMcpLocalBridge(root / "ION", tmp_path / "bridge-state")

    result = bridge.call_tool("ion.codex.source_bundle.stage_review", {})

    assert result.execution_resolution == IonMcpExecutionResolution.READ_ONLY
    assert result.kernel_truth_mutated is False
    assert result.live_execution_authorized is False
    assert result.payload["schema_id"] == "ion.codex_source_bundle_stage_review.v1"
    assert result.payload["git_mutation_performed"] is False
    assert result.payload["source_bundle_stage_ready"] is True
