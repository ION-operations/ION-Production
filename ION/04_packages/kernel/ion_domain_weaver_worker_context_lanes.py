"""Per-worker Domain Weaver context lanes.

This module keeps worker-local context receipts out of the lead Codex Solo
capsule. Worker rows are carrier intake only: they may be summarized for fan-in,
but they do not assert accepted state or production/live/secrets authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, Mapping


WORKER_CONTEXT_LANE_SCHEMA_ID = "ion.domain_weaver.worker_context_lane.v0_1"
CONTEXT_RECEIPT_SCHEMA_ID = "ion.domain_weaver.worker_context_receipt.v0_1"
CANDIDATE_ROW_SCHEMA_ID = "ion.domain_weaver.worker_candidate_row.v0_1"
FANIN_SUMMARY_SCHEMA_ID = "ion.domain_weaver.worker_fanin_summary.v0_1"
SPAWN_REQUEST_SCHEMA_ID = "ion.domain_weaver.worker_spawn_request.v0_1"

WORKER_CONTEXT_RELATIVE_ROOT = Path("ION/05_context/current/domain_weaver/workers")
CODEX_SOLO_RELATIVE_PATH = Path("ION/05_context/current/codex_solo")

_RESERVED_WORKER_IDS = {
    "codex-solo",
    "codex_solo",
    "solo",
    "lead",
    "lead-capsule",
    "lead_capsule",
}

_FORBIDDEN_AUTHORITY_KEYS = {
    "accepted_state",
    "accepted_state_claim",
    "accepted_state_authority",
    "production",
    "production_authority",
    "live_execution",
    "live_execution_authority",
    "secrets",
    "secrets_authority",
    "secret_access",
    "registry",
    "registry_movement",
    "materialization",
    "materialization_authority",
    "materialization_movement",
    "materialize_all",
}

_DEFAULT_SPAWN_FORBIDDEN_ACTIONS = (
    "accepted_state_claim",
    "production_or_live_execution",
    "secrets_access",
    "registry_or_materialization_movement",
    "direct_codex_solo_write",
    "raw_external_codex_exec",
    "direct_nested_subagent_spawn",
)


@dataclass(frozen=True)
class WorkerContextLane:
    """Resolved per-worker Domain Weaver context lane."""

    active_root: Path
    worker_id_raw: str
    worker_id: str
    context_path: Path

    @property
    def receipts_path(self) -> Path:
        return self.context_path / "receipts"

    @property
    def candidates_path(self) -> Path:
        return self.context_path / "candidates"

    @property
    def fanin_path(self) -> Path:
        return self.context_path / "fanin"

    @property
    def spawn_requests_path(self) -> Path:
        return self.context_path / "spawn_requests"

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_id": WORKER_CONTEXT_LANE_SCHEMA_ID,
            "worker_id_raw": self.worker_id_raw,
            "worker_id": self.worker_id,
            "active_root": str(self.active_root),
            "context_path": _relative_posix(self.active_root, self.context_path),
            "receipts_path": _relative_posix(self.active_root, self.receipts_path),
            "candidates_path": _relative_posix(self.active_root, self.candidates_path),
            "fanin_path": _relative_posix(self.active_root, self.fanin_path),
            "spawn_requests_path": _relative_posix(
                self.active_root,
                self.spawn_requests_path,
            ),
            "codex_solo_path": CODEX_SOLO_RELATIVE_PATH.as_posix(),
            "codex_solo_write_allowed": False,
            "accepted_state": False,
        }


def sanitize_worker_id(worker_id: str) -> str:
    """Return a path-safe worker id, rejecting lead-capsule aliases."""

    raw = str(worker_id or "").strip()
    if not raw:
        raise ValueError("worker_id_required")
    if "/" in raw or "\\" in raw:
        raise ValueError("worker_id_must_not_contain_path_separators")
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", raw).strip("._-").lower()
    if not slug:
        raise ValueError("worker_id_empty_after_sanitization")
    if slug in {".", ".."} or slug in _RESERVED_WORKER_IDS:
        raise ValueError("worker_id_reserved_for_lead_capsule")
    if len(slug) > 96:
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
        slug = f"{slug[:83].rstrip('._-')}-{digest}"
    return slug


def resolve_worker_context_lane(
    active_root: str | Path,
    worker_id: str,
    *,
    create: bool = False,
) -> WorkerContextLane:
    """Resolve or create a worker-local context lane under Domain Weaver."""

    root = _require_active_root(active_root)
    safe_worker_id = sanitize_worker_id(worker_id)
    context_path = root / WORKER_CONTEXT_RELATIVE_ROOT / safe_worker_id / "context"
    _assert_under_worker_root(root, context_path)
    lane = WorkerContextLane(
        active_root=root,
        worker_id_raw=str(worker_id),
        worker_id=safe_worker_id,
        context_path=context_path,
    )
    if create:
        for path in (
            lane.receipts_path,
            lane.candidates_path,
            lane.fanin_path,
            lane.spawn_requests_path,
        ):
            path.mkdir(parents=True, exist_ok=True)
    return lane


def write_context_receipt(
    active_root: str | Path,
    worker_id: str,
    payload: Mapping[str, Any],
    *,
    row_id: str | None = None,
) -> dict[str, Any]:
    """Write a worker-local context receipt row."""

    return _write_worker_row(
        active_root,
        worker_id,
        payload,
        kind="context_receipt",
        schema_id=CONTEXT_RECEIPT_SCHEMA_ID,
        row_dir_name="receipts",
        suffix=".json",
        row_id=row_id,
    )


def write_candidate_row(
    active_root: str | Path,
    worker_id: str,
    payload: Mapping[str, Any],
    *,
    row_id: str | None = None,
) -> dict[str, Any]:
    """Write a worker-local candidate row."""

    return _write_worker_row(
        active_root,
        worker_id,
        payload,
        kind="candidate_row",
        schema_id=CANDIDATE_ROW_SCHEMA_ID,
        row_dir_name="candidates",
        suffix=".candidate.json",
        row_id=row_id,
    )


def write_spawn_request(
    active_root: str | Path,
    parent_worker_id: str,
    *,
    requested_domain: str,
    requested_packet: str,
    allowed_scope: Any,
    forbidden_actions: Any,
    evidence_requirements: Any,
    requested_callsign: str | None = None,
    requested_true_name: str | None = None,
    requested_role_id: str | None = None,
    requested_role_tier: str | None = None,
    work_class: str | None = None,
    lane_id: str | None = None,
    domain_context_package: str | None = None,
    required_context_reads: Any | None = None,
    planned_writes: Any | None = None,
    row_id: str | None = None,
) -> dict[str, Any]:
    """Write a worker-local queue-mediated child specialist request.

    The artifact is a request for lead fan-in and queue settlement only. It does
    not spawn a process, call Codex, write the lead capsule, or grant authority.
    """

    request_payload: dict[str, Any] = {
        "requested_domain": _required_text(requested_domain, "requested_domain"),
        "requested_packet": _required_text(requested_packet, "requested_packet"),
        "allowed_scope": _required_json_value(allowed_scope, "allowed_scope"),
        "forbidden_actions": _merge_forbidden_actions(forbidden_actions),
        "evidence_requirements": _required_json_value(
            evidence_requirements,
            "evidence_requirements",
        ),
    }
    if requested_callsign is not None:
        request_payload["requested_callsign"] = _required_text(
            requested_callsign,
            "requested_callsign",
        )
    if requested_true_name is not None:
        request_payload["requested_true_name"] = _required_text(
            requested_true_name,
            "requested_true_name",
        )
    optional_text_fields = {
        "requested_role_id": requested_role_id,
        "requested_role_tier": requested_role_tier,
        "work_class": work_class,
        "lane_id": lane_id,
    }
    for field, value in optional_text_fields.items():
        if value is not None:
            request_payload[field] = _required_text(value, field)
    if domain_context_package is not None:
        request_payload["domain_context_package"] = _required_json_value(
            domain_context_package,
            "domain_context_package",
        )
    if required_context_reads is not None:
        request_payload["required_context_reads"] = _required_json_value(
            required_context_reads,
            "required_context_reads",
        )
    if planned_writes is not None:
        request_payload["planned_writes"] = _required_json_value(
            planned_writes,
            "planned_writes",
        )
    _assert_no_forbidden_authority_claims(request_payload)

    lane = resolve_worker_context_lane(active_root, parent_worker_id, create=True)
    envelope: dict[str, Any] = {
        "schema_id": SPAWN_REQUEST_SCHEMA_ID,
        "kind": "spawn_request",
        "status": "requested",
        "created_at": _utc_now(),
        "parent_worker_id_raw": lane.worker_id_raw,
        "parent_worker_id": lane.worker_id,
        "worker_id_raw": lane.worker_id_raw,
        "worker_id": lane.worker_id,
        "authority": _authority_block(),
        "spawn_execution": {
            "actual_spawn_performed": False,
            "queue_mediated_required": True,
            "lead_fanin_required": True,
            "raw_external_codex_exec_allowed": False,
            "direct_nested_subagent_spawn_allowed": False,
        },
        "paths": {
            "active_root": str(lane.active_root),
            "worker_context_path": _relative_posix(lane.active_root, lane.context_path),
            "spawn_requests_path": _relative_posix(
                lane.active_root,
                lane.spawn_requests_path,
            ),
            "codex_solo_path": CODEX_SOLO_RELATIVE_PATH.as_posix(),
            "codex_solo_touched": False,
        },
        **request_payload,
    }
    name = _row_filename(row_id, envelope, suffix=".spawn_request.json")
    path = lane.spawn_requests_path / name
    _assert_under_worker_root(lane.active_root, path)
    _atomic_write_json(path, envelope)
    result = dict(envelope)
    result["path"] = _relative_posix(lane.active_root, path)
    return result


def list_worker_context_refs(
    active_root: str | Path,
    worker_id: str,
) -> dict[str, Any]:
    """List worker-local receipt and candidate refs without reading payloads."""

    lane = resolve_worker_context_lane(active_root, worker_id, create=False)
    receipt_refs = _list_refs(lane.active_root, lane.receipts_path, "*.json")
    candidate_refs = _list_refs(lane.active_root, lane.candidates_path, "*.candidate.json")
    spawn_request_refs = _list_refs(
        lane.active_root,
        lane.spawn_requests_path,
        "*.spawn_request.json",
    )
    return {
        "schema_id": FANIN_SUMMARY_SCHEMA_ID,
        "worker_id": lane.worker_id,
        "worker_id_raw": lane.worker_id_raw,
        "context_path": _relative_posix(lane.active_root, lane.context_path),
        "receipt_refs": receipt_refs,
        "candidate_refs": candidate_refs,
        "spawn_request_refs": spawn_request_refs,
        "receipt_count": len(receipt_refs),
        "candidate_count": len(candidate_refs),
        "spawn_request_count": len(spawn_request_refs),
        "accepted_state": False,
        "carrier_intake_only": True,
        "codex_solo_touched": False,
    }


def write_fanin_summary(
    active_root: str | Path,
    worker_id: str,
    *,
    row_id: str | None = None,
) -> dict[str, Any]:
    """Write a worker-local fan-in summary made only of worker row refs."""

    lane = resolve_worker_context_lane(active_root, worker_id, create=True)
    summary = list_worker_context_refs(active_root, worker_id)
    summary.update(
        {
            "kind": "fanin_summary",
            "created_at": _utc_now(),
            "authority": _authority_block(),
        }
    )
    name = _row_filename(row_id, summary, suffix=".fanin.json")
    path = lane.fanin_path / name
    _atomic_write_json(path, summary)
    result = dict(summary)
    result["path"] = _relative_posix(lane.active_root, path)
    return result


def _write_worker_row(
    active_root: str | Path,
    worker_id: str,
    payload: Mapping[str, Any],
    *,
    kind: str,
    schema_id: str,
    row_dir_name: str,
    suffix: str,
    row_id: str | None,
) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise TypeError("payload_must_be_mapping")
    _assert_no_forbidden_authority_claims(payload)
    lane = resolve_worker_context_lane(active_root, worker_id, create=True)
    row_dir = getattr(lane, f"{row_dir_name}_path")
    envelope: dict[str, Any] = {
        "schema_id": schema_id,
        "kind": kind,
        "created_at": _utc_now(),
        "worker_id_raw": lane.worker_id_raw,
        "worker_id": lane.worker_id,
        "authority": _authority_block(),
        "paths": {
            "active_root": str(lane.active_root),
            "worker_context_path": _relative_posix(lane.active_root, lane.context_path),
            "codex_solo_path": CODEX_SOLO_RELATIVE_PATH.as_posix(),
            "codex_solo_touched": False,
        },
        "payload": dict(payload),
    }
    name = _row_filename(row_id, envelope, suffix=suffix)
    path = row_dir / name
    _assert_under_worker_root(lane.active_root, path)
    _atomic_write_json(path, envelope)
    result = dict(envelope)
    result["path"] = _relative_posix(lane.active_root, path)
    return result


def _require_active_root(active_root: str | Path) -> Path:
    root = Path(active_root).expanduser().resolve()
    if not (root / "pyproject.toml").is_file():
        raise ValueError("active_root_missing_pyproject")
    if not (root / "ION/REPO_AUTHORITY.md").is_file():
        raise ValueError("active_root_missing_repo_authority")
    return root


def _assert_under_worker_root(active_root: Path, path: Path) -> None:
    worker_root = (active_root / WORKER_CONTEXT_RELATIVE_ROOT).resolve()
    resolved = path.resolve()
    if not _is_relative_to(resolved, worker_root):
        raise ValueError("worker_lane_path_escape")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _assert_no_forbidden_authority_claims(payload: Mapping[str, Any]) -> None:
    _assert_no_forbidden_authority_claims_at(payload, path="payload")


def _assert_no_forbidden_authority_claims_at(value: Any, *, path: str) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized_key = _normalize_claim_key(str(key))
            if normalized_key in _FORBIDDEN_AUTHORITY_KEYS and item not in (
                None,
                False,
                "",
                [],
                {},
                0,
            ):
                raise ValueError(f"forbidden_authority_claim:{key}")
            _assert_no_forbidden_authority_claims_at(item, path=f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _assert_no_forbidden_authority_claims_at(item, path=f"{path}[{index}]")


def _normalize_claim_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", key.strip().lower()).strip("_")


def _required_text(value: Any, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"{field_name}_required")
    if "/" in text or "\\" in text:
        raise ValueError(f"{field_name}_must_not_contain_path_separators")
    return text


def _required_json_value(value: Any, field_name: str) -> Any:
    if value in (None, "", [], {}):
        raise ValueError(f"{field_name}_required")
    json.dumps(value, sort_keys=True, default=str)
    return value


def _merge_forbidden_actions(forbidden_actions: Any) -> list[Any]:
    requested = _required_json_value(forbidden_actions, "forbidden_actions")
    if isinstance(requested, str):
        requested_items: list[Any] = [requested]
    elif isinstance(requested, (list, tuple)):
        requested_items = list(requested)
    else:
        raise ValueError("forbidden_actions_must_be_list_or_string")
    merged: list[Any] = list(_DEFAULT_SPAWN_FORBIDDEN_ACTIONS)
    for item in requested_items:
        if item not in merged:
            merged.append(item)
    return merged


def _legacy_assert_no_forbidden_authority_claims(payload: Mapping[str, Any]) -> None:
    for key in _FORBIDDEN_AUTHORITY_KEYS:
        value = payload.get(key)
        if value not in (None, False, "", [], {}, 0):
            raise ValueError(f"forbidden_authority_claim:{key}")


def _authority_block() -> dict[str, Any]:
    return {
        "accepted_state": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "registry_movement": False,
        "materialization_movement": False,
        "carrier_intake_only": True,
        "codex_solo_write_allowed": False,
    }


def _row_filename(row_id: str | None, payload: Mapping[str, Any], *, suffix: str) -> str:
    if row_id:
        stem = re.sub(r"[^A-Za-z0-9._-]+", "-", str(row_id).strip()).strip("._-").lower()
        if not stem or stem in {".", ".."}:
            raise ValueError("row_id_empty_after_sanitization")
    else:
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()[:12]
        stem = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}-{digest}"
    if not suffix.startswith("."):
        suffix = f".{suffix}"
    if stem.endswith(suffix):
        return stem
    return f"{stem}{suffix}"


def _list_refs(active_root: Path, directory: Path, pattern: str) -> list[str]:
    if not directory.is_dir():
        return []
    refs = []
    for path in sorted(directory.glob(pattern)):
        if path.is_file():
            _assert_under_worker_root(active_root, path)
            refs.append(_relative_posix(active_root, path))
    return refs


def _relative_posix(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(body, encoding="utf-8")
    tmp.replace(path)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
