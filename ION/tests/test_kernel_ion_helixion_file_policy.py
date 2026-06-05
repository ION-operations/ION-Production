from pathlib import Path

from kernel.ion_helixion_file_policy import (
    HelixionFileOperation,
    HelixionFilePolicyRequest,
    build_file_policy_projection,
    decide_helixion_file_policy,
)
from kernel.ion_helixion_multi_user_identity import HelixionRankCeiling
from kernel.ion_helixion_project_access_inventory import build_project_access_inventory
from kernel.ion_path_authority import WorkspaceAuthority


def _authority(root: Path) -> WorkspaceAuthority:
    repo = root / "ION_Developement"
    return WorkspaceAuthority(
        workspace_root=root,
        active_repo_root=repo,
        ion_content_root=repo / "ION",
        export_root=root / "ION_EXPORTS_LOCAL",
        vault_root=root / "ION_VAULT_LOCAL",
        allowed_sibling_roots=(root / "Needs_Routed",),
        forbidden_roots=(root.parent / "ION_EXPORTS_LOCAL",),
        path_policy={"forbid_parent_segments_for_write": True},
        manifest_path=root / "ION_WORKSPACE_MANIFEST.yaml",
    )


def _inventory(root: Path):
    source = root / "ION_Developement" / "Cosmos" / "hyper-h2o-v002"
    return build_project_access_inventory(
        {
            "schema_id": "ion.project_portfolio.v1",
            "generated_at": "2026-06-02T00:00:00Z",
            "canonical_domains": [
                {
                    "domain_id": "water-simulation",
                    "label": "Water Simulation",
                    "summary": "Ocean and wave work.",
                    "project_count": 1,
                    "version_count": 1,
                    "family_count": 1,
                    "launchable_count": 1,
                    "doc_count": 1,
                    "diff_count": 1,
                }
            ],
            "families": [
                {
                    "family_id": "cosmos:hyper-h2o",
                    "domain_id": "water-simulation",
                    "label": "Hyper H2O",
                    "current_path": source.as_posix(),
                    "project_count": 1,
                    "version_count": 1,
                    "branch_count": 1,
                    "diff_count": 1,
                    "doc_count": 1,
                    "launchable_count": 1,
                    "source_ids": ["cosmos"],
                    "diffs": [
                        {
                            "diff_id": "001_v001_to_v002",
                            "manifest_path": (source / "lineage" / "DIFF_MANIFEST.json").as_posix(),
                            "status": "candidate_diff_manifest",
                        }
                    ],
                    "versions": [
                        {
                            "version_id": "001-v002",
                            "project_id": "cosmos:hyper-h2o-v002",
                            "display_label": "Hyper H2O v002",
                            "sequence_label": "v002",
                            "path": source.as_posix(),
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
                                        "title": "README",
                                        "rel_path": "README.md",
                                        "path": (source / "README.md").as_posix(),
                                        "kind": "readme",
                                        "extension": ".md",
                                        "primary": True,
                                        "reference": False,
                                        "bytes": 123,
                                    }
                                ]
                            },
                        }
                    ],
                }
            ],
        },
        workspace_id="wsp_test",
    )


def _object(inventory, object_type: str):
    return next(item for item in inventory["objects"] if item["object_type"] == object_type)


def test_builder_source_read_allows_only_with_object_grant_and_path_authority(tmp_path):
    inventory = _inventory(tmp_path)
    file_root = _object(inventory, "file_root")

    decision = decide_helixion_file_policy(
        inventory,
        HelixionFilePolicyRequest(
            subject_id="usr_builder",
            rank_ceiling=HelixionRankCeiling.BUILDER_CONTRIBUTOR,
            workspace_id="wsp_test",
            object_ref=file_root["object_id"],
            operation=HelixionFileOperation.SOURCE_READ,
            relative_path="src/App.tsx",
            object_grant=True,
        ),
        path_authority=_authority(tmp_path),
    )

    assert decision["allowed"] is True
    assert decision["path_authority_evaluated"] is True
    assert decision["path_authority"]["authorized"] is True
    assert decision["path_authority"]["resolved_path"] is None
    assert decision["path_authority"]["resolved_path_sha256"].startswith("sha256:")
    assert decision["object"]["canonical_ref"] is None
    assert decision["target_virtual_path"].endswith("/source/files/src/App.tsx")


def test_source_child_path_escape_is_denied_before_path_authority(tmp_path):
    inventory = _inventory(tmp_path)
    file_root = _object(inventory, "file_root")

    decision = decide_helixion_file_policy(
        inventory,
        {
            "subject_id": "usr_builder",
            "rank_ceiling": "builder_contributor",
            "workspace_id": "wsp_test",
            "object_ref": file_root["virtual_path"],
            "operation": "source_read",
            "relative_path": "../secret.txt",
            "object_grant": True,
        },
        path_authority=_authority(tmp_path),
    )

    assert decision["allowed"] is False
    assert decision["path_authority_evaluated"] is False
    assert "PARENT_SEGMENT_FORBIDDEN" in decision["reasons"]
    assert "PATH_AUTHORITY_REQUIRED" in decision["reasons"]


def test_dotenv_under_source_root_is_denied_by_path_authority(tmp_path):
    inventory = _inventory(tmp_path)
    file_root = _object(inventory, "file_root")

    decision = decide_helixion_file_policy(
        inventory,
        HelixionFilePolicyRequest(
            subject_id="usr_founder",
            rank_ceiling=HelixionRankCeiling.FOUNDER_ROOT_STEWARD,
            workspace_id="wsp_test",
            object_ref=file_root["object_id"],
            operation=HelixionFileOperation.SOURCE_READ,
            relative_path=".env.local",
            object_grant=True,
            approval=True,
        ),
        path_authority=_authority(tmp_path),
    )

    assert decision["allowed"] is False
    assert "PATH_AUTHORITY_DENIED:DOTENV_WRITE_FORBIDDEN" in decision["reasons"]
    assert decision["path_authority"]["authorized"] is False
    assert decision["path_authority"]["reason_code"] == "DOTENV_WRITE_FORBIDDEN"


def test_viewer_doc_read_allowed_with_redacted_path(tmp_path):
    inventory = _inventory(tmp_path)
    doc = _object(inventory, "doc")

    decision = decide_helixion_file_policy(
        inventory,
        HelixionFilePolicyRequest(
            subject_id="usr_viewer",
            rank_ceiling=HelixionRankCeiling.VIEWER_CLIENT,
            workspace_id="wsp_test",
            object_ref=doc["object_id"],
            operation=HelixionFileOperation.DOC_READ,
            object_grant=True,
        ),
        path_authority=_authority(tmp_path),
    )

    assert decision["allowed"] is True
    assert decision["object"]["canonical_ref"] is None
    assert decision["path_authority"]["resolved_path"] is None
    assert decision["path_authority"]["path_redacted"] is True


def test_lead_doc_read_can_include_path_evidence(tmp_path):
    inventory = _inventory(tmp_path)
    doc = _object(inventory, "doc")

    decision = decide_helixion_file_policy(
        inventory,
        HelixionFilePolicyRequest(
            subject_id="usr_lead",
            rank_ceiling=HelixionRankCeiling.LEAD_ARCHITECT,
            workspace_id="wsp_test",
            object_ref=doc["object_id"],
            operation=HelixionFileOperation.DOC_READ,
            object_grant=True,
        ),
        path_authority=_authority(tmp_path),
    )

    assert decision["allowed"] is True
    assert decision["object"]["canonical_ref"]
    assert decision["path_authority"]["resolved_path"]
    assert decision["path_authority"]["path_redacted"] is False


def test_launch_requires_approval_localhost_and_path_authority(tmp_path):
    inventory = _inventory(tmp_path)
    launch = _object(inventory, "launch")

    missing_approval = decide_helixion_file_policy(
        inventory,
        HelixionFilePolicyRequest(
            subject_id="usr_lead",
            rank_ceiling=HelixionRankCeiling.LEAD_ARCHITECT,
            workspace_id="wsp_test",
            object_ref=launch["object_id"],
            operation=HelixionFileOperation.LAUNCH,
            object_grant=True,
            localhost_context=True,
        ),
        path_authority=_authority(tmp_path),
    )
    allowed = decide_helixion_file_policy(
        inventory,
        HelixionFilePolicyRequest(
            subject_id="usr_lead",
            rank_ceiling=HelixionRankCeiling.LEAD_ARCHITECT,
            workspace_id="wsp_test",
            object_ref=launch["object_id"],
            operation=HelixionFileOperation.LAUNCH,
            object_grant=True,
            approval=True,
            localhost_context=True,
        ),
        path_authority=_authority(tmp_path),
    )

    assert missing_approval["allowed"] is False
    assert "LOCAL_CONTROL_APPROVAL_REQUIRED" in missing_approval["reasons"]
    assert allowed["allowed"] is True


def test_file_policy_projection_is_candidate_and_lists_operations():
    projection = build_file_policy_projection()

    assert projection["status"] == "candidate_not_live_route_wired"
    assert projection["operations"]["source_read"]["path_required"] is True
    assert projection["operations"]["launch"]["route_class"] == "local_control"
    assert projection["child_paths_forbid_parent_segments"] is True
    assert projection["authority"]["secrets_authority"] is False
