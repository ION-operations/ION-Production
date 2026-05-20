"""Small vNext context-package primitives.

This candidate is intentionally in-memory only. It describes, validates,
classifies, and hashes bounded context-package records without reading current
runtime state, writing capsules, scanning source pools, or materializing branch
context.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Mapping, Sequence


SCHEMA_ID = "ion.vnext.context_package_core.v1"
READY_VERDICT = "ION_CONTEXT_PACKAGE_CORE_READY"
BLOCKED_VERDICT = "ION_CONTEXT_PACKAGE_CORE_BLOCKED"

ALLOWED_CONTEXT_KINDS = {
    "domain_context_package",
    "branch_context_package",
    "carrier_context_package",
    "operator_context_package",
    "source_pool_context_package",
    "release_context_package",
}
ALLOWED_STATUSES = {
    "CANDIDATE",
    "READY_FOR_REVIEW",
    "LANDED_WITH_RECEIPT",
    "BLOCKED",
    "SUPERSEDED",
    "REFERENCE_ONLY",
}
AUTHORITY_FLAGS = (
    "accepted_state_claim",
    "production_authority",
    "live_execution_authority",
    "secrets_authority",
)
FORBIDDEN_PATH_FRAGMENTS = (
    ".env",
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    "ION_VAULT_LOCAL",
    "browser_profile",
    "browser-profiles",
)
FORBIDDEN_RUNTIME_PREFIXES = (
    "ION/05_context/current/ACTIVE_",
    "ION/05_context/current/runtime/",
    "ION/05_context/current/chatgpt_connector/",
    "ION/05_context/runtime_state/",
    "ION_VNEXT/05_runtime/",
)
FORBIDDEN_STATE_WORDS = ("/queues/", "/queue/", "/ledgers/", "/ledger/")


@dataclass(frozen=True)
class ContextPackageRecord:
    schema_id: str
    package_id: str
    context_kind: str
    status: str
    created_at: str
    domain: str
    summary: str
    read_order: tuple[str, ...]
    source_receipts: tuple[str, ...]
    source_hashes: Mapping[str, str] = field(default_factory=dict)
    relationship_refs: tuple[str, ...] = ()
    authority: Mapping[str, bool] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    payload: Mapping[str, Any] = field(default_factory=dict)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_context_package_record(
    *,
    package_id: str,
    context_kind: str,
    domain: str,
    summary: str,
    read_order: Sequence[str],
    source_receipts: Sequence[str],
    status: str = "CANDIDATE",
    source_hashes: Mapping[str, str] | None = None,
    relationship_refs: Sequence[str] | None = None,
    authority: Mapping[str, bool] | None = None,
    warnings: Sequence[str] | None = None,
    payload: Mapping[str, Any] | None = None,
    created_at: str | None = None,
) -> ContextPackageRecord:
    normalized_authority = {flag: False for flag in AUTHORITY_FLAGS}
    normalized_authority.update({str(key): bool(value) for key, value in (authority or {}).items()})
    return ContextPackageRecord(
        schema_id=SCHEMA_ID,
        package_id=str(package_id),
        context_kind=str(context_kind),
        status=str(status),
        created_at=created_at or utc_now(),
        domain=str(domain),
        summary=str(summary),
        read_order=tuple(str(path) for path in read_order),
        source_receipts=tuple(str(path) for path in source_receipts),
        source_hashes={str(key): str(value) for key, value in (source_hashes or {}).items()},
        relationship_refs=tuple(str(path) for path in (relationship_refs or ())),
        authority=normalized_authority,
        warnings=tuple(str(warning) for warning in (warnings or ())),
        payload=dict(payload or {}),
    )


def context_package_to_dict(record: ContextPackageRecord | Mapping[str, Any]) -> dict[str, Any]:
    value = asdict(record) if isinstance(record, ContextPackageRecord) else dict(record)
    return _jsonable(value)


def stable_context_package_hash(record: ContextPackageRecord | Mapping[str, Any]) -> str:
    value = context_package_to_dict(record)
    value.pop("context_package_hash", None)
    payload = json.dumps(_sort_jsonable(value), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def attach_context_package_hash(record: ContextPackageRecord | Mapping[str, Any]) -> dict[str, Any]:
    value = context_package_to_dict(record)
    value["context_package_hash"] = stable_context_package_hash(value)
    return value


def validate_context_package_record(record: ContextPackageRecord | Mapping[str, Any]) -> tuple[str, ...]:
    value = context_package_to_dict(record)
    errors: list[str] = []

    if value.get("schema_id") != SCHEMA_ID:
        errors.append("schema_id_invalid")
    for field_name in ("package_id", "created_at", "domain", "summary"):
        if not _non_empty(value.get(field_name)):
            errors.append(f"{field_name}_required")
    if value.get("context_kind") not in ALLOWED_CONTEXT_KINDS:
        errors.append("context_kind_invalid")
    if value.get("status") not in ALLOWED_STATUSES:
        errors.append("status_invalid")

    _validate_path_list(value.get("read_order"), "read_order", errors)
    _validate_path_list(value.get("source_receipts"), "source_receipts", errors)
    relationship_refs = value.get("relationship_refs", [])
    if relationship_refs:
        _validate_path_list(relationship_refs, "relationship_refs", errors)

    source_hashes = value.get("source_hashes")
    if not isinstance(source_hashes, dict) or not source_hashes:
        errors.append("source_hashes_required")
    elif any(not _sha256(digest) for digest in source_hashes.values()):
        errors.append("source_hashes_include_invalid_sha256")

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


def classify_context_package_record(record: ContextPackageRecord | Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_context_package_record(record)
    return {
        "schema_id": "ion.vnext.context_package_core.classification.v1",
        "ok": not errors,
        "verdict": READY_VERDICT if not errors else BLOCKED_VERDICT,
        "errors": list(errors),
        "context_package_hash": stable_context_package_hash(record),
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _validate_path_list(value: Any, field_name: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{field_name}_required")
        return
    if any(not _path_allowed(path) for path in value):
        errors.append(f"{field_name}_include_forbidden_or_runtime_path")


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


def _path_allowed(path: Any) -> bool:
    if not isinstance(path, str) or not path.strip():
        return False
    raw = path.replace("\\", "/")
    if raw.startswith("/") or ".." in raw.split("/"):
        return False
    normalized = raw.lstrip("./")
    if any(fragment in normalized for fragment in FORBIDDEN_PATH_FRAGMENTS):
        return False
    if any(normalized.startswith(prefix) for prefix in FORBIDDEN_RUNTIME_PREFIXES):
        return False
    return not any(word in f"/{normalized}/" for word in FORBIDDEN_STATE_WORDS)
