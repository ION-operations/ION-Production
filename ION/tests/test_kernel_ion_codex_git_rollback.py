import json
import subprocess
from pathlib import Path

from kernel.ion_codex_git_rollback import (
    WRITE_CONFIRMATION_TOKEN,
    apply_codex_git_rollback,
    build_codex_git_rollback_model,
    capture_codex_diff_checkpoint,
    preview_codex_git_rollback,
)


SESSION_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def _run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def _seed_git_repo(root: Path) -> Path:
    _run(["git", "init"], root)
    _run(["git", "config", "user.email", "ion@example.test"], root)
    _run(["git", "config", "user.name", "ION Test"], root)
    target = root / "app.py"
    target.write_text("VALUE = 1\n", encoding="utf-8")
    _run(["git", "add", "app.py"], root)
    _run(["git", "commit", "-m", "initial"], root)
    return target


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_codex_git_rollback_captures_previews_and_applies_reverse_patch(tmp_path: Path):
    target = _seed_git_repo(tmp_path)
    target.write_text("VALUE = 2\n", encoding="utf-8")

    captured = capture_codex_diff_checkpoint(
        tmp_path,
        {
            "confirmation": WRITE_CONFIRMATION_TOKEN,
            "session_id": SESSION_ID,
            "turn_id": "turn-1",
            "label": "test rollback",
        },
    )
    preview = preview_codex_git_rollback(tmp_path, {"checkpoint_id": captured["data"]["checkpoint_id"]})
    applied = apply_codex_git_rollback(
        tmp_path,
        {
            "confirmation": WRITE_CONFIRMATION_TOKEN,
            "checkpoint_id": captured["data"]["checkpoint_id"],
        },
    )

    assert captured["ok"] is True
    assert captured["data"]["rollback_supported"] is True
    assert captured["data"]["diff_stats"]["files"] == ["app.py"]
    assert preview["ok"] is True
    assert preview["data"]["rollback_ready"] is True
    assert applied["ok"] is True
    assert target.read_text(encoding="utf-8") == "VALUE = 1\n"


def test_codex_git_rollback_blocks_when_file_drifted_after_checkpoint(tmp_path: Path):
    target = _seed_git_repo(tmp_path)
    target.write_text("VALUE = 2\n", encoding="utf-8")
    captured = capture_codex_diff_checkpoint(
        tmp_path,
        {"confirmation": WRITE_CONFIRMATION_TOKEN, "label": "drift checkpoint"},
    )
    target.write_text("VALUE = 3\n", encoding="utf-8")

    preview = preview_codex_git_rollback(tmp_path, {"checkpoint_id": captured["data"]["checkpoint_id"]})

    assert preview["ok"] is True
    assert preview["data"]["rollback_ready"] is False
    assert "current_file_does_not_match_checkpoint" in preview["data"]["blockers"]


def test_codex_git_rollback_model_includes_archive_diff_evidence(monkeypatch, tmp_path: Path):
    codex_home = tmp_path / "codex-home"
    monkeypatch.setenv("CODEX_HOME", codex_home.as_posix())
    _write_jsonl(codex_home / "session_index.jsonl", [{"id": SESSION_ID, "thread_name": "Diff chat"}])
    _write_jsonl(codex_home / "history.jsonl", [{"session_id": SESSION_ID, "text": "diff chat"}])
    _write_jsonl(
        codex_home / f"sessions/2026/05/24/rollout-{SESSION_ID}.jsonl",
        [
            {"type": "session_meta", "timestamp": "2026-05-24T12:00:00+00:00", "payload": {"id": SESSION_ID}},
            {
                "type": "response_item",
                "timestamp": "2026-05-24T12:01:00+00:00",
                "payload": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "diff --git a/app.py b/app.py\n--- a/app.py\n+++ b/app.py\n@@\n-VALUE = 1\n+VALUE = 2\n",
                        }
                    ],
                },
            },
        ],
    )

    model = build_codex_git_rollback_model(tmp_path, selected_session_id=SESSION_ID)

    assert model["schema_id"] == "ion.codex_git_rollback.v1"
    assert model["summary"]["archive_diff_evidence_count"] == 1
    assert model["archive_diff_evidence"][0]["diff_stats"]["files"] == ["app.py"]
    assert model["archive_diff_evidence"][0]["rollback_supported"] is False


def test_codex_git_rollback_model_distinguishes_dirty_chat_from_greenfield_start(tmp_path: Path):
    target = _seed_git_repo(tmp_path)
    target.write_text("VALUE = 2\n", encoding="utf-8")

    model = build_codex_git_rollback_model(tmp_path)

    assert model["tree_discipline"]["active_chat_mode"] == "dirty_tree_compatible"
    assert model["tree_discipline"]["current_tree_blocks_chat"] is False
    assert model["tree_discipline"]["new_project_mode"] == "clean_tree_required"
    assert model["tree_discipline"]["current_tree_blocks_new_project_start"] is True
    assert model["current_worktree"]["dirty"] is True
    assert model["summary"]["current_file_count"] == 1
    assert model["summary"]["current_added_lines"] == 1
    assert model["summary"]["current_removed_lines"] == 1
    assert model["current_worktree"]["file_edits"][0]["path"] == "app.py"
    assert "+VALUE = 2" in model["current_worktree"]["file_edits"][0]["safe_diff_excerpt"]


def test_codex_git_rollback_model_projects_staged_and_untracked_edits(tmp_path: Path):
    target = _seed_git_repo(tmp_path)
    target.write_text("VALUE = 2\n", encoding="utf-8")
    _run(["git", "add", "app.py"], tmp_path)
    (tmp_path / "new.txt").write_text("new file\n", encoding="utf-8")

    model = build_codex_git_rollback_model(tmp_path)
    worktree = model["current_worktree"]

    assert worktree["staged_file_count"] == 1
    assert worktree["untracked_file_count"] == 1
    assert worktree["diff_stats"]["files"] == ["app.py", "new.txt"]
    assert [row["source"] for row in worktree["file_edits"]] == ["staged", "untracked"]
    assert worktree["file_edits"][1]["safe_diff_excerpt"] == "Untracked file content is not exported by the cockpit diff projection."
