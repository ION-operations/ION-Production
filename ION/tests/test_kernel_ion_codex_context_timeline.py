import json
from pathlib import Path

from kernel.ion_codex_context_timeline import (
    SCHEMA_ID,
    build_codex_context_timeline_model,
)


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _checkpoint(root: Path, stamp: str, capsule_id: str, mini_text: str, capsule_tail: list[str], summary: str) -> None:
    payload = {
        "schema_id": "ion.codex_solo_post_checkpoint.v1",
        "checkpoint_id": f"codex_solo_post_{stamp}",
        "capsule_entry_id": capsule_id,
        "created_at": f"2026-05-24T{stamp[9:11]}:{stamp[11:13]}:{stamp[13:15]}+00:00",
        "status": "SETTLED_CANDIDATE",
        "summary": summary,
        "evidence_paths": [f"ION/evidence/{capsule_id}.json"],
        "production_authority": False,
        "live_execution_authority": False,
        "model": {
            "mini": {
                "ok": True,
                "role": "lookup_receipt_index_for_capsule_history",
                "line_count": len(mini_text.splitlines()),
                "max_lines": 30,
                "text": mini_text,
                "findings": [],
            },
            "capsule": {
                "ok": True,
                "path": "ION/05_context/current/codex_solo/CAPSULE.md",
                "entry_count": int(capsule_id.split("-")[-1]),
                "tail": capsule_tail,
                "recent_rows": [{"id": capsule_id, "summary": summary}],
                "findings": [],
            },
            "hot_context": {
                "ok": True,
                "path": "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
                "bytes": 1000 + int(capsule_id.split("-")[-1]),
            },
            "long_horizon": {
                "path": "ION/05_context/current/codex_solo/LONG_HORIZON.json",
                "epoch_count": 1,
                "capsule_entry_count": int(capsule_id.split("-")[-1]),
                "latest_epochs": [{"epoch_id": "E-001", "summary": summary}],
            },
            "route": {
                "schema_id": "ion.codex_solo_route_validation.v1",
                "ok": True,
                "entries": [{"path": "ION/05_context/current/codex_solo/CAPSULE.md", "required": True, "exists": True}],
                "findings": [],
                "production_authority": False,
                "live_execution_authority": False,
            },
            "context_packages": {
                "path": "ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json",
                "package_count": 1,
                "selected_by_default": ["minimum_working_capsule"],
                "packages": [{"package_id": "minimum_working_capsule", "path_refs": ["ION/05_context/current/codex_solo/CAPSULE.md"]}],
            },
        },
    }
    _write(root, f"ION/05_context/current/codex_solo/history/codex_solo_post_{stamp}.json", json.dumps(payload))


def _seed_root(root: Path) -> None:
    _write(root, "pyproject.toml", "[project]\nname = \"ion-test\"\n")
    _write(root, "ION/REPO_AUTHORITY.md", "# authority\n")
    _write(root, "ION/05_context/current/codex_solo/MINI.md", "CODEX SOLO MINI INDEX\nLAST_RECEIPT: current context\n- C-002 current\n")
    _write(root, "ION/05_context/current/codex_solo/CAPSULE.md", "# Capsule\n| C-001 | old context |\n| C-002 | current context |\n")
    _write(root, "ION/05_context/current/codex_solo/HOT_CONTEXT.md", "# Hot\ncurrent boot context\n")
    _write(root, "ION/05_context/current/codex_solo/LONG_HORIZON.json", json.dumps({"epoch_count": 1, "capsule_entry_count": 2, "epochs": [{"epoch_id": "E-001"}]}))
    _write(
        root,
        "ION/05_context/current/codex_solo/ROUTE.json",
        json.dumps({"entries": [{"path": "ION/05_context/current/codex_solo/CAPSULE.md", "required": True, "exists": True}], "findings": []}),
    )
    _write(
        root,
        "ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json",
        json.dumps({"package_count": 1, "selected_by_default": ["minimum_working_capsule"], "packages": [{"package_id": "minimum_working_capsule"}]}),
    )
    _write(root, "ION/05_context/current/codex_solo/STATUS.json", json.dumps({"status": "ready", "latest": "C-002"}))
    _write(root, "ION/05_context/current/codex_solo/CODEX_CARRIER_LIMITS_CONTEXT.json", json.dumps({"limits": [{"id": "context_window"}]}))
    _write(root, "ION/05_context/current/codex_solo/ION_CONTEXT_CAPSULE.candidate.yaml", "status: candidate\n")
    _write(root, "ION/05_context/current/codex_cli/hooks/runtime/postcompact/receipt.json", "{\"summary\":\"context compact boundary preserved capsule\"}\n")
    _checkpoint(
        root,
        "20260524T010000+0000",
        "C-001",
        "CODEX SOLO MINI INDEX\nLAST_RECEIPT: old context\n- C-001 old\n",
        ["| C-001 | old context |"],
        "old context",
    )
    _checkpoint(
        root,
        "20260524T020000+0000",
        "C-002",
        "CODEX SOLO MINI INDEX\nLAST_RECEIPT: new context\n- C-001 old\n- C-002 new\n",
        ["| C-001 | old context |", "| C-002 | new context |"],
        "new context",
    )


def test_codex_context_timeline_builds_surface_diff_lanes_and_boundaries(tmp_path: Path) -> None:
    _seed_root(tmp_path)

    model = build_codex_context_timeline_model(tmp_path)

    assert model["schema_id"] == SCHEMA_ID
    assert model["visibility_contract"]["hidden_reasoning_exposed"] is False
    assert model["production_authority"] is False
    assert model["summary"]["surface_count"] >= 9
    assert model["summary"]["history_snapshot_count"] == 2
    assert model["summary"]["diff_event_count"] >= 1
    assert model["summary"]["boundary_event_count"] == 1
    assert model["topology"]["required_route_ref_count"] == 1
    assert model["topology"]["selected_package_count"] == 1

    mini_lane = next(lane for lane in model["lanes"] if lane["surface_id"] == "mini")
    assert mini_lane["change_count"] >= 1

    diff_events = [event for event in model["timeline"] if event["surface_changes"]]
    assert any(change["surface_id"] == "mini" for event in diff_events for change in event["surface_changes"])
    assert any("+LAST_RECEIPT" in change["diff_excerpt"] or "-LAST_RECEIPT" in change["diff_excerpt"] for event in diff_events for change in event["surface_changes"])
