from __future__ import annotations

import json
from pathlib import Path

from kernel.ion_true_name_binding import (
    bind_true_name,
    claim_bound_work_lease,
    load_true_name_binding,
    parse_true_name,
    validate_lease_claim,
    validate_path_claim,
)
from kernel.ion_worker_shift_presence import load_shift_board, sign_off, sign_on


def _root(tmp_path: Path) -> Path:
    root = tmp_path / "ion-root"
    (root / "ION").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")
    return root


def test_codex_a2_vault_move_parses_structured_fields() -> None:
    parsed = parse_true_name("codex_a2_vault_move")

    assert parsed["carrier"] == "codex"
    assert parsed["lane"] == "A"
    assert parsed["sequence"] == 2
    assert parsed["mission_movement"] == "vault_move"
    assert parsed["inferred_domain"] == "security.vault"
    assert parsed["authority"]["production_authority"] is False
    assert parsed["authority"]["live_execution_authority"] is False


def test_vault_true_name_can_touch_vault_paths_only_when_explicitly_assigned() -> None:
    binding = bind_true_name(
        "codex_a2_vault_move",
        folder_domains=["security.vault"],
        context_package_ids=["CTX-SECURITY-VAULT"],
        allowed_path_scopes=["ION_VAULT_LOCAL/env", "ION/05_context/current/security"],
    )

    accepted = validate_path_claim(binding, ["ION_VAULT_LOCAL/env/supabase.local.env"])
    assert accepted["ok"] is True

    unassigned = bind_true_name(
        "codex_a2_vault_move",
        folder_domains=["security.vault"],
        context_package_ids=["CTX-SECURITY-VAULT"],
        allowed_path_scopes=["ION/05_context/current/security"],
    )
    rejected = validate_path_claim(unassigned, ["ION_VAULT_LOCAL/env/supabase.local.env"])

    assert rejected["ok"] is False
    assert rejected["rejections"][0]["reasons"] == ["PATH_OUTSIDE_TRUE_NAME_BINDING"]


def test_wave_reconcile_true_name_cannot_touch_vault_or_env_paths() -> None:
    binding = bind_true_name(
        "codex_c1_wave_reconcile",
        folder_domains=["context.wave"],
        context_package_ids=["CTX-WAVE-RECONCILE"],
        allowed_path_scopes=["ION/05_context/current/context_settlement", "ION/05_context/current/waves"],
    )

    rejected = validate_path_claim(binding, ["ION_VAULT_LOCAL/env/supabase.local.env"])

    assert rejected["ok"] is False
    rejection = rejected["rejections"][0]
    assert "PATH_OUTSIDE_TRUE_NAME_BINDING" in rejection["reasons"]
    assert "DOMAIN_PATH_MISMATCH" in rejection["reasons"]


def test_missing_context_package_marks_binding_incomplete_not_ready() -> None:
    binding = bind_true_name(
        "codex_b2_true_name_binding",
        folder_domains=["mission.true_name_binding"],
        allowed_path_scopes=["ION/04_packages/kernel/ion_true_name_binding.py"],
    )

    assert binding["binding_status"] == "INCOMPLETE"
    assert binding["binding_ready"] is False
    assert binding["incomplete_reasons"] == ["MISSING_CONTEXT_PACKAGE"]

    rejected = validate_path_claim(binding, ["ION/04_packages/kernel/ion_true_name_binding.py"])
    assert rejected["ok"] is False
    assert rejected["rejections"][0]["reason"] == "TRUE_NAME_BINDING_INCOMPLETE"


def test_true_name_binding_never_grants_production_live_or_secret_authority(tmp_path: Path) -> None:
    root = _root(tmp_path)
    binding = bind_true_name(
        "codex_b2_true_name_binding",
        folder_domains=["mission.true_name_binding"],
        context_package_ids=["CTX-TRUE-NAME-BINDING"],
        allowed_path_scopes=["ION/04_packages/kernel/ion_true_name_binding.py"],
        root=root,
        write=True,
    )

    loaded = load_true_name_binding("codex_b2_true_name_binding", root=root)
    assert loaded is not None
    assert json.loads(json.dumps(loaded))["true_name"] == "codex_b2_true_name_binding"
    assert binding["authority"]["production_authority"] is False
    assert binding["authority"]["live_execution_authority"] is False
    assert binding["authority"]["secrets_authority"] is False
    assert binding["authority"]["deploy_authority"] is False


def test_signed_off_or_expired_true_name_cannot_claim_new_lease_without_new_sign_on(tmp_path: Path) -> None:
    root = _root(tmp_path)
    binding = bind_true_name(
        "codex_b2_true_name_binding",
        folder_domains=["mission.true_name_binding"],
        context_package_ids=["CTX-TRUE-NAME-BINDING"],
        allowed_path_scopes=["ION/04_packages/kernel/ion_true_name_binding.py"],
    )
    sign_on(
        "codex_b2_true_name_binding",
        "codex_cli",
        "true_name_context_binding",
        ["ION/04_packages/kernel/ion_true_name_binding.py"],
        root=root,
        now="2026-05-17T16:00:00+00:00",
    )
    board = load_shift_board(root)
    active = validate_lease_claim(
        binding,
        lease_id="lease-codex-b2",
        paths=["ION/04_packages/kernel/ion_true_name_binding.py"],
        mode="write",
        board=board,
    )
    assert active["ok"] is True

    sign_off(
        "codex_b2_true_name_binding",
        "done",
        root=root,
        now="2026-05-17T16:10:00+00:00",
    )
    signed_off_board = load_shift_board(root)
    rejected = validate_lease_claim(
        binding,
        lease_id="lease-codex-b2-late",
        paths=["ION/04_packages/kernel/ion_true_name_binding.py"],
        mode="write",
        board=signed_off_board,
    )
    assert rejected["ok"] is False
    assert rejected["rejections"][-1]["reason"] == "TRUE_NAME_HAS_NO_ACTIVE_SIGN_ON"

    expired_binding = dict(binding)
    expired_binding["binding_status"] = "EXPIRED"
    expired_binding["binding_ready"] = False
    expired = validate_lease_claim(
        expired_binding,
        lease_id="lease-codex-b2-expired",
        paths=["ION/04_packages/kernel/ion_true_name_binding.py"],
        mode="write",
        board=board,
    )
    assert expired["ok"] is False
    assert expired["rejections"][0]["reason"] == "TRUE_NAME_BINDING_NOT_ACTIVE"


def test_parent_child_path_matching_for_binding_scopes() -> None:
    binding = bind_true_name(
        "codex_b2_true_name_binding",
        folder_domains=["mission.true_name_binding"],
        context_package_ids=["CTX-TRUE-NAME-BINDING"],
        allowed_path_scopes=["ION/04_packages/kernel"],
    )

    child = validate_path_claim(binding, ["ION/04_packages/kernel/ion_true_name_binding.py"])
    sibling = validate_path_claim(binding, ["ION/tests/test_kernel_ion_true_name_binding.py"])

    assert child["ok"] is True
    assert sibling["ok"] is False
    assert sibling["rejections"][0]["reasons"] == ["PATH_OUTSIDE_TRUE_NAME_BINDING"]


def test_claim_bound_work_lease_validates_before_claiming(tmp_path: Path) -> None:
    root = _root(tmp_path)
    binding = bind_true_name(
        "codex_b2_true_name_binding",
        folder_domains=["mission.true_name_binding"],
        context_package_ids=["CTX-TRUE-NAME-BINDING"],
        allowed_path_scopes=["ION/04_packages/kernel/ion_true_name_binding.py"],
    )
    sign_on(
        "codex_b2_true_name_binding",
        "codex_cli",
        "true_name_context_binding",
        ["ION/04_packages/kernel/ion_true_name_binding.py"],
        root=root,
        now="2026-05-17T16:00:00+00:00",
    )
    board = load_shift_board(root)

    claimed = claim_bound_work_lease(
        binding,
        root=root,
        lease_id="lease-codex-b2",
        paths=["ION/04_packages/kernel/ion_true_name_binding.py"],
        mode="write",
        board=board,
        now="2026-05-17T16:01:00+00:00",
    )

    assert claimed["ok"] is True
    assert claimed["lease_claim"]["receipt"]["result"] == "ACTIVE"
