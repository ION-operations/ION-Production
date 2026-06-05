"""Pure no-write materialization pointer helpers for Domain Weaver.

This leaf module only shapes deterministic candidate records. It must not
import the Domain Weaver monolith, inspect the filesystem, write files, mutate
registries, refresh projections, invoke queues, or claim materialization
readiness.
"""
from __future__ import annotations

import hashlib
from typing import Any, Mapping, Sequence

MATERIALIZATION_POINTER_SCHEMA_ID = "ion.domain_weaver.materialization_pointer.v0_1_candidate"
MATERIALIZATION_POINTER_STATUS_ROW_SCHEMA_ID = (
    "ion.domain_weaver.materialization_pointer_status_row.v0_1_candidate"
)
MATERIALIZATION_POINTER_PATH_ROW_SCHEMA_ID = (
    "ion.domain_weaver.materialization_pointer_path_row.v0_1_candidate"
)
MATERIALIZATION_POINTER_SUMMARY_SCHEMA_ID = (
    "ion.domain_weaver.materialization_pointer_summary.v0_1_candidate"
)

_READY_STATUS_TOKENS = {
    "accepted",
    "complete",
    "materialization_ready",
    "ready",
    "ready_to_materialize",
}

_SAFE_STATUS_TOKENS = {
    "blocked",
    "blocked_ready_claim_rejected",
    "candidate",
    "needs_review",
    "not_ready",
    "path_only",
    "pointer_only",
    "settlement_required",
    "status_only",
}

_READY_CLAIM_BLOCKER = "materialization_ready_true_claim_forbidden"


def domain_weaver_materialization_pointer_authority() -> dict[str, bool]:
    """Return the fixed authority envelope for pointer-only candidate shaping."""

    return {
        "candidate_shape_only": True,
        "materialization_write_authority": False,
        "registry_mutation_authority": False,
        "topology_movement_authority": False,
        "ui_projection_movement_authority": False,
        "live_execution_authority": False,
        "queue_runner_invocation_authority": False,
        "queue_dispatch_authority": False,
        "lifecycle_mutation_authority": False,
        "operator_action_history_mutation_authority": False,
        "projection_refresh_authority": False,
        "accepted_state_authority": False,
        "production_authority": False,
        "secrets_authority": False,
        "materialization_ready_claim_authority": False,
    }


def domain_weaver_materialization_pointer_id(
    *,
    pointer_kind: Any,
    target_path: Any = "",
    source_path: Any = "",
    subject_id: Any = "",
) -> str:
    """Build a deterministic opaque pointer id from stable caller-supplied fields."""

    seed = "\n".join(
        (
            _clean_text(pointer_kind, "unspecified"),
            _clean_text(subject_id),
            _clean_text(source_path),
            _clean_text(target_path),
        )
    )
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return f"dw_mat_ptr_{digest[:16]}"


def shape_domain_weaver_materialization_path_row(
    *,
    path: Any,
    path_kind: Any = "candidate_path",
    source_field: Any = "",
    required: bool = True,
    reason: Any = "",
) -> dict[str, Any]:
    """Shape a path reference without probing or creating filesystem state."""

    return {
        "schema_id": MATERIALIZATION_POINTER_PATH_ROW_SCHEMA_ID,
        "row_kind": "domain_weaver_materialization_pointer_path_row",
        "path": _clean_text(path),
        "path_kind": _clean_status_token(path_kind, "candidate_path"),
        "source_field": _clean_text(source_field),
        "required": bool(required),
        "reason": _clean_text(reason),
        "path_probe_performed": False,
        "exists": None,
        "sha256": None,
        "would_create_path": False,
        "would_write_path": False,
        "authority": domain_weaver_materialization_pointer_authority(),
    }


def shape_domain_weaver_materialization_status_row(
    *,
    pointer_id: Any,
    status: Any = "candidate",
    summary: Any = "",
    blockers: Sequence[Any] = (),
    warnings: Sequence[Any] = (),
    materialization_ready: Any = False,
    next_action: Any = "settlement_review_required_before_materialization_claim",
) -> dict[str, Any]:
    """Shape a status row while rejecting any materialization-ready claim."""

    cleaned_blockers = _clean_list(blockers)
    requested_status = _clean_status_token(status, "candidate")
    ready_claim_rejected = bool(materialization_ready) or requested_status in _READY_STATUS_TOKENS
    if ready_claim_rejected and _READY_CLAIM_BLOCKER not in cleaned_blockers:
        cleaned_blockers = [*cleaned_blockers, _READY_CLAIM_BLOCKER]

    return {
        "schema_id": MATERIALIZATION_POINTER_STATUS_ROW_SCHEMA_ID,
        "row_kind": "domain_weaver_materialization_pointer_status_row",
        "pointer_id": _clean_text(pointer_id),
        "requested_status": requested_status,
        "status": _safe_status(requested_status, cleaned_blockers, ready_claim_rejected),
        "summary": _clean_text(summary),
        "blockers": cleaned_blockers,
        "warnings": _clean_list(warnings),
        "materialization_ready": False,
        "materialization_ready_claim_rejected": ready_claim_rejected,
        "next_action": _clean_text(next_action, "settlement_review_required_before_materialization_claim"),
        "would_materialize": False,
        "would_write": False,
        "authority": domain_weaver_materialization_pointer_authority(),
    }


def shape_domain_weaver_materialization_pointer(
    *,
    pointer_kind: Any,
    target_path: Any = "",
    source_path: Any = "",
    subject_id: Any = "",
    status: Any = "candidate",
    summary: Any = "",
    blockers: Sequence[Any] = (),
    warnings: Sequence[Any] = (),
    evidence_paths: Sequence[Any] = (),
    path_rows: Sequence[Mapping[str, Any]] = (),
    materialization_ready: Any = False,
) -> dict[str, Any]:
    """Shape a complete candidate pointer record without materializing anything."""

    cleaned_pointer_kind = _clean_status_token(pointer_kind, "unspecified")
    cleaned_target_path = _clean_text(target_path)
    cleaned_source_path = _clean_text(source_path)
    cleaned_subject_id = _clean_text(subject_id)
    pointer_id = domain_weaver_materialization_pointer_id(
        pointer_kind=cleaned_pointer_kind,
        subject_id=cleaned_subject_id,
        source_path=cleaned_source_path,
        target_path=cleaned_target_path,
    )
    shaped_path_rows = _pointer_path_rows(
        target_path=cleaned_target_path,
        source_path=cleaned_source_path,
        evidence_paths=evidence_paths,
        supplied_rows=path_rows,
    )
    status_row = shape_domain_weaver_materialization_status_row(
        pointer_id=pointer_id,
        status=status,
        summary=summary,
        blockers=blockers,
        warnings=warnings,
        materialization_ready=materialization_ready,
    )

    return {
        "schema_id": MATERIALIZATION_POINTER_SCHEMA_ID,
        "row_kind": "domain_weaver_materialization_pointer_candidate",
        "pointer_id": pointer_id,
        "pointer_kind": cleaned_pointer_kind,
        "subject_id": cleaned_subject_id,
        "source_path": cleaned_source_path,
        "target_path": cleaned_target_path,
        "status": status_row["status"],
        "status_row": status_row,
        "path_rows": shaped_path_rows,
        "path_row_count": len(shaped_path_rows),
        "evidence_paths": _clean_list(evidence_paths),
        "materialization_ready": False,
        "materialization_ready_claim_rejected": status_row["materialization_ready_claim_rejected"],
        "would_materialize": False,
        "would_write": False,
        "authority": domain_weaver_materialization_pointer_authority(),
    }


def shape_domain_weaver_materialization_pointer_summary(
    pointers: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize shaped pointer candidates without promoting or writing them."""

    cleaned_pointers = [dict(pointer) for pointer in pointers if isinstance(pointer, Mapping)]
    status_counts: dict[str, int] = {}
    path_row_count = 0
    ready_claim_rejected_count = 0
    blocked_pointer_count = 0
    for pointer in cleaned_pointers:
        status = _clean_status_token(pointer.get("status"), "candidate")
        status_counts[status] = status_counts.get(status, 0) + 1
        path_row_count += _safe_int(pointer.get("path_row_count"))
        if bool(pointer.get("materialization_ready_claim_rejected")):
            ready_claim_rejected_count += 1
        if status.startswith("blocked") or status == "not_ready":
            blocked_pointer_count += 1

    return {
        "schema_id": MATERIALIZATION_POINTER_SUMMARY_SCHEMA_ID,
        "row_kind": "domain_weaver_materialization_pointer_summary",
        "pointer_count": len(cleaned_pointers),
        "path_row_count": path_row_count,
        "blocked_pointer_count": blocked_pointer_count,
        "ready_claim_rejected_count": ready_claim_rejected_count,
        "status_counts": {key: status_counts[key] for key in sorted(status_counts)},
        "materialization_ready": False,
        "would_materialize": False,
        "would_write": False,
        "would_refresh_projection": False,
        "authority": domain_weaver_materialization_pointer_authority(),
    }


def _pointer_path_rows(
    *,
    target_path: str,
    source_path: str,
    evidence_paths: Sequence[Any],
    supplied_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen_paths: set[tuple[str, str]] = set()

    for row in supplied_rows:
        if isinstance(row, Mapping):
            key = (
                _clean_text(row.get("path")),
                _clean_status_token(row.get("path_kind"), "candidate_path"),
            )
            if key[0] and key not in seen_paths:
                rows.append(
                    shape_domain_weaver_materialization_path_row(
                        path=key[0],
                        path_kind=key[1],
                        source_field=row.get("source_field", "supplied_path_rows"),
                        required=bool(row.get("required", True)),
                        reason=row.get("reason", "caller supplied path reference normalized to no-write shape"),
                    )
                )
                seen_paths.add(key)

    candidate_rows = (
        ("target_path", target_path, "materialization target path candidate"),
        ("source_path", source_path, "source pointer path candidate"),
    )
    for source_field, path, reason in candidate_rows:
        key = (path, source_field)
        if path and key not in seen_paths:
            rows.append(
                shape_domain_weaver_materialization_path_row(
                    path=path,
                    path_kind=source_field,
                    source_field=source_field,
                    reason=reason,
                )
            )
            seen_paths.add(key)

    for path in _clean_list(evidence_paths):
        key = (path, "evidence_path")
        if key not in seen_paths:
            rows.append(
                shape_domain_weaver_materialization_path_row(
                    path=path,
                    path_kind="evidence_path",
                    source_field="evidence_paths",
                    required=False,
                    reason="supporting evidence path reference",
                )
            )
            seen_paths.add(key)

    return rows


def _safe_status(status: str, blockers: Sequence[str], ready_claim_rejected: bool) -> str:
    if ready_claim_rejected:
        return "blocked_ready_claim_rejected"
    if blockers and status not in {"blocked", "not_ready"}:
        return "blocked"
    if status in _SAFE_STATUS_TOKENS:
        return status
    return "candidate"


def _safe_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return max(value, 0)
    return 0


def _clean_list(values: Sequence[Any]) -> list[str]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes, bytearray)):
        return []
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = _clean_text(value)
        if text and text not in seen:
            cleaned.append(text)
            seen.add(text)
    return cleaned


def _clean_status_token(value: Any, default: str) -> str:
    text = _clean_text(value, default).lower().replace("-", "_").replace(" ", "_")
    token = "".join(character for character in text if character.isalnum() or character == "_")
    return token or default


def _clean_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default
