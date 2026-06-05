from __future__ import annotations

import json
from pathlib import Path

from kernel.ion_domain_weaver_spawn_request_dispatcher import (
    DISPATCH_CANDIDATE_SCHEMA_ID,
    DISPATCH_ENQUEUE_RECEIPT_SCHEMA_ID,
    DISPATCH_REJECTION_SCHEMA_ID,
    QUEUE_PACKET_CANDIDATE_SCHEMA_ID,
    SPAWN_DISPATCH_START_PLAN_SCHEMA_ID,
    build_spawn_dispatch_start_plan,
    build_spawn_dispatch_legacy_receipt_quarantine,
    dispatch_requested_spawn_requests,
    enqueue_requested_spawn_requests,
    find_requested_spawn_requests,
    render_spawn_dispatch_legacy_receipt_quarantine,
    validate_spawn_request,
)
from kernel.ion_domain_weaver_worker_context_lanes import (
    SPAWN_REQUEST_SCHEMA_ID,
    write_fanin_summary,
    write_spawn_request,
)


def _active_root(tmp_path: Path) -> Path:
    root = tmp_path / "active"
    (root / "ION").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = 'ion-test'\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").write_text("test authority\n", encoding="utf-8")
    return root


def _spawn_request(root: Path, *, row_id: str = "child") -> dict:
    return write_spawn_request(
        root,
        "Babbage",
        requested_domain="domain.context.cartographer",
        requested_packet="PCKT-DOMAIN-WEAVER-CONTEXT-CARTOGRAPHY-CHILD",
        requested_callsign="Lovelace",
        requested_true_name="Ada Lovelace",
        requested_role_id="role.context_cartographer",
        requested_role_tier="specialist",
        work_class="domain_weaver_spawn_dispatch",
        lane_id="context_lane",
        domain_context_package="ION/05_context/current/domain_weaver/.ion/ACTIVE_CONTEXT_PACKAGE.md",
        required_context_reads=[
            {
                "kind": "file",
                "path": "ION/05_context/current/domain_weaver/AGENTS.md",
                "required": True,
            }
        ],
        planned_writes=[
            "ION/05_context/current/domain_weaver/workers/lovelace/context/candidates/result.candidate.json"
        ],
        allowed_scope=["read active-root source", "write worker-local candidate artifact"],
        forbidden_actions=["mutate active source", "touch Codex Solo"],
        evidence_requirements=["active-root proof", "worker-lane receipt"],
        row_id=row_id,
    )


def test_find_requested_spawn_requests_filters_consumed_rows(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    requested = _spawn_request(root, row_id="requested")
    consumed = _spawn_request(root, row_id="consumed")
    consumed_path = root / consumed["path"]
    consumed_payload = json.loads(consumed_path.read_text(encoding="utf-8"))
    consumed_payload["status"] = "consumed_by_dispatcher"
    consumed_path.write_text(json.dumps(consumed_payload), encoding="utf-8")

    found = find_requested_spawn_requests(root)

    assert [entry["path"] for entry in found] == [requested["path"]]


def test_dispatcher_emits_candidate_and_marks_source_consumed(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    request = _spawn_request(root, row_id="dispatch-me")

    result = dispatch_requested_spawn_requests(
        root,
        dispatcher_id="lead-codex",
        run_id="run-a",
    )

    assert result["requested_count"] == 1
    assert result["candidate_count"] == 1
    assert result["queue_packet_candidate_count"] == 1
    assert result["rejection_count"] == 0
    assert result["blocked_count"] == 0
    assert result["actual_spawn_performed"] is False
    assert result["direct_nested_spawn"] is False
    assert result["raw_external_codex_exec"] is False
    assert result["live_queue_state_mutated"] is False
    assert result["codex_work_request_written"] is False
    assert result["codex_queue_run_started"] is False

    candidate = result["dispatch_candidates"][0]
    assert candidate["schema_id"] == DISPATCH_CANDIDATE_SCHEMA_ID
    assert candidate["status"] == "dispatch_candidate"
    assert candidate["source_request_path"] == request["path"]
    assert candidate["source_request_sha256"]
    assert candidate["parent_worker_id"] == "babbage"
    assert candidate["requested_domain"] == "domain.context.cartographer"
    assert candidate["lead_fanin_required"] is True
    assert candidate["queue_mediated_required"] is True
    assert candidate["actual_spawn_performed"] is False
    assert candidate["direct_nested_spawn"] is False
    assert candidate["raw_external_codex_exec"] is False
    assert candidate["authority"]["carrier_intake_only"] is True
    assert candidate["authority"]["accepted_state"] is False
    assert candidate["bounded_dispatch_packet"]["worker_return_is_carrier_intake_only"] is True
    assert candidate["bounded_dispatch_packet"]["queue_packet_candidate_ref"]
    assert candidate["queue_packet_candidate_ref"]
    assert candidate["live_queue_state_mutated"] is False
    assert candidate["codex_work_request_written"] is False
    assert candidate["codex_queue_run_started"] is False

    written_candidate = json.loads((root / candidate["path"]).read_text(encoding="utf-8"))
    assert written_candidate["status"] == "dispatch_candidate"

    queue_packet_candidate = result["queue_packet_candidates"][0]
    assert queue_packet_candidate["schema_id"] == QUEUE_PACKET_CANDIDATE_SCHEMA_ID
    assert queue_packet_candidate["status"] == "queue_packet_candidate"
    assert queue_packet_candidate["source_request_path"] == request["path"]
    assert queue_packet_candidate["source_dispatch_candidate_path"] == candidate["path"]
    assert queue_packet_candidate["candidate_artifact_only"] is True
    assert queue_packet_candidate["actual_spawn_performed"] is False
    assert queue_packet_candidate["direct_nested_spawn"] is False
    assert queue_packet_candidate["raw_external_codex_exec"] is False
    assert queue_packet_candidate["live_queue_state_mutated"] is False
    assert queue_packet_candidate["codex_work_request_written"] is False
    assert queue_packet_candidate["codex_queue_run_started"] is False
    assert queue_packet_candidate["authority"]["accepted_state"] is False
    assert queue_packet_candidate["authority"]["production_authority"] is False
    assert (
        queue_packet_candidate["bounded_codex_work_packet_request"]["status"]
        == "candidate_only_not_queued"
    )
    assert (
        queue_packet_candidate["bounded_codex_work_packet_request"]["packet_id"]
        == "PCKT-DOMAIN-WEAVER-CONTEXT-CARTOGRAPHY-CHILD"
    )
    assert (
        queue_packet_candidate["bounded_codex_work_packet_request"][
            "live_queue_state_mutated"
        ]
        is False
    )
    assert (
        queue_packet_candidate["bounded_codex_work_packet_request"][
            "codex_queue_run_started"
        ]
        is False
    )
    assert candidate["queue_packet_candidate_ref"] == queue_packet_candidate["path"]
    written_queue_packet_candidate = json.loads(
        (root / queue_packet_candidate["path"]).read_text(encoding="utf-8")
    )
    assert written_queue_packet_candidate["status"] == "queue_packet_candidate"

    source_after = json.loads((root / request["path"]).read_text(encoding="utf-8"))
    assert source_after["status"] == "consumed_by_dispatcher"
    assert source_after["dispatcher_consumption"]["source_deleted"] is False
    assert source_after["dispatcher_consumption"]["dispatch_ref"] == candidate["path"]
    assert (root / request["path"]).is_file()


def test_dispatcher_enqueues_valid_spawn_request_as_codex_work_request_without_starting_worker(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    request = _spawn_request(root, row_id="enqueue-me")

    result = enqueue_requested_spawn_requests(
        root,
        dispatcher_id="lead-codex",
        run_id="enqueue-run",
        mark_consumed=False,
    )
    replay = enqueue_requested_spawn_requests(
        root,
        dispatcher_id="lead-codex",
        run_id="enqueue-run",
        mark_consumed=False,
    )

    assert result["schema_id"] == "ion.domain_weaver.spawn_dispatch_enqueue_run.v0_1"
    assert result["requested_count"] == 1
    assert result["candidate_count"] == 1
    assert result["queue_packet_candidate_count"] == 1
    assert result["enqueue_receipt_count"] == 1
    assert result["rejection_count"] == 0
    assert result["actual_spawn_performed"] is False
    assert result["codex_queue_run_started"] is False
    assert result["worker_start_allowed"] is False

    receipt = result["enqueue_receipts"][0]
    assert receipt["schema_id"] == DISPATCH_ENQUEUE_RECEIPT_SCHEMA_ID
    assert receipt["status"] == "spawn_dispatch_enqueued"
    assert receipt["source_request_path"] == request["path"]
    assert receipt["connector_ok"] is True
    assert receipt["connector_packet_path"]
    assert receipt["worker_return_is_carrier_intake_only"] is True
    assert receipt["actual_spawn_performed"] is False
    assert receipt["codex_queue_run_started"] is False
    assert receipt["accepted_state_claimed"] is False

    packet = json.loads((root / receipt["connector_packet_path"]).read_text(encoding="utf-8"))
    assert packet["status"] == "QUEUED_FOR_CODEX_CARRIER"
    assert packet["request_kind"] == "domain_weaver_spawn_dispatch"
    assert packet["work_class"] == "domain_weaver_spawn_dispatch"
    assert packet["domain_id"] == "domain.context.cartographer"
    assert packet["agent_role_id"] == "role.context_cartographer"
    assert packet["role_tier"] == "specialist"
    assert packet["callsign"] == "Lovelace"
    assert packet["true_name"] == "Ada Lovelace"
    assert packet["domain_context_package"] == (
        "ION/05_context/current/domain_weaver/.ion/ACTIVE_CONTEXT_PACKAGE.md"
    )
    assert packet["domain_weaver_spawn_dispatch"]["source_spawn_request_path"] == request["path"]
    assert packet["domain_weaver_spawn_dispatch"]["worker_return_is_carrier_intake_only"] is True
    assert packet["domain_weaver_spawn_dispatch"]["actual_spawn_performed"] is False
    assert packet["domain_weaver_spawn_dispatch"]["codex_queue_run_started"] is False
    required_paths = {row["path"] for row in packet["required_context_reads"]}
    assert request["path"] in required_paths
    assert "ION/05_context/current/domain_weaver/AGENTS.md" in required_paths

    replay_receipt = replay["enqueue_receipts"][0]
    assert replay_receipt["connector_idempotent_replay"] is True
    assert replay_receipt["connector_duplicate_prevented"] is True
    assert replay_receipt["connector_packet_path"] == receipt["connector_packet_path"]
    request_after = json.loads((root / request["path"]).read_text(encoding="utf-8"))
    assert request_after["status"] == "requested"


def test_dispatcher_does_not_count_blocked_connector_receipt_as_enqueued(
    tmp_path: Path,
    monkeypatch,
) -> None:
    import kernel.ion_domain_weaver_spawn_request_dispatcher as dispatcher

    root = _active_root(tmp_path)
    request = _spawn_request(root, row_id="blocked-connector")

    def fake_connector(*_args, **_kwargs):
        return {
            "ok": False,
            "finding": "connector_policy_blocked_for_test",
            "data": {},
        }

    monkeypatch.setattr(dispatcher, "call_chatgpt_connector_tool", fake_connector)

    result = enqueue_requested_spawn_requests(
        root,
        dispatcher_id="lead-codex",
        run_id="blocked-connector-run",
        mark_consumed=True,
    )

    assert result["requested_count"] == 1
    assert result["candidate_count"] == 1
    assert result["queue_packet_candidate_count"] == 1
    assert result["enqueue_receipt_count"] == 0
    assert result["blocked_enqueue_receipt_count"] == 1
    assert result["proof_gate"]["enqueued"] == 0
    assert result["proof_gate"]["enqueue_blocked"] == 1
    assert result["proof_gate"]["enqueue_receipt_paths"] == []
    assert result["proof_gate"]["blocked_enqueue_receipt_paths"] == [
        result["blocked_enqueue_receipts"][0]["path"]
    ]
    receipt = result["blocked_enqueue_receipts"][0]
    assert receipt["schema_id"] == DISPATCH_ENQUEUE_RECEIPT_SCHEMA_ID
    assert receipt["status"] == "spawn_dispatch_enqueue_blocked"
    assert receipt["connector_ok"] is False
    assert receipt["connector_finding"] == "connector_policy_blocked_for_test"
    assert receipt["codex_work_request_written"] is False
    assert receipt["connector_packet_path"] is None
    source_after = json.loads((root / request["path"]).read_text(encoding="utf-8"))
    assert source_after["status"] == "enqueue_blocked_by_dispatcher"
    assert source_after["dispatcher_consumption"]["dispatch_ref"] == receipt["path"]
    assert source_after["dispatcher_consumption"]["validation_ok"] is False
    assert "spawn_dispatch_enqueue_blocked" in source_after["dispatcher_consumption"]["validation_reasons"]
    assert "codex_work_request_not_written" in source_after["dispatcher_consumption"]["validation_reasons"]
    assert not list(
        (root / "ION/05_context/current/chatgpt_connector/codex_work_requests").glob(
            "*.json"
        )
    )


def test_legacy_receipt_quarantine_excludes_blocked_receipt_listed_as_enqueued(
    tmp_path: Path,
    monkeypatch,
) -> None:
    import kernel.ion_domain_weaver_spawn_request_dispatcher as dispatcher

    root = _active_root(tmp_path)
    _spawn_request(root, row_id="legacy-blocked")

    def fake_connector(*_args, **_kwargs):
        return {
            "ok": False,
            "finding": "structured_route_metadata_required_for_test",
            "data": {},
        }

    monkeypatch.setattr(dispatcher, "call_chatgpt_connector_tool", fake_connector)

    enqueue = enqueue_requested_spawn_requests(
        root,
        dispatcher_id="lead-codex",
        run_id="legacy-blocked-run",
        mark_consumed=True,
    )
    blocked = enqueue["blocked_enqueue_receipts"][0]
    legacy_path = (
        root
        / "ION/05_context/current/domain_weaver/acceleration/DW_SPW_002_OVERFLOW_QUEUE_MEDIATED_SPAWN.latest.json"
    )
    legacy_path.parent.mkdir(parents=True, exist_ok=True)
    legacy_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.domain_weaver.legacy_test_artifact",
                "enqueue_result": {
                    "schema_id": "ion.domain_weaver.spawn_dispatch_enqueue_run.v0_1",
                    "status": "dispatch_enqueue_run_completed",
                    "enqueue_receipt_count": 1,
                    "enqueue_receipts": [blocked],
                    "proof_gate": {
                        "enqueued": 1,
                        "enqueue_receipt_paths": [blocked["path"]],
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    quarantine = build_spawn_dispatch_legacy_receipt_quarantine(root)

    assert quarantine["schema_id"] == "ion.domain_weaver.spawn_dispatch_legacy_receipt_quarantine.v0_1_candidate"
    assert quarantine["legacy_false_enqueue_detected"] is True
    assert quarantine["embedded_receipt_count"] == 1
    assert quarantine["claimed_enqueue_receipt_count"] == 1
    assert quarantine["verified_enqueue_receipt_count"] == 0
    assert quarantine["blocked_receipt_count"] == 1
    assert quarantine["quarantined_false_enqueue_count"] == 1
    assert quarantine["verified_enqueue_receipt_paths"] == []
    assert quarantine["quarantined_receipt_paths"] == [blocked["path"]]
    row = quarantine["quarantine_rows"][0]
    assert row["claimed_as_enqueued_by_container"] is True
    assert row["verified_enqueue"] is False
    assert row["count_as_enqueued"] is False
    assert row["ui_count_as_enqueued"] is False
    assert row["projection_count_as_enqueued"] is False
    assert "connector_not_ok:structured_route_metadata_required_for_test" in row["enqueue_blockers"]
    assert "codex_work_request_not_written" in row["enqueue_blockers"]
    assert "connector_packet_path_missing" in row["enqueue_blockers"]
    assert quarantine["proof_gate"]["dispatch_enqueue_receipt_with_connector_ok_false_counts_as_enqueued"] is False
    report = render_spawn_dispatch_legacy_receipt_quarantine(quarantine)
    assert "quarantined false-enqueue receipts: `1`" in report
    assert blocked["path"] in report


def test_legacy_receipt_quarantine_requires_full_success_predicate_not_status_only(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    receipt_path = (
        root
        / "ION/05_context/current/domain_weaver/spawn_dispatch/poison.dispatch_enqueue_receipt.json"
    )
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    poisoned_receipt = {
        "schema_id": DISPATCH_ENQUEUE_RECEIPT_SCHEMA_ID,
        "status": "spawn_dispatch_enqueued",
        "connector_ok": False,
        "codex_work_request_written": False,
        "connector_packet_path": "",
        "path": "ION/05_context/current/domain_weaver/spawn_dispatch/poison.dispatch_enqueue_receipt.json",
    }
    receipt_path.write_text(json.dumps(poisoned_receipt), encoding="utf-8")
    legacy_path = root / "ION/05_context/current/domain_weaver/acceleration/poison.json"
    legacy_path.parent.mkdir(parents=True, exist_ok=True)
    legacy_path.write_text(
        json.dumps({"enqueue_result": {"enqueue_receipts": [poisoned_receipt]}}),
        encoding="utf-8",
    )

    quarantine = build_spawn_dispatch_legacy_receipt_quarantine(
        root,
        artifact_paths=["ION/05_context/current/domain_weaver/acceleration/poison.json"],
    )

    assert quarantine["claimed_enqueue_receipt_count"] == 1
    assert quarantine["verified_enqueue_receipt_count"] == 0
    assert quarantine["quarantined_false_enqueue_count"] == 1
    row = quarantine["quarantine_rows"][0]
    assert row["status"] == "spawn_dispatch_enqueued"
    assert row["connector_ok"] is False
    assert row["count_as_enqueued"] is False
    assert "connector_not_ok" in row["enqueue_blockers"]
    assert "codex_work_request_not_written" in row["enqueue_blockers"]
    assert "connector_packet_path_missing" in row["enqueue_blockers"]


def test_dispatcher_rejects_spawn_request_missing_executable_lane_before_enqueue(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    request = _spawn_request(root, row_id="missing-lane")
    request_path = root / request["path"]
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    payload.pop("lane_id", None)
    request_path.write_text(json.dumps(payload), encoding="utf-8")

    result = enqueue_requested_spawn_requests(
        root,
        dispatcher_id="lead-codex",
        run_id="missing-lane-run",
    )

    assert result["enqueue_receipt_count"] == 0
    assert result["rejection_count"] == 1
    assert result["codex_queue_run_started"] is False
    assert result["worker_start_allowed"] is False
    reasons = result["rejections"][0]["reasons"]
    assert "lane_id_required_for_spawn_dispatch" in reasons
    assert not list(
        (root / "ION/05_context/current/chatgpt_connector/codex_work_requests").glob(
            "*.json"
        )
    )


def test_dispatcher_rejects_non_executable_lane_before_enqueue(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    request = _spawn_request(root, row_id="non-executable-lane")
    request_path = root / request["path"]
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    payload["lane_id"] = "needs_triage"
    request_path.write_text(json.dumps(payload), encoding="utf-8")

    result = enqueue_requested_spawn_requests(
        root,
        dispatcher_id="lead-codex",
        run_id="non-executable-lane-run",
    )

    assert result["enqueue_receipt_count"] == 0
    assert result["rejection_count"] == 1
    reasons = result["rejections"][0]["reasons"]
    assert "lane_id_not_executable:needs_triage" in reasons
    assert result["actual_spawn_performed"] is False
    assert result["codex_queue_run_started"] is False


def test_spawn_dispatch_start_plan_is_read_only_and_blocks_until_readiness(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    request = _spawn_request(root, row_id="start-plan")
    enqueue = enqueue_requested_spawn_requests(
        root,
        dispatcher_id="lead-codex",
        run_id="start-plan-run",
        mark_consumed=False,
    )
    receipt = enqueue["enqueue_receipts"][0]

    plan = build_spawn_dispatch_start_plan(
        root,
        request_paths=[receipt["connector_packet_path"]],
        max_lanes=3,
    )

    assert plan["schema_id"] == SPAWN_DISPATCH_START_PLAN_SCHEMA_ID
    assert plan["queueable_spawn_dispatch_request_count"] == 1
    assert plan["planned_start_count"] == 0
    assert plan["blocked_start_count"] == 1
    assert plan["candidate_exact_request_paths"] == []
    assert plan["blocked_request_paths"] == [receipt["connector_packet_path"]]
    assert plan["actual_spawn_performed"] is False
    assert plan["codex_queue_run_started"] is False
    assert plan["general_queue_processing_allowed"] is False
    blocked = plan["blocked_rows"][0]
    assert blocked["request_path"] == receipt["connector_packet_path"]
    assert blocked["lane_id"] == "context_lane"
    assert blocked["exact_request_path_required"] is True
    assert blocked["start_allowed"] is False
    assert "worker_start_readiness_blocked" in blocked["blockers"]
    assert blocked["codex_queue_run_started"] is False
    assert blocked["actual_spawn_performed"] is False
    source_after = json.loads((root / request["path"]).read_text(encoding="utf-8"))
    assert source_after["status"] == "requested"


def test_dispatcher_rejects_authority_claims_and_marks_source(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    request = _spawn_request(root, row_id="bad-authority")
    request_path = root / request["path"]
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    payload["authority"]["production_authority"] = True
    request_path.write_text(json.dumps(payload), encoding="utf-8")

    result = dispatch_requested_spawn_requests(root, run_id="run-b")

    assert result["candidate_count"] == 0
    assert result["queue_packet_candidate_count"] == 0
    assert result["rejection_count"] == 1
    rejection = result["rejections"][0]
    assert rejection["schema_id"] == DISPATCH_REJECTION_SCHEMA_ID
    assert rejection["status"] == "dispatch_rejected"
    assert "forbidden_authority_claim:authority.production_authority" in rejection["reasons"]
    assert rejection["actual_spawn_performed"] is False
    assert rejection["direct_nested_spawn"] is False

    source_after = json.loads(request_path.read_text(encoding="utf-8"))
    assert source_after["status"] == "rejected_by_dispatcher"
    assert source_after["dispatcher_consumption"]["validation_ok"] is False
    assert source_after["dispatcher_consumption"]["source_deleted"] is False


def test_babbage_fanin_spawn_request_proof_gate_dispatches_valid_and_rejects_unsafe(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    valid = _spawn_request(root, row_id="babbage-valid-child")
    spawn_dir = (root / valid["path"]).parent
    unsafe_path = spawn_dir / "babbage-unsafe-child.spawn_request.json"
    unsafe_payload = {
        "schema_id": SPAWN_REQUEST_SCHEMA_ID,
        "kind": "spawn_request",
        "status": "requested",
        "parent_worker_id": "babbage",
        "worker_id": "babbage",
        "requested_domain": "domain.context.cartographer",
        "requested_packet": "PCKT-DOMAIN-WEAVER-UNSAFE-CHILD",
        "allowed_scope": ["claim production authority"],
        "forbidden_actions": ["accepted_state_claim"],
        "evidence_requirements": ["active-root proof"],
        "authority": {
            "accepted_state": True,
            "production_authority": True,
        },
        "spawn_execution": {
            "actual_spawn_performed": False,
            "queue_mediated_required": True,
            "lead_fanin_required": True,
            "raw_external_codex_exec_allowed": False,
            "direct_nested_subagent_spawn_allowed": False,
        },
        "paths": {
            "active_root": str(root),
            "worker_context_path": "ION/05_context/current/domain_weaver/workers/babbage/context",
            "spawn_requests_path": "ION/05_context/current/domain_weaver/workers/babbage/context/spawn_requests",
            "codex_solo_path": "ION/05_context/current/codex_solo",
            "codex_solo_touched": False,
        },
    }
    unsafe_path.write_text(json.dumps(unsafe_payload, indent=2), encoding="utf-8")

    fanin = write_fanin_summary(root, "Babbage", row_id="babbage-spawn-proof")

    assert fanin["spawn_request_count"] == 2
    assert valid["path"] in fanin["spawn_request_refs"]
    assert unsafe_path.relative_to(root).as_posix() in fanin["spawn_request_refs"]

    result = dispatch_requested_spawn_requests(
        root,
        dispatcher_id="lead-codex",
        run_id="proof-gate",
    )

    assert result["requested_count"] == 2
    assert result["candidate_count"] == 1
    assert result["queue_packet_candidate_count"] == 1
    assert result["rejection_count"] == 1
    assert result["blocked_count"] == 0
    assert result["proof_gate"]["requests_inspected"] == 2
    assert result["proof_gate"]["candidates_emitted"] == 1
    assert result["proof_gate"]["queue_packet_candidates_emitted"] == 1
    assert result["proof_gate"]["rejected"] == 1
    assert result["proof_gate"]["blocked"] == 0
    assert result["proof_gate"]["valid_spawn_request_consumed"] is True
    assert result["proof_gate"]["unsafe_spawn_request_rejected"] is True
    assert result["proof_gate"]["actual_spawn_performed"] is False
    assert result["proof_gate"]["direct_nested_spawn"] is False
    assert result["proof_gate"]["raw_external_codex_exec"] is False
    assert result["proof_gate"]["codex_solo_write_allowed"] is False
    assert result["proof_gate"]["queue_packet_candidate_paths"] == [
        result["queue_packet_candidates"][0]["path"]
    ]

    candidate = result["dispatch_candidates"][0]
    assert candidate["source_request_path"] == valid["path"]
    assert candidate["actual_spawn_performed"] is False
    assert candidate["direct_nested_spawn"] is False
    assert candidate["raw_external_codex_exec"] is False
    assert candidate["queue_packet_candidate_ref"] == result["queue_packet_candidates"][0]["path"]

    queue_packet_candidate = result["queue_packet_candidates"][0]
    assert queue_packet_candidate["source_request_path"] == valid["path"]
    assert queue_packet_candidate["source_dispatch_candidate_path"] == candidate["path"]
    assert queue_packet_candidate["bounded_codex_work_packet_request"]["candidate_only"] is True
    assert (
        queue_packet_candidate["bounded_codex_work_packet_request"][
            "actual_spawn_performed"
        ]
        is False
    )

    rejection = result["rejections"][0]
    assert rejection["source_request_path"] == unsafe_path.relative_to(root).as_posix()
    assert "forbidden_authority_claim:authority.accepted_state" in rejection["reasons"]
    assert "forbidden_authority_claim:authority.production_authority" in rejection["reasons"]
    assert "forbidden_scope_claim:production authority" in rejection["reasons"]
    assert "forbidden_action_missing:raw_external_codex_exec" in rejection["reasons"]

    valid_after = json.loads((root / valid["path"]).read_text(encoding="utf-8"))
    unsafe_after = json.loads(unsafe_path.read_text(encoding="utf-8"))
    assert valid_after["status"] == "consumed_by_dispatcher"
    assert unsafe_after["status"] == "rejected_by_dispatcher"


def test_dispatcher_rejects_wrong_active_root_proof(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    request = _spawn_request(root, row_id="wrong-root")
    request_path = root / request["path"]
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    payload["paths"]["active_root"] = str(tmp_path / "other-root")
    request_path.write_text(json.dumps(payload), encoding="utf-8")

    validation = validate_spawn_request(root, request_path, payload)

    assert validation["ok"] is False
    assert "active_root_proof_mismatch" in validation["reasons"]


def test_dispatcher_rejects_missing_boundary_forbidden_actions(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    request = _spawn_request(root, row_id="weak-boundary")
    request_path = root / request["path"]
    payload = json.loads(request_path.read_text(encoding="utf-8"))
    payload["forbidden_actions"] = ["mutate active source"]
    request_path.write_text(json.dumps(payload), encoding="utf-8")

    result = dispatch_requested_spawn_requests(root, run_id="run-c")

    assert result["candidate_count"] == 0
    assert result["queue_packet_candidate_count"] == 0
    assert result["rejection_count"] == 1
    reasons = result["rejections"][0]["reasons"]
    assert "forbidden_action_missing:accepted_state_claim" in reasons
    assert "forbidden_action_missing:raw_external_codex_exec" in reasons
    assert "forbidden_action_missing:direct_nested_subagent_spawn" in reasons


def test_dispatcher_does_not_mark_source_when_disabled(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    request = _spawn_request(root, row_id="preview-only")

    result = dispatch_requested_spawn_requests(root, run_id="run-d", mark_consumed=False)

    assert result["candidate_count"] == 1
    source_after = json.loads((root / request["path"]).read_text(encoding="utf-8"))
    assert source_after["status"] == "requested"
    assert "dispatcher_consumption" not in source_after
