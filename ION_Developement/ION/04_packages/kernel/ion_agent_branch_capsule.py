"""ION agent branch capsule runtime helpers.

This module treats per-agent/per-conversation context as a candidate branch.
It does not merge accepted state, assign C-numbers, or mutate shared
Capsule/Mini/HOT_CONTEXT surfaces. The helper is intentionally stdlib-only so
it can run from Codex hooks, local scripts, and tests without service startup.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


DEFAULT_PARENT_CONTEXT_ID = "ION_MAIN_CURRENT_CONTEXT"
READY_VERDICT = "BRANCH_GUARD_READY"
BLOCKED_VERDICT = "BRANCH_GUARD_BLOCKED"
REGISTRY_SCHEMA = "ion.agent_branch_capsule.registry.v1"
SETTLEMENT_PACKET_SCHEMA = "ion.context_settlement.branch_capsule_request.v1"

PROTOCOL_REFS = (
    "ION/02_architecture/ION_AGENT_BRANCH_CAPSULE_PROTOCOL_V0_1.md",
    "ION/02_architecture/ION_AGENT_BRANCH_CAPSULE_BOOTSTRAP_BINDING_PROTOCOL_V0_1.md",
    "ION/02_architecture/ION_AGENT_BRANCH_CAPSULE_MATERIAL_WORK_GUARD_PROTOCOL_V0_1.md",
    "ION/02_architecture/ION_AGENT_BRANCH_CAPSULE_SETTLEMENT_INTAKE_PROTOCOL_V0_1.md",
    "ION/02_architecture/ION_AGENT_BRANCH_CAPSULE_REGISTRY_RECONCILIATION_PROTOCOL_V0_1.md",
)

BRANCH_ROOT = Path("ION/05_context/current/agent_context_branches")
BRANCH_REGISTRY_PATH = BRANCH_ROOT / "BRANCH_CAPSULE_REGISTRY_V0_1.json"
SETTLEMENT_INBOX = Path("ION/05_context/current/context_settlement/inbox")
SETTLEMENT_CLAIMS = Path("ION/05_context/current/context_settlement/claims")

SHARED_CONTEXT_SURFACES = (
    "ION/05_context/current/codex_solo/CAPSULE.md",
    "ION/05_context/current/codex_solo/MINI.md",
    "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
    "ION/05_context/current/codex_solo/STATUS.json",
    "ION/05_context/current/codex_solo/ROUTE.json",
    "ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json",
)

CHECKPOINT_FORBIDDEN_PATTERNS = (
    re.compile(r"(^|/)C-[0-9]{3,}"),
    re.compile(r"checkpoint", re.IGNORECASE),
    re.compile(r"accepted_state", re.IGNORECASE),
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _timestamp_token() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _stable_hash(parts: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update(part.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def normalize_tag(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "unnamed"


def _as_rel(path: str | Path, root: Path | None = None) -> str:
    p = Path(path)
    if root is not None and p.is_absolute():
        try:
            p = p.relative_to(root)
        except ValueError:
            return p.as_posix()
    return p.as_posix()


def _norm_rel(path: str | Path, root: Path | None = None) -> str:
    rel = _as_rel(path, root)
    return rel.strip().lstrip("./")


def _is_shared_context_surface(path: str | Path) -> bool:
    rel = _norm_rel(path)
    return any(rel == surface or rel.startswith(surface + "/") for surface in SHARED_CONTEXT_SURFACES)


def _is_checkpoint_surface(path: str | Path) -> bool:
    rel = _norm_rel(path)
    return any(pattern.search(rel) for pattern in CHECKPOINT_FORBIDDEN_PATTERNS)


def _paths_overlap(a: str | Path, b: str | Path) -> bool:
    left = _norm_rel(a).rstrip("/")
    right = _norm_rel(b).rstrip("/")
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def default_loaded_refs() -> list[str]:
    return list(PROTOCOL_REFS) + [
        "ION/04_packages/kernel/ion_agent_branch_capsule.py",
        "ION/05_context/current/agent_context_branches/BRANCH_CAPSULE_REGISTRY_V0_1.json",
    ]


@dataclass(frozen=True)
class BranchCapsuleRecord:
    context_instance_id: str
    branch_id: str
    agent_tag: str
    conversation_tag: str
    parent_context_id: str = DEFAULT_PARENT_CONTEXT_ID
    loaded_refs: tuple[str, ...] = field(default_factory=tuple)
    write_scope: tuple[str, ...] = field(default_factory=tuple)
    settlement_required: bool = True
    accepted_state_authority: bool = False
    branch_type: str = "agent_context_branch"
    parent_branch_id: str | None = None
    task_tag: str | None = None
    root: str | None = None
    status: str = "BRANCH_ACTIVE_CANDIDATE"
    shared_context_write: bool = False
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": REGISTRY_SCHEMA + ".record",
            "context_instance_id": self.context_instance_id,
            "branch_id": self.branch_id,
            "branch_type": self.branch_type,
            "agent_tag": self.agent_tag,
            "conversation_tag": self.conversation_tag,
            "task_tag": self.task_tag,
            "parent_context_id": self.parent_context_id,
            "parent_branch_id": self.parent_branch_id,
            "root": self.root,
            "loaded_refs": list(self.loaded_refs),
            "write_scope": list(self.write_scope),
            "shared_context_write": self.shared_context_write,
            "settlement_required": self.settlement_required,
            "accepted_state_authority": self.accepted_state_authority,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "authority": {
                "production_authority": False,
                "deployment_authority": False,
                "secrets_authority": False,
                "accepted_state_authority": self.accepted_state_authority,
            },
        }

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "BranchCapsuleRecord":
        return cls(
            context_instance_id=str(payload["context_instance_id"]),
            branch_id=str(payload["branch_id"]),
            agent_tag=str(payload["agent_tag"]),
            conversation_tag=str(payload["conversation_tag"]),
            parent_context_id=str(payload.get("parent_context_id") or DEFAULT_PARENT_CONTEXT_ID),
            loaded_refs=tuple(str(x) for x in payload.get("loaded_refs", [])),
            write_scope=tuple(str(x) for x in payload.get("write_scope", [])),
            settlement_required=bool(payload.get("settlement_required", True)),
            accepted_state_authority=bool(payload.get("accepted_state_authority", False)),
            branch_type=str(payload.get("branch_type") or "agent_context_branch"),
            parent_branch_id=payload.get("parent_branch_id"),
            task_tag=payload.get("task_tag"),
            root=payload.get("root"),
            status=str(payload.get("status") or "BRANCH_ACTIVE_CANDIDATE"),
            shared_context_write=bool(payload.get("shared_context_write", False)),
            created_at=str(payload.get("created_at") or _now()),
            updated_at=str(payload.get("updated_at") or _now()),
        )


def branch_dir_for(root: Path, record: BranchCapsuleRecord | Mapping[str, Any]) -> Path:
    if isinstance(record, BranchCapsuleRecord):
        conversation = record.conversation_tag
        agent = record.agent_tag
    else:
        conversation = str(record["conversation_tag"])
        agent = str(record["agent_tag"])
    return root / BRANCH_ROOT / normalize_tag(conversation) / normalize_tag(agent)


def build_branch_capsule_record(
    *,
    root: Path | str,
    context_instance_id: str,
    branch_id: str,
    agent_tag: str,
    conversation_tag: str,
    parent_context_id: str = DEFAULT_PARENT_CONTEXT_ID,
    loaded_refs: Sequence[str] | None = None,
    write_scope: Sequence[str] | None = None,
    branch_type: str = "agent_context_branch",
    parent_branch_id: str | None = None,
    task_tag: str | None = None,
    settlement_required: bool = True,
    accepted_state_authority: bool = False,
) -> BranchCapsuleRecord:
    root_path = Path(root).resolve()
    return BranchCapsuleRecord(
        context_instance_id=context_instance_id,
        branch_id=branch_id,
        branch_type=branch_type,
        agent_tag=normalize_tag(agent_tag),
        conversation_tag=normalize_tag(conversation_tag),
        parent_context_id=parent_context_id,
        parent_branch_id=parent_branch_id,
        task_tag=normalize_tag(task_tag) if task_tag else None,
        root=root_path.as_posix(),
        loaded_refs=tuple(loaded_refs or default_loaded_refs()),
        write_scope=tuple(_norm_rel(path, root_path) for path in (write_scope or ())),
        settlement_required=settlement_required,
        accepted_state_authority=accepted_state_authority,
    )


def validate_branch_record(
    root: Path | str,
    record: BranchCapsuleRecord | Mapping[str, Any],
    *,
    active_claims: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    payload = record.to_dict() if isinstance(record, BranchCapsuleRecord) else dict(record)
    findings: list[dict[str, Any]] = []

    required = (
        "context_instance_id",
        "branch_id",
        "agent_tag",
        "conversation_tag",
        "parent_context_id",
        "loaded_refs",
        "write_scope",
        "settlement_required",
        "accepted_state_authority",
    )
    for key in required:
        if key not in payload or payload[key] in (None, "", []):
            findings.append({"code": "missing_required_branch_identity_field", "field": key})

    declared_root = payload.get("root")
    if declared_root and Path(str(declared_root)).resolve() != root_path:
        findings.append(
            {
                "code": "root_mismatch",
                "declared_root": str(declared_root),
                "actual_root": root_path.as_posix(),
            }
        )

    if payload.get("accepted_state_authority") is not False:
        findings.append({"code": "accepted_state_authority_must_be_false"})
    if payload.get("settlement_required") is not True:
        findings.append({"code": "settlement_required_must_be_true"})
    if payload.get("shared_context_write"):
        findings.append({"code": "shared_context_write_forbidden"})

    loaded_refs = payload.get("loaded_refs", [])
    if not isinstance(loaded_refs, list):
        findings.append({"code": "loaded_refs_must_be_list"})
    write_scope = payload.get("write_scope", [])
    if not isinstance(write_scope, list):
        findings.append({"code": "write_scope_must_be_list"})
        write_scope = []
    if not write_scope:
        findings.append({"code": "write_scope_required_for_material_edits"})

    for path in write_scope:
        rel = _norm_rel(str(path), root_path)
        if Path(rel).is_absolute() or rel.startswith(".."):
            findings.append({"code": "write_scope_must_be_repo_relative", "path": str(path)})
        if _is_shared_context_surface(rel):
            findings.append({"code": "shared_context_surface_in_write_scope", "path": rel})
        if _is_checkpoint_surface(rel):
            findings.append({"code": "checkpoint_assignment_surface_forbidden", "path": rel})

    for claim in active_claims or ():
        claim_branch = str(claim.get("branch_id") or "")
        if claim_branch == str(payload.get("branch_id") or ""):
            continue
        for left in write_scope:
            for right in claim.get("write_scope", []) or []:
                if _paths_overlap(str(left), str(right)):
                    findings.append(
                        {
                            "code": "write_scope_overlap",
                            "branch_id": payload.get("branch_id"),
                            "other_branch_id": claim_branch,
                            "path": _norm_rel(str(left)),
                            "other_path": _norm_rel(str(right)),
                        }
                    )

    return {
        "ok": not findings,
        "verdict": READY_VERDICT if not findings else BLOCKED_VERDICT,
        "branch_id": payload.get("branch_id"),
        "context_instance_id": payload.get("context_instance_id"),
        "findings": findings,
    }


def validate_branch_capsule(
    root: Path | str,
    record: BranchCapsuleRecord | Mapping[str, Any],
    *,
    active_claims: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Alias with protocol language for branch-capsule validation."""

    return validate_branch_record(root, record, active_claims=active_claims)


def detect_wrong_context_drift(
    root: Path | str,
    record: BranchCapsuleRecord | Mapping[str, Any],
    *,
    active_claims: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return only findings that indicate wrong-context or unsafe branch drift."""

    validation = validate_branch_record(root, record, active_claims=active_claims)
    drift_codes = {
        "root_mismatch",
        "missing_required_branch_identity_field",
        "shared_context_write_forbidden",
        "shared_context_surface_in_write_scope",
        "checkpoint_assignment_surface_forbidden",
        "write_scope_overlap",
        "accepted_state_authority_must_be_false",
        "settlement_required_must_be_true",
    }
    drift = [item for item in validation["findings"] if item.get("code") in drift_codes]
    return {
        "ok": not drift,
        "verdict": READY_VERDICT if not drift else BLOCKED_VERDICT,
        "branch_id": validation.get("branch_id"),
        "context_instance_id": validation.get("context_instance_id"),
        "drift_findings": drift,
    }


def render_context_identity_card(record: BranchCapsuleRecord | Mapping[str, Any]) -> str:
    payload = record.to_dict() if isinstance(record, BranchCapsuleRecord) else dict(record)
    refs = "\n".join(f"- {ref}" for ref in payload.get("loaded_refs", []))
    scope = "\n".join(f"- {path}" for path in payload.get("write_scope", []))
    return (
        "### ION BRANCH CONTEXT IDENTITY\n"
        f"- context_instance_id: {payload.get('context_instance_id')}\n"
        f"- branch_id: {payload.get('branch_id')}\n"
        f"- agent_tag: {payload.get('agent_tag')}\n"
        f"- conversation_tag: {payload.get('conversation_tag')}\n"
        f"- parent_context_id: {payload.get('parent_context_id')}\n"
        f"- settlement_required: {payload.get('settlement_required')}\n"
        f"- accepted_state_authority: {payload.get('accepted_state_authority')}\n"
        "\n### LOADED REFS\n"
        f"{refs or '- none'}\n"
        "\n### WRITE SCOPE\n"
        f"{scope or '- none'}\n"
    )


def render_branch_capsule(record: BranchCapsuleRecord | Mapping[str, Any]) -> str:
    return render_context_identity_card(record) + (
        "\n### LAW\n"
        "- This capsule is candidate branch context only.\n"
        "- Shared Capsule/Mini/HOT_CONTEXT/STATUS/ROUTE writes are forbidden.\n"
        "- Accepted state requires settlement.\n"
        "- C-number/checkpoint assignment is forbidden to this branch.\n"
    )


def branch_status(record: BranchCapsuleRecord | Mapping[str, Any], validation: Mapping[str, Any]) -> dict[str, Any]:
    payload = record.to_dict() if isinstance(record, BranchCapsuleRecord) else dict(record)
    return {
        "schema": "ion.agent_branch_capsule.status.v1",
        "branch_id": payload.get("branch_id"),
        "context_instance_id": payload.get("context_instance_id"),
        "agent_tag": payload.get("agent_tag"),
        "conversation_tag": payload.get("conversation_tag"),
        "status": payload.get("status", "BRANCH_ACTIVE_CANDIDATE"),
        "guard_verdict": validation.get("verdict"),
        "guard_ok": validation.get("ok"),
        "findings": validation.get("findings", []),
        "updated_at": _now(),
        "accepted_state_authority": False,
    }


def update_branch_registry(root: Path | str, record: BranchCapsuleRecord | Mapping[str, Any]) -> dict[str, Any]:
    root_path = Path(root).resolve()
    payload = record.to_dict() if isinstance(record, BranchCapsuleRecord) else dict(record)
    registry_path = root_path / BRANCH_REGISTRY_PATH
    registry = _read_json(
        registry_path,
        {
            "schema": REGISTRY_SCHEMA,
            "status": "ACTIVE_PROVISIONAL",
            "registered_branches": [],
            "authority": {"accepted_state_authority": False},
        },
    )
    rows = [row for row in registry.get("registered_branches", []) if row.get("branch_id") != payload["branch_id"]]
    branch_dir = branch_dir_for(root_path, payload)
    rows.append(
        {
            "branch_id": payload["branch_id"],
            "context_instance_id": payload["context_instance_id"],
            "agent_tag": payload["agent_tag"],
            "conversation_tag": payload["conversation_tag"],
            "status": payload.get("status", "BRANCH_ACTIVE_CANDIDATE"),
            "branch_record_path": _as_rel(branch_dir / "BRANCH_RECORD.json", root_path),
            "write_scope": payload.get("write_scope", []),
            "settlement_required": payload.get("settlement_required", True),
            "accepted_state_authority": False,
            "updated_at": _now(),
        }
    )
    registry["registered_branches"] = sorted(rows, key=lambda row: row["branch_id"])
    registry["updated_at"] = _now()
    _write_json(registry_path, registry)
    return registry


def write_branch_capsule(root: Path | str, record: BranchCapsuleRecord | Mapping[str, Any]) -> dict[str, str]:
    root_path = Path(root).resolve()
    branch = BranchCapsuleRecord.from_mapping(record) if not isinstance(record, BranchCapsuleRecord) else record
    validation = validate_branch_record(root_path, branch)
    branch_dir = branch_dir_for(root_path, branch)
    branch_dir.mkdir(parents=True, exist_ok=True)
    _write_json(branch_dir / "BRANCH_RECORD.json", branch.to_dict())
    _write_json(branch_dir / "STATUS.json", branch_status(branch, validation))
    _write_json(branch_dir / "LOADED_REFS.json", {"loaded_refs": list(branch.loaded_refs), "updated_at": _now()})
    (branch_dir / "CAPSULE.md").write_text(render_branch_capsule(branch), encoding="utf-8")
    (branch_dir / "SETTLEMENT_REQUESTS").mkdir(exist_ok=True)
    update_branch_registry(root_path, branch)
    return {
        "branch_dir": _as_rel(branch_dir, root_path),
        "record_path": _as_rel(branch_dir / "BRANCH_RECORD.json", root_path),
        "status_path": _as_rel(branch_dir / "STATUS.json", root_path),
        "capsule_path": _as_rel(branch_dir / "CAPSULE.md", root_path),
    }


def load_branch_record(root: Path | str, branch_record_path: str | Path) -> BranchCapsuleRecord:
    root_path = Path(root).resolve()
    path = Path(branch_record_path)
    if not path.is_absolute():
        path = root_path / path
    return BranchCapsuleRecord.from_mapping(json.loads(path.read_text(encoding="utf-8")))


def load_branch_records(root: Path | str) -> list[dict[str, Any]]:
    root_path = Path(root).resolve()
    if not (root_path / BRANCH_ROOT).exists():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted((root_path / BRANCH_ROOT).rglob("BRANCH_RECORD.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            records.append({"branch_record_path": _as_rel(path, root_path), "error": str(exc)})
            continue
        payload.setdefault("branch_record_path", _as_rel(path, root_path))
        records.append(payload)
    return records


def load_active_branch_claims(root: Path | str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    registry = _read_json(Path(root).resolve() / BRANCH_REGISTRY_PATH, {"registered_branches": []})
    for row in registry.get("registered_branches", []) or []:
        if str(row.get("status") or "").upper().startswith(("BRANCH_ACTIVE", "ACTIVE")):
            rows.append(row)
    return rows


def material_work_preflight(
    root: Path | str,
    *,
    branch_record: BranchCapsuleRecord | Mapping[str, Any] | None = None,
    branch_record_path: str | Path | None = None,
    requested_write_scope: Sequence[str] | None = None,
    active_claims: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    if branch_record is None and branch_record_path is not None:
        branch_record = load_branch_record(root_path, branch_record_path)
    if branch_record is None:
        return {
            "ok": False,
            "verdict": BLOCKED_VERDICT,
            "findings": [{"code": "branch_identity_required_for_material_work"}],
        }

    payload = branch_record.to_dict() if isinstance(branch_record, BranchCapsuleRecord) else dict(branch_record)
    claims = list(active_claims) if active_claims is not None else load_active_branch_claims(root_path)
    validation = validate_branch_record(root_path, payload, active_claims=claims)
    findings = list(validation["findings"])
    declared_scope = [str(path) for path in payload.get("write_scope", []) or []]

    for requested in requested_write_scope or ():
        rel = _norm_rel(requested, root_path)
        if _is_shared_context_surface(rel):
            findings.append({"code": "requested_write_scope_shared_context_surface_forbidden", "path": rel})
        if _is_checkpoint_surface(rel):
            findings.append({"code": "requested_write_scope_checkpoint_surface_forbidden", "path": rel})
        if declared_scope and not any(_paths_overlap(rel, declared) for declared in declared_scope):
            findings.append(
                {
                    "code": "requested_write_scope_not_declared_in_branch",
                    "path": rel,
                    "branch_id": payload.get("branch_id"),
                }
            )

    return {
        "ok": not findings,
        "verdict": READY_VERDICT if not findings else BLOCKED_VERDICT,
        "branch_id": payload.get("branch_id"),
        "context_instance_id": payload.get("context_instance_id"),
        "findings": findings,
    }


def build_settlement_request(
    root: Path | str,
    record: BranchCapsuleRecord | Mapping[str, Any],
    *,
    workload_diff: Sequence[str],
    guard_evidence: Mapping[str, Any],
    result_summary: str,
    source_refs: Sequence[str] | None = None,
    packet_id: str | None = None,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    payload = record.to_dict() if isinstance(record, BranchCapsuleRecord) else dict(record)
    token = _timestamp_token()
    packet_id = packet_id or f"SETTLE_{normalize_tag(payload['branch_id']).upper()}_{token}"
    return {
        "schema": SETTLEMENT_PACKET_SCHEMA,
        "packet_id": packet_id,
        "status": "CANDIDATE_SETTLEMENT_REQUEST",
        "created_at": _now(),
        "root": root_path.as_posix(),
        "branch_identity": {
            "context_instance_id": payload.get("context_instance_id"),
            "branch_id": payload.get("branch_id"),
            "agent_tag": payload.get("agent_tag"),
            "conversation_tag": payload.get("conversation_tag"),
            "parent_context_id": payload.get("parent_context_id"),
        },
        "requested_write_scope": payload.get("write_scope", []),
        "loaded_refs": payload.get("loaded_refs", []),
        "source_refs": list(source_refs or []),
        "guard_evidence": dict(guard_evidence),
        "workload_diff": list(workload_diff),
        "result_summary": result_summary,
        "settlement_request": {
            "requested_action": "REVIEW_BRANCH_CANDIDATE_OUTPUT",
            "direct_accepted_state_merge": False,
            "requires_human_or_steward_review": True,
        },
        "authority": {
            "production_authority": False,
            "deployment_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
        },
        "non_claims": [
            "not accepted state",
            "no C-number assigned",
            "no shared context mutation claimed",
            "no production deployment",
        ],
    }


def write_settlement_request(
    root: Path | str,
    record: BranchCapsuleRecord | Mapping[str, Any],
    *,
    workload_diff: Sequence[str],
    guard_evidence: Mapping[str, Any],
    result_summary: str,
    source_refs: Sequence[str] | None = None,
    packet_id: str | None = None,
) -> dict[str, str]:
    root_path = Path(root).resolve()
    packet = build_settlement_request(
        root_path,
        record,
        workload_diff=workload_diff,
        guard_evidence=guard_evidence,
        result_summary=result_summary,
        source_refs=source_refs,
        packet_id=packet_id,
    )
    inbox_path = root_path / SETTLEMENT_INBOX / f"{packet['packet_id']}.json"
    _write_json(inbox_path, packet)
    branch_dir = branch_dir_for(root_path, packet["branch_identity"])
    branch_settlement_path = branch_dir / "SETTLEMENT_REQUESTS" / f"{packet['packet_id']}.json"
    _write_json(branch_settlement_path, packet)
    return {
        "packet_id": packet["packet_id"],
        "inbox_path": _as_rel(inbox_path, root_path),
        "branch_settlement_path": _as_rel(branch_settlement_path, root_path),
    }


def settlement_intake_preflight(
    root: Path | str,
    *,
    packet: Mapping[str, Any] | None = None,
    settlement_packet_path: str | Path | None = None,
) -> dict[str, Any]:
    root_path = Path(root).resolve()
    if packet is None and settlement_packet_path is not None:
        path = Path(settlement_packet_path)
        if not path.is_absolute():
            path = root_path / path
        packet = json.loads(path.read_text(encoding="utf-8"))
    if packet is None:
        return {
            "ok": False,
            "verdict": BLOCKED_VERDICT,
            "findings": [{"code": "settlement_packet_required"}],
        }

    findings: list[dict[str, Any]] = []
    identity = packet.get("branch_identity") or {}
    for key in ("context_instance_id", "branch_id", "agent_tag", "conversation_tag", "parent_context_id"):
        if not identity.get(key):
            findings.append({"code": "missing_branch_identity_field", "field": key})

    workload_diff = packet.get("workload_diff")
    if not workload_diff:
        findings.append({"code": "missing_workload_diff"})
    guard = packet.get("guard_evidence")
    if not guard:
        findings.append({"code": "missing_guard_evidence"})
    elif guard.get("ok") is not True:
        findings.append({"code": "guard_evidence_not_ready", "guard_verdict": guard.get("verdict")})

    for path in packet.get("source_refs", []) or []:
        rel = _norm_rel(str(path), root_path)
        if _is_shared_context_surface(rel):
            findings.append({"code": "shared_context_surface_cannot_be_source_ref_for_merge", "path": rel})

    for path in packet.get("requested_write_scope", []) or []:
        rel = _norm_rel(str(path), root_path)
        if _is_checkpoint_surface(rel):
            findings.append({"code": "checkpoint_assignment_forbidden_in_settlement_request", "path": rel})

    if packet.get("settlement_request", {}).get("direct_accepted_state_merge"):
        findings.append({"code": "direct_accepted_state_merge_forbidden"})
    if packet.get("authority", {}).get("accepted_state_authority"):
        findings.append({"code": "accepted_state_authority_forbidden"})

    return {
        "ok": not findings,
        "verdict": READY_VERDICT if not findings else BLOCKED_VERDICT,
        "packet_id": packet.get("packet_id"),
        "branch_id": identity.get("branch_id"),
        "findings": findings,
    }


def _branch_has_settlement_request(root: Path, branch: Mapping[str, Any]) -> bool:
    branch_dir = branch_dir_for(root, branch)
    if (branch_dir / "SETTLEMENT_REQUESTS").exists():
        if any((branch_dir / "SETTLEMENT_REQUESTS").glob("*.json")):
            return True
    branch_id = str(branch.get("branch_id") or "")
    if (root / SETTLEMENT_INBOX).exists():
        for path in (root / SETTLEMENT_INBOX).glob("*.json"):
            try:
                packet = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if packet.get("branch_identity", {}).get("branch_id") == branch_id:
                return True
    return False


def reconcile_branch_registry(root: Path | str, *, write_report: bool = False) -> dict[str, Any]:
    root_path = Path(root).resolve()
    registry = _read_json(root_path / BRANCH_REGISTRY_PATH, {"registered_branches": []})
    registry_rows = registry.get("registered_branches", []) or []
    records = load_branch_records(root_path)
    record_by_id = {str(record.get("branch_id")): record for record in records if record.get("branch_id")}
    findings: list[dict[str, Any]] = []

    for row in registry_rows:
        branch_id = str(row.get("branch_id") or "")
        if not branch_id:
            findings.append({"code": "registry_row_missing_branch_id", "row": row})
            continue
        if branch_id not in record_by_id:
            findings.append({"code": "registry_row_missing_branch_record", "branch_id": branch_id})

    for branch_id, record in record_by_id.items():
        if not any(str(row.get("branch_id") or "") == branch_id for row in registry_rows):
            findings.append({"code": "branch_record_missing_registry_row", "branch_id": branch_id})
        validation = validate_branch_record(root_path, record)
        for item in validation["findings"]:
            findings.append({"code": "branch_record_validation", "branch_id": branch_id, "finding": item})
        if record.get("settlement_required") and not _branch_has_settlement_request(root_path, record):
            findings.append({"code": "missing_settlement_request", "branch_id": branch_id})

    active_records = [
        record
        for record in records
        if str(record.get("status") or "").upper().startswith(("BRANCH_ACTIVE", "ACTIVE"))
    ]
    for index, left in enumerate(active_records):
        for right in active_records[index + 1 :]:
            for left_path in left.get("write_scope", []) or []:
                for right_path in right.get("write_scope", []) or []:
                    if _paths_overlap(str(left_path), str(right_path)):
                        findings.append(
                            {
                                "code": "write_scope_collision",
                                "branch_id": left.get("branch_id"),
                                "other_branch_id": right.get("branch_id"),
                                "path": _norm_rel(str(left_path)),
                                "other_path": _norm_rel(str(right_path)),
                            }
                        )

    snapshot = {
        "schema": "ion.agent_branch_capsule.reconciliation_report.v1",
        "created_at": _now(),
        "registry_path": BRANCH_REGISTRY_PATH.as_posix(),
        "registered_branch_count": len(registry_rows),
        "branch_record_count": len(records),
        "active_branch_count": len(active_records),
        "ok": not findings,
        "verdict": READY_VERDICT if not findings else BLOCKED_VERDICT,
        "findings": findings,
    }
    if write_report:
        report_path = root_path / BRANCH_ROOT / "BRANCH_RECONCILIATION_REPORT_V0_1.json"
        _write_json(report_path, snapshot)
        snapshot["report_path"] = _as_rel(report_path, root_path)
    return snapshot


def build_branch_cockpit_snapshot(root: Path | str) -> dict[str, Any]:
    root_path = Path(root).resolve()
    reconciliation = reconcile_branch_registry(root_path)
    registry = _read_json(root_path / BRANCH_REGISTRY_PATH, {"registered_branches": []})
    return {
        "schema": "ion.agent_branch_capsule.cockpit_snapshot.v1",
        "created_at": _now(),
        "status": "READY" if reconciliation["ok"] else "NEEDS_ATTENTION",
        "branch_count": len(registry.get("registered_branches", []) or []),
        "reconciliation": reconciliation,
        "accepted_state_authority": False,
    }


def create_branch_capsule(
    root: Path | str,
    *,
    context_instance_id: str,
    branch_id: str,
    agent_tag: str,
    conversation_tag: str,
    parent_context_id: str = DEFAULT_PARENT_CONTEXT_ID,
    loaded_refs: Sequence[str] | None = None,
    write_scope: Sequence[str] | None = None,
    task_tag: str | None = None,
) -> dict[str, Any]:
    record = build_branch_capsule_record(
        root=root,
        context_instance_id=context_instance_id,
        branch_id=branch_id,
        agent_tag=agent_tag,
        conversation_tag=conversation_tag,
        parent_context_id=parent_context_id,
        loaded_refs=loaded_refs,
        write_scope=write_scope,
        task_tag=task_tag,
    )
    validation = validate_branch_record(root, record)
    paths = write_branch_capsule(root, record)
    return {
        "ok": validation["ok"],
        "record": record.to_dict(),
        "validation": validation,
        "paths": paths,
        "accepted_state_authority": False,
    }


def _cli_create(args: argparse.Namespace) -> dict[str, Any]:
    return create_branch_capsule(
        args.ion_root,
        context_instance_id=args.context_instance_id,
        branch_id=args.branch_id,
        agent_tag=args.agent_tag,
        conversation_tag=args.conversation_tag,
        parent_context_id=args.parent_context_id,
        loaded_refs=args.loaded_ref or None,
        write_scope=args.write_scope or None,
        task_tag=args.task_tag,
    )


def _cli_preflight(args: argparse.Namespace) -> dict[str, Any]:
    return material_work_preflight(
        args.ion_root,
        branch_record_path=args.branch_record,
        requested_write_scope=args.write_scope or None,
    )


def _cli_reconcile(args: argparse.Namespace) -> dict[str, Any]:
    return reconcile_branch_registry(args.ion_root, write_report=args.write_report)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ION agent branch capsule helper")
    parser.add_argument("--ion-root", default=os.getcwd())
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create")
    create.add_argument("--context-instance-id", required=True)
    create.add_argument("--branch-id", required=True)
    create.add_argument("--agent-tag", required=True)
    create.add_argument("--conversation-tag", required=True)
    create.add_argument("--parent-context-id", default=DEFAULT_PARENT_CONTEXT_ID)
    create.add_argument("--task-tag")
    create.add_argument("--loaded-ref", action="append")
    create.add_argument("--write-scope", action="append")
    create.set_defaults(func=_cli_create)

    preflight = sub.add_parser("preflight")
    preflight.add_argument("--branch-record", required=True)
    preflight.add_argument("--write-scope", action="append")
    preflight.set_defaults(func=_cli_preflight)

    reconcile = sub.add_parser("reconcile")
    reconcile.add_argument("--write-report", action="store_true")
    reconcile.set_defaults(func=_cli_reconcile)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    payload = args.func(args)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("ok", True) is not False else 2


if __name__ == "__main__":
    raise SystemExit(main())
