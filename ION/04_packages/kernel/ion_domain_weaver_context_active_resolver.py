"""No-write active context resolver for Domain Weaver.

This helper answers one question: which active context package should a domain
or role use right now? It reads local mount evidence only. It does not start
workers, mutate registries, materialize topology, or claim accepted state.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_domain_weaver_semantic_ids import canonicalize_codex_mount_identity

SCHEMA_ID = "ion.domain_weaver.context_active_resolver.v0_2_candidate"
DEFAULT_MAX_CONTEXT_AGE_SECONDS = 48 * 60 * 60
ACTIVE_CONTEXT_REISSUE_PREFLIGHT_PACKET_ID = "PCKT-DOMAIN-WEAVER-ACTIVE-CONTEXT-REISSUE-PREFLIGHT-AND-GATED-REFRESH-V0_1"
ACTIVE_CONTEXT_GATED_REFRESH_PACKET_ID = "PCKT-DOMAIN-WEAVER-ACTIVE-CONTEXT-GATED-REFRESH-V0_1"
ACTIVE_CONTEXT_GATED_REFRESH_SCHEMA_ID = "ion.domain_weaver.active_context.gated_refresh.v0_1_candidate"
ACTIVE_CONTEXT_REFRESH_APPLY_SCHEMA_ID = "ion.domain_weaver.active_context.gated_refresh_apply.v0_1_candidate"
ACTIVE_CONTEXT_REFRESH_APPLY_RECEIPT_SCHEMA_ID = "ion.domain_weaver.active_context.gated_refresh_apply_receipt.v0_1"
BOUNDED_WRITE_CONFIRMATION = "ION_BOUNDED_WRITE_CONFIRMED"
ACTIVE_CONTEXT_REFRESH_PROOF_FIELDS = (
    "confirmation",
    "idempotency_key",
    "agent_id",
    "lease_id",
    "lease_type=exclusive_write",
    "lease_proof.ok_or_active",
    "lease_proof.agent_id",
    "lease_proof.lease_id",
    "lease_proof.lease_type=exclusive_write",
    "lease_proof.target_paths",
)
CODEX_AGENT_MOUNTS = Path("ION/05_context/current/codex_agent_mounts")
CODEX_SOLO_DIR = Path("ION/05_context/current/codex_solo")
CODEX_SOLO_CONTEXT_PACKAGES = CODEX_SOLO_DIR / "CONTEXT_PACKAGES.json"
CODEX_SOLO_BOOT_REFS = (
    CODEX_SOLO_DIR / "CAPSULE.md",
    CODEX_SOLO_DIR / "MINI.md",
    CODEX_SOLO_DIR / "HOT_CONTEXT.md",
    CODEX_SOLO_DIR / "LONG_HORIZON.json",
    CODEX_SOLO_DIR / "ROUTE.json",
    CODEX_SOLO_DIR / "STATUS.json",
    CODEX_SOLO_CONTEXT_PACKAGES,
)
ROOT_PROOF_REQUIRED_REFS = (
    Path("pyproject.toml"),
    Path("ION/REPO_AUTHORITY.md"),
)
READ_FIRST_FILES = (
    "ION_CONTEXT_CAPSULE.yaml",
    "ACTIVE_CONTEXT_PACKAGE.md",
    "ACTIVE_CONTEXT_PACKAGE.json",
    "AGENT.yaml",
    "DOMAIN.yaml",
    "RELATIONSHIPS.yaml",
    "COMMUNICATIONS.json",
    "ADDRESS_BOOK.json",
)
LAUNCH_REQUIRED_TOP_FILES = ("ION_AGENT_MOUNT_MANIFEST.json",)
LAUNCH_REQUIRED_ION_FILES = READ_FIRST_FILES + ("CONTEXT_IDENTITY.json",)


def _authority() -> dict[str, bool]:
    return {
        "accepted_state": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "materialization_write_authority": False,
    }


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return list(value)
    return []


def _unique_texts(values: list[Any]) -> list[str]:
    seen: set[str] = set()
    rows: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        rows.append(text)
    return rows


def _load_refresh_preflight(preflight: Mapping[str, Any] | str | Path) -> tuple[dict[str, Any], list[str]]:
    if isinstance(preflight, Mapping):
        return dict(preflight), []
    path = Path(preflight).expanduser()
    payload, finding = _read_json_mapping(path)
    if payload is None:
        return {}, [f"active_context_refresh_preflight_{finding}"]
    return dict(payload), []


def _required_refresh_target_paths(preflight: Mapping[str, Any]) -> list[str]:
    exact_refs = _required_refresh_target_refs(preflight)
    if exact_refs:
        return _unique_texts([ref.get("path") for ref in exact_refs])
    paths: list[Any] = []
    for lease in _as_list(preflight.get("gated_refresh_required_leases")):
        if isinstance(lease, Mapping):
            paths.extend(_as_list(lease.get("target_paths")))
    for target in _as_list(preflight.get("target_mounts")):
        if not isinstance(target, Mapping):
            continue
        for lease in _as_list(target.get("required_refresh_leases")):
            if isinstance(lease, Mapping):
                paths.extend(_as_list(lease.get("target_paths")))
    return _unique_texts(paths)


def _required_refresh_target_refs(preflight: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for ref in _as_list(preflight.get("mount_package_refs_requiring_reissue")):
        if not isinstance(ref, Mapping):
            continue
        path = str(ref.get("path") or "").strip()
        if not path or path in seen:
            continue
        seen.add(path)
        rows.append({
            "path": path,
            "mount_id": str(ref.get("mount_id") or "").strip(),
            "reason": str(ref.get("reason") or "active_context_package_requires_reissue").strip(),
            "source": str(ref.get("source") or "mount_package_refs_requiring_reissue").strip(),
        })
    for target in _as_list(preflight.get("target_mounts")):
        if not isinstance(target, Mapping):
            continue
        for ref in _as_list(target.get("active_context_package_refs_requiring_refresh")):
            if not isinstance(ref, Mapping):
                continue
            path = str(ref.get("path") or "").strip()
            if not path or path in seen:
                continue
            seen.add(path)
            rows.append({
                "path": path,
                "mount_id": str(ref.get("mount_id") or target.get("mount_id") or "").strip(),
                "reason": str(ref.get("reason") or "active_context_package_requires_reissue").strip(),
                "source": "target_mount_active_context_package_ref",
            })
    return rows


def _preflight_target_mount_ids(preflight: Mapping[str, Any]) -> list[str]:
    return _unique_texts([
        target.get("mount_id")
        for target in _as_list(preflight.get("target_mounts"))
        if isinstance(target, Mapping)
    ])


def _identity_is_unbound(value: Any) -> bool:
    normalized = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    return normalized in {"", "anonymous", "none", "null", "unknown", "unbound", "unbound_worker_id"}


def _lease_proof_targets(lease_proof: Mapping[str, Any] | None, lease_target_paths: list[str] | None) -> list[str]:
    paths: list[Any] = []
    if lease_target_paths:
        paths.extend(lease_target_paths)
    if isinstance(lease_proof, Mapping):
        paths.extend(_as_list(lease_proof.get("target_paths")))
        paths.extend(_as_list(lease_proof.get("paths")))
        paths.extend(_as_list(lease_proof.get("raw_paths")))
    return _unique_texts(paths)


def derive_active_context_refresh_target_coverage(
    preflight: Mapping[str, Any] | str | Path,
    *,
    lease_target_paths: list[str] | None = None,
    lease_proof: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Derive exact gated-refresh lease target coverage from preflight evidence.

    Stale or missing active-context package refs are the primary source of
    truth. Existing lease target paths are used only as compatibility fallback
    for older preflight artifacts that did not preserve per-ref rows.
    """

    preflight_result, blockers = _load_refresh_preflight(preflight)
    required_refs = _required_refresh_target_refs(preflight_result)
    required_paths = _required_refresh_target_paths(preflight_result)
    provided_paths = _lease_proof_targets(lease_proof, lease_target_paths)
    provided_set = set(provided_paths)
    missing_paths = [path for path in required_paths if path not in provided_set]
    coverage_blockers: list[str] = list(blockers)
    if not required_paths:
        coverage_blockers.append("active_context_refresh_target_paths_required")
    if missing_paths:
        coverage_blockers.append("active_context_refresh_lease_target_coverage_incomplete")
    return {
        "schema_id": "ion.domain_weaver.active_context.refresh_target_coverage.v0_1",
        "required_target_paths": required_paths,
        "required_target_count": len(required_paths),
        "required_target_refs": required_refs,
        "provided_target_paths": provided_paths,
        "provided_target_count": len(provided_paths),
        "missing_target_paths": missing_paths,
        "missing_target_count": len(missing_paths),
        "target_coverage_ok": bool(required_paths) and not missing_paths,
        "proof_fields_required": list(ACTIVE_CONTEXT_REFRESH_PROOF_FIELDS),
        "proof_requirements": {
            "lease_target_coverage_rule": "lease_proof.target_paths or lease_target_paths must cover every required_target_path",
            "target_source_preference": [
                "mount_package_refs_requiring_reissue",
                "target_mounts.active_context_package_refs_requiring_refresh",
                "gated_refresh_required_leases.target_paths",
                "target_mounts.required_refresh_leases.target_paths",
            ],
            "refresh_execution_allowed_by_this_function": False,
        },
        "blockers": _unique_texts(coverage_blockers),
        "authority": _authority(),
    }


def _same_resolved_root(left: str | Path, right: str | Path) -> bool:
    return Path(left).expanduser().resolve(strict=False) == Path(right).expanduser().resolve(strict=False)


def _public_worker_shift_gate(gate: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(gate, Mapping):
        return {}
    return {
        str(key): value
        for key, value in gate.items()
        if key not in {"active_lease"}
    }


def _live_lease_blockers(gate: Mapping[str, Any] | None) -> list[str]:
    if not isinstance(gate, Mapping):
        return ["active_context_refresh_live_lease_gate_missing"]
    if gate.get("ok") is True:
        return []
    blockers: list[str] = []
    finding = str(gate.get("finding") or "").strip()
    if finding == "active_context_refresh_live_lease_root_required":
        blockers.append("active_context_refresh_live_lease_root_required")
    elif finding == "active_context_refresh_live_lease_root_mismatch":
        blockers.append("active_context_refresh_live_lease_root_mismatch")
    elif finding == "active_context_refresh_live_lease_gate_unavailable":
        blockers.append("active_context_refresh_live_lease_gate_unavailable")
    elif finding == "active_edit_lease_not_found":
        blockers.extend([
            "active_context_refresh_live_lease_not_found",
            "active_context_refresh_live_lease_wrong_root_or_absent",
        ])
    elif finding == "active_edit_lease_invalid":
        blockers.append("active_context_refresh_live_lease_invalid")
    elif finding:
        blockers.append(f"active_context_refresh_{finding}")
    for blocker in _as_list(gate.get("blockers")):
        text = str(blocker or "").strip()
        if text == "lease_agent_mismatch":
            blockers.append("active_context_refresh_live_lease_actor_mismatch")
        elif text == "lease_type_mismatch":
            blockers.append("active_context_refresh_live_lease_mode_mismatch")
        elif text == "lease_missing_target_coverage":
            blockers.append("active_context_refresh_live_lease_target_coverage_incomplete")
        elif text == "lease_not_fresh":
            blockers.append("active_context_refresh_live_lease_stale")
        elif text == "lease_identity_binding_blocked":
            blockers.append("active_context_refresh_live_lease_identity_blocked")
    if gate.get("ok") is not True and not blockers:
        blockers.append("active_context_refresh_live_lease_gate_failed")
    return _unique_texts(blockers)


def _worker_shift_live_lease_gate(
    root: str | Path | None,
    preflight: Mapping[str, Any],
    *,
    agent_id: str,
    lease_id: str,
    required_paths: list[str],
) -> dict[str, Any]:
    preflight_root = str(preflight.get("active_root") or "").strip()
    root_blockers: list[str] = []
    if root is None:
        if preflight_root:
            live_root = Path(preflight_root).expanduser().resolve(strict=False)
        else:
            live_root = None
            root_blockers.append("active_context_refresh_live_lease_root_required")
    else:
        live_root = Path(root).expanduser().resolve(strict=False)
        if preflight_root and not _same_resolved_root(live_root, preflight_root):
            root_blockers.append("active_context_refresh_live_lease_root_mismatch")
    if root_blockers:
        return {
            "schema_id": "ion.domain_weaver.active_context.worker_shift_live_lease_gate.v0_1",
            "ok": False,
            "finding": root_blockers[0],
            "active_root": live_root.as_posix() if live_root is not None else "",
            "preflight_active_root": preflight_root,
            "required_target_paths": required_paths,
            "worker_shift_gate": {},
            "blockers": root_blockers,
            "authority": _authority(),
        }
    live_input_blockers: list[str] = []
    if _identity_is_unbound(agent_id):
        live_input_blockers.append("active_context_refresh_actor_identity_required")
    if not str(lease_id or "").strip():
        live_input_blockers.append("active_context_refresh_lease_id_required")
    if not required_paths:
        live_input_blockers.append("active_context_refresh_target_paths_required")
    if live_input_blockers:
        return {
            "schema_id": "ion.domain_weaver.active_context.worker_shift_live_lease_gate.v0_1",
            "ok": False,
            "finding": live_input_blockers[0],
            "active_root": live_root.as_posix() if live_root is not None else "",
            "preflight_active_root": preflight_root,
            "required_target_paths": required_paths,
            "worker_shift_gate": {},
            "blockers": live_input_blockers,
            "authority": _authority(),
        }
    try:
        from .ion_worker_shift_presence import require_active_edit_lease
    except Exception as exc:  # pragma: no cover - fail-closed import guard
        return {
            "schema_id": "ion.domain_weaver.active_context.worker_shift_live_lease_gate.v0_1",
            "ok": False,
            "finding": "active_context_refresh_live_lease_gate_unavailable",
            "active_root": live_root.as_posix() if live_root is not None else "",
            "preflight_active_root": preflight_root,
            "required_target_paths": required_paths,
            "error_type": type(exc).__name__,
            "worker_shift_gate": {},
            "blockers": ["active_context_refresh_live_lease_gate_unavailable"],
            "authority": _authority(),
        }
    gate = require_active_edit_lease(
        live_root,
        agent_id=agent_id,
        lease_id=lease_id,
        target_files=required_paths,
        required_mode="exclusive_write",
    )
    public_gate = _public_worker_shift_gate(gate)
    blockers = _live_lease_blockers(public_gate)
    return {
        "schema_id": "ion.domain_weaver.active_context.worker_shift_live_lease_gate.v0_1",
        "ok": bool(public_gate.get("ok")),
        "finding": public_gate.get("finding"),
        "active_root": live_root.as_posix() if live_root is not None else "",
        "preflight_active_root": preflight_root,
        "required_target_paths": required_paths,
        "worker_shift_gate": public_gate,
        "blockers": blockers,
        "authority": _authority(),
    }


def build_active_context_gated_refresh_plan(
    preflight: Mapping[str, Any] | str | Path,
    *,
    root: str | Path | None = None,
    confirmation: str = "",
    idempotency_key: str = "",
    agent_id: str = "",
    lease_id: str = "",
    lease_type: str = "",
    lease_target_paths: list[str] | None = None,
    lease_proof: Mapping[str, Any] | None = None,
    preview_only: bool = True,
    allow_write: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build a gated active-context refresh plan without mutating packages.

    This is the lawful bridge between Boole's no-write preflight and any future
    active-context package refresh. It validates explicit operator/actor/lease
    proof and returns a receipt-grade plan. The active write path is intentionally
    not implemented here; non-preview execution remains blocked.
    """

    now = now or datetime.now(timezone.utc)
    generated_at = now.isoformat()
    preflight_result, blockers = _load_refresh_preflight(preflight)
    target_coverage = derive_active_context_refresh_target_coverage(
        preflight_result,
        lease_target_paths=lease_target_paths,
        lease_proof=lease_proof,
    )
    required_paths = list(target_coverage.get("required_target_paths") or [])
    provided_paths = list(target_coverage.get("provided_target_paths") or [])
    missing_lease_targets = list(target_coverage.get("missing_target_paths") or [])
    requested_write = bool(allow_write) or preview_only is False
    preview_diagnostic_only = bool(preview_only)
    live_lease_gate: dict[str, Any] | None = None
    if requested_write:
        live_lease_gate = _worker_shift_live_lease_gate(
            root,
            preflight_result,
            agent_id=str(agent_id or "").strip(),
            lease_id=str(lease_id or "").strip(),
            required_paths=required_paths,
        )
        worker_shift_gate = live_lease_gate.get("worker_shift_gate") if isinstance(live_lease_gate, Mapping) else {}
        live_lease_paths = _unique_texts(_as_list(worker_shift_gate.get("lease_paths")) if isinstance(worker_shift_gate, Mapping) else [])
        live_missing_target_rows = [
            row for row in _as_list(worker_shift_gate.get("missing_targets")) if isinstance(row, Mapping)
        ] if isinstance(worker_shift_gate, Mapping) else []
        live_missing_paths = _unique_texts([row.get("path") for row in live_missing_target_rows])
        provided_paths = live_lease_paths
        if live_missing_paths:
            missing_lease_targets = live_missing_paths
        elif live_lease_gate.get("ok") is True:
            missing_lease_targets = []
        elif required_paths and not live_lease_paths:
            missing_lease_targets = required_paths
        coverage_blockers = [
            str(blocker)
            for blocker in _as_list(target_coverage.get("blockers"))
            if str(blocker) != "active_context_refresh_lease_target_coverage_incomplete"
        ]
        coverage_blockers.extend(_as_list(live_lease_gate.get("blockers")))
        if missing_lease_targets:
            coverage_blockers.append("active_context_refresh_live_lease_target_coverage_incomplete")
        target_coverage = {
            **target_coverage,
            "provided_target_paths": provided_paths,
            "provided_target_count": len(provided_paths),
            "missing_target_paths": missing_lease_targets,
            "missing_target_count": len(missing_lease_targets),
            "target_coverage_ok": bool(required_paths) and bool(live_lease_gate.get("ok")),
            "lease_evidence_source": "worker_shift.require_active_edit_lease",
            "worker_shift_live_lease_gate": live_lease_gate,
            "blockers": _unique_texts(coverage_blockers),
        }

    gate_blockers: list[str] = list(blockers)
    if not preflight_result:
        gate_blockers.append("active_context_refresh_preflight_required")
    if preflight_result and preflight_result.get("preflight_completed") is not True:
        gate_blockers.append("active_context_refresh_preflight_not_completed")
    if preflight_result and preflight_result.get("refresh_run") is True:
        gate_blockers.append("active_context_refresh_preflight_must_be_no_write")
    if preflight_result and preflight_result.get("mutates_active_state") is True:
        gate_blockers.append("active_context_refresh_preflight_mutated_active_state")
    if not required_paths:
        gate_blockers.append("active_context_refresh_target_paths_required")
    if confirmation != BOUNDED_WRITE_CONFIRMATION:
        gate_blockers.append("active_context_refresh_confirmation_required")
    if not str(idempotency_key or "").strip():
        gate_blockers.append("active_context_refresh_idempotency_key_required")
    if _identity_is_unbound(agent_id):
        gate_blockers.append("active_context_refresh_actor_identity_required")
    if not str(lease_id or "").strip():
        gate_blockers.append("active_context_refresh_lease_id_required")
    if (not requested_write and str(lease_type or "").strip() != "exclusive_write") or (
        requested_write and str(lease_type or "").strip() not in {"", "exclusive_write"}
    ):
        gate_blockers.append("active_context_refresh_exclusive_write_lease_required")
    if requested_write:
        if isinstance(live_lease_gate, Mapping):
            gate_blockers.extend(_as_list(live_lease_gate.get("blockers")))
        else:
            gate_blockers.append("active_context_refresh_live_lease_gate_missing")
    elif not isinstance(lease_proof, Mapping):
        gate_blockers.append("active_context_refresh_lease_proof_required")
    else:
        proof_id = str(lease_proof.get("lease_id") or "").strip()
        proof_actor = str(lease_proof.get("agent_id") or lease_proof.get("actor_id") or "").strip()
        proof_type = str(lease_proof.get("lease_type") or "").strip()
        proof_active = (
            lease_proof.get("ok") is True
            or lease_proof.get("active") is True
            or lease_proof.get("lease_active") is True
        )
        if proof_id and proof_id != lease_id:
            gate_blockers.append("active_context_refresh_lease_id_mismatch")
        if proof_actor and proof_actor != agent_id:
            gate_blockers.append("active_context_refresh_actor_identity_mismatch")
        if proof_type and proof_type != "exclusive_write":
            gate_blockers.append("active_context_refresh_lease_proof_not_exclusive_write")
        if not proof_active:
            gate_blockers.append("active_context_refresh_lease_proof_not_active")
    if missing_lease_targets and not requested_write:
        gate_blockers.append("active_context_refresh_lease_target_coverage_incomplete")

    write_blockers: list[str] = []
    if requested_write:
        write_blockers.append("active_context_refresh_write_path_not_implemented")
    all_gate_blockers = _unique_texts(gate_blockers)
    write_blockers = _unique_texts(write_blockers)
    live_worker_shift_gate_checked = bool(requested_write)
    write_gate_passed = bool(requested_write and not all_gate_blockers)
    write_authority_granted = bool(write_gate_passed and not write_blockers)
    non_preview_refresh_allowed = False
    preview_gate_inputs_valid = bool(preview_diagnostic_only and not all_gate_blockers)
    result_blockers = list(all_gate_blockers) + write_blockers
    if preview_diagnostic_only:
        result_blockers.append("active_context_refresh_preview_diagnostic_only_not_write_authority")
        result_blockers.append("active_context_refresh_preview_only_not_run")
    result_blockers = _unique_texts(result_blockers)

    preflight_blockers = _unique_texts(_as_list(preflight_result.get("blockers"))) if preflight_result else []
    target_mount_ids = _preflight_target_mount_ids(preflight_result)
    diagnostic_target_coverage_ok = bool(target_coverage.get("target_coverage_ok"))
    target_coverage = {
        **target_coverage,
        "diagnostic_target_coverage_ok": diagnostic_target_coverage_ok,
        "preview_diagnostic_only": preview_diagnostic_only,
        "self_attested_preview_evidence": bool(preview_diagnostic_only and isinstance(lease_proof, Mapping)),
        "write_authority_granted": write_authority_granted,
        "live_worker_shift_gate_checked": live_worker_shift_gate_checked,
        "non_preview_refresh_allowed": non_preview_refresh_allowed,
        "readiness_claimed": False,
    }
    if preview_diagnostic_only:
        target_coverage["target_coverage_ok"] = False
        target_coverage["lease_evidence_source"] = "caller_supplied_preview_lease_proof_diagnostic_only"
    return {
        "schema_id": ACTIVE_CONTEXT_GATED_REFRESH_SCHEMA_ID,
        "packet_id": ACTIVE_CONTEXT_GATED_REFRESH_PACKET_ID,
        "preflight_packet_id": ACTIVE_CONTEXT_REISSUE_PREFLIGHT_PACKET_ID,
        "generated_at": generated_at,
        "ok": write_authority_granted,
        "write_gate_passed": write_gate_passed,
        "preview_only": bool(preview_only),
        "preview_plan_generated": bool(preview_diagnostic_only and preflight_result),
        "preview_inputs_valid": preview_gate_inputs_valid,
        "preview_diagnostic_only": preview_diagnostic_only,
        "write_authority_granted": write_authority_granted,
        "live_worker_shift_gate_checked": live_worker_shift_gate_checked,
        "non_preview_refresh_allowed": non_preview_refresh_allowed,
        "readiness_claimed": False,
        "allow_write_requested": bool(allow_write),
        "refresh_run": False,
        "refresh_allowed_now": False,
        "mutates_active_state": False,
        "authority": _authority(),
        "materialize_all_guard": {
            "materialize_all_allowed": False,
            "finding": "materialize_all_blocked_for_active_context_gated_refresh",
            "forbidden_actions": [
                "materialize_all",
                "registry_materialization_movement",
                "topology_resume",
                "ui_resume",
            ],
            "blockers": ["materialize_all_forbidden_in_gated_refresh_packet"],
        },
        "actor": {
            "agent_id": str(agent_id or "").strip(),
            "actor_identity_bound": not _identity_is_unbound(agent_id),
        },
        "idempotency_key": str(idempotency_key or "").strip(),
        "confirmation": {
            "provided": confirmation,
            "required": BOUNDED_WRITE_CONFIRMATION,
            "ok": confirmation == BOUNDED_WRITE_CONFIRMATION,
        },
        "lease_gate": {
            "lease_id": str(lease_id or "").strip(),
            "lease_type": str(lease_type or "").strip(),
            "required_lease_type": "exclusive_write",
            "proof_present": isinstance(lease_proof, Mapping),
            "preview_diagnostic_only": preview_diagnostic_only,
            "self_attested_preview_evidence": bool(preview_diagnostic_only and isinstance(lease_proof, Mapping)),
            "write_authority_granted": write_authority_granted,
            "live_worker_shift_gate_checked": live_worker_shift_gate_checked,
            "non_preview_refresh_allowed": non_preview_refresh_allowed,
            "readiness_claimed": False,
            "lease_evidence_source": (
                "worker_shift.require_active_edit_lease"
                if requested_write
                else "caller_supplied_preview_lease_proof_diagnostic_only"
            ),
            "worker_shift_live_lease_required": requested_write,
            "worker_shift_live_lease_gate": live_lease_gate,
            "caller_supplied_lease_proof_scope": (
                "preview_diagnostics_only_not_write_authority"
                if requested_write
                else "preview_diagnostics_only_not_write_authority"
            ),
            "provided_target_paths": provided_paths,
            "provided_target_count": len(provided_paths),
            "required_target_paths": required_paths,
            "required_target_count": len(required_paths),
            "missing_target_paths": missing_lease_targets,
            "missing_target_count": len(missing_lease_targets),
            "target_coverage_ok": (
                bool(live_lease_gate.get("ok")) and bool(required_paths)
                if isinstance(live_lease_gate, Mapping)
                else not missing_lease_targets and bool(required_paths) and not preview_diagnostic_only
            ),
            "diagnostic_target_coverage_ok": diagnostic_target_coverage_ok,
        },
        "target_coverage": target_coverage,
        "proof_requirements": {
            "required_fields": list(ACTIVE_CONTEXT_REFRESH_PROOF_FIELDS),
            "target_coverage_rule": "provided lease target paths must cover every stale or missing active-context package ref",
            "preview_only_default": True,
            "preview_lease_proof_scope": "diagnostic_self_attested_only_not_write_authority",
            "preview_proof_can_pass_write_gate": False,
            "live_worker_shift_gate_required_for_non_preview": True,
            "non_preview_lease_gate": "worker_shift.require_active_edit_lease",
            "refresh_execution_allowed": False,
            "non_preview_refresh_allowed": non_preview_refresh_allowed,
        },
        "preflight_summary": {
            "preflight_completed": preflight_result.get("preflight_completed") is True,
            "preflight_refresh_run": preflight_result.get("refresh_run") is True,
            "preflight_mutates_active_state": preflight_result.get("mutates_active_state") is True,
            "target_mount_count": len(target_mount_ids),
            "target_mount_ids": target_mount_ids,
            "stale_ref_count": len(_as_list(preflight_result.get("stale_package_refs"))),
            "missing_ref_count": len(_as_list(preflight_result.get("missing_package_refs"))),
            "preflight_blockers_preserved": preflight_blockers,
        },
        "refresh_plan": {
            "schema_id": "ion.domain_weaver.active_context.refresh_plan.v0_1",
            "operation": "active_context_reissue_preview",
            "generated_at": generated_at,
            "target_mount_count": len(target_mount_ids),
            "target_mount_ids": target_mount_ids,
            "would_write_paths": required_paths,
            "write_strategy": "not_implemented_in_this_packet",
            "requires_separate_write_implementation": True,
            "rollback_required_before_write": True,
            "receipt_required_after_write": True,
            "write_authority_granted": write_authority_granted,
            "non_preview_refresh_allowed": non_preview_refresh_allowed,
            "readiness_claimed": False,
        },
        "receipt": {
            "schema_id": "ion.domain_weaver.active_context.gated_refresh_receipt.v0_1",
            "generated_at": generated_at,
            "result": "preview_diagnostic_only" if preview_diagnostic_only else "write_blocked",
            "agent_id": str(agent_id or "").strip(),
            "idempotency_key": str(idempotency_key or "").strip(),
            "lease_id": str(lease_id or "").strip(),
            "write_gate_passed": write_gate_passed,
            "preview_diagnostic_only": preview_diagnostic_only,
            "write_authority_granted": write_authority_granted,
            "live_worker_shift_gate_checked": live_worker_shift_gate_checked,
            "non_preview_refresh_allowed": non_preview_refresh_allowed,
            "readiness_claimed": False,
            "target_coverage_ok": (
                bool(live_lease_gate.get("ok")) and bool(required_paths)
                if isinstance(live_lease_gate, Mapping)
                else not missing_lease_targets and bool(required_paths) and not preview_diagnostic_only
            ),
            "diagnostic_target_coverage_ok": diagnostic_target_coverage_ok,
            "refresh_run": False,
            "mutates_active_state": False,
            "blockers": result_blockers,
        },
        "blockers": result_blockers,
        "next_action": (
            "preserve_preview_diagnostic_receipt_no_refresh"
            if preview_gate_inputs_valid
            else "repair_refresh_gate_inputs"
            if all_gate_blockers
            else "implement_separate_active_context_refresh_write_path"
        ),
    }


def apply_active_context_gated_refresh(
    preflight: Mapping[str, Any] | str | Path,
    *,
    root: str | Path | None,
    confirmation: str,
    idempotency_key: str,
    agent_id: str,
    lease_id: str,
    lease_type: str = "exclusive_write",
    execute_write: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Apply a bounded active-context package refresh after live lease proof.

    This is intentionally separate from the read-only Branch Gateway route. It
    writes only active-context package files listed by preflight evidence and
    only after the existing non-preview gate passes with a live Worker Shift
    exclusive-write lease. It does not alter projections, registries, topology,
    Codex Solo, production, live execution, secrets, or accepted state.
    """

    shell_root = Path(root or ".").expanduser().resolve(strict=False)
    now = now or datetime.now(timezone.utc)
    generated_at = now.isoformat()
    preflight_result, load_blockers = _load_refresh_preflight(preflight)
    gate = build_active_context_gated_refresh_plan(
        preflight_result,
        root=shell_root,
        confirmation=confirmation,
        idempotency_key=idempotency_key,
        agent_id=agent_id,
        lease_id=lease_id,
        lease_type=lease_type,
        preview_only=False,
        allow_write=True,
        now=now,
    )
    target_rows, target_blockers = _active_context_refresh_apply_targets(shell_root, preflight_result)
    blockers = _unique_texts(
        list(load_blockers)
        + target_blockers
        + ([] if gate.get("write_gate_passed") is True else _as_list(gate.get("blockers")))
    )
    if not execute_write:
        blockers.append("active_context_refresh_execute_write_required")
    if not idempotency_key.strip():
        blockers.append("active_context_refresh_idempotency_key_required")
    if blockers:
        return {
            "schema_id": ACTIVE_CONTEXT_REFRESH_APPLY_SCHEMA_ID,
            "packet_id": ACTIVE_CONTEXT_GATED_REFRESH_PACKET_ID,
            "generated_at": generated_at,
            "ok": False,
            "refresh_run": False,
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
            "active_root": shell_root.as_posix(),
            "gate": gate,
            "target_count": len(target_rows),
            "targets": target_rows,
            "blockers": _unique_texts(blockers),
            "next_action": "repair_active_context_refresh_apply_inputs",
            "authority": _authority(),
        }

    writes: list[dict[str, Any]] = []
    for row in target_rows:
        target = shell_root / str(row["path"])
        before = _file_digest_row(target)
        content = _active_context_refresh_target_content(
            row,
            preflight_result=preflight_result,
            generated_at=generated_at,
            agent_id=agent_id,
            lease_id=lease_id,
            idempotency_key=idempotency_key,
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write_text(target, content)
        after = _file_digest_row(target)
        writes.append({
            **row,
            "before": before,
            "after": after,
            "changed": before.get("sha256") != after.get("sha256"),
        })

    receipt = {
        "schema_id": ACTIVE_CONTEXT_REFRESH_APPLY_RECEIPT_SCHEMA_ID,
        "generated_at": generated_at,
        "result": "active_context_refresh_applied_candidate_only",
        "active_root": shell_root.as_posix(),
        "agent_id": agent_id,
        "lease_id": lease_id,
        "idempotency_key": idempotency_key,
        "target_count": len(writes),
        "targets": writes,
        "gate_write_gate_passed": gate.get("write_gate_passed") is True,
        "refresh_run": True,
        "mutates_active_state": True,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "authority": _authority(),
        "non_claims": [
            "This receipt updates active-context package files only.",
            "It does not move accepted projection, registry, materialization, topology, UI, production, live, secrets, or git state.",
            "It does not start workers or process queues.",
        ],
    }
    receipt_path = _active_context_refresh_receipt_path(shell_root, generated_at, idempotency_key)
    _write_json_atomic(receipt_path, receipt)
    return {
        "schema_id": ACTIVE_CONTEXT_REFRESH_APPLY_SCHEMA_ID,
        "packet_id": ACTIVE_CONTEXT_GATED_REFRESH_PACKET_ID,
        "generated_at": generated_at,
        "ok": True,
        "refresh_run": True,
        "mutates_active_state": True,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "active_root": shell_root.as_posix(),
        "gate": gate,
        "target_count": len(writes),
        "targets": writes,
        "receipt_path": _rel(receipt_path, shell_root),
        "blockers": [],
        "next_action": "run_active_context_reissue_preflight_and_fanin_settlement",
        "authority": _authority(),
    }


def _active_context_refresh_apply_targets(
    root: Path,
    preflight: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    target_mounts = {
        str(row.get("mount_id") or ""): row
        for row in _as_list(preflight.get("target_mounts"))
        if isinstance(row, Mapping)
    }
    rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    seen: set[str] = set()
    for ref in _required_refresh_target_refs(preflight):
        path_text = str(ref.get("path") or "").strip()
        row, row_blockers = _active_context_refresh_apply_target_row(root, path_text)
        blockers.extend(row_blockers)
        if row_blockers or not row:
            continue
        if row["path"] in seen:
            continue
        seen.add(str(row["path"]))
        mount_id = str(row.get("mount_id") or ref.get("mount_id") or "")
        target_mount = target_mounts.get(mount_id, {})
        rows.append({
            **row,
            "mount_id": mount_id,
            "role_id": str(target_mount.get("role_id") or ""),
            "domain_id": str(target_mount.get("domain_id") or ""),
            "lane_ids": [str(item) for item in _as_list(target_mount.get("lane_ids")) if str(item or "").strip()],
            "semantic_identity": target_mount.get("semantic_identity") if isinstance(target_mount.get("semantic_identity"), Mapping) else {},
            "reason": str(ref.get("reason") or "active_context_package_requires_reissue"),
            "source": str(ref.get("source") or "active_context_reissue_preflight"),
        })
    if not rows:
        blockers.append("active_context_refresh_apply_targets_required")
    return rows, _unique_texts(blockers)


def _active_context_refresh_apply_target_row(root: Path, path_text: str) -> tuple[dict[str, Any] | None, list[str]]:
    blockers: list[str] = []
    if not path_text:
        return None, ["active_context_refresh_target_path_required"]
    raw = Path(path_text)
    if raw.is_absolute() or any(part == ".." for part in raw.parts):
        return None, ["active_context_refresh_target_path_must_be_repo_relative_without_escape"]
    target = (root / raw).resolve(strict=False)
    try:
        rel = target.relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return None, ["active_context_refresh_target_path_outside_active_root"]
    parts = Path(rel).parts
    expected_prefix = ("ION", "05_context", "current", "codex_agent_mounts")
    if len(parts) != 7 or parts[:4] != expected_prefix or parts[5] != ".ion":
        blockers.append("active_context_refresh_target_must_be_mount_ion_active_context_package")
    filename = parts[-1] if parts else ""
    if filename not in {"ACTIVE_CONTEXT_PACKAGE.md", "ACTIVE_CONTEXT_PACKAGE.json"}:
        blockers.append("active_context_refresh_target_filename_not_allowed")
    mount_id = parts[4] if len(parts) > 4 else ""
    mount_path = root / "ION/05_context/current/codex_agent_mounts" / mount_id
    if not mount_id or not mount_path.is_dir():
        blockers.append("active_context_refresh_target_mount_missing")
    return (
        {
            "path": rel,
            "mount_id": mount_id,
            "filename": filename,
            "content_type": "markdown" if filename.endswith(".md") else "json",
        },
        _unique_texts(blockers),
    )


def _active_context_refresh_target_content(
    row: Mapping[str, Any],
    *,
    preflight_result: Mapping[str, Any],
    generated_at: str,
    agent_id: str,
    lease_id: str,
    idempotency_key: str,
) -> str:
    if row.get("content_type") == "json":
        payload = {
            "schema_id": "ion.domain_weaver.active_context_package.refreshed.v0_1_candidate",
            "context_generated_at": generated_at,
            "mount_id": row.get("mount_id"),
            "role_id": row.get("role_id"),
            "domain_id": row.get("domain_id"),
            "lane_ids": row.get("lane_ids") or [],
            "semantic_identity": row.get("semantic_identity") if isinstance(row.get("semantic_identity"), Mapping) else {},
            "source_preflight_packet_id": preflight_result.get("packet_id"),
            "source_preflight_generated_at": preflight_result.get("generated_at"),
            "source_reason": row.get("reason"),
            "refresh_agent_id": agent_id,
            "refresh_lease_id": lease_id,
            "idempotency_key": idempotency_key,
            "write_posture": "gated_active_context_refresh",
            "candidate_context_only": True,
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
            "materialization_authority": False,
            "authority": _authority(),
            "non_claims": [
                "This package is active-context carrier input only.",
                "It is not accepted projection, registry, materialization, topology, UI, production, live, or secrets authority.",
            ],
        }
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"
    lines = [
        "# Active Context Package",
        "",
        f"mount_id: {row.get('mount_id')}",
        f"role_id: {row.get('role_id')}",
        f"domain_id: {row.get('domain_id')}",
        f"context_generated_at: {generated_at}",
        "write_posture: gated_active_context_refresh",
        "candidate_context_only: true",
        "accepted_state_authority: false",
        "production_authority: false",
        "live_execution_authority: false",
        "secrets_authority: false",
        "materialization_authority: false",
        "",
        "## Policy",
        "",
        "- This package was refreshed by the bounded active-context gated refresh path.",
        "- It is carrier input for this generated Codex mount only.",
        "- It does not move accepted projection, registry, materialization, topology, UI, production, live, secrets, or git state.",
        "- Worker returns remain carrier intake only until separate settlement.",
        "",
        "## Source",
        "",
        f"- source_preflight_packet_id: {preflight_result.get('packet_id')}",
        f"- source_preflight_generated_at: {preflight_result.get('generated_at')}",
        f"- source_reason: {row.get('reason')}",
        f"- refresh_agent_id: {agent_id}",
        f"- refresh_lease_id: {lease_id}",
        f"- idempotency_key: {idempotency_key}",
        "",
    ]
    lane_ids = [str(item) for item in _as_list(row.get("lane_ids")) if str(item or "").strip()]
    if lane_ids:
        lines.extend(["## Lanes", ""])
        lines.extend([f"- {lane_id}" for lane_id in lane_ids])
        lines.append("")
    return "\n".join(lines)


def _active_context_refresh_receipt_path(root: Path, generated_at: str, idempotency_key: str) -> Path:
    stamp = generated_at.replace("-", "").replace(":", "").replace("+00:00", "Z")
    safe_key = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in idempotency_key)[:80] or "refresh"
    return root / "ION/05_context/current/domain_weaver/active_context_refresh/apply_receipts" / f"{stamp}_{safe_key}.json"


def _file_digest_row(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"exists": False, "sha256": "", "bytes": 0}
    data = path.read_bytes()
    return {
        "exists": True,
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def _atomic_write_text(path: Path, text: str) -> None:
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _id_from_mount_part(part: str, prefix: str) -> str:
    if not part.startswith(prefix):
        return ""
    return f"{prefix[:-1]}.{part[len(prefix):]}"


def _ids_from_mount_name(name: str) -> tuple[str, str]:
    left, marker, right = name.partition("__")
    if not marker:
        return "", ""
    return _id_from_mount_part(left, "role_"), _id_from_mount_part(right, "domain_")


def _canonical_mount_dirs(mounts_root: Path) -> list[Path]:
    if not mounts_root.is_dir():
        return []
    return [
        mount
        for mount in sorted(mounts_root.iterdir())
        if mount.is_dir() and not mount.name.startswith(".") and _ids_from_mount_name(mount.name) != ("", "")
    ]


def _mount_launch_completeness(root: Path, mount_path: Path, now: datetime) -> dict[str, Any]:
    ion_dir = mount_path / ".ion"
    top_files = {
        name: _file_row(root, mount_path / name, now)
        for name in LAUNCH_REQUIRED_TOP_FILES
    }
    ion_files = {
        name: _file_row(root, ion_dir / name, now)
        for name in LAUNCH_REQUIRED_ION_FILES
    }
    missing_top = [
        row["path"]
        for row in top_files.values()
        if not row.get("exists")
    ]
    missing_ion = [
        row["path"]
        for row in ion_files.values()
        if not row.get("exists")
    ]
    missing_refs = missing_top + missing_ion
    blockers: list[str] = []
    if missing_refs:
        blockers.append("mount_launch_completeness_missing_required_refs")
    if not ion_files.get("CONTEXT_IDENTITY.json", {}).get("exists"):
        blockers.append("mount_context_identity_missing")
    return {
        "schema_id": "ion.domain_weaver.mount_launch_completeness.v0_1_candidate",
        "mount_id": mount_path.name,
        "mount_launch_ready": not missing_refs,
        "required_top_files": top_files,
        "required_ion_files": ion_files,
        "missing_launch_refs": missing_refs,
        "missing_launch_ref_count": len(missing_refs),
        "blockers": _unique_texts(blockers),
        "authority": _authority(),
    }


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _parse_timestamp(value: Any) -> datetime | None:
    text = _clean_text(value)
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _read_json_mapping(path: Path) -> tuple[Mapping[str, Any] | None, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "missing"
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None, "invalid_json"
    if not isinstance(payload, Mapping):
        return None, "json_not_object"
    return payload, ""


def _file_row(root: Path, path: Path, now: datetime) -> dict[str, Any]:
    exists = path.is_file()
    row: dict[str, Any] = {
        "path": _rel(path, root),
        "exists": exists,
    }
    if exists:
        modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        row.update({
            "modified_at": modified.isoformat(),
            "age_seconds": round(max(0.0, (now - modified).total_seconds()), 3),
            "bytes": path.stat().st_size,
        })
    return row


def _root_proof(root: Path, now: datetime) -> dict[str, Any]:
    rows = {ref.as_posix(): _file_row(root, root / ref, now) for ref in ROOT_PROOF_REQUIRED_REFS}
    missing = [ref for ref, row in rows.items() if not row.get("exists")]
    blockers = ["active_root_proof_failed"] if missing else []
    return {
        "schema_id": "ion.domain_weaver.active_root_proof.v0_1",
        "ok": not missing,
        "active_root": root.as_posix(),
        "required_siblings": rows,
        "missing_required_siblings": missing,
        "blockers": blockers,
        "authority": _authority(),
    }


def _is_repo_relative(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root)
    except ValueError:
        return False
    return True


def _generated_codex_solo_ref(path_ref: str) -> bool:
    prefix = CODEX_SOLO_DIR.as_posix() + "/"
    return path_ref.startswith(prefix) and not path_ref.endswith("/history")


def _context_ref_row(
    root: Path,
    path_ref: str,
    now: datetime,
    max_age_seconds: int,
    *,
    stale_sensitive: bool,
) -> dict[str, Any]:
    ref_text = _clean_text(path_ref)
    path = Path(ref_text).expanduser()
    if not path.is_absolute():
        path = root / path
    exists = path.exists()
    repo_relative = _is_repo_relative(path, root)
    row: dict[str, Any] = {
        "path": ref_text,
        "resolved_path": _rel(path, root),
        "exists": exists,
        "repo_relative": repo_relative,
        "is_file": path.is_file() if exists else False,
        "is_dir": path.is_dir() if exists else False,
        "stale_sensitive": stale_sensitive,
        "stale": False,
        "blockers": [],
    }
    if exists:
        modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        age_seconds = round(max(0.0, (now - modified).total_seconds()), 3)
        row.update({
            "modified_at": modified.isoformat(),
            "age_seconds": age_seconds,
            "bytes": path.stat().st_size if path.is_file() else None,
        })
        if stale_sensitive and age_seconds > max_age_seconds:
            row["stale"] = True
            row["blockers"].append("codex_solo_context_package_ref_stale")
    else:
        row["blockers"].append("codex_solo_context_package_ref_missing")
    if not repo_relative:
        row["blockers"].append("codex_solo_context_package_ref_outside_active_root")
    return row


def _package_rows(
    root: Path,
    payload: Mapping[str, Any],
    now: datetime,
    max_age_seconds: int,
) -> tuple[list[dict[str, Any]], list[str], list[str], list[str]]:
    package_rows: list[dict[str, Any]] = []
    missing_refs: list[str] = []
    stale_refs: list[str] = []
    blockers: list[str] = []
    raw_packages = payload.get("packages")
    if not isinstance(raw_packages, list):
        return [], [], [], ["codex_solo_context_packages_invalid"]
    for index, package in enumerate(raw_packages):
        if not isinstance(package, Mapping):
            blockers.append("codex_solo_context_package_invalid")
            package_rows.append({
                "package_index": index,
                "package_id": "",
                "ok": False,
                "blockers": ["codex_solo_context_package_invalid"],
                "path_refs": [],
            })
            continue
        package_id = _clean_text(package.get("package_id")) or f"package_{index}"
        raw_refs = package.get("path_refs")
        path_refs = raw_refs if isinstance(raw_refs, list) else []
        ref_rows = [
            _context_ref_row(
                root,
                _clean_text(ref),
                now,
                max_age_seconds,
                stale_sensitive=_generated_codex_solo_ref(_clean_text(ref)),
            )
            for ref in path_refs
        ]
        row_blockers = sorted({
            str(blocker)
            for ref_row in ref_rows
            for blocker in ref_row.get("blockers", [])
        })
        for ref_row in ref_rows:
            if "codex_solo_context_package_ref_missing" in ref_row.get("blockers", []):
                missing_refs.append(str(ref_row.get("path")))
            if "codex_solo_context_package_ref_stale" in ref_row.get("blockers", []):
                stale_refs.append(str(ref_row.get("path")))
        blockers.extend(row_blockers)
        package_rows.append({
            "package_index": index,
            "package_id": package_id,
            "context_type": _clean_text(package.get("context_type")),
            "load_policy": _clean_text(package.get("load_policy")),
            "ok": not row_blockers,
            "path_ref_count": len(ref_rows),
            "missing_path_ref_count": sum(1 for row in ref_rows if "codex_solo_context_package_ref_missing" in row.get("blockers", [])),
            "stale_path_ref_count": sum(1 for row in ref_rows if "codex_solo_context_package_ref_stale" in row.get("blockers", [])),
            "path_refs": ref_rows,
            "blockers": row_blockers,
        })
    return package_rows, missing_refs, stale_refs, blockers


def _codex_solo_context_health(root: Path, now: datetime, max_age_seconds: int) -> dict[str, Any]:
    blockers: list[str] = []
    missing_refs: list[str] = []
    stale_refs: list[str] = []
    manifest_path = root / CODEX_SOLO_CONTEXT_PACKAGES
    manifest_row = _file_row(root, manifest_path, now)
    boot_refs = [
        _context_ref_row(
            root,
            ref.as_posix(),
            now,
            max_age_seconds,
            stale_sensitive=True,
        )
        for ref in CODEX_SOLO_BOOT_REFS
    ]
    for row in boot_refs:
        if "codex_solo_context_package_ref_missing" in row.get("blockers", []):
            missing_refs.append(str(row.get("path")))
        if "codex_solo_context_package_ref_stale" in row.get("blockers", []):
            stale_refs.append(str(row.get("path")))
    blockers.extend(str(blocker) for row in boot_refs for blocker in row.get("blockers", []))
    payload, read_error = _read_json_mapping(manifest_path)
    package_rows: list[dict[str, Any]] = []
    selected_by_default: list[str] = []
    generated_at = ""
    generated_age_seconds: float | None = None
    declared_package_count: int | None = None
    if read_error:
        blockers.append(f"codex_solo_context_packages_{read_error}")
    elif payload is not None:
        generated_at = _clean_text(payload.get("generated_at"))
        parsed_generated = _parse_timestamp(generated_at)
        if parsed_generated is not None:
            generated_age_seconds = round(max(0.0, (now - parsed_generated).total_seconds()), 3)
            if generated_age_seconds > max_age_seconds:
                blockers.append("codex_solo_context_manifest_stale")
        else:
            blockers.append("codex_solo_context_manifest_generated_at_missing_or_invalid")
        selected_raw = payload.get("selected_by_default")
        if isinstance(selected_raw, list):
            selected_by_default = [_clean_text(item) for item in selected_raw if _clean_text(item)]
        count_raw = payload.get("package_count")
        declared_package_count = count_raw if isinstance(count_raw, int) else None
        package_rows, package_missing, package_stale, package_blockers = _package_rows(root, payload, now, max_age_seconds)
        missing_refs.extend(package_missing)
        stale_refs.extend(package_stale)
        blockers.extend(package_blockers)
        if declared_package_count is not None and declared_package_count != len(package_rows):
            blockers.append("codex_solo_context_package_count_mismatch")
        package_ids = {str(row.get("package_id")) for row in package_rows}
        if selected_by_default and any(package_id not in package_ids for package_id in selected_by_default):
            blockers.append("codex_solo_context_selected_package_missing")
    blockers = sorted(set(blockers))
    missing_refs = sorted(set(ref for ref in missing_refs if ref))
    stale_refs = sorted(set(ref for ref in stale_refs if ref))
    ok = not blockers
    return {
        "schema_id": "ion.codex_solo.active_context_package_health.v0_1",
        "ok": ok,
        "health": "fresh" if ok else "blocked",
        "context_packages_path": _rel(manifest_path, root),
        "context_packages_manifest": manifest_row,
        "generated_at": generated_at,
        "generated_age_seconds": generated_age_seconds,
        "max_context_age_seconds": max_age_seconds,
        "declared_package_count": declared_package_count,
        "package_count": len(package_rows),
        "selected_by_default": selected_by_default,
        "missing_path_refs": missing_refs,
        "stale_path_refs": stale_refs,
        "boot_refs": boot_refs,
        "package_rows": package_rows,
        "blockers": blockers,
        "authority": _authority(),
    }


def _materialize_all_guard(
    *,
    root_proof: Mapping[str, Any],
    codex_solo_context_health: Mapping[str, Any],
    inspected_mount_count: int,
    fresh_active_context_count: int,
    stale_or_missing_active_context_count: int,
    selected: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    blockers = ["resolver_has_no_materialization_authority"]
    if not root_proof.get("ok"):
        blockers.append("active_root_proof_failed")
    if not codex_solo_context_health.get("ok"):
        blockers.append("codex_solo_context_package_health_blocked")
    selected_fresh = bool(selected and selected.get("active_context_fresh"))
    if not selected_fresh and fresh_active_context_count <= 0:
        blockers.append("fresh_active_context_package_proof_missing")
    if stale_or_missing_active_context_count > 0:
        blockers.append("active_context_mounts_stale_or_missing")
    return {
        "schema_id": "ion.domain_weaver.materialize_all_guard.v0_1",
        "materialize_all_allowed": False,
        "blocked": True,
        "finding": "materialize_all_blocked_until_fresh_active_context_package_proof",
        "recommended_next_packet": ACTIVE_CONTEXT_REISSUE_PREFLIGHT_PACKET_ID,
        "inspected_mount_count": inspected_mount_count,
        "fresh_active_context_count": fresh_active_context_count,
        "stale_or_missing_active_context_count": stale_or_missing_active_context_count,
        "selected_active_context_fresh": selected_fresh,
        "blockers": sorted(set(blockers)),
        "authority": _authority(),
    }


def _context_lane_ids(path: Path) -> list[str]:
    if not path.is_file():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return []
    if not isinstance(payload, Mapping):
        return []
    raw_values: list[Any] = [
        payload.get("lane_id"),
        payload.get("lane"),
        payload.get("domain_weaver_lane_id"),
    ]
    for key in ("lanes", "lane_ids"):
        value = payload.get(key)
        if isinstance(value, list):
            raw_values.extend(value)
    value = payload.get("lane_metadata")
    if isinstance(value, list):
        for item in value:
            if isinstance(item, Mapping):
                raw_values.extend([item.get("lane_id"), item.get("lane"), item.get("invocation_lane")])
            else:
                raw_values.append(item)
    for key in ("context", "capsule", "domain_weaver"):
        value = payload.get(key)
        if isinstance(value, Mapping):
            raw_values.extend([value.get("lane_id"), value.get("lane")])
    lane_ids: list[str] = []
    seen: set[str] = set()
    for value in raw_values:
        text = _clean_text(value)
        if text and text not in seen:
            lane_ids.append(text)
            seen.add(text)
    return lane_ids


def _mount_row(root: Path, mount_path: Path, now: datetime, max_age_seconds: int) -> dict[str, Any]:
    manifest, _manifest_error = _read_json_mapping(mount_path / "ION_AGENT_MOUNT_MANIFEST.json")
    identity = canonicalize_codex_mount_identity(mount_path.name, manifest or {})
    role_id = str(identity.get("role_id") or "")
    domain_id = str(identity.get("domain_id") or "")
    ion_dir = mount_path / ".ion"
    files = {name: _file_row(root, ion_dir / name, now) for name in READ_FIRST_FILES}
    launch_completeness = _mount_launch_completeness(root, mount_path, now)
    active_md = files["ACTIVE_CONTEXT_PACKAGE.md"]
    active_json = files["ACTIVE_CONTEXT_PACKAGE.json"]
    active_exists = bool(active_md["exists"] or active_json["exists"])
    ages = [
        float(row["age_seconds"])
        for row in (active_md, active_json)
        if row.get("exists") and isinstance(row.get("age_seconds"), (int, float))
    ]
    lane_ids = _context_lane_ids(ion_dir / "ACTIVE_CONTEXT_PACKAGE.json")
    active_age = min(ages) if ages else None
    fresh = active_age is not None and active_age <= max_age_seconds
    blockers: list[str] = []
    if not active_exists:
        blockers.append("active_context_package_missing")
    if active_exists and not fresh:
        blockers.append("active_context_package_stale")
    return {
        "row_kind": "domain_weaver_active_context_candidate",
        "mount_id": mount_path.name,
        "mount_path": _rel(mount_path, root),
        "role_id": role_id,
        "domain_id": domain_id,
        "semantic_identity": identity,
        "active_context_package_exists": active_exists,
        "active_context_fresh": fresh,
        "active_context_age_seconds": active_age,
        "lane_ids": lane_ids,
        "max_context_age_seconds": max_age_seconds,
        "read_first": [_rel(ion_dir / name, root) for name in READ_FIRST_FILES],
        "files": files,
        "mount_launch_ready": launch_completeness["mount_launch_ready"],
        "missing_launch_refs": launch_completeness["missing_launch_refs"],
        "missing_launch_ref_count": launch_completeness["missing_launch_ref_count"],
        "mount_completeness": launch_completeness,
        "mount_completeness_blockers": launch_completeness["blockers"],
        "blockers": blockers,
        "authority": _authority(),
    }


def _score(row: Mapping[str, Any], role_id: str, domain_id: str, lane_id: str) -> tuple[int, int, int, int, float]:
    role_match = int(bool(role_id and row.get("role_id") == role_id))
    domain_match = int(bool(domain_id and row.get("domain_id") == domain_id))
    lane_match = int(bool(lane_id and lane_id in set(row.get("lane_ids") or [])))
    fresh = int(bool(row.get("active_context_fresh")))
    age = float(row.get("active_context_age_seconds") if row.get("active_context_age_seconds") is not None else 10**12)
    return role_match, domain_match, lane_match, fresh, -age


def _matches_requested_context(row: Mapping[str, Any], domain_id: str, role_id: str, lane_id: str) -> bool:
    if domain_id and row.get("domain_id") != domain_id:
        return False
    if role_id and row.get("role_id") != role_id:
        return False
    if lane_id and lane_id not in set(row.get("lane_ids") or []):
        return False
    return True


def _active_context_package_paths(row: Mapping[str, Any]) -> list[str]:
    files = row.get("files") if isinstance(row.get("files"), Mapping) else {}
    paths: list[str] = []
    seen: set[str] = set()
    for name in ("ACTIVE_CONTEXT_PACKAGE.md", "ACTIVE_CONTEXT_PACKAGE.json"):
        file_row = files.get(name) if isinstance(files, Mapping) else None
        path = _clean_text(file_row.get("path") if isinstance(file_row, Mapping) else "")
        if path and path not in seen:
            paths.append(path)
            seen.add(path)
    return paths


def _expected_lane_metadata(row: Mapping[str, Any], *, domain_id: str, role_id: str, lane_id: str) -> dict[str, Any]:
    expected_lanes = [lane_id] if lane_id else [str(item) for item in row.get("lane_ids") or [] if _clean_text(item)]
    return {
        "schema_id": "ion.domain_weaver.active_context.expected_lane_metadata.v0_1",
        "mount_id": _clean_text(row.get("mount_id")),
        "domain_id": domain_id or _clean_text(row.get("domain_id")),
        "role_id": role_id or _clean_text(row.get("role_id")),
        "lane_ids": expected_lanes,
        "required_fields": [
            "domain_id",
            "role_id",
            "lane_id_or_lane_ids",
            "role_tier",
            "callsign",
            "packet_id",
            "context_generated_at",
            "active_root",
            "source_receipt_path",
            "authority.accepted_state=false",
            "authority.production_authority=false",
            "authority.live_execution_authority=false",
            "authority.secrets_authority=false",
        ],
        "forbidden_fields": [
            "accepted_state=true",
            "production_authority=true",
            "live_execution_authority=true",
            "secrets_authority=true",
            "materialization_write_authority=true",
        ],
        "authority": _authority(),
    }


def _required_refresh_leases(row: Mapping[str, Any]) -> list[dict[str, Any]]:
    paths = _active_context_refresh_target_paths(row)
    return [
        {
            "schema_id": "ion.domain_weaver.active_context.refresh_required_lease.v0_1",
            "lease_scope": "gated_refresh_only",
            "lease_type": "exclusive_write",
            "target_mount_id": _clean_text(row.get("mount_id")),
            "target_paths": paths,
            "required_actor_fields": ["agent_id", "lease_id"],
            "required_confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key_required": True,
            "refresh_preflight_only": True,
            "lease_not_requested_by_preflight": True,
        }
    ]


def _active_context_refresh_target_paths(row: Mapping[str, Any]) -> list[str]:
    refs = _mount_stale_or_missing_refs(row)
    paths = _unique_texts([ref.get("path") for ref in refs])
    return paths if paths else _active_context_package_paths(row)


def _mount_stale_or_missing_refs(row: Mapping[str, Any]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    files = row.get("files") if isinstance(row.get("files"), Mapping) else {}
    md_row = files.get("ACTIVE_CONTEXT_PACKAGE.md") if isinstance(files, Mapping) else None
    json_row = files.get("ACTIVE_CONTEXT_PACKAGE.json") if isinstance(files, Mapping) else None
    active_rows = [item for item in (md_row, json_row) if isinstance(item, Mapping)]
    any_exists = any(bool(item.get("exists")) for item in active_rows)
    for name in ("ACTIVE_CONTEXT_PACKAGE.md", "ACTIVE_CONTEXT_PACKAGE.json"):
        file_row = files.get(name) if isinstance(files, Mapping) else None
        if not isinstance(file_row, Mapping):
            continue
        exists = bool(file_row.get("exists"))
        age = file_row.get("age_seconds")
        stale = exists and isinstance(age, (int, float)) and age > float(row.get("max_context_age_seconds") or 0)
        missing_required = not exists and not any_exists
        if missing_required or stale:
            refs.append({
                "mount_id": _clean_text(row.get("mount_id")),
                "path": _clean_text(file_row.get("path")),
                "reason": "active_context_package_missing" if not exists else "active_context_package_stale",
                "age_seconds": age if exists else None,
                "max_context_age_seconds": row.get("max_context_age_seconds"),
            })
    return refs


def build_active_context_reissue_preflight(
    root: str | Path | None,
    *,
    domain_id: str | None = None,
    role_id: str | None = None,
    lane: str | None = None,
    max_age_seconds: int = DEFAULT_MAX_CONTEXT_AGE_SECONDS,
) -> dict[str, Any]:
    """Build the read-only preflight for active-context package reissue.

    This function deliberately does not refresh, reissue, materialize, start
    workers, write leases, or mutate registries. It turns the resolver's
    current evidence into a bounded next-packet contract for a later gated
    refresh lane.
    """

    shell_root = Path(root or ".").expanduser().resolve()
    now = datetime.now(timezone.utc)
    wanted_domain = _clean_text(domain_id)
    wanted_role = _clean_text(role_id)
    wanted_lane = _clean_text(lane)
    root_proof = _root_proof(shell_root, now)
    codex_solo_context_health = _codex_solo_context_health(shell_root, now, max_age_seconds)
    mounts_root = shell_root / CODEX_AGENT_MOUNTS
    mount_rows = [
        _mount_row(shell_root, mount, now, max_age_seconds)
        for mount in _canonical_mount_dirs(mounts_root)
    ]
    launch_incomplete_rows = [
        row for row in mount_rows if not row.get("mount_launch_ready")
    ]
    requested_filter_present = bool(wanted_domain or wanted_role or wanted_lane)
    matching_rows = [
        row for row in mount_rows
        if _matches_requested_context(row, wanted_domain, wanted_role, wanted_lane)
    ]
    target_rows = [
        row for row in (matching_rows if requested_filter_present else mount_rows)
        if row.get("blockers") or not row.get("active_context_fresh") or _mount_stale_or_missing_refs(row)
    ]
    stale_package_refs = [
        {
            "source": "codex_solo_context_package",
            "path": path,
            "reason": "codex_solo_context_package_ref_stale",
        }
        for path in codex_solo_context_health.get("stale_path_refs") or []
    ]
    missing_package_refs = [
        {
            "source": "codex_solo_context_package",
            "path": path,
            "reason": "codex_solo_context_package_ref_missing",
        }
        for path in codex_solo_context_health.get("missing_path_refs") or []
    ]
    mount_refs = [
        ref for row in target_rows for ref in _mount_stale_or_missing_refs(row)
    ]
    target_mounts = [
        {
            "mount_id": row.get("mount_id"),
            "mount_path": row.get("mount_path"),
            "role_id": row.get("role_id"),
            "domain_id": row.get("domain_id"),
            "semantic_identity": row.get("semantic_identity"),
            "lane_ids": row.get("lane_ids") or [],
            "active_context_package_exists": row.get("active_context_package_exists"),
            "active_context_fresh": row.get("active_context_fresh"),
            "active_context_age_seconds": row.get("active_context_age_seconds"),
            "active_context_package_refs_requiring_refresh": _mount_stale_or_missing_refs(row),
            "required_refresh_target_paths": _active_context_refresh_target_paths(row),
            "mount_launch_ready": row.get("mount_launch_ready"),
            "missing_launch_refs": row.get("missing_launch_refs") or [],
            "missing_launch_ref_count": row.get("missing_launch_ref_count"),
            "mount_completeness_blockers": row.get("mount_completeness_blockers") or [],
            "blockers": row.get("blockers") or [],
            "expected_lane_metadata": _expected_lane_metadata(
                row,
                domain_id=wanted_domain,
                role_id=wanted_role,
                lane_id=wanted_lane,
            ),
            "required_refresh_leases": _required_refresh_leases(row),
            "authority": _authority(),
        }
        for row in target_rows
    ]
    blockers = sorted(set(
        [str(item) for item in root_proof.get("blockers") or []]
        + [str(item) for item in codex_solo_context_health.get("blockers") or []]
        + ["gated_refresh_not_run_preflight_only", "gated_refresh_requires_followup_packet"]
        + (["no_matching_target_mount"] if requested_filter_present and not matching_rows else [])
        + (["active_context_targets_require_reissue"] if target_rows else [])
        + (["mount_launch_completeness_incomplete"] if launch_incomplete_rows else [])
    ))
    launch_incomplete_mounts = [
        {
            "mount_id": row.get("mount_id"),
            "mount_path": row.get("mount_path"),
            "role_id": row.get("role_id"),
            "domain_id": row.get("domain_id"),
            "semantic_identity": row.get("semantic_identity"),
            "mount_launch_ready": row.get("mount_launch_ready"),
            "missing_launch_refs": row.get("missing_launch_refs") or [],
            "missing_launch_ref_count": row.get("missing_launch_ref_count"),
            "mount_completeness_blockers": row.get("mount_completeness_blockers") or [],
            "authority": _authority(),
        }
        for row in launch_incomplete_rows
    ]
    return {
        "schema_id": "ion.domain_weaver.active_context_reissue_preflight.v0_1_candidate",
        "packet_id": ACTIVE_CONTEXT_REISSUE_PREFLIGHT_PACKET_ID,
        "ok": True,
        "preflight_completed": True,
        "mutates_active_state": False,
        "refresh_run": False,
        "refresh_allowed_now": False,
        "active_root": shell_root.as_posix(),
        "generated_at": now.isoformat(),
        "domain_id": wanted_domain,
        "role_id": wanted_role,
        "lane": wanted_lane,
        "root_proof": root_proof,
        "codex_solo_context_health": codex_solo_context_health,
        "inspected_mount_count": len(mount_rows),
        "matching_mount_count": len(matching_rows),
        "launch_incomplete_mount_count": len(launch_incomplete_rows),
        "launch_incomplete_mounts": launch_incomplete_mounts,
        "target_mount_count": len(target_mounts),
        "stale_package_refs": stale_package_refs,
        "missing_package_refs": missing_package_refs,
        "mount_package_refs_requiring_reissue": mount_refs,
        "mount_package_refs_requiring_reissue_count": len(mount_refs),
        "target_mounts": target_mounts,
        "preflight_required_leases": [],
        "gated_refresh_required_leases": [
            lease for target in target_mounts for lease in target.get("required_refresh_leases", [])
        ],
        "rollback_plan": {
            "required_before_refresh": True,
            "steps": [
                "capture_before_hash_for_each_target_path",
                "write_preview_receipt_before_any_refresh_write",
                "write_new_context_package_to_temp_path_first",
                "atomically_replace_only_paths_covered_by_active_exclusive_write_lease",
                "on_failure_restore_before_hash_match_or_emit_rollback_blocker",
                "write_refresh_apply_or_rollback_receipt",
            ],
        },
        "receipt_plan": {
            "preflight_artifact_required": True,
            "refresh_preview_receipt_required": True,
            "refresh_apply_receipt_required": True,
            "rollback_receipt_required_on_failure": True,
            "fanin_settlement_required": True,
            "codex_solo_post_allowed_only_after_lead_fanin_settlement": True,
        },
        "gated_refresh_gate": {
            "refresh_run": False,
            "allowed_now": False,
            "gate": "preflight_only",
            "forbidden_actions": [
                "reissue_active_context_package",
                "refresh_active_context_package",
                "materialize_all",
                "registry_movement",
                "worker_start",
                "topology_resume",
            ],
            "required_next_packet": "PCKT-DOMAIN-WEAVER-ACTIVE-CONTEXT-GATED-REFRESH-V0_1",
        },
        "blockers": blockers,
        "next_packet": "PCKT-DOMAIN-WEAVER-ACTIVE-CONTEXT-GATED-REFRESH-V0_1",
        "authority": _authority(),
    }


def resolve_domain_active_context(
    root: str | Path | None,
    *,
    domain_id: str | None = None,
    role_id: str | None = None,
    lane: str | None = None,
    max_age_seconds: int = DEFAULT_MAX_CONTEXT_AGE_SECONDS,
) -> dict[str, Any]:
    """Resolve the best active context package for a domain or role."""

    shell_root = Path(root or ".").expanduser().resolve()
    now = datetime.now(timezone.utc)
    wanted_domain = _clean_text(domain_id)
    wanted_role = _clean_text(role_id)
    wanted_lane = _clean_text(lane)
    blockers: list[str] = []
    root_proof = _root_proof(shell_root, now)
    codex_solo_context_health = _codex_solo_context_health(shell_root, now, max_age_seconds)
    blockers.extend(str(item) for item in root_proof.get("blockers") or [])
    blockers.extend(str(item) for item in codex_solo_context_health.get("blockers") or [])
    if not wanted_domain and not wanted_role:
        blockers.append("domain_id_or_role_id_required")
    mounts_root = shell_root / CODEX_AGENT_MOUNTS
    mount_rows = [
        _mount_row(shell_root, mount, now, max_age_seconds)
        for mount in _canonical_mount_dirs(mounts_root)
    ]
    candidates = [
        row for row in mount_rows
        if (not wanted_domain or row.get("domain_id") == wanted_domain)
        and (not wanted_role or row.get("role_id") == wanted_role)
        and (not wanted_lane or wanted_lane in set(row.get("lane_ids") or []))
    ]
    candidates.sort(key=lambda row: _score(row, wanted_role, wanted_domain, wanted_lane), reverse=True)
    selected = candidates[0] if candidates else None
    if not selected and (wanted_domain or wanted_role):
        blockers.append("no_matching_active_context_mount_for_lane" if wanted_lane else "no_matching_active_context_mount")
    if selected and not selected.get("active_context_fresh"):
        blockers.extend(str(item) for item in selected.get("blockers") or [])
    if selected and not selected.get("mount_launch_ready"):
        blockers.extend(str(item) for item in selected.get("mount_completeness_blockers") or [])
    fresh_active_context_count = sum(1 for row in mount_rows if row.get("active_context_fresh"))
    stale_or_missing_active_context_count = len(mount_rows) - fresh_active_context_count
    launch_ready_count = sum(1 for row in mount_rows if row.get("mount_launch_ready"))
    launch_incomplete_count = len(mount_rows) - launch_ready_count
    materialize_all_guard = _materialize_all_guard(
        root_proof=root_proof,
        codex_solo_context_health=codex_solo_context_health,
        inspected_mount_count=len(mount_rows),
        fresh_active_context_count=fresh_active_context_count,
        stale_or_missing_active_context_count=stale_or_missing_active_context_count,
        selected=selected if isinstance(selected, Mapping) else None,
    )
    ok = bool(
        selected
        and selected.get("active_context_fresh")
        and selected.get("mount_launch_ready")
        and root_proof.get("ok")
        and codex_solo_context_health.get("ok")
        and not blockers
    )
    if not root_proof.get("ok"):
        next_action = "repair_active_root_proof"
    elif not codex_solo_context_health.get("ok"):
        next_action = "repair_or_reissue_codex_solo_context_packages"
    elif selected and not selected.get("mount_launch_ready"):
        next_action = "repair_generated_mount_launch_completeness"
    elif ok:
        next_action = "use_selected_active_context"
    else:
        next_action = "repair_or_reissue_active_context_package"
    return {
        "schema_id": SCHEMA_ID,
        "ok": ok,
        "resolver_id": "domain.context_active_resolver",
        "mutates_active_state": False,
        "domain_id": wanted_domain,
        "role_id": wanted_role,
        "lane": wanted_lane,
        "root_proof": root_proof,
        "codex_solo_context_health": codex_solo_context_health,
        "materialize_all_guard": materialize_all_guard,
        "selected": selected,
        "candidate_count": len(candidates),
        "inspected_mount_count": len(mount_rows),
        "launch_ready_mount_count": launch_ready_count,
        "launch_incomplete_mount_count": launch_incomplete_count,
        "blockers": sorted(set(blockers)),
        "next_action": next_action,
        "authority": _authority(),
    }


def build_context_active_resolver_status(root: str | Path | None) -> dict[str, Any]:
    shell_root = Path(root or ".").expanduser().resolve()
    now = datetime.now(timezone.utc)
    root_proof = _root_proof(shell_root, now)
    codex_solo_context_health = _codex_solo_context_health(shell_root, now, DEFAULT_MAX_CONTEXT_AGE_SECONDS)
    mounts_root = shell_root / CODEX_AGENT_MOUNTS
    mount_rows = [
        _mount_row(shell_root, mount, now, DEFAULT_MAX_CONTEXT_AGE_SECONDS)
        for mount in _canonical_mount_dirs(mounts_root)
    ]
    fresh_count = sum(1 for row in mount_rows if row.get("active_context_fresh"))
    stale_or_missing_count = len(mount_rows) - fresh_count
    launch_ready_count = sum(1 for row in mount_rows if row.get("mount_launch_ready"))
    launch_incomplete_rows = [
        row for row in mount_rows if not row.get("mount_launch_ready")
    ]
    materialize_all_guard = _materialize_all_guard(
        root_proof=root_proof,
        codex_solo_context_health=codex_solo_context_health,
        inspected_mount_count=len(mount_rows),
        fresh_active_context_count=fresh_count,
        stale_or_missing_active_context_count=stale_or_missing_count,
    )
    blockers = sorted(set(
        [str(item) for item in root_proof.get("blockers") or []]
        + [str(item) for item in codex_solo_context_health.get("blockers") or []]
        + (["mount_launch_completeness_incomplete"] if launch_incomplete_rows else [])
    ))
    return {
        "schema_id": f"{SCHEMA_ID}.status",
        "resolver_id": "domain.context_active_resolver",
        "available": True,
        "ok": bool(root_proof.get("ok") and codex_solo_context_health.get("ok")),
        "mutates_active_state": False,
        "mount_root": _rel(mounts_root, shell_root),
        "root_proof": root_proof,
        "codex_solo_context_health": codex_solo_context_health,
        "materialize_all_guard": materialize_all_guard,
        "inspected_mount_count": len(mount_rows),
        "fresh_active_context_count": fresh_count,
        "stale_or_missing_active_context_count": stale_or_missing_count,
        "launch_ready_mount_count": launch_ready_count,
        "launch_incomplete_mount_count": len(launch_incomplete_rows),
        "launch_incomplete_mounts": [
            {
                "mount_id": row.get("mount_id"),
                "mount_path": row.get("mount_path"),
                "role_id": row.get("role_id"),
                "domain_id": row.get("domain_id"),
                "semantic_identity": row.get("semantic_identity"),
                "missing_launch_refs": row.get("missing_launch_refs") or [],
                "missing_launch_ref_count": row.get("missing_launch_ref_count"),
                "mount_completeness_blockers": row.get("mount_completeness_blockers") or [],
                "authority": _authority(),
            }
            for row in launch_incomplete_rows
        ],
        "blockers": blockers,
        "authority": _authority(),
    }
