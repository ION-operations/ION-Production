from __future__ import annotations

import json
from pathlib import Path

from kernel.ion_domain_weaver_larger_fanout_control import (
    SCHEMA_ID,
    build_larger_fanout_control_readiness,
    write_larger_fanout_control_readiness,
)


def _active_root(tmp_path: Path) -> Path:
    root = tmp_path / "active"
    (root / "ION/REPO_AUTHORITY.md").parent.mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname = 'ion-test'\n", encoding="utf-8")
    (root / "ION/REPO_AUTHORITY.md").write_text("test authority\n", encoding="utf-8")
    return root


def _write_json(root: Path, rel: str, payload: dict) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _seed_required_domain_weaver_artifacts(root: Path) -> None:
    envelope = (
        root
        / "ION/05_context/current/domain_weaver/stewarded_autonomy/DOMAIN_WEAVER_LARGER_FANOUT_OPERATING_ENVELOPE_20260604T0410Z.md"
    )
    envelope.parent.mkdir(parents=True, exist_ok=True)
    envelope.write_text("# envelope\n", encoding="utf-8")

    _write_json(
        root,
        "ION/05_context/current/domain_weaver/operator_actions/20260604T035500Z_domain_weaver_alternate_worker_return_lane_patch_and_live_dogfood_settlement.json",
        {
            "schema_id": "ion.domain_weaver.operator_action_receipt.v0_1",
            "result": "active_root_patch_validated_and_live_dogfooded_carrier_intake_only",
        },
    )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/operator_actions/20260604T040100Z_domain_weaver_alternate_worker_provenance_receipt_bridge_settlement.json",
        {
            "schema_id": "ion.domain_weaver.operator_action_receipt.v0_1",
            "result": "active_root_patch_validated_and_live_receipt_recorded",
        },
    )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/operator_actions/20260604T040700Z_domain_weaver_native_subagent_transcript_bridge_live_dogfood_settlement.json",
        {
            "schema_id": "ion.domain_weaver.operator_action_receipt.v0_1",
            "result": "active_root_patch_validated_and_native_subagent_bridge_dogfooded",
            "focused_validation": {"passed": True},
            "live_dogfood": {
                "accepted_for_carrier_intake": True,
                "native_subagent_transcript_verified": True,
                "product_state_accepted": False,
            },
            "proof_projection": {
                "proof_ok": True,
                "automatic_agent_reaction_proven": False,
            },
        },
    )
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/operator_actions/20260604T041000Z_domain_weaver_larger_fanout_operating_envelope_created.json",
        {
            "schema_id": "ion.domain_weaver.operator_action_receipt.v0_1",
            "result": "candidate_operating_envelope_created",
            "fanout_wave": [
                "recursive_native_spawn_probe",
                "scalable_fanout_control_plane_cartography",
                "nemesis_larger_fanout_review",
            ],
        },
    )


def test_larger_fanout_readiness_allows_three_lane_candidate_wave(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    _seed_required_domain_weaver_artifacts(root)

    readiness = build_larger_fanout_control_readiness(
        root,
        requested_lane_count=3,
        generated_at="2026-06-04T04:16:00Z",
    )

    assert readiness["schema_id"] == SCHEMA_ID
    assert readiness["readiness_ok"] is True
    assert readiness["larger_fanout_candidate_allowed"] is True
    assert readiness["max_candidate_lane_count"] == 3
    assert readiness["candidate_wave"] == [
        "recursive_native_spawn_probe",
        "scalable_fanout_control_plane_cartography",
        "nemesis_larger_fanout_review",
    ]
    assert readiness["recursive_native_spawn_allowed"] is False
    assert readiness["blockers"] == []
    assert readiness["authority"]["production_authority"] is False


def test_larger_fanout_readiness_blocks_over_cap_and_recursive_spawn_without_probe(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_required_domain_weaver_artifacts(root)

    readiness = build_larger_fanout_control_readiness(
        root,
        requested_lane_count=4,
        recursive_native_spawn_requested=True,
    )

    assert readiness["readiness_ok"] is False
    assert "requested_lane_count_exceeds_candidate_cap" in readiness["blockers"]
    assert (
        "recursive_native_spawn_requested_without_one_child_probe_receipt"
        in readiness["blockers"]
    )
    assert readiness["recursive_native_spawn_allowed"] is False


def test_larger_fanout_readiness_blocks_missing_native_transcript_proof(
    tmp_path: Path,
) -> None:
    root = _active_root(tmp_path)
    _seed_required_domain_weaver_artifacts(root)
    native = (
        root
        / "ION/05_context/current/domain_weaver/operator_actions/20260604T040700Z_domain_weaver_native_subagent_transcript_bridge_live_dogfood_settlement.json"
    )
    payload = json.loads(native.read_text(encoding="utf-8"))
    payload["live_dogfood"]["native_subagent_transcript_verified"] = False
    native.write_text(json.dumps(payload), encoding="utf-8")

    readiness = build_larger_fanout_control_readiness(root)

    assert readiness["readiness_ok"] is False
    assert "native_subagent_transcript_not_verified" in readiness["blockers"]


def test_write_larger_fanout_readiness_artifacts(tmp_path: Path) -> None:
    root = _active_root(tmp_path)
    _seed_required_domain_weaver_artifacts(root)

    result = write_larger_fanout_control_readiness(
        root,
        generated_at="2026-06-04T04:16:00Z",
    )

    json_path = root / result["json_path"]
    markdown_path = root / result["markdown_path"]
    assert json_path.exists()
    assert markdown_path.exists()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert payload["readiness_ok"] is True
    assert "Domain Weaver Larger Fanout Control Readiness" in markdown
    assert "recursive_native_spawn_probe" in markdown
