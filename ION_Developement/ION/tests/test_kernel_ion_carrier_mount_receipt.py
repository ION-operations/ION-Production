from pathlib import Path

from kernel.ion_carrier_mount_receipt import (
    BLOCKED_VERDICT,
    READY_VERDICT,
    build_loaded_ref,
    build_mount_receipt,
    build_persona_presentation,
    compare_mount_to_branch_capsule,
    degrade_to_receipt_only,
    detect_mount_drift,
    render_mount_identity_card,
    render_public_working_state,
    validate_mount_receipt,
    validate_persona_presentation,
    write_mount_receipt_candidate,
)


def _seed_ref(root: Path) -> dict:
    ref = root / "ION/REPO_AUTHORITY.md"
    ref.parent.mkdir(parents=True, exist_ok=True)
    ref.write_text("# authority\n", encoding="utf-8")
    return build_loaded_ref(root, "ION/REPO_AUTHORITY.md")


def _valid_receipt(root: Path) -> dict:
    persona = build_persona_presentation(
        persona_id="role.persona_interface",
        public_working_state="Mounted and presenting a public working state.",
    )
    return build_mount_receipt(
        root=root,
        agent_tag="codex_local_ion_mason",
        carrier="codex_cli",
        carrier_instance_id="carrier_test_001",
        conversation_tag="mount_persona_test",
        context_instance_id="ctx_test_001",
        branch_id="branch_test_001",
        current_packet="PCKT-TEST",
        model_lane="codex_local",
        loaded_refs=[_seed_ref(root)],
        write_scope=["ION/04_packages/kernel/ion_carrier_mount_receipt.py"],
        source_posture={"repo_observed": ["ION/REPO_AUTHORITY.md"]},
        persona_presentation=persona,
    )


def test_valid_mount_receipt_passes_validation(tmp_path: Path):
    receipt = _valid_receipt(tmp_path)

    result = validate_mount_receipt(receipt)

    assert result["ok"] is True
    assert result["verdict"] == READY_VERDICT


def test_missing_context_instance_id_fails_validation(tmp_path: Path):
    receipt = _valid_receipt(tmp_path)
    receipt["carrier_mount"]["context_instance_id"] = ""

    result = validate_mount_receipt(receipt)

    assert result["ok"] is False
    assert any(item["field"] == "context_instance_id" for item in result["findings"])


def test_accepted_state_authority_defaults_false(tmp_path: Path):
    receipt = _valid_receipt(tmp_path)

    authority = receipt["carrier_mount"]["authority"]

    assert authority["accepted_state_authority"] is False
    assert authority["production_authority"] is False
    assert authority["live_execution_authority"] is False


def test_loaded_refs_preserve_source_type_and_sha256(tmp_path: Path):
    ref = _seed_ref(tmp_path)

    assert ref["source_type"] == "repo"
    assert ref["path"] == "ION/REPO_AUTHORITY.md"
    assert len(ref["sha256"]) == 64


def test_persona_full_mode_validates_with_id_and_public_state():
    persona = build_persona_presentation(
        persona_id="role.persona_interface",
        public_working_state="Showing public progress without hidden reasoning.",
    )

    result = validate_persona_presentation(persona)

    assert persona["presentation_mode"] == "full_persona"
    assert persona["persona_mounted"] is True
    assert result["ok"] is True


def test_persona_missing_context_degrades_to_receipt_only():
    persona = build_persona_presentation(persona_id=None, public_working_state=None)

    assert persona["presentation_mode"] == "receipt_only"
    assert persona["persona_mounted"] is False
    assert "operate_receipt_only" in persona["fallback_behavior"]


def test_hidden_reasoning_exposed_true_fails_validation():
    persona = build_persona_presentation(
        persona_id="role.persona_interface",
        public_working_state="bad",
        hidden_reasoning_exposed=True,
    )

    result = validate_persona_presentation(persona)

    assert result["ok"] is False
    assert any(item["code"] == "hidden_reasoning_exposed_forbidden" for item in result["findings"])


def test_render_mount_identity_card_includes_authority_and_source_posture(tmp_path: Path):
    receipt = _valid_receipt(tmp_path)

    card = render_mount_identity_card(receipt)

    assert "ION CARRIER MOUNT RECEIPT" in card
    assert "ACCEPTED_STATE_AUTHORITY: False" in card
    assert "SOURCE_POSTURE" in card
    assert "ION/REPO_AUTHORITY.md" in card


def test_render_public_working_state_never_exposes_hidden_reasoning():
    persona = degrade_to_receipt_only()

    text = render_public_working_state(persona)

    assert "hidden_reasoning_exposed: false" in text
    assert "receipt_only" in text


def test_detect_mount_drift_flags_persona_hidden_reasoning(tmp_path: Path):
    receipt = _valid_receipt(tmp_path)
    receipt["persona_presentation"]["hidden_reasoning_exposed"] = True

    result = detect_mount_drift(receipt)

    assert result["ok"] is False
    assert result["verdict"] == BLOCKED_VERDICT


def test_compare_mount_to_branch_capsule_detects_mismatch(tmp_path: Path):
    receipt = _valid_receipt(tmp_path)
    branch = {
        "context_instance_id": "ctx_other",
        "branch_id": "branch_test_001",
        "agent_tag": "codex_local_ion_mason",
        "conversation_tag": "mount_persona_test",
        "parent_context_id": "ION_MAIN_CURRENT_CONTEXT",
        "write_scope": ["ION/04_packages/kernel/ion_carrier_mount_receipt.py"],
    }

    result = compare_mount_to_branch_capsule(receipt, branch)

    assert result["ok"] is False
    assert any(item["field"] == "context_instance_id" for item in result["findings"])


def test_write_mount_receipt_candidate_writes_candidate_file(tmp_path: Path):
    receipt = _valid_receipt(tmp_path)

    result = write_mount_receipt_candidate(tmp_path, receipt)

    assert result["ok"] == "true"
    assert (tmp_path / result["path"]).exists()
