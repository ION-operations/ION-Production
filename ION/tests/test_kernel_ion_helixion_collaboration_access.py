from kernel.ion_helixion_collaboration_access import (
    build_helixion_collaboration_access_model,
    build_helixion_route_registry_projection,
    build_session_access_projection,
    evaluate_registered_route_access,
    find_registered_route,
)
from kernel.ion_cockpit_view_model import build_cockpit_surface_view_model
from kernel.ion_public_cockpit_auth import validate_permission_token


def test_route_registry_is_candidate_deny_by_default():
    registry = build_helixion_route_registry_projection()

    assert registry["status"] == "candidate_not_live_route_wired"
    assert registry["deny_by_default"] is True
    assert registry["live_route_enforcement"] is False
    assert registry["route_count"] >= 20
    assert registry["shareable_route_count"] > 0
    assert registry["local_control_route_count"] > 0
    assert registry["authority"]["production_authority"] is False


def test_registered_route_lookup_matches_path_and_method():
    route, finding = find_registered_route("/cockpit/chat/archive.json?session_id=abc", method="GET")
    project_route, project_finding = find_registered_route("/projects/application-dev?view=apps", method="GET")
    project_preview_route, project_preview_finding = find_registered_route("/projects/cosmos/preview/", method="GET")
    proxy_route, proxy_finding = find_registered_route("/cockpit/projects/launch/proxy/demo-launch/", method="GET")
    wrong_method, wrong_finding = find_registered_route("/cockpit/chat/archive.json", method="POST")
    missing, missing_finding = find_registered_route("/cockpit/raw/filesystem/list", method="GET")

    assert finding is None
    assert route is not None
    assert route.route_id == "get_cockpit_chat_archive.json"
    assert project_finding is None
    assert project_route is not None
    assert project_route.path_template == "/projects/{project_id}"
    assert project_route.capability == "public_preview_read"
    assert project_route.object_grant_required is False
    assert project_preview_finding is None
    assert project_preview_route is not None
    assert project_preview_route.path_template == "/projects/{project_id}/preview"
    assert project_preview_route.capability == "public_preview_read"
    assert project_preview_route.object_grant_required is False
    assert proxy_finding is None
    assert proxy_route is not None
    assert proxy_route.path_template == "/cockpit/projects/launch/proxy/{launch_id}"
    assert proxy_route.object_grant_required is True
    assert proxy_route.receipt_required is True
    assert wrong_method is None
    assert wrong_finding == "METHOD_NOT_REGISTERED_FOR_ROUTE"
    assert missing is None
    assert missing_finding == "ROUTE_NOT_REGISTERED"


def test_session_projection_reuses_conservative_principal_mapping():
    auth = validate_permission_token(
        "friend-token",
        {"ION_COCKPIT_INVITE_TOKENS": "friend=friend-token"},
    )

    access = build_session_access_projection(auth.principal or {})

    assert access["subject"]["rank_ceiling"] == "viewer_client"
    assert access["rank_is_ceiling"] is True
    assert access["rank_is_permission"] is False
    assert access["enforcement_active"] is False
    assert access["authority"]["secrets_authority"] is False


def test_session_access_route_can_load_but_chat_archive_needs_object_grant():
    auth = validate_permission_token(
        "friend-token",
        {"ION_COCKPIT_INVITE_TOKENS": "friend=friend-token"},
    )
    principal = auth.principal or {}

    session_route = evaluate_registered_route_access("/cockpit/session/access.json", principal=principal)
    archive_denied = evaluate_registered_route_access("/cockpit/chat/archive.json", principal=principal)
    archive_granted = evaluate_registered_route_access("/cockpit/chat/archive.json", principal=principal, object_grant=True)

    assert session_route["allowed_if_enforced"] is True
    assert session_route["candidate_enforcement_active"] is False
    assert archive_denied["allowed_if_enforced"] is False
    assert "OBJECT_GRANT_REQUIRED" in archive_denied["reasons"]
    assert archive_granted["allowed_if_enforced"] is False
    assert "RANK_CEILING_BELOW_CAPABILITY" in archive_granted["reasons"]


def test_owner_still_needs_object_grant_for_shared_project_routes():
    auth = validate_permission_token(
        "owner-token",
        {"ION_COCKPIT_PUBLIC_TOKEN": "owner-token"},
    )
    principal = auth.principal or {}

    projects_denied = evaluate_registered_route_access("/cockpit/projects/model.json", principal=principal)
    projects_granted = evaluate_registered_route_access("/cockpit/projects/model.json", principal=principal, object_grant=True)

    assert projects_denied["allowed_if_enforced"] is False
    assert "OBJECT_GRANT_REQUIRED" in projects_denied["reasons"]
    assert projects_granted["allowed_if_enforced"] is True


def test_source_and_local_control_routes_show_missing_path_and_local_gates():
    auth = validate_permission_token(
        "owner-token",
        {"ION_COCKPIT_PUBLIC_TOKEN": "owner-token"},
    )
    principal = auth.principal or {}

    ide = evaluate_registered_route_access("/cockpit/ide/model.json", principal=principal, object_grant=True)
    launch = evaluate_registered_route_access(
        "/cockpit/projects/launch/start",
        method="POST",
        principal=principal,
        object_grant=True,
        approval=True,
        path_authority={"authorized": True, "reason_code": "AUTHORIZED"},
        localhost_context=False,
    )

    assert ide["allowed_if_enforced"] is False
    assert "PATH_AUTHORITY_REQUIRED" in ide["reasons"]
    assert launch["allowed_if_enforced"] is False
    assert "LOCALHOST_CONTEXT_REQUIRED" in launch["reasons"]


def test_unknown_route_is_explicit_deny_with_session_projection():
    decision = evaluate_registered_route_access("/cockpit/raw/filesystem/list")

    assert decision["allowed_if_enforced"] is False
    assert decision["finding"] == "ROUTE_NOT_REGISTERED"
    assert decision["route"] is None
    assert decision["session_access"]["subject"]["rank_ceiling"] == "guest"


def test_collaboration_access_model_has_operator_visible_contract(tmp_path):
    auth = validate_permission_token(
        "owner-token",
        {"ION_COCKPIT_PUBLIC_TOKEN": "owner-token"},
    )
    model = build_helixion_collaboration_access_model(tmp_path, principal=auth.principal or {})

    assert model["schema_id"] == "ion.helixion_collaboration_access.v0_1"
    assert model["candidate_packet"] == "PCKT-COLLAB-001"
    assert model["live_route_enforcement"] is False
    assert model["root"] == "local_ion_root_redacted"
    assert str(tmp_path) not in str(model)
    assert model["session_access"]["subject"]["rank_ceiling"] == "founder_root_steward"
    assert any(check["path"] == "/cockpit/chat/archive.json" for check in model["route_checks"])
    assert "unknown_routes_deny" in model["denial_defaults"]


def test_collab_cockpit_surface_model_is_fast_candidate_projection(tmp_path):
    auth = validate_permission_token(
        "owner-token",
        {"ION_COCKPIT_PUBLIC_TOKEN": "owner-token"},
    )
    model = build_cockpit_surface_view_model(tmp_path, surface="collab", principal=auth.principal or {})

    assert model["schema_id"] == "ion.cockpit_surface_view_model.v1"
    assert model["surface"] == "collab"
    assert model["runtime"]["shell_root"] == "local_ion_root_redacted"
    assert model["collab_cockpit"]["candidate_packet"] == "PCKT-COLLAB-001"
    assert model["collab_cockpit"]["live_route_enforcement"] is False
    assert model["collab_cockpit"]["session_access"]["subject"]["rank_ceiling"] == "founder_root_steward"
