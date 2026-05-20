"""Small vNext receipt primitives for source-bound governance evidence.

This candidate is intentionally not a runtime receipt writer. It creates,
validates, classifies, and hashes in-memory receipt records only. Callers that
write receipts must pass through later path-authority and artifact gates.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Mapping, Sequence


SCHEMA_ID = "ion.vnext.receipt_core.v1"
READY_VERDICT = "ION_RECEIPT_CORE_READY"
BLOCKED_VERDICT = "ION_RECEIPT_CORE_BLOCKED"

ALLOWED_RECEIPT_TYPES = {
    "context_proof",
    "template_action_proof",
    "carrier_mount",
    "operator_artifact_hygiene",
    "control_promotion",
    "selection_report",
    "validation",
}
ALLOWED_STATUSES = {
    "CANDIDATE",
    "LANDED_WITH_RECEIPT",
    "BLOCKED",
    "REJECTED",
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
    "ION/05_context/runtime_state/",
)


@dataclass(frozen=True)
class ReceiptRecord:
    schema_id: str
    receipt_id: str
    receipt_type: str
    status: str
    created_at: str
    producer: str
    subject: str
    claim: str
    source_paths: tuple[str, ...]
    evidence_hashes: Mapping[str, str] = field(default_factory=dict)
    authority: Mapping[str, bool] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    payload: Mapping[str, Any] = field(default_factory=dict)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_receipt_record(
    *,
    receipt_type: str,
    producer: str,
    subject: str,
    claim: str,
    source_paths: Sequence[str],
    status: str = "CANDIDATE",
    evidence_hashes: Mapping[str, str] | None = None,
    authority: Mapping[str, bool] | None = None,
    warnings: Sequence[str] | None = None,
    payload: Mapping[str, Any] | None = None,
    created_at: str | None = None,
    receipt_id: str | None = None,
) -> ReceiptRecord:
    timestamp = created_at or utc_now()
    normalized_authority = {flag: False for flag in AUTHORITY_FLAGS}
    normalized_authority.update({str(key): bool(value) for key, value in (authority or {}).items()})
    normalized_hashes = {str(key): str(value) for key, value in (evidence_hashes or {}).items()}
    normalized_sources = tuple(str(path) for path in source_paths)
    rid = receipt_id or _stable_id(
        "receipt-core",
        receipt_type,
        producer,
        subject,
        claim,
        timestamp,
        *normalized_sources,
        *[f"{key}={value}" for key, value in sorted(normalized_hashes.items())],
    )
    return ReceiptRecord(
        schema_id=SCHEMA_ID,
        receipt_id=rid,
        receipt_type=receipt_type,
        status=status,
        created_at=timestamp,
        producer=producer,
        subject=subject,
        claim=claim,
        source_paths=normalized_sources,
        evidence_hashes=normalized_hashes,
        authority=normalized_authority,
        warnings=tuple(str(warning) for warning in (warnings or ())),
        payload=dict(payload or {}),
    )


def receipt_to_dict(receipt: ReceiptRecord | Mapping[str, Any]) -> dict[str, Any]:
    value = asdict(receipt) if isinstance(receipt, ReceiptRecord) else dict(receipt)
    return _jsonable(value)


def stable_receipt_hash(receipt: ReceiptRecord | Mapping[str, Any]) -> str:
    value = receipt_to_dict(receipt)
    value.pop("receipt_hash", None)
    payload = json.dumps(_sort_jsonable(value), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def attach_receipt_hash(receipt: ReceiptRecord | Mapping[str, Any]) -> dict[str, Any]:
    value = receipt_to_dict(receipt)
    value["receipt_hash"] = stable_receipt_hash(value)
    return value


def validate_receipt_record(receipt: ReceiptRecord | Mapping[str, Any]) -> tuple[str, ...]:
    value = receipt_to_dict(receipt)
    errors: list[str] = []

    if value.get("schema_id") != SCHEMA_ID:
        errors.append("schema_id_invalid")
    if not _non_empty(value.get("receipt_id")):
        errors.append("receipt_id_required")
    if value.get("receipt_type") not in ALLOWED_RECEIPT_TYPES:
        errors.append("receipt_type_invalid")
    if value.get("status") not in ALLOWED_STATUSES:
        errors.append("status_invalid")
    for field_name in ("created_at", "producer", "subject", "claim"):
        if not _non_empty(value.get(field_name)):
            errors.append(f"{field_name}_required")

    source_paths = value.get("source_paths")
    if not isinstance(source_paths, list) or not source_paths:
        errors.append("source_paths_required")
    elif any(not _path_allowed(path) for path in source_paths):
        errors.append("source_paths_include_forbidden_or_runtime_path")

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

    if value.get("payload") is not None and not isinstance(value.get("payload"), dict):
        errors.append("payload_must_be_mapping")
    if value.get("warnings") is not None and not isinstance(value.get("warnings"), list):
        errors.append("warnings_must_be_list")

    return tuple(errors)


def classify_receipt_record(receipt: ReceiptRecord | Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_receipt_record(receipt)
    return {
        "schema_id": "ion.vnext.receipt_core.classification.v1",
        "ok": not errors,
        "verdict": READY_VERDICT if not errors else BLOCKED_VERDICT,
        "errors": list(errors),
        "receipt_hash": stable_receipt_hash(receipt),
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update(part.encode("utf-8"))
        digest.update(b"\0")
    return f"{prefix}-{digest.hexdigest()[:16]}"


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
    return not any(normalized.startswith(prefix) for prefix in FORBIDDEN_RUNTIME_PREFIXES)
