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
    assert model["summary"]["comparison_count"] == 0
    assert model["comparisons"] == []
    assert model["surface_matrix"]["schema_id"] == "ion.project_preview_surface_matrix.v0_1"
    assert "viewer_local" in model["surface_matrix"]["runner_locations"]
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


def test_preview_sessions_registers_read_only_comparison_pair_without_capture_or_loopback(tmp_path: Path):
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
                "runtime_truth": {"finding": "process_control_attached"},
                "state": "running",
            }
        ],
    }
    projects = [
        {
            "project_id": "demo",
            "label": "Demo Public Project",
            "status": "registered",
            "path": "/tmp/private/demo",
            "route_href": "/projects/demo",
            "preview_href": "/projects/demo/preview/",
        }
    ]

    model = build_preview_sessions_from_cockpit(tmp_path, projects=projects, portfolio={}, launcher_status=launcher_status)
    payload = json.dumps(model, sort_keys=True)
    comparison = model["comparisons"][0]

    assert model["summary"]["comparison_count"] == 1
    assert model["summary"]["comparable_session_count"] == 2
    assert comparison["schema_id"] == "ion.project_preview_comparison.v0_1"
    assert comparison["baseline_preview_id"] == "project:demo:cockpit_internal_surface"
    assert comparison["candidate_preview_id"] == "launch:demo-launch"
    assert comparison["pair_basis"] == "project"
    assert comparison["surface_pair"] == "local_host_to_local_host"
    assert comparison["route"] == "/cockpit/projects/launch/proxy/demo-launch/"
    assert comparison["route_source"] == "candidate"
    assert comparison["route_basis"] == "same_origin_embed_url"
    assert comparison["baseline_route"] == "/projects/demo/preview/"
    assert comparison["baseline_route_basis"] == "same_origin_embed_url"
    assert comparison["candidate_route"] == "/cockpit/projects/launch/proxy/demo-launch/"
    assert comparison["candidate_route_basis"] == "same_origin_embed_url"
    assert comparison["verdict"] == "not_compared"
    assert comparison["status"] == "registered_read_only"
    assert comparison["capabilities"]["preview_read"] is True
    assert comparison["capabilities"]["preview_interaction"] is False
    assert comparison["authority"]["preview_mutation"] is False
    assert comparison["authority"]["ai_observe_preview"] is False
    assert comparison["capture_pair_receipt_refs"] == []
    assert comparison["screenshot_refs"] == []
    assert comparison["console_delta"] == "not_captured"
    assert comparison["network_delta"] == "not_captured"
    assert model["surface_matrix"]["comparison_count"] == 1
    assert model["surface_matrix"]["session_counts_by_location"]["local_host"] == 2
    assert "http://127.0.0.1:6320" not in payload
    assert "/tmp/private/demo" not in payload


def test_preview_sessions_comparisons_do_not_pair_unrelated_same_version_ids(tmp_path: Path):
    projects = [
        {
            "project_id": "alpha",
            "label": "Alpha",
            "status": "registered",
            "path": "/tmp/private/alpha",
            "route_href": "/projects/alpha",
            "preview_href": "/projects/alpha/preview/",
        },
        {
            "project_id": "beta",
            "label": "Beta",
            "status": "registered",
            "path": "/tmp/private/beta",
            "route_href": "/projects/beta",
            "preview_href": "/projects/beta/preview/",
        },
    ]
    portfolio = {
        "families": [
            {
                "family_id": "alpha-family",
                "versions": [{"version_id": "v1", "project_id": "alpha", "path": "/tmp/private/alpha", "launchable": True}],
            },
            {
                "family_id": "beta-family",
                "versions": [{"version_id": "v1", "project_id": "beta", "path": "/tmp/private/beta", "launchable": True}],
            },
        ]
    }

    model = build_preview_sessions_from_cockpit(
        tmp_path,
        projects=projects,
        portfolio=portfolio,
        launcher_status={"ok": True, "running_count": 0, "launch_count": 0, "launches": []},
    )

    assert model["summary"]["comparison_count"] == 2
    pairs = {(item["baseline_preview_id"], item["candidate_preview_id"]) for item in model["comparisons"]}
    assert ("project:alpha:cockpit_internal_surface", "portfolio:alpha-family:v1") in pairs
    assert ("project:beta:cockpit_internal_surface", "portfolio:beta-family:v1") in pairs
    assert all("alpha" in left + right or "beta" in left + right for left, right in pairs)
    assert {item["pair_basis"] for item in model["comparisons"]} == {"project"}


def test_preview_sessions_scrubs_protocol_relative_and_tokenized_comparison_routes(tmp_path: Path):
    projects = [
        {
            "project_id": "demo",
            "label": "Demo Public Project",
            "status": "registered",
            "path": "/tmp/private/demo",
            "route_href": "/projects/demo?access_token=secret",
            "preview_href": "//127.0.0.1:5173/preview/?token=secret",
        }
    ]
    portfolio = {
        "families": [
            {
                "family_id": "demo-family",
                "versions": [{"version_id": "v1", "project_id": "demo", "path": "/tmp/private/demo", "launchable": True}],
            }
        ]
    }

    model = build_preview_sessions_from_cockpit(
        tmp_path,
        projects=projects,
        portfolio=portfolio,
        launcher_status={"ok": True, "running_count": 0, "launch_count": 0, "launches": []},
    )
    payload = json.dumps(model, sort_keys=True)
    comparison = model["comparisons"][0]

    assert comparison["route"] == ""
    assert comparison["route_source"] == ""
    assert comparison["route_basis"] == ""
    assert comparison["baseline_route"] == ""
    assert comparison["candidate_route"] == ""
    assert "127.0.0.1:5173" not in payload
    assert "access_token=secret" not in payload
    assert "token=secret" not in payload


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
