"""Helixion file policy and path-authority bridge.

PCKT-MU-004 connects project access objects to local path authority and the
central Helixion authorization evaluator. It is still a candidate kernel slice:
no live cockpit routes are wired here.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from .ion_helixion_authorization import HelixionAuthorizationRequest, authorize_helixion_access
from .ion_helixion_multi_user_identity import (
    AUTHORITY_FALSE,
    HelixionCapability,
    HelixionRankCeiling,
    HelixionRouteClass,
    HelixionSensitivityTier,
    normalize_rank,
)
from .ion_helixion_project_access_inventory import rank_can_inspect_absolute_paths
from .ion_path_authority import WorkspaceAuthority, decide_path_authority
from .model import StrEnum


SCHEMA_ID = "ion.helixion_file_policy_decision.v0_1"


class HelixionFileOperation(StrEnum):
    DOC_READ = "doc_read"
    DIFF_READ = "diff_read"
    SOURCE_READ = "source_read"
    SOURCE_SEARCH = "source_search"
    SOURCE_DRAFT_WRITE = "source_draft_write"
    SOURCE_APPLY_WRITE = "source_apply_write"
    LAUNCH = "launch"
    DIAGNOSTICS = "diagnostics"


OPERATION_RULES: dict[HelixionFileOperation, dict[str, Any]] = {
    HelixionFileOperation.DOC_READ: {
        "route_class": HelixionRouteClass.PROJECT_READ,
        "capability": HelixionCapability.CURATED_DOC_READ,
        "purpose": "read",
        "path_required": True,
        "default_sensitivity": HelixionSensitivityTier.INTERNAL,
    },
    HelixionFileOperation.DIFF_READ: {
        "route_class": HelixionRouteClass.PROJECT_READ,
        "capability": HelixionCapability.ASSIGNED_DIFF_READ,
        "purpose": "read",
        "path_required": True,
        "default_sensitivity": HelixionSensitivityTier.INTERNAL,
    },
    HelixionFileOperation.SOURCE_READ: {
        "route_class": HelixionRouteClass.SOURCE_READ,
        "capability": HelixionCapability.SOURCE_READ,
        "purpose": "read",
        "path_required": True,
        "default_sensitivity": HelixionSensitivityTier.SOURCE,
    },
    HelixionFileOperation.SOURCE_SEARCH: {
        "route_class": HelixionRouteClass.SOURCE_READ,
        "capability": HelixionCapability.SOURCE_READ,
        "purpose": "read",
        "path_required": True,
        "default_sensitivity": HelixionSensitivityTier.SOURCE,
    },
    HelixionFileOperation.SOURCE_DRAFT_WRITE: {
        "route_class": HelixionRouteClass.DRAFT_WRITE,
        "capability": HelixionCapability.SOURCE_DRAFT_WRITE,
        "purpose": "write",
        "path_required": True,
        "default_sensitivity": HelixionSensitivityTier.SOURCE,
    },
    HelixionFileOperation.SOURCE_APPLY_WRITE: {
        "route_class": HelixionRouteClass.APPLY_WRITE,
        "capability": HelixionCapability.SOURCE_APPLY_WRITE,
        "purpose": "write",
        "path_required": True,
        "default_sensitivity": HelixionSensitivityTier.SOURCE,
    },
    HelixionFileOperation.LAUNCH: {
        "route_class": HelixionRouteClass.LOCAL_CONTROL,
        "capability": HelixionCapability.PREVIEW_LAUNCH,
        "purpose": "read",
        "path_required": True,
        "default_sensitivity": HelixionSensitivityTier.LOCAL_CONTROL,
    },
    HelixionFileOperation.DIAGNOSTICS: {
        "route_class": HelixionRouteClass.LOCAL_CONTROL,
        "capability": HelixionCapability.LOCAL_CONTROL_REQUEST,
        "purpose": "read",
        "path_required": True,
        "default_sensitivity": HelixionSensitivityTier.LOCAL_CONTROL,
    },
}


def _enum_value(value: Any) -> Any:
    if isinstance(value, StrEnum):
        return str(value)
    if isinstance(value, tuple):
        return [_enum_value(item) for item in value]
    if isinstance(value, list):
        return [_enum_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _enum_value(item) for key, item in value.items()}
    return value


def _record_dict(record: object) -> dict[str, Any]:
    return _enum_value(asdict(record))


def _normalize_operation(operation: str | HelixionFileOperation) -> HelixionFileOperation:
    if isinstance(operation, HelixionFileOperation):
        return operation
    text = str(operation or "").strip().lower()
    for item in HelixionFileOperation:
        if item.value == text:
            return item
    raise ValueError(f"unknown Helixion file operation:{operation}")


def _normalize_sensitivity(value: Any, fallback: HelixionSensitivityTier) -> HelixionSensitivityTier:
    text = str(value or "").strip().lower()
    for item in HelixionSensitivityTier:
        if item.value == text:
            return item
    return fallback


def _hash_path(value: Any) -> str:
    import hashlib

    return "sha256:" + hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()


def _has_parent_segment(relative_path: str) -> bool:
    return any(part == ".." for part in PurePosixPath(relative_path).parts)


def _is_within(path: Path, parent: Path) -> bool:
    path = path.resolve(strict=False)
    parent = parent.resolve(strict=False)
    return path == parent or parent in path.parents


def _redact_path_authority(decision: Mapping[str, Any] | None, *, rank: HelixionRankCeiling) -> dict[str, Any] | None:
    if decision is None:
        return None
    row = deepcopy(dict(decision))
    if rank_can_inspect_absolute_paths(rank):
        row["path_redacted"] = False
        return row
    for key in ("raw_path", "resolved_path"):
        if row.get(key):
            row[f"{key}_sha256"] = _hash_path(row.get(key))
            row[key] = None
    manifest = row.get("manifest")
    if isinstance(manifest, Mapping):
        redacted_manifest = dict(manifest)
        for key, value in list(redacted_manifest.items()):
            if key.endswith("root") or key.endswith("path") or key in {
                "workspace_root",
                "active_repo_root",
                "ion_content_root",
                "export_root",
                "vault_root",
            }:
                redacted_manifest[f"{key}_sha256"] = _hash_path(value)
                redacted_manifest[key] = None
            elif isinstance(value, list) and key.endswith("roots"):
                redacted_manifest[f"{key}_sha256"] = [_hash_path(item) for item in value]
                redacted_manifest[key] = []
        row["manifest"] = redacted_manifest
    row["path_redacted"] = True
    return row


def _redact_object(access_object: Mapping[str, Any], *, rank: HelixionRankCeiling) -> dict[str, Any]:
    row = deepcopy(dict(access_object))
    if not rank_can_inspect_absolute_paths(rank) and row.get("canonical_ref"):
        row["canonical_ref_sha256"] = row.get("canonical_ref_sha256") or _hash_path(row.get("canonical_ref"))
        row["canonical_ref"] = None
        row["canonical_ref_redacted"] = True
    return row


def find_access_object(inventory: Mapping[str, Any], object_ref: str) -> dict[str, Any] | None:
    for item in inventory.get("objects") or []:
        if not isinstance(item, Mapping):
            continue
        if item.get("object_id") == object_ref or item.get("virtual_path") == object_ref:
            return dict(item)
    return None


def _resolve_target_path(access_object: Mapping[str, Any], relative_path: str = "") -> tuple[Path | None, list[str]]:
    canonical = str(access_object.get("canonical_ref") or "").strip()
    reasons: list[str] = []
    if not canonical:
        return None, ["OBJECT_CANONICAL_REF_MISSING"]
    root = Path(canonical).expanduser().resolve(strict=False)
    rel = relative_path.strip()
    if not rel:
        return root, []
    if PurePosixPath(rel).is_absolute() or Path(rel).is_absolute():
        return None, ["ABSOLUTE_CHILD_PATH_FORBIDDEN"]
    if _has_parent_segment(rel):
        return None, ["PARENT_SEGMENT_FORBIDDEN"]
    target = (root / rel).resolve(strict=False)
    if not _is_within(target, root):
        reasons.append("OBJECT_ROOT_ESCAPE")
    return target, reasons


@dataclass(frozen=True)
class HelixionFilePolicyRequest:
    subject_id: str
    rank_ceiling: HelixionRankCeiling | str
    workspace_id: str
    object_ref: str
    operation: HelixionFileOperation | str
    relative_path: str = ""
    object_grant: bool = False
    approval: bool = False
    localhost_context: bool = False


def decide_helixion_file_policy(
    inventory: Mapping[str, Any],
    request: HelixionFilePolicyRequest | Mapping[str, Any],
    *,
    path_authority: WorkspaceAuthority | None = None,
    manifest_path: str | Path | None = None,
) -> dict[str, Any]:
    """Return a file-policy decision for an access object and operation."""

    req = HelixionFilePolicyRequest(**dict(request)) if isinstance(request, Mapping) else request
    rank = normalize_rank(req.rank_ceiling)
    operation = _normalize_operation(req.operation)
    rule = OPERATION_RULES[operation]
    access_object = find_access_object(inventory, req.object_ref)
    reasons: list[str] = []
    path_decision: dict[str, Any] | None = None
    target_path, target_reasons = (None, ["OBJECT_NOT_FOUND"])

    if access_object is not None:
        target_path, target_reasons = _resolve_target_path(access_object, req.relative_path)
    reasons.extend(target_reasons)
    if target_path is not None and rule["path_required"]:
        path_decision = decide_path_authority(
            target_path,
            purpose=str(rule["purpose"]),
            base_root="workspace",
            manifest_path=manifest_path,
            authority=path_authority,
        )
        if not path_decision.get("authorized"):
            reasons.append(f"PATH_AUTHORITY_DENIED:{path_decision.get('reason_code')}")

    sensitivity = _normalize_sensitivity(
        (access_object or {}).get("sensitivity") if access_object else None,
        rule["default_sensitivity"],
    )
    # Local-control operations are treated as local-control even when the
    # underlying object is a source root.
    if operation in {HelixionFileOperation.LAUNCH, HelixionFileOperation.DIAGNOSTICS}:
        sensitivity = HelixionSensitivityTier.LOCAL_CONTROL

    auth_decision = authorize_helixion_access(
        HelixionAuthorizationRequest(
            subject_id=req.subject_id,
            subject_rank=rank,
            workspace_id=req.workspace_id,
            object_workspace_id=str((access_object or {}).get("workspace_id") or req.workspace_id),
            route_class=rule["route_class"],
            capability=rule["capability"],
            sensitivity=sensitivity,
            object_grant=req.object_grant,
            approval=req.approval,
            path_authority=path_decision,
            localhost_context=req.localhost_context,
        )
    )
    reasons.extend(auth_decision.reasons)
    unique_reasons = tuple(dict.fromkeys(reasons))
    allowed = not unique_reasons
    return {
        "schema_id": SCHEMA_ID,
        "allowed": allowed,
        "operation": str(operation),
        "subject_id": req.subject_id,
        "workspace_id": req.workspace_id,
        "rank_ceiling": str(rank),
        "object_ref": req.object_ref,
        "relative_path": req.relative_path,
        "object": _redact_object(access_object, rank=rank) if access_object else None,
        "target_virtual_path": _target_virtual_path(access_object, req.relative_path) if access_object else "",
        "path_authority": _redact_path_authority(path_decision, rank=rank),
        "authorization": auth_decision.to_dict(),
        "reasons": list(unique_reasons),
        "path_authority_evaluated": path_decision is not None,
        "authority": dict(AUTHORITY_FALSE),
    }


def _target_virtual_path(access_object: Mapping[str, Any], relative_path: str) -> str:
    base = str(access_object.get("virtual_path") or "")
    rel = relative_path.strip().strip("/")
    if not rel:
        return base
    return f"{base}/files/{rel}"


def build_file_policy_projection() -> dict[str, Any]:
    return {
        "schema_id": "ion.helixion_file_policy_projection.v0_1",
        "status": "candidate_not_live_route_wired",
        "operations": {
            str(operation): {
                "route_class": str(rule["route_class"]),
                "capability": str(rule["capability"]),
                "purpose": str(rule["purpose"]),
                "path_required": bool(rule["path_required"]),
                "default_sensitivity": str(rule["default_sensitivity"]),
            }
            for operation, rule in OPERATION_RULES.items()
        },
        "absolute_paths_redacted_for_lower_ranks": True,
        "child_paths_forbid_parent_segments": True,
        "authority": dict(AUTHORITY_FALSE),
    }
