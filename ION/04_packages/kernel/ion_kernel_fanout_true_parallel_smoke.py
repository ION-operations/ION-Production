"""Bounded true-parallel no-op child-process smoke harness for kernel fan-out.

This harness is candidate/local only. It runs a tightly bounded local process smoke
with explicit caps and receipt emission; it does not launch Codex LLM workers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_kernel_fanout_plan import build_kernel_fanout_plan

SCHEMA_ID = "ion.kernel_fanout_true_parallel_smoke_result.v1"
RUN_RECEIPT_SCHEMA_ID = "ion.kernel_fanout_true_parallel_smoke_run_receipt.v1"
SIGNIN_SCHEMA_ID = "ion.worker_context_awareness_receipt.v1"
STATUS_ACK = "WORKER_CONTEXT_ACKNOWLEDGED"
STATUS_BLOCKED = "WORKER_CONTEXT_BLOCKED"
DEFAULT_OUTPUT_ROOT = Path("ION/05_context/current/kernel_fanout_scheduler/true_parallel_smoke_runs")
DEFAULT_RESULT_FILENAME = "fanout_true_parallel_smoke_result_20260514.json"
DEFAULT_PARENT_TIMEOUT_SECONDS = 120
MAX_PARENT_TIMEOUT_SECONDS = 180
DEFAULT_CHILD_TIMEOUT_SECONDS = 20
MAX_CHILD_TIMEOUT_SECONDS = 60
DEFAULT_POLL_SECONDS = 0.02
DEFAULT_HEARTBEAT_INTERVAL_SECONDS = 0.1
MAX_RUNNING_CHILDREN = 2
MAX_TOTAL_CHILDREN = 3
MAX_CONFLICT_DEFERRED_CHILDREN = 1


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha256_payload(payload: Mapping[str, Any]) -> str:
    material = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(material.encode("utf-8", errors="replace")).hexdigest()


def _safe_rel_path(value: Any) -> str | None:
    text = str(value or "").strip()
    if not text:
        return None
    candidate = Path(text)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    return candidate.as_posix()


def _safe_child_row(raw: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "child_id": str(raw.get("child_id") or ""),
        "depends_on": [str(dep) for dep in raw.get("depends_on", [])],
        "write_paths": [str(path) for path in raw.get("write_paths", [])],
        "lease": dict(raw.get("lease") or {}),
        "telemetry": dict(raw.get("telemetry") or {}),
        "artifacts": dict(raw.get("artifacts") or {}),
        "required_receipt_chain": [str(item) for item in raw.get("required_receipt_chain", [])],
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
    accepted_signin_return: Mapping[str, Any] | None,
    required_chain: list[str],
) -> dict[str, Any]:
    witness: dict[str, Any] = {}
    if isinstance(accepted_signin_return, Mapping):
        witness = {
            "path": accepted_signin_return.get("path"),
            "sha256": accepted_signin_return.get("sha256"),
        }
    receipt = {
        "schema_id": SIGNIN_SCHEMA_ID,
        "generated_by": "kernel.ion_kernel_fanout_true_parallel_smoke",
        "simulated_machine_receipt": True,
        "worker_authored": False,
        "status": STATUS_ACK if _contains_machine_signin_requirement(required_chain) else STATUS_BLOCKED,
        "run_id": run_id,
        "request_id": request_id,
        "child_id": child.get("child_id"),
        "selected_model": child.get("model_move", {}).get("selected_model"),
        "selected_reasoning_effort": child.get("model_move", {}).get("selected_reasoning_effort"),
        "required_receipt_chain": list(required_chain),
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
        "generated_at": _now(),
    }
    receipt["machine_attestation_sha256"] = _sha256_payload(receipt)
    return receipt


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_noop_child(
    *,
    child_id: str,
    duration_seconds: float,
    heartbeat_interval_seconds: float,
    event_queue: mp.Queue,
) -> None:
    started_mono = time.monotonic()
    started_at = _now()
    heartbeat_count = 0
    try:
        event_queue.put(
            {
                "event": "child_started",
                "child_id": child_id,
                "started_at": started_at,
                "started_monotonic": started_mono,
            }
        )
        deadline = started_mono + max(0.05, duration_seconds)
        while True:
            now_mono = time.monotonic()
            if now_mono >= deadline:
                break
            sleep_for = min(max(0.01, heartbeat_interval_seconds), max(0.0, deadline - now_mono))
            time.sleep(sleep_for)
            heartbeat_count += 1
            event_queue.put(
                {
                    "event": "heartbeat",
                    "child_id": child_id,
                    "beat_index": heartbeat_count,
                    "at": _now(),
                    "monotonic": time.monotonic(),
                    "status": "live",
                }
            )
        completed_mono = time.monotonic()
        event_queue.put(
            {
                "event": "child_completed",
                "child_id": child_id,
                "completed_at": _now(),
                "completed_monotonic": completed_mono,
                "started_monotonic": started_mono,
                "heartbeat_count": heartbeat_count,
            }
        )
    except BaseException as exc:  # pragma: no cover - defensive capture
        event_queue.put(
            {
                "event": "child_error",
                "child_id": child_id,
                "error": repr(exc),
                "at": _now(),
            }
        )


def _default_graph(*, artifact_root: str) -> dict[str, Any]:
    return {
        "parent_packet_id": "PCKT-ION-KERNEL-FANOUT-SCHEDULER-TRUE-PARALLEL-WORKER-SMOKE-BOUNDED-20260514",
        "request_id": "codex_req_kernel_fanout_true_parallel_smoke_20260514",
        "max_parallel": 2,
        "artifact_root": artifact_root,
        "children": [
            {
                "child_id": "child_alpha",
                "objective": "Safe no-op child alpha.",
                "write_paths": [f"{artifact_root}/outputs/alpha.txt"],
                "heartbeat_seconds": 1,
            },
            {
                "child_id": "child_beta",
                "objective": "Safe no-op child beta.",
                "write_paths": [f"{artifact_root}/outputs/beta.txt"],
                "heartbeat_seconds": 1,
            },
            {
                "child_id": "child_alpha_conflict",
                "objective": "Safe no-op child conflict blocked/deferred by lock while alpha runs.",
                "depends_on": ["child_beta"],
                "write_paths": [f"{artifact_root}/outputs/alpha.txt"],
                "heartbeat_seconds": 1,
            },
        ],
    }


def _persist_child_receipts(
    *,
    repo_root: Path,
    status_row: dict[str, Any],
    receipt_root_override: Path | None,
) -> None:
    child_id = str(status_row.get("child_id") or "unknown_child")
    lease_receipt = dict(status_row.get("lease_receipt") or {})
    heartbeat_receipt = dict(status_row.get("heartbeat_receipt") or {})
    signin_receipt = dict(status_row.get("machine_signin_receipt") or {})

    if receipt_root_override is not None:
        child_dir = receipt_root_override / child_id
        _write_json(child_dir / "lease.json", lease_receipt)
        _write_json(child_dir / "heartbeat.json", heartbeat_receipt)
        _write_json(child_dir / "worker_context_awareness_receipt.json", signin_receipt)
        status_row["lease_receipt_path"] = (child_dir / "lease.json").as_posix()
        status_row["heartbeat_receipt_path"] = (child_dir / "heartbeat.json").as_posix()
        status_row["machine_signin_receipt_path"] = (
            child_dir / "worker_context_awareness_receipt.json"
        ).as_posix()
        return

    lease_rel = _safe_rel_path(lease_receipt.get("lease_path"))
    if lease_rel:
        _write_json(repo_root / lease_rel, lease_receipt)
        status_row["lease_receipt_path"] = lease_rel
    heartbeat_rel = _safe_rel_path(heartbeat_receipt.get("heartbeat_path"))
    if heartbeat_rel:
        _write_json(repo_root / heartbeat_rel, heartbeat_receipt)
        status_row["heartbeat_receipt_path"] = heartbeat_rel
    signin_rel = _safe_rel_path(signin_receipt.get("receipt_path"))
    if signin_rel:
        _write_json(repo_root / signin_rel, signin_receipt)
        status_row["machine_signin_receipt_path"] = signin_rel


def simulate_kernel_fanout_true_parallel_smoke(
    graph: Mapping[str, Any],
    *,
    child_durations_seconds: Mapping[str, float] | None = None,
    child_timeout_seconds: int = DEFAULT_CHILD_TIMEOUT_SECONDS,
    parent_timeout_seconds: int = DEFAULT_PARENT_TIMEOUT_SECONDS,
    heartbeat_interval_seconds: float = DEFAULT_HEARTBEAT_INTERVAL_SECONDS,
    accepted_signin_return: Mapping[str, Any] | None = None,
    emitted_at: str | None = None,
    receipt_root_override: Path | None = None,
) -> dict[str, Any]:
    """Run bounded true parallel no-op local child processes from a fan-out graph."""

    if child_timeout_seconds < 1 or child_timeout_seconds > MAX_CHILD_TIMEOUT_SECONDS:
        raise ValueError(f"child_timeout_seconds must be within 1..{MAX_CHILD_TIMEOUT_SECONDS}")
    if parent_timeout_seconds < 1 or parent_timeout_seconds > MAX_PARENT_TIMEOUT_SECONDS:
        raise ValueError(f"parent_timeout_seconds must be within 1..{MAX_PARENT_TIMEOUT_SECONDS}")

    plan = build_kernel_fanout_plan(graph, compact=True, emitted_at=emitted_at)
    child_rows = [_safe_child_row(row) for row in plan.get("children", [])]
    by_id = {row["child_id"]: row for row in child_rows}
    lock_index = _lock_index(plan)

    request_id = str(graph.get("request_id") or graph.get("parent_packet_id") or "fanout_true_parallel_request")
    run_id = "fanout_true_parallel_smoke_" + hashlib.sha256(
        f"{request_id}:{plan.get('plan_id')}".encode("utf-8", errors="replace")
    ).hexdigest()[:16]

    findings: list[dict[str, Any]] = []
    if len(child_rows) > MAX_TOTAL_CHILDREN:
        findings.append(
            {
                "code": "child_count_over_cap",
                "severity": "blocked",
                "message": f"child_count={len(child_rows)} exceeds cap {MAX_TOTAL_CHILDREN}",
            }
        )
    if int(plan.get("max_parallel", 1)) > MAX_RUNNING_CHILDREN:
        findings.append(
            {
                "code": "max_parallel_over_cap",
                "severity": "blocked",
                "message": f"max_parallel={plan.get('max_parallel')} exceeds cap {MAX_RUNNING_CHILDREN}",
            }
        )

    max_parallel = min(MAX_RUNNING_CHILDREN, int(plan.get("max_parallel", 1)))

    statuses: dict[str, dict[str, Any]] = {
        row["child_id"]: {
            "child_id": row["child_id"],
            "depends_on": list(row.get("depends_on", [])),
            "dependency_gate_initial": "open" if not row.get("depends_on") else "await_dependencies",
            "dependency_gate_open_at": _now() if not row.get("depends_on") else None,
            "state": "pending",
            "started_at": None,
            "completed_at": None,
            "started_monotonic": None,
            "completed_monotonic": None,
            "lock_blocked_events": [],
            "lease_receipt": None,
            "heartbeat_receipt": None,
            "machine_signin_receipt": None,
        }
        for row in child_rows
    }

    if plan.get("verdict") != "ION_KERNEL_FANOUT_PLAN_READY":
        findings.append(
            {
                "code": "plan_not_ready",
                "severity": "blocked",
                "message": "fanout plan is blocked; true parallel smoke not executed",
            }
        )

    if any(item.get("severity") == "blocked" for item in findings):
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
                "max_parallel_observed": 0,
                "overlap_seconds": 0.0,
            },
            "children": [statuses[row["child_id"]] for row in child_rows],
            "timeline": [],
            "heartbeat_events": [],
            "conflict_lock_observation": [],
            "dependency_gate_observation": [
                {
                    "child_id": row["child_id"],
                    "depends_on": list(statuses[row["child_id"]]["depends_on"]),
                    "dependency_gate_initial": statuses[row["child_id"]]["dependency_gate_initial"],
                    "dependency_gate_open_at": statuses[row["child_id"]]["dependency_gate_open_at"],
                }
                for row in child_rows
            ],
            "reducer_settlement_summary": {
                "verdict": "SMOKE_BLOCKED",
                "blocked_children": sorted(row["child_id"] for row in child_rows),
                "completed_children": [],
                "required_receipt_chain_complete": False,
            },
            "blocked_findings": findings,
            "production_authority": False,
            "live_execution_authority": False,
            "read_only_noop": True,
            "true_parallel_harness": True,
        }
        result["result_sha256"] = _sha256_payload(result)
        return result

    repo_root = Path.cwd()
    durations = {
        str(key): max(0.05, float(value))
        for key, value in (child_durations_seconds or {}).items()
    }
    event_queue: mp.Queue = mp.Queue()
    waiting = {row["child_id"] for row in child_rows}
    running: dict[str, dict[str, Any]] = {}
    completed: set[str] = set()
    timeline: list[dict[str, Any]] = []
    heartbeat_events: list[dict[str, Any]] = []
    max_parallel_observed = 0

    parent_deadline = time.monotonic() + float(parent_timeout_seconds)

    def drain_events() -> None:
        while True:
            try:
                event = event_queue.get_nowait()
            except Exception:
                break
            child_id = str(event.get("child_id") or "")
            if child_id not in statuses:
                continue
            state = statuses[child_id]
            event_name = str(event.get("event") or "")
            if event_name == "child_started":
                state["started_at"] = event.get("started_at")
                state["started_monotonic"] = event.get("started_monotonic")
                timeline.append({"event": "child_started", "child_id": child_id, "at": state["started_at"]})
            elif event_name == "heartbeat":
                beat = {
                    "beat_index": int(event.get("beat_index") or 0),
                    "at": event.get("at"),
                    "status": str(event.get("status") or "live"),
                    "monotonic": float(event.get("monotonic") or 0.0),
                }
                heartbeat = state.get("heartbeat_receipt") or {"beats": []}
                heartbeat.setdefault("beats", []).append(beat)
                state["heartbeat_receipt"] = heartbeat
                heartbeat_events.append({"child_id": child_id, **beat})
            elif event_name == "child_completed":
                state["completed_at"] = event.get("completed_at")
                state["completed_monotonic"] = event.get("completed_monotonic")
                if state.get("started_monotonic") is None:
                    state["started_monotonic"] = event.get("started_monotonic")
                state["state"] = "completed"
                completed.add(child_id)
                timeline.append({"event": "child_completed", "child_id": child_id, "at": state["completed_at"]})
            elif event_name == "child_error":
                state["state"] = "blocked_child_error"
                state["error"] = event.get("error")
                timeline.append({"event": "child_error", "child_id": child_id, "at": event.get("at")})

    while waiting or running:
        drain_events()

        now_mono = time.monotonic()
        if now_mono > parent_deadline:
            findings.append(
                {
                    "code": "parent_timeout",
                    "severity": "blocked",
                    "message": f"parent_timeout_seconds={parent_timeout_seconds} exceeded",
                }
            )
            for child_id, proc_meta in list(running.items()):
                process = proc_meta["process"]
                if process.is_alive():
                    process.terminate()
                    process.join(timeout=1)
                statuses[child_id]["state"] = "blocked_parent_timeout"
            running.clear()
            break

        ready_children = []
        for child_id in sorted(waiting):
            deps = list(by_id[child_id].get("depends_on", []))
            if all(dep in completed for dep in deps):
                ready_children.append(child_id)
                if statuses[child_id]["dependency_gate_open_at"] is None:
                    statuses[child_id]["dependency_gate_open_at"] = _now()

        slots = max(0, max_parallel - len(running))
        for child_id in ready_children:
            if slots <= 0:
                break
            blocking = sorted(other for other in lock_index.get(child_id, set()) if other in running)
            if blocking:
                statuses[child_id]["lock_blocked_events"].append(
                    {
                        "at": _now(),
                        "blocked_by": blocking,
                    }
                )
                timeline.append(
                    {
                        "event": "deferred_by_conflict_lock",
                        "child_id": child_id,
                        "blocked_by": blocking,
                        "at": _now(),
                    }
                )
                continue

            child_row = by_id[child_id]
            required_chain = list(child_row.get("required_receipt_chain", []))
            machine_signin_receipt = _build_machine_signin_receipt(
                child=child_row,
                run_id=run_id,
                request_id=request_id,
                accepted_signin_return=accepted_signin_return,
                required_chain=required_chain,
            )
            if machine_signin_receipt["status"] != STATUS_ACK:
                statuses[child_id]["state"] = "blocked_missing_machine_signin_requirement"
                waiting.remove(child_id)
                timeline.append(
                    {
                        "event": "blocked_machine_signin_requirement",
                        "child_id": child_id,
                        "at": _now(),
                    }
                )
                continue

            duration_seconds = durations.get(child_id, 1.2)
            lease = dict(child_row.get("lease") or {})
            lease_receipt = {
                "schema_id": "ion.kernel_fanout_child_lease_receipt.v1",
                "run_id": run_id,
                "child_id": child_id,
                "lease_id": lease.get("lease_id"),
                "lease_seconds": min(MAX_CHILD_TIMEOUT_SECONDS, int(lease.get("lease_seconds") or child_timeout_seconds)),
                "lease_path": lease.get("lease_path"),
                "issued_at": _now(),
                "status": "lease_active",
            }
            artifacts = dict(child_row.get("artifacts") or {})
            heartbeat_receipt = {
                "schema_id": "ion.kernel_fanout_child_heartbeat_receipt.v1",
                "run_id": run_id,
                "child_id": child_id,
                "heartbeat_seconds": child_row.get("telemetry", {}).get("heartbeat_seconds"),
                "stale_after_seconds": child_row.get("telemetry", {}).get("stale_after_seconds"),
                "zombie_after_seconds": child_row.get("telemetry", {}).get("zombie_after_seconds"),
                "heartbeat_path": f"{Path(str(artifacts.get('worker_context_awareness_receipt_path') or 'artifact')).parent.as_posix()}/heartbeat.json",
                "beats": [],
            }
            machine_signin_receipt["receipt_path"] = artifacts.get("worker_context_awareness_receipt_path")

            process = mp.Process(
                target=_run_noop_child,
                kwargs={
                    "child_id": child_id,
                    "duration_seconds": duration_seconds,
                    "heartbeat_interval_seconds": heartbeat_interval_seconds,
                    "event_queue": event_queue,
                },
                daemon=True,
            )
            process.start()

            statuses[child_id]["state"] = "running"
            statuses[child_id]["lease_receipt"] = lease_receipt
            statuses[child_id]["heartbeat_receipt"] = heartbeat_receipt
            statuses[child_id]["machine_signin_receipt"] = machine_signin_receipt

            running[child_id] = {
                "process": process,
                "deadline": time.monotonic() + min(float(child_timeout_seconds), MAX_CHILD_TIMEOUT_SECONDS),
            }
            waiting.remove(child_id)
            slots -= 1
            timeline.append({"event": "spawned", "child_id": child_id, "at": _now()})

        for child_id in list(running.keys()):
            proc_meta = running[child_id]
            process = proc_meta["process"]
            deadline = float(proc_meta["deadline"])
            if process.is_alive() and time.monotonic() > deadline:
                process.terminate()
                process.join(timeout=1)
                statuses[child_id]["state"] = "blocked_child_timeout"
                statuses[child_id]["completed_at"] = _now()
                findings.append(
                    {
                        "code": "child_timeout",
                        "severity": "blocked",
                        "child_id": child_id,
                        "message": f"child exceeded timeout cap {child_timeout_seconds}s",
                    }
                )
                running.pop(child_id, None)
                continue
            if not process.is_alive():
                process.join(timeout=1)
                running.pop(child_id, None)

        max_parallel_observed = max(max_parallel_observed, len(running))
        time.sleep(DEFAULT_POLL_SECONDS)

    drain_events()

    for child_id, state in statuses.items():
        if state.get("state") == "running":
            state["state"] = "blocked_unsettled"
        if state.get("state") == "pending":
            state["state"] = "blocked_not_scheduled"
        if state.get("heartbeat_receipt") is None:
            state["heartbeat_receipt"] = {
                "schema_id": "ion.kernel_fanout_child_heartbeat_receipt.v1",
                "run_id": run_id,
                "child_id": child_id,
                "beats": [],
            }
        if state.get("lease_receipt") is None:
            state["lease_receipt"] = {
                "schema_id": "ion.kernel_fanout_child_lease_receipt.v1",
                "run_id": run_id,
                "child_id": child_id,
                "status": "not_issued",
            }
        if state.get("machine_signin_receipt") is None:
            state["machine_signin_receipt"] = {
                "schema_id": SIGNIN_SCHEMA_ID,
                "run_id": run_id,
                "child_id": child_id,
                "status": STATUS_BLOCKED,
            }

    child_results = [statuses[row["child_id"]] for row in child_rows]
    for row in child_results:
        _persist_child_receipts(
            repo_root=repo_root,
            status_row=row,
            receipt_root_override=receipt_root_override,
        )

    started_windows = [
        (
            float(row.get("started_monotonic")),
            float(row.get("completed_monotonic")),
        )
        for row in child_results
        if row.get("started_monotonic") is not None and row.get("completed_monotonic") is not None
    ]
    overlap_seconds = 0.0
    if len(started_windows) >= 2:
        started_windows.sort(key=lambda item: item[0])
        first = started_windows[0]
        second = started_windows[1]
        overlap_seconds = max(0.0, min(first[1], second[1]) - max(first[0], second[0]))

    conflict_lock_observation = [
        {
            "child_id": row["child_id"],
            "deferral_count": len(row.get("lock_blocked_events", [])),
            "deferrals": row.get("lock_blocked_events", []),
        }
        for row in child_results
        if row.get("lock_blocked_events")
    ]
    deferred_children = [item["child_id"] for item in conflict_lock_observation if item.get("deferral_count", 0) > 0]
    if len(deferred_children) > MAX_CONFLICT_DEFERRED_CHILDREN:
        findings.append(
            {
                "code": "too_many_conflict_deferred_children",
                "severity": "blocked",
                "message": (
                    f"deferred_children={len(deferred_children)} exceeds cap "
                    f"{MAX_CONFLICT_DEFERRED_CHILDREN}"
                ),
            }
        )

    completed_children = sorted(row["child_id"] for row in child_results if row.get("state") == "completed")
    blocked_children = sorted(
        row["child_id"]
        for row in child_results
        if str(row.get("state", "")).startswith("blocked")
    )

    settlement_verdict = "SMOKE_READY"
    if blocked_children or any(item.get("severity") == "blocked" for item in findings):
        settlement_verdict = "SMOKE_BLOCKED"

    reducer_summary = {
        "mode": plan.get("reducer_settlement_plan", {}).get("mode"),
        "accept_requires": plan.get("reducer_settlement_plan", {}).get("accept_requires", []),
        "reject_if": plan.get("reducer_settlement_plan", {}).get("reject_if", []),
        "completed_children": completed_children,
        "blocked_children": blocked_children,
        "required_receipt_chain_complete": all(
            row.get("machine_signin_receipt", {}).get("status") == STATUS_ACK for row in child_results
        ),
        "conflict_deferred_children": deferred_children,
        "verdict": settlement_verdict,
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
            "max_parallel_observed": max_parallel_observed,
            "overlap_seconds": round(overlap_seconds, 4),
        },
        "dependency_gate_observation": [
            {
                "child_id": row["child_id"],
                "depends_on": row["depends_on"],
                "dependency_gate_initial": statuses[row["child_id"]]["dependency_gate_initial"],
                "dependency_gate_open_at": statuses[row["child_id"]]["dependency_gate_open_at"],
            }
            for row in child_rows
        ],
        "conflict_lock_observation": conflict_lock_observation,
        "heartbeat_events": heartbeat_events,
        "timeline": timeline,
        "children": child_results,
        "reducer_settlement_summary": reducer_summary,
        "blocked_findings": findings,
        "production_authority": False,
        "live_execution_authority": False,
        "read_only_noop": True,
        "true_parallel_harness": True,
        "timeouts": {
            "parent_timeout_seconds": parent_timeout_seconds,
            "child_timeout_seconds": child_timeout_seconds,
            "max_parent_timeout_seconds": MAX_PARENT_TIMEOUT_SECONDS,
            "max_child_timeout_seconds": MAX_CHILD_TIMEOUT_SECONDS,
        },
    }
    result["result_sha256"] = _sha256_payload(result)
    return result


def run_default_true_parallel_smoke(
    *,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    accepted_signin_return: Mapping[str, Any] | None = None,
    child_timeout_seconds: int = DEFAULT_CHILD_TIMEOUT_SECONDS,
    parent_timeout_seconds: int = DEFAULT_PARENT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Run the default bounded true-parallel smoke and persist compact artifacts."""

    output_root.mkdir(parents=True, exist_ok=True)
    artifact_root = "ION/05_context/current/kernel_fanout_scheduler/true_parallel_smoke_runs/fanout_true_parallel_smoke_20260514"
    graph = _default_graph(artifact_root=artifact_root)
    result = simulate_kernel_fanout_true_parallel_smoke(
        graph,
        child_durations_seconds={
            "child_alpha": 1.2,
            "child_beta": 0.8,
            "child_alpha_conflict": 0.5,
        },
        child_timeout_seconds=child_timeout_seconds,
        parent_timeout_seconds=parent_timeout_seconds,
        heartbeat_interval_seconds=0.1,
        accepted_signin_return=accepted_signin_return,
        receipt_root_override=output_root / "child_receipts",
    )

    output_path = output_root / DEFAULT_RESULT_FILENAME
    _write_json(output_path, result)

    return {
        "schema_id": RUN_RECEIPT_SCHEMA_ID,
        "result": "TRUE_PARALLEL_SMOKE_COMPLETED" if result["reducer_settlement_summary"]["verdict"] == "SMOKE_READY" else "TRUE_PARALLEL_SMOKE_BLOCKED",
        "output_path": output_path.as_posix(),
        "result_sha256": result.get("result_sha256"),
        "production_authority": False,
        "live_execution_authority": False,
        "summary": {
            "max_parallel_observed": result.get("parallel_observation", {}).get("max_parallel_observed"),
            "overlap_seconds": result.get("parallel_observation", {}).get("overlap_seconds"),
            "conflict_deferred_children": result.get("reducer_settlement_summary", {}).get("conflict_deferred_children", []),
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
    parser = argparse.ArgumentParser(description="Run bounded true-parallel kernel fanout smoke harness.")
    parser.add_argument("--graph-json", help="Optional input graph JSON path")
    parser.add_argument("--output", help="Optional output path for smoke result JSON or run receipt")
    parser.add_argument("--accepted-signin-return", help="Optional accepted machine sign-in task return JSON path")
    parser.add_argument("--child-timeout-seconds", type=int, default=DEFAULT_CHILD_TIMEOUT_SECONDS)
    parser.add_argument("--parent-timeout-seconds", type=int, default=DEFAULT_PARENT_TIMEOUT_SECONDS)
    args = parser.parse_args(argv)

    accepted_signin_return = None
    if args.accepted_signin_return:
        accepted_signin_return = _read_json(Path(args.accepted_signin_return))

    if args.graph_json:
        graph = _read_json(Path(args.graph_json))
        result = simulate_kernel_fanout_true_parallel_smoke(
            graph,
            accepted_signin_return=accepted_signin_return,
            child_timeout_seconds=args.child_timeout_seconds,
            parent_timeout_seconds=args.parent_timeout_seconds,
        )
        payload = result
    else:
        payload = run_default_true_parallel_smoke(
            accepted_signin_return=accepted_signin_return,
            child_timeout_seconds=args.child_timeout_seconds,
            parent_timeout_seconds=args.parent_timeout_seconds,
        )

    if args.output:
        Path(args.output).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
