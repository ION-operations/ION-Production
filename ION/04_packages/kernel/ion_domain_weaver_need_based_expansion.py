"""Need-based Domain Weaver domain/agent expansion planning.

This module turns current Domain Weaver evidence into worker-local spawn
request lanes. The lane count is a capacity ceiling, not the objective: current
blockers, uncovered domain-universe rows, route gaps, context/proof gaps, and
fan-in obligations choose the work.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

from kernel.ion_codex_queue_runner import (
    EXECUTABLE_CODEX_WORK_LANES,
    normalize_codex_work_lane_id,
)
from kernel.ion_codex_agent_mount import (
    build_codex_agent_mount_candidate,
    compile_codex_agent_mount_active_context,
    materialize_codex_agent_mount,
)
from kernel.ion_domain_weaver_pressure_wave import (
    PRESSURE_WAVE_CONFIRMATION,
    seed_pressure_wave_spawn_requests,
)


PLAN_SCHEMA_ID = "ion.domain_weaver.need_based_domain_agent_expansion_plan.v0_1_candidate"
SEED_SCHEMA_ID = "ion.domain_weaver.need_based_domain_agent_expansion_spawn_seed.v0_1"
WRITE_RESULT_SCHEMA_ID = "ion.domain_weaver.need_based_domain_agent_expansion_plan.write_result.v0_1"
CONTEXT_MATERIALIZATION_SCHEMA_ID = "ion.domain_weaver.need_based_expansion.context_materialization.v0_1"

DEFAULT_CONTEXT_ROOT = Path("ION/05_context/current/domain_weaver")
DEFAULT_OUTPUT_DIR = DEFAULT_CONTEXT_ROOT / "need_based_expansion"
DEFAULT_PARENT_WORKER_ID = "need_based_expansion_scheduler"
DEFAULT_CAPACITY_CEILING = 64
DEFAULT_CONTEXT_PACKAGE = DEFAULT_CONTEXT_ROOT / ".ion/ACTIVE_CONTEXT_PACKAGE.md"
CODEX_WORK_REQUESTS_DIR = Path("ION/05_context/current/chatgpt_connector/codex_work_requests")
CONTEXT_MATERIALIZATION_RECEIPTS_DIR = DEFAULT_OUTPUT_DIR / "context_materialization_receipts"
COMMUNICATION_DIRECTORY_PATH = Path("ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json")
DOMAIN_UNIVERSE_LATEST_GLOB = (
    DEFAULT_CONTEXT_ROOT
    / "domain_agent_expansion_engine/domain_universe_index/DOMAIN_UNIVERSE_INDEX_336_24*.candidate.json"
)
MISSION035_DOMAIN_UNIVERSE_PATH = (
    DEFAULT_CONTEXT_ROOT / "mission035_domain_agent_expansion_engine/domain_universe_index.candidate.json"
)
MISSION035_ROUTE_GATE_MATRIX_PATH = (
    DEFAULT_CONTEXT_ROOT / "mission035_domain_agent_expansion_engine/expansion_route_gate_matrix.candidate.json"
)
MISSION035_SPAWN_ROW_VALIDATION_MATRIX_PATH = (
    DEFAULT_CONTEXT_ROOT / "mission035_domain_agent_expansion_engine/spawn_row_validation_matrix.candidate.json"
)
MISSION035_PACKET_TEMPLATE_FAMILY_PATH = (
    DEFAULT_CONTEXT_ROOT / "mission035_domain_agent_expansion_engine/expansion_packet_template_family.candidate.md"
)
SWARM_READINESS_PATH = DEFAULT_CONTEXT_ROOT / "swarm_control_plane/DOMAIN_WEAVER_SWARM_READINESS.latest.json"
LARGER_FANOUT_READINESS_PATH = (
    DEFAULT_CONTEXT_ROOT / "larger_fanout/DOMAIN_WEAVER_LARGER_FANOUT_CONTROL_READINESS.latest.json"
)

AUTHORITY = {
    "candidate_only": True,
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "materialization_authority": False,
    "codex_queue_run_started": False,
    "actual_spawn_performed": False,
}
CONTEXT_MATERIALIZATION_AUTHORITY = {
    "candidate_only": True,
    "candidate_materialization_authority": True,
    "materialization_scope": "generated_codex_agent_mounts_and_exact_codex_work_request_identity_bindings_only",
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "codex_queue_run_started": False,
    "actual_spawn_performed": False,
    "worker_start_performed": False,
}
FORBIDDEN_ACTIONS = [
    "accepted_state_claim",
    "production_or_live_execution",
    "secrets_access",
    "registry_or_materialization_movement",
    "direct_codex_solo_write",
    "raw_external_codex_exec",
    "direct_nested_subagent_spawn",
]
CONTEXT_MATERIALIZATION_REQUIRED_TARGET_ROOTS = [
    "ION/05_context/current/codex_agent_mounts",
    "ION/05_context/current/chatgpt_connector/codex_work_requests",
    "ION/05_context/current/domain_weaver/need_based_expansion/context_materialization_receipts",
]
EVIDENCE_REQUIREMENTS = [
    "active-root proof",
    "folder-local Domain Weaver context capsule",
    "current need-source artifact path and sha256",
    "worker-local fan-in receipt",
    "non-claim authority block",
]


def build_need_based_domain_agent_expansion_plan(
    active_root: str | Path,
    *,
    max_lanes: int = DEFAULT_CAPACITY_CEILING,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a candidate plan whose lanes are selected by current need."""

    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    ceiling = max(0, int(max_lanes))
    universe_path = _select_domain_universe_path(root)
    universe = _read_json(universe_path) if universe_path else {}
    readiness = _read_json(root / SWARM_READINESS_PATH)
    route_matrix = _read_json(root / MISSION035_ROUTE_GATE_MATRIX_PATH)
    spawn_matrix = _read_json(root / MISSION035_SPAWN_ROW_VALIDATION_MATRIX_PATH)
    larger_fanout = _read_json(root / LARGER_FANOUT_READINESS_PATH)

    system_needs = _system_need_rows(
        universe,
        readiness,
        route_matrix,
        spawn_matrix,
    )
    domain_needs = _domain_need_rows(universe)
    all_needs = _dedupe_need_rows([*system_needs, *domain_needs])
    ranked_needs = sorted(
        all_needs,
        key=lambda row: (-int(row["score"]), int(row["ordinal"]), str(row["need_id"])),
    )
    selected_needs = ranked_needs[:ceiling] if ceiling else []
    selected_lanes = [_lane_from_need(row) for row in selected_needs]
    read_only_plan = {
        "schema_id": PLAN_SCHEMA_ID,
        "status": "need_based_domain_agent_expansion_plan_built",
        "generated_at": generated,
        "active_root": str(root),
        "root_proof": _root_proof(root),
        "authority": AUTHORITY,
        "selection_policy": {
            "fixed_agent_count_is_objective": False,
            "capacity_ceiling": ceiling,
            "capacity_ceiling_used_as": "upper_bound_only",
            "need_sources_choose_lanes": True,
            "selected_lane_count": len(selected_lanes),
            "unselected_need_count": max(0, len(ranked_needs) - len(selected_lanes)),
        },
        "source_artifacts": _source_artifacts(root, universe_path),
        "source_summaries": {
            "domain_universe": _domain_universe_summary(universe),
            "swarm_readiness": _swarm_readiness_summary(readiness),
            "route_gate_matrix": _route_gate_summary(route_matrix),
            "spawn_row_validation_matrix": _spawn_matrix_summary(spawn_matrix),
            "larger_fanout_readiness": _larger_fanout_summary(larger_fanout),
        },
        "need_count": len(ranked_needs),
        "system_need_count": len(system_needs),
        "domain_need_count": len(domain_needs),
        "selected_lane_count": len(selected_lanes),
        "selected_needs": selected_needs,
        "selected_lanes": selected_lanes,
        "ranked_need_preview": ranked_needs[: min(len(ranked_needs), 128)],
        "blocked_or_deferred": _blocked_or_deferred(larger_fanout, len(selected_lanes), ceiling),
        "next_action": (
            "seed_selected_need_lanes_as_worker_local_spawn_requests"
            if selected_lanes
            else "repair_need_sources_before_expansion"
        ),
        "non_claims": [
            "does not treat 32, 64, or any fixed count as the product",
            "does not create accepted domains",
            "does not mutate DOMAIN_WEAVER_PROJECTION.json",
            "does not create generated mounts",
            "does not enqueue Codex work requests",
            "does not start workers or process queues",
            "does not grant production, live execution, secrets, materialization, or accepted-state authority",
        ],
        "effects": {
            "plan_written": False,
            "spawn_request_rows_written": False,
            "codex_work_requests_written": False,
            "codex_queue_run_started": False,
            "accepted_state_touched": False,
            "domain_weaver_projection_modified": False,
        },
    }
    return read_only_plan


def write_need_based_domain_agent_expansion_plan(
    active_root: str | Path,
    *,
    max_lanes: int = DEFAULT_CAPACITY_CEILING,
    generated_at: str | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Write a candidate need-based expansion plan artifact."""

    root = _require_active_root(active_root)
    plan = build_need_based_domain_agent_expansion_plan(
        root,
        max_lanes=max_lanes,
        generated_at=generated_at,
    )
    stamp = _stamp(str(plan["generated_at"]))
    out_dir = _resolve_output_dir(root, output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"DOMAIN_WEAVER_NEED_BASED_EXPANSION_PLAN_{stamp}.candidate.json"
    md_path = out_dir / f"DOMAIN_WEAVER_NEED_BASED_EXPANSION_PLAN_{stamp}.candidate.md"
    latest_json_path = out_dir / "DOMAIN_WEAVER_NEED_BASED_EXPANSION_PLAN.latest.candidate.json"
    latest_md_path = out_dir / "DOMAIN_WEAVER_NEED_BASED_EXPANSION_PLAN.latest.candidate.md"
    plan["effects"] = {**dict(plan["effects"]), "plan_written": True}
    plan["artifact_paths"] = {
        "json": _rel(root, json_path),
        "markdown": _rel(root, md_path),
        "latest_json": _rel(root, latest_json_path),
        "latest_markdown": _rel(root, latest_md_path),
    }
    json_text = _stable_json(plan)
    md_text = render_need_based_domain_agent_expansion_plan(plan)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json_path.write_text(json_text, encoding="utf-8")
    md_path.write_text(md_text, encoding="utf-8")
    latest_md_path.write_text(md_text, encoding="utf-8")
    return {
        "schema_id": WRITE_RESULT_SCHEMA_ID,
        "status": "need_based_domain_agent_expansion_plan_written",
        "generated_at": plan["generated_at"],
        "active_root": str(root),
        "artifact_paths": dict(plan["artifact_paths"]),
        "selected_lane_count": plan["selected_lane_count"],
        "need_count": plan["need_count"],
        "json_sha256": _sha256_text(json_text),
        "markdown_sha256": _sha256_text(md_text),
        "authority": AUTHORITY,
        "effects": dict(plan["effects"]),
    }


def seed_need_based_expansion_spawn_requests(
    active_root: str | Path,
    *,
    max_lanes: int = DEFAULT_CAPACITY_CEILING,
    parent_worker_id: str = DEFAULT_PARENT_WORKER_ID,
    execute_write: bool = False,
    confirmation: str | None = None,
    idempotency_key: str | None = None,
    agent_id: str | None = None,
    write_intent_lease_id: str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Seed selected need lanes as worker-local spawn requests.

    This delegates row writing to the existing pressure-wave seeder so gate,
    row shape, idempotence, and non-claim semantics stay identical.
    """

    root = _require_active_root(active_root)
    plan = build_need_based_domain_agent_expansion_plan(
        root,
        max_lanes=max_lanes,
        generated_at=generated_at,
    )
    seed = seed_pressure_wave_spawn_requests(
        root,
        lanes=plan["selected_lanes"],
        parent_worker_id=parent_worker_id,
        execute_write=execute_write,
        confirmation=confirmation,
        idempotency_key=idempotency_key,
        agent_id=agent_id,
        write_intent_lease_id=write_intent_lease_id,
        limit=None,
    )
    return {
        "schema_id": SEED_SCHEMA_ID,
        "status": (
            "need_based_expansion_spawn_requests_seeded"
            if seed.get("status") == "pressure_wave_spawn_requests_seeded"
            else "need_based_expansion_spawn_request_seed_preview"
            if not execute_write
            else "need_based_expansion_spawn_request_seed_blocked"
        ),
        "created_at": _utc_now(),
        "active_root": str(root),
        "parent_worker_id": parent_worker_id,
        "max_lanes": max(0, int(max_lanes)),
        "need_count": plan["need_count"],
        "selected_lane_count": plan["selected_lane_count"],
        "selected_need_ids": [str(row.get("need_id")) for row in plan["selected_needs"]],
        "execute_write": bool(execute_write),
        "write_gate": seed.get("write_gate", {}),
        "spawn_request_count": int(seed.get("spawn_request_count") or 0),
        "spawn_request_paths": list(seed.get("spawn_request_paths") or []),
        "idempotent_replay_paths": list(seed.get("idempotent_replay_paths") or []),
        "seed_result": seed,
        "plan": plan,
        "authority": CONTEXT_MATERIALIZATION_AUTHORITY,
        "effects": {
            "spawn_request_rows_written": bool(seed.get("spawn_request_count") and execute_write),
            "codex_work_requests_written": False,
            "codex_queue_run_started": False,
            "accepted_state_touched": False,
            "domain_weaver_projection_modified": False,
        },
        "actual_spawn_performed": False,
        "codex_queue_run_started": False,
        "worker_start_allowed": False,
        "accepted_state_claimed": False,
        "production_or_live_authority": False,
        "secrets_authority": False,
    }


def materialize_need_based_expansion_worker_contexts(
    active_root: str | Path,
    *,
    request_paths: Sequence[str] | None = None,
    parent_worker_id: str = DEFAULT_PARENT_WORKER_ID,
    run_id: str | None = None,
    execute_write: bool = False,
    confirmation: str | None = None,
    idempotency_key: str | None = None,
    agent_id: str | None = None,
    write_intent_lease_id: str | None = None,
    limit: int | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Materialize generated worker mounts and bind exact queued requests.

    This is the missing bridge between a queued need-selected spawn dispatch and
    the worker-start readiness gate. It does not start workers, process queues,
    mutate projection, or claim accepted state.
    """

    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    rows = _need_based_queue_request_rows(
        root,
        request_paths=request_paths,
        parent_worker_id=parent_worker_id,
        run_id=run_id,
        limit=limit,
    )
    plans = [
        _context_materialization_plan_row(root, row)
        for row in rows
    ]
    target_paths = _context_materialization_target_paths(plans)
    gate = _context_materialization_write_gate(
        execute_write=execute_write,
        confirmation=confirmation,
        idempotency_key=idempotency_key,
        agent_id=agent_id,
        write_intent_lease_id=write_intent_lease_id,
        target_paths=target_paths,
    )
    if execute_write and not gate["ok"]:
        return _context_materialization_result(
            root,
            generated_at=generated,
            status="need_based_expansion_context_materialization_blocked",
            parent_worker_id=parent_worker_id,
            run_id=run_id,
            execute_write=execute_write,
            write_gate=gate,
            plans=plans,
            materialized_rows=[],
            receipt_paths=[],
            effects={
                "codex_agent_mounts_written": False,
                "codex_work_requests_patched": False,
                "receipt_written": False,
                "codex_queue_run_started": False,
                "workers_started": False,
                "accepted_state_touched": False,
                "domain_weaver_projection_modified": False,
            },
        )

    if not execute_write:
        return _context_materialization_result(
            root,
            generated_at=generated,
            status="need_based_expansion_context_materialization_preview",
            parent_worker_id=parent_worker_id,
            run_id=run_id,
            execute_write=execute_write,
            write_gate=gate,
            plans=plans,
            materialized_rows=[],
            receipt_paths=[],
            effects={
                "codex_agent_mounts_written": False,
                "codex_work_requests_patched": False,
                "receipt_written": False,
                "codex_queue_run_started": False,
                "workers_started": False,
                "accepted_state_touched": False,
                "domain_weaver_projection_modified": False,
            },
        )

    communication_directory = _read_json(root / COMMUNICATION_DIRECTORY_PATH)
    materialized_rows: list[dict[str, Any]] = []
    for plan in plans:
        row = _apply_context_materialization_plan(
            root,
            plan,
            generated_at=generated,
            idempotency_key=str(idempotency_key or ""),
            agent_id=str(agent_id or ""),
            write_intent_lease_id=str(write_intent_lease_id or ""),
            communication_directory=communication_directory,
        )
        materialized_rows.append(row)
    successful_statuses = {
        "context_materialized_and_request_bound",
        "context_materialization_idempotent_replay",
    }
    all_rows_succeeded = bool(materialized_rows) and all(
        str(row.get("status") or "") in successful_statuses
        for row in materialized_rows
    )
    receipt_paths = _write_context_materialization_receipts(
        root,
        generated_at=generated,
        idempotency_key=str(idempotency_key or ""),
        result_rows=materialized_rows,
        parent_worker_id=parent_worker_id,
        run_id=run_id,
        write_gate=gate,
    )
    return _context_materialization_result(
        root,
        generated_at=generated,
        status=(
            "need_based_expansion_contexts_materialized"
            if all_rows_succeeded
            else "need_based_expansion_context_materialization_incomplete"
        ),
        parent_worker_id=parent_worker_id,
        run_id=run_id,
        execute_write=execute_write,
        write_gate=gate,
        plans=plans,
        materialized_rows=materialized_rows,
        receipt_paths=receipt_paths,
        effects={
            "codex_agent_mounts_written": any(
                row.get("mount_materialized") for row in materialized_rows
            ),
            "codex_work_requests_patched": any(row.get("request_patched") for row in materialized_rows),
            "receipt_written": bool(receipt_paths),
            "codex_queue_run_started": False,
            "workers_started": False,
            "accepted_state_touched": False,
            "domain_weaver_projection_modified": False,
        },
    )


def render_need_based_domain_agent_expansion_plan(plan: Mapping[str, Any]) -> str:
    policy = _mapping(plan.get("selection_policy"))
    source = _mapping(plan.get("source_summaries"))
    lines = [
        "# Domain Weaver Need-Based Expansion Plan",
        "",
        f"Generated: `{plan.get('generated_at')}`",
        "",
        "Authority: candidate-only. This does not mutate accepted state, projection, generated mounts, queue state, or worker runtime.",
        "",
        "## Selection",
        "",
        f"- fixed agent count objective: `{str(bool(policy.get('fixed_agent_count_is_objective'))).lower()}`",
        f"- capacity ceiling: `{policy.get('capacity_ceiling')}`",
        f"- need count: `{plan.get('need_count')}`",
        f"- selected lanes: `{plan.get('selected_lane_count')}`",
        f"- unselected needs: `{policy.get('unselected_need_count')}`",
        "",
        "## Source Summaries",
        "",
        f"- domain universe domains: `{_mapping(source.get('domain_universe')).get('domain_count')}`",
        f"- domain universe biomes: `{_mapping(source.get('domain_universe')).get('biome_count')}`",
        f"- swarm readiness verdict: `{_mapping(source.get('swarm_readiness')).get('verdict')}`",
        f"- readiness blocker count: `{_mapping(source.get('swarm_readiness')).get('blocker_count')}`",
        f"- route gate status: `{_mapping(source.get('route_gate_matrix')).get('status')}`",
        f"- spawn validation status: `{_mapping(source.get('spawn_row_validation_matrix')).get('status')}`",
        "",
        "## Selected Lanes",
        "",
        "| Score | Need | Domain | Packet | Queue Lane |",
        "|---:|---|---|---|---|",
    ]
    for need in plan.get("selected_needs") if isinstance(plan.get("selected_needs"), list) else []:
        if not isinstance(need, Mapping):
            continue
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{need.get('score')}`",
                    f"`{need.get('need_id')}`",
                    f"`{need.get('domain_id')}`",
                    f"`{need.get('packet_id')}`",
                    f"`{need.get('queue_lane_id')}`",
                ]
            )
            + " |"
        )
    lines.extend(["", "## Non-Claims", ""])
    for claim in plan.get("non_claims") if isinstance(plan.get("non_claims"), list) else []:
        lines.append(f"- {claim}")
    return "\n".join(lines) + "\n"


def _system_need_rows(
    universe: Mapping[str, Any],
    readiness: Mapping[str, Any],
    route_matrix: Mapping[str, Any],
    spawn_matrix: Mapping[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    ordinal = 0

    def add(
        need_id: str,
        *,
        score: int,
        domain_id: str,
        role_id: str,
        packet_id: str,
        title: str,
        queue_lane_id: str,
        reason: str,
        evidence: Sequence[str],
    ) -> None:
        nonlocal ordinal
        ordinal += 1
        rows.append(
            _need_row(
                need_id,
                ordinal=ordinal,
                score=score,
                need_class="system",
                domain_id=domain_id,
                role_id=role_id,
                role_tier="manager",
                packet_id=packet_id,
                title=title,
                queue_lane_id=queue_lane_id,
                reason=reason,
                evidence=evidence,
            )
        )

    universe_blockers = {str(item) for item in universe.get("blockers") or [] if str(item).strip()}
    if "route_ownership_staffing_spawn_rows_and_proof_edges_not_attached_per_domain" in universe_blockers:
        add(
            "route_ownership_staffing_proof_edges",
            score=980,
            domain_id="domain.domain_agent_expansion_engine",
            role_id="role.domain_agent_expansion_router",
            packet_id="PCKT-DOMAIN-WEAVER-M035-ROUTE-OWNERSHIP-STAFFING-PROOF-EDGES-V0_1",
            title="Route Ownership Staffing Proof Edge Router",
            queue_lane_id="domain_agent_index_router_lane",
            reason="The 336-domain universe exists but route ownership, staffing rows, and proof edges are not attached per domain.",
            evidence=[_rel_source(MISSION035_DOMAIN_UNIVERSE_PATH)],
        )
    if "runtime_domain_universe_ingestor_route_missing" in universe_blockers:
        add(
            "runtime_domain_universe_ingestor_route",
            score=970,
            domain_id="domain.routes.domain_universe_ingestor",
            role_id="role.domain_universe_ingestor_route_steward",
            packet_id="PCKT-DOMAIN-WEAVER-M035-DOMAIN-UNIVERSE-INGESTOR-ROUTE-V0_1",
            title="Domain Universe Ingestor Route Steward",
            queue_lane_id="architecture_lane",
            reason="The valid 336-domain artifact needs a runtime ingestor route before it can drive future expansion waves.",
            evidence=[_rel_source(MISSION035_DOMAIN_UNIVERSE_PATH)],
        )
    if "seed_alias_bridge_review_required" in universe_blockers:
        add(
            "seed_alias_bridge_review",
            score=950,
            domain_id="domain.semantic_alias_canonicalization",
            role_id="role.seed_alias_bridge_reviewer",
            packet_id="PCKT-DOMAIN-WEAVER-M035-SEED-ALIAS-BRIDGE-REVIEW-V0_1",
            title="Seed Alias Bridge Reviewer",
            queue_lane_id="audit_lane",
            reason="Seed/intended-domain aliases need review before domain rows become stable route identity.",
            evidence=[_rel_source(MISSION035_DOMAIN_UNIVERSE_PATH)],
        )

    recommended = str(spawn_matrix.get("recommended_next_packet") or "").strip()
    if recommended:
        add(
            "spawn_row_start_blocker_repair",
            score=930,
            domain_id="domain.runtime.spawn_rows",
            role_id="role.spawn_row_start_blocker_repair",
            packet_id=recommended,
            title="Spawn Row Start Blocker Repair",
            queue_lane_id="maintenance_lane",
            reason="Wave0 spawn-row validation produced a concrete recommended next packet.",
            evidence=[_rel_source(MISSION035_SPAWN_ROW_VALIDATION_MATRIX_PATH)],
        )

    for blocker in readiness.get("blockers_ranked") or []:
        if not isinstance(blocker, Mapping):
            continue
        code = str(blocker.get("code") or "").strip()
        if not code:
            continue
        mapped = _readiness_blocker_lane(code)
        if not mapped:
            continue
        severity = str(blocker.get("severity") or "")
        add(
            mapped["need_id"],
            score=mapped["score"] + _severity_bonus(severity),
            domain_id=mapped["domain_id"],
            role_id=mapped["role_id"],
            packet_id=mapped["packet_id"],
            title=mapped["title"],
            queue_lane_id=mapped["queue_lane_id"],
            reason=str(blocker.get("detail") or mapped["reason"]),
            evidence=[str(item) for item in blocker.get("evidence") or [] if str(item).strip()],
        )

    summary = route_matrix.get("summary") if isinstance(route_matrix.get("summary"), Mapping) else {}
    route_gap_count = int(summary.get("domain_weaver_mutating_route_gap_count") or 0)
    if route_gap_count:
        add(
            "route_gate_gap_repair",
            score=900 + route_gap_count,
            domain_id="domain.routes.route_gate_matrix",
            role_id="role.route_gate_gap_repair",
            packet_id="PCKT-DOMAIN-WEAVER-M035-ROUTE-GATE-GAP-REPAIR-V0_1",
            title="Route Gate Gap Repair",
            queue_lane_id="audit_lane",
            reason="Route-gate matrix still reports Domain Weaver mutation-route gaps.",
            evidence=[_rel_source(MISSION035_ROUTE_GATE_MATRIX_PATH)],
        )
    return rows


def _domain_need_rows(universe: Mapping[str, Any]) -> list[dict[str, Any]]:
    domains = [dict(row) for row in universe.get("domains") or [] if isinstance(row, Mapping)]
    seeded_biomes: set[str] = set()
    rows: list[dict[str, Any]] = []
    for index, domain in enumerate(domains, start=1):
        domain_id = str(domain.get("domain_id") or "").strip()
        if not domain_id:
            continue
        biome_id = str(domain.get("primary_biome_id") or domain.get("primary_biome_slug") or domain.get("primary_biome_name") or "")
        score, reasons = _domain_score(domain, seeded_biomes)
        if biome_id:
            seeded_biomes.add(biome_id)
        slug = _domain_slug(domain_id)
        packet_id = f"PCKT-DOMAIN-WEAVER-DOMAIN-SEED-{_packet_fragment(slug)}-V0_1"
        rows.append(
            _need_row(
                f"domain_seed.{slug}",
                ordinal=10000 + index,
                score=score,
                need_class="domain_seed",
                domain_id=domain_id,
                role_id=f"role.{slug}_seed_steward",
                role_tier="specialist",
                packet_id=packet_id,
                title=f"Domain Seed {slug.replace('_', ' ').title()}",
                queue_lane_id=_queue_lane_for_domain(domain_id, domain),
                reason="; ".join(reasons),
                evidence=[_rel_source(MISSION035_DOMAIN_UNIVERSE_PATH)],
                biome_id=biome_id,
            )
        )
    return rows


def _domain_score(domain: Mapping[str, Any], seeded_biomes: set[str]) -> tuple[int, list[str]]:
    domain_id = str(domain.get("domain_id") or "")
    lowered = domain_id.lower()
    biome_id = str(domain.get("primary_biome_id") or domain.get("primary_biome_slug") or domain.get("primary_biome_name") or "")
    status = str(domain.get("implementation_state") or domain.get("status") or "").lower()
    score = 500
    reasons = ["intended-domain universe row needs staffing and proof edges"]
    if "not_proven" in status or "not_built" in status or "candidate" in status:
        score += 60
        reasons.append("implementation not proven built")
    if biome_id and biome_id not in seeded_biomes:
        score += 80
        reasons.append("first selected row for biome coverage")
    if ".core_law." in lowered:
        score += 160
        reasons.append("core law governs authority and state semantics")
    if any(token in lowered for token in ("authority", "accepted_state", "candidate_state", "operator_approval")):
        score += 140
        reasons.append("authority or state-transition semantics")
    if any(token in lowered for token in ("route", "spawn", "queue", "worker", "runtime", "carrier")):
        score += 120
        reasons.append("runtime route or worker fabric")
    if any(token in lowered for token in ("proof", "receipt", "fanin", "settlement", "nemesis")):
        score += 110
        reasons.append("proof or fan-in custody")
    if any(token in lowered for token in ("context", "mount", "memory", "capsule")):
        score += 100
        reasons.append("context or mount quality")
    if any(token in lowered for token in ("comms", "communication", "signal")):
        score += 90
        reasons.append("communications fabric")
    return score, reasons


def _readiness_blocker_lane(code: str) -> dict[str, Any] | None:
    mapping: dict[str, dict[str, Any]] = {
        "ACCEPTED_STATE_WRITE_GATE_NOT_GRANTED_FOR_PROJECTION": {
            "need_id": "accepted_state_projection_gate_review",
            "score": 900,
            "domain_id": "domain.core_law.accepted_state_protocol",
            "role_id": "role.accepted_state_projection_gate_reviewer",
            "packet_id": "PCKT-DOMAIN-WEAVER-ACCEPTED-PROJECTION-GATE-REVIEW-V0_1",
            "title": "Accepted Projection Gate Reviewer",
            "queue_lane_id": "audit_lane",
            "reason": "Accepted-state projection gate needs candidate review without apply authority.",
        },
        "MATERIALIZATION_READY_FALSE": {
            "need_id": "materialization_readiness_remaining_gates",
            "score": 880,
            "domain_id": "domain.materialization_readiness",
            "role_id": "role.materialization_gate_auditor",
            "packet_id": "PCKT-DOMAIN-WEAVER-MATERIALIZATION-READINESS-REMAINING-GATES-V0_1",
            "title": "Materialization Remaining Gates Auditor",
            "queue_lane_id": "approval_governance_lane",
            "reason": "Materialization is not ready and remaining gates must be separated from expansion planning.",
        },
        "SEMANTIC_ALIAS_ACCEPTED_STATE_APPLY_GATE_NOT_GRANTED": {
            "need_id": "semantic_alias_apply_gate_review",
            "score": 860,
            "domain_id": "domain.semantic_alias_canonicalization",
            "role_id": "role.semantic_alias_apply_gate_reviewer",
            "packet_id": "PCKT-DOMAIN-WEAVER-SEMANTIC-ALIAS-APPLY-GATE-REVIEW-V0_1",
            "title": "Semantic Alias Apply Gate Reviewer",
            "queue_lane_id": "audit_lane",
            "reason": "Semantic alias evidence needs currentness review without accepted projection mutation.",
        },
        "AUTOMATIC_ORIGINAL_AGENT_REACTION_NOT_PROVEN": {
            "need_id": "original_autoreaction_proof",
            "score": 840,
            "domain_id": "domain.agent_communication_systems",
            "role_id": "role.autoreaction_proof_lead",
            "packet_id": "PCKT-DOMAIN-WEAVER-COMMS-AUTOREACTION-PROOF-V0_2-ORIGINAL-WORKER-BOUND",
            "title": "Original Autoreaction Proof Lead",
            "queue_lane_id": "comms_lane",
            "reason": "Original automatic reaction proof remains separate from alternate-worker recovery evidence.",
        },
        "GLOBAL_QUEUE_BACKLOG_CONTEXT_IDENTITY_HYGIENE_NOT_CLEAN": {
            "need_id": "global_queue_context_identity_hygiene",
            "score": 835,
            "domain_id": "domain.codex_queue_hygiene",
            "role_id": "role.queue_hygiene_steward",
            "packet_id": "PCKT-DOMAIN-WEAVER-GLOBAL-QUEUE-BACKLOG-CONTEXT-IDENTITY-HYGIENE-V0_1",
            "title": "Global Queue Context Identity Hygiene Steward",
            "queue_lane_id": "audit_lane",
            "reason": "Global queue hygiene must not block exact path work indefinitely.",
        },
        "SESSIONSTART_CANDIDATE_RECEIPT_LANE_MISSING": {
            "need_id": "sessionstart_candidate_receipt_lane",
            "score": 780,
            "domain_id": "domain.receipt_proof_graph",
            "role_id": "role.sessionstart_receipt_lane_steward",
            "packet_id": "PCKT-SESSIONSTART-CANDIDATE-RECEIPT-LANE-V0_1",
            "title": "SessionStart Candidate Receipt Lane Steward",
            "queue_lane_id": "audit_lane",
            "reason": "SessionStart needs a candidate receipt lane for durable proof custody.",
        },
        "BOUNDED_REISSUE_PACKET_EXECUTION_REQUIRED": {
            "need_id": "bounded_reissue_return_fanin",
            "score": 830,
            "domain_id": "domain.swarm_fanin_settlement",
            "role_id": "role.parent_relay_reissue_fanin_steward",
            "packet_id": "PCKT-DOMAIN-WEAVER-PARENT-RELAY-REISSUE-RETURN-FANIN-V0_1",
            "title": "Parent Relay Reissue Fan-In Steward",
            "queue_lane_id": "settlement_lane",
            "reason": "Fresh reissue worker returns need fan-in before lifecycle closeout.",
        },
    }
    return mapping.get(code)


def _need_row(
    need_id: str,
    *,
    ordinal: int,
    score: int,
    need_class: str,
    domain_id: str,
    role_id: str,
    role_tier: str,
    packet_id: str,
    title: str,
    queue_lane_id: str,
    reason: str,
    evidence: Sequence[str],
    biome_id: str = "",
) -> dict[str, Any]:
    lane_id = _safe_fragment(need_id)
    executable_lane = normalize_codex_work_lane_id(queue_lane_id) or "audit_lane"
    if executable_lane not in EXECUTABLE_CODEX_WORK_LANES:
        executable_lane = "audit_lane"
    return {
        "need_id": need_id,
        "ordinal": int(ordinal),
        "score": int(score),
        "need_class": need_class,
        "lane_id": lane_id,
        "title": title,
        "domain_id": domain_id,
        "role_id": role_id,
        "role_tier": role_tier,
        "packet_id": packet_id,
        "queue_lane_id": executable_lane,
        "reason": reason,
        "biome_id": biome_id,
        "evidence": list(dict.fromkeys(str(item) for item in evidence if str(item).strip())),
    }


def _lane_from_need(row: Mapping[str, Any]) -> dict[str, Any]:
    context_reads = [
        {"kind": "file", "path": "ION/05_context/current/domain_weaver/.ion/ION_CONTEXT_CAPSULE.yaml", "required": True},
        {"kind": "file", "path": DEFAULT_CONTEXT_PACKAGE.as_posix(), "required": True},
    ]
    for path in row.get("evidence") or []:
        context_reads.append({"kind": "file", "path": str(path), "required": False})
    return {
        "lane_id": str(row["lane_id"]),
        "title": str(row["title"]),
        "domain_id": str(row["domain_id"]),
        "role_id": str(row["role_id"]),
        "role_tier": str(row["role_tier"]),
        "queue_lane_id": str(row["queue_lane_id"]),
        "packet_id": str(row["packet_id"]),
        "objective": str(row["reason"]),
        "required_context_reads": _dedupe_context_reads(context_reads),
        "planned_writes": [
            f"ION/05_context/current/domain_weaver/need_based_expansion/worker_returns/{row['lane_id']}.candidate.md"
        ],
        "need_score": int(row["score"]),
        "need_id": str(row["need_id"]),
        "actual_spawn_performed": False,
        "codex_queue_run_started": False,
    }


def _dedupe_need_rows(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        key = (str(row.get("need_id")), str(row.get("domain_id")), str(row.get("packet_id")))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(dict(row))
    return deduped


def _dedupe_context_reads(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        path = str(row.get("path") or "").strip()
        if not path or path in seen:
            continue
        seen.add(path)
        deduped.append({"kind": str(row.get("kind") or "file"), "path": path, "required": bool(row.get("required"))})
    return deduped[:64]


def _queue_lane_for_domain(domain_id: str, domain: Mapping[str, Any]) -> str:
    text = " ".join(
        [
            domain_id,
            str(domain.get("responsibility") or ""),
            str(domain.get("primary_biome_title") or domain.get("primary_biome_name") or ""),
        ]
    ).lower()
    if any(token in text for token in ("comms", "communication", "signal")):
        return "comms_lane"
    if any(token in text for token in ("context", "memory", "mount", "capsule")):
        return "context_lane"
    if any(token in text for token in ("proof", "receipt", "audit", "nemesis", "settlement")):
        return "audit_lane"
    if any(token in text for token in ("operator", "approval", "authority", "accepted_state", "materialization")):
        return "approval_governance_lane"
    if any(token in text for token in ("ui", "browser", "interface", "perception")):
        return "browser_lane"
    if any(token in text for token in ("runtime", "worker", "spawn", "queue", "implementation")):
        return "implementation_lane"
    return "architecture_lane"


def _select_domain_universe_path(root: Path) -> Path | None:
    candidates = sorted(root.glob(DOMAIN_UNIVERSE_LATEST_GLOB.as_posix()))
    if candidates:
        return candidates[-1]
    fallback = root / MISSION035_DOMAIN_UNIVERSE_PATH
    return fallback if fallback.is_file() else None


def _source_artifacts(root: Path, universe_path: Path | None) -> list[dict[str, Any]]:
    paths = [
        universe_path,
        root / MISSION035_DOMAIN_UNIVERSE_PATH,
        root / MISSION035_ROUTE_GATE_MATRIX_PATH,
        root / MISSION035_SPAWN_ROW_VALIDATION_MATRIX_PATH,
        root / MISSION035_PACKET_TEMPLATE_FAMILY_PATH,
        root / SWARM_READINESS_PATH,
        root / LARGER_FANOUT_READINESS_PATH,
    ]
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in paths:
        if path is None:
            continue
        rel = _rel(root, path)
        if rel in seen:
            continue
        seen.add(rel)
        rows.append(
            {
                "path": rel,
                "present": path.is_file(),
                "sha256": _sha256_file(path) if path.is_file() else "",
            }
        )
    return rows


def _blocked_or_deferred(
    larger_fanout: Mapping[str, Any],
    selected_lane_count: int,
    capacity_ceiling: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    recorded_cap = int(larger_fanout.get("max_candidate_lane_count") or 0)
    if recorded_cap and selected_lane_count > recorded_cap:
        rows.append(
            {
                "code": "selected_lanes_exceed_recorded_larger_fanout_candidate_cap",
                "recorded_cap": recorded_cap,
                "selected_lane_count": selected_lane_count,
                "interpretation": "This is a stale/control-plane capacity warning for candidate row seeding, not a proof that need selection should stop.",
            }
        )
    if capacity_ceiling == 0:
        rows.append(
            {
                "code": "capacity_ceiling_zero",
                "interpretation": "No lanes can be selected while capacity ceiling is zero.",
            }
        )
    return rows


def _domain_universe_summary(universe: Mapping[str, Any]) -> dict[str, Any]:
    domains = universe.get("domains") if isinstance(universe.get("domains"), list) else []
    biomes = universe.get("biomes") if isinstance(universe.get("biomes"), list) else []
    coverage = universe.get("coverage") if isinstance(universe.get("coverage"), Mapping) else {}
    counts = universe.get("counts") if isinstance(universe.get("counts"), Mapping) else {}
    return {
        "schema_id": universe.get("schema_id"),
        "domain_count": coverage.get("domain_count") or counts.get("observed_domain_count") or len(domains),
        "biome_count": coverage.get("biome_count") or counts.get("observed_biome_section_count") or len(biomes),
        "blockers": list(universe.get("blockers") or []),
    }


def _swarm_readiness_summary(readiness: Mapping[str, Any]) -> dict[str, Any]:
    blockers = readiness.get("blockers_ranked") if isinstance(readiness.get("blockers_ranked"), list) else []
    return {
        "schema_id": readiness.get("schema_id"),
        "status": readiness.get("status"),
        "verdict": readiness.get("verdict"),
        "blocker_count": len(blockers),
        "critical_or_high_blocker_count": sum(
            1
            for row in blockers
            if isinstance(row, Mapping) and str(row.get("severity") or "") in {"critical", "high"}
        ),
    }


def _route_gate_summary(route_matrix: Mapping[str, Any]) -> dict[str, Any]:
    summary = route_matrix.get("summary") if isinstance(route_matrix.get("summary"), Mapping) else {}
    return {
        "schema_id": route_matrix.get("schema_id"),
        "status": route_matrix.get("status"),
        "domain_weaver_mutating_route_gap_count": summary.get("domain_weaver_mutating_route_gap_count"),
        "handler_contract_gap_count": summary.get("handler_contract_gap_count"),
    }


def _spawn_matrix_summary(spawn_matrix: Mapping[str, Any]) -> dict[str, Any]:
    validation = spawn_matrix.get("validation") if isinstance(spawn_matrix.get("validation"), Mapping) else {}
    return {
        "schema_id": spawn_matrix.get("schema_id"),
        "status": spawn_matrix.get("status"),
        "validation_ok": validation.get("ok"),
        "recommended_next_packet": spawn_matrix.get("recommended_next_packet"),
        "blocker_count": len(spawn_matrix.get("blockers") or []),
    }


def _larger_fanout_summary(larger_fanout: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": larger_fanout.get("schema_id"),
        "readiness_ok": larger_fanout.get("readiness_ok"),
        "max_candidate_lane_count": larger_fanout.get("max_candidate_lane_count"),
        "requested_lane_count": larger_fanout.get("requested_lane_count"),
        "blockers": list(larger_fanout.get("blockers") or []),
    }


def _need_based_queue_request_rows(
    root: Path,
    *,
    request_paths: Sequence[str] | None,
    parent_worker_id: str,
    run_id: str | None,
    limit: int | None,
) -> list[dict[str, Any]]:
    candidates: list[Path] = []
    if request_paths:
        for raw_path in request_paths:
            resolved = _resolve_bounded_request_path(root, raw_path)
            if resolved is not None:
                candidates.append(resolved)
    else:
        candidates = sorted((root / CODEX_WORK_REQUESTS_DIR).glob("*.json"))

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    safe_parent = str(parent_worker_id or "").strip()
    safe_run_id = str(run_id or "").strip()
    for path in candidates:
        rel_path = _rel(root, path)
        if rel_path in seen:
            continue
        seen.add(rel_path)
        payload = _read_json(path)
        if not payload:
            continue
        dispatch = _mapping(payload.get("domain_weaver_spawn_dispatch"))
        if str(payload.get("request_kind") or "") != "domain_weaver_spawn_dispatch":
            continue
        if str(payload.get("work_class") or "") != "domain_weaver_spawn_dispatch":
            continue
        if str(payload.get("status") or "") != "QUEUED_FOR_CODEX_CARRIER":
            continue
        if safe_parent and str(dispatch.get("parent_worker_id") or "") != safe_parent:
            continue
        if safe_run_id:
            haystack = " ".join(
                str(dispatch.get(key) or "")
                for key in (
                    "source_spawn_request_path",
                    "dispatch_candidate_path",
                    "queue_packet_candidate_path",
                )
            )
            if safe_run_id not in haystack:
                continue
        rows.append({"path": path, "request_path": rel_path, "payload": payload})
        if limit is not None and len(rows) >= max(0, int(limit)):
            break
    return rows


def _resolve_bounded_request_path(root: Path, raw_path: Any) -> Path | None:
    text = str(raw_path or "").strip()
    if not text:
        return None
    path = Path(text)
    if path.is_absolute():
        resolved = path.resolve(strict=False)
    else:
        if any(part == ".." for part in path.parts):
            return None
        resolved = (root / path).resolve(strict=False)
    try:
        resolved.relative_to((root / CODEX_WORK_REQUESTS_DIR).resolve(strict=False))
    except ValueError:
        return None
    if resolved.suffix != ".json":
        return None
    return resolved if resolved.is_file() else None


def _context_materialization_plan_row(root: Path, row: Mapping[str, Any]) -> dict[str, Any]:
    payload = _mapping(row.get("payload"))
    request_path = str(row.get("request_path") or "")
    dispatch = _mapping(payload.get("domain_weaver_spawn_dispatch"))
    domain_id = str(payload.get("domain_id") or dispatch.get("requested_domain") or "").strip()
    role_id = str(payload.get("agent_role_id") or payload.get("role_id") or "").strip()
    raw_lane = str(payload.get("lane_id") or "").strip()
    lane_id = normalize_codex_work_lane_id(raw_lane) or raw_lane
    callsign = str(payload.get("callsign") or _display_from_id(role_id) or role_id).strip()
    role_tier = str(payload.get("role_tier") or "").strip()
    blockers: list[str] = []
    if not request_path:
        blockers.append("request_path_missing")
    if not domain_id:
        blockers.append("request_domain_id_missing")
    if not role_id:
        blockers.append("request_agent_role_id_missing")
    if not lane_id or lane_id not in EXECUTABLE_CODEX_WORK_LANES:
        blockers.append("request_lane_not_executable")
    agent = _agent_descriptor_from_request(
        payload,
        domain_id=domain_id,
        role_id=role_id,
        lane_id=lane_id,
        callsign=callsign,
        role_tier=role_tier,
    )
    domain = _domain_descriptor_from_request(
        payload,
        domain_id=domain_id,
        lane_id=lane_id,
        context_refs=_context_refs_from_request(payload, request_path=request_path),
    )
    mount_candidate = build_codex_agent_mount_candidate(root, agent, domain) if not blockers else {}
    return {
        "request_path": request_path,
        "request_id": payload.get("request_id"),
        "domain_id": domain_id,
        "role_id": role_id,
        "lane_id": lane_id,
        "role_tier": role_tier,
        "callsign": callsign,
        "source_spawn_request_path": dispatch.get("source_spawn_request_path"),
        "requested_packet": dispatch.get("requested_packet"),
        "agent": agent,
        "domain": domain,
        "mount_candidate": mount_candidate,
        "planned_mount_id": mount_candidate.get("mount_id"),
        "planned_mount_path": mount_candidate.get("mount_path"),
        "request_already_bound": bool(payload.get("selected_mount_id") and payload.get("working_capsule_identity")),
        "blockers": blockers,
    }


def _agent_descriptor_from_request(
    payload: Mapping[str, Any],
    *,
    domain_id: str,
    role_id: str,
    lane_id: str,
    callsign: str,
    role_tier: str,
) -> dict[str, Any]:
    context_refs = _context_refs_from_request(payload, request_path="")
    return {
        "role_id": role_id,
        "display_name": callsign or _display_from_id(role_id),
        "registry_primary_domain": domain_id,
        "registry_secondary_domains": [],
        "lane_ids": [lane_id] if lane_id else [],
        "queue_lanes": [lane_id] if lane_id else [],
        "role_tier": role_tier,
        "package_strategy": "domain_weaver_need_based_expansion_worker_context",
        "default_active_package_class": "need_selected_domain_agent_worker",
        "write_posture": "candidate_only",
        "context_paths": context_refs,
        "source_refs": context_refs,
        "mount_source_policy": "generated from queued need-based Domain Weaver spawn-dispatch request",
    }


def _domain_descriptor_from_request(
    payload: Mapping[str, Any],
    *,
    domain_id: str,
    lane_id: str,
    context_refs: list[str],
) -> dict[str, Any]:
    dispatch = _mapping(payload.get("domain_weaver_spawn_dispatch"))
    return {
        "domain_id": domain_id,
        "display_name": _display_from_id(domain_id),
        "purpose": str(payload.get("objective") or dispatch.get("requested_packet") or "need-selected Domain Weaver worker lane"),
        "status": "candidate_need_selected",
        "authority": "candidate_only",
        "fact_posture": "candidate",
        "maturity_estimate": "worker_review_required",
        "lane_ids": [lane_id] if lane_id else [],
        "paths": context_refs,
        "owned_or_stewarded_surfaces": context_refs,
        "mount_source_policy": "generated from queued need-based Domain Weaver spawn-dispatch request",
    }


def _context_refs_from_request(payload: Mapping[str, Any], *, request_path: str) -> list[str]:
    refs: list[str] = []
    for row in list(payload.get("required_context_reads") or []):
        if isinstance(row, Mapping):
            _append_unique(refs, row.get("path"))
        else:
            _append_unique(refs, row)
    for key in ("domain_context_package", "packet_path", "latest_return_packet_path"):
        _append_unique(refs, payload.get(key))
    dispatch = _mapping(payload.get("domain_weaver_spawn_dispatch"))
    for key in ("source_spawn_request_path", "dispatch_candidate_path", "queue_packet_candidate_path"):
        _append_unique(refs, dispatch.get(key))
    _append_unique(refs, request_path)
    _append_unique(refs, DEFAULT_CONTEXT_PACKAGE.as_posix())
    return refs


def _context_materialization_target_paths(plans: Sequence[Mapping[str, Any]]) -> list[str]:
    targets: list[str] = []
    for plan in plans:
        _append_unique(targets, plan.get("request_path"))
        _append_unique(targets, plan.get("planned_mount_path"))
    _append_unique(targets, CONTEXT_MATERIALIZATION_RECEIPTS_DIR.as_posix())
    return targets


def _context_materialization_write_gate(
    *,
    execute_write: bool,
    confirmation: str | None,
    idempotency_key: str | None,
    agent_id: str | None,
    write_intent_lease_id: str | None,
    target_paths: Sequence[str],
) -> dict[str, Any]:
    blockers: list[str] = []
    if execute_write:
        if confirmation != PRESSURE_WAVE_CONFIRMATION:
            blockers.append("confirmation_required")
        if not str(idempotency_key or "").strip():
            blockers.append("idempotency_key_required")
        if not str(agent_id or "").strip():
            blockers.append("agent_id_required")
        if not str(write_intent_lease_id or "").strip():
            blockers.append("write_intent_lease_id_required")
        if not target_paths:
            blockers.append("target_paths_required")
    return {
        "ok": not blockers,
        "execute_write": bool(execute_write),
        "blockers": blockers,
        "confirmation_required": PRESSURE_WAVE_CONFIRMATION,
        "idempotency_key_required": True,
        "agent_id_required": True,
        "write_intent_lease_id_required": True,
        "required_target_roots": list(CONTEXT_MATERIALIZATION_REQUIRED_TARGET_ROOTS),
        "target_paths": list(target_paths),
    }


def _apply_context_materialization_plan(
    root: Path,
    plan: Mapping[str, Any],
    *,
    generated_at: str,
    idempotency_key: str,
    agent_id: str,
    write_intent_lease_id: str,
    communication_directory: Mapping[str, Any],
) -> dict[str, Any]:
    if plan.get("blockers"):
        return {
            "request_path": plan.get("request_path"),
            "status": "context_materialization_skipped",
            "blockers": list(plan.get("blockers") or []),
            "request_patched": False,
            "mount_materialized": False,
        }
    request_path = root / str(plan.get("request_path") or "")
    try:
        original_request_text = request_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {
            "request_path": plan.get("request_path"),
            "status": "context_materialization_skipped",
            "blockers": ["request_unreadable_before_context_materialization"],
            "request_patched": False,
            "mount_materialized": False,
        }
    payload = _read_json(request_path)
    existing = _mapping(payload.get("need_based_context_materialization"))
    if (
        existing.get("idempotency_key") == idempotency_key
        and payload.get("selected_mount_id")
        and isinstance(payload.get("working_capsule_identity"), Mapping)
        and (root / str(payload.get("selected_mount_path") or "") / "ION_AGENT_MOUNT_MANIFEST.json").is_file()
    ):
        return {
            "request_path": plan.get("request_path"),
            "request_id": payload.get("request_id"),
            "status": "context_materialization_idempotent_replay",
            "selected_mount_id": payload.get("selected_mount_id"),
            "selected_mount_path": payload.get("selected_mount_path"),
            "request_patched": False,
            "mount_materialized": True,
            "blockers": [],
        }
    mount = materialize_codex_agent_mount(
        root,
        plan["agent"],
        plan["domain"],
        communication_directory=communication_directory,
    )
    context_identity = _read_json(root / str(mount.get("portable_context_identity_path") or ""))
    working_identity = dict(_mapping(context_identity.get("working_capsule_identity")))
    working_identity["lane_id"] = plan.get("lane_id")
    working_identity["selected_mount_id"] = mount.get("mount_id")
    working_identity["selected_mount_path"] = mount.get("mount_path")
    working_identity["codex_agent_mount_path"] = mount.get("mount_path")
    mount_manifest_path = str(mount.get("manifest_path") or "")
    payload["selected_mount_id"] = mount.get("mount_id")
    payload["selected_mount_path"] = mount.get("mount_path")
    payload["codex_agent_mount_id"] = mount.get("mount_id")
    payload["codex_agent_mount_path"] = mount.get("mount_path")
    payload["codex_agent_mount_manifest"] = mount_manifest_path
    payload["ai_movement_root_envelope"] = _merge_ai_movement_root_envelope(
        payload.get("ai_movement_root_envelope"),
        mount_id=str(mount.get("mount_id") or ""),
        mount_path=str(mount.get("mount_path") or ""),
        mount_manifest_path=mount_manifest_path,
    )
    payload["working_capsule_identity"] = working_identity
    payload["updated_at"] = generated_at
    payload["need_based_context_materialization"] = {
        "schema_id": CONTEXT_MATERIALIZATION_SCHEMA_ID,
        "status": "request_bound_to_generated_codex_agent_mount",
        "generated_at": generated_at,
        "idempotency_key": idempotency_key,
        "agent_id": agent_id,
        "write_intent_lease_id": write_intent_lease_id,
        "parent_worker_id": DEFAULT_PARENT_WORKER_ID,
        "source_spawn_request_path": plan.get("source_spawn_request_path"),
        "selected_mount_id": mount.get("mount_id"),
        "selected_mount_path": mount.get("mount_path"),
        "codex_agent_mount_id": mount.get("mount_id"),
        "codex_agent_mount_path": mount.get("mount_path"),
        "codex_agent_mount_manifest": mount_manifest_path,
        "portable_context_identity_path": mount.get("portable_context_identity_path"),
        "lane_id": plan.get("lane_id"),
        "domain_id": plan.get("domain_id"),
        "role_id": plan.get("role_id"),
        "actual_spawn_performed": False,
        "codex_queue_run_started": False,
        "worker_start_performed": False,
        "accepted_state_claimed": False,
    }
    request_path.write_text(_stable_json(payload), encoding="utf-8")
    refresh_binding = {
        "schema_id": "ion.domain_weaver.need_based_expansion.context_refresh_binding.v0_1_candidate",
        "request_id": payload.get("request_id"),
        "request_path": plan.get("request_path"),
        "idempotency_key": idempotency_key,
        "write_intent_lease_id": write_intent_lease_id,
        "generated_at": generated_at,
        "candidate_context_only": True,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }
    try:
        compilation = compile_codex_agent_mount_active_context(
            root,
            str(mount.get("mount_id") or ""),
            generated_at=generated_at,
            refresh_binding=refresh_binding,
        )
        active_context_targets = {
            root / str(mount.get("active_context_package_path") or ""): str(
                compilation["json_text"]
            ),
            root / str(mount.get("active_context_package_md_path") or ""): str(
                compilation["markdown_text"]
            ),
            root / str(mount.get("portable_active_context_package_path") or ""): str(
                compilation["json_text"]
            ),
            root / str(mount.get("portable_active_context_package_md_path") or ""): str(
                compilation["markdown_text"]
            ),
        }
        if len(active_context_targets) != 4 or any(
            path.is_symlink()
            or not path.is_file()
            or path.stat().st_nlink != 1
            for path in active_context_targets
        ):
            raise ValueError("active context pair targets are not four single-link regular files")
        for path, text in active_context_targets.items():
            path.write_text(text, encoding="utf-8")
    except (KeyError, OSError, TypeError, ValueError) as exc:
        request_path.write_text(original_request_text, encoding="utf-8")
        return {
            "request_path": plan.get("request_path"),
            "request_id": payload.get("request_id"),
            "status": "context_materialization_compile_blocked",
            "selected_mount_id": mount.get("mount_id"),
            "selected_mount_path": mount.get("mount_path"),
            "request_patched": False,
            "mount_materialized": True,
            "blockers": [
                f"active_context_compilation_failed:{type(exc).__name__}"
            ],
        }
    return {
        "request_path": plan.get("request_path"),
        "request_id": payload.get("request_id"),
        "status": "context_materialized_and_request_bound",
        "selected_mount_id": mount.get("mount_id"),
        "selected_mount_path": mount.get("mount_path"),
        "portable_context_identity_path": mount.get("portable_context_identity_path"),
        "working_capsule_identity_present": bool(working_identity),
        "active_context_compiler_source_digest": compilation.get(
            "compiler_source_digest"
        ),
        "active_context_target_paths": [
            _rel(root, path) for path in active_context_targets
        ],
        "request_patched": True,
        "mount_materialized": True,
        "blockers": [],
    }


def _merge_ai_movement_root_envelope(
    existing: Any,
    *,
    mount_id: str,
    mount_path: str,
    mount_manifest_path: str,
) -> dict[str, Any]:
    envelope = dict(existing) if isinstance(existing, Mapping) else {}
    if mount_id:
        envelope["codex_agent_mount_id"] = mount_id
    if mount_path:
        envelope["codex_agent_mount_path"] = mount_path
        envelope["worker_launch_cwd"] = mount_path
        envelope["target_command_cwd"] = mount_path
    if mount_manifest_path:
        envelope["codex_agent_mount_manifest"] = mount_manifest_path
        envelope["ion_codex_agent_mount_manifest"] = mount_manifest_path
    return envelope


def _write_context_materialization_receipts(
    root: Path,
    *,
    generated_at: str,
    idempotency_key: str,
    result_rows: list[dict[str, Any]],
    parent_worker_id: str,
    run_id: str | None,
    write_gate: Mapping[str, Any],
) -> list[str]:
    receipts_dir = root / CONTEXT_MATERIALIZATION_RECEIPTS_DIR
    receipts_dir.mkdir(parents=True, exist_ok=True)
    stamp = _stamp(generated_at)
    key_fragment = _safe_fragment(idempotency_key)[:48]
    receipt_path = receipts_dir / f"{stamp}_{key_fragment}.candidate.json"
    latest_path = receipts_dir / "DOMAIN_WEAVER_NEED_BASED_CONTEXT_MATERIALIZATION.latest.candidate.json"
    receipt = {
        "schema_id": CONTEXT_MATERIALIZATION_SCHEMA_ID,
        "status": "need_based_expansion_context_materialization_receipt",
        "generated_at": generated_at,
        "parent_worker_id": parent_worker_id,
        "run_id": run_id,
        "idempotency_key": idempotency_key,
        "write_gate": dict(write_gate),
        "materialized_request_count": sum(
            1 for row in result_rows if row.get("mount_materialized")
        ),
        "blocked_request_count": sum(
            1 for row in result_rows if row.get("blockers")
        ),
        "patched_request_count": sum(1 for row in result_rows if row.get("request_patched")),
        "result_rows": result_rows,
        "authority": CONTEXT_MATERIALIZATION_AUTHORITY,
        "effects": {
            "codex_agent_mounts_written": any(
                row.get("mount_materialized") for row in result_rows
            ),
            "codex_work_requests_patched": any(row.get("request_patched") for row in result_rows),
            "codex_queue_run_started": False,
            "workers_started": False,
            "accepted_state_touched": False,
            "domain_weaver_projection_modified": False,
        },
    }
    text = _stable_json(receipt)
    receipt_path.write_text(text, encoding="utf-8")
    latest_path.write_text(text, encoding="utf-8")
    return [_rel(root, receipt_path), _rel(root, latest_path)]


def _context_materialization_result(
    root: Path,
    *,
    generated_at: str,
    status: str,
    parent_worker_id: str,
    run_id: str | None,
    execute_write: bool,
    write_gate: Mapping[str, Any],
    plans: list[dict[str, Any]],
    materialized_rows: list[dict[str, Any]],
    receipt_paths: list[str],
    effects: Mapping[str, Any],
) -> dict[str, Any]:
    blocked_plans = [row for row in plans if row.get("blockers")]
    blocked_materialization_rows = [
        row for row in materialized_rows if row.get("blockers")
    ]
    successful_statuses = {
        "context_materialized_and_request_bound",
        "context_materialization_idempotent_replay",
    }
    successful_materialization_rows = [
        row
        for row in materialized_rows
        if str(row.get("status") or "") in successful_statuses
    ]
    execution_complete = (
        bool(plans)
        and len(successful_materialization_rows) == len(plans)
        and not blocked_materialization_rows
    )
    return {
        "schema_id": CONTEXT_MATERIALIZATION_SCHEMA_ID,
        "status": status,
        "generated_at": generated_at,
        "active_root": str(root),
        "parent_worker_id": parent_worker_id,
        "run_id": run_id,
        "execute_write": bool(execute_write),
        "write_gate": dict(write_gate),
        "request_count": len(plans),
        "blocked_request_count": (
            len(blocked_materialization_rows)
            if materialized_rows
            else len(blocked_plans)
        ),
        "materialized_request_count": sum(
            1 for row in materialized_rows if row.get("mount_materialized")
        ),
        "patched_request_count": sum(1 for row in materialized_rows if row.get("request_patched")),
        "request_paths": [str(row.get("request_path")) for row in plans if row.get("request_path")],
        "planned_mount_paths": [str(row.get("planned_mount_path")) for row in plans if row.get("planned_mount_path")],
        "planned_rows": plans,
        "materialized_rows": materialized_rows,
        "receipt_paths": receipt_paths,
        "authority": AUTHORITY,
        "effects": dict(effects),
        "actual_spawn_performed": False,
        "codex_queue_run_started": False,
        "worker_start_performed": False,
        "accepted_state_claimed": False,
        "production_or_live_authority": False,
        "secrets_authority": False,
        "next_action": (
            "run_exact_worker_start_readiness_for_bound_request_paths"
            if execute_write and execution_complete
            else "repair_context_materialization_blockers_or_preview_exact_request_paths"
            if blocked_plans or blocked_materialization_rows
            else "execute_context_materialization_with_bounded_write_gate"
            if not execute_write and plans
            else "no_need_based_queued_requests_found"
        ),
    }


def _display_from_id(value: str) -> str:
    text = str(value or "").strip()
    for prefix in ("role.", "domain."):
        if text.startswith(prefix):
            text = text[len(prefix) :]
    text = text.replace(".", " ").replace("_", " ").replace("-", " ")
    return " ".join(part.capitalize() for part in text.split()) or "ION Worker"


def _append_unique(rows: list[str], value: Any) -> None:
    text = str(value or "").strip()
    if text and text not in rows:
        rows.append(text)


def _severity_bonus(severity: str) -> int:
    return {"critical": 70, "high": 40, "medium": 15}.get(str(severity).lower(), 0)


def _root_proof(root: Path) -> dict[str, Any]:
    return {
        "pyproject_toml": (root / "pyproject.toml").is_file(),
        "repo_authority": (root / "ION/REPO_AUTHORITY.md").is_file(),
        "proof_ok": (root / "pyproject.toml").is_file() and (root / "ION/REPO_AUTHORITY.md").is_file(),
    }


def _require_active_root(active_root: str | Path) -> Path:
    root = Path(active_root).expanduser().resolve(strict=False)
    proof = _root_proof(root)
    if not proof["proof_ok"]:
        raise ValueError("active_root_proof_failed")
    return root


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _stable_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(dict(payload), indent=2, sort_keys=True) + "\n"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()


def _rel_source(path: Path) -> str:
    return path.as_posix()


def _resolve_output_dir(root: Path, output_dir: str | Path | None) -> Path:
    if output_dir is None:
        return root / DEFAULT_OUTPUT_DIR
    path = Path(output_dir)
    return path if path.is_absolute() else root / path


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _stamp(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        parsed = datetime.now(timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safe_fragment(value: object) -> str:
    rendered = str(value or "").strip().lower()
    rendered = re.sub(r"[^a-z0-9._-]+", "_", rendered)
    rendered = rendered.strip("._-")
    return rendered[:96] or "need"


def _domain_slug(domain_id: str) -> str:
    rendered = domain_id
    if rendered.startswith("domain."):
        rendered = rendered[len("domain.") :]
    return _safe_fragment(rendered.replace(".", "_"))


def _packet_fragment(slug: str) -> str:
    return _safe_fragment(slug).upper().replace("_", "-").replace(".", "-")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
