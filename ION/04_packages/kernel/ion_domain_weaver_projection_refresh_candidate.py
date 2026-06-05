"""Candidate-only Domain Weaver projection refresh evidence.

This helper builds a reproducible refresh packet around the current
``DOMAIN_WEAVER_PROJECTION.json`` without rewriting it. It exists to make
projection-staleness and context-mount freshness evidence rerunnable by later
agents.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

from .ion_domain_weaver_context_active_resolver import (
    build_active_context_reissue_preflight,
    build_context_active_resolver_status,
)
from .ion_domain_weaver_route_gate_matrix import build_domain_weaver_route_gate_matrix
from .ion_domain_weaver_semantic_ids import (
    VNEXT_FRONT_DOOR_ALIASES,
    VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID,
    canonicalize_codex_mount_identity,
)


SCHEMA_ID = "ion.domain_weaver.projection_refresh_candidate.v0_1"
WRITE_RESULT_SCHEMA_ID = "ion.domain_weaver.projection_refresh_candidate.write_result.v0_1"
CONTEXT_DELTA_SCHEMA_ID = "ion.domain_weaver.projection_refresh.context_graph_deltas.v0_1_candidate"
ACCEPTED_REFRESH_PLAN_SCHEMA_ID = "ion.domain_weaver.projection_accepted_refresh_plan.v0_1_candidate"
REPLACEMENT_BODY_CANDIDATE_SCHEMA_ID = (
    "ion.domain_weaver.projection_replacement_body_candidate.v0_1_candidate"
)
APPLY_GATE_REBASELINE_DRYRUN_SCHEMA_ID = (
    "ion.domain_weaver.projection_apply_gate_rebaseline_dryrun.v0_1_candidate"
)
APPLY_GATE_REBASELINE_DRYRUN_WRITE_RESULT_SCHEMA_ID = (
    "ion.domain_weaver.projection_apply_gate_rebaseline_dryrun.write_result.v0_1"
)
ACCEPTED_REFRESH_APPLY_SCHEMA_ID = "ion.domain_weaver.projection_accepted_refresh_apply.v0_1_candidate"
ACCEPTED_REFRESH_APPLY_RECEIPT_SCHEMA_ID = "ion.domain_weaver.projection_accepted_refresh_apply_receipt.v0_1"
BOUNDED_WRITE_CONFIRMATION = "ION_BOUNDED_WRITE_CONFIRMED"
ACCEPTED_STATE_WRITE_CONFIRMATION = "ION_DOMAIN_WEAVER_PROJECTION_ACCEPTED_WRITE_CONFIRMED"

DEFAULT_CONTEXT_ROOT = Path("ION/05_context/current/domain_weaver")
DEFAULT_OUTPUT_DIR = DEFAULT_CONTEXT_ROOT / "projection_refresh"
DEFAULT_ACTIVE_CONTEXT_REFRESH_DIR = DEFAULT_CONTEXT_ROOT / "active_context_refresh"
DEFAULT_OPERATOR_ACTION_DIR = DEFAULT_CONTEXT_ROOT / "operator_actions"
DEFAULT_MOUNT_ROOT = Path("ION/05_context/current/codex_agent_mounts")

DEFAULT_PROJECTION_PATH = DEFAULT_CONTEXT_ROOT / "DOMAIN_WEAVER_PROJECTION.json"
DEFAULT_ACTIVE_BINDING_PATH = (
    DEFAULT_CONTEXT_ROOT / "live_carrier_binding/ACTIVE_INVOKABLE_BINDING_PROOF_ROWS.candidate.json"
)
DEFAULT_READY_REVIEW_PATH = DEFAULT_CONTEXT_ROOT / "ready_review/STEWARD_READY_REVIEW.json"
DEFAULT_SELF_EVOLUTION_READINESS_PATH = (
    DEFAULT_CONTEXT_ROOT / "self_evolution_readiness/DOMAIN_WEAVER_SELF_EVOLUTION_READINESS.latest.json"
)
DEFAULT_QUEUE_HYGIENE_PATH = (
    DEFAULT_CONTEXT_ROOT / "queue_governance/DOMAIN_WEAVER_WORKER_START_BACKLOG_HYGIENE.latest.json"
)
DEFAULT_ACCEPTED_REFRESH_PLAN_PATH = (
    DEFAULT_CONTEXT_ROOT / "projection_refresh/DOMAIN_WEAVER_PROJECTION_ACCEPTED_REFRESH_PLAN.latest.json"
)
DEFAULT_ACCEPTED_REFRESH_APPLY_RECEIPT_DIR = DEFAULT_OUTPUT_DIR / "accepted_apply_receipts"
DEFAULT_SEMANTIC_ALIAS_REVIEW_PATH = (
    DEFAULT_CONTEXT_ROOT
    / "semantic_alias_canonicalization/DOMAIN_WEAVER_SEMANTIC_ALIAS_ACCEPTED_PROJECTION_REVIEW.latest.candidate.json"
)

DEFAULT_JSON_NAME = "DOMAIN_WEAVER_PROJECTION_REFRESH_CANDIDATE.latest.json"
DEFAULT_REPORT_NAME = "DOMAIN_WEAVER_PROJECTION_REFRESH_CANDIDATE.latest.md"
DEFAULT_CONTEXT_DELTA_NAME = "DOMAIN_WEAVER_CONTEXT_GRAPH_DELTAS_PROJECTION_REFRESH.latest.candidate.json"
DEFAULT_ACCEPTED_REFRESH_PLAN_REPORT_NAME = "DOMAIN_WEAVER_PROJECTION_ACCEPTED_REFRESH_PLAN.latest.md"
DEFAULT_REPLACEMENT_BODY_CANDIDATE_NAME = "DOMAIN_WEAVER_PROJECTION_REPLACEMENT_BODY_CANDIDATE.latest.json"
DEFAULT_REPLACEMENT_BODY_CANDIDATE_REPORT_NAME = "DOMAIN_WEAVER_PROJECTION_REPLACEMENT_BODY_CANDIDATE.latest.md"
DEFAULT_APPLY_GATE_REBASELINE_DRYRUN_NAME = "DOMAIN_WEAVER_PROJECTION_APPLY_GATE_REBASELINE_DRYRUN.latest.json"
DEFAULT_APPLY_GATE_REBASELINE_DRYRUN_REPORT_NAME = "DOMAIN_WEAVER_PROJECTION_APPLY_GATE_REBASELINE_DRYRUN.latest.md"
DEFAULT_PREFLIGHT_JSON_NAME = "ACTIVE_CONTEXT_REISSUE_PREFLIGHT_CURRENT.latest.json"
DEFAULT_PREFLIGHT_REPORT_NAME = "ACTIVE_CONTEXT_REISSUE_PREFLIGHT_CURRENT.latest.md"

AUTHORITY = {
    "candidate_context_only": True,
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "materialization_authority": False,
    "projection_overwrite_performed": False,
}

NON_CLAIMS = [
    "This artifact does not overwrite DOMAIN_WEAVER_PROJECTION.json.",
    "Candidate context graph deltas are not accepted state.",
    "Declared route gates do not prove handler write-set parity.",
    "Exact-active binding proof is not materialization authority.",
    "No worker is started and no queue request is processed.",
]

def build_projection_refresh_candidate(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
    max_context_age_seconds: int | None = None,
) -> dict[str, Any]:
    """Build a candidate projection-refresh packet from active-root evidence."""

    root = Path(active_root).expanduser().resolve(strict=False)
    generated = generated_at or utc_now()
    projection_path = root / DEFAULT_PROJECTION_PATH
    source_projection = read_json(projection_path)
    latest_receipt = latest_operator_receipt(root)
    source_generated_at = str(source_projection.get("generated_at") or "")
    projection_stale = is_older_than(source_generated_at, latest_receipt.get("receipt_at", ""))

    preflight = build_active_context_reissue_preflight(
        root,
        max_age_seconds=max_context_age_seconds or 48 * 60 * 60,
    )
    route_gate_matrix = build_domain_weaver_route_gate_matrix(root)
    mount_census = summarize_generated_mounts(root)
    exact_active = summarize_exact_active_binding(root)
    route_summary = mapping(route_gate_matrix.get("summary"))
    preflight_summary = summarize_preflight(preflight)
    context_deltas = build_context_graph_deltas(
        exact_active=exact_active,
        mount_census=mount_census,
        preflight_summary=preflight_summary,
        route_summary=route_summary,
    )

    blockers = build_blockers(
        projection_stale=projection_stale,
        source_projection=source_projection,
        mount_census=mount_census,
        preflight_summary=preflight_summary,
        route_summary=route_summary,
        exact_active=exact_active,
    )

    return {
        "schema_id": SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "authority": dict(AUTHORITY),
        "source_projection": {
            "path": DEFAULT_PROJECTION_PATH.as_posix(),
            "generated_at": source_generated_at,
            "weave_status": source_projection.get("weave_status"),
            "stale_against_latest_receipts": projection_stale,
            "latest_receipt_path": latest_receipt.get("path", ""),
            "latest_receipt_at": latest_receipt.get("receipt_at", ""),
            "reason": (
                "projection_generated_before_latest_domain_weaver_receipt"
                if projection_stale
                else "no_newer_operator_receipt_detected"
            ),
        },
        "ready_review": {
            "path": DEFAULT_READY_REVIEW_PATH.as_posix(),
            "stale_against_latest_receipts": projection_stale,
        },
        "mount_census": mount_census,
        "active_context_reissue_preflight": preflight_summary,
        "route_gate_matrix": {
            "path": (DEFAULT_CONTEXT_ROOT / "route_policy/DOMAIN_WEAVER_ACTION_ROUTE_GATE_MATRIX.latest.json").as_posix(),
            "summary": route_summary,
            "domain_weaver_gapped_mutating_route_count": int(
                route_summary.get("domain_weaver_gapped_mutating_route_count") or 0
            ),
            "handler_parity_proven": False,
            "must_fix_before_serious_self_evolution": route_gate_matrix.get("must_fix_before_serious_self_evolution") or [],
        },
        "exact_active_binding_candidate": exact_active,
        "materialization_ready": False,
        "automatic_original_agent_reaction_proven": False,
        "candidate_context_graph_deltas": context_deltas,
        "blockers": blockers,
        "non_claims": list(NON_CLAIMS),
        "next_packets": [
            "PCKT-DOMAIN-WEAVER-ACTIVE-CONTEXT-GATED-REFRESH-V0_1",
            "PCKT-DOMAIN-WEAVER-SEMANTIC-ALIAS-CANONICALIZATION-V0_1",
            "PCKT-DOMAIN-WEAVER-HANDLER-WRITE-SET-PARITY-V0_1",
            "PCKT-DOMAIN-WEAVER-SELF-EVOLUTION-PROJECTION-REFRESH-V0_2",
        ],
        "verdict": "PROJECTION_REFRESH_CANDIDATE_WRITTEN_NOT_ACCEPTED_STATE",
        "_embedded_preflight": preflight,
        "_embedded_route_gate_matrix": route_gate_matrix,
    }


def write_projection_refresh_candidate(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
    max_context_age_seconds: int | None = None,
) -> dict[str, Any]:
    """Write candidate projection-refresh artifacts and a receipt."""

    root = Path(active_root).expanduser().resolve(strict=False)
    payload = build_projection_refresh_candidate(
        root,
        generated_at=generated_at,
        max_context_age_seconds=max_context_age_seconds,
    )
    preflight = dict(payload.pop("_embedded_preflight"))
    route_gate_matrix = dict(payload.pop("_embedded_route_gate_matrix"))
    generated = str(payload["generated_at"])
    stamp = timestamp_for_filename(generated)

    output_dir = root / DEFAULT_OUTPUT_DIR
    active_context_dir = root / DEFAULT_ACTIVE_CONTEXT_REFRESH_DIR
    operator_action_dir = root / DEFAULT_OPERATOR_ACTION_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    active_context_dir.mkdir(parents=True, exist_ok=True)
    operator_action_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / DEFAULT_JSON_NAME
    report_path = output_dir / DEFAULT_REPORT_NAME
    delta_path = output_dir / DEFAULT_CONTEXT_DELTA_NAME
    preflight_json_path = active_context_dir / DEFAULT_PREFLIGHT_JSON_NAME
    preflight_report_path = active_context_dir / DEFAULT_PREFLIGHT_REPORT_NAME
    receipt_path = operator_action_dir / f"{stamp}_domain_weaver_projection_refresh_candidate_generated.json"

    write_json(json_path, payload)
    write_json(delta_path, payload["candidate_context_graph_deltas"])
    write_json(preflight_json_path, preflight)
    write_text(report_path, render_projection_refresh_report(payload))
    write_text(preflight_report_path, render_preflight_report(preflight))

    receipt = {
        "schema_id": "ion.domain_weaver.operator_action_receipt.v0_1",
        "receipt_type": "domain_weaver_projection_refresh_candidate_generated",
        "generated_at": generated,
        "result": "candidate_projection_refresh_written_no_accepted_state",
        "active_root": str(root),
        "authority": dict(AUTHORITY),
        "artifacts": {
            "projection_refresh_json": rel(json_path, root),
            "projection_refresh_report": rel(report_path, root),
            "context_graph_deltas": rel(delta_path, root),
            "active_context_reissue_preflight_json": rel(preflight_json_path, root),
            "active_context_reissue_preflight_report": rel(preflight_report_path, root),
        },
        "preflight_summary": payload["active_context_reissue_preflight"],
        "route_gate_summary": payload["route_gate_matrix"]["summary"],
        "blockers": payload["blockers"],
        "non_claims": list(NON_CLAIMS),
        "validation": [],
    }
    write_json(receipt_path, receipt)

    return {
        "schema_id": WRITE_RESULT_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "json_path": rel(json_path, root),
        "report_path": rel(report_path, root),
        "context_graph_delta_path": rel(delta_path, root),
        "active_context_reissue_preflight_json_path": rel(preflight_json_path, root),
        "active_context_reissue_preflight_report_path": rel(preflight_report_path, root),
        "operator_receipt_path": rel(receipt_path, root),
        "projection_overwrite_performed": False,
        "refresh_run": False,
        "mutates_active_state": False,
        "route_gate_matrix_written_inline": bool(route_gate_matrix),
        "authority": dict(AUTHORITY),
    }


def build_projection_replacement_body_candidate(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
    max_context_age_seconds: int | None = None,
) -> dict[str, Any]:
    """Build a candidate replacement body for DOMAIN_WEAVER_PROJECTION.json.

    The returned candidate body is not written. It preserves blocked readiness
    states and only injects bounded current control-plane evidence.
    """

    root = Path(active_root).expanduser().resolve(strict=False)
    generated = generated_at or utc_now()
    projection_path = root / DEFAULT_PROJECTION_PATH
    source_projection = read_json(projection_path)
    if not source_projection:
        return {
            "schema_id": REPLACEMENT_BODY_CANDIDATE_SCHEMA_ID,
            "generated_at": generated,
            "active_root": str(root),
            "ok": False,
            "status": "source_projection_missing",
            "target": {
                "path": DEFAULT_PROJECTION_PATH.as_posix(),
                "exists": False,
                "before_sha256": None,
                "candidate_body_sha256": None,
            },
            "candidate_body": None,
            "blockers": [
                {
                    "code": "source_projection_missing",
                    "severity": "critical",
                    "evidence": [DEFAULT_PROJECTION_PATH.as_posix()],
                }
            ],
            "authority": dict(AUTHORITY),
            "mutates_active_state": False,
            "accepted_state_claim": False,
        }

    from .ion_domain_weaver_worker_start_readiness import build_domain_weaver_worker_start_backlog_hygiene

    route_gate_matrix = build_domain_weaver_route_gate_matrix(root)
    route_summary = mapping(route_gate_matrix.get("summary"))
    context_status = build_context_active_resolver_status(root)
    queue_hygiene = build_domain_weaver_worker_start_backlog_hygiene(root)
    self_readiness = read_json(root / DEFAULT_SELF_EVOLUTION_READINESS_PATH)
    semantic_review = read_json(root / DEFAULT_SEMANTIC_ALIAS_REVIEW_PATH)
    source_sha256 = sha256_file(projection_path)
    candidate_body = json.loads(json.dumps(source_projection))
    summary = dict(candidate_body.get("summary") if isinstance(candidate_body.get("summary"), Mapping) else {})
    queue_summary = mapping(queue_hygiene.get("summary"))
    context_summary = {
        "inspected_mount_count": context_status.get("inspected_mount_count"),
        "fresh_active_context_count": context_status.get("fresh_active_context_count"),
        "stale_or_missing_active_context_count": context_status.get("stale_or_missing_active_context_count"),
        "materialize_all_allowed": mapping(context_status.get("materialize_all_guard")).get("materialize_all_allowed"),
    }
    semantic_gate = mapping(semantic_review.get("accepted_state_gate_remaining"))
    semantic_apply_scope = as_list(semantic_gate.get("minimum_apply_scope_for_review"))
    semantic_projection_alias_count = 0
    for row in semantic_apply_scope:
        if not isinstance(row, Mapping) or row.get("path") != DEFAULT_PROJECTION_PATH.as_posix():
            continue
        for rewrite in as_list(row.get("rewrites")):
            if isinstance(rewrite, Mapping):
                semantic_projection_alias_count += int(rewrite.get("candidate_observed_count") or 0)

    summary.update(
        {
            "projection_replacement_body_candidate_generated_at": generated,
            "projection_replacement_body_candidate_ready": True,
            "projection_replacement_body_candidate_source_sha256": source_sha256,
            "projection_replacement_body_candidate_write_performed": False,
            "projection_accepted_apply_ready": False,
            "projection_accepted_state_write_gate_granted": False,
            "route_gate_matrix_route_count": int(route_summary.get("route_count") or 0),
            "route_gate_matrix_mutating_route_count": int(route_summary.get("mutating_route_count") or 0),
            "route_gate_matrix_strong_mutating_route_count": int(route_summary.get("strong_mutating_route_count") or 0),
            "route_gate_matrix_gapped_mutating_route_count": int(route_summary.get("gapped_mutating_route_count") or 0),
            "route_gate_matrix_systemic_mutation_route_coverage_proven": bool(
                route_summary.get("systemic_mutation_route_coverage_proven")
            ),
            "context_active_resolver_available": bool(context_status.get("ok", True)),
            "context_active_resolver_inspected_mount_count": context_summary["inspected_mount_count"],
            "context_active_resolver_fresh_active_context_count": context_summary["fresh_active_context_count"],
            "context_active_resolver_stale_or_missing_active_context_count": context_summary[
                "stale_or_missing_active_context_count"
            ],
            "context_active_resolver_materialize_all_allowed": bool(context_summary["materialize_all_allowed"]),
            "worker_start_ready_to_start_workers": bool(queue_hygiene.get("global_worker_start_readiness_ok")),
            "worker_start_queueable_request_count": int(queue_summary.get("queueable_for_start_request_count") or 0),
            "worker_start_ready_request_count": int(queue_summary.get("ready_request_count") or 0),
            "worker_start_blocked_request_count": int(queue_summary.get("blocked_request_count") or 0),
            "worker_start_exact_spawn_dispatch_ready_count": int(
                queue_summary.get("exact_spawn_dispatch_ready_count") or 0
            ),
            "worker_start_general_queue_processing_allowed": False,
            "semantic_alias_projection_alias_observed_count": semantic_projection_alias_count,
            "semantic_alias_accepted_apply_gate_granted": False,
            "serious_self_evolution_ready": bool(self_readiness.get("serious_self_evolution_ready")),
            "autonomous_self_evolution_ready": bool(self_readiness.get("autonomous_self_evolution_ready")),
            "production_ready": bool(self_readiness.get("production_ready")),
            "supervised_candidate_wave_allowed": bool(self_readiness.get("supervised_candidate_wave_allowed")),
        }
    )
    for key in (
        "full_domain_weaver_ready",
        "self_evolution_ready",
        "self_evolution_lattice_executable",
        "ui_development_ready",
        "ui_operator_usable",
    ):
        summary[key] = False
    candidate_body["summary"] = summary
    candidate_body["generated_at"] = generated
    candidate_body["accepted_state_authority"] = False
    candidate_body["production_authority"] = False
    candidate_body["live_execution_authority"] = False
    candidate_body["secrets_authority"] = False
    authority = dict(candidate_body.get("authority") if isinstance(candidate_body.get("authority"), Mapping) else {})
    authority.update(
        {
            "candidate_projection_only": True,
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        }
    )
    candidate_body["authority"] = authority
    candidate_body["accepted_refresh_replacement_candidate"] = {
        "schema_id": "ion.domain_weaver.projection.accepted_refresh_replacement_section.v0_1_candidate",
        "generated_at": generated,
        "source_projection_path": DEFAULT_PROJECTION_PATH.as_posix(),
        "source_projection_sha256": source_sha256,
        "write_performed": False,
        "accepted_state_claim": False,
        "route_gate_matrix_summary": route_summary,
        "context_active_resolver_summary": context_summary,
        "worker_start_backlog_hygiene_summary": queue_summary,
        "self_evolution_readiness": {
            "verdict": self_readiness.get("verdict"),
            "serious_self_evolution_ready": bool(self_readiness.get("serious_self_evolution_ready")),
            "autonomous_self_evolution_ready": bool(self_readiness.get("autonomous_self_evolution_ready")),
            "production_ready": bool(self_readiness.get("production_ready")),
            "supervised_candidate_wave_allowed": bool(self_readiness.get("supervised_candidate_wave_allowed")),
            "blockers_ranked": as_list(self_readiness.get("blockers_ranked")),
        },
        "semantic_alias_gate": semantic_gate,
        "next_packets": [
            "PCKT-DOMAIN-WEAVER-PROJECTION-ACCEPTED-STATE-WRITE-APPLY-V0_1",
            "PCKT-DOMAIN-WEAVER-SEMANTIC-ALIAS-CANONICALIZATION-APPLY-GATE-V0_1",
            "PCKT-DOMAIN-WEAVER-COMMS-AUTOREACTION-PROOF-V0_2A-ORIGINAL-WORKER-BOUND-READONLY-REPLAY",
        ],
        "non_claims": [
            "candidate replacement body only",
            "not accepted state until separately applied through a write-gated route",
            "does not grant materialization readiness",
            "does not start workers or process queues",
        ],
    }
    candidate_canonical_sha256 = sha256_json(candidate_body)
    candidate_sha256 = sha256_text(json_write_text(candidate_body))
    invariants = _projection_replacement_invariants(candidate_body)
    blockers = [
        {
            "code": "accepted_state_write_gate_not_granted",
            "severity": "critical",
            "evidence": ["projection_accepted_refresh_apply_not_invoked"],
        },
        {
            "code": "semantic_alias_accepted_apply_gate_not_granted",
            "severity": "high",
            "evidence": [DEFAULT_SEMANTIC_ALIAS_REVIEW_PATH.as_posix()],
        },
    ]
    if not invariants["ok"]:
        blockers.append(
            {
                "code": "replacement_body_invariant_failure",
                "severity": "critical",
                "evidence": invariants["failures"],
            }
        )
    return {
        "schema_id": REPLACEMENT_BODY_CANDIDATE_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "ok": bool(invariants["ok"]),
        "status": "projection_replacement_body_candidate_built",
        "target": {
            "path": DEFAULT_PROJECTION_PATH.as_posix(),
            "exists": projection_path.is_file(),
            "before_sha256": source_sha256,
            "candidate_body_sha256": candidate_sha256,
            "candidate_body_canonical_sha256": candidate_canonical_sha256,
            "candidate_body_sha256_semantics": "sha256_of_exact_pretty_json_utf8_bytes_to_write",
            "write_performed": False,
        },
        "candidate_body": candidate_body,
        "candidate_body_summary_patch": {
            key: summary.get(key)
            for key in (
                "projection_replacement_body_candidate_ready",
                "projection_accepted_apply_ready",
                "route_gate_matrix_route_count",
                "route_gate_matrix_gapped_mutating_route_count",
                "context_active_resolver_fresh_active_context_count",
                "context_active_resolver_stale_or_missing_active_context_count",
                "worker_start_exact_spawn_dispatch_ready_count",
                "worker_start_general_queue_processing_allowed",
                "semantic_alias_projection_alias_observed_count",
                "semantic_alias_accepted_apply_gate_granted",
                "serious_self_evolution_ready",
                "autonomous_self_evolution_ready",
                "production_ready",
                "supervised_candidate_wave_allowed",
            )
        },
        "invariants": invariants,
        "blockers": blockers,
        "apply_ready": False,
        "mutates_active_state": False,
        "projection_overwrite_performed": False,
        "accepted_state_claim": False,
        "authority": dict(AUTHORITY),
        "non_claims": [
            "No projection overwrite was performed.",
            "No accepted-state authority was granted.",
            "No materialization readiness was claimed.",
            "No worker was started and no queue row was processed.",
        ],
    }


def apply_projection_accepted_refresh(
    active_root: str | Path,
    *,
    confirmation: str,
    accepted_state_write_confirmation: str,
    idempotency_key: str,
    agent_id: str,
    lease_id: str,
    before_sha256: str,
    replacement_body_sha256: str,
    replacement_body: Mapping[str, Any] | None = None,
    replacement_body_path: str | Path | None = None,
    execute_write: bool = False,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Apply a bounded accepted projection refresh after exact proof gates.

    This writes only ``DOMAIN_WEAVER_PROJECTION.json`` and a deterministic
    idempotency receipt. It never invokes broad materializers, starts workers,
    processes queues, writes registries, or grants production/live/secrets
    authority.
    """

    root = Path(active_root).expanduser().resolve(strict=False)
    generated = generated_at or utc_now()
    target_path = root / DEFAULT_PROJECTION_PATH
    target_rel = DEFAULT_PROJECTION_PATH.as_posix()
    receipt_path = _projection_apply_receipt_path(root, idempotency_key)
    body, body_source, body_load_blockers = _load_projection_replacement_body(
        root,
        replacement_body=replacement_body,
        replacement_body_path=replacement_body_path,
    )
    body_text = json_write_text(body) if body else ""
    calculated_replacement_sha256 = sha256_text(body_text) if body_text else None
    invariants = _projection_replacement_invariants(body) if body else {
        "ok": False,
        "failures": ["replacement_body_required"],
        "checked": [],
    }
    current_sha256 = sha256_file(target_path)
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

    gate = _projection_apply_live_lease_gate(
        root,
        agent_id=str(agent_id or "").strip(),
        lease_id=str(lease_id or "").strip(),
        target_paths=[target_rel],
    )
    blockers: list[str] = list(body_load_blockers)
    if confirmation != BOUNDED_WRITE_CONFIRMATION:
        blockers.append("projection_apply_bounded_write_confirmation_required")
    if accepted_state_write_confirmation != ACCEPTED_STATE_WRITE_CONFIRMATION:
        blockers.append("projection_apply_accepted_state_write_confirmation_required")
    if not str(idempotency_key or "").strip():
        blockers.append("projection_apply_idempotency_key_required")
    if _identity_is_unbound(agent_id):
        blockers.append("projection_apply_actor_identity_required")
    if not str(lease_id or "").strip():
        blockers.append("projection_apply_lease_id_required")
    if not execute_write:
        blockers.append("projection_apply_execute_write_required")
    if not target_path.is_file():
        blockers.append("projection_apply_target_missing")
    if not str(before_sha256 or "").strip():
        blockers.append("projection_apply_before_sha256_required")
    if not str(replacement_body_sha256 or "").strip():
        blockers.append("projection_apply_replacement_body_sha256_required")
    if calculated_replacement_sha256 and str(replacement_body_sha256 or "").strip() != calculated_replacement_sha256:
        blockers.append("projection_apply_replacement_body_sha256_mismatch")
    if not invariants.get("ok"):
        blockers.append("projection_apply_replacement_body_invariant_failure")
    if gate.get("ok") is not True:
        blockers.append("projection_apply_live_exclusive_write_lease_required")
        blockers.extend(_projection_apply_live_lease_blockers(gate))
    if receipt:
        if not existing_receipt_matches:
            blockers.append("projection_apply_idempotency_conflict")
        elif current_sha256 != receipt_target.get("after_sha256"):
            blockers.append("projection_apply_idempotent_replay_target_sha_mismatch")
    elif current_sha256 != str(before_sha256 or "").strip():
        blockers.append("projection_apply_before_sha256_mismatch")
    blockers = unique_texts(blockers)

    base = {
        "schema_id": ACCEPTED_REFRESH_APPLY_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "target": {
            "path": target_rel,
            "exists": target_path.is_file(),
            "before_sha256": current_sha256,
            "expected_before_sha256": str(before_sha256 or "").strip(),
            "after_sha256": calculated_replacement_sha256,
            "write_performed": False,
        },
        "replacement_body_source": body_source,
        "replacement_body_sha256": calculated_replacement_sha256,
        "expected_replacement_body_sha256": str(replacement_body_sha256 or "").strip(),
        "replacement_body_sha256_semantics": "sha256_of_exact_pretty_json_utf8_bytes_to_write",
        "invariants": invariants,
        "live_lease_gate": gate,
        "idempotency_key": str(idempotency_key or "").strip(),
        "agent_id": str(agent_id or "").strip(),
        "lease_id": str(lease_id or "").strip(),
        "execute_write": bool(execute_write),
        "confirmation_ok": confirmation == BOUNDED_WRITE_CONFIRMATION,
        "accepted_state_write_confirmation_ok": (
            accepted_state_write_confirmation == ACCEPTED_STATE_WRITE_CONFIRMATION
        ),
        "projection_overwrite_performed": False,
        "accepted_projection_write_performed": False,
        "mutates_active_state": False,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "materialization_authority": False,
        "authority": projection_apply_authority(False),
        "non_claims": [
            "No production, live-execution, secrets, materialization, topology, UI, queue, worker, Codex Solo, git, or broad registry authority is granted.",
            "This route may write only the Domain Weaver projection file and its apply receipt when every gate passes.",
        ],
    }
    if blockers:
        return {
            **base,
            "ok": False,
            "status": "projection_accepted_refresh_apply_blocked",
            "receipt_path": rel(receipt_path, root),
            "blockers": blockers,
            "next_action": "repair_projection_accepted_refresh_apply_inputs",
        }
    if receipt and existing_receipt_matches:
        return {
            **base,
            "ok": True,
            "status": "projection_accepted_refresh_apply_idempotent_replay",
            "idempotent_replay": True,
            "receipt_path": rel(receipt_path, root),
            "blockers": [],
            "next_action": "no_op_idempotent_replay_preserved",
        }

    before_row = file_digest_row(target_path)
    atomic_write_text(target_path, body_text)
    after_row = file_digest_row(target_path)
    if after_row.get("sha256") != calculated_replacement_sha256:
        return {
            **base,
            "ok": False,
            "status": "projection_accepted_refresh_apply_post_write_hash_mismatch",
            "target": {
                **base["target"],
                "before": before_row,
                "after": after_row,
                "write_performed": True,
            },
            "projection_overwrite_performed": True,
            "accepted_projection_write_performed": True,
            "mutates_active_state": True,
            "accepted_state_claim": True,
            "authority": projection_apply_authority(True),
            "receipt_path": rel(receipt_path, root),
            "blockers": ["projection_apply_post_write_hash_mismatch"],
            "next_action": "halt_and_review_projection_apply_hash_mismatch",
        }

    receipt_payload = {
        "schema_id": ACCEPTED_REFRESH_APPLY_RECEIPT_SCHEMA_ID,
        "generated_at": generated,
        "result": "domain_weaver_projection_accepted_refresh_applied",
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
        "replacement_body_source": body_source,
        "replacement_body_sha256": calculated_replacement_sha256,
        "replacement_body_sha256_semantics": "sha256_of_exact_pretty_json_utf8_bytes_to_write",
        "live_lease_gate": gate,
        "invariants": invariants,
        "write_set": [
            target_rel,
            rel(receipt_path, root),
        ],
        "projection_overwrite_performed": True,
        "accepted_projection_write_performed": True,
        "mutates_active_state": True,
        "accepted_state_claim": True,
        "accepted_state_scope": "domain_weaver_projection_file_only",
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "materialization_authority": False,
        "authority": projection_apply_authority(True),
        "non_claims": [
            "This receipt proves only a bounded Domain Weaver projection file replacement.",
            "It does not grant production, live-execution, secrets, materialization, autonomous self-evolution, queue processing, worker start, topology, UI, Codex Solo, broad registry, or git authority.",
        ],
    }
    write_json(receipt_path, receipt_payload)
    return {
        **base,
        "ok": True,
        "status": "projection_accepted_refresh_applied",
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
        "accepted_state_scope": "domain_weaver_projection_file_only",
        "authority": projection_apply_authority(True),
        "blockers": [],
        "next_action": "preserve_apply_receipt_and_run_projection_readiness_fanin",
    }


def build_projection_accepted_refresh_plan(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
    max_context_age_seconds: int | None = None,
) -> dict[str, Any]:
    """Build a no-write plan for a future accepted projection refresh gate."""

    root = Path(active_root).expanduser().resolve(strict=False)
    source_projection_path = root / DEFAULT_PROJECTION_PATH
    candidate = build_projection_refresh_candidate(
        root,
        generated_at=generated_at,
        max_context_age_seconds=max_context_age_seconds,
    )
    candidate.pop("_embedded_preflight", None)
    candidate.pop("_embedded_route_gate_matrix", None)
    replacement = build_projection_replacement_body_candidate(
        root,
        generated_at=generated_at,
        max_context_age_seconds=max_context_age_seconds,
    )
    candidate_sha256 = sha256_json(candidate)
    source_sha256 = sha256_file(source_projection_path)
    replacement_sha256 = mapping(replacement.get("target")).get("candidate_body_sha256")
    route_summary = mapping(mapping(candidate.get("route_gate_matrix")).get("summary"))
    blockers = [
        {
            "code": "accepted_state_write_gate_not_granted",
            "severity": "critical",
            "evidence": ["no projection_accepted_refresh_apply route invoked"],
        },
    ]
    if not replacement.get("ok"):
        blockers.append(
            {
                "code": "accepted_projection_replacement_body_invariant_failure",
                "severity": "critical",
                "evidence": list(mapping(replacement.get("invariants")).get("failures") or []),
            }
        )
    if not source_projection_path.is_file():
        blockers.append(
            {
                "code": "accepted_projection_target_missing",
                "severity": "critical",
                "evidence": [DEFAULT_PROJECTION_PATH.as_posix()],
            }
        )
    if candidate.get("blockers"):
        blockers.append(
            {
                "code": "projection_refresh_candidate_has_open_blockers",
                "severity": "high",
                "evidence": [str(row.get("code")) for row in as_list(candidate.get("blockers")) if isinstance(row, Mapping)],
            }
        )
    if int(route_summary.get("gapped_mutating_route_count") or 0):
        blockers.append(
            {
                "code": "route_gate_matrix_has_mutating_gaps",
                "severity": "critical",
                "evidence": [str(route_summary.get("gapped_mutating_route_count"))],
            }
        )
    return {
        "schema_id": ACCEPTED_REFRESH_PLAN_SCHEMA_ID,
        "generated_at": generated_at or utc_now(),
        "active_root": str(root),
        "status": "projection_accepted_refresh_plan_built_no_write",
        "plan_ok": False,
        "apply_ready": False,
        "write_performed": False,
        "projection_overwrite_performed": False,
        "mutates_active_state": False,
        "accepted_state_claim": False,
        "authority": dict(AUTHORITY),
        "target": {
            "path": DEFAULT_PROJECTION_PATH.as_posix(),
            "exists": source_projection_path.is_file(),
            "before_sha256": source_sha256,
            "after_sha256": replacement_sha256,
            "after_sha256_status": "candidate_replacement_body_available_not_applied"
            if replacement_sha256
            else "unavailable_until_replacement_projection_body_built",
        },
        "candidate_evidence": {
            "schema_id": candidate.get("schema_id"),
            "generated_at": candidate.get("generated_at"),
            "sha256": candidate_sha256,
            "source_projection": candidate.get("source_projection"),
            "route_gate_matrix": candidate.get("route_gate_matrix"),
            "active_context_reissue_preflight": candidate.get("active_context_reissue_preflight"),
            "exact_active_binding_candidate": candidate.get("exact_active_binding_candidate"),
            "blockers": candidate.get("blockers"),
        },
        "replacement_body_candidate": {
            "schema_id": replacement.get("schema_id"),
            "status": replacement.get("status"),
            "ok": replacement.get("ok"),
            "target": replacement.get("target"),
            "candidate_body_summary_patch": replacement.get("candidate_body_summary_patch"),
            "invariants": replacement.get("invariants"),
            "blockers": replacement.get("blockers"),
            "body_omitted_from_plan": True,
        },
        "allowed_write_set_for_future_apply": [
            DEFAULT_PROJECTION_PATH.as_posix(),
            (DEFAULT_OUTPUT_DIR / "accepted_apply_receipts").as_posix(),
        ],
        "forbidden_write_sets": [
            "broad materialize_domain_weaver_projection side effects",
            "codex_solo",
            "chatgpt_connector/codex_work_requests",
            "production",
            "secrets",
            "git push",
        ],
        "required_apply_gate": {
            "confirmation": "ION_BOUNDED_WRITE_CONFIRMED",
            "idempotency_key_required": True,
            "agent_id_required": True,
            "live_worker_shift_lease_required": True,
            "lease_type": "exclusive_write",
            "required_lease_targets": [DEFAULT_PROJECTION_PATH.as_posix()],
            "execute_write_required": True,
            "replacement_body_sha256_required": True,
        },
        "blockers": blockers,
        "next_packets": [
            "PCKT-DOMAIN-WEAVER-PROJECTION-ACCEPTED-STATE-REPLACEMENT-BODY-BUILDER-V0_1",
            "PCKT-DOMAIN-WEAVER-PROJECTION-ACCEPTED-STATE-WRITE-APPLY-V0_1",
        ],
        "non_claims": [
            "This plan does not overwrite DOMAIN_WEAVER_PROJECTION.json.",
            "This plan does not grant accepted-state authority.",
            "This plan does not materialize topology.",
            "This plan does not start workers or process queues.",
            "Candidate evidence sha256 is not an accepted projection after-sha.",
        ],
    }


def build_projection_apply_gate_rebaseline_dryrun(
    active_root: str | Path,
    *,
    previous_plan_path: str | Path | None = None,
    generated_at: str | None = None,
    max_context_age_seconds: int | None = None,
) -> dict[str, Any]:
    """Build a no-write rebaseline packet for the projection apply gate.

    The packet compares the current projection hash against the previous latest
    accepted-refresh plan, then builds a fresh no-write plan and replacement
    body candidate for the current projection bytes.
    """

    root = Path(active_root).expanduser().resolve(strict=False)
    generated = generated_at or utc_now()
    projection_path = root / DEFAULT_PROJECTION_PATH
    previous_path = _repo_relative_or_absolute_path(root, previous_plan_path or DEFAULT_ACCEPTED_REFRESH_PLAN_PATH)
    previous_plan = read_json(previous_path)
    previous_target = mapping(previous_plan.get("target"))
    previous_before_sha256 = str(previous_target.get("before_sha256") or "")
    previous_after_sha256 = str(previous_target.get("after_sha256") or "")

    current_plan = build_projection_accepted_refresh_plan(
        root,
        generated_at=generated,
        max_context_age_seconds=max_context_age_seconds,
    )
    replacement = build_projection_replacement_body_candidate(
        root,
        generated_at=generated,
        max_context_age_seconds=max_context_age_seconds,
    )
    plan_target = mapping(current_plan.get("target"))
    replacement_target = mapping(replacement.get("target"))
    current_before_sha256 = str(plan_target.get("before_sha256") or sha256_file(projection_path) or "")
    current_after_sha256 = str(plan_target.get("after_sha256") or replacement_target.get("candidate_body_sha256") or "")
    previous_plan_exists = previous_path.is_file()
    previous_plan_stale = bool(previous_plan_exists and previous_before_sha256 and previous_before_sha256 != current_before_sha256)
    current_plan_target_current = bool(current_before_sha256 and current_before_sha256 == str(sha256_file(projection_path) or ""))

    blockers: list[dict[str, Any]] = [
        {
            "code": str(row.get("code")),
            "severity": str(row.get("severity") or "high"),
            "evidence": [str(item) for item in as_list(row.get("evidence"))],
        }
        for row in as_list(current_plan.get("blockers"))
        if isinstance(row, Mapping) and row.get("code")
    ]
    if previous_plan_stale:
        blockers.append(
            {
                "code": "projection_apply_previous_plan_stale_against_current_projection_sha",
                "severity": "high",
                "evidence": [
                    rel(previous_path, root),
                    previous_before_sha256,
                    current_before_sha256,
                ],
            }
        )
    blockers.append(
        {
            "code": "projection_apply_execute_write_not_requested",
            "severity": "info",
            "evidence": ["dry_run_only"],
        }
    )

    return {
        "schema_id": APPLY_GATE_REBASELINE_DRYRUN_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "projection_apply_gate_rebaseline_dryrun_built_no_write",
        "ok": True,
        "plan_ok": False,
        "apply_ready": False,
        "write_performed": False,
        "projection_overwrite_performed": False,
        "accepted_projection_write_performed": False,
        "mutates_active_state": False,
        "accepted_state_claim": False,
        "authority": dict(AUTHORITY),
        "target": {
            "path": DEFAULT_PROJECTION_PATH.as_posix(),
            "exists": projection_path.is_file(),
            "current_before_sha256": current_before_sha256,
            "current_after_candidate_sha256": current_after_sha256,
            "current_plan_target_current": current_plan_target_current,
            "write_performed": False,
        },
        "previous_plan": {
            "path": rel(previous_path, root),
            "exists": previous_plan_exists,
            "schema_id": previous_plan.get("schema_id"),
            "generated_at": previous_plan.get("generated_at"),
            "before_sha256": previous_before_sha256,
            "after_sha256": previous_after_sha256,
            "stale_against_current_projection_sha": previous_plan_stale,
        },
        "current_plan": {
            "schema_id": current_plan.get("schema_id"),
            "generated_at": current_plan.get("generated_at"),
            "status": current_plan.get("status"),
            "target": current_plan.get("target"),
            "blockers": current_plan.get("blockers"),
            "sha256": sha256_json(current_plan),
        },
        "replacement_body_candidate": {
            "schema_id": replacement.get("schema_id"),
            "generated_at": replacement.get("generated_at"),
            "status": replacement.get("status"),
            "ok": replacement.get("ok"),
            "target": replacement.get("target"),
            "invariants": replacement.get("invariants"),
            "blockers": replacement.get("blockers"),
            "candidate_body_omitted_from_dryrun": True,
        },
        "required_apply_gate": current_plan.get("required_apply_gate"),
        "blockers": blockers,
        "next_packets": [
            "PCKT-DOMAIN-WEAVER-PROJECTION-ACCEPTED-STATE-WRITE-GATE-DECISION-V0_1",
            "PCKT-DOMAIN-WEAVER-PROJECTION-APPLY-LEASED-EXECUTION-V0_1",
        ],
        "non_claims": [
            "This dry-run does not overwrite DOMAIN_WEAVER_PROJECTION.json.",
            "This dry-run does not grant accepted-state authority.",
            "This dry-run does not request execute_write.",
            "The replacement body candidate is written only as candidate evidence by the write helper.",
        ],
        "_embedded_current_plan": current_plan,
        "_embedded_replacement_body_candidate": replacement,
    }


def write_projection_apply_gate_rebaseline_dryrun(
    active_root: str | Path,
    *,
    previous_plan_path: str | Path | None = None,
    generated_at: str | None = None,
    max_context_age_seconds: int | None = None,
) -> dict[str, Any]:
    """Write current projection apply-gate rebaseline evidence without applying it."""

    root = Path(active_root).expanduser().resolve(strict=False)
    dryrun = build_projection_apply_gate_rebaseline_dryrun(
        root,
        previous_plan_path=previous_plan_path,
        generated_at=generated_at,
        max_context_age_seconds=max_context_age_seconds,
    )
    current_plan = dict(dryrun.pop("_embedded_current_plan"))
    replacement = dict(dryrun.pop("_embedded_replacement_body_candidate"))
    generated = str(dryrun["generated_at"])
    stamp = timestamp_for_filename(generated)

    output_dir = root / DEFAULT_OUTPUT_DIR
    operator_action_dir = root / DEFAULT_OPERATOR_ACTION_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    operator_action_dir.mkdir(parents=True, exist_ok=True)

    plan_json_path = root / DEFAULT_ACCEPTED_REFRESH_PLAN_PATH
    plan_report_path = output_dir / DEFAULT_ACCEPTED_REFRESH_PLAN_REPORT_NAME
    plan_snapshot_json_path = output_dir / f"{stamp}_projection_accepted_refresh_plan.json"
    plan_snapshot_report_path = output_dir / f"{stamp}_projection_accepted_refresh_plan.md"
    replacement_json_path = output_dir / DEFAULT_REPLACEMENT_BODY_CANDIDATE_NAME
    replacement_report_path = output_dir / DEFAULT_REPLACEMENT_BODY_CANDIDATE_REPORT_NAME
    replacement_snapshot_json_path = output_dir / f"{stamp}_projection_replacement_body_candidate.json"
    replacement_snapshot_report_path = output_dir / f"{stamp}_projection_replacement_body_candidate.md"
    dryrun_json_path = output_dir / DEFAULT_APPLY_GATE_REBASELINE_DRYRUN_NAME
    dryrun_report_path = output_dir / DEFAULT_APPLY_GATE_REBASELINE_DRYRUN_REPORT_NAME
    dryrun_snapshot_json_path = output_dir / f"{stamp}_projection_apply_gate_rebaseline_dryrun.json"
    dryrun_snapshot_report_path = output_dir / f"{stamp}_projection_apply_gate_rebaseline_dryrun.md"
    receipt_path = operator_action_dir / f"{stamp}_domain_weaver_projection_apply_gate_rebaseline_dryrun.json"

    artifacts = {
        "accepted_refresh_plan": rel(plan_json_path, root),
        "accepted_refresh_plan_report": rel(plan_report_path, root),
        "accepted_refresh_plan_snapshot": rel(plan_snapshot_json_path, root),
        "accepted_refresh_plan_snapshot_report": rel(plan_snapshot_report_path, root),
        "replacement_body_candidate": rel(replacement_json_path, root),
        "replacement_body_candidate_report": rel(replacement_report_path, root),
        "replacement_body_candidate_snapshot": rel(replacement_snapshot_json_path, root),
        "replacement_body_candidate_snapshot_report": rel(replacement_snapshot_report_path, root),
        "apply_gate_rebaseline_dryrun": rel(dryrun_json_path, root),
        "apply_gate_rebaseline_dryrun_report": rel(dryrun_report_path, root),
        "apply_gate_rebaseline_dryrun_snapshot": rel(dryrun_snapshot_json_path, root),
        "apply_gate_rebaseline_dryrun_snapshot_report": rel(dryrun_snapshot_report_path, root),
    }
    dryrun["artifacts"] = artifacts

    write_json(plan_json_path, current_plan)
    write_json(plan_snapshot_json_path, current_plan)
    write_text(plan_report_path, render_projection_accepted_refresh_plan_report(current_plan))
    write_text(plan_snapshot_report_path, render_projection_accepted_refresh_plan_report(current_plan))
    write_json(replacement_json_path, replacement)
    write_json(replacement_snapshot_json_path, replacement)
    write_text(replacement_report_path, render_projection_replacement_body_candidate_report(replacement))
    write_text(replacement_snapshot_report_path, render_projection_replacement_body_candidate_report(replacement))
    write_json(dryrun_json_path, dryrun)
    write_json(dryrun_snapshot_json_path, dryrun)
    write_text(dryrun_report_path, render_projection_apply_gate_rebaseline_dryrun_report(dryrun))
    write_text(dryrun_snapshot_report_path, render_projection_apply_gate_rebaseline_dryrun_report(dryrun))

    receipt = {
        "schema_id": "ion.domain_weaver.operator_action_receipt.v0_1",
        "receipt_type": "domain_weaver_projection_apply_gate_rebaseline_dryrun",
        "generated_at": generated,
        "result": "projection_apply_gate_rebaseline_dryrun_written_no_accepted_state",
        "active_root": str(root),
        "authority": dict(AUTHORITY),
        "artifacts": artifacts,
        "target": dryrun["target"],
        "previous_plan": dryrun["previous_plan"],
        "blockers": dryrun["blockers"],
        "non_claims": dryrun["non_claims"],
        "validation": [],
    }
    write_json(receipt_path, receipt)

    return {
        "schema_id": APPLY_GATE_REBASELINE_DRYRUN_WRITE_RESULT_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "json_path": rel(dryrun_json_path, root),
        "report_path": rel(dryrun_report_path, root),
        "snapshot_json_path": rel(dryrun_snapshot_json_path, root),
        "snapshot_report_path": rel(dryrun_snapshot_report_path, root),
        "accepted_refresh_plan_path": rel(plan_json_path, root),
        "accepted_refresh_plan_snapshot_path": rel(plan_snapshot_json_path, root),
        "replacement_body_candidate_path": rel(replacement_json_path, root),
        "replacement_body_candidate_snapshot_path": rel(replacement_snapshot_json_path, root),
        "operator_receipt_path": rel(receipt_path, root),
        "previous_plan_stale_against_current_projection_sha": dryrun["previous_plan"][
            "stale_against_current_projection_sha"
        ],
        "current_plan_target_current": dryrun["target"]["current_plan_target_current"],
        "projection_overwrite_performed": False,
        "accepted_projection_write_performed": False,
        "mutates_active_state": False,
        "accepted_state_claim": False,
        "authority": dict(AUTHORITY),
    }


def summarize_generated_mounts(root: Path) -> dict[str, Any]:
    mounts_root = root / DEFAULT_MOUNT_ROOT
    rows: list[dict[str, Any]] = []
    if mounts_root.is_dir():
        for mount in sorted(path for path in mounts_root.iterdir() if path.is_dir() and not path.name.startswith(".")):
            manifest_path = mount / "ION_AGENT_MOUNT_MANIFEST.json"
            if not manifest_path.is_file():
                continue
            manifest = read_json(manifest_path)
            identity = canonicalize_codex_mount_identity(mount.name, manifest)
            ion_dir = mount / ".ion"
            active_context_path = ion_dir / "ACTIVE_CONTEXT_PACKAGE.md"
            capsule_path = ion_dir / "ION_CONTEXT_CAPSULE.yaml"
            manifest_domain_id = str(identity.get("manifest_domain_id") or identity.get("raw_domain_id") or "").strip()
            manifest_role_id = str(identity.get("manifest_role_id") or identity.get("raw_role_id") or "").strip()
            row = {
                "mount_id": mount.name,
                "mount_path": rel(mount, root),
                "manifest_path": rel(manifest_path, root),
                "manifest_domain_id": manifest_domain_id or None,
                "manifest_role_id": manifest_role_id or None,
                "raw_domain_id": identity.get("raw_domain_id"),
                "canonical_domain_id": identity.get("canonical_domain_id"),
                "domain_alias_detected": identity.get("domain_alias_detected"),
                "semantic_identity": identity,
                "active_context_package_path": rel(active_context_path, root),
                "active_context_package_exists": active_context_path.is_file(),
                "capsule_path": rel(capsule_path, root),
                "capsule_exists": capsule_path.is_file(),
            }
            row["manifest_only"] = not row["active_context_package_exists"] and not row["capsule_exists"]
            rows.append(row)

    manifest_only_mounts = [row for row in rows if row["manifest_only"]]
    semantic_alias_mounts = [
        row
        for row in rows
        if row["mount_id"].endswith("__ion_vnext_front_door")
        or str(row.get("manifest_domain_id") or "") in set(VNEXT_FRONT_DOOR_ALIASES)
        or row.get("canonical_domain_id") == VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID
    ]
    return {
        "mount_root": DEFAULT_MOUNT_ROOT.as_posix(),
        "manifest_count": len(rows),
        "active_context_package_count": sum(1 for row in rows if row["active_context_package_exists"]),
        "capsule_count": sum(1 for row in rows if row["capsule_exists"]),
        "manifest_only_mount_count": len(manifest_only_mounts),
        "manifest_only_mounts": manifest_only_mounts,
        "semantic_alias_mounts": semantic_alias_mounts,
    }


def summarize_preflight(preflight: Mapping[str, Any]) -> dict[str, Any]:
    target_mounts = as_list(preflight.get("target_mounts"))
    mount_refs = as_list(preflight.get("mount_package_refs_requiring_reissue"))
    return {
        "path": (DEFAULT_ACTIVE_CONTEXT_REFRESH_DIR / DEFAULT_PREFLIGHT_JSON_NAME).as_posix(),
        "schema_id": preflight.get("schema_id"),
        "generated_at": preflight.get("generated_at"),
        "inspected_mount_count": int(preflight.get("inspected_mount_count") or 0),
        "target_mount_count": int(preflight.get("target_mount_count") or len(target_mounts)),
        "target_mount_ids": [
            str(row.get("mount_id"))
            for row in target_mounts
            if isinstance(row, Mapping) and row.get("mount_id")
        ],
        "mount_package_refs_requiring_reissue_count": int(
            preflight.get("mount_package_refs_requiring_reissue_count") or len(mount_refs)
        ),
        "refresh_run": bool(preflight.get("refresh_run")),
        "mutates_active_state": bool(preflight.get("mutates_active_state")),
        "next_packet": "PCKT-DOMAIN-WEAVER-ACTIVE-CONTEXT-GATED-REFRESH-V0_1",
        "blockers": [str(item) for item in as_list(preflight.get("blockers"))],
    }


def summarize_exact_active_binding(root: Path) -> dict[str, Any]:
    payload = read_json(root / DEFAULT_ACTIVE_BINDING_PATH)
    summary = mapping(payload.get("summary"))
    required = int(summary.get("required_specialist_binding_count") or 0)
    proved = int(summary.get("exact_active_binding_proved_count") or summary.get("exact_active_binding_count") or 0)
    missing = int(summary.get("missing_exact_active_binding_count") or max(0, required - proved))
    return {
        "source": DEFAULT_ACTIVE_BINDING_PATH.as_posix(),
        "required": required,
        "proved": proved,
        "missing": missing,
        "state": "candidate_complete_not_materialization_authority" if required and proved >= required and missing == 0 else "incomplete",
        "materialization_ready": bool(summary.get("materialization_ready")),
    }


def build_context_graph_deltas(
    *,
    exact_active: Mapping[str, Any],
    mount_census: Mapping[str, Any],
    preflight_summary: Mapping[str, Any],
    route_summary: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_id": CONTEXT_DELTA_SCHEMA_ID,
        "write_performed": False,
        "accepted_state_moved": False,
        "authority": dict(AUTHORITY),
        "mark_stale": [
            {
                "id": "domain_weaver.DOMAIN_WEAVER_PROJECTION",
                "reason": "older_than_latest_2026_06_04_receipts",
                "evidence": [DEFAULT_PROJECTION_PATH.as_posix()],
            },
            {
                "id": "domain_weaver.ready_review.STEWARD_READY_REVIEW",
                "reason": "older_than_latest_2026_06_04_receipts",
                "evidence": [DEFAULT_READY_REVIEW_PATH.as_posix()],
            },
        ],
        "upsert_claims": [
            {
                "id": "domain_weaver.exact_active_bindings.candidate_complete",
                "state": "proved_candidate_not_accepted",
                "value": {
                    "required": exact_active.get("required"),
                    "proved": exact_active.get("proved"),
                    "missing": exact_active.get("missing"),
                },
            },
            {
                "id": "domain_weaver.route_gate_matrix.domain_weaver_declared_gates",
                "state": "declared_registry_gates_strong_for_domain_weaver_mutations",
                "value": {
                    "domain_weaver_gapped_mutating_route_count": int(
                        route_summary.get("domain_weaver_gapped_mutating_route_count") or 0
                    ),
                    "handler_parity_proven": False,
                },
            },
            {
                "id": "domain_weaver.active_context_mounts.current_census",
                "state": "gated_reissue_required",
                "value": {
                    "manifest_count": mount_census.get("manifest_count"),
                    "active_context_package_count": mount_census.get("active_context_package_count"),
                    "manifest_only_mount_count": mount_census.get("manifest_only_mount_count"),
                    "preflight_target_mount_count": preflight_summary.get("target_mount_count"),
                    "mount_package_refs_requiring_reissue_count": preflight_summary.get(
                        "mount_package_refs_requiring_reissue_count"
                    ),
                },
            },
            {
                "id": "domain_weaver.semantic_branch_identity.vnext_front_door",
                "state": "canonicalization_required",
                "value": {
                    "canonical": VNEXT_FRONT_DOOR_CANONICAL_DOMAIN_ID,
                    "aliases": list(VNEXT_FRONT_DOOR_ALIASES),
                },
            },
            {
                "id": "domain_weaver.materialization_ready",
                "state": "blocked_false",
                "value": {
                    "accepted_state_authority": False,
                    "materialization_authority": False,
                    "refresh_run": False,
                },
            },
        ],
        "emit_edges": [
            {
                "from": "domain_weaver.active_context_mounts.current_census",
                "relation": "requires_gated_refresh_before",
                "to": "domain_weaver.self_evolution.semantic_branch_fabric",
            },
            {
                "from": "domain_weaver.route_gate_matrix.domain_weaver_declared_gates",
                "relation": "insufficient_without_handler_parity_for",
                "to": "domain_weaver.serious_self_evolution_readiness",
            },
            {
                "from": "domain_weaver.exact_active_bindings.candidate_complete",
                "relation": "insufficient_without_accepted_settlement_for",
                "to": "domain_weaver.materialization_ready",
            },
        ],
    }


def build_blockers(
    *,
    projection_stale: bool,
    source_projection: Mapping[str, Any],
    mount_census: Mapping[str, Any],
    preflight_summary: Mapping[str, Any],
    route_summary: Mapping[str, Any],
    exact_active: Mapping[str, Any],
) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    if projection_stale:
        blockers.append(blocker("DOMAIN_WEAVER_PROJECTION_STALE", "high", DEFAULT_PROJECTION_PATH.as_posix()))
    if preflight_summary.get("target_mount_count"):
        blockers.append(blocker("ACTIVE_CONTEXT_REISSUE_REQUIRED", "high", preflight_summary.get("path")))
    if mount_census.get("manifest_only_mount_count"):
        blockers.append(blocker("MANIFEST_ONLY_MOUNTS_NOT_WORKING_CAPSULES", "high", DEFAULT_MOUNT_ROOT.as_posix()))
    if mount_census.get("semantic_alias_mounts"):
        blockers.append(blocker("SEMANTIC_BRANCH_ID_DRIFT", "high", DEFAULT_MOUNT_ROOT.as_posix()))
    if int(route_summary.get("domain_weaver_gapped_mutating_route_count") or 0) > 0:
        blockers.append(blocker("DOMAIN_WEAVER_DECLARED_MUTATION_GATE_GAPS", "critical", "ION/03_registry"))
    blockers.append(blocker("HANDLER_WRITE_SET_PARITY_NOT_PROVEN", "high", "ION/03_registry/ion_action_mcp_branch_leader_registry.yaml"))
    projection_summary = mapping(source_projection.get("summary"))
    if projection_summary.get("self_evolution_ready") is False:
        blockers.append(blocker("SELF_EVOLUTION_READY_FALSE_IN_PROJECTION", "critical", DEFAULT_PROJECTION_PATH.as_posix()))
    if projection_summary.get("self_evolution_lattice_executable") is False:
        blockers.append(blocker("SELF_EVOLUTION_LATTICE_NOT_EXECUTABLE", "critical", DEFAULT_PROJECTION_PATH.as_posix()))
    if exact_active.get("materialization_ready") is not True:
        blockers.append(blocker("MATERIALIZATION_READY_FALSE", "critical", str(exact_active.get("source") or "")))
    return blockers


def blocker(code: str, severity: str, evidence: Any) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "evidence": [str(evidence)] if evidence else [],
    }


def render_projection_refresh_report(payload: Mapping[str, Any]) -> str:
    source = mapping(payload.get("source_projection"))
    mount = mapping(payload.get("mount_census"))
    preflight = mapping(payload.get("active_context_reissue_preflight"))
    route = mapping(payload.get("route_gate_matrix"))
    exact = mapping(payload.get("exact_active_binding_candidate"))
    lines = [
        "# Domain Weaver Projection Refresh Candidate",
        "",
        f"Generated: `{payload.get('generated_at')}`",
        "",
        "Authority: candidate-only. This does not overwrite `DOMAIN_WEAVER_PROJECTION.json`, refresh mounts, materialize topology, start workers, or move accepted state.",
        "",
        "## Source Projection",
        "",
        f"- path: `{source.get('path')}`",
        f"- generated_at: `{source.get('generated_at')}`",
        f"- latest receipt: `{source.get('latest_receipt_path')}`",
        f"- stale against latest receipts: `{source.get('stale_against_latest_receipts')}`",
        "",
        "## Current Evidence",
        "",
        f"- exact-active bindings: `{exact.get('proved')}/{exact.get('required')}` candidate-proven, still not materialization authority",
        f"- generated mounts: `{mount.get('manifest_count')}` manifests, `{mount.get('active_context_package_count')}` active context packages, `{mount.get('manifest_only_mount_count')}` manifest-only mounts",
        f"- active-context reissue preflight: `{preflight.get('target_mount_count')}` target mounts and `{preflight.get('mount_package_refs_requiring_reissue_count')}` refs requiring gated refresh",
        f"- Domain Weaver mutating route declared gate gaps: `{route.get('domain_weaver_gapped_mutating_route_count')}`; handler parity still not fully proven",
        "",
        "## Manifest-Only Mounts",
        "",
    ]
    manifest_only = as_list(mount.get("manifest_only_mounts"))
    if manifest_only:
        for row in manifest_only:
            if isinstance(row, Mapping):
                lines.append(f"- `{row.get('mount_id')}`: domain `{row.get('manifest_domain_id')}`")
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Candidate Deltas",
        "",
        "- mark projection and ready review stale",
        "- preserve materialization_ready=false",
        "- preserve exact-active 6/6 as candidate substrate only",
        "- canonicalize vNext front-door to `domain.vnext_front_door`",
        "- require gated active-context refresh before self-evolution semantic branch fabric",
        "",
        "## Blockers",
        "",
    ])
    for row in as_list(payload.get("blockers")):
        if isinstance(row, Mapping):
            lines.append(f"- `{row.get('severity')}` `{row.get('code')}`")
    lines.extend([
        "",
        "## Next Packets",
        "",
    ])
    for packet in as_list(payload.get("next_packets")):
        lines.append(f"- `{packet}`")
    return "\n".join(lines) + "\n"


def render_preflight_report(preflight: Mapping[str, Any]) -> str:
    lines = [
        "# Active Context Reissue Preflight Current",
        "",
        f"Generated: `{preflight.get('generated_at')}`",
        "",
        "Authority: candidate-only and no-write. This preflight does not refresh mounts, materialize topology, start workers, or move accepted state.",
        "",
        "## Summary",
        "",
        f"- inspected mounts: `{preflight.get('inspected_mount_count')}`",
        f"- target mounts requiring gated refresh: `{preflight.get('target_mount_count')}`",
        f"- mount package refs requiring reissue: `{preflight.get('mount_package_refs_requiring_reissue_count')}`",
        f"- refresh run: `{preflight.get('refresh_run')}`",
        "- next packet: `PCKT-DOMAIN-WEAVER-ACTIVE-CONTEXT-GATED-REFRESH-V0_1`",
        "",
        "## Target Mounts",
        "",
    ]
    target_mounts = [
        row.get("mount_id")
        for row in as_list(preflight.get("target_mounts"))
        if isinstance(row, Mapping) and row.get("mount_id")
    ]
    if target_mounts:
        for mount_id in target_mounts:
            lines.append(f"- `{mount_id}`")
    else:
        lines.append("- none")
    lines.extend([
        "",
        "## Blockers",
        "",
    ])
    for item in as_list(preflight.get("blockers")):
        lines.append(f"- `{item}`")
    return "\n".join(lines) + "\n"


def render_projection_accepted_refresh_plan_report(plan: Mapping[str, Any]) -> str:
    target = mapping(plan.get("target"))
    replacement = mapping(plan.get("replacement_body_candidate"))
    replacement_target = mapping(replacement.get("target"))
    required_gate = mapping(plan.get("required_apply_gate"))
    lines = [
        "# Domain Weaver Projection Accepted Refresh Plan",
        "",
        f"Generated: `{plan.get('generated_at')}`",
        "",
        "Authority: candidate-only. This plan does not overwrite `DOMAIN_WEAVER_PROJECTION.json` or grant accepted-state authority.",
        "",
        "## Target",
        "",
        f"- path: `{target.get('path')}`",
        f"- exists: `{target.get('exists')}`",
        f"- before sha256: `{target.get('before_sha256')}`",
        f"- candidate after sha256: `{target.get('after_sha256')}`",
        f"- after status: `{target.get('after_sha256_status')}`",
        "",
        "## Replacement Body Candidate",
        "",
        f"- schema: `{replacement.get('schema_id')}`",
        f"- ok: `{replacement.get('ok')}`",
        f"- body omitted from plan: `{replacement.get('body_omitted_from_plan')}`",
        f"- candidate body sha256: `{replacement_target.get('candidate_body_sha256')}`",
        "",
        "## Required Future Apply Gate",
        "",
        f"- bounded confirmation: `{required_gate.get('confirmation')}`",
        f"- execute write required: `{required_gate.get('execute_write_required')}`",
        f"- replacement body sha256 required: `{required_gate.get('replacement_body_sha256_required')}`",
        "",
        "## Blockers",
        "",
    ]
    for row in as_list(plan.get("blockers")):
        if isinstance(row, Mapping):
            lines.append(f"- `{row.get('severity')}` `{row.get('code')}`")
    lines.extend([
        "",
        "## Non-Claims",
        "",
    ])
    for claim in as_list(plan.get("non_claims")):
        lines.append(f"- {claim}")
    return "\n".join(lines) + "\n"


def render_projection_replacement_body_candidate_report(candidate: Mapping[str, Any]) -> str:
    target = mapping(candidate.get("target"))
    summary_patch = mapping(candidate.get("candidate_body_summary_patch"))
    invariants = mapping(candidate.get("invariants"))
    lines = [
        "# Domain Weaver Projection Replacement Body Candidate",
        "",
        f"Generated: `{candidate.get('generated_at')}`",
        "",
        "Authority: candidate-only. This does not overwrite `DOMAIN_WEAVER_PROJECTION.json`.",
        "",
        "## Target",
        "",
        f"- path: `{target.get('path')}`",
        f"- exists: `{target.get('exists')}`",
        f"- before sha256: `{target.get('before_sha256')}`",
        f"- candidate body sha256: `{target.get('candidate_body_sha256')}`",
        f"- write performed: `{target.get('write_performed')}`",
        "",
        "## Summary Patch",
        "",
    ]
    for key in sorted(summary_patch):
        lines.append(f"- `{key}`: `{summary_patch.get(key)}`")
    lines.extend([
        "",
        "## Invariants",
        "",
        f"- ok: `{invariants.get('ok')}`",
        f"- failures: `{invariants.get('failures')}`",
        "",
        "## Blockers",
        "",
    ])
    for row in as_list(candidate.get("blockers")):
        if isinstance(row, Mapping):
            lines.append(f"- `{row.get('severity')}` `{row.get('code')}`")
    lines.extend([
        "",
        "## Non-Claims",
        "",
    ])
    for claim in as_list(candidate.get("non_claims")):
        lines.append(f"- {claim}")
    return "\n".join(lines) + "\n"


def render_projection_apply_gate_rebaseline_dryrun_report(dryrun: Mapping[str, Any]) -> str:
    target = mapping(dryrun.get("target"))
    previous = mapping(dryrun.get("previous_plan"))
    current = mapping(dryrun.get("current_plan"))
    artifacts = mapping(dryrun.get("artifacts"))
    lines = [
        "# Domain Weaver Projection Apply Gate Rebaseline Dry-Run",
        "",
        f"Generated: `{dryrun.get('generated_at')}`",
        "",
        "Authority: candidate-only. This dry-run does not apply the accepted projection refresh.",
        "",
        "## Target",
        "",
        f"- path: `{target.get('path')}`",
        f"- current before sha256: `{target.get('current_before_sha256')}`",
        f"- current candidate after sha256: `{target.get('current_after_candidate_sha256')}`",
        f"- current plan target current: `{target.get('current_plan_target_current')}`",
        f"- write performed: `{target.get('write_performed')}`",
        "",
        "## Previous Plan",
        "",
        f"- path: `{previous.get('path')}`",
        f"- exists: `{previous.get('exists')}`",
        f"- previous before sha256: `{previous.get('before_sha256')}`",
        f"- stale against current projection sha: `{previous.get('stale_against_current_projection_sha')}`",
        "",
        "## Current Plan",
        "",
        f"- schema: `{current.get('schema_id')}`",
        f"- status: `{current.get('status')}`",
        f"- sha256: `{current.get('sha256')}`",
        "",
        "## Artifacts",
        "",
    ]
    if artifacts:
        for key in sorted(artifacts):
            lines.append(f"- `{key}`: `{artifacts.get(key)}`")
    else:
        lines.append("- none written")
    lines.extend([
        "",
        "## Blockers",
        "",
    ])
    for row in as_list(dryrun.get("blockers")):
        if isinstance(row, Mapping):
            lines.append(f"- `{row.get('severity')}` `{row.get('code')}`")
    lines.extend([
        "",
        "## Non-Claims",
        "",
    ])
    for claim in as_list(dryrun.get("non_claims")):
        lines.append(f"- {claim}")
    return "\n".join(lines) + "\n"


def latest_operator_receipt(root: Path) -> dict[str, str]:
    action_dir = root / DEFAULT_OPERATOR_ACTION_DIR
    rows: list[dict[str, str]] = []
    if action_dir.is_dir():
        for path in action_dir.glob("*.json"):
            receipt_at = receipt_time_from_name(path.name)
            if receipt_at:
                rows.append({"path": rel(path, root), "receipt_at": receipt_at})
    rows.sort(key=lambda row: row["receipt_at"], reverse=True)
    return rows[0] if rows else {"path": "", "receipt_at": ""}


def receipt_time_from_name(name: str) -> str:
    prefix = name.split("_", 1)[0]
    try:
        parsed = datetime.strptime(prefix, "%Y%m%dT%H%M%SZ")
    except ValueError:
        return ""
    return parsed.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def is_older_than(left: str, right: str) -> bool:
    left_dt = parse_time(left)
    right_dt = parse_time(right)
    if left_dt is None or right_dt is None:
        return False
    return left_dt < right_dt


def parse_time(value: str) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def timestamp_for_filename(value: str) -> str:
    parsed = parse_time(value)
    if parsed is None:
        return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return parsed.strftime("%Y%m%dT%H%M%SZ")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def sha256_json(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(dict(payload), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def json_write_text(payload: Mapping[str, Any]) -> str:
    return json.dumps(dict(payload), indent=2, sort_keys=True) + "\n"


def _projection_replacement_invariants(candidate_body: Mapping[str, Any]) -> dict[str, Any]:
    summary = mapping(candidate_body.get("summary"))
    authority = mapping(candidate_body.get("authority"))
    failures: list[str] = []
    for key in (
        "accepted_state_authority",
        "production_authority",
        "live_execution_authority",
        "secrets_authority",
    ):
        if candidate_body.get(key) is not False:
            failures.append(f"top_level_{key}_must_be_false")
        if authority.get(key) is not False:
            failures.append(f"authority_{key}_must_be_false")
    for key in (
        "full_domain_weaver_ready",
        "self_evolution_ready",
        "self_evolution_lattice_executable",
        "serious_self_evolution_ready",
        "autonomous_self_evolution_ready",
        "production_ready",
        "projection_accepted_apply_ready",
        "projection_accepted_state_write_gate_granted",
        "context_active_resolver_materialize_all_allowed",
        "worker_start_ready_to_start_workers",
        "worker_start_general_queue_processing_allowed",
        "semantic_alias_accepted_apply_gate_granted",
    ):
        if summary.get(key) is not False:
            failures.append(f"summary_{key}_must_be_false")
    section = mapping(candidate_body.get("accepted_refresh_replacement_candidate"))
    if section.get("write_performed") is not False:
        failures.append("replacement_section_write_performed_must_be_false")
    if section.get("accepted_state_claim") is not False:
        failures.append("replacement_section_accepted_state_claim_must_be_false")
    return {
        "ok": not failures,
        "failures": failures,
        "checked": [
            "no accepted-state authority",
            "no production/live/secrets authority",
            "blocked readiness flags remain false",
            "no projection write performed",
            "no general queue processing enabled",
        ],
    }


def projection_apply_authority(write_performed: bool) -> dict[str, Any]:
    return {
        "candidate_context_only": not write_performed,
        "accepted_state_authority": bool(write_performed),
        "accepted_state_authority_scope": (
            "domain_weaver_projection_file_only" if write_performed else "not_granted"
        ),
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "materialization_authority": False,
        "projection_overwrite_performed": bool(write_performed),
    }


def _load_projection_replacement_body(
    root: Path,
    *,
    replacement_body: Mapping[str, Any] | None,
    replacement_body_path: str | Path | None,
) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    blockers: list[str] = []
    path_text = str(replacement_body_path or "").strip()
    if replacement_body is not None and path_text:
        blockers.append("projection_apply_replacement_body_single_source_required")
    if replacement_body is None and not path_text:
        return {}, {"source": "missing"}, ["projection_apply_replacement_body_required"]
    if replacement_body is not None:
        return dict(replacement_body), {"source": "inline_replacement_body"}, blockers

    raw = Path(path_text)
    if raw.is_absolute() or any(part == ".." for part in raw.parts):
        return {}, {"source": "replacement_body_path", "path": path_text}, [
            *blockers,
            "projection_apply_replacement_body_path_must_be_repo_relative_without_escape",
        ]
    resolved = (root / raw).resolve(strict=False)
    try:
        rel_path = resolved.relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return {}, {"source": "replacement_body_path", "path": path_text}, [
            *blockers,
            "projection_apply_replacement_body_path_outside_active_root",
        ]
    payload = read_json(resolved)
    if not payload:
        return {}, {"source": "replacement_body_path", "path": rel_path}, [
            *blockers,
            "projection_apply_replacement_body_path_missing_or_invalid_json",
        ]
    candidate_body = payload.get("candidate_body")
    if isinstance(candidate_body, Mapping):
        return dict(candidate_body), {
            "source": "replacement_body_candidate_artifact",
            "path": rel_path,
            "artifact_schema_id": payload.get("schema_id"),
        }, blockers
    return payload, {"source": "replacement_body_path", "path": rel_path}, blockers


def _projection_apply_live_lease_gate(
    root: Path,
    *,
    agent_id: str,
    lease_id: str,
    target_paths: list[str],
) -> dict[str, Any]:
    try:
        from .ion_worker_shift_presence import require_active_edit_lease
    except Exception as exc:  # pragma: no cover - fail closed import guard
        return {
            "schema_id": "ion.domain_weaver.projection_apply.live_lease_gate.v0_1",
            "ok": False,
            "finding": "projection_apply_live_lease_gate_unavailable",
            "error_type": type(exc).__name__,
            "blockers": ["projection_apply_live_lease_gate_unavailable"],
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
        "schema_id": "ion.domain_weaver.projection_apply.live_lease_gate.v0_1",
        "ok": bool(public_gate.get("ok")),
        "finding": public_gate.get("finding"),
        "required_target_paths": target_paths,
        "worker_shift_gate": public_gate,
        "blockers": _projection_apply_live_lease_blockers(public_gate),
        "authority": dict(AUTHORITY),
    }


def _projection_apply_live_lease_blockers(gate: Mapping[str, Any]) -> list[str]:
    if gate.get("ok") is True:
        return []
    worker_gate = mapping(gate.get("worker_shift_gate")) or gate
    blockers: list[str] = []
    finding = str(worker_gate.get("finding") or gate.get("finding") or "").strip()
    if finding == "active_edit_lease_not_found":
        blockers.append("projection_apply_live_lease_not_found")
    elif finding == "active_edit_lease_invalid":
        blockers.append("projection_apply_live_lease_invalid")
    elif finding:
        blockers.append(str(finding))
    for blocker in as_list(worker_gate.get("blockers")):
        text = str(blocker or "").strip()
        if text == "lease_agent_mismatch":
            blockers.append("projection_apply_live_lease_actor_mismatch")
        elif text == "lease_type_mismatch":
            blockers.append("projection_apply_live_lease_mode_mismatch")
        elif text == "lease_missing_target_coverage":
            blockers.append("projection_apply_live_lease_target_coverage_incomplete")
        elif text == "lease_not_fresh":
            blockers.append("projection_apply_live_lease_stale")
        elif text == "lease_identity_binding_blocked":
            blockers.append("projection_apply_live_lease_identity_blocked")
        elif text:
            blockers.append(text)
    if not blockers:
        blockers.append("projection_apply_live_lease_gate_failed")
    return unique_texts(blockers)


def _projection_apply_receipt_path(root: Path, idempotency_key: str) -> Path:
    safe_key = "".join(
        ch if ch.isalnum() or ch in {"-", "_"} else "_"
        for ch in str(idempotency_key or "").strip()
    )[:96] or "projection_apply"
    return root / DEFAULT_ACCEPTED_REFRESH_APPLY_RECEIPT_DIR / f"{safe_key}.json"


def file_digest_row(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"exists": False, "sha256": "", "bytes": 0}
    data = path.read_bytes()
    return {
        "exists": True,
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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


def _identity_is_unbound(value: Any) -> bool:
    normalized = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    return normalized in {"", "anonymous", "none", "null", "unknown", "unbound", "unbound_worker_id"}


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _repo_relative_or_absolute_path(root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate.resolve(strict=False)
    return (root / candidate).resolve(strict=False)


def ids_from_mount_name(name: str) -> tuple[str, str]:
    left, marker, right = name.partition("__")
    if not marker:
        return "", ""
    role_id = f"role.{left[len('role_'):]}" if left.startswith("role_") else ""
    domain_id = f"domain.{right[len('domain_'):]}" if right.startswith("domain_") else ""
    return role_id, domain_id


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Active ION root")
    parser.add_argument("--generated-at", default="", help="Override generated_at")
    parser.add_argument("--max-context-age-seconds", type=int, default=48 * 60 * 60)
    parser.add_argument("--write", action="store_true", help="Write candidate artifacts and receipt")
    parser.add_argument(
        "--apply-gate-rebaseline-dryrun",
        action="store_true",
        help="Build projection apply-gate rebaseline dry-run evidence instead of the generic refresh candidate",
    )
    parser.add_argument(
        "--write-apply-gate-rebaseline-dryrun",
        action="store_true",
        help="Write projection apply-gate rebaseline dry-run evidence and receipt",
    )
    parser.add_argument(
        "--previous-plan-path",
        default="",
        help="Optional previous accepted-refresh plan path for rebaseline currentness comparison",
    )
    args = parser.parse_args(argv)
    if args.write_apply_gate_rebaseline_dryrun:
        result = write_projection_apply_gate_rebaseline_dryrun(
            args.root,
            previous_plan_path=args.previous_plan_path or None,
            generated_at=args.generated_at or None,
            max_context_age_seconds=args.max_context_age_seconds,
        )
    elif args.apply_gate_rebaseline_dryrun:
        result = build_projection_apply_gate_rebaseline_dryrun(
            args.root,
            previous_plan_path=args.previous_plan_path or None,
            generated_at=args.generated_at or None,
            max_context_age_seconds=args.max_context_age_seconds,
        )
        result.pop("_embedded_current_plan", None)
        result.pop("_embedded_replacement_body_candidate", None)
    elif args.write:
        result = write_projection_refresh_candidate(
            args.root,
            generated_at=args.generated_at or None,
            max_context_age_seconds=args.max_context_age_seconds,
        )
    else:
        result = build_projection_refresh_candidate(
            args.root,
            generated_at=args.generated_at or None,
            max_context_age_seconds=args.max_context_age_seconds,
        )
        result.pop("_embedded_preflight", None)
        result.pop("_embedded_route_gate_matrix", None)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
