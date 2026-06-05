"""Bounded agent comms task runs.

A run is not a mock conversation and not a background decider. It is a durable
operator-approved wrapper around the existing agent comms, directive pickup, and
spawn-template paths so humans can start a task, process explicit agent-authored
directives under limits, and watch the filesystem evidence unfold.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_agent_comms import AGENT_COMMS_ROOT, extract_agent_mentions, send_agent_message
from .ion_agent_comms_audit_gate import audit_gate_for_run
from .ion_agent_comms_directives import DIRECTIVE_LEDGER_PATH, extract_agent_comms_directives, process_agent_comms_directives
from .ion_agent_spawn_templates import execute_agent_spawn_template
from .ion_codex_queue_runner import process_codex_queue_once

RUN_SCHEMA_ID = "ion.agent_comms.run.v1"
RUN_RESULT_SCHEMA_ID = "ion.agent_comms.run.result.v1"
RUN_PICKUP_SCHEMA_ID = "ion.agent_comms.run.pickup.result.v1"
RUN_WORKER_SCHEMA_ID = "ion.agent_comms.run.worker_start.result.v1"
RUN_CONTINUE_SCHEMA_ID = "ion.agent_comms.run.continue.result.v1"
RUN_PROJECTION_SCHEMA_ID = "ion.agent_comms.runs.projection.v1"
FOLLOWUP_DECISION_SCHEMA_ID = "ion.agent_comms.followup_decision.v1"

RUNS_DIR = AGENT_COMMS_ROOT / "runs"
RUN_INDEX_PATH = RUNS_DIR / "RUN_INDEX.json"
RUN_RECEIPT_DIR = RUNS_DIR / "receipts"
CODEX_WORK_REQUESTS_DIR = Path("ION/05_context/current/chatgpt_connector/codex_work_requests")
TASK_RETURNS_DIR = Path("ION/05_context/current/chatgpt_connector/task_returns")

ALLOWED_RUN_DISPATCH_MODES = {"comms_only", "prepare_workpack", "queue_workpack"}
DEFAULT_MAX_AGENTS_PER_RUN = 8
DEFAULT_MAX_WORKPACKS_PER_RUN = 8
DEFAULT_MAX_GRAPH_NODES = 180
DEFAULT_MAX_GRAPH_EDGES = 260
FOLLOWUP_DECISION_LANGS = {
    "ion-agent-decision",
    "ion_agent_decision",
    "ion-agent-followup",
    "ion_agent_followup",
    "ion-agent-comms-decision",
    "ion_agent_comms_decision",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ%f")


def _slug(value: Any, fallback: str = "run") -> str:
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
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _text(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text or fallback


def _list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in re.split(r"[\n,]", value) if item.strip()]
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _record(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _int_limit(value: Any, default: int, floor: int, ceiling: int) -> int:
    try:
        parsed = int(value or default)
    except (TypeError, ValueError):
        parsed = default
    return max(floor, min(parsed, ceiling))


def _read_repo_json(root: Path, rel_path: Any) -> dict[str, Any]:
    text = _text(rel_path)
    if not text:
        return {}
    path = Path(text)
    if path.is_absolute() or ".." in path.parts:
        return {}
    return _read_json(root / path)


def _task_return_rows(root: Path, workpack_path: str, workpack: Mapping[str, Any]) -> list[dict[str, Any]]:
    request_id = _text(workpack.get("request_id") or workpack.get("codex_work_request_id"))
    explicit_paths = [
        *_list(workpack.get("return_packet_paths")),
        _text(workpack.get("latest_return_packet_path")),
    ]
    rows: dict[str, dict[str, Any]] = {}
    for explicit_path in explicit_paths:
        if not explicit_path:
            continue
        packet = _read_repo_json(root, explicit_path)
        rows[explicit_path] = {"path": explicit_path, "packet": packet}
    returns_root = root / TASK_RETURNS_DIR
    if returns_root.exists():
        for path in sorted(returns_root.glob("*.json")):
            packet = _read_json(path)
            if not packet:
                continue
            if workpack_path and packet.get("work_request_path") == workpack_path:
                rows[_rel(path, root)] = {"path": _rel(path, root), "packet": packet}
            elif request_id and packet.get("work_request_id") == request_id:
                rows[_rel(path, root)] = {"path": _rel(path, root), "packet": packet}
    return sorted(rows.values(), key=lambda item: str(_record(item.get("packet")).get("created_at") or item.get("path") or ""))


def _task_return_summary(packet: Mapping[str, Any]) -> str:
    for key in ("result", "status", "finding", "summary"):
        value = _text(packet.get(key))
        if value:
            return value[:240]
    preview = _text(packet.get("task_output_preview") or packet.get("output_preview"))
    if preview:
        return preview.replace("\n", " ")[:240]
    return "task return packet recorded"


def _task_return_output_text(packet: Mapping[str, Any]) -> str:
    chunks: list[str] = []
    for key in ("task_output_preview", "output_preview", "task_output", "output", "response", "final_response", "body"):
        value = _text(packet.get(key))
        if value and value not in chunks:
            chunks.append(value)
    return "\n\n".join(chunks)


def _task_return_full_output_text(root: Path, item: Mapping[str, Any], packet: Mapping[str, Any]) -> str:
    chunks = [_task_return_output_text(packet)]
    workpack = _read_repo_json(root, item.get("workpack_path"))
    for run_path in _list(workpack.get("codex_queue_runner_runs")):
        path = Path(run_path)
        if path.is_absolute() or ".." in path.parts:
            continue
        run_dir = (root / path).parent
        for candidate in (run_dir / "latest_return.md", run_dir / "task_return_body.md"):
            try:
                text_value = candidate.read_text(encoding="utf-8")
            except OSError:
                continue
            if text_value and text_value not in chunks:
                chunks.append(text_value)
    return "\n\n".join(chunk for chunk in chunks if chunk)


def _fenced_blocks(text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    in_block = False
    lang = ""
    lines: list[str] = []
    for line in (text or "").splitlines():
        open_match = re.match(r"^\s*```([A-Za-z0-9_.-]*)\s*$", line)
        close_match = re.match(r"^\s*```\s*$", line)
        if not in_block:
            if open_match:
                in_block = True
                lang = (open_match.group(1) or "").strip().lower()
                lines = []
            continue
        if close_match:
            body = "\n".join(lines).strip()
            if body:
                blocks.append((lang, body))
            in_block = False
            lang = ""
            lines = []
            continue
        lines.append(line)
    return blocks


def _normalize_followup_decision(value: Any) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")
    aliases = {
        "none": "no_followup",
        "no_follow_up": "no_followup",
        "no_followup_needed": "no_followup",
        "no_agent_needed": "no_followup",
        "stop": "no_followup",
        "done": "no_followup",
        "complete": "no_followup",
        "call": "call_agent",
        "followup": "call_agent",
        "follow_up": "call_agent",
        "needs_agent": "call_agent",
        "call_specialist": "call_agent",
        "route_agent": "call_agent",
    }
    return aliases.get(normalized, normalized)


def _extract_followup_decision_blocks(text: str) -> dict[str, Any]:
    decisions: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for index, (lang, block) in enumerate(_fenced_blocks(text), start=1):
        if lang not in FOLLOWUP_DECISION_LANGS and lang != "json":
            continue
        try:
            payload = json.loads(block)
        except json.JSONDecodeError:
            if lang in FOLLOWUP_DECISION_LANGS:
                findings.append({"finding": "followup_decision_json_invalid", "index": index, "raw": block[:500]})
            continue
        if not isinstance(payload, Mapping):
            findings.append({"finding": "followup_decision_not_object", "index": index})
            continue
        if lang == "json" and _text(payload.get("schema_id")) != FOLLOWUP_DECISION_SCHEMA_ID:
            continue
        decision = _normalize_followup_decision(payload.get("decision") or payload.get("state") or payload.get("action"))
        if decision not in {"no_followup", "call_agent", "blocked"}:
            findings.append({"finding": "unsupported_followup_decision", "index": index, "decision": decision})
            continue
        decisions.append(
            {
                "schema_id": FOLLOWUP_DECISION_SCHEMA_ID,
                "decision": decision,
                "reason": _text(payload.get("reason") or payload.get("summary")),
                "agent": _text(payload.get("agent") or payload.get("target_agent") or payload.get("to_role")),
                "evidence_refs": _list(payload.get("evidence_refs") or payload.get("source_refs")),
                "index": index,
            }
        )
    return {
        "schema_id": "ion.agent_comms.followup_decision_extract.v1",
        "decision_count": len(decisions),
        "finding_count": len(findings),
        "decisions": decisions,
        "findings": findings,
        **_no_authority(),
    }


def _task_return_followup_decision(root: Path, item: Mapping[str, Any], packet: Mapping[str, Any]) -> dict[str, Any]:
    if not packet:
        return {"schema_id": "ion.agent_comms.work_item.followup_decision.v1", "state": "waiting_return", **_no_authority()}
    output = _task_return_full_output_text(root, item, packet)
    directives = extract_agent_comms_directives(output)
    directive_rows = [_record(row) for row in list(directives.get("directives") or [])]
    if directive_rows:
        return {
            "schema_id": "ion.agent_comms.work_item.followup_decision.v1",
            "state": "followup_directive",
            "decision": "call_agent",
            "directive_count": len(directive_rows),
            "target_agents": [_text(row.get("agent")) for row in directive_rows if _text(row.get("agent"))],
            "reason": "agent emitted executable ion-agent-comms directive",
            **_no_authority(),
        }
    decision_extract = _extract_followup_decision_blocks(output)
    decision_rows = [_record(row) for row in list(decision_extract.get("decisions") or [])]
    if decision_rows:
        latest = decision_rows[-1]
        decision = _text(latest.get("decision"))
        if decision == "call_agent":
            state = "call_agent_missing_directive"
        elif decision == "blocked":
            state = "blocked"
        else:
            state = "no_followup"
        return {
            "schema_id": "ion.agent_comms.work_item.followup_decision.v1",
            "state": state,
            "decision": decision,
            "reason": _text(latest.get("reason")),
            "agent": _text(latest.get("agent")),
            "evidence_refs": list(latest.get("evidence_refs") or []),
            "decision_count": len(decision_rows),
            **_no_authority(),
        }
    findings = list(decision_extract.get("findings") or []) + list(directives.get("findings") or [])
    if findings:
        return {
            "schema_id": "ion.agent_comms.work_item.followup_decision.v1",
            "state": "decision_invalid",
            "decision": "invalid",
            "reason": _text(_record(findings[-1]).get("finding"), "invalid follow-up decision block"),
            "findings": findings[:5],
            **_no_authority(),
        }
    return {
        "schema_id": "ion.agent_comms.work_item.followup_decision.v1",
        "state": "decision_missing",
        "decision": "unknown",
        "reason": "return did not declare no-followup or emit an executable ion-agent-comms directive",
        **_no_authority(),
    }


def _sync_usage_observed_counts(run: Mapping[str, Any]) -> dict[str, Any]:
    updated = dict(run)
    usage = _record(updated.get("usage"))
    usage["queued_workpack_count"] = len({str(path) for path in list(updated.get("workpack_paths") or []) if str(path)})
    usage["agent_return_message_count"] = len(_record(updated.get("return_message_ids")))
    updated["usage"] = usage
    return updated


def _workpack_response_state(status: str, has_returns: bool, has_workpack: bool) -> str:
    if has_returns:
        return "returned"
    upper = status.upper()
    if "QUEUED" in upper:
        return "queued"
    if "PREPARED" in upper:
        return "prepared"
    if has_workpack:
        return "workpack_active"
    return "workpack_missing"


def _work_items(root: Path, run: Mapping[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[str] = set()
    for workpack_path in [str(path) for path in list(run.get("workpack_paths") or []) if str(path)]:
        if workpack_path in seen:
            continue
        seen.add(workpack_path)
        workpack = _read_repo_json(root, workpack_path)
        returns = _task_return_rows(root, workpack_path, workpack)
        latest_return = returns[-1] if returns else {}
        latest_packet = _record(latest_return.get("packet"))
        status = _text(workpack.get("status") or workpack.get("codex_work_request_status"), "missing_workpack")
        agent_role_id = _text(
            workpack.get("agent_role_id")
            or workpack.get("agent_role")
            or latest_packet.get("agent_role_id")
            or latest_packet.get("agent_role")
        )
        if not agent_role_id:
            target_roles = [str(role) for role in list(run.get("target_roles") or []) if str(role)]
            agent_role_id = target_roles[0] if target_roles else "role.steward"
        return_paths = [str(item.get("path")) for item in returns if str(item.get("path"))]
        item_seed = {"workpack_path": workpack_path}
        followup_decision = _task_return_followup_decision(root, item_seed, latest_packet) if latest_packet else {
            "schema_id": "ion.agent_comms.work_item.followup_decision.v1",
            "state": "waiting_return",
            **_no_authority(),
        }
        items.append(
            {
                "workpack_path": workpack_path,
                "request_id": workpack.get("request_id") or workpack.get("codex_work_request_id"),
                "agent_role_id": agent_role_id,
                "agent_display_name": _text(workpack.get("agent_display_name") or latest_packet.get("agent_display_name") or agent_role_id),
                "work_request_status": status,
                "response_state": _workpack_response_state(status, bool(returns), bool(workpack)),
                "task_return_count": len(returns),
                "accepted_return_count": sum(1 for item in returns if _record(item.get("packet")).get("accepted_for_carrier_intake") is True),
                "return_packet_paths": return_paths,
                "latest_return_packet_path": str(latest_return.get("path") or workpack.get("latest_return_packet_path") or ""),
                "latest_return_summary": _task_return_summary(latest_packet) if latest_packet else "",
                "followup_decision": followup_decision,
                "followup_decision_state": followup_decision.get("state"),
            }
        )
    return items


def _agent_response_messages(root: Path, run: Mapping[str, Any]) -> list[dict[str, Any]]:
    from_role = _text(run.get("from_role"), "operator")
    responses: list[dict[str, Any]] = []
    seen: set[str] = set()
    for message_path in _message_paths_for_threads(root, [str(item) for item in list(run.get("thread_ids") or []) if str(item)]):
        message = _read_repo_json(root, message_path)
        sender = _text(message.get("from_role"))
        if not sender or sender == from_role or sender == "operator" or not sender.startswith("role."):
            continue
        message_id = _text(message.get("message_id"), message_path)
        if message_id in seen:
            continue
        seen.add(message_id)
        responses.append(
            {
                "message_id": message_id,
                "message_path": message_path,
                "from_role": sender,
                "message_kind": message.get("message_kind"),
                "subject": message.get("subject"),
                "summary": message.get("summary"),
                "created_at": message.get("created_at"),
                "source_refs": list(message.get("source_refs") or []),
                "artifact_refs": list(message.get("artifact_refs") or []),
            }
        )
    return responses


def _run_followup_decision_state(work_items: list[Mapping[str, Any]]) -> dict[str, Any]:
    if not work_items:
        return {"schema_id": "ion.agent_comms.run.followup_decision_state.v1", "state": "not_applicable", **_no_authority()}
    states: dict[str, int] = {}
    latest: dict[str, Any] = {}
    latest_state = ""
    for item in work_items:
        decision = _record(_record(item).get("followup_decision"))
        state = _text(decision.get("state"), "decision_missing")
        states[state] = states.get(state, 0) + 1
        if state != "waiting_return":
            latest = decision
            latest_state = state
    returned_count = sum(1 for item in work_items if _text(_record(item).get("response_state")) == "returned")
    if latest_state == "no_followup":
        state = "no_followup_declared"
    elif latest_state == "decision_missing":
        state = "terminal_decision_missing" if states.get("followup_directive") else "decision_missing"
    elif latest_state == "followup_directive":
        state = "followup_directive_observed"
    elif states.get("call_agent_missing_directive"):
        state = "call_agent_missing_directive"
    elif states.get("blocked"):
        state = "blocked_declared"
    elif returned_count and returned_count == len(work_items) and states.get("no_followup") == len(work_items):
        state = "no_followup_declared"
    elif states.get("waiting_return"):
        state = "waiting_return"
    elif states.get("decision_invalid"):
        state = "decision_invalid"
    elif states.get("decision_missing"):
        state = "decision_missing"
    else:
        state = "unknown"
    return {
        "schema_id": "ion.agent_comms.run.followup_decision_state.v1",
        "state": state,
        "state_counts": states,
        "workpack_count": len(work_items),
        "returned_workpack_count": returned_count,
        "latest_decision": latest,
        "latest_decision_state": latest_state,
        **_no_authority(),
    }


def _run_directive_state(root: Path, run: Mapping[str, Any]) -> dict[str, Any]:
    ledger = _read_json(root / DIRECTIVE_LEDGER_PATH)
    processed = _record(ledger.get("processed"))
    pending: list[dict[str, Any]] = []
    processed_count = 0
    directive_count = 0
    finding_count = 0
    for message_path in _message_paths_for_threads(root, [str(item) for item in list(run.get("thread_ids") or []) if str(item)]):
        message = _read_repo_json(root, message_path)
        extracted = extract_agent_comms_directives(
            _text(message.get("body")),
            source_ref=message_path,
            source_message_id=_text(message.get("message_id")),
            from_role=_text(message.get("from_role")),
            scope_id=_text(run.get("run_id")),
        )
        finding_count += len(list(extracted.get("findings") or []))
        for directive in list(extracted.get("directives") or []):
            record = _record(directive)
            directive_id = _text(record.get("directive_id"))
            if not directive_id:
                continue
            directive_count += 1
            legacy_directive_id = _text(record.get("legacy_directive_id"))
            if directive_id in processed or (legacy_directive_id and legacy_directive_id in processed):
                processed_count += 1
                continue
            pending.append(
                {
                    "directive_id": directive_id,
                    "from_role": record.get("from_role"),
                    "agent": record.get("agent"),
                    "dispatch_mode": record.get("dispatch_mode"),
                    "objective": record.get("objective"),
                    "source_ref": message_path,
                    "source_message_id": record.get("source_message_id"),
                }
            )
    return {
        "schema_id": "ion.agent_comms.run.directive_state.v1",
        "directive_count": directive_count,
        "processed_directive_count": processed_count,
        "pending_directive_count": len(pending),
        "finding_count": finding_count,
        "pending_directives": pending[:8],
        **_no_authority(),
    }


def _run_operational_evidence(root: Path, run: Mapping[str, Any]) -> dict[str, Any]:
    message_paths = _message_paths_for_threads(root, [str(item) for item in list(run.get("thread_ids") or []) if str(item)])
    work_items = _work_items(root, run)
    followup_decision = _run_followup_decision_state(work_items)
    agent_responses = _agent_response_messages(root, run)
    task_return_count = sum(int(item.get("task_return_count") or 0) for item in work_items)
    accepted_return_count = sum(int(item.get("accepted_return_count") or 0) for item in work_items)
    latest_return_paths = [str(item.get("latest_return_packet_path")) for item in work_items if str(item.get("latest_return_packet_path") or "")]
    if task_return_count or agent_responses:
        operational_state = "response_observed"
    elif work_items:
        operational_state = "workpack_active"
    elif message_paths or run.get("root_message_ids"):
        operational_state = "messages_delivered"
    else:
        operational_state = "no_operational_evidence"
    return {
        "operational_state": operational_state,
        "operational_checks": [
            {"check": "messages_delivered", "ok": bool(message_paths or run.get("root_message_ids")), "count": len(message_paths)},
            {"check": "workpacks_tracked", "ok": bool(work_items), "count": len(work_items)},
            {"check": "task_returns_observed", "ok": task_return_count > 0, "count": task_return_count},
            {"check": "agent_messages_observed", "ok": bool(agent_responses), "count": len(agent_responses)},
            {
                "check": "followup_decision_observed",
                "ok": _text(followup_decision.get("state")) in {"followup_directive_observed", "no_followup_declared", "blocked_declared"},
                "count": sum(
                    int(value)
                    for key, value in _record(followup_decision.get("state_counts")).items()
                    if key in {"followup_directive", "no_followup", "blocked"}
                ),
            },
            {"check": "automation_limits_active", "ok": bool(_record(run.get("limits"))), "count": int(_record(run.get("limits")).get("max_directives") or 0)},
        ],
        "work_items": work_items,
        "followup_decision": followup_decision,
        "message_count": len(message_paths),
        "workpack_count": len(work_items),
        "task_return_count": task_return_count,
        "accepted_return_count": accepted_return_count,
        "agent_response_count": len(agent_responses),
        "latest_return_packet_path": latest_return_paths[-1] if latest_return_paths else "",
        "latest_agent_message": agent_responses[-1] if agent_responses else {},
    }


def _pid_matches_worker(pid: int, run_packet_path: str = "") -> bool:
    if pid <= 0:
        return False
    proc_cmdline = Path("/proc") / str(pid) / "cmdline"
    if proc_cmdline.exists():
        try:
            cmdline = proc_cmdline.read_bytes().replace(b"\0", b" ").decode("utf-8", errors="replace")
        except OSError:
            cmdline = ""
        if run_packet_path and run_packet_path in cmdline:
            return True
        return "ion_codex_queue_runner" in cmdline and "--worker-run" in cmdline
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _run_worker_runtime(root: Path, run: Mapping[str, Any], work_items: list[dict[str, Any]]) -> dict[str, Any]:
    work_by_path = {_text(item.get("workpack_path")): item for item in work_items if _text(item.get("workpack_path"))}
    workers: list[dict[str, Any]] = []
    for event in list(run.get("events") or []):
        row = _record(event)
        if row.get("event") != "request_specific_worker_start" or row.get("worker_started") is not True:
            continue
        pid_text = _text(row.get("pid") or row.get("worker_pid"))
        try:
            pid = int(pid_text or 0)
        except ValueError:
            pid = 0
        workpack_path = _text(row.get("workpack_path") or row.get("request_path"))
        work_item = _record(work_by_path.get(workpack_path))
        returned = bool(work_item.get("latest_return_packet_path") or int(work_item.get("task_return_count") or 0) > 0)
        run_packet_path = _text(row.get("run_packet_path"))
        running = (not returned) and _pid_matches_worker(pid, str(root / run_packet_path) if run_packet_path else "")
        if running:
            status = "running"
        elif returned:
            status = "returned"
        else:
            status = "started_no_return"
        workers.append(
            {
                "status": status,
                "active": running,
                "pid": pid or None,
                "started_at": row.get("created_at"),
                "workpack_path": workpack_path,
                "agent_role_id": work_item.get("agent_role_id"),
                "agent_display_name": work_item.get("agent_display_name"),
                "work_request_status": work_item.get("work_request_status"),
                "response_state": work_item.get("response_state"),
                "latest_return_packet_path": work_item.get("latest_return_packet_path"),
                "run_packet_path": run_packet_path,
                "queue_runner_result": row.get("queue_runner_result"),
                "finding": row.get("finding"),
            }
        )
    active_workers = [worker for worker in workers if worker.get("active") is True]
    latest_worker = workers[-1] if workers else {}
    return {
        "schema_id": "ion.agent_comms.run.worker_runtime.v1",
        "active_worker_count": len(active_workers),
        "worker_count": len(workers),
        "has_active_worker": bool(active_workers),
        "latest_worker": latest_worker,
        "active_workers": active_workers,
        "workers": workers[-8:],
        **_no_authority(),
    }


def _run_graph(root: Path, run: Mapping[str, Any], evidence: Mapping[str, Any]) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    node_ids: set[str] = set()
    edge_ids: set[str] = set()

    def add_node(node_id: str, kind: str, label: str, **extra: Any) -> str:
        if not node_id:
            return ""
        if node_id not in node_ids:
            node_ids.add(node_id)
            nodes.append({"id": node_id, "kind": kind, "label": label, **extra})
        return node_id

    def add_edge(source: str, target: str, kind: str, **extra: Any) -> None:
        if not source or not target:
            return
        edge_id = f"{source}->{target}:{kind}"
        if edge_id in edge_ids:
            return
        edge_ids.add(edge_id)
        edges.append({"id": edge_id, "source": source, "target": target, "kind": kind, **extra})

    run_id = _text(run.get("run_id"), "run")
    run_node = add_node(
        f"run:{run_id}",
        "run",
        _text(run.get("objective"), run_id),
        state=run.get("status"),
        evidence_path=_rel(_run_path(root, run_id), root),
        created_at=run.get("created_at"),
        updated_at=run.get("updated_at"),
    )
    for thread_id in [str(item) for item in list(run.get("thread_ids") or []) if str(item)]:
        thread_node = add_node(f"thread:{thread_id}", "thread", thread_id, state="active")
        add_edge(run_node, thread_node, "has_thread")
    message_by_path: dict[str, str] = {}
    message_by_id: dict[str, str] = {}
    for message_path in _message_paths_for_threads(root, [str(item) for item in list(run.get("thread_ids") or []) if str(item)]):
        message = _read_repo_json(root, message_path)
        message_id = _text(message.get("message_id"), _slug(message_path, "message"))
        message_node = add_node(
            f"message:{message_id}",
            "message",
            _text(message.get("subject") or message.get("summary"), message_id),
            state=message.get("status"),
            role=message.get("from_role"),
            message_kind=message.get("message_kind"),
            evidence_path=message_path,
            created_at=message.get("created_at"),
        )
        message_by_path[message_path] = message_node
        message_by_id[message_id] = message_node
        thread_id = _text(message.get("thread_id"))
        if thread_id:
            add_edge(f"thread:{thread_id}", message_node, "contains_message")
        if message_id in [str(item) for item in list(run.get("root_message_ids") or []) if str(item)]:
            add_edge(run_node, message_node, "root_message")
        parent_id = _text(message.get("parent_message_id"))
        if parent_id:
            add_edge(f"message:{parent_id}", message_node, "reply")
    return_message_ids = _record(run.get("return_message_ids"))
    for item in list(evidence.get("work_items") or []):
        work = _record(item)
        workpack_path = _text(work.get("workpack_path"))
        request_id = _text(work.get("request_id"), _slug(workpack_path, "workpack"))
        work_node = add_node(
            f"workpack:{request_id}",
            "workpack",
            _text(work.get("agent_display_name") or work.get("agent_role_id"), request_id),
            state=work.get("response_state"),
            role=work.get("agent_role_id"),
            evidence_path=workpack_path,
            status=work.get("work_request_status"),
        )
        add_edge(run_node, work_node, "tracks_workpack")
        for message_node in list(message_by_path.values()):
            message = _read_repo_json(root, str(next((path for path, node in message_by_path.items() if node == message_node), "")))
            if workpack_path and workpack_path in [str(ref) for ref in list(message.get("source_refs") or []) + list(message.get("artifact_refs") or [])]:
                add_edge(message_node, work_node, "references_workpack")
        for return_path in [str(path) for path in list(work.get("return_packet_paths") or []) if str(path)]:
            packet = _read_repo_json(root, return_path)
            return_node = add_node(
                f"return:{_slug(return_path, 'return')}",
                "return",
                _task_return_summary(packet),
                state="accepted" if packet.get("accepted_for_carrier_intake") is True else "observed",
                evidence_path=return_path,
                accepted_for_carrier_intake=packet.get("accepted_for_carrier_intake"),
                created_at=packet.get("created_at"),
            )
            add_edge(work_node, return_node, "produced_return")
            synced_message_id = _text(return_message_ids.get(return_path))
            if synced_message_id:
                synced_node = message_by_id.get(synced_message_id) or add_node(
                    f"message:{synced_message_id}",
                    "message",
                    synced_message_id,
                    state="sent",
                    evidence_path=_record(run.get("return_message_paths")).get(return_path),
                )
                add_edge(return_node, synced_node, "synced_reply")

    limits = _record(run.get("limits"))
    max_nodes = _int_limit(limits.get("max_graph_nodes"), DEFAULT_MAX_GRAPH_NODES, 8, 2000)
    max_edges = _int_limit(limits.get("max_graph_edges"), DEFAULT_MAX_GRAPH_EDGES, 8, 3000)
    node_count = len(nodes)
    edge_count = len(edges)
    return {
        "schema_id": "ion.agent_comms.run_graph.v1",
        "node_count": node_count,
        "edge_count": edge_count,
        "truncated": node_count > max_nodes or edge_count > max_edges,
        "visible_node_count": min(node_count, max_nodes),
        "visible_edge_count": min(edge_count, max_edges),
        "nodes": nodes[:max_nodes],
        "edges": edges[:max_edges],
        "limits": {"max_graph_nodes": max_nodes, "max_graph_edges": max_edges},
        **_no_authority(),
    }


def _run_policy_gate(run: Mapping[str, Any], evidence: Mapping[str, Any], graph: Mapping[str, Any]) -> dict[str, Any]:
    limits = _record(run.get("limits"))
    work_items = [_record(item) for item in list(evidence.get("work_items") or [])]
    agent_roles = {
        *[str(role) for role in list(run.get("target_roles") or []) if str(role)],
        *[str(item.get("agent_role_id")) for item in work_items if str(item.get("agent_role_id") or "")],
    }
    latest_message = _record(evidence.get("latest_agent_message"))
    if latest_message.get("from_role"):
        agent_roles.add(str(latest_message.get("from_role")))
    checks = [
        {
            "limit": "max_agents",
            "used": len(agent_roles),
            "max": _int_limit(limits.get("max_agents"), DEFAULT_MAX_AGENTS_PER_RUN, 1, 100),
        },
        {
            "limit": "max_workpacks",
            "used": int(evidence.get("workpack_count") or 0),
            "max": _int_limit(limits.get("max_workpacks"), DEFAULT_MAX_WORKPACKS_PER_RUN, 1, 500),
        },
        {
            "limit": "max_directives",
            "used": int(_record(run.get("usage")).get("processed_directive_count") or 0),
            "max": _int_limit(limits.get("max_directives"), 3, 1, 25),
        },
        {
            "limit": "automation_prompt_limit",
            "used": int(_record(run.get("usage")).get("processed_directive_count") or 0),
            "max": _int_limit(limits.get("automation_prompt_limit"), 6, 1, 100),
        },
        {
            "limit": "max_graph_nodes",
            "used": int(graph.get("node_count") or 0),
            "max": _int_limit(limits.get("max_graph_nodes"), DEFAULT_MAX_GRAPH_NODES, 8, 2000),
        },
        {
            "limit": "max_graph_edges",
            "used": int(graph.get("edge_count") or 0),
            "max": _int_limit(limits.get("max_graph_edges"), DEFAULT_MAX_GRAPH_EDGES, 8, 3000),
        },
    ]
    enriched_checks = [{**check, "ok": int(check["used"]) <= int(check["max"])} for check in checks]
    blocked = [check for check in enriched_checks if not check["ok"]]
    return {
        "schema_id": "ion.agent_comms.run_policy_gate.v1",
        "state": "blocked_by_policy" if blocked else "within_limits",
        "ok": not blocked,
        "checks": enriched_checks,
        "blocked_limits": [str(check["limit"]) for check in blocked],
        "policy": "Limits bound courier automation only. Agents still decide communication by writing visible messages or directive packets; this gate only constrains pickup, workpack fanout, graph size, prompts, and visible proof.",
        **_no_authority(),
    }


def _task_return_message_body(root: Path, run: Mapping[str, Any], item: Mapping[str, Any], return_path: str, packet: Mapping[str, Any]) -> str:
    output = _task_return_full_output_text(root, item, packet)
    lines = [
        f"Real task return observed for comms run {run.get('run_id')}.",
        "",
        f"Agent: {_text(item.get('agent_display_name') or item.get('agent_role_id'), 'agent')}",
        f"Result: {_task_return_summary(packet)}",
        f"Accepted for carrier intake: {packet.get('accepted_for_carrier_intake')}",
        f"Work request: {item.get('workpack_path')}",
        f"Return packet: {return_path}",
    ]
    if output:
        lines.extend(["", "Return output:", output[:24000]])
    return "\n".join(lines)


def sync_run_task_returns(root: str | Path | None, run: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _root(root)
    updated = dict(run)
    evidence = _run_operational_evidence(shell_root, updated)
    return_message_ids = _record(updated.get("return_message_ids"))
    return_message_paths = _record(updated.get("return_message_paths"))
    synced: list[dict[str, Any]] = []
    created_sync_count = 0
    refreshed_sync_count = 0
    for item in list(evidence.get("work_items") or []):
        item_record = _record(item)
        for return_path in [str(path) for path in list(item_record.get("return_packet_paths") or []) if str(path)]:
            packet = _read_repo_json(shell_root, return_path)
            if not packet:
                continue
            body = _task_return_message_body(shell_root, updated, item_record, return_path, packet)
            if return_path in return_message_ids:
                message_path = _text(return_message_paths.get(return_path))
                message = _read_repo_json(shell_root, message_path)
                existing_body = _text(message.get("body"))
                if message and body and body != existing_body and len(body) > len(existing_body):
                    message["body"] = body
                    message["updated_at"] = _now()
                    _write_json(shell_root / message_path, message)
                    synced.append(
                        {
                            "return_packet_path": return_path,
                            "message_id": return_message_ids.get(return_path),
                            "message_path": message_path,
                            "refreshed": True,
                        }
                    )
                    refreshed_sync_count += 1
                continue
            sent = send_agent_message(
                shell_root,
                {
                    "channel_id": "team",
                    "thread_id": _text(list(updated.get("thread_ids") or [None])[0]),
                    "from_role": _text(item_record.get("agent_role_id"), "role.steward"),
                    "to_roles": [_text(updated.get("from_role"), "operator")],
                    "message_kind": "answer",
                    "subject": f"Task return observed: {_text(item_record.get('agent_display_name') or item_record.get('agent_role_id'), 'agent')}",
                    "summary": _task_return_summary(packet),
                    "body": body,
                    "parent_message_id": _text(list(updated.get("root_message_ids") or [None])[0]),
                    "source_refs": [_text(item_record.get("workpack_path"))],
                    "artifact_refs": [return_path],
                    "routing_policy": "task_return_packet_projection",
                    "visibility": "team_projection",
                    "requires_response": False,
                },
            )
            if not sent.get("ok"):
                continue
            return_message_ids[return_path] = sent.get("message_id")
            return_message_paths[return_path] = sent.get("message_path")
            updated.setdefault("message_paths", [])
            if sent.get("message_path") and sent.get("message_path") not in updated["message_paths"]:
                updated["message_paths"].append(sent.get("message_path"))
            updated.setdefault("thread_ids", [])
            if sent.get("thread_id") and sent.get("thread_id") not in updated["thread_ids"]:
                updated["thread_ids"].append(sent.get("thread_id"))
            synced.append({"return_packet_path": return_path, "message_id": sent.get("message_id"), "message_path": sent.get("message_path")})
            created_sync_count += 1
    updated["return_message_ids"] = return_message_ids
    updated["return_message_paths"] = return_message_paths
    updated["updated_at"] = _now() if synced else updated.get("updated_at")
    usage = _record(updated.get("usage"))
    usage["agent_return_message_count"] = len(return_message_ids)
    if refreshed_sync_count:
        usage["agent_return_refresh_count"] = int(usage.get("agent_return_refresh_count") or 0) + refreshed_sync_count
    updated["usage"] = usage
    updated = _sync_usage_observed_counts(updated)
    return {
        "ok": True,
        "run": updated,
        "return_sync_count": len(synced),
        "created_return_sync_count": created_sync_count,
        "refreshed_return_sync_count": refreshed_sync_count,
        "synced_returns": synced,
        "operational_evidence": _run_operational_evidence(shell_root, updated),
        **_no_authority(),
    }


def _no_authority() -> dict[str, bool]:
    return {
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def _blocked(schema_id: str, finding: str, **extra: Any) -> dict[str, Any]:
    return {"schema_id": schema_id, "ok": False, "finding": finding, **extra, **_no_authority()}


def _run_path(root: Path, run_id: str) -> Path:
    return root / RUNS_DIR / f"{_slug(run_id, 'run')}.json"


def _load_index(root: Path) -> dict[str, Any]:
    index = _read_json(root / RUN_INDEX_PATH)
    if index:
        index.setdefault("runs", {})
        return index
    return {
        "schema_id": "ion.agent_comms.run_index.v1",
        "created_at": _now(),
        "updated_at": _now(),
        "runs": {},
        **_no_authority(),
    }


def _save_index(root: Path, index: Mapping[str, Any]) -> None:
    value = dict(index)
    value["updated_at"] = _now()
    _write_json(root / RUN_INDEX_PATH, value)


def _save_run(root: Path, run: Mapping[str, Any]) -> str:
    run = _finalize_run_if_idle(root, run, reason="save_run") if run.get("schema_id") == RUN_SCHEMA_ID else _sync_usage_observed_counts(run)
    path = _run_path(root, str(run.get("run_id") or "run"))
    _write_json(path, run)
    index = _load_index(root)
    index.setdefault("runs", {})[str(run.get("run_id"))] = {
        "run_id": run.get("run_id"),
        "run_path": _rel(path, root),
        "status": run.get("status"),
        "objective": run.get("objective"),
        "target_roles": list(run.get("target_roles") or []),
        "dispatch_mode": run.get("dispatch_mode"),
        "created_at": run.get("created_at"),
        "updated_at": run.get("updated_at"),
    }
    _save_index(root, index)
    return _rel(path, root)


def _receipt(root: Path, action: str, payload: Mapping[str, Any]) -> str:
    path = root / RUN_RECEIPT_DIR / f"{_stamp()}_{_slug(action, 'run')}.json"
    _write_json(path, payload)
    return _rel(path, root)


def _load_run(root: Path, run_id: str) -> dict[str, Any]:
    return _read_json(_run_path(root, run_id))


def _run_limits(data: Mapping[str, Any]) -> dict[str, int]:
    return {
        "max_directives": _int_limit(data.get("max_directives"), 3, 1, 25),
        "max_pickups": _int_limit(data.get("max_pickups"), 12, 1, 100),
        "max_agents": _int_limit(data.get("max_agents"), DEFAULT_MAX_AGENTS_PER_RUN, 1, 100),
        "max_workpacks": _int_limit(data.get("max_workpacks"), DEFAULT_MAX_WORKPACKS_PER_RUN, 1, 500),
        "max_graph_nodes": _int_limit(data.get("max_graph_nodes"), DEFAULT_MAX_GRAPH_NODES, 8, 2000),
        "max_graph_edges": _int_limit(data.get("max_graph_edges"), DEFAULT_MAX_GRAPH_EDGES, 8, 3000),
        "automation_window_minutes": _int_limit(data.get("automation_window_minutes"), 60, 1, 1440),
        "automation_prompt_limit": _int_limit(data.get("automation_prompt_limit"), 6, 1, 100),
        "automation_time_budget_minutes": _int_limit(data.get("automation_time_budget_minutes"), 120, 1, 1440),
        "automation_prompt_char_limit": _int_limit(data.get("automation_prompt_char_limit"), 6000, 1, 20000),
    }


def _agent_followup_contract(limits: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "Agent follow-up contract:",
            "- End every return with exactly one follow-up decision: either an executable `ion-agent-comms` directive or a `ion-agent-decision` no-followup block.",
            "- If another ION agent is needed, write exactly one fenced `ion-agent-comms` JSON block in your return.",
            "- The directive must include schema_id, from_role, agent, dispatch_mode, objective, body, and source_refs.",
            "- If no other agent is needed, write exactly one fenced `ion-agent-decision` JSON block with schema_id `ion.agent_comms.followup_decision.v1`, decision `no_followup`, reason, and evidence_refs.",
            f"- Current run limits: max_directives={limits.get('max_directives')} max_workpacks={limits.get('max_workpacks')} max_agents={limits.get('max_agents')}.",
            "- Do not invent replies for other agents; automation will route only explicit directives and visible packet evidence.",
        ]
    )


def _resolve_target_roles(root: Path, payload: Mapping[str, Any], body: str) -> list[str]:
    roles = _list(payload.get("target_roles") or payload.get("to_roles") or payload.get("agents") or payload.get("agent"))
    if roles:
        return roles
    mentions = extract_agent_mentions(root, body)
    return [str(role) for role in list(mentions.get("roles") or []) if str(role)]


def _message_paths_for_threads(root: Path, thread_ids: list[str]) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()
    for thread_id in thread_ids:
        messages_dir = root / AGENT_COMMS_ROOT / "threads" / _slug(thread_id, "thread") / "messages"
        if not messages_dir.exists():
            continue
        for path in sorted(messages_dir.glob("*.json")):
            rel = _rel(path, root)
            if rel not in seen:
                seen.add(rel)
                paths.append(rel)
    return paths


def start_agent_comms_run(root: str | Path | None, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    shell_root = _root(root)
    data = dict(payload or {})
    objective = _text(data.get("objective") or data.get("subject") or data.get("task"))
    body = _text(data.get("body") or data.get("message") or objective)
    if not objective:
        return _blocked(RUN_RESULT_SCHEMA_ID, "objective_required")
    if not body:
        return _blocked(RUN_RESULT_SCHEMA_ID, "body_required")
    dispatch_mode = _text(data.get("dispatch_mode"), "comms_only")
    if dispatch_mode not in ALLOWED_RUN_DISPATCH_MODES:
        return _blocked(RUN_RESULT_SCHEMA_ID, "unsupported_dispatch_mode", dispatch_mode=dispatch_mode)
    target_roles = _resolve_target_roles(shell_root, data, body)
    if not target_roles:
        target_roles = ["role.steward"]
    limits = _run_limits(data)
    attached_workpack_paths = _list(data.get("workpack_paths") or data.get("existing_workpack_paths") or data.get("evidence_workpack_paths"))
    unique_target_count = len({str(role) for role in target_roles if str(role)})
    if unique_target_count > limits["max_agents"]:
        return _blocked(
            RUN_RESULT_SCHEMA_ID,
            "run_policy_limit_exceeded",
            limit="max_agents",
            used=unique_target_count,
            max=limits["max_agents"],
        )
    prospective_workpacks = len({str(path) for path in attached_workpack_paths if str(path)})
    if dispatch_mode != "comms_only":
        prospective_workpacks += unique_target_count
    if prospective_workpacks > limits["max_workpacks"]:
        return _blocked(
            RUN_RESULT_SCHEMA_ID,
            "run_policy_limit_exceeded",
            limit="max_workpacks",
            used=prospective_workpacks,
            max=limits["max_workpacks"],
        )
    now = _now()
    run_id = _text(data.get("run_id")) or f"agent_run_{_stamp()}_{_slug(objective, 'task')}"
    automation_id = _text(data.get("automation_id"), f"agent_comms_run:{run_id}")
    from_role = _text(data.get("from_role"), "operator")
    channel_id = _text(data.get("channel_id"), "team")
    thread_ids: list[str] = []
    message_ids: list[str] = []
    message_paths: list[str] = []
    workpack_paths: list[str] = []
    spawn_results: list[dict[str, Any]] = []
    body_with_run = "\n\n".join(
        [
            body,
            f"Comms run: {run_id}",
            f"Objective: {objective}",
            f"Limits: max_directives={limits['max_directives']} automation_prompt_limit={limits['automation_prompt_limit']} window_minutes={limits['automation_window_minutes']}",
            _agent_followup_contract(limits),
        ]
    )
    if dispatch_mode == "comms_only":
        comms_result = send_agent_message(
            shell_root,
            {
                "channel_id": channel_id,
                "thread_id": _text(data.get("thread_id")) or None,
                "from_role": from_role,
                "to_roles": target_roles,
                "message_kind": _text(data.get("message_kind"), "task_dispatch"),
                "subject": _text(data.get("subject"), objective),
                "body": body_with_run,
                "summary": objective,
                "requires_response": True,
                "source_refs": _list(data.get("source_refs") or data.get("context_refs")),
                "artifact_refs": _list(data.get("artifact_refs") or data.get("evidence_refs")),
            },
        )
        spawn_results.append({"dispatch_mode": "comms_only", "comms_result": comms_result})
    else:
        for role in target_roles:
            spawn_result = execute_agent_spawn_template(
                shell_root,
                {
                    "template_id": _text(data.get("template_id"), "agent_workpack_decision"),
                    "dispatch_mode": dispatch_mode,
                    "dispatch_source": "automation",
                    "automation_id": automation_id,
                    **limits,
                    "agent": role,
                    "from_role": from_role,
                    "domain_id": _text(data.get("domain_id")),
                    "objective": objective,
                    "body": body_with_run,
                    "subject": _text(data.get("subject"), objective),
                    "message_kind": _text(data.get("message_kind"), "task_dispatch"),
                    "channel_id": channel_id,
                    "source_refs": _list(data.get("source_refs") or data.get("context_refs")),
                    "artifact_refs": _list(data.get("artifact_refs") or data.get("evidence_refs")),
                    "planned_writes": _list(data.get("planned_writes")),
                    "planned_artifacts": _list(data.get("planned_artifacts")),
                },
            )
            spawn_results.append(spawn_result)
    for result in spawn_results:
        comms_result = _record(result.get("comms_result"))
        if comms_result.get("message_id"):
            message_ids.append(str(comms_result.get("message_id")))
        if comms_result.get("message_path"):
            message_paths.append(str(comms_result.get("message_path")))
        if comms_result.get("thread_id") and str(comms_result.get("thread_id")) not in thread_ids:
            thread_ids.append(str(comms_result.get("thread_id")))
        workpack_path = _text(result.get("workpack_path") or _record(result.get("invocation_result")).get("codex_work_request_path"))
        if workpack_path:
            workpack_paths.append(workpack_path)
    for workpack_path in attached_workpack_paths:
        if workpack_path not in workpack_paths:
            workpack_paths.append(workpack_path)
    ok = bool(spawn_results) and all(_record(result.get("comms_result")).get("ok", result.get("ok")) for result in spawn_results)
    run = {
        "schema_id": RUN_SCHEMA_ID,
        "run_id": run_id,
        "created_at": now,
        "updated_at": now,
        "status": "active" if ok else "blocked",
        "objective": objective,
        "body": body,
        "initiated_by": _text(data.get("initiated_by"), "operator"),
        "from_role": from_role,
        "target_roles": target_roles,
        "dispatch_mode": dispatch_mode,
        "template_id": _text(data.get("template_id"), "agent_workpack_decision") if dispatch_mode != "comms_only" else "",
        "automation_id": automation_id,
        "limits": limits,
        "usage": {
            "pickup_count": 0,
            "processed_directive_count": 0,
            "already_processed_count": 0,
            "finding_count": 0,
            "spawned_message_count": len(message_ids),
            "queued_workpack_count": len(workpack_paths),
        },
        "thread_ids": thread_ids,
        "root_message_ids": message_ids,
        "message_paths": message_paths,
        "workpack_paths": workpack_paths,
        "return_message_ids": {},
        "return_message_paths": {},
        "events": [
            {
                "event": "run_started",
                "created_at": now,
                "dispatch_mode": dispatch_mode,
                "target_roles": target_roles,
                "message_ids": message_ids,
                "workpack_paths": workpack_paths,
            }
        ],
        "spawn_results": spawn_results,
        "policy": "Run pickup only processes explicit ion-agent-comms directive blocks inside run threads. It does not invent agent replies or decide when agents communicate.",
        **_no_authority(),
    }
    return_sync = sync_run_task_returns(shell_root, run)
    run = _record(return_sync.get("run"))
    if int(return_sync.get("return_sync_count") or 0) > 0:
        run.setdefault("events", []).append(
            {
                "event": "return_sync",
                "created_at": _now(),
                "return_sync_count": return_sync.get("return_sync_count"),
                "synced_returns": return_sync.get("synced_returns"),
            }
        )
    operational_evidence = _record(return_sync.get("operational_evidence")) or _run_operational_evidence(shell_root, run)
    graph = _run_graph(shell_root, run, operational_evidence)
    policy_gate = _run_policy_gate(run, operational_evidence, graph)
    run_path = _save_run(shell_root, run)
    receipt_payload = {
        "schema_id": RUN_RESULT_SCHEMA_ID,
        "ok": ok,
        "created_at": now,
        "run": run,
        "run_path": run_path,
        "return_sync_count": return_sync.get("return_sync_count"),
        "synced_returns": return_sync.get("synced_returns"),
        "operational_evidence": operational_evidence,
        "graph": graph,
        "policy_gate": policy_gate,
        **_no_authority(),
    }
    receipt_path = _receipt(shell_root, "run_start", receipt_payload)
    return {
        "schema_id": RUN_RESULT_SCHEMA_ID,
        "ok": ok,
        "run_id": run_id,
        "run_path": run_path,
        "receipt_path": receipt_path,
        "thread_ids": thread_ids,
        "message_ids": message_ids,
        "message_paths": message_paths,
        "workpack_paths": workpack_paths,
        "return_sync_count": return_sync.get("return_sync_count"),
        "synced_returns": return_sync.get("synced_returns"),
        "operational_evidence": operational_evidence,
        "graph": graph,
        "policy_gate": policy_gate,
        "spawn_results": spawn_results,
        **_no_authority(),
    }


def pickup_agent_comms_run(root: str | Path | None, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    shell_root = _root(root)
    data = dict(payload or {})
    run_id = _text(data.get("run_id"))
    if not run_id:
        return _blocked(RUN_PICKUP_SCHEMA_ID, "run_id_required")
    run = _load_run(shell_root, run_id)
    if not run:
        return _blocked(RUN_PICKUP_SCHEMA_ID, "run_not_found", run_id=run_id)
    if _text(run.get("status")) != "active":
        original_status = _text(run.get("status"))
        return_sync = sync_run_task_returns(shell_root, run)
        if int(return_sync.get("return_sync_count") or 0) > 0:
            run = _record(return_sync.get("run"))
            now = _now()
            run.setdefault("events", []).append(
                {
                    "event": "return_sync",
                    "created_at": now,
                    "return_sync_count": return_sync.get("return_sync_count"),
                    "synced_returns": return_sync.get("synced_returns"),
                }
            )
            completion = _run_completion_state(shell_root, run, evidence=return_sync.get("operational_evidence"))
            if original_status == "complete" and _text(completion.get("state")) in {"pending_directive", "ready_to_start_worker"}:
                run["status"] = "active"
                run["updated_at"] = now
                run.setdefault("events", []).append(
                    {
                        "event": "run_reopened",
                        "created_at": now,
                        "reason": "return_sync_exposed_pending_work",
                        "completion_state": completion.get("state"),
                    }
                )
                _save_run(shell_root, run)
            elif original_status in {"limit_reached", "blocked_by_limit", "blocked_by_policy", "complete"}:
                run["updated_at"] = now
                run_path = _save_run(shell_root, run)
                evidence = _record(return_sync.get("operational_evidence")) or _run_operational_evidence(shell_root, run)
                graph = _run_graph(shell_root, run, evidence)
                policy_gate = _run_policy_gate(run, evidence, graph)
                receipt_payload = {
                    "schema_id": RUN_PICKUP_SCHEMA_ID,
                    "ok": True,
                    "created_at": now,
                    "run_id": run_id,
                    "run_path": run_path,
                    "finding": "run_complete" if _text(run.get("status")) == "complete" else "run_not_active_return_sync_complete",
                    "processed_directive_count": 0,
                    "already_processed_count": 0,
                    "finding_count": 0,
                    "return_sync_count": return_sync.get("return_sync_count"),
                    "synced_returns": return_sync.get("synced_returns"),
                    "operational_evidence": evidence,
                    "graph": graph,
                    "policy_gate": policy_gate,
                    "results": [],
                    **_no_authority(),
                }
                receipt_path = _receipt(shell_root, "run_pickup", receipt_payload)
                return {**receipt_payload, "receipt_path": receipt_path}
        if _text(run.get("status")) != "active":
            if _text(run.get("status")) == "complete":
                now = _now()
                evidence = _run_operational_evidence(shell_root, run)
                graph = _run_graph(shell_root, run, evidence)
                policy_gate = _run_policy_gate(run, evidence, graph)
                receipt_payload = {
                    "schema_id": RUN_PICKUP_SCHEMA_ID,
                    "ok": True,
                    "created_at": now,
                    "run_id": run_id,
                    "run_path": _rel(_run_path(shell_root, run_id), shell_root),
                    "finding": "run_complete",
                    "processed_directive_count": 0,
                    "already_processed_count": 0,
                    "finding_count": 0,
                    "return_sync_count": 0,
                    "synced_returns": [],
                    "operational_evidence": evidence,
                    "graph": graph,
                    "policy_gate": policy_gate,
                    "results": [],
                    **_no_authority(),
                }
                receipt_path = _receipt(shell_root, "run_pickup", receipt_payload)
                return {**receipt_payload, "receipt_path": receipt_path}
            return _blocked(RUN_PICKUP_SCHEMA_ID, "run_not_active", run_id=run_id, status=run.get("status"))
    limits = _record(run.get("limits"))
    usage = _record(run.get("usage"))
    max_pickups = _int_limit(limits.get("max_pickups"), 12, 1, 100)
    pickup_before = int(usage.get("pickup_count") or 0)
    if pickup_before >= max_pickups:
        return_sync = sync_run_task_returns(shell_root, run)
        run = _record(return_sync.get("run"))
        now = _now()
        evidence = _run_operational_evidence(shell_root, run)
        graph = _run_graph(shell_root, run, evidence)
        policy_gate = _run_policy_gate(run, evidence, graph)
        if _text(evidence.get("operational_state")) == "response_observed" or int(return_sync.get("return_sync_count") or 0) > 0:
            run["updated_at"] = now
            run.setdefault("events", []).append(
                {
                    "event": "pickup_limit_reached_response_observed",
                    "created_at": now,
                    "limit": "max_pickups",
                    "used": pickup_before,
                    "max": max_pickups,
                    "return_sync_count": return_sync.get("return_sync_count"),
                    "synced_returns": return_sync.get("synced_returns"),
                }
            )
            run_path = _save_run(shell_root, run)
            receipt_payload = {
                "schema_id": RUN_PICKUP_SCHEMA_ID,
                "ok": True,
                "created_at": now,
                "run_id": run_id,
                "run_path": run_path,
                "finding": "max_pickups_reached_response_observed",
                "processed_directive_count": 0,
                "already_processed_count": 0,
                "finding_count": 0,
                "return_sync_count": return_sync.get("return_sync_count"),
                "synced_returns": return_sync.get("synced_returns"),
                "operational_evidence": evidence,
                "policy_gate": policy_gate,
                "graph": graph,
                "results": [],
                **_no_authority(),
            }
            receipt_path = _receipt(shell_root, "run_pickup", receipt_payload)
            return {**receipt_payload, "receipt_path": receipt_path}
        run["status"] = "blocked_by_policy"
        run["updated_at"] = now
        run.setdefault("events", []).append(
            {
                "event": "pickup_blocked_by_policy",
                "created_at": now,
                "limit": "max_pickups",
                "used": pickup_before,
                "max": max_pickups,
                "return_sync_count": return_sync.get("return_sync_count"),
            }
        )
        run_path = _save_run(shell_root, run)
        return _blocked(
            RUN_PICKUP_SCHEMA_ID,
            "run_policy_limit_exceeded",
            run_id=run_id,
            run_path=run_path,
            limit="max_pickups",
            used=pickup_before,
            max=max_pickups,
            policy_gate=policy_gate,
            graph=graph,
            return_sync_count=return_sync.get("return_sync_count"),
            synced_returns=return_sync.get("synced_returns"),
        )
    max_directives = int(limits.get("max_directives") or 1)
    processed_before = int(usage.get("processed_directive_count") or 0)
    remaining = max_directives - processed_before
    if remaining <= 0:
        return_sync = sync_run_task_returns(shell_root, run)
        if int(return_sync.get("return_sync_count") or 0) > 0:
            run = _record(return_sync.get("run"))
            now = _now()
            run.setdefault("events", []).append(
                {
                    "event": "return_sync",
                    "created_at": now,
                    "return_sync_count": return_sync.get("return_sync_count"),
                    "synced_returns": return_sync.get("synced_returns"),
                }
            )
            run["updated_at"] = now
            run_path = _save_run(shell_root, run)
            receipt_payload = {
                "schema_id": RUN_PICKUP_SCHEMA_ID,
                "ok": True,
                "created_at": now,
                "run_id": run_id,
                "run_path": run_path,
                "processed_directive_count": 0,
                "already_processed_count": 0,
                "finding_count": 0,
                "return_sync_count": return_sync.get("return_sync_count"),
                "synced_returns": return_sync.get("synced_returns"),
                "operational_evidence": return_sync.get("operational_evidence"),
                "results": [],
                **_no_authority(),
            }
            receipt_path = _receipt(shell_root, "run_pickup", receipt_payload)
            return {**receipt_payload, "receipt_path": receipt_path}
        run["status"] = "blocked_by_limit"
        run["updated_at"] = _now()
        run.setdefault("events", []).append({"event": "pickup_blocked_by_limit", "created_at": run["updated_at"], "max_directives": max_directives})
        run_path = _save_run(shell_root, run)
        return _blocked(RUN_PICKUP_SCHEMA_ID, "run_directive_limit_reached", run_id=run_id, run_path=run_path, max_directives=max_directives)
    pre_directive_return_sync = sync_run_task_returns(shell_root, run)
    pre_directive_return_sync_count = int(pre_directive_return_sync.get("return_sync_count") or 0)
    if pre_directive_return_sync_count:
        run = _record(pre_directive_return_sync.get("run"))
        usage = _record(run.get("usage"))
        run.setdefault("events", []).append(
            {
                "event": "return_sync_before_directive_pickup",
                "created_at": _now(),
                "return_sync_count": pre_directive_return_sync_count,
                "synced_returns": pre_directive_return_sync.get("synced_returns"),
            }
        )
    max_workpacks = _int_limit(limits.get("max_workpacks"), DEFAULT_MAX_WORKPACKS_PER_RUN, 1, 500)
    current_workpack_count = len({str(path) for path in list(run.get("workpack_paths") or []) if str(path)})
    workpack_capacity = max_workpacks - current_workpack_count
    if workpack_capacity <= 0:
        return_sync = sync_run_task_returns(shell_root, run)
        run = _record(return_sync.get("run"))
        now = _now()
        evidence = _run_operational_evidence(shell_root, run)
        graph = _run_graph(shell_root, run, evidence)
        policy_gate = _run_policy_gate(run, evidence, graph)
        return_sync_count = pre_directive_return_sync_count + int(return_sync.get("return_sync_count") or 0)
        synced_returns = list(pre_directive_return_sync.get("synced_returns") or []) + list(return_sync.get("synced_returns") or [])
        usage["pickup_count"] = int(usage.get("pickup_count") or 0) + 1
        run["usage"] = usage
        run["updated_at"] = now
        if return_sync_count:
            event = "pickup_return_sync_at_workpack_capacity"
            finding = "workpack_capacity_reached_return_sync_complete"
        elif _text(evidence.get("operational_state")) == "response_observed":
            event = "pickup_response_observed_at_workpack_capacity"
            finding = "workpack_capacity_reached_response_observed"
        else:
            event = "pickup_waiting_for_workpack_return"
            finding = "workpack_capacity_reached_waiting_for_returns"
        run.setdefault("events", []).append(
            {
                "event": event,
                "created_at": now,
                "limit": "max_workpacks",
                "used": current_workpack_count,
                "max": max_workpacks,
                "return_sync_count": return_sync_count,
                "synced_returns": synced_returns,
            }
        )
        run_path = _save_run(shell_root, run)
        receipt_payload = {
            "schema_id": RUN_PICKUP_SCHEMA_ID,
            "ok": True,
            "created_at": now,
            "run_id": run_id,
            "run_path": run_path,
            "finding": finding,
            "processed_directive_count": 0,
            "already_processed_count": 0,
            "finding_count": 0,
            "return_sync_count": return_sync_count,
            "synced_returns": synced_returns,
            "operational_evidence": evidence,
            "policy_gate": policy_gate,
            "graph": graph,
            "results": [],
            **_no_authority(),
        }
        receipt_path = _receipt(shell_root, "run_pickup", receipt_payload)
        return {**receipt_payload, "receipt_path": receipt_path}
    requested = max(1, min(int(data.get("max_directives") or remaining), remaining, workpack_capacity))
    thread_ids = [str(item) for item in list(run.get("thread_ids") or []) if str(item)]
    message_paths = _message_paths_for_threads(shell_root, thread_ids)
    results: list[dict[str, Any]] = []
    processed_now = 0
    already_now = 0
    findings_now = 0
    workpack_paths: list[str] = []
    spawned_message_ids: list[str] = []
    spawned_message_paths: list[str] = []
    spawned_thread_ids: list[str] = []
    for message_path in message_paths:
        if processed_now >= requested:
            break
        result = process_agent_comms_directives(
            shell_root,
            {
                "message_path": message_path,
                "max_directives": requested - processed_now,
                "run_id": run_id,
                "run_objective": run.get("objective"),
                "followup_contract": _agent_followup_contract(limits),
                "automation_id": run.get("automation_id"),
                "automation_window_minutes": limits.get("automation_window_minutes"),
                "automation_prompt_limit": limits.get("automation_prompt_limit"),
                "automation_time_budget_minutes": limits.get("automation_time_budget_minutes"),
                "automation_prompt_char_limit": limits.get("automation_prompt_char_limit"),
            },
        )
        results.append(result)
        processed_now += int(result.get("processed_directive_count") or 0)
        already_now += int(result.get("already_processed_count") or 0)
        findings_now += int(result.get("finding_count") or 0)
        for row in list(result.get("results") or []):
            record = _record(row.get("ledger_record"))
            if record.get("workpack_path"):
                workpack_paths.append(str(record.get("workpack_path")))
            if record.get("spawned_comms_message_id"):
                spawned_message_ids.append(str(record.get("spawned_comms_message_id")))
            if record.get("comms_message_path"):
                spawned_message_paths.append(str(record.get("comms_message_path")))
            if record.get("thread_id"):
                spawned_thread_ids.append(str(record.get("thread_id")))
    now = _now()
    usage["pickup_count"] = int(usage.get("pickup_count") or 0) + 1
    usage["processed_directive_count"] = processed_before + processed_now
    usage["already_processed_count"] = int(usage.get("already_processed_count") or 0) + already_now
    usage["finding_count"] = int(usage.get("finding_count") or 0) + findings_now
    run["usage"] = usage
    run["updated_at"] = now
    run.setdefault("workpack_paths", [])
    for path in workpack_paths:
        if path not in run["workpack_paths"]:
            run["workpack_paths"].append(path)
    run.setdefault("message_paths", [])
    for path in spawned_message_paths:
        if path not in run["message_paths"]:
            run["message_paths"].append(path)
    run.setdefault("thread_ids", [])
    for thread_id in spawned_thread_ids:
        if thread_id not in run["thread_ids"]:
            run["thread_ids"].append(thread_id)
    run = _sync_usage_observed_counts(run)
    return_sync = sync_run_task_returns(shell_root, run)
    run = _record(return_sync.get("run"))
    run.setdefault("events", []).append(
        {
            "event": "directive_pickup",
            "created_at": now,
            "requested_directives": requested,
            "processed_directive_count": processed_now,
            "already_processed_count": already_now,
            "finding_count": findings_now,
            "source_message_count": len(message_paths),
            "spawned_message_ids": spawned_message_ids,
            "spawned_message_paths": spawned_message_paths,
            "spawned_thread_ids": spawned_thread_ids,
            "workpack_paths": workpack_paths,
            "return_sync_count": pre_directive_return_sync_count + int(return_sync.get("return_sync_count") or 0),
            "synced_returns": list(pre_directive_return_sync.get("synced_returns") or []) + list(return_sync.get("synced_returns") or []),
        }
    )
    if usage["processed_directive_count"] >= max_directives:
        run["status"] = "limit_reached"
    run_path = _save_run(shell_root, run)
    operational_evidence = _record(return_sync.get("operational_evidence")) or _run_operational_evidence(shell_root, run)
    graph = _run_graph(shell_root, run, operational_evidence)
    policy_gate = _run_policy_gate(run, operational_evidence, graph)
    receipt_payload = {
        "schema_id": RUN_PICKUP_SCHEMA_ID,
        "ok": all(result.get("ok", True) for result in results),
        "created_at": now,
        "run_id": run_id,
        "run_path": run_path,
        "processed_directive_count": processed_now,
        "already_processed_count": already_now,
        "finding_count": findings_now,
        "return_sync_count": pre_directive_return_sync_count + int(return_sync.get("return_sync_count") or 0),
        "synced_returns": list(pre_directive_return_sync.get("synced_returns") or []) + list(return_sync.get("synced_returns") or []),
        "operational_evidence": operational_evidence,
        "graph": graph,
        "policy_gate": policy_gate,
        "results": results,
        **_no_authority(),
    }
    receipt_path = _receipt(shell_root, "run_pickup", receipt_payload)
    return {**receipt_payload, "receipt_path": receipt_path}


def _started_workpack_paths(run: Mapping[str, Any]) -> set[str]:
    started: set[str] = set()
    for event in list(run.get("events") or []):
        event_record = _record(event)
        if event_record.get("event") != "request_specific_worker_start":
            continue
        if event_record.get("worker_started") is not True:
            continue
        workpack_path = _text(event_record.get("workpack_path"))
        if workpack_path:
            started.add(workpack_path)
    return started


def _startable_workpack_paths(root: Path, run: Mapping[str, Any], *, include_started: bool = True) -> list[str]:
    started = _started_workpack_paths(run)
    paths: list[str] = []
    for workpack_path in [str(path) for path in list(run.get("workpack_paths") or []) if str(path)]:
        if not include_started and workpack_path in started:
            continue
        workpack = _read_repo_json(root, workpack_path)
        if not workpack:
            continue
        status = _text(workpack.get("status") or workpack.get("codex_work_request_status"))
        if _task_return_rows(root, workpack_path, workpack) or "RETURN" in status.upper():
            continue
        paths.append(workpack_path)
    return paths


def _run_completion_state(
    root: Path,
    run: Mapping[str, Any],
    evidence: Mapping[str, Any] | None = None,
    worker_runtime: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    evidence_record = _record(evidence) or _run_operational_evidence(root, run)
    work_items = [_record(item) for item in list(evidence_record.get("work_items") or [])]
    worker_record = _record(worker_runtime) or _run_worker_runtime(root, run, work_items)
    directive_state = _run_directive_state(root, run)
    followup_decision = _record(evidence_record.get("followup_decision")) or _run_followup_decision_state(work_items)
    startable_workpacks = _startable_workpack_paths(root, run, include_started=False)
    returned_count = sum(1 for item in work_items if _text(item.get("response_state")) == "returned" or _text(item.get("latest_return_packet_path")))
    workpack_count = len(work_items)
    has_started_without_return = any(_text(worker.get("status")) == "started_no_return" for worker in list(worker_record.get("workers") or []))
    if int(worker_record.get("active_worker_count") or 0) > 0:
        state = "worker_running"
    elif has_started_without_return:
        state = "awaiting_return"
    elif startable_workpacks:
        state = "ready_to_start_worker"
    elif int(directive_state.get("pending_directive_count") or 0) > 0:
        state = "pending_directive"
    elif workpack_count > 0 and returned_count == workpack_count:
        state = "complete"
    else:
        state = _text(evidence_record.get("operational_state"), "active")
    stored_status = _text(run.get("status"), "active")
    projected_status = "complete" if state == "complete" else ("active" if stored_status == "complete" else stored_status)
    return {
        "schema_id": "ion.agent_comms.run.completion_state.v1",
        "state": state,
        "is_complete": state == "complete",
        "is_active": state in {"worker_running", "awaiting_return", "ready_to_start_worker", "pending_directive", "workpack_active", "messages_delivered"},
        "stored_status": run.get("status"),
        "projected_status": projected_status,
        "workpack_count": workpack_count,
        "returned_workpack_count": returned_count,
        "startable_workpack_count": len(startable_workpacks),
        "startable_workpack_paths": startable_workpacks,
        "directive_state": directive_state,
        "followup_decision": followup_decision,
        "active_worker_count": worker_record.get("active_worker_count"),
        **_no_authority(),
    }


def _finalize_run_if_idle(
    root: Path,
    run: Mapping[str, Any],
    *,
    reason: str,
    evidence: Mapping[str, Any] | None = None,
    worker_runtime: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    updated = _sync_usage_observed_counts(run)
    completion = _run_completion_state(root, updated, evidence=evidence, worker_runtime=worker_runtime)
    if completion.get("is_complete") is True and _text(updated.get("status")) != "complete":
        now = _now()
        updated["status"] = "complete"
        updated["updated_at"] = now
        updated.setdefault("events", []).append(
            {
                "event": "run_completed",
                "created_at": now,
                "reason": reason,
                "workpack_count": completion.get("workpack_count"),
                "returned_workpack_count": completion.get("returned_workpack_count"),
                "pending_directive_count": _record(completion.get("directive_state")).get("pending_directive_count"),
            }
        )
    elif _text(updated.get("status")) == "complete" and completion.get("is_complete") is not True and completion.get("is_active") is True:
        now = _now()
        updated["status"] = "active"
        updated["updated_at"] = now
        updated.setdefault("events", []).append(
            {
                "event": "run_reopened",
                "created_at": now,
                "reason": reason,
                "completion_state": completion.get("state"),
            }
        )
    return updated


def start_agent_comms_run_worker(root: str | Path | None, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    shell_root = _root(root)
    data = dict(payload or {})
    run_id = _text(data.get("run_id"))
    if not run_id:
        return _blocked(RUN_WORKER_SCHEMA_ID, "run_id_required")
    run = _load_run(shell_root, run_id)
    if not run:
        return _blocked(RUN_WORKER_SCHEMA_ID, "run_not_found", run_id=run_id)
    workpack_paths = [str(path) for path in list(run.get("workpack_paths") or []) if str(path)]
    if not workpack_paths:
        return _blocked(RUN_WORKER_SCHEMA_ID, "run_has_no_workpacks", run_id=run_id)
    evidence = _run_operational_evidence(shell_root, run)
    graph = _run_graph(shell_root, run, evidence)
    policy_gate = _run_policy_gate(run, evidence, graph)
    if not policy_gate.get("ok"):
        return _blocked(
            RUN_WORKER_SCHEMA_ID,
            "run_policy_gate_blocked",
            run_id=run_id,
            policy_gate=policy_gate,
            graph=graph,
            operational_evidence=evidence,
            request_specific_worker_start=True,
        )
    requested_workpack_path = _text(data.get("workpack_path") or data.get("request_path"))
    if requested_workpack_path:
        if requested_workpack_path not in workpack_paths:
            return _blocked(
                RUN_WORKER_SCHEMA_ID,
                "workpack_not_in_run",
                run_id=run_id,
                workpack_path=requested_workpack_path,
                workpack_paths=workpack_paths,
                request_specific_worker_start=True,
            )
        workpack_path = requested_workpack_path
    else:
        startable = _startable_workpack_paths(shell_root, run)
        workpack_path = startable[0] if startable else workpack_paths[0]
    workpack = _read_repo_json(shell_root, workpack_path)
    if not workpack:
        return _blocked(
            RUN_WORKER_SCHEMA_ID,
            "workpack_json_missing",
            run_id=run_id,
            workpack_path=workpack_path,
            request_specific_worker_start=True,
        )
    return_rows = _task_return_rows(shell_root, workpack_path, workpack)
    workpack_status = _text(workpack.get("status") or workpack.get("codex_work_request_status"))
    if return_rows or "RETURN" in workpack_status.upper():
        return_sync = sync_run_task_returns(shell_root, run)
        run = _record(return_sync.get("run"))
        now = _now()
        run.setdefault("events", []).append(
            {
                "event": "worker_start_skipped_return_observed",
                "created_at": now,
                "workpack_path": workpack_path,
                "workpack_status": workpack_status,
                "return_packet_paths": [str(item.get("path")) for item in return_rows if str(item.get("path"))],
                "return_sync_count": return_sync.get("return_sync_count"),
                "request_specific_worker_start": True,
            }
        )
        run["updated_at"] = now
        run_path = _save_run(shell_root, run)
        operational_evidence = _record(return_sync.get("operational_evidence")) or _run_operational_evidence(shell_root, run)
        graph = _run_graph(shell_root, run, operational_evidence)
        policy_gate = _run_policy_gate(run, operational_evidence, graph)
        receipt_payload = {
            "schema_id": RUN_WORKER_SCHEMA_ID,
            "ok": True,
            "created_at": now,
            "run_id": run_id,
            "run_path": run_path,
            "finding": "workpack_already_returned",
            "worker_started": False,
            "request_specific_worker_start": True,
            "workpack_path": workpack_path,
            "workpack_status": workpack_status,
            "return_packet_paths": [str(item.get("path")) for item in return_rows if str(item.get("path"))],
            "return_sync_count": return_sync.get("return_sync_count"),
            "synced_returns": return_sync.get("synced_returns"),
            "operational_evidence": operational_evidence,
            "graph": graph,
            "policy_gate": policy_gate,
            **_no_authority(),
        }
        receipt_path = _receipt(shell_root, "run_worker_start", receipt_payload)
        return {**receipt_payload, "receipt_path": receipt_path}
    timeout_seconds = _int_limit(data.get("timeout_seconds"), 1800, 30, 86400)
    queue_result = process_codex_queue_once(
        shell_root,
        request_path=workpack_path,
        start=True,
        background=True,
        timeout_seconds=timeout_seconds,
    )
    now = _now()
    queue_run = _record(queue_result.get("run"))
    worker_started = bool(queue_result.get("ok")) and _text(queue_result.get("result")) == "CODEX_QUEUE_RUNNER_WORKER_STARTED"
    usage = _record(run.get("usage"))
    usage["worker_start_attempt_count"] = int(usage.get("worker_start_attempt_count") or 0) + 1
    if worker_started:
        usage["worker_start_count"] = int(usage.get("worker_start_count") or 0) + 1
    run["usage"] = usage
    run["updated_at"] = now
    run.setdefault("events", []).append(
        {
            "event": "request_specific_worker_start",
            "created_at": now,
            "workpack_path": workpack_path,
            "request_path": _text(queue_run.get("request_path"), workpack_path),
            "worker_started": worker_started,
            "queue_runner_result": queue_result.get("result"),
            "finding": queue_result.get("finding"),
            "run_packet_path": queue_run.get("run_packet_path"),
            "pid": queue_run.get("pid"),
            "timeout_seconds": timeout_seconds,
            "request_specific_worker_start": True,
        }
    )
    return_sync = sync_run_task_returns(shell_root, run)
    run = _record(return_sync.get("run"))
    run_path = _save_run(shell_root, run)
    operational_evidence = _record(return_sync.get("operational_evidence")) or _run_operational_evidence(shell_root, run)
    graph = _run_graph(shell_root, run, operational_evidence)
    policy_gate = _run_policy_gate(run, operational_evidence, graph)
    receipt_payload = {
        "schema_id": RUN_WORKER_SCHEMA_ID,
        "ok": bool(queue_result.get("ok")),
        "created_at": now,
        "run_id": run_id,
        "run_path": run_path,
        "finding": queue_result.get("finding") or queue_result.get("result"),
        "worker_started": worker_started,
        "request_specific_worker_start": True,
        "workpack_path": workpack_path,
        "request_path": _text(queue_run.get("request_path"), workpack_path),
        "run_packet_path": queue_run.get("run_packet_path"),
        "pid": queue_run.get("pid"),
        "timeout_seconds": timeout_seconds,
        "queue_runner_result": queue_result,
        "return_sync_count": return_sync.get("return_sync_count"),
        "synced_returns": return_sync.get("synced_returns"),
        "operational_evidence": operational_evidence,
        "graph": graph,
        "policy_gate": policy_gate,
        **_no_authority(),
    }
    receipt_path = _receipt(shell_root, "run_worker_start", receipt_payload)
    return {**receipt_payload, "receipt_path": receipt_path}


def continue_agent_comms_run(root: str | Path | None, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    shell_root = _root(root)
    data = dict(payload or {})
    run_id = _text(data.get("run_id"))
    if not run_id:
        return _blocked(RUN_CONTINUE_SCHEMA_ID, "run_id_required")
    pickup_result = pickup_agent_comms_run(
        shell_root,
        {
            "run_id": run_id,
            "max_directives": data.get("max_directives"),
        },
    )
    run = _load_run(shell_root, run_id)
    if not run:
        return _blocked(RUN_CONTINUE_SCHEMA_ID, "run_not_found", run_id=run_id, pickup_result=pickup_result)
    max_worker_starts = _int_limit(data.get("max_worker_starts"), 1, 0, 10)
    start_workers = data.get("start_workers") is not False
    worker_results: list[dict[str, Any]] = []
    if start_workers and max_worker_starts > 0:
        for workpack_path in _startable_workpack_paths(shell_root, run, include_started=False)[:max_worker_starts]:
            worker_result = start_agent_comms_run_worker(
                shell_root,
                {
                    "run_id": run_id,
                    "workpack_path": workpack_path,
                    "timeout_seconds": data.get("timeout_seconds") or 1800,
                },
            )
            worker_results.append(worker_result)
            run = _load_run(shell_root, run_id) or run
    evidence = _run_operational_evidence(shell_root, run)
    graph = _run_graph(shell_root, run, evidence)
    policy_gate = _run_policy_gate(run, evidence, graph)
    now = _now()
    receipt_payload = {
        "schema_id": RUN_CONTINUE_SCHEMA_ID,
        "ok": bool(pickup_result.get("ok", True)) and all(result.get("ok", True) for result in worker_results),
        "created_at": now,
        "run_id": run_id,
        "run_path": _rel(_run_path(shell_root, run_id), shell_root),
        "pickup_result": pickup_result,
        "processed_directive_count": int(pickup_result.get("processed_directive_count") or 0),
        "return_sync_count": int(pickup_result.get("return_sync_count") or 0),
        "worker_start_count": sum(1 for result in worker_results if result.get("worker_started") is True),
        "worker_results": worker_results,
        "startable_workpack_paths": _startable_workpack_paths(shell_root, run, include_started=False),
        "operational_evidence": evidence,
        "graph": graph,
        "policy_gate": policy_gate,
        "policy": "Continue syncs real returns, processes explicit agent-authored directives, and starts only run-attached unreturned workpacks under limits.",
        **_no_authority(),
    }
    receipt_path = _receipt(shell_root, "run_continue", receipt_payload)
    return {**receipt_payload, "receipt_path": receipt_path}


def build_agent_comms_runs_projection(root: str | Path | None = None, limit: int = 20) -> dict[str, Any]:
    shell_root = _root(root)
    index = _load_index(shell_root)
    rows = []
    for row in list(_record(index.get("runs")).values()):
        run_path = _text(_record(row).get("run_path"))
        run = _read_json(shell_root / run_path) if run_path else {}
        if run:
            rows.append(run)
    rows.sort(key=lambda item: str(item.get("updated_at") or item.get("created_at") or ""), reverse=True)
    row_limit = max(1, min(int(limit or 20), 100))
    projected_runs: list[dict[str, Any]] = []
    for row in rows[:row_limit]:
        evidence = _run_operational_evidence(shell_root, row)
        worker_runtime = _run_worker_runtime(shell_root, row, [_record(item) for item in list(evidence.get("work_items") or [])])
        completion_state = _run_completion_state(shell_root, row, evidence=evidence, worker_runtime=worker_runtime)
        graph = _run_graph(shell_root, row, evidence)
        policy_gate = _run_policy_gate(row, evidence, graph)
        projected_status = _text(completion_state.get("projected_status") or row.get("status"), "active")
        run_path = _rel(_run_path(shell_root, _text(row.get("run_id"), "run")), shell_root)
        audit_gate = audit_gate_for_run(shell_root, _text(row.get("run_id")), run_path=run_path)
        if completion_state.get("is_complete") is True:
            clean_state = "clean" if audit_gate.get("clean") is True else _text(audit_gate.get("state"), "audit_required")
        else:
            clean_state = "not_complete"
        projected_runs.append(
            {
                "run_id": row.get("run_id"),
                "run_path": run_path,
                "status": projected_status,
                "stored_status": row.get("status"),
                "completion_state": completion_state,
                "is_clean": clean_state == "clean",
                "clean_state": clean_state,
                "audit_gate": audit_gate,
                "objective": row.get("objective"),
                "dispatch_mode": row.get("dispatch_mode"),
                "target_roles": list(row.get("target_roles") or []),
                "thread_ids": list(row.get("thread_ids") or []),
                "root_message_ids": list(row.get("root_message_ids") or []),
                "workpack_paths": list(row.get("workpack_paths") or []),
                "return_message_ids": _record(row.get("return_message_ids")),
                "return_message_paths": _record(row.get("return_message_paths")),
                "limits": dict(row.get("limits") or {}),
                "usage": dict(row.get("usage") or {}),
                "created_at": row.get("created_at"),
                "updated_at": row.get("updated_at"),
                "events": list(row.get("events") or [])[-8:],
                "worker_runtime": worker_runtime,
                "active_worker_count": worker_runtime.get("active_worker_count"),
                "latest_worker": worker_runtime.get("latest_worker"),
                "graph": graph,
                "policy_gate": policy_gate,
                **evidence,
            }
        )
    return {
        "schema_id": RUN_PROJECTION_SCHEMA_ID,
        "generated_at": _now(),
        "run_count": len(rows),
        "active_run_count": sum(1 for row in projected_runs if row.get("status") == "active"),
        "complete_run_count": sum(1 for row in projected_runs if row.get("status") == "complete"),
        "clean_run_count": sum(1 for row in projected_runs if row.get("is_clean") is True),
        "audit_missing_count": sum(1 for row in projected_runs if _record(row.get("audit_gate")).get("state") == "audit_missing"),
        "audit_stale_count": sum(1 for row in projected_runs if _record(row.get("audit_gate")).get("state") == "audit_stale"),
        "audit_failed_count": sum(1 for row in projected_runs if _record(row.get("audit_gate")).get("state") == "audit_failed"),
        "audit_required_count": sum(1 for row in projected_runs if row.get("status") == "complete" and row.get("is_clean") is not True),
        "limit_reached_count": sum(1 for row in rows if row.get("status") in {"limit_reached", "blocked_by_limit"}),
        "response_observed_count": sum(1 for row in projected_runs if row.get("operational_state") == "response_observed"),
        "policy_blocked_count": sum(1 for row in projected_runs if _record(row.get("policy_gate")).get("state") == "blocked_by_policy"),
        "task_return_count": sum(int(row.get("task_return_count") or 0) for row in projected_runs),
        "agent_response_count": sum(int(row.get("agent_response_count") or 0) for row in projected_runs),
        "active_worker_count": sum(int(row.get("active_worker_count") or 0) for row in projected_runs),
        "runs": projected_runs,
        "policy": "Runs are bounded wrappers over real durable comms and explicit directive pickup. Complete means returned; clean requires a fresh PASS audit receipt over unchanged evidence.",
        **_no_authority(),
    }
