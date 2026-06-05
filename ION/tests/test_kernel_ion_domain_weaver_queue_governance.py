from __future__ import annotations

import ast
import importlib
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from kernel import ion_domain_weaver
from kernel import ion_domain_weaver_queue_governance as governance
from kernel import ion_queue_governor


def _request(**overrides: Any) -> dict[str, Any]:
    now = datetime(2026, 6, 3, 12, 0, 0, tzinfo=timezone.utc)
    created_at = overrides.pop("created_at", now - timedelta(minutes=5))
    request = {
        "request_id": "codex_req_domain_weaver_queue_governance_001",
        "path": "ION/05_context/current/chatgpt_connector/codex_work_requests/request.json",
        "status": "QUEUED_FOR_CODEX_CARRIER",
        "created_at": created_at.replace(microsecond=0).isoformat(),
        "updated_at": created_at.replace(microsecond=0).isoformat(),
        "objective": "Reconcile stale queue currentness for Domain Weaver.",
        "dedupe_key": "domain_weaver_queue_governance",
        "objective_sha256": "objective-digest",
        "linked_return_count": 0,
        "accepted_return_count": 0,
    }
    request.update(overrides)
    return request


def test_domain_weaver_classification_matches_queue_governor_for_representative_request() -> None:
    now = datetime(2026, 6, 3, 12, 0, 0, tzinfo=timezone.utc)
    request = _request(
        status="RETURN_TEMPLATE_INVALID",
        objective="Audit template_invalid queue evidence.",
        payload={
            "queue_lifecycle_decision": {
                "schema_id": "ion.codex_work_request_queue_lifecycle_decision.v1",
                "disposition": "digest_then_supersede",
            }
        },
        settlement_relevant_automation_diagnosis={"classification": "template_contract_drift", "finding_count": 2},
        linked_return_count=1,
    )

    assert governance.queue_lane_for_domain_weaver_request(request) == ion_queue_governor.queue_lane_for_request(request)
    assert governance.classify_domain_weaver_queue_request(request, now=now) == ion_queue_governor.classify_queue_request(
        request,
        now=now,
    )


def test_projection_row_shapes_stale_request_without_dispatch_or_projection_write_authority() -> None:
    now = datetime(2026, 6, 3, 12, 0, 0, tzinfo=timezone.utc)
    request = _request(created_at=now - timedelta(days=3))

    row = governance.shape_domain_weaver_queue_projection_row(request, now=now)

    assert row["schema_id"] == governance.DOMAIN_WEAVER_QUEUE_GOVERNANCE_PROJECTION_ROW_SCHEMA_ID
    assert row["row_kind"] == "domain_weaver_queue_request_governance_projection"
    assert row["classification"] == "stale_waiting_request"
    assert row["next_action"] == "reconcile_or_supersede_before_claim"
    assert row["stale"] is True
    assert row["terminal_repair_needed"] is False
    assert row["authority"]["candidate_projection_only"] is True
    assert row["authority"]["queue_dispatch_authority"] is False
    assert row["authority"]["projection_write_authority"] is False
    assert row["authority"]["lifecycle_ledger_mutation_authority"] is False
    assert row["authority"]["accepted_state_authority"] is False


def test_ledger_row_is_stable_candidate_shape_without_lifecycle_mutation() -> None:
    now = datetime(2026, 6, 3, 12, 0, 0, tzinfo=timezone.utc)
    request = _request(
        created_at=now - timedelta(days=2),
        status="CODEX_QUEUE_RUNNER_FAILED",
        objective="Classify blocker and emit repair packet candidate.",
    )

    first = governance.shape_domain_weaver_queue_ledger_row(request, now=now)
    second = governance.shape_domain_weaver_queue_ledger_row(request, now=now)

    assert first == second
    assert first["schema_id"] == governance.DOMAIN_WEAVER_QUEUE_GOVERNANCE_LEDGER_ROW_SCHEMA_ID
    assert first["row_kind"] == "domain_weaver_queue_request_lifecycle_ledger_candidate"
    assert first["classification"] == "terminal_blocked_or_failed_repair"
    assert first["recommended_lifecycle_disposition"] == "classify_blocker_and_emit_repair_packet"
    assert first["would_write_lifecycle_ledger"] is False
    assert first["would_mutate_request_file"] is False
    assert first["would_refresh_projection"] is False
    assert first["authority"]["queue_runner_invocation_authority"] is False
    assert first["authority"]["materialization_write_authority"] is False
    assert first["authority"]["operator_action_history_mutation_authority"] is False


def test_governance_projection_payload_summarizes_rows_without_writes() -> None:
    now = datetime(2026, 6, 3, 12, 0, 0, tzinfo=timezone.utc)
    requests = [
        _request(request_id="codex_req_fresh", created_at=now - timedelta(minutes=5)),
        _request(request_id="codex_req_stale", created_at=now - timedelta(days=3)),
        _request(
            request_id="codex_req_template_invalid",
            created_at=now - timedelta(days=3),
            status="RETURN_TEMPLATE_INVALID",
            objective="Audit template invalid return.",
        ),
        _request(
            request_id="codex_req_accepted",
            created_at=now - timedelta(days=3),
            status="RETURN_RECORDED_PROOF_ACCEPTED",
            objective="Preserve accepted receipt.",
            accepted_return_count=1,
        ),
    ]

    payload = governance.shape_domain_weaver_queue_governance_rows(requests, now=now)

    assert payload["schema_id"] == governance.DOMAIN_WEAVER_QUEUE_GOVERNANCE_PROJECTION_SCHEMA_ID
    assert payload["request_count"] == 4
    assert payload["projection_row_count"] == 4
    assert payload["ledger_candidate_row_count"] == 4
    assert payload["summary"]["waiting_request_count"] == 2
    assert payload["summary"]["stale_waiting_request_count"] == 1
    assert payload["summary"]["terminal_repair_request_count"] == 1
    assert payload["summary"]["actionable_duplicate_group_count"] == 1
    assert payload["status_counts"]["RETURN_RECORDED_PROOF_ACCEPTED"] == 1
    assert payload["authority"]["queue_start_authority"] is False
    assert payload["authority"]["projection_refresh_authority"] is False
    assert payload["authority"]["production_authority"] is False


def test_monolith_queue_governance_compatibility_wrappers_match_helper_payloads() -> None:
    now = datetime(2026, 6, 3, 12, 0, 0, tzinfo=timezone.utc)
    requests = [
        _request(request_id="codex_req_fresh", created_at=now - timedelta(minutes=5)),
        _request(request_id="codex_req_stale", created_at=now - timedelta(days=3)),
        _request(
            request_id="codex_req_failed",
            created_at=now - timedelta(days=2),
            status="CODEX_QUEUE_RUNNER_FAILED",
            objective="Classify blocker and emit repair packet candidate.",
        ),
    ]
    request = requests[1]

    assert ion_domain_weaver.QUEUE_STALE_AFTER_SECONDS == governance.QUEUE_STALE_AFTER_SECONDS
    assert (
        ion_domain_weaver.DOMAIN_WEAVER_QUEUE_GOVERNANCE_PROJECTION_SCHEMA_ID
        == governance.DOMAIN_WEAVER_QUEUE_GOVERNANCE_PROJECTION_SCHEMA_ID
    )
    assert (
        ion_domain_weaver.DOMAIN_WEAVER_QUEUE_GOVERNANCE_PROJECTION_ROW_SCHEMA_ID
        == governance.DOMAIN_WEAVER_QUEUE_GOVERNANCE_PROJECTION_ROW_SCHEMA_ID
    )
    assert (
        ion_domain_weaver.DOMAIN_WEAVER_QUEUE_GOVERNANCE_LEDGER_ROW_SCHEMA_ID
        == governance.DOMAIN_WEAVER_QUEUE_GOVERNANCE_LEDGER_ROW_SCHEMA_ID
    )
    assert ion_domain_weaver.queue_lane_for_domain_weaver_request(
        request
    ) == governance.queue_lane_for_domain_weaver_request(request)
    assert ion_domain_weaver.classify_domain_weaver_queue_request(
        request,
        now=now,
    ) == governance.classify_domain_weaver_queue_request(
        request,
        now=now,
    )
    assert ion_domain_weaver.shape_domain_weaver_queue_projection_row(
        request,
        now=now,
        source_path="ION/05_context/current/chatgpt_connector/codex_work_requests/request.json",
    ) == governance.shape_domain_weaver_queue_projection_row(
        request,
        now=now,
        source_path="ION/05_context/current/chatgpt_connector/codex_work_requests/request.json",
    )
    assert ion_domain_weaver.shape_domain_weaver_queue_ledger_row(
        request,
        now=now,
    ) == governance.shape_domain_weaver_queue_ledger_row(
        request,
        now=now,
    )
    assert ion_domain_weaver.shape_domain_weaver_queue_governance_rows(
        requests,
        now=now,
    ) == governance.shape_domain_weaver_queue_governance_rows(
        requests,
        now=now,
    )
    assert ion_domain_weaver.domain_weaver_duplicate_group_count(
        requests
    ) == governance.domain_weaver_duplicate_group_count(requests)
    assert ion_domain_weaver.actionable_domain_weaver_duplicate_group_count(
        requests
    ) == governance.actionable_domain_weaver_duplicate_group_count(requests)


def test_queue_governance_helper_has_no_reverse_or_stateful_imports() -> None:
    sys.modules.pop("kernel.ion_domain_weaver_queue_governance", None)
    sys.modules.pop("kernel.ion_domain_weaver", None)
    sys.modules.pop("kernel.ion_queue_governor", None)

    module = importlib.import_module("kernel.ion_domain_weaver_queue_governance")

    assert module.DOMAIN_WEAVER_QUEUE_GOVERNANCE_PROJECTION_SCHEMA_ID == (
        governance.DOMAIN_WEAVER_QUEUE_GOVERNANCE_PROJECTION_SCHEMA_ID
    )
    assert "kernel.ion_domain_weaver" not in sys.modules
    assert "kernel.ion_queue_governor" not in sys.modules

    source_path = Path(module.__file__).resolve()
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    observed_imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            observed_imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            observed_imports.append(node.module or "")

    assert observed_imports == ["__future__", "hashlib", "datetime", "typing"]
    forbidden_import_fragments = (
        "ion_domain_weaver",
        "ion_queue_governor",
        "queue_runner",
        "materializ",
        "dispatcher",
        "operator_action",
        "projection_refresh",
        "registry",
        "live",
        "topology",
        "cockpit",
        "secret",
    )
    assert not any(
        fragment in imported
        for imported in observed_imports
        for fragment in forbidden_import_fragments
    )
