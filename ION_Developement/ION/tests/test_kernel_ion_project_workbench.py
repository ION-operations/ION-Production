import base64
from pathlib import Path

from kernel.ion_project_workbench import (
    WRITE_CONFIRMATION_TOKEN,
    build_project_workbench_timeline,
    build_project_workspace_status,
    project_context_capsule,
    project_browser_capture,
    project_file_read,
    project_file_slice_read,
    project_patch_apply,
    project_patch_preview,
    project_patch_revert,
)


def _seed_cosmos(tmp_path: Path, monkeypatch):
    ion_root = tmp_path / "ion"
    cosmos = tmp_path / "cosmos"
    ion_root.mkdir()
    (cosmos / "src").mkdir(parents=True)
    (cosmos / "src/App.tsx").write_text("export const VALUE = 1;\n", encoding="utf-8")
    (cosmos / "package.json").write_text('{"scripts":{"build":"vite build","test":"vitest run"}}\n', encoding="utf-8")
    monkeypatch.setenv("ION_COSMOS_PROJECT_ROOT", cosmos.as_posix())
    return ion_root, cosmos


def test_project_workspace_status_projects_cosmos(monkeypatch, tmp_path):
    ion_root, cosmos = _seed_cosmos(tmp_path, monkeypatch)

    result = build_project_workspace_status(ion_root, project_id="cosmos")

    assert result["ok"] is True
    assert result["project"]["project_id"] == "cosmos"
    assert result["project"]["root"] == cosmos.as_posix()
    assert result["project"]["preview_base_path"] == "/projects/cosmos/preview/"
    assert "build" in result["package_scripts"]
    assert result["public_preview_allowed"] is True
    assert result["mutations_require_cockpit_auth"] is True


def test_project_file_read_is_scoped_to_allowlist(monkeypatch, tmp_path):
    ion_root, _cosmos = _seed_cosmos(tmp_path, monkeypatch)

    allowed = project_file_read(ion_root, {"project_id": "cosmos", "path": "src/App.tsx"})
    blocked = project_file_read(ion_root, {"project_id": "cosmos", "path": ".env"})

    assert allowed["ok"] is True
    assert "VALUE = 1" in allowed["data"]["text"]
    assert blocked["ok"] is False
    assert blocked["finding"] == "project_path_contains_forbidden_part"


def test_project_patch_preview_apply_and_revert(monkeypatch, tmp_path):
    ion_root, cosmos = _seed_cosmos(tmp_path, monkeypatch)
    target = cosmos / "src/App.tsx"

    operations = [
        {
            "path": "src/App.tsx",
            "old_text": "export const VALUE = 1;\n",
            "new_text": "export const VALUE = 2;\n",
        }
    ]
    preview = project_patch_preview(ion_root, {"project_id": "cosmos", "operations": operations})
    applied = project_patch_apply(
        ion_root,
        {
            "project_id": "cosmos",
            "operations": operations,
            "confirmation": WRITE_CONFIRMATION_TOKEN,
            "idempotency_key": "cosmos-app-value",
        },
    )
    assert applied["ok"] is True
    assert target.read_text(encoding="utf-8") == "export const VALUE = 2;\n"
    replay = project_patch_apply(
        ion_root,
        {
            "project_id": "cosmos",
            "operations": operations,
            "confirmation": WRITE_CONFIRMATION_TOKEN,
            "idempotency_key": "cosmos-app-value",
        },
    )
    reverted = project_patch_revert(
        ion_root,
        {
            "project_id": "cosmos",
            "receipt_path": applied["data"]["receipt_path"],
            "confirmation": WRITE_CONFIRMATION_TOKEN,
        },
    )

    assert preview["ok"] is True
    assert "-export const VALUE = 1;" in preview["data"]["previews"][0]["diff"]
    assert replay["ok"] is True
    assert replay["data"]["idempotent_replay"] is True
    assert reverted["ok"] is True
    assert target.read_text(encoding="utf-8") == "export const VALUE = 1;\n"


def test_project_patch_blocks_non_allowlisted_path(monkeypatch, tmp_path):
    ion_root, cosmos = _seed_cosmos(tmp_path, monkeypatch)
    (cosmos / "random.txt").write_text("x\n", encoding="utf-8")

    result = project_patch_preview(
        ion_root,
        {
            "project_id": "cosmos",
            "path": "random.txt",
            "old_text": "x\n",
            "new_text": "y\n",
        },
    )

    assert result["ok"] is False
    assert result["finding"] == "project_path_not_in_allowlist"


def test_project_browser_capture_is_confirmation_and_bookmark_gated(monkeypatch, tmp_path):
    ion_root, _cosmos = _seed_cosmos(tmp_path, monkeypatch)

    missing_confirmation = project_browser_capture(
        ion_root,
        {"project_id": "cosmos", "bookmark": "orbit"},
    )
    bad_bookmark = project_browser_capture(
        ion_root,
        {"project_id": "cosmos", "bookmark": "not-a-route", "confirmation": WRITE_CONFIRMATION_TOKEN},
    )

    assert missing_confirmation["ok"] is False
    assert missing_confirmation["finding"] == "confirmation_required"
    assert bad_bookmark["ok"] is False
    assert bad_bookmark["finding"] == "project_browser_bookmark_not_allowlisted"
    assert "cloud-terminator" in bad_bookmark["data"]["allowed_bookmarks"]


def test_project_workbench_timeline_compiles_patch_and_visual_history(monkeypatch, tmp_path):
    import json

    ion_root, cosmos = _seed_cosmos(tmp_path, monkeypatch)
    applied = project_patch_apply(
        ion_root,
        {
            "project_id": "cosmos",
            "path": "src/App.tsx",
            "old_text": "export const VALUE = 1;\n",
            "new_text": "export const VALUE = 2;\n",
            "confirmation": WRITE_CONFIRMATION_TOKEN,
            "idempotency_key": "timeline-cosmos-apply",
        },
    )
    capture_receipt = ion_root / "ION/05_context/current/project_workbench/browser_captures/cosmos/20260513T215426Z122134_orbit.json"
    capture_receipt.parent.mkdir(parents=True, exist_ok=True)
    capture_receipt.write_text(
        json.dumps(
            {
                "schema_id": "ion.project_browser_capture_receipt.v1",
                "action": "ion_project_browser_capture",
                "status": "PROJECT_BROWSER_CAPTURE_COMPLETE",
                "project_id": "cosmos",
                "bookmark": "orbit",
                "url": "https://ion.helixion.net/projects/cosmos/preview/cosmos-review?bookmark=orbit&panel=1",
                "created_at": "2026-05-13T21:54:32+00:00",
                "screenshot_path": "ION/05_context/current/project_workbench/browser_captures/cosmos/20260513T215426Z122134_orbit.png",
                "console_errors": [],
                "bad_responses": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    timeline = build_project_workbench_timeline(ion_root, project_id="cosmos", max_items=4)
    timeline_again = build_project_workbench_timeline(ion_root, project_id="cosmos", max_items=4)

    assert applied["ok"] is True
    assert timeline["ok"] is True
    assert timeline["schema_id"] == "ion.project_workbench_timeline.v1"
    assert timeline["project_id"] == "cosmos"
    assert timeline["session"]["session_id"] == timeline_again["session"]["session_id"]
    assert timeline["latest_patch_receipts"][0]["action"] == "ion_project_patch_apply"
    assert timeline["latest_browser_captures"][0]["bookmark"] == "orbit"
    assert timeline["rollback_supported_receipts"][0]["receipt_path"] == applied["data"]["receipt_path"]
    assert timeline["next_recommended_safe_action"]["tool"] == "ion_project_patch_revert"
    assert any(item["bookmark"] == "orbit" for item in timeline["allowed_bookmarks"])


def test_project_context_capsule_compact_shape_and_budget(monkeypatch, tmp_path):
    ion_root, cosmos = _seed_cosmos(tmp_path, monkeypatch)
    (cosmos / "docs/cosmos").mkdir(parents=True, exist_ok=True)
    (cosmos / "docs/cosmos/notes.md").write_text("context\n", encoding="utf-8")

    capsule = project_context_capsule(ion_root, {"project_id": "cosmos", "probe_preview": False})

    assert capsule["ok"] is True
    data = capsule["data"]
    assert data["schema_id"] == "ion.project_context_capsule.v1"
    assert data["project"]["project_id"] == "cosmos"
    assert "src" in data["project"]["allowed_roots"]
    assert "package.json" in data["project"]["allowed_files"]
    assert data["timeline_counters"]["patch_receipt_count"] >= 0
    assert data["size_budget_posture"]["action_gateway_max_body_bytes"] == 262144
    assert data["size_budget_posture"]["capsule_response_bytes"] < data["size_budget_posture"]["action_gateway_max_body_bytes"]
    assert any(item["tool"] == "ion_project_file_slice_read" for item in data["suggested_next_reads"])
    assert all(not row["path"].startswith("../") for row in data["files_index"])


def test_project_file_slice_read_paginates_and_rejects_traversal(monkeypatch, tmp_path):
    ion_root, cosmos = _seed_cosmos(tmp_path, monkeypatch)
    payload = ("0123456789abcdef" * 7000).encode("utf-8")
    target = cosmos / "src/Chunk.txt"
    target.write_bytes(payload)

    first = project_file_slice_read(ion_root, {"project_id": "cosmos", "path": "src/Chunk.txt", "start_byte": 0, "max_bytes": 131072})
    assert first["ok"] is True
    first_data = first["data"]
    assert first_data["start_byte"] == 0
    assert first_data["end_byte"] == 112000
    assert first_data["is_final_chunk"] is True
    assert first_data["slice_cursor"] is None
    assert first_data["sha256_full"] == first_data["sha256_chunk"]
    assert base64.b64decode(first_data["content_b64"].encode("ascii")) == payload

    paged = project_file_slice_read(ion_root, {"project_id": "cosmos", "path": "src/Chunk.txt", "start_byte": 10, "max_bytes": 64})
    assert paged["ok"] is True
    paged_data = paged["data"]
    assert paged_data["start_byte"] == 10
    assert paged_data["end_byte"] == 74
    assert paged_data["is_final_chunk"] is False
    assert paged_data["slice_cursor"]["start_byte"] == 74
    assert paged_data["slice_cursor"]["expected_sha256"] == paged_data["sha256_full"]
    assert base64.b64decode(paged_data["content_b64"].encode("ascii")) == payload[10:74]

    mismatch = project_file_slice_read(
        ion_root,
        {"project_id": "cosmos", "path": "src/Chunk.txt", "start_byte": 0, "max_bytes": 12, "expected_sha256": "deadbeef"},
    )
    traversal = project_file_slice_read(ion_root, {"project_id": "cosmos", "path": "../outside.txt", "start_byte": 0, "max_bytes": 32})

    assert mismatch["ok"] is False
    assert mismatch["finding"] == "expected_sha256_mismatch"
    assert traversal["ok"] is False
    assert traversal["finding"] == "project_path_must_be_relative"
