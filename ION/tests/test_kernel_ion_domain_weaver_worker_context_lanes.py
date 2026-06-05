from __future__ import annotations

import json
from pathlib import Path

import pytest

from kernel.ion_domain_weaver_worker_context_lanes import (
    CODEX_SOLO_RELATIVE_PATH,
    resolve_worker_context_lane,
    sanitize_worker_id,
    write_candidate_row,
    write_context_receipt,
    write_fanin_summary,
    write_spawn_request,
)


def _active_root(tmp_path: Path) -> Path:
    root = tmp_path / "active"
    (root / "ION").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = 'ion-test'\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").write_text("test authority\n", encoding="utf-8")
    return root


def test_sanitize_worker_id_rejects_path_escape_and_lead_aliases() -> None:
    assert sanitize_worker_id("McCarthy Worker") == "mccarthy-worker"
    assert sanitize_worker_id("019E8FCF_915C") == "019e8fcf_915c"

    with pytest.raises(ValueError, match="path_separators"):
        sanitize_worker_id("../codex_solo")

    with pytest.raises(ValueError, match="reserved"):
        sanitize_worker_id("codex_solo")


def test_resolve_worker_lane_requires_active_root_proof(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="missing_pyproject"):
        resolve_worker_context_lane(tmp_path / "missing", "mccarthy")

    root = tmp_path / "partial"
    root.mkdir()
    (root / "pyproject.toml").write_text("[project]\nname = 'partial'\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing_repo_authority"):
        resolve_worker_context_lane(root, "mccarthy")


def test_worker_rows_are_local_and_codex_solo_is_untouched(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    codex_solo = root / CODEX_SOLO_RELATIVE_PATH
    codex_solo.mkdir(parents=True)
    hot_context = codex_solo / "HOT_CONTEXT.md"
    hot_context.write_text("lead capsule sentinel\n", encoding="utf-8")

    receipt = write_context_receipt(
        root,
        "McCarthy",
        {"packet_id": "PCKT-DOMAIN-WEAVER-WORKER-CAPSULE-LANE-V0_1"},
        row_id="context-receipt",
    )

    assert receipt["worker_id"] == "mccarthy"
    assert receipt["authority"]["accepted_state"] is False
    assert receipt["authority"]["carrier_intake_only"] is True
    assert receipt["paths"]["codex_solo_touched"] is False
    assert receipt["path"] == (
        "ION/05_context/current/domain_weaver/workers/"
        "mccarthy/context/receipts/context-receipt.json"
    )
    assert hot_context.read_text(encoding="utf-8") == "lead capsule sentinel\n"


def test_candidate_rows_reject_accepted_state_claims(tmp_path: Path) -> None:
    root = _active_root(tmp_path)

    with pytest.raises(ValueError, match="forbidden_authority_claim:accepted_state"):
        write_candidate_row(root, "mccarthy", {"accepted_state": True})

    with pytest.raises(ValueError, match="forbidden_authority_claim:production_authority"):
        write_context_receipt(root, "mccarthy", {"production_authority": True})


def test_fanin_summary_contains_worker_local_refs_only(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    write_context_receipt(root, "McCarthy", {"packet_id": "PCKT"}, row_id="receipt-a")
    write_candidate_row(root, "McCarthy", {"candidate": "worker-lane"}, row_id="candidate-a")
    write_spawn_request(
        root,
        "McCarthy",
        requested_domain="domain.nemesis.review",
        requested_packet="PCKT-DOMAIN-WEAVER-NEMESIS-CHILD-REQUEST",
        requested_callsign="Dijkstra",
        allowed_scope=["read-only audit", "candidate artifact"],
        forbidden_actions=["source_patch_without_lead_settlement"],
        evidence_requirements=["root proof", "fan-in receipt"],
        row_id="spawn-a",
    )

    summary = write_fanin_summary(root, "McCarthy", row_id="fanin-a")

    assert summary["accepted_state"] is False
    assert summary["carrier_intake_only"] is True
    assert summary["codex_solo_touched"] is False
    assert summary["receipt_refs"] == [
        "ION/05_context/current/domain_weaver/workers/"
        "mccarthy/context/receipts/receipt-a.json"
    ]
    assert summary["candidate_refs"] == [
        "ION/05_context/current/domain_weaver/workers/"
        "mccarthy/context/candidates/candidate-a.candidate.json"
    ]
    assert summary["spawn_request_refs"] == [
        "ION/05_context/current/domain_weaver/workers/"
        "mccarthy/context/spawn_requests/spawn-a.spawn_request.json"
    ]
    assert summary["path"] == (
        "ION/05_context/current/domain_weaver/workers/"
        "mccarthy/context/fanin/fanin-a.fanin.json"
    )

    written = json.loads((root / summary["path"]).read_text(encoding="utf-8"))
    assert written["authority"]["codex_solo_write_allowed"] is False
    assert written["spawn_request_count"] == 1


def test_spawn_request_is_queue_mediated_and_never_spawns(tmp_path: Path) -> None:
    root = _active_root(tmp_path)

    request = write_spawn_request(
        root,
        "Babbage",
        requested_domain="domain.context.cartographer",
        requested_packet="PCKT-DOMAIN-WEAVER-CONTEXT-CARTOGRAPHY-CHILD",
        requested_callsign="Lovelace",
        requested_true_name="Ada Lovelace",
        requested_role_id="role.context_cartographer",
        requested_role_tier="specialist",
        work_class="domain_weaver_spawn_dispatch",
        lane_id="context_lane",
        domain_context_package="ION/05_context/current/domain_weaver/.ion/ACTIVE_CONTEXT_PACKAGE.md",
        required_context_reads=[
            {
                "kind": "file",
                "path": "ION/05_context/current/domain_weaver/AGENTS.md",
                "required": True,
            }
        ],
        planned_writes=[
            "ION/05_context/current/domain_weaver/workers/lovelace/context/candidates/result.candidate.json"
        ],
        allowed_scope=["read active-root source", "write worker-local candidate artifact"],
        forbidden_actions=["mutate active source", "touch Codex Solo"],
        evidence_requirements=["active-root proof", "worker-lane receipt"],
        row_id="context-child",
    )

    assert request["status"] == "requested"
    assert request["parent_worker_id"] == "babbage"
    assert request["requested_domain"] == "domain.context.cartographer"
    assert request["requested_callsign"] == "Lovelace"
    assert request["requested_true_name"] == "Ada Lovelace"
    assert request["requested_role_id"] == "role.context_cartographer"
    assert request["requested_role_tier"] == "specialist"
    assert request["work_class"] == "domain_weaver_spawn_dispatch"
    assert request["lane_id"] == "context_lane"
    assert request["domain_context_package"] == (
        "ION/05_context/current/domain_weaver/.ion/ACTIVE_CONTEXT_PACKAGE.md"
    )
    assert request["required_context_reads"][0]["path"] == (
        "ION/05_context/current/domain_weaver/AGENTS.md"
    )
    assert request["planned_writes"] == [
        "ION/05_context/current/domain_weaver/workers/lovelace/context/candidates/result.candidate.json"
    ]
    assert request["authority"]["carrier_intake_only"] is True
    assert request["authority"]["accepted_state"] is False
    assert request["spawn_execution"]["actual_spawn_performed"] is False
    assert request["spawn_execution"]["queue_mediated_required"] is True
    assert request["spawn_execution"]["raw_external_codex_exec_allowed"] is False
    assert request["spawn_execution"]["direct_nested_subagent_spawn_allowed"] is False
    assert "raw_external_codex_exec" in request["forbidden_actions"]
    assert "direct_nested_subagent_spawn" in request["forbidden_actions"]
    assert request["path"] == (
        "ION/05_context/current/domain_weaver/workers/"
        "babbage/context/spawn_requests/context-child.spawn_request.json"
    )

    written = json.loads((root / request["path"]).read_text(encoding="utf-8"))
    assert written["paths"]["codex_solo_touched"] is False


def test_spawn_request_rejects_authority_claims_and_path_escape(tmp_path: Path) -> None:
    root = _active_root(tmp_path)

    with pytest.raises(ValueError, match="forbidden_authority_claim:production_authority"):
        write_spawn_request(
            root,
            "Babbage",
            requested_domain="domain.security",
            requested_packet="PCKT",
            allowed_scope={"production_authority": True},
            forbidden_actions=["none"],
            evidence_requirements=["proof"],
        )

    with pytest.raises(ValueError, match="requested_domain_must_not_contain_path_separators"):
        write_spawn_request(
            root,
            "Babbage",
            requested_domain="../escape",
            requested_packet="PCKT",
            allowed_scope=["read-only"],
            forbidden_actions=["none"],
            evidence_requirements=["proof"],
        )
