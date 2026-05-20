from __future__ import annotations

from pathlib import Path

from kernel.ion_ai_movement_gate import evaluate_ai_movement_gate


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
  require_workspace_containment_for_artifacts: true
  require_artifacts_outside_active_repo: true

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
        "ION_Developement/ION/05_context/current/reports",
        "ION_Developement/ION/05_context/current/worker_shift/signons",
        "ION_Developement/ION/05_context/current/worker_shift/leases",
        "ION_Developement/ION/05_context/current/worker_shift/signoffs",
        "ION_GPT",
        "browser_extension/ion_chatops_bridge/src",
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
    _write_manifest(workspace / "ION_WORKSPACE_MANIFEST.yaml", allowed_archive_root=allowed_archive_root)
    return workspace


def _base_envelope(workspace: Path) -> dict:
    active_root = workspace / "ION_Developement"
    return {
        "actual_cwd": str(active_root),
        "actual_realpath": str(active_root),
        "expected_cwd": str(active_root),
        "expected_realpath": str(active_root),
        "target_project_root": str(active_root),
        "target_content_root": str(active_root / "ION"),
        "movement_class": "ION_KERNEL_CONTROL_MOVEMENT",
        "domain_context_package": "ION/05_context/current/system_cartography",
        "active_template": "CODEX_SOLO_WORK_UNIT",
        "requested_authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        },
        "planned_reads": ["ION/REPO_AUTHORITY.md"],
        "planned_writes": ["ION/05_context/current/reports/example.md"],
        "planned_artifacts": [],
        "settlement_target": "ION/05_context/current/reports/example-ledger.json",
        "receipt_paths": [
            "ION/05_context/current/worker_shift/signons/**",
            "ION/05_context/current/worker_shift/leases/**",
            "ION/05_context/current/worker_shift/signoffs/**",
        ],
    }


def _codes(decision: dict) -> set[str]:
    return {blocker["code"] for blocker in decision["blockers"]}


def test_accepts_active_ion_report_only_movement(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)

    decision = evaluate_ai_movement_gate(
        _base_envelope(workspace),
        manifest_path=workspace / "ION_WORKSPACE_MANIFEST.yaml",
    )

    assert decision["accepted"] is True
    assert decision["target_root_id"] == "active_ion_control"
    assert decision["target_root_class"] == "ACTIVE_ION_CONTROL_ROOT"
    assert decision["path_authority_decisions"]


def test_rejects_wrong_cwd_and_realpath(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    envelope = _base_envelope(workspace)
    envelope["actual_cwd"] = str(workspace)
    envelope["actual_realpath"] = str(workspace)

    decision = evaluate_ai_movement_gate(envelope, manifest_path=workspace / "ION_WORKSPACE_MANIFEST.yaml")

    assert decision["accepted"] is False
    assert "WRONG_ROOT_CWD" in _codes(decision)
    assert "EXPECTED_REALPATH_MISMATCH" in _codes(decision)


def test_rejects_active_ion_parent_relative_sibling_write(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    envelope = _base_envelope(workspace)
    envelope["planned_writes"] = ["../ION_GPT/01_GPT_BUILDER_INPUTS/README.md"]

    decision = evaluate_ai_movement_gate(envelope, manifest_path=workspace / "ION_WORKSPACE_MANIFEST.yaml")

    assert decision["accepted"] is False
    assert "PATH_AUTHORITY_REJECTED" in _codes(decision)
    assert "ACTIVE_ROOT_PARENT_RELATIVE_WRITE" in _codes(decision)
    assert "SIBLING_ROOT_IMPLICIT_EDIT" in _codes(decision)


def test_rejects_missing_context_template_and_receipts(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    envelope = _base_envelope(workspace)
    envelope.pop("domain_context_package")
    envelope.pop("active_template")
    envelope["receipt_paths"] = []

    decision = evaluate_ai_movement_gate(envelope, manifest_path=workspace / "ION_WORKSPACE_MANIFEST.yaml")

    assert decision["accepted"] is False
    assert "DOMAIN_PACKAGE_MISSING" in _codes(decision)
    assert "TEMPLATE_MISSING" in _codes(decision)
    assert "MISSING_SIGNON_RECEIPT" in _codes(decision)
    assert "MISSING_LEASE_RECEIPT" in _codes(decision)
    assert "MISSING_SIGNOFF_RECEIPT" in _codes(decision)


def test_rejects_authority_escalation(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    envelope = _base_envelope(workspace)
    envelope["requested_authority"] = {
        "production_authority": True,
        "live_execution_authority": True,
        "accepted_state_claim": True,
        "service_restart_authority": True,
    }

    decision = evaluate_ai_movement_gate(envelope, manifest_path=workspace / "ION_WORKSPACE_MANIFEST.yaml")

    assert decision["accepted"] is False
    assert "PRODUCTION_AUTHORITY_UNGRANTED" in _codes(decision)
    assert "LIVE_EXECUTION_AUTHORITY_UNGRANTED" in _codes(decision)
    assert "ACCEPTED_STATE_CLAIM_UNGRANTED" in _codes(decision)
    assert "SERVICE_RESTART_AUTHORITY_UNGRANTED" in _codes(decision)


def test_rejects_daimon_movement_from_active_ion_cwd(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    active_root = workspace / "ION_Developement"
    daimon = workspace / "dAimon"
    envelope = _base_envelope(workspace)
    envelope.update(
        {
            "actual_cwd": str(active_root),
            "actual_realpath": str(active_root),
            "expected_cwd": str(daimon),
            "expected_realpath": str(daimon),
            "target_project_root": str(daimon),
            "target_content_root": str(daimon),
            "movement_class": "DAIMON_PROJECT_MOVEMENT",
            "planned_writes": [str(daimon / "README.md")],
        }
    )

    decision = evaluate_ai_movement_gate(envelope, manifest_path=workspace / "ION_WORKSPACE_MANIFEST.yaml")

    assert decision["accepted"] is False
    assert "WRONG_ROOT_CWD" in _codes(decision)
    assert "EXPECTED_REALPATH_MISMATCH" in _codes(decision)
    assert decision["target_root_id"] == "daimon"


def test_rejects_unknown_parallel_top_level_root(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    envelope = _base_envelope(workspace)
    target = workspace / "ION_CODEX"
    envelope["target_project_root"] = str(target)
    envelope["target_content_root"] = str(target)

    decision = evaluate_ai_movement_gate(envelope, manifest_path=workspace / "ION_WORKSPACE_MANIFEST.yaml")

    assert decision["accepted"] is False
    assert "UNKNOWN_ROOT_CLASS" in _codes(decision)
    assert "DUPLICATE_TOP_LEVEL_ROOT_CREATION" in _codes(decision)


def test_rejects_blocked_quarantine_alias_target(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    envelope = _base_envelope(workspace)
    target = workspace / "quarantine"
    envelope["target_project_root"] = str(target)
    envelope["target_content_root"] = str(target)

    decision = evaluate_ai_movement_gate(envelope, manifest_path=workspace / "ION_WORKSPACE_MANIFEST.yaml")

    assert decision["accepted"] is False
    assert "DUPLICATE_TOP_LEVEL_ROOT_CREATION" in _codes(decision)


def test_rejects_vault_and_env_reads(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    envelope = _base_envelope(workspace)
    envelope["planned_reads"] = [
        str(workspace / "ION_VAULT_LOCAL/secret.txt"),
        str(workspace / ".env.local"),
    ]

    decision = evaluate_ai_movement_gate(envelope, manifest_path=workspace / "ION_WORKSPACE_MANIFEST.yaml")

    assert decision["accepted"] is False
    assert "VAULT_OR_ENV_READ_ATTEMPT" in _codes(decision)


def test_rejects_active_repo_artifact_output(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    envelope = _base_envelope(workspace)
    envelope["planned_artifacts"] = [str(workspace / "ION_Developement/ION_EXPORTS_LOCAL/package.zip")]

    decision = evaluate_ai_movement_gate(envelope, manifest_path=workspace / "ION_WORKSPACE_MANIFEST.yaml")

    assert decision["accepted"] is False
    assert "ARTIFACT_INSIDE_ACTIVE_REPO" in _codes(decision)
