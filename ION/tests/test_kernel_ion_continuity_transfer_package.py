from pathlib import Path
import json
import zipfile

from kernel.ion_continuity_transfer_package import build_package


def test_continuity_transfer_package_builds_required_files(tmp_path):
    workspace = Path(__file__).resolve().parents[2]
    result = build_package(workspace, tmp_path, "20260513T000000Z")
    assert result["ok"] is True
    assert result["accepted_state_claim"] is False
    zpath = Path(result["zip_path"])
    assert zpath.exists()
    with zipfile.ZipFile(zpath) as zf:
        names = set(zf.namelist())
    required = {
        "README_START_HERE.md",
        "ion_continuity_transfer_manifest.yaml",
        "ion_boot_sequence_result.yaml",
        "ion_persona_response_envelope.yaml",
        "ion_sequence_continuation.yaml",
        "ion_dynamic_domain_agent_expansion.yaml",
        "ion_project_profile.yaml",
        "ion_receipt_summary.yaml",
        "ion_proof_manifest.yaml",
        "ion_non_claims.yaml",
        "ion_settlement_required.yaml",
        "patches/cumulative_candidate.patch",
        "reports/validation_report.md",
        "tests/validation_results.yaml",
        "sources/source_manifest.yaml",
        "NEXT_CHAT_PROMPT.txt",
    }
    assert required <= names


def test_continuity_transfer_package_has_no_authority_claims(tmp_path):
    workspace = Path(__file__).resolve().parents[2]
    result = build_package(workspace, tmp_path, "20260513T000001Z")
    with zipfile.ZipFile(result["zip_path"]) as zf:
        manifest = zf.read("ion_continuity_transfer_manifest.yaml").decode()
        non_claims = zf.read("ion_non_claims.yaml").decode()
    assert "accepted_state_claim: false" in manifest
    assert "production_authority: false" in manifest
    assert "live_execution_authority: false" in manifest
    assert "secrets_included: false" in non_claims


def test_continuity_transfer_package_assigns_project_hash(tmp_path):
    workspace = Path(__file__).resolve().parents[2]
    result = build_package(workspace, tmp_path, "20260513T000002Z")
    with zipfile.ZipFile(result["zip_path"]) as zf:
        manifest = zf.read("ion_continuity_transfer_manifest.yaml").decode()
        boot = zf.read("ion_boot_sequence_result.yaml").decode()
        continuation = zf.read("ion_sequence_continuation.yaml").decode()
        profile = zf.read("ion_project_profile.yaml").decode()
        next_prompt = zf.read("NEXT_CHAT_PROMPT.txt").decode()
    assert "ion_project_hash: ionproj_" in manifest
    assert "project_hash_status: assigned_candidate" in manifest
    assert "ion_project_hash: ionproj_" in boot
    assert "ion_project_hash: ionproj_" in continuation
    assert "ion_project_hash: ionproj_" in profile
    assert "PROJECT_HASH :: missing" in next_prompt
