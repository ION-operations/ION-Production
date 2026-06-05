"""Safe Codex conversation archive projection for the cockpit.

This module indexes local Codex history/session files for navigation. It does
not export raw transcripts by default, expose secrets, or claim that archived
threads are active context.
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SCHEMA_ID = "ion.codex_conversation_archive.v1"
READY_VERDICT = "ION_CODEX_CONVERSATION_ARCHIVE_READY"
DEGRADED_VERDICT = "ION_CODEX_CONVERSATION_ARCHIVE_DEGRADED"

DEFAULT_SESSION_LIMIT = 80
DEFAULT_HISTORY_LIMIT = 5000
SESSION_LINE_SCAN_LIMIT = 4000
SNIPPET_LIMIT = 260
EXCERPT_LIMIT = 24
SELECTED_TRANSCRIPT_LIMIT = 1000
SELECTED_TRANSCRIPT_CHUNK_LIMIT = 500
SELECTED_TRANSCRIPT_TEXT_LIMIT = 12000
ATTACH_EXCERPT_LIMIT = 80
ATTACH_TEXT_LIMIT = 20000
ATTACHMENTS_DIR = Path("ION/05_context/current/codex_capsule_chat/archive_attachments")
WRITE_CONFIRMATION_TOKEN = "ION_BOUNDED_WRITE_CONFIRMED"

SECRET_PATTERNS = (
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]{8,}"),
    re.compile(r"(?i)((?:api[_-]?key|token|secret|password)\s*[:=]\s*)[^\s,;]{4,}"),
)

MISSION_FIELD_PATTERNS = (
    ("active_mission", re.compile(r"(?im)^\s*active_mission\s*:\s*(.+?)\s*$")),
    ("mission", re.compile(r"(?im)^\s*mission\s*:\s*(.+?)\s*$")),
    ("primary_goal", re.compile(r"(?im)^\s*primary_goal\s*:\s*>?\s*(.+?)\s*$")),
)

AGENT_ROLE_NAMES = (
    "PERSONA_INTERFACE",
    "RELAY",
    "STEWARD",
    "VIZIER",
    "MASON",
    "NEMESIS",
    "VICE_REVIEW",
    "SCRIBE",
    "CODEX",
    "CURSOR",
    "GPT",
)

ROLE_PATTERN = re.compile(r"\b(PERSONA_INTERFACE(?:_INGRESS|_RESPONSE)?|RELAY|STEWARD|VIZIER|MASON|NEMESIS(?:_OR_VICE_REVIEW)?|VICE_REVIEW|SCRIBE|CODEX(?:_CLI)?|CURSOR|GPT(?:-\d+(?:\.\d+)?)?)\b", re.IGNORECASE)
FIELD_PATTERN = re.compile(r"(?im)^\s*(suggested_skill|suggested_domain|carrier|carrier_identity|active_phase)\s*:\s*(.+?)\s*$")
PATH_REF_PATTERN = re.compile(r"(?:(?:/home/sev|/tmp|ION|ION_VNEXT|Needs_Routed|browser_extension|local_daemon|product_packager|\.codex)/[^\s,`'\"<>]+)")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    if configured:
        return Path(configured).expanduser()
    return Path(os.environ.get("HOME") or str(Path.home())).expanduser() / ".codex"


def _read_jsonl(path: Path, *, limit: int | None = None) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for index, line in enumerate(handle):
            if limit is not None and index >= limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                rows.append(payload)
    return rows


def _redact(value: Any, *, limit: int = SNIPPET_LIMIT) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(r"\1[REDACTED]", text)
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def _redact_transcript_text(value: Any, *, limit: int = SELECTED_TRANSCRIPT_TEXT_LIMIT) -> str:
    text = str(value or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(r"\1[REDACTED]", text)
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n...[MESSAGE_TRUNCATED]"


def _mtime(path: Path) -> str | None:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat()
    except OSError:
        return None


def _session_id_from_path(path: Path) -> str:
    match = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", path.name)
    return match.group(1) if match else path.stem


def _text_from_response_item(item: Mapping[str, Any]) -> str:
    chunks: list[str] = []
    content = item.get("content")
    if isinstance(content, list):
        for part in content:
            if isinstance(part, Mapping):
                text = part.get("text") or part.get("input_text") or part.get("output_text")
                if text:
                    chunks.append(str(text))
    elif isinstance(content, str):
        chunks.append(content)
    return "\n".join(chunks)


def _function_call_text(item: Mapping[str, Any]) -> str:
    name = str(item.get("name") or "function_call")
    arguments = item.get("arguments")
    if arguments in {None, ""}:
        return name
    if isinstance(arguments, str):
        try:
            parsed = json.loads(arguments)
            argument_text = json.dumps(parsed, indent=2, sort_keys=True)
        except json.JSONDecodeError:
            argument_text = arguments
    else:
        argument_text = json.dumps(arguments, indent=2, sort_keys=True)
    return f"{name}\n{argument_text}"


def _function_output_text(item: Mapping[str, Any]) -> str:
    output = item.get("output")
    if isinstance(output, str):
        return output
    if output is None:
        return "function_call_output"
    return json.dumps(output, indent=2, sort_keys=True)


def _path_refs(value: str, *, limit: int = 12) -> list[str]:
    refs: list[str] = []
    seen: set[str] = set()
    for match in PATH_REF_PATTERN.findall(value or ""):
        cleaned = _redact(match.rstrip(").];:"), limit=180)
        key = cleaned.lower()
        if not cleaned or key in seen:
            continue
        seen.add(key)
        refs.append(cleaned)
        if len(refs) >= limit:
            break
    return refs


def _diff_detail(value: str) -> dict[str, Any]:
    files: list[str] = []
    seen: set[str] = set()
    added = 0
    removed = 0
    for raw_line in str(value or "").splitlines():
        line = raw_line.rstrip()
        lowered = line.lower()
        file_ref = ""
        if lowered.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                file_ref = parts[3].removeprefix("b/")
        elif line.startswith("*** Update File: ") or line.startswith("*** Add File: ") or line.startswith("*** Delete File: "):
            file_ref = line.split(": ", 1)[-1]
        elif line.startswith("+++ ") and not line.startswith("+++ /dev/null"):
            file_ref = line[4:].removeprefix("b/")
        if file_ref:
            cleaned = _redact(file_ref, limit=180)
            key = cleaned.lower()
            if cleaned and key not in seen:
                seen.add(key)
                files.append(cleaned)
        if line.startswith("+") and not line.startswith("+++") and not line.startswith("***"):
            added += 1
        elif line.startswith("-") and not line.startswith("---") and not line.startswith("***"):
            removed += 1
    return {
        "files": files[:12],
        "file_count": len(files),
        "added_lines": added,
        "removed_lines": removed,
    }


def _context_refs(value: str) -> list[str]:
    refs = [ref for ref in _path_refs(value, limit=16) if "context" in ref.lower() or "capsule" in ref.lower() or "mini" in ref.lower()]
    marker_refs: list[str] = []
    for marker in ("CAPSULE.md", "MINI.md", "HOT_CONTEXT.md", "LONG_HORIZON.json", "CONTEXT_PACKAGES.json", "STATUS.json"):
        if marker.lower() in str(value or "").lower() and marker not in marker_refs:
            marker_refs.append(marker)
    return [*refs, *marker_refs][:16]


def _compaction_markers(value: str, *, truncated: bool) -> list[str]:
    haystack = str(value or "").lower()
    markers: list[str] = []
    for needle, label in (
        ("precompact", "PRECOMPACT"),
        ("postcompact", "POSTCOMPACT"),
        ("context refreshed", "CONTEXT_REFRESHED"),
        ("mini_auto_post", "MINI_AUTO_POST"),
        ("[message_truncated]", "MESSAGE_TRUNCATED"),
        ("[attachment_truncated]", "ATTACHMENT_TRUNCATED"),
        ("context boundary", "CONTEXT_BOUNDARY"),
    ):
        if needle in haystack and label not in markers:
            markers.append(label)
    if truncated and "MESSAGE_TRUNCATED" not in markers:
        markers.append("MESSAGE_TRUNCATED")
    return markers


def _classify_transcript_item(*, role: str, row_type: str, payload: Mapping[str, Any], text: str, truncated: bool) -> dict[str, Any]:
    role_value = str(role or "").lower()
    payload_type = str(payload.get("type") or "").lower()
    event_type = str(payload.get("type") or payload.get("event") or "").lower()
    haystack = f"{role_value}\n{payload_type}\n{event_type}\n{text}".lower()
    direct_participant_response = row_type == "response_item" and role_value in {
        "assistant",
        "codex_cli",
        "codex-cli",
        "codex_chat_engine",
        "codex-chat-engine",
        "user",
        "operator",
    }
    common: dict[str, Any] = {"path_refs": _path_refs(text)}
    if truncated:
        return {
            "message_kind": "truncated",
            "visual_lane": "compaction",
            "detail_label": "truncated transcript item",
            "compaction_markers": _compaction_markers(text, truncated=truncated),
            **common,
        }
    if not direct_participant_response and (
        "compact" in haystack or "precompact" in haystack or "postcompact" in haystack or "context refreshed" in haystack
    ):
        return {
            "message_kind": "compaction",
            "visual_lane": "compaction",
            "detail_label": "compaction/context boundary",
            "context_refs": _context_refs(text),
            "compaction_markers": _compaction_markers(text, truncated=truncated),
            **common,
        }
    if (
        "diff --git" in haystack
        or "*** begin patch" in haystack
        or "*** end patch" in haystack
        or "\n+++" in haystack
        or "\n---" in haystack
        or "apply_patch" in haystack
    ):
        return {
            "message_kind": "diff",
            "visual_lane": "diff",
            "detail_label": "file diff / patch",
            "diff_stats": _diff_detail(text),
            **common,
        }
    if role_value in {"tool_call", "tool_result", "function_call", "function_call_output"} or payload_type in {"function_call", "function_call_output"}:
        return {
            "message_kind": "tool",
            "visual_lane": "trace",
            "detail_label": "tool call/result",
            **common,
        }
    if row_type == "event_msg" and event_type in {"user_message", "agent_message"}:
        return {
            "message_kind": "event",
            "visual_lane": "event",
            "detail_label": "runtime event",
            **common,
        }
    if row_type == "response_item" and role_value in {"assistant", "codex_cli", "codex-cli", "codex_chat_engine", "codex-chat-engine"}:
        return {
            "message_kind": "assistant_reply",
            "visual_lane": "ai",
            "detail_label": "assistant reply",
            **common,
        }
    if row_type == "response_item" and role_value in {"user", "operator"}:
        return {
            "message_kind": "user_message",
            "visual_lane": "user",
            "detail_label": "operator message",
            **common,
        }
    if (
        "wrote " in haystack
        or "updated " in haystack
        or "modified " in haystack
        or "created " in haystack
        or "deleted " in haystack
        or "files changed" in haystack
    ) and ("/" in text or "." in text):
        return {
            "message_kind": "file_edit",
            "visual_lane": "diff",
            "detail_label": "file edit evidence",
            "diff_stats": _diff_detail(text),
            **common,
        }
    if (
        "capsule" in haystack
        or "mini_ref" in haystack
        or "hot_context" in haystack
        or "long_horizon" in haystack
        or "ion/05_context" in haystack
        or "developer_context" in haystack
        or "system" == role_value
    ):
        return {
            "message_kind": "capsule_context",
            "visual_lane": "context",
            "detail_label": "capsule/context",
            "context_refs": _context_refs(text),
            "compaction_markers": _compaction_markers(text, truncated=truncated),
            **common,
        }
    if row_type == "event_msg":
        return {
            "message_kind": "event",
            "visual_lane": "event",
            "detail_label": "runtime event",
            **common,
        }
    if role_value in {"assistant", "codex_cli", "codex-cli", "codex_chat_engine", "codex-chat-engine"}:
        return {
            "message_kind": "assistant_reply",
            "visual_lane": "ai",
            "detail_label": "assistant reply",
            **common,
        }
    if role_value in {"user", "operator"}:
        return {
            "message_kind": "user_message",
            "visual_lane": "user",
            "detail_label": "operator message",
            **common,
        }
    return {
        "message_kind": "non_direct",
        "visual_lane": "event",
        "detail_label": "non-direct transcript item",
        **common,
    }


def _iter_text_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        chunks: list[str] = []
        for child in value.values():
            chunks.extend(_iter_text_values(child))
        return chunks
    if isinstance(value, list):
        chunks = []
        for child in value:
            chunks.extend(_iter_text_values(child))
        return chunks
    return []


def _normalize_signal_text(value: str) -> str:
    return str(value or "").replace("\\n", "\n").replace("\\t", "\t")


def _looks_like_bootstrap_title(value: str) -> bool:
    normalized = _normalize_signal_text(value).strip().lower()
    if not normalized:
        return True
    return any(marker in normalized[:900] for marker in (
        "# agents.md instructions",
        "<instructions>",
        "continuity recovery rule",
        "environment_context",
        "ion codex carrier sync",
        "ion codex mount guard",
        "ion codex operational posture",
        "ion codex response contract",
    ))


def _clean_title(value: Any, *, limit: int = 110) -> str:
    cleaned = _redact(value, limit=limit * 2)
    cleaned = re.sub(r"^#+\s*", "", cleaned).strip()
    cleaned = re.sub(r"(?i)^user\s*:\s*", "", cleaned).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit].rstrip() + "..."


def _display_title(*candidates: Any, session_id: str) -> str:
    cleaned_candidates = [_clean_title(candidate) for candidate in candidates if str(candidate or "").strip()]
    for candidate in cleaned_candidates:
        if not _looks_like_bootstrap_title(candidate):
            return candidate
    for candidate in cleaned_candidates:
        if candidate:
            return candidate
    return session_id


def _project_fields(cwd: Any) -> dict[str, str]:
    value = str(cwd or "").strip()
    if not value:
        return {"project_key": "project_unknown", "project_label": "Project Unknown"}
    parts = [part for part in value.split("/") if part]
    label = "/".join(parts[-2:]) if len(parts) >= 2 else value
    key = _safe_slug(label, limit=96)
    return {"project_key": key, "project_label": label}


def _label(label: str, *, source: str, confidence: str) -> dict[str, str]:
    return {
        "label": _redact(label, limit=96),
        "source": _redact(source, limit=80),
        "confidence": confidence,
    }


def _add_label(labels: dict[str, dict[str, str]], label: str, *, source: str, confidence: str) -> None:
    cleaned = _redact(label, limit=96)
    if not cleaned:
        return
    key = re.sub(r"[^a-z0-9]+", " ", cleaned.lower()).strip()
    if not key:
        return
    strength = {"weak": 0, "inferred": 1, "explicit": 2}
    existing = labels.get(key)
    if existing and strength.get(existing.get("confidence", "weak"), 0) >= strength.get(confidence, 0):
        return
    labels[key] = _label(cleaned, source=source, confidence=confidence)


def _canonical_agent_label(value: str) -> str:
    normalized = value.upper().replace("-", "_")
    if normalized.startswith("PERSONA_INTERFACE"):
        return "PERSONA"
    if normalized.startswith("NEMESIS"):
        return "NEMESIS"
    if normalized == "CODEX_CLI":
        return "CODEX"
    return normalized


def _mission_keyword_labels(value: str) -> list[str]:
    normalized = value.lower()
    labels: list[str] = []
    keyword_map = (
        (("drawer", "past conversation", "sessions", "archive"), "Conversation Navigator"),
        (("codex", "cockpit", "chat"), "Codex Workbench"),
        (("capsule", "context", "memory"), "Context Continuity"),
        (("launcher", "launch"), "Launcher Work"),
        (("cosmos", "earth", "orbit"), "Cosmos Work"),
        (("vnext", "rebuild", "production authority"), "ION vNext"),
        (("extension", "browser", "mcp"), "Browser Carrier"),
    )
    for keywords, label in keyword_map:
        if any(keyword in normalized for keyword in keywords):
            labels.append(label)
    return labels


def _derive_session_intelligence(
    *,
    session_id: str,
    thread_name: Any,
    first_user: Any,
    latest_user: Any,
    cwd: Any,
    model: Any,
    signal_texts: list[str],
    role_counts: Counter[str],
    tool_counts: Counter[str],
    event_counts: Counter[str],
    history_prompt_count: Any,
    line_count: int,
    sampled: bool,
) -> dict[str, Any]:
    project = _project_fields(cwd)
    display_title = _display_title(first_user, latest_user, thread_name, session_id=session_id)
    mission_labels: dict[str, dict[str, str]] = {}
    agent_labels: dict[str, dict[str, str]] = {}

    for raw_text in signal_texts[:300]:
        text = _normalize_signal_text(raw_text)
        for source, pattern in MISSION_FIELD_PATTERNS:
            for match in pattern.findall(text):
                value = str(match).strip().strip('"')
                if value and value not in {"-", "none", "None"}:
                    _add_label(mission_labels, value, source=source, confidence="explicit")
        for field_name, value in FIELD_PATTERN.findall(text):
            cleaned = str(value).strip().strip('"')
            if field_name in {"suggested_skill", "suggested_domain", "carrier", "carrier_identity"}:
                _add_label(agent_labels, cleaned, source=field_name, confidence="explicit")
        if "role_phase_sequence" in text or "visible_role_markers" in text:
            for match in ROLE_PATTERN.findall(text):
                _add_label(agent_labels, _canonical_agent_label(match), source="role_phase_sequence", confidence="explicit")

    for role in role_counts:
        canonical = _canonical_agent_label(str(role))
        if canonical in AGENT_ROLE_NAMES or canonical in {"ASSISTANT", "USER"}:
            continue
        if canonical in {"CUSTOM_TOOL_CALL", "FUNCTION_CALL", "REASONING", "TOOL_SEARCH_CALL", "WEB_SEARCH_CALL"}:
            continue
        _add_label(agent_labels, canonical, source="response_role", confidence="inferred")

    model_text = str(model or "")
    if "codex" in model_text.lower():
        _add_label(agent_labels, "CODEX", source="model", confidence="inferred")
    elif model_text:
        _add_label(agent_labels, model_text, source="model", confidence="weak")

    if tool_counts:
        _add_label(agent_labels, "Tool-Using Codex", source="tool_usage", confidence="inferred")
    for keyword_label in _mission_keyword_labels(" ".join(str(value or "") for value in (display_title, first_user, latest_user, cwd))):
        _add_label(mission_labels, keyword_label, source="prompt_keyword", confidence="weak")

    top_tools = [
        {"name": name, "count": count}
        for name, count in sorted(tool_counts.items(), key=lambda item: (-item[1], item[0]))[:6]
    ]
    activity_score = (
        int(history_prompt_count or 0)
        + line_count
        + sum(event_counts.values())
        + sum(role_counts.values())
        + sum(tool_counts.values())
    )
    session_flags = {
        "line_scan_limited": sampled,
        "raw_transcript_blocked": True,
        "tools_used": bool(tool_counts),
        "has_explicit_mission": any(label["confidence"] == "explicit" for label in mission_labels.values()),
        "has_explicit_agent": any(label["confidence"] == "explicit" for label in agent_labels.values()),
    }
    return {
        "display_title": display_title,
        **project,
        "mission_labels": list(mission_labels.values()),
        "agent_labels": list(agent_labels.values()),
        "tool_summary": top_tools,
        "activity_score": activity_score,
        "session_flags": session_flags,
    }


def _session_summary(path: Path, *, index_meta: Mapping[str, Any], history_meta: Mapping[str, Any]) -> dict[str, Any]:
    event_counts: Counter[str] = Counter()
    role_counts: Counter[str] = Counter()
    tool_counts: Counter[str] = Counter()
    first_user = ""
    latest_user = ""
    latest_assistant = ""
    first_timestamp = None
    last_timestamp = None
    session_id = str(index_meta.get("id") or history_meta.get("session_id") or _session_id_from_path(path))
    cwd = None
    model = None
    line_count = 0
    sampled = False
    signal_texts: list[str] = []
    for line_count, row in enumerate(_read_jsonl(path, limit=SESSION_LINE_SCAN_LIMIT), start=1):
        row_type = str(row.get("type") or "unknown")
        event_counts[row_type] += 1
        timestamp = row.get("timestamp")
        first_timestamp = first_timestamp or timestamp
        last_timestamp = timestamp or last_timestamp
        payload = row.get("payload") if isinstance(row.get("payload"), Mapping) else {}
        for value in _iter_text_values(payload):
            if value and len(signal_texts) < 600:
                signal_texts.append(value)
        if row_type == "session_meta":
            session_id = str(payload.get("id") or session_id)
            cwd = payload.get("cwd") or cwd
        if row_type == "turn_context":
            cwd = payload.get("cwd") or cwd
            model = payload.get("model") or model
        if row_type == "event_msg":
            event_type = str(payload.get("type") or "")
            message = str(payload.get("message") or "")
            if event_type == "user_message" and message:
                latest_user = _redact(message)
                first_user = first_user or latest_user
            elif event_type == "agent_message" and message:
                latest_assistant = _redact(message)
        if row_type == "response_item":
            item = payload
            role = str(item.get("role") or item.get("type") or "unknown")
            role_counts[role] += 1
            if item.get("type") == "function_call" and item.get("name"):
                tool_counts[str(item.get("name"))] += 1
            text = _text_from_response_item(item)
            if role == "user" and text:
                latest_user = _redact(text)
                first_user = first_user or latest_user
            if role == "assistant" and text:
                latest_assistant = _redact(text)
    if line_count >= SESSION_LINE_SCAN_LIMIT:
        sampled = True
    thread_name = index_meta.get("thread_name") or history_meta.get("thread_name") or first_user or session_id
    intelligence = _derive_session_intelligence(
        session_id=session_id,
        thread_name=thread_name,
        first_user=first_user,
        latest_user=latest_user or history_meta.get("latest_prompt_snippet") or "",
        cwd=cwd,
        model=model,
        signal_texts=signal_texts,
        role_counts=role_counts,
        tool_counts=tool_counts,
        event_counts=event_counts,
        history_prompt_count=history_meta.get("prompt_count", 0),
        line_count=line_count,
        sampled=sampled,
    )
    return {
        "schema_id": "ion.codex_conversation_archive_session.v1",
        "session_id": session_id,
        "thread_name": thread_name,
        **intelligence,
        "updated_at": index_meta.get("updated_at") or last_timestamp or _mtime(path),
        "created_at": first_timestamp,
        "session_path": path.as_posix(),
        "cwd": cwd,
        "model": model,
        "bytes": path.stat().st_size if path.is_file() else 0,
        "line_count_sampled": line_count,
        "line_scan_limited": sampled,
        "event_counts": dict(event_counts),
        "role_counts": dict(role_counts),
        "tool_counts": dict(tool_counts),
        "first_user_snippet": first_user,
        "latest_user_snippet": latest_user or history_meta.get("latest_prompt_snippet") or "",
        "latest_assistant_snippet": latest_assistant,
        "history_prompt_count": history_meta.get("prompt_count", 0),
        "history_latest_ts": history_meta.get("latest_ts"),
        "raw_transcript_exported": False,
    }


def _session_excerpt(
    path: Path,
    *,
    limit: int = EXCERPT_LIMIT,
    text_limit: int = 420,
    scan_limit: int | None = SESSION_LINE_SCAN_LIMIT,
    prefer_tail: bool = False,
) -> list[dict[str, Any]]:
    excerpt: list[dict[str, Any]] = []
    for row in _read_jsonl(path, limit=scan_limit):
        row_type = str(row.get("type") or "")
        payload = row.get("payload") if isinstance(row.get("payload"), Mapping) else {}
        role = ""
        text = ""
        if row_type == "event_msg":
            event_type = str(payload.get("type") or "")
            if event_type == "user_message":
                role = "user"
                text = str(payload.get("message") or "")
            elif event_type == "agent_message":
                role = "assistant"
                text = str(payload.get("message") or "")
        elif row_type == "response_item":
            role = str(payload.get("role") or payload.get("type") or "")
            if payload.get("type") == "reasoning" or role == "reasoning":
                continue
            if payload.get("type") == "function_call":
                role = "tool_call"
                text = _function_call_text(payload)
            elif payload.get("type") == "function_call_output":
                role = "tool_result"
                text = _function_output_text(payload)
            else:
                text = _text_from_response_item(payload)
        if role and text:
            safe_text = _redact_transcript_text(text, limit=text_limit)
            truncated = safe_text.endswith("...[MESSAGE_TRUNCATED]")
            item_classification = _classify_transcript_item(
                role=role,
                row_type=row_type,
                payload=payload,
                text=text,
                truncated=truncated,
            )
            excerpt.append({
                "index": len(excerpt) + 1,
                "timestamp": row.get("timestamp"),
                "role": role,
                "source_type": row_type,
                "snippet": _redact(text, limit=420),
                "text": safe_text,
                "truncated": truncated,
                **item_classification,
            })
    if limit > 0 and len(excerpt) > limit:
        return excerpt[-limit:] if prefer_tail else excerpt[:limit]
    return excerpt


def _safe_read_json(path: Path) -> Mapping[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, Mapping) else {}


def _hook_receipt_text(data: Mapping[str, Any], receipt_ref: str) -> str:
    operation = data.get("operation_payload") if isinstance(data.get("operation_payload"), Mapping) else {}
    objective = operation.get("active_objective") if isinstance(operation.get("active_objective"), Mapping) else {}
    precompact_ref = operation.get("precompact_checkpoint_ref") if isinstance(operation.get("precompact_checkpoint_ref"), Mapping) else {}
    lines = [
        f"ION {data.get('event_name') or 'Compaction'} hook receipt",
        f"receipt_ref: {receipt_ref}",
        f"created_at: {data.get('created_at') or ''}",
        f"checkpoint_kind: {operation.get('checkpoint_kind') or operation.get('verification_kind') or ''}",
        f"precompact_checkpoint_found: {operation.get('precompact_checkpoint_found')}" if "precompact_checkpoint_found" in operation else "",
        f"precompact_checkpoint_ref: {precompact_ref.get('receipt_path') or precompact_ref.get('path') or ''}" if precompact_ref else "",
        f"active_mission: {objective.get('mission') or ''}" if objective else "",
        f"active_phase: {objective.get('phase') or ''}" if objective else "",
        f"last_receipt: {objective.get('last_receipt') or ''}" if objective else "",
        f"next_action: {objective.get('next_action') or ''}" if objective else "",
        f"ion_operation_targets: {', '.join(str(item) for item in data.get('ion_operation_targets', []) if item)}" if isinstance(data.get("ion_operation_targets"), list) else "",
        "authority: candidate only; no production, live execution, accepted-state, or secrets authority",
    ]
    return "\n".join(_redact(line, limit=700) for line in lines if str(line or "").strip())


def _hook_receipt_items(root: Path, session_id: str) -> list[dict[str, Any]]:
    if not session_id:
        return []
    base = root / "ION/05_context/current/codex_cli/hooks/runtime"
    items: list[dict[str, Any]] = []
    for event_dir in ("precompact", "postcompact"):
        runtime_dir = base / event_dir
        if not runtime_dir.is_dir():
            continue
        for path in sorted(runtime_dir.glob(f"*_{session_id}_*.json")):
            data = _safe_read_json(path)
            if not data:
                continue
            try:
                receipt_ref = path.relative_to(root).as_posix()
            except ValueError:
                receipt_ref = path.as_posix()
            event_name = str(data.get("event_name") or event_dir).strip() or event_dir
            safe_text = _hook_receipt_text(data, receipt_ref)
            timestamp = str(data.get("created_at") or "")
            markers = [event_name.upper()]
            if event_name.lower() == "postcompact" and "POSTCOMPACT" not in markers:
                markers.append("POSTCOMPACT")
            if event_name.lower() == "precompact" and "PRECOMPACT" not in markers:
                markers.append("PRECOMPACT")
            items.append({
                "index": 0,
                "timestamp": timestamp,
                "role": "compaction",
                "source_type": "hook_receipt",
                "snippet": _redact(safe_text, limit=420),
                "text": safe_text,
                "truncated": False,
                "message_kind": "compaction",
                "visual_lane": "compaction",
                "detail_label": f"{event_name} hook receipt",
                "path_refs": [receipt_ref],
                "context_refs": _context_refs(safe_text),
                "compaction_markers": markers,
                "synthetic": True,
            })
    return items


def _session_excerpt_window(
    path: Path,
    *,
    start_index: int | None = None,
    count: int = SELECTED_TRANSCRIPT_LIMIT,
    text_limit: int = SELECTED_TRANSCRIPT_TEXT_LIMIT,
    hook_items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    all_items = _session_excerpt(
        path,
        limit=0,
        text_limit=text_limit,
        scan_limit=None,
        prefer_tail=False,
    )
    if hook_items:
        all_items.extend(hook_items)
        all_items.sort(key=lambda item: str(item.get("timestamp") or ""))
        for index, item in enumerate(all_items, start=1):
            item["index"] = index
    total = len(all_items)
    safe_count = max(1, min(int(count or SELECTED_TRANSCRIPT_LIMIT), SELECTED_TRANSCRIPT_LIMIT))
    if total == 0:
        return {
            "items": [],
            "total_displayable_items": 0,
            "displayed_item_count": 0,
            "oldest_item_index": None,
            "newest_item_index": None,
            "omitted_older_items": 0,
            "omitted_newer_items": 0,
            "has_older_items": False,
            "has_newer_items": False,
            "window_start_index": None,
            "window_end_index": None,
            "window_count": safe_count,
            "window_mode": "empty",
        }
    if start_index is None:
        start = max(1, total - safe_count + 1)
        mode = "latest_tail" if total > safe_count else "complete_within_limit"
    else:
        requested = max(1, int(start_index))
        start = min(requested, total)
        mode = "bounded_window"
    end = min(total, start + safe_count - 1)
    if end - start + 1 < safe_count and start > 1:
        start = max(1, end - safe_count + 1)
    items = all_items[start - 1:end]
    oldest = int(items[0]["index"]) if items else None
    newest = int(items[-1]["index"]) if items else None
    omitted_older = max(0, (oldest or 1) - 1)
    omitted_newer = max(0, total - (newest or total))
    return {
        "items": items,
        "total_displayable_items": total,
        "displayed_item_count": len(items),
        "oldest_item_index": oldest,
        "newest_item_index": newest,
        "omitted_older_items": omitted_older,
        "omitted_newer_items": omitted_newer,
        "has_older_items": omitted_older > 0,
        "has_newer_items": omitted_newer > 0,
        "window_start_index": oldest,
        "window_end_index": newest,
        "window_count": safe_count,
        "window_mode": mode,
    }


def _session_paths(codex_home: Path) -> list[Path]:
    sessions_root = codex_home / "sessions"
    return sorted(
        (path for path in sessions_root.rglob("*.jsonl") if path.is_file()) if sessions_root.is_dir() else [],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def _session_path_by_id(codex_home: Path, session_id: str) -> Path | None:
    requested = str(session_id or "").strip()
    if not requested:
        return None
    for path in _session_paths(codex_home):
        if _session_id_from_path(path) == requested:
            return path
    return None


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safe_slug(value: Any, *, limit: int = 80) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").lower()).strip("_")[:limit] or "archive"


def _sha256_text(value: str) -> str:
    import hashlib

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _attachment_text(summary: Mapping[str, Any], excerpt: list[Mapping[str, Any]]) -> str:
    lines = [
        "ATTACHED CODEX PAST CHAT",
        "",
        f"session_id: {summary.get('session_id')}",
        f"title: {_redact(summary.get('thread_name'), limit=180)}",
        f"updated_at: {summary.get('updated_at')}",
        f"cwd: {_redact(summary.get('cwd'), limit=240)}",
        f"model: {_redact(summary.get('model'), limit=120)}",
        f"events_sampled: {summary.get('line_count_sampled')}",
        f"history_prompts: {summary.get('history_prompt_count')}",
        "",
        "POLICY:",
        "- This is a redacted context attachment from a previous local Codex session.",
        "- It is active working context for this cockpit chat only after explicit attach.",
        "- Raw transcript, secrets, and private/internal reasoning text are not exported.",
        "- Treat it as historical witness context, not accepted current state.",
        "",
        "REDACTED EXCERPT:",
    ]
    for item in excerpt:
        role = _redact(item.get("role"), limit=40)
        timestamp = _redact(item.get("timestamp"), limit=80)
        snippet = _redact(item.get("snippet"), limit=700)
        lines.append(f"- [{timestamp}] {role}: {snippet}")
    text = "\n".join(lines).strip()
    if len(text) <= ATTACH_TEXT_LIMIT:
        return text
    return text[:ATTACH_TEXT_LIMIT].rstrip() + "\n...[ATTACHMENT_TRUNCATED]"


def _resume_command(session_id: str, *, fork: bool = False, prompt: str | None = None) -> list[str]:
    command = ["codex", "fork" if fork else "resume", session_id]
    if prompt:
        command.append(prompt)
    return command


def _session_search_text(session: Mapping[str, Any]) -> str:
    label_values: list[str] = []
    for key in ("mission_labels", "agent_labels", "tool_summary"):
        values = session.get(key)
        if isinstance(values, list):
            for item in values:
                if isinstance(item, Mapping):
                    label_values.extend(str(item.get(field) or "") for field in ("label", "name", "source", "confidence"))
    fields = [
        "session_id",
        "thread_name",
        "display_title",
        "cwd",
        "project_key",
        "project_label",
        "model",
        "latest_user_snippet",
        "latest_assistant_snippet",
        "first_user_snippet",
    ]
    return " ".join([*(str(session.get(key) or "") for key in fields), *label_values]).lower()


def build_codex_conversation_archive(
    root: str | Path | None = None,
    *,
    session_limit: int = DEFAULT_SESSION_LIMIT,
    selected_session_id: str | None = None,
    query: str | None = None,
    selected_window_start: int | None = None,
    selected_window_count: int = SELECTED_TRANSCRIPT_LIMIT,
) -> dict[str, Any]:
    shell_root = Path(root or ".").expanduser().resolve()
    codex_home = _codex_home()
    history_path = codex_home / "history.jsonl"
    session_index_path = codex_home / "session_index.jsonl"
    index_rows = _read_jsonl(session_index_path)
    history_rows = _read_jsonl(history_path, limit=DEFAULT_HISTORY_LIMIT)
    index_by_id = {str(row.get("id")): row for row in index_rows if row.get("id")}
    history_by_session: dict[str, dict[str, Any]] = {}
    latest_history_row = next((row for row in reversed(history_rows) if row.get("session_id")), {})
    current_session_id = str(latest_history_row.get("session_id") or "")
    for row in history_rows:
        session_id = str(row.get("session_id") or "")
        if not session_id:
            continue
        meta = history_by_session.setdefault(session_id, {"session_id": session_id, "prompt_count": 0})
        meta["prompt_count"] = int(meta.get("prompt_count") or 0) + 1
        meta["latest_ts"] = row.get("ts") or meta.get("latest_ts")
        if row.get("text"):
            meta["latest_prompt_snippet"] = _redact(row.get("text"))
    sessions_root = codex_home / "sessions"
    paths = _session_paths(codex_home)
    sessions = []
    selected_path = None
    for path in paths[: max(1, session_limit)]:
        path_session_id = _session_id_from_path(path)
        meta = index_by_id.get(path_session_id, {})
        history_meta = history_by_session.get(path_session_id, {"session_id": path_session_id})
        summary = _session_summary(path, index_meta=meta, history_meta=history_meta)
        summary["is_current_session"] = bool(current_session_id and summary["session_id"] == current_session_id)
        if isinstance(summary.get("session_flags"), dict):
            summary["session_flags"]["current_session"] = bool(summary["is_current_session"])
        if selected_session_id and summary["session_id"] == selected_session_id:
            selected_path = path
        sessions.append(summary)
    normalized_query = (query or "").strip().lower()
    if normalized_query:
        sessions = [
            session for session in sessions
            if normalized_query in _session_search_text(session)
        ]
    selected_excerpt = None
    if selected_session_id:
        if selected_path is None:
            for path in paths:
                if _session_id_from_path(path) == selected_session_id:
                    selected_path = path
                    break
        transcript_window = _session_excerpt_window(
            selected_path,
            start_index=selected_window_start,
            count=selected_window_count,
            text_limit=SELECTED_TRANSCRIPT_TEXT_LIMIT,
            hook_items=_hook_receipt_items(shell_root, selected_session_id),
        ) if selected_path is not None else {
            "items": [],
            "total_displayable_items": 0,
            "displayed_item_count": 0,
            "oldest_item_index": None,
            "newest_item_index": None,
            "omitted_older_items": 0,
            "omitted_newer_items": 0,
            "has_older_items": False,
            "has_newer_items": False,
            "window_start_index": None,
            "window_end_index": None,
            "window_count": selected_window_count,
            "window_mode": "not_found",
        }
        transcript_items = transcript_window["items"]
        line_count = len(_read_jsonl(selected_path, limit=None)) if selected_path is not None else 0
        total_displayable_items = int(transcript_window["total_displayable_items"])
        displayed_item_count = len(transcript_items)
        omitted_older_items = int(transcript_window["omitted_older_items"])
        omitted_newer_items = int(transcript_window["omitted_newer_items"])
        window_mode = str(transcript_window["window_mode"])
        if not omitted_older_items and not omitted_newer_items:
            display_mode = "safe_redacted_full_transcript"
        elif window_mode == "latest_tail":
            display_mode = "safe_redacted_latest_transcript_window"
        else:
            display_mode = "safe_redacted_transcript_window"
        selected_excerpt = {
            "session_id": selected_session_id,
            "is_current_session": bool(current_session_id and selected_session_id == current_session_id),
            "found": selected_path is not None,
            "raw_transcript_exported": False,
            "hidden_reasoning_exposed": False,
            "safe_transcript_exported": True,
            "display_mode": display_mode,
            "window_mode": window_mode,
            "policy": "safe redacted transcript window; private/internal reasoning text and secrets are not exported",
            "session_path": selected_path.as_posix() if selected_path is not None else None,
            "line_scan_limit": None,
            "line_scan_limited": False,
            "excerpt_limit": int(transcript_window["window_count"]),
            "item_count": displayed_item_count,
            "displayed_item_count": displayed_item_count,
            "total_displayable_items": total_displayable_items,
            "omitted_older_items": omitted_older_items,
            "omitted_newer_items": omitted_newer_items,
            "has_older_items": bool(transcript_window["has_older_items"]),
            "has_newer_items": bool(transcript_window["has_newer_items"]),
            "oldest_item_index": transcript_window["oldest_item_index"],
            "newest_item_index": transcript_window["newest_item_index"],
            "window_start_index": transcript_window["window_start_index"],
            "window_end_index": transcript_window["window_end_index"],
            "window_count": int(transcript_window["window_count"]),
            "line_count": line_count,
            "items": transcript_items,
        }
    return {
        "schema_id": SCHEMA_ID,
        "verdict": READY_VERDICT if codex_home.exists() else DEGRADED_VERDICT,
        "generated_at": _now(),
        "codex_home": codex_home.as_posix(),
        "sources": {
            "history_path": history_path.as_posix(),
            "session_index_path": session_index_path.as_posix(),
            "sessions_root": sessions_root.as_posix(),
        },
        "source_counts": {
            "history_rows_sampled": len(history_rows),
            "session_index_rows": len(index_rows),
            "session_files_total": len(paths),
            "session_files_returned": len(sessions),
        },
        "current_session_id": current_session_id,
        "current_prompt_ts": latest_history_row.get("ts"),
        "current_prompt_snippet": _redact(latest_history_row.get("text")) if latest_history_row else "",
        "sessions": sessions,
        "selected_session_excerpt": selected_excerpt,
        "query": query or "",
        "session_limit": session_limit,
        "raw_content_exported": False,
        "raw_transcript_exported": False,
        "hidden_reasoning_exposed": False,
        "secrets_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "policy": "safe_index_and_selected_redacted_transcript_only; raw Codex transcripts, secrets, and private/internal reasoning text are not exported",
    }


def attach_codex_conversation_to_chat(
    root: str | Path | None = None,
    *,
    session_id: str,
    confirmation: str,
    prompt: str | None = None,
) -> dict[str, Any]:
    if confirmation != WRITE_CONFIRMATION_TOKEN:
        return {"ok": False, "finding": "bounded_write_confirmation_required", "required_confirmation": WRITE_CONFIRMATION_TOKEN}
    requested = str(session_id or "").strip()
    if not requested:
        return {"ok": False, "finding": "session_id_required"}
    shell_root = Path(root or ".").expanduser().resolve()
    codex_home = _codex_home()
    path = _session_path_by_id(codex_home, requested)
    if path is None:
        return {"ok": False, "finding": "session_not_found", "session_id": requested}

    session_index_path = codex_home / "session_index.jsonl"
    history_path = codex_home / "history.jsonl"
    index_by_id = {str(row.get("id")): row for row in _read_jsonl(session_index_path) if row.get("id")}
    history_meta: dict[str, Any] = {"session_id": requested, "prompt_count": 0}
    for row in _read_jsonl(history_path, limit=DEFAULT_HISTORY_LIMIT):
        if str(row.get("session_id") or "") != requested:
            continue
        history_meta["prompt_count"] = int(history_meta.get("prompt_count") or 0) + 1
        history_meta["latest_ts"] = row.get("ts") or history_meta.get("latest_ts")
        if row.get("text"):
            history_meta["latest_prompt_snippet"] = _redact(row.get("text"))
    summary = _session_summary(path, index_meta=index_by_id.get(requested, {}), history_meta=history_meta)
    excerpt = _session_excerpt(path, limit=ATTACH_EXCERPT_LIMIT)
    attachment_text = _attachment_text(summary, excerpt)
    now = _now()
    attach_id = f"archive_attach_{_stamp()}_{_safe_slug(requested, limit=36)}"
    packet = {
        "schema_id": "ion.codex_conversation_archive_attachment.v1",
        "attachment_id": attach_id,
        "created_at": now,
        "session_id": summary.get("session_id"),
        "thread_name": summary.get("thread_name"),
        "source_session_path": summary.get("session_path"),
        "cwd": summary.get("cwd"),
        "model": summary.get("model"),
        "updated_at": summary.get("updated_at"),
        "excerpt_limit": ATTACH_EXCERPT_LIMIT,
        "excerpt_count": len(excerpt),
        "attachment_text": attachment_text,
        "attachment_sha256": _sha256_text(attachment_text),
        "raw_transcript_exported": False,
        "hidden_reasoning_exposed": False,
        "secrets_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "state_acceptance_granted": False,
        "policy": "explicit_redacted_archive_attachment_for_active_codex_cockpit_chat",
        "codex_resume": {
            "command": _resume_command(str(summary.get("session_id") or requested), prompt=prompt),
            "command_text": " ".join(_resume_command(str(summary.get("session_id") or requested), prompt=prompt)),
            "interactive_terminal_required": True,
            "cockpit_spawned_process": False,
        },
        "codex_fork": {
            "command": _resume_command(str(summary.get("session_id") or requested), fork=True, prompt=prompt),
            "command_text": " ".join(_resume_command(str(summary.get("session_id") or requested), fork=True, prompt=prompt)),
            "interactive_terminal_required": True,
            "cockpit_spawned_process": False,
        },
    }
    out_path = shell_root / ATTACHMENTS_DIR / f"{attach_id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    packet["packet_path"] = out_path.relative_to(shell_root).as_posix()

    from .ion_dual_codex_chat import build_dual_codex_chat_model, load_dual_chat_state, save_dual_chat_state

    state = load_dual_chat_state(shell_root)
    state.setdefault("memory", {}).setdefault("archive_attachments", [])
    attachment_record = {
        "attachment_id": attach_id,
        "session_id": packet["session_id"],
        "thread_name": packet["thread_name"],
        "packet_path": packet["packet_path"],
        "created_at": now,
        "status": "active",
        "scope": "active_codex_cockpit_chat",
        "raw_transcript_exported": False,
        "production_authority": False,
        "live_execution_authority": False,
    }
    state["memory"]["archive_attachments"].append(attachment_record)
    state.setdefault("lanes", {}).setdefault("codex_general", {}).setdefault("turns", []).append({
        "turn_id": f"attach_{now.replace(':', '').replace('+', 'Z')}_{_safe_slug(requested)}",
        "lane_id": "codex_general",
        "author": "codex_archive",
        "kind": "archive_attachment",
        "message": attachment_text,
        "message_sha256": packet["attachment_sha256"],
        "created_at": now,
        "attachment_id": attach_id,
        "session_id": packet["session_id"],
        "packet_path": packet["packet_path"],
        "production_authority": False,
        "live_execution_authority": False,
    })
    save_dual_chat_state(shell_root, state)
    model = build_dual_codex_chat_model(shell_root, write=True)
    return {
        "ok": True,
        "attachment": attachment_record,
        "packet": packet,
        "model": model,
        "production_authority": False,
        "live_execution_authority": False,
    }
