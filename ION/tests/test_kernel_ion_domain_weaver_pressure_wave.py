from __future__ import annotations

import json
from pathlib import Path

from kernel.ion_domain_weaver_pressure_wave import (
    PRESSURE_WAVE_CONFIRMATION,
    PRESSURE_WAVE_PLAN_SCHEMA_ID,
    PRESSURE_WAVE_SPAWN_REQUEST_SEED_SCHEMA_ID,
    build_pressure_wave_plan,
    seed_pressure_wave_spawn_requests,
)


def _active_root(tmp_path: Path) -> Path:
    root = tmp_path / "active"
    (root / "ION").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = 'ion-test'\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").write_text("test authority\n", encoding="utf-8")
    return root


def test_pressure_wave_plan_batches_over_native_slot_cap_without_spawning(tmp_path: Path) -> None:
    root = _active_root(tmp_path)

    plan = build_pressure_wave_plan(
        root,
        native_slot_cap=6,
        active_native_agent_count=3,
        exact_queue_start_cap=2,
    )

    assert plan["schema_id"] == PRESSURE_WAVE_PLAN_SCHEMA_ID
    assert plan["status"] == "pressure_wave_plan_built"
    assert plan["lane_count"] == 12
    assert plan["caps"]["native_slot_cap"] == 6
    assert plan["caps"]["active_native_agent_count"] == 3
    assert plan["caps"]["available_native_slots"] == 3
    assert plan["caps"]["exact_queue_start_cap"] == 2
    assert plan["caps"]["recursive_child_spawn_cap"] == 0
    assert plan["caps"]["general_queue_processing_allowed"] is False
    assert plan["lane_counts"]["foreground_native_batch_count"] == 3
    assert plan["lane_counts"]["overflow_durable_spawn_row_count"] == 9
    assert plan["lane_counts"]["native_batch_count"] == 2
    assert plan["actual_spawn_performed"] is False
    assert plan["direct_nested_spawn"] is False
    assert plan["recursive_child_spawn_allowed"] is False
    assert plan["codex_queue_run_started"] is False
    assert plan["worker_start_allowed"] is False
    assert plan["accepted_state_claimed"] is False
    assert plan["exact_queue_start_plan"]["general_queue_processing_allowed"] is False
    assert (
        "any_dispatch_receipt_with_connector_ok_false_counts_as_enqueued"
        in plan["hard_stop_conditions"]
    )
    assert len(plan["durable_spawn_request_templates"]) == 9
    assert plan["durable_spawn_request_templates"][0]["actual_spawn_performed"] is False


def test_pressure_wave_seed_preview_does_not_write_spawn_requests(tmp_path: Path) -> None:
    root = _active_root(tmp_path)

    preview = seed_pressure_wave_spawn_requests(root, execute_write=False, limit=2)

    assert preview["schema_id"] == PRESSURE_WAVE_SPAWN_REQUEST_SEED_SCHEMA_ID
    assert preview["status"] == "pressure_wave_spawn_request_seed_preview"
    assert preview["spawn_request_count"] == 0
    assert len(preview["spawn_request_templates"]) == 2
    assert preview["actual_spawn_performed"] is False
    assert preview["codex_queue_run_started"] is False
    assert not list((root / "ION/05_context/current/domain_weaver/workers").glob("**/*.spawn_request.json"))


def test_pressure_wave_seed_writes_worker_local_rows_only_when_gate_is_complete(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    blocked = seed_pressure_wave_spawn_requests(
        root,
        execute_write=True,
        confirmation=PRESSURE_WAVE_CONFIRMATION,
        idempotency_key="pressure-wave-seed",
        agent_id="codex_cli:test-pressure-wave",
        limit=2,
    )

    assert blocked["status"] == "pressure_wave_spawn_request_seed_blocked"
    assert blocked["write_gate"]["ok"] is False
    assert "write_intent_lease_id_required" in blocked["write_gate"]["blockers"]
    assert blocked["spawn_request_count"] == 0

    seeded = seed_pressure_wave_spawn_requests(
        root,
        execute_write=True,
        confirmation=PRESSURE_WAVE_CONFIRMATION,
        idempotency_key="pressure-wave-seed",
        agent_id="codex_cli:test-pressure-wave",
        write_intent_lease_id="lease-pressure-wave",
        limit=2,
    )
    replay = seed_pressure_wave_spawn_requests(
        root,
        execute_write=True,
        confirmation=PRESSURE_WAVE_CONFIRMATION,
        idempotency_key="pressure-wave-seed",
        agent_id="codex_cli:test-pressure-wave",
        write_intent_lease_id="lease-pressure-wave",
        limit=2,
    )

    assert seeded["status"] == "pressure_wave_spawn_requests_seeded"
    assert seeded["spawn_request_count"] == 2
    assert seeded["actual_spawn_performed"] is False
    assert seeded["codex_queue_run_started"] is False
    assert seeded["worker_start_allowed"] is False
    assert seeded["accepted_state_claimed"] is False
    for rel_path in seeded["spawn_request_paths"]:
        payload = json.loads((root / rel_path).read_text(encoding="utf-8"))
        assert payload["status"] == "requested"
        assert payload["spawn_execution"]["actual_spawn_performed"] is False
        assert payload["spawn_execution"]["queue_mediated_required"] is True
        assert payload["spawn_execution"]["direct_nested_subagent_spawn_allowed"] is False
        assert payload["paths"]["codex_solo_touched"] is False
    assert replay["spawn_request_count"] == 2
    assert replay["idempotent_replay_paths"] == seeded["spawn_request_paths"]
