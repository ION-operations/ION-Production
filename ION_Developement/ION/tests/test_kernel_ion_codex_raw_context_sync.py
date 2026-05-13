from pathlib import Path

import pytest

from kernel.ion_codex_raw_context_sync import (
    LANE_READY_VERDICT,
    WRITE_CONFIRMATION_TOKEN,
    build_raw_context_sync_lane_status,
    create_raw_context_manifest,
    initialize_raw_context_sync_lane,
    main,
)


def _minimal_shell_root(tmp_path: Path) -> Path:
    root = tmp_path / "ion-shell"
    (root / "ION" / "02_architecture").mkdir(parents=True)
    (root / "ION" / "05_context" / "current" / "agent_context_branches" / "unit" / "branch-1").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    (root / "ION" / "REPO_AUTHORITY.md").write_text("# repo authority\n", encoding="utf-8")
    (root / "ION" / "02_architecture" / "CODEX_RAW_CONTEXT_SYNC_LANE_PROTOCOL.md").write_text(
        "# Raw context protocol\n", encoding="utf-8"
    )
    return root


def test_raw_context_sync_lane_initializes_policy_and_gitignore_guard(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)

    before = build_raw_context_sync_lane_status(root)
    assert before["ok"] is False
    assert "missing_raw_context_policy:ION/05_context/current/codex_carrier/CODEX_RAW_CONTEXT_SYNC_LANE_POLICY.md" in before["findings"]

    result = initialize_raw_context_sync_lane(root)

    assert result["verdict"] == LANE_READY_VERDICT
    assert (root / "ION/05_context/current/codex_carrier/CODEX_RAW_CONTEXT_SYNC_LANE_POLICY.md").exists()
    assert ".ion_private/codex_raw_context/" in (root / ".gitignore").read_text(encoding="utf-8")
    after = build_raw_context_sync_lane_status(root)
    assert after["ok"] is True
    assert after["raw_content_exported"] is False
    assert after["production_authority"] is False
    assert after["live_execution_authority"] is False


def test_create_raw_context_manifest_is_public_safe_and_branch_bound(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    initialize_raw_context_sync_lane(root)
    branch = "ION/05_context/current/agent_context_branches/unit/branch-1"

    manifest = create_raw_context_manifest(
        root,
        agent_tag="codex_local_ion_mason",
        session_id="codex_session_unit",
        branch_id="branch_unit",
        packet_id="PCKT-UNIT-RAW-CONTEXT",
        branch_capsule=branch,
        diagnostic_summary="Build failure only reproduced after resumed session context; no raw text exported.",
    )

    assert manifest["schema_id"] == "ion.codex_raw_context_manifest.v1"
    assert manifest["snapshot_content_committed"] is False
    assert manifest["snapshot_mirrored_externally"] is False
    assert manifest["authority"]["accepted_state_authority"] is False
    assert manifest["diagnostic_summary"].startswith("Build failure")
    assert (root / manifest["path"]).exists()
    assert (root / branch / "RAW_CONTEXT_MANIFEST.json").exists()
    status = build_raw_context_sync_lane_status(root)
    assert status["manifest_count"] == 1


def test_raw_context_manifest_rejects_secret_like_diagnostic_summary(tmp_path: Path) -> None:
    root = _minimal_shell_root(tmp_path)
    initialize_raw_context_sync_lane(root)

    with pytest.raises(ValueError):
        create_raw_context_manifest(
            root,
            agent_tag="codex_local_ion_mason",
            session_id="codex_session_unit",
            branch_id="branch_unit",
            packet_id="PCKT-UNIT-RAW-CONTEXT",
            diagnostic_summary="bad bearer abcdefghijklmnop",
        )


def test_raw_context_cli_requires_confirmation_for_writes(tmp_path: Path, capsys) -> None:
    root = _minimal_shell_root(tmp_path)

    assert main(["init", "--ion-root", str(root), "--confirmation", "WRONG", "--json"]) == 3
    refused = capsys.readouterr().out
    assert "CONFIRMATION_REQUIRED" in refused

    assert main(["init", "--ion-root", str(root), "--confirmation", WRITE_CONFIRMATION_TOKEN, "--json"]) == 0
    accepted = capsys.readouterr().out
    assert LANE_READY_VERDICT in accepted
