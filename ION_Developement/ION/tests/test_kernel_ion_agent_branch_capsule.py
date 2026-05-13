import json
from pathlib import Path

from kernel.ion_agent_branch_capsule import (
    BLOCKED_VERDICT,
    READY_VERDICT,
    build_branch_capsule_record,
    build_settlement_request,
    create_branch_capsule,
    detect_wrong_context_drift,
    material_work_preflight,
    reconcile_branch_registry,
    render_context_identity_card,
    settlement_intake_preflight,
    validate_branch_capsule,
    validate_branch_record,
)


def test_branch_capsule_record_validates_and_renders_identity(tmp_path: Path):
    record = build_branch_capsule_record(
        root=tmp_path,
        context_instance_id="ctx_test_001",
        branch_id="branch_test_001",
        agent_tag="Codex Local",
        conversation_tag="Branch Capsule Test",
        write_scope=["ION/04_packages/kernel/ion_agent_branch_capsule.py"],
    )

    validation = validate_branch_record(tmp_path, record)
    card = render_context_identity_card(record)

    assert validation["ok"] is True
    assert validation["verdict"] == READY_VERDICT
    assert record.agent_tag == "codex_local"
    assert "context_instance_id: ctx_test_001" in card
    assert "accepted_state_authority: False" in card
    assert validate_branch_capsule(tmp_path, record)["ok"] is True


def test_detect_wrong_context_drift_reports_root_mismatch(tmp_path: Path):
    other_root = tmp_path / "other"
    record = build_branch_capsule_record(
        root=other_root,
        context_instance_id="ctx_drift_001",
        branch_id="branch_drift_001",
        agent_tag="codex",
        conversation_tag="drift",
        write_scope=["ION/docs/drift.md"],
    )

    result = detect_wrong_context_drift(tmp_path, record)

    assert result["ok"] is False
    assert result["verdict"] == BLOCKED_VERDICT
    assert any(item["code"] == "root_mismatch" for item in result["drift_findings"])


def test_branch_capsule_blocks_shared_context_write_scope(tmp_path: Path):
    record = build_branch_capsule_record(
        root=tmp_path,
        context_instance_id="ctx_bad_001",
        branch_id="branch_bad_001",
        agent_tag="codex",
        conversation_tag="bad",
        write_scope=["ION/05_context/current/codex_solo/HOT_CONTEXT.md"],
    )

    validation = validate_branch_record(tmp_path, record)

    assert validation["ok"] is False
    assert validation["verdict"] == BLOCKED_VERDICT
    assert any(item["code"] == "shared_context_surface_in_write_scope" for item in validation["findings"])


def test_material_work_preflight_requires_declared_scope_and_blocks_shared_context(tmp_path: Path):
    record = build_branch_capsule_record(
        root=tmp_path,
        context_instance_id="ctx_scope_001",
        branch_id="branch_scope_001",
        agent_tag="codex",
        conversation_tag="scope",
        write_scope=["ION/04_packages/kernel/ion_agent_branch_capsule.py"],
    )

    result = material_work_preflight(
        tmp_path,
        branch_record=record,
        requested_write_scope=[
            "ION/04_packages/kernel/ion_agent_branch_capsule.py",
            "ION/05_context/current/codex_solo/MINI.md",
            "ION/docs/out_of_scope.md",
        ],
        active_claims=[],
    )

    codes = {item["code"] for item in result["findings"]}
    assert result["ok"] is False
    assert "requested_write_scope_shared_context_surface_forbidden" in codes
    assert "requested_write_scope_not_declared_in_branch" in codes


def test_settlement_intake_requires_branch_identity_guard_and_workload_diff(tmp_path: Path):
    bad = settlement_intake_preflight(tmp_path, packet={"packet_id": "SETTLE_BAD"})

    assert bad["ok"] is False
    codes = {item["code"] for item in bad["findings"]}
    assert "missing_workload_diff" in codes
    assert "missing_guard_evidence" in codes
    assert "missing_branch_identity_field" in codes


def test_settlement_request_passes_intake_when_guard_ready(tmp_path: Path):
    record = build_branch_capsule_record(
        root=tmp_path,
        context_instance_id="ctx_settle_001",
        branch_id="branch_settle_001",
        agent_tag="codex",
        conversation_tag="settle",
        write_scope=["ION/tests/test_kernel_ion_agent_branch_capsule.py"],
    )
    guard = validate_branch_record(tmp_path, record)
    packet = build_settlement_request(
        tmp_path,
        record,
        workload_diff=["ION/tests/test_kernel_ion_agent_branch_capsule.py"],
        guard_evidence=guard,
        result_summary="candidate helper test",
    )

    result = settlement_intake_preflight(tmp_path, packet=packet)

    assert result["ok"] is True
    assert result["verdict"] == READY_VERDICT
    assert packet["settlement_request"]["direct_accepted_state_merge"] is False


def test_reconciliation_detects_registry_row_without_record(tmp_path: Path):
    registry_path = tmp_path / "ION/05_context/current/agent_context_branches/BRANCH_CAPSULE_REGISTRY_V0_1.json"
    registry_path.parent.mkdir(parents=True)
    registry_path.write_text(
        json.dumps(
            {
                "schema": "ion.agent_branch_capsule.registry.v1",
                "registered_branches": [
                    {
                        "branch_id": "branch_missing",
                        "context_instance_id": "ctx_missing",
                        "agent_tag": "codex",
                        "conversation_tag": "missing",
                        "status": "BRANCH_ACTIVE_CANDIDATE",
                        "write_scope": ["ION/docs/missing.md"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = reconcile_branch_registry(tmp_path)

    assert result["ok"] is False
    assert any(item["code"] == "registry_row_missing_branch_record" for item in result["findings"])


def test_create_branch_capsule_writes_candidate_branch_files(tmp_path: Path):
    result = create_branch_capsule(
        tmp_path,
        context_instance_id="ctx_create_001",
        branch_id="branch_create_001",
        agent_tag="codex",
        conversation_tag="create",
        write_scope=["ION/docs/create.md"],
    )

    assert result["ok"] is True
    record_path = tmp_path / result["paths"]["record_path"]
    status_path = tmp_path / result["paths"]["status_path"]
    capsule_path = tmp_path / result["paths"]["capsule_path"]
    assert record_path.exists()
    assert status_path.exists()
    assert capsule_path.exists()
    assert "candidate branch context only" in capsule_path.read_text(encoding="utf-8")
