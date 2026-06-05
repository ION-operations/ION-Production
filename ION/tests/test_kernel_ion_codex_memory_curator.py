from __future__ import annotations

import json
import subprocess
from pathlib import Path

from kernel.ion_codex_memory_curator import (
    AD_HOC_NOTE_SCHEMA_ID,
    build_ad_hoc_memory_note,
    classify_memory_path,
    diff_memory_snapshots,
    snapshot_memory_workspace,
    write_ad_hoc_memory_note,
)


def _memory_root(tmp_path: Path) -> Path:
    root = tmp_path / "memories"
    (root / "extensions/ad_hoc").mkdir(parents=True)
    (root / "rollout_summaries").mkdir()
    (root / "MEMORY.md").write_text(
        "# Task Group: ION carrier evidence\n\n"
        "## User preferences\n\n"
        "- user said keep repo-observed and MCP-observed separate.\n",
        encoding="utf-8",
    )
    (root / "memory_summary.md").write_text(
        "## User Profile\n\n"
        "Project-orientation note: ION is being actively developed and dogfooded. [ad-hoc note]\n",
        encoding="utf-8",
    )
    (root / "raw_memories.md").write_text(
        "# Raw Memories\n\n"
        "Reusable knowledge and stale listener blocker evidence.\n",
        encoding="utf-8",
    )
    (root / "extensions/ad_hoc/0001_developing_and_dogfooding_ion.md").write_text(
        "# Memory 0001 - ION Dogfooding\n\n"
        "Core framing: ION is the system under development and dogfooded carrier continuity layer.\n",
        encoding="utf-8",
    )
    (root / "rollout_summaries/run.md").write_text(
        "# Run\n\n"
        "The live listener was stale and queue-runner validation passed.\n",
        encoding="utf-8",
    )
    (root / "ION_CONTEXT_RECOVERY_BOOTSTRAP.md").write_text("lost Codex chat recovery bootstrap\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(
        ["git", "-c", "user.email=test@example.invalid", "-c", "user.name=Test", "commit", "-qm", "baseline"],
        cwd=root,
        check=True,
    )
    return root


def test_snapshot_classifies_visible_memory_artifact_layer(tmp_path: Path) -> None:
    root = _memory_root(tmp_path)

    snapshot = snapshot_memory_workspace(root)

    by_path = {item["path"]: item for item in snapshot["files"]}
    assert snapshot["schema_id"] == "ion.codex_memory_workspace_snapshot.v0_1"
    assert snapshot["git_head"]
    assert snapshot["git_status_short"] == []
    assert by_path["MEMORY.md"]["classification"]["generated"] is True
    assert "generated_summary" in by_path["MEMORY.md"]["classification"]["classes"]
    assert "user_preference" in by_path["MEMORY.md"]["classification"]["classes"]
    assert "generated_raw_memory" in by_path["raw_memories.md"]["classification"]["classes"]
    assert by_path["extensions/ad_hoc/0001_developing_and_dogfooding_ion.md"]["classification"][
        "contribution_lane"
    ] == "ad_hoc"
    assert "ad_hoc_note" in by_path["extensions/ad_hoc/0001_developing_and_dogfooding_ion.md"]["classification"][
        "classes"
    ]
    assert "rollout_evidence" in by_path["rollout_summaries/run.md"]["classification"]["classes"]
    assert "recovery_bootstrap" in by_path["ION_CONTEXT_RECOVERY_BOOTSTRAP.md"]["classification"]["classes"]
    assert snapshot["authority"]["memory_is_recall_not_authority"] is True


def test_classification_detects_secret_like_content_without_emitting_values() -> None:
    result = classify_memory_path("extensions/ad_hoc/token_note.md", "api_key = sk-secret-value-that-must-not-print")

    assert "unsafe_secret_like_content" in result["classes"]
    encoded = json.dumps(result)
    assert "sk-secret-value" not in encoded


def test_ad_hoc_note_builder_declares_recall_boundary() -> None:
    note = build_ad_hoc_memory_note(
        title="ION Dogfooding",
        body="We are developing and dogfooding ION.",
        source="operator-requested",
        memory_classes=("project_convention", "stable_workflow_fact"),
        created_at="2026-05-15T00:00:00+00:00",
    )

    assert f"schema_id: {AD_HOC_NOTE_SCHEMA_ID}" in note
    assert "contribution_lane: extensions/ad_hoc" in note
    assert "memory_is_recall_not_authority: true" in note
    assert "accepted_state_claim: false" in note
    assert "We are developing and dogfooding ION." in note


def test_write_ad_hoc_memory_note_is_dry_run_by_default(tmp_path: Path) -> None:
    root = _memory_root(tmp_path)

    dry = write_ad_hoc_memory_note(
        memory_root=root,
        title="Dry Run",
        body="This should not write yet.",
        memory_classes=("stable_workflow_fact",),
    )

    assert dry["wrote"] is False
    assert dry["relative_path"].startswith("extensions/ad_hoc/")
    assert not (root / dry["relative_path"]).exists()

    written = write_ad_hoc_memory_note(
        memory_root=root,
        title="Dry Run",
        body="This should write now.",
        memory_classes=("stable_workflow_fact",),
        write=True,
    )
    assert written["wrote"] is True
    assert (root / written["relative_path"]).is_file()
    assert len(written["sha256"]) == 64


def test_diff_memory_snapshots_tracks_generated_and_contribution_changes(tmp_path: Path) -> None:
    root = _memory_root(tmp_path)
    before = snapshot_memory_workspace(root)
    (root / "MEMORY.md").write_text("# Task Group\n\nGenerated memory changed.\n", encoding="utf-8")
    (root / "extensions/ad_hoc/new_note.md").write_text("# New note\n\nA contribution.\n", encoding="utf-8")
    after = snapshot_memory_workspace(root)

    diff = diff_memory_snapshots(before, after)

    assert diff["schema_id"] == "ion.codex_memory_workspace_diff.v0_1"
    assert "MEMORY.md" in diff["changed_paths"]
    assert "MEMORY.md" in diff["generated_paths_changed"]
    assert "extensions/ad_hoc/new_note.md" in diff["added_paths"]
    assert "extensions/ad_hoc/new_note.md" in diff["contribution_paths_changed"]
    assert diff["classification"] == "generated_consolidation_observed"
    assert "does not reveal Codex memory scoring" in diff["inference_boundary"]
