import json
import subprocess
from pathlib import Path

from kernel.ion_git_root_normalization_preview import (
    WRITE_CONFIRMATION_TOKEN,
    build_git_root_normalization_preview,
    main,
    write_git_root_normalization_preview,
)
from kernel.ion_mcp_local_bridge import IonMcpExecutionResolution, IonMcpLocalBridge


def _run(command, cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)


def _seed_repo(tmp_path: Path) -> Path:
    root = tmp_path / "ion-shell"
    (root / "ION").mkdir(parents=True)
    (root / "ION_Developement/ION/04_packages/kernel").mkdir(parents=True)
    (root / "ION_Developement/ION/05_context/current/execution_cycle/cloudflared").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")
    (root / "ION_Developement/ION/04_packages/kernel/same.py").write_text("VALUE = 'same'\n", encoding="utf-8")
    (root / "ION_Developement/ION/04_packages/kernel/changed.py").write_text("VALUE = 'old'\n", encoding="utf-8")
    (
        root / "ION_Developement/ION/05_context/current/execution_cycle/cloudflared/tunnel.json"
    ).write_text("{\"token\":\"fixture\"}\n", encoding="utf-8")
    _run(["git", "init"], root)
    _run(["git", "config", "user.email", "ion@example.invalid"], root)
    _run(["git", "config", "user.name", "ION Test"], root)
    _run(["git", "add", "pyproject.toml", "ION/REPO_AUTHORITY.md", "ION_Developement"], root)
    _run(["git", "commit", "-m", "legacy-root"], root)
    return root


def test_git_root_normalization_preview_maps_legacy_paths_without_mutation(tmp_path: Path) -> None:
    root = _seed_repo(tmp_path)
    (root / "ION/04_packages/kernel").mkdir(parents=True, exist_ok=True)
    (root / "ION/tests").mkdir(parents=True)
    (root / "ION/05_context/current/execution_cycle/cloudflared").mkdir(parents=True, exist_ok=True)
    (root / "ION/04_packages/kernel/same.py").write_text("VALUE = 'same'\n", encoding="utf-8")
    (root / "ION/04_packages/kernel/changed.py").write_text("VALUE = 'new'\n", encoding="utf-8")
    (root / "ION/04_packages/kernel/new_kernel.py").write_text("VALUE = 'new'\n", encoding="utf-8")
    (root / "ION/tests/test_new_kernel.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    (root / "ION/05_context/current/execution_cycle/cloudflared/tunnel.json").write_text(
        "{\"token\":\"new-fixture\"}\n",
        encoding="utf-8",
    )
    for path in [
        "ION_Developement/ION/04_packages/kernel/same.py",
        "ION_Developement/ION/04_packages/kernel/changed.py",
        "ION_Developement/ION/05_context/current/execution_cycle/cloudflared/tunnel.json",
    ]:
        (root / path).unlink()

    result = build_git_root_normalization_preview(root)

    assert result["schema_id"] == "ion.git_root_normalization_preview.v1"
    assert result["ok"] is True
    assert result["root_normalization_ready"] is False
    assert result["git_mutation_performed"] is False
    assert result["secret_contents_read_or_printed"] is False
    counts = result["tracked_to_active_map_summary"]["classification_counts"]
    assert counts["same_content_relocation_candidate"] == 1
    assert counts["changed_content_relocation_candidate"] == 1
    assert counts["active_exists_path_risk_not_hashed"] == 1
    assert result["new_active_source_summary"]["path_count"] == 2
    assert "ION/04_packages/kernel/new_kernel.py" in result["new_active_source_paths"]
    assert result["secret_risk_path_review"]["path_content_read"] is False
    new_source_chunks = result["candidate_preview_chunks"]["new_active_source_add_chunks"]
    assert new_source_chunks
    assert new_source_chunks[0]["argv_preview"][:3] == ["git", "add", "--"]
    assert "ION/04_packages/kernel/new_kernel.py" in new_source_chunks[0]["argv_preview"]
    assert result["candidate_preview_chunks"]["same_content_active_add_chunks"]
    same_delete_chunks = result["candidate_preview_chunks"]["same_content_tracked_delete_chunks"]
    changed_delete_chunks = result["candidate_preview_chunks"]["changed_content_tracked_delete_review_chunks"]
    path_risk_delete_chunks = result["candidate_preview_chunks"]["path_risk_tracked_delete_review_chunks"]
    assert "ION_Developement/ION/04_packages/kernel/same.py" in same_delete_chunks[0]["argv_preview"]
    assert "ION_Developement/ION/04_packages/kernel/changed.py" in changed_delete_chunks[0]["argv_preview"]
    assert (
        "ION_Developement/ION/05_context/current/execution_cycle/cloudflared/tunnel.json"
        in path_risk_delete_chunks[0]["argv_preview"]
    )

    status_after = subprocess.run(["git", "status", "--porcelain=v1", "-uall"], cwd=root, check=True, capture_output=True, text=True)
    assert "D ION_Developement/ION/04_packages/kernel/same.py" in status_after.stdout
    assert "?? ION/04_packages/kernel/same.py" in status_after.stdout


def test_git_root_normalization_preview_write_requires_confirmation(tmp_path: Path, capsys) -> None:
    root = _seed_repo(tmp_path)

    assert main(["--ion-root", str(root), "--write", "--confirmation", "WRONG", "--json"]) == 3
    refused = capsys.readouterr().out
    assert "CONFIRMATION_REQUIRED" in refused

    result = write_git_root_normalization_preview(root)
    assert result["written_paths"] == [
        "ION/05_context/current/repo_organization/GIT_ROOT_NORMALIZATION_PREVIEW.candidate.json",
        "ION/05_context/current/repo_organization/GIT_ROOT_NORMALIZATION_PREVIEW_SUMMARY.candidate.json",
        "ION/05_context/current/repo_organization/GIT_ROOT_NORMALIZATION_PREVIEW.candidate.md",
    ]
    assert json.loads((root / result["written_paths"][0]).read_text())["schema_id"] == "ion.git_root_normalization_preview.v1"
    summary = json.loads((root / result["written_paths"][1]).read_text())
    assert summary["schema_id"] == "ion.git_root_normalization_preview_summary.v1"
    assert "new_active_source_stage_preview" in summary
    assert "root_normalization_delete_preview" in summary
    assert summary["root_normalization_delete_preview"]["active_missing_review"]["path_count"] == 3
    assert (root / result["written_paths"][2]).read_text().startswith("# Git Root Normalization Preview")

    assert main(["--ion-root", str(root), "--write", "--confirmation", WRITE_CONFIRMATION_TOKEN, "--json"]) == 0
    accepted = capsys.readouterr().out
    assert "ion.git_root_normalization_preview.v1" in accepted


def test_mcp_git_root_normalization_preview_is_read_only_projection(tmp_path: Path) -> None:
    root = _seed_repo(tmp_path)
    bridge = IonMcpLocalBridge(root / "ION", tmp_path / "bridge-state")

    result = bridge.call_tool("ion.git.root_normalization.preview", {})

    assert result.execution_resolution == IonMcpExecutionResolution.READ_ONLY
    assert result.kernel_truth_mutated is False
    assert result.live_execution_authorized is False
    assert result.payload["schema_id"] == "ion.git_root_normalization_preview.v1"
    assert result.payload["git_mutation_performed"] is False
