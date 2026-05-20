from __future__ import annotations

from pathlib import Path

from kernel.ion_agent_cwd_boundary import build_agent_cwd_boundary


def _write_manifest(path: Path) -> None:
    workspace = path.parent
    path.write_text(
        f"""schema_id: ion.workspace_manifest.v1
status: TEST

workspace_root: "{workspace}"
active_repo_root: "{workspace}/ION_Developement"
ion_content_root: "{workspace}/ION_Developement/ION"
export_root: "{workspace}/ION_EXPORTS_LOCAL"
vault_root: "{workspace}/ION_VAULT_LOCAL"

allowed_sibling_roots:
  - "{workspace}/ION_EXPORTS_LOCAL"
  - "{workspace}/ION_VAULT_LOCAL"
  - "{workspace}/Needs_Routed"
  - "{workspace}/quarentine"

forbidden_roots:
  - "{workspace.parent}/ION_EXPORTS_LOCAL"
  - "{workspace.parent}/.ssh"

path_policy:
  forbid_parent_segments_for_write: true
  canonicalize_all_leases: true

families:
  ION_Developement:
    role: active ION kernel/context repo
    git_status: nested_repo_current
  browser_extension:
    role: browser carrier extension
    git_status: workspace_folder_candidate
  dAimon:
    role: dAimon app/agent project
    git_status: nested_repo_current
  Needs_Routed:
    role: operator staging/inbox
    git_status: workspace_folder_candidate
  quarentine:
    role: archive witness and quarantine
    git_status: workspace_folder_candidate
    active_source: false
""",
        encoding="utf-8",
    )


def _workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "ION - Production"
    for rel in (
        "ION_Developement/ION",
        "browser_extension/ion_chatops_bridge",
        "dAimon",
        "Needs_Routed",
        "quarentine",
        "ION_EXPORTS_LOCAL",
        "ION_VAULT_LOCAL",
    ):
        (workspace / rel).mkdir(parents=True)
    _write_manifest(workspace / "ION_WORKSPACE_MANIFEST.yaml")
    return workspace


def test_active_ion_movement_launches_from_active_root(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    active = workspace / "ION_Developement"

    boundary = build_agent_cwd_boundary(
        {
            "workspace_root": str(workspace),
            "active_ion_root": str(active),
            "actual_cwd": str(active),
            "actual_realpath": str(active),
            "target_project_root": str(active),
            "target_content_root": str(active / "ION"),
        },
        active_root=active,
        manifest_path=workspace / "ION_WORKSPACE_MANIFEST.yaml",
    )

    assert boundary["accepted"] is True
    assert boundary["worker_launch_cwd"] == str(active)
    assert boundary["target_command_cwd"] == str(active)
    assert boundary["target_root_id"] == "active_ion_control"


def test_sibling_project_movement_launches_from_target_project_root(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    active = workspace / "ION_Developement"
    extension = workspace / "browser_extension/ion_chatops_bridge"

    boundary = build_agent_cwd_boundary(
        {
            "workspace_root": str(workspace),
            "active_ion_root": str(active),
            "actual_cwd": str(active),
            "actual_realpath": str(active),
            "target_project_root": str(extension),
            "target_content_root": str(extension),
        },
        active_root=active,
        manifest_path=workspace / "ION_WORKSPACE_MANIFEST.yaml",
    )

    assert boundary["accepted"] is True
    assert boundary["control_plane_cwd"] == str(active)
    assert boundary["worker_launch_cwd"] == str(extension)
    assert boundary["target_command_cwd"] == str(extension)
    assert boundary["target_root_id"] == "browser_extension"


def test_blocks_unknown_parallel_top_level_worker_cwd(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    active = workspace / "ION_Developement"
    duplicate = workspace / "ION_CODEX"

    boundary = build_agent_cwd_boundary(
        {
            "workspace_root": str(workspace),
            "active_ion_root": str(active),
            "actual_cwd": str(active),
            "actual_realpath": str(active),
            "target_project_root": str(duplicate),
            "target_content_root": str(duplicate),
        },
        active_root=active,
        manifest_path=workspace / "ION_WORKSPACE_MANIFEST.yaml",
    )

    assert boundary["accepted"] is False
    assert "AGENT_CWD_UNKNOWN_TARGET_ROOT" in boundary["blocker_codes"]


def test_blocks_declared_sibling_worker_cwd_that_points_back_to_active_root(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    active = workspace / "ION_Developement"
    daimon = workspace / "dAimon"

    boundary = build_agent_cwd_boundary(
        {
            "workspace_root": str(workspace),
            "active_ion_root": str(active),
            "actual_cwd": str(active),
            "actual_realpath": str(active),
            "target_project_root": str(daimon),
            "target_content_root": str(daimon),
            "worker_launch_cwd": str(active),
        },
        active_root=active,
        manifest_path=workspace / "ION_WORKSPACE_MANIFEST.yaml",
    )

    assert boundary["accepted"] is False
    assert "WORKER_LAUNCH_CWD_TARGET_MISMATCH" in boundary["blocker_codes"]
