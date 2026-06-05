from kernel.ion_helixion_authorization import (
    HelixionAuthorizationRequest,
    authorize_helixion_access,
    build_authorization_evaluator_projection,
)
from kernel.ion_helixion_multi_user_identity import (
    HelixionAccessStatus,
    HelixionCapability,
    HelixionRankCeiling,
    HelixionRouteClass,
    HelixionSensitivityTier,
)


AUTHORIZED_PATH = {"authorized": True, "reason_code": "AUTHORIZED"}
DENIED_PATH = {"authorized": False, "reason_code": "DOTENV_WRITE_FORBIDDEN"}


def test_public_status_allows_public_guest_without_membership():
    decision = authorize_helixion_access(
        HelixionAuthorizationRequest(
            subject_id="guest",
            subject_rank=HelixionRankCeiling.GUEST,
            workspace_id="public",
            route_class=HelixionRouteClass.PUBLIC_STATUS,
            capability=HelixionCapability.PUBLIC_DOC_READ,
            sensitivity=HelixionSensitivityTier.PUBLIC,
            membership_status=HelixionAccessStatus.REVOKED,
        )
    )

    assert decision.allowed is True
    assert decision.to_dict()["outcome"] == "allow"
    assert decision.authority["production_authority"] is False


def test_viewer_cannot_read_source_even_with_object_grant_and_path_authority():
    decision = authorize_helixion_access(
        HelixionAuthorizationRequest(
            subject_id="usr_viewer",
            subject_rank=HelixionRankCeiling.VIEWER_CLIENT,
            workspace_id="wsp",
            object_workspace_id="wsp",
            route_class=HelixionRouteClass.SOURCE_READ,
            capability=HelixionCapability.SOURCE_READ,
            sensitivity=HelixionSensitivityTier.SOURCE,
            object_grant=True,
            path_authority=AUTHORIZED_PATH,
        )
    )

    assert decision.allowed is False
    assert "RANK_CEILING_BELOW_CAPABILITY" in decision.reasons


def test_builder_source_read_requires_object_grant_and_path_authority():
    missing_grant = authorize_helixion_access(
        HelixionAuthorizationRequest(
            subject_id="usr_builder",
            subject_rank=HelixionRankCeiling.BUILDER_CONTRIBUTOR,
            workspace_id="wsp",
            object_workspace_id="wsp",
            route_class=HelixionRouteClass.SOURCE_READ,
            capability=HelixionCapability.SOURCE_READ,
            sensitivity=HelixionSensitivityTier.SOURCE,
            path_authority=AUTHORIZED_PATH,
        )
    )
    missing_path = authorize_helixion_access(
        HelixionAuthorizationRequest(
            subject_id="usr_builder",
            subject_rank=HelixionRankCeiling.BUILDER_CONTRIBUTOR,
            workspace_id="wsp",
            object_workspace_id="wsp",
            route_class=HelixionRouteClass.SOURCE_READ,
            capability=HelixionCapability.SOURCE_READ,
            sensitivity=HelixionSensitivityTier.SOURCE,
            object_grant=True,
        )
    )
    allowed = authorize_helixion_access(
        HelixionAuthorizationRequest(
            subject_id="usr_builder",
            subject_rank=HelixionRankCeiling.BUILDER_CONTRIBUTOR,
            workspace_id="wsp",
            object_workspace_id="wsp",
            route_class=HelixionRouteClass.SOURCE_READ,
            capability=HelixionCapability.SOURCE_READ,
            sensitivity=HelixionSensitivityTier.SOURCE,
            object_grant=True,
            path_authority=AUTHORIZED_PATH,
        )
    )

    assert missing_grant.allowed is False
    assert "OBJECT_GRANT_REQUIRED" in missing_grant.reasons
    assert missing_path.allowed is False
    assert "PATH_AUTHORITY_REQUIRED" in missing_path.reasons
    assert allowed.allowed is True


def test_workspace_mismatch_and_path_denial_are_explicit():
    decision = authorize_helixion_access(
        HelixionAuthorizationRequest(
            subject_id="usr_builder",
            subject_rank=HelixionRankCeiling.BUILDER_CONTRIBUTOR,
            workspace_id="wsp_a",
            object_workspace_id="wsp_b",
            route_class=HelixionRouteClass.DRAFT_WRITE,
            capability=HelixionCapability.SOURCE_DRAFT_WRITE,
            sensitivity=HelixionSensitivityTier.SOURCE,
            object_grant=True,
            path_authority=DENIED_PATH,
        )
    )

    assert decision.allowed is False
    assert "WORKSPACE_OBJECT_MISMATCH" in decision.reasons
    assert "PATH_AUTHORITY_DENIED:DOTENV_WRITE_FORBIDDEN" in decision.reasons


def test_sensitive_source_requires_approval_even_for_lead():
    denied = authorize_helixion_access(
        HelixionAuthorizationRequest(
            subject_id="usr_lead",
            subject_rank=HelixionRankCeiling.LEAD_ARCHITECT,
            workspace_id="wsp",
            object_workspace_id="wsp",
            route_class=HelixionRouteClass.SOURCE_READ,
            capability=HelixionCapability.SOURCE_READ,
            sensitivity=HelixionSensitivityTier.SENSITIVE_SOURCE,
            object_grant=True,
            path_authority=AUTHORIZED_PATH,
        )
    )
    allowed = authorize_helixion_access(
        HelixionAuthorizationRequest(
            subject_id="usr_lead",
            subject_rank=HelixionRankCeiling.LEAD_ARCHITECT,
            workspace_id="wsp",
            object_workspace_id="wsp",
            route_class=HelixionRouteClass.SOURCE_READ,
            capability=HelixionCapability.SOURCE_READ,
            sensitivity=HelixionSensitivityTier.SENSITIVE_SOURCE,
            object_grant=True,
            approval=True,
            path_authority=AUTHORIZED_PATH,
        )
    )

    assert denied.allowed is False
    assert "SENSITIVE_SOURCE_APPROVAL_REQUIRED" in denied.reasons
    assert denied.requires_approval is True
    assert allowed.allowed is True


def test_secret_boundary_denies_founder_with_approval():
    decision = authorize_helixion_access(
        HelixionAuthorizationRequest(
            subject_id="usr_founder",
            subject_rank=HelixionRankCeiling.FOUNDER_ROOT_STEWARD,
            workspace_id="wsp",
            object_workspace_id="wsp",
            route_class=HelixionRouteClass.SOURCE_READ,
            capability=HelixionCapability.SOURCE_READ,
            sensitivity=HelixionSensitivityTier.SECRET_BOUNDARY,
            object_grant=True,
            approval=True,
            path_authority=AUTHORIZED_PATH,
        )
    )

    assert decision.allowed is False
    assert "SECRET_BOUNDARY_DENIED" in decision.reasons


def test_local_control_requires_localhost_approval_and_path_authority():
    remote = authorize_helixion_access(
        HelixionAuthorizationRequest(
            subject_id="usr_lead",
            subject_rank=HelixionRankCeiling.LEAD_ARCHITECT,
            workspace_id="wsp",
            object_workspace_id="wsp",
            route_class=HelixionRouteClass.LOCAL_CONTROL,
            capability=HelixionCapability.LOCAL_CONTROL_REQUEST,
            sensitivity=HelixionSensitivityTier.LOCAL_CONTROL,
            object_grant=True,
            approval=True,
            path_authority=AUTHORIZED_PATH,
            localhost_context=False,
        )
    )
    local = authorize_helixion_access(
        HelixionAuthorizationRequest(
            subject_id="usr_lead",
            subject_rank=HelixionRankCeiling.LEAD_ARCHITECT,
            workspace_id="wsp",
            object_workspace_id="wsp",
            route_class=HelixionRouteClass.LOCAL_CONTROL,
            capability=HelixionCapability.LOCAL_CONTROL_REQUEST,
            sensitivity=HelixionSensitivityTier.LOCAL_CONTROL,
            object_grant=True,
            approval=True,
            path_authority=AUTHORIZED_PATH,
            localhost_context=True,
        )
    )

    assert remote.allowed is False
    assert "LOCALHOST_CONTEXT_REQUIRED" in remote.reasons
    assert local.allowed is True


def test_ai_action_uses_ai_route_and_delegated_capability_only():
    delegated = authorize_helixion_access(
        HelixionAuthorizationRequest(
            subject_id="agent_codex",
            subject_rank=HelixionRankCeiling.AI_SERVICE_ACCOUNT,
            workspace_id="wsp",
            object_workspace_id="wsp",
            route_class=HelixionRouteClass.AI_ACTION,
            capability=HelixionCapability.DELEGATED_READ,
            sensitivity=HelixionSensitivityTier.SOURCE,
            object_grant=True,
            path_authority=AUTHORIZED_PATH,
        )
    )
    wrong_route = authorize_helixion_access(
        HelixionAuthorizationRequest(
            subject_id="agent_codex",
            subject_rank=HelixionRankCeiling.AI_SERVICE_ACCOUNT,
            workspace_id="wsp",
            object_workspace_id="wsp",
            route_class=HelixionRouteClass.ADMIN_POLICY,
            capability=HelixionCapability.POLICY_ADMIN,
            sensitivity=HelixionSensitivityTier.INTERNAL,
            object_grant=True,
            approval=True,
        )
    )

    assert delegated.allowed is True
    assert wrong_route.allowed is False
    assert "RANK_CEILING_BELOW_CAPABILITY" in wrong_route.reasons


def test_evaluator_projection_is_candidate_and_deny_by_default():
    projection = build_authorization_evaluator_projection()

    assert projection["status"] == "candidate_not_live_route_wired"
    assert projection["deny_by_default"] is True
    assert "source_read" in projection["path_authority_required_route_classes"]
    assert "local_control" in projection["route_capabilities"]
    assert projection["authority"]["accepted_state_authority"] is False
