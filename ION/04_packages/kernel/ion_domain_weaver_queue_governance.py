"""Pure Domain Weaver queue-governance helper seam.

This module classifies request mappings and shapes in-memory queue-governance
projection/ledger rows only. It performs no filesystem reads or writes, no
queue runner invocation, no dispatch/start, no lifecycle-ledger mutation, no
materialization, no registry mutation, no operator action history mutation, no
projection refresh/write, no live execution, no UI/topology movement, no
secrets access, and no accepted-state movement.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence


QUEUE_STALE_AFTER_SECONDS = 24 * 60 * 60
DOMAIN_WEAVER_QUEUE_GOVERNANCE_PROJECTION_SCHEMA_ID = (
    "ion.domain_weaver.queue_governance.projection.v0_1_candidate"
)
DOMAIN_WEAVER_QUEUE_GOVERNANCE_PROJECTION_ROW_SCHEMA_ID = (
    "ion.domain_weaver.queue_governance.projection_row.v0_1_candidate"
)
DOMAIN_WEAVER_QUEUE_GOVERNANCE_LEDGER_ROW_SCHEMA_ID = (
    "ion.domain_weaver.queue_governance.ledger_row.v0_1_candidate"
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    raw = str(value).strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _utc_now(now: datetime | None) -> datetime:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc)


def _count_field(rows: Sequence[Mapping[str, Any]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get(field) or "UNKNOWN")
        counts[value] = counts.get(value, 0) + 1
    return counts


def _authority_boundary() -> dict[str, bool]:
    return {
        "candidate_projection_only": True,
        "queue_dispatch_authority": False,
        "queue_start_authority": False,
        "queue_runner_invocation_authority": False,
        "lifecycle_ledger_mutation_authority": False,
        "materialization_write_authority": False,
        "registry_mutation_authority": False,
        "operator_action_history_mutation_authority": False,
        "projection_refresh_authority": False,
        "projection_write_authority": False,
        "live_execution_authority": False,
        "ui_topology_movement_authority": False,
        "secrets_authority": False,
        "production_authority": False,
        "accepted_state_authority": False,
    }


def _stable_row_id(prefix: str, row: Mapping[str, Any]) -> str:
    parts = (
        str(row.get("event_kind") or ""),
        str(row.get("request_id") or ""),
        str(row.get("path") or row.get("source_path") or ""),
        str(row.get("status") or ""),
        str(row.get("lane_id") or ""),
        str(row.get("classification") or ""),
        str(row.get("next_action") or ""),
        str(row.get("dedupe_key") or ""),
        str(row.get("objective_sha256") or ""),
    )
    digest = hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()
    return f"{prefix}:{digest[:32]}"


def queue_lane_for_domain_weaver_request(request: Mapping[str, Any]) -> str:
    raw_metadata = _as_mapping(_as_mapping(request.get("route_enforcement_receipt")).get("route_metadata"))
    raw_route = _as_mapping(raw_metadata.get("raw"))
    work_class = str(request.get("work_class") or raw_route.get("work_class") or "").lower()
    objective = str(request.get("objective") or "").lower()
    request_id = str(request.get("request_id") or "").lower()
    search = f"{work_class} {objective} {request_id}"
    if any(
        term in search
        for term in (
            "approval_governance",
            "approval governance",
            "authority_receipt",
            "authority receipt",
            "receipt_issuance",
            "receipt issuance",
            "accepted_state_movement_authority",
        )
    ):
        return "approval_governance_lane"
    if any(term in search for term in ("queue", "runner", "stale", "currentness", "reconcile", "consolidat", "maintenance")):
        return "maintenance_lane"
    if any(term in search for term in ("nemesis", "audit", "proof", "template_invalid", "review")):
        return "audit_lane"
    if any(term in search for term in ("mason", "implement", "patch", "code", "kernel")):
        return "implementation_lane"
    if any(term in search for term in ("comms", "communication", "team-comms")):
        return "comms_lane"
    if any(term in search for term in ("browser", "dom", "extension")):
        return "browser_lane"
    if any(term in search for term in ("context", "capsule", "ionologist", "cartographer", "manifest")):
        return "context_lane"
    if any(term in search for term in ("vizier", "steward", "architecture", "domain weave", "domain-weave")):
        return "architecture_lane"
    return "needs_triage"


def classify_domain_weaver_queue_request(
    request: Mapping[str, Any],
    *,
    now: datetime | None = None,
    stale_after_seconds: int = QUEUE_STALE_AFTER_SECONDS,
) -> dict[str, Any]:
    """Classify one queue/work-request mapping without reading or mutating state."""

    current_time = _utc_now(now)
    status = str(request.get("status") or "UNKNOWN")
    created = _parse_time(request.get("created_at"))
    updated = _parse_time(request.get("updated_at")) or created
    age_seconds = int((current_time - created).total_seconds()) if created else None
    lane_id = queue_lane_for_domain_weaver_request(request)
    payload = _as_mapping(request.get("payload"))
    lifecycle_decision = _as_mapping(request.get("queue_lifecycle_decision") or payload.get("queue_lifecycle_decision"))
    lifecycle_disposition = str(lifecycle_decision.get("disposition") or "")
    lifecycle_classified = bool(lifecycle_decision)
    classification = "current_or_terminal"
    next_action = "observe"
    stale = False
    terminal_repair_needed = False
    if status in {"QUEUED_FOR_CODEX_CARRIER", "PREPARED_FOR_CODEX_CARRIER_NOT_QUEUED"}:
        if age_seconds is not None and age_seconds > stale_after_seconds:
            classification = "stale_waiting_request"
            next_action = "reconcile_or_supersede_before_claim"
            stale = True
        else:
            classification = "fresh_waiting_request"
            next_action = "eligible_for_lane_claim"
    elif status == "RETURN_TEMPLATE_INVALID":
        if lifecycle_classified:
            classification = "classified_terminal_return_contract_backlog"
            next_action = lifecycle_disposition or "preserve_lifecycle_classification"
        else:
            classification = "terminal_return_contract_repair"
            next_action = "repair_or_digest_template_invalid_evidence"
            terminal_repair_needed = True
    elif status in {"CODEX_QUEUE_RUNNER_FAILED", "CODEX_CLI_EXIT_NONZERO", "RETURN_RECORDED_PROOF_BLOCKED"}:
        if lifecycle_classified:
            classification = "classified_terminal_blocked_or_failed_backlog"
            next_action = lifecycle_disposition or "preserve_lifecycle_classification"
        else:
            classification = "terminal_blocked_or_failed_repair"
            next_action = "classify_blocker_and_emit_repair_packet"
            terminal_repair_needed = True
    elif status == "RETURN_RECORDED_PROOF_ACCEPTED":
        classification = "accepted_terminal"
        next_action = "preserve_receipt"
    diagnosis = _as_mapping(request.get("settlement_relevant_automation_diagnosis"))
    return {
        "request_id": request.get("request_id"),
        "path": str(request.get("path") or ""),
        "status": status,
        "lane_id": lane_id,
        "created_at": request.get("created_at"),
        "updated_at": request.get("updated_at"),
        "age_seconds": age_seconds,
        "updated_age_seconds": int((current_time - updated).total_seconds()) if updated else None,
        "classification": classification,
        "next_action": next_action,
        "stale": stale,
        "terminal_repair_needed": terminal_repair_needed,
        "classified_by_queue_lifecycle_decision": lifecycle_classified,
        "queue_lifecycle_disposition": lifecycle_disposition or None,
        "linked_return_count": request.get("linked_return_count", 0),
        "accepted_return_count": request.get("accepted_return_count", 0),
        "automation_diagnosis_classification": diagnosis.get("classification"),
        "automation_diagnosis_finding_count": int(diagnosis.get("finding_count") or 0),
        "dedupe_key": request.get("dedupe_key"),
        "objective_sha256": request.get("objective_sha256"),
        "objective_excerpt": str(request.get("objective") or "")[:240],
    }


def _is_actionable_duplicate_candidate(row: Mapping[str, Any]) -> bool:
    status = str(row.get("status") or "").upper()
    if status.startswith("SUPERSEDED"):
        return False
    if status in {"RETURN_RECORDED_PROOF_ACCEPTED", "INVALID_PLACEHOLDER_ACTION_ARCHIVE_ONLY"}:
        return False
    if row.get("classified_by_queue_lifecycle_decision") and status in {
        "RETURN_TEMPLATE_INVALID",
        "CODEX_QUEUE_RUNNER_FAILED",
        "CODEX_CLI_EXIT_NONZERO",
        "RETURN_RECORDED_PROOF_BLOCKED",
    }:
        return False
    return True


def actionable_domain_weaver_duplicate_group_count(rows: Sequence[Mapping[str, Any]]) -> int:
    groups: dict[str, int] = {}
    for row in rows:
        if not _is_actionable_duplicate_candidate(row):
            continue
        key = str(row.get("dedupe_key") or row.get("objective_sha256") or "").strip()
        if key:
            groups[key] = groups.get(key, 0) + 1
    return sum(1 for count in groups.values() if count > 1)


def domain_weaver_duplicate_group_count(rows: Sequence[Mapping[str, Any]]) -> int:
    groups: dict[str, int] = {}
    for row in rows:
        key = str(row.get("dedupe_key") or row.get("objective_sha256") or "").strip()
        if key:
            groups[key] = groups.get(key, 0) + 1
    return sum(1 for count in groups.values() if count > 1)


def shape_domain_weaver_queue_projection_row(
    request: Mapping[str, Any],
    *,
    now: datetime | None = None,
    stale_after_seconds: int = QUEUE_STALE_AFTER_SECONDS,
    source_path: str | None = None,
) -> dict[str, Any]:
    """Shape one in-memory projection row without refreshing or writing a projection."""

    classified = classify_domain_weaver_queue_request(
        request,
        now=now,
        stale_after_seconds=stale_after_seconds,
    )
    path = str(source_path or classified.get("path") or "")
    row = {
        "schema_id": DOMAIN_WEAVER_QUEUE_GOVERNANCE_PROJECTION_ROW_SCHEMA_ID,
        "row_kind": "domain_weaver_queue_request_governance_projection",
        "request_id": classified.get("request_id"),
        "source_path": path,
        "status": classified.get("status"),
        "lane_id": classified.get("lane_id"),
        "classification": classified.get("classification"),
        "next_action": classified.get("next_action"),
        "stale": bool(classified.get("stale")),
        "terminal_repair_needed": bool(classified.get("terminal_repair_needed")),
        "classified_by_queue_lifecycle_decision": bool(classified.get("classified_by_queue_lifecycle_decision")),
        "queue_lifecycle_disposition": classified.get("queue_lifecycle_disposition"),
        "age_seconds": classified.get("age_seconds"),
        "updated_age_seconds": classified.get("updated_age_seconds"),
        "created_at": classified.get("created_at"),
        "updated_at": classified.get("updated_at"),
        "linked_return_count": classified.get("linked_return_count"),
        "accepted_return_count": classified.get("accepted_return_count"),
        "automation_diagnosis_classification": classified.get("automation_diagnosis_classification"),
        "automation_diagnosis_finding_count": classified.get("automation_diagnosis_finding_count"),
        "dedupe_key": classified.get("dedupe_key"),
        "objective_sha256": classified.get("objective_sha256"),
        "objective_excerpt": classified.get("objective_excerpt"),
        "authority": _authority_boundary(),
    }
    row["row_id"] = _stable_row_id("dwqg_projection", {**row, "path": path})
    return row


def shape_domain_weaver_queue_ledger_row(
    request: Mapping[str, Any],
    *,
    now: datetime | None = None,
    stale_after_seconds: int = QUEUE_STALE_AFTER_SECONDS,
    event_kind: str = "queue_request_classified",
    source_path: str | None = None,
) -> dict[str, Any]:
    """Shape one candidate lifecycle-ledger row without mutating a ledger."""

    classified = classify_domain_weaver_queue_request(
        request,
        now=now,
        stale_after_seconds=stale_after_seconds,
    )
    path = str(source_path or classified.get("path") or "")
    row = {
        "schema_id": DOMAIN_WEAVER_QUEUE_GOVERNANCE_LEDGER_ROW_SCHEMA_ID,
        "row_kind": "domain_weaver_queue_request_lifecycle_ledger_candidate",
        "event_kind": event_kind,
        "request_id": classified.get("request_id"),
        "source_path": path,
        "status": classified.get("status"),
        "lane_id": classified.get("lane_id"),
        "classification": classified.get("classification"),
        "recommended_lifecycle_disposition": classified.get("next_action"),
        "stale": bool(classified.get("stale")),
        "terminal_repair_needed": bool(classified.get("terminal_repair_needed")),
        "classified_by_queue_lifecycle_decision": bool(classified.get("classified_by_queue_lifecycle_decision")),
        "queue_lifecycle_disposition": classified.get("queue_lifecycle_disposition"),
        "linked_return_count": classified.get("linked_return_count"),
        "accepted_return_count": classified.get("accepted_return_count"),
        "dedupe_key": classified.get("dedupe_key"),
        "objective_sha256": classified.get("objective_sha256"),
        "would_write_lifecycle_ledger": False,
        "would_mutate_request_file": False,
        "would_refresh_projection": False,
        "authority": _authority_boundary(),
    }
    row["row_id"] = _stable_row_id("dwqg_ledger", {**row, "path": path})
    return row


def shape_domain_weaver_queue_governance_rows(
    requests: Sequence[Mapping[str, Any]],
    *,
    now: datetime | None = None,
    stale_after_seconds: int = QUEUE_STALE_AFTER_SECONDS,
) -> dict[str, Any]:
    """Shape a deterministic candidate queue-governance projection payload."""

    current_time = _utc_now(now)
    classified = [
        classify_domain_weaver_queue_request(row, now=current_time, stale_after_seconds=stale_after_seconds)
        for row in requests
    ]
    projection_rows = [
        shape_domain_weaver_queue_projection_row(row, now=current_time, stale_after_seconds=stale_after_seconds)
        for row in requests
    ]
    ledger_rows = [
        shape_domain_weaver_queue_ledger_row(row, now=current_time, stale_after_seconds=stale_after_seconds)
        for row in requests
    ]
    waiting_rows = [
        row
        for row in classified
        if row.get("status") in {"QUEUED_FOR_CODEX_CARRIER", "PREPARED_FOR_CODEX_CARRIER_NOT_QUEUED"}
    ]
    queued_rows = [row for row in classified if row.get("status") == "QUEUED_FOR_CODEX_CARRIER"]
    prepared_rows = [row for row in classified if row.get("status") == "PREPARED_FOR_CODEX_CARRIER_NOT_QUEUED"]
    stale_rows = [row for row in classified if row.get("stale")]
    repair_rows = [row for row in classified if row.get("terminal_repair_needed")]
    classified_terminal_rows = [
        row
        for row in classified
        if row.get("classified_by_queue_lifecycle_decision")
        and str(row.get("status") or "")
        in {"RETURN_TEMPLATE_INVALID", "CODEX_QUEUE_RUNNER_FAILED", "CODEX_CLI_EXIT_NONZERO", "RETURN_RECORDED_PROOF_BLOCKED"}
    ]
    return {
        "schema_id": DOMAIN_WEAVER_QUEUE_GOVERNANCE_PROJECTION_SCHEMA_ID,
        "as_of": current_time.replace(microsecond=0).isoformat(),
        "request_count": len(classified),
        "projection_row_count": len(projection_rows),
        "ledger_candidate_row_count": len(ledger_rows),
        "summary": {
            "classified_request_count": len(classified),
            "waiting_request_count": len(waiting_rows),
            "claimable_waiting_request_count": len(queued_rows),
            "prepared_request_count": len(prepared_rows),
            "stale_waiting_request_count": len(stale_rows),
            "terminal_repair_request_count": len(repair_rows),
            "classified_terminal_backlog_count": len(classified_terminal_rows),
            "duplicate_group_count": domain_weaver_duplicate_group_count(classified),
            "actionable_duplicate_group_count": actionable_domain_weaver_duplicate_group_count(classified),
        },
        "status_counts": _count_field(classified, "status"),
        "lane_counts": _count_field(classified, "lane_id"),
        "projection_rows": projection_rows,
        "ledger_candidate_rows": ledger_rows,
        "policy": (
            "Domain Weaver queue governance rows are in-memory candidate shapes only; "
            "they do not dispatch queues, mutate lifecycle ledgers, materialize files, "
            "write projections, write operator history, or claim accepted state."
        ),
        "authority": _authority_boundary(),
    }


__all__ = [
    "DOMAIN_WEAVER_QUEUE_GOVERNANCE_LEDGER_ROW_SCHEMA_ID",
    "DOMAIN_WEAVER_QUEUE_GOVERNANCE_PROJECTION_ROW_SCHEMA_ID",
    "DOMAIN_WEAVER_QUEUE_GOVERNANCE_PROJECTION_SCHEMA_ID",
    "QUEUE_STALE_AFTER_SECONDS",
    "actionable_domain_weaver_duplicate_group_count",
    "classify_domain_weaver_queue_request",
    "domain_weaver_duplicate_group_count",
    "queue_lane_for_domain_weaver_request",
    "shape_domain_weaver_queue_governance_rows",
    "shape_domain_weaver_queue_ledger_row",
    "shape_domain_weaver_queue_projection_row",
]
