"""Operational graph projection for ION Agent Comms threads.

This module turns filesystem-first Team Comms threads into a UI-safe graph of
objective, route, context, scheduler lifecycle, proof, and accepted-state boundary.
It never mutates comms state.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

SCHEMA_ID = "ion.agent_comms.thread_operational_graph.v1"
ROUTE_NODE_SCHEMA_ID = "ion.agent_comms.operational_route_node.v1"
ROUTE_EDGE_SCHEMA_ID = "ion.agent_comms.operational_route_edge.v1"
THREAD_LIFECYCLE_STEPS = ("INTAKE", "ROUTED", "DISPATCHED", "RETURNED", "AUDITED", "SETTLED")
SCHEDULER_LIFECYCLE_STEPS = ("FUTURE_CANDIDATE", "READY", "CLAIMED", "IN_FLIGHT", "ENACTED_UNLANDED", "COMPLETED")


def _shell_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "ION/05_context").exists():
            return path
        if (path / "05_context").exists() and (path / "REPO_AUTHORITY.md").exists():
            return path.parent
    return candidate


def _safe_id(value: Any, fallback: str = "item") -> str:
    text = str(value or "").strip().lower()
    out = []
    for char in text:
        if char.isalnum() or char in "._-":
            out.append(char)
        else:
            out.append("_")
    rendered = "".join(out).strip("._-")
    return rendered[:96] or fallback


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
    if value is None:
        return []
    return [value]


def _message_text(message: Mapping[str, Any]) -> str:
    return str(message.get("body") or message.get("summary") or message.get("subject") or "")


def _message_summary(message: Mapping[str, Any], limit: int = 240) -> str:
    text = " ".join(_message_text(message).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def _find_default_thread(root: Path, *, preferred_text: str | None = None) -> str:
    from .ion_agent_comms import list_agent_threads

    preferred = (preferred_text or "pristine post-patch").lower()
    result = list_agent_threads(root, limit=200)
    threads = [thread for thread in _as_list(result.get("threads")) if isinstance(thread, Mapping)]
    for thread in threads:
        haystack = " ".join(
            str(thread.get(field) or "")
            for field in ("thread_id", "subject", "latest_summary", "mission", "channel_id")
        ).lower()
        if preferred and preferred in haystack:
            return str(thread.get("thread_id") or "")
    for thread in threads:
        if str(thread.get("channel_id") or "") == "team":
            return str(thread.get("thread_id") or "")
    return str(threads[0].get("thread_id") or "") if threads else ""


def _node(role: str, *, label: str | None = None, node_type: str = "agent", detail: str = "") -> dict[str, Any]:
    return {
        "schema_id": ROUTE_NODE_SCHEMA_ID,
        "node_id": _safe_id(role, "node"),
        "node_type": node_type,
        "label": label or role,
        "detail": detail,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def _edge(from_node: str, to_node: str, edge_type: str, *, message_id: str = "", label: str = "") -> dict[str, Any]:
    return {
        "schema_id": ROUTE_EDGE_SCHEMA_ID,
        "edge_id": f"{_safe_id(from_node)}__{edge_type.lower()}__{_safe_id(to_node)}__{_safe_id(message_id, 'edge')}",
        "from_node": _safe_id(from_node),
        "to_node": _safe_id(to_node),
        "edge_type": edge_type,
        "message_id": message_id,
        "label": label or edge_type.replace("_", " ").title(),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def _thread_lifecycle(thread: Mapping[str, Any], messages: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    kinds = {str(message.get("message_kind") or "") for message in messages}
    statuses = {str(message.get("status") or "") for message in messages}
    route_roles = {
        str(message.get("from_role") or "")
        for message in messages
        if str(message.get("from_role") or "")
    }
    has_dispatch = bool(kinds & {"task_dispatch", "decision_request", "handoff"})
    has_answer = bool(kinds & {"answer", "receipt", "audit"})
    has_auditish = any(
        "audit" in _message_text(message).lower()
        or "verify" in _message_text(message).lower()
        or str(message.get("message_kind") or "") == "audit"
        for message in messages
    )
    has_settled = any(status in {"answered", "settled", "archived"} for status in statuses)
    path = ["INTAKE"]
    if len(route_roles) > 1 or has_dispatch:
        path.append("ROUTED")
    if has_dispatch:
        path.append("DISPATCHED")
    if has_answer:
        path.append("RETURNED")
    if has_auditish:
        path.append("AUDITED")
    if has_settled:
        path.append("SETTLED")
    current = path[-1]
    return {
        "schema_id": "ion.agent_comms.thread_lifecycle_projection.v1",
        "state": current,
        "path": path,
        "all_steps": list(THREAD_LIFECYCLE_STEPS),
        "message_kind_counts": dict(Counter(str(message.get("message_kind") or "thread_note") for message in messages)),
        "policy": "Thread lifecycle is a workroom/message lifecycle, not mission phase or scheduler state.",
    }


def _followup_contract(messages: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    text = "\n".join(_message_text(message).lower() for message in messages)
    no_followup = "no_followup" in text or "no-followup" in text
    directive = "ion-agent-comms" in text or "directive" in text or "task_dispatch" in {
        str(message.get("message_kind") or "") for message in messages
    }
    decision_mentions = text.count("no_followup") + text.count("no-followup")
    if no_followup and decision_mentions <= 3:
        state = "VALID_NO_FOLLOWUP"
    elif no_followup:
        state = "NO_FOLLOWUP_MENTIONED_REVIEW_DUPLICATE_RISK"
    elif directive:
        state = "DIRECTIVE_PRESENT"
    else:
        state = "MISSING_OR_UNCLEAR"
    return {
        "schema_id": "ion.agent_comms.followup_contract_projection.v1",
        "required": True,
        "state": state,
        "decision_shape": "ion-agent-decision/no_followup" if no_followup else "",
        "directive_observed": directive,
        "no_followup_observed": no_followup,
        "policy": "Agent work should close with exactly one executable comms directive or one no_followup decision.",
    }


def _context_segments(thread: Mapping[str, Any], messages: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    source_refs = sorted(
        {
            str(ref)
            for item in [thread, *messages]
            for ref in _as_list(item.get("source_refs"))
            if str(ref).strip()
        }
    )
    artifact_refs = sorted(
        {
            str(ref)
            for item in [thread, *messages]
            for ref in _as_list(item.get("artifact_refs"))
            if str(ref).strip()
        }
    )
    receipt_refs = sorted(
        {
            str(ref)
            for item in [thread, *messages]
            for ref in _as_list(item.get("receipt_refs"))
            if str(ref).strip()
        }
    )
    participants = sorted({str(role) for role in _as_list(thread.get("participants")) if str(role).strip()})
    return [
        {
            "segment_id": "context.live_thread",
            "label": "Live Thread",
            "window_class": "LIVE_THREAD",
            "state": "loaded",
            "summary": f"{len(messages)} messages in selected workroom.",
            "refs": [str(thread.get("path") or "")] if thread.get("path") else [],
        },
        {
            "segment_id": "context.room_capsule",
            "label": "Room Capsule",
            "window_class": "ROOM_CAPSULE",
            "state": "available" if thread.get("room_capsule_path") else "missing",
            "summary": str(thread.get("room_id") or "room not declared"),
            "refs": [str(thread.get("room_capsule_path") or "")] if thread.get("room_capsule_path") else [],
        },
        {
            "segment_id": "context.agent_context",
            "label": "Agent Context",
            "window_class": "AGENT_CONTEXT",
            "state": "available",
            "summary": ", ".join(participants) or "participants not declared",
            "refs": [],
        },
        {
            "segment_id": "context.domain_weave",
            "label": "Domain Weave",
            "window_class": "DOMAIN_WEAVE",
            "state": "candidate",
            "summary": "agent_communication_systems ↔ codex_carrier_sync ↔ ion_system_definition",
            "refs": source_refs[:8],
        },
        {
            "segment_id": "context.proof_refs",
            "label": "Proof Refs",
            "window_class": "PROOF",
            "state": "available" if receipt_refs or artifact_refs else "candidate",
            "summary": f"{len(receipt_refs)} receipt refs, {len(artifact_refs)} artifact refs.",
            "refs": receipt_refs[:8] + artifact_refs[:8],
        },
        {
            "segment_id": "context.omitted_blocked",
            "label": "Omitted / Blocked",
            "window_class": "OMITTED_OR_BLOCKED",
            "state": "controlled",
            "summary": "Hidden reasoning, secrets, production/live authority, and unrelated cold context are not exposed.",
            "refs": [],
        },
    ]


def _proof_projection(thread: Mapping[str, Any], messages: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    refs = sorted(
        {
            str(ref)
            for item in [thread, *messages]
            for field in ("receipt_refs", "artifact_refs", "source_refs")
            for ref in _as_list(item.get(field))
            if str(ref).strip()
        }
    )
    text = "\n".join(_message_text(message).lower() for message in messages)
    if "audit clean" in text or "clean" in text and "no_followup" in text:
        state = "AUDIT_CLEAN_CANDIDATE"
    elif refs:
        state = "ACCEPTED_AS_EVIDENCE_CANDIDATE"
    else:
        state = "CANDIDATE_RETURN"
    return {
        "schema_id": "ion.agent_comms.thread_proof_projection.v1",
        "proof_state": state,
        "proof_ref_count": len(refs),
        "proof_refs": refs[:24],
        "accepted_state_receipts": [],
        "warnings": [
            "Thread proof is evidence; it does not accept product state by itself.",
        ],
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def build_agent_comms_thread_operational_graph(
    root: str | Path | None = None,
    *,
    thread_id: str | None = None,
    preferred_text: str | None = None,
    limit: int = 200,
) -> dict[str, Any]:
    """Build a selected Team Comms thread operational graph."""

    shell_root = _shell_root(root)
    from .ion_agent_comms import read_agent_thread

    selected_thread_id = thread_id or _find_default_thread(shell_root, preferred_text=preferred_text)
    if not selected_thread_id:
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "finding": "no_agent_comms_thread_available",
            "thread_id": "",
            "nodes": [],
            "edges": [],
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }

    thread_result = read_agent_thread(shell_root, selected_thread_id, limit=limit)
    thread = thread_result.get("thread") if isinstance(thread_result.get("thread"), Mapping) else {}
    messages = [message for message in _as_list(thread_result.get("messages")) if isinstance(message, Mapping)]

    nodes_by_id: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    previous_from = ""
    for message in messages:
        from_role = str(message.get("from_role") or "unknown")
        nodes_by_id.setdefault(_safe_id(from_role), _node(from_role, label=from_role, detail="message author"))
        to_roles = [str(role) for role in _as_list(message.get("to_roles")) if str(role).strip()]
        if not to_roles and previous_from and previous_from != from_role:
            # A response without explicit target still represents a return to the prior route.
            to_roles = [previous_from]
        for role in to_roles:
            nodes_by_id.setdefault(_safe_id(role), _node(role, label=role, detail="message target"))
            edge_type = "DIRECTIVE_TO" if str(message.get("message_kind") or "") == "task_dispatch" else "MESSAGE_TO"
            edges.append(_edge(from_role, role, edge_type, message_id=str(message.get("message_id") or "")))
        previous_from = from_role

    for ref in _proof_projection(thread, messages).get("proof_refs", [])[:6]:
        ref_id = f"receipt:{_safe_id(ref)}"
        nodes_by_id.setdefault(_safe_id(ref_id), _node(ref_id, label="proof ref", node_type="proof", detail=str(ref)))
        if previous_from:
            edges.append(_edge(previous_from, ref_id, "PRODUCED_PROOF", message_id="proof"))

    route_roles = [node.get("label") for node in nodes_by_id.values() if node.get("node_type") == "agent"]
    lifecycle = _thread_lifecycle(thread, messages)
    followup = _followup_contract(messages)
    proof = _proof_projection(thread, messages)

    return {
        "schema_id": SCHEMA_ID,
        "ok": True,
        "thread_id": selected_thread_id,
        "thread": thread,
        "message_count": len(messages),
        "messages": [
            {
                "message_id": str(message.get("message_id") or ""),
                "from_role": str(message.get("from_role") or ""),
                "to_roles": list(message.get("to_roles") or []),
                "message_kind": str(message.get("message_kind") or "thread_note"),
                "created_at": str(message.get("created_at") or ""),
                "summary": _message_summary(message),
                "source_refs": list(message.get("source_refs") or []),
                "artifact_refs": list(message.get("artifact_refs") or []),
                "receipt_refs": list(message.get("receipt_refs") or []),
            }
            for message in messages
        ],
        "parent_scope_id": "mission.team_comms.operational_graph_projection",
        "objective_ref": "objective.pristine_chain_proof",
        "route": {
            "schema_id": "ion.agent_comms.operational_route.v1",
            "nodes": list(nodes_by_id.values()),
            "edges": edges,
            "route_roles": route_roles,
            "edge_count": len(edges),
        },
        "thread_lifecycle": lifecycle,
        "scheduler_lifecycle": {
            "schema_id": "ion.agent_comms.thread_scheduler_lifecycle_hint.v1",
            "state": "COMPLETED_AS_EVIDENCE" if proof.get("proof_state") != "CANDIDATE_RETURN" else "ENACTED_UNLANDED",
            "schedule_state": "ENACTED_UNLANDED",
            "commitment": "ENACTED",
            "all_steps": list(SCHEDULER_LIFECYCLE_STEPS),
            "policy": "Scheduler lifecycle is a projection hint until backed by schedule receipts.",
        },
        "followup_contract": followup,
        "context_segments": _context_segments(thread, messages),
        "proof_projection": proof,
        "accepted_state_boundary": {
            "state": "candidate_evidence_not_accepted_state",
            "summary": "Messages and returns do not become product state without acceptance receipts.",
        },
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }
