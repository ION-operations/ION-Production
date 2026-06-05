"""Agent communication directory and automation comms guardrails.

This module projects who can receive/answer ION agent communication and applies
bounded automation limits before automated prompts create durable comms packets.
It does not run agents, grant live authority, or make accepted-state claims.
"""
from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .ion_agent_comms import AGENT_COMMS_ROOT, default_agent_channels, normalize_role_id

DIRECTORY_SCHEMA_ID = "ion.agent_communication_directory.v1"
CONTACT_CONTRACT_SCHEMA_ID = "ion.agent_contact_contract.v1"
ROOM_CONTRACT_SCHEMA_ID = "ion.agent_room_contract.v1"
AUTOMATION_POLICY_SCHEMA_ID = "ion.agent_comms.automation_policy.v1"
AUTOMATION_CHECK_SCHEMA_ID = "ion.agent_comms.automation_limit_check.v1"
AUTOMATION_USAGE_SCHEMA_ID = "ion.agent_comms.automation_usage.v1"

COMMUNICATION_DIRECTORY_PATH = AGENT_COMMS_ROOT / "COMMUNICATION_DIRECTORY.json"
AUTOMATION_USAGE_LOG = AGENT_COMMS_ROOT / "automation" / "USAGE.jsonl"

DEFAULT_AUTOMATION_COMMS_LIMITS: dict[str, int] = {
    "default_window_minutes": 60,
    "default_prompt_limit": 12,
    "default_time_budget_minutes": 120,
    "default_prompt_char_limit": 6000,
    "max_window_minutes": 1440,
    "max_prompt_limit": 100,
    "max_time_budget_minutes": 1440,
    "max_prompt_char_limit": 20000,
}

DEFAULT_TASK_RUN_LIMITS: dict[str, int] = {
    "max_agents": 8,
    "max_workpacks": 8,
    "max_directives": 3,
    "max_pickups": 12,
    "max_graph_nodes": 180,
    "max_graph_edges": 260,
}

CONTACT_RELATIONSHIP_TAXONOMY: list[str] = [
    "selected_domain_peer",
    "shared_domain_peer",
    "orchestration_escalation",
    "packet_relay",
    "implementation_or_runtime",
    "context_or_continuity",
    "ion_system_definition",
    "canon_or_template_law",
    "review_or_dissent",
    "operator_interface",
    "evidence_history_or_receipts",
    "general_available_contact",
    "self",
]

CONTACT_GROUP_TAGS: dict[str, str] = {
    "selected_domain_peers": "selected_domain_peer",
    "shared_domain_peers": "shared_domain_peer",
    "orchestration": "orchestration_escalation",
    "relay": "packet_relay",
    "review": "review_or_dissent",
    "implementation_runtime": "implementation_or_runtime",
    "context_continuity": "context_or_continuity",
    "ion_system_definition": "ion_system_definition",
    "canon_template": "canon_or_template_law",
    "operator_interface": "operator_interface",
    "evidence_history_receipts": "evidence_history_or_receipts",
}

CONTACT_ROUTING_RULES: list[dict[str, str]] = [
    {
        "need": "orchestration_or_blocker",
        "contact_group": "orchestration",
        "default_channel": "steward_ops",
        "template_hint": "agent_workpack_decision",
    },
    {
        "need": "packet_boundary_or_operator_reexpression",
        "contact_group": "relay",
        "default_channel": "relay",
        "template_hint": "agent_comms_decision",
    },
    {
        "need": "implementation_runtime_or_codex_carrier_work",
        "contact_group": "implementation_runtime",
        "default_channel": "team",
        "template_hint": "agent_workpack_decision",
    },
    {
        "need": "context_capsule_route_or_continuity_question",
        "contact_group": "context_continuity",
        "default_channel": "handoffs",
        "template_hint": "domain_context_review",
    },
    {
        "need": "ION_protocol_or_domain_definition_question",
        "contact_group": "ion_system_definition",
        "default_channel": "team",
        "template_hint": "domain_context_review",
    },
    {
        "need": "risk_dissent_release_or_truth_review",
        "contact_group": "review",
        "default_channel": "audit",
        "template_hint": "audit_review",
    },
    {
        "need": "canon_template_or_registry_law_change",
        "contact_group": "canon_template",
        "default_channel": "gates",
        "template_hint": "domain_context_review",
    },
    {
        "need": "receipt_status_or_historical_evidence",
        "contact_group": "evidence_history_receipts",
        "default_channel": "signals",
        "template_hint": "agent_comms_decision",
    },
]

CONTACT_TEMPLATE_CONTRACTS: dict[str, dict[str, Any]] = {
    "agent_comms_decision": {
        "template_id": "agent_comms_decision",
        "intent": "Ask an available agent for a bounded communication decision or answer.",
        "dispatch_modes": ["comms_only", "prepare_workpack", "queue_workpack"],
        "directive_schema_id": "ion.agent_comms.directive.v1",
        "required_fields": ["from_role", "agent", "template_id", "objective", "body", "source_refs"],
        "recommended_message_kind": "agent_question",
        "requires_source_refs": True,
        "candidate_only": True,
    },
    "agent_workpack_decision": {
        "template_id": "agent_workpack_decision",
        "intent": "Route a specialist workpack to another agent for a bounded return.",
        "dispatch_modes": ["prepare_workpack", "queue_workpack", "start_workpack"],
        "directive_schema_id": "ion.agent_comms.directive.v1",
        "required_fields": ["from_role", "agent", "template_id", "dispatch_mode", "objective", "body", "source_refs"],
        "recommended_message_kind": "workpack_request",
        "requires_source_refs": True,
        "candidate_only": True,
    },
    "domain_context_review": {
        "template_id": "domain_context_review",
        "intent": "Ask a domain/context specialist to review domain fit, capsule context, or routing evidence.",
        "dispatch_modes": ["prepare_workpack", "queue_workpack"],
        "directive_schema_id": "ion.agent_comms.directive.v1",
        "required_fields": ["from_role", "agent", "template_id", "objective", "body", "source_refs"],
        "recommended_message_kind": "domain_review_request",
        "requires_source_refs": True,
        "candidate_only": True,
    },
    "audit_review": {
        "template_id": "audit_review",
        "intent": "Ask a review/dissent agent to audit claims, receipts, or release risk.",
        "dispatch_modes": ["prepare_workpack", "queue_workpack"],
        "directive_schema_id": "ion.agent_comms.directive.v1",
        "required_fields": ["from_role", "agent", "template_id", "objective", "body", "source_refs"],
        "recommended_message_kind": "audit_request",
        "requires_source_refs": True,
        "candidate_only": True,
    },
}

CONTACT_ESCALATION_ROUTES: list[dict[str, Any]] = [
    {
        "route_id": "orchestration",
        "relationship_tag": "orchestration_escalation",
        "preferred_roles": ["role.steward"],
        "default_template_id": "agent_workpack_decision",
    },
    {
        "route_id": "relay",
        "relationship_tag": "packet_relay",
        "preferred_roles": ["role.relay"],
        "default_template_id": "agent_comms_decision",
    },
    {
        "route_id": "review",
        "relationship_tag": "review_or_dissent",
        "preferred_roles": ["role.nemesis", "role.vice", "role.nemesis_reviewer"],
        "default_template_id": "audit_review",
    },
    {
        "route_id": "context_continuity",
        "relationship_tag": "context_or_continuity",
        "preferred_roles": ["role.context_cartographer", "role.vizier"],
        "default_template_id": "domain_context_review",
    },
    {
        "route_id": "ion_system_definition",
        "relationship_tag": "ion_system_definition",
        "preferred_roles": ["role.ionologist"],
        "default_template_id": "domain_context_review",
    },
    {
        "route_id": "implementation_runtime",
        "relationship_tag": "implementation_or_runtime",
        "preferred_roles": ["role.mason", "role.codex_carrier_steward", "role.runtime_cartographer"],
        "default_template_id": "agent_workpack_decision",
    },
]

ROOM_KIND_CONTRACTS: list[dict[str, Any]] = [
    {
        "room_kind": "main",
        "purpose": "Shared visible rooms for operator intake, team coordination, relay, gates, and status.",
        "default_visibility": "team_projection",
        "summary_required": False,
        "route_deeper_default": "thread_when_evidence_needed",
    },
    {
        "room_kind": "mission",
        "purpose": "Task or run-specific working rooms that gather a multi-agent chain around one objective.",
        "default_visibility": "mission_participants",
        "summary_required": True,
        "route_deeper_default": "room_capsule_then_thread",
    },
    {
        "room_kind": "domain",
        "purpose": "Domain-owned rooms for specialists maintaining a domain, capsule, or route family.",
        "default_visibility": "domain_participants",
        "summary_required": True,
        "route_deeper_default": "room_capsule_then_domain_refs",
    },
    {
        "room_kind": "direct",
        "purpose": "Agent-to-agent direct room for a focused question or pair decision.",
        "default_visibility": "direct_agent_pair",
        "summary_required": True,
        "route_deeper_default": "room_capsule_then_latest_message",
    },
    {
        "room_kind": "audit",
        "purpose": "Dissent, proof, template, risk, and receipt review rooms.",
        "default_visibility": "audit_projection",
        "summary_required": True,
        "route_deeper_default": "room_capsule_then_receipts",
    },
    {
        "room_kind": "handoff",
        "purpose": "Role-to-role handoff rooms with exact refs, blockers, and requested next action.",
        "default_visibility": "handoff_participants",
        "summary_required": True,
        "route_deeper_default": "room_capsule_then_handoff_packet",
    },
    {
        "room_kind": "incident",
        "purpose": "Blocker or outage rooms that must report back to the main team room.",
        "default_visibility": "incident_participants",
        "summary_required": True,
        "route_deeper_default": "room_capsule_then_audit_refs",
    },
]

ROOM_ROUTING_RULES: list[dict[str, Any]] = [
    {
        "need": "operator_intake_or_user_visible_report",
        "room_kind": "main",
        "default_room_id": "room.channel.front_door",
        "channel_id": "front_door",
    },
    {
        "need": "team_wide_mission_report_or_steward_broadcast",
        "room_kind": "main",
        "default_room_id": "room.main.team",
        "channel_id": "team",
    },
    {
        "need": "agent_pair_question_or_specialist_reply",
        "room_kind": "direct",
        "default_room_id": "computed_from_participants",
        "channel_id": "computed_dm_channel",
    },
    {
        "need": "domain_specialist_coordination",
        "room_kind": "domain",
        "default_room_id": "room.domain.<domain_id>",
        "channel_id": "domain_<domain_id>",
    },
    {
        "need": "bounded_multi_agent_work_chain",
        "room_kind": "mission",
        "default_room_id": "room.mission.<mission_or_run_id>",
        "channel_id": "mission_<mission_or_run_id>",
    },
    {
        "need": "proof_risk_or_template_dissent",
        "room_kind": "audit",
        "default_room_id": "room.audit",
        "channel_id": "audit",
    },
    {
        "need": "role_handoff_or_context_transfer",
        "room_kind": "handoff",
        "default_room_id": "room.handoff",
        "channel_id": "handoffs",
    },
]

ROOM_REPORTING_RULES: list[dict[str, Any]] = [
    {
        "room_kind": "direct",
        "report_to_room_id": "room.main.team",
        "rule": "Direct agent rooms keep details compact and report decisions or blockers back to the main team room when relevant.",
    },
    {
        "room_kind": "domain",
        "report_to_room_id": "room.main.team",
        "rule": "Domain rooms report promotions, blockers, or cross-domain decisions back to the main team room.",
    },
    {
        "room_kind": "mission",
        "report_to_room_id": "room.main.team",
        "rule": "Mission rooms maintain a room capsule and publish mission-close summaries to the main team room.",
    },
    {
        "room_kind": "audit",
        "report_to_room_id": "room.main.team",
        "rule": "Audit rooms report clean/blocking findings to the main team room without creating accepted-state authority.",
    },
    {
        "room_kind": "handoff",
        "report_to_room_id": "room.main.team",
        "rule": "Handoff rooms keep transfer details and report ownership changes back to the main team room.",
    },
    {
        "room_kind": "incident",
        "report_to_room_id": "room.main.team",
        "rule": "Incident rooms report resolution, blockers, and follow-up owners back to the main team room.",
    },
]


def _now_dt() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _now() -> str:
    return _now_dt().isoformat()


def _resolve_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    return candidate


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


def _int(value: Any, fallback: int, *, lower: int, upper: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = fallback
    return max(lower, min(number, upper))


def _role_slug(role_id: str) -> str:
    normalized = normalize_role_id(role_id) or "role.unknown"
    return normalized.replace("role.", "role_").replace(".", "_").replace("/", "_")


def _alias_token(value: Any) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in str(value or "").strip().lower().lstrip("@")).strip("._-")


def _agent_aliases(role_id: str, display_name: Any = "") -> list[str]:
    role = normalize_role_id(role_id)
    display = str(display_name or "").strip()
    values = [
        role,
        role.replace("role.", "", 1),
        role.replace(".", "_"),
        display,
        display.replace(" ", "_"),
    ]
    aliases: list[str] = []
    seen: set[str] = set()
    for value in values:
        alias = _alias_token(value)
        if alias and alias not in seen:
            seen.add(alias)
            aliases.append(alias)
    return aliases


def _parse_time(value: Any) -> datetime | None:
    text = str(value or "").strip()
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


def _agent_domain_ids(agent: Mapping[str, Any]) -> list[str]:
    mount = _record(agent.get("native_codex_mount"))
    ids = [_text(agent.get("registry_primary_domain")), _text(mount.get("domain_id"))]
    ids.extend(_list(agent.get("registry_secondary_domains")))
    seen: set[str] = set()
    return [item for item in ids if item and not (item in seen or seen.add(item))]


def _profile_domain_ids(profile: Mapping[str, Any]) -> list[str]:
    values: list[str] = []
    primary = _text(profile.get("primary_domain"))
    if primary:
        values.append(primary)
    for value in profile.get("domain_ids") or []:
        text = _text(value)
        if text and text not in values:
            values.append(text)
    return values


def contact_relationship_tags(
    role_id: str,
    contact: Mapping[str, Any],
    *,
    own_domains: Sequence[str],
    selected_domain: str,
) -> list[str]:
    contact_role = normalize_role_id(contact.get("role_id") or "")
    contact_domains = _profile_domain_ids(contact)
    tags: list[str] = []
    if selected_domain and selected_domain in contact_domains:
        tags.append("selected_domain_peer")
    if any(domain in own_domains for domain in contact_domains):
        tags.append("shared_domain_peer")
    if contact_role == "role.steward":
        tags.append("orchestration_escalation")
    if contact_role == "role.relay":
        tags.append("packet_relay")
    if contact_role in {"role.nemesis", "role.vice", "role.nemesis_reviewer"}:
        tags.append("review_or_dissent")
    if contact_role in {"role.mason", "role.codex_carrier_steward", "role.runtime_cartographer"}:
        tags.append("implementation_or_runtime")
    if contact_role in {"role.context_cartographer", "role.vizier"}:
        tags.append("context_or_continuity")
    if contact_role == "role.ionologist":
        tags.append("ion_system_definition")
    if contact_role in {"role.canon_librarian", "role.template_curator"}:
        tags.append("canon_or_template_law")
    if contact_role == "role.persona_interface":
        tags.append("operator_interface")
    if contact_role in {"role.atlas", "role.thoth", "role.vestige", "role.scribe"}:
        tags.append("evidence_history_or_receipts")
    if contact_role == normalize_role_id(role_id):
        tags.append("self")
    return tags or ["general_available_contact"]


def contact_groups_from_contacts(contacts: Sequence[Mapping[str, Any]]) -> dict[str, list[str]]:
    return {
        group_id: [str(row.get("role_id") or "") for row in contacts if tag in list(row.get("relationship_tags") or [])]
        for group_id, tag in CONTACT_GROUP_TAGS.items()
    }


def _contact_role_profile(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "role_id": row.get("role_id"),
        "display_name": row.get("display_name"),
        "mention": row.get("mention"),
        "aliases": list(row.get("aliases") or []),
        "primary_domain": row.get("primary_domain"),
        "domain_ids": _profile_domain_ids(row),
        "available_for_comms": bool(row.get("available_for_comms")),
        "can_initiate_comms": bool(row.get("can_initiate_comms")),
        "can_receive_workpacks": bool(row.get("can_receive_workpacks")),
        "default_channels": list(row.get("default_channels") or []),
        "template_ids": list(row.get("start_comms_template_ids") or row.get("handoff_template_ids") or []),
        "communication_contract": dict(row.get("communication_contract") or {}),
    }


def _contact_entry(row: Mapping[str, Any], tags: Sequence[str]) -> dict[str, Any]:
    entry = _contact_role_profile(row)
    entry["relationship_tags"] = list(tags)
    entry["contract_ref"] = f"agents_by_role.{entry.get('role_id')}.communication_contract"
    return entry


def _aliases_by_token(agent_rows: Sequence[Mapping[str, Any]]) -> tuple[dict[str, str], dict[str, list[str]]]:
    aliases_by_token: dict[str, str] = {}
    conflicts: dict[str, set[str]] = {}
    for row in agent_rows:
        role_id = normalize_role_id(row.get("role_id") or "")
        if not role_id:
            continue
        tokens = list(row.get("aliases") or [])
        tokens.extend([row.get("mention"), role_id])
        for token_value in tokens:
            token = _alias_token(token_value)
            if not token:
                continue
            existing = aliases_by_token.get(token)
            if existing and existing != role_id:
                conflicts.setdefault(token, {existing}).add(role_id)
                continue
            aliases_by_token[token] = role_id
    return aliases_by_token, {token: sorted(values) for token, values in conflicts.items()}


def build_agent_contact_contract(
    *,
    agents: Sequence[Mapping[str, Any]],
    domains: Sequence[Mapping[str, Any]],
    generated_at: str | None = None,
    automation_policy: Mapping[str, Any] | None = None,
    task_run_policy: Mapping[str, Any] | None = None,
    start_comms: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    agent_rows = [dict(agent) for agent in agents if isinstance(agent, Mapping)]
    available_rows = [row for row in agent_rows if row.get("available_for_comms")]
    aliases_by_token, alias_conflicts = _aliases_by_token(agent_rows)
    contacts_by_role: dict[str, list[dict[str, Any]]] = {}
    contact_groups_by_role: dict[str, dict[str, list[str]]] = {}
    contact_edges: list[dict[str, Any]] = []
    for source in agent_rows:
        source_role = normalize_role_id(source.get("role_id") or "")
        if not source_role:
            continue
        own_domains = _profile_domain_ids(source)
        selected_domain = _text(source.get("primary_domain"))
        source_contacts: list[dict[str, Any]] = []
        for target in available_rows:
            target_role = normalize_role_id(target.get("role_id") or "")
            tags = contact_relationship_tags(source_role, target, own_domains=own_domains, selected_domain=selected_domain)
            if "self" in tags:
                continue
            contact = _contact_entry(target, tags)
            source_contacts.append(contact)
            contact_edges.append(
                {
                    "from_role": source_role,
                    "to_role": target_role,
                    "relationship_tags": list(tags),
                    "template_ids": list(contact.get("template_ids") or []),
                    "can_receive_workpacks": bool(target.get("can_receive_workpacks")),
                }
            )
        contacts_by_role[source_role] = source_contacts
        contact_groups_by_role[source_role] = contact_groups_from_contacts(source_contacts)

    available_role_ids = {normalize_role_id(row.get("role_id") or "") for row in available_rows}
    escalation_routes = []
    for route in CONTACT_ESCALATION_ROUTES:
        preferred = [role for role in route["preferred_roles"] if role in available_role_ids]
        escalation_routes.append({**route, "available_roles": preferred})

    domains_by_id = {}
    for domain in domains:
        domain_id = _text(domain.get("domain_id"))
        if not domain_id:
            continue
        domain_agents = [dict(row) for row in list(domain.get("agents") or []) if isinstance(row, Mapping)]
        domains_by_id[domain_id] = {
            "domain_id": domain_id,
            "display_name": domain.get("display_name") or domain_id,
            "available_agent_roles": [row.get("role_id") for row in domain_agents if row.get("available_for_comms")],
            "workpack_agent_roles": [row.get("role_id") for row in domain_agents if row.get("can_receive_workpacks")],
            "agent_count": len(domain_agents),
        }

    return {
        "schema_id": CONTACT_CONTRACT_SCHEMA_ID,
        "generated_at": generated_at or _now(),
        "source_directory_path": COMMUNICATION_DIRECTORY_PATH.as_posix(),
        "agent_count": len(agent_rows),
        "available_agent_count": len(available_rows),
        "contact_edge_count": len(contact_edges),
        "agents_by_role": {normalize_role_id(row.get("role_id") or ""): _contact_role_profile(row) for row in agent_rows if row.get("role_id")},
        "aliases_by_token": aliases_by_token,
        "alias_conflicts": alias_conflicts,
        "domains_by_id": domains_by_id,
        "contacts_by_role": contacts_by_role,
        "contact_groups_by_role": contact_groups_by_role,
        "contact_edges": contact_edges,
        "relationship_taxonomy": list(CONTACT_RELATIONSHIP_TAXONOMY),
        "routing_rules": deepcopy(CONTACT_ROUTING_RULES),
        "template_contracts": deepcopy(CONTACT_TEMPLATE_CONTRACTS),
        "escalation_routes": escalation_routes,
        "automation_comms_policy_ref": dict(automation_policy or {}),
        "task_run_policy_ref": dict(task_run_policy or {}),
        "start_comms_ref": dict(start_comms or {}),
        "agent_decision_boundary": "Agents choose who to contact from this contract and write visible @mentions or ion-agent-comms directives. Automation only validates limits and carries packets.",
        "routing_source_of_truth": "COMMUNICATION_DIRECTORY.json#contact_contract",
        "policy": "This contact contract is the canonical peer-discovery, routing, template, and escalation contract for agent comms; it is not a fake agent simulation.",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def _room_channel_id_for_domain(domain_id: str) -> str:
    return _alias_token(f"domain_{domain_id}") or "domain_general"


def _room_id_for_domain(domain_id: str) -> str:
    return _alias_token(f"room.domain.{domain_id}") or "room.domain.general"


def build_agent_room_contract(
    *,
    agents: Sequence[Mapping[str, Any]],
    domains: Sequence[Mapping[str, Any]],
    generated_at: str | None = None,
    contact_contract: Mapping[str, Any] | None = None,
    start_comms: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    agent_rows = [dict(agent) for agent in agents if isinstance(agent, Mapping)]
    domain_rows = [dict(domain) for domain in domains if isinstance(domain, Mapping)]
    default_rooms: list[dict[str, Any]] = [
        {
            "room_id": "room.channel.front_door",
            "room_kind": "main",
            "channel_id": "front_door",
            "display_name": "Front Door",
            "purpose": "Operator-facing intake and Persona/Relay packet boundary.",
            "default_participants": ["operator", "role.persona_interface", "role.relay"],
            "report_to_room_id": "",
            "visibility": "team_projection",
            "summary_required": False,
        },
        {
            "room_id": "room.main.team",
            "room_kind": "main",
            "channel_id": "team",
            "display_name": "Team",
            "purpose": "Main team coordination, mission reports, and cross-domain status.",
            "default_participants": ["role.steward", "role.mason", "role.ionologist", "role.codex_carrier_steward"],
            "report_to_room_id": "",
            "visibility": "team_projection",
            "summary_required": False,
        },
        {
            "room_id": "room.channel.relay",
            "room_kind": "main",
            "channel_id": "relay",
            "display_name": "Relay",
            "purpose": "Packet relay, re-expression, and boundary control.",
            "default_participants": ["role.relay", "role.steward", "operator"],
            "report_to_room_id": "room.main.team",
            "visibility": "team_projection",
            "summary_required": False,
        },
        {
            "room_id": "room.channel.steward_ops",
            "room_kind": "main",
            "channel_id": "steward_ops",
            "display_name": "Steward Ops",
            "purpose": "Orchestration routing, dependency waits, and worker status.",
            "default_participants": ["role.steward", "role.relay"],
            "report_to_room_id": "room.main.team",
            "visibility": "team_projection",
            "summary_required": False,
        },
        {
            "room_id": "room.handoff",
            "room_kind": "handoff",
            "channel_id": "handoffs",
            "display_name": "Handoffs",
            "purpose": "Role-to-role context and ownership transfer.",
            "default_participants": ["role.steward"],
            "report_to_room_id": "room.main.team",
            "visibility": "handoff_participants",
            "summary_required": True,
        },
        {
            "room_id": "room.channel.signals",
            "room_kind": "main",
            "channel_id": "signals",
            "display_name": "Signals",
            "purpose": "Completion, ready, blocker, dissent, and receipt signals.",
            "default_participants": ["role.steward", "role.nemesis"],
            "report_to_room_id": "room.main.team",
            "visibility": "team_projection",
            "summary_required": False,
        },
        {
            "room_id": "room.channel.gates",
            "room_kind": "audit",
            "channel_id": "gates",
            "display_name": "Gates",
            "purpose": "Operator gates, authority requests, and release blockers.",
            "default_participants": ["operator", "role.steward", "role.nemesis"],
            "report_to_room_id": "room.main.team",
            "visibility": "audit_projection",
            "summary_required": True,
        },
        {
            "room_id": "room.audit",
            "room_kind": "audit",
            "channel_id": "audit",
            "display_name": "Audit",
            "purpose": "Proof, dissent, template drift, and release-risk review.",
            "default_participants": ["role.nemesis", "role.vice", "role.steward"],
            "report_to_room_id": "room.main.team",
            "visibility": "audit_projection",
            "summary_required": True,
        },
    ]
    domain_rooms: list[dict[str, Any]] = []
    for domain in domain_rows:
        domain_id = _text(domain.get("domain_id"))
        if not domain_id:
            continue
        agents_for_domain = [row for row in list(domain.get("agents") or []) if isinstance(row, Mapping)]
        participant_roles = [str(row.get("role_id") or "") for row in agents_for_domain if row.get("available_for_comms")]
        domain_rooms.append(
            {
                "room_id": _room_id_for_domain(domain_id),
                "room_kind": "domain",
                "channel_id": _room_channel_id_for_domain(domain_id),
                "display_name": domain.get("display_name") or domain_id,
                "domain_id": domain_id,
                "purpose": "Domain specialist coordination, capsule maintenance, and local routing decisions.",
                "default_participants": participant_roles,
                "available_agent_count": len(participant_roles),
                "report_to_room_id": "room.main.team",
                "visibility": "domain_participants",
                "summary_required": True,
            }
        )
    all_rooms = [*default_rooms, *domain_rooms]
    return {
        "schema_id": ROOM_CONTRACT_SCHEMA_ID,
        "generated_at": generated_at or _now(),
        "source_directory_path": COMMUNICATION_DIRECTORY_PATH.as_posix(),
        "owner_domain_id": "domain.agent_communication_systems",
        "recommended_owner_role": "role.comms_cartographer",
        "room_kinds": deepcopy(ROOM_KIND_CONTRACTS),
        "default_rooms": default_rooms,
        "domain_rooms": domain_rooms,
        "rooms_by_id": {str(room.get("room_id")): room for room in all_rooms if room.get("room_id")},
        "room_count": len(all_rooms),
        "dynamic_room_templates": [
            {
                "room_kind": "direct",
                "room_id_template": "room.direct.<participant_role_ids>",
                "channel_id_template": "dm_<participant_role_ids>",
                "required_fields": ["from_role", "to_roles"],
                "report_to_room_id": "room.main.team",
            },
            {
                "room_kind": "mission",
                "room_id_template": "room.mission.<mission_or_run_id>",
                "channel_id_template": "mission_<mission_or_run_id>",
                "required_fields": ["mission_id or run_id"],
                "report_to_room_id": "room.main.team",
            },
            {
                "room_kind": "domain",
                "room_id_template": "room.domain.<domain_id>",
                "channel_id_template": "domain_<domain_id>",
                "required_fields": ["domain_id"],
                "report_to_room_id": "room.main.team",
            },
        ],
        "routing_rules": deepcopy(ROOM_ROUTING_RULES),
        "reporting_rules": deepcopy(ROOM_REPORTING_RULES),
        "context_loading": {
            "first_read": "room_capsule",
            "capsule_schema_id": "ion.agent_comms.room_capsule.v1",
            "route_deeper_refs": ["thread_path", "message_path", "message_index_path"],
            "rule": "Agents should read the active room capsule first, then follow route_deeper_refs only when the decision needs full transcript evidence.",
        },
        "contact_contract_ref": (contact_contract or {}).get("routing_source_of_truth") or "COMMUNICATION_DIRECTORY.json#contact_contract",
        "start_comms_ref": dict(start_comms or {}),
        "agent_decision_boundary": "Agents choose the room or direct contact from this contract. Automation only validates limits, writes durable packets, and updates room capsules.",
        "routing_source_of_truth": "COMMUNICATION_DIRECTORY.json#room_contract",
        "policy": "This room contract defines real comms organization and context-loading rules; it is not a chat simulation.",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def _agent_directory_row(root: Path, agent: Mapping[str, Any]) -> dict[str, Any]:
    role_id = normalize_role_id(agent.get("role_id") or agent.get("agent_id"))
    evidence = _record(agent.get("agent_page_evidence"))
    identity = _record(evidence.get("identity"))
    mount = _record(agent.get("native_codex_mount"))
    context_card = _text(agent.get("context_system_card"))
    context_card_exists = bool(context_card and (root / context_card).exists())
    capsule_path = _text(mount.get("portable_context_manifest_path"))
    capsule_exists = bool(capsule_path and (root / capsule_path).exists())
    available = bool(role_id and (agent.get("invocable") or context_card_exists or capsule_exists))
    aliases = _agent_aliases(role_id, agent.get("display_name"))
    channels = []
    for channel in default_agent_channels():
        participants = [normalize_role_id(item) for item in channel.get("default_participants") or []]
        if role_id in participants or channel.get("channel_id") in {"team", "handoffs", "signals"}:
            channels.append(str(channel.get("channel_id")))
    return {
        "role_id": role_id,
        "display_name": agent.get("display_name") or role_id,
        "aliases": aliases,
        "mention": f"@{aliases[0]}" if aliases else "",
        "contact_syntax": f"@{aliases[0]}" if aliases else role_id,
        "available_for_comms": available,
        "availability_state": "available" if available else "context_missing",
        "invocable": bool(agent.get("invocable")),
        "context_card": context_card,
        "context_card_exists": context_card_exists,
        "capsule_path": capsule_path,
        "capsule_exists": capsule_exists,
        "is_capsule_agent": bool(identity.get("is_capsule_agent") or capsule_exists),
        "is_codex_native_mount": bool(identity.get("is_codex_native_mount") or mount.get("materialized")),
        "domain_ids": _agent_domain_ids(agent),
        "primary_domain": _text(agent.get("registry_primary_domain")) or _text(mount.get("domain_id")),
        "inbox_path": (AGENT_COMMS_ROOT / "inbox" / _role_slug(role_id)).as_posix(),
        "outbox_path": (AGENT_COMMS_ROOT / "outbox" / _role_slug(role_id)).as_posix(),
        "default_channels": channels,
        "can_initiate_comms": available,
        "can_receive_workpacks": bool(agent.get("invocable")),
        "automation_comms_allowed": available,
        "communication_contract": {
            "schema_id": "ion.agent_role_contact_profile.v1",
            "contact_contract_schema_id": CONTACT_CONTRACT_SCHEMA_ID,
            "contact_contract_ref": f"{COMMUNICATION_DIRECTORY_PATH.as_posix()}#contact_contract",
            "room_contract_schema_id": ROOM_CONTRACT_SCHEMA_ID,
            "room_contract_ref": f"{COMMUNICATION_DIRECTORY_PATH.as_posix()}#room_contract",
            "mention_route": f"Use @{aliases[0]} in Team Comms or directive body." if aliases else "Use the role_id in Team Comms or directive body.",
            "directive_role": role_id,
            "preferred_channels": channels,
            "requires_source_refs": True,
            "candidate_only": True,
        },
        "start_comms_template_ids": ["agent_comms_decision", "agent_workpack_decision"],
        "handoff_template_ids": ["agent_workpack_decision", "domain_context_review", "audit_review"],
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def build_automation_comms_policy(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    return {
        "schema_id": AUTOMATION_POLICY_SCHEMA_ID,
        "generated_at": _now(),
        "policy_id": "default_bounded_agent_automation_comms",
        "usage_log_path": AUTOMATION_USAGE_LOG.as_posix(),
        "limits": dict(DEFAULT_AUTOMATION_COMMS_LIMITS),
        "guard_inputs": [
            "dispatch_source=automation",
            "automation_id",
            "automation_window_minutes",
            "automation_prompt_limit",
            "automation_time_budget_minutes",
            "automation_prompt_char_limit",
            "automation_started_at",
        ],
        "requirements": [
            "Automated comms must identify automation_id.",
            "Automated comms are counted in a time window before packet creation.",
            "Objective/body prompt text is length-limited before packet creation.",
            "A provided automation_started_at can enforce elapsed time budget.",
            "Blocked automation comms do not write agent messages or workpack requests.",
        ],
        "directory_path": COMMUNICATION_DIRECTORY_PATH.as_posix(),
        "directory_exists": (shell_root / COMMUNICATION_DIRECTORY_PATH).is_file(),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def build_agent_communication_directory(
    root: str | Path | None,
    *,
    agents: Sequence[Mapping[str, Any]],
    domains: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    generated_at = _now()
    agent_rows = [_agent_directory_row(shell_root, agent) for agent in agents]
    by_role = {str(row.get("role_id")): row for row in agent_rows if row.get("role_id")}
    domain_rows = []
    for domain in domains:
        domain_id = _text(domain.get("domain_id"))
        if not domain_id:
            continue
        bound = [row for row in agent_rows if domain_id in list(row.get("domain_ids") or [])]
        domain_rows.append(
            {
                "domain_id": domain_id,
                "display_name": domain.get("display_name") or domain_id,
                "available_agent_count": sum(1 for row in bound if row.get("available_for_comms")),
                "invocable_agent_count": sum(1 for row in bound if row.get("invocable")),
                "agents": [
                    {
                        "role_id": row.get("role_id"),
                        "display_name": row.get("display_name"),
                        "available_for_comms": bool(row.get("available_for_comms")),
                        "can_receive_workpacks": bool(row.get("can_receive_workpacks")),
                    }
                    for row in bound
                ],
            }
        )
    automation_policy = build_automation_comms_policy(shell_root)
    task_run_policy = {
        "schema_id": "ion.agent_comms.task_run_policy.v1",
        "default_limits": dict(DEFAULT_TASK_RUN_LIMITS),
        "observability": {
            "run_graph_schema_id": "ion.agent_comms.run_graph.v1",
            "policy_gate_schema_id": "ion.agent_comms.run_policy_gate.v1",
            "audit_gate_schema_id": "ion.agent_comms.audit_gate.v1",
            "states": ["messages_delivered", "workpack_active", "response_observed", "blocked_by_policy", "limit_reached"],
            "evidence_chain": ["message", "directive", "workpack", "task_return", "synced_reply"],
        },
        "agent_decision_boundary": "Agents decide whether to communicate by writing visible messages or ion-agent-comms directive blocks. Automation only validates limits, routes packets, and projects evidence.",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }
    start_comms = {
        "manual_endpoint": "/cockpit/agents/spawn-template",
        "task_run_start_endpoint": "/cockpit/agents/comms/run/start",
        "task_run_pickup_endpoint": "/cockpit/agents/comms/run/pickup",
        "task_run_audit_endpoint": "/cockpit/agents/comms/run/audit",
        "agent_packet_bus": AGENT_COMMS_ROOT.as_posix(),
        "agent_initiated_policy": "Agents initiate communication by creating durable comms packets through governed ION flows; direct live execution remains separate proof-gated broker work.",
        "default_from_role": "current_agent_role_id",
        "default_to_role": "role.steward",
        "requires_source_refs": True,
        "task_run_policy": "Task runs are operator-approved bounded wrappers around real comms and explicit ion-agent-comms directive pickup; they do not simulate replies or decide for agents.",
        "mention_syntax": "@agent_alias",
        "directive_fence": "ion-agent-comms",
        "directive_schema_id": "ion.agent_comms.directive.v1",
        "agent_to_agent_rule": "If an agent needs another agent, it writes a visible @mention message or an ion-agent-comms directive block with source_refs; pickup/automation routes it under task-run policy limits.",
        "example_directive": {
            "schema_id": "ion.agent_comms.directive.v1",
            "from_role": "current_agent_role_id",
            "agent": "role.ionologist",
            "template_id": "agent_workpack_decision",
            "dispatch_mode": "queue_workpack",
            "objective": "Review the cited packet and return a bounded decision.",
            "body": "Use the source refs and do not claim accepted state.",
            "room_kind": "direct",
            "report_to_room_id": "room.main.team",
            "source_refs": ["ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json"],
        },
    }
    contact_contract = build_agent_contact_contract(
        agents=agent_rows,
        domains=domain_rows,
        generated_at=generated_at,
        automation_policy=automation_policy,
        task_run_policy=task_run_policy,
        start_comms=start_comms,
    )
    room_contract = build_agent_room_contract(
        agents=agent_rows,
        domains=domain_rows,
        generated_at=generated_at,
        contact_contract=contact_contract,
        start_comms=start_comms,
    )
    return {
        "schema_id": DIRECTORY_SCHEMA_ID,
        "generated_at": generated_at,
        "directory_path": COMMUNICATION_DIRECTORY_PATH.as_posix(),
        "agent_count": len(agent_rows),
        "available_agent_count": sum(1 for row in agent_rows if row.get("available_for_comms")),
        "invocable_agent_count": sum(1 for row in agent_rows if row.get("invocable")),
        "domain_count": len(domain_rows),
        "channels": default_agent_channels(),
        "agents": agent_rows,
        "agents_by_role": by_role,
        "domains": domain_rows,
        "automation_comms_policy": automation_policy,
        "task_run_policy": task_run_policy,
        "start_comms": start_comms,
        "contact_contract": contact_contract,
        "room_contract": room_contract,
        "policy": "This directory tells agents who is available and how to start bounded communication. It is a packet directory, not a live-agent simulation.",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def materialize_agent_communication_directory(
    root: str | Path | None,
    *,
    agents: Sequence[Mapping[str, Any]],
    domains: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    directory = build_agent_communication_directory(shell_root, agents=agents, domains=domains)
    path = shell_root / COMMUNICATION_DIRECTORY_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(directory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    contact_contract = _record(directory.get("contact_contract"))
    room_contract = _record(directory.get("room_contract"))
    return {
        "schema_id": "ion.agent_communication_directory.materialize_result.v1",
        "ok": True,
        "directory_path": COMMUNICATION_DIRECTORY_PATH.as_posix(),
        "available_agent_count": directory.get("available_agent_count"),
        "agent_count": directory.get("agent_count"),
        "contact_contract_schema_id": contact_contract.get("schema_id"),
        "contact_edge_count": contact_contract.get("contact_edge_count"),
        "room_contract_schema_id": room_contract.get("schema_id"),
        "room_count": room_contract.get("room_count"),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def _automation_guard_requested(payload: Mapping[str, Any]) -> bool:
    source = _text(payload.get("dispatch_source") or payload.get("source_kind") or payload.get("initiated_by"))
    if source == "automation":
        return True
    return any(
        key in payload
        for key in (
            "automation_id",
            "automation_prompt_limit",
            "automation_window_minutes",
            "automation_time_budget_minutes",
            "automation_started_at",
        )
    )


def _usage_rows(root: Path, automation_id: str, window_start: datetime) -> list[dict[str, Any]]:
    path = root / AUTOMATION_USAGE_LOG
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, Mapping):
            continue
        if str(row.get("automation_id") or "") != automation_id:
            continue
        timestamp = _parse_time(row.get("created_at"))
        if timestamp and timestamp >= window_start:
            rows.append(dict(row))
    return rows


def check_automation_comms_quota(
    root: str | Path | None,
    payload: Mapping[str, Any],
    *,
    agent: str,
    template_id: str,
    dispatch_mode: str,
    objective: str,
    body: str,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    policy = build_automation_comms_policy(shell_root)
    limits = dict(policy["limits"])
    if not _automation_guard_requested(payload):
        return {
            "schema_id": AUTOMATION_CHECK_SCHEMA_ID,
            "guard_active": False,
            "allowed": True,
            "policy": policy,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }
    automation_id = _text(payload.get("automation_id"))
    if not automation_id:
        return {
            "schema_id": AUTOMATION_CHECK_SCHEMA_ID,
            "guard_active": True,
            "allowed": False,
            "finding": "automation_id_required",
            "policy": policy,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }
    window_minutes = _int(
        payload.get("automation_window_minutes"),
        int(limits["default_window_minutes"]),
        lower=1,
        upper=int(limits["max_window_minutes"]),
    )
    prompt_limit = _int(
        payload.get("automation_prompt_limit"),
        int(limits["default_prompt_limit"]),
        lower=1,
        upper=int(limits["max_prompt_limit"]),
    )
    time_budget_minutes = _int(
        payload.get("automation_time_budget_minutes"),
        int(limits["default_time_budget_minutes"]),
        lower=1,
        upper=int(limits["max_time_budget_minutes"]),
    )
    prompt_char_limit = _int(
        payload.get("automation_prompt_char_limit"),
        int(limits["default_prompt_char_limit"]),
        lower=1,
        upper=int(limits["max_prompt_char_limit"]),
    )
    prompt_chars = len(objective) + len(body)
    if prompt_chars > prompt_char_limit:
        return {
            "schema_id": AUTOMATION_CHECK_SCHEMA_ID,
            "guard_active": True,
            "allowed": False,
            "finding": "automation_prompt_char_limit_exceeded",
            "automation_id": automation_id,
            "prompt_chars": prompt_chars,
            "prompt_char_limit": prompt_char_limit,
            "policy": policy,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }
    now = _now_dt()
    started_at = _parse_time(payload.get("automation_started_at"))
    if started_at and now > started_at + timedelta(minutes=time_budget_minutes):
        return {
            "schema_id": AUTOMATION_CHECK_SCHEMA_ID,
            "guard_active": True,
            "allowed": False,
            "finding": "automation_time_budget_exceeded",
            "automation_id": automation_id,
            "automation_started_at": started_at.isoformat(),
            "time_budget_minutes": time_budget_minutes,
            "policy": policy,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }
    window_start = now - timedelta(minutes=window_minutes)
    rows = _usage_rows(shell_root, automation_id, window_start)
    if len(rows) >= prompt_limit:
        return {
            "schema_id": AUTOMATION_CHECK_SCHEMA_ID,
            "guard_active": True,
            "allowed": False,
            "finding": "automation_prompt_limit_exceeded",
            "automation_id": automation_id,
            "window_minutes": window_minutes,
            "prompt_limit": prompt_limit,
            "used_prompt_count": len(rows),
            "remaining_prompt_count": 0,
            "policy": policy,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        }
    return {
        "schema_id": AUTOMATION_CHECK_SCHEMA_ID,
        "guard_active": True,
        "allowed": True,
        "automation_id": automation_id,
        "agent": agent,
        "template_id": template_id,
        "dispatch_mode": dispatch_mode,
        "window_minutes": window_minutes,
        "prompt_limit": prompt_limit,
        "used_prompt_count": len(rows),
        "remaining_prompt_count": max(0, prompt_limit - len(rows) - 1),
        "prompt_chars": prompt_chars,
        "prompt_char_limit": prompt_char_limit,
        "time_budget_minutes": time_budget_minutes,
        "policy": policy,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def record_automation_comms_usage(
    root: str | Path | None,
    check: Mapping[str, Any],
    *,
    payload: Mapping[str, Any],
    result: Mapping[str, Any],
) -> str:
    if not check.get("guard_active") or not check.get("allowed"):
        return ""
    shell_root = _resolve_root(root)
    path = shell_root / AUTOMATION_USAGE_LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "schema_id": AUTOMATION_USAGE_SCHEMA_ID,
        "created_at": _now(),
        "automation_id": check.get("automation_id"),
        "automation_prompt_id": payload.get("automation_prompt_id") or payload.get("idempotency_key") or result.get("comms_result", {}).get("message_id"),
        "template_id": result.get("template_id"),
        "dispatch_mode": result.get("dispatch_mode"),
        "agent": result.get("agent"),
        "domain_id": result.get("domain_id"),
        "spawn_status": result.get("spawn_status"),
        "message_id": _record(result.get("comms_result")).get("message_id"),
        "workpack_path": _record(result.get("invocation_result")).get("codex_work_request_path"),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
    return AUTOMATION_USAGE_LOG.as_posix()
