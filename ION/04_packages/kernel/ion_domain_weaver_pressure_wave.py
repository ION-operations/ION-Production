"""Domain Weaver pressure-wave planning over scarce native Codex slots.

This module gives Domain Weaver a durable fanout layer above the native
subagent pool. It plans more lanes than the foreground Codex carrier can hold,
and can seed worker-local spawn request rows for later dispatcher intake. It
does not start workers, process the general queue, call Codex, or move accepted
state.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

from kernel.ion_codex_queue_runner import (
    EXECUTABLE_CODEX_WORK_LANES,
    normalize_codex_work_lane_id,
)
from kernel.ion_domain_weaver_spawn_request_dispatcher import (
    build_spawn_dispatch_start_plan,
)
from kernel.ion_domain_weaver_worker_context_lanes import (
    resolve_worker_context_lane,
    write_spawn_request,
)
from kernel.ion_domain_weaver_worker_start_readiness import (
    build_domain_weaver_worker_start_backlog_hygiene,
)


PRESSURE_WAVE_PLAN_SCHEMA_ID = "ion.domain_weaver.pressure_wave_plan.v0_1_candidate"
PRESSURE_WAVE_SPAWN_REQUEST_SEED_SCHEMA_ID = (
    "ion.domain_weaver.pressure_wave_spawn_request_seed.v0_1"
)
PRESSURE_WAVE_CONFIRMATION = "ION_BOUNDED_WRITE_CONFIRMED"
DEFAULT_CONTEXT_PACKAGE = "ION/05_context/current/domain_weaver/.ion/ACTIVE_CONTEXT_PACKAGE.md"
DEFAULT_PARENT_WORKER_ID = "pressure_scheduler"
DEFAULT_NATIVE_SLOT_CAP = 6
DEFAULT_READ_ONLY_MANAGER_TARGET = 12
DEFAULT_CANDIDATE_PACKET_CAP = 12
DEFAULT_ACTIVE_PATCH_CAP = 3
DEFAULT_EXACT_QUEUE_START_CAP = 2

DEFAULT_PRESSURE_LANES: tuple[dict[str, Any], ...] = (
    {
        "lane_id": "swarm_concurrency_governor",
        "title": "Swarm Concurrency Governor",
        "domain_id": "domain.domain_weaver_fanout_control",
        "role_id": "role.domain_weaver_concurrency_governor",
        "role_tier": "manager",
        "queue_lane_id": "architecture_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-SWARM-CONCURRENCY-GOVERNOR",
        "objective": "Define pressure-wave caps, stop gates, and fan-in requirements.",
    },
    {
        "lane_id": "queue_hygiene_exact_path",
        "title": "Queue Hygiene Exact-Path Quarantine",
        "domain_id": "domain.codex_queue_hygiene",
        "role_id": "role.queue_hygiene_steward",
        "role_tier": "manager",
        "queue_lane_id": "audit_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-QUEUE-HYGIENE-EXACT-PATH",
        "objective": "Separate exact-ready spawn-dispatch starts from dirty global queue rows.",
    },
    {
        "lane_id": "dispatcher_guardrail_verifier",
        "title": "Dispatcher Guardrail Verifier",
        "domain_id": "domain.spawn_dispatch_guardrails",
        "role_id": "role.dispatcher_guardrail_verifier",
        "role_tier": "specialist",
        "queue_lane_id": "audit_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-DISPATCHER-GUARDRAIL-VERIFY",
        "objective": "Verify blocked connector receipts cannot count as enqueued.",
    },
    {
        "lane_id": "original_autoreaction_proof",
        "title": "Original Autoreaction Proof",
        "domain_id": "domain.agent_autoreaction_proof",
        "role_id": "role.autoreaction_proof_lead",
        "role_tier": "manager",
        "queue_lane_id": "comms_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-ORIGINAL-AUTOREACTION-PROOF",
        "objective": "Map the missing non-alternate original worker reaction proof chain.",
    },
    {
        "lane_id": "semantic_alias_apply_decision",
        "title": "Semantic Alias Apply Decision",
        "domain_id": "domain.semantic_alias_canonicalization",
        "role_id": "role.semantic_alias_gatekeeper",
        "role_tier": "manager",
        "queue_lane_id": "approval_governance_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-SEMANTIC-ALIAS-APPLY-DECISION",
        "objective": "Prepare supervised alias apply decision logic and stop conditions.",
    },
    {
        "lane_id": "projection_refresh_after_alias",
        "title": "Projection Refresh After Alias",
        "domain_id": "domain.projection_refresh",
        "role_id": "role.projection_refresh_lead",
        "role_tier": "manager",
        "queue_lane_id": "architecture_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-PROJECTION-REFRESH-AFTER-ALIAS",
        "objective": "Design accepted projection refresh sequence after alias currentness changes.",
    },
    {
        "lane_id": "materialization_guard",
        "title": "Materialization Guard",
        "domain_id": "domain.materialization_readiness",
        "role_id": "role.materialization_gate_auditor",
        "role_tier": "manager",
        "queue_lane_id": "approval_governance_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-MATERIALIZATION-GUARD",
        "objective": "Design future materialize-all guard requirements without materializing.",
    },
    {
        "lane_id": "context_mount_quality",
        "title": "Context Mount Quality",
        "domain_id": "domain.context_mount_quality",
        "role_id": "role.context_mount_quality_lead",
        "role_tier": "specialist",
        "queue_lane_id": "context_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-CONTEXT-MOUNT-QUALITY",
        "objective": "Audit generated mounts, folder-local capsules, and per-agent uniqueness.",
    },
    {
        "lane_id": "ui_ide_swarm_status_adapter",
        "title": "UI IDE Swarm Status Adapter",
        "domain_id": "domain.operator_workbench_truth_surface",
        "role_id": "role.ui_swarm_status_adapter",
        "role_tier": "specialist",
        "queue_lane_id": "browser_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-UI-IDE-SWARM-STATUS-ADAPTER",
        "objective": "Design UI adapter contract for candidate, accepted, queue, and context truth.",
    },
    {
        "lane_id": "monolith_decomposition",
        "title": "Monolith Decomposition",
        "domain_id": "domain.monolith_decomposition",
        "role_id": "role.monolith_decomposition_lead",
        "role_tier": "specialist",
        "queue_lane_id": "implementation_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-MONOLITH-DECOMPOSITION",
        "objective": "Rank next disjoint Domain Weaver decomposition lanes and tests.",
    },
    {
        "lane_id": "agent_comms_protocol_package",
        "title": "Agent Comms Protocol Package",
        "domain_id": "domain.agent_communication_systems",
        "role_id": "role.agent_comms_protocol_lead",
        "role_tier": "manager",
        "queue_lane_id": "comms_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-AGENT-COMMS-PROTOCOL-PACKAGE",
        "objective": "Design manager/subworker comms packages without false autonomy claims.",
    },
    {
        "lane_id": "nemesis_pressure_auditor",
        "title": "Nemesis Pressure Auditor",
        "domain_id": "domain.nemesis_pressure_audit",
        "role_id": "role.nemesis_pressure_auditor",
        "role_tier": "nemesis",
        "queue_lane_id": "audit_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-NEMESIS-PRESSURE-AUDIT",
        "objective": "Attack false autonomy, queue storms, stale context, and fake proof.",
    },
)


def build_pressure_wave_plan(
    active_root: str | Path,
    *,
    lanes: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None = None,
    native_slot_cap: int = DEFAULT_NATIVE_SLOT_CAP,
    active_native_agent_count: int = 0,
    exact_queue_start_cap: int = DEFAULT_EXACT_QUEUE_START_CAP,
    candidate_packet_cap: int = DEFAULT_CANDIDATE_PACKET_CAP,
    active_patch_cap: int = DEFAULT_ACTIVE_PATCH_CAP,
    request_paths: list[str] | tuple[str, ...] | None = None,
    max_age_seconds: int = 48 * 60 * 60,
) -> dict[str, Any]:
    """Plan a wide pressure wave without spawning or starting workers."""

    root = _require_active_root(active_root)
    normalized_lanes = _normalize_lanes(lanes)
    native_cap = max(0, int(native_slot_cap))
    active_native_count = max(0, int(active_native_agent_count))
    available_native_slots = max(0, native_cap - active_native_count)
    exact_start_cap = max(0, int(exact_queue_start_cap))
    candidate_cap = max(0, int(candidate_packet_cap))
    patch_cap = max(0, int(active_patch_cap))

    native_batches = _batch_lanes(normalized_lanes, native_cap or 1)
    foreground_native_batch = normalized_lanes[:available_native_slots]
    overflow_lanes = normalized_lanes[available_native_slots:]
    durable_templates = [_spawn_request_template(row) for row in overflow_lanes]

    start_plan = build_spawn_dispatch_start_plan(
        root,
        request_paths=list(request_paths or []) or None,
        max_lanes=exact_start_cap,
        max_age_seconds=max_age_seconds,
    )
    backlog_hygiene = build_domain_weaver_worker_start_backlog_hygiene(
        root,
        max_age_seconds=max_age_seconds,
        example_limit=6,
    )

    blockers = _plan_blockers(
        normalized_lanes,
        native_cap=native_cap,
        exact_queue_start_cap=exact_start_cap,
        candidate_packet_cap=candidate_cap,
    )
    return {
        "schema_id": PRESSURE_WAVE_PLAN_SCHEMA_ID,
        "status": "pressure_wave_plan_built",
        "created_at": _utc_now(),
        "active_root": str(root),
        "lane_count": len(normalized_lanes),
        "caps": {
            "native_slot_cap": native_cap,
            "active_native_agent_count": active_native_count,
            "available_native_slots": available_native_slots,
            "read_only_manager_target": DEFAULT_READ_ONLY_MANAGER_TARGET,
            "candidate_packet_cap": candidate_cap,
            "active_patch_cap": patch_cap,
            "exact_queue_start_cap": exact_start_cap,
            "recursive_child_spawn_cap": 0,
            "general_queue_processing_allowed": False,
        },
        "lane_counts": {
            "foreground_native_batch_count": len(foreground_native_batch),
            "overflow_durable_spawn_row_count": len(overflow_lanes),
            "native_batch_count": len(native_batches),
        },
        "lanes": normalized_lanes,
        "foreground_native_batch": foreground_native_batch,
        "native_batches": native_batches,
        "durable_spawn_request_templates": durable_templates,
        "exact_queue_start_plan": _compact_start_plan(start_plan),
        "queue_hygiene": _compact_backlog_hygiene(backlog_hygiene),
        "blockers": blockers,
        "hard_stop_conditions": _hard_stop_conditions(),
        "pressure_test_sequence": [
            "spawn_native_batch_until_native_slot_cap_then_fan_in_or_close_completed_slots",
            "seed_overflow_worker_local_spawn_request_rows_only_with_gated_route",
            "dispatch_spawn_rows_to_queued_not_started_requests_only_after validation",
            "start_exact_request_paths_only_under codex_queue.process_once gate",
            "fan_in_worker_returns_before_widening_or_claiming readiness",
        ],
        "authority": _authority_block(),
        "actual_spawn_performed": False,
        "direct_nested_spawn": False,
        "recursive_child_spawn_allowed": False,
        "raw_external_codex_exec": False,
        "codex_queue_run_started": False,
        "worker_start_allowed": False,
        "accepted_state_claimed": False,
        "production_or_live_authority": False,
        "secrets_authority": False,
        "materialization_ready_claimed": False,
        "verdict": "PRESSURE_WAVE_PLAN_READY_CANDIDATE_ONLY",
    }


def seed_pressure_wave_spawn_requests(
    active_root: str | Path,
    *,
    lanes: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None = None,
    parent_worker_id: str = DEFAULT_PARENT_WORKER_ID,
    execute_write: bool = False,
    confirmation: str | None = None,
    idempotency_key: str | None = None,
    agent_id: str | None = None,
    write_intent_lease_id: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Seed durable worker-local spawn requests for later dispatcher intake."""

    root = _require_active_root(active_root)
    normalized_lanes = _normalize_lanes(lanes)
    if limit is not None:
        normalized_lanes = normalized_lanes[: max(0, int(limit))]
    templates = [_spawn_request_template(row) for row in normalized_lanes]
    gate = _write_gate(
        execute_write=execute_write,
        confirmation=confirmation,
        idempotency_key=idempotency_key,
        agent_id=agent_id,
        write_intent_lease_id=write_intent_lease_id,
    )
    if not execute_write or not gate["ok"]:
        return {
            "schema_id": PRESSURE_WAVE_SPAWN_REQUEST_SEED_SCHEMA_ID,
            "status": "pressure_wave_spawn_request_seed_preview"
            if not execute_write
            else "pressure_wave_spawn_request_seed_blocked",
            "created_at": _utc_now(),
            "active_root": str(root),
            "execute_write": bool(execute_write),
            "write_gate": gate,
            "spawn_request_count": 0,
            "spawn_request_templates": templates,
            "spawn_request_paths": [],
            "idempotent_replay_paths": [],
            "authority": _authority_block(),
            "actual_spawn_performed": False,
            "codex_queue_run_started": False,
            "worker_start_allowed": False,
            "accepted_state_claimed": False,
        }

    seeded: list[dict[str, Any]] = []
    replay_paths: list[str] = []
    lane = resolve_worker_context_lane(root, parent_worker_id, create=True)
    safe_key = _safe_fragment(str(idempotency_key))
    for row in normalized_lanes:
        row_id = _safe_fragment(f"{safe_key}-{row['lane_id']}")
        target = lane.spawn_requests_path / f"{row_id}.spawn_request.json"
        if target.is_file():
            replay_paths.append(_relative_posix(root, target))
            seeded.append(_read_json(target) | {"path": _relative_posix(root, target)})
            continue
        seeded.append(
            write_spawn_request(
                root,
                parent_worker_id,
                requested_domain=row["domain_id"],
                requested_packet=row["packet_id"],
                requested_callsign=row["title"],
                requested_true_name=row["title"],
                requested_role_id=row["role_id"],
                requested_role_tier=row["role_tier"],
                work_class="domain_weaver_spawn_dispatch",
                lane_id=row["queue_lane_id"],
                domain_context_package=DEFAULT_CONTEXT_PACKAGE,
                required_context_reads=row["required_context_reads"],
                planned_writes=row["planned_writes"] or None,
                allowed_scope=[
                    "read active-root source",
                    "read Domain Weaver context artifacts",
                    "write worker-local candidate artifact only",
                    "return carrier-intake proof only",
                ],
                forbidden_actions=[
                    "mutate active source",
                    "process general queue",
                    "start queue worker",
                ],
                evidence_requirements=[
                    "active-root proof",
                    "folder-local Domain Weaver context capsule",
                    "worker-local fan-in receipt",
                    "non-claim authority block",
                ],
                row_id=row_id,
            )
        )

    return {
        "schema_id": PRESSURE_WAVE_SPAWN_REQUEST_SEED_SCHEMA_ID,
        "status": "pressure_wave_spawn_requests_seeded",
        "created_at": _utc_now(),
        "active_root": str(root),
        "execute_write": True,
        "write_gate": gate,
        "parent_worker_id": resolve_worker_context_lane(root, parent_worker_id).worker_id,
        "spawn_request_count": len(seeded),
        "spawn_request_paths": [row["path"] for row in seeded],
        "idempotent_replay_paths": replay_paths,
        "spawn_requests": seeded,
        "authority": _authority_block(),
        "actual_spawn_performed": False,
        "direct_nested_spawn": False,
        "raw_external_codex_exec": False,
        "codex_queue_run_started": False,
        "worker_start_allowed": False,
        "accepted_state_claimed": False,
        "production_or_live_authority": False,
        "secrets_authority": False,
        "materialization_ready_claimed": False,
        "next_action": "dispatch_spawn_rows_only_after_lead_fanin_and_route_gate",
    }


def _normalize_lanes(
    lanes: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None,
) -> list[dict[str, Any]]:
    source = list(lanes or DEFAULT_PRESSURE_LANES)
    normalized: list[dict[str, Any]] = []
    for index, lane in enumerate(source, start=1):
        title = _clean_text(lane.get("title")) or f"Pressure Lane {index}"
        lane_id = _safe_fragment(lane.get("lane_id") or title)
        domain_id = _safe_token(
            lane.get("domain_id") or "domain.current_phase_orchestration_management",
            "domain_id",
        )
        role_id = _safe_token(lane.get("role_id") or "role.domain_weaver_specialist", "role_id")
        role_tier = _safe_token(lane.get("role_tier") or "specialist", "role_tier")
        packet_id = _safe_token(
            lane.get("packet_id") or f"PCKT-DOMAIN-WEAVER-PRESSURE-LANE-{index:02d}",
            "packet_id",
        )
        queue_lane_id = normalize_codex_work_lane_id(lane.get("queue_lane_id"))
        blockers: list[str] = []
        if not queue_lane_id or queue_lane_id not in EXECUTABLE_CODEX_WORK_LANES:
            blockers.append("queue_lane_id_not_executable")
            queue_lane_id = "audit_lane"
        required_context_reads = _context_reads(lane)
        normalized.append(
            {
                "lane_index": index,
                "lane_id": lane_id,
                "title": title,
                "objective": _clean_text(lane.get("objective")) or title,
                "domain_id": domain_id,
                "role_id": role_id,
                "role_tier": role_tier,
                "packet_id": packet_id,
                "queue_lane_id": queue_lane_id,
                "required_context_reads": required_context_reads,
                "planned_writes": _safe_string_list(lane.get("planned_writes")),
                "worker_return_is_carrier_intake_only": True,
                "actual_spawn_performed": False,
                "codex_queue_run_started": False,
                "blockers": blockers,
            }
        )
    return normalized


def _context_reads(lane: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = [
        {"kind": "file", "path": "ION/05_context/current/domain_weaver/AGENTS.md", "required": True},
        {"kind": "file", "path": "ION/05_context/current/domain_weaver/.ion/ION_CONTEXT_CAPSULE.yaml", "required": True},
        {"kind": "file", "path": DEFAULT_CONTEXT_PACKAGE, "required": True},
        {"kind": "file", "path": "ION/05_context/current/domain_weaver/acceleration/DW_SWARM_001_MANAGER_FANIN.latest.md", "required": False},
    ]
    for item in lane.get("required_context_reads") or []:
        if isinstance(item, Mapping):
            path = _clean_text(item.get("path"))
            if path:
                rows.append(
                    {
                        "kind": _clean_text(item.get("kind")) or "file",
                        "path": path,
                        "required": bool(item.get("required", True)),
                    }
                )
        elif _clean_text(item):
            rows.append({"kind": "file", "path": _clean_text(item), "required": True})
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        path = str(row["path"])
        if path not in seen:
            deduped.append(row)
            seen.add(path)
    return deduped[:64]


def _spawn_request_template(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "parent_worker_id": DEFAULT_PARENT_WORKER_ID,
        "requested_domain": row["domain_id"],
        "requested_packet": row["packet_id"],
        "requested_role_id": row["role_id"],
        "requested_role_tier": row["role_tier"],
        "requested_callsign": row["title"],
        "lane_id": row["queue_lane_id"],
        "domain_context_package": DEFAULT_CONTEXT_PACKAGE,
        "required_context_reads": row["required_context_reads"],
        "planned_writes": row["planned_writes"],
        "allowed_scope": [
            "read active-root source",
            "write worker-local candidate artifact only",
            "return carrier-intake proof only",
        ],
        "forbidden_actions": [
            "accepted_state_claim",
            "production_or_live_execution",
            "secrets_access",
            "registry_or_materialization_movement",
            "direct_codex_solo_write",
            "raw_external_codex_exec",
            "direct_nested_subagent_spawn",
        ],
        "evidence_requirements": [
            "active-root proof",
            "folder-local Domain Weaver context capsule",
            "worker-local fan-in receipt",
            "non-claim authority block",
        ],
        "actual_spawn_performed": False,
        "codex_queue_run_started": False,
    }


def _batch_lanes(lanes: list[dict[str, Any]], batch_size: int) -> list[dict[str, Any]]:
    size = max(1, int(batch_size))
    batches: list[dict[str, Any]] = []
    for index in range(0, len(lanes), size):
        batch = lanes[index : index + size]
        batches.append(
            {
                "batch_index": len(batches) + 1,
                "batch_size": len(batch),
                "lane_ids": [row["lane_id"] for row in batch],
                "native_slot_cap_respected": len(batch) <= size,
                "fan_in_required_before_next_batch": True,
            }
        )
    return batches


def _compact_start_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": plan.get("schema_id"),
        "queueable_spawn_dispatch_request_count": plan.get("queueable_spawn_dispatch_request_count"),
        "planned_start_count": plan.get("planned_start_count"),
        "blocked_start_count": plan.get("blocked_start_count"),
        "candidate_exact_request_paths": list(plan.get("candidate_exact_request_paths") or []),
        "blocked_request_paths": list(plan.get("blocked_request_paths") or []),
        "worker_start_readiness_ok": bool(plan.get("worker_start_readiness_ok")),
        "global_worker_start_readiness_ok": bool(plan.get("global_worker_start_readiness_ok")),
        "worker_start_readiness_blockers": list(plan.get("worker_start_readiness_blockers") or []),
        "global_worker_start_readiness_blockers": list(plan.get("global_worker_start_readiness_blockers") or []),
        "codex_queue_run_started": False,
        "general_queue_processing_allowed": False,
    }


def _compact_backlog_hygiene(hygiene: Mapping[str, Any]) -> dict[str, Any]:
    summary = hygiene.get("summary") if isinstance(hygiene.get("summary"), Mapping) else {}
    groups = hygiene.get("groups") if isinstance(hygiene.get("groups"), Mapping) else {}
    return {
        "schema_id": hygiene.get("schema_id"),
        "hygiene_ok": bool(hygiene.get("hygiene_ok")),
        "blockers": list(hygiene.get("blockers") or []),
        "summary": dict(summary),
        "group_counts": {
            str(name): len(value) if isinstance(value, list) else 0
            for name, value in groups.items()
        },
        "general_queue_processing_allowed": False,
        "codex_queue_run_started": False,
    }


def _plan_blockers(
    lanes: list[Mapping[str, Any]],
    *,
    native_cap: int,
    exact_queue_start_cap: int,
    candidate_packet_cap: int,
) -> list[str]:
    blockers: list[str] = []
    if native_cap <= 0:
        blockers.append("native_slot_cap_zero")
    if exact_queue_start_cap > 2:
        blockers.append("exact_queue_start_cap_above_dirty_queue_default")
    if len(lanes) > candidate_packet_cap:
        blockers.append("candidate_lane_count_above_candidate_packet_cap")
    for row in lanes:
        for blocker in row.get("blockers") or []:
            blockers.append(f"{row.get('lane_id')}:{blocker}")
    return sorted(set(blockers))


def _write_gate(
    *,
    execute_write: bool,
    confirmation: str | None,
    idempotency_key: str | None,
    agent_id: str | None,
    write_intent_lease_id: str | None,
) -> dict[str, Any]:
    blockers: list[str] = []
    if execute_write:
        if confirmation != PRESSURE_WAVE_CONFIRMATION:
            blockers.append("confirmation_required")
        if not _clean_text(idempotency_key):
            blockers.append("idempotency_key_required")
        if not _clean_text(agent_id):
            blockers.append("agent_id_required")
        if not _clean_text(write_intent_lease_id):
            blockers.append("write_intent_lease_id_required")
    return {
        "ok": not blockers,
        "execute_write": bool(execute_write),
        "confirmation_required": PRESSURE_WAVE_CONFIRMATION,
        "idempotency_key_present": bool(_clean_text(idempotency_key)),
        "agent_id_present": bool(_clean_text(agent_id)),
        "write_intent_lease_id_present": bool(_clean_text(write_intent_lease_id)),
        "blockers": blockers,
    }


def _hard_stop_conditions() -> list[str]:
    return [
        "any_lane_claims_accepted_state_or_materialization_ready",
        "any_lane_claims_recursive_child_spawn_without_current_probe_receipt",
        "any_dispatch_receipt_with_connector_ok_false_counts_as_enqueued",
        "general_queue_processing_requested_while_global_queue_hygiene_dirty",
        "exact_queue_start_requested_without_exact_request_path_and_gate",
        "worker_return_lacks_fanin_or_provenance_binding",
        "ui_labels_candidate_or_queued_work_as_accepted_or_running",
    ]


def _authority_block() -> dict[str, Any]:
    return {
        "candidate_only": True,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "materialization_authority": False,
        "worker_return_is_carrier_intake_only": True,
    }


def _require_active_root(active_root: str | Path) -> Path:
    root = Path(active_root).expanduser().resolve()
    if not (root / "pyproject.toml").is_file():
        raise ValueError("active_root_missing_pyproject")
    if not (root / "ION/REPO_AUTHORITY.md").is_file():
        raise ValueError("active_root_missing_repo_authority")
    return root


def _safe_token(value: Any, field_name: str) -> str:
    text = _clean_text(value)
    if not text:
        raise ValueError(f"{field_name}_required")
    if "/" in text or "\\" in text:
        raise ValueError(f"{field_name}_must_not_contain_path_separators")
    return text


def _safe_fragment(value: Any) -> str:
    text = _clean_text(value)
    if not text:
        text = hashlib.sha256(b"empty").hexdigest()[:12]
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", text).strip("._-").lower()
    if not slug:
        slug = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return slug[:96]


def _safe_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    raw = value if isinstance(value, (list, tuple)) else [value]
    rows: list[str] = []
    for item in raw:
        text = _clean_text(item)
        if text:
            rows.append(text)
    return rows


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return dict(payload) if isinstance(payload, Mapping) else {}


def _relative_posix(root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
