"""Worker Shift and Presence helpers for ION.

This candidate helper keeps lightweight worker presence and work leases in
durable local JSON receipts. It complements carrier mount, executor lifecycle,
carrier messaging, scheduler, and allocator surfaces; it does not replace them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from kernel.ion_path_authority import WorkspaceAuthority, decide_path_authority, load_workspace_authority


SCHEMA_ID = "ion.worker_shift_presence.v0_1"
BOARD_SCHEMA_ID = "ion.worker_shift_board.v0_1"
SIGNON_RECEIPT_SCHEMA_ID = "ion.worker_shift_signon_receipt.v0_1"
SIGNOFF_RECEIPT_SCHEMA_ID = "ion.worker_shift_signoff_receipt.v0_1"
HEARTBEAT_RECEIPT_SCHEMA_ID = "ion.worker_shift_heartbeat_receipt.v0_1"
LEASE_RECEIPT_SCHEMA_ID = "ion.worker_shift_work_lease_receipt.v0_1"
UNBOUND_LEASE_SETTLEMENT_SCHEMA_ID = "ion.worker_shift_live_unbound_lease_settlement.v0_1"
ORPHAN_LEASE_RECONCILIATION_SCHEMA_ID = "ion.worker_shift_orphan_exclusive_write_reconciliation.v0_1"
HANDOFF_REQUEST_RECEIPT_SCHEMA_ID = "ion.worker_shift.handoff_request_receipt.v0_2"
HANDOFF_REQUEST_RESULT_SCHEMA_ID = "ion.worker_shift.request_handoff_result.v0_2"
OPERATOR_OVERRIDE_REQUEST_RECEIPT_SCHEMA_ID = "ion.worker_shift.operator_override_request_receipt.v0_2"
OPERATOR_OVERRIDE_REQUEST_RESULT_SCHEMA_ID = "ion.worker_shift.request_operator_override_result.v0_2"
AI_MOVEMENT_ROOT_ENVELOPE_SCHEMA_ID = "ion.ai_movement_root_envelope.v1"
AI_MOVEMENT_GATE_DECISION_SCHEMA_ID = "ion.ai_movement_gate_decision.v1"
AI_MOVEMENT_WORKER_SHIFT_FRAGMENT_SCHEMA_ID = "ion.ai_movement_worker_shift_receipt_fragment.v1"

WORKER_SHIFT_ROOT = Path("ION/05_context/current/worker_shift")
ACTIVE_BOARD_PATH = WORKER_SHIFT_ROOT / "ACTIVE_WORKER_SHIFT_BOARD.json"

AUTHORITY_FALSE: dict[str, bool] = {
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
}

LEASE_MODES: tuple[str, ...] = ("read", "write", "exclusive_write", "artifact")
LEGACY_LEASE_MODE_ALIASES: dict[str, str] = {
    "read_interest": "read",
    "review_only": "read",
    "write_intent": "write",
    "blocked": "write",
}
LEASE_TYPES: tuple[str, ...] = LEASE_MODES + tuple(LEGACY_LEASE_MODE_ALIASES)
REASON_WORKSPACE_EXPORT_REQUIRES_ARTIFACT_LEASE = "WORKSPACE_EXPORT_REQUIRES_ARTIFACT_LEASE"
REASON_WORKER_ID_ACTIVE_SIGNON_MISMATCH = "WORKER_ID_ACTIVE_SIGNON_MISMATCH"
REASON_AI_MOVEMENT_GATE_BLOCKED = "AI_MOVEMENT_GATE_BLOCKED"
WRITE_INTENT_CONFIRMATION = "ION_WRITE_INTENT_CONFIRMED"
WRITE_INTENT_LEASE_CLASS = "write_intent_lease"
WRITE_OPERATION_LEASE_MODES: tuple[str, ...] = ("write", "exclusive_write")
WRITE_INTENT_ROOT_SCOPES: tuple[str, ...] = ("active_root", "active_repo")
PREVIEW_ONLY_ROUTE_TOKENS: tuple[str, ...] = ("parallel_plan_preview", "preview_only", "read_only", "dry_run")
IDENTITY_BOUND_TRUE_NAME = "BOUND_TRUE_NAME"
IDENTITY_DECLARED_WORKER_ID = "DECLARED_WORKER_ID"
IDENTITY_UNBOUND_WORKER_ID = "UNBOUND_WORKER_ID"
HANDOFF_CONFIRMATION_MARKER = "ION_HANDOFF_REQUEST_CONFIRMED"
OPERATOR_OVERRIDE_PROOF_MARKER = "ION_OPERATOR_OVERRIDE_REQUESTED"
BLOCKED_IDENTITY_STATUS_TOKENS = {
    "mismatch",
    "unbound",
    "unbound_no_active_signon",
    "unbound_worker_id",
    "generated_fallback",
    "blocked_worker_id_mismatch",
}

LIFECYCLE_STATE_MAP: dict[str, str] = {
    "SIGNED_ON": "ACTIVE",
    "ACTIVE": "ACTIVE",
    "HEARTBEAT": "ACTIVE",
    "STALE": "SUSPENDED",
    "EXPIRED": "SUSPENDED",
    "RETURNED": "RETURNED",
    "RELEASED": "RELEASED",
    "FAILED": "RELEASED",
    "SUSPENDED": "SUSPENDED",
}

_CARRIER_FAMILY = {
    "chatgpt_browser": "BrowserGPT",
    "browser_gpt": "BrowserGPT",
    "codex_cli": "Codex",
    "codex": "Codex",
    "queued_codex": "Codex",
    "capsule_agent": "Capsule",
    "branch_agent": "Branch",
    "swarm_worker": "Swarm",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stamp(now: str | None = None) -> str:
    value = now or _now()
    return value.replace("-", "").replace(":", "").replace("+00:00", "Z")


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        text = str(value)
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _slug(value: Any, *, fallback: str = "item", limit: int = 96) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "").strip()).strip("._-")
    return (slug or fallback)[:limit]


def _hash_short(value: Any) -> str:
    return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()[:12]


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _compact_ai_movement_gate_decision(decision: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(decision, Mapping):
        return None
    blockers = [item for item in decision.get("blockers", []) if isinstance(item, Mapping)]
    warnings = [item for item in decision.get("warnings", []) if isinstance(item, Mapping)]
    return {
        "schema_id": str(decision.get("schema_id") or AI_MOVEMENT_GATE_DECISION_SCHEMA_ID),
        "accepted": bool(decision.get("accepted")) if decision.get("accepted") is not None else None,
        "verdict": decision.get("verdict"),
        "movement_class": decision.get("movement_class"),
        "target_root_id": decision.get("target_root_id") or decision.get("root_id"),
        "target_root_class": decision.get("target_root_class"),
        "target_root_relation": decision.get("target_root_relation"),
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "blocker_codes": sorted({str(item.get("code")) for item in blockers if item.get("code")}),
        "warning_codes": sorted({str(item.get("code")) for item in warnings if item.get("code")}),
        "settlement_target": decision.get("settlement_target"),
    }


def _ai_movement_gate_blocks(gate_summary: Mapping[str, Any] | None) -> bool:
    if not isinstance(gate_summary, Mapping):
        return False
    if gate_summary.get("accepted") is False:
        return True
    return str(gate_summary.get("verdict") or "").upper() == "BLOCKED"


def _ai_movement_receipt_payload(
    *,
    envelope: Mapping[str, Any] | None = None,
    gate_decision: Mapping[str, Any] | None = None,
) -> dict[str, Any] | None:
    root_envelope = _json_safe(envelope) if isinstance(envelope, Mapping) else None
    gate_summary = _compact_ai_movement_gate_decision(gate_decision)
    if root_envelope is None and gate_summary is None:
        return None
    envelope_schema_id = AI_MOVEMENT_ROOT_ENVELOPE_SCHEMA_ID
    if isinstance(root_envelope, Mapping):
        nested = root_envelope.get("ai_movement_root_envelope")
        if isinstance(nested, Mapping):
            envelope_schema_id = str(nested.get("schema_id") or envelope_schema_id)
        else:
            envelope_schema_id = str(root_envelope.get("schema_id") or envelope_schema_id)
    return {
        "schema_id": AI_MOVEMENT_WORKER_SHIFT_FRAGMENT_SCHEMA_ID,
        "root_envelope_schema_id": envelope_schema_id,
        "gate_decision_schema_id": (gate_summary or {}).get("schema_id"),
        "envelope": root_envelope,
        "gate_decision": gate_summary,
        "gate_required": True,
        "receipt_integration_only": True,
        "runner_integration_performed": False,
        "authority": dict(AUTHORITY_FALSE),
    }


def _resolve_root(root: str | Path | None = None) -> Path:
    return Path(root or ".").expanduser().resolve(strict=False)


def _rel(path: Path | str, root: Path) -> str:
    candidate = Path(path)
    try:
        return candidate.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return candidate.as_posix()


def _runtime_path(root: Path, relative: Path) -> Path:
    return root / relative


def _ensure_runtime_dirs(root: Path) -> None:
    for rel in (
        WORKER_SHIFT_ROOT,
        WORKER_SHIFT_ROOT / "signons",
        WORKER_SHIFT_ROOT / "signoffs",
        WORKER_SHIFT_ROOT / "heartbeats",
        WORKER_SHIFT_ROOT / "leases",
        WORKER_SHIFT_ROOT / "messages",
        WORKER_SHIFT_ROOT / "stale",
    ):
        _runtime_path(root, rel).mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _read_json(path: Path) -> Any | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _default_board(now: str | None = None) -> dict[str, Any]:
    timestamp = now or _now()
    return {
        "schema_id": BOARD_SCHEMA_ID,
        "updated_at": timestamp,
        "authority": dict(AUTHORITY_FALSE),
        "active_shifts": [],
        "active_leases": [],
        "stale_workers": [],
        "recent_signoffs": [],
        "recent_receipts": [],
    }


def _coerce_board(board: Mapping[str, Any] | None, now: str | None = None) -> dict[str, Any]:
    result = _default_board(now=now)
    if isinstance(board, Mapping):
        result.update({key: value for key, value in board.items() if key != "authority"})
        authority = dict(AUTHORITY_FALSE)
        if isinstance(board.get("authority"), Mapping):
            authority.update({key: bool(value) for key, value in board["authority"].items()})
        result["authority"] = authority
    for key in ("active_shifts", "active_leases", "stale_workers", "recent_signoffs", "recent_receipts"):
        if not isinstance(result.get(key), list):
            result[key] = []
    result["schema_id"] = BOARD_SCHEMA_ID
    return result


def load_shift_board(root: str | Path | None = None) -> dict[str, Any]:
    """Load the active worker shift board or return an empty candidate board."""

    shell_root = _resolve_root(root)
    return _coerce_board(_read_json(_runtime_path(shell_root, ACTIVE_BOARD_PATH)))


def write_shift_board(board: Mapping[str, Any], root: str | Path | None = None) -> dict[str, Any]:
    """Persist the active worker shift board."""

    shell_root = _resolve_root(root)
    _ensure_runtime_dirs(shell_root)
    payload = _coerce_board(board)
    payload["updated_at"] = _now()
    _write_json(_runtime_path(shell_root, ACTIVE_BOARD_PATH), payload)
    return payload


def _next_ordinal(board: Mapping[str, Any], carrier_type: str) -> int:
    family = _CARRIER_FAMILY.get(carrier_type.lower(), _slug(carrier_type, fallback="Worker"))
    highest = 0
    for shift in board.get("active_shifts", []):
        callsign = str(shift.get("identity", {}).get("display_callsign", ""))
        match = re.match(rf"{re.escape(family)}-(\d+)", callsign)
        if match:
            highest = max(highest, int(match.group(1)))
    return highest + 1


def generate_worker_id(
    *,
    carrier_type: str,
    active_root: str | Path | None = None,
    carrier_instance_id: str | None = None,
    model: str | None = None,
    role_hint: str | None = None,
    domain_hint: str | None = None,
    board: Mapping[str, Any] | None = None,
    now: str | None = None,
    ordinal: int | None = None,
) -> dict[str, Any]:
    """Generate a runtime worker identity for one active worker instance."""

    timestamp = now or _now()
    root_text = str(Path(active_root).expanduser().resolve(strict=False)) if active_root else ""
    board_payload = _coerce_board(board, now=timestamp)
    carrier = _slug(carrier_type, fallback="worker").lower()
    number = ordinal or _next_ordinal(board_payload, carrier)
    family = _CARRIER_FAMILY.get(carrier, _slug(carrier_type, fallback="Worker"))
    workspace = _slug(Path(root_text).name if root_text else "workspace", fallback="workspace")
    date = (timestamp[:10] if len(timestamp) >= 10 else "unknown").replace("-", "")
    role = _slug(role_hint, fallback="Worker")
    domain = _slug(domain_hint, fallback="General")
    return {
        "worker_id": f"{carrier}:{workspace}:{date}:{number:03d}",
        "display_callsign": f"{family}-{number:03d} / {role} / {domain}",
        "declared_true_name": None,
        "identity_binding_status": IDENTITY_UNBOUND_WORKER_ID,
        "worker_id_source": "generated_fallback",
        "unbound_worker_id": True,
        "carrier_type": carrier,
        "carrier_instance_id": carrier_instance_id,
        "model": model,
        "role_hint": role_hint,
        "domain_hint": domain_hint,
        "active_root": root_text or None,
        "created_at": timestamp,
        "authority": dict(AUTHORITY_FALSE),
    }


def _parse_true_name_or_none(worker_id: str) -> dict[str, Any] | None:
    try:
        from .ion_true_name_binding import parse_true_name

        return parse_true_name(worker_id)
    except Exception:
        return None


def _declared_identity_fields(worker_id: str, *, generated_fallback: bool = False) -> dict[str, Any]:
    if generated_fallback:
        return {
            "declared_true_name": None,
            "identity_binding_status": IDENTITY_UNBOUND_WORKER_ID,
            "worker_id_source": "generated_fallback",
            "unbound_worker_id": True,
            "parsed_true_name": None,
        }
    parsed = _parse_true_name_or_none(worker_id)
    if parsed:
        return {
            "declared_true_name": worker_id,
            "identity_binding_status": IDENTITY_BOUND_TRUE_NAME,
            "worker_id_source": "declared_true_name",
            "unbound_worker_id": False,
            "parsed_true_name": parsed,
        }
    return {
        "declared_true_name": worker_id,
        "identity_binding_status": IDENTITY_DECLARED_WORKER_ID,
        "worker_id_source": "declared_worker_id",
        "unbound_worker_id": False,
        "parsed_true_name": None,
    }


def _normalize_worker_identity(identity: Mapping[str, Any], *, generated_fallback: bool = False) -> dict[str, Any]:
    value = dict(identity)
    worker_id = str(value.get("worker_id") or "").strip()
    if not worker_id:
        raise ValueError("worker identity must include worker_id")
    fields = _declared_identity_fields(worker_id, generated_fallback=generated_fallback)
    for key, field_value in fields.items():
        value.setdefault(key, field_value)
    return value


def _identity_status_token(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")


def _lease_identity_binding_blocked(lease: Mapping[str, Any]) -> bool:
    status_tokens = {
        _identity_status_token(lease.get("identity_binding_status")),
        _identity_status_token(lease.get("worker_id_source")),
    }
    authorization = lease.get("worker_id_authorization")
    if isinstance(authorization, Mapping):
        status_tokens.add(_identity_status_token(authorization.get("identity_binding_status")))
        status_tokens.add(_identity_status_token(authorization.get("worker_id_source")))
    identity = lease.get("identity")
    if isinstance(identity, Mapping):
        status_tokens.add(_identity_status_token(identity.get("identity_binding_status")))
        status_tokens.add(_identity_status_token(identity.get("worker_id_source")))
        if identity.get("unbound_worker_id") is True:
            return True
    if lease.get("unbound_worker_id") is True:
        return True
    return bool(status_tokens.intersection(BLOCKED_IDENTITY_STATUS_TOKENS))


def _active_shift_for_worker_id(board: Mapping[str, Any], worker_id: str) -> Mapping[str, Any] | None:
    for shift in board.get("active_shifts", []):
        if not isinstance(shift, Mapping):
            continue
        if shift.get("worker_id") != worker_id:
            continue
        if shift.get("status") in {"ACTIVE", "SIGNED_ON", "HEARTBEAT", "STALE", "SUSPENDED"}:
            return shift
    return None


def _lease_release_evidence_for_active_lease(
    root: Path,
    lease: Mapping[str, Any],
    *,
    max_receipts: int = 5,
) -> list[dict[str, Any]]:
    """Find release receipts that plausibly refer to an active lease.

    This is diagnostic evidence only. It does not authorize deleting an active
    lease from the board because a distinct lease release receipt exists.
    """

    leases_dir = _runtime_path(root, WORKER_SHIFT_ROOT / "leases")
    if not leases_dir.is_dir():
        return []
    lease_id = str(lease.get("lease_id") or "").strip()
    worker_id = str(lease.get("worker_id") or "").strip()
    lease_paths = [
        str(path).replace("\\", "/").strip()
        for path in list(lease.get("paths") or []) + list(lease.get("raw_paths") or [])
        if str(path or "").strip()
    ]
    evidence: list[dict[str, Any]] = []
    for receipt_path in sorted(leases_dir.glob("*_release.json"), reverse=True):
        payload = _read_json(receipt_path)
        if not isinstance(payload, Mapping):
            continue
        released_leases = payload.get("released_leases")
        if not isinstance(released_leases, list):
            continue
        for released in released_leases:
            if not isinstance(released, Mapping):
                continue
            released_lease_id = str(released.get("lease_id") or "").strip()
            released_worker_id = str(released.get("worker_id") or "").strip()
            released_paths = [
                str(path).replace("\\", "/").strip()
                for path in list(released.get("paths") or []) + list(released.get("raw_paths") or [])
                if str(path or "").strip()
            ]
            overlaps = [
                {"lease_path": lease_path, "released_path": released_path}
                for lease_path in lease_paths
                for released_path in released_paths
                if _path_overlap(lease_path, released_path)
            ]
            same_lease_id = bool(lease_id and released_lease_id == lease_id)
            same_worker_id = bool(worker_id and released_worker_id == worker_id)
            if not same_lease_id and not same_worker_id and not overlaps:
                continue
            evidence.append(
                {
                    "receipt_path": _rel(receipt_path, root),
                    "release_result": payload.get("result"),
                    "released_lease_id": released_lease_id,
                    "released_worker_id": released_worker_id,
                    "released_lease_type": released.get("lease_type") or released.get("mode"),
                    "released_at": released.get("released_at"),
                    "release_reason": released.get("release_reason"),
                    "same_lease_id": same_lease_id,
                    "same_worker_id": same_worker_id,
                    "path_overlap_count": len(overlaps),
                    "path_overlaps": overlaps[:10],
                }
            )
            if len(evidence) >= max_receipts:
                return evidence
    return evidence


def _orphan_reconciliation_for_active_lease(
    root: Path,
    board: Mapping[str, Any],
    lease: Mapping[str, Any],
) -> dict[str, Any]:
    """Classify whether an unbound active lease is an orphan candidate."""

    worker_id = str(lease.get("worker_id") or "").strip()
    active_shift = _active_shift_for_worker_id(board, worker_id) if worker_id else None
    lease_type = str(lease.get("lease_type") or lease.get("mode") or "unknown").strip() or "unknown"
    release_evidence = _lease_release_evidence_for_active_lease(root, lease)
    exact_release_evidence = [
        item
        for item in release_evidence
        if item.get("same_lease_id") and str(item.get("release_result") or "") == "RELEASED"
    ]
    orphan_candidate = active_shift is None and _lease_identity_binding_blocked(lease)
    exclusive_orphan_candidate = orphan_candidate and lease_type == "exclusive_write"
    if exact_release_evidence:
        classification = "ACTIVE_LEASE_HAS_EXACT_RELEASE_RECEIPT"
    elif exclusive_orphan_candidate:
        classification = "ORPHAN_ACTIVE_EXCLUSIVE_WRITE_BLOCKED"
    elif orphan_candidate:
        classification = "ORPHAN_ACTIVE_NON_EXCLUSIVE_LEASE_BLOCKED"
    else:
        classification = "LIVE_LEASE_NOT_ORPHAN"
    return {
        "schema_id": ORPHAN_LEASE_RECONCILIATION_SCHEMA_ID,
        "classification": classification,
        "orphan_candidate": orphan_candidate,
        "exclusive_write_orphan_candidate": exclusive_orphan_candidate,
        "active_shift_found": active_shift is not None,
        "matching_active_shift_id": active_shift.get("shift_id") if isinstance(active_shift, Mapping) else None,
        "exact_release_receipt_count": len(exact_release_evidence),
        "release_receipt_evidence_count": len(release_evidence),
        "release_receipt_evidence": release_evidence,
        "auto_release_allowed": False,
        "reconcile_action": "classified_left_active_blocked" if orphan_candidate else "no_reconciliation_needed",
        "release_requirement": "bound_agent_release_or_operator_override_receipt_required" if orphan_candidate else None,
        "forbidden_actions": [
            "silent_active_lease_deletion",
            "release_based_only_on_distinct_queue_runner_lease_receipt",
            "accepted_state_claim_from_orphan_classifier",
        ],
        "authority": dict(AUTHORITY_FALSE),
    }


def _worker_id_authorization(
    board: Mapping[str, Any],
    worker_id: str,
    *,
    allow_mismatch: bool = False,
) -> dict[str, Any]:
    active_shifts = [
        shift for shift in board.get("active_shifts", [])
        if isinstance(shift, Mapping) and shift.get("status") in {"ACTIVE", "SIGNED_ON", "HEARTBEAT", "STALE", "SUSPENDED"}
    ]
    matched = _active_shift_for_worker_id(board, worker_id)
    blocked = bool(active_shifts and matched is None and not allow_mismatch)
    if matched:
        identity = matched.get("identity") if isinstance(matched.get("identity"), Mapping) else {}
        fields = _declared_identity_fields(worker_id)
        binding_status = identity.get("identity_binding_status") or matched.get("identity_binding_status") or fields["identity_binding_status"]
        declared_true_name = identity.get("declared_true_name") or matched.get("declared_true_name") or fields["declared_true_name"]
        source = identity.get("worker_id_source") or matched.get("worker_id_source") or fields["worker_id_source"]
    else:
        fields = _declared_identity_fields(worker_id, generated_fallback=not active_shifts)
        binding_status = fields["identity_binding_status"] if active_shifts else IDENTITY_UNBOUND_WORKER_ID
        declared_true_name = fields["declared_true_name"] if active_shifts else None
        source = fields["worker_id_source"] if active_shifts else "unbound_no_active_signon"
    return {
        "authorized": not blocked,
        "reason_code": REASON_WORKER_ID_ACTIVE_SIGNON_MISMATCH if blocked else "AUTHORIZED",
        "worker_id": worker_id,
        "active_signon_required": bool(active_shifts),
        "active_signon_matched": matched is not None,
        "active_worker_ids": [str(shift.get("worker_id")) for shift in active_shifts],
        "declared_true_name": declared_true_name,
        "identity_binding_status": binding_status,
        "worker_id_source": source,
    }


def _receipt_ref(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": _rel(path, root),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _record_receipt(board: dict[str, Any], receipt_path: Path, root: Path) -> None:
    refs = list(board.get("recent_receipts", []))
    refs.append(_receipt_ref(receipt_path, root))
    board["recent_receipts"] = refs[-50:]


def _upsert_shift(board: dict[str, Any], shift: Mapping[str, Any]) -> None:
    worker_id = shift.get("worker_id")
    board["active_shifts"] = [
        existing for existing in board.get("active_shifts", []) if existing.get("worker_id") != worker_id
    ]
    if shift.get("status") in {"ACTIVE", "SIGNED_ON", "HEARTBEAT", "STALE", "SUSPENDED"}:
        board["active_shifts"].append(dict(shift))


def _clean_path(value: str | Path) -> str:
    text = str(value).replace("\\", "/")
    text = re.sub(r"/+", "/", text).strip()
    while text.startswith("./"):
        text = text[2:]
    if len(text) > 1:
        text = text.rstrip("/")
    return text or "."


def _paths(paths: Iterable[str | Path] | None) -> list[str]:
    return sorted({_clean_path(path) for path in (paths or [])})


def _workspace_authority_for_root(root: Path) -> WorkspaceAuthority:
    resolved_root = root.resolve(strict=False)
    root_manifest = resolved_root / "ION_WORKSPACE_MANIFEST.yaml"
    if root_manifest.is_file():
        try:
            authority = load_workspace_authority(root_manifest)
            if authority.active_repo_root == resolved_root:
                return authority
        except Exception:
            pass
    try:
        authority = load_workspace_authority()
        if authority.active_repo_root == resolved_root:
            return authority
    except Exception:
        pass

    workspace_root = resolved_root.parent.resolve(strict=False)
    return WorkspaceAuthority(
        workspace_root=workspace_root,
        active_repo_root=resolved_root,
        ion_content_root=(resolved_root / "ION").resolve(strict=False),
        export_root=(workspace_root / "ION_EXPORTS_LOCAL").resolve(strict=False),
        vault_root=(workspace_root / "ION_VAULT_LOCAL").resolve(strict=False),
        allowed_sibling_roots=(
            (workspace_root / "ION_EXPORTS_LOCAL").resolve(strict=False),
            (workspace_root / "ION_VAULT_LOCAL").resolve(strict=False),
            (workspace_root / "Needs_Routed").resolve(strict=False),
            (workspace_root / "quarantine").resolve(strict=False),
            (workspace_root / "quarentine").resolve(strict=False),
        ),
        forbidden_roots=(
            Path("/home/sev/ION_EXPORTS_LOCAL").resolve(strict=False),
            Path("/home/sev/.ssh").resolve(strict=False),
            Path("/home/sev/.config").resolve(strict=False),
            Path("/home/sev/.codex").resolve(strict=False),
        ),
        path_policy={
            "forbid_parent_segments_for_write": True,
            "canonicalize_all_leases": True,
            "require_workspace_containment_for_artifacts": True,
            "require_artifacts_outside_active_repo": True,
            "require_human_override_for_external_paths": True,
        },
        manifest_path=Path("/home/sev/ION - Production/ION_WORKSPACE_MANIFEST.yaml"),
    )


def _lease_path_purpose(lease_mode: str) -> str:
    if lease_mode == "read":
        return "read"
    if lease_mode == "artifact":
        return "artifact"
    return "write"


def _authorize_lease_paths(root: Path, paths: Iterable[str], lease_mode: str) -> list[dict[str, Any]]:
    authority = _workspace_authority_for_root(root)
    purpose = _lease_path_purpose(lease_mode)
    decisions: list[dict[str, Any]] = []
    for path in paths:
        decision = decide_path_authority(path, purpose=purpose, base_root="active_repo", authority=authority)
        if (
            lease_mode in {"write", "exclusive_write"}
            and decision.get("authorized")
            and decision.get("classification") == "WORKSPACE_EXPORT"
        ):
            decision = dict(decision)
            decision["authorized"] = False
            decision["reason_code"] = REASON_WORKSPACE_EXPORT_REQUIRES_ARTIFACT_LEASE
        decisions.append(decision)
    return decisions


def _path_authority_summary(decisions: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    items = [dict(decision) for decision in decisions]
    blocked = [item for item in items if not item.get("authorized")]
    return {
        "authorized": not blocked,
        "decision_count": len(items),
        "blocked_count": len(blocked),
        "reason_codes": sorted({str(item.get("reason_code")) for item in blocked}),
        "classifications": sorted({str(item.get("classification")) for item in items}),
    }


def _normalize_lease_mode(value: Any) -> str:
    mode = str(value or "").strip()
    if mode in LEASE_MODES:
        return mode
    if mode in LEGACY_LEASE_MODE_ALIASES:
        return LEGACY_LEASE_MODE_ALIASES[mode]
    raise ValueError(f"unsupported lease mode:{mode}")


def _safe_normalize_lease_mode(value: Any) -> str:
    try:
        return _normalize_lease_mode(value)
    except ValueError:
        return str(value or "").strip()


def _path_overlap(left: str, right: str) -> bool:
    left_clean = left.rstrip("/")
    right_clean = right.rstrip("/")
    return (
        left_clean == right_clean
        or left_clean.startswith(f"{right_clean}/")
        or right_clean.startswith(f"{left_clean}/")
    )


def detect_lease_conflicts(
    candidate_lease: Mapping[str, Any],
    *,
    board: Mapping[str, Any] | None = None,
    existing_leases: Iterable[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Classify lease conflicts. Exclusive writes and same-target writes are hard."""

    leases = list(existing_leases or (board or {}).get("active_leases", []))
    candidate_id = candidate_lease.get("lease_id")
    candidate_mode = _normalize_lease_mode(candidate_lease.get("mode") or candidate_lease.get("lease_type"))
    candidate_paths = [str(path) for path in candidate_lease.get("paths", [])]
    hard: list[dict[str, Any]] = []
    advisory: list[dict[str, Any]] = []
    for lease in leases:
        if lease.get("status") not in (None, "ACTIVE", "CLAIMED"):
            continue
        if candidate_id and lease.get("lease_id") == candidate_id:
            continue
        lease_mode = _normalize_lease_mode(lease.get("mode") or lease.get("lease_type"))
        lease_paths = [str(path) for path in lease.get("paths", [])]
        overlaps = [
            {"candidate_path": candidate_path, "existing_path": existing_path}
            for candidate_path in candidate_paths
            for existing_path in lease_paths
            if _path_overlap(candidate_path, existing_path)
        ]
        if not overlaps:
            continue
        item = {
            "lease_id": lease.get("lease_id"),
            "worker_id": lease.get("worker_id"),
            "mode": lease_mode,
            "lease_type": lease.get("lease_type") or lease_mode,
            "overlaps": overlaps,
        }
        if candidate_mode == "exclusive_write" or lease_mode == "exclusive_write":
            hard.append(item)
        elif candidate_mode == "write" and lease_mode == "write":
            hard.append(item)
        elif not (candidate_mode == "read" and lease_mode == "read"):
            advisory.append(item)
    return {
        "hard_conflicts": hard,
        "advisory_conflicts": advisory,
        "has_hard_conflict": bool(hard),
        "has_advisory_conflict": bool(advisory),
        "policy": "exclusive_write_or_same_target_write_blocks_overlap",
    }


def write_signon_receipt(
    *,
    root: str | Path | None = None,
    identity: Mapping[str, Any] | None = None,
    carrier_type: str = "codex_cli",
    carrier_instance_id: str | None = None,
    model: str | None = None,
    role_hint: str | None = None,
    domain_hint: str | None = None,
    packet_id: str | None = None,
    current_objective: str | None = None,
    current_branch: str | None = None,
    return_target: str | None = None,
    likely_touched_paths: Iterable[str | Path] | None = None,
    mount_receipt_ref: str | None = None,
    ai_movement_envelope: Mapping[str, Any] | None = None,
    ai_movement_gate_decision: Mapping[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    """Write a sign-on receipt and add/update the active shift board."""

    shell_root = _resolve_root(root)
    timestamp = now or _now()
    _ensure_runtime_dirs(shell_root)
    board = load_shift_board(shell_root)
    worker_identity = _normalize_worker_identity(
        identity
        or generate_worker_id(
            carrier_type=carrier_type,
            active_root=shell_root,
            carrier_instance_id=carrier_instance_id,
            model=model,
            role_hint=role_hint,
            domain_hint=domain_hint,
            board=board,
            now=timestamp,
        ),
        generated_fallback=identity is None,
    )
    worker_id = str(worker_identity["worker_id"])
    shift_id = f"shift:{_hash_short(worker_id + timestamp)}"
    touched = _paths(likely_touched_paths)
    path_authority_decisions = _authorize_lease_paths(shell_root, touched, "write") if touched else []
    path_authority = _path_authority_summary(path_authority_decisions)
    ai_movement = _ai_movement_receipt_payload(
        envelope=ai_movement_envelope,
        gate_decision=ai_movement_gate_decision,
    )
    ai_movement_gate = ai_movement.get("gate_decision") if ai_movement else None
    candidate_leases = [
        {
            "worker_id": worker_id,
            "declared_true_name": worker_identity.get("declared_true_name"),
            "identity_binding_status": worker_identity.get("identity_binding_status"),
            "worker_id_source": worker_identity.get("worker_id_source"),
            "mode": "write",
            "lease_type": "write",
            "paths": touched,
            "raw_paths": touched,
            "resolved_paths": [decision["resolved_path"] for decision in path_authority_decisions],
            "path_authority": path_authority,
            "path_authority_decisions": path_authority_decisions,
            "ai_movement_gate": ai_movement_gate,
            "status": "CANDIDATE" if path_authority["authorized"] else "CANDIDATE_BLOCKED_PATH_AUTHORITY",
        }
    ] if touched else []
    receipt = {
        "schema_id": SIGNON_RECEIPT_SCHEMA_ID,
        "receipt_type": "sign_on",
        "created_at": timestamp,
        "shift_id": shift_id,
        "worker_id": worker_id,
        "declared_true_name": worker_identity.get("declared_true_name"),
        "identity_binding_status": worker_identity.get("identity_binding_status"),
        "worker_id_source": worker_identity.get("worker_id_source"),
        "identity": worker_identity,
        "status": "SIGNED_ON",
        "executor_lifecycle_state": LIFECYCLE_STATE_MAP["SIGNED_ON"],
        "packet_id": packet_id,
        "current_objective": current_objective,
        "current_branch": current_branch,
        "return_target": return_target,
        "likely_touched_paths": touched,
        "candidate_leases": candidate_leases,
        "mount_receipt_ref": mount_receipt_ref,
        "relationships": {
            "complements_carrier_mount_receipts": True,
            "maps_to_executor_lifecycle": True,
            "uses_carrier_messages_for_communication": True,
            "feeds_scheduler_allocator_presence": True,
        },
        "authority": dict(AUTHORITY_FALSE),
    }
    if ai_movement:
        receipt["ai_movement"] = ai_movement
    receipt_path = _runtime_path(shell_root, WORKER_SHIFT_ROOT / "signons" / f"{_stamp(timestamp)}_{_slug(worker_id)}.json")
    _write_json(receipt_path, receipt)
    shift = {
        "shift_id": shift_id,
        "worker_id": worker_id,
        "declared_true_name": worker_identity.get("declared_true_name"),
        "identity_binding_status": worker_identity.get("identity_binding_status"),
        "worker_id_source": worker_identity.get("worker_id_source"),
        "identity": worker_identity,
        "status": "ACTIVE",
        "executor_lifecycle_state": "ACTIVE",
        "started_at": timestamp,
        "last_heartbeat_at": timestamp,
        "packet_id": packet_id,
        "current_objective": current_objective,
        "current_branch": current_branch,
        "return_target": return_target,
        "likely_touched_paths": touched,
        "signon_receipt_path": _rel(receipt_path, shell_root),
    }
    if ai_movement_gate:
        shift["ai_movement_gate"] = ai_movement_gate
    _upsert_shift(board, shift)
    _record_receipt(board, receipt_path, shell_root)
    write_shift_board(board, shell_root)
    return {"receipt": receipt, "receipt_path": _rel(receipt_path, shell_root), "board": load_shift_board(shell_root)}


def write_heartbeat(
    *,
    root: str | Path | None = None,
    worker_id: str,
    shift_id: str | None = None,
    status: str = "HEARTBEAT",
    note: str | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    """Write a quiet heartbeat receipt and refresh the board timestamp."""

    shell_root = _resolve_root(root)
    timestamp = now or _now()
    _ensure_runtime_dirs(shell_root)
    board = load_shift_board(shell_root)
    matched_shift = None
    for shift in board.get("active_shifts", []):
        if shift.get("worker_id") == worker_id and (shift_id is None or shift.get("shift_id") == shift_id):
            matched_shift = shift
            shift["last_heartbeat_at"] = timestamp
            shift["status"] = "ACTIVE"
            shift["executor_lifecycle_state"] = "ACTIVE"
            break
    receipt = {
        "schema_id": HEARTBEAT_RECEIPT_SCHEMA_ID,
        "receipt_type": "heartbeat",
        "created_at": timestamp,
        "worker_id": worker_id,
        "shift_id": shift_id or (matched_shift or {}).get("shift_id"),
        "status": status,
        "note": note,
        "authority": dict(AUTHORITY_FALSE),
    }
    receipt_path = _runtime_path(shell_root, WORKER_SHIFT_ROOT / "heartbeats" / f"{_stamp(timestamp)}_{_slug(worker_id)}.json")
    _write_json(receipt_path, receipt)
    _record_receipt(board, receipt_path, shell_root)
    write_shift_board(board, shell_root)
    return {"receipt": receipt, "receipt_path": _rel(receipt_path, shell_root), "board": load_shift_board(shell_root)}


def sign_on(
    worker_id: str,
    carrier: str,
    mission: str,
    allowed_paths: Iterable[str | Path],
    *,
    root: str | Path | None = None,
    display_callsign: str | None = None,
    carrier_instance_id: str | None = None,
    model: str | None = None,
    role_hint: str | None = None,
    domain_hint: str | None = None,
    packet_id: str | None = None,
    ai_movement_envelope: Mapping[str, Any] | None = None,
    ai_movement_gate_decision: Mapping[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    """Minimal public sign-on API for one worker shift."""

    shell_root = _resolve_root(root)
    timestamp = now or _now()
    carrier_type = _slug(carrier, fallback="worker").lower()
    identity = {
        "worker_id": worker_id,
        "display_callsign": display_callsign or worker_id,
        **_declared_identity_fields(worker_id),
        "carrier_type": carrier_type,
        "carrier_instance_id": carrier_instance_id,
        "model": model,
        "role_hint": role_hint,
        "domain_hint": domain_hint,
        "active_root": str(shell_root),
        "created_at": timestamp,
        "authority": dict(AUTHORITY_FALSE),
    }
    return write_signon_receipt(
        root=shell_root,
        identity=identity,
        carrier_type=carrier_type,
        carrier_instance_id=carrier_instance_id,
        model=model,
        role_hint=role_hint,
        domain_hint=domain_hint,
        packet_id=packet_id,
        current_objective=mission,
        likely_touched_paths=allowed_paths,
        ai_movement_envelope=ai_movement_envelope,
        ai_movement_gate_decision=ai_movement_gate_decision,
        now=timestamp,
    )


def heartbeat(
    worker_id: str,
    *,
    root: str | Path | None = None,
    shift_id: str | None = None,
    note: str | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    """Minimal public heartbeat API for an active worker."""

    return write_heartbeat(root=root, worker_id=worker_id, shift_id=shift_id, note=note, now=now)


def claim_work_lease(
    worker_id: str | None = None,
    lease_id: str | None = None,
    paths: Iterable[str | Path] | None = None,
    mode: str | None = None,
    *,
    root: str | Path | None = None,
    lease_type: str | None = None,
    objective: str | None = None,
    packet_id: str | None = None,
    branch_id: str | None = None,
    ai_movement_envelope: Mapping[str, Any] | None = None,
    ai_movement_gate_decision: Mapping[str, Any] | None = None,
    now: str | None = None,
    allow_hard_conflict: bool = False,
    allow_worker_id_mismatch: bool = False,
) -> dict[str, Any]:
    """Claim a work lease. Advisory conflicts do not block; hard conflicts do."""

    shell_root = _resolve_root(root)
    timestamp = now or _now()
    _ensure_runtime_dirs(shell_root)
    if not worker_id:
        raise ValueError("worker_id is required")
    lease_mode = _normalize_lease_mode(mode or lease_type)
    lease_paths = _paths(paths)
    if not lease_paths:
        raise ValueError("at least one lease path is required")
    board = load_shift_board(shell_root)
    worker_id_authorization = _worker_id_authorization(
        board,
        worker_id,
        allow_mismatch=allow_worker_id_mismatch,
    )
    path_authority_decisions = _authorize_lease_paths(shell_root, lease_paths, lease_mode)
    path_authority = _path_authority_summary(path_authority_decisions)
    ai_movement = _ai_movement_receipt_payload(
        envelope=ai_movement_envelope,
        gate_decision=ai_movement_gate_decision,
    )
    ai_movement_gate = ai_movement.get("gate_decision") if ai_movement else None
    lease = {
        "lease_id": lease_id or f"lease:{_hash_short(worker_id + lease_mode + '|'.join(lease_paths) + timestamp)}",
        "worker_id": worker_id,
        "declared_true_name": worker_id_authorization.get("declared_true_name"),
        "identity_binding_status": worker_id_authorization.get("identity_binding_status"),
        "worker_id_source": worker_id_authorization.get("worker_id_source"),
        "worker_id_authorization": worker_id_authorization,
        "mode": lease_mode,
        "lease_type": lease_mode,
        "paths": lease_paths,
        "raw_paths": lease_paths,
        "resolved_paths": [decision["resolved_path"] for decision in path_authority_decisions],
        "path_authority": path_authority,
        "path_authority_decisions": path_authority_decisions,
        "objective": objective,
        "packet_id": packet_id,
        "branch_id": branch_id,
        "status": "ACTIVE",
        "claimed_at": timestamp,
        "authority": dict(AUTHORITY_FALSE),
    }
    if ai_movement:
        lease["ai_movement"] = ai_movement
        lease["ai_movement_gate"] = ai_movement_gate
    conflicts = detect_lease_conflicts(lease, board=board)
    blocked_by_ai_movement_gate = _ai_movement_gate_blocks(ai_movement_gate)
    blocked_by_path_authority = not path_authority["authorized"]
    blocked_by_conflict = conflicts["has_hard_conflict"] and not allow_hard_conflict
    blocked_by_worker_id = not worker_id_authorization["authorized"]
    blocked = blocked_by_ai_movement_gate or blocked_by_path_authority or blocked_by_conflict or blocked_by_worker_id
    if blocked_by_ai_movement_gate:
        lease["status"] = "BLOCKED_AI_MOVEMENT_GATE"
        lease["block_reason_code"] = REASON_AI_MOVEMENT_GATE_BLOCKED
    elif blocked_by_worker_id:
        lease["status"] = "BLOCKED_WORKER_ID_MISMATCH"
    elif blocked_by_path_authority:
        lease["status"] = "BLOCKED_PATH_AUTHORITY"
    elif blocked_by_conflict:
        lease["status"] = "BLOCKED_HARD_CONFLICT"
    receipt = {
        "schema_id": LEASE_RECEIPT_SCHEMA_ID,
        "receipt_type": "lease_claim",
        "created_at": timestamp,
        "lease": lease,
        "path_authority": path_authority,
        "path_authority_decisions": path_authority_decisions,
        "worker_id_authorization": worker_id_authorization,
        "conflicts": conflicts,
        "result": lease["status"],
        "authority": dict(AUTHORITY_FALSE),
    }
    if ai_movement:
        receipt["ai_movement"] = ai_movement
    receipt_path = _runtime_path(shell_root, WORKER_SHIFT_ROOT / "leases" / f"{_stamp(timestamp)}_{_slug(lease['lease_id'])}_claim.json")
    _write_json(receipt_path, receipt)
    if not blocked:
        board["active_leases"] = [
            existing for existing in board.get("active_leases", []) if existing.get("lease_id") != lease["lease_id"]
        ]
        board["active_leases"].append(lease)
    _record_receipt(board, receipt_path, shell_root)
    write_shift_board(board, shell_root)
    return {"receipt": receipt, "receipt_path": _rel(receipt_path, shell_root), "board": load_shift_board(shell_root)}


def release_work_lease(
    worker_id: str | None = None,
    lease_id: str | None = None,
    *,
    root: str | Path | None = None,
    paths: Iterable[str | Path] | None = None,
    reason: str = "released",
    now: str | None = None,
) -> dict[str, Any]:
    """Release matching active leases and write a lease-release receipt."""

    shell_root = _resolve_root(root)
    timestamp = now or _now()
    _ensure_runtime_dirs(shell_root)
    board = load_shift_board(shell_root)
    wanted_paths = set(_paths(paths))
    released: list[dict[str, Any]] = []
    kept: list[dict[str, Any]] = []
    for lease in board.get("active_leases", []):
        matches = True
        if lease_id is not None:
            matches = matches and lease.get("lease_id") == lease_id
        if worker_id is not None:
            matches = matches and lease.get("worker_id") == worker_id
        if wanted_paths:
            matches = matches and bool(wanted_paths.intersection(set(lease.get("paths", []))))
        if matches:
            updated = dict(lease)
            updated["status"] = "RELEASED"
            updated["released_at"] = timestamp
            updated["release_reason"] = reason
            released.append(updated)
        else:
            kept.append(lease)
    board["active_leases"] = kept
    receipt = {
        "schema_id": LEASE_RECEIPT_SCHEMA_ID,
        "receipt_type": "lease_release",
        "created_at": timestamp,
        "lease_id": lease_id,
        "worker_id": worker_id,
        "paths": sorted(wanted_paths),
        "released_leases": released,
        "result": "RELEASED" if released else "NO_MATCHING_ACTIVE_LEASE",
        "authority": dict(AUTHORITY_FALSE),
    }
    receipt_path = _runtime_path(shell_root, WORKER_SHIFT_ROOT / "leases" / f"{_stamp(timestamp)}_{_slug(worker_id or lease_id or 'lease')}_release.json")
    _write_json(receipt_path, receipt)
    _record_receipt(board, receipt_path, shell_root)
    write_shift_board(board, shell_root)
    return {"receipt": receipt, "receipt_path": _rel(receipt_path, shell_root), "board": load_shift_board(shell_root)}


def sign_off(
    worker_id: str,
    summary: str | Mapping[str, Any],
    *,
    root: str | Path | None = None,
    shift_id: str | None = None,
    touched_paths: Iterable[str | Path] | None = None,
    validation: Iterable[str] | None = None,
    next_baton: str | None = None,
    status: str = "RETURNED",
    ai_movement_envelope: Mapping[str, Any] | None = None,
    ai_movement_gate_decision: Mapping[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    """Minimal public sign-off API for one worker shift."""

    work_done: str | None
    if isinstance(summary, Mapping):
        work_done = summary.get("work_done") or summary.get("summary") or json.dumps(summary, sort_keys=True)
        touched = touched_paths if touched_paths is not None else summary.get("touched_paths")
        checks = validation if validation is not None else summary.get("validation")
        baton = next_baton if next_baton is not None else summary.get("next_baton")
        movement_envelope = ai_movement_envelope if ai_movement_envelope is not None else summary.get("ai_movement_envelope")
        movement_gate_decision = (
            ai_movement_gate_decision
            if ai_movement_gate_decision is not None
            else summary.get("ai_movement_gate_decision")
        )
    else:
        work_done = str(summary)
        touched = touched_paths
        checks = validation
        baton = next_baton
        movement_envelope = ai_movement_envelope
        movement_gate_decision = ai_movement_gate_decision
    return write_signoff_receipt(
        root=root,
        worker_id=worker_id,
        shift_id=shift_id,
        status=status,
        work_done=work_done,
        touched_paths=touched,
        validation=checks,
        next_baton=baton,
        ai_movement_envelope=movement_envelope,
        ai_movement_gate_decision=movement_gate_decision,
        now=now,
    )


def write_signoff_receipt(
    *,
    root: str | Path | None = None,
    worker_id: str,
    shift_id: str | None = None,
    status: str = "RETURNED",
    work_done: str | None = None,
    touched_paths: Iterable[str | Path] | None = None,
    validation: Iterable[str] | None = None,
    receipts_created: Iterable[str | Path] | None = None,
    next_baton: str | None = None,
    release_leases: bool = True,
    allow_worker_id_mismatch: bool = False,
    ai_movement_envelope: Mapping[str, Any] | None = None,
    ai_movement_gate_decision: Mapping[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    """Write a sign-off receipt, remove the shift, and optionally release leases."""

    shell_root = _resolve_root(root)
    timestamp = now or _now()
    _ensure_runtime_dirs(shell_root)
    board = load_shift_board(shell_root)
    worker_id_authorization = _worker_id_authorization(
        board,
        worker_id,
        allow_mismatch=allow_worker_id_mismatch,
    )
    blocked_by_worker_id = not worker_id_authorization["authorized"]
    receipt_status = "BLOCKED_WORKER_ID_MISMATCH" if blocked_by_worker_id else status
    lifecycle_state = LIFECYCLE_STATE_MAP.get(receipt_status, "SUSPENDED" if blocked_by_worker_id else "RETURNED")
    released_lease_ids: list[str] = []
    if release_leases and not blocked_by_worker_id:
        for lease in board.get("active_leases", []):
            if lease.get("worker_id") == worker_id:
                released_lease_ids.append(str(lease.get("lease_id")))
        board["active_leases"] = [lease for lease in board.get("active_leases", []) if lease.get("worker_id") != worker_id]
    if not blocked_by_worker_id:
        board["active_shifts"] = [
            shift
            for shift in board.get("active_shifts", [])
            if not (shift.get("worker_id") == worker_id and (shift_id is None or shift.get("shift_id") == shift_id))
        ]
    ai_movement = _ai_movement_receipt_payload(
        envelope=ai_movement_envelope,
        gate_decision=ai_movement_gate_decision,
    )
    receipt = {
        "schema_id": SIGNOFF_RECEIPT_SCHEMA_ID,
        "receipt_type": "sign_off",
        "created_at": timestamp,
        "worker_id": worker_id,
        "declared_true_name": worker_id_authorization.get("declared_true_name"),
        "identity_binding_status": worker_id_authorization.get("identity_binding_status"),
        "worker_id_source": worker_id_authorization.get("worker_id_source"),
        "worker_id_authorization": worker_id_authorization,
        "shift_id": shift_id,
        "status": receipt_status,
        "requested_status": status,
        "executor_lifecycle_state": lifecycle_state,
        "work_done": work_done,
        "touched_paths": _paths(touched_paths),
        "validation": list(validation or []),
        "receipts_created": [str(path) for path in (receipts_created or [])],
        "released_lease_ids": released_lease_ids,
        "next_baton": next_baton,
        "authority": dict(AUTHORITY_FALSE),
    }
    if ai_movement:
        receipt["ai_movement"] = ai_movement
    receipt_path = _runtime_path(shell_root, WORKER_SHIFT_ROOT / "signoffs" / f"{_stamp(timestamp)}_{_slug(worker_id)}.json")
    _write_json(receipt_path, receipt)
    recent = list(board.get("recent_signoffs", []))
    recent.append(
        {
            "worker_id": worker_id,
            "shift_id": shift_id,
            "status": receipt_status,
            "signed_off_at": timestamp,
            "receipt_path": _rel(receipt_path, shell_root),
        }
    )
    board["recent_signoffs"] = recent[-25:]
    _record_receipt(board, receipt_path, shell_root)
    write_shift_board(board, shell_root)
    return {"receipt": receipt, "receipt_path": _rel(receipt_path, shell_root), "board": load_shift_board(shell_root)}


def classify_stale_workers(
    *,
    root: str | Path | None = None,
    board: Mapping[str, Any] | None = None,
    now: str | None = None,
    stale_after_minutes: int = 45,
    expired_after_minutes: int = 120,
    write: bool = False,
) -> dict[str, Any]:
    """Classify active shifts as fresh, stale, or expired by heartbeat age."""

    shell_root = _resolve_root(root)
    timestamp = now or _now()
    current = _parse_time(timestamp) or datetime.now(timezone.utc)
    payload = _coerce_board(board or load_shift_board(shell_root))
    stale: list[dict[str, Any]] = []
    fresh: list[dict[str, Any]] = []
    updated_shifts: list[dict[str, Any]] = []
    for shift in payload.get("active_shifts", []):
        item = dict(shift)
        heartbeat = _parse_time(item.get("last_heartbeat_at") or item.get("started_at"))
        if heartbeat is None:
            age = None
            classification = "STALE"
        else:
            age_delta = current - heartbeat
            age = int(age_delta.total_seconds() // 60)
            if age_delta >= timedelta(minutes=expired_after_minutes):
                classification = "EXPIRED"
            elif age_delta >= timedelta(minutes=stale_after_minutes):
                classification = "STALE"
            else:
                classification = "FRESH"
        item["presence_classification"] = classification
        item["heartbeat_age_minutes"] = age
        item["classified_at"] = timestamp
        if classification in {"STALE", "EXPIRED"}:
            item["status"] = classification
            item["executor_lifecycle_state"] = LIFECYCLE_STATE_MAP[classification]
            stale.append(item)
        else:
            fresh.append(item)
        updated_shifts.append(item)
    result = {
        "schema_id": "ion.worker_shift_stale_classification.v0_1",
        "classified_at": timestamp,
        "fresh_workers": fresh,
        "stale_workers": stale,
        "stale_after_minutes": stale_after_minutes,
        "expired_after_minutes": expired_after_minutes,
        "authority": dict(AUTHORITY_FALSE),
    }
    if write:
        payload["active_shifts"] = updated_shifts
        payload["stale_workers"] = stale
        stale_path = _runtime_path(shell_root, WORKER_SHIFT_ROOT / "stale" / f"{_stamp(timestamp)}_stale_workers.json")
        _write_json(stale_path, result)
        _record_receipt(payload, stale_path, shell_root)
        write_shift_board(payload, shell_root)
        result["receipt_path"] = _rel(stale_path, shell_root)
        result["board"] = load_shift_board(shell_root)
    return result


def summarize_shift_board(
    *,
    root: str | Path | None = None,
    board: Mapping[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    """Return a compact active shift-board summary for schedulers and operators."""

    shell_root = _resolve_root(root)
    payload = _coerce_board(board or load_shift_board(shell_root))
    stale = classify_stale_workers(root=shell_root, board=payload, now=now)
    active_by_status: dict[str, int] = {}
    leases_by_type: dict[str, int] = {}
    for shift in payload.get("active_shifts", []):
        status = str(shift.get("status") or "UNKNOWN")
        active_by_status[status] = active_by_status.get(status, 0) + 1
    for lease in payload.get("active_leases", []):
        lease_type = str(lease.get("lease_type") or "unknown")
        leases_by_type[lease_type] = leases_by_type.get(lease_type, 0) + 1
    unbound_lease_settlement = classify_live_unbound_leases(
        root=shell_root,
        board=payload,
        now=now,
        write_receipt=False,
    )
    orphan_rows = [
        {
            "lease_id": lease.get("lease_id"),
            "worker_id": lease.get("worker_id"),
            "lease_type": lease.get("lease_type"),
            "mode": lease.get("mode"),
            "paths": lease.get("paths", []),
            "classification": (lease.get("orphan_reconciliation") or {}).get("classification")
            if isinstance(lease.get("orphan_reconciliation"), Mapping)
            else None,
            "reconcile_action": (lease.get("orphan_reconciliation") or {}).get("reconcile_action")
            if isinstance(lease.get("orphan_reconciliation"), Mapping)
            else None,
            "auto_release_allowed": (lease.get("orphan_reconciliation") or {}).get("auto_release_allowed")
            if isinstance(lease.get("orphan_reconciliation"), Mapping)
            else None,
            "release_receipt_evidence_count": (lease.get("orphan_reconciliation") or {}).get(
                "release_receipt_evidence_count"
            )
            if isinstance(lease.get("orphan_reconciliation"), Mapping)
            else 0,
        }
        for lease in unbound_lease_settlement.get("unbound_active_leases", [])
        if isinstance(lease, Mapping)
        and isinstance(lease.get("orphan_reconciliation"), Mapping)
        and (lease.get("orphan_reconciliation") or {}).get("exclusive_write_orphan_candidate") is True
    ]
    return {
        "schema_id": "ion.worker_shift_board_summary.v0_1",
        "generated_at": now or _now(),
        "board_path": _rel(_runtime_path(shell_root, ACTIVE_BOARD_PATH), shell_root),
        "active_worker_count": len(payload.get("active_shifts", [])),
        "active_lease_count": len(payload.get("active_leases", [])),
        "unbound_active_lease_count": unbound_lease_settlement["unbound_active_lease_count"],
        "unbound_active_exclusive_write_count": unbound_lease_settlement["unbound_active_exclusive_write_count"],
        "orphan_active_exclusive_write_count": unbound_lease_settlement["orphan_active_exclusive_write_count"],
        "readiness_blocked_by_unbound_leases": unbound_lease_settlement["readiness_blocked"],
        "worker_shift_blockers": ["live_unbound_active_lease"] if unbound_lease_settlement["readiness_blocked"] else [],
        "orphan_exclusive_write_leases": orphan_rows,
        "live_unbound_lease_settlement": {
            "schema_id": unbound_lease_settlement["schema_id"],
            "ok": unbound_lease_settlement["ok"],
            "result": unbound_lease_settlement["result"],
            "settlement_required": unbound_lease_settlement["settlement_required"],
            "receipt_only": unbound_lease_settlement["receipt_only"],
            "no_silent_lease_deletion": unbound_lease_settlement["no_silent_lease_deletion"],
            "orphan_active_exclusive_write_count": unbound_lease_settlement["orphan_active_exclusive_write_count"],
            "orphan_reconciliation_schema_id": ORPHAN_LEASE_RECONCILIATION_SCHEMA_ID,
        },
        "stale_worker_count": len(stale["stale_workers"]),
        "active_by_status": active_by_status,
        "leases_by_type": leases_by_type,
        "workers": [
            {
                "worker_id": shift.get("worker_id"),
                "declared_true_name": shift.get("declared_true_name") or shift.get("identity", {}).get("declared_true_name"),
                "identity_binding_status": shift.get("identity_binding_status") or shift.get("identity", {}).get("identity_binding_status"),
                "worker_id_source": shift.get("worker_id_source") or shift.get("identity", {}).get("worker_id_source"),
                "display_callsign": shift.get("identity", {}).get("display_callsign"),
                "status": shift.get("status"),
                "packet_id": shift.get("packet_id"),
                "current_branch": shift.get("current_branch"),
                "last_heartbeat_at": shift.get("last_heartbeat_at"),
            }
            for shift in payload.get("active_shifts", [])
        ],
        "active_leases": [
            {
                "lease_id": lease.get("lease_id"),
                "worker_id": lease.get("worker_id"),
                "declared_true_name": lease.get("declared_true_name"),
                "identity_binding_status": lease.get("identity_binding_status"),
                "worker_id_source": lease.get("worker_id_source"),
                "mode": lease.get("mode") or _normalize_lease_mode(lease.get("lease_type")),
                "lease_type": lease.get("lease_type"),
                "paths": lease.get("paths", []),
            }
            for lease in payload.get("active_leases", [])
        ],
        "authority": dict(AUTHORITY_FALSE),
    }


def _parse_edit_lease_timestamp(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _edit_lease_freshness(lease: Mapping[str, Any], *, max_age_seconds: int) -> dict[str, Any]:
    timestamp_value = (
        lease.get("last_heartbeat_at")
        or lease.get("heartbeat_at")
        or lease.get("updated_at")
        or lease.get("claimed_at")
    )
    parsed = _parse_edit_lease_timestamp(timestamp_value)
    if parsed is None:
        return {
            "fresh": False,
            "reason": "lease_timestamp_missing_or_invalid",
            "max_age_seconds": max_age_seconds,
        }
    age_seconds = max(0.0, (datetime.now(timezone.utc) - parsed).total_seconds())
    return {
        "fresh": age_seconds <= max_age_seconds,
        "timestamp": parsed.isoformat(),
        "age_seconds": round(age_seconds, 3),
        "max_age_seconds": max_age_seconds,
    }


def _edit_lease_target_rows(target_files: Iterable[Any] | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in target_files or []:
        if isinstance(item, Mapping):
            candidates = [
                str(candidate).replace("\\", "/").strip()
                for candidate in item.get("lease_path_candidates") or item.get("path_candidates") or []
                if str(candidate or "").strip()
            ]
            if not candidates and str(item.get("path") or "").strip():
                candidates = [str(item.get("path")).replace("\\", "/").strip()]
            rows.append({**dict(item), "lease_path_candidates": candidates})
        else:
            text = str(item or "").replace("\\", "/").strip()
            if text:
                rows.append({"path": text, "lease_path_candidates": [text]})
    return rows


def _first_text(args: Mapping[str, Any], *field_names: str) -> str:
    for field_name in field_names:
        value = str(args.get(field_name) or "").strip()
        if value:
            return value
    return ""


def _route_is_preview_only(value: str) -> bool:
    token = _identity_status_token(value)
    return any(marker in token for marker in PREVIEW_ONLY_ROUTE_TOKENS)


def _lease_path_covers_target(lease_path: str, target_path: str) -> bool:
    lease_clean = _clean_path(lease_path)
    target_clean = _clean_path(target_path)
    if not lease_clean or not target_clean:
        return False
    return target_clean == lease_clean or target_clean.startswith(f"{lease_clean.rstrip('/')}/")


def _missing_edit_lease_targets(
    targets: Iterable[Mapping[str, Any]],
    lease_paths: Iterable[str],
) -> list[dict[str, Any]]:
    normalized_lease_paths = [
        _clean_path(path)
        for path in lease_paths
        if str(path or "").strip()
    ]
    missing: list[dict[str, Any]] = []
    for row in targets:
        candidates = [
            _clean_path(candidate)
            for candidate in row.get("lease_path_candidates") or []
            if str(candidate or "").strip()
        ]
        if candidates and any(
            _lease_path_covers_target(lease_path, candidate)
            for lease_path in normalized_lease_paths
            for candidate in candidates
        ):
            continue
        missing.append(dict(row))
    return missing


def _same_root(left: str | Path | None, right: str | Path | None) -> bool:
    if not left or not right:
        return False
    return _resolve_root(left) == _resolve_root(right)


def require_active_edit_lease(
    root: str | Path | None,
    *,
    agent_id: str | None,
    lease_id: str | None,
    target_files: Iterable[Any] | None,
    required_mode: str = "exclusive_write",
    allowed_modes: Iterable[str] | None = None,
    max_age_seconds: int = 2 * 60 * 60,
) -> dict[str, Any]:
    """Validate that an actor holds a fresh active edit lease covering targets."""

    shell_root = _resolve_root(root)
    normalized_required_mode = _safe_normalize_lease_mode(required_mode)
    normalized_allowed_modes = sorted({
        _safe_normalize_lease_mode(mode)
        for mode in (allowed_modes or [required_mode])
        if str(mode or "").strip()
    })
    if not normalized_allowed_modes:
        normalized_allowed_modes = [normalized_required_mode]
    wanted_agent = str(agent_id or "").strip()
    wanted_lease = str(lease_id or "").strip()
    targets = _edit_lease_target_rows(target_files)
    base = {
        "schema_id": "ion.worker_shift.active_edit_lease_gate.v0_1",
        "ok": False,
        "required_lease_type": normalized_required_mode,
        "allowed_lease_types": normalized_allowed_modes,
        "required_fields": ["agent_id", "lease_id"],
        "agent_id": wanted_agent,
        "lease_id": wanted_lease,
        "target_files": targets,
        "authority": dict(AUTHORITY_FALSE),
    }
    if not wanted_agent or not wanted_lease:
        return {
            **base,
            "finding": f"{required_mode}_lease_required",
            "provided_agent_id": bool(wanted_agent),
            "provided_lease_id": bool(wanted_lease),
        }
    board = load_shift_board(shell_root)
    active = [
        lease for lease in board.get("active_leases", [])
        if isinstance(lease, Mapping)
        and str(lease.get("lease_id") or "") == wanted_lease
        and str(lease.get("status") or "ACTIVE") in {"ACTIVE", "CLAIMED"}
    ]
    if not active:
        return {**base, "finding": "active_edit_lease_not_found", "active_lease_found": False}
    lease = dict(active[0])
    lease_agent_ids = {
        str(value).strip()
        for value in (
            lease.get("agent_id"),
            lease.get("worker_id"),
            lease.get("carrier_id"),
            lease.get("declared_true_name"),
        )
        if str(value or "").strip()
    }
    lease_type = str(lease.get("lease_type") or lease.get("mode") or "").strip()
    lease_paths = {
        str(path).replace("\\", "/").strip()
        for path in list(lease.get("paths") or []) + list(lease.get("raw_paths") or []) + list(lease.get("resolved_paths") or [])
        if str(path or "").strip()
    }
    missing_targets = _missing_edit_lease_targets(targets, lease_paths)
    freshness = _edit_lease_freshness(lease, max_age_seconds=max_age_seconds)
    identity_blocked = _lease_identity_binding_blocked(lease)
    blockers: list[str] = []
    if wanted_agent not in lease_agent_ids:
        blockers.append("lease_agent_mismatch")
    if lease_type not in normalized_allowed_modes:
        blockers.append("lease_type_mismatch")
    if missing_targets:
        blockers.append("lease_missing_target_coverage")
    if not freshness["fresh"]:
        blockers.append("lease_not_fresh")
    if identity_blocked:
        blockers.append("lease_identity_binding_blocked")
    if blockers:
        return {
            **base,
            "finding": "active_edit_lease_invalid",
            "blockers": blockers,
            "active_lease_found": True,
            "lease_agent_ids": sorted(lease_agent_ids),
            "lease_type": lease_type,
            "lease_paths": sorted(lease_paths),
            "missing_targets": missing_targets,
            "lease_freshness": freshness,
            "identity_binding_status": lease.get("identity_binding_status"),
            "identity_blocked": identity_blocked,
        }
    return {
        **base,
        "ok": True,
        "finding": None,
        "active_lease_found": True,
        "lease_type": lease_type,
        "covered_target_count": len(targets),
        "lease_paths": sorted(lease_paths),
        "lease_freshness": freshness,
        "identity_binding_status": lease.get("identity_binding_status"),
        "active_lease": lease,
    }


def request_edit_lease(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    """Claim an edit lease through a route-friendly wrapper."""

    shell_root = _resolve_root(root)
    agent_id = str(args.get("agent_id") or args.get("worker_id") or "").strip()
    paths = _paths(args.get("target_paths") or args.get("paths") or [])
    if not agent_id:
        return {"ok": False, "finding": "agent_id_required", "authority": dict(AUTHORITY_FALSE)}
    if not paths:
        return {"ok": False, "finding": "target_paths_required", "authority": dict(AUTHORITY_FALSE)}
    allowed_modes = {"artifact", "exclusive_write"}
    requested_modes: list[str] = []
    for field_name in ("lease_type", "lease_mode"):
        raw_mode = args.get(field_name)
        if str(raw_mode or "").strip():
            try:
                requested_modes.append(_normalize_lease_mode(raw_mode))
            except ValueError:
                return {
                    "ok": False,
                    "finding": "unsupported_lease_mode",
                    "provided_field": field_name,
                    "provided_lease_mode": str(raw_mode).strip(),
                    "supported_lease_modes": sorted(allowed_modes),
                    "authority": dict(AUTHORITY_FALSE),
                }
    unique_requested_modes = sorted(set(requested_modes))
    if len(unique_requested_modes) > 1:
        return {
            "ok": False,
            "finding": "lease_mode_conflict",
            "lease_type": str(args.get("lease_type") or "").strip(),
            "lease_mode": str(args.get("lease_mode") or "").strip(),
            "supported_lease_modes": sorted(allowed_modes),
            "authority": dict(AUTHORITY_FALSE),
        }
    lease_mode = unique_requested_modes[0] if unique_requested_modes else "exclusive_write"
    if lease_mode not in allowed_modes:
        return {
            "ok": False,
            "finding": "unsupported_lease_mode",
            "provided_lease_mode": lease_mode,
            "supported_lease_modes": sorted(allowed_modes),
            "authority": dict(AUTHORITY_FALSE),
        }
    claim = claim_work_lease(
        root=shell_root,
        worker_id=agent_id,
        lease_id=str(args.get("lease_id") or "").strip() or None,
        mode=lease_mode,
        paths=paths,
        objective=str(args.get("objective") or "").strip() or None,
        packet_id=str(args.get("packet_id") or "").strip() or None,
        branch_id=str(args.get("branch_id") or "").strip() or None,
    )
    lease = dict(claim.get("receipt", {}).get("lease") or {})
    ok = str(claim.get("receipt", {}).get("result") or "") == "ACTIVE"
    if ok:
        timestamp = _now()
        board = load_shift_board(shell_root)
        for active in board.get("active_leases", []):
            if active.get("lease_id") == lease.get("lease_id"):
                active["agent_id"] = agent_id
                active["lease_class"] = "edit_lease"
                active["target_route_id"] = str(args.get("target_route_id") or "").strip()
                active["target_tool"] = str(args.get("target_tool") or "").strip()
                active["project_id"] = str(args.get("project_id") or "").strip()
                active["idempotency_key"] = str(args.get("idempotency_key") or "").strip()
                active["client_request_id"] = str(args.get("client_request_id") or "").strip()
                active["last_heartbeat_at"] = timestamp
                active["updated_at"] = timestamp
                lease = dict(active)
        write_shift_board(board, shell_root)
    return {
        "ok": ok,
        "schema_id": "ion.worker_shift.request_edit_lease_result.v0_1",
        "lease_id": lease.get("lease_id"),
        "agent_id": agent_id,
        "claim_status": claim.get("receipt", {}).get("result"),
        "active_lease": lease if ok else None,
        "conflicts": claim.get("receipt", {}).get("conflicts", {}),
        "path_authority": claim.get("receipt", {}).get("path_authority", {}),
        "receipt_path": claim.get("receipt_path"),
        "authority": dict(AUTHORITY_FALSE),
    }


def request_write_intent_lease(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    """Claim a first-class write-intent lease before active mutation."""

    shell_root = _resolve_root(root)
    agent_id = str(args.get("agent_id") or args.get("worker_id") or "").strip()
    paths = _paths(args.get("target_paths") or args.get("paths") or [])
    root_scope = _first_text(args, "root_scope", "target_root_scope")
    target_route_id = _first_text(args, "target_route_id", "route_id", "route")
    mutation_context = _first_text(args, "mutation_context", "operation_context", "context_id", "target_context")
    idempotency_key = _first_text(args, "idempotency_key")
    client_request_id = _first_text(args, "client_request_id")
    confirmation = _first_text(args, "confirmation", "write_confirmation")
    base = {
        "ok": False,
        "schema_id": "ion.worker_shift.request_write_intent_lease_result.v0_1",
        "lease_class": WRITE_INTENT_LEASE_CLASS,
        "required_lease_type": "write",
        "agent_id": agent_id,
        "root_scope": root_scope,
        "target_route_id": target_route_id,
        "mutation_context": mutation_context,
        "required_confirmation": WRITE_INTENT_CONFIRMATION,
        "authority": dict(AUTHORITY_FALSE),
    }
    if not agent_id:
        return {**base, "finding": "agent_id_required"}
    if not paths:
        return {**base, "finding": "target_paths_required"}
    if root_scope not in WRITE_INTENT_ROOT_SCOPES:
        return {
            **base,
            "finding": "root_scope_required",
            "supported_root_scopes": list(WRITE_INTENT_ROOT_SCOPES),
        }
    for root_field in ("active_root", "target_root"):
        provided_root = str(args.get(root_field) or "").strip()
        if provided_root and not _same_root(provided_root, shell_root):
            return {
                **base,
                "finding": "root_mismatch",
                "provided_root_field": root_field,
                "provided_root": provided_root,
                "active_root": str(shell_root),
            }
    if not target_route_id or _route_is_preview_only(target_route_id):
        return {**base, "finding": "mutating_route_required"}
    if not mutation_context or _route_is_preview_only(mutation_context):
        return {**base, "finding": "mutating_context_required"}
    if not idempotency_key:
        return {**base, "finding": "idempotency_key_required"}
    if confirmation != WRITE_INTENT_CONFIRMATION:
        return {**base, "finding": "write_intent_confirmation_required"}

    board = load_shift_board(shell_root)
    active_shift = _active_shift_for_worker_id(board, agent_id)
    if active_shift is None:
        return {**base, "finding": "bound_active_signon_required"}
    if _lease_identity_binding_blocked(active_shift):
        return {
            **base,
            "finding": "bound_actor_identity_required",
            "identity_binding_status": active_shift.get("identity_binding_status")
            or (active_shift.get("identity") or {}).get("identity_binding_status")
            if isinstance(active_shift.get("identity"), Mapping)
            else active_shift.get("identity_binding_status"),
        }

    claim = claim_work_lease(
        root=shell_root,
        worker_id=agent_id,
        lease_id=str(args.get("lease_id") or "").strip() or None,
        mode="write",
        paths=paths,
        objective=str(args.get("objective") or "").strip() or None,
        packet_id=str(args.get("packet_id") or "").strip() or None,
        branch_id=str(args.get("branch_id") or "").strip() or None,
    )
    lease = dict(claim.get("receipt", {}).get("lease") or {})
    ok = str(claim.get("receipt", {}).get("result") or "") == "ACTIVE"
    if ok:
        timestamp = _now()
        board = load_shift_board(shell_root)
        for active in board.get("active_leases", []):
            if active.get("lease_id") == lease.get("lease_id"):
                active["agent_id"] = agent_id
                active["lease_class"] = WRITE_INTENT_LEASE_CLASS
                active["write_intent_required"] = True
                active["root_scope"] = root_scope
                active["active_root"] = str(shell_root)
                active["target_route_id"] = target_route_id
                active["mutation_context"] = mutation_context
                active["idempotency_key"] = idempotency_key
                active["client_request_id"] = client_request_id
                active["confirmation"] = confirmation
                active["target_paths"] = paths
                active["operation_class"] = "active_write_mutation"
                active["last_heartbeat_at"] = timestamp
                active["updated_at"] = timestamp
                lease = dict(active)
                break
        write_shift_board(board, shell_root)
    return {
        **base,
        "ok": ok,
        "finding": None if ok else "write_intent_lease_not_active",
        "lease_id": lease.get("lease_id"),
        "claim_status": claim.get("receipt", {}).get("result"),
        "active_lease": lease if ok else None,
        "conflicts": claim.get("receipt", {}).get("conflicts", {}),
        "path_authority": claim.get("receipt", {}).get("path_authority", {}),
        "receipt_path": claim.get("receipt_path"),
    }


def require_active_write_intent_lease(
    root: str | Path | None,
    *,
    agent_id: str | None,
    lease_id: str | None,
    target_files: Iterable[Any] | None,
    root_scope: str = "active_root",
    target_route_id: str | None = None,
    mutation_context: str | None = None,
    idempotency_key: str | None = None,
    confirmation: str | None = WRITE_INTENT_CONFIRMATION,
    max_age_seconds: int = 2 * 60 * 60,
) -> dict[str, Any]:
    """Validate that an actor holds a lawful write-intent lease for active writes."""

    shell_root = _resolve_root(root)
    normalized_root_scope = str(root_scope or "").strip()
    expected_confirmation = str(confirmation or WRITE_INTENT_CONFIRMATION).strip()
    gate = require_active_edit_lease(
        shell_root,
        agent_id=agent_id,
        lease_id=lease_id,
        target_files=target_files,
        required_mode="write",
        allowed_modes=WRITE_OPERATION_LEASE_MODES,
        max_age_seconds=max_age_seconds,
    )
    base = {
        "schema_id": "ion.worker_shift.active_write_intent_lease_gate.v0_1",
        "ok": False,
        "agent_id": str(agent_id or "").strip(),
        "lease_id": str(lease_id or "").strip(),
        "required_root_scope": normalized_root_scope,
        "required_confirmation": expected_confirmation,
        "allowed_lease_types": list(WRITE_OPERATION_LEASE_MODES),
        "edit_lease_gate": gate,
        "authority": dict(AUTHORITY_FALSE),
    }
    if not gate.get("ok"):
        return {
            **base,
            "finding": gate.get("finding") or "active_write_intent_lease_invalid",
            "blockers": list(gate.get("blockers") or []),
        }
    lease = dict(gate.get("active_lease") or {})
    lease_type = _safe_normalize_lease_mode(lease.get("lease_type") or lease.get("mode"))
    lease_active_root = str(lease.get("active_root") or "").strip()
    lease_root_scope = str(lease.get("root_scope") or lease.get("target_root_scope") or "").strip()
    lease_route = str(lease.get("target_route_id") or lease.get("route_id") or lease.get("route") or "").strip()
    lease_context = str(
        lease.get("mutation_context")
        or lease.get("operation_context")
        or lease.get("context_id")
        or lease.get("target_context")
        or ""
    ).strip()
    lease_idempotency = str(lease.get("idempotency_key") or "").strip()
    lease_confirmation = str(lease.get("confirmation") or lease.get("write_confirmation") or "").strip()
    blockers: list[str] = []
    if lease_type == "write" and lease.get("lease_class") != WRITE_INTENT_LEASE_CLASS:
        blockers.append("lease_class_not_write_intent")
    if normalized_root_scope not in WRITE_INTENT_ROOT_SCOPES:
        blockers.append("required_root_scope_unsupported")
    if lease_root_scope != normalized_root_scope:
        blockers.append("lease_root_scope_mismatch")
    if not _same_root(lease_active_root, shell_root):
        blockers.append("lease_root_mismatch")
    if not lease_route or _route_is_preview_only(lease_route):
        blockers.append("lease_mutating_route_missing_or_preview_only")
    if target_route_id and str(target_route_id).strip() != lease_route:
        blockers.append("lease_mutating_route_mismatch")
    if not lease_context or _route_is_preview_only(lease_context):
        blockers.append("lease_mutating_context_missing_or_preview_only")
    if mutation_context and str(mutation_context).strip() != lease_context:
        blockers.append("lease_mutating_context_mismatch")
    if not lease_idempotency:
        blockers.append("lease_idempotency_key_missing")
    if idempotency_key and str(idempotency_key).strip() != lease_idempotency:
        blockers.append("lease_idempotency_key_mismatch")
    if lease_confirmation != WRITE_INTENT_CONFIRMATION:
        blockers.append("lease_write_intent_confirmation_missing")
    if expected_confirmation and expected_confirmation != lease_confirmation:
        blockers.append("lease_write_intent_confirmation_mismatch")
    if blockers:
        return {
            **base,
            "finding": "active_write_intent_lease_invalid",
            "blockers": blockers,
            "active_lease_found": True,
            "lease_type": lease_type,
            "lease_root_scope": lease_root_scope,
            "lease_active_root": lease_active_root,
            "lease_target_route_id": lease_route,
            "lease_mutation_context": lease_context,
            "lease_idempotency_key": lease_idempotency,
            "lease_confirmation": lease_confirmation,
            "active_lease": lease,
        }
    return {
        **base,
        "ok": True,
        "finding": None,
        "active_lease_found": True,
        "lease_type": lease_type,
        "covered_target_count": gate.get("covered_target_count"),
        "lease_root_scope": lease_root_scope,
        "lease_active_root": lease_active_root,
        "lease_target_route_id": lease_route,
        "lease_mutation_context": lease_context,
        "lease_idempotency_key": lease_idempotency,
        "active_lease": lease,
    }


def heartbeat_edit_lease(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    """Refresh freshness fields on one active edit lease."""

    shell_root = _resolve_root(root)
    timestamp = _now()
    agent_id = str(args.get("agent_id") or args.get("worker_id") or "").strip()
    lease_id = str(args.get("lease_id") or "").strip()
    if not agent_id:
        return {"ok": False, "finding": "agent_id_required", "authority": dict(AUTHORITY_FALSE)}
    if not lease_id:
        return {"ok": False, "finding": "lease_id_required", "authority": dict(AUTHORITY_FALSE)}
    board = load_shift_board(shell_root)
    updated: dict[str, Any] | None = None
    for lease in board.get("active_leases", []):
        if lease.get("lease_id") == lease_id and lease.get("worker_id") == agent_id:
            lease["agent_id"] = agent_id
            lease["last_heartbeat_at"] = timestamp
            lease["updated_at"] = timestamp
            lease["status"] = "ACTIVE"
            updated = dict(lease)
            break
    if updated is None:
        return {
            "ok": False,
            "finding": "active_edit_lease_not_found",
            "lease_id": lease_id,
            "agent_id": agent_id,
            "authority": dict(AUTHORITY_FALSE),
        }
    receipt = {
        "schema_id": "ion.worker_shift.edit_lease_heartbeat_receipt.v0_1",
        "receipt_type": "edit_lease_heartbeat",
        "created_at": timestamp,
        "lease_id": lease_id,
        "agent_id": agent_id,
        "lease": updated,
        "authority": dict(AUTHORITY_FALSE),
    }
    receipt_path = _runtime_path(
        shell_root,
        WORKER_SHIFT_ROOT / "leases" / f"{_stamp(timestamp)}_{_slug(lease_id)}_heartbeat.json",
    )
    _write_json(receipt_path, receipt)
    _record_receipt(board, receipt_path, shell_root)
    write_shift_board(board, shell_root)
    return {
        "ok": True,
        "schema_id": "ion.worker_shift.heartbeat_edit_lease_result.v0_1",
        "lease_id": lease_id,
        "agent_id": agent_id,
        "active_lease": updated,
        "receipt_path": _rel(receipt_path, shell_root),
        "authority": dict(AUTHORITY_FALSE),
    }


def release_edit_lease(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    """Release exactly one edit lease by agent and lease id."""

    agent_id = str(args.get("agent_id") or args.get("worker_id") or "").strip()
    lease_id = str(args.get("lease_id") or "").strip()
    if not agent_id:
        return {"ok": False, "finding": "agent_id_required", "authority": dict(AUTHORITY_FALSE)}
    if not lease_id:
        return {"ok": False, "finding": "lease_id_required", "authority": dict(AUTHORITY_FALSE)}
    result = release_work_lease(
        root=root,
        worker_id=agent_id,
        lease_id=lease_id,
        reason=str(args.get("reason") or "edit_lease_released").strip(),
    )
    released = result.get("receipt", {}).get("released_leases", result.get("receipt", {}).get("released", []))
    return {
        "ok": bool(released),
        "schema_id": "ion.worker_shift.release_edit_lease_result.v0_1",
        "lease_id": lease_id,
        "agent_id": agent_id,
        "release_status": result.get("receipt", {}).get("result"),
        "released": released,
        "receipt_path": result.get("receipt_path"),
        "authority": dict(AUTHORITY_FALSE),
    }


def classify_live_unbound_leases(
    *,
    root: str | Path | None = None,
    board: Mapping[str, Any] | None = None,
    now: str | None = None,
    write_receipt: bool = False,
    reason: str | None = None,
) -> dict[str, Any]:
    """Classify active leases with blocked identity binding without deleting state."""

    shell_root = _resolve_root(root)
    timestamp = now or _now()
    payload = _coerce_board(board or load_shift_board(shell_root), now=timestamp)
    active_leases = [
        lease
        for lease in payload.get("active_leases", [])
        if isinstance(lease, Mapping) and str(lease.get("status") or "ACTIVE").strip().upper() in {"ACTIVE", "CLAIMED"}
    ]
    unbound_active_leases: list[dict[str, Any]] = []
    for lease in active_leases:
        if not _lease_identity_binding_blocked(lease):
            continue
        lease_type = str(lease.get("lease_type") or lease.get("mode") or "unknown").strip() or "unknown"
        orphan_reconciliation = _orphan_reconciliation_for_active_lease(shell_root, payload, lease)
        unbound_active_leases.append(
            {
                "lease_id": lease.get("lease_id"),
                "worker_id": lease.get("worker_id"),
                "agent_id": lease.get("agent_id"),
                "lease_type": lease_type,
                "mode": lease.get("mode") or lease_type,
                "status": lease.get("status") or "ACTIVE",
                "identity_binding_status": lease.get("identity_binding_status"),
                "worker_id_source": lease.get("worker_id_source"),
                "paths": list(lease.get("paths") or []),
                "raw_paths": list(lease.get("raw_paths") or []),
                "created_at": lease.get("created_at"),
                "updated_at": lease.get("updated_at"),
                "last_heartbeat_at": lease.get("last_heartbeat_at"),
                "settlement_required": True,
                "release_requirement": "lawful_release_by_bound_agent_or_operator_override_receipt_required",
                "silent_deletion_allowed": False,
                "orphan_reconciliation": orphan_reconciliation,
            }
        )
    blocked = bool(unbound_active_leases)
    orphan_active_exclusive_write_count = sum(
        1
        for lease in unbound_active_leases
        if isinstance(lease.get("orphan_reconciliation"), Mapping)
        and lease["orphan_reconciliation"].get("exclusive_write_orphan_candidate") is True
    )
    result: dict[str, Any] = {
        "schema_id": UNBOUND_LEASE_SETTLEMENT_SCHEMA_ID,
        "classified_at": timestamp,
        "ok": not blocked,
        "result": "BLOCKED_LIVE_UNBOUND_LEASES" if blocked else "NO_LIVE_UNBOUND_LEASES",
        "reason": reason or "live_worker_shift_unbound_lease_settlement_check",
        "receipt_only": True,
        "no_silent_lease_deletion": True,
        "mutates_active_leases": False,
        "active_lease_count": len(active_leases),
        "unbound_active_lease_count": len(unbound_active_leases),
        "unbound_active_exclusive_write_count": sum(
            1 for lease in unbound_active_leases if lease.get("lease_type") == "exclusive_write"
        ),
        "orphan_active_exclusive_write_count": orphan_active_exclusive_write_count,
        "orphan_reconciliation_schema_id": ORPHAN_LEASE_RECONCILIATION_SCHEMA_ID,
        "readiness_blocked": blocked,
        "settlement_required": blocked,
        "operator_override_required": blocked,
        "authorized_release_required": blocked,
        "required_next_actions": [
            "preserve_active_lease_until_lawful_settlement",
            "record_worker_shift.request_operator_override if operator override is requested",
            "release through worker_shift.release_edit_lease only with matching bound agent proof",
            "rerun classify_live_unbound_leases after settlement",
        ]
        if blocked
        else [],
        "forbidden_actions": [
            "silent_active_lease_deletion",
            "implicit_release_without_receipt",
            "accepted_state_claim_from_classifier",
            "production_or_live_authority_claim",
        ],
        "settlement_routes": {
            "diagnostic": "worker_shift.classify_live_unbound_leases",
            "operator_override_request": "worker_shift.request_operator_override",
            "lawful_release": "worker_shift.release_edit_lease",
            "post_settlement_check": "worker_shift.classify_live_unbound_leases",
        },
        "unbound_active_leases": unbound_active_leases,
        "authority": dict(AUTHORITY_FALSE),
    }
    if write_receipt:
        receipt = {
            **result,
            "receipt_type": "live_unbound_lease_settlement",
            "active_board_path": _rel(_runtime_path(shell_root, ACTIVE_BOARD_PATH), shell_root),
        }
        receipt_path = _runtime_path(
            shell_root,
            WORKER_SHIFT_ROOT / "lease_settlements" / f"{_stamp(timestamp)}_live_unbound_lease_settlement.json",
        )
        _write_json(receipt_path, receipt)
        if board is None:
            _record_receipt(payload, receipt_path, shell_root)
            write_shift_board(payload, shell_root)
        result["receipt_path"] = _rel(receipt_path, shell_root)
    return result


ACTIVE_REQUEST_LEASE_STATUSES = {"ACTIVE", "CLAIMED"}


def _request_rejection(schema_id: str, finding: str, **extra: Any) -> dict[str, Any]:
    return {
        "ok": False,
        "schema_id": schema_id,
        "finding": finding,
        "authority": dict(AUTHORITY_FALSE),
        **extra,
    }


def _target_paths_from_args(args: Mapping[str, Any]) -> list[str]:
    raw = args.get("target_paths")
    if raw is None:
        raw = args.get("paths")
    if isinstance(raw, (str, Path)):
        return _paths([raw])
    return _paths(raw or [])


def _find_referenced_active_lease(
    board: Mapping[str, Any],
    lease_id: str,
) -> tuple[dict[str, Any] | None, str | None, dict[str, Any]]:
    if not lease_id:
        return None, "lease_id_required", {}
    for lease in board.get("active_leases", []):
        if not isinstance(lease, Mapping):
            continue
        if str(lease.get("lease_id") or "").strip() != lease_id:
            continue
        status = str(lease.get("status") or "ACTIVE").strip().upper()
        if status not in ACTIVE_REQUEST_LEASE_STATUSES:
            return None, "stale_lease_reference", {"lease_status": status}
        return dict(lease), None, {"lease_status": status}
    return None, "lease_reference_not_found", {}


def _lease_holder_id(lease: Mapping[str, Any]) -> str:
    return str(lease.get("worker_id") or lease.get("agent_id") or "").strip()


def _lease_target_coverage(lease: Mapping[str, Any], target_paths: Iterable[str]) -> dict[str, Any]:
    lease_paths = [
        str(path).replace("\\", "/").strip()
        for path in list(lease.get("paths") or []) + list(lease.get("raw_paths") or [])
        if str(path or "").strip()
    ]
    missing: list[str] = []
    covered: list[dict[str, str]] = []
    for target in target_paths:
        target_text = str(target).replace("\\", "/").strip()
        matches = [lease_path for lease_path in lease_paths if _path_overlap(lease_path, target_text)]
        if not matches:
            missing.append(target_text)
            continue
        covered.append({"target_path": target_text, "lease_path": matches[0]})
    return {
        "ok": not missing,
        "lease_paths": lease_paths,
        "covered_targets": covered,
        "missing_target_paths": missing,
    }


def _lease_paths_fully_covered_by_targets(lease: Mapping[str, Any], target_paths: Iterable[str]) -> dict[str, Any]:
    lease_paths = [
        str(path).replace("\\", "/").strip()
        for path in list(lease.get("paths") or []) + list(lease.get("raw_paths") or [])
        if str(path or "").strip()
    ]
    normalized_targets = [str(path).replace("\\", "/").strip() for path in target_paths if str(path or "").strip()]
    missing = [
        lease_path
        for lease_path in lease_paths
        if not any(_path_overlap(lease_path, target_path) for target_path in normalized_targets)
    ]
    return {
        "ok": not missing,
        "lease_paths": lease_paths,
        "target_paths": normalized_targets,
        "missing_lease_paths": missing,
    }


def _board_state_counts(board: Mapping[str, Any]) -> dict[str, int]:
    return {
        "active_shift_count": len([item for item in board.get("active_shifts", []) if isinstance(item, Mapping)]),
        "active_lease_count": len([item for item in board.get("active_leases", []) if isinstance(item, Mapping)]),
        "stale_worker_count": len([item for item in board.get("stale_workers", []) if isinstance(item, Mapping)]),
        "recent_signoff_count": len([item for item in board.get("recent_signoffs", []) if isinstance(item, Mapping)]),
        "recent_receipt_count": len([item for item in board.get("recent_receipts", []) if isinstance(item, Mapping)]),
    }


def _receipt_evidence_from_args(args: Mapping[str, Any], evidence: Mapping[str, Any]) -> list[str]:
    values: list[str] = []
    for source in (args, evidence):
        for key in (
            "receipt_evidence",
            "receipt_evidence_paths",
            "receipt_paths",
            "related_receipt_path",
            "source_receipt_path",
            "classification_receipt_path",
            "blocked_finding_receipt_path",
        ):
            raw = source.get(key)
            if isinstance(raw, (str, Path)):
                values.append(str(raw).strip())
            elif isinstance(raw, Iterable) and not isinstance(raw, Mapping):
                values.extend(str(item).strip() for item in raw if str(item or "").strip())
    return sorted({value for value in values if value})


def _blocked_finding_allows_operator_release(blocked_finding: str) -> bool:
    normalized = re.sub(r"[^A-Z0-9]+", "_", str(blocked_finding or "").upper()).strip("_")
    return normalized in {
        "LIVE_UNBOUND_ACTIVE_LEASE",
        "LIVE_UNBOUND_EXCLUSIVE_WRITE_LEASE_BLOCKER",
        "ORPHAN_ACTIVE_EXCLUSIVE_WRITE_BLOCKED",
    }


def _request_root_scope(
    shell_root: Path,
    args: Mapping[str, Any],
) -> tuple[dict[str, Any] | None, str | None, dict[str, Any]]:
    raw_scope = args.get("root_scope")
    if raw_scope is None:
        raw_scope = args.get("active_root")
    if isinstance(raw_scope, Mapping):
        requested = raw_scope.get("active_root") or raw_scope.get("root") or raw_scope.get("path")
        scope_label = str(raw_scope.get("scope") or raw_scope.get("scope_type") or "active_root").strip()
    else:
        requested = raw_scope
        scope_label = "active_root"
    requested_text = str(requested or "").strip()
    if not requested_text:
        return None, "root_scope_required", {}
    if requested_text.lower() in {"active_root", "ion_active_root"}:
        requested_root = shell_root
    else:
        requested_root = Path(requested_text).expanduser().resolve(strict=False)
    if requested_root != shell_root:
        return (
            None,
            "root_scope_mismatch",
            {
                "requested_root_scope": requested_text,
                "active_root": str(shell_root),
            },
        )
    return (
        {
            "scope_type": scope_label or "active_root",
            "requested_root_scope": requested_text,
            "active_root": str(shell_root),
            "active_board_path": _rel(_runtime_path(shell_root, ACTIVE_BOARD_PATH), shell_root),
        },
        None,
        {},
    )


def _identity_markers_from_mapping(identity: Mapping[str, Any]) -> list[str]:
    markers: list[str] = []
    for key in ("identity_binding_status", "worker_id_source", "status", "binding_status"):
        marker = str(identity.get(key) or "").strip()
        if marker:
            markers.append(marker)
    if identity.get("unbound_worker_id") is True:
        markers.append(IDENTITY_UNBOUND_WORKER_ID)
    return markers


def _request_identity_blocker(
    args: Mapping[str, Any],
    roles: Mapping[str, Iterable[str]],
) -> dict[str, Any] | None:
    for role, aliases in roles.items():
        for alias in aliases:
            identity = args.get(f"{alias}_identity")
            markers = _identity_markers_from_mapping(identity) if isinstance(identity, Mapping) else []
            for suffix in ("identity_binding_status", "worker_id_source", "status"):
                value = str(args.get(f"{alias}_{suffix}") or "").strip()
                if value:
                    markers.append(value)
            if alias in {"actor", "agent", "worker"}:
                for suffix in ("identity_binding_status", "worker_id_source"):
                    value = str(args.get(suffix) or "").strip()
                    if value:
                        markers.append(value)
                if args.get("unbound_worker_id") is True:
                    markers.append(IDENTITY_UNBOUND_WORKER_ID)
            for marker in markers:
                token = _identity_status_token(marker)
                if token in BLOCKED_IDENTITY_STATUS_TOKENS:
                    return {
                        "role": role,
                        "identity_marker": marker,
                        "identity_token": token,
                    }
    return None


def _confirmation_value(args: Mapping[str, Any], *keys: str) -> str:
    for key in keys:
        value = str(args.get(key) or "").strip()
        if value:
            return value
    return ""


def request_handoff(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    """Record a lease handoff request without transferring write authority."""

    shell_root = _resolve_root(root)
    timestamp = _now()
    board = load_shift_board(shell_root)
    actor_id = str(args.get("actor_id") or args.get("from_agent_id") or args.get("agent_id") or args.get("worker_id") or "").strip()
    target_holder_id = str(args.get("target_holder_id") or args.get("to_agent_id") or args.get("target_agent_id") or "").strip()
    lease_id = str(args.get("source_lease_id") or args.get("lease_id") or "").strip()
    reason = str(args.get("reason") or args.get("summary") or "").strip()
    target_paths = _target_paths_from_args(args)
    confirmation = _confirmation_value(args, "confirmation", "handoff_confirmation")
    if not actor_id:
        return _request_rejection(HANDOFF_REQUEST_RESULT_SCHEMA_ID, "actor_id_required")
    if not target_holder_id:
        return _request_rejection(HANDOFF_REQUEST_RESULT_SCHEMA_ID, "target_holder_id_required", actor_id=actor_id)
    identity_blocker = _request_identity_blocker(
        args,
        {
            "actor": ("actor", "agent", "worker", "from_agent"),
            "target_holder": ("target_holder", "to_agent", "target_agent"),
        },
    )
    if identity_blocker:
        return _request_rejection(
            HANDOFF_REQUEST_RESULT_SCHEMA_ID,
            "unbound_identity_rejected",
            actor_id=actor_id,
            lease_id=lease_id,
            identity_blocker=identity_blocker,
        )
    if not reason:
        return _request_rejection(HANDOFF_REQUEST_RESULT_SCHEMA_ID, "reason_required", actor_id=actor_id, lease_id=lease_id)
    if not target_paths:
        return _request_rejection(HANDOFF_REQUEST_RESULT_SCHEMA_ID, "target_paths_required", actor_id=actor_id, lease_id=lease_id)
    if confirmation != HANDOFF_CONFIRMATION_MARKER:
        return _request_rejection(
            HANDOFF_REQUEST_RESULT_SCHEMA_ID,
            "handoff_confirmation_required",
            actor_id=actor_id,
            lease_id=lease_id,
            required_confirmation=HANDOFF_CONFIRMATION_MARKER,
        )
    root_scope, root_scope_error, root_scope_extra = _request_root_scope(shell_root, args)
    if root_scope_error:
        return _request_rejection(
            HANDOFF_REQUEST_RESULT_SCHEMA_ID,
            root_scope_error,
            actor_id=actor_id,
            lease_id=lease_id,
            **root_scope_extra,
        )
    active_lease, lease_error, lease_extra = _find_referenced_active_lease(board, lease_id)
    if lease_error:
        return _request_rejection(
            HANDOFF_REQUEST_RESULT_SCHEMA_ID,
            lease_error,
            actor_id=actor_id,
            lease_id=lease_id,
            **lease_extra,
        )
    assert active_lease is not None
    if _lease_identity_binding_blocked(active_lease):
        return _request_rejection(
            HANDOFF_REQUEST_RESULT_SCHEMA_ID,
            "current_holder_identity_unbound",
            actor_id=actor_id,
            lease_id=lease_id,
            current_holder_id=_lease_holder_id(active_lease),
        )
    current_holder_id = _lease_holder_id(active_lease)
    prior_holder_id = str(args.get("prior_holder_id") or args.get("current_holder_id") or args.get("from_agent_id") or current_holder_id).strip()
    if current_holder_id and prior_holder_id and prior_holder_id != current_holder_id:
        return _request_rejection(
            HANDOFF_REQUEST_RESULT_SCHEMA_ID,
            "lease_holder_mismatch",
            actor_id=actor_id,
            lease_id=lease_id,
            prior_holder_id=prior_holder_id,
            current_holder_id=current_holder_id,
        )
    coverage = _lease_target_coverage(active_lease, target_paths)
    if not coverage["ok"]:
        return _request_rejection(
            HANDOFF_REQUEST_RESULT_SCHEMA_ID,
            "missing_target_coverage",
            actor_id=actor_id,
            lease_id=lease_id,
            missing_target_paths=coverage["missing_target_paths"],
            lease_paths=coverage["lease_paths"],
        )
    idempotency_key = str(args.get("idempotency_key") or _hash_short(f"handoff|{actor_id}|{lease_id}|{target_holder_id}|{target_paths}|{reason}")).strip()
    handoff_id = str(args.get("handoff_id") or f"handoff:{idempotency_key}").strip()
    receipt = {
        "schema_id": HANDOFF_REQUEST_RECEIPT_SCHEMA_ID,
        "receipt_type": "edit_lease_handoff_request",
        "created_at": timestamp,
        "handoff_id": handoff_id,
        "request_status": "CANDIDATE_RECORDED",
        "actor_id": actor_id,
        "prior_holder_id": prior_holder_id or current_holder_id,
        "current_holder_id": current_holder_id,
        "target_holder_id": target_holder_id,
        "from_agent_id": prior_holder_id or current_holder_id,
        "to_agent_id": target_holder_id,
        "source_lease_id": lease_id,
        "lease_id": lease_id,
        "target_paths": target_paths,
        "paths": target_paths,
        "target_coverage": coverage,
        "root_scope": root_scope,
        "reason": reason,
        "summary": str(args.get("summary") or reason).strip(),
        "confirmation": confirmation,
        "required_confirmation": HANDOFF_CONFIRMATION_MARKER,
        "idempotency_key": idempotency_key,
        "related_receipt_path": str(args.get("related_receipt_path") or args.get("source_receipt_path") or "").strip() or None,
        "next_baton": str(args.get("next_baton") or "").strip(),
        "authority_transfer": False,
        "lease_transfer_performed": False,
        "active_lease_mutated": False,
        "active_lease_state_preserved": True,
        "recommended_next_call": "worker_shift.request_edit_lease by target agent",
        "authority": dict(AUTHORITY_FALSE),
    }
    receipt_path = _runtime_path(
        shell_root,
        WORKER_SHIFT_ROOT / "handoffs" / f"{_stamp(timestamp)}_{_slug(handoff_id)}.json",
    )
    _write_json(receipt_path, receipt)
    _record_receipt(board, receipt_path, shell_root)
    write_shift_board(board, shell_root)
    return {
        "ok": True,
        "schema_id": HANDOFF_REQUEST_RESULT_SCHEMA_ID,
        "handoff_id": handoff_id,
        "receipt_path": _rel(receipt_path, shell_root),
        "authority_transfer": False,
        "lease_transfer_performed": False,
        "active_lease_mutated": False,
        "current_holder_id": current_holder_id,
        "target_holder_id": target_holder_id,
        "idempotency_key": idempotency_key,
        "authority": dict(AUTHORITY_FALSE),
    }


def request_operator_override(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    """Record an operator override request.

    By default this is receipt-only and does not grant an override. The existing
    orphan-settlement mode remains available only when explicit operator proof,
    root scope, active lease reference, and target coverage gates all pass.
    """

    shell_root = _resolve_root(root)
    timestamp = _now()
    board = load_shift_board(shell_root)
    before_board_state_counts = _board_state_counts(board)
    actor_id = str(args.get("actor_id") or args.get("operator_id") or args.get("agent_id") or args.get("worker_id") or "").strip()
    operator_id = str(args.get("operator_id") or "").strip()
    lease_id = str(args.get("lease_id") or "").strip()
    reason = str(args.get("reason") or "").strip()
    blocked_finding = str(args.get("blocked_finding") or args.get("finding") or "").strip()
    target_paths = _target_paths_from_args(args)
    evidence = args.get("evidence") if isinstance(args.get("evidence"), Mapping) else {}
    receipt_evidence_paths = _receipt_evidence_from_args(args, evidence)
    proof_marker = _confirmation_value(args, "operator_proof_marker", "proof_marker", "confirmation")
    if not proof_marker and isinstance(evidence, Mapping):
        proof_marker = str(evidence.get("operator_proof_marker") or evidence.get("proof_marker") or "").strip()
    if not actor_id:
        return _request_rejection(OPERATOR_OVERRIDE_REQUEST_RESULT_SCHEMA_ID, "actor_id_required")
    identity_blocker = _request_identity_blocker(
        args,
        {
            "actor": ("actor", "agent", "worker", "operator"),
        },
    )
    if identity_blocker:
        return _request_rejection(
            OPERATOR_OVERRIDE_REQUEST_RESULT_SCHEMA_ID,
            "unbound_identity_rejected",
            actor_id=actor_id,
            lease_id=lease_id,
            identity_blocker=identity_blocker,
        )
    if not reason:
        return _request_rejection(OPERATOR_OVERRIDE_REQUEST_RESULT_SCHEMA_ID, "reason_required", actor_id=actor_id, lease_id=lease_id)
    if not blocked_finding:
        return _request_rejection(
            OPERATOR_OVERRIDE_REQUEST_RESULT_SCHEMA_ID,
            "blocked_finding_required",
            actor_id=actor_id,
            lease_id=lease_id,
        )
    if not target_paths:
        return _request_rejection(
            OPERATOR_OVERRIDE_REQUEST_RESULT_SCHEMA_ID,
            "target_paths_required",
            actor_id=actor_id,
            lease_id=lease_id,
        )
    if proof_marker != OPERATOR_OVERRIDE_PROOF_MARKER:
        return _request_rejection(
            OPERATOR_OVERRIDE_REQUEST_RESULT_SCHEMA_ID,
            "operator_proof_marker_required",
            actor_id=actor_id,
            lease_id=lease_id,
            required_operator_proof_marker=OPERATOR_OVERRIDE_PROOF_MARKER,
        )
    root_scope, root_scope_error, root_scope_extra = _request_root_scope(shell_root, args)
    if root_scope_error:
        return _request_rejection(
            OPERATOR_OVERRIDE_REQUEST_RESULT_SCHEMA_ID,
            root_scope_error,
            actor_id=actor_id,
            lease_id=lease_id,
            **root_scope_extra,
        )
    active_lease, lease_error, lease_extra = _find_referenced_active_lease(board, lease_id)
    if lease_error:
        return _request_rejection(
            OPERATOR_OVERRIDE_REQUEST_RESULT_SCHEMA_ID,
            lease_error,
            actor_id=actor_id,
            lease_id=lease_id,
            **lease_extra,
        )
    assert active_lease is not None
    coverage = _lease_target_coverage(active_lease, target_paths)
    if not coverage["ok"]:
        return _request_rejection(
            OPERATOR_OVERRIDE_REQUEST_RESULT_SCHEMA_ID,
            "missing_target_coverage",
            actor_id=actor_id,
            lease_id=lease_id,
            missing_target_paths=coverage["missing_target_paths"],
            lease_paths=coverage["lease_paths"],
        )
    lease_path_coverage = _lease_paths_fully_covered_by_targets(active_lease, target_paths)
    current_holder_id = _lease_holder_id(active_lease)
    requested_current_holder_id = str(args.get("current_holder_id") or args.get("prior_holder_id") or "").strip()
    if requested_current_holder_id and current_holder_id and requested_current_holder_id != current_holder_id:
        return _request_rejection(
            OPERATOR_OVERRIDE_REQUEST_RESULT_SCHEMA_ID,
            "lease_holder_mismatch",
            actor_id=actor_id,
            lease_id=lease_id,
            requested_current_holder_id=requested_current_holder_id,
            current_holder_id=current_holder_id,
        )
    override_action = str(evidence.get("override_action") or args.get("override_action") or "").strip()
    release_orphan_requested = override_action == "release_orphan_unbound_lease"
    explicit_idempotency_key = str(args.get("idempotency_key") or "").strip()
    idempotency_key = explicit_idempotency_key or _hash_short(f"override|{actor_id}|{lease_id}|{target_paths}|{reason}|{blocked_finding}")
    override_id = str(args.get("override_id") or f"override:{idempotency_key}").strip()
    released_leases: list[dict[str, Any]] = []
    operator_override_proof_missing: list[str] = []
    settlement_result = "RECEIPT_ONLY"
    post_settlement: dict[str, Any] | None = None
    override_granted = False
    mutates_active_leases = False
    if release_orphan_requested:
        if not operator_id:
            operator_override_proof_missing.append("operator_id")
        if not explicit_idempotency_key:
            operator_override_proof_missing.append("idempotency_key")
        if not receipt_evidence_paths:
            operator_override_proof_missing.append("receipt_evidence")
        if not _blocked_finding_allows_operator_release(blocked_finding):
            operator_override_proof_missing.append("blocked_finding")
        if not lease_path_coverage["ok"]:
            operator_override_proof_missing.append("target_coverage_for_all_lease_paths")
        if operator_override_proof_missing:
            settlement_result = "BLOCKED_INCOMPLETE_OPERATOR_OVERRIDE_PROOF"
        elif not lease_id:
            settlement_result = "LEASE_ID_REQUIRED"
        else:
            kept: list[dict[str, Any]] = []
            matched = False
            for lease in board.get("active_leases", []):
                if lease.get("lease_id") != lease_id:
                    kept.append(lease)
                    continue
                matched = True
                orphan = _orphan_reconciliation_for_active_lease(shell_root, board, lease)
                if (
                    orphan.get("orphan_candidate") is True
                    and orphan.get("exclusive_write_orphan_candidate") is True
                    and orphan.get("classification") == "ORPHAN_ACTIVE_EXCLUSIVE_WRITE_BLOCKED"
                    and orphan.get("auto_release_allowed") is False
                ):
                    released = dict(lease)
                    released["status"] = "RELEASED_BY_OPERATOR_OVERRIDE"
                    released["released_at"] = timestamp
                    released["release_reason"] = str(args.get("reason") or "operator_override_orphan_lease_settlement").strip()
                    released["operator_override_id"] = override_id
                    released["orphan_reconciliation"] = orphan
                    released_leases.append(released)
                    override_granted = True
                    mutates_active_leases = True
                    settlement_result = "ORPHAN_ACTIVE_LEASE_RELEASED_BY_OPERATOR_OVERRIDE"
                else:
                    kept.append(lease)
                    settlement_result = "LEASE_NOT_ELIGIBLE_FOR_ORPHAN_OVERRIDE"
            if not matched:
                settlement_result = "NO_MATCHING_ACTIVE_LEASE"
            if mutates_active_leases:
                board["active_leases"] = kept
    target_lease_identity_blocked = _lease_identity_binding_blocked(active_lease)
    after_board_state_counts = _board_state_counts(board)
    receipt = {
        "schema_id": OPERATOR_OVERRIDE_REQUEST_RECEIPT_SCHEMA_ID,
        "receipt_type": "operator_override_settlement" if mutates_active_leases else "operator_override_request",
        "created_at": timestamp,
        "override_id": override_id,
        "request_status": "SETTLEMENT_RECORDED" if mutates_active_leases else "CANDIDATE_RECORDED",
        "actor_id": actor_id,
        "operator_id": str(args.get("operator_id") or actor_id).strip(),
        "agent_id": str(args.get("agent_id") or args.get("worker_id") or "").strip() or None,
        "lease_id": lease_id,
        "current_holder_id": current_holder_id,
        "prior_holder_id": str(args.get("prior_holder_id") or current_holder_id).strip(),
        "target_paths": target_paths,
        "paths": target_paths,
        "target_coverage": coverage,
        "lease_path_coverage": lease_path_coverage,
        "root_scope": root_scope,
        "reason": reason,
        "blocked_finding": blocked_finding,
        "blockers_preserved": not mutates_active_leases,
        "target_lease_identity_blocked": target_lease_identity_blocked,
        "live_unbound_lease_preserved": target_lease_identity_blocked and not mutates_active_leases,
        "operator_proof_marker": proof_marker,
        "required_operator_proof_marker": OPERATOR_OVERRIDE_PROOF_MARKER,
        "confirmation": proof_marker,
        "idempotency_key": idempotency_key,
        "related_receipt_path": str(args.get("related_receipt_path") or args.get("source_receipt_path") or "").strip() or None,
        "receipt_evidence_paths": receipt_evidence_paths,
        "evidence": evidence,
        "override_action": override_action,
        "operator_override_proof_complete": not operator_override_proof_missing,
        "operator_override_proof_missing": operator_override_proof_missing,
        "override_granted": override_granted,
        "candidate_request_only": not mutates_active_leases,
        "settlement_result": settlement_result,
        "settlement_explanation": (
            "explicit operator override released classified orphan active exclusive-write lease"
            if mutates_active_leases
            else "candidate request recorded; active lease preserved"
        ),
        "changed_lease_id": lease_id if mutates_active_leases else None,
        "changed_lease_before": active_lease if mutates_active_leases else None,
        "changed_lease_after": released_leases[0] if released_leases else None,
        "before_board_state_counts": before_board_state_counts,
        "after_board_state_counts": after_board_state_counts,
        "released_leases": released_leases,
        "released_lease_count": len(released_leases),
        "mutates_active_leases": mutates_active_leases,
        "active_lease_mutated": mutates_active_leases,
        "active_lease_state_preserved": not mutates_active_leases,
        "non_claims": [
            "no_accepted_state_claim",
            "no_production_authority",
            "no_live_execution_authority",
            "no_secrets_authority",
            "no_git_push_authority",
            "no_deletion_authority",
            "no_materialization_or_registry_movement",
        ],
        "accepted_state_claimed": False,
        "materialization_performed": False,
        "registry_movement_performed": False,
        "production_or_live_authority_claimed": False,
        "authority": dict(AUTHORITY_FALSE),
    }
    receipt_path = _runtime_path(
        shell_root,
        WORKER_SHIFT_ROOT / "operator_overrides" / f"{_stamp(timestamp)}_{_slug(override_id)}.json",
    )
    _write_json(receipt_path, receipt)
    _record_receipt(board, receipt_path, shell_root)
    write_shift_board(board, shell_root)
    if mutates_active_leases:
        post_settlement = classify_live_unbound_leases(
            root=shell_root,
            write_receipt=True,
            reason=f"post_operator_override_settlement:{override_id}",
        )
    return {
        "ok": True,
        "schema_id": OPERATOR_OVERRIDE_REQUEST_RESULT_SCHEMA_ID,
        "override_id": override_id,
        "receipt_path": _rel(receipt_path, shell_root),
        "override_granted": override_granted,
        "candidate_request_only": not mutates_active_leases,
        "settlement_result": settlement_result,
        "released_lease_count": len(released_leases),
        "mutates_active_leases": mutates_active_leases,
        "active_lease_mutated": mutates_active_leases,
        "active_lease_state_preserved": not mutates_active_leases,
        "current_holder_id": current_holder_id,
        "target_lease_identity_blocked": target_lease_identity_blocked,
        "live_unbound_lease_preserved": target_lease_identity_blocked and not mutates_active_leases,
        "idempotency_key": idempotency_key,
        "receipt_evidence_paths": receipt_evidence_paths,
        "operator_override_proof_complete": not operator_override_proof_missing,
        "operator_override_proof_missing": operator_override_proof_missing,
        "before_board_state_counts": before_board_state_counts,
        "after_board_state_counts": after_board_state_counts,
        "post_settlement": post_settlement,
        "authority": dict(AUTHORITY_FALSE),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ION Worker Shift and Presence helper")
    parser.add_argument("--root", default=".", help="ION active root")
    sub = parser.add_subparsers(dest="command", required=True)

    signon = sub.add_parser("signon")
    signon.add_argument("--worker-id")
    signon.add_argument("--true-name", dest="true_name")
    signon.add_argument("--carrier-type", default="codex_cli")
    signon.add_argument("--carrier-instance-id")
    signon.add_argument("--model")
    signon.add_argument("--role-hint")
    signon.add_argument("--domain-hint")
    signon.add_argument("--packet-id")
    signon.add_argument("--objective")
    signon.add_argument("--path", action="append", default=[])

    heartbeat = sub.add_parser("heartbeat")
    heartbeat.add_argument("--worker-id", required=True)
    heartbeat.add_argument("--note")

    lease = sub.add_parser("claim-lease")
    lease.add_argument("--worker-id", required=True)
    lease.add_argument("--lease-id")
    lease.add_argument("--mode", choices=LEASE_TYPES)
    lease.add_argument("--lease-type", choices=LEASE_TYPES)
    lease.add_argument("--path", action="append", required=True)
    lease.add_argument("--objective")
    lease.add_argument("--allow-worker-id-mismatch", action="store_true")

    release = sub.add_parser("release-lease")
    release.add_argument("--worker-id")
    release.add_argument("--lease-id")

    signoff = sub.add_parser("signoff")
    signoff.add_argument("--worker-id", required=True)
    signoff.add_argument("--status", default="RETURNED")
    signoff.add_argument("--work-done")
    signoff.add_argument("--path", action="append", default=[])
    signoff.add_argument("--allow-worker-id-mismatch", action="store_true")

    sub.add_parser("summary")
    sub.add_parser("classify-stale")
    unbound = sub.add_parser("classify-unbound-leases")
    unbound.add_argument("--write-receipt", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "signon":
        declared_worker_id = args.true_name or args.worker_id
        if declared_worker_id:
            result = sign_on(
                declared_worker_id,
                args.carrier_type,
                args.objective or "",
                args.path,
                root=args.root,
                display_callsign=declared_worker_id,
                carrier_instance_id=args.carrier_instance_id,
                model=args.model,
                role_hint=args.role_hint,
                domain_hint=args.domain_hint,
                packet_id=args.packet_id,
            )
        else:
            result = write_signon_receipt(
                root=args.root,
                carrier_type=args.carrier_type,
                carrier_instance_id=args.carrier_instance_id,
                model=args.model,
                role_hint=args.role_hint,
                domain_hint=args.domain_hint,
                packet_id=args.packet_id,
                current_objective=args.objective,
                likely_touched_paths=args.path,
            )
    elif args.command == "heartbeat":
        result = write_heartbeat(root=args.root, worker_id=args.worker_id, note=args.note)
    elif args.command == "claim-lease":
        result = claim_work_lease(
            root=args.root,
            worker_id=args.worker_id,
            lease_id=args.lease_id,
            mode=args.mode,
            lease_type=args.lease_type,
            paths=args.path,
            objective=args.objective,
            allow_worker_id_mismatch=args.allow_worker_id_mismatch,
        )
    elif args.command == "release-lease":
        result = release_work_lease(root=args.root, worker_id=args.worker_id, lease_id=args.lease_id)
    elif args.command == "signoff":
        result = write_signoff_receipt(
            root=args.root,
            worker_id=args.worker_id,
            status=args.status,
            work_done=args.work_done,
            touched_paths=args.path,
            allow_worker_id_mismatch=args.allow_worker_id_mismatch,
        )
    elif args.command == "classify-stale":
        result = classify_stale_workers(root=args.root, write=True)
    elif args.command == "classify-unbound-leases":
        result = classify_live_unbound_leases(root=args.root, write_receipt=args.write_receipt)
    else:
        result = summarize_shift_board(root=args.root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
