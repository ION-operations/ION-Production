"""Filesystem-first ION agent communication substrate.

This is the cockpit-facing projection of the lawful ION communication model:
agent-private continuity remains source truth, while team communication moves
through durable packets, channels, inbox/outbox refs, signals, and projections.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

SCHEMA_ID = "ion.agent_comms.v1"
PROJECTION_SCHEMA_ID = "ion.agent_comms.projection.v1"
THREAD_SCHEMA_ID = "ion.agent_comms.thread.v1"
MESSAGE_SCHEMA_ID = "ion.agent_comms.message.v1"
ACK_SCHEMA_ID = "ion.agent_comms.ack.v1"
WORK_PANEL_SCHEMA_ID = "ion.agent_comms.work_panel.v1"
MENTION_SCHEMA_ID = "ion.agent_comms.mentions.v1"
ROOM_CAPSULE_SCHEMA_ID = "ion.agent_comms.room_capsule.v1"

AGENT_COMMS_ROOT = Path("ION/05_context/current/agent_comms")

DEFAULT_CHANNELS: tuple[dict[str, Any], ...] = (
    {
        "channel_id": "front_door",
        "label": "Front Door",
        "kind": "operator_persona_relay",
        "purpose": "Operator -> Persona -> Relay intake and user-facing return packets.",
        "default_participants": ["operator", "role.persona_interface", "role.relay"],
        "order": 10,
    },
    {
        "channel_id": "relay",
        "label": "Relay",
        "kind": "semantic_boundary",
        "purpose": "Relay packetization, inbound digest, outbound courier, and controlled re-expression.",
        "default_participants": ["role.relay", "role.steward", "operator"],
        "order": 20,
    },
    {
        "channel_id": "steward_ops",
        "label": "Steward Ops",
        "kind": "orchestration",
        "purpose": "Steward routing, support-role activation, dependency waits, and proof review.",
        "default_participants": ["role.steward", "role.relay"],
        "order": 30,
    },
    {
        "channel_id": "team",
        "label": "Team",
        "kind": "roundtable",
        "purpose": "Visible team coordination across active ION roles.",
        "default_participants": ["role.steward", "role.mason", "role.ionologist", "role.codex_carrier_steward"],
        "order": 40,
    },
    {
        "channel_id": "handoffs",
        "label": "Handoffs",
        "kind": "handoff",
        "purpose": "Role-to-role handoff packets with exact refs, blockers, and requested next action.",
        "default_participants": ["role.steward"],
        "order": 50,
    },
    {
        "channel_id": "signals",
        "label": "Signals",
        "kind": "signal_bus",
        "purpose": "Completion, blocker, ready, dissent, and audit signals that point to source artifacts.",
        "default_participants": ["role.steward", "role.nemesis"],
        "order": 60,
    },
    {
        "channel_id": "gates",
        "label": "Gates",
        "kind": "approval",
        "purpose": "Human gates, authority-expansion requests, release blockers, and settlement decisions.",
        "default_participants": ["operator", "role.steward", "role.nemesis"],
        "order": 70,
    },
    {
        "channel_id": "audit",
        "label": "Audit",
        "kind": "audit",
        "purpose": "Nemesis, Vice, diagnostics, drift, and release-risk evidence.",
        "default_participants": ["role.nemesis", "role.vice", "role.steward"],
        "order": 80,
    },
)

KNOWN_ROLE_ALIASES = {
    "agent.codex": "role.codex",
    "codex": "role.codex",
    "codex_carrier_steward": "role.codex_carrier_steward",
    "comms_cartographer": "role.comms_cartographer",
    "ionologist": "role.ionologist",
    "mason": "role.mason",
    "nemesis": "role.nemesis",
    "operator": "operator",
    "persona": "role.persona_interface",
    "persona_interface": "role.persona_interface",
    "relay": "role.relay",
    "steward": "role.steward",
    "system": "system",
    "vice": "role.vice",
    "vizier": "role.vizier",
}

MESSAGE_KINDS = {
    "operator_intent",
    "relay_packet",
    "task_dispatch",
    "handoff",
    "question",
    "answer",
    "signal",
    "audit",
    "status",
    "digest",
    "receipt",
    "blocker",
    "decision_request",
    "thread_note",
}

TERMINAL_MESSAGE_STATUSES = {"answered", "blocked", "settled", "archived"}
MENTION_RE = re.compile(r"(?<![\w/])@([A-Za-z][A-Za-z0-9_.-]{0,127})")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ%f")


def _slug(value: Any, fallback: str = "item") -> str:
    text = str(value or "").strip().lower()
    slug = re.sub(r"[^a-z0-9._-]+", "_", text).strip("._-")
    return slug[:96] or fallback


def normalize_role_id(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    lowered = raw.lower().replace(" ", "_")
    if lowered in KNOWN_ROLE_ALIASES:
        return KNOWN_ROLE_ALIASES[lowered]
    if lowered.startswith("role."):
        return lowered
    if lowered in {"all", "broadcast", "*"}:
        return "broadcast"
    return lowered


def _root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    return candidate


def _comms_root(root: Path) -> Path:
    return root / AGENT_COMMS_ROOT


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _safe_repo_path(root: Path, rel_path: str) -> Path | None:
    value = Path(rel_path)
    if value.is_absolute() or ".." in value.parts:
        return None
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _append_jsonl(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def _coerce_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in re.split(r"[\n,]", value) if item.strip()]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray, str)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _role_slug(role_id: str) -> str:
    return _slug(role_id.replace("role.", "role_"), "role")


def _mention_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9.]+", "_", str(value or "").strip().lower().lstrip("@")).strip("._")


def _agent_aliases(role_id: str, display_name: Any = "") -> list[str]:
    role = normalize_role_id(role_id)
    aliases = [role, role.replace("role.", "", 1), role.replace(".", "_")]
    display = str(display_name or "").strip()
    if display:
        aliases.extend([display, display.replace(" ", "_"), re.sub(r"[^A-Za-z0-9]+", "_", display)])
    return [_mention_key(alias) for alias in aliases if _mention_key(alias)]


def _mention_alias_map(root: Path) -> dict[str, str]:
    aliases = {_mention_key(alias): normalize_role_id(role) for alias, role in KNOWN_ROLE_ALIASES.items()}
    directory = _read_json(root / AGENT_COMMS_ROOT / "COMMUNICATION_DIRECTORY.json")
    agents_by_role = directory.get("agents_by_role") if isinstance(directory.get("agents_by_role"), Mapping) else {}
    for role_id, agent in agents_by_role.items():
        if not isinstance(agent, Mapping):
            continue
        role = normalize_role_id(agent.get("role_id") or role_id)
        if not role:
            continue
        for alias in _agent_aliases(role, agent.get("display_name")):
            aliases.setdefault(alias, role)
    return aliases


def extract_agent_mentions(root: str | Path | None, text_value: str) -> dict[str, Any]:
    shell_root = _root(root)
    aliases = _mention_alias_map(shell_root)
    records: list[dict[str, Any]] = []
    roles: list[str] = []
    unresolved: list[str] = []
    seen_tokens: set[str] = set()
    seen_roles: set[str] = set()
    for match in MENTION_RE.finditer(text_value or ""):
        raw_token = match.group(0).rstrip(".,;:!?")
        key = _mention_key(match.group(1).rstrip(".,;:!?"))
        if not key or raw_token in seen_tokens:
            continue
        seen_tokens.add(raw_token)
        role = aliases.get(key) or normalize_role_id(key)
        if role and (role.startswith("role.") or role in {"operator", "system", "broadcast"}):
            records.append({"token": raw_token, "alias": key, "role_id": role, "resolved": True})
            if role not in {"broadcast"} and role not in seen_roles:
                seen_roles.add(role)
                roles.append(role)
        else:
            records.append({"token": raw_token, "alias": key, "role_id": "", "resolved": False})
            unresolved.append(raw_token)
    return {
        "schema_id": MENTION_SCHEMA_ID,
        "mention_count": len(records),
        "resolved_count": len(roles),
        "mentions": records,
        "roles": roles,
        "unresolved": unresolved,
        "production_authority": False,
        "live_execution_authority": False,
    }


def default_agent_channels() -> list[dict[str, Any]]:
    return [
        {
            **channel,
            "schema_id": "ion.agent_comms.channel.v1",
            "source": "ION/AIMOS/Victus filesystem-first comms synthesis",
            "production_authority": False,
            "live_execution_authority": False,
        }
        for channel in DEFAULT_CHANNELS
    ]


def _channel_by_id(channel_id: str) -> dict[str, Any]:
    normalized = _slug(channel_id, "team")
    for channel in default_agent_channels():
        if channel["channel_id"] == normalized:
            return channel
    return {
        "schema_id": "ion.agent_comms.channel.v1",
        "channel_id": normalized,
        "label": normalized.replace("_", " ").title(),
        "kind": "custom",
        "purpose": "Operator-created or imported communication channel.",
        "default_participants": [],
        "order": 999,
        "source": "operator_or_runtime",
        "production_authority": False,
        "live_execution_authority": False,
    }


def _message_kind(value: Any) -> str:
    kind = _slug(value or "thread_note", "thread_note")
    return kind if kind in MESSAGE_KINDS else "thread_note"


def _default_channel_for_kind(kind: str, to_roles: list[str]) -> str:
    if kind == "operator_intent":
        return "front_door"
    if kind in {"relay_packet", "digest"}:
        return "relay"
    if kind in {"task_dispatch", "decision_request"}:
        return "steward_ops"
    if kind == "handoff":
        return "handoffs"
    if kind == "signal":
        return "signals"
    if kind in {"audit", "blocker"}:
        return "audit"
    if "operator" in to_roles:
        return "gates"
    return "team"


def _room_channel_id(room_kind: str, room_id: str, channel_id: str, participants: Sequence[str]) -> str:
    if channel_id:
        return _slug(channel_id, "team")
    if room_kind == "direct":
        roles = sorted(_slug(role.replace("role.", "role_"), "role") for role in participants if role and role != "broadcast")
        return _slug(f"dm_{'_'.join(roles[:4])}", "direct")
    if room_kind == "domain" and room_id.startswith("room.domain."):
        return _slug(room_id.removeprefix("room."), "domain")
    if room_kind == "mission" and room_id.startswith("room.mission."):
        return _slug(room_id.removeprefix("room."), "mission")
    return "team"


def _infer_room_kind(data: Mapping[str, Any], *, kind: str, channel_id: str) -> str:
    requested = _slug(data.get("room_kind") or data.get("room_type") or "", "")
    if requested in {"main", "mission", "domain", "direct", "audit", "handoff", "incident"}:
        return requested
    visibility = _slug(data.get("visibility") or "", "")
    if visibility in {"direct", "direct_chat", "private_agent_pair"}:
        return "direct"
    if data.get("domain_id"):
        return "domain"
    if channel_id in {"audit", "gates"} or kind in {"audit", "blocker"}:
        return "audit"
    if channel_id == "handoffs" or kind == "handoff":
        return "handoff"
    if kind == "blocker" and channel_id == "steward_ops":
        return "incident"
    if data.get("mission") or channel_id.startswith("mission"):
        return "mission"
    return "main"


def _default_room_id(data: Mapping[str, Any], *, room_kind: str, channel_id: str, participants: Sequence[str]) -> str:
    explicit = str(data.get("room_id") or "").strip()
    if explicit:
        return _slug(explicit, "room")
    domain_id = str(data.get("domain_id") or "").strip()
    if room_kind == "domain" and domain_id:
        return _slug(f"room.domain.{domain_id}", "room_domain")
    mission = str(data.get("mission") or data.get("mission_id") or data.get("run_id") or "").strip()
    if room_kind == "mission" and mission:
        return _slug(f"room.mission.{mission}", "room_mission")
    if room_kind == "direct":
        roles = sorted(_slug(role.replace("role.", "role_"), "role") for role in participants if role and role != "broadcast")
        return _slug(f"room.direct.{'.'.join(roles[:4])}", "room_direct")
    if room_kind == "audit":
        return "room.audit"
    if room_kind == "handoff":
        return "room.handoff"
    if room_kind == "incident":
        return _slug(f"room.incident.{data.get('mission') or data.get('subject') or channel_id}", "room_incident")
    if channel_id == "team":
        return "room.main.team"
    return _slug(f"room.channel.{channel_id}", "room_channel")


def _default_report_to_room(room_kind: str, data: Mapping[str, Any]) -> str:
    explicit = str(data.get("report_to_room_id") or data.get("report_room_id") or "").strip()
    if explicit:
        return _slug(explicit, "room")
    if room_kind in {"domain", "direct", "audit", "handoff", "incident"}:
        return "room.main.team"
    return ""


def _thread_path(comms: Path, thread_id: str) -> Path:
    return comms / "threads" / _slug(thread_id, "thread") / "THREAD.json"


def _messages_dir(comms: Path, thread_id: str) -> Path:
    return comms / "threads" / _slug(thread_id, "thread") / "messages"


def _message_index_path(comms: Path) -> Path:
    return comms / "projections" / "MESSAGE_INDEX.json"


def _load_message_index(comms: Path) -> dict[str, Any]:
    value = _read_json(_message_index_path(comms))
    if not value:
        return {
            "schema_id": "ion.agent_comms.message_index.v1",
            "updated_at": _now(),
            "messages": {},
            "production_authority": False,
            "live_execution_authority": False,
        }
    value.setdefault("messages", {})
    return value


def _save_message_index(comms: Path, index: Mapping[str, Any]) -> None:
    value = dict(index)
    value["updated_at"] = _now()
    _write_json(_message_index_path(comms), value)


def _load_thread(comms: Path, thread_id: str) -> dict[str, Any]:
    return _read_json(_thread_path(comms, thread_id))


def _write_thread(comms: Path, thread: Mapping[str, Any]) -> Path:
    path = _thread_path(comms, str(thread.get("thread_id") or "thread"))
    _write_json(path, thread)
    return path


def _message_file(comms: Path, thread_id: str, message_id: str, created_at: str) -> Path:
    created_slug = re.sub(r"[^0-9TZ]", "", created_at)[:32] or _timestamp_slug()
    return _messages_dir(comms, thread_id) / f"{created_slug}_{_slug(message_id, 'msg')}.json"


def _message_participants(from_role: str, to_roles: list[str], cc_roles: list[str]) -> list[str]:
    participants = [from_role, *to_roles, *cc_roles]
    seen: set[str] = set()
    unique: list[str] = []
    for role in participants:
        normalized = normalize_role_id(role)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique.append(normalized)
    return unique


def _message_summary(body: str, fallback: str = "") -> str:
    summary = " ".join(str(body or "").split())
    return (summary[:157] + "...") if len(summary) > 160 else (summary or fallback)


def _safe_message_payload(message: Mapping[str, Any]) -> dict[str, Any]:
    safe = dict(message)
    safe.pop("body", None)
    return safe


def _tab(tab_id: str, label: str, records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "tab_id": tab_id,
        "label": label,
        "count": len(records),
        "records": [dict(item) for item in records],
    }


def _message_ref_records(label: str, values: Sequence[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, value in enumerate(values, start=1):
        text_value = str(value or "").strip()
        if not text_value:
            continue
        rows.append(
            {
                "title": f"{label} {index}",
                "detail": text_value,
                "kind": label,
            }
        )
    return rows


def _room_capsule_file(comms: Path, room_id: str) -> Path:
    return comms / "rooms" / _slug(room_id, "room") / "ROOM_CAPSULE.json"


def _write_room_capsule(
    root: Path,
    comms: Path,
    *,
    message: Mapping[str, Any],
    thread: Mapping[str, Any],
    message_path: Path,
    thread_path: Path,
) -> str:
    room_id = str(message.get("room_id") or thread.get("room_id") or "room.main.team")
    capsule_path = _room_capsule_file(comms, room_id)
    existing = _read_json(capsule_path)
    thread_ids = list(existing.get("thread_ids") or [])
    thread_id = str(thread.get("thread_id") or "")
    if thread_id and thread_id not in thread_ids:
        thread_ids.append(thread_id)
    participants = sorted(
        {
            normalize_role_id(role)
            for role in [
                *list(existing.get("participants") or []),
                *list(thread.get("participants") or []),
                *list(message.get("participants") or []),
            ]
            if normalize_role_id(role)
        }
    )
    source_refs = sorted({*list(existing.get("source_refs") or []), *list(message.get("source_refs") or []), *list(thread.get("source_refs") or [])})
    artifact_refs = sorted(
        {*list(existing.get("artifact_refs") or []), *list(message.get("artifact_refs") or []), *list(thread.get("artifact_refs") or [])}
    )
    capsule = {
        "schema_id": ROOM_CAPSULE_SCHEMA_ID,
        "room_id": room_id,
        "room_kind": message.get("room_kind") or thread.get("room_kind") or "main",
        "channel_id": message.get("channel_id") or thread.get("channel_id"),
        "report_to_room_id": message.get("report_to_room_id") or thread.get("report_to_room_id") or "",
        "visibility": message.get("visibility") or thread.get("visibility") or "team_projection",
        "summary_required": bool(message.get("summary_required") or thread.get("summary_required")),
        "thread_ids": thread_ids[-25:],
        "thread_count": len(thread_ids),
        "latest_thread_id": thread_id,
        "latest_message_id": message.get("message_id"),
        "latest_summary": message.get("summary"),
        "participants": participants,
        "source_refs": source_refs[-50:],
        "artifact_refs": artifact_refs[-50:],
        "route_deeper_refs": {
            "thread_path": _rel(thread_path, root),
            "message_path": _rel(message_path, root),
            "message_index_path": (AGENT_COMMS_ROOT / "projections/MESSAGE_INDEX.json").as_posix(),
        },
        "room_contract_ref": (AGENT_COMMS_ROOT / "COMMUNICATION_DIRECTORY.json").as_posix() + "#room_contract",
        "updated_at": _now(),
        "policy": "Read this room capsule first; open route_deeper_refs only when the room state or task requires transcript-level evidence.",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }
    _write_json(capsule_path, capsule)
    return _rel(capsule_path, root)


def _recent_room_capsules(root: Path, comms: Path, *, limit: int = 100) -> list[dict[str, Any]]:
    rooms_root = comms / "rooms"
    if not rooms_root.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(rooms_root.glob("*/ROOM_CAPSULE.json"), key=lambda item: item.stat().st_mtime, reverse=True)[:limit]:
        payload = _read_json(path)
        if not payload:
            continue
        row = dict(payload)
        row["path"] = _rel(path, root)
        rows.append(row)
    return rows


def _room_projection(
    root: Path,
    comms: Path,
    threads: Sequence[Mapping[str, Any]],
    *,
    limit: int = 100,
) -> dict[str, Any]:
    capsules = _recent_room_capsules(root, comms, limit=limit)
    rooms_by_id: dict[str, dict[str, Any]] = {}
    for capsule in capsules:
        room_id = str(capsule.get("room_id") or "").strip()
        if not room_id:
            continue
        rooms_by_id[room_id] = {
            "room_id": room_id,
            "room_kind": str(capsule.get("room_kind") or "main"),
            "channel_id": str(capsule.get("channel_id") or ""),
            "report_to_room_id": str(capsule.get("report_to_room_id") or ""),
            "visibility": str(capsule.get("visibility") or "team_projection"),
            "summary_required": bool(capsule.get("summary_required")),
            "thread_ids": list(capsule.get("thread_ids") or []),
            "thread_count": int(capsule.get("thread_count") or len(list(capsule.get("thread_ids") or []))),
            "latest_thread_id": str(capsule.get("latest_thread_id") or ""),
            "latest_message_id": str(capsule.get("latest_message_id") or ""),
            "latest_summary": str(capsule.get("latest_summary") or ""),
            "participants": list(capsule.get("participants") or []),
            "source_refs": list(capsule.get("source_refs") or []),
            "artifact_refs": list(capsule.get("artifact_refs") or []),
            "route_deeper_refs": dict(capsule.get("route_deeper_refs") or {}),
            "room_capsule_path": str(capsule.get("path") or ""),
            "updated_at": str(capsule.get("updated_at") or ""),
        }
    for thread in threads:
        room_id = str(thread.get("room_id") or "").strip()
        if not room_id:
            continue
        room = rooms_by_id.setdefault(
            room_id,
            {
                "room_id": room_id,
                "room_kind": str(thread.get("room_kind") or "main"),
                "channel_id": str(thread.get("channel_id") or ""),
                "report_to_room_id": str(thread.get("report_to_room_id") or ""),
                "visibility": str(thread.get("visibility") or "team_projection"),
                "summary_required": bool(thread.get("summary_required")),
                "thread_ids": [],
                "thread_count": 0,
                "latest_thread_id": "",
                "latest_message_id": "",
                "latest_summary": "",
                "participants": [],
                "source_refs": [],
                "artifact_refs": [],
                "route_deeper_refs": {},
                "room_capsule_path": str(thread.get("room_capsule_path") or ""),
                "updated_at": "",
            },
        )
        thread_id = str(thread.get("thread_id") or "")
        if thread_id and thread_id not in room["thread_ids"]:
            room["thread_ids"].append(thread_id)
        room["thread_count"] = max(int(room.get("thread_count") or 0), len(list(room.get("thread_ids") or [])))
        if str(thread.get("updated_at") or "") >= str(room.get("updated_at") or ""):
            room["latest_thread_id"] = thread_id
            room["latest_message_id"] = str(thread.get("latest_message_id") or room.get("latest_message_id") or "")
            room["latest_summary"] = str(thread.get("latest_summary") or room.get("latest_summary") or "")
            room["updated_at"] = str(thread.get("updated_at") or "")
        participants = sorted({*list(room.get("participants") or []), *list(thread.get("participants") or [])})
        room["participants"] = participants
    rooms = sorted(rooms_by_id.values(), key=lambda row: str(row.get("updated_at") or ""), reverse=True)
    room_kind_counts: dict[str, int] = {}
    for room in rooms:
        kind = str(room.get("room_kind") or "main")
        room_kind_counts[kind] = room_kind_counts.get(kind, 0) + 1
    return {
        "schema_id": "ion.agent_comms.rooms.projection.v1",
        "room_count": len(rooms),
        "room_kind_counts": dict(sorted(room_kind_counts.items())),
        "rooms": rooms[:limit],
        "capsule_count": len(capsules),
        "capsule_root": (AGENT_COMMS_ROOT / "rooms").as_posix(),
        "policy": "Rooms organize visible comms; room capsules are compact context entry points with route-deeper refs.",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def _build_message_work_panel(
    root: Path,
    message: Mapping[str, Any],
    thread: Mapping[str, Any],
    *,
    child_messages: Sequence[Mapping[str, Any]] = (),
    branch_threads: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    body = str(message.get("body") or message.get("summary") or "")
    message_id = str(message.get("message_id") or "")
    thread_id = str(message.get("thread_id") or "")
    parent_message_id = str(message.get("parent_message_id") or "")
    child_ids = [str(item.get("message_id") or "") for item in child_messages if item.get("message_id")]
    branch_thread_ids = [str(item.get("thread_id") or "") for item in branch_threads if item.get("thread_id")]
    route_records = [
        {
            "title": "room",
            "detail": str(message.get("room_id") or thread.get("room_id") or ""),
            "kind": "room_id",
        },
        {
            "title": "room kind",
            "detail": str(message.get("room_kind") or thread.get("room_kind") or ""),
            "kind": "room_kind",
        },
        {
            "title": "from",
            "detail": str(message.get("from_role") or ""),
            "kind": "from_role",
        },
        {
            "title": "to",
            "detail": ", ".join(str(item) for item in list(message.get("to_roles") or [])) or "none",
            "kind": "to_roles",
        },
        {
            "title": "status",
            "detail": str(message.get("status") or ""),
            "kind": "status",
        },
        {
            "title": "policy",
            "detail": str(message.get("routing_policy") or ""),
            "kind": "routing_policy",
        },
        {
            "title": "authority",
            "detail": str(message.get("authority_boundary") or ""),
            "kind": "authority_boundary",
        },
        {
            "title": "report to",
            "detail": str(message.get("report_to_room_id") or thread.get("report_to_room_id") or "none"),
            "kind": "report_to_room_id",
        },
    ]
    context_records = [
        *_message_ref_records("source_ref", list(message.get("source_refs") or [])),
        *_message_ref_records("artifact_ref", list(message.get("artifact_refs") or [])),
        *_message_ref_records("receipt_ref", list(message.get("receipt_refs") or [])),
    ]
    if message.get("path"):
        context_records.append({"title": "message_path", "detail": str(message.get("path")), "kind": "message_path"})
    if thread.get("path"):
        context_records.append({"title": "thread_path", "detail": str(thread.get("path")), "kind": "thread_path"})
    if message.get("room_capsule_path") or thread.get("room_capsule_path"):
        context_records.append(
            {
                "title": "room_capsule",
                "detail": str(message.get("room_capsule_path") or thread.get("room_capsule_path")),
                "kind": "room_capsule",
            }
        )
    branch_records: list[dict[str, Any]] = []
    if parent_message_id:
        branch_records.append(
            {
                "title": "parent message",
                "detail": parent_message_id,
                "kind": "parent_message",
                "message_id": parent_message_id,
            }
        )
    for child in child_messages:
        branch_records.append(
            {
                "title": str(child.get("subject") or "child message"),
                "detail": str(child.get("summary") or child.get("message_id") or ""),
                "kind": "child_message",
                "message_id": child.get("message_id"),
                "thread_id": child.get("thread_id"),
            }
        )
    for branch in branch_threads:
        branch_records.append(
            {
                "title": str(branch.get("subject") or "branch thread"),
                "detail": str(branch.get("latest_summary") or branch.get("thread_id") or ""),
                "kind": "branch_thread",
                "thread_id": branch.get("thread_id"),
                "status": branch.get("status"),
            }
        )
    agent_records = [
        {
            "title": "participants",
            "detail": ", ".join(str(item) for item in list(message.get("participants") or thread.get("participants") or [])) or "none",
            "kind": "participants",
        },
        {
            "title": "acknowledgements",
            "detail": str(len(list(message.get("acked_by") or []))),
            "kind": "acks",
        },
        {
            "title": "requires response",
            "detail": "yes" if bool(message.get("requires_response")) else "no",
            "kind": "requires_response",
        },
    ]
    mentioned_roles = [str(item) for item in list(message.get("mentioned_roles") or []) if str(item).strip()]
    unresolved_mentions = [str(item) for item in list(message.get("unresolved_mentions") or []) if str(item).strip()]
    if mentioned_roles:
        agent_records.append(
            {
                "title": "mentions",
                "detail": ", ".join(mentioned_roles),
                "kind": "mentions",
            }
        )
    if unresolved_mentions:
        agent_records.append(
            {
                "title": "unresolved mentions",
                "detail": ", ".join(unresolved_mentions),
                "kind": "unresolved_mentions",
            }
        )
    tabs = [
        _tab(
            "message",
            "MESSAGE",
            [
                {
                    "title": str(message.get("subject") or thread.get("subject") or "message"),
                    "detail": body,
                    "summary": str(message.get("summary") or _message_summary(body)),
                    "kind": str(message.get("message_kind") or "thread_note"),
                    "message_id": message_id,
                }
            ],
        ),
        _tab("route", "ROUTE", route_records),
        _tab("context", "CONTEXT", context_records),
        _tab("branches", "BRANCHES", branch_records),
        _tab("agents", "AGENTS", agent_records),
        _tab(
            "raw",
            "RAW",
            [
                {
                    "title": "safe payload",
                    "detail": json.dumps(_safe_message_payload(message), indent=2, sort_keys=True, ensure_ascii=False),
                    "kind": "raw",
                }
            ],
        ),
    ]
    return {
        "schema_id": WORK_PANEL_SCHEMA_ID,
        "panel_id": f"agent_work_{_slug(message_id, 'message')}",
        "panel_kind": "agent_comms_message",
        "message_id": message_id,
        "thread_id": thread_id,
        "channel_id": str(message.get("channel_id") or thread.get("channel_id") or ""),
        "room_id": str(message.get("room_id") or thread.get("room_id") or ""),
        "room_kind": str(message.get("room_kind") or thread.get("room_kind") or ""),
        "report_to_room_id": str(message.get("report_to_room_id") or thread.get("report_to_room_id") or ""),
        "from_role": str(message.get("from_role") or ""),
        "to_roles": list(message.get("to_roles") or []),
        "message_kind": str(message.get("message_kind") or "thread_note"),
        "subject": str(message.get("subject") or thread.get("subject") or ""),
        "summary": str(message.get("summary") or _message_summary(body)),
        "created_at": str(message.get("created_at") or ""),
        "updated_at": str(message.get("updated_at") or ""),
        "body_chars": len(body),
        "tabs": tabs,
        "navigation": {
            "can_open_detail": True,
            "can_branch": True,
            "thread_id": thread_id,
            "message_id": message_id,
            "parent_message_id": parent_message_id,
            "child_message_ids": child_ids,
            "branch_thread_ids": branch_thread_ids,
            "source_refs": list(message.get("source_refs") or []),
            "artifact_refs": list(message.get("artifact_refs") or []),
            "room_capsule_path": str(message.get("room_capsule_path") or thread.get("room_capsule_path") or ""),
        },
        "source_path": str(message.get("path") or ""),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def _decorate_messages_with_work_panels(root: Path, comms: Path, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not messages:
        return messages
    messages_by_thread: dict[str, list[dict[str, Any]]] = {}
    for message in messages:
        messages_by_thread.setdefault(str(message.get("thread_id") or ""), []).append(message)
    thread_rows: dict[str, dict[str, Any]] = {}
    for thread_id in messages_by_thread:
        thread = _load_thread(comms, thread_id)
        if thread:
            thread["path"] = _rel(_thread_path(comms, thread_id), root)
        thread_rows[thread_id] = thread
    branch_threads_by_parent: dict[str, list[dict[str, Any]]] = {}
    for path in _iter_thread_paths(comms):
        thread = _read_json(path)
        if not thread:
            continue
        parent = str(thread.get("branch_parent_message_id") or thread.get("parent_message_id") or "")
        if parent:
            row = dict(thread)
            row["path"] = _rel(path, root)
            branch_threads_by_parent.setdefault(parent, []).append(row)
    children_by_parent: dict[str, list[dict[str, Any]]] = {}
    for message in messages:
        parent = str(message.get("parent_message_id") or "")
        if parent:
            children_by_parent.setdefault(parent, []).append(message)
    for message in messages:
        thread_id = str(message.get("thread_id") or "")
        message_id = str(message.get("message_id") or "")
        message["work_panel"] = _build_message_work_panel(
            root,
            message,
            thread_rows.get(thread_id, {}),
            child_messages=children_by_parent.get(message_id, []),
            branch_threads=branch_threads_by_parent.get(message_id, []),
        )
    return messages


def _write_ref(path: Path, payload: Mapping[str, Any]) -> None:
    _write_json(path, payload)


def _write_inbox_outbox_refs(root: Path, comms: Path, message: Mapping[str, Any], message_path: Path) -> dict[str, list[str]]:
    refs = {"inbox_refs": [], "outbox_refs": []}
    ref_base = {
        "schema_id": "ion.agent_comms.message_ref.v1",
        "message_id": message.get("message_id"),
        "thread_id": message.get("thread_id"),
        "channel_id": message.get("channel_id"),
        "room_id": message.get("room_id"),
        "room_kind": message.get("room_kind"),
        "report_to_room_id": message.get("report_to_room_id"),
        "room_capsule_path": message.get("room_capsule_path"),
        "message_kind": message.get("message_kind"),
        "subject": message.get("subject"),
        "from_role": message.get("from_role"),
        "summary": message.get("summary"),
        "created_at": message.get("created_at"),
        "message_path": _rel(message_path, root),
        "mentioned_roles": list(message.get("mentioned_roles") or []),
        "unresolved_mentions": list(message.get("unresolved_mentions") or []),
        "status": "unread",
        "production_authority": False,
        "live_execution_authority": False,
    }
    for role_id in list(message.get("to_roles") or []) + list(message.get("cc_roles") or []):
        normalized = normalize_role_id(role_id)
        if not normalized or normalized == "broadcast":
            continue
        inbox_path = comms / "inbox" / _role_slug(normalized) / f"{message['message_id']}.json"
        _write_ref(inbox_path, {**ref_base, "role_id": normalized, "box": "inbox"})
        refs["inbox_refs"].append(_rel(inbox_path, root))
    from_role = normalize_role_id(message.get("from_role"))
    if from_role:
        outbox_path = comms / "outbox" / _role_slug(from_role) / f"{message['message_id']}.json"
        _write_ref(outbox_path, {**ref_base, "role_id": from_role, "box": "outbox", "status": "sent"})
        refs["outbox_refs"].append(_rel(outbox_path, root))
    return refs


def _write_signal(root: Path, comms: Path, message: Mapping[str, Any], message_path: Path) -> str:
    signal_id = f"AGENT_COMMS_{_slug(message.get('channel_id'), 'channel')}_{_slug(message.get('message_kind'), 'msg')}_{_timestamp_slug()}"
    signal = {
        "schema_id": "ion.agent_comms.signal.v1",
        "signal_id": signal_id,
        "signal": "AGENT_COMMS_MESSAGE",
        "from_role": message.get("from_role"),
        "to_roles": list(message.get("to_roles") or []),
        "thread_id": message.get("thread_id"),
        "message_id": message.get("message_id"),
        "channel_id": message.get("channel_id"),
        "room_id": message.get("room_id"),
        "room_kind": message.get("room_kind"),
        "report_to_room_id": message.get("report_to_room_id"),
        "room_capsule_path": message.get("room_capsule_path"),
        "message_kind": message.get("message_kind"),
        "summary": message.get("summary"),
        "message_path": _rel(message_path, root),
        "created_at": _now(),
        "production_authority": False,
        "live_execution_authority": False,
    }
    signal_path = comms / "signals" / f"{signal_id}.json"
    _write_json(signal_path, signal)
    return _rel(signal_path, root)


def _blocked(action: str, finding: str, **extra: Any) -> dict[str, Any]:
    return {
        "schema_id": f"ion.agent_comms.{action}.result.v1",
        "ok": False,
        "finding": finding,
        **extra,
        "production_authority": False,
        "live_execution_authority": False,
    }


def send_agent_message(root: str | Path | None, payload: Mapping[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    shell_root = _root(root)
    comms = _comms_root(shell_root)
    data: dict[str, Any] = {}
    if payload:
        data.update(dict(payload))
    data.update({key: value for key, value in kwargs.items() if value is not None})

    from_role = normalize_role_id(data.get("from_role") or data.get("sender") or data.get("from") or "operator")
    to_roles = [normalize_role_id(item) for item in _coerce_list(data.get("to_roles") or data.get("to") or data.get("recipient"))]
    cc_roles = [normalize_role_id(item) for item in _coerce_list(data.get("cc_roles") or data.get("cc"))]
    to_roles = [role for role in to_roles if role]
    cc_roles = [role for role in cc_roles if role]
    body = str(data.get("body") or data.get("message") or data.get("content") or "").strip()
    if not from_role:
        return _blocked("send", "from_role_required")
    if not body:
        return _blocked("send", "body_required")
    mention_projection = extract_agent_mentions(shell_root, body)
    mention_roles = [
        role
        for role in list(mention_projection.get("roles") or [])
        if role and role != from_role and role not in to_roles and role not in cc_roles
    ]
    if mention_roles:
        to_roles.extend(mention_roles)
    if not to_roles and not cc_roles:
        to_roles = ["role.steward"] if from_role == "operator" else ["operator"]
    kind = _message_kind(data.get("message_kind") or data.get("kind"))
    participants = _message_participants(from_role, to_roles, cc_roles)
    requested_channel_id = _slug(data.get("channel_id") or data.get("channel") or "", "")
    default_channel_id = _default_channel_for_kind(kind, to_roles)
    room_kind = _infer_room_kind(data, kind=kind, channel_id=requested_channel_id or default_channel_id)
    room_id = _default_room_id(data, room_kind=room_kind, channel_id=requested_channel_id or default_channel_id, participants=participants)
    channel_id = _room_channel_id(room_kind, room_id, requested_channel_id, participants)
    if not requested_channel_id and channel_id == "team" and room_kind not in {"direct", "domain", "mission"}:
        channel_id = default_channel_id
    channel = _channel_by_id(channel_id)
    report_to_room_id = _default_report_to_room(room_kind, data)
    if "summary_required" in data:
        summary_required = bool(data.get("summary_required"))
    else:
        summary_required = room_kind in {"mission", "domain", "direct", "audit", "incident"}
    visibility = str(data.get("visibility") or ("direct_agent_pair" if room_kind == "direct" else "team_projection"))
    subject = str(data.get("subject") or data.get("title") or channel.get("label") or "Agent message").strip()
    now = _now()
    thread_id = str(data.get("thread_id") or "").strip()
    if not thread_id:
        thread_id = f"thread_{_timestamp_slug()}_{channel_id}_{_slug(subject, 'message')}"
    thread_id = _slug(thread_id, "thread")
    source_refs = _coerce_list(data.get("source_refs") or data.get("context_refs"))
    artifact_refs = _coerce_list(data.get("artifact_refs") or data.get("evidence_refs"))
    message_id = f"msg_{_timestamp_slug()}_{_slug(from_role, 'from')}"
    message = {
        "schema_id": MESSAGE_SCHEMA_ID,
        "message_id": message_id,
        "thread_id": thread_id,
        "channel_id": channel_id,
        "room_id": room_id,
        "room_kind": room_kind,
        "report_to_room_id": report_to_room_id,
        "summary_required": summary_required,
        "from_role": from_role,
        "to_roles": to_roles,
        "cc_roles": cc_roles,
        "participants": participants,
        "message_kind": kind,
        "subject": subject,
        "body": body,
        "summary": str(data.get("summary") or _message_summary(body, subject)),
        "priority": str(data.get("priority") or "P2"),
        "requires_response": bool(data.get("requires_response")),
        "response_due": str(data.get("response_due") or ""),
        "parent_message_id": str(data.get("parent_message_id") or ""),
        "branch_id": str(data.get("branch_id") or ""),
        "branch_root_message_id": str(data.get("branch_root_message_id") or data.get("parent_message_id") or ""),
        "branch_parent_thread_id": str(data.get("branch_parent_thread_id") or ""),
        "branch_reason": str(data.get("branch_reason") or ""),
        "authority_boundary": str(data.get("authority_boundary") or "candidate_comms_not_accepted_state"),
        "routing_policy": str(data.get("routing_policy") or "relay_or_steward_mediated"),
        "visibility": visibility,
        "status": str(data.get("status") or "sent"),
        "source_refs": source_refs,
        "artifact_refs": artifact_refs,
        "receipt_refs": _coerce_list(data.get("receipt_refs")),
        "mentions": list(mention_projection.get("mentions") or []),
        "mentioned_roles": list(mention_projection.get("roles") or []),
        "unresolved_mentions": list(mention_projection.get("unresolved") or []),
        "mention_routing_applied": bool(mention_roles),
        "created_at": now,
        "updated_at": now,
        "acked_by": [],
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }

    thread = _load_thread(comms, thread_id)
    if not thread:
        thread = {
            "schema_id": THREAD_SCHEMA_ID,
            "thread_id": thread_id,
            "channel_id": channel_id,
            "room_id": room_id,
            "room_kind": room_kind,
            "report_to_room_id": report_to_room_id,
            "summary_required": summary_required,
            "visibility": visibility,
            "channel_label": channel.get("label"),
            "subject": subject,
            "mission": str(data.get("mission") or ""),
            "status": "active",
            "participants": participants,
            "created_by": from_role,
            "created_at": now,
            "updated_at": now,
            "message_count": 0,
            "latest_message_id": "",
            "latest_summary": "",
            "source_refs": [],
            "artifact_refs": [],
            "room_capsule_path": "",
            "branch_parent_message_id": str(data.get("branch_parent_message_id") or data.get("parent_message_id") or ""),
            "branch_parent_thread_id": str(data.get("branch_parent_thread_id") or ""),
            "branch_reason": str(data.get("branch_reason") or ""),
            "unread_by_role": {},
            "production_authority": False,
            "live_execution_authority": False,
        }
    else:
        merged_participants = _message_participants("", list(thread.get("participants") or []) + participants, [])
        thread["participants"] = merged_participants
        participants = merged_participants
    thread["updated_at"] = now
    thread.setdefault("room_id", room_id)
    thread.setdefault("room_kind", room_kind)
    thread.setdefault("report_to_room_id", report_to_room_id)
    thread.setdefault("summary_required", summary_required)
    thread.setdefault("visibility", visibility)
    thread["message_count"] = int(thread.get("message_count") or 0) + 1
    thread["latest_message_id"] = message_id
    thread["latest_summary"] = message["summary"]
    thread["source_refs"] = sorted({*list(thread.get("source_refs") or []), *source_refs})
    thread["artifact_refs"] = sorted({*list(thread.get("artifact_refs") or []), *artifact_refs})
    unread = dict(thread.get("unread_by_role") or {})
    for role in to_roles + cc_roles:
        if role != from_role:
            unread[role] = int(unread.get(role) or 0) + 1
    thread["unread_by_role"] = unread

    message_path = _message_file(comms, thread_id, message_id, now)
    _write_json(message_path, message)
    thread_path = _write_thread(comms, thread)
    room_capsule_path = _write_room_capsule(shell_root, comms, message=message, thread=thread, message_path=message_path, thread_path=thread_path)
    message["room_capsule_path"] = room_capsule_path
    thread["room_capsule_path"] = room_capsule_path
    _write_json(message_path, message)
    thread_path = _write_thread(comms, thread)
    refs = _write_inbox_outbox_refs(shell_root, comms, message, message_path)
    signal_path = ""
    if data.get("emit_signal", True) is not False:
        signal_path = _write_signal(shell_root, comms, message, message_path)

    index = _load_message_index(comms)
    index.setdefault("messages", {})[message_id] = {
        "thread_id": thread_id,
        "message_path": _rel(message_path, shell_root),
        "thread_path": _rel(thread_path, shell_root),
        "created_at": now,
        "from_role": from_role,
        "to_roles": to_roles,
        "mentioned_roles": list(mention_projection.get("roles") or []),
        "unresolved_mentions": list(mention_projection.get("unresolved") or []),
        "channel_id": channel_id,
        "room_id": room_id,
        "room_kind": room_kind,
        "report_to_room_id": report_to_room_id,
        "room_capsule_path": room_capsule_path,
    }
    _save_message_index(comms, index)
    log_payload = {
        "timestamp": now,
        "event": "agent_message_sent",
        "message_id": message_id,
        "thread_id": thread_id,
        "channel_id": channel_id,
        "room_id": room_id,
        "room_kind": room_kind,
        "report_to_room_id": report_to_room_id,
        "room_capsule_path": room_capsule_path,
        "from_role": from_role,
        "to_roles": to_roles,
        "mentioned_roles": list(mention_projection.get("roles") or []),
        "unresolved_mentions": list(mention_projection.get("unresolved") or []),
        "message_path": _rel(message_path, shell_root),
    }
    _append_jsonl(comms / "logs" / "messages.jsonl", log_payload)

    return {
        "schema_id": "ion.agent_comms.send.result.v1",
        "ok": True,
        "message_id": message_id,
        "thread_id": thread_id,
        "channel_id": channel_id,
        "message_path": _rel(message_path, shell_root),
        "thread_path": _rel(thread_path, shell_root),
        "room_id": room_id,
        "room_kind": room_kind,
        "report_to_room_id": report_to_room_id,
        "room_capsule_path": room_capsule_path,
        "signal_path": signal_path,
        "to_roles": to_roles,
        "mentions": list(mention_projection.get("mentions") or []),
        "mentioned_roles": list(mention_projection.get("roles") or []),
        "unresolved_mentions": list(mention_projection.get("unresolved") or []),
        "mention_routing_applied": bool(mention_roles),
        **refs,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _iter_thread_paths(comms: Path) -> list[Path]:
    root = comms / "threads"
    if not root.exists():
        return []
    return sorted(root.glob("*/THREAD.json"), key=lambda path: path.stat().st_mtime, reverse=True)


def _load_thread_messages(comms: Path, thread_id: str, *, limit: int = 200) -> list[dict[str, Any]]:
    messages_dir = _messages_dir(comms, thread_id)
    if not messages_dir.exists():
        return []
    shell_root = _root(comms)
    paths = sorted(messages_dir.glob("*.json"), key=lambda path: path.name)
    rows: list[dict[str, Any]] = []
    for path in paths[-limit:]:
        row = _read_json(path)
        if row:
            row["path"] = _rel(path, shell_root)
            rows.append(row)
    return _decorate_messages_with_work_panels(shell_root, comms, rows)


def list_agent_threads(
    root: str | Path | None = None,
    *,
    role_id: str | None = None,
    channel_id: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    shell_root = _root(root)
    comms = _comms_root(shell_root)
    role = normalize_role_id(role_id)
    channel = _slug(channel_id or "", "")
    threads: list[dict[str, Any]] = []
    for path in _iter_thread_paths(comms):
        thread = _read_json(path)
        if not thread:
            continue
        participants = {normalize_role_id(item) for item in list(thread.get("participants") or [])}
        if role and role not in participants:
            continue
        if channel and thread.get("channel_id") != channel:
            continue
        row = dict(thread)
        row["path"] = _rel(path, shell_root)
        threads.append(row)
        if len(threads) >= limit:
            break
    return {
        "schema_id": "ion.agent_comms.thread_list.v1",
        "ok": True,
        "thread_count": len(threads),
        "threads": threads,
        "role_id": role,
        "channel_id": channel,
        "production_authority": False,
        "live_execution_authority": False,
    }


def read_agent_thread(
    root: str | Path | None,
    thread_id: str,
    *,
    role_id: str | None = None,
    limit: int = 200,
) -> dict[str, Any]:
    shell_root = _root(root)
    comms = _comms_root(shell_root)
    thread_key = _slug(thread_id, "thread")
    thread = _load_thread(comms, thread_key)
    if not thread:
        return _blocked("thread", "thread_not_found", thread_id=thread_id)
    role = normalize_role_id(role_id)
    if role:
        participants = {normalize_role_id(item) for item in list(thread.get("participants") or [])}
        if role not in participants:
            return _blocked("thread", "role_not_in_thread", thread_id=thread_key, role_id=role)
    messages = _load_thread_messages(comms, thread_key, limit=limit)
    return {
        "schema_id": "ion.agent_comms.thread_read.v1",
        "ok": True,
        "thread": thread,
        "messages": messages,
        "message_count": len(messages),
        "production_authority": False,
        "live_execution_authority": False,
    }


def create_agent_message_branch(root: str | Path | None, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    shell_root = _root(root)
    comms = _comms_root(shell_root)
    data = dict(payload or {})
    source_message_id = str(data.get("source_message_id") or data.get("message_id") or "").strip()
    if not source_message_id:
        return _blocked("branch", "source_message_id_required")
    source_path = _message_path_from_index(comms, shell_root, source_message_id)
    if source_path is None:
        return _blocked("branch", "source_message_not_found", source_message_id=source_message_id)
    source_message = _read_json(source_path)
    if not source_message:
        return _blocked("branch", "source_message_unreadable", source_message_id=source_message_id)
    source_thread_id = str(source_message.get("thread_id") or "")
    source_thread = _load_thread(comms, source_thread_id)
    subject = str(data.get("subject") or f"Branch: {source_message.get('subject') or source_message.get('summary') or source_message_id}").strip()
    body = str(
        data.get("body")
        or "\n".join(
            [
                f"Branch opened from agent comms message {source_message_id}.",
                "",
                f"Source summary: {source_message.get('summary') or _message_summary(str(source_message.get('body') or ''))}",
                "",
                "Use this branch to inspect, answer, or expand the communication without losing the parent thread.",
            ]
        )
    ).strip()
    target_roles = _coerce_list(data.get("to_roles") or data.get("to"))
    if not target_roles:
        target_roles = list(source_message.get("to_roles") or []) or ["role.steward"]
    branch_thread_id = _slug(
        data.get("thread_id") or f"branch_{source_message_id}_{_timestamp_slug()}_{_slug(subject, 'agent_comms_branch')}",
        "agent_comms_branch",
    )
    source_refs = [
        _rel(source_path, shell_root),
        _rel(_thread_path(comms, source_thread_id), shell_root) if source_thread_id else "",
        *list(source_message.get("source_refs") or []),
    ]
    result = send_agent_message(
        shell_root,
        {
            "channel_id": data.get("channel_id") or source_message.get("channel_id") or source_thread.get("channel_id") or "team",
            "thread_id": branch_thread_id,
            "from_role": data.get("from_role") or data.get("opened_by") or "operator",
            "to_roles": target_roles,
            "cc_roles": data.get("cc_roles") or [],
            "message_kind": data.get("message_kind") or "thread_note",
            "subject": subject,
            "body": body,
            "summary": data.get("summary") or _message_summary(body, subject),
            "requires_response": bool(data.get("requires_response", True)),
            "parent_message_id": source_message_id,
            "branch_id": branch_thread_id,
            "branch_root_message_id": source_message.get("branch_root_message_id") or source_message_id,
            "branch_parent_message_id": source_message_id,
            "branch_parent_thread_id": source_thread_id,
            "branch_reason": data.get("branch_reason") or "open_detail_branch",
            "source_refs": [item for item in source_refs if item],
            "artifact_refs": list(source_message.get("artifact_refs") or []),
            "receipt_refs": list(source_message.get("receipt_refs") or []),
            "authority_boundary": "candidate_comms_branch_not_accepted_state",
            "routing_policy": "branch_navigation_detail_thread",
            "visibility": "team_projection",
        },
    )
    if not result.get("ok"):
        return result
    return {
        **result,
        "schema_id": "ion.agent_comms.branch.result.v1",
        "source_message_id": source_message_id,
        "source_thread_id": source_thread_id,
        "new_thread_id": result.get("thread_id"),
        "branch_thread_id": result.get("thread_id"),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def _message_path_from_index(comms: Path, root: Path, message_id: str) -> Path | None:
    index = _load_message_index(comms)
    row = dict(index.get("messages", {}).get(message_id) or {})
    rel_path = str(row.get("message_path") or "")
    if rel_path:
        candidate = (root / rel_path).resolve()
        if candidate.exists():
            return candidate
    for path in (comms / "threads").glob(f"*/messages/*_{_slug(message_id, 'msg')}.json"):
        if path.exists():
            return path
    return None


def ack_agent_message(
    root: str | Path | None,
    payload: Mapping[str, Any] | None = None,
    *,
    message_id: str | None = None,
    ack_by: str | None = None,
    status: str = "acknowledged",
) -> dict[str, Any]:
    shell_root = _root(root)
    comms = _comms_root(shell_root)
    data = dict(payload or {})
    message_key = str(data.get("message_id") or message_id or "").strip()
    ack_role = normalize_role_id(data.get("ack_by") or data.get("ack_by_role") or ack_by or "")
    if not message_key:
        return _blocked("ack", "message_id_required")
    if not ack_role:
        return _blocked("ack", "ack_by_required")
    message_path = _message_path_from_index(comms, shell_root, message_key)
    if message_path is None:
        return _blocked("ack", "message_not_found", message_id=message_key)
    message = _read_json(message_path)
    if not message:
        return _blocked("ack", "message_unreadable", message_id=message_key)
    now = _now()
    ack = {
        "schema_id": ACK_SCHEMA_ID,
        "message_id": message_key,
        "thread_id": message.get("thread_id"),
        "ack_by": ack_role,
        "status": status if status in TERMINAL_MESSAGE_STATUSES else "acknowledged",
        "acked_at": now,
        "production_authority": False,
        "live_execution_authority": False,
    }
    acked_by = list(message.get("acked_by") or [])
    acked_by.append(ack)
    message["acked_by"] = acked_by
    message["updated_at"] = now
    if message.get("status") not in TERMINAL_MESSAGE_STATUSES:
        message["status"] = "acknowledged"
    _write_json(message_path, message)

    thread_id = str(message.get("thread_id") or "")
    thread = _load_thread(comms, thread_id)
    if thread:
        unread = dict(thread.get("unread_by_role") or {})
        unread[ack_role] = max(0, int(unread.get(ack_role) or 0) - 1)
        thread["unread_by_role"] = unread
        thread["updated_at"] = now
        _write_thread(comms, thread)
    inbox_ref = comms / "inbox" / _role_slug(ack_role) / f"{message_key}.json"
    if inbox_ref.exists():
        ref = _read_json(inbox_ref)
        ref["status"] = "read"
        ref["acked_at"] = now
        _write_json(inbox_ref, ref)
    ack_path = comms / "receipts" / "acks" / f"{_timestamp_slug()}_{_slug(message_key, 'msg')}_{_role_slug(ack_role)}.json"
    _write_json(ack_path, ack)
    _append_jsonl(comms / "logs" / "acks.jsonl", {**ack, "ack_path": _rel(ack_path, shell_root)})
    return {
        "schema_id": "ion.agent_comms.ack.result.v1",
        "ok": True,
        "message_id": message_key,
        "thread_id": thread_id,
        "status": message.get("status"),
        "ack_path": _rel(ack_path, shell_root),
        "production_authority": False,
        "live_execution_authority": False,
    }


def _recent_messages(root: Path, comms: Path, *, limit: int = 100) -> list[dict[str, Any]]:
    message_paths = []
    threads_root = comms / "threads"
    if threads_root.exists():
        message_paths = sorted(threads_root.glob("*/messages/*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    rows: list[dict[str, Any]] = []
    for path in message_paths[:limit]:
        row = _read_json(path)
        if row:
            row["path"] = _rel(path, root)
            rows.append(row)
    return _decorate_messages_with_work_panels(root, comms, rows)


def _unread_by_role(threads: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for thread in threads:
        unread = thread.get("unread_by_role")
        if not isinstance(unread, Mapping):
            continue
        for role, count in unread.items():
            try:
                counts[str(role)] = counts.get(str(role), 0) + int(count or 0)
            except (TypeError, ValueError):
                continue
    return dict(sorted(counts.items()))


def _compact_home_view_projection(root: Path, limit: int = 12) -> list[dict[str, Any]]:
    projection_dir = _comms_root(root) / "projections"
    if not projection_dir.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(projection_dir.glob("agent_home_view_*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        name = path.name
        if name.startswith("agent_home_view_smoke_"):
            continue
        if name.startswith("agent_home_view_scout_context_card_"):
            continue
        if name.startswith("agent_home_view_self_improvement_"):
            continue
        home_view = _read_json(path)
        if not home_view:
            continue
        identity = home_view.get("identity") if isinstance(home_view.get("identity"), Mapping) else {}
        role_id = normalize_role_id(identity.get("assigned_role") or "")
        if not role_id:
            continue
        scout_card = home_view.get("scout_context_card") if isinstance(home_view.get("scout_context_card"), Mapping) else {}
        loop = home_view.get("self_improvement_loop") if isinstance(home_view.get("self_improvement_loop"), Mapping) else {}
        scout_path = str(home_view.get("scout_context_card_path") or "").strip()
        if not scout_card and scout_path:
            scout_abs = _safe_repo_path(root, scout_path)
            if scout_abs is not None:
                scout_card = _read_json(scout_abs)
        loop_path = str(home_view.get("self_improvement_loop_path") or "").strip()
        if not loop and loop_path:
            loop_abs = _safe_repo_path(root, loop_path)
            if loop_abs is not None:
                loop = _read_json(loop_abs)
        source_surfaces = home_view.get("source_surfaces") if isinstance(home_view.get("source_surfaces"), Mapping) else {}
        not_used_for_orientation = _coerce_list(source_surfaces.get("not_used_for_orientation"))
        scout_forbidden = _coerce_list(scout_card.get("forbidden_default_surfaces")) if isinstance(scout_card, Mapping) else []
        loop_items = [item for item in list(loop.get("items") or []) if isinstance(item, Mapping)][:40]
        rows.append(
            {
                "role_id": role_id,
                "projection_path": _rel(path, root),
                "updated_at": home_view.get("updated_at"),
                "schema_id": home_view.get("schema_id"),
                "source_surfaces": {
                    "files": _coerce_list(source_surfaces.get("files"))[:24],
                    "not_used_for_orientation": not_used_for_orientation[:12],
                },
                "scout_context_card": {
                    "schema_id": scout_card.get("schema_id") if isinstance(scout_card, Mapping) else "",
                    "compact_defaults": dict(scout_card.get("compact_defaults") or {}) if isinstance(scout_card, Mapping) else {},
                    "context_read_order": [
                        {
                            "step": item.get("step"),
                            "surface": item.get("surface"),
                            "scan_cap": item.get("scan_cap"),
                            "reason": item.get("reason"),
                        }
                        for item in list(scout_card.get("context_read_order") or [])
                        if isinstance(item, Mapping)
                    ][:20],
                    "forbidden_default_surfaces": sorted({*not_used_for_orientation, *scout_forbidden})[:16],
                },
                "self_improvement_loop": {
                    "schema_id": loop.get("schema_id") if isinstance(loop, Mapping) else "",
                    "status": loop.get("status") if isinstance(loop, Mapping) else "",
                    "counts": dict(loop.get("counts") or {}) if isinstance(loop, Mapping) else {},
                    "items": [
                        {
                            "work_item_id": item.get("work_item_id"),
                            "kind": item.get("kind"),
                            "priority": item.get("priority"),
                            "summary": item.get("summary"),
                            "suggested_action": item.get("suggested_action"),
                            "proof_links": _coerce_list(item.get("proof_links"))[:8],
                            "source": item.get("source"),
                        }
                        for item in loop_items
                    ],
                },
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
            }
        )
        if len(rows) >= limit:
            break
    return rows


def build_agent_comms_projection(
    root: str | Path | None = None,
    *,
    agents: Sequence[Mapping[str, Any]] | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    shell_root = _root(root)
    comms = _comms_root(shell_root)
    channels = default_agent_channels()
    channel_ids = {channel["channel_id"] for channel in channels}
    threads_result = list_agent_threads(shell_root, limit=limit)
    threads = list(threads_result.get("threads") or [])
    recent_messages = _recent_messages(shell_root, comms, limit=limit)
    dynamic_channel_counts: dict[str, int] = {channel_id: 0 for channel_id in channel_ids}
    for thread in threads:
        channel_id = str(thread.get("channel_id") or "team")
        if channel_id not in dynamic_channel_counts:
            channels.append(_channel_by_id(channel_id))
            dynamic_channel_counts[channel_id] = 0
        dynamic_channel_counts[channel_id] += 1
    for channel in channels:
        channel["thread_count"] = dynamic_channel_counts.get(str(channel.get("channel_id")), 0)

    agent_rows = list(agents or [])
    available_roles = sorted(
        {
            normalize_role_id(agent.get("role_id") or agent.get("agent_id"))
            for agent in agent_rows
            if normalize_role_id(agent.get("role_id") or agent.get("agent_id"))
        }
    )
    message_kinds: dict[str, int] = {}
    for message in recent_messages:
        kind = str(message.get("message_kind") or "thread_note")
        message_kinds[kind] = message_kinds.get(kind, 0) + 1
    compact_home_views = _compact_home_view_projection(shell_root, limit=min(max(limit, 1), 20))
    rooms_projection = _room_projection(shell_root, comms, threads, limit=limit)
    selected_thread = threads[0] if threads else {}
    selected_thread_id = str(selected_thread.get("thread_id") or "")
    selected_messages = [message for message in recent_messages if str(message.get("thread_id") or "") == selected_thread_id]
    try:
        from .ion_agent_comms_operational_graph import build_agent_comms_thread_operational_graph

        operational_graph = build_agent_comms_thread_operational_graph(
            shell_root,
            thread_id=selected_thread_id or None,
            limit=limit,
        )
    except Exception as exc:
        operational_graph = {
            "schema_id": "ion.agent_comms.thread_operational_graph.v1",
            "ok": False,
            "finding": "operational_graph_projection_failed",
            "error": exc.__class__.__name__,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }
    try:
        from .ion_agent_comms_runs import build_agent_comms_runs_projection

        runs_projection = build_agent_comms_runs_projection(shell_root)
    except Exception as exc:
        runs_projection = {
            "schema_id": "ion.agent_comms.runs.projection.v1",
            "ok": False,
            "finding": "runs_projection_failed",
            "error": exc.__class__.__name__,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }
    return {
        "schema_id": PROJECTION_SCHEMA_ID,
        "ok": True,
        "comms_root": AGENT_COMMS_ROOT.as_posix(),
        "source_model": {
            "agent_private_continuity": "source_truth",
            "agent_comms": "durable_packet_bus",
            "cockpit": "compiled_projection",
            "mcp": "accelerator_not_dependency",
            "accepted_state": "not_granted_by_messages",
        },
        "channels": sorted(channels, key=lambda item: int(item.get("order") or 999)),
        "threads": threads,
        "recent_messages": recent_messages,
        "rooms": rooms_projection,
        "runs": runs_projection,
        "agent_home_views": compact_home_views,
        "conversation": {
            "schema_id": "ion.agent_comms.conversation_projection.v1",
            "selected_thread_id": selected_thread_id,
            "selected_channel_id": str(selected_thread.get("channel_id") or ""),
            "selected_thread": selected_thread,
            "work_panels": [record.get("work_panel") for record in selected_messages if isinstance(record.get("work_panel"), Mapping)],
            "panel_count": len(selected_messages),
            "operational_graph": operational_graph,
            "policy": "Agent comms render through Codex-style work panels and the operational graph so humans and agents can navigate objective, routing, scheduler, context, branch, proof, and raw evidence lanes.",
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        },
        "unread_by_role": _unread_by_role(threads),
        "available_roles": available_roles,
        "summary": {
            "channel_count": len(channels),
            "thread_count": len(threads),
            "message_count": len(recent_messages),
            "room_count": rooms_projection.get("room_count", 0),
            "room_kind_counts": rooms_projection.get("room_kind_counts", {}),
            "unread_role_count": len(_unread_by_role(threads)),
            "message_kinds": dict(sorted(message_kinds.items())),
            "agent_home_view_count": len(compact_home_views),
        },
        "policy": [
            "Filesystem-first: comms remain readable without MCP or live servers.",
            "Agent continuity stays private; this surface carries packets and projections only.",
            "Relay, Steward, Persona, Vice, Nemesis, and support agents keep separate authority burdens.",
            "Messages do not create production, live execution, or accepted-state authority.",
        ],
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }
