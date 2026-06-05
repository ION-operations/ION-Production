from __future__ import annotations

from pathlib import Path

import pytest

from kernel.ion_artifact_purpose import (
    ARTIFACT_PURPOSES,
    CLASS_WORKSPACE_EXPORT,
    PURPOSE_CHATOPS_PAYLOAD,
    PURPOSE_CONTINUITY_TRANSFER_PACKAGE,
    PURPOSE_CUSTOM_GPT_SANDBOX_PACKAGE,
    PURPOSE_CUSTOM_GPT_UPLOAD_SET,
    PURPOSE_FULL_PROJECT_PACKAGE,
    PURPOSE_GDRIVE_CONTEXT_MIRROR,
    PURPOSE_LIFECYCLE_PACKAGE,
    PURPOSE_MCP_CONNECTOR_CONTRACT,
    REASON_UPLOAD_LIVE_ACTION_FORBIDDEN,
    authorize_artifact_path,
)
from kernel.ion_chatgpt_browser_mcp_connector_contract import _require_connector_artifact_path
from kernel.ion_chatops_bridge import _require_chatops_artifact_path
from kernel.ion_continuity_transfer_package import build_package as build_continuity_package
from kernel.ion_custom_gpt_sandbox_package import build_package as build_custom_gpt_sandbox_package
from kernel.ion_custom_gpt_upload_set_builder import build_package as build_custom_gpt_upload_package
from kernel.ion_gdrive_context_mirror import build_gdrive_context_mirror
from kernel.ion_lifecycle_packager import create_lifecycle_package_zip
from kernel.ion_safe_full_project_packager import create_safe_full_project_package


PATCHED_PURPOSES = (
    PURPOSE_FULL_PROJECT_PACKAGE,
    PURPOSE_CUSTOM_GPT_UPLOAD_SET,
    PURPOSE_CUSTOM_GPT_SANDBOX_PACKAGE,
    PURPOSE_LIFECYCLE_PACKAGE,
    PURPOSE_CONTINUITY_TRANSFER_PACKAGE,
    PURPOSE_GDRIVE_CONTEXT_MIRROR,
    PURPOSE_CHATOPS_PAYLOAD,
    PURPOSE_MCP_CONNECTOR_CONTRACT,
)


def _seed_workspace(tmp_path: Path) -> tuple[Path, Path]:
    workspace = tmp_path / "workspace"
    active = workspace / "ION_Developement"
    (active / "ION").mkdir(parents=True)
    (active / "pyproject.toml").write_text("[project]\nname = 'ion-artifact-surface-test'\n", encoding="utf-8")
    (active / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")
    return workspace, active


@pytest.mark.parametrize("purpose", PATCHED_PURPOSES)
def test_artifact_purposes_reject_legacy_home_export_root(tmp_path: Path, purpose: str) -> None:
    _, active = _seed_workspace(tmp_path)

    decision = authorize_artifact_path(
        "/home/sev/ION_EXPORTS_LOCAL",
        purpose=purpose,
        active_root=active,
        base_root="workspace",
    )

    assert decision["authorized"] is False
    assert decision["classification"] == "FORBIDDEN_ROOT"
    assert decision["reason_code"] == "FORBIDDEN_ROOT"


@pytest.mark.parametrize("purpose", PATCHED_PURPOSES)
def test_artifact_purposes_reject_parent_segment_output(tmp_path: Path, purpose: str) -> None:
    _, active = _seed_workspace(tmp_path)

    decision = authorize_artifact_path(
        "../ION_EXPORTS_LOCAL",
        purpose=purpose,
        active_root=active,
        base_root="workspace",
    )

    assert decision["authorized"] is False
    assert decision["reason_code"] == "PARENT_SEGMENT_FORBIDDEN"


@pytest.mark.parametrize("purpose", PATCHED_PURPOSES)
def test_workspace_export_root_acceptance_matches_purpose_policy(tmp_path: Path, purpose: str) -> None:
    workspace, active = _seed_workspace(tmp_path)
    export_path = workspace / "ION_EXPORTS_LOCAL" / f"{purpose}.zip"
    decision = authorize_artifact_path(export_path, purpose=purpose, active_root=active)
    policy = ARTIFACT_PURPOSES[purpose]

    if CLASS_WORKSPACE_EXPORT in policy.allowed_root_classes:
        assert decision["authorized"] is True
        assert decision["classification"] == CLASS_WORKSPACE_EXPORT
    else:
        assert decision["authorized"] is False
        assert decision["reason_code"] == "ARTIFACT_ROOT_CLASS_NOT_ALLOWED"


@pytest.mark.parametrize(
    "surface",
    (
        "safe_full_project",
        "custom_gpt_upload_set",
        "custom_gpt_sandbox_package",
        "lifecycle_package",
        "continuity_transfer_package",
        "gdrive_context_mirror",
        "chatops_payload",
        "mcp_connector_contract",
    ),
)
@pytest.mark.parametrize("bad_output", ("/home/sev/ION_EXPORTS_LOCAL", "../ION_EXPORTS_LOCAL"))
def test_patched_surfaces_block_forbidden_outputs_before_materialization(
    tmp_path: Path,
    surface: str,
    bad_output: str,
) -> None:
    workspace, active = _seed_workspace(tmp_path)

    with pytest.raises(ValueError, match="artifact path authority rejected"):
        if surface == "safe_full_project":
            create_safe_full_project_package(
                active,
                output_zip=bad_output,
                write_manifests=False,
                write_report=False,
            )
        elif surface == "custom_gpt_upload_set":
            build_custom_gpt_upload_package(
                workspace,
                "ion_latest_status_and_receipts",
                Path(bad_output),
                "20260517T000000Z",
            )
        elif surface == "custom_gpt_sandbox_package":
            build_custom_gpt_sandbox_package(workspace, Path(bad_output))
        elif surface == "lifecycle_package":
            create_lifecycle_package_zip(active, output_zip=bad_output, write_manifest=False)
        elif surface == "continuity_transfer_package":
            build_continuity_package(workspace, Path(bad_output), "20260517T000000Z")
        elif surface == "gdrive_context_mirror":
            build_gdrive_context_mirror(active, output=bad_output, emitted_at="2026-05-17T00:00:00Z")
        elif surface == "chatops_payload":
            _require_chatops_artifact_path(active, bad_output)
        elif surface == "mcp_connector_contract":
            _require_connector_artifact_path(active, bad_output)

    assert not (tmp_path / "ION_EXPORTS_LOCAL").exists()


def test_upload_or_live_action_mode_is_blocked_by_default(tmp_path: Path) -> None:
    _, active = _seed_workspace(tmp_path)
    decision = authorize_artifact_path(
        active / "ION/05_context/current/chatgpt_connector/artifacts/upload.bin",
        purpose=PURPOSE_MCP_CONNECTOR_CONTRACT,
        active_root=active,
        live_action=True,
    )

    assert decision["authorized"] is False
    assert decision["reason_code"] == REASON_UPLOAD_LIVE_ACTION_FORBIDDEN
