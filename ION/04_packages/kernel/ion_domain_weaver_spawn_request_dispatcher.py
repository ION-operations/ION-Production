"""Lead-side dispatcher for Domain Weaver worker-local spawn requests.

Workers may request child specialists by writing worker-local
``spawn_requests/*.spawn_request.json`` artifacts. This module consumes those
requests into lead/queue dispatch candidates without spawning a process,
calling Codex, writing Codex Solo, or granting production/live/accepted-state
authority.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

from kernel.ion_chatgpt_browser_mcp_connector_contract import call_chatgpt_connector_tool
from kernel.ion_codex_queue_runner import (
    EXECUTABLE_CODEX_WORK_LANES,
    normalize_codex_work_lane_id,
)
from kernel.ion_domain_weaver_worker_start_readiness import (
    build_domain_weaver_worker_start_readiness,
)
from kernel.ion_domain_weaver_worker_context_lanes import (
    SPAWN_REQUEST_SCHEMA_ID,
    WORKER_CONTEXT_RELATIVE_ROOT,
    sanitize_worker_id,
)


DISPATCH_CANDIDATE_SCHEMA_ID = "ion.domain_weaver.spawn_dispatch_candidate.v0_1"
DISPATCH_REJECTION_SCHEMA_ID = "ion.domain_weaver.spawn_dispatch_rejection.v0_1"
DISPATCH_RUN_SCHEMA_ID = "ion.domain_weaver.spawn_dispatch_run.v0_1"
QUEUE_PACKET_CANDIDATE_SCHEMA_ID = (
    "ion.domain_weaver.spawn_dispatch_queue_packet_candidate.v0_1"
)
DISPATCH_ENQUEUE_RECEIPT_SCHEMA_ID = (
    "ion.domain_weaver.spawn_dispatch_enqueue_receipt.v0_1"
)
DISPATCH_ENQUEUE_RUN_SCHEMA_ID = "ion.domain_weaver.spawn_dispatch_enqueue_run.v0_1"
CODEX_WORK_PACKET_REQUEST_CANDIDATE_SCHEMA_ID = (
    "ion.codex.work_packet_request_candidate.v0_1"
)
SPAWN_DISPATCH_START_PLAN_SCHEMA_ID = (
    "ion.domain_weaver.spawn_dispatch_start_plan.v0_1_candidate"
)
LEGACY_RECEIPT_QUARANTINE_SCHEMA_ID = (
    "ion.domain_weaver.spawn_dispatch_legacy_receipt_quarantine.v0_1_candidate"
)

SPAWN_DISPATCH_RELATIVE_ROOT = Path("ION/05_context/current/domain_weaver/spawn_dispatch")
CODEX_WORK_REQUESTS_RELATIVE_ROOT = Path(
    "ION/05_context/current/chatgpt_connector/codex_work_requests"
)
DEFAULT_LEGACY_RECEIPT_QUARANTINE_ARTIFACTS = (
    Path("ION/05_context/current/domain_weaver/acceleration/DW_SPW_002_OVERFLOW_QUEUE_MEDIATED_SPAWN.latest.json"),
)
QUEUEABLE_FOR_CODEX_STATUS = "QUEUED_FOR_CODEX_CARRIER"

_REQUIRED_FORBIDDEN_ACTIONS = {
    "accepted_state_claim",
    "production_or_live_execution",
    "secrets_access",
    "registry_or_materialization_movement",
    "direct_codex_solo_write",
    "raw_external_codex_exec",
    "direct_nested_subagent_spawn",
}

_FORBIDDEN_AUTHORITY_KEYS = {
    "accepted_state",
    "accepted_state_authority",
    "accepted_state_claim",
    "production",
    "production_authority",
    "live_execution",
    "live_execution_authority",
    "secrets",
    "secret_access",
    "secrets_authority",
    "registry_movement",
    "materialization",
    "materialization_authority",
    "materialization_movement",
    "materialize_all",
}

_FORBIDDEN_TEXT_CLAIM_MARKERS = {
    "accepted-state claim",
    "accepted_state_claim",
    "accepted state claim",
    "production authority",
    "live execution authority",
    "secret access",
    "secrets access",
    "registry movement",
    "materialization movement",
    "materialize_all",
}


def find_requested_spawn_requests(active_root: str | Path) -> list[dict[str, Any]]:
    """Return requested worker-local spawn requests under the active root."""

    root = _require_active_root(active_root)
    worker_root = root / WORKER_CONTEXT_RELATIVE_ROOT
    if not worker_root.exists():
        return []
    requests: list[dict[str, Any]] = []
    for path in sorted(worker_root.glob("*/context/spawn_requests/*.spawn_request.json")):
        payload = _read_json(path)
        if isinstance(payload, Mapping) and payload.get("status") == "requested":
            requests.append(
                {
                    "path": _relative_posix(root, path),
                    "absolute_path": str(path),
                    "request": dict(payload),
                }
            )
    return requests


def enqueue_requested_spawn_requests(
    active_root: str | Path,
    *,
    dispatcher_id: str = "lead_codex",
    mark_consumed: bool = True,
    run_id: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Enqueue validated spawn rows as bounded Codex work requests.

    This is the ION-native fanout handoff: valid worker-local spawn requests
    become ``QUEUED_FOR_CODEX_CARRIER`` work request rows through the connector
    contract. It does not start a queue worker, run Codex, write Codex Solo, or
    settle product state.
    """

    root = _require_active_root(active_root)
    run_key = _safe_fragment(run_id or _utc_stamp())
    entries = find_requested_spawn_requests(root)
    if limit is not None:
        entries = entries[: max(0, int(limit))]

    dispatch_candidates: list[dict[str, Any]] = []
    queue_packet_candidates: list[dict[str, Any]] = []
    enqueue_receipts: list[dict[str, Any]] = []
    blocked_enqueue_receipts: list[dict[str, Any]] = []
    rejections: list[dict[str, Any]] = []

    for entry in entries:
        source_path = root / entry["path"]
        request = dict(entry["request"])
        validation = validate_spawn_request(root, source_path, request)
        if not validation["ok"]:
            rejection = _write_dispatch_rejection(
                root,
                source_path,
                request,
                validation["reasons"],
                dispatcher_id=dispatcher_id,
                run_key=run_key,
            )
            rejections.append(rejection)
            if mark_consumed:
                _mark_request(
                    source_path,
                    request,
                    status="rejected_by_dispatcher",
                    dispatcher_id=dispatcher_id,
                    dispatch_ref=rejection["path"],
                    validation=validation,
                )
            continue

        candidate = _write_dispatch_candidate(
            root,
            source_path,
            request,
            dispatcher_id=dispatcher_id,
            run_key=run_key,
        )
        queue_packet_candidate = _write_queue_packet_candidate(
            root,
            source_path,
            request,
            dispatch_candidate=candidate,
            dispatcher_id=dispatcher_id,
            run_key=run_key,
        )
        dispatch_candidates.append(candidate)
        queue_packet_candidates.append(queue_packet_candidate)

        connector_args = _codex_work_request_args_for_spawn_request(
            root,
            source_path,
            request,
            dispatch_candidate=candidate,
            queue_packet_candidate=queue_packet_candidate,
        )
        connector_result = call_chatgpt_connector_tool(
            root,
            "ion_request_codex_work_packet",
            connector_args,
        )
        enqueue_receipt = _write_dispatch_enqueue_receipt(
            root,
            source_path,
            request,
            dispatch_candidate=candidate,
            queue_packet_candidate=queue_packet_candidate,
            connector_args=connector_args,
            connector_result=connector_result,
            dispatcher_id=dispatcher_id,
            run_key=run_key,
        )
        enqueue_succeeded = spawn_dispatch_enqueue_succeeded(enqueue_receipt)
        if enqueue_succeeded:
            enqueue_receipts.append(enqueue_receipt)
        else:
            blocked_enqueue_receipts.append(enqueue_receipt)
        if mark_consumed and enqueue_succeeded:
            _mark_request(
                source_path,
                request,
                status="enqueued_by_dispatcher",
                dispatcher_id=dispatcher_id,
                dispatch_ref=enqueue_receipt["path"],
                validation=validation,
            )
        elif mark_consumed:
            _mark_request(
                source_path,
                request,
                status="enqueue_blocked_by_dispatcher",
                dispatcher_id=dispatcher_id,
                dispatch_ref=enqueue_receipt["path"],
                validation={
                    **dict(validation),
                    "ok": False,
                    "reasons": list(validation.get("reasons") or [])
                    + spawn_dispatch_enqueue_blockers(enqueue_receipt),
                },
            )

    proof_gate = {
        "status": "spawn_request_enqueue_gate_evaluated",
        "requests_inspected": len(entries),
        "enqueued": len(enqueue_receipts),
        "enqueue_blocked": len(blocked_enqueue_receipts),
        "rejected": len(rejections),
        "lead_fanin_required": True,
        "queue_mediated_required": True,
        "actual_spawn_performed": False,
        "direct_nested_spawn": False,
        "raw_external_codex_exec": False,
        "codex_solo_write_allowed": False,
        "codex_queue_run_started": False,
        "worker_start_allowed": False,
        "enqueue_receipt_paths": [str(row.get("path")) for row in enqueue_receipts],
        "blocked_enqueue_receipt_paths": [
            str(row.get("path")) for row in blocked_enqueue_receipts
        ],
        "rejection_paths": [str(row.get("path")) for row in rejections],
    }
    return {
        "schema_id": DISPATCH_ENQUEUE_RUN_SCHEMA_ID,
        "status": "dispatch_enqueue_run_completed",
        "created_at": _utc_now(),
        "active_root": str(root),
        "dispatcher_id": str(dispatcher_id),
        "requested_count": len(entries),
        "candidate_count": len(dispatch_candidates),
        "queue_packet_candidate_count": len(queue_packet_candidates),
        "enqueue_receipt_count": len(enqueue_receipts),
        "blocked_enqueue_receipt_count": len(blocked_enqueue_receipts),
        "rejection_count": len(rejections),
        "mark_consumed": bool(mark_consumed),
        "actual_spawn_performed": False,
        "direct_nested_spawn": False,
        "raw_external_codex_exec": False,
        "codex_solo_write_allowed": False,
        "codex_queue_run_started": False,
        "worker_start_allowed": False,
        "lead_fanin_required": True,
        "proof_gate": proof_gate,
        "dispatch_candidates": dispatch_candidates,
        "queue_packet_candidates": queue_packet_candidates,
        "enqueue_receipts": enqueue_receipts,
        "blocked_enqueue_receipts": blocked_enqueue_receipts,
        "rejections": rejections,
    }


def dispatch_requested_spawn_requests(
    active_root: str | Path,
    *,
    dispatcher_id: str = "lead_codex",
    mark_consumed: bool = True,
    run_id: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Validate requested spawn requests and emit dispatch candidates.

    Invalid requested artifacts produce rejection receipts. Valid requests
    produce dispatch candidates. When ``mark_consumed`` is true, the source
    request artifact remains in place and is status-marked with dispatcher
    metadata.
    """

    root = _require_active_root(active_root)
    run_key = _safe_fragment(run_id or _utc_stamp())
    entries = find_requested_spawn_requests(root)
    if limit is not None:
        entries = entries[: max(0, int(limit))]

    dispatch_candidates: list[dict[str, Any]] = []
    queue_packet_candidates: list[dict[str, Any]] = []
    rejections: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []

    for entry in entries:
        source_path = root / entry["path"]
        request = dict(entry["request"])
        validation = validate_spawn_request(root, source_path, request)
        if validation["ok"]:
            candidate = _write_dispatch_candidate(
                root,
                source_path,
                request,
                dispatcher_id=dispatcher_id,
                run_key=run_key,
            )
            queue_packet_candidate = _write_queue_packet_candidate(
                root,
                source_path,
                request,
                dispatch_candidate=candidate,
                dispatcher_id=dispatcher_id,
                run_key=run_key,
            )
            dispatch_candidates.append(candidate)
            queue_packet_candidates.append(queue_packet_candidate)
            if mark_consumed:
                _mark_request(
                    source_path,
                    request,
                    status="consumed_by_dispatcher",
                    dispatcher_id=dispatcher_id,
                    dispatch_ref=candidate["path"],
                    validation=validation,
                )
        else:
            rejection = _write_dispatch_rejection(
                root,
                source_path,
                request,
                validation["reasons"],
                dispatcher_id=dispatcher_id,
                run_key=run_key,
            )
            rejections.append(rejection)
            if mark_consumed:
                _mark_request(
                    source_path,
                    request,
                    status="rejected_by_dispatcher",
                    dispatcher_id=dispatcher_id,
                    dispatch_ref=rejection["path"],
                    validation=validation,
                )

    proof_gate = {
        "status": "spawn_request_dispatcher_proof_gate_evaluated",
        "requests_inspected": len(entries),
        "candidates_emitted": len(dispatch_candidates),
        "queue_packet_candidates_emitted": len(queue_packet_candidates),
        "rejected": len(rejections),
        "blocked": len(blocked),
        "requested_count": len(entries),
        "candidate_count": len(dispatch_candidates),
        "queue_packet_candidate_count": len(queue_packet_candidates),
        "rejection_count": len(rejections),
        "blocked_count": len(blocked),
        "valid_spawn_request_consumed": bool(dispatch_candidates),
        "unsafe_spawn_request_rejected": bool(rejections),
        "lead_fanin_required": True,
        "queue_mediated_required": True,
        "actual_spawn_performed": False,
        "direct_nested_spawn": False,
        "raw_external_codex_exec": False,
        "codex_solo_write_allowed": False,
        "dispatch_candidate_paths": [
            str(candidate.get("path")) for candidate in dispatch_candidates
        ],
        "queue_packet_candidate_paths": [
            str(candidate.get("path")) for candidate in queue_packet_candidates
        ],
        "rejection_paths": [str(rejection.get("path")) for rejection in rejections],
        "blocked_paths": [str(item.get("path")) for item in blocked],
    }

    return {
        "schema_id": DISPATCH_RUN_SCHEMA_ID,
        "status": "dispatch_run_completed",
        "created_at": _utc_now(),
        "active_root": str(root),
        "dispatcher_id": str(dispatcher_id),
        "requests_inspected": len(entries),
        "candidates_emitted": len(dispatch_candidates),
        "queue_packet_candidates_emitted": len(queue_packet_candidates),
        "rejected": len(rejections),
        "blocked": len(blocked),
        "requested_count": len(entries),
        "candidate_count": len(dispatch_candidates),
        "queue_packet_candidate_count": len(queue_packet_candidates),
        "rejection_count": len(rejections),
        "blocked_count": len(blocked),
        "mark_consumed": bool(mark_consumed),
        "actual_spawn_performed": False,
        "direct_nested_spawn": False,
        "raw_external_codex_exec": False,
        "live_queue_state_mutated": False,
        "codex_work_request_written": False,
        "codex_queue_run_started": False,
        "lead_fanin_required": True,
        "proof_gate": proof_gate,
        "dispatch_candidates": dispatch_candidates,
        "queue_packet_candidates": queue_packet_candidates,
        "rejections": rejections,
        "blocked_items": blocked,
    }


def build_spawn_dispatch_start_plan(
    active_root: str | Path,
    *,
    request_paths: list[str] | tuple[str, ...] | None = None,
    max_lanes: int = 3,
    max_age_seconds: int | None = None,
) -> dict[str, Any]:
    """Build a read-only exact-request start plan for queued spawn dispatch rows.

    This plan inspects queued Domain Weaver spawn-dispatch work requests and
    worker-start readiness. It does not start a queue worker, mark packets, write
    Codex Solo, or settle product state.
    """

    root = _require_active_root(active_root)
    requested_path_filter = {
        _normalize_rel_request_path(root, value)
        for value in (request_paths or [])
        if str(value or "").strip()
    }
    requested_path_filter.discard("")
    max_lane_count = max(0, int(max_lanes))
    queued_rows = _queued_spawn_dispatch_request_rows(root)
    if requested_path_filter:
        queued_rows = [
            row
            for row in queued_rows
            if str(row.get("request_path") or "") in requested_path_filter
        ]
    readiness_kwargs: dict[str, Any] = {}
    if max_age_seconds is not None:
        readiness_kwargs["max_age_seconds"] = int(max_age_seconds)
    readiness = build_domain_weaver_worker_start_readiness(root, **readiness_kwargs)
    readiness_by_path = {
        str(row.get("request_path") or ""): dict(row)
        for row in list(readiness.get("request_results") or [])
        if isinstance(row, Mapping)
    }
    selected_readiness_rows = [
        readiness_by_path[str(row.get("request_path") or "")]
        for row in queued_rows
        if str(row.get("request_path") or "") in readiness_by_path
    ]
    exact_readiness_blockers = sorted(
        {
            str(code)
            for row in selected_readiness_rows
            if not row.get("ready")
            for code in list(row.get("blockers") or [])
            if str(code).strip()
        }
    )
    exact_readiness_summary = {
        "scope": "requested_path_filter" if requested_path_filter else "queued_spawn_dispatch_rows",
        "request_count": len(queued_rows),
        "matched_readiness_request_count": len(selected_readiness_rows),
        "ready_request_count": sum(1 for row in selected_readiness_rows if row.get("ready")),
        "blocked_request_count": sum(1 for row in selected_readiness_rows if not row.get("ready")),
        "blockers": exact_readiness_blockers,
    }

    planned: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    selected_lanes: set[str] = set()
    for row in queued_rows:
        request_path = str(row.get("request_path") or "")
        raw_lane_id = str(row.get("lane_id") or "").strip()
        lane_id = normalize_codex_work_lane_id(raw_lane_id or None)
        blockers: list[str] = []
        if not lane_id:
            blockers.append("lane_id_not_supported")
        elif lane_id not in EXECUTABLE_CODEX_WORK_LANES:
            blockers.append("lane_id_not_executable")
        if max_lane_count <= 0:
            blockers.append("start_plan_lane_cap_zero")
        elif len(selected_lanes) >= max_lane_count and lane_id not in selected_lanes:
            blockers.append("start_plan_lane_cap_exceeded")
        if lane_id and lane_id in selected_lanes:
            blockers.append("same_lane_parallelism_one")

        readiness_row = readiness_by_path.get(request_path)
        if readiness_row is None:
            blockers.append("worker_start_readiness_missing_for_request")
            readiness_summary: dict[str, Any] = {}
        else:
            readiness_summary = _compact_readiness_row(readiness_row)
            if not readiness_row.get("ready"):
                blockers.append("worker_start_readiness_blocked")

        plan_row = {
            "request_path": request_path,
            "request_id": row.get("request_id"),
            "status": row.get("status"),
            "lane_id": lane_id or raw_lane_id or None,
            "raw_lane_id": raw_lane_id or None,
            "domain_id": row.get("domain_id"),
            "agent_role_id": row.get("agent_role_id"),
            "role_tier": row.get("role_tier"),
            "callsign": row.get("callsign"),
            "true_name": row.get("true_name"),
            "source_spawn_request_path": row.get("source_spawn_request_path"),
            "worker_return_is_carrier_intake_only": True,
            "exact_request_path_required": True,
            "start_allowed": not blockers,
            "blockers": list(dict.fromkeys(blockers)),
            "worker_start_readiness": readiness_summary,
            "codex_queue_run_started": False,
            "actual_spawn_performed": False,
        }
        if blockers:
            blocked.append(plan_row)
            continue
        selected_lanes.add(str(lane_id))
        planned.append(plan_row)

    return {
        "schema_id": SPAWN_DISPATCH_START_PLAN_SCHEMA_ID,
        "status": "spawn_dispatch_start_plan_built",
        "created_at": _utc_now(),
        "active_root": str(root),
        "requested_path_filter": sorted(requested_path_filter),
        "queueable_spawn_dispatch_request_count": len(queued_rows),
        "planned_start_count": len(planned),
        "blocked_start_count": len(blocked),
        "max_lanes": max_lane_count,
        "selected_lane_ids": sorted(selected_lanes),
        "candidate_exact_request_paths": [
            str(row.get("request_path") or "") for row in planned
        ],
        "blocked_request_paths": [
            str(row.get("request_path") or "") for row in blocked
        ],
        "start_plan_rows": planned,
        "blocked_rows": blocked,
        "worker_start_readiness_scope": "requested_path_filter" if requested_path_filter else "global_queue",
        "worker_start_readiness_summary": exact_readiness_summary if requested_path_filter else readiness.get("summary"),
        "worker_start_readiness_ok": (
            bool(queued_rows)
            and len(selected_readiness_rows) == len(queued_rows)
            and all(row.get("ready") for row in selected_readiness_rows)
        ) if requested_path_filter else bool(readiness.get("ok")),
        "worker_start_readiness_blockers": exact_readiness_blockers if requested_path_filter else list(readiness.get("blockers") or []),
        "global_worker_start_readiness_summary": readiness.get("summary"),
        "global_worker_start_readiness_ok": bool(readiness.get("ok")),
        "global_worker_start_readiness_blockers": list(readiness.get("blockers") or []),
        "authority": _authority_block(),
        "actual_spawn_performed": False,
        "direct_nested_spawn": False,
        "raw_external_codex_exec": False,
        "codex_solo_write_allowed": False,
        "codex_queue_run_started": False,
        "accepted_state_claimed": False,
        "production_or_live_authority": False,
        "secrets_authority": False,
        "general_queue_processing_allowed": False,
        "next_action": (
            "start_exact_request_paths_after_operator_or_route_gate"
            if planned
            else "repair_spawn_dispatch_start_blockers"
        ),
    }


def validate_spawn_request(
    active_root: str | Path,
    source_path: str | Path,
    request: Mapping[str, Any],
) -> dict[str, Any]:
    """Validate a worker-local spawn request for lead dispatch."""

    root = _require_active_root(active_root)
    path = Path(source_path)
    reasons: list[str] = []

    try:
        relative_path = _relative_posix(root, path)
    except ValueError:
        relative_path = str(path)
        reasons.append("source_path_outside_active_root")

    worker_root = root / WORKER_CONTEXT_RELATIVE_ROOT
    try:
        worker_relative = path.resolve(strict=False).relative_to(
            worker_root.resolve(strict=False)
        )
    except ValueError:
        worker_relative = None
        reasons.append("source_path_outside_worker_context_root")

    if request.get("schema_id") != SPAWN_REQUEST_SCHEMA_ID:
        reasons.append("schema_id_not_worker_spawn_request")
    if request.get("status") != "requested":
        reasons.append("status_not_requested")
    if request.get("kind") != "spawn_request":
        reasons.append("kind_not_spawn_request")

    paths = request.get("paths")
    declared_root = paths.get("active_root") if isinstance(paths, Mapping) else None
    if not declared_root:
        reasons.append("active_root_proof_missing")
    elif Path(str(declared_root)).resolve(strict=False) != root.resolve(strict=False):
        reasons.append("active_root_proof_mismatch")

    parent_worker_id = _required_text(request.get("parent_worker_id"))
    if parent_worker_id is None:
        reasons.append("parent_worker_id_required")
        safe_parent = None
    else:
        try:
            safe_parent = sanitize_worker_id(parent_worker_id)
        except ValueError as exc:
            safe_parent = None
            reasons.append(f"parent_worker_id_invalid:{exc}")
    if safe_parent and safe_parent != parent_worker_id:
        reasons.append("parent_worker_id_not_sanitized")
    if safe_parent and worker_relative is not None and worker_relative.parts:
        if worker_relative.parts[0] != safe_parent:
            reasons.append("parent_worker_id_path_mismatch")
    worker_id = request.get("worker_id")
    if worker_id is not None and safe_parent and str(worker_id) != safe_parent:
        reasons.append("worker_id_parent_mismatch")

    requested_domain = _required_text(request.get("requested_domain"))
    if requested_domain is None:
        reasons.append("requested_domain_required")
    elif "/" in requested_domain or "\\" in requested_domain:
        reasons.append("requested_domain_must_not_contain_path_separators")

    requested_packet = _required_text(request.get("requested_packet"))
    if requested_packet is None:
        reasons.append("requested_packet_required")
    elif "/" in requested_packet or "\\" in requested_packet:
        reasons.append("requested_packet_must_not_contain_path_separators")

    lane_validation = _validate_executable_lane_id(request.get("lane_id"))
    if not lane_validation["ok"]:
        reasons.extend(lane_validation["reasons"])

    if not _present_json_value(request.get("allowed_scope")):
        reasons.append("allowed_scope_required")
    if not _present_json_value(request.get("evidence_requirements")):
        reasons.append("evidence_requirements_required")

    forbidden_actions = request.get("forbidden_actions")
    if not _present_json_value(forbidden_actions):
        reasons.append("forbidden_actions_required")
    else:
        normalized_actions = {_normalize_token(item) for item in _as_list(forbidden_actions)}
        missing_actions = sorted(_REQUIRED_FORBIDDEN_ACTIONS - normalized_actions)
        for action in missing_actions:
            reasons.append(f"forbidden_action_missing:{action}")

    for claim in _forbidden_authority_claims(request):
        reasons.append(f"forbidden_authority_claim:{claim}")
    for text_claim in _forbidden_text_claims(request.get("allowed_scope")):
        reasons.append(f"forbidden_scope_claim:{text_claim}")

    spawn_execution = request.get("spawn_execution")
    if not isinstance(spawn_execution, Mapping):
        reasons.append("spawn_execution_required")
    else:
        if spawn_execution.get("actual_spawn_performed") is not False:
            reasons.append("actual_spawn_performed_must_be_false")
        if spawn_execution.get("lead_fanin_required") is not True:
            reasons.append("lead_fanin_required_must_be_true")
        if spawn_execution.get("queue_mediated_required") is not True:
            reasons.append("queue_mediated_required_must_be_true")
        if spawn_execution.get("raw_external_codex_exec_allowed") is not False:
            reasons.append("raw_external_codex_exec_allowed_must_be_false")
        if spawn_execution.get("direct_nested_subagent_spawn_allowed") is not False:
            reasons.append("direct_nested_subagent_spawn_allowed_must_be_false")

    return {
        "ok": not reasons,
        "source_request_path": relative_path,
        "parent_worker_id": safe_parent,
        "requested_domain": requested_domain,
        "requested_packet": requested_packet,
        "lane_id": lane_validation.get("lane_id"),
        "raw_lane_id": lane_validation.get("raw_lane_id"),
        "reasons": reasons,
    }


def _codex_work_request_args_for_spawn_request(
    root: Path,
    source_path: Path,
    request: Mapping[str, Any],
    *,
    dispatch_candidate: Mapping[str, Any],
    queue_packet_candidate: Mapping[str, Any],
) -> dict[str, Any]:
    source_rel = _relative_posix(root, source_path)
    source_sha = _sha256_file(source_path)
    requested_domain = str(request["requested_domain"])
    requested_packet = str(request["requested_packet"])
    parent_worker_id = str(request["parent_worker_id"])
    role_id = str(request.get("requested_role_id") or request.get("requested_callsign") or "").strip()
    role_tier = str(request.get("requested_role_tier") or "").strip()
    callsign = str(request.get("requested_callsign") or "").strip()
    true_name = str(request.get("requested_true_name") or "").strip()
    work_class = str(request.get("work_class") or "domain_weaver_spawn_dispatch").strip()
    lane_validation = _validate_executable_lane_id(request.get("lane_id"))
    if not lane_validation["ok"]:
        raise ValueError(
            "spawn_dispatch_lane_not_executable:"
            + ",".join(lane_validation["reasons"])
        )
    lane_id = str(lane_validation["lane_id"])
    domain_context_package = str(
        request.get("domain_context_package")
        or "ION/05_context/current/domain_weaver/.ion/ACTIVE_CONTEXT_PACKAGE.md"
    ).strip()
    objective = (
        f"Domain Weaver spawn dispatch for {requested_domain}: {requested_packet} "
        f"requested by worker {parent_worker_id}."
    )
    args: dict[str, Any] = {
        "objective": objective,
        "idempotency_key": _spawn_dispatch_idempotency_key(source_rel, source_sha),
        "client_request_id": f"domain-weaver-spawn-dispatch:{source_sha[:16]}",
        "request_kind": "domain_weaver_spawn_dispatch",
        "work_class": work_class,
        "risk_level": "bounded",
        "route_family": "domain_weaver_larger_fanout_control_plane",
        "lane_id": lane_id,
        "domain_id": requested_domain,
        "domain_context_package": domain_context_package,
        "required_context_reads": _spawn_dispatch_required_context_reads(
            request,
            source_rel=source_rel,
            dispatch_candidate_path=str(dispatch_candidate.get("path") or ""),
            queue_packet_candidate_path=str(queue_packet_candidate.get("path") or ""),
        ),
        "domain_weaver_spawn_dispatch": {
            "schema_id": "ion.domain_weaver.spawn_dispatch_connector_binding.v0_1",
            "source_spawn_request_path": source_rel,
            "source_spawn_request_sha256": source_sha,
            "dispatch_candidate_path": str(dispatch_candidate.get("path") or ""),
            "queue_packet_candidate_path": str(queue_packet_candidate.get("path") or ""),
            "parent_worker_id": parent_worker_id,
            "requested_domain": requested_domain,
            "requested_packet": requested_packet,
            "worker_return_is_carrier_intake_only": True,
            "actual_spawn_performed": False,
            "codex_queue_run_started": False,
        },
    }
    if role_id:
        args["agent_role_id"] = role_id
        args["agent_role"] = role_id
    if role_tier:
        args["role_tier"] = role_tier
    if callsign:
        args["callsign"] = callsign
    if true_name:
        args["true_name"] = true_name
    planned_writes = _safe_string_list(request.get("planned_writes"))
    if planned_writes:
        args["planned_writes"] = planned_writes
    return args


def _spawn_dispatch_required_context_reads(
    request: Mapping[str, Any],
    *,
    source_rel: str,
    dispatch_candidate_path: str,
    queue_packet_candidate_path: str,
) -> list[dict[str, Any]]:
    default_paths = [
        "ION/05_context/current/domain_weaver/AGENTS.md",
        "ION/05_context/current/domain_weaver/.ion/ION_CONTEXT_CAPSULE.yaml",
        "ION/05_context/current/domain_weaver/.ion/ACTIVE_CONTEXT_PACKAGE.md",
        "ION/05_context/current/domain_weaver/larger_fanout/DOMAIN_WEAVER_LARGER_FANOUT_CONTROL_READINESS.latest.md",
        source_rel,
        dispatch_candidate_path,
        queue_packet_candidate_path,
    ]
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in default_paths:
        if path and path not in seen:
            seen.add(path)
            rows.append({"kind": "file", "path": path, "required": True})
    for item in _as_list(request.get("required_context_reads")):
        if isinstance(item, Mapping):
            path = str(item.get("path") or "").strip()
            kind = str(item.get("kind") or "file").strip() or "file"
            required = bool(item.get("required", True))
        else:
            path = str(item or "").strip()
            kind = "file"
            required = True
        if path and path not in seen:
            seen.add(path)
            rows.append({"kind": kind, "path": path, "required": required})
    return rows[:64]


def _spawn_dispatch_idempotency_key(source_rel: str, source_sha: str) -> str:
    return f"domain-weaver-spawn-dispatch-{hashlib.sha256((source_rel + source_sha).encode('utf-8')).hexdigest()[:24]}"


def _validate_executable_lane_id(value: Any) -> dict[str, Any]:
    raw_lane_id = str(value or "").strip()
    reasons: list[str] = []
    lane_id: str | None = None
    if not raw_lane_id:
        reasons.append("lane_id_required_for_spawn_dispatch")
    else:
        lane_id = normalize_codex_work_lane_id(raw_lane_id)
        if not lane_id:
            reasons.append(f"lane_id_not_supported:{raw_lane_id}")
        elif lane_id not in EXECUTABLE_CODEX_WORK_LANES:
            reasons.append(f"lane_id_not_executable:{lane_id}")
    return {
        "ok": not reasons,
        "raw_lane_id": raw_lane_id or None,
        "lane_id": lane_id,
        "executable_lane_ids": list(EXECUTABLE_CODEX_WORK_LANES),
        "reasons": reasons,
    }


def _queued_spawn_dispatch_request_rows(root: Path) -> list[dict[str, Any]]:
    request_dir = root / CODEX_WORK_REQUESTS_RELATIVE_ROOT
    if not request_dir.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(request_dir.glob("*.json")):
        payload = _read_json(path)
        if not isinstance(payload, Mapping):
            continue
        if str(payload.get("status") or "").strip() != QUEUEABLE_FOR_CODEX_STATUS:
            continue
        spawn_binding = payload.get("domain_weaver_spawn_dispatch")
        if not isinstance(spawn_binding, Mapping):
            continue
        rows.append(
            {
                "request_path": _relative_posix(root, path),
                "request_id": payload.get("request_id"),
                "status": payload.get("status"),
                "lane_id": payload.get("lane_id"),
                "domain_id": payload.get("domain_id"),
                "agent_role_id": payload.get("agent_role_id") or payload.get("agent_role"),
                "role_tier": payload.get("role_tier"),
                "callsign": payload.get("callsign"),
                "true_name": payload.get("true_name"),
                "source_spawn_request_path": spawn_binding.get("source_spawn_request_path"),
                "source_spawn_request_sha256": spawn_binding.get("source_spawn_request_sha256"),
                "dispatch_candidate_path": spawn_binding.get("dispatch_candidate_path"),
                "queue_packet_candidate_path": spawn_binding.get("queue_packet_candidate_path"),
                "worker_return_is_carrier_intake_only": bool(
                    spawn_binding.get("worker_return_is_carrier_intake_only")
                ),
                "payload": dict(payload),
            }
        )
    return rows


def _normalize_rel_request_path(root: Path, value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    path = Path(text)
    if not path.is_absolute():
        path = root / path
    try:
        return _relative_posix(root, path)
    except ValueError:
        return ""


def _compact_readiness_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ready": bool(row.get("ready")),
        "active_context_ready": bool(row.get("active_context_ready")),
        "queueable_for_start": bool(row.get("queueable_for_start")),
        "active_context_check_status": row.get("active_context_check_status"),
        "blockers": list(row.get("blockers") or []),
        "next_action": row.get("next_action"),
        "selected_mount_id": row.get("selected_mount_id"),
        "capsule_identity_blockers": list(row.get("capsule_identity_blockers") or []),
        "worker_return_status": row.get("worker_return_status"),
    }


def _write_dispatch_enqueue_receipt(
    root: Path,
    source_path: Path,
    request: Mapping[str, Any],
    *,
    dispatch_candidate: Mapping[str, Any],
    queue_packet_candidate: Mapping[str, Any],
    connector_args: Mapping[str, Any],
    connector_result: Mapping[str, Any],
    dispatcher_id: str,
    run_key: str,
) -> dict[str, Any]:
    source_rel = _relative_posix(root, source_path)
    path = _dispatch_path(
        root,
        run_key=run_key,
        parent_worker_id=str(request.get("parent_worker_id") or "unknown-worker"),
        requested_domain=str(request.get("requested_domain") or "unknown-domain"),
        source_rel=source_rel,
        suffix=".dispatch_enqueue_receipt.json",
    )
    data = connector_result.get("data") if isinstance(connector_result.get("data"), Mapping) else {}
    ok = bool(connector_result.get("ok"))
    receipt = {
        "schema_id": DISPATCH_ENQUEUE_RECEIPT_SCHEMA_ID,
        "status": "spawn_dispatch_enqueued" if ok else "spawn_dispatch_enqueue_blocked",
        "created_at": _utc_now(),
        "dispatcher_id": str(dispatcher_id),
        "source_request_path": source_rel,
        "source_request_sha256": _sha256_file(source_path),
        "source_dispatch_candidate_path": str(dispatch_candidate.get("path") or ""),
        "source_queue_packet_candidate_path": str(queue_packet_candidate.get("path") or ""),
        "parent_worker_id": request.get("parent_worker_id"),
        "requested_domain": request.get("requested_domain"),
        "requested_packet": request.get("requested_packet"),
        "connector_tool": "ion_request_codex_work_packet",
        "connector_ok": ok,
        "connector_finding": connector_result.get("finding"),
        "connector_request_id": data.get("request_id"),
        "connector_packet_path": data.get("packet_path"),
        "connector_idempotent_replay": bool(data.get("idempotent_replay")),
        "connector_duplicate_prevented": bool(data.get("duplicate_prevented")),
        "connector_dedupe_key": data.get("dedupe_key") or connector_args.get("idempotency_key"),
        "domain_weaver_spawn_dispatch": connector_args.get("domain_weaver_spawn_dispatch"),
        "authority": _authority_block(),
        "worker_return_is_carrier_intake_only": True,
        "actual_spawn_performed": False,
        "direct_nested_spawn": False,
        "raw_external_codex_exec": False,
        "codex_solo_write_allowed": False,
        "codex_work_request_written": ok,
        "codex_queue_run_started": False,
        "worker_start_allowed": False,
        "accepted_state_claimed": False,
        "production_or_live_authority": False,
        "secrets_authority": False,
        "registry_or_materialization_movement": False,
        "path": _relative_posix(root, path),
    }
    _write_json(path, receipt)
    return receipt


def spawn_dispatch_enqueue_succeeded(receipt: Mapping[str, Any]) -> bool:
    return (
        str(receipt.get("status") or "") == "spawn_dispatch_enqueued"
        and receipt.get("connector_ok") is True
        and receipt.get("codex_work_request_written") is True
        and bool(str(receipt.get("connector_packet_path") or "").strip())
    )


def spawn_dispatch_enqueue_blockers(receipt: Mapping[str, Any]) -> list[str]:
    if spawn_dispatch_enqueue_succeeded(receipt):
        return []
    blockers: list[str] = ["spawn_dispatch_enqueue_blocked"]
    if receipt.get("connector_ok") is not True:
        finding = str(receipt.get("connector_finding") or "").strip()
        blockers.append(f"connector_not_ok:{finding}" if finding else "connector_not_ok")
    if receipt.get("codex_work_request_written") is not True:
        blockers.append("codex_work_request_not_written")
    if not str(receipt.get("connector_packet_path") or "").strip():
        blockers.append("connector_packet_path_missing")
    return list(dict.fromkeys(blockers))


def build_spawn_dispatch_legacy_receipt_quarantine(
    active_root: str | Path,
    *,
    artifact_paths: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Read historical fanout artifacts and quarantine false enqueue claims.

    Older artifacts may have embedded blocked connector receipts inside an
    ``enqueue_receipts`` list. This read-only classifier recomputes enqueue
    proof from each receipt's own fields, so status surfaces can ignore stale
    blocked-as-enqueued evidence without rewriting history.
    """

    root = _require_active_root(active_root)
    selected_paths = _legacy_quarantine_artifact_paths(root, artifact_paths)
    inspected: list[dict[str, Any]] = []
    receipt_rows: list[dict[str, Any]] = []
    missing_paths: list[str] = []
    for artifact_path in selected_paths:
        rel_artifact = _relative_posix(root, artifact_path)
        if not artifact_path.is_file():
            missing_paths.append(rel_artifact)
            continue
        payload = _read_json(artifact_path)
        inspected.append(
            {
                "artifact_path": rel_artifact,
                "artifact_sha256": _sha256_file(artifact_path),
            }
        )
        receipt_rows.extend(
            _embedded_dispatch_enqueue_receipts(
                root,
                payload,
                artifact_path=rel_artifact,
                pointer="",
            )
        )

    verified_enqueue_rows: list[dict[str, Any]] = []
    blocked_rows: list[dict[str, Any]] = []
    quarantine_rows: list[dict[str, Any]] = []
    connector_packet_written_only_rows: list[dict[str, Any]] = []
    for row in receipt_rows:
        receipt = row["receipt"]
        blockers = spawn_dispatch_enqueue_blockers(receipt)
        status = str(receipt.get("status") or "")
        claimed_as_enqueued = bool(row.get("claimed_as_enqueued"))
        verified = spawn_dispatch_enqueue_succeeded(receipt)
        entry = {
            "artifact_path": row["artifact_path"],
            "json_pointer": row["json_pointer"],
            "receipt_path": row.get("receipt_path"),
            "source_request_path": receipt.get("source_request_path"),
            "status": status,
            "connector_ok": receipt.get("connector_ok"),
            "codex_work_request_written": receipt.get("codex_work_request_written"),
            "connector_packet_path": receipt.get("connector_packet_path"),
            "claimed_as_enqueued_by_container": claimed_as_enqueued,
            "verified_enqueue": verified,
            "enqueue_blockers": blockers,
            "count_as_enqueued": verified,
            "worker_start_allowed": False,
            "codex_queue_run_started": False,
            "actual_spawn_performed": False,
        }
        if verified:
            verified_enqueue_rows.append(entry)
            connector_packet_written_only_rows.append(
                {
                    "path": entry.get("receipt_path"),
                    "connector_packet_path": entry.get("connector_packet_path"),
                    "label": "connector_packet_written_only",
                    "must_not_count_as": [
                        "worker_started",
                        "live_agent",
                        "accepted_state",
                        "queue_execution",
                        "automatic_agent_reaction",
                    ],
                }
            )
            continue
        blocked_rows.append(entry)
        if claimed_as_enqueued:
            quarantine_rows.append(
                {
                    **entry,
                    "quarantine_reason": "blocked_receipt_listed_under_enqueue_receipts",
                    "quarantined_from_enqueue_proof": True,
                    "ui_count_as_enqueued": False,
                    "projection_count_as_enqueued": False,
                }
            )

    return {
        "schema_id": LEGACY_RECEIPT_QUARANTINE_SCHEMA_ID,
        "status": "spawn_dispatch_legacy_receipt_quarantine_built",
        "created_at": _utc_now(),
        "active_root": str(root),
        "source_wave_id": "DW-SPW-002",
        "quarantine_mode": "label_only_no_move_no_delete",
        "artifact_paths": [_relative_posix(root, path) for path in selected_paths],
        "missing_artifact_paths": missing_paths,
        "artifacts_inspected": inspected,
        "embedded_receipt_count": len(receipt_rows),
        "claimed_enqueue_receipt_count": sum(
            1 for row in receipt_rows if row.get("claimed_as_enqueued")
        ),
        "verified_enqueue_receipt_count": len(verified_enqueue_rows),
        "blocked_receipt_count": len(blocked_rows),
        "quarantined_false_enqueue_count": len(quarantine_rows),
        "legacy_false_enqueue_detected": bool(quarantine_rows),
        "verified_enqueue_receipt_paths": _unique_nonempty(
            row.get("receipt_path") for row in verified_enqueue_rows
        ),
        "quarantined_receipt_paths": _unique_nonempty(
            row.get("receipt_path") for row in quarantine_rows
        ),
        "blocked_receipt_paths": _unique_nonempty(
            row.get("receipt_path") for row in blocked_rows
        ),
        "quarantined_fields": _legacy_quarantined_fields(root, selected_paths),
        "quarantined_paths": connector_packet_written_only_rows
        + [
            {
                "path": row.get("receipt_path"),
                "label": "blocked_receipt_must_not_count_as_enqueued",
                "must_not_count_as": [
                    "enqueued",
                    "worker_started",
                    "live_agent",
                    "accepted_state",
                    "queue_execution",
                    "automatic_agent_reaction",
                ],
            }
            for row in quarantine_rows
        ],
        "canonical_truth_fields": {
            "actual_spawn_performed": False,
            "codex_queue_run_started": False,
            "worker_start_allowed": False,
        },
        "superseding_evidence": [
            "ION/05_context/current/domain_weaver/acceleration/DW_SWARM_002_PRESSURE_WAVE_FANIN.latest.json",
            "ION/05_context/current/domain_weaver/acceleration/DW_SWARM_002_BATCH_B_FANIN.latest.json",
        ],
        "verified_enqueue_rows": verified_enqueue_rows,
        "blocked_rows": blocked_rows,
        "quarantine_rows": quarantine_rows,
        "proof_gate": {
            "status": "legacy_enqueue_claims_recomputed",
            "legacy_false_enqueue_detected": bool(quarantine_rows),
            "count_enqueued_from_verified_receipts_only": True,
            "blocked_receipts_count_as_enqueued": False,
            "dispatch_enqueue_receipt_with_connector_ok_false_counts_as_enqueued": False,
            "safe_enqueue_receipt_paths": _unique_nonempty(
                row.get("receipt_path") for row in verified_enqueue_rows
            ),
            "quarantined_false_enqueue_receipt_paths": _unique_nonempty(
                row.get("receipt_path") for row in quarantine_rows
            ),
        },
        "non_claims": [
            "historical artifacts are not rewritten",
            "quarantine does not start workers",
            "dispatch enqueue receipts do not prove worker start",
            "blocked connector receipts do not count as enqueued",
            "candidate quarantine is not accepted-state movement",
        ],
        "authority": _authority_block(),
        "actual_spawn_performed": False,
        "codex_queue_run_started": False,
        "worker_start_allowed": False,
        "accepted_state_claimed": False,
        "production_or_live_authority": False,
        "secrets_authority": False,
    }


def render_spawn_dispatch_legacy_receipt_quarantine(payload: Mapping[str, Any]) -> str:
    """Render a compact operator report for stale false-enqueue quarantine."""

    lines = [
        "# Spawn Dispatch Legacy Receipt Quarantine",
        "",
        f"Generated: `{payload.get('created_at')}`",
        "",
        "Authority: candidate-only. This report is read-only; it does not rewrite historical receipts, start workers, process queues, or move accepted state.",
        "",
        "## Summary",
        "",
        f"- embedded receipts: `{payload.get('embedded_receipt_count')}`",
        f"- claimed enqueue receipts: `{payload.get('claimed_enqueue_receipt_count')}`",
        f"- verified enqueue receipts: `{payload.get('verified_enqueue_receipt_count')}`",
        f"- blocked receipts: `{payload.get('blocked_receipt_count')}`",
        f"- quarantined false-enqueue receipts: `{payload.get('quarantined_false_enqueue_count')}`",
        f"- legacy false enqueue detected: `{payload.get('legacy_false_enqueue_detected')}`",
        "",
        "## Quarantined Receipts",
        "",
    ]
    rows = payload.get("quarantine_rows") if isinstance(payload.get("quarantine_rows"), list) else []
    if rows:
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            blockers = ", ".join(str(item) for item in row.get("enqueue_blockers", [])) or "none"
            lines.append(
                f"- `{row.get('receipt_path')}` from `{row.get('artifact_path')}` at "
                f"`{row.get('json_pointer')}`: `{row.get('quarantine_reason')}`; blockers `{blockers}`"
            )
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Safe Enqueue Receipt Paths",
            "",
        ]
    )
    safe_paths = payload.get("verified_enqueue_receipt_paths")
    if isinstance(safe_paths, list) and safe_paths:
        for path in safe_paths:
            lines.append(f"- `{path}`")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
        ]
    )
    for claim in payload.get("non_claims", []):
        lines.append(f"- {claim}")
    lines.append("")
    return "\n".join(lines)


def _write_dispatch_candidate(
    root: Path,
    source_path: Path,
    request: Mapping[str, Any],
    *,
    dispatcher_id: str,
    run_key: str,
) -> dict[str, Any]:
    source_rel = _relative_posix(root, source_path)
    source_sha = _sha256_file(source_path)
    parent_worker_id = str(request["parent_worker_id"])
    requested_domain = str(request["requested_domain"])
    requested_packet = str(request["requested_packet"])
    path = _dispatch_path(
        root,
        run_key=run_key,
        parent_worker_id=parent_worker_id,
        requested_domain=requested_domain,
        source_rel=source_rel,
        suffix=".dispatch_candidate.json",
    )
    queue_packet_candidate_path = _dispatch_path(
        root,
        run_key=run_key,
        parent_worker_id=parent_worker_id,
        requested_domain=requested_domain,
        source_rel=source_rel,
        suffix=".queue_packet_candidate.json",
    )
    queue_packet_candidate_ref = _relative_posix(root, queue_packet_candidate_path)
    candidate: dict[str, Any] = {
        "schema_id": DISPATCH_CANDIDATE_SCHEMA_ID,
        "status": "dispatch_candidate",
        "created_at": _utc_now(),
        "dispatcher_id": str(dispatcher_id),
        "source_request_path": source_rel,
        "source_request_sha256": source_sha,
        "parent_worker_id": parent_worker_id,
        "requested_domain": requested_domain,
        "requested_packet": requested_packet,
        "requested_callsign": request.get("requested_callsign"),
        "requested_true_name": request.get("requested_true_name"),
        "allowed_scope": request.get("allowed_scope"),
        "forbidden_actions": request.get("forbidden_actions"),
        "evidence_requirements": request.get("evidence_requirements"),
        "bounded_dispatch_packet": {
            "status": "dispatch_ready_after_lead_fanin",
            "packet_id": requested_packet,
            "domain_id": requested_domain,
            "parent_worker_id": parent_worker_id,
            "allowed_scope": request.get("allowed_scope"),
            "forbidden_actions": request.get("forbidden_actions"),
            "evidence_requirements": request.get("evidence_requirements"),
            "worker_return_is_carrier_intake_only": True,
            "queue_packet_candidate_ref": queue_packet_candidate_ref,
        },
        "queue_packet_candidate_ref": queue_packet_candidate_ref,
        "authority": _authority_block(),
        "lead_fanin_required": True,
        "queue_mediated_required": True,
        "actual_spawn_performed": False,
        "direct_nested_spawn": False,
        "raw_external_codex_exec": False,
        "codex_solo_write_allowed": False,
        "live_queue_state_mutated": False,
        "codex_work_request_written": False,
        "codex_queue_run_started": False,
        "path": _relative_posix(root, path),
    }
    _write_json(path, candidate)
    return candidate


def _write_queue_packet_candidate(
    root: Path,
    source_path: Path,
    request: Mapping[str, Any],
    *,
    dispatch_candidate: Mapping[str, Any],
    dispatcher_id: str,
    run_key: str,
) -> dict[str, Any]:
    source_rel = _relative_posix(root, source_path)
    source_sha = _sha256_file(source_path)
    parent_worker_id = str(request["parent_worker_id"])
    requested_domain = str(request["requested_domain"])
    requested_packet = str(request["requested_packet"])
    path = _dispatch_path(
        root,
        run_key=run_key,
        parent_worker_id=parent_worker_id,
        requested_domain=requested_domain,
        source_rel=source_rel,
        suffix=".queue_packet_candidate.json",
    )
    path_rel = _relative_posix(root, path)
    dispatch_candidate_path = str(dispatch_candidate.get("path") or "")
    bounded_work_packet = {
        "schema_id": CODEX_WORK_PACKET_REQUEST_CANDIDATE_SCHEMA_ID,
        "status": "candidate_only_not_queued",
        "template_id": "CODEX_SOLO_WORK_UNIT",
        "packet_id": requested_packet,
        "domain_id": requested_domain,
        "parent_worker_id": parent_worker_id,
        "requested_callsign": request.get("requested_callsign"),
        "requested_true_name": request.get("requested_true_name"),
        "allowed_scope": request.get("allowed_scope"),
        "forbidden_actions": request.get("forbidden_actions"),
        "evidence_requirements": request.get("evidence_requirements"),
        "source_spawn_request_path": source_rel,
        "source_dispatch_candidate_path": dispatch_candidate_path,
        "candidate_artifact_path": path_rel,
        "candidate_only": True,
        "lead_fanin_required": True,
        "queue_mediated_required": True,
        "worker_return_is_carrier_intake_only": True,
        "actual_spawn_performed": False,
        "direct_nested_spawn": False,
        "raw_external_codex_exec": False,
        "live_queue_state_mutated": False,
        "codex_work_request_written": False,
        "codex_queue_run_started": False,
        "codex_solo_write_allowed": False,
        "accepted_state_claimed": False,
        "production_or_live_authority": False,
        "secrets_authority": False,
        "registry_or_materialization_movement": False,
    }
    candidate = {
        "schema_id": QUEUE_PACKET_CANDIDATE_SCHEMA_ID,
        "status": "queue_packet_candidate",
        "created_at": _utc_now(),
        "dispatcher_id": str(dispatcher_id),
        "source_request_path": source_rel,
        "source_request_sha256": source_sha,
        "source_dispatch_candidate_path": dispatch_candidate_path,
        "parent_worker_id": parent_worker_id,
        "requested_domain": requested_domain,
        "requested_packet": requested_packet,
        "requested_callsign": request.get("requested_callsign"),
        "requested_true_name": request.get("requested_true_name"),
        "bounded_codex_work_packet_request": bounded_work_packet,
        "authority": _authority_block(),
        "candidate_artifact_only": True,
        "lead_fanin_required": True,
        "queue_mediated_required": True,
        "actual_spawn_performed": False,
        "direct_nested_spawn": False,
        "raw_external_codex_exec": False,
        "live_queue_state_mutated": False,
        "codex_work_request_written": False,
        "codex_queue_run_started": False,
        "codex_solo_write_allowed": False,
        "path": path_rel,
    }
    _write_json(path, candidate)
    return candidate


def _write_dispatch_rejection(
    root: Path,
    source_path: Path,
    request: Mapping[str, Any],
    reasons: list[str],
    *,
    dispatcher_id: str,
    run_key: str,
) -> dict[str, Any]:
    source_rel = _relative_posix(root, source_path)
    source_sha = _sha256_file(source_path)
    parent_worker_id = str(request.get("parent_worker_id") or "unknown-worker")
    requested_domain = str(request.get("requested_domain") or "unknown-domain")
    path = _dispatch_path(
        root,
        run_key=run_key,
        parent_worker_id=parent_worker_id,
        requested_domain=requested_domain,
        source_rel=source_rel,
        suffix=".dispatch_rejected.json",
    )
    rejection = {
        "schema_id": DISPATCH_REJECTION_SCHEMA_ID,
        "status": "dispatch_rejected",
        "created_at": _utc_now(),
        "dispatcher_id": str(dispatcher_id),
        "source_request_path": source_rel,
        "source_request_sha256": source_sha,
        "parent_worker_id": request.get("parent_worker_id"),
        "requested_domain": request.get("requested_domain"),
        "requested_packet": request.get("requested_packet"),
        "reasons": list(reasons),
        "authority": _authority_block(),
        "lead_fanin_required": True,
        "actual_spawn_performed": False,
        "direct_nested_spawn": False,
        "raw_external_codex_exec": False,
        "path": _relative_posix(root, path),
    }
    _write_json(path, rejection)
    return rejection


def _mark_request(
    source_path: Path,
    request: Mapping[str, Any],
    *,
    status: str,
    dispatcher_id: str,
    dispatch_ref: str,
    validation: Mapping[str, Any],
) -> None:
    updated = dict(request)
    updated["status"] = status
    updated["dispatcher_consumption"] = {
        "status": status,
        "consumed_at": _utc_now(),
        "dispatcher_id": str(dispatcher_id),
        "dispatch_ref": dispatch_ref,
        "validation_ok": bool(validation.get("ok")),
        "validation_reasons": list(validation.get("reasons") or []),
        "source_deleted": False,
    }
    _write_json(source_path, updated)


def _dispatch_path(
    root: Path,
    *,
    run_key: str,
    parent_worker_id: str,
    requested_domain: str,
    source_rel: str,
    suffix: str,
) -> Path:
    dispatch_dir = root / SPAWN_DISPATCH_RELATIVE_ROOT
    dispatch_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(source_rel.encode("utf-8")).hexdigest()[:12]
    safe_parent = _safe_fragment(parent_worker_id)
    safe_domain = _safe_fragment(requested_domain)
    return dispatch_dir / f"{run_key}_{safe_parent}_{safe_domain}_{digest}{suffix}"


def _require_active_root(active_root: str | Path) -> Path:
    root = Path(active_root).expanduser().resolve(strict=False)
    if not (root / "pyproject.toml").is_file():
        raise ValueError("active_root_missing_pyproject")
    if not (root / "ION/REPO_AUTHORITY.md").is_file():
        raise ValueError("active_root_missing_repo_authority")
    return root


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _relative_posix(root: Path, path: Path) -> str:
    return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safe_fragment(value: str) -> str:
    fragment = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "")).strip("._-").lower()
    return fragment or "unknown"


def _required_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _present_json_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return list(value)
    return [value]


def _safe_string_list(value: Any) -> list[str]:
    items: list[str] = []
    seen: set[str] = set()
    for item in _as_list(value):
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        items.append(text)
    return items[:64]


def _legacy_quarantine_artifact_paths(
    root: Path,
    artifact_paths: list[str] | tuple[str, ...] | None,
) -> list[Path]:
    raw_paths = list(artifact_paths or [])
    if not raw_paths:
        raw_paths = [path.as_posix() for path in DEFAULT_LEGACY_RECEIPT_QUARANTINE_ARTIFACTS]
    paths: list[Path] = []
    seen: set[str] = set()
    for raw in raw_paths:
        text = str(raw or "").strip()
        if not text:
            continue
        path = Path(text)
        if not path.is_absolute():
            path = root / path
        try:
            rel = _relative_posix(root, path)
        except ValueError:
            continue
        if rel in seen:
            continue
        seen.add(rel)
        paths.append(path)
    return paths


def _legacy_quarantined_fields(root: Path, artifact_paths: list[Path]) -> list[dict[str, Any]]:
    field_specs = [
        (
            "/enqueue_result/proof_gate/enqueued",
            "stale_false_enqueue_count",
            "connector receipts only; recompute enqueue proof from receipt predicate",
        ),
        (
            "/enqueue_result/proof_gate/enqueue_receipt_paths",
            "stale_as_enqueue_or_start_proof",
            "receipt references only; blocked receipts must be excluded from enqueue proof",
        ),
        (
            "/enqueue_result/status",
            "connector_run_completion_only",
            "dispatch enqueue run completion does not prove all embedded receipts enqueued",
        ),
        (
            "/enqueue_result/enqueue_receipts",
            "legacy_mixed_receipt_container",
            "container may include blocked connector receipts; recompute each receipt independently",
        ),
        (
            "/start_plan_route/delegated_result/blocked_rows",
            "blocked_durable_requests_not_runnable_workers",
            "blocked QUEUED_FOR_CODEX_CARRIER rows are exact-path candidates only",
        ),
        (
            "/actual_spawn_performed",
            "canonical_truth_field",
            "must remain false",
        ),
        (
            "/codex_queue_run_started",
            "canonical_truth_field",
            "must remain false",
        ),
        (
            "/worker_start_allowed",
            "canonical_truth_field",
            "must remain false",
        ),
    ]
    rows: list[dict[str, Any]] = []
    for artifact_path in artifact_paths:
        if not artifact_path.is_file():
            continue
        payload = _read_json(artifact_path)
        rel_artifact = _relative_posix(root, artifact_path)
        for pointer, label, interpretation in field_specs:
            found, observed = _json_pointer_get(payload, pointer)
            if not found:
                continue
            rows.append(
                {
                    "path": rel_artifact,
                    "json_pointer": pointer,
                    "observed_value": observed,
                    "label": label,
                    "correct_interpretation": interpretation,
                }
            )
    return rows


def _json_pointer_get(value: Any, pointer: str) -> tuple[bool, Any]:
    if pointer == "":
        return True, value
    current = value
    for raw_part in pointer.split("/")[1:]:
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, Mapping):
            if part not in current:
                return False, None
            current = current[part]
        elif isinstance(current, list):
            try:
                index = int(part)
            except ValueError:
                return False, None
            if index < 0 or index >= len(current):
                return False, None
            current = current[index]
        else:
            return False, None
    return True, current


def _embedded_dispatch_enqueue_receipts(
    root: Path,
    value: Any,
    *,
    artifact_path: str,
    pointer: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(value, Mapping):
        if _looks_like_dispatch_enqueue_receipt(value):
            receipt = _resolve_receipt_payload(root, value)
            rows.append(
                {
                    "artifact_path": artifact_path,
                    "json_pointer": pointer or "/",
                    "receipt_path": _receipt_path(value),
                    "claimed_as_enqueued": _pointer_has_segment(pointer, "enqueue_receipts"),
                    "receipt": receipt,
                }
            )
            return rows
        for key, nested in value.items():
            rows.extend(
                _embedded_dispatch_enqueue_receipts(
                    root,
                    nested,
                    artifact_path=artifact_path,
                    pointer=f"{pointer}/{_json_pointer_token(str(key))}",
                )
            )
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            rows.extend(
                _embedded_dispatch_enqueue_receipts(
                    root,
                    nested,
                    artifact_path=artifact_path,
                    pointer=f"{pointer}/{index}",
                )
            )
    return rows


def _looks_like_dispatch_enqueue_receipt(value: Mapping[str, Any]) -> bool:
    if value.get("schema_id") == DISPATCH_ENQUEUE_RECEIPT_SCHEMA_ID:
        return True
    status = str(value.get("status") or "")
    return status in {"spawn_dispatch_enqueued", "spawn_dispatch_enqueue_blocked"} and (
        "connector_ok" in value or "connector_packet_path" in value
    )


def _resolve_receipt_payload(root: Path, value: Mapping[str, Any]) -> dict[str, Any]:
    receipt = dict(value)
    path_text = _receipt_path(value)
    if not path_text:
        return receipt
    path = Path(path_text)
    if not path.is_absolute():
        path = root / path
    try:
        _relative_posix(root, path)
    except ValueError:
        return receipt
    actual = _read_json(path)
    if isinstance(actual, Mapping) and _looks_like_dispatch_enqueue_receipt(actual):
        return dict(actual)
    return receipt


def _receipt_path(value: Mapping[str, Any]) -> str | None:
    text = str(value.get("path") or "").strip()
    return text or None


def _pointer_has_segment(pointer: str, segment: str) -> bool:
    return segment in [part for part in pointer.split("/") if part]


def _json_pointer_token(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _unique_nonempty(values: Any) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def _normalize_token(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")


def _forbidden_authority_claims(value: Any, *, prefix: str = "") -> list[str]:
    claims: list[str] = []
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            key_path = f"{prefix}.{key_text}" if prefix else key_text
            if _normalize_token(key_text) in _FORBIDDEN_AUTHORITY_KEYS and bool(nested):
                claims.append(key_path)
            claims.extend(_forbidden_authority_claims(nested, prefix=key_path))
    elif isinstance(value, list):
        for idx, nested in enumerate(value):
            claims.extend(_forbidden_authority_claims(nested, prefix=f"{prefix}[{idx}]"))
    return claims


def _forbidden_text_claims(value: Any) -> list[str]:
    claims: list[str] = []
    for item in _flatten_json_values(value):
        if not isinstance(item, str):
            continue
        lowered = item.strip().lower()
        for marker in _FORBIDDEN_TEXT_CLAIM_MARKERS:
            if marker in lowered:
                claims.append(marker)
    return sorted(set(claims))


def _flatten_json_values(value: Any) -> list[Any]:
    if isinstance(value, Mapping):
        items: list[Any] = []
        for nested in value.values():
            items.extend(_flatten_json_values(nested))
        return items
    if isinstance(value, list):
        items = []
        for nested in value:
            items.extend(_flatten_json_values(nested))
        return items
    return [value]


def _authority_block() -> dict[str, bool]:
    return {
        "accepted_state": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "registry_movement": False,
        "materialization_movement": False,
        "codex_solo_write_allowed": False,
        "carrier_intake_only": True,
    }
