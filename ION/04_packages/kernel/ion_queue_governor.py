"""Reusable queue currentness and lane-governance projection.

This module classifies queue freshness, terminal repair debt, duplicate
pressure, active-run posture, and lane projection health. It is read-only and
does not claim, reorder, delete, or accept queue state.
"""
from __future__ import annotations

import json
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

SCHEMA_ID = "ion.queue_governor.projection.v0_1"
DOGFOOD_SCHEMA_ID = "ion.queue_governor.dogfood_projection.v0_1"
DEFAULT_CODEX_WORK_QUEUE_PATH = Path("ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json")
DEFAULT_CODEX_QUEUE_RUNNER_STATE_PATH = Path("ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json")
DEFAULT_CODEX_WORK_LANE_INDEX_PATH = Path("ION/05_context/current/chatgpt_connector/work_lanes/INDEX.json")
DEFAULT_CODEX_WORK_REQUESTS_DIR = Path("ION/05_context/current/chatgpt_connector/codex_work_requests")
QUEUE_STALE_AFTER_SECONDS = 24 * 60 * 60


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    return candidate


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _read_json_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


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


def queue_lane_for_request(request: Mapping[str, Any]) -> str:
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


def classify_queue_request(
    request: Mapping[str, Any],
    *,
    now: datetime | None = None,
    stale_after_seconds: int = QUEUE_STALE_AFTER_SECONDS,
) -> dict[str, Any]:
    current_time = now or datetime.now(timezone.utc)
    status = str(request.get("status") or "UNKNOWN")
    created = _parse_time(request.get("created_at"))
    updated = _parse_time(request.get("updated_at")) or created
    age_seconds = int((current_time - created).total_seconds()) if created else None
    lane_id = queue_lane_for_request(request)
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


def actionable_duplicate_group_count(rows: list[Mapping[str, Any]]) -> int:
    groups: dict[str, int] = {}
    for row in rows:
        if not _is_actionable_duplicate_candidate(row):
            continue
        key = str(row.get("dedupe_key") or row.get("objective_sha256") or "").strip()
        if key:
            groups[key] = groups.get(key, 0) + 1
    return sum(1 for count in groups.values() if count > 1)


def duplicate_group_count(rows: list[Mapping[str, Any]]) -> int:
    groups: dict[str, int] = {}
    for row in rows:
        key = str(row.get("dedupe_key") or row.get("objective_sha256") or "").strip()
        if key:
            groups[key] = groups.get(key, 0) + 1
    return sum(1 for count in groups.values() if count > 1)


def work_request_file_rows(
    root: str | Path | None = None,
    *,
    requests_dir: Path = DEFAULT_CODEX_WORK_REQUESTS_DIR,
) -> list[dict[str, Any]]:
    shell_root = _resolve_root(root)
    request_root = shell_root / requests_dir
    if not request_root.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(request_root.glob("*.json")):
        payload = _read_json_file(path)
        if not payload:
            continue
        row = dict(payload)
        try:
            rel_path = path.relative_to(shell_root).as_posix()
        except ValueError:
            rel_path = path.as_posix()
        row.setdefault("path", rel_path)
        objective = str(row.get("objective") or "")
        if objective and not row.get("objective_sha256"):
            row["objective_sha256"] = hashlib.sha256(objective.encode("utf-8")).hexdigest()
        rows.append(row)
    return rows


def active_run_entries_from_state(runner_state: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    entries: list[Mapping[str, Any]] = []
    active_runs_raw = runner_state.get("active_runs")
    if isinstance(active_runs_raw, Mapping):
        entries.extend(row for row in active_runs_raw.values() if isinstance(row, Mapping))
    elif isinstance(active_runs_raw, list):
        entries.extend(row for row in active_runs_raw if isinstance(row, Mapping))
    active_run = _as_mapping(runner_state.get("active_run"))
    active_run_id = str(active_run.get("run_id") or "")
    if active_run and not any(str(row.get("run_id") or "") == active_run_id for row in entries):
        entries.append(active_run)
    return entries


def worker_concurrency_ready(runner_state: Mapping[str, Any]) -> bool:
    concurrency = _as_mapping(runner_state.get("concurrency"))
    lane_locks = _as_mapping(runner_state.get("active_lane_locks"))
    return (
        concurrency.get("schema_id") == "ion.codex_worker_concurrency.v0_1"
        and lane_locks.get("schema_id") == "ion.codex_lane_lock_index.v0_1"
        and concurrency.get("global_active_lock") is False
        and int(concurrency.get("same_lane_parallelism") or 0) == 1
    )


def _lane_index_ready(lane_index: Mapping[str, Any], queued_count: int) -> bool:
    lane_index_counts = _as_mapping(lane_index.get("lane_counts"))
    return (
        lane_index.get("schema_id") == "ion.codex_work_lane_index.v0_1"
        and bool(lane_index_counts)
        and int(lane_index.get("queued_request_count") or 0) == queued_count
    )


def _summary_for_classified_rows(
    classified: list[dict[str, Any]],
    *,
    queue: Mapping[str, Any],
    runner_state: Mapping[str, Any],
    lane_index: Mapping[str, Any],
) -> dict[str, Any]:
    waiting_rows = [row for row in classified if row.get("status") in {"QUEUED_FOR_CODEX_CARRIER", "PREPARED_FOR_CODEX_CARRIER_NOT_QUEUED"}]
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
    active_runs = active_run_entries_from_state(runner_state)
    lane_index_ready = _lane_index_ready(lane_index, len(queued_rows))
    return {
        "request_count": int(queue.get("request_count") or len(classified)),
        "total_request_count": int(queue.get("total_request_count") or len(classified)),
        "classified_request_count": len(classified),
        "waiting_request_count": len(waiting_rows),
        "claimable_waiting_request_count": len(queued_rows),
        "prepared_request_count": len(prepared_rows),
        "stale_waiting_request_count": len(stale_rows),
        "terminal_repair_request_count": len(repair_rows),
        "classified_terminal_backlog_count": len(classified_terminal_rows),
        "duplicate_group_count": int(queue.get("duplicate_group_count") or 0),
        "actionable_duplicate_group_count": actionable_duplicate_group_count(classified),
        "active_run_count": len(active_runs),
        "work_lane_projection_ready": lane_index_ready,
        "worker_concurrency_ready": worker_concurrency_ready(runner_state),
        "work_lane_waiting_request_count": int(lane_index.get("queued_request_count") or 0),
        "work_lane_needs_triage_count": int(lane_index.get("needs_triage_count") or 0),
    }


def _count_field(rows: list[Mapping[str, Any]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get(field) or "UNKNOWN")
        counts[value] = counts.get(value, 0) + 1
    return counts


def _scenario_checks(summary: Mapping[str, Any], expected: Mapping[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for key, expected_value in expected.items():
        observed = summary.get(key)
        checks.append({"check_id": key, "expected": expected_value, "observed": observed, "passed": observed == expected_value})
    return checks


def _scenario_request(
    request_id: str,
    *,
    created_at: datetime,
    objective: str,
    status: str = "QUEUED_FOR_CODEX_CARRIER",
    objective_sha256: str | None = None,
    lifecycle_disposition: str | None = None,
) -> dict[str, Any]:
    request: dict[str, Any] = {
        "request_id": request_id,
        "path": f"ION/05_context/current/chatgpt_connector/codex_work_requests/{request_id}.json",
        "status": status,
        "created_at": created_at.replace(microsecond=0).isoformat(),
        "updated_at": created_at.replace(microsecond=0).isoformat(),
        "objective": objective,
        "linked_return_count": 1 if status.startswith("RETURN_") else 0,
        "accepted_return_count": 1 if status == "RETURN_RECORDED_PROOF_ACCEPTED" else 0,
    }
    if objective_sha256:
        request["objective_sha256"] = objective_sha256
    if lifecycle_disposition:
        request["payload"] = {
            "queue_lifecycle_decision": {
                "schema_id": "ion.codex_work_request_queue_lifecycle_decision.v1",
                "disposition": lifecycle_disposition,
                "request_file_mutation": "lifecycle_metadata_only",
                "superseded": False,
            }
        }
    return request


def build_queue_governor_dogfood_projection(*, now: datetime | None = None) -> dict[str, Any]:
    current_time = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0)
    fresh_time = current_time - timedelta(minutes=5)
    stale_time = current_time - timedelta(days=3)
    scenarios: list[dict[str, Any]] = [
        {
            "scenario_id": "clean_empty_queue",
            "description": "No queued work, no active runs, lane projection current.",
            "requests": [],
            "queue": {"request_count": 0, "total_request_count": 0, "duplicate_group_count": 0},
            "runner_state": {
                "active_run": None,
                "active_runs": {},
                "active_lane_locks": {"schema_id": "ion.codex_lane_lock_index.v0_1", "same_lane_parallelism": 1},
                "concurrency": {"schema_id": "ion.codex_worker_concurrency.v0_1", "global_active_lock": False, "same_lane_parallelism": 1},
            },
            "lane_index": {"schema_id": "ion.codex_work_lane_index.v0_1", "queued_request_count": 0, "needs_triage_count": 0, "lane_counts": {"maintenance_lane": 0}},
            "expected": {"waiting_request_count": 0, "active_run_count": 0, "work_lane_projection_ready": True, "worker_concurrency_ready": True},
            "covered_behaviors": ["clean_queue_ready"],
        },
        {
            "scenario_id": "fresh_waiting_lane_ready",
            "description": "Fresh waiting request is eligible for lane claim and does not count as stale.",
            "requests": [
                _scenario_request(
                    "codex_req_fresh_comms",
                    created_at=fresh_time,
                    objective="ION agent invocation for COMMS_CARTOGRAPHER.",
                )
            ],
            "queue": {"request_count": 1, "total_request_count": 1, "duplicate_group_count": 0},
            "runner_state": {
                "active_run": None,
                "active_runs": {},
                "active_lane_locks": {"schema_id": "ion.codex_lane_lock_index.v0_1", "same_lane_parallelism": 1},
                "concurrency": {"schema_id": "ion.codex_worker_concurrency.v0_1", "global_active_lock": False, "same_lane_parallelism": 1},
            },
            "lane_index": {"schema_id": "ion.codex_work_lane_index.v0_1", "queued_request_count": 1, "needs_triage_count": 0, "lane_counts": {"comms_lane": 1}},
            "expected": {"waiting_request_count": 1, "stale_waiting_request_count": 0, "work_lane_projection_ready": True},
            "covered_behaviors": ["fresh_waiting_request", "lane_ready"],
        },
        {
            "scenario_id": "stale_duplicate_repair",
            "description": "Stale waiting work and an unclassified template-invalid return share a duplicate key.",
            "requests": [
                _scenario_request(
                    "codex_req_stale_queue",
                    created_at=stale_time,
                    objective="Reconcile stale queue currentness.",
                    objective_sha256="dogfood-duplicate-key",
                ),
                _scenario_request(
                    "codex_req_template_invalid",
                    created_at=stale_time,
                    objective="Audit template invalid queue evidence.",
                    status="RETURN_TEMPLATE_INVALID",
                    objective_sha256="dogfood-duplicate-key",
                ),
            ],
            "queue": {"request_count": 2, "total_request_count": 2, "duplicate_group_count": 1},
            "runner_state": {"active_run": None},
            "lane_index": {"schema_id": "ion.codex_work_lane_index.v0_1", "queued_request_count": 1, "needs_triage_count": 0, "lane_counts": {"maintenance_lane": 1, "audit_lane": 1}},
            "expected": {"stale_waiting_request_count": 1, "terminal_repair_request_count": 1, "actionable_duplicate_group_count": 1},
            "covered_behaviors": ["stale_waiting_request", "terminal_return_contract_repair", "actionable_duplicate_group"],
        },
        {
            "scenario_id": "classified_terminal_backlog",
            "description": "Lifecycle-classified template-invalid return stays preserved instead of being reflagged for repair.",
            "requests": [
                _scenario_request(
                    "codex_req_classified_template_invalid",
                    created_at=stale_time,
                    objective="Classified template invalid evidence.",
                    status="RETURN_TEMPLATE_INVALID",
                    lifecycle_disposition="digest_then_supersede",
                )
            ],
            "queue": {"request_count": 1, "total_request_count": 1, "duplicate_group_count": 0},
            "runner_state": {"active_run": None},
            "lane_index": {"schema_id": "ion.codex_work_lane_index.v0_1", "queued_request_count": 0, "needs_triage_count": 0, "lane_counts": {"audit_lane": 0}},
            "expected": {"classified_terminal_backlog_count": 1, "terminal_repair_request_count": 0},
            "covered_behaviors": ["classified_terminal_backlog"],
        },
        {
            "scenario_id": "active_run_and_triage",
            "description": "Active run state and unclassified request lane triage remain visible.",
            "requests": [
                _scenario_request(
                    "codex_req_needs_triage",
                    created_at=fresh_time,
                    objective="Unclassified operator follow-up.",
                )
            ],
            "queue": {"request_count": 1, "total_request_count": 1, "duplicate_group_count": 0},
            "runner_state": {
                "active_run": {"run_id": "dogfood_active_run", "request_id": "codex_req_other"},
                "active_runs": {"dogfood_active_run": {"run_id": "dogfood_active_run", "request_id": "codex_req_other"}},
                "active_lane_locks": {"schema_id": "ion.codex_lane_lock_index.v0_1", "same_lane_parallelism": 1},
                "concurrency": {"schema_id": "ion.codex_worker_concurrency.v0_1", "global_active_lock": False, "same_lane_parallelism": 1},
            },
            "lane_index": {"schema_id": "ion.codex_work_lane_index.v0_1", "queued_request_count": 1, "needs_triage_count": 1, "lane_counts": {"needs_triage": 1}},
            "expected": {"active_run_count": 1, "work_lane_needs_triage_count": 1, "worker_concurrency_ready": True},
            "covered_behaviors": ["active_run_present", "needs_triage_lane", "bounded_worker_concurrency"],
        },
    ]
    scenario_results: list[dict[str, Any]] = []
    behavior_coverage: set[str] = set()
    for scenario in scenarios:
        requests = [row for row in scenario.get("requests") or [] if isinstance(row, Mapping)]
        queue = _as_mapping(scenario.get("queue"))
        runner_state = _as_mapping(scenario.get("runner_state"))
        lane_index = _as_mapping(scenario.get("lane_index"))
        classified = [classify_queue_request(row, now=current_time) for row in requests]
        summary = _summary_for_classified_rows(classified, queue=queue, runner_state=runner_state, lane_index=lane_index)
        status_counts = _count_field(classified, "status")
        lane_counts = _count_field(classified, "lane_id")
        checks = _scenario_checks(summary, _as_mapping(scenario.get("expected")))
        passed = all(check.get("passed") is True for check in checks)
        coverage = [str(item) for item in scenario.get("covered_behaviors") or [] if str(item)]
        behavior_coverage.update(coverage)
        scenario_results.append(
            {
                "scenario_id": scenario.get("scenario_id"),
                "description": scenario.get("description"),
                "passed": passed,
                "covered_behaviors": coverage,
                "summary": summary,
                "status_counts": status_counts,
                "lane_counts": lane_counts,
                "checks": checks,
                "classified_requests": classified,
            }
        )
    failed = [row for row in scenario_results if not row.get("passed")]
    return {
        "schema_id": DOGFOOD_SCHEMA_ID,
        "generated_at": current_time.isoformat(),
        "status": "queue_governor_dogfood_ready" if not failed else "queue_governor_dogfood_failed",
        "summary": {
            "scenario_count": len(scenario_results),
            "passed_scenario_count": len(scenario_results) - len(failed),
            "failed_scenario_count": len(failed),
            "covered_behavior_count": len(behavior_coverage),
            "covered_behaviors": sorted(behavior_coverage),
        },
        "scenarios": scenario_results,
        "policy": "Queue Governor dogfood scenarios are in-memory classification checks. They do not mutate the live queue, runner state, lane index, accepted state, or receipts.",
        "authority": {
            "candidate_projection_only": True,
            "synthetic_scenarios_only": True,
            "queue_mutation_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def build_queue_governor_projection(
    root: str | Path | None = None,
    *,
    queue_path: Path = DEFAULT_CODEX_WORK_QUEUE_PATH,
    runner_state_path: Path = DEFAULT_CODEX_QUEUE_RUNNER_STATE_PATH,
    lane_index_path: Path = DEFAULT_CODEX_WORK_LANE_INDEX_PATH,
    stale_after_seconds: int = QUEUE_STALE_AFTER_SECONDS,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    queue = _read_json_file(shell_root / queue_path)
    runner_state = _read_json_file(shell_root / runner_state_path)
    lane_index = _read_json_file(shell_root / lane_index_path)
    now = datetime.now(timezone.utc)
    queue_requests = [row for row in queue.get("requests") or [] if isinstance(row, Mapping)]
    file_requests = work_request_file_rows(shell_root)
    requests = file_requests or queue_requests
    request_source = "work_request_files" if file_requests else "queue_projection"
    source_request_count = len(requests)
    classified = [classify_queue_request(row, now=now, stale_after_seconds=stale_after_seconds) for row in requests]
    status_counts: dict[str, int] = {}
    lane_counts: dict[str, int] = {}
    for row in classified:
        status = str(row.get("status") or "UNKNOWN")
        lane_id = str(row.get("lane_id") or "needs_triage")
        status_counts[status] = status_counts.get(status, 0) + 1
        lane_counts[lane_id] = lane_counts.get(lane_id, 0) + 1
    stale_rows = [row for row in classified if row.get("stale")]
    repair_rows = [row for row in classified if row.get("terminal_repair_needed")]
    classified_terminal_rows = [
        row
        for row in classified
        if row.get("classified_by_queue_lifecycle_decision")
        and str(row.get("status") or "")
        in {"RETURN_TEMPLATE_INVALID", "CODEX_QUEUE_RUNNER_FAILED", "CODEX_CLI_EXIT_NONZERO", "RETURN_RECORDED_PROOF_BLOCKED"}
    ]
    waiting_rows = [row for row in classified if row.get("status") in {"QUEUED_FOR_CODEX_CARRIER", "PREPARED_FOR_CODEX_CARRIER_NOT_QUEUED"}]
    queued_rows = [row for row in classified if row.get("status") == "QUEUED_FOR_CODEX_CARRIER"]
    prepared_rows = [row for row in classified if row.get("status") == "PREPARED_FOR_CODEX_CARRIER_NOT_QUEUED"]
    queue_request_count = int(queue.get("request_count") or len(queue_requests))
    queue_total_request_count = int(queue.get("total_request_count") or len(queue_requests))
    effective_total_request_count = max(queue_total_request_count, source_request_count)
    duplicate_group_count_value = duplicate_group_count(classified) if file_requests else int(queue.get("duplicate_group_count") or 0)
    actionable_duplicates = actionable_duplicate_group_count(classified)
    lane_index_counts = _as_mapping(lane_index.get("lane_counts"))
    lane_index_ready = _lane_index_ready(lane_index, len(queued_rows))
    active_runs = active_run_entries_from_state(runner_state)
    concurrency_ready = worker_concurrency_ready(runner_state)
    findings: list[dict[str, Any]] = []
    if not queue:
        findings.append({"code": "QUEUE_PROJECTION_MISSING", "path": queue_path.as_posix()})
    if stale_rows:
        findings.append({"code": "STALE_WAITING_REQUESTS", "count": len(stale_rows)})
    if repair_rows:
        findings.append({"code": "TERMINAL_REPAIR_REQUESTS", "count": len(repair_rows)})
    if actionable_duplicates:
        findings.append({"code": "ACTIONABLE_DUPLICATE_QUEUE_GROUPS_PRESENT", "count": actionable_duplicates})
    if active_runs:
        findings.append({"code": "ACTIVE_RUN_PRESENT", "count": len(active_runs)})
    if lane_counts.get("needs_triage"):
        findings.append({"code": "REQUESTS_NEED_TRIAGE", "count": lane_counts.get("needs_triage")})
    status = "queue_governor_ready"
    if not queue:
        status = "queue_governor_missing"
    elif findings:
        status = "queue_governor_needs_consolidation"
    next_packets: list[dict[str, Any]] = []
    if findings:
        next_packets.append(
            {
                "packet_id": "PCKT-ION-QUEUE-GOVERNOR-CURRENTNESS-RECONCILIATION-20260531",
                "lane_id": "maintenance_lane",
                "work_class": "maintenance",
                "objective": "Build a bounded queue currentness digest and emit supersede/repair recommendations without mutating accepted state.",
            }
        )
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "status": status,
        "queue_path": queue_path.as_posix(),
        "runner_state_path": runner_state_path.as_posix(),
        "work_lane_index_path": lane_index_path.as_posix(),
        "queue_exists": bool(queue),
        "runner_state_exists": bool(runner_state),
        "work_lane_index_exists": bool(lane_index),
        "work_lane_projection_ready": lane_index_ready,
        "summary": {
            "request_count": source_request_count if file_requests else queue_request_count,
            "total_request_count": effective_total_request_count,
            "classified_source_request_count": source_request_count,
            "request_source": request_source,
            "request_file_count": len(file_requests),
            "queue_projection_request_count": queue_request_count,
            "queue_projection_total_request_count": queue_total_request_count,
            "queue_projection_paginated": queue_total_request_count > queue_request_count,
            "classified_request_count": len(classified),
            "waiting_request_count": len(waiting_rows),
            "claimable_waiting_request_count": len(queued_rows),
            "prepared_request_count": len(prepared_rows),
            "stale_waiting_request_count": len(stale_rows),
            "terminal_repair_request_count": len(repair_rows),
            "classified_terminal_backlog_count": len(classified_terminal_rows),
            "duplicate_group_count": duplicate_group_count_value,
            "actionable_duplicate_group_count": actionable_duplicates,
            "active_run_count": len(active_runs),
            "work_lane_projection_ready": lane_index_ready,
            "worker_concurrency_ready": concurrency_ready,
            "work_lane_waiting_request_count": int(lane_index.get("queued_request_count") or 0),
            "work_lane_needs_triage_count": int(lane_index.get("needs_triage_count") or 0),
            "finding_count": len(findings),
            "next_packet_count": len(next_packets),
        },
        "status_counts": status_counts,
        "lane_counts": lane_counts,
        "work_lane_counts": dict(lane_index_counts),
        "worker_concurrency": _as_mapping(runner_state.get("concurrency")),
        "active_lane_locks": _as_mapping(runner_state.get("active_lane_locks")),
        "findings": findings,
        "flagged_requests": [row for row in classified if row.get("stale") or row.get("terminal_repair_needed")][:20],
        "next_packets": next_packets,
        "policy": "Queue Governor is a read-only projection. It may classify queue currentness and emit bounded repair recommendations; it does not claim, reorder, delete, or accept queue state.",
        "authority": {
            "candidate_projection_only": True,
            "queue_mutation_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }
