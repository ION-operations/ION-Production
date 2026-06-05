"""Durable bridge records for existing/live Codex CLI/UI sessions.

This module does not control a live Codex UI. It creates first-class ION
candidate records so Browser GPT, ION, an operator, and a current Codex session
can exchange durable inbox/outbox messages and receipts by session id.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SCHEMA_ID = "ion.codex_live_session_bridge.v1_candidate"
CONFIRMATION_TOKEN = "ION_BOUNDED_WRITE_CONFIRMED"
BASE_RELATIVE_PATH = Path("ION/05_context/current/chatgpt_connector/codex_live_sessions")
MAX_TEXT_CHARS = 12_000
MAX_OBJECT_TEXT_CHARS = 4_000
SAFE_SESSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{2,127}$")

AUTHORITY_FALSE = {
    "accepted_state_claim": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "git_push_authority": False,
    "deletion_authority": False,
}
SOURCE_CLASSES = {
    "ui_session_evidence",
    "durable_ion_receipt",
    "carrier_intake_evidence",
    "candidate_summary",
}
NON_CLAIMS = [
    "This bridge does not directly control an existing Codex UI or CLI process.",
    "Inbound relay records are durable inbox entries until a Codex process or operator reads them.",
    "Outbox and harvest records are candidate evidence only.",
    "No accepted-state, production, live-execution, secrets, git-push, deletion, materialization, or active-registry movement authority is granted.",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_root(root: str | Path | None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").is_file() and (path / "ION/REPO_AUTHORITY.md").is_file():
            return path
    return candidate


def _repo_rel(root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject(route_id: str, finding: str, *, refusal_class: str = "SCHEMA_INVALID", data: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": False,
        "schema_id": SCHEMA_ID,
        "route_id": route_id,
        "finding": finding,
        "refusal_class": refusal_class,
        "mutates_active_state": False,
        **AUTHORITY_FALSE,
    }
    if data:
        payload.update(dict(data))
    return payload


def _success(route_id: str, data: Mapping[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": True,
        "schema_id": SCHEMA_ID,
        "route_id": route_id,
        "generated_at": _now(),
        **AUTHORITY_FALSE,
    }
    payload.update(dict(data))
    return payload


def _redact_secret_text(value: str) -> str:
    text = value
    text = re.sub(r"sk-[A-Za-z0-9_-]{10,}", "sk-***REDACTED***", text)
    text = re.sub(r"gh[pousr]_[A-Za-z0-9_]{16,}", "gh***_***REDACTED***", text)
    text = re.sub(r"AIza[0-9A-Za-z_-]{20,}", "AIza***REDACTED***", text)
    text = re.sub(r"ya29\.[0-9A-Za-z_.-]+", "ya29.***REDACTED***", text)
    text = re.sub(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}", "Bearer ***REDACTED***", text)

    def _pair(match: re.Match[str]) -> str:
        return f"{match.group(1)}=***REDACTED***"

    text = re.sub(
        r"(?i)\b([A-Z0-9_]*(?:API[_-]?KEY|TOKEN|SECRET|PASSWORD|AUTHORIZATION)[A-Z0-9_]*)\s*[:=]\s*['\"]?[^ \n\r\t,'\"]+",
        _pair,
        text,
    )
    return text


def _safe_text(value: Any, *, limit: int = MAX_TEXT_CHARS) -> str:
    text = str(value or "").strip()
    redacted = _redact_secret_text(text)
    if len(redacted) <= limit:
        return redacted
    return redacted[:limit] + "...[truncated]"


def _sanitize_jsonish(value: Any, *, text_limit: int = MAX_OBJECT_TEXT_CHARS) -> Any:
    if isinstance(value, Mapping):
        return {_safe_text(key, limit=120): _sanitize_jsonish(item, text_limit=text_limit) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize_jsonish(item, text_limit=text_limit) for item in value[:100]]
    if isinstance(value, tuple):
        return [_sanitize_jsonish(item, text_limit=text_limit) for item in value[:100]]
    if isinstance(value, str):
        return _safe_text(value, limit=text_limit)
    if isinstance(value, (bool, int, float)) or value is None:
        return value
    return _safe_text(value, limit=text_limit)


def _safe_session_id(value: Any) -> str:
    session_id = str(value or "").strip()
    if not session_id:
        raise ValueError("session_id_required")
    if "/" in session_id or "\\" in session_id or ".." in session_id:
        raise ValueError("unsafe_session_id")
    if not SAFE_SESSION_RE.match(session_id):
        raise ValueError("unsafe_session_id")
    return session_id


def _safe_key(value: Any) -> str:
    key = str(value or "").strip()
    if not key:
        raise ValueError("idempotency_key_required")
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
    slug = re.sub(r"[^A-Za-z0-9_.:-]+", "_", key).strip("._:-")
    if not slug or ".." in slug or "/" in slug or "\\" in slug:
        slug = "key"
    return f"{slug[:72]}_{digest}"


def _safe_rel_path(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    path = Path(text)
    if path.is_absolute() or text.startswith("~") or "\\" in text:
        raise ValueError("unsafe_path_ref")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("unsafe_path_ref")
    return path.as_posix()


def _safe_refs(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    raw = value if isinstance(value, list) else [value]
    refs: list[str] = []
    for item in raw[:100]:
        refs.append(_safe_rel_path(item))
    return refs


def _safe_status(value: Any) -> str:
    status = str(value or "active").strip().lower()
    return status if status in {"active", "paused", "completed", "unknown"} else "unknown"


def _safe_source_class(value: Any, default: str) -> str:
    source = str(value or default).strip()
    return source if source in SOURCE_CLASSES else default


def _paths(root: Path, session_id: str) -> dict[str, Path]:
    base = root / BASE_RELATIVE_PATH
    session_dir = base / session_id
    return {
        "base": base,
        "index": base / "INDEX.json",
        "session_dir": session_dir,
        "session": session_dir / "session.json",
        "inbox": session_dir / "inbox.jsonl",
        "outbox": session_dir / "outbox.jsonl",
        "relays": session_dir / "relays",
        "harvests": session_dir / "harvests",
        "receipts": session_dir / "receipts",
        "latest_status": session_dir / "latest_status.json",
    }


def _ensure_session_dirs(paths: Mapping[str, Path]) -> None:
    for key in ["base", "session_dir", "relays", "harvests", "receipts"]:
        paths[key].mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return dict(value) if isinstance(value, Mapping) else None


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _append_jsonl(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def _jsonl_count(path: Path) -> int:
    if not path.is_file():
        return 0
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return sum(1 for line in handle if line.strip())


def _latest_file(path: Path, pattern: str = "*") -> Path | None:
    if not path.is_dir():
        return None
    candidates = [item for item in path.glob(pattern) if item.is_file()]
    if not candidates:
        return None
    return sorted(candidates, key=lambda item: (item.stat().st_mtime, item.name), reverse=True)[0]


def _record_base(schema_id: str, session_id: str, source_class: str, *, created_at: str | None = None) -> dict[str, Any]:
    return {
        "schema_id": schema_id,
        "created_at": created_at or _now(),
        "session_id": session_id,
        **AUTHORITY_FALSE,
        "authority": dict(AUTHORITY_FALSE),
        "source_of_truth_classification": source_class,
        "non_claims": list(NON_CLAIMS),
    }


def _session_record(args: Mapping[str, Any], *, existing: Mapping[str, Any] | None = None) -> dict[str, Any]:
    session_id = _safe_session_id(args.get("session_id"))
    existing = existing or {}
    created_at = str(existing.get("created_at") or _now())
    role_id = _safe_text(args.get("role_id") or existing.get("role_id") or "unknown_codex_live_session_role", limit=240)
    display_name = _safe_text(args.get("display_name") or existing.get("display_name") or role_id or session_id, limit=240)
    context_refs = _safe_refs(args.get("context_refs") if "context_refs" in args else existing.get("context_refs"))
    evidence_refs = _safe_refs(args.get("evidence_refs") if "evidence_refs" in args else existing.get("evidence_refs") or context_refs)
    current_packet_path = _safe_rel_path(args.get("current_packet_path") if "current_packet_path" in args else existing.get("current_packet_path"))
    source_class = _safe_source_class(args.get("source_of_truth_classification"), "carrier_intake_evidence")
    relay_policy = args.get("relay_policy") if isinstance(args.get("relay_policy"), Mapping) else existing.get("relay_policy")
    if not isinstance(relay_policy, Mapping):
        relay_policy = {
            "inbound_delivery": "durable_inbox_record_only",
            "codex_session_polling_required": True,
            "operator_paste_fallback": True,
            "outbox_reply": "durable_outbox_record",
            "automatic_live_ui_control_proven": False,
            "max_message_chars": MAX_TEXT_CHARS,
        }
    record = _record_base("ion.codex_live_session_bridge.session.v1", session_id, source_class, created_at=created_at)
    record.update(
        {
            "updated_at": _now(),
            "role_id": role_id,
            "display_name": display_name,
            "objective": _safe_text(args.get("objective") or existing.get("objective"), limit=MAX_TEXT_CHARS),
            "current_packet_id": _safe_text(args.get("current_packet_id") or existing.get("current_packet_id") or "unknown_current_packet", limit=240),
            "current_packet_path": current_packet_path,
            "domain_id": _safe_text(args.get("domain_id") or existing.get("domain_id") or "unknown_domain", limit=240),
            "owner": _safe_text(args.get("owner") or existing.get("owner") or "codex_cli_current_session", limit=160),
            "registered_by": _safe_text(args.get("registered_by") or existing.get("registered_by") or "ion", limit=160),
            "status": _safe_status(args.get("status") or existing.get("status")),
            "relay_policy": _sanitize_jsonish(relay_policy),
            "authority_flags": dict(AUTHORITY_FALSE),
            "context_refs": context_refs,
            "evidence_refs": evidence_refs,
            "notes": _safe_text(args.get("notes") or existing.get("notes"), limit=MAX_TEXT_CHARS),
        }
    )
    return record


def _index_record(root: Path, session: Mapping[str, Any]) -> dict[str, Any]:
    paths = _paths(root, str(session["session_id"]))
    existing = _read_json(paths["index"]) or {}
    sessions = existing.get("sessions") if isinstance(existing.get("sessions"), Mapping) else {}
    sessions = dict(sessions)
    sessions[str(session["session_id"])] = {
        "session_id": session["session_id"],
        "role_id": session.get("role_id"),
        "display_name": session.get("display_name"),
        "objective": session.get("objective"),
        "domain_id": session.get("domain_id"),
        "current_packet_id": session.get("current_packet_id"),
        "status": session.get("status"),
        "updated_at": session.get("updated_at"),
        "session_path": _repo_rel(root, paths["session"]),
        "latest_status_path": _repo_rel(root, paths["latest_status"]),
    }
    record = _record_base(
        "ion.codex_live_session_bridge.index.v1",
        "__index__",
        "durable_ion_receipt",
        created_at=str(existing.get("created_at") or _now()),
    )
    record.update(
        {
            "updated_at": _now(),
            "session_count": len(sessions),
            "sessions": dict(sorted(sessions.items())),
        }
    )
    return record


def _receipt_path(paths: Mapping[str, Path], operation: str, key: str | None = None) -> Path:
    if operation == "session_register" and not key:
        return paths["receipts"] / "session_register_receipt.json"
    suffix = _safe_key(key or operation)
    return paths["receipts"] / f"{operation}_{suffix}_receipt.json"


def _write_receipt(root: Path, paths: Mapping[str, Path], operation: str, payload: Mapping[str, Any], *, idempotency_key: str | None = None) -> tuple[Path, Path | None]:
    primary = _receipt_path(paths, operation)
    idem = _receipt_path(paths, operation, idempotency_key) if idempotency_key else None
    receipt = dict(payload)
    receipt["receipt_path"] = _repo_rel(root, primary)
    if idem:
        receipt["idempotency_receipt_path"] = _repo_rel(root, idem)
    _write_json(primary, receipt)
    if idem and idem != primary:
        _write_json(idem, receipt)
    return primary, idem


def _idempotent_receipt(paths: Mapping[str, Path], operation: str, idempotency_key: Any) -> dict[str, Any] | None:
    try:
        path = _receipt_path(paths, operation, str(idempotency_key or ""))
    except ValueError:
        return None
    return _read_json(path)


def _status_payload(root: Path, session_id: str) -> dict[str, Any]:
    paths = _paths(root, session_id)
    session = _read_json(paths["session"])
    latest_harvest = _latest_file(paths["harvests"], "*.json")
    latest_receipt = _latest_file(paths["receipts"], "*.json")
    record = _record_base("ion.codex_live_session_bridge.status.v1", session_id, "durable_ion_receipt")
    record.update(
        {
            "registered": bool(session),
            "session_path": _repo_rel(root, paths["session"]),
            "index_path": _repo_rel(root, paths["index"]),
            "inbox_path": _repo_rel(root, paths["inbox"]),
            "outbox_path": _repo_rel(root, paths["outbox"]),
            "latest_status_path": _repo_rel(root, paths["latest_status"]),
            "inbox_count": _jsonl_count(paths["inbox"]),
            "outbox_count": _jsonl_count(paths["outbox"]),
            "receipt_count": len([item for item in paths["receipts"].glob("*.json")]) if paths["receipts"].is_dir() else 0,
            "latest_harvest_path": _repo_rel(root, latest_harvest) if latest_harvest else None,
            "latest_receipt_path": _repo_rel(root, latest_receipt) if latest_receipt else None,
            "session": session,
            "direct_live_codex_ui_control_proven": False,
            "automatic_polling_proven": False,
            "durable_inbox_outbox_relay_proven": bool(session),
            "mutates_active_state": False,
        }
    )
    return record


def _write_latest_status(root: Path, session_id: str) -> Path:
    paths = _paths(root, session_id)
    status = _status_payload(root, session_id)
    _write_json(paths["latest_status"], status)
    return paths["latest_status"]


def _require_mutation_gate(route_id: str, args: Mapping[str, Any]) -> dict[str, Any] | None:
    if not str(args.get("idempotency_key") or "").strip():
        return _reject(route_id, "idempotency_key_required", refusal_class="IDEMPOTENCY_KEY_REQUIRED")
    if str(args.get("confirmation") or "") != CONFIRMATION_TOKEN:
        return _reject(route_id, "confirmation_required", refusal_class="CONFIRMATION_REQUIRED", data={"required_confirmation": CONFIRMATION_TOKEN})
    return None


def _relay_payload(args: Mapping[str, Any], *, relay_id: str) -> dict[str, Any]:
    session_id = _safe_session_id(args.get("session_id"))
    source_class = _safe_source_class(args.get("source_of_truth_classification"), "carrier_intake_evidence")
    contract = args.get("expected_response_contract")
    if not isinstance(contract, Mapping):
        contract = {
            "reply_route": "codex_live_session_bridge.outbox_record",
            "reply_required": True,
            "preserve_non_claims": True,
        }
    stop_condition = args.get("stop_settlement_condition") or args.get("stop_condition") or "Stop after recording a durable outbox reply or a precise durable status path."
    record = _record_base("ion.codex_live_session_bridge.relay_message.v1", session_id, source_class)
    record.update(
        {
            "relay_id": relay_id,
            "from": _safe_text(args.get("from") or "browser_gpt", limit=80),
            "to": "codex_session",
            "objective": _safe_text(args.get("objective"), limit=MAX_TEXT_CHARS),
            "message": _safe_text(args.get("message"), limit=MAX_TEXT_CHARS),
            "expected_response_contract": _sanitize_jsonish(contract),
            "stop_settlement_condition": _safe_text(stop_condition, limit=MAX_TEXT_CHARS),
            "authority_flags": dict(AUTHORITY_FALSE),
        }
    )
    return record


def _outbox_payload(args: Mapping[str, Any], *, outbox_id: str) -> dict[str, Any]:
    session_id = _safe_session_id(args.get("session_id"))
    record = _record_base("ion.codex_live_session_bridge.outbox_message.v1", session_id, "carrier_intake_evidence")
    record.update(
        {
            "outbox_id": outbox_id,
            "from": "codex_session",
            "to": _safe_text(args.get("to") or "browser_gpt", limit=80),
            "objective": _safe_text(args.get("objective"), limit=MAX_TEXT_CHARS),
            "message": _safe_text(args.get("message") or args.get("reply"), limit=MAX_TEXT_CHARS),
            "summary": _safe_text(args.get("summary"), limit=MAX_TEXT_CHARS),
            "progress_status": _safe_text(args.get("progress_status") or "candidate_update", limit=160),
            "evidence_paths": _safe_refs(args.get("evidence_paths") or args.get("evidence_refs")),
            "authority_flags": dict(AUTHORITY_FALSE),
        }
    )
    return record


def _harvest_payload(args: Mapping[str, Any], *, harvest_id: str) -> dict[str, Any]:
    session_id = _safe_session_id(args.get("session_id"))
    record = _record_base("ion.codex_live_session_bridge.harvest.v1", session_id, "ui_session_evidence")
    record.update(
        {
            "harvest_id": harvest_id,
            "source_session_id": session_id,
            "transcript_excerpt": _safe_text(args.get("transcript_excerpt") or args.get("transcript"), limit=MAX_TEXT_CHARS),
            "summary": _safe_text(args.get("summary"), limit=MAX_TEXT_CHARS),
            "evidence_paths": _safe_refs(args.get("evidence_paths") or args.get("evidence_refs")),
            "candidate_summary": _safe_text(args.get("candidate_summary"), limit=MAX_TEXT_CHARS),
            "authority_flags": dict(AUTHORITY_FALSE),
        }
    )
    return record


def _session_register_preview(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    session = _session_record(args)
    paths = _paths(root, str(session["session_id"]))
    return _success(
        "session_register_preview",
        {
            "session_id": session["session_id"],
            "session_preview": session,
            "would_write": False,
            "would_write_paths": [
                _repo_rel(root, paths["session"]),
                _repo_rel(root, paths["index"]),
                _repo_rel(root, paths["receipts"] / "session_register_receipt.json"),
                _repo_rel(root, paths["latest_status"]),
            ],
            "mutates_active_state": False,
        },
    )


def _session_register(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    gated = _require_mutation_gate("session_register", args)
    if gated:
        return gated
    session_id = _safe_session_id(args.get("session_id"))
    paths = _paths(root, session_id)
    _ensure_session_dirs(paths)
    replay = _idempotent_receipt(paths, "session_register", args.get("idempotency_key"))
    if replay:
        return _success(
            "session_register",
            {
                "session_id": session_id,
                "idempotent_replay": True,
                "receipt": replay,
                "receipt_path": replay.get("receipt_path"),
                "mutates_active_state": False,
            },
        )
    existing = _read_json(paths["session"])
    session = _session_record(args, existing=existing)
    _write_json(paths["session"], session)
    index = _index_record(root, session)
    _write_json(paths["index"], index)
    latest_status = _write_latest_status(root, session_id)
    receipt = _record_base("ion.codex_live_session_bridge.session_register_receipt.v1", session_id, "durable_ion_receipt")
    touched = [paths["session"], paths["index"], latest_status]
    receipt.update(
        {
            "operation": "session_register",
            "idempotency_key": _safe_text(args.get("idempotency_key"), limit=200),
            "session_path": _repo_rel(root, paths["session"]),
            "index_path": _repo_rel(root, paths["index"]),
            "latest_status_path": _repo_rel(root, latest_status),
            "touched_paths": [_repo_rel(root, path) for path in touched],
            "session_sha256": _sha256_file(paths["session"]),
            "index_sha256": _sha256_file(paths["index"]),
        }
    )
    primary, idem = _write_receipt(root, paths, "session_register", receipt, idempotency_key=str(args.get("idempotency_key") or ""))
    return _success(
        "session_register",
        {
            "session_id": session_id,
            "session_path": _repo_rel(root, paths["session"]),
            "index_path": _repo_rel(root, paths["index"]),
            "receipt_path": _repo_rel(root, primary),
            "idempotency_receipt_path": _repo_rel(root, idem) if idem else None,
            "latest_status_path": _repo_rel(root, latest_status),
            "mutates_active_state": True,
        },
    )


def _session_status(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    session_id = _safe_session_id(args.get("session_id"))
    return _success("session_status", {**_status_payload(root, session_id), "mutates_active_state": False})


def _relay_enqueue_preview(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    session_id = _safe_session_id(args.get("session_id"))
    relay_id = _safe_text(args.get("relay_id") or "relay_preview", limit=160)
    payload = _relay_payload(args, relay_id=relay_id)
    paths = _paths(root, session_id)
    return _success(
        "relay_enqueue_preview",
        {
            "session_id": session_id,
            "session_registered": paths["session"].is_file(),
            "message_payload": payload,
            "would_append": False,
            "target_inbox_path": _repo_rel(root, paths["inbox"]),
            "mutates_active_state": False,
        },
    )


def _relay_enqueue(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    gated = _require_mutation_gate("relay_enqueue", args)
    if gated:
        return gated
    session_id = _safe_session_id(args.get("session_id"))
    paths = _paths(root, session_id)
    if not paths["session"].is_file():
        return _reject("relay_enqueue", "session_not_registered", refusal_class="SESSION_NOT_REGISTERED", data={"session_id": session_id})
    _ensure_session_dirs(paths)
    replay = _idempotent_receipt(paths, "relay_enqueue", args.get("idempotency_key"))
    if replay:
        return _success(
            "relay_enqueue",
            {
                "session_id": session_id,
                "idempotent_replay": True,
                "receipt": replay,
                "receipt_path": replay.get("receipt_path"),
                "mutates_active_state": False,
            },
        )
    relay_slug = _safe_key(args.get("relay_id") or args.get("idempotency_key"))
    relay_id = _safe_text(args.get("relay_id") or f"relay_{relay_slug}", limit=180)
    relay = _relay_payload(args, relay_id=relay_id)
    relay_path = paths["relays"] / f"{relay_slug}.json"
    if relay_path.exists():
        return _reject("relay_enqueue", "relay_id_already_exists", refusal_class="IDEMPOTENCY_KEY_REQUIRED", data={"relay_path": _repo_rel(root, relay_path)})
    _write_json(relay_path, relay)
    _append_jsonl(paths["inbox"], relay)
    latest_status = _write_latest_status(root, session_id)
    receipt = _record_base("ion.codex_live_session_bridge.relay_enqueue_receipt.v1", session_id, "durable_ion_receipt")
    receipt.update(
        {
            "operation": "relay_enqueue",
            "relay_id": relay_id,
            "idempotency_key": _safe_text(args.get("idempotency_key"), limit=200),
            "relay_path": _repo_rel(root, relay_path),
            "inbox_path": _repo_rel(root, paths["inbox"]),
            "latest_status_path": _repo_rel(root, latest_status),
            "inbox_count_after": _jsonl_count(paths["inbox"]),
            "message_excerpt": _safe_text(relay.get("message"), limit=500),
        }
    )
    primary, idem = _write_receipt(root, paths, "relay_enqueue", receipt, idempotency_key=str(args.get("idempotency_key") or ""))
    return _success(
        "relay_enqueue",
        {
            "session_id": session_id,
            "relay_id": relay_id,
            "inbox_path": _repo_rel(root, paths["inbox"]),
            "relay_path": _repo_rel(root, relay_path),
            "receipt_path": _repo_rel(root, primary),
            "idempotency_receipt_path": _repo_rel(root, idem) if idem else None,
            "mutates_active_state": True,
        },
    )


def _outbox_record(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    gated = _require_mutation_gate("outbox_record", args)
    if gated:
        return gated
    session_id = _safe_session_id(args.get("session_id"))
    paths = _paths(root, session_id)
    if not paths["session"].is_file():
        return _reject("outbox_record", "session_not_registered", refusal_class="SESSION_NOT_REGISTERED", data={"session_id": session_id})
    _ensure_session_dirs(paths)
    replay = _idempotent_receipt(paths, "outbox_record", args.get("idempotency_key"))
    if replay:
        return _success("outbox_record", {"session_id": session_id, "idempotent_replay": True, "receipt": replay, "receipt_path": replay.get("receipt_path"), "mutates_active_state": False})
    outbox_slug = _safe_key(args.get("outbox_id") or args.get("idempotency_key"))
    outbox_id = _safe_text(args.get("outbox_id") or f"outbox_{outbox_slug}", limit=180)
    outbox = _outbox_payload(args, outbox_id=outbox_id)
    _append_jsonl(paths["outbox"], outbox)
    latest_status = _write_latest_status(root, session_id)
    receipt = _record_base("ion.codex_live_session_bridge.outbox_record_receipt.v1", session_id, "durable_ion_receipt")
    receipt.update(
        {
            "operation": "outbox_record",
            "outbox_id": outbox_id,
            "idempotency_key": _safe_text(args.get("idempotency_key"), limit=200),
            "outbox_path": _repo_rel(root, paths["outbox"]),
            "latest_status_path": _repo_rel(root, latest_status),
            "outbox_count_after": _jsonl_count(paths["outbox"]),
            "message_excerpt": _safe_text(outbox.get("message"), limit=500),
            "evidence_paths": outbox.get("evidence_paths") or [],
        }
    )
    primary, idem = _write_receipt(root, paths, "outbox_record", receipt, idempotency_key=str(args.get("idempotency_key") or ""))
    return _success(
        "outbox_record",
        {
            "session_id": session_id,
            "outbox_id": outbox_id,
            "outbox_path": _repo_rel(root, paths["outbox"]),
            "receipt_path": _repo_rel(root, primary),
            "idempotency_receipt_path": _repo_rel(root, idem) if idem else None,
            "mutates_active_state": True,
        },
    )


def _harvest_record(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    gated = _require_mutation_gate("harvest_record", args)
    if gated:
        return gated
    session_id = _safe_session_id(args.get("session_id"))
    paths = _paths(root, session_id)
    if not paths["session"].is_file():
        return _reject("harvest_record", "session_not_registered", refusal_class="SESSION_NOT_REGISTERED", data={"session_id": session_id})
    _ensure_session_dirs(paths)
    replay = _idempotent_receipt(paths, "harvest_record", args.get("idempotency_key"))
    if replay:
        return _success("harvest_record", {"session_id": session_id, "idempotent_replay": True, "receipt": replay, "receipt_path": replay.get("receipt_path"), "mutates_active_state": False})
    harvest_slug = _safe_key(args.get("harvest_id") or args.get("idempotency_key"))
    harvest_id = _safe_text(args.get("harvest_id") or f"harvest_{harvest_slug}", limit=180)
    harvest = _harvest_payload(args, harvest_id=harvest_id)
    harvest_path = paths["harvests"] / f"{harvest_slug}.json"
    _write_json(harvest_path, harvest)
    latest_status = _write_latest_status(root, session_id)
    receipt = _record_base("ion.codex_live_session_bridge.harvest_record_receipt.v1", session_id, "durable_ion_receipt")
    receipt.update(
        {
            "operation": "harvest_record",
            "harvest_id": harvest_id,
            "idempotency_key": _safe_text(args.get("idempotency_key"), limit=200),
            "harvest_path": _repo_rel(root, harvest_path),
            "latest_status_path": _repo_rel(root, latest_status),
            "summary_excerpt": _safe_text(harvest.get("summary"), limit=500),
            "evidence_paths": harvest.get("evidence_paths") or [],
        }
    )
    primary, idem = _write_receipt(root, paths, "harvest_record", receipt, idempotency_key=str(args.get("idempotency_key") or ""))
    return _success(
        "harvest_record",
        {
            "session_id": session_id,
            "harvest_id": harvest_id,
            "harvest_path": _repo_rel(root, harvest_path),
            "receipt_path": _repo_rel(root, primary),
            "idempotency_receipt_path": _repo_rel(root, idem) if idem else None,
            "mutates_active_state": True,
        },
    )


def _session_receipts(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    session_id = _safe_session_id(args.get("session_id"))
    limit = max(1, min(int(args.get("limit") or 20), 100))
    paths = _paths(root, session_id)
    receipts = []
    if paths["receipts"].is_dir():
        for item in sorted(paths["receipts"].glob("*.json"), key=lambda path: (path.stat().st_mtime, path.name), reverse=True)[:limit]:
            receipts.append(
                {
                    "path": _repo_rel(root, item),
                    "size_bytes": item.stat().st_size,
                    "sha256": _sha256_file(item),
                }
            )
    return _success(
        "session_receipts",
        {
            "session_id": session_id,
            "receipt_count": len(receipts),
            "receipts": receipts,
            "mutates_active_state": False,
        },
    )


def _session_discovery(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    session_id = _safe_session_id(args.get("session_id"))
    home = Path.home()
    candidates = [
        home / ".codex/history.jsonl",
        home / ".codex/session_index.jsonl",
    ]
    sessions_dir = home / ".codex/sessions"
    if sessions_dir.is_dir():
        files = [item for item in sessions_dir.rglob("*") if item.is_file()]
        candidates.extend(sorted(files, key=lambda item: (item.stat().st_mtime, item.name), reverse=True)[:200])
    findings = []
    for path in candidates:
        row = {
            "path": path.as_posix(),
            "exists": path.is_file(),
            "session_id_appears": False,
            "content_excerpt_returned": False,
        }
        if path.is_file():
            try:
                text = path.read_text(encoding="utf-8", errors="replace")[:2_000_000]
                row["session_id_appears"] = session_id in text or session_id in path.name
                row["scanned_bytes_max"] = min(len(text), 2_000_000)
            except Exception as exc:
                row["read_error"] = exc.__class__.__name__
        findings.append(row)
    return _success(
        "session_discovery",
        {
            "session_id": session_id,
            "safe_paths_only": True,
            "findings": findings,
            "mutates_active_state": False,
            "searched_from_root": _repo_rel(root, root),
        },
    )


def invoke_codex_live_session_bridge_route(
    root: str | Path | None,
    *,
    route_id: str,
    args: Mapping[str, Any],
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    try:
        if route_id == "session_register_preview":
            return _session_register_preview(shell_root, args)
        if route_id == "session_register":
            return _session_register(shell_root, args)
        if route_id == "session_status":
            return _session_status(shell_root, args)
        if route_id == "relay_enqueue_preview":
            return _relay_enqueue_preview(shell_root, args)
        if route_id == "relay_enqueue":
            return _relay_enqueue(shell_root, args)
        if route_id == "outbox_record":
            return _outbox_record(shell_root, args)
        if route_id == "harvest_record":
            return _harvest_record(shell_root, args)
        if route_id == "session_receipts":
            return _session_receipts(shell_root, args)
        if route_id == "session_discovery":
            return _session_discovery(shell_root, args)
    except ValueError as exc:
        return _reject(route_id, str(exc), refusal_class="SCHEMA_INVALID")
    return _reject(route_id, "route_not_supported_by_codex_live_session_bridge", refusal_class="BRANCH_ROUTE_NOT_FOUND", data={"route_id": route_id})
