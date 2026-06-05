"""Working capsule identity and local maintenance helpers.

This module validates the per-agent/chat/domain capsule identity used for
material work. It is deliberately narrower than branch-capsule settlement:
shared Codex Solo context may be a fallback witness, but it must not masquerade
as a unique working capsule.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


SCHEMA_ID = "ion.working_capsule_identity.v1"
MAINTENANCE_SCHEMA_ID = "ion.working_capsule_local_maintenance.v1"
READY_VERDICT = "WORKING_CAPSULE_IDENTITY_READY"
BLOCKED_VERDICT = "WORKING_CAPSULE_IDENTITY_BLOCKED"
REPAIR_REQUIRED_VERDICT = "WORKING_CAPSULE_IDENTITY_REPAIR_REQUIRED"
FALLBACK_VERDICT = "SHARED_CODEX_SOLO_FALLBACK_DECLARED"

OLD_ROOT_FRAGMENT = "/home/sev/ION - Production/ION_CODEX FULL"
SHARED_CODEX_SOLO_REL = "ION/05_context/current/codex_solo"
AGENT_MOUNTS_REL = "ION/05_context/current/codex_agent_mounts"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stable_hash(*parts: str) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update(part.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.:-]+", "_", value.strip()).strip("._:-")
    return slug[:96] or "working_capsule"


def _as_path(value: Any) -> Path | None:
    text = str(value or "").strip()
    return Path(text).expanduser() if text else None


def _repo_rel(root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(parent.resolve(strict=False))
        return True
    except ValueError:
        return False


def _contains_old_root(value: Any) -> bool:
    return OLD_ROOT_FRAGMENT in str(value or "")


def _contains_shared_codex_solo(value: Any) -> bool:
    return SHARED_CODEX_SOLO_REL in str(value or "") or str(value or "").strip() in {"codex_solo", "shared_codex_solo"}


@dataclass(frozen=True)
class WorkingCapsuleIdentity:
    instance_capsule_id: str
    domain_id: str
    carrier_instance_id: str
    cwd: str
    root: str
    role_id: str | None = None
    agent_id: str | None = None
    parent_capsule_ref: str | None = None
    lineage_id: str | None = None
    working_capsule_path: str | None = None
    codex_agent_mount: str | None = None
    production_authority: bool = False
    live_execution_authority: bool = False
    accepted_state_authority: bool = False
    secrets_authority: bool = False
    generated_at: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_id": SCHEMA_ID,
            "instance_capsule_id": self.instance_capsule_id,
            "domain_id": self.domain_id,
            "role_id": self.role_id,
            "agent_id": self.agent_id,
            "carrier_instance_id": self.carrier_instance_id,
            "parent_capsule_ref": self.parent_capsule_ref,
            "lineage_id": self.lineage_id,
            "cwd": self.cwd,
            "root": self.root,
            "working_capsule_path": self.working_capsule_path,
            "codex_agent_mount": self.codex_agent_mount,
            "authority": {
                "production_authority": self.production_authority,
                "live_execution_authority": self.live_execution_authority,
                "accepted_state_authority": self.accepted_state_authority,
                "secrets_authority": self.secrets_authority,
            },
            "non_claims": [
                "not accepted state",
                "no production authority",
                "no live execution authority",
                "no secrets authority",
            ],
            "generated_at": self.generated_at,
        }

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "WorkingCapsuleIdentity":
        authority = payload.get("authority") if isinstance(payload.get("authority"), Mapping) else {}
        return cls(
            instance_capsule_id=str(payload.get("instance_capsule_id") or ""),
            domain_id=str(payload.get("domain_id") or ""),
            role_id=str(payload.get("role_id") or "") or None,
            agent_id=str(payload.get("agent_id") or "") or None,
            carrier_instance_id=str(payload.get("carrier_instance_id") or ""),
            parent_capsule_ref=str(payload.get("parent_capsule_ref") or "") or None,
            lineage_id=str(payload.get("lineage_id") or "") or None,
            cwd=str(payload.get("cwd") or ""),
            root=str(payload.get("root") or ""),
            working_capsule_path=str(payload.get("working_capsule_path") or "") or None,
            codex_agent_mount=str(payload.get("codex_agent_mount") or "") or None,
            production_authority=bool(payload.get("production_authority", authority.get("production_authority", False))),
            live_execution_authority=bool(payload.get("live_execution_authority", authority.get("live_execution_authority", False))),
            accepted_state_authority=bool(payload.get("accepted_state_authority", authority.get("accepted_state_authority", False))),
            secrets_authority=bool(payload.get("secrets_authority", authority.get("secrets_authority", False))),
        )


def build_working_capsule_identity(
    *,
    root: str | Path,
    cwd: str | Path,
    domain_id: str,
    carrier_instance_id: str,
    role_id: str | None = None,
    agent_id: str | None = None,
    parent_capsule_ref: str | None = None,
    lineage_id: str | None = None,
    codex_agent_mount: str | Path | None = None,
    instance_capsule_id: str | None = None,
) -> WorkingCapsuleIdentity:
    root_path = Path(root).expanduser().resolve()
    cwd_path = Path(cwd).expanduser().resolve()
    owner = role_id or agent_id or "agent"
    capsule_id = instance_capsule_id or "wcaps_" + _stable_hash(
        root_path.as_posix(),
        cwd_path.as_posix(),
        domain_id,
        owner,
        carrier_instance_id,
    )[:20]
    mount_path = Path(codex_agent_mount).expanduser().resolve() if codex_agent_mount else None
    return WorkingCapsuleIdentity(
        instance_capsule_id=capsule_id,
        domain_id=domain_id,
        role_id=role_id,
        agent_id=agent_id,
        carrier_instance_id=carrier_instance_id,
        parent_capsule_ref=parent_capsule_ref,
        lineage_id=lineage_id,
        cwd=cwd_path.as_posix(),
        root=root_path.as_posix(),
        working_capsule_path=(cwd_path / ".ion").as_posix(),
        codex_agent_mount=mount_path.as_posix() if mount_path else None,
    )


def validate_working_capsule_identity(
    root: str | Path,
    identity: WorkingCapsuleIdentity | Mapping[str, Any],
) -> dict[str, Any]:
    root_path = Path(root).expanduser().resolve()
    capsule = identity if isinstance(identity, WorkingCapsuleIdentity) else WorkingCapsuleIdentity.from_mapping(identity)
    payload = capsule.to_dict()
    findings: list[dict[str, Any]] = []

    for key in ("instance_capsule_id", "domain_id", "carrier_instance_id", "cwd", "root"):
        if not payload.get(key):
            findings.append({"code": "missing_required_working_capsule_identity_field", "field": key})
    if not payload.get("role_id") and not payload.get("agent_id"):
        findings.append({"code": "role_id_or_agent_id_required"})

    declared_root = _as_path(payload.get("root"))
    cwd = _as_path(payload.get("cwd"))
    capsule_path = _as_path(payload.get("working_capsule_path")) or ((cwd / ".ion") if cwd else None)
    mount_path = _as_path(payload.get("codex_agent_mount"))

    if declared_root and declared_root.resolve(strict=False) != root_path:
        findings.append({"code": "root_binding_mismatch", "declared_root": declared_root.as_posix(), "actual_root": root_path.as_posix()})
    if cwd and not _is_under(cwd, root_path):
        findings.append({"code": "cwd_outside_active_root", "cwd": cwd.as_posix(), "root": root_path.as_posix()})
    if capsule_path and not _is_under(capsule_path, root_path):
        findings.append({"code": "working_capsule_path_outside_active_root", "working_capsule_path": capsule_path.as_posix()})

    for field in ("instance_capsule_id", "cwd", "root", "working_capsule_path", "codex_agent_mount"):
        if _contains_shared_codex_solo(payload.get(field)):
            findings.append({"code": "shared_codex_solo_as_working_capsule_forbidden", "field": field})
    for field in ("cwd", "root", "working_capsule_path", "codex_agent_mount", "parent_capsule_ref"):
        if _contains_old_root(payload.get(field)):
            findings.append({"code": "stale_ion_codex_full_root_reference", "field": field})

    if payload.get("parent_capsule_ref") and not payload.get("lineage_id"):
        findings.append({"code": "clone_lineage_required"})
    if mount_path:
        if not _is_under(mount_path, root_path / AGENT_MOUNTS_REL):
            findings.append({"code": "codex_agent_mount_outside_mount_root", "codex_agent_mount": mount_path.as_posix()})
    elif not capsule_path:
        findings.append({"code": "codex_agent_mount_or_unique_capsule_required"})

    authority = payload.get("authority") if isinstance(payload.get("authority"), Mapping) else {}
    for key in ("production_authority", "live_execution_authority", "accepted_state_authority", "secrets_authority"):
        if authority.get(key) is not False:
            findings.append({"code": f"{key}_must_be_false"})

    return {
        "schema_id": "ion.working_capsule_identity_validation.v1",
        "ok": not findings,
        "verdict": READY_VERDICT if not findings else BLOCKED_VERDICT,
        "instance_capsule_id": payload.get("instance_capsule_id") or None,
        "domain_id": payload.get("domain_id") or None,
        "role_id": payload.get("role_id") or None,
        "agent_id": payload.get("agent_id") or None,
        "findings": findings,
    }


def working_capsule_preflight(
    root: str | Path,
    payload: Mapping[str, Any],
    *,
    active_root_repair_allowed: bool = False,
) -> dict[str, Any]:
    identity_payload = payload.get("working_capsule_identity")
    if not isinstance(identity_payload, Mapping):
        fallback_reason = str(payload.get("shared_codex_solo_fallback_reason") or "").strip()
        if fallback_reason:
            return {
                "schema_id": "ion.working_capsule_preflight.v1",
                "ok": True,
                "verdict": FALLBACK_VERDICT,
                "classification": "shared_codex_solo_fallback",
                "shared_codex_solo_fallback_reason": fallback_reason,
                "findings": [{"code": "shared_codex_solo_fallback_declared"}],
            }
        return {
            "schema_id": "ion.working_capsule_preflight.v1",
            "ok": bool(active_root_repair_allowed),
            "verdict": REPAIR_REQUIRED_VERDICT,
            "classification": "repair_required" if active_root_repair_allowed else "fallback_required",
            "findings": [{"code": "working_capsule_identity_missing"}],
        }

    validation = validate_working_capsule_identity(root, identity_payload)
    return {
        "schema_id": "ion.working_capsule_preflight.v1",
        "ok": bool(validation.get("ok")),
        "verdict": validation.get("verdict"),
        "classification": "identity_ready" if validation.get("ok") else "identity_blocked",
        "identity_validation": validation,
        "findings": list(validation.get("findings", [])),
    }


def prepare_local_capsule_maintenance(
    root: str | Path,
    identity: WorkingCapsuleIdentity | Mapping[str, Any],
    *,
    task_return_packet_path: str,
    machine_receipt_path: str,
    proof_status: str,
) -> dict[str, Any]:
    root_path = Path(root).expanduser().resolve()
    capsule = identity if isinstance(identity, WorkingCapsuleIdentity) else WorkingCapsuleIdentity.from_mapping(identity)
    validation = validate_working_capsule_identity(root_path, capsule)
    if not validation.get("ok"):
        return {
            "schema_id": MAINTENANCE_SCHEMA_ID,
            "ok": False,
            "verdict": BLOCKED_VERDICT,
            "identity_validation": validation,
            "findings": list(validation.get("findings", [])),
        }

    cwd = Path(capsule.cwd).expanduser().resolve()
    ion_dir = Path(capsule.working_capsule_path).expanduser().resolve() if capsule.working_capsule_path else cwd / ".ion"
    if not _is_under(ion_dir, root_path):
        return {
            "schema_id": MAINTENANCE_SCHEMA_ID,
            "ok": False,
            "verdict": BLOCKED_VERDICT,
            "findings": [{"code": "maintenance_target_outside_active_root", "path": ion_dir.as_posix()}],
        }

    receipt_dir = ion_dir / "machine_receipts"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    for child in ("CAPSULE.md", "MINI.md", "HOT_CONTEXT.md"):
        (ion_dir / child).parent.mkdir(parents=True, exist_ok=True)

    identity_json = json.dumps(capsule.to_dict(), indent=2, sort_keys=True)
    (ion_dir / "CAPSULE.md").write_text(
        "\n".join(
            [
                "# ION Working Capsule",
                "",
                f"instance_capsule_id: {capsule.instance_capsule_id}",
                f"domain_id: {capsule.domain_id}",
                f"role_id: {capsule.role_id or ''}",
                f"agent_id: {capsule.agent_id or ''}",
                f"carrier_instance_id: {capsule.carrier_instance_id}",
                f"parent_capsule_ref: {capsule.parent_capsule_ref or ''}",
                f"lineage_id: {capsule.lineage_id or ''}",
                f"cwd: {capsule.cwd}",
                f"root: {capsule.root}",
                "",
                "This is a candidate local working capsule. It is not accepted state and grants no production/live/secrets authority.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (ion_dir / "MINI.md").write_text(
        "\n".join(
            [
                "# ION Working Capsule Mini",
                "",
                f"ACTIVE_CAPSULE: .ion/CAPSULE.md",
                f"INSTANCE_CAPSULE_ID: {capsule.instance_capsule_id}",
                f"DOMAIN_ID: {capsule.domain_id}",
                f"LAST_TASK_RETURN: {task_return_packet_path}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (ion_dir / "HOT_CONTEXT.md").write_text(
        "\n".join(
            [
                "# ION Working Capsule Hot Context",
                "",
                f"generated_at: {_now()}",
                f"instance_capsule_id: {capsule.instance_capsule_id}",
                "production_authority: false",
                "live_execution_authority: false",
                "accepted_state_authority: false",
                "",
                "## Latest Proof",
                f"- proof_status: {proof_status}",
                f"- task_return_packet_path: {task_return_packet_path}",
                f"- machine_receipt_path: {machine_receipt_path}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    receipt = {
        "schema_id": MAINTENANCE_SCHEMA_ID,
        "created_at": _now(),
        "ok": True,
        "verdict": READY_VERDICT,
        "identity": capsule.to_dict(),
        "identity_sha256": _stable_hash(identity_json),
        "proof_status": proof_status,
        "task_return_packet_path": task_return_packet_path,
        "machine_receipt_path": machine_receipt_path,
        "written_paths": [
            _repo_rel(root_path, ion_dir / "CAPSULE.md"),
            _repo_rel(root_path, ion_dir / "MINI.md"),
            _repo_rel(root_path, ion_dir / "HOT_CONTEXT.md"),
        ],
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
        "non_claims": ["not accepted state", "no production/live/secrets authority"],
    }
    receipt_path = receipt_dir / f"{_safe_slug(capsule.instance_capsule_id)}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_maintenance.json"
    receipt["receipt_path"] = _repo_rel(root_path, receipt_path)
    receipt["written_paths"].append(receipt["receipt_path"])
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt
