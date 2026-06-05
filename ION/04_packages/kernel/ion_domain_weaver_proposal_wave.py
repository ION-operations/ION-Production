"""Domain Weaver proposal-write swarm planning.

This module gives Domain Weaver a writeable acceleration surface that is still
auditable: workers may write proposal artifacts in bounded lane workspaces, but
they do not receive raw source-write, patch-apply, production, live execution,
or accepted-state authority.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping


PROPOSAL_WAVE_PLAN_SCHEMA_ID = "ion.domain_weaver.proposal_wave_plan.v0_1_candidate"
PROPOSAL_WORKSPACE_SEED_SCHEMA_ID = (
    "ion.domain_weaver.proposal_workspace_seed.v0_1"
)
PROPOSAL_WORKSPACE_SCHEMA_ID = "ion.domain_weaver.proposal_workspace.v0_1_candidate"
PROPOSAL_WORKSPACE_RECEIPT_SCHEMA_ID = (
    "ion.domain_weaver.proposal_workspace_receipt.v0_1"
)
PROPOSAL_WRITE_CONFIRMATION = "ION_PROPOSAL_WRITE_CONFIRMED"

DEFAULT_PROPOSAL_ROOT = Path("ION/05_context/current/domain_weaver/proposal_wave")
DEFAULT_NATIVE_SLOT_CAP = 6
DEFAULT_ACTIVE_NATIVE_AGENT_COUNT = 3
DEFAULT_PROPOSAL_WORKSPACE_CAP = 18

PROPOSAL_TIERS: dict[str, dict[str, Any]] = {
    "T0_READ_ONLY_SCOUT": {
        "description": "Read and return findings only.",
        "proposal_file_write_allowed": False,
        "patch_proposal_file_allowed": False,
        "raw_source_write_allowed": False,
        "patch_apply_allowed": False,
        "worker_assignable": True,
    },
    "T1_PROPOSAL_FILE_WRITER": {
        "description": "Write proposal markdown/json only in assigned proposal workspace.",
        "proposal_file_write_allowed": True,
        "patch_proposal_file_allowed": False,
        "raw_source_write_allowed": False,
        "patch_apply_allowed": False,
        "worker_assignable": True,
    },
    "T2_PATCH_PROPOSAL_WRITER": {
        "description": "Write proposal artifacts plus unapplied patch/diff proposals.",
        "proposal_file_write_allowed": True,
        "patch_proposal_file_allowed": True,
        "raw_source_write_allowed": False,
        "patch_apply_allowed": False,
        "worker_assignable": True,
    },
    "T3_LEAD_APPLY_CANDIDATE": {
        "description": "Lead-only apply candidate after review and explicit confirmation.",
        "proposal_file_write_allowed": True,
        "patch_proposal_file_allowed": True,
        "raw_source_write_allowed": False,
        "patch_apply_allowed": False,
        "worker_assignable": False,
    },
}

DEFAULT_PROPOSAL_LANES: tuple[dict[str, Any], ...] = (
    {
        "lane_id": "concurrency_governor",
        "title": "Concurrency Governor",
        "tier": "T1_PROPOSAL_FILE_WRITER",
        "domain_id": "domain.domain_weaver_fanout_control",
        "role_id": "role.domain_weaver_concurrency_governor",
        "objective": "Define native-slot, queue-row, proposal-workspace, and fan-in caps for serious self-evolution.",
    },
    {
        "lane_id": "proposal_workspace_protocol",
        "title": "Proposal Workspace Protocol",
        "tier": "T2_PATCH_PROPOSAL_WRITER",
        "domain_id": "domain.proposal_workspace_protocol",
        "role_id": "role.proposal_workspace_steward",
        "objective": "Specify required proposal fields, receipt rules, review gates, and allowed file patterns.",
    },
    {
        "lane_id": "context_graph_branch_fabric",
        "title": "Context Graph Branch Fabric",
        "tier": "T2_PATCH_PROPOSAL_WRITER",
        "domain_id": "domain.context_graph_branch_fabric",
        "role_id": "role.context_graph_cartographer",
        "objective": "Design lazy branch visibility so agents can see IDE/files/tool state through context deltas.",
    },
    {
        "lane_id": "agent_comms_autoreaction",
        "title": "Agent Comms Autoreaction",
        "tier": "T2_PATCH_PROPOSAL_WRITER",
        "domain_id": "domain.agent_communication_systems",
        "role_id": "role.agent_comms_protocol_lead",
        "objective": "Close the original autoreaction proof gap without confusing alternate-worker recovery for automatic reaction.",
    },
    {
        "lane_id": "queue_gateway_route_parity",
        "title": "Queue Gateway Route Parity",
        "tier": "T2_PATCH_PROPOSAL_WRITER",
        "domain_id": "domain.action_route_parity",
        "role_id": "role.gateway_route_auditor",
        "objective": "Verify action route parity, gateway freshness, mutation gates, and exact queue start behavior.",
    },
    {
        "lane_id": "proof_receipt_graph",
        "title": "Proof Receipt Graph",
        "tier": "T2_PATCH_PROPOSAL_WRITER",
        "domain_id": "domain.receipt_proof_graph",
        "role_id": "role.proof_graph_librarian",
        "objective": "Map task-return, provenance, native transcript, fan-in, and settlement receipts into a navigable graph.",
    },
    {
        "lane_id": "codex_carrier_reliability",
        "title": "Codex Carrier Reliability",
        "tier": "T2_PATCH_PROPOSAL_WRITER",
        "domain_id": "domain.codex_carrier_sync",
        "role_id": "role.codex_carrier_steward",
        "objective": "Harden saved-session resume, usage-limit prompt-through, mount freshness, and alternate-worker returns.",
    },
    {
        "lane_id": "context_capsule_mount_quality",
        "title": "Context Capsule Mount Quality",
        "tier": "T2_PATCH_PROPOSAL_WRITER",
        "domain_id": "domain.context_mount_quality",
        "role_id": "role.context_capsule_curator",
        "objective": "Audit per-agent/per-domain capsule uniqueness and generated codex_agent_mount quality.",
    },
    {
        "lane_id": "monolith_decomposition",
        "title": "Monolith Decomposition",
        "tier": "T2_PATCH_PROPOSAL_WRITER",
        "domain_id": "domain.monolith_decomposition",
        "role_id": "role.monolith_decomposition_lead",
        "objective": "Rank the next disjoint implementation slices for Domain Weaver monolith reduction.",
    },
    {
        "lane_id": "ui_operator_truth_surface",
        "title": "UI Operator Truth Surface",
        "tier": "T1_PROPOSAL_FILE_WRITER",
        "domain_id": "domain.operator_workbench_truth_surface",
        "role_id": "role.ui_truth_surface_adapter",
        "objective": "Specify how chat, drawers, IDE, timeline, context systems, and swarm status should show candidate vs accepted truth.",
    },
    {
        "lane_id": "semantic_alias_projection_sequence",
        "title": "Semantic Alias Projection Sequence",
        "tier": "T2_PATCH_PROPOSAL_WRITER",
        "domain_id": "domain.semantic_alias_canonicalization",
        "role_id": "role.semantic_alias_gatekeeper",
        "objective": "Prepare the alias apply and projection refresh sequence with hash gates and rollback evidence.",
    },
    {
        "lane_id": "nemesis_false_autonomy_audit",
        "title": "Nemesis False Autonomy Audit",
        "tier": "T1_PROPOSAL_FILE_WRITER",
        "domain_id": "domain.nemesis_pressure_audit",
        "role_id": "role.nemesis_pressure_auditor",
        "objective": "Attack false autonomy, queue storms, stale context, fake proof, and accepted-state drift.",
    },
)


def build_proposal_wave_plan(
    active_root: str | Path,
    *,
    lanes: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None = None,
    native_slot_cap: int = DEFAULT_NATIVE_SLOT_CAP,
    active_native_agent_count: int = DEFAULT_ACTIVE_NATIVE_AGENT_COUNT,
    proposal_workspace_cap: int = DEFAULT_PROPOSAL_WORKSPACE_CAP,
    proposal_root: str | Path = DEFAULT_PROPOSAL_ROOT,
) -> dict[str, Any]:
    """Build a wide proposal-write plan without writing files or starting workers."""

    root = _require_active_root(active_root)
    normalized_lanes = _normalize_lanes(lanes)
    native_cap = max(0, int(native_slot_cap))
    active_native_count = max(0, int(active_native_agent_count))
    available_native_slots = max(0, native_cap - active_native_count)
    workspace_cap = max(0, int(proposal_workspace_cap))
    foreground_lanes = normalized_lanes[:available_native_slots]
    overflow_lanes = normalized_lanes[available_native_slots:]
    blockers = _plan_blockers(
        normalized_lanes,
        native_slot_cap=native_cap,
        proposal_workspace_cap=workspace_cap,
    )
    return {
        "schema_id": PROPOSAL_WAVE_PLAN_SCHEMA_ID,
        "status": "proposal_wave_plan_built",
        "created_at": _utc_now(),
        "active_root": str(root),
        "proposal_root": _relative_posix(root, _proposal_root(root, proposal_root)),
        "lane_count": len(normalized_lanes),
        "tier_model": PROPOSAL_TIERS,
        "caps": {
            "native_slot_cap": native_cap,
            "active_native_agent_count": active_native_count,
            "available_native_slots": available_native_slots,
            "proposal_workspace_cap": workspace_cap,
            "recursive_child_spawn_cap": 0,
            "raw_source_write_allowed": False,
            "patch_apply_allowed": False,
            "general_queue_processing_allowed": False,
        },
        "lane_counts": {
            "foreground_native_assignable_count": len(foreground_lanes),
            "overflow_proposal_workspace_count": len(overflow_lanes),
            "proposal_workspace_template_count": len(normalized_lanes),
        },
        "lanes": normalized_lanes,
        "foreground_native_assignable_lanes": foreground_lanes,
        "overflow_proposal_workspace_lanes": overflow_lanes,
        "workspace_templates": [
            _workspace_template(root, row, proposal_root=proposal_root)
            for row in normalized_lanes
        ],
        "blockers": blockers,
        "hard_stop_conditions": _hard_stop_conditions(),
        "authority": _authority_block(),
        "actual_spawn_performed": False,
        "codex_queue_run_started": False,
        "worker_start_allowed": False,
        "accepted_state_claimed": False,
        "product_state_accepted": False,
        "verdict": "PROPOSAL_WRITE_SWARM_PLAN_READY_CANDIDATE_ONLY"
        if not blockers
        else "PROPOSAL_WRITE_SWARM_PLAN_HAS_BLOCKERS",
    }


def seed_proposal_workspaces(
    active_root: str | Path,
    *,
    lanes: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None = None,
    proposal_root: str | Path = DEFAULT_PROPOSAL_ROOT,
    wave_id: str | None = None,
    execute_write: bool = False,
    confirmation: str | None = None,
    idempotency_key: str | None = None,
    agent_id: str | None = None,
    write_intent_lease_id: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Seed bounded proposal workspaces for auditable worker writes."""

    root = _require_active_root(active_root)
    normalized_lanes = _normalize_lanes(lanes)
    if limit is not None:
        normalized_lanes = normalized_lanes[: max(0, int(limit))]
    wave_key = _safe_fragment(wave_id or idempotency_key or _utc_stamp())
    workspace_root = _proposal_root(root, proposal_root) / wave_key
    _assert_under_proposal_root(root, workspace_root, proposal_root=proposal_root)
    templates = [
        _workspace_template(root, row, proposal_root=proposal_root, wave_id=wave_key)
        for row in normalized_lanes
    ]
    gate = _write_gate(
        execute_write=execute_write,
        confirmation=confirmation,
        idempotency_key=idempotency_key,
        agent_id=agent_id,
        write_intent_lease_id=write_intent_lease_id,
    )
    if not execute_write or not gate["ok"]:
        return {
            "schema_id": PROPOSAL_WORKSPACE_SEED_SCHEMA_ID,
            "status": "proposal_workspace_seed_preview"
            if not execute_write
            else "proposal_workspace_seed_blocked",
            "created_at": _utc_now(),
            "active_root": str(root),
            "proposal_root": _relative_posix(root, _proposal_root(root, proposal_root)),
            "wave_id": wave_key,
            "execute_write": bool(execute_write),
            "write_gate": gate,
            "workspace_count": 0,
            "workspace_templates": templates,
            "workspace_paths": [],
            "idempotent_replay_paths": [],
            "authority": _authority_block(),
            "actual_spawn_performed": False,
            "codex_queue_run_started": False,
            "worker_start_allowed": False,
            "accepted_state_claimed": False,
            "product_state_accepted": False,
        }

    seeded: list[dict[str, Any]] = []
    replay_paths: list[str] = []
    for row in normalized_lanes:
        seeded_row = _write_workspace(
            root,
            row,
            workspace_root=workspace_root,
            proposal_root=proposal_root,
            gate=gate,
            agent_id=str(agent_id),
            write_intent_lease_id=str(write_intent_lease_id),
            idempotency_key=str(idempotency_key),
        )
        seeded.append(seeded_row)
        if seeded_row.get("idempotent_replay"):
            replay_paths.append(str(seeded_row["workspace_path"]))

    return {
        "schema_id": PROPOSAL_WORKSPACE_SEED_SCHEMA_ID,
        "status": "proposal_workspaces_seeded",
        "created_at": _utc_now(),
        "active_root": str(root),
        "proposal_root": _relative_posix(root, _proposal_root(root, proposal_root)),
        "wave_id": wave_key,
        "execute_write": True,
        "write_gate": gate,
        "workspace_count": len(seeded),
        "workspace_paths": [str(row["workspace_path"]) for row in seeded],
        "idempotent_replay_paths": replay_paths,
        "workspaces": seeded,
        "authority": _authority_block(),
        "actual_spawn_performed": False,
        "codex_queue_run_started": False,
        "worker_start_allowed": False,
        "accepted_state_claimed": False,
        "product_state_accepted": False,
        "next_action": "assign_workers_to_proposal_workspaces_then_fan_in_through_nemesis_review",
    }


def render_proposal_wave_plan_markdown(plan: Mapping[str, Any]) -> str:
    """Render a compact operator-facing plan summary."""

    lines = [
        "# Domain Weaver Proposal-Write Swarm Plan",
        "",
        f"- status: `{plan.get('status')}`",
        f"- verdict: `{plan.get('verdict')}`",
        f"- lane_count: `{plan.get('lane_count')}`",
        f"- proposal_root: `{plan.get('proposal_root')}`",
        "- authority: candidate-only; no production/live/accepted-state/secrets",
        "- nonclaim: proposal workspaces are not product-state acceptance",
        "",
        "## Caps",
    ]
    caps = plan.get("caps") if isinstance(plan.get("caps"), Mapping) else {}
    for key in sorted(caps):
        lines.append(f"- {key}: `{caps[key]}`")
    lines.extend(["", "## Lanes"])
    for row in plan.get("lanes") or []:
        if not isinstance(row, Mapping):
            continue
        lines.append(
            f"- `{row.get('lane_id')}` | `{row.get('tier')}` | {row.get('title')}"
        )
    blockers = list(plan.get("blockers") or [])
    lines.extend(["", "## Blockers"])
    lines.extend([f"- {blocker}" for blocker in blockers] or ["- none"])
    lines.extend(["", "## Hard Stops"])
    lines.extend(f"- {item}" for item in plan.get("hard_stop_conditions") or [])
    lines.append("")
    return "\n".join(lines)


def _normalize_lanes(
    lanes: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None,
) -> list[dict[str, Any]]:
    source = list(lanes or DEFAULT_PROPOSAL_LANES)
    normalized: list[dict[str, Any]] = []
    for index, lane in enumerate(source, start=1):
        tier = str(lane.get("tier") or "T1_PROPOSAL_FILE_WRITER").strip()
        tier_policy = PROPOSAL_TIERS.get(tier)
        blockers: list[str] = []
        if not tier_policy:
            blockers.append("unknown_proposal_tier")
            tier = "T1_PROPOSAL_FILE_WRITER"
            tier_policy = PROPOSAL_TIERS[tier]
        lane_id = _safe_fragment(lane.get("lane_id") or lane.get("title") or f"lane-{index:02d}")
        planned_proposal_files = _proposal_files_for_lane(lane_id, tier)
        normalized.append(
            {
                "lane_index": index,
                "lane_id": lane_id,
                "title": _clean_text(lane.get("title")) or f"Proposal Lane {index}",
                "tier": tier,
                "tier_policy": dict(tier_policy),
                "domain_id": _safe_token(lane.get("domain_id") or "domain.domain_weaver", "domain_id"),
                "role_id": _safe_token(lane.get("role_id") or "role.domain_weaver_specialist", "role_id"),
                "objective": _clean_text(lane.get("objective")) or _clean_text(lane.get("title")) or lane_id,
                "required_context_reads": _context_reads(lane),
                "planned_proposal_files": planned_proposal_files,
                "worker_assignable": bool(tier_policy["worker_assignable"]),
                "proposal_file_write_allowed": bool(tier_policy["proposal_file_write_allowed"]),
                "patch_proposal_file_allowed": bool(tier_policy["patch_proposal_file_allowed"]),
                "raw_source_write_allowed": False,
                "patch_apply_allowed": False,
                "accepted_state_claimed": False,
                "blockers": blockers,
            }
        )
    return normalized


def _proposal_files_for_lane(lane_id: str, tier: str) -> list[str]:
    files = ["PROPOSAL_WORKSPACE.json", "README.md", "workspace_receipt.json"]
    if PROPOSAL_TIERS[tier]["proposal_file_write_allowed"]:
        files.extend(["proposal.candidate.md", "proposal.candidate.json"])
    if PROPOSAL_TIERS[tier]["patch_proposal_file_allowed"]:
        files.append("patch_proposal.diff")
    return files


def _workspace_template(
    root: Path,
    row: Mapping[str, Any],
    *,
    proposal_root: str | Path,
    wave_id: str = "<wave_id>",
) -> dict[str, Any]:
    lane_id = str(row["lane_id"])
    workspace_path = _proposal_root(root, proposal_root) / wave_id / lane_id
    return {
        "schema_id": PROPOSAL_WORKSPACE_SCHEMA_ID,
        "lane_id": lane_id,
        "tier": row["tier"],
        "workspace_path": _relative_posix(root, workspace_path),
        "expected_files": list(row.get("planned_proposal_files") or []),
        "allowed_write_root": _relative_posix(root, workspace_path),
        "raw_source_write_allowed": False,
        "patch_apply_allowed": False,
        "accepted_state_claimed": False,
    }


def _write_workspace(
    root: Path,
    row: Mapping[str, Any],
    *,
    workspace_root: Path,
    proposal_root: str | Path,
    gate: Mapping[str, Any],
    agent_id: str,
    write_intent_lease_id: str,
    idempotency_key: str,
) -> dict[str, Any]:
    lane_id = str(row["lane_id"])
    lane_workspace = workspace_root / lane_id
    _assert_under_proposal_root(root, lane_workspace, proposal_root=proposal_root)
    workspace_rel = _relative_posix(root, lane_workspace)
    workspace_json = lane_workspace / "PROPOSAL_WORKSPACE.json"
    idempotent_replay = workspace_json.is_file()
    lane_workspace.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_id": PROPOSAL_WORKSPACE_SCHEMA_ID,
        "status": "proposal_workspace_seeded",
        "created_at": _utc_now(),
        "active_root": str(root),
        "workspace_path": workspace_rel,
        "lane": dict(row),
        "write_gate": dict(gate),
        "agent_id": agent_id,
        "write_intent_lease_id": write_intent_lease_id,
        "idempotency_key": idempotency_key,
        "allowed_write_scope": [
            f"{workspace_rel}/proposal.candidate.md",
            f"{workspace_rel}/proposal.candidate.json",
            f"{workspace_rel}/patch_proposal.diff",
            f"{workspace_rel}/workspace_receipt.json",
        ],
        "forbidden_actions": [
            "raw_source_write",
            "patch_apply",
            "accepted_state_claim",
            "production_or_live_execution",
            "secrets_access",
            "git_push",
            "delete_or_move_source",
            "write_outside_workspace_path",
        ],
        "required_fan_in": [
            "active_root_proof",
            "context_reads_with_sha256_or_excerpt",
            "touched_paths_limited_to_workspace",
            "proposal_summary",
            "risk_and_validation_recommendations",
            "nonclaim_authority_block",
        ],
        "authority": _authority_block(),
        "actual_spawn_performed": False,
        "codex_queue_run_started": False,
        "worker_start_allowed": False,
        "accepted_state_claimed": False,
        "product_state_accepted": False,
    }
    _write_json(workspace_json, payload)
    _write_text_if_missing(lane_workspace / "README.md", _workspace_readme(row, workspace_rel))
    if row.get("proposal_file_write_allowed"):
        _write_text_if_missing(lane_workspace / "proposal.candidate.md", _proposal_stub(row))
        _write_json_if_missing(
            lane_workspace / "proposal.candidate.json",
            {
                "schema_id": "ion.domain_weaver.proposal_artifact.v0_1_candidate",
                "status": "stub_waiting_for_worker",
                "lane_id": lane_id,
                "objective": row.get("objective"),
                "proposal_summary": "",
                "changed_source_paths_proposed": [],
                "validation_recommendations": [],
                "authority": _authority_block(),
            },
        )
    if row.get("patch_proposal_file_allowed"):
        _write_text_if_missing(
            lane_workspace / "patch_proposal.diff",
            "# Unapplied patch proposal only. Do not apply without lead review.\n",
        )
    receipt = {
        "schema_id": PROPOSAL_WORKSPACE_RECEIPT_SCHEMA_ID,
        "status": "proposal_workspace_receipt",
        "created_at": _utc_now(),
        "workspace_path": workspace_rel,
        "lane_id": lane_id,
        "tier": row.get("tier"),
        "workspace_json_sha256": _sha256_file(workspace_json),
        "idempotent_replay": idempotent_replay,
        "authority": _authority_block(),
        "actual_spawn_performed": False,
        "codex_queue_run_started": False,
        "accepted_state_claimed": False,
        "product_state_accepted": False,
    }
    _write_json(lane_workspace / "workspace_receipt.json", receipt)
    return {
        "lane_id": lane_id,
        "tier": row.get("tier"),
        "workspace_path": workspace_rel,
        "workspace_json_path": _relative_posix(root, workspace_json),
        "receipt_path": _relative_posix(root, lane_workspace / "workspace_receipt.json"),
        "idempotent_replay": idempotent_replay,
        "raw_source_write_allowed": False,
        "patch_apply_allowed": False,
        "accepted_state_claimed": False,
    }


def _workspace_readme(row: Mapping[str, Any], workspace_rel: str) -> str:
    return "\n".join(
        [
            f"# {row.get('title')}",
            "",
            f"- lane_id: `{row.get('lane_id')}`",
            f"- tier: `{row.get('tier')}`",
            f"- workspace: `{workspace_rel}`",
            "- allowed: write proposal artifacts in this workspace only",
            "- forbidden: raw source writes, patch apply, accepted-state claims, production/live execution, secrets, git push",
            "",
            "## Objective",
            str(row.get("objective") or ""),
            "",
        ]
    )


def _proposal_stub(row: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            f"# {row.get('title')} Proposal",
            "",
            "## Context Proof",
            "- active root: pending",
            "",
            "## Proposal",
            "pending",
            "",
            "## Candidate Source Changes",
            "- none proposed yet",
            "",
            "## Validation",
            "- pending",
            "",
            "## Risks",
            "- pending",
            "",
            "## Nonclaims",
            "- candidate proposal only",
            "- not accepted state",
            "- no production/live/secrets authority",
            "",
        ]
    )


def _context_reads(lane: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = [
        {"kind": "file", "path": "ION/05_context/current/domain_weaver/AGENTS.md", "required": True},
        {"kind": "file", "path": "ION/05_context/current/domain_weaver/.ion/ION_CONTEXT_CAPSULE.yaml", "required": True},
        {"kind": "file", "path": "ION/05_context/current/domain_weaver/queue_governance/DOMAIN_WEAVER_EXACT_SPAWN_DISPATCH_FINAL_SETTLEMENT.latest.md", "required": False},
        {"kind": "file", "path": "ION/04_packages/kernel/ion_domain_weaver_pressure_wave.py", "required": True},
        {"kind": "file", "path": "ION/04_packages/kernel/ion_domain_weaver_spawn_request_dispatcher.py", "required": True},
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
        if path in seen:
            continue
        seen.add(path)
        deduped.append(row)
    return deduped[:64]


def _plan_blockers(
    lanes: list[Mapping[str, Any]],
    *,
    native_slot_cap: int,
    proposal_workspace_cap: int,
) -> list[str]:
    blockers: list[str] = []
    if native_slot_cap <= 0:
        blockers.append("native_slot_cap_zero")
    if len(lanes) > proposal_workspace_cap:
        blockers.append("lane_count_above_proposal_workspace_cap")
    for row in lanes:
        for blocker in row.get("blockers") or []:
            blockers.append(f"{row.get('lane_id')}:{blocker}")
        if row.get("raw_source_write_allowed"):
            blockers.append(f"{row.get('lane_id')}:raw_source_write_allowed")
        if row.get("patch_apply_allowed"):
            blockers.append(f"{row.get('lane_id')}:patch_apply_allowed")
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
        if confirmation != PROPOSAL_WRITE_CONFIRMATION:
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
        "confirmation_required": PROPOSAL_WRITE_CONFIRMATION,
        "idempotency_key_present": bool(_clean_text(idempotency_key)),
        "agent_id_present": bool(_clean_text(agent_id)),
        "write_intent_lease_id_present": bool(_clean_text(write_intent_lease_id)),
        "blockers": blockers,
    }


def _hard_stop_conditions() -> list[str]:
    return [
        "any_worker_writes_outside_assigned_proposal_workspace",
        "any_worker_applies_patch_or_edits_source_without_lead_apply_gate",
        "any_lane_claims_accepted_state_product_state_or_materialization_ready",
        "any_lane_claims_recursive_child_spawn_without_current_spawn_primitive_proof",
        "any_usage_limit_prompt_through_claims_success_without_valid_task_return",
        "any_queue_row_dispatch_counts_blocked_connector_receipt_as_enqueued",
        "nemesis_review_missing_before_escalating_from_proposal_to_apply",
    ]


def _authority_block() -> dict[str, Any]:
    return {
        "candidate_only": True,
        "carrier_intake_only": True,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "materialization_authority": False,
        "raw_source_write_authority": False,
        "patch_apply_authority": False,
    }


def _proposal_root(root: Path, proposal_root: str | Path) -> Path:
    rel = Path(proposal_root)
    if rel.is_absolute():
        candidate = rel.resolve(strict=False)
    else:
        candidate = (root / rel).resolve(strict=False)
    default = (root / DEFAULT_PROPOSAL_ROOT).resolve(strict=False)
    try:
        candidate.relative_to(default)
    except ValueError:
        raise ValueError("proposal_root_must_stay_under_domain_weaver_proposal_wave")
    return candidate


def _assert_under_proposal_root(
    root: Path,
    path: Path,
    *,
    proposal_root: str | Path,
) -> None:
    proposal_root_path = _proposal_root(root, proposal_root)
    try:
        path.resolve(strict=False).relative_to(proposal_root_path)
    except ValueError:
        raise ValueError("path_outside_proposal_root")


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


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_json_if_missing(path: Path, payload: Mapping[str, Any]) -> None:
    if path.exists():
        return
    _write_json(path, payload)


def _write_text_if_missing(path: Path, text: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative_posix(root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.as_posix()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
