"""Steward-owned dispatcher projection for bounded agent team work.

The dispatcher is an operational layer over existing ION comms, workpacks,
Domain Weaver, and audit gates. It does not invent agents, simulate replies,
grant authority, or claim accepted state.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from time import monotonic
from pathlib import Path
from typing import Any, Mapping, Sequence

from .ion_agent_comms import extract_agent_mentions, normalize_role_id
from .ion_agent_comms_runs import build_agent_comms_runs_projection, continue_agent_comms_run, start_agent_comms_run

SCHEMA_ID = "ion.steward_dispatcher.v1"
ROUTE_RESULT_SCHEMA_ID = "ion.steward_dispatcher.route_result.v1"
TICK_RESULT_SCHEMA_ID = "ion.steward_dispatcher.tick_result.v1"
PAUSE_RESULT_SCHEMA_ID = "ion.steward_dispatcher.pause_result.v1"
RUNNER_RESULT_SCHEMA_ID = "ion.steward_dispatcher.runner_result.v1"
STATE_SCHEMA_ID = "ion.steward_dispatcher.state.v1"

DISPATCHER_ROOT = Path("ION/05_context/current/steward_dispatcher")
DISPATCHER_STATE_PATH = DISPATCHER_ROOT / "STATE.json"
DISPATCHER_RECEIPT_DIR = DISPATCHER_ROOT / "receipts"

DEFAULT_LIMITS: dict[str, int] = {
    "max_directives": 3,
    "max_pickups": 12,
    "max_agents": 8,
    "max_workpacks": 8,
    "max_graph_nodes": 180,
    "max_graph_edges": 260,
    "automation_window_minutes": 60,
    "automation_prompt_limit": 6,
    "automation_time_budget_minutes": 120,
    "automation_prompt_char_limit": 6000,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ%f")


def _slug(value: Any, fallback: str = "dispatch") -> str:
    text = str(value or "").strip().lower()
    slug = re.sub(r"[^a-z0-9._-]+", "_", text).strip("._-")
    return slug[:96] or fallback


def _root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    return candidate


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _record(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _records(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _text(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text or fallback


def _list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in re.split(r"[\n,]", value) if item.strip()]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _int_limit(value: Any, default: int, floor: int, ceiling: int) -> int:
    try:
        parsed = int(value if value is not None else default)
    except (TypeError, ValueError):
        parsed = default
    return max(floor, min(parsed, ceiling))


def _no_authority() -> dict[str, bool]:
    return {
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def _dispatcher_state(root: Path) -> dict[str, Any]:
    state = _read_json(root / DISPATCHER_STATE_PATH)
    if state:
        state.setdefault("schema_id", STATE_SCHEMA_ID)
        state.setdefault("paused", False)
        return state
    return {
        "schema_id": STATE_SCHEMA_ID,
        "paused": False,
        "pause_reason": "",
        "updated_at": "",
        **_no_authority(),
    }


def _write_receipt(root: Path, action: str, payload: Mapping[str, Any]) -> str:
    receipt_path = root / DISPATCHER_RECEIPT_DIR / f"{_stamp()}_{_slug(action)}.json"
    _write_json(receipt_path, payload)
    return _rel(receipt_path, root)


def _latest_receipt(root: Path, action: str) -> dict[str, Any]:
    receipt_dir = root / DISPATCHER_RECEIPT_DIR
    if not receipt_dir.exists():
        return {}
    suffix = f"_{_slug(action)}.json"
    for path in sorted(receipt_dir.glob(f"*{suffix}"), reverse=True):
        packet = _read_json(path)
        if packet:
            return {"path": _rel(path, root), "packet": packet}
    return {}


def _run_rows(communications: Mapping[str, Any]) -> list[dict[str, Any]]:
    team_comms = _record(communications.get("team_comms"))
    runs = _record(team_comms.get("runs"))
    return _records(runs.get("runs"))


def _run_completion_state(run: Mapping[str, Any]) -> str:
    return _text(_record(run.get("completion_state")).get("state"))


def _run_followup_state(run: Mapping[str, Any]) -> str:
    followup = _record(run.get("followup_decision") or _record(run.get("completion_state")).get("followup_decision"))
    return _text(followup.get("state"))


def _run_worker_active(run: Mapping[str, Any]) -> bool:
    worker = _record(run.get("worker_runtime"))
    latest = _record(worker.get("latest_worker") or run.get("latest_worker"))
    return bool(worker.get("has_active_worker")) or _text(latest.get("status")) == "running"


def _run_policy_state(run: Mapping[str, Any]) -> str:
    return _text(_record(run.get("policy_gate")).get("state"), "unknown")


def _run_audit_clean(run: Mapping[str, Any]) -> bool:
    return bool(_record(run.get("audit_gate")).get("clean") or run.get("is_clean"))


def _run_next_action(run: Mapping[str, Any]) -> str:
    status = _text(run.get("status"))
    completion = _run_completion_state(run)
    policy_state = _run_policy_state(run)
    if "blocked" in status or policy_state == "blocked_by_policy":
        return "inspect_blocker"
    if _run_worker_active(run):
        return "wait_for_return"
    if completion == "ready_to_start_worker":
        return "start_worker"
    if completion == "pending_directive":
        return "pickup_directive"
    if completion in {"awaiting_return", "workpack_active"}:
        return "wait_for_return"
    if status == "active":
        return "continue_run"
    if status == "complete" and not _run_audit_clean(run):
        return "audit_run"
    if status == "complete":
        return "clean_complete"
    return "observe"


def _run_dispatcher_state(run: Mapping[str, Any]) -> str:
    action = _run_next_action(run)
    if action in {"start_worker", "pickup_directive", "continue_run"}:
        return "actionable"
    if action == "wait_for_return":
        return "active"
    if action == "inspect_blocker":
        return "blocked"
    if action == "audit_run":
        return "audit_required"
    if action == "clean_complete":
        return "complete"
    return "idle"


def _run_agents(run: Mapping[str, Any]) -> list[str]:
    roles = [normalize_role_id(role) for role in _list(run.get("target_roles"))]
    for item in _records(run.get("work_items")):
        role = normalize_role_id(item.get("agent_role_id") or item.get("agent_role") or item.get("from_role"))
        if role:
            roles.append(role)
    seen: set[str] = set()
    return [role for role in roles if role and not (role in seen or seen.add(role))]


def _workpack_paths(run: Mapping[str, Any]) -> list[str]:
    paths = _list(run.get("workpack_paths"))
    paths.extend(_text(item.get("workpack_path")) for item in _records(run.get("work_items")) if _text(item.get("workpack_path")))
    seen: set[str] = set()
    return [path for path in paths if path and not (path in seen or seen.add(path))]


def _proof_refs(run: Mapping[str, Any]) -> list[str]:
    refs = [
        *_list(run.get("message_paths")),
        *_workpack_paths(run),
        *[_text(item.get("latest_return_packet_path")) for item in _records(run.get("work_items"))],
        _text(_record(run.get("audit_gate")).get("latest_audit_path")),
        _text(run.get("run_path")),
    ]
    seen: set[str] = set()
    return [ref for ref in refs if ref and not (ref in seen or seen.add(ref))]


def _queue_row(run: Mapping[str, Any]) -> dict[str, Any]:
    worker = _record(run.get("worker_runtime"))
    directive_state = _record(_record(run.get("completion_state")).get("directive_state") or run.get("directive_state"))
    return {
        "run_id": run.get("run_id"),
        "state": _run_dispatcher_state(run),
        "next_action": _run_next_action(run),
        "status": run.get("status"),
        "objective": run.get("objective"),
        "assigned_agents": _run_agents(run),
        "workpack_paths": _workpack_paths(run),
        "pending_directive_count": int(directive_state.get("pending_directive_count") or 0),
        "active_worker_count": int(worker.get("active_worker_count") or (1 if _run_worker_active(run) else 0)),
        "task_return_count": int(run.get("task_return_count") or 0),
        "agent_response_count": int(run.get("agent_response_count") or 0),
        "followup_state": _run_followup_state(run),
        "policy_state": _run_policy_state(run),
        "audit_clean": _run_audit_clean(run),
        "proof_refs": _proof_refs(run)[:12],
    }


def _agent_load(agents: Sequence[Mapping[str, Any]], queue: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    role_ids = [normalize_role_id(agent.get("role_id") or agent.get("agent_id")) for agent in agents]
    for run in queue:
        role_ids.extend(_run_agents(run))
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for role_id in [role for role in role_ids if role and not (role in seen or seen.add(role))]:
        assigned_runs = [run for run in queue if role_id in _run_agents(run)]
        rows.append(
            {
                "role_id": role_id,
                "assigned_run_count": len(assigned_runs),
                "active_run_count": sum(1 for run in assigned_runs if _run_dispatcher_state(run) in {"active", "actionable"}),
                "active_worker_count": sum(1 for run in assigned_runs if _run_worker_active(run)),
                "pending_directive_count": sum(
                    int(_record(_record(run.get("completion_state")).get("directive_state") or run.get("directive_state")).get("pending_directive_count") or 0)
                    for run in assigned_runs
                ),
                "available_for_comms": bool(next((_record(agent.get("communication_profile")).get("available_for_comms") for agent in agents if normalize_role_id(agent.get("role_id") or agent.get("agent_id")) == role_id), False)),
            }
        )
    rows.sort(key=lambda item: (-int(item["active_worker_count"]), -int(item["active_run_count"]), str(item["role_id"])))
    return rows


def _domain_gap_rows(domain_weaver: Mapping[str, Any]) -> list[dict[str, Any]]:
    gaps = _records(domain_weaver.get("gaps"))
    if gaps:
        return gaps
    return [
        {
            "scope": "domain",
            "id": domain.get("domain_id"),
            "gap": domain.get("status"),
        }
        for domain in _records(domain_weaver.get("domains"))
        if _text(domain.get("status")) not in {"usable", "candidate_covered"}
    ]


def build_steward_dispatcher_projection(
    root: str | Path | None = None,
    *,
    agents: Sequence[Mapping[str, Any]] | None = None,
    domains: Sequence[Mapping[str, Any]] | None = None,
    communications: Mapping[str, Any] | None = None,
    runs: Mapping[str, Any] | None = None,
    domain_weaver: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    shell_root = _root(root)
    state = _dispatcher_state(shell_root)
    agent_rows = [dict(agent) for agent in agents or [] if isinstance(agent, Mapping)]
    domain_rows = [dict(domain) for domain in domains or [] if isinstance(domain, Mapping)]
    run_rows = _run_rows(_record(communications))
    queue_rows = [_queue_row(run) for run in run_rows]
    active = [row for row in queue_rows if row["state"] in {"active", "actionable"}]
    actionable = [row for row in queue_rows if row["state"] == "actionable"]
    blocked = [row for row in queue_rows if row["state"] == "blocked"]
    audit_required = [row for row in queue_rows if row["state"] == "audit_required"]
    next_action = actionable[0] if actionable else (active[0] if active else (audit_required[0] if audit_required else (queue_rows[0] if queue_rows else {})))
    domain_gaps = _domain_gap_rows(_record(domain_weaver))
    load_rows = _agent_load(agent_rows, run_rows)
    runs_record = _record(runs)
    latest_runner = _latest_receipt(shell_root, "runner")
    latest_runner_packet = _record(latest_runner.get("packet"))
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "state_path": DISPATCHER_STATE_PATH.as_posix(),
        "receipt_dir": DISPATCHER_RECEIPT_DIR.as_posix(),
        "paused": bool(state.get("paused")),
        "pause_reason": state.get("pause_reason") or "",
        "dispatcher_state": "paused" if state.get("paused") else ("actionable" if actionable else ("active" if active else ("audit_required" if audit_required else "idle"))),
        "summary": {
            "agent_count": len(agent_rows),
            "domain_count": len(domain_rows),
            "run_count": len(queue_rows),
            "active_run_count": len(active),
            "actionable_run_count": len(actionable),
            "active_worker_count": sum(int(row.get("active_worker_count") or 0) for row in queue_rows),
            "pending_directive_count": sum(int(row.get("pending_directive_count") or 0) for row in queue_rows),
            "blocked_run_count": len(blocked),
            "audit_required_count": len(audit_required),
            "domain_gap_count": len(domain_gaps),
            "queued_agent_codex_work_request_count": runs_record.get("queued_agent_codex_work_request_count", 0),
        },
        "next_action": next_action,
        "queue": queue_rows,
        "agent_load": load_rows,
        "domain_gaps": domain_gaps[:50],
        "runner": {
            "schema_id": "ion.steward_dispatcher.runner.v1",
            "endpoint": "/cockpit/agents/dispatcher/runner",
            "latest_receipt_path": latest_runner.get("path") or "",
            "latest_finding": latest_runner_packet.get("finding") or "",
            "latest_ok": latest_runner_packet.get("ok"),
            "latest_tick_count": latest_runner_packet.get("tick_count"),
            "latest_usage": latest_runner_packet.get("usage") or {},
            "limits": {
                "max_ticks": 6,
                "max_runtime_seconds": 30,
                "max_worker_starts": 1,
                "max_directives": DEFAULT_LIMITS["max_directives"],
            },
            **_no_authority(),
        },
        "controls": {
            "route_endpoint": "/cockpit/agents/dispatcher/route",
            "tick_endpoint": "/cockpit/agents/dispatcher/tick",
            "pause_endpoint": "/cockpit/agents/dispatcher/pause",
            "runner_endpoint": "/cockpit/agents/dispatcher/runner",
            "default_dispatch_mode": "queue_workpack",
            "bounded_auto_default": True,
            "limits": dict(DEFAULT_LIMITS),
            "runner_limits": {
                "max_ticks": 6,
                "max_runtime_seconds": 30,
                "max_worker_starts": 1,
                "max_directives": DEFAULT_LIMITS["max_directives"],
            },
        },
        "policy": "Steward Dispatcher routes and ticks existing durable Team Comms runs only. Agents communicate through explicit @mentions, messages, returns, and ion-agent-comms directives; no replies are simulated.",
        **_no_authority(),
    }


def _route_plan(root: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    objective = _text(payload.get("objective") or payload.get("subject") or payload.get("task"))
    body = _text(payload.get("body") or payload.get("message") or objective)
    target_roles = [normalize_role_id(role) for role in _list(payload.get("target_roles") or payload.get("to_roles"))]
    target_roles = [role for role in target_roles if role]
    if not target_roles:
        mentions = extract_agent_mentions(root, "\n".join([objective, body]))
        target_roles = [normalize_role_id(role) for role in _list(mentions.get("roles"))]
    if not target_roles:
        target_roles = ["role.steward"]
    seen: set[str] = set()
    target_roles = [role for role in target_roles if role and not (role in seen or seen.add(role))]
    dispatch_mode = _text(payload.get("dispatch_mode"), "queue_workpack")
    if dispatch_mode not in {"comms_only", "prepare_workpack", "queue_workpack"}:
        dispatch_mode = "queue_workpack"
    limits = {
        "max_directives": _int_limit(payload.get("max_directives"), DEFAULT_LIMITS["max_directives"], 1, 25),
        "max_pickups": _int_limit(payload.get("max_pickups"), DEFAULT_LIMITS["max_pickups"], 1, 100),
        "max_agents": _int_limit(payload.get("max_agents"), DEFAULT_LIMITS["max_agents"], 1, 100),
        "max_workpacks": _int_limit(payload.get("max_workpacks"), DEFAULT_LIMITS["max_workpacks"], 1, 500),
        "max_graph_nodes": _int_limit(payload.get("max_graph_nodes"), DEFAULT_LIMITS["max_graph_nodes"], 8, 2000),
        "max_graph_edges": _int_limit(payload.get("max_graph_edges"), DEFAULT_LIMITS["max_graph_edges"], 8, 3000),
        "automation_window_minutes": _int_limit(payload.get("automation_window_minutes"), DEFAULT_LIMITS["automation_window_minutes"], 1, 1440),
        "automation_prompt_limit": _int_limit(payload.get("automation_prompt_limit"), DEFAULT_LIMITS["automation_prompt_limit"], 1, 100),
        "automation_time_budget_minutes": _int_limit(payload.get("automation_time_budget_minutes"), DEFAULT_LIMITS["automation_time_budget_minutes"], 1, 1440),
        "automation_prompt_char_limit": _int_limit(payload.get("automation_prompt_char_limit"), DEFAULT_LIMITS["automation_prompt_char_limit"], 1, 20000),
    }
    return {
        "dispatch_id": _text(payload.get("dispatch_id")) or f"steward_dispatch_{_stamp()}_{_slug(objective, 'task')}",
        "objective": objective,
        "body": body,
        "target_roles": target_roles,
        "dispatch_mode": dispatch_mode,
        "channel_id": _text(payload.get("channel_id"), "team"),
        "thread_id": _text(payload.get("thread_id")),
        "from_role": _text(payload.get("from_role"), "operator"),
        "domain_id": _text(payload.get("domain_id")),
        "limits": limits,
        "source_refs": _list(payload.get("source_refs") or payload.get("context_refs")),
        "artifact_refs": _list(payload.get("artifact_refs") or payload.get("evidence_refs")),
        "steward_authority_role": "role.steward",
        "dispatcher_layer": "steward_dispatcher",
    }


def route_steward_dispatcher(root: str | Path | None, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    shell_root = _root(root)
    data = dict(payload or {})
    state = _dispatcher_state(shell_root)
    if state.get("paused"):
        return {
            "schema_id": ROUTE_RESULT_SCHEMA_ID,
            "ok": False,
            "finding": "dispatcher_paused",
            "pause_reason": state.get("pause_reason") or "",
            **_no_authority(),
        }
    plan = _route_plan(shell_root, data)
    if not plan["objective"]:
        return {"schema_id": ROUTE_RESULT_SCHEMA_ID, "ok": False, "finding": "objective_required", "route_plan": plan, **_no_authority()}
    if not plan["body"]:
        return {"schema_id": ROUTE_RESULT_SCHEMA_ID, "ok": False, "finding": "body_required", "route_plan": plan, **_no_authority()}
    if data.get("dry_run") is True or data.get("start") is False:
        return {
            "schema_id": ROUTE_RESULT_SCHEMA_ID,
            "ok": True,
            "routed": False,
            "route_plan": plan,
            "policy": "Dry-run route plan only; no comms run was created.",
            **_no_authority(),
        }
    run_payload = {
        "objective": plan["objective"],
        "body": plan["body"],
        "from_role": plan["from_role"],
        "target_roles": plan["target_roles"],
        "dispatch_mode": plan["dispatch_mode"],
        "channel_id": plan["channel_id"],
        "thread_id": plan["thread_id"] or None,
        "domain_id": plan["domain_id"] or None,
        "source_refs": plan["source_refs"],
        "artifact_refs": plan["artifact_refs"],
        "initiated_by": "steward_dispatcher",
        "automation_id": f"steward_dispatcher:{plan['dispatch_id']}",
        **plan["limits"],
    }
    run_result = start_agent_comms_run(shell_root, run_payload)
    receipt = {
        "schema_id": ROUTE_RESULT_SCHEMA_ID,
        "created_at": _now(),
        "ok": bool(run_result.get("ok")),
        "dispatch_id": plan["dispatch_id"],
        "route_plan": plan,
        "run_id": run_result.get("run_id"),
        "run_path": run_result.get("run_path"),
        "run_receipt_path": run_result.get("receipt_path"),
        "thread_ids": list(run_result.get("thread_ids") or []),
        "message_ids": list(run_result.get("message_ids") or []),
        "workpack_paths": list(run_result.get("workpack_paths") or []),
        "finding": run_result.get("finding"),
        **_no_authority(),
    }
    receipt_path = _write_receipt(shell_root, "route", receipt)
    return {
        **receipt,
        "receipt_path": receipt_path,
        "routed": bool(run_result.get("ok")),
        "run_result": run_result,
    }


def tick_steward_dispatcher(root: str | Path | None, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    shell_root = _root(root)
    data = dict(payload or {})
    state = _dispatcher_state(shell_root)
    if state.get("paused"):
        return {
            "schema_id": TICK_RESULT_SCHEMA_ID,
            "ok": False,
            "finding": "dispatcher_paused",
            "pause_reason": state.get("pause_reason") or "",
            **_no_authority(),
        }
    run_id = _text(data.get("run_id"))
    if not run_id:
        return {"schema_id": TICK_RESULT_SCHEMA_ID, "ok": False, "finding": "run_id_required", **_no_authority()}
    max_directives = _int_limit(data.get("max_directives"), DEFAULT_LIMITS["max_directives"], 1, 25)
    max_worker_starts = _int_limit(data.get("max_worker_starts"), 1, 0, 10)
    result = continue_agent_comms_run(
        shell_root,
        {
            "run_id": run_id,
            "max_directives": max_directives,
            "max_worker_starts": max_worker_starts,
            "start_workers": data.get("start_workers") is not False,
            "timeout_seconds": _int_limit(data.get("timeout_seconds"), 1800, 30, 86400),
        },
    )
    receipt = {
        "schema_id": TICK_RESULT_SCHEMA_ID,
        "created_at": _now(),
        "ok": bool(result.get("ok")),
        "run_id": run_id,
        "max_directives": max_directives,
        "max_worker_starts": max_worker_starts,
        "tick_result": result,
        "finding": result.get("finding"),
        **_no_authority(),
    }
    receipt_path = _write_receipt(shell_root, "tick", receipt)
    return {**receipt, "receipt_path": receipt_path}


def _runner_projection(root: Path, limit: int = 100) -> dict[str, Any]:
    runs_projection = build_agent_comms_runs_projection(root, limit=limit)
    return build_steward_dispatcher_projection(
        root,
        communications={"team_comms": {"runs": runs_projection}},
        runs={"queued_agent_codex_work_request_count": runs_projection.get("queued_agent_codex_work_request_count", 0)},
    )


def _runner_selected_run(projection: Mapping[str, Any], explicit_run_id: str = "") -> dict[str, Any]:
    queue = _records(projection.get("queue"))
    if explicit_run_id:
        return next((row for row in queue if _text(row.get("run_id")) == explicit_run_id), {"run_id": explicit_run_id, "state": "explicit"})
    actionable = [row for row in queue if _text(row.get("state")) == "actionable"]
    if actionable:
        return actionable[0]
    next_action = _record(projection.get("next_action"))
    if _text(next_action.get("run_id")) and _text(next_action.get("state")) == "actionable":
        return next_action
    return {}


def _tick_counter(result: Mapping[str, Any], key: str) -> int:
    tick = _record(result.get("tick_result"))
    try:
        return int(tick.get(key) or result.get(key) or 0)
    except (TypeError, ValueError):
        return 0


def run_steward_dispatcher_runner(root: str | Path | None, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Run a bounded mechanical dispatcher loop.

    The runner only selects actionable Team Comms runs and calls
    ``tick_steward_dispatcher``. It does not route new work or decide which agent
    should communicate.
    """

    shell_root = _root(root)
    data = dict(payload or {})
    state = _dispatcher_state(shell_root)
    created_at = _now()
    max_ticks = _int_limit(data.get("max_ticks"), 1, 1, 50)
    max_runtime_seconds = _int_limit(data.get("max_runtime_seconds"), 30, 1, 3600)
    max_directives_per_tick = _int_limit(data.get("max_directives_per_tick") or data.get("max_directives"), DEFAULT_LIMITS["max_directives"], 1, 25)
    max_worker_starts_per_tick = _int_limit(data.get("max_worker_starts_per_tick"), 1, 0, 10)
    max_worker_starts = _int_limit(data.get("max_worker_starts"), 1, 0, 100)
    max_processed_directives = _int_limit(data.get("max_processed_directives"), DEFAULT_LIMITS["max_directives"], 1, 100)
    explicit_run_id = _text(data.get("run_id"))
    start_workers = data.get("start_workers") is not False
    timeout_seconds = _int_limit(data.get("timeout_seconds"), 1800, 30, 86400)
    dry_run = data.get("dry_run") is True
    ticks: list[dict[str, Any]] = []
    tick_receipt_paths: list[str] = []
    selected_run_ids: list[str] = []
    worker_start_count = 0
    processed_directive_count = 0
    return_sync_count = 0
    finding = ""
    started = monotonic()

    if state.get("paused"):
        finding = "dispatcher_paused"
    else:
        for tick_index in range(max_ticks):
            elapsed = monotonic() - started
            if elapsed >= max_runtime_seconds:
                finding = "runtime_limit_reached"
                break
            projection = _runner_projection(shell_root)
            selected = _runner_selected_run(projection, explicit_run_id)
            run_id = _text(selected.get("run_id"))
            selected_state = _text(selected.get("state"))
            if not run_id:
                finding = "no_actionable_run"
                break
            if not explicit_run_id and selected_state != "actionable":
                finding = "no_actionable_run"
                break
            selected_run_ids.append(run_id)
            if dry_run:
                finding = "dry_run_selected"
                ticks.append(
                    {
                        "tick_index": tick_index,
                        "run_id": run_id,
                        "selected_state": selected_state,
                        "next_action": selected.get("next_action"),
                        "dry_run": True,
                    }
                )
                break
            tick_result = tick_steward_dispatcher(
                shell_root,
                {
                    "run_id": run_id,
                    "max_directives": max_directives_per_tick,
                    "max_worker_starts": max_worker_starts_per_tick,
                    "start_workers": start_workers,
                    "timeout_seconds": timeout_seconds,
                },
            )
            tick_receipt = _text(tick_result.get("receipt_path"))
            if tick_receipt:
                tick_receipt_paths.append(tick_receipt)
            tick_worker_starts = _tick_counter(tick_result, "worker_start_count")
            tick_processed_directives = _tick_counter(tick_result, "processed_directive_count")
            tick_return_sync = _tick_counter(tick_result, "return_sync_count")
            worker_start_count += tick_worker_starts
            processed_directive_count += tick_processed_directives
            return_sync_count += tick_return_sync
            ticks.append(
                {
                    "tick_index": tick_index,
                    "run_id": run_id,
                    "selected_state": selected_state,
                    "next_action": selected.get("next_action"),
                    "ok": tick_result.get("ok"),
                    "finding": tick_result.get("finding"),
                    "receipt_path": tick_receipt,
                    "worker_start_count": tick_worker_starts,
                    "processed_directive_count": tick_processed_directives,
                    "return_sync_count": tick_return_sync,
                }
            )
            if tick_result.get("ok") is not True:
                finding = _text(tick_result.get("finding"), "tick_failed")
                break
            if worker_start_count >= max_worker_starts:
                finding = "worker_start_limit_reached"
                break
            if processed_directive_count >= max_processed_directives:
                finding = "directive_limit_reached"
                break
        else:
            finding = "tick_limit_reached"

    final_projection = _runner_projection(shell_root) if not state.get("paused") else {}
    elapsed_ms = int((monotonic() - started) * 1000)
    ok = finding in {"dry_run_selected", "tick_limit_reached", "worker_start_limit_reached", "directive_limit_reached", "no_actionable_run"} or (
        bool(ticks) and all(tick.get("ok", True) is True for tick in ticks)
    )
    receipt = {
        "schema_id": RUNNER_RESULT_SCHEMA_ID,
        "ok": ok,
        "created_at": created_at,
        "completed_at": _now(),
        "finding": finding or "runner_complete",
        "dry_run": dry_run,
        "selected_run_ids": selected_run_ids,
        "tick_count": len(ticks),
        "ticks": ticks,
        "tick_receipt_paths": tick_receipt_paths,
        "limits": {
            "max_ticks": max_ticks,
            "max_runtime_seconds": max_runtime_seconds,
            "max_directives_per_tick": max_directives_per_tick,
            "max_worker_starts_per_tick": max_worker_starts_per_tick,
            "max_worker_starts": max_worker_starts,
            "max_processed_directives": max_processed_directives,
            "timeout_seconds": timeout_seconds,
        },
        "usage": {
            "elapsed_ms": elapsed_ms,
            "worker_start_count": worker_start_count,
            "processed_directive_count": processed_directive_count,
            "return_sync_count": return_sync_count,
        },
        "final_dispatcher_state": final_projection.get("dispatcher_state"),
        "final_summary": final_projection.get("summary"),
        "policy": "Runner only calls dispatcher ticks for existing actionable Team Comms runs under hard limits. It never invents routing, messages, returns, receipts, or accepted state.",
        **_no_authority(),
    }
    receipt_path = _write_receipt(shell_root, "runner", receipt)
    return {**receipt, "receipt_path": receipt_path}


def pause_steward_dispatcher(root: str | Path | None, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    shell_root = _root(root)
    data = dict(payload or {})
    current = _dispatcher_state(shell_root)
    paused = data.get("paused")
    if paused is None:
        paused = not bool(current.get("paused"))
    state = {
        "schema_id": STATE_SCHEMA_ID,
        "paused": bool(paused),
        "pause_reason": _text(data.get("reason") or data.get("pause_reason")),
        "updated_at": _now(),
        **_no_authority(),
    }
    _write_json(shell_root / DISPATCHER_STATE_PATH, state)
    receipt = {
        "schema_id": PAUSE_RESULT_SCHEMA_ID,
        "ok": True,
        "created_at": state["updated_at"],
        "state": state,
        **_no_authority(),
    }
    receipt_path = _write_receipt(shell_root, "pause" if state["paused"] else "resume", receipt)
    return {**receipt, "receipt_path": receipt_path}
