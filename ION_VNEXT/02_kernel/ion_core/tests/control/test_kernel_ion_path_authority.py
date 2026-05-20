from __future__ import annotations

from pathlib import Path

from kernel.ion_path_authority import (
    CLASS_ION_CONTENT,
    CLASS_OUTSIDE_WORKSPACE,
    CLASS_WORKSPACE_EXPORT,
    CLASS_WORKSPACE_SIBLING,
    CLASS_WORKSPACE_VAULT,
    REASON_ARTIFACT_INSIDE_ACTIVE_REPO,
    REASON_DOTENV_WRITE_FORBIDDEN,
    REASON_FORBIDDEN_ROOT,
    REASON_PARENT_SEGMENT_FORBIDDEN,
    REASON_VAULT_WRITE_FORBIDDEN,
    decide_path_authority,
    load_workspace_authority,
)


ION_ROOT = Path("/home/sev/ION - Production/ION_Developement")
WORKSPACE_ROOT = Path("/home/sev/ION - Production")


def test_exact_f1_1_parent_output_escape_is_blocked() -> None:
    raw = "../ION_EXPORTS_LOCAL"

    decision = decide_path_authority(raw, purpose="artifact", base_root="active_repo")

    assert decision["authorized"] is False
    assert decision["reason_code"] == REASON_PARENT_SEGMENT_FORBIDDEN
    assert decision["raw_path"] == raw
    assert decision["resolved_path"] != "/home/sev/ION_EXPORTS_LOCAL"


def test_exact_f1_1_builder_workspace_base_escape_is_blocked() -> None:
    decision = decide_path_authority("../ION_EXPORTS_LOCAL", purpose="artifact", base_root="workspace")

    assert decision["authorized"] is False
    assert decision["reason_code"] == REASON_PARENT_SEGMENT_FORBIDDEN
    assert decision["resolved_path"] == "/home/sev/ION_EXPORTS_LOCAL"


def test_bad_legacy_export_root_is_rejected() -> None:
    decision = decide_path_authority("/home/sev/ION_EXPORTS_LOCAL", purpose="artifact")

    assert decision["authorized"] is False
    assert decision["reason_code"] == REASON_FORBIDDEN_ROOT
    assert decision["classification"] == "FORBIDDEN_ROOT"


def test_correct_workspace_export_root_is_accepted() -> None:
    decision = decide_path_authority("/home/sev/ION - Production/ION_EXPORTS_LOCAL", purpose="artifact")

    assert decision["authorized"] is True
    assert decision["classification"] == CLASS_WORKSPACE_EXPORT
    assert decision["resolved_path"] == "/home/sev/ION - Production/ION_EXPORTS_LOCAL"


def test_active_repo_export_root_is_rejected_for_artifacts() -> None:
    decision = decide_path_authority(
        "/home/sev/ION - Production/ION_Developement/ION_EXPORTS_LOCAL",
        purpose="artifact",
    )

    assert decision["authorized"] is False
    assert decision["reason_code"] == REASON_ARTIFACT_INSIDE_ACTIVE_REPO


def test_vault_and_dotenv_writes_are_rejected_without_future_override() -> None:
    vault_absolute = decide_path_authority(
        "/home/sev/ION - Production/ION_VAULT_LOCAL/secret-note.txt",
        purpose="write",
    )
    vault_relative = decide_path_authority("ION_VAULT_LOCAL/secret-note.txt", purpose="write")
    dotenv = decide_path_authority(".env.local", purpose="write")

    assert vault_absolute["authorized"] is False
    assert vault_absolute["classification"] == CLASS_WORKSPACE_VAULT
    assert vault_absolute["reason_code"] == REASON_VAULT_WRITE_FORBIDDEN
    assert vault_relative["authorized"] is False
    assert vault_relative["reason_code"] == REASON_VAULT_WRITE_FORBIDDEN
    assert dotenv["authorized"] is False
    assert dotenv["reason_code"] == REASON_DOTENV_WRITE_FORBIDDEN


def test_child_paths_under_allowed_roots_classify_correctly() -> None:
    ion_content = decide_path_authority(
        "/home/sev/ION - Production/ION_Developement/ION/04_packages/kernel/ion_status.py",
        purpose="write",
    )
    export_child = decide_path_authority(
        "/home/sev/ION - Production/ION_EXPORTS_LOCAL/review/file.zip",
        purpose="artifact",
    )
    needs_routed_child = decide_path_authority(
        "/home/sev/ION - Production/Needs_Routed/inbox/example.md",
        purpose="read",
    )

    assert ion_content["authorized"] is True
    assert ion_content["classification"] == CLASS_ION_CONTENT
    assert export_child["authorized"] is True
    assert export_child["classification"] == CLASS_WORKSPACE_EXPORT
    assert needs_routed_child["authorized"] is True
    assert needs_routed_child["classification"] == CLASS_WORKSPACE_SIBLING


def test_outside_workspace_child_path_classifies_outside_and_rejects_write() -> None:
    decision = decide_path_authority("/home/sev/Projects/outside.txt", purpose="write")

    assert decision["authorized"] is False
    assert decision["classification"] == CLASS_OUTSIDE_WORKSPACE


def test_workspace_manifest_loads_canonical_roots() -> None:
    authority = load_workspace_authority()

    assert authority.workspace_root == WORKSPACE_ROOT
    assert authority.active_repo_root == ION_ROOT
    assert authority.export_root == WORKSPACE_ROOT / "ION_EXPORTS_LOCAL"
    assert Path("/home/sev/ION_EXPORTS_LOCAL") in authority.forbidden_roots
