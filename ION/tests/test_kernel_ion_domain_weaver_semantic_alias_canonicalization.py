from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from kernel.ion_domain_weaver_semantic_alias_canonicalization import (
    BOUNDED_WRITE_CONFIRMATION,
    MOUNT_MANIFEST_APPLY_SCHEMA_ID,
    MOUNT_MANIFEST_REWRITE_CANDIDATE_SCHEMA_ID,
    PROJECTION_APPLY_SCHEMA_ID,
    PROJECTION_REWRITE_CANDIDATE_SCHEMA_ID,
    SCHEMA_ID,
    SEMANTIC_ALIAS_ACCEPTED_WRITE_CONFIRMATION,
    SEMANTIC_ALIAS_MANIFEST_WRITE_CONFIRMATION,
    SUPERVISED_APPLY_PREFLIGHT_SCHEMA_ID,
    SUPERVISED_APPLY_PREFLIGHT_WRITE_RESULT_SCHEMA_ID,
    apply_semantic_alias_mount_manifest_rewrite,
    apply_semantic_alias_projection_rewrite,
    build_semantic_alias_mount_manifest_rewrite_candidate,
    build_semantic_alias_projection_rewrite_candidate,
    build_semantic_alias_supervised_apply_preflight,
    build_semantic_alias_canonicalization_candidate,
    json_write_text,
    write_semantic_alias_supervised_apply_preflight,
    write_semantic_alias_canonicalization_candidate,
)
from kernel.ion_domain_weaver_semantic_ids import VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID


def _write_json(root: Path, rel_path: str, payload: dict) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _seed(root: Path) -> None:
    _write_json(
        root,
        "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json",
        {
            "domains": [{"domain_id": "ion_vnext_front_door"}],
            "edges": [{"from": "ion_vnext_front_door", "to": "role.steward"}],
        },
    )
    promotion = {
        "decisions": [
            {
                "candidate_domain_id": "ion_vnext_front_door",
                "proposed_active_domain_id": VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID,
                "proposed_active_registry_target": "ION/03_registry/domains/domain.vnext_front_door.domain.yaml",
                "candidate_draft_path": (
                    "ION/05_context/current/domain_weaver/promotion_drafts/"
                    "domain.vnext_front_door.domain.candidate.yaml"
                ),
            }
        ]
    }
    _write_json(root, "ION/05_context/current/domain_weaver/PROMOTION_REVIEW.json", promotion)
    _write_json(root, "ION/05_context/current/domain_weaver/PROMOTION_GATE.json", promotion)
    _write_json(
        root,
        "ION/05_context/current/codex_agent_mounts/role_atlas__ion_vnext_front_door/ION_AGENT_MOUNT_MANIFEST.json",
        {"domain_id": "ion_vnext_front_door"},
    )


def _seed_apply_lease(
    root: Path,
    *,
    agent_id: str,
    lease_id: str,
    target_paths: list[str],
) -> None:
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    board_path = root / "ION/05_context/current/worker_shift/ACTIVE_WORKER_SHIFT_BOARD.json"
    board_path.parent.mkdir(parents=True, exist_ok=True)
    board_path.write_text(
        json.dumps(
            {
                "schema_id": "ion.worker_shift_board.v0_1",
                "updated_at": timestamp,
                "authority": {
                    "accepted_state_authority": False,
                    "production_authority": False,
                    "live_execution_authority": False,
                    "secrets_authority": False,
                },
                "active_shifts": [],
                "active_leases": [
                    {
                        "lease_id": lease_id,
                        "agent_id": agent_id,
                        "worker_id": agent_id,
                        "declared_true_name": agent_id,
                        "identity_binding_status": "BOUND_TRUE_NAME",
                        "worker_id_source": "declared_true_name",
                        "unbound_worker_id": False,
                        "mode": "exclusive_write",
                        "lease_type": "exclusive_write",
                        "lease_class": "semantic_alias_projection_apply_lease",
                        "root_scope": "active_root",
                        "active_root": str(root),
                        "paths": target_paths,
                        "raw_paths": target_paths,
                        "resolved_paths": [
                            (root / target_path).resolve(strict=False).as_posix()
                            for target_path in target_paths
                        ],
                        "claimed_at": timestamp,
                        "last_heartbeat_at": timestamp,
                        "updated_at": timestamp,
                        "status": "ACTIVE",
                    }
                ],
                "stale_workers": [],
                "recent_signoffs": [],
                "recent_receipts": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def test_semantic_alias_candidate_preserves_aliases_without_writes(tmp_path: Path) -> None:
    _seed(tmp_path)

    payload = build_semantic_alias_canonicalization_candidate(
        tmp_path,
        generated_at="2026-06-04T06:00:00Z",
    )

    assert payload["schema_id"] == SCHEMA_ID
    assert payload["candidate_map"]["canonical_id"] == VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID
    assert payload["authority"]["registry_write_performed"] is False
    assert payload["authority"]["projection_overwrite_performed"] is False
    assert "semantic_alias_references_require_candidate_rewrite_review" in payload["blockers"]
    assert payload["context_graph_deltas"]["upsert_claims"][0]["value"]["canonical"] == VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID


def test_write_semantic_alias_candidate_artifacts_and_receipt(tmp_path: Path) -> None:
    _seed(tmp_path)

    result = write_semantic_alias_canonicalization_candidate(
        tmp_path,
        generated_at="2026-06-04T06:00:00Z",
    )

    json_path = tmp_path / result["json_path"]
    report_path = tmp_path / result["report_path"]
    receipt_path = tmp_path / result["operator_receipt_path"]
    assert json_path.exists()
    assert report_path.exists()
    assert receipt_path.exists()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["result"] == "semantic_alias_canonicalization_candidate_written_no_state_movement"
    assert result["accepted_state_moved"] is False


def test_semantic_alias_projection_rewrite_candidate_rewrites_exact_values_only(tmp_path: Path) -> None:
    _seed(tmp_path)
    projection_path = tmp_path / "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    projection["metadata"] = {
        "ion_vnext_front_door": "key_must_not_be_rewritten",
        "partial": "prefix ion_vnext_front_door suffix",
        "authority": "domain.ion_vnext_front_door_authority",
    }
    projection_path.write_text(json.dumps(projection, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    candidate = build_semantic_alias_projection_rewrite_candidate(
        tmp_path,
        generated_at="2026-06-04T07:00:00Z",
    )

    assert candidate["schema_id"] == PROJECTION_REWRITE_CANDIDATE_SCHEMA_ID
    assert candidate["ok"] is True
    assert candidate["mutates_active_state"] is False
    assert candidate["accepted_state_claim"] is False
    assert candidate["target"]["candidate_body_sha256"]
    body = candidate["candidate_body"]
    assert body["domains"][0]["domain_id"] == VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID
    assert body["edges"][0]["from"] == VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID
    assert body["metadata"]["authority"] == VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID
    assert body["metadata"]["ion_vnext_front_door"] == "key_must_not_be_rewritten"
    assert body["metadata"]["partial"] == "prefix ion_vnext_front_door suffix"
    assert candidate["rewrite_summary"]["rewritten_value_count"] == 3
    assert candidate["rewrite_summary"]["mount_manifest_rewrite_included"] is False


def test_semantic_alias_mount_manifest_rewrite_candidate_rewrites_top_level_domain_fields_only(tmp_path: Path) -> None:
    _seed(tmp_path)
    manifest_rel = (
        "ION/05_context/current/codex_agent_mounts/"
        "role_atlas__ion_vnext_front_door/ION_AGENT_MOUNT_MANIFEST.json"
    )
    manifest_path = tmp_path / manifest_rel
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update(
        {
            "domain": "domain.ion_vnext_front_door_authority",
            "nested": {"domain_id": "ion_vnext_front_door"},
            "partial": "prefix ion_vnext_front_door suffix",
        }
    )
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    candidate = build_semantic_alias_mount_manifest_rewrite_candidate(
        tmp_path,
        generated_at="2026-06-04T07:10:00Z",
    )

    assert candidate["schema_id"] == MOUNT_MANIFEST_REWRITE_CANDIDATE_SCHEMA_ID
    assert candidate["ok"] is True
    assert candidate["mutates_active_state"] is False
    assert candidate["accepted_state_claim"] is False
    assert candidate["target"]["path"] == manifest_rel
    assert candidate["target"]["candidate_body_sha256"]
    body = candidate["candidate_body"]
    assert body["domain_id"] == VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID
    assert body["domain"] == VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID
    assert body["nested"]["domain_id"] == "ion_vnext_front_door"
    assert body["partial"] == "prefix ion_vnext_front_door suffix"
    assert candidate["rewrite_summary"]["rewritten_field_count"] == 2
    assert candidate["rewrite_summary"]["projection_rewrite_included"] is False
    assert candidate["rewrite_summary"]["active_context_package_refresh_included"] is False


def test_semantic_alias_supervised_apply_preflight_builds_two_step_no_write_plan(tmp_path: Path) -> None:
    _seed(tmp_path)
    projection_rel = "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    manifest_rel = (
        "ION/05_context/current/codex_agent_mounts/"
        "role_atlas__ion_vnext_front_door/ION_AGENT_MOUNT_MANIFEST.json"
    )
    projection_before = (tmp_path / projection_rel).read_text(encoding="utf-8")
    manifest_before = (tmp_path / manifest_rel).read_text(encoding="utf-8")

    preflight = build_semantic_alias_supervised_apply_preflight(
        tmp_path,
        generated_at="2026-06-04T07:20:00Z",
        agent_id="codex_cli:test-semantic-alias",
        lease_id="lease-semantic-alias-both",
        idempotency_prefix="dw-spw-012",
    )

    assert preflight["schema_id"] == SUPERVISED_APPLY_PREFLIGHT_SCHEMA_ID
    assert preflight["ok"] is True
    assert preflight["mutates_active_state"] is False
    assert preflight["accepted_state_claim"] is False
    assert preflight["active_root_apply_invoked"] is False
    assert preflight["projection_overwrite_performed"] is False
    assert preflight["mount_manifest_write_performed"] is False
    assert preflight["active_context_package_refresh_performed"] is False
    assert preflight["required_combined_lease_targets"] == [projection_rel, manifest_rel]
    sequence = preflight["write_sequence"]
    assert [step["route_id"] for step in sequence] == [
        "semantic_alias_projection_apply",
        "semantic_alias_mount_manifest_apply",
    ]
    assert sequence[0]["route_call_args_template"]["before_sha256"] == preflight["targets"]["projection"]["before_sha256"]
    assert sequence[0]["route_call_args_template"]["replacement_body_sha256"] == (
        preflight["targets"]["projection"]["candidate_body_sha256"]
    )
    assert sequence[1]["route_call_args_template"]["before_sha256"] == (
        preflight["targets"]["mount_manifest"]["before_sha256"]
    )
    assert sequence[1]["route_call_args_template"]["replacement_body_sha256"] == (
        preflight["targets"]["mount_manifest"]["candidate_body_sha256"]
    )
    assert preflight["candidate_summaries"]["projection"]["candidate_body"]["omitted"] is True
    assert preflight["candidate_summaries"]["mount_manifest"]["candidate_body"]["omitted"] is True
    assert (tmp_path / projection_rel).read_text(encoding="utf-8") == projection_before
    assert (tmp_path / manifest_rel).read_text(encoding="utf-8") == manifest_before


def test_write_semantic_alias_supervised_apply_preflight_refreshes_stale_previous_without_writes(
    tmp_path: Path,
) -> None:
    _seed(tmp_path)
    projection_rel = "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    manifest_rel = (
        "ION/05_context/current/codex_agent_mounts/"
        "role_atlas__ion_vnext_front_door/ION_AGENT_MOUNT_MANIFEST.json"
    )
    previous_rel = (
        "ION/05_context/current/domain_weaver/semantic_alias_canonicalization/"
        "DOMAIN_WEAVER_SEMANTIC_ALIAS_SUPERVISED_APPLY_PREFLIGHT.latest.json"
    )
    previous = build_semantic_alias_supervised_apply_preflight(
        tmp_path,
        generated_at="2026-06-04T07:20:00Z",
        idempotency_prefix="dw-spw-012",
    )
    _write_json(tmp_path, previous_rel, previous)

    projection_path = tmp_path / projection_rel
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    projection["edges"].append({"from": "domain.ion_vnext_front_door_authority", "to": "role.audit"})
    _write_json(tmp_path, projection_rel, projection)
    projection_before = projection_path.read_text(encoding="utf-8")
    manifest_before = (tmp_path / manifest_rel).read_text(encoding="utf-8")

    result = write_semantic_alias_supervised_apply_preflight(
        tmp_path,
        generated_at="2026-06-04T07:30:00Z",
        agent_id="codex_cli:test-semantic-alias",
        lease_id="lease-semantic-alias-both",
        idempotency_prefix="dw-spw-012",
    )

    assert result["schema_id"] == SUPERVISED_APPLY_PREFLIGHT_WRITE_RESULT_SCHEMA_ID
    assert result["previous_preflight_stale_against_current_projection_sha"] is True
    assert result["current_projection_target_current"] is True
    assert result["active_root_apply_invoked"] is False
    assert result["projection_overwrite_performed"] is False
    assert result["mount_manifest_write_performed"] is False
    assert result["mutates_active_state"] is False
    assert result["accepted_state_claim"] is False
    assert projection_path.read_text(encoding="utf-8") == projection_before
    assert (tmp_path / manifest_rel).read_text(encoding="utf-8") == manifest_before

    preflight_path = tmp_path / result["json_path"]
    projection_candidate_path = tmp_path / result["projection_rewrite_candidate_path"]
    manifest_candidate_path = tmp_path / result["mount_manifest_rewrite_candidate_path"]
    receipt_path = tmp_path / result["operator_receipt_path"]
    assert preflight_path.is_file()
    assert projection_candidate_path.is_file()
    assert manifest_candidate_path.is_file()
    assert receipt_path.is_file()
    written = json.loads(preflight_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert written["schema_id"] == SUPERVISED_APPLY_PREFLIGHT_SCHEMA_ID
    assert written["previous_preflight_currentness"]["stale_against_current_projection_sha"] is True
    assert written["targets"]["projection"]["before_sha256"] != previous["targets"]["projection"]["before_sha256"]
    assert written["write_sequence"][0]["route_call_args_template"]["before_sha256"] == (
        written["targets"]["projection"]["before_sha256"]
    )
    assert receipt["result"] == "semantic_alias_supervised_apply_preflight_written_no_state_movement"
    assert receipt["previous_preflight_currentness"]["stale_against_current_projection_sha"] is True


def test_semantic_alias_projection_apply_blocks_without_required_gates(tmp_path: Path) -> None:
    _seed(tmp_path)
    agent_id = "codex_cli:semantic-alias-apply"
    lease_id = "lease-semantic-alias-apply"
    target_rel = "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    _seed_apply_lease(tmp_path, agent_id=agent_id, lease_id=lease_id, target_paths=[target_rel])
    candidate = build_semantic_alias_projection_rewrite_candidate(tmp_path, generated_at="2026-06-04T07:00:00Z")
    before_text = (tmp_path / target_rel).read_text(encoding="utf-8")

    result = apply_semantic_alias_projection_rewrite(
        tmp_path,
        confirmation=BOUNDED_WRITE_CONFIRMATION,
        semantic_alias_write_confirmation="",
        idempotency_key="semantic-alias-missing-gates",
        agent_id=agent_id,
        lease_id=lease_id,
        before_sha256=candidate["target"]["before_sha256"],
        replacement_body_sha256=candidate["target"]["candidate_body_sha256"],
        execute_write=False,
        generated_at="2026-06-04T07:01:00Z",
    )

    assert result["schema_id"] == PROJECTION_APPLY_SCHEMA_ID
    assert result["ok"] is False
    assert result["projection_overwrite_performed"] is False
    assert result["accepted_state_claim"] is False
    assert "semantic_alias_projection_apply_accepted_write_confirmation_required" in result["blockers"]
    assert "semantic_alias_projection_apply_execute_write_required" in result["blockers"]
    assert (tmp_path / target_rel).read_text(encoding="utf-8") == before_text


def test_semantic_alias_mount_manifest_apply_blocks_without_required_gates(tmp_path: Path) -> None:
    _seed(tmp_path)
    agent_id = "codex_cli:semantic-alias-manifest-apply"
    lease_id = "lease-semantic-alias-manifest-apply"
    target_rel = (
        "ION/05_context/current/codex_agent_mounts/"
        "role_atlas__ion_vnext_front_door/ION_AGENT_MOUNT_MANIFEST.json"
    )
    _seed_apply_lease(tmp_path, agent_id=agent_id, lease_id=lease_id, target_paths=[target_rel])
    candidate = build_semantic_alias_mount_manifest_rewrite_candidate(
        tmp_path,
        generated_at="2026-06-04T07:10:00Z",
    )
    before_text = (tmp_path / target_rel).read_text(encoding="utf-8")

    result = apply_semantic_alias_mount_manifest_rewrite(
        tmp_path,
        confirmation=BOUNDED_WRITE_CONFIRMATION,
        manifest_write_confirmation="",
        idempotency_key="semantic-alias-manifest-missing-gates",
        agent_id=agent_id,
        lease_id=lease_id,
        before_sha256=candidate["target"]["before_sha256"],
        replacement_body_sha256=candidate["target"]["candidate_body_sha256"],
        execute_write=False,
        generated_at="2026-06-04T07:11:00Z",
    )

    assert result["schema_id"] == MOUNT_MANIFEST_APPLY_SCHEMA_ID
    assert result["ok"] is False
    assert result["projection_overwrite_performed"] is False
    assert result["mount_manifest_write_performed"] is False
    assert result["accepted_state_claim"] is False
    assert "semantic_alias_mount_manifest_apply_manifest_write_confirmation_required" in result["blockers"]
    assert "semantic_alias_mount_manifest_apply_execute_write_required" in result["blockers"]
    assert (tmp_path / target_rel).read_text(encoding="utf-8") == before_text


def test_semantic_alias_projection_apply_rejects_hash_races(tmp_path: Path) -> None:
    _seed(tmp_path)
    agent_id = "codex_cli:semantic-alias-apply"
    lease_id = "lease-semantic-alias-apply"
    target_rel = "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    _seed_apply_lease(tmp_path, agent_id=agent_id, lease_id=lease_id, target_paths=[target_rel])
    candidate = build_semantic_alias_projection_rewrite_candidate(tmp_path, generated_at="2026-06-04T07:00:00Z")
    before_text = (tmp_path / target_rel).read_text(encoding="utf-8")
    base_args = {
        "confirmation": BOUNDED_WRITE_CONFIRMATION,
        "semantic_alias_write_confirmation": SEMANTIC_ALIAS_ACCEPTED_WRITE_CONFIRMATION,
        "idempotency_key": "semantic-alias-hash-race",
        "agent_id": agent_id,
        "lease_id": lease_id,
        "before_sha256": candidate["target"]["before_sha256"],
        "replacement_body_sha256": candidate["target"]["candidate_body_sha256"],
        "execute_write": True,
        "generated_at": "2026-06-04T07:01:00Z",
    }

    stale_before = apply_semantic_alias_projection_rewrite(
        tmp_path,
        **{**base_args, "before_sha256": "0" * 64, "idempotency_key": "semantic-alias-stale-before"},
    )
    bad_replacement = apply_semantic_alias_projection_rewrite(
        tmp_path,
        **{
            **base_args,
            "replacement_body_sha256": "1" * 64,
            "idempotency_key": "semantic-alias-bad-replacement",
        },
    )

    assert stale_before["ok"] is False
    assert "semantic_alias_projection_apply_before_sha256_mismatch" in stale_before["blockers"]
    assert bad_replacement["ok"] is False
    assert "semantic_alias_projection_apply_replacement_body_sha256_mismatch" in bad_replacement["blockers"]
    assert (tmp_path / target_rel).read_text(encoding="utf-8") == before_text


def test_semantic_alias_mount_manifest_apply_rejects_hash_races(tmp_path: Path) -> None:
    _seed(tmp_path)
    agent_id = "codex_cli:semantic-alias-manifest-apply"
    lease_id = "lease-semantic-alias-manifest-apply"
    target_rel = (
        "ION/05_context/current/codex_agent_mounts/"
        "role_atlas__ion_vnext_front_door/ION_AGENT_MOUNT_MANIFEST.json"
    )
    _seed_apply_lease(tmp_path, agent_id=agent_id, lease_id=lease_id, target_paths=[target_rel])
    candidate = build_semantic_alias_mount_manifest_rewrite_candidate(
        tmp_path,
        generated_at="2026-06-04T07:10:00Z",
    )
    before_text = (tmp_path / target_rel).read_text(encoding="utf-8")
    base_args = {
        "confirmation": BOUNDED_WRITE_CONFIRMATION,
        "manifest_write_confirmation": SEMANTIC_ALIAS_MANIFEST_WRITE_CONFIRMATION,
        "idempotency_key": "semantic-alias-manifest-hash-race",
        "agent_id": agent_id,
        "lease_id": lease_id,
        "before_sha256": candidate["target"]["before_sha256"],
        "replacement_body_sha256": candidate["target"]["candidate_body_sha256"],
        "execute_write": True,
        "generated_at": "2026-06-04T07:11:00Z",
    }

    stale_before = apply_semantic_alias_mount_manifest_rewrite(
        tmp_path,
        **{**base_args, "before_sha256": "0" * 64, "idempotency_key": "semantic-alias-manifest-stale-before"},
    )
    bad_replacement = apply_semantic_alias_mount_manifest_rewrite(
        tmp_path,
        **{
            **base_args,
            "replacement_body_sha256": "1" * 64,
            "idempotency_key": "semantic-alias-manifest-bad-replacement",
        },
    )

    assert stale_before["ok"] is False
    assert "semantic_alias_mount_manifest_apply_before_sha256_mismatch" in stale_before["blockers"]
    assert bad_replacement["ok"] is False
    assert "semantic_alias_mount_manifest_apply_replacement_body_sha256_mismatch" in bad_replacement["blockers"]
    assert (tmp_path / target_rel).read_text(encoding="utf-8") == before_text


def test_semantic_alias_projection_apply_writes_projection_only_and_idempotent_receipt(tmp_path: Path) -> None:
    _seed(tmp_path)
    agent_id = "codex_cli:semantic-alias-apply"
    lease_id = "lease-semantic-alias-apply"
    target_rel = "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    manifest_rel = (
        "ION/05_context/current/codex_agent_mounts/"
        "role_atlas__ion_vnext_front_door/ION_AGENT_MOUNT_MANIFEST.json"
    )
    _seed_apply_lease(tmp_path, agent_id=agent_id, lease_id=lease_id, target_paths=[target_rel])
    candidate = build_semantic_alias_projection_rewrite_candidate(tmp_path, generated_at="2026-06-04T07:00:00Z")
    manifest_before = (tmp_path / manifest_rel).read_text(encoding="utf-8")
    apply_args = {
        "confirmation": BOUNDED_WRITE_CONFIRMATION,
        "semantic_alias_write_confirmation": SEMANTIC_ALIAS_ACCEPTED_WRITE_CONFIRMATION,
        "idempotency_key": "semantic-alias-happy-path",
        "agent_id": agent_id,
        "lease_id": lease_id,
        "before_sha256": candidate["target"]["before_sha256"],
        "replacement_body_sha256": candidate["target"]["candidate_body_sha256"],
        "execute_write": True,
        "generated_at": "2026-06-04T07:01:00Z",
    }

    applied = apply_semantic_alias_projection_rewrite(tmp_path, **apply_args)
    replayed = apply_semantic_alias_projection_rewrite(
        tmp_path,
        **{**apply_args, "generated_at": "2026-06-04T07:02:00Z"},
    )
    conflict = apply_semantic_alias_projection_rewrite(
        tmp_path,
        **{
            **apply_args,
            "replacement_body_sha256": "2" * 64,
            "generated_at": "2026-06-04T07:03:00Z",
        },
    )

    assert applied["ok"] is True
    assert applied["status"] == "semantic_alias_projection_apply_applied"
    assert applied["projection_overwrite_performed"] is True
    assert applied["accepted_state_claim"] is True
    assert applied["production_authority"] is False
    assert applied["live_execution_authority"] is False
    assert applied["secrets_authority"] is False
    assert applied["materialization_authority"] is False
    projection = json.loads((tmp_path / target_rel).read_text(encoding="utf-8"))
    assert projection == candidate["candidate_body"]
    assert (tmp_path / target_rel).read_text(encoding="utf-8") == json_write_text(candidate["candidate_body"])
    assert (tmp_path / manifest_rel).read_text(encoding="utf-8") == manifest_before
    receipt_path = tmp_path / applied["receipt_path"]
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["schema_id"] == "ion.domain_weaver.semantic_alias.projection_apply_receipt.v0_1"
    assert receipt["target"]["path"] == target_rel
    assert receipt["write_set"] == [target_rel, applied["receipt_path"]]
    assert receipt["rewrite_summary"]["mount_manifest_rewrite_included"] is False
    assert replayed["ok"] is True
    assert replayed["idempotent_replay"] is True
    assert replayed["mutates_active_state"] is False
    assert conflict["ok"] is False
    assert "semantic_alias_projection_apply_idempotency_conflict" in conflict["blockers"]


def test_semantic_alias_mount_manifest_apply_writes_manifest_only_and_idempotent_receipt(tmp_path: Path) -> None:
    _seed(tmp_path)
    agent_id = "codex_cli:semantic-alias-manifest-apply"
    lease_id = "lease-semantic-alias-manifest-apply"
    manifest_rel = (
        "ION/05_context/current/codex_agent_mounts/"
        "role_atlas__ion_vnext_front_door/ION_AGENT_MOUNT_MANIFEST.json"
    )
    projection_rel = "ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
    active_package_rel = (
        "ION/05_context/current/codex_agent_mounts/"
        "role_atlas__ion_vnext_front_door/.ion/ACTIVE_CONTEXT_PACKAGE.json"
    )
    _write_json(tmp_path, active_package_rel, {"domain_id": "ion_vnext_front_door", "package": "unchanged"})
    _seed_apply_lease(tmp_path, agent_id=agent_id, lease_id=lease_id, target_paths=[manifest_rel])
    candidate = build_semantic_alias_mount_manifest_rewrite_candidate(
        tmp_path,
        generated_at="2026-06-04T07:10:00Z",
    )
    projection_before = (tmp_path / projection_rel).read_text(encoding="utf-8")
    active_package_before = (tmp_path / active_package_rel).read_text(encoding="utf-8")
    apply_args = {
        "confirmation": BOUNDED_WRITE_CONFIRMATION,
        "manifest_write_confirmation": SEMANTIC_ALIAS_MANIFEST_WRITE_CONFIRMATION,
        "idempotency_key": "semantic-alias-manifest-happy-path",
        "agent_id": agent_id,
        "lease_id": lease_id,
        "before_sha256": candidate["target"]["before_sha256"],
        "replacement_body_sha256": candidate["target"]["candidate_body_sha256"],
        "execute_write": True,
        "generated_at": "2026-06-04T07:11:00Z",
    }

    applied = apply_semantic_alias_mount_manifest_rewrite(tmp_path, **apply_args)
    replayed = apply_semantic_alias_mount_manifest_rewrite(
        tmp_path,
        **{**apply_args, "generated_at": "2026-06-04T07:12:00Z"},
    )
    conflict = apply_semantic_alias_mount_manifest_rewrite(
        tmp_path,
        **{
            **apply_args,
            "replacement_body_sha256": "2" * 64,
            "generated_at": "2026-06-04T07:13:00Z",
        },
    )

    assert applied["ok"] is True
    assert applied["status"] == "semantic_alias_mount_manifest_apply_applied"
    assert applied["projection_overwrite_performed"] is False
    assert applied["mount_manifest_write_performed"] is True
    assert applied["active_context_package_refresh_performed"] is False
    assert applied["accepted_state_claim"] is True
    assert applied["production_authority"] is False
    assert applied["live_execution_authority"] is False
    assert applied["secrets_authority"] is False
    assert applied["materialization_authority"] is False
    manifest = json.loads((tmp_path / manifest_rel).read_text(encoding="utf-8"))
    assert manifest == candidate["candidate_body"]
    assert (tmp_path / manifest_rel).read_text(encoding="utf-8") == json_write_text(candidate["candidate_body"])
    assert (tmp_path / projection_rel).read_text(encoding="utf-8") == projection_before
    assert (tmp_path / active_package_rel).read_text(encoding="utf-8") == active_package_before
    receipt_path = tmp_path / applied["receipt_path"]
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["schema_id"] == "ion.domain_weaver.semantic_alias.mount_manifest_apply_receipt.v0_1"
    assert receipt["target"]["path"] == manifest_rel
    assert receipt["write_set"] == [manifest_rel, applied["receipt_path"]]
    assert receipt["rewrite_summary"]["projection_rewrite_included"] is False
    assert receipt["rewrite_summary"]["active_context_package_refresh_included"] is False
    assert replayed["ok"] is True
    assert replayed["idempotent_replay"] is True
    assert replayed["mutates_active_state"] is False
    assert conflict["ok"] is False
    assert "semantic_alias_mount_manifest_apply_idempotency_conflict" in conflict["blockers"]
