"""Deterministic projection-record helpers for Domain Weaver.

This module shapes in-memory agent/domain projection records only. It performs
no filesystem reads or writes, no registry/materialization movement, no live
execution, no UI/topology projection work, no dispatcher/operator-action
history work, no secrets access, and no accepted-state authority movement.
"""
from __future__ import annotations

from typing import Any, Mapping

CANDIDATE_DOMAIN_ROLE_COVERAGE: dict[str, list[str]] = {
    "front_door": ["role.steward", "role.relay", "role.persona_interface"],
    "canon": ["role.canon_librarian", "role.ionologist", "role.template_curator", "role.steward"],
    "kernel": ["role.mason", "role.codex_carrier_steward", "role.runtime_cartographer"],
    "products": ["role.scribe", "role.steward", "role.atlas"],
    "carriers": ["role.codex_carrier_steward", "role.relay", "role.persona_interface"],
    "runtime": ["role.runtime_cartographer", "role.codex_carrier_steward", "role.mason"],
    "context": ["role.context_cartographer", "role.vizier", "role.ionologist"],
    "work_release": ["role.steward", "role.scribe", "role.nemesis"],
    "references": ["role.atlas", "role.thoth", "role.vestige"],
    "archive_private": ["role.scribe", "role.vestige", "role.nemesis"],
}


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _clean_list(values: Any) -> list[str]:
    if not isinstance(values, (list, tuple)):
        return []
    cleaned: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned


def _role_id(agent: Mapping[str, Any]) -> str:
    return str(agent.get("role_id") or agent.get("agent_id") or "").strip()


def _domain_id(domain: Mapping[str, Any]) -> str:
    return str(domain.get("domain_id") or "").strip()


def _agent_domain_ids(agent: Mapping[str, Any]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    primary = str(agent.get("registry_primary_domain") or agent.get("primary_domain") or "").strip()
    if primary and not primary.startswith("NONE_DECLARED"):
        rows.append((primary, "primary"))
    for value in _clean_list(agent.get("registry_secondary_domains")):
        if value != primary:
            rows.append((value, "secondary"))
    for value in _clean_list(agent.get("domain_ids")):
        if value and all(existing != value for existing, _relationship in rows):
            rows.append((value, "member"))
    mount = _as_mapping(agent.get("native_codex_mount"))
    mount_domain = str(mount.get("domain_id") or "").strip()
    if mount_domain and all(existing != mount_domain for existing, _relationship in rows):
        rows.append((mount_domain, "mount"))
    return rows


def _agent_mount(agent: Mapping[str, Any], mounts_by_role: Mapping[str, Mapping[str, Any]]) -> Mapping[str, Any]:
    mount = _as_mapping(agent.get("native_codex_mount"))
    if mount:
        return mount
    return mounts_by_role.get(_role_id(agent), {})


def _mount_ready(mount: Mapping[str, Any]) -> bool:
    return bool(mount.get("materialized") and mount.get("agents_md_exists") and mount.get("config_exists"))


def _capsule_ready(mount: Mapping[str, Any]) -> bool:
    return bool(
        mount.get("portable_context_manifest_exists")
        and mount.get("portable_communications_exists")
        and mount.get("portable_address_book_exists")
        and mount.get("portable_active_context_package_md_exists")
    )


def _agent_record(
    agent: Mapping[str, Any],
    mount: Mapping[str, Any],
    communication_profile: Mapping[str, Any],
    *,
    portable_package: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    role_id = _role_id(agent)
    package = _as_mapping(portable_package) or {"exists": False, "drop_in_ready": False, "latest_path": ""}
    domain_rows = _agent_domain_ids(agent)
    mount_domain = str(mount.get("domain_id") or "").strip()
    if mount_domain and all(existing != mount_domain for existing, _relationship in domain_rows):
        domain_rows.append((mount_domain, "mount"))
    gaps: list[str] = []
    if not domain_rows:
        gaps.append("missing_domain_binding")
    if not mount:
        gaps.append("missing_codex_mount_projection")
    elif not _mount_ready(mount):
        gaps.append("codex_mount_not_materialized")
    if not _capsule_ready(mount):
        gaps.append("capsule_context_not_materialized")
    if not communication_profile or not communication_profile.get("available_for_comms"):
        gaps.append("communication_profile_unavailable")
    return {
        "role_id": role_id,
        "display_name": agent.get("display_name") or role_id,
        "primary_domain": str(agent.get("registry_primary_domain") or agent.get("primary_domain") or ""),
        "domain_ids": [domain_id for domain_id, _relationship in domain_rows],
        "domain_relationships": [
            {"domain_id": domain_id, "relationship": relationship}
            for domain_id, relationship in domain_rows
        ],
        "context_system_card": agent.get("context_system_card"),
        "context_system_status": agent.get("context_system_status"),
        "default_active_package_class": agent.get("default_active_package_class"),
        "template_bindings": _clean_list(agent.get("template_bindings") or agent.get("primary_templates")),
        "codex_mount": {
            "mount_id": mount.get("mount_id"),
            "domain_id": mount.get("domain_id"),
            "mount_path": mount.get("mount_path"),
            "materialized": bool(mount.get("materialized")),
            "ready": _mount_ready(mount),
            "portable_context_manifest_path": mount.get("portable_context_manifest_path"),
            "portable_capsule_path": mount.get("portable_capsule_path"),
            "portable_communications_path": mount.get("portable_communications_path"),
            "portable_address_book_path": mount.get("portable_address_book_path"),
            "portable_active_context_package_md_path": mount.get("portable_active_context_package_md_path"),
        },
        "capsule": {
            "ready": _capsule_ready(mount),
            "read_first": [
                mount.get("portable_context_manifest_path"),
                mount.get("portable_active_context_package_md_path"),
                mount.get("portable_agent_path"),
                mount.get("portable_domain_path"),
                mount.get("portable_relationships_path"),
                mount.get("portable_communications_path"),
                mount.get("portable_address_book_path"),
            ],
        },
        "portable_package": package,
        "communication": {
            "available_for_comms": bool(communication_profile.get("available_for_comms")),
            "mention": communication_profile.get("mention"),
            "aliases": list(communication_profile.get("aliases") or []),
            "inbox_path": communication_profile.get("inbox_path"),
            "outbox_path": communication_profile.get("outbox_path"),
            "can_receive_workpacks": bool(communication_profile.get("can_receive_workpacks")),
            "can_initiate_comms": bool(communication_profile.get("can_initiate_comms")),
        },
        "gaps": gaps,
        "ready_for_domain_weave": not gaps,
    }


def _is_candidate_domain(domain: Mapping[str, Any]) -> bool:
    domain_id = _domain_id(domain)
    fact_posture = str(domain.get("fact_posture") or "").lower()
    return domain_id.startswith("ion_vnext_") or "candidate" in fact_posture or "inferred" in fact_posture


def _coverage_key_for_domain(domain: Mapping[str, Any]) -> str:
    domain_id = _domain_id(domain)
    if domain_id.startswith("ion_vnext_"):
        return domain_id.removeprefix("ion_vnext_")
    steward_class = str(domain.get("suggested_steward_class") or "").lower()
    for key in CANDIDATE_DOMAIN_ROLE_COVERAGE:
        if key in steward_class:
            return key
    paths = " ".join(str(path).lower() for path in domain.get("paths") or [])
    for key in CANDIDATE_DOMAIN_ROLE_COVERAGE:
        if key in paths:
            return key
    return ""


def _candidate_coverage_rows(
    domain: Mapping[str, Any],
    agents_by_role: Mapping[str, Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    if not _is_candidate_domain(domain):
        return []
    key = _coverage_key_for_domain(domain)
    role_ids = CANDIDATE_DOMAIN_ROLE_COVERAGE.get(key, [])
    rows: list[Mapping[str, Any]] = []
    for role_id in role_ids:
        agent = agents_by_role.get(role_id)
        if agent:
            rows.append(agent)
    return rows


def _domain_status(
    agent_rows: list[Mapping[str, Any]],
    candidate_coverage_rows: list[Mapping[str, Any]],
    *,
    candidate: bool,
) -> str:
    if not agent_rows:
        if candidate and candidate_coverage_rows:
            return "candidate_covered"
        if candidate:
            return "candidate_needs_coverage"
        return "needs_agent_binding"
    if not any(_as_mapping(row.get("capsule")).get("ready") for row in agent_rows):
        return "needs_capsule_agent"
    if not any(_as_mapping(row.get("communication")).get("available_for_comms") for row in agent_rows):
        return "needs_comms_profile"
    return "usable"


def _domain_record(
    domain: Mapping[str, Any],
    agent_rows: list[Mapping[str, Any]],
    candidate_coverage_rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    domain_id = _domain_id(domain)
    read_first = list(domain.get("local_read_first_files") or [])
    source_registry = domain.get("source_registry") or next(
        (ref for ref in read_first if str(ref).endswith(".domain.yaml")),
        "",
    )
    primary_agents = [
        row
        for row in agent_rows
        if any(
            item.get("domain_id") == domain_id and item.get("relationship") == "primary"
            for item in row.get("domain_relationships") or []
            if isinstance(item, Mapping)
        )
    ]
    candidate = _is_candidate_domain(domain)
    status = _domain_status(agent_rows, candidate_coverage_rows, candidate=candidate)
    gaps: list[str] = []
    if status not in {"usable", "candidate_covered"}:
        gaps.append(status)
    if not source_registry:
        gaps.append("missing_domain_source_registry")
    if not domain.get("paths") and not read_first:
        gaps.append("missing_domain_context_refs")
    return {
        "domain_id": domain_id,
        "display_name": domain.get("display_name") or domain_id,
        "source_registry": source_registry,
        "candidate_domain": candidate,
        "accepted_ion_state": bool(domain.get("accepted_ion_state")) and not candidate,
        "fact_posture": domain.get("fact_posture"),
        "maturity_estimate": domain.get("maturity_estimate"),
        "status": status,
        "paths": list(domain.get("paths") or []),
        "read_first": read_first,
        "agent_count": len(agent_rows),
        "primary_agent_count": len(primary_agents),
        "capsule_agent_count": sum(1 for row in agent_rows if _as_mapping(row.get("capsule")).get("ready")),
        "codex_mount_count": sum(1 for row in agent_rows if _as_mapping(row.get("codex_mount")).get("mount_id")),
        "materialized_mount_count": sum(
            1 for row in agent_rows if _as_mapping(row.get("codex_mount")).get("ready")
        ),
        "portable_package_count": sum(
            1 for row in agent_rows if _as_mapping(row.get("portable_package")).get("drop_in_ready")
        ),
        "communication_agent_count": sum(
            1 for row in agent_rows if _as_mapping(row.get("communication")).get("available_for_comms")
        ),
        "candidate_coverage_count": len(candidate_coverage_rows),
        "agent_roles": [
            {
                "role_id": row.get("role_id"),
                "display_name": row.get("display_name"),
                "relationships": [
                    item.get("relationship")
                    for item in row.get("domain_relationships") or []
                    if isinstance(item, Mapping) and item.get("domain_id") == domain_id
                ],
                "capsule_ready": _as_mapping(row.get("capsule")).get("ready"),
                "comms_ready": _as_mapping(row.get("communication")).get("available_for_comms"),
            }
            for row in agent_rows
        ],
        "candidate_coverage_roles": [
            {
                "role_id": row.get("role_id"),
                "display_name": row.get("display_name"),
                "coverage_class": _coverage_key_for_domain(domain),
                "capsule_ready": _as_mapping(row.get("capsule")).get("ready"),
                "comms_ready": _as_mapping(row.get("communication")).get("available_for_comms"),
                "mount_id": _as_mapping(row.get("codex_mount")).get("mount_id"),
                "mount_domain": _as_mapping(row.get("codex_mount")).get("domain_id"),
            }
            for row in candidate_coverage_rows
        ],
        "gaps": gaps,
    }
