"""Workspace-first read model for agent comms orientation.

This module adds a minimal layer above carrier/agent message transport so a
role can orient from compact read models instead of polling full logs.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .ion_agent_comms import AGENT_COMMS_ROOT, normalize_role_id

WORKSPACE_PROTOCOL_SCHEMA_ID = "ion.agent_workspace_comms_protocol.v0"
AGENT_HOME_VIEW_SCHEMA_ID = "ion.agent_home_view.v0"
AGENT_HOME_VIEW_SMOKE_SCHEMA_ID = "ion.agent_home_view.smoke.v0"
SCOUT_CONTEXT_CARD_SCHEMA_ID = "ion.agent_home_view.scout_context_card.v0"
SELF_IMPROVEMENT_LOOP_SCHEMA_ID = "ion.agent_home_view.self_improvement_loop.v0"
AGENT_INBOX_PICKUP_PREVIEW_SCHEMA_ID = "ion.agent_comms.inbox_pickup.preview.v0"
AGENT_INBOX_PICKUP_SCHEMA_ID = "ion.agent_comms.inbox_pickup.v0"

WORKSPACE_PROTOCOL_PATH = AGENT_COMMS_ROOT / "ion_agent_workspace_comms_protocol.v0.json"
MESSAGE_INDEX_PATH = AGENT_COMMS_ROOT / "projections" / "MESSAGE_INDEX.json"
COMMUNICATION_DIRECTORY_PATH = AGENT_COMMS_ROOT / "COMMUNICATION_DIRECTORY.json"
PICKUP_RECEIPT_ROOT = AGENT_COMMS_ROOT / "receipts" / "pickups"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _slug(value: Any, fallback: str = "item") -> str:
    text = str(value or "").strip().lower()
    slug = re.sub(r"[^a-z0-9._-]+", "_", text).strip("._-")
    return slug[:96] or fallback


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
    value_text = str(value).strip()
    return [value_text] if value_text else []


def _record(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    return candidate


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


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
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _append_jsonl(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(payload), sort_keys=True, ensure_ascii=False) + "\n")


def _load_message(root: Path, rel_path: str) -> dict[str, Any]:
    path = _safe_repo_path(root, rel_path)
    if path is None:
        return {}
    payload = _read_json(path)
    if payload:
        payload["path"] = rel_path
    return payload


def _phase_from_codex_mini(root: Path) -> str:
    mini_path = root / "ION/05_context/current/codex_solo/MINI.md"
    if not mini_path.exists():
        return "unknown"
    try:
        text = mini_path.read_text(encoding="utf-8")
    except OSError:
        return "unknown"
    match = re.search(r"(?m)^PHASE:\s*(.+)$", text)
    return _text(match.group(1) if match else "", "unknown")


def _default_context_package_id(root: Path) -> str:
    payload = _read_json(root / "ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json")
    selected = _list(payload.get("selected_by_default"))
    if selected:
        return selected[0]
    packages = payload.get("packages")
    if isinstance(packages, list) and packages:
        return _text(_record(packages[0]).get("package_id"), "unknown")
    return "unknown"


def _role_inbox_path(root: Path, role: str, message_id: str) -> Path:
    return root / AGENT_COMMS_ROOT / "inbox" / _slug(role.replace("role.", "role_"), "role") / f"{message_id}.json"


def preview_agent_inbox_pickup(
    root: str | Path | None,
    *,
    role_id: str,
    message_id: str,
    thread_id: str = "",
    carrier_id: str = "CODEX_CLI_CARRIER",
    context_package_id: str = "",
) -> dict[str, Any]:
    shell_root = _root(root)
    role = normalize_role_id(role_id)
    message_key = _text(message_id)
    if not role:
        return {
            "schema_id": AGENT_INBOX_PICKUP_PREVIEW_SCHEMA_ID,
            "ok": False,
            "finding": "role_id_required",
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }
    if not message_key:
        return {
            "schema_id": AGENT_INBOX_PICKUP_PREVIEW_SCHEMA_ID,
            "ok": False,
            "finding": "message_id_required",
            "role_id": role,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }
    inbox_path = _role_inbox_path(shell_root, role, message_key)
    ref = _read_json(inbox_path)
    if not ref:
        return {
            "schema_id": AGENT_INBOX_PICKUP_PREVIEW_SCHEMA_ID,
            "ok": False,
            "finding": "inbox_ref_not_found",
            "role_id": role,
            "message_id": message_key,
            "inbox_ref_path": _rel(inbox_path, shell_root),
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }
    ref_thread_id = _text(ref.get("thread_id"))
    requested_thread_id = _text(thread_id)
    if requested_thread_id and requested_thread_id != ref_thread_id:
        return {
            "schema_id": AGENT_INBOX_PICKUP_PREVIEW_SCHEMA_ID,
            "ok": False,
            "finding": "thread_id_mismatch",
            "role_id": role,
            "message_id": message_key,
            "requested_thread_id": requested_thread_id,
            "actual_thread_id": ref_thread_id,
            "inbox_ref_path": _rel(inbox_path, shell_root),
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }
    return {
        "schema_id": AGENT_INBOX_PICKUP_PREVIEW_SCHEMA_ID,
        "ok": True,
        "would_mark_inbox_ref_picked_up": _text(ref.get("status"), "unread") == "unread",
        "pickup_allowed": _text(ref.get("status"), "unread") == "unread",
        "blocking_finding": "" if _text(ref.get("status"), "unread") == "unread" else "inbox_ref_not_unread",
        "role_id": role,
        "carrier_id": _text(carrier_id, "CODEX_CLI_CARRIER"),
        "context_package_id": _text(context_package_id or _default_context_package_id(shell_root), "unknown"),
        "message_id": message_key,
        "thread_id": ref_thread_id,
        "current_ref_status": _text(ref.get("status"), "unread"),
        "message_path": _text(ref.get("message_path")),
        "inbox_ref_path": _rel(inbox_path, shell_root),
        "required_for_pickup": ["idempotency_key", "ION_BOUNDED_WRITE_CONFIRMED"],
        "pickup_claim_boundary": "consumption_receipt_only_not_worker_execution",
        "mutates_active_state": False,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def pickup_agent_inbox_message(
    root: str | Path | None,
    *,
    role_id: str,
    message_id: str,
    thread_id: str = "",
    carrier_id: str = "CODEX_CLI_CARRIER",
    context_package_id: str = "",
    pickup_reason: str = "",
    idempotency_key: str = "",
) -> dict[str, Any]:
    shell_root = _root(root)
    preview = preview_agent_inbox_pickup(
        shell_root,
        role_id=role_id,
        message_id=message_id,
        thread_id=thread_id,
        carrier_id=carrier_id,
        context_package_id=context_package_id,
    )
    if preview.get("ok") is not True:
        return {**preview, "schema_id": AGENT_INBOX_PICKUP_SCHEMA_ID}

    role = _text(preview.get("role_id"))
    message_key = _text(preview.get("message_id"))
    inbox_path = _role_inbox_path(shell_root, role, message_key)
    ref = _read_json(inbox_path)
    now = _now()
    previous_status = _text(ref.get("status"), "unread")
    idempotency_slug = _slug(idempotency_key, "")
    receipt_name = (
        f"idempotency_{idempotency_slug}.json"
        if idempotency_slug
        else f"{re.sub(r'[^0-9]', '', now)[:14]}_{_slug(message_key, 'msg')}_{_slug(role, 'role')}.json"
    )
    receipt_path = shell_root / PICKUP_RECEIPT_ROOT / receipt_name
    receipt_rel = _rel(receipt_path, shell_root)
    existing_receipt = _read_json(receipt_path)
    if existing_receipt:
        return {
            **existing_receipt,
            "pickup_receipt_path": receipt_rel,
            "idempotent_replay": True,
            "mutates_active_state": False,
        }
    if previous_status != "unread":
        return {
            "schema_id": AGENT_INBOX_PICKUP_SCHEMA_ID,
            "ok": False,
            "finding": "inbox_ref_not_unread",
            "role_id": role,
            "carrier_id": _text(carrier_id, "CODEX_CLI_CARRIER"),
            "context_package_id": _text(context_package_id or preview.get("context_package_id"), "unknown"),
            "message_id": message_key,
            "thread_id": _text(ref.get("thread_id")),
            "inbox_ref_path": _rel(inbox_path, shell_root),
            "previous_ref_status": previous_status,
            "claim_boundary": "rejects_duplicate_or_non_unread_pickup_without_exact_idempotent_replay",
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        }

    context_id = _text(context_package_id or preview.get("context_package_id"), "unknown")
    carrier = _text(carrier_id, "CODEX_CLI_CARRIER")

    ref["status"] = "picked_up"
    ref["picked_up_at"] = now
    ref["picked_up_by_role"] = role
    ref["picked_up_by_carrier"] = carrier
    ref["pickup_context_package_id"] = context_id
    ref["pickup_receipt_path"] = receipt_rel
    _write_json(inbox_path, ref)

    thread_rel = f"{AGENT_COMMS_ROOT.as_posix()}/threads/{_text(ref.get('thread_id'))}/THREAD.json"
    thread_path = shell_root / thread_rel
    thread = _read_json(thread_path)
    if thread:
        unread = dict(thread.get("unread_by_role") or {})
        if previous_status not in {"read", "picked_up", "acknowledged", "answered", "settled", "archived"}:
            unread[role] = max(0, int(unread.get(role) or 0) - 1)
        thread["unread_by_role"] = unread
        thread["updated_at"] = now
        _write_json(thread_path, thread)

    receipt = {
        "schema_id": AGENT_INBOX_PICKUP_SCHEMA_ID,
        "ok": True,
        "created_at": now,
        "role_id": role,
        "carrier_id": carrier,
        "context_package_id": context_id,
        "idempotency_key": _text(idempotency_key),
        "message_id": message_key,
        "thread_id": _text(ref.get("thread_id")),
        "message_path": _text(ref.get("message_path")),
        "inbox_ref_path": _rel(inbox_path, shell_root),
        "thread_path": thread_rel if thread else "",
        "previous_ref_status": previous_status,
        "ref_status": "picked_up",
        "pickup_reason": _text(pickup_reason, "agent_context_consumption"),
        "claim_boundary": "proves_role_inbox_pickup_only_not_worker_execution_or_accepted_state",
        "non_claims": [
            "automatic_agent_reaction_not_proven_by_pickup_alone",
            "worker_execution_not_proven_by_pickup_alone",
            "accepted_state_authority_not_granted",
            "production_authority_not_granted",
            "live_execution_authority_not_granted",
            "secrets_authority_not_granted",
        ],
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }
    _write_json(receipt_path, receipt)
    _append_jsonl(shell_root / AGENT_COMMS_ROOT / "logs" / "pickups.jsonl", {**receipt, "pickup_receipt_path": receipt_rel})
    return {**receipt, "pickup_receipt_path": receipt_rel, "mutates_active_state": True}


def _queue_rows(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    for key in ("messages", "items", "carrier_messages"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [_record(row) for row in rows if isinstance(row, Mapping)]
    return []


def _build_context_read_order(
    shell_root: Path,
    *,
    role: str,
    max_inbox_scan: int,
    max_thread_scan: int,
    max_index_scan: int,
    max_carrier_scan: int,
) -> dict[str, Any]:
    role_inbox_rel = (AGENT_COMMS_ROOT / "inbox" / _slug(role.replace("role.", "role_"), "role")).as_posix()
    read_order = [
        {
            "step": 1,
            "surface": WORKSPACE_PROTOCOL_PATH.as_posix(),
            "reason": "Protocol and non-claims before data reads.",
            "scan_cap": 1,
        },
        {
            "step": 2,
            "surface": COMMUNICATION_DIRECTORY_PATH.as_posix(),
            "reason": "Resolve role aliases and room contract surfaces.",
            "scan_cap": 1,
        },
        {
            "step": 3,
            "surface": MESSAGE_INDEX_PATH.as_posix(),
            "reason": "Compact role mentions and thread refs.",
            "scan_cap": max_index_scan,
        },
        {
            "step": 4,
            "surface": role_inbox_rel,
            "reason": "Direct work items and blockers for assigned role.",
            "scan_cap": max_inbox_scan,
        },
        {
            "step": 5,
            "surface": (AGENT_COMMS_ROOT / "threads").as_posix(),
            "reason": "Owned thread summaries only.",
            "scan_cap": max_thread_scan,
        },
        {
            "step": 6,
            "surface": "ION/05_context/current/ACTIVE_CARRIER_MESSAGE_QUEUE.json",
            "reason": "Carrier-level mentions and receipts.",
            "scan_cap": max_carrier_scan,
        },
    ]
    return {
        "schema_id": SCOUT_CONTEXT_CARD_SCHEMA_ID,
        "role_id": role,
        "context_read_order": read_order,
        "compact_defaults": {
            "message_index_scan_cap": max_index_scan,
            "inbox_scan_cap": max_inbox_scan,
            "thread_scan_cap": max_thread_scan,
            "carrier_queue_scan_cap": max_carrier_scan,
        },
        "forbidden_default_surfaces": [
            (AGENT_COMMS_ROOT / "logs/messages.jsonl").as_posix(),
            "ION/05_context/current/chatgpt_connector/codex_queue_runs",
        ],
        "proof_policy": {
            "required": True,
            "proof_links_field": "proof_links",
            "rule": "Work items must include compact source refs before route-deeper actions.",
        },
        "updated_at": _now(),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def _build_self_improvement_loop(
    *,
    role: str,
    blockers: Sequence[Mapping[str, Any]],
    warnings: Sequence[Mapping[str, Any]],
    directives: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    def _append_item(row: Mapping[str, Any]) -> None:
        item_id = _text(row.get("work_item_id"))
        if not item_id or item_id in seen_ids:
            return
        seen_ids.add(item_id)
        items.append(dict(row))

    for blocker in blockers[:20]:
        message_id = _text(blocker.get("message_id") or blocker.get("thread_id"), "blocker")
        proof_links = sorted({item for item in [_text(blocker.get("message_path")), _text(blocker.get("thread_path"))] if item})
        _append_item(
            {
                "work_item_id": _slug(f"{role}_{message_id}_blocker", "blocker"),
                "kind": "blocker",
                "priority": "high",
                "summary": _text(blocker.get("summary"), "Resolve blocker and return proof-linked reply."),
                "suggested_action": "respond_with_task_return_and_receipts",
                "proof_links": proof_links,
                "source": _text(blocker.get("message_id") or blocker.get("thread_id")),
            }
        )

    for warning in warnings[:20]:
        code = _text(warning.get("code"), "warning")
        detail = _text(warning.get("detail"))
        kind = "blocker" if code.startswith("missing_") else "follow_up"
        priority = "high" if kind == "blocker" else "medium"
        proof_links = [detail] if detail.startswith("ION/") else []
        _append_item(
            {
                "work_item_id": _slug(f"{role}_{code}_{detail}", "warning"),
                "kind": kind,
                "priority": priority,
                "summary": f"{code}: {detail or 'compact surface needs attention'}",
                "suggested_action": "fix_missing_surface_or_acknowledge_scan_limit",
                "proof_links": proof_links,
                "source": code,
            }
        )

    for directive in directives[:20]:
        room_header = _record(directive.get("room_header"))
        current_directive = _record(directive.get("current_directive"))
        expected_reply = _text(current_directive.get("expected_reply_shape"), "ack_or_followup")
        if expected_reply != "task_return_with_receipts":
            continue
        message_id = _text(current_directive.get("message_id") or room_header.get("room_id"), "directive")
        proof_links = sorted(
            {
                item
                for item in [
                    _text(current_directive.get("message_path")),
                    _text(room_header.get("room_capsule_path")),
                    *_list(current_directive.get("receipt_links")),
                ]
                if item
            }
        )
        _append_item(
            {
                "work_item_id": _slug(f"{role}_{message_id}_follow_up", "follow_up"),
                "kind": "follow_up",
                "priority": "medium",
                "summary": _text(current_directive.get("summary"), "Follow up on pinned directive with proof-linked response."),
                "suggested_action": "prepare_follow_up_packet_or_task_return",
                "proof_links": proof_links,
                "source": _text(room_header.get("room_id")),
            }
        )

    return {
        "schema_id": SELF_IMPROVEMENT_LOOP_SCHEMA_ID,
        "role_id": role,
        "status": "items_ready" if items else "quiet",
        "items": items[:80],
        "counts": {
            "blockers": sum(1 for row in items if _text(row.get("kind")) == "blocker"),
            "follow_ups": sum(1 for row in items if _text(row.get("kind")) == "follow_up"),
            "total": len(items),
        },
        "loop_rule": "Home view emits compact, proof-linked follow-ups; deeper reads are explicit and bounded.",
        "updated_at": _now(),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def materialize_agent_workspace_comms_protocol(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _root(root)
    protocol = {
        "schema_id": WORKSPACE_PROTOCOL_SCHEMA_ID,
        "protocol_name": "ion_agent_workspace_comms_protocol.v0",
        "status": "candidate",
        "owned_artifact": WORKSPACE_PROTOCOL_PATH.as_posix(),
        "source_of_truth": {
            "transport": ["carrier_message_send", "carrier_message_poll", "carrier_message_ack"],
            "workspace": [
                COMMUNICATION_DIRECTORY_PATH.as_posix(),
                MESSAGE_INDEX_PATH.as_posix(),
                (AGENT_COMMS_ROOT / "rooms").as_posix(),
                (AGENT_COMMS_ROOT / "inbox").as_posix(),
                (AGENT_COMMS_ROOT / "threads").as_posix(),
            ],
        },
        "agent_home_view_shape": {
            "identity": [
                "carrier_id",
                "assigned_role",
                "mounted_role_phase",
                "context_package_id",
                "authority_flags",
            ],
            "attention": [
                "direct_mentions",
                "role_mentions",
                "owned_threads",
                "blockers_waiting_on_me",
                "pinned_current_directives",
                "unread_ack_defer_state",
                "partial_visibility_warnings",
            ],
            "safety": [
                "non_claims",
                "authority_bounds",
                "receipt_links",
                "source_surfaces",
            ],
        },
        "room_projection": {
            "room_header": [
                "room_id",
                "room_kind",
                "channel_id",
                "purpose",
                "participants",
                "thread_count",
                "latest_summary",
            ],
            "pins": ["source_refs", "artifact_refs"],
            "current_directive": ["message_id", "message_kind", "subject", "expected_reply_shape", "receipt_links"],
        },
        "partial_visibility_policy": {
            "required": True,
            "warnings": [
                "carrier_queue_scan_limited",
                "message_index_scan_limited",
                "missing_room_capsule",
                "missing_message_index",
                "missing_inbox_for_role",
            ],
        },
        "non_claims": {
            "accepted_state": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
        "updated_at": _now(),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }
    _write_json(shell_root / WORKSPACE_PROTOCOL_PATH, protocol)
    return protocol


def build_agent_home_view(
    root: str | Path | None,
    *,
    role_id: str,
    carrier_id: str = "CODEX_CLI_CARRIER",
    mounted_role_phase: str = "",
    context_package_id: str = "",
    max_inbox_scan: int = 200,
    max_thread_scan: int = 200,
    max_carrier_scan: int = 200,
    max_index_scan: int = 800,
    write_projection: bool = False,
) -> dict[str, Any]:
    shell_root = _root(root)
    comms_root = shell_root / AGENT_COMMS_ROOT
    role = normalize_role_id(role_id)
    if not role:
        return {
            "schema_id": AGENT_HOME_VIEW_SCHEMA_ID,
            "ok": False,
            "finding": "role_id_required",
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }

    protocol = materialize_agent_workspace_comms_protocol(shell_root)
    directory = _read_json(shell_root / COMMUNICATION_DIRECTORY_PATH)
    room_contract = _record(directory.get("room_contract"))
    rooms_by_id = _record(room_contract.get("rooms_by_id"))
    agents_by_role = _record(directory.get("agents_by_role"))
    role_profile = _record(agents_by_role.get(role))

    inbox_dir = comms_root / "inbox" / _slug(role.replace("role.", "role_"), "role")
    inbox_rows: list[dict[str, Any]] = []
    inbox_count = 0
    if inbox_dir.exists():
        inbox_paths = sorted(inbox_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
        inbox_count = len(inbox_paths)
        for path in inbox_paths[:max_inbox_scan]:
            row = _read_json(path)
            if not row:
                continue
            row["path"] = _rel(path, shell_root)
            inbox_rows.append(row)

    message_index = _read_json(shell_root / MESSAGE_INDEX_PATH)
    indexed_messages = list(_record(message_index.get("messages")).items())
    indexed_messages.sort(key=lambda item: _text(_record(item[1]).get("created_at")), reverse=True)
    indexed_rows = [(message_id, _record(row)) for message_id, row in indexed_messages[:max_index_scan]]

    direct_mentions: list[dict[str, Any]] = []
    role_mentions: list[dict[str, Any]] = []
    owned_room_ids: set[str] = set()
    receipt_links: set[str] = set()
    for row in inbox_rows:
        direct_mentions.append(
            {
                "message_id": _text(row.get("message_id")),
                "thread_id": _text(row.get("thread_id")),
                "from_role": _text(row.get("from_role")),
                "subject": _text(row.get("subject")),
                "summary": _text(row.get("summary")),
                "message_kind": _text(row.get("message_kind")),
                "status": _text(row.get("status"), "unread"),
                "message_path": _text(row.get("message_path")),
                "room_id": _text(row.get("room_id")),
                "room_capsule_path": _text(row.get("room_capsule_path")),
                "created_at": _text(row.get("created_at")),
            }
        )
        room_id = _text(row.get("room_id"))
        if room_id:
            owned_room_ids.add(room_id)
        for key in ("message_path", "room_capsule_path"):
            value = _text(row.get(key))
            if value:
                receipt_links.add(value)

    for message_id, row in indexed_rows:
        mentioned = [normalize_role_id(item) for item in _list(row.get("mentioned_roles"))]
        if role not in mentioned:
            continue
        role_mentions.append(
            {
                "message_id": message_id,
                "thread_id": _text(row.get("thread_id")),
                "from_role": _text(row.get("from_role")),
                "created_at": _text(row.get("created_at")),
                "message_path": _text(row.get("message_path")),
                "room_id": _text(row.get("room_id")),
                "room_capsule_path": _text(row.get("room_capsule_path")),
            }
        )
        room_id = _text(row.get("room_id"))
        if room_id:
            owned_room_ids.add(room_id)
        for key in ("message_path", "room_capsule_path"):
            value = _text(row.get(key))
            if value:
                receipt_links.add(value)

    thread_rows: list[dict[str, Any]] = []
    thread_dir = comms_root / "threads"
    thread_count = 0
    if thread_dir.exists():
        thread_paths = sorted(thread_dir.glob("*/THREAD.json"), key=lambda item: item.stat().st_mtime, reverse=True)
        thread_count = len(thread_paths)
        for path in thread_paths[:max_thread_scan]:
            row = _read_json(path)
            if not row:
                continue
            participants = {normalize_role_id(item) for item in _list(row.get("participants"))}
            created_by = normalize_role_id(row.get("created_by"))
            if role not in participants and created_by != role:
                continue
            row["path"] = _rel(path, shell_root)
            thread_rows.append(row)
            owned_room = _text(row.get("room_id"))
            if owned_room:
                owned_room_ids.add(owned_room)

    blockers: list[dict[str, Any]] = []
    for row in inbox_rows:
        text = f"{_text(row.get('subject'))} {_text(row.get('summary'))} {_text(row.get('message_kind'))}".lower()
        if _text(row.get("message_kind")) == "blocker" or "blocker" in text or _text(row.get("status")).lower() == "blocked":
            blockers.append(
                {
                    "message_id": _text(row.get("message_id")),
                    "thread_id": _text(row.get("thread_id")),
                    "from_role": _text(row.get("from_role")),
                    "summary": _text(row.get("summary")),
                    "status": _text(row.get("status"), "unread"),
                    "message_path": _text(row.get("message_path")),
                }
            )
            value = _text(row.get("message_path"))
            if value:
                receipt_links.add(value)

    for row in thread_rows:
        status = _text(row.get("status")).lower()
        room_kind = _text(row.get("room_kind")).lower()
        if "block" in status or room_kind == "incident":
            blockers.append(
                {
                    "thread_id": _text(row.get("thread_id")),
                    "room_id": _text(row.get("room_id")),
                    "status": _text(row.get("status")),
                    "summary": _text(row.get("latest_summary")),
                    "thread_path": _text(row.get("path")),
                }
            )
            value = _text(row.get("path"))
            if value:
                receipt_links.add(value)

    room_models: list[dict[str, Any]] = []
    for room_id in sorted(owned_room_ids):
        room_capsule_rel = ""
        room_capsule = {}
        explicit_capsule = ""
        for row in inbox_rows:
            if _text(row.get("room_id")) == room_id and _text(row.get("room_capsule_path")):
                explicit_capsule = _text(row.get("room_capsule_path"))
                break
        if explicit_capsule:
            room_capsule_rel = explicit_capsule
            room_capsule = _read_json(shell_root / explicit_capsule)
        if not room_capsule:
            fallback_path = AGENT_COMMS_ROOT / "rooms" / _slug(room_id, "room") / "ROOM_CAPSULE.json"
            if (shell_root / fallback_path).exists():
                room_capsule_rel = fallback_path.as_posix()
                room_capsule = _read_json(shell_root / fallback_path)
        room_profile = _record(rooms_by_id.get(room_id))
        pinned_refs = [*sorted(set(_list(room_capsule.get("source_refs")))), *sorted(set(_list(room_capsule.get("artifact_refs"))))]
        current_message_rel = _text(_record(room_capsule.get("route_deeper_refs")).get("message_path"))
        current_message = _load_message(shell_root, current_message_rel) if current_message_rel else {}
        current_receipts = [
            *_list(current_message.get("receipt_refs")),
            *_list(current_message.get("artifact_refs")),
        ]
        current_directive = {
            "message_id": _text(current_message.get("message_id") or room_capsule.get("latest_message_id")),
            "message_kind": _text(current_message.get("message_kind"), "thread_note"),
            "subject": _text(current_message.get("subject")),
            "summary": _text(current_message.get("summary") or room_capsule.get("latest_summary")),
            "expected_reply_shape": "task_return_with_receipts"
            if bool(current_message.get("requires_response"))
            else "ack_or_followup",
            "receipt_links": current_receipts,
            "message_path": current_message_rel,
        }
        room_models.append(
            {
                "room_header": {
                    "room_id": room_id,
                    "room_kind": _text(room_capsule.get("room_kind") or room_profile.get("room_kind"), "main"),
                    "channel_id": _text(room_capsule.get("channel_id") or room_profile.get("channel_id")),
                    "purpose": _text(room_profile.get("purpose")),
                    "participants": _list(room_capsule.get("participants")),
                    "thread_count": int(room_capsule.get("thread_count") or len(_list(room_capsule.get("thread_ids")))),
                    "latest_summary": _text(room_capsule.get("latest_summary")),
                    "room_capsule_path": room_capsule_rel,
                },
                "pinned_context_refs": pinned_refs[:16],
                "current_directive": current_directive,
            }
        )
        if room_capsule_rel:
            receipt_links.add(room_capsule_rel)
        if current_message_rel:
            receipt_links.add(current_message_rel)
        for value in current_receipts:
            if value:
                receipt_links.add(value)

    queue_payload = _read_json(shell_root / "ION/05_context/current/ACTIVE_CARRIER_MESSAGE_QUEUE.json")
    queue_rows = _queue_rows(queue_payload)
    carrier_rows = queue_rows[-max_carrier_scan:]
    alias_tokens = {
        _slug(role, "role"),
        _slug(role.replace("role.", ""), "role"),
        _slug(_text(role_profile.get("display_name")), "role"),
        _slug(_text(role_profile.get("mention")).lstrip("@"), "role"),
    }
    carrier_mentions: list[dict[str, Any]] = []
    for row in carrier_rows:
        recipient = normalize_role_id(row.get("recipient"))
        body = _text(row.get("body")).lower()
        role_token_hit = any(f"@{token}" in body for token in alias_tokens if token)
        if recipient not in {role, "broadcast"} and not role_token_hit:
            continue
        carrier_mentions.append(
            {
                "message_id": _text(row.get("message_id")),
                "sender_carrier_id": _text(row.get("sender_carrier_id")),
                "recipient": _text(row.get("recipient")),
                "channel": _text(row.get("channel")),
                "message_type": _text(row.get("message_type")),
                "status": _text(row.get("status"), "pending"),
                "created_at": _text(row.get("created_at")),
                "packet_path": _text(row.get("packet_path")),
                "receipt_refs": _list(row.get("receipt_refs")),
                "context_refs": _list(row.get("context_refs")),
            }
        )
        for key in ("packet_path",):
            value = _text(row.get(key))
            if value:
                receipt_links.add(value)
        for value in _list(row.get("receipt_refs")):
            receipt_links.add(value)

    unread_count = 0
    acked_count = 0
    deferred_count = 0
    for row in inbox_rows:
        status = _text(row.get("status"), "unread").lower()
        if "defer" in status:
            deferred_count += 1
        elif status in {"read", "acknowledged", "answered", "settled", "archived"}:
            acked_count += 1
        else:
            unread_count += 1

    warnings: list[dict[str, Any]] = []
    if not inbox_dir.exists():
        warnings.append({"code": "missing_inbox_for_role", "detail": inbox_dir.as_posix()})
    if not message_index:
        warnings.append({"code": "missing_message_index", "detail": MESSAGE_INDEX_PATH.as_posix()})
    if len(indexed_messages) > max_index_scan:
        warnings.append(
            {
                "code": "message_index_scan_limited",
                "detail": f"scanned {max_index_scan} of {len(indexed_messages)} indexed messages",
            }
        )
    if inbox_count > max_inbox_scan:
        warnings.append(
            {
                "code": "inbox_scan_limited",
                "detail": f"scanned {max_inbox_scan} of {inbox_count} inbox rows",
            }
        )
    if thread_count > max_thread_scan:
        warnings.append(
            {
                "code": "thread_scan_limited",
                "detail": f"scanned {max_thread_scan} of {thread_count} thread rows",
            }
        )
    if len(queue_rows) > max_carrier_scan:
        warnings.append(
            {
                "code": "carrier_queue_scan_limited",
                "detail": f"scanned {max_carrier_scan} of {len(queue_rows)} carrier messages",
            }
        )
    for room in room_models:
        if not _text(_record(room.get("room_header")).get("room_capsule_path")):
            warnings.append(
                {
                    "code": "missing_room_capsule",
                    "detail": _text(_record(room.get("room_header")).get("room_id"), "unknown_room"),
                }
            )

    mounted_phase = _text(mounted_role_phase)
    if not mounted_phase and role in {"role.codex_carrier_steward", "role.codex"}:
        mounted_phase = _phase_from_codex_mini(shell_root)
    if not mounted_phase:
        mounted_phase = "unknown"

    scout_context_card = _build_context_read_order(
        shell_root,
        role=role,
        max_inbox_scan=max_inbox_scan,
        max_thread_scan=max_thread_scan,
        max_index_scan=max_index_scan,
        max_carrier_scan=max_carrier_scan,
    )
    self_improvement_loop = _build_self_improvement_loop(
        role=role,
        blockers=blockers,
        warnings=warnings,
        directives=room_models,
    )

    result = {
        "schema_id": AGENT_HOME_VIEW_SCHEMA_ID,
        "ok": True,
        "protocol_ref": WORKSPACE_PROTOCOL_PATH.as_posix(),
        "identity": {
            "carrier_id": _text(carrier_id, "UNKNOWN_CARRIER"),
            "assigned_role": role,
            "mounted_role_phase": mounted_phase,
            "context_package_id": _text(context_package_id or _default_context_package_id(shell_root), "unknown"),
            "authority_flags": {
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
            },
        },
        "attention": {
            "direct_mentions": direct_mentions[:80],
            "role_mentions": role_mentions[:80],
            "carrier_mentions": carrier_mentions[:80],
            "owned_threads": [
                {
                    "thread_id": _text(row.get("thread_id")),
                    "room_id": _text(row.get("room_id")),
                    "room_kind": _text(row.get("room_kind")),
                    "status": _text(row.get("status"), "active"),
                    "latest_summary": _text(row.get("latest_summary")),
                    "unread_for_role": int(_record(row.get("unread_by_role")).get(role) or 0),
                    "thread_path": _text(row.get("path")),
                    "room_capsule_path": _text(row.get("room_capsule_path")),
                }
                for row in thread_rows[:80]
            ],
            "blockers_waiting_on_me": blockers[:80],
            "operator_escalations": [row for row in direct_mentions if _text(row.get("from_role")) == "operator"][:40],
            "pinned_current_directives": room_models[:40],
            "unread_ack_defer_state": {
                "unread_count": unread_count,
                "acknowledged_or_read_count": acked_count,
                "deferred_count": deferred_count,
            },
            "partial_visibility_warnings": warnings,
        },
        "receipt_links": sorted(receipt_links)[:200],
        "context_read_order": _list(scout_context_card.get("context_read_order")),
        "scout_context_card": scout_context_card,
        "self_improvement_loop": self_improvement_loop,
        "source_surfaces": {
            "files": sorted(
                {
                    COMMUNICATION_DIRECTORY_PATH.as_posix(),
                    MESSAGE_INDEX_PATH.as_posix(),
                    "ION/05_context/current/ACTIVE_CARRIER_MESSAGE_QUEUE.json",
                    _rel(inbox_dir, shell_root) if inbox_dir.exists() else "",
                    *[
                        _text(_record(room.get("room_header")).get("room_capsule_path"))
                        for room in room_models
                        if _text(_record(room.get("room_header")).get("room_capsule_path"))
                    ],
                }
                - {""}
            ),
            "transport_preserved": ["carrier_message_send", "carrier_message_poll", "carrier_message_ack"],
            "not_used_for_orientation": [(AGENT_COMMS_ROOT / "logs/messages.jsonl").as_posix()],
        },
        "non_claims": {
            "accepted_state": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
        "updated_at": _now(),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }

    if write_projection:
        projection_path = (
            shell_root
            / AGENT_COMMS_ROOT
            / "projections"
            / f"agent_home_view_{_slug(role.replace('role.', ''), 'role')}.json"
        )
        scout_card_path = (
            shell_root
            / AGENT_COMMS_ROOT
            / "projections"
            / f"agent_home_view_scout_context_card_{_slug(role.replace('role.', ''), 'role')}.json"
        )
        loop_path = (
            shell_root
            / AGENT_COMMS_ROOT
            / "projections"
            / f"agent_home_view_self_improvement_{_slug(role.replace('role.', ''), 'role')}.json"
        )
        _write_json(projection_path, result)
        _write_json(scout_card_path, scout_context_card)
        _write_json(loop_path, self_improvement_loop)
        result["projection_path"] = _rel(projection_path, shell_root)
        result["scout_context_card_path"] = _rel(scout_card_path, shell_root)
        result["self_improvement_loop_path"] = _rel(loop_path, shell_root)
    return result


def run_agent_home_view_smoke(
    root: str | Path | None,
    *,
    role_id: str,
    carrier_id: str = "CODEX_CLI_CARRIER",
) -> dict[str, Any]:
    shell_root = _root(root)
    view = build_agent_home_view(
        shell_root,
        role_id=role_id,
        carrier_id=carrier_id,
        write_projection=True,
    )
    surfaces = set(_list(_record(view.get("source_surfaces")).get("files")))
    forbidden_surface = (AGENT_COMMS_ROOT / "logs/messages.jsonl").as_posix()
    used_full_log = forbidden_surface in surfaces
    oriented = bool(
        _record(view.get("identity")).get("assigned_role")
        and (
            _record(view.get("attention")).get("direct_mentions")
            or _record(view.get("attention")).get("role_mentions")
            or _record(view.get("attention")).get("carrier_mentions")
            or _record(view.get("attention")).get("owned_threads")
            or _record(view.get("attention")).get("pinned_current_directives")
        )
    )
    result = {
        "schema_id": AGENT_HOME_VIEW_SMOKE_SCHEMA_ID,
        "ok": bool(view.get("ok")) and oriented and not used_full_log,
        "role_id": normalize_role_id(role_id),
        "carrier_id": carrier_id,
        "oriented_without_full_log_polling": oriented and not used_full_log,
        "used_full_log_polling": used_full_log,
        "full_log_path": forbidden_surface,
        "projection_path": _text(view.get("projection_path")),
        "source_surfaces": sorted(surfaces),
        "warning_count": len(_list(_record(view.get("attention")).get("partial_visibility_warnings"))),
        "updated_at": _now(),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }
    smoke_path = (
        shell_root
        / AGENT_COMMS_ROOT
        / "projections"
        / f"agent_home_view_smoke_{_slug(role_id.replace('role.', ''), 'role')}.json"
    )
    _write_json(smoke_path, result)
    result["smoke_receipt_path"] = _rel(smoke_path, shell_root)
    return result
