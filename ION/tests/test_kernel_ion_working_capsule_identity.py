import json
from pathlib import Path

from kernel.ion_working_capsule_identity import (
    BLOCKED_VERDICT,
    FALLBACK_VERDICT,
    READY_VERDICT,
    REPAIR_REQUIRED_VERDICT,
    build_working_capsule_identity,
    prepare_local_capsule_maintenance,
    validate_working_capsule_identity,
    working_capsule_preflight,
)


def _seed_root(root: Path) -> None:
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    authority = root / "ION/REPO_AUTHORITY.md"
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("# authority\n", encoding="utf-8")


def _identity(root: Path, **overrides):
    cwd = root / "ION/05_context/current/codex_agent_mounts/role_demo__domain_demo"
    payload = build_working_capsule_identity(
        root=root,
        cwd=cwd,
        domain_id="domain.demo",
        role_id="role.demo",
        carrier_instance_id="codex_session_demo",
        codex_agent_mount=cwd,
    ).to_dict()
    payload.update(overrides)
    return payload


def test_working_capsule_blocks_shared_codex_solo_as_working_identity(tmp_path: Path) -> None:
    _seed_root(tmp_path)
    payload = _identity(
        tmp_path,
        instance_capsule_id="shared_codex_solo",
        working_capsule_path=(tmp_path / "ION/05_context/current/codex_solo").as_posix(),
    )

    result = validate_working_capsule_identity(tmp_path, payload)

    assert result["ok"] is False
    assert result["verdict"] == BLOCKED_VERDICT
    assert any(item["code"] == "shared_codex_solo_as_working_capsule_forbidden" for item in result["findings"])


def test_working_capsule_blocks_clone_without_lineage(tmp_path: Path) -> None:
    _seed_root(tmp_path)
    payload = _identity(tmp_path, parent_capsule_ref="wcaps_parent", lineage_id=None)

    result = validate_working_capsule_identity(tmp_path, payload)

    assert result["ok"] is False
    assert any(item["code"] == "clone_lineage_required" for item in result["findings"])


def test_working_capsule_preflight_classifies_codex_agent_mount_null_as_repair_required(tmp_path: Path) -> None:
    _seed_root(tmp_path)

    result = working_capsule_preflight(
        tmp_path,
        {"codex_agent_mount": None, "work_class": "active_root_repair"},
        active_root_repair_allowed=True,
    )

    assert result["ok"] is True
    assert result["verdict"] == REPAIR_REQUIRED_VERDICT
    assert result["classification"] == "repair_required"
    assert any(item["code"] == "working_capsule_identity_missing" for item in result["findings"])


def test_working_capsule_preflight_accepts_explicit_shared_codex_solo_fallback(tmp_path: Path) -> None:
    _seed_root(tmp_path)

    result = working_capsule_preflight(
        tmp_path,
        {"shared_codex_solo_fallback_reason": "active-root repair lane uses global witness while identity gate is being patched"},
    )

    assert result["ok"] is True
    assert result["verdict"] == FALLBACK_VERDICT


def test_working_capsule_blocks_old_root_reference(tmp_path: Path) -> None:
    _seed_root(tmp_path)
    payload = _identity(
        tmp_path,
        parent_capsule_ref="/home/sev/ION - Production/ION_CODEX FULL/ION/05_context/current/codex_solo/CAPSULE.md",
        lineage_id="lineage_demo",
    )

    result = validate_working_capsule_identity(tmp_path, payload)

    assert result["ok"] is False
    assert any(item["code"] == "stale_ion_codex_full_root_reference" for item in result["findings"])


def test_generated_domain_agent_instance_capsule_maintenance(tmp_path: Path) -> None:
    _seed_root(tmp_path)
    identity = _identity(tmp_path, lineage_id="lineage_demo", parent_capsule_ref="parent_wcaps")

    result = prepare_local_capsule_maintenance(
        tmp_path,
        identity,
        task_return_packet_path="ION/05_context/current/chatgpt_connector/task_returns/test_task_return.json",
        machine_receipt_path="ION/05_context/current/chatgpt_connector/task_return_machine_receipts/test_receipt.json",
        proof_status="RETURN_RECORDED_PROOF_ACCEPTED",
    )

    assert result["ok"] is True
    assert result["verdict"] == READY_VERDICT
    capsule_dir = Path(identity["working_capsule_path"])
    assert (capsule_dir / "CAPSULE.md").is_file()
    assert (capsule_dir / "MINI.md").is_file()
    assert (capsule_dir / "HOT_CONTEXT.md").is_file()
    receipt = json.loads((tmp_path / result["receipt_path"]).read_text(encoding="utf-8"))
    assert receipt["identity"]["instance_capsule_id"] == identity["instance_capsule_id"]
    assert receipt["authority"]["accepted_state_authority"] is False


def test_active_branch_templates_do_not_govern_old_codex_full_root() -> None:
    template_root = Path("ION/05_context/current/agent_context_branches/templates")
    for rel in (
        "AGENT_BRANCH_CAPSULE.template.md",
        "AGENT_BRANCH_STATUS.template.json",
        "AGENT_CONTEXT_IDENTITY_CARD.template.md",
    ):
        text = (template_root / rel).read_text(encoding="utf-8")
        assert "/home/sev/ION - Production/ION_CODEX FULL" not in text
