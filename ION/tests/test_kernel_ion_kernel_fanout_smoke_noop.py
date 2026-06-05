import json

from kernel.ion_kernel_fanout_smoke_noop import (
    run_default_noop_parallel_smoke,
    simulate_kernel_fanout_noop_smoke,
)


def _child(result, child_id):
    for row in result["children"]:
        if row["child_id"] == child_id:
            return row
    raise AssertionError(f"missing child {child_id}")


def test_noop_smoke_exercises_parallel_conflict_dependency_and_receipts():
    graph = {
        "parent_packet_id": "PCKT-TEST-NOOP-SMOKE-001",
        "request_id": "codex_req_test_noop_smoke_001",
        "max_parallel": 2,
        "children": [
            {
                "child_id": "child_a",
                "objective": "No-op child A.",
                "write_paths": ["ION/05_context/current/kernel_fanout_scheduler/smoke_runs/a.txt"],
            },
            {
                "child_id": "child_b",
                "objective": "No-op child B.",
                "write_paths": ["ION/05_context/current/kernel_fanout_scheduler/smoke_runs/b.txt"],
            },
            {
                "child_id": "child_a_conflict",
                "objective": "No-op child conflicts with child_a.",
                "write_paths": ["ION/05_context/current/kernel_fanout_scheduler/smoke_runs/a.txt"],
            },
            {
                "child_id": "child_after_b",
                "objective": "No-op child after B.",
                "depends_on": ["child_b"],
                "write_paths": ["ION/05_context/current/kernel_fanout_scheduler/smoke_runs/after_b.txt"],
            },
        ],
    }
    durations = {
        "child_a": 3,
        "child_b": 2,
        "child_a_conflict": 1,
        "child_after_b": 1,
    }
    accepted_signin_return = {
        "path": "ION/05_context/current/chatgpt_connector/task_returns/2026-05-13T231604Z0000_task_return.json",
        "sha256": "65e8e2a0444815fd31e194661fdfdee7ea96a38247613e3cc074cabbb865d34c",
    }

    result = simulate_kernel_fanout_noop_smoke(
        graph,
        child_durations=durations,
        accepted_signin_return=accepted_signin_return,
    )

    child_a = _child(result, "child_a")
    child_b = _child(result, "child_b")
    child_conflict_a = _child(result, "child_a_conflict")
    child_after_b = _child(result, "child_after_b")

    assert result["plan_verdict"] == "ION_KERNEL_FANOUT_PLAN_READY"
    assert result["parallel_observation"]["max_parallel_observed"] == 2
    assert child_a["started_tick"] == 1
    assert child_b["started_tick"] == 1
    assert child_conflict_a["started_tick"] > child_a["completed_tick"]
    assert child_after_b["started_tick"] > child_b["completed_tick"]

    assert child_conflict_a["lock_blocked_ticks"]
    blocked_event = child_conflict_a["lock_blocked_ticks"][0]
    assert "child_a" in blocked_event["blocked_by"]

    for row in (child_a, child_b, child_conflict_a, child_after_b):
        assert row["state"] == "completed"
        assert row["lease_receipt"]["lease_id"].startswith("lease_")
        assert row["heartbeat_receipt"]["beats"]
        receipt = row["machine_signin_receipt"]
        assert receipt["schema_id"] == "ion.worker_context_awareness_receipt.v1"
        assert receipt["status"] == "WORKER_CONTEXT_ACKNOWLEDGED"

    settlement = result["reducer_settlement_summary"]
    assert settlement["verdict"] == "SMOKE_READY"
    assert settlement["required_receipt_chain_complete"] is True
    assert settlement["blocked_children"] == []


def test_default_noop_smoke_writes_compact_run_artifact(tmp_path):
    accepted_signin_return = {
        "path": "ION/05_context/current/chatgpt_connector/task_returns/2026-05-13T231604Z0000_task_return.json",
        "sha256": "65e8e2a0444815fd31e194661fdfdee7ea96a38247613e3cc074cabbb865d34c",
    }
    receipt = run_default_noop_parallel_smoke(
        output_root=tmp_path,
        accepted_signin_return=accepted_signin_return,
    )

    assert receipt["result"] == "NOOP_SMOKE_COMPLETED"
    path = tmp_path / "fanout_noop_smoke_result_20260514.json"
    assert path.exists()

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_id"] == "ion.kernel_fanout_noop_smoke_result.v1"
    assert payload["read_only_noop"] is True
    assert payload["production_authority"] is False
    assert payload["live_execution_authority"] is False
    assert payload["reducer_settlement_summary"]["verdict"] == "SMOKE_READY"
