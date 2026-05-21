"""Small vNext promotion-plan primitives.

This candidate bridges source-pool audit decisions to future curated promotion
work. It builds, validates, classifies, and hashes in-memory plan records only.
It does not copy, move, delete, scan source pools, mutate legacy roots, touch
git, or write files.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Mapping, Sequence

from .ion_source_pool_audit_core import PROMOTION_DECISIONS, RISK_FLAGS, normalize_decision


SCHEMA_ID = "ion.vnext.promotion_plan_core.v1"
ITEM_SCHEMA_ID = "ion.vnext.promotion_plan_item.v1"
READY_VERDICT = "ION_PROMOTION_PLAN_CORE_READY"
BLOCKED_VERDICT = "ION_PROMOTION_PLAN_CORE_BLOCKED"

PLAN_STATUSES = {
    "CANDIDATE",
    "READY_FOR_REVIEW",
    "BLOCKED",
    "SUPERSEDED",
    "REFERENCE_ONLY",
}

PROMOTION_ACTION_DECISIONS = {
    "PROMOTE_ACTIVE",
    "PROMOTE_WITH_RENAME",
    "MERGE_INTO_CANON",
}

NON_PROMOTING_DECISIONS = {
    "PROMOTE_AS_REFERENCE",
    "ARCHIVE_EVIDENCE",
    "REGENERATE_FROM_SOURCE",
    "ROUTE_WORK_ITEM",
    "PRIVATE_EXCLUDE",
    "STALE_REMOVE_LATER",
    "BLOCKED_NEEDS_HUMAN",
}

REQUIRED_PROMOTION_VALIDATIONS = {
    "source_hash_verified",
    "target_path_authorized",
    "tests_or_validation_defined",
}

REQUIRED_PROMOTION_APPROVALS = {
    "operator_approval",
    "steward_review",
}

AUTHORITY_FLAGS = (
    "accepted_state_claim",
    "production_authority",
    "live_execution_authority",
    "secrets_authority",
)

FORBIDDEN_RELATIVE_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
}

PRIVATE_MARKERS = (
    "ION_VAULT_LOCAL",
    "99_private",
    "browser_sessions",
    "credentials",
    "private_auth",
)

ENV_MARKERS = (
    ".env",
    ".env.",
)

RUNTIME_MARKERS = (
    "ION/05_context/current/ACTIVE_",
    "ION/05_context/current/runtime/",
    "ION/05_context/runtime_state/",
    "ION_VNEXT/05_runtime/",
)

QUEUE_LEDGER_MARKERS = (
    "/queue/",
    "/queues/",
    "/ledger/",
    "/ledgers/",
    "ACTIVE_CARRIER_MESSAGE_QUEUE",
    "ACTIVE_OPERATOR_MESSAGE_QUEUE",
    "ACTIVE_CARRIER_TASK_RETURN_LEDGER",
)


@dataclass(frozen=True)
class PromotionPlanItem:
    schema_id: str
    item_id: str
    source_pool_id: str
    source_path: str
    target_path: str
    decision: str
    required_receipts: tuple[str, ...]
    validation_obligations: tuple[str, ...]
    rollback_obligations: tuple[str, ...]
    approval_gates: tuple[str, ...]
    risk_flags: tuple[str, ...] = ()
    source_hashes: Mapping[str, str] = field(default_factory=dict)
    source_pool_hash: str = ""
    notes: tuple[str, ...] = ()
    payload: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PromotionPlanRecord:
    schema_id: str
    plan_id: str
    status: str
    created_at: str
    planner: str
    source_pool_id: str
    target_family: str
    summary: str
    items: tuple[PromotionPlanItem, ...]
    required_receipts: tuple[str, ...] = ()
    authority: Mapping[str, bool] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    payload: Mapping[str, Any] = field(default_factory=dict)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_promotion_plan_item(
    *,
    item_id: str,
    source_pool_id: str,
    source_path: str,
    target_path: str = "",
    decision: str,
    required_receipts: Sequence[str],
    validation_obligations: Sequence[str],
    rollback_obligations: Sequence[str],
    approval_gates: Sequence[str],
    risk_flags: Sequence[str] | None = None,
    source_hashes: Mapping[str, str] | None = None,
    source_pool_hash: str = "",
    notes: Sequence[str] | None = None,
    payload: Mapping[str, Any] | None = None,
) -> PromotionPlanItem:
    return PromotionPlanItem(
        schema_id=ITEM_SCHEMA_ID,
        item_id=str(item_id),
        source_pool_id=str(source_pool_id),
        source_path=str(source_path),
        target_path=str(target_path),
        decision=normalize_decision(decision),
        required_receipts=tuple(str(path) for path in required_receipts),
        validation_obligations=tuple(str(value) for value in validation_obligations),
        rollback_obligations=tuple(str(value) for value in rollback_obligations),
        approval_gates=tuple(str(value) for value in approval_gates),
        risk_flags=tuple(str(flag) for flag in (risk_flags or ())),
        source_hashes={str(key): str(value) for key, value in (source_hashes or {}).items()},
        source_pool_hash=str(source_pool_hash),
        notes=tuple(str(note) for note in (notes or ())),
        payload=dict(payload or {}),
    )


def build_promotion_item_from_source_pool_classification(
    *,
    item_id: str,
    source_pool_id: str,
    source_path: str,
    target_path: str = "",
    classification: Mapping[str, Any],
    required_receipts: Sequence[str],
    validation_obligations: Sequence[str],
    rollback_obligations: Sequence[str],
    approval_gates: Sequence[str],
    source_hashes: Mapping[str, str] | None = None,
    notes: Sequence[str] | None = None,
    payload: Mapping[str, Any] | None = None,
) -> PromotionPlanItem:
    return build_promotion_plan_item(
        item_id=item_id,
        source_pool_id=source_pool_id,
        source_path=source_path,
        target_path=target_path,
        decision=str(classification.get("recommended_decision") or classification.get("declared_decision") or ""),
        required_receipts=required_receipts,
        validation_obligations=validation_obligations,
        rollback_obligations=rollback_obligations,
        approval_gates=approval_gates,
        risk_flags=tuple(str(flag) for flag in classification.get("risk_flags", []) or ()),
        source_hashes=source_hashes,
        source_pool_hash=str(classification.get("source_pool_hash") or ""),
        notes=notes,
        payload=payload,
    )


def build_promotion_plan_record(
    *,
    plan_id: str,
    planner: str,
    source_pool_id: str,
    target_family: str,
    summary: str,
    items: Sequence[PromotionPlanItem | Mapping[str, Any]],
    required_receipts: Sequence[str] | None = None,
    status: str = "CANDIDATE",
    authority: Mapping[str, bool] | None = None,
    warnings: Sequence[str] | None = None,
    payload: Mapping[str, Any] | None = None,
    created_at: str | None = None,
) -> PromotionPlanRecord:
    normalized_authority = {flag: False for flag in AUTHORITY_FLAGS}
    normalized_authority.update({str(key): bool(value) for key, value in (authority or {}).items()})
    normalized_items = tuple(
        item if isinstance(item, PromotionPlanItem) else _item_from_mapping(item)
        for item in items
    )
    return PromotionPlanRecord(
        schema_id=SCHEMA_ID,
        plan_id=str(plan_id),
        status=str(status),
        created_at=created_at or utc_now(),
        planner=str(planner),
        source_pool_id=str(source_pool_id),
        target_family=str(target_family),
        summary=str(summary),
        items=normalized_items,
        required_receipts=tuple(str(path) for path in (required_receipts or ())),
        authority=normalized_authority,
        warnings=tuple(str(warning) for warning in (warnings or ())),
        payload=dict(payload or {}),
    )


def promotion_item_to_dict(item: PromotionPlanItem | Mapping[str, Any]) -> dict[str, Any]:
    value = asdict(item) if isinstance(item, PromotionPlanItem) else dict(item)
    return _jsonable(value)


def promotion_plan_to_dict(plan: PromotionPlanRecord | Mapping[str, Any]) -> dict[str, Any]:
    value = asdict(plan) if isinstance(plan, PromotionPlanRecord) else dict(plan)
    return _jsonable(value)


def stable_promotion_plan_hash(plan: PromotionPlanRecord | Mapping[str, Any]) -> str:
    value = promotion_plan_to_dict(plan)
    value.pop("promotion_plan_hash", None)
    payload = json.dumps(_sort_jsonable(value), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def attach_promotion_plan_hash(plan: PromotionPlanRecord | Mapping[str, Any]) -> dict[str, Any]:
    value = promotion_plan_to_dict(plan)
    value["promotion_plan_hash"] = stable_promotion_plan_hash(value)
    return value


def validate_promotion_plan_item(item: PromotionPlanItem | Mapping[str, Any]) -> tuple[str, ...]:
    value = promotion_item_to_dict(item)
    errors: list[str] = []

    if value.get("schema_id") != ITEM_SCHEMA_ID:
        errors.append("item_schema_id_invalid")
    for field_name in ("item_id", "source_pool_id", "source_path"):
        if not _non_empty(value.get(field_name)):
            errors.append(f"{field_name}_required")

    decision = normalize_decision(str(value.get("decision", "")))
    if decision not in PROMOTION_DECISIONS:
        errors.append("decision_invalid")

    if not _source_path_allowed(value.get("source_path"), decision=decision):
        errors.append("source_path_invalid_or_forbidden")
    if _decision_requires_target(decision) and not _target_path_allowed(value.get("target_path")):
        errors.append("target_path_required_or_invalid")
    if not _decision_requires_target(decision) and value.get("target_path") and not _target_path_allowed(value.get("target_path"), allow_private=decision == "PRIVATE_EXCLUDE"):
        errors.append("target_path_invalid")

    risk_flags = tuple(str(flag) for flag in value.get("risk_flags", []) or ())
    unknown_flags = sorted(flag for flag in risk_flags if flag not in RISK_FLAGS)
    if unknown_flags:
        errors.append("risk_flags_unknown:" + ",".join(unknown_flags))
    if risk_flags and decision in PROMOTION_ACTION_DECISIONS:
        errors.append("direct_promotion_requires_risk_closure")
    if "private_path_present" in risk_flags and decision != "PRIVATE_EXCLUDE":
        errors.append("private_risk_requires_private_exclude")
    if "active_queue_or_ledger_present" in risk_flags:
        errors.append("active_queue_or_ledger_forbidden")
    if "runtime_current_state_present" in risk_flags and decision not in {"BLOCKED_NEEDS_HUMAN", "REGENERATE_FROM_SOURCE"}:
        errors.append("runtime_current_state_requires_block_or_regenerate")

    _validate_path_tuple(value.get("required_receipts"), "required_receipts", errors)
    for tuple_field in ("validation_obligations", "rollback_obligations", "approval_gates"):
        if not isinstance(value.get(tuple_field), list):
            errors.append(f"{tuple_field}_must_be_list")

    if decision in PROMOTION_ACTION_DECISIONS:
        _validate_direct_promotion_obligations(value, errors)
    if decision == "PRIVATE_EXCLUDE" and not risk_flags:
        errors.append("private_exclude_requires_private_risk_flag")
    if decision == "BLOCKED_NEEDS_HUMAN" and not value.get("notes"):
        errors.append("blocked_plan_item_requires_note")

    source_hashes = value.get("source_hashes")
    if not isinstance(source_hashes, dict):
        errors.append("source_hashes_must_be_mapping")
    else:
        for key, digest in source_hashes.items():
            if not _sha256(digest):
                errors.append(f"source_hash_invalid:{key}")
    if value.get("source_pool_hash") and not _sha256(value.get("source_pool_hash")):
        errors.append("source_pool_hash_invalid")
    if value.get("payload") is not None and not isinstance(value.get("payload"), dict):
        errors.append("payload_must_be_mapping")

    return tuple(errors)


def validate_promotion_plan_record(plan: PromotionPlanRecord | Mapping[str, Any]) -> tuple[str, ...]:
    value = promotion_plan_to_dict(plan)
    errors: list[str] = []

    if value.get("schema_id") != SCHEMA_ID:
        errors.append("schema_id_invalid")
    for field_name in ("plan_id", "created_at", "planner", "source_pool_id", "target_family", "summary"):
        if not _non_empty(value.get(field_name)):
            errors.append(f"{field_name}_required")
    if value.get("status") not in PLAN_STATUSES:
        errors.append("status_invalid")
    items = value.get("items")
    if not isinstance(items, list) or not items:
        errors.append("items_required")
    elif len({str(item.get("item_id")) for item in items if isinstance(item, dict)}) != len(items):
        errors.append("item_ids_must_be_unique")
    else:
        for index, item in enumerate(items):
            for item_error in validate_promotion_plan_item(item):
                errors.append(f"item[{index}].{item_error}")

    _validate_path_tuple(value.get("required_receipts"), "plan_required_receipts", errors, required=False)

    authority = value.get("authority")
    if not isinstance(authority, dict):
        errors.append("authority_required")
    else:
        for flag in AUTHORITY_FLAGS:
            if authority.get(flag) is not False:
                errors.append(f"{flag}_must_be_false")
    if value.get("payload") is not None and not isinstance(value.get("payload"), dict):
        errors.append("payload_must_be_mapping")
    if value.get("warnings") is not None and not isinstance(value.get("warnings"), list):
        errors.append("warnings_must_be_list")

    return tuple(errors)


def classify_promotion_plan_record(plan: PromotionPlanRecord | Mapping[str, Any]) -> dict[str, Any]:
    value = promotion_plan_to_dict(plan)
    errors = validate_promotion_plan_record(value)
    item_decisions = [
        normalize_decision(str(item.get("decision", "")))
        for item in value.get("items", [])
        if isinstance(item, dict)
    ]
    return {
        "schema_id": "ion.vnext.promotion_plan_core.classification.v1",
        "ok": not errors,
        "verdict": READY_VERDICT if not errors else BLOCKED_VERDICT,
        "errors": list(errors),
        "item_count": len(item_decisions),
        "decisions": item_decisions,
        "direct_file_operations_performed": False,
        "source_pool_bulk_copy_allowed": False,
        "promotion_plan_hash": stable_promotion_plan_hash(value),
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _validate_direct_promotion_obligations(value: Mapping[str, Any], errors: list[str]) -> None:
    validations = set(str(item) for item in value.get("validation_obligations", []) or ())
    approvals = set(str(item) for item in value.get("approval_gates", []) or ())
    if not REQUIRED_PROMOTION_VALIDATIONS.issubset(validations):
        errors.append("direct_promotion_missing_required_validations")
    if not approvals.intersection(REQUIRED_PROMOTION_APPROVALS):
        errors.append("direct_promotion_missing_approval_gate")
    if not value.get("rollback_obligations"):
        errors.append("direct_promotion_missing_rollback_obligations")
    if not value.get("required_receipts"):
        errors.append("direct_promotion_missing_required_receipts")
    if not value.get("source_hashes"):
        errors.append("direct_promotion_missing_source_hashes")


def _validate_path_tuple(value: Any, field_name: str, errors: list[str], *, required: bool = True) -> None:
    if value is None:
        if required:
            errors.append(f"{field_name}_required")
        return
    if not isinstance(value, list):
        errors.append(f"{field_name}_must_be_list")
        return
    if required and not value:
        errors.append(f"{field_name}_required")
        return
    if any(not _generic_path_allowed(path) for path in value):
        errors.append(f"{field_name}_include_forbidden_path")


def _item_from_mapping(value: Mapping[str, Any]) -> PromotionPlanItem:
    return build_promotion_plan_item(
        item_id=str(value.get("item_id", "")),
        source_pool_id=str(value.get("source_pool_id", "")),
        source_path=str(value.get("source_path", "")),
        target_path=str(value.get("target_path", "")),
        decision=str(value.get("decision", "")),
        required_receipts=value.get("required_receipts", []) or (),
        validation_obligations=value.get("validation_obligations", []) or (),
        rollback_obligations=value.get("rollback_obligations", []) or (),
        approval_gates=value.get("approval_gates", []) or (),
        risk_flags=value.get("risk_flags", []) or (),
        source_hashes=value.get("source_hashes", {}) or {},
        source_pool_hash=str(value.get("source_pool_hash", "")),
        notes=value.get("notes", []) or (),
        payload=value.get("payload", {}) or {},
    )


def _decision_requires_target(decision: str) -> bool:
    return decision in PROMOTION_ACTION_DECISIONS or decision in {"PROMOTE_AS_REFERENCE", "ARCHIVE_EVIDENCE", "REGENERATE_FROM_SOURCE", "ROUTE_WORK_ITEM"}


def _source_path_allowed(path: Any, *, decision: str) -> bool:
    allow_private = decision == "PRIVATE_EXCLUDE"
    return _generic_path_allowed(path, allow_private=allow_private)


def _target_path_allowed(path: Any, *, allow_private: bool = False) -> bool:
    return _generic_path_allowed(path, allow_private=allow_private)


def _generic_path_allowed(path: Any, *, allow_private: bool = False) -> bool:
    if not isinstance(path, str) or not path.strip():
        return False
    raw = path.replace("\\", "/")
    if raw.startswith("/") or ".." in raw.split("/"):
        return False
    normalized = raw.lstrip("./")
    lower = normalized.lower()
    parts = [part for part in normalized.split("/") if part]
    if any(part in FORBIDDEN_RELATIVE_PARTS for part in parts):
        return False
    if any(lower == marker or lower.startswith(marker) or f"/{marker}" in lower for marker in ENV_MARKERS):
        return False
    if any(normalized.startswith(marker) or marker in normalized for marker in RUNTIME_MARKERS):
        return False
    if any(marker in f"/{normalized}/" for marker in QUEUE_LEDGER_MARKERS):
        return False
    if not allow_private and any(marker.lower() in lower for marker in PRIVATE_MARKERS):
        return False
    return True


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def _sort_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _sort_jsonable(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [_sort_jsonable(item) for item in value]
    return value


def _non_empty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value)
