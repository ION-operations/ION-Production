from __future__ import annotations

from pathlib import Path

import pytest

from kernel.ion_chatgpt_sandbox_return_intake import (
    authorize_sandbox_return_output_path,
    register_sandbox_return,
    write_sandbox_return_file,
)
from kernel.ion_mcp_client_configs import authorize_mcp_client_config_output_dir, write_profiles
from kernel.ion_trunk_preservation_gate import (
    authorize_trunk_preservation_output_path,
    build_file_manifest,
    write_file_manifest,
)
from kernel.ion_worker_shift_presence import claim_work_lease, load_shift_board, sign_off, sign_on
from kernel.root_authority_bundle import (
    KernelRootAuthorityBundleError,
    KernelRootAuthorityBundleManager,
    authorize_root_authority_bundle_output_path,
)


TRUE_NAME = "codex_g5_deferred_artifact_surface_guard"
RETURN_ID = "sev-20260517-224500-g5-guard"

G5_SURFACE_CLASSIFICATIONS = {
    "ion_chatgpt_sandbox_return_intake.py": {
        "classification": "PATCHED_TO_USE_PATH_AUTHORITY",
        "uses_path_authority": True,
        "exemption_reason": None,
    },
    "root_authority_bundle.py": {
        "classification": "PATCHED_TO_USE_PATH_AUTHORITY",
        "uses_path_authority": True,
        "exemption_reason": None,
    },
    "ion_trunk_preservation_gate.py": {
        "classification": "PATCHED_TO_USE_PATH_AUTHORITY",
        "uses_path_authority": True,
        "exemption_reason": None,
    },
    "ion_mcp_client_configs.py": {
        "classification": "PATCHED_TO_USE_PATH_AUTHORITY",
        "uses_path_authority": True,
        "exemption_reason": None,
    },
}


def _active_root(tmp_path: Path) -> Path:
    active = tmp_path / "workspace" / "ION_Developement"
    (active / "ION/REPO_AUTHORITY.md").parent.mkdir(parents=True, exist_ok=True)
    (active / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")
    (active / "pyproject.toml").write_text("[project]\nname = \"ion-g5-test\"\n", encoding="utf-8")
    return active


def _packet() -> dict:
    return {
        "return_id": RETURN_ID,
        "summary_text": "# G5 Sandbox Return\n\nGuard test only.",
        "source_snapshot": {
            "package_path_seen_by_chatgpt": "g5.zip",
            "package_sha256": "unknown-unless-provided-or-computed",
            "archive_root_confirmed": True,
            "expected_root_markers": ["pyproject.toml", "ION/REPO_AUTHORITY.md"],
        },
        "changed_paths": ["ION/04_packages/kernel/ion_chatgpt_sandbox_return_intake.py"],
        "sandbox_validation": {"commands_run": [], "passed": None, "limitations": ["guard test only"]},
    }


def test_g5_surface_classifications_cover_all_surfaces_without_silent_exemptions() -> None:
    assert set(G5_SURFACE_CLASSIFICATIONS) == {
        "ion_chatgpt_sandbox_return_intake.py",
        "root_authority_bundle.py",
        "ion_trunk_preservation_gate.py",
        "ion_mcp_client_configs.py",
    }
    assert all(item["classification"] == "PATCHED_TO_USE_PATH_AUTHORITY" for item in G5_SURFACE_CLASSIFICATIONS.values())
    assert all(item["uses_path_authority"] is True for item in G5_SURFACE_CLASSIFICATIONS.values())
    assert not [item for item in G5_SURFACE_CLASSIFICATIONS.values() if item["exemption_reason"]]


@pytest.mark.parametrize(
    ("raw_path", "reason_code"),
    (
        ("/home/sev/ION_EXPORTS_LOCAL", "FORBIDDEN_ROOT"),
        ("../ION_EXPORTS_LOCAL", "PARENT_SEGMENT_FORBIDDEN"),
    ),
)
def test_every_g5_surface_authorizer_rejects_forbidden_export_paths(tmp_path: Path, raw_path: str, reason_code: str) -> None:
    active = _active_root(tmp_path)
    decisions = {
        "ion_chatgpt_sandbox_return_intake.py": authorize_sandbox_return_output_path(active, raw_path),
        "root_authority_bundle.py": authorize_root_authority_bundle_output_path(active, raw_path),
        "ion_trunk_preservation_gate.py": authorize_trunk_preservation_output_path(active, raw_path),
        "ion_mcp_client_configs.py": authorize_mcp_client_config_output_dir(active, raw_path),
    }

    assert set(decisions) == set(G5_SURFACE_CLASSIFICATIONS)
    for decision in decisions.values():
        assert decision["authorized"] is False
        assert decision["reason_code"] == reason_code
        assert decision["raw_path"] == raw_path
        assert decision["resolved_path"]
        assert decision["classification"]


@pytest.mark.parametrize("bad_output", ("/home/sev/ION_EXPORTS_LOCAL", "../ION_EXPORTS_LOCAL"))
def test_patched_surfaces_block_bad_outputs_before_materialization(tmp_path: Path, bad_output: str) -> None:
    active = _active_root(tmp_path)
    assert register_sandbox_return(active, _packet())["ok"] is True

    sandbox = write_sandbox_return_file(active, RETURN_ID, bad_output, {"text": "blocked"})
    assert sandbox["ok"] is False
    assert sandbox["path_authority"]["authorized"] is False

    manager = KernelRootAuthorityBundleManager()
    with pytest.raises(KernelRootAuthorityBundleError, match="path authority rejected"):
        manager.materialize_external_exercise_brief(
            workspace_root=active,
            carrier_key="browser_chatgpt",
            output_path=bad_output,
        )

    manifest = build_file_manifest(active, generated_at="2026-05-17T22:45:00+00:00")
    with pytest.raises(ValueError, match="path authority rejected"):
        write_file_manifest(active, manifest, bad_output)

    with pytest.raises(ValueError, match="path authority rejected"):
        write_profiles(bad_output, active / "ION", python_executable="python")

    if bad_output.startswith(".."):
        assert not (active.parent / "ION_EXPORTS_LOCAL").exists()


def test_g5_guard_exercises_no_live_upload_or_action(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    active = _active_root(tmp_path)
    calls: list[tuple[object, ...]] = []

    def forbidden_live_call(*args: object, **kwargs: object) -> dict:
        calls.append(args)
        raise AssertionError("live action should not be called by G5 guard tests")

    import kernel.ion_chatgpt_browser_mcp_connector_contract as connector_contract

    monkeypatch.setattr(connector_contract, "call_chatgpt_connector_tool", forbidden_live_call)
    assert register_sandbox_return(active, _packet())["ok"] is True
    blocked = write_sandbox_return_file(active, RETURN_ID, "../ION_EXPORTS_LOCAL", {"text": "blocked"})

    assert blocked["ok"] is False
    assert calls == []


def test_worker_shift_true_name_consistency_for_g5(tmp_path: Path) -> None:
    active = _active_root(tmp_path)
    path = "ION/tests/test_kernel_ion_deferred_artifact_surface_guard.py"

    signon = sign_on(
        TRUE_NAME,
        "codex",
        "G5 deferred artifact surface guard",
        [path],
        root=active,
        now="2026-05-17T22:45:00+00:00",
    )
    lease = claim_work_lease(
        TRUE_NAME,
        "lease:codex_g5_deferred_artifact_surface_guard_allowed_paths",
        [path],
        "write",
        root=active,
        now="2026-05-17T22:46:00+00:00",
    )
    signoff = sign_off(
        TRUE_NAME,
        {"summary": "G5 guard test signoff", "validation": ["true-name preserved"]},
        root=active,
        now="2026-05-17T22:47:00+00:00",
    )

    assert signon["receipt"]["worker_id"] == TRUE_NAME
    assert lease["receipt"]["lease"]["worker_id"] == TRUE_NAME
    assert signoff["receipt"]["worker_id"] == TRUE_NAME
    assert signoff["receipt"]["declared_true_name"] == TRUE_NAME
    assert load_shift_board(active)["active_shifts"] == []
