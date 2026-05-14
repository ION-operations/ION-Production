import json

import pytest

from kernel.ion_kernel_fanout_true_parallel_smoke import (
    run_default_true_parallel_smoke,
    simulate_kernel_fanout_true_parallel_smoke,
)


ACCEPTED_SIGNIN_RETURN = {
    "path": "ION/05_context/current/chatgpt_connector/task_returns/2026-05-13T231604Z0000_task_return.json",
    "sha256": "711b91fdac2c17aeaf5d3d94507e03f1c29770d24f1b2ff1a69693d7de783a1f",
}


def _child(result, child_id):
    for row in result["children"]:
        if row["child_id"] == child_id:
            return row
    raise AssertionError(f"missing child {child_id}")


def test_true_parallel_smoke_runs_two_children_and_defers_conflict(tmp_path):
    artifact_root = "ION/05_context/current/kernel_fanout_scheduler/true_parallel_smoke_runs/test_true_parallel"
    graph = {
        "parent_packet_id": "PCKT-TEST-TRUE-PARALLEL-SMOKE-001",
        "request_id": "codex_req_test_true_parallel_001",
        "max_parallel": 2,
        "artifact_root": artifact_root,
        "children": [
            {
                "child_id": "child_alpha",
                "objective": "No-op alpha.",
                "write_paths": [f"{artifact_root}/outputs/alpha.txt"],
                "heartbeat_seconds": 1,
            },
            {
                "child_id": "child_beta",
                "objective": "No-op beta.",
                "write_paths": [f"{artifact_root}/outputs/beta.txt"],
                "heartbeat_seconds": 1,
            },
            {
                "child_id": "child_alpha_conflict",
                "objective": "No-op conflict child.",
                "depends_on": ["child_beta"],
                "write_paths": [f"{artifact_root}/outputs/alpha.txt"],
                "heartbeat_seconds": 1,
            },
        ],
    }

    result = simulate_kernel_fanout_true_parallel_smoke(
        graph,
        child_durations_seconds={
            "child_alpha": 1.2,
            "child_beta": 0.8,
            "child_alpha_conflict": 0.5,
        },
        child_timeout_seconds=20,
        parent_timeout_seconds=120,
        heartbeat_interval_seconds=0.1,
        accepted_signin_return=ACCEPTED_SIGNIN_RETURN,
        receipt_root_override=tmp_path / "child_receipts",
    )

    alpha = _child(result, "child_alpha")
    beta = _child(result, "child_beta")
    conflict = _child(result, "child_alpha_conflict")

    assert result["plan_verdict"] == "ION_KERNEL_FANOUT_PLAN_READY"
    assert result["parallel_observation"]["max_parallel_observed"] == 2
    assert result["parallel_observation"]["overlap_seconds"] > 0

    assert alpha["state"] == "completed"
    assert beta["state"] == "completed"
    assert conflict["state"] == "completed"

    assert alpha["machine_signin_receipt"]["status"] == "WORKER_CONTEXT_ACKNOWLEDGED"
    assert beta["machine_signin_receipt"]["status"] == "WORKER_CONTEXT_ACKNOWLEDGED"
    assert conflict["machine_signin_receipt"]["status"] == "WORKER_CONTEXT_ACKNOWLEDGED"

    assert conflict["lock_blocked_events"]
    assert conflict["started_monotonic"] > beta["completed_monotonic"]
    assert conflict["started_monotonic"] > alpha["completed_monotonic"]

    for row in (alpha, beta, conflict):
        assert row["lease_receipt_path"]
        assert row["heartbeat_receipt_path"]
        assert row["machine_signin_receipt_path"]
        assert (tmp_path / "child_receipts" / row["child_id"] / "lease.json").exists()
        assert (tmp_path / "child_receipts" / row["child_id"] / "heartbeat.json").exists()
        assert (
            tmp_path
            / "child_receipts"
            / row["child_id"]
            / "worker_context_awareness_receipt.json"
        ).exists()

    settlement = result["reducer_settlement_summary"]
    assert settlement["verdict"] == "SMOKE_READY"
    assert settlement["blocked_children"] == []
    assert settlement["conflict_deferred_children"] == ["child_alpha_conflict"]


def test_true_parallel_smoke_enforces_timeout_caps():
    graph = {
        "parent_packet_id": "PCKT-TEST-TRUE-PARALLEL-SMOKE-CAPS",
        "request_id": "codex_req_test_true_parallel_caps",
        "max_parallel": 1,
        "children": [{"child_id": "child_a", "objective": "No-op child."}],
    }

    with pytest.raises(ValueError):
        simulate_kernel_fanout_true_parallel_smoke(
            graph,
            child_timeout_seconds=61,
            parent_timeout_seconds=120,
        )

    with pytest.raises(ValueError):
        simulate_kernel_fanout_true_parallel_smoke(
            graph,
            child_timeout_seconds=20,
            parent_timeout_seconds=181,
        )


def test_default_true_parallel_smoke_writes_compact_artifact(tmp_path):
    receipt = run_default_true_parallel_smoke(
        output_root=tmp_path,
        accepted_signin_return=ACCEPTED_SIGNIN_RETURN,
        child_timeout_seconds=20,
        parent_timeout_seconds=120,
    )

    assert receipt["result"] == "TRUE_PARALLEL_SMOKE_COMPLETED"

    output_path = tmp_path / "fanout_true_parallel_smoke_result_20260514.json"
    assert output_path.exists()

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["schema_id"] == "ion.kernel_fanout_true_parallel_smoke_result.v1"
    assert payload["true_parallel_harness"] is True
    assert payload["read_only_noop"] is True
    assert payload["production_authority"] is False
    assert payload["live_execution_authority"] is False
    assert payload["parallel_observation"]["max_parallel_observed"] == 2
    assert payload["reducer_settlement_summary"]["verdict"] == "SMOKE_READY"
