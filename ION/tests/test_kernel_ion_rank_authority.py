from __future__ import annotations

from kernel.ion_rank_authority import (
    c1_settlement_requirement,
    classify_true_name_rank,
    produce_rank_signoff,
    rank_vector,
    required_signoff_rank,
    validate_parallel_fan_in,
    validate_rank_lifecycle,
    validate_ranked_signoff,
)


def _c1_proof() -> dict[str, object]:
    return {
        "candidate_output_ref": "ION/05_context/current/reports/WAVE_001_002_RECONCILIATION_REPORT.md",
        "evidence_refs": [
            "ION/05_context/current/reports/WAVE_001_002_RECONCILIATION_REPORT.md",
            "ION/05_context/current/reports/WAVE_001_002_RECONCILIATION_LEDGER.json",
            "ION/05_context/current/reports/WAVE_003_PLAN_ONLY.md",
        ],
        "validation_refs": ["read-only reconciliation report and ledger reviewed"],
    }


def test_c1_wave_reconcile_classifies_as_r3_branch_integrator_candidate() -> None:
    c1 = classify_true_name_rank("codex_c1_wave_reconcile")

    assert c1["rank_id"] == "R3_BRANCH_INTEGRATOR"
    assert c1["primary_domain"] == "context.wave"
    assert c1["mutation_class"] == "branch_reconciliation"
    assert c1["settlement_power"] == "recommend_branch_promotion_only"


def test_r3_branch_integrator_can_recommend_but_not_self_accept() -> None:
    c1 = classify_true_name_rank("codex_c1_wave_reconcile")

    result = validate_ranked_signoff(
        candidate_true_name="codex_c1_wave_reconcile",
        candidate_rank=c1,
        signer_true_name="codex_c1_wave_reconcile",
        signer_rank=c1,
        output_class="branch_reconciliation_promotion",
        proof=_c1_proof(),
    )

    assert result["ok"] is False
    assert {"reason": "SAME_TRUE_NAME_CANNOT_SIGN_OFF_OWN_CANDIDATE"} in result["rejections"]
    assert any(rejection["reason"] == "SIGNER_RANK_BELOW_REQUIRED" for rejection in result["rejections"])


def test_r3_wave_reconciliation_requires_r4_settlement_before_promotion() -> None:
    requirement = c1_settlement_requirement()

    assert requirement["candidate"]["rank_id"] == "R3_BRANCH_INTEGRATOR"
    assert requirement["required_signoff_rank"]["required_rank"] == "R4_SETTLEMENT_STEWARD"
    assert requirement["can_self_accept"] is False
    assert required_signoff_rank("branch_reconciliation_promotion")["promotion_requires"] == "R4_SETTLEMENT_STEWARD"


def test_r4_settlement_steward_can_sign_off_c1_style_return_with_evidence() -> None:
    c1 = classify_true_name_rank("codex_c1_wave_reconcile")
    steward = rank_vector("R4_SETTLEMENT_STEWARD")

    signoff = produce_rank_signoff(
        candidate_true_name="codex_c1_wave_reconcile",
        candidate_rank=c1,
        signer_true_name="codex_d4_wave_settlement",
        signer_rank=steward,
        output_class="branch_reconciliation_promotion",
        proof=_c1_proof(),
    )

    assert signoff["decision"] == "ACCEPT"
    assert signoff["validation"]["ok"] is True
    assert signoff["authority"]["production_authority"] is False
    assert signoff["authority"]["live_execution_authority"] is False


def test_r4_cannot_grant_production_or_live_authority() -> None:
    c1 = classify_true_name_rank("codex_c1_wave_reconcile")
    steward = rank_vector("R4_SETTLEMENT_STEWARD")

    result = validate_ranked_signoff(
        candidate_true_name="codex_c1_wave_reconcile",
        candidate_rank=c1,
        signer_true_name="codex_d4_wave_settlement",
        signer_rank=steward,
        output_class="branch_reconciliation_promotion",
        proof=_c1_proof(),
        requested_authority={"production_authority": True, "live_execution_authority": True},
    )

    assert result["ok"] is False
    assert any(
        rejection["reason"] == "RANK_CANNOT_GRANT_PRODUCTION_OR_LIVE_AUTHORITY"
        for rejection in result["rejections"]
    )


def test_r5_root_governor_action_requires_explicit_human_approval() -> None:
    candidate = rank_vector("R5_ROOT_GOVERNOR")
    governor = rank_vector("R5_ROOT_GOVERNOR")

    missing_gate = validate_ranked_signoff(
        candidate_true_name="codex_r5_root_profile",
        candidate_rank=candidate,
        signer_true_name="codex_r5_root_governor",
        signer_rank=governor,
        output_class="root_profile_change",
        proof={
            "candidate_output_ref": "ION/02_architecture/CANDIDATE_ROOT_PROFILE_CHANGE.md",
            "evidence_refs": ["ION/REPO_AUTHORITY.md"],
        },
    )

    assert missing_gate["ok"] is False
    assert any(
        rejection["reason"] == "ROOT_PROFILE_CHANGE_REQUIRES_EXPLICIT_HUMAN_APPROVAL"
        for rejection in missing_gate["rejections"]
    )

    with_gate = validate_ranked_signoff(
        candidate_true_name="codex_r5_root_profile",
        candidate_rank=candidate,
        signer_true_name="codex_r5_root_governor",
        signer_rank=governor,
        output_class="root_profile_change",
        proof={
            "candidate_output_ref": "ION/02_architecture/CANDIDATE_ROOT_PROFILE_CHANGE.md",
            "evidence_refs": ["ION/REPO_AUTHORITY.md"],
            "human_approval_ref": "operator:explicit-root-profile-approval",
        },
    )

    assert with_gate["ok"] is True


def test_missing_proof_burden_blocks_signoff() -> None:
    c1 = classify_true_name_rank("codex_c1_wave_reconcile")

    result = validate_ranked_signoff(
        candidate_true_name="codex_c1_wave_reconcile",
        candidate_rank=c1,
        signer_true_name="codex_d4_wave_settlement",
        signer_rank=rank_vector("R4_SETTLEMENT_STEWARD"),
        output_class="branch_reconciliation_promotion",
        proof={"candidate_output_ref": "ION/05_context/current/reports/WAVE_001_002_RECONCILIATION_REPORT.md"},
    )

    assert result["ok"] is False
    assert any(rejection["reason"] == "MISSING_PROOF_BURDEN" for rejection in result["rejections"])


def test_same_true_name_cannot_sign_off_own_candidate_even_at_required_rank() -> None:
    steward = rank_vector("R4_SETTLEMENT_STEWARD")

    result = validate_ranked_signoff(
        candidate_true_name="codex_d4_wave_settlement",
        candidate_rank=steward,
        signer_true_name="codex_d4_wave_settlement",
        signer_rank=steward,
        output_class="branch_reconciliation_promotion",
        proof=_c1_proof(),
    )

    assert result["ok"] is False
    assert {"reason": "SAME_TRUE_NAME_CANNOT_SIGN_OFF_OWN_CANDIDATE"} in result["rejections"]


def test_rank_expires_with_true_name_or_worker_shift_lifecycle() -> None:
    c1 = classify_true_name_rank("codex_c1_wave_reconcile")

    expired_binding = validate_rank_lifecycle(c1, true_name_binding={"binding_status": "EXPIRED"})
    signed_off_shift = validate_rank_lifecycle(c1, worker_shift={"status": "RETURNED"})
    active = validate_rank_lifecycle(c1, true_name_binding={"binding_status": "ACTIVE"}, worker_shift={"status": "ACTIVE"})

    assert expired_binding["ok"] is False
    assert expired_binding["rejections"][0]["reason"] == "TRUE_NAME_BINDING_NOT_ACTIVE"
    assert signed_off_shift["ok"] is False
    assert signed_off_shift["rejections"][0]["reason"] == "WORKER_SHIFT_NOT_ACTIVE"
    assert active["ok"] is True


def test_lower_rank_parallel_workers_fan_in_through_higher_rank_signoff() -> None:
    children = [
        {"true_name": "codex_a1_local_patch", "rank_id": "R1_LOCAL_WORKER"},
        {"true_name": "codex_b2_domain_check", "rank_id": "R2_DOMAIN_WORKER"},
        {"true_name": "codex_c1_wave_reconcile", "rank_id": "R3_BRANCH_INTEGRATOR"},
    ]

    result = validate_parallel_fan_in(
        children,
        signer_rank=rank_vector("R4_SETTLEMENT_STEWARD"),
        output_class="branch_reconciliation_promotion",
        proof=_c1_proof(),
    )

    assert result["ok"] is True
    assert result["child_count"] == 3

    too_low = validate_parallel_fan_in(
        children,
        signer_rank=rank_vector("R2_DOMAIN_WORKER"),
        output_class="branch_reconciliation_promotion",
        proof=_c1_proof(),
    )

    assert too_low["ok"] is False
    assert any(rejection["reason"] == "SIGNER_RANK_BELOW_REQUIRED" for rejection in too_low["rejections"])
