import json

from kernel.ion_helixion_project_access_inventory import (
    build_helixion_project_family_detail_model,
    build_helixion_projects_surface_model,
    build_project_access_inventory,
    project_access_inventory_summary,
    redact_project_access_inventory_for_rank,
)
from kernel.ion_helixion_multi_user_identity import HelixionRankCeiling


def _manifest():
    return {
        "schema_id": "ion.project_portfolio.v1",
        "generated_at": "2026-06-02T00:00:00Z",
        "summary": {
            "project_root_count": 2,
            "family_count": 1,
            "canonical_domain_count": 1,
            "launchable_count": 1,
            "documentation_surface_count": 2,
            "project_os_ready_count": 1,
            "project_os_watch_count": 0,
            "project_os_blocked_count": 0,
            "materialized_present": True,
        },
        "canonical_domains": [
            {
                "domain_id": "water-simulation",
                "label": "Water Simulation",
                "summary": "Ocean and wave work.",
                "sort_order": 1,
                "project_count": 1,
                "version_count": 2,
                "family_count": 1,
                "launchable_count": 1,
                "doc_count": 2,
                "diff_count": 1,
                "operating_system": {
                    "schema_id": "ion.project_domain_operating_system.v1",
                    "posture": "ready",
                    "average_readiness_score": 80,
                    "ready_count": 1,
                    "watch_count": 0,
                    "blocked_count": 0,
                    "maintenance_rhythm": [{"label": "Release Review", "cadence": "per milestone", "focus": "proof"}],
                    "top_risks": [
                        {
                            "risk_id": "no_visual_proof",
                            "title": "Visual proof missing",
                            "severity": "medium",
                            "mitigation": "attach screenshot",
                            "family_id": "cosmos:hyper-h2o",
                            "family_label": "Hyper H2O",
                        }
                    ],
                },
            }
        ],
        "families": [
            {
                "family_id": "cosmos:hyper-h2o",
                "domain_id": "water-simulation",
                "label": "Hyper H2O",
                "current_path": "/home/sev/ION - Production/ION_Developement/Cosmos/hyper-h2o-v002",
                "project_count": 2,
                "version_count": 2,
                "branch_count": 1,
                "diff_count": 1,
                "doc_count": 2,
                "launchable_count": 1,
                "source_ids": ["cosmos"],
                "lineage_status": "version_chain_ready",
                "operating_system": {
                    "schema_id": "ion.project_operating_system.v1",
                    "posture": "ready",
                    "readiness_score": 82,
                    "lifecycle": [
                        {
                            "stage_id": "01_inventory",
                            "label": "Inventory",
                            "objective": "Identify source roots.",
                            "status": "ready",
                        }
                    ],
                    "maintenance_lanes": [
                        {
                            "lane_id": "source_canon",
                            "label": "Source Canon",
                            "objective": "Keep one current source path.",
                            "status": "ready",
                            "next_action": "/home/sev/ION - Production/ION_Developement/Cosmos/hyper-h2o-v002",
                        }
                    ],
                    "quality_gates": [
                        {
                            "gate_id": "source_current",
                            "label": "Current Source",
                            "status": "pass",
                            "evidence": "/home/sev/ION - Production/ION_Developement/Cosmos/hyper-h2o-v002",
                        }
                    ],
                    "human_workflows": [
                        {
                            "workflow_id": "launch_review",
                            "label": "Launch Review",
                            "trigger": "launchable source selected",
                            "cadence": "per version",
                            "output": "managed launch proof",
                        }
                    ],
                    "operating_principles": ["docs attach to project/version"],
                    "next_actions": [
                        {
                            "action_id": "attach_visual_proof",
                            "label": "Attach visual proof",
                            "lane": "quality_proof",
                            "priority": "medium",
                            "detail": "capture current renderer",
                        }
                    ],
                    "risk_register": [
                        {
                            "risk_id": "no_visual_proof",
                            "title": "Visual proof missing",
                            "severity": "medium",
                            "mitigation": "attach screenshot",
                        }
                    ],
                    "summary": {"version_count": 2, "doc_count": 2, "launchable_count": 1, "risk_count": 1},
                },
                "diffs": [
                    {
                        "diff_id": "001_v001_to_v002",
                        "manifest_path": "/home/sev/ION_PROJECTS_PROFESSIONAL_ORGANIZED_CANDIDATE/domains/water/hyper/DIFF_MANIFEST.json",
                        "from_project_id": "cosmos:hyper-h2o-v001",
                        "to_project_id": "cosmos:hyper-h2o-v002",
                        "status": "candidate_diff_manifest",
                        "file_diff": {"added_count": 3, "changed_count": 2, "removed_count": 1},
                    }
                ],
                "versions": [
                    {
                        "version_id": "001-v001",
                        "project_id": "cosmos:hyper-h2o-v001",
                        "display_label": "Hyper H2O v001",
                        "sequence_label": "v001",
                        "path": "/home/sev/ION - Production/ION_Developement/Cosmos/hyper-h2o-v001",
                        "stack": "vite",
                        "launchable": False,
                        "is_current": False,
                        "docs": {"docs": []},
                    },
                    {
                        "version_id": "002-v002",
                        "project_id": "cosmos:hyper-h2o-v002",
                        "display_label": "Hyper H2O v002",
                        "sequence_label": "v002",
                        "path": "/home/sev/ION - Production/ION_Developement/Cosmos/hyper-h2o-v002",
                        "stack": "vite",
                        "launchable": True,
                        "is_current": True,
                        "launch": {
                            "framework": "vite",
                            "mode": "managed_local_dev_server",
                            "requires_local_machine": True,
                            "managed_window_stops_server": True,
                        },
                        "docs": {
                            "docs": [
                                {
                                    "title": "Hyper H2O README",
                                    "rel_path": "README.md",
                                    "path": "/home/sev/ION - Production/ION_Developement/Cosmos/hyper-h2o-v002/README.md",
                                    "kind": "readme",
                                    "extension": ".md",
                                    "primary": True,
                                    "reference": False,
                                    "bytes": 123,
                                },
                                {
                                    "title": "Ocean Notes",
                                    "rel_path": "docs/ocean.md",
                                    "path": "/home/sev/ION - Production/ION_Developement/Cosmos/hyper-h2o-v002/docs/ocean.md",
                                    "kind": "doc",
                                    "extension": ".md",
                                    "primary": False,
                                    "reference": False,
                                    "bytes": 456,
                                },
                            ]
                        },
                    },
                ],
            }
        ],
    }


def test_project_portfolio_builds_access_objects_with_virtual_paths():
    inventory = build_project_access_inventory(_manifest(), workspace_id="wsp_test")
    summary = inventory["summary"]
    objects = inventory["objects"]

    assert inventory["schema_id"] == "ion.helixion_project_access_inventory.v0_1"
    assert summary["domain_count"] == 1
    assert summary["project_family_count"] == 1
    assert summary["version_count"] == 2
    assert summary["file_root_count"] == 2
    assert summary["doc_count"] == 2
    assert summary["diff_count"] == 1
    assert summary["launch_count"] == 1
    assert all(item["virtual_path"].startswith("ion://workspace/wsp-test/") for item in objects)
    assert inventory["authority"]["production_authority"] is False
    assert project_access_inventory_summary(inventory)["summary"]["object_count"] == summary["object_count"]


def test_viewer_sees_internal_project_context_but_not_source_or_launch_paths():
    inventory = build_project_access_inventory(_manifest(), workspace_id="wsp_test")
    redacted = redact_project_access_inventory_for_rank(inventory, HelixionRankCeiling.VIEWER_CLIENT)
    object_types = {item["object_type"] for item in redacted["objects"]}

    assert "domain" in object_types
    assert "project_family" in object_types
    assert "project_version" in object_types
    assert "doc" in object_types
    assert "file_root" not in object_types
    assert "launch" not in object_types
    assert redacted["path_inspection_allowed"] is False
    assert all(item.get("canonical_ref") is None for item in redacted["objects"] if item.get("canonical_ref_sha256"))
    assert redacted["hidden_object_count"] == 3


def test_builder_can_see_source_objects_without_absolute_paths():
    inventory = build_project_access_inventory(_manifest(), workspace_id="wsp_test")
    redacted = redact_project_access_inventory_for_rank(inventory, HelixionRankCeiling.BUILDER_CONTRIBUTOR)
    file_roots = [item for item in redacted["objects"] if item["object_type"] == "file_root"]
    launches = [item for item in redacted["objects"] if item["object_type"] == "launch"]

    assert len(file_roots) == 2
    assert len(launches) == 1
    assert redacted["path_inspection_allowed"] is False
    assert all(item["canonical_ref"] is None for item in file_roots)
    assert all(item["canonical_ref_sha256"].startswith("sha256:") for item in file_roots)


def test_lead_can_inspect_canonical_refs_while_guest_cannot_see_internal_inventory():
    inventory = build_project_access_inventory(_manifest(), workspace_id="wsp_test")
    lead = redact_project_access_inventory_for_rank(inventory, HelixionRankCeiling.LEAD_ARCHITECT)
    guest = redact_project_access_inventory_for_rank(inventory, HelixionRankCeiling.GUEST)

    assert lead["path_inspection_allowed"] is True
    assert any(item["canonical_ref"] for item in lead["objects"] if item["object_type"] == "file_root")
    assert guest["object_count"] == 0
    assert guest["hidden_object_count"] == inventory["summary"]["object_count"]


def test_helixion_projects_surface_model_is_canonical_and_path_redacted():
    surface = build_helixion_projects_surface_model(_manifest(), workspace_id="wsp_test")
    family = surface["featured_families"][0]
    ops = family["operating_system"]

    assert surface["schema_id"] == "ion.helixion_projects_surface.v0_1"
    assert surface["portfolio_summary"]["project_root_count"] == 2
    assert surface["access_summary"]["path_inspection_allowed"] is False
    assert surface["access_summary"]["visible_by_type"]["project_family"] == 1
    assert surface["canonical_domains"][0]["operating_system"]["posture"] == "ready"
    assert family["family_id"] == "cosmos:hyper-h2o"
    assert family["detail_href"] == "/projects/family/cosmos%3Ahyper-h2o"
    assert family["current"]["virtual_path"].startswith("ion://workspace/wsp-test/domains/water-simulation/projects/cosmos-hyper-h2o/")
    assert ops["maintenance_lanes"][0]["next_action"] == "redacted_local_ref"
    assert ops["quality_gates"][0]["evidence"] == "redacted_local_ref"
    assert surface["project_canon_contract"]["authority"]["production_authority"] is False
    assert {axis["axis_id"] for axis in surface["timeline_axes"]} >= {"version_lineage", "context_capsule", "future_plan"}


def test_helixion_project_family_detail_model_includes_versions_diffs_preview_and_redacts_paths():
    detail = build_helixion_project_family_detail_model(
        _manifest(),
        "cosmos:hyper-h2o",
        workspace_id="wsp_test",
        workbench_project_id="cosmos",
        workbench_summary={
            "schema_id": "ion.project_workbench_timeline.v1",
            "ok": True,
            "project_id": "cosmos",
            "project": {
                "project_id": "cosmos",
                "label": "Cosmos Water World",
                "preview_public_path": "/projects/cosmos",
            },
            "preview": {"status": "not_probed"},
            "history_counts": {
                "patch_receipt_count": 2,
                "browser_capture_count": 1,
                "rollback_candidate_count": 1,
            },
            "next_recommended_safe_action": {
                "action_id": "capture_orbit",
                "label": "Capture orbit",
                "reason": "Refresh visual proof.",
            },
            "public_preview_allowed": True,
            "mutations_require_cockpit_auth": True,
            "write_confirmation_required": True,
        },
    )

    assert detail["schema_id"] == "ion.helixion_project_family_detail.v0_1"
    assert detail["family"]["detail_href"] == "/projects/family/cosmos%3Ahyper-h2o"
    assert detail["preview_capability"]["capability"] == "embedded_workbench"
    assert detail["preview_capability"]["embed_src"] == "/projects/cosmos/preview/"
    assert detail["versions"][1]["docs"]["items"][0]["rel_path"] == "README.md"
    assert detail["diffs"][0]["changed_count"] == 2
    assert detail["workbench_summary"]["history_counts"]["browser_capture_count"] == 1
    assert {proof["proof_id"] for proof in detail["proof_ladder"]} >= {"version_lineage", "visual_capture", "rollback_lane"}
    assert detail["proof_summary"]["pass_count"] >= 5
    assert detail["context_capsule_lane"]["authority"]["production_authority"] is False
    payload = json.dumps(detail, sort_keys=True)
    assert "/home/sev" not in payload
    assert "file://" not in payload
