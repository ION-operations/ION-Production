"""Artifact-purpose path policy layered on workspace path authority."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ion_path_authority import (
    CLASS_ACTIVE_REPO,
    CLASS_FORBIDDEN_ROOT,
    CLASS_ION_CONTENT,
    CLASS_OUTSIDE_WORKSPACE,
    CLASS_WORKSPACE_EXPORT,
    CLASS_WORKSPACE_SIBLING,
    CLASS_WORKSPACE_VAULT,
    REASON_ALLOWED,
    REASON_ARTIFACT_INSIDE_ACTIVE_REPO,
    WorkspaceAuthority,
    decide_path_authority,
    load_workspace_authority,
)

SCHEMA_ID = "ion.artifact_path_authority_decision.v1"

PURPOSE_CLEAN_EXPORT = "clean_export"
PURPOSE_FULL_PROJECT_PACKAGE = "full_project_package"
PURPOSE_CUSTOM_GPT_UPLOAD_SET = "custom_gpt_upload_set"
PURPOSE_CUSTOM_GPT_SANDBOX_PACKAGE = "custom_gpt_sandbox_package"
PURPOSE_LIFECYCLE_PACKAGE = "lifecycle_package"
PURPOSE_CONTINUITY_TRANSFER_PACKAGE = "continuity_transfer_package"
PURPOSE_GDRIVE_CONTEXT_MIRROR = "gdrive_context_mirror"
PURPOSE_CHATOPS_PAYLOAD = "chatops_payload"
PURPOSE_MCP_CONNECTOR_CONTRACT = "mcp_connector_contract"
PURPOSE_REPORT_ONLY = "report_only"
PURPOSE_TEST_FIXTURE = "test_fixture"

REASON_ARTIFACT_ROOT_CLASS_NOT_ALLOWED = "ARTIFACT_ROOT_CLASS_NOT_ALLOWED"
REASON_ARTIFACT_PURPOSE_UNKNOWN = "ARTIFACT_PURPOSE_UNKNOWN"
REASON_UPLOAD_LIVE_ACTION_FORBIDDEN = "UPLOAD_LIVE_ACTION_FORBIDDEN"


@dataclass(frozen=True)
class ArtifactPurposePolicy:
    purpose: str
    allowed_root_classes: tuple[str, ...]
    must_be_outside_active_repo: bool
    workspace_containment_required: bool
    vault_env_access_forbidden: bool = True
    upload_live_action_allowed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "purpose": self.purpose,
            "allowed_root_classes": list(self.allowed_root_classes),
            "must_be_outside_active_repo": self.must_be_outside_active_repo,
            "workspace_containment_required": self.workspace_containment_required,
            "vault_env_access_forbidden": self.vault_env_access_forbidden,
            "upload_live_action_allowed": self.upload_live_action_allowed,
        }


_REPO_LOCAL_CLASSES = (CLASS_ION_CONTENT, CLASS_ACTIVE_REPO)
_WORKSPACE_PACKAGE_CLASSES = (CLASS_WORKSPACE_EXPORT, CLASS_WORKSPACE_SIBLING, CLASS_ION_CONTENT, CLASS_ACTIVE_REPO)

ARTIFACT_PURPOSES: dict[str, ArtifactPurposePolicy] = {
    PURPOSE_CLEAN_EXPORT: ArtifactPurposePolicy(
        purpose=PURPOSE_CLEAN_EXPORT,
        allowed_root_classes=(CLASS_WORKSPACE_EXPORT,),
        must_be_outside_active_repo=True,
        workspace_containment_required=True,
    ),
    PURPOSE_FULL_PROJECT_PACKAGE: ArtifactPurposePolicy(
        purpose=PURPOSE_FULL_PROJECT_PACKAGE,
        allowed_root_classes=_WORKSPACE_PACKAGE_CLASSES,
        must_be_outside_active_repo=False,
        workspace_containment_required=True,
    ),
    PURPOSE_CUSTOM_GPT_UPLOAD_SET: ArtifactPurposePolicy(
        purpose=PURPOSE_CUSTOM_GPT_UPLOAD_SET,
        allowed_root_classes=_WORKSPACE_PACKAGE_CLASSES,
        must_be_outside_active_repo=False,
        workspace_containment_required=True,
    ),
    PURPOSE_CUSTOM_GPT_SANDBOX_PACKAGE: ArtifactPurposePolicy(
        purpose=PURPOSE_CUSTOM_GPT_SANDBOX_PACKAGE,
        allowed_root_classes=_WORKSPACE_PACKAGE_CLASSES,
        must_be_outside_active_repo=False,
        workspace_containment_required=True,
    ),
    PURPOSE_LIFECYCLE_PACKAGE: ArtifactPurposePolicy(
        purpose=PURPOSE_LIFECYCLE_PACKAGE,
        allowed_root_classes=_WORKSPACE_PACKAGE_CLASSES,
        must_be_outside_active_repo=False,
        workspace_containment_required=True,
    ),
    PURPOSE_CONTINUITY_TRANSFER_PACKAGE: ArtifactPurposePolicy(
        purpose=PURPOSE_CONTINUITY_TRANSFER_PACKAGE,
        allowed_root_classes=_WORKSPACE_PACKAGE_CLASSES,
        must_be_outside_active_repo=False,
        workspace_containment_required=True,
    ),
    PURPOSE_GDRIVE_CONTEXT_MIRROR: ArtifactPurposePolicy(
        purpose=PURPOSE_GDRIVE_CONTEXT_MIRROR,
        allowed_root_classes=(CLASS_WORKSPACE_SIBLING, CLASS_WORKSPACE_EXPORT, CLASS_ION_CONTENT, CLASS_ACTIVE_REPO),
        must_be_outside_active_repo=False,
        workspace_containment_required=True,
    ),
    PURPOSE_CHATOPS_PAYLOAD: ArtifactPurposePolicy(
        purpose=PURPOSE_CHATOPS_PAYLOAD,
        allowed_root_classes=_REPO_LOCAL_CLASSES,
        must_be_outside_active_repo=False,
        workspace_containment_required=True,
    ),
    PURPOSE_MCP_CONNECTOR_CONTRACT: ArtifactPurposePolicy(
        purpose=PURPOSE_MCP_CONNECTOR_CONTRACT,
        allowed_root_classes=_REPO_LOCAL_CLASSES,
        must_be_outside_active_repo=False,
        workspace_containment_required=True,
    ),
    PURPOSE_REPORT_ONLY: ArtifactPurposePolicy(
        purpose=PURPOSE_REPORT_ONLY,
        allowed_root_classes=_REPO_LOCAL_CLASSES,
        must_be_outside_active_repo=False,
        workspace_containment_required=True,
    ),
    PURPOSE_TEST_FIXTURE: ArtifactPurposePolicy(
        purpose=PURPOSE_TEST_FIXTURE,
        allowed_root_classes=(
            CLASS_WORKSPACE_EXPORT,
            CLASS_WORKSPACE_SIBLING,
            CLASS_ION_CONTENT,
            CLASS_ACTIVE_REPO,
        ),
        must_be_outside_active_repo=False,
        workspace_containment_required=True,
    ),
}


def workspace_authority_for_root(root: str | Path | None = None) -> WorkspaceAuthority:
    """Return manifest authority or a local test/workspace fallback."""

    resolved = Path(root or ".").expanduser().resolve(strict=False)
    try:
        authority = load_workspace_authority()
        if resolved in {authority.active_repo_root, authority.workspace_root}:
            return authority
    except Exception:
        pass

    if (resolved / "pyproject.toml").is_file() and (resolved / "ION/REPO_AUTHORITY.md").is_file():
        active_repo_root = resolved
        workspace_root = resolved.parent.resolve(strict=False)
    elif (
        (resolved / "ION_Developement/pyproject.toml").is_file()
        and (resolved / "ION_Developement/ION/REPO_AUTHORITY.md").is_file()
    ):
        workspace_root = resolved
        active_repo_root = (resolved / "ION_Developement").resolve(strict=False)
    else:
        active_repo_root = resolved
        workspace_root = resolved.parent.resolve(strict=False)

    return WorkspaceAuthority(
        workspace_root=workspace_root,
        active_repo_root=active_repo_root,
        ion_content_root=(active_repo_root / "ION").resolve(strict=False),
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


def authorize_artifact_path(
    raw_path: str | Path,
    *,
    purpose: str,
    active_root: str | Path | None = None,
    base_root: str = "active_repo",
    authority: WorkspaceAuthority | None = None,
    live_action: bool = False,
) -> dict[str, Any]:
    policy = ARTIFACT_PURPOSES.get(purpose)
    loaded = authority or workspace_authority_for_root(active_root)
    if policy is None:
        base_decision = decide_path_authority(raw_path, purpose="write", base_root=base_root, authority=loaded)
        return {
            "schema_id": SCHEMA_ID,
            "purpose": purpose,
            "authorized": False,
            "reason_code": REASON_ARTIFACT_PURPOSE_UNKNOWN,
            "raw_path": str(raw_path),
            "resolved_path": base_decision.get("resolved_path"),
            "classification": base_decision.get("classification"),
            "base_root": base_root,
            "policy": None,
            "path_authority": base_decision,
        }

    base_decision = decide_path_authority(raw_path, purpose="write", base_root=base_root, authority=loaded)
    classification = str(base_decision.get("classification") or "")
    authorized = bool(base_decision.get("authorized"))
    reason = str(base_decision.get("reason_code") or REASON_ALLOWED)

    if authorized and policy.workspace_containment_required and classification in {
        CLASS_OUTSIDE_WORKSPACE,
        CLASS_FORBIDDEN_ROOT,
    }:
        authorized = False
        reason = str(base_decision.get("reason_code") or REASON_ARTIFACT_ROOT_CLASS_NOT_ALLOWED)
    if authorized and classification not in policy.allowed_root_classes:
        authorized = False
        reason = REASON_ARTIFACT_ROOT_CLASS_NOT_ALLOWED
    if authorized and policy.must_be_outside_active_repo and classification in {CLASS_ACTIVE_REPO, CLASS_ION_CONTENT}:
        authorized = False
        reason = REASON_ARTIFACT_INSIDE_ACTIVE_REPO
    if authorized and live_action and not policy.upload_live_action_allowed:
        authorized = False
        reason = REASON_UPLOAD_LIVE_ACTION_FORBIDDEN

    return {
        "schema_id": SCHEMA_ID,
        "purpose": purpose,
        "authorized": authorized,
        "reason_code": reason,
        "raw_path": str(raw_path),
        "resolved_path": base_decision.get("resolved_path"),
        "classification": classification,
        "base_root": base_root,
        "policy": policy.to_dict(),
        "path_authority": base_decision,
    }


def require_artifact_path(
    raw_path: str | Path,
    *,
    purpose: str,
    active_root: str | Path | None = None,
    base_root: str = "active_repo",
    authority: WorkspaceAuthority | None = None,
    live_action: bool = False,
) -> Path:
    decision = authorize_artifact_path(
        raw_path,
        purpose=purpose,
        active_root=active_root,
        base_root=base_root,
        authority=authority,
        live_action=live_action,
    )
    if not decision["authorized"]:
        raise ValueError(
            "artifact path authority rejected:"
            f"{decision['purpose']}:{decision['reason_code']}:{decision.get('resolved_path')}"
        )
    return Path(str(decision["resolved_path"]))
