"""Read-only bounded kernel fan-out plan compiler.

This module compiles a small work graph into a deterministic scheduling plan
without spawning workers or mutating execution lanes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from .ion_codex_model_moves import build_codex_model_move_plan

SCHEMA_ID = "ion.kernel_fanout_plan.v1"
READY_VERDICT = "ION_KERNEL_FANOUT_PLAN_READY"
BLOCKED_VERDICT = "ION_KERNEL_FANOUT_PLAN_BLOCKED"
VERSION = "V1_KERNEL_FANOUT_SCHEDULER_CANDIDATE"
DEFAULT_MAX_PARALLEL = 2
MAX_MAX_PARALLEL = 16
DEFAULT_LEASE_SECONDS = 1800
DEFAULT_RETRY_MAX = 1
DEFAULT_HEARTBEAT_SECONDS = 30
DEFAULT_STALE_AFTER_SECONDS = 120
DEFAULT_ZOMBIE_AFTER_SECONDS = 300
DEFAULT_ARTIFACT_ROOT = "ION/05_context/current/chatgpt_connector/fanout_runs"
DEFAULT_REQUIRED_RECEIPT_CHAIN = (
    "context_receipt.json",
    "worker_context_awareness_receipt.v1(machine_generated)",
    "run.json",
    "stdout.log + stderr.log",
    "latest_return.md",
    "task_return.json",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stable_id(*parts: str) -> str:
    payload = "::".join(parts)
    return hashlib.sha256(payload.encode("utf-8", errors="replace")).hexdigest()[:24]


def _trim(value: Any, *, limit: int = 4000) -> str:
    return str(value or "").replace("\r\n", "\n").strip()[:limit]


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _safe_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")[:64] or "worker"


def _normalize_path(value: str) -> str | None:
    text = _trim(value, limit=512).strip()
    if not text:
        return None
    if text.startswith("/") or text.startswith("~"):
        return None
    path = PurePosixPath(text)
    if ".." in path.parts:
        return None
    return path.as_posix().lstrip("./")


def _path_overlap(left: str, right: str) -> bool:
    if left == right:
        return True
    left_parts = PurePosixPath(left).parts
    right_parts = PurePosixPath(right).parts
    min_len = min(len(left_parts), len(right_parts))
    return left_parts[:min_len] == right_parts[:min_len]


def _default_required_receipt_chain(accepted_worker_return: Mapping[str, Any] | None) -> list[str]:
    chain = list(DEFAULT_REQUIRED_RECEIPT_CHAIN)
    if accepted_worker_return:
        path_value = _trim(accepted_worker_return.get("path"), limit=400)
        sha_value = _trim(accepted_worker_return.get("sha256"), limit=128)
        if path_value and sha_value:
            chain.append(f"accepted_worker_receipt_return:{path_value}#sha256={sha_value}")
    return chain


def _topological_order(children: list[dict[str, Any]]) -> tuple[list[str], list[dict[str, Any]]]:
    by_id = {str(row["child_id"]): row for row in children}
    indegree = {child_id: 0 for child_id in by_id}
    dependents: dict[str, list[str]] = {child_id: [] for child_id in by_id}
    findings: list[dict[str, Any]] = []

    for row in children:
        child_id = str(row["child_id"])
        deps = [str(dep) for dep in row.get("depends_on", [])]
        deduped = []
        seen: set[str] = set()
        for dep in deps:
            if dep in seen:
                continue
            seen.add(dep)
            deduped.append(dep)
        row["depends_on"] = deduped
        for dep in deduped:
            if dep not in by_id:
                findings.append(
                    {
                        "code": "missing_dependency",
                        "severity": "blocked",
                        "child_id": child_id,
                        "dependency": dep,
                        "message": f"child '{child_id}' depends on missing child '{dep}'",
                    }
                )
                continue
            indegree[child_id] += 1
            dependents[dep].append(child_id)

    ready = sorted(child_id for child_id, degree in indegree.items() if degree == 0)
    order: list[str] = []
    while ready:
        current = ready.pop(0)
        order.append(current)
        for nxt in sorted(dependents[current]):
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                ready.append(nxt)
        ready.sort()

    if len(order) != len(children):
        blocked_ids = sorted(child_id for child_id, degree in indegree.items() if degree > 0)
        findings.append(
            {
                "code": "dependency_cycle",
                "severity": "blocked",
                "blocked_children": blocked_ids,
                "message": "dependency cycle detected; scheduler cannot derive full order",
            }
        )
    return order, findings


def _conflict_locks(children: list[dict[str, Any]]) -> list[dict[str, Any]]:
    locks: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    for left_idx, left in enumerate(children):
        left_id = str(left["child_id"])
        left_paths = [str(path) for path in left.get("write_paths", [])]
        left_resources = [str(lock) for lock in left.get("resource_locks", [])]
        for right in children[left_idx + 1 :]:
            right_id = str(right["child_id"])
            right_paths = [str(path) for path in right.get("write_paths", [])]
            right_resources = [str(lock) for lock in right.get("resource_locks", [])]

            for l_path in left_paths:
                for r_path in right_paths:
                    if not _path_overlap(l_path, r_path):
                        continue
                    lock_key = f"path::{min(l_path, r_path)}::{max(l_path, r_path)}::{left_id}::{right_id}"
                    if lock_key in seen_keys:
                        continue
                    seen_keys.add(lock_key)
                    locks.append(
                        {
                            "lock_id": "fanout_lock_" + _stable_id(lock_key),
                            "lock_type": "path_overlap",
                            "holder_children": sorted([left_id, right_id]),
                            "left_path": l_path,
                            "right_path": r_path,
                            "enforcement": "serialize_conflicting_children",
                        }
                    )

            for l_lock in left_resources:
                for r_lock in right_resources:
                    if l_lock != r_lock:
                        continue
                    lock_key = f"resource::{l_lock}::{left_id}::{right_id}"
                    if lock_key in seen_keys:
                        continue
                    seen_keys.add(lock_key)
                    locks.append(
                        {
                            "lock_id": "fanout_lock_" + _stable_id(lock_key),
                            "lock_type": "resource_match",
                            "resource": l_lock,
                            "holder_children": sorted([left_id, right_id]),
                            "enforcement": "serialize_conflicting_children",
                        }
                    )
    return sorted(locks, key=lambda row: str(row["lock_id"]))


def _dependency_gates(children: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gates = []
    by_id = {str(row["child_id"]) for row in children}
    for row in children:
        child_id = str(row["child_id"])
        deps = [str(dep) for dep in row.get("depends_on", [])]
        gates.append(
            {
                "child_id": child_id,
                "blocked_on": deps,
                "gate_state": "open" if not deps else "await_dependencies",
                "can_schedule_now": not bool(deps),
                "all_dependencies_known": all(dep in by_id for dep in deps),
            }
        )
    return gates


def _reducer_plan() -> dict[str, Any]:
    return {
        "mode": "proof_gated_settlement",
        "accept_requires": [
            "context_proof_accepted",
            "template_action_proof_accepted",
            "workload_diff_present",
            "required_receipt_chain_complete",
        ],
        "reject_if": [
            "missing_required_receipt_chain",
            "worker_context_status=WORKER_CONTEXT_BLOCKED",
            "task_return_sha256_mismatch",
            "explicit_operator_reject",
        ],
        "merge_behavior": "candidate_only_until_steward_settlement",
        "settlement_receipt": "ion.kernel_fanout_settlement_receipt.v1",
    }


def build_kernel_fanout_plan(
    graph: Mapping[str, Any],
    *,
    emitted_at: str | None = None,
    compact: bool = True,
) -> dict[str, Any]:
    timestamp = emitted_at or _now()
    parent_packet_id = _trim(graph.get("parent_packet_id"), limit=240)
    raw_children = [row for row in _as_list(graph.get("children")) if isinstance(row, Mapping)]
    findings: list[dict[str, Any]] = []

    max_parallel_raw = graph.get("max_parallel", DEFAULT_MAX_PARALLEL)
    try:
        max_parallel = int(max_parallel_raw)
    except (TypeError, ValueError):
        max_parallel = DEFAULT_MAX_PARALLEL
        findings.append(
            {
                "code": "invalid_max_parallel",
                "severity": "blocked",
                "message": f"max_parallel '{max_parallel_raw}' is not an integer",
            }
        )
    if max_parallel < 1:
        findings.append(
            {
                "code": "max_parallel_too_low",
                "severity": "blocked",
                "message": "max_parallel must be >= 1",
            }
        )
    if max_parallel > MAX_MAX_PARALLEL:
        findings.append(
            {
                "code": "max_parallel_too_high",
                "severity": "blocked",
                "message": f"max_parallel must be <= {MAX_MAX_PARALLEL}",
            }
        )
    max_parallel = max(1, min(max_parallel, MAX_MAX_PARALLEL))

    if not parent_packet_id:
        findings.append(
            {
                "code": "missing_parent_packet_id",
                "severity": "blocked",
                "message": "parent_packet_id is required",
            }
        )

    accepted_worker_return = graph.get("accepted_worker_return")
    if not isinstance(accepted_worker_return, Mapping):
        accepted_worker_return = None

    default_receipt_chain = _default_required_receipt_chain(accepted_worker_return)
    artifact_root = _normalize_path(_trim(graph.get("artifact_root"), limit=300)) or DEFAULT_ARTIFACT_ROOT

    seen_child_ids: set[str] = set()
    children: list[dict[str, Any]] = []
    for idx, payload in enumerate(raw_children, start=1):
        child_id = _trim(payload.get("child_id") or payload.get("id") or f"child_{idx}", limit=96)
        if child_id in seen_child_ids:
            findings.append(
                {
                    "code": "duplicate_child_id",
                    "severity": "blocked",
                    "child_id": child_id,
                    "message": f"duplicate child_id '{child_id}'",
                }
            )
            continue
        seen_child_ids.add(child_id)

        objective = _trim(payload.get("objective"), limit=4000)
        if not objective:
            findings.append(
                {
                    "code": "missing_objective",
                    "severity": "blocked",
                    "child_id": child_id,
                    "message": f"child '{child_id}' has no objective",
                }
            )

        write_paths: list[str] = []
        for raw_path in _as_list(payload.get("write_paths")):
            normalized = _normalize_path(_trim(raw_path, limit=400))
            if not normalized:
                findings.append(
                    {
                        "code": "invalid_write_path",
                        "severity": "blocked",
                        "child_id": child_id,
                        "path": str(raw_path),
                        "message": "write_paths must be repo-relative and may not escape root",
                    }
                )
                continue
            write_paths.append(normalized)

        resource_locks = []
        for lock in _as_list(payload.get("resource_locks")):
            text = _trim(lock, limit=200)
            if text:
                resource_locks.append(text)

        depends_on = []
        for dep in _as_list(payload.get("depends_on")):
            dep_id = _trim(dep, limit=96)
            if dep_id:
                depends_on.append(dep_id)

        selected = build_codex_model_move_plan(
            lane_id="codex_general",
            stage_id=_trim(payload.get("stage_id"), limit=80) or None,
            work_class=_trim(payload.get("work_class"), limit=80) or None,
            objective=objective,
            risk_level=_trim(payload.get("risk_level"), limit=40) or None,
            context_need=_trim(payload.get("context_need"), limit=40) or "medium",
            routing_posture=_trim(payload.get("routing_posture"), limit=80) or "conserve_main_bank",
            emitted_at=timestamp,
        )

        child_slug = _safe_slug(child_id)
        run_base = f"{artifact_root}/{child_slug}"
        lease_seconds = int(payload.get("lease_seconds") or DEFAULT_LEASE_SECONDS)
        heartbeat_seconds = int(payload.get("heartbeat_seconds") or DEFAULT_HEARTBEAT_SECONDS)
        stale_after_seconds = int(payload.get("stale_after_seconds") or DEFAULT_STALE_AFTER_SECONDS)
        zombie_after_seconds = int(payload.get("zombie_after_seconds") or DEFAULT_ZOMBIE_AFTER_SECONDS)
        retry_max = int(payload.get("retry_max") or DEFAULT_RETRY_MAX)

        if stale_after_seconds <= heartbeat_seconds:
            stale_after_seconds = heartbeat_seconds * 2
        if zombie_after_seconds <= stale_after_seconds:
            zombie_after_seconds = stale_after_seconds * 2

        required_receipt_chain = [
            _trim(item, limit=240)
            for item in _as_list(payload.get("required_receipt_chain")) or list(default_receipt_chain)
            if _trim(item, limit=240)
        ]

        children.append(
            {
                "child_id": child_id,
                "objective_excerpt": objective[:180],
                "objective_sha256": hashlib.sha256(objective.encode("utf-8", errors="replace")).hexdigest(),
                "depends_on": sorted(set(depends_on)),
                "write_paths": sorted(set(write_paths)),
                "resource_locks": sorted(set(resource_locks)),
                "lease": {
                    "lease_id": "lease_" + _stable_id(parent_packet_id or "missing_parent", child_id),
                    "lease_seconds": max(30, lease_seconds),
                    "lease_path": f"{run_base}/lease.json",
                },
                "telemetry": {
                    "heartbeat_seconds": max(5, heartbeat_seconds),
                    "stale_after_seconds": max(10, stale_after_seconds),
                    "zombie_after_seconds": max(20, zombie_after_seconds),
                    "states": ["live", "stale", "zombie"],
                },
                "artifacts": {
                    "stdout_path": f"{run_base}/stdout.log",
                    "stderr_path": f"{run_base}/stderr.log",
                    "latest_return_path": f"{run_base}/latest_return.md",
                    "task_return_path": f"{run_base}/task_return.json",
                    "worker_context_awareness_receipt_path": f"{run_base}/worker_context_awareness_receipt.json",
                },
                "model_move": {
                    "selected_model": selected["selected_model"],
                    "selected_reasoning_effort": selected["selected_reasoning_effort"],
                    "usage_pool_id": selected["usage_pool_id"],
                    "work_class": selected["work_class"],
                    "risk_level": selected["risk_level"],
                    "model_selection_reasons": list(selected.get("model_selection_reasons", []))[:6],
                },
                "required_receipt_chain": required_receipt_chain,
                "cancel_retry_controls": {
                    "cancel_modes": ["graceful", "hard_timeout"],
                    "retry_max": max(0, retry_max),
                    "retry_backoff_seconds": max(5, int(payload.get("retry_backoff_seconds") or 30)),
                },
            }
        )

    dependency_order, dependency_findings = _topological_order(children)
    findings.extend(dependency_findings)

    conflict_locks = _conflict_locks(children)
    blocked = any(str(row.get("severity")) == "blocked" for row in findings)

    plan_id = "fanout_plan_" + _stable_id(
        parent_packet_id or "missing_parent",
        str(max_parallel),
        str(len(children)),
        timestamp,
    )

    plan = {
        "schema_id": SCHEMA_ID,
        "version": VERSION,
        "verdict": BLOCKED_VERDICT if blocked else READY_VERDICT,
        "emitted_at": timestamp,
        "plan_id": plan_id,
        "parent_packet_id": parent_packet_id or None,
        "child_count": len(children),
        "max_parallel": max_parallel,
        "conflict_locks": conflict_locks,
        "dependency_order": dependency_order,
        "dependency_gates": _dependency_gates(children),
        "children": children,
        "reducer_settlement_plan": _reducer_plan(),
        "blocked_findings": findings,
        "read_only_compiler": True,
        "production_authority": False,
        "live_execution_authority": False,
    }

    if compact:
        plan["children"] = [
            {
                "child_id": row["child_id"],
                "depends_on": row["depends_on"],
                "write_paths": row["write_paths"],
                "lease": row["lease"],
                "telemetry": row["telemetry"],
                "artifacts": row["artifacts"],
                "model_move": row["model_move"],
                "required_receipt_chain": row["required_receipt_chain"],
                "cancel_retry_controls": row["cancel_retry_controls"],
                "objective_excerpt": row["objective_excerpt"],
                "objective_sha256": row["objective_sha256"],
            }
            for row in children
        ]
        plan["response_compact"] = True
    else:
        plan["response_compact"] = False
    return plan


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid graph payload: {path}")
    return payload


def compile_kernel_fanout_plan_from_file(path: str | Path, *, compact: bool = True) -> dict[str, Any]:
    graph = _read_json(Path(path))
    return build_kernel_fanout_plan(graph, compact=compact)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile a read-only bounded kernel fan-out plan.")
    parser.add_argument("graph_json", help="Path to graph JSON input")
    parser.add_argument("--no-compact", action="store_true", help="Emit fuller child payloads")
    args = parser.parse_args(argv)
    payload = compile_kernel_fanout_plan_from_file(args.graph_json, compact=not args.no_compact)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
