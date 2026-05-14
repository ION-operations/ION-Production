import json
from pathlib import Path

from kernel.ion_kernel_fanout_carrier_dryrun import (
    build_kernel_fanout_carrier_dryrun_status,
    run_default_carrier_dryrun,
    run_kernel_fanout_carrier_dryrun,
)


ACCEPTED_SIGNIN_RETURN = {
    "path": "ION/05_context/current/chatgpt_connector/task_returns/2026-05-13T231604Z0000_task_return.json",
    "sha256": "711b91fdac2c17aeaf5d3d94507e03f1c29770d24f1b2ff1a69693d7de783a1f",
}


def _scenario(result, name):
    for row in result["scenarios"]:
        if row["scenario"] == name:
            return row
    raise AssertionError(f"missing scenario {name}")


def test_carrier_dryrun_enforces_caps_and_fail_closed_without_queue_mutation(tmp_path):
    result = run_kernel_fanout_carrier_dryrun(
        output_root=tmp_path,
        accepted_signin_return=ACCEPTED_SIGNIN_RETURN,
    )

    assert result["schema_id"] == "ion.kernel_fanout_carrier_dryrun_result.v1"
    assert result["verdict"] == "CARRIER_DRYRUN_READY"
    assert result["queue_integrity"]["queue_mutation_detected"] is False
    assert result["blocked_findings"] == []
    assert result["child_caps"]["max_executable_children_per_scenario"] == 2
    assert result["child_caps"]["max_child_timeout_seconds"] == 10

    success = _scenario(result, "success")
    timeout_case = _scenario(result, "forced_timeout")
    conflict = _scenario(result, "forced_conflict")

    assert success["child_timeout_seconds"] <= 10
    assert timeout_case["child_timeout_seconds"] <= 10
    assert conflict["child_timeout_seconds"] <= 10

    success_summary = success["compact_summary"]
    assert success_summary["settlement_verdict"] == "SMOKE_READY"
    assert success_summary["child_count"] == 2
    assert success_summary["max_parallel_observed"] == 2
    assert success_summary["overlap_seconds"] > 0
    assert success_summary["blocked_children"] == []

    timeout_summary = timeout_case["compact_summary"]
    assert timeout_summary["settlement_verdict"] == "SMOKE_BLOCKED"
    assert timeout_summary["child_count"] == 2
    assert timeout_summary["timeout_evidence"]
    timeout_codes = {row.get("code") for row in timeout_summary["timeout_evidence"]}
    assert "child_timeout" in timeout_codes
    assert timeout_summary["blocked_children"]

    conflict_summary = conflict["compact_summary"]
    assert conflict_summary["settlement_verdict"] == "SMOKE_READY"
    assert conflict_summary["child_count"] == 2
    assert conflict_summary["conflict_deferral_events"] > 0
    assert conflict_summary["max_parallel_observed"] <= 1
    assert conflict_summary["blocked_children"] == []

    for row in result["queue_integrity"]["rows"]:
        assert row["unchanged"] is True

    for scenario_name in ("success", "forced_timeout", "forced_conflict"):
        scenario = _scenario(result, scenario_name)
        result_path = Path(scenario["result_path"])
        parent_path = Path(scenario["parent_receipt_path"])
        assert result_path.exists()
        assert parent_path.exists()
        payload = json.loads(result_path.read_text(encoding="utf-8"))
        assert payload["true_parallel_harness"] is True
        assert payload["read_only_noop"] is True
        for child in payload["children"]:
            child_dir = Path(scenario["child_receipt_root"]) / child["child_id"]
            assert (child_dir / "lease.json").exists()
            assert (child_dir / "heartbeat.json").exists()
            assert (child_dir / "worker_context_awareness_receipt.json").exists()


def test_default_carrier_dryrun_writes_compact_receipt_and_result_file(tmp_path):
    receipt = run_default_carrier_dryrun(
        output_root=tmp_path,
        accepted_signin_return=ACCEPTED_SIGNIN_RETURN,
    )

    assert receipt["schema_id"] == "ion.kernel_fanout_carrier_dryrun_receipt.v1"
    assert receipt["result"] == "CARRIER_DRYRUN_READY"
    assert receipt["queue_mutation_detected"] is False
    assert len(receipt["scenario_summaries"]) == 3

    result_path = tmp_path / "fanout_carrier_dryrun_result_20260514.json"
    assert result_path.exists()
    result = json.loads(result_path.read_text(encoding="utf-8"))
    assert result["schema_id"] == "ion.kernel_fanout_carrier_dryrun_result.v1"
    assert result["queue_integrity"]["queue_mutation_detected"] is False


def test_dryrun_status_payload_is_compact_and_reports_timeout_conflict_success(tmp_path):
    receipt = run_default_carrier_dryrun(
        output_root=tmp_path,
        accepted_signin_return=ACCEPTED_SIGNIN_RETURN,
    )
    assert receipt["result"] == "CARRIER_DRYRUN_READY"

    status = build_kernel_fanout_carrier_dryrun_status(
        Path.cwd(),
        result_path=tmp_path / "fanout_carrier_dryrun_result_20260514.json",
        accepted_return_path="ION/05_context/current/chatgpt_connector/task_returns/2026-05-14T021628Z0000_task_return.json",
    )

    assert status["schema_id"] == "ion.kernel_fanout_carrier_dryrun_status.v1"
    assert status["mutates_active_state"] is False
    assert status["production_authority"] is False
    assert status["live_execution_authority"] is False
    assert status["latest_dryrun_result_path"].endswith("fanout_carrier_dryrun_result_20260514.json")
    assert isinstance(status["latest_dryrun_result_sha256"], str) and status["latest_dryrun_result_sha256"]
    verdicts = {row["scenario"]: row["settlement_verdict"] for row in status["scenario_verdicts"]}
    assert verdicts["success"] == "SMOKE_READY"
    assert verdicts["forced_timeout"] == "SMOKE_BLOCKED"
    assert verdicts["forced_conflict"] == "SMOKE_READY"
    assert status["queue_mutation_detected"] is False
    timeout = status["timeout_fail_closed_summary"]
    assert timeout["scenario"] == "forced_timeout"
    assert timeout["fail_closed"] is True
    assert "child_timeout" in timeout["timeout_codes"]
    conflict = status["conflict_lock_summary"]
    assert conflict["scenario"] == "forced_conflict"
    assert conflict["conflict_deferral_events"] > 0
    artifacts = status["receipt_artifacts"]
    assert any(row["kind"] == "latest_dryrun_result" and row["exists"] is True for row in artifacts)
    assert any(row["kind"] == "scenario_parent_receipt" and row["exists"] is True for row in artifacts)
