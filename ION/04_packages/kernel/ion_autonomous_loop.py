"""ION V101 local autonomous-loop survival slice."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from .ion_autonomous_goal_wakeup import run_scheduler_tick
from .ion_steward_integrate import steward_integrate_return
from .ion_template_action_gate import evaluate_template_action_proof
from .ion_context_lifecycle import build_context_lifecycle_report, context_lifecycle_report_to_dict, write_context_lifecycle_report

LAST_RESULT_REL = Path("ION/05_context/current/LAST_ION_AUTONOMOUS_LOOP_RESULT.json")
COCKPIT_REL = Path("ION/05_context/current/ACTIVE_COCKPIT_VIEW_MODEL.json")
RUN_ROOT_REL = Path("ION/05_context/current/autonomous_loop")
LEAD_DEV_CONTEXT_REL = Path("ION/05_context/current/agent_context_systems/LEAD_DEV_ACTIVE_CONTEXT_PACKAGE_V101.md")
IDLE_STREAK_REL = Path("ION/05_context/current/autonomous_loop/LOOP_IDLE_STREAK.candidate.json")
IDLE_ABSENCE_ALERT_REL = Path(
    "ION/05_context/current/autonomous_loop/LOOP_IDLE_ABSENCE_ALERT.candidate.json"
)
DEFAULT_MAX_STEPS = 3
MAX_MAX_STEPS = 32
IDLE_ABSENCE_ALERT_THRESHOLD = 3


def _bound_max_steps(max_steps: int) -> int:
    if max_steps < 1:
        return DEFAULT_MAX_STEPS
    return min(int(max_steps), MAX_MAX_STEPS)


def _load_idle_streak(shell: Path) -> dict[str, Any]:
    path = shell / IDLE_STREAK_REL
    if not path.is_file():
        return {
            "schema_id": "ion.autonomous_loop_idle_streak.v0_1_candidate",
            "consecutive_idle_cycles": 0,
            "last_cycle_id": None,
            "last_updated_at": None,
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {
            "schema_id": "ion.autonomous_loop_idle_streak.v0_1_candidate",
            "consecutive_idle_cycles": 0,
            "last_cycle_id": None,
            "last_updated_at": None,
        }
    if not isinstance(data, dict):
        data = {}
    return {
        "schema_id": "ion.autonomous_loop_idle_streak.v0_1_candidate",
        "consecutive_idle_cycles": int(data.get("consecutive_idle_cycles") or 0),
        "last_cycle_id": data.get("last_cycle_id"),
        "last_updated_at": data.get("last_updated_at"),
    }


def update_loop_idle_streak(
    shell: Path,
    *,
    cycle_id: str,
    integrated: int,
    stop_reason: str,
    write: bool,
    created_at: str,
) -> dict[str, Any]:
    """Track consecutive NO_ACCEPTED_LOCAL_DELTA cycles; emit report-only absence alert at threshold."""
    streak = _load_idle_streak(shell)
    if integrated > 0:
        streak["consecutive_idle_cycles"] = 0
    elif stop_reason == "NO_ACCEPTED_LOCAL_DELTA":
        streak["consecutive_idle_cycles"] = int(streak.get("consecutive_idle_cycles") or 0) + 1
    streak["last_cycle_id"] = cycle_id
    streak["last_updated_at"] = created_at
    alert_active = streak["consecutive_idle_cycles"] >= IDLE_ABSENCE_ALERT_THRESHOLD
    alert_payload: dict[str, Any] | None = None
    if alert_active:
        alert_payload = {
            "schema_id": "ion.autonomous_loop_idle_absence_alert.v0_1_candidate",
            "evaluated_at": created_at,
            "finding_code": "FINDING_AUTONOMOUS_LOOP_CONSECUTIVE_IDLE_CYCLES",
            "consecutive_idle_cycles": streak["consecutive_idle_cycles"],
            "threshold": IDLE_ABSENCE_ALERT_THRESHOLD,
            "stop_reason": stop_reason,
            "report_only": True,
            "detects_absence": True,
        }
    if write:
        streak_path = shell / IDLE_STREAK_REL
        _write_json(streak_path, streak)
        alert_path = shell / IDLE_ABSENCE_ALERT_REL
        if alert_payload:
            _write_json(alert_path, alert_payload)
        elif alert_path.is_file():
            _write_json(
                alert_path,
                {
                    "schema_id": "ion.autonomous_loop_idle_absence_alert.v0_1_candidate",
                    "evaluated_at": created_at,
                    "alert_active": False,
                    "consecutive_idle_cycles": streak["consecutive_idle_cycles"],
                    "threshold": IDLE_ABSENCE_ALERT_THRESHOLD,
                    "report_only": True,
                },
            )
    return {
        "consecutive_idle_cycles": streak["consecutive_idle_cycles"],
        "absence_alert_active": alert_active,
        "absence_alert": alert_payload,
        "idle_streak_path": str(IDLE_STREAK_REL),
    }

def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _root(path: str | Path) -> Path:
    p = Path(path).expanduser().resolve()
    return p.parent if p.name == "ION" else p

def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:64] or "cycle"

def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")

def _sha(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _context_lifecycle_status(shell: Path) -> dict[str, Any]:
    report = build_context_lifecycle_report(shell)
    data = context_lifecycle_report_to_dict(report)
    return {
        "verdict": data.get("verdict"),
        "findings": data.get("findings", []),
        "total_context_bytes": data.get("total_context_bytes"),
        "hot_bytes": data.get("hot_bytes"),
        "warm_bytes": data.get("warm_bytes"),
        "cold_bytes": data.get("cold_bytes"),
        "quarantine_candidate_bytes": data.get("quarantine_candidate_bytes"),
        "template_proposal_bytes": data.get("template_proposal_bytes"),
        "execution_cycle_bytes": data.get("execution_cycle_bytes"),
        "mutation_performed": data.get("mutation_performed"),
    }


def _context_lines(shell: Path) -> str:
    rels = [
        "ION/REPO_AUTHORITY.md",
        "ION/05_context/current/PRODUCTIZED_RUNTIME_MANIFEST_V96.json",
        "ION/05_context/current/PRODUCTIZED_RUNTIME_MANIFEST_V100.json",
        "ION/05_context/current/ION_RUNTIME_SEPARATION_PLAN_V99.json",
        "ION/02_architecture/ION_AGENT_CONTEXT_CONTINUITY_TIMELINE_AND_ROUTE_MAP_PROTOCOL.md",
        "ION/02_architecture/ION_LIVING_ENCYCLOPEDIA_MAINTENANCE_PROTOCOL.md",
        "ION/02_architecture/ION_CONTEXT_METABOLISM_AND_LIFECYCLE_PROTOCOL.md",
        "ION/05_context/current/CONTEXT_LIFECYCLE_AUDIT_V102.json",
    ]
    lines: list[str] = []
    for rel in rels:
        path = shell / rel
        excerpt = ""
        if path.is_file():
            excerpt = path.read_text(encoding="utf-8", errors="replace")[:180].replace("\n", " ")
        lines.append(f"- {rel} | exists={path.exists()} | sha256={_sha(path)} | excerpt={excerpt}")
    lifecycle = _context_lifecycle_status(shell)
    lines.append(
        "- kernel.context_lifecycle_gate"
        f" | verdict={lifecycle.get('verdict')}"
        f" | total_context_bytes={lifecycle.get('total_context_bytes')}"
        f" | findings={lifecycle.get('findings')}"
        " | mutation_performed=false"
    )
    return "\n".join(lines)

def _worker_return(*, shell: Path, goal: str, cycle_id: str, step_index: int) -> str:
    touched = "\n".join([
        "  - ION/05_context/current/LAST_ION_AUTONOMOUS_LOOP_RESULT.json",
        "  - ION/05_context/current/ACTIVE_COCKPIT_VIEW_MODEL.json",
        "  - ION/05_context/current/autonomous_loop/",
        "  - ION/05_context/current/agent_context_systems/LEAD_DEV_ACTIVE_CONTEXT_PACKAGE_V101.md",
    ])
    return f"""### CONTEXT PROOF
cycle_id: {cycle_id}
step_index: {step_index}
required_context_reads:
{_context_lines(shell)}
context_statement: Local autonomous loop read available project authority, runtime manifest, runtime separation, context-continuity, and encyclopedia-maintenance surfaces before proposing an integration delta.

### TEMPLATE ACTION PROOF
template_id: ion.template.autonomous_loop.local_worker.v1
action_id: {cycle_id}.step_{step_index:02d}.local_worker_delta
result: accepted_state_delta_candidate
touched_paths:
{touched}
production_authority: false
external_execution_authority: false

### RESULT
Goal: {goal}
Observation: ION now has enough context architecture to justify a local deterministic survival loop. The next boundary is executable proof.
Delta: This step validates context proof, template/action proof, Steward integration, state receipts, and cockpit projection without Cursor Task, MCP, or API calls.
Next: Replace the deterministic local worker with bounded worker adapters only after this loop remains stable under tests.
"""

def _lead_dev_context(created_at: str, cycle_id: str, goal: str, result: Mapping[str, Any]) -> str:
    return f"""# LEAD DEV Active Context Package V101

```yaml
schema_id: ion.lead_dev_active_context_package.v1
created_at: {created_at}
cycle_id: {cycle_id}
production_authority: false
external_execution_authority: false
```

## Current true north

Implement and preserve a host-independent ION autonomous-loop proof before trusting Cursor, MCP, API workers, or multi-agent theatre.

## Current goal

{goal}

## Current accepted state

- local autonomous loop status: `{result.get('status')}`
- steps attempted: `{result.get('steps_attempted')}`
- steps integrated: `{result.get('steps_integrated')}`
- stop reason: `{result.get('stop_reason')}`

## Next lawful move

Advance from deterministic local worker simulation to a bounded worker-adapter interface only after the V101 loop tests pass and the full project zip remains coherent.
"""

def run_autonomous_loop(*, ion_root: str | Path, goal: str, max_steps: int = DEFAULT_MAX_STEPS, write: bool = False) -> dict[str, Any]:
    shell = _root(ion_root)
    max_steps = _bound_max_steps(max_steps)
    created_at = _now()
    wakeup_tick = run_scheduler_tick(
        ion_root=shell,
        write=write,
        trigger="autonomous_loop_cycle",
    )
    lifecycle_report = build_context_lifecycle_report(shell, emitted_at=created_at)
    lifecycle_status = context_lifecycle_report_to_dict(lifecycle_report)
    if write:
        write_context_lifecycle_report(shell, lifecycle_report)
    cycle_id = f"v101_{_slug(goal)}_{created_at.replace(':', '').replace('+', 'z')}"
    run_root = shell / RUN_ROOT_REL / cycle_id
    steps: list[dict[str, Any]] = []
    integrated = 0
    for step_index in range(1, max_steps + 1):
        output = _worker_return(shell=shell, goal=goal, cycle_id=cycle_id, step_index=step_index)
        gate = evaluate_template_action_proof(worker_output=output)
        integration = steward_integrate_return(ion_root=shell, worker_output=output, source="kernel.ion_autonomous_loop.local_worker", cycle_id=cycle_id, step_index=step_index, write=write)
        if write:
            _write_text(run_root / f"step_{step_index:02d}_worker_return.md", output)
            _write_json(run_root / f"step_{step_index:02d}_template_action_gate.json", gate)
            _write_json(run_root / f"step_{step_index:02d}_steward_integration_result.json", integration)
        steps.append({"step_index": step_index, "gate_accepted": bool(gate.get("accepted")), "integration_accepted": bool(integration.get("accepted")), "gate_findings": gate.get("findings", []), "integration_receipt_path": integration.get("receipt_path")})
        if integration.get("accepted"):
            integrated += 1
            break
    status = "PASS" if integrated else "BLOCKED"
    stop_reason = "LOCAL_SURVIVAL_SLICE_ACCEPTED_FIRST_DELTA" if integrated else "NO_ACCEPTED_LOCAL_DELTA"
    idle_streak = update_loop_idle_streak(
        shell,
        cycle_id=cycle_id,
        integrated=integrated,
        stop_reason=stop_reason,
        write=write,
        created_at=created_at,
    )
    result: dict[str, Any] = {"schema_id": "ion.autonomous_loop_result.v1", "created_at": created_at, "cycle_id": cycle_id, "goal": goal, "status": status, "steps_attempted": len(steps), "steps_integrated": integrated, "max_steps": max_steps, "stop_reason": stop_reason, "steps": steps, "run_root": str(RUN_ROOT_REL / cycle_id), "context_lifecycle_verdict": lifecycle_status.get("verdict"), "context_lifecycle_findings": lifecycle_status.get("findings", []), "context_lifecycle_report_path": "ION/05_context/current/CONTEXT_LIFECYCLE_AUDIT_V102.json", "write_performed": write, "production_authority": False, "external_execution_authority": False, "detects_absence": True, "idle_streak": idle_streak, "goal_wakeup_tick": {"tick_id": wakeup_tick.get("tick_id"), "scheduler_verdict": (wakeup_tick.get("scheduler_status") or {}).get("verdict"), "wakeup_receipt_count": len(wakeup_tick.get("wakeup_receipts") or [])}}
    if idle_streak.get("absence_alert_active") and idle_streak.get("absence_alert"):
        result["loop_absence_findings"] = [idle_streak["absence_alert"]]
    if write:
        _write_json(shell / LAST_RESULT_REL, result)
        _write_json(run_root / "loop_result.json", result)
        _write_json(shell / COCKPIT_REL, {"schema_id": "ion.active_cockpit_view_model.v103", "updated_at": created_at, "active_line": "V103_TEMPORAL_CONTEXT_ENFORCEMENT_RECONCILIATION", "goal": goal, "loop_status": result["status"], "cycle_id": cycle_id, "steps_attempted": result["steps_attempted"], "steps_integrated": result["steps_integrated"], "stop_reason": result["stop_reason"], "context_lifecycle_verdict": result["context_lifecycle_verdict"], "context_lifecycle_findings": result["context_lifecycle_findings"], "next_lawful_move": "Promote context lifecycle from audit-adjacent surface into temporal/schedule/carrier packaging enforcement gates without deleting evidence.", "production_authority": False})
        _write_text(shell / LEAD_DEV_CONTEXT_REL, _lead_dev_context(created_at, cycle_id, goal, result))
    return result

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local ION autonomous-loop survival slice.")
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--goal", required=True)
    parser.add_argument("--max-steps", type=int, default=DEFAULT_MAX_STEPS)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = run_autonomous_loop(ion_root=args.ion_root, goal=args.goal, max_steps=args.max_steps, write=args.write)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else f"ION_AUTONOMOUS_LOOP_{result['status']}\n{result['stop_reason']}")
    if result["status"] == "PASS":
        return 0
    if result.get("stop_reason") == "NO_ACCEPTED_LOCAL_DELTA":
        return 0
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
