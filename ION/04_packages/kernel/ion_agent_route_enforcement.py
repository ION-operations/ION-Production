"""Hard route enforcement for high-stakes Codex/agent work packets.

This module validates structured route metadata and model override fields. It
does not grant authority or execute work; it only blocks ambiguous or
under-specified packets before they can silently fall back to default Codex
model routing.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

SCHEMA_ID = "ion.agent_route_enforcement_receipt.v1"
REQUIRED_HIGH_STAKES_MODEL = "gpt-5.5"
REQUIRED_HIGH_STAKES_REASONING_EFFORTS = ("high", "xhigh")
OPERATOR_ARTIFACT_HYGIENE_SECTION = "### OPERATOR ARTIFACT HYGIENE"

HIGH_STAKES_ROUTE_FAMILIES = {
    "red_alert",
    "action_native_mount",
    "authority_security",
    "authority",
    "security",
    "gpt_builder",
    "settlement",
    "branch_gateway_mount_equivalence",
    "operator_release_packaging",
}

HIGH_STAKES_WORK_CLASSES = {
    "red_alert",
    "action_native_mount",
    "authority_security",
    "authority",
    "security",
    "gpt_builder",
    "settlement",
    "branch_gateway_mount_equivalence",
    "operator_release_packaging",
}

HIGH_STAKES_RISK_LEVELS = {"red_alert", "critical"}

OPERATOR_ARTIFACT_ROUTE_FAMILIES = {
    "operator_release_packaging",
    "gpt_builder",
    "release_packaging",
    "upload_packaging",
}

OPERATOR_ARTIFACT_WORK_CLASSES = {
    "operator_release_packaging",
    "gpt_builder",
    "release_packaging",
    "upload_packaging",
    "package_release",
}

PROSE_GUARDRAIL_PATTERNS = (
    "red alert",
    "action-native",
    "action native",
    "authority/security",
    "authority security",
    "gpt builder",
    "settlement",
    "branch gateway mount equivalence",
    "operator release packaging",
)


def _normalize(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")


def _raw_text(value: Any) -> str:
    return str(value or "").strip()


def _route_metadata(payload: Mapping[str, Any]) -> dict[str, Any]:
    model_move = payload.get("codex_model_move") if isinstance(payload.get("codex_model_move"), Mapping) else {}
    work_class_raw = (
        _raw_text(payload.get("work_class"))
        or _raw_text(payload.get("workload_class"))
        or _raw_text(model_move.get("work_class"))
        or "general_codex_work"
    )
    risk_level_raw = _raw_text(payload.get("risk_level")) or _raw_text(payload.get("risk")) or "low"
    route_family_raw = (
        _raw_text(payload.get("route_family"))
        or _raw_text(payload.get("request_family"))
        or _raw_text(payload.get("request_kind"))
        or "general_codex_work"
    )
    return {
        "work_class": _normalize(work_class_raw),
        "risk_level": _normalize(risk_level_raw),
        "route_family": _normalize(route_family_raw),
        "raw": {
            "work_class": work_class_raw,
            "risk_level": risk_level_raw,
            "route_family": route_family_raw,
        },
        "explicit_fields": {
            "work_class": bool(_raw_text(payload.get("work_class")) or _raw_text(payload.get("workload_class"))),
            "risk_level": bool(_raw_text(payload.get("risk_level")) or _raw_text(payload.get("risk"))),
            "route_family": bool(_raw_text(payload.get("route_family")) or _raw_text(payload.get("request_family"))),
        },
    }


def _metadata_is_high_stakes(metadata: Mapping[str, Any]) -> bool:
    return (
        str(metadata.get("route_family") or "") in HIGH_STAKES_ROUTE_FAMILIES
        or str(metadata.get("work_class") or "") in HIGH_STAKES_WORK_CLASSES
        or str(metadata.get("risk_level") or "") in HIGH_STAKES_RISK_LEVELS
    )


def _metadata_requires_operator_artifact_hygiene(metadata: Mapping[str, Any]) -> bool:
    return (
        str(metadata.get("route_family") or "") in OPERATOR_ARTIFACT_ROUTE_FAMILIES
        or str(metadata.get("work_class") or "") in OPERATOR_ARTIFACT_WORK_CLASSES
    )


def _objective_has_high_stakes_prose_guardrail(payload: Mapping[str, Any]) -> bool:
    objective = _raw_text(payload.get("objective")).lower()
    return any(pattern in objective for pattern in PROSE_GUARDRAIL_PATTERNS)


def _override_fields(payload: Mapping[str, Any]) -> dict[str, str]:
    override = payload.get("codex_model_override") if isinstance(payload.get("codex_model_override"), Mapping) else {}
    selected_model = (
        _raw_text(override.get("selected_model"))
        or _raw_text(override.get("model"))
        or _raw_text(override.get("requested_model"))
    )
    selected_effort = (
        _raw_text(override.get("selected_reasoning_effort"))
        or _raw_text(override.get("reasoning_effort"))
        or _raw_text(override.get("requested_reasoning_effort"))
    )
    return {
        "codex_model_override.selected_model": selected_model,
        "codex_model_override.selected_reasoning_effort": selected_effort,
        "requested_model": _raw_text(payload.get("requested_model")),
        "requested_reasoning_effort": _raw_text(payload.get("requested_reasoning_effort")),
        "model_override_reason": _raw_text(payload.get("model_override_reason")),
        "codex_model_override.reason": _raw_text(override.get("reason")),
    }


def validate_codex_route_enforcement(payload: Mapping[str, Any], *, source: str) -> dict[str, Any]:
    """Return a proof-bearing receipt for Codex route/model enforcement."""

    metadata = _route_metadata(payload)
    high_stakes = _metadata_is_high_stakes(metadata)
    prose_guardrail = _objective_has_high_stakes_prose_guardrail(payload)
    operator_artifact_hygiene_required = _metadata_requires_operator_artifact_hygiene(metadata)
    fields = _override_fields(payload)
    findings: list[str] = []

    if prose_guardrail and not high_stakes:
        findings.append("structured_route_metadata_required_for_high_stakes_objective")

    if high_stakes:
        explicit = metadata.get("explicit_fields") if isinstance(metadata.get("explicit_fields"), Mapping) else {}
        for key in ("work_class", "risk_level", "route_family"):
            if not bool(explicit.get(key)):
                findings.append(f"high_stakes_{key}_required")
        if str(metadata.get("risk_level") or "") not in {"high", "critical", "red_alert"}:
            findings.append("high_stakes_risk_level_must_be_high_critical_or_red_alert")
        if not _raw_text(payload.get("idempotency_key")):
            findings.append("high_stakes_idempotency_key_required")
        if fields["codex_model_override.selected_model"] != REQUIRED_HIGH_STAKES_MODEL:
            findings.append("high_stakes_codex_model_override_selected_model_must_be_gpt_5_5")
        if fields["codex_model_override.selected_reasoning_effort"] not in REQUIRED_HIGH_STAKES_REASONING_EFFORTS:
            findings.append("high_stakes_codex_model_override_reasoning_effort_must_be_high_or_xhigh")
        if fields["requested_model"] != REQUIRED_HIGH_STAKES_MODEL:
            findings.append("high_stakes_requested_model_must_be_gpt_5_5")
        if fields["requested_reasoning_effort"] not in REQUIRED_HIGH_STAKES_REASONING_EFFORTS:
            findings.append("high_stakes_requested_reasoning_effort_must_be_high_or_xhigh")
        if not fields["model_override_reason"]:
            findings.append("high_stakes_model_override_reason_required")

    return {
        "schema_id": SCHEMA_ID,
        "ok": not findings,
        "source": source,
        "finding": findings[0] if findings else None,
        "findings": findings,
        "route_metadata": metadata,
        "high_stakes": high_stakes,
        "prose_guardrail_triggered": prose_guardrail,
        "model_override_receipt_required": high_stakes,
        "operator_artifact_hygiene_required": operator_artifact_hygiene_required,
        "operator_artifact_hygiene_gate": {
            "required": operator_artifact_hygiene_required,
            "checker": "ION/04_packages/kernel/ion_operator_artifact_hygiene_check.py",
            "required_section": OPERATOR_ARTIFACT_HYGIENE_SECTION,
            "allowed_operator_outcomes": [
                "OPERATOR_FINAL",
                "ION_GPT_FINAL_OPERATOR_UPLOAD_KIT_<timestamp>",
                "BLOCKED_NO_OPERATOR_ARTIFACT",
            ],
            "internal_material_policy": "INTERNAL_REFERENCE_DO_NOT_TOUCH",
        },
        "required_model_override": {
            "selected_model": REQUIRED_HIGH_STAKES_MODEL,
            "selected_reasoning_efforts": list(REQUIRED_HIGH_STAKES_REASONING_EFFORTS),
        } if high_stakes else None,
        "observed_model_override_fields": fields,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }


def apply_route_enforcement_metadata(payload: dict[str, Any], receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Persist normalized route metadata and gate flags into a work packet."""

    metadata = receipt.get("route_metadata") if isinstance(receipt.get("route_metadata"), Mapping) else {}
    for key in ("work_class", "risk_level", "route_family"):
        value = str(metadata.get(key) or "").strip()
        if value:
            payload[key] = value
    payload["route_enforcement_receipt"] = dict(receipt)
    payload["operator_artifact_hygiene_required"] = bool(receipt.get("operator_artifact_hygiene_required"))
    return payload


def operator_artifact_hygiene_required(payload: Mapping[str, Any]) -> bool:
    receipt = payload.get("route_enforcement_receipt") if isinstance(payload.get("route_enforcement_receipt"), Mapping) else None
    if receipt is not None:
        return bool(receipt.get("operator_artifact_hygiene_required"))
    return bool(validate_codex_route_enforcement(payload, source="operator_artifact_hygiene_probe").get("operator_artifact_hygiene_required"))
