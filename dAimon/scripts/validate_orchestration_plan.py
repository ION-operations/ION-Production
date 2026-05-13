"""Validate dAimon orchestration planning assets.

This script checks the repo-owned orchestration contracts that govern the build.
It intentionally validates structure and proof boundaries, not business truth.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "sample_outputs" / "orchestration_validation.json"


REQUIRED_FILES = [
    "orchestration/product_layers.json",
    "orchestration/domain_registry.json",
    "orchestration/template_registry.json",
    "orchestration/receipt_registry.json",
    "orchestration/build_roadmap.json",
    "orchestration/test_matrix.json",
    "orchestration/management_cadence.json",
    "orchestration/ui_surface_plan.json",
    "orchestration/partner_adapter_registry.json",
    "orchestration/connector_expansion_registry.json",
    "docs/full_orchestration_plan.md",
    "docs/self_demonstrating_video_agent.md",
    "docs/contest_vertical_slice_plan.md",
    "docs/custom_gpt_expansion_plan.md",
    "docs/ui_canon_product_plan.md",
    "docs/partner_ecosystem_expansion.md",
    "docs/custom_gpt_action_connection.md",
    "docs/gitlab_connection_readiness.md",
]

REQUIRED_LAYERS = {
    "continuity_substrate",
    "generative_governance_engine",
    "enterprise_trust_layer",
    "partner_adapter_fabric",
    "contest_vertical_slice",
}

REQUIRED_DOMAINS = {
    "continuity_substrate",
    "generative_governance",
    "capability_routing",
    "mcp_visibility",
    "enterprise_trust",
    "cloud_runtime",
    "demo_video_agent",
    "product_ops",
    "ion_product_boundary",
    "technology_fabric",
    "portable_continuation",
    "voice_local_work",
    "security_red_team",
    "project_identity_collaboration",
}

REQUIRED_CORE_TEMPLATES = {
    "import_witness_bundle",
    "classify_continuity_objects",
    "route_objective",
    "settle_outputs",
    "issue_receipt",
    "resolve_inheritance",
    "mcp_visibility_trace",
}

REQUIRED_EXPANSION_TEMPLATES = {
    "settle_product_boundary",
    "register_adapter_manifest",
    "normalize_adapter_object",
    "settle_cross_surface_path",
    "export_portable_context_package",
    "replay_continuation_packet",
    "route_voice_packet",
    "confirm_high_risk_voice_intent",
    "run_security_lab_scenario",
    "issue_containment_receipt",
    "create_first_contact_package",
    "pair_project_connector",
    "invite_project_collaborator",
}

REQUIRED_TEST_GROUPS = {
    "local_scaffold",
    "orchestration_contracts",
    "live_mongodb",
    "google_cloud",
    "agent_builder",
    "google_user_access",
    "security",
    "demo_video",
    "partner_adapter_registry",
    "adapter_fabric",
    "portable_continuation",
    "voice_safety",
    "project_identity",
    "red_team_lab",
}

REQUIRED_RECEIPT_FIELDS = {
    "receipt_id",
    "template_id",
    "domain_id",
    "objective",
    "proof_refs",
    "authority_scope",
    "settlement_decision",
    "accepted_state_changed",
    "external_mutation_attempted",
    "inheritance_permissions",
}

REQUIRED_PARTNERS = {
    "mongodb",
    "arize",
    "elastic",
    "fivetran",
    "gitlab",
}

REQUIRED_CONNECTORS = {
    "custom_gpt_actions",
    "gitlab",
    "arize_phoenix",
    "elastic",
    "fivetran",
}


class ValidationError(Exception):
    """Raised when orchestration assets fail validation."""


def load_json(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{relative_path} is not valid JSON: {exc}") from exc


def require_non_empty(record: dict[str, Any], key: str, label: str) -> None:
    if key not in record:
        raise ValidationError(f"{label} missing required key {key!r}")
    value = record[key]
    if value in ("", None, [], {}):
        raise ValidationError(f"{label} has empty required key {key!r}")


def validate_required_files() -> list[str]:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        raise ValidationError(f"Missing required orchestration files: {missing}")
    return REQUIRED_FILES


def validate_layers(data: dict[str, Any]) -> dict[str, int]:
    layers = data.get("layers", [])
    if not isinstance(layers, list):
        raise ValidationError("product_layers.json field 'layers' must be a list")
    layer_ids = {layer.get("layer_id") for layer in layers}
    missing = REQUIRED_LAYERS - layer_ids
    if missing:
        raise ValidationError(f"Missing required product layers: {sorted(missing)}")
    for layer in layers:
        label = f"layer {layer.get('layer_id')}"
        for key in (
            "name",
            "question_answered",
            "responsibilities",
            "entrypoints",
            "current_status",
            "evidence",
            "next_build_targets",
            "tests",
        ):
            require_non_empty(layer, key, label)
    return {"layer_count": len(layers)}


def validate_domains(data: dict[str, Any]) -> dict[str, int]:
    domains = data.get("domains", [])
    if not isinstance(domains, list):
        raise ValidationError("domain_registry.json field 'domains' must be a list")
    domain_ids = {domain.get("domain_id") for domain in domains}
    missing = REQUIRED_DOMAINS - domain_ids
    if missing:
        raise ValidationError(f"Missing required domains: {sorted(missing)}")
    for domain in domains:
        label = f"domain {domain.get('domain_id')}"
        for key in (
            "name",
            "layer_ids",
            "purpose",
            "owner_role",
            "context_objects",
            "templates",
            "proof_obligations",
            "authority_ceiling",
            "settlement_rules",
            "neighboring_domain_routes",
            "fission_triggers",
        ):
            require_non_empty(domain, key, label)
    return {"domain_count": len(domains)}


def validate_templates(data: dict[str, Any], domain_ids: set[str]) -> dict[str, int]:
    templates = data.get("templates", [])
    if not isinstance(templates, list):
        raise ValidationError("template_registry.json field 'templates' must be a list")
    template_ids = {template.get("template_id") for template in templates}
    missing = (REQUIRED_CORE_TEMPLATES | REQUIRED_EXPANSION_TEMPLATES) - template_ids
    if missing:
        raise ValidationError(f"Missing required templates: {sorted(missing)}")
    for template in templates:
        label = f"template {template.get('template_id')}"
        for key in (
            "name",
            "action_type",
            "domain_id",
            "required_context",
            "inputs",
            "outputs",
            "proof_obligations",
            "authority_ceiling",
            "state_mutation",
            "settlement_path",
            "validation",
        ):
            require_non_empty(template, key, label)
        if template["domain_id"] not in domain_ids:
            raise ValidationError(
                f"{label} references unknown domain_id {template['domain_id']!r}"
            )
    return {"template_count": len(templates)}


def validate_receipts(data: dict[str, Any]) -> dict[str, int]:
    fields = set(data.get("required_receipt_fields", []))
    missing = REQUIRED_RECEIPT_FIELDS - fields
    if missing:
        raise ValidationError(f"Missing required receipt fields: {sorted(missing)}")
    receipt_types = data.get("receipt_types", [])
    if not isinstance(receipt_types, list) or not receipt_types:
        raise ValidationError("receipt_registry.json must define receipt_types")
    for receipt_type in receipt_types:
        label = f"receipt_type {receipt_type.get('receipt_type_id')}"
        for key in (
            "name",
            "purpose",
            "required_extra_fields",
            "inheritance_rule",
        ):
            require_non_empty(receipt_type, key, label)
    return {
        "receipt_type_count": len(receipt_types),
        "required_receipt_field_count": len(fields),
    }


def validate_roadmap(data: dict[str, Any]) -> dict[str, int]:
    phases = data.get("phases", [])
    if not isinstance(phases, list) or not phases:
        raise ValidationError("build_roadmap.json must define phases")
    for phase in phases:
        label = f"roadmap phase {phase.get('phase_id')}"
        for key in (
            "name",
            "status",
            "objectives",
            "deliverables",
            "dependencies",
            "evidence",
            "tests",
            "exit_criteria",
        ):
            require_non_empty(phase, key, label)
    return {"roadmap_phase_count": len(phases)}


def validate_test_matrix(data: dict[str, Any]) -> dict[str, int]:
    groups = data.get("test_groups", [])
    if not isinstance(groups, list):
        raise ValidationError("test_matrix.json field 'test_groups' must be a list")
    group_ids = {group.get("group_id") for group in groups}
    missing = REQUIRED_TEST_GROUPS - group_ids
    if missing:
        raise ValidationError(f"Missing required test groups: {sorted(missing)}")
    for group in groups:
        label = f"test group {group.get('group_id')}"
        for key in (
            "name",
            "scope",
            "required_env",
            "commands",
            "proves",
            "does_not_prove",
            "gate",
        ):
            if key == "required_env":
                if key not in group:
                    raise ValidationError(f"{label} missing required key {key!r}")
            else:
                require_non_empty(group, key, label)
    return {"test_group_count": len(groups)}


def validate_management(data: dict[str, Any]) -> dict[str, int]:
    cadences = data.get("cadences", [])
    lanes = data.get("work_lanes", [])
    if not isinstance(cadences, list) or not cadences:
        raise ValidationError("management_cadence.json must define cadences")
    if not isinstance(lanes, list) or not lanes:
        raise ValidationError("management_cadence.json must define work_lanes")
    for cadence in cadences:
        label = f"cadence {cadence.get('cadence_id')}"
        for key in ("name", "frequency", "steps", "outputs"):
            require_non_empty(cadence, key, label)
    for lane in lanes:
        label = f"work lane {lane.get('lane_id')}"
        for key in ("name", "owned_domains", "definition_of_done"):
            require_non_empty(lane, key, label)
    return {"cadence_count": len(cadences), "work_lane_count": len(lanes)}


def validate_ui_surface(data: dict[str, Any]) -> dict[str, int]:
    for key in (
        "visual_language",
        "shell",
        "navigation_groups",
        "visual_instruments",
        "build_phases",
        "immediate_next_slice",
    ):
        require_non_empty(data, key, "ui_surface_plan")
    instruments = data["visual_instruments"]
    phases = data["build_phases"]
    if not isinstance(instruments, list) or len(instruments) < 5:
        raise ValidationError("ui_surface_plan.json must define at least 5 visual instruments")
    if not isinstance(phases, list) or len(phases) < 3:
        raise ValidationError("ui_surface_plan.json must define at least 3 UI build phases")
    for instrument in instruments:
        label = f"visual instrument {instrument.get('id')}"
        for key in ("id", "purpose", "replaces_generic_ui"):
            require_non_empty(instrument, key, label)
    return {
        "ui_visual_instrument_count": len(instruments),
        "ui_build_phase_count": len(phases),
    }


def validate_partner_adapters(data: dict[str, Any]) -> dict[str, int]:
    adapters = data.get("partner_adapters", [])
    if not isinstance(adapters, list):
        raise ValidationError("partner_adapter_registry.json field 'partner_adapters' must be a list")
    partner_ids = {adapter.get("partner_id") for adapter in adapters}
    missing = REQUIRED_PARTNERS - partner_ids
    if missing:
        raise ValidationError(f"Missing required partner adapters: {sorted(missing)}")
    if data.get("contest_primary_track") != "mongodb":
        raise ValidationError("partner_adapter_registry.json must keep MongoDB as contest_primary_track")
    for adapter in adapters:
        label = f"partner adapter {adapter.get('partner_id')}"
        for key in (
            "name",
            "role",
            "status",
            "governed_surfaces",
            "read_capabilities",
            "write_capabilities",
            "authority_boundary",
            "proof_obligations",
            "current_evidence",
            "next_gate",
            "non_claims",
        ):
            require_non_empty(adapter, key, label)
    mongodb = next(adapter for adapter in adapters if adapter.get("partner_id") == "mongodb")
    if "primary" not in str(mongodb.get("status", "")):
        raise ValidationError("MongoDB adapter must be marked as the primary proof substrate")
    return {"partner_adapter_count": len(adapters)}


def validate_connector_expansion(data: dict[str, Any]) -> dict[str, int]:
    connectors = data.get("connector_targets", [])
    if not isinstance(connectors, list):
        raise ValidationError("connector_expansion_registry.json field 'connector_targets' must be a list")
    connector_ids = {connector.get("connector_id") for connector in connectors}
    missing = REQUIRED_CONNECTORS - connector_ids
    if missing:
        raise ValidationError(f"Missing required connector targets: {sorted(missing)}")
    for connector in connectors:
        label = f"connector target {connector.get('connector_id')}"
        for key in (
            "name",
            "category",
            "status",
            "priority",
            "connection_surface",
            "required_env",
            "secret_handling",
            "read_capabilities",
            "write_capabilities",
            "authority_boundary",
            "proof_gates",
            "current_evidence",
            "next_gate",
            "non_claims",
        ):
            require_non_empty(connector, key, label)
    return {"connector_target_count": len(connectors)}


def main() -> int:
    try:
        validated_files = validate_required_files()
        product_layers = load_json("orchestration/product_layers.json")
        domain_registry = load_json("orchestration/domain_registry.json")
        template_registry = load_json("orchestration/template_registry.json")
        receipt_registry = load_json("orchestration/receipt_registry.json")
        build_roadmap = load_json("orchestration/build_roadmap.json")
        test_matrix = load_json("orchestration/test_matrix.json")
        management_cadence = load_json("orchestration/management_cadence.json")
        ui_surface_plan = load_json("orchestration/ui_surface_plan.json")
        partner_adapter_registry = load_json("orchestration/partner_adapter_registry.json")
        connector_expansion_registry = load_json("orchestration/connector_expansion_registry.json")

        layer_summary = validate_layers(product_layers)
        domain_summary = validate_domains(domain_registry)
        domain_ids = {domain["domain_id"] for domain in domain_registry["domains"]}
        template_summary = validate_templates(template_registry, domain_ids)
        receipt_summary = validate_receipts(receipt_registry)
        roadmap_summary = validate_roadmap(build_roadmap)
        test_summary = validate_test_matrix(test_matrix)
        management_summary = validate_management(management_cadence)
        ui_surface_summary = validate_ui_surface(ui_surface_plan)
        partner_summary = validate_partner_adapters(partner_adapter_registry)
        connector_summary = validate_connector_expansion(connector_expansion_registry)

        result = {
            "ok": True,
            "project": "dAimon",
            "validator": "scripts/validate_orchestration_plan.py",
            "validated_files": validated_files,
            "accepted_state_changed": False,
            "external_mutation_attempted": False,
            "summary": {
                **layer_summary,
                **domain_summary,
                **template_summary,
                **receipt_summary,
                **roadmap_summary,
                **test_summary,
                **management_summary,
                **ui_surface_summary,
                **partner_summary,
                **connector_summary,
                "core_template_count": len(REQUIRED_CORE_TEMPLATES),
                "expansion_template_count": len(REQUIRED_EXPANSION_TEMPLATES),
            },
        }
        OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 0
    except ValidationError as exc:
        result = {
            "ok": False,
            "project": "dAimon",
            "validator": "scripts/validate_orchestration_plan.py",
            "accepted_state_changed": False,
            "external_mutation_attempted": False,
            "error": str(exc),
        }
        OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
