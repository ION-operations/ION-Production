"""Small vNext source-pool audit primitives.

This candidate classifies declared source pools and promotion decisions in
memory only. It does not scan source roots, copy files, read private material,
touch runtime/current-state JSON, or mutate legacy roots.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Mapping, Sequence


SCHEMA_ID = "ion.vnext.source_pool_audit_core.v1"
READY_VERDICT = "ION_SOURCE_POOL_AUDIT_CORE_READY"
BLOCKED_VERDICT = "ION_SOURCE_POOL_AUDIT_CORE_BLOCKED"

ALLOWED_SOURCE_POOL_CLASSES = {
    "ACTIVE_KERNEL_SOURCE_POOL",
    "PRODUCT_SOURCE_POOL",
    "CARRIER_SOURCE_POOL",
    "WORK_INBOX_SOURCE_POOL",
    "REFERENCE_SOURCE_POOL",
    "ARCHIVE_WITNESS_POOL",
    "RELEASE_OUTPUT_POOL",
    "PRIVATE_EXCLUDED_POOL",
    "UNKNOWN_SOURCE_POOL",
}

PROMOTION_DECISIONS = {
    "PROMOTE_ACTIVE",
    "PROMOTE_WITH_RENAME",
    "MERGE_INTO_CANON",
    "PROMOTE_AS_REFERENCE",
    "ARCHIVE_EVIDENCE",
    "REGENERATE_FROM_SOURCE",
    "ROUTE_WORK_ITEM",
    "PRIVATE_EXCLUDE",
    "STALE_REMOVE_LATER",
    "BLOCKED_NEEDS_HUMAN",
}

DECISION_ALIASES = {
    "MERGE": "MERGE_INTO_CANON",
    "REGENERATE": "REGENERATE_FROM_SOURCE",
    "AUDIT_FOR_PROMOTION": "BLOCKED_NEEDS_HUMAN",
    "AUDIT_FOR_REFERENCE_PROMOTION": "PROMOTE_AS_REFERENCE",
    "REFERENCE_FIRST_PROMOTION_ONLY": "PROMOTE_AS_REFERENCE",
    "ROUTE_NOT_PROMOTE_AS_SOURCE": "ROUTE_WORK_ITEM",
    "DO_NOT_UNPACK_INTO_VNEXT": "ARCHIVE_EVIDENCE",
    "BLOCK_DIRECT_PROMOTION_CLEAN_EXPORT_REQUIRED": "BLOCKED_NEEDS_HUMAN",
}

AUTHORITY_FLAGS = (
    "accepted_state_claim",
    "production_authority",
    "live_execution_authority",
    "secrets_authority",
)

RISK_FLAGS = {
    "secret_name_present",
    "private_path_present",
    "env_path_present",
    "git_path_present",
    "cache_or_generated_path_present",
    "runtime_current_state_present",
    "active_queue_or_ledger_present",
    "nested_archive_present",
    "stale_or_conflicting_source",
    "unknown_source_family",
}

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
class SourcePoolRecord:
    schema_id: str
    source_pool_id: str
    family: str
    source_pool_class: str
    canonical_target: str
    source_paths: tuple[str, ...]
    default_decision: str
    created_at: str
    evidence_hashes: Mapping[str, str] = field(default_factory=dict)
    observed_counts: Mapping[str, int] = field(default_factory=dict)
    risk_flags: tuple[str, ...] = ()
    authority: Mapping[str, bool] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    payload: Mapping[str, Any] = field(default_factory=dict)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_decision(value: str) -> str:
    decision = str(value).strip().upper()
    return DECISION_ALIASES.get(decision, decision)


def build_source_pool_record(
    *,
    source_pool_id: str,
    family: str,
    source_pool_class: str,
    canonical_target: str,
    source_paths: Sequence[str],
    default_decision: str | None = None,
    evidence_hashes: Mapping[str, str] | None = None,
    observed_counts: Mapping[str, int] | None = None,
    risk_flags: Sequence[str] | None = None,
    authority: Mapping[str, bool] | None = None,
    warnings: Sequence[str] | None = None,
    payload: Mapping[str, Any] | None = None,
    created_at: str | None = None,
) -> SourcePoolRecord:
    normalized_authority = {flag: False for flag in AUTHORITY_FLAGS}
    normalized_authority.update({str(key): bool(value) for key, value in (authority or {}).items()})
    decision = normalize_decision(default_decision or recommended_decision_for_class(source_pool_class))
    return SourcePoolRecord(
        schema_id=SCHEMA_ID,
        source_pool_id=str(source_pool_id),
        family=str(family),
        source_pool_class=str(source_pool_class),
        canonical_target=str(canonical_target),
        source_paths=tuple(str(path) for path in source_paths),
        default_decision=decision,
        created_at=created_at or utc_now(),
        evidence_hashes={str(key): str(value) for key, value in (evidence_hashes or {}).items()},
        observed_counts={str(key): int(value) for key, value in (observed_counts or {}).items()},
        risk_flags=tuple(str(flag) for flag in (risk_flags or ())),
        authority=normalized_authority,
        warnings=tuple(str(warning) for warning in (warnings or ())),
        payload=dict(payload or {}),
    )


def recommended_decision_for_class(source_pool_class: str) -> str:
    return {
        "ACTIVE_KERNEL_SOURCE_POOL": "PROMOTE_ACTIVE",
        "PRODUCT_SOURCE_POOL": "PROMOTE_ACTIVE",
        "CARRIER_SOURCE_POOL": "PROMOTE_ACTIVE",
        "WORK_INBOX_SOURCE_POOL": "ROUTE_WORK_ITEM",
        "REFERENCE_SOURCE_POOL": "PROMOTE_AS_REFERENCE",
        "ARCHIVE_WITNESS_POOL": "ARCHIVE_EVIDENCE",
        "RELEASE_OUTPUT_POOL": "REGENERATE_FROM_SOURCE",
        "PRIVATE_EXCLUDED_POOL": "PRIVATE_EXCLUDE",
    }.get(str(source_pool_class), "BLOCKED_NEEDS_HUMAN")


def source_pool_to_dict(record: SourcePoolRecord | Mapping[str, Any]) -> dict[str, Any]:
    value = asdict(record) if isinstance(record, SourcePoolRecord) else dict(record)
    return _jsonable(value)


def stable_source_pool_hash(record: SourcePoolRecord | Mapping[str, Any]) -> str:
    value = source_pool_to_dict(record)
    value.pop("source_pool_hash", None)
    payload = json.dumps(_sort_jsonable(value), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def attach_source_pool_hash(record: SourcePoolRecord | Mapping[str, Any]) -> dict[str, Any]:
    value = source_pool_to_dict(record)
    value["source_pool_hash"] = stable_source_pool_hash(value)
    return value


def validate_source_pool_record(record: SourcePoolRecord | Mapping[str, Any]) -> tuple[str, ...]:
    value = source_pool_to_dict(record)
    errors: list[str] = []

    if value.get("schema_id") != SCHEMA_ID:
        errors.append("schema_id_invalid")
    for field_name in ("source_pool_id", "family", "canonical_target", "created_at"):
        if not _non_empty(value.get(field_name)):
            errors.append(f"{field_name}_required")
    source_pool_class = value.get("source_pool_class")
    if source_pool_class not in ALLOWED_SOURCE_POOL_CLASSES:
        errors.append("source_pool_class_invalid")

    decision = normalize_decision(str(value.get("default_decision", "")))
    if decision not in PROMOTION_DECISIONS:
        errors.append("default_decision_invalid")

    source_paths = value.get("source_paths")
    if not isinstance(source_paths, list) or not source_paths:
        errors.append("source_paths_required")
    elif any(not _path_shape_allowed(path) for path in source_paths):
        errors.append("source_paths_include_forbidden_shape")

    path_flags = _path_risk_flags(source_paths if isinstance(source_paths, list) else [])
    declared_flags = tuple(str(flag) for flag in value.get("risk_flags", []) or [])
    unknown_flags = sorted(flag for flag in declared_flags if flag not in RISK_FLAGS)
    if unknown_flags:
        errors.append("risk_flags_unknown:" + ",".join(unknown_flags))

    combined_flags = set(declared_flags) | set(path_flags)
    if combined_flags and decision in {"PROMOTE_ACTIVE", "PROMOTE_WITH_RENAME", "MERGE_INTO_CANON"}:
        errors.append("direct_promotion_requires_risk_closure")
    if "private_path_present" in combined_flags and (source_pool_class != "PRIVATE_EXCLUDED_POOL" or decision != "PRIVATE_EXCLUDE"):
        errors.append("private_path_requires_private_exclude")
    if "env_path_present" in combined_flags:
        errors.append("env_path_must_not_be_source_pool_content")
    if "runtime_current_state_present" in combined_flags and decision not in {"BLOCKED_NEEDS_HUMAN", "REGENERATE_FROM_SOURCE"}:
        errors.append("runtime_current_state_requires_block_or_regenerate")
    if "active_queue_or_ledger_present" in combined_flags:
        errors.append("active_queue_or_ledger_forbidden")

    canonical_target = value.get("canonical_target")
    private_exclude_target = source_pool_class == "PRIVATE_EXCLUDED_POOL" and decision == "PRIVATE_EXCLUDE"
    if not _target_shape_allowed(canonical_target, allow_private=private_exclude_target):
        errors.append("canonical_target_invalid")

    authority = value.get("authority")
    if not isinstance(authority, dict):
        errors.append("authority_required")
    else:
        for flag in AUTHORITY_FLAGS:
            if authority.get(flag) is not False:
                errors.append(f"{flag}_must_be_false")

    evidence_hashes = value.get("evidence_hashes")
    if not isinstance(evidence_hashes, dict):
        errors.append("evidence_hashes_must_be_mapping")
    else:
        for key, digest in evidence_hashes.items():
            if not _sha256(digest):
                errors.append(f"evidence_hash_invalid:{key}")

    observed_counts = value.get("observed_counts")
    if not isinstance(observed_counts, dict):
        errors.append("observed_counts_must_be_mapping")
    elif any(not isinstance(count, int) or count < 0 for count in observed_counts.values()):
        errors.append("observed_counts_must_be_non_negative_integers")

    if value.get("payload") is not None and not isinstance(value.get("payload"), dict):
        errors.append("payload_must_be_mapping")
    if value.get("warnings") is not None and not isinstance(value.get("warnings"), list):
        errors.append("warnings_must_be_list")

    return tuple(errors)


def classify_source_pool_record(record: SourcePoolRecord | Mapping[str, Any]) -> dict[str, Any]:
    value = source_pool_to_dict(record)
    errors = validate_source_pool_record(value)
    source_pool_class = str(value.get("source_pool_class") or "UNKNOWN_SOURCE_POOL")
    declared_decision = normalize_decision(str(value.get("default_decision", "")))
    path_flags = _path_risk_flags(value.get("source_paths", []) if isinstance(value.get("source_paths"), list) else [])
    risk_flags = sorted(set(value.get("risk_flags", []) or []) | set(path_flags))
    recommended = _safe_recommended_decision(
        source_pool_class=source_pool_class,
        declared_decision=declared_decision,
        risk_flags=risk_flags,
        errors=errors,
    )
    return {
        "schema_id": "ion.vnext.source_pool_audit_core.classification.v1",
        "ok": not errors,
        "verdict": READY_VERDICT if not errors else BLOCKED_VERDICT,
        "errors": list(errors),
        "source_pool_class": source_pool_class,
        "declared_decision": declared_decision,
        "recommended_decision": recommended,
        "risk_flags": risk_flags,
        "direct_bulk_copy_allowed": False,
        "source_pool_hash": stable_source_pool_hash(value),
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _safe_recommended_decision(
    *,
    source_pool_class: str,
    declared_decision: str,
    risk_flags: Sequence[str],
    errors: Sequence[str],
) -> str:
    if "private_path_present" in risk_flags or source_pool_class == "PRIVATE_EXCLUDED_POOL":
        return "PRIVATE_EXCLUDE"
    if "active_queue_or_ledger_present" in risk_flags or "env_path_present" in risk_flags:
        return "BLOCKED_NEEDS_HUMAN"
    if risk_flags and declared_decision in {"PROMOTE_ACTIVE", "PROMOTE_WITH_RENAME", "MERGE_INTO_CANON"}:
        return "BLOCKED_NEEDS_HUMAN"
    if errors and declared_decision not in PROMOTION_DECISIONS:
        return "BLOCKED_NEEDS_HUMAN"
    return declared_decision if declared_decision in PROMOTION_DECISIONS else recommended_decision_for_class(source_pool_class)


def _path_risk_flags(paths: Sequence[str]) -> tuple[str, ...]:
    flags: set[str] = set()
    for path in paths:
        normalized = str(path).replace("\\", "/").lstrip("./")
        lower = normalized.lower()
        parts = [part for part in normalized.split("/") if part]
        if any(part in FORBIDDEN_RELATIVE_PARTS for part in parts):
            if ".git" in parts:
                flags.add("git_path_present")
            else:
                flags.add("cache_or_generated_path_present")
        if any(marker.lower() in lower for marker in PRIVATE_MARKERS):
            flags.add("private_path_present")
        if any(lower == marker or lower.startswith(marker) or f"/{marker}" in lower for marker in ENV_MARKERS):
            flags.add("env_path_present")
        if any(normalized.startswith(marker) or marker in normalized for marker in RUNTIME_MARKERS):
            flags.add("runtime_current_state_present")
        if any(marker in f"/{normalized}/" for marker in QUEUE_LEDGER_MARKERS):
            flags.add("active_queue_or_ledger_present")
        if lower.endswith((".zip", ".tar", ".tar.gz", ".tgz", ".7z", ".rar")):
            flags.add("nested_archive_present")
    return tuple(sorted(flags))


def _path_shape_allowed(path: Any) -> bool:
    if not isinstance(path, str) or not path.strip():
        return False
    raw = path.replace("\\", "/")
    if raw.startswith("/") or ".." in raw.split("/"):
        return False
    return True


def _target_shape_allowed(path: Any, *, allow_private: bool = False) -> bool:
    if not _path_shape_allowed(path):
        return False
    normalized = str(path).replace("\\", "/").lstrip("./")
    if allow_private:
        return True
    return not any(marker.lower() in normalized.lower() for marker in PRIVATE_MARKERS)


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
