"""Bounded no-op smoke harness for kernel fan-out plan validation.

This harness simulates child scheduling from an accepted fan-out plan without
spawning real workers or mutating external systems.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_kernel_fanout_plan import build_kernel_fanout_plan

SCHEMA_ID = "ion.kernel_fanout_noop_smoke_result.v1"
SIGNIN_SCHEMA_ID = "ion.worker_context_awareness_receipt.v1"
STATUS_ACK = "WORKER_CONTEXT_ACKNOWLEDGED"
STATUS_BLOCKED = "WORKER_CONTEXT_BLOCKED"
DEFAULT_STEP_SECONDS = 1
DEFAULT_OUTPUT_ROOT = Path("ION/05_context/current/kernel_fanout_scheduler/smoke_runs")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha256_payload(payload: Mapping[str, Any]) -> str:
    material = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(material.encode("utf-8", errors="replace")).hexdigest()


def _safe_child_row(raw: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "child_id": str(raw.get("child_id") or ""),
        "depends_on": [str(dep) for dep in raw.get("depends_on", [])],
        "write_paths": [str(path) for path in raw.get("write_paths", [])],
        "lease": dict(raw.get("lease") or {}),
        "telemetry": dict(raw.get("telemetry") or {}),
        "artifacts": dict(raw.get("artifacts") or {}),
        "required_receipt_chain": [str(item) for item in raw.get("required_receipt_chain", [])],
        "cancel_retry_controls": dict(raw.get("cancel_retry_controls") or {}),
        "model_move": dict(raw.get("model_move") or {}),
    }


def _lock_index(plan: Mapping[str, Any]) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {}
    for lock in plan.get("conflict_locks", []):
        holders = [str(child_id) for child_id in lock.get("holder_children", [])]
        for child_id in holders:
            index.setdefault(child_id, set()).update(other for other in holders if other != child_id)
    return index


def _contains_machine_signin_requirement(required_chain: list[str]) -> bool:
    for item in required_chain:
        token = item.lower()
        if "worker_context_awareness_receipt" in token:
            return True
    return False


def _build_machine_signin_receipt(
    *,
    child: Mapping[str, Any],
    run_id: str,
    request_id: str,
    tick: int,
    accepted_signin_return: Mapping[str, Any] | None,
    required_chain: list[str],
) -> dict[str, Any]:
    witness: dict[str, Any] = {}
    if isinstance(accepted_signin_return, Mapping):
        witness = {
            "path": accepted_signin_return.get("path"),
            "sha256": accepted_signin_return.get("sha256"),
        }
    base = {
        "schema_id": SIGNIN_SCHEMA_ID,
        "generated_by": "kernel.ion_kernel_fanout_smoke_noop",
        "worker_authored": False,
        "status": STATUS_ACK if _contains_machine_signin_requirement(required_chain) else STATUS_BLOCKED,
        "run_id": run_id,
        "request_id": request_id,
        "child_id": child.get("child_id"),
        "selected_model": child.get("model_move", {}).get("selected_model"),
        "selected_reasoning_effort": child.get("model_move", {}).get("selected_reasoning_effort"),
        "required_receipt_chain": required_chain,
        "required_context_reads": [
            {
                "kind": "accepted_machine_signin_return",
                "path": witness.get("path"),
                "sha256": witness.get("sha256"),
                "status": "READY" if witness.get("path") and witness.get("sha256") else "MISSING_OPTIONAL_WITNESS",
            }
        ],
        "authority_boundaries": {
            "production_authority": False,
            "live_execution_authority": False,
        },
        "started_at_tick": tick,
    }
    base["machine_attestation_sha256"] = _sha256_payload(base)
    return base


def simulate_kernel_fanout_noop_smoke(
    graph: Mapping[str, Any],
    *,
    child_durations: Mapping[str, int] | None = None,
    accepted_signin_return: Mapping[str, Any] | None = None,
    emitted_at: str | None = None,
) -> dict[str, Any]:
    """Simulate a bounded no-op run from a fan-out graph.

    The scheduler enforces dependencies, conflict locks, max parallel slots,
    and required machine-signin receipt gates without launching real workers.
    """

    plan = build_kernel_fanout_plan(graph, compact=True, emitted_at=emitted_at)
    child_rows = [_safe_child_row(row) for row in plan.get("children", [])]
    by_id = {row["child_id"]: row for row in child_rows}
    lock_index = _lock_index(plan)
    duration_map = {str(key): max(1, int(value)) for key, value in (child_durations or {}).items()}

    request_id = str(graph.get("request_id") or graph.get("parent_packet_id") or "fanout_noop_request")
    run_id = "fanout_noop_smoke_" + hashlib.sha256(
        f"{request_id}:{plan.get('plan_id')}".encode("utf-8", errors="replace")
    ).hexdigest()[:16]

    waiting = {row["child_id"] for row in child_rows}
    running: dict[str, int] = {}
    completed: set[str] = set()
    statuses: dict[str, dict[str, Any]] = {
        row["child_id"]: {
            "child_id": row["child_id"],
            "depends_on": list(row.get("depends_on", [])),
            "dependency_gate_initial": "open" if not row.get("depends_on") else "await_dependencies",
            "dependency_gate_open_tick": 0 if not row.get("depends_on") else None,
            "lock_blocked_ticks": [],
            "started_tick": None,
            "completed_tick": None,
            "state": "pending",
            "duration_steps": duration_map.get(row["child_id"], 1),
            "lease_receipt": None,
            "heartbeat_receipt": None,
            "machine_signin_receipt": None,
        }
        for row in child_rows
    }

    timeline: list[dict[str, Any]] = []
    heartbeat_events: list[dict[str, Any]] = []
    tick = 0
    max_parallel = int(plan.get("max_parallel", 1))

    while waiting or running:
        tick += 1

        ready = []
        for child_id in sorted(waiting):
            deps = list(by_id.get(child_id, {}).get("depends_on", []))
            if all(dep in completed for dep in deps):
                ready.append(child_id)
                if statuses[child_id]["dependency_gate_open_tick"] is None:
                    statuses[child_id]["dependency_gate_open_tick"] = tick

        slots = max(0, max_parallel - len(running))
        scheduled_this_tick: list[str] = []
        if slots > 0:
            for child_id in ready:
                if slots <= 0:
                    break
                conflicts = sorted(lock_index.get(child_id, set()))
                blocking = sorted(other for other in conflicts if other in running)
                if blocking:
                    statuses[child_id]["lock_blocked_ticks"].append(
                        {"tick": tick, "blocked_by": blocking}
                    )
                    timeline.append(
                        {
                            "tick": tick,
                            "event": "deferred_by_conflict_lock",
                            "child_id": child_id,
                            "blocked_by": blocking,
                        }
                    )
                    continue

                row = by_id[child_id]
                required_chain = list(row.get("required_receipt_chain", []))
                signin_receipt = _build_machine_signin_receipt(
                    child=row,
                    run_id=run_id,
                    request_id=request_id,
                    tick=tick,
                    accepted_signin_return=accepted_signin_return,
                    required_chain=required_chain,
                )
                if signin_receipt["status"] != STATUS_ACK:
                    statuses[child_id]["state"] = "blocked_missing_machine_signin_requirement"
                    waiting.remove(child_id)
                    timeline.append(
                        {
                            "tick": tick,
                            "event": "blocked_machine_signin_requirement",
                            "child_id": child_id,
                        }
                    )
                    continue

                duration_steps = int(statuses[child_id]["duration_steps"])
                running[child_id] = duration_steps
                waiting.remove(child_id)
                slots -= 1
                scheduled_this_tick.append(child_id)
                statuses[child_id]["state"] = "running"
                statuses[child_id]["started_tick"] = tick
                statuses[child_id]["machine_signin_receipt"] = signin_receipt
                statuses[child_id]["lease_receipt"] = {
                    "lease_id": row.get("lease", {}).get("lease_id"),
                    "lease_path": row.get("lease", {}).get("lease_path"),
                    "lease_seconds": row.get("lease", {}).get("lease_seconds"),
                    "issued_tick": tick,
                    "expires_after_tick": tick + max(1, duration_steps),
                    "status": "lease_active",
                }
                statuses[child_id]["heartbeat_receipt"] = {
                    "heartbeat_seconds": row.get("telemetry", {}).get("heartbeat_seconds"),
                    "stale_after_seconds": row.get("telemetry", {}).get("stale_after_seconds"),
                    "zombie_after_seconds": row.get("telemetry", {}).get("zombie_after_seconds"),
                    "states": row.get("telemetry", {}).get("states", ["live", "stale", "zombie"]),
                    "beats": [],
                }
                timeline.append({"tick": tick, "event": "started", "child_id": child_id})

        for child_id in sorted(list(running.keys())):
            running[child_id] -= 1
            heartbeat = statuses[child_id].get("heartbeat_receipt") or {"beats": []}
            beat = {"tick": tick, "status": "live"}
            heartbeat.setdefault("beats", []).append(beat)
            statuses[child_id]["heartbeat_receipt"] = heartbeat
            heartbeat_events.append({"child_id": child_id, **beat})

        completed_this_tick = [child_id for child_id, remaining in running.items() if remaining <= 0]
        for child_id in sorted(completed_this_tick):
            running.pop(child_id, None)
            completed.add(child_id)
            statuses[child_id]["state"] = "completed"
            statuses[child_id]["completed_tick"] = tick
            timeline.append({"tick": tick, "event": "completed", "child_id": child_id})

    child_results = [statuses[row["child_id"]] for row in child_rows]
    completed_children = sorted(
        row["child_id"] for row in child_results if row.get("state") == "completed"
    )
    blocked_children = sorted(
        row["child_id"] for row in child_results if str(row.get("state", "")).startswith("blocked_")
    )
    conflict_deferrals = [
        {
            "child_id": row["child_id"],
            "deferral_count": len(row.get("lock_blocked_ticks", [])),
            "deferrals": row.get("lock_blocked_ticks", []),
        }
        for row in child_results
        if row.get("lock_blocked_ticks")
    ]

    reducer_summary = {
        "mode": plan.get("reducer_settlement_plan", {}).get("mode"),
        "accept_requires": plan.get("reducer_settlement_plan", {}).get("accept_requires", []),
        "reject_if": plan.get("reducer_settlement_plan", {}).get("reject_if", []),
        "completed_children": completed_children,
        "blocked_children": blocked_children,
        "required_receipt_chain_complete": all(
            bool(row.get("machine_signin_receipt")) and row.get("state") == "completed"
            for row in child_results
            if row.get("state") != "blocked_missing_machine_signin_requirement"
        ),
        "verdict": "SMOKE_READY" if not blocked_children else "SMOKE_BLOCKED",
    }

    result = {
        "schema_id": SCHEMA_ID,
        "emitted_at": _now(),
        "run_id": run_id,
        "request_id": request_id,
        "plan_id": plan.get("plan_id"),
        "plan_verdict": plan.get("verdict"),
        "max_parallel": max_parallel,
        "child_count": len(child_rows),
        "parallel_observation": {
            "max_parallel_configured": max_parallel,
            "max_parallel_observed": max(
                [
                    sum(
                        1
                        for row in child_results
                        if row.get("started_tick") is not None
                        and row.get("completed_tick") is not None
                        and row["started_tick"] <= tick_idx <= row["completed_tick"]
                    )
                    for tick_idx in range(1, tick + 1)
                ]
                or [0]
            ),
        },
        "dependency_gate_observation": [
            {
                "child_id": row["child_id"],
                "depends_on": row["depends_on"],
                "dependency_gate_initial": row["dependency_gate_initial"],
                "dependency_gate_open_tick": row["dependency_gate_open_tick"],
            }
            for row in child_results
        ],
        "conflict_lock_observation": conflict_deferrals,
        "heartbeat_events": heartbeat_events,
        "children": child_results,
        "reducer_settlement_summary": reducer_summary,
        "production_authority": False,
        "live_execution_authority": False,
        "read_only_noop": True,
    }
    result["result_sha256"] = _sha256_payload(result)
    return result


def run_default_noop_parallel_smoke(
    *,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    accepted_signin_return: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute a compact default smoke scenario and persist JSON output."""

    graph = {
        "parent_packet_id": "PCKT-ION-KERNEL-FANOUT-SCHEDULER-PARALLEL-SMOKE-NOOP-20260514",
        "request_id": "codex_req_kernel_fanout_smoke_noop_20260514",
        "max_parallel": 2,
        "children": [
            {
                "child_id": "child_collect_a",
                "objective": "No-op child A.",
                "write_paths": [
                    "ION/05_context/current/kernel_fanout_scheduler/smoke_runs/noop_child_a.txt"
                ],
            },
            {
                "child_id": "child_collect_b",
                "objective": "No-op child B.",
                "write_paths": [
                    "ION/05_context/current/kernel_fanout_scheduler/smoke_runs/noop_child_b.txt"
                ],
            },
            {
                "child_id": "child_z_conflict_a",
                "objective": "No-op child conflicting with child_collect_a.",
                "write_paths": [
                    "ION/05_context/current/kernel_fanout_scheduler/smoke_runs/noop_child_a.txt"
                ],
            },
            {
                "child_id": "child_zz_after_b",
                "objective": "No-op child that depends on child_collect_b.",
                "depends_on": ["child_collect_b"],
                "write_paths": [
                    "ION/05_context/current/kernel_fanout_scheduler/smoke_runs/noop_child_after_b.txt"
                ],
            },
        ],
    }
    child_durations = {
        "child_collect_a": 3,
        "child_collect_b": 2,
        "child_z_conflict_a": 1,
        "child_zz_after_b": 1,
    }
    result = simulate_kernel_fanout_noop_smoke(
        graph,
        child_durations=child_durations,
        accepted_signin_return=accepted_signin_return,
    )

    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "fanout_noop_smoke_result_20260514.json"
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        "schema_id": "ion.kernel_fanout_noop_smoke_run_receipt.v1",
        "result": "NOOP_SMOKE_COMPLETED",
        "output_path": str(output_path.as_posix()),
        "result_sha256": result.get("result_sha256"),
        "production_authority": False,
        "live_execution_authority": False,
        "summary": {
            "max_parallel_observed": result.get("parallel_observation", {}).get("max_parallel_observed"),
            "completed_children": result.get("reducer_settlement_summary", {}).get("completed_children", []),
            "blocked_children": result.get("reducer_settlement_summary", {}).get("blocked_children", []),
        },
    }


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid payload: {path}")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run bounded no-op kernel fanout smoke harness.")
    parser.add_argument("--graph-json", help="Optional input graph JSON path")
    parser.add_argument("--output", help="Optional output path for smoke result JSON")
    parser.add_argument(
        "--accepted-signin-return",
        help="Optional accepted machine sign-in task return JSON path",
    )
    args = parser.parse_args(argv)

    accepted_signin_return = None
    if args.accepted_signin_return:
        accepted_signin_return = _read_json(Path(args.accepted_signin_return))

    if args.graph_json:
        graph = _read_json(Path(args.graph_json))
        result = simulate_kernel_fanout_noop_smoke(
            graph,
            accepted_signin_return=accepted_signin_return,
        )
        if args.output:
            Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        else:
            print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    receipt = run_default_noop_parallel_smoke(accepted_signin_return=accepted_signin_return)
    if args.output:
        Path(args.output).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
