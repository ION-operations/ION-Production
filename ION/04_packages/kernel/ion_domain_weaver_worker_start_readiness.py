"""Read-only Domain Weaver worker-start readiness projection.

This helper keeps Domain Weaver honest before it starts Codex CLI workers. It
does not queue, launch, mutate registries, materialize topology, or claim
accepted state. It only inspects queued work requests and verifies that each
queued lane has a fresh active context package through domain.context_active_resolver.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_domain_weaver_context_active_resolver import resolve_domain_active_context
from .ion_worker_shift_presence import load_shift_board
from .ion_working_capsule_identity import working_capsule_preflight

SCHEMA_ID = "ion.domain_weaver.worker_start_readiness.v0_1_candidate"
BACKLOG_HYGIENE_SCHEMA_ID = "ion.domain_weaver.worker_start_backlog_hygiene.v0_1_candidate"
CODEX_WORK_REQUESTS_DIR = Path("ION/05_context/current/chatgpt_connector/codex_work_requests")
QUEUEABLE_STATUSES = {"QUEUED_FOR_CODEX_CARRIER"}
CONTEXT_GATE_BLOCKED_STATUS = "CODEX_QUEUE_RUNNER_BLOCKED_CONTEXT_GATE"
READINESS_EVIDENCE_STATUSES = QUEUEABLE_STATUSES | {CONTEXT_GATE_BLOCKED_STATUS}
DEFAULT_MAX_CONTEXT_AGE_SECONDS = 48 * 60 * 60
DEFAULT_BACKLOG_EXAMPLE_LIMIT = 8
CONTEXT_ACTIVE_RESOLVER_SERVICE_DOMAIN_ID = "domain.context_active_resolver"
UNBOUND_WORKER_ID_VALUES = {
    "",
    "none",
    "null",
    "unknown",
    "unbound",
    "unbound_worker_id",
    "worker_id_unbound",
}
AGENT_ROLE_REQUEST_FIELDS = (
    "agent_role_id",
    "agent_role",
    "requested_role",
    "target_agent_role",
    "target_agent_role_id",
    "agent",
    "agent_id",
    "agent_display_name",
    "role_id",
)
ROLE_TIER_REQUEST_FIELDS = (
    "role_tier",
    "agent_role_tier",
    "requested_role_tier",
    "target_role_tier",
    "domain_weaver_role_tier",
)
CALLSIGN_REQUEST_FIELDS = (
    "callsign",
    "agent_callsign",
    "display_callsign",
    "worker_callsign",
    "true_name",
    "agent_true_name",
)
DOMAIN_REQUEST_FIELDS = (
    "domain_id",
    "target_domain_id",
    "route_domain_id",
    "context_domain_id",
    "agent_domain_id",
    "domain",
    "target_domain",
    "route_domain",
)
LANE_REQUEST_FIELDS = (
    "lane_id",
    "lane",
    "readiness_lane",
    "target_lane",
    "target_lane_id",
    "route_lane",
    "route_lane_id",
    "context_lane",
    "context_lane_id",
    "worker_lane",
    "worker_lane_id",
    "lane_request",
)
SELECTED_MOUNT_ID_REQUEST_FIELDS = (
    "selected_mount_id",
    "target_mount_id",
    "context_mount_id",
    "codex_agent_mount_id",
    "agent_mount_id",
    "mount_id",
)
SELECTED_MOUNT_PATH_REQUEST_FIELDS = (
    "selected_mount_path",
    "target_mount_path",
    "context_mount_path",
    "codex_agent_mount_path",
    "agent_mount_path",
    "codex_agent_mount",
    "mount_path",
)
READINESS_LANE_ALIASES = {
    "validation": "audit_lane",
    "validation_lane": "audit_lane",
    "audit": "audit_lane",
    "audit_lane": "audit_lane",
    "context": "context_lane",
    "context_lane": "context_lane",
    "architecture": "architecture_lane",
    "architecture_lane": "architecture_lane",
    "implementation": "implementation_lane",
    "implementation_lane": "implementation_lane",
    "comms": "comms_lane",
    "comms_lane": "comms_lane",
    "browser": "browser_lane",
    "browser_lane": "browser_lane",
    "maintenance": "maintenance_lane",
    "maintenance_lane": "maintenance_lane",
    "approval_governance": "approval_governance_lane",
    "approval_governance_lane": "approval_governance_lane",
    "settlement": "settlement_lane",
    "settlement_lane": "settlement_lane",
}
WORKER_START_BLOCKED_CAPSULE_PREFLIGHT_CLASSIFICATIONS = {
    "shared_codex_solo_fallback",
}


def _authority() -> dict[str, bool]:
    return {
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "materialization_write_authority": False,
    }


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _active_root_proof(root: Path) -> dict[str, Any]:
    pyproject = root / "pyproject.toml"
    repo_authority = root / "ION/REPO_AUTHORITY.md"
    proof_ok = pyproject.is_file() and repo_authority.is_file()
    return {
        "schema_id": "ion.active_root_proof.v0_1_candidate",
        "active_root": str(root),
        "active_root_realpath": str(root.resolve(strict=False)),
        "required_siblings": {
            "pyproject.toml": {
                "path": "pyproject.toml",
                "present": pyproject.is_file(),
            },
            "ION/REPO_AUTHORITY.md": {
                "path": "ION/REPO_AUTHORITY.md",
                "present": repo_authority.is_file(),
            },
        },
        "proof_ok": proof_ok,
        **_authority(),
    }


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _parse_datetime(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _first_string_with_field(payload: Mapping[str, Any], fields: tuple[str, ...]) -> tuple[str, str]:
    for field in fields:
        value = payload.get(field)
        if isinstance(value, str) and value.strip():
            return field, value.strip()
    for field in ("routing", "route", "context", "metadata", "domain_weaver", "worker", "request", "payload"):
        value = payload.get(field)
        if isinstance(value, Mapping):
            found_field, found = _first_string_with_field(value, fields)
            if found:
                return found_field, found
    return "", ""


def _first_string(payload: Mapping[str, Any], fields: tuple[str, ...]) -> str:
    return _first_string_with_field(payload, fields)[1]


def _repo_rel_path(root: Path, value: Any) -> str:
    text = _clean_text(value)
    if not text:
        return ""
    path = Path(text).expanduser()
    if not path.is_absolute():
        path = root / path
    return _rel(path.resolve(strict=False), root)


def _mount_path_from_capsule_path(root: Path, value: Any) -> str:
    rel = _repo_rel_path(root, value)
    if rel.endswith("/.ion"):
        return rel[: -len("/.ion")]
    return rel


def _mount_id_from_path(value: Any) -> str:
    text = _clean_text(value)
    return Path(text).name if text else ""


def _normalize_readiness_lane(value: Any) -> str:
    raw = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    if not raw:
        return ""
    if raw in READINESS_LANE_ALIASES:
        return READINESS_LANE_ALIASES[raw]
    candidate = f"{raw}_lane"
    return READINESS_LANE_ALIASES.get(candidate, str(value or "").strip())


def _capsule_identity_binding_fields(root: Path, identity_payload: Any) -> dict[str, Any]:
    identity = _mapping(identity_payload)
    if not identity:
        return {}
    identity_mount_path = ""
    for field in ("codex_agent_mount", "codex_agent_mount_path", "selected_mount_path", "mount_path", "cwd"):
        identity_mount_path = _repo_rel_path(root, identity.get(field))
        if identity_mount_path:
            break
    if not identity_mount_path:
        identity_mount_path = _mount_path_from_capsule_path(root, identity.get("working_capsule_path"))
    selected_mount_id = _first_string(identity, SELECTED_MOUNT_ID_REQUEST_FIELDS) or _mount_id_from_path(identity_mount_path)
    return {
        "domain_id": _clean_text(identity.get("domain_id")),
        "role_id": _clean_text(identity.get("role_id")),
        "agent_id": _clean_text(identity.get("agent_id")),
        "lane_id": _normalize_readiness_lane(_first_string(identity, LANE_REQUEST_FIELDS)),
        "selected_mount_id": selected_mount_id,
        "selected_mount_path": identity_mount_path,
        "working_capsule_path": _repo_rel_path(root, identity.get("working_capsule_path")),
        "capsule_identity_present": True,
    }


def _binding_mismatch(
    blockers: list[str],
    findings: list[dict[str, Any]],
    *,
    code: str,
    left_name: str,
    left: str,
    right_name: str,
    right: str,
) -> None:
    if left and right and left != right:
        blockers.append(code)
        findings.append(
            {
                "code": code,
                left_name: left,
                right_name: right,
            }
        )


def _capsule_request_binding_for_row(
    root: Path,
    row: Mapping[str, Any],
    resolver: Mapping[str, Any] | None,
) -> dict[str, Any]:
    identity = _mapping(row.get("capsule_identity_binding_fields"))
    if not identity:
        return {
            "schema_id": "ion.domain_weaver.working_capsule_request_binding.v0_1_candidate",
            "ok": True,
            "checked": False,
            "finding": "no_declared_working_capsule_identity_to_bind",
            "blockers": [],
            "findings": [],
        }

    resolver_selected = _mapping(_mapping(resolver).get("selected"))
    request_lane_id = _normalize_readiness_lane(row.get("lane_id"))
    identity_lane_id = _normalize_readiness_lane(identity.get("lane_id"))
    selected_lane_ids = [
        _normalize_readiness_lane(item)
        for item in list(resolver_selected.get("lane_ids") or [])
        if _normalize_readiness_lane(item)
    ]
    request_mount_path = _repo_rel_path(root, row.get("requested_selected_mount_path"))
    selected_mount_path = _repo_rel_path(root, resolver_selected.get("mount_path"))
    selected_mount_id = _clean_text(resolver_selected.get("mount_id"))
    identity_mount_path = _clean_text(identity.get("selected_mount_path"))
    identity_mount_id = _clean_text(identity.get("selected_mount_id")) or _mount_id_from_path(identity_mount_path)
    request_mount_id = _clean_text(row.get("requested_selected_mount_id"))

    blockers: list[str] = []
    findings: list[dict[str, Any]] = []
    _binding_mismatch(
        blockers,
        findings,
        code="working_capsule_domain_id_request_mismatch",
        left_name="request_domain_id",
        left=_clean_text(row.get("domain_id")),
        right_name="capsule_domain_id",
        right=_clean_text(identity.get("domain_id")),
    )
    _binding_mismatch(
        blockers,
        findings,
        code="working_capsule_role_id_request_mismatch",
        left_name="request_role_id",
        left=_clean_text(row.get("role_id")),
        right_name="capsule_role_id",
        right=_clean_text(identity.get("role_id")),
    )
    _binding_mismatch(
        blockers,
        findings,
        code="working_capsule_lane_id_request_mismatch",
        left_name="request_lane_id",
        left=request_lane_id,
        right_name="capsule_lane_id",
        right=identity_lane_id,
    )
    if request_lane_id and selected_lane_ids and request_lane_id not in selected_lane_ids:
        blockers.append("selected_mount_lane_id_request_mismatch")
        findings.append(
            {
                "code": "selected_mount_lane_id_request_mismatch",
                "request_lane_id": request_lane_id,
                "selected_lane_ids": selected_lane_ids,
            }
        )
    _binding_mismatch(
        blockers,
        findings,
        code="request_selected_mount_id_mismatch",
        left_name="request_selected_mount_id",
        left=request_mount_id,
        right_name="resolver_selected_mount_id",
        right=selected_mount_id,
    )
    _binding_mismatch(
        blockers,
        findings,
        code="request_selected_mount_path_mismatch",
        left_name="request_selected_mount_path",
        left=request_mount_path,
        right_name="resolver_selected_mount_path",
        right=selected_mount_path,
    )
    _binding_mismatch(
        blockers,
        findings,
        code="working_capsule_selected_mount_id_mismatch",
        left_name="capsule_selected_mount_id",
        left=identity_mount_id,
        right_name="resolver_selected_mount_id",
        right=selected_mount_id,
    )
    _binding_mismatch(
        blockers,
        findings,
        code="working_capsule_selected_mount_path_mismatch",
        left_name="capsule_selected_mount_path",
        left=identity_mount_path,
        right_name="resolver_selected_mount_path",
        right=selected_mount_path,
    )
    _binding_mismatch(
        blockers,
        findings,
        code="working_capsule_request_mount_id_mismatch",
        left_name="request_selected_mount_id",
        left=request_mount_id,
        right_name="capsule_selected_mount_id",
        right=identity_mount_id,
    )
    _binding_mismatch(
        blockers,
        findings,
        code="working_capsule_request_mount_path_mismatch",
        left_name="request_selected_mount_path",
        left=request_mount_path,
        right_name="capsule_selected_mount_path",
        right=identity_mount_path,
    )

    blockers = list(dict.fromkeys(blockers))
    return {
        "schema_id": "ion.domain_weaver.working_capsule_request_binding.v0_1_candidate",
        "ok": not blockers,
        "checked": True,
        "finding": "working_capsule_request_binding_ready" if not blockers else "working_capsule_request_binding_blocked",
        "request_domain_id": _clean_text(row.get("domain_id")) or None,
        "capsule_domain_id": _clean_text(identity.get("domain_id")) or None,
        "request_role_id": _clean_text(row.get("role_id")) or None,
        "capsule_role_id": _clean_text(identity.get("role_id")) or None,
        "request_lane_id": request_lane_id or None,
        "capsule_lane_id": identity_lane_id or None,
        "request_selected_mount_id": request_mount_id or None,
        "capsule_selected_mount_id": identity_mount_id or None,
        "resolver_selected_mount_id": selected_mount_id or None,
        "request_selected_mount_path": request_mount_path or None,
        "capsule_selected_mount_path": identity_mount_path or None,
        "resolver_selected_mount_path": selected_mount_path or None,
        "blockers": blockers,
        "findings": findings,
    }


def _combine_capsule_blockers(*groups: list[str]) -> list[str]:
    return list(dict.fromkeys(str(code).strip() for group in groups for code in group if str(code).strip()))


def _worker_identity_for_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": "ion.domain_weaver.worker_identity.v0_1_candidate",
        "lane_id": str(row.get("lane_id") or "").strip() or None,
        "raw_lane_id": str(row.get("raw_lane_id") or "").strip() or None,
        "domain_id": str(row.get("domain_id") or "").strip() or None,
        "role_id": str(row.get("role_id") or "").strip() or None,
        "role_tier": str(row.get("role_tier") or "").strip() or None,
        "callsign": str(row.get("callsign") or "").strip() or None,
        "identity_authority": "carrier_declared_candidate_only",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def _domain_alignment_for_row(row: Mapping[str, Any]) -> dict[str, Any]:
    target_domain_id = str(row.get("domain_id") or "").strip()
    return {
        "schema_id": "ion.domain_weaver.worker_domain_alignment.v0_1_candidate",
        "resolver_service_domain_id": CONTEXT_ACTIVE_RESOLVER_SERVICE_DOMAIN_ID,
        "target_request_domain_id": target_domain_id or None,
        "prestart_domain_checked": target_domain_id or None,
        "queue_runner_domain_source": "request_payload",
        "uses_resolver_service_domain_as_target": target_domain_id == CONTEXT_ACTIVE_RESOLVER_SERVICE_DOMAIN_ID,
        "finding": "target_request_domain_checked" if target_domain_id else "target_request_domain_missing",
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _blocker_preserving_return_status(row: Mapping[str, Any], *, ready: bool, blockers: list[str]) -> dict[str, Any]:
    status = str(row.get("status") or "").strip()
    return {
        "schema_id": "ion.domain_weaver.worker_return_status.v0_1_candidate",
        "request_status": status or None,
        "queueable_for_start": bool(row.get("queueable_for_start")),
        "ready": bool(ready),
        "blockers": [str(code) for code in blockers if str(code).strip()],
        "carrier_intake_only": True,
        "product_state": False,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _lease_paths(lease: Mapping[str, Any]) -> list[str]:
    rows: list[str] = []
    for field in ("paths", "target_files", "target_paths", "raw_paths"):
        value = lease.get(field)
        if isinstance(value, list):
            rows.extend(str(item).strip() for item in value if str(item).strip())
    return rows


def _worker_id_is_unbound(value: Any) -> bool:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_") in UNBOUND_WORKER_ID_VALUES


def _worker_shift_conflict_posture(root: Path) -> dict[str, Any]:
    try:
        board = load_shift_board(root)
    except Exception as exc:
        return {
            "schema_id": "ion.domain_weaver.worker_shift_conflict_posture.v0_1_candidate",
            "available": False,
            "risk_level": "unknown",
            "finding": "worker_shift_board_unreadable",
            "error": exc.__class__.__name__,
            "blockers": ["worker_shift_board_unreadable"],
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    active_workers = list(board.get("active_workers") or board.get("active_shifts") or [])
    active_leases = [item for item in list(board.get("active_leases") or []) if isinstance(item, Mapping)]
    exclusive_leases = [
        lease
        for lease in active_leases
        if str(lease.get("lease_mode") or lease.get("mode") or lease.get("lease_type") or "").strip().lower() == "exclusive_write"
    ]
    write_like_leases = [
        lease
        for lease in active_leases
        if str(lease.get("lease_mode") or lease.get("mode") or lease.get("lease_type") or "").strip().lower()
        in {"write", "exclusive_write"}
    ]
    path_to_lease_ids: dict[str, list[str]] = {}
    for lease in write_like_leases:
        lease_id = str(lease.get("lease_id") or "").strip() or "unknown_lease"
        for path in _lease_paths(lease):
            path_to_lease_ids.setdefault(path, []).append(lease_id)
    overlapping_write_paths = sorted(path for path, lease_ids in path_to_lease_ids.items() if len(set(lease_ids)) > 1)
    unbound_lease_worker_ids = [
        str(lease.get("lease_id") or "").strip() or "unknown_lease"
        for lease in active_leases
        if _worker_id_is_unbound(lease.get("worker_id") or lease.get("agent_id") or lease.get("holder_id"))
    ]
    unbound_workers = [
        worker
        for worker in active_workers
        if isinstance(worker, Mapping)
        and (
            _worker_id_is_unbound(worker.get("worker_id") or worker.get("agent_id") or worker.get("holder_id"))
            or not (
                worker.get("worker_identity")
                or worker.get("codex_agent_mount_id")
                or worker.get("domain_context_package")
                or worker.get("role_id")
            )
        )
    ]
    blockers: list[str] = []
    if exclusive_leases:
        blockers.append("active_exclusive_write_lease_present")
    if overlapping_write_paths:
        blockers.append("overlapping_write_lease_hard_conflict_present")
    if unbound_lease_worker_ids or unbound_workers:
        blockers.append("unbound_worker_identity_present")
    if len(active_workers) > 1 and unbound_workers:
        blockers.append("shared_capsule_concurrency_hazard_live")
    risk_level = "none"
    if blockers:
        risk_level = "high"
    return {
        "schema_id": "ion.domain_weaver.worker_shift_conflict_posture.v0_1_candidate",
        "available": True,
        "risk_level": risk_level,
        "active_worker_count": len(active_workers),
        "active_lease_count": len(active_leases),
        "exclusive_write_lease_count": len(exclusive_leases),
        "write_like_lease_count": len(write_like_leases),
        "overlapping_write_paths": overlapping_write_paths,
        "unbound_lease_worker_ids": unbound_lease_worker_ids,
        "unbound_active_worker_count": len(unbound_workers),
        "blockers": blockers,
        "note": "readiness posture only; lease enforcement remains owned by Worker Shift and mutation gates",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }


def _capsule_identity_preflight_blockers(preflight: Mapping[str, Any]) -> list[str]:
    classification = str(preflight.get("classification") or "").strip()
    findings = [item for item in list(preflight.get("findings") or []) if isinstance(item, Mapping)]
    blockers: list[str] = []
    if not preflight.get("ok"):
        blockers.extend(str(item.get("code") or "").strip() for item in findings if str(item.get("code") or "").strip())
        if not blockers:
            blockers.append("working_capsule_identity_preflight_failed")
    if classification in WORKER_START_BLOCKED_CAPSULE_PREFLIGHT_CLASSIFICATIONS:
        blockers.append("shared_codex_solo_fallback_not_worker_start_identity")
    return list(dict.fromkeys(blockers))


def _queueable_request_rows(root: Path) -> list[dict[str, Any]]:
    requests_root = root / CODEX_WORK_REQUESTS_DIR
    if not requests_root.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(requests_root.glob("*.json")):
        payload = _read_json(path)
        status = str(payload.get("status") or "").strip()
        if status not in READINESS_EVIDENCE_STATUSES:
            continue
        context_gate = payload.get("context_gate") if isinstance(payload.get("context_gate"), Mapping) else None
        raw_lane_id = _first_string(payload, LANE_REQUEST_FIELDS)
        normalized_lane_id = _normalize_readiness_lane(raw_lane_id)
        capsule_preflight = working_capsule_preflight(root, payload, active_root_repair_allowed=False)
        capsule_blockers = _capsule_identity_preflight_blockers(capsule_preflight)
        requested_selected_mount_id = _first_string(payload, SELECTED_MOUNT_ID_REQUEST_FIELDS)
        requested_selected_mount_path = _first_string(payload, SELECTED_MOUNT_PATH_REQUEST_FIELDS)
        rows.append(
            {
                "request_id": payload.get("request_id"),
                "request_path": _rel(path, root),
                "created_at": payload.get("created_at"),
                "updated_at": payload.get("updated_at"),
                "packet_path": payload.get("packet_path"),
                "latest_return_packet_path": payload.get("latest_return_packet_path"),
                "status": status,
                "queueable_for_start": status in QUEUEABLE_STATUSES,
                "lane_id": normalized_lane_id,
                "raw_lane_id": raw_lane_id,
                "domain_id": _first_string(payload, DOMAIN_REQUEST_FIELDS),
                "role_id": _first_string(payload, AGENT_ROLE_REQUEST_FIELDS),
                "role_tier": _first_string(payload, ROLE_TIER_REQUEST_FIELDS),
                "callsign": _first_string(payload, CALLSIGN_REQUEST_FIELDS),
                "work_class": payload.get("work_class"),
                "request_kind": payload.get("request_kind"),
                "context_gate": context_gate,
                "capsule_identity_preflight": capsule_preflight,
                "capsule_identity_preflight_blockers": capsule_blockers,
                "capsule_identity_blockers": capsule_blockers,
                "capsule_identity_binding_fields": _capsule_identity_binding_fields(
                    root,
                    payload.get("working_capsule_identity"),
                ),
                "requested_selected_mount_id": requested_selected_mount_id or None,
                "requested_selected_mount_path": requested_selected_mount_path or None,
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
            }
        )
    return rows


def build_domain_weaver_worker_start_readiness(
    root: str | Path | None,
    *,
    max_age_seconds: int = DEFAULT_MAX_CONTEXT_AGE_SECONDS,
) -> dict[str, Any]:
    shell_root = Path(root or ".").expanduser().resolve()
    active_root_proof = _active_root_proof(shell_root)
    worker_shift_conflict_posture = _worker_shift_conflict_posture(shell_root)
    queueable_requests = _queueable_request_rows(shell_root)
    lane_ids = sorted(
        {
            str(row.get("lane_id") or "").strip()
            for row in queueable_requests
            if str(row.get("lane_id") or "").strip()
        }
    )
    missing_lane_request_count = sum(1 for row in queueable_requests if not str(row.get("lane_id") or "").strip())
    request_results: list[dict[str, Any]] = []
    for row in queueable_requests:
        lane_id = str(row.get("lane_id") or "").strip()
        domain_id = str(row.get("domain_id") or "").strip()
        role_id = str(row.get("role_id") or "").strip()
        worker_identity = _worker_identity_for_row(row)
        domain_alignment = _domain_alignment_for_row(row)
        capsule_preflight_blockers = list(row.get("capsule_identity_preflight_blockers") or [])
        if not lane_id or not domain_id:
            capsule_request_binding = _capsule_request_binding_for_row(shell_root, row, None)
            capsule_binding_blockers = list(capsule_request_binding.get("blockers") or [])
            capsule_blockers = _combine_capsule_blockers(capsule_preflight_blockers, capsule_binding_blockers)
            blockers_for_row = [
                code
                for code, missing in (
                    ("queueable_request_missing_lane_id", not lane_id),
                    ("queueable_request_missing_domain_id", not domain_id),
                )
                if missing
            ]
            blockers_for_row = list(dict.fromkeys(blockers_for_row + capsule_blockers))
            request_results.append(
                {
                    **row,
                    "ready": False,
                    "active_context_ready": False,
                    "active_context_check_status": "not_checked_missing_request_metadata",
                    "blockers": blockers_for_row,
                    "next_action": "repair_queue_request_lane_and_domain_metadata",
                    "context_active_resolver": None,
                    "capsule_identity_request_binding": capsule_request_binding,
                    "capsule_identity_binding_blockers": capsule_binding_blockers,
                    "capsule_identity_blockers": capsule_blockers,
                    "active_root_proof": active_root_proof,
                    "worker_identity": worker_identity,
                    "domain_alignment": domain_alignment,
                    "worker_return_status": _blocker_preserving_return_status(row, ready=False, blockers=blockers_for_row),
                }
            )
            continue
        if str(row.get("status") or "").strip() == CONTEXT_GATE_BLOCKED_STATUS:
            context_gate = row.get("context_gate") if isinstance(row.get("context_gate"), Mapping) else {}
            resolver = context_gate.get("context_active_resolver") if isinstance(context_gate.get("context_active_resolver"), Mapping) else {}
            preserved_blockers = ["request_previously_blocked_by_context_gate"]
            finding = str(context_gate.get("finding") or "").strip()
            if finding:
                preserved_blockers.append(finding)
            preserved_blockers.extend(str(code) for code in list(resolver.get("blockers") or []) if str(code).strip())
            capsule_request_binding = _capsule_request_binding_for_row(shell_root, row, resolver)
            capsule_binding_blockers = list(capsule_request_binding.get("blockers") or [])
            capsule_blockers = _combine_capsule_blockers(capsule_preflight_blockers, capsule_binding_blockers)
            blockers_for_row = sorted(set(preserved_blockers + capsule_blockers))
            request_results.append(
                {
                    **row,
                    "ready": False,
                    "active_context_ready": False,
                    "active_context_check_status": "preserved_context_gate_blocker",
                    "domain_id": domain_id,
                    "role_id": role_id or None,
                    "blockers": blockers_for_row,
                    "next_action": "repair_context_gate_blocker_before_worker_start",
                    "context_active_resolver": resolver or None,
                    "capsule_identity_request_binding": capsule_request_binding,
                    "capsule_identity_binding_blockers": capsule_binding_blockers,
                    "capsule_identity_blockers": capsule_blockers,
                    "active_root_proof": active_root_proof,
                    "worker_identity": worker_identity,
                    "domain_alignment": domain_alignment,
                    "worker_return_status": _blocker_preserving_return_status(row, ready=False, blockers=blockers_for_row),
                }
            )
            continue
        resolver = resolve_domain_active_context(
            shell_root,
            domain_id=domain_id,
            role_id=role_id or None,
            lane=lane_id,
            max_age_seconds=max_age_seconds,
        )
        resolver_blockers = list(resolver.get("blockers") or [])
        capsule_request_binding = _capsule_request_binding_for_row(shell_root, row, resolver)
        capsule_binding_blockers = list(capsule_request_binding.get("blockers") or [])
        capsule_blockers = _combine_capsule_blockers(capsule_preflight_blockers, capsule_binding_blockers)
        blockers_for_row = list(dict.fromkeys(resolver_blockers + capsule_blockers))
        row_ready = bool(resolver.get("ok")) and not capsule_blockers
        next_action = resolver.get("next_action")
        if capsule_blockers and resolver.get("ok"):
            next_action = "repair_working_capsule_identity_before_worker_start"
        request_results.append(
            {
                **row,
                "lane_id": lane_id,
                "ready": row_ready,
                "active_context_ready": bool(resolver.get("ok")),
                "active_context_check_status": "resolver_checked",
                "domain_id": domain_id,
                "role_id": role_id or None,
                "role_tier": str(row.get("role_tier") or "").strip() or None,
                "callsign": str(row.get("callsign") or "").strip() or None,
                "resolver_id": resolver.get("resolver_id"),
                "selected_mount_id": (resolver.get("selected") or {}).get("mount_id")
                if isinstance(resolver.get("selected"), Mapping)
                else None,
                "blockers": blockers_for_row,
                "next_action": next_action,
                "context_active_resolver": resolver,
                "capsule_identity_request_binding": capsule_request_binding,
                "capsule_identity_binding_blockers": capsule_binding_blockers,
                "capsule_identity_blockers": capsule_blockers,
                "active_root_proof": active_root_proof,
                "worker_identity": worker_identity,
                "domain_alignment": domain_alignment,
                "worker_return_status": _blocker_preserving_return_status(
                    row,
                    ready=row_ready,
                    blockers=blockers_for_row,
                ),
            }
        )
    lane_results: list[dict[str, Any]] = []
    for lane_id in lane_ids:
        rows = [row for row in request_results if str(row.get("lane_id") or "").strip() == lane_id]
        blocked_rows = [row for row in rows if not row.get("ready")]
        lane_results.append(
            {
                "lane_id": lane_id,
                "ready": bool(rows and not blocked_rows),
                "request_count": len(rows),
                "ready_request_count": len(rows) - len(blocked_rows),
                "blocked_request_count": len(blocked_rows),
                "blockers": sorted({code for row in blocked_rows for code in list(row.get("blockers") or [])}),
                "requests": rows,
            }
        )
    queueable_start_rows = [row for row in request_results if row.get("queueable_for_start")]
    shared_capsule_queue_rows = [
        row
        for row in queueable_start_rows
        if not str(row.get("role_id") or "").strip() or not str(row.get("selected_mount_id") or "").strip()
    ]
    queueable_shared_capsule_hazard = len(queueable_start_rows) > 1 and bool(shared_capsule_queue_rows)
    if queueable_shared_capsule_hazard:
        posture = dict(worker_shift_conflict_posture)
        posture_blockers = list(posture.get("blockers") or [])
        if "shared_capsule_concurrency_hazard_live" not in posture_blockers:
            posture_blockers.append("shared_capsule_concurrency_hazard_live")
        posture["blockers"] = posture_blockers
        posture["risk_level"] = "high"
        posture["queueable_role_or_mount_missing_count"] = len(shared_capsule_queue_rows)
        worker_shift_conflict_posture = posture
    blocked_lanes = [row for row in lane_results if not row.get("ready")]
    context_blocker_rows = [
        row
        for row in request_results
        if row.get("active_context_check_status") in {"preserved_context_gate_blocker", "resolver_checked"}
        and not row.get("active_context_ready")
    ]
    capsule_identity_blocker_rows = [row for row in request_results if list(row.get("capsule_identity_blockers") or [])]
    capsule_identity_preflight_blocker_rows = [
        row for row in request_results if list(row.get("capsule_identity_preflight_blockers") or [])
    ]
    capsule_identity_binding_blocker_rows = [
        row for row in request_results if list(row.get("capsule_identity_binding_blockers") or [])
    ]
    blockers: list[str] = []
    if missing_lane_request_count:
        blockers.append("queueable_requests_missing_lane_id")
    if any(not str(row.get("domain_id") or "").strip() for row in queueable_requests):
        blockers.append("queueable_requests_missing_domain_id")
    if context_blocker_rows:
        blockers.append("queueable_lanes_missing_fresh_active_context")
    if worker_shift_conflict_posture.get("risk_level") not in {None, "", "none"}:
        blockers.append("worker_shift_conflict_posture_not_clear")
    if capsule_identity_preflight_blocker_rows:
        blockers.append("working_capsule_identity_preflight_blocked")
    if capsule_identity_binding_blocker_rows:
        blockers.append("working_capsule_identity_request_binding_blocked")
    if queueable_shared_capsule_hazard:
        blockers.append("shared_capsule_concurrency_hazard_live")
    if not queueable_requests:
        next_action = "no_queueable_worker_start_requests"
    elif (
        capsule_identity_blocker_rows
        and not context_blocker_rows
        and not missing_lane_request_count
        and all(str(row.get("domain_id") or "").strip() for row in queueable_requests)
    ):
        next_action = "repair_working_capsule_identity_before_worker_start"
    elif blockers:
        next_action = "hydrate_or_reissue_lane_active_context_packages"
    else:
        next_action = "worker_start_context_ready"
    ready = bool(queueable_requests and not blockers)
    return {
        "schema_id": SCHEMA_ID,
        "ok": ready,
        "ready_to_start_workers": ready,
        "queueable_requests": queueable_requests,
        "request_results": request_results,
        "lane_results": lane_results,
        "blockers": blockers,
        "next_action": next_action,
        "summary": {
            "queueable_request_count": len(queueable_requests),
            "ready_queueable_request_count": sum(1 for row in request_results if row.get("ready")),
            "resolver_ready_request_count": sum(1 for row in request_results if row.get("active_context_ready")),
            "queueable_for_start_request_count": sum(1 for row in queueable_requests if row.get("queueable_for_start")),
            "blocked_context_gate_request_count": sum(
                1 for row in queueable_requests if str(row.get("status") or "").strip() == CONTEXT_GATE_BLOCKED_STATUS
            ),
            "queueable_lane_count": len(lane_ids),
            "ready_lane_count": len(lane_results) - len(blocked_lanes),
            "blocked_lane_count": len(blocked_lanes),
            "missing_lane_request_count": missing_lane_request_count,
            "ready_to_start_workers": ready,
            "worker_shift_conflict_risk_level": worker_shift_conflict_posture.get("risk_level"),
            "worker_shift_conflict_blockers": list(worker_shift_conflict_posture.get("blockers") or []),
            "shared_capsule_concurrency_hazard": queueable_shared_capsule_hazard,
            "capsule_identity_blocked_request_count": len(capsule_identity_blocker_rows),
            "capsule_identity_preflight_blocked_request_count": len(capsule_identity_preflight_blocker_rows),
            "capsule_identity_binding_blocked_request_count": len(capsule_identity_binding_blocker_rows),
            "capsule_identity_repair_required": bool(capsule_identity_blocker_rows),
            "capsule_identity_blockers": sorted(
                {
                    code
                    for row in capsule_identity_blocker_rows
                    for code in list(row.get("capsule_identity_blockers") or [])
                }
            ),
            "capsule_identity_binding_blockers": sorted(
                {
                    code
                    for row in capsule_identity_binding_blocker_rows
                    for code in list(row.get("capsule_identity_binding_blockers") or [])
                }
            ),
            "next_action": next_action,
        },
        "authority": _authority(),
        "active_root_proof": active_root_proof,
        "worker_shift_conflict_posture": worker_shift_conflict_posture,
    }


def _row_age_seconds(row: Mapping[str, Any], now: datetime) -> int | None:
    timestamp = _parse_datetime(row.get("updated_at")) or _parse_datetime(row.get("created_at"))
    if timestamp is None:
        return None
    return max(0, int((now - timestamp).total_seconds()))


def _is_domain_weaver_spawn_dispatch_row(row: Mapping[str, Any]) -> bool:
    return (
        str(row.get("work_class") or "").strip() == "domain_weaver_spawn_dispatch"
        or str(row.get("request_kind") or "").strip() == "domain_weaver_spawn_dispatch"
    )


def _compact_hygiene_row(row: Mapping[str, Any], *, now: datetime, stale_after_seconds: int) -> dict[str, Any]:
    blockers = [str(code) for code in list(row.get("blockers") or []) if str(code).strip()]
    age_seconds = _row_age_seconds(row, now)
    stale = age_seconds is not None and age_seconds > stale_after_seconds
    return {
        "request_path": row.get("request_path"),
        "request_id": row.get("request_id"),
        "status": row.get("status"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "age_seconds": age_seconds,
        "stale_for_hygiene": stale,
        "lane_id": row.get("lane_id"),
        "domain_id": row.get("domain_id"),
        "role_id": row.get("role_id"),
        "role_tier": row.get("role_tier"),
        "callsign": row.get("callsign"),
        "work_class": row.get("work_class"),
        "request_kind": row.get("request_kind"),
        "queueable_for_start": bool(row.get("queueable_for_start")),
        "ready": bool(row.get("ready")),
        "active_context_ready": bool(row.get("active_context_ready")),
        "selected_mount_id": row.get("selected_mount_id") or row.get("requested_selected_mount_id"),
        "selected_mount_path": row.get("selected_mount_path") or row.get("requested_selected_mount_path"),
        "latest_return_packet_path": row.get("latest_return_packet_path"),
        "blockers": blockers,
        "next_action": row.get("next_action"),
        "domain_weaver_spawn_dispatch": _is_domain_weaver_spawn_dispatch_row(row),
        "worker_return_is_carrier_intake_only": True,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def _limited_rows(rows: list[Mapping[str, Any]], *, now: datetime, stale_after_seconds: int, limit: int) -> list[dict[str, Any]]:
    return [
        _compact_hygiene_row(row, now=now, stale_after_seconds=stale_after_seconds)
        for row in rows[: max(0, int(limit))]
    ]


def build_domain_weaver_worker_start_backlog_hygiene(
    root: str | Path | None,
    *,
    max_age_seconds: int = DEFAULT_MAX_CONTEXT_AGE_SECONDS,
    stale_after_seconds: int = 12 * 60 * 60,
    example_limit: int = DEFAULT_BACKLOG_EXAMPLE_LIMIT,
) -> dict[str, Any]:
    """Classify queue backlog causes without starting or mutating workers."""

    shell_root = Path(root or ".").expanduser().resolve()
    now = datetime.now(timezone.utc)
    readiness = build_domain_weaver_worker_start_readiness(
        shell_root,
        max_age_seconds=max_age_seconds,
    )
    request_results = [
        row
        for row in list(readiness.get("request_results") or [])
        if isinstance(row, Mapping)
    ]
    queueable_for_start_rows = [row for row in request_results if row.get("queueable_for_start")]
    blocked_rows = [row for row in request_results if not row.get("ready")]
    exact_spawn_dispatch_rows = [
        row
        for row in queueable_for_start_rows
        if _is_domain_weaver_spawn_dispatch_row(row)
    ]
    exact_spawn_dispatch_ready_rows = [
        row
        for row in exact_spawn_dispatch_rows
        if row.get("ready")
    ]
    exact_spawn_dispatch_blocked_rows = [
        row
        for row in exact_spawn_dispatch_rows
        if not row.get("ready")
    ]
    missing_domain_rows = [
        row for row in request_results if not str(row.get("domain_id") or "").strip()
    ]
    missing_lane_rows = [
        row for row in request_results if not str(row.get("lane_id") or "").strip()
    ]
    context_gate_rows = [
        row
        for row in request_results
        if str(row.get("status") or "").strip() == CONTEXT_GATE_BLOCKED_STATUS
    ]
    context_blocked_rows = [
        row
        for row in request_results
        if not row.get("active_context_ready")
        and str(row.get("active_context_check_status") or "") in {"preserved_context_gate_blocker", "resolver_checked"}
    ]
    capsule_blocked_rows = [
        row for row in request_results if list(row.get("capsule_identity_blockers") or [])
    ]
    shared_capsule_hazard_rows = [
        row
        for row in queueable_for_start_rows
        if not str(row.get("role_id") or "").strip()
        or not str(row.get("selected_mount_id") or row.get("requested_selected_mount_id") or "").strip()
    ]
    historical_rows = [
        row
        for row in request_results
        if (_row_age_seconds(row, now) or 0) > stale_after_seconds
    ]
    non_spawn_dispatch_rows = [
        row
        for row in queueable_for_start_rows
        if not _is_domain_weaver_spawn_dispatch_row(row)
    ]
    dirty_general_rows = [
        row
        for row in blocked_rows
        if row not in exact_spawn_dispatch_ready_rows
    ]
    lane_ids = sorted({str(row.get("lane_id") or "").strip() for row in request_results if str(row.get("lane_id") or "").strip()})
    dirty_lanes = sorted({str(row.get("lane_id") or "").strip() for row in blocked_rows if str(row.get("lane_id") or "").strip()})
    blocker_counts: dict[str, int] = {}
    for row in blocked_rows:
        for blocker in list(row.get("blockers") or []):
            key = str(blocker or "").strip()
            if key:
                blocker_counts[key] = blocker_counts.get(key, 0) + 1
    blocker_rank = [
        {"blocker": blocker, "request_count": count}
        for blocker, count in sorted(blocker_counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    worker_shift = readiness.get("worker_shift_conflict_posture")
    if not isinstance(worker_shift, Mapping):
        worker_shift = {}
    readiness_summary = readiness.get("summary") if isinstance(readiness.get("summary"), Mapping) else {}
    exact_start_possible = bool(exact_spawn_dispatch_ready_rows)
    global_dirty = bool(readiness.get("blockers"))
    candidate_exact_request_paths = [
        str(row.get("request_path") or "")
        for row in exact_spawn_dispatch_ready_rows
        if str(row.get("request_path") or "").strip()
    ]
    next_packets: list[dict[str, Any]] = []
    if dirty_general_rows:
        next_packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-WORKER-START-READINESS-QUEUE-HYGIENE-SETTLEMENT-V0_1",
                "purpose": "retire, repair, or reissue dirty global queue rows without broad queue processing",
                "authority": "candidate_only_until_branch_gateway_write_gate",
            }
        )
    if exact_start_possible:
        next_packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-EXACT-SPAWN-DISPATCH-START-GATE-V0_1",
                "purpose": "start only explicit ready request paths after operator or route-gated approval",
                "candidate_exact_request_paths": candidate_exact_request_paths,
                "authority": "exact_request_path_only_no_general_queue_processing",
            }
        )
    if context_blocked_rows:
        next_packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-ACTIVE-CONTEXT-GATED-REFRESH-OR-REISSUE-V0_2",
                "purpose": "repair stale or missing active context for blocked lanes",
                "authority": "preflight_first_then_lease_gated_write",
            }
        )
    if capsule_blocked_rows or shared_capsule_hazard_rows:
        next_packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-WORKING-CAPSULE-IDENTITY-REISSUE-V0_1",
                "purpose": "bind queued workers to unique folder-local mount capsules",
                "authority": "candidate_only_no_codex_solo_as_working_capsule",
            }
        )
    return {
        "schema_id": BACKLOG_HYGIENE_SCHEMA_ID,
        "status": "worker_start_backlog_hygiene_built",
        "created_at": _utc_now(),
        "active_root": str(shell_root),
        "hygiene_ok": not global_dirty,
        "global_worker_start_readiness_ok": bool(readiness.get("ok")),
        "global_worker_start_readiness_blockers": list(readiness.get("blockers") or []),
        "exact_start_possible": exact_start_possible,
        "candidate_exact_request_paths": candidate_exact_request_paths,
        "exact_request_path_required": True,
        "general_queue_processing_allowed": False,
        "codex_queue_run_started": False,
        "actual_spawn_performed": False,
        "direct_nested_spawn": False,
        "raw_external_codex_exec": False,
        "accepted_state_claimed": False,
        "production_or_live_authority": False,
        "secrets_authority": False,
        "summary": {
            "readiness_request_count": len(request_results),
            "queueable_for_start_request_count": len(queueable_for_start_rows),
            "ready_request_count": sum(1 for row in request_results if row.get("ready")),
            "blocked_request_count": len(blocked_rows),
            "blocked_context_gate_request_count": len(context_gate_rows),
            "context_blocked_request_count": len(context_blocked_rows),
            "capsule_identity_blocked_request_count": len(capsule_blocked_rows),
            "shared_capsule_hazard_request_count": len(shared_capsule_hazard_rows),
            "missing_domain_request_count": len(missing_domain_rows),
            "missing_lane_request_count": len(missing_lane_rows),
            "exact_spawn_dispatch_request_count": len(exact_spawn_dispatch_rows),
            "exact_spawn_dispatch_ready_count": len(exact_spawn_dispatch_ready_rows),
            "exact_spawn_dispatch_blocked_count": len(exact_spawn_dispatch_blocked_rows),
            "non_spawn_dispatch_queueable_count": len(non_spawn_dispatch_rows),
            "historical_or_stale_request_count": len(historical_rows),
            "lane_count": len(lane_ids),
            "dirty_lane_count": len(dirty_lanes),
            "worker_shift_conflict_risk_level": worker_shift.get("risk_level"),
            "shared_capsule_concurrency_hazard": bool(readiness_summary.get("shared_capsule_concurrency_hazard")),
            "next_action": (
                "start_exact_request_paths_only_after_gate_and_repair_global_backlog"
                if exact_start_possible and global_dirty
                else "repair_global_worker_start_backlog"
                if global_dirty
                else "worker_start_backlog_hygiene_clean"
            ),
        },
        "lanes": {
            "all_lane_ids": lane_ids,
            "dirty_lane_ids": dirty_lanes,
        },
        "blocker_rank": blocker_rank,
        "groups": {
            "exact_spawn_dispatch_ready": _limited_rows(
                exact_spawn_dispatch_ready_rows,
                now=now,
                stale_after_seconds=stale_after_seconds,
                limit=example_limit,
            ),
            "exact_spawn_dispatch_blocked": _limited_rows(
                exact_spawn_dispatch_blocked_rows,
                now=now,
                stale_after_seconds=stale_after_seconds,
                limit=example_limit,
            ),
            "missing_domain": _limited_rows(
                missing_domain_rows,
                now=now,
                stale_after_seconds=stale_after_seconds,
                limit=example_limit,
            ),
            "context_gate_blocked": _limited_rows(
                context_gate_rows,
                now=now,
                stale_after_seconds=stale_after_seconds,
                limit=example_limit,
            ),
            "capsule_identity_blocked": _limited_rows(
                capsule_blocked_rows,
                now=now,
                stale_after_seconds=stale_after_seconds,
                limit=example_limit,
            ),
            "shared_capsule_hazard": _limited_rows(
                shared_capsule_hazard_rows,
                now=now,
                stale_after_seconds=stale_after_seconds,
                limit=example_limit,
            ),
            "historical_or_stale": _limited_rows(
                historical_rows,
                now=now,
                stale_after_seconds=stale_after_seconds,
                limit=example_limit,
            ),
            "non_spawn_dispatch_queueable": _limited_rows(
                non_spawn_dispatch_rows,
                now=now,
                stale_after_seconds=stale_after_seconds,
                limit=example_limit,
            ),
        },
        "next_packets": next_packets,
        "worker_start_readiness_summary": readiness_summary,
        "active_root_proof": readiness.get("active_root_proof"),
        "authority": _authority(),
        "non_claims": [
            "does not start workers",
            "does not process the general queue",
            "does not retire or mutate queued rows",
            "does not claim accepted state",
            "worker returns remain carrier intake only",
        ],
    }
