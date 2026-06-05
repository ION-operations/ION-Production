"""Candidate semantic-alias canonicalization for Domain Weaver."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from .ion_domain_weaver_semantic_ids import (
    VNEXT_FRONT_DOOR_ALIASES,
    VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID,
)

SCHEMA_ID = "ion.domain_weaver.semantic_alias_canonicalization.v0_1_candidate"
WRITE_RESULT_SCHEMA_ID = "ion.domain_weaver.semantic_alias_canonicalization.write_result.v0_1"
PROJECTION_REWRITE_CANDIDATE_SCHEMA_ID = (
    "ion.domain_weaver.semantic_alias.projection_rewrite_candidate.v0_1_candidate"
)
PROJECTION_APPLY_SCHEMA_ID = "ion.domain_weaver.semantic_alias.projection_apply.v0_1_candidate"
PROJECTION_APPLY_RECEIPT_SCHEMA_ID = "ion.domain_weaver.semantic_alias.projection_apply_receipt.v0_1"
MOUNT_MANIFEST_REWRITE_CANDIDATE_SCHEMA_ID = (
    "ion.domain_weaver.semantic_alias.mount_manifest_rewrite_candidate.v0_1_candidate"
)
MOUNT_MANIFEST_APPLY_SCHEMA_ID = "ion.domain_weaver.semantic_alias.mount_manifest_apply.v0_1_candidate"
MOUNT_MANIFEST_APPLY_RECEIPT_SCHEMA_ID = "ion.domain_weaver.semantic_alias.mount_manifest_apply_receipt.v0_1"
SUPERVISED_APPLY_PREFLIGHT_SCHEMA_ID = (
    "ion.domain_weaver.semantic_alias.supervised_apply_preflight.v0_1_candidate"
)
SUPERVISED_APPLY_PREFLIGHT_WRITE_RESULT_SCHEMA_ID = (
    "ion.domain_weaver.semantic_alias.supervised_apply_preflight.write_result.v0_1"
)
BOUNDED_WRITE_CONFIRMATION = "ION_BOUNDED_WRITE_CONFIRMED"
SEMANTIC_ALIAS_ACCEPTED_WRITE_CONFIRMATION = "ION_DOMAIN_WEAVER_SEMANTIC_ALIAS_ACCEPTED_WRITE_CONFIRMED"
SEMANTIC_ALIAS_MANIFEST_WRITE_CONFIRMATION = "ION_DOMAIN_WEAVER_SEMANTIC_ALIAS_MANIFEST_WRITE_CONFIRMED"

DEFAULT_CONTEXT_ROOT = Path("ION/05_context/current/domain_weaver")
DEFAULT_OUTPUT_DIR = DEFAULT_CONTEXT_ROOT / "semantic_alias_canonicalization"
DEFAULT_OPERATOR_ACTION_DIR = DEFAULT_CONTEXT_ROOT / "operator_actions"
DEFAULT_PROJECTION_PATH = DEFAULT_CONTEXT_ROOT / "DOMAIN_WEAVER_PROJECTION.json"
DEFAULT_PROMOTION_REVIEW_PATH = DEFAULT_CONTEXT_ROOT / "PROMOTION_REVIEW.json"
DEFAULT_PROMOTION_GATE_PATH = DEFAULT_CONTEXT_ROOT / "PROMOTION_GATE.json"
DEFAULT_MOUNT_ROOT = Path("ION/05_context/current/codex_agent_mounts")
DEFAULT_MANIFEST_ALIAS_TARGET_PATH = (
    DEFAULT_MOUNT_ROOT
    / "role_atlas__ion_vnext_front_door"
    / "ION_AGENT_MOUNT_MANIFEST.json"
)
DEFAULT_ACCEPTED_APPLY_RECEIPT_DIR = DEFAULT_OUTPUT_DIR / "accepted_apply_receipts"
DEFAULT_MANIFEST_ACCEPTED_APPLY_RECEIPT_DIR = DEFAULT_OUTPUT_DIR / "manifest_apply_receipts"
DEFAULT_JSON_NAME = "DOMAIN_WEAVER_SEMANTIC_ALIAS_CANONICALIZATION.latest.candidate.json"
DEFAULT_REPORT_NAME = "DOMAIN_WEAVER_SEMANTIC_ALIAS_CANONICALIZATION.latest.md"
DEFAULT_PROJECTION_REWRITE_CANDIDATE_NAME = "DOMAIN_WEAVER_SEMANTIC_ALIAS_PROJECTION_REWRITE_CANDIDATE.latest.json"
DEFAULT_PROJECTION_REWRITE_CANDIDATE_REPORT_NAME = "DOMAIN_WEAVER_SEMANTIC_ALIAS_PROJECTION_REWRITE_CANDIDATE.latest.md"
DEFAULT_MOUNT_MANIFEST_REWRITE_CANDIDATE_NAME = "DOMAIN_WEAVER_SEMANTIC_ALIAS_MOUNT_MANIFEST_REWRITE_CANDIDATE.latest.json"
DEFAULT_MOUNT_MANIFEST_REWRITE_CANDIDATE_REPORT_NAME = "DOMAIN_WEAVER_SEMANTIC_ALIAS_MOUNT_MANIFEST_REWRITE_CANDIDATE.latest.md"
DEFAULT_SUPERVISED_APPLY_PREFLIGHT_NAME = "DOMAIN_WEAVER_SEMANTIC_ALIAS_SUPERVISED_APPLY_PREFLIGHT.latest.json"
DEFAULT_SUPERVISED_APPLY_PREFLIGHT_REPORT_NAME = "DOMAIN_WEAVER_SEMANTIC_ALIAS_SUPERVISED_APPLY_PREFLIGHT.latest.md"

AUTHORITY = {
    "candidate_context_only": True,
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "projection_overwrite_performed": False,
    "registry_write_performed": False,
    "mount_write_performed": False,
}


def build_semantic_alias_canonicalization_candidate(active_root: str | Path, *, generated_at: str | None = None) -> dict[str, Any]:
    root = Path(active_root).expanduser().resolve(strict=False)
    generated = generated_at or utc_now()
    projection = read_json(root / DEFAULT_PROJECTION_PATH)
    promotion_review = read_json(root / DEFAULT_PROMOTION_REVIEW_PATH)
    promotion_gate = read_json(root / DEFAULT_PROMOTION_GATE_PATH)
    promotion_rows = promotion_evidence(promotion_review, promotion_gate)
    observed_aliases = observe_aliases(root, projection)
    candidate_map = {
        "canonical_id": VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID,
        "aliases": list(VNEXT_FRONT_DOOR_ALIASES),
        "promotion_evidence": promotion_rows,
        "observed_aliases": observed_aliases,
    }
    blockers = []
    if observed_aliases:
        blockers.append("semantic_alias_references_require_candidate_rewrite_review")
    if not any(row.get("proposed_active_domain_id") == VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID for row in promotion_rows):
        blockers.append("promotion_evidence_for_canonical_id_missing")
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "authority": dict(AUTHORITY),
        "candidate_map": candidate_map,
        "would_change_refs": would_change_refs(observed_aliases),
        "context_graph_deltas": {
            "write_performed": False,
            "accepted_state_moved": False,
            "upsert_claims": [
                {
                    "id": "domain_weaver.semantic_branch_identity.vnext_front_door",
                    "state": "canonicalization_candidate_ready_not_applied",
                    "value": {
                        "canonical": VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID,
                        "aliases": list(VNEXT_FRONT_DOOR_ALIASES),
                    },
                }
            ],
            "emit_edges": [
                {
                    "from": "domain_weaver.semantic_branch_identity.vnext_front_door",
                    "relation": "requires_candidate_review_before",
                    "to": "domain_weaver.self_evolution.semantic_branch_fabric",
                }
            ],
        },
        "blockers": blockers,
        "next_packet": "PCKT-DOMAIN-WEAVER-SEMANTIC-ALIAS-CANONICALIZATION-APPLY-GATE-V0_1",
        "non_claims": [
            "This artifact does not rewrite DOMAIN_WEAVER_PROJECTION.json.",
            "This artifact does not write registry domain files or mount manifests.",
            "Candidate aliases are not accepted state.",
        ],
        "verdict": "SEMANTIC_ALIAS_CANONICALIZATION_CANDIDATE_READY_NOT_APPLIED",
    }


def write_semantic_alias_canonicalization_candidate(active_root: str | Path, *, generated_at: str | None = None) -> dict[str, Any]:
    root = Path(active_root).expanduser().resolve(strict=False)
    payload = build_semantic_alias_canonicalization_candidate(root, generated_at=generated_at)
    stamp = timestamp_for_filename(str(payload["generated_at"]))
    output_dir = root / DEFAULT_OUTPUT_DIR
    receipt_dir = root / DEFAULT_OPERATOR_ACTION_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    receipt_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / DEFAULT_JSON_NAME
    report_path = output_dir / DEFAULT_REPORT_NAME
    receipt_path = receipt_dir / f"{stamp}_domain_weaver_semantic_alias_canonicalization_candidate.json"
    write_json(json_path, payload)
    write_text(report_path, render_report(payload))
    receipt = {
        "schema_id": "ion.domain_weaver.operator_action_receipt.v0_1",
        "receipt_type": "domain_weaver_semantic_alias_canonicalization_candidate",
        "generated_at": payload["generated_at"],
        "result": "semantic_alias_canonicalization_candidate_written_no_state_movement",
        "active_root": str(root),
        "artifacts": {
            "candidate_json": rel(json_path, root),
            "candidate_report": rel(report_path, root),
        },
        "authority": dict(AUTHORITY),
        "blockers": payload["blockers"],
        "validation": [],
    }
    write_json(receipt_path, receipt)
    return {
        "schema_id": WRITE_RESULT_SCHEMA_ID,
        "generated_at": payload["generated_at"],
        "json_path": rel(json_path, root),
        "report_path": rel(report_path, root),
        "operator_receipt_path": rel(receipt_path, root),
        "mutates_active_state": False,
        "accepted_state_moved": False,
        "authority": dict(AUTHORITY),
    }


def build_semantic_alias_projection_rewrite_candidate(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    root = Path(active_root).expanduser().resolve(strict=False)
    generated = generated_at or utc_now()
    projection_path = root / DEFAULT_PROJECTION_PATH
    projection = read_json(projection_path)
    if not projection:
        return {
            "schema_id": PROJECTION_REWRITE_CANDIDATE_SCHEMA_ID,
            "generated_at": generated,
            "active_root": str(root),
            "ok": False,
            "status": "source_projection_missing",
            "target": {
                "path": DEFAULT_PROJECTION_PATH.as_posix(),
                "exists": projection_path.is_file(),
                "before_sha256": sha256_file(projection_path),
                "candidate_body_sha256": None,
                "write_performed": False,
            },
            "candidate_body": None,
            "rewrite_summary": {},
            "blockers": ["semantic_alias_projection_source_missing"],
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "authority": dict(AUTHORITY),
        }

    candidate_body, rewrite_rows = rewrite_alias_values(projection)
    observed_after = observe_projection_alias_values(candidate_body)
    candidate_sha = sha256_text(json_write_text(candidate_body))
    blockers: list[str] = []
    if observed_after:
        blockers.append("semantic_alias_projection_alias_values_remain_after_candidate_rewrite")
    if not rewrite_rows:
        blockers.append("semantic_alias_projection_rewrite_no_alias_values_found")
    return {
        "schema_id": PROJECTION_REWRITE_CANDIDATE_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "ok": not observed_after and bool(rewrite_rows),
        "status": "semantic_alias_projection_rewrite_candidate_built",
        "target": {
            "path": DEFAULT_PROJECTION_PATH.as_posix(),
            "exists": projection_path.is_file(),
            "before_sha256": sha256_file(projection_path),
            "candidate_body_sha256": candidate_sha,
            "candidate_body_sha256_semantics": "sha256_of_exact_pretty_json_utf8_bytes_to_write",
            "write_performed": False,
        },
        "candidate_body": candidate_body,
        "rewrite_summary": {
            "canonical_id": VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID,
            "rewritten_value_count": len(rewrite_rows),
            "rewrite_rows": rewrite_rows,
            "remaining_alias_value_count": len(observed_after),
            "remaining_alias_values": observed_after,
            "projection_only": True,
            "mount_manifest_rewrite_included": False,
        },
        "blockers": blockers,
        "mutates_active_state": False,
        "accepted_state_claim": False,
        "projection_overwrite_performed": False,
        "authority": dict(AUTHORITY),
        "non_claims": [
            "This artifact does not rewrite DOMAIN_WEAVER_PROJECTION.json.",
            "It rewrites exact JSON string values only in the candidate body.",
            "It does not rewrite mount manifests, registry files, receipts, queues, topology, UI, production, live, secrets, or git state.",
        ],
    }


def build_semantic_alias_mount_manifest_rewrite_candidate(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    root = Path(active_root).expanduser().resolve(strict=False)
    generated = generated_at or utc_now()
    manifest_path = root / DEFAULT_MANIFEST_ALIAS_TARGET_PATH
    manifest = read_json(manifest_path)
    if not manifest:
        return {
            "schema_id": MOUNT_MANIFEST_REWRITE_CANDIDATE_SCHEMA_ID,
            "generated_at": generated,
            "active_root": str(root),
            "ok": False,
            "status": "source_mount_manifest_missing",
            "target": {
                "path": DEFAULT_MANIFEST_ALIAS_TARGET_PATH.as_posix(),
                "exists": manifest_path.is_file(),
                "before_sha256": sha256_file(manifest_path),
                "candidate_body_sha256": None,
                "write_performed": False,
            },
            "candidate_body": None,
            "rewrite_summary": {},
            "blockers": ["semantic_alias_mount_manifest_source_missing"],
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "authority": dict(AUTHORITY),
        }

    candidate_body, rewrite_rows = rewrite_manifest_alias_fields(manifest)
    observed_after = observe_manifest_alias_fields(candidate_body)
    candidate_sha = sha256_text(json_write_text(candidate_body))
    blockers: list[str] = []
    if observed_after:
        blockers.append("semantic_alias_mount_manifest_alias_fields_remain_after_candidate_rewrite")
    if not rewrite_rows:
        blockers.append("semantic_alias_mount_manifest_rewrite_no_alias_fields_found")
    return {
        "schema_id": MOUNT_MANIFEST_REWRITE_CANDIDATE_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "ok": not observed_after and bool(rewrite_rows),
        "status": "semantic_alias_mount_manifest_rewrite_candidate_built",
        "target": {
            "path": DEFAULT_MANIFEST_ALIAS_TARGET_PATH.as_posix(),
            "exists": manifest_path.is_file(),
            "before_sha256": sha256_file(manifest_path),
            "candidate_body_sha256": candidate_sha,
            "candidate_body_sha256_semantics": "sha256_of_exact_pretty_json_utf8_bytes_to_write",
            "write_performed": False,
        },
        "candidate_body": candidate_body,
        "rewrite_summary": {
            "canonical_id": VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID,
            "rewritten_field_count": len(rewrite_rows),
            "rewrite_rows": rewrite_rows,
            "remaining_alias_field_count": len(observed_after),
            "remaining_alias_fields": observed_after,
            "mount_manifest_only": True,
            "projection_rewrite_included": False,
            "active_context_package_refresh_included": False,
        },
        "blockers": blockers,
        "mutates_active_state": False,
        "accepted_state_claim": False,
        "projection_overwrite_performed": False,
        "mount_manifest_write_performed": False,
        "authority": dict(AUTHORITY),
        "non_claims": [
            "This artifact does not rewrite ION_AGENT_MOUNT_MANIFEST.json.",
            "It rewrites only exact top-level domain_id/domain alias values in the candidate body.",
            "It does not rewrite DOMAIN_WEAVER_PROJECTION.json, active context packages, registry files, receipts, queues, topology, UI, production, live, secrets, materialization, workers, or git state.",
        ],
    }


def build_semantic_alias_supervised_apply_preflight(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
    agent_id: str = "codex_cli:semantic-alias-supervised-apply",
    lease_id: str = "<live-exclusive-write-lease-id-covering-semantic-alias-targets>",
    idempotency_prefix: str = "semantic-alias-supervised-apply",
    include_candidate_bodies: bool = False,
) -> dict[str, Any]:
    root = Path(active_root).expanduser().resolve(strict=False)
    generated = generated_at or utc_now()
    projection_candidate = build_semantic_alias_projection_rewrite_candidate(root, generated_at=generated)
    manifest_candidate = build_semantic_alias_mount_manifest_rewrite_candidate(root, generated_at=generated)
    projection_target = mapping(projection_candidate.get("target"))
    manifest_target = mapping(manifest_candidate.get("target"))
    normalized_agent = str(agent_id or "").strip() or "codex_cli:semantic-alias-supervised-apply"
    normalized_lease = str(lease_id or "").strip() or "<live-exclusive-write-lease-id-covering-semantic-alias-targets>"
    normalized_prefix = str(idempotency_prefix or "").strip() or "semantic-alias-supervised-apply"
    projection_idempotency = stable_preflight_idempotency_key(
        normalized_prefix,
        "projection",
        projection_target.get("before_sha256"),
        projection_target.get("candidate_body_sha256"),
    )
    manifest_idempotency = stable_preflight_idempotency_key(
        normalized_prefix,
        "manifest",
        manifest_target.get("before_sha256"),
        manifest_target.get("candidate_body_sha256"),
    )
    projection_target_path = DEFAULT_PROJECTION_PATH.as_posix()
    manifest_target_path = DEFAULT_MANIFEST_ALIAS_TARGET_PATH.as_posix()
    write_sequence = [
        {
            "order": 1,
            "branch_id": "domain_weaver_agents",
            "route_id": "semantic_alias_projection_apply",
            "target_path": projection_target_path,
            "required_live_exclusive_write_lease_target": projection_target_path,
            "route_call_args_template": {
                "execute_write": True,
                "before_sha256": projection_target.get("before_sha256"),
                "replacement_body_sha256": projection_target.get("candidate_body_sha256"),
                "semantic_alias_write_confirmation": SEMANTIC_ALIAS_ACCEPTED_WRITE_CONFIRMATION,
                "idempotency_key": projection_idempotency,
                "confirmation": BOUNDED_WRITE_CONFIRMATION,
                "agent_id": normalized_agent,
                "lease_id": normalized_lease,
            },
            "candidate_ok": bool(projection_candidate.get("ok")),
            "candidate_blockers": list(projection_candidate.get("blockers") or []),
            "writes_only": [
                projection_target_path,
                "ION/05_context/current/domain_weaver/semantic_alias_canonicalization/accepted_apply_receipts/<idempotency_key>.json",
            ],
        },
        {
            "order": 2,
            "branch_id": "domain_weaver_agents",
            "route_id": "semantic_alias_mount_manifest_apply",
            "target_path": manifest_target_path,
            "required_live_exclusive_write_lease_target": manifest_target_path,
            "route_call_args_template": {
                "execute_write": True,
                "before_sha256": manifest_target.get("before_sha256"),
                "replacement_body_sha256": manifest_target.get("candidate_body_sha256"),
                "manifest_write_confirmation": SEMANTIC_ALIAS_MANIFEST_WRITE_CONFIRMATION,
                "idempotency_key": manifest_idempotency,
                "confirmation": BOUNDED_WRITE_CONFIRMATION,
                "agent_id": normalized_agent,
                "lease_id": normalized_lease,
            },
            "candidate_ok": bool(manifest_candidate.get("ok")),
            "candidate_blockers": list(manifest_candidate.get("blockers") or []),
            "writes_only": [
                manifest_target_path,
                "ION/05_context/current/domain_weaver/semantic_alias_canonicalization/manifest_apply_receipts/<idempotency_key>.json",
            ],
        },
    ]
    blockers: list[str] = []
    if not projection_candidate.get("ok"):
        blockers.append("semantic_alias_projection_candidate_not_apply_ready")
        blockers.extend(projection_candidate.get("blockers") or [])
    if not manifest_candidate.get("ok"):
        blockers.append("semantic_alias_mount_manifest_candidate_not_apply_ready")
        blockers.extend(manifest_candidate.get("blockers") or [])
    if not projection_target.get("candidate_body_sha256"):
        blockers.append("semantic_alias_projection_candidate_body_sha_missing")
    if not manifest_target.get("candidate_body_sha256"):
        blockers.append("semantic_alias_mount_manifest_candidate_body_sha_missing")
    blockers = unique_texts(blockers)
    return {
        "schema_id": SUPERVISED_APPLY_PREFLIGHT_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "ok": not blockers,
        "status": (
            "semantic_alias_supervised_apply_preflight_ready"
            if not blockers
            else "semantic_alias_supervised_apply_preflight_blocked"
        ),
        "targets": {
            "projection": {
                "path": projection_target_path,
                "exists": bool(projection_target.get("exists")),
                "before_sha256": projection_target.get("before_sha256"),
                "candidate_body_sha256": projection_target.get("candidate_body_sha256"),
            },
            "mount_manifest": {
                "path": manifest_target_path,
                "exists": bool(manifest_target.get("exists")),
                "before_sha256": manifest_target.get("before_sha256"),
                "candidate_body_sha256": manifest_target.get("candidate_body_sha256"),
            },
        },
        "candidate_summaries": {
            "projection": redact_candidate_body(projection_candidate, include_candidate_bodies=include_candidate_bodies),
            "mount_manifest": redact_candidate_body(manifest_candidate, include_candidate_bodies=include_candidate_bodies),
        },
        "write_sequence": write_sequence,
        "required_combined_lease_targets": [projection_target_path, manifest_target_path],
        "required_operator_decision": "explicit accepted-state semantic alias apply decision plus live exclusive edit lease",
        "current_run_authority": {
            "candidate_context_only": True,
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
            "materialization_authority": False,
        },
        "active_root_apply_invoked": False,
        "projection_overwrite_performed": False,
        "mount_manifest_write_performed": False,
        "active_context_package_refresh_performed": False,
        "mutates_active_state": False,
        "accepted_state_claim": False,
        "blockers": blockers,
        "context_graph_deltas": {
            "write_performed": False,
            "accepted_state_moved": False,
            "upsert_claims": [
                {
                    "id": "domain_weaver.semantic_alias.supervised_apply_preflight",
                    "state": "candidate_preflight_ready_not_invoked" if not blockers else "candidate_preflight_blocked",
                    "value": {
                        "projection_candidate_body_sha256": projection_target.get("candidate_body_sha256"),
                        "mount_manifest_candidate_body_sha256": manifest_target.get("candidate_body_sha256"),
                        "write_sequence_length": len(write_sequence),
                    },
                }
            ],
        },
        "next_packet": "DW-SPW-013 semantic alias accepted-state apply decision or active-context refresh preflight after alias application",
        "non_claims": [
            "This preflight does not invoke semantic_alias_projection_apply or semantic_alias_mount_manifest_apply.",
            "It does not write DOMAIN_WEAVER_PROJECTION.json or ION_AGENT_MOUNT_MANIFEST.json.",
            "It does not refresh active context packages, registries, receipts history, queues, workers, topology, UI, production, live, secrets, materialization, or git state.",
            "Route-call templates are inert until an accepted-state authority decision, idempotency key, actor identity, and live exclusive edit lease are supplied to the mutating routes.",
        ],
    }


def write_semantic_alias_supervised_apply_preflight(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
    agent_id: str = "codex_cli:semantic-alias-supervised-apply",
    lease_id: str = "<live-exclusive-write-lease-id-covering-semantic-alias-targets>",
    idempotency_prefix: str = "semantic-alias-supervised-apply",
    include_candidate_bodies: bool = False,
) -> dict[str, Any]:
    """Write current semantic-alias supervised apply preflight evidence only."""

    root = Path(active_root).expanduser().resolve(strict=False)
    generated = generated_at or utc_now()
    output_dir = root / DEFAULT_OUTPUT_DIR
    receipt_dir = root / DEFAULT_OPERATOR_ACTION_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    receipt_dir.mkdir(parents=True, exist_ok=True)
    stamp = timestamp_for_filename(generated)

    previous_preflight_path = output_dir / DEFAULT_SUPERVISED_APPLY_PREFLIGHT_NAME
    previous_preflight = read_json(previous_preflight_path)
    previous_projection_before_sha256 = str(
        mapping(mapping(previous_preflight.get("targets")).get("projection")).get("before_sha256") or ""
    )

    projection_candidate = build_semantic_alias_projection_rewrite_candidate(root, generated_at=generated)
    manifest_candidate = build_semantic_alias_mount_manifest_rewrite_candidate(root, generated_at=generated)
    preflight = build_semantic_alias_supervised_apply_preflight(
        root,
        generated_at=generated,
        agent_id=agent_id,
        lease_id=lease_id,
        idempotency_prefix=idempotency_prefix,
        include_candidate_bodies=include_candidate_bodies,
    )
    current_projection_before_sha256 = str(
        mapping(mapping(preflight.get("targets")).get("projection")).get("before_sha256") or ""
    )
    previous_stale = bool(
        previous_preflight_path.is_file()
        and previous_projection_before_sha256
        and previous_projection_before_sha256 != current_projection_before_sha256
    )
    previous_currentness = {
        "path": rel(previous_preflight_path, root),
        "exists": previous_preflight_path.is_file(),
        "schema_id": previous_preflight.get("schema_id"),
        "generated_at": previous_preflight.get("generated_at"),
        "projection_before_sha256": previous_projection_before_sha256,
        "stale_against_current_projection_sha": previous_stale,
    }
    preflight["previous_preflight_currentness"] = previous_currentness
    preflight["current_projection_before_sha256"] = current_projection_before_sha256
    preflight["current_projection_target_current"] = current_projection_before_sha256 == str(
        sha256_file(root / DEFAULT_PROJECTION_PATH) or ""
    )

    projection_json_path = output_dir / DEFAULT_PROJECTION_REWRITE_CANDIDATE_NAME
    projection_report_path = output_dir / DEFAULT_PROJECTION_REWRITE_CANDIDATE_REPORT_NAME
    projection_snapshot_json_path = output_dir / f"{stamp}_semantic_alias_projection_rewrite_candidate.json"
    projection_snapshot_report_path = output_dir / f"{stamp}_semantic_alias_projection_rewrite_candidate.md"
    manifest_json_path = output_dir / DEFAULT_MOUNT_MANIFEST_REWRITE_CANDIDATE_NAME
    manifest_report_path = output_dir / DEFAULT_MOUNT_MANIFEST_REWRITE_CANDIDATE_REPORT_NAME
    manifest_snapshot_json_path = output_dir / f"{stamp}_semantic_alias_mount_manifest_rewrite_candidate.json"
    manifest_snapshot_report_path = output_dir / f"{stamp}_semantic_alias_mount_manifest_rewrite_candidate.md"
    preflight_json_path = output_dir / DEFAULT_SUPERVISED_APPLY_PREFLIGHT_NAME
    preflight_report_path = output_dir / DEFAULT_SUPERVISED_APPLY_PREFLIGHT_REPORT_NAME
    preflight_snapshot_json_path = output_dir / f"{stamp}_semantic_alias_supervised_apply_preflight.json"
    preflight_snapshot_report_path = output_dir / f"{stamp}_semantic_alias_supervised_apply_preflight.md"
    receipt_path = receipt_dir / f"{stamp}_domain_weaver_semantic_alias_supervised_apply_preflight.json"

    artifacts = {
        "projection_rewrite_candidate": rel(projection_json_path, root),
        "projection_rewrite_candidate_report": rel(projection_report_path, root),
        "projection_rewrite_candidate_snapshot": rel(projection_snapshot_json_path, root),
        "projection_rewrite_candidate_snapshot_report": rel(projection_snapshot_report_path, root),
        "mount_manifest_rewrite_candidate": rel(manifest_json_path, root),
        "mount_manifest_rewrite_candidate_report": rel(manifest_report_path, root),
        "mount_manifest_rewrite_candidate_snapshot": rel(manifest_snapshot_json_path, root),
        "mount_manifest_rewrite_candidate_snapshot_report": rel(manifest_snapshot_report_path, root),
        "supervised_apply_preflight": rel(preflight_json_path, root),
        "supervised_apply_preflight_report": rel(preflight_report_path, root),
        "supervised_apply_preflight_snapshot": rel(preflight_snapshot_json_path, root),
        "supervised_apply_preflight_snapshot_report": rel(preflight_snapshot_report_path, root),
    }
    preflight["artifacts"] = artifacts

    write_json(projection_json_path, projection_candidate)
    write_json(projection_snapshot_json_path, projection_candidate)
    write_text(projection_report_path, render_semantic_alias_rewrite_candidate_report(projection_candidate, title="Projection Rewrite Candidate"))
    write_text(projection_snapshot_report_path, render_semantic_alias_rewrite_candidate_report(projection_candidate, title="Projection Rewrite Candidate"))
    write_json(manifest_json_path, manifest_candidate)
    write_json(manifest_snapshot_json_path, manifest_candidate)
    write_text(manifest_report_path, render_semantic_alias_rewrite_candidate_report(manifest_candidate, title="Mount Manifest Rewrite Candidate"))
    write_text(manifest_snapshot_report_path, render_semantic_alias_rewrite_candidate_report(manifest_candidate, title="Mount Manifest Rewrite Candidate"))
    write_json(preflight_json_path, preflight)
    write_json(preflight_snapshot_json_path, preflight)
    write_text(preflight_report_path, render_semantic_alias_supervised_apply_preflight_report(preflight))
    write_text(preflight_snapshot_report_path, render_semantic_alias_supervised_apply_preflight_report(preflight))

    receipt = {
        "schema_id": "ion.domain_weaver.operator_action_receipt.v0_1",
        "receipt_type": "domain_weaver_semantic_alias_supervised_apply_preflight",
        "generated_at": generated,
        "result": "semantic_alias_supervised_apply_preflight_written_no_state_movement",
        "active_root": str(root),
        "artifacts": artifacts,
        "targets": preflight.get("targets"),
        "previous_preflight_currentness": previous_currentness,
        "authority": dict(AUTHORITY),
        "active_root_apply_invoked": False,
        "projection_overwrite_performed": False,
        "mount_manifest_write_performed": False,
        "mutates_active_state": False,
        "accepted_state_claim": False,
        "blockers": preflight.get("blockers"),
        "validation": [],
    }
    write_json(receipt_path, receipt)

    return {
        "schema_id": SUPERVISED_APPLY_PREFLIGHT_WRITE_RESULT_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "json_path": rel(preflight_json_path, root),
        "report_path": rel(preflight_report_path, root),
        "snapshot_json_path": rel(preflight_snapshot_json_path, root),
        "snapshot_report_path": rel(preflight_snapshot_report_path, root),
        "projection_rewrite_candidate_path": rel(projection_json_path, root),
        "mount_manifest_rewrite_candidate_path": rel(manifest_json_path, root),
        "operator_receipt_path": rel(receipt_path, root),
        "previous_preflight_stale_against_current_projection_sha": previous_stale,
        "current_projection_target_current": preflight["current_projection_target_current"],
        "active_root_apply_invoked": False,
        "projection_overwrite_performed": False,
        "mount_manifest_write_performed": False,
        "mutates_active_state": False,
        "accepted_state_claim": False,
        "authority": dict(AUTHORITY),
    }


def apply_semantic_alias_mount_manifest_rewrite(
    active_root: str | Path,
    *,
    confirmation: str,
    manifest_write_confirmation: str,
    idempotency_key: str,
    agent_id: str,
    lease_id: str,
    before_sha256: str,
    replacement_body_sha256: str,
    execute_write: bool = False,
    generated_at: str | None = None,
) -> dict[str, Any]:
    root = Path(active_root).expanduser().resolve(strict=False)
    generated = generated_at or utc_now()
    target_rel = DEFAULT_MANIFEST_ALIAS_TARGET_PATH.as_posix()
    target_path = root / DEFAULT_MANIFEST_ALIAS_TARGET_PATH
    receipt_path = semantic_alias_manifest_apply_receipt_path(root, idempotency_key)
    candidate = build_semantic_alias_mount_manifest_rewrite_candidate(root, generated_at=generated)
    candidate_body = candidate.get("candidate_body") if isinstance(candidate.get("candidate_body"), Mapping) else None
    candidate_sha = mapping(candidate.get("target")).get("candidate_body_sha256")
    current_sha = sha256_file(target_path)
    receipt = read_json(receipt_path)
    receipt_target = mapping(receipt.get("target"))
    existing_receipt_matches = (
        bool(receipt)
        and receipt.get("idempotency_key") == str(idempotency_key or "").strip()
        and receipt_target.get("path") == target_rel
        and receipt_target.get("before_sha256") == str(before_sha256 or "").strip()
        and receipt_target.get("after_sha256") == str(replacement_body_sha256 or "").strip()
        and receipt.get("replacement_body_sha256") == str(replacement_body_sha256 or "").strip()
    )
    gate = semantic_alias_live_lease_gate(
        root,
        agent_id=str(agent_id or "").strip(),
        lease_id=str(lease_id or "").strip(),
        target_paths=[target_rel],
        blocker_prefix="semantic_alias_mount_manifest_apply",
    )
    blockers: list[str] = list(candidate.get("blockers") or [])
    if confirmation != BOUNDED_WRITE_CONFIRMATION:
        blockers.append("semantic_alias_mount_manifest_apply_bounded_write_confirmation_required")
    if manifest_write_confirmation != SEMANTIC_ALIAS_MANIFEST_WRITE_CONFIRMATION:
        blockers.append("semantic_alias_mount_manifest_apply_manifest_write_confirmation_required")
    if not str(idempotency_key or "").strip():
        blockers.append("semantic_alias_mount_manifest_apply_idempotency_key_required")
    if identity_is_unbound(agent_id):
        blockers.append("semantic_alias_mount_manifest_apply_actor_identity_required")
    if not str(lease_id or "").strip():
        blockers.append("semantic_alias_mount_manifest_apply_lease_id_required")
    if not execute_write:
        blockers.append("semantic_alias_mount_manifest_apply_execute_write_required")
    if not target_path.is_file():
        blockers.append("semantic_alias_mount_manifest_apply_target_missing")
    if not str(before_sha256 or "").strip():
        blockers.append("semantic_alias_mount_manifest_apply_before_sha256_required")
    if not str(replacement_body_sha256 or "").strip():
        blockers.append("semantic_alias_mount_manifest_apply_replacement_body_sha256_required")
    if candidate_sha and str(replacement_body_sha256 or "").strip() != candidate_sha:
        blockers.append("semantic_alias_mount_manifest_apply_replacement_body_sha256_mismatch")
    if gate.get("ok") is not True:
        blockers.append("semantic_alias_mount_manifest_apply_live_exclusive_write_lease_required")
        blockers.extend(semantic_alias_live_lease_blockers(gate, prefix="semantic_alias_mount_manifest_apply"))
    if receipt:
        if not existing_receipt_matches:
            blockers.append("semantic_alias_mount_manifest_apply_idempotency_conflict")
        elif current_sha != receipt_target.get("after_sha256"):
            blockers.append("semantic_alias_mount_manifest_apply_idempotent_replay_target_sha_mismatch")
    elif current_sha != str(before_sha256 or "").strip():
        blockers.append("semantic_alias_mount_manifest_apply_before_sha256_mismatch")
    if existing_receipt_matches and current_sha == receipt_target.get("after_sha256"):
        blockers = [
            blocker
            for blocker in blockers
            if blocker not in {
                "semantic_alias_mount_manifest_rewrite_no_alias_fields_found",
                "semantic_alias_mount_manifest_alias_fields_remain_after_candidate_rewrite",
            }
        ]
    blockers = unique_texts(blockers)
    base = {
        "schema_id": MOUNT_MANIFEST_APPLY_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "target": {
            "path": target_rel,
            "exists": target_path.is_file(),
            "before_sha256": current_sha,
            "expected_before_sha256": str(before_sha256 or "").strip(),
            "after_sha256": candidate_sha,
            "write_performed": False,
        },
        "rewrite_summary": candidate.get("rewrite_summary"),
        "replacement_body_sha256": candidate_sha,
        "expected_replacement_body_sha256": str(replacement_body_sha256 or "").strip(),
        "replacement_body_sha256_semantics": "sha256_of_exact_pretty_json_utf8_bytes_to_write",
        "live_lease_gate": gate,
        "idempotency_key": str(idempotency_key or "").strip(),
        "agent_id": str(agent_id or "").strip(),
        "lease_id": str(lease_id or "").strip(),
        "execute_write": bool(execute_write),
        "projection_overwrite_performed": False,
        "accepted_projection_write_performed": False,
        "mount_manifest_write_performed": False,
        "active_context_package_refresh_performed": False,
        "mutates_active_state": False,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "materialization_authority": False,
        "authority": semantic_alias_manifest_apply_authority(False),
    }
    if blockers:
        return {
            **base,
            "ok": False,
            "status": "semantic_alias_mount_manifest_apply_blocked",
            "receipt_path": rel(receipt_path, root),
            "blockers": blockers,
            "next_action": "repair_semantic_alias_mount_manifest_apply_inputs",
        }
    if receipt and existing_receipt_matches:
        return {
            **base,
            "ok": True,
            "status": "semantic_alias_mount_manifest_apply_idempotent_replay",
            "idempotent_replay": True,
            "receipt_path": rel(receipt_path, root),
            "blockers": [],
            "next_action": "no_op_idempotent_replay_preserved",
        }

    assert candidate_body is not None
    before_row = file_digest_row(target_path)
    atomic_write_text(target_path, json_write_text(candidate_body))
    after_row = file_digest_row(target_path)
    receipt_payload = {
        "schema_id": MOUNT_MANIFEST_APPLY_RECEIPT_SCHEMA_ID,
        "generated_at": generated,
        "result": "semantic_alias_mount_manifest_rewrite_applied",
        "active_root": str(root),
        "agent_id": str(agent_id or "").strip(),
        "lease_id": str(lease_id or "").strip(),
        "idempotency_key": str(idempotency_key or "").strip(),
        "target": {
            "path": target_rel,
            "before_sha256": before_row.get("sha256"),
            "after_sha256": after_row.get("sha256"),
            "bytes": after_row.get("bytes"),
        },
        "replacement_body_sha256": candidate_sha,
        "rewrite_summary": candidate.get("rewrite_summary"),
        "live_lease_gate": gate,
        "write_set": [target_rel, rel(receipt_path, root)],
        "projection_overwrite_performed": False,
        "accepted_projection_write_performed": False,
        "mount_manifest_write_performed": True,
        "active_context_package_refresh_performed": False,
        "mutates_active_state": True,
        "accepted_state_claim": True,
        "accepted_state_scope": "domain_weaver_vnext_front_door_mount_manifest_alias_field_only",
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "materialization_authority": False,
        "authority": semantic_alias_manifest_apply_authority(True),
        "non_claims": [
            "This receipt proves only exact top-level semantic alias field rewrites in the vNext front-door generated mount manifest.",
            "It does not rewrite DOMAIN_WEAVER_PROJECTION.json, active context packages, registry files, receipts, queues, topology, UI, production, live, secrets, materialization, workers, or git state.",
        ],
    }
    write_json(receipt_path, receipt_payload)
    return {
        **base,
        "ok": True,
        "status": "semantic_alias_mount_manifest_apply_applied",
        "target": {
            **base["target"],
            "before": before_row,
            "after": after_row,
            "before_sha256": before_row.get("sha256"),
            "after_sha256": after_row.get("sha256"),
            "write_performed": True,
        },
        "receipt_path": rel(receipt_path, root),
        "mount_manifest_write_performed": True,
        "mutates_active_state": True,
        "accepted_state_claim": True,
        "accepted_state_scope": "domain_weaver_vnext_front_door_mount_manifest_alias_field_only",
        "authority": semantic_alias_manifest_apply_authority(True),
        "blockers": [],
        "next_action": "rerun_semantic_alias_manifest_and_context_mount_validation",
    }


def apply_semantic_alias_projection_rewrite(
    active_root: str | Path,
    *,
    confirmation: str,
    semantic_alias_write_confirmation: str,
    idempotency_key: str,
    agent_id: str,
    lease_id: str,
    before_sha256: str,
    replacement_body_sha256: str,
    execute_write: bool = False,
    generated_at: str | None = None,
) -> dict[str, Any]:
    root = Path(active_root).expanduser().resolve(strict=False)
    generated = generated_at or utc_now()
    target_rel = DEFAULT_PROJECTION_PATH.as_posix()
    target_path = root / DEFAULT_PROJECTION_PATH
    receipt_path = semantic_alias_apply_receipt_path(root, idempotency_key)
    candidate = build_semantic_alias_projection_rewrite_candidate(root, generated_at=generated)
    candidate_body = candidate.get("candidate_body") if isinstance(candidate.get("candidate_body"), Mapping) else None
    candidate_sha = mapping(candidate.get("target")).get("candidate_body_sha256")
    current_sha = sha256_file(target_path)
    receipt = read_json(receipt_path)
    receipt_target = mapping(receipt.get("target"))
    existing_receipt_matches = (
        bool(receipt)
        and receipt.get("idempotency_key") == str(idempotency_key or "").strip()
        and receipt_target.get("path") == target_rel
        and receipt_target.get("before_sha256") == str(before_sha256 or "").strip()
        and receipt_target.get("after_sha256") == str(replacement_body_sha256 or "").strip()
        and receipt.get("replacement_body_sha256") == str(replacement_body_sha256 or "").strip()
    )
    gate = semantic_alias_live_lease_gate(
        root,
        agent_id=str(agent_id or "").strip(),
        lease_id=str(lease_id or "").strip(),
        target_paths=[target_rel],
    )
    blockers: list[str] = list(candidate.get("blockers") or [])
    if confirmation != BOUNDED_WRITE_CONFIRMATION:
        blockers.append("semantic_alias_projection_apply_bounded_write_confirmation_required")
    if semantic_alias_write_confirmation != SEMANTIC_ALIAS_ACCEPTED_WRITE_CONFIRMATION:
        blockers.append("semantic_alias_projection_apply_accepted_write_confirmation_required")
    if not str(idempotency_key or "").strip():
        blockers.append("semantic_alias_projection_apply_idempotency_key_required")
    if identity_is_unbound(agent_id):
        blockers.append("semantic_alias_projection_apply_actor_identity_required")
    if not str(lease_id or "").strip():
        blockers.append("semantic_alias_projection_apply_lease_id_required")
    if not execute_write:
        blockers.append("semantic_alias_projection_apply_execute_write_required")
    if not target_path.is_file():
        blockers.append("semantic_alias_projection_apply_target_missing")
    if not str(before_sha256 or "").strip():
        blockers.append("semantic_alias_projection_apply_before_sha256_required")
    if not str(replacement_body_sha256 or "").strip():
        blockers.append("semantic_alias_projection_apply_replacement_body_sha256_required")
    if candidate_sha and str(replacement_body_sha256 or "").strip() != candidate_sha:
        blockers.append("semantic_alias_projection_apply_replacement_body_sha256_mismatch")
    if gate.get("ok") is not True:
        blockers.append("semantic_alias_projection_apply_live_exclusive_write_lease_required")
        blockers.extend(semantic_alias_live_lease_blockers(gate))
    if receipt:
        if not existing_receipt_matches:
            blockers.append("semantic_alias_projection_apply_idempotency_conflict")
        elif current_sha != receipt_target.get("after_sha256"):
            blockers.append("semantic_alias_projection_apply_idempotent_replay_target_sha_mismatch")
    elif current_sha != str(before_sha256 or "").strip():
        blockers.append("semantic_alias_projection_apply_before_sha256_mismatch")
    if existing_receipt_matches and current_sha == receipt_target.get("after_sha256"):
        blockers = [
            blocker
            for blocker in blockers
            if blocker not in {
                "semantic_alias_projection_rewrite_no_alias_values_found",
                "semantic_alias_projection_alias_values_remain_after_candidate_rewrite",
            }
        ]
    blockers = unique_texts(blockers)
    base = {
        "schema_id": PROJECTION_APPLY_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "target": {
            "path": target_rel,
            "exists": target_path.is_file(),
            "before_sha256": current_sha,
            "expected_before_sha256": str(before_sha256 or "").strip(),
            "after_sha256": candidate_sha,
            "write_performed": False,
        },
        "rewrite_summary": candidate.get("rewrite_summary"),
        "replacement_body_sha256": candidate_sha,
        "expected_replacement_body_sha256": str(replacement_body_sha256 or "").strip(),
        "replacement_body_sha256_semantics": "sha256_of_exact_pretty_json_utf8_bytes_to_write",
        "live_lease_gate": gate,
        "idempotency_key": str(idempotency_key or "").strip(),
        "agent_id": str(agent_id or "").strip(),
        "lease_id": str(lease_id or "").strip(),
        "execute_write": bool(execute_write),
        "projection_overwrite_performed": False,
        "accepted_projection_write_performed": False,
        "mutates_active_state": False,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "materialization_authority": False,
        "authority": semantic_alias_apply_authority(False),
    }
    if blockers:
        return {
            **base,
            "ok": False,
            "status": "semantic_alias_projection_apply_blocked",
            "receipt_path": rel(receipt_path, root),
            "blockers": blockers,
            "next_action": "repair_semantic_alias_projection_apply_inputs",
        }
    if receipt and existing_receipt_matches:
        return {
            **base,
            "ok": True,
            "status": "semantic_alias_projection_apply_idempotent_replay",
            "idempotent_replay": True,
            "receipt_path": rel(receipt_path, root),
            "blockers": [],
            "next_action": "no_op_idempotent_replay_preserved",
        }

    assert candidate_body is not None
    before_row = file_digest_row(target_path)
    atomic_write_text(target_path, json_write_text(candidate_body))
    after_row = file_digest_row(target_path)
    receipt_payload = {
        "schema_id": PROJECTION_APPLY_RECEIPT_SCHEMA_ID,
        "generated_at": generated,
        "result": "semantic_alias_projection_rewrite_applied",
        "active_root": str(root),
        "agent_id": str(agent_id or "").strip(),
        "lease_id": str(lease_id or "").strip(),
        "idempotency_key": str(idempotency_key or "").strip(),
        "target": {
            "path": target_rel,
            "before_sha256": before_row.get("sha256"),
            "after_sha256": after_row.get("sha256"),
            "bytes": after_row.get("bytes"),
        },
        "replacement_body_sha256": candidate_sha,
        "rewrite_summary": candidate.get("rewrite_summary"),
        "live_lease_gate": gate,
        "write_set": [target_rel, rel(receipt_path, root)],
        "projection_overwrite_performed": True,
        "accepted_projection_write_performed": True,
        "mutates_active_state": True,
        "accepted_state_claim": True,
        "accepted_state_scope": "domain_weaver_projection_semantic_alias_values_only",
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "materialization_authority": False,
        "authority": semantic_alias_apply_authority(True),
        "non_claims": [
            "This receipt proves only exact JSON value alias rewrites in DOMAIN_WEAVER_PROJECTION.json.",
            "It does not rewrite mount manifests, registry files, receipts, queues, topology, UI, production, live, secrets, materialization, workers, or git state.",
        ],
    }
    write_json(receipt_path, receipt_payload)
    return {
        **base,
        "ok": True,
        "status": "semantic_alias_projection_apply_applied",
        "target": {
            **base["target"],
            "before": before_row,
            "after": after_row,
            "before_sha256": before_row.get("sha256"),
            "after_sha256": after_row.get("sha256"),
            "write_performed": True,
        },
        "receipt_path": rel(receipt_path, root),
        "projection_overwrite_performed": True,
        "accepted_projection_write_performed": True,
        "mutates_active_state": True,
        "accepted_state_claim": True,
        "accepted_state_scope": "domain_weaver_projection_semantic_alias_values_only",
        "authority": semantic_alias_apply_authority(True),
        "blockers": [],
        "next_action": "rerun_semantic_alias_and_projection_refresh_validation",
    }


def observe_aliases(root: Path, projection: Mapping[str, Any]) -> list[dict[str, Any]]:
    observed: list[dict[str, Any]] = []
    counts = {alias: count_values(projection, alias) for alias in VNEXT_FRONT_DOOR_ALIASES}
    for alias, count in counts.items():
        if count:
            observed.append({
                "source": DEFAULT_PROJECTION_PATH.as_posix(),
                "alias": alias,
                "occurrence_count": count,
            })
    mounts_root = root / DEFAULT_MOUNT_ROOT
    if mounts_root.is_dir():
        for manifest_path in sorted(mounts_root.glob("*/ION_AGENT_MOUNT_MANIFEST.json")):
            manifest = read_json(manifest_path)
            domain_id = str(manifest.get("domain_id") or manifest.get("domain") or "").strip()
            if domain_id in VNEXT_FRONT_DOOR_ALIASES:
                observed.append({
                    "source": rel(manifest_path, root),
                    "alias": domain_id,
                    "occurrence_count": 1,
                })
    return observed


def promotion_evidence(*payloads: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for payload in payloads:
        rows.extend(find_promotion_rows(payload))
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        key = json.dumps(row, sort_keys=True)
        if key not in seen:
            seen.add(key)
            deduped.append(row)
    return deduped


def find_promotion_rows(value: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(value, Mapping):
        candidate = str(value.get("candidate_domain_id") or "").strip()
        proposed = str(value.get("proposed_active_domain_id") or "").strip()
        if candidate in VNEXT_FRONT_DOOR_ALIASES or proposed == VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID:
            rows.append({
                "candidate_domain_id": candidate,
                "proposed_active_domain_id": proposed,
                "proposed_active_registry_target": str(value.get("proposed_active_registry_target") or "").strip(),
                "candidate_draft_path": str(value.get("candidate_draft_path") or "").strip(),
            })
        for child in value.values():
            rows.extend(find_promotion_rows(child))
    elif isinstance(value, list):
        for child in value:
            rows.extend(find_promotion_rows(child))
    return rows


def would_change_refs(observed_aliases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "source": row["source"],
            "from_alias": row["alias"],
            "to_canonical": VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID,
            "apply_now": False,
        }
        for row in observed_aliases
    ]


def count_values(value: Any, needle: str) -> int:
    if isinstance(value, Mapping):
        return sum(count_values(item, needle) for item in value.values())
    if isinstance(value, list):
        return sum(count_values(item, needle) for item in value)
    return int(str(value) == needle)


def observe_projection_alias_values(value: Any, path: str = "$") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            rows.extend(observe_projection_alias_values(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(observe_projection_alias_values(child, f"{path}[{index}]"))
    elif isinstance(value, str) and value in VNEXT_FRONT_DOOR_ALIASES:
        rows.append({"path": path, "alias": value})
    return rows


def rewrite_alias_values(value: Any, path: str = "$") -> tuple[Any, list[dict[str, Any]]]:
    if isinstance(value, Mapping):
        rewritten: dict[str, Any] = {}
        rows: list[dict[str, Any]] = []
        for key, child in value.items():
            new_child, child_rows = rewrite_alias_values(child, f"{path}.{key}")
            rewritten[str(key)] = new_child
            rows.extend(child_rows)
        return rewritten, rows
    if isinstance(value, list):
        rewritten_list: list[Any] = []
        rows = []
        for index, child in enumerate(value):
            new_child, child_rows = rewrite_alias_values(child, f"{path}[{index}]")
            rewritten_list.append(new_child)
            rows.extend(child_rows)
        return rewritten_list, rows
    if isinstance(value, str) and value in VNEXT_FRONT_DOOR_ALIASES:
        return VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID, [
            {
                "json_path": path,
                "from_exact_value": value,
                "to_exact_value": VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID,
            }
        ]
    return value, []


def observe_manifest_alias_fields(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for field_name in ("domain_id", "domain"):
        value = manifest.get(field_name)
        if isinstance(value, str) and value in VNEXT_FRONT_DOOR_ALIASES:
            rows.append({"json_path": f"$.{field_name}", "field": field_name, "alias": value})
    return rows


def rewrite_manifest_alias_fields(manifest: Mapping[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rewritten = dict(manifest)
    rows: list[dict[str, Any]] = []
    for field_name in ("domain_id", "domain"):
        value = rewritten.get(field_name)
        if isinstance(value, str) and value in VNEXT_FRONT_DOOR_ALIASES:
            rewritten[field_name] = VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID
            rows.append(
                {
                    "json_path": f"$.{field_name}",
                    "field": field_name,
                    "from_exact_value": value,
                    "to_exact_value": VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID,
                }
            )
    return rewritten, rows


def json_write_text(payload: Mapping[str, Any]) -> str:
    return json.dumps(dict(payload), indent=2, sort_keys=True) + "\n"


def redact_candidate_body(candidate: Mapping[str, Any], *, include_candidate_bodies: bool) -> dict[str, Any]:
    payload = dict(candidate)
    if not include_candidate_bodies and "candidate_body" in payload:
        target = mapping(payload.get("target"))
        payload["candidate_body"] = {
            "omitted": True,
            "reason": "compact_preflight_default",
            "candidate_body_sha256": target.get("candidate_body_sha256"),
            "candidate_body_sha256_semantics": target.get("candidate_body_sha256_semantics"),
        }
    return payload


def stable_preflight_idempotency_key(prefix: str, lane: str, before_sha256: Any, replacement_sha256: Any) -> str:
    raw = f"{prefix}-{lane}-{str(before_sha256 or '')[:12]}-{str(replacement_sha256 or '')[:12]}"
    safe = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in raw.lower())
    while "--" in safe:
        safe = safe.replace("--", "-")
    return safe.strip("-")[:96] or f"semantic-alias-{lane}-apply"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def semantic_alias_apply_authority(write_performed: bool) -> dict[str, Any]:
    return {
        "candidate_context_only": not write_performed,
        "accepted_state_authority": bool(write_performed),
        "accepted_state_authority_scope": (
            "domain_weaver_projection_semantic_alias_values_only" if write_performed else "not_granted"
        ),
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "materialization_authority": False,
        "projection_overwrite_performed": bool(write_performed),
        "registry_write_performed": False,
        "mount_write_performed": False,
    }


def semantic_alias_manifest_apply_authority(write_performed: bool) -> dict[str, Any]:
    return {
        "candidate_context_only": not write_performed,
        "accepted_state_authority": bool(write_performed),
        "accepted_state_authority_scope": (
            "domain_weaver_vnext_front_door_mount_manifest_alias_field_only" if write_performed else "not_granted"
        ),
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "materialization_authority": False,
        "projection_overwrite_performed": False,
        "registry_write_performed": False,
        "mount_write_performed": bool(write_performed),
        "active_context_package_refresh_performed": False,
    }


def semantic_alias_live_lease_gate(
    root: Path,
    *,
    agent_id: str,
    lease_id: str,
    target_paths: list[str],
    blocker_prefix: str = "semantic_alias_projection_apply",
) -> dict[str, Any]:
    try:
        from .ion_worker_shift_presence import require_active_edit_lease
    except Exception as exc:  # pragma: no cover - fail closed import guard
        return {
            "schema_id": "ion.domain_weaver.semantic_alias.live_lease_gate.v0_1",
            "ok": False,
            "finding": "semantic_alias_live_lease_gate_unavailable",
            "error_type": type(exc).__name__,
            "blockers": ["semantic_alias_live_lease_gate_unavailable"],
            "authority": dict(AUTHORITY),
        }
    gate = require_active_edit_lease(
        root,
        agent_id=agent_id,
        lease_id=lease_id,
        target_files=target_paths,
        required_mode="exclusive_write",
    )
    public_gate = {
        str(key): value
        for key, value in dict(gate).items()
        if key != "active_lease"
    }
    return {
        "schema_id": "ion.domain_weaver.semantic_alias.live_lease_gate.v0_1",
        "ok": bool(public_gate.get("ok")),
        "finding": public_gate.get("finding"),
        "required_target_paths": target_paths,
        "worker_shift_gate": public_gate,
        "blockers": semantic_alias_live_lease_blockers(public_gate, prefix=blocker_prefix),
        "authority": dict(AUTHORITY),
    }


def semantic_alias_live_lease_blockers(
    gate: Mapping[str, Any],
    *,
    prefix: str = "semantic_alias_projection_apply",
) -> list[str]:
    if gate.get("ok") is True:
        return []
    worker_gate = mapping(gate.get("worker_shift_gate")) or gate
    blockers: list[str] = []
    finding = str(worker_gate.get("finding") or gate.get("finding") or "").strip()
    if finding == "active_edit_lease_not_found":
        blockers.append(f"{prefix}_live_lease_not_found")
    elif finding == "active_edit_lease_invalid":
        blockers.append(f"{prefix}_live_lease_invalid")
    elif finding:
        blockers.append(finding)
    for blocker in as_list(worker_gate.get("blockers")):
        text = str(blocker or "").strip()
        if text == "lease_agent_mismatch":
            blockers.append(f"{prefix}_live_lease_actor_mismatch")
        elif text == "lease_type_mismatch":
            blockers.append(f"{prefix}_live_lease_mode_mismatch")
        elif text == "lease_missing_target_coverage":
            blockers.append(f"{prefix}_live_lease_target_coverage_incomplete")
        elif text == "lease_not_fresh":
            blockers.append(f"{prefix}_live_lease_stale")
        elif text == "lease_identity_binding_blocked":
            blockers.append(f"{prefix}_live_lease_identity_blocked")
        elif text:
            blockers.append(text)
    return unique_texts(blockers or [f"{prefix}_live_lease_gate_failed"])


def semantic_alias_apply_receipt_path(root: Path, idempotency_key: str) -> Path:
    safe_key = "".join(
        ch if ch.isalnum() or ch in {"-", "_"} else "_"
        for ch in str(idempotency_key or "").strip()
    )[:96] or "semantic_alias_projection_apply"
    return root / DEFAULT_ACCEPTED_APPLY_RECEIPT_DIR / f"{safe_key}.json"


def semantic_alias_manifest_apply_receipt_path(root: Path, idempotency_key: str) -> Path:
    safe_key = "".join(
        ch if ch.isalnum() or ch in {"-", "_"} else "_"
        for ch in str(idempotency_key or "").strip()
    )[:96] or "semantic_alias_mount_manifest_apply"
    return root / DEFAULT_MANIFEST_ACCEPTED_APPLY_RECEIPT_DIR / f"{safe_key}.json"


def file_digest_row(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"exists": False, "sha256": "", "bytes": 0}
    data = path.read_bytes()
    return {"exists": True, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def unique_texts(values: list[Any]) -> list[str]:
    rows: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value or "").strip()
        if text and text not in seen:
            rows.append(text)
            seen.add(text)
    return rows


def identity_is_unbound(value: Any) -> bool:
    normalized = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    return normalized in {"", "anonymous", "none", "null", "unknown", "unbound", "unbound_worker_id"}


def render_report(payload: Mapping[str, Any]) -> str:
    candidate = payload["candidate_map"] if isinstance(payload.get("candidate_map"), Mapping) else {}
    lines = [
        "# Domain Weaver Semantic Alias Canonicalization Candidate",
        "",
        f"Generated: `{payload.get('generated_at')}`",
        "",
        f"Canonical candidate: `{candidate.get('canonical_id')}`",
        "",
        "Authority: candidate-only; no projection, registry, or mount writes.",
        "",
        "## Aliases",
        "",
    ]
    for alias in candidate.get("aliases", []):
        lines.append(f"- `{alias}`")
    lines.extend(["", "## Observed References", ""])
    for row in candidate.get("observed_aliases", []):
        lines.append(f"- `{row.get('alias')}` in `{row.get('source')}`: `{row.get('occurrence_count')}`")
    lines.extend(["", "## Promotion Evidence", ""])
    for row in candidate.get("promotion_evidence", []):
        lines.append(f"- `{row.get('candidate_domain_id')}` -> `{row.get('proposed_active_domain_id')}`")
    lines.extend(["", "## Blockers", ""])
    for blocker in payload.get("blockers", []):
        lines.append(f"- `{blocker}`")
    return "\n".join(lines) + "\n"


def render_semantic_alias_rewrite_candidate_report(payload: Mapping[str, Any], *, title: str) -> str:
    target = mapping(payload.get("target"))
    summary = mapping(payload.get("rewrite_summary"))
    lines = [
        f"# Domain Weaver Semantic Alias {title}",
        "",
        f"Generated: `{payload.get('generated_at')}`",
        "",
        "Authority: candidate-only. This artifact does not write projection, mount, registry, queue, worker, UI, production, live, secrets, materialization, or git state.",
        "",
        "## Target",
        "",
        f"- path: `{target.get('path')}`",
        f"- exists: `{target.get('exists')}`",
        f"- before sha256: `{target.get('before_sha256')}`",
        f"- candidate body sha256: `{target.get('candidate_body_sha256')}`",
        f"- write performed: `{target.get('write_performed')}`",
        "",
        "## Rewrite Summary",
        "",
    ]
    for key in sorted(summary):
        if key == "rewrite_rows":
            continue
        lines.append(f"- `{key}`: `{summary.get(key)}`")
    lines.extend(["", "## Blockers", ""])
    blockers = as_list(payload.get("blockers"))
    if blockers:
        for blocker in blockers:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Non-Claims", ""])
    for claim in as_list(payload.get("non_claims")):
        lines.append(f"- {claim}")
    return "\n".join(lines) + "\n"


def render_semantic_alias_supervised_apply_preflight_report(payload: Mapping[str, Any]) -> str:
    targets = mapping(payload.get("targets"))
    projection = mapping(targets.get("projection"))
    manifest = mapping(targets.get("mount_manifest"))
    previous = mapping(payload.get("previous_preflight_currentness"))
    lines = [
        "# Domain Weaver Semantic Alias Supervised Apply Preflight",
        "",
        f"Generated: `{payload.get('generated_at')}`",
        "",
        "Authority: candidate-only. This preflight does not invoke semantic alias apply routes.",
        "",
        "## Currentness",
        "",
        f"- current projection before sha256: `{payload.get('current_projection_before_sha256')}`",
        f"- current projection target current: `{payload.get('current_projection_target_current')}`",
        f"- previous preflight path: `{previous.get('path')}`",
        f"- previous projection before sha256: `{previous.get('projection_before_sha256')}`",
        f"- previous stale against current projection sha: `{previous.get('stale_against_current_projection_sha')}`",
        "",
        "## Targets",
        "",
        f"- projection: `{projection.get('path')}` before `{projection.get('before_sha256')}` replacement `{projection.get('candidate_body_sha256')}`",
        f"- mount manifest: `{manifest.get('path')}` before `{manifest.get('before_sha256')}` replacement `{manifest.get('candidate_body_sha256')}`",
        "",
        "## Write Sequence",
        "",
    ]
    for step in as_list(payload.get("write_sequence")):
        if isinstance(step, Mapping):
            lines.append(
                f"- `{step.get('order')}` `domain_weaver_agents.{step.get('route_id')}` "
                f"target `{step.get('target_path')}`"
            )
    lines.extend(["", "## Required Lease Targets", ""])
    for target in as_list(payload.get("required_combined_lease_targets")):
        lines.append(f"- `{target}`")
    lines.extend(["", "## Blockers", ""])
    blockers = as_list(payload.get("blockers"))
    if blockers:
        for blocker in blockers:
            lines.append(f"- `{blocker}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Non-Claims", ""])
    for claim in as_list(payload.get("non_claims")):
        lines.append(f"- {claim}")
    return "\n".join(lines) + "\n"


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_time(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def timestamp_for_filename(value: str) -> str:
    parsed = parse_time(value)
    return (parsed or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--generated-at", default="")
    parser.add_argument("--write", action="store_true")
    parser.add_argument(
        "--write-supervised-apply-preflight",
        action="store_true",
        help="Write semantic-alias projection/manifest candidates and supervised apply preflight only",
    )
    args = parser.parse_args(argv)
    if args.write_supervised_apply_preflight:
        result = write_semantic_alias_supervised_apply_preflight(args.root, generated_at=args.generated_at or None)
    elif args.write:
        result = write_semantic_alias_canonicalization_candidate(args.root, generated_at=args.generated_at or None)
    else:
        result = build_semantic_alias_canonicalization_candidate(args.root, generated_at=args.generated_at or None)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
