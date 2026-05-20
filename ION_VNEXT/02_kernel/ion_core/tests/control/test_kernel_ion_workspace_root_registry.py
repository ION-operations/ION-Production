from __future__ import annotations

from pathlib import Path

from kernel.ion_workspace_root_registry import (
    CLASS_ACTIVE_ION_CONTROL_ROOT,
    CLASS_ARCHIVE_FILE_WITNESS,
    CLASS_ARCHIVE_WITNESS_ROOT,
    CLASS_CARRIER_INTEGRATION_ROOT,
    CLASS_EXTERNAL_GOVERNED_PROJECT_ROOT,
    CLASS_FORBIDDEN_EXTERNAL_ROOT,
    CLASS_ION_CONTENT_ROOT,
    CLASS_INTAKE_ROOT,
    CLASS_PRODUCT_PROJECTION_ROOT,
    CLASS_UNKNOWN_ROOT,
    CONFLICT_ROOT_ALIAS_OR_TYPO,
    build_workspace_root_registry,
    classify_workspace_path,
)


WORKSPACE_ROOT = Path("/home/sev/ION - Production")
ION_ROOT = WORKSPACE_ROOT / "ION_Developement"


def _write_manifest(path: Path, *, allowed_archive_root: str = "quarentine") -> None:
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
  - "{workspace}/{allowed_archive_root}"

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
  ION_GPT:
    role: Custom GPT surfaces
    git_status: workspace_folder_candidate
  browser_extension:
    role: browser carrier extension
    git_status: workspace_folder_candidate
  mcp:
    role: MCP and ChatGPT browser connector surfaces
    git_status: workspace_folder_candidate
  local_daemon:
    role: local bridge daemons
    git_status: workspace_folder_candidate
  systemd:
    role: local user service templates
    git_status: workspace_folder_candidate
  product_packager:
    role: packaging/export builders
    git_status: workspace_folder_candidate
  Cursor:
    role: Cursor integration surfaces
    git_status: workspace_folder_candidate
  dAimon:
    role: dAimon app/agent project
    git_status: nested_repo_current
  AIM-OS:
    role: AIM/legacy/adjacent architecture corpus
    git_status: nested_repo_current
  ATLAS:
    role: ATLAS surfaces
    git_status: workspace_folder_candidate
  wisdomNET:
    role: WisdomNET surfaces
    git_status: workspace_folder_candidate
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


def _workspace(tmp_path: Path, *, allowed_archive_root: str = "quarentine") -> Path:
    workspace = tmp_path / "ION - Production"
    for rel in (
        "ION_Developement/ION",
        "ION_GPT",
        "browser_extension",
        "mcp",
        "local_daemon",
        "systemd",
        "product_packager",
        "Cursor",
        "dAimon",
        "AIM-OS",
        "ATLAS",
        "wisdomNET",
        "Needs_Routed",
        "quarentine",
        "ION_EXPORTS_LOCAL",
        "ION_VAULT_LOCAL",
    ):
        (workspace / rel).mkdir(parents=True)
    (workspace / "ION_GPT.zip").write_text("archive witness\n", encoding="utf-8")
    _write_manifest(workspace / "ION_WORKSPACE_MANIFEST.yaml", allowed_archive_root=allowed_archive_root)
    return workspace


def _by_id(registry: dict, root_id: str) -> dict:
    return next(entry for entry in registry["roots"] if entry["root_id"] == root_id)


def test_current_workspace_manifest_projects_quarentine_without_quarantine_conflict() -> None:
    registry = build_workspace_root_registry()

    assert registry["accepted"] is True
    assert "/home/sev/ION - Production/quarentine" in registry["manifest"]["allowed_sibling_roots"]
    assert "/home/sev/ION - Production/quarantine" not in registry["manifest"]["allowed_sibling_roots"]
    assert registry["conflicts"] == []
    alias = registry["aliases"][0]
    assert alias["canonical_root_id"] == "quarentine"
    assert alias["allowed_to_create_alias_path"] is False


def test_registry_classifies_primary_projection_carrier_and_external_roots(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    registry = build_workspace_root_registry(workspace / "ION_WORKSPACE_MANIFEST.yaml")

    assert _by_id(registry, "active_ion_control")["root_class"] == CLASS_ACTIVE_ION_CONTROL_ROOT
    assert _by_id(registry, "ion_content")["root_class"] == CLASS_ION_CONTENT_ROOT
    assert _by_id(registry, "ion_gpt")["root_class"] == CLASS_PRODUCT_PROJECTION_ROOT
    assert _by_id(registry, "browser_extension")["root_class"] == CLASS_CARRIER_INTEGRATION_ROOT
    assert _by_id(registry, "mcp")["root_class"] == CLASS_CARRIER_INTEGRATION_ROOT
    assert _by_id(registry, "local_daemon")["root_class"] == CLASS_CARRIER_INTEGRATION_ROOT
    assert _by_id(registry, "systemd")["root_class"] == CLASS_CARRIER_INTEGRATION_ROOT
    assert _by_id(registry, "cursor")["root_class"] == CLASS_CARRIER_INTEGRATION_ROOT
    assert _by_id(registry, "daimon")["root_class"] == CLASS_EXTERNAL_GOVERNED_PROJECT_ROOT
    assert _by_id(registry, "needs_routed")["root_class"] == CLASS_INTAKE_ROOT
    assert _by_id(registry, "quarentine")["root_class"] == CLASS_ARCHIVE_WITNESS_ROOT
    assert _by_id(registry, "quarentine")["active_source"] is False


def test_registry_classifies_archive_zips_as_witness_files_not_roots(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    registry = build_workspace_root_registry(workspace / "ION_WORKSPACE_MANIFEST.yaml")

    assert registry["archive_files"]
    archive = registry["archive_files"][0]
    assert archive["path"].endswith("ION_GPT.zip")
    assert archive["root_class"] == CLASS_ARCHIVE_FILE_WITNESS
    assert archive["active_source"] is False
    assert archive["extraction_allowed"] is False
    assert archive["promotion_required"] is True


def test_quarantine_manifest_alias_conflict_is_reported_without_creating_folder(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path, allowed_archive_root="quarantine")
    registry = build_workspace_root_registry(workspace / "ION_WORKSPACE_MANIFEST.yaml")

    assert registry["accepted"] is False
    assert not (workspace / "quarantine").exists()
    assert registry["conflicts"][0]["type"] == CONFLICT_ROOT_ALIAS_OR_TYPO
    assert registry["conflicts"][0]["manifest_path"] == str(workspace / "quarantine")
    assert registry["conflicts"][0]["observed_path"] == str(workspace / "quarentine")


def test_classify_workspace_path_rejects_home_as_project_root_and_unknown_workspace_child(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    registry = build_workspace_root_registry(workspace / "ION_WORKSPACE_MANIFEST.yaml")

    outside = classify_workspace_path(workspace.parent, registry=registry)
    unknown_child = classify_workspace_path(workspace / "new_parallel_root", registry=registry)

    assert outside["root_class"] == CLASS_FORBIDDEN_EXTERNAL_ROOT
    assert unknown_child["root_class"] == CLASS_UNKNOWN_ROOT


def test_classify_workspace_path_maps_children_to_root_classes(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    registry = build_workspace_root_registry(workspace / "ION_WORKSPACE_MANIFEST.yaml")

    ion_child = classify_workspace_path(workspace / "ION_Developement/ION/04_packages/kernel/example.py", registry=registry)
    extension_child = classify_workspace_path(workspace / "browser_extension/ion_chatops_bridge/src/content.ts", registry=registry)
    archive_child = classify_workspace_path(workspace / "quarentine/old-package.zip", registry=registry)

    assert ion_child["root_class"] == CLASS_ION_CONTENT_ROOT
    assert ion_child["root_id"] == "ion_content"
    assert extension_child["root_class"] == CLASS_CARRIER_INTEGRATION_ROOT
    assert extension_child["root_id"] == "browser_extension"
    assert archive_child["root_class"] == CLASS_ARCHIVE_WITNESS_ROOT
    assert archive_child["root_id"] == "quarentine"
