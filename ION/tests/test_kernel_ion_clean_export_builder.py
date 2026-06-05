from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from kernel.ion_clean_export_builder import authorize_output_dir, build_clean_export, resolve_ion_root, resolve_output_dir


def _write(path: Path, text: str = "content\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seed_root(root: Path) -> None:
    _write(root / "pyproject.toml", "[project]\nname='ion-clean-export-test'\n")
    _write(root / "README.md", "# ION test root\n")
    _write(root / "SECURITY.md", "security\n")
    _write(root / "ION/REPO_AUTHORITY.md", "# authority\n")
    _write(root / "ION/02_architecture/ION_CLEAN_EXPORT_POLICY.md", "# policy\n")
    _write(root / "ION/04_packages/kernel/example.py", "VALUE = 1\n")
    _write(root / "ION/tests/test_example.py", "def test_example():\n    assert True\n")
    _write(root / "ION/07_templates/export/CLEAN_EXPORT_MANIFEST_TEMPLATE.md", "# template\n")
    _write(
        root / "ION/05_context/current/reports/SINGLE_CARRIER_OPERATING_SPINE_SETTLEMENT_REPORT.md",
        "# spine\n",
    )
    _write(root / "ION/05_context/current/reports/SINGLE_CARRIER_OPERATING_SPINE_SETTLEMENT_LEDGER.json", "{}\n")
    _write(root / "ION/05_context/current/reports/WAVE_001_002_RECONCILIATION_REPORT.md", "# wave\n")
    _write(root / "ION/05_context/current/reports/WAVE_001_002_RECONCILIATION_LEDGER.json", "{}\n")
    _write(root / "ION/05_context/current/reports/WAVE_003_PLAN_ONLY.md", "# plan only\n")
    _write(root / "ION/05_context/current/ACTIVE_WORK_PACKET.json", "{}\n")
    _write(root / "ION/05_context/current/worker_shift/signons/signon.json", "{}\n")
    _write(root / "ION/05_context/current/worker_shift/leases/lease.json", "{}\n")
    _write(root / "ION/05_context/current/worker_shift/signoffs/signoff.json", "{}\n")


def _export_root(root: Path) -> Path:
    return root.parent / "ION_EXPORTS_LOCAL"


def test_clean_export_excludes_forbidden_paths_and_raw_needs_routed(tmp_path: Path) -> None:
    root = tmp_path / "workspace" / "ION_Developement"
    _seed_root(root)
    _write(root / ".env", "LOCAL_ONLY=dummy-value\n")
    _write(root / ".env.supabase.local.example", "SUPABASE_URL=replace-me\n")
    _write(root / "ION_VAULT_LOCAL/secret.txt", "dummy vault\n")
    _write(root / "ION/04_packages/kernel/__pycache__/example.cpython-312.pyc", "bytecode\n")
    _write(root / "ION/04_packages/kernel/stale.pyc", "bytecode\n")
    _write(root / "node_modules/pkg/index.js", "module\n")
    _write(root / "Needs_Routed/raw_packet.md", "raw bulk\n")

    result = build_clean_export(root, output_dir=_export_root(root), dry_run=True)
    paths = {item["path"] for item in result["included_files"]}
    summary = result["excluded_summary"]["counts_by_reason"]

    assert result["ok"] is True
    assert ".env" not in paths
    assert ".env.supabase.local.example" not in paths
    assert not any(path.startswith("ION_VAULT_LOCAL") for path in paths)
    assert not any("__pycache__" in path or path.endswith(".pyc") for path in paths)
    assert not any("node_modules" in path for path in paths)
    assert not any(path.startswith("Needs_Routed/") for path in paths)
    assert summary["dotenv_file"] >= 2
    assert summary["forbidden_runtime_or_cache_dir"] >= 2
    assert summary["needs_routed_raw_bulk"] == 1


def test_clean_export_refuses_when_included_file_contains_raw_secret(tmp_path: Path) -> None:
    root = tmp_path / "workspace" / "ION_Developement"
    _seed_root(root)
    _write(
        root / "ION/02_architecture/SECRET_EXAMPLE.md",
        "SUPABASE_SERVICE_ROLE_KEY=live_material_value_123456789\n",
    )

    result = build_clean_export(root, output_dir=_export_root(root), dry_run=False)

    assert result["ok"] is False
    assert result["verdict"] == "REFUSED_SECRET_SCAN_BLOCKER"
    assert result["secret_scan"]["accepted"] is False
    assert result["secret_scan"]["findings"][0]["path"] == "ION/02_architecture/SECRET_EXAMPLE.md"
    assert result["archive_path"] is None
    assert not list(_export_root(root).glob("*.zip"))
    assert "live_material_value" not in json.dumps(result)


def test_clean_export_manifest_contains_hash_counts_exclusions_and_status(tmp_path: Path) -> None:
    root = tmp_path / "workspace" / "ION_Developement"
    _seed_root(root)
    _write(root / ".env.local", "LOCAL_ONLY=dummy-value\n")

    result = build_clean_export(root, output_dir=_export_root(root), dry_run=False, export_id="TEST_EXPORT")

    assert result["ok"] is True
    assert result["archive_sha256"]
    assert len(result["archive_sha256"]) == 64
    assert result["file_count"] == len(result["included_files"])
    assert result["excluded_summary"]["counts_by_reason"]["dotenv_file"] == 1
    assert result["status_verdict_at_export_time"]["verdict"]
    assert result["workspace_root"] == str(root.parent)
    assert result["output_root_policy"] == "workspace_local_outside_active_repo"
    assert result["output_authorization"]["authorized"] is True
    assert Path(result["sidecar_manifest_path"]).is_file()


def test_clean_export_zip_has_no_forbidden_paths_and_includes_review_reports(tmp_path: Path) -> None:
    root = tmp_path / "workspace" / "ION_Developement"
    _seed_root(root)
    _write(root / "ION_VAULT_LOCAL/secret.txt", "dummy vault\n")
    _write(root / "Needs_Routed/raw.md", "raw\n")

    result = build_clean_export(root, output_dir=_export_root(root), dry_run=False, export_id="TEST_EXPORT")

    with zipfile.ZipFile(result["archive_path"]) as archive:
        names = set(archive.namelist())

    forbidden_fragments = ("ION_VAULT_LOCAL", ".env", "__pycache__", "node_modules", "Needs_Routed", ".git")
    assert not any(any(fragment in name for fragment in forbidden_fragments) for name in names)
    assert f"ION_CLEAN_EXPORT/{'ION/05_context/current/reports/SINGLE_CARRIER_OPERATING_SPINE_SETTLEMENT_REPORT.md'}" in names
    assert f"ION_CLEAN_EXPORT/{'ION/05_context/current/reports/SINGLE_CARRIER_OPERATING_SPINE_SETTLEMENT_LEDGER.json'}" in names
    assert f"ION_CLEAN_EXPORT/{'ION/05_context/current/reports/WAVE_001_002_RECONCILIATION_REPORT.md'}" in names
    assert f"ION_CLEAN_EXPORT/{'ION/05_context/current/reports/WAVE_001_002_RECONCILIATION_LEDGER.json'}" in names
    assert f"ION_CLEAN_EXPORT/{'ION/05_context/current/reports/WAVE_003_PLAN_ONLY.md'}" in names


def test_clean_export_default_output_path_is_workspace_local(tmp_path: Path) -> None:
    root = tmp_path / "workspace" / "ION_Developement"
    _seed_root(root)

    resolved = resolve_output_dir(resolve_ion_root(root))

    assert resolved == root.parent / "ION_EXPORTS_LOCAL"


def test_clean_export_relative_parent_output_cannot_escape_workspace_due_to_cwd(tmp_path: Path) -> None:
    root = tmp_path / "workspace" / "ION_Developement"
    _seed_root(root)

    with pytest.raises(ValueError, match="PARENT_SEGMENT_FORBIDDEN"):
        resolve_output_dir(resolve_ion_root(root), "../ION_EXPORTS_LOCAL")


def test_clean_export_rejects_output_path_inside_active_repo(tmp_path: Path) -> None:
    root = tmp_path / "workspace" / "ION_Developement"
    _seed_root(root)

    with pytest.raises(ValueError, match="ARTIFACT_INSIDE_ACTIVE_REPO"):
        resolve_output_dir(resolve_ion_root(root), "ION_Developement/ION_EXPORTS_LOCAL")


def test_clean_export_rejects_output_path_outside_workspace(tmp_path: Path) -> None:
    root = tmp_path / "workspace" / "ION_Developement"
    outside = tmp_path / "outside" / "ION_EXPORTS_LOCAL"
    _seed_root(root)

    with pytest.raises(ValueError, match="WORKSPACE_ESCAPE_BLOCKED"):
        resolve_output_dir(resolve_ion_root(root), outside)


def test_clean_export_rejects_legacy_escaped_home_export_path(tmp_path: Path) -> None:
    root = tmp_path / "workspace" / "ION_Developement"
    _seed_root(root)

    with pytest.raises(ValueError, match="FORBIDDEN_ROOT"):
        resolve_output_dir(resolve_ion_root(root), "/home/sev/ION_EXPORTS_LOCAL")


def test_clean_export_accepts_workspace_local_export_path(tmp_path: Path) -> None:
    root = tmp_path / "workspace" / "ION_Developement"
    _seed_root(root)

    resolved = resolve_output_dir(resolve_ion_root(root), "ION_EXPORTS_LOCAL")

    assert resolved == root.parent / "ION_EXPORTS_LOCAL"


def test_clean_export_dry_run_with_parent_relative_output_is_blocked_without_archive(tmp_path: Path) -> None:
    root = tmp_path / "workspace" / "ION_Developement"
    _seed_root(root)

    result = build_clean_export(root, output_dir="../ION_EXPORTS_LOCAL", dry_run=True, export_id="BLOCKED_EXPORT")

    assert result["ok"] is False
    assert result["verdict"] == "BLOCKED_OUTPUT_PATH_AUTHORITY"
    assert result["output_authorization"]["authorized"] is False
    assert result["output_authorization"]["reason_code"] == "PARENT_SEGMENT_FORBIDDEN"
    assert result["archive_path"] is None
    assert not list((tmp_path / "ION_EXPORTS_LOCAL").glob("*.zip"))


def test_clean_export_dry_run_with_legacy_home_export_root_is_blocked_without_archive(tmp_path: Path) -> None:
    root = tmp_path / "workspace" / "ION_Developement"
    _seed_root(root)

    result = build_clean_export(root, output_dir="/home/sev/ION_EXPORTS_LOCAL", dry_run=True)

    assert result["ok"] is False
    assert result["verdict"] == "BLOCKED_OUTPUT_PATH_AUTHORITY"
    assert result["output_authorization"]["classification"] == "FORBIDDEN_ROOT"
    assert result["output_authorization"]["reason_code"] == "FORBIDDEN_ROOT"
    assert result["archive_path"] is None


def test_clean_export_default_dry_run_reports_workspace_local_authorization(tmp_path: Path) -> None:
    root = tmp_path / "workspace" / "ION_Developement"
    _seed_root(root)

    result = build_clean_export(root, dry_run=True)
    decision = authorize_output_dir(resolve_ion_root(root))

    assert result["ok"] is True
    assert result["archive_path"] is None
    assert result["output_dir"] == str(root.parent / "ION_EXPORTS_LOCAL")
    assert result["output_authorization"]["authorized"] is True
    assert decision["resolved_path"] == str(root.parent / "ION_EXPORTS_LOCAL")
