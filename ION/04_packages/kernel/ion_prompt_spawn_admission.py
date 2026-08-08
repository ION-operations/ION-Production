"""Proof-bound admission validation shared by CLI carrier adapters.

The prompt-spawn executor issues the admission.  Carrier adapters independently
recompute and bind it before they inspect credentials, create artifacts, or
contact a provider.  This module grants no execution or accepted-state
authority.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any, Mapping

from .ion_directive_transport import (
    validate_directive_transport_binding,
)


# PCKT-DIRECTIVE-PROVENANCE-CLASSES-ON-SPAWN-ADMISSION — admission-side enum aligned
# with gate.spawn_lineage_provenance spawn_lineage_provenance_stamping_law.
DIRECTIVE_PROVENANCE_CLASSES = (
    "operator_direct",
    "parent_prose_orchestration",
    "operator_transport",
    "ion_handoff_relay",
    "spawn_plan_row",
    "inspection_mandate_default",
)

DIRECTIVE_PROVENANCE_CLASS_TO_LINEAGE = {
    "operator_direct": "operator_direct_lawful",
    "parent_prose_orchestration": "parent_prose_contaminated_witness",
    "operator_transport": "operator_transport_candidate",
    "ion_handoff_relay": "ion_handoff_relay_candidate",
    "spawn_plan_row": "spawn_plan_row_lawful",
    "inspection_mandate_default": "inspection_mandate_default_lawful",
}


def operator_direct_enabled() -> bool:
    """True when the operator is directing a run explicitly (ION_OPERATOR_DIRECT=1).

    Without this, a human-authored directive always resolves to
    ``parent_prose_orchestration`` (refused) and naming a domain explicitly is
    refused as ``parent_domain_selection_forbidden``.  The combination made it
    impossible for the operator to hand ION any work at all: the only runs that
    could be admitted were ION's own self-generated ones, which supply no
    work_class and therefore resolve to the read-only audit template.
    """

    return str(os.environ.get("ION_OPERATOR_DIRECT", "")).strip().lower() in {
        "1",
        "true",
        "yes",
    }


SPAWN_PLAN_SOURCE_KINDS = frozenset({"role_spawn_plan", "spawn_plan_row"})
TRANSPORT_EXEMPT_PROVENANCE_CLASSES = frozenset(
    {"spawn_plan_row", "inspection_mandate_default", "operator_direct"}
)
AUTO_ROUTING_EXEMPT_PROVENANCE_CLASSES = frozenset({"spawn_plan_row"})

_HANDOFF_OBJECTIVE_MARKERS = (
    "prompt_spawn_",
    "accepted ruling",
    "your own accepted ruling",
    "pckt-",
    "hand-off",
    "handoff",
    "named owner",
)


def _normalize_routing_token(value: Any) -> str:
    return str(value or "").strip().lower()


def is_parent_fixed_routing(routing_request_basis: Mapping[str, Any] | None) -> bool:
    """True when routing_request_basis pins carrier/model instead of auto routing."""

    if not isinstance(routing_request_basis, Mapping):
        return False
    carrier = _normalize_routing_token(routing_request_basis.get("requested_carrier"))
    if carrier and carrier not in {"auto", "none"}:
        return True
    model = routing_request_basis.get("requested_model")
    if model is not None and str(model).strip():
        return True
    return False


def extract_handoff_source_ref(
    *,
    intent: Mapping[str, Any] | None,
    objective: str | None = None,
) -> str | None:
    explicit = str((intent or {}).get("handoff_source_ref") or "").strip()
    if explicit:
        return explicit
    text = str(objective or (intent or {}).get("objective") or "")
    match = re.search(r"prompt_spawn_[0-9TZ+\-]+(?:domain_worker_[a-z0-9]+)?", text)
    if match:
        return match.group(0)
    return None


def _objective_indicates_ion_handoff(objective: str) -> bool:
    lowered = objective.lower()
    return any(marker in lowered for marker in _HANDOFF_OBJECTIVE_MARKERS)


def derive_directive_provenance_class(
    *,
    source_kind: str | None = None,
    intent: Mapping[str, Any] | None = None,
    objective: str | None = None,
    directive_transport_receipt: Mapping[str, Any] | None = None,
    routing_request_basis: Mapping[str, Any] | None = None,
    operator_routing_override_attested: bool | None = None,
    inspection_mandate_default: bool | None = None,
    spawn_plan_row: bool | None = None,
) -> str:
    """Derive admission-side directive_provenance_class from spawn evidence."""

    row = intent if isinstance(intent, Mapping) else {}
    if operator_direct_enabled() or bool(row.get("operator_approved")):
        return "operator_direct"

    normalized_source_kind = str(source_kind or row.get("source_kind") or "").strip()
    normalized_objective = str(objective or row.get("objective") or "")
    handoff_source_ref = extract_handoff_source_ref(
        intent=row,
        objective=normalized_objective,
    )
    override_attested = (
        bool(operator_routing_override_attested)
        if operator_routing_override_attested is not None
        else bool(row.get("operator_routing_override_attested"))
    )
    mandate_default = (
        bool(inspection_mandate_default)
        if inspection_mandate_default is not None
        else bool(row.get("inspection_mandate_default"))
    )
    plan_row = (
        bool(spawn_plan_row)
        if spawn_plan_row is not None
        else bool(row.get("spawn_plan_row"))
    )

    if plan_row or normalized_source_kind in SPAWN_PLAN_SOURCE_KINDS:
        return "spawn_plan_row"

    if mandate_default or str(row.get("directive_origin") or "") == "inspection_mandate":
        return "inspection_mandate_default"

    bundle = row.get("bundle")
    if (
        isinstance(bundle, Mapping)
        and str(bundle.get("default_directive") or "").strip() == normalized_objective.strip()
        and directive_transport_receipt is None
        and normalized_source_kind == "explicit_domain"
    ):
        return "inspection_mandate_default"

    if normalized_source_kind == "explicit_domain" and (
        handoff_source_ref or _objective_indicates_ion_handoff(normalized_objective)
    ):
        return "ion_handoff_relay"

    if isinstance(directive_transport_receipt, Mapping):
        if is_parent_fixed_routing(routing_request_basis) and not override_attested:
            return "parent_prose_orchestration"
        return "operator_transport"

    if is_parent_fixed_routing(routing_request_basis):
        return "parent_prose_orchestration"

    return "parent_prose_orchestration"


def validate_directive_provenance_on_admission(
    *,
    directive_provenance_class: str,
    objective: str,
    directive_transport_receipt: Mapping[str, Any] | None,
    routing_request_basis: Mapping[str, Any] | None,
    operator_routing_override_attested: bool = False,
    work_class: str | None = None,
    source_kind: str | None = None,
) -> list[str]:
    """Fail-closed provenance checks at spawn admission emit/bind time."""

    blockers: list[str] = []
    provenance_class = str(directive_provenance_class or "").strip()
    if provenance_class not in DIRECTIVE_PROVENANCE_CLASSES:
        blockers.append("spawn_admission_directive_provenance_class_invalid")

    # Operator-directed runs are lawful: the operator may name a domain and
    # author the directive.  Everything below this point exists to stop a
    # *parent agent* from doing so on its own initiative.
    if provenance_class == "operator_direct":
        return blockers

    if provenance_class == "parent_prose_orchestration":
        blockers.append("spawn_admission_directive_provenance_parent_prose_orchestration")

    # Sovereign / Domain Weaver law: Cursor parent must never select domains.
    # Only ION-generated spawn_plan_row (or inspection mandate) may bind domain_id.
    normalized_source_kind = str(source_kind or "").strip()
    if normalized_source_kind == "explicit_domain" and provenance_class not in {
        "spawn_plan_row",
        "inspection_mandate_default",
    }:
        blockers.append("spawn_admission_parent_domain_selection_forbidden")

    if provenance_class not in TRANSPORT_EXEMPT_PROVENANCE_CLASSES:
        if directive_transport_receipt is None:
            blockers.append("spawn_admission_directive_provenance_transport_required")
        else:
            blockers.extend(
                validate_directive_transport_binding(
                    objective=objective,
                    directive_transport_receipt=directive_transport_receipt,
                    work_class=work_class,
                )
            )

    if provenance_class not in AUTO_ROUTING_EXEMPT_PROVENANCE_CLASSES:
        if is_parent_fixed_routing(routing_request_basis) and not operator_routing_override_attested:
            blockers.append("spawn_admission_directive_provenance_parent_fixed_routing")

    return list(dict.fromkeys(blockers))


# PCKT-SPAWN-ADMISSION-AUTHORITY-LEXICON-V0_1 — candidate authority membrane fields.
CANDIDATE_INTERNAL_EXECUTION_SCOPE = (
    "diagnostic_validation",
    "dedup_receipt_emission",
    "audit_observation",
    "carrier_recovery_bridge_preview_only",
    "code_implementation",
    "schema_law",
    "rank_law",
    "queue_currentness_digest_refresh",
    "lane_visible_queue_reconciliation",
    "dogfood_json_parity_refresh",
    "legacy_alias_fan_in",
)

WORK_CLASS_AUTHORITY_MAP: dict[str, str] = {
    "diagnostic_validation": "candidate_internal_only",
    "dedup_receipt_emission": "candidate_internal_receipt_write_permitted",
    "carrier_recovery_bridge": "preview_candidate_only_bridge_create_blocked",
    "code_implementation": "candidate_internal_only",
    "audit_observation": "candidate_internal_only",
    "schema_law": "candidate_internal_only",
    "rank_law": "candidate_internal_only",
    "queue_currentness_digest_refresh": "candidate_internal_only",
    "lane_visible_queue_reconciliation": "candidate_internal_only",
    "dogfood_json_parity_refresh": "candidate_internal_only",
    "legacy_alias_fan_in": "candidate_internal_receipt_write_permitted",
    "documentation": "candidate_internal_only",
    "integration": "candidate_internal_only",
    "domain_analysis": "candidate_internal_only",
}

_CANDIDATE_INTERNAL_AUTHORITY_CLASSES = frozenset(
    {
        "candidate_internal_only",
        "candidate_internal_receipt_write_permitted",
        "preview_candidate_only_bridge_create_blocked",
    }
)

ADMISSION_BASIS_FIELDS = (
    "schema_id",
    "routing_decision_id",
    "routing_decision_sha256",
    "routing_source_sha256",
    "routing_packet_sha256",
    "fallback_decision_id",
    "fallback_decision_sha256",
    "domain_id",
    "work_class",
    "carrier_id",
    "model",
    "reasoning_effort",
    "mount_id",
    "mount_active_context_age_seconds",
    "mount_context_proof",
    "carrier_readiness",
    "blockers",
    "ok",
    "carrier_invocation_admitted",
    "production_authority",
    "live_execution_authority",
    "accepted_state_claim",
    "secrets_authority",
    "candidate_internal_execution_authority",
    "candidate_internal_execution_scope",
    "bridge_create_requires_live_execution",
    "receipt_write_requires_live_execution",
    "work_class_authority_map",
    "directive_transport_receipt",
    "directive_provenance_class",
    "handoff_source_ref",
    "operator_routing_override_attested",
    "advisory_economics_governed",
    "advisory_economics_binding_sha256",
    "economics_database_path",
    # Template<->context join fields (T03 tier_1_doctrine). These are minted into the admission
    # basis by ion_prompt_spawn_executor.resolve_spawn_admission_template_fields; they MUST be
    # listed here or the recomputed admission hash diverges from the minted one and every live
    # spawn is refused with cursor_spawn_admission_hash_mismatch / _id_mismatch.
    # Emergency operator repair 2026-08-04 — ratification chain (candidate):
    # ION/05_context/current/domain_weaver/candidate_founding_domains/
    # domain.kernel_ownership_runtime_carrier_slice/receipts/
    # P02_EMERGENCY_KERNEL_EDIT_RATIFICATION_CHAIN_20260805.candidate.yaml
    # overturn_review_owner: domain.honest_agency_validation (queued idw-cc8f8512518c4256).
    # Join fields were added to the mint without being listed here, which made ION
    # globally undispatchable until this tuple was repaired.
    "template_id",
    "governing_template_id",
    "governing_template_spec_path",
    # Emergency operator repair 2026-08-05 — THIRD occurrence of this same defect class.
    # `explicit_premium_model` was added to the minted admission basis by the premium-intent
    # fix (correct in substance) but not listed here, so the mint hashed 39 fields while the
    # validator recomputed over 38. Every Cursor spawn was refused with
    # cursor_spawn_admission_hash_mismatch and ION became globally undispatchable — meaning no
    # domain could be routed the fix, including this one.
    # This is a STRUCTURAL fault: any domain lawfully adding a key to the minted admission
    # silently downs ION, and nothing warns them. The correct repair is to derive the hash from
    # the minted dict itself, or add a test that fails when mint and basis diverge.
    # Routed to domain.runtime_carrier_and_action_admission; see
    # scratchpad/hash_drift_third_time.md. overturn_review_owner: domain.honest_agency_validation.
    "explicit_premium_model",
    "operation_mode",
    "execution_tier",
)

# PCKT-RUNTIME-ADVISORY-ECONOMICS-BINDING-R3 — governed high-end advisory models (Fable only; Opus banned).
ADVISORY_ECONOMICS_GOVERNED_MODEL_IDS = frozenset({"claude-fable-5"})
EXPLICIT_ONLY_CLAUDE_MODELS = frozenset({"claude-fable-5"})
SOVEREIGN_BANNED_SPAWN_MODELS = frozenset({"claude-opus-5"})
SOVEREIGN_BANNED_SPAWN_MODEL_FINDING = "sovereign_banned_spawn_model"
ADVISORY_ECONOMICS_BINDING_SCHEMA_ID = (
    "ion.advisory_economics_binding.v0_1_candidate"
)
ADVISORY_ECONOMICS_RESERVATION_REQUEST_FIELDS = (
    "idempotency_key",
    "call_window_id",
    "slot_id",
    "lineage_id",
    "owning_domain_id",
    "budget_window_id",
    "economics_policy_id",
    "policy_sha256",
    "exact_model_id",
    "requested_usd_micros",
    "reservation_id",
    "lease_id",
    "lease_expires_at",
    "occurred_at",
    "evidence_ref",
)
ADVISORY_ECONOMICS_BINDING_IMMUTABLE_FIELDS = (
    "schema_id",
    "economics_database_path",
    "reservation_id",
    "lease_id",
    "attempt_id",
    "idempotency_key",
    "run_id",
    "requested_model_id",
    "requested_usd_micros",
    "call_window_id",
    "slot_id",
    "owning_domain_id",
    "lineage_id",
    "budget_window_id",
    "economics_policy_id",
    "policy_sha256",
    "lease_expires_at",
    "reserve_receipt_sha256",
    "reserve_status",
    "concurrency_scope",
    "budget_cap_mode",
    "pre_spend_hard_cap_enforced",
    "internal_reservation_is_provider_cap",
    "provider_charge_upper_bound_proven",
    "binding_sha256",
)


def resolve_spawn_admission_authority_lexicon(work_class: str) -> dict[str, Any]:
    """Derive authority-lexicon fields for spawn_admission.json emission."""

    normalized = str(work_class or "").strip()
    authority_class = WORK_CLASS_AUTHORITY_MAP.get(normalized)
    candidate_internal = normalized in CANDIDATE_INTERNAL_EXECUTION_SCOPE or (
        authority_class in _CANDIDATE_INTERNAL_AUTHORITY_CLASSES
    )
    return {
        "candidate_internal_execution_authority": candidate_internal,
        "candidate_internal_execution_scope": list(CANDIDATE_INTERNAL_EXECUTION_SCOPE),
        "bridge_create_requires_live_execution": True,
        "receipt_write_requires_live_execution": False,
        "work_class_authority_map": dict(WORK_CLASS_AUTHORITY_MAP),
    }


# Audit observation template id — explicit mode only, never a silent default.
# Provenance: Sovereign scoped a temporary read-only audit/consolidation gate (months ago,
# several audits since complete). An earlier kernel default mapped unmapped work_class to this
# template, which produced read-only runs with no deliverables. Read-only audit remains
# available when work_class or intent_template_id explicitly selects it.
DEFAULT_PROMPT_SPAWN_TEMPLATE_ID = "ion.template.audit_observation.v1"

PROMPT_SPAWN_WORK_CLASS_TO_TEMPLATE_ID: dict[str, str] = {
    "code_implementation": "ion.template.patch_proposal.v1",
    "diagnostic_validation": "ion.template.audit_observation.v1",
    "audit_observation": "ion.template.audit_observation.v1",
    "dedup_receipt_emission": "ion.template.single_carrier_sequence_receipt.v1",
    "carrier_recovery_bridge": "ion.template.audit_observation.v1",
    "schema_law": "ion.template.patch_proposal.v1",
    "rank_law": "ion.template.patch_proposal.v1",
    "queue_currentness_digest_refresh": "ion.template.patch_proposal.v1",
    "lane_visible_queue_reconciliation": "ion.template.patch_proposal.v1",
    "dogfood_json_parity_refresh": "ion.template.context_system.maintenance.v1",
    "legacy_alias_fan_in": "ion.template.single_carrier_sequence_receipt.v1",
    "documentation": "ion.template.patch_proposal.v1",
    "integration": "ion.template.patch_proposal.v1",
    "domain_analysis": "ion.template.audit_observation.v1",
}

READ_ONLY_PROMPT_SPAWN_TEMPLATE_IDS = frozenset({DEFAULT_PROMPT_SPAWN_TEMPLATE_ID})

_VALID_PROMPT_SPAWN_WORK_CLASSES = tuple(sorted(PROMPT_SPAWN_WORK_CLASS_TO_TEMPLATE_ID))


def list_prompt_spawn_work_class_catalog() -> list[dict[str, str | bool]]:
    """Emit every mapped work_class with template_id and read_only from kernel constants."""

    rows: list[dict[str, str | bool]] = []
    for work_class in sorted(PROMPT_SPAWN_WORK_CLASS_TO_TEMPLATE_ID):
        template_id = PROMPT_SPAWN_WORK_CLASS_TO_TEMPLATE_ID[work_class]
        read_only = resolve_prompt_spawn_read_only_posture(work_class=work_class)
        rows.append(
            {
                "work_class": work_class,
                "template_id": template_id,
                "read_only": read_only,
            }
        )
    return rows


class PromptSpawnWorkClassResolutionError(ValueError):
    """Fail-closed refusal when work_class cannot be mapped to a spawn template."""

    def __init__(
        self,
        *,
        finding_id: str,
        work_class: str | None,
        valid_work_classes: tuple[str, ...] = _VALID_PROMPT_SPAWN_WORK_CLASSES,
    ) -> None:
        self.finding_id = finding_id
        self.work_class = work_class
        self.valid_work_classes = valid_work_classes
        label = repr(work_class) if work_class is not None else "absent"
        super().__init__(
            f"{finding_id}: work_class={label}; "
            f"valid_work_classes={list(valid_work_classes)}"
        )


READ_ONLY_MISSION_MARKERS = (
    "read-only",
    "read only",
    "do not edit",
    "no edits",
    "report only",
    "stdout only",
)

_READ_ONLY_DO_NOT_WRITE = re.compile(r"\bdo not write\b", re.IGNORECASE)


DEFAULT_GOVERNING_TEMPLATE_SPEC_PATH = (
    "ION/06_intelligence/specs/T03_ContextPackageSchema.spec.md"
)
FOUNDING_DOMAIN_CONTEXT_REQUIREMENTS_REL = Path(
    "ION/05_context/current/domain_weaver/candidate_founding_domains"
)


def _parse_governing_join_from_context_requirements(
    ctx_path: Path,
) -> tuple[str | None, str | None]:
    if not ctx_path.is_file():
        return None, None
    governing_id: str | None = None
    spec_path: str | None = None
    for line in ctx_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("governing_template_id:"):
            governing_id = line.split(":", 1)[1].strip() or None
        elif line.startswith("governing_template_spec_path:"):
            spec_path = line.split(":", 1)[1].strip() or None
    return governing_id, spec_path


def resolve_spawn_admission_template_fields(
    *,
    ion_root: Path | None,
    domain_id: str | None,
    work_class: str,
    intent_template_id: str | None = None,
) -> dict[str, str]:
    """Emit template_id + governing join fields for spawn_admission.json (T03 tier_1_doctrine)."""

    template_id = resolve_prompt_spawn_template_id(
        work_class,
        intent_template_id=intent_template_id,
    )
    governing_template_id = template_id
    governing_template_spec_path = DEFAULT_GOVERNING_TEMPLATE_SPEC_PATH
    normalized_domain = str(domain_id or "").strip()
    if ion_root is not None and normalized_domain:
        ctx_path = (
            ion_root
            / FOUNDING_DOMAIN_CONTEXT_REQUIREMENTS_REL
            / normalized_domain
            / "CONTEXT_REQUIREMENTS.candidate.yaml"
        )
        ctx_governing, ctx_spec = _parse_governing_join_from_context_requirements(ctx_path)
        if ctx_governing:
            governing_template_id = ctx_governing
        if ctx_spec:
            governing_template_spec_path = ctx_spec
    return {
        "template_id": template_id,
        "governing_template_id": governing_template_id,
        "governing_template_spec_path": governing_template_spec_path,
    }


def resolve_prompt_spawn_template_id(
    work_class: str | None = None,
    *,
    intent_template_id: str | None = None,
) -> str:
    """Resolve materialized template_id from explicit intent or work_class map."""

    explicit = str(intent_template_id or "").strip()
    if explicit:
        return explicit
    normalized = str(work_class or "").strip()
    if not normalized:
        raise PromptSpawnWorkClassResolutionError(
            finding_id="spawn_admission_work_class_absent_for_template_resolution",
            work_class=None,
        )
    mapped = PROMPT_SPAWN_WORK_CLASS_TO_TEMPLATE_ID.get(normalized)
    if mapped:
        return mapped
    raise PromptSpawnWorkClassResolutionError(
        finding_id="spawn_admission_work_class_unmapped",
        work_class=normalized,
    )


def resolve_prompt_spawn_read_only_posture(
    work_class: str | None = None,
    *,
    intent_template_id: str | None = None,
    mission_text: str | None = None,
    codex_sandbox_mode: str | None = None,
    workload_posture: str | None = None,
) -> bool:
    """Derive read-only deliverable posture from template/work_class, not naive substrings."""

    if str(codex_sandbox_mode or "").strip().lower() == "read-only":
        return True
    if str(workload_posture or "").strip().lower() == "read_only":
        return True

    explicit_template = str(intent_template_id or "").strip()
    normalized_work_class = str(work_class or "").strip()
    template_id = resolve_prompt_spawn_template_id(
        normalized_work_class or None,
        intent_template_id=explicit_template or None,
    )

    if explicit_template or normalized_work_class in PROMPT_SPAWN_WORK_CLASS_TO_TEMPLATE_ID:
        return template_id in READ_ONLY_PROMPT_SPAWN_TEMPLATE_IDS

    mission_lower = str(mission_text or "").lower()
    if any(marker in mission_lower for marker in READ_ONLY_MISSION_MARKERS):
        return True
    if _READ_ONLY_DO_NOT_WRITE.search(str(mission_text or "")):
        return True
    return template_id in READ_ONLY_PROMPT_SPAWN_TEMPLATE_IDS


AUTHORITY_FIELDS = (
    "production_authority",
    "live_execution_authority",
    "accepted_state_claim",
)


def _canonical_sha256(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


ADMISSION_NON_BASIS_KEYS = frozenset(
    {
        "admission_sha256",
        "admission_id",
        "admission_path",
        "authorization_basis",
    }
)


def admission_basis_extra_keys(admission: Mapping[str, Any]) -> list[str]:
    """Admission JSON keys outside the hashed basis tuple (excluding metadata)."""
    return sorted(
        key
        for key in admission
        if key not in ADMISSION_BASIS_FIELDS and key not in ADMISSION_NON_BASIS_KEYS
    )


def admission_basis_missing_keys(admission: Mapping[str, Any]) -> list[str]:
    """Basis tuple fields absent from the minted admission dict (validator vs mint drift)."""
    return sorted(
        field for field in ADMISSION_BASIS_FIELDS if field not in admission
    )


def project_admission_basis(admission: Mapping[str, Any]) -> dict[str, Any]:
    """Project any admission-shaped mapping onto the hashed basis tuple."""
    return {field: admission.get(field) for field in ADMISSION_BASIS_FIELDS}


def recompute_admission_sha256(admission: Mapping[str, Any]) -> str:
    return _canonical_sha256(project_admission_basis(admission))


def admission_sha256_matches(admission: Mapping[str, Any]) -> bool:
    stored = str(admission.get("admission_sha256") or "").strip()
    if not stored:
        return False
    return stored == recompute_admission_sha256(admission)


def _is_sha256(value: Any) -> bool:
    text = str(value or "").strip().lower()
    return len(text) == 64 and all(character in "0123456789abcdef" for character in text)


def carrier_scoped_readiness_blockers(
    blocked_by: list[Any] | None,
    carrier_id: str,
) -> list[str]:
    """Return readiness blockers that apply to the admitted carrier only.

    Executor status aggregates every carrier lane; admission and binding checks
    must not let Codex/Claude advisory items gate a Cursor spawn (and vice versa).
    """

    items = [str(item).strip() for item in (blocked_by or []) if str(item).strip()]
    carrier = str(carrier_id or "").strip()
    if carrier == "cursor_cli":
        return [
            item
            for item in items
            if item.startswith("cursor_")
            or item == "cursor_auth_unverified"
            or item.startswith("spawn_stop:")
        ]
    if carrier == "claude_cli":
        return [
            item
            for item in items
            if item.startswith("claude:") or item.startswith("spawn_stop:")
        ]
    if carrier == "codex_cli":
        return [
            item
            for item in items
            if item.startswith("codex:") or item.startswith("spawn_stop:")
        ]
    return items


def advisory_economics_binding_context(
    row: Mapping[str, Any],
    admission: Mapping[str, Any],
    intent: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], str | None]:
    """Merge spawn row / admission / caller intent for spawn_requires_advisory_economics_binding."""

    intent_row: dict[str, Any] = {}
    if isinstance(row.get("intent"), Mapping):
        intent_row.update(dict(row["intent"]))
    if isinstance(intent, Mapping):
        for key, value in intent.items():
            if value is not None:
                intent_row.setdefault(key, value)
    for source in (admission, row):
        if not isinstance(source, Mapping):
            continue
        for key in (
            "explicit_premium_model",
            "work_class",
            "carrier_economics_mode",
            "economics_mode",
            "economics_database_path",
        ):
            if source.get(key) is not None and key not in intent_row:
                intent_row[key] = source.get(key)
    economics_mode = (
        row.get("carrier_economics_mode")
        or row.get("economics_mode")
        or admission.get("carrier_economics_mode")
        or admission.get("economics_mode")
    )
    mode = str(economics_mode or "").strip().lower() or None
    return intent_row, mode


def validate_prompt_spawn_binding(
    spawn_row: Mapping[str, Any] | None,
    *,
    carrier_id: str,
    model: str,
    reasoning_effort: str | None,
    blocker_prefix: str,
    ready_verdicts: tuple[str, ...],
    domain_id: str | None = None,
    mount_id: str | None = None,
    expected_mount_context_proof: Mapping[str, Any] | None = None,
    require_mount: bool = False,
    shell_root: str | Path | None = None,
    intent: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a modern prompt-spawn row and its complete proof chain."""

    prefix = str(blocker_prefix).strip() or carrier_id
    blockers: list[str] = []
    model_normalized = str(model or "").strip()
    if model_normalized in SOVEREIGN_BANNED_SPAWN_MODELS:
        blockers.append(f"{SOVEREIGN_BANNED_SPAWN_MODEL_FINDING}:{model_normalized}")
    row: Mapping[str, Any] = spawn_row if isinstance(spawn_row, Mapping) else {}
    if not isinstance(spawn_row, Mapping):
        blockers.append(f"{prefix}_spawn_admission_required")

    raw_admission = row.get("spawn_admission")
    admission: Mapping[str, Any] = (
        raw_admission if isinstance(raw_admission, Mapping) else {}
    )
    if not isinstance(raw_admission, Mapping):
        blockers.append(f"{prefix}_spawn_admission_required")
    raw_proof = row.get("routing_decision")
    routing_proof: Mapping[str, Any] = raw_proof if isinstance(raw_proof, Mapping) else {}

    if admission.get("schema_id") != "ion.prompt_spawn_admission.v1":
        blockers.append(f"{prefix}_spawn_admission_schema_mismatch")
    if admission.get("ok") is not True or admission.get("carrier_invocation_admitted") is not True:
        blockers.append(f"{prefix}_spawn_admission_not_admitted")
    declared_blockers = admission.get("blockers")
    if not isinstance(declared_blockers, list):
        blockers.append(f"{prefix}_spawn_admission_blockers_invalid")
    elif declared_blockers:
        blockers.append(f"{prefix}_spawn_admission_declares_blockers")

    for field in (
        "routing_decision_sha256",
        "routing_source_sha256",
        "routing_packet_sha256",
        "admission_sha256",
    ):
        if not _is_sha256(admission.get(field)):
            blockers.append(f"{prefix}_spawn_admission_{field}_invalid")
    if not str(admission.get("routing_decision_id") or "").startswith("route_"):
        blockers.append(f"{prefix}_spawn_admission_routing_decision_id_invalid")
    if not str(admission.get("domain_id") or "").strip():
        blockers.append(f"{prefix}_spawn_admission_domain_required")
    if not str(admission.get("work_class") or "").strip():
        blockers.append(f"{prefix}_spawn_admission_work_class_required")

    fallback_id = admission.get("fallback_decision_id")
    fallback_sha = admission.get("fallback_decision_sha256")
    if bool(fallback_id) != bool(fallback_sha):
        blockers.append(f"{prefix}_spawn_admission_fallback_proof_incomplete")
    if fallback_id and not str(fallback_id).startswith("fallback_"):
        blockers.append(f"{prefix}_spawn_admission_fallback_decision_id_invalid")
    if fallback_sha and not _is_sha256(fallback_sha):
        blockers.append(f"{prefix}_spawn_admission_fallback_decision_sha256_invalid")

    readiness = admission.get("carrier_readiness")
    if not isinstance(readiness, Mapping):
        row_readiness = row.get("carrier_readiness")
        if isinstance(row_readiness, Mapping):
            readiness = row_readiness
    if not isinstance(readiness, Mapping):
        blockers.append(f"{prefix}_spawn_admission_readiness_required")
    else:
        scoped_blocked = carrier_scoped_readiness_blockers(
            list(readiness.get("blocked_by") or []),
            str(admission.get("carrier_id") or carrier_id),
        )
        if (
            readiness.get("verdict") not in ready_verdicts
            or bool(readiness.get("finding"))
            or scoped_blocked
        ):
            blockers.append(f"{prefix}_spawn_admission_readiness_not_ready")

    for field in (*AUTHORITY_FIELDS, "secrets_authority"):
        if admission.get(field) is not False:
            blockers.append(f"{prefix}_spawn_admission_{field}_must_be_false")

    expected_domain = str(domain_id or admission.get("domain_id") or "").strip()
    expected_effort = reasoning_effort if reasoning_effort is not None else None
    admission_bindings = {
        "domain_id": expected_domain,
        "carrier_id": carrier_id,
        "model": model,
        "reasoning_effort": expected_effort,
    }
    for field, expected in admission_bindings.items():
        if admission.get(field) != expected:
            blockers.append(f"{prefix}_spawn_admission_{field}_mismatch")

    raw_objective = str(row.get("objective") or admission.get("objective") or "")
    transport_receipt = admission.get("directive_transport_receipt")
    declared_provenance = str(admission.get("directive_provenance_class") or "").strip()
    if transport_receipt is not None:
        if raw_objective:
            blockers.extend(
                validate_directive_transport_binding(
                    objective=raw_objective,
                    directive_transport_receipt=transport_receipt,
                    work_class=str(admission.get("work_class") or ""),
                )
            )
        else:
            blockers.append(f"{prefix}_spawn_admission_directive_transport_without_objective")
    else:
        objective = raw_objective.strip()
        if objective:
            blockers.extend(
                validate_directive_transport_binding(
                    objective=objective,
                    directive_transport_receipt=None,
                    work_class=str(admission.get("work_class") or ""),
                    require_receipt_for_mutating=(
                        declared_provenance not in TRANSPORT_EXEMPT_PROVENANCE_CLASSES
                    ),
                )
            )

    routing_request_basis = None
    if isinstance(raw_proof, Mapping):
        routing_request_basis = raw_proof.get("routing_request_basis")
    if declared_provenance:
        blockers.extend(
            validate_directive_provenance_on_admission(
                directive_provenance_class=declared_provenance,
                objective=raw_objective,
                directive_transport_receipt=(
                    transport_receipt if isinstance(transport_receipt, Mapping) else None
                ),
                routing_request_basis=(
                    routing_request_basis
                    if isinstance(routing_request_basis, Mapping)
                    else None
                ),
                operator_routing_override_attested=bool(
                    admission.get("operator_routing_override_attested")
                ),
                work_class=str(admission.get("work_class") or ""),
                source_kind=str(admission.get("source_kind") or "") or None,
            )
        )
    else:
        blockers.append(f"{prefix}_spawn_admission_directive_provenance_class_required")

    admitted_mount_id = str(admission.get("mount_id") or "").strip()
    if require_mount and not admitted_mount_id:
        blockers.append(f"{prefix}_spawn_admission_mount_id_required")
    if mount_id is not None and admitted_mount_id != str(mount_id).strip():
        blockers.append(f"{prefix}_spawn_admission_mount_mismatch")

    raw_mount_context_proof = admission.get("mount_context_proof")
    if require_mount and not isinstance(raw_mount_context_proof, Mapping):
        blockers.append(f"{prefix}_spawn_admission_mount_context_proof_required")
    if isinstance(raw_mount_context_proof, Mapping):
        mount_context_proof = dict(raw_mount_context_proof)
        declared_mount_context_sha256 = mount_context_proof.pop(
            "proof_sha256", None
        )
        observed_mount_context_sha256 = _canonical_sha256(mount_context_proof)
        if declared_mount_context_sha256 != observed_mount_context_sha256:
            blockers.append(
                f"{prefix}_spawn_admission_mount_context_proof_hash_mismatch"
            )
        if raw_mount_context_proof.get("schema_id") != "ion.codex_mount_context_proof.v1":
            blockers.append(
                f"{prefix}_spawn_admission_mount_context_proof_schema_mismatch"
            )
        if str(raw_mount_context_proof.get("mount_id") or "") != admitted_mount_id:
            blockers.append(
                f"{prefix}_spawn_admission_mount_context_proof_mount_mismatch"
            )
        if str(raw_mount_context_proof.get("domain_id") or "") != expected_domain:
            blockers.append(
                f"{prefix}_spawn_admission_mount_context_proof_domain_mismatch"
            )
        files = raw_mount_context_proof.get("files")
        if not isinstance(files, list) or len(files) != 4 or any(
            not isinstance(item, Mapping)
            or not str(item.get("path") or "").strip()
            or not _is_sha256(item.get("sha256"))
            or not isinstance(item.get("bytes"), int)
            or int(item.get("bytes")) < 0
            for item in (files or [])
        ):
            blockers.append(
                f"{prefix}_spawn_admission_mount_context_files_invalid"
            )
        for field in (*AUTHORITY_FIELDS, "secrets_authority"):
            if raw_mount_context_proof.get(field) is not False:
                blockers.append(
                    f"{prefix}_spawn_admission_mount_context_proof_{field}_must_be_false"
                )
        if (
            expected_mount_context_proof is not None
            and dict(raw_mount_context_proof) != dict(expected_mount_context_proof)
        ):
            blockers.append(
                f"{prefix}_spawn_admission_mount_context_proof_mismatch"
            )

    row_bindings = {
        "carrier_id": "carrier_id",
        "selected_model": "model",
        "selected_reasoning_effort": "reasoning_effort",
        "work_class": "work_class",
        "routing_decision_id": "routing_decision_id",
        "routing_decision_sha256": "routing_decision_sha256",
        "routing_source_sha256": "routing_source_sha256",
        "routing_packet_sha256": "routing_packet_sha256",
        "spawn_admission_id": "admission_id",
        "spawn_admission_sha256": "admission_sha256",
    }
    for row_field, admission_field in row_bindings.items():
        if row.get(row_field) != admission.get(admission_field):
            blockers.append(f"{prefix}_spawn_row_{row_field}_mismatch")
    for field in AUTHORITY_FIELDS:
        if row.get(field) is not False:
            blockers.append(f"{prefix}_spawn_row_{field}_must_be_false")

    basis_extra = admission_basis_extra_keys(admission)
    if basis_extra:
        blockers.append(f"{prefix}_spawn_admission_basis_extra_keys")
    basis_missing = admission_basis_missing_keys(admission)
    if basis_missing:
        blockers.append(f"{prefix}_spawn_admission_basis_missing_keys")

    observed_admission_sha256 = recompute_admission_sha256(admission)
    if admission.get("admission_sha256") != observed_admission_sha256:
        blockers.append(f"{prefix}_spawn_admission_hash_mismatch")
    if admission.get("admission_id") != f"spawn_admission_{observed_admission_sha256[:24]}":
        blockers.append(f"{prefix}_spawn_admission_id_mismatch")

    if not isinstance(raw_proof, Mapping):
        blockers.append(f"{prefix}_spawn_row_routing_proof_required")
        observed_routing_packet_sha256 = None
    else:
        if routing_proof.get("schema_id") != "ion.prompt_spawn_routing_decision_proof.v1":
            blockers.append(f"{prefix}_spawn_row_routing_proof_schema_mismatch")
        proof_basis = dict(routing_proof)
        declared_packet_sha = proof_basis.pop("routing_packet_sha256", None)
        observed_routing_packet_sha256 = _canonical_sha256(proof_basis)
        if (
            declared_packet_sha != observed_routing_packet_sha256
            or declared_packet_sha != admission.get("routing_packet_sha256")
        ):
            blockers.append(f"{prefix}_spawn_row_routing_packet_hash_mismatch")
        proof_bindings = {
            "routing_decision_id": admission.get("routing_decision_id"),
            "routing_decision_sha256": admission.get("routing_decision_sha256"),
            "routing_source_sha256": admission.get("routing_source_sha256"),
            "domain_id": expected_domain,
            "work_class": admission.get("work_class"),
            "carrier_id": carrier_id,
            "selected_model": model,
            "selected_reasoning_effort": expected_effort,
        }
        for field, expected in proof_bindings.items():
            if routing_proof.get(field) != expected:
                blockers.append(f"{prefix}_spawn_row_routing_proof_{field}_mismatch")
        if routing_proof.get("routing_source_parity_ok") is not True:
            blockers.append(f"{prefix}_spawn_row_routing_source_parity_required")
        allowed = routing_proof.get("effective_allowed_carriers")
        if not isinstance(allowed, list) or carrier_id not in allowed:
            blockers.append(f"{prefix}_spawn_row_carrier_not_effectively_allowed")
        for field in AUTHORITY_FIELDS:
            if routing_proof.get(field) is not False:
                blockers.append(f"{prefix}_spawn_row_routing_proof_{field}_must_be_false")

    econ_intent, econ_mode = advisory_economics_binding_context(row, admission, intent)
    work_class_for_econ = str(
        admission.get("work_class") or row.get("work_class") or ""
    ).strip() or None
    requires_advisory_binding = spawn_requires_advisory_economics_binding(
        carrier_id=carrier_id,
        model=model,
        work_class=work_class_for_econ,
        intent=econ_intent,
        shell_root=shell_root,
        economics_mode=econ_mode,
    )
    binding: Mapping[str, Any] | None = None
    if requires_advisory_binding:
        raw_binding = row.get("advisory_economics_binding")
        binding = raw_binding if isinstance(raw_binding, Mapping) else None
        if binding is None:
            blockers.append(f"{prefix}_advisory_economics_binding_required")
        else:
            blockers.extend(
                validate_advisory_economics_binding_handoff(
                    binding=binding,
                    admission=admission,
                    spawn_row=row,
                    model=model,
                    blocker_prefix=prefix,
                )
            )
        declared_binding_sha = admission.get("advisory_economics_binding_sha256")
        if binding is not None:
            observed_binding_sha = advisory_economics_binding_sha256(binding)
            if declared_binding_sha != observed_binding_sha:
                blockers.append(
                    f"{prefix}_advisory_economics_binding_sha256_mismatch"
                )

    return {
        "ok": not blockers,
        "blockers": list(dict.fromkeys(blockers)),
        "admission": dict(admission),
        "routing_proof": dict(routing_proof),
        "observed_admission_sha256": observed_admission_sha256,
        "observed_routing_packet_sha256": observed_routing_packet_sha256,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }


def is_advisory_economics_governed_model(model_id: str | None) -> bool:
    return str(model_id or "").strip() in ADVISORY_ECONOMICS_GOVERNED_MODEL_IDS


def spawn_requires_advisory_economics_binding(
    *,
    carrier_id: str,
    model: str,
    work_class: str | None = None,
    intent: Mapping[str, Any] | None = None,
    shell_root: str | Path | None = None,
    economics_mode: str | None = None,
) -> bool:
    """Advisory-economics DB reserve applies only when subscription claude_cli law does not govern."""

    if not is_advisory_economics_governed_model(model):
        return False
    row = intent if isinstance(intent, Mapping) else {}
    normalized_carrier = str(carrier_id or "").strip()
    mode = str(
        economics_mode
        or row.get("carrier_economics_mode")
        or row.get("economics_mode")
        or ""
    ).strip().lower()
    if not mode and normalized_carrier == "claude_cli":
        from .ion_claude_cli_runner import default_carrier_economics_mode

        mode = default_carrier_economics_mode("claude_cli")
    if normalized_carrier == "claude_cli" and mode == "subscription":
        if bool(row.get("explicit_premium_model")):
            return False
        wc = str(work_class or row.get("work_class") or "").strip()
        if shell_root is not None and wc:
            from .ion_cli_model_selection import judgment_work_class_grants_premium_intent

            if judgment_work_class_grants_premium_intent(
                shell_root, wc, normalized_carrier, str(model or "").strip()
            ):
                return False
    return True


def advisory_economics_truth_constants() -> dict[str, bool | str]:
    from .ion_advisory_economics_store import TRUTH_CONSTANTS

    return dict(TRUTH_CONSTANTS)


def _advisory_economics_positive_micros(value: Any, field_name: str) -> list[str]:
    blockers: list[str] = []
    if not isinstance(value, int) or isinstance(value, bool):
        blockers.append(f"spawn_admission_advisory_economics_{field_name}_invalid")
    elif value <= 0:
        blockers.append(f"spawn_admission_advisory_economics_{field_name}_nonpositive")
    return blockers


def validate_advisory_economics_reservation_request(
    reservation_request: Mapping[str, Any] | None,
    *,
    model: str,
    domain_id: str | None = None,
) -> list[str]:
    """Fail-closed structural validation for an explicit reserve request payload."""

    blockers: list[str] = []
    if not isinstance(reservation_request, Mapping):
        return ["spawn_admission_advisory_economics_reservation_request_required"]
    for store_owned_field in (
        "attempt_id",
        "reserve_receipt_sha256",
        "reservation_receipt_sha256",
    ):
        if store_owned_field in reservation_request:
            blockers.append(
                "spawn_admission_advisory_economics_"
                f"caller_supplied_{store_owned_field}_forbidden"
            )
    for field in ADVISORY_ECONOMICS_RESERVATION_REQUEST_FIELDS:
        value = reservation_request.get(field)
        if value is None or str(value).strip() == "":
            blockers.append(
                f"spawn_admission_advisory_economics_reservation_{field}_required"
            )
    exact_model_id = str(reservation_request.get("exact_model_id") or "").strip()
    if exact_model_id and exact_model_id != str(model).strip():
        blockers.append(
            "spawn_admission_advisory_economics_reservation_exact_model_id_mismatch"
        )
    if domain_id and str(reservation_request.get("owning_domain_id") or "").strip() not in {
        "",
        str(domain_id).strip(),
    }:
        blockers.append(
            "spawn_admission_advisory_economics_reservation_domain_id_mismatch"
        )
    blockers.extend(
        _advisory_economics_positive_micros(
            reservation_request.get("requested_usd_micros"),
            "requested_usd_micros",
        )
    )
    return list(dict.fromkeys(blockers))


def validate_advisory_economics_admission_prerequisites(
    *,
    intent: Mapping[str, Any] | None,
    model: str,
    domain_id: str | None = None,
    shell_root: str | Path | None = None,
    carrier_id: str | None = None,
    work_class: str | None = None,
    economics_mode: str | None = None,
) -> list[str]:
    """Gate-A prerequisites before reserve; never infers or provisions a database."""

    if not spawn_requires_advisory_economics_binding(
        carrier_id=str(carrier_id or ""),
        model=model,
        work_class=work_class,
        intent=intent,
        shell_root=shell_root,
        economics_mode=economics_mode,
    ):
        return []
    blockers: list[str] = []
    row = intent if isinstance(intent, Mapping) else {}
    database_path = str(row.get("economics_database_path") or "").strip()
    if not database_path:
        blockers.append("spawn_admission_advisory_economics_database_path_required")
        return blockers
    resolved = Path(database_path)
    if shell_root is not None and not resolved.is_absolute():
        resolved = Path(shell_root).resolve() / resolved
    else:
        resolved = resolved.resolve()
    if not resolved.is_file():
        blockers.append("spawn_admission_advisory_economics_database_path_not_file")
    reservation_request = row.get("advisory_economics_reservation_request")
    if reservation_request is None:
        reservation_request = row.get("reservation_request")
    blockers.extend(
        validate_advisory_economics_reservation_request(
            reservation_request if isinstance(reservation_request, Mapping) else None,
            model=model,
            domain_id=domain_id,
        )
    )
    return list(dict.fromkeys(blockers))


R5_ADVISORY_ECONOMICS_BINDING_IMMUTABLE_FIELDS = (
    "economics_database_path",
    "reservation_id",
    "lease_id",
    "attempt_id",
    "idempotency_key",
    "run_id",
    "intent_id",
    "intent_semantic_digest",
    "requested_model_id",
    "reserved_usd_micros",
    "call_id",
    "slot_id",
    "domain_id",
    "lineage_id",
    "concurrency_binding",
    "lease_expires_at",
    "reservation_receipt_sha256",
)


def advisory_economics_binding_basis(binding: Mapping[str, Any]) -> dict[str, Any]:
    fields = dict.fromkeys(
        (
            *ADVISORY_ECONOMICS_BINDING_IMMUTABLE_FIELDS,
            *R5_ADVISORY_ECONOMICS_BINDING_IMMUTABLE_FIELDS,
        )
    )
    return {field: binding.get(field) for field in fields}


def advisory_economics_binding_sha256(binding: Mapping[str, Any]) -> str:
    payload = advisory_economics_binding_basis(binding)
    payload.pop("binding_sha256", None)
    return _canonical_sha256(payload)


def build_advisory_economics_binding(
    *,
    economics_database_path: str | Path,
    intent: Mapping[str, Any],
    reservation_request: Mapping[str, Any],
    run_id: str,
    reserve_result: Mapping[str, Any],
) -> dict[str, Any]:
    attempt_id = str(reserve_result.get("attempt_id") or "")
    reservation_receipt_sha256 = str(
        reserve_result.get("reserve_receipt_sha256") or ""
    )
    binding: dict[str, Any] = {
        "schema_id": ADVISORY_ECONOMICS_BINDING_SCHEMA_ID,
        "economics_database_path": str(Path(economics_database_path).resolve()),
        "reservation_id": str(reserve_result.get("reservation_id") or ""),
        "lease_id": str(reserve_result.get("lease_id") or ""),
        "attempt_id": attempt_id,
        "idempotency_key": str(reservation_request.get("idempotency_key") or ""),
        "run_id": str(run_id),
        "intent_id": str(intent.get("intent_id") or ""),
        "intent_semantic_digest": str(
            intent.get("intent_semantic_digest") or ""
        ),
        "requested_model_id": str(reservation_request.get("exact_model_id") or ""),
        "reserved_usd_micros": int(
            reserve_result.get("requested_usd_micros") or 0
        ),
        "call_id": str(reservation_request.get("call_window_id") or ""),
        "domain_id": str(reservation_request.get("owning_domain_id") or ""),
        "requested_usd_micros": int(reserve_result.get("requested_usd_micros") or 0),
        "call_window_id": str(reservation_request.get("call_window_id") or ""),
        "slot_id": str(reservation_request.get("slot_id") or ""),
        "owning_domain_id": str(reservation_request.get("owning_domain_id") or ""),
        "lineage_id": str(reservation_request.get("lineage_id") or ""),
        "budget_window_id": str(reservation_request.get("budget_window_id") or ""),
        "economics_policy_id": str(
            reservation_request.get("economics_policy_id") or ""
        ),
        "policy_sha256": str(reservation_request.get("policy_sha256") or ""),
        "lease_expires_at": str(reservation_request.get("lease_expires_at") or ""),
        "reserve_receipt_sha256": reservation_receipt_sha256,
        "reservation_receipt_sha256": reservation_receipt_sha256,
        "reserve_status": str(reserve_result.get("status") or ""),
        "concurrency_binding": {
            "call_id": str(reservation_request.get("call_window_id") or ""),
            "slot_id": str(reservation_request.get("slot_id") or ""),
            "lineage_id": str(reservation_request.get("lineage_id") or ""),
            "domain_id": str(
                reservation_request.get("owning_domain_id") or ""
            ),
            "budget_window_id": str(
                reservation_request.get("budget_window_id") or ""
            ),
            "lease_id": str(reserve_result.get("lease_id") or ""),
        },
        "concurrency_scope": {
            "call_window_id": str(reservation_request.get("call_window_id") or ""),
            "slot_id": str(reservation_request.get("slot_id") or ""),
            "lineage_id": str(reservation_request.get("lineage_id") or ""),
            "owning_domain_id": str(
                reservation_request.get("owning_domain_id") or ""
            ),
            "budget_window_id": str(
                reservation_request.get("budget_window_id") or ""
            ),
            "lease_id": str(reserve_result.get("lease_id") or ""),
        },
        **advisory_economics_truth_constants(),
    }
    binding["binding_sha256"] = advisory_economics_binding_sha256(binding)
    return binding


def validate_committed_advisory_economics_reservation_binding(
    *,
    binding: Mapping[str, Any],
    intent: Mapping[str, Any],
    reservation_request: Mapping[str, Any],
    reserve_result: Mapping[str, Any],
    run_id: str,
    model: str,
    domain_id: str,
) -> list[str]:
    """Require exact request/result identity before reservation-backed admission."""

    blockers: list[str] = []
    reserve_status = str(reserve_result.get("status") or "")
    if reserve_status not in {"RESERVED", "IDEMPOTENT_REPLAY"}:
        blockers.append(
            "spawn_admission_advisory_economics_reservation_not_committed"
        )

    store_attempt_id = str(reserve_result.get("attempt_id") or "")
    receipt_sha256 = str(
        reserve_result.get("reserve_receipt_sha256") or ""
    )
    if not store_attempt_id:
        blockers.append(
            "spawn_admission_advisory_economics_store_attempt_id_required"
        )
    exact_bindings = {
        "reservation_id": str(reservation_request.get("reservation_id") or ""),
        "lease_id": str(reservation_request.get("lease_id") or ""),
        "attempt_id": store_attempt_id,
        "run_id": str(run_id),
        "requested_model_id": str(model).strip(),
        "reserved_usd_micros": int(
            reservation_request.get("requested_usd_micros") or 0
        ),
        "call_id": str(reservation_request.get("call_window_id") or ""),
        "slot_id": str(reservation_request.get("slot_id") or ""),
        "domain_id": str(domain_id).strip(),
        "lineage_id": str(reservation_request.get("lineage_id") or ""),
        "lease_expires_at": str(
            reservation_request.get("lease_expires_at") or ""
        ),
        "intent_id": str(intent.get("intent_id") or ""),
        "intent_semantic_digest": str(
            intent.get("intent_semantic_digest") or ""
        ),
        "reservation_receipt_sha256": receipt_sha256,
    }
    for field, expected in exact_bindings.items():
        if binding.get(field) != expected:
            blockers.append(
                f"spawn_admission_advisory_economics_binding_{field}_mismatch"
            )

    result_bindings = {
        "reservation_id": exact_bindings["reservation_id"],
        "lease_id": exact_bindings["lease_id"],
        "attempt_id": exact_bindings["attempt_id"],
        "run_id": exact_bindings["run_id"],
        "requested_usd_micros": exact_bindings["reserved_usd_micros"],
    }
    for field, expected in result_bindings.items():
        if reserve_result.get(field) != expected:
            blockers.append(
                f"spawn_admission_advisory_economics_reserve_result_{field}_mismatch"
            )

    if not re.fullmatch(r"[0-9a-f]{64}", receipt_sha256):
        blockers.append(
            "spawn_admission_advisory_economics_reservation_receipt_invalid"
        )
    if binding.get("reservation_receipt_sha256") != receipt_sha256:
        blockers.append(
            "spawn_admission_advisory_economics_reservation_receipt_mismatch"
        )
    if binding.get("reserve_receipt_sha256") != receipt_sha256:
        blockers.append(
            "spawn_admission_advisory_economics_reserve_receipt_mismatch"
        )

    expected_concurrency_binding = {
        "call_id": exact_bindings["call_id"],
        "slot_id": exact_bindings["slot_id"],
        "lineage_id": exact_bindings["lineage_id"],
        "domain_id": exact_bindings["domain_id"],
        "budget_window_id": str(
            reservation_request.get("budget_window_id") or ""
        ),
        "lease_id": exact_bindings["lease_id"],
    }
    if binding.get("concurrency_binding") != expected_concurrency_binding:
        blockers.append(
            "spawn_admission_advisory_economics_concurrency_binding_mismatch"
        )
    if advisory_economics_binding_sha256(binding) != binding.get(
        "binding_sha256"
    ):
        blockers.append(
            "spawn_admission_advisory_economics_binding_sha256_mismatch"
        )
    return list(dict.fromkeys(blockers))


def merge_advisory_economics_binding_into_admission(
    admission: Mapping[str, Any],
    binding: Mapping[str, Any],
) -> dict[str, Any]:
    merged = dict(admission)
    merged["advisory_economics_governed"] = True
    merged["economics_database_path"] = binding.get("economics_database_path")
    merged["advisory_economics_binding_sha256"] = advisory_economics_binding_sha256(
        binding
    )
    admission_sha256 = _canonical_sha256(project_admission_basis(merged))
    merged["admission_sha256"] = admission_sha256
    merged["admission_id"] = f"spawn_admission_{admission_sha256[:24]}"
    return merged


def validate_advisory_economics_binding_handoff(
    *,
    binding: Mapping[str, Any],
    admission: Mapping[str, Any],
    spawn_row: Mapping[str, Any],
    model: str,
    blocker_prefix: str,
) -> list[str]:
    prefix = str(blocker_prefix).strip() or "carrier"
    blockers: list[str] = []
    if binding.get("schema_id") != ADVISORY_ECONOMICS_BINDING_SCHEMA_ID:
        blockers.append(f"{prefix}_advisory_economics_binding_schema_mismatch")
    if advisory_economics_binding_sha256(binding) != binding.get("binding_sha256"):
        blockers.append(f"{prefix}_advisory_economics_binding_hash_mismatch")
    if str(binding.get("requested_model_id") or "") != str(model).strip():
        blockers.append(f"{prefix}_advisory_economics_binding_model_mismatch")
    for field in R5_ADVISORY_ECONOMICS_BINDING_IMMUTABLE_FIELDS:
        value = binding.get(field)
        if value is None or value == "":
            blockers.append(
                f"{prefix}_advisory_economics_binding_{field}_required"
            )
    if binding.get("reserved_usd_micros") != binding.get(
        "requested_usd_micros"
    ):
        blockers.append(
            f"{prefix}_advisory_economics_binding_reserved_amount_mismatch"
        )
    if binding.get("call_id") != binding.get("call_window_id"):
        blockers.append(
            f"{prefix}_advisory_economics_binding_call_id_mismatch"
        )
    if binding.get("domain_id") != binding.get("owning_domain_id"):
        blockers.append(
            f"{prefix}_advisory_economics_binding_domain_id_mismatch"
        )
    if binding.get("reservation_receipt_sha256") != binding.get(
        "reserve_receipt_sha256"
    ):
        blockers.append(
            f"{prefix}_advisory_economics_binding_reservation_receipt_mismatch"
        )
    if admission.get("advisory_economics_binding_sha256") != binding.get(
        "binding_sha256"
    ):
        blockers.append(
            f"{prefix}_advisory_economics_admission_binding_sha256_mismatch"
        )
    if admission.get("economics_database_path") != binding.get("economics_database_path"):
        blockers.append(
            f"{prefix}_advisory_economics_admission_database_path_mismatch"
        )
    row_binding = spawn_row.get("advisory_economics_binding")
    if row_binding != dict(binding):
        blockers.append(f"{prefix}_advisory_economics_spawn_row_binding_mismatch")
    for truth_field, expected in advisory_economics_truth_constants().items():
        if binding.get(truth_field) != expected:
            blockers.append(
                f"{prefix}_advisory_economics_binding_{truth_field}_truth_mismatch"
            )
    return list(dict.fromkeys(blockers))


def attempt_advisory_economics_reservation(
    *,
    shell_root: str | Path,
    intent: Mapping[str, Any],
    model: str,
    run_id: str,
    domain_id: str | None = None,
) -> dict[str, Any]:
    """Open an existing economics DB and reserve atomically; never creates a DB."""

    from .ion_advisory_economics_store import (
        EconomicsStoreError,
        ReserveRequest,
        open_existing_economics_store,
        reserve_advisory_call,
    )

    blockers = validate_advisory_economics_admission_prerequisites(
        intent=intent,
        model=model,
        domain_id=domain_id,
        shell_root=shell_root,
    )
    if blockers:
        return {
            "ok": False,
            "blockers": blockers,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    intent_id = str(intent.get("intent_id") or "").strip()
    intent_semantic_digest = str(
        intent.get("intent_semantic_digest") or ""
    ).strip()
    admitted_domain_id = str(domain_id or "").strip()
    identity_blockers: list[str] = []
    if not intent_id:
        identity_blockers.append(
            "spawn_admission_advisory_economics_intent_id_required"
        )
    if not re.fullmatch(r"[0-9a-f]{64}", intent_semantic_digest):
        identity_blockers.append(
            "spawn_admission_advisory_economics_intent_semantic_digest_invalid"
        )
    if not admitted_domain_id:
        identity_blockers.append(
            "spawn_admission_advisory_economics_domain_id_required"
        )
    if identity_blockers:
        return {
            "ok": False,
            "blockers": identity_blockers,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            **advisory_economics_truth_constants(),
        }
    database_path = str(intent.get("economics_database_path") or "").strip()
    resolved_db = Path(database_path)
    if not resolved_db.is_absolute():
        resolved_db = Path(shell_root).resolve() / resolved_db
    reservation_request = intent.get("advisory_economics_reservation_request")
    if reservation_request is None:
        reservation_request = intent.get("reservation_request")
    request_mapping = dict(reservation_request if isinstance(reservation_request, Mapping) else {})
    request_mapping["run_id"] = str(run_id)
    request_mapping["exact_model_id"] = str(model).strip()
    connection = None
    try:
        reserve_request = ReserveRequest(**request_mapping)
        connection = open_existing_economics_store(resolved_db)
        reserve_result = reserve_advisory_call(connection, reserve_request)
    except EconomicsStoreError as exc:
        return {
            "ok": False,
            "blockers": [
                f"spawn_admission_advisory_economics_reserve_refused:{type(exc).__name__}"
            ],
            "error": exc.to_dict(),
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    except (TypeError, ValueError) as exc:
        return {
            "ok": False,
            "blockers": [
                f"spawn_admission_advisory_economics_reserve_request_invalid:{type(exc).__name__}"
            ],
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    except Exception as exc:
        return {
            "ok": False,
            "blockers": [
                f"spawn_admission_advisory_economics_store_boundary_refused:{type(exc).__name__}"
            ],
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            **advisory_economics_truth_constants(),
        }
    finally:
        if connection is not None:
            connection.close()
    reserve_result_dict = reserve_result.to_dict()
    binding = build_advisory_economics_binding(
        economics_database_path=resolved_db,
        intent=intent,
        reservation_request=request_mapping,
        run_id=str(run_id),
        reserve_result=reserve_result_dict,
    )
    binding_blockers = validate_committed_advisory_economics_reservation_binding(
        binding=binding,
        intent=intent,
        reservation_request=request_mapping,
        reserve_result=reserve_result_dict,
        run_id=str(run_id),
        model=model,
        domain_id=admitted_domain_id,
    )
    if binding_blockers:
        return {
            "ok": False,
            "blockers": binding_blockers,
            "reservation_committed": True,
            "requires_unreconciled_hold": True,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            **advisory_economics_truth_constants(),
        }
    return {
        "ok": True,
        "blockers": [],
        "binding": binding,
        "reserve_result": reserve_result_dict,
        "reservation_committed": True,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
        **advisory_economics_truth_constants(),
    }


def reconcile_advisory_economics_before_provider_start(
    *,
    binding: Mapping[str, Any],
    shell_root: str | Path,
    outcome: str,
    evidence_ref: str,
    occurred_at: str,
    provider_start_uncertain: bool = False,
) -> dict[str, Any]:
    """Cancel unstarted reservations or hold orphaned leases; retain reserve/active truth."""

    from .ion_advisory_economics_store import (
        CancelUnstartedRequest,
        EconomicsStoreError,
        OrphanLeaseRequest,
        cancel_unstarted_reservation,
        hold_orphaned_lease,
    )

    database_path = Path(str(binding.get("economics_database_path") or ""))
    if not database_path.is_file():
        return {
            "ok": False,
            "action": "blocked_database_unavailable",
            "blockers": ["advisory_economics_reconcile_database_not_file"],
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            **advisory_economics_truth_constants(),
        }
    idempotency_key = f"reconcile:{outcome}:{binding.get('reservation_id')}:{occurred_at}"
    try:
        if provider_start_uncertain:
            request = OrphanLeaseRequest(
                idempotency_key=idempotency_key,
                reservation_id=str(binding.get("reservation_id") or ""),
                lease_id=str(binding.get("lease_id") or ""),
                run_id=str(binding.get("run_id") or ""),
                reason=outcome,
                occurred_at=occurred_at,
                evidence_ref=evidence_ref,
            )
            result = hold_orphaned_lease(database_path, request)
            return {
                "ok": True,
                "action": "hold_orphaned_lease",
                "result": result.to_dict(),
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_claim": False,
                **advisory_economics_truth_constants(),
            }
        proof_digest = hashlib.sha256(
            f"no_provider_process:{binding.get('run_id')}:{binding.get('reservation_id')}:{outcome}".encode(
                "utf-8"
            )
        ).hexdigest()
        request = CancelUnstartedRequest(
            idempotency_key=idempotency_key,
            reservation_id=str(binding.get("reservation_id") or ""),
            lease_id=str(binding.get("lease_id") or ""),
            run_id=str(binding.get("run_id") or ""),
            no_process_proof_digest=proof_digest,
            no_process_attested=True,
            occurred_at=occurred_at,
            evidence_ref=evidence_ref,
        )
        result = cancel_unstarted_reservation(database_path, request)
        return {
            "ok": True,
            "action": "cancel_unstarted_reservation",
            "result": result.to_dict(),
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            **advisory_economics_truth_constants(),
        }
    except EconomicsStoreError as exc:
        return {
            "ok": False,
            "action": "reconcile_failed",
            "blockers": [f"advisory_economics_reconcile_refused:{type(exc).__name__}"],
            "error": exc.to_dict(),
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            **advisory_economics_truth_constants(),
        }


def validate_prompt_spawn_route_authority(
    spawn_row: Mapping[str, Any] | None,
    *,
    source_root: str | Path,
    blocker_prefix: str,
) -> dict[str, Any]:
    """Re-run canonical selection from the proof's complete request basis.

    Hash self-consistency is insufficient because a caller can fabricate an
    internally consistent packet.  This check reloads the current canonical
    YAML/JSON route source and independently recomputes the selected carrier,
    model, effort, decision hash, and source digest.
    """

    from .ion_cli_model_selection import resolve_execution_selection
    from .ion_high_level_carrier_policy import evaluate_high_level_carrier_assignment

    prefix = str(blocker_prefix).strip() or "carrier"
    row = spawn_row if isinstance(spawn_row, Mapping) else {}
    proof = row.get("routing_decision")
    blockers: list[str] = []
    if not isinstance(proof, Mapping):
        return {
            "ok": False,
            "blockers": [f"{prefix}_spawn_route_authority_proof_required"],
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    request_basis = proof.get("routing_request_basis")
    declared_decision_basis = proof.get("routing_decision_basis")
    request_fields = {
        "domain_id",
        "work_class",
        "requested_carrier",
        "requested_model",
        "requested_posture",
        "allowed_carriers",
        "execution_surface",
    }
    if not isinstance(request_basis, Mapping) or set(request_basis) != request_fields:
        blockers.append(f"{prefix}_spawn_route_request_basis_invalid")
        request_basis = {}
    if not isinstance(declared_decision_basis, Mapping):
        blockers.append(f"{prefix}_spawn_route_decision_basis_required")
        declared_decision_basis = {}
    allowed = request_basis.get("allowed_carriers")
    if allowed is not None and (
        not isinstance(allowed, list)
        or any(not isinstance(item, str) or not item.strip() for item in allowed)
    ):
        blockers.append(f"{prefix}_spawn_route_allowed_carriers_invalid")
        allowed = []

    try:
        canonical = resolve_execution_selection(
            Path(source_root).resolve(),
            domain_id=request_basis.get("domain_id"),
            carrier=request_basis.get("requested_carrier"),
            requested_model=request_basis.get("requested_model"),
            work_class=request_basis.get("work_class"),
            posture=request_basis.get("requested_posture"),
            allowed_carriers=list(allowed) if isinstance(allowed, list) else None,
            execution_surface=request_basis.get("execution_surface"),
        )
    except (OSError, ValueError, TypeError) as exc:
        return {
            "ok": False,
            "blockers": [
                *blockers,
                f"{prefix}_spawn_route_authority_recompute_failed:{type(exc).__name__}",
            ],
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }

    if canonical.get("policy_blocked"):
        blockers.append(f"{prefix}_spawn_route_authority_policy_blocked")
    if canonical.get("routing_source_parity_ok") is not True:
        blockers.append(f"{prefix}_spawn_route_authority_source_parity_required")
    if canonical.get("routing_request_basis") != dict(request_basis):
        blockers.append(f"{prefix}_spawn_route_request_basis_mismatch")
    if canonical.get("routing_decision_basis") != dict(declared_decision_basis):
        blockers.append(f"{prefix}_spawn_route_decision_basis_mismatch")

    rank_value = row.get("rank_id") or row.get("rank")
    if isinstance(rank_value, Mapping):
        rank_value = rank_value.get("rank_id")
    high_level_carrier_policy = evaluate_high_level_carrier_assignment(
        source_root,
        role_id=str(row.get("role") or row.get("role_id") or ""),
        rank_id=str(rank_value or ""),
        carrier_id=str(canonical.get("carrier_id") or ""),
        model_id=str(canonical.get("model") or ""),
    )
    # Operator model-routing preferences are advisory metadata. They are not
    # execution authority and must never manufacture an admission blocker.

    proof_bindings = {
        "routing_decision_id": canonical.get("routing_decision_id"),
        "routing_decision_sha256": canonical.get("routing_decision_sha256"),
        "routing_source_path": canonical.get("routing_source_path"),
        "routing_source_sha256": canonical.get("routing_source_sha256"),
        "routing_source_parity_ok": canonical.get("routing_source_parity_ok"),
        "domain_id": canonical.get("domain_id"),
        "work_class": canonical.get("work_class"),
        "carrier_id": canonical.get("carrier_id"),
        "selected_model": canonical.get("model"),
        "selected_reasoning_effort": canonical.get("reasoning_effort"),
        "source_model_tier": canonical.get("source_model_tier"),
        "effective_allowed_carriers": canonical.get("effective_allowed_carriers"),
    }
    for field, expected in proof_bindings.items():
        if proof.get(field) != expected:
            blockers.append(f"{prefix}_spawn_route_authority_{field}_mismatch")
    row_bindings = {
        "carrier_id": canonical.get("carrier_id"),
        "selected_model": canonical.get("model"),
        "selected_reasoning_effort": canonical.get("reasoning_effort"),
        "routing_decision_id": canonical.get("routing_decision_id"),
        "routing_decision_sha256": canonical.get("routing_decision_sha256"),
        "routing_source_sha256": canonical.get("routing_source_sha256"),
    }
    for field, expected in row_bindings.items():
        if row.get(field) != expected:
            blockers.append(f"{prefix}_spawn_route_authority_row_{field}_mismatch")
    return {
        "ok": not blockers,
        "blockers": list(dict.fromkeys(blockers)),
        "canonical_selection": canonical,
        "high_level_carrier_policy": high_level_carrier_policy,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }
