from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from kernel.ion_carrier_control_proof import (
    CARRIER_CONTROL_PROOF_HEADING,
    evaluate_carrier_control_proof,
    evaluate_carrier_control_proof_file,
    write_receipt,
)

TURN_REL = "ION/05_context/current/ACTIVE_CARRIER_TURN_PACKET.json"
PLAN_REL = "ION/05_context/current/ACTIVE_ROLE_SPAWN_PLAN.json"
HOOK_REL = "ION/05_context/current/ACTIVE_CURSOR_HOOK_STATE.json"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def shell_root(tmp_path: Path) -> Path:
    root = tmp_path
    (root / "pyproject.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
    (root / "ION").mkdir(parents=True, exist_ok=True)
    (root / "ION" / "REPO_AUTHORITY.md").write_text("# authority\n", encoding="utf-8")

    ctx = root / "ION" / "05_context" / "current"
    ctx.mkdir(parents=True)

    objective = "test objective for carrier control proof"
    turn_packet = {
        "schema_id": "ion.carrier_turn_packet.v1",
        "objective": objective,
        "spawn_queue": [{"index": 1, "role": "steward"}],
    }
    spawn_plan = {
        "schema_id": "ion.role_spawn_plan.v1",
        "role_spawn_plan": [{"index": 1, "role": "steward", "spawn": True}],
    }
    hook_state = {
        "schema_id": "ion.cursor_hook_state.v1",
        "continue_verdict": "ION_CARRIER_CONTINUE_READY",
    }

    turn_path = ctx / "ACTIVE_CARRIER_TURN_PACKET.json"
    plan_path = ctx / "ACTIVE_ROLE_SPAWN_PLAN.json"
    hook_path = ctx / "ACTIVE_CURSOR_HOOK_STATE.json"

    turn_path.write_text(json.dumps(turn_packet, indent=2) + "\n", encoding="utf-8")
    plan_path.write_text(json.dumps(spawn_plan, indent=2) + "\n", encoding="utf-8")
    hook_path.write_text(json.dumps(hook_state, indent=2) + "\n", encoding="utf-8")
    return root


def _fixture_shas(shell_root: Path) -> dict[str, str]:
    ctx = shell_root / "ION" / "05_context" / "current"
    turn_path = ctx / "ACTIVE_CARRIER_TURN_PACKET.json"
    plan_path = ctx / "ACTIVE_ROLE_SPAWN_PLAN.json"
    hook_path = ctx / "ACTIVE_CURSOR_HOOK_STATE.json"
    turn_packet = json.loads(turn_path.read_text(encoding="utf-8"))
    objective = turn_packet["objective"]
    return {
        "turn_sha": _sha256_file(turn_path),
        "plan_sha": _sha256_file(plan_path),
        "hook_sha": _sha256_file(hook_path),
        "objective_sha": _sha256_text(objective),
    }


def _build_proof(
    shell_root: Path,
    *,
    carrier_surface: str = "CURSOR_CARRIER_CONTROL_SURFACE",
    turn_sha: str | None = None,
    plan_sha: str | None = None,
    hook_sha: str | None = None,
    continue_verdict: str = "ION_CARRIER_CONTINUE_READY",
    objective_sha256: str | None = None,
    spawn_rows: list[tuple[int, str]] | None = None,
    extra: str = "",
) -> str:
    shas = _fixture_shas(shell_root)
    turn_sha = turn_sha or shas["turn_sha"]
    plan_sha = plan_sha or shas["plan_sha"]
    hook_sha = hook_sha or shas["hook_sha"]
    objective_sha256 = objective_sha256 or shas["objective_sha"]
    spawn_rows = spawn_rows if spawn_rows is not None else [(1, "steward")]

    spawn_lines = "\n".join(f"- index={index} role={role}" for index, role in spawn_rows)
    return (
        f"{CARRIER_CONTROL_PROOF_HEADING}\n"
        f"carrier_surface: {carrier_surface}\n"
        f"shell_root: {shell_root}\n"
        "operator_message: continue\n"
        "loaded:\n"
        f'- path={TURN_REL} sha256={turn_sha} bytes=100 excerpt="schema_id"\n'
        f'- path={PLAN_REL} sha256={plan_sha} bytes=100 excerpt="schema_id"\n'
        f'- path={HOOK_REL} sha256={hook_sha} bytes=100 excerpt="continue_verdict"\n'
        f"continue_verdict: {continue_verdict}\n"
        f"objective_sha256: {objective_sha256}\n"
        f"spawn_queue:\n{spawn_lines}\n"
        "next_lawful_action: execute spawn rows\n"
        f"{extra}"
    )


def test_accepted_proof_passes_and_writes_receipt(shell_root: Path, tmp_path: Path) -> None:
    proof_text = _build_proof(shell_root)
    result = evaluate_carrier_control_proof(shell_root=shell_root, proof_text=proof_text)

    assert result["accepted"] is True
    assert result["findings"] == []
    assert result["schema_id"] == "ion.carrier_control_proof_evaluation.v1"
    assert result["integration_decision"] == "ALLOW_CARRIER_CONTROL_CONTINUE"
    assert result["production_authority"] is False
    assert result["live_execution_authority"] is False
    assert all(item["match"] for item in result["verified_reads"])

    receipt_path = write_receipt(
        shell_root=shell_root,
        evaluation=result,
        operator_message="continue",
    )
    assert receipt_path == shell_root / "ION/05_context/current/ACTIVE_CARRIER_CONTROL_PROOF_RECEIPT.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["schema_id"] == "ion.carrier_control_proof_receipt.v1"
    assert receipt["accepted"] is True
    assert "created_at" in receipt

    ledger_path = shell_root / "ION/05_context/current/ACTIVE_CARRIER_CONTROL_PROOF_LEDGER.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert ledger["schema_id"] == "ion.carrier_control_proof_ledger.v1"
    assert len(ledger["records"]) == 1
    assert ledger["records"][0]["accepted"] is True
    assert ledger["records"][0]["finding_count"] == 0
    assert ledger["records"][0]["integration_decision"] == "ALLOW_CARRIER_CONTROL_CONTINUE"

    proof_file = tmp_path / "proof.md"
    proof_file.write_text(proof_text, encoding="utf-8")
    file_result = evaluate_carrier_control_proof_file(shell_root=shell_root, proof_path=proof_file)
    assert file_result["accepted"] is True
    assert file_result["proof_path"] == str(proof_file)
    assert file_result["shell_root"] == str(shell_root)


def test_missing_heading_rejected(shell_root: Path) -> None:
    proof_text = _build_proof(shell_root).replace(CARRIER_CONTROL_PROOF_HEADING, "### WRONG HEADING")
    result = evaluate_carrier_control_proof(shell_root=shell_root, proof_text=proof_text)
    assert result["accepted"] is False
    assert "missing_initial_carrier_control_proof_heading" in result["findings"]


def test_stale_sha_rejected(shell_root: Path) -> None:
    proof_text = _build_proof(shell_root, turn_sha="f" * 64)
    result = evaluate_carrier_control_proof(shell_root=shell_root, proof_text=proof_text)
    assert result["accepted"] is False
    assert f"stale_or_mismatched_sha256:{TURN_REL}" in result["findings"]


def test_carrier_surface_role_rejected(shell_root: Path) -> None:
    proof_text = _build_proof(shell_root, carrier_surface="STEWARD")
    result = evaluate_carrier_control_proof(shell_root=shell_root, proof_text=proof_text)
    assert result["accepted"] is False
    assert "carrier_surface_must_not_be_ion_role:STEWARD" in result["findings"]


def test_continue_verdict_mismatch_rejected(shell_root: Path) -> None:
    proof_text = _build_proof(shell_root, continue_verdict="ION_CARRIER_CONTINUE_BLOCKED")
    result = evaluate_carrier_control_proof(shell_root=shell_root, proof_text=proof_text)
    assert result["accepted"] is False
    assert "continue_verdict_mismatch" in result["findings"]


def test_objective_sha_mismatch_rejected(shell_root: Path) -> None:
    proof_text = _build_proof(shell_root, objective_sha256="e" * 64)
    result = evaluate_carrier_control_proof(shell_root=shell_root, proof_text=proof_text)
    assert result["accepted"] is False
    assert "objective_sha256_mismatch" in result["findings"]


def test_spawn_queue_mismatch_rejected(shell_root: Path) -> None:
    proof_text = _build_proof(shell_root, spawn_rows=[(2, "relay")])
    result = evaluate_carrier_control_proof(shell_root=shell_root, proof_text=proof_text)
    assert result["accepted"] is False
    assert "spawn_queue_mismatch" in result["findings"]


def test_missing_required_path_rejected(shell_root: Path) -> None:
    proof_text = _build_proof(shell_root).replace(f"path={PLAN_REL}", "path=ION/05_context/current/MISSING.json")
    result = evaluate_carrier_control_proof(shell_root=shell_root, proof_text=proof_text)
    assert result["accepted"] is False
    assert f"missing_required_loaded_path:{PLAN_REL}" in result["findings"]
