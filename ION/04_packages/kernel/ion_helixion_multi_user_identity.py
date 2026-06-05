"""Helixion multi-user identity and rank schema candidate.

This module models user/app ranks for the Helixion cockpit. It is deliberately
separate from ``ion_rank_authority.py``, which models ION settlement rank.

The schema here does not grant production, live execution, accepted-state, or
secrets authority. Rank is treated as a ceiling only; project, object, approval,
route, and path checks remain separate gates.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
import hashlib
from typing import Any, Iterable, Mapping

from .model import StrEnum


SCHEMA_ID = "ion.helixion_multi_user_identity.v0_1"
RANK_SCHEMA_ID = "ion.helixion_multi_user_rank_ceiling.v0_1"
SESSION_SCHEMA_ID = "ion.helixion_multi_user_session_projection.v0_1"
DECISION_SCHEMA_ID = "ion.helixion_multi_user_rank_preview_decision.v0_1"

AUTHORITY_FALSE: dict[str, bool] = {
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
}


class HelixionSubjectType(StrEnum):
    HUMAN_USER = "human_user"
    GUEST_USER = "guest_user"
    AI_SERVICE_ACCOUNT = "ai_service_account"
    SYSTEM_SERVICE = "system_service"
    BREAK_GLASS_STEWARD = "break_glass_steward"


class HelixionRankCeiling(StrEnum):
    FOUNDER_ROOT_STEWARD = "founder_root_steward"
    STEWARD_ADMIN = "steward_admin"
    LEAD_ARCHITECT = "lead_architect"
    BUILDER_CONTRIBUTOR = "builder_contributor"
    REVIEWER_AUDITOR = "reviewer_auditor"
    VIEWER_CLIENT = "viewer_client"
    GUEST = "guest"
    AI_SERVICE_ACCOUNT = "ai_service_account"


class HelixionCapability(StrEnum):
    PUBLIC_DOC_READ = "public_doc_read"
    PUBLIC_PREVIEW_READ = "public_preview_read"
    CURATED_DOC_READ = "curated_doc_read"
    CURATED_SCREENSHOT_READ = "curated_screenshot_read"
    ASSIGNED_DOC_READ = "assigned_doc_read"
    ASSIGNED_DIFF_READ = "assigned_diff_read"
    ASSIGNED_RECEIPT_READ = "assigned_receipt_read"
    COMMENT = "comment"
    SOURCE_READ = "source_read"
    SOURCE_DRAFT_WRITE = "source_draft_write"
    SOURCE_APPLY_WRITE = "source_apply_write"
    SENSITIVE_SOURCE_REQUEST = "sensitive_source_request"
    PREVIEW_LAUNCH = "preview_launch"
    LOCAL_CONTROL_REQUEST = "local_control_request"
    PROJECT_POLICY_ADMIN = "project_policy_admin"
    MEMBER_ADMIN = "member_admin"
    WORKSPACE_ADMIN = "workspace_admin"
    POLICY_ADMIN = "policy_admin"
    DELEGATED_READ = "delegated_read"
    DELEGATED_DRAFT = "delegated_draft"
    DELEGATED_PREVIEW_CAPTURE = "delegated_preview_capture"
    SECRET_VALUE_READ = "secret_value_read"
    PRODUCTION_DEPLOY = "production_deploy"
    ACCEPTED_STATE_CLAIM = "accepted_state_claim"


class HelixionSensitivityTier(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    SOURCE = "source"
    SENSITIVE_SOURCE = "sensitive_source"
    LOCAL_CONTROL = "local_control"
    SECRET_BOUNDARY = "secret_boundary"
    PRODUCTION_LIVE_ACCEPTED_STATE = "production_live_accepted_state"


class HelixionRouteClass(StrEnum):
    PUBLIC_STATUS = "public_status"
    COCKPIT_UI = "cockpit_ui"
    PROJECT_READ = "project_read"
    SOURCE_READ = "source_read"
    DRAFT_WRITE = "draft_write"
    APPLY_WRITE = "apply_write"
    LOCAL_CONTROL = "local_control"
    AI_ACTION = "ai_action"
    ADMIN_POLICY = "admin_policy"


class HelixionAccessStatus(StrEnum):
    ACTIVE = "active"
    PENDING = "pending"
    REVOKED = "revoked"
    EXPIRED = "expired"


RANK_ORDER: tuple[HelixionRankCeiling, ...] = (
    HelixionRankCeiling.GUEST,
    HelixionRankCeiling.VIEWER_CLIENT,
    HelixionRankCeiling.REVIEWER_AUDITOR,
    HelixionRankCeiling.BUILDER_CONTRIBUTOR,
    HelixionRankCeiling.LEAD_ARCHITECT,
    HelixionRankCeiling.STEWARD_ADMIN,
    HelixionRankCeiling.FOUNDER_ROOT_STEWARD,
)

RANK_CAPABILITY_CEILINGS: dict[HelixionRankCeiling, frozenset[HelixionCapability]] = {
    HelixionRankCeiling.GUEST: frozenset(
        {
            HelixionCapability.PUBLIC_DOC_READ,
            HelixionCapability.PUBLIC_PREVIEW_READ,
        }
    ),
    HelixionRankCeiling.VIEWER_CLIENT: frozenset(
        {
            HelixionCapability.PUBLIC_DOC_READ,
            HelixionCapability.PUBLIC_PREVIEW_READ,
            HelixionCapability.CURATED_DOC_READ,
            HelixionCapability.CURATED_SCREENSHOT_READ,
        }
    ),
    HelixionRankCeiling.REVIEWER_AUDITOR: frozenset(
        {
            HelixionCapability.PUBLIC_DOC_READ,
            HelixionCapability.PUBLIC_PREVIEW_READ,
            HelixionCapability.CURATED_DOC_READ,
            HelixionCapability.CURATED_SCREENSHOT_READ,
            HelixionCapability.ASSIGNED_DOC_READ,
            HelixionCapability.ASSIGNED_DIFF_READ,
            HelixionCapability.ASSIGNED_RECEIPT_READ,
            HelixionCapability.COMMENT,
        }
    ),
    HelixionRankCeiling.BUILDER_CONTRIBUTOR: frozenset(
        {
            HelixionCapability.PUBLIC_DOC_READ,
            HelixionCapability.PUBLIC_PREVIEW_READ,
            HelixionCapability.CURATED_DOC_READ,
            HelixionCapability.CURATED_SCREENSHOT_READ,
            HelixionCapability.ASSIGNED_DOC_READ,
            HelixionCapability.ASSIGNED_DIFF_READ,
            HelixionCapability.ASSIGNED_RECEIPT_READ,
            HelixionCapability.COMMENT,
            HelixionCapability.SOURCE_READ,
            HelixionCapability.SOURCE_DRAFT_WRITE,
            HelixionCapability.PREVIEW_LAUNCH,
        }
    ),
    HelixionRankCeiling.LEAD_ARCHITECT: frozenset(
        {
            HelixionCapability.PUBLIC_DOC_READ,
            HelixionCapability.PUBLIC_PREVIEW_READ,
            HelixionCapability.CURATED_DOC_READ,
            HelixionCapability.CURATED_SCREENSHOT_READ,
            HelixionCapability.ASSIGNED_DOC_READ,
            HelixionCapability.ASSIGNED_DIFF_READ,
            HelixionCapability.ASSIGNED_RECEIPT_READ,
            HelixionCapability.COMMENT,
            HelixionCapability.SOURCE_READ,
            HelixionCapability.SOURCE_DRAFT_WRITE,
            HelixionCapability.SOURCE_APPLY_WRITE,
            HelixionCapability.SENSITIVE_SOURCE_REQUEST,
            HelixionCapability.PREVIEW_LAUNCH,
            HelixionCapability.LOCAL_CONTROL_REQUEST,
        }
    ),
    HelixionRankCeiling.STEWARD_ADMIN: frozenset(
        {
            HelixionCapability.PUBLIC_DOC_READ,
            HelixionCapability.PUBLIC_PREVIEW_READ,
            HelixionCapability.CURATED_DOC_READ,
            HelixionCapability.CURATED_SCREENSHOT_READ,
            HelixionCapability.ASSIGNED_DOC_READ,
            HelixionCapability.ASSIGNED_DIFF_READ,
            HelixionCapability.ASSIGNED_RECEIPT_READ,
            HelixionCapability.COMMENT,
            HelixionCapability.SOURCE_READ,
            HelixionCapability.SOURCE_DRAFT_WRITE,
            HelixionCapability.SOURCE_APPLY_WRITE,
            HelixionCapability.SENSITIVE_SOURCE_REQUEST,
            HelixionCapability.PREVIEW_LAUNCH,
            HelixionCapability.LOCAL_CONTROL_REQUEST,
            HelixionCapability.PROJECT_POLICY_ADMIN,
            HelixionCapability.MEMBER_ADMIN,
            HelixionCapability.WORKSPACE_ADMIN,
        }
    ),
    HelixionRankCeiling.FOUNDER_ROOT_STEWARD: frozenset(
        {
            HelixionCapability.PUBLIC_DOC_READ,
            HelixionCapability.PUBLIC_PREVIEW_READ,
            HelixionCapability.CURATED_DOC_READ,
            HelixionCapability.CURATED_SCREENSHOT_READ,
            HelixionCapability.ASSIGNED_DOC_READ,
            HelixionCapability.ASSIGNED_DIFF_READ,
            HelixionCapability.ASSIGNED_RECEIPT_READ,
            HelixionCapability.COMMENT,
            HelixionCapability.SOURCE_READ,
            HelixionCapability.SOURCE_DRAFT_WRITE,
            HelixionCapability.SOURCE_APPLY_WRITE,
            HelixionCapability.SENSITIVE_SOURCE_REQUEST,
            HelixionCapability.PREVIEW_LAUNCH,
            HelixionCapability.LOCAL_CONTROL_REQUEST,
            HelixionCapability.PROJECT_POLICY_ADMIN,
            HelixionCapability.MEMBER_ADMIN,
            HelixionCapability.WORKSPACE_ADMIN,
            HelixionCapability.POLICY_ADMIN,
        }
    ),
    HelixionRankCeiling.AI_SERVICE_ACCOUNT: frozenset(
        {
            HelixionCapability.DELEGATED_READ,
            HelixionCapability.DELEGATED_DRAFT,
            HelixionCapability.DELEGATED_PREVIEW_CAPTURE,
        }
    ),
}

HARD_DENIED_CAPABILITIES: frozenset[HelixionCapability] = frozenset(
    {
        HelixionCapability.SECRET_VALUE_READ,
        HelixionCapability.PRODUCTION_DEPLOY,
        HelixionCapability.ACCEPTED_STATE_CLAIM,
    }
)

OBJECT_GRANT_REQUIRED: frozenset[HelixionCapability] = frozenset(
    {
        HelixionCapability.CURATED_DOC_READ,
        HelixionCapability.CURATED_SCREENSHOT_READ,
        HelixionCapability.ASSIGNED_DOC_READ,
        HelixionCapability.ASSIGNED_DIFF_READ,
        HelixionCapability.ASSIGNED_RECEIPT_READ,
        HelixionCapability.COMMENT,
        HelixionCapability.SOURCE_READ,
        HelixionCapability.SOURCE_DRAFT_WRITE,
        HelixionCapability.SOURCE_APPLY_WRITE,
        HelixionCapability.SENSITIVE_SOURCE_REQUEST,
        HelixionCapability.PREVIEW_LAUNCH,
        HelixionCapability.LOCAL_CONTROL_REQUEST,
        HelixionCapability.PROJECT_POLICY_ADMIN,
        HelixionCapability.MEMBER_ADMIN,
        HelixionCapability.WORKSPACE_ADMIN,
        HelixionCapability.POLICY_ADMIN,
        HelixionCapability.DELEGATED_READ,
        HelixionCapability.DELEGATED_DRAFT,
        HelixionCapability.DELEGATED_PREVIEW_CAPTURE,
    }
)

APPROVAL_REQUIRED: frozenset[HelixionCapability] = frozenset(
    {
        HelixionCapability.SOURCE_APPLY_WRITE,
        HelixionCapability.SENSITIVE_SOURCE_REQUEST,
        HelixionCapability.LOCAL_CONTROL_REQUEST,
        HelixionCapability.PROJECT_POLICY_ADMIN,
        HelixionCapability.MEMBER_ADMIN,
        HelixionCapability.WORKSPACE_ADMIN,
        HelixionCapability.POLICY_ADMIN,
        HelixionCapability.DELEGATED_DRAFT,
        HelixionCapability.DELEGATED_PREVIEW_CAPTURE,
    }
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _plus_minutes(minutes: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).replace(microsecond=0).isoformat()


def _stable_ref(prefix: str, *parts: object) -> str:
    seed = "|".join(str(part or "") for part in parts).encode("utf-8")
    return f"{prefix}_{hashlib.sha256(seed).hexdigest()[:24]}"


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


def normalize_rank(rank: str | HelixionRankCeiling | None, *, fallback: HelixionRankCeiling = HelixionRankCeiling.GUEST) -> HelixionRankCeiling:
    if isinstance(rank, HelixionRankCeiling):
        return rank
    text = str(rank or "").strip().lower()
    for item in HelixionRankCeiling:
        if item.value == text:
            return item
    return fallback


def normalize_capability(capability: str | HelixionCapability) -> HelixionCapability:
    if isinstance(capability, HelixionCapability):
        return capability
    text = str(capability or "").strip().lower()
    for item in HelixionCapability:
        if item.value == text:
            return item
    raise ValueError(f"unknown Helixion capability:{capability}")


@dataclass(frozen=True)
class HelixionAccessSubject:
    subject_id: str
    subject_type: HelixionSubjectType
    display_handle: str
    rank_ceiling: HelixionRankCeiling
    status: HelixionAccessStatus = HelixionAccessStatus.ACTIVE
    identity_refs: tuple[str, ...] = ()
    created_at: str = field(default_factory=_utc_now)
    authority: Mapping[str, bool] = field(default_factory=lambda: dict(AUTHORITY_FALSE))
    schema_id: str = SCHEMA_ID

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class HelixionWorkspaceMembership:
    subject_id: str
    workspace_id: str
    rank_ceiling: HelixionRankCeiling
    status: HelixionAccessStatus = HelixionAccessStatus.ACTIVE
    capabilities: tuple[HelixionCapability, ...] = ()
    created_at: str = field(default_factory=_utc_now)
    schema_id: str = "ion.helixion_workspace_membership.v0_1"

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class HelixionSessionProjection:
    session_id: str
    subject_id: str
    workspace_id: str
    rank_ceiling: HelixionRankCeiling
    auth_method: str
    issued_at: str
    expires_at: str
    device_id: str | None = None
    aal: str = "aal1"
    status: HelixionAccessStatus = HelixionAccessStatus.ACTIVE
    authority: Mapping[str, bool] = field(default_factory=lambda: dict(AUTHORITY_FALSE))
    schema_id: str = SESSION_SCHEMA_ID

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class HelixionConnectionRef:
    connection_ref: str
    subject_id: str
    workspace_id: str
    scopes: tuple[str, ...]
    status: HelixionAccessStatus = HelixionAccessStatus.ACTIVE
    expires_at: str = field(default_factory=lambda: _plus_minutes(60))
    secret_material_emitted: bool = False
    schema_id: str = "ion.helixion_connection_ref.v0_1"

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


@dataclass(frozen=True)
class HelixionAccessObject:
    object_id: str
    object_type: str
    workspace_id: str
    sensitivity: HelixionSensitivityTier
    virtual_path: str
    parent_object_id: str | None = None
    canonical_ref: str | None = None
    schema_id: str = "ion.helixion_access_object.v0_1"

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


def rank_capability_ceiling(rank: str | HelixionRankCeiling) -> dict[str, Any]:
    """Return the capability ceiling for an app/user rank."""

    normalized = normalize_rank(rank)
    capabilities = tuple(sorted(RANK_CAPABILITY_CEILINGS[normalized], key=str))
    return {
        "schema_id": RANK_SCHEMA_ID,
        "rank_ceiling": str(normalized),
        "rank_order": RANK_ORDER.index(normalized) if normalized in RANK_ORDER else None,
        "capability_ceiling": [str(item) for item in capabilities],
        "hard_denies": [str(item) for item in sorted(HARD_DENIED_CAPABILITIES, key=str)],
        "rank_is_permission": False,
        "rank_is_ceiling": True,
        "requires_object_grants": True,
        "authority": dict(AUTHORITY_FALSE),
    }


def rank_ceiling_allows(rank: str | HelixionRankCeiling, capability: str | HelixionCapability) -> bool:
    normalized_rank = normalize_rank(rank)
    normalized_capability = normalize_capability(capability)
    if normalized_capability in HARD_DENIED_CAPABILITIES:
        return False
    return normalized_capability in RANK_CAPABILITY_CEILINGS[normalized_rank]


def capability_requires_object_grant(capability: str | HelixionCapability) -> bool:
    return normalize_capability(capability) in OBJECT_GRANT_REQUIRED


def capability_requires_approval(capability: str | HelixionCapability) -> bool:
    return normalize_capability(capability) in APPROVAL_REQUIRED


def preview_rank_capability_decision(
    rank: str | HelixionRankCeiling,
    capability: str | HelixionCapability,
    *,
    object_grant: bool = False,
    approval: bool = False,
) -> dict[str, Any]:
    """Preview rank/object/approval gates before the full evaluator exists."""

    normalized_rank = normalize_rank(rank)
    normalized_capability = normalize_capability(capability)
    reasons: list[str] = []
    if normalized_capability in HARD_DENIED_CAPABILITIES:
        reasons.append("HARD_DENY_AUTHORITY_BOUNDARY")
    elif not rank_ceiling_allows(normalized_rank, normalized_capability):
        reasons.append("RANK_CEILING_BELOW_CAPABILITY")
    if capability_requires_object_grant(normalized_capability) and not object_grant:
        reasons.append("OBJECT_GRANT_REQUIRED")
    if capability_requires_approval(normalized_capability) and not approval:
        reasons.append("APPROVAL_REQUIRED")
    return {
        "schema_id": DECISION_SCHEMA_ID,
        "allowed": not reasons,
        "rank_ceiling": str(normalized_rank),
        "capability": str(normalized_capability),
        "object_grant": object_grant,
        "approval": approval,
        "reasons": reasons,
        "rank_is_permission": False,
        "rank_is_ceiling": True,
        "path_authority_evaluated": False,
        "route_authority_evaluated": False,
        "authority": dict(AUTHORITY_FALSE),
    }


def rank_from_cockpit_principal(principal: Mapping[str, Any]) -> HelixionRankCeiling:
    """Project current cockpit login methods into conservative rank ceilings."""

    explicit = principal.get("helixion_rank") or principal.get("rank_ceiling")
    if explicit:
        return normalize_rank(str(explicit), fallback=HelixionRankCeiling.VIEWER_CLIENT)
    auth_method = str(principal.get("auth_method") or "").strip().lower()
    token_label = str(principal.get("token_label") or "").strip().lower()
    subject = str(principal.get("subject") or "").strip().lower()
    if auth_method == "permission_token" and (token_label == "public-token" or subject == "public-token"):
        return HelixionRankCeiling.FOUNDER_ROOT_STEWARD
    if auth_method == "google" and token_label == "google_allowlist":
        return HelixionRankCeiling.STEWARD_ADMIN
    if auth_method in {"permission_token", "google"}:
        return HelixionRankCeiling.VIEWER_CLIENT
    return HelixionRankCeiling.GUEST


def subject_from_cockpit_principal(principal: Mapping[str, Any]) -> HelixionAccessSubject:
    auth_method = str(principal.get("auth_method") or "unknown").strip().lower()
    raw_handle = str(principal.get("email") or principal.get("subject") or principal.get("token_label") or "guest").strip()
    display_handle = raw_handle or "guest"
    subject_type = HelixionSubjectType.GUEST_USER if auth_method in {"", "unknown", "guest"} else HelixionSubjectType.HUMAN_USER
    identity_ref = _stable_ref("idref", auth_method, display_handle)
    subject_id = _stable_ref("usr", auth_method, display_handle)
    return HelixionAccessSubject(
        subject_id=subject_id,
        subject_type=subject_type,
        display_handle=display_handle,
        rank_ceiling=rank_from_cockpit_principal(principal),
        identity_refs=(identity_ref,),
    )


def session_projection_from_cockpit_principal(
    principal: Mapping[str, Any],
    *,
    workspace_id: str = "wsp_local_operator",
) -> dict[str, Any]:
    """Build a rank-bearing read-only projection for the current cockpit session."""

    subject = subject_from_cockpit_principal(principal)
    issued_at = str(principal.get("issued_at") or _utc_now())
    expires_at = str(principal.get("expires_at") or _plus_minutes(60))
    session_id = str(principal.get("session_id") or _stable_ref("sess", subject.subject_id, issued_at))
    session = HelixionSessionProjection(
        session_id=session_id,
        subject_id=subject.subject_id,
        workspace_id=workspace_id,
        rank_ceiling=subject.rank_ceiling,
        auth_method=str(principal.get("auth_method") or "unknown"),
        issued_at=issued_at,
        expires_at=expires_at,
    )
    membership = HelixionWorkspaceMembership(
        subject_id=subject.subject_id,
        workspace_id=workspace_id,
        rank_ceiling=subject.rank_ceiling,
    )
    connection = HelixionConnectionRef(
        connection_ref=_stable_ref("conn", session_id, subject.subject_id, workspace_id),
        subject_id=subject.subject_id,
        workspace_id=workspace_id,
        scopes=tuple(sorted(str(item) for item in RANK_CAPABILITY_CEILINGS[subject.rank_ceiling])),
    )
    return {
        "schema_id": "ion.helixion_cockpit_session_access_projection.v0_1",
        "subject": subject.to_dict(),
        "session": session.to_dict(),
        "membership": membership.to_dict(),
        "connection": connection.to_dict(),
        "rank_ceiling": rank_capability_ceiling(subject.rank_ceiling),
        "rank_is_permission": False,
        "rank_is_ceiling": True,
        "enforcement_active": False,
        "authority": dict(AUTHORITY_FALSE),
    }


def build_ai_service_subject(
    *,
    agent_id: str,
    workspace_id: str,
    delegated_capabilities: Iterable[HelixionCapability | str] = (),
    expires_at: str | None = None,
) -> dict[str, Any]:
    """Build a scoped AI subject projection without inheriting a human rank."""

    subject = HelixionAccessSubject(
        subject_id=_stable_ref("agent", agent_id, workspace_id),
        subject_type=HelixionSubjectType.AI_SERVICE_ACCOUNT,
        display_handle=agent_id,
        rank_ceiling=HelixionRankCeiling.AI_SERVICE_ACCOUNT,
        identity_refs=(_stable_ref("idref", "agent", agent_id),),
    )
    capabilities = tuple(sorted({normalize_capability(item) for item in delegated_capabilities}, key=str))
    unsupported = [str(item) for item in capabilities if item not in RANK_CAPABILITY_CEILINGS[HelixionRankCeiling.AI_SERVICE_ACCOUNT]]
    connection = HelixionConnectionRef(
        connection_ref=_stable_ref("conn", "agent", agent_id, workspace_id),
        subject_id=subject.subject_id,
        workspace_id=workspace_id,
        scopes=tuple(str(item) for item in capabilities if item in RANK_CAPABILITY_CEILINGS[HelixionRankCeiling.AI_SERVICE_ACCOUNT]),
        expires_at=expires_at or _plus_minutes(60),
    )
    return {
        "schema_id": "ion.helixion_ai_service_subject_projection.v0_1",
        "subject": subject.to_dict(),
        "connection": connection.to_dict(),
        "unsupported_delegated_capabilities": unsupported,
        "inherits_human_rank": False,
        "rank_ceiling": rank_capability_ceiling(subject.rank_ceiling),
        "authority": dict(AUTHORITY_FALSE),
    }


def required_identity_access_tables() -> dict[str, Any]:
    return {
        "schema_id": "ion.helixion_identity_access_tables.v0_1",
        "required_tables": [
            "users",
            "identities",
            "organizations",
            "workspaces",
            "workspace_members",
            "domains",
            "projects",
            "project_versions",
            "access_objects",
            "file_roots",
            "file_index",
            "grants",
            "devices",
            "sessions",
            "connections",
            "delegations",
            "action_requests",
            "approvals",
            "audit_events",
            "receipts",
        ],
        "route_classes": [str(item) for item in HelixionRouteClass],
        "sensitivity_tiers": [str(item) for item in HelixionSensitivityTier],
        "rank_ceilings": [str(item) for item in HelixionRankCeiling],
        "rank_is_permission": False,
        "rank_is_ceiling": True,
        "authority": dict(AUTHORITY_FALSE),
    }


def build_identity_access_schema_projection() -> dict[str, Any]:
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _utc_now(),
        "rank_ceilings": {
            str(rank): rank_capability_ceiling(rank)
            for rank in HelixionRankCeiling
        },
        "hard_denied_capabilities": [str(item) for item in sorted(HARD_DENIED_CAPABILITIES, key=str)],
        "object_grant_required_capabilities": [str(item) for item in sorted(OBJECT_GRANT_REQUIRED, key=str)],
        "approval_required_capabilities": [str(item) for item in sorted(APPROVAL_REQUIRED, key=str)],
        "schema_tables": required_identity_access_tables(),
        "authority": dict(AUTHORITY_FALSE),
    }
