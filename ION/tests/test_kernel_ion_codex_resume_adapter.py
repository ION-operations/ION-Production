from __future__ import annotations

import json
from pathlib import Path

from kernel.ion_codex_resume_adapter import (
    build_bounded_resume_prompt,
    classify_transcript_ref,
    create_fork_side_route,
    evaluate_resume_lawfulness,
    load_codex_session_manifest,
    make_resume_receipt,
    register_codex_session_manifest,
)


TRUE_NAME = "codex_d1_codex_resume_adapter"
SESSION_ID = "019e370f-d72f-7012-a66f-f7a85f0a0475"
SESSION_PATH = "ION/04_packages/kernel/ion_codex_resume_adapter.py"


def _root(tmp_path: Path) -> Path:
    root = tmp_path / "ion-root"
    (root / "ION/05_context/current/codex_solo").mkdir(parents=True)
    (root / "ION/04_packages/kernel").mkdir(parents=True)
    (root / "ION/tests").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = \"ion-test\"\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")
    (root / "ION/05_context/current/codex_solo/CAPSULE.md").write_text("capsule v1\n", encoding="utf-8")
    (root / SESSION_PATH).write_text("# adapter placeholder\n", encoding="utf-8")
    return root


def _rank(**overrides: object) -> dict[str, object]:
    rank: dict[str, object] = {
        "rank_id": "R2_DOMAIN_WORKER",
        "context_level": "R2_DOMAIN_WORKER",
        "domain_scope": "carrier.codex_cli",
        "mutation_class": "candidate_patch",
        "settlement_power": "recommend_only",
    }
    rank.update(overrides)
    return rank


def _lease(**overrides: object) -> dict[str, object]:
    lease: dict[str, object] = {
        "lease_id": "lease-codex-d1",
        "worker_id": TRUE_NAME,
        "mode": "write",
        "paths": [SESSION_PATH],
        "status": "ACTIVE",
    }
    lease.update(overrides)
    return lease


def _manifest(root: Path, **overrides: object) -> dict[str, object]:
    params: dict[str, object] = {
        "codex_session_id": SESSION_ID,
        "worker_true_name": TRUE_NAME,
        "rank_vector": _rank(),
        "context_package_refs": ["ION/05_context/current/codex_solo/CAPSULE.md"],
        "status_verdict": "ION_STATUS_SINGLE_CARRIER_READY",
        "cwd": root,
        "ion_root": root,
        "leases": [_lease()],
        "required_lease_paths": [SESSION_PATH],
        "transcript_ref": ".codex/sessions/2026/05/17/session.jsonl",
        "root": root,
        "now": "2026-05-17T18:00:00+00:00",
    }
    params.update(overrides)
    return register_codex_session_manifest(**params)


def _allowed_decision(root: Path, manifest: dict[str, object]) -> dict[str, object]:
    return evaluate_resume_lawfulness(
        manifest,
        requested_session_id=SESSION_ID,
        current_rank_vector=_rank(),
        current_cwd=root,
        current_ion_root=root,
        requested_mode="write",
        root=root,
        now="2026-05-17T18:05:00+00:00",
    )


def test_explicit_session_id_resume_allowed_when_status_rank_lease_context_pass(tmp_path: Path) -> None:
    root = _root(tmp_path)
    manifest = _manifest(root, write=True)

    decision = _allowed_decision(root, manifest)
    receipt = make_resume_receipt(manifest, decision, root=root)
    loaded = load_codex_session_manifest(SESSION_ID, root=root)

    assert loaded is not None
    assert decision["decision"] == "ALLOW_RESUME"
    assert decision["resume_lawful"] is True
    assert decision["actual_resume_executed"] is False
    assert "worker_true_name: codex_d1_codex_resume_adapter" in decision["bounded_resume_prompt"]
    assert json.loads(json.dumps(receipt))["decision"]["ok"] is True
    assert receipt["authority"]["production_authority"] is False
    assert receipt["authority"]["live_execution_authority"] is False


def test_blind_latest_session_resume_is_blocked_by_default(tmp_path: Path) -> None:
    root = _root(tmp_path)
    manifest = _manifest(root)

    decision = evaluate_resume_lawfulness(
        manifest,
        use_last=True,
        current_rank_vector=_rank(),
        requested_mode="write",
        root=root,
    )

    assert decision["decision"] == "BLOCK_RESUME"
    assert any(rejection["reason"] == "BLIND_LAST_RESUME_BLOCKED" for rejection in decision["rejections"])
    assert any(rejection["reason"] == "EXPLICIT_SESSION_ID_REQUIRED" for rejection in decision["rejections"])


def test_expired_true_name_blocks_resume(tmp_path: Path) -> None:
    root = _root(tmp_path)
    manifest = _manifest(root, true_name_expires_at="2026-05-17T17:00:00+00:00")

    decision = evaluate_resume_lawfulness(
        manifest,
        requested_session_id=SESSION_ID,
        current_rank_vector=_rank(),
        requested_mode="write",
        root=root,
        now="2026-05-17T18:05:00+00:00",
    )

    assert decision["decision"] == "BLOCK_RESUME"
    assert any(rejection["reason"] == "TRUE_NAME_EXPIRED" for rejection in decision["rejections"])


def test_missing_write_lease_blocks_write_resume(tmp_path: Path) -> None:
    root = _root(tmp_path)
    manifest = _manifest(root, leases=[], required_lease_paths=[SESSION_PATH])

    decision = evaluate_resume_lawfulness(
        manifest,
        requested_session_id=SESSION_ID,
        current_rank_vector=_rank(),
        requested_mode="write",
        root=root,
    )

    assert decision["decision"] == "BLOCK_RESUME"
    rejection = next(item for item in decision["rejections"] if item["reason"] == "REQUIRED_WRITE_LEASE_MISSING")
    assert rejection["missing_paths"] == [SESSION_PATH]


def test_rank_drift_blocks_resume(tmp_path: Path) -> None:
    root = _root(tmp_path)
    manifest = _manifest(root)

    decision = evaluate_resume_lawfulness(
        manifest,
        requested_session_id=SESSION_ID,
        current_rank_vector=_rank(domain_scope="browser.chatgpt"),
        requested_mode="write",
        root=root,
    )

    assert decision["decision"] == "BLOCK_RESUME"
    assert any(rejection["reason"] == "RANK_DRIFT" for rejection in decision["rejections"])


def test_status_blocker_blocks_resume(tmp_path: Path) -> None:
    root = _root(tmp_path)
    manifest = _manifest(root)

    decision = evaluate_resume_lawfulness(
        manifest,
        requested_session_id=SESSION_ID,
        current_rank_vector=_rank(),
        current_status_verdict="ION_STATUS_TRUTH_BLOCKED",
        requested_mode="write",
        root=root,
    )

    assert decision["decision"] == "BLOCK_RESUME"
    assert any(rejection["reason"] == "STATUS_BLOCKED" for rejection in decision["rejections"])


def test_transcript_is_witness_not_state(tmp_path: Path) -> None:
    root = _root(tmp_path)
    manifest = _manifest(root)
    classified = classify_transcript_ref(".codex/sessions/native.jsonl")

    assert manifest["transcript"]["classification"] == "transcript_witness_not_state"
    assert manifest["transcript"]["state_authority"] is False
    assert classified["accepted_state_claim"] is False


def test_fork_side_route_creates_candidate_child_true_name_not_accepted_state(tmp_path: Path) -> None:
    root = _root(tmp_path)
    manifest = _manifest(root)

    route = create_fork_side_route(
        manifest,
        movement="codex_resume_adapter_side_route",
        now="2026-05-17T18:10:00+00:00",
    )

    assert route["parent_true_name"] == TRUE_NAME
    assert route["candidate_child_true_name"] == "codex_d2_codex_resume_adapter_side_route"
    assert route["accepted_state_claim"] is False
    assert route["authority"]["accepted_state_authority"] is False


def test_resume_cannot_grant_production_or_live_authority(tmp_path: Path) -> None:
    root = _root(tmp_path)
    manifest = _manifest(root)

    decision = evaluate_resume_lawfulness(
        manifest,
        requested_session_id=SESSION_ID,
        current_rank_vector=_rank(),
        requested_mode="write",
        requested_authority={"production_authority": True, "live_execution_authority": True},
        root=root,
    )

    assert decision["decision"] == "BLOCK_RESUME"
    assert any(
        rejection["reason"] == "RESUME_CANNOT_GRANT_PRODUCTION_OR_LIVE_AUTHORITY"
        for rejection in decision["rejections"]
    )
    assert decision["authority"]["production_authority"] is False
    assert decision["authority"]["live_execution_authority"] is False


def test_context_hash_drift_blocks_unapproved_resume(tmp_path: Path) -> None:
    root = _root(tmp_path)
    manifest = _manifest(root)
    (root / "ION/05_context/current/codex_solo/CAPSULE.md").write_text("capsule v2\n", encoding="utf-8")

    decision = evaluate_resume_lawfulness(
        manifest,
        requested_session_id=SESSION_ID,
        current_rank_vector=_rank(),
        requested_mode="write",
        root=root,
    )

    assert decision["decision"] == "BLOCK_RESUME"
    assert any(rejection["reason"] == "CONTEXT_HASH_DRIFT" for rejection in decision["rejections"])


def test_cwd_or_root_mismatch_blocks_resume(tmp_path: Path) -> None:
    root = _root(tmp_path)
    other_root = tmp_path / "other-root"
    other_root.mkdir()
    manifest = _manifest(root)

    decision = evaluate_resume_lawfulness(
        manifest,
        requested_session_id=SESSION_ID,
        current_rank_vector=_rank(),
        current_cwd=other_root,
        current_ion_root=root,
        requested_mode="write",
        root=root,
    )

    assert decision["decision"] == "BLOCK_RESUME"
    assert any(rejection["reason"] == "CWD_ROOT_MISMATCH" for rejection in decision["rejections"])


def test_bounded_prompt_keeps_authority_false(tmp_path: Path) -> None:
    root = _root(tmp_path)
    manifest = _manifest(root)

    prompt = build_bounded_resume_prompt(manifest)

    assert "production_authority: false" in prompt
    assert "live_execution_authority: false" in prompt
    assert "accepted_state_claim: false" in prompt
