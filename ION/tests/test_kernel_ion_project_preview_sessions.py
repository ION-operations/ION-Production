import json
from pathlib import Path

from kernel.ion_project_preview_sessions import build_preview_sessions_from_cockpit


def test_preview_sessions_empty_projection_is_read_only(tmp_path: Path):
    model = build_preview_sessions_from_cockpit(
        tmp_path,
        projects=[],
        portfolio={},
        launcher_status={"ok": True, "running_count": 0, "launch_count": 0, "launches": []},
    )

    assert model["schema_id"] == "ion.project_preview_sessions.v0_1"
    assert model["ok"] is True
    assert model["summary"]["session_count"] == 0
    assert {provider["provider_id"] for provider in model["providers"]} >= {
        "local_loopback_launcher",
        "application_dev_launcher",
        "cockpit_internal_surface",
        "vm_runner",
        "viewer_local_runner",
    }
    assert model["authority"]["preview_read"] is True
    assert model["authority"]["preview_mutation"] is False
    assert model["authority"]["production_authority"] is False
    assert model["authority"]["live_execution_authority"] is False


def test_preview_sessions_maps_launcher_record_without_leaking_tokens(tmp_path: Path):
    receipt_dir = tmp_path / "ION/05_context/current/project_launcher/receipts"
    receipt_dir.mkdir(parents=True)
    (receipt_dir / "20260605_demo-launch_start.json").write_text('{"ok": true}\n', encoding="utf-8")
    launcher_status = {
        "ok": True,
        "running_count": 1,
        "launch_count": 1,
        "launches": [
            {
                "launch_id": "demo-launch",
                "project_id": "demo",
                "version_id": "v1",
                "label": "Demo App",
                "path": "/tmp/private/demo",
                "framework": "vite",
                "url": "http://127.0.0.1:6320/",
                "open_href": "/cockpit/projects/launch/open/demo-launch?stop_token=secret-stop-token",
                "instrumented_open_href": "/cockpit/projects/launch/proxy/demo-launch/",
                "status_path": "/cockpit/projects/launch/status",
                "diagnostics_path": "/cockpit/projects/launch/diagnostics",
                "running": True,
                "detached": False,
                "process_attached": True,
                "actual_process_control": True,
                "stop_available": True,
                "ownership_confidence": "attached_process_object",
                "process_control_level": "attached_popen",
                "runtime_truth": {
                    "finding": "process_control_attached",
                    "process_identity_verified": True,
                    "stop_would_signal_process": True,
                },
                "state": "running",
                "created_at": "2026-06-05T19:00:00+00:00",
            }
        ],
    }

    model = build_preview_sessions_from_cockpit(tmp_path, projects=[], portfolio={}, launcher_status=launcher_status)
    payload = json.dumps(model, sort_keys=True)
    session = model["sessions"][0]

    assert session["preview_id"] == "launch:demo-launch"
    assert session["provider_id"] == "local_loopback_launcher"
    assert session["lifecycle_state"] == "running"
    assert session["same_origin_embed_url"] == "/cockpit/projects/launch/proxy/demo-launch/"
    assert session["runtime_state_class"] == "running"
    assert session["state_basis"] == "attached_process_object"
    assert session["association_state"] == "managed_attached_process"
    assert session["actual_process_control"] is True
    assert session["stop_available"] is True
    assert session["local_url_ref"] == "loopback_url_present"
    assert session["source_root_ref"].startswith("local_path_sha256:")
    assert session["receipt_refs"] == ["ION/05_context/current/project_launcher/receipts/20260605_demo-launch_start.json"]
    assert "secret-stop-token" not in payload
    assert "stop_token=" not in payload
    assert "http://127.0.0.1:6320" not in payload
    assert "/tmp/private/demo" not in payload
    assert session["authority"]["process_start_authority"] is False
    assert session["authority"]["process_stop_authority"] is False


def test_preview_sessions_classifies_detached_manifest_without_managed_preview_url(tmp_path: Path):
    launcher_status = {
        "ok": True,
        "running_count": 0,
        "detached_count": 1,
        "launch_count": 1,
        "launches": [
            {
                "launch_id": "detached-launch",
                "project_id": "demo",
                "version_id": "v1",
                "label": "Detached App",
                "path": "/tmp/private/detached",
                "framework": "vite",
                "url": "http://127.0.0.1:6321/",
                "instrumented_open_href": "/cockpit/projects/launch/proxy/detached-launch/",
                "status_path": "/cockpit/projects/launch/status",
                "diagnostics_path": "/cockpit/projects/launch/diagnostics",
                "running": False,
                "detached": True,
                "process_attached": False,
                "actual_process_control": False,
                "stop_available": False,
                "ownership_confidence": "stale_manifest_no_listener",
                "process_control_level": "none",
                "loopback_reachable": False,
                "last_known_state": "running",
                "recovered_at": "2026-06-05T20:00:00+00:00",
                "runtime_truth": {
                    "finding": "durable_manifest_recovered_without_process_or_listener",
                    "process_identity_available": True,
                    "process_identity_verified": False,
                    "stop_would_signal_process": False,
                    "unsafe_to_kill_by_pid_only": True,
                },
                "state": "detached",
            }
        ],
    }

    model = build_preview_sessions_from_cockpit(tmp_path, projects=[], portfolio={}, launcher_status=launcher_status)
    payload = json.dumps(model, sort_keys=True)
    session = model["sessions"][0]

    assert session["preview_id"] == "launch:detached-launch"
    assert session["runtime_state_class"] == "stale"
    assert session["state_basis"] == "durable_state_recovery"
    assert session["association_state"] == "recovered_detached_record"
    assert session["same_origin_embed_url"] == ""
    assert session["public_url"] == ""
    assert session["capabilities"]["preview_interaction"] is False
    assert session["authority"]["preview_interaction"] is False
    assert session["detached"] is True
    assert session["actual_process_control"] is False
    assert session["stop_available"] is False
    assert session["stale"] is True
    assert session["stale_reasons"] == ["detached_durable_manifest", "loopback_listener_absent", "no_attached_process_control"]
    assert session["launcher_finding"] == "durable_manifest_recovered_without_process_or_listener"
    assert model["summary"]["detached_count"] == 1
    assert model["summary"]["stale_count"] == 1
    assert model["summary"]["runtime_state_counts"]["stale"] == 1
    assert "http://127.0.0.1:6321" not in payload


def test_preview_sessions_classifies_orphaned_listener_as_visible_not_controlled(tmp_path: Path):
    launcher_status = {
        "ok": True,
        "running_count": 0,
        "detached_count": 1,
        "launch_count": 1,
        "launches": [
            {
                "launch_id": "orphaned-launch",
                "project_id": "demo",
                "version_id": "v1",
                "label": "Orphaned Listener",
                "path": "/tmp/private/orphaned",
                "framework": "static",
                "url": "http://127.0.0.1:6322/",
                "running": False,
                "detached": True,
                "actual_process_control": False,
                "stop_available": False,
                "ownership_confidence": "orphaned_local_preview_unverified",
                "process_control_level": "none",
                "loopback_reachable": True,
                "last_known_state": "running",
                "runtime_truth": {
                    "finding": "loopback_listener_present_but_process_ownership_unverified",
                    "stop_would_signal_process": False,
                },
                "state": "detached",
            }
        ],
    }

    model = build_preview_sessions_from_cockpit(tmp_path, projects=[], portfolio={}, launcher_status=launcher_status)
    session = model["sessions"][0]

    assert session["provider_id"] == "local_static_file_server"
    assert session["runtime_state_class"] == "orphaned"
    assert session["association_state"] == "orphaned_listener_unverified"
    assert session["same_origin_embed_url"] == ""
    assert session["local_url_ref"] == "loopback_listener_unverified"
    assert session["capabilities"]["preview_interaction"] is False
    assert session["loopback_reachable"] is True
    assert session["actual_process_control"] is False
    assert session["launcher_finding"] == "loopback_listener_present_but_process_ownership_unverified"
    assert model["summary"]["orphaned_count"] == 1
    assert model["summary"]["runtime_state_counts"]["orphaned"] == 1


def test_preview_sessions_maps_project_and_portfolio_rows(tmp_path: Path):
    projects = [
        {
            "project_id": "application_dev",
            "label": "Application Dev Apps",
            "status": "workspace_ready",
            "path": "/home/sev/Application_Dev",
            "route_href": "/projects/application-dev",
            "launcher_url": "http://127.0.0.1:5199/",
            "app_catalog_url": "/projects/application-dev/apps.json",
        },
        {
            "project_id": "cosmos",
            "label": "Cosmos",
            "status": "registered",
            "path": "/home/sev/Cosmos",
            "route_href": "/projects/cosmos",
            "preview_href": "/projects/cosmos/preview/",
        },
    ]
    portfolio = {
        "families": [
            {
                "family_id": "family-demo",
                "versions": [
                    {
                        "version_id": "v001",
                        "project_id": "family-demo-v001",
                        "display_label": "Family Demo",
                        "path": "/tmp/private/family-demo",
                        "launchable": True,
                        "launch": {
                            "launchable": True,
                            "project_id": "family-demo",
                            "version_id": "v001",
                            "project_path": "/tmp/private/family-demo",
                            "action_path": "/cockpit/projects/launch/start",
                            "status": "ready",
                        },
                    }
                ],
            }
        ]
    }

    model = build_preview_sessions_from_cockpit(
        tmp_path,
        projects=projects,
        portfolio=portfolio,
        launcher_status={"ok": True, "running_count": 0, "launch_count": 0, "launches": []},
    )
    by_id = {session["preview_id"]: session for session in model["sessions"]}

    assert by_id["project:application-dev:application_dev_launcher"]["provider_id"] == "application_dev_launcher"
    assert by_id["project:cosmos:cockpit_internal_surface"]["same_origin_embed_url"] == "/projects/cosmos/preview/"
    assert by_id["portfolio:family-demo:v001"]["provider_id"] == "local_loopback_launcher"
    assert model["summary"]["source_counts"]["project_row"] == 2
    assert model["summary"]["source_counts"]["portfolio_version"] == 1
    assert model["summary"]["public_preview_count"] == 2
