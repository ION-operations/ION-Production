"""Agent roster and spawn-template projection for the cockpit.

This layer does not create a parallel agent system. It projects the existing
agent/domain registries, Codex mounts, durable comms, and invocation broker into
one roster surface, then lets a filled template create either a comms packet or
a broker-prepared workpack.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from .ion_agent_comms import send_agent_message
from .ion_agent_comms_directory import (
    build_agent_communication_directory,
    check_automation_comms_quota,
    record_automation_comms_usage,
)
from .ion_agent_invocation_broker import invoke_agent

SCHEMA_ID = "ion.agent_roster.projection.v1"
SPAWN_RESULT_SCHEMA_ID = "ion.agent_spawn_template.result.v1"

SPAWN_TEMPLATES: tuple[dict[str, Any], ...] = (
    {
        "template_id": "agent_comms_decision",
        "label": "Comms Decision",
        "template_kind": "durable_agent_comms",
        "default_dispatch_mode": "comms_only",
        "channel_id": "team",
        "message_kind": "decision_request",
        "subject_template": "Decision request for {agent}",
        "required_fields": ["agent", "objective", "body"],
        "description": "Route a decision request into the selected agent inbox without preparing backend work.",
    },
    {
        "template_id": "agent_workpack_decision",
        "label": "Workpack Decision",
        "template_kind": "broker_prepared_workpack",
        "default_dispatch_mode": "prepare_workpack",
        "channel_id": "handoffs",
        "message_kind": "task_dispatch",
        "work_class": "agent_workpack_decision",
        "route_family": "agent_invocation",
        "risk_level": "medium",
        "subject_template": "Workpack prepared for {agent}",
        "required_fields": ["agent", "objective"],
        "description": "Prepare a proof-gated Codex work request for the selected agent and announce it through comms.",
    },
    {
        "template_id": "domain_context_review",
        "label": "Domain Context Review",
        "template_kind": "broker_prepared_workpack",
        "default_dispatch_mode": "prepare_workpack",
        "channel_id": "gates",
        "message_kind": "decision_request",
        "work_class": "domain_context_review",
        "route_family": "domain_context_review",
        "risk_level": "medium",
        "subject_template": "Domain context review for {domain}",
        "required_fields": ["agent", "domain_id", "objective"],
        "description": "Prepare a selected-agent review of whether a domain has the right ION/capsule agent binding.",
    },
    {
        "template_id": "audit_review",
        "label": "Audit Review",
        "template_kind": "broker_prepared_workpack",
        "default_dispatch_mode": "prepare_workpack",
        "channel_id": "audit",
        "message_kind": "audit",
        "work_class": "agent_audit_review",
        "route_family": "agent_audit",
        "risk_level": "high",
        "subject_template": "Audit review for {agent}",
        "required_fields": ["agent", "objective"],
        "description": "Prepare a bounded audit workpack for review agents; no accepted-state authority is granted.",
    },
)


def _text(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text or fallback


def _list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, tuple):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.splitlines() if item.strip()]
    return []


def _record(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _no_authority() -> dict[str, bool]:
    return {
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def _find_template(template_id: str) -> dict[str, Any] | None:
    return next((dict(item) for item in SPAWN_TEMPLATES if item["template_id"] == template_id), None)


def _agent_domain_ids(agent: Mapping[str, Any]) -> list[str]:
    mount = _record(agent.get("native_codex_mount"))
    ids = [_text(agent.get("registry_primary_domain")), _text(mount.get("domain_id"))]
    ids.extend(_list(agent.get("registry_secondary_domains")))
    seen: set[str] = set()
    return [item for item in ids if item and not (item in seen or seen.add(item))]


def _agent_roster_row(root: Path, agent: Mapping[str, Any], domain_index: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    evidence = _record(agent.get("agent_page_evidence"))
    identity = _record(evidence.get("identity"))
    proof = _record(evidence.get("proof"))
    mount = _record(agent.get("native_codex_mount"))
    primary_domain_id = _text(agent.get("registry_primary_domain")) or _text(mount.get("domain_id"))
    primary_domain = _record(domain_index.get(primary_domain_id))
    context_card = _text(agent.get("context_system_card"))
    context_card_exists = bool(context_card and (root / context_card).exists())
    template_paths = _list(agent.get("primary_templates") or agent.get("template_bindings"))
    missing_templates = [path for path in template_paths if not (root / path).exists()]
    has_domain = bool(primary_domain_id and primary_domain)
    is_capsule_agent = bool(identity.get("is_capsule_agent"))
    is_codex_mount = bool(identity.get("is_codex_native_mount") or mount.get("materialized"))
    status = "ready"
    if not has_domain:
        status = "missing_domain_binding"
    elif not context_card_exists:
        status = "missing_context_card"
    elif not is_capsule_agent:
        status = "needs_capsule_mount"
    elif missing_templates:
        status = "missing_template_refs"
    return {
        "role_id": agent.get("role_id"),
        "display_name": agent.get("display_name"),
        "live_status": agent.get("live_status"),
        "invocable": bool(agent.get("invocable")),
        "roster_status": status,
        "registry_primary_domain": primary_domain_id,
        "registry_secondary_domains": _list(agent.get("registry_secondary_domains")),
        "domain_ids": _agent_domain_ids(agent),
        "domain_display": primary_domain.get("display_name") or primary_domain.get("domain_id") or primary_domain_id,
        "domain_has_registry": has_domain,
        "context_system_card": context_card,
        "context_card_exists": context_card_exists,
        "context_system_status": agent.get("context_system_status"),
        "agent_kind": identity.get("agent_kind"),
        "is_ion_context_system": bool(identity.get("is_ion_context_system")),
        "is_capsule_agent": is_capsule_agent,
        "is_codex_native_mount": is_codex_mount,
        "is_portable_package_agent": bool(identity.get("is_portable_package_agent")),
        "codex_mount_path": mount.get("mount_path"),
        "codex_mount_materialized": bool(mount.get("materialized")),
        "active_context_package": mount.get("active_context_package_md_path"),
        "template_count": len(template_paths),
        "missing_template_refs": missing_templates,
        "missing_declared_context_paths": _list(agent.get("missing_declared_context_paths")),
        "missing_critical": _list(proof.get("missing_critical")),
        "spawn_supported": bool(agent.get("invocable") and context_card_exists),
        "production_authority": False,
        "live_execution_authority": False,
    }


def _domain_roster_row(domain: Mapping[str, Any], roster_agents: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    domain_id = _text(domain.get("domain_id"))
    bound = [agent for agent in roster_agents if domain_id in _list(agent.get("domain_ids"))]
    primary = [agent for agent in bound if _text(agent.get("registry_primary_domain")) == domain_id]
    capsule_agents = [agent for agent in bound if agent.get("is_capsule_agent")]
    invocable = [agent for agent in bound if agent.get("invocable")]
    status = "built_with_capsule_agents" if capsule_agents else ("domain_has_agents_needs_capsule_mount" if bound else "needs_agent_binding")
    return {
        "domain_id": domain_id,
        "purpose": domain.get("purpose"),
        "fact_posture": domain.get("fact_posture"),
        "maturity_estimate": domain.get("maturity_estimate"),
        "source_registry": domain.get("source_registry"),
        "agent_count": len(bound),
        "primary_agent_count": len(primary),
        "capsule_agent_count": len(capsule_agents),
        "invocable_agent_count": len(invocable),
        "roster_status": status,
        "agents": [
            {
                "role_id": agent.get("role_id"),
                "display_name": agent.get("display_name"),
                "roster_status": agent.get("roster_status"),
                "is_capsule_agent": bool(agent.get("is_capsule_agent")),
                "is_codex_native_mount": bool(agent.get("is_codex_native_mount")),
            }
            for agent in bound
        ],
        "production_authority": False,
        "live_execution_authority": False,
    }


def build_agent_spawn_templates_projection() -> dict[str, Any]:
    return {
        "schema_id": "ion.agent_spawn_templates.v1",
        "templates": [dict(item) for item in SPAWN_TEMPLATES],
        "default_dispatch_modes": ["comms_only", "prepare_workpack", "queue_workpack", "start_workpack"],
        "default_endpoint": "/cockpit/agents/spawn-template",
        "policy": "Templates create durable comms packets or broker workpack records. start_workpack is only for explicit directive/broker pickup; no fake agent simulation or accepted-state authority is granted.",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def build_agent_roster_projection(
    root: str | Path | None,
    *,
    agents: Sequence[Mapping[str, Any]],
    domains: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    shell_root = Path(root or ".").expanduser().resolve()
    domain_index = {_text(domain.get("domain_id")): domain for domain in domains if _text(domain.get("domain_id"))}
    agent_rows = [_agent_roster_row(shell_root, agent, domain_index) for agent in agents]
    domain_rows = [_domain_roster_row(domain, agent_rows) for domain in domains]
    communication_directory = build_agent_communication_directory(shell_root, agents=agents, domains=domains)
    comms_by_role = _record(communication_directory.get("agents_by_role"))
    for agent in agent_rows:
        profile = _record(comms_by_role.get(str(agent.get("role_id") or "")))
        agent["communication_profile"] = profile
        agent["available_for_comms"] = bool(profile.get("available_for_comms"))
        agent["can_initiate_comms"] = bool(profile.get("can_initiate_comms"))
        agent["automation_comms_allowed"] = bool(profile.get("automation_comms_allowed"))
    return {
        "schema_id": SCHEMA_ID,
        "agent_count": len(agent_rows),
        "domain_count": len(domain_rows),
        "invocable_agent_count": sum(1 for agent in agent_rows if agent.get("invocable")),
        "capsule_agent_count": sum(1 for agent in agent_rows if agent.get("is_capsule_agent")),
        "codex_mount_agent_count": sum(1 for agent in agent_rows if agent.get("is_codex_native_mount")),
        "domain_built_count": sum(1 for domain in domain_rows if domain.get("roster_status") == "built_with_capsule_agents"),
        "agents": agent_rows,
        "domains": domain_rows,
        "spawn_templates": build_agent_spawn_templates_projection()["templates"],
        "communication_directory": communication_directory,
        "policy": "Roster truth comes from registry/domain/context/mount evidence. Spawn means comms packet or broker workpack, not fake agent simulation.",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def execute_agent_spawn_template(root: str | Path | None, payload: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = Path(root or ".").expanduser().resolve()
    template_id = _text(payload.get("template_id"), "agent_workpack_decision")
    template = _find_template(template_id)
    if template is None:
        return {
            "schema_id": SPAWN_RESULT_SCHEMA_ID,
            "ok": False,
            "finding": "unknown_spawn_template",
            "template_id": template_id,
            "available_templates": [item["template_id"] for item in SPAWN_TEMPLATES],
            **_no_authority(),
        }
    agent = _text(payload.get("agent") or payload.get("role_id") or payload.get("agent_id"))
    objective = _text(payload.get("objective"))
    body = _text(payload.get("body") or payload.get("message") or objective)
    domain_id = _text(payload.get("domain_id"))
    if not agent:
        return {"schema_id": SPAWN_RESULT_SCHEMA_ID, "ok": False, "finding": "agent_required", "template_id": template_id, **_no_authority()}
    if not objective:
        return {"schema_id": SPAWN_RESULT_SCHEMA_ID, "ok": False, "finding": "objective_required", "template_id": template_id, **_no_authority()}
    dispatch_mode = _text(payload.get("dispatch_mode"), template["default_dispatch_mode"])
    if dispatch_mode not in {"comms_only", "prepare_workpack", "queue_workpack", "start_workpack"}:
        return {"schema_id": SPAWN_RESULT_SCHEMA_ID, "ok": False, "finding": "unsupported_dispatch_mode", "template_id": template_id, **_no_authority()}
    automation_check = check_automation_comms_quota(
        shell_root,
        payload,
        agent=agent,
        template_id=template_id,
        dispatch_mode=dispatch_mode,
        objective=objective,
        body=body,
    )
    if not automation_check.get("allowed"):
        return {
            "schema_id": SPAWN_RESULT_SCHEMA_ID,
            "ok": False,
            "finding": automation_check.get("finding") or "automation_comms_blocked",
            "template_id": template_id,
            "dispatch_mode": dispatch_mode,
            "agent": agent,
            "target_agent": agent,
            "domain_id": domain_id or None,
            "automation_comms_check": automation_check,
            **_no_authority(),
        }
    subject = _text(payload.get("subject")) or str(template.get("subject_template") or "{agent}").format(
        agent=agent,
        domain=domain_id or "selected domain",
    )
    source_refs = _list(payload.get("source_refs") or payload.get("context_refs"))
    artifact_refs = _list(payload.get("artifact_refs") or payload.get("evidence_refs"))
    invocation_result: dict[str, Any] | None = None
    if dispatch_mode in {"prepare_workpack", "queue_workpack", "start_workpack"}:
        invocation_result = invoke_agent(
            shell_root,
            agent=agent,
            objective=objective,
            mode="spawn_template_prepare",
            queue=dispatch_mode in {"queue_workpack", "start_workpack"},
            start=dispatch_mode == "start_workpack",
            context_refs=source_refs,
            timeout_seconds=int(payload.get("timeout_seconds") or 1800),
            work_class=_text(payload.get("work_class"), _text(template.get("work_class"), "agent_invocation")),
            risk_level=_text(payload.get("risk_level"), _text(template.get("risk_level"), "medium")),
            route_family=_text(payload.get("route_family"), _text(template.get("route_family"), "agent_invocation")),
            idempotency_key=_text(payload.get("idempotency_key")) or None,
            target_root_id=_text(payload.get("target_root_id"), "active_ion_control"),
            movement_class=_text(payload.get("movement_class"), "ION_KERNEL_CONTROL_MOVEMENT"),
            target_project_subpath=_text(payload.get("target_project_subpath")) or None,
            planned_writes=_list(payload.get("planned_writes")),
            planned_artifacts=_list(payload.get("planned_artifacts")),
            domain_id=domain_id or None,
            use_codex_mount=payload.get("use_codex_mount") is not False,
            body=body,
        )
        if not invocation_result.get("ok"):
            return {
                "schema_id": SPAWN_RESULT_SCHEMA_ID,
                "ok": False,
                "finding": "workpack_prepare_failed",
                "template_id": template_id,
                "invocation_result": invocation_result,
                **_no_authority(),
            }
        for key in ("invocation_path", "capsule_context_path", "codex_work_request_path"):
            value = _text(invocation_result.get(key))
            if value:
                artifact_refs.append(value)
    message_body = "\n\n".join(
        part
        for part in [
            body,
            f"Objective: {objective}",
            f"Template: {template_id}",
            f"Domain: {domain_id}" if domain_id else "",
            f"Workpack: {invocation_result.get('codex_work_request_path')}" if invocation_result else "",
        ]
        if part
    )
    comms_result = send_agent_message(
        shell_root,
        {
            "channel_id": _text(payload.get("channel_id"), _text(template.get("channel_id"), "team")),
            "thread_id": _text(payload.get("thread_id")) or None,
            "from_role": _text(payload.get("from_role"), "operator"),
            "to_roles": [agent],
            "cc_roles": _list(payload.get("cc_roles")),
            "message_kind": _text(payload.get("message_kind"), _text(template.get("message_kind"), "decision_request")),
            "room_id": _text(payload.get("room_id")),
            "room_kind": _text(payload.get("room_kind") or payload.get("room_type")),
            "report_to_room_id": _text(payload.get("report_to_room_id") or payload.get("report_room_id")),
            "visibility": _text(payload.get("visibility")),
            **({"summary_required": bool(payload.get("summary_required"))} if payload.get("summary_required") is not None else {}),
            "subject": subject,
            "body": message_body,
            "summary": _text(payload.get("summary")) or objective,
            "requires_response": payload.get("requires_response") is not False,
            "source_refs": source_refs,
            "artifact_refs": artifact_refs,
        },
    )
    result = {
        "schema_id": SPAWN_RESULT_SCHEMA_ID,
        "ok": bool(comms_result.get("ok") and (invocation_result is None or invocation_result.get("ok"))),
        "template_id": template_id,
        "dispatch_mode": dispatch_mode,
        "agent": agent,
        "target_agent": agent,
        "domain_id": domain_id or None,
        "objective": objective,
        "spawn_status": "COMMS_PACKET_SENT"
        if invocation_result is None
        else ("WORKPACK_STARTED" if dispatch_mode == "start_workpack" else ("WORKPACK_QUEUED" if dispatch_mode == "queue_workpack" else "WORKPACK_PREPARED")),
        "comms_result": comms_result,
        "spawned_comms_message_id": comms_result.get("message_id"),
        "invocation_result": invocation_result,
        "workpack_path": _record(invocation_result).get("codex_work_request_path"),
        "workpack_status": _record(invocation_result).get("codex_work_request_status"),
        "automation_comms_check": automation_check,
        "live_external_agent_execution_proven": False,
        **_no_authority(),
    }
    usage_log_path = record_automation_comms_usage(shell_root, automation_check, payload=payload, result=result)
    if usage_log_path:
        result["automation_usage_log_path"] = usage_log_path
    return result
