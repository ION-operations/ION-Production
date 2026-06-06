"""Helixion collaboration route registry and access projection candidate.

This module is the first implementation slice for project-scoped co-user
collaboration. It does not switch live route enforcement on. It gives the
cockpit a single deny-by-default route catalog, a current-principal projection,
and candidate decisions that can be displayed and tested before sharing claims
are made in the UI.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import re
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

from .ion_helixion_authorization import HelixionAuthorizationRequest, authorize_helixion_access
from .ion_helixion_multi_user_identity import (
    AUTHORITY_FALSE,
    HelixionCapability,
    HelixionRouteClass,
    HelixionSensitivityTier,
    session_projection_from_cockpit_principal,
)
from .model import StrEnum


SCHEMA_ID = "ion.helixion_collaboration_access.v0_1"
ROUTE_REGISTRY_SCHEMA_ID = "ion.helixion_collaboration_route_registry.v0_1"
DEFAULT_WORKSPACE_ID = "wsp_local_operator"
REGISTRY_STATUS = "candidate_not_live_route_wired"


class HelixionRouteDefaultOutcome(StrEnum):
    DENY = "deny"


class HelixionObjectResolver(StrEnum):
    NONE = "none"
    SESSION_PRINCIPAL = "session_principal"
    COCKPIT_SURFACE = "cockpit_surface"
    PROJECT_PORTFOLIO = "project_portfolio"
    PROJECT_FAMILY = "project_family"
    PROJECT_LAUNCH = "project_launch"
    PROJECT_WORKBENCH = "project_workbench"
    CHAT_SESSION = "chat_session"
    CHAT_ROOM = "chat_room"
    AGENT_COMMS_ROOM = "agent_comms_room"
    AGENT_RUN = "agent_run"
    LOCAL_SERVICE = "local_service"
    SYSTEM_DIAGNOSTIC = "system_diagnostic"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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


def _normalize_path(path: str) -> str:
    parsed = urlparse(path or "/")
    clean = parsed.path or "/"
    if len(clean) > 1:
        clean = clean.rstrip("/")
    return clean


def _route_id(methods: tuple[str, ...], path_template: str) -> str:
    seed = path_template.strip("/").replace("/", "_").replace("{", "").replace("}", "").replace("-", "_")
    return f"{'_'.join(methods).lower()}_{seed or 'root'}"


@dataclass(frozen=True)
class HelixionRegisteredRoute:
    path_template: str
    methods: tuple[str, ...]
    route_class: HelixionRouteClass
    capability: HelixionCapability
    sensitivity: HelixionSensitivityTier
    object_resolver: HelixionObjectResolver = HelixionObjectResolver.NONE
    mutation: bool = False
    same_origin_required: bool = False
    localhost_context_required: bool = False
    object_grant_required: bool = False
    approval_required: bool = False
    receipt_required: bool = False
    shareable_with_co_users: bool = False
    description: str = ""
    route_id: str | None = None
    default_outcome: HelixionRouteDefaultOutcome = HelixionRouteDefaultOutcome.DENY
    status: str = REGISTRY_STATUS
    authority: Mapping[str, bool] = field(default_factory=lambda: dict(AUTHORITY_FALSE))
    schema_id: str = "ion.helixion_registered_route.v0_1"

    def __post_init__(self) -> None:
        object.__setattr__(self, "methods", tuple(str(item).upper() for item in self.methods))
        if self.route_id is None:
            object.__setattr__(self, "route_id", _route_id(self.methods, self.path_template))

    def to_dict(self) -> dict[str, Any]:
        return _record_dict(self)


def route(
    path_template: str,
    methods: tuple[str, ...],
    route_class: HelixionRouteClass,
    capability: HelixionCapability,
    sensitivity: HelixionSensitivityTier,
    *,
    object_resolver: HelixionObjectResolver = HelixionObjectResolver.NONE,
    mutation: bool = False,
    same_origin_required: bool = False,
    localhost_context_required: bool = False,
    object_grant_required: bool = False,
    approval_required: bool = False,
    receipt_required: bool = False,
    shareable_with_co_users: bool = False,
    description: str = "",
) -> HelixionRegisteredRoute:
    return HelixionRegisteredRoute(
        path_template=path_template,
        methods=methods,
        route_class=route_class,
        capability=capability,
        sensitivity=sensitivity,
        object_resolver=object_resolver,
        mutation=mutation,
        same_origin_required=same_origin_required,
        localhost_context_required=localhost_context_required,
        object_grant_required=object_grant_required,
        approval_required=approval_required,
        receipt_required=receipt_required,
        shareable_with_co_users=shareable_with_co_users,
        description=description,
    )


REGISTERED_ROUTES: tuple[HelixionRegisteredRoute, ...] = (
    route(
        "/cockpit/session/access.json",
        ("GET",),
        HelixionRouteClass.COCKPIT_UI,
        HelixionCapability.PUBLIC_DOC_READ,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.SESSION_PRINCIPAL,
        description="Current principal, rank ceiling, and collaboration access posture.",
    ),
    route(
        "/cockpit/collab/model.json",
        ("GET",),
        HelixionRouteClass.COCKPIT_UI,
        HelixionCapability.PUBLIC_DOC_READ,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.COCKPIT_SURFACE,
        description="Candidate collaboration control surface model.",
    ),
    route(
        "/cockpit/devsecops/model.json",
        ("GET",),
        HelixionRouteClass.COCKPIT_UI,
        HelixionCapability.PUBLIC_DOC_READ,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.COCKPIT_SURFACE,
        description="Read-only developer security operations projection; no live controls.",
    ),
    route(
        "/cockpit/model.json",
        ("GET",),
        HelixionRouteClass.COCKPIT_UI,
        HelixionCapability.PUBLIC_PREVIEW_READ,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.COCKPIT_SURFACE,
        description="Main cockpit projection. Not a co-user sharing surface.",
    ),
    route(
        "/cockpit/system/model.json",
        ("GET",),
        HelixionRouteClass.COCKPIT_UI,
        HelixionCapability.CURATED_DOC_READ,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.SYSTEM_DIAGNOSTIC,
        description="System diagnostics model; developer/operator projection only.",
    ),
    route(
        "/cockpit/codex/model.json",
        ("GET",),
        HelixionRouteClass.PROJECT_READ,
        HelixionCapability.ASSIGNED_RECEIPT_READ,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.CHAT_SESSION,
        object_grant_required=True,
        shareable_with_co_users=True,
        description="Codex workbench projection requires explicit chat/session grants before sharing.",
    ),
    route(
        "/cockpit/chat/model.json",
        ("GET",),
        HelixionRouteClass.PROJECT_READ,
        HelixionCapability.ASSIGNED_RECEIPT_READ,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.CHAT_SESSION,
        object_grant_required=True,
        shareable_with_co_users=True,
        description="Dual Codex chat model requires explicit chat grants before sharing.",
    ),
    route(
        "/cockpit/chat/archive.json",
        ("GET",),
        HelixionRouteClass.PROJECT_READ,
        HelixionCapability.ASSIGNED_RECEIPT_READ,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.CHAT_SESSION,
        object_grant_required=True,
        shareable_with_co_users=True,
        description="Codex archive windows are never globally visible.",
    ),
    route(
        "/cockpit/ide/model.json",
        ("GET",),
        HelixionRouteClass.SOURCE_READ,
        HelixionCapability.SOURCE_READ,
        HelixionSensitivityTier.SOURCE,
        object_resolver=HelixionObjectResolver.PROJECT_WORKBENCH,
        object_grant_required=True,
        receipt_required=True,
        description="IDE source surfaces require object grants and path policy.",
    ),
    route(
        "/cockpit/projects/model.json",
        ("GET",),
        HelixionRouteClass.PROJECT_READ,
        HelixionCapability.CURATED_DOC_READ,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.PROJECT_PORTFOLIO,
        object_grant_required=True,
        shareable_with_co_users=True,
        description="Project mission projection; co-users see only granted objects.",
    ),
    route(
        "/cockpit/apps/model.json",
        ("GET",),
        HelixionRouteClass.PROJECT_READ,
        HelixionCapability.CURATED_SCREENSHOT_READ,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.PROJECT_PORTFOLIO,
        object_grant_required=True,
        shareable_with_co_users=True,
        description="App preview catalog; co-users see granted previews only.",
    ),
    route(
        "/projects/portfolio.json",
        ("GET",),
        HelixionRouteClass.PROJECT_READ,
        HelixionCapability.CURATED_DOC_READ,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.PROJECT_PORTFOLIO,
        object_grant_required=True,
        shareable_with_co_users=True,
        description="Public project portfolio projection.",
    ),
    route(
        "/projects/surface.json",
        ("GET",),
        HelixionRouteClass.PROJECT_READ,
        HelixionCapability.CURATED_DOC_READ,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.PROJECT_PORTFOLIO,
        object_grant_required=True,
        shareable_with_co_users=True,
        description="Project surface projection.",
    ),
    route(
        "/cockpit/projects/launch/start",
        ("POST",),
        HelixionRouteClass.LOCAL_CONTROL,
        HelixionCapability.PREVIEW_LAUNCH,
        HelixionSensitivityTier.LOCAL_CONTROL,
        object_resolver=HelixionObjectResolver.PROJECT_LAUNCH,
        mutation=True,
        same_origin_required=True,
        localhost_context_required=True,
        object_grant_required=True,
        approval_required=True,
        receipt_required=True,
        description="Local preview launch control; not enabled for co-users by rank alone.",
    ),
    route(
        "/cockpit/projects/launch/stop",
        ("POST",),
        HelixionRouteClass.LOCAL_CONTROL,
        HelixionCapability.LOCAL_CONTROL_REQUEST,
        HelixionSensitivityTier.LOCAL_CONTROL,
        object_resolver=HelixionObjectResolver.PROJECT_LAUNCH,
        mutation=True,
        same_origin_required=True,
        localhost_context_required=True,
        object_grant_required=True,
        approval_required=True,
        receipt_required=True,
        description="Local preview stop control; requires confirmation and local context.",
    ),
    route(
        "/cockpit/projects/launch/status",
        ("POST",),
        HelixionRouteClass.LOCAL_CONTROL,
        HelixionCapability.LOCAL_CONTROL_REQUEST,
        HelixionSensitivityTier.LOCAL_CONTROL,
        object_resolver=HelixionObjectResolver.PROJECT_LAUNCH,
        mutation=True,
        same_origin_required=True,
        localhost_context_required=True,
        object_grant_required=True,
        approval_required=True,
        receipt_required=True,
        description="Local launch status still exposes local control state.",
    ),
    route(
        "/cockpit/projects/launch/diagnostics",
        ("POST",),
        HelixionRouteClass.LOCAL_CONTROL,
        HelixionCapability.LOCAL_CONTROL_REQUEST,
        HelixionSensitivityTier.LOCAL_CONTROL,
        object_resolver=HelixionObjectResolver.PROJECT_LAUNCH,
        mutation=True,
        same_origin_required=True,
        localhost_context_required=True,
        object_grant_required=True,
        approval_required=True,
        receipt_required=True,
        description="Local launch diagnostics can expose local-control state and logs.",
    ),
    route(
        "/cockpit/projects/launch/diagnostics/timeline",
        ("POST",),
        HelixionRouteClass.PROJECT_READ,
        HelixionCapability.ASSIGNED_RECEIPT_READ,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.PROJECT_LAUNCH,
        mutation=True,
        same_origin_required=True,
        object_grant_required=True,
        receipt_required=True,
        shareable_with_co_users=True,
        description="App diagnostics timeline is receipt-scoped and must not expose raw logs.",
    ),
    route(
        "/cockpit/projects/launch/diagnostics/snapshot",
        ("POST",),
        HelixionRouteClass.LOCAL_CONTROL,
        HelixionCapability.PREVIEW_LAUNCH,
        HelixionSensitivityTier.LOCAL_CONTROL,
        object_resolver=HelixionObjectResolver.PROJECT_LAUNCH,
        mutation=True,
        same_origin_required=True,
        localhost_context_required=True,
        object_grant_required=True,
        approval_required=True,
        receipt_required=True,
        description="App diagnostics snapshot remains local-control until redaction and grant gates are live.",
    ),
    route(
        "/cockpit/system/preview_action",
        ("POST",),
        HelixionRouteClass.LOCAL_CONTROL,
        HelixionCapability.LOCAL_CONTROL_REQUEST,
        HelixionSensitivityTier.LOCAL_CONTROL,
        object_resolver=HelixionObjectResolver.SYSTEM_DIAGNOSTIC,
        mutation=True,
        same_origin_required=True,
        localhost_context_required=True,
        object_grant_required=True,
        approval_required=True,
        receipt_required=True,
        description="System action preview is local-control planning and must stay operator scoped.",
    ),
    route(
        "/cockpit/browser-gpt-dom/probe-snapshot",
        ("POST",),
        HelixionRouteClass.AI_ACTION,
        HelixionCapability.DELEGATED_PREVIEW_CAPTURE,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.COCKPIT_SURFACE,
        mutation=True,
        same_origin_required=True,
        object_grant_required=True,
        receipt_required=True,
        description="Browser GPT DOM probe snapshots require auth parity before online collaboration.",
    ),
    route(
        "/projects/cosmos/patch/preview",
        ("POST",),
        HelixionRouteClass.DRAFT_WRITE,
        HelixionCapability.SOURCE_DRAFT_WRITE,
        HelixionSensitivityTier.SOURCE,
        object_resolver=HelixionObjectResolver.PROJECT_WORKBENCH,
        mutation=True,
        same_origin_required=True,
        object_grant_required=True,
        receipt_required=True,
        shareable_with_co_users=True,
        description="Patch preview can be delegated only against granted project slices.",
    ),
    route(
        "/projects/cosmos/patch/apply",
        ("POST",),
        HelixionRouteClass.APPLY_WRITE,
        HelixionCapability.SOURCE_APPLY_WRITE,
        HelixionSensitivityTier.SENSITIVE_SOURCE,
        object_resolver=HelixionObjectResolver.PROJECT_WORKBENCH,
        mutation=True,
        same_origin_required=True,
        object_grant_required=True,
        approval_required=True,
        receipt_required=True,
        description="Patch apply requires explicit approval, path policy, and receipt proof.",
    ),
    route(
        "/cockpit/chat/turn",
        ("POST",),
        HelixionRouteClass.DRAFT_WRITE,
        HelixionCapability.COMMENT,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.CHAT_ROOM,
        mutation=True,
        same_origin_required=True,
        object_grant_required=True,
        receipt_required=True,
        shareable_with_co_users=True,
        description="Chat turns require room membership, not client-chosen author identity.",
    ),
    route(
        "/cockpit/chat/archive/attach",
        ("POST",),
        HelixionRouteClass.DRAFT_WRITE,
        HelixionCapability.COMMENT,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.CHAT_SESSION,
        mutation=True,
        same_origin_required=True,
        object_grant_required=True,
        receipt_required=True,
        description="Archive attach mutates chat context and requires explicit session grant.",
    ),
    route(
        "/cockpit/agents/comms/list",
        ("POST",),
        HelixionRouteClass.PROJECT_READ,
        HelixionCapability.ASSIGNED_RECEIPT_READ,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.AGENT_COMMS_ROOM,
        mutation=True,
        same_origin_required=True,
        object_grant_required=True,
        shareable_with_co_users=True,
        description="Agent comms list is a room-scoped projection.",
    ),
    route(
        "/cockpit/agents/comms/thread",
        ("POST",),
        HelixionRouteClass.PROJECT_READ,
        HelixionCapability.ASSIGNED_RECEIPT_READ,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.AGENT_COMMS_ROOM,
        mutation=True,
        same_origin_required=True,
        object_grant_required=True,
        shareable_with_co_users=True,
        description="Agent comms thread is room-scoped.",
    ),
    route(
        "/cockpit/agents/comms/send",
        ("POST",),
        HelixionRouteClass.DRAFT_WRITE,
        HelixionCapability.COMMENT,
        HelixionSensitivityTier.INTERNAL,
        object_resolver=HelixionObjectResolver.AGENT_COMMS_ROOM,
        mutation=True,
        same_origin_required=True,
        object_grant_required=True,
        receipt_required=True,
        shareable_with_co_users=True,
        description="Human/agent room messages must use the server principal.",
    ),
    route(
        "/cockpit/agents/spawn-template",
        ("POST",),
        HelixionRouteClass.AI_ACTION,
        HelixionCapability.DELEGATED_DRAFT,
        HelixionSensitivityTier.SENSITIVE_SOURCE,
        object_resolver=HelixionObjectResolver.AGENT_RUN,
        mutation=True,
        same_origin_required=True,
        object_grant_required=True,
        approval_required=True,
        receipt_required=True,
        description="Agent spawning is delegated execution, not normal co-user chat.",
    ),
    route(
        "/cockpit/services/restart",
        ("POST",),
        HelixionRouteClass.LOCAL_CONTROL,
        HelixionCapability.LOCAL_CONTROL_REQUEST,
        HelixionSensitivityTier.LOCAL_CONTROL,
        object_resolver=HelixionObjectResolver.LOCAL_SERVICE,
        mutation=True,
        same_origin_required=True,
        localhost_context_required=True,
        object_grant_required=True,
        approval_required=True,
        receipt_required=True,
        description="Local service restart remains operator/local-control only.",
    ),
    route(
        "/cockpit/system/execute_action",
        ("POST",),
        HelixionRouteClass.LOCAL_CONTROL,
        HelixionCapability.LOCAL_CONTROL_REQUEST,
        HelixionSensitivityTier.LOCAL_CONTROL,
        object_resolver=HelixionObjectResolver.SYSTEM_DIAGNOSTIC,
        mutation=True,
        same_origin_required=True,
        localhost_context_required=True,
        object_grant_required=True,
        approval_required=True,
        receipt_required=True,
        description="System diagnostic execution is local-control.",
    ),
)


def _route_pattern(path_template: str) -> re.Pattern[str]:
    escaped = re.escape(_normalize_path(path_template))
    pattern = re.sub(r"\\\{[^/]+\\\}", r"[^/]+", escaped)
    return re.compile(f"^{pattern}$")


def find_registered_route(path: str, *, method: str = "GET") -> tuple[HelixionRegisteredRoute | None, str | None]:
    clean_path = _normalize_path(path)
    clean_method = str(method or "GET").upper()
    method_mismatch = False
    for row in REGISTERED_ROUTES:
        if not _route_pattern(row.path_template).match(clean_path):
            continue
        if clean_method not in row.methods:
            method_mismatch = True
            continue
        return row, None
    if method_mismatch:
        return None, "METHOD_NOT_REGISTERED_FOR_ROUTE"
    return None, "ROUTE_NOT_REGISTERED"


def build_helixion_route_registry_projection() -> dict[str, Any]:
    routes = [row.to_dict() for row in REGISTERED_ROUTES]
    return {
        "schema_id": ROUTE_REGISTRY_SCHEMA_ID,
        "generated_at": _utc_now(),
        "status": REGISTRY_STATUS,
        "deny_by_default": True,
        "live_route_enforcement": False,
        "unknown_routes": "deny",
        "route_count": len(routes),
        "mutation_route_count": sum(1 for row in REGISTERED_ROUTES if row.mutation),
        "shareable_route_count": sum(1 for row in REGISTERED_ROUTES if row.shareable_with_co_users),
        "local_control_route_count": sum(1 for row in REGISTERED_ROUTES if row.route_class == HelixionRouteClass.LOCAL_CONTROL),
        "source_route_count": sum(1 for row in REGISTERED_ROUTES if row.sensitivity in {HelixionSensitivityTier.SOURCE, HelixionSensitivityTier.SENSITIVE_SOURCE}),
        "routes": routes,
        "authority": dict(AUTHORITY_FALSE),
    }


def build_session_access_projection(
    principal: Mapping[str, Any] | None = None,
    *,
    workspace_id: str = DEFAULT_WORKSPACE_ID,
) -> dict[str, Any]:
    return session_projection_from_cockpit_principal(principal or {}, workspace_id=workspace_id)


def evaluate_registered_route_access(
    path: str,
    *,
    method: str = "GET",
    principal: Mapping[str, Any] | None = None,
    workspace_id: str = DEFAULT_WORKSPACE_ID,
    object_grant: bool = False,
    approval: bool = False,
    path_authority: Mapping[str, Any] | None = None,
    localhost_context: bool = False,
) -> dict[str, Any]:
    route_row, finding = find_registered_route(path, method=method)
    session_access = build_session_access_projection(principal, workspace_id=workspace_id)
    subject = session_access.get("subject") if isinstance(session_access.get("subject"), Mapping) else {}
    session = session_access.get("session") if isinstance(session_access.get("session"), Mapping) else {}
    membership = session_access.get("membership") if isinstance(session_access.get("membership"), Mapping) else {}
    if route_row is None:
        return {
            "schema_id": "ion.helixion_collaboration_route_access_decision.v0_1",
            "generated_at": _utc_now(),
            "status": REGISTRY_STATUS,
            "candidate_enforcement_active": False,
            "live_route_enforcement": False,
            "allowed_if_enforced": False,
            "path": _normalize_path(path),
            "method": str(method or "GET").upper(),
            "finding": finding or "ROUTE_NOT_REGISTERED",
            "reasons": [finding or "ROUTE_NOT_REGISTERED"],
            "route": None,
            "session_access": session_access,
            "authority": dict(AUTHORITY_FALSE),
        }

    decision = authorize_helixion_access(
        HelixionAuthorizationRequest(
            subject_id=str(subject.get("subject_id") or "usr_unknown"),
            subject_rank=str(subject.get("rank_ceiling") or "guest"),
            workspace_id=str(session.get("workspace_id") or workspace_id),
            route_class=route_row.route_class,
            capability=route_row.capability,
            object_workspace_id=str(membership.get("workspace_id") or workspace_id),
            sensitivity=route_row.sensitivity,
            object_grant=object_grant,
            approval=approval,
            path_authority=path_authority,
            localhost_context=localhost_context,
        )
    )
    return {
        "schema_id": "ion.helixion_collaboration_route_access_decision.v0_1",
        "generated_at": _utc_now(),
        "status": REGISTRY_STATUS,
        "candidate_enforcement_active": False,
        "live_route_enforcement": False,
        "allowed_if_enforced": decision.allowed,
        "path": _normalize_path(path),
        "method": str(method or "GET").upper(),
        "finding": None if decision.allowed else "CANDIDATE_ROUTE_ACCESS_DENIED",
        "reasons": list(decision.reasons),
        "route": route_row.to_dict(),
        "authorization_decision": decision.to_dict(),
        "session_access": session_access,
        "authority": dict(AUTHORITY_FALSE),
    }


def build_helixion_collaboration_access_model(
    ion_root: str | Path = ".",
    *,
    principal: Mapping[str, Any] | None = None,
    workspace_id: str = DEFAULT_WORKSPACE_ID,
) -> dict[str, Any]:
    root = Path(ion_root).resolve()
    registry = build_helixion_route_registry_projection()
    session_access = build_session_access_projection(principal, workspace_id=workspace_id)
    route_checks = [
        evaluate_registered_route_access("/cockpit/session/access.json", principal=principal, workspace_id=workspace_id),
        evaluate_registered_route_access("/cockpit/collab/model.json", principal=principal, workspace_id=workspace_id),
        evaluate_registered_route_access("/cockpit/projects/model.json", principal=principal, workspace_id=workspace_id),
        evaluate_registered_route_access("/cockpit/chat/archive.json", principal=principal, workspace_id=workspace_id),
        evaluate_registered_route_access("/cockpit/ide/model.json", principal=principal, workspace_id=workspace_id),
        evaluate_registered_route_access("/cockpit/projects/launch/start", method="POST", principal=principal, workspace_id=workspace_id),
    ]
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _utc_now(),
        "root": "local_ion_root_redacted",
        "root_present": root.exists(),
        "status": REGISTRY_STATUS,
        "candidate_packet": "PCKT-COLLAB-001",
        "live_route_enforcement": False,
        "candidate_enforcement_active": False,
        "deny_by_default": True,
        "product_posture": "project_scoped_read_only_first",
        "session_access": session_access,
        "route_registry": registry,
        "route_checks": route_checks,
        "denial_defaults": [
            "unknown_routes_deny",
            "rank_is_ceiling_not_permission",
            "explicit_object_grant_required_for_project_chat_source_and_local_control",
            "source_routes_require_path_policy",
            "local_control_requires_same_origin_localhost_approval_and_receipts",
            "secret_production_live_and_accepted_state_authority_hard_denied",
        ],
        "next_packets": [
            "PCKT-COLLAB-002 durable workspace members grants and share links",
            "PCKT-COLLAB-003 human-aware agent_comms room participants",
            "PCKT-COLLAB-004 Codex chat/archive ACL windows",
            "PCKT-COLLAB-005 live route guard dry-run receipts",
        ],
        "non_claims": [
            "No broad co-user cockpit access is granted by this projection.",
            "No live route enforcement is enabled by this projection.",
            "No production, live execution, accepted-state, or secrets authority is granted.",
        ],
        "authority": dict(AUTHORITY_FALSE),
    }
