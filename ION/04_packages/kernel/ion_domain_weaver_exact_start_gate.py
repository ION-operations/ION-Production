"""Exact-path gate for the Domain Weaver spawn-dispatch main test.

This helper turns a read-only spawn-dispatch start plan into an operator-facing
main-test gate. It can preserve candidate artifacts, but it never starts Codex,
processes the general queue, claims accepted state, or materializes topology.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from kernel.ion_domain_weaver_spawn_request_dispatcher import (
    SPAWN_DISPATCH_START_PLAN_SCHEMA_ID,
    build_spawn_dispatch_start_plan,
)


EXACT_START_GATE_SCHEMA_ID = (
    "ion.domain_weaver.exact_spawn_dispatch_start_gate.v0_1_candidate"
)
EXACT_START_GATE_RECEIPT_SCHEMA_ID = (
    "ion.domain_weaver.exact_spawn_dispatch_start_gate_receipt.v0_1"
)
DEFAULT_TIMEOUT_SECONDS = 1800
DEFAULT_OUTPUT_DIR = Path("ION/05_context/current/domain_weaver/queue_governance")
DEFAULT_OPERATOR_RECEIPT_DIR = Path(
    "ION/05_context/current/domain_weaver/operator_actions"
)
RUNNER_STATE_PATH = Path(
    "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
)
DEFAULT_EXACT_SPAWN_DISPATCH_REQUEST_PATHS: tuple[str, ...] = (
    "ION/05_context/current/chatgpt_connector/codex_work_requests/2026-06-04T124258Z0000_domain_weaver_spawn_dispatch_for_domain_domain_weaver_fanout_control_pckt_domain.json",
    "ION/05_context/current/chatgpt_connector/codex_work_requests/2026-06-04T124310Z0000_domain_weaver_spawn_dispatch_for_domain_domain_weaver_nemesis_production_gate_pc.json",
)


def build_exact_spawn_dispatch_start_gate(
    active_root: str | Path,
    *,
    request_paths: list[str] | tuple[str, ...] | None = None,
    max_lanes: int = 2,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    start_plan: Mapping[str, Any] | None = None,
    runner_state: Mapping[str, Any] | None = None,
    fresh_runtime_status_confirmed: bool = False,
) -> dict[str, Any]:
    """Build the exact-path main-test gate without starting workers."""

    root = _require_active_root(active_root)
    normalized_paths = _normalize_request_paths(
        root,
        request_paths
        if request_paths is not None
        else DEFAULT_EXACT_SPAWN_DISPATCH_REQUEST_PATHS,
    )
    plan = dict(
        start_plan
        if start_plan is not None
        else build_spawn_dispatch_start_plan(
            root,
            request_paths=normalized_paths,
            max_lanes=max_lanes,
        )
    )
    state = dict(runner_state) if runner_state is not None else _read_json(root / RUNNER_STATE_PATH)
    selected_lanes = [str(row.get("lane_id") or "") for row in plan.get("start_plan_rows") or []]
    runtime_idle = _runner_idle_check(state, selected_lanes=selected_lanes)
    candidate_checks = _candidate_checks(
        root,
        normalized_paths=normalized_paths,
        start_plan=plan,
    )
    candidate_blockers = _candidate_blockers(candidate_checks, plan)
    immediate_blockers = list(candidate_blockers)
    if not fresh_runtime_status_confirmed:
        immediate_blockers.append("fresh_runtime_status_not_confirmed")
    if runtime_idle["ok"] is not True:
        immediate_blockers.extend(runtime_idle["blockers"])

    ready_candidate = not candidate_blockers
    ready_immediate = ready_candidate and not immediate_blockers
    gate = {
        "schema_id": EXACT_START_GATE_SCHEMA_ID,
        "status": "exact_spawn_dispatch_start_gate_built",
        "created_at": _utc_now(),
        "active_root": str(root),
        "active_root_proof": _active_root_proof(root),
        "request_paths": normalized_paths,
        "request_path_count": len(normalized_paths),
        "max_lanes": max(0, int(max_lanes)),
        "timeout_seconds": max(1, int(timeout_seconds)),
        "start_plan_schema_id": plan.get("schema_id"),
        "start_plan": _compact_start_plan(plan),
        "candidate_checks": candidate_checks,
        "candidate_blockers": candidate_blockers,
        "runtime_idle_check": runtime_idle,
        "fresh_runtime_status_confirmed": bool(fresh_runtime_status_confirmed),
        "ready_for_main_test_candidate": ready_candidate,
        "ready_for_immediate_exact_start": ready_immediate,
        "verdict": (
            "READY_FOR_EXACT_PATH_MAIN_TEST_AFTER_FRESH_RUNTIME_PREFLIGHT"
            if ready_candidate and not ready_immediate
            else (
                "READY_FOR_IMMEDIATE_EXACT_PATH_MAIN_TEST"
                if ready_immediate
                else "NOT_READY_BLOCKED_BY_EXACT_START_GATE"
            )
        ),
        "recommended_mode": "staged_sequential_exact_paths",
        "parallel_exact_start_eligible": ready_candidate
        and len(set(selected_lanes)) == len(selected_lanes)
        and len(selected_lanes) > 1,
        "general_queue_processing_allowed": False,
        "exact_request_path_required": True,
        "status_command": _status_command(),
        "start_commands": [
            _start_command(path, timeout_seconds=max(1, int(timeout_seconds)))
            for path in normalized_paths
        ],
        "proof_requirements": _proof_requirements(),
        "hard_stop_conditions": _hard_stop_conditions(),
        "non_claims": _non_claims(),
        "authority": _authority_block(),
        "actual_spawn_performed": False,
        "codex_queue_run_started": False,
        "worker_start_performed_by_gate": False,
        "accepted_state_claimed": False,
        "production_or_live_authority": False,
        "secrets_authority": False,
        "materialization_ready_claimed": False,
        "next_action": (
            "run_fresh_runtime_status_then_start_only_the_two_exact_request_paths"
            if ready_candidate
            else "repair_exact_start_gate_blockers"
        ),
    }
    return gate


def write_exact_spawn_dispatch_start_gate(
    active_root: str | Path,
    *,
    request_paths: list[str] | tuple[str, ...] | None = None,
    max_lanes: int = 2,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    fresh_runtime_status_confirmed: bool = False,
) -> dict[str, Any]:
    """Write latest candidate gate artifacts and an operator receipt."""

    root = _require_active_root(active_root)
    gate = build_exact_spawn_dispatch_start_gate(
        root,
        request_paths=request_paths,
        max_lanes=max_lanes,
        timeout_seconds=timeout_seconds,
        fresh_runtime_status_confirmed=fresh_runtime_status_confirmed,
    )
    output_dir = root / DEFAULT_OUTPUT_DIR
    receipt_dir = root / DEFAULT_OPERATOR_RECEIPT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    receipt_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "DOMAIN_WEAVER_EXACT_SPAWN_DISPATCH_START_GATE.latest.json"
    md_path = output_dir / "DOMAIN_WEAVER_EXACT_SPAWN_DISPATCH_START_GATE.latest.md"
    _write_json(json_path, gate)
    md_path.write_text(render_exact_spawn_dispatch_start_gate(gate), encoding="utf-8")
    receipt = {
        "schema_id": EXACT_START_GATE_RECEIPT_SCHEMA_ID,
        "created_at": _utc_now(),
        "active_root": str(root),
        "json_path": _relative_posix(root, json_path),
        "markdown_path": _relative_posix(root, md_path),
        "json_sha256": _sha256(json_path),
        "markdown_sha256": _sha256(md_path),
        "ready_for_main_test_candidate": gate["ready_for_main_test_candidate"],
        "ready_for_immediate_exact_start": gate["ready_for_immediate_exact_start"],
        "verdict": gate["verdict"],
        "general_queue_processing_allowed": False,
        "worker_start_performed_by_gate": False,
        "authority": _authority_block(),
    }
    receipt_path = (
        receipt_dir
        / f"{_stamp_for_path()}_domain_weaver_exact_spawn_dispatch_start_gate.json"
    )
    _write_json(receipt_path, receipt)
    return {
        "gate": gate,
        "json_path": _relative_posix(root, json_path),
        "markdown_path": _relative_posix(root, md_path),
        "receipt_path": _relative_posix(root, receipt_path),
        "receipt": receipt,
    }


def render_exact_spawn_dispatch_start_gate(gate: Mapping[str, Any]) -> str:
    """Render the gate as a compact operator-facing Markdown report."""

    start_plan = gate.get("start_plan") if isinstance(gate.get("start_plan"), Mapping) else {}
    lines = [
        "# Domain Weaver Exact Spawn-Dispatch Start Gate",
        "",
        f"- schema: `{gate.get('schema_id')}`",
        f"- created_at: `{gate.get('created_at')}`",
        f"- verdict: `{gate.get('verdict')}`",
        f"- ready_for_main_test_candidate: `{_bool_text(gate.get('ready_for_main_test_candidate'))}`",
        f"- ready_for_immediate_exact_start: `{_bool_text(gate.get('ready_for_immediate_exact_start'))}`",
        f"- general_queue_processing_allowed: `{_bool_text(gate.get('general_queue_processing_allowed'))}`",
        f"- worker_start_performed_by_gate: `{_bool_text(gate.get('worker_start_performed_by_gate'))}`",
        "",
        "## Exact Request Paths",
    ]
    for path in gate.get("request_paths") or []:
        lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "## Start Plan",
            f"- planned_start_count: `{start_plan.get('planned_start_count')}`",
            f"- blocked_start_count: `{start_plan.get('blocked_start_count')}`",
            f"- worker_start_readiness_ok: `{_bool_text(start_plan.get('worker_start_readiness_ok'))}`",
            f"- global_worker_start_readiness_ok: `{_bool_text(start_plan.get('global_worker_start_readiness_ok'))}`",
            "",
            "## Required Commands",
            "Fresh runtime status must be checked immediately before the starts:",
            "",
            "```bash",
            str(gate.get("status_command") or ""),
            "```",
            "",
            "Start only by exact request path:",
            "",
        ]
    )
    for command in gate.get("start_commands") or []:
        lines.extend(["```bash", str(command), "```", ""])
    lines.extend(["## Candidate Blockers"])
    blockers = list(gate.get("candidate_blockers") or [])
    if blockers:
        lines.extend(f"- `{blocker}`" for blocker in blockers)
    else:
        lines.append("- none")
    lines.extend(["", "## Hard Stops"])
    lines.extend(f"- `{item}`" for item in gate.get("hard_stop_conditions") or [])
    lines.extend(["", "## Non-Claims"])
    lines.extend(f"- `{item}`" for item in gate.get("non_claims") or [])
    return "\n".join(lines).rstrip() + "\n"


def _candidate_checks(
    root: Path,
    *,
    normalized_paths: list[str],
    start_plan: Mapping[str, Any],
) -> dict[str, bool]:
    planned_paths = set(str(path) for path in start_plan.get("candidate_exact_request_paths") or [])
    requested_paths = set(normalized_paths)
    return {
        "active_root_proof_ok": _active_root_proof(root)["proof_ok"],
        "exact_request_paths_present": bool(normalized_paths),
        "exact_request_paths_unique": len(normalized_paths) == len(requested_paths),
        "start_plan_schema_ok": start_plan.get("schema_id") == SPAWN_DISPATCH_START_PLAN_SCHEMA_ID,
        "start_plan_matches_requested_paths": planned_paths == requested_paths,
        "planned_start_count_matches_request_count": int(start_plan.get("planned_start_count") or 0)
        == len(normalized_paths),
        "blocked_start_count_zero": int(start_plan.get("blocked_start_count") or 0) == 0,
        "worker_start_readiness_ok": bool(start_plan.get("worker_start_readiness_ok")),
        "general_queue_processing_disallowed": start_plan.get("general_queue_processing_allowed") is False,
        "codex_queue_run_not_started": start_plan.get("codex_queue_run_started") is False,
        "actual_spawn_not_performed": start_plan.get("actual_spawn_performed") is False,
    }


def _candidate_blockers(
    checks: Mapping[str, bool],
    start_plan: Mapping[str, Any],
) -> list[str]:
    blockers = [name for name, ok in checks.items() if not ok]
    blockers.extend(str(item) for item in start_plan.get("worker_start_readiness_blockers") or [])
    for row in start_plan.get("blocked_rows") or []:
        if isinstance(row, Mapping):
            path = str(row.get("request_path") or "unknown_request_path")
            for blocker in row.get("blockers") or []:
                blockers.append(f"{path}:{blocker}")
    return sorted(set(blockers))


def _runner_idle_check(
    runner_state: Mapping[str, Any],
    *,
    selected_lanes: list[str],
) -> dict[str, Any]:
    if not runner_state:
        return {
            "ok": None,
            "source": RUNNER_STATE_PATH.as_posix(),
            "blockers": ["runner_state_snapshot_missing"],
            "fresh_status_still_required": True,
        }
    blockers: list[str] = []
    active_runs = runner_state.get("active_runs")
    if isinstance(active_runs, Mapping) and active_runs:
        blockers.append("runner_state_active_runs_present")
    if runner_state.get("active_run"):
        blockers.append("runner_state_active_run_present")
    if runner_state.get("active_process_running") is True:
        blockers.append("runner_state_active_process_running")
    locks = runner_state.get("active_lane_locks")
    selected_lane_locks: dict[str, Any] = {}
    if isinstance(locks, Mapping):
        if int(locks.get("active_run_count") or 0) > 0:
            blockers.append("runner_state_active_run_count_nonzero")
        if int(locks.get("active_lane_count") or 0) > 0:
            blockers.append("runner_state_active_lane_count_nonzero")
        if int(locks.get("unknown_lane_active_run_count") or 0) > 0:
            blockers.append("runner_state_unknown_lane_active_run_count_nonzero")
        lock_rows = locks.get("locks")
        if isinstance(lock_rows, Mapping):
            for lane in selected_lanes:
                lock = lock_rows.get(lane)
                if isinstance(lock, Mapping):
                    selected_lane_locks[lane] = dict(lock)
                    if lock.get("locked"):
                        blockers.append(f"selected_lane_locked:{lane}")
    return {
        "ok": not blockers,
        "source": RUNNER_STATE_PATH.as_posix(),
        "updated_at": runner_state.get("updated_at"),
        "active_process_running": runner_state.get("active_process_running"),
        "selected_lane_locks": selected_lane_locks,
        "blockers": sorted(set(blockers)),
        "fresh_status_still_required": True,
    }


def _compact_start_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": plan.get("schema_id"),
        "status": plan.get("status"),
        "created_at": plan.get("created_at"),
        "queueable_spawn_dispatch_request_count": plan.get("queueable_spawn_dispatch_request_count"),
        "planned_start_count": plan.get("planned_start_count"),
        "blocked_start_count": plan.get("blocked_start_count"),
        "max_lanes": plan.get("max_lanes"),
        "selected_lane_ids": list(plan.get("selected_lane_ids") or []),
        "candidate_exact_request_paths": list(plan.get("candidate_exact_request_paths") or []),
        "blocked_request_paths": list(plan.get("blocked_request_paths") or []),
        "worker_start_readiness_scope": plan.get("worker_start_readiness_scope"),
        "worker_start_readiness_ok": bool(plan.get("worker_start_readiness_ok")),
        "worker_start_readiness_blockers": list(plan.get("worker_start_readiness_blockers") or []),
        "global_worker_start_readiness_ok": bool(plan.get("global_worker_start_readiness_ok")),
        "global_worker_start_readiness_blockers": list(plan.get("global_worker_start_readiness_blockers") or []),
        "start_plan_rows": list(plan.get("start_plan_rows") or []),
        "blocked_rows": list(plan.get("blocked_rows") or []),
        "general_queue_processing_allowed": False,
        "codex_queue_run_started": False,
        "actual_spawn_performed": False,
    }


def _proof_requirements() -> list[str]:
    return [
        "start_result_ok_true",
        "start_result_CODEX_QUEUE_RUNNER_WORKER_STARTED",
        "exact_request_path_match_in_run_json",
        "worker_context_awareness_receipt_path_present",
        "context_receipt_path_present",
        "worker_shift_lease_claim_and_release_recorded",
        "task_return_path_present_or_explicit_terminal_failure_classification",
        "task_return_machine_receipt_path_present_when_return_accepted",
        "carrier_intake_only_true",
        "product_state_accepted_false",
        "accepted_state_authority_false",
        "automatic_agent_reaction_proven_false_unless_original_chain_is_separately_proven",
        "nemesis_review_required_before_widening",
    ]


def _hard_stop_conditions() -> list[str]:
    return [
        "general_queue_processing_requested",
        "start_without_exact_request_path",
        "request_path_no_longer_queued_for_codex_carrier",
        "request_kind_not_domain_weaver_spawn_dispatch",
        "same_lane_or_unknown_lane_active_run",
        "shared_codex_solo_used_as_working_capsule",
        "worker_start_context_gate_blocked",
        "worker_shift_lease_blocked",
        "connector_ok_false_counted_as_enqueue",
        "dispatch_enqueue_receipt_treated_as_worker_run",
        "failed_cli_log_treated_as_task_return",
        "accepted_state_or_product_state_claim",
        "production_live_secret_or_materialization_claim",
        "semantic_alias_or_projection_apply_before_supervised_apply_gate",
        "alternate_worker_recovery_counted_as_original_autoreaction",
        "recursive_child_spawn_or_over_cap_fanout_used",
    ]


def _non_claims() -> list[str]:
    return [
        "this_gate_does_not_start_workers",
        "this_gate_does_not_process_the_queue",
        "queued_not_started_is_not_a_live_worker",
        "candidate_graph_delta_is_not_accepted_state",
        "readiness_is_not_product_state_acceptance",
        "worker_returns_are_carrier_intake_only",
        "automatic_agent_reaction_is_not_proven_by_alternate_worker_recovery",
    ]


def _authority_block() -> dict[str, Any]:
    return {
        "candidate_only": True,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "materialization_authority": False,
        "worker_return_is_carrier_intake_only": True,
    }


def _active_root_proof(root: Path) -> dict[str, Any]:
    pyproject = root / "pyproject.toml"
    repo_authority = root / "ION/REPO_AUTHORITY.md"
    return {
        "schema_id": "ion.active_root_proof.v0_1_candidate",
        "active_root": str(root),
        "required_siblings": {
            "pyproject.toml": {"path": "pyproject.toml", "present": pyproject.is_file()},
            "ION/REPO_AUTHORITY.md": {
                "path": "ION/REPO_AUTHORITY.md",
                "present": repo_authority.is_file(),
            },
        },
        "proof_ok": pyproject.is_file() and repo_authority.is_file(),
        **_authority_block(),
    }


def _normalize_request_paths(
    root: Path,
    request_paths: list[str] | tuple[str, ...] | None,
) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for value in request_paths or []:
        text = str(value or "").strip()
        if not text:
            continue
        path = Path(text)
        if path.is_absolute():
            try:
                text = path.resolve(strict=False).relative_to(root).as_posix()
            except ValueError:
                text = path.as_posix()
        text = text.replace("\\", "/")
        if text not in seen:
            normalized.append(text)
            seen.add(text)
    return normalized


def _start_command(path: str, *, timeout_seconds: int) -> str:
    return (
        "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ION/04_packages "
        "python3 -S -m kernel.ion_codex_queue_runner --ion-root . "
        "--process-once --start "
        f"--timeout-seconds {int(timeout_seconds)} "
        f"--request-path '{path}' --json"
    )


def _status_command() -> str:
    return (
        "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ION/04_packages "
        "python3 -m kernel.ion_codex_queue_runner --ion-root . --status --json"
    )


def _require_active_root(active_root: str | Path) -> Path:
    root = Path(active_root).expanduser().resolve()
    if not (root / "pyproject.toml").is_file():
        raise ValueError("active_root_missing_pyproject")
    if not (root / "ION/REPO_AUTHORITY.md").is_file():
        raise ValueError("active_root_missing_repo_authority")
    return root


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative_posix(root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _stamp_for_path() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _bool_text(value: Any) -> str:
    return "true" if value is True else "false" if value is False else str(value)
