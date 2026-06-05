"""Domain Weaver self-evolution readiness projection.

This module reads current active-root evidence and writes candidate-only
readiness artifacts. It does not import ``ion_domain_weaver``, start workers,
process the Codex queue, move accepted state, materialize topology, or claim
product acceptance.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA_ID = "ion.domain_weaver.self_evolution_readiness.v0_1"
CONTEXT_DELTA_SCHEMA_ID = "ion.domain_weaver.self_evolution.context_graph_deltas.v0_1_candidate"
WRITE_RESULT_SCHEMA_ID = "ion.domain_weaver.self_evolution_readiness.write_result.v0_1"

DEFAULT_CONTEXT_ROOT = Path("ION/05_context/current/domain_weaver")
DEFAULT_OUTPUT_DIR = DEFAULT_CONTEXT_ROOT / "self_evolution_readiness"
DEFAULT_JSON_NAME = "DOMAIN_WEAVER_SELF_EVOLUTION_READINESS.latest.json"
DEFAULT_REPORT_NAME = "DOMAIN_WEAVER_SELF_EVOLUTION_READINESS_REPORT.latest.md"
DEFAULT_CONTEXT_DELTA_NAME = "DOMAIN_WEAVER_SELF_EVOLUTION_CONTEXT_GRAPH_DELTAS.latest.candidate.json"

CAPSULE_PATH = DEFAULT_CONTEXT_ROOT / ".ion/ION_CONTEXT_CAPSULE.yaml"
PROJECTION_PATH = DEFAULT_CONTEXT_ROOT / "DOMAIN_WEAVER_PROJECTION.json"
PROMOTION_REVIEW_PATH = DEFAULT_CONTEXT_ROOT / "PROMOTION_REVIEW.json"
PROMOTION_GATE_PATH = DEFAULT_CONTEXT_ROOT / "PROMOTION_GATE.json"
PROMOTION_STALENESS_SEAL_PATH = DEFAULT_CONTEXT_ROOT / "LEGACY_PROMOTION_DOC_STALENESS_SEAL_20260604.md"
STEWARD_READY_REVIEW_PATH = DEFAULT_CONTEXT_ROOT / "ready_review/STEWARD_READY_REVIEW.json"
LARGER_FANOUT_READINESS_PATH = (
    DEFAULT_CONTEXT_ROOT / "larger_fanout/DOMAIN_WEAVER_LARGER_FANOUT_CONTROL_READINESS.latest.json"
)
ACTIVE_BINDING_ROWS_PATH = (
    DEFAULT_CONTEXT_ROOT / "live_carrier_binding/ACTIVE_INVOKABLE_BINDING_PROOF_ROWS.candidate.json"
)
MONOLITH_INDEX_PATH = DEFAULT_CONTEXT_ROOT / "monolith_index/DOMAIN_WEAVER_MONOLITH_INDEX.latest.json"
QUEUE_PATH = Path("ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json")
QUEUE_RUNNER_STATE_PATH = Path("ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json")
LATEST_LARGER_FANOUT_PATCH_RECEIPT = (
    DEFAULT_CONTEXT_ROOT / "operator_actions/20260604T042751Z_domain_weaver_larger_fanout_control_plane_patch_validated.json"
)
NATIVE_SUBAGENT_RECEIPT = (
    DEFAULT_CONTEXT_ROOT / "operator_actions/20260604T040700Z_domain_weaver_native_subagent_transcript_bridge_live_dogfood_settlement.json"
)
RECURSIVE_SPAWN_PROBE_RECEIPT = (
    DEFAULT_CONTEXT_ROOT / "operator_actions/20260604T041925Z_domain_weaver_recursive_native_spawn_probe_no_child_available.json"
)

AUTHORITY = {
    "candidate_context_only": True,
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "materialization_authority": False,
    "git_push_authority": False,
}

NON_CLAIMS = [
    "Worker returns are carrier intake only.",
    "Candidate graph deltas are not accepted state.",
    "Readiness is not product-state acceptance.",
    "This projection does not start workers or process the general queue.",
    "This projection does not move registry, materialization, topology, UI, production, live, secrets, or git state.",
]


def build_self_evolution_readiness(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a candidate-only self-evolution readiness projection."""

    root = Path(active_root).expanduser().resolve(strict=False)
    generated = generated_at or utc_now()
    root_proof = active_root_proof(root)

    capsule = parse_capsule(root, root / CAPSULE_PATH)
    projection = read_json(root / PROJECTION_PATH)
    projection_summary = mapping(projection.get("summary"))
    promotion_review = read_json(root / PROMOTION_REVIEW_PATH)
    promotion_gate = read_json(root / PROMOTION_GATE_PATH)
    ready_review = read_json(root / STEWARD_READY_REVIEW_PATH)
    fanout = read_json(root / LARGER_FANOUT_READINESS_PATH)
    active_bindings = read_json(root / ACTIVE_BINDING_ROWS_PATH)
    monolith_index = read_json(root / MONOLITH_INDEX_PATH)
    mount_summary = summarize_generated_mounts(root)
    queue = read_json(root / QUEUE_PATH)
    queue_runner_state = read_json(root / QUEUE_RUNNER_STATE_PATH)
    latest_fanout_receipt = read_json(root / LATEST_LARGER_FANOUT_PATCH_RECEIPT)
    native_receipt = read_json(root / NATIVE_SUBAGENT_RECEIPT)
    recursive_probe = read_json(root / RECURSIVE_SPAWN_PROBE_RECEIPT)

    operator_receipts = latest_operator_receipts(root)
    latest_receipt_at = operator_receipts[0]["receipt_at"] if operator_receipts else ""
    projection_generated_at = str(projection.get("generated_at") or "")
    ready_review_created_at = str(ready_review.get("created_at") or "")

    queue_summary = summarize_queue(queue, queue_runner_state)
    validation_summary = summarize_validations(latest_fanout_receipt)
    context_delta = build_context_graph_deltas(
        active_bindings=active_bindings,
        fanout=fanout,
        native_receipt=native_receipt,
        projection_summary=projection_summary,
        projection_generated_at=projection_generated_at,
        latest_receipt_at=latest_receipt_at,
    )

    blockers = build_blockers(
        root_proof=root_proof,
        capsule=capsule,
        projection_summary=projection_summary,
        projection_generated_at=projection_generated_at,
        ready_review_created_at=ready_review_created_at,
        latest_receipt_at=latest_receipt_at,
        fanout=fanout,
        native_receipt=native_receipt,
        recursive_probe=recursive_probe,
        validation_summary=validation_summary,
        queue_summary=queue_summary,
        active_bindings=active_bindings,
        monolith_index=monolith_index,
        mount_summary=mount_summary,
    )

    verdict = self_evolution_verdict(blockers)
    supervised_candidate_wave_allowed = bool(fanout.get("readiness_ok")) and not any(
        blocker["code"] == "ROOT_PROOF_MISSING" for blocker in blockers
    )

    passed_validations = [
        {
            "id": "active_root_required_siblings",
            "result": "passed" if root_proof["proof_ok"] else "failed",
            "evidence": ["pyproject.toml", "ION/REPO_AUTHORITY.md"],
        },
        {
            "id": "larger_fanout_focused_validation",
            "result": "passed" if validation_summary["focused_passed"] else "not_proven",
            "evidence": [LATEST_LARGER_FANOUT_PATCH_RECEIPT.as_posix()],
        },
        {
            "id": "larger_fanout_candidate_gate",
            "result": "passed" if bool(fanout.get("readiness_ok")) else "failed",
            "evidence": [LARGER_FANOUT_READINESS_PATH.as_posix()],
        },
        {
            "id": "queue_runner_idle_projection",
            "result": "passed" if queue_summary["active_run_count"] == 0 else "failed",
            "evidence": [QUEUE_RUNNER_STATE_PATH.as_posix()],
        },
    ]
    failed_or_broader_risk_validations = [
        row
        for row in [
            validation_summary.get("broad_suite"),
            {
                "id": "automatic_original_agent_reaction",
                "result": "failed",
                "detail": "alternate-worker recovery chain is proven, original Codex worker automatic reaction is not",
                "evidence": [NATIVE_SUBAGENT_RECEIPT.as_posix()],
            },
            {
                "id": "materialization_readiness",
                "result": "failed",
                "detail": "candidate exact-active substrate is insufficient without accepted settlement and materialization gate",
                "evidence": [ACTIVE_BINDING_ROWS_PATH.as_posix(), PROJECTION_PATH.as_posix()],
            },
            {
                "id": "route_action_parity_for_spawn_dispatch",
                "result": "not_proven",
                "detail": "spawn-row enqueue exists, but action-route parity and policy freshness are not yet proven",
                "evidence": [LATEST_LARGER_FANOUT_PATCH_RECEIPT.as_posix()],
            },
        ]
        if row
    ]

    return {
        "schema_id": SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "context_root": DEFAULT_CONTEXT_ROOT.as_posix(),
        "root_proof": root_proof,
        "authority": AUTHORITY,
        "verdict": verdict,
        "supervised_candidate_wave_allowed": supervised_candidate_wave_allowed,
        "supervised_candidate_wave_ceiling": {
            "max_candidate_lane_count": int(fanout.get("max_candidate_lane_count") or 0),
            "recursive_native_spawn_allowed": bool(fanout.get("recursive_native_spawn_allowed")),
            "state_movement_allowed": False,
        },
        "capsule": capsule,
        "projection": {
            "path": PROJECTION_PATH.as_posix(),
            "generated_at": projection_generated_at,
            "latest_operator_receipt_at": latest_receipt_at,
            "stale_against_latest_receipt": timestamp_less_than(projection_generated_at, latest_receipt_at),
            "summary": pick(
                projection_summary,
                [
                    "full_domain_weaver_ready",
                    "self_evolution_ready",
                    "self_evolution_lattice_executable",
                    "materialization_ready",
                    "exact_active_specialist_binding_count",
                    "queue_request_count",
                    "queue_stale_waiting_request_count",
                    "live_return_complete",
                    "ui_operator_usable",
                    "ui_development_ready",
                    "operator_action_record_count",
                    "original_plan_blocker_count",
                ],
            ),
        },
        "promotion_surfaces": {
            "review_path": PROMOTION_REVIEW_PATH.as_posix(),
            "gate_path": PROMOTION_GATE_PATH.as_posix(),
            "staleness_seal_path": PROMOTION_STALENESS_SEAL_PATH.as_posix(),
            "review_status": promotion_review.get("promotion_status"),
            "gate_status": promotion_gate.get("gate_status"),
            "candidate_only": True,
            "sealed_as_historical_candidate_language": (root / PROMOTION_STALENESS_SEAL_PATH).is_file(),
        },
        "queue_state": queue_summary,
        "generated_mounts": mount_summary,
        "latest_operator_receipts": operator_receipts[:12],
        "validations": {
            "passed": passed_validations,
            "failed_or_broader_risk": failed_or_broader_risk_validations,
        },
        "blockers_ranked": blockers,
        "candidate_context_graph_deltas": context_delta,
        "next_packets": next_packets(),
        "nemesis_dissent": nemesis_dissent(blockers, queue_summary, validation_summary),
        "source_evidence": evidence_checks(root),
        "non_claims": NON_CLAIMS,
    }


def write_self_evolution_readiness(
    active_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    generated_at: str | None = None,
    write_receipt: bool = True,
) -> dict[str, Any]:
    """Write readiness JSON, Markdown report, context deltas, and receipt."""

    root = Path(active_root).expanduser().resolve(strict=False)
    readiness = build_self_evolution_readiness(root, generated_at=generated_at)
    out_dir = Path(output_dir) if output_dir is not None else root / DEFAULT_OUTPUT_DIR
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / DEFAULT_JSON_NAME
    report_path = out_dir / DEFAULT_REPORT_NAME
    delta_path = out_dir / DEFAULT_CONTEXT_DELTA_NAME
    json_text = stable_json(readiness)
    report_text = render_report(readiness)
    delta_text = stable_json(readiness["candidate_context_graph_deltas"])
    json_path.write_text(json_text, encoding="utf-8")
    report_path.write_text(report_text, encoding="utf-8")
    delta_path.write_text(delta_text, encoding="utf-8")

    result = {
        "schema_id": WRITE_RESULT_SCHEMA_ID,
        "generated_at": readiness["generated_at"],
        "json_path": rel(json_path, root),
        "json_sha256": sha256_text(json_text),
        "report_path": rel(report_path, root),
        "report_sha256": sha256_text(report_text),
        "context_graph_delta_path": rel(delta_path, root),
        "context_graph_delta_sha256": sha256_text(delta_text),
        "verdict": readiness["verdict"],
        "supervised_candidate_wave_allowed": readiness["supervised_candidate_wave_allowed"],
        "blocker_count": len(readiness["blockers_ranked"]),
        "authority": AUTHORITY,
    }
    if write_receipt:
        receipt_path = write_operator_receipt(root, result, readiness)
        result["operator_receipt_path"] = receipt_path
    return result


def build_blockers(
    *,
    root_proof: Mapping[str, Any],
    capsule: Mapping[str, Any],
    projection_summary: Mapping[str, Any],
    projection_generated_at: str,
    ready_review_created_at: str,
    latest_receipt_at: str,
    fanout: Mapping[str, Any],
    native_receipt: Mapping[str, Any],
    recursive_probe: Mapping[str, Any],
    validation_summary: Mapping[str, Any],
    queue_summary: Mapping[str, Any],
    active_bindings: Mapping[str, Any],
    monolith_index: Mapping[str, Any],
    mount_summary: Mapping[str, Any],
) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    if not bool(root_proof.get("proof_ok")):
        blockers.append(blocker("critical", "ROOT_PROOF_MISSING", "Active root proof is incomplete.", []))

    if capsule.get("materialization_ready") is False:
        blockers.append(
            blocker(
                "critical",
                "MATERIALIZATION_READY_FALSE",
                "Folder-local capsule preserves materialization_ready=false.",
                [CAPSULE_PATH.as_posix()],
            )
        )
    if projection_summary.get("self_evolution_ready") is False:
        blockers.append(
            blocker(
                "critical",
                "SELF_EVOLUTION_READY_FALSE_IN_PROJECTION",
                "Current projection still says self_evolution_ready=false.",
                [PROJECTION_PATH.as_posix()],
            )
        )
    if projection_summary.get("self_evolution_lattice_executable") is False:
        blockers.append(
            blocker(
                "critical",
                "SELF_EVOLUTION_LATTICE_NOT_EXECUTABLE",
                "Current projection still says self_evolution_lattice_executable=false.",
                [PROJECTION_PATH.as_posix()],
            )
        )
    proof_projection = mapping(native_receipt.get("proof_projection"))
    if proof_projection.get("automatic_agent_reaction_proven") is not True:
        blockers.append(
            blocker(
                "critical",
                "AUTOMATIC_ORIGINAL_AGENT_REACTION_NOT_PROVEN",
                "Alternate-worker recovery chain is proven, but original automatic Codex worker reaction is not.",
                [NATIVE_SUBAGENT_RECEIPT.as_posix()],
            )
        )
    if timestamp_less_than(projection_generated_at, latest_receipt_at):
        blockers.append(
            blocker(
                "high",
                "DOMAIN_WEAVER_PROJECTION_STALE",
                f"Projection generated at {projection_generated_at or 'unknown'} is older than latest receipt {latest_receipt_at or 'unknown'}.",
                [PROJECTION_PATH.as_posix()],
            )
        )
    if timestamp_less_than(ready_review_created_at, latest_receipt_at):
        blockers.append(
            blocker(
                "high",
                "STEWARD_READY_REVIEW_STALE",
                f"Steward ready review created at {ready_review_created_at or 'unknown'} is older than latest receipt {latest_receipt_at or 'unknown'}.",
                [STEWARD_READY_REVIEW_PATH.as_posix()],
            )
        )
    broad = validation_summary.get("broad_suite") or {}
    if broad.get("result") == "failed":
        blockers.append(
            blocker(
                "high",
                "BROAD_CONNECTOR_FANOUT_VALIDATION_FAILED",
                str(broad.get("detail") or "Broader combined validation failed."),
                [LATEST_LARGER_FANOUT_PATCH_RECEIPT.as_posix()],
            )
        )
    if bool(fanout.get("recursive_native_spawn_allowed")) is False:
        blockers.append(
            blocker(
                "high",
                "RECURSIVE_NATIVE_SPAWN_NOT_AVAILABLE",
                "Current recursive native-spawn probe did not prove child-spawn availability.",
                [RECURSIVE_SPAWN_PROBE_RECEIPT.as_posix()],
            )
        )
    if queue_summary.get("queued_request_count", 0) > 0:
        blockers.append(
            blocker(
                "high",
                "GENERAL_QUEUE_HAS_PENDING_REQUESTS",
                "Queue has pending requests; self-evolution starts must use exact request-path or explicit lane scope.",
                [QUEUE_PATH.as_posix()],
            )
        )
    if int(mapping(active_bindings.get("summary")).get("exact_active_binding_count") or 0) == 0:
        blockers.append(
            blocker(
                "high",
                "EXACT_ACTIVE_BINDINGS_NOT_PROVEN",
                "No exact-active bindings are proven in candidate proof rows.",
                [ACTIVE_BINDING_ROWS_PATH.as_posix()],
            )
        )
    if mapping(active_bindings.get("summary")).get("materialization_ready") is False:
        blockers.append(
            blocker(
                "high",
                "EXACT_ACTIVE_SUBSTRATE_NOT_MATERIALIZATION_AUTHORITY",
                "Exact-active candidate substrate exists but still does not grant materialization authority.",
                [ACTIVE_BINDING_ROWS_PATH.as_posix()],
            )
        )
    monolith_summary = mapping(monolith_index.get("summary"))
    if int(monolith_summary.get("dispatcher_branch_action_count") or 0) > 0:
        blockers.append(
            blocker(
                "high",
                "MUTATION_ROUTE_COVERAGE_NOT_SYSTEMIC",
                "Monolith/action surface is broad; mutation-route gate coverage is not yet proven systemic.",
                [MONOLITH_INDEX_PATH.as_posix()],
            )
        )
    if int(mount_summary.get("stale_or_missing_active_context_count") or 0) > 0:
        blockers.append(
            blocker(
                "high",
                "ACTIVE_CONTEXT_MOUNT_REISSUE_REQUIRED",
                "Generated mounts include stale or missing active contexts; semantic branch fabric is not clean for self-evolution.",
                [Path(mount_summary.get("mount_root", "")).as_posix()],
            )
        )
    if int(mount_summary.get("manifest_only_mount_count") or 0) > 0:
        blockers.append(
            blocker(
                "high",
                "MANIFEST_ONLY_MOUNTS_NOT_WORKING_CAPSULES",
                "Some mounts have manifests but no active context package; manifests must not be treated as working capsules.",
                [Path(mount_summary.get("mount_root", "")).as_posix()],
            )
        )
    if bool(mount_summary.get("semantic_alias_drift_detected")):
        blockers.append(
            blocker(
                "high",
                "SEMANTIC_BRANCH_ID_DRIFT",
                "vNext front-door branch appears under multiple domain identifiers; canonicalization is required before self-evolution fabric uses these identities.",
                [
                    PROMOTION_REVIEW_PATH.as_posix(),
                    PROJECTION_PATH.as_posix(),
                    Path(mount_summary.get("mount_root", "")).as_posix(),
                ],
            )
        )
    blockers.append(
        blocker(
            "high",
            "SPAWN_DISPATCH_ACTION_ROUTE_PARITY_NOT_PROVEN",
            "Spawn-row enqueue exists, but confirmation/idempotency/agent/write-intent parity with action routes is not yet proven.",
            [LATEST_LARGER_FANOUT_PATCH_RECEIPT.as_posix()],
        )
    )
    if projection_summary.get("ui_operator_usable") is False:
        blockers.append(
            blocker(
                "medium",
                "UI_OPERATOR_USABLE_FALSE",
                "Projection still says ui_operator_usable=false; UI/topology resume remains blocked.",
                [PROJECTION_PATH.as_posix()],
            )
        )
    return sorted(blockers, key=lambda row: severity_rank(row["severity"]))


def build_context_graph_deltas(
    *,
    active_bindings: Mapping[str, Any],
    fanout: Mapping[str, Any],
    native_receipt: Mapping[str, Any],
    projection_summary: Mapping[str, Any],
    projection_generated_at: str,
    latest_receipt_at: str,
) -> dict[str, Any]:
    binding_summary = mapping(active_bindings.get("summary"))
    proof_projection = mapping(native_receipt.get("proof_projection"))
    return {
        "schema_id": CONTEXT_DELTA_SCHEMA_ID,
        "write_performed": False,
        "delta_kind": "candidate_readiness_proof_graph_delta",
        "upsert_claims": [
            {
                "id": "domain_weaver.exact_active_bindings.candidate_complete",
                "state": "proved_candidate",
                "value": {
                    "required": int(binding_summary.get("required_specialist_binding_count") or 0),
                    "proved": int(binding_summary.get("exact_active_binding_proved_count") or 0),
                    "missing": int(binding_summary.get("missing_exact_active_binding_count") or 0),
                    "delegated": int(binding_summary.get("delegated_active_binding_count") or 0),
                    "boot_only": int(binding_summary.get("candidate_boot_only_count") or 0),
                },
                "evidence": [ACTIVE_BINDING_ROWS_PATH.as_posix()],
            },
            {
                "id": "domain_weaver.materialization_ready",
                "state": "blocked_false",
                "blockers": [
                    "operator_decision_required",
                    "candidate_substrate_not_accepted_state",
                    "materialization_authority_false",
                    "self_evolution_lattice_not_executable",
                ],
                "evidence": [CAPSULE_PATH.as_posix(), PROJECTION_PATH.as_posix()],
            },
            {
                "id": "domain_weaver.comms.autoreaction",
                "state": "alternate_worker_recovery_chain_proven_original_reaction_unproven",
                "proof_state": proof_projection.get("proof_state"),
                "automatic_agent_reaction_proven": bool(proof_projection.get("automatic_agent_reaction_proven")),
                "evidence": [NATIVE_SUBAGENT_RECEIPT.as_posix()],
            },
            {
                "id": "domain_weaver.larger_fanout_control_plane",
                "state": "proved_candidate_focused_only",
                "max_candidate_lane_count": int(fanout.get("max_candidate_lane_count") or 0),
                "recursive_native_spawn_allowed": bool(fanout.get("recursive_native_spawn_allowed")),
                "evidence": [LARGER_FANOUT_READINESS_PATH.as_posix()],
            },
            {
                "id": "domain_weaver.projection.currentness",
                "state": "stale_against_latest_receipts"
                if timestamp_less_than(projection_generated_at, latest_receipt_at)
                else "current_against_latest_receipts",
                "projection_generated_at": projection_generated_at,
                "latest_receipt_at": latest_receipt_at,
                "self_evolution_ready": projection_summary.get("self_evolution_ready"),
                "evidence": [PROJECTION_PATH.as_posix()],
            },
            {
                "id": "domain_weaver.active_context_mounts",
                "state": "reissue_required_before_self_evolution",
                "blockers": [
                    "stale_or_missing_active_context_packages",
                    "manifest_only_mounts_not_working_capsules",
                ],
                "evidence": ["ION/05_context/current/codex_agent_mounts"],
            },
            {
                "id": "domain_weaver.semantic_branch_identity.vnext_front_door",
                "state": "canonicalization_required",
                "aliases": [
                    "ion_vnext_front_door",
                    "domain.vnext_front_door",
                    "domain.ion_vnext_front_door_authority",
                ],
                "evidence": [PROMOTION_REVIEW_PATH.as_posix(), PROJECTION_PATH.as_posix()],
            },
            {
                "id": "codex_solo.domain_weaver_context",
                "state": "fallback_only_stale_for_domain_weaver",
                "evidence": [CAPSULE_PATH.as_posix()],
            },
        ],
        "mark_stale": [
            {
                "id": "domain_weaver.DOMAIN_WEAVER_PROJECTION",
                "reason": "older_than_latest_2026_06_04_operator_receipts",
                "evidence": [PROJECTION_PATH.as_posix()],
            },
            {
                "id": "domain_weaver.ready_review.STEWARD_READY_REVIEW",
                "reason": "older_than_latest_2026_06_04_operator_receipts",
                "evidence": [STEWARD_READY_REVIEW_PATH.as_posix()],
            },
            {
                "id": "domain_weaver.PROMOTION_REVIEW_AND_GATE_READY_LANGUAGE",
                "reason": "sealed_as_historical_candidate_language_not_current_readiness",
                "evidence": [PROMOTION_STALENESS_SEAL_PATH.as_posix()],
            },
            {
                "id": "codex_solo.shared_fallback_context",
                "reason": "not_folder_local_unique_working_capsule_for_domain_weaver",
                "evidence": [CAPSULE_PATH.as_posix()],
            },
        ],
        "emit_edges": [
            {
                "from": "domain_weaver.exact_active_bindings.candidate_complete",
                "to": "domain_weaver.materialization_ready",
                "relation": "insufficient_without_accepted_settlement",
            },
            {
                "from": "domain_weaver.comms.alternate_worker_recovery",
                "to": "domain_weaver.automatic_original_agent_reaction",
                "relation": "does_not_prove",
            },
            {
                "from": "domain_weaver.larger_fanout_control_plane",
                "to": "domain_weaver.serious_self_evolution_readiness",
                "relation": "insufficient_focused_candidate_gate_only",
            },
            {
                "from": "domain_weaver.spawn_dispatch_enqueue",
                "to": "domain_weaver.action_route_parity",
                "relation": "requires_confirmation_idempotency_agent_write_intent_gate_proof",
            },
            {
                "from": "domain_weaver.active_context_mounts",
                "to": "domain_weaver.self_evolution.semantic_branch_fabric",
                "relation": "blocks_until_reissued",
            },
            {
                "from": "domain_weaver.semantic_branch_identity.vnext_front_door",
                "to": "domain_weaver.self_evolution.semantic_branch_fabric",
                "relation": "requires_canonicalization",
            },
        ],
    }


def next_packets() -> dict[str, list[dict[str, str]]]:
    return {
        "A_must_fix_before_serious_self_evolution": [
            packet("PCKT-DOMAIN-WEAVER-COMMS-AUTOREACTION-PROOF-V0_2", "Prove original automatic Codex worker reaction or preserve false."),
            packet("PCKT-DOMAIN-WEAVER-SELF-EVOLUTION-PROJECTION-REFRESH-V0_1", "Refresh projection, ready review, and staleness seals from 2026-06-04 receipts."),
            packet("PCKT-DOMAIN-WEAVER-LARGER-FANOUT-CONTROL-PLANE-V0_2", "Add wave ledger, backlog caps, route parity, policy freshness, provenance gates, and fan-in settlement."),
            packet("PCKT-MANDATORY-EDIT-LEASE-GATE-COVERAGE-V0_2", "Prove mutation-gate coverage for every non-read-only Domain Weaver branch/action route."),
            packet("PCKT-DOMAIN-WEAVER-BROAD-CONNECTOR-FANOUT-VALIDATION-REPAIR-V0_1", "Resolve or formally classify the 17 broad-suite failures."),
            packet("PCKT-DOMAIN-WEAVER-MATERIALIZATION-READINESS-SETTLEMENT-FANIN-CANDIDATE-ONLY-20260603-ATTEMPT-001", "Keep materialization blocked until an explicit accepted settlement exists."),
        ],
        "B_can_run_during_supervised_self_evolution": [
            packet("PCKT-DOMAIN-WEAVER-SUBAGENT-PROVENANCE-VERIFIER-V0_1", "Generalize native/alternate worker provenance verification."),
            packet("PCKT-DOMAIN-WEAVER-NATIVE-SUBAGENT-TRANSCRIPT-BRIDGE-FANIN-V0_2", "Fan in native transcript bridge evidence without product-state claims."),
            packet("PCKT-DOMAIN-WEAVER-MONOLITH-DECOMPOSITION-SEAM-CARTOGRAPHY-READ-ONLY-20260603-ATTEMPT-001", "Continue read-only seam cartography and proof-first extraction planning."),
            packet("PCKT-DOMAIN-WEAVER-CONTEXT-GRAPH-DELTA-HYDRATION-V0_1", "Hydrate candidate context deltas into a reviewable graph, still not accepted state."),
            packet("PCKT-DOMAIN-WEAVER-ACTION-ROUTE-PARITY-AUDIT-V0_1", "Audit branch/gateway/tool policy parity as read-only or candidate-only work."),
        ],
        "C_later_hardening": [
            packet("PCKT-DOMAIN-WEAVER-DOMAIN-OWNED-SELF-REPAIR-ROUTING-V0_1", "Enable domain-owned repair only after A-gates pass."),
            packet("PCKT-DOMAIN-WEAVER-SELF-REPAIR-WATCHED-TRIAL-V0_1", "Run watched self-repair after entry conditions are satisfied."),
            packet("PCKT-DOMAIN-WEAVER-TRUE-NAME-DOMAIN-STEWARD-SYSTEM-V0_1", "Harden role/domain identity semantics."),
            packet("PCKT-DOMAIN-WEAVER-UI-OPERATOR-USABILITY-SETTLEMENT-V0_1", "Unblock UI/operator usability after fresh proof and operator rejection supersession."),
            packet("PCKT-DOMAIN-WEAVER-RECURSIVE-NATIVE-SPAWN-ONE-CHILD-PROBE-V0_1", "Re-test recursive native spawning only if the carrier exposes child spawn tools."),
        ],
    }


def self_evolution_verdict(blockers: Sequence[Mapping[str, Any]]) -> str:
    serious_blocker_codes = {
        str(row.get("code"))
        for row in blockers
        if row.get("severity") in {"critical", "high"}
    }
    if serious_blocker_codes:
        return (
            "NOT_READY_BLOCKED_BY_AUTOMATIC_REACTION_PROOF_STALE_PROJECTION_"
            "MATERIALIZATION_GATE_MUTATION_COVERAGE_AND_BROAD_VALIDATION"
        )
    return "READY_FOR_SUPERVISED_SELF_EVOLUTION_CANDIDATE_WAVE"


def nemesis_dissent(
    blockers: Sequence[Mapping[str, Any]],
    queue_summary: Mapping[str, Any],
    validation_summary: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "verdict": "dissent_sustained",
        "summary": (
            "No clearance for serious self-evolution. Current evidence supports only a bounded "
            "candidate-control-plane slice capped at three lanes, with no recursive native spawn, "
            "no accepted state, and no materialization or registry movement."
        ),
        "must_not_overclaim": [
            "alternate worker recovery is not original automatic agent reaction",
            "focused tests are not systemic validation",
            "candidate exact-active bindings are not materialization authority",
            "promotion-ready wording is historical candidate language",
            "general queue processing would risk wrong-work execution",
        ],
        "queue_risk": {
            "queued_request_count": queue_summary.get("queued_request_count"),
            "active_run_count": queue_summary.get("active_run_count"),
            "required_start_policy": "exact_request_path_or_explicit_lane_scope_only",
        },
        "validation_risk": validation_summary.get("broad_suite"),
        "dissent_blocker_codes": [str(row.get("code")) for row in blockers[:10]],
    }


def summarize_validations(latest_fanout_receipt: Mapping[str, Any]) -> dict[str, Any]:
    rows = latest_fanout_receipt.get("validation")
    validations = rows if isinstance(rows, list) else []
    focused_passed = any(
        row.get("result") == "passed" and "focused" in str(row.get("command", "")).lower()
        for row in validations
        if isinstance(row, Mapping)
    )
    broad_suite = None
    for row in validations:
        if not isinstance(row, Mapping):
            continue
        command = str(row.get("command") or "")
        output = str(row.get("output") or "")
        if row.get("result") == "failed" or "failed" in output:
            broad_suite = {
                "id": "broad_connector_worker_dispatcher_larger_fanout_suite",
                "result": "failed",
                "command": command,
                "detail": output or "broader suite failed",
                "evidence": [LATEST_LARGER_FANOUT_PATCH_RECEIPT.as_posix()],
            }
    return {
        "focused_passed": focused_passed,
        "broad_suite": broad_suite,
        "raw_validation_count": len(validations),
    }


def summarize_queue(queue: Mapping[str, Any], queue_runner_state: Mapping[str, Any]) -> dict[str, Any]:
    requests = queue.get("requests")
    rows = requests if isinstance(requests, list) else []
    queued_rows = [row for row in rows if isinstance(row, Mapping) and row.get("status") == "QUEUED_FOR_CODEX_CARRIER"]
    domain_weaver_rows = [
        row
        for row in rows
        if isinstance(row, Mapping)
        and ("domain_weaver" in str(row.get("work_class", "")).lower() or "domain weaver" in str(row.get("objective", "")).lower())
    ]
    active_run = queue_runner_state.get("active_run")
    return {
        "queue_path": QUEUE_PATH.as_posix(),
        "runner_state_path": QUEUE_RUNNER_STATE_PATH.as_posix(),
        "request_count": int(queue.get("request_count") or len(rows)),
        "queued_request_count": len(queued_rows),
        "domain_weaver_request_count": len(domain_weaver_rows),
        "active_run_count": 1 if active_run else 0,
        "active_process_running": bool(active_run),
        "general_queue_processing_allowed_for_self_evolution": False,
        "required_start_policy": "exact_request_path_or_explicit_lane_scope_only",
        "queued_request_ids": [str(row.get("request_id") or "") for row in queued_rows[:20]],
    }


def summarize_generated_mounts(root: Path) -> dict[str, Any]:
    mount_root = root / "ION/05_context/current/codex_agent_mounts"
    mount_dirs = [path for path in sorted(mount_root.iterdir()) if path.is_dir()] if mount_root.is_dir() else []
    visible_mount_dirs = [path for path in mount_dirs if not path.name.startswith(".")]
    active_contexts = [path for path in visible_mount_dirs if (path / "ACTIVE_CONTEXT_PACKAGE.md").is_file()]
    manifests = [path for path in visible_mount_dirs if (path / "ION_AGENT_MOUNT_MANIFEST.json").is_file()]
    manifest_only = [
        path
        for path in visible_mount_dirs
        if (path / "ION_AGENT_MOUNT_MANIFEST.json").is_file()
        and not (path / "ACTIVE_CONTEXT_PACKAGE.md").is_file()
    ]
    hidden_dirs = [path.name for path in mount_dirs if path.name.startswith(".")]
    alias_names = []
    for path in visible_mount_dirs:
        if "ion_vnext_front_door" in path.name or "vnext_front_door" in path.name:
            alias_names.append(path.name)
    return {
        "mount_root": "ION/05_context/current/codex_agent_mounts",
        "inspected_dir_count": len(visible_mount_dirs),
        "hidden_dir_count": len(hidden_dirs),
        "hidden_dirs_excluded": hidden_dirs,
        "active_context_package_count": len(active_contexts),
        "manifest_count": len(manifests),
        "manifest_only_mount_count": len(manifest_only),
        "manifest_only_mounts": [rel(path, root) for path in manifest_only],
        "stale_or_missing_active_context_count": max(0, len(visible_mount_dirs) - len(active_contexts)),
        "semantic_alias_drift_detected": bool(alias_names),
        "semantic_alias_mounts": alias_names,
        "working_capsule_rule": "require_folder_local_ACTIVE_CONTEXT_PACKAGE_not_manifest_only",
    }


def parse_capsule(root: Path, path: Path) -> dict[str, Any]:
    text = read_text(path)
    values: dict[str, Any] = {"path": rel(path, root) if path.exists() else path.as_posix(), "present": path.is_file()}
    for line in text.splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        key, raw = line.split(":", 1)
        key = key.strip()
        raw_value = raw.strip()
        if key in {"context_id", "focus", "last_refreshed_at", "current_blocker", "active_root", "context_root"}:
            values[key] = raw_value
        elif key in {"materialization_ready", "shared_codex_solo_is_working_capsule"}:
            values[key] = raw_value.lower() == "true"
    return values


def latest_operator_receipts(root: Path) -> list[dict[str, Any]]:
    action_dir = root / DEFAULT_CONTEXT_ROOT / "operator_actions"
    if not action_dir.is_dir():
        return []
    rows = []
    for path in sorted(action_dir.glob("*.json"), reverse=True):
        receipt_at = timestamp_from_filename(path.name)
        rows.append(
            {
                "path": rel(path, root),
                "receipt_at": receipt_at,
                "sha256": sha256_file(path),
            }
        )
    return rows


def evidence_checks(root: Path) -> dict[str, dict[str, Any]]:
    paths = [
        CAPSULE_PATH,
        PROJECTION_PATH,
        PROMOTION_REVIEW_PATH,
        PROMOTION_GATE_PATH,
        PROMOTION_STALENESS_SEAL_PATH,
        STEWARD_READY_REVIEW_PATH,
        LARGER_FANOUT_READINESS_PATH,
        ACTIVE_BINDING_ROWS_PATH,
        MONOLITH_INDEX_PATH,
        QUEUE_PATH,
        QUEUE_RUNNER_STATE_PATH,
        LATEST_LARGER_FANOUT_PATCH_RECEIPT,
        NATIVE_SUBAGENT_RECEIPT,
        RECURSIVE_SPAWN_PROBE_RECEIPT,
    ]
    result: dict[str, dict[str, Any]] = {}
    for rel_path in paths:
        path = root / rel_path
        result[rel_path.as_posix()] = {
            "present": path.is_file(),
            "sha256": sha256_file(path) if path.is_file() else "",
        }
    return result


def render_report(readiness: Mapping[str, Any]) -> str:
    lines = [
        "# Domain Weaver Self-Evolution Readiness Report",
        "",
        f"Generated: `{readiness.get('generated_at')}`",
        f"Verdict: `{readiness.get('verdict')}`",
        f"Supervised candidate wave allowed: `{str(bool(readiness.get('supervised_candidate_wave_allowed'))).lower()}`",
        "",
        "Authority: candidate-only. No accepted-state, production, live execution, secrets, materialization, topology/UI, destructive, or git-push authority is granted.",
        "",
        "## Decision",
        "",
        "Domain Weaver is useful for bounded supervised candidate waves, but it is not ready for serious self-evolution. The current safe ceiling is a capped candidate-control-plane slice, not autonomous state movement.",
        "",
        "## Blockers Ranked",
        "",
    ]
    for row in readiness.get("blockers_ranked") or []:
        lines.append(f"- `{row.get('severity')}` `{row.get('code')}`: {row.get('detail')}")
    lines.extend(["", "## Passed Validations", ""])
    for row in mapping(readiness.get("validations")).get("passed") or []:
        lines.append(f"- `{row.get('id')}`: `{row.get('result')}`")
    lines.extend(["", "## Failed Or Broader-Risk Validations", ""])
    for row in mapping(readiness.get("validations")).get("failed_or_broader_risk") or []:
        lines.append(f"- `{row.get('id')}`: `{row.get('result')}` - {row.get('detail', '')}")
    lines.extend(["", "## Candidate Context Graph Deltas", ""])
    deltas = mapping(readiness.get("candidate_context_graph_deltas"))
    for claim in deltas.get("upsert_claims") or []:
        lines.append(f"- `{claim.get('id')}` -> `{claim.get('state')}`")
    lines.extend(["", "## Next Packets", ""])
    for group, packets in mapping(readiness.get("next_packets")).items():
        lines.append(f"### {group}")
        for row in packets:
            lines.append(f"- `{row.get('packet_id')}`: {row.get('purpose')}")
        lines.append("")
    lines.extend(["## Nemesis Dissent", ""])
    dissent = mapping(readiness.get("nemesis_dissent"))
    lines.append(str(dissent.get("summary") or "No dissent recorded."))
    lines.extend(["", "Nemesis must-not-overclaim list:"])
    for item in dissent.get("must_not_overclaim") or []:
        lines.append(f"- {item}")
    lines.extend(["", "## Non-Claims", ""])
    for item in readiness.get("non_claims") or []:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def write_operator_receipt(root: Path, result: Mapping[str, Any], readiness: Mapping[str, Any]) -> str:
    receipt_dir = root / DEFAULT_CONTEXT_ROOT / "operator_actions"
    receipt_dir.mkdir(parents=True, exist_ok=True)
    stamp = timestamp_for_filename(str(readiness.get("generated_at") or utc_now()))
    receipt_path = receipt_dir / f"{stamp}_domain_weaver_self_evolution_readiness_swarm_fanin.json"
    receipt = {
        "schema_id": "ion.domain_weaver.operator_action_receipt.v0_1",
        "action": "domain_weaver_self_evolution_readiness_swarm_fanin",
        "generated_at": readiness.get("generated_at"),
        "result": "candidate_readiness_report_written",
        "verdict": readiness.get("verdict"),
        "supervised_candidate_wave_allowed": readiness.get("supervised_candidate_wave_allowed"),
        "artifact_paths": {
            "json": result.get("json_path"),
            "report": result.get("report_path"),
            "context_graph_delta": result.get("context_graph_delta_path"),
        },
        "blocker_count": len(readiness.get("blockers_ranked") or []),
        "hard_boundaries": AUTHORITY,
        "non_claims": NON_CLAIMS,
    }
    receipt_text = stable_json(receipt)
    receipt_path.write_text(receipt_text, encoding="utf-8")
    return rel(receipt_path, root)


def blocker(severity: str, code: str, detail: str, evidence: Sequence[str]) -> dict[str, Any]:
    return {"severity": severity, "code": code, "detail": detail, "evidence": list(evidence)}


def packet(packet_id: str, purpose: str) -> dict[str, str]:
    return {"packet_id": packet_id, "purpose": purpose}


def active_root_proof(root: Path) -> dict[str, Any]:
    pyproject = root / "pyproject.toml"
    repo_authority = root / "ION/REPO_AUTHORITY.md"
    return {
        "schema_id": "ion.active_root_proof.v0_1_candidate",
        "active_root": str(root),
        "required_siblings": {
            "pyproject.toml": pyproject.is_file(),
            "ION/REPO_AUTHORITY.md": repo_authority.is_file(),
        },
        "proof_ok": pyproject.is_file() and repo_authority.is_file(),
    }


def severity_rank(severity: str) -> int:
    return {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(severity, 9)


def pick(payload: Mapping[str, Any], keys: Sequence[str]) -> dict[str, Any]:
    return {key: payload.get(key) for key in keys if key in payload}


def mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return dict(value) if isinstance(value, Mapping) else {}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def stable_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def timestamp_from_filename(name: str) -> str:
    prefix = name.split("_", 1)[0]
    if len(prefix) == 16 and prefix.endswith("Z") and "T" in prefix:
        return (
            f"{prefix[0:4]}-{prefix[4:6]}-{prefix[6:8]}T"
            f"{prefix[9:11]}:{prefix[11:13]}:{prefix[13:15]}Z"
        )
    return ""


def timestamp_for_filename(value: str) -> str:
    normalized = value.replace("+00:00", "Z")
    try:
        dt = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError:
        dt = datetime.now(timezone.utc)
    return dt.strftime("%Y%m%dT%H%M%SZ")


def timestamp_less_than(left: str, right: str) -> bool:
    left_dt = parse_timestamp(left)
    right_dt = parse_timestamp(right)
    if left_dt is None or right_dt is None:
        return False
    return left_dt < right_dt


def parse_timestamp(value: str) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Active ION root")
    parser.add_argument("--write", action="store_true", help="Write readiness artifacts")
    parser.add_argument("--no-receipt", action="store_true", help="Skip operator action receipt")
    parser.add_argument("--generated-at", default=None)
    args = parser.parse_args(argv)

    if args.write:
        result = write_self_evolution_readiness(
            args.root,
            generated_at=args.generated_at,
            write_receipt=not args.no_receipt,
        )
    else:
        result = build_self_evolution_readiness(args.root, generated_at=args.generated_at)
    print(stable_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
