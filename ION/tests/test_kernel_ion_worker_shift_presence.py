from __future__ import annotations

import json
import subprocess
from pathlib import Path

from kernel.ion_worker_shift_presence import (
    ACTIVE_BOARD_PATH,
    BOARD_SCHEMA_ID,
    IDENTITY_BOUND_TRUE_NAME,
    IDENTITY_UNBOUND_WORKER_ID,
    WRITE_INTENT_CONFIRMATION,
    heartbeat,
    heartbeat_edit_lease,
    classify_live_unbound_leases,
    claim_work_lease,
    classify_stale_workers,
    detect_lease_conflicts,
    generate_worker_id,
    load_shift_board,
    release_edit_lease,
    release_work_lease,
    require_active_edit_lease,
    require_active_write_intent_lease,
    request_edit_lease,
    request_write_intent_lease,
    request_handoff,
    request_operator_override,
    sign_off,
    sign_on,
    summarize_shift_board,
    write_heartbeat,
    write_signoff_receipt,
    write_signon_receipt,
    write_shift_board,
)


def _root(tmp_path: Path) -> Path:
    root = tmp_path / "ion-root"
    (root / "ION").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")
    return root


def _ai_movement_envelope(root: Path) -> dict[str, object]:
    return {
        "ai_movement_root_envelope": {
            "schema_id": "ion.ai_movement_root_envelope.v1",
            "actual_cwd": str(root),
            "actual_realpath": str(root),
            "expected_cwd": str(root),
            "expected_realpath": str(root),
            "target_project_root": str(root),
            "target_content_root": str(root / "ION"),
            "movement_class": "ION_KERNEL_CONTROL_MOVEMENT",
            "domain_context_package": "ION/05_context/current/system_cartography",
            "active_template": "ION/07_templates/ai_movement/ION_AI_MOVEMENT_ROOT_ENVELOPE.template.yaml",
            "planned_writes": ["ION/05_context/current/reports/example.md"],
            "settlement_target": "ION/05_context/current/reports/example_ledger.json",
            "receipt_paths": [
                "ION/05_context/current/worker_shift/signons/**",
                "ION/05_context/current/worker_shift/leases/**",
                "ION/05_context/current/worker_shift/signoffs/**",
            ],
        }
    }


def _ai_movement_gate_decision(*, accepted: bool = True) -> dict[str, object]:
    blockers = [] if accepted else [{"code": "WRONG_ROOT_CWD", "detail": "actual cwd mismatch"}]
    return {
        "schema_id": "ion.ai_movement_gate_decision.v1",
        "accepted": accepted,
        "verdict": "ACCEPTED" if accepted else "BLOCKED",
        "movement_class": "ION_KERNEL_CONTROL_MOVEMENT",
        "target_root_id": "active_ion_control",
        "target_root_class": "ACTIVE_ION_CONTROL_ROOT",
        "target_root_relation": "active_ion_control_root",
        "blockers": blockers,
        "warnings": [],
        "settlement_target": "ION/05_context/current/reports/example_ledger.json",
    }


def test_generate_worker_identity_uses_callsign_and_authority_boundary(tmp_path: Path) -> None:
    root = _root(tmp_path)

    identity = generate_worker_id(
        carrier_type="codex_cli",
        active_root=root,
        role_hint="Mason",
        domain_hint="Worker-Shift",
        model="gpt-5.5",
        now="2026-05-15T15:00:00+00:00",
        ordinal=7,
    )

    assert identity["worker_id"] == "codex_cli:ion-root:20260515:007"
    assert identity["display_callsign"] == "Codex-007 / Mason / Worker-Shift"
    assert identity["authority"]["production_authority"] is False
    assert identity["authority"]["live_execution_authority"] is False


def test_signon_heartbeat_and_signoff_update_board_and_receipts(tmp_path: Path) -> None:
    root = _root(tmp_path)

    signon = write_signon_receipt(
        root=root,
        carrier_type="codex_cli",
        role_hint="Mason",
        domain_hint="Worker-Shift",
        packet_id="PCKT-ION-WORKER-SHIFT-PRESENCE-V0_1",
        current_objective="implement worker shift",
        likely_touched_paths=["ION/04_packages/kernel/ion_worker_shift_presence.py"],
        now="2026-05-15T15:00:00+00:00",
    )

    board = load_shift_board(root)
    worker_id = signon["receipt"]["worker_id"]
    shift_id = signon["receipt"]["shift_id"]
    assert (root / signon["receipt_path"]).is_file()
    assert board["schema_id"] == BOARD_SCHEMA_ID
    assert board["active_shifts"][0]["worker_id"] == worker_id
    assert board["active_shifts"][0]["executor_lifecycle_state"] == "ACTIVE"
    assert board["active_shifts"][0]["likely_touched_paths"] == [
        "ION/04_packages/kernel/ion_worker_shift_presence.py"
    ]

    heartbeat = write_heartbeat(
        root=root,
        worker_id=worker_id,
        shift_id=shift_id,
        now="2026-05-15T15:10:00+00:00",
    )
    assert (root / heartbeat["receipt_path"]).is_file()
    assert load_shift_board(root)["active_shifts"][0]["last_heartbeat_at"] == "2026-05-15T15:10:00+00:00"

    signoff = write_signoff_receipt(
        root=root,
        worker_id=worker_id,
        shift_id=shift_id,
        work_done="implemented helper",
        touched_paths=["ION/04_packages/kernel/ion_worker_shift_presence.py"],
        validation=["focused tests passed"],
        now="2026-05-15T15:20:00+00:00",
    )

    final_board = load_shift_board(root)
    assert (root / signoff["receipt_path"]).is_file()
    assert signoff["receipt"]["touched_paths"] == ["ION/04_packages/kernel/ion_worker_shift_presence.py"]
    assert final_board["active_shifts"] == []
    assert final_board["recent_signoffs"][0]["worker_id"] == worker_id
    assert final_board["recent_signoffs"][0]["status"] == "RETURNED"
    assert (root / ACTIVE_BOARD_PATH).is_file()


def test_lease_conflicts_hard_block_overlapping_write_path_collision(tmp_path: Path) -> None:
    root = _root(tmp_path)
    first = claim_work_lease(
        root=root,
        worker_id="codex_cli:ion-root:20260515:001",
        lease_type="write_intent",
        paths=["ION/04_packages/kernel/ion_worker_shift_presence.py"],
        now="2026-05-15T15:00:00+00:00",
    )

    advisory = claim_work_lease(
        root=root,
        worker_id="codex_cli:ion-root:20260515:002",
        lease_type="write_intent",
        paths=["ION/04_packages/kernel/ion_worker_shift_presence.py"],
        now="2026-05-15T15:01:00+00:00",
    )

    assert first["receipt"]["result"] == "ACTIVE"
    assert advisory["receipt"]["result"] == "BLOCKED_HARD_CONFLICT"
    assert advisory["receipt"]["lease"]["paths"] == ["ION/04_packages/kernel/ion_worker_shift_presence.py"]
    assert advisory["receipt"]["conflicts"]["has_advisory_conflict"] is False
    assert advisory["receipt"]["conflicts"]["has_hard_conflict"] is True

    hard = claim_work_lease(
        root=root,
        worker_id="codex_cli:ion-root:20260515:003",
        lease_type="exclusive_write",
        paths=["ION/04_packages/kernel/ion_worker_shift_presence.py"],
        now="2026-05-15T15:02:00+00:00",
    )

    assert hard["receipt"]["result"] == "BLOCKED_HARD_CONFLICT"
    assert hard["receipt"]["conflicts"]["has_hard_conflict"] is True
    assert len(load_shift_board(root)["active_leases"]) == 1

    release = release_work_lease(
        root=root,
        worker_id="codex_cli:ion-root:20260515:001",
        now="2026-05-15T15:03:00+00:00",
    )
    assert release["receipt"]["result"] == "RELEASED"
    assert len(load_shift_board(root)["active_leases"]) == 0


def test_detect_lease_conflicts_accepts_plain_board_data() -> None:
    result = detect_lease_conflicts(
        {
            "worker_id": "w2",
            "lease_type": "read_interest",
            "paths": ["ION/02_architecture"],
        },
        board={
            "active_leases": [
                {
                    "lease_id": "lease-1",
                    "worker_id": "w1",
                    "lease_type": "exclusive_write",
                    "paths": ["ION/02_architecture/ION_WORKER_SHIFT_AND_PRESENCE_PROTOCOL.md"],
                    "status": "ACTIVE",
                }
            ]
        },
    )

    assert result["has_hard_conflict"] is True
    assert result["policy"] == "exclusive_write_or_same_target_write_blocks_overlap"


def test_edit_lease_wrappers_request_heartbeat_and_release(tmp_path: Path) -> None:
    root = _root(tmp_path)

    requested = request_edit_lease(
        root,
        {
            "agent_id": "codex_cli:ion-root:20260515:010",
            "lease_id": "lease-domain-weaver-edit",
            "target_paths": ["ION/04_packages/kernel/ion_domain_weaver.py"],
            "objective": "domain weaver bounded edit",
            "target_route_id": "project_workbench.patch_apply",
        },
    )
    heartbeat_result = heartbeat_edit_lease(
        root,
        {
            "agent_id": "codex_cli:ion-root:20260515:010",
            "lease_id": "lease-domain-weaver-edit",
        },
    )
    released = release_edit_lease(
        root,
        {
            "agent_id": "codex_cli:ion-root:20260515:010",
            "lease_id": "lease-domain-weaver-edit",
        },
    )

    assert requested["ok"] is True
    assert requested["active_lease"]["lease_type"] == "exclusive_write"
    assert requested["active_lease"]["lease_class"] == "edit_lease"
    assert heartbeat_result["ok"] is True
    assert heartbeat_result["active_lease"]["last_heartbeat_at"]
    assert released["ok"] is True
    assert load_shift_board(root)["active_leases"] == []


def test_request_edit_lease_accepts_lease_type_or_lease_mode(tmp_path: Path) -> None:
    root = _root(tmp_path)
    export_root = root.parent / "ION_EXPORTS_LOCAL"

    artifact_requested = request_edit_lease(
        root,
        {
            "agent_id": "codex_cli:ion-root:20260515:012",
            "lease_id": "lease-artifact-mode",
            "target_paths": [export_root],
            "lease_mode": "artifact",
        },
    )
    exclusive_requested = request_edit_lease(
        root,
        {
            "agent_id": "codex_cli:ion-root:20260515:013",
            "lease_id": "lease-exclusive-type",
            "target_paths": ["ION/04_packages/kernel/ion_worker_shift_presence.py"],
            "lease_type": "exclusive_write",
        },
    )
    rejected = request_edit_lease(
        root,
        {
            "agent_id": "codex_cli:ion-root:20260515:014",
            "lease_id": "lease-read-not-edit",
            "target_paths": ["ION/04_packages/kernel/ion_worker_shift_presence.py"],
            "lease_mode": "read",
        },
    )

    assert artifact_requested["ok"] is True
    assert artifact_requested["active_lease"]["mode"] == "artifact"
    assert artifact_requested["active_lease"]["lease_type"] == "artifact"
    assert exclusive_requested["ok"] is True
    assert exclusive_requested["active_lease"]["mode"] == "exclusive_write"
    assert exclusive_requested["active_lease"]["lease_type"] == "exclusive_write"
    assert rejected == {
        "ok": False,
        "finding": "unsupported_lease_mode",
        "provided_lease_mode": "read",
        "supported_lease_modes": ["artifact", "exclusive_write"],
        "authority": {
            "accepted_state_authority": False,
            "live_execution_authority": False,
            "production_authority": False,
            "secrets_authority": False,
        },
    }


def test_shared_edit_lease_gate_validates_fresh_target_coverage(tmp_path: Path) -> None:
    root = _root(tmp_path)
    sign_on(
        "codex_cli:ion-root:20260515:011",
        "codex_cli",
        "worker_shift_presence_v0_1",
        ["ION/04_packages/kernel/ion_domain_weaver.py"],
        root=root,
        display_callsign="Codex 011",
        now="2026-05-15T15:00:00+00:00",
    )
    request_edit_lease(
        root,
        {
            "agent_id": "codex_cli:ion-root:20260515:011",
            "lease_id": "lease-shared-gate",
            "target_paths": ["ION/04_packages/kernel/ion_domain_weaver.py"],
        },
    )

    gate = require_active_edit_lease(
        root,
        agent_id="codex_cli:ion-root:20260515:011",
        lease_id="lease-shared-gate",
        target_files=[
            {
                "path": "ION/04_packages/kernel/ion_domain_weaver.py",
                "lease_path_candidates": ["ION/04_packages/kernel/ion_domain_weaver.py"],
            }
        ],
    )
    wrong_path = require_active_edit_lease(
        root,
        agent_id="codex_cli:ion-root:20260515:011",
        lease_id="lease-shared-gate",
        target_files=[{"path": "ION/04_packages/kernel/other.py", "lease_path_candidates": ["ION/04_packages/kernel/other.py"]}],
    )

    assert gate["ok"] is True
    assert gate["covered_target_count"] == 1
    assert wrong_path["ok"] is False
    assert "lease_missing_target_coverage" in wrong_path["blockers"]


def test_shared_edit_lease_gate_rejects_unbound_identity_status_variants(tmp_path: Path) -> None:
    root = _root(tmp_path)
    request_edit_lease(
        root,
        {
            "agent_id": "codex_cli:ion-root:20260515:099",
            "lease_id": "lease-unbound-gate",
            "target_paths": ["ION/04_packages/kernel/ion_domain_weaver.py"],
        },
    )

    base_gate = require_active_edit_lease(
        root,
        agent_id="codex_cli:ion-root:20260515:099",
        lease_id="lease-unbound-gate",
        target_files=["ION/04_packages/kernel/ion_domain_weaver.py"],
    )
    assert base_gate["ok"] is False
    assert "lease_identity_binding_blocked" in base_gate["blockers"]
    assert base_gate["identity_blocked"] is True

    board = load_shift_board(root)
    board["active_leases"][0]["identity_binding_status"] = "unbound-worker-id"
    write_shift_board(board, root)
    hyphen_gate = require_active_edit_lease(
        root,
        agent_id="codex_cli:ion-root:20260515:099",
        lease_id="lease-unbound-gate",
        target_files=["ION/04_packages/kernel/ion_domain_weaver.py"],
    )
    assert hyphen_gate["ok"] is False
    assert "lease_identity_binding_blocked" in hyphen_gate["blockers"]

    board = load_shift_board(root)
    board["active_leases"][0]["identity_binding_status"] = "UNBOUND WORKER ID"
    write_shift_board(board, root)
    spaced_gate = require_active_edit_lease(
        root,
        agent_id="codex_cli:ion-root:20260515:099",
        lease_id="lease-unbound-gate",
        target_files=["ION/04_packages/kernel/ion_domain_weaver.py"],
    )
    assert spaced_gate["ok"] is False
    assert "lease_identity_binding_blocked" in spaced_gate["blockers"]


def test_write_intent_lease_issues_and_validates_for_bound_mutation(tmp_path: Path) -> None:
    root = _root(tmp_path)
    true_name = "codex_worker_shift_write_intent_bound_actor"
    target_path = "ION/04_packages/kernel/ion_worker_shift_presence.py"
    sign_on(
        true_name,
        "codex",
        "worker_shift_write_intent",
        [target_path],
        root=root,
        now="2026-06-04T01:00:00+00:00",
    )

    requested = request_write_intent_lease(
        root,
        {
            "agent_id": true_name,
            "lease_id": "lease-write-intent-ok",
            "target_paths": [target_path],
            "root_scope": "active_root",
            "active_root": str(root),
            "target_route_id": "worker_shift.apply_candidate_patch",
            "mutation_context": "active_root_candidate_patch",
            "idempotency_key": "write-intent-001",
            "confirmation": WRITE_INTENT_CONFIRMATION,
        },
    )
    gate = require_active_write_intent_lease(
        root,
        agent_id=true_name,
        lease_id="lease-write-intent-ok",
        target_files=[target_path],
        root_scope="active_root",
        target_route_id="worker_shift.apply_candidate_patch",
        mutation_context="active_root_candidate_patch",
        idempotency_key="write-intent-001",
        confirmation=WRITE_INTENT_CONFIRMATION,
    )

    assert requested["ok"] is True
    assert requested["active_lease"]["lease_type"] == "write"
    assert requested["active_lease"]["lease_class"] == "write_intent_lease"
    assert requested["active_lease"]["active_root"] == str(root.resolve(strict=False))
    assert gate["ok"] is True
    assert gate["lease_type"] == "write"
    assert gate["covered_target_count"] == 1


def test_write_intent_lease_rejects_unbound_preview_and_missing_confirmation(tmp_path: Path) -> None:
    root = _root(tmp_path)
    target_path = "ION/04_packages/kernel/ion_worker_shift_presence.py"

    unbound = request_write_intent_lease(
        root,
        {
            "agent_id": "codex_worker_shift_write_intent_unbound",
            "lease_id": "lease-write-intent-unbound",
            "target_paths": [target_path],
            "root_scope": "active_root",
            "target_route_id": "worker_shift.apply_candidate_patch",
            "mutation_context": "active_root_candidate_patch",
            "idempotency_key": "write-intent-unbound",
            "confirmation": WRITE_INTENT_CONFIRMATION,
        },
    )
    assert unbound["ok"] is False
    assert unbound["finding"] == "bound_active_signon_required"

    true_name = "codex_worker_shift_write_intent_preview_guard"
    sign_on(
        true_name,
        "codex",
        "worker_shift_write_intent",
        [target_path],
        root=root,
        now="2026-06-04T01:05:00+00:00",
    )
    preview = request_write_intent_lease(
        root,
        {
            "agent_id": true_name,
            "lease_id": "lease-write-intent-preview",
            "target_paths": [target_path],
            "root_scope": "active_root",
            "target_route_id": "parallel_plan_preview",
            "mutation_context": "active_root_candidate_patch",
            "idempotency_key": "write-intent-preview",
            "confirmation": WRITE_INTENT_CONFIRMATION,
        },
    )
    missing_confirmation = request_write_intent_lease(
        root,
        {
            "agent_id": true_name,
            "lease_id": "lease-write-intent-missing-confirmation",
            "target_paths": [target_path],
            "root_scope": "active_root",
            "target_route_id": "worker_shift.apply_candidate_patch",
            "mutation_context": "active_root_candidate_patch",
            "idempotency_key": "write-intent-missing-confirmation",
        },
    )

    assert preview["ok"] is False
    assert preview["finding"] == "mutating_route_required"
    assert missing_confirmation["ok"] is False
    assert missing_confirmation["finding"] == "write_intent_confirmation_required"


def test_write_intent_validation_rejects_path_root_stale_and_weaker_type(tmp_path: Path) -> None:
    root = _root(tmp_path)
    true_name = "codex_worker_shift_write_intent_validation"
    target_path = "ION/04_packages/kernel/ion_worker_shift_presence.py"
    sign_on(
        true_name,
        "codex",
        "worker_shift_write_intent",
        [target_path],
        root=root,
        now="2026-06-04T01:10:00+00:00",
    )
    request_write_intent_lease(
        root,
        {
            "agent_id": true_name,
            "lease_id": "lease-write-intent-validation",
            "target_paths": [target_path],
            "root_scope": "active_root",
            "target_route_id": "worker_shift.apply_candidate_patch",
            "mutation_context": "active_root_candidate_patch",
            "idempotency_key": "write-intent-validation",
            "confirmation": WRITE_INTENT_CONFIRMATION,
        },
    )

    wrong_path = require_active_write_intent_lease(
        root,
        agent_id=true_name,
        lease_id="lease-write-intent-validation",
        target_files=["ION/04_packages/kernel/other.py"],
    )
    assert wrong_path["ok"] is False
    assert "lease_missing_target_coverage" in wrong_path["blockers"]

    board = load_shift_board(root)
    board["active_leases"][0]["active_root"] = str(root.parent / "other-root")
    write_shift_board(board, root)
    wrong_root = require_active_write_intent_lease(
        root,
        agent_id=true_name,
        lease_id="lease-write-intent-validation",
        target_files=[target_path],
    )
    assert wrong_root["ok"] is False
    assert "lease_root_mismatch" in wrong_root["blockers"]

    board = load_shift_board(root)
    board["active_leases"][0]["active_root"] = str(root)
    board["active_leases"][0]["last_heartbeat_at"] = "2020-01-01T00:00:00+00:00"
    write_shift_board(board, root)
    stale = require_active_write_intent_lease(
        root,
        agent_id=true_name,
        lease_id="lease-write-intent-validation",
        target_files=[target_path],
    )
    assert stale["ok"] is False
    assert "lease_not_fresh" in stale["blockers"]

    weaker = claim_work_lease(
        true_name,
        "lease-write-intent-read-is-weaker",
        ["ION/tests/test_kernel_ion_worker_shift_presence.py"],
        "read",
        root=root,
    )
    assert weaker["receipt"]["result"] == "ACTIVE"
    weaker_gate = require_active_write_intent_lease(
        root,
        agent_id=true_name,
        lease_id="lease-write-intent-read-is-weaker",
        target_files=["ION/tests/test_kernel_ion_worker_shift_presence.py"],
    )
    assert weaker_gate["ok"] is False
    assert "lease_type_mismatch" in weaker_gate["blockers"]


def test_live_unbound_lease_settlement_records_receipt_without_deleting_lease(tmp_path: Path) -> None:
    root = _root(tmp_path)
    board = load_shift_board(root)
    board["active_leases"] = [
        {
            "lease_id": "lease-live-unbound",
            "worker_id": "codex_cli:unbound-live-worker",
            "lease_type": "exclusive_write",
            "mode": "exclusive_write",
            "status": "ACTIVE",
            "identity_binding_status": IDENTITY_UNBOUND_WORKER_ID,
            "worker_id_source": "generated_fallback",
            "paths": ["ION/04_packages/kernel/ion_worker_shift_presence.py"],
            "raw_paths": ["ION/04_packages/kernel/ion_worker_shift_presence.py"],
        }
    ]
    write_shift_board(board, root)

    settlement = classify_live_unbound_leases(
        root=root,
        now="2026-06-03T23:51:00+00:00",
        write_receipt=True,
        reason="riemann_live_unbound_lease_settlement",
    )
    updated_board = load_shift_board(root)

    assert settlement["ok"] is False
    assert settlement["result"] == "BLOCKED_LIVE_UNBOUND_LEASES"
    assert settlement["receipt_only"] is True
    assert settlement["no_silent_lease_deletion"] is True
    assert settlement["mutates_active_leases"] is False
    assert settlement["readiness_blocked"] is True
    assert settlement["operator_override_required"] is True
    assert settlement["authorized_release_required"] is True
    assert settlement["unbound_active_lease_count"] == 1
    assert settlement["unbound_active_exclusive_write_count"] == 1
    assert settlement["orphan_active_exclusive_write_count"] == 1
    assert settlement["unbound_active_leases"][0]["lease_id"] == "lease-live-unbound"
    orphan = settlement["unbound_active_leases"][0]["orphan_reconciliation"]
    assert orphan["classification"] == "ORPHAN_ACTIVE_EXCLUSIVE_WRITE_BLOCKED"
    assert orphan["reconcile_action"] == "classified_left_active_blocked"
    assert orphan["auto_release_allowed"] is False
    assert updated_board["active_leases"][0]["lease_id"] == "lease-live-unbound"
    assert updated_board["active_leases"][0]["identity_binding_status"] == IDENTITY_UNBOUND_WORKER_ID
    assert (root / settlement["receipt_path"]).is_file()
    assert updated_board["recent_receipts"][-1]["path"] == settlement["receipt_path"]


def test_worker_shift_summary_blocks_readiness_when_live_unbound_lease_exists(tmp_path: Path) -> None:
    root = _root(tmp_path)
    board = load_shift_board(root)
    board["active_leases"] = [
        {
            "lease_id": "lease-live-unbound-summary",
            "worker_id": "codex_cli:unbound-summary-worker",
            "lease_type": "exclusive_write",
            "mode": "exclusive_write",
            "status": "ACTIVE",
            "identity_binding_status": "UNBOUND WORKER ID",
            "paths": ["ION/04_packages/kernel/ion_worker_shift_presence.py"],
        }
    ]
    write_shift_board(board, root)

    summary = summarize_shift_board(root=root, now="2026-06-03T23:52:00+00:00")

    assert summary["unbound_active_lease_count"] == 1
    assert summary["unbound_active_exclusive_write_count"] == 1
    assert summary["orphan_active_exclusive_write_count"] == 1
    assert summary["readiness_blocked_by_unbound_leases"] is True
    assert summary["worker_shift_blockers"] == ["live_unbound_active_lease"]
    assert summary["live_unbound_lease_settlement"]["receipt_only"] is True
    assert summary["orphan_exclusive_write_leases"][0]["classification"] == "ORPHAN_ACTIVE_EXCLUSIVE_WRITE_BLOCKED"


def test_handoff_and_operator_override_are_explicit_candidate_receipts(tmp_path: Path) -> None:
    root = _root(tmp_path)
    source_worker = "codex_g4_1_worker_shift_handoff_source"
    target_worker = "codex_g4_1_worker_shift_handoff_target"
    target_path = "ION/04_packages/kernel/ion_domain_weaver.py"
    claim_work_lease(
        source_worker,
        "lease-a",
        [target_path],
        "exclusive_write",
        root=root,
    )

    handoff = request_handoff(
        root,
        {
            "actor_id": source_worker,
            "from_agent_id": source_worker,
            "to_agent_id": target_worker,
            "source_lease_id": "lease-a",
            "target_paths": [target_path],
            "root_scope": str(root),
            "reason": "handoff context for next shift",
            "summary": "handoff context",
            "confirmation": "ION_HANDOFF_REQUEST_CONFIRMED",
            "idempotency_key": "handoff-explicit-1",
        },
    )
    override = request_operator_override(
        root,
        {
            "actor_id": "operator:sev",
            "operator_id": "operator:sev",
            "lease_id": "lease-a",
            "target_paths": [target_path],
            "root_scope": str(root),
            "reason": "hard conflict requires operator review",
            "blocked_finding": "hard_conflict",
            "operator_proof_marker": "ION_OPERATOR_OVERRIDE_REQUESTED",
            "idempotency_key": "override-explicit-1",
        },
    )
    board = load_shift_board(root)

    assert handoff["ok"] is True
    assert handoff["authority_transfer"] is False
    assert handoff["lease_transfer_performed"] is False
    assert handoff["active_lease_mutated"] is False
    assert handoff["current_holder_id"] == source_worker
    assert handoff["target_holder_id"] == target_worker
    assert (root / handoff["receipt_path"]).is_file()
    assert override["ok"] is True
    assert override["override_granted"] is False
    assert override["candidate_request_only"] is True
    assert override["active_lease_mutated"] is False
    assert override["current_holder_id"] == source_worker
    assert (root / override["receipt_path"]).is_file()
    assert board["active_leases"][0]["lease_id"] == "lease-a"
    assert board["active_leases"][0]["worker_id"] == source_worker


def test_handoff_and_operator_override_reject_unsafe_request_shapes(tmp_path: Path) -> None:
    root = _root(tmp_path)
    source_worker = "codex_g4_1_worker_shift_handoff_source"
    target_path = "ION/04_packages/kernel/ion_domain_weaver.py"
    claim_work_lease(
        source_worker,
        "lease-a",
        [target_path],
        "exclusive_write",
        root=root,
    )

    missing_lease = request_handoff(
        root,
        {
            "actor_id": source_worker,
            "to_agent_id": "codex_g4_1_worker_shift_handoff_target",
            "lease_id": "lease-missing",
            "target_paths": [target_path],
            "root_scope": str(root),
            "reason": "handoff context",
            "confirmation": "ION_HANDOFF_REQUEST_CONFIRMED",
        },
    )
    blank_reason = request_handoff(
        root,
        {
            "actor_id": source_worker,
            "to_agent_id": "codex_g4_1_worker_shift_handoff_target",
            "lease_id": "lease-a",
            "target_paths": [target_path],
            "root_scope": str(root),
            "confirmation": "ION_HANDOFF_REQUEST_CONFIRMED",
        },
    )
    missing_coverage = request_handoff(
        root,
        {
            "actor_id": source_worker,
            "to_agent_id": "codex_g4_1_worker_shift_handoff_target",
            "lease_id": "lease-a",
            "target_paths": ["ION/04_packages/kernel/other.py"],
            "root_scope": str(root),
            "reason": "handoff context",
            "confirmation": "ION_HANDOFF_REQUEST_CONFIRMED",
        },
    )
    unbound_actor = request_handoff(
        root,
        {
            "actor_id": "codex_cli:generated-worker",
            "actor_identity_binding_status": IDENTITY_UNBOUND_WORKER_ID,
            "to_agent_id": "codex_g4_1_worker_shift_handoff_target",
            "lease_id": "lease-a",
            "target_paths": [target_path],
            "root_scope": str(root),
            "reason": "handoff context",
            "confirmation": "ION_HANDOFF_REQUEST_CONFIRMED",
        },
    )
    missing_operator_proof = request_operator_override(
        root,
        {
            "actor_id": "operator:sev",
            "lease_id": "lease-a",
            "target_paths": [target_path],
            "root_scope": str(root),
            "reason": "operator review requested",
            "blocked_finding": "hard_conflict",
        },
    )

    assert missing_lease["ok"] is False
    assert missing_lease["finding"] == "lease_reference_not_found"
    assert blank_reason["ok"] is False
    assert blank_reason["finding"] == "reason_required"
    assert missing_coverage["ok"] is False
    assert missing_coverage["finding"] == "missing_target_coverage"
    assert unbound_actor["ok"] is False
    assert unbound_actor["finding"] == "unbound_identity_rejected"
    assert missing_operator_proof["ok"] is False
    assert missing_operator_proof["finding"] == "operator_proof_marker_required"


def test_operator_override_preserves_live_unbound_lease_as_candidate_only(tmp_path: Path) -> None:
    root = _root(tmp_path)
    board = load_shift_board(root)
    board["active_leases"] = [
        {
            "lease_id": "lease-live-unbound",
            "worker_id": "codex_cli:unbound-live-worker",
            "lease_type": "exclusive_write",
            "mode": "exclusive_write",
            "status": "ACTIVE",
            "identity_binding_status": IDENTITY_UNBOUND_WORKER_ID,
            "worker_id_source": "generated_fallback",
            "paths": ["ION/04_packages/kernel/ion_worker_shift_presence.py"],
            "raw_paths": ["ION/04_packages/kernel/ion_worker_shift_presence.py"],
        }
    ]
    write_shift_board(board, root)

    override = request_operator_override(
        root,
        {
            "actor_id": "operator:sev",
            "operator_id": "operator:sev",
            "lease_id": "lease-live-unbound",
            "target_paths": ["ION/04_packages/kernel/ion_worker_shift_presence.py"],
            "root_scope": str(root),
            "reason": "live unbound lease requires explicit operator review",
            "blocked_finding": "live_unbound_active_lease",
            "operator_proof_marker": "ION_OPERATOR_OVERRIDE_REQUESTED",
        },
    )
    updated_board = load_shift_board(root)

    assert override["ok"] is True
    assert override["override_granted"] is False
    assert override["candidate_request_only"] is True
    assert override["target_lease_identity_blocked"] is True
    assert override["live_unbound_lease_preserved"] is True
    assert updated_board["active_leases"][0]["lease_id"] == "lease-live-unbound"
    assert updated_board["active_leases"][0]["identity_binding_status"] == IDENTITY_UNBOUND_WORKER_ID


def test_operator_override_release_requires_receipt_evidence_before_mutation(tmp_path: Path) -> None:
    root = _root(tmp_path)
    board = load_shift_board(root)
    board["active_leases"] = [
        {
            "lease_id": "lease-live-unbound",
            "worker_id": "codex_cli:unbound-live-worker",
            "lease_type": "exclusive_write",
            "mode": "exclusive_write",
            "status": "ACTIVE",
            "identity_binding_status": IDENTITY_UNBOUND_WORKER_ID,
            "worker_id_source": "generated_fallback",
            "paths": ["ION/04_packages/kernel/ion_action_mcp_branch_leaders.py"],
            "raw_paths": ["ION/04_packages/kernel/ion_action_mcp_branch_leaders.py"],
        }
    ]
    write_shift_board(board, root)

    override = request_operator_override(
        root,
        {
            "override_id": "override-missing-receipt-evidence",
            "actor_id": "operator:codex",
            "operator_id": "operator:codex",
            "lease_id": "lease-live-unbound",
            "target_paths": ["ION/04_packages/kernel/ion_action_mcp_branch_leaders.py"],
            "root_scope": str(root),
            "reason": "operator-approved orphan exclusive-write settlement",
            "blocked_finding": "ORPHAN_ACTIVE_EXCLUSIVE_WRITE_BLOCKED",
            "operator_proof_marker": "ION_OPERATOR_OVERRIDE_REQUESTED",
            "evidence": {
                "override_action": "release_orphan_unbound_lease",
                "operator_packet": "PCKT-WORKER-SHIFT-ORPHAN-LEASE-FINAL-CLEANUP-V0_1",
            },
            "idempotency_key": "override-missing-receipt-evidence",
        },
    )
    updated_board = load_shift_board(root)

    assert override["ok"] is True
    assert override["override_granted"] is False
    assert override["settlement_result"] == "BLOCKED_INCOMPLETE_OPERATOR_OVERRIDE_PROOF"
    assert override["operator_override_proof_complete"] is False
    assert override["operator_override_proof_missing"] == ["receipt_evidence"]
    assert override["candidate_request_only"] is True
    assert override["mutates_active_leases"] is False
    assert override["live_unbound_lease_preserved"] is True
    assert updated_board["active_leases"][0]["lease_id"] == "lease-live-unbound"


def test_operator_override_settles_classified_orphan_exclusive_write_lease(tmp_path: Path) -> None:
    root = _root(tmp_path)
    board = load_shift_board(root)
    board["active_leases"] = [
        {
            "lease_id": "lease-live-unbound",
            "worker_id": "codex_cli:unbound-live-worker",
            "lease_type": "exclusive_write",
            "mode": "exclusive_write",
            "status": "ACTIVE",
            "identity_binding_status": IDENTITY_UNBOUND_WORKER_ID,
            "worker_id_source": "generated_fallback",
            "paths": ["ION/04_packages/kernel/ion_action_mcp_branch_leaders.py"],
            "raw_paths": ["ION/04_packages/kernel/ion_action_mcp_branch_leaders.py"],
        }
    ]
    write_shift_board(board, root)

    override = request_operator_override(
        root,
        {
            "override_id": "override-settle-live-unbound",
            "actor_id": "operator:codex",
            "operator_id": "operator:codex",
            "lease_id": "lease-live-unbound",
            "target_paths": ["ION/04_packages/kernel/ion_action_mcp_branch_leaders.py"],
            "root_scope": str(root),
            "reason": "operator-approved orphan exclusive-write settlement",
            "blocked_finding": "ORPHAN_ACTIVE_EXCLUSIVE_WRITE_BLOCKED",
            "operator_proof_marker": "ION_OPERATOR_OVERRIDE_REQUESTED",
            "evidence": {
                "override_action": "release_orphan_unbound_lease",
                "operator_packet": "PCKT-WORKER-SHIFT-ORPHAN-LEASE-FINAL-CLEANUP-V0_1",
                "receipt_evidence": [
                    "ION/05_context/current/worker_shift/lease_settlements/classified-live-unbound.json"
                ],
            },
            "idempotency_key": "override-settle-live-unbound",
        },
    )

    assert override["ok"] is True
    assert override["override_granted"] is True
    assert override["settlement_result"] == "ORPHAN_ACTIVE_LEASE_RELEASED_BY_OPERATOR_OVERRIDE"
    assert override["released_lease_count"] == 1
    assert override["mutates_active_leases"] is True
    assert override["active_lease_mutated"] is True
    assert override["operator_override_proof_complete"] is True
    assert override["operator_override_proof_missing"] == []
    assert override["before_board_state_counts"]["active_lease_count"] == 1
    assert override["after_board_state_counts"]["active_lease_count"] == 0
    assert override["receipt_evidence_paths"] == [
        "ION/05_context/current/worker_shift/lease_settlements/classified-live-unbound.json"
    ]
    assert override["authority"]["accepted_state_authority"] is False
    assert (root / override["receipt_path"]).is_file()
    receipt = json.loads((root / override["receipt_path"]).read_text(encoding="utf-8"))
    assert receipt["reason"] == "operator-approved orphan exclusive-write settlement"
    assert receipt["changed_lease_id"] == "lease-live-unbound"
    assert receipt["changed_lease_before"]["status"] == "ACTIVE"
    assert receipt["changed_lease_after"]["status"] == "RELEASED_BY_OPERATOR_OVERRIDE"
    assert receipt["before_board_state_counts"]["active_lease_count"] == 1
    assert receipt["after_board_state_counts"]["active_lease_count"] == 0
    assert receipt["accepted_state_claimed"] is False
    assert receipt["materialization_performed"] is False
    assert receipt["registry_movement_performed"] is False
    assert load_shift_board(root)["active_leases"] == []
    post = override["post_settlement"]
    assert post["ok"] is True
    assert post["result"] == "NO_LIVE_UNBOUND_LEASES"
    assert (root / post["receipt_path"]).is_file()


def test_required_public_api_sign_on_heartbeat_and_sign_off(tmp_path: Path) -> None:
    root = _root(tmp_path)

    signed_on = sign_on(
        "codex-b",
        "codex_cli",
        "worker_shift_presence_v0_1",
        ["ION/04_packages/kernel/ion_worker_shift_presence.py"],
        root=root,
        display_callsign="Codex B",
        now="2026-05-17T15:00:00+00:00",
    )

    assert signed_on["receipt"]["worker_id"] == "codex-b"
    assert signed_on["receipt"]["current_objective"] == "worker_shift_presence_v0_1"
    assert signed_on["receipt"]["likely_touched_paths"] == ["ION/04_packages/kernel/ion_worker_shift_presence.py"]

    beat = heartbeat("codex-b", root=root, now="2026-05-17T15:05:00+00:00")
    assert beat["receipt"]["receipt_type"] == "heartbeat"
    assert load_shift_board(root)["active_shifts"][0]["last_heartbeat_at"] == "2026-05-17T15:05:00+00:00"

    signed_off = sign_off(
        "codex-b",
        {"summary": "candidate patch complete", "validation": ["focused tests passed"]},
        root=root,
        now="2026-05-17T15:10:00+00:00",
    )
    assert signed_off["receipt"]["work_done"] == "candidate patch complete"
    assert signed_off["receipt"]["validation"] == ["focused tests passed"]
    assert load_shift_board(root)["active_shifts"] == []


def test_worker_shift_receipts_record_ai_movement_gate_metadata(tmp_path: Path) -> None:
    root = _root(tmp_path)
    worker_id = "codex_workspace_ai_movement_gate_template_receipt_integration"
    envelope = _ai_movement_envelope(root)
    decision = _ai_movement_gate_decision()

    signed_on = sign_on(
        worker_id,
        "codex",
        "ai_movement_gate_template_receipt_integration",
        ["ION/04_packages/kernel/ion_worker_shift_presence.py"],
        root=root,
        ai_movement_envelope=envelope,
        ai_movement_gate_decision=decision,
        now="2026-05-18T19:00:00+00:00",
    )
    lease = claim_work_lease(
        worker_id,
        "lease-ai-movement-ok",
        ["ION/04_packages/kernel/ion_worker_shift_presence.py"],
        "write",
        root=root,
        ai_movement_envelope=envelope,
        ai_movement_gate_decision=decision,
        now="2026-05-18T19:01:00+00:00",
    )
    signed_off = sign_off(
        worker_id,
        {
            "summary": "done",
            "ai_movement_envelope": envelope,
            "ai_movement_gate_decision": decision,
        },
        root=root,
        now="2026-05-18T19:02:00+00:00",
    )

    signon_gate = signed_on["receipt"]["ai_movement"]["gate_decision"]
    lease_gate = lease["receipt"]["lease"]["ai_movement_gate"]
    signoff_gate = signed_off["receipt"]["ai_movement"]["gate_decision"]
    assert signon_gate["schema_id"] == "ion.ai_movement_gate_decision.v1"
    assert signon_gate["accepted"] is True
    assert signed_on["board"]["active_shifts"][0]["ai_movement_gate"]["verdict"] == "ACCEPTED"
    assert lease["receipt"]["result"] == "ACTIVE"
    assert lease_gate["target_root_id"] == "active_ion_control"
    assert signoff_gate["accepted"] is True
    assert signed_off["receipt"]["ai_movement"]["runner_integration_performed"] is False


def test_lease_rejects_blocked_ai_movement_gate_decision(tmp_path: Path) -> None:
    root = _root(tmp_path)
    worker_id = "codex_workspace_ai_movement_gate_template_receipt_integration"
    envelope = _ai_movement_envelope(root)
    decision = _ai_movement_gate_decision(accepted=False)

    sign_on(
        worker_id,
        "codex",
        "ai_movement_gate_template_receipt_integration",
        ["ION/04_packages/kernel/ion_worker_shift_presence.py"],
        root=root,
        now="2026-05-18T19:10:00+00:00",
    )
    rejected = claim_work_lease(
        worker_id,
        "lease-ai-movement-blocked",
        ["ION/04_packages/kernel/ion_worker_shift_presence.py"],
        "write",
        root=root,
        ai_movement_envelope=envelope,
        ai_movement_gate_decision=decision,
        now="2026-05-18T19:11:00+00:00",
    )

    assert rejected["receipt"]["result"] == "BLOCKED_AI_MOVEMENT_GATE"
    assert rejected["receipt"]["lease"]["block_reason_code"] == "AI_MOVEMENT_GATE_BLOCKED"
    assert rejected["receipt"]["ai_movement"]["gate_decision"]["blocker_codes"] == ["WRONG_ROOT_CWD"]
    assert load_shift_board(root)["active_leases"] == []


def test_required_lease_modes_non_overlap_and_conflict_rule(tmp_path: Path) -> None:
    root = _root(tmp_path)

    first = claim_work_lease(
        "worker-a",
        "lease-a",
        ["ION/04_packages/kernel/ion_worker_shift_presence.py"],
        "exclusive_write",
        root=root,
        now="2026-05-17T15:00:00+00:00",
    )
    assert first["receipt"]["result"] == "ACTIVE"
    assert first["receipt"]["lease"]["mode"] == "exclusive_write"

    non_overlap = claim_work_lease(
        "worker-b",
        "lease-b",
        ["ION/tests/test_kernel_ion_worker_shift_presence.py"],
        "write",
        root=root,
        now="2026-05-17T15:01:00+00:00",
    )
    assert non_overlap["receipt"]["result"] == "ACTIVE"
    assert non_overlap["receipt"]["conflicts"]["has_hard_conflict"] is False

    child_conflict = claim_work_lease(
        "worker-c",
        "lease-c",
        ["ION/04_packages/kernel"],
        "read",
        root=root,
        now="2026-05-17T15:02:00+00:00",
    )
    assert child_conflict["receipt"]["result"] == "BLOCKED_HARD_CONFLICT"
    assert child_conflict["receipt"]["conflicts"]["hard_conflicts"][0]["overlaps"] == [
        {
            "candidate_path": "ION/04_packages/kernel",
            "existing_path": "ION/04_packages/kernel/ion_worker_shift_presence.py",
        }
    ]

    release = release_work_lease("worker-a", "lease-a", root=root, now="2026-05-17T15:03:00+00:00")
    assert release["receipt"]["result"] == "RELEASED"

    read_a = claim_work_lease(
        "worker-d",
        "lease-d",
        ["ION/02_architecture/ION_WORKER_SHIFT_AND_PRESENCE_PROTOCOL.md"],
        "read",
        root=root,
        now="2026-05-17T15:04:00+00:00",
    )
    read_b = claim_work_lease(
        "worker-e",
        "lease-e",
        ["ION/02_architecture"],
        "read",
        root=root,
        now="2026-05-17T15:05:00+00:00",
    )
    assert read_a["receipt"]["result"] == "ACTIVE"
    assert read_b["receipt"]["result"] == "ACTIVE"
    assert read_b["receipt"]["conflicts"]["has_hard_conflict"] is False
    assert read_b["receipt"]["conflicts"]["has_advisory_conflict"] is False


def test_worker_shift_rejects_parent_relative_export_lease(tmp_path: Path) -> None:
    root = _root(tmp_path)

    result = claim_work_lease(
        "worker-f1",
        "lease-f1",
        ["../ION_EXPORTS_LOCAL"],
        "write",
        root=root,
        now="2026-05-17T16:00:00+00:00",
    )

    decision = result["receipt"]["path_authority_decisions"][0]
    assert result["receipt"]["result"] == "BLOCKED_PATH_AUTHORITY"
    assert decision["raw_path"] == "../ION_EXPORTS_LOCAL"
    assert decision["authorized"] is False
    assert decision["reason_code"] == "PARENT_SEGMENT_FORBIDDEN"
    assert load_shift_board(root)["active_leases"] == []


def test_worker_shift_rejects_legacy_home_export_lease(tmp_path: Path) -> None:
    root = _root(tmp_path)

    result = claim_work_lease(
        "worker-f2",
        "lease-f2",
        ["/home/sev/ION_EXPORTS_LOCAL"],
        "write",
        root=root,
        now="2026-05-17T16:01:00+00:00",
    )

    decision = result["receipt"]["path_authority_decisions"][0]
    assert result["receipt"]["result"] == "BLOCKED_PATH_AUTHORITY"
    assert decision["resolved_path"] == "/home/sev/ION_EXPORTS_LOCAL"
    assert decision["classification"] == "FORBIDDEN_ROOT"
    assert decision["reason_code"] == "FORBIDDEN_ROOT"
    assert load_shift_board(root)["active_leases"] == []


def test_worker_shift_accepts_workspace_export_only_for_artifact_lease(tmp_path: Path) -> None:
    root = _root(tmp_path)
    export_root = root.parent / "ION_EXPORTS_LOCAL"

    write_result = claim_work_lease(
        "worker-f3",
        "lease-f3-write",
        [export_root],
        "write",
        root=root,
        now="2026-05-17T16:02:00+00:00",
    )
    artifact_result = claim_work_lease(
        "worker-f3",
        "lease-f3-artifact",
        [export_root],
        "artifact",
        root=root,
        now="2026-05-17T16:03:00+00:00",
    )

    assert write_result["receipt"]["result"] == "BLOCKED_PATH_AUTHORITY"
    assert write_result["receipt"]["path_authority_decisions"][0]["reason_code"] == (
        "WORKSPACE_EXPORT_REQUIRES_ARTIFACT_LEASE"
    )
    assert artifact_result["receipt"]["result"] == "ACTIVE"
    assert artifact_result["receipt"]["lease"]["resolved_paths"] == [str(export_root.resolve(strict=False))]
    assert artifact_result["receipt"]["path_authority_decisions"][0]["classification"] == "WORKSPACE_EXPORT"
    assert len(load_shift_board(root)["active_leases"]) == 1


def test_worker_shift_normal_repo_report_lease_records_path_authority(tmp_path: Path) -> None:
    root = _root(tmp_path)

    result = claim_work_lease(
        "worker-f4",
        "lease-f4",
        ["ION/05_context/current/reports/WORKSPACE_BOUNDARY_G2_GUARD_INTEGRATION_REPORT.md"],
        "write",
        root=root,
        now="2026-05-17T16:04:00+00:00",
    )

    decision = result["receipt"]["path_authority_decisions"][0]
    assert result["receipt"]["result"] == "ACTIVE"
    assert result["receipt"]["path_authority"]["authorized"] is True
    assert decision["authorized"] is True
    assert decision["classification"] == "ION_CONTENT"
    assert decision["raw_path"] == "ION/05_context/current/reports/WORKSPACE_BOUNDARY_G2_GUARD_INTEGRATION_REPORT.md"


def test_signon_lease_signoff_preserve_declared_true_name(tmp_path: Path) -> None:
    root = _root(tmp_path)
    true_name = "codex_g4_1_worker_shift_true_name_receipts"
    paths = ["ION/04_packages/kernel/ion_worker_shift_presence.py"]

    signed_on = sign_on(
        true_name,
        "codex",
        "worker_shift_true_name_receipts",
        paths,
        root=root,
        now="2026-05-17T17:00:00+00:00",
    )
    lease = claim_work_lease(
        true_name,
        "lease-g4-1",
        paths,
        "write",
        root=root,
        now="2026-05-17T17:01:00+00:00",
    )
    summary = summarize_shift_board(root=root, now="2026-05-17T17:02:00+00:00")
    signed_off = sign_off(
        true_name,
        {"summary": "done"},
        root=root,
        now="2026-05-17T17:03:00+00:00",
    )

    assert signed_on["receipt"]["worker_id"] == true_name
    assert signed_on["receipt"]["declared_true_name"] == true_name
    assert signed_on["receipt"]["identity"]["identity_binding_status"] == IDENTITY_BOUND_TRUE_NAME
    assert lease["receipt"]["lease"]["worker_id"] == true_name
    assert lease["receipt"]["lease"]["declared_true_name"] == true_name
    assert lease["receipt"]["lease"]["identity_binding_status"] == IDENTITY_BOUND_TRUE_NAME
    assert summary["workers"][0]["worker_id"] == true_name
    assert summary["workers"][0]["declared_true_name"] == true_name
    assert summary["active_leases"][0]["worker_id"] == true_name
    assert signed_off["receipt"]["worker_id"] == true_name
    assert signed_off["receipt"]["declared_true_name"] == true_name
    assert signed_off["receipt"]["released_lease_ids"] == ["lease-g4-1"]


def test_lease_worker_id_mismatch_with_active_signon_is_rejected(tmp_path: Path) -> None:
    root = _root(tmp_path)
    true_name = "codex_g4_1_worker_shift_true_name_receipts"
    other_worker = "codex_g4_artifact_surface_guard"

    sign_on(
        true_name,
        "codex",
        "worker_shift_true_name_receipts",
        ["ION/04_packages/kernel/ion_worker_shift_presence.py"],
        root=root,
        now="2026-05-17T17:10:00+00:00",
    )
    rejected = claim_work_lease(
        other_worker,
        "lease-mismatch",
        ["ION/04_packages/kernel/ion_worker_shift_presence.py"],
        "write",
        root=root,
        now="2026-05-17T17:11:00+00:00",
    )

    assert rejected["receipt"]["result"] == "BLOCKED_WORKER_ID_MISMATCH"
    auth = rejected["receipt"]["worker_id_authorization"]
    assert auth["authorized"] is False
    assert auth["reason_code"] == "WORKER_ID_ACTIVE_SIGNON_MISMATCH"
    assert auth["active_worker_ids"] == [true_name]
    assert load_shift_board(root)["active_leases"] == []


def test_generated_worker_id_is_marked_unbound(tmp_path: Path) -> None:
    root = _root(tmp_path)

    signed_on = write_signon_receipt(
        root=root,
        carrier_type="codex_cli",
        role_hint="Mason",
        domain_hint="Worker-Shift",
        now="2026-05-17T17:20:00+00:00",
    )
    summary = summarize_shift_board(root=root, now="2026-05-17T17:21:00+00:00")

    assert signed_on["receipt"]["identity"]["identity_binding_status"] == IDENTITY_UNBOUND_WORKER_ID
    assert signed_on["receipt"]["identity"]["declared_true_name"] is None
    assert signed_on["receipt"]["identity"]["unbound_worker_id"] is True
    assert summary["workers"][0]["identity_binding_status"] == IDENTITY_UNBOUND_WORKER_ID


def test_board_summary_is_json_serializable(tmp_path: Path) -> None:
    root = _root(tmp_path)
    claim_work_lease(
        "worker-a",
        "lease-a",
        ["ION/02_architecture"],
        "read",
        root=root,
        now="2026-05-17T15:00:00+00:00",
    )

    summary = summarize_shift_board(root=root, now="2026-05-17T15:01:00+00:00")

    assert json.loads(json.dumps(summary))["active_leases"][0]["mode"] == "read"


def test_stale_classification_and_summary(tmp_path: Path) -> None:
    root = _root(tmp_path)
    signon = write_signon_receipt(
        root=root,
        carrier_type="chatgpt_browser",
        role_hint="LeadDev",
        domain_hint="ION-Actions",
        now="2026-05-15T12:00:00+00:00",
    )

    stale = classify_stale_workers(root=root, now="2026-05-15T13:00:00+00:00", write=True)
    summary = summarize_shift_board(root=root, now="2026-05-15T13:00:00+00:00")

    assert stale["stale_workers"][0]["worker_id"] == signon["receipt"]["worker_id"]
    assert stale["stale_workers"][0]["presence_classification"] == "STALE"
    assert stale["stale_workers"][0]["executor_lifecycle_state"] == "SUSPENDED"
    assert (root / stale["receipt_path"]).is_file()
    assert summary["active_worker_count"] == 1
    assert summary["stale_worker_count"] == 1
    assert summary["workers"][0]["display_callsign"].startswith("BrowserGPT-001")


def test_python_s_py_compile_has_no_third_party_imports() -> None:
    result = subprocess.run(
        [
            "python3",
            "-S",
            "-m",
            "py_compile",
            "ION/04_packages/kernel/ion_worker_shift_presence.py",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
