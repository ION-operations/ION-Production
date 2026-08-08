"""ION candidate autonomous goal wakeup scheduler (wake-on-work, no idle burn)."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

GOAL_REGISTRY_REL = Path("ION/05_context/current/autonomous_goals/GOAL_REGISTRY.candidate.json")
SCHEDULER_HEALTH_REL = Path("ION/05_context/current/autonomous_goals/SCHEDULER_HEALTH.candidate.yaml")
SCHEDULER_STATE_REL = Path("ION/05_context/current/autonomous_goals/scheduler/last_tick.candidate.json")
WAKEUP_RECEIPTS_REL = Path("ION/05_context/current/autonomous_goals/wakeup_receipts")
WORKER_SHIFT_BOARD_REL = Path("ION/05_context/current/worker_shift/ACTIVE_WORKER_SHIFT_BOARD.json")
MEMBRANE_REL = Path(
    "ION/05_context/current/domain_weaver/candidate_founding_domains/"
    "domain.local_worker_scheduling_and_autonomous_loop/"
    "AUTONOMOUS_GOAL_WAKEUP_MEMBRANE.candidate.yaml"
)

OWNER_DOMAIN_ID = "domain.local_worker_scheduling_and_autonomous_loop"
OWNER_MOUNT_ID = "role_autonomous_loop_steward__domain_local_worker_scheduling_and_autonomous_loop"
MAX_ACTIVE_DETACHED = 3
MIN_HEALTH_TICK_SECONDS = 300
STALE_GOAL_THRESHOLD = timedelta(hours=24)

AUTHORITY_FALSE = {
    "accepted_state_authority": False,
    "live_execution_authority": False,
    "production_authority": False,
    "secrets_authority": False,
}

ACTIVATION_GATE = {
    "verdict": "ION_AUTONOMOUS_GOAL_WAKEUP_ACTIVATION_BLOCKED",
    "live_scheduler_start_requires": [
        "spawn_admission_verdict_runtime_carrier: allow",
        "live_execution_authority: true",
        "steward_or_operator_signed_activation_record: present",
        "goal_status: ready_for_wakeup for at least one bound goal",
    ],
    "current_lane_authority": AUTHORITY_FALSE.copy(),
    "candidate_mechanism_ready": True,
    "note": "Health tick and wakeup receipt preparation are permitted; detached worker spawn is not.",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _root(path: str | Path) -> Path:
    p = Path(path).expanduser().resolve()
    return p.parent if p.name == "ION" else p


def _sha(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _load_registry(shell: Path) -> dict[str, Any]:
    return _read_json(shell / GOAL_REGISTRY_REL)


def _active_worker_shift_count(shell: Path) -> int:
    board = _read_json(shell / WORKER_SHIFT_BOARD_REL)
    leases = board.get("active_leases") or []
    return len(leases) if isinstance(leases, list) else 0


def _goal_wake_reason(goal: Mapping[str, Any], *, now: datetime) -> str | None:
    status = str(goal.get("status") or "")
    if status in {"completed", "retired", "blocked_escalated"}:
        return None
    if status in {"ready_for_wakeup", "scheduled"}:
        return "lead_goal_chain_advance"
    blocking = goal.get("blocking_dependencies") or []
    if blocking and status == "admission_pending_dependencies":
        return None
    next_wakeup = _parse_ts(goal.get("next_wakeup_at"))
    if next_wakeup and next_wakeup <= now:
        return "scheduled_health_tick"
    last_wakeup = _parse_ts(goal.get("last_wakeup_at"))
    if last_wakeup and now - last_wakeup >= STALE_GOAL_THRESHOLD:
        return "stale_goal_threshold_exceeded"
    if goal.get("lease_id") is None and status in {"registered", "candidate_bound"}:
        return "dependency_cleared"
    return None


def _backoff_seconds(attempt: int) -> int:
    return min(300 * (2 ** max(0, attempt - 1)), 3600)


def evaluate_wakeup_candidates(
    *,
    ion_root: str | Path,
    trigger: str = "scheduled_health_tick",
) -> dict[str, Any]:
    shell = _root(ion_root)
    now = datetime.now(timezone.utc)
    registry = _load_registry(shell)
    goals = registry.get("goals") or []
    candidates: list[dict[str, Any]] = []
    stale_count = 0
    for goal in goals:
        if not isinstance(goal, dict):
            continue
        reason = _goal_wake_reason(goal, now=now)
        if reason is None:
            last = _parse_ts(goal.get("last_wakeup_at"))
            if last and now - last >= STALE_GOAL_THRESHOLD:
                stale_count += 1
            continue
        if trigger != "all" and reason != trigger and trigger not in {
            "scheduled_health_tick",
            "manual_evaluate",
        }:
            continue
        candidates.append(
            {
                "goal_id": goal.get("goal_id"),
                "wake_reason": reason,
                "owner_mount_id": goal.get("owner_mount_id"),
                "continuity_package_path": goal.get("continuity_package_path"),
                "carrier_class": goal.get("carrier_class", "cursor_agent"),
                "model_default": goal.get("model_default", "composer-2.5"),
                "status": goal.get("status"),
                "retry_backoff_seconds": _backoff_seconds(int(goal.get("wakeup_attempt_count") or 0)),
            }
        )
    active_shift = _active_worker_shift_count(shell)
    return {
        "evaluated_at": _now(),
        "owner_domain_id": OWNER_DOMAIN_ID,
        "trigger": trigger,
        "candidate_count": len(candidates),
        "candidates": candidates[:MAX_ACTIVE_DETACHED],
        "stale_goal_count": stale_count,
        "active_worker_shift_leases": active_shift,
        "detached_worker_count_within_bounds": len(candidates) <= MAX_ACTIVE_DETACHED,
        "activation_gate": ACTIVATION_GATE,
        "registry_path": str(GOAL_REGISTRY_REL),
        "registry_sha256": _sha(shell / GOAL_REGISTRY_REL),
    }


def prepare_wakeup_receipt(
    *,
    shell: Path,
    goal: Mapping[str, Any],
    wake_reason: str,
    tick_id: str,
) -> dict[str, Any]:
    goal_id = str(goal.get("goal_id") or "unknown")
    receipt_id = f"{tick_id}_{goal_id}_WAKEUP_PREPARE"
    return {
        "schema_id": "ion.autonomous_goals.wakeup_prepare_receipt.v0_1_candidate",
        "receipt_id": receipt_id,
        "created_at": _now(),
        "tick_id": tick_id,
        "goal_id": goal_id,
        "wake_reason": wake_reason,
        "owner_domain_id": goal.get("owner_domain_id", OWNER_DOMAIN_ID),
        "owner_mount_id": goal.get("owner_mount_id"),
        "continuity_package_path": goal.get("continuity_package_path"),
        "carrier_class": goal.get("carrier_class", "cursor_agent"),
        "model_default": goal.get("model_default", "composer-2.5"),
        "context_proof_required": True,
        "detached_worker_started": False,
        "worker_shift_lease_claimed": False,
        "activation_gate": ACTIVATION_GATE,
        "recovery": {
            "replay_from": goal.get("receipt_chain_ref"),
            "backoff_seconds": _backoff_seconds(int(goal.get("wakeup_attempt_count") or 0)),
        },
        "authority": AUTHORITY_FALSE.copy(),
        "non_claims": [
            "candidate_prepare_only",
            "no_detached_worker_spawn",
            "no_worker_shift_board_mutation",
        ],
    }


def _health_yaml(payload: Mapping[str, Any]) -> str:
    lines = [
        "schema_id: ion.autonomous_goals.scheduler_health.v0_1_candidate",
        f"generated_at: \"{payload['generated_at']}\"",
        f"owner_domain_id: {payload['owner_domain_id']}",
        f"owner_mount_id: {payload['owner_mount_id']}",
        "posture: candidate_only",
        "",
        "scheduler_status:",
        f"  verdict: {payload['scheduler_status']['verdict']}",
        f"  live_daemon_running: {str(payload['scheduler_status']['live_daemon_running']).lower()}",
        f"  last_tick_at: \"{payload['scheduler_status']['last_tick_at']}\"",
        f"  min_health_tick_seconds: {MIN_HEALTH_TICK_SECONDS}",
        "",
        "health_measures:",
    ]
    for key, value in payload["health_measures"].items():
        if isinstance(value, bool):
            lines.append(f"  {key}: {str(value).lower()}")
        else:
            lines.append(f"  {key}: {value}")
    lines.extend(
        [
            "",
            "activation_gate:",
            f"  verdict: {payload['activation_gate']['verdict']}",
            "  live_scheduler_start_requires:",
        ]
    )
    for req in payload["activation_gate"]["live_scheduler_start_requires"]:
        lines.append(f"    - {req}")
    lines.extend(
        [
            "",
            "health_reporting_targets:",
            "  - domain.local_worker_scheduling_and_autonomous_loop",
            "  - domain.swarm_scale_scheduling_and_workload_economics",
            "  - domain.current_phase_orchestration_management",
            "",
            "non_claims:",
            "  - candidate_only",
            "  - no_accepted_state",
            "  - health_emission_is_not_live_scheduler_operation",
        ]
    )
    return "\n".join(lines) + "\n"


def run_scheduler_tick(*, ion_root: str | Path, write: bool = False, trigger: str = "scheduled_health_tick") -> dict[str, Any]:
    shell = _root(ion_root)
    created_at = _now()
    tick_id = f"tick_{created_at.replace(':', '').replace('-', '')}"
    evaluation = evaluate_wakeup_candidates(ion_root=shell, trigger=trigger)
    registry = _load_registry(shell)
    goals_by_id = {g.get("goal_id"): g for g in (registry.get("goals") or []) if isinstance(g, dict)}
    wakeup_receipts: list[dict[str, Any]] = []
    for candidate in evaluation.get("candidates") or []:
        goal = goals_by_id.get(candidate.get("goal_id")) or candidate
        wakeup_receipts.append(
            prepare_wakeup_receipt(
                shell=shell,
                goal=goal,
                wake_reason=str(candidate.get("wake_reason")),
                tick_id=tick_id,
            )
        )

    goal_count = len(registry.get("goals") or [])
    bound_mount = (
        shell
        / "ION/05_context/current/codex_agent_mounts/"
        "role_autonomous_loop_steward__domain_local_worker_scheduling_and_autonomous_loop"
    ).is_dir()

    health_measures = {
        "goal_registered": goal_count > 0,
        "continuity_package_bound": any(
            g.get("continuity_package_path") for g in (registry.get("goals") or []) if isinstance(g, dict)
        ),
        "mount_materialized": bound_mount,
        "scheduler_tick_recent": True,
        "detached_worker_count_within_bounds": evaluation.get("detached_worker_count_within_bounds", True),
        "stale_goal_count": evaluation.get("stale_goal_count", 0),
        "crash_recovery_pending": 0,
        "wakeup_candidates_prepared": len(wakeup_receipts),
        "active_worker_shift_leases": evaluation.get("active_worker_shift_leases", 0),
    }

    result: dict[str, Any] = {
        "schema_id": "ion.autonomous_goals.scheduler_tick.v0_1_candidate",
        "tick_id": tick_id,
        "created_at": created_at,
        "owner_domain_id": OWNER_DOMAIN_ID,
        "owner_mount_id": OWNER_MOUNT_ID,
        "trigger": trigger,
        "scheduler_status": {
            "verdict": "candidate_mechanism_ready",
            "live_daemon_running": False,
            "last_tick_at": created_at,
        },
        "health_measures": health_measures,
        "evaluation": evaluation,
        "wakeup_receipts": [r["receipt_id"] for r in wakeup_receipts],
        "activation_gate": ACTIVATION_GATE,
        "membrane_ref": str(MEMBRANE_REL),
        "membrane_sha256": _sha(shell / MEMBRANE_REL),
        "write_performed": write,
        "authority": AUTHORITY_FALSE.copy(),
    }

    if write:
        _write_json(shell / SCHEDULER_STATE_REL, result)
        health_path = shell / SCHEDULER_HEALTH_REL
        health_path.parent.mkdir(parents=True, exist_ok=True)
        health_path.write_text(
            _health_yaml(
                {
                    "generated_at": created_at,
                    "owner_domain_id": OWNER_DOMAIN_ID,
                    "owner_mount_id": OWNER_MOUNT_ID,
                    "scheduler_status": result["scheduler_status"],
                    "health_measures": health_measures,
                    "activation_gate": ACTIVATION_GATE,
                }
            ),
            encoding="utf-8",
        )
        receipt_root = shell / WAKEUP_RECEIPTS_REL
        receipt_root.mkdir(parents=True, exist_ok=True)
        for receipt in wakeup_receipts:
            _write_json(receipt_root / f"{receipt['receipt_id']}.candidate.json", receipt)

        if registry:
            updated_goals = []
            for goal in registry.get("goals") or []:
                if not isinstance(goal, dict):
                    continue
                g = dict(goal)
                if any(r.get("goal_id") == g.get("goal_id") for r in wakeup_receipts):
                    g["last_wakeup_at"] = created_at
                    g["wakeup_attempt_count"] = int(g.get("wakeup_attempt_count") or 0) + 1
                    g["active_goal_bound"] = True
                    if g.get("status") == "registered":
                        g["status"] = "candidate_bound"
                updated_goals.append(g)
            registry = dict(registry)
            registry["goals"] = updated_goals
            registry["last_scheduler_tick_at"] = created_at
            registry["scheduler_owner_domain_id"] = OWNER_DOMAIN_ID
            _write_json(shell / GOAL_REGISTRY_REL, registry)

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Candidate autonomous goal wakeup scheduler tick.")
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--trigger", default="scheduled_health_tick")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = run_scheduler_tick(ion_root=args.ion_root, write=args.write, trigger=args.trigger)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["scheduler_status"]["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
