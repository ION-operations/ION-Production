from kernel.ion_helixion_multi_user_identity import (
    HelixionCapability,
    HelixionRankCeiling,
    build_ai_service_subject,
    build_identity_access_schema_projection,
    capability_requires_object_grant,
    preview_rank_capability_decision,
    rank_capability_ceiling,
    rank_ceiling_allows,
    session_projection_from_cockpit_principal,
)
from kernel.ion_public_cockpit_auth import validate_permission_token


def test_public_token_projects_to_founder_ceiling_without_live_authority():
    auth = validate_permission_token(
        "owner-token",
        {"ION_COCKPIT_PUBLIC_TOKEN": "owner-token"},
    )

    projection = session_projection_from_cockpit_principal(auth.principal or {})

    assert projection["subject"]["rank_ceiling"] == "founder_root_steward"
    assert projection["rank_is_ceiling"] is True
    assert projection["rank_is_permission"] is False
    assert projection["enforcement_active"] is False
    assert projection["authority"]["production_authority"] is False
    assert projection["authority"]["live_execution_authority"] is False
    assert projection["authority"]["accepted_state_authority"] is False
    assert projection["authority"]["secrets_authority"] is False


def test_invite_token_projects_to_viewer_not_source_access():
    auth = validate_permission_token(
        "friend-token",
        {"ION_COCKPIT_INVITE_TOKENS": "friend=friend-token"},
    )

    projection = session_projection_from_cockpit_principal(auth.principal or {})
    source = preview_rank_capability_decision(
        projection["subject"]["rank_ceiling"],
        HelixionCapability.SOURCE_READ,
        object_grant=True,
    )
    curated = preview_rank_capability_decision(
        projection["subject"]["rank_ceiling"],
        HelixionCapability.CURATED_DOC_READ,
        object_grant=True,
    )

    assert projection["subject"]["rank_ceiling"] == "viewer_client"
    assert curated["allowed"] is True
    assert source["allowed"] is False
    assert source["reasons"] == ["RANK_CEILING_BELOW_CAPABILITY"]


def test_rank_is_ceiling_and_builder_still_needs_object_grant():
    assert rank_ceiling_allows(HelixionRankCeiling.BUILDER_CONTRIBUTOR, HelixionCapability.SOURCE_READ) is True
    assert capability_requires_object_grant(HelixionCapability.SOURCE_READ) is True

    missing_grant = preview_rank_capability_decision(
        HelixionRankCeiling.BUILDER_CONTRIBUTOR,
        HelixionCapability.SOURCE_READ,
    )
    with_grant = preview_rank_capability_decision(
        HelixionRankCeiling.BUILDER_CONTRIBUTOR,
        HelixionCapability.SOURCE_READ,
        object_grant=True,
    )

    assert missing_grant["allowed"] is False
    assert missing_grant["reasons"] == ["OBJECT_GRANT_REQUIRED"]
    assert with_grant["allowed"] is True


def test_sensitive_and_local_control_require_approval_beyond_rank_and_object():
    sensitive = preview_rank_capability_decision(
        HelixionRankCeiling.LEAD_ARCHITECT,
        HelixionCapability.SENSITIVE_SOURCE_REQUEST,
        object_grant=True,
    )
    approved = preview_rank_capability_decision(
        HelixionRankCeiling.LEAD_ARCHITECT,
        HelixionCapability.SENSITIVE_SOURCE_REQUEST,
        object_grant=True,
        approval=True,
    )
    local_control = preview_rank_capability_decision(
        HelixionRankCeiling.FOUNDER_ROOT_STEWARD,
        HelixionCapability.LOCAL_CONTROL_REQUEST,
        object_grant=True,
    )

    assert sensitive["allowed"] is False
    assert "APPROVAL_REQUIRED" in sensitive["reasons"]
    assert approved["allowed"] is True
    assert local_control["allowed"] is False
    assert "APPROVAL_REQUIRED" in local_control["reasons"]


def test_secret_production_and_accepted_state_are_hard_denied_even_for_founder():
    for capability in (
        HelixionCapability.SECRET_VALUE_READ,
        HelixionCapability.PRODUCTION_DEPLOY,
        HelixionCapability.ACCEPTED_STATE_CLAIM,
    ):
        decision = preview_rank_capability_decision(
            HelixionRankCeiling.FOUNDER_ROOT_STEWARD,
            capability,
            object_grant=True,
            approval=True,
        )
        assert decision["allowed"] is False
        assert decision["reasons"] == ["HARD_DENY_AUTHORITY_BOUNDARY"]


def test_ai_service_subject_has_own_ceiling_and_does_not_inherit_human_rank():
    subject = build_ai_service_subject(
        agent_id="codex",
        workspace_id="wsp_local_operator",
        delegated_capabilities=[
            HelixionCapability.DELEGATED_READ,
            HelixionCapability.DELEGATED_DRAFT,
            HelixionCapability.POLICY_ADMIN,
        ],
    )
    policy = preview_rank_capability_decision(
        subject["subject"]["rank_ceiling"],
        HelixionCapability.POLICY_ADMIN,
        object_grant=True,
        approval=True,
    )
    delegated = preview_rank_capability_decision(
        subject["subject"]["rank_ceiling"],
        HelixionCapability.DELEGATED_READ,
        object_grant=True,
    )

    assert subject["subject"]["subject_type"] == "ai_service_account"
    assert subject["subject"]["rank_ceiling"] == "ai_service_account"
    assert subject["inherits_human_rank"] is False
    assert subject["connection"]["scopes"] == ["delegated_draft", "delegated_read"]
    assert subject["unsupported_delegated_capabilities"] == ["policy_admin"]
    assert policy["allowed"] is False
    assert delegated["allowed"] is True


def test_schema_projection_lists_tables_route_classes_and_rank_boundaries():
    schema = build_identity_access_schema_projection()
    tables = schema["schema_tables"]["required_tables"]
    routes = schema["schema_tables"]["route_classes"]
    founder = rank_capability_ceiling(HelixionRankCeiling.FOUNDER_ROOT_STEWARD)

    assert "users" in tables
    assert "workspace_members" in tables
    assert "delegations" in tables
    assert "audit_events" in tables
    assert "project_read" in routes
    assert "admin_policy" in routes
    assert "secret_value_read" in schema["hard_denied_capabilities"]
    assert "secret_value_read" not in founder["capability_ceiling"]
    assert schema["authority"]["secrets_authority"] is False
