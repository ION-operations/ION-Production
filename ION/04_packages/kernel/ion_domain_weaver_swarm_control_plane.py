"""Domain Weaver swarm control-plane synthesis.

This module builds the next control layer above Domain Weaver's existing
pressure-wave, proposal-wave, queue-dispatch, receipt, and readiness artifacts.
It writes candidate-only planning/proof artifacts. It does not spawn workers,
start Codex queue runs, write accepted state, materialize topology, or claim
production/live authority.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from kernel.ion_domain_weaver_pressure_wave import build_pressure_wave_plan
from kernel.ion_domain_weaver_proposal_wave import build_proposal_wave_plan
from kernel.ion_domain_weaver_queue_governance import (
    shape_domain_weaver_queue_governance_rows,
)
from kernel.ion_domain_weaver_worker_start_readiness import (
    build_domain_weaver_worker_start_backlog_hygiene,
    build_domain_weaver_worker_start_readiness,
)


CONTROL_PLANE_SCHEMA_ID = "ion.domain_weaver.swarm_control_plane.v0_1_candidate"
SWARM_READINESS_SCHEMA_ID = "ion.domain_weaver.swarm_readiness.v0_1_candidate"
WATCH_MATRIX_SCHEMA_ID = "ion.domain_weaver.swarm_watch_matrix.v0_1_candidate"
FLEET_PLAN_SCHEMA_ID = "ion.domain_weaver.swarm_fleet_plan.v0_1_candidate"
CONTEXT_GRAPH_DELTA_SCHEMA_ID = (
    "ion.domain_weaver.swarm_context_graph_deltas.v0_1_candidate"
)
LIMITED_WATCH_REFRESH_SCHEMA_ID = (
    "ion.domain_weaver.limited_watch_matrix_refresh.v0_1_candidate"
)
LIMITED_WATCH_ALERTS_SCHEMA_ID = (
    "ion.domain_weaver.limited_watch_alerts.v0_1_candidate"
)
GLOBAL_QUEUE_HYGIENE_SCHEMA_ID = (
    "ion.domain_weaver.global_queue_backlog_context_identity_hygiene.v0_1_candidate"
)
GLOBAL_QUEUE_CONTEXT_IDENTITY_DELTA_SCHEMA_ID = (
    "ion.domain_weaver.global_queue_context_identity_deltas.v0_1_candidate"
)
GLOBAL_QUEUE_REPAIR_PREVIEW_SCHEMA_ID = (
    "ion.domain_weaver.global_queue_backlog_identity_repair_preview.v0_1_candidate"
)
GLOBAL_QUEUE_REPAIR_PREVIEW_DELTA_SCHEMA_ID = (
    "ion.domain_weaver.global_queue_identity_repair_preview_deltas.v0_1_candidate"
)
QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_SCHEMA_ID = (
    "ion.domain_weaver.queue_request_metadata_identity_reissue.v0_1_candidate"
)
QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_DELTA_SCHEMA_ID = (
    "ion.domain_weaver.queue_request_metadata_identity_reissue_deltas.v0_1_candidate"
)
QUEUE_METADATA_IDENTITY_ASSIGNMENT_SCHEMA_ID = (
    "ion.domain_weaver.queue_metadata_identity_assignment.v0_1_candidate"
)
QUEUE_METADATA_IDENTITY_ASSIGNMENT_DELTA_SCHEMA_ID = (
    "ion.domain_weaver.queue_metadata_identity_assignment_deltas.v0_1_candidate"
)
STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_SCHEMA_ID = (
    "ion.domain_weaver.stale_non_domain_queue_quarantine_settlement.v0_1_candidate"
)
STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_DELTA_SCHEMA_ID = (
    "ion.domain_weaver.stale_non_domain_queue_quarantine_settlement_deltas.v0_1_candidate"
)
QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_SCHEMA_ID = (
    "ion.domain_weaver.queue_metadata_identity_reissue_apply_review.v0_1_candidate"
)
QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_DELTA_SCHEMA_ID = (
    "ion.domain_weaver.queue_metadata_identity_reissue_apply_review_deltas.v0_1_candidate"
)
QUEUE_METADATA_IDENTITY_REISSUE_APPLY_RESULT_SCHEMA_ID = (
    "ion.domain_weaver.queue_metadata_identity_reissue.apply_result.v0_1"
)
QUEUE_METADATA_SOURCE_SAFETY_REVIEW_SCHEMA_ID = (
    "ion.domain_weaver.queue_metadata_source_safety_review.v0_1_candidate"
)
QUEUE_METADATA_SOURCE_SAFETY_REVIEW_DELTA_SCHEMA_ID = (
    "ion.domain_weaver.queue_metadata_source_safety_review_deltas.v0_1_candidate"
)
CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_SCHEMA_ID = (
    "ion.domain_weaver.context_gate_blocked_request_reissue.v0_1_candidate"
)
CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_DELTA_SCHEMA_ID = (
    "ion.domain_weaver.context_gate_blocked_request_reissue_deltas.v0_1_candidate"
)
EXACT_REISSUE_REQUEST_DISPATCH_READINESS_SCHEMA_ID = (
    "ion.domain_weaver.exact_reissue_request_dispatch_readiness.v0_1_candidate"
)
EXACT_REISSUE_REQUEST_DISPATCH_READINESS_DELTA_SCHEMA_ID = (
    "ion.domain_weaver.exact_reissue_request_dispatch_readiness_deltas.v0_1_candidate"
)
STALE_WAITING_RECONCILIATION_REVIEW_SCHEMA_ID = (
    "ion.domain_weaver.stale_waiting_reconciliation_review.v0_1_candidate"
)
STALE_WAITING_RECONCILIATION_REVIEW_DELTA_SCHEMA_ID = (
    "ion.domain_weaver.stale_waiting_reconciliation_review_deltas.v0_1_candidate"
)
STALE_WAITING_RECONCILIATION_SETTLEMENT_SCHEMA_ID = (
    "ion.domain_weaver.stale_waiting_reconciliation_settlement.v0_2_candidate"
)
STALE_WAITING_RECONCILIATION_SETTLEMENT_DELTA_SCHEMA_ID = (
    "ion.domain_weaver.stale_waiting_reconciliation_settlement_deltas.v0_2_candidate"
)
POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_SCHEMA_ID = (
    "ion.domain_weaver.post_sidecar_global_queue_hygiene.v0_1_candidate"
)
POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_DELTA_SCHEMA_ID = (
    "ion.domain_weaver.post_sidecar_global_queue_hygiene_deltas.v0_1_candidate"
)
GENERATED_MOUNT_CREATION_SCHEMA_ID = (
    "ion.domain_weaver.generated_mount_creation_for_metadata_reissue.v0_1_candidate"
)
GENERATED_MOUNT_CREATION_DELTA_SCHEMA_ID = (
    "ion.domain_weaver.generated_mount_creation_for_metadata_reissue_deltas.v0_1_candidate"
)
WRITE_RESULT_SCHEMA_ID = "ion.domain_weaver.swarm_control_plane.write_result.v0_1"
WATCH_REFRESH_WRITE_RESULT_SCHEMA_ID = (
    "ion.domain_weaver.limited_watch_matrix_refresh.write_result.v0_1"
)
GLOBAL_QUEUE_HYGIENE_WRITE_RESULT_SCHEMA_ID = (
    "ion.domain_weaver.global_queue_backlog_context_identity_hygiene.write_result.v0_1"
)
GLOBAL_QUEUE_REPAIR_PREVIEW_WRITE_RESULT_SCHEMA_ID = (
    "ion.domain_weaver.global_queue_backlog_identity_repair_preview.write_result.v0_1"
)
QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_WRITE_RESULT_SCHEMA_ID = (
    "ion.domain_weaver.queue_request_metadata_identity_reissue.write_result.v0_1"
)
QUEUE_METADATA_IDENTITY_ASSIGNMENT_WRITE_RESULT_SCHEMA_ID = (
    "ion.domain_weaver.queue_metadata_identity_assignment.write_result.v0_1"
)
STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_WRITE_RESULT_SCHEMA_ID = (
    "ion.domain_weaver.stale_non_domain_queue_quarantine_settlement.write_result.v0_1"
)
QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_WRITE_RESULT_SCHEMA_ID = (
    "ion.domain_weaver.queue_metadata_identity_reissue_apply_review.write_result.v0_1"
)
QUEUE_METADATA_SOURCE_SAFETY_REVIEW_WRITE_RESULT_SCHEMA_ID = (
    "ion.domain_weaver.queue_metadata_source_safety_review.write_result.v0_1"
)
CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_WRITE_RESULT_SCHEMA_ID = (
    "ion.domain_weaver.context_gate_blocked_request_reissue.write_result.v0_1"
)
CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_APPLY_RESULT_SCHEMA_ID = (
    "ion.domain_weaver.context_gate_blocked_request_reissue.apply_result.v0_1"
)
EXACT_REISSUE_REQUEST_DISPATCH_READINESS_WRITE_RESULT_SCHEMA_ID = (
    "ion.domain_weaver.exact_reissue_request_dispatch_readiness.write_result.v0_1"
)
STALE_WAITING_RECONCILIATION_REVIEW_WRITE_RESULT_SCHEMA_ID = (
    "ion.domain_weaver.stale_waiting_reconciliation_review.write_result.v0_1"
)
STALE_WAITING_RECONCILIATION_SETTLEMENT_WRITE_RESULT_SCHEMA_ID = (
    "ion.domain_weaver.stale_waiting_reconciliation_settlement.write_result.v0_2"
)
POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_WRITE_RESULT_SCHEMA_ID = (
    "ion.domain_weaver.post_sidecar_global_queue_hygiene.write_result.v0_1"
)
GENERATED_MOUNT_CREATION_WRITE_RESULT_SCHEMA_ID = (
    "ion.domain_weaver.generated_mount_creation_for_metadata_reissue.write_result.v0_1"
)
OPERATOR_RECEIPT_SCHEMA_ID = (
    "ion.domain_weaver.swarm_control_plane.operator_receipt.v0_1_candidate"
)

DEFAULT_CONTEXT_ROOT = Path("ION/05_context/current/domain_weaver")
DEFAULT_OUTPUT_DIR = DEFAULT_CONTEXT_ROOT / "swarm_control_plane"
DEFAULT_CONTROL_PLANE_NAME = "DOMAIN_WEAVER_SWARM_CONTROL_PLANE.latest.md"
DEFAULT_READINESS_NAME = "DOMAIN_WEAVER_SWARM_READINESS.latest.json"
DEFAULT_WATCH_MATRIX_NAME = "DOMAIN_WEAVER_SWARM_WATCH_MATRIX.latest.json"
DEFAULT_FLEET_PLAN_NAME = "DOMAIN_WEAVER_SWARM_FLEET_PLAN.latest.json"
DEFAULT_CONTEXT_DELTAS_NAME = "DOMAIN_WEAVER_SWARM_CONTEXT_GRAPH_DELTAS.latest.candidate.json"
DEFAULT_WATCH_REFRESH_NAME = "DOMAIN_WEAVER_LIMITED_WATCH_MATRIX_REFRESH.latest.json"
DEFAULT_WATCH_REFRESH_REPORT_NAME = "DOMAIN_WEAVER_LIMITED_WATCH_MATRIX_REFRESH.latest.md"
DEFAULT_WATCH_ALERTS_NAME = "DOMAIN_WEAVER_LIMITED_WATCH_ALERTS.latest.candidate.json"
DEFAULT_QUEUE_GOVERNANCE_DIR = DEFAULT_CONTEXT_ROOT / "queue_governance"
DEFAULT_GLOBAL_QUEUE_HYGIENE_NAME = (
    "DOMAIN_WEAVER_GLOBAL_QUEUE_BACKLOG_HYGIENE.latest.json"
)
DEFAULT_GLOBAL_QUEUE_HYGIENE_REPORT_NAME = (
    "DOMAIN_WEAVER_GLOBAL_QUEUE_BACKLOG_HYGIENE.latest.md"
)
DEFAULT_GLOBAL_QUEUE_CONTEXT_IDENTITY_DELTAS_NAME = (
    "DOMAIN_WEAVER_GLOBAL_QUEUE_CONTEXT_IDENTITY_DELTAS.latest.candidate.json"
)
DEFAULT_GLOBAL_QUEUE_REPAIR_PREVIEW_NAME = (
    "DOMAIN_WEAVER_GLOBAL_QUEUE_BACKLOG_IDENTITY_REPAIR_PREVIEW.latest.json"
)
DEFAULT_GLOBAL_QUEUE_REPAIR_PREVIEW_REPORT_NAME = (
    "DOMAIN_WEAVER_GLOBAL_QUEUE_BACKLOG_IDENTITY_REPAIR_PREVIEW.latest.md"
)
DEFAULT_GLOBAL_QUEUE_REPAIR_PREVIEW_DELTAS_NAME = (
    "DOMAIN_WEAVER_GLOBAL_QUEUE_REPAIR_PREVIEW_DELTAS.latest.candidate.json"
)
DEFAULT_QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_NAME = (
    "DOMAIN_WEAVER_QUEUE_REQUEST_METADATA_IDENTITY_REISSUE.latest.json"
)
DEFAULT_QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_REPORT_NAME = (
    "DOMAIN_WEAVER_QUEUE_REQUEST_METADATA_IDENTITY_REISSUE.latest.md"
)
DEFAULT_QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_DELTAS_NAME = (
    "DOMAIN_WEAVER_QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_DELTAS.latest.candidate.json"
)
DEFAULT_QUEUE_METADATA_IDENTITY_ASSIGNMENT_NAME = (
    "DOMAIN_WEAVER_QUEUE_METADATA_IDENTITY_ASSIGNMENT.latest.json"
)
DEFAULT_QUEUE_METADATA_IDENTITY_ASSIGNMENT_REPORT_NAME = (
    "DOMAIN_WEAVER_QUEUE_METADATA_IDENTITY_ASSIGNMENT.latest.md"
)
DEFAULT_QUEUE_METADATA_IDENTITY_ASSIGNMENT_DELTAS_NAME = (
    "DOMAIN_WEAVER_QUEUE_METADATA_IDENTITY_ASSIGNMENT_DELTAS.latest.candidate.json"
)
STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_CONFIRMATION = (
    "ION_STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_CONFIRMED"
)
DEFAULT_STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_NAME = (
    "DOMAIN_WEAVER_STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT.latest.json"
)
DEFAULT_STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_REPORT_NAME = (
    "DOMAIN_WEAVER_STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT.latest.md"
)
DEFAULT_STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_DELTAS_NAME = (
    "DOMAIN_WEAVER_STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_DELTAS.latest.candidate.json"
)
DEFAULT_QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_NAME = (
    "DOMAIN_WEAVER_QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW.latest.json"
)
DEFAULT_QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_REPORT_NAME = (
    "DOMAIN_WEAVER_QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW.latest.md"
)
DEFAULT_QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_DELTAS_NAME = (
    "DOMAIN_WEAVER_QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_DELTAS.latest.candidate.json"
)
DEFAULT_QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_BODY_DIR_NAME = (
    "metadata_identity_reissue_apply_review_bodies"
)
QUEUE_METADATA_IDENTITY_REISSUE_APPLY_CONFIRMATION = (
    "ION_QUEUE_METADATA_IDENTITY_REISSUE_APPLY_CONFIRMED"
)
DEFAULT_QUEUE_METADATA_SOURCE_SAFETY_REVIEW_NAME = (
    "DOMAIN_WEAVER_QUEUE_METADATA_SOURCE_SAFETY_REVIEW.latest.json"
)
DEFAULT_QUEUE_METADATA_SOURCE_SAFETY_REVIEW_REPORT_NAME = (
    "DOMAIN_WEAVER_QUEUE_METADATA_SOURCE_SAFETY_REVIEW.latest.md"
)
DEFAULT_QUEUE_METADATA_SOURCE_SAFETY_REVIEW_DELTAS_NAME = (
    "DOMAIN_WEAVER_QUEUE_METADATA_SOURCE_SAFETY_REVIEW_DELTAS.latest.candidate.json"
)
DEFAULT_CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_NAME = (
    "DOMAIN_WEAVER_CONTEXT_GATE_BLOCKED_REQUEST_REISSUE.latest.json"
)
DEFAULT_CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_REPORT_NAME = (
    "DOMAIN_WEAVER_CONTEXT_GATE_BLOCKED_REQUEST_REISSUE.latest.md"
)
DEFAULT_CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_DELTAS_NAME = (
    "DOMAIN_WEAVER_CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_DELTAS.latest.candidate.json"
)
DEFAULT_CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_BODY_DIR_NAME = (
    "context_gate_blocked_request_reissue_bodies"
)
CONTEXT_GATE_REISSUE_APPLY_CONFIRMATION = "ION_CONTEXT_GATE_REISSUE_APPLY_CONFIRMED"
DEFAULT_EXACT_REISSUE_REQUEST_DISPATCH_READINESS_NAME = (
    "DOMAIN_WEAVER_EXACT_REISSUE_REQUEST_DISPATCH_READINESS.latest.json"
)
DEFAULT_EXACT_REISSUE_REQUEST_DISPATCH_READINESS_REPORT_NAME = (
    "DOMAIN_WEAVER_EXACT_REISSUE_REQUEST_DISPATCH_READINESS.latest.md"
)
DEFAULT_EXACT_REISSUE_REQUEST_DISPATCH_READINESS_DELTAS_NAME = (
    "DOMAIN_WEAVER_EXACT_REISSUE_REQUEST_DISPATCH_READINESS_DELTAS.latest.candidate.json"
)
DEFAULT_STALE_WAITING_RECONCILIATION_REVIEW_NAME = (
    "DOMAIN_WEAVER_STALE_WAITING_RECONCILIATION_REVIEW.latest.json"
)
DEFAULT_STALE_WAITING_RECONCILIATION_REVIEW_REPORT_NAME = (
    "DOMAIN_WEAVER_STALE_WAITING_RECONCILIATION_REVIEW.latest.md"
)
DEFAULT_STALE_WAITING_RECONCILIATION_REVIEW_DELTAS_NAME = (
    "DOMAIN_WEAVER_STALE_WAITING_RECONCILIATION_REVIEW_DELTAS.latest.candidate.json"
)
STALE_WAITING_RECONCILIATION_SETTLEMENT_CONFIRMATION = (
    "ION_STALE_WAITING_RECONCILIATION_SETTLEMENT_CONFIRMED"
)
DEFAULT_STALE_WAITING_RECONCILIATION_SETTLEMENT_NAME = (
    "DOMAIN_WEAVER_STALE_WAITING_RECONCILIATION_SETTLEMENT.latest.json"
)
DEFAULT_STALE_WAITING_RECONCILIATION_SETTLEMENT_REPORT_NAME = (
    "DOMAIN_WEAVER_STALE_WAITING_RECONCILIATION_SETTLEMENT.latest.md"
)
DEFAULT_STALE_WAITING_RECONCILIATION_SETTLEMENT_DELTAS_NAME = (
    "DOMAIN_WEAVER_STALE_WAITING_RECONCILIATION_SETTLEMENT_DELTAS.latest.candidate.json"
)
DEFAULT_POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_NAME = (
    "DOMAIN_WEAVER_POST_SIDECAR_GLOBAL_QUEUE_HYGIENE.latest.json"
)
DEFAULT_POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_REPORT_NAME = (
    "DOMAIN_WEAVER_POST_SIDECAR_GLOBAL_QUEUE_HYGIENE.latest.md"
)
DEFAULT_POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_DELTAS_NAME = (
    "DOMAIN_WEAVER_POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_DELTAS.latest.candidate.json"
)
DEFAULT_GENERATED_MOUNT_CREATION_NAME = (
    "DOMAIN_WEAVER_GENERATED_MOUNT_CREATION_FOR_METADATA_REISSUE.latest.json"
)
DEFAULT_GENERATED_MOUNT_CREATION_REPORT_NAME = (
    "DOMAIN_WEAVER_GENERATED_MOUNT_CREATION_FOR_METADATA_REISSUE.latest.md"
)
DEFAULT_GENERATED_MOUNT_CREATION_DELTAS_NAME = (
    "DOMAIN_WEAVER_GENERATED_MOUNT_CREATION_FOR_METADATA_REISSUE_DELTAS.latest.candidate.json"
)

DOMAIN_CONTEXT_PACKAGE = (
    "ION/05_context/current/domain_weaver/.ion/ACTIVE_CONTEXT_PACKAGE.md"
)
LEAD_DEV_CONTEXT_PACKAGE = (
    "ION/05_context/current/domain_weaver/lead_dev_self_context/"
    "LEAD_DEV_CODEX_OPERATING_PACKAGE.latest.md"
)
PROPOSAL_FANIN_PATH = (
    DEFAULT_CONTEXT_ROOT / "proposal_wave/DOMAIN_WEAVER_PROPOSAL_WRITE_SWARM_FANIN.latest.json"
)
SELF_EVOLUTION_READINESS_PATH = (
    DEFAULT_CONTEXT_ROOT
    / "self_evolution_readiness/DOMAIN_WEAVER_SELF_EVOLUTION_READINESS.latest.json"
)
DOMAIN_CAPSULE_PATH = DEFAULT_CONTEXT_ROOT / ".ion/ION_CONTEXT_CAPSULE.yaml"
PROJECTION_PATH = DEFAULT_CONTEXT_ROOT / "DOMAIN_WEAVER_PROJECTION.json"
PROMOTION_GATE_PATH = DEFAULT_CONTEXT_ROOT / "PROMOTION_GATE.json"
QUEUE_PATH = Path("ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json")
QUEUE_RUNNER_STATE_PATH = Path(
    "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json"
)
CODEX_WORK_REQUESTS_DIR = Path("ION/05_context/current/chatgpt_connector/codex_work_requests")
WORKER_SPAWN_REQUESTS_GLOB = (
    "ION/05_context/current/domain_weaver/workers/*/context/spawn_requests/*.spawn_request.json"
)

AUTHORITY = {
    "candidate_context_only": True,
    "production_authority": False,
    "live_execution_authority": False,
    "accepted_state_authority": False,
    "secrets_authority": False,
    "materialization_authority": False,
    "git_push_authority": False,
    "codex_queue_run_started": False,
    "actual_spawn_performed": False,
}
STALE_LIFECYCLE_PREVIEW_METADATA_STATUS = "STALE_PREVIEW_NOT_CURRENT_ROUTE_IDENTITY"
STALE_LIFECYCLE_PREVIEW_IDENTITY_SCOPE = "historical_source_queue_lifecycle_preview"

NON_CLAIMS = [
    "Swarm control-plane artifacts are candidate planning/proof surfaces, not accepted state.",
    "Worker returns remain carrier intake until lead/Nemesis settlement.",
    "The control plane does not spawn workers, start queue runs, or process the general queue.",
    "The control plane does not grant production, live execution, accepted-state, secrets, materialization, deploy, push, topology, or UI resume authority.",
]


SWARM_COMMAND_LANES: tuple[dict[str, Any], ...] = (
    {
        "lane_id": "root_steward_command",
        "title": "Root Steward Command",
        "role_id": "role.domain_weaver_root_steward",
        "domain_id": "domain.current_phase_orchestration_management",
        "tier": "command",
        "queue_lane_id": "architecture_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-ROOT-STEWARD-COMMAND-V0_1",
        "objective": "Own tranche intent, authority ceiling, lane caps, fan-in timing, and final verdict.",
        "watch_targets": ["swarm_fanin_state", "receipt_gaps", "accepted_state_confusion"],
    },
    {
        "lane_id": "domain_steward_council",
        "title": "Domain Steward Council",
        "role_id": "role.domain_steward_council",
        "domain_id": "domain.domain_ecology",
        "tier": "manager",
        "queue_lane_id": "architecture_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-DOMAIN-STEWARD-COUNCIL-V0_1",
        "objective": "Assign meaningful domains and route packets without flattening role/domain identity.",
        "watch_targets": ["context_graph_deltas", "branch_route_drift", "stale_context"],
    },
    {
        "lane_id": "watch_command_center",
        "title": "Watch Command Center",
        "role_id": "role.domain_weaver_watch_commander",
        "domain_id": "domain.swarm_watch",
        "tier": "manager",
        "queue_lane_id": "audit_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-WATCH-COMMAND-CENTER-V0_1",
        "objective": "Turn stale or blocked evidence into alerts, graph deltas, and next packets.",
        "watch_targets": ["queue_state", "worker_state", "failed_returns", "carrier_failures"],
    },
    {
        "lane_id": "fleet_spawn_lifecycle",
        "title": "Fleet Spawn Lifecycle",
        "role_id": "role.domain_weaver_fleet_lifecycle_steward",
        "domain_id": "domain.domain_weaver_fanout_control",
        "tier": "manager",
        "queue_lane_id": "implementation_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-FLEET-SPAWN-LIFECYCLE-V0_1",
        "objective": "Bind intent, lane metadata, context package, worker-local rows, queue requests, heartbeat, and fan-in.",
        "watch_targets": ["spawn_request_rows", "worker_state", "duplicate_requests"],
    },
    {
        "lane_id": "queue_worker_steward",
        "title": "Queue And Worker Steward",
        "role_id": "role.queue_worker_steward",
        "domain_id": "domain.codex_queue_hygiene",
        "tier": "manager",
        "queue_lane_id": "audit_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-QUEUE-WORKER-STEWARD-V0_1",
        "objective": "Protect exact request starts from dirty global queue state and classify staleness.",
        "watch_targets": ["queue_state", "worker_state", "global_queue_hygiene"],
    },
    {
        "lane_id": "context_graph_cartographer",
        "title": "Context Graph Cartographer",
        "role_id": "role.context_graph_cartographer",
        "domain_id": "domain.context_graph_branch_fabric",
        "tier": "specialist",
        "queue_lane_id": "context_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-CONTEXT-GRAPH-CARTOGRAPHER-V0_1",
        "objective": "Emit evidence-backed candidate graph deltas connecting domains, agents, branches, receipts, blockers, and packets.",
        "watch_targets": ["context_graph_deltas", "stale_context", "semantic_alias_drift"],
    },
    {
        "lane_id": "receipt_proof_librarian",
        "title": "Receipt And Proof Librarian",
        "role_id": "role.receipt_proof_librarian",
        "domain_id": "domain.receipt_proof_graph",
        "tier": "specialist",
        "queue_lane_id": "audit_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-RECEIPT-PROOF-LIBRARIAN-V0_1",
        "objective": "Preserve receipt adjacency and prevent carrier-intake proof from becoming accepted-state proof.",
        "watch_targets": ["receipt_gaps", "failed_returns", "accepted_state_confusion"],
    },
    {
        "lane_id": "comms_autoreaction_auditor",
        "title": "Comms Autoreaction Auditor",
        "role_id": "role.autoreaction_proof_lead",
        "domain_id": "domain.agent_communication_systems",
        "tier": "manager",
        "queue_lane_id": "comms_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-COMMS-AUTOREACTION-AUDITOR-V0_1",
        "objective": "Separate alternate-worker recovery from original automatic reaction proof.",
        "watch_targets": ["unread_comms", "failed_returns", "carrier_failures"],
    },
    {
        "lane_id": "action_gateway_freshness_guard",
        "title": "Action Gateway Freshness Guard",
        "role_id": "role.gateway_route_auditor",
        "domain_id": "domain.action_route_parity",
        "tier": "specialist",
        "queue_lane_id": "audit_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-ACTION-GATEWAY-FRESHNESS-GUARD-V0_1",
        "objective": "Watch route gate matrix, mutation gate coverage, and gateway/dispatcher drift.",
        "watch_targets": ["branch_route_drift", "action_gateway_freshness"],
    },
    {
        "lane_id": "proposal_wave_validator",
        "title": "Proposal Wave Validator",
        "role_id": "role.proposal_wave_validator",
        "domain_id": "domain.proposal_workspace_protocol",
        "tier": "specialist",
        "queue_lane_id": "audit_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-PROPOSAL-WAVE-VALIDATOR-V0_1",
        "objective": "Validate workspace roots, JSON, nonclaims, patch-proposal boundaries, and source-write nonclaims before widening.",
        "watch_targets": ["proposal_wave_state", "receipt_gaps", "accepted_state_confusion"],
    },
    {
        "lane_id": "fanin_synthesizer",
        "title": "Fan-In Synthesizer",
        "role_id": "role.domain_weaver_fanin_synthesizer",
        "domain_id": "domain.swarm_fanin_settlement",
        "tier": "manager",
        "queue_lane_id": "architecture_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-FANIN-SYNTHESIZER-V0_1",
        "objective": "Collect returns, classify blockers, generate next packets, and produce readiness verdicts.",
        "watch_targets": ["swarm_fanin_state", "worker_state", "receipt_gaps"],
    },
    {
        "lane_id": "nemesis_vice_review",
        "title": "Nemesis And Vice Review",
        "role_id": "role.nemesis_pressure_auditor",
        "domain_id": "domain.nemesis_pressure_audit",
        "tier": "nemesis",
        "queue_lane_id": "audit_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-NEMESIS-VICE-REVIEW-V0_1",
        "objective": "Attack false autonomy, queue storms, stale context, fake proof, identity loss, and accepted-state confusion.",
        "watch_targets": ["accepted_state_confusion", "queue_state", "swarm_fanin_state"],
    },
    {
        "lane_id": "operator_truth_surface_adapter",
        "title": "Operator Truth Surface Adapter",
        "role_id": "role.operator_truth_surface_adapter",
        "domain_id": "domain.operator_workbench_truth_surface",
        "tier": "specialist",
        "queue_lane_id": "browser_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-OPERATOR-TRUTH-SURFACE-ADAPTER-V0_1",
        "objective": "Project candidate, queued, running, blocked, fan-in, and accepted-state differences to the operator UI.",
        "watch_targets": ["ui_operator_truth", "context_graph_deltas", "swarm_fanin_state"],
    },
    {
        "lane_id": "escalation_packet_router",
        "title": "Escalation Packet Router",
        "role_id": "role.escalation_packet_router",
        "domain_id": "domain.packet_routing",
        "tier": "manager",
        "queue_lane_id": "approval_governance_lane",
        "packet_id": "PCKT-DOMAIN-WEAVER-ESCALATION-PACKET-ROUTER-V0_1",
        "objective": "Convert alerts and blockers into stop, follow-up, apply-review, or supervised candidate packets.",
        "watch_targets": ["receipt_gaps", "global_queue_hygiene", "materialization_gate"],
    },
)


WATCH_TARGET_DEFS: tuple[dict[str, Any], ...] = (
    {
        "target_id": "queue_state",
        "title": "Connector Codex Work Queue",
        "watcher_role_id": "role.queue_worker_steward",
        "watcher_domain_id": "domain.codex_queue_hygiene",
        "evidence": [QUEUE_PATH.as_posix(), QUEUE_RUNNER_STATE_PATH.as_posix()],
        "trigger": "queued_or_running_rows_stale_duplicate_or_missing_identity",
        "response_packet": "PCKT-DOMAIN-WEAVER-GLOBAL-QUEUE-BACKLOG-CONTEXT-IDENTITY-HYGIENE-V0_1",
    },
    {
        "target_id": "worker_state",
        "title": "Worker Context Lanes And Runtime State",
        "watcher_role_id": "role.domain_weaver_fleet_lifecycle_steward",
        "watcher_domain_id": "domain.domain_weaver_fanout_control",
        "evidence": [
            "ION/05_context/current/domain_weaver/workers",
            "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json",
        ],
        "trigger": "worker_row_missing_heartbeat_stale_or_unsettled_return",
        "response_packet": "PCKT-DOMAIN-WEAVER-WORKER-LIFECYCLE-HEARTBEAT-V0_1",
    },
    {
        "target_id": "spawn_request_rows",
        "title": "Worker-Local Spawn Request Rows",
        "watcher_role_id": "role.domain_weaver_fleet_lifecycle_steward",
        "watcher_domain_id": "domain.spawn_dispatch_guardrails",
        "evidence": [
            "ION/05_context/current/domain_weaver/workers/*/context/spawn_requests/*.spawn_request.json",
            "ION/05_context/current/domain_weaver/spawn_dispatch",
        ],
        "trigger": "requested_rows_unvalidated_rejected_or_enqueue_blocked",
        "response_packet": "PCKT-DOMAIN-WEAVER-SPAWN-REQUEST-VALIDATION-FANIN-V0_1",
    },
    {
        "target_id": "failed_returns",
        "title": "Task Return Failures And Blocked Intake",
        "watcher_role_id": "role.receipt_proof_librarian",
        "watcher_domain_id": "domain.receipt_proof_graph",
        "evidence": [
            "ION/05_context/current/chatgpt_connector/task_returns",
            "ION/05_context/current/chatgpt_connector/task_return_machine_receipts",
        ],
        "trigger": "return_rejected_blocked_or_lacks_context_template_proof",
        "response_packet": "PCKT-DOMAIN-WEAVER-TASK-RETURN-PROOF-REPAIR-V0_1",
    },
    {
        "target_id": "stale_context",
        "title": "Folder-Local Context Freshness",
        "watcher_role_id": "role.context_capsule_curator",
        "watcher_domain_id": "domain.context_mount_quality",
        "evidence": [
            DOMAIN_CAPSULE_PATH.as_posix(),
            LEAD_DEV_CONTEXT_PACKAGE,
            "ION/05_context/current/codex_agent_mounts",
        ],
        "trigger": "context_last_refreshed_before_latest_receipt_or_shared_capsule_identity",
        "response_packet": "PCKT-DOMAIN-WEAVER-CONTEXT-MOUNT-FRESHNESS-REBASELINE-V0_1",
    },
    {
        "target_id": "unread_comms",
        "title": "Agent Comms Threads And Signals",
        "watcher_role_id": "role.autoreaction_proof_lead",
        "watcher_domain_id": "domain.agent_communication_systems",
        "evidence": [
            "ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json",
            "ION/05_context/current/agent_comms/threads",
        ],
        "trigger": "unread_signal_unsettled_directive_or_no_synced_reply_after_return",
        "response_packet": "PCKT-DOMAIN-WEAVER-COMMS-AUTOREACTION-PROOF-V0_2-ORIGINAL-WORKER-BOUND",
    },
    {
        "target_id": "branch_route_drift",
        "title": "Branch Route And Mutation Gate Drift",
        "watcher_role_id": "role.gateway_route_auditor",
        "watcher_domain_id": "domain.action_route_parity",
        "evidence": [
            "ION/05_context/current/domain_weaver/route_policy/DOMAIN_WEAVER_ACTION_ROUTE_GATE_MATRIX.latest.json",
            "ION/03_registry/ion_action_mcp_branch_leader_registry.yaml",
        ],
        "trigger": "declared_route_gap_mutation_gate_gap_or_handler_write_contract_drift",
        "response_packet": "PCKT-DOMAIN-WEAVER-ACTION-ROUTE-PARITY-GUARD-V0_1",
    },
    {
        "target_id": "action_gateway_freshness",
        "title": "Action Gateway Freshness",
        "watcher_role_id": "role.gateway_route_auditor",
        "watcher_domain_id": "domain.ion_gpt_action_gateway",
        "evidence": [
            "ION/04_packages/kernel/ion_custom_gpt_action_gateway.py",
            "ION/05_context/current/domain_weaver/route_policy/DOMAIN_WEAVER_ACTION_ROUTE_GATE_MATRIX.latest.json",
        ],
        "trigger": "gateway_schema_or_dispatch_catalog_stale_against_route_matrix",
        "response_packet": "PCKT-DOMAIN-WEAVER-ACTION-GATEWAY-FRESHNESS-REVIEW-V0_1",
    },
    {
        "target_id": "receipt_gaps",
        "title": "Receipt And Proof Gaps",
        "watcher_role_id": "role.receipt_proof_librarian",
        "watcher_domain_id": "domain.receipt_proof_graph",
        "evidence": [
            "ION/05_context/current/domain_weaver/operator_actions",
            "ION/05_context/current/codex_cli/hooks/runtime",
        ],
        "trigger": "material_artifact_without_operator_receipt_or_missing_sessionstart_receipt",
        "response_packet": "PCKT-SESSIONSTART-CANDIDATE-RECEIPT-LANE-V0_1",
    },
    {
        "target_id": "context_graph_deltas",
        "title": "Context Graph Delta Production",
        "watcher_role_id": "role.context_graph_cartographer",
        "watcher_domain_id": "domain.context_graph_branch_fabric",
        "evidence": [
            "ION/05_context/current/domain_weaver/self_evolution_readiness/DOMAIN_WEAVER_SELF_EVOLUTION_CONTEXT_GRAPH_DELTAS.latest.candidate.json",
            "ION/05_context/current/domain_weaver/projection_refresh/DOMAIN_WEAVER_CONTEXT_GRAPH_DELTAS_PROJECTION_REFRESH.latest.candidate.json",
        ],
        "trigger": "meaningful_new_receipt_or_blocker_without_graph_edge",
        "response_packet": "PCKT-DOMAIN-WEAVER-CONTEXT-GRAPH-DELTA-FANIN-V0_1",
    },
    {
        "target_id": "duplicate_requests",
        "title": "Duplicate Or Conflicting Requests",
        "watcher_role_id": "role.queue_worker_steward",
        "watcher_domain_id": "domain.codex_queue_hygiene",
        "evidence": [
            "ION/05_context/current/chatgpt_connector/codex_work_requests",
            "ION/05_context/current/domain_weaver/spawn_dispatch",
        ],
        "trigger": "same_packet_context_lane_or_idempotency_key_reappears_without_settlement",
        "response_packet": "PCKT-DOMAIN-WEAVER-DUPLICATE-REQUEST-QUARANTINE-V0_1",
    },
    {
        "target_id": "carrier_failures",
        "title": "Codex Carrier Failures",
        "watcher_role_id": "role.codex_carrier_steward",
        "watcher_domain_id": "domain.codex_carrier_sync",
        "evidence": [
            "ION/05_context/current/chatgpt_connector/codex_queue_runs",
            "ION/04_packages/kernel/ion_codex_queue_runner.py",
        ],
        "trigger": "usage_limit_false_success_resume_failure_or_missing_task_return",
        "response_packet": "PCKT-ION-CODEX-CARRIER-RELIABILITY-PROMPT-THROUGH-V0_2",
    },
    {
        "target_id": "proposal_wave_state",
        "title": "Proposal Wave Returns",
        "watcher_role_id": "role.proposal_wave_validator",
        "watcher_domain_id": "domain.proposal_workspace_protocol",
        "evidence": [
            PROPOSAL_FANIN_PATH.as_posix(),
            "ION/05_context/current/domain_weaver/proposal_wave",
        ],
        "trigger": "proposal_json_invalid_patch_proposal_unbounded_or_source_write_claim",
        "response_packet": "PCKT-DOMAIN-WEAVER-PROPOSAL-WAVE-SCHEMA-PATH-NONCLAIM-VALIDATOR-V0_1",
    },
    {
        "target_id": "swarm_fanin_state",
        "title": "Swarm Fan-In State",
        "watcher_role_id": "role.domain_weaver_fanin_synthesizer",
        "watcher_domain_id": "domain.swarm_fanin_settlement",
        "evidence": [
            "ION/05_context/current/domain_weaver/acceleration",
            DEFAULT_OUTPUT_DIR.as_posix(),
        ],
        "trigger": "fanout_started_without_fanin_or_return_settlement_missing",
        "response_packet": "PCKT-DOMAIN-WEAVER-SWARM-FANIN-SYNTHESIS-V0_1",
    },
    {
        "target_id": "accepted_state_confusion",
        "title": "Accepted-State Claim Boundary",
        "watcher_role_id": "role.nemesis_pressure_auditor",
        "watcher_domain_id": "domain.nemesis_pressure_audit",
        "evidence": [
            PROJECTION_PATH.as_posix(),
            PROMOTION_GATE_PATH.as_posix(),
            "ION/05_context/current/domain_weaver/projection_refresh",
        ],
        "trigger": "candidate_receipt_or_carrier_intake_described_as_accepted_state",
        "response_packet": "PCKT-DOMAIN-WEAVER-NEMESIS-ACCEPTED-STATE-BOUNDARY-V0_1",
    },
    {
        "target_id": "global_queue_hygiene",
        "title": "Global Queue Hygiene",
        "watcher_role_id": "role.queue_hygiene_steward",
        "watcher_domain_id": "domain.codex_queue_hygiene",
        "evidence": [
            "ION/05_context/current/domain_weaver/acceleration/DW_SPW_006_QUEUE_BACKLOG_HYGIENE.latest.json",
            QUEUE_PATH.as_posix(),
        ],
        "trigger": "general_queue_processing_requested_while_backlog_or_identity_hazards_remain",
        "response_packet": "PCKT-DOMAIN-WEAVER-GLOBAL-QUEUE-BACKLOG-CONTEXT-IDENTITY-HYGIENE-V0_1",
    },
    {
        "target_id": "materialization_gate",
        "title": "Materialization Gate",
        "watcher_role_id": "role.materialization_gate_auditor",
        "watcher_domain_id": "domain.materialization_readiness",
        "evidence": [
            "ION/05_context/current/domain_weaver/materialization_readiness/MATERIALIZATION_READINESS_REMAINING_GATES_M2_20260604T124130Z.candidate.json",
            DOMAIN_CAPSULE_PATH.as_posix(),
        ],
        "trigger": "materialization_ready_claim_while_capsule_or_gate_false",
        "response_packet": "PCKT-DOMAIN-WEAVER-MATERIALIZATION-READINESS-SETTLEMENT-V0_2",
    },
    {
        "target_id": "ui_operator_truth",
        "title": "Operator UI Truth Surface",
        "watcher_role_id": "role.operator_truth_surface_adapter",
        "watcher_domain_id": "domain.operator_workbench_truth_surface",
        "evidence": [
            "ION/05_context/current/domain_weaver/proposal_wave/dw_proposal_write_swarm_20260604t164205z/ui_operator_evidence_packet_templates/proposal.candidate.json",
            PROJECTION_PATH.as_posix(),
        ],
        "trigger": "ui_shows_context_or_swarm_state_without_candidate_vs_accepted_boundary",
        "response_packet": "PCKT-LEAD-DEV-OPERATOR-DASHBOARD-EVIDENCE-V0_1",
    },
    {
        "target_id": "semantic_alias_drift",
        "title": "Semantic Alias Drift",
        "watcher_role_id": "role.semantic_alias_gatekeeper",
        "watcher_domain_id": "domain.semantic_alias_canonicalization",
        "evidence": [
            "ION/05_context/current/domain_weaver/semantic_alias_canonicalization/DOMAIN_WEAVER_SEMANTIC_ALIAS_ACCEPTED_PROJECTION_REVIEW.latest.candidate.json",
            "ION/05_context/current/domain_weaver/semantic_alias_canonicalization/DOMAIN_WEAVER_SEMANTIC_ALIAS_CANONICALIZATION.latest.candidate.json",
        ],
        "trigger": "candidate_alias_resolves_but_accepted_projection_or_mount_manifest_not_refreshed",
        "response_packet": "PCKT-DOMAIN-WEAVER-SEMANTIC-ALIAS-SUPERVISED-APPLY-GATE-V0_1",
    },
)


def build_swarm_control_plane(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    root_proof = _active_root_proof(root)
    watch_matrix = build_swarm_watch_matrix(root, generated_at=generated)
    fleet_plan = build_swarm_fleet_plan(root, generated_at=generated)
    proposal_validation = validate_current_proposal_wave(root)
    context_graph_deltas = build_swarm_context_graph_deltas(
        root,
        generated_at=generated,
        watch_matrix=watch_matrix,
        fleet_plan=fleet_plan,
        proposal_validation=proposal_validation,
    )
    readiness = build_swarm_readiness(
        root,
        generated_at=generated,
        root_proof=root_proof,
        watch_matrix=watch_matrix,
        fleet_plan=fleet_plan,
        proposal_validation=proposal_validation,
        context_graph_deltas=context_graph_deltas,
    )
    return {
        "schema_id": CONTROL_PLANE_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "context_root": DEFAULT_CONTEXT_ROOT.as_posix(),
        "root_proof": root_proof,
        "authority": AUTHORITY,
        "verdict": readiness["verdict"],
        "command_structure": build_command_structure(),
        "control_plane_capabilities": {
            "watch_matrix_built": True,
            "fleet_plan_built": True,
            "candidate_context_graph_deltas_built": True,
            "proposal_wave_validator_available": proposal_validation["validator_available"],
            "pressure_wave_preview_integrated": True,
            "proposal_wave_preview_integrated": True,
            "actual_spawn_performed": False,
            "codex_queue_run_started": False,
            "accepted_state_moved": False,
        },
        "watch_matrix": watch_matrix,
        "fleet_plan": fleet_plan,
        "proposal_wave_validation": proposal_validation,
        "candidate_context_graph_deltas": context_graph_deltas,
        "readiness": readiness,
        "nemesis_dissent": readiness["nemesis_dissent"],
        "next_packets": readiness["next_packets"],
        "non_claims": NON_CLAIMS,
    }


def build_swarm_watch_matrix(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    targets: list[dict[str, Any]] = []
    for row in WATCH_TARGET_DEFS:
        evidence_refs = [_evidence_ref(root, value) for value in row["evidence"]]
        missing_required = [
            ref["path"] for ref in evidence_refs if ref.get("required") and not ref.get("exists")
        ]
        targets.append(
            {
                "target_id": row["target_id"],
                "title": row["title"],
                "watcher_role_id": row["watcher_role_id"],
                "watcher_domain_id": row["watcher_domain_id"],
                "evidence_refs": evidence_refs,
                "trigger": row["trigger"],
                "response_packet": row["response_packet"],
                "candidate_graph_delta_id": f"domain_weaver.watch.{row['target_id']}",
                "status": "watch_ready" if not missing_required else "watch_has_missing_evidence",
                "missing_required_evidence": missing_required,
                "state_movement_allowed": False,
            }
        )
    coverage = {
        "target_count": len(targets),
        "ready_target_count": sum(1 for row in targets if row["status"] == "watch_ready"),
        "missing_evidence_target_count": sum(
            1 for row in targets if row["status"] == "watch_has_missing_evidence"
        ),
        "response_packet_count": len({row["response_packet"] for row in targets}),
    }
    return {
        "schema_id": WATCH_MATRIX_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "swarm_watch_matrix_built",
        "coverage": coverage,
        "targets": targets,
        "authority": AUTHORITY,
        "actual_watch_daemon_started": False,
        "worker_start_allowed": False,
        "accepted_state_claimed": False,
    }


def build_swarm_fleet_plan(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    lanes = [_fleet_lane(row) for row in SWARM_COMMAND_LANES]
    pressure_preview = _compact_pressure_plan(build_pressure_wave_plan(root))
    proposal_preview = _compact_proposal_plan(build_proposal_wave_plan(root))
    return {
        "schema_id": FLEET_PLAN_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "swarm_fleet_plan_built",
        "lane_count": len(lanes),
        "lanes": lanes,
        "lifecycle": {
            "intent_to_plan": "root_steward_command selects bounded wave objective and authority ceiling",
            "plan_to_rows": "fleet_spawn_lifecycle emits worker-local spawn request rows with role/domain/context binding",
            "rows_to_queue": "spawn_dispatch validates rows and may enqueue QUEUED_FOR_CODEX_CARRIER requests without starting workers",
            "queue_to_worker": "exact request-path queue runner starts only selected rows under explicit gate",
            "worker_to_fanin": "worker returns are carrier intake until receipt/proof and fan-in settlement",
            "fanin_to_next_packet": "fanin_synthesizer classifies blockers and emits next packet groups",
        },
        "caps": {
            "native_slot_cap": 6,
            "default_foreground_lane_cap": 3,
            "proposal_workspace_cap": 18,
            "recursive_child_spawn_cap": 0,
            "exact_queue_start_cap": 2,
            "general_queue_processing_allowed": False,
            "raw_source_write_allowed_for_workers": False,
            "patch_apply_allowed_for_workers": False,
        },
        "pressure_wave_preview": pressure_preview,
        "proposal_wave_preview": proposal_preview,
        "dedupe_conflict_checks": [
            "same lane_id cannot have more than one active unsatisfied queue request without explicit replay key",
            "same worker-local spawn request path cannot enqueue more than one non-idempotent packet",
            "same patch target cannot be assigned to multiple source-apply candidates without a lead apply-review merge plan",
            "same domain/context capsule cannot be treated as both shared fallback and unique worker capsule",
        ],
        "hard_stop_conditions": [
            "root_proof_missing",
            "context_package_missing_or_shared_codex_solo_claimed_as_working_capsule",
            "worker_return_claims_accepted_state",
            "general_queue_processing_requested_while_backlog_hygiene_not_clean",
            "fanout_wave_started_without_fanin_owner",
            "proposal_wave_validator_fails",
            "nemesis_stop_condition_raised",
        ],
        "authority": AUTHORITY,
        "actual_spawn_performed": False,
        "codex_queue_run_started": False,
        "accepted_state_claimed": False,
    }


def build_swarm_context_graph_deltas(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
    watch_matrix: Mapping[str, Any] | None = None,
    fleet_plan: Mapping[str, Any] | None = None,
    proposal_validation: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    watch = watch_matrix or build_swarm_watch_matrix(root, generated_at=generated)
    fleet = fleet_plan or build_swarm_fleet_plan(root, generated_at=generated)
    proposal = proposal_validation or validate_current_proposal_wave(root)
    upsert_claims: list[dict[str, Any]] = [
        {
            "id": "domain_weaver.swarm_control_plane",
            "kind": "control_plane",
            "state": "candidate_control_plane_built",
            "evidence": [DEFAULT_OUTPUT_DIR.as_posix()],
            "value": {
                "watch_target_count": watch["coverage"]["target_count"],
                "fleet_lane_count": fleet["lane_count"],
                "proposal_wave_validation_ok": proposal["ok"],
            },
        },
        {
            "id": "domain_weaver.lead_dev_context_mount",
            "kind": "context_mount",
            "state": "candidate_folder_local_mount_ready_for_hook_smoke",
            "evidence": [
                "ION/05_context/current/lead_dev_context_mounts/domain_weaver_lead_dev/.ion/ION_CONTEXT_CAPSULE.yaml",
                LEAD_DEV_CONTEXT_PACKAGE,
            ],
            "value": {
                "working_capsule_source": "folder_local_ion_context_capsule",
                "shared_codex_solo_is_working_capsule": False,
            },
        },
        {
            "id": "domain_weaver.proposal_wave.validator",
            "kind": "validator",
            "state": "candidate_validator_evaluated",
            "evidence": [PROPOSAL_FANIN_PATH.as_posix()],
            "value": {
                "ok": proposal["ok"],
                "lane_count": proposal["lane_count"],
                "blocker_count": len(proposal["blockers"]),
            },
        },
    ]
    upsert_claims.extend(
        {
            "id": f"domain_weaver.swarm_watch.{row['target_id']}",
            "kind": "watch_target",
            "state": row["status"],
            "evidence": [ref["path"] for ref in row["evidence_refs"] if ref.get("exists")],
            "value": {
                "watcher_role_id": row["watcher_role_id"],
                "watcher_domain_id": row["watcher_domain_id"],
                "trigger": row["trigger"],
                "response_packet": row["response_packet"],
            },
        }
        for row in watch["targets"]
    )
    edges: list[dict[str, Any]] = []
    for lane in fleet["lanes"]:
        edges.append(
            {
                "from": f"role.{lane['lane_id']}",
                "to": lane["domain_id"],
                "kind": "stewards_or_audits_domain",
                "evidence": [lane["context_package"]],
            }
        )
        for target_id in lane["watch_targets"]:
            edges.append(
                {
                    "from": f"role.{lane['lane_id']}",
                    "to": f"domain_weaver.swarm_watch.{target_id}",
                    "kind": "watches",
                    "evidence": [DEFAULT_WATCH_MATRIX_NAME],
                }
            )
    return {
        "schema_id": CONTEXT_GRAPH_DELTA_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "candidate_context_graph_deltas_built",
        "upsert_claims": upsert_claims,
        "edges": edges,
        "write_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def build_swarm_readiness(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
    root_proof: Mapping[str, Any] | None = None,
    watch_matrix: Mapping[str, Any] | None = None,
    fleet_plan: Mapping[str, Any] | None = None,
    proposal_validation: Mapping[str, Any] | None = None,
    context_graph_deltas: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    proof = dict(root_proof or _active_root_proof(root))
    watch = watch_matrix or build_swarm_watch_matrix(root, generated_at=generated)
    fleet = fleet_plan or build_swarm_fleet_plan(root, generated_at=generated)
    proposal = proposal_validation or validate_current_proposal_wave(root)
    graph = context_graph_deltas or build_swarm_context_graph_deltas(
        root,
        generated_at=generated,
        watch_matrix=watch,
        fleet_plan=fleet,
        proposal_validation=proposal,
    )
    self_readiness = _read_json(root / SELF_EVOLUTION_READINESS_PATH)
    self_blockers = _self_readiness_blockers(self_readiness)
    blockers = _swarm_blockers(proof, watch, fleet, proposal, self_blockers)
    verdict = _swarm_verdict(proof, watch, fleet, proposal, blockers)
    already_proven = [
        "active_root_local_mount_ready",
        "folder_local_domain_weaver_context_exists",
        "larger_fanout_candidate_gate_exists",
        "pressure_wave_planning_can_exceed_native_slots_without_spawning",
        "proposal_wave_can_box_worker_writes_without_source_authority",
        "spawn_dispatch_can_validate_worker_local_rows_and_enqueue_without_starting_workers",
        "alternate_worker_recovery_chain_is_proven_as_carrier_intake_not_product_state",
    ]
    newly_advanced = [
        "next_generation_swarm_command_structure_defined",
        "watch_matrix_defined_with_response_packets_and_graph_delta_ids",
        "fleet_plan_defined_with_lifecycle_from_intent_to_fanin",
        "proposal_wave_validator_evaluated_from_current_fanin",
        "candidate_context_graph_deltas_emitted_for swarm roles watch targets and blockers",
        "readiness verdict now separates limited watch/fanout from serious supervised self-evolution",
    ]
    can_run_during_supervised = [
        "bounded watch-matrix refreshes",
        "proposal workspace waves after validator remains green",
        "worker-local spawn row previews",
        "exact-request queue starts for prevalidated rows only",
        "Nemesis review of fan-in and proposal returns",
    ]
    still_blocked = [row["code"] for row in blockers if row["severity"] in {"critical", "high"}]
    return {
        "schema_id": SWARM_READINESS_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "swarm_readiness_built",
        "verdict": verdict,
        "root_proof": proof,
        "authority": AUTHORITY,
        "already_proven": already_proven,
        "newly_advanced_in_this_tranche": newly_advanced,
        "ready_for_supervised_candidate_wave": verdict
        == "READY_FOR_SUPERVISED_SELF_EVOLUTION_CANDIDATE_WAVE",
        "ready_for_limited_watch_and_fanout": verdict
        in {
            "READY_FOR_LIMITED_SWARM_WATCH_AND_FANOUT",
            "READY_FOR_SUPERVISED_SELF_EVOLUTION_CANDIDATE_WAVE",
        },
        "still_blocked": still_blocked,
        "blockers_ranked": blockers,
        "watch_coverage": watch["coverage"],
        "fleet_lane_count": fleet["lane_count"],
        "proposal_wave_validation": proposal,
        "context_graph_delta_claim_count": len(graph["upsert_claims"]),
        "can_run_during_supervised_self_evolution": can_run_during_supervised,
        "later_hardening": [
            "domain-weaver-lead-dev native Codex skill",
            "SessionStart candidate receipt lane",
            "domain-owned watch daemon runner after proof gates",
            "operator UI context drawer and swarm truth-surface adapter",
            "recursive native child-spawn one-child probe if tool surface changes",
        ],
        "next_packets": next_packets(verdict, blockers),
        "nemesis_dissent": nemesis_dissent(verdict, blockers),
        "source_evidence": source_evidence(root),
        "non_claims": NON_CLAIMS,
    }


def validate_current_proposal_wave(active_root: str | Path) -> dict[str, Any]:
    root = _require_active_root(active_root)
    fanin_path = root / PROPOSAL_FANIN_PATH
    fanin = _read_json(fanin_path)
    blockers: list[dict[str, Any]] = []
    lane_results: list[dict[str, Any]] = []
    if not fanin:
        return {
            "schema_id": "ion.domain_weaver.proposal_wave_validation.v0_1_candidate",
            "validator_available": True,
            "ok": False,
            "status": "proposal_fanin_missing",
            "fanin_path": PROPOSAL_FANIN_PATH.as_posix(),
            "lane_count": 0,
            "lane_results": [],
            "blockers": [
                {
                    "code": "PROPOSAL_FANIN_MISSING",
                    "severity": "high",
                    "detail": "Current proposal wave fan-in JSON is missing or invalid.",
                }
            ],
        }
    for lane in fanin.get("lanes") or []:
        if not isinstance(lane, Mapping):
            continue
        lane_id = str(lane.get("lane_id") or "unknown")
        files = lane.get("files") if isinstance(lane.get("files"), Mapping) else {}
        lane_blockers: list[str] = []
        workspace_ref = _file_payload_ref(root, files.get("workspace"))
        proposal_json_ref = _file_payload_ref(root, files.get("proposal_json"))
        proposal_md_ref = _file_payload_ref(root, files.get("proposal_md"))
        patch_ref = _file_payload_ref(root, files.get("patch_proposal"), required=False)

        for ref in (workspace_ref, proposal_json_ref, proposal_md_ref, patch_ref):
            if ref["required"] and not ref["exists"]:
                lane_blockers.append(f"missing_required_file:{ref['path']}")
            if ref["exists"] and not _is_under(root, root / ref["path"], root / DEFAULT_CONTEXT_ROOT / "proposal_wave"):
                lane_blockers.append(f"path_outside_proposal_wave:{ref['path']}")
        proposal_payload = _read_json(root / proposal_json_ref["path"]) if proposal_json_ref["exists"] else {}
        workspace_payload = _read_json(root / workspace_ref["path"]) if workspace_ref["exists"] else {}
        if proposal_json_ref["exists"] and not proposal_payload:
            lane_blockers.append("proposal_json_not_parseable")
        if workspace_ref["exists"] and not workspace_payload:
            lane_blockers.append("workspace_json_not_parseable")
        if lane.get("candidate_only") is not True:
            lane_blockers.append("lane_candidate_only_not_true")
        if lane.get("source_files_edited") is not False:
            lane_blockers.append("lane_source_files_edited_not_false")
        if patch_ref["exists"] and lane.get("patch_proposal_unapplied") is not True:
            lane_blockers.append("patch_proposal_exists_but_unapplied_not_true")
        if workspace_payload:
            authority = workspace_payload.get("authority")
            if isinstance(authority, Mapping):
                if authority.get("raw_source_write_authority") is not False:
                    lane_blockers.append("workspace_raw_source_write_authority_not_false")
                if authority.get("patch_apply_authority") is not False:
                    lane_blockers.append("workspace_patch_apply_authority_not_false")
        lane_results.append(
            {
                "lane_id": lane_id,
                "ok": not lane_blockers,
                "blockers": lane_blockers,
                "files": {
                    "workspace": workspace_ref,
                    "proposal_json": proposal_json_ref,
                    "proposal_md": proposal_md_ref,
                    "patch_proposal": patch_ref,
                },
            }
        )
        for blocker_text in lane_blockers:
            blockers.append(
                {
                    "code": "PROPOSAL_WAVE_LANE_VALIDATION_FAILED",
                    "severity": "high",
                    "lane_id": lane_id,
                    "detail": blocker_text,
                }
            )
    return {
        "schema_id": "ion.domain_weaver.proposal_wave_validation.v0_1_candidate",
        "validator_available": True,
        "ok": not blockers,
        "status": "proposal_wave_validation_passed" if not blockers else "proposal_wave_validation_failed",
        "fanin_path": PROPOSAL_FANIN_PATH.as_posix(),
        "lane_count": len(lane_results),
        "lane_results": lane_results,
        "blockers": blockers,
        "source_files_edited_by_workers": any(
            row.get("source_files_edited") is True for row in fanin.get("lanes") or []
        ),
        "patches_applied": False,
        "accepted_state_claimed": False,
    }


def write_swarm_control_plane(
    active_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    generated_at: str | None = None,
    write_receipt: bool = True,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    control = build_swarm_control_plane(root, generated_at=generated_at)
    out_dir = _resolve_output_dir(root, output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    report_path = out_dir / DEFAULT_CONTROL_PLANE_NAME
    readiness_path = out_dir / DEFAULT_READINESS_NAME
    watch_path = out_dir / DEFAULT_WATCH_MATRIX_NAME
    fleet_path = out_dir / DEFAULT_FLEET_PLAN_NAME
    graph_path = out_dir / DEFAULT_CONTEXT_DELTAS_NAME

    report_text = render_control_plane_report(control)
    readiness_text = _stable_json(control["readiness"])
    watch_text = _stable_json(control["watch_matrix"])
    fleet_text = _stable_json(control["fleet_plan"])
    graph_text = _stable_json(control["candidate_context_graph_deltas"])

    report_path.write_text(report_text, encoding="utf-8")
    readiness_path.write_text(readiness_text, encoding="utf-8")
    watch_path.write_text(watch_text, encoding="utf-8")
    fleet_path.write_text(fleet_text, encoding="utf-8")
    graph_path.write_text(graph_text, encoding="utf-8")

    result = {
        "schema_id": WRITE_RESULT_SCHEMA_ID,
        "generated_at": control["generated_at"],
        "active_root": str(root),
        "verdict": control["verdict"],
        "report_path": _rel(root, report_path),
        "report_sha256": _sha256_text(report_text),
        "readiness_path": _rel(root, readiness_path),
        "readiness_sha256": _sha256_text(readiness_text),
        "watch_matrix_path": _rel(root, watch_path),
        "watch_matrix_sha256": _sha256_text(watch_text),
        "fleet_plan_path": _rel(root, fleet_path),
        "fleet_plan_sha256": _sha256_text(fleet_text),
        "context_graph_delta_path": _rel(root, graph_path),
        "context_graph_delta_sha256": _sha256_text(graph_text),
        "watch_target_count": control["watch_matrix"]["coverage"]["target_count"],
        "fleet_lane_count": control["fleet_plan"]["lane_count"],
        "blocker_count": len(control["readiness"]["blockers_ranked"]),
        "authority": AUTHORITY,
    }
    if write_receipt:
        result["operator_receipt_path"] = write_operator_receipt(root, result, control)
    return result


def build_limited_watch_matrix_refresh(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Evaluate current watch targets without starting workers or queue runs."""

    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    matrix_path = root / DEFAULT_OUTPUT_DIR / DEFAULT_WATCH_MATRIX_NAME
    watch_matrix = _read_json(matrix_path) or build_swarm_watch_matrix(
        root, generated_at=generated
    )
    readiness = _read_json(root / DEFAULT_OUTPUT_DIR / DEFAULT_READINESS_NAME)
    self_readiness = _read_json(root / SELF_EVOLUTION_READINESS_PATH)
    proposal_validation = validate_current_proposal_wave(root)
    blocker_rows = _dedupe_blockers(
        [
            *[
                dict(row)
                for row in readiness.get("blockers_ranked") or []
                if isinstance(row, Mapping)
            ],
            *_self_readiness_blockers(self_readiness),
        ]
    )
    blocker_codes = {str(row.get("code") or "") for row in blocker_rows}
    queue_summary = _watch_queue_summary(root)
    spawn_summary = _watch_spawn_request_summary(root)
    observations = [
        _build_watch_observation(
            root,
            target,
            blocker_codes=blocker_codes,
            proposal_validation=proposal_validation,
            queue_summary=queue_summary,
            spawn_summary=spawn_summary,
        )
        for target in watch_matrix.get("targets") or []
        if isinstance(target, Mapping)
    ]
    alerts = [
        alert
        for observation in observations
        for alert in observation.get("alerts", [])
        if isinstance(alert, Mapping)
    ]
    severity_counts = {
        severity: sum(1 for alert in alerts if alert.get("severity") == severity)
        for severity in ("critical", "high", "medium", "low", "info")
    }
    response_packets = []
    for observation in observations:
        if observation.get("alert_level") in {"critical", "high", "medium"}:
            packet = str(observation.get("response_packet") or "")
            if packet and packet not in response_packets:
                response_packets.append(packet)
    graph_deltas = _limited_watch_graph_deltas(
        root,
        generated_at=generated,
        observations=observations,
        alerts=alerts,
    )
    verdict = _limited_watch_verdict(severity_counts)
    return {
        "schema_id": LIMITED_WATCH_REFRESH_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "limited_watch_matrix_refresh_built",
        "verdict": verdict,
        "source_watch_matrix_path": DEFAULT_WATCH_MATRIX_NAME,
        "authority": AUTHORITY,
        "summary": {
            "target_count": len(observations),
            "alert_count": len(alerts),
            "severity_counts": severity_counts,
            "response_packet_count": len(response_packets),
            "graph_delta_claim_count": len(graph_deltas["upsert_claims"]),
        },
        "queue_summary": queue_summary,
        "spawn_request_summary": spawn_summary,
        "proposal_wave_validation": proposal_validation,
        "blocker_codes_observed": sorted(blocker_codes),
        "observations": observations,
        "alerts": alerts,
        "response_packets": response_packets,
        "candidate_context_graph_deltas": graph_deltas,
        "next_packet": response_packets[0]
        if response_packets
        else "PCKT-DOMAIN-WEAVER-BOUNDARY-CAPPED-CANDIDATE-FANOUT-WAVE-V0_4",
        "actual_watch_daemon_started": False,
        "actual_spawn_performed": False,
        "codex_queue_run_started": False,
        "general_queue_processing_allowed": False,
        "accepted_state_claimed": False,
        "non_claims": NON_CLAIMS,
    }


def write_limited_watch_matrix_refresh(
    active_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    generated_at: str | None = None,
    write_receipt: bool = True,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    refresh = build_limited_watch_matrix_refresh(root, generated_at=generated_at)
    out_dir = _resolve_output_dir(root, output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    refresh_path = out_dir / DEFAULT_WATCH_REFRESH_NAME
    report_path = out_dir / DEFAULT_WATCH_REFRESH_REPORT_NAME
    alerts_path = out_dir / DEFAULT_WATCH_ALERTS_NAME
    refresh_text = _stable_json(refresh)
    report_text = render_limited_watch_refresh_report(refresh)
    alerts_payload = {
        "schema_id": LIMITED_WATCH_ALERTS_SCHEMA_ID,
        "generated_at": refresh["generated_at"],
        "active_root": refresh["active_root"],
        "verdict": refresh["verdict"],
        "summary": refresh["summary"],
        "alerts": refresh["alerts"],
        "response_packets": refresh["response_packets"],
        "candidate_context_graph_deltas": refresh["candidate_context_graph_deltas"],
        "authority": AUTHORITY,
        "non_claims": NON_CLAIMS,
    }
    alerts_text = _stable_json(alerts_payload)
    refresh_path.write_text(refresh_text, encoding="utf-8")
    report_path.write_text(report_text, encoding="utf-8")
    alerts_path.write_text(alerts_text, encoding="utf-8")

    result = {
        "schema_id": WATCH_REFRESH_WRITE_RESULT_SCHEMA_ID,
        "generated_at": refresh["generated_at"],
        "active_root": str(root),
        "verdict": refresh["verdict"],
        "refresh_path": _rel(root, refresh_path),
        "refresh_sha256": _sha256_text(refresh_text),
        "report_path": _rel(root, report_path),
        "report_sha256": _sha256_text(report_text),
        "alerts_path": _rel(root, alerts_path),
        "alerts_sha256": _sha256_text(alerts_text),
        "alert_count": refresh["summary"]["alert_count"],
        "target_count": refresh["summary"]["target_count"],
        "next_packet": refresh["next_packet"],
        "authority": AUTHORITY,
    }
    if write_receipt:
        result["operator_receipt_path"] = write_watch_refresh_operator_receipt(
            root, result, refresh
        )
    return result


def build_global_queue_backlog_context_identity_hygiene(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Evaluate global queue/backlog context identity without queue mutation."""

    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    generated_dt = _parse_iso(generated)
    work_requests = _load_work_request_rows(root)
    governance = shape_domain_weaver_queue_governance_rows(
        work_requests,
        now=generated_dt,
    )
    worker_readiness = build_domain_weaver_worker_start_readiness(root)
    worker_backlog = build_domain_weaver_worker_start_backlog_hygiene(root)
    queue_summary = _watch_queue_summary(root)
    spawn_summary = _global_spawn_request_summary(root)
    readiness_summary = _mapping(worker_readiness.get("summary"))
    governance_summary = _mapping(governance.get("summary"))
    blocker_rows = _global_queue_hygiene_blockers(
        worker_readiness=worker_readiness,
        worker_backlog=worker_backlog,
        governance=governance,
        spawn_summary=spawn_summary,
    )
    repair_packets = _global_queue_hygiene_repair_packets(
        worker_readiness=worker_readiness,
        worker_backlog=worker_backlog,
        governance=governance,
        spawn_summary=spawn_summary,
    )
    graph_deltas = _global_queue_hygiene_graph_deltas(
        root,
        generated_at=generated,
        blocker_rows=blocker_rows,
        repair_packets=repair_packets,
        worker_readiness=worker_readiness,
        worker_backlog=worker_backlog,
        governance=governance,
        spawn_summary=spawn_summary,
    )
    exact_paths = list(worker_backlog.get("candidate_exact_request_paths") or [])
    hygiene_ok = not blocker_rows
    verdict = (
        "GLOBAL_QUEUE_CONTEXT_IDENTITY_HYGIENE_CLEAN"
        if hygiene_ok
        else "GLOBAL_QUEUE_CONTEXT_IDENTITY_HYGIENE_BLOCKED_EXACT_PATH_ONLY"
    )
    return {
        "schema_id": GLOBAL_QUEUE_HYGIENE_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "global_queue_backlog_context_identity_hygiene_built",
        "verdict": verdict,
        "hygiene_ok": hygiene_ok,
        "exact_request_path_required": True,
        "general_queue_processing_allowed": False,
        "codex_queue_run_started": False,
        "actual_spawn_performed": False,
        "direct_nested_spawn": False,
        "raw_external_codex_exec": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
        "summary": {
            "work_request_file_count": len(work_requests),
            "active_queue_request_count": int(queue_summary.get("request_count") or 0),
            "queueable_readiness_request_count": int(
                readiness_summary.get("queueable_request_count") or 0
            ),
            "ready_queueable_request_count": int(
                readiness_summary.get("ready_queueable_request_count") or 0
            ),
            "blocked_request_count": int(
                worker_backlog.get("summary", {}).get("blocked_request_count") or 0
            ),
            "stale_waiting_request_count": int(
                governance_summary.get("stale_waiting_request_count") or 0
            ),
            "terminal_repair_request_count": int(
                governance_summary.get("terminal_repair_request_count") or 0
            ),
            "actionable_duplicate_group_count": int(
                governance_summary.get("actionable_duplicate_group_count") or 0
            ),
            "candidate_exact_request_path_count": len(exact_paths),
            "spawn_request_count": int(spawn_summary.get("spawn_request_count") or 0),
            "requested_spawn_request_count": int(spawn_summary.get("requested_count") or 0),
            "blocker_count": len(blocker_rows),
            "repair_packet_count": len(repair_packets),
            "graph_delta_claim_count": len(graph_deltas["upsert_claims"]),
        },
        "active_queue_summary": queue_summary,
        "all_work_request_governance_summary": governance_summary,
        "work_request_status_counts": governance.get("status_counts", {}),
        "work_request_lane_counts": governance.get("lane_counts", {}),
        "worker_start_readiness_summary": readiness_summary,
        "worker_start_readiness_blockers": list(worker_readiness.get("blockers") or []),
        "worker_start_backlog_hygiene_summary": worker_backlog.get("summary", {}),
        "worker_start_backlog_blocker_rank": worker_backlog.get("blocker_rank", []),
        "worker_start_backlog_groups": worker_backlog.get("groups", {}),
        "candidate_exact_request_paths": exact_paths,
        "spawn_request_summary": spawn_summary,
        "blockers_ranked": blocker_rows,
        "repair_packets": repair_packets,
        "candidate_context_graph_deltas": graph_deltas,
        "next_packet": repair_packets[0]["packet_id"]
        if repair_packets
        else "PCKT-DOMAIN-WEAVER-LIMITED-WATCH-MATRIX-REFRESH-V0_2",
        "source_evidence": [
            _evidence_ref(root, QUEUE_PATH.as_posix()),
            _evidence_ref(root, QUEUE_RUNNER_STATE_PATH.as_posix()),
            _evidence_ref(root, CODEX_WORK_REQUESTS_DIR.as_posix()),
            _evidence_ref(root, "ION/05_context/current/domain_weaver/workers"),
        ],
        "non_claims": [
            *NON_CLAIMS,
            "This evaluator does not start exact paths; it only identifies whether exact-path-only handling remains required.",
            "Global queue backlog hygiene is not accepted-state repair and does not mutate request files.",
            "Candidate context graph deltas are not materialized graph state.",
        ],
    }


def write_global_queue_backlog_context_identity_hygiene(
    active_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    generated_at: str | None = None,
    write_receipt: bool = True,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    hygiene = build_global_queue_backlog_context_identity_hygiene(
        root,
        generated_at=generated_at,
    )
    out_dir = _resolve_output_dir(root, output_dir or DEFAULT_QUEUE_GOVERNANCE_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    hygiene_path = out_dir / DEFAULT_GLOBAL_QUEUE_HYGIENE_NAME
    report_path = out_dir / DEFAULT_GLOBAL_QUEUE_HYGIENE_REPORT_NAME
    deltas_path = out_dir / DEFAULT_GLOBAL_QUEUE_CONTEXT_IDENTITY_DELTAS_NAME
    hygiene_text = _stable_json(hygiene)
    report_text = render_global_queue_hygiene_report(hygiene)
    deltas_payload = dict(hygiene["candidate_context_graph_deltas"])
    deltas_text = _stable_json(deltas_payload)
    hygiene_path.write_text(hygiene_text, encoding="utf-8")
    report_path.write_text(report_text, encoding="utf-8")
    deltas_path.write_text(deltas_text, encoding="utf-8")

    result = {
        "schema_id": GLOBAL_QUEUE_HYGIENE_WRITE_RESULT_SCHEMA_ID,
        "generated_at": hygiene["generated_at"],
        "active_root": str(root),
        "verdict": hygiene["verdict"],
        "hygiene_path": _rel(root, hygiene_path),
        "hygiene_sha256": _sha256_text(hygiene_text),
        "report_path": _rel(root, report_path),
        "report_sha256": _sha256_text(report_text),
        "context_graph_delta_path": _rel(root, deltas_path),
        "context_graph_delta_sha256": _sha256_text(deltas_text),
        "blocker_count": hygiene["summary"]["blocker_count"],
        "repair_packet_count": hygiene["summary"]["repair_packet_count"],
        "next_packet": hygiene["next_packet"],
        "authority": AUTHORITY,
    }
    if write_receipt:
        result["operator_receipt_path"] = write_global_queue_hygiene_operator_receipt(
            root,
            result,
            hygiene,
        )
    return result


def build_post_sidecar_global_queue_hygiene(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
    expected_source_original_count: int = 7,
) -> dict[str, Any]:
    """Fan in the sidecar queue-hygiene result without mutating queue state."""

    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    source_rows = _queued_source_original_rows(root)
    classification_rows = [
        _post_sidecar_queue_hygiene_row(root, row)
        for row in source_rows
    ]
    classification_counts: dict[str, int] = {}
    replacement_status_counts: dict[str, int] = {}
    for row in classification_rows:
        classification = str(row.get("candidate_classification") or "unknown")
        classification_counts[classification] = classification_counts.get(classification, 0) + 1
        replacement_status = str(row.get("replacement_current_status") or "")
        if replacement_status:
            replacement_status_counts[replacement_status] = (
                replacement_status_counts.get(replacement_status, 0) + 1
            )
    unsettled_rows = [
        row
        for row in classification_rows
        if row.get("candidate_classification") == "unsettled_queued_original_requires_review"
    ]
    supersede_rows = [
        row
        for row in classification_rows
        if row.get("candidate_classification") == "supersede_with_fresh_exact_request"
    ]
    missing_replacement_rows = [
        row
        for row in supersede_rows
        if not row.get("replacement_request_found")
    ]
    failed_replacement_rows = [
        row
        for row in supersede_rows
        if _post_sidecar_replacement_failed(row)
    ]
    accepted_replacement_count = sum(
        1
        for row in supersede_rows
        if row.get("replacement_current_status") == "RETURN_RECORDED_PROOF_ACCEPTED"
    )
    source_original_count_matches_expected = (
        len(source_rows) == max(0, int(expected_source_original_count))
    )
    all_source_originals_classified = (
        source_original_count_matches_expected
        and not unsettled_rows
        and len(classification_rows) == max(0, int(expected_source_original_count))
    )
    graph_deltas = _post_sidecar_global_queue_hygiene_graph_deltas(
        root,
        generated_at=generated,
        rows=classification_rows,
    )
    blockers = _post_sidecar_global_queue_hygiene_blockers(
        source_original_count=len(source_rows),
        expected_source_original_count=max(0, int(expected_source_original_count)),
        unsettled_rows=unsettled_rows,
        missing_replacement_rows=missing_replacement_rows,
        failed_replacement_rows=failed_replacement_rows,
    )
    if unsettled_rows or missing_replacement_rows:
        verdict = "POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_BLOCKED_BY_UNSETTLED_OR_MISSING_REPLACEMENTS"
    elif failed_replacement_rows:
        verdict = "POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_CLASSIFIED_EXACT_PATH_ONLY_REPLACEMENT_FAILURES_PRESENT"
    elif all_source_originals_classified:
        verdict = "POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_CLASSIFIED_EXACT_PATH_ONLY"
    else:
        verdict = "POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_COUNT_DRIFT_REVIEW_REQUIRED"
    next_packets = _post_sidecar_global_queue_hygiene_next_packets(
        unsettled_rows=unsettled_rows,
        missing_replacement_rows=missing_replacement_rows,
        failed_replacement_rows=failed_replacement_rows,
        all_source_originals_classified=all_source_originals_classified,
    )
    return {
        "schema_id": POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "post_sidecar_global_queue_hygiene_built",
        "verdict": verdict,
        "hygiene_ok": False,
        "source_originals_remain_queued": bool(source_rows),
        "all_expected_source_originals_classified": all_source_originals_classified,
        "exact_request_path_required": True,
        "general_queue_processing_allowed": False,
        "codex_queue_run_started": False,
        "codex_queue_run_started_by_this_packet": False,
        "actual_spawn_performed": False,
        "source_request_files_mutated": False,
        "replacement_request_files_written": 0,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
        "summary": {
            "expected_source_original_count": max(0, int(expected_source_original_count)),
            "queued_source_original_count": len(source_rows),
            "source_original_count_matches_expected": source_original_count_matches_expected,
            "classified_source_original_count": len(classification_rows) - len(unsettled_rows),
            "unsettled_source_original_count": len(unsettled_rows),
            "quarantine_as_stale_external_non_domain_count": classification_counts.get(
                "quarantine_as_stale_external_non_domain",
                0,
            ),
            "supersede_with_fresh_exact_request_count": classification_counts.get(
                "supersede_with_fresh_exact_request",
                0,
            ),
            "replacement_request_found_count": sum(
                1 for row in supersede_rows if row.get("replacement_request_found")
            ),
            "missing_replacement_request_count": len(missing_replacement_rows),
            "replacement_return_accepted_count": accepted_replacement_count,
            "replacement_failed_count": len(failed_replacement_rows),
            "replacement_current_status_counts": replacement_status_counts,
            "classification_counts": classification_counts,
            "blocker_count": len(blockers),
            "graph_delta_claim_count": len(graph_deltas["upsert_claims"]),
            "source_request_files_mutated": False,
            "replacement_request_files_written": 0,
            "codex_queue_run_started_by_this_packet": False,
            "general_queue_processing_allowed": False,
        },
        "source_original_rows": classification_rows,
        "blockers_ranked": blockers,
        "next_packets": next_packets,
        "next_packet": next_packets[0]["packet_id"]
        if next_packets
        else "PCKT-DOMAIN-WEAVER-LIMITED-WATCH-MATRIX-REFRESH-V0_2",
        "candidate_context_graph_deltas": graph_deltas,
        "source_evidence": [
            _evidence_ref(root, CODEX_WORK_REQUESTS_DIR.as_posix()),
            _evidence_ref(
                root,
                (DEFAULT_QUEUE_GOVERNANCE_DIR / DEFAULT_STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_NAME).as_posix(),
            ),
            _evidence_ref(
                root,
                (DEFAULT_QUEUE_GOVERNANCE_DIR / DEFAULT_STALE_WAITING_RECONCILIATION_SETTLEMENT_NAME).as_posix(),
            ),
            _evidence_ref(
                root,
                (DEFAULT_QUEUE_GOVERNANCE_DIR / DEFAULT_EXACT_REISSUE_REQUEST_DISPATCH_READINESS_NAME).as_posix(),
            ),
        ],
        "non_claims": [
            *NON_CLAIMS,
            "This post-sidecar readback classifies current queued source originals only; it does not mutate their status.",
            "Replacement request outcomes are carrier intake evidence, not proof of automatic original-agent reaction.",
            "Failed replacement request rows require fan-in and repair; they do not authorize general queue processing.",
            "Candidate lifecycle/quarantine settlements are not accepted lifecycle state.",
        ],
    }


def write_post_sidecar_global_queue_hygiene(
    active_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    generated_at: str | None = None,
    expected_source_original_count: int = 7,
    write_receipt: bool = True,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    readback = build_post_sidecar_global_queue_hygiene(
        root,
        generated_at=generated_at,
        expected_source_original_count=expected_source_original_count,
    )
    out_dir = _resolve_output_dir(root, output_dir or DEFAULT_QUEUE_GOVERNANCE_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    readback_path = out_dir / DEFAULT_POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_NAME
    report_path = out_dir / DEFAULT_POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_REPORT_NAME
    deltas_path = out_dir / DEFAULT_POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_DELTAS_NAME
    readback_text = _stable_json(readback)
    report_text = render_post_sidecar_global_queue_hygiene_report(readback)
    deltas_text = _stable_json(dict(readback["candidate_context_graph_deltas"]))
    readback_path.write_text(readback_text, encoding="utf-8")
    report_path.write_text(report_text, encoding="utf-8")
    deltas_path.write_text(deltas_text, encoding="utf-8")

    result = {
        "schema_id": POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_WRITE_RESULT_SCHEMA_ID,
        "generated_at": readback["generated_at"],
        "active_root": str(root),
        "verdict": readback["verdict"],
        "readback_path": _rel(root, readback_path),
        "readback_sha256": _sha256_text(readback_text),
        "report_path": _rel(root, report_path),
        "report_sha256": _sha256_text(report_text),
        "context_graph_delta_path": _rel(root, deltas_path),
        "context_graph_delta_sha256": _sha256_text(deltas_text),
        "queued_source_original_count": readback["summary"]["queued_source_original_count"],
        "classified_source_original_count": readback["summary"]["classified_source_original_count"],
        "replacement_failed_count": readback["summary"]["replacement_failed_count"],
        "general_queue_processing_allowed": False,
        "source_request_files_mutated": False,
        "replacement_request_files_written": 0,
        "codex_queue_run_started": False,
        "actual_spawn_performed": False,
        "accepted_state_claimed": False,
        "next_packet": readback["next_packet"],
        "authority": AUTHORITY,
    }
    if write_receipt:
        result["operator_receipt_path"] = write_post_sidecar_global_queue_hygiene_operator_receipt(
            root,
            result,
            readback,
        )
    return result


def build_global_queue_backlog_identity_repair_preview(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build candidate repair rows for blocked queue/context identity posture."""

    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    generated_dt = _parse_iso(generated)
    work_requests = _load_work_request_rows(root)
    governance = shape_domain_weaver_queue_governance_rows(
        work_requests,
        now=generated_dt,
    )
    worker_readiness = build_domain_weaver_worker_start_readiness(root)
    worker_backlog = build_domain_weaver_worker_start_backlog_hygiene(root)
    hygiene = build_global_queue_backlog_context_identity_hygiene(
        root,
        generated_at=generated,
    )
    repair_rows = _queue_identity_repair_rows(worker_readiness)
    lifecycle_rows = _queue_lifecycle_preview_rows(governance)
    graph_deltas = _global_queue_repair_preview_graph_deltas(
        root,
        generated_at=generated,
        repair_rows=repair_rows,
        lifecycle_rows=lifecycle_rows,
        hygiene=hygiene,
    )
    repair_class_counts: dict[str, int] = {}
    for row in repair_rows:
        repair_class = str(row.get("repair_class") or "unknown")
        repair_class_counts[repair_class] = repair_class_counts.get(repair_class, 0) + 1
    lifecycle_class_counts: dict[str, int] = {}
    for row in lifecycle_rows:
        repair_class = str(row.get("repair_class") or "unknown")
        lifecycle_class_counts[repair_class] = lifecycle_class_counts.get(repair_class, 0) + 1
    mutation_gate_required = bool(repair_rows or lifecycle_rows)
    verdict = (
        "GLOBAL_QUEUE_REPAIR_PREVIEW_ROWS_READY_MUTATION_GATE_REQUIRED"
        if mutation_gate_required
        else "GLOBAL_QUEUE_REPAIR_PREVIEW_NO_ROWS_REQUIRED"
    )
    next_packets = _repair_preview_next_packets(
        repair_rows=repair_rows,
        lifecycle_rows=lifecycle_rows,
        hygiene=hygiene,
    )
    return {
        "schema_id": GLOBAL_QUEUE_REPAIR_PREVIEW_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "global_queue_backlog_identity_repair_preview_built",
        "verdict": verdict,
        "source_hygiene_verdict": hygiene.get("verdict"),
        "source_hygiene_summary": hygiene.get("summary"),
        "exact_request_path_required": True,
        "general_queue_processing_allowed": False,
        "codex_queue_run_started": False,
        "actual_spawn_performed": False,
        "request_files_mutated": False,
        "lifecycle_ledger_mutated": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
        "summary": {
            "queueable_repair_row_count": len(repair_rows),
            "repair_class_counts": repair_class_counts,
            "lifecycle_preview_row_count": len(lifecycle_rows),
            "lifecycle_class_counts": lifecycle_class_counts,
            "candidate_exact_request_path_count": len(
                worker_backlog.get("candidate_exact_request_paths") or []
            ),
            "graph_delta_claim_count": len(graph_deltas["upsert_claims"]),
            "mutation_gate_required": mutation_gate_required,
        },
        "candidate_exact_request_paths": list(
            worker_backlog.get("candidate_exact_request_paths") or []
        ),
        "queueable_repair_rows": repair_rows,
        "lifecycle_preview_rows": lifecycle_rows,
        "next_packets": next_packets,
        "next_packet": next_packets[0]["packet_id"]
        if next_packets
        else "PCKT-DOMAIN-WEAVER-LIMITED-WATCH-MATRIX-REFRESH-V0_2",
        "candidate_context_graph_deltas": graph_deltas,
        "source_evidence": [
            _evidence_ref(root, CODEX_WORK_REQUESTS_DIR.as_posix()),
            _evidence_ref(root, QUEUE_PATH.as_posix()),
            _evidence_ref(root, QUEUE_RUNNER_STATE_PATH.as_posix()),
            _evidence_ref(root, DEFAULT_QUEUE_GOVERNANCE_DIR.as_posix()),
        ],
        "non_claims": [
            *NON_CLAIMS,
            "Repair preview rows are candidate instructions only and do not mutate work-request files.",
            "Lifecycle preview rows are not lifecycle-ledger writes.",
            "Rows with missing domain or capsule identity must be reissued or separately approved; no inferred identity is accepted state.",
        ],
    }


def write_global_queue_backlog_identity_repair_preview(
    active_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    generated_at: str | None = None,
    write_receipt: bool = True,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    preview = build_global_queue_backlog_identity_repair_preview(
        root,
        generated_at=generated_at,
    )
    out_dir = _resolve_output_dir(root, output_dir or DEFAULT_QUEUE_GOVERNANCE_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    preview_path = out_dir / DEFAULT_GLOBAL_QUEUE_REPAIR_PREVIEW_NAME
    report_path = out_dir / DEFAULT_GLOBAL_QUEUE_REPAIR_PREVIEW_REPORT_NAME
    deltas_path = out_dir / DEFAULT_GLOBAL_QUEUE_REPAIR_PREVIEW_DELTAS_NAME
    preview_text = _stable_json(preview)
    report_text = render_global_queue_repair_preview_report(preview)
    deltas_text = _stable_json(dict(preview["candidate_context_graph_deltas"]))
    preview_path.write_text(preview_text, encoding="utf-8")
    report_path.write_text(report_text, encoding="utf-8")
    deltas_path.write_text(deltas_text, encoding="utf-8")

    result = {
        "schema_id": GLOBAL_QUEUE_REPAIR_PREVIEW_WRITE_RESULT_SCHEMA_ID,
        "generated_at": preview["generated_at"],
        "active_root": str(root),
        "verdict": preview["verdict"],
        "preview_path": _rel(root, preview_path),
        "preview_sha256": _sha256_text(preview_text),
        "report_path": _rel(root, report_path),
        "report_sha256": _sha256_text(report_text),
        "context_graph_delta_path": _rel(root, deltas_path),
        "context_graph_delta_sha256": _sha256_text(deltas_text),
        "queueable_repair_row_count": preview["summary"]["queueable_repair_row_count"],
        "lifecycle_preview_row_count": preview["summary"]["lifecycle_preview_row_count"],
        "next_packet": preview["next_packet"],
        "authority": AUTHORITY,
    }
    if write_receipt:
        result["operator_receipt_path"] = write_global_queue_repair_preview_operator_receipt(
            root,
            result,
            preview,
        )
    return result


def build_queue_request_metadata_identity_reissue(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
    source_preview: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build candidate reissue review rows for requests missing metadata identity.

    This is a worksheet layer only. It does not write replacement request files
    or infer missing domain/capsule identity as truth.
    """

    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    preview, preview_ref = _load_repair_preview_or_build(
        root,
        generated_at=generated,
        source_preview=source_preview,
    )
    source_rows = [
        row
        for row in list(preview.get("queueable_repair_rows") or [])
        if isinstance(row, Mapping)
        and row.get("repair_class") == "metadata_identity_reissue_required"
    ]
    excluded_rows = [
        row
        for row in list(preview.get("queueable_repair_rows") or [])
        if isinstance(row, Mapping)
        and row.get("repair_class") != "metadata_identity_reissue_required"
    ]
    worksheet_rows = [
        _metadata_identity_reissue_review_row(root, row)
        for row in source_rows
    ]
    allowed_count = sum(1 for row in worksheet_rows if row["candidate_reissue_allowed_now"])
    blocked_count = len(worksheet_rows) - allowed_count
    graph_deltas = _queue_request_metadata_identity_reissue_graph_deltas(
        root,
        generated_at=generated,
        worksheet_rows=worksheet_rows,
        source_preview_ref=preview_ref,
    )
    verdict = "QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_NO_ROWS_REQUIRED"
    if worksheet_rows and allowed_count:
        verdict = "QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_READY"
    elif worksheet_rows:
        verdict = "QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_ASSIGNMENT_BLOCKED"
    next_packet = (
        "PCKT-DOMAIN-WEAVER-QUEUE-REQUEST-METADATA-IDENTITY-REISSUE-APPLY-REVIEW-V0_1"
        if allowed_count
        else "PCKT-DOMAIN-WEAVER-DOMAIN-ROLE-CAPSULE-ASSIGNMENT-FOR-METADATA-REISSUE-V0_1"
    )
    return {
        "schema_id": QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "queue_request_metadata_identity_reissue_candidate_built",
        "verdict": verdict,
        "source_preview": preview_ref,
        "source_preview_verdict": preview.get("verdict"),
        "source_preview_generated_at": preview.get("generated_at"),
        "source_preview_is_latest_file": bool(preview_ref.get("path")),
        "metadata_identity_source_rows": len(source_rows),
        "excluded_non_metadata_repair_rows": [
            {
                "request_id": row.get("request_id"),
                "repair_class": row.get("repair_class"),
                "repair_packet_id": row.get("repair_packet_id"),
            }
            for row in excluded_rows
        ],
        "summary": {
            "worksheet_row_count": len(worksheet_rows),
            "candidate_reissue_allowed_now_count": allowed_count,
            "candidate_reissue_blocked_count": blocked_count,
            "excluded_non_metadata_repair_row_count": len(excluded_rows),
            "source_preview_queueable_repair_row_count": len(
                list(preview.get("queueable_repair_rows") or [])
            ),
            "graph_delta_claim_count": len(graph_deltas["upsert_claims"]),
            "request_files_mutated": False,
            "replacement_requests_written": 0,
        },
        "worksheet_rows": worksheet_rows,
        "next_packets": _metadata_identity_reissue_next_packets(
            allowed_count=allowed_count,
            blocked_count=blocked_count,
            excluded_rows=excluded_rows,
        ),
        "next_packet": next_packet,
        "request_files_mutated": False,
        "replacement_requests_written": 0,
        "codex_queue_run_started": False,
        "actual_spawn_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
        "candidate_context_graph_deltas": graph_deltas,
        "source_evidence": [
            preview_ref,
            _evidence_ref(root, CODEX_WORK_REQUESTS_DIR.as_posix()),
            _evidence_ref(root, DOMAIN_CAPSULE_PATH.as_posix()),
            _evidence_ref(root, DEFAULT_QUEUE_GOVERNANCE_DIR.as_posix()),
        ],
        "non_claims": [
            *NON_CLAIMS,
            "Metadata identity reissue rows are worksheets only; no replacement request file has been written.",
            "Missing domain, role, selected mount, active context, or working capsule identity must be supplied by an explicit later packet.",
            "The context-gate repair row is intentionally excluded from this metadata-only packet and remains routed to its own gate proof.",
        ],
    }


def write_queue_request_metadata_identity_reissue(
    active_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    generated_at: str | None = None,
    write_receipt: bool = True,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    worksheet = build_queue_request_metadata_identity_reissue(
        root,
        generated_at=generated_at,
    )
    out_dir = _resolve_output_dir(root, output_dir or DEFAULT_QUEUE_GOVERNANCE_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    worksheet_path = out_dir / DEFAULT_QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_NAME
    report_path = out_dir / DEFAULT_QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_REPORT_NAME
    deltas_path = out_dir / DEFAULT_QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_DELTAS_NAME
    worksheet_text = _stable_json(worksheet)
    report_text = render_queue_request_metadata_identity_reissue_report(worksheet)
    deltas_text = _stable_json(dict(worksheet["candidate_context_graph_deltas"]))
    worksheet_path.write_text(worksheet_text, encoding="utf-8")
    report_path.write_text(report_text, encoding="utf-8")
    deltas_path.write_text(deltas_text, encoding="utf-8")

    result = {
        "schema_id": QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_WRITE_RESULT_SCHEMA_ID,
        "generated_at": worksheet["generated_at"],
        "active_root": str(root),
        "verdict": worksheet["verdict"],
        "worksheet_path": _rel(root, worksheet_path),
        "worksheet_sha256": _sha256_text(worksheet_text),
        "report_path": _rel(root, report_path),
        "report_sha256": _sha256_text(report_text),
        "context_graph_delta_path": _rel(root, deltas_path),
        "context_graph_delta_sha256": _sha256_text(deltas_text),
        "worksheet_row_count": worksheet["summary"]["worksheet_row_count"],
        "candidate_reissue_allowed_now_count": worksheet["summary"][
            "candidate_reissue_allowed_now_count"
        ],
        "candidate_reissue_blocked_count": worksheet["summary"][
            "candidate_reissue_blocked_count"
        ],
        "next_packet": worksheet["next_packet"],
        "request_files_mutated": False,
        "replacement_requests_written": 0,
        "codex_queue_run_started": False,
        "authority": AUTHORITY,
    }
    if write_receipt:
        result["operator_receipt_path"] = write_queue_request_metadata_identity_reissue_operator_receipt(
            root,
            result,
            worksheet,
        )
    return result


def build_queue_metadata_identity_assignment(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
    source_reissue: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Assign candidate domain/role/mount/capsule bindings for reissue rows."""

    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    reissue, reissue_ref = _load_metadata_reissue_or_build(
        root,
        generated_at=generated,
        source_reissue=source_reissue,
    )
    mount_inventory = _codex_agent_mount_inventory(root)
    lifecycle_by_request_id = _metadata_assignment_lifecycle_map(root)
    assignment_rows = [
        _metadata_identity_assignment_row(
            root,
            row,
            mount_inventory=mount_inventory,
            lifecycle_row=lifecycle_by_request_id.get(str(row.get("source_request_id") or "")),
        )
        for row in list(reissue.get("worksheet_rows") or [])
        if isinstance(row, Mapping)
    ]
    disposition_counts: dict[str, int] = {}
    for row in assignment_rows:
        disposition = str(row.get("assignment_disposition") or "unknown")
        disposition_counts[disposition] = disposition_counts.get(disposition, 0) + 1
    existing_ready_count = sum(
        1 for row in assignment_rows if row.get("assignment_disposition") == "existing_mount_assignment_ready"
    )
    apply_review_ready_count = sum(
        1 for row in assignment_rows if row.get("candidate_reissue_apply_review_ready")
    )
    source_safety_blocked_count = sum(
        1
        for row in assignment_rows
        if row.get("assignment_disposition") == "existing_mount_assignment_ready"
        and _source_safety_blockers(row)
    )
    mount_required_count = sum(
        1 for row in assignment_rows if row.get("assignment_disposition") == "generated_mount_required"
    )
    quarantine_count = sum(
        1 for row in assignment_rows if row.get("assignment_disposition") == "supersede_or_quarantine_recommended"
    )
    graph_deltas = _queue_metadata_identity_assignment_graph_deltas(
        root,
        generated_at=generated,
        assignment_rows=assignment_rows,
        source_reissue_ref=reissue_ref,
    )
    if apply_review_ready_count and (mount_required_count or quarantine_count or source_safety_blocked_count):
        verdict = "QUEUE_METADATA_IDENTITY_ASSIGNMENT_PARTIAL_APPLY_REVIEW_READY"
    elif apply_review_ready_count:
        verdict = "QUEUE_METADATA_IDENTITY_ASSIGNMENT_APPLY_REVIEW_READY"
    elif source_safety_blocked_count:
        verdict = "QUEUE_METADATA_IDENTITY_ASSIGNMENT_SOURCE_SAFETY_BLOCKED"
    elif mount_required_count:
        verdict = "QUEUE_METADATA_IDENTITY_ASSIGNMENT_MOUNT_GENERATION_REQUIRED"
    elif quarantine_count:
        verdict = "QUEUE_METADATA_IDENTITY_ASSIGNMENT_QUARANTINE_REVIEW_REQUIRED"
    else:
        verdict = "QUEUE_METADATA_IDENTITY_ASSIGNMENT_NO_ROWS_REQUIRED"
    next_packets = _metadata_identity_assignment_next_packets(
        apply_review_ready_count=apply_review_ready_count,
        source_safety_blocked_count=source_safety_blocked_count,
        mount_required_count=mount_required_count,
        quarantine_count=quarantine_count,
    )
    return {
        "schema_id": QUEUE_METADATA_IDENTITY_ASSIGNMENT_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "queue_metadata_identity_assignment_candidate_built",
        "verdict": verdict,
        "source_reissue": reissue_ref,
        "source_reissue_verdict": reissue.get("verdict"),
        "source_reissue_generated_at": reissue.get("generated_at"),
        "source_reissue_is_latest_file": bool(reissue_ref.get("path")),
        "summary": {
            "assignment_row_count": len(assignment_rows),
            "existing_mount_assignment_ready_count": existing_ready_count,
            "apply_review_ready_count": apply_review_ready_count,
            "source_safety_blocked_count": source_safety_blocked_count,
            "generated_mount_required_count": mount_required_count,
            "supersede_or_quarantine_recommended_count": quarantine_count,
            "disposition_counts": disposition_counts,
            "mount_inventory_count": len(mount_inventory),
            "graph_delta_claim_count": len(graph_deltas["upsert_claims"]),
            "request_files_mutated": False,
            "replacement_requests_written": 0,
            "mounts_created": 0,
        },
        "assignment_rows": assignment_rows,
        "next_packets": next_packets,
        "next_packet": next_packets[0]["packet_id"]
        if next_packets
        else "PCKT-DOMAIN-WEAVER-LIMITED-WATCH-MATRIX-REFRESH-V0_2",
        "request_files_mutated": False,
        "replacement_requests_written": 0,
        "mounts_created": 0,
        "codex_queue_run_started": False,
        "actual_spawn_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
        "candidate_context_graph_deltas": graph_deltas,
        "source_evidence": [
            reissue_ref,
            _evidence_ref(root, "ION/05_context/current/codex_agent_mounts"),
            _evidence_ref(root, DEFAULT_QUEUE_GOVERNANCE_DIR.as_posix()),
        ],
        "non_claims": [
            *NON_CLAIMS,
            "Assignment rows are candidate bindings only and do not write replacement queue requests.",
            "Generated-mount-required rows have proposed identities but no new mount has been created by this packet.",
            "Supersede/quarantine rows remain review recommendations, not lifecycle-ledger writes.",
        ],
    }


def write_queue_metadata_identity_assignment(
    active_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    generated_at: str | None = None,
    write_receipt: bool = True,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    assignment = build_queue_metadata_identity_assignment(
        root,
        generated_at=generated_at,
    )
    out_dir = _resolve_output_dir(root, output_dir or DEFAULT_QUEUE_GOVERNANCE_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    assignment_path = out_dir / DEFAULT_QUEUE_METADATA_IDENTITY_ASSIGNMENT_NAME
    report_path = out_dir / DEFAULT_QUEUE_METADATA_IDENTITY_ASSIGNMENT_REPORT_NAME
    deltas_path = out_dir / DEFAULT_QUEUE_METADATA_IDENTITY_ASSIGNMENT_DELTAS_NAME
    assignment_text = _stable_json(assignment)
    report_text = render_queue_metadata_identity_assignment_report(assignment)
    deltas_text = _stable_json(dict(assignment["candidate_context_graph_deltas"]))
    assignment_path.write_text(assignment_text, encoding="utf-8")
    report_path.write_text(report_text, encoding="utf-8")
    deltas_path.write_text(deltas_text, encoding="utf-8")

    result = {
        "schema_id": QUEUE_METADATA_IDENTITY_ASSIGNMENT_WRITE_RESULT_SCHEMA_ID,
        "generated_at": assignment["generated_at"],
        "active_root": str(root),
        "verdict": assignment["verdict"],
        "assignment_path": _rel(root, assignment_path),
        "assignment_sha256": _sha256_text(assignment_text),
        "report_path": _rel(root, report_path),
        "report_sha256": _sha256_text(report_text),
        "context_graph_delta_path": _rel(root, deltas_path),
        "context_graph_delta_sha256": _sha256_text(deltas_text),
        "assignment_row_count": assignment["summary"]["assignment_row_count"],
        "existing_mount_assignment_ready_count": assignment["summary"][
            "existing_mount_assignment_ready_count"
        ],
        "apply_review_ready_count": assignment["summary"]["apply_review_ready_count"],
        "source_safety_blocked_count": assignment["summary"]["source_safety_blocked_count"],
        "generated_mount_required_count": assignment["summary"][
            "generated_mount_required_count"
        ],
        "supersede_or_quarantine_recommended_count": assignment["summary"][
            "supersede_or_quarantine_recommended_count"
        ],
        "next_packet": assignment["next_packet"],
        "request_files_mutated": False,
        "replacement_requests_written": 0,
        "mounts_created": 0,
        "codex_queue_run_started": False,
        "authority": AUTHORITY,
    }
    if write_receipt:
        result["operator_receipt_path"] = write_queue_metadata_identity_assignment_operator_receipt(
            root,
            result,
            assignment,
        )
    return result


def build_stale_non_domain_queue_quarantine_settlement(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
    source_assignment: Mapping[str, Any] | None = None,
    settlement_decision: str = "quarantine_as_stale_external_non_domain",
) -> dict[str, Any]:
    """Build a candidate quarantine settlement for stale non-Domain-Weaver rows."""

    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    assignment, assignment_ref = _load_metadata_assignment_or_build(
        root,
        generated_at=generated,
        source_assignment=source_assignment,
    )
    quarantine_rows = [
        row
        for row in list(assignment.get("assignment_rows") or [])
        if isinstance(row, Mapping)
        and row.get("assignment_disposition") == "supersede_or_quarantine_recommended"
    ]
    settlement_rows = [
        _stale_non_domain_quarantine_settlement_row(
            root,
            row,
            settlement_decision=settlement_decision,
        )
        for row in quarantine_rows
    ]
    blocked_rows = [
        row for row in settlement_rows if not row.get("settlement_ready")
    ]
    graph_deltas = _stale_non_domain_quarantine_settlement_graph_deltas(
        root,
        generated_at=generated,
        settlement_rows=settlement_rows,
        assignment_ref=assignment_ref,
    )
    if not settlement_rows:
        verdict = "STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_NO_ROWS"
    elif blocked_rows:
        verdict = "STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_BLOCKED"
    else:
        verdict = "STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_READY"
    next_packets = _stale_non_domain_quarantine_settlement_next_packets(
        settlement_rows=settlement_rows,
        blocked_rows=blocked_rows,
    )
    return {
        "schema_id": STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "stale_non_domain_queue_quarantine_settlement_candidate_built",
        "verdict": verdict,
        "source_assignment": assignment_ref,
        "source_assignment_verdict": assignment.get("verdict"),
        "source_assignment_generated_at": assignment.get("generated_at"),
        "settlement_decision": settlement_decision,
        "summary": {
            "settlement_row_count": len(settlement_rows),
            "settlement_ready_count": len(settlement_rows) - len(blocked_rows),
            "blocked_row_count": len(blocked_rows),
            "candidate_quarantine_settlement_written": False,
            "source_request_files_mutated": False,
            "replacement_request_files_written": 0,
            "codex_queue_run_started": False,
            "accepted_state_claimed": False,
            "graph_delta_claim_count": len(graph_deltas["upsert_claims"]),
        },
        "settlement_rows": settlement_rows,
        "blocked_rows": blocked_rows,
        "next_packets": next_packets,
        "next_packet": next_packets[0]["packet_id"]
        if next_packets
        else "PCKT-DOMAIN-WEAVER-LIMITED-WATCH-MATRIX-REFRESH-V0_2",
        "candidate_quarantine_settlement_written": False,
        "source_request_files_mutated": False,
        "replacement_request_files_written": 0,
        "codex_queue_run_started": False,
        "actual_spawn_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
        "candidate_context_graph_deltas": graph_deltas,
        "source_evidence": [
            assignment_ref,
            _evidence_ref(root, CODEX_WORK_REQUESTS_DIR.as_posix()),
            _evidence_ref(root, DEFAULT_QUEUE_GOVERNANCE_DIR.as_posix()),
        ],
        "non_claims": [
            *NON_CLAIMS,
            "Stale non-domain quarantine settlement writes a candidate quarantine ledger only.",
            "The old desktop-rescue source request file is not mutated or deleted.",
            "The queue runner is not started and the stale external request must not be run broadly.",
            "This does not claim accepted lifecycle state or production readiness.",
        ],
    }


def write_stale_non_domain_queue_quarantine_settlement(
    active_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    generated_at: str | None = None,
    source_assignment: Mapping[str, Any] | None = None,
    settlement_decision: str = "quarantine_as_stale_external_non_domain",
    confirmation: str | None = None,
    write_receipt: bool = True,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    if confirmation != STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_CONFIRMATION:
        result = {
            "schema_id": STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_WRITE_RESULT_SCHEMA_ID,
            "generated_at": _utc_now(),
            "active_root": str(root),
            "ok": False,
            "verdict": "STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_CONFIRMATION_REQUIRED",
            "required_confirmation": STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_CONFIRMATION,
            "provided_confirmation": confirmation,
            "settlement_path": None,
            "settlement_row_count": 0,
            "candidate_quarantine_settlement_written": False,
            "source_request_files_mutated": False,
            "replacement_request_files_written": 0,
            "codex_queue_run_started": False,
            "authority": AUTHORITY,
        }
        if write_receipt:
            result["operator_receipt_path"] = (
                write_stale_non_domain_queue_quarantine_settlement_operator_receipt(
                    root,
                    result,
                    None,
                )
            )
        return result
    settlement = build_stale_non_domain_queue_quarantine_settlement(
        root,
        generated_at=generated_at,
        source_assignment=source_assignment,
        settlement_decision=settlement_decision,
    )
    if settlement["verdict"] != "STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_READY":
        result = {
            "schema_id": STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_WRITE_RESULT_SCHEMA_ID,
            "generated_at": settlement["generated_at"],
            "active_root": str(root),
            "ok": False,
            "verdict": settlement["verdict"],
            "blocked_rows": settlement.get("blocked_rows", []),
            "settlement_row_count": settlement["summary"]["settlement_row_count"],
            "candidate_quarantine_settlement_written": False,
            "source_request_files_mutated": False,
            "replacement_request_files_written": 0,
            "codex_queue_run_started": False,
            "authority": AUTHORITY,
        }
        if write_receipt:
            result["operator_receipt_path"] = (
                write_stale_non_domain_queue_quarantine_settlement_operator_receipt(
                    root,
                    result,
                    settlement,
                )
            )
        return result
    out_dir = _resolve_output_dir(root, output_dir or DEFAULT_QUEUE_GOVERNANCE_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    settlement["verdict"] = "STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_WRITTEN"
    settlement["candidate_quarantine_settlement_written"] = True
    settlement["summary"]["candidate_quarantine_settlement_written"] = True
    settlement["candidate_context_graph_deltas"] = (
        _stale_non_domain_quarantine_settlement_graph_deltas(
            root,
            generated_at=str(settlement["generated_at"]),
            settlement_rows=list(settlement.get("settlement_rows") or []),
            assignment_ref=_mapping(settlement.get("source_assignment")),
            write_performed=True,
        )
    )
    settlement_path = out_dir / DEFAULT_STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_NAME
    report_path = out_dir / DEFAULT_STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_REPORT_NAME
    deltas_path = out_dir / DEFAULT_STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_DELTAS_NAME
    settlement_text = _stable_json(settlement)
    report_text = render_stale_non_domain_queue_quarantine_settlement_report(settlement)
    deltas_text = _stable_json(dict(settlement["candidate_context_graph_deltas"]))
    settlement_path.write_text(settlement_text, encoding="utf-8")
    report_path.write_text(report_text, encoding="utf-8")
    deltas_path.write_text(deltas_text, encoding="utf-8")
    result = {
        "schema_id": STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_WRITE_RESULT_SCHEMA_ID,
        "generated_at": settlement["generated_at"],
        "active_root": str(root),
        "ok": True,
        "verdict": "STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_WRITTEN",
        "settlement_path": _rel(root, settlement_path),
        "settlement_sha256": _sha256_text(settlement_text),
        "report_path": _rel(root, report_path),
        "report_sha256": _sha256_text(report_text),
        "context_graph_delta_path": _rel(root, deltas_path),
        "context_graph_delta_sha256": _sha256_text(deltas_text),
        "settlement_row_count": settlement["summary"]["settlement_row_count"],
        "settlement_ready_count": settlement["summary"]["settlement_ready_count"],
        "candidate_quarantine_settlement_written": True,
        "source_request_files_mutated": False,
        "replacement_request_files_written": 0,
        "codex_queue_run_started": False,
        "next_packet": settlement["next_packet"],
        "authority": AUTHORITY,
    }
    if write_receipt:
        result["operator_receipt_path"] = (
            write_stale_non_domain_queue_quarantine_settlement_operator_receipt(
                root,
                result,
                settlement,
            )
        )
    return result


def build_queue_metadata_identity_reissue_apply_review(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
    source_assignment: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build candidate replacement bodies for assignment-ready metadata rows."""

    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    assignment, assignment_ref = _load_metadata_assignment_or_build(
        root,
        generated_at=generated,
        source_assignment=source_assignment,
    )
    ready_rows = [
        row
        for row in list(assignment.get("assignment_rows") or [])
        if isinstance(row, Mapping) and row.get("candidate_reissue_apply_review_ready")
    ]
    excluded_rows = [
        row
        for row in list(assignment.get("assignment_rows") or [])
        if isinstance(row, Mapping) and not row.get("candidate_reissue_apply_review_ready")
    ]
    apply_rows = [
        _metadata_reissue_apply_review_row(
            root,
            row,
            generated_at=generated,
        )
        for row in ready_rows
    ]
    graph_deltas = _queue_metadata_identity_reissue_apply_review_graph_deltas(
        root,
        generated_at=generated,
        apply_rows=apply_rows,
        source_assignment_ref=assignment_ref,
    )
    ready_count = sum(1 for row in apply_rows if row.get("apply_candidate_ready"))
    verdict = (
        "QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_READY"
        if ready_count
        else "QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_NO_READY_ROWS"
    )
    next_packets = _metadata_reissue_apply_review_next_packets(
        ready_count=ready_count,
        excluded_rows=excluded_rows,
    )
    return {
        "schema_id": QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "queue_metadata_identity_reissue_apply_review_candidate_built",
        "verdict": verdict,
        "source_assignment": assignment_ref,
        "source_assignment_verdict": assignment.get("verdict"),
        "source_assignment_generated_at": assignment.get("generated_at"),
        "source_assignment_is_latest_file": bool(assignment_ref.get("path")),
        "summary": {
            "apply_review_row_count": len(apply_rows),
            "apply_candidate_ready_count": ready_count,
            "excluded_assignment_row_count": len(excluded_rows),
            "candidate_replacement_body_count": len(apply_rows),
            "candidate_body_files_intended": len(apply_rows),
            "replacement_request_files_written": 0,
            "source_request_files_mutated": False,
            "codex_queue_run_started": False,
            "graph_delta_claim_count": len(graph_deltas["upsert_claims"]),
        },
        "apply_review_rows": apply_rows,
        "excluded_assignment_rows": [
            {
                "source_request_id": row.get("source_request_id"),
                "assignment_disposition": row.get("assignment_disposition"),
                "next_packet": row.get("next_packet"),
            }
            for row in excluded_rows
        ],
        "next_packets": next_packets,
        "next_packet": next_packets[0]["packet_id"]
        if next_packets
        else "PCKT-DOMAIN-WEAVER-LIMITED-WATCH-MATRIX-REFRESH-V0_2",
        "request_files_mutated": False,
        "replacement_request_files_written": 0,
        "candidate_body_files_written": 0,
        "codex_queue_run_started": False,
        "actual_spawn_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
        "candidate_context_graph_deltas": graph_deltas,
        "source_evidence": [
            assignment_ref,
            _evidence_ref(root, CODEX_WORK_REQUESTS_DIR.as_posix()),
            _evidence_ref(root, "ION/05_context/current/codex_agent_mounts"),
        ],
        "non_claims": [
            *NON_CLAIMS,
            "Apply-review rows are candidate replacement bodies only, not queue request writes.",
            "Future apply must verify source_request_sha256 and candidate_replacement_body_sha256 before writing any new exact request path.",
            "General queue processing remains blocked; any future run must be exact-request-path only.",
        ],
    }


def write_queue_metadata_identity_reissue_apply_review(
    active_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    generated_at: str | None = None,
    write_receipt: bool = True,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    review = build_queue_metadata_identity_reissue_apply_review(
        root,
        generated_at=generated_at,
    )
    out_dir = _resolve_output_dir(root, output_dir or DEFAULT_QUEUE_GOVERNANCE_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    body_dir = out_dir / DEFAULT_QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_BODY_DIR_NAME
    body_dir.mkdir(parents=True, exist_ok=True)

    for row in list(review.get("apply_review_rows") or []):
        if not isinstance(row, dict):
            continue
        body = _mapping(row.get("candidate_replacement_body"))
        body_text = _stable_json(body)
        body_path = body_dir / str(row.get("candidate_body_filename") or "body.candidate.json")
        body_path.write_text(body_text, encoding="utf-8")
        row["candidate_replacement_body_path"] = _rel(root, body_path)
        row["candidate_replacement_body_file_sha256"] = _sha256_text(body_text)

    review["candidate_body_files_written"] = len(list(review.get("apply_review_rows") or []))
    review["summary"]["candidate_body_files_written"] = review["candidate_body_files_written"]
    review["candidate_context_graph_deltas"] = _queue_metadata_identity_reissue_apply_review_graph_deltas(
        root,
        generated_at=str(review["generated_at"]),
        apply_rows=list(review.get("apply_review_rows") or []),
        source_assignment_ref=_mapping(review.get("source_assignment")),
    )
    review["summary"]["graph_delta_claim_count"] = len(
        review["candidate_context_graph_deltas"]["upsert_claims"]
    )

    review_path = out_dir / DEFAULT_QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_NAME
    report_path = out_dir / DEFAULT_QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_REPORT_NAME
    deltas_path = out_dir / DEFAULT_QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_DELTAS_NAME
    review_text = _stable_json(review)
    report_text = render_queue_metadata_identity_reissue_apply_review_report(review)
    deltas_text = _stable_json(dict(review["candidate_context_graph_deltas"]))
    review_path.write_text(review_text, encoding="utf-8")
    report_path.write_text(report_text, encoding="utf-8")
    deltas_path.write_text(deltas_text, encoding="utf-8")

    result = {
        "schema_id": QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_WRITE_RESULT_SCHEMA_ID,
        "generated_at": review["generated_at"],
        "active_root": str(root),
        "verdict": review["verdict"],
        "review_path": _rel(root, review_path),
        "review_sha256": _sha256_text(review_text),
        "report_path": _rel(root, report_path),
        "report_sha256": _sha256_text(report_text),
        "context_graph_delta_path": _rel(root, deltas_path),
        "context_graph_delta_sha256": _sha256_text(deltas_text),
        "candidate_body_files_written": review["candidate_body_files_written"],
        "apply_review_row_count": review["summary"]["apply_review_row_count"],
        "apply_candidate_ready_count": review["summary"]["apply_candidate_ready_count"],
        "replacement_request_files_written": 0,
        "source_request_files_mutated": False,
        "codex_queue_run_started": False,
        "next_packet": review["next_packet"],
        "authority": AUTHORITY,
    }
    if write_receipt:
        result["operator_receipt_path"] = write_queue_metadata_identity_reissue_apply_review_operator_receipt(
            root,
            result,
            review,
        )
    return result


def apply_queue_metadata_identity_reissue_apply_review(
    active_root: str | Path,
    *,
    confirmation: str | None = None,
    review: Mapping[str, Any] | None = None,
    source_request_id: str | None = None,
    allow_existing_target: bool = False,
    write_receipt: bool = True,
) -> dict[str, Any]:
    """Write reviewed metadata-reissue replacement requests behind exact hash gates."""

    root = _require_active_root(active_root)
    loaded_review, review_ref = _load_metadata_apply_review_or_build(root, review=review)
    if confirmation != QUEUE_METADATA_IDENTITY_REISSUE_APPLY_CONFIRMATION:
        result = {
            "schema_id": QUEUE_METADATA_IDENTITY_REISSUE_APPLY_RESULT_SCHEMA_ID,
            "generated_at": _utc_now(),
            "active_root": str(root),
            "ok": False,
            "result": "QUEUE_METADATA_IDENTITY_REISSUE_APPLY_BLOCKED_CONFIRMATION_REQUIRED",
            "required_confirmation": QUEUE_METADATA_IDENTITY_REISSUE_APPLY_CONFIRMATION,
            "provided_confirmation": confirmation,
            "review": review_ref,
            "writes": [],
            "replacement_request_files_written": 0,
            "source_request_files_mutated": False,
            "codex_queue_run_started": False,
            "accepted_state_claimed": False,
            "authority": AUTHORITY,
        }
        if write_receipt:
            result["operator_receipt_path"] = (
                write_queue_metadata_identity_reissue_apply_operator_receipt(root, result)
            )
        return result

    rows = [
        row
        for row in list(loaded_review.get("apply_review_rows") or [])
        if isinstance(row, Mapping)
        and row.get("apply_candidate_ready")
        and (not source_request_id or row.get("source_request_id") == source_request_id)
    ]
    writes: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    for row in rows:
        prepared = _prepare_metadata_identity_reissue_apply_row(
            root,
            row,
            allow_existing_target=allow_existing_target,
        )
        if prepared.get("ok"):
            writes.append(prepared)
        else:
            blockers.append(prepared)
    if blockers:
        result = {
            "schema_id": QUEUE_METADATA_IDENTITY_REISSUE_APPLY_RESULT_SCHEMA_ID,
            "generated_at": _utc_now(),
            "active_root": str(root),
            "ok": False,
            "result": "QUEUE_METADATA_IDENTITY_REISSUE_APPLY_BLOCKED_BY_PRECHECK",
            "review": review_ref,
            "blockers": blockers,
            "writes": [],
            "replacement_request_files_written": 0,
            "source_request_files_mutated": False,
            "codex_queue_run_started": False,
            "accepted_state_claimed": False,
            "authority": AUTHORITY,
        }
        if write_receipt:
            result["operator_receipt_path"] = (
                write_queue_metadata_identity_reissue_apply_operator_receipt(root, result)
            )
        return result
    for prepared in writes:
        target_path = root / str(prepared["candidate_replacement_request_path"])
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(str(prepared["candidate_replacement_body_text"]), encoding="utf-8")
        prepared["write_performed"] = True
        prepared["written_ref"] = _file_ref(root, target_path)
    result = {
        "schema_id": QUEUE_METADATA_IDENTITY_REISSUE_APPLY_RESULT_SCHEMA_ID,
        "generated_at": _utc_now(),
        "active_root": str(root),
        "ok": True,
        "result": "QUEUE_METADATA_IDENTITY_REISSUE_APPLY_WRITTEN",
        "review": review_ref,
        "writes": [
            {
                key: value
                for key, value in prepared.items()
                if key != "candidate_replacement_body_text"
            }
            for prepared in writes
        ],
        "replacement_request_files_written": len(writes),
        "source_request_files_mutated": False,
        "codex_queue_run_started": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
        "non_claims": [
            *NON_CLAIMS,
            "Metadata identity reissue apply writes only exact replacement request paths after hash checks.",
            "The source request files are not mutated by this apply.",
            "The queue runner is not started by this apply; general queue processing remains blocked.",
            "Replacement requests remain queued candidate carrier work until exact-request dispatch and fan-in proof.",
        ],
    }
    if write_receipt:
        result["operator_receipt_path"] = (
            write_queue_metadata_identity_reissue_apply_operator_receipt(root, result)
        )
    return result


def build_queue_metadata_source_safety_review(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
    source_assignment: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Review assignment rows blocked by source lifecycle or context-gate safety."""

    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    assignment, assignment_ref = _load_metadata_assignment_or_build(
        root,
        generated_at=generated,
        source_assignment=source_assignment,
    )
    assignment_rows = [
        row
        for row in list(assignment.get("assignment_rows") or [])
        if isinstance(row, Mapping)
    ]
    blocked_assignment_rows = [
        row
        for row in assignment_rows
        if row.get("assignment_disposition") == "existing_mount_assignment_ready"
        and not row.get("candidate_reissue_apply_review_ready")
        and _source_safety_blockers(row)
    ]
    blocked_row_ids = {id(row) for row in blocked_assignment_rows}
    review_rows = [
        _metadata_source_safety_review_row(root, row)
        for row in blocked_assignment_rows
    ]
    excluded_rows = [
        {
            "source_request_id": row.get("source_request_id"),
            "assignment_disposition": row.get("assignment_disposition"),
            "candidate_reissue_apply_review_ready": bool(
                row.get("candidate_reissue_apply_review_ready")
            ),
            "next_packet": row.get("next_packet"),
        }
        for row in assignment_rows
        if id(row) not in blocked_row_ids
    ]
    blocker_counts = _metadata_source_safety_blocker_counts(review_rows)
    required_packet_counts = _metadata_source_safety_required_packet_counts(review_rows)
    graph_deltas = _queue_metadata_source_safety_review_graph_deltas(
        root,
        generated_at=generated,
        review_rows=review_rows,
        source_assignment_ref=assignment_ref,
    )
    verdict = (
        "QUEUE_METADATA_SOURCE_SAFETY_REVIEW_BLOCKERS_ACTIVE"
        if review_rows
        else "QUEUE_METADATA_SOURCE_SAFETY_REVIEW_NO_BLOCKERS"
    )
    next_packets = _metadata_source_safety_review_next_packets(
        review_rows=review_rows,
        assignment_summary=_mapping(assignment.get("summary")),
    )
    return {
        "schema_id": QUEUE_METADATA_SOURCE_SAFETY_REVIEW_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "queue_metadata_source_safety_review_candidate_built",
        "verdict": verdict,
        "source_assignment": assignment_ref,
        "source_assignment_verdict": assignment.get("verdict"),
        "source_assignment_generated_at": assignment.get("generated_at"),
        "source_assignment_is_latest_file": bool(assignment_ref.get("path")),
        "summary": {
            "source_safety_review_row_count": len(review_rows),
            "excluded_assignment_row_count": len(excluded_rows),
            "context_gate_blocked_count": blocker_counts.get(
                "source_context_gate_requires_dedicated_reissue_packet",
                0,
            ),
            "stale_lifecycle_blocked_count": blocker_counts.get(
                "source_lifecycle_stale_waiting_requires_reconciliation",
                0,
            ),
            "terminal_lifecycle_blocked_count": blocker_counts.get(
                "source_terminal_lifecycle_requires_classification",
                0,
            ),
            "lineage_proof_missing_count": sum(
                1
                for row in review_rows
                if not row.get("candidate_identity_lineage_proven")
            ),
            "required_packet_counts": required_packet_counts,
            "blocker_code_counts": blocker_counts,
            "apply_review_rows_unblocked": 0,
            "source_request_files_mutated": False,
            "replacement_request_files_written": 0,
            "codex_queue_run_started": False,
            "graph_delta_claim_count": len(graph_deltas["upsert_claims"]),
        },
        "source_safety_review_rows": review_rows,
        "excluded_assignment_rows": excluded_rows,
        "next_packets": next_packets,
        "next_packet": next_packets[0]["packet_id"]
        if next_packets
        else "PCKT-DOMAIN-WEAVER-LIMITED-WATCH-MATRIX-REFRESH-V0_2",
        "request_files_mutated": False,
        "replacement_request_files_written": 0,
        "apply_review_rows_unblocked": 0,
        "codex_queue_run_started": False,
        "actual_spawn_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
        "candidate_context_graph_deltas": graph_deltas,
        "source_evidence": [
            assignment_ref,
            _evidence_ref(root, CODEX_WORK_REQUESTS_DIR.as_posix()),
            _evidence_ref(root, DEFAULT_QUEUE_GOVERNANCE_DIR.as_posix()),
        ],
        "non_claims": [
            *NON_CLAIMS,
            "Source-safety review classifies context-gate and lifecycle blockers only; it does not unblock apply review.",
            "Context-gate rows require a dedicated context-gate reissue or fresh context proof packet before metadata replacement bodies.",
            "Stale lifecycle rows require reconciliation, supersession, or explicit preservation before metadata replacement bodies.",
            "Working capsule identity readiness is mount-bound posture evidence, not lineage proof.",
        ],
    }


def write_queue_metadata_source_safety_review(
    active_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    generated_at: str | None = None,
    write_receipt: bool = True,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    review = build_queue_metadata_source_safety_review(
        root,
        generated_at=generated_at,
    )
    out_dir = _resolve_output_dir(root, output_dir or DEFAULT_QUEUE_GOVERNANCE_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    review_path = out_dir / DEFAULT_QUEUE_METADATA_SOURCE_SAFETY_REVIEW_NAME
    report_path = out_dir / DEFAULT_QUEUE_METADATA_SOURCE_SAFETY_REVIEW_REPORT_NAME
    deltas_path = out_dir / DEFAULT_QUEUE_METADATA_SOURCE_SAFETY_REVIEW_DELTAS_NAME
    review_text = _stable_json(review)
    report_text = render_queue_metadata_source_safety_review_report(review)
    deltas_text = _stable_json(dict(review["candidate_context_graph_deltas"]))
    review_path.write_text(review_text, encoding="utf-8")
    report_path.write_text(report_text, encoding="utf-8")
    deltas_path.write_text(deltas_text, encoding="utf-8")

    result = {
        "schema_id": QUEUE_METADATA_SOURCE_SAFETY_REVIEW_WRITE_RESULT_SCHEMA_ID,
        "generated_at": review["generated_at"],
        "active_root": str(root),
        "verdict": review["verdict"],
        "review_path": _rel(root, review_path),
        "review_sha256": _sha256_text(review_text),
        "report_path": _rel(root, report_path),
        "report_sha256": _sha256_text(report_text),
        "context_graph_delta_path": _rel(root, deltas_path),
        "context_graph_delta_sha256": _sha256_text(deltas_text),
        "source_safety_review_row_count": review["summary"][
            "source_safety_review_row_count"
        ],
        "context_gate_blocked_count": review["summary"]["context_gate_blocked_count"],
        "stale_lifecycle_blocked_count": review["summary"][
            "stale_lifecycle_blocked_count"
        ],
        "terminal_lifecycle_blocked_count": review["summary"][
            "terminal_lifecycle_blocked_count"
        ],
        "apply_review_rows_unblocked": 0,
        "replacement_request_files_written": 0,
        "source_request_files_mutated": False,
        "codex_queue_run_started": False,
        "next_packet": review["next_packet"],
        "authority": AUTHORITY,
    }
    if write_receipt:
        result["operator_receipt_path"] = write_queue_metadata_source_safety_review_operator_receipt(
            root,
            result,
            review,
        )
    return result


def build_context_gate_blocked_request_reissue(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
    source_safety_review: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build candidate exact replacement bodies for context-gate blocked rows."""

    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    source_review, source_review_ref = _load_source_safety_review_or_build(
        root,
        generated_at=generated,
        source_safety_review=source_safety_review,
    )
    source_rows = [
        row
        for row in list(source_review.get("source_safety_review_rows") or [])
        if isinstance(row, Mapping)
    ]
    context_gate_rows = [
        row
        for row in source_rows
        if "source_context_gate_requires_dedicated_reissue_packet"
        in set(str(code or "") for code in list(row.get("blocker_codes") or []))
    ]
    context_gate_row_ids = {id(row) for row in context_gate_rows}
    reissue_rows = [
        _context_gate_reissue_review_row(root, row, generated_at=generated)
        for row in context_gate_rows
    ]
    excluded_rows = [
        {
            "source_request_id": row.get("source_request_id"),
            "blocker_codes": list(row.get("blocker_codes") or []),
            "required_packets": list(row.get("required_packets") or []),
            "review_disposition": row.get("review_disposition"),
        }
        for row in source_rows
        if id(row) not in context_gate_row_ids
    ]
    ready_count = sum(1 for row in reissue_rows if row.get("candidate_body_ready"))
    graph_deltas = _context_gate_blocked_request_reissue_graph_deltas(
        root,
        generated_at=generated,
        reissue_rows=reissue_rows,
        source_review_ref=source_review_ref,
    )
    verdict = (
        "CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_CANDIDATE_BODIES_READY"
        if ready_count
        else "CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_NO_READY_ROWS"
    )
    next_packets = _context_gate_blocked_request_reissue_next_packets(
        ready_count=ready_count,
        source_review=_mapping(source_review),
    )
    return {
        "schema_id": CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "context_gate_blocked_request_reissue_candidate_built",
        "verdict": verdict,
        "source_safety_review": source_review_ref,
        "source_safety_review_verdict": source_review.get("verdict"),
        "source_safety_review_generated_at": source_review.get("generated_at"),
        "source_safety_review_is_latest_file": bool(source_review_ref.get("path")),
        "summary": {
            "context_gate_reissue_row_count": len(reissue_rows),
            "candidate_body_ready_count": ready_count,
            "candidate_replacement_body_count": len(reissue_rows),
            "candidate_body_files_intended": len(reissue_rows),
            "candidate_body_files_written": 0,
            "excluded_source_safety_row_count": len(excluded_rows),
            "replacement_request_files_written": 0,
            "source_request_files_mutated": False,
            "codex_queue_run_started": False,
            "graph_delta_claim_count": len(graph_deltas["upsert_claims"]),
        },
        "context_gate_reissue_rows": reissue_rows,
        "excluded_source_safety_rows": excluded_rows,
        "next_packets": next_packets,
        "next_packet": next_packets[0]["packet_id"]
        if next_packets
        else "PCKT-DOMAIN-WEAVER-LIMITED-WATCH-MATRIX-REFRESH-V0_2",
        "request_files_mutated": False,
        "replacement_request_files_written": 0,
        "candidate_body_files_written": 0,
        "codex_queue_run_started": False,
        "actual_spawn_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
        "candidate_context_graph_deltas": graph_deltas,
        "source_evidence": [
            source_review_ref,
            _evidence_ref(root, CODEX_WORK_REQUESTS_DIR.as_posix()),
            _evidence_ref(root, DEFAULT_QUEUE_GOVERNANCE_DIR.as_posix()),
        ],
        "non_claims": [
            *NON_CLAIMS,
            "Context-gate reissue rows are candidate exact replacement bodies only, not queue request writes.",
            "Future apply must verify source_request_sha256 and candidate_replacement_body_sha256 before writing any exact request path.",
            "General queue processing remains blocked; any future run must be exact-request-path only.",
            "This packet repairs missing request identity metadata but does not prove worker execution or autonomous reaction.",
        ],
    }


def write_context_gate_blocked_request_reissue(
    active_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    generated_at: str | None = None,
    write_receipt: bool = True,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    review = build_context_gate_blocked_request_reissue(
        root,
        generated_at=generated_at,
    )
    out_dir = _resolve_output_dir(root, output_dir or DEFAULT_QUEUE_GOVERNANCE_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    body_dir = out_dir / DEFAULT_CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_BODY_DIR_NAME
    body_dir.mkdir(parents=True, exist_ok=True)

    for row in list(review.get("context_gate_reissue_rows") or []):
        if not isinstance(row, dict):
            continue
        body = _mapping(row.get("candidate_replacement_body"))
        body_text = _stable_json(body)
        body_path = body_dir / str(row.get("candidate_body_filename") or "body.candidate.json")
        body_path.write_text(body_text, encoding="utf-8")
        row["candidate_replacement_body_path"] = _rel(root, body_path)
        row["candidate_replacement_body_file_sha256"] = _sha256_text(body_text)

    review["candidate_body_files_written"] = len(
        list(review.get("context_gate_reissue_rows") or [])
    )
    review["summary"]["candidate_body_files_written"] = review[
        "candidate_body_files_written"
    ]
    review["candidate_context_graph_deltas"] = _context_gate_blocked_request_reissue_graph_deltas(
        root,
        generated_at=str(review["generated_at"]),
        reissue_rows=list(review.get("context_gate_reissue_rows") or []),
        source_review_ref=_mapping(review.get("source_safety_review")),
    )
    review["summary"]["graph_delta_claim_count"] = len(
        review["candidate_context_graph_deltas"]["upsert_claims"]
    )

    review_path = out_dir / DEFAULT_CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_NAME
    report_path = out_dir / DEFAULT_CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_REPORT_NAME
    deltas_path = out_dir / DEFAULT_CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_DELTAS_NAME
    review_text = _stable_json(review)
    report_text = render_context_gate_blocked_request_reissue_report(review)
    deltas_text = _stable_json(dict(review["candidate_context_graph_deltas"]))
    review_path.write_text(review_text, encoding="utf-8")
    report_path.write_text(report_text, encoding="utf-8")
    deltas_path.write_text(deltas_text, encoding="utf-8")

    result = {
        "schema_id": CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_WRITE_RESULT_SCHEMA_ID,
        "generated_at": review["generated_at"],
        "active_root": str(root),
        "verdict": review["verdict"],
        "review_path": _rel(root, review_path),
        "review_sha256": _sha256_text(review_text),
        "report_path": _rel(root, report_path),
        "report_sha256": _sha256_text(report_text),
        "context_graph_delta_path": _rel(root, deltas_path),
        "context_graph_delta_sha256": _sha256_text(deltas_text),
        "candidate_body_files_written": review["candidate_body_files_written"],
        "context_gate_reissue_row_count": review["summary"][
            "context_gate_reissue_row_count"
        ],
        "candidate_body_ready_count": review["summary"]["candidate_body_ready_count"],
        "replacement_request_files_written": 0,
        "source_request_files_mutated": False,
        "codex_queue_run_started": False,
        "next_packet": review["next_packet"],
        "authority": AUTHORITY,
    }
    if write_receipt:
        result["operator_receipt_path"] = write_context_gate_blocked_request_reissue_operator_receipt(
            root,
            result,
            review,
        )
    return result


def apply_context_gate_blocked_request_reissue(
    active_root: str | Path,
    *,
    confirmation: str,
    source_request_id: str | None = None,
    review: Mapping[str, Any] | None = None,
    allow_existing_target: bool = False,
    write_receipt: bool = True,
) -> dict[str, Any]:
    """Apply reviewed context-gate reissue bodies to exact new request paths."""

    root = _require_active_root(active_root)
    loaded_review, review_ref = _load_context_gate_reissue_review(root, review=review)
    if confirmation != CONTEXT_GATE_REISSUE_APPLY_CONFIRMATION:
        result = {
            "schema_id": CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_APPLY_RESULT_SCHEMA_ID,
            "generated_at": _utc_now(),
            "active_root": str(root),
            "ok": False,
            "result": "CONTEXT_GATE_REISSUE_APPLY_BLOCKED_CONFIRMATION_REQUIRED",
            "required_confirmation": CONTEXT_GATE_REISSUE_APPLY_CONFIRMATION,
            "provided_confirmation": confirmation,
            "review": review_ref,
            "writes": [],
            "replacement_request_files_written": 0,
            "source_request_files_mutated": False,
            "codex_queue_run_started": False,
            "accepted_state_claimed": False,
            "authority": AUTHORITY,
        }
        if write_receipt:
            result["operator_receipt_path"] = write_context_gate_reissue_apply_operator_receipt(
                root,
                result,
            )
        return result
    rows = [
        row
        for row in list(loaded_review.get("context_gate_reissue_rows") or [])
        if isinstance(row, Mapping)
        and row.get("candidate_body_ready")
        and (not source_request_id or row.get("source_request_id") == source_request_id)
    ]
    writes: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    for row in rows:
        prepared = _prepare_context_gate_reissue_apply_row(
            root,
            row,
            allow_existing_target=allow_existing_target,
        )
        if prepared.get("ok"):
            writes.append(prepared)
        else:
            blockers.append(prepared)
    if blockers:
        result = {
            "schema_id": CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_APPLY_RESULT_SCHEMA_ID,
            "generated_at": _utc_now(),
            "active_root": str(root),
            "ok": False,
            "result": "CONTEXT_GATE_REISSUE_APPLY_BLOCKED_BY_PRECHECK",
            "review": review_ref,
            "blockers": blockers,
            "writes": [],
            "replacement_request_files_written": 0,
            "source_request_files_mutated": False,
            "codex_queue_run_started": False,
            "accepted_state_claimed": False,
            "authority": AUTHORITY,
        }
        if write_receipt:
            result["operator_receipt_path"] = write_context_gate_reissue_apply_operator_receipt(
                root,
                result,
            )
        return result
    for prepared in writes:
        target_path = root / str(prepared["candidate_replacement_request_path"])
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(str(prepared["candidate_replacement_body_text"]), encoding="utf-8")
        prepared["write_performed"] = True
        prepared["written_ref"] = _file_ref(root, target_path)
    result = {
        "schema_id": CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_APPLY_RESULT_SCHEMA_ID,
        "generated_at": _utc_now(),
        "active_root": str(root),
        "ok": True,
        "result": "CONTEXT_GATE_REISSUE_APPLY_WRITTEN",
        "review": review_ref,
        "writes": [
            {
                key: value
                for key, value in prepared.items()
                if key != "candidate_replacement_body_text"
            }
            for prepared in writes
        ],
        "replacement_request_files_written": len(writes),
        "source_request_files_mutated": False,
        "codex_queue_run_started": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
        "non_claims": [
            *NON_CLAIMS,
            "Context-gate apply writes only exact replacement request paths after hash checks.",
            "The source request is not mutated by this apply.",
            "The queue runner is not started by this apply; general queue processing remains blocked.",
        ],
    }
    if write_receipt:
        result["operator_receipt_path"] = write_context_gate_reissue_apply_operator_receipt(
            root,
            result,
        )
    return result


def build_exact_reissue_request_dispatch_readiness(
    active_root: str | Path,
    *,
    request_paths: Sequence[str] | None = None,
    source_runtime_status: Mapping[str, Any] | None = None,
    generated_at: str | None = None,
    max_parallel_lanes: int = 3,
    timeout_seconds: int = 900,
    max_runtime_status_age_seconds: int = 300,
) -> dict[str, Any]:
    """Validate exact reissue request rows before any bounded queue start."""

    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    paths = list(request_paths or _discover_exact_reissue_request_paths(root))
    runtime_status = _exact_reissue_runtime_status(
        root,
        generated_at=generated,
        max_runtime_status_age_seconds=max_runtime_status_age_seconds,
        source_runtime_status=source_runtime_status,
    )
    rows = [
        _exact_reissue_request_readiness_row(
            root,
            path,
            timeout_seconds=timeout_seconds,
        )
        for path in paths
    ]
    ready_rows = [row for row in rows if row.get("dispatch_ready")]
    blocked_rows = [row for row in rows if not row.get("dispatch_ready")]
    dispatch_groups = _exact_reissue_dispatch_groups(
        ready_rows,
        max_parallel_lanes=max_parallel_lanes,
    )
    ready_after_status_refresh = bool(rows) and len(ready_rows) == len(rows)
    ready_for_immediate_exact_start = bool(
        ready_after_status_refresh
        and runtime_status.get("runtime_status_fresh_enough")
        and runtime_status.get("runtime_active_clear")
    )
    if not rows:
        verdict = "EXACT_REISSUE_REQUEST_DISPATCH_NO_ROWS"
    elif blocked_rows:
        verdict = "EXACT_REISSUE_REQUEST_DISPATCH_BLOCKED_BY_REQUEST_PRECHECK"
    elif not ready_for_immediate_exact_start:
        verdict = "EXACT_REISSUE_REQUEST_DISPATCH_READY_AFTER_RUNTIME_STATUS_REFRESH"
    else:
        verdict = "EXACT_REISSUE_REQUEST_DISPATCH_READY"
    graph_deltas = _exact_reissue_request_dispatch_graph_deltas(
        root,
        generated_at=generated,
        rows=rows,
        runtime_status=runtime_status,
        verdict=verdict,
    )
    next_packets = _exact_reissue_request_dispatch_next_packets(
        rows=rows,
        blocked_rows=blocked_rows,
        runtime_status=runtime_status,
        ready_for_immediate_exact_start=ready_for_immediate_exact_start,
    )
    return {
        "schema_id": EXACT_REISSUE_REQUEST_DISPATCH_READINESS_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "exact_reissue_request_dispatch_readiness_built",
        "verdict": verdict,
        "exact_request_path_required": True,
        "general_queue_processing_allowed": False,
        "max_parallel_lanes": max(1, int(max_parallel_lanes)),
        "timeout_seconds": max(1, int(timeout_seconds)),
        "ready_for_staged_exact_dispatch_after_status_refresh": ready_after_status_refresh,
        "ready_for_immediate_exact_start": ready_for_immediate_exact_start,
        "summary": {
            "request_path_count": len(paths),
            "readiness_row_count": len(rows),
            "dispatch_ready_count": len(ready_rows),
            "blocked_row_count": len(blocked_rows),
            "dispatch_group_count": len(dispatch_groups),
            "runtime_status_fresh_enough": bool(
                runtime_status.get("runtime_status_fresh_enough")
            ),
            "runtime_active_clear": bool(runtime_status.get("runtime_active_clear")),
            "codex_queue_run_started": False,
            "actual_spawn_performed": False,
            "accepted_state_claimed": False,
            "graph_delta_claim_count": len(graph_deltas["upsert_claims"]),
        },
        "runtime_status": runtime_status,
        "readiness_rows": rows,
        "blocked_rows": blocked_rows,
        "dispatch_groups": dispatch_groups,
        "start_commands": [
            row["start_command"]
            for row in ready_rows
            if isinstance(row.get("start_command"), str)
        ],
        "status_command": _exact_reissue_status_command(),
        "candidate_context_graph_deltas": graph_deltas,
        "next_packets": next_packets,
        "next_packet": next_packets[0]["packet_id"]
        if next_packets
        else "PCKT-DOMAIN-WEAVER-LIMITED-WATCH-MATRIX-REFRESH-V0_2",
        "codex_queue_run_started": False,
        "actual_spawn_performed": False,
        "source_request_files_mutated": False,
        "replacement_request_files_written": 0,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
        "source_evidence": [
            _evidence_ref(root, CODEX_WORK_REQUESTS_DIR.as_posix()),
            _evidence_ref(root, QUEUE_RUNNER_STATE_PATH.as_posix()),
            _evidence_ref(root, DEFAULT_QUEUE_GOVERNANCE_DIR.as_posix()),
        ],
        "non_claims": [
            *NON_CLAIMS,
            "This packet validates exact context/metadata reissue requests only; it does not use the spawn-dispatch start gate.",
            "Start commands are candidate operator commands and are not executed by this builder.",
            "A fresh queue-runner status check is required before any real exact request-path start.",
            "Each worker return remains carrier intake until fan-in, receipt proof, and lead/Nemesis settlement.",
        ],
    }


def write_exact_reissue_request_dispatch_readiness(
    active_root: str | Path,
    *,
    request_paths: Sequence[str] | None = None,
    source_runtime_status: Mapping[str, Any] | None = None,
    output_dir: str | Path | None = None,
    generated_at: str | None = None,
    max_parallel_lanes: int = 3,
    timeout_seconds: int = 900,
    max_runtime_status_age_seconds: int = 300,
    write_receipt: bool = True,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    readiness = build_exact_reissue_request_dispatch_readiness(
        root,
        request_paths=request_paths,
        source_runtime_status=source_runtime_status,
        generated_at=generated_at,
        max_parallel_lanes=max_parallel_lanes,
        timeout_seconds=timeout_seconds,
        max_runtime_status_age_seconds=max_runtime_status_age_seconds,
    )
    out_dir = _resolve_output_dir(root, output_dir or DEFAULT_QUEUE_GOVERNANCE_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    readiness_path = out_dir / DEFAULT_EXACT_REISSUE_REQUEST_DISPATCH_READINESS_NAME
    report_path = out_dir / DEFAULT_EXACT_REISSUE_REQUEST_DISPATCH_READINESS_REPORT_NAME
    deltas_path = out_dir / DEFAULT_EXACT_REISSUE_REQUEST_DISPATCH_READINESS_DELTAS_NAME
    readiness_text = _stable_json(readiness)
    report_text = render_exact_reissue_request_dispatch_readiness_report(readiness)
    deltas_text = _stable_json(dict(readiness["candidate_context_graph_deltas"]))
    readiness_path.write_text(readiness_text, encoding="utf-8")
    report_path.write_text(report_text, encoding="utf-8")
    deltas_path.write_text(deltas_text, encoding="utf-8")

    result = {
        "schema_id": EXACT_REISSUE_REQUEST_DISPATCH_READINESS_WRITE_RESULT_SCHEMA_ID,
        "generated_at": readiness["generated_at"],
        "active_root": str(root),
        "verdict": readiness["verdict"],
        "readiness_path": _rel(root, readiness_path),
        "readiness_sha256": _sha256_text(readiness_text),
        "report_path": _rel(root, report_path),
        "report_sha256": _sha256_text(report_text),
        "context_graph_delta_path": _rel(root, deltas_path),
        "context_graph_delta_sha256": _sha256_text(deltas_text),
        "request_path_count": readiness["summary"]["request_path_count"],
        "dispatch_ready_count": readiness["summary"]["dispatch_ready_count"],
        "blocked_row_count": readiness["summary"]["blocked_row_count"],
        "ready_for_staged_exact_dispatch_after_status_refresh": readiness[
            "ready_for_staged_exact_dispatch_after_status_refresh"
        ],
        "ready_for_immediate_exact_start": readiness["ready_for_immediate_exact_start"],
        "codex_queue_run_started": False,
        "actual_spawn_performed": False,
        "accepted_state_claimed": False,
        "next_packet": readiness["next_packet"],
        "authority": AUTHORITY,
    }
    if write_receipt:
        result["operator_receipt_path"] = write_exact_reissue_request_dispatch_readiness_operator_receipt(
            root,
            result,
            readiness,
        )
    return result


def build_stale_waiting_reconciliation_review(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
    source_safety_review: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a candidate decision matrix for stale waiting source rows."""

    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    source_review, source_review_ref = _load_source_safety_review_or_build(
        root,
        generated_at=generated,
        source_safety_review=source_safety_review,
    )
    source_rows = [
        row
        for row in list(source_review.get("source_safety_review_rows") or [])
        if isinstance(row, Mapping)
    ]
    stale_rows = [
        row
        for row in source_rows
        if "source_lifecycle_stale_waiting_requires_reconciliation"
        in set(str(code or "") for code in list(row.get("blocker_codes") or []))
    ]
    stale_row_ids = {id(row) for row in stale_rows}
    reconciliation_rows = [
        _stale_waiting_reconciliation_review_row(root, row)
        for row in stale_rows
    ]
    excluded_rows = [
        {
            "source_request_id": row.get("source_request_id"),
            "blocker_codes": list(row.get("blocker_codes") or []),
            "required_packets": list(row.get("required_packets") or []),
            "review_disposition": row.get("review_disposition"),
        }
        for row in source_rows
        if id(row) not in stale_row_ids
    ]
    graph_deltas = _stale_waiting_reconciliation_review_graph_deltas(
        root,
        generated_at=generated,
        reconciliation_rows=reconciliation_rows,
        source_review_ref=source_review_ref,
    )
    verdict = (
        "STALE_WAITING_RECONCILIATION_REVIEW_DECISION_REQUIRED"
        if reconciliation_rows
        else "STALE_WAITING_RECONCILIATION_REVIEW_NO_ROWS"
    )
    next_packets = _stale_waiting_reconciliation_review_next_packets(
        reconciliation_rows=reconciliation_rows,
        source_review=_mapping(source_review),
    )
    return {
        "schema_id": STALE_WAITING_RECONCILIATION_REVIEW_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "stale_waiting_reconciliation_review_candidate_built",
        "verdict": verdict,
        "source_safety_review": source_review_ref,
        "source_safety_review_verdict": source_review.get("verdict"),
        "source_safety_review_generated_at": source_review.get("generated_at"),
        "source_safety_review_is_latest_file": bool(source_review_ref.get("path")),
        "summary": {
            "stale_reconciliation_row_count": len(reconciliation_rows),
            "decision_required_count": len(reconciliation_rows),
            "excluded_source_safety_row_count": len(excluded_rows),
            "lifecycle_ledger_mutated": False,
            "request_files_mutated": False,
            "replacement_request_files_written": 0,
            "codex_queue_run_started": False,
            "graph_delta_claim_count": len(graph_deltas["upsert_claims"]),
        },
        "stale_reconciliation_rows": reconciliation_rows,
        "excluded_source_safety_rows": excluded_rows,
        "next_packets": next_packets,
        "next_packet": next_packets[0]["packet_id"]
        if next_packets
        else "PCKT-DOMAIN-WEAVER-LIMITED-WATCH-MATRIX-REFRESH-V0_2",
        "lifecycle_ledger_mutated": False,
        "request_files_mutated": False,
        "replacement_request_files_written": 0,
        "codex_queue_run_started": False,
        "actual_spawn_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
        "candidate_context_graph_deltas": graph_deltas,
        "source_evidence": [
            source_review_ref,
            _evidence_ref(root, CODEX_WORK_REQUESTS_DIR.as_posix()),
            _evidence_ref(root, DEFAULT_QUEUE_GOVERNANCE_DIR.as_posix()),
        ],
        "non_claims": [
            *NON_CLAIMS,
            "Stale waiting reconciliation review is a decision matrix only, not lifecycle settlement.",
            "No lifecycle ledger, source request, replacement request, or queue runner state is mutated by this packet.",
            "A future settlement packet must choose preserve, supersede, or quarantine with exact source hash evidence.",
            "Stale worker returns remain carrier intake only until lead/Nemesis fan-in accepts them.",
        ],
    }


def write_stale_waiting_reconciliation_review(
    active_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    generated_at: str | None = None,
    write_receipt: bool = True,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    review = build_stale_waiting_reconciliation_review(
        root,
        generated_at=generated_at,
    )
    out_dir = _resolve_output_dir(root, output_dir or DEFAULT_QUEUE_GOVERNANCE_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    review_path = out_dir / DEFAULT_STALE_WAITING_RECONCILIATION_REVIEW_NAME
    report_path = out_dir / DEFAULT_STALE_WAITING_RECONCILIATION_REVIEW_REPORT_NAME
    deltas_path = out_dir / DEFAULT_STALE_WAITING_RECONCILIATION_REVIEW_DELTAS_NAME
    review_text = _stable_json(review)
    report_text = render_stale_waiting_reconciliation_review_report(review)
    deltas_text = _stable_json(dict(review["candidate_context_graph_deltas"]))
    review_path.write_text(review_text, encoding="utf-8")
    report_path.write_text(report_text, encoding="utf-8")
    deltas_path.write_text(deltas_text, encoding="utf-8")

    result = {
        "schema_id": STALE_WAITING_RECONCILIATION_REVIEW_WRITE_RESULT_SCHEMA_ID,
        "generated_at": review["generated_at"],
        "active_root": str(root),
        "verdict": review["verdict"],
        "review_path": _rel(root, review_path),
        "review_sha256": _sha256_text(review_text),
        "report_path": _rel(root, report_path),
        "report_sha256": _sha256_text(report_text),
        "context_graph_delta_path": _rel(root, deltas_path),
        "context_graph_delta_sha256": _sha256_text(deltas_text),
        "stale_reconciliation_row_count": review["summary"][
            "stale_reconciliation_row_count"
        ],
        "decision_required_count": review["summary"]["decision_required_count"],
        "lifecycle_ledger_mutated": False,
        "request_files_mutated": False,
        "replacement_request_files_written": 0,
        "codex_queue_run_started": False,
        "next_packet": review["next_packet"],
        "authority": AUTHORITY,
    }
    if write_receipt:
        result["operator_receipt_path"] = write_stale_waiting_reconciliation_review_operator_receipt(
            root,
            result,
            review,
        )
    return result


def build_stale_waiting_reconciliation_settlement(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
    review: Mapping[str, Any] | None = None,
    settlement_decision: str = "supersede_with_fresh_exact_request",
) -> dict[str, Any]:
    """Build a bounded candidate settlement for stale waiting source rows."""

    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    loaded_review, review_ref = _load_stale_waiting_reconciliation_review_or_build(
        root,
        generated_at=generated,
        review=review,
    )
    review_rows = [
        row
        for row in list(loaded_review.get("stale_reconciliation_rows") or [])
        if isinstance(row, Mapping)
    ]
    settlement_rows = [
        _stale_waiting_settlement_row(
            root,
            row,
            settlement_decision=settlement_decision,
        )
        for row in review_rows
    ]
    blocked_rows = [
        row for row in settlement_rows if not row.get("settlement_ready")
    ]
    graph_deltas = _stale_waiting_reconciliation_settlement_graph_deltas(
        root,
        generated_at=generated,
        settlement_rows=settlement_rows,
        review_ref=review_ref,
    )
    if not settlement_rows:
        verdict = "STALE_WAITING_RECONCILIATION_SETTLEMENT_NO_ROWS"
    elif blocked_rows:
        verdict = "STALE_WAITING_RECONCILIATION_SETTLEMENT_BLOCKED"
    else:
        verdict = "STALE_WAITING_RECONCILIATION_SETTLEMENT_READY"
    next_packets = _stale_waiting_reconciliation_settlement_next_packets(
        settlement_rows=settlement_rows,
        blocked_rows=blocked_rows,
    )
    return {
        "schema_id": STALE_WAITING_RECONCILIATION_SETTLEMENT_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "stale_waiting_reconciliation_settlement_candidate_built",
        "verdict": verdict,
        "source_review": review_ref,
        "source_review_verdict": loaded_review.get("verdict"),
        "source_review_generated_at": loaded_review.get("generated_at"),
        "settlement_decision": settlement_decision,
        "summary": {
            "settlement_row_count": len(settlement_rows),
            "settlement_ready_count": len(settlement_rows) - len(blocked_rows),
            "blocked_row_count": len(blocked_rows),
            "candidate_lifecycle_settlement_written": False,
            "accepted_lifecycle_ledger_mutated": False,
            "source_request_files_mutated": False,
            "replacement_request_files_written": 0,
            "codex_queue_run_started": False,
            "graph_delta_claim_count": len(graph_deltas["upsert_claims"]),
        },
        "settlement_rows": settlement_rows,
        "blocked_rows": blocked_rows,
        "next_packets": next_packets,
        "next_packet": next_packets[0]["packet_id"]
        if next_packets
        else "PCKT-DOMAIN-WEAVER-LIMITED-WATCH-MATRIX-REFRESH-V0_2",
        "candidate_lifecycle_settlement_written": False,
        "accepted_lifecycle_ledger_mutated": False,
        "source_request_files_mutated": False,
        "replacement_request_files_written": 0,
        "codex_queue_run_started": False,
        "actual_spawn_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
        "candidate_context_graph_deltas": graph_deltas,
        "source_evidence": [
            review_ref,
            _evidence_ref(root, CODEX_WORK_REQUESTS_DIR.as_posix()),
            _evidence_ref(root, DEFAULT_QUEUE_GOVERNANCE_DIR.as_posix()),
        ],
        "non_claims": [
            *NON_CLAIMS,
            "Stale waiting settlement writes a candidate settlement ledger only.",
            "The original stale source request files are not mutated by this packet.",
            "The candidate settlement does not start the queue runner or authorize general queue processing.",
            "Only rows whose current source SHA matches the review SHA are usable by later metadata reissue safety checks.",
            "Accepted lifecycle state remains unchanged until a separate accepted-state route proves that authority.",
        ],
    }


def write_stale_waiting_reconciliation_settlement(
    active_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    generated_at: str | None = None,
    review: Mapping[str, Any] | None = None,
    settlement_decision: str = "supersede_with_fresh_exact_request",
    confirmation: str | None = None,
    write_receipt: bool = True,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    if confirmation != STALE_WAITING_RECONCILIATION_SETTLEMENT_CONFIRMATION:
        result = {
            "schema_id": STALE_WAITING_RECONCILIATION_SETTLEMENT_WRITE_RESULT_SCHEMA_ID,
            "generated_at": _utc_now(),
            "active_root": str(root),
            "ok": False,
            "verdict": "STALE_WAITING_RECONCILIATION_SETTLEMENT_CONFIRMATION_REQUIRED",
            "required_confirmation": STALE_WAITING_RECONCILIATION_SETTLEMENT_CONFIRMATION,
            "provided_confirmation": confirmation,
            "settlement_path": None,
            "settlement_row_count": 0,
            "candidate_lifecycle_settlement_written": False,
            "accepted_lifecycle_ledger_mutated": False,
            "source_request_files_mutated": False,
            "replacement_request_files_written": 0,
            "codex_queue_run_started": False,
            "authority": AUTHORITY,
        }
        if write_receipt:
            result["operator_receipt_path"] = (
                write_stale_waiting_reconciliation_settlement_operator_receipt(
                    root,
                    result,
                    None,
                )
            )
        return result

    settlement = build_stale_waiting_reconciliation_settlement(
        root,
        generated_at=generated_at,
        review=review,
        settlement_decision=settlement_decision,
    )
    if settlement["verdict"] != "STALE_WAITING_RECONCILIATION_SETTLEMENT_READY":
        result = {
            "schema_id": STALE_WAITING_RECONCILIATION_SETTLEMENT_WRITE_RESULT_SCHEMA_ID,
            "generated_at": settlement["generated_at"],
            "active_root": str(root),
            "ok": False,
            "verdict": settlement["verdict"],
            "blocked_rows": settlement.get("blocked_rows", []),
            "settlement_row_count": settlement["summary"]["settlement_row_count"],
            "candidate_lifecycle_settlement_written": False,
            "accepted_lifecycle_ledger_mutated": False,
            "source_request_files_mutated": False,
            "replacement_request_files_written": 0,
            "codex_queue_run_started": False,
            "authority": AUTHORITY,
        }
        if write_receipt:
            result["operator_receipt_path"] = (
                write_stale_waiting_reconciliation_settlement_operator_receipt(
                    root,
                    result,
                    settlement,
                )
            )
        return result

    out_dir = _resolve_output_dir(root, output_dir or DEFAULT_QUEUE_GOVERNANCE_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    settlement["verdict"] = "STALE_WAITING_RECONCILIATION_SETTLEMENT_WRITTEN"
    settlement["candidate_lifecycle_settlement_written"] = True
    settlement["summary"]["candidate_lifecycle_settlement_written"] = True
    settlement["candidate_context_graph_deltas"] = (
        _stale_waiting_reconciliation_settlement_graph_deltas(
            root,
            generated_at=str(settlement["generated_at"]),
            settlement_rows=list(settlement.get("settlement_rows") or []),
            review_ref=_mapping(settlement.get("source_review")),
            write_performed=True,
        )
    )
    settlement_path = out_dir / DEFAULT_STALE_WAITING_RECONCILIATION_SETTLEMENT_NAME
    report_path = out_dir / DEFAULT_STALE_WAITING_RECONCILIATION_SETTLEMENT_REPORT_NAME
    deltas_path = out_dir / DEFAULT_STALE_WAITING_RECONCILIATION_SETTLEMENT_DELTAS_NAME
    settlement_text = _stable_json(settlement)
    report_text = render_stale_waiting_reconciliation_settlement_report(settlement)
    deltas_text = _stable_json(dict(settlement["candidate_context_graph_deltas"]))
    settlement_path.write_text(settlement_text, encoding="utf-8")
    report_path.write_text(report_text, encoding="utf-8")
    deltas_path.write_text(deltas_text, encoding="utf-8")

    result = {
        "schema_id": STALE_WAITING_RECONCILIATION_SETTLEMENT_WRITE_RESULT_SCHEMA_ID,
        "generated_at": settlement["generated_at"],
        "active_root": str(root),
        "ok": True,
        "verdict": "STALE_WAITING_RECONCILIATION_SETTLEMENT_WRITTEN",
        "settlement_path": _rel(root, settlement_path),
        "settlement_sha256": _sha256_text(settlement_text),
        "report_path": _rel(root, report_path),
        "report_sha256": _sha256_text(report_text),
        "context_graph_delta_path": _rel(root, deltas_path),
        "context_graph_delta_sha256": _sha256_text(deltas_text),
        "settlement_row_count": settlement["summary"]["settlement_row_count"],
        "settlement_ready_count": settlement["summary"]["settlement_ready_count"],
        "candidate_lifecycle_settlement_written": True,
        "accepted_lifecycle_ledger_mutated": False,
        "source_request_files_mutated": False,
        "replacement_request_files_written": 0,
        "codex_queue_run_started": False,
        "next_packet": settlement["next_packet"],
        "authority": AUTHORITY,
    }
    if write_receipt:
        result["operator_receipt_path"] = (
            write_stale_waiting_reconciliation_settlement_operator_receipt(
                root,
                result,
                settlement,
            )
        )
    return result


def build_generated_mount_creation_for_metadata_reissue(
    active_root: str | Path,
    *,
    generated_at: str | None = None,
    source_assignment: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Plan generated Codex agent mounts for metadata reissue rows."""

    root = _require_active_root(active_root)
    generated = generated_at or _utc_now()
    assignment, assignment_ref = _load_metadata_assignment_or_build(
        root,
        generated_at=generated,
        source_assignment=source_assignment,
    )
    assignment_rows = [
        row
        for row in list(assignment.get("assignment_rows") or [])
        if isinstance(row, Mapping)
    ]
    generated_rows = [
        row
        for row in assignment_rows
        if row.get("assignment_disposition") == "generated_mount_required"
        and _mapping(row.get("generated_mount_spec")).get("mount_id")
    ]
    creation_rows = _generated_mount_creation_rows(
        root,
        generated_rows=generated_rows,
        materialized_mounts={},
    )
    graph_deltas = _generated_mount_creation_graph_deltas(
        root,
        generated_at=generated,
        creation_rows=creation_rows,
        source_assignment_ref=assignment_ref,
    )
    ready_count = sum(1 for row in creation_rows if row.get("creation_candidate_ready"))
    existing_count = sum(1 for row in creation_rows if row.get("preexisting_manifest_ref", {}).get("exists"))
    verdict = (
        "GENERATED_MOUNT_CREATION_READY"
        if ready_count
        else "GENERATED_MOUNT_CREATION_NO_ROWS"
    )
    next_packets = _generated_mount_creation_next_packets(
        ready_count=ready_count,
        assignment_summary=_mapping(assignment.get("summary")),
    )
    return {
        "schema_id": GENERATED_MOUNT_CREATION_SCHEMA_ID,
        "generated_at": generated,
        "active_root": str(root),
        "status": "generated_mount_creation_for_metadata_reissue_candidate_built",
        "verdict": verdict,
        "source_assignment": assignment_ref,
        "source_assignment_verdict": assignment.get("verdict"),
        "source_assignment_generated_at": assignment.get("generated_at"),
        "source_assignment_is_latest_file": bool(assignment_ref.get("path")),
        "summary": {
            "source_generated_mount_required_row_count": len(generated_rows),
            "unique_mount_candidate_count": len(creation_rows),
            "creation_candidate_ready_count": ready_count,
            "preexisting_mount_count": existing_count,
            "mounts_materialized": 0,
            "source_request_files_mutated": False,
            "replacement_request_files_written": 0,
            "codex_queue_run_started": False,
            "graph_delta_claim_count": len(graph_deltas["upsert_claims"]),
        },
        "generated_mount_creation_rows": creation_rows,
        "next_packets": next_packets,
        "next_packet": next_packets[0]["packet_id"]
        if next_packets
        else "PCKT-DOMAIN-WEAVER-LIMITED-WATCH-MATRIX-REFRESH-V0_2",
        "mounts_materialized": 0,
        "request_files_mutated": False,
        "replacement_request_files_written": 0,
        "codex_queue_run_started": False,
        "actual_spawn_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
        "candidate_context_graph_deltas": graph_deltas,
        "source_evidence": [
            assignment_ref,
            _evidence_ref(root, "ION/05_context/current/codex_agent_mounts"),
            _evidence_ref(root, DEFAULT_QUEUE_GOVERNANCE_DIR.as_posix()),
        ],
        "non_claims": [
            *NON_CLAIMS,
            "Generated mount creation materializes candidate Codex carrier folders only; it does not start workers.",
            "Generated mounts do not prove source lifecycle safety, request apply readiness, or accepted state.",
            "Rows sharing a mount_id are deduped to one mount and remain separately bound by later assignment refresh.",
            "General queue processing remains blocked; any future worker run must be exact-request-path only.",
        ],
    }


def write_generated_mount_creation_for_metadata_reissue(
    active_root: str | Path,
    *,
    output_dir: str | Path | None = None,
    generated_at: str | None = None,
    materialize_mounts: bool = True,
    write_receipt: bool = True,
) -> dict[str, Any]:
    root = _require_active_root(active_root)
    review = build_generated_mount_creation_for_metadata_reissue(
        root,
        generated_at=generated_at,
    )
    materialized_mounts: dict[str, Mapping[str, Any]] = {}
    if materialize_mounts:
        materialized_mounts = _materialize_generated_mount_creation_rows(
            root,
            rows=list(review.get("generated_mount_creation_rows") or []),
        )
        assignment, assignment_ref = _load_metadata_assignment_or_build(
            root,
            generated_at=str(review["generated_at"]),
            source_assignment=None,
        )
        generated_rows = [
            row
            for row in list(assignment.get("assignment_rows") or [])
            if isinstance(row, Mapping)
            and row.get("assignment_disposition") == "generated_mount_required"
            and _mapping(row.get("generated_mount_spec")).get("mount_id")
        ]
        review["generated_mount_creation_rows"] = _generated_mount_creation_rows(
            root,
            generated_rows=generated_rows,
            materialized_mounts=materialized_mounts,
        )
        review["source_assignment"] = assignment_ref
        review["source_assignment_verdict"] = assignment.get("verdict")
        review["source_assignment_generated_at"] = assignment.get("generated_at")
        review["source_assignment_is_latest_file"] = bool(assignment_ref.get("path"))

    creation_rows = list(review.get("generated_mount_creation_rows") or [])
    materialized_count = sum(1 for row in creation_rows if row.get("materialized_by_this_packet"))
    ready_count = sum(1 for row in creation_rows if row.get("creation_candidate_ready"))
    existing_count = sum(
        1 for row in creation_rows if _mapping(row.get("post_manifest_ref")).get("exists")
    )
    review["mounts_materialized"] = materialized_count
    review["summary"]["mounts_materialized"] = materialized_count
    review["summary"]["creation_candidate_ready_count"] = ready_count
    review["summary"]["post_materialized_mount_count"] = existing_count
    review["summary"]["missing_required_file_count"] = sum(
        len(list(row.get("missing_required_files") or [])) for row in creation_rows
    )
    review["candidate_context_graph_deltas"] = _generated_mount_creation_graph_deltas(
        root,
        generated_at=str(review["generated_at"]),
        creation_rows=creation_rows,
        source_assignment_ref=_mapping(review.get("source_assignment")),
    )
    review["summary"]["graph_delta_claim_count"] = len(
        review["candidate_context_graph_deltas"]["upsert_claims"]
    )
    review["verdict"] = (
        "GENERATED_MOUNT_CREATION_MOUNTS_MATERIALIZED"
        if materialized_count
        else review.get("verdict")
    )

    out_dir = _resolve_output_dir(root, output_dir or DEFAULT_QUEUE_GOVERNANCE_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    review_path = out_dir / DEFAULT_GENERATED_MOUNT_CREATION_NAME
    report_path = out_dir / DEFAULT_GENERATED_MOUNT_CREATION_REPORT_NAME
    deltas_path = out_dir / DEFAULT_GENERATED_MOUNT_CREATION_DELTAS_NAME
    review_text = _stable_json(review)
    report_text = render_generated_mount_creation_report(review)
    deltas_text = _stable_json(dict(review["candidate_context_graph_deltas"]))
    review_path.write_text(review_text, encoding="utf-8")
    report_path.write_text(report_text, encoding="utf-8")
    deltas_path.write_text(deltas_text, encoding="utf-8")

    result = {
        "schema_id": GENERATED_MOUNT_CREATION_WRITE_RESULT_SCHEMA_ID,
        "generated_at": review["generated_at"],
        "active_root": str(root),
        "verdict": review["verdict"],
        "review_path": _rel(root, review_path),
        "review_sha256": _sha256_text(review_text),
        "report_path": _rel(root, report_path),
        "report_sha256": _sha256_text(report_text),
        "context_graph_delta_path": _rel(root, deltas_path),
        "context_graph_delta_sha256": _sha256_text(deltas_text),
        "source_generated_mount_required_row_count": review["summary"][
            "source_generated_mount_required_row_count"
        ],
        "unique_mount_candidate_count": review["summary"]["unique_mount_candidate_count"],
        "mounts_materialized": materialized_count,
        "source_request_files_mutated": False,
        "replacement_request_files_written": 0,
        "codex_queue_run_started": False,
        "next_packet": review["next_packet"],
        "authority": AUTHORITY,
    }
    if write_receipt:
        result["operator_receipt_path"] = write_generated_mount_creation_operator_receipt(
            root,
            result,
            review,
        )
    return result


def render_control_plane_report(control: Mapping[str, Any]) -> str:
    readiness = _mapping(control.get("readiness"))
    watch = _mapping(control.get("watch_matrix"))
    fleet = _mapping(control.get("fleet_plan"))
    proposal = _mapping(control.get("proposal_wave_validation"))
    blockers = list(readiness.get("blockers_ranked") or [])
    next_packet_groups = _mapping(readiness.get("next_packets"))
    lines = [
        "# Domain Weaver Swarm Control Plane",
        "",
        f"generated_at: {control.get('generated_at')}",
        f"active_root: `{control.get('active_root')}`",
        f"verdict: `{control.get('verdict')}`",
        "authority: candidate-only; no production, live execution, accepted-state, secrets, materialization, deploy, push, topology, UI resume, or destructive authority",
        "",
        "## What Was Built",
        "",
        "- A command structure for root steward, domain stewards, watch, fleet lifecycle, queue/worker, context graph, receipt/proof, comms, action gateway, proposal validation, fan-in, Nemesis, operator truth, and escalation lanes.",
        f"- A watch matrix with `{_mapping(watch.get('coverage')).get('target_count', 0)}` watched targets and response packets.",
        f"- A fleet plan with `{fleet.get('lane_count', 0)}` bounded lanes and lifecycle from intent to fan-in.",
        f"- Candidate context graph deltas with `{readiness.get('context_graph_delta_claim_count', 0)}` claims.",
        f"- A proposal-wave validation result: `{proposal.get('status')}`.",
        "",
        "## What Changed In Readiness",
        "",
    ]
    for item in readiness.get("newly_advanced_in_this_tranche") or []:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## What The Swarm Can Now Do",
            "",
            "- Convert Domain Weaver intent into a role/domain/context-bound fleet plan without starting workers.",
            "- Watch queue, worker, comms, route, gateway, receipt, graph, proposal, fan-in, materialization, UI, and semantic-alias surfaces.",
            "- Classify alerts into response packets and candidate graph deltas.",
            "- Validate proposal-wave returns for path/schema/nonclaim safety before widening.",
            "- Preserve the distinction between carrier intake, candidate graph deltas, and accepted state.",
            "",
            "## Remaining Blockers",
            "",
        ]
    )
    if blockers:
        for row in blockers:
            lines.append(
                f"- `{row.get('severity')}` `{row.get('code')}`: {row.get('detail')}"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Next Packets", ""])
    for group_name, packets in next_packet_groups.items():
        lines.append(f"### {group_name}")
        for packet in packets:
            lines.append(f"- `{packet}`")
        lines.append("")
    lines.extend(
        [
            "## Nemesis Dissent",
            "",
            str(readiness.get("nemesis_dissent") or ""),
            "",
            "## Non-Claims",
            "",
        ]
    )
    for item in control.get("non_claims") or NON_CLAIMS:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def render_limited_watch_refresh_report(refresh: Mapping[str, Any]) -> str:
    summary = _mapping(refresh.get("summary"))
    lines = [
        "# Domain Weaver Limited Watch Matrix Refresh",
        "",
        f"generated_at: {refresh.get('generated_at')}",
        f"active_root: `{refresh.get('active_root')}`",
        f"verdict: `{refresh.get('verdict')}`",
        "authority: candidate-only; no workers spawned; no queue run started; no accepted-state movement",
        "",
        "## Summary",
        "",
        f"- Targets evaluated: `{summary.get('target_count', 0)}`",
        f"- Alerts: `{summary.get('alert_count', 0)}`",
        f"- Response packets: `{summary.get('response_packet_count', 0)}`",
        f"- Graph delta claims: `{summary.get('graph_delta_claim_count', 0)}`",
        "",
        "## Alerts",
        "",
    ]
    alerts = list(refresh.get("alerts") or [])
    if not alerts:
        lines.append("- none")
    for alert in alerts:
        if not isinstance(alert, Mapping):
            continue
        lines.append(
            f"- `{alert.get('severity')}` `{alert.get('code')}` "
            f"on `{alert.get('target_id')}`: {alert.get('detail')}"
        )
    lines.extend(["", "## Response Packets", ""])
    packets = list(refresh.get("response_packets") or [])
    if not packets:
        lines.append("- none")
    for packet in packets:
        lines.append(f"- `{packet}`")
    lines.extend(
        [
            "",
            "## Next Packet",
            "",
            f"`{refresh.get('next_packet')}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    for item in refresh.get("non_claims") or NON_CLAIMS:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def render_global_queue_hygiene_report(hygiene: Mapping[str, Any]) -> str:
    summary = _mapping(hygiene.get("summary"))
    lines = [
        "# Domain Weaver Global Queue Backlog Context Identity Hygiene",
        "",
        f"generated_at: {hygiene.get('generated_at')}",
        f"active_root: `{hygiene.get('active_root')}`",
        f"verdict: `{hygiene.get('verdict')}`",
        "authority: candidate-only; no queue mutation; no queue run started; no worker spawned; no accepted-state movement",
        "",
        "## Summary",
        "",
        f"- Work-request files: `{summary.get('work_request_file_count', 0)}`",
        f"- Active queue rows: `{summary.get('active_queue_request_count', 0)}`",
        f"- Queueable readiness rows: `{summary.get('queueable_readiness_request_count', 0)}`",
        f"- Blocked queue/readiness rows: `{summary.get('blocked_request_count', 0)}`",
        f"- Stale waiting rows: `{summary.get('stale_waiting_request_count', 0)}`",
        f"- Terminal repair rows: `{summary.get('terminal_repair_request_count', 0)}`",
        f"- Actionable duplicate groups: `{summary.get('actionable_duplicate_group_count', 0)}`",
        f"- Candidate exact request paths: `{summary.get('candidate_exact_request_path_count', 0)}`",
        "",
        "## Blockers",
        "",
    ]
    blockers = list(hygiene.get("blockers_ranked") or [])
    if not blockers:
        lines.append("- none")
    for row in blockers:
        if isinstance(row, Mapping):
            lines.append(
                f"- `{row.get('severity')}` `{row.get('code')}`: {row.get('detail')}"
            )
    lines.extend(["", "## Repair Packets", ""])
    packets = list(hygiene.get("repair_packets") or [])
    if not packets:
        lines.append("- none")
    for packet in packets:
        if isinstance(packet, Mapping):
            lines.append(
                f"- `{packet.get('packet_id')}`: {packet.get('purpose')}"
            )
    lines.extend(["", "## Exact-Path Candidates", ""])
    exact_paths = list(hygiene.get("candidate_exact_request_paths") or [])
    if not exact_paths:
        lines.append("- none")
    for path in exact_paths:
        lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "## Next Packet",
            "",
            f"`{hygiene.get('next_packet')}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    for item in hygiene.get("non_claims") or NON_CLAIMS:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def render_post_sidecar_global_queue_hygiene_report(readback: Mapping[str, Any]) -> str:
    summary = _mapping(readback.get("summary"))
    lines = [
        "# Domain Weaver Post-Sidecar Global Queue Hygiene",
        "",
        f"generated_at: {readback.get('generated_at')}",
        f"active_root: `{readback.get('active_root')}`",
        f"verdict: `{readback.get('verdict')}`",
        "authority: candidate readback only; no source request mutation; no replacement writes; no queue run started; no accepted-state movement",
        "",
        "## Summary",
        "",
        f"- Expected source originals: `{summary.get('expected_source_original_count', 0)}`",
        f"- Queued source originals: `{summary.get('queued_source_original_count', 0)}`",
        f"- Classified source originals: `{summary.get('classified_source_original_count', 0)}`",
        f"- External quarantine rows: `{summary.get('quarantine_as_stale_external_non_domain_count', 0)}`",
        f"- Supersede-with-fresh-exact rows: `{summary.get('supersede_with_fresh_exact_request_count', 0)}`",
        f"- Replacement requests found: `{summary.get('replacement_request_found_count', 0)}`",
        f"- Accepted replacement returns: `{summary.get('replacement_return_accepted_count', 0)}`",
        f"- Failed replacement returns: `{summary.get('replacement_failed_count', 0)}`",
        f"- General queue processing allowed: `{summary.get('general_queue_processing_allowed')}`",
        "",
        "## Source Original Matrix",
        "",
    ]
    rows = list(readback.get("source_original_rows") or [])
    if not rows:
        lines.append("- none")
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        lines.append(
            f"- `{row.get('source_request_id')}` `{row.get('candidate_classification')}` "
            f"source_status=`{row.get('source_status')}` "
            f"replacement_status=`{row.get('replacement_current_status') or 'none'}`"
        )
    lines.extend(["", "## Blockers", ""])
    blockers = list(readback.get("blockers_ranked") or [])
    if not blockers:
        lines.append("- none")
    for row in blockers:
        if isinstance(row, Mapping):
            lines.append(
                f"- `{row.get('severity')}` `{row.get('code')}`: {row.get('detail')}"
            )
    lines.extend(["", "## Next Packets", ""])
    packets = list(readback.get("next_packets") or [])
    if not packets:
        lines.append("- none")
    for packet in packets:
        if isinstance(packet, Mapping):
            lines.append(f"- `{packet.get('packet_id')}`: {packet.get('purpose')}")
    lines.extend(["", "## Non-Claims", ""])
    for item in readback.get("non_claims") or NON_CLAIMS:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def render_global_queue_repair_preview_report(preview: Mapping[str, Any]) -> str:
    summary = _mapping(preview.get("summary"))
    lines = [
        "# Domain Weaver Global Queue Backlog Identity Repair Preview",
        "",
        f"generated_at: {preview.get('generated_at')}",
        f"active_root: `{preview.get('active_root')}`",
        f"verdict: `{preview.get('verdict')}`",
        "authority: candidate-only; no request files mutated; no lifecycle ledger write; no queue run started; no accepted-state movement",
        "",
        "## Summary",
        "",
        f"- Queueable repair rows: `{summary.get('queueable_repair_row_count', 0)}`",
        f"- Lifecycle preview rows: `{summary.get('lifecycle_preview_row_count', 0)}`",
        f"- Candidate exact request paths: `{summary.get('candidate_exact_request_path_count', 0)}`",
        f"- Graph delta claims: `{summary.get('graph_delta_claim_count', 0)}`",
        f"- Mutation gate required: `{summary.get('mutation_gate_required')}`",
        "",
        "## Repair Classes",
        "",
    ]
    class_counts = _mapping(summary.get("repair_class_counts"))
    if not class_counts:
        lines.append("- none")
    for repair_class, count in class_counts.items():
        lines.append(f"- `{repair_class}`: `{count}`")
    lines.extend(["", "## Queueable Repair Rows", ""])
    repair_rows = list(preview.get("queueable_repair_rows") or [])
    if not repair_rows:
        lines.append("- none")
    for row in repair_rows:
        if not isinstance(row, Mapping):
            continue
        lines.append(
            f"- `{row.get('repair_class')}` `{row.get('request_id')}`: "
            f"{row.get('recommended_action')} (`{row.get('request_path')}`)"
        )
    lines.extend(["", "## Lifecycle Preview Rows", ""])
    lifecycle_rows = list(preview.get("lifecycle_preview_rows") or [])
    if not lifecycle_rows:
        lines.append("- none")
    for row in lifecycle_rows:
        if not isinstance(row, Mapping):
            continue
        lines.append(
            f"- `{row.get('repair_class')}` `{row.get('request_id')}`: "
            f"{row.get('recommended_action')} (`{row.get('source_path')}`)"
        )
    lines.extend(["", "## Next Packets", ""])
    packets = list(preview.get("next_packets") or [])
    if not packets:
        lines.append("- none")
    for packet in packets:
        if isinstance(packet, Mapping):
            lines.append(f"- `{packet.get('packet_id')}`: {packet.get('purpose')}")
    lines.extend(
        [
            "",
            "## Next Packet",
            "",
            f"`{preview.get('next_packet')}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    for item in preview.get("non_claims") or NON_CLAIMS:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def render_queue_request_metadata_identity_reissue_report(worksheet: Mapping[str, Any]) -> str:
    summary = _mapping(worksheet.get("summary"))
    lines = [
        "# Domain Weaver Queue Request Metadata Identity Reissue",
        "",
        f"generated_at: {worksheet.get('generated_at')}",
        f"active_root: `{worksheet.get('active_root')}`",
        f"verdict: `{worksheet.get('verdict')}`",
        "authority: candidate-only; no replacement requests written; no source requests mutated; no queue run started; no accepted-state movement",
        "",
        "## Summary",
        "",
        f"- Worksheet rows: `{summary.get('worksheet_row_count', 0)}`",
        f"- Reissue allowed now: `{summary.get('candidate_reissue_allowed_now_count', 0)}`",
        f"- Reissue blocked: `{summary.get('candidate_reissue_blocked_count', 0)}`",
        f"- Excluded non-metadata repair rows: `{summary.get('excluded_non_metadata_repair_row_count', 0)}`",
        f"- Replacement requests written: `{summary.get('replacement_requests_written', 0)}`",
        f"- Graph delta claims: `{summary.get('graph_delta_claim_count', 0)}`",
        "",
        "## Worksheet Rows",
        "",
    ]
    rows = list(worksheet.get("worksheet_rows") or [])
    if not rows:
        lines.append("- none")
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        lines.append(
            f"- `{row.get('source_request_id')}`: `{row.get('review_disposition')}` "
            f"domain=`{row.get('domain_assignment_status')}` "
            f"role=`{row.get('role_assignment_status')}` "
            f"capsule=`{row.get('capsule_identity_status')}` "
            f"allowed_now=`{row.get('candidate_reissue_allowed_now')}`"
        )
    lines.extend(["", "## Excluded Rows", ""])
    excluded = list(worksheet.get("excluded_non_metadata_repair_rows") or [])
    if not excluded:
        lines.append("- none")
    for row in excluded:
        if isinstance(row, Mapping):
            lines.append(
                f"- `{row.get('repair_class')}` `{row.get('request_id')}` -> `{row.get('repair_packet_id')}`"
            )
    lines.extend(["", "## Next Packets", ""])
    packets = list(worksheet.get("next_packets") or [])
    if not packets:
        lines.append("- none")
    for packet in packets:
        if isinstance(packet, Mapping):
            lines.append(f"- `{packet.get('packet_id')}`: {packet.get('purpose')}")
    lines.extend(
        [
            "",
            "## Next Packet",
            "",
            f"`{worksheet.get('next_packet')}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    for item in worksheet.get("non_claims") or NON_CLAIMS:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def render_queue_metadata_identity_assignment_report(assignment: Mapping[str, Any]) -> str:
    summary = _mapping(assignment.get("summary"))
    lines = [
        "# Domain Weaver Queue Metadata Identity Assignment",
        "",
        f"generated_at: {assignment.get('generated_at')}",
        f"active_root: `{assignment.get('active_root')}`",
        f"verdict: `{assignment.get('verdict')}`",
        "authority: candidate-only; no replacement requests written; no source requests mutated; no mounts created; no queue run started; no accepted-state movement",
        "",
        "## Summary",
        "",
        f"- Assignment rows: `{summary.get('assignment_row_count', 0)}`",
        f"- Existing-mount ready: `{summary.get('existing_mount_assignment_ready_count', 0)}`",
        f"- Apply-review ready: `{summary.get('apply_review_ready_count', 0)}`",
        f"- Source-safety blocked: `{summary.get('source_safety_blocked_count', 0)}`",
        f"- Generated-mount required: `{summary.get('generated_mount_required_count', 0)}`",
        f"- Supersede/quarantine recommended: `{summary.get('supersede_or_quarantine_recommended_count', 0)}`",
        f"- Replacement requests written: `{summary.get('replacement_requests_written', 0)}`",
        f"- Mounts created: `{summary.get('mounts_created', 0)}`",
        f"- Graph delta claims: `{summary.get('graph_delta_claim_count', 0)}`",
        "",
        "## Assignment Rows",
        "",
    ]
    rows = list(assignment.get("assignment_rows") or [])
    if not rows:
        lines.append("- none")
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        assigned = _mapping(row.get("assigned_identity"))
        lines.append(
            f"- `{row.get('source_request_id')}`: `{row.get('assignment_disposition')}` "
            f"domain=`{assigned.get('domain_id')}` role=`{assigned.get('role_id')}` "
            f"mount=`{assigned.get('selected_mount_id')}` "
            f"apply_ready=`{row.get('candidate_reissue_apply_review_ready')}`"
        )
    lines.extend(["", "## Next Packets", ""])
    packets = list(assignment.get("next_packets") or [])
    if not packets:
        lines.append("- none")
    for packet in packets:
        if isinstance(packet, Mapping):
            lines.append(f"- `{packet.get('packet_id')}`: {packet.get('purpose')}")
    lines.extend(
        [
            "",
            "## Next Packet",
            "",
            f"`{assignment.get('next_packet')}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    for item in assignment.get("non_claims") or NON_CLAIMS:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def render_exact_reissue_request_dispatch_readiness_report(
    readiness: Mapping[str, Any],
) -> str:
    summary = _mapping(readiness.get("summary"))
    runtime = _mapping(readiness.get("runtime_status"))
    lines = [
        "# Domain Weaver Exact Reissue Request Dispatch Readiness",
        "",
        f"generated_at: {readiness.get('generated_at')}",
        f"active_root: `{readiness.get('active_root')}`",
        f"verdict: `{readiness.get('verdict')}`",
        "authority: candidate-only; exact request-path validation only; no queue run started; no accepted-state movement",
        "",
        "## Summary",
        "",
        f"- Request paths: `{summary.get('request_path_count', 0)}`",
        f"- Dispatch ready: `{summary.get('dispatch_ready_count', 0)}`",
        f"- Blocked rows: `{summary.get('blocked_row_count', 0)}`",
        f"- Dispatch groups: `{summary.get('dispatch_group_count', 0)}`",
        f"- Runtime status fresh enough: `{summary.get('runtime_status_fresh_enough')}`",
        f"- Runtime active clear: `{summary.get('runtime_active_clear')}`",
        f"- Ready after status refresh: `{readiness.get('ready_for_staged_exact_dispatch_after_status_refresh')}`",
        f"- Ready for immediate exact start: `{readiness.get('ready_for_immediate_exact_start')}`",
        f"- Queue run started: `{summary.get('codex_queue_run_started')}`",
        f"- Graph delta claims: `{summary.get('graph_delta_claim_count', 0)}`",
        "",
        "## Runtime Status",
        "",
        f"- State path: `{runtime.get('state_path')}`",
        f"- Updated at: `{runtime.get('updated_at')}`",
        f"- Age seconds: `{runtime.get('age_seconds')}`",
        f"- Status command: `{readiness.get('status_command')}`",
        "",
        "## Readiness Rows",
        "",
    ]
    rows = list(readiness.get("readiness_rows") or [])
    if not rows:
        lines.append("- none")
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        blockers = list(row.get("dispatch_blockers") or [])
        blocker_text = ",".join(str(item) for item in blockers) if blockers else "none"
        lines.append(
            f"- `{row.get('request_id')}`: class=`{row.get('request_class')}` "
            f"lane=`{row.get('lane_id')}` role=`{row.get('role_id')}` "
            f"mount=`{row.get('selected_mount_path')}` ready=`{row.get('dispatch_ready')}` "
            f"blockers=`{blocker_text}`"
        )
    lines.extend(["", "## Dispatch Groups", ""])
    groups = list(readiness.get("dispatch_groups") or [])
    if not groups:
        lines.append("- none")
    for group in groups:
        if not isinstance(group, Mapping):
            continue
        request_ids = ", ".join(str(value) for value in group.get("request_ids") or [])
        lines.append(
            f"- wave `{group.get('wave_index')}` lanes=`{group.get('lane_ids')}` "
            f"requests=`{request_ids}`"
        )
    lines.extend(["", "## Next Packets", ""])
    packets = list(readiness.get("next_packets") or [])
    if not packets:
        lines.append("- none")
    for packet in packets:
        if isinstance(packet, Mapping):
            lines.append(f"- `{packet.get('packet_id')}`: {packet.get('purpose')}")
    lines.extend(
        [
            "",
            "## Next Packet",
            "",
            f"`{readiness.get('next_packet')}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    for item in readiness.get("non_claims") or NON_CLAIMS:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def render_stale_non_domain_queue_quarantine_settlement_report(
    settlement: Mapping[str, Any],
) -> str:
    summary = _mapping(settlement.get("summary"))
    lines = [
        "# Domain Weaver Stale Non-Domain Queue Quarantine Settlement",
        "",
        f"generated_at: {settlement.get('generated_at')}",
        f"active_root: `{settlement.get('active_root')}`",
        f"verdict: `{settlement.get('verdict')}`",
        "authority: candidate quarantine ledger only; no source request mutation; no queue run started; no accepted-state movement",
        "",
        "## Summary",
        "",
        f"- Settlement rows: `{summary.get('settlement_row_count', 0)}`",
        f"- Settlement ready: `{summary.get('settlement_ready_count', 0)}`",
        f"- Blocked rows: `{summary.get('blocked_row_count', 0)}`",
        f"- Candidate quarantine settlement written: `{summary.get('candidate_quarantine_settlement_written')}`",
        f"- Source request files mutated: `{summary.get('source_request_files_mutated')}`",
        f"- Replacement request files written: `{summary.get('replacement_request_files_written', 0)}`",
        f"- Queue run started: `{summary.get('codex_queue_run_started')}`",
        f"- Graph delta claims: `{summary.get('graph_delta_claim_count', 0)}`",
        "",
        "## Settlement Rows",
        "",
    ]
    rows = list(settlement.get("settlement_rows") or [])
    if not rows:
        lines.append("- none")
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        lines.append(
            f"- `{row.get('source_request_id')}`: decision=`{row.get('settlement_decision')}` "
            f"ready=`{row.get('settlement_ready')}` source_hash_match=`{row.get('source_hash_matches_assignment')}`"
        )
    lines.extend(["", "## Next Packets", ""])
    packets = list(settlement.get("next_packets") or [])
    if not packets:
        lines.append("- none")
    for packet in packets:
        if isinstance(packet, Mapping):
            lines.append(f"- `{packet.get('packet_id')}`: {packet.get('purpose')}")
    lines.extend(
        [
            "",
            "## Next Packet",
            "",
            f"`{settlement.get('next_packet')}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    for item in settlement.get("non_claims") or NON_CLAIMS:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def render_queue_metadata_identity_reissue_apply_review_report(
    review: Mapping[str, Any],
) -> str:
    summary = _mapping(review.get("summary"))
    lines = [
        "# Domain Weaver Queue Metadata Identity Reissue Apply Review",
        "",
        f"generated_at: {review.get('generated_at')}",
        f"active_root: `{review.get('active_root')}`",
        f"verdict: `{review.get('verdict')}`",
        "authority: candidate-only; candidate body files only; no source request mutation; no replacement request files written; no queue run started; no accepted-state movement",
        "",
        "## Summary",
        "",
        f"- Apply-review rows: `{summary.get('apply_review_row_count', 0)}`",
        f"- Apply candidates ready: `{summary.get('apply_candidate_ready_count', 0)}`",
        f"- Excluded assignment rows: `{summary.get('excluded_assignment_row_count', 0)}`",
        f"- Candidate body files written: `{summary.get('candidate_body_files_written', 0)}`",
        f"- Replacement request files written: `{summary.get('replacement_request_files_written', 0)}`",
        f"- Source request files mutated: `{summary.get('source_request_files_mutated')}`",
        f"- Graph delta claims: `{summary.get('graph_delta_claim_count', 0)}`",
        "",
        "## Apply-Review Rows",
        "",
    ]
    rows = list(review.get("apply_review_rows") or [])
    if not rows:
        lines.append("- none")
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        lines.append(
            f"- `{row.get('source_request_id')}` -> `{row.get('candidate_replacement_request_id')}` "
            f"ready=`{row.get('apply_candidate_ready')}` body=`{row.get('candidate_replacement_body_path')}`"
        )
    lines.extend(["", "## Excluded Rows", ""])
    excluded = list(review.get("excluded_assignment_rows") or [])
    if not excluded:
        lines.append("- none")
    for row in excluded:
        if isinstance(row, Mapping):
            lines.append(
                f"- `{row.get('source_request_id')}`: `{row.get('assignment_disposition')}` -> `{row.get('next_packet')}`"
            )
    lines.extend(["", "## Next Packets", ""])
    packets = list(review.get("next_packets") or [])
    if not packets:
        lines.append("- none")
    for packet in packets:
        if isinstance(packet, Mapping):
            lines.append(f"- `{packet.get('packet_id')}`: {packet.get('purpose')}")
    lines.extend(
        [
            "",
            "## Next Packet",
            "",
            f"`{review.get('next_packet')}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    for item in review.get("non_claims") or NON_CLAIMS:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def render_queue_metadata_source_safety_review_report(
    review: Mapping[str, Any],
) -> str:
    summary = _mapping(review.get("summary"))
    lines = [
        "# Domain Weaver Queue Metadata Source-Safety Review",
        "",
        f"generated_at: {review.get('generated_at')}",
        f"active_root: `{review.get('active_root')}`",
        f"verdict: `{review.get('verdict')}`",
        "authority: candidate-only; no source request mutation; no replacement request files written; no queue run started; no accepted-state movement",
        "",
        "## Summary",
        "",
        f"- Source-safety review rows: `{summary.get('source_safety_review_row_count', 0)}`",
        f"- Context-gate blocked: `{summary.get('context_gate_blocked_count', 0)}`",
        f"- Stale lifecycle blocked: `{summary.get('stale_lifecycle_blocked_count', 0)}`",
        f"- Terminal lifecycle blocked: `{summary.get('terminal_lifecycle_blocked_count', 0)}`",
        f"- Lineage proof missing: `{summary.get('lineage_proof_missing_count', 0)}`",
        f"- Apply-review rows unblocked: `{summary.get('apply_review_rows_unblocked', 0)}`",
        f"- Replacement request files written: `{summary.get('replacement_request_files_written', 0)}`",
        f"- Source request files mutated: `{summary.get('source_request_files_mutated')}`",
        f"- Graph delta claims: `{summary.get('graph_delta_claim_count', 0)}`",
        "",
        "## Required Packets",
        "",
    ]
    required_packet_counts = _mapping(summary.get("required_packet_counts"))
    if not required_packet_counts:
        lines.append("- none")
    for packet_id, count in required_packet_counts.items():
        lines.append(f"- `{packet_id}`: `{count}`")
    lines.extend(["", "## Source-Safety Rows", ""])
    rows = list(review.get("source_safety_review_rows") or [])
    if not rows:
        lines.append("- none")
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        lines.append(
            f"- `{row.get('source_request_id')}`: `{row.get('review_disposition')}` "
            f"required=`{', '.join(row.get('required_packets') or [])}` "
            f"next_after_clear=`{row.get('next_packet_after_clear')}`"
        )
    lines.extend(["", "## Excluded Rows", ""])
    excluded = list(review.get("excluded_assignment_rows") or [])
    if not excluded:
        lines.append("- none")
    for row in excluded:
        if isinstance(row, Mapping):
            lines.append(
                f"- `{row.get('source_request_id')}`: `{row.get('assignment_disposition')}` "
                f"apply_ready=`{row.get('candidate_reissue_apply_review_ready')}` "
                f"next=`{row.get('next_packet')}`"
            )
    lines.extend(["", "## Next Packets", ""])
    packets = list(review.get("next_packets") or [])
    if not packets:
        lines.append("- none")
    for packet in packets:
        if isinstance(packet, Mapping):
            lines.append(f"- `{packet.get('packet_id')}`: {packet.get('purpose')}")
    lines.extend(
        [
            "",
            "## Next Packet",
            "",
            f"`{review.get('next_packet')}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    for item in review.get("non_claims") or NON_CLAIMS:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def render_context_gate_blocked_request_reissue_report(
    review: Mapping[str, Any],
) -> str:
    summary = _mapping(review.get("summary"))
    lines = [
        "# Domain Weaver Context-Gate Blocked Request Reissue",
        "",
        f"generated_at: {review.get('generated_at')}",
        f"active_root: `{review.get('active_root')}`",
        f"verdict: `{review.get('verdict')}`",
        "authority: candidate-only; candidate body files only; no source request mutation; no replacement request files written; no queue run started; no accepted-state movement",
        "",
        "## Summary",
        "",
        f"- Context-gate reissue rows: `{summary.get('context_gate_reissue_row_count', 0)}`",
        f"- Candidate bodies ready: `{summary.get('candidate_body_ready_count', 0)}`",
        f"- Candidate body files written: `{summary.get('candidate_body_files_written', 0)}`",
        f"- Replacement request files written: `{summary.get('replacement_request_files_written', 0)}`",
        f"- Source request files mutated: `{summary.get('source_request_files_mutated')}`",
        f"- Excluded source-safety rows: `{summary.get('excluded_source_safety_row_count', 0)}`",
        f"- Graph delta claims: `{summary.get('graph_delta_claim_count', 0)}`",
        "",
        "## Reissue Rows",
        "",
    ]
    rows = list(review.get("context_gate_reissue_rows") or [])
    if not rows:
        lines.append("- none")
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        lines.append(
            f"- `{row.get('source_request_id')}` -> `{row.get('candidate_replacement_request_id')}` "
            f"ready=`{row.get('candidate_body_ready')}` body=`{row.get('candidate_replacement_body_path')}`"
        )
    lines.extend(["", "## Excluded Source-Safety Rows", ""])
    excluded = list(review.get("excluded_source_safety_rows") or [])
    if not excluded:
        lines.append("- none")
    for row in excluded:
        if isinstance(row, Mapping):
            lines.append(
                f"- `{row.get('source_request_id')}`: blockers=`{', '.join(row.get('blocker_codes') or [])}` "
                f"required=`{', '.join(row.get('required_packets') or [])}`"
            )
    lines.extend(["", "## Next Packets", ""])
    packets = list(review.get("next_packets") or [])
    if not packets:
        lines.append("- none")
    for packet in packets:
        if isinstance(packet, Mapping):
            lines.append(f"- `{packet.get('packet_id')}`: {packet.get('purpose')}")
    lines.extend(
        [
            "",
            "## Next Packet",
            "",
            f"`{review.get('next_packet')}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    for item in review.get("non_claims") or NON_CLAIMS:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def render_stale_waiting_reconciliation_review_report(
    review: Mapping[str, Any],
) -> str:
    summary = _mapping(review.get("summary"))
    lines = [
        "# Domain Weaver Stale Waiting Reconciliation Review",
        "",
        f"generated_at: {review.get('generated_at')}",
        f"active_root: `{review.get('active_root')}`",
        f"verdict: `{review.get('verdict')}`",
        "authority: candidate-only; decision matrix only; no lifecycle ledger write; no source request mutation; no queue run started; no accepted-state movement",
        "",
        "## Summary",
        "",
        f"- Stale reconciliation rows: `{summary.get('stale_reconciliation_row_count', 0)}`",
        f"- Decision required: `{summary.get('decision_required_count', 0)}`",
        f"- Excluded source-safety rows: `{summary.get('excluded_source_safety_row_count', 0)}`",
        f"- Lifecycle ledger mutated: `{summary.get('lifecycle_ledger_mutated')}`",
        f"- Request files mutated: `{summary.get('request_files_mutated')}`",
        f"- Replacement request files written: `{summary.get('replacement_request_files_written', 0)}`",
        f"- Graph delta claims: `{summary.get('graph_delta_claim_count', 0)}`",
        "",
        "## Reconciliation Rows",
        "",
    ]
    rows = list(review.get("stale_reconciliation_rows") or [])
    if not rows:
        lines.append("- none")
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        lines.append(
            f"- `{row.get('source_request_id')}`: `{row.get('recommended_reconciliation')}` "
            f"source_status=`{row.get('source_status')}` decision_ready=`{row.get('decision_ready')}`"
        )
    lines.extend(["", "## Excluded Source-Safety Rows", ""])
    excluded = list(review.get("excluded_source_safety_rows") or [])
    if not excluded:
        lines.append("- none")
    for row in excluded:
        if isinstance(row, Mapping):
            lines.append(
                f"- `{row.get('source_request_id')}`: blockers=`{', '.join(row.get('blocker_codes') or [])}` "
                f"required=`{', '.join(row.get('required_packets') or [])}`"
            )
    lines.extend(["", "## Next Packets", ""])
    packets = list(review.get("next_packets") or [])
    if not packets:
        lines.append("- none")
    for packet in packets:
        if isinstance(packet, Mapping):
            lines.append(f"- `{packet.get('packet_id')}`: {packet.get('purpose')}")
    lines.extend(
        [
            "",
            "## Next Packet",
            "",
            f"`{review.get('next_packet')}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    for item in review.get("non_claims") or NON_CLAIMS:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def render_stale_waiting_reconciliation_settlement_report(
    settlement: Mapping[str, Any],
) -> str:
    summary = _mapping(settlement.get("summary"))
    lines = [
        "# Domain Weaver Stale Waiting Reconciliation Settlement",
        "",
        f"generated_at: {settlement.get('generated_at')}",
        f"active_root: `{settlement.get('active_root')}`",
        f"verdict: `{settlement.get('verdict')}`",
        "authority: candidate settlement ledger only; no source request mutation; no queue run started; no accepted-state movement",
        "",
        "## Summary",
        "",
        f"- Settlement rows: `{summary.get('settlement_row_count', 0)}`",
        f"- Settlement ready: `{summary.get('settlement_ready_count', 0)}`",
        f"- Blocked rows: `{summary.get('blocked_row_count', 0)}`",
        f"- Candidate lifecycle settlement written: `{summary.get('candidate_lifecycle_settlement_written')}`",
        f"- Accepted lifecycle ledger mutated: `{summary.get('accepted_lifecycle_ledger_mutated')}`",
        f"- Source request files mutated: `{summary.get('source_request_files_mutated')}`",
        f"- Replacement request files written: `{summary.get('replacement_request_files_written', 0)}`",
        f"- Graph delta claims: `{summary.get('graph_delta_claim_count', 0)}`",
        "",
        "## Settlement Rows",
        "",
    ]
    rows = list(settlement.get("settlement_rows") or [])
    if not rows:
        lines.append("- none")
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        lines.append(
            f"- `{row.get('source_request_id')}`: decision=`{row.get('settlement_decision')}` "
            f"ready=`{row.get('settlement_ready')}` source_hash_match=`{row.get('source_hash_matches_review')}`"
        )
    lines.extend(["", "## Next Packets", ""])
    packets = list(settlement.get("next_packets") or [])
    if not packets:
        lines.append("- none")
    for packet in packets:
        if isinstance(packet, Mapping):
            lines.append(f"- `{packet.get('packet_id')}`: {packet.get('purpose')}")
    lines.extend(
        [
            "",
            "## Next Packet",
            "",
            f"`{settlement.get('next_packet')}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    for item in settlement.get("non_claims") or NON_CLAIMS:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def render_generated_mount_creation_report(review: Mapping[str, Any]) -> str:
    summary = _mapping(review.get("summary"))
    lines = [
        "# Domain Weaver Generated Mount Creation For Metadata Reissue",
        "",
        f"generated_at: {review.get('generated_at')}",
        f"active_root: `{review.get('active_root')}`",
        f"verdict: `{review.get('verdict')}`",
        "authority: candidate-only generated Codex mount folders; no workers spawned; no queue run started; no accepted-state movement",
        "",
        "## Summary",
        "",
        f"- Source generated-mount rows: `{summary.get('source_generated_mount_required_row_count', 0)}`",
        f"- Unique mount candidates: `{summary.get('unique_mount_candidate_count', 0)}`",
        f"- Creation candidates ready: `{summary.get('creation_candidate_ready_count', 0)}`",
        f"- Mounts materialized: `{summary.get('mounts_materialized', 0)}`",
        f"- Post materialized mounts: `{summary.get('post_materialized_mount_count', 0)}`",
        f"- Missing required files: `{summary.get('missing_required_file_count', 0)}`",
        f"- Replacement request files written: `{summary.get('replacement_request_files_written', 0)}`",
        f"- Source request files mutated: `{summary.get('source_request_files_mutated')}`",
        f"- Graph delta claims: `{summary.get('graph_delta_claim_count', 0)}`",
        "",
        "## Mount Rows",
        "",
    ]
    rows = list(review.get("generated_mount_creation_rows") or [])
    if not rows:
        lines.append("- none")
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        lines.append(
            f"- `{row.get('mount_id')}` domain=`{row.get('domain_id')}` role=`{row.get('role_id')}` "
            f"sources=`{len(row.get('source_request_ids') or [])}` "
            f"materialized=`{row.get('materialized_by_this_packet')}` "
            f"missing=`{len(row.get('missing_required_files') or [])}`"
        )
    lines.extend(["", "## Next Packets", ""])
    packets = list(review.get("next_packets") or [])
    if not packets:
        lines.append("- none")
    for packet in packets:
        if isinstance(packet, Mapping):
            lines.append(f"- `{packet.get('packet_id')}`: {packet.get('purpose')}")
    lines.extend(
        [
            "",
            "## Next Packet",
            "",
            f"`{review.get('next_packet')}`",
            "",
            "## Non-Claims",
            "",
        ]
    )
    for item in review.get("non_claims") or NON_CLAIMS:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def write_operator_receipt(
    root: Path,
    result: Mapping[str, Any],
    control: Mapping[str, Any],
) -> str:
    stamp = _stamp_from_iso(str(control.get("generated_at") or _utc_now()))
    receipt_path = (
        root
        / DEFAULT_CONTEXT_ROOT
        / "operator_actions"
        / f"{stamp}_domain_weaver_swarm_control_plane_tranche.json"
    )
    receipt = {
        "schema_id": OPERATOR_RECEIPT_SCHEMA_ID,
        "generated_at": control.get("generated_at"),
        "active_root": str(root),
        "action": "domain_weaver_swarm_control_plane_tranche",
        "result": "candidate_swarm_control_plane_written",
        "verdict": control.get("verdict"),
        "outputs": {
            "report_path": result.get("report_path"),
            "readiness_path": result.get("readiness_path"),
            "watch_matrix_path": result.get("watch_matrix_path"),
            "fleet_plan_path": result.get("fleet_plan_path"),
            "context_graph_delta_path": result.get("context_graph_delta_path"),
        },
        "validation_required_next": [
            "focused_swarm_control_plane_tests",
            "json_parse_for_written_artifacts",
            "capsule_pointer_update_if_tranche_is_accepted_as_current_candidate_context",
        ],
        "authority": AUTHORITY,
        "nonclaims": {
            "accepted_state": False,
            "production_ready": False,
            "live_execution": False,
            "materialization_ready": False,
            "workers_spawned": False,
            "queue_started": False,
        },
    }
    receipt_text = _stable_json(receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(receipt_text, encoding="utf-8")
    return _rel(root, receipt_path)


def write_watch_refresh_operator_receipt(
    root: Path,
    result: Mapping[str, Any],
    refresh: Mapping[str, Any],
) -> str:
    stamp = _stamp_from_iso(str(refresh.get("generated_at") or _utc_now()))
    receipt_path = (
        root
        / DEFAULT_CONTEXT_ROOT
        / "operator_actions"
        / f"{stamp}_domain_weaver_limited_watch_matrix_refresh.json"
    )
    receipt = {
        "schema_id": "ion.domain_weaver.limited_watch_matrix_refresh.operator_receipt.v0_1_candidate",
        "generated_at": refresh.get("generated_at"),
        "active_root": str(root),
        "action": "domain_weaver_limited_watch_matrix_refresh",
        "result": "candidate_watch_refresh_written",
        "verdict": refresh.get("verdict"),
        "outputs": {
            "refresh_path": result.get("refresh_path"),
            "report_path": result.get("report_path"),
            "alerts_path": result.get("alerts_path"),
        },
        "summary": refresh.get("summary"),
        "next_packet": refresh.get("next_packet"),
        "authority": AUTHORITY,
        "nonclaims": {
            "accepted_state": False,
            "production_ready": False,
            "live_execution": False,
            "materialization_ready": False,
            "workers_spawned": False,
            "queue_started": False,
        },
    }
    receipt_text = _stable_json(receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(receipt_text, encoding="utf-8")
    return _rel(root, receipt_path)


def write_global_queue_hygiene_operator_receipt(
    root: Path,
    result: Mapping[str, Any],
    hygiene: Mapping[str, Any],
) -> str:
    stamp = _stamp_from_iso(str(hygiene.get("generated_at") or _utc_now()))
    receipt_path = (
        root
        / DEFAULT_CONTEXT_ROOT
        / "operator_actions"
        / f"{stamp}_domain_weaver_global_queue_backlog_context_identity_hygiene.json"
    )
    receipt = {
        "schema_id": "ion.domain_weaver.global_queue_backlog_context_identity_hygiene.operator_receipt.v0_1_candidate",
        "generated_at": hygiene.get("generated_at"),
        "active_root": str(root),
        "action": "domain_weaver_global_queue_backlog_context_identity_hygiene",
        "result": "candidate_global_queue_hygiene_written",
        "verdict": hygiene.get("verdict"),
        "outputs": {
            "hygiene_path": result.get("hygiene_path"),
            "report_path": result.get("report_path"),
            "context_graph_delta_path": result.get("context_graph_delta_path"),
        },
        "summary": hygiene.get("summary"),
        "next_packet": hygiene.get("next_packet"),
        "authority": AUTHORITY,
        "nonclaims": {
            "accepted_state": False,
            "production_ready": False,
            "live_execution": False,
            "materialization_ready": False,
            "workers_spawned": False,
            "queue_started": False,
            "request_files_mutated": False,
        },
    }
    receipt_text = _stable_json(receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(receipt_text, encoding="utf-8")
    return _rel(root, receipt_path)


def write_post_sidecar_global_queue_hygiene_operator_receipt(
    root: Path,
    result: Mapping[str, Any],
    readback: Mapping[str, Any],
) -> str:
    stamp = _stamp_from_iso(str(readback.get("generated_at") or _utc_now()))
    receipt_path = (
        root
        / DEFAULT_CONTEXT_ROOT
        / "operator_actions"
        / f"{stamp}_domain_weaver_post_sidecar_global_queue_hygiene.json"
    )
    receipt = {
        "schema_id": "ion.domain_weaver.post_sidecar_global_queue_hygiene.operator_receipt.v0_1_candidate",
        "generated_at": readback.get("generated_at"),
        "active_root": str(root),
        "action": "domain_weaver_post_sidecar_global_queue_hygiene",
        "result": "candidate_post_sidecar_global_queue_hygiene_written",
        "verdict": readback.get("verdict"),
        "outputs": {
            "readback_path": result.get("readback_path"),
            "report_path": result.get("report_path"),
            "context_graph_delta_path": result.get("context_graph_delta_path"),
        },
        "summary": readback.get("summary"),
        "next_packet": readback.get("next_packet"),
        "authority": AUTHORITY,
        "nonclaims": {
            "accepted_state": False,
            "production_ready": False,
            "live_execution": False,
            "materialization_ready": False,
            "workers_spawned": False,
            "queue_started": False,
            "request_files_mutated": False,
            "replacement_request_files_written": False,
            "automatic_original_agent_reaction_proven": False,
        },
    }
    receipt_text = _stable_json(receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(receipt_text, encoding="utf-8")
    return _rel(root, receipt_path)


def write_global_queue_repair_preview_operator_receipt(
    root: Path,
    result: Mapping[str, Any],
    preview: Mapping[str, Any],
) -> str:
    stamp = _stamp_from_iso(str(preview.get("generated_at") or _utc_now()))
    receipt_path = (
        root
        / DEFAULT_CONTEXT_ROOT
        / "operator_actions"
        / f"{stamp}_domain_weaver_global_queue_backlog_identity_repair_preview.json"
    )
    receipt = {
        "schema_id": "ion.domain_weaver.global_queue_backlog_identity_repair_preview.operator_receipt.v0_1_candidate",
        "generated_at": preview.get("generated_at"),
        "active_root": str(root),
        "action": "domain_weaver_global_queue_backlog_identity_repair_preview",
        "result": "candidate_global_queue_identity_repair_preview_written",
        "verdict": preview.get("verdict"),
        "outputs": {
            "preview_path": result.get("preview_path"),
            "report_path": result.get("report_path"),
            "context_graph_delta_path": result.get("context_graph_delta_path"),
        },
        "summary": preview.get("summary"),
        "next_packet": preview.get("next_packet"),
        "authority": AUTHORITY,
        "nonclaims": {
            "accepted_state": False,
            "production_ready": False,
            "live_execution": False,
            "materialization_ready": False,
            "workers_spawned": False,
            "queue_started": False,
            "request_files_mutated": False,
            "lifecycle_ledger_mutated": False,
        },
    }
    receipt_text = _stable_json(receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(receipt_text, encoding="utf-8")
    return _rel(root, receipt_path)


def write_queue_request_metadata_identity_reissue_operator_receipt(
    root: Path,
    result: Mapping[str, Any],
    worksheet: Mapping[str, Any],
) -> str:
    stamp = _stamp_from_iso(str(worksheet.get("generated_at") or _utc_now()))
    receipt_path = (
        root
        / DEFAULT_CONTEXT_ROOT
        / "operator_actions"
        / f"{stamp}_domain_weaver_queue_request_metadata_identity_reissue.json"
    )
    receipt = {
        "schema_id": "ion.domain_weaver.queue_request_metadata_identity_reissue.operator_receipt.v0_1_candidate",
        "generated_at": worksheet.get("generated_at"),
        "active_root": str(root),
        "action": "domain_weaver_queue_request_metadata_identity_reissue",
        "result": "candidate_metadata_identity_reissue_worksheet_written",
        "verdict": worksheet.get("verdict"),
        "outputs": {
            "worksheet_path": result.get("worksheet_path"),
            "report_path": result.get("report_path"),
            "context_graph_delta_path": result.get("context_graph_delta_path"),
        },
        "summary": worksheet.get("summary"),
        "next_packet": worksheet.get("next_packet"),
        "authority": AUTHORITY,
        "nonclaims": {
            "accepted_state": False,
            "production_ready": False,
            "live_execution": False,
            "materialization_ready": False,
            "workers_spawned": False,
            "queue_started": False,
            "request_files_mutated": False,
            "replacement_requests_written": False,
        },
    }
    receipt_text = _stable_json(receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(receipt_text, encoding="utf-8")
    return _rel(root, receipt_path)


def write_queue_metadata_identity_assignment_operator_receipt(
    root: Path,
    result: Mapping[str, Any],
    assignment: Mapping[str, Any],
) -> str:
    stamp = _stamp_from_iso(str(assignment.get("generated_at") or _utc_now()))
    receipt_path = (
        root
        / DEFAULT_CONTEXT_ROOT
        / "operator_actions"
        / f"{stamp}_domain_weaver_queue_metadata_identity_assignment.json"
    )
    receipt = {
        "schema_id": "ion.domain_weaver.queue_metadata_identity_assignment.operator_receipt.v0_1_candidate",
        "generated_at": assignment.get("generated_at"),
        "active_root": str(root),
        "action": "domain_weaver_queue_metadata_identity_assignment",
        "result": "candidate_metadata_identity_assignment_written",
        "verdict": assignment.get("verdict"),
        "outputs": {
            "assignment_path": result.get("assignment_path"),
            "report_path": result.get("report_path"),
            "context_graph_delta_path": result.get("context_graph_delta_path"),
        },
        "summary": assignment.get("summary"),
        "next_packet": assignment.get("next_packet"),
        "authority": AUTHORITY,
        "nonclaims": {
            "accepted_state": False,
            "production_ready": False,
            "live_execution": False,
            "materialization_ready": False,
            "workers_spawned": False,
            "queue_started": False,
            "request_files_mutated": False,
            "replacement_requests_written": False,
            "mounts_created": False,
        },
    }
    receipt_text = _stable_json(receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(receipt_text, encoding="utf-8")
    return _rel(root, receipt_path)


def write_stale_non_domain_queue_quarantine_settlement_operator_receipt(
    root: Path,
    result: Mapping[str, Any],
    settlement: Mapping[str, Any] | None,
) -> str:
    stamp = _stamp_from_iso(str(result.get("generated_at") or _utc_now()))
    receipt_path = (
        root
        / DEFAULT_CONTEXT_ROOT
        / "operator_actions"
        / f"{stamp}_domain_weaver_stale_non_domain_queue_quarantine_settlement.json"
    )
    receipt = {
        "schema_id": "ion.domain_weaver.stale_non_domain_queue_quarantine_settlement.operator_receipt.v0_1_candidate",
        "generated_at": result.get("generated_at"),
        "active_root": str(root),
        "action": "domain_weaver_stale_non_domain_queue_quarantine_settlement",
        "result": result.get("verdict"),
        "ok": bool(result.get("ok")),
        "outputs": {
            "settlement_path": result.get("settlement_path"),
            "report_path": result.get("report_path"),
            "context_graph_delta_path": result.get("context_graph_delta_path"),
        },
        "summary": _mapping(settlement.get("summary")) if settlement else {},
        "next_packet": result.get("next_packet")
        or (_mapping(settlement).get("next_packet") if settlement else None),
        "authority": AUTHORITY,
        "nonclaims": {
            "accepted_state": False,
            "production_ready": False,
            "live_execution": False,
            "materialization_ready": False,
            "workers_spawned": False,
            "queue_started": False,
            "source_request_files_mutated": False,
            "replacement_request_files_written": False,
            "candidate_quarantine_settlement_written": bool(
                result.get("candidate_quarantine_settlement_written")
            ),
        },
    }
    receipt_text = _stable_json(receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(receipt_text, encoding="utf-8")
    return _rel(root, receipt_path)


def write_queue_metadata_identity_reissue_apply_review_operator_receipt(
    root: Path,
    result: Mapping[str, Any],
    review: Mapping[str, Any],
) -> str:
    stamp = _stamp_from_iso(str(review.get("generated_at") or _utc_now()))
    receipt_path = (
        root
        / DEFAULT_CONTEXT_ROOT
        / "operator_actions"
        / f"{stamp}_domain_weaver_queue_metadata_identity_reissue_apply_review.json"
    )
    receipt = {
        "schema_id": "ion.domain_weaver.queue_metadata_identity_reissue_apply_review.operator_receipt.v0_1_candidate",
        "generated_at": review.get("generated_at"),
        "active_root": str(root),
        "action": "domain_weaver_queue_metadata_identity_reissue_apply_review",
        "result": "candidate_metadata_identity_reissue_apply_review_written",
        "verdict": review.get("verdict"),
        "outputs": {
            "review_path": result.get("review_path"),
            "report_path": result.get("report_path"),
            "context_graph_delta_path": result.get("context_graph_delta_path"),
        },
        "summary": review.get("summary"),
        "next_packet": review.get("next_packet"),
        "authority": AUTHORITY,
        "nonclaims": {
            "accepted_state": False,
            "production_ready": False,
            "live_execution": False,
            "materialization_ready": False,
            "workers_spawned": False,
            "queue_started": False,
            "request_files_mutated": False,
            "replacement_request_files_written": False,
            "candidate_body_files_only": True,
        },
    }
    receipt_text = _stable_json(receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(receipt_text, encoding="utf-8")
    return _rel(root, receipt_path)


def write_queue_metadata_identity_reissue_apply_operator_receipt(
    root: Path,
    result: Mapping[str, Any],
) -> str:
    stamp = _stamp_from_iso(str(result.get("generated_at") or _utc_now()))
    receipt_path = (
        root
        / DEFAULT_CONTEXT_ROOT
        / "operator_actions"
        / f"{stamp}_domain_weaver_queue_metadata_identity_reissue_apply.json"
    )
    receipt = {
        "schema_id": "ion.domain_weaver.queue_metadata_identity_reissue_apply.operator_receipt.v0_1_candidate",
        "generated_at": result.get("generated_at"),
        "active_root": str(root),
        "action": "domain_weaver_queue_metadata_identity_reissue_apply",
        "result": result.get("result"),
        "ok": bool(result.get("ok")),
        "outputs": {
            "written_paths": [
                row.get("candidate_replacement_request_path")
                for row in list(result.get("writes") or [])
                if isinstance(row, Mapping)
            ],
        },
        "replacement_request_files_written": result.get("replacement_request_files_written", 0),
        "source_request_files_mutated": result.get("source_request_files_mutated"),
        "codex_queue_run_started": result.get("codex_queue_run_started"),
        "authority": AUTHORITY,
        "nonclaims": {
            "accepted_state": False,
            "production_ready": False,
            "live_execution": False,
            "materialization_ready": False,
            "workers_spawned": False,
            "queue_started": False,
            "source_request_files_mutated": False,
            "exact_replacement_request_write_only": True,
        },
    }
    receipt_text = _stable_json(receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(receipt_text, encoding="utf-8")
    return _rel(root, receipt_path)


def write_queue_metadata_source_safety_review_operator_receipt(
    root: Path,
    result: Mapping[str, Any],
    review: Mapping[str, Any],
) -> str:
    stamp = _stamp_from_iso(str(review.get("generated_at") or _utc_now()))
    receipt_path = (
        root
        / DEFAULT_CONTEXT_ROOT
        / "operator_actions"
        / f"{stamp}_domain_weaver_queue_metadata_source_safety_review.json"
    )
    receipt = {
        "schema_id": "ion.domain_weaver.queue_metadata_source_safety_review.operator_receipt.v0_1_candidate",
        "generated_at": review.get("generated_at"),
        "active_root": str(root),
        "action": "domain_weaver_queue_metadata_source_safety_review",
        "result": "candidate_metadata_source_safety_review_written",
        "verdict": review.get("verdict"),
        "outputs": {
            "review_path": result.get("review_path"),
            "report_path": result.get("report_path"),
            "context_graph_delta_path": result.get("context_graph_delta_path"),
        },
        "summary": review.get("summary"),
        "next_packet": review.get("next_packet"),
        "authority": AUTHORITY,
        "nonclaims": {
            "accepted_state": False,
            "production_ready": False,
            "live_execution": False,
            "materialization_ready": False,
            "workers_spawned": False,
            "queue_started": False,
            "request_files_mutated": False,
            "replacement_request_files_written": False,
            "apply_review_rows_unblocked": False,
        },
    }
    receipt_text = _stable_json(receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(receipt_text, encoding="utf-8")
    return _rel(root, receipt_path)


def write_context_gate_blocked_request_reissue_operator_receipt(
    root: Path,
    result: Mapping[str, Any],
    review: Mapping[str, Any],
) -> str:
    stamp = _stamp_from_iso(str(review.get("generated_at") or _utc_now()))
    receipt_path = (
        root
        / DEFAULT_CONTEXT_ROOT
        / "operator_actions"
        / f"{stamp}_domain_weaver_context_gate_blocked_request_reissue.json"
    )
    receipt = {
        "schema_id": "ion.domain_weaver.context_gate_blocked_request_reissue.operator_receipt.v0_1_candidate",
        "generated_at": review.get("generated_at"),
        "active_root": str(root),
        "action": "domain_weaver_context_gate_blocked_request_reissue",
        "result": "candidate_context_gate_reissue_review_written",
        "verdict": review.get("verdict"),
        "outputs": {
            "review_path": result.get("review_path"),
            "report_path": result.get("report_path"),
            "context_graph_delta_path": result.get("context_graph_delta_path"),
        },
        "summary": review.get("summary"),
        "next_packet": review.get("next_packet"),
        "authority": AUTHORITY,
        "nonclaims": {
            "accepted_state": False,
            "production_ready": False,
            "live_execution": False,
            "materialization_ready": False,
            "workers_spawned": False,
            "queue_started": False,
            "request_files_mutated": False,
            "replacement_request_files_written": False,
            "candidate_body_files_only": True,
        },
    }
    receipt_text = _stable_json(receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(receipt_text, encoding="utf-8")
    return _rel(root, receipt_path)


def write_context_gate_reissue_apply_operator_receipt(
    root: Path,
    result: Mapping[str, Any],
) -> str:
    stamp = _stamp_from_iso(str(result.get("generated_at") or _utc_now()))
    receipt_path = (
        root
        / DEFAULT_CONTEXT_ROOT
        / "operator_actions"
        / f"{stamp}_domain_weaver_context_gate_reissue_apply.json"
    )
    receipt = {
        "schema_id": "ion.domain_weaver.context_gate_reissue_apply.operator_receipt.v0_1_candidate",
        "generated_at": result.get("generated_at"),
        "active_root": str(root),
        "action": "domain_weaver_context_gate_reissue_apply",
        "result": result.get("result"),
        "ok": bool(result.get("ok")),
        "outputs": {
            "written_paths": [
                row.get("candidate_replacement_request_path")
                for row in list(result.get("writes") or [])
                if isinstance(row, Mapping)
            ],
        },
        "replacement_request_files_written": result.get("replacement_request_files_written", 0),
        "source_request_files_mutated": result.get("source_request_files_mutated"),
        "codex_queue_run_started": result.get("codex_queue_run_started"),
        "authority": AUTHORITY,
        "nonclaims": {
            "accepted_state": False,
            "production_ready": False,
            "live_execution": False,
            "materialization_ready": False,
            "workers_spawned": False,
            "queue_started": False,
            "source_request_files_mutated": False,
            "exact_replacement_request_write_only": True,
        },
    }
    receipt_text = _stable_json(receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(receipt_text, encoding="utf-8")
    return _rel(root, receipt_path)


def write_exact_reissue_request_dispatch_readiness_operator_receipt(
    root: Path,
    result: Mapping[str, Any],
    readiness: Mapping[str, Any],
) -> str:
    stamp = _stamp_from_iso(str(readiness.get("generated_at") or _utc_now()))
    receipt_path = (
        root
        / DEFAULT_CONTEXT_ROOT
        / "operator_actions"
        / f"{stamp}_domain_weaver_exact_reissue_request_dispatch_readiness.json"
    )
    receipt = {
        "schema_id": "ion.domain_weaver.exact_reissue_request_dispatch_readiness.operator_receipt.v0_1_candidate",
        "generated_at": readiness.get("generated_at"),
        "active_root": str(root),
        "action": "domain_weaver_exact_reissue_request_dispatch_readiness",
        "result": "candidate_exact_reissue_request_dispatch_readiness_written",
        "verdict": readiness.get("verdict"),
        "outputs": {
            "readiness_path": result.get("readiness_path"),
            "report_path": result.get("report_path"),
            "context_graph_delta_path": result.get("context_graph_delta_path"),
        },
        "summary": readiness.get("summary"),
        "next_packet": readiness.get("next_packet"),
        "authority": AUTHORITY,
        "nonclaims": {
            "accepted_state": False,
            "production_ready": False,
            "live_execution": False,
            "materialization_ready": False,
            "workers_spawned": False,
            "queue_started": False,
            "source_request_files_mutated": False,
            "replacement_request_files_written": False,
            "start_commands_executed": False,
            "worker_returns_are_product_state": False,
        },
    }
    receipt_text = _stable_json(receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(receipt_text, encoding="utf-8")
    return _rel(root, receipt_path)


def write_stale_waiting_reconciliation_review_operator_receipt(
    root: Path,
    result: Mapping[str, Any],
    review: Mapping[str, Any],
) -> str:
    stamp = _stamp_from_iso(str(review.get("generated_at") or _utc_now()))
    receipt_path = (
        root
        / DEFAULT_CONTEXT_ROOT
        / "operator_actions"
        / f"{stamp}_domain_weaver_stale_waiting_reconciliation_review.json"
    )
    receipt = {
        "schema_id": "ion.domain_weaver.stale_waiting_reconciliation_review.operator_receipt.v0_1_candidate",
        "generated_at": review.get("generated_at"),
        "active_root": str(root),
        "action": "domain_weaver_stale_waiting_reconciliation_review",
        "result": "candidate_stale_waiting_reconciliation_review_written",
        "verdict": review.get("verdict"),
        "outputs": {
            "review_path": result.get("review_path"),
            "report_path": result.get("report_path"),
            "context_graph_delta_path": result.get("context_graph_delta_path"),
        },
        "summary": review.get("summary"),
        "next_packet": review.get("next_packet"),
        "authority": AUTHORITY,
        "nonclaims": {
            "accepted_state": False,
            "production_ready": False,
            "live_execution": False,
            "materialization_ready": False,
            "workers_spawned": False,
            "queue_started": False,
            "request_files_mutated": False,
            "replacement_request_files_written": False,
            "lifecycle_ledger_mutated": False,
            "decision_matrix_only": True,
        },
    }
    receipt_text = _stable_json(receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(receipt_text, encoding="utf-8")
    return _rel(root, receipt_path)


def write_stale_waiting_reconciliation_settlement_operator_receipt(
    root: Path,
    result: Mapping[str, Any],
    settlement: Mapping[str, Any] | None,
) -> str:
    stamp = _stamp_from_iso(str(result.get("generated_at") or _utc_now()))
    receipt_path = (
        root
        / DEFAULT_CONTEXT_ROOT
        / "operator_actions"
        / f"{stamp}_domain_weaver_stale_waiting_reconciliation_settlement.json"
    )
    receipt = {
        "schema_id": "ion.domain_weaver.stale_waiting_reconciliation_settlement.operator_receipt.v0_2_candidate",
        "generated_at": result.get("generated_at"),
        "active_root": str(root),
        "action": "domain_weaver_stale_waiting_reconciliation_settlement",
        "result": result.get("verdict"),
        "ok": bool(result.get("ok")),
        "outputs": {
            "settlement_path": result.get("settlement_path"),
            "report_path": result.get("report_path"),
            "context_graph_delta_path": result.get("context_graph_delta_path"),
        },
        "summary": _mapping(settlement.get("summary")) if settlement else {},
        "next_packet": result.get("next_packet")
        or (_mapping(settlement).get("next_packet") if settlement else None),
        "authority": AUTHORITY,
        "nonclaims": {
            "accepted_state": False,
            "production_ready": False,
            "live_execution": False,
            "materialization_ready": False,
            "workers_spawned": False,
            "queue_started": False,
            "source_request_files_mutated": False,
            "replacement_request_files_written": False,
            "candidate_lifecycle_settlement_written": bool(
                result.get("candidate_lifecycle_settlement_written")
            ),
            "accepted_lifecycle_ledger_mutated": False,
        },
    }
    receipt_text = _stable_json(receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(receipt_text, encoding="utf-8")
    return _rel(root, receipt_path)


def write_generated_mount_creation_operator_receipt(
    root: Path,
    result: Mapping[str, Any],
    review: Mapping[str, Any],
) -> str:
    stamp = _stamp_from_iso(str(review.get("generated_at") or _utc_now()))
    receipt_path = (
        root
        / DEFAULT_CONTEXT_ROOT
        / "operator_actions"
        / f"{stamp}_domain_weaver_generated_mount_creation_for_metadata_reissue.json"
    )
    receipt = {
        "schema_id": "ion.domain_weaver.generated_mount_creation_for_metadata_reissue.operator_receipt.v0_1_candidate",
        "generated_at": review.get("generated_at"),
        "active_root": str(root),
        "action": "domain_weaver_generated_mount_creation_for_metadata_reissue",
        "result": "candidate_generated_mount_creation_written",
        "verdict": review.get("verdict"),
        "outputs": {
            "review_path": result.get("review_path"),
            "report_path": result.get("report_path"),
            "context_graph_delta_path": result.get("context_graph_delta_path"),
        },
        "summary": review.get("summary"),
        "next_packet": review.get("next_packet"),
        "authority": AUTHORITY,
        "nonclaims": {
            "accepted_state": False,
            "production_ready": False,
            "live_execution": False,
            "materialization_ready": False,
            "workers_spawned": False,
            "queue_started": False,
            "request_files_mutated": False,
            "replacement_request_files_written": False,
            "candidate_mount_folders_only": True,
        },
    }
    receipt_text = _stable_json(receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(receipt_text, encoding="utf-8")
    return _rel(root, receipt_path)


def build_command_structure() -> dict[str, Any]:
    return {
        "root_steward": "root_steward_command",
        "domain_stewards": [
            "domain_steward_council",
            "queue_worker_steward",
            "fleet_spawn_lifecycle",
            "comms_autoreaction_auditor",
        ],
        "watch_agents": ["watch_command_center"],
        "audit_agents": [
            "receipt_proof_librarian",
            "action_gateway_freshness_guard",
            "proposal_wave_validator",
        ],
        "context_graph_agents": ["context_graph_cartographer"],
        "queue_and_worker_agents": ["fleet_spawn_lifecycle", "queue_worker_steward"],
        "nemesis_vice_review": ["nemesis_vice_review"],
        "fanin_synthesizer": ["fanin_synthesizer"],
        "escalation_logic": ["escalation_packet_router"],
        "operator_truth_surface": ["operator_truth_surface_adapter"],
    }


def source_evidence(root: Path) -> list[dict[str, Any]]:
    refs = [
        "pyproject.toml",
        "ION/REPO_AUTHORITY.md",
        DOMAIN_CAPSULE_PATH.as_posix(),
        PROJECTION_PATH.as_posix(),
        SELF_EVOLUTION_READINESS_PATH.as_posix(),
        PROPOSAL_FANIN_PATH.as_posix(),
        "ION/04_packages/kernel/ion_domain_weaver_pressure_wave.py",
        "ION/04_packages/kernel/ion_domain_weaver_proposal_wave.py",
        "ION/04_packages/kernel/ion_domain_weaver_spawn_request_dispatcher.py",
    ]
    return [_evidence_ref(root, value) for value in refs]


def next_packets(verdict: str, blockers: Sequence[Mapping[str, Any]]) -> dict[str, list[str]]:
    must_fix = [
        "PCKT-DOMAIN-WEAVER-PROPOSAL-WAVE-SCHEMA-PATH-NONCLAIM-VALIDATOR-V0_1",
        "PCKT-SESSIONSTART-CANDIDATE-RECEIPT-LANE-V0_1",
        "PCKT-DOMAIN-WEAVER-GLOBAL-QUEUE-BACKLOG-CONTEXT-IDENTITY-HYGIENE-V0_1",
        "PCKT-DOMAIN-WEAVER-COMMS-AUTOREACTION-PROOF-V0_2-ORIGINAL-WORKER-BOUND",
    ]
    if any(row.get("code") == "ACCEPTED_PROJECTION_OR_MATERIALIZATION_BLOCKED" for row in blockers):
        must_fix.insert(0, "PCKT-DOMAIN-WEAVER-ACCEPTED-PROJECTION-AND-MATERIALIZATION-GATE-REVIEW-V0_1")
    can_run = [
        "PCKT-DOMAIN-WEAVER-LIMITED-WATCH-MATRIX-REFRESH-V0_1",
        "PCKT-DOMAIN-WEAVER-BOUNDARY-CAPPED-CANDIDATE-FANOUT-WAVE-V0_4",
        "PCKT-DOMAIN-WEAVER-FLEET-SPAWN-ROW-PREVIEW-V0_1",
        "PCKT-DOMAIN-WEAVER-NEMESIS-SWARM-FANIN-REVIEW-V0_1",
        "PCKT-LEAD-DEV-OPERATOR-DASHBOARD-EVIDENCE-V0_1",
    ]
    if verdict == "READY_FOR_SUPERVISED_SELF_EVOLUTION_CANDIDATE_WAVE":
        can_run.insert(0, "PCKT-DOMAIN-WEAVER-SUPERVISED-SELF-EVOLUTION-CANDIDATE-WAVE-V0_1")
    return {
        "A_must_fix_before_serious_supervised_self_evolution": must_fix,
        "B_can_run_during_limited_supervised_swarm_work": can_run,
        "C_later_hardening": [
            "PCKT-DOMAIN-WEAVER-DEDICATED-LEAD-DEV-SKILL-V0_1",
            "PCKT-DOMAIN-WEAVER-DOMAIN-OWNED-WATCH-DAEMON-V0_1",
            "PCKT-DOMAIN-WEAVER-RECURSIVE-NATIVE-SPAWN-ONE-CHILD-PROBE-V0_1",
            "PCKT-DOMAIN-WEAVER-FULL-HANDLER-PARITY-AUDIT-V0_1",
        ],
    }


def nemesis_dissent(verdict: str, blockers: Sequence[Mapping[str, Any]]) -> str:
    high = [row.get("code") for row in blockers if row.get("severity") in {"critical", "high"}]
    return (
        "The swarm control plane is useful only if it remains a candidate control surface. "
        "It must not be described as autonomous production readiness, accepted-state movement, "
        "or proof that original automatic worker reaction exists. Current verdict is "
        f"{verdict}; high-risk blockers still present: {', '.join(map(str, high)) or 'none'}. "
        "Any over-cap fanout without fan-in owner, queue hygiene gate, identity-bound context, "
        "and Nemesis review should stop the wave."
    )


def _swarm_blockers(
    root_proof: Mapping[str, Any],
    watch: Mapping[str, Any],
    fleet: Mapping[str, Any],
    proposal: Mapping[str, Any],
    self_blockers: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    if not root_proof.get("proof_ok"):
        blockers.append(_blocker("critical", "ROOT_PROOF_MISSING", "Active-root proof is incomplete."))
    if int(_mapping(watch.get("coverage")).get("target_count") or 0) < 12:
        blockers.append(_blocker("high", "WATCH_MATRIX_TOO_NARROW", "Watch matrix has insufficient target coverage."))
    if int(fleet.get("lane_count") or 0) < 12:
        blockers.append(_blocker("high", "FLEET_PLAN_TOO_NARROW", "Fleet plan has insufficient lane coverage."))
    if not proposal.get("ok"):
        blockers.append(
            _blocker(
                "high",
                "PROPOSAL_WAVE_VALIDATOR_FAILED",
                "Proposal-wave validator did not pass for current fan-in returns.",
                evidence=[PROPOSAL_FANIN_PATH.as_posix()],
            )
        )
    for row in self_blockers:
        code = str(row.get("code") or "")
        if code in {
            "MATERIALIZATION_READY_FALSE",
            "ACCEPTED_STATE_WRITE_GATE_NOT_GRANTED_FOR_PROJECTION",
            "AUTOMATIC_ORIGINAL_AGENT_REACTION_NOT_PROVEN",
            "GLOBAL_QUEUE_BACKLOG_CONTEXT_IDENTITY_HYGIENE_NOT_CLEAN",
            "SEMANTIC_ALIAS_ACCEPTED_STATE_APPLY_GATE_NOT_GRANTED",
        }:
            blockers.append(
                _blocker(
                    "critical" if "MATERIALIZATION" in code or "ACCEPTED_STATE" in code else "high",
                    code,
                    str(row.get("detail") or "Self-evolution readiness blocker remains."),
                    evidence=list(row.get("evidence") or []),
                )
            )
    blockers.append(
        _blocker(
            "medium",
            "SESSIONSTART_CANDIDATE_RECEIPT_LANE_MISSING",
            "SessionStart still lacks the shared candidate receipt lane.",
            evidence=[".codex/hooks/ion_session_start_context.py"],
        )
    )
    return _dedupe_blockers(blockers)


def _swarm_verdict(
    root_proof: Mapping[str, Any],
    watch: Mapping[str, Any],
    fleet: Mapping[str, Any],
    proposal: Mapping[str, Any],
    blockers: Sequence[Mapping[str, Any]],
) -> str:
    if not root_proof.get("proof_ok"):
        return "NOT_READY_BLOCKED_BY_ROOT_PROOF_MISSING"
    critical_codes = {str(row.get("code")) for row in blockers if row.get("severity") == "critical"}
    if not watch.get("coverage") or int(_mapping(watch.get("coverage")).get("target_count") or 0) < 12:
        return "READY_FOR_CONTROL_PLANE_ONLY"
    if int(fleet.get("lane_count") or 0) < 12:
        return "READY_FOR_CONTROL_PLANE_ONLY"
    if not proposal.get("validator_available"):
        return "READY_FOR_CONTROL_PLANE_ONLY"
    if critical_codes:
        return "READY_FOR_LIMITED_SWARM_WATCH_AND_FANOUT"
    if proposal.get("ok"):
        return "READY_FOR_SUPERVISED_SELF_EVOLUTION_CANDIDATE_WAVE"
    return "READY_FOR_LIMITED_SWARM_WATCH_AND_FANOUT"


def _self_readiness_blockers(self_readiness: Mapping[str, Any]) -> list[dict[str, Any]]:
    blockers = self_readiness.get("blockers_ranked")
    if isinstance(blockers, list):
        return [dict(row) for row in blockers if isinstance(row, Mapping)]
    return []


def _build_watch_observation(
    root: Path,
    target: Mapping[str, Any],
    *,
    blocker_codes: set[str],
    proposal_validation: Mapping[str, Any],
    queue_summary: Mapping[str, Any],
    spawn_summary: Mapping[str, Any],
) -> dict[str, Any]:
    target_id = str(target.get("target_id") or "unknown")
    alerts: list[dict[str, Any]] = []
    missing = list(target.get("missing_required_evidence") or [])
    if missing:
        alerts.append(
            _watch_alert(
                "high",
                "WATCH_EVIDENCE_MISSING",
                target_id,
                f"Required evidence is missing: {', '.join(map(str, missing))}.",
                response_packet=str(target.get("response_packet") or ""),
            )
        )

    if target_id in {"queue_state", "global_queue_hygiene"} and (
        "GLOBAL_QUEUE_BACKLOG_CONTEXT_IDENTITY_HYGIENE_NOT_CLEAN" in blocker_codes
        or int(queue_summary.get("queued_count") or 0) > 0
        or int(queue_summary.get("running_count") or 0) > 0
    ):
        severity = (
            "high"
            if "GLOBAL_QUEUE_BACKLOG_CONTEXT_IDENTITY_HYGIENE_NOT_CLEAN" in blocker_codes
            else "medium"
        )
        alerts.append(
            _watch_alert(
                severity,
                "QUEUE_HYGIENE_REQUIRES_EXACT_PATH_ONLY",
                target_id,
                "Queue state requires exact-path handling; general queue processing remains blocked.",
                response_packet=str(target.get("response_packet") or ""),
                evidence=[QUEUE_PATH.as_posix(), QUEUE_RUNNER_STATE_PATH.as_posix()],
            )
        )

    if target_id in {"spawn_request_rows", "worker_state"} and int(
        spawn_summary.get("requested_count") or 0
    ) > 0:
        alerts.append(
            _watch_alert(
                "medium",
                "SPAWN_REQUEST_ROWS_AWAIT_DISPATCH_OR_SETTLEMENT",
                target_id,
                "Worker-local spawn request rows exist and must stay validation/fan-in bound.",
                response_packet=str(target.get("response_packet") or ""),
            )
        )

    if target_id in {"unread_comms", "carrier_failures"} and (
        "AUTOMATIC_ORIGINAL_AGENT_REACTION_NOT_PROVEN" in blocker_codes
    ):
        alerts.append(
            _watch_alert(
                "high",
                "ORIGINAL_AUTOREACTION_NOT_PROVEN",
                target_id,
                "Alternate-worker recovery is carrier-intake proof only; original automatic reaction remains unproven.",
                response_packet=str(target.get("response_packet") or ""),
            )
        )

    if target_id == "proposal_wave_state" and not proposal_validation.get("ok"):
        alerts.append(
            _watch_alert(
                "high",
                "PROPOSAL_WAVE_VALIDATION_FAILED",
                target_id,
                "Proposal-wave path/schema/nonclaim validation failed.",
                response_packet=str(target.get("response_packet") or ""),
                evidence=[PROPOSAL_FANIN_PATH.as_posix()],
            )
        )

    if target_id == "receipt_gaps" and (
        "SESSIONSTART_CANDIDATE_RECEIPT_LANE_MISSING" in blocker_codes
    ):
        alerts.append(
            _watch_alert(
                "medium",
                "SESSIONSTART_RECEIPT_LANE_MISSING",
                target_id,
                "SessionStart does not yet write through the shared candidate receipt lane.",
                response_packet=str(target.get("response_packet") or ""),
                evidence=[".codex/hooks/ion_session_start_context.py"],
            )
        )

    if target_id in {"accepted_state_confusion", "materialization_gate"}:
        if "ACCEPTED_STATE_WRITE_GATE_NOT_GRANTED_FOR_PROJECTION" in blocker_codes:
            alerts.append(
                _watch_alert(
                    "critical",
                    "ACCEPTED_PROJECTION_GATE_NOT_GRANTED",
                    target_id,
                    "Accepted projection write authority is not granted.",
                    response_packet=str(target.get("response_packet") or ""),
                    evidence=[PROJECTION_PATH.as_posix()],
                )
            )
        if "MATERIALIZATION_READY_FALSE" in blocker_codes:
            alerts.append(
                _watch_alert(
                    "critical",
                    "MATERIALIZATION_READY_FALSE",
                    target_id,
                    "Materialization readiness remains false.",
                    response_packet=str(target.get("response_packet") or ""),
                    evidence=[DOMAIN_CAPSULE_PATH.as_posix()],
                )
            )

    if target_id == "semantic_alias_drift" and (
        "SEMANTIC_ALIAS_ACCEPTED_STATE_APPLY_GATE_NOT_GRANTED" in blocker_codes
    ):
        alerts.append(
            _watch_alert(
                "critical",
                "SEMANTIC_ALIAS_ACCEPTED_APPLY_GATE_NOT_GRANTED",
                target_id,
                "Semantic alias accepted projection/mount-manifest apply authority is not granted.",
                response_packet=str(target.get("response_packet") or ""),
            )
        )

    level = _highest_alert_level(alerts)
    return {
        "target_id": target_id,
        "title": target.get("title"),
        "watcher_role_id": target.get("watcher_role_id"),
        "watcher_domain_id": target.get("watcher_domain_id"),
        "response_packet": target.get("response_packet"),
        "candidate_graph_delta_id": target.get("candidate_graph_delta_id"),
        "evidence_state": target.get("status"),
        "alert_level": level,
        "alerts": alerts,
        "state_movement_allowed": False,
    }


def _watch_alert(
    severity: str,
    code: str,
    target_id: str,
    detail: str,
    *,
    response_packet: str,
    evidence: Sequence[str] | None = None,
) -> dict[str, Any]:
    return {
        "severity": severity,
        "code": code,
        "target_id": target_id,
        "detail": detail,
        "response_packet": response_packet,
        "evidence": list(evidence or []),
    }


def _highest_alert_level(alerts: Sequence[Mapping[str, Any]]) -> str:
    if not alerts:
        return "info"
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    return min((str(alert.get("severity") or "info") for alert in alerts), key=lambda value: order.get(value, 99))


def _limited_watch_verdict(severity_counts: Mapping[str, int]) -> str:
    if int(severity_counts.get("critical") or 0) > 0:
        return "WATCH_REFRESH_ALERTS_ACTIVE_LIMITED_FANOUT_ONLY"
    if int(severity_counts.get("high") or 0) > 0:
        return "WATCH_REFRESH_HIGH_ALERTS_ACTIVE"
    if int(severity_counts.get("medium") or 0) > 0:
        return "WATCH_REFRESH_MEDIUM_ALERTS_ACTIVE"
    return "WATCH_REFRESH_CLEAR_FOR_NEXT_LIMITED_PACKET"


def _limited_watch_graph_deltas(
    root: Path,
    *,
    generated_at: str,
    observations: Sequence[Mapping[str, Any]],
    alerts: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    claims = [
        {
            "id": f"domain_weaver.limited_watch.{observation.get('target_id')}",
            "kind": "watch_observation",
            "state": observation.get("alert_level"),
            "evidence": [
                DEFAULT_WATCH_MATRIX_NAME,
                DEFAULT_READINESS_NAME,
            ],
            "value": {
                "watcher_role_id": observation.get("watcher_role_id"),
                "watcher_domain_id": observation.get("watcher_domain_id"),
                "response_packet": observation.get("response_packet"),
                "alert_count": len(observation.get("alerts") or []),
            },
        }
        for observation in observations
    ]
    claims.extend(
        {
            "id": f"domain_weaver.limited_watch.alert.{alert.get('target_id')}.{alert.get('code')}",
            "kind": "watch_alert",
            "state": alert.get("severity"),
            "evidence": list(alert.get("evidence") or []),
            "value": {
                "detail": alert.get("detail"),
                "response_packet": alert.get("response_packet"),
            },
        }
        for alert in alerts
    )
    return {
        "schema_id": "ion.domain_weaver.limited_watch.context_graph_deltas.v0_1_candidate",
        "generated_at": generated_at,
        "active_root": str(root),
        "status": "candidate_limited_watch_graph_deltas_built",
        "upsert_claims": claims,
        "write_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _watch_queue_summary(root: Path) -> dict[str, Any]:
    queue = _read_json(root / QUEUE_PATH)
    runner = _read_json(root / QUEUE_RUNNER_STATE_PATH)
    rows = queue.get("requests")
    if not isinstance(rows, list):
        rows = []
    status_counts: dict[str, int] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        status = str(row.get("status") or "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    active_run = runner.get("active_run")
    return {
        "queue_path": QUEUE_PATH.as_posix(),
        "runner_state_path": QUEUE_RUNNER_STATE_PATH.as_posix(),
        "request_count": len(rows),
        "status_counts": status_counts,
        "queued_count": status_counts.get("QUEUED_FOR_CODEX_CARRIER", 0),
        "running_count": status_counts.get("CODEX_CLI_RUNNING", 0)
        + status_counts.get("RUNNING", 0),
        "active_run_present": bool(active_run),
    }


def _watch_spawn_request_summary(root: Path) -> dict[str, Any]:
    paths = sorted(
        (root / "ION/05_context/current/domain_weaver/workers").glob(
            "*/context/spawn_requests/*.spawn_request.json"
        )
    )
    status_counts: dict[str, int] = {}
    for path in paths:
        payload = _read_json(path)
        status = str(payload.get("status") or "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "spawn_request_count": len(paths),
        "requested_count": status_counts.get("requested", 0),
        "status_counts": status_counts,
        "sample_paths": [_rel(root, path) for path in paths[:8]],
    }


def _load_work_request_rows(root: Path) -> list[dict[str, Any]]:
    request_root = root / CODEX_WORK_REQUESTS_DIR
    if not request_root.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(request_root.glob("*.json")):
        payload = _read_json(path)
        if not payload:
            continue
        rel_path = _rel(root, path)
        row = dict(payload)
        row.setdefault("path", rel_path)
        row["source_path"] = rel_path
        row["source_sha256"] = _sha256_file(path)
        rows.append(row)
    return rows


def _global_spawn_request_summary(root: Path) -> dict[str, Any]:
    paths = sorted(root.glob(WORKER_SPAWN_REQUESTS_GLOB))
    status_counts: dict[str, int] = {}
    domain_counts: dict[str, int] = {}
    role_counts: dict[str, int] = {}
    rows: list[dict[str, Any]] = []
    for path in paths:
        payload = _read_json(path)
        status = str(payload.get("status") or "unknown")
        domain = str(payload.get("requested_domain") or "unknown")
        role = str(payload.get("requested_role_id") or "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        role_counts[role] = role_counts.get(role, 0) + 1
        rows.append(
            {
                "path": _rel(root, path),
                "sha256": _sha256_file(path),
                "status": status,
                "requested_domain": payload.get("requested_domain"),
                "requested_packet": payload.get("requested_packet"),
                "requested_role_id": payload.get("requested_role_id"),
                "requested_callsign": payload.get("requested_callsign"),
                "parent_worker_id": payload.get("parent_worker_id"),
                "domain_context_package": payload.get("domain_context_package"),
            }
        )
    return {
        "spawn_request_count": len(paths),
        "requested_count": status_counts.get("requested", 0),
        "enqueued_count": status_counts.get("enqueued_by_dispatcher", 0),
        "rejected_count": status_counts.get("rejected_by_dispatcher", 0),
        "status_counts": status_counts,
        "domain_counts": domain_counts,
        "role_counts": role_counts,
        "sample_rows": rows[:12],
    }


def _global_queue_hygiene_blockers(
    *,
    worker_readiness: Mapping[str, Any],
    worker_backlog: Mapping[str, Any],
    governance: Mapping[str, Any],
    spawn_summary: Mapping[str, Any],
) -> list[dict[str, Any]]:
    summary = _mapping(worker_readiness.get("summary"))
    backlog_summary = _mapping(worker_backlog.get("summary"))
    governance_summary = _mapping(governance.get("summary"))
    blockers: list[dict[str, Any]] = []
    if list(worker_readiness.get("blockers") or []):
        blockers.append(
            _blocker(
                "high",
                "GLOBAL_QUEUE_BACKLOG_CONTEXT_IDENTITY_HYGIENE_NOT_CLEAN",
                "Global worker-start readiness still has queue/context/identity blockers; exact request paths remain the only lawful start shape.",
                evidence=[CODEX_WORK_REQUESTS_DIR.as_posix()],
            )
        )
    if int(summary.get("missing_lane_request_count") or 0) > 0:
        blockers.append(
            _blocker(
                "high",
                "QUEUEABLE_REQUESTS_MISSING_LANE_ID",
                "At least one queueable request lacks a lane binding.",
            )
        )
    if any(code == "queueable_requests_missing_domain_id" for code in list(worker_readiness.get("blockers") or [])):
        blockers.append(
            _blocker(
                "high",
                "QUEUEABLE_REQUESTS_MISSING_DOMAIN_ID",
                "At least one queueable request lacks a domain binding.",
            )
        )
    if int(summary.get("capsule_identity_blocked_request_count") or 0) > 0:
        blockers.append(
            _blocker(
                "high",
                "WORKING_CAPSULE_IDENTITY_BLOCKED",
                "One or more queueable requests lack a valid unique working capsule identity.",
            )
        )
    if int(summary.get("blocked_context_gate_request_count") or 0) > 0:
        blockers.append(
            _blocker(
                "high",
                "CONTEXT_GATE_BLOCKED_REQUESTS_PRESENT",
                "One or more queued requests are preserved as blocked by the context gate.",
            )
        )
    if bool(backlog_summary.get("shared_capsule_concurrency_hazard")):
        blockers.append(
            _blocker(
                "critical",
                "SHARED_CAPSULE_CONCURRENCY_HAZARD",
                "Multiple queueable rows would risk shared-capsule worker identity if processed through the general queue.",
            )
        )
    if int(governance_summary.get("stale_waiting_request_count") or 0) > 0:
        blockers.append(
            _blocker(
                "medium",
                "STALE_WAITING_REQUESTS_PRESENT",
                "Stale waiting requests need reconciliation or supersession before any broad worker-start claim.",
            )
        )
    if int(governance_summary.get("terminal_repair_request_count") or 0) > 0:
        blockers.append(
            _blocker(
                "medium",
                "TERMINAL_REPAIR_BACKLOG_PRESENT",
                "Terminal failed/template-invalid rows still need lifecycle classification or repair packets.",
            )
        )
    if int(governance_summary.get("actionable_duplicate_group_count") or 0) > 0:
        blockers.append(
            _blocker(
                "medium",
                "ACTIONABLE_DUPLICATE_REQUEST_GROUPS_PRESENT",
                "Actionable duplicate request groups remain in the historical work-request set.",
            )
        )
    if int(spawn_summary.get("requested_count") or 0) > 0:
        blockers.append(
            _blocker(
                "medium",
                "REQUESTED_SPAWN_ROWS_AWAIT_DISPATCH",
                "Worker-local spawn rows remain requested and need dispatcher validation or rejection.",
            )
        )
    return _dedupe_blockers(blockers)


def _global_queue_hygiene_repair_packets(
    *,
    worker_readiness: Mapping[str, Any],
    worker_backlog: Mapping[str, Any],
    governance: Mapping[str, Any],
    spawn_summary: Mapping[str, Any],
) -> list[dict[str, Any]]:
    summary = _mapping(worker_readiness.get("summary"))
    governance_summary = _mapping(governance.get("summary"))
    packets: list[dict[str, Any]] = []
    if list(worker_readiness.get("blockers") or []):
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-GLOBAL-QUEUE-BACKLOG-IDENTITY-REPAIR-PREVIEW-V0_1",
                "purpose": "produce exact repair rows for queueable requests missing domain, lane, context, or capsule identity",
                "authority": "candidate_only_no_request_file_mutation",
            }
        )
    if int(summary.get("blocked_context_gate_request_count") or 0) > 0:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-CONTEXT-GATE-BLOCKED-REQUEST-REISSUE-V0_1",
                "purpose": "reissue or supersede context-gate-blocked rows with fresh active context packages",
                "authority": "preflight_first_then_explicit_write_gate",
            }
        )
    if int(summary.get("capsule_identity_blocked_request_count") or 0) > 0:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-WORKING-CAPSULE-IDENTITY-REISSUE-V0_2",
                "purpose": "bind queueable requests to unique folder-local working capsules before any worker start",
                "authority": "candidate_only_no_shared_codex_solo_working_capsule",
            }
        )
    if int(governance_summary.get("stale_waiting_request_count") or 0) > 0:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-STALE-WAITING-REQUEST-RECONCILIATION-V0_2",
                "purpose": "digest, supersede, or explicitly preserve stale waiting rows without broad queue processing",
                "authority": "candidate_lifecycle_rows_until_mutation_gate",
            }
        )
    if int(governance_summary.get("actionable_duplicate_group_count") or 0) > 0:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-ACTIONABLE-DUPLICATE-QUEUE-DEDUP-V0_1",
                "purpose": "separate true duplicate hazards from already-superseded or accepted historical rows",
                "authority": "candidate_lifecycle_rows_until_mutation_gate",
            }
        )
    if int(spawn_summary.get("requested_count") or 0) > 0:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-SPAWN-REQUEST-DISPATCH-VALIDATION-V0_2",
                "purpose": "validate requested worker-local spawn rows before any queue handoff",
                "authority": "dispatcher_validation_only_no_worker_start",
            }
        )
    if list(worker_backlog.get("candidate_exact_request_paths") or []):
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-EXACT-PATH-ONLY-START-GATE-AFTER-HYGIENE-V0_1",
                "purpose": "allow only named request-path starts after the dirty global backlog remains isolated",
                "authority": "exact_request_path_only_no_general_queue_processing",
                "candidate_exact_request_paths": list(
                    worker_backlog.get("candidate_exact_request_paths") or []
                ),
            }
        )
    return packets


def _global_queue_hygiene_graph_deltas(
    root: Path,
    *,
    generated_at: str,
    blocker_rows: Sequence[Mapping[str, Any]],
    repair_packets: Sequence[Mapping[str, Any]],
    worker_readiness: Mapping[str, Any],
    worker_backlog: Mapping[str, Any],
    governance: Mapping[str, Any],
    spawn_summary: Mapping[str, Any],
) -> dict[str, Any]:
    claims: list[dict[str, Any]] = [
        {
            "id": "domain_weaver.global_queue_backlog_context_identity_hygiene",
            "kind": "queue_hygiene_posture",
            "state": "blocked" if blocker_rows else "clean",
            "evidence": [
                QUEUE_PATH.as_posix(),
                CODEX_WORK_REQUESTS_DIR.as_posix(),
                QUEUE_RUNNER_STATE_PATH.as_posix(),
            ],
            "value": {
                "worker_start_readiness_ok": bool(worker_readiness.get("ok")),
                "exact_request_path_required": True,
                "general_queue_processing_allowed": False,
                "candidate_exact_request_path_count": len(
                    worker_backlog.get("candidate_exact_request_paths") or []
                ),
                "spawn_request_count": spawn_summary.get("spawn_request_count"),
            },
        },
        {
            "id": "domain_weaver.queue_governance.all_work_requests",
            "kind": "queue_governance_projection_summary",
            "state": "candidate_projection",
            "evidence": [CODEX_WORK_REQUESTS_DIR.as_posix()],
            "value": _mapping(governance.get("summary")),
        },
    ]
    claims.extend(
        {
            "id": f"domain_weaver.queue_hygiene.blocker.{row.get('code')}",
            "kind": "queue_hygiene_blocker",
            "state": row.get("severity"),
            "evidence": list(row.get("evidence") or []),
            "value": {"detail": row.get("detail")},
        }
        for row in blocker_rows
    )
    claims.extend(
        {
            "id": f"domain_weaver.queue_hygiene.repair_packet.{packet.get('packet_id')}",
            "kind": "next_packet",
            "state": "candidate",
            "evidence": [CODEX_WORK_REQUESTS_DIR.as_posix()],
            "value": {
                "purpose": packet.get("purpose"),
                "authority": packet.get("authority"),
            },
        }
        for packet in repair_packets
    )
    return {
        "schema_id": GLOBAL_QUEUE_CONTEXT_IDENTITY_DELTA_SCHEMA_ID,
        "generated_at": generated_at,
        "active_root": str(root),
        "status": "candidate_global_queue_context_identity_deltas_built",
        "upsert_claims": claims,
        "write_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _queued_source_original_rows(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in _load_work_request_rows(root):
        if row.get("status") != "QUEUED_FOR_CODEX_CARRIER":
            continue
        if _mapping(row.get("metadata_identity_reissue")) or _mapping(row.get("context_gate_reissue")):
            continue
        request_id = str(row.get("request_id") or "")
        if request_id.startswith("codex_req_metadata_identity_reissue_"):
            continue
        if request_id.startswith("codex_req_context_gate_reissue_"):
            continue
        rows.append(row)
    return rows


def _post_sidecar_queue_hygiene_row(
    root: Path,
    source_row: Mapping[str, Any],
) -> dict[str, Any]:
    request_id = str(source_row.get("request_id") or "")
    source_path = str(source_row.get("source_path") or source_row.get("path") or "")
    quarantine = dict(_stale_non_domain_quarantine_settlement_map(root).get(request_id) or {})
    stale_settlement = dict(_stale_waiting_settlement_map(root).get(request_id) or {})
    metadata_reissue = dict(_metadata_identity_reissue_written_map(root).get(request_id) or {})
    context_reissue = dict(_context_gate_reissue_written_map(root).get(request_id) or {})
    replacement = metadata_reissue or context_reissue
    if quarantine:
        classification = "quarantine_as_stale_external_non_domain"
        settlement = quarantine
        evidence_path = (
            DEFAULT_QUEUE_GOVERNANCE_DIR
            / DEFAULT_STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_NAME
        ).as_posix()
    elif stale_settlement:
        classification = "supersede_with_fresh_exact_request"
        settlement = stale_settlement
        evidence_path = (
            DEFAULT_QUEUE_GOVERNANCE_DIR
            / DEFAULT_STALE_WAITING_RECONCILIATION_SETTLEMENT_NAME
        ).as_posix()
    else:
        classification = "unsettled_queued_original_requires_review"
        settlement = {}
        evidence_path = ""
    replacement_status = str(replacement.get("replacement_request_status") or "")
    return {
        "schema_id": "ion.domain_weaver.post_sidecar_global_queue_hygiene_row.v0_1_candidate",
        "row_kind": "post_sidecar_queued_source_original_classification",
        "source_request_id": request_id,
        "source_request_path": source_path,
        "source_status": source_row.get("status"),
        "source_sha256": source_row.get("source_sha256"),
        "work_class": source_row.get("work_class"),
        "request_kind": source_row.get("request_kind"),
        "lane_id": source_row.get("lane_id"),
        "domain_id": source_row.get("domain_id") or None,
        "role_id": source_row.get("role_id") or source_row.get("agent_role_id") or None,
        "candidate_classification": classification,
        "settlement_evidence_path": evidence_path,
        "settlement_decision": settlement.get("settlement_decision"),
        "settlement_source_hash_matches_current": bool(
            settlement.get("source_hash_matches_review")
            or settlement.get("source_hash_matches_assignment")
        ),
        "replacement_request_found": bool(replacement),
        "replacement_kind": (
            "metadata_identity_reissue"
            if metadata_reissue
            else "context_gate_reissue"
            if context_reissue
            else None
        ),
        "replacement_request_id": replacement.get("replacement_request_id"),
        "replacement_request_path": replacement.get("replacement_request_path"),
        "replacement_current_status": replacement_status or None,
        "replacement_request_sha256": replacement.get("replacement_request_sha256"),
        "replacement_source_hash_matches_current": bool(
            replacement.get("source_hash_matches_reissue")
        ),
        "candidate_action": _post_sidecar_row_candidate_action(
            classification=classification,
            replacement_status=replacement_status,
            replacement_found=bool(replacement),
        ),
        "general_queue_processing_allowed": False,
        "exact_request_path_required": True,
        "source_request_files_mutated": False,
        "replacement_request_files_written": 0,
        "codex_queue_run_started_by_this_packet": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _post_sidecar_row_candidate_action(
    *,
    classification: str,
    replacement_status: str,
    replacement_found: bool,
) -> str:
    if classification == "quarantine_as_stale_external_non_domain":
        return "preserve_as_quarantined_historical_source_do_not_run_broadly"
    if classification == "unsettled_queued_original_requires_review":
        return "run_queue_hygiene_review_before_any_reissue_or_start"
    if not replacement_found:
        return "write_or_refresh_exact_replacement_request_candidate"
    if replacement_status == "RETURN_RECORDED_PROOF_ACCEPTED":
        return "fan_in_accepted_replacement_return_before_any_source_lifecycle_close"
    if replacement_status.startswith("CODEX_QUEUE_RUNNER_FAILED"):
        return "fan_in_failed_replacement_return_and_prepare_exact_retry_or_repair"
    if replacement_status == "QUEUED_FOR_CODEX_CARRIER":
        return "eligible_only_for_named_exact_request_path_start_after_runtime_status_refresh"
    return "review_replacement_status_before_next_action"


def _post_sidecar_replacement_failed(row: Mapping[str, Any]) -> bool:
    return str(row.get("replacement_current_status") or "").startswith(
        "CODEX_QUEUE_RUNNER_FAILED"
    )


def _post_sidecar_global_queue_hygiene_blockers(
    *,
    source_original_count: int,
    expected_source_original_count: int,
    unsettled_rows: Sequence[Mapping[str, Any]],
    missing_replacement_rows: Sequence[Mapping[str, Any]],
    failed_replacement_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = [
        _blocker(
            "high",
            "GLOBAL_QUEUE_BACKLOG_CONTEXT_IDENTITY_HYGIENE_NOT_CLEAN",
            "The historical source originals still have QUEUED_FOR_CODEX_CARRIER status; broad queue processing remains blocked.",
            evidence=[CODEX_WORK_REQUESTS_DIR.as_posix()],
        )
    ]
    if source_original_count != expected_source_original_count:
        blockers.append(
            _blocker(
                "medium",
                "POST_SIDECAR_SOURCE_ORIGINAL_COUNT_DRIFT",
                "The queued source original count differs from the expected seven-row sidecar set.",
                evidence=[CODEX_WORK_REQUESTS_DIR.as_posix()],
            )
        )
    if unsettled_rows:
        blockers.append(
            _blocker(
                "high",
                "POST_SIDECAR_QUEUED_ORIGINALS_UNSETTLED",
                "At least one queued source original lacks quarantine or stale-settlement evidence.",
            )
        )
    if missing_replacement_rows:
        blockers.append(
            _blocker(
                "high",
                "POST_SIDECAR_REPLACEMENT_REQUESTS_MISSING",
                "At least one superseded source original lacks a current exact replacement request ref.",
            )
        )
    if failed_replacement_rows:
        blockers.append(
            _blocker(
                "high",
                "POST_SIDECAR_REPLACEMENT_REQUEST_FAILURES_PRESENT",
                "One or more exact replacement request runs failed and need fan-in repair before the source backlog can be closed.",
            )
        )
    return _dedupe_blockers(blockers)


def _post_sidecar_global_queue_hygiene_next_packets(
    *,
    unsettled_rows: Sequence[Mapping[str, Any]],
    missing_replacement_rows: Sequence[Mapping[str, Any]],
    failed_replacement_rows: Sequence[Mapping[str, Any]],
    all_source_originals_classified: bool,
) -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    if unsettled_rows:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-POST-SIDECAR-UNSETTLED-QUEUE-SOURCE-REVIEW-V0_1",
                "purpose": "classify any queued source originals that lack quarantine or stale-settlement evidence",
                "authority": "candidate_review_only_no_queue_start",
                "row_count": len(unsettled_rows),
            }
        )
    if missing_replacement_rows:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-MISSING-EXACT-REPLACEMENT-REQUEST-REISSUE-V0_1",
                "purpose": "write or refresh missing exact replacement requests behind source-hash gates",
                "authority": "bounded_replacement_request_write_gate_no_source_mutation",
                "row_count": len(missing_replacement_rows),
            }
        )
    if failed_replacement_rows:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-FAILED-EXACT-REISSUE-FANIN-AND-REPAIR-V0_1",
                "purpose": "fan in failed exact replacement attempts and decide retry, repair, or quarantine",
                "authority": "carrier_intake_fanin_only_until_new_exact_retry_packet",
                "row_count": len(failed_replacement_rows),
            }
        )
    if all_source_originals_classified:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-HISTORICAL-SOURCE-QUEUE-LIFECYCLE-LEDGER-APPLY-V0_1",
                "purpose": "prepare a hash-bound lifecycle ledger closeout for historical source originals without broad queue processing",
                "authority": "candidate_or_explicit_lifecycle_gate_only_no_accepted_state_claim",
            }
        )
    packets.append(
        {
            "packet_id": "PCKT-DOMAIN-WEAVER-LIMITED-WATCH-MATRIX-REFRESH-V0_2",
            "purpose": "refresh watch alerts after post-sidecar queue readback",
            "authority": "candidate_readback_only",
        }
    )
    return packets


def _post_sidecar_global_queue_hygiene_graph_deltas(
    root: Path,
    *,
    generated_at: str,
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    claims: list[dict[str, Any]] = [
        {
            "id": "domain_weaver.post_sidecar_global_queue_hygiene",
            "kind": "post_sidecar_queue_hygiene_readback",
            "state": "exact_path_only",
            "evidence": [
                CODEX_WORK_REQUESTS_DIR.as_posix(),
                (DEFAULT_QUEUE_GOVERNANCE_DIR / DEFAULT_STALE_WAITING_RECONCILIATION_SETTLEMENT_NAME).as_posix(),
                (DEFAULT_QUEUE_GOVERNANCE_DIR / DEFAULT_STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_NAME).as_posix(),
            ],
            "value": {
                "queued_source_original_count": len(rows),
                "general_queue_processing_allowed": False,
                "source_request_files_mutated": False,
                "codex_queue_run_started_by_this_packet": False,
            },
        }
    ]
    claims.extend(
        {
            "id": f"domain_weaver.post_sidecar_global_queue_hygiene.{row.get('source_request_id')}",
            "kind": "post_sidecar_queued_source_original",
            "state": row.get("candidate_classification"),
            "evidence": [
                str(row.get("source_request_path") or ""),
                str(row.get("settlement_evidence_path") or ""),
                str(row.get("replacement_request_path") or ""),
            ],
            "value": {
                "source_status": row.get("source_status"),
                "replacement_current_status": row.get("replacement_current_status"),
                "candidate_action": row.get("candidate_action"),
                "general_queue_processing_allowed": False,
            },
        }
        for row in rows
    )
    return {
        "schema_id": POST_SIDECAR_GLOBAL_QUEUE_HYGIENE_DELTA_SCHEMA_ID,
        "generated_at": generated_at,
        "active_root": str(root),
        "status": "candidate_post_sidecar_global_queue_hygiene_deltas_built",
        "upsert_claims": claims,
        "write_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _queue_identity_repair_rows(worker_readiness: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in list(worker_readiness.get("request_results") or []):
        if not isinstance(row, Mapping) or row.get("ready"):
            continue
        blockers = [str(code) for code in list(row.get("blockers") or []) if str(code).strip()]
        repair_class = _queue_repair_class(row, blockers)
        rows.append(
            {
                "schema_id": "ion.domain_weaver.global_queue_identity_repair_row.v0_1_candidate",
                "row_kind": "queueable_request_identity_repair_preview",
                "request_id": row.get("request_id"),
                "request_path": row.get("request_path"),
                "status": row.get("status"),
                "repair_class": repair_class,
                "repair_packet_id": _queue_repair_packet_id(repair_class),
                "recommended_action": _queue_repair_action(repair_class),
                "lane_id": row.get("lane_id"),
                "raw_lane_id": row.get("raw_lane_id"),
                "domain_id": row.get("domain_id") or None,
                "role_id": row.get("role_id") or None,
                "role_tier": row.get("role_tier") or None,
                "callsign": row.get("callsign") or None,
                "work_class": row.get("work_class"),
                "request_kind": row.get("request_kind"),
                "selected_mount_id": row.get("selected_mount_id") or row.get("requested_selected_mount_id"),
                "selected_mount_path": row.get("selected_mount_path") or row.get("requested_selected_mount_path"),
                "active_context_check_status": row.get("active_context_check_status"),
                "active_context_ready": bool(row.get("active_context_ready")),
                "queueable_for_start": bool(row.get("queueable_for_start")),
                "blockers": blockers,
                "capsule_identity_blockers": list(row.get("capsule_identity_blockers") or []),
                "capsule_identity_binding_blockers": list(row.get("capsule_identity_binding_blockers") or []),
                "candidate_reissue_fields": _candidate_reissue_fields(row, blockers),
                "requires_new_request_path": True,
                "in_place_request_mutation_allowed": False,
                "would_mutate_request_file": False,
                "would_start_worker": False,
                "worker_return_is_carrier_intake_only": True,
                "accepted_state_claimed": False,
                "authority": AUTHORITY,
            }
        )
    return rows


def _load_repair_preview_or_build(
    root: Path,
    *,
    generated_at: str,
    source_preview: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if source_preview is not None:
        return dict(source_preview), {
            "path": "",
            "exists": True,
            "required": False,
            "kind": "provided_payload",
            "schema_id": source_preview.get("schema_id"),
            "generated_at": source_preview.get("generated_at"),
        }
    preview_path = (
        root
        / DEFAULT_QUEUE_GOVERNANCE_DIR
        / DEFAULT_GLOBAL_QUEUE_REPAIR_PREVIEW_NAME
    )
    preview = _read_json(preview_path)
    if preview:
        ref = _file_ref(root, preview_path)
        ref["kind"] = "file"
        ref["schema_id"] = preview.get("schema_id")
        ref["generated_at"] = preview.get("generated_at")
        return preview, ref
    built = build_global_queue_backlog_identity_repair_preview(
        root,
        generated_at=generated_at,
    )
    return built, {
        "path": "",
        "exists": True,
        "required": False,
        "kind": "rebuilt_in_memory",
        "schema_id": built.get("schema_id"),
        "generated_at": built.get("generated_at"),
    }


def _metadata_identity_reissue_review_row(
    root: Path,
    row: Mapping[str, Any],
) -> dict[str, Any]:
    candidate_fields = _mapping(row.get("candidate_reissue_fields"))
    preserve = _mapping(candidate_fields.get("preserve_if_trusted"))
    missing_or_untrusted = [
        str(value)
        for value in list(candidate_fields.get("missing_or_untrusted_fields") or [])
        if str(value).strip()
    ]
    source_request_path = str(row.get("request_path") or "")
    source_payload_path = root / source_request_path if source_request_path else Path("")
    source_payload = _read_json(source_payload_path) if source_request_path else {}
    source_ref = _file_ref(root, source_payload_path) if source_request_path else {
        "path": "",
        "exists": False,
        "required": True,
    }
    lane_id = _first_truthy(row.get("lane_id"), preserve.get("lane_id"), source_payload.get("lane_id"))
    raw_lane_id = _first_truthy(row.get("raw_lane_id"), source_payload.get("raw_lane_id"))
    domain_id = _first_truthy(row.get("domain_id"), preserve.get("domain_id"), source_payload.get("domain_id"))
    role_id = _first_truthy(
        row.get("role_id"),
        preserve.get("role_id"),
        source_payload.get("role_id"),
        source_payload.get("agent_role_id"),
    )
    callsign = _first_truthy(row.get("callsign"), preserve.get("callsign"), source_payload.get("callsign"))
    selected_mount_id = _first_truthy(
        row.get("selected_mount_id"),
        preserve.get("selected_mount_id"),
        source_payload.get("selected_mount_id"),
        source_payload.get("requested_selected_mount_id"),
    )
    selected_mount_path = _first_truthy(
        row.get("selected_mount_path"),
        preserve.get("selected_mount_path"),
        source_payload.get("selected_mount_path"),
        source_payload.get("requested_selected_mount_path"),
    )
    working_capsule_identity = source_payload.get("working_capsule_identity")
    working_capsule_identity_present = isinstance(working_capsule_identity, Mapping) and bool(
        working_capsule_identity
    )
    domain_ready = bool(domain_id) and "domain_id" not in missing_or_untrusted
    lane_ready = bool(lane_id) and "lane_id" not in missing_or_untrusted
    role_ready = bool(role_id or callsign)
    mount_ready = bool(selected_mount_id or selected_mount_path)
    capsule_ready = working_capsule_identity_present and "working_capsule_identity" not in missing_or_untrusted
    active_context_ready = bool(row.get("active_context_ready")) and (
        "fresh_active_context_package" not in missing_or_untrusted
    )
    candidate_reissue_allowed_now = all(
        [
            source_ref.get("exists"),
            domain_ready,
            lane_ready,
            role_ready,
            mount_ready,
            capsule_ready,
            active_context_ready,
        ]
    )
    required_fields_before_reissue = [
        "domain_id",
        "lane_id",
        "role_id_or_callsign",
        "selected_mount_id_or_selected_mount_path",
        "working_capsule_identity",
        "fresh_active_context_package",
        "production_authority=false",
        "live_execution_authority=false",
        "accepted_state_authority=false",
        "secrets_authority=false",
    ]
    blocker_codes = list(row.get("blockers") or [])
    review_disposition = (
        "candidate_apply_review_ready"
        if candidate_reissue_allowed_now
        else "requires_domain_role_mount_capsule_assignment_before_reissue"
    )
    return {
        "schema_id": "ion.domain_weaver.queue_request_metadata_identity_reissue_row.v0_1_candidate",
        "row_kind": "metadata_identity_reissue_candidate_review",
        "source_request_id": row.get("request_id"),
        "source_request_path": source_request_path,
        "source_request_ref": source_ref,
        "source_status": row.get("status") or source_payload.get("status"),
        "source_repair_class": row.get("repair_class"),
        "source_blockers": blocker_codes,
        "missing_or_untrusted_fields": list(dict.fromkeys(missing_or_untrusted)),
        "preserve_if_trusted": dict(preserve),
        "proposed_identity": {
            "lane_id": lane_id,
            "raw_lane_id": raw_lane_id,
            "domain_id": domain_id,
            "role_id": role_id,
            "callsign": callsign,
            "role_tier": _first_truthy(row.get("role_tier"), preserve.get("role_tier"), source_payload.get("role_tier")),
            "work_class": _first_truthy(row.get("work_class"), preserve.get("work_class"), source_payload.get("work_class")),
            "request_kind": _first_truthy(row.get("request_kind"), preserve.get("request_kind"), source_payload.get("request_kind")),
            "selected_mount_id": selected_mount_id,
            "selected_mount_path": selected_mount_path,
        },
        "domain_assignment_status": (
            "domain_identity_present_but_untrusted"
            if domain_id and not domain_ready
            else "trusted_domain_present"
            if domain_ready
            else "requires_domain_steward_assignment"
        ),
        "lane_assignment_status": (
            "lane_identity_present_but_untrusted"
            if lane_id and not lane_ready
            else "trusted_lane_present"
            if lane_ready
            else "requires_lane_assignment"
        ),
        "role_assignment_status": (
            "trusted_role_or_callsign_present"
            if role_ready
            else "requires_role_assignment"
        ),
        "mount_binding_status": (
            "trusted_mount_present"
            if mount_ready
            else "requires_selected_mount_binding"
        ),
        "capsule_identity_status": (
            "working_capsule_identity_present_but_untrusted"
            if working_capsule_identity_present and not capsule_ready
            else "trusted_working_capsule_identity_present"
            if capsule_ready
            else "requires_unique_folder_local_mount_or_agent_mount_binding"
        ),
        "active_context_status": (
            "fresh_active_context_package_present"
            if active_context_ready
            else "requires_fresh_active_context_package"
        ),
        "required_fields_before_reissue": required_fields_before_reissue,
        "candidate_reissue_allowed_now": candidate_reissue_allowed_now,
        "review_disposition": review_disposition,
        "recommended_action": (
            "prepare exact replacement request under explicit apply-review mutation gate"
            if candidate_reissue_allowed_now
            else "assign domain, role/callsign, selected mount, working capsule identity, and fresh active context before replacement request write"
        ),
        "proposed_reissue_packet_id": (
            "PCKT-DOMAIN-WEAVER-QUEUE-REQUEST-METADATA-IDENTITY-REISSUE-APPLY-REVIEW-V0_1"
        ),
        "quarantine_or_supersede_consideration": (
            "old_non_domain_weaver_or_stale_request_may_be_superseded_instead_of_reissued"
            if not str(row.get("request_id") or "").startswith("codex_req_domain_weaver")
            else "domain_weaver_request_requires_domain_steward_assignment_before_reissue"
        ),
        "would_write_new_request": False,
        "would_mutate_source_request": False,
        "would_start_worker": False,
        "codex_queue_run_started": False,
        "worker_return_is_carrier_intake_only": True,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _metadata_identity_reissue_next_packets(
    *,
    allowed_count: int,
    blocked_count: int,
    excluded_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    if blocked_count:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-DOMAIN-ROLE-CAPSULE-ASSIGNMENT-FOR-METADATA-REISSUE-V0_1",
                "purpose": "assign missing domain/role/mount/capsule identity before replacement request files can be reviewed",
                "authority": "candidate_assignment_only_no_request_file_mutation",
            }
        )
    if allowed_count:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-QUEUE-REQUEST-METADATA-IDENTITY-REISSUE-APPLY-REVIEW-V0_1",
                "purpose": "review exact replacement request bodies behind an explicit mutation gate",
                "authority": "apply_review_only_no_automatic_queue_start",
            }
        )
    if excluded_rows:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-CONTEXT-GATE-BLOCKED-REQUEST-REISSUE-V0_1",
                "purpose": "handle excluded context-gate rows through fresh active-context proof",
                "authority": "context_gate_preflight_only",
            }
        )
    return packets


def _queue_request_metadata_identity_reissue_graph_deltas(
    root: Path,
    *,
    generated_at: str,
    worksheet_rows: Sequence[Mapping[str, Any]],
    source_preview_ref: Mapping[str, Any],
) -> dict[str, Any]:
    allowed_count = sum(1 for row in worksheet_rows if row.get("candidate_reissue_allowed_now"))
    claims: list[dict[str, Any]] = [
        {
            "id": "domain_weaver.queue_request_metadata_identity_reissue",
            "kind": "queue_metadata_identity_reissue_worksheet",
            "state": "apply_review_ready" if allowed_count else "assignment_blocked",
            "evidence": [
                str(source_preview_ref.get("path") or ""),
                CODEX_WORK_REQUESTS_DIR.as_posix(),
            ],
            "value": {
                "worksheet_row_count": len(worksheet_rows),
                "candidate_reissue_allowed_now_count": allowed_count,
                "request_files_mutated": False,
                "replacement_requests_written": 0,
            },
        }
    ]
    claims.extend(
        {
            "id": f"domain_weaver.queue_request_metadata_identity_reissue.{row.get('source_request_id')}",
            "kind": "queue_request_metadata_identity_review_row",
            "state": row.get("review_disposition"),
            "evidence": [str(row.get("source_request_path") or "")],
            "value": {
                "domain_assignment_status": row.get("domain_assignment_status"),
                "role_assignment_status": row.get("role_assignment_status"),
                "capsule_identity_status": row.get("capsule_identity_status"),
                "mount_binding_status": row.get("mount_binding_status"),
                "candidate_reissue_allowed_now": bool(
                    row.get("candidate_reissue_allowed_now")
                ),
                "would_write_new_request": False,
                "would_mutate_source_request": False,
            },
        }
        for row in worksheet_rows
    )
    return {
        "schema_id": QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_DELTA_SCHEMA_ID,
        "generated_at": generated_at,
        "active_root": str(root),
        "status": "candidate_queue_request_metadata_identity_reissue_deltas_built",
        "upsert_claims": claims,
        "write_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _load_metadata_reissue_or_build(
    root: Path,
    *,
    generated_at: str,
    source_reissue: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if source_reissue is not None:
        return dict(source_reissue), {
            "path": "",
            "exists": True,
            "required": False,
            "kind": "provided_payload",
            "schema_id": source_reissue.get("schema_id"),
            "generated_at": source_reissue.get("generated_at"),
        }
    reissue_path = (
        root
        / DEFAULT_QUEUE_GOVERNANCE_DIR
        / DEFAULT_QUEUE_REQUEST_METADATA_IDENTITY_REISSUE_NAME
    )
    reissue = _read_json(reissue_path)
    if reissue:
        ref = _file_ref(root, reissue_path)
        ref["kind"] = "file"
        ref["schema_id"] = reissue.get("schema_id")
        ref["generated_at"] = reissue.get("generated_at")
        return reissue, ref
    built = build_queue_request_metadata_identity_reissue(root, generated_at=generated_at)
    return built, {
        "path": "",
        "exists": True,
        "required": False,
        "kind": "rebuilt_in_memory",
        "schema_id": built.get("schema_id"),
        "generated_at": built.get("generated_at"),
    }


def _stale_non_domain_quarantine_settlement_row(
    root: Path,
    row: Mapping[str, Any],
    *,
    settlement_decision: str,
) -> dict[str, Any]:
    allowed_decisions = {
        "quarantine_as_stale_external_non_domain",
        "preserve_as_explicit_external_backlog",
    }
    source_request_id = str(row.get("source_request_id") or "")
    source_request_path = str(row.get("source_request_path") or "")
    source_path = root / source_request_path if source_request_path else root
    source_ref = _mapping(row.get("source_request_ref"))
    expected_source_sha = str(source_ref.get("sha256") or "")
    current_source_sha = _sha256_file(source_path) if source_path.is_file() else ""
    blockers: list[str] = []
    if settlement_decision not in allowed_decisions:
        blockers.append("invalid_settlement_decision")
    if not source_request_id:
        blockers.append("missing_source_request_id")
    if not source_request_path:
        blockers.append("missing_source_request_path")
    if not source_path.is_file():
        blockers.append("source_request_file_missing")
    if current_source_sha != expected_source_sha:
        blockers.append("source_request_sha_mismatch")
    settlement_ready = not blockers
    return {
        "schema_id": "ion.domain_weaver.stale_non_domain_queue_quarantine_settlement_row.v0_1_candidate",
        "row_kind": "stale_non_domain_queue_quarantine_settlement_candidate",
        "source_request_id": source_request_id,
        "source_request_path": source_request_path,
        "source_request_ref": _file_ref(root, source_path)
        if source_request_path
        else dict(source_ref),
        "source_request_sha256": expected_source_sha,
        "current_source_request_sha256": current_source_sha,
        "source_hash_matches_assignment": bool(
            current_source_sha and current_source_sha == expected_source_sha
        ),
        "assigned_identity": dict(_mapping(row.get("assigned_identity"))),
        "assignment_basis": row.get("assignment_basis"),
        "source_proposed_identity": dict(_mapping(row.get("source_proposed_identity"))),
        "settlement_decision": settlement_decision,
        "settlement_effect": _stale_non_domain_quarantine_settlement_effect(
            settlement_decision
        ),
        "settlement_ready": settlement_ready,
        "settlement_blockers": blockers,
        "metadata_assignment_quarantine_may_clear": bool(
            settlement_ready
            and settlement_decision == "quarantine_as_stale_external_non_domain"
        ),
        "source_request_files_mutated": False,
        "replacement_request_files_written": 0,
        "codex_queue_run_started": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _stale_non_domain_quarantine_settlement_effect(settlement_decision: str) -> str:
    if settlement_decision == "quarantine_as_stale_external_non_domain":
        return (
            "the stale external desktop-rescue request is candidate-quarantined "
            "from Domain Weaver self-evolution routing and must not be run broadly"
        )
    if settlement_decision == "preserve_as_explicit_external_backlog":
        return (
            "the stale external request remains explicit backlog evidence and "
            "does not clear the quarantine review by itself"
        )
    return "invalid settlement decision"


def _stale_non_domain_quarantine_settlement_next_packets(
    *,
    settlement_rows: Sequence[Mapping[str, Any]],
    blocked_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if blocked_rows:
        return [
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-STALE-NON-DOMAIN-QUEUE-QUARANTINE-REVIEW-REFRESH-V0_1",
                "purpose": "refresh quarantine review or inspect source hash mismatches before settlement",
                "authority": "candidate_review_only_no_request_file_mutation",
                "row_count": len(blocked_rows),
            }
        ]
    if settlement_rows:
        return [
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-QUEUE-METADATA-IDENTITY-ASSIGNMENT-REFRESH-AFTER-QUARANTINE-V0_1",
                "purpose": "refresh metadata assignment so stale external rows are no longer active blockers",
                "authority": "candidate_projection_refresh_only_no_queue_start",
                "row_count": len(settlement_rows),
            }
        ]
    return []


def _stale_non_domain_quarantine_settlement_graph_deltas(
    root: Path,
    *,
    generated_at: str,
    settlement_rows: Sequence[Mapping[str, Any]],
    assignment_ref: Mapping[str, Any],
    write_performed: bool = False,
) -> dict[str, Any]:
    claims: list[dict[str, Any]] = [
        {
            "id": "domain_weaver.stale_non_domain_queue_quarantine_settlement",
            "kind": "stale_non_domain_queue_quarantine_settlement",
            "state": "written" if write_performed else "ready",
            "evidence": [
                str(assignment_ref.get("path") or ""),
                CODEX_WORK_REQUESTS_DIR.as_posix(),
            ],
            "value": {
                "settlement_row_count": len(settlement_rows),
                "candidate_quarantine_settlement_written": write_performed,
                "source_request_files_mutated": False,
                "replacement_request_files_written": 0,
                "codex_queue_run_started": False,
            },
        }
    ]
    claims.extend(
        {
            "id": f"domain_weaver.stale_non_domain_queue_quarantine_settlement.{row.get('source_request_id')}",
            "kind": "stale_non_domain_queue_quarantine_settlement_row",
            "state": row.get("settlement_decision"),
            "evidence": [
                str(row.get("source_request_path") or ""),
                str(assignment_ref.get("path") or ""),
            ],
            "value": {
                "source_request_sha256": row.get("source_request_sha256"),
                "source_hash_matches_assignment": row.get(
                    "source_hash_matches_assignment"
                ),
                "metadata_assignment_quarantine_may_clear": row.get(
                    "metadata_assignment_quarantine_may_clear"
                ),
                "candidate_quarantine_settlement_written": write_performed,
            },
        }
        for row in settlement_rows
    )
    return {
        "schema_id": STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_DELTA_SCHEMA_ID,
        "generated_at": generated_at,
        "active_root": str(root),
        "status": "candidate_stale_non_domain_queue_quarantine_settlement_deltas_built",
        "upsert_claims": claims,
        "write_performed": write_performed,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _stale_non_domain_quarantine_settlement_map(root: Path) -> dict[str, Mapping[str, Any]]:
    settlement_path = (
        root
        / DEFAULT_QUEUE_GOVERNANCE_DIR
        / DEFAULT_STALE_NON_DOMAIN_QUEUE_QUARANTINE_SETTLEMENT_NAME
    )
    settlement = _read_json(settlement_path)
    if not settlement:
        return {}
    rows: dict[str, Mapping[str, Any]] = {}
    for row in list(settlement.get("settlement_rows") or []):
        if not isinstance(row, Mapping):
            continue
        request_id = str(row.get("source_request_id") or "")
        source_path = str(row.get("source_request_path") or "")
        expected_sha = str(row.get("source_request_sha256") or "")
        current_sha = _sha256_file(root / source_path) if source_path else ""
        if (
            request_id
            and bool(row.get("settlement_ready"))
            and bool(row.get("metadata_assignment_quarantine_may_clear"))
            and current_sha
            and current_sha == expected_sha
        ):
            rows[request_id] = row
    return rows


def _codex_agent_mount_inventory(root: Path) -> dict[str, dict[str, Any]]:
    mounts_root = root / "ION/05_context/current/codex_agent_mounts"
    inventory: dict[str, dict[str, Any]] = {}
    if not mounts_root.is_dir():
        return inventory
    for mount_root in sorted(path for path in mounts_root.iterdir() if path.is_dir()):
        manifest_path = mount_root / "ION_AGENT_MOUNT_MANIFEST.json"
        if not manifest_path.is_file():
            continue
        manifest = _read_json(manifest_path)
        active_context_json = _read_json(mount_root / ".ion/ACTIVE_CONTEXT_PACKAGE.json")
        mount_id = str(manifest.get("mount_id") or mount_root.name)
        role_id = _first_truthy(
            manifest.get("agent_role_id"),
            manifest.get("role_id"),
            active_context_json.get("role_id"),
        )
        domain_id = _first_truthy(
            manifest.get("domain_id"),
            active_context_json.get("domain_id"),
        )
        mount_path = str(manifest.get("mount_path") or _rel(root, mount_root))
        active_context_path = str(
            manifest.get("portable_active_context_package_md_path")
            or _rel(root, mount_root / ".ion/ACTIVE_CONTEXT_PACKAGE.md")
        )
        inventory[mount_id] = {
            "mount_id": mount_id,
            "mount_path": mount_path,
            "mount_ref": _file_ref(root, manifest_path),
            "role_id": role_id,
            "domain_id": domain_id,
            "active_context_package_path": active_context_path,
            "active_context_package_ref": _file_ref(root, root / active_context_path),
            "working_capsule_path": _rel(root, mount_root / ".ion"),
            "working_capsule_ref": _evidence_ref(root, _rel(root, mount_root / ".ion")),
            "manifest": manifest,
        }
    return inventory


def _metadata_identity_assignment_row(
    root: Path,
    row: Mapping[str, Any],
    *,
    mount_inventory: Mapping[str, Mapping[str, Any]],
    lifecycle_row: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_identity = _mapping(row.get("proposed_identity"))
    source_request_path = str(row.get("source_request_path") or "")
    source_payload = _read_json(root / source_request_path) if source_request_path else {}
    policy = _metadata_assignment_policy(row)
    assigned_domain = policy.get("domain_id")
    assigned_role = policy.get("role_id")
    selected_mount_id = str(policy.get("selected_mount_id") or "")
    mount = _select_existing_mount(
        mount_inventory,
        domain_id=str(assigned_domain or ""),
        role_id=str(assigned_role or ""),
        selected_mount_id=selected_mount_id,
    )
    source_request_ref = _mapping(row.get("source_request_ref"))
    source_exists = bool(source_request_ref.get("exists"))
    source_safety = _metadata_assignment_source_safety(
        root,
        row,
        source_payload=source_payload,
        lifecycle_row=_mapping(lifecycle_row),
    )
    quarantine_settlement = dict(
        _stale_non_domain_quarantine_settlement_map(root).get(
            str(row.get("source_request_id") or "")
        )
        or {}
    )
    if (
        policy.get("disposition") == "supersede_or_quarantine_recommended"
        and quarantine_settlement
    ):
        disposition = "external_quarantine_settled"
    elif policy.get("disposition") == "supersede_or_quarantine_recommended":
        disposition = "supersede_or_quarantine_recommended"
    elif mount:
        disposition = "existing_mount_assignment_ready"
    else:
        disposition = "generated_mount_required"
    active_context_ready = bool(mount and _mapping(mount).get("active_context_package_ref", {}).get("exists"))
    candidate_identity = (
        _candidate_working_capsule_identity(
            root,
            source_request_id=str(row.get("source_request_id") or ""),
            domain_id=str(assigned_domain or ""),
            role_id=str(assigned_role or ""),
            mount=mount,
        )
        if disposition == "existing_mount_assignment_ready" and active_context_ready
        else {}
    )
    candidate_identity_ready = bool(
        candidate_identity
        and _mapping(candidate_identity.get("validation")).get("verdict")
        == "WORKING_CAPSULE_IDENTITY_READY"
    )
    apply_ready = bool(
        disposition == "existing_mount_assignment_ready"
        and source_exists
        and assigned_domain
        and assigned_role
        and active_context_ready
        and candidate_identity_ready
        and source_safety.get("apply_source_safe")
        and not source_safety.get("source_context_gate_reissued_for_metadata_reissue")
        and not source_safety.get("source_metadata_identity_reissued_for_metadata_reissue")
    )
    assigned_identity = {
        "domain_id": assigned_domain,
        "role_id": assigned_role,
        "callsign": policy.get("callsign"),
        "lane_id": _first_truthy(policy.get("lane_id"), source_identity.get("lane_id")),
        "request_kind": _first_truthy(source_identity.get("request_kind"), policy.get("request_kind")),
        "work_class": _first_truthy(source_identity.get("work_class"), policy.get("work_class")),
        "selected_mount_id": mount.get("mount_id") if mount else policy.get("proposed_mount_id"),
        "selected_mount_path": mount.get("mount_path") if mount else policy.get("proposed_mount_path"),
        "active_context_package_path": mount.get("active_context_package_path") if mount else None,
    }
    generated_mount_spec = {}
    if disposition == "generated_mount_required":
        generated_mount_spec = {
            "mount_id": policy.get("proposed_mount_id"),
            "mount_path": policy.get("proposed_mount_path"),
            "domain_id": assigned_domain,
            "role_id": assigned_role,
            "source_request_id": row.get("source_request_id"),
            "required_files": [
                "ION_AGENT_MOUNT_MANIFEST.json",
                ".ion/ION_CONTEXT_CAPSULE.yaml",
                ".ion/ACTIVE_CONTEXT_PACKAGE.md",
                ".ion/ACTIVE_CONTEXT_PACKAGE.json",
                ".ion/AGENT.yaml",
                ".ion/DOMAIN.yaml",
            ],
            "authority": "candidate_mount_generation_only_no_worker_start",
        }
    row_next_packet = _assignment_row_next_packet(disposition)
    recommended_action = _assignment_recommended_action(disposition)
    reissue_already_satisfied = bool(
        source_safety.get("source_context_gate_reissued_for_metadata_reissue")
        or source_safety.get("source_metadata_identity_reissued_for_metadata_reissue")
    )
    if disposition == "existing_mount_assignment_ready" and reissue_already_satisfied:
        row_next_packet = "PCKT-DOMAIN-WEAVER-METADATA-REISSUE-ALREADY-WRITTEN-FANIN-V0_1"
        recommended_action = "replacement request already exists for this source hash; do not write duplicate metadata reissue"
    elif disposition == "external_quarantine_settled":
        row_next_packet = "PCKT-DOMAIN-WEAVER-STALE-NON-DOMAIN-QUEUE-QUARANTINE-FANIN-V0_1"
        recommended_action = "stale external non-domain row is candidate-quarantined; do not reissue or run broadly"
    elif disposition == "existing_mount_assignment_ready" and not apply_ready:
        row_next_packet = "PCKT-DOMAIN-WEAVER-SOURCE-SAFETY-BLOCKED-METADATA-REISSUE-REVIEW-V0_1"
        recommended_action = "settle source context-gate or lifecycle safety blockers before replacement request body generation"
    return {
        "schema_id": "ion.domain_weaver.queue_metadata_identity_assignment_row.v0_1_candidate",
        "row_kind": "queue_metadata_identity_assignment_candidate",
        "source_request_id": row.get("source_request_id"),
        "source_request_path": row.get("source_request_path"),
        "source_request_ref": dict(source_request_ref),
        "source_assignment_statuses": {
            "domain_assignment_status": row.get("domain_assignment_status"),
            "role_assignment_status": row.get("role_assignment_status"),
            "mount_binding_status": row.get("mount_binding_status"),
            "capsule_identity_status": row.get("capsule_identity_status"),
            "active_context_status": row.get("active_context_status"),
        },
        "source_safety": source_safety,
        "source_proposed_identity": dict(source_identity),
        "assignment_basis": policy.get("basis"),
        "assignment_disposition": disposition,
        "assigned_identity": assigned_identity,
        "existing_mount_ref": dict(mount or {}),
        "generated_mount_spec": generated_mount_spec,
        "candidate_working_capsule_identity": candidate_identity.get("identity"),
        "candidate_working_capsule_validation": candidate_identity.get("validation"),
        "working_capsule_identity_posture": (
            "mount_bound_identity_not_lineage_proof"
            if candidate_identity
            else "no_candidate_working_capsule_identity"
        ),
        "candidate_identity_lineage_proven": False,
        "candidate_reissue_apply_review_ready": apply_ready,
        "candidate_reissue_already_satisfied": reissue_already_satisfied,
        "candidate_quarantine_already_satisfied": bool(quarantine_settlement),
        "candidate_quarantine_settlement": quarantine_settlement or None,
        "recommended_action": recommended_action,
        "next_packet": row_next_packet,
        "would_write_replacement_request": False,
        "would_mutate_source_request": False,
        "would_create_mount": False,
        "would_start_worker": False,
        "codex_queue_run_started": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _metadata_assignment_policy(row: Mapping[str, Any]) -> dict[str, Any]:
    identity = _mapping(row.get("proposed_identity"))
    request_id = str(row.get("source_request_id") or "")
    work_class = str(identity.get("work_class") or "")
    request_kind = str(identity.get("request_kind") or "")
    role_id = str(identity.get("role_id") or "")
    lane_id = str(identity.get("lane_id") or "")
    if work_class == "desktop_rescue_execution" or "urgent_desktop_rescue" in request_id:
        return {
            "disposition": "supersede_or_quarantine_recommended",
            "basis": "stale_or_external_desktop_rescue_request_not_domain_weaver_self_evolution",
            "domain_id": "domain.codex_carrier_sync",
            "role_id": "role.codex_carrier_steward",
            "callsign": "CODEX_CARRIER_STEWARD",
            "lane_id": lane_id,
            "work_class": work_class,
            "request_kind": request_kind,
        }
    if work_class == "incident_nemesis_review" or request_kind == "read_only_nemesis":
        return _existing_mount_policy(
            "incident_nemesis_review_maps_to_confidence_drift_nemesis",
            "domain.confidence_drift_review",
            "role.nemesis",
            "role_nemesis__domain_confidence_drift_review",
            lane_id,
            work_class,
            request_kind,
            callsign="NEMESIS",
        )
    if (
        work_class == "domain_weaver_agent_comms_queue_runner_pickup_proof"
        or role_id == "role.context_cartographer"
    ):
        return _existing_mount_policy(
            "agent_comms_pickup_proof_maps_to_agent_communication_context_cartographer",
            "domain.agent_communication_systems",
            "role.context_cartographer",
            "role_context_cartographer__domain_agent_communication_systems",
            lane_id,
            work_class,
            request_kind,
            callsign="CONTEXT_CARTOGRAPHER",
        )
    if work_class in {"receipt_pointer_lineage_repair", "receipt_integrity_proof_graph"}:
        return _generated_mount_policy(
            "receipt_lineage_or_proof_graph_work_requires_receipt_proof_graph_specialist_mount",
            "domain.receipt_proof_graph",
            "role.receipt_integrity_proof_graph_steward",
            lane_id,
            work_class,
            request_kind,
        )
    if work_class == "monolith_decomposition_cartography":
        return _generated_mount_policy(
            "monolith_decomposition_maps_to_context_graph_branch_fabric_specialist_mount",
            "domain.context_graph_branch_fabric",
            "role.monolith_decomposition_cartographer",
            lane_id,
            work_class,
            request_kind,
        )
    if work_class == "exact_active_binding_audit":
        return _generated_mount_policy(
            "exact_active_binding_audit_maps_to_codex_carrier_sync_specialist_mount",
            "domain.codex_carrier_sync",
            "role.exact_active_binding_specialist",
            lane_id,
            work_class,
            request_kind,
        )
    if work_class == "continuous_nemesis_review" or role_id == "role.continuous_nemesis":
        return _generated_mount_policy(
            "continuous_nemesis_requires_exact_continuous_nemesis_mount_not_generic_nemesis_substitution",
            "domain.confidence_drift_review",
            "role.continuous_nemesis",
            lane_id,
            work_class,
            request_kind,
        )
    domain = str(identity.get("domain_id") or "domain.unassigned")
    role = role_id or "role.unassigned"
    return _generated_mount_policy(
        "fallback_assignment_requires_domain_steward_review",
        domain,
        role,
        lane_id,
        work_class,
        request_kind,
    )


def _metadata_assignment_lifecycle_map(root: Path) -> dict[str, Mapping[str, Any]]:
    preview_path = (
        root
        / DEFAULT_QUEUE_GOVERNANCE_DIR
        / DEFAULT_GLOBAL_QUEUE_REPAIR_PREVIEW_NAME
    )
    preview = _read_json(preview_path)
    if not preview:
        return {}
    lifecycle_map: dict[str, Mapping[str, Any]] = {}
    for row in list(preview.get("lifecycle_preview_rows") or []):
        if not isinstance(row, Mapping):
            continue
        request_id = str(row.get("request_id") or "")
        if request_id:
            lifecycle_map[request_id] = _label_stale_lifecycle_preview_metadata(row)
    return lifecycle_map


def _stale_lifecycle_preview_metadata_label(row: Mapping[str, Any]) -> dict[str, Any]:
    preview_lane_id = str(row.get("preview_lane_id") or row.get("lane_id") or "")
    return {
        "lifecycle_preview_metadata_status": STALE_LIFECYCLE_PREVIEW_METADATA_STATUS,
        "identity_scope": STALE_LIFECYCLE_PREVIEW_IDENTITY_SCOPE,
        "preview_lane_id": preview_lane_id,
        "current_route_identity_authority": False,
        "current_mount_identity_authority": False,
        "current_worker_identity_authority": False,
        "current_route_identity_source": (
            "replacement_request_fields_or_metadata_identity_reissue.assignment"
        ),
    }


def _label_stale_lifecycle_preview_metadata(row: Mapping[str, Any]) -> dict[str, Any]:
    if not row:
        return {}
    labeled = dict(row)
    if str(labeled.get("repair_class") or "") in {
        "stale_waiting_reconciliation_required",
        "terminal_lifecycle_classification_required",
    } or labeled.get("stale") or labeled.get("terminal_repair_needed"):
        labeled.update(_stale_lifecycle_preview_metadata_label(labeled))
    return labeled


def _unlabeled_stale_lifecycle_preview_metadata(row: Mapping[str, Any]) -> bool:
    if not row:
        return False
    stale_preview = (
        str(row.get("repair_class") or "") in {
            "stale_waiting_reconciliation_required",
            "terminal_lifecycle_classification_required",
        }
        or bool(row.get("stale"))
        or bool(row.get("terminal_repair_needed"))
    )
    if not stale_preview:
        return False
    return str(row.get("lifecycle_preview_metadata_status") or "") != (
        STALE_LIFECYCLE_PREVIEW_METADATA_STATUS
    )


def _request_lifecycle_preview_rows(
    payload: Mapping[str, Any],
    reissue_body: Mapping[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in (
        _mapping(payload.get("source_safety")),
        _mapping(_mapping(reissue_body.get("source_safety"))),
    ):
        lifecycle_row = _mapping(source.get("lifecycle_preview_row"))
        if lifecycle_row:
            rows.append(dict(lifecycle_row))
    return rows


def _metadata_assignment_source_safety(
    root: Path,
    row: Mapping[str, Any],
    *,
    source_payload: Mapping[str, Any],
    lifecycle_row: Mapping[str, Any],
) -> dict[str, Any]:
    source_status = str(row.get("source_status") or source_payload.get("status") or "")
    context_gate = source_payload.get("context_gate")
    lifecycle_row_labeled = _label_stale_lifecycle_preview_metadata(lifecycle_row)
    lifecycle_repair_class = str(lifecycle_row.get("repair_class") or "")
    blockers: list[dict[str, Any]] = []
    context_gate_reissue = dict(
        _context_gate_reissue_written_map(root).get(str(row.get("source_request_id") or ""))
        or {}
    )
    context_gate_reissued_for_metadata_reissue = bool(context_gate_reissue)
    metadata_identity_reissue = dict(
        _metadata_identity_reissue_written_map(root).get(str(row.get("source_request_id") or ""))
        or {}
    )
    metadata_identity_reissued_for_metadata_reissue = bool(metadata_identity_reissue)
    stale_settlement = dict(
        _stale_waiting_settlement_map(root).get(str(row.get("source_request_id") or ""))
        or {}
    )
    stale_settled_for_metadata_reissue = bool(stale_settlement)
    if (
        source_status == "CODEX_QUEUE_RUNNER_BLOCKED_CONTEXT_GATE"
        or isinstance(context_gate, Mapping)
    ) and not context_gate_reissued_for_metadata_reissue:
        blockers.append(
            {
                "code": "source_context_gate_requires_dedicated_reissue_packet",
                "detail": "source request is context-gate blocked or carries context_gate evidence",
                "required_packet": "PCKT-DOMAIN-WEAVER-CONTEXT-GATE-BLOCKED-REQUEST-REISSUE-V0_1",
            }
        )
    if (
        lifecycle_repair_class == "stale_waiting_reconciliation_required"
        and not stale_settled_for_metadata_reissue
    ):
        blockers.append(
            {
                "code": "source_lifecycle_stale_waiting_requires_reconciliation",
                "detail": "source request is stale waiting in lifecycle preview",
                "required_packet": "PCKT-DOMAIN-WEAVER-STALE-WAITING-REQUEST-RECONCILIATION-V0_2",
            }
        )
    if lifecycle_repair_class == "terminal_lifecycle_classification_required":
        blockers.append(
            {
                "code": "source_terminal_lifecycle_requires_classification",
                "detail": "source request needs terminal lifecycle classification before reissue",
                "required_packet": "PCKT-DOMAIN-WEAVER-QUEUE-LIFECYCLE-PREVIEW-SETTLEMENT-V0_1",
            }
        )
    return {
        "apply_source_safe": not blockers,
        "source_status": source_status,
        "source_queueable_for_start": bool(row.get("queueable_for_start")),
        "source_active_context_ready": bool(row.get("active_context_ready")),
        "source_context_gate_present": isinstance(context_gate, Mapping),
        "source_context_gate": dict(context_gate) if isinstance(context_gate, Mapping) else None,
        "source_context_gate_reissued_for_metadata_reissue": context_gate_reissued_for_metadata_reissue,
        "source_context_gate_reissue": context_gate_reissue or None,
        "source_metadata_identity_reissued_for_metadata_reissue": metadata_identity_reissued_for_metadata_reissue,
        "source_metadata_identity_reissue": metadata_identity_reissue or None,
        "lifecycle_preview_class": lifecycle_repair_class or None,
        "lifecycle_preview_metadata_label": (
            _stale_lifecycle_preview_metadata_label(lifecycle_row_labeled)
            if lifecycle_row_labeled
            else None
        ),
        "lifecycle_preview_row": lifecycle_row_labeled if lifecycle_row_labeled else None,
        "source_lifecycle_settled_for_metadata_reissue": stale_settled_for_metadata_reissue,
        "source_lifecycle_settlement": stale_settlement or None,
        "safety_blockers": blockers,
    }


def _existing_mount_policy(
    basis: str,
    domain_id: str,
    role_id: str,
    mount_id: str,
    lane_id: str,
    work_class: str,
    request_kind: str,
    *,
    callsign: str,
) -> dict[str, Any]:
    return {
        "disposition": "existing_mount_assignment_ready",
        "basis": basis,
        "domain_id": domain_id,
        "role_id": role_id,
        "callsign": callsign,
        "selected_mount_id": mount_id,
        "lane_id": lane_id,
        "work_class": work_class,
        "request_kind": request_kind,
    }


def _generated_mount_policy(
    basis: str,
    domain_id: str,
    role_id: str,
    lane_id: str,
    work_class: str,
    request_kind: str,
) -> dict[str, Any]:
    mount_id = f"{role_id.replace('.', '_')}__{domain_id.replace('.', '_')}"
    return {
        "disposition": "generated_mount_required",
        "basis": basis,
        "domain_id": domain_id,
        "role_id": role_id,
        "callsign": role_id.removeprefix("role.").upper(),
        "lane_id": lane_id,
        "work_class": work_class,
        "request_kind": request_kind,
        "proposed_mount_id": mount_id,
        "proposed_mount_path": f"ION/05_context/current/codex_agent_mounts/{mount_id}",
    }


def _select_existing_mount(
    mount_inventory: Mapping[str, Mapping[str, Any]],
    *,
    domain_id: str,
    role_id: str,
    selected_mount_id: str,
) -> Mapping[str, Any]:
    if selected_mount_id and selected_mount_id in mount_inventory:
        mount = mount_inventory[selected_mount_id]
        if mount.get("domain_id") == domain_id and mount.get("role_id") == role_id:
            return mount
    for mount in mount_inventory.values():
        if mount.get("domain_id") == domain_id and mount.get("role_id") == role_id:
            return mount
    return {}


def _candidate_working_capsule_identity(
    root: Path,
    *,
    source_request_id: str,
    domain_id: str,
    role_id: str,
    mount: Mapping[str, Any],
) -> dict[str, Any]:
    from kernel.ion_working_capsule_identity import (
        build_working_capsule_identity,
        validate_working_capsule_identity,
    )

    mount_path = root / str(mount.get("mount_path") or "")
    identity = build_working_capsule_identity(
        root=root,
        cwd=mount_path,
        domain_id=domain_id,
        role_id=role_id,
        carrier_instance_id=f"codex_metadata_assignment_{_id_fragment(source_request_id)}",
        codex_agent_mount=mount_path,
    ).to_dict()
    validation = validate_working_capsule_identity(root, identity)
    return {"identity": identity, "validation": validation}


def _assignment_recommended_action(disposition: str) -> str:
    return {
        "existing_mount_assignment_ready": "include this row in metadata reissue apply-review candidate replacement body generation",
        "generated_mount_required": "generate or select a unique specialist codex_agent_mount before replacement request review",
        "supersede_or_quarantine_recommended": "route to stale/external backlog quarantine or supersession review instead of automatic reissue",
        "external_quarantine_settled": "stale external non-domain row is candidate-quarantined from Domain Weaver self-evolution routing",
    }.get(disposition, "review metadata assignment before any replacement request generation")


def _assignment_row_next_packet(disposition: str) -> str:
    return {
        "existing_mount_assignment_ready": "PCKT-DOMAIN-WEAVER-QUEUE-REQUEST-METADATA-IDENTITY-REISSUE-APPLY-REVIEW-V0_1",
        "generated_mount_required": "PCKT-DOMAIN-WEAVER-GENERATED-MOUNT-CREATION-FOR-METADATA-REISSUE-V0_1",
        "supersede_or_quarantine_recommended": "PCKT-DOMAIN-WEAVER-STALE-NON-DOMAIN-QUEUE-QUARANTINE-REVIEW-V0_1",
        "external_quarantine_settled": "PCKT-DOMAIN-WEAVER-STALE-NON-DOMAIN-QUEUE-QUARANTINE-FANIN-V0_1",
    }.get(disposition, "PCKT-DOMAIN-WEAVER-METADATA-ASSIGNMENT-REVIEW-V0_1")


def _metadata_identity_assignment_next_packets(
    *,
    apply_review_ready_count: int,
    source_safety_blocked_count: int,
    mount_required_count: int,
    quarantine_count: int,
) -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    if apply_review_ready_count:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-QUEUE-REQUEST-METADATA-IDENTITY-REISSUE-APPLY-REVIEW-V0_1",
                "purpose": "build exact replacement request bodies for existing-mount-ready rows behind hash and mutation gates",
                "authority": "candidate_replacement_body_generation_only_no_queue_start",
                "row_count": apply_review_ready_count,
            }
        )
    if source_safety_blocked_count:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-SOURCE-SAFETY-BLOCKED-METADATA-REISSUE-REVIEW-V0_1",
                "purpose": "settle context-gate or lifecycle safety blockers before replacement-body generation",
                "authority": "candidate_review_only_no_request_file_mutation",
                "row_count": source_safety_blocked_count,
            }
        )
    if mount_required_count:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-GENERATED-MOUNT-CREATION-FOR-METADATA-REISSUE-V0_1",
                "purpose": "create candidate specialist mount packets for rows lacking exact generated mounts",
                "authority": "candidate_mount_generation_only_no_worker_start",
                "row_count": mount_required_count,
            }
        )
    if quarantine_count:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-STALE-NON-DOMAIN-QUEUE-QUARANTINE-REVIEW-V0_1",
                "purpose": "decide whether stale non-Domain-Weaver rows should be superseded, quarantined, or explicitly preserved",
                "authority": "candidate_lifecycle_review_only_no_ledger_write",
                "row_count": quarantine_count,
            }
        )
    return packets


def _queue_metadata_identity_assignment_graph_deltas(
    root: Path,
    *,
    generated_at: str,
    assignment_rows: Sequence[Mapping[str, Any]],
    source_reissue_ref: Mapping[str, Any],
) -> dict[str, Any]:
    claims: list[dict[str, Any]] = [
        {
            "id": "domain_weaver.queue_metadata_identity_assignment",
            "kind": "queue_metadata_identity_assignment",
            "state": "partial_apply_review_ready"
            if any(row.get("candidate_reissue_apply_review_ready") for row in assignment_rows)
            else "blocked",
            "evidence": [
                str(source_reissue_ref.get("path") or ""),
                "ION/05_context/current/codex_agent_mounts",
            ],
            "value": {
                "assignment_row_count": len(assignment_rows),
                "apply_review_ready_count": sum(
                    1 for row in assignment_rows if row.get("candidate_reissue_apply_review_ready")
                ),
                "source_safety_blocked_count": sum(
                    1
                    for row in assignment_rows
                    if row.get("assignment_disposition") == "existing_mount_assignment_ready"
                    and not row.get("candidate_reissue_apply_review_ready")
                ),
                "request_files_mutated": False,
                "replacement_requests_written": 0,
                "mounts_created": 0,
            },
        }
    ]
    claims.extend(
        {
            "id": f"domain_weaver.queue_metadata_identity_assignment.{row.get('source_request_id')}",
            "kind": "queue_metadata_identity_assignment_row",
            "state": row.get("assignment_disposition"),
            "evidence": [
                str(row.get("source_request_path") or ""),
                str(_mapping(row.get("assigned_identity")).get("selected_mount_path") or ""),
            ],
            "value": {
                "assigned_identity": dict(_mapping(row.get("assigned_identity"))),
                "candidate_reissue_apply_review_ready": bool(
                    row.get("candidate_reissue_apply_review_ready")
                ),
                "source_safety": dict(_mapping(row.get("source_safety"))),
                "would_write_replacement_request": False,
                "would_create_mount": False,
            },
        }
        for row in assignment_rows
    )
    return {
        "schema_id": QUEUE_METADATA_IDENTITY_ASSIGNMENT_DELTA_SCHEMA_ID,
        "generated_at": generated_at,
        "active_root": str(root),
        "status": "candidate_queue_metadata_identity_assignment_deltas_built",
        "upsert_claims": claims,
        "write_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _load_metadata_assignment_or_build(
    root: Path,
    *,
    generated_at: str,
    source_assignment: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if source_assignment is not None:
        return dict(source_assignment), {
            "path": "",
            "exists": True,
            "required": False,
            "kind": "provided_payload",
            "schema_id": source_assignment.get("schema_id"),
            "generated_at": source_assignment.get("generated_at"),
        }
    assignment_path = (
        root
        / DEFAULT_QUEUE_GOVERNANCE_DIR
        / DEFAULT_QUEUE_METADATA_IDENTITY_ASSIGNMENT_NAME
    )
    assignment = _read_json(assignment_path)
    if assignment:
        ref = _file_ref(root, assignment_path)
        ref["kind"] = "file"
        ref["schema_id"] = assignment.get("schema_id")
        ref["generated_at"] = assignment.get("generated_at")
        return assignment, ref
    built = build_queue_metadata_identity_assignment(root, generated_at=generated_at)
    return built, {
        "path": "",
        "exists": True,
        "required": False,
        "kind": "rebuilt_in_memory",
        "schema_id": built.get("schema_id"),
        "generated_at": built.get("generated_at"),
    }


def _load_metadata_apply_review_or_build(
    root: Path,
    *,
    review: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if review is not None:
        return dict(review), {
            "path": "",
            "exists": True,
            "required": False,
            "kind": "provided_payload",
            "schema_id": review.get("schema_id"),
            "generated_at": review.get("generated_at"),
        }
    review_path = (
        root
        / DEFAULT_QUEUE_GOVERNANCE_DIR
        / DEFAULT_QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_NAME
    )
    loaded = _read_json(review_path)
    if loaded:
        ref = _file_ref(root, review_path)
        ref["kind"] = "file"
        ref["schema_id"] = loaded.get("schema_id")
        ref["generated_at"] = loaded.get("generated_at")
        return loaded, ref
    built = build_queue_metadata_identity_reissue_apply_review(root)
    return built, {
        "path": "",
        "exists": True,
        "required": False,
        "kind": "rebuilt_in_memory",
        "schema_id": built.get("schema_id"),
        "generated_at": built.get("generated_at"),
    }


def _metadata_reissue_apply_review_row(
    root: Path,
    row: Mapping[str, Any],
    *,
    generated_at: str,
) -> dict[str, Any]:
    source_request_id = str(row.get("source_request_id") or "")
    source_request_path = str(row.get("source_request_path") or "")
    source_path = root / source_request_path
    source_payload = _read_json(source_path)
    source_ref = _file_ref(root, source_path)
    source_sha = _sha256_file(source_path) if source_path.is_file() else ""
    assigned_identity = _mapping(row.get("assigned_identity"))
    replacement_request_id = _candidate_replacement_request_id(
        source_request_id,
        source_sha,
        generated_at,
    )
    replacement_request_path = (
        CODEX_WORK_REQUESTS_DIR / f"{replacement_request_id}.json"
    ).as_posix()
    replacement_body = _candidate_metadata_reissue_replacement_body(
        source_payload=source_payload,
        source_request_id=source_request_id,
        source_request_path=source_request_path,
        source_request_sha256=source_sha,
        replacement_request_id=replacement_request_id,
        replacement_request_path=replacement_request_path,
        assigned_identity=assigned_identity,
        working_capsule_identity=_mapping(row.get("candidate_working_capsule_identity")),
        source_safety=_mapping(row.get("source_safety")),
        generated_at=generated_at,
    )
    replacement_body_text = _stable_json(replacement_body)
    replacement_body_sha = _sha256_text(replacement_body_text)
    target_path = root / replacement_request_path
    apply_ready = bool(
        source_ref.get("exists")
        and source_sha
        and assigned_identity.get("domain_id")
        and assigned_identity.get("role_id")
        and assigned_identity.get("selected_mount_id")
        and replacement_body.get("working_capsule_identity")
    )
    return {
        "schema_id": "ion.domain_weaver.queue_metadata_identity_reissue_apply_review_row.v0_1_candidate",
        "row_kind": "queue_metadata_identity_reissue_apply_review_candidate",
        "source_request_id": source_request_id,
        "source_request_path": source_request_path,
        "source_request_ref": source_ref,
        "source_request_sha256": source_sha,
        "source_assignment_disposition": row.get("assignment_disposition"),
        "source_safety": dict(_mapping(row.get("source_safety"))),
        "assigned_identity": dict(assigned_identity),
        "candidate_replacement_request_id": replacement_request_id,
        "candidate_replacement_request_path": replacement_request_path,
        "candidate_replacement_target_ref": _file_ref(root, target_path, required=False),
        "candidate_body_filename": _candidate_replacement_body_filename(
            source_request_id,
            replacement_body_sha,
        ),
        "candidate_replacement_body_sha256": replacement_body_sha,
        "candidate_replacement_body": replacement_body,
        "apply_candidate_ready": apply_ready,
        "required_apply_confirmation": "ION_METADATA_IDENTITY_REISSUE_APPLY_CONFIRMED",
        "required_apply_checks": [
            "source_request_sha256_matches_current_file",
            "candidate_replacement_body_sha256_matches_review",
            "candidate_replacement_target_path_absent_or_explicitly_supersede_confirmed",
            "exact_request_path_only_after_write",
            "general_queue_processing_remains_blocked",
        ],
        "apply_performed": False,
        "would_write_replacement_request": False,
        "would_mutate_source_request": False,
        "codex_queue_run_started": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _exact_reissue_route_fields(
    *,
    source_payload: Mapping[str, Any],
    assigned_identity: Mapping[str, Any],
) -> dict[str, Any]:
    work_class = str(
        assigned_identity.get("work_class")
        or source_payload.get("work_class")
        or source_payload.get("workload_class")
        or "domain_weaver_exact_reissue"
    )
    route_family = str(
        source_payload.get("route_family")
        or source_payload.get("request_family")
        or source_payload.get("request_kind")
        or "domain_weaver_exact_reissue"
    )
    source_risk = str(source_payload.get("risk_level") or source_payload.get("risk") or "")
    normalized_risk = "red_alert" if source_risk == "red_alert" else "critical"
    model_override = source_payload.get("codex_model_override")
    if not isinstance(model_override, Mapping):
        model_override = {}
    override_reason = str(
        model_override.get("reason")
        or source_payload.get("model_override_reason")
        or "Exact Domain Weaver reissue worker requires high-integrity bounded context proof."
    )
    requested_effort = str(source_payload.get("requested_reasoning_effort") or "xhigh")
    return {
        "work_class": work_class,
        "route_family": route_family,
        "risk_level": normalized_risk,
        "risk_detail": source_risk or normalized_risk,
        "route_metadata": {
            "work_class": work_class,
            "route_family": route_family,
            "risk_level": normalized_risk,
            "risk_detail": source_risk or normalized_risk,
            "raw": {
                "work_class": str(source_payload.get("work_class") or work_class),
                "route_family": str(source_payload.get("route_family") or route_family),
                "risk_level": source_risk or normalized_risk,
            },
            "explicit_fields": {
                "work_class": True,
                "route_family": True,
                "risk_level": True,
            },
        },
        "requested_model": str(source_payload.get("requested_model") or "gpt-5.5"),
        "requested_reasoning_effort": requested_effort,
        "model_override_reason": str(
            source_payload.get("model_override_reason") or override_reason
        ),
        "codex_model_override": {
            "selected_model": str(model_override.get("selected_model") or "gpt-5.5"),
            "selected_reasoning_effort": str(
                model_override.get("selected_reasoning_effort") or requested_effort
            ),
            "reason": override_reason,
            "service_tier": str(model_override.get("service_tier") or "fast"),
        },
    }


def _candidate_metadata_reissue_replacement_body(
    *,
    source_payload: Mapping[str, Any],
    source_request_id: str,
    source_request_path: str,
    source_request_sha256: str,
    replacement_request_id: str,
    replacement_request_path: str,
    assigned_identity: Mapping[str, Any],
    working_capsule_identity: Mapping[str, Any],
    source_safety: Mapping[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    replacement = dict(source_payload)
    source_context_gate = replacement.pop("context_gate", None)
    source_status = replacement.get("status")
    source_safety_payload = dict(source_safety)
    lifecycle_preview_row = _label_stale_lifecycle_preview_metadata(
        _mapping(source_safety_payload.get("lifecycle_preview_row"))
    )
    lifecycle_preview_label = (
        _stale_lifecycle_preview_metadata_label(lifecycle_preview_row)
        if lifecycle_preview_row
        else None
    )
    if lifecycle_preview_row:
        source_safety_payload["lifecycle_preview_row"] = lifecycle_preview_row
        source_safety_payload["lifecycle_preview_metadata_label"] = lifecycle_preview_label
    objective = str(replacement.get("objective") or "")
    objective_sha = str(replacement.get("objective_sha256") or "") or _sha256_text(objective).strip()
    route_fields = _exact_reissue_route_fields(
        source_payload=source_payload,
        assigned_identity=assigned_identity,
    )
    replacement.update(
        {
            "request_id": replacement_request_id,
            "path": replacement_request_path,
            "status": "QUEUED_FOR_CODEX_CARRIER",
            "created_at": generated_at,
            "updated_at": generated_at,
            "domain_id": assigned_identity.get("domain_id"),
            "lane_id": assigned_identity.get("lane_id"),
            "role_id": assigned_identity.get("role_id"),
            "agent_role_id": assigned_identity.get("role_id"),
            "callsign": assigned_identity.get("callsign"),
            "work_class": assigned_identity.get("work_class"),
            "request_kind": assigned_identity.get("request_kind"),
            **route_fields,
            "selected_mount_id": assigned_identity.get("selected_mount_id"),
            "selected_mount_path": assigned_identity.get("selected_mount_path"),
            "active_context_package_path": assigned_identity.get("active_context_package_path"),
            "active_context_ready": True,
            "active_context_check_status": "metadata_identity_reissue_apply_review_ready",
            "working_capsule_identity": dict(working_capsule_identity),
            "source_request_id": source_request_id,
            "source_request_path": source_request_path,
            "source_request_sha256": source_request_sha256,
            "source_request_status": source_status,
            "source_safety": source_safety_payload,
            "source_lifecycle_preview_metadata_label": lifecycle_preview_label,
            "source_dedupe_key": source_payload.get("dedupe_key"),
            "dedupe_key": _metadata_reissue_dedupe_key(
                source_request_id,
                source_request_sha256,
            ),
            "objective_sha256": objective_sha,
            "exact_request_path_required": True,
            "general_queue_processing_allowed": False,
            "worker_return_is_carrier_intake_only": True,
            "candidate_only": True,
            "accepted_state_claimed": False,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
            "metadata_identity_reissue": {
                "schema_id": "ion.domain_weaver.metadata_identity_reissue_request_body.v0_1_candidate",
                "generated_at": generated_at,
                "source_request_id": source_request_id,
                "source_request_path": source_request_path,
                "source_request_sha256": source_request_sha256,
                "replacement_request_id": replacement_request_id,
                "replacement_request_path": replacement_request_path,
                "assignment": dict(assigned_identity),
                "source_safety": source_safety_payload,
                "source_lifecycle_preview_metadata_label": lifecycle_preview_label,
                "apply_review_only": True,
                "apply_performed": False,
            },
        }
    )
    if source_context_gate is not None:
        replacement["metadata_reissue_source_context_gate"] = source_context_gate
    return replacement


def _candidate_replacement_request_id(
    source_request_id: str,
    source_sha: str,
    generated_at: str,
) -> str:
    stamp = _stamp_from_iso(generated_at).lower()
    digest = hashlib.sha256(
        f"{source_request_id}\0{source_sha}\0{generated_at}".encode("utf-8")
    ).hexdigest()[:12]
    return f"codex_req_metadata_identity_reissue_{stamp}_{digest}"


def _candidate_replacement_body_filename(
    source_request_id: str,
    body_sha: str,
) -> str:
    return f"{_id_fragment(source_request_id)}_{body_sha[:12]}.candidate_replacement_body.json"


def _metadata_reissue_dedupe_key(source_request_id: str, source_sha: str) -> str:
    digest = hashlib.sha256(f"{source_request_id}\0{source_sha}".encode("utf-8")).hexdigest()[:16]
    return f"idempotency_key:metadata-identity-reissue:{digest}"


def _metadata_reissue_apply_review_next_packets(
    *,
    ready_count: int,
    excluded_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    if ready_count:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-QUEUE-REQUEST-METADATA-IDENTITY-REISSUE-BOUNDED-APPLY-V0_1",
                "purpose": "apply reviewed replacement request bodies only after source-before and replacement-body hashes match",
                "authority": "bounded_apply_requires_explicit_confirmation_no_queue_start",
                "row_count": ready_count,
            }
        )
    packet_counts: dict[str, int] = {}
    for row in excluded_rows:
        packet_id = str(row.get("next_packet") or "")
        if packet_id:
            packet_counts[packet_id] = packet_counts.get(packet_id, 0) + 1
    priority = [
        "PCKT-DOMAIN-WEAVER-SOURCE-SAFETY-BLOCKED-METADATA-REISSUE-REVIEW-V0_1",
        "PCKT-DOMAIN-WEAVER-CONTEXT-GATE-BLOCKED-REQUEST-REISSUE-V0_1",
        "PCKT-DOMAIN-WEAVER-STALE-WAITING-REQUEST-RECONCILIATION-V0_2",
        "PCKT-DOMAIN-WEAVER-GENERATED-MOUNT-CREATION-FOR-METADATA-REISSUE-V0_1",
        "PCKT-DOMAIN-WEAVER-STALE-NON-DOMAIN-QUEUE-QUARANTINE-REVIEW-V0_1",
    ]
    ordered_packet_ids = [
        packet_id for packet_id in priority if packet_id in packet_counts
    ]
    ordered_packet_ids.extend(
        packet_id for packet_id in packet_counts if packet_id not in set(priority)
    )
    for packet_id in ordered_packet_ids:
        count = packet_counts[packet_id]
        packets.append(
            {
                "packet_id": packet_id,
                "purpose": "continue excluded assignment row handling before apply review",
                "authority": "candidate_only_no_request_file_mutation",
                "row_count": count,
            }
        )
    return packets


def _queue_metadata_identity_reissue_apply_review_graph_deltas(
    root: Path,
    *,
    generated_at: str,
    apply_rows: Sequence[Mapping[str, Any]],
    source_assignment_ref: Mapping[str, Any],
) -> dict[str, Any]:
    claims: list[dict[str, Any]] = [
        {
            "id": "domain_weaver.queue_metadata_identity_reissue_apply_review",
            "kind": "queue_metadata_identity_reissue_apply_review",
            "state": "ready" if apply_rows else "no_ready_rows",
            "evidence": [
                str(source_assignment_ref.get("path") or ""),
                CODEX_WORK_REQUESTS_DIR.as_posix(),
            ],
            "value": {
                "apply_review_row_count": len(apply_rows),
                "replacement_request_files_written": 0,
                "source_request_files_mutated": False,
                "codex_queue_run_started": False,
            },
        }
    ]
    claims.extend(
        {
            "id": f"domain_weaver.queue_metadata_identity_reissue_apply_review.{row.get('source_request_id')}",
            "kind": "queue_metadata_identity_reissue_apply_review_row",
            "state": "apply_candidate_ready" if row.get("apply_candidate_ready") else "blocked",
            "evidence": [
                str(row.get("source_request_path") or ""),
                str(row.get("candidate_replacement_body_path") or ""),
            ],
            "value": {
                "candidate_replacement_request_id": row.get("candidate_replacement_request_id"),
                "candidate_replacement_request_path": row.get("candidate_replacement_request_path"),
                "source_request_sha256": row.get("source_request_sha256"),
                "candidate_replacement_body_sha256": row.get("candidate_replacement_body_sha256"),
                "apply_performed": False,
            },
        }
        for row in apply_rows
    )
    return {
        "schema_id": QUEUE_METADATA_IDENTITY_REISSUE_APPLY_REVIEW_DELTA_SCHEMA_ID,
        "generated_at": generated_at,
        "active_root": str(root),
        "status": "candidate_queue_metadata_identity_reissue_apply_review_deltas_built",
        "upsert_claims": claims,
        "write_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _prepare_metadata_identity_reissue_apply_row(
    root: Path,
    row: Mapping[str, Any],
    *,
    allow_existing_target: bool,
) -> dict[str, Any]:
    source_request_path = str(row.get("source_request_path") or "")
    source_path = root / source_request_path
    expected_source_sha = str(row.get("source_request_sha256") or "")
    current_source_sha = _sha256_file(source_path) if source_path.is_file() else ""
    target_rel = str(row.get("candidate_replacement_request_path") or "")
    target_path = root / target_rel
    body_path_rel = str(row.get("candidate_replacement_body_path") or "")
    candidate_body = _mapping(row.get("candidate_replacement_body"))
    if body_path_rel:
        body_path = root / body_path_rel
        if not body_path.is_file():
            return _metadata_identity_apply_blocker(
                row,
                "candidate_replacement_body_file_missing",
                body_path=body_path_rel,
            )
        body_text = body_path.read_text(encoding="utf-8")
        try:
            body_payload = json.loads(body_text)
        except json.JSONDecodeError:
            return _metadata_identity_apply_blocker(
                row,
                "candidate_replacement_body_file_invalid_json",
                body_path=body_path_rel,
            )
    else:
        body_payload = dict(candidate_body)
        body_text = _stable_json(body_payload)
    expected_body_sha = str(row.get("candidate_replacement_body_sha256") or "")
    current_body_sha = _sha256_text(body_text)
    blockers: list[str] = []
    if not source_path.is_file():
        blockers.append("source_request_missing")
    if expected_source_sha != current_source_sha:
        blockers.append("source_request_sha256_mismatch")
    if expected_body_sha != current_body_sha:
        blockers.append("candidate_replacement_body_sha256_mismatch")
    if target_path.exists() and not allow_existing_target:
        blockers.append("candidate_replacement_target_path_already_exists")
    if str(body_payload.get("path") or "") != target_rel:
        blockers.append("candidate_body_path_mismatch")
    if str(body_payload.get("request_id") or "") != str(row.get("candidate_replacement_request_id") or ""):
        blockers.append("candidate_body_request_id_mismatch")
    if blockers:
        return {
            "ok": False,
            "source_request_id": row.get("source_request_id"),
            "candidate_replacement_request_path": target_rel,
            "blockers": blockers,
            "expected_source_request_sha256": expected_source_sha,
            "current_source_request_sha256": current_source_sha,
            "expected_candidate_replacement_body_sha256": expected_body_sha,
            "current_candidate_replacement_body_sha256": current_body_sha,
            "target_exists": target_path.exists(),
        }
    return {
        "ok": True,
        "source_request_id": row.get("source_request_id"),
        "source_request_path": source_request_path,
        "candidate_replacement_request_id": row.get("candidate_replacement_request_id"),
        "candidate_replacement_request_path": target_rel,
        "source_request_sha256": current_source_sha,
        "candidate_replacement_body_sha256": current_body_sha,
        "candidate_replacement_body_text": body_text,
        "target_preexisting": target_path.exists(),
        "source_request_files_mutated": False,
        "codex_queue_run_started": False,
        "accepted_state_claimed": False,
    }


def _metadata_identity_apply_blocker(
    row: Mapping[str, Any],
    code: str,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "ok": False,
        "source_request_id": row.get("source_request_id"),
        "candidate_replacement_request_path": row.get("candidate_replacement_request_path"),
        "blockers": [code],
        **extra,
    }


def _source_safety_blockers(row: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    safety = _mapping(row.get("source_safety"))
    return [
        blocker
        for blocker in list(safety.get("safety_blockers") or [])
        if isinstance(blocker, Mapping)
    ]


def _metadata_source_safety_review_row(root: Path, row: Mapping[str, Any]) -> dict[str, Any]:
    source_request_path = str(row.get("source_request_path") or "")
    source_path = root / source_request_path if source_request_path else root
    source_ref = (
        _file_ref(root, source_path)
        if source_request_path
        else dict(_mapping(row.get("source_request_ref")))
    )
    source_sha = _sha256_file(source_path) if source_request_path and source_path.is_file() else ""
    source_safety = _mapping(row.get("source_safety"))
    blockers = _source_safety_blockers(row)
    blocker_codes = [
        str(blocker.get("code") or "")
        for blocker in blockers
        if blocker.get("code")
    ]
    required_packets = list(
        dict.fromkeys(
            str(blocker.get("required_packet") or "")
            for blocker in blockers
            if blocker.get("required_packet")
        )
    )
    return {
        "schema_id": "ion.domain_weaver.queue_metadata_source_safety_review_row.v0_1_candidate",
        "row_kind": "queue_metadata_source_safety_review_candidate",
        "source_request_id": row.get("source_request_id"),
        "source_request_path": source_request_path,
        "source_request_ref": source_ref,
        "source_request_sha256": source_sha,
        "assignment_disposition": row.get("assignment_disposition"),
        "assigned_identity": dict(_mapping(row.get("assigned_identity"))),
        "existing_mount_ref": dict(_mapping(row.get("existing_mount_ref"))),
        "candidate_working_capsule_validation": dict(
            _mapping(row.get("candidate_working_capsule_validation"))
        ),
        "working_capsule_identity_posture": row.get("working_capsule_identity_posture"),
        "candidate_identity_lineage_proven": bool(
            row.get("candidate_identity_lineage_proven")
        ),
        "source_status": source_safety.get("source_status"),
        "source_safety": dict(source_safety),
        "source_context_gate": source_safety.get("source_context_gate"),
        "lifecycle_preview_row": source_safety.get("lifecycle_preview_row"),
        "blocker_codes": blocker_codes,
        "required_packets": required_packets,
        "review_disposition": _metadata_source_safety_review_disposition(blocker_codes),
        "next_packet_after_clear": (
            "PCKT-DOMAIN-WEAVER-QUEUE-REQUEST-METADATA-IDENTITY-REISSUE-APPLY-REVIEW-V0_1"
        ),
        "apply_review_unblocked_by_this_packet": False,
        "would_write_replacement_request": False,
        "would_mutate_source_request": False,
        "codex_queue_run_started": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _metadata_source_safety_review_disposition(blocker_codes: Sequence[str]) -> str:
    blocker_set = set(blocker_codes)
    if "source_context_gate_requires_dedicated_reissue_packet" in blocker_set:
        return "context_gate_reissue_or_fresh_context_proof_before_metadata_reissue"
    if "source_lifecycle_stale_waiting_requires_reconciliation" in blocker_set:
        return "lifecycle_reconcile_or_supersede_before_metadata_reissue"
    if "source_terminal_lifecycle_requires_classification" in blocker_set:
        return "terminal_lifecycle_classification_before_metadata_reissue"
    return "review_source_safety_before_metadata_reissue"


def _metadata_source_safety_blocker_counts(
    review_rows: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in review_rows:
        for code in list(row.get("blocker_codes") or []):
            code_str = str(code or "")
            if code_str:
                counts[code_str] = counts.get(code_str, 0) + 1
    return counts


def _metadata_source_safety_required_packet_counts(
    review_rows: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in review_rows:
        for packet_id in list(row.get("required_packets") or []):
            packet_str = str(packet_id or "")
            if packet_str:
                counts[packet_str] = counts.get(packet_str, 0) + 1
    return counts


def _metadata_source_safety_review_next_packets(
    *,
    review_rows: Sequence[Mapping[str, Any]],
    assignment_summary: Mapping[str, Any],
) -> list[dict[str, Any]]:
    required_packet_counts = _metadata_source_safety_required_packet_counts(review_rows)
    purpose_by_packet = {
        "PCKT-DOMAIN-WEAVER-CONTEXT-GATE-BLOCKED-REQUEST-REISSUE-V0_1": "settle context-gate blocked source requests with fresh context evidence or exact reissue",
        "PCKT-DOMAIN-WEAVER-STALE-WAITING-REQUEST-RECONCILIATION-V0_2": "reconcile, supersede, or explicitly preserve stale waiting source requests before metadata reissue",
        "PCKT-DOMAIN-WEAVER-QUEUE-LIFECYCLE-PREVIEW-SETTLEMENT-V0_1": "classify terminal lifecycle source rows before metadata reissue",
    }
    priority = [
        "PCKT-DOMAIN-WEAVER-CONTEXT-GATE-BLOCKED-REQUEST-REISSUE-V0_1",
        "PCKT-DOMAIN-WEAVER-STALE-WAITING-REQUEST-RECONCILIATION-V0_2",
        "PCKT-DOMAIN-WEAVER-QUEUE-LIFECYCLE-PREVIEW-SETTLEMENT-V0_1",
    ]
    ordered = [packet_id for packet_id in priority if packet_id in required_packet_counts]
    ordered.extend(
        packet_id for packet_id in required_packet_counts if packet_id not in set(priority)
    )
    packets = [
        {
            "packet_id": packet_id,
            "purpose": purpose_by_packet.get(
                packet_id,
                "settle source-safety blocker before metadata reissue apply review",
            ),
            "authority": "candidate_review_or_reissue_packet_only_no_general_queue_start",
            "row_count": required_packet_counts[packet_id],
        }
        for packet_id in ordered
    ]
    generated_mount_required_count = int(
        assignment_summary.get("generated_mount_required_count") or 0
    )
    quarantine_count = int(
        assignment_summary.get("supersede_or_quarantine_recommended_count") or 0
    )
    if generated_mount_required_count:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-GENERATED-MOUNT-CREATION-FOR-METADATA-REISSUE-V0_1",
                "purpose": "create or select generated specialist mounts for remaining metadata reissue rows",
                "authority": "candidate_mount_generation_only_no_worker_start",
                "row_count": generated_mount_required_count,
            }
        )
    if quarantine_count:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-STALE-NON-DOMAIN-QUEUE-QUARANTINE-REVIEW-V0_1",
                "purpose": "decide whether stale non-Domain-Weaver rows should be superseded, quarantined, or explicitly preserved",
                "authority": "candidate_lifecycle_review_only_no_ledger_write",
                "row_count": quarantine_count,
            }
        )
    return packets


def _queue_metadata_source_safety_review_graph_deltas(
    root: Path,
    *,
    generated_at: str,
    review_rows: Sequence[Mapping[str, Any]],
    source_assignment_ref: Mapping[str, Any],
) -> dict[str, Any]:
    claims: list[dict[str, Any]] = [
        {
            "id": "domain_weaver.queue_metadata_source_safety_review",
            "kind": "queue_metadata_source_safety_review",
            "state": "blockers_active" if review_rows else "no_blockers",
            "evidence": [
                str(source_assignment_ref.get("path") or ""),
                CODEX_WORK_REQUESTS_DIR.as_posix(),
            ],
            "value": {
                "source_safety_review_row_count": len(review_rows),
                "required_packet_counts": _metadata_source_safety_required_packet_counts(
                    review_rows
                ),
                "apply_review_rows_unblocked": 0,
                "replacement_request_files_written": 0,
                "source_request_files_mutated": False,
            },
        }
    ]
    claims.extend(
        {
            "id": f"domain_weaver.queue_metadata_source_safety_review.{row.get('source_request_id')}",
            "kind": "queue_metadata_source_safety_review_row",
            "state": row.get("review_disposition"),
            "evidence": [
                str(row.get("source_request_path") or ""),
                str(source_assignment_ref.get("path") or ""),
            ],
            "value": {
                "assigned_identity": dict(_mapping(row.get("assigned_identity"))),
                "blocker_codes": list(row.get("blocker_codes") or []),
                "required_packets": list(row.get("required_packets") or []),
                "candidate_identity_lineage_proven": bool(
                    row.get("candidate_identity_lineage_proven")
                ),
                "apply_review_unblocked_by_this_packet": False,
            },
        }
        for row in review_rows
    )
    return {
        "schema_id": QUEUE_METADATA_SOURCE_SAFETY_REVIEW_DELTA_SCHEMA_ID,
        "generated_at": generated_at,
        "active_root": str(root),
        "status": "candidate_queue_metadata_source_safety_review_deltas_built",
        "upsert_claims": claims,
        "write_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _load_source_safety_review_or_build(
    root: Path,
    *,
    generated_at: str,
    source_safety_review: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if source_safety_review is not None:
        return dict(source_safety_review), {
            "path": "",
            "exists": True,
            "required": False,
            "kind": "provided_payload",
            "schema_id": source_safety_review.get("schema_id"),
            "generated_at": source_safety_review.get("generated_at"),
        }
    review_path = (
        root
        / DEFAULT_QUEUE_GOVERNANCE_DIR
        / DEFAULT_QUEUE_METADATA_SOURCE_SAFETY_REVIEW_NAME
    )
    review = _read_json(review_path)
    if review:
        ref = _file_ref(root, review_path)
        ref["kind"] = "file"
        ref["schema_id"] = review.get("schema_id")
        ref["generated_at"] = review.get("generated_at")
        return review, ref
    built = build_queue_metadata_source_safety_review(root, generated_at=generated_at)
    return built, {
        "path": "",
        "exists": True,
        "required": False,
        "kind": "rebuilt_in_memory",
        "schema_id": built.get("schema_id"),
        "generated_at": built.get("generated_at"),
    }


def _context_gate_reissue_review_row(
    root: Path,
    row: Mapping[str, Any],
    *,
    generated_at: str,
) -> dict[str, Any]:
    source_request_id = str(row.get("source_request_id") or "")
    source_request_path = str(row.get("source_request_path") or "")
    source_path = root / source_request_path
    source_payload = _read_json(source_path)
    source_ref = _file_ref(root, source_path)
    source_sha = _sha256_file(source_path) if source_path.is_file() else ""
    assigned_identity = _mapping(row.get("assigned_identity"))
    mount = _mapping(row.get("existing_mount_ref"))
    working_capsule = (
        _candidate_working_capsule_identity(
            root,
            source_request_id=source_request_id,
            domain_id=str(assigned_identity.get("domain_id") or ""),
            role_id=str(assigned_identity.get("role_id") or ""),
            mount=mount,
        )
        if assigned_identity.get("domain_id")
        and assigned_identity.get("role_id")
        and mount.get("mount_path")
        else {}
    )
    working_capsule_validation = _mapping(working_capsule.get("validation"))
    replacement_request_id = _candidate_context_gate_reissue_request_id(
        source_request_id,
        source_sha,
        generated_at,
    )
    replacement_request_path = (
        CODEX_WORK_REQUESTS_DIR / f"{replacement_request_id}.json"
    ).as_posix()
    replacement_body = _candidate_context_gate_reissue_replacement_body(
        source_payload=source_payload,
        source_request_id=source_request_id,
        source_request_path=source_request_path,
        source_request_sha256=source_sha,
        replacement_request_id=replacement_request_id,
        replacement_request_path=replacement_request_path,
        assigned_identity=assigned_identity,
        working_capsule_identity=_mapping(working_capsule.get("identity")),
        source_context_gate=_mapping(row.get("source_context_gate")),
        generated_at=generated_at,
    )
    replacement_body_text = _stable_json(replacement_body)
    replacement_body_sha = _sha256_text(replacement_body_text)
    target_path = root / replacement_request_path
    candidate_ready = bool(
        source_ref.get("exists")
        and source_sha
        and assigned_identity.get("domain_id")
        and assigned_identity.get("role_id")
        and assigned_identity.get("selected_mount_id")
        and replacement_body.get("working_capsule_identity")
        and working_capsule_validation.get("verdict") == "WORKING_CAPSULE_IDENTITY_READY"
    )
    return {
        "schema_id": "ion.domain_weaver.context_gate_blocked_request_reissue_row.v0_1_candidate",
        "row_kind": "context_gate_blocked_request_reissue_candidate",
        "source_request_id": source_request_id,
        "source_request_path": source_request_path,
        "source_request_ref": source_ref,
        "source_request_sha256": source_sha,
        "source_context_gate": dict(_mapping(row.get("source_context_gate"))),
        "source_blocker_codes": list(row.get("blocker_codes") or []),
        "assigned_identity": dict(assigned_identity),
        "existing_mount_ref": dict(mount),
        "candidate_working_capsule_identity": working_capsule.get("identity"),
        "candidate_working_capsule_validation": dict(working_capsule_validation),
        "working_capsule_identity_posture": "mount_bound_identity_not_lineage_proof"
        if working_capsule
        else "no_candidate_working_capsule_identity",
        "candidate_identity_lineage_proven": False,
        "candidate_replacement_request_id": replacement_request_id,
        "candidate_replacement_request_path": replacement_request_path,
        "candidate_replacement_target_ref": _file_ref(root, target_path, required=False),
        "candidate_body_filename": _candidate_context_gate_reissue_body_filename(
            source_request_id,
            replacement_body_sha,
        ),
        "candidate_replacement_body_sha256": replacement_body_sha,
        "candidate_replacement_body": replacement_body,
        "candidate_body_ready": candidate_ready,
        "required_apply_confirmation": "ION_CONTEXT_GATE_REISSUE_APPLY_CONFIRMED",
        "required_apply_checks": [
            "source_request_sha256_matches_current_file",
            "candidate_replacement_body_sha256_matches_review",
            "candidate_replacement_target_path_absent_or_explicitly_supersede_confirmed",
            "exact_request_path_only_after_write",
            "general_queue_processing_remains_blocked",
        ],
        "apply_performed": False,
        "would_write_replacement_request": False,
        "would_mutate_source_request": False,
        "codex_queue_run_started": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _candidate_context_gate_reissue_replacement_body(
    *,
    source_payload: Mapping[str, Any],
    source_request_id: str,
    source_request_path: str,
    source_request_sha256: str,
    replacement_request_id: str,
    replacement_request_path: str,
    assigned_identity: Mapping[str, Any],
    working_capsule_identity: Mapping[str, Any],
    source_context_gate: Mapping[str, Any],
    generated_at: str,
) -> dict[str, Any]:
    replacement = dict(source_payload)
    source_gate = replacement.pop("context_gate", None)
    source_status = replacement.get("status")
    objective = str(replacement.get("objective") or "")
    objective_sha = str(replacement.get("objective_sha256") or "") or _sha256_text(objective).strip()
    route_fields = _exact_reissue_route_fields(
        source_payload=source_payload,
        assigned_identity=assigned_identity,
    )
    replacement.update(
        {
            "request_id": replacement_request_id,
            "path": replacement_request_path,
            "packet_path": replacement_request_path,
            "status": "QUEUED_FOR_CODEX_CARRIER",
            "dispatch_status": "queued_not_started",
            "created_at": generated_at,
            "updated_at": generated_at,
            "domain_id": assigned_identity.get("domain_id"),
            "lane_id": assigned_identity.get("lane_id"),
            "role_id": assigned_identity.get("role_id"),
            "agent_role_id": assigned_identity.get("role_id"),
            "agent_role": assigned_identity.get("role_id"),
            "consumer_role_id": assigned_identity.get("role_id"),
            "callsign": assigned_identity.get("callsign"),
            "agent_display_name": assigned_identity.get("callsign"),
            "work_class": assigned_identity.get("work_class"),
            "request_kind": assigned_identity.get("request_kind")
            or "context_gate_blocked_request_reissue",
            **route_fields,
            "selected_mount_id": assigned_identity.get("selected_mount_id"),
            "selected_mount_path": assigned_identity.get("selected_mount_path"),
            "active_context_package_path": assigned_identity.get("active_context_package_path"),
            "active_context_ready": True,
            "active_context_check_status": "context_gate_reissue_candidate_ready",
            "working_capsule_identity": dict(working_capsule_identity),
            "source_request_id": source_request_id,
            "source_request_path": source_request_path,
            "source_request_sha256": source_request_sha256,
            "source_request_status": source_status,
            "source_context_gate": dict(source_context_gate or _mapping(source_gate)),
            "source_dedupe_key": source_payload.get("dedupe_key"),
            "dedupe_key": _context_gate_reissue_dedupe_key(
                source_request_id,
                source_request_sha256,
            ),
            "objective_sha256": objective_sha,
            "exact_request_path_required": True,
            "general_queue_processing_allowed": False,
            "worker_return_is_carrier_intake_only": True,
            "candidate_only": True,
            "accepted_state_claimed": False,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
            "context_gate_reissue": {
                "schema_id": "ion.domain_weaver.context_gate_reissue_request_body.v0_1_candidate",
                "generated_at": generated_at,
                "source_request_id": source_request_id,
                "source_request_path": source_request_path,
                "source_request_sha256": source_request_sha256,
                "replacement_request_id": replacement_request_id,
                "replacement_request_path": replacement_request_path,
                "assignment": dict(assigned_identity),
                "source_context_gate": dict(source_context_gate or _mapping(source_gate)),
                "apply_review_only": True,
                "apply_performed": False,
            },
        }
    )
    return replacement


def _candidate_context_gate_reissue_request_id(
    source_request_id: str,
    source_sha: str,
    generated_at: str,
) -> str:
    stamp = _stamp_from_iso(generated_at).lower()
    digest = hashlib.sha256(
        f"context_gate_reissue\0{source_request_id}\0{source_sha}\0{generated_at}".encode(
            "utf-8"
        )
    ).hexdigest()[:12]
    return f"codex_req_context_gate_reissue_{stamp}_{digest}"


def _candidate_context_gate_reissue_body_filename(
    source_request_id: str,
    body_sha: str,
) -> str:
    return f"{_id_fragment(source_request_id)}_{body_sha[:12]}.context_gate_reissue_body.json"


def _context_gate_reissue_dedupe_key(source_request_id: str, source_sha: str) -> str:
    digest = hashlib.sha256(
        f"context_gate_reissue\0{source_request_id}\0{source_sha}".encode("utf-8")
    ).hexdigest()[:16]
    return f"idempotency_key:context-gate-reissue:{digest}"


def _context_gate_blocked_request_reissue_next_packets(
    *,
    ready_count: int,
    source_review: Mapping[str, Any],
) -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    if ready_count:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-CONTEXT-GATE-BLOCKED-REQUEST-REISSUE-BOUNDED-APPLY-V0_1",
                "purpose": "apply reviewed context-gate replacement request bodies only after source-before and body hashes match",
                "authority": "bounded_apply_requires_explicit_confirmation_no_queue_start",
                "row_count": ready_count,
            }
        )
    required_counts = _mapping(_mapping(source_review.get("summary")).get("required_packet_counts"))
    stale_count = int(
        required_counts.get("PCKT-DOMAIN-WEAVER-STALE-WAITING-REQUEST-RECONCILIATION-V0_2")
        or 0
    )
    if stale_count:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-STALE-WAITING-REQUEST-RECONCILIATION-V0_2",
                "purpose": "reconcile, supersede, or explicitly preserve stale waiting source requests before metadata reissue",
                "authority": "candidate_lifecycle_review_only_no_ledger_write",
                "row_count": stale_count,
            }
        )
    for packet in list(source_review.get("next_packets") or []):
        if not isinstance(packet, Mapping):
            continue
        packet_id = str(packet.get("packet_id") or "")
        if packet_id in {
            "PCKT-DOMAIN-WEAVER-CONTEXT-GATE-BLOCKED-REQUEST-REISSUE-V0_1",
            "PCKT-DOMAIN-WEAVER-STALE-WAITING-REQUEST-RECONCILIATION-V0_2",
        }:
            continue
        packets.append(dict(packet))
    return packets


def _context_gate_blocked_request_reissue_graph_deltas(
    root: Path,
    *,
    generated_at: str,
    reissue_rows: Sequence[Mapping[str, Any]],
    source_review_ref: Mapping[str, Any],
) -> dict[str, Any]:
    claims: list[dict[str, Any]] = [
        {
            "id": "domain_weaver.context_gate_blocked_request_reissue",
            "kind": "context_gate_blocked_request_reissue",
            "state": "candidate_bodies_ready" if reissue_rows else "no_ready_rows",
            "evidence": [
                str(source_review_ref.get("path") or ""),
                CODEX_WORK_REQUESTS_DIR.as_posix(),
            ],
            "value": {
                "context_gate_reissue_row_count": len(reissue_rows),
                "candidate_body_ready_count": sum(
                    1 for row in reissue_rows if row.get("candidate_body_ready")
                ),
                "replacement_request_files_written": 0,
                "source_request_files_mutated": False,
                "codex_queue_run_started": False,
            },
        }
    ]
    claims.extend(
        {
            "id": f"domain_weaver.context_gate_blocked_request_reissue.{row.get('source_request_id')}",
            "kind": "context_gate_blocked_request_reissue_row",
            "state": "candidate_body_ready" if row.get("candidate_body_ready") else "blocked",
            "evidence": [
                str(row.get("source_request_path") or ""),
                str(row.get("candidate_replacement_body_path") or ""),
            ],
            "value": {
                "candidate_replacement_request_id": row.get("candidate_replacement_request_id"),
                "candidate_replacement_request_path": row.get("candidate_replacement_request_path"),
                "source_request_sha256": row.get("source_request_sha256"),
                "candidate_replacement_body_sha256": row.get("candidate_replacement_body_sha256"),
                "apply_performed": False,
            },
        }
        for row in reissue_rows
    )
    return {
        "schema_id": CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_DELTA_SCHEMA_ID,
        "generated_at": generated_at,
        "active_root": str(root),
        "status": "candidate_context_gate_blocked_request_reissue_deltas_built",
        "upsert_claims": claims,
        "write_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _load_context_gate_reissue_review(
    root: Path,
    *,
    review: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if review is not None:
        return dict(review), {
            "path": "",
            "exists": True,
            "required": False,
            "kind": "provided_payload",
            "schema_id": review.get("schema_id"),
            "generated_at": review.get("generated_at"),
        }
    review_path = (
        root
        / DEFAULT_QUEUE_GOVERNANCE_DIR
        / DEFAULT_CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_NAME
    )
    loaded = _read_json(review_path)
    if loaded:
        ref = _file_ref(root, review_path)
        ref["kind"] = "file"
        ref["schema_id"] = loaded.get("schema_id")
        ref["generated_at"] = loaded.get("generated_at")
        return loaded, ref
    built = build_context_gate_blocked_request_reissue(root)
    return built, {
        "path": "",
        "exists": True,
        "required": False,
        "kind": "rebuilt_in_memory",
        "schema_id": built.get("schema_id"),
        "generated_at": built.get("generated_at"),
    }


def _prepare_context_gate_reissue_apply_row(
    root: Path,
    row: Mapping[str, Any],
    *,
    allow_existing_target: bool,
) -> dict[str, Any]:
    source_request_path = str(row.get("source_request_path") or "")
    source_path = root / source_request_path
    expected_source_sha = str(row.get("source_request_sha256") or "")
    current_source_sha = _sha256_file(source_path) if source_path.is_file() else ""
    target_rel = str(row.get("candidate_replacement_request_path") or "")
    target_path = root / target_rel
    candidate_body = _mapping(row.get("candidate_replacement_body"))
    body_path_rel = str(row.get("candidate_replacement_body_path") or "")
    if body_path_rel:
        body_path = root / body_path_rel
        if not body_path.is_file():
            return _context_gate_apply_blocker(
                row,
                "candidate_replacement_body_file_missing",
                body_path=body_path_rel,
            )
        body_text = body_path.read_text(encoding="utf-8")
        try:
            body_payload = json.loads(body_text)
        except json.JSONDecodeError:
            return _context_gate_apply_blocker(
                row,
                "candidate_replacement_body_file_invalid_json",
                body_path=body_path_rel,
            )
    else:
        body_payload = dict(candidate_body)
        body_text = _stable_json(body_payload)
    expected_body_sha = str(row.get("candidate_replacement_body_sha256") or "")
    current_body_sha = _sha256_text(body_text)
    blockers: list[str] = []
    if not source_path.is_file():
        blockers.append("source_request_missing")
    if expected_source_sha != current_source_sha:
        blockers.append("source_request_sha256_mismatch")
    if expected_body_sha != current_body_sha:
        blockers.append("candidate_replacement_body_sha256_mismatch")
    if target_path.exists() and not allow_existing_target:
        blockers.append("candidate_replacement_target_path_already_exists")
    if str(body_payload.get("path") or "") != target_rel:
        blockers.append("candidate_body_path_mismatch")
    if str(body_payload.get("request_id") or "") != str(row.get("candidate_replacement_request_id") or ""):
        blockers.append("candidate_body_request_id_mismatch")
    if blockers:
        return {
            "ok": False,
            "source_request_id": row.get("source_request_id"),
            "candidate_replacement_request_path": target_rel,
            "blockers": blockers,
            "expected_source_request_sha256": expected_source_sha,
            "current_source_request_sha256": current_source_sha,
            "expected_candidate_replacement_body_sha256": expected_body_sha,
            "current_candidate_replacement_body_sha256": current_body_sha,
            "target_exists": target_path.exists(),
        }
    return {
        "ok": True,
        "source_request_id": row.get("source_request_id"),
        "source_request_path": source_request_path,
        "candidate_replacement_request_id": row.get("candidate_replacement_request_id"),
        "candidate_replacement_request_path": target_rel,
        "source_request_sha256": current_source_sha,
        "candidate_replacement_body_sha256": current_body_sha,
        "candidate_replacement_body_text": body_text,
        "target_preexisting": target_path.exists(),
        "source_request_files_mutated": False,
        "codex_queue_run_started": False,
        "accepted_state_claimed": False,
    }


def _context_gate_apply_blocker(
    row: Mapping[str, Any],
    code: str,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "ok": False,
        "source_request_id": row.get("source_request_id"),
        "candidate_replacement_request_path": row.get("candidate_replacement_request_path"),
        "blockers": [code],
        **extra,
    }


def _context_gate_reissue_written_map(root: Path) -> dict[str, Mapping[str, Any]]:
    work_dir = root / CODEX_WORK_REQUESTS_DIR
    if not work_dir.is_dir():
        return {}
    rows: dict[str, Mapping[str, Any]] = {}
    for path in sorted(work_dir.glob("*.json")):
        payload = _read_json(path)
        if not payload:
            continue
        reissue = _mapping(payload.get("context_gate_reissue"))
        if not reissue:
            continue
        source_request_id = str(
            reissue.get("source_request_id") or payload.get("source_request_id") or ""
        )
        source_request_path = str(
            reissue.get("source_request_path") or payload.get("source_request_path") or ""
        )
        expected_source_sha = str(
            reissue.get("source_request_sha256")
            or payload.get("source_request_sha256")
            or ""
        )
        current_source_sha = (
            _sha256_file(root / source_request_path)
            if source_request_path and (root / source_request_path).is_file()
            else ""
        )
        replacement_request_id = str(
            reissue.get("replacement_request_id") or payload.get("request_id") or ""
        )
        replacement_request_path = str(
            reissue.get("replacement_request_path") or payload.get("path") or _rel(root, path)
        )
        if (
            source_request_id
            and source_request_path
            and expected_source_sha
            and current_source_sha == expected_source_sha
            and replacement_request_id == str(payload.get("request_id") or "")
            and replacement_request_path == _rel(root, path)
        ):
            rows[source_request_id] = {
                "schema_id": "ion.domain_weaver.context_gate_reissue_written_ref.v0_1_candidate",
                "source_request_id": source_request_id,
                "source_request_path": source_request_path,
                "source_request_sha256": expected_source_sha,
                "current_source_request_sha256": current_source_sha,
                "replacement_request_id": replacement_request_id,
                "replacement_request_path": replacement_request_path,
                "replacement_request_sha256": _sha256_file(path),
                "replacement_request_status": payload.get("status"),
                "source_hash_matches_reissue": True,
                "source_request_files_mutated": False,
                "codex_queue_run_started": False,
                "accepted_state_claimed": False,
                "authority": AUTHORITY,
            }
    return rows


def _metadata_identity_reissue_written_map(root: Path) -> dict[str, Mapping[str, Any]]:
    work_dir = root / CODEX_WORK_REQUESTS_DIR
    if not work_dir.is_dir():
        return {}
    rows: dict[str, Mapping[str, Any]] = {}
    for path in sorted(work_dir.glob("*.json")):
        payload = _read_json(path)
        if not payload:
            continue
        reissue = _mapping(payload.get("metadata_identity_reissue"))
        if not reissue:
            continue
        source_request_id = str(
            reissue.get("source_request_id") or payload.get("source_request_id") or ""
        )
        source_request_path = str(
            reissue.get("source_request_path") or payload.get("source_request_path") or ""
        )
        expected_source_sha = str(
            reissue.get("source_request_sha256")
            or payload.get("source_request_sha256")
            or ""
        )
        current_source_sha = (
            _sha256_file(root / source_request_path)
            if source_request_path and (root / source_request_path).is_file()
            else ""
        )
        replacement_request_id = str(
            reissue.get("replacement_request_id") or payload.get("request_id") or ""
        )
        replacement_request_path = str(
            reissue.get("replacement_request_path") or payload.get("path") or _rel(root, path)
        )
        if (
            source_request_id
            and source_request_path
            and expected_source_sha
            and current_source_sha == expected_source_sha
            and replacement_request_id == str(payload.get("request_id") or "")
            and replacement_request_path == _rel(root, path)
        ):
            rows[source_request_id] = {
                "schema_id": "ion.domain_weaver.metadata_identity_reissue_written_ref.v0_1_candidate",
                "source_request_id": source_request_id,
                "source_request_path": source_request_path,
                "source_request_sha256": expected_source_sha,
                "current_source_request_sha256": current_source_sha,
                "replacement_request_id": replacement_request_id,
                "replacement_request_path": replacement_request_path,
                "replacement_request_sha256": _sha256_file(path),
                "replacement_request_status": payload.get("status"),
                "source_hash_matches_reissue": True,
                "source_request_files_mutated": False,
                "codex_queue_run_started": False,
                "accepted_state_claimed": False,
                "authority": AUTHORITY,
            }
    return rows


def _stale_waiting_reconciliation_review_row(
    root: Path,
    row: Mapping[str, Any],
) -> dict[str, Any]:
    source_request_id = str(row.get("source_request_id") or "")
    source_request_path = str(row.get("source_request_path") or "")
    source_path = root / source_request_path
    source_payload = _read_json(source_path)
    source_ref = _file_ref(root, source_path)
    source_sha = _sha256_file(source_path) if source_path.is_file() else ""
    lifecycle_row = _mapping(row.get("lifecycle_preview_row"))
    assigned_identity = _mapping(row.get("assigned_identity"))
    source_status = str(
        lifecycle_row.get("status")
        or _mapping(row.get("source_safety")).get("source_status")
        or source_payload.get("status")
        or ""
    )
    recommended = _stale_waiting_recommended_reconciliation(
        lifecycle_row=lifecycle_row,
        source_payload=source_payload,
    )
    return {
        "schema_id": "ion.domain_weaver.stale_waiting_reconciliation_review_row.v0_1_candidate",
        "row_kind": "stale_waiting_reconciliation_review_candidate",
        "source_request_id": source_request_id,
        "source_request_path": source_request_path,
        "source_request_ref": source_ref,
        "source_request_sha256": source_sha,
        "source_status": source_status,
        "source_created_at": source_payload.get("created_at"),
        "source_updated_at": source_payload.get("updated_at"),
        "source_dedupe_key": source_payload.get("dedupe_key"),
        "source_objective_sha256": source_payload.get("objective_sha256"),
        "assigned_identity": dict(assigned_identity),
        "lifecycle_preview_row": dict(lifecycle_row),
        "recommended_reconciliation": recommended,
        "candidate_reconciliation_choices": [
            {
                "choice": "supersede_with_fresh_exact_request",
                "effect": "future packet may write a fresh exact request and mark the stale source superseded behind hash and ledger gates",
                "requires_mutation_gate": True,
            },
            {
                "choice": "preserve_as_explicit_backlog",
                "effect": "future packet may preserve the stale source with an explicit backlog rationale",
                "requires_mutation_gate": True,
            },
            {
                "choice": "quarantine_as_stale_non_current",
                "effect": "future packet may quarantine or retire the stale source after lead/Nemesis review",
                "requires_mutation_gate": True,
            },
        ],
        "decision_ready": False,
        "decision_blocker": "lead_or_operator_must_choose_reconcile_supersede_preserve_or_quarantine",
        "required_settlement_confirmation": "ION_STALE_WAITING_RECONCILIATION_SETTLEMENT_CONFIRMED",
        "would_write_lifecycle_ledger": False,
        "would_mutate_source_request": False,
        "would_write_replacement_request": False,
        "codex_queue_run_started": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _stale_waiting_recommended_reconciliation(
    *,
    lifecycle_row: Mapping[str, Any],
    source_payload: Mapping[str, Any],
) -> str:
    request_kind = str(source_payload.get("request_kind") or "")
    work_class = str(source_payload.get("work_class") or "")
    if request_kind == "read_only_nemesis" or work_class == "incident_nemesis_review":
        return "supersede_with_fresh_exact_request_or_preserve_as_incident_backlog_after_nemesis_review"
    if lifecycle_row.get("recommended_lifecycle_disposition"):
        return str(lifecycle_row.get("recommended_lifecycle_disposition"))
    return "reconcile_or_supersede_before_claim"


def _stale_waiting_reconciliation_review_next_packets(
    *,
    reconciliation_rows: Sequence[Mapping[str, Any]],
    source_review: Mapping[str, Any],
) -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    if reconciliation_rows:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-STALE-WAITING-REQUEST-RECONCILIATION-SETTLEMENT-V0_2",
                "purpose": "choose preserve, supersede, or quarantine for stale waiting rows behind source hash and ledger gates",
                "authority": "bounded_lifecycle_settlement_requires_explicit_confirmation",
                "row_count": len(reconciliation_rows),
            }
        )
    for packet in list(source_review.get("next_packets") or []):
        if not isinstance(packet, Mapping):
            continue
        packet_id = str(packet.get("packet_id") or "")
        if packet_id in {
            "PCKT-DOMAIN-WEAVER-CONTEXT-GATE-BLOCKED-REQUEST-REISSUE-V0_1",
            "PCKT-DOMAIN-WEAVER-STALE-WAITING-REQUEST-RECONCILIATION-V0_2",
        }:
            continue
        packets.append(dict(packet))
    return packets


def _stale_waiting_reconciliation_review_graph_deltas(
    root: Path,
    *,
    generated_at: str,
    reconciliation_rows: Sequence[Mapping[str, Any]],
    source_review_ref: Mapping[str, Any],
) -> dict[str, Any]:
    claims: list[dict[str, Any]] = [
        {
            "id": "domain_weaver.stale_waiting_reconciliation_review",
            "kind": "stale_waiting_reconciliation_review",
            "state": "decision_required" if reconciliation_rows else "no_rows",
            "evidence": [
                str(source_review_ref.get("path") or ""),
                CODEX_WORK_REQUESTS_DIR.as_posix(),
            ],
            "value": {
                "stale_reconciliation_row_count": len(reconciliation_rows),
                "decision_required_count": len(reconciliation_rows),
                "lifecycle_ledger_mutated": False,
                "request_files_mutated": False,
                "replacement_request_files_written": 0,
            },
        }
    ]
    claims.extend(
        {
            "id": f"domain_weaver.stale_waiting_reconciliation_review.{row.get('source_request_id')}",
            "kind": "stale_waiting_reconciliation_review_row",
            "state": row.get("recommended_reconciliation"),
            "evidence": [
                str(row.get("source_request_path") or ""),
                str(source_review_ref.get("path") or ""),
            ],
            "value": {
                "source_request_sha256": row.get("source_request_sha256"),
                "source_status": row.get("source_status"),
                "decision_ready": bool(row.get("decision_ready")),
                "decision_blocker": row.get("decision_blocker"),
                "would_write_lifecycle_ledger": False,
            },
        }
        for row in reconciliation_rows
    )
    return {
        "schema_id": STALE_WAITING_RECONCILIATION_REVIEW_DELTA_SCHEMA_ID,
        "generated_at": generated_at,
        "active_root": str(root),
        "status": "candidate_stale_waiting_reconciliation_review_deltas_built",
        "upsert_claims": claims,
        "write_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _load_stale_waiting_reconciliation_review_or_build(
    root: Path,
    *,
    generated_at: str,
    review: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if review is not None:
        return dict(review), {
            "path": "",
            "exists": True,
            "required": False,
            "kind": "provided_payload",
            "schema_id": review.get("schema_id"),
            "generated_at": review.get("generated_at"),
        }
    review_path = (
        root
        / DEFAULT_QUEUE_GOVERNANCE_DIR
        / DEFAULT_STALE_WAITING_RECONCILIATION_REVIEW_NAME
    )
    loaded = _read_json(review_path)
    if loaded:
        ref = _file_ref(root, review_path)
        ref["kind"] = "file"
        ref["schema_id"] = loaded.get("schema_id")
        ref["generated_at"] = loaded.get("generated_at")
        return loaded, ref
    built = build_stale_waiting_reconciliation_review(root, generated_at=generated_at)
    return built, {
        "path": "",
        "exists": True,
        "required": False,
        "kind": "rebuilt_in_memory",
        "schema_id": built.get("schema_id"),
        "generated_at": built.get("generated_at"),
    }


def _stale_waiting_settlement_row(
    root: Path,
    row: Mapping[str, Any],
    *,
    settlement_decision: str,
) -> dict[str, Any]:
    allowed_decisions = {
        "supersede_with_fresh_exact_request",
        "preserve_as_explicit_backlog",
        "quarantine_as_stale_non_current",
    }
    source_request_id = str(row.get("source_request_id") or "")
    source_request_path = str(row.get("source_request_path") or "")
    source_path = root / source_request_path if source_request_path else root
    source_exists = source_path.is_file()
    review_sha = str(row.get("source_request_sha256") or "")
    current_sha = _sha256_file(source_path) if source_exists else ""
    blockers: list[str] = []
    if settlement_decision not in allowed_decisions:
        blockers.append("invalid_settlement_decision")
    if not source_request_id:
        blockers.append("missing_source_request_id")
    if not source_request_path:
        blockers.append("missing_source_request_path")
    if not source_exists:
        blockers.append("source_request_file_missing")
    if current_sha != review_sha:
        blockers.append("source_request_sha_mismatch")
    settlement_ready = not blockers
    return {
        "schema_id": "ion.domain_weaver.stale_waiting_reconciliation_settlement_row.v0_2_candidate",
        "row_kind": "stale_waiting_reconciliation_settlement_candidate",
        "source_request_id": source_request_id,
        "source_request_path": source_request_path,
        "source_request_ref": _file_ref(root, source_path)
        if source_request_path
        else dict(_mapping(row.get("source_request_ref"))),
        "source_request_sha256": review_sha,
        "current_source_request_sha256": current_sha,
        "source_hash_matches_review": bool(current_sha and current_sha == review_sha),
        "source_status": row.get("source_status"),
        "assigned_identity": dict(_mapping(row.get("assigned_identity"))),
        "review_recommended_reconciliation": row.get("recommended_reconciliation"),
        "settlement_decision": settlement_decision,
        "settlement_effect": _stale_waiting_settlement_effect(settlement_decision),
        "settlement_ready": settlement_ready,
        "settlement_blockers": blockers,
        "metadata_reissue_source_safety_may_clear": bool(
            settlement_ready
            and settlement_decision == "supersede_with_fresh_exact_request"
        ),
        "candidate_lifecycle_settlement_written": False,
        "accepted_lifecycle_ledger_mutated": False,
        "source_request_files_mutated": False,
        "replacement_request_files_written": 0,
        "codex_queue_run_started": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _stale_waiting_settlement_effect(settlement_decision: str) -> str:
    if settlement_decision == "supersede_with_fresh_exact_request":
        return (
            "future metadata reissue may create a fresh exact replacement request; "
            "the stale source request remains historical and must not be run broadly"
        )
    if settlement_decision == "preserve_as_explicit_backlog":
        return (
            "the stale source remains explicit backlog evidence and does not clear "
            "metadata reissue source-safety by itself"
        )
    if settlement_decision == "quarantine_as_stale_non_current":
        return (
            "the stale source is candidate-quarantined from current self-evolution "
            "routing and does not clear metadata reissue source-safety by itself"
        )
    return "invalid settlement decision"


def _stale_waiting_reconciliation_settlement_next_packets(
    *,
    settlement_rows: Sequence[Mapping[str, Any]],
    blocked_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if blocked_rows:
        return [
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-STALE-WAITING-REQUEST-RECONCILIATION-REVIEW-REFRESH-V0_2",
                "purpose": "refresh stale waiting review or inspect source hash mismatches before settlement",
                "authority": "candidate_review_only_no_request_file_mutation",
                "row_count": len(blocked_rows),
            }
        ]
    if settlement_rows:
        return [
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-QUEUE-METADATA-SOURCE-SAFETY-REFRESH-AFTER-STALE-SETTLEMENT-V0_1",
                "purpose": "refresh assignment/source-safety/apply review so hash-settled stale rows can move to replacement-body review",
                "authority": "candidate_projection_refresh_only_no_queue_start",
                "row_count": len(settlement_rows),
            }
        ]
    return []


def _stale_waiting_reconciliation_settlement_graph_deltas(
    root: Path,
    *,
    generated_at: str,
    settlement_rows: Sequence[Mapping[str, Any]],
    review_ref: Mapping[str, Any],
    write_performed: bool = False,
) -> dict[str, Any]:
    claims: list[dict[str, Any]] = [
        {
            "id": "domain_weaver.stale_waiting_reconciliation_settlement",
            "kind": "stale_waiting_reconciliation_settlement",
            "state": "written" if write_performed else "ready",
            "evidence": [
                str(review_ref.get("path") or ""),
                CODEX_WORK_REQUESTS_DIR.as_posix(),
            ],
            "value": {
                "settlement_row_count": len(settlement_rows),
                "candidate_lifecycle_settlement_written": write_performed,
                "accepted_lifecycle_ledger_mutated": False,
                "source_request_files_mutated": False,
                "replacement_request_files_written": 0,
                "codex_queue_run_started": False,
            },
        }
    ]
    claims.extend(
        {
            "id": f"domain_weaver.stale_waiting_reconciliation_settlement.{row.get('source_request_id')}",
            "kind": "stale_waiting_reconciliation_settlement_row",
            "state": row.get("settlement_decision"),
            "evidence": [
                str(row.get("source_request_path") or ""),
                str(review_ref.get("path") or ""),
            ],
            "value": {
                "source_request_sha256": row.get("source_request_sha256"),
                "source_hash_matches_review": row.get("source_hash_matches_review"),
                "metadata_reissue_source_safety_may_clear": row.get(
                    "metadata_reissue_source_safety_may_clear"
                ),
                "candidate_lifecycle_settlement_written": write_performed,
            },
        }
        for row in settlement_rows
    )
    return {
        "schema_id": STALE_WAITING_RECONCILIATION_SETTLEMENT_DELTA_SCHEMA_ID,
        "generated_at": generated_at,
        "active_root": str(root),
        "status": "candidate_stale_waiting_reconciliation_settlement_deltas_built",
        "upsert_claims": claims,
        "write_performed": write_performed,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _stale_waiting_settlement_map(root: Path) -> dict[str, Mapping[str, Any]]:
    settlement_path = (
        root
        / DEFAULT_QUEUE_GOVERNANCE_DIR
        / DEFAULT_STALE_WAITING_RECONCILIATION_SETTLEMENT_NAME
    )
    settlement = _read_json(settlement_path)
    if not settlement:
        return {}
    rows: dict[str, Mapping[str, Any]] = {}
    for row in list(settlement.get("settlement_rows") or []):
        if not isinstance(row, Mapping):
            continue
        request_id = str(row.get("source_request_id") or "")
        source_path = str(row.get("source_request_path") or "")
        expected_sha = str(row.get("source_request_sha256") or "")
        current_sha = _sha256_file(root / source_path) if source_path else ""
        if (
            request_id
            and bool(row.get("settlement_ready"))
            and bool(row.get("metadata_reissue_source_safety_may_clear"))
            and current_sha
            and current_sha == expected_sha
        ):
            rows[request_id] = row
    return rows


def _generated_mount_creation_rows(
    root: Path,
    *,
    generated_rows: Sequence[Mapping[str, Any]],
    materialized_mounts: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    by_mount: dict[str, list[Mapping[str, Any]]] = {}
    for row in generated_rows:
        spec = _mapping(row.get("generated_mount_spec"))
        mount_id = str(spec.get("mount_id") or "")
        if mount_id:
            by_mount.setdefault(mount_id, []).append(row)
    creation_rows: list[dict[str, Any]] = []
    for mount_id in sorted(by_mount):
        rows = by_mount[mount_id]
        first = rows[0]
        spec = _mapping(first.get("generated_mount_spec"))
        assigned = _mapping(first.get("assigned_identity"))
        role_id = str(spec.get("role_id") or assigned.get("role_id") or "")
        domain_id = str(spec.get("domain_id") or assigned.get("domain_id") or "")
        mount_path = str(spec.get("mount_path") or assigned.get("selected_mount_path") or "")
        manifest_path = root / mount_path / "ION_AGENT_MOUNT_MANIFEST.json"
        materialized = _mapping(materialized_mounts.get(mount_id))
        candidate = _generated_mount_candidate_record(
            root,
            rows=rows,
            role_id=role_id,
            domain_id=domain_id,
        )
        source_request_ids = [str(row.get("source_request_id") or "") for row in rows]
        required_files = _generated_mount_required_files(mount_path)
        missing_required_files = [
            rel for rel in required_files if not (root / rel).exists()
        ]
        post_manifest_ref = _file_ref(root, manifest_path, required=False)
        creation_rows.append(
            {
                "schema_id": "ion.domain_weaver.generated_mount_creation_row.v0_1_candidate",
                "row_kind": "generated_mount_creation_for_metadata_reissue_candidate",
                "mount_id": mount_id,
                "mount_path": mount_path,
                "domain_id": domain_id,
                "role_id": role_id,
                "callsign": assigned.get("callsign") or role_id.removeprefix("role.").upper(),
                "source_request_ids": source_request_ids,
                "source_request_count": len(source_request_ids),
                "source_assignment_rows": [
                    {
                        "source_request_id": row.get("source_request_id"),
                        "source_request_path": row.get("source_request_path"),
                        "assigned_identity": dict(_mapping(row.get("assigned_identity"))),
                        "source_safety": dict(_mapping(row.get("source_safety"))),
                    }
                    for row in rows
                ],
                "generated_mount_spec": dict(spec),
                "agent_record": dict(candidate["agent"]),
                "domain_record": dict(candidate["domain"]),
                "candidate_mount": dict(candidate["mount"]),
                "preexisting_manifest_ref": _file_ref(root, manifest_path, required=False),
                "post_manifest_ref": post_manifest_ref,
                "materialized_by_this_packet": bool(materialized),
                "materialization_result": materialized.get("materialization_result"),
                "materialized_mount": dict(materialized),
                "required_files": required_files,
                "missing_required_files": missing_required_files,
                "creation_candidate_ready": bool(
                    mount_id
                    and mount_path
                    and role_id
                    and domain_id
                    and not materialized.get("error")
                ),
                "would_start_worker": False,
                "codex_queue_run_started": False,
                "accepted_state_claimed": False,
                "authority": AUTHORITY,
            }
        )
    return creation_rows


def _generated_mount_candidate_record(
    root: Path,
    *,
    rows: Sequence[Mapping[str, Any]],
    role_id: str,
    domain_id: str,
) -> dict[str, Any]:
    from kernel.ion_codex_agent_mount import build_codex_agent_mount_candidate

    first = rows[0] if rows else {}
    assigned = _mapping(first.get("assigned_identity"))
    callsign = str(assigned.get("callsign") or role_id.removeprefix("role.").upper())
    lane_ids = sorted(
        {
            str(_mapping(row.get("assigned_identity")).get("lane_id") or "").strip()
            for row in rows
            if str(_mapping(row.get("assigned_identity")).get("lane_id") or "").strip()
        }
    )
    source_request_ids = [str(row.get("source_request_id") or "") for row in rows]
    context_paths = [
        DOMAIN_CAPSULE_PATH.as_posix(),
        (DEFAULT_QUEUE_GOVERNANCE_DIR / DEFAULT_QUEUE_METADATA_IDENTITY_ASSIGNMENT_NAME).as_posix(),
        (DEFAULT_QUEUE_GOVERNANCE_DIR / DEFAULT_GENERATED_MOUNT_CREATION_NAME).as_posix(),
        (DEFAULT_QUEUE_GOVERNANCE_DIR / DEFAULT_STALE_WAITING_RECONCILIATION_REVIEW_NAME).as_posix(),
        (DEFAULT_QUEUE_GOVERNANCE_DIR / DEFAULT_CONTEXT_GATE_BLOCKED_REQUEST_REISSUE_NAME).as_posix(),
    ]
    agent = {
        "role_id": role_id,
        "agent_id": role_id,
        "display_name": callsign,
        "registry_primary_domain": domain_id,
        "primary_domain": domain_id,
        "registry_secondary_domains": [],
        "lane_id": lane_ids[0] if lane_ids else None,
        "lane_ids": lane_ids,
        "lane_metadata": [
            {
                "lane_id": lane_id,
                "source": "domain_weaver_metadata_assignment",
            }
            for lane_id in lane_ids
        ],
        "context_paths": context_paths,
        "context_system_card": "",
        "package_strategy": "generated_from_domain_weaver_metadata_assignment",
        "default_active_package_class": "generated_mount_metadata_reissue_candidate",
        "write_posture": "candidate_proposal_and_return_artifacts_only",
        "mount_source_policy": "generated from Domain Weaver metadata-assignment candidate rows; not registry-backed accepted truth",
        "invocable": True,
        "available_for_comms": True,
        "source_request_ids": source_request_ids,
        "authority": {
            "candidate_mount_only": True,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
    }
    domain = {
        "domain_id": domain_id,
        "purpose": f"Generated Domain Weaver metadata-reissue mount for {role_id}",
        "lane_id": lane_ids[0] if lane_ids else None,
        "lane_ids": lane_ids,
        "lane_metadata": [
            {
                "lane_id": lane_id,
                "source": "domain_weaver_metadata_assignment",
            }
            for lane_id in lane_ids
        ],
        "fact_posture": "candidate",
        "maturity_estimate": "generated_mount_bootstrap",
        "suggested_steward_class": callsign,
        "mount_source_policy": "generated from Domain Weaver metadata-assignment candidate rows; not registry-backed accepted truth",
        "paths": context_paths,
        "source_request_ids": source_request_ids,
        "authority": {
            "candidate_mount_only": True,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
    }
    mount = build_codex_agent_mount_candidate(root, agent, domain)
    return {"agent": agent, "domain": domain, "mount": mount}


def _generated_mount_required_files(mount_path: str) -> list[str]:
    required_suffixes = [
        "ION_AGENT_MOUNT_MANIFEST.json",
        "AGENTS.md",
        "AGENT_SYSTEM_CARD.md",
        "DOMAIN_SYSTEM_CARD.md",
        "ACTIVE_CONTEXT_PACKAGE.json",
        "ACTIVE_CONTEXT_PACKAGE.md",
        ".codex/config.toml",
        ".ion/ION_CONTEXT_CAPSULE.yaml",
        ".ion/MINI.md",
        ".ion/CAPSULE.md",
        ".ion/LONG_HORIZON.json",
        ".ion/ROUTE.json",
        ".ion/AGENT.yaml",
        ".ion/DOMAIN.yaml",
        ".ion/RELATIONSHIPS.yaml",
        ".ion/COMMUNICATIONS.json",
        ".ion/ADDRESS_BOOK.json",
        ".ion/ACTIVE_CONTEXT_PACKAGE.json",
        ".ion/ACTIVE_CONTEXT_PACKAGE.md",
    ]
    return [f"{mount_path}/{suffix}" for suffix in required_suffixes if mount_path]


def _materialize_generated_mount_creation_rows(
    root: Path,
    *,
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Mapping[str, Any]]:
    from kernel.ion_codex_agent_mount import materialize_codex_agent_mount

    materialized: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        mount_id = str(row.get("mount_id") or "")
        if not mount_id:
            continue
        manifest_ref = _mapping(row.get("preexisting_manifest_ref"))
        if manifest_ref.get("exists"):
            existing_manifest = _read_json(root / str(row.get("mount_path") or "") / "ION_AGENT_MOUNT_MANIFEST.json")
            if (
                existing_manifest.get("mount_id") != mount_id
                or existing_manifest.get("domain_id") != row.get("domain_id")
                or existing_manifest.get("agent_role_id") != row.get("role_id")
            ):
                continue
        agent = _mapping(row.get("agent_record"))
        domain = _mapping(row.get("domain_record"))
        materialized[mount_id] = materialize_codex_agent_mount(root, agent, domain)
    return materialized


def _generated_mount_creation_next_packets(
    *,
    ready_count: int,
    assignment_summary: Mapping[str, Any],
) -> list[dict[str, Any]]:
    packets: list[dict[str, Any]] = []
    if ready_count:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-QUEUE-METADATA-IDENTITY-ASSIGNMENT-REFRESH-AFTER-GENERATED-MOUNTS-V0_1",
                "purpose": "refresh metadata identity assignment so newly materialized mounts can become existing-mount rows",
                "authority": "candidate_assignment_refresh_only_no_queue_start",
                "row_count": ready_count,
            }
        )
    source_safety_count = int(assignment_summary.get("source_safety_blocked_count") or 0)
    quarantine_count = int(
        assignment_summary.get("supersede_or_quarantine_recommended_count") or 0
    )
    if source_safety_count:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-SOURCE-SAFETY-BLOCKED-METADATA-REISSUE-REVIEW-V0_1",
                "purpose": "continue source-safety blocker handling before apply review",
                "authority": "candidate_review_only_no_request_file_mutation",
                "row_count": source_safety_count,
            }
        )
    if quarantine_count:
        packets.append(
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-STALE-NON-DOMAIN-QUEUE-QUARANTINE-REVIEW-V0_1",
                "purpose": "decide whether stale non-Domain-Weaver rows should be superseded, quarantined, or explicitly preserved",
                "authority": "candidate_lifecycle_review_only_no_ledger_write",
                "row_count": quarantine_count,
            }
        )
    return packets


def _generated_mount_creation_graph_deltas(
    root: Path,
    *,
    generated_at: str,
    creation_rows: Sequence[Mapping[str, Any]],
    source_assignment_ref: Mapping[str, Any],
) -> dict[str, Any]:
    claims: list[dict[str, Any]] = [
        {
            "id": "domain_weaver.generated_mount_creation_for_metadata_reissue",
            "kind": "generated_mount_creation_for_metadata_reissue",
            "state": "mounts_materialized"
            if any(row.get("materialized_by_this_packet") for row in creation_rows)
            else "ready",
            "evidence": [
                str(source_assignment_ref.get("path") or ""),
                "ION/05_context/current/codex_agent_mounts",
            ],
            "value": {
                "unique_mount_candidate_count": len(creation_rows),
                "mounts_materialized": sum(
                    1 for row in creation_rows if row.get("materialized_by_this_packet")
                ),
                "request_files_mutated": False,
                "replacement_request_files_written": 0,
                "codex_queue_run_started": False,
            },
        }
    ]
    claims.extend(
        {
            "id": f"domain_weaver.generated_mount_creation_for_metadata_reissue.{row.get('mount_id')}",
            "kind": "generated_codex_agent_mount",
            "state": "materialized"
            if _mapping(row.get("post_manifest_ref")).get("exists")
            else "planned",
            "evidence": [
                str(row.get("mount_path") or ""),
                str(source_assignment_ref.get("path") or ""),
            ],
            "value": {
                "domain_id": row.get("domain_id"),
                "role_id": row.get("role_id"),
                "source_request_ids": list(row.get("source_request_ids") or []),
                "materialized_by_this_packet": bool(row.get("materialized_by_this_packet")),
                "missing_required_files": list(row.get("missing_required_files") or []),
            },
        }
        for row in creation_rows
    )
    return {
        "schema_id": GENERATED_MOUNT_CREATION_DELTA_SCHEMA_ID,
        "generated_at": generated_at,
        "active_root": str(root),
        "status": "candidate_generated_mount_creation_deltas_built",
        "upsert_claims": claims,
        "write_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _discover_exact_reissue_request_paths(root: Path) -> list[str]:
    work_request_dir = root / CODEX_WORK_REQUESTS_DIR
    paths = [
        *work_request_dir.glob("codex_req_context_gate_reissue_*.json"),
        *work_request_dir.glob("codex_req_metadata_identity_reissue_*.json"),
    ]
    selected: list[str] = []
    for path in sorted(paths):
        payload = _read_json(path)
        if payload.get("status") != "QUEUED_FOR_CODEX_CARRIER":
            continue
        selected.append(_rel(root, path))
    return selected


def _exact_reissue_request_readiness_row(
    root: Path,
    request_path: str,
    *,
    timeout_seconds: int,
) -> dict[str, Any]:
    rel_path = _root_relative_path(root, request_path)
    path = root / rel_path
    payload = _read_json(path)
    request_ref = _file_ref(root, path)
    blockers: list[str] = []
    if not rel_path.startswith(CODEX_WORK_REQUESTS_DIR.as_posix() + "/"):
        blockers.append("request_path_not_under_codex_work_requests")
    if not path.is_file():
        blockers.append("request_file_missing")
    if not payload:
        blockers.append("request_json_missing_or_invalid")
    payload_path = str(payload.get("path") or "")
    if payload_path and payload_path != rel_path:
        blockers.append("request_payload_path_mismatch")
    if payload.get("status") != "QUEUED_FOR_CODEX_CARRIER":
        blockers.append("request_status_not_queued_for_codex_carrier")
    if payload.get("exact_request_path_required") is not True:
        blockers.append("exact_request_path_required_not_true")
    if payload.get("general_queue_processing_allowed") is not False:
        blockers.append("general_queue_processing_not_explicitly_false")

    request_class, reissue_body = _exact_reissue_request_class(payload)
    if request_class == "unknown":
        blockers.append("request_is_not_context_or_metadata_reissue")
    if request_class == "ambiguous":
        blockers.append("request_has_multiple_reissue_bodies")

    assignment = _mapping(reissue_body.get("assignment"))
    working_capsule = _mapping(payload.get("working_capsule_identity"))
    working_authority = _mapping(working_capsule.get("authority"))
    domain_id = str(payload.get("domain_id") or assignment.get("domain_id") or "")
    lane_id = str(payload.get("lane_id") or assignment.get("lane_id") or "")
    role_id = str(payload.get("role_id") or assignment.get("role_id") or "")
    callsign = str(payload.get("callsign") or assignment.get("callsign") or "")
    if not domain_id:
        blockers.append("domain_id_missing")
    if not lane_id:
        blockers.append("lane_id_missing")
    if not role_id:
        blockers.append("role_id_missing")
    if not callsign:
        blockers.append("callsign_missing")

    selected_mount_path = _selected_mount_path(
        root,
        assignment=assignment,
        working_capsule=working_capsule,
        role_id=role_id,
        domain_id=domain_id,
    )
    active_context_package_path = str(
        assignment.get("active_context_package_path")
        or (
            f"{selected_mount_path}/.ion/ACTIVE_CONTEXT_PACKAGE.md"
            if selected_mount_path
            else ""
        )
    )
    mount_ref = (
        _evidence_ref(root, selected_mount_path)
        if selected_mount_path
        else {"path": "", "exists": False, "required": True, "kind": "missing"}
    )
    active_context_ref = (
        _file_ref(root, root / active_context_package_path)
        if active_context_package_path
        else {"path": "", "exists": False, "required": True}
    )
    if not selected_mount_path:
        blockers.append("selected_mount_path_missing")
    elif not str(selected_mount_path).startswith(
        "ION/05_context/current/codex_agent_mounts/"
    ):
        blockers.append("selected_mount_path_not_codex_agent_mount")
    elif not (root / selected_mount_path).is_dir():
        blockers.append("selected_mount_missing")
    if not active_context_package_path:
        blockers.append("active_context_package_path_missing")
    elif not (root / active_context_package_path).is_file():
        blockers.append("active_context_package_missing")

    if not working_capsule:
        blockers.append("working_capsule_identity_missing")
    if working_capsule.get("domain_id") and working_capsule.get("domain_id") != domain_id:
        blockers.append("working_capsule_domain_mismatch")
    if working_capsule.get("role_id") and working_capsule.get("role_id") != role_id:
        blockers.append("working_capsule_role_mismatch")
    wc_root = str(working_capsule.get("root") or "")
    if wc_root and Path(wc_root).resolve(strict=False) != root.resolve(strict=False):
        blockers.append("working_capsule_root_mismatch")
    wc_mount_rel = _root_relative_path(root, str(working_capsule.get("codex_agent_mount") or ""))
    if wc_mount_rel and selected_mount_path and wc_mount_rel != selected_mount_path:
        blockers.append("working_capsule_mount_mismatch")
    wc_capsule_path = _root_relative_path(
        root,
        str(working_capsule.get("working_capsule_path") or ""),
    )
    wc_capsule_ref = (
        _evidence_ref(root, wc_capsule_path)
        if wc_capsule_path
        else {"path": "", "exists": False, "required": True, "kind": "missing"}
    )
    if wc_capsule_path and not (root / wc_capsule_path).is_dir():
        blockers.append("working_capsule_path_missing")
    for authority_key in (
        "production_authority",
        "live_execution_authority",
        "accepted_state_authority",
        "secrets_authority",
    ):
        if payload.get(authority_key) is not False:
            blockers.append(f"{authority_key}_not_false")
        if working_authority and working_authority.get(authority_key) is not False:
            blockers.append(f"working_capsule_{authority_key}_not_false")

    source_request_id = str(reissue_body.get("source_request_id") or "")
    source_request_path = str(reissue_body.get("source_request_path") or "")
    source_expected_sha = str(reissue_body.get("source_request_sha256") or "")
    source_ref = (
        _file_ref(root, root / source_request_path)
        if source_request_path
        else {"path": "", "exists": False, "required": True}
    )
    current_source_sha = (
        _sha256_file(root / source_request_path)
        if source_request_path and (root / source_request_path).is_file()
        else ""
    )
    if not source_request_id:
        blockers.append("source_request_id_missing")
    if not source_request_path:
        blockers.append("source_request_path_missing")
    elif not (root / source_request_path).is_file():
        blockers.append("source_request_file_missing")
    if not source_expected_sha:
        blockers.append("source_request_sha256_missing")
    elif current_source_sha != source_expected_sha:
        blockers.append("source_request_sha256_mismatch")

    replacement_request_id = str(
        reissue_body.get("replacement_request_id") or payload.get("request_id") or ""
    )
    replacement_request_path = str(
        reissue_body.get("replacement_request_path") or payload_path or rel_path
    )
    if replacement_request_id and replacement_request_id != str(payload.get("request_id") or ""):
        blockers.append("replacement_request_id_mismatch")
    if replacement_request_path and replacement_request_path != rel_path:
        blockers.append("replacement_request_path_mismatch")

    lifecycle_preview_rows = _request_lifecycle_preview_rows(payload, reissue_body)
    if any(_unlabeled_stale_lifecycle_preview_metadata(row) for row in lifecycle_preview_rows):
        blockers.append("unlabeled_stale_lifecycle_preview_metadata")
    labeled_lifecycle_preview_rows = [
        _label_stale_lifecycle_preview_metadata(row) for row in lifecycle_preview_rows
    ]

    dispatch_ready = not blockers
    return {
        "schema_id": "ion.domain_weaver.exact_reissue_request_dispatch_readiness_row.v0_1_candidate",
        "row_kind": "exact_reissue_request_dispatch_readiness",
        "request_path": rel_path,
        "request_ref": request_ref,
        "request_id": payload.get("request_id"),
        "request_kind": payload.get("request_kind"),
        "request_class": request_class,
        "request_status": payload.get("status"),
        "active_context_check_status": payload.get("active_context_check_status"),
        "domain_id": domain_id,
        "lane_id": lane_id,
        "role_id": role_id,
        "callsign": callsign,
        "selected_mount_path": selected_mount_path,
        "selected_mount_ref": mount_ref,
        "active_context_package_path": active_context_package_path,
        "active_context_package_ref": active_context_ref,
        "working_capsule_identity": dict(working_capsule),
        "working_capsule_path": wc_capsule_path,
        "working_capsule_ref": wc_capsule_ref,
        "source_request_id": source_request_id,
        "source_request_path": source_request_path,
        "source_request_ref": source_ref,
        "source_request_sha256": source_expected_sha,
        "current_source_request_sha256": current_source_sha,
        "source_hash_matches": bool(
            source_expected_sha and current_source_sha == source_expected_sha
        ),
        "replacement_request_id": replacement_request_id,
        "replacement_request_path": replacement_request_path,
        "lifecycle_preview_metadata_rows": labeled_lifecycle_preview_rows,
        "exact_request_path_required": payload.get("exact_request_path_required"),
        "general_queue_processing_allowed": payload.get("general_queue_processing_allowed"),
        "dispatch_ready": dispatch_ready,
        "dispatch_blockers": blockers,
        "start_command": _exact_reissue_start_command(
            rel_path,
            timeout_seconds=timeout_seconds,
        )
        if dispatch_ready
        else None,
        "expected_return_posture": {
            "worker_return_is_carrier_intake_only": True,
            "requires_task_return_receipt": True,
            "requires_fanin_settlement": True,
            "accepted_state_claimed": False,
        },
        "codex_queue_run_started": False,
        "actual_spawn_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _exact_reissue_request_class(
    payload: Mapping[str, Any],
) -> tuple[str, Mapping[str, Any]]:
    has_context = isinstance(payload.get("context_gate_reissue"), Mapping)
    has_metadata = isinstance(payload.get("metadata_identity_reissue"), Mapping)
    if has_context and has_metadata:
        return "ambiguous", {}
    if has_context:
        return "context_gate_reissue", _mapping(payload.get("context_gate_reissue"))
    if has_metadata:
        return "metadata_identity_reissue", _mapping(payload.get("metadata_identity_reissue"))
    return "unknown", {}


def _selected_mount_path(
    root: Path,
    *,
    assignment: Mapping[str, Any],
    working_capsule: Mapping[str, Any],
    role_id: str,
    domain_id: str,
) -> str:
    selected = str(assignment.get("selected_mount_path") or "")
    if selected:
        return _root_relative_path(root, selected)
    capsule_mount = str(working_capsule.get("codex_agent_mount") or "")
    if capsule_mount:
        return _root_relative_path(root, capsule_mount)
    if role_id and domain_id:
        return (
            "ION/05_context/current/codex_agent_mounts/"
            f"{role_id.replace('.', '_')}__{domain_id.replace('.', '_')}"
        )
    return ""


def _root_relative_path(root: Path, value: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    path = Path(text)
    if path.is_absolute():
        return _rel(root, path)
    return path.as_posix()


def _exact_reissue_runtime_status(
    root: Path,
    *,
    generated_at: str,
    max_runtime_status_age_seconds: int,
    source_runtime_status: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    state_path = root / QUEUE_RUNNER_STATE_PATH
    state = _read_json(state_path)
    ref = _file_ref(root, state_path, required=False)
    provided_status = dict(source_runtime_status or {})
    if provided_status:
        concurrency = _mapping(provided_status.get("concurrency"))
        lane_locks = _mapping(provided_status.get("active_lane_locks"))
        active_run_count = int(
            provided_status.get("active_run_count")
            or concurrency.get("active_run_count")
            or lane_locks.get("active_run_count")
            or 0
        )
        active_lane_count = int(
            concurrency.get("active_lane_count")
            or lane_locks.get("active_lane_count")
            or 0
        )
        global_active_lock = bool(concurrency.get("global_active_lock"))
        unknown_lane_active_run_count = int(
            concurrency.get("unknown_lane_active_run_count")
            or lane_locks.get("unknown_lane_active_run_count")
            or 0
        )
        active_clear = bool(
            active_run_count == 0
            and active_lane_count == 0
            and unknown_lane_active_run_count == 0
            and not global_active_lock
            and not bool(provided_status.get("active_process_running"))
            and not list(provided_status.get("active_runs") or [])
        )
        verdict_ready = provided_status.get("verdict") == "ION_CODEX_QUEUE_RUNNER_READY"
        return {
            "schema_id": "ion.domain_weaver.exact_reissue_runtime_status_ref.v0_1_candidate",
            "source": "provided_read_only_status_snapshot",
            "state_path": QUEUE_RUNNER_STATE_PATH.as_posix(),
            "state_ref": ref,
            "updated_at": provided_status.get("updated_at") or generated_at,
            "generated_at": generated_at,
            "max_runtime_status_age_seconds": max_runtime_status_age_seconds,
            "age_seconds": 0,
            "runtime_status_fresh_enough": bool(verdict_ready and active_clear),
            "runtime_active_clear": active_clear,
            "active_run_count": active_run_count,
            "active_lane_count": active_lane_count,
            "unknown_lane_active_run_count": unknown_lane_active_run_count,
            "global_active_lock": global_active_lock,
            "active_lane_ids": list(concurrency.get("active_lane_ids") or []),
            "status_command_required_before_start": False,
            "provided_status_verdict": provided_status.get("verdict"),
            "provided_status_sha256": _sha256_text(_stable_json(provided_status)),
            "provided_status_summary": {
                "verdict": provided_status.get("verdict"),
                "active_process_running": provided_status.get("active_process_running"),
                "active_run_count": active_run_count,
                "queued_request_count": provided_status.get("queued_request_count"),
                "runner_state_path": provided_status.get("runner_state_path"),
                "manual_proceed_relay_required": provided_status.get(
                    "manual_proceed_relay_required"
                ),
            },
            "codex_queue_run_started": False,
            "accepted_state_claimed": False,
        }
    updated_at = str(state.get("updated_at") or "")
    age_seconds: int | None = None
    fresh_enough = False
    if updated_at:
        generated_dt = _parse_iso(generated_at)
        updated_dt = _parse_iso(updated_at)
        age_seconds = max(0, int((generated_dt - updated_dt).total_seconds()))
        fresh_enough = age_seconds <= max(0, int(max_runtime_status_age_seconds))
    concurrency = _mapping(state.get("concurrency"))
    active_run_count = int(concurrency.get("active_run_count") or 0)
    active_lane_count = int(concurrency.get("active_lane_count") or 0)
    global_active_lock = bool(concurrency.get("global_active_lock"))
    unknown_lane_active_run_count = int(
        concurrency.get("unknown_lane_active_run_count") or 0
    )
    active_clear = bool(
        state_path.is_file()
        and state.get("active_run") is None
        and not _mapping(state.get("active_runs"))
        and active_run_count == 0
        and active_lane_count == 0
        and unknown_lane_active_run_count == 0
        and not global_active_lock
    )
    return {
        "schema_id": "ion.domain_weaver.exact_reissue_runtime_status_ref.v0_1_candidate",
        "state_path": QUEUE_RUNNER_STATE_PATH.as_posix(),
        "state_ref": ref,
        "updated_at": updated_at or None,
        "generated_at": generated_at,
        "max_runtime_status_age_seconds": max_runtime_status_age_seconds,
        "age_seconds": age_seconds,
        "runtime_status_fresh_enough": fresh_enough,
        "runtime_active_clear": active_clear,
        "active_run_count": active_run_count,
        "active_lane_count": active_lane_count,
        "unknown_lane_active_run_count": unknown_lane_active_run_count,
        "global_active_lock": global_active_lock,
        "active_lane_ids": list(concurrency.get("active_lane_ids") or []),
        "status_command_required_before_start": not fresh_enough,
        "codex_queue_run_started": False,
        "accepted_state_claimed": False,
    }


def _exact_reissue_dispatch_groups(
    rows: Sequence[Mapping[str, Any]],
    *,
    max_parallel_lanes: int,
) -> list[dict[str, Any]]:
    lane_order = {
        "context_lane": 0,
        "audit_lane": 1,
        "architecture_lane": 2,
        "implementation_lane": 3,
        "settlement_lane": 4,
    }
    class_order = {
        "context_gate_reissue": 0,
        "metadata_identity_reissue": 1,
    }
    remaining = sorted(
        [row for row in rows if row.get("dispatch_ready")],
        key=lambda row: (
            class_order.get(str(row.get("request_class") or ""), 99),
            lane_order.get(str(row.get("lane_id") or ""), 99),
            str(row.get("role_id") or ""),
            str(row.get("request_id") or ""),
        ),
    )
    groups: list[dict[str, Any]] = []
    cap = max(1, int(max_parallel_lanes))
    wave_index = 1
    while remaining:
        used_lanes: set[str] = set()
        selected: list[Mapping[str, Any]] = []
        next_remaining: list[Mapping[str, Any]] = []
        for row in remaining:
            lane_id = str(row.get("lane_id") or "")
            if lane_id and lane_id not in used_lanes and len(used_lanes) < cap:
                selected.append(row)
                used_lanes.add(lane_id)
            else:
                next_remaining.append(row)
        if not selected:
            selected = [next_remaining.pop(0)]
        groups.append(
            {
                "schema_id": "ion.domain_weaver.exact_reissue_dispatch_group.v0_1_candidate",
                "wave_index": wave_index,
                "lane_ids": [str(row.get("lane_id") or "") for row in selected],
                "request_ids": [str(row.get("request_id") or "") for row in selected],
                "request_paths": [str(row.get("request_path") or "") for row in selected],
                "start_commands": [
                    str(row.get("start_command") or "")
                    for row in selected
                    if row.get("start_command")
                ],
                "same_lane_parallelism": 1,
                "codex_queue_run_started": False,
                "accepted_state_claimed": False,
            }
        )
        remaining = next_remaining
        wave_index += 1
    return groups


def _exact_reissue_start_command(path: str, *, timeout_seconds: int) -> str:
    return (
        "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ION/04_packages "
        "python3 -S -m kernel.ion_codex_queue_runner --ion-root . "
        "--process-once --start "
        f"--timeout-seconds {int(timeout_seconds)} "
        f"--request-path '{path}' --json"
    )


def _exact_reissue_status_command() -> str:
    return (
        "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ION/04_packages "
        "python3 -S -m kernel.ion_codex_queue_runner --ion-root . --status --json"
    )


def _exact_reissue_request_dispatch_next_packets(
    *,
    rows: Sequence[Mapping[str, Any]],
    blocked_rows: Sequence[Mapping[str, Any]],
    runtime_status: Mapping[str, Any],
    ready_for_immediate_exact_start: bool,
) -> list[dict[str, Any]]:
    if not rows:
        return [
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-QUEUE-METADATA-IDENTITY-REISSUE-APPLY-V0_1",
                "purpose": "write exact context/metadata reissue requests before dispatch readiness",
                "authority": "bounded_exact_request_write_only_no_queue_start",
                "row_count": 0,
            }
        ]
    if blocked_rows:
        return [
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-EXACT-REISSUE-REQUEST-DISPATCH-PRECHECK-REPAIR-V0_1",
                "purpose": "repair blocked exact reissue request identity, mount, source-hash, or exact-path gates before any worker start",
                "authority": "candidate_precheck_repair_only_no_queue_start",
                "row_count": len(blocked_rows),
            }
        ]
    if not runtime_status.get("runtime_status_fresh_enough"):
        return [
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-EXACT-REISSUE-RUNTIME-STATUS-REFRESH-V0_1",
                "purpose": "run read-only queue-runner status before starting exact request paths",
                "authority": "read_only_runtime_status_no_worker_start",
                "row_count": len(rows),
            },
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-EXACT-REISSUE-REQUEST-DISPATCH-WAVE-V0_1",
                "purpose": "start validated exact request paths in staged lane waves after fresh status proof",
                "authority": "bounded_exact_request_path_start_only_no_general_queue",
                "row_count": len(rows),
            },
        ]
    if not runtime_status.get("runtime_active_clear"):
        return [
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-EXACT-REISSUE-ACTIVE-RUN-FANIN-WAIT-V0_1",
                "purpose": "wait for current active runs to settle before exact reissue dispatch",
                "authority": "fanin_wait_only_no_new_start",
                "row_count": len(rows),
            }
        ]
    if ready_for_immediate_exact_start:
        return [
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-EXACT-REISSUE-REQUEST-DISPATCH-WAVE-V0_1",
                "purpose": "start validated exact request paths in staged lane waves",
                "authority": "bounded_exact_request_path_start_only_no_general_queue",
                "row_count": len(rows),
            },
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-EXACT-REISSUE-REQUEST-DISPATCH-FANIN-V0_1",
                "purpose": "collect task returns, native receipts, and Nemesis dissent after exact reissue workers finish",
                "authority": "carrier_intake_fanin_only_no_accepted_state",
                "row_count": len(rows),
            },
        ]
    return []


def _exact_reissue_request_dispatch_graph_deltas(
    root: Path,
    *,
    generated_at: str,
    rows: Sequence[Mapping[str, Any]],
    runtime_status: Mapping[str, Any],
    verdict: str,
) -> dict[str, Any]:
    claims: list[dict[str, Any]] = [
        {
            "id": "domain_weaver.exact_reissue_request_dispatch_readiness",
            "kind": "exact_reissue_request_dispatch_readiness",
            "state": verdict,
            "evidence": [
                CODEX_WORK_REQUESTS_DIR.as_posix(),
                QUEUE_RUNNER_STATE_PATH.as_posix(),
            ],
            "value": {
                "row_count": len(rows),
                "dispatch_ready_count": sum(1 for row in rows if row.get("dispatch_ready")),
                "runtime_status_fresh_enough": bool(
                    runtime_status.get("runtime_status_fresh_enough")
                ),
                "runtime_active_clear": bool(runtime_status.get("runtime_active_clear")),
                "codex_queue_run_started": False,
                "accepted_state_claimed": False,
            },
        }
    ]
    for row in rows:
        claims.append(
            {
                "id": f"domain_weaver.exact_reissue_request_dispatch_readiness.{row.get('request_id')}",
                "kind": "exact_reissue_request_dispatch_readiness_row",
                "state": "dispatch_ready" if row.get("dispatch_ready") else "blocked",
                "evidence": [
                    str(row.get("request_path") or ""),
                    str(row.get("selected_mount_path") or ""),
                    str(row.get("source_request_path") or ""),
                ],
                "value": {
                    "request_class": row.get("request_class"),
                    "lane_id": row.get("lane_id"),
                    "role_id": row.get("role_id"),
                    "source_hash_matches": bool(row.get("source_hash_matches")),
                    "dispatch_blockers": list(row.get("dispatch_blockers") or []),
                    "codex_queue_run_started": False,
                    "accepted_state_claimed": False,
                },
            }
        )
    return {
        "schema_id": EXACT_REISSUE_REQUEST_DISPATCH_READINESS_DELTA_SCHEMA_ID,
        "generated_at": generated_at,
        "active_root": str(root),
        "status": "candidate_exact_reissue_request_dispatch_readiness_deltas_built",
        "upsert_claims": claims,
        "write_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _queue_lifecycle_preview_rows(governance: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in list(governance.get("ledger_candidate_rows") or []):
        if not isinstance(row, Mapping):
            continue
        if not (row.get("stale") or row.get("terminal_repair_needed")):
            continue
        repair_class = (
            "terminal_lifecycle_classification_required"
            if row.get("terminal_repair_needed")
            else "stale_waiting_reconciliation_required"
        )
        preview_row = {
                "schema_id": "ion.domain_weaver.global_queue_lifecycle_preview_row.v0_1_candidate",
                "row_kind": "queue_lifecycle_preview_not_applied",
                "request_id": row.get("request_id"),
                "source_path": row.get("source_path"),
                "status": row.get("status"),
                "lane_id": row.get("lane_id"),
                "classification": row.get("classification"),
                "repair_class": repair_class,
                "recommended_action": (
                    "classify terminal evidence and emit a lifecycle repair packet"
                    if row.get("terminal_repair_needed")
                    else "digest, supersede, or explicitly preserve stale waiting row"
                ),
                "recommended_lifecycle_disposition": row.get("recommended_lifecycle_disposition"),
                "stale": bool(row.get("stale")),
                "terminal_repair_needed": bool(row.get("terminal_repair_needed")),
                "would_write_lifecycle_ledger": False,
                "would_mutate_request_file": False,
                "would_refresh_projection": False,
                "accepted_state_claimed": False,
                "authority": AUTHORITY,
            }
        preview_row.update(_stale_lifecycle_preview_metadata_label(preview_row))
        rows.append(preview_row)
    return rows


def _queue_repair_class(row: Mapping[str, Any], blockers: Sequence[str]) -> str:
    blocker_set = set(blockers)
    status = str(row.get("status") or "")
    if {
        "queueable_request_missing_domain_id",
        "queueable_request_missing_lane_id",
    } & blocker_set:
        return "metadata_identity_reissue_required"
    if status == "CODEX_QUEUE_RUNNER_BLOCKED_CONTEXT_GATE" or "request_previously_blocked_by_context_gate" in blocker_set:
        return "context_gate_reissue_required"
    if any("working_capsule" in blocker for blocker in blocker_set):
        return "working_capsule_identity_reissue_required"
    if not row.get("active_context_ready"):
        return "active_context_reissue_required"
    return "blocked_queueable_request_review_required"


def _queue_repair_packet_id(repair_class: str) -> str:
    return {
        "metadata_identity_reissue_required": "PCKT-DOMAIN-WEAVER-QUEUE-REQUEST-METADATA-IDENTITY-REISSUE-V0_1",
        "context_gate_reissue_required": "PCKT-DOMAIN-WEAVER-CONTEXT-GATE-BLOCKED-REQUEST-REISSUE-V0_1",
        "working_capsule_identity_reissue_required": "PCKT-DOMAIN-WEAVER-WORKING-CAPSULE-IDENTITY-REISSUE-V0_2",
        "active_context_reissue_required": "PCKT-DOMAIN-WEAVER-ACTIVE-CONTEXT-GATED-REFRESH-OR-REISSUE-V0_2",
    }.get(repair_class, "PCKT-DOMAIN-WEAVER-BLOCKED-QUEUEABLE-REQUEST-REVIEW-V0_1")


def _queue_repair_action(repair_class: str) -> str:
    return {
        "metadata_identity_reissue_required": "reissue request with explicit domain_id, lane_id, role/callsign, and working capsule identity",
        "context_gate_reissue_required": "refresh active context evidence or supersede with a new exact request after context gate proof",
        "working_capsule_identity_reissue_required": "bind request to a unique folder-local codex agent mount before worker start",
        "active_context_reissue_required": "reissue or refresh active context package for the selected role/domain/lane",
    }.get(repair_class, "review blocked queueable request before any start")


def _candidate_reissue_fields(row: Mapping[str, Any], blockers: Sequence[str]) -> dict[str, Any]:
    missing_fields: list[str] = []
    if "queueable_request_missing_domain_id" in blockers:
        missing_fields.append("domain_id")
    if "queueable_request_missing_lane_id" in blockers:
        missing_fields.append("lane_id")
    if any("working_capsule" in blocker for blocker in blockers):
        missing_fields.append("working_capsule_identity")
    if not row.get("active_context_ready"):
        missing_fields.append("fresh_active_context_package")
    return {
        "preserve_if_trusted": {
            "lane_id": row.get("lane_id") or None,
            "domain_id": row.get("domain_id") or None,
            "role_id": row.get("role_id") or None,
            "role_tier": row.get("role_tier") or None,
            "callsign": row.get("callsign") or None,
            "work_class": row.get("work_class") or None,
            "request_kind": row.get("request_kind") or None,
            "selected_mount_id": row.get("selected_mount_id") or row.get("requested_selected_mount_id"),
            "selected_mount_path": row.get("selected_mount_path") or row.get("requested_selected_mount_path"),
        },
        "missing_or_untrusted_fields": list(dict.fromkeys(missing_fields)),
        "identity_inference_allowed": False,
        "requires_exact_new_request_path": True,
    }


def _repair_preview_next_packets(
    *,
    repair_rows: Sequence[Mapping[str, Any]],
    lifecycle_rows: Sequence[Mapping[str, Any]],
    hygiene: Mapping[str, Any],
) -> list[dict[str, Any]]:
    packet_by_id: dict[str, dict[str, Any]] = {}
    for row in repair_rows:
        packet_id = str(row.get("repair_packet_id") or "")
        if not packet_id:
            continue
        packet_by_id.setdefault(
            packet_id,
            {
                "packet_id": packet_id,
                "purpose": str(row.get("recommended_action") or "repair blocked queueable request"),
                "authority": "candidate_preview_only_no_request_file_mutation",
            },
        )
    if lifecycle_rows:
        packet_by_id.setdefault(
            "PCKT-DOMAIN-WEAVER-QUEUE-LIFECYCLE-PREVIEW-SETTLEMENT-V0_1",
            {
                "packet_id": "PCKT-DOMAIN-WEAVER-QUEUE-LIFECYCLE-PREVIEW-SETTLEMENT-V0_1",
                "purpose": "settle stale and terminal lifecycle preview rows behind explicit mutation gates",
                "authority": "candidate_lifecycle_preview_only",
            },
        )
    if hygiene.get("next_packet"):
        packet_by_id.setdefault(
            str(hygiene.get("next_packet")),
            {
                "packet_id": hygiene.get("next_packet"),
                "purpose": "continue from source queue hygiene packet",
                "authority": "candidate_only_no_queue_start",
            },
        )
    return list(packet_by_id.values())


def _global_queue_repair_preview_graph_deltas(
    root: Path,
    *,
    generated_at: str,
    repair_rows: Sequence[Mapping[str, Any]],
    lifecycle_rows: Sequence[Mapping[str, Any]],
    hygiene: Mapping[str, Any],
) -> dict[str, Any]:
    claims: list[dict[str, Any]] = [
        {
            "id": "domain_weaver.global_queue_identity_repair_preview",
            "kind": "queue_identity_repair_preview",
            "state": "mutation_gate_required" if repair_rows or lifecycle_rows else "no_rows_required",
            "evidence": [
                DEFAULT_GLOBAL_QUEUE_HYGIENE_NAME,
                CODEX_WORK_REQUESTS_DIR.as_posix(),
            ],
            "value": {
                "queueable_repair_row_count": len(repair_rows),
                "lifecycle_preview_row_count": len(lifecycle_rows),
                "source_hygiene_verdict": hygiene.get("verdict"),
                "request_files_mutated": False,
            },
        }
    ]
    claims.extend(
        {
            "id": f"domain_weaver.queue_identity_repair.{row.get('request_id')}",
            "kind": "queueable_request_repair_preview",
            "state": row.get("repair_class"),
            "evidence": [str(row.get("request_path") or "")],
            "value": {
                "repair_packet_id": row.get("repair_packet_id"),
                "recommended_action": row.get("recommended_action"),
                "would_mutate_request_file": False,
            },
        }
        for row in repair_rows
    )
    claims.extend(
        {
            "id": f"domain_weaver.queue_lifecycle_preview.{row.get('request_id')}",
            "kind": "queue_lifecycle_preview",
            "state": row.get("repair_class"),
            "evidence": [str(row.get("source_path") or "")],
            "value": {
                "recommended_action": row.get("recommended_action"),
                "would_write_lifecycle_ledger": False,
            },
        }
        for row in lifecycle_rows[:24]
    )
    return {
        "schema_id": GLOBAL_QUEUE_REPAIR_PREVIEW_DELTA_SCHEMA_ID,
        "generated_at": generated_at,
        "active_root": str(root),
        "status": "candidate_global_queue_identity_repair_preview_deltas_built",
        "upsert_claims": claims,
        "write_performed": False,
        "accepted_state_claimed": False,
        "authority": AUTHORITY,
    }


def _fleet_lane(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        **dict(row),
        "context_package": DOMAIN_CONTEXT_PACKAGE,
        "lead_context_package": LEAD_DEV_CONTEXT_PACKAGE,
        "worker_return_is_carrier_intake_only": True,
        "candidate_only": True,
        "planned_scope": [
            "read active-root evidence",
            "write assigned candidate artifact or proposal workspace only",
            "emit receipt/proof references",
        ],
        "forbidden_actions": [
            "accepted_state_claim",
            "production_or_live_execution",
            "secrets_access",
            "raw_source_write_without_lead_apply_packet",
            "patch_apply_without_lead_apply_packet",
            "direct_nested_subagent_spawn",
            "general_queue_processing",
        ],
        "fanin_required": True,
        "actual_spawn_performed": False,
        "codex_queue_run_started": False,
    }


def _compact_pressure_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": plan.get("schema_id"),
        "status": plan.get("status"),
        "lane_count": plan.get("lane_count"),
        "caps": plan.get("caps"),
        "lane_counts": plan.get("lane_counts"),
        "blocker_count": len(plan.get("blockers") or []),
        "actual_spawn_performed": plan.get("actual_spawn_performed"),
        "codex_queue_run_started": plan.get("codex_queue_run_started"),
        "accepted_state_claimed": plan.get("accepted_state_claimed"),
    }


def _compact_proposal_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_id": plan.get("schema_id"),
        "status": plan.get("status"),
        "lane_count": plan.get("lane_count"),
        "caps": plan.get("caps"),
        "lane_counts": plan.get("lane_counts"),
        "blocker_count": len(plan.get("blockers") or []),
        "actual_spawn_performed": plan.get("actual_spawn_performed"),
        "codex_queue_run_started": plan.get("codex_queue_run_started"),
        "accepted_state_claimed": plan.get("accepted_state_claimed"),
        "product_state_accepted": plan.get("product_state_accepted"),
    }


def _require_active_root(active_root: str | Path) -> Path:
    root = Path(active_root).expanduser().resolve(strict=False)
    if not (root / "pyproject.toml").is_file():
        raise ValueError(f"active_root_missing_pyproject: {root}")
    if not (root / "ION/REPO_AUTHORITY.md").is_file():
        raise ValueError(f"active_root_missing_repo_authority: {root}")
    return root


def _active_root_proof(root: Path) -> dict[str, Any]:
    pyproject = root / "pyproject.toml"
    authority = root / "ION/REPO_AUTHORITY.md"
    return {
        "proof_ok": pyproject.is_file() and authority.is_file(),
        "pyproject": _file_ref(root, pyproject),
        "repo_authority": _file_ref(root, authority),
    }


def _evidence_ref(root: Path, value: str) -> dict[str, Any]:
    rel_path = Path(value)
    path = root / rel_path
    has_glob = any(ch in value for ch in "*?[")
    if has_glob:
        matches = sorted(root.glob(value))
        return {
            "path": value,
            "exists": bool(matches),
            "required": False,
            "kind": "glob",
            "match_count": len(matches),
            "sample_matches": [_rel(root, path) for path in matches[:8]],
        }
    if path.is_file():
        ref = _file_ref(root, path)
        ref["kind"] = "file"
        return ref
    if path.is_dir():
        return {
            "path": value,
            "exists": True,
            "required": False,
            "kind": "directory",
            "child_count": sum(1 for _ in path.iterdir()),
        }
    return {
        "path": value,
        "exists": False,
        "required": False,
        "kind": "missing",
    }


def _file_payload_ref(root: Path, value: Any, *, required: bool = True) -> dict[str, Any]:
    path_text = ""
    expected_sha = ""
    if isinstance(value, Mapping):
        path_text = str(value.get("path") or "")
        expected_sha = str(value.get("sha256") or "")
    elif isinstance(value, str):
        path_text = value
    if not path_text:
        return {"path": "", "exists": False, "required": required, "sha256_ok": False}
    path = root / path_text
    ref = _file_ref(root, path, required=required)
    if expected_sha and ref.get("sha256"):
        ref["expected_sha256"] = expected_sha
        ref["sha256_ok"] = expected_sha == ref["sha256"]
    elif expected_sha:
        ref["expected_sha256"] = expected_sha
        ref["sha256_ok"] = False
    else:
        ref["sha256_ok"] = bool(ref.get("sha256"))
    return ref


def _file_ref(root: Path, path: Path, *, required: bool = True) -> dict[str, Any]:
    ref: dict[str, Any] = {
        "path": _rel(root, path),
        "exists": path.is_file(),
        "required": required,
    }
    if path.is_file():
        ref["sha256"] = _sha256_file(path)
    return ref


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _parse_iso(value: str) -> datetime:
    text = str(value or "").strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return datetime.now(timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _stable_json(data: Mapping[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rel(root: Path, path: Path | str) -> str:
    target = Path(path)
    try:
        return target.relative_to(root).as_posix()
    except ValueError:
        return target.as_posix()


def _is_under(root: Path, path: Path, parent: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(parent.resolve(strict=False))
    except ValueError:
        return False
    return True


def _resolve_output_dir(root: Path, output_dir: str | Path | None) -> Path:
    if output_dir is None:
        return root / DEFAULT_OUTPUT_DIR
    path = Path(output_dir)
    if not path.is_absolute():
        path = root / path
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError as exc:
        raise ValueError(f"output_dir_escapes_active_root: {output_dir}") from exc
    return path


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _first_truthy(*values: Any) -> Any:
    for value in values:
        if value:
            return value
    return None


def _id_fragment(value: str, *, size: int = 16) -> str:
    text = str(value or "unknown")
    safe = "".join(ch if ch.isalnum() else "_" for ch in text).strip("_")
    if safe:
        return safe[:48]
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:size]


def _blocker(
    severity: str,
    code: str,
    detail: str,
    *,
    evidence: Sequence[str] | None = None,
) -> dict[str, Any]:
    return {
        "severity": severity,
        "code": code,
        "detail": detail,
        "evidence": list(evidence or []),
    }


def _dedupe_blockers(blockers: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for row in blockers:
        code = str(row.get("code") or "")
        if not code or code in seen:
            continue
        seen.add(code)
        deduped.append(dict(row))
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    return sorted(deduped, key=lambda item: severity_order.get(str(item.get("severity")), 9))


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _stamp_from_iso(value: str) -> str:
    text = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        parsed = datetime.now(timezone.utc)
    return parsed.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
