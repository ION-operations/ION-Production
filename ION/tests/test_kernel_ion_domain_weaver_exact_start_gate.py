from __future__ import annotations

from pathlib import Path

from kernel.ion_domain_weaver_exact_start_gate import (
    EXACT_START_GATE_SCHEMA_ID,
    build_exact_spawn_dispatch_start_gate,
    render_exact_spawn_dispatch_start_gate,
)
from kernel.ion_domain_weaver_spawn_request_dispatcher import (
    SPAWN_DISPATCH_START_PLAN_SCHEMA_ID,
)


def _active_root(tmp_path: Path) -> Path:
    root = tmp_path / "active"
    (root / "ION").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = 'ion-test'\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").write_text("test authority\n", encoding="utf-8")
    return root


def _start_plan(paths: list[str]) -> dict[str, object]:
    rows = [
        {
            "request_path": path,
            "request_id": f"req-{index}",
            "lane_id": lane,
            "domain_id": domain,
            "agent_role_id": role,
            "start_allowed": True,
            "blockers": [],
            "codex_queue_run_started": False,
            "actual_spawn_performed": False,
        }
        for index, (path, lane, domain, role) in enumerate(
            [
                (
                    paths[0],
                    "architecture_lane",
                    "domain.domain_weaver_fanout_control",
                    "role.wave_scheduler",
                ),
                (
                    paths[1],
                    "audit_lane",
                    "domain.domain_weaver_nemesis_production_gate",
                    "role.nemesis",
                ),
            ],
            start=1,
        )
    ]
    return {
        "schema_id": SPAWN_DISPATCH_START_PLAN_SCHEMA_ID,
        "status": "spawn_dispatch_start_plan_built",
        "queueable_spawn_dispatch_request_count": len(paths),
        "planned_start_count": len(paths),
        "blocked_start_count": 0,
        "max_lanes": 2,
        "selected_lane_ids": ["architecture_lane", "audit_lane"],
        "candidate_exact_request_paths": paths,
        "blocked_request_paths": [],
        "start_plan_rows": rows,
        "blocked_rows": [],
        "worker_start_readiness_scope": "requested_path_filter",
        "worker_start_readiness_ok": True,
        "worker_start_readiness_blockers": [],
        "global_worker_start_readiness_ok": False,
        "global_worker_start_readiness_blockers": ["global_queue_hygiene_dirty"],
        "general_queue_processing_allowed": False,
        "codex_queue_run_started": False,
        "actual_spawn_performed": False,
    }


def _idle_runner_state() -> dict[str, object]:
    return {
        "schema_id": "ion.codex_queue_runner_state.v1",
        "updated_at": "2026-06-04T16:00:00+00:00",
        "active_runs": {},
        "active_run": None,
        "active_lane_locks": {
            "active_run_count": 0,
            "active_lane_count": 0,
            "unknown_lane_active_run_count": 0,
            "locks": {
                "architecture_lane": {"locked": False},
                "audit_lane": {"locked": False},
            },
        },
    }


def test_exact_start_gate_accepts_two_exact_paths_without_starting_workers(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    paths = [
        "ION/05_context/current/chatgpt_connector/codex_work_requests/one.json",
        "ION/05_context/current/chatgpt_connector/codex_work_requests/two.json",
    ]

    gate = build_exact_spawn_dispatch_start_gate(
        root,
        request_paths=paths,
        start_plan=_start_plan(paths),
        runner_state=_idle_runner_state(),
        fresh_runtime_status_confirmed=True,
    )

    assert gate["schema_id"] == EXACT_START_GATE_SCHEMA_ID
    assert gate["ready_for_main_test_candidate"] is True
    assert gate["ready_for_immediate_exact_start"] is True
    assert gate["verdict"] == "READY_FOR_IMMEDIATE_EXACT_PATH_MAIN_TEST"
    assert gate["general_queue_processing_allowed"] is False
    assert gate["worker_start_performed_by_gate"] is False
    assert gate["codex_queue_run_started"] is False
    assert gate["actual_spawn_performed"] is False
    assert len(gate["start_commands"]) == 2
    assert "--process-once --start" in gate["start_commands"][0]
    assert "--request-path 'ION/05_context/current/chatgpt_connector/codex_work_requests/one.json'" in gate["start_commands"][0]


def test_exact_start_gate_requires_fresh_runtime_status_before_immediate_start(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    paths = [
        "ION/05_context/current/chatgpt_connector/codex_work_requests/one.json",
        "ION/05_context/current/chatgpt_connector/codex_work_requests/two.json",
    ]

    gate = build_exact_spawn_dispatch_start_gate(
        root,
        request_paths=paths,
        start_plan=_start_plan(paths),
        runner_state=_idle_runner_state(),
    )

    assert gate["ready_for_main_test_candidate"] is True
    assert gate["ready_for_immediate_exact_start"] is False
    assert gate["verdict"] == "READY_FOR_EXACT_PATH_MAIN_TEST_AFTER_FRESH_RUNTIME_PREFLIGHT"
    assert "fresh_runtime_status_not_confirmed" not in gate["candidate_blockers"]
    assert gate["runtime_idle_check"]["ok"] is True


def test_exact_start_gate_blocks_when_start_plan_has_blocked_row(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    paths = [
        "ION/05_context/current/chatgpt_connector/codex_work_requests/one.json",
        "ION/05_context/current/chatgpt_connector/codex_work_requests/two.json",
    ]
    plan = _start_plan(paths)
    plan["planned_start_count"] = 1
    plan["blocked_start_count"] = 1
    plan["candidate_exact_request_paths"] = [paths[0]]
    plan["blocked_request_paths"] = [paths[1]]
    plan["worker_start_readiness_ok"] = False
    plan["worker_start_readiness_blockers"] = ["worker_start_readiness_blocked"]
    plan["blocked_rows"] = [
        {
            "request_path": paths[1],
            "blockers": ["worker_start_readiness_blocked"],
        }
    ]

    gate = build_exact_spawn_dispatch_start_gate(
        root,
        request_paths=paths,
        start_plan=plan,
        runner_state=_idle_runner_state(),
        fresh_runtime_status_confirmed=True,
    )

    assert gate["ready_for_main_test_candidate"] is False
    assert gate["ready_for_immediate_exact_start"] is False
    assert gate["verdict"] == "NOT_READY_BLOCKED_BY_EXACT_START_GATE"
    assert "worker_start_readiness_ok" in gate["candidate_blockers"]
    assert "worker_start_readiness_blocked" in gate["candidate_blockers"]
    assert (
        "ION/05_context/current/chatgpt_connector/codex_work_requests/two.json:worker_start_readiness_blocked"
        in gate["candidate_blockers"]
    )


def test_exact_start_gate_markdown_preserves_non_claims(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    paths = [
        "ION/05_context/current/chatgpt_connector/codex_work_requests/one.json",
        "ION/05_context/current/chatgpt_connector/codex_work_requests/two.json",
    ]
    gate = build_exact_spawn_dispatch_start_gate(
        root,
        request_paths=paths,
        start_plan=_start_plan(paths),
        runner_state=_idle_runner_state(),
    )

    rendered = render_exact_spawn_dispatch_start_gate(gate)

    assert "Domain Weaver Exact Spawn-Dispatch Start Gate" in rendered
    assert "this_gate_does_not_start_workers" in rendered
    assert "general_queue_processing_requested" in rendered
