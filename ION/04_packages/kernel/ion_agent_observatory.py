"""ION Agent Observatory / active agent visibility plane.

This module aggregates existing ION carrier/session/worker surfaces into a
single Branch Gateway projection. It is not a source of accepted state and does
not directly control Codex UI/TUI sessions.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

SCHEMA_ID = "ion.agent_observatory.v1_candidate"
CONFIRMATION_TOKEN = "ION_BOUNDED_WRITE_CONFIRMED"
CONTEXT_RELATIVE_ROOT = Path("ION/05_context/current/agent_observatory")
TARGET_DOMAIN_WEAVER_SESSION_ID = "019e8b2b-c770-71d3-b2d8-e4c1c14eba0b"
MAX_MESSAGE_CHARS = 1200
MAX_BYTES = 262_144
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:@-]{0,159}$")
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\-]{10,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{16,}"),
    re.compile(r"AIza[0-9A-Za-z_\-]{20,}"),
    re.compile(r"ya29\.[0-9A-Za-z_.\-]+"),
    re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(r"(?i)\b([A-Z0-9_]*(?:API[_-]?KEY|TOKEN|SECRET|PASSWORD|AUTHORIZATION)[A-Z0-9_]*)\s*[:=]\s*['\"]?[^ \n\r\t,'\"]+"),
]

AUTHORITY_FALSE = {
    "accepted_state_claim": False,
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "git_push_authority": False,
    "deletion_authority": False,
}
NON_CLAIMS = [
    "Agent Observatory is a visibility/proof router, not an accepted-state authority layer.",
    "Saved Codex transcripts are session evidence, not accepted state.",
    "Codex queue returns are carrier intake evidence until separately accepted with proof.",
    "Cockpit/UI observations are projection evidence only.",
    "No production, live external execution, secrets, git push, deletion, materialization, or accepted-state authority is granted.",
]
SOURCE_CLASSES = {
    "durable_ion_receipt",
    "ui_session_evidence",
    "saved_session_evidence",
    "carrier_intake_evidence",
    "cockpit_projection",
    "candidate_summary",
}
SOURCE_KEYS = {
    "codex_saved_sessions",
    "codex_live_sessions",
    "codex_queue",
    "domain_weaver",
    "gemini_sandbox",
    "multi_root_workspace",
    "cockpit",
    "resume_send",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _age_seconds(value: Any) -> int | None:
    parsed = _parse_time(value)
    if not parsed:
        return None
    return max(0, int((datetime.now(timezone.utc) - parsed).total_seconds()))


def _resolve_root(root: str | Path | None) -> Path:
    candidate = Path(root or ".").expanduser().resolve(strict=False)
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").is_file() and (path / "ION/REPO_AUTHORITY.md").is_file():
            return path
    return candidate


def _repo_rel(root: Path, path: Path | str | None) -> str | None:
    if path is None:
        return None
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        return candidate.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return candidate.as_posix()


def _safe_id(value: Any, *, field: str = "id", required: bool = True) -> str:
    text = str(value or "").strip()
    if not text:
        if required:
            raise ValueError(f"{field}_required")
        return ""
    if "/" in text or "\\" in text or ".." in text:
        raise ValueError(f"unsafe_{field}")
    if not SAFE_ID_RE.match(text):
        raise ValueError(f"unsafe_{field}")
    return text


def _safe_file_slug(value: Any, *, field: str = "id") -> str:
    text = _safe_id(value, field=field)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    slug = re.sub(r"[^A-Za-z0-9_.:-]+", "_", text).strip("._:-") or field
    if "/" in slug or "\\" in slug or ".." in slug:
        slug = field
    return f"{slug[:80]}_{digest}"


def _redact(value: Any, *, limit: int = MAX_MESSAGE_CHARS) -> str:
    text = str(value or "")
    for pattern in SECRET_PATTERNS:
        if pattern.pattern.startswith("(?i)\\b([A-Z0-9_"):
            text = pattern.sub(lambda match: f"{match.group(1)}=***REDACTED***", text)
        else:
            text = pattern.sub("***REDACTED***", text)
    if len(text) > limit:
        return text[:limit] + "...[truncated]"
    return text


def _sanitize(value: Any, *, limit: int = MAX_MESSAGE_CHARS) -> Any:
    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            key_text = _redact(key, limit=160)
            if any(marker in key_text.lower() for marker in ("token", "password", "authorization", "api_key", "apikey")) and not isinstance(item, (bool, int, float, type(None))):
                sanitized[key_text] = "***REDACTED***"
            elif "secret" in key_text.lower() and not isinstance(item, (bool, int, float, type(None))) and str(item).strip():
                sanitized[key_text] = "***REDACTED***"
            else:
                sanitized[key_text] = _sanitize(item, limit=limit)
        return sanitized
    if isinstance(value, list):
        return [_sanitize(item, limit=limit) for item in value[:80]]
    if isinstance(value, str):
        return _redact(value, limit=limit)
    if isinstance(value, (bool, int, float)) or value is None:
        return value
    return _redact(value, limit=limit)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return dict(value) if isinstance(value, Mapping) else {}


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_text_tail(path: Path, *, max_bytes: int = 64_000, line_count: int = 80) -> dict[str, Any]:
    if not path.is_file():
        return {"exists": False, "path": path.as_posix(), "records": [], "text": ""}
    max_bytes = max(1_000, min(int(max_bytes), MAX_BYTES))
    raw = path.read_bytes()[-max_bytes:]
    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()[-max(1, min(int(line_count), 500)) :]
    records = [{"line_no_from_tail": index + 1, "text": _redact(line, limit=4000)} for index, line in enumerate(lines)]
    return {
        "exists": True,
        "path": path.as_posix(),
        "size_bytes": path.stat().st_size,
        "returned_bytes_approx": len("\n".join(lines).encode("utf-8", errors="replace")),
        "records": records,
        "text": _redact("\n".join(lines), limit=max_bytes),
        "bounded": True,
    }


def _jsonl_tail(path: Path, *, line_count: int = 20) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    tail = _read_text_tail(path, max_bytes=128_000, line_count=line_count).get("records") or []
    rows: list[dict[str, Any]] = []
    for item in tail:
        text = str(item.get("text") or "")
        try:
            value = json.loads(text)
        except Exception:
            rows.append({"text": _redact(text, limit=1200)})
            continue
        rows.append(_sanitize(value, limit=1200) if isinstance(value, dict) else {"value": _sanitize(value, limit=1200)})
    return rows


def _recent_files(base: Path, patterns: Iterable[str] = ("*.json", "*.md", "*.jsonl", "*.txt"), *, limit: int = 20) -> list[Path]:
    if not base.is_dir():
        return []
    files: list[Path] = []
    for pattern in patterns:
        files.extend(path for path in base.glob(pattern) if path.is_file())
    unique = {path.resolve(strict=False): path for path in files}
    return sorted(unique.values(), key=lambda item: (item.stat().st_mtime, item.as_posix()), reverse=True)[: max(1, min(limit, 100))]


def _resolve_repo_path(root: Path, value: Any) -> Path:
    text = str(value or "").strip()
    if not text:
        raise ValueError("path_required")
    path = Path(text).expanduser()
    candidate = path.resolve(strict=False) if path.is_absolute() else (root / path).resolve(strict=False)
    try:
        candidate.relative_to(root.resolve(strict=False))
    except ValueError as exc:
        raise ValueError("path_outside_active_root") from exc
    lowered = candidate.as_posix().lower()
    if any(marker in lowered for marker in ("/.git/", "/.env", "secret", "token", "credentials", "auth.json")):
        raise ValueError("path_excluded_by_observatory_policy")
    return candidate


def _base(route_id: str, *, ok: bool = True, finding: str | None = None, refusal_class: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": ok,
        "schema_id": SCHEMA_ID,
        "route_id": route_id,
        "generated_at": _now(),
        "mutates_active_state": False,
        **AUTHORITY_FALSE,
        "authority": dict(AUTHORITY_FALSE),
        "non_claims": list(NON_CLAIMS),
    }
    if finding:
        payload["finding"] = finding
    if refusal_class:
        payload["refusal_class"] = refusal_class
    return payload


def _blocked(route_id: str, finding: str, *, refusal_class: str = "SCHEMA_INVALID", data: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = _base(route_id, ok=False, finding=finding, refusal_class=refusal_class)
    if data:
        payload.update(dict(data))
    return payload


def _require_gate(route_id: str, args: Mapping[str, Any]) -> dict[str, Any] | None:
    if not str(args.get("idempotency_key") or "").strip():
        return _blocked(route_id, "idempotency_key_required", refusal_class="IDEMPOTENCY_KEY_REQUIRED")
    if str(args.get("confirmation") or "") != CONFIRMATION_TOKEN:
        return _blocked(route_id, "confirmation_required", refusal_class="CONFIRMATION_REQUIRED", data={"required_confirmation": CONFIRMATION_TOKEN})
    return None


def _freshness(timestamp: Any, *, generated_at: str | None = None) -> dict[str, Any]:
    generated = generated_at or _now()
    age = _age_seconds(timestamp)
    stale = age is not None and age > 24 * 60 * 60
    return {
        "generated_at": generated,
        "age_seconds": age,
        "stale": bool(stale),
        "stale_reason": "older_than_24h" if stale else None,
    }


def _row(
    *,
    agent_ref: str,
    agent_kind: str,
    carrier: str,
    status: str = "unknown",
    role_id: str = "unknown_role",
    display_name: str | None = None,
    domain_id: str = "unknown_domain",
    objective: str = "",
    current_packet_id: str = "unknown_current_packet",
    current_packet_path: str | None = None,
    session_id: str | None = None,
    run_id: str | None = None,
    request_id: str | None = None,
    root_id: str | None = None,
    cwd: str | None = None,
    latest_timestamp: str | None = None,
    latest_message: str | None = None,
    latest_return_path: str | None = None,
    latest_receipt_path: str | None = None,
    evidence_paths: list[str] | None = None,
    blockers: list[str] | None = None,
    next_lawful_actions: list[str] | None = None,
    available_actions: list[dict[str, Any]] | None = None,
    source_of_truth_classification: str = "candidate_summary",
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    safe_ref = _safe_id(agent_ref.replace("/", ":"), field="agent_ref")
    source_class = source_of_truth_classification if source_of_truth_classification in SOURCE_CLASSES else "candidate_summary"
    return {
        "agent_ref": safe_ref,
        "agent_kind": agent_kind,
        "carrier": carrier,
        "status": status,
        "role_id": _redact(role_id, limit=240),
        "display_name": _redact(display_name or role_id or agent_ref, limit=240),
        "domain_id": _redact(domain_id, limit=240),
        "objective": _redact(objective, limit=2000),
        "current_packet_id": _redact(current_packet_id, limit=240),
        "current_packet_path": _redact(current_packet_path, limit=500) if current_packet_path else None,
        "session_id": _redact(session_id, limit=180) if session_id else None,
        "run_id": _redact(run_id, limit=180) if run_id else None,
        "request_id": _redact(request_id, limit=180) if request_id else None,
        "root_id": _redact(root_id, limit=180) if root_id else None,
        "cwd": _redact(cwd, limit=600) if cwd else None,
        "latest_timestamp": _redact(latest_timestamp, limit=100) if latest_timestamp else None,
        "latest_message": _redact(latest_message, limit=MAX_MESSAGE_CHARS) if latest_message else None,
        "latest_return_path": _redact(latest_return_path, limit=500) if latest_return_path else None,
        "latest_receipt_path": _redact(latest_receipt_path, limit=500) if latest_receipt_path else None,
        "evidence_paths": [_redact(item, limit=500) for item in (evidence_paths or []) if item],
        "blockers": [_redact(item, limit=800) for item in (blockers or []) if item],
        "next_lawful_actions": [_redact(item, limit=800) for item in (next_lawful_actions or []) if item],
        "available_actions": _sanitize(available_actions or [], limit=1200),
        "authority": dict(AUTHORITY_FALSE),
        **AUTHORITY_FALSE,
        "source_of_truth_classification": source_class,
        "freshness": _freshness(latest_timestamp),
        "metadata": _sanitize(metadata or {}, limit=1500),
    }


def _source_unavailable(source: str, finding: str, *, evidence_paths: list[str] | None = None) -> dict[str, Any]:
    return _row(
        agent_ref=f"source_unavailable:{source}",
        agent_kind="source_unavailable",
        carrier="unknown",
        status="unknown",
        role_id="source_unavailable",
        display_name=f"{source} unavailable",
        objective=finding,
        evidence_paths=evidence_paths or [],
        blockers=[finding],
        next_lawful_actions=["repair source route or inspect source-specific branch"],
        available_actions=[],
        source_of_truth_classification="candidate_summary",
        metadata={"source": source, "finding": finding},
    )


def _call_session_store(root: Path, route_id: str, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_codex_session_store_bridge import invoke_codex_session_store_route

    return invoke_codex_session_store_route(root, route_id=route_id, args=args)


def _call_live_bridge(root: Path, route_id: str, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_codex_live_session_bridge import invoke_codex_live_session_bridge_route

    return invoke_codex_live_session_bridge_route(root, route_id=route_id, args=args)


def _call_multi_root(root: Path, route_id: str, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_multi_root_workspace import invoke_multi_root_workspace_route

    return invoke_multi_root_workspace_route(root, route_id=route_id, args=args)


def _session_domain(summary: Mapping[str, Any]) -> str:
    text = json.dumps(summary, sort_keys=True).lower()
    if "domain weaver" in text or "domain_weaver" in text or "nemesis" in text or "exact-active" in text or "exact active" in text:
        return "domain.domain_weaver"
    return "unknown_domain"


def _latest_message_from_summary(summary: Mapping[str, Any]) -> str:
    latest = summary.get("latest_assistant_message") or summary.get("latest_user_message")
    if isinstance(latest, Mapping):
        return str(latest.get("text") or latest.get("payload_summary") or "")
    messages = summary.get("latest_messages") if isinstance(summary.get("latest_messages"), list) else []
    for item in reversed(messages):
        if isinstance(item, Mapping) and item.get("text"):
            return str(item.get("text"))
    return ""


def _codex_saved_session_actions(session_id: str) -> list[dict[str, Any]]:
    return [
        {"action_id": "read_summary", "branch_id": "codex_session_store", "route_id": "session_summary", "args": {"session_id": session_id, "message_count": 10}, "requires_confirmation": False},
        {"action_id": "read_transcript_slice", "branch_id": "codex_session_store", "route_id": "session_transcript_slice", "args": {"session_id": session_id, "line_count": 50, "max_bytes": 64000}, "requires_confirmation": False},
        {"action_id": "search_transcript", "branch_id": "codex_session_store", "route_id": "session_find", "args": {"session_id": session_id, "query": "<query>", "max_matches": 20}, "requires_confirmation": False},
        {"action_id": "resume_send_preview_read_only", "branch_id": "codex_session_store", "route_id": "session_resume_send_preview", "args": {"session_id": session_id, "prompt": "<bounded prompt>", "sandbox_mode": "read-only"}, "requires_confirmation": False},
        {"action_id": "resume_send_preview_workspace_write", "branch_id": "codex_session_store", "route_id": "session_resume_send_preview", "args": {"session_id": session_id, "prompt": "<bounded active-root patch prompt>", "sandbox_mode": "workspace-write"}, "requires_confirmation": False},
        {"action_id": "resume_send_read_only", "branch_id": "codex_session_store", "route_id": "session_resume_send", "args": {"session_id": session_id, "prompt": "<bounded prompt>", "sandbox_mode": "read-only", "idempotency_key": "<stable key>", "confirmation": CONFIRMATION_TOKEN}, "requires_confirmation": True},
        {"action_id": "resume_send_workspace_write", "branch_id": "codex_session_store", "route_id": "session_resume_send", "args": {"session_id": session_id, "prompt": "<bounded active-root patch prompt>", "sandbox_mode": "workspace-write", "idempotency_key": "<stable key>", "confirmation": CONFIRMATION_TOKEN}, "requires_confirmation": True},
        {"action_id": "harvest_to_ion", "branch_id": "codex_session_store", "route_id": "session_harvest_to_ion", "args": {"session_id": session_id, "idempotency_key": "<stable key>", "confirmation": CONFIRMATION_TOKEN}, "requires_confirmation": True},
    ]


def _collect_codex_saved_sessions(root: Path, *, limit: int, max_message_chars: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    try:
        listed = _call_session_store(root, "session_list", {"limit": max(5, min(limit, 50))})
    except Exception as exc:
        return [_source_unavailable("codex_saved_sessions", exc.__class__.__name__)], {"ok": False, "finding": exc.__class__.__name__}
    if not listed.get("ok"):
        return [_source_unavailable("codex_saved_sessions", str(listed.get("finding") or "session_list_failed"))], listed
    raw_sessions = [item for item in listed.get("sessions") or [] if isinstance(item, Mapping)]
    session_ids: list[str] = []
    for item in raw_sessions:
        session_id = str(item.get("session_id") or "").strip()
        if session_id and session_id not in session_ids:
            session_ids.append(session_id)
    if TARGET_DOMAIN_WEAVER_SESSION_ID not in session_ids:
        session_ids.insert(0, TARGET_DOMAIN_WEAVER_SESSION_ID)
    rows: list[dict[str, Any]] = []
    for session_id in session_ids[: max(1, min(limit, 50))]:
        try:
            summary = _call_session_store(root, "session_summary", {"session_id": session_id, "message_count": 8})
        except Exception as exc:
            rows.append(_source_unavailable("codex_saved_session", exc.__class__.__name__, evidence_paths=[session_id]))
            continue
        if not summary.get("found"):
            if session_id == TARGET_DOMAIN_WEAVER_SESSION_ID:
                rows.append(
                    _row(
                        agent_ref=f"codex_saved_session:{session_id}",
                        agent_kind="codex_saved_session",
                        carrier="codex_cli",
                        status="unknown",
                        role_id="lead_codex_domain_weaver_build_manager",
                        display_name="Lead Codex Domain Weaver Build Manager",
                        domain_id="domain.domain_weaver",
                        objective="Known target saved Codex session was not found by the session store bridge.",
                        session_id=session_id,
                        blockers=["session_not_found"],
                        available_actions=_codex_saved_session_actions(session_id),
                        source_of_truth_classification="saved_session_evidence",
                    )
                )
            continue
        latest_message = _latest_message_from_summary(summary)
        domain_id = _session_domain(summary)
        role_id = "lead_codex_domain_weaver_build_manager" if session_id == TARGET_DOMAIN_WEAVER_SESSION_ID or domain_id == "domain.domain_weaver" else "codex_cli_saved_session"
        display_name = "Lead Codex Domain Weaver Build Manager" if session_id == TARGET_DOMAIN_WEAVER_SESSION_ID else f"Codex saved session {session_id[:8]}"
        status = "active" if session_id == TARGET_DOMAIN_WEAVER_SESSION_ID else "unknown"
        evidence_paths = [str(summary.get("storage_path") or "")]
        resume_status = _call_session_store(root, "session_resume_status", {"session_id": session_id})
        latest_resume = resume_status.get("latest_run") if isinstance(resume_status.get("latest_run"), Mapping) else None
        if latest_resume and latest_resume.get("receipt_path"):
            evidence_paths.append(str(latest_resume.get("receipt_path")))
        rows.append(
            _row(
                agent_ref=f"codex_saved_session:{session_id}",
                agent_kind="codex_saved_session",
                carrier="codex_cli",
                status=status,
                role_id=role_id,
                display_name=display_name,
                domain_id=domain_id,
                objective=str((summary.get("latest_user_message") or {}).get("text") if isinstance(summary.get("latest_user_message"), Mapping) else "Saved Codex CLI session"),
                session_id=session_id,
                cwd=str(summary.get("cwd") or "") or None,
                latest_timestamp=str(summary.get("latest_timestamp") or "") or None,
                latest_message=_redact(latest_message, limit=max_message_chars),
                evidence_paths=evidence_paths,
                latest_receipt_path=str(latest_resume.get("receipt_path")) if latest_resume and latest_resume.get("receipt_path") else None,
                next_lawful_actions=["read transcript slice", "inspect action affordances", "resume_send_preview only unless confirmation is supplied"],
                available_actions=_codex_saved_session_actions(session_id),
                source_of_truth_classification="saved_session_evidence",
                metadata={
                    "line_count": summary.get("line_count"),
                    "message_count": summary.get("message_count"),
                    "originator": summary.get("originator"),
                    "model_provider": summary.get("model_provider"),
                    "resume_preview_available": True,
                    "resume_send_route_available": True,
                    "latest_resume_run": latest_resume,
                },
            )
        )
    return rows, {"ok": True, "session_count": len(rows), "session_list": listed}


def _collect_live_sessions(root: Path, *, limit: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    index_path = root / "ION/05_context/current/chatgpt_connector/codex_live_sessions/INDEX.json"
    index = _read_json(index_path)
    sessions = index.get("sessions") if isinstance(index.get("sessions"), Mapping) else {}
    rows: list[dict[str, Any]] = []
    for session_id, record in list(dict(sessions).items())[: max(1, min(limit, 100))]:
        try:
            safe_session_id = _safe_id(session_id, field="session_id")
            status = _call_live_bridge(root, "session_status", {"session_id": safe_session_id})
        except Exception as exc:
            rows.append(_source_unavailable("codex_live_session", exc.__class__.__name__, evidence_paths=[str(index_path)]))
            continue
        session = status.get("session") if isinstance(status.get("session"), Mapping) else (record if isinstance(record, Mapping) else {})
        rows.append(
            _row(
                agent_ref=f"codex_live_session:{safe_session_id}",
                agent_kind="codex_live_session",
                carrier="codex_tui",
                status=str(session.get("status") or ("registered" if status.get("registered") else "unknown")),
                role_id=str(session.get("role_id") or record.get("role_id") if isinstance(record, Mapping) else "codex_live_session"),
                display_name=str(session.get("display_name") or record.get("display_name") if isinstance(record, Mapping) else f"Codex live session {safe_session_id[:8]}"),
                domain_id=str(session.get("domain_id") or record.get("domain_id") if isinstance(record, Mapping) else "unknown_domain"),
                objective=str(session.get("objective") or record.get("objective") if isinstance(record, Mapping) else ""),
                current_packet_id=str(session.get("current_packet_id") or record.get("current_packet_id") if isinstance(record, Mapping) else "unknown_current_packet"),
                current_packet_path=str(session.get("current_packet_path") or "") or None,
                session_id=safe_session_id,
                latest_timestamp=str(session.get("updated_at") or record.get("updated_at") if isinstance(record, Mapping) else "") or None,
                latest_message=f"inbox={status.get('inbox_count', 0)} outbox={status.get('outbox_count', 0)} receipts={status.get('receipt_count', 0)}",
                latest_receipt_path=str(status.get("latest_receipt_path") or "") or None,
                evidence_paths=[str(status.get("session_path") or ""), str(status.get("latest_status_path") or ""), str(status.get("latest_receipt_path") or "")],
                blockers=[] if status.get("durable_inbox_outbox_relay_proven") else ["durable relay not registered"],
                next_lawful_actions=["relay enqueue preview", "read inbox/outbox tail", "record external observation if operator sees UI state"],
                available_actions=[
                    {"action_id": "live_status", "branch_id": "codex_live_session_bridge", "route_id": "session_status", "args": {"session_id": safe_session_id}, "requires_confirmation": False},
                    {"action_id": "relay_enqueue_preview", "branch_id": "codex_live_session_bridge", "route_id": "relay_enqueue_preview", "args": {"session_id": safe_session_id, "message": "<bounded message>"}, "requires_confirmation": False},
                    {"action_id": "relay_enqueue", "branch_id": "codex_live_session_bridge", "route_id": "relay_enqueue", "args": {"session_id": safe_session_id, "idempotency_key": "<stable key>", "confirmation": CONFIRMATION_TOKEN}, "requires_confirmation": True},
                ],
                source_of_truth_classification="durable_ion_receipt",
                metadata={
                    "inbox_count": status.get("inbox_count"),
                    "outbox_count": status.get("outbox_count"),
                    "automatic_polling_proven": bool(status.get("automatic_polling_proven")),
                    "direct_live_codex_ui_control_proven": bool(status.get("direct_live_codex_ui_control_proven")),
                    "durable_inbox_outbox_relay_proven": bool(status.get("durable_inbox_outbox_relay_proven")),
                },
            )
        )
    if not rows:
        return [_source_unavailable("codex_live_sessions", "no_registered_live_sessions", evidence_paths=[_repo_rel(root, index_path) or str(index_path)])], {"ok": True, "registered_session_count": 0, "index_path": _repo_rel(root, index_path)}
    return rows, {"ok": True, "registered_session_count": len(rows), "index_path": _repo_rel(root, index_path), "index": _sanitize(index)}


def _latest_task_return(root: Path) -> dict[str, Any] | None:
    candidates: list[tuple[Path, dict[str, Any]]] = []
    for base in [root / "ION/05_context/current/chatgpt_connector/task_returns", root / "ION/05_context/current/chatgpt_connector/task_return_machine_receipts"]:
        for path in _recent_files(base, ("*.json",), limit=20):
            data = _read_json(path)
            candidates.append((path, data))
    if not candidates:
        return None
    path, data = sorted(candidates, key=lambda item: (item[0].stat().st_mtime, item[0].as_posix()), reverse=True)[0]
    return {"path": _repo_rel(root, path), "data": _sanitize(data, limit=2000), "mtime": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()}


def _collect_codex_queue(root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    try:
        from .ion_queue_governor import active_run_entries_from_state, build_queue_governor_projection
    except Exception as exc:
        return [_source_unavailable("codex_queue", exc.__class__.__name__)], {"ok": False, "finding": exc.__class__.__name__}
    projection = build_queue_governor_projection(root)
    runner_path = root / "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
    runner_state = _read_json(runner_path)
    active_runs = [dict(item) for item in active_run_entries_from_state(runner_state)]
    latest_return = _latest_task_return(root)
    summary = projection.get("summary") if isinstance(projection.get("summary"), Mapping) else {}
    status = "active" if active_runs else ("queued" if int(summary.get("waiting_request_count") or 0) else "waiting")
    rows = [
        _row(
            agent_ref="codex_queue:current",
            agent_kind="codex_queue_worker",
            carrier="codex_queue",
            status=status,
            role_id="codex_queue_worker_lane",
            display_name="Codex Queue Worker Lane",
            domain_id="domain.domain_weaver" if "domain_weaver" in json.dumps(projection).lower() else "unknown_domain",
            objective="Queue/worker lane currentness, active run, and latest return projection.",
            run_id=str(active_runs[0].get("run_id")) if active_runs and active_runs[0].get("run_id") else None,
            request_id=str(active_runs[0].get("request_id")) if active_runs and active_runs[0].get("request_id") else None,
            latest_timestamp=str(runner_state.get("updated_at") or runner_state.get("generated_at") or projection.get("generated_at") or "") or None,
            latest_message=f"active_runs={len(active_runs)} waiting={summary.get('waiting_request_count', 0)} stale={summary.get('stale_waiting_request_count', 0)} terminal_repair={summary.get('terminal_repair_request_count', 0)}",
            latest_return_path=str(latest_return.get("path")) if latest_return else None,
            latest_receipt_path=str(latest_return.get("path")) if latest_return else None,
            evidence_paths=[projection.get("queue_path"), projection.get("runner_state_path"), projection.get("work_lane_index_path"), latest_return.get("path") if latest_return else None],
            blockers=[finding.get("code") for finding in projection.get("findings") or [] if isinstance(finding, Mapping)],
            next_lawful_actions=[str((projection.get("next_packets") or [{}])[0].get("objective"))] if projection.get("next_packets") else ["observe queue status or read latest return"],
            available_actions=[
                {"action_id": "worker_shift_status", "branch_id": "worker_shift", "route_id": "status_summary", "args": {}, "requires_confirmation": False},
                {"action_id": "latest_tail", "branch_id": "agent_observatory", "route_id": "agent_observatory_latest_tail", "args": {"agent_ref": "codex_queue:current", "source": "latest_return", "line_count": 80}, "requires_confirmation": False},
            ],
            source_of_truth_classification="carrier_intake_evidence",
            metadata={"projection": projection, "active_runs": _sanitize(active_runs), "latest_return": latest_return},
        )
    ]
    for active in active_runs[:10]:
        run_id = str(active.get("run_id") or "unknown_run")
        rows.append(
            _row(
                agent_ref=f"codex_queue_run:{run_id}",
                agent_kind="codex_queue_worker",
                carrier="codex_queue",
                status="active",
                role_id=str(active.get("agent_role_id") or "codex_queue_worker"),
                display_name=str(active.get("agent_display_name") or f"Codex queue run {run_id[:10]}"),
                domain_id="domain.domain_weaver" if "domain_weaver" in json.dumps(active).lower() else "unknown_domain",
                objective=str(active.get("objective") or "Active Codex queue run"),
                run_id=run_id,
                request_id=str(active.get("request_id") or "") or None,
                latest_timestamp=str(active.get("started_at") or active.get("updated_at") or projection.get("generated_at") or "") or None,
                latest_message=str(active.get("latest_worker_lifecycle_event") or active.get("status") or "active run"),
                latest_return_path=str(active.get("latest_return_packet_path") or "") or None,
                evidence_paths=[_repo_rel(root, runner_path) or runner_path.as_posix(), str(active.get("latest_return_packet_path") or "")],
                next_lawful_actions=["read worker trace/status; do not claim accepted state from run output alone"],
                available_actions=[{"action_id": "worker_shift_status", "branch_id": "worker_shift", "route_id": "status_summary", "args": {}, "requires_confirmation": False}],
                source_of_truth_classification="carrier_intake_evidence",
                metadata=active,
            )
        )
    return rows, {"ok": True, "projection": projection, "active_run_count": len(active_runs), "latest_return": latest_return}


def _find_numeric_key(value: Any, keys: set[str]) -> int | None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key) in keys and isinstance(item, (int, float)):
                return int(item)
        for item in value.values():
            found = _find_numeric_key(item, keys)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value[:200]:
            found = _find_numeric_key(item, keys)
            if found is not None:
                return found
    return None


def _find_bool_key(value: Any, keys: set[str]) -> bool | None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key) in keys and isinstance(item, bool):
                return bool(item)
        for item in value.values():
            found = _find_bool_key(item, keys)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value[:200]:
            found = _find_bool_key(item, keys)
            if found is not None:
                return found
    return None


def _domain_weaver_card(root: Path) -> dict[str, Any]:
    dw_root = root / "ION/05_context/current/domain_weaver"
    status_path = root / "ION/05_context/current/codex_solo/STATUS.json"
    hot_path = root / "ION/05_context/current/codex_solo/HOT_CONTEXT.md"
    proof_path = dw_root / "live_carrier_binding/ACTIVE_INVOKABLE_BINDING_PROOF_ROWS.candidate.json"
    projection_path = dw_root / "DOMAIN_WEAVER_PROJECTION.json"
    proof = _read_json(proof_path)
    status = _read_json(status_path)
    projection = _read_json(projection_path)
    latest_artifacts = _recent_files(dw_root / "live_carrier_binding", ("*.json", "*.md"), limit=8) + _recent_files(dw_root / "monolith_decomposition", ("*.json", "*.md"), limit=8) + _recent_files(dw_root / "operator_actions", ("*.json",), limit=4)
    exact_count = _find_numeric_key(proof, {"exact_active_binding_count", "exact_active_count", "active_invocable_binding_count"})
    missing_count = _find_numeric_key(proof, {"missing_exact_active_binding_count", "missing_active_invocable_binding_count", "missing_binding_count"})
    if exact_count is None:
        exact_count = 0
    if missing_count is None:
        text = json.dumps(proof).lower()
        missing_count = text.count("missing_exact_active") + text.count("missing exact-active") + text.count("missing_exact_active_binding")
    materialization_ready = _find_bool_key(proof, {"materialization_ready", "materialization_allowed", "ready_for_materialization"})
    topology_allowed = _find_bool_key(proof, {"topology_materialization_allowed", "topology_allowed", "ui_materialization_allowed"})
    if materialization_ready is None:
        materialization_ready = False
    if topology_allowed is None:
        topology_allowed = False
    blocker_candidates: list[str] = []
    for source in [status, projection, proof]:
        text = json.dumps(source, sort_keys=True)
        for marker in ["blocker", "blocked", "missing_exact", "materialization"]:
            index = text.lower().find(marker)
            if index >= 0:
                blocker_candidates.append(_redact(text[max(0, index - 120) : index + 360], limit=520))
                break
    latest_next_packet = None
    for artifact in latest_artifacts:
        if "NEXT" in artifact.name.upper() or "PACKET" in artifact.name.upper() or "RESULT" in artifact.name.upper():
            latest_next_packet = _repo_rel(root, artifact)
            break
    latest_timestamp = None
    if latest_artifacts:
        latest_timestamp = datetime.fromtimestamp(latest_artifacts[0].stat().st_mtime, timezone.utc).isoformat()
    return {
        "schema_id": "ion.agent_observatory.domain_weaver_status.v1_candidate",
        "generated_at": _now(),
        "status": "candidate_observed",
        "exact_active_binding_count": exact_count,
        "missing_exact_active_binding_count": missing_count,
        "materialization_ready": bool(materialization_ready),
        "topology_materialization_allowed": bool(topology_allowed),
        "latest_next_packet": latest_next_packet,
        "latest_blocker": blocker_candidates[0] if blocker_candidates else "No blocker text extracted; inspect evidence paths.",
        "latest_operator_action": next((_repo_rel(root, path) for path in latest_artifacts if "operator_actions" in path.as_posix()), None),
        "latest_fan_in_settlement": next((_repo_rel(root, path) for path in latest_artifacts if "FANIN" in path.name.upper() or "SETTLEMENT" in path.name.upper()), None),
        "active_recent_worker_sessions": [TARGET_DOMAIN_WEAVER_SESSION_ID],
        "latest_codex_session_managing_domain_weaver": TARGET_DOMAIN_WEAVER_SESSION_ID,
        "latest_codex_queue_run": None,
        "latest_gemini_sandbox": None,
        "recommended_next_lawful_action": "Read current Domain Weaver evidence and route focused proof work; do not materialize UI/topology until exact-active evidence proves readiness.",
        "evidence_paths": [
            _repo_rel(root, status_path),
            _repo_rel(root, hot_path),
            _repo_rel(root, proof_path),
            _repo_rel(root, projection_path),
            *[_repo_rel(root, path) for path in latest_artifacts[:12]],
        ],
        "latest_timestamp": latest_timestamp,
        "authority": dict(AUTHORITY_FALSE),
        **AUTHORITY_FALSE,
        "source_of_truth_classification": "candidate_summary",
        "non_claims": list(NON_CLAIMS),
    }


def _collect_domain_weaver(root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    card = _domain_weaver_card(root)
    row = _row(
        agent_ref="domain_weaver:current",
        agent_kind="domain_weaver_worker",
        carrier="domain_weaver",
        status="blocked" if card.get("materialization_ready") is not True else "candidate",
        role_id="domain_weaver_stewardship_plane",
        display_name="Domain Weaver Current State",
        domain_id="domain.domain_weaver",
        objective="Living ION self-model, active binding proof, and materialization blocker projection.",
        current_packet_id=str(card.get("latest_next_packet") or "unknown_current_packet"),
        current_packet_path=str(card.get("latest_next_packet") or "") or None,
        session_id=TARGET_DOMAIN_WEAVER_SESSION_ID,
        latest_timestamp=str(card.get("latest_timestamp") or card.get("generated_at")),
        latest_message=str(card.get("latest_blocker") or "Domain Weaver status card generated"),
        evidence_paths=[str(item) for item in card.get("evidence_paths") or [] if item],
        blockers=[str(card.get("latest_blocker"))] if card.get("latest_blocker") else [],
        next_lawful_actions=[str(card.get("recommended_next_lawful_action"))],
        available_actions=[
            {"action_id": "domain_weaver_status", "branch_id": "agent_observatory", "route_id": "agent_observatory_domain_weaver_status", "args": {}, "requires_confirmation": False},
            {"action_id": "target_session_detail", "branch_id": "agent_observatory", "route_id": "agent_observatory_agent_detail", "args": {"session_id": TARGET_DOMAIN_WEAVER_SESSION_ID}, "requires_confirmation": False},
        ],
        source_of_truth_classification="candidate_summary",
        metadata=card,
    )
    return [row], {"ok": True, "card": card}


def _collect_gemini(root: Path, *, limit: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    base = root / "ION/05_context/current/gemini_ion_sandboxes"
    context_base = root / "ION/05_context/current/gemini_cli_carrier_context"
    artifacts = _recent_files(base, ("*.json", "*.md", "*.txt"), limit=limit)
    if base.is_dir():
        for child in sorted([item for item in base.iterdir() if item.is_dir()], key=lambda item: item.stat().st_mtime, reverse=True)[: max(1, min(limit, 20))]:
            artifacts.extend(_recent_files(child, ("*.json", "*.md", "*.txt", "*.patch"), limit=4))
    artifacts.extend(_recent_files(context_base, ("*.json", "*.md", "*.txt"), limit=limit))
    if not artifacts:
        return [_source_unavailable("gemini_sandbox", "no_gemini_sandbox_artifacts_found", evidence_paths=[_repo_rel(root, base) or str(base)])], {"ok": True, "artifact_count": 0}
    latest = sorted({path.resolve(strict=False): path for path in artifacts}.values(), key=lambda item: (item.stat().st_mtime, item.as_posix()), reverse=True)[0]
    row = _row(
        agent_ref="gemini_sandbox:latest",
        agent_kind="gemini_sandbox",
        carrier="gemini_cli",
        status="candidate",
        role_id="gemini_sandbox_worker",
        display_name="Latest Gemini ION Sandbox",
        domain_id="unknown_domain",
        objective="Disposable sandbox carrier artifacts for read/write/test/patch candidate work.",
        root_id="gemini_ion_sandbox_root",
        cwd=_repo_rel(root, latest.parent),
        latest_timestamp=datetime.fromtimestamp(latest.stat().st_mtime, timezone.utc).isoformat(),
        latest_message=f"latest sandbox artifact {latest.name}",
        latest_receipt_path=_repo_rel(root, latest),
        evidence_paths=[_repo_rel(root, path) for path in sorted({path.resolve(strict=False): path for path in artifacts}.values(), key=lambda item: (item.stat().st_mtime, item.as_posix()), reverse=True)[:12]],
        next_lawful_actions=["read latest sandbox result; write/test only inside registered sandbox root with confirmation if routed"],
        available_actions=[{"action_id": "sandbox_root_profile", "branch_id": "multi_root_workspace", "route_id": "root_file_profile", "args": {"root_id": "gemini_ion_sandbox_root", "path": "."}, "requires_confirmation": False}],
        source_of_truth_classification="carrier_intake_evidence",
        metadata={"read_write_test_patch_proven_in_sandbox_only": True, "active_root_mutation_proven": False},
    )
    return [row], {"ok": True, "artifact_count": len(artifacts), "latest_artifact": _repo_rel(root, latest)}


def _collect_multi_root(root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    try:
        registry = _call_multi_root(root, "root_registry", {"limit": 100})
    except Exception as exc:
        return [_source_unavailable("multi_root_workspace", exc.__class__.__name__)], {"ok": False, "finding": exc.__class__.__name__}
    if not registry.get("ok"):
        return [_source_unavailable("multi_root_workspace", str(registry.get("finding") or "root_registry_failed"))], registry
    roots = [item for item in registry.get("roots") or [] if isinstance(item, Mapping)]
    row = _row(
        agent_ref="multi_root_workspace:registry",
        agent_kind="multi_root_spawn_packet",
        carrier="domain_weaver",
        status="registered",
        role_id="multi_root_workspace_authority_layer",
        display_name="Multi-root Workspace Registry",
        objective=f"{len(roots)} registered root authority profiles available for bounded read/search/profile/spawn preview.",
        root_id=str(registry.get("default_root_id") or "active_ion_control"),
        latest_timestamp=str(registry.get("generated_at") or "") or None,
        latest_message=", ".join(str(item.get("root_id")) for item in roots[:8]),
        evidence_paths=[str(registry.get("registry_path") or "ION/03_registry/ion_workspace_root_registry.yaml")],
        next_lawful_actions=["use root_file_profile/root_search for approved roots", "use root_agent_spawn_preview before any spawn"],
        available_actions=[
            {"action_id": "root_registry", "branch_id": "multi_root_workspace", "route_id": "root_registry", "args": {"limit": 50}, "requires_confirmation": False},
            {"action_id": "spawn_preview", "branch_id": "multi_root_workspace", "route_id": "root_agent_spawn_preview", "args": {"root_id": "<root_id>", "cwd": ".", "objective": "<objective>", "agent_role": "<role>"}, "requires_confirmation": False},
        ],
        source_of_truth_classification="durable_ion_receipt",
        metadata={"root_count": len(roots), "roots": roots},
    )
    return [row], {"ok": True, "registry": registry}


def _runtime_status(root: Path) -> dict[str, Any]:
    if os.environ.get("ION_AGENT_OBSERVATORY_SKIP_SERVICE_STATUS"):
        return {"ok": False, "finding": "service_status_skipped_by_environment"}
    try:
        from .ion_runtime_service_control import service_status

        return service_status(root, {"probe_health": False})
    except Exception as exc:
        return {"ok": False, "finding": exc.__class__.__name__}


def _browser_queue_counts(root: Path) -> dict[str, Any]:
    candidates = [
        root / "ION/05_context/current/ACTIVE_BROWSER_QUEUE.json",
        root / "ION/05_context/current/browser_queue/ACTIVE_BROWSER_QUEUE.json",
        root / "ION/05_context/current/chatgpt_connector/browser_queue/ACTIVE_BROWSER_QUEUE.json",
    ]
    for path in candidates:
        data = _read_json(path)
        if data:
            rows = data.get("requests") or data.get("items") or data.get("queue") or []
            counts: dict[str, int] = {}
            if isinstance(rows, list):
                for item in rows:
                    if isinstance(item, Mapping):
                        status = str(item.get("status") or item.get("state") or "unknown")
                        counts[status] = counts.get(status, 0) + 1
            return {"available": True, "path": _repo_rel(root, path), "counts": counts, "raw_summary": _sanitize(data, limit=1000)}
    return {"available": False, "finding": "browser_queue_projection_not_found", "searched_paths": [_repo_rel(root, path) for path in candidates]}


def _cockpit_card(root: Path) -> dict[str, Any]:
    runtime = _runtime_status(root)
    browser_queue = _browser_queue_counts(root)
    dist_index = root / "ION/08_ui/joc_cockpit_shell/dist/index.html"
    source_paths = [
        root / "ION/08_ui/joc_cockpit_shell/AgentControlPlanePanel.tsx",
        root / "ION/08_ui/joc_cockpit_shell/CodexWorkbenchShell.tsx",
        root / "ION/04_packages/kernel/ion_chatgpt_browser_mcp_http_preview.py",
        dist_index,
    ]
    services = runtime.get("services") if isinstance(runtime.get("services"), list) else []
    service_rows = [item for item in services if isinstance(item, Mapping)]
    cockpit_services = [item for item in service_rows if str(item.get("service_id")) in {"mcp_preview", "cockpit_app", "action_gateway"}]
    status = "available" if cockpit_services or dist_index.is_file() else "unknown"
    return {
        "schema_id": "ion.agent_observatory.cockpit_status.v1_candidate",
        "generated_at": _now(),
        "status": status,
        "cockpit_service_status": _sanitize(cockpit_services, limit=1500),
        "cockpit_url": next((str(item.get("local_url")) for item in cockpit_services if item.get("local_url")), None) or "http://127.0.0.1:8765/cockpit",
        "supabase_availability": {"available": False, "finding": "not_probed_by_agent_observatory_read_route"},
        "browser_queue": browser_queue,
        "latest_captures_or_previews": [],
        "source_paths": [_repo_rel(root, path) for path in source_paths],
        "blockers": [] if status == "available" else ["cockpit service/status not proven by runtime route"],
        "authority": dict(AUTHORITY_FALSE),
        **AUTHORITY_FALSE,
        "source_of_truth_classification": "cockpit_projection",
        "non_claims": list(NON_CLAIMS),
    }


def _collect_cockpit(root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    card = _cockpit_card(root)
    row = _row(
        agent_ref="cockpit:helixion",
        agent_kind="cockpit_surface",
        carrier="cockpit",
        status=str(card.get("status") or "unknown"),
        role_id="helixion_cockpit_projection",
        display_name="Helixion Cockpit Visibility Surface",
        objective="Local cockpit/browser/Supabase visibility posture for agent observation.",
        latest_timestamp=str(card.get("generated_at")),
        latest_message=f"cockpit_url={card.get('cockpit_url')} supabase_available={card.get('supabase_availability', {}).get('available')}",
        evidence_paths=[str(item) for item in card.get("source_paths") or [] if item],
        blockers=[str(item) for item in card.get("blockers") or []],
        next_lawful_actions=["Use cockpit UI as projection evidence; call agent_observatory routes for structured Browser GPT visibility."],
        available_actions=[{"action_id": "cockpit_status", "branch_id": "agent_observatory", "route_id": "agent_observatory_cockpit_status", "args": {}, "requires_confirmation": False}],
        source_of_truth_classification="cockpit_projection",
        metadata=card,
    )
    return [row], {"ok": True, "card": card}


def _overview_rows(root: Path, args: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    limit = max(1, min(int(args.get("limit") or 40), 200))
    max_message_chars = max(100, min(int(args.get("max_message_chars") or MAX_MESSAGE_CHARS), 4000))
    requested_sources = args.get("include_sources")
    if isinstance(requested_sources, list) and requested_sources:
        sources = {str(item) for item in requested_sources if str(item) in SOURCE_KEYS}
    else:
        sources = set(SOURCE_KEYS)
    source_status: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []
    collectors = [
        ("codex_saved_sessions", lambda: _collect_codex_saved_sessions(root, limit=limit, max_message_chars=max_message_chars)),
        ("codex_live_sessions", lambda: _collect_live_sessions(root, limit=limit)),
        ("codex_queue", lambda: _collect_codex_queue(root)),
        ("domain_weaver", lambda: _collect_domain_weaver(root)),
        ("gemini_sandbox", lambda: _collect_gemini(root, limit=limit)),
        ("multi_root_workspace", lambda: _collect_multi_root(root)),
        ("cockpit", lambda: _collect_cockpit(root)),
    ]
    for source, collector in collectors:
        if source not in sources:
            continue
        try:
            collected, status = collector()
        except Exception as exc:
            collected, status = [_source_unavailable(source, exc.__class__.__name__)], {"ok": False, "finding": exc.__class__.__name__}
        rows.extend(collected)
        source_status[source] = status
    focus_domain = str(args.get("focus_domain") or "").strip()
    include_completed = bool(args.get("include_completed"))
    if focus_domain:
        rows = [row for row in rows if focus_domain in str(row.get("domain_id") or "") or focus_domain in json.dumps(row.get("metadata") or {}).lower()]
    if not include_completed:
        rows = [row for row in rows if str(row.get("status") or "").lower() != "completed"]
    sorted_rows = sorted(rows, key=lambda row: (_parse_time(row.get("latest_timestamp")) or datetime.min.replace(tzinfo=timezone.utc), row.get("agent_ref") or ""), reverse=True)
    pinned_refs: set[str] = set()
    pinned_rows: list[dict[str, Any]] = []
    for row in sorted_rows:
        if row.get("session_id") == TARGET_DOMAIN_WEAVER_SESSION_ID and row.get("agent_kind") in {"codex_saved_session", "codex_live_session", "domain_weaver_worker"}:
            ref = str(row.get("agent_ref") or "")
            if ref not in pinned_refs:
                pinned_rows.append(row)
                pinned_refs.add(ref)
    rows = [*pinned_rows, *[row for row in sorted_rows if str(row.get("agent_ref") or "") not in pinned_refs]][:limit]
    return rows, source_status


def _overview(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    rows, source_status = _overview_rows(root, args)
    payload = _base("agent_observatory_overview")
    payload.update(
        {
            "agent_count": len(rows),
            "agents": rows,
            "source_status": _sanitize(source_status, limit=2200),
            "normalization_contract": "All rows carry authority false flags and source-of-truth classification; output is candidate projection evidence only.",
        }
    )
    return payload


def _find_row(root: Path, args: Mapping[str, Any]) -> dict[str, Any] | None:
    agent_ref = _safe_id(args.get("agent_ref"), field="agent_ref", required=False)
    session_id = _safe_id(args.get("session_id"), field="session_id", required=False)
    run_id = _safe_id(args.get("run_id"), field="run_id", required=False)
    request_id = _safe_id(args.get("request_id"), field="request_id", required=False)
    root_id = _safe_id(args.get("root_id"), field="root_id", required=False)
    rows, _status = _overview_rows(root, {"include_completed": True, "limit": 120})
    if agent_ref:
        for row in rows:
            if row.get("agent_ref") == agent_ref:
                return row
    if session_id:
        for preferred_kind in ("codex_saved_session", "codex_live_session", "domain_weaver_worker"):
            for row in rows:
                if row.get("session_id") == session_id and row.get("agent_kind") == preferred_kind:
                    return row
        for row in rows:
            if row.get("session_id") == session_id:
                return row
    for row in rows:
        if run_id and row.get("run_id") == run_id:
            return row
        if request_id and row.get("request_id") == request_id:
            return row
        if root_id and row.get("root_id") == root_id:
            return row
    return None


def _agent_detail(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    row = _find_row(root, args)
    payload = _base("agent_observatory_agent_detail")
    if not row:
        payload.update({"found": False, "finding": "agent_not_found"})
        return payload
    detail: dict[str, Any] = {"record": row, "evidence": []}
    session_id = row.get("session_id")
    if session_id and row.get("agent_kind") == "codex_saved_session":
        detail["codex_session_summary"] = _call_session_store(root, "session_summary", {"session_id": session_id, "message_count": 12})
        detail["codex_session_resume_status"] = _call_session_store(root, "session_resume_status", {"session_id": session_id})
    if session_id and row.get("agent_kind") == "codex_live_session":
        detail["codex_live_session_status"] = _call_live_bridge(root, "session_status", {"session_id": session_id})
    for path_value in row.get("evidence_paths") or []:
        if not path_value:
            continue
        try:
            path = _resolve_repo_path(root, path_value)
            detail["evidence"].append({"path": _repo_rel(root, path), "exists": path.exists(), "size_bytes": path.stat().st_size if path.exists() else None})
        except ValueError:
            detail["evidence"].append({"path": _redact(path_value), "exists": None, "note": "external_or_not_repo_path"})
    payload.update({"found": True, "agent_ref": row.get("agent_ref"), "detail": _sanitize(detail, limit=2200)})
    return payload


def _timeline(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    limit = max(1, min(int(args.get("limit") or 30), 200))
    events: list[dict[str, Any]] = []
    session_id = _safe_id(args.get("session_id"), field="session_id", required=False)
    row = _find_row(root, args) if (args.get("agent_ref") or args.get("run_id") or args.get("request_id") or args.get("root_id")) else None
    if not session_id and row and row.get("session_id"):
        session_id = str(row.get("session_id"))
    if session_id:
        summary = _call_session_store(root, "session_summary", {"session_id": session_id, "message_count": 3})
        if summary.get("found"):
            line_count = int(summary.get("line_count") or 1)
            slice_payload = _call_session_store(root, "session_transcript_slice", {"session_id": session_id, "start_line": max(1, line_count - limit), "line_count": limit, "max_bytes": 96_000})
            for record in slice_payload.get("records") or []:
                if isinstance(record, Mapping):
                    events.append({"source": "saved_session", "timestamp": record.get("timestamp"), "event_type": record.get("role") or record.get("payload_type") or record.get("record_type"), "line_no": record.get("line_no"), "text": record.get("text"), "source_of_truth_classification": "saved_session_evidence"})
    for path in _recent_files(root / "ION/05_context/current/chatgpt_connector/task_returns", ("*.json",), limit=limit):
        data = _read_json(path)
        events.append({"source": "codex_queue", "timestamp": data.get("created_at") or data.get("generated_at") or datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(), "event_type": data.get("status") or data.get("schema_id") or "task_return", "path": _repo_rel(root, path), "text": _redact(data.get("summary") or data.get("objective") or data.get("result") or path.name, limit=1200), "source_of_truth_classification": "carrier_intake_evidence"})
    for path in _recent_files(root / "ION/05_context/current/agent_observatory", ("*.json", "*.md"), limit=limit):
        events.append({"source": "agent_observatory", "timestamp": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(), "event_type": "observatory_receipt", "path": _repo_rel(root, path), "source_of_truth_classification": "durable_ion_receipt"})
    events = sorted(events, key=lambda event: _parse_time(event.get("timestamp")) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)[:limit]
    payload = _base("agent_observatory_timeline")
    payload.update({"event_count": len(events), "events": _sanitize(events, limit=1600)})
    return payload


def _latest_tail(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    source = str(args.get("source") or "auto").strip() or "auto"
    line_count = max(1, min(int(args.get("line_count") or 80), 500))
    max_bytes = max(1_000, min(int(args.get("max_bytes") or 64_000), MAX_BYTES))
    session_id = _safe_id(args.get("session_id"), field="session_id", required=False)
    row = _find_row(root, args) if (args.get("agent_ref") or args.get("run_id") or args.get("request_id") or args.get("root_id")) else None
    if not session_id and row and row.get("session_id"):
        session_id = str(row.get("session_id"))
    if source == "auto":
        source = "saved_session" if session_id else "latest_return"
    payload = _base("agent_observatory_latest_tail")
    if source == "saved_session":
        if not session_id:
            return _blocked("agent_observatory_latest_tail", "session_id_required_for_saved_session")
        summary = _call_session_store(root, "session_summary", {"session_id": session_id, "message_count": 3})
        if not summary.get("found"):
            payload.update({"found": False, "session_id": session_id, "finding": "session_not_found"})
            return payload
        start = max(1, int(summary.get("line_count") or 1) - line_count)
        slice_payload = _call_session_store(root, "session_transcript_slice", {"session_id": session_id, "start_line": start, "line_count": line_count, "max_bytes": max_bytes})
        payload.update({"source": source, "session_id": session_id, "tail": slice_payload, "bounded": True})
        return payload
    if source in {"inbox", "outbox"}:
        if not session_id:
            return _blocked("agent_observatory_latest_tail", "session_id_required_for_live_session_tail")
        path = root / "ION/05_context/current/chatgpt_connector/codex_live_sessions" / session_id / f"{source}.jsonl"
        payload.update({"source": source, "session_id": session_id, "tail": _jsonl_tail(path, line_count=line_count), "path": _repo_rel(root, path), "bounded": True})
        return payload
    if source in {"latest_return", "stdout", "stderr"}:
        target_path = None
        if row and row.get("latest_return_path"):
            target_path = row.get("latest_return_path")
        elif args.get("path"):
            target_path = args.get("path")
        if not target_path:
            latest = _latest_task_return(root)
            target_path = latest.get("path") if latest else None
        if not target_path:
            payload.update({"source": source, "found": False, "finding": "no_tail_path_available"})
            return payload
        try:
            path = _resolve_repo_path(root, target_path)
        except ValueError as exc:
            return _blocked("agent_observatory_latest_tail", str(exc), refusal_class="PATH_NOT_ALLOWED")
        payload.update({"source": source, "path": _repo_rel(root, path), "tail": _read_text_tail(path, max_bytes=max_bytes, line_count=line_count), "bounded": True})
        return payload
    return _blocked("agent_observatory_latest_tail", "unsupported_tail_source", data={"source": source})


def _action_affordances(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    row = _find_row(root, args)
    session_id = _safe_id(args.get("session_id"), field="session_id", required=False)
    if row and row.get("session_id"):
        session_id = str(row.get("session_id"))
    actions: list[dict[str, Any]] = []
    if session_id:
        actions.extend(_codex_saved_session_actions(session_id))
        live_status_path = root / "ION/05_context/current/chatgpt_connector/codex_live_sessions" / session_id / "session.json"
        if live_status_path.is_file():
            actions.extend(
                [
                    {"action_id": "live_session_status", "branch_id": "codex_live_session_bridge", "route_id": "session_status", "args": {"session_id": session_id}, "requires_confirmation": False},
                    {"action_id": "relay_enqueue_preview", "branch_id": "codex_live_session_bridge", "route_id": "relay_enqueue_preview", "args": {"session_id": session_id, "message": "<bounded message>"}, "requires_confirmation": False},
                    {"action_id": "relay_enqueue", "branch_id": "codex_live_session_bridge", "route_id": "relay_enqueue", "args": {"session_id": session_id, "idempotency_key": "<stable key>", "confirmation": CONFIRMATION_TOKEN}, "requires_confirmation": True},
                ]
            )
    if row and row.get("agent_kind") == "codex_queue_worker":
        actions.extend(
            [
                {"action_id": "worker_shift_status", "branch_id": "worker_shift", "route_id": "status_summary", "args": {}, "requires_confirmation": False},
                {"action_id": "latest_return_tail", "branch_id": "agent_observatory", "route_id": "agent_observatory_latest_tail", "args": {"agent_ref": row.get("agent_ref"), "source": "latest_return", "line_count": 80}, "requires_confirmation": False},
            ]
        )
    root_id = _safe_id(args.get("root_id"), field="root_id", required=False) or (str(row.get("root_id")) if row and row.get("root_id") else "")
    if root_id:
        actions.extend(
            [
                {"action_id": "root_profile", "branch_id": "multi_root_workspace", "route_id": "root_file_profile", "args": {"root_id": root_id, "path": "."}, "requires_confirmation": False},
                {"action_id": "root_spawn_preview", "branch_id": "multi_root_workspace", "route_id": "root_agent_spawn_preview", "args": {"root_id": root_id, "cwd": ".", "objective": "<objective>", "agent_role": "<role>"}, "requires_confirmation": False},
            ]
        )
    if not actions:
        actions.append({"action_id": "no_action_available", "reason": "No recognized agent_ref/session_id/run_id/root_id affordance", "requires_confirmation": False})
    payload = _base("agent_observatory_action_affordances")
    payload.update({"agent_ref": row.get("agent_ref") if row else None, "session_id": session_id or None, "action_count": len(actions), "actions": _sanitize(actions, limit=1200), "all_mutating_actions_require_confirmation": all((not action.get("requires_confirmation")) or CONFIRMATION_TOKEN in json.dumps(action.get("args") or {}) for action in actions if isinstance(action, Mapping))})
    return payload


def _domain_weaver_status(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    payload = _base("agent_observatory_domain_weaver_status")
    payload.update(_domain_weaver_card(root))
    payload["route_id"] = "agent_observatory_domain_weaver_status"
    return payload


def _cockpit_status(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    payload = _base("agent_observatory_cockpit_status")
    payload.update(_cockpit_card(root))
    payload["route_id"] = "agent_observatory_cockpit_status"
    return payload


def _register_external_observation(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "agent_observatory_register_external_observation"
    gated = _require_gate(route_id, args)
    if gated:
        return gated
    key = _safe_file_slug(args.get("idempotency_key"), field="idempotency_key")
    observation_id = _safe_file_slug(args.get("observation_id") or args.get("idempotency_key"), field="observation_id")
    session_id = _safe_id(args.get("session_id"), field="session_id", required=False)
    path = root / CONTEXT_RELATIVE_ROOT / "observations" / observation_id / "observation.json"
    receipt_path = root / CONTEXT_RELATIVE_ROOT / "observations" / observation_id / f"register_external_observation_{key}_receipt.json"
    if receipt_path.is_file():
        receipt = _read_json(receipt_path)
        payload = _base(route_id)
        payload.update({"idempotent_replay": True, "receipt_path": _repo_rel(root, receipt_path), "receipt": receipt})
        return payload
    observation = {
        "schema_id": "ion.agent_observatory.external_ui_observation.v1_candidate",
        "created_at": _now(),
        "observation_id": observation_id,
        "session_id": session_id or None,
        "agent_ref": _safe_id(args.get("agent_ref"), field="agent_ref", required=False) or None,
        "observed_status": _redact(args.get("observed_status") or args.get("status") or "unknown", limit=240),
        "observation": _redact(args.get("observation") or args.get("message") or "", limit=6000),
        "observer": _redact(args.get("observer") or "browser_gpt_or_operator", limit=160),
        "evidence_paths": [_redact(item, limit=500) for item in (args.get("evidence_paths") or []) if item] if isinstance(args.get("evidence_paths"), list) else [],
        "source_of_truth_classification": "ui_session_evidence",
        "authority": dict(AUTHORITY_FALSE),
        **AUTHORITY_FALSE,
        "non_claims": list(NON_CLAIMS),
    }
    _write_json(path, observation)
    receipt = {
        "schema_id": "ion.agent_observatory.external_ui_observation_receipt.v1_candidate",
        "created_at": _now(),
        "operation": route_id,
        "idempotency_key_hash": hashlib.sha256(str(args.get("idempotency_key") or "").encode("utf-8")).hexdigest(),
        "observation_path": _repo_rel(root, path),
        "observation_id": observation_id,
        "session_id": session_id or None,
        "source_of_truth_classification": "durable_ion_receipt",
        "authority": dict(AUTHORITY_FALSE),
        **AUTHORITY_FALSE,
        "non_claims": list(NON_CLAIMS),
    }
    _write_json(receipt_path, receipt)
    payload = _base(route_id)
    payload.update({"mutates_active_state": True, "observation_path": _repo_rel(root, path), "receipt_path": _repo_rel(root, receipt_path), "session_id": session_id or None})
    return payload


def _receipts(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    limit = max(1, min(int(args.get("limit") or 50), 200))
    base = root / CONTEXT_RELATIVE_ROOT
    receipts: list[dict[str, Any]] = []
    if base.is_dir():
        for path in sorted(base.rglob("*.json"), key=lambda item: (item.stat().st_mtime, item.as_posix()), reverse=True):
            if len(receipts) >= limit:
                break
            data = _read_json(path)
            receipts.append({"path": _repo_rel(root, path), "schema_id": data.get("schema_id"), "created_at": data.get("created_at") or data.get("generated_at"), "session_id": data.get("session_id"), "size_bytes": path.stat().st_size})
    payload = _base("agent_observatory_receipts")
    payload.update({"receipt_count": len(receipts), "receipts": receipts, "context_root": _repo_rel(root, base)})
    return payload


def _session_search(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    session_id = _safe_id(args.get("session_id"), field="session_id")
    query = str(args.get("query") or "").strip()
    if not query:
        return _blocked("agent_observatory_session_search", "query_required")
    result = _call_session_store(root, "session_find", {"session_id": session_id, "query": query, "max_matches": args.get("max_matches") or 20})
    payload = _base("agent_observatory_session_search")
    payload.update({"session_id": session_id, "wrapped_branch_id": "codex_session_store", "wrapped_route_id": "session_find", "result": _sanitize(result, limit=1600)})
    return payload


def _recommended_next(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    rows, source_status = _overview_rows(root, {"limit": 60, "include_completed": False})
    domain_row = next((row for row in rows if row.get("agent_ref") == "domain_weaver:current"), None)
    target_row = next((row for row in rows if row.get("session_id") == TARGET_DOMAIN_WEAVER_SESSION_ID), None)
    recommendation = {
        "action_class": "read_detail",
        "branch_id": "agent_observatory",
        "route_id": "agent_observatory_agent_detail",
        "args": {"session_id": TARGET_DOMAIN_WEAVER_SESSION_ID},
        "rationale": "Target Domain Weaver Codex session is the clearest high-signal current evidence surface.",
    }
    if domain_row and domain_row.get("blockers"):
        recommendation = {
            "action_class": "observe",
            "branch_id": "agent_observatory",
            "route_id": "agent_observatory_domain_weaver_status",
            "args": {},
            "rationale": "Domain Weaver still carries materialization/exact-active blockers; inspect compact status before any work packet.",
        }
    if not target_row:
        recommendation = {"action_class": "blocker", "branch_id": "codex_session_store", "route_id": "session_store_discovery", "args": {"session_id": TARGET_DOMAIN_WEAVER_SESSION_ID}, "rationale": "Target saved session not visible in observatory overview."}
    payload = _base("agent_observatory_recommended_next")
    payload.update({"recommended_next": recommendation, "source_status": _sanitize(source_status, limit=1200)})
    return payload


def _snapshot(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    route_id = "agent_observatory_snapshot"
    gated = _require_gate(route_id, args)
    if gated:
        return gated
    key = _safe_file_slug(args.get("idempotency_key"), field="idempotency_key")
    requested_name = str(args.get("snapshot_name") or "").strip()
    if requested_name:
        if "/" in requested_name or "\\" in requested_name or ".." in requested_name or not requested_name.endswith(".json"):
            return _blocked(route_id, "unsafe_snapshot_name", refusal_class="PATH_NOT_ALLOWED")
        filename = requested_name
    else:
        filename = f"AGENT_OBSERVATORY_SNAPSHOT_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{key}.candidate.json"
    path = root / CONTEXT_RELATIVE_ROOT / "snapshots" / filename
    receipt_path = root / CONTEXT_RELATIVE_ROOT / "snapshots" / f"{filename}.receipt.json"
    if path.is_file() and receipt_path.is_file():
        payload = _base(route_id)
        payload.update({"idempotent_replay": True, "snapshot_path": _repo_rel(root, path), "receipt_path": _repo_rel(root, receipt_path)})
        return payload
    overview = _overview(root, {"limit": args.get("limit") or 80, "include_completed": True, "max_message_chars": 1000})
    domain = _domain_weaver_status(root, {})
    cockpit = _cockpit_status(root, {})
    target_detail = _agent_detail(root, {"session_id": TARGET_DOMAIN_WEAVER_SESSION_ID})
    snapshot = {
        "schema_id": "ion.agent_observatory.snapshot.v1_candidate",
        "created_at": _now(),
        "snapshot_name": filename,
        "overview": overview,
        "domain_weaver_status": domain,
        "cockpit_status": cockpit,
        "target_session_detail": target_detail,
        "source_paths": [
            "ION/04_packages/kernel/ion_agent_observatory.py",
            "ION/04_packages/kernel/ion_action_mcp_branch_leaders.py",
            "ION/03_registry/ion_action_mcp_branch_leader_registry.yaml",
        ],
        "limitations": [
            "Direct Codex UI control is not claimed.",
            "Automatic live-session polling is not claimed.",
            "Snapshot is candidate projection only.",
        ],
        "authority": dict(AUTHORITY_FALSE),
        **AUTHORITY_FALSE,
        "non_claims": list(NON_CLAIMS),
    }
    _write_json(path, snapshot)
    receipt = {
        "schema_id": "ion.agent_observatory.snapshot_receipt.v1_candidate",
        "created_at": _now(),
        "operation": route_id,
        "snapshot_path": _repo_rel(root, path),
        "snapshot_name": filename,
        "idempotency_key_hash": hashlib.sha256(str(args.get("idempotency_key") or "").encode("utf-8")).hexdigest(),
        "source_of_truth_classification": "durable_ion_receipt",
        "authority": dict(AUTHORITY_FALSE),
        **AUTHORITY_FALSE,
        "non_claims": list(NON_CLAIMS),
    }
    _write_json(receipt_path, receipt)
    payload = _base(route_id)
    payload.update({"mutates_active_state": True, "snapshot_path": _repo_rel(root, path), "receipt_path": _repo_rel(root, receipt_path), "agent_count": overview.get("agent_count")})
    return payload


ROUTES = {
    "agent_observatory_overview": _overview,
    "agent_observatory_agent_detail": _agent_detail,
    "agent_observatory_timeline": _timeline,
    "agent_observatory_latest_tail": _latest_tail,
    "agent_observatory_action_affordances": _action_affordances,
    "agent_observatory_domain_weaver_status": _domain_weaver_status,
    "agent_observatory_cockpit_status": _cockpit_status,
    "agent_observatory_register_external_observation": _register_external_observation,
    "agent_observatory_receipts": _receipts,
    "agent_observatory_session_search": _session_search,
    "agent_observatory_recommended_next": _recommended_next,
    "agent_observatory_snapshot": _snapshot,
}


def invoke_agent_observatory_route(root: str | Path | None, *, route_id: str, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    handler = ROUTES.get(route_id)
    if handler is None:
        return _blocked(route_id, "route_not_supported_by_agent_observatory", refusal_class="BRANCH_ROUTE_NOT_FOUND", data={"route_id": route_id})
    try:
        return handler(shell_root, args or {})
    except ValueError as exc:
        return _blocked(route_id, str(exc), refusal_class="SCHEMA_INVALID")
