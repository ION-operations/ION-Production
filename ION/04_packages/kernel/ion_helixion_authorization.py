"""Helixion deny-by-default authorization evaluator candidate.

This is the PCKT-MU-002 kernel slice. It evaluates route class, rank ceiling,
workspace/object relationship, sensitivity, approval, and path-authority
evidence in one place. It is not yet wired into live cockpit routes.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from .ion_helixion_multi_user_identity import (
    AUTHORITY_FALSE,
    HelixionAccessStatus,
    HelixionCapability,
    HelixionRankCeiling,
    HelixionRouteClass,
    HelixionSensitivityTier,
    capability_requires_approval,
    normalize_capability,
    normalize_rank,
    preview_rank_capability_decision,
)
from .model import StrEnum


SCHEMA_ID = "ion.helixion_authorization_decision.v0_1"


class HelixionAuthorizationOutcome(StrEnum):
    ALLOW = "allow"
    DENY = "deny"


ROUTE_CAPABILITIES: dict[HelixionRouteClass, frozenset[HelixionCapability]] = {
    HelixionRouteClass.PUBLIC_STATUS: frozenset(
        {
            HelixionCapability.PUBLIC_DOC_READ,
            HelixionCapability.PUBLIC_PREVIEW_READ,
        }
    ),
    HelixionRouteClass.COCKPIT_UI: frozenset(
        {
            HelixionCapability.PUBLIC_DOC_READ,
            HelixionCapability.PUBLIC_PREVIEW_READ,
            HelixionCapability.CURATED_DOC_READ,
            HelixionCapability.CURATED_SCREENSHOT_READ,
        }
    ),
    HelixionRouteClass.PROJECT_READ: frozenset(
        {
            HelixionCapability.CURATED_DOC_READ,
            HelixionCapability.CURATED_SCREENSHOT_READ,
            HelixionCapability.ASSIGNED_DOC_READ,
            HelixionCapability.ASSIGNED_DIFF_READ,
            HelixionCapability.ASSIGNED_RECEIPT_READ,
            HelixionCapability.PUBLIC_PREVIEW_READ,
        }
    ),
    HelixionRouteClass.SOURCE_READ: frozenset(
        {
            HelixionCapability.SOURCE_READ,
        }
    ),
    HelixionRouteClass.DRAFT_WRITE: frozenset(
        {
            HelixionCapability.COMMENT,
            HelixionCapability.SOURCE_DRAFT_WRITE,
            HelixionCapability.DELEGATED_DRAFT,
        }
    ),
    HelixionRouteClass.APPLY_WRITE: frozenset(
        {
            HelixionCapability.SOURCE_APPLY_WRITE,
        }
    ),
    HelixionRouteClass.LOCAL_CONTROL: frozenset(
        {
            HelixionCapability.PREVIEW_LAUNCH,
            HelixionCapability.LOCAL_CONTROL_REQUEST,
            HelixionCapability.DELEGATED_PREVIEW_CAPTURE,
        }
    ),
    HelixionRouteClass.AI_ACTION: frozenset(
        {
            HelixionCapability.DELEGATED_READ,
            HelixionCapability.DELEGATED_DRAFT,
            HelixionCapability.DELEGATED_PREVIEW_CAPTURE,
        }
    ),
    HelixionRouteClass.ADMIN_POLICY: frozenset(
        {
            HelixionCapability.PROJECT_POLICY_ADMIN,
            HelixionCapability.MEMBER_ADMIN,
            HelixionCapability.WORKSPACE_ADMIN,
            HelixionCapability.POLICY_ADMIN,
        }
    ),
}

PATH_AUTHORITY_ROUTE_CLASSES: frozenset[HelixionRouteClass] = frozenset(
    {
        HelixionRouteClass.SOURCE_READ,
        HelixionRouteClass.DRAFT_WRITE,
        HelixionRouteClass.APPLY_WRITE,
        HelixionRouteClass.LOCAL_CONTROL,
    }
)


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


def _normalize_route(route_class: str | HelixionRouteClass) -> HelixionRouteClass:
    if isinstance(route_class, HelixionRouteClass):
        return route_class
    text = str(route_class or "").strip().lower()
    for item in HelixionRouteClass:
        if item.value == text:
            return item
    raise ValueError(f"unknown Helixion route class:{route_class}")


def _normalize_sensitivity(sensitivity: str | HelixionSensitivityTier) -> HelixionSensitivityTier:
    if isinstance(sensitivity, HelixionSensitivityTier):
        return sensitivity
    text = str(sensitivity or "").strip().lower()
    for item in HelixionSensitivityTier:
        if item.value == text:
            return item
    raise ValueError(f"unknown Helixion sensitivity tier:{sensitivity}")


def _normalize_status(status: str | HelixionAccessStatus | None) -> HelixionAccessStatus:
    if isinstance(status, HelixionAccessStatus):
        return status
    text = str(status or HelixionAccessStatus.ACTIVE).strip().lower()
    for item in HelixionAccessStatus:
        if item.value == text:
            return item
    return HelixionAccessStatus.REVOKED


@dataclass(frozen=True)
class HelixionAuthorizationRequest:
    subject_id: str
    subject_rank: HelixionRankCeiling | str
    workspace_id: str
    route_class: HelixionRouteClass | str
    capability: HelixionCapability | str
    object_id: str | None = None
    object_workspace_id: str | None = None
    sensitivity: HelixionSensitivityTier | str = HelixionSensitivityTier.INTERNAL
    object_grant: bool = False
    approval: bool = False
    session_status: HelixionAccessStatus | str = HelixionAccessStatus.ACTIVE
    membership_status: HelixionAccessStatus | str = HelixionAccessStatus.ACTIVE
    connection_status: HelixionAccessStatus | str | None = None
    path_authority: Mapping[str, Any] | None = None
    localhost_context: bool = False


@dataclass(frozen=True)
class HelixionAuthorizationDecision:
    outcome: HelixionAuthorizationOutcome
    allowed: bool
    subject_id: str
    workspace_id: str
    rank_ceiling: str
    route_class: str
    capability: str
    sensitivity: str
    reasons: tuple[str, ...]
    requires_approval: bool
    path_authority_evaluated: bool
    authority: Mapping[str, bool] = field(default_factory=lambda: dict(AUTHORITY_FALSE))
    schema_id: str = SCHEMA_ID

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


def _public_without_membership(route_class: HelixionRouteClass, capability: HelixionCapability, sensitivity: HelixionSensitivityTier) -> bool:
    return (
        route_class == HelixionRouteClass.PUBLIC_STATUS
        and sensitivity == HelixionSensitivityTier.PUBLIC
        and capability in ROUTE_CAPABILITIES[HelixionRouteClass.PUBLIC_STATUS]
    )


def _sensitivity_reasons(
    *,
    route_class: HelixionRouteClass,
    capability: HelixionCapability,
    sensitivity: HelixionSensitivityTier,
    approval: bool,
) -> list[str]:
    reasons: list[str] = []
    if sensitivity == HelixionSensitivityTier.SECRET_BOUNDARY:
        reasons.append("SECRET_BOUNDARY_DENIED")
    elif sensitivity == HelixionSensitivityTier.PRODUCTION_LIVE_ACCEPTED_STATE:
        reasons.append("PRODUCTION_LIVE_ACCEPTED_STATE_DENIED")
    elif sensitivity == HelixionSensitivityTier.SENSITIVE_SOURCE:
        if capability not in {
            HelixionCapability.SOURCE_READ,
            HelixionCapability.SOURCE_APPLY_WRITE,
            HelixionCapability.SENSITIVE_SOURCE_REQUEST,
            HelixionCapability.DELEGATED_READ,
            HelixionCapability.DELEGATED_DRAFT,
        }:
            reasons.append("SENSITIVE_SOURCE_CAPABILITY_MISMATCH")
        if not approval:
            reasons.append("SENSITIVE_SOURCE_APPROVAL_REQUIRED")
    elif sensitivity == HelixionSensitivityTier.LOCAL_CONTROL:
        if route_class != HelixionRouteClass.LOCAL_CONTROL:
            reasons.append("LOCAL_CONTROL_ROUTE_REQUIRED")
        if not approval:
            reasons.append("LOCAL_CONTROL_APPROVAL_REQUIRED")
    elif sensitivity == HelixionSensitivityTier.SOURCE and route_class not in {
        HelixionRouteClass.SOURCE_READ,
        HelixionRouteClass.DRAFT_WRITE,
        HelixionRouteClass.APPLY_WRITE,
        HelixionRouteClass.AI_ACTION,
    }:
        reasons.append("SOURCE_ROUTE_REQUIRED")
    return reasons


def authorize_helixion_access(request: HelixionAuthorizationRequest | Mapping[str, Any]) -> HelixionAuthorizationDecision:
    """Evaluate a Helixion route access request with deny-by-default behavior."""

    if isinstance(request, Mapping):
        req = HelixionAuthorizationRequest(**dict(request))
    else:
        req = request
    rank = normalize_rank(req.subject_rank)
    route_class = _normalize_route(req.route_class)
    capability = normalize_capability(req.capability)
    sensitivity = _normalize_sensitivity(req.sensitivity)
    session_status = _normalize_status(req.session_status)
    membership_status = _normalize_status(req.membership_status)
    connection_status = _normalize_status(req.connection_status) if req.connection_status is not None else None
    reasons: list[str] = []

    if session_status != HelixionAccessStatus.ACTIVE and not _public_without_membership(route_class, capability, sensitivity):
        reasons.append("SESSION_NOT_ACTIVE")
    if connection_status is not None and connection_status != HelixionAccessStatus.ACTIVE:
        reasons.append("CONNECTION_NOT_ACTIVE")
    if membership_status != HelixionAccessStatus.ACTIVE and not _public_without_membership(route_class, capability, sensitivity):
        reasons.append("WORKSPACE_MEMBERSHIP_NOT_ACTIVE")
    if req.object_workspace_id and req.object_workspace_id != req.workspace_id:
        reasons.append("WORKSPACE_OBJECT_MISMATCH")
    if capability not in ROUTE_CAPABILITIES[route_class]:
        reasons.append("ROUTE_CLASS_CAPABILITY_MISMATCH")

    rank_preview = preview_rank_capability_decision(
        rank,
        capability,
        object_grant=req.object_grant,
        approval=req.approval,
    )
    reasons.extend(str(reason) for reason in rank_preview["reasons"])
    reasons.extend(_sensitivity_reasons(route_class=route_class, capability=capability, sensitivity=sensitivity, approval=req.approval))

    path_evaluated = req.path_authority is not None
    path_required = route_class in PATH_AUTHORITY_ROUTE_CLASSES or sensitivity in {
        HelixionSensitivityTier.SOURCE,
        HelixionSensitivityTier.SENSITIVE_SOURCE,
        HelixionSensitivityTier.LOCAL_CONTROL,
        HelixionSensitivityTier.SECRET_BOUNDARY,
    }
    if path_required:
        if req.path_authority is None:
            reasons.append("PATH_AUTHORITY_REQUIRED")
        elif not bool(req.path_authority.get("authorized")):
            reason_code = str(req.path_authority.get("reason_code") or "unknown")
            reasons.append(f"PATH_AUTHORITY_DENIED:{reason_code}")

    if sensitivity == HelixionSensitivityTier.LOCAL_CONTROL and not req.localhost_context:
        reasons.append("LOCALHOST_CONTEXT_REQUIRED")

    unique_reasons = tuple(dict.fromkeys(reasons))
    return HelixionAuthorizationDecision(
        outcome=HelixionAuthorizationOutcome.ALLOW if not unique_reasons else HelixionAuthorizationOutcome.DENY,
        allowed=not unique_reasons,
        subject_id=req.subject_id,
        workspace_id=req.workspace_id,
        rank_ceiling=str(rank),
        route_class=str(route_class),
        capability=str(capability),
        sensitivity=str(sensitivity),
        reasons=unique_reasons,
        requires_approval=capability_requires_approval(capability) or sensitivity in {
            HelixionSensitivityTier.SENSITIVE_SOURCE,
            HelixionSensitivityTier.LOCAL_CONTROL,
        },
        path_authority_evaluated=path_evaluated,
    )


def build_authorization_evaluator_projection() -> dict[str, Any]:
    return {
        "schema_id": "ion.helixion_authorization_evaluator_projection.v0_1",
        "status": "candidate_not_live_route_wired",
        "deny_by_default": True,
        "route_capabilities": {
            str(route): [str(capability) for capability in sorted(capabilities, key=str)]
            for route, capabilities in ROUTE_CAPABILITIES.items()
        },
        "path_authority_required_route_classes": [str(item) for item in sorted(PATH_AUTHORITY_ROUTE_CLASSES, key=str)],
        "authority": dict(AUTHORITY_FALSE),
    }
