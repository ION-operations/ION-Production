from __future__ import annotations

import json
from pathlib import Path

from kernel.ion_codex_mount_guard import (
    BLOCKED_STATE,
    PARTIAL_STATE,
    READY_STATE,
    build_codex_mount_status,
    main,
    render_mount_guard_block,
    write_current_mount_status,
)


def _seed_ready_root(tmp_path: Path) -> Path:
    root = tmp_path / "ion-root"
    required_paths = [
        "pyproject.toml",
        "ION/REPO_AUTHORITY.md",
        "ION/02_architecture/ION_MOUNT_CONTRACT.md",
        "ION/02_architecture/CODEX_CLI_CARRIER_PROTOCOL.md",
        "ION/03_registry/codex_cli_carrier_profile.yaml",
        "ION/07_templates/carriers/CODEX_CLI_EXECUTION_PACKET.md",
        "ION/05_context/current/codex_solo/CAPSULE.md",
        "ION/05_context/current/codex_solo/MINI.md",
        "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
        "ION/05_context/current/codex_solo/STATUS.json",
        "ION/04_packages/kernel/ion_codex_carrier_sync.py",
        "ION/04_packages/kernel/ion_carrier_mount_receipt.py",
    ]
    for rel_path in required_paths:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{rel_path}\n", encoding="utf-8")
    return root


def test_codex_mount_status_ready_when_all_required_refs_exist(tmp_path: Path) -> None:
    root = _seed_ready_root(tmp_path)

    status = build_codex_mount_status(root)

    assert status["schema_id"] == "ion.codex_mount_guard.v0_1"
    assert status["mount_truth_state"] == READY_STATE
    assert status["ok"] is True
    assert status["required_refs_present"] == status["required_ref_count"]
    assert status["authority"]["production_authority"] is False
    assert status["authority"]["accepted_state_authority"] is False
    assert all(ref["sha256"] for ref in status["required_refs"])


def test_codex_mount_status_partial_when_context_refs_are_missing(tmp_path: Path) -> None:
    root = tmp_path / "ion-root"
    (root / "ION").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")

    status = build_codex_mount_status(root)

    assert status["mount_truth_state"] == PARTIAL_STATE
    assert status["ok"] is False
    assert "required_mount_refs_missing" in status["blockers"]
    assert "ION/02_architecture/ION_MOUNT_CONTRACT.md" in status["missing_required_refs"]


def test_codex_mount_status_blocked_when_root_proof_missing(tmp_path: Path) -> None:
    status = build_codex_mount_status(tmp_path)

    assert status["mount_truth_state"] == BLOCKED_STATE
    assert status["ok"] is False
    assert "root_proof_missing" in status["blockers"]


def test_render_mount_guard_block_is_compact_and_authority_bounded(tmp_path: Path) -> None:
    status = build_codex_mount_status(_seed_ready_root(tmp_path))

    block = render_mount_guard_block(status)

    assert "ION Codex Mount Guard v0.1" in block
    assert f"mount_truth_state: {READY_STATE}" in block
    assert "no production" in block
    assert "ION Codex carrier mounted" in block
    assert "blockers: none" in block


def test_write_current_mount_status_writes_candidate_snapshot(tmp_path: Path) -> None:
    root = _seed_ready_root(tmp_path)
    status = build_codex_mount_status(root)

    result = write_current_mount_status(root, status)

    assert result["ok"] is True
    written = json.loads((root / result["path"]).read_text(encoding="utf-8"))
    assert written["mount_truth_state"] == READY_STATE
    assert written["non_claims"]


def test_cli_status_can_write_current_snapshot(tmp_path: Path, capsys) -> None:
    root = _seed_ready_root(tmp_path)

    assert main(["--ion-root", str(root), "status", "--json", "--write-current"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"]["mount_truth_state"] == READY_STATE
    assert payload["write_current"]["path"].endswith("CURRENT_CODEX_CARRIER_MOUNT.json")
