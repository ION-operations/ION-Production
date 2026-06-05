from __future__ import annotations

import json
from pathlib import Path

import pytest

from kernel.ion_domain_weaver_proposal_wave import (
    PROPOSAL_WAVE_PLAN_SCHEMA_ID,
    PROPOSAL_WORKSPACE_SEED_SCHEMA_ID,
    PROPOSAL_WORKSPACE_SCHEMA_ID,
    PROPOSAL_WRITE_CONFIRMATION,
    build_proposal_wave_plan,
    seed_proposal_workspaces,
)


def _active_root(tmp_path: Path) -> Path:
    root = tmp_path / "active"
    (root / "ION").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = 'ion-test'\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").write_text("test authority\n", encoding="utf-8")
    return root


def test_proposal_wave_plan_expands_past_native_slots_without_source_authority(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)

    plan = build_proposal_wave_plan(
        root,
        native_slot_cap=6,
        active_native_agent_count=3,
    )

    assert plan["schema_id"] == PROPOSAL_WAVE_PLAN_SCHEMA_ID
    assert plan["status"] == "proposal_wave_plan_built"
    assert plan["lane_count"] == 12
    assert plan["caps"]["native_slot_cap"] == 6
    assert plan["caps"]["active_native_agent_count"] == 3
    assert plan["caps"]["available_native_slots"] == 3
    assert plan["caps"]["raw_source_write_allowed"] is False
    assert plan["caps"]["patch_apply_allowed"] is False
    assert plan["caps"]["recursive_child_spawn_cap"] == 0
    assert plan["lane_counts"]["foreground_native_assignable_count"] == 3
    assert plan["lane_counts"]["overflow_proposal_workspace_count"] == 9
    assert plan["lane_counts"]["proposal_workspace_template_count"] == 12
    assert plan["actual_spawn_performed"] is False
    assert plan["codex_queue_run_started"] is False
    assert plan["worker_start_allowed"] is False
    assert plan["accepted_state_claimed"] is False
    assert plan["product_state_accepted"] is False
    assert plan["blockers"] == []
    assert "T2_PATCH_PROPOSAL_WRITER" in plan["tier_model"]
    assert all(row["raw_source_write_allowed"] is False for row in plan["lanes"])
    assert all(row["patch_apply_allowed"] is False for row in plan["lanes"])
    assert (
        "any_worker_applies_patch_or_edits_source_without_lead_apply_gate"
        in plan["hard_stop_conditions"]
    )


def test_proposal_workspace_seed_preview_does_not_write(tmp_path: Path) -> None:
    root = _active_root(tmp_path)

    preview = seed_proposal_workspaces(
        root,
        execute_write=False,
        wave_id="preview-wave",
        limit=2,
    )

    assert preview["schema_id"] == PROPOSAL_WORKSPACE_SEED_SCHEMA_ID
    assert preview["status"] == "proposal_workspace_seed_preview"
    assert preview["workspace_count"] == 0
    assert len(preview["workspace_templates"]) == 2
    assert preview["actual_spawn_performed"] is False
    assert preview["codex_queue_run_started"] is False
    assert not (root / "ION/05_context/current/domain_weaver/proposal_wave/preview-wave").exists()


def test_proposal_workspace_seed_requires_full_write_gate(tmp_path: Path) -> None:
    root = _active_root(tmp_path)

    blocked = seed_proposal_workspaces(
        root,
        execute_write=True,
        confirmation=PROPOSAL_WRITE_CONFIRMATION,
        idempotency_key="proposal-wave",
        agent_id="codex_cli:test-proposal-wave",
        wave_id="proposal-wave",
        limit=1,
    )

    assert blocked["status"] == "proposal_workspace_seed_blocked"
    assert blocked["write_gate"]["ok"] is False
    assert "write_intent_lease_id_required" in blocked["write_gate"]["blockers"]
    assert blocked["workspace_count"] == 0
    assert not (root / "ION/05_context/current/domain_weaver/proposal_wave/proposal-wave").exists()


def test_proposal_workspace_seed_writes_only_boxed_lane_files_and_replays(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)

    seeded = seed_proposal_workspaces(
        root,
        execute_write=True,
        confirmation=PROPOSAL_WRITE_CONFIRMATION,
        idempotency_key="proposal-wave",
        agent_id="codex_cli:test-proposal-wave",
        write_intent_lease_id="lease-proposal-wave",
        wave_id="proposal-wave",
        limit=3,
    )
    replay = seed_proposal_workspaces(
        root,
        execute_write=True,
        confirmation=PROPOSAL_WRITE_CONFIRMATION,
        idempotency_key="proposal-wave",
        agent_id="codex_cli:test-proposal-wave",
        write_intent_lease_id="lease-proposal-wave",
        wave_id="proposal-wave",
        limit=3,
    )

    assert seeded["status"] == "proposal_workspaces_seeded"
    assert seeded["workspace_count"] == 3
    assert seeded["actual_spawn_performed"] is False
    assert seeded["codex_queue_run_started"] is False
    assert seeded["worker_start_allowed"] is False
    assert seeded["accepted_state_claimed"] is False
    assert seeded["product_state_accepted"] is False
    for workspace in seeded["workspaces"]:
        rel = Path(workspace["workspace_path"])
        assert rel.parts[:5] == (
            "ION",
            "05_context",
            "current",
            "domain_weaver",
            "proposal_wave",
        )
        workspace_json = root / workspace["workspace_json_path"]
        payload = json.loads(workspace_json.read_text(encoding="utf-8"))
        assert payload["schema_id"] == PROPOSAL_WORKSPACE_SCHEMA_ID
        assert payload["status"] == "proposal_workspace_seeded"
        assert payload["authority"]["raw_source_write_authority"] is False
        assert payload["authority"]["patch_apply_authority"] is False
        assert payload["accepted_state_claimed"] is False
        assert (root / workspace["receipt_path"]).is_file()
        assert (root / workspace["workspace_path"] / "README.md").is_file()
        assert (root / workspace["workspace_path"] / "proposal.candidate.md").is_file()
    assert replay["workspace_count"] == 3
    assert sorted(replay["idempotent_replay_paths"]) == sorted(seeded["workspace_paths"])


def test_proposal_workspace_seed_rejects_paths_outside_proposal_root(tmp_path: Path) -> None:
    root = _active_root(tmp_path)

    with pytest.raises(ValueError, match="proposal_root_must_stay_under"):
        seed_proposal_workspaces(
            root,
            proposal_root="ION/05_context/current/domain_weaver/not_proposal_wave",
            execute_write=False,
        )
