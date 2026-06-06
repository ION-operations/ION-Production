import json
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import urllib.error
import urllib.request


def _seed_root(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    authority = root / "ION/REPO_AUTHORITY.md"
    authority.parent.mkdir(parents=True)
    authority.write_text("# authority\n", encoding="utf-8")


def _read_json(request: urllib.request.Request) -> dict:
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def _assert_no_live_authority(authority: dict) -> None:
    assert authority["preview_read"] is True
    for key in [
        "app_cast_authority",
        "app_cast_host_authority",
        "app_cast_interaction_authority",
        "app_cast_view_authority",
        "browser_automation_authority",
        "capture_authority",
        "live_execution_authority",
        "loopback_mutation",
        "loopback_probe",
        "preview_mutation",
        "production_authority",
        "secrets_authority",
        "stream_authority",
        "viewer_control_authority",
    ]:
        assert authority[key] is False


def _assert_target_share_grant_contract(target: dict) -> None:
    contract = target["share_grant_contract"]
    route_evidence = contract["route_auth_evidence"]

    assert contract["schema_id"] == "ion.project_preview_app_cast_share_grant_contract.v0_1"
    assert contract["status"] == "candidate_contract_only_no_grant"
    assert contract["share_grant_state"] == "not_granted"
    assert contract["pairing_state"] == "not_paired"
    assert contract["candidate_enforcement_active"] is False
    assert contract["live_route_enforcement"] is False
    assert contract["viewer_required_capability"] == "public_preview_read"
    assert contract["viewer_interaction"] == "view_only"
    assert contract["viewer_session_required"] is True
    assert contract["object_share_grant_ref"] == ""
    assert contract["share_grant_ref"] == ""
    assert contract["host_viewer_pair_ref"] == ""
    assert contract["expiry_policy"]["expires_at_required_for_active_grant"] is True
    assert contract["revocation_policy"]["revocable"] is True
    assert contract["audit_policy"]["audit_receipt_required"] is True
    assert "No share grant is active." in contract["non_claims"]
    _assert_no_live_authority(contract["authority"])

    assert route_evidence["schema_id"] == "ion.project_preview_app_cast_route_auth_evidence.v0_1"
    assert route_evidence["route"] == target["route"]
    assert route_evidence["method"] == "GET"
    assert route_evidence["route_class"] == "project_read"
    assert route_evidence["capability"] == "public_preview_read"
    assert route_evidence["mutation"] is False
    assert route_evidence["candidate_enforcement_active"] is False
    assert route_evidence["live_route_enforcement"] is False
    assert route_evidence["target_public_preview_allowed"] == target["public_preview_allowed"]
    assert route_evidence["target_access_basis"] == target["viewer_grant_requirement"]
    assert route_evidence["target_object_grant_required"] == (
        target["viewer_grant_requirement"] != "public_preview_read"
    )
    _assert_no_live_authority(route_evidence["authority"])


def test_public_preview_routes_serve_real_model_with_app_cast_contract(monkeypatch, tmp_path: Path):
    _seed_root(tmp_path)
    monkeypatch.setenv("ION_COCKPIT_PUBLIC_TOKEN", "test-token")

    from kernel.ion_chatgpt_browser_mcp_http_preview import IonChatGPTPreviewHandler

    preview_server = ThreadingHTTPServer(("127.0.0.1", 0), IonChatGPTPreviewHandler)
    preview_server.ion_root = tmp_path
    preview_thread = Thread(target=preview_server.serve_forever, daemon=True)
    preview_thread.start()
    try:
        base = f"http://127.0.0.1:{preview_server.server_address[1]}"
        paths = ["/cockpit/previews/model.json", "/cockpit/projects/previews/model.json"]

        for path in paths:
            unauthenticated = urllib.request.Request(
                f"{base}{path}",
                headers={"Host": "ion.example.test", "Accept": "application/json"},
            )
            try:
                urllib.request.urlopen(unauthenticated, timeout=5)
                raise AssertionError(f"unauthenticated preview model route should not return 200: {path}")
            except urllib.error.HTTPError as exc:
                payload = json.loads(exc.read().decode("utf-8"))
                assert exc.code == 401
                assert payload["finding"] == "public_cockpit_login_required"

            query_token = urllib.request.Request(
                f"{base}{path}?token=test-token",
                headers={"Host": "ion.example.test", "Accept": "application/json"},
            )
            try:
                urllib.request.urlopen(query_token, timeout=5)
                raise AssertionError(f"query-token preview model route should not return 200: {path}")
            except urllib.error.HTTPError as exc:
                payload = json.loads(exc.read().decode("utf-8"))
                assert exc.code == 401
                assert payload["finding"] == "public_cockpit_login_required"

            allowed = urllib.request.Request(
                f"{base}{path}",
                headers={"Host": "ion.example.test", "Accept": "application/json", "Authorization": "Bearer test-token"},
            )
            payload = _read_json(allowed)
            payload_text = json.dumps(payload, sort_keys=True)
            app_cast = payload["app_cast_preview"]
            share_contract = app_cast["share_grant_contract"]

            assert payload["schema_id"] == "ion.project_preview_sessions.v0_1"
            assert payload["ok"] is True
            assert payload["authority"]["preview_mutation"] is False
            assert payload["authority"]["production_authority"] is False
            assert payload["authority"]["live_execution_authority"] is False
            assert app_cast["schema_id"] == "ion.project_preview_app_cast_preview.v0_1"
            assert app_cast["status"] == "candidate_projection_only_no_stream"
            assert app_cast["target_count"] == len(app_cast["targets"])
            assert app_cast["target_count"] == payload["summary"]["app_cast_target_count"]
            assert app_cast["target_count"] > 0
            assert app_cast["blocked_target_count"] == len(app_cast["blocked_targets"])
            assert app_cast["blocked_target_count"] == payload["summary"]["app_cast_blocked_target_count"]
            assert app_cast["share_grant_contract_count"] == len(app_cast["targets"])
            assert app_cast["share_grant_blocked_contract_count"] == len(app_cast["blocked_targets"])
            assert app_cast["object_grant_required_target_count"] >= 0
            assert app_cast["registered_route_target_count"] >= 0
            _assert_no_live_authority(app_cast["authority"])
            assert share_contract["schema_id"] == "ion.project_preview_app_cast_share_grant_contract.v0_1"
            assert share_contract["status"] == "candidate_contract_only_no_grants_active"
            assert share_contract["active_share_grant_count"] == 0
            assert share_contract["target_contract_count"] == len(app_cast["targets"])
            assert share_contract["blocked_contract_count"] == len(app_cast["blocked_targets"])
            assert share_contract["object_grant_required_target_count"] == app_cast["object_grant_required_target_count"]
            assert share_contract["registered_route_target_count"] == app_cast["registered_route_target_count"]
            assert share_contract["host_viewer_pairing_state"] == "not_paired"
            assert share_contract["candidate_enforcement_active"] is False
            assert share_contract["live_route_enforcement"] is False
            assert share_contract["expiry_policy"]["expires_at_required_for_active_grant"] is True
            assert share_contract["revocation_policy"]["revocable"] is True
            assert share_contract["audit_policy"]["audit_receipt_required"] is True
            _assert_no_live_authority(share_contract["authority"])
            for target in app_cast["targets"]:
                assert target["target_kind"] == "app_cast_target"
                assert target["cast_mode"] == "app_only_view"
                assert target["app_only_boundary"] == "single_preview_route_only"
                assert target["auth_mode"] == "read_only_same_origin"
                assert target["stream_state"] == "not_streaming"
                assert target["transport_state"] == "transport_deferred"
                assert target["source_capture_state"] == "not_captured"
                assert target["share_grant_state"] == "not_granted"
                assert target["host_control_state"] == "not_granted"
                assert target["viewer_interaction"] == "view_only"
                assert target["viewer_interaction_state"] == "view_only"
                assert target["viewer_grant_requirement"] == "public_preview_read"
                assert target["route"].startswith("/")
                _assert_no_live_authority(target["authority"])
                _assert_target_share_grant_contract(target)
            for blocked in app_cast["blocked_targets"]:
                assert blocked["share_grant_state"] == "not_granted"
                assert blocked["stream_state"] == "not_streaming"
                assert blocked["route"] == ""
                assert blocked["blocked_reason"]
            assert "No app stream was started." in app_cast["non_claims"]
            assert "test-token" not in payload_text
            assert str(tmp_path) not in payload_text
    finally:
        preview_server.shutdown()
        preview_server.server_close()
        preview_thread.join(timeout=5)
