"""AI movement target binding for Codex work requests.

Queue runners may reject legacy packets that do not declare a target root.
This helper keeps request emitters aligned on the same target evidence shape.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

SCHEMA_ID = "ion.codex_work_request_target_binding.v1"
AUDIT_PROJECTION_SCHEMA_ID = "ion.codex_work_request_target_binding_audit_projection.v1"
TEMPLATE_REF = "ION/07_templates/ai_movement/ION_CODEX_WORK_REQUEST_TARGET_BINDING.template.yaml"

TARGETS: dict[str, dict[str, str]] = {
    "active_ion_control": {
        "family": "ION_Developement",
        "movement_class": "ION_KERNEL_CONTROL_MOVEMENT",
        "root_relation": "active_ion_control_root",
    },
    "ion_gpt": {
        "family": "ION_GPT",
        "movement_class": "CUSTOM_GPT_RELEASE_MOVEMENT",
        "root_relation": "product_projection_root",
    },
    "product_packager": {
        "family": "product_packager",
        "movement_class": "CUSTOM_GPT_RELEASE_MOVEMENT",
        "root_relation": "product_projection_root",
    },
    "browser_extension": {
        "family": "browser_extension",
        "movement_class": "BROWSER_EXTENSION_MOVEMENT",
        "root_relation": "sibling_project_root",
    },
    "mcp": {
        "family": "mcp",
        "movement_class": "MCP_BRIDGE_MOVEMENT",
        "root_relation": "sibling_project_root",
    },
    "local_daemon": {
        "family": "local_daemon",
        "movement_class": "LOCAL_DAEMON_MOVEMENT",
        "root_relation": "sibling_project_root",
    },
    "systemd": {
        "family": "systemd",
        "movement_class": "LOCAL_DAEMON_MOVEMENT",
        "root_relation": "sibling_project_root",
    },
    "daimon": {
        "family": "dAimon",
        "movement_class": "DAIMON_PROJECT_MOVEMENT",
        "root_relation": "external_governed_project_root",
    },
    "needs_routed": {
        "family": "Needs_Routed",
        "movement_class": "INTAKE_ROUTING_MOVEMENT",
        "root_relation": "intake_root",
    },
    "ion_exports_local": {
        "family": "ION_EXPORTS_LOCAL",
        "movement_class": "EXPORT_PACKAGE_MOVEMENT",
        "root_relation": "export_root",
    },
    "quarentine": {
        "family": "quarentine",
        "movement_class": "ARCHIVE_REFERENCE_MOVEMENT",
        "root_relation": "archive_witness_root",
    },
    "aim_os": {
        "family": "AIM-OS",
        "movement_class": "ARCHIVE_REFERENCE_MOVEMENT",
        "root_relation": "reference_library_root",
    },
    "atlas": {
        "family": "ATLAS",
        "movement_class": "ARCHIVE_REFERENCE_MOVEMENT",
        "root_relation": "reference_library_root",
    },
    "wisdomnet": {
        "family": "wisdomNET",
        "movement_class": "ARCHIVE_REFERENCE_MOVEMENT",
        "root_relation": "reference_library_root",
    },
}

TARGET_ALIASES = {
    "active": "active_ion_control",
    "active_repo": "active_ion_control",
    "ion": "active_ion_control",
    "ion_developement": "active_ion_control",
    "ion_development": "active_ion_control",
    "kernel": "active_ion_control",
    "agent_invocation": "active_ion_control",
    "bounded_agent_invocation": "active_ion_control",
    "codex_work": "active_ion_control",
    "ion_gpt": "ion_gpt",
    "custom_gpt": "ion_gpt",
    "gpt": "ion_gpt",
    "gpt_builder": "ion_gpt",
    "action_schema_release": "ion_gpt",
    "operator_release_packaging": "ion_gpt",
    "browser_extension": "browser_extension",
    "extension": "browser_extension",
    "chatops_extension": "browser_extension",
    "mcp": "mcp",
    "mcp_bridge": "mcp",
    "local_daemon": "local_daemon",
    "daemon": "local_daemon",
    "runtime_service": "local_daemon",
    "systemd": "systemd",
    "daimon": "daimon",
    "d_aimon": "daimon",
    "daimon_project": "daimon",
    "needs_routed": "needs_routed",
    "intake": "needs_routed",
    "routing_intake": "needs_routed",
    "ion_exports_local": "ion_exports_local",
    "exports": "ion_exports_local",
    "export": "ion_exports_local",
    "clean_export": "ion_exports_local",
    "quarentine": "quarentine",
    "quarantine": "quarentine",
    "archive": "quarentine",
    "aim_os": "aim_os",
    "atlas": "atlas",
    "wisdomnet": "wisdomnet",
}

ROOT_ID_BY_FAMILY = {str(meta["family"]).lower(): root_id for root_id, meta in TARGETS.items()}
ROOT_ID_BY_MOVEMENT_CLASS = {
    str(meta["movement_class"]): root_id
    for root_id, meta in TARGETS.items()
    if root_id not in {"product_packager", "systemd", "aim_os", "atlas", "wisdomnet"}
}

TARGET_FIELDS = (
    "ai_movement_target_root_id",
    "target_root_id",
    "workspace_target_root_id",
    "target_workspace_root_id",
    "target_project_root_id",
    "target_family",
    "target_project",
    "target_project_root_name",
)
DOMAIN_FIELDS = (
    "movement_domain",
    "domain",
    "project_id",
    "project",
    "request_kind",
    "route_family",
    "work_class",
    "workload_class",
)
PROJECT_SUBPATH_FIELDS = (
    "target_project_subpath",
    "target_content_subpath",
    "project_subpath",
    "workspace_project_subpath",
)
WRITE_FIELDS = (
    "planned_writes",
    "allowed_write_paths",
    "target_write_paths",
    "write_scope",
    "expected_touched_paths",
)
ARTIFACT_FIELDS = (
    "planned_artifacts",
    "artifact_paths",
    "planned_output_artifacts",
)


def _slug_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")


def normalize_target_root_id(value: Any) -> str | None:
    key = _slug_key(value)
    if not key:
        return None
    if key in TARGETS:
        return key
    if key in TARGET_ALIASES:
        return TARGET_ALIASES[key]
    return ROOT_ID_BY_FAMILY.get(key)


def _normalize_movement_class(value: Any) -> str | None:
    text = str(value or "").strip()
    return text if text in ROOT_ID_BY_MOVEMENT_CLASS else None


def _path_values(request: Mapping[str, Any], fields: tuple[str, ...]) -> list[str]:
    values: list[str] = []
    for field in fields:
        raw = request.get(field)
        if raw is None:
            continue
        items = raw if isinstance(raw, list) else [raw]
        for item in items:
            if isinstance(item, Mapping):
                path = str(item.get("path") or item.get("raw_path") or item.get("target") or "").strip()
            else:
                path = str(item or "").strip()
            if path:
                values.append(path)
    return values


def _target_from_path(path_value: str) -> str | None:
    clean = path_value.replace("\\", "/").strip()
    while clean.startswith("./"):
        clean = clean[2:]
    parts = [part for part in clean.split("/") if part and part != ".."]
    if not parts:
        return None
    first = parts[0]
    if first == "ION":
        return "active_ion_control"
    return ROOT_ID_BY_FAMILY.get(first.lower()) or normalize_target_root_id(first)


def _resolve_target(request: Mapping[str, Any], default_target_root_id: str) -> tuple[str, str, str | None]:
    for field in TARGET_FIELDS:
        target = normalize_target_root_id(request.get(field))
        if target:
            return target, f"request.{field}", None
    movement_class = _normalize_movement_class(request.get("movement_class"))
    if movement_class:
        return ROOT_ID_BY_MOVEMENT_CLASS[movement_class], "request.movement_class", movement_class
    for field in DOMAIN_FIELDS:
        target = normalize_target_root_id(request.get(field))
        if target:
            return target, f"request.{field}", None
    for field in WRITE_FIELDS + ARTIFACT_FIELDS:
        for path in _path_values(request, (field,)):
            target = _target_from_path(path)
            if target:
                return target, f"request.{field}", None
    return normalize_target_root_id(default_target_root_id) or "active_ion_control", "default.active_ion_control", None


def _declared_ai_movement_envelope(request: Mapping[str, Any]) -> Mapping[str, Any]:
    raw = request.get("ai_movement_root_envelope")
    if not isinstance(raw, Mapping):
        return {}
    nested = raw.get("ai_movement_root_envelope")
    return nested if isinstance(nested, Mapping) else raw


def _runner_target_evidence(request: Mapping[str, Any]) -> tuple[str | None, str | None, str | None]:
    for field in TARGET_FIELDS:
        target = normalize_target_root_id(request.get(field))
        if target:
            return target, f"request.{field}", None
    declared = _declared_ai_movement_envelope(request)
    for field in TARGET_FIELDS:
        target = normalize_target_root_id(declared.get(field))
        if target:
            return target, f"request.ai_movement_root_envelope.{field}", None
    movement_class = _normalize_movement_class(request.get("movement_class"))
    if movement_class:
        return ROOT_ID_BY_MOVEMENT_CLASS[movement_class], "request.movement_class", movement_class
    declared_movement_class = _normalize_movement_class(declared.get("movement_class"))
    if declared_movement_class:
        return ROOT_ID_BY_MOVEMENT_CLASS[declared_movement_class], "request.ai_movement_root_envelope.movement_class", declared_movement_class
    for field in WRITE_FIELDS + ARTIFACT_FIELDS:
        for path in _path_values(request, (field,)):
            target = _target_from_path(path)
            if target:
                return target, f"request.{field}", None
    return None, None, None


def _movement_class_for_target(target_root_id: str, request: Mapping[str, Any], explicit: str | None) -> str:
    requested = explicit or str(request.get("movement_class") or "").strip()
    if requested:
        return requested
    return TARGETS.get(target_root_id, TARGETS["active_ion_control"])["movement_class"]


def _first_non_empty_paths(request: Mapping[str, Any], fields: tuple[str, ...]) -> list[str]:
    for field in fields:
        paths = _path_values(request, (field,))
        if paths:
            return paths
    return []


def _first_text(request: Mapping[str, Any], fields: tuple[str, ...]) -> tuple[str, str] | tuple[None, None]:
    for field in fields:
        text = str(request.get(field) or "").strip()
        if text:
            return field, text
    return None, None


def build_codex_work_request_target_binding(
    request: Mapping[str, Any],
    *,
    source: str,
    default_target_root_id: str = "active_ion_control",
) -> dict[str, Any]:
    target_root_id, binding_source, movement_from_source = _resolve_target(request, default_target_root_id)
    movement_class = _movement_class_for_target(target_root_id, request, movement_from_source)
    meta = TARGETS.get(target_root_id, TARGETS["active_ion_control"])
    project_subpath_field, project_subpath = _first_text(request, PROJECT_SUBPATH_FIELDS)
    return {
        "schema_id": SCHEMA_ID,
        "template_ref": TEMPLATE_REF,
        "source": source,
        "target_root_id": target_root_id,
        "movement_class": movement_class,
        "target_family": meta["family"],
        "root_relation": meta["root_relation"],
        "binding_source": binding_source,
        "target_project_subpath": project_subpath,
        "target_project_subpath_source": f"request.{project_subpath_field}" if project_subpath_field else None,
        "planned_writes": _first_non_empty_paths(request, WRITE_FIELDS),
        "planned_artifacts": _first_non_empty_paths(request, ARTIFACT_FIELDS),
        "required_for_queue_preflight": True,
        "runner_legacy_default_allowed": False,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def apply_codex_work_request_target_binding(
    payload: dict[str, Any],
    request: Mapping[str, Any],
    *,
    source: str,
    default_target_root_id: str = "active_ion_control",
) -> dict[str, Any]:
    binding = build_codex_work_request_target_binding(
        request,
        source=source,
        default_target_root_id=default_target_root_id,
    )
    payload.setdefault("target_root_id", binding["target_root_id"])
    payload.setdefault("movement_class", binding["movement_class"])
    for field in PROJECT_SUBPATH_FIELDS:
        value = str(request.get(field) or "").strip()
        if value and field not in payload:
            payload[field] = value
    if binding["planned_writes"] and "planned_writes" not in payload:
        payload["planned_writes"] = list(binding["planned_writes"])
    if binding["planned_artifacts"] and "planned_artifacts" not in payload:
        payload["planned_artifacts"] = list(binding["planned_artifacts"])
    payload["ai_movement_request_template"] = binding
    return binding


def compact_codex_work_request_target_binding_projection(request: Mapping[str, Any]) -> dict[str, Any]:
    binding = request.get("ai_movement_request_template")
    binding = binding if isinstance(binding, Mapping) else {}
    binding_schema = str(binding.get("schema_id") or "")
    template_present = binding_schema == SCHEMA_ID
    template_target = normalize_target_root_id(binding.get("target_root_id"))
    template_movement = str(binding.get("movement_class") or "").strip()
    runner_target, runner_source, runner_movement = _runner_target_evidence(request)
    top_target = normalize_target_root_id(request.get("target_root_id") or request.get("ai_movement_target_root_id"))
    top_movement = str(request.get("movement_class") or "").strip()
    blockers: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    if template_present:
        if not template_target:
            blockers.append({"code": "TARGET_BINDING_TEMPLATE_TARGET_MISSING", "detail": "ai_movement_request_template target_root_id is missing or unknown"})
        if not template_movement:
            blockers.append({"code": "TARGET_BINDING_TEMPLATE_MOVEMENT_MISSING", "detail": "ai_movement_request_template movement_class is missing"})
        if not runner_target:
            blockers.append({"code": "TARGET_BINDING_RUNNER_EVIDENCE_MISSING", "detail": "top-level request target evidence recognized by the queue runner is missing"})
        if template_target and runner_target and template_target != runner_target:
            blockers.append({"code": "TARGET_BINDING_TARGET_CONFLICT", "detail": "template target_root_id conflicts with runner-recognized request target evidence"})
        if template_movement and top_movement and template_movement != top_movement:
            blockers.append({"code": "TARGET_BINDING_MOVEMENT_CONFLICT", "detail": "template movement_class conflicts with top-level movement_class"})
        status = "TARGET_BINDING_CONFLICT" if blockers else "TARGET_BINDING_OK"
    elif runner_target:
        warnings.append({"code": "TARGET_BINDING_TEMPLATE_MISSING", "detail": "request has runner-recognized target evidence but no generated target binding template"})
        status = "LEGACY_TARGET_EVIDENCE_ONLY"
    else:
        blockers.append({"code": "TARGET_BINDING_MISSING", "detail": "request is missing ai_movement_request_template, target_root_id, movement_class, and target path evidence"})
        status = "TARGET_BINDING_MISSING"

    accepted = not blockers
    warning_level = "blocked" if blockers else ("warning" if warnings else "ok")
    return {
        "schema_id": AUDIT_PROJECTION_SCHEMA_ID,
        "accepted": accepted,
        "status": status,
        "warning_level": warning_level,
        "target_root_id": template_target or runner_target,
        "movement_class": template_movement or runner_movement or top_movement or None,
        "binding_source": binding.get("binding_source") or runner_source,
        "template_ref": binding.get("template_ref") or None,
        "template_present": template_present,
        "runner_target_evidence_present": bool(runner_target),
        "runner_target_evidence_source": runner_source,
        "top_level_target_root_id": top_target,
        "top_level_movement_class": top_movement or None,
        "runner_legacy_default_allowed": bool(binding.get("runner_legacy_default_allowed")) if binding else None,
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "blocker_codes": [item["code"] for item in blockers],
        "warning_codes": [item["code"] for item in warnings],
        "blockers": blockers,
        "warnings": warnings,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }
