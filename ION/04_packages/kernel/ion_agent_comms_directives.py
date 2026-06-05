"""Agent-authored comms directive pickup.

Agents do not need a separate decider to communicate. They write an explicit
directive block in chat/comms output; automation services pick up that block and
route it through the existing comms/spawn-template/broker path.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_agent_comms import AGENT_COMMS_ROOT, normalize_role_id
from .ion_agent_spawn_templates import execute_agent_spawn_template

DIRECTIVE_SCHEMA_ID = "ion.agent_comms.directive.v1"
DIRECTIVE_PICKUP_SCHEMA_ID = "ion.agent_comms.directive_pickup.v1"
DIRECTIVE_PICKUP_PROJECTION_SCHEMA_ID = "ion.agent_comms.directive_pickup.projection.v1"
DIRECTIVE_RESULT_SCHEMA_ID = "ion.agent_comms.directive_pickup.result.v1"

DIRECTIVE_LEDGER_PATH = AGENT_COMMS_ROOT / "automation" / "DIRECTIVE_LEDGER.json"
DIRECTIVE_RECEIPTS_DIR = AGENT_COMMS_ROOT / "automation" / "directive_receipts"
MESSAGE_INDEX_PATH = AGENT_COMMS_ROOT / "projections" / "MESSAGE_INDEX.json"

DIRECTIVE_LANGS = {
    "ion-agent-comms",
    "ion_agent_comms",
    "ion-agent-workpack",
    "ion_agent_workpack",
}

ALLOWED_DISPATCH_MODES = {"comms_only", "prepare_workpack", "queue_workpack", "start_workpack"}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _resolve_root(root: str | Path | None = None) -> Path:
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


def _text(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text or fallback


def _list(value: Any) -> list[str]:
    if isinstance(value, list | tuple):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.replace(",", "\n").splitlines() if item.strip()]
    return []


def _record(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _hash_id(*parts: str) -> str:
    digest = hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"agent_comms_directive_{digest}"


def _stable_json(value: Mapping[str, Any]) -> str:
    return json.dumps(dict(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


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


def _parse_json_block(lang: str, block: str) -> dict[str, Any] | None:
    if lang not in DIRECTIVE_LANGS and lang != "json":
        return None
    try:
        payload = json.loads(block)
    except json.JSONDecodeError:
        return {"schema_id": DIRECTIVE_SCHEMA_ID, "ok": False, "finding": "directive_json_invalid", "raw": block[:500]}
    if not isinstance(payload, dict):
        return {"schema_id": DIRECTIVE_SCHEMA_ID, "ok": False, "finding": "directive_not_object"}
    schema_id = str(payload.get("schema_id") or "")
    marker = str(payload.get("directive_kind") or payload.get("kind") or "")
    if lang in DIRECTIVE_LANGS or schema_id == DIRECTIVE_SCHEMA_ID or marker in {"agent_comms", "agent_workpack", "ion_agent_comms"}:
        return dict(payload)
    return None


def extract_agent_comms_directives(
    text: str,
    *,
    source_ref: str = "",
    source_message_id: str = "",
    from_role: str = "",
    scope_id: str = "",
) -> dict[str, Any]:
    directives: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for index, (lang, block) in enumerate(_fenced_blocks(text), start=1):
        parsed = _parse_json_block(lang, block)
        if parsed is None:
            continue
        if parsed.get("ok") is False:
            findings.append(parsed)
            continue
        directive = _normalize_directive(
            parsed,
            source_ref=source_ref,
            source_message_id=source_message_id,
            from_role=from_role,
            scope_id=scope_id,
            block=block,
            index=index,
        )
        if directive.get("ok") is False:
            findings.append(directive)
        else:
            directives.append(directive)
    return {
        "schema_id": "ion.agent_comms.directive_extract.v1",
        "ok": not findings,
        "directive_count": len(directives),
        "directives": directives,
        "findings": findings,
        "source_ref": source_ref,
        "source_message_id": source_message_id,
        "scope_id": scope_id,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def _normalize_directive(
    payload: Mapping[str, Any],
    *,
    source_ref: str,
    source_message_id: str,
    from_role: str,
    scope_id: str,
    block: str,
    index: int,
) -> dict[str, Any]:
    target = _text(payload.get("agent") or payload.get("to_role") or payload.get("target_role") or payload.get("role_id"))
    objective = _text(payload.get("objective"))
    body = _text(payload.get("body") or payload.get("message") or objective)
    if not target:
        return {"schema_id": DIRECTIVE_SCHEMA_ID, "ok": False, "finding": "agent_required", "source_ref": source_ref}
    if not objective:
        return {"schema_id": DIRECTIVE_SCHEMA_ID, "ok": False, "finding": "objective_required", "source_ref": source_ref}
    dispatch_mode = _text(payload.get("dispatch_mode"), "queue_workpack")
    if payload.get("start") is True and dispatch_mode == "queue_workpack":
        dispatch_mode = "start_workpack"
    if dispatch_mode not in ALLOWED_DISPATCH_MODES:
        return {
            "schema_id": DIRECTIVE_SCHEMA_ID,
            "ok": False,
            "finding": "unsupported_dispatch_mode",
            "dispatch_mode": dispatch_mode,
            "source_ref": source_ref,
        }
    source_refs = _list(payload.get("source_refs") or payload.get("context_refs"))
    if source_ref and source_ref not in source_refs:
        source_refs.insert(0, source_ref)
    from_role_id = normalize_role_id(payload.get("from_role") or from_role or "operator")
    target_role_id = normalize_role_id(target)
    template_id = _text(payload.get("template_id"), "agent_workpack_decision")
    legacy_directive_id = _hash_id(source_message_id, source_ref, str(index), block)
    explicit_directive_id = _text(payload.get("directive_id"))
    identity_payload = {
        "scope_id": _text(scope_id),
        "from_role": from_role_id,
        "agent": target_role_id,
        "template_id": template_id,
        "dispatch_mode": dispatch_mode,
        "domain_id": _text(payload.get("domain_id")),
        "room_id": _text(payload.get("room_id")),
        "room_kind": _text(payload.get("room_kind") or payload.get("room_type")),
        "report_to_room_id": _text(payload.get("report_to_room_id") or payload.get("report_room_id")),
        "objective": objective,
        "body": body,
        "subject": _text(payload.get("subject")),
        "message_kind": _text(payload.get("message_kind")),
        "planned_writes": _list(payload.get("planned_writes")),
        "planned_artifacts": _list(payload.get("planned_artifacts")),
        "work_class": _text(payload.get("work_class")),
        "risk_level": _text(payload.get("risk_level")),
        "route_family": _text(payload.get("route_family")),
    }
    directive_id = explicit_directive_id or _hash_id(_stable_json(identity_payload))
    return {
        "schema_id": DIRECTIVE_SCHEMA_ID,
        "ok": True,
        "directive_id": directive_id,
        "legacy_directive_id": legacy_directive_id,
        "idempotency_scope": _text(scope_id),
        "created_from": "agent_chat_code_block",
        "source_ref": source_ref,
        "source_message_id": source_message_id,
        "from_role": from_role_id,
        "agent": target_role_id,
        "template_id": template_id,
        "dispatch_mode": dispatch_mode,
        "domain_id": _text(payload.get("domain_id")),
        "objective": objective,
        "body": body,
        "subject": _text(payload.get("subject")),
        "message_kind": _text(payload.get("message_kind")),
        "channel_id": _text(payload.get("channel_id")),
        "room_id": _text(payload.get("room_id")),
        "room_kind": _text(payload.get("room_kind") or payload.get("room_type")),
        "report_to_room_id": _text(payload.get("report_to_room_id") or payload.get("report_room_id")),
        "visibility": _text(payload.get("visibility")),
        "summary_required": bool(payload.get("summary_required")) if payload.get("summary_required") is not None else None,
        "source_refs": source_refs,
        "artifact_refs": _list(payload.get("artifact_refs") or payload.get("evidence_refs")),
        "planned_writes": _list(payload.get("planned_writes")),
        "planned_artifacts": _list(payload.get("planned_artifacts")),
        "work_class": _text(payload.get("work_class")),
        "risk_level": _text(payload.get("risk_level")),
        "route_family": _text(payload.get("route_family")),
        "automation_id": _text(payload.get("automation_id"), f"agent_comms:{from_role_id}"),
        "automation_window_minutes": payload.get("automation_window_minutes"),
        "automation_prompt_limit": payload.get("automation_prompt_limit"),
        "automation_time_budget_minutes": payload.get("automation_time_budget_minutes"),
        "automation_prompt_char_limit": payload.get("automation_prompt_char_limit"),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def _load_ledger(root: Path) -> dict[str, Any]:
    ledger = _read_json(root / DIRECTIVE_LEDGER_PATH)
    if not ledger:
        return {
            "schema_id": "ion.agent_comms.directive_ledger.v1",
            "created_at": _now(),
            "updated_at": _now(),
            "processed": {},
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }
    ledger.setdefault("processed", {})
    return ledger


def _save_ledger(root: Path, ledger: Mapping[str, Any]) -> None:
    value = dict(ledger)
    value["updated_at"] = _now()
    _write_json(root / DIRECTIVE_LEDGER_PATH, value)


def _message_sources(root: Path, payload: Mapping[str, Any]) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    direct_text = _text(payload.get("text") or payload.get("body") or payload.get("message"))
    if direct_text:
        sources.append(
            {
                "text": direct_text,
                "source_ref": _text(payload.get("source_ref"), "inline_agent_chat_text"),
                "source_message_id": _text(payload.get("source_message_id")),
                "from_role": _text(payload.get("from_role")),
                "thread_id": _text(payload.get("thread_id")),
                "channel_id": _text(payload.get("channel_id")),
                "room_id": _text(payload.get("room_id")),
                "room_kind": _text(payload.get("room_kind") or payload.get("room_type")),
                "report_to_room_id": _text(payload.get("report_to_room_id") or payload.get("report_room_id")),
                "visibility": _text(payload.get("visibility")),
                "summary_required": payload.get("summary_required"),
            }
        )
    message_path = _text(payload.get("message_path"))
    if message_path:
        path = root / message_path
        message = _read_json(path)
        if message:
            sources.append(
                {
                    "text": _text(message.get("body")),
                    "source_ref": message_path,
                    "source_message_id": _text(message.get("message_id")),
                    "from_role": _text(message.get("from_role")),
                    "thread_id": _text(message.get("thread_id")),
                    "channel_id": _text(message.get("channel_id")),
                    "room_id": _text(message.get("room_id")),
                    "room_kind": _text(message.get("room_kind")),
                    "report_to_room_id": _text(message.get("report_to_room_id")),
                    "visibility": _text(message.get("visibility")),
                    "summary_required": message.get("summary_required"),
                }
            )
    if direct_text or message_path:
        return sources
    limit = max(1, min(int(payload.get("limit") or 25), 200))
    index = _read_json(root / MESSAGE_INDEX_PATH)
    rows = list((index.get("messages") or {}).values()) if isinstance(index.get("messages"), Mapping) else []
    rows.sort(key=lambda row: str(row.get("created_at") or ""), reverse=True)
    for row in rows[:limit]:
        if not isinstance(row, Mapping):
            continue
        rel = _text(row.get("message_path"))
        message = _read_json(root / rel)
        if not message:
            continue
        sources.append(
            {
                "text": _text(message.get("body")),
                "source_ref": rel,
                "source_message_id": _text(message.get("message_id")),
                "from_role": _text(message.get("from_role")),
                "thread_id": _text(message.get("thread_id")),
                "channel_id": _text(message.get("channel_id")),
                "room_id": _text(message.get("room_id")),
                "room_kind": _text(message.get("room_kind")),
                "report_to_room_id": _text(message.get("report_to_room_id")),
                "visibility": _text(message.get("visibility")),
                "summary_required": message.get("summary_required"),
            }
        )
    return sources


def _append_text_once(base: str, addition: str) -> str:
    base_text = _text(base)
    addition_text = _text(addition)
    if not addition_text or addition_text in base_text:
        return base_text
    if not base_text:
        return addition_text
    return "\n\n".join([base_text, addition_text])


def _directive_to_spawn_payload(
    directive: Mapping[str, Any],
    *,
    followup_contract: str = "",
    run_id: str = "",
    run_objective: str = "",
) -> dict[str, Any]:
    body = _text(directive.get("body"))
    run_context = "\n".join(
        line
        for line in [
            f"Comms run: {run_id}" if _text(run_id) else "",
            f"Run objective: {run_objective}" if _text(run_objective) else "",
        ]
        if line
    )
    body = _append_text_once(body, run_context)
    body = _append_text_once(body, followup_contract)
    payload = {
        "template_id": directive.get("template_id"),
        "dispatch_mode": directive.get("dispatch_mode"),
        "dispatch_source": "automation",
        "automation_id": directive.get("automation_id"),
        "automation_window_minutes": directive.get("automation_window_minutes"),
        "automation_prompt_limit": directive.get("automation_prompt_limit"),
        "automation_time_budget_minutes": directive.get("automation_time_budget_minutes"),
        "automation_prompt_char_limit": directive.get("automation_prompt_char_limit"),
        "agent": directive.get("agent"),
        "from_role": directive.get("from_role"),
        "domain_id": directive.get("domain_id"),
        "objective": directive.get("objective"),
        "body": body,
        "subject": directive.get("subject"),
        "message_kind": directive.get("message_kind"),
        "channel_id": directive.get("channel_id"),
        "room_id": directive.get("room_id"),
        "room_kind": directive.get("room_kind"),
        "report_to_room_id": directive.get("report_to_room_id"),
        "visibility": directive.get("visibility"),
        "summary_required": directive.get("summary_required"),
        "thread_id": directive.get("thread_id"),
        "source_refs": directive.get("source_refs"),
        "artifact_refs": directive.get("artifact_refs"),
        "planned_writes": directive.get("planned_writes"),
        "planned_artifacts": directive.get("planned_artifacts"),
        "work_class": directive.get("work_class"),
        "risk_level": directive.get("risk_level"),
        "route_family": directive.get("route_family"),
        "idempotency_key": directive.get("directive_id"),
    }
    return {key: value for key, value in payload.items() if value not in (None, "", [])}


def process_agent_comms_directives(root: str | Path | None = None, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    data = dict(payload or {})
    max_directives = max(1, min(int(data.get("max_directives") or 10), 50))
    sources = _message_sources(shell_root, data)
    ledger = _load_ledger(shell_root)
    processed = dict(ledger.get("processed") or {})
    results: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for source in sources:
        idempotency_scope = _text(data.get("run_id") or source.get("thread_id"))
        extracted = extract_agent_comms_directives(
            source["text"],
            source_ref=source["source_ref"],
            source_message_id=source["source_message_id"],
            from_role=source["from_role"],
            scope_id=idempotency_scope,
        )
        findings.extend(list(extracted.get("findings") or []))
        for directive in list(extracted.get("directives") or []):
            if len(results) >= max_directives:
                break
            if source.get("thread_id") and not directive.get("thread_id"):
                directive["thread_id"] = source["thread_id"]
            if source.get("channel_id") and not directive.get("channel_id"):
                directive["channel_id"] = source["channel_id"]
            for key in ("room_id", "room_kind", "report_to_room_id", "visibility", "summary_required"):
                if source.get(key) not in (None, "") and directive.get(key) in (None, ""):
                    directive[key] = source.get(key)
            directive_id = str(directive.get("directive_id") or "")
            legacy_directive_id = _text(directive.get("legacy_directive_id"))
            processed_directive_id = directive_id if directive_id in processed else ""
            if not processed_directive_id and legacy_directive_id in processed:
                processed_directive_id = legacy_directive_id
            if processed_directive_id:
                results.append(
                    {
                        "directive_id": directive_id,
                        "processed_directive_id": processed_directive_id,
                        "legacy_directive_id": legacy_directive_id or None,
                        "status": "already_processed",
                        "ledger_record": processed[processed_directive_id],
                    }
                )
                continue
            for key in (
                "automation_id",
                "automation_window_minutes",
                "automation_prompt_limit",
                "automation_time_budget_minutes",
                "automation_prompt_char_limit",
            ):
                if data.get(key) not in (None, ""):
                    directive[key] = data.get(key)
            spawn_payload = _directive_to_spawn_payload(
                directive,
                followup_contract=_text(data.get("followup_contract")),
                run_id=_text(data.get("run_id")),
                run_objective=_text(data.get("run_objective")),
            )
            spawn_result = execute_agent_spawn_template(shell_root, spawn_payload)
            comms_result = _record(spawn_result.get("comms_result"))
            invocation_result = _record(spawn_result.get("invocation_result"))
            backend_start_result = _record(invocation_result.get("start_result"))
            spawned_comms_message_id = _text(spawn_result.get("spawned_comms_message_id") or comms_result.get("message_id"))
            spawned_comms_message_path = _text(comms_result.get("message_path"))
            spawned_thread_id = _text(comms_result.get("thread_id"))
            spawned_thread_path = _text(comms_result.get("thread_path"))
            workpack_path = _text(spawn_result.get("workpack_path") or invocation_result.get("codex_work_request_path"))
            target_agent = _text(spawn_result.get("target_agent") or directive.get("agent"))
            record = {
                "directive_id": directive_id,
                "legacy_directive_id": legacy_directive_id or None,
                "idempotency_scope": directive.get("idempotency_scope"),
                "processed_at": _now(),
                "source_ref": directive.get("source_ref"),
                "source_message_id": directive.get("source_message_id"),
                "from_role": directive.get("from_role"),
                "agent": directive.get("agent"),
                "target_agent": target_agent,
                "template_id": directive.get("template_id"),
                "dispatch_mode": directive.get("dispatch_mode"),
                "ok": bool(spawn_result.get("ok")),
                "finding": spawn_result.get("finding"),
                "spawn_status": spawn_result.get("spawn_status"),
                "comms_message_id": spawned_comms_message_id or None,
                "spawned_comms_message_id": spawned_comms_message_id or None,
                "comms_message_path": spawned_comms_message_path or None,
                "thread_id": spawned_thread_id or None,
                "thread_path": spawned_thread_path or None,
                "room_id": comms_result.get("room_id") or directive.get("room_id") or None,
                "room_kind": comms_result.get("room_kind") or directive.get("room_kind") or None,
                "report_to_room_id": comms_result.get("report_to_room_id") or directive.get("report_to_room_id") or None,
                "room_capsule_path": comms_result.get("room_capsule_path") or None,
                "workpack_path": workpack_path or None,
                "workpack_status": _text(spawn_result.get("workpack_status") or invocation_result.get("codex_work_request_status")) or None,
                "backend_start_proven": bool(backend_start_result.get("ok")),
                "live_external_agent_execution_proven": False,
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
            }
            processed[directive_id] = record
            results.append({"directive": directive, "spawn_payload": spawn_payload, "spawn_result": spawn_result, "ledger_record": record})
        if len(results) >= max_directives:
            break
    ledger["processed"] = processed
    _save_ledger(shell_root, ledger)
    receipt = {
        "schema_id": DIRECTIVE_RESULT_SCHEMA_ID,
        "ok": not findings
        and all((result.get("spawn_result") or {}).get("ok", True) for result in results if result.get("status") != "already_processed"),
        "created_at": _now(),
        "source_count": len(sources),
        "processed_directive_count": sum(1 for result in results if result.get("status") != "already_processed"),
        "already_processed_count": sum(1 for result in results if result.get("status") == "already_processed"),
        "finding_count": len(findings),
        "results": results,
        "findings": findings,
        "ledger_path": DIRECTIVE_LEDGER_PATH.as_posix(),
        "evidence_fields": [
            "source_message_id",
            "spawned_comms_message_id",
            "target_agent",
            "dispatch_mode",
            "room_id",
            "room_kind",
            "room_capsule_path",
            "workpack_path",
            "production_authority",
            "live_execution_authority",
            "accepted_state_authority",
        ],
        "live_external_agent_execution_proven": False,
        "policy": "Automation pickup only executes explicit agent-authored directive blocks. It does not decide when agents communicate.",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }
    receipt_path = shell_root / DIRECTIVE_RECEIPTS_DIR / f"{_stamp()}_directive_pickup.json"
    _write_json(receipt_path, receipt)
    receipt["receipt_path"] = _rel(receipt_path, shell_root)
    return receipt


def _recent_directive_receipts(root: Path, limit: int) -> list[dict[str, Any]]:
    receipt_dir = root / DIRECTIVE_RECEIPTS_DIR
    if not receipt_dir.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(receipt_dir.glob("*.json"), key=lambda item: item.name, reverse=True)[:limit]:
        payload = _read_json(path)
        rows.append(
            {
                "path": _rel(path, root),
                "schema_id": payload.get("schema_id"),
                "ok": bool(payload.get("ok")),
                "created_at": payload.get("created_at"),
                "source_count": payload.get("source_count", 0),
                "processed_directive_count": payload.get("processed_directive_count", 0),
                "already_processed_count": payload.get("already_processed_count", 0),
                "finding_count": payload.get("finding_count", 0),
                "live_external_agent_execution_proven": bool(payload.get("live_external_agent_execution_proven")),
                "policy": payload.get("policy"),
            }
        )
    return rows


def build_agent_comms_directive_pickup_projection(root: str | Path | None = None, limit: int = 20) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    row_limit = max(1, min(int(limit or 20), 100))
    ledger = _load_ledger(shell_root)
    processed = ledger.get("processed") if isinstance(ledger.get("processed"), Mapping) else {}
    processed_rows = [dict(row) for row in processed.values() if isinstance(row, Mapping)]
    processed_rows.sort(key=lambda row: str(row.get("processed_at") or ""), reverse=True)
    receipt_dir = shell_root / DIRECTIVE_RECEIPTS_DIR
    receipt_count = len(list(receipt_dir.glob("*.json"))) if receipt_dir.exists() else 0
    return {
        "schema_id": DIRECTIVE_PICKUP_PROJECTION_SCHEMA_ID,
        "generated_at": _now(),
        "action_id": "agent_comms.process_directives",
        "directive_schema_id": DIRECTIVE_SCHEMA_ID,
        "directive_fence": "ion-agent-comms",
        "directive_langs": sorted(DIRECTIVE_LANGS),
        "allowed_dispatch_modes": sorted(ALLOWED_DISPATCH_MODES),
        "evidence_fields": [
            "source_message_id",
            "spawned_comms_message_id",
            "target_agent",
            "dispatch_mode",
            "room_id",
            "room_kind",
            "room_capsule_path",
            "workpack_path",
            "production_authority",
            "live_execution_authority",
            "accepted_state_authority",
        ],
        "ledger_path": DIRECTIVE_LEDGER_PATH.as_posix(),
        "ledger_exists": (shell_root / DIRECTIVE_LEDGER_PATH).exists(),
        "receipt_dir": DIRECTIVE_RECEIPTS_DIR.as_posix(),
        "receipt_count": receipt_count,
        "processed_count": len(processed_rows),
        "recent_processed": processed_rows[:row_limit],
        "recent_receipts": _recent_directive_receipts(shell_root, row_limit),
        "live_external_agent_execution_proven": False,
        "policy": "Automation pickup only executes explicit agent-authored directive blocks. It does not decide when agents communicate.",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }
