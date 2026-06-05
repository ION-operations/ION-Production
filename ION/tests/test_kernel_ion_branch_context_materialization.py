from __future__ import annotations

import json
from pathlib import Path

from kernel.ion_branch_context_materialization import (
    build_candidate_branch_capsule,
    build_materialization_receipt,
    classify_branch_context,
    find_parent_branch_context,
    inspect_branch_path,
    should_ignore_branch_path,
    write_materialization_receipt,
)


def _root(tmp_path: Path) -> Path:
    root = tmp_path / "ion-root"
    (root / "ION").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")
    (root / "README.md").write_text("# Root\n\nRead `ION_CONTEXT_CAPSULE.yaml`.\n", encoding="utf-8")
    (root / "ION_CONTEXT_CAPSULE.yaml").write_text(
        "\n".join(
            [
                "schema_id: ion.branch_context_node.v0_1",
                "branch_id: root",
                "branch_label: Root",
                "path: .",
                "maturity_level: B2_capsule_node",
                "purpose: Root context.",
                "authority:",
                "  accepted_state_claim: false",
                "  production_authority: false",
                "  live_execution_authority: false",
                "read_order:",
                "  - README.md",
                "local_surfaces: {}",
                "receipts:",
                "  latest: []",
                "continuity_export:",
                "  include:",
                "    - README.md",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return root


def test_absent_meaningful_folder_inherits_parent_when_dry_run(tmp_path: Path) -> None:
    root = _root(tmp_path)
    branch = root / "ION/04_packages/kernel/demo_branch"
    branch.mkdir(parents=True)
    (branch / "worker.py").write_text("print('candidate')\n", encoding="utf-8")

    result = classify_branch_context(branch, root=root)

    assert result["classification"] == "materializable_branch"
    assert result["decision"] == "inherited"
    assert result["maturity_level"] == "level_1_inherited"
    assert result["candidate_available"] is True
    assert result["should_write_files"] is False
    assert result["parent_context"]["capsule_path"] == "ION_CONTEXT_CAPSULE.yaml"
    assert not (branch / "ION_CONTEXT_CAPSULE.yaml").exists()


def test_meaningful_source_folder_can_produce_candidate_capsule_data(tmp_path: Path) -> None:
    root = _root(tmp_path)
    branch = root / "ION/04_packages/kernel/new_helper"
    branch.mkdir(parents=True)
    (branch / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")
    inspection = inspect_branch_path(branch, root=root)
    parent = find_parent_branch_context(branch, root=root)

    capsule = build_candidate_branch_capsule(branch, parent, inspection, root=root)

    assert capsule["schema_id"] == "ion.branch_context_capsule_candidate.v0_1"
    assert capsule["path"] == "ION/04_packages/kernel/new_helper"
    assert capsule["parent_branch_ref"] == "ION_CONTEXT_CAPSULE.yaml"
    assert capsule["maturity_level"] == "level_3_candidate"
    assert capsule["accepted_state_claim"] is False


def test_existing_local_capsule_is_detected_and_not_overwritten(tmp_path: Path) -> None:
    root = _root(tmp_path)
    branch = root / "ION/02_architecture"
    branch.mkdir(parents=True)
    capsule = branch / "ION_CONTEXT_CAPSULE.yaml"
    capsule.write_text(
        "schema_id: ion.branch_context_node.v0_1\nmaturity_level: B2_capsule_node\n",
        encoding="utf-8",
    )
    before = capsule.read_text(encoding="utf-8")

    result = classify_branch_context(branch, root=root, materialize=True)

    assert result["classification"] == "existing_local_context"
    assert result["decision"] == "inherited"
    assert result["candidate_available"] is False
    assert capsule.read_text(encoding="utf-8") == before


def test_ignored_paths_are_skipped() -> None:
    ignored = [
        ".git/config",
        "node_modules/pkg",
        "venv/lib",
        ".venv/lib",
        "dist/app.js",
        "build/out",
        "cache/blob",
        "__pycache__/module.pyc",
        "vendor/pkg",
        "quarentine/archive",
        "ION_VAULT_LOCAL/secrets.env",
        "vault/secrets/token.txt",
        "artifact.tar.gz",
    ]

    for path in ignored:
        assert should_ignore_branch_path(path), path


def test_parent_context_discovery_works_upward(tmp_path: Path) -> None:
    root = _root(tmp_path)
    parent = root / "ION/04_packages"
    child = parent / "kernel/subbranch"
    child.mkdir(parents=True)
    (parent / "README.md").write_text("# Packages\n\nRead `ION_CONTEXT_CAPSULE.yaml`.\n", encoding="utf-8")
    (parent / "ION_CONTEXT_CAPSULE.yaml").write_text(
        "schema_id: ion.branch_context_node.v0_1\nmaturity_level: B2_capsule_node\n",
        encoding="utf-8",
    )

    found = find_parent_branch_context(child, root=root)

    assert found["found"] is True
    assert found["path"] == "ION/04_packages"
    assert found["capsule_path"] == "ION/04_packages/ION_CONTEXT_CAPSULE.yaml"


def test_materialization_receipt_includes_parent_decision_paths_and_hashes(tmp_path: Path) -> None:
    root = _root(tmp_path)
    branch = root / "ION/07_templates/context/demo"
    branch.mkdir(parents=True)
    created = branch / "ION_CONTEXT_CAPSULE.yaml"
    created.write_text("schema_id: ion.branch_context_capsule_candidate.v0_1\n", encoding="utf-8")
    classification = classify_branch_context(branch, root=root, materialize=True)

    receipt = build_materialization_receipt(
        branch,
        classification=classification,
        touched_paths=[created],
        created_files=[created],
        next_carrier_instructions=["read the candidate capsule before editing this branch"],
        root=root,
    )

    assert receipt["schema_id"] == "ion.branch_context_materialization_receipt.v0_1"
    assert receipt["branch_path"] == "ION/07_templates/context/demo"
    assert receipt["parent_context_used"]["capsule_path"] == "ION_CONTEXT_CAPSULE.yaml"
    assert receipt["decision"] == "inherited"
    assert receipt["touched_paths"] == ["ION/07_templates/context/demo/ION_CONTEXT_CAPSULE.yaml"]
    assert len(receipt["created_file_sha256"]["ION/07_templates/context/demo/ION_CONTEXT_CAPSULE.yaml"]) == 64
    assert receipt["accepted_state_claim"] is False


def test_write_materialization_receipt_is_dry_run_by_default(tmp_path: Path) -> None:
    root = _root(tmp_path)
    branch = root / "ION/04_packages/kernel/dry_run"
    branch.mkdir(parents=True)
    receipt = build_materialization_receipt(branch, root=root, classification="materializable_branch")

    dry = write_materialization_receipt(receipt, root=root)

    assert dry["wrote"] is False
    assert not (root / "ION/05_context/current/branch_context_materialization/receipts").exists()

    written = write_materialization_receipt(receipt, root=root, write=True)
    assert written["wrote"] is True
    receipt_path = root / written["receipt_path"]
    assert receipt_path.is_file()
    assert json.loads(receipt_path.read_text(encoding="utf-8"))["schema_id"] == receipt["schema_id"]
