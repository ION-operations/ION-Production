"""Bounded Codex queue runner for ChatGPT Browser MCP work packets.

This module is a local carrier adapter over the existing ChatGPT connector
Codex work queue. It does not create a second work system and it does not expose
arbitrary shell. The only executable path is the fixed Codex CLI carrier command
for an already queued ``QUEUED_FOR_CODEX_CARRIER`` packet.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_carrier_onboard import resolve_shell_root_from_ion_root
from .ion_codex_model_moves import (
    build_codex_model_move_plan,
    codex_exec_args_from_model_move,
    summarize_model_move,
    validate_codex_model_override,
)
from .ion_agent_route_enforcement import (
    OPERATOR_ARTIFACT_HYGIENE_SECTION,
    operator_artifact_hygiene_required,
    validate_codex_route_enforcement,
)
from .ion_codex_operational_posture import (
    OPERATIONAL_POSTURE_SECTION,
    ion_operational_posture_required,
)
from .ion_agent_cwd_boundary import build_agent_cwd_boundary
from .ion_ai_movement_gate import evaluate_ai_movement_gate
from .ion_codex_agent_mount import (
    ACTIVE_CONTEXT_PACKAGE_MD as CODEX_AGENT_MOUNT_ACTIVE_CONTEXT_PACKAGE_MD,
    MOUNT_MANIFEST_NAME as CODEX_AGENT_MOUNT_MANIFEST_NAME,
    MOUNT_ROOT as CODEX_AGENT_MOUNT_ROOT,
    PORTABLE_CAPSULE as CODEX_AGENT_MOUNT_PORTABLE_CAPSULE,
    PORTABLE_CONTEXT_DIR as CODEX_AGENT_MOUNT_PORTABLE_CONTEXT_DIR,
    PORTABLE_CONTEXT_MANIFEST as CODEX_AGENT_MOUNT_PORTABLE_CONTEXT_MANIFEST,
)
from .ion_domain_weaver_context_active_resolver import resolve_domain_active_context

SCHEMA_ID = "ion.codex_queue_runner.v1"
READY_VERDICT = "ION_CODEX_QUEUE_RUNNER_READY"
BLOCKED_VERDICT = "ION_CODEX_QUEUE_RUNNER_BLOCKED"
CODEX_QUEUE_RUNNER_STOP_CONFIRMATION = "ION_STOP_CODEX_AGENT_CONFIRMED"
OPERATOR_STOPPED_STATUS = "CODEX_QUEUE_RUNNER_STOPPED_BY_OPERATOR"
WORKER_SHIFT_LEASE_BLOCKED_STATUS = "WORKER_SHIFT_LEASE_BLOCKED"
CONNECTOR_STATE_DIR = Path("ION/05_context/current/chatgpt_connector")
CODEX_WORK_REQUESTS_DIR = CONNECTOR_STATE_DIR / "codex_work_requests"
CODEX_QUEUE_RUNS_DIR = CONNECTOR_STATE_DIR / "codex_queue_runs"
CODEX_QUEUE_PREFLIGHTS_DIR = CONNECTOR_STATE_DIR / "codex_queue_preflights"
CODEX_WORK_LANES_DIR = CONNECTOR_STATE_DIR / "work_lanes"
RUNTIME_DIR = CONNECTOR_STATE_DIR / "runtime"
RUNNER_STATE_PATH = RUNTIME_DIR / "codex_queue_runner_state.json"
CODEX_WORK_QUEUE_INDEX = Path("ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json")
CODEX_QUEUE_RUN_SHARED_COORDINATION_PATHS = (
    CODEX_WORK_QUEUE_INDEX.as_posix(),
    RUNNER_STATE_PATH.as_posix(),
)
DOMAIN_WEAVER_CONTEXT_ACTIVE_RESOLVER_DOMAIN_ID = "domain.context_active_resolver"
AI_MOVEMENT_PREFLIGHT_SCHEMA_ID = "ion.codex_queue_runner_ai_movement_preflight.v1"
AI_MOVEMENT_PREFLIGHT_PROJECTION_SCHEMA_ID = "ion.codex_queue_runner_ai_movement_preflight_projection.v1"
AI_MOVEMENT_PREFLIGHT_WARNING_MAP_SCHEMA_ID = "ion.codex_queue_runner_ai_movement_preflight_warning_map.v1"
AGENT_CWD_BOUNDARY_PROJECTION_SCHEMA_ID = "ion.codex_queue_runner_agent_cwd_boundary_projection.v1"
CODEX_AGENT_MOUNT_RESOLUTION_SCHEMA_ID = "ion.codex_queue_runner_agent_mount_resolution.v1"
AI_MOVEMENT_GATE_REJECTED_RESULT = "AI_MOVEMENT_GATE_REJECTED"
LEGACY_TARGET_POLICY_SCHEMA_ID = "ion.codex_queue_runner_legacy_target_policy.v1"
LEGACY_TARGET_POLICY_BLOCKER_CODE = "LEGACY_QUEUE_REQUEST_TARGET_ROOT_MISSING"
CODEX_AGENT_MOUNT_REQUIRED_FILES = {
    "manifest": CODEX_AGENT_MOUNT_MANIFEST_NAME,
    "agents_md": "AGENTS.md",
    "codex_config": ".codex/config.toml",
    "portable_context_manifest": f"{CODEX_AGENT_MOUNT_PORTABLE_CONTEXT_DIR}/{CODEX_AGENT_MOUNT_PORTABLE_CONTEXT_MANIFEST}",
    "portable_capsule": f"{CODEX_AGENT_MOUNT_PORTABLE_CONTEXT_DIR}/{CODEX_AGENT_MOUNT_PORTABLE_CAPSULE}",
    "portable_active_context_package": f"{CODEX_AGENT_MOUNT_PORTABLE_CONTEXT_DIR}/{CODEX_AGENT_MOUNT_ACTIVE_CONTEXT_PACKAGE_MD}",
}
AGENT_ROLE_REQUEST_FIELDS = (
    "agent_role_id",
    "agent_role",
    "requested_role",
    "target_agent_role",
    "target_agent_role_id",
    "agent",
    "agent_id",
    "agent_display_name",
)
ROLE_TIER_REQUEST_FIELDS = (
    "role_tier",
    "agent_role_tier",
    "requested_role_tier",
    "target_role_tier",
    "domain_weaver_role_tier",
)
CALLSIGN_REQUEST_FIELDS = (
    "callsign",
    "agent_callsign",
    "display_callsign",
    "worker_callsign",
    "true_name",
    "agent_true_name",
)
DOMAIN_REQUEST_FIELDS = (
    "domain_id",
    "target_domain_id",
    "route_domain_id",
    "context_domain_id",
    "agent_domain_id",
    "domain",
    "target_domain",
    "route_domain",
)
AI_MOVEMENT_TARGETS = {
    "active_ion_control": {
        "family": "ION_Developement",
        "movement_class": "ION_KERNEL_CONTROL_MOVEMENT",
        "root_relation": "active_ion_control_root",
        "content_subpath": "ION",
    },
    "ion_gpt": {
        "family": "ION_GPT",
        "movement_class": "CUSTOM_GPT_RELEASE_MOVEMENT",
        "root_relation": "product_projection_root",
    },
    "product_packager": {
        "family": "product_packager",
        "movement_class": "CUSTOM_GPT_RELEASE_MOVEMENT",
        "root_relation": "product_projection_root",
    },
    "browser_extension": {
        "family": "browser_extension",
        "movement_class": "BROWSER_EXTENSION_MOVEMENT",
        "root_relation": "sibling_project_root",
    },
    "mcp": {
        "family": "mcp",
        "movement_class": "MCP_BRIDGE_MOVEMENT",
        "root_relation": "sibling_project_root",
    },
    "local_daemon": {
        "family": "local_daemon",
        "movement_class": "LOCAL_DAEMON_MOVEMENT",
        "root_relation": "sibling_project_root",
    },
    "systemd": {
        "family": "systemd",
        "movement_class": "LOCAL_DAEMON_MOVEMENT",
        "root_relation": "sibling_project_root",
    },
    "daimon": {
        "family": "dAimon",
        "movement_class": "DAIMON_PROJECT_MOVEMENT",
        "root_relation": "external_governed_project_root",
    },
    "needs_routed": {
        "family": "Needs_Routed",
        "movement_class": "INTAKE_ROUTING_MOVEMENT",
        "root_relation": "intake_root",
    },
    "ion_exports_local": {
        "family": "ION_EXPORTS_LOCAL",
        "movement_class": "EXPORT_PACKAGE_MOVEMENT",
        "root_relation": "export_root",
    },
    "quarentine": {
        "family": "quarentine",
        "movement_class": "ARCHIVE_REFERENCE_MOVEMENT",
        "root_relation": "archive_witness_root",
    },
    "aim_os": {
        "family": "AIM-OS",
        "movement_class": "ARCHIVE_REFERENCE_MOVEMENT",
        "root_relation": "reference_library_root",
    },
    "atlas": {
        "family": "ATLAS",
        "movement_class": "ARCHIVE_REFERENCE_MOVEMENT",
        "root_relation": "reference_library_root",
    },
    "wisdomnet": {
        "family": "wisdomNET",
        "movement_class": "ARCHIVE_REFERENCE_MOVEMENT",
        "root_relation": "reference_library_root",
    },
}
AI_MOVEMENT_TARGET_ALIASES = {
    "active": "active_ion_control",
    "active_repo": "active_ion_control",
    "ion": "active_ion_control",
    "ion_developement": "active_ion_control",
    "ion_development": "active_ion_control",
    "ion_gpt": "ion_gpt",
    "custom_gpt": "ion_gpt",
    "gpt": "ion_gpt",
    "browser_extension": "browser_extension",
    "extension": "browser_extension",
    "mcp": "mcp",
    "local_daemon": "local_daemon",
    "daemon": "local_daemon",
    "systemd": "systemd",
    "daimon": "daimon",
    "d_aimon": "daimon",
    "daimon_project": "daimon",
    "needs_routed": "needs_routed",
    "intake": "needs_routed",
    "ion_exports_local": "ion_exports_local",
    "exports": "ion_exports_local",
    "export": "ion_exports_local",
    "quarentine": "quarentine",
    "quarantine": "quarentine",
    "aim_os": "aim_os",
    "atlas": "atlas",
    "wisdomnet": "wisdomnet",
}
AI_MOVEMENT_ROOT_ID_BY_FAMILY = {
    str(meta["family"]).lower(): root_id
    for root_id, meta in AI_MOVEMENT_TARGETS.items()
}
AI_MOVEMENT_ROOT_ID_BY_MOVEMENT_CLASS = {
    "ION_KERNEL_CONTROL_MOVEMENT": "active_ion_control",
    "CUSTOM_GPT_RELEASE_MOVEMENT": "ion_gpt",
    "BROWSER_EXTENSION_MOVEMENT": "browser_extension",
    "MCP_BRIDGE_MOVEMENT": "mcp",
    "LOCAL_DAEMON_MOVEMENT": "local_daemon",
    "DAIMON_PROJECT_MOVEMENT": "daimon",
    "INTAKE_ROUTING_MOVEMENT": "needs_routed",
    "EXPORT_PACKAGE_MOVEMENT": "ion_exports_local",
    "ARCHIVE_REFERENCE_MOVEMENT": "quarentine",
}
AI_MOVEMENT_REQUEST_TARGET_FIELDS = (
    "ai_movement_target_root_id",
    "target_root_id",
    "workspace_target_root_id",
    "target_workspace_root_id",
    "target_project_root_id",
    "target_family",
    "target_project",
    "target_project_root_name",
)
AI_MOVEMENT_REQUEST_PROJECT_SUBPATH_FIELDS = (
    "target_project_subpath",
    "target_content_subpath",
    "project_subpath",
    "workspace_project_subpath",
)
AI_MOVEMENT_REQUEST_WRITE_FIELDS = (
    "planned_writes",
    "allowed_write_paths",
    "target_write_paths",
    "write_scope",
    "expected_touched_paths",
)
AI_MOVEMENT_REQUEST_ARTIFACT_FIELDS = (
    "planned_artifacts",
    "artifact_paths",
    "planned_output_artifacts",
)
DEFAULT_CODEX_TIMEOUT_SECONDS = 1800
MAX_CODEX_TIMEOUT_SECONDS = 7200
DEFAULT_DISABLE_IMAGE_GENERATION = True
CODEX_SERVICE_TIERS = {"auto", "fast"}
CODEX_TRANSIENT_USAGE_LIMIT_BUG_STATUS = "CODEX_CLI_TRANSIENT_USAGE_LIMIT_BUG_RETRY_EXHAUSTED"
CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS = "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_BUG"
CODEX_TRANSIENT_USAGE_LIMIT_RETRY_EVENT = "codex_cli_transient_usage_limit_retry"
CODEX_TRANSIENT_USAGE_LIMIT_PROMPT_THROUGH_EVENT = "codex_cli_transient_usage_limit_prompt_through"
CODEX_TRANSIENT_USAGE_LIMIT_PROMPT_THROUGH_SCHEMA_ID = (
    "ion.codex_cli_transient_usage_limit_prompt_through.v0_1"
)
CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_SCHEMA_ID = "ion.codex_cli_transient_usage_limit_recovery.v0_1"
CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_CONFIRMATION = "ION_CODEX_CARRIER_SESSION_RECOVERY_CONFIRMED"
CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_REQUEUED = "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_RECOVERY_REQUEUED"
CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_ALREADY_REQUEUED = "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_RECOVERY_ALREADY_REQUEUED"
CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_EXHAUSTED = "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_RECOVERY_EXHAUSTED"
CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_SCHEMA_ID = "ion.codex_cli_transient_usage_limit_recovery_bridge.v0_1"
CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_CONFIRMATION = "ION_CODEX_CARRIER_SESSION_BRIDGE_CONFIRMED"
CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_CREATED = "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_BRIDGE_CREATED"
CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_ALREADY_CREATED = "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_BRIDGE_ALREADY_CREATED"
CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_EXHAUSTED = "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_BRIDGE_EXHAUSTED"
CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_NOT_ELIGIBLE = "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_BRIDGE_NOT_ELIGIBLE"
MAX_CODEX_TRANSIENT_USAGE_LIMIT_RETRIES = 1
MAX_CODEX_TRANSIENT_USAGE_LIMIT_PROMPT_THROUGH_ATTEMPTS = 3
CODEX_TRANSIENT_USAGE_LIMIT_PROMPT_THROUGH_TIMEOUT_SECONDS = 180
MAX_CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_REQUEUES = 1
MAX_CODEX_TRANSIENT_USAGE_LIMIT_BRIDGES_PER_REQUEST = 1
CODEX_CARRIER_RECOVERY_BRIDGES_DIR = CONNECTOR_STATE_DIR / "codex_carrier_recovery_bridges"
DOMAIN_WEAVER_CARRIER_RECOVERY_RELAY_REQUESTS_DIR = Path("ION/05_context/current/domain_weaver/carrier_recovery/relay_requests")
MAX_LIVE_PREVIEW_BYTES = 2048
DEFAULT_LIVE_PREVIEW_BYTES = 512
MAX_WORKER_LIFECYCLE_EVENTS = 40
WORKER_TRACE_SCHEMA_ID = "ion.codex_worker_observability_trace.v0"
START_NO_RECEIPT_GRACE_SECONDS = 120
START_REQUESTED_RUN_STATUSES = {
    "CLAIMED_BY_CODEX_QUEUE_RUNNER",
    "CODEX_QUEUE_RUNNER_WORKER_STARTED",
}
START_NO_RECEIPT_STATUS = "CODEX_QUEUE_START_NO_RECEIPT"
CODEX_CLI_VANISHED_NO_OUTPUT_STATUS = "CODEX_CLI_VANISHED_NO_OUTPUT"
WORKER_CONTEXT_AWARENESS_RECEIPT_FILENAME = "worker_context_awareness_receipt.json"
WORKER_CONTEXT_ACKNOWLEDGED = "WORKER_CONTEXT_ACKNOWLEDGED"
WORKER_CONTEXT_BLOCKED = "WORKER_CONTEXT_BLOCKED"
BASE_RETURN_CONTRACT_SECTIONS = (
    "### CONTEXT PROOF",
    "### TEMPLATE ACTION PROOF",
    "### VALIDATION",
    "### RESULT",
    "### WORKLOAD DIFF",
    "### BLOCKERS",
    "### RECOMMENDED NEXT PACKET",
)
WORKLOAD_DIFF_SECTION = "### WORKLOAD DIFF"
WORKLOAD_DIFF_REQUEST_HINTS = (
    "agent",
    "cartograph",
    "probe",
    "proof",
    "design",
)
MANDATORY_RETURN_SECTIONS = (
    "### CONTEXT PROOF",
    "### TEMPLATE ACTION PROOF",
    "### VALIDATION",
    "### RESULT",
    "### WORKLOAD DIFF",
    "### BLOCKERS",
    "### RECOMMENDED NEXT PACKET",
)
WORKLOAD_TEMPLATE_BY_CLASS = {
    "proof_repair": "ion.template.autonomous_loop.local_worker.v1",
    "context_package_materialization": "ion.template.autonomous_loop.local_worker.v1",
    "code_patch": "ion.template.patch_proposal.v1",
    "design_report": "ion.template.audit_observation.v1",
    "cartography": "ion.template.autonomous_loop.local_worker.v1",
}
CODEX_WORK_LANE_SCHEMA_ID = "ion.codex_work_lane_projection.v0_1"
CODEX_WORK_LANE_INDEX_SCHEMA_ID = "ion.codex_work_lane_index.v0_1"
CODEX_WORK_LANE_ROUTE_SCHEMA_ID = "ion.codex_work_lane_route.v0_1"
CODEX_LANE_LOCK_INDEX_SCHEMA_ID = "ion.codex_lane_lock_index.v0_1"
CODEX_WORKER_CONCURRENCY_SCHEMA_ID = "ion.codex_worker_concurrency.v0_1"
CODEX_PARALLEL_PLAN_PREVIEW_SCHEMA_ID = "ion.codex_queue_parallel_plan_preview.v0_1"
CODEX_WORK_LANES = (
    "architecture_lane",
    "implementation_lane",
    "audit_lane",
    "comms_lane",
    "browser_lane",
    "context_lane",
    "maintenance_lane",
    "approval_governance_lane",
    "settlement_lane",
    "needs_triage",
)
EXECUTABLE_CODEX_WORK_LANES = tuple(lane for lane in CODEX_WORK_LANES if lane != "needs_triage")
CODEX_WORK_LANE_ALIASES = {
    "validation": "audit_lane",
    "validation_lane": "audit_lane",
}
WORK_CLASS_TO_LANE = {
    "architecture": "architecture_lane",
    "architect": "architecture_lane",
    "design": "architecture_lane",
    "design_report": "architecture_lane",
    "proposal": "architecture_lane",
    "steward": "architecture_lane",
    "vizier": "architecture_lane",
    "implementation": "implementation_lane",
    "code": "implementation_lane",
    "code_patch": "implementation_lane",
    "patch": "implementation_lane",
    "mason": "implementation_lane",
    "audit": "audit_lane",
    "validation": "audit_lane",
    "review": "audit_lane",
    "nemesis": "audit_lane",
    "vice": "audit_lane",
    "comms": "comms_lane",
    "communications": "comms_lane",
    "agent_comms": "comms_lane",
    "browser": "browser_lane",
    "browser_probe": "browser_lane",
    "visual_proof": "browser_lane",
    "visual_proof_and_review": "browser_lane",
    "ui_visual_proof": "browser_lane",
    "dom": "browser_lane",
    "context": "context_lane",
    "cartography": "context_lane",
    "runtime_cartography": "context_lane",
    "context_package_materialization": "context_lane",
    "maintenance": "maintenance_lane",
    "queue": "maintenance_lane",
    "queue_hygiene": "maintenance_lane",
    "proof_repair": "maintenance_lane",
    "repair": "maintenance_lane",
    "approval": "approval_governance_lane",
    "approval_governance": "approval_governance_lane",
    "authority_receipt": "approval_governance_lane",
    "receipt_issuance": "approval_governance_lane",
    "settlement": "settlement_lane",
}
AGENT_ROLE_TO_LANE = {
    "role.vizier": "architecture_lane",
    "vizier": "architecture_lane",
    "role.steward": "architecture_lane",
    "steward": "architecture_lane",
    "role.mason": "implementation_lane",
    "mason": "implementation_lane",
    "role.nemesis": "audit_lane",
    "nemesis": "audit_lane",
    "role.vice": "audit_lane",
    "vice": "audit_lane",
    "role.comms_cartographer": "comms_lane",
    "comms_cartographer": "comms_lane",
    "role.browser_dom_cartographer": "browser_lane",
    "browser_dom_cartographer": "browser_lane",
    "role.visual_proof_auditor": "browser_lane",
    "visual_proof_auditor": "browser_lane",
    "role.context_cartographer": "context_lane",
    "context_cartographer": "context_lane",
    "role.ionologist": "context_lane",
    "ionologist": "context_lane",
    "approval_governance_domain": "approval_governance_lane",
    "approval_governor": "approval_governance_lane",
}

FAILURE_CLASSES = (
    "BACKEND_CODEX_FAILURE",
    "CARRIER_ADAPTER_FAILURE",
    "CODEX_CLI_FAILURE",
    "DAEMON_FAILURE",
    "ION_CORE_FAILURE",
)

ACTIVE_RUN_STATUSES = {
    "CLAIMED_BY_CODEX_QUEUE_RUNNER",
    "CODEX_QUEUE_RUNNER_WORKER_STARTED",
    "CODEX_CLI_RUNNING",
}

TERMINAL_RUN_STATUSES = {
    CODEX_TRANSIENT_USAGE_LIMIT_BUG_STATUS,
    "RETURN_RECORDED_PROOF_ACCEPTED",
    "RETURN_RECORDED_PROOF_BLOCKED",
    "RETURN_TEMPLATE_INVALID",
    "CODEX_CLI_EXIT_NONZERO",
    CODEX_CLI_VANISHED_NO_OUTPUT_STATUS,
    "CODEX_CLI_TIMEOUT",
    "WORKER_CONTEXT_MOUNT_INVALID",
    WORKER_SHIFT_LEASE_BLOCKED_STATUS,
    "DAEMON_WORKER_EXITED_WITHOUT_FINALIZATION",
    OPERATOR_STOPPED_STATUS,
    START_NO_RECEIPT_STATUS,
}

TERMINAL_FAILED_STATUSES = {
    "CODEX_CLI_EXIT_NONZERO",
    CODEX_CLI_VANISHED_NO_OUTPUT_STATUS,
    "CODEX_CLI_TIMEOUT",
    "WORKER_CONTEXT_MOUNT_INVALID",
    "DAEMON_WORKER_EXITED_WITHOUT_FINALIZATION",
    START_NO_RECEIPT_STATUS,
}


def _collect_blockers_from_mapping(payload: Mapping[str, Any] | None) -> list[str]:
    if not isinstance(payload, Mapping):
        return []
    blockers: list[str] = []
    finding = str(payload.get("finding") or "").strip()
    if finding:
        blockers.append(finding)
    raw_blockers = payload.get("blockers")
    if isinstance(raw_blockers, list):
        for item in raw_blockers:
            if isinstance(item, Mapping):
                code = str(item.get("code") or item.get("finding") or item.get("detail") or "").strip()
            else:
                code = str(item or "").strip()
            if code:
                blockers.append(code)
    resolver = payload.get("context_active_resolver")
    if isinstance(resolver, Mapping):
        blockers.extend(_collect_blockers_from_mapping(resolver))
    return blockers


def _worker_return_status_for_run(
    run: Mapping[str, Any],
    *,
    result: str | None = None,
    context_gate: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    submit = run.get("submit_result") if isinstance(run.get("submit_result"), Mapping) else {}
    status = str(run.get("status") or result or "").strip()
    accepted = submit.get("accepted_for_carrier_intake")
    blockers: list[str] = []
    for source in (
        context_gate,
        run.get("context_gate") if isinstance(run.get("context_gate"), Mapping) else None,
        run.get("worker_shift_lease") if isinstance(run.get("worker_shift_lease"), Mapping) else None,
        run.get("ai_movement_preflight") if isinstance(run.get("ai_movement_preflight"), Mapping) else None,
        run.get("codex_agent_mount_resolution") if isinstance(run.get("codex_agent_mount_resolution"), Mapping) else None,
        submit,
    ):
        blockers.extend(_collect_blockers_from_mapping(source))
    failure = str(run.get("failure_classification") or "").strip()
    if failure and failure not in blockers:
        blockers.append(failure)
    deduped_blockers = sorted({code for code in blockers if str(code).strip()})
    return {
        "schema_id": "ion.codex_queue_runner.worker_return_status.v0_1_candidate",
        "run_status": status or None,
        "result": result or status or None,
        "terminal": status in TERMINAL_RUN_STATUSES,
        "failure_classification": failure or None,
        "accepted_for_carrier_intake": accepted if isinstance(accepted, bool) else None,
        "carrier_intake_state": submit.get("carrier_intake_state"),
        "carrier_intake_only": True,
        "product_state_accepted": False,
        "content_returned": submit.get("content_returned"),
        "return_template_valid": submit.get("return_template_valid"),
        "context_proof_accepted": submit.get("context_proof_accepted"),
        "template_action_proof_accepted": submit.get("template_action_proof_accepted"),
        "latest_return_packet_path": run.get("latest_return_packet_path") or submit.get("packet_path"),
        "return_packet_paths": list(run.get("return_packet_paths") or []),
        "latest_task_return_machine_receipt_path": run.get("latest_task_return_machine_receipt_path") or submit.get("machine_receipt_path"),
        "blockers": deduped_blockers,
        "carrier_intake_only": True,
        "product_state": False,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
    }

LIVE_PREVIEW_TARGETS = {
    "latest_return",
    "stdout",
    "stderr",
    "worker_stdout",
    "worker_stderr",
}
WORKER_TRACE_PREVIEW_PRIORITY = (
    "latest_return",
    "stdout",
    "stderr",
    "worker_stderr",
    "worker_stdout",
)

DEFAULT_CONTEXT_READS = (
    "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json",
    "ION/05_context/current/ACTIVE_CARRIER_MESSAGE_QUEUE.json",
    "ION/04_packages/kernel/ion_chatgpt_browser_mcp_connector_contract.py",
    "ION/04_packages/kernel/ion_carrier_task_return.py",
    "ION/04_packages/kernel/ion_carrier_continue.py",
    "ION/04_packages/kernel/ion_codex_queue_runner.py",
    "ION/02_architecture/ION_FULL_CARRIER_MCP_PARITY_PROTOCOL.md",
    "ION/03_registry/chatgpt_browser_carrier_profile.yaml",
    "ION/03_registry/codex_cli_carrier_profile.yaml",
    "ION/04_packages/kernel/ion_cockpit_view_model.py",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _safe_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")[:80] or "codex_queue"


def _safe_unique_slug(value: str, *, max_base_length: int = 64, digest_length: int = 12) -> str:
    raw = str(value or "").strip() or "codex_queue"
    base = re.sub(r"[^a-z0-9]+", "_", raw.lower()).strip("_")[:max_base_length] or "codex_queue"
    digest = hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:digest_length]
    return f"{base}_{digest}"


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_json_payload(payload: Mapping[str, Any]) -> str:
    material = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(material.encode("utf-8", errors="replace")).hexdigest()


def _clean_path_value(value: str | Path) -> str:
    text = str(value).replace("\\", "/").strip()
    while text.startswith("./"):
        text = text[2:]
    return text.rstrip("/") or "."


def _slug_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")


def _request_path_values(request: Mapping[str, Any], fields: tuple[str, ...]) -> list[str]:
    values: list[str] = []
    for field in fields:
        raw = request.get(field)
        if raw is None:
            continue
        items = raw if isinstance(raw, list) else [raw]
        for item in items:
            if isinstance(item, Mapping):
                path = str(item.get("path") or item.get("raw_path") or item.get("target") or "").strip()
            else:
                path = str(item or "").strip()
            if path:
                values.append(path)
    return values


def _normalize_target_root_id(value: Any) -> str | None:
    key = _slug_key(value)
    if not key:
        return None
    if key in AI_MOVEMENT_TARGETS:
        return key
    if key in AI_MOVEMENT_TARGET_ALIASES:
        return AI_MOVEMENT_TARGET_ALIASES[key]
    return AI_MOVEMENT_ROOT_ID_BY_FAMILY.get(key)


def _movement_class_for_target_root(request: Mapping[str, Any], target_root_id: str) -> str:
    requested = str(request.get("movement_class") or "").strip()
    if requested:
        return requested
    meta = AI_MOVEMENT_TARGETS.get(target_root_id) or {}
    return str(meta.get("movement_class") or "ION_KERNEL_CONTROL_MOVEMENT")


def _target_root_id_from_path(path_value: str) -> str | None:
    clean = _clean_path_value(path_value)
    parts = [part for part in clean.split("/") if part and part != ".."]
    if not parts:
        return None
    first = parts[0]
    if first == "ION":
        return "active_ion_control"
    return AI_MOVEMENT_ROOT_ID_BY_FAMILY.get(first.lower()) or _normalize_target_root_id(first)


def _request_target_root_resolution(request: Mapping[str, Any]) -> dict[str, Any]:
    for field in AI_MOVEMENT_REQUEST_TARGET_FIELDS:
        target = _normalize_target_root_id(request.get(field))
        if target:
            return {
                "schema_id": LEGACY_TARGET_POLICY_SCHEMA_ID,
                "target_root_id": target,
                "source": f"request.{field}",
                "accepted": True,
                "status": "EXPLICIT_TARGET_BOUND",
            }
    declared = _request_declared_ai_movement_envelope(request)
    for field in AI_MOVEMENT_REQUEST_TARGET_FIELDS:
        target = _normalize_target_root_id(declared.get(field))
        if target:
            return {
                "schema_id": LEGACY_TARGET_POLICY_SCHEMA_ID,
                "target_root_id": target,
                "source": f"request.ai_movement_root_envelope.{field}",
                "accepted": True,
                "status": "EXPLICIT_ENVELOPE_TARGET_BOUND",
            }
    movement_class = str(request.get("movement_class") or "").strip()
    if movement_class in AI_MOVEMENT_ROOT_ID_BY_MOVEMENT_CLASS:
        return {
            "schema_id": LEGACY_TARGET_POLICY_SCHEMA_ID,
            "target_root_id": AI_MOVEMENT_ROOT_ID_BY_MOVEMENT_CLASS[movement_class],
            "source": "request.movement_class",
            "accepted": True,
            "status": "MOVEMENT_CLASS_TARGET_BOUND",
        }
    declared_movement_class = str(declared.get("movement_class") or "").strip()
    if declared_movement_class in AI_MOVEMENT_ROOT_ID_BY_MOVEMENT_CLASS:
        return {
            "schema_id": LEGACY_TARGET_POLICY_SCHEMA_ID,
            "target_root_id": AI_MOVEMENT_ROOT_ID_BY_MOVEMENT_CLASS[declared_movement_class],
            "source": "request.ai_movement_root_envelope.movement_class",
            "accepted": True,
            "status": "ENVELOPE_MOVEMENT_CLASS_TARGET_BOUND",
        }
    for field in AI_MOVEMENT_REQUEST_WRITE_FIELDS + AI_MOVEMENT_REQUEST_ARTIFACT_FIELDS:
        for path in _request_path_values(request, (field,)):
            target = _target_root_id_from_path(path)
            if target:
                return {
                    "schema_id": LEGACY_TARGET_POLICY_SCHEMA_ID,
                    "target_root_id": target,
                    "source": f"request.{field}",
                    "source_path": path,
                    "accepted": True,
                    "status": "REQUEST_PATH_TARGET_BOUND",
                }
    return {
        "schema_id": LEGACY_TARGET_POLICY_SCHEMA_ID,
        "target_root_id": "active_ion_control",
        "source": "legacy_default_active_ion_control",
        "accepted": False,
        "status": "BLOCKED",
        "blocker": {
            "code": LEGACY_TARGET_POLICY_BLOCKER_CODE,
            "detail": (
                "Legacy queued request is missing target_root_id, movement_class, "
                "ai_movement_root_envelope target fields, and target path evidence."
            ),
        },
    }


def _request_target_root_id(request: Mapping[str, Any]) -> str:
    return str(_request_target_root_resolution(request).get("target_root_id") or "active_ion_control")


def _section_heading_present(text: str, heading: str) -> bool:
    normalized = heading.strip().lower()
    for line in text.splitlines():
        if line.strip().lower() == normalized:
            return True
    return False


def _has_required_return_sections(text: str, sections: list[str]) -> bool:
    if not sections:
        return False
    return all(_section_heading_present(text, heading) for heading in sections if heading.startswith("### "))


def _read_rel_text_if_exists(root: Path, rel_path: str) -> str | None:
    try:
        candidate = _safe_rel_path(root, rel_path)
    except ValueError:
        return None
    if not candidate.exists():
        return None
    return candidate.read_text(encoding="utf-8", errors="replace")


def _select_task_output_for_submit(
    root: Path,
    run: Mapping[str, Any],
    request: Mapping[str, Any],
    task_output: str,
) -> tuple[str, str]:
    required_sections = _return_contract_sections_for_request(request)
    task_return_body_rel = str(run.get("task_return_body_path") or "").strip()
    if task_return_body_rel:
        task_return_body = _read_rel_text_if_exists(root, task_return_body_rel)
        if task_return_body and _has_required_return_sections(task_return_body, required_sections):
            return task_return_body, "task_return_body_path"
    return task_output, "last_message_path"


REQUEST_TASK_RETURN_TERMINAL_STATUSES = {
    "RETURN_RECORDED_PROOF_ACCEPTED",
    "RETURN_RECORDED_PROOF_BLOCKED",
    "RETURN_TEMPLATE_INVALID",
}


def _terminal_request_result_for_run(
    root: Path,
    run: Mapping[str, Any],
    request_rel_fallback: str | None = None,
) -> dict[str, Any] | None:
    request_rel = str(run.get("request_path") or request_rel_fallback or "").strip()
    if not request_rel:
        return None
    try:
        request_path = _safe_rel_path(root, request_rel)
        request = _load_request(request_path)
    except (OSError, ValueError):
        return None
    status = str(request.get("status") or "").strip()
    if status not in REQUEST_TASK_RETURN_TERMINAL_STATUSES:
        return None
    return {
        "status": status,
        "request_path": _connector_rel(request_path, root),
        "request_id": request.get("request_id"),
        "latest_return_packet_path": request.get("latest_return_packet_path"),
        "return_packet_paths": request.get("return_packet_paths") if isinstance(request.get("return_packet_paths"), list) else [],
        "latest_task_return_machine_receipt_path": request.get("latest_task_return_machine_receipt_path"),
        "failure_classification": request.get("failure_classification"),
    }


def _adopt_terminal_request_result_for_run(
    root: Path,
    run_path: Path,
    run: dict[str, Any],
    request_result: Mapping[str, Any],
    *,
    reason: str,
    output_presence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    now = _now()
    previous_status = str(run.get("status") or "")
    status = str(request_result.get("status") or "")
    accepted = status == "RETURN_RECORDED_PROOF_ACCEPTED"
    packet_path = str(request_result.get("latest_return_packet_path") or "").strip()
    request_return_packet_paths = [
        str(item)
        for item in (request_result.get("return_packet_paths") or [])
        if str(item).strip()
    ]
    if packet_path and packet_path not in request_return_packet_paths:
        request_return_packet_paths.append(packet_path)
    machine_receipt_path = str(request_result.get("latest_task_return_machine_receipt_path") or "").strip()
    run["status"] = status
    run["completed_at"] = run.get("completed_at") or now
    run["updated_at"] = now
    run["failure_classification"] = (
        None
        if accepted
        else str(request_result.get("failure_classification") or "BACKEND_CODEX_FAILURE")
    )
    if packet_path:
        run["latest_return_packet_path"] = packet_path
    if request_return_packet_paths:
        run["return_packet_paths"] = request_return_packet_paths
    if machine_receipt_path:
        run["latest_task_return_machine_receipt_path"] = machine_receipt_path
    if not isinstance(run.get("submit_result"), Mapping):
        run["submit_result"] = {
            "accepted_for_carrier_intake": accepted,
            "packet_path": packet_path or None,
            "machine_receipt_path": machine_receipt_path or None,
            "return_packet_paths": request_return_packet_paths,
            "reconciled_from_request_status": True,
        }
    run["daemon_reconciliation"] = {
        "reconciled_at": now,
        "reason": reason,
        "previous_status": previous_status,
        "request_status": status,
        "request_path": request_result.get("request_path"),
        "latest_return_packet_path": packet_path or None,
        "return_packet_paths": request_return_packet_paths,
        "latest_task_return_machine_receipt_path": machine_receipt_path or None,
        "output_presence": dict(output_presence or {}),
    }
    _append_worker_lifecycle_event(
        run,
        "worker_terminal",
        terminal_state="request_terminal_status_adopted",
        task_return_packet_path=packet_path or None,
        context_proof_accepted=accepted or None,
        template_action_proof_accepted=accepted or None,
    )
    _write_run_packet(run_path, run)
    snapshot_rel = _worker_trace_snapshot_rel(run)
    if snapshot_rel:
        _write_worker_trace_snapshot(root, run)
    return {
        "adopted_status": status,
        "previous_status": previous_status,
        "request_path": request_result.get("request_path"),
        "latest_return_packet_path": packet_path or None,
        "return_packet_paths": request_return_packet_paths,
        "latest_task_return_machine_receipt_path": machine_receipt_path or None,
    }


def _append_worker_lifecycle_event(run: dict[str, Any], event: str, **fields: Any) -> None:
    events = list(run.get("worker_lifecycle_events") or [])
    payload = {
        "event": event,
        "at": _now(),
        "run_id": run.get("run_id"),
        "request_id": run.get("request_id"),
        "status": run.get("status"),
        "pid": run.get("pid"),
        "production_authority": False,
        "live_execution_authority": False,
    }
    payload.update({key: value for key, value in fields.items() if value is not None})
    events.append(payload)
    run["worker_lifecycle_events"] = events[-MAX_WORKER_LIFECYCLE_EVENTS:]


def _resolve_root(root: str | Path | None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    if candidate.is_dir() and (candidate / "ION").exists():
        return candidate
    return resolve_shell_root_from_ion_root(root)


def _safe_rel_path(root: Path, value: str) -> Path:
    rel = Path(value)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("path must be repo-relative and may not escape the repo root")
    target = (root / rel).resolve()
    target.relative_to(root)
    return target


def _connector_rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _active_root_proof(root: Path) -> dict[str, Any]:
    pyproject = root / "pyproject.toml"
    repo_authority = root / "ION/REPO_AUTHORITY.md"
    proof_ok = pyproject.is_file() and repo_authority.is_file()
    return {
        "schema_id": "ion.active_root_proof.v0_1_candidate",
        "active_root": str(root),
        "active_root_realpath": str(root.resolve(strict=False)),
        "required_siblings": {
            "pyproject.toml": {
                "path": "pyproject.toml",
                "present": pyproject.is_file(),
            },
            "ION/REPO_AUTHORITY.md": {
                "path": "ION/REPO_AUTHORITY.md",
                "present": repo_authority.is_file(),
            },
        },
        "proof_ok": proof_ok,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "materialization_write_authority": False,
    }


def _excerpt_for_context(path: Path, *, max_chars: int = 220) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        compact = line.strip()
        if compact:
            return compact[:max_chars]
    return text[:max_chars]


def _observe_context_path(root: Path, path_value: str, *, required: bool = True) -> dict[str, Any]:
    row: dict[str, Any] = {
        "kind": "file",
        "path": path_value,
        "required": bool(required),
        "status": "MISSING_REQUIRED" if required else "MISSING_OPTIONAL",
        "exists": False,
        "sha256": None,
        "excerpt": None,
        "bytes": None,
        "error": None,
    }
    try:
        target = _safe_rel_path(root, path_value)
    except ValueError:
        row["status"] = "INVALID_PATH"
        row["error"] = "path_not_repo_relative"
        return row
    if not target.exists() or not target.is_file():
        return row
    try:
        stat = target.stat()
        row["exists"] = True
        row["bytes"] = int(stat.st_size)
        row["sha256"] = _sha256_file(target)
        row["excerpt"] = _excerpt_for_context(target)
        row["status"] = "READY"
    except Exception as exc:  # pragma: no cover - defensive only
        row["status"] = "READ_ERROR"
        row["error"] = str(exc)
    return row


def _load_request(path: Path) -> dict[str, Any]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"invalid work request JSON: {path}")
    return payload


def normalize_codex_work_lane_id(value: str | None) -> str | None:
    raw = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    if not raw:
        return None
    if raw in CODEX_WORK_LANE_ALIASES:
        return CODEX_WORK_LANE_ALIASES[raw]
    if raw in CODEX_WORK_LANES:
        return raw
    if raw.endswith("_lane") and raw in CODEX_WORK_LANES:
        return raw
    candidate = f"{raw}_lane"
    if candidate in CODEX_WORK_LANE_ALIASES:
        return CODEX_WORK_LANE_ALIASES[candidate]
    return candidate if candidate in CODEX_WORK_LANES else None


def _normalized_lane_source(value: Any) -> str:
    return re.sub(r"[^a-z0-9_.]+", "_", str(value or "").strip().lower()).strip("_")


def _request_text_for_lane(request: Mapping[str, Any]) -> str:
    fields: list[str] = []
    for key in (
        "objective",
        "request_kind",
        "work_class",
        "workload_class",
        "route_family",
        "agent_role",
        "agent",
        "requested_role",
    ):
        value = request.get(key)
        if value:
            fields.append(str(value))
    route_metadata = request.get("route_metadata")
    if isinstance(route_metadata, Mapping):
        for key in ("work_class", "route_family", "agent_role"):
            value = route_metadata.get(key)
            if value:
                fields.append(str(value))
    return "\n".join(fields).lower()


def classify_codex_work_request_lane(request: Mapping[str, Any]) -> dict[str, Any]:
    """Return the deterministic compatibility lane for a Codex work request."""

    raw_explicit_lane = str(request.get("lane_id") or "").strip()
    explicit_lane = normalize_codex_work_lane_id(raw_explicit_lane or None)
    reasons: list[str] = []
    if explicit_lane:
        normalized_explicit_lane = raw_explicit_lane.lower().replace("-", "_").replace(" ", "_")
        candidate_explicit_lane = f"{normalized_explicit_lane}_lane"
        if normalized_explicit_lane in CODEX_WORK_LANE_ALIASES or candidate_explicit_lane in CODEX_WORK_LANE_ALIASES:
            reasons.append("validation_lane_alias_to_audit_lane")
        reasons.append("explicit_lane_id")
        return {
            "schema_id": CODEX_WORK_LANE_ROUTE_SCHEMA_ID,
            "lane_id": explicit_lane,
            "work_class": request.get("work_class") or request.get("workload_class"),
            "source": "explicit_lane_id",
            "reasons": reasons,
            "valid_lane": explicit_lane in CODEX_WORK_LANES,
            "production_authority": False,
            "live_execution_authority": False,
        }

    route_metadata = request.get("route_metadata")
    candidate_values: list[tuple[str, Any]] = [
        ("work_class", request.get("work_class")),
        ("workload_class", request.get("workload_class")),
        ("request_kind", request.get("request_kind")),
        ("route_family", request.get("route_family")),
    ]
    if isinstance(route_metadata, Mapping):
        candidate_values.extend(
            [
                ("route_metadata.work_class", route_metadata.get("work_class")),
                ("route_metadata.route_family", route_metadata.get("route_family")),
            ]
        )
    for source, value in candidate_values:
        normalized = _normalized_lane_source(value)
        if normalized in WORK_CLASS_TO_LANE:
            lane_id = WORK_CLASS_TO_LANE[normalized]
            reasons.append(f"{source}:{normalized}")
            return {
                "schema_id": CODEX_WORK_LANE_ROUTE_SCHEMA_ID,
                "lane_id": lane_id,
                "work_class": request.get("work_class") or request.get("workload_class") or normalized,
                "source": source,
                "reasons": reasons,
                "valid_lane": True,
                "production_authority": False,
                "live_execution_authority": False,
            }

    agent_candidate_values = [
        request.get("agent_role"),
        request.get("agent_role_id"),
        request.get("requested_role"),
        request.get("agent"),
        request.get("agent_display_name"),
    ]
    for value in agent_candidate_values:
        normalized = _normalized_lane_source(value)
        role_key = f"role.{normalized}" if normalized and not normalized.startswith("role.") else normalized
        if role_key in AGENT_ROLE_TO_LANE:
            lane_id = AGENT_ROLE_TO_LANE[role_key]
            reasons.append(f"agent_field:{role_key}")
            return {
                "schema_id": CODEX_WORK_LANE_ROUTE_SCHEMA_ID,
                "lane_id": lane_id,
                "work_class": request.get("work_class") or request.get("workload_class") or "agent_invocation",
                "source": "agent_field",
                "reasons": reasons,
                "valid_lane": True,
                "production_authority": False,
                "live_execution_authority": False,
            }

    text = _request_text_for_lane(request)
    for role in re.findall(r"role\.[a-z0-9_]+", text):
        if role in AGENT_ROLE_TO_LANE:
            lane_id = AGENT_ROLE_TO_LANE[role]
            reasons.append(f"agent_role:{role}")
            return {
                "schema_id": CODEX_WORK_LANE_ROUTE_SCHEMA_ID,
                "lane_id": lane_id,
                "work_class": request.get("work_class") or request.get("workload_class") or "agent_invocation",
                "source": "agent_role_text",
                "reasons": reasons,
                "valid_lane": True,
                "production_authority": False,
                "live_execution_authority": False,
            }

    keyword_lane_pairs = (
        (
            (
                "approval_governance",
                "approval governance",
                "authority_receipt",
                "authority receipt",
                "receipt_issuance",
                "receipt issuance",
                "accepted_state_movement_authority",
            ),
            "approval_governance_lane",
        ),
        (("domain weave", "domain_weave", "architecture", "protocol"), "architecture_lane"),
        (("mason", "patch", "implement", "code"), "implementation_lane"),
        (("nemesis", "audit", "review", "validate"), "audit_lane"),
        (("comms", "communication", "cockpit", "team comms"), "comms_lane"),
        (("browser", "dom", "extension"), "browser_lane"),
        (("context", "capsule", "cartograph", "manifest"), "context_lane"),
        (("queue", "hygiene", "stale", "supersede", "duplicate", "repair"), "maintenance_lane"),
        (("settlement", "submit_task_return", "task return"), "settlement_lane"),
    )
    for keywords, lane_id in keyword_lane_pairs:
        if any(keyword in text for keyword in keywords):
            reasons.append(f"keyword:{lane_id}")
            return {
                "schema_id": CODEX_WORK_LANE_ROUTE_SCHEMA_ID,
                "lane_id": lane_id,
                "work_class": request.get("work_class") or request.get("workload_class"),
                "source": "objective_keyword",
                "reasons": reasons,
                "valid_lane": True,
                "production_authority": False,
                "live_execution_authority": False,
            }

    return {
        "schema_id": CODEX_WORK_LANE_ROUTE_SCHEMA_ID,
        "lane_id": "needs_triage",
        "work_class": request.get("work_class") or request.get("workload_class"),
        "source": "unclassified",
        "reasons": ["no_deterministic_lane_match"],
        "valid_lane": True,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _codex_work_lane_row(root: Path, path: Path, request: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(request or _load_request(path))
    route = classify_codex_work_request_lane(payload)
    return {
        "request_id": payload.get("request_id"),
        "path": _connector_rel(path, root),
        "status": payload.get("status"),
        "lane_id": route.get("lane_id"),
        "work_class": payload.get("work_class") or payload.get("workload_class") or route.get("work_class"),
        "route_family": payload.get("route_family"),
        "risk_level": payload.get("risk_level"),
        "agent_role": payload.get("agent_role"),
        "created_at": payload.get("created_at"),
        "updated_at": payload.get("updated_at"),
        "objective_sha256": payload.get("objective_sha256")
        or hashlib.sha256(str(payload.get("objective") or "").encode("utf-8")).hexdigest(),
        "route": route,
    }


def build_codex_work_lane_index(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    lane_rows: dict[str, list[dict[str, Any]]] = {lane_id: [] for lane_id in CODEX_WORK_LANES}
    queued_rows: list[dict[str, Any]] = []
    for path in _request_paths(shell_root):
        payload = _load_request(path)
        if payload.get("status") != "QUEUED_FOR_CODEX_CARRIER":
            continue
        row = _codex_work_lane_row(shell_root, path, payload)
        lane_id = str(row.get("lane_id") or "needs_triage")
        if lane_id not in lane_rows:
            lane_id = "needs_triage"
            row["lane_id"] = lane_id
        lane_rows[lane_id].append(row)
        queued_rows.append(row)
    lanes: list[dict[str, Any]] = []
    for lane_id in CODEX_WORK_LANES:
        rows = sorted(lane_rows[lane_id], key=lambda row: (str(row.get("created_at") or ""), str(row.get("path") or "")))
        lanes.append(
            {
                "schema_id": CODEX_WORK_LANE_SCHEMA_ID,
                "lane_id": lane_id,
                "queue_path": (CODEX_WORK_LANES_DIR / f"{lane_id}.json").as_posix(),
                "request_count": len(rows),
                "next_request_path": rows[0]["path"] if rows else None,
                "requests": rows,
                "production_authority": False,
                "live_execution_authority": False,
            }
        )
    executable_waiting = [row for row in queued_rows if row.get("lane_id") in EXECUTABLE_CODEX_WORK_LANES]
    return {
        "schema_id": CODEX_WORK_LANE_INDEX_SCHEMA_ID,
        "generated_at": _now(),
        "lane_dir": CODEX_WORK_LANES_DIR.as_posix(),
        "lane_ids": list(CODEX_WORK_LANES),
        "executable_lane_ids": list(EXECUTABLE_CODEX_WORK_LANES),
        "queued_request_count": len(queued_rows),
        "executable_waiting_request_count": len(executable_waiting),
        "needs_triage_count": len(lane_rows["needs_triage"]),
        "lanes": lanes,
        "lane_counts": {lane["lane_id"]: lane["request_count"] for lane in lanes},
        "next_request_by_lane": {lane["lane_id"]: lane["next_request_path"] for lane in lanes},
        "production_authority": False,
        "live_execution_authority": False,
    }


def materialize_codex_work_lane_index(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    index = build_codex_work_lane_index(shell_root)
    lane_dir = shell_root / CODEX_WORK_LANES_DIR
    lane_dir.mkdir(parents=True, exist_ok=True)
    for lane in index.get("lanes") or []:
        if not isinstance(lane, Mapping):
            continue
        lane_id = str(lane.get("lane_id") or "")
        if lane_id not in CODEX_WORK_LANES:
            continue
        _write_json(lane_dir / f"{lane_id}.json", lane)
    compact_index = {k: v for k, v in index.items() if k != "lanes"}
    _write_json(lane_dir / "INDEX.json", compact_index)
    return index


def _request_paths(root: Path) -> list[Path]:
    request_root = root / CODEX_WORK_REQUESTS_DIR
    if not request_root.exists():
        return []
    return sorted((path for path in request_root.glob("*.json") if path.is_file()), key=lambda path: path.name)


def _queued_request_paths(root: Path, lane_id: str | None = None) -> list[Path]:
    normalized_lane_id = normalize_codex_work_lane_id(lane_id)
    queued: list[Path] = []
    for path in _request_paths(root):
        payload = _load_request(path)
        if payload.get("status") != "QUEUED_FOR_CODEX_CARRIER":
            continue
        if normalized_lane_id and classify_codex_work_request_lane(payload).get("lane_id") != normalized_lane_id:
            continue
        queued.append(path)
    return queued


def _active_run_entries(state: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return active worker references without assuming a single global worker.

    Compatibility note: older state files use ``active_run`` as a singleton.
    Newer multi-lane/parallel-safe state may also carry ``active_runs`` keyed by
    run_id. This helper is intentionally read-side tolerant so introducing lane
    workers does not strand old receipts or require a state migration.
    """
    entries: list[dict[str, Any]] = []
    active_runs = state.get("active_runs")
    if isinstance(active_runs, Mapping):
        for value in active_runs.values():
            if isinstance(value, Mapping):
                entries.append(dict(value))
    elif isinstance(active_runs, list):
        for value in active_runs:
            if isinstance(value, Mapping):
                entries.append(dict(value))
    active = state.get("active_run")
    if isinstance(active, Mapping):
        active_run_id = str(active.get("run_id") or "")
        if active_run_id and not any(str(row.get("run_id") or "") == active_run_id for row in entries):
            entries.append(dict(active))
    return entries


def _running_active_run_entries(state: Mapping[str, Any]) -> list[dict[str, Any]]:
    running: list[dict[str, Any]] = []
    for entry in _active_run_entries(state):
        try:
            pid = int(entry.get("pid")) if entry.get("pid") else None
        except (TypeError, ValueError):
            pid = None
        if pid and _pid_running(pid):
            running.append(entry)
    return running


def _active_runs_with_entry(entries: list[dict[str, Any]], entry: Mapping[str, Any]) -> dict[str, Any]:
    active_runs: dict[str, Any] = {}
    for row in entries:
        key = _active_run_key(row)
        if key:
            active_runs[key] = dict(row)
    key = _active_run_key(entry)
    if key:
        active_runs[key] = dict(entry)
    return active_runs


def _active_run_key(entry: Mapping[str, Any]) -> str:
    for field in ("run_id", "run_packet_path", "request_path"):
        value = str(entry.get(field) or "").strip()
        if value:
            return value
    return ""


def _active_entry_matches(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    for field in ("run_id", "run_packet_path", "request_path"):
        left_value = str(left.get(field) or "").strip()
        right_value = str(right.get(field) or "").strip()
        if left_value and right_value and left_value == right_value:
            return True
    return False


def _active_runs_without_entry(entries: list[dict[str, Any]], entry: Mapping[str, Any]) -> dict[str, Any]:
    active_runs: dict[str, Any] = {}
    for row in entries:
        if _active_entry_matches(row, entry):
            continue
        key = _active_run_key(row)
        if key:
            active_runs[key] = dict(row)
    return active_runs


def _latest_active_entry(entries: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not entries:
        return None
    return sorted(
        entries,
        key=lambda row: (str(row.get("started_at") or ""), str(row.get("run_id") or ""), str(row.get("run_packet_path") or "")),
    )[-1]


def _active_runs_by_lane(entries: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_lane: dict[str, list[dict[str, Any]]] = {lane_id: [] for lane_id in EXECUTABLE_CODEX_WORK_LANES}
    by_lane["unknown_lane"] = []
    for entry in entries:
        lane_id = str(entry.get("lane_id") or "").strip()
        if lane_id not in EXECUTABLE_CODEX_WORK_LANES:
            lane_id = "unknown_lane"
        by_lane.setdefault(lane_id, []).append(dict(entry))
    return by_lane


def _lane_lock_index(entries: list[dict[str, Any]]) -> dict[str, Any]:
    by_lane = _active_runs_by_lane(entries)
    locks: dict[str, Any] = {}
    for lane_id in EXECUTABLE_CODEX_WORK_LANES:
        rows = by_lane.get(lane_id) or []
        locks[lane_id] = {
            "lane_id": lane_id,
            "locked": bool(rows),
            "active_run_count": len(rows),
            "active_run_ids": [str(row.get("run_id") or "") for row in rows if str(row.get("run_id") or "").strip()],
            "request_paths": [str(row.get("request_path") or "") for row in rows if str(row.get("request_path") or "").strip()],
            "same_lane_parallelism": 1,
        }
    unknown_rows = by_lane.get("unknown_lane") or []
    return {
        "schema_id": CODEX_LANE_LOCK_INDEX_SCHEMA_ID,
        "policy": "different_lanes_may_run_concurrently_same_lane_parallelism_is_one_unknown_lane_blocks_all_lane_starts",
        "same_lane_parallelism": 1,
        "active_run_count": len(entries),
        "active_lane_count": sum(1 for lane_id in EXECUTABLE_CODEX_WORK_LANES if locks[lane_id]["locked"]),
        "unknown_lane_active_run_count": len(unknown_rows),
        "unknown_lane_blocks_new_lane_starts": bool(unknown_rows),
        "locks": locks,
    }


def _concurrency_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    lane_locks = _lane_lock_index(entries)
    return {
        "schema_id": CODEX_WORKER_CONCURRENCY_SCHEMA_ID,
        "mode": "bounded_per_lane_workers",
        "global_active_lock": False,
        "same_lane_parallelism": 1,
        "cross_lane_parallelism": "bounded_by_executable_lane_count",
        "executable_lane_count": len(EXECUTABLE_CODEX_WORK_LANES),
        "active_run_count": len(entries),
        "active_lane_count": lane_locks["active_lane_count"],
        "active_lane_ids": [
            lane_id
            for lane_id, lock in lane_locks["locks"].items()
            if isinstance(lock, Mapping) and lock.get("locked")
        ],
        "unknown_lane_active_run_count": lane_locks["unknown_lane_active_run_count"],
        "production_authority": False,
        "live_execution_authority": False,
    }


def _normalize_idempotency_token(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.:-]+", "_", value.strip())[:180]


def _codex_objective_fingerprint(objective: str) -> str:
    normalized = re.sub(r"\s+", " ", objective).strip()
    return hashlib.sha256(normalized.encode("utf-8", errors="replace")).hexdigest()


def _parallel_preview_request(args: Mapping[str, Any] | None) -> tuple[dict[str, Any], str]:
    arguments = dict(args or {})
    for key in ("proposed_request", "request", "work_request"):
        value = arguments.get(key)
        if isinstance(value, Mapping):
            payload = dict(value)
            source = key
            break
    else:
        payload = {
            key: value
            for key, value in arguments.items()
            if key
            not in {
                "request_path",
                "proposed_request",
                "request",
                "work_request",
            }
        }
        source = "args"

    lane_request = str(payload.get("lane_request") or payload.get("lane_id") or "").strip()
    if lane_request and not str(payload.get("lane_id") or "").strip():
        payload["lane_id"] = lane_request
    return payload, source


def _parallel_preview_dedupe_signature(request: Mapping[str, Any]) -> dict[str, Any]:
    objective = str(request.get("objective") or "")
    objective_sha256 = str(request.get("objective_sha256") or "").strip() or _codex_objective_fingerprint(objective)
    explicit_dedupe = str(request.get("dedupe_key") or "").strip()
    if explicit_dedupe:
        return {
            "dedupe_key": explicit_dedupe,
            "idempotency_source": "dedupe_key",
            "implicit_idempotency_key": False,
            "objective_sha256": objective_sha256,
        }
    idempotency_key = str(request.get("idempotency_key") or "").strip()
    if idempotency_key:
        return {
            "dedupe_key": f"idempotency_key:{_normalize_idempotency_token(idempotency_key)}",
            "idempotency_source": "idempotency_key",
            "implicit_idempotency_key": False,
            "objective_sha256": objective_sha256,
        }
    client_request_id = str(request.get("client_request_id") or "").strip()
    if client_request_id:
        return {
            "dedupe_key": f"client_request_id:{_normalize_idempotency_token(client_request_id)}",
            "idempotency_source": "client_request_id",
            "implicit_idempotency_key": False,
            "objective_sha256": objective_sha256,
        }
    return {
        "dedupe_key": f"objective_sha256:{objective_sha256}",
        "idempotency_source": "objective_sha256",
        "implicit_idempotency_key": True,
        "objective_sha256": objective_sha256,
    }


def _scope_values(request: Mapping[str, Any], fields: tuple[str, ...]) -> list[str]:
    values: list[str] = []
    for field in fields:
        raw = request.get(field)
        if raw is None:
            continue
        items = raw if isinstance(raw, list) else [raw]
        for item in items:
            if isinstance(item, Mapping):
                value = item.get("path") or item.get("target") or item.get("raw_path") or item.get("scope")
            else:
                value = item
            text = str(value or "").strip()
            if text:
                values.append(_clean_path_value(text))
    return sorted(dict.fromkeys(values))


def _parallel_preview_read_set(request: Mapping[str, Any]) -> list[str]:
    return _scope_values(
        request,
        (
            "read_set",
            "required_context_reads",
            "context_refs",
            "context_paths",
            "evidence_paths",
        ),
    )


def _parallel_preview_write_set(request: Mapping[str, Any]) -> list[str]:
    return _scope_values(
        request,
        (
            "write_set",
            "planned_writes",
            "planned_write_paths",
            "touched_paths",
            "likely_touched_paths",
            "target_paths",
        ),
    )


def _scope_overlap(left: str, right: str) -> bool:
    left_clean = _clean_path_value(left)
    right_clean = _clean_path_value(right)
    return (
        left_clean == right_clean
        or left_clean.startswith(f"{right_clean}/")
        or right_clean.startswith(f"{left_clean}/")
    )


def _overlap_rows(left: list[str], right: list[str], *, left_label: str, right_label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for left_path in left:
        for right_path in right:
            if _scope_overlap(left_path, right_path):
                rows.append({left_label: left_path, right_label: right_path})
    return rows


def _request_payload_for_rel(root: Path, request_rel: str | None) -> dict[str, Any]:
    if not request_rel:
        return {}
    try:
        request_path = _safe_rel_path(root, request_rel)
        request_path.relative_to((root / CODEX_WORK_REQUESTS_DIR).resolve())
    except (ValueError, RuntimeError):
        return {}
    if not request_path.is_file():
        return {}
    loaded = _read_json(request_path)
    return dict(loaded) if isinstance(loaded, Mapping) else {}


def _parallel_preview_active_runs(root: Path) -> list[dict[str, Any]]:
    state = _read_json(root / RUNNER_STATE_PATH)
    if not isinstance(state, Mapping):
        return []
    rows: list[dict[str, Any]] = []
    for entry in _running_active_run_entries(state):
        request = _request_payload_for_rel(root, str(entry.get("request_path") or ""))
        rows.append(
            {
                "run_id": entry.get("run_id"),
                "pid": entry.get("pid"),
                "run_packet_path": entry.get("run_packet_path"),
                "request_path": entry.get("request_path"),
                "request_id": request.get("request_id"),
                "lane_id": entry.get("lane_id") or classify_codex_work_request_lane(request).get("lane_id"),
                "read_set": _parallel_preview_read_set(request),
                "write_set": _parallel_preview_write_set(request),
                "dedupe_signature": _parallel_preview_dedupe_signature(request) if request else None,
            }
        )
    return rows


def _parallel_preview_existing_matches(root: Path, signature: Mapping[str, Any]) -> list[dict[str, Any]]:
    dedupe_key = str(signature.get("dedupe_key") or "").strip()
    objective_sha256 = str(signature.get("objective_sha256") or "").strip()
    matches: list[dict[str, Any]] = []
    for path in _request_paths(root):
        payload = _load_request(path)
        existing_objective_sha = str(payload.get("objective_sha256") or _codex_objective_fingerprint(str(payload.get("objective") or "")))
        if str(payload.get("dedupe_key") or "").strip() != dedupe_key and existing_objective_sha != objective_sha256:
            continue
        status = str(payload.get("status") or "")
        matches.append(
            {
                "request_id": payload.get("request_id"),
                "path": _connector_rel(path, root),
                "status": status,
                "dedupe_key": payload.get("dedupe_key"),
                "objective_sha256": existing_objective_sha,
                "active_or_terminal": status
                in {
                    "QUEUED_FOR_CODEX_CARRIER",
                    "CLAIMED_BY_CODEX_QUEUE_RUNNER",
                    "CODEX_QUEUE_RUNNER_WORKER_STARTED",
                    "CODEX_CLI_RUNNING",
                    "RETURN_RECORDED_PROOF_ACCEPTED",
                },
            }
        )
    return matches


def _parallel_preview_worker_shift_leases(root: Path) -> list[dict[str, Any]]:
    board_path = root / "ION/05_context/current/worker_shift/ACTIVE_WORKER_SHIFT_BOARD.json"
    board = _read_json(board_path)
    if not isinstance(board, Mapping):
        return []
    leases: list[dict[str, Any]] = []
    for lease in board.get("active_leases") or []:
        if not isinstance(lease, Mapping):
            continue
        leases.append(
            {
                "lease_id": lease.get("lease_id"),
                "worker_id": lease.get("worker_id"),
                "mode": lease.get("mode") or lease.get("lease_type"),
                "lease_type": lease.get("lease_type") or lease.get("mode"),
                "paths": _scope_values(lease, ("paths", "raw_paths")),
            }
        )
    return leases


def _parallel_preview_lane_remap(lane_request: str | None, lane_route: Mapping[str, Any]) -> dict[str, Any]:
    requested = str(lane_request or "").strip()
    resolved = str(lane_route.get("lane_id") or "needs_triage")
    normalized = normalize_codex_work_lane_id(requested) if requested else None
    reason = None
    if requested and normalized == resolved:
        reason = None
    elif requested and not normalized:
        reason = "requested_lane_not_supported"
    elif requested and normalized != resolved:
        reason = "requested_lane_changed_by_route_projection"
    elif not requested:
        reason = f"inferred_from_{lane_route.get('source') or 'unclassified'}"
    return {
        "lane_request": requested or None,
        "lane_request_normalized": normalized,
        "lane_resolved": resolved,
        "lane_remap_reason": reason,
        "lane_remap_evidence": list(lane_route.get("reasons") or []),
        "lane_route": dict(lane_route),
    }


def build_codex_parallel_plan_preview(
    root: str | Path | None = None,
    args: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Project queue lane, dedupe, conflict, and lease decisions without writes."""

    shell_root = _resolve_root(root)
    arguments = dict(args or {})
    request_source = "args"
    request_path = str(arguments.get("request_path") or "").strip()
    if request_path:
        request = _request_payload_for_rel(shell_root, request_path)
        request_source = "request_path" if request else "request_path_unavailable"
    else:
        request, request_source = _parallel_preview_request(arguments)
    lane_request = str(request.get("lane_request") or request.get("lane_id") or "").strip() or None
    if lane_request and not str(request.get("lane_id") or "").strip():
        request["lane_id"] = lane_request
    lane_route = classify_codex_work_request_lane(request)
    lane_projection = _parallel_preview_lane_remap(lane_request, lane_route)
    read_set = _parallel_preview_read_set(request)
    write_set = _parallel_preview_write_set(request)
    authority_class = str(
        request.get("authority_class")
        or ("read_only" if not write_set else request.get("movement_class") or "candidate_write")
    )
    signature = _parallel_preview_dedupe_signature(request)
    existing_matches = _parallel_preview_existing_matches(shell_root, signature)
    active_runs = _parallel_preview_active_runs(shell_root)
    active_same_lane = [
        row for row in active_runs if str(row.get("lane_id") or "") == str(lane_projection["lane_resolved"])
    ]
    active_write_conflicts: list[dict[str, Any]] = []
    active_read_stability_risks: list[dict[str, Any]] = []
    for row in active_runs:
        write_overlaps = _overlap_rows(
            write_set,
            list(row.get("write_set") or []),
            left_label="candidate_write",
            right_label="active_write",
        )
        for overlap in write_overlaps:
            active_write_conflicts.append({**overlap, "active_run": {k: row.get(k) for k in ("run_id", "request_id", "request_path", "lane_id")}})
        read_overlaps = _overlap_rows(
            read_set,
            list(row.get("write_set") or []),
            left_label="candidate_read",
            right_label="active_write",
        )
        for overlap in read_overlaps:
            active_read_stability_risks.append({**overlap, "active_run": {k: row.get(k) for k in ("run_id", "request_id", "request_path", "lane_id")}})

    lease_conflicts: list[dict[str, Any]] = []
    for lease in _parallel_preview_worker_shift_leases(shell_root):
        if str(lease.get("mode") or lease.get("lease_type") or "") == "read":
            continue
        for overlap in _overlap_rows(write_set, list(lease.get("paths") or []), left_label="candidate_write", right_label="lease_path"):
            lease_conflicts.append({**overlap, "lease": lease})

    duplicate_active_matches = [row for row in existing_matches if row.get("active_or_terminal")]
    if duplicate_active_matches:
        decision = "supersede_duplicate_or_reuse_existing"
    elif active_write_conflicts or lease_conflicts:
        decision = "convert_to_read_only_or_queue_after"
    elif active_same_lane:
        decision = "queue_after_same_lane_active"
    elif lane_projection["lane_resolved"] == "needs_triage":
        decision = "needs_triage_before_lease"
    else:
        decision = "allow_parallel"
    lease_type = "read_lease" if not write_set or authority_class == "read_only" else "write_intent_lease"
    if "exclusive" in authority_class:
        lease_type = "exclusive_write_lease"
    return {
        "schema_id": CODEX_PARALLEL_PLAN_PREVIEW_SCHEMA_ID,
        "generated_at": _now(),
        "request_source": request_source,
        "request_path": request_path or None,
        "request_id": request.get("request_id"),
        "objective_sha256": signature["objective_sha256"],
        **lane_projection,
        "dedupe_signature": signature,
        "read_set": read_set,
        "write_set": write_set,
        "authority_class": authority_class,
        "conflict_projection": {
            "active_codex_run_count": len(active_runs),
            "active_same_lane_count": len(active_same_lane),
            "duplicate_match_count": len(existing_matches),
            "duplicate_active_or_terminal_count": len(duplicate_active_matches),
            "write_conflict_count": len(active_write_conflicts) + len(lease_conflicts),
            "read_stability_risk_count": len(active_read_stability_risks),
            "active_runs": active_runs,
            "duplicate_matches": existing_matches,
            "write_conflicts": active_write_conflicts,
            "worker_shift_lease_conflicts": lease_conflicts,
            "read_stability_risks": active_read_stability_risks,
        },
        "lease_decision": {
            "decision": decision,
            "lease_type": lease_type,
            "would_issue_lease": False,
            "would_enqueue": False,
            "worker_process_started": False,
            "projection_only": True,
        },
        "mutates_active_state": False,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
        "secrets_authority": False,
    }


def _codex_queue_worker_id_for_run(run: Mapping[str, Any]) -> str:
    return f"codex_queue_runner:{_safe_unique_slug(str(run.get('run_id') or run.get('request_id') or 'run'))}"


def _codex_queue_lease_id_for_run(run: Mapping[str, Any]) -> str:
    return f"codex_queue_lease:{_safe_unique_slug(str(run.get('run_id') or run.get('request_id') or 'run'))}"


def _codex_queue_run_lease_paths(request: Mapping[str, Any], run: Mapping[str, Any]) -> list[str]:
    control_plane_fields = (
        "request_path",
        "run_packet_path",
        "context_receipt_path",
        "prompt_path",
        "stdout_path",
        "stderr_path",
        "last_message_path",
        "task_return_body_path",
        "worker_context_awareness_receipt_path",
    )
    paths = [
        str(run.get(field) or "").strip()
        for field in control_plane_fields
        if str(run.get(field) or "").strip()
    ]
    paths.extend(_parallel_preview_write_set(request))
    return sorted({_clean_path_value(path) for path in paths if str(path or "").strip()})


def _claim_codex_queue_run_lease(root: Path, run: Mapping[str, Any]) -> dict[str, Any]:
    request_rel = str(run.get("request_path") or "").strip()
    request = _load_request(root / request_rel) if request_rel else {}
    authority_class = str(
        request.get("authority_class")
        or request.get("movement_class")
        or "candidate_write"
    )
    mode = "exclusive_write" if "exclusive" in authority_class else "write"
    paths = _codex_queue_run_lease_paths(request, run)
    preflight = run.get("ai_movement_preflight") if isinstance(run.get("ai_movement_preflight"), Mapping) else {}
    root_envelope = preflight.get("root_envelope") if isinstance(preflight.get("root_envelope"), Mapping) else None
    gate_decision = {
        "schema_id": AI_MOVEMENT_PREFLIGHT_SCHEMA_ID,
        "accepted": bool(preflight.get("accepted")),
        "verdict": preflight.get("verdict"),
        "movement_class": (root_envelope or {}).get("movement_class") if isinstance(root_envelope, Mapping) else None,
        "target_root_id": (root_envelope or {}).get("target_root_id") if isinstance(root_envelope, Mapping) else None,
        "blockers": preflight.get("blockers") if isinstance(preflight.get("blockers"), list) else [],
        "warnings": preflight.get("warnings") if isinstance(preflight.get("warnings"), list) else [],
    }
    worker_id = _codex_queue_worker_id_for_run(run)
    lease_id = _codex_queue_lease_id_for_run(run)
    try:
        from .ion_worker_shift_presence import claim_work_lease

        claim = claim_work_lease(
            worker_id=worker_id,
            lease_id=lease_id,
            paths=paths,
            mode=mode,
            root=root,
            objective=str(request.get("objective") or run.get("request_id") or "").strip() or None,
            packet_id=str(request.get("packet_id") or request.get("work_packet_id") or request.get("request_id") or "").strip() or None,
            branch_id=f"codex_queue:{run.get('lane_id') or 'needs_triage'}",
            ai_movement_envelope=root_envelope,
            ai_movement_gate_decision=gate_decision,
            allow_worker_id_mismatch=True,
        )
    except Exception as exc:
        return {
            "schema_id": "ion.codex_queue_runner_worker_shift_lease.v0_1",
            "ok": False,
            "finding": exc.__class__.__name__,
            "worker_id": worker_id,
            "lease_id": lease_id,
            "mode": mode,
            "paths": paths,
            "shared_coordination_paths_excluded_from_worker_shift_lease": list(CODEX_QUEUE_RUN_SHARED_COORDINATION_PATHS),
            "receipt_path": None,
            "claim_status": "EXCEPTION",
            "production_authority": False,
            "live_execution_authority": False,
        }
    receipt = claim.get("receipt") if isinstance(claim.get("receipt"), Mapping) else {}
    lease = receipt.get("lease") if isinstance(receipt.get("lease"), Mapping) else {}
    claim_status = str(receipt.get("result") or lease.get("status") or "")
    return {
        "schema_id": "ion.codex_queue_runner_worker_shift_lease.v0_1",
        "ok": claim_status == "ACTIVE",
        "finding": None if claim_status == "ACTIVE" else "worker_shift_lease_claim_blocked",
        "worker_id": worker_id,
        "lease_id": lease_id,
        "mode": mode,
        "paths": paths,
        "shared_coordination_paths_excluded_from_worker_shift_lease": list(CODEX_QUEUE_RUN_SHARED_COORDINATION_PATHS),
        "receipt_path": claim.get("receipt_path"),
        "claim_status": claim_status,
        "block_reason_code": lease.get("block_reason_code"),
        "hard_conflict_count": len((receipt.get("conflicts") or {}).get("hard_conflicts") or [])
        if isinstance(receipt.get("conflicts"), Mapping)
        else 0,
        "advisory_conflict_count": len((receipt.get("conflicts") or {}).get("advisory_conflicts") or [])
        if isinstance(receipt.get("conflicts"), Mapping)
        else 0,
        "path_authority": receipt.get("path_authority"),
        "worker_id_authorization": receipt.get("worker_id_authorization"),
        "production_authority": False,
        "live_execution_authority": False,
    }


def _release_codex_queue_run_lease(root: Path, run: dict[str, Any], *, reason: str) -> dict[str, Any] | None:
    if isinstance(run.get("worker_shift_lease_release"), Mapping):
        return dict(run["worker_shift_lease_release"])
    lease = run.get("worker_shift_lease") if isinstance(run.get("worker_shift_lease"), Mapping) else None
    if not lease or not str(lease.get("lease_id") or "").strip():
        return None
    if lease.get("ok") is not True and str(lease.get("claim_status") or "") != "ACTIVE":
        return None
    try:
        from .ion_worker_shift_presence import release_work_lease

        release = release_work_lease(
            root=root,
            worker_id=str(lease.get("worker_id") or "") or None,
            lease_id=str(lease.get("lease_id") or ""),
            reason=reason,
        )
    except Exception as exc:
        summary = {
            "schema_id": "ion.codex_queue_runner_worker_shift_lease_release.v0_1",
            "ok": False,
            "finding": exc.__class__.__name__,
            "lease_id": lease.get("lease_id"),
            "worker_id": lease.get("worker_id"),
            "receipt_path": None,
            "release_result": "EXCEPTION",
            "production_authority": False,
            "live_execution_authority": False,
        }
        run["worker_shift_lease_release"] = summary
        return summary
    receipt = release.get("receipt") if isinstance(release.get("receipt"), Mapping) else {}
    released = receipt.get("released_leases") if isinstance(receipt.get("released_leases"), list) else []
    summary = {
        "schema_id": "ion.codex_queue_runner_worker_shift_lease_release.v0_1",
        "ok": str(receipt.get("result") or "") == "RELEASED",
        "finding": None if str(receipt.get("result") or "") == "RELEASED" else "no_matching_active_lease",
        "lease_id": lease.get("lease_id"),
        "worker_id": lease.get("worker_id"),
        "receipt_path": release.get("receipt_path"),
        "release_result": receipt.get("result"),
        "released_count": len(released),
        "release_reason": reason,
        "production_authority": False,
        "live_execution_authority": False,
    }
    run["worker_shift_lease_release"] = summary
    return summary


def _state_for_active_entries(
    entries: list[dict[str, Any]],
    *,
    latest_run: str | None,
    latest_worker_lifecycle_event: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    latest_active = _latest_active_entry(entries)
    payload: dict[str, Any] = {
        "active_run": latest_active,
        "active_runs": {_active_run_key(row): dict(row) for row in entries if _active_run_key(row)},
        "active_lane_locks": _lane_lock_index(entries),
        "concurrency": _concurrency_summary(entries),
        "latest_run": latest_run,
        "manual_proceed_relay_required": False,
    }
    if latest_worker_lifecycle_event is not None:
        payload["latest_worker_lifecycle_event"] = dict(latest_worker_lifecycle_event)
    return payload


def _current_running_entries_with(root: Path, entry: Mapping[str, Any]) -> list[dict[str, Any]]:
    current_state = _read_json(root / RUNNER_STATE_PATH) or {}
    current_running_entries = _running_active_run_entries(current_state)
    return list(_active_runs_with_entry(current_running_entries, entry).values())


def _current_running_entries_without(root: Path, entry: Mapping[str, Any]) -> list[dict[str, Any]]:
    current_state = _read_json(root / RUNNER_STATE_PATH) or {}
    current_running_entries = _running_active_run_entries(current_state)
    return list(_active_runs_without_entry(current_running_entries, entry).values())


def _active_entry_for_run(run: Mapping[str, Any], *, pid: int | None = None, started_at: str | None = None) -> dict[str, Any]:
    worker_identity = run.get("worker_identity") if isinstance(run.get("worker_identity"), Mapping) else {}
    worker_return_status = run.get("worker_return_status") if isinstance(run.get("worker_return_status"), Mapping) else _worker_return_status_for_run(run)
    entry: dict[str, Any] = {
        "run_id": run.get("run_id"),
        "pid": pid if pid is not None else run.get("pid"),
        "run_packet_path": run.get("run_packet_path"),
        "request_path": run.get("request_path"),
        "lane_id": run.get("lane_id"),
        "domain_id": run.get("domain_id") or worker_identity.get("domain_id"),
        "role_id": run.get("role_id") or worker_identity.get("role_id"),
        "role_tier": run.get("role_tier") or worker_identity.get("role_tier"),
        "callsign": run.get("callsign") or worker_identity.get("callsign"),
        "started_at": started_at or run.get("started_at"),
        "active_root_proof": run.get("active_root_proof"),
        "worker_identity": worker_identity,
        "domain_alignment": run.get("domain_alignment") if isinstance(run.get("domain_alignment"), Mapping) else None,
        "worker_return_status": worker_return_status,
    }
    events = run.get("worker_lifecycle_events")
    if isinstance(events, list) and events:
        entry["latest_worker_lifecycle_event"] = events[-1]
    lease = run.get("worker_shift_lease") if isinstance(run.get("worker_shift_lease"), Mapping) else None
    if lease:
        entry["worker_shift_lease_id"] = lease.get("lease_id")
        entry["worker_shift_lease_receipt_path"] = lease.get("receipt_path")
    return entry


def _latest_files(root: Path, rel: Path, *, limit: int = 5) -> list[dict[str, Any]]:
    base = root / rel
    if not base.exists():
        return []
    paths = sorted((path for path in base.glob("*.json") if path.is_file()), key=lambda path: path.stat().st_mtime, reverse=True)
    return [
        {
            "path": _connector_rel(path, root),
            "name": path.name,
            "mtime": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat(),
        }
        for path in paths[:limit]
    ]


def _latest_run_packets(root: Path, *, limit: int = 5) -> list[dict[str, Any]]:
    base = root / CODEX_QUEUE_RUNS_DIR
    if not base.exists():
        return []
    paths = sorted((path for path in base.rglob("run.json") if path.is_file()), key=lambda path: path.stat().st_mtime, reverse=True)
    runs: list[dict[str, Any]] = []
    for path in paths[:limit]:
        payload = _read_json(path) or {}
        runs.append({
            "path": _connector_rel(path, root),
            "run_id": payload.get("run_id"),
            "request_id": payload.get("request_id"),
            "status": payload.get("status"),
            "mtime": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat(),
        })
    return runs


def _latest_run_packet_rel(root: Path) -> str | None:
    latest = _latest_run_packets(root, limit=1)
    if not latest:
        return None
    rel = str(latest[0].get("path") or "").strip()
    return rel or None


def _compact_finding_codes(items: Any) -> list[str]:
    rows = items if isinstance(items, list) else []
    return sorted({
        str(item.get("code"))
        for item in rows
        if isinstance(item, Mapping) and item.get("code")
    })


def compact_agent_cwd_boundary_projection(boundary: Mapping[str, Any] | None) -> dict[str, Any]:
    """Return the operator-facing subset of an agent cwd boundary receipt."""

    if not isinstance(boundary, Mapping):
        return {
            "schema_id": AGENT_CWD_BOUNDARY_PROJECTION_SCHEMA_ID,
            "status": "MISSING",
            "accepted": None,
            "warning_level": "warning",
            "blocker_count": 0,
            "warning_count": 1,
            "blocker_codes": [],
            "warning_codes": ["AGENT_CWD_BOUNDARY_MISSING"],
            "operator_warning_rows": [
                {
                    "code": "AGENT_CWD_BOUNDARY_MISSING",
                    "severity": "WARNING",
                    "message": "No agent cwd boundary is attached to this preflight; terminal-folder proof is incomplete.",
                }
            ],
            "projection_only": True,
            "queue_processing_started": False,
            "worker_process_started": False,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }

    blockers = boundary.get("blockers") if isinstance(boundary.get("blockers"), list) else []
    warnings = boundary.get("warnings") if isinstance(boundary.get("warnings"), list) else []
    blocker_codes = _compact_finding_codes(blockers)
    warning_codes = _compact_finding_codes(warnings)
    operator_rows: list[dict[str, Any]] = []
    accepted = boundary.get("accepted")
    if accepted is False:
        operator_rows.append(
            {
                "code": "AGENT_CWD_BOUNDARY_BLOCKED",
                "severity": "BLOCKER",
                "message": "Agent cwd boundary blocked worker launch before process creation.",
            }
        )
    for item in blockers:
        if isinstance(item, Mapping):
            operator_rows.append(
                {
                    "code": str(item.get("code") or "AGENT_CWD_BOUNDARY_BLOCKER"),
                    "severity": "BLOCKER",
                    "message": str(item.get("detail") or item.get("message") or item.get("reason") or "Agent cwd boundary blocker."),
                }
            )
    for item in warnings:
        if isinstance(item, Mapping):
            operator_rows.append(
                {
                    "code": str(item.get("code") or "AGENT_CWD_BOUNDARY_WARNING"),
                    "severity": "WARNING",
                    "message": str(item.get("detail") or item.get("message") or item.get("reason") or "Agent cwd boundary warning."),
                }
            )
    if accepted is False:
        warning_level = "blocked"
    elif warning_codes:
        warning_level = "warning"
    elif accepted is True:
        warning_level = "ok"
    else:
        warning_level = "unknown"
    return {
        "schema_id": AGENT_CWD_BOUNDARY_PROJECTION_SCHEMA_ID,
        "status": str(boundary.get("status") or "UNKNOWN"),
        "accepted": accepted if isinstance(accepted, bool) else None,
        "warning_level": warning_level,
        "workspace_root": boundary.get("workspace_root"),
        "active_ion_root": boundary.get("active_ion_root"),
        "control_plane_cwd": boundary.get("control_plane_cwd"),
        "worker_launch_cwd": boundary.get("worker_launch_cwd"),
        "target_command_cwd": boundary.get("target_command_cwd"),
        "target_project_root": boundary.get("target_project_root"),
        "target_content_root": boundary.get("target_content_root"),
        "target_root_id": boundary.get("target_root_id"),
        "target_root_class": boundary.get("target_root_class"),
        "target_root_relation": boundary.get("target_root_relation"),
        "blocker_count": len(blocker_codes),
        "warning_count": len(warning_codes),
        "blocker_codes": blocker_codes,
        "warning_codes": warning_codes,
        "operator_warning_rows": operator_rows,
        "projection_only": True,
        "queue_processing_started": False,
        "worker_process_started": False,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }


def compact_ai_movement_preflight_projection(
    preflight: Mapping[str, Any] | None,
    *,
    source_path: str | None = None,
) -> dict[str, Any]:
    """Return a compact operator-safe projection of queue preflight evidence."""

    if not isinstance(preflight, Mapping):
        return {
            "schema_id": AI_MOVEMENT_PREFLIGHT_PROJECTION_SCHEMA_ID,
            "source_path": source_path,
            "status": "UNKNOWN",
            "accepted": None,
            "warning_level": "unknown",
            "operator_warning_rows": [
                {
                    "code": "AI_MOVEMENT_PREFLIGHT_MISSING",
                    "severity": "WARNING",
                    "message": "No AI movement preflight receipt is available for this row.",
                }
            ],
        }
    decision = preflight.get("gate_decision") if isinstance(preflight.get("gate_decision"), Mapping) else {}
    envelope = preflight.get("root_envelope") if isinstance(preflight.get("root_envelope"), Mapping) else {}
    blockers = decision.get("blockers") if isinstance(decision.get("blockers"), list) else []
    warnings = decision.get("warnings") if isinstance(decision.get("warnings"), list) else []
    accepted = preflight.get("accepted")
    blocker_codes = _compact_finding_codes(blockers)
    warning_codes = _compact_finding_codes(warnings)
    operator_rows: list[dict[str, Any]] = []
    agent_cwd_boundary = (
        envelope.get("agent_cwd_boundary")
        if isinstance(envelope.get("agent_cwd_boundary"), Mapping)
        else None
    )
    agent_cwd_projection = compact_agent_cwd_boundary_projection(agent_cwd_boundary)
    if accepted is False:
        operator_rows.append(
            {
                "code": "AI_MOVEMENT_GATE_BLOCKED",
                "severity": "BLOCKER",
                "message": "AI movement gate blocked runner start before worker process creation.",
            }
        )
    for item in blockers:
        if isinstance(item, Mapping):
            operator_rows.append(
                {
                    "code": str(item.get("code") or "AI_MOVEMENT_GATE_BLOCKER"),
                    "severity": "BLOCKER",
                    "message": str(item.get("detail") or item.get("message") or item.get("reason") or "AI movement blocker."),
                }
            )
    for item in warnings:
        if isinstance(item, Mapping):
            operator_rows.append(
                {
                    "code": str(item.get("code") or "AI_MOVEMENT_GATE_WARNING"),
                    "severity": "WARNING",
                    "message": str(item.get("detail") or item.get("message") or item.get("reason") or "AI movement warning."),
                }
            )
    for item in agent_cwd_projection.get("operator_warning_rows") or []:
        if isinstance(item, Mapping):
            operator_rows.append(dict(item))
    if accepted is False or agent_cwd_projection.get("warning_level") == "blocked":
        warning_level = "blocked"
    elif warning_codes or agent_cwd_projection.get("warning_level") == "warning":
        warning_level = "warning"
    elif accepted is True:
        warning_level = "ok"
    else:
        warning_level = "unknown"
    return {
        "schema_id": AI_MOVEMENT_PREFLIGHT_PROJECTION_SCHEMA_ID,
        "source_path": source_path or preflight.get("receipt_path"),
        "receipt_path": preflight.get("receipt_path"),
        "request_id": preflight.get("request_id"),
        "request_path": preflight.get("request_path"),
        "run_packet_path": preflight.get("run_packet_path"),
        "generated_at": preflight.get("generated_at"),
        "status": str(preflight.get("verdict") or "UNKNOWN"),
        "accepted": accepted if isinstance(accepted, bool) else None,
        "finding": preflight.get("finding"),
        "runner_start_allowed": bool(preflight.get("runner_start_allowed")) if preflight.get("runner_start_allowed") is not None else None,
        "target_root_id": envelope.get("target_root_id") or decision.get("target_root_id"),
        "movement_class": envelope.get("movement_class") or decision.get("movement_class"),
        "root_relation": envelope.get("root_relation") or decision.get("target_root_relation"),
        "target_project_root": envelope.get("target_project_root"),
        "target_content_root": envelope.get("target_content_root"),
        "cwd_boundary_status": agent_cwd_projection.get("status"),
        "worker_launch_cwd": agent_cwd_projection.get("worker_launch_cwd"),
        "target_command_cwd": agent_cwd_projection.get("target_command_cwd"),
        "agent_cwd_boundary_projection": agent_cwd_projection,
        "blocker_count": len(blocker_codes),
        "warning_count": len(warning_codes),
        "blocker_codes": blocker_codes,
        "warning_codes": warning_codes,
        "warning_level": warning_level,
        "operator_warning_rows": operator_rows,
        "worker_process_started": bool(preflight.get("worker_process_started")),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }


def _latest_ai_movement_preflight_projections(root: Path, *, limit: int = 10) -> list[dict[str, Any]]:
    rows: list[tuple[float, dict[str, Any]]] = []
    seen_sources: set[str] = set()
    preflight_root = root / CODEX_QUEUE_PREFLIGHTS_DIR
    if preflight_root.exists():
        for path in preflight_root.glob("*.json"):
            if not path.is_file():
                continue
            payload = _read_json(path)
            rel = _connector_rel(path, root)
            seen_sources.add(rel)
            rows.append((path.stat().st_mtime, compact_ai_movement_preflight_projection(payload, source_path=rel)))
    runs_root = root / CODEX_QUEUE_RUNS_DIR
    if runs_root.exists():
        for path in runs_root.rglob("run.json"):
            if not path.is_file():
                continue
            run = _read_json(path) or {}
            preflight = run.get("ai_movement_preflight") if isinstance(run.get("ai_movement_preflight"), Mapping) else None
            if not preflight:
                continue
            source = str(run.get("ai_movement_preflight_receipt_path") or preflight.get("receipt_path") or _connector_rel(path, root))
            if source in seen_sources:
                continue
            seen_sources.add(source)
            rows.append((path.stat().st_mtime, compact_ai_movement_preflight_projection(preflight, source_path=source)))
    ordered = [row for _, row in sorted(rows, key=lambda item: item[0], reverse=True)]
    return ordered[: max(1, int(limit))]


def build_ai_movement_preflight_warning_map(root: str | Path | None = None, *, limit: int = 10) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    preflights = _latest_ai_movement_preflight_projections(shell_root, limit=limit)
    warning_rows: list[dict[str, Any]] = []
    for preflight in preflights:
        for row in preflight.get("operator_warning_rows") or []:
            if isinstance(row, Mapping):
                warning_rows.append(
                    {
                        **dict(row),
                        "request_id": preflight.get("request_id"),
                        "request_path": preflight.get("request_path"),
                        "receipt_path": preflight.get("receipt_path") or preflight.get("source_path"),
                        "target_root_id": preflight.get("target_root_id"),
                        "movement_class": preflight.get("movement_class"),
                    }
                )
    blocked_count = sum(1 for item in preflights if item.get("accepted") is False)
    accepted_count = sum(1 for item in preflights if item.get("accepted") is True)
    warning_count = sum(1 for item in preflights if item.get("warning_level") == "warning")
    cwd_projections = [
        item.get("agent_cwd_boundary_projection")
        for item in preflights
        if isinstance(item.get("agent_cwd_boundary_projection"), Mapping)
    ]
    cwd_missing_count = sum(1 for item in cwd_projections if item.get("status") == "MISSING")
    cwd_blocked_count = sum(1 for item in cwd_projections if item.get("warning_level") == "blocked")
    cwd_warning_count = sum(1 for item in cwd_projections if item.get("warning_level") == "warning")
    return {
        "schema_id": AI_MOVEMENT_PREFLIGHT_WARNING_MAP_SCHEMA_ID,
        "status": "READ_ONLY_PROJECTION",
        "preflight_receipt_dir": CODEX_QUEUE_PREFLIGHTS_DIR.as_posix(),
        "preflight_count": len(preflights),
        "accepted_count": accepted_count,
        "blocked_count": blocked_count,
        "warning_count": warning_count,
        "agent_cwd_boundary_missing_count": cwd_missing_count,
        "agent_cwd_boundary_blocked_count": cwd_blocked_count,
        "agent_cwd_boundary_warning_count": cwd_warning_count,
        "operator_warning_count": len(warning_rows),
        "latest_preflight": preflights[0] if preflights else None,
        "latest_preflights": preflights,
        "warning_rows": warning_rows,
        "projection_only": True,
        "queue_processing_started": False,
        "worker_process_started": False,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }


def _pid_running(pid: int | None) -> bool:
    if not pid or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    try:
        stat = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return True
    end = stat.rfind(")")
    state = stat[end + 1 :].strip()[:1] if end >= 0 else ""
    return state != "Z"


def _run_output_presence(root: Path, run: Mapping[str, Any]) -> dict[str, bool]:
    return {
        key.replace("_path", "_exists"): bool(run.get(key) and (root / str(run.get(key))).exists())
        for key in ("stdout_path", "stderr_path", "last_message_path")
    }


def _run_has_terminal_output(root: Path, run: Mapping[str, Any]) -> bool:
    for key in ("stdout_path", "stderr_path", "last_message_path"):
        rel = str(run.get(key) or "").strip()
        if not rel:
            continue
        path = root / rel
        try:
            if path.exists() and path.stat().st_size > 0:
                return True
        except OSError:
            continue
    return False


def _parse_iso8601(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _elapsed_seconds(start: datetime | None, end: datetime | None) -> int | None:
    if start is None or end is None:
        return None
    delta = int((end - start).total_seconds())
    return delta if delta >= 0 else None


def _run_start_request_age_seconds(run: Mapping[str, Any], now: datetime) -> int | None:
    started = (
        _parse_iso8601(run.get("started_at"))
        or _parse_iso8601(run.get("updated_at"))
        or _parse_iso8601(run.get("created_at"))
    )
    if started is None:
        return None
    return _elapsed_seconds(started, now)


def _file_meta(root: Path, rel_path: str | None) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "path": rel_path,
        "exists": False,
        "bytes": None,
        "modified_at": None,
        "finding": None,
    }
    if not rel_path:
        return meta
    try:
        target = _safe_rel_path(root, rel_path)
    except ValueError:
        meta["finding"] = "path_not_repo_relative"
        return meta
    if not target.exists() or not target.is_file():
        return meta
    stat = target.stat()
    meta["exists"] = True
    meta["bytes"] = int(stat.st_size)
    meta["modified_at"] = datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0).isoformat()
    return meta


def _latest_event_timestamp(*values: Any) -> str | None:
    latest: datetime | None = None
    for value in values:
        if isinstance(value, str):
            parsed = _parse_iso8601(value)
            if parsed and (latest is None or parsed > latest):
                latest = parsed
        elif isinstance(value, Mapping):
            parsed = _parse_iso8601(value.get("modified_at"))
            if parsed and (latest is None or parsed > latest):
                latest = parsed
    return latest.replace(microsecond=0).isoformat() if latest else None


def _tail_preview(meta: Mapping[str, Any], root: Path, *, max_bytes: int) -> dict[str, Any]:
    rel_path = str(meta.get("path") or "")
    if not rel_path:
        return {"included": False, "finding": "preview_path_missing"}
    try:
        target = _safe_rel_path(root, rel_path)
    except ValueError:
        return {"included": False, "finding": "preview_path_not_repo_relative"}
    if not target.exists() or not target.is_file():
        return {"included": False, "finding": "preview_path_missing"}
    data = target.read_bytes()
    bounded = min(max(int(max_bytes), 1), MAX_LIVE_PREVIEW_BYTES)
    tail = data[-bounded:]
    return {
        "included": True,
        "path": rel_path,
        "bytes": len(data),
        "shown_bytes": len(tail),
        "truncated": len(data) > len(tail),
        "text": tail.decode("utf-8", errors="replace"),
    }


def _artifact_has_content(meta: Mapping[str, Any] | None) -> bool:
    if not isinstance(meta, Mapping) or not meta.get("exists"):
        return False
    try:
        return int(meta.get("bytes") or 0) > 0
    except (TypeError, ValueError):
        return False


def _preferred_worker_preview(
    artifacts: Mapping[str, Mapping[str, Any]],
    root: Path,
    *,
    max_bytes: int,
) -> dict[str, Any]:
    for target in WORKER_TRACE_PREVIEW_PRIORITY:
        meta = artifacts.get(target)
        if _artifact_has_content(meta):
            return {
                "target": target,
                "selected_by": "most_informative_available_artifact",
                **_tail_preview(meta or {}, root, max_bytes=max_bytes),
            }
    for target in WORKER_TRACE_PREVIEW_PRIORITY:
        meta = artifacts.get(target)
        if isinstance(meta, Mapping) and meta.get("exists"):
            return {
                "target": target,
                "selected_by": "first_existing_empty_artifact",
                **_tail_preview(meta, root, max_bytes=max_bytes),
            }
    return {
        "included": False,
        "target": None,
        "selected_by": "none",
        "finding": "no_public_worker_artifact_available",
    }


def _read_bounded_artifact_text(
    root: Path,
    meta: Mapping[str, Any] | None,
    *,
    max_bytes: int = 65536,
) -> str:
    if not isinstance(meta, Mapping):
        return ""
    rel_path = str(meta.get("path") or "")
    if not rel_path:
        return ""
    try:
        target = _safe_rel_path(root, rel_path)
    except ValueError:
        return ""
    if not target.exists() or not target.is_file():
        return ""
    return target.read_bytes()[-max_bytes:].decode("utf-8", errors="replace")


def _looks_like_codex_transient_usage_limit_bug(*texts: str) -> bool:
    combined = "\n".join(str(text or "") for text in texts).lower()
    if "usage limit" not in combined:
        return False
    return any(
        marker in combined
        for marker in (
            "try again at",
            "purchase more credits",
            "upgrade to pro",
            "codex/settings/usage",
        )
    )


def _bounded_usage_limit_excerpt(*texts: str, limit: int = 500) -> str:
    combined = "\n".join(str(text or "") for text in texts).strip()
    return combined[-limit:] if len(combined) > limit else combined


def _combined_codex_attempt_output(attempts: list[str], *, label: str) -> str:
    if not attempts:
        return ""
    if len(attempts) == 1:
        return attempts[0]
    rows: list[str] = []
    for index, text in enumerate(attempts, start=1):
        if index > 1:
            rows.append(f"\n\n--- codex transient retry attempt {index} {label} ---\n")
        rows.append(text)
    return "".join(rows)


def _candidate_session_id_from_value(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if "/" in text or "\\" in text or ".." in text:
        return ""
    if re.match(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{2,127}$", text):
        return text
    return ""


def _extract_codex_session_id_from_text(*texts: str) -> str:
    combined = "\n".join(str(text or "") for text in texts)
    for pattern in (
        r"\b[0-9a-f]{8,}-[0-9a-f]{4,}-[0-9a-f]{4,}-[0-9a-f]{4,}-[0-9a-f]{12,}\b",
        r"(?:session_id|session id|session)\s*[:=]\s*([A-Za-z0-9_.:-]{3,127})",
    ):
        match = re.search(pattern, combined, flags=re.IGNORECASE)
        if not match:
            continue
        candidate = match.group(1) if match.lastindex else match.group(0)
        session_id = _candidate_session_id_from_value(candidate)
        if session_id:
            return session_id
    return ""


def _explicit_codex_resume_session_id(run: Mapping[str, Any]) -> str:
    for key in (
        "codex_resume_session_id",
        "codex_session_id",
        "session_id",
        "saved_session_id",
    ):
        session_id = _candidate_session_id_from_value(run.get(key))
        if session_id:
            return session_id
    for key in ("codex_session", "carrier_session", "saved_session"):
        value = run.get(key)
        if not isinstance(value, Mapping):
            continue
        for nested_key in ("session_id", "id", "resume_session_id"):
            session_id = _candidate_session_id_from_value(value.get(nested_key))
            if session_id:
                return session_id
    return ""


def _latest_matching_codex_session_id(root: Path, run: Mapping[str, Any]) -> str:
    """Best-effort saved-session match for the bounded prompt-through path."""

    try:
        from . import ion_codex_session_store_bridge as session_bridge
    except Exception:
        return ""
    cwd_candidates = {
        str(root.resolve(strict=False)),
        str(Path(str(run.get("worker_launch_cwd") or root)).expanduser().resolve(strict=False)),
        str(Path(str(run.get("target_command_cwd") or run.get("worker_launch_cwd") or root)).expanduser().resolve(strict=False)),
    }
    best: tuple[float, str] | None = None
    try:
        session_files = session_bridge._iter_session_files(limit=80)  # type: ignore[attr-defined]
    except Exception:
        return ""
    for path in session_files:
        try:
            meta = session_bridge._metadata_from_file(path)  # type: ignore[attr-defined]
        except Exception:
            continue
        session_id = _candidate_session_id_from_value(meta.get("session_id"))
        if not session_id:
            continue
        cwd = str((meta.get("session_meta") or {}).get("cwd") or "").strip()
        if cwd:
            cwd = str(Path(cwd).expanduser().resolve(strict=False))
        if cwd and cwd not in cwd_candidates:
            continue
        score = float(path.stat().st_mtime)
        if cwd in cwd_candidates:
            score += 10_000_000_000.0
        if best is None or score > best[0]:
            best = (score, session_id)
    return best[1] if best else ""


def _resolve_codex_prompt_through_session_id(
    root: Path,
    run: Mapping[str, Any],
    *,
    stdout_text: str = "",
    stderr_text: str = "",
) -> dict[str, Any]:
    explicit = _explicit_codex_resume_session_id(run)
    if explicit:
        return {"session_id": explicit, "source": "run_packet_explicit_session_id"}
    extracted = _extract_codex_session_id_from_text(stdout_text, stderr_text)
    if extracted:
        return {"session_id": extracted, "source": "codex_output_excerpt"}
    matched = _latest_matching_codex_session_id(root, run)
    if matched:
        return {"session_id": matched, "source": "latest_matching_codex_session_store_cwd"}
    return {"session_id": "", "source": "not_found"}


def _read_prompt_through_task_output(root: Path, result: Mapping[str, Any]) -> str:
    stdout_rel = str(result.get("stdout_path") or "").strip()
    if stdout_rel:
        stdout_text = _read_rel_text_if_exists(root, stdout_rel) or ""
        if stdout_text.strip():
            return stdout_text
    receipt_rel = str(result.get("receipt_path") or "").strip()
    if not receipt_rel:
        return ""
    try:
        receipt_path = _safe_rel_path(root, receipt_rel)
    except ValueError:
        return ""
    receipt = _read_json(receipt_path)
    if not isinstance(receipt, Mapping):
        return ""
    tail = receipt.get("tail_harvest")
    records = tail.get("records") if isinstance(tail, Mapping) else None
    if not isinstance(records, list):
        return ""
    for item in reversed(records):
        if not isinstance(item, Mapping):
            continue
        role = str(item.get("role") or "").strip()
        payload_type = str(item.get("payload_type") or "").strip()
        text = str(item.get("text") or "").strip()
        if text and (role == "assistant" or payload_type == "agent_message"):
            return text
    return ""


def _read_prompt_through_route_output(root: Path, result: Mapping[str, Any]) -> tuple[str, str]:
    stdout = ""
    stderr = ""
    stdout_rel = str(result.get("stdout_path") or "").strip()
    stderr_rel = str(result.get("stderr_path") or "").strip()
    if stdout_rel:
        stdout = _read_rel_text_if_exists(root, stdout_rel) or ""
    if stderr_rel:
        stderr = _read_rel_text_if_exists(root, stderr_rel) or ""
    return stdout, stderr


def _attempt_codex_usage_limit_prompt_through(
    root: Path,
    run: Mapping[str, Any],
    *,
    stdout_text: str,
    stderr_text: str,
    attempt: int = 1,
) -> dict[str, Any]:
    session_resolution = _resolve_codex_prompt_through_session_id(
        root,
        run,
        stdout_text=stdout_text,
        stderr_text=stderr_text,
    )
    session_id = str(session_resolution.get("session_id") or "")
    if not session_id:
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_PROMPT_THROUGH_SCHEMA_ID,
            "attempted": False,
            "ok": False,
            "finding": "codex_saved_session_not_found_for_prompt_through",
            "session_resolution": session_resolution,
            "prompt": "continue",
            "attempt": attempt,
            "max_attempts": MAX_CODEX_TRANSIENT_USAGE_LIMIT_PROMPT_THROUGH_ATTEMPTS,
            "driver_mode": "tui_inline",
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    try:
        from . import ion_codex_session_store_bridge as session_bridge
    except Exception as exc:
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_PROMPT_THROUGH_SCHEMA_ID,
            "attempted": False,
            "ok": False,
            "finding": "codex_session_store_bridge_unavailable",
            "error": str(exc),
            "session_resolution": session_resolution,
            "prompt": "continue",
            "attempt": attempt,
            "max_attempts": MAX_CODEX_TRANSIENT_USAGE_LIMIT_PROMPT_THROUGH_ATTEMPTS,
            "driver_mode": "tui_inline",
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    idempotency_key = f"{run.get('run_id') or 'codex_run'}:usage-limit-prompt-through-{attempt}"
    prompt_through_timeout = max(
        10,
        min(
            int(run.get("timeout_seconds") or DEFAULT_CODEX_TIMEOUT_SECONDS),
            CODEX_TRANSIENT_USAGE_LIMIT_PROMPT_THROUGH_TIMEOUT_SECONDS,
        ),
    )
    result = session_bridge.invoke_codex_session_store_route(
        root,
        route_id="session_resume_send",
        args={
            "session_id": session_id,
            "prompt": "continue",
            "sandbox_mode": "workspace-write",
            "driver_mode": "tui_inline",
            "idempotency_key": idempotency_key,
            "confirmation": session_bridge.CONFIRMATION_TOKEN,
            "timeout_seconds": prompt_through_timeout,
        },
    )
    route_stdout, route_stderr = _read_prompt_through_route_output(root, result)
    route_output_usage_limit = _looks_like_codex_transient_usage_limit_bug(route_stdout, route_stderr)
    task_output = _read_prompt_through_task_output(root, result) if result.get("ok") else ""
    return {
        "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_PROMPT_THROUGH_SCHEMA_ID,
        "attempted": True,
        "ok": bool(result.get("ok") and task_output.strip()),
        "finding": None
        if result.get("ok") and task_output.strip()
        else "prompt_through_did_not_produce_task_output",
        "session_resolution": session_resolution,
        "prompt": "continue",
        "attempt": attempt,
        "max_attempts": MAX_CODEX_TRANSIENT_USAGE_LIMIT_PROMPT_THROUGH_ATTEMPTS,
        "timeout_seconds": prompt_through_timeout,
        "driver_mode": "tui_inline",
        "route_output_usage_limit_recurred": bool(route_output_usage_limit),
        "route_output_excerpt": _bounded_usage_limit_excerpt(route_stdout, route_stderr)
        if route_output_usage_limit
        else "",
        "route_result": {
            "ok": bool(result.get("ok")),
            "finding": result.get("finding"),
            "returncode": result.get("returncode"),
            "timed_out": result.get("timed_out"),
            "receipt_path": result.get("receipt_path"),
            "stdout_path": result.get("stdout_path"),
            "stderr_path": result.get("stderr_path"),
            "line_count_delta": result.get("line_count_delta"),
            "message_count_delta": result.get("message_count_delta"),
            "driver_mode": result.get("driver_mode"),
            "driver_label": result.get("driver_label"),
        },
        "task_output_sha256": hashlib.sha256(task_output.encode("utf-8", errors="replace")).hexdigest()
        if task_output
        else None,
        "task_output": task_output,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }


def _transient_usage_limit_recovery_projection(
    root: Path,
    run: Mapping[str, Any],
    *,
    request_rel: str | None = None,
) -> dict[str, Any]:
    resolved_request_rel = _clean_path_value(str(request_rel or run.get("request_path") or "").strip())
    run_packet = _clean_path_value(str(run.get("run_packet_path") or "").strip())
    status = str(run.get("status") or "").strip()
    failure = str(run.get("failure_classification") or "").strip()
    request_status = None
    request_recovery_count = 0
    request_bridge_count = 0
    if resolved_request_rel:
        try:
            request_payload = _read_json(_safe_rel_path(root, resolved_request_rel))
        except ValueError:
            request_payload = None
        if isinstance(request_payload, Mapping):
            request_status = str(request_payload.get("status") or "").strip() or None
            request_recovery_count = len([
                item
                for item in (request_payload.get("carrier_session_recovery_history") or [])
                if isinstance(item, Mapping)
            ])
            request_bridge_count = len([
                item
                for item in (request_payload.get("carrier_session_bridge_history") or [])
                if isinstance(item, Mapping)
            ])
    recovery_exhausted = (
        request_recovery_count >= MAX_CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_REQUEUES
        and request_status != "QUEUED_FOR_CODEX_CARRIER"
    )
    eligible = (status == CODEX_TRANSIENT_USAGE_LIMIT_BUG_STATUS or failure == CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS) and not recovery_exhausted
    bridge_required = (
        (status == CODEX_TRANSIENT_USAGE_LIMIT_BUG_STATUS or failure == CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS)
        and recovery_exhausted
    )
    bridge_exhausted = request_bridge_count >= MAX_CODEX_TRANSIENT_USAGE_LIMIT_BRIDGES_PER_REQUEST
    basis = {
        "request_path": resolved_request_rel,
        "source_run_packet_path": run_packet,
        "source_run_status": status,
        "failure_classification": failure,
        "recovery_class": CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS,
    }
    recovery_id = f"codex_carrier_recovery_{_sha256_json_payload(basis)[:24]}"
    return {
        "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_SCHEMA_ID,
        "eligible": bool(eligible and resolved_request_rel and run_packet),
        "recovery_id": recovery_id,
        "recovery_class": CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS,
        "required_confirmation": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_CONFIRMATION,
        "request_path": resolved_request_rel or None,
        "source_run_packet_path": run_packet or None,
        "source_run_status": status or None,
        "source_failure_classification": failure or None,
        "request_status": request_status,
        "request_recovery_count": request_recovery_count,
        "recovery_exhausted": recovery_exhausted,
        "bridge_required": bridge_required,
        "bridge_eligible": bool(bridge_required and not bridge_exhausted),
        "bridge_count": request_bridge_count,
        "bridge_exhausted": bridge_exhausted,
        "recommended_bridge_route": "parent_session_relay" if bridge_required else None,
        "operator_reported_actual_usage_exhausted": False,
        "claim_boundary": "Carrier session recovery only; not authoritative quota state and not product state.",
        "max_requeues_per_request": MAX_CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_REQUEUES,
        "max_bridges_per_request": MAX_CODEX_TRANSIENT_USAGE_LIMIT_BRIDGES_PER_REQUEST,
        "allowed_actions": [
            "requeue_same_request_for_codex_carrier",
            "start_new_queue_run_after_requeue_with_fresh_context_gate_and_worker_shift_lease",
        ],
        "forbidden_actions": [
            "accepted_state_claim",
            "production_or_live_authority_claim",
            "materialization_or_registry_movement",
            "reuse_failed_run_as_success",
            "synthesize_worker_return_from_error_logs",
            "unbounded_retry_loop",
        ],
        "proof_requirements": [
            "source_run_packet_path",
            "source_run_terminal_status",
            "same_request_path",
            "no_active_same_request_worker",
            "fresh_context_active_resolver_on_next_start",
            "fresh_worker_shift_lease_on_next_start",
            "new_run_packet_for_next_attempt",
        ],
        "dedupe_boundary": {
            "same_request_only": True,
            "new_run_required": True,
            "source_run_preserved": True,
            "recovery_id": recovery_id,
        },
        "suggested_start_command": (
            f"PYTHONPATH=ION/04_packages python -m kernel.ion_codex_queue_runner "
            f"--ion-root . --process-once --start --request-path {resolved_request_rel} --json"
            if resolved_request_rel
            else None
        ),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }


def _transient_usage_limit_bridge_projection(
    root: Path,
    run: Mapping[str, Any],
    *,
    request_rel: str | None = None,
    idempotency_key: str | None = None,
    bridge_mode: str = "parent_session_relay",
) -> dict[str, Any]:
    resolved_request_rel = _clean_path_value(str(request_rel or run.get("request_path") or "").strip())
    run_packet = _clean_path_value(str(run.get("run_packet_path") or "").strip())
    status = str(run.get("status") or "").strip()
    failure = str(run.get("failure_classification") or "").strip()
    recovery = _transient_usage_limit_recovery_projection(root, run, request_rel=resolved_request_rel)
    request_payload: dict[str, Any] = {}
    request_status = None
    bridge_history: list[dict[str, Any]] = []
    if resolved_request_rel:
        try:
            loaded = _read_json(_safe_rel_path(root, resolved_request_rel))
        except ValueError:
            loaded = None
        if isinstance(loaded, Mapping):
            request_payload = dict(loaded)
            request_status = str(request_payload.get("status") or "").strip() or None
            bridge_history = [
                dict(item)
                for item in (request_payload.get("carrier_session_bridge_history") or [])
                if isinstance(item, Mapping)
            ]
    state = _read_json(root / RUNNER_STATE_PATH) or {}
    active_same_request = [
        dict(entry)
        for entry in _active_run_entries(state)
        if _clean_path_value(str(entry.get("request_path") or "").strip()) == resolved_request_rel
    ]
    bridge_key = _clean_path_value(str(idempotency_key or "").strip())
    basis = {
        "request_path": resolved_request_rel,
        "source_run_packet_path": run_packet,
        "failure_classification": failure,
        "bridge_mode": bridge_mode,
        "idempotency_key": bridge_key,
    }
    bridge_id = f"codex_carrier_bridge_{_sha256_json_payload(basis)[:24]}"
    already_created = [
        item
        for item in bridge_history
        if str(item.get("bridge_id") or "") == bridge_id
        or (bridge_key and str(item.get("idempotency_key") or "") == bridge_key)
    ]
    bridge_exhausted = (
        len(bridge_history) >= MAX_CODEX_TRANSIENT_USAGE_LIMIT_BRIDGES_PER_REQUEST
        and not already_created
    )
    lineage_failure, lineage_basis = _vanished_no_output_failure_classification(
        root,
        run,
        resolved_request_rel,
    )
    terminal_bug = (
        status == CODEX_TRANSIENT_USAGE_LIMIT_BUG_STATUS
        or failure == CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS
        or (
            status == CODEX_CLI_VANISHED_NO_OUTPUT_STATUS
            and lineage_failure == CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS
        )
    )
    eligible = bool(
        terminal_bug
        and recovery.get("recovery_exhausted") is True
        and resolved_request_rel
        and run_packet
        and request_payload
        and not active_same_request
        and not bridge_exhausted
    )
    blockers: list[str] = []
    if not terminal_bug:
        blockers.append("source_run_not_transient_usage_limit_bug")
    if recovery.get("recovery_exhausted") is not True:
        blockers.append("same_request_recovery_not_exhausted")
    if not resolved_request_rel:
        blockers.append("request_path_missing")
    if not run_packet:
        blockers.append("source_run_packet_path_missing")
    if not request_payload:
        blockers.append("request_unreadable")
    if active_same_request:
        blockers.append("active_same_request_worker_present")
    if bridge_exhausted:
        blockers.append("bridge_cap_exhausted")
    return {
        "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_SCHEMA_ID,
        "eligible": eligible,
        "bridge_id": bridge_id,
        "bridge_mode": bridge_mode,
        "required_confirmation": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_CONFIRMATION,
        "request_path": resolved_request_rel or None,
        "request_status": request_status,
        "source_run_packet_path": run_packet or None,
        "source_run_status": status or None,
        "failure_classification": (
            CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS
            if (
                terminal_bug
                and status == CODEX_CLI_VANISHED_NO_OUTPUT_STATUS
                and lineage_failure == CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS
            )
            else failure or None
        ),
        "source_run_failure_classification": failure or None,
        "lineage_failure_classification_basis": lineage_basis,
        "recovery_exhausted": recovery.get("recovery_exhausted") is True,
        "recovery_count": recovery.get("request_recovery_count"),
        "bridge_count": len(bridge_history),
        "bridge_exhausted": bridge_exhausted,
        "already_created": bool(already_created),
        "existing_bridge_receipt_path": (already_created[0].get("receipt_path") if already_created else None),
        "active_same_request_worker_count": len(active_same_request),
        "active_same_request_workers": active_same_request,
        "same_request_requeue_allowed": False,
        "worker_start_allowed": False,
        "creates_task_return": False,
        "accepted_for_carrier_intake": False,
        "automatic_agent_reaction_proven": False,
        "blockers": blockers,
        "next_recommended_action": "Create parent-session relay bridge" if eligible else "Preserve blocker; bridge creation is not eligible",
        "forbidden_actions": [
            "requeue_same_exhausted_request",
            "synthesize_task_return_from_failed_cli_log",
            "emit_comms_synced_reply_without_accepted_task_return",
            "claim_automatic_agent_reaction",
            "claim_accepted_state",
            "materialize_or_register",
        ],
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
        "secrets_authority": False,
    }


def _vanished_no_output_failure_classification(
    root: Path,
    run: Mapping[str, Any],
    request_rel: str,
) -> tuple[str, dict[str, Any]]:
    """Preserve usage-limit lineage when a recovered Codex session vanishes."""

    request_path_text = _clean_path_value(str(request_rel or run.get("request_path") or "").strip())
    basis = {
        "default_failure_classification": "CODEX_CLI_FAILURE",
        "request_path": request_path_text or None,
        "preserved_from_prior_transient_usage_limit": False,
    }
    candidates = [
        str(run.get("failure_classification") or ""),
        str(run.get("last_failure_classification") or ""),
    ]
    request_payload: Mapping[str, Any] = {}
    if request_path_text:
        try:
            loaded = _read_json(_safe_rel_path(root, request_path_text))
        except ValueError:
            loaded = None
        if isinstance(loaded, Mapping):
            request_payload = loaded
            candidates.extend(
                [
                    str(request_payload.get("failure_classification") or ""),
                    str(request_payload.get("last_failure_classification") or ""),
                ]
            )
            for item in request_payload.get("carrier_session_recovery_history") or []:
                if not isinstance(item, Mapping):
                    continue
                candidates.extend(
                    [
                        str(item.get("recovery_class") or ""),
                        str(item.get("previous_failure_classification") or ""),
                        str(item.get("source_failure_classification") or ""),
                    ]
                )
    if CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS in candidates:
        basis.update(
            {
                "preserved_from_prior_transient_usage_limit": True,
                "prior_failure_classification": CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS,
                "request_recovery_history_count": len(
                    [
                        item
                        for item in request_payload.get("carrier_session_recovery_history", [])
                        if isinstance(item, Mapping)
                    ]
                )
                if request_payload
                else 0,
                "bridge_route_may_be_eligible_after_recovery_exhaustion": True,
            }
        )
        return CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS, basis
    return "CODEX_CLI_FAILURE", basis


def preview_codex_transient_usage_limit_bridge(
    root: str | Path | None = None,
    *,
    run_packet_path: str,
    idempotency_key: str | None = None,
    bridge_mode: str = "parent_session_relay",
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    clean_run_rel = _clean_path_value(str(run_packet_path or "").strip())
    if not clean_run_rel:
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_SCHEMA_ID,
            "ok": False,
            "result": "RUN_PACKET_PATH_REQUIRED",
            "mutates_active_state": False,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        }
    try:
        run_path = _safe_rel_path(shell_root, clean_run_rel)
    except ValueError:
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_SCHEMA_ID,
            "ok": False,
            "result": "RUN_PACKET_PATH_OUTSIDE_ROOT",
            "run_packet_path": clean_run_rel,
            "mutates_active_state": False,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        }
    run = _read_json(run_path)
    if not isinstance(run, Mapping):
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_SCHEMA_ID,
            "ok": False,
            "result": "RUN_PACKET_UNREADABLE",
            "run_packet_path": clean_run_rel,
            "mutates_active_state": False,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        }
    projection = _transient_usage_limit_bridge_projection(
        shell_root,
        run,
        request_rel=str(run.get("request_path") or ""),
        idempotency_key=idempotency_key,
        bridge_mode=bridge_mode,
    )
    return {
        "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_SCHEMA_ID,
        "ok": True,
        "result": "CODEX_CARRIER_TRANSIENT_USAGE_LIMIT_BRIDGE_PREVIEW",
        "run_packet_path": clean_run_rel,
        "carrier_session_bridge": projection,
        "would_create_bridge": bool(projection.get("eligible")),
        "mutates_active_state": False,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
        "secrets_authority": False,
    }


def _objective_summary(root: Path, request_rel: str | None) -> dict[str, Any]:
    if not request_rel:
        return {"request_path": None, "summary": None, "objective_sha256": None, "finding": "request_path_missing"}
    try:
        request_path = _safe_rel_path(root, request_rel)
    except ValueError:
        return {"request_path": request_rel, "summary": None, "objective_sha256": None, "finding": "request_path_not_repo_relative"}
    request = _read_json(request_path)
    if not isinstance(request, dict):
        return {"request_path": request_rel, "summary": None, "objective_sha256": None, "finding": "request_json_missing_or_invalid"}
    objective = str(request.get("objective") or "")
    summary = next((line.strip() for line in objective.splitlines() if line.strip()), "")
    return {
        "request_path": request_rel,
        "summary": summary[:280] or None,
        "objective_sha256": request.get("objective_sha256") or hashlib.sha256(objective.encode("utf-8", errors="replace")).hexdigest(),
        "requested_model": request.get("requested_model"),
        "requested_reasoning_effort": request.get("requested_reasoning_effort"),
        "status": request.get("status"),
    }


def _extract_section_lines(text: str, section_name: str) -> list[str]:
    lines: list[str] = []
    capture = False
    wanted = section_name.strip().lower()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("### "):
            if capture:
                break
            capture = stripped.lower() == wanted
            continue
        if capture:
            lines.append(line)
    return lines


def _looks_like_repo_path(value: str) -> bool:
    cleaned = value.strip().strip("`").strip()
    if not cleaned or cleaned.startswith(("-", "#")):
        return False
    return cleaned.startswith((".codex/", "ION/", "docs/", "browser_extension/", "../Needs_Routed/")) or "/" in cleaned


def _extract_touched_paths(return_text: str) -> list[str]:
    paths: list[str] = []
    capture_touched = False
    for line in return_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("### ") and capture_touched:
            break
        if stripped.lower().startswith("touched_paths"):
            capture_touched = True
            continue
        if not capture_touched:
            continue
        match = re.match(r"[-*]\s+(.+?)\s*$", stripped)
        if match:
            candidate = match.group(1).strip().strip("`")
            if _looks_like_repo_path(candidate) and candidate not in paths:
                paths.append(candidate)
    if not paths:
        for line in _extract_section_lines(return_text, "### WORKLOAD DIFF"):
            match = re.match(r"\s*[-*]\s+(.+?)\s*$", line)
            if match:
                candidate = match.group(1).strip().strip("`")
                if _looks_like_repo_path(candidate) and candidate not in paths:
                    paths.append(candidate)
    return paths[:50]


def _extract_test_summaries(return_text: str) -> list[str]:
    rows: list[str] = []
    for line in return_text.splitlines():
        stripped = line.strip().strip("-").strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if (
            re.search(r"\b\d+\s+passed\b", lowered)
            or "pytest" in lowered
            or "py_compile" in lowered
            or "smoke" in lowered and ("passed" in lowered or "ok" in lowered)
        ):
            rows.append(stripped[:280])
    return rows[:16]


def _extract_error_summaries(log_text: str) -> list[str]:
    rows: list[str] = []
    for line in log_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if "error" in lowered or "exception" in lowered or "traceback" in lowered or "modulenotfounderror" in lowered:
            rows.append(stripped[:280])
    return rows[-10:]


def _worker_trace_snapshot_rel(run: Mapping[str, Any]) -> str | None:
    existing = str(run.get("worker_trace_snapshot_path") or "").strip()
    if existing:
        return existing
    run_dir = str(run.get("run_dir") or "").strip()
    if run_dir:
        return f"{run_dir.rstrip('/')}/worker_trace_snapshot.json"
    run_packet = str(run.get("run_packet_path") or "").strip()
    if run_packet:
        return (Path(run_packet).parent / "worker_trace_snapshot.json").as_posix()
    return None


def _next_worker_action(
    *,
    phase_status: str,
    run_status: str,
    terminal_intake_state: str,
    artifacts: Mapping[str, Mapping[str, Any]],
    failure_classification: str | None,
) -> str:
    if phase_status == "active":
        return "Continue monitoring lifecycle events and bounded artifact tails."
    if terminal_intake_state == "accepted":
        return "Route the accepted return through the normal receipt/settlement lane."
    if terminal_intake_state == "template_invalid":
        return "Repair the return contract, especially context/template proof and workload diff sections."
    if terminal_intake_state == "blocked":
        return "Inspect proof-gate blocker fields and compile the next repair packet."
    if failure_classification:
        if failure_classification == CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS:
            return (
                "Use the confirmed carrier-session recovery lane to requeue the same request with preserved proof; "
                "the next attempt must create a new run, fresh context gate, and fresh worker-shift lease."
            )
        if _artifact_has_content(artifacts.get("latest_return")):
            return "Inspect latest_return plus failure logs; usable work may exist despite terminal failure."
        return "Inspect worker stderr/stdout and rerun only after the failure class is understood."
    if run_status:
        return "Review run packet and artifact timestamps before starting new queue work."
    return "No active worker trace is available; inspect the queued work list."


def build_codex_worker_observability_trace(
    root: str | Path | None = None,
    *,
    run: Mapping[str, Any] | None = None,
    run_rel: str | None = None,
    phase_status: str | None = None,
    terminal_intake_state: str | None = None,
    active_process_running: bool | None = None,
    elapsed_seconds: int | None = None,
    include_previews: bool = True,
    preview_max_bytes: int = DEFAULT_LIVE_PREVIEW_BYTES,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    loaded_run: dict[str, Any] = dict(run or {})
    resolved_run_rel = str(run_rel or loaded_run.get("run_packet_path") or "").strip()
    if not loaded_run and resolved_run_rel:
        payload = _read_json(shell_root / resolved_run_rel)
        if isinstance(payload, dict):
            loaded_run = payload
    run_dir = str(loaded_run.get("run_dir") or "")
    worker_stdout_path = f"{run_dir}/worker_stdout.log" if run_dir else None
    worker_stderr_path = f"{run_dir}/worker_stderr.log" if run_dir else None
    artifacts: dict[str, dict[str, Any]] = {
        "run_packet": _file_meta(shell_root, resolved_run_rel or None),
        "prompt": _file_meta(shell_root, str(loaded_run.get("prompt_path") or "") or None),
        "context_receipt": _file_meta(shell_root, str(loaded_run.get("context_receipt_path") or "") or None),
        "worker_context_awareness_receipt": _file_meta(shell_root, str(loaded_run.get("worker_context_awareness_receipt_path") or "") or None),
        "stdout": _file_meta(shell_root, str(loaded_run.get("stdout_path") or "") or None),
        "stderr": _file_meta(shell_root, str(loaded_run.get("stderr_path") or "") or None),
        "latest_return": _file_meta(shell_root, str(loaded_run.get("last_message_path") or "") or None),
        "worker_stdout": _file_meta(shell_root, worker_stdout_path),
        "worker_stderr": _file_meta(shell_root, worker_stderr_path),
    }
    snapshot_rel = _worker_trace_snapshot_rel(loaded_run)
    snapshot_meta = _file_meta(shell_root, snapshot_rel)
    request_rel = str(loaded_run.get("request_path") or "")
    request_summary = _objective_summary(shell_root, request_rel or None)
    model_move = loaded_run.get("codex_model_move") if isinstance(loaded_run.get("codex_model_move"), Mapping) else {}
    submit = loaded_run.get("submit_result") if isinstance(loaded_run.get("submit_result"), Mapping) else {}
    lifecycle = list(loaded_run.get("worker_lifecycle_events") or [])[-MAX_WORKER_LIFECYCLE_EVENTS:]
    latest_event = lifecycle[-1] if lifecycle and isinstance(lifecycle[-1], Mapping) else None
    return_text = _read_bounded_artifact_text(shell_root, artifacts["latest_return"])
    stderr_text = _read_bounded_artifact_text(shell_root, artifacts["stderr"], max_bytes=32768)
    worker_stderr_text = _read_bounded_artifact_text(shell_root, artifacts["worker_stderr"], max_bytes=32768)
    preferred_preview = _preferred_worker_preview(artifacts, shell_root, max_bytes=preview_max_bytes)
    previews = {}
    if include_previews:
        previews = {
            key: _tail_preview(artifacts[key], shell_root, max_bytes=preview_max_bytes)
            for key in WORKER_TRACE_PREVIEW_PRIORITY
        }
    observed_terminal_state = str((latest_event or {}).get("terminal_state") or "")
    observed_terminal_intake = terminal_intake_state or "not-completed"
    run_status = str(loaded_run.get("status") or "")
    observed_phase = phase_status or ("terminal" if run_status in TERMINAL_RUN_STATUSES else ("active" if active_process_running else "idle"))
    failure_classification = str(loaded_run.get("failure_classification") or "") or None
    daemon_reconciliation = loaded_run.get("daemon_reconciliation") if isinstance(loaded_run.get("daemon_reconciliation"), Mapping) else {}
    next_action = _next_worker_action(
        phase_status=observed_phase,
        run_status=run_status,
        terminal_intake_state=observed_terminal_intake,
        artifacts=artifacts,
        failure_classification=failure_classification,
    )
    carrier_session_recovery = _transient_usage_limit_recovery_projection(
        shell_root,
        loaded_run,
        request_rel=request_rel,
    )
    if carrier_session_recovery.get("recovery_exhausted"):
        next_action = (
            "Do not requeue this request again; carrier-session recovery is exhausted. "
            "Route a session bridge or alternate worker launch repair packet before further Codex CLI worker execution."
        )
    carrier_session_bridge = _transient_usage_limit_bridge_projection(
        shell_root,
        loaded_run,
        request_rel=request_rel,
    )
    return {
        "schema_id": WORKER_TRACE_SCHEMA_ID,
        "generated_at": _now(),
        "run": {
            "run_id": loaded_run.get("run_id"),
            "request_id": loaded_run.get("request_id"),
            "run_status": run_status or None,
            "phase_status": observed_phase,
            "pid": loaded_run.get("pid"),
            "active_process_running": bool(active_process_running),
            "started_at": loaded_run.get("started_at"),
            "completed_at": loaded_run.get("completed_at"),
            "elapsed_seconds": elapsed_seconds,
            "failure_classification": failure_classification,
        },
        "objective": request_summary,
        "active_root_proof": loaded_run.get("active_root_proof") if isinstance(loaded_run.get("active_root_proof"), Mapping) else _active_root_proof(shell_root),
        "worker_identity": loaded_run.get("worker_identity") if isinstance(loaded_run.get("worker_identity"), Mapping) else {},
        "domain_alignment": loaded_run.get("domain_alignment") if isinstance(loaded_run.get("domain_alignment"), Mapping) else {},
        "worker_return_status": loaded_run.get("worker_return_status") if isinstance(loaded_run.get("worker_return_status"), Mapping) else _worker_return_status_for_run(loaded_run),
        "model": {
            "selected_model": model_move.get("selected_model"),
            "selected_reasoning_effort": model_move.get("selected_reasoning_effort"),
            "work_class": model_move.get("work_class"),
            "usage_pool_id": model_move.get("usage_pool_id"),
            "model_move_id": model_move.get("model_move_id"),
            "summary": loaded_run.get("codex_model_move_summary"),
        },
        "commands": {
            "codex_command_preview": list(loaded_run.get("codex_command") or [])[:16],
            "worker_command_preview": list(loaded_run.get("worker_command") or [])[:16],
            "shell_expansion_allowed": False,
            "arbitrary_shell_exposed": False,
        },
        "context": {
            "prompt_path": loaded_run.get("prompt_path"),
            "run_packet_path": resolved_run_rel or loaded_run.get("run_packet_path"),
            "context_receipt_path": loaded_run.get("context_receipt_path"),
            "worker_context_awareness_receipt_path": loaded_run.get("worker_context_awareness_receipt_path"),
            "worker_sign_in_status": (latest_event or {}).get("worker_sign_in_status"),
        },
        "lifecycle": {
            "events": lifecycle,
            "latest_event": latest_event,
            "terminal_state": observed_terminal_state or None,
            "last_heartbeat_or_artifact_at": _latest_event_timestamp(
                loaded_run.get("updated_at"),
                artifacts["run_packet"],
                artifacts["stdout"],
                artifacts["stderr"],
                artifacts["latest_return"],
                artifacts["worker_stdout"],
                artifacts["worker_stderr"],
            ),
            "artifact_update_times": {
                key: value.get("modified_at")
                for key, value in artifacts.items()
                if value.get("modified_at")
            },
        },
        "artifacts": {
            "metadata": artifacts,
            "preferred_preview": preferred_preview,
            "previews": previews,
            "preview_policy": {
                "max_preview_bytes": min(max(int(preview_max_bytes), 1), MAX_LIVE_PREVIEW_BYTES),
                "public_artifact_targets": list(WORKER_TRACE_PREVIEW_PRIORITY),
                "bounded_tails_only": True,
            },
        },
        "proof": {
            "terminal_intake_state": observed_terminal_intake,
            "accepted_for_carrier_intake": submit.get("accepted_for_carrier_intake"),
            "context_proof_accepted": submit.get("context_proof_accepted"),
            "template_action_proof_accepted": submit.get("template_action_proof_accepted"),
            "return_template_valid": submit.get("return_template_valid"),
            "workload_diff_required": submit.get("workload_diff_required"),
            "workload_diff_present": submit.get("workload_diff_present"),
            "workload_diff_accepted": submit.get("workload_diff_accepted"),
            "task_return_packet_path": submit.get("packet_path"),
        },
        "operational_summary": {
            "touched_paths": _extract_touched_paths(return_text),
            "test_summaries": _extract_test_summaries(return_text),
            "error_summaries": _extract_error_summaries(stderr_text + "\n" + worker_stderr_text),
            "latest_return_has_content": _artifact_has_content(artifacts["latest_return"]),
        },
        "blocker": {
            "failure_classification": failure_classification,
            "daemon_reconciliation_reason": daemon_reconciliation.get("reason"),
            "daemon_reconciliation_output_presence": daemon_reconciliation.get("output_presence"),
        },
        "next_recommended_action": next_action,
        "carrier_session_recovery": carrier_session_recovery,
        "carrier_session_bridge": carrier_session_bridge,
        "durable_trace": {
            "live_projection": run_status not in TERMINAL_RUN_STATUSES,
            "snapshot_path": snapshot_rel,
            "snapshot_exists": bool(snapshot_meta.get("exists")),
            "snapshot_modified_at": snapshot_meta.get("modified_at"),
            "snapshot_write_policy": "terminal workers are snapshotted by runner write paths; read tools do not mutate state",
        },
        "chain_of_thought_policy": {
            "hidden_model_chain_of_thought_requested": False,
            "hidden_model_chain_of_thought_exposed": False,
            "operational_artifacts_only": True,
        },
        "production_authority": False,
        "live_execution_authority": False,
    }


def _write_worker_trace_snapshot(root: Path, run: Mapping[str, Any]) -> str | None:
    snapshot_rel = _worker_trace_snapshot_rel(run)
    if not snapshot_rel:
        return None
    try:
        snapshot_path = _safe_rel_path(root, snapshot_rel)
    except ValueError:
        return None
    trace = build_codex_worker_observability_trace(
        root,
        run=run,
        run_rel=str(run.get("run_packet_path") or ""),
        phase_status="terminal" if str(run.get("status") or "") in TERMINAL_RUN_STATUSES else None,
        terminal_intake_state=None,
        active_process_running=False,
        include_previews=True,
    )
    trace["durable_trace"]["snapshot_write_state"] = "snapshot_written"
    trace["durable_trace"]["snapshot_written_at"] = _now()
    trace["durable_trace"]["snapshot_exists"] = True
    _write_json(snapshot_path, trace)
    return snapshot_rel


def _build_live_worker_telemetry(
    root: Path,
    *,
    state: Mapping[str, Any],
    active: Mapping[str, Any] | None,
    active_pid: int | None,
    active_running: bool,
    stale_active_run_detected: bool,
    queued_request_count: int,
    include_preview: bool,
    preview_target: str | None,
    preview_max_bytes: int,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    run_rel = ""
    if active and isinstance(active.get("run_packet_path"), str):
        run_rel = str(active.get("run_packet_path") or "")
    if not run_rel:
        run_rel = str(state.get("latest_run") or "")
    if not run_rel:
        run_rel = _latest_run_packet_rel(root) or ""
    run: dict[str, Any] = {}
    if run_rel:
        run_path = root / run_rel
        loaded = _read_json(run_path)
        if isinstance(loaded, dict):
            run = loaded

    run_status = str(run.get("status") or "")
    run_dir = str(run.get("run_dir") or "")
    worker_stdout_path = f"{run_dir}/worker_stdout.log" if run_dir else None
    worker_stderr_path = f"{run_dir}/worker_stderr.log" if run_dir else None
    artifacts = {
        "run_packet": _file_meta(root, run_rel or None),
        "stdout": _file_meta(root, str(run.get("stdout_path") or "") or None),
        "stderr": _file_meta(root, str(run.get("stderr_path") or "") or None),
        "latest_return": _file_meta(root, str(run.get("last_message_path") or "") or None),
        "worker_context_awareness_receipt": _file_meta(root, str(run.get("worker_context_awareness_receipt_path") or "") or None),
        "worker_stdout": _file_meta(root, worker_stdout_path),
        "worker_stderr": _file_meta(root, worker_stderr_path),
    }
    awareness_receipt_rel = str(run.get("worker_context_awareness_receipt_path") or "")
    awareness_receipt = _read_json(root / awareness_receipt_rel) if awareness_receipt_rel else None
    awareness_status = None
    awareness_machine_attestation_sha256 = None
    if isinstance(awareness_receipt, Mapping):
        awareness_status = str(awareness_receipt.get("status") or "") or None
        awareness_machine_attestation_sha256 = str(awareness_receipt.get("machine_attestation_sha256") or "") or None

    run_pid = int(run.get("pid")) if run.get("pid") else None
    run_process_running = _pid_running(run_pid)
    worker_running = active_running or run_process_running
    start_request_age_seconds = (
        _run_start_request_age_seconds(run, now)
        if run_status in START_REQUESTED_RUN_STATUSES
        else None
    )

    phase_status = "idle"
    if run_status == START_NO_RECEIPT_STATUS:
        phase_status = "start_no_receipt"
    elif stale_active_run_detected:
        phase_status = "stale-active-reference"
    elif worker_running:
        phase_status = "active"
    elif run_status == "CLAIMED_BY_CODEX_QUEUE_RUNNER":
        if start_request_age_seconds is not None and start_request_age_seconds >= START_NO_RECEIPT_GRACE_SECONDS:
            phase_status = "start_no_receipt"
        else:
            phase_status = "start_requested"
    elif run_status == "CODEX_QUEUE_RUNNER_WORKER_STARTED":
        phase_status = "start_no_receipt"
    elif run_status == "PREPARED_NOT_STARTED":
        phase_status = "prepared-not-started"
    elif run_status == "RETURN_RECORDED_PROOF_ACCEPTED":
        phase_status = "terminal-accepted"
    elif run_status == "RETURN_RECORDED_PROOF_BLOCKED":
        phase_status = "terminal-blocked"
    elif run_status == "RETURN_TEMPLATE_INVALID":
        phase_status = "template-invalid"
    elif run_status in TERMINAL_FAILED_STATUSES:
        phase_status = "terminal-failed"
    elif queued_request_count > 0:
        phase_status = "idle"

    started_at = _parse_iso8601(run.get("started_at")) or _parse_iso8601((active or {}).get("started_at"))
    completed_at = _parse_iso8601(run.get("completed_at"))
    elapsed = _elapsed_seconds(started_at, completed_at or now)

    submit = run.get("submit_result") if isinstance(run.get("submit_result"), Mapping) else {}
    accepted_for_intake = submit.get("accepted_for_carrier_intake")
    terminal_intake_state = "not-completed"
    if run_status == "RETURN_RECORDED_PROOF_ACCEPTED" or accepted_for_intake is True:
        terminal_intake_state = "accepted"
    elif run_status == "RETURN_TEMPLATE_INVALID":
        terminal_intake_state = "template_invalid"
    elif run_status == "RETURN_RECORDED_PROOF_BLOCKED" or accepted_for_intake is False:
        terminal_intake_state = "blocked"
    elif run_status in TERMINAL_FAILED_STATUSES:
        terminal_intake_state = "failed"

    proof_checks = {
        "context_receipt_exists": _file_meta(root, str(run.get("context_receipt_path") or "") or None).get("exists"),
        "worker_context_awareness_receipt_exists": artifacts["worker_context_awareness_receipt"].get("exists"),
        "request_path_exists": _file_meta(root, str(run.get("request_path") or "") or None).get("exists"),
        "latest_return_exists": artifacts["latest_return"].get("exists"),
        "submit_result_present": bool(submit),
    }

    preview: dict[str, Any] = {"requested": bool(include_preview), "included": False}
    if include_preview:
        target = str(preview_target or "").strip()
        if target not in LIVE_PREVIEW_TARGETS:
            if target:
                preview["finding"] = "preview_target_not_allowed_public_log_only"
            else:
                preview = {
                    "requested": True,
                    **_preferred_worker_preview(artifacts, root, max_bytes=preview_max_bytes),
                }
        elif not run:
            preview["finding"] = "preview_unavailable_no_run_packet"
        else:
            preview = {
                "requested": True,
                "target": target,
                **_tail_preview(artifacts[target], root, max_bytes=preview_max_bytes),
            }

    trace = build_codex_worker_observability_trace(
        root,
        run=run,
        run_rel=run_rel or None,
        phase_status=phase_status,
        terminal_intake_state=terminal_intake_state,
        active_process_running=worker_running,
        elapsed_seconds=elapsed,
        include_previews=include_preview,
        preview_max_bytes=preview_max_bytes,
    )
    ai_movement_preflight = (
        run.get("ai_movement_preflight")
        if isinstance(run.get("ai_movement_preflight"), Mapping)
        else None
    )

    return {
        "schema_id": "ion.codex_worker_live_status.v1",
        "phase_status": phase_status,
        "run_status": run_status or None,
        "worker_lifecycle_events": list(run.get("worker_lifecycle_events") or [])[-MAX_WORKER_LIFECYCLE_EVENTS:],
        "latest_worker_lifecycle_event": (list(run.get("worker_lifecycle_events") or [])[-1] if run.get("worker_lifecycle_events") else None),
        "active_worker_pid": active_pid if active_running else (run_pid if run_process_running else None),
        "active_run_id": run.get("run_id") or (active or {}).get("run_id"),
        "request_id": run.get("request_id") or (active or {}).get("request_id"),
        "request_path": run.get("request_path") or (active or {}).get("request_path"),
        "run_packet_path": run_rel or None,
        "active_root_proof": run.get("active_root_proof") if isinstance(run.get("active_root_proof"), Mapping) else _active_root_proof(root),
        "worker_identity": run.get("worker_identity") if isinstance(run.get("worker_identity"), Mapping) else (active or {}).get("worker_identity"),
        "domain_alignment": run.get("domain_alignment") if isinstance(run.get("domain_alignment"), Mapping) else (active or {}).get("domain_alignment"),
        "worker_return_status": run.get("worker_return_status") if isinstance(run.get("worker_return_status"), Mapping) else _worker_return_status_for_run(run),
        "elapsed_seconds": elapsed,
        "start_request_age_seconds": start_request_age_seconds,
        "start_no_receipt_grace_seconds": START_NO_RECEIPT_GRACE_SECONDS,
        "active_process_running": worker_running,
        "stale_active_reference_detected": stale_active_run_detected,
        "worker_sign_in_status": awareness_status,
        "worker_context_awareness_receipt_path": awareness_receipt_rel or None,
        "worker_context_awareness_receipt_sha256": _sha256_for_rel_path(root, awareness_receipt_rel or None),
        "worker_context_awareness_machine_attestation_sha256": awareness_machine_attestation_sha256,
        "proof_gate_preflight": {
            "determinable": bool(run),
            "checks": proof_checks,
            "context_proof_accepted": submit.get("context_proof_accepted"),
            "template_action_proof_accepted": submit.get("template_action_proof_accepted"),
        },
        "ai_movement_gate_preflight": compact_ai_movement_preflight_projection(
            ai_movement_preflight,
            source_path=str(run.get("ai_movement_preflight_receipt_path") or "") or None,
        ),
        "terminal_intake_result": {
            "state": terminal_intake_state,
            "accepted_for_carrier_intake": accepted_for_intake if isinstance(accepted_for_intake, bool) else None,
            "context_proof_accepted": submit.get("context_proof_accepted"),
            "template_action_proof_accepted": submit.get("template_action_proof_accepted"),
            "packet_path": submit.get("packet_path"),
        },
        "artifacts": artifacts,
        "last_heartbeat_or_event_at": _latest_event_timestamp(
            state.get("updated_at"),
            run.get("updated_at"),
            artifacts["run_packet"],
            artifacts["stdout"],
            artifacts["stderr"],
            artifacts["latest_return"],
            artifacts["worker_stdout"],
            artifacts["worker_stderr"],
        ),
        "preview": preview,
        "preferred_preview": trace.get("artifacts", {}).get("preferred_preview") if isinstance(trace.get("artifacts"), Mapping) else None,
        "observability_trace": trace,
    }


def _refresh_codex_work_queue_index(root: Path) -> dict[str, Any]:
    from .ion_chatgpt_browser_mcp_connector_contract import call_chatgpt_connector_tool

    result = call_chatgpt_connector_tool(root, "ion_codex_work_queue", {"limit": 100})
    queue = dict(result.get("data") or {})
    _write_json(root / CODEX_WORK_QUEUE_INDEX, queue)
    materialize_codex_work_lane_index(root)
    return queue


def build_codex_queue_runner_status(
    root: str | Path | None = None,
    *,
    reconcile: bool = True,
    include_preview: bool = False,
    preview_target: str | None = None,
    preview_max_bytes: int = DEFAULT_LIVE_PREVIEW_BYTES,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    reconciliation = reconcile_codex_queue_runner_state(shell_root, write=True) if reconcile else {
        "schema_id": "ion.codex_queue_runner_reconciliation.v1",
        "ok": True,
        "write": False,
        "action": "not_requested",
    }
    state = _read_json(shell_root / RUNNER_STATE_PATH) or {}
    active_entries = _running_active_run_entries(state)
    active = active_entries[0] if active_entries else (
        state.get("active_run") if isinstance(state.get("active_run"), dict) else None
    )
    active_pid = int(active.get("pid")) if active and active.get("pid") else None
    active_running = bool(active_entries) or _pid_running(active_pid)
    queued = _queued_request_paths(shell_root)
    lane_index = materialize_codex_work_lane_index(shell_root)
    lane_locks = _lane_lock_index(active_entries)
    concurrency = _concurrency_summary(active_entries)
    ai_movement_warning_map = build_ai_movement_preflight_warning_map(shell_root, limit=10)
    live_worker = _build_live_worker_telemetry(
        shell_root,
        state=state,
        active=active,
        active_pid=active_pid,
        active_running=active_running,
        stale_active_run_detected=bool(reconciliation.get("stale_active_run_detected")),
        queued_request_count=len(queued),
        include_preview=include_preview,
        preview_target=preview_target,
        preview_max_bytes=preview_max_bytes,
    )
    return {
        "schema_id": SCHEMA_ID,
        "verdict": READY_VERDICT,
        "runner_state_path": RUNNER_STATE_PATH.as_posix(),
        "queue_path": CODEX_WORK_QUEUE_INDEX.as_posix(),
        "queued_request_count": len(queued),
        "next_request_path": _connector_rel(queued[0], shell_root) if queued else None,
        "lane_queue_path": (CODEX_WORK_LANES_DIR / "INDEX.json").as_posix(),
        "lane_queue": {k: v for k, v in lane_index.items() if k != "lanes"},
        "active_run": active,
        "active_runs": active_entries,
        "active_run_count": len(active_entries),
        "active_lane_locks": lane_locks,
        "concurrency": concurrency,
        "active_process_running": active_running,
        "stale_active_run_detected": bool(reconciliation.get("stale_active_run_detected")),
        "reconciliation": reconciliation,
        "live_worker_telemetry": live_worker,
        "latest_runs": _latest_run_packets(shell_root, limit=5),
        "ai_movement_preflight_warning_map": ai_movement_warning_map,
        "failure_classes": list(FAILURE_CLASSES),
        "manual_proceed_relay_required": False,
        "automation_surface": "ion_codex_queue_process_once",
        "autorun_loop_state": "NOT_STARTED_PROCESS_ONCE_AVAILABLE",
        "production_authority": False,
        "live_execution_authority": False,
    }


def _context_receipt_for_request(root: Path, request_rel: str, request: Mapping[str, Any] | None = None) -> dict[str, Any]:
    request_context_reads: list[str] = []
    if request:
        for item in request.get("required_context_reads") or []:
            if isinstance(item, Mapping):
                path = str(item.get("path") or "").strip()
            else:
                path = str(item or "").strip()
            if path:
                request_context_reads.append(path)
    paths = [request_rel, *request_context_reads, *DEFAULT_CONTEXT_READS]
    ordered: list[str] = []
    seen: set[str] = set()
    for path in paths:
        if path not in seen:
            ordered.append(path)
            seen.add(path)
    observed_rows = [_observe_context_path(root, path, required=True) for path in ordered]
    required_missing = [row["path"] for row in observed_rows if row.get("required") and row.get("status") != "READY"]
    attestation_fields = {
        "request_path": request_rel,
        "required_context_reads": [
            {
                "path": row.get("path"),
                "required": bool(row.get("required")),
                "status": row.get("status"),
                "sha256": row.get("sha256"),
            }
            for row in observed_rows
        ],
    }
    return {
        "schema_id": "ion.context_load_receipt.v1",
        "generated_by": "runner_or_control_plane",
        "worker_authored": False,
        "request_path": request_rel,
        "generated_at": _now(),
        "required_context_reads": observed_rows,
        "all_required_context_present": not required_missing,
        "missing_required_context_paths": required_missing,
        "machine_attestation_sha256": _sha256_json_payload(attestation_fields),
    }


def _workspace_manifest_for_root(root: Path) -> Path:
    local = root / "ION_WORKSPACE_MANIFEST.yaml"
    if local.exists():
        return local
    return root.parent / "ION_WORKSPACE_MANIFEST.yaml"


def _target_project_subpath(request: Mapping[str, Any]) -> str:
    for field in AI_MOVEMENT_REQUEST_PROJECT_SUBPATH_FIELDS:
        value = _clean_path_value(str(request.get(field) or "").strip())
        if value and value != ".":
            return value.lstrip("/")
    return ""


def _target_root_path(root: Path, target_root_id: str, request: Mapping[str, Any]) -> Path:
    absolute = str(request.get("target_project_root") or "").strip()
    if absolute:
        return Path(absolute).expanduser().resolve(strict=False)
    if target_root_id == "active_ion_control":
        return root.resolve(strict=False)
    family = str((AI_MOVEMENT_TARGETS.get(target_root_id) or {}).get("family") or "")
    base = (root.parent / family).resolve(strict=False)
    subpath = _target_project_subpath(request)
    if subpath and target_root_id not in {"ion_exports_local"}:
        return (base / subpath).resolve(strict=False)
    return base


def _target_content_root_path(root: Path, target_root_id: str, request: Mapping[str, Any]) -> Path:
    absolute = str(request.get("target_content_root") or "").strip()
    if absolute:
        return Path(absolute).expanduser().resolve(strict=False)
    project_root = _target_root_path(root, target_root_id, request)
    meta = AI_MOVEMENT_TARGETS.get(target_root_id) or {}
    content_subpath = str(meta.get("content_subpath") or "").strip()
    if content_subpath:
        return (project_root / content_subpath).resolve(strict=False)
    return project_root


def _workspace_prefixed_path(
    root: Path,
    target_root_id: str,
    request: Mapping[str, Any],
    path_value: str,
) -> str:
    clean = _clean_path_value(path_value)
    path = Path(clean).expanduser()
    if path.is_absolute():
        return str(path.resolve(strict=False))
    while clean.startswith("../"):
        clean = clean[3:]
    if clean.startswith("ION/"):
        return clean
    known_families = {str(meta["family"]) for meta in AI_MOVEMENT_TARGETS.values()}
    if clean.split("/", 1)[0] in known_families:
        return clean
    if target_root_id == "active_ion_control":
        return clean
    family = str((AI_MOVEMENT_TARGETS.get(target_root_id) or {}).get("family") or "")
    subpath = _target_project_subpath(request)
    prefix = "/".join(part for part in (family, subpath) if part)
    return f"{prefix}/{clean}".strip("/")


def _movement_planned_writes(
    root: Path,
    request: Mapping[str, Any],
    *,
    target_root_id: str,
    control_plane_write_paths: list[str],
) -> tuple[list[str], list[str]]:
    raw_paths = _request_path_values(request, AI_MOVEMENT_REQUEST_WRITE_FIELDS)
    if target_root_id == "active_ion_control":
        raw_paths = [*control_plane_write_paths, *raw_paths]
    normalized: list[str] = []
    seen: set[str] = set()
    for path in raw_paths:
        clean = _workspace_prefixed_path(root, target_root_id, request, path)
        if clean not in seen:
            normalized.append(clean)
            seen.add(clean)
    return normalized, [_clean_path_value(path) for path in control_plane_write_paths]


def _movement_planned_artifacts(root: Path, request: Mapping[str, Any], *, target_root_id: str) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for path in _request_path_values(request, AI_MOVEMENT_REQUEST_ARTIFACT_FIELDS):
        clean = _workspace_prefixed_path(root, target_root_id, request, path)
        if clean not in seen:
            normalized.append(clean)
            seen.add(clean)
    return normalized


def _request_requested_authority(request: Mapping[str, Any]) -> dict[str, bool]:
    raw = request.get("requested_authority") if isinstance(request.get("requested_authority"), Mapping) else {}
    return {
        "production_authority": bool(raw.get("production_authority") or request.get("production_authority")),
        "live_execution_authority": bool(raw.get("live_execution_authority") or request.get("live_execution_authority")),
        "accepted_state_claim": bool(raw.get("accepted_state_claim") or request.get("accepted_state_claim")),
        "git_push_authority": bool(raw.get("git_push_authority") or request.get("git_push_authority")),
        "deletion_authority": bool(raw.get("deletion_authority") or request.get("deletion_authority")),
        "service_restart_authority": bool(raw.get("service_restart_authority") or request.get("service_restart_authority")),
    }


def _request_declared_ai_movement_envelope(request: Mapping[str, Any]) -> dict[str, Any]:
    raw = request.get("ai_movement_root_envelope")
    if not isinstance(raw, Mapping):
        raw = request.get("ai_movement")
    if not isinstance(raw, Mapping):
        return {}
    nested = raw.get("ai_movement_root_envelope")
    if isinstance(nested, Mapping):
        return dict(nested)
    return dict(raw)


def _repo_rel_or_abs(root: Path, path: Path) -> str:
    resolved = path.expanduser().resolve(strict=False)
    try:
        return resolved.relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return str(resolved)


def _is_path_within(path: Path, parent: Path) -> bool:
    resolved = path.expanduser().resolve(strict=False)
    parent_resolved = parent.expanduser().resolve(strict=False)
    return resolved == parent_resolved or parent_resolved in resolved.parents


def _iter_nested_request_values(
    request: Mapping[str, Any],
    fields: tuple[str, ...],
) -> list[tuple[str, Any]]:
    rows: list[tuple[str, Any]] = []
    containers: list[tuple[str, Mapping[str, Any]]] = [("request", request)]
    for key in (
        "route_metadata",
        "agent_invocation",
        "ion_agent_invocation",
        "target_agent",
        "agent_identity",
        "context_system",
        "working_capsule_identity",
    ):
        value = request.get(key)
        if isinstance(value, Mapping):
            containers.append((f"request.{key}", value))
    for prefix, container in containers:
        for field in fields:
            if field in container:
                rows.append((f"{prefix}.{field}", container.get(field)))
    return rows


def _normalize_dotted_identity(value: Any, *, prefix: str) -> str:
    if value is None:
        return ""
    if isinstance(value, Mapping):
        keys = (
            f"{prefix}_id",
            f"{prefix}_role_id",
            "role_id",
            "agent_role_id",
            "agent_role",
            "id",
            "display_name",
            "name",
        ) if prefix == "role" else (
            f"{prefix}_id",
            "domain_id",
            "target_domain_id",
            "route_domain_id",
            "id",
            "display_name",
            "name",
        )
        for key in keys:
            normalized = _normalize_dotted_identity(value.get(key), prefix=prefix)
            if normalized:
                return normalized
        return ""
    text = str(value or "").strip()
    if not text:
        return ""
    existing = re.search(rf"{re.escape(prefix)}\.[a-z0-9_]+", text.lower())
    if existing:
        return existing.group(0)
    normalized = _normalized_lane_source(text)
    if not normalized:
        return ""
    if normalized.startswith(f"{prefix}."):
        return normalized
    if normalized.startswith(f"{prefix}_"):
        normalized = normalized[len(prefix) + 1 :]
    return f"{prefix}.{normalized}"


def _request_agent_role_identity(request: Mapping[str, Any]) -> dict[str, str]:
    for source, value in _iter_nested_request_values(request, AGENT_ROLE_REQUEST_FIELDS):
        role_id = _normalize_dotted_identity(value, prefix="role")
        if role_id:
            return {"agent_role_id": role_id, "source": source}
    text = _request_text_for_lane(request)
    match = re.search(r"role\.[a-z0-9_]+", text)
    if match:
        return {"agent_role_id": match.group(0), "source": "request.text"}
    return {"agent_role_id": "", "source": ""}


def _request_domain_identity(request: Mapping[str, Any]) -> dict[str, str]:
    for source, value in _iter_nested_request_values(request, DOMAIN_REQUEST_FIELDS):
        domain_id = _normalize_dotted_identity(value, prefix="domain")
        if domain_id:
            return {"domain_id": domain_id, "source": source}
    text = _request_text_for_lane(request)
    match = re.search(r"domain\.[a-z0-9_]+", text)
    if match:
        return {"domain_id": match.group(0), "source": "request.text"}
    return {"domain_id": "", "source": ""}


def _request_declared_identity_value(request: Mapping[str, Any], fields: tuple[str, ...]) -> dict[str, str]:
    for source, value in _iter_nested_request_values(request, fields):
        text = str(value or "").strip()
        if text:
            return {"value": text, "source": source}
    return {"value": "", "source": ""}


def _worker_identity_for_request(
    request: Mapping[str, Any],
    *,
    lane_id: str | None = None,
    lane_route: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    role_identity = _request_agent_role_identity(request)
    domain_identity = _request_domain_identity(request)
    role_tier = _request_declared_identity_value(request, ROLE_TIER_REQUEST_FIELDS)
    callsign = _request_declared_identity_value(request, CALLSIGN_REQUEST_FIELDS)
    resolved_lane = normalize_codex_work_lane_id(lane_id) if lane_id else None
    if not resolved_lane and isinstance(lane_route, Mapping):
        resolved_lane = normalize_codex_work_lane_id(str(lane_route.get("lane_id") or "")) or str(lane_route.get("lane_id") or "")
    if not resolved_lane:
        classified = classify_codex_work_request_lane(request)
        resolved_lane = str(classified.get("lane_id") or "").strip() or None
        lane_route = classified
    return {
        "schema_id": "ion.codex_queue_runner.worker_identity.v0_1_candidate",
        "lane_id": resolved_lane,
        "lane_source": (lane_route or {}).get("source") if isinstance(lane_route, Mapping) else None,
        "domain_id": domain_identity.get("domain_id") or None,
        "domain_source": domain_identity.get("source") or None,
        "role_id": role_identity.get("agent_role_id") or None,
        "role_source": role_identity.get("source") or None,
        "role_tier": role_tier.get("value") or None,
        "role_tier_source": role_tier.get("source") or None,
        "callsign": callsign.get("value") or None,
        "callsign_source": callsign.get("source") or None,
        "identity_authority": "carrier_declared_candidate_only",
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def _worker_domain_alignment(target_domain_id: str | None) -> dict[str, Any]:
    target = str(target_domain_id or "").strip()
    return {
        "schema_id": "ion.codex_queue_runner.worker_domain_alignment.v0_1_candidate",
        "resolver_service_domain_id": DOMAIN_WEAVER_CONTEXT_ACTIVE_RESOLVER_DOMAIN_ID,
        "target_request_domain_id": target or None,
        "prestart_domain_checked": target or None,
        "queue_runner_domain_source": "request_payload",
        "uses_resolver_service_domain_as_target": target == DOMAIN_WEAVER_CONTEXT_ACTIVE_RESOLVER_DOMAIN_ID,
        "finding": "target_request_domain_checked" if target else "target_request_domain_missing",
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _declared_codex_agent_mount_path(
    root: Path,
    *,
    request: Mapping[str, Any],
    declared: Mapping[str, Any],
) -> Path | None:
    mount_root = (root / CODEX_AGENT_MOUNT_ROOT).resolve(strict=False)
    raw_values = [
        declared.get("worker_launch_cwd"),
        declared.get("target_command_cwd"),
        declared.get("codex_agent_mount_manifest"),
        declared.get("ion_codex_agent_mount_manifest"),
        declared.get("codex_agent_mount_path"),
        request.get("codex_agent_mount_manifest"),
        request.get("codex_agent_mount_path"),
        request.get("domain_context_package"),
    ]
    for value in raw_values:
        text = str(value or "").strip()
        if not text:
            continue
        path = Path(text).expanduser()
        if not path.is_absolute():
            path = root / path
        resolved = path.resolve(strict=False)
        candidate = resolved.parent if resolved.name == CODEX_AGENT_MOUNT_MANIFEST_NAME else resolved
        if candidate.name == CODEX_AGENT_MOUNT_PORTABLE_CONTEXT_DIR:
            candidate = candidate.parent
        if _is_path_within(candidate, mount_root) and candidate != mount_root:
            return candidate
    mount_id = str(declared.get("codex_agent_mount_id") or request.get("codex_agent_mount_id") or "").strip()
    if mount_id:
        clean_mount_id = mount_id.strip().strip("/")
        if clean_mount_id and "/" not in clean_mount_id and ".." not in Path(clean_mount_id).parts:
            candidate = (mount_root / clean_mount_id).resolve(strict=False)
            if _is_path_within(candidate, mount_root):
                return candidate
        candidate = (mount_root / _safe_slug(mount_id)).resolve(strict=False)
        if _is_path_within(candidate, mount_root):
            return candidate
    return None


def _mount_manifest_identity(mount_path: Path) -> dict[str, str]:
    manifest = mount_path / CODEX_AGENT_MOUNT_MANIFEST_NAME
    if not manifest.is_file():
        return {}
    try:
        loaded = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(loaded, Mapping):
        return {}
    return {
        "agent_role_id": str(loaded.get("agent_role_id") or "").strip(),
        "domain_id": str(loaded.get("domain_id") or "").strip(),
        "mount_id": str(loaded.get("mount_id") or mount_path.name).strip(),
    }


def _codex_agent_mount_status(root: Path, mount_path: Path) -> dict[str, Any]:
    missing: list[dict[str, str]] = []
    paths: dict[str, str] = {}
    for label, rel in CODEX_AGENT_MOUNT_REQUIRED_FILES.items():
        path = mount_path / rel
        paths[label] = _repo_rel_or_abs(root, path)
        if not path.is_file():
            missing.append({"label": label, "path": _repo_rel_or_abs(root, path)})
    return {
        "mount_id": mount_path.name,
        "mount_path": _repo_rel_or_abs(root, mount_path),
        "mount_abspath": str(mount_path.resolve(strict=False)),
        "manifest_path": _repo_rel_or_abs(root, mount_path / CODEX_AGENT_MOUNT_MANIFEST_NAME),
        "context_ready": not missing,
        "missing_required_files": missing,
        "required_files": paths,
        **_mount_manifest_identity(mount_path),
    }


def _selected_mount_resolution(
    root: Path,
    *,
    role_identity: Mapping[str, str],
    domain_identity: Mapping[str, str],
    selected: Mapping[str, Any],
    source: str,
) -> dict[str, Any]:
    mount_path = Path(str(selected.get("mount_abspath") or root / str(selected.get("mount_path") or ""))).resolve(strict=False)
    manifest_path = mount_path / CODEX_AGENT_MOUNT_MANIFEST_NAME
    portable_dir = mount_path / CODEX_AGENT_MOUNT_PORTABLE_CONTEXT_DIR
    role_id = str(selected.get("agent_role_id") or role_identity.get("agent_role_id") or "").strip()
    domain_id = str(selected.get("domain_id") or domain_identity.get("domain_id") or "").strip()
    required_reads = [
        manifest_path,
        mount_path / "AGENTS.md",
        mount_path / ".codex/config.toml",
        portable_dir / CODEX_AGENT_MOUNT_PORTABLE_CONTEXT_MANIFEST,
        portable_dir / CODEX_AGENT_MOUNT_PORTABLE_CAPSULE,
        portable_dir / CODEX_AGENT_MOUNT_ACTIVE_CONTEXT_PACKAGE_MD,
    ]
    return {
        "schema_id": CODEX_AGENT_MOUNT_RESOLUTION_SCHEMA_ID,
        "required": True,
        "accepted": True,
        "status": "CODEX_AGENT_MOUNT_RESOLVED",
        "source": source,
        "agent_role_id": role_id,
        "agent_role_source": role_identity.get("source"),
        "domain_id": domain_id,
        "domain_source": domain_identity.get("source"),
        "mount_id": str(selected.get("mount_id") or mount_path.name),
        "mount_path": _repo_rel_or_abs(root, mount_path),
        "mount_abspath": str(mount_path),
        "codex_agent_mount_manifest": str(manifest_path),
        "worker_launch_cwd": str(mount_path),
        "target_command_cwd": str(mount_path),
        "domain_context_package": _repo_rel_or_abs(root, mount_path),
        "portable_context_dir": _repo_rel_or_abs(root, portable_dir),
        "portable_context_manifest_path": _repo_rel_or_abs(root, portable_dir / CODEX_AGENT_MOUNT_PORTABLE_CONTEXT_MANIFEST),
        "portable_capsule_path": _repo_rel_or_abs(root, portable_dir / CODEX_AGENT_MOUNT_PORTABLE_CAPSULE),
        "portable_active_context_package_path": _repo_rel_or_abs(root, portable_dir / CODEX_AGENT_MOUNT_ACTIVE_CONTEXT_PACKAGE_MD),
        "required_read_paths": [_repo_rel_or_abs(root, path) for path in required_reads],
        "blockers": [],
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }


def _blocked_mount_resolution(
    *,
    role_identity: Mapping[str, str],
    domain_identity: Mapping[str, str],
    status: str,
    code: str,
    detail: str,
    candidates: list[Mapping[str, Any]] | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    blocker = {"code": code, "detail": detail}
    if extra:
        blocker.update(dict(extra))
    return {
        "schema_id": CODEX_AGENT_MOUNT_RESOLUTION_SCHEMA_ID,
        "required": True,
        "accepted": False,
        "status": status,
        "agent_role_id": role_identity.get("agent_role_id"),
        "agent_role_source": role_identity.get("source"),
        "domain_id": domain_identity.get("domain_id"),
        "domain_source": domain_identity.get("source"),
        "candidate_count": len(candidates or []),
        "candidates": list(candidates or []),
        "blockers": [blocker],
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }


def _codex_agent_mount_resolution_for_request(
    root: Path,
    *,
    request: Mapping[str, Any],
    declared: Mapping[str, Any],
    target_root_id: str,
) -> dict[str, Any]:
    declared_mount = _declared_codex_agent_mount_path(root, request=request, declared=declared)
    role_identity = _request_agent_role_identity(request)
    domain_identity = _request_domain_identity(request)
    if declared_mount is not None:
        manifest_identity = _mount_manifest_identity(declared_mount)
        if manifest_identity.get("agent_role_id") and not role_identity.get("agent_role_id"):
            role_identity = {"agent_role_id": str(manifest_identity["agent_role_id"]), "source": "declared_mount_manifest"}
        if manifest_identity.get("domain_id") and not domain_identity.get("domain_id"):
            domain_identity = {"domain_id": str(manifest_identity["domain_id"]), "source": "declared_mount_manifest"}
    if target_root_id != "active_ion_control" and declared_mount is None:
        return {
            "schema_id": CODEX_AGENT_MOUNT_RESOLUTION_SCHEMA_ID,
            "required": False,
            "accepted": True,
            "status": "CODEX_AGENT_MOUNT_NOT_REQUIRED_FOR_TARGET_ROOT",
            "target_root_id": target_root_id,
        }
    if not role_identity.get("agent_role_id") and declared_mount is None:
        return {
            "schema_id": CODEX_AGENT_MOUNT_RESOLUTION_SCHEMA_ID,
            "required": False,
            "accepted": True,
            "status": "NO_AGENT_ROLE_DECLARED",
            "target_root_id": target_root_id,
        }

    mount_root = (root / CODEX_AGENT_MOUNT_ROOT).resolve(strict=False)
    role_id = str(role_identity.get("agent_role_id") or "").strip()
    domain_id = str(domain_identity.get("domain_id") or "").strip()
    candidates: list[dict[str, Any]] = []
    source = "agent_role_domain"
    if declared_mount is not None:
        candidates = [_codex_agent_mount_status(root, declared_mount)]
        source = "declared_codex_agent_mount"
    elif role_id and domain_id:
        mount_path = mount_root / f"{_safe_slug(role_id)}__{_safe_slug(domain_id)}"
        if mount_path.is_dir():
            candidates = [_codex_agent_mount_status(root, mount_path)]
        else:
            return _blocked_mount_resolution(
                role_identity=role_identity,
                domain_identity=domain_identity,
                status="CODEX_AGENT_MOUNT_NOT_FOUND",
                code="CODEX_AGENT_MOUNT_NOT_FOUND",
                detail="Declared agent role/domain has no generated Codex agent mount; runner will not fall back to shared codex_solo.",
                extra={"expected_mount_path": _repo_rel_or_abs(root, mount_path)},
            )
    elif role_id:
        candidates = [
            _codex_agent_mount_status(root, path)
            for path in sorted(mount_root.glob(f"{_safe_slug(role_id)}__*"))
            if path.is_dir()
        ]

    if not candidates:
        return _blocked_mount_resolution(
            role_identity=role_identity,
            domain_identity=domain_identity,
            status="CODEX_AGENT_MOUNT_NOT_FOUND",
            code="CODEX_AGENT_MOUNT_NOT_FOUND",
            detail="Agent role was declared but no generated Codex agent mount exists; runner will not fall back to shared codex_solo.",
        )
    ready = [row for row in candidates if row.get("context_ready")]
    if len(ready) == 1:
        return _selected_mount_resolution(
            root,
            role_identity=role_identity,
            domain_identity=domain_identity,
            selected=ready[0],
            source=source,
        )
    if not ready:
        return _blocked_mount_resolution(
            role_identity=role_identity,
            domain_identity=domain_identity,
            status="CODEX_AGENT_MOUNT_CONTEXT_MISSING",
            code="CODEX_AGENT_MOUNT_CONTEXT_MISSING",
            detail="Generated Codex agent mount lacks required folder-local .ion context; runner will not fall back to shared codex_solo.",
            candidates=candidates,
        )
    return _blocked_mount_resolution(
        role_identity=role_identity,
        domain_identity=domain_identity,
        status="CODEX_AGENT_MOUNT_AMBIGUOUS",
        code="CODEX_AGENT_MOUNT_AMBIGUOUS",
        detail="Agent role resolves to multiple context-ready mounts without a domain; request must bind domain_id explicitly.",
        candidates=ready,
    )


def _ai_movement_root_envelope_for_request(
    root: Path,
    *,
    request: Mapping[str, Any],
    request_rel: str,
    run_packet_rel: str,
    planned_write_paths: list[str],
    planned_artifact_paths: list[str] | None = None,
) -> dict[str, Any]:
    request_context_reads: list[str] = []
    for item in request.get("required_context_reads") or []:
        if isinstance(item, Mapping):
            path = str(item.get("path") or "").strip()
        else:
            path = str(item or "").strip()
        if path:
            request_context_reads.append(path)
    planned_reads = [request_rel, *request_context_reads, *DEFAULT_CONTEXT_READS]
    ordered_reads: list[str] = []
    seen_reads: set[str] = set()
    for path in planned_reads:
        clean = _clean_path_value(path)
        if clean not in seen_reads:
            ordered_reads.append(clean)
            seen_reads.add(clean)

    target_root_resolution = _request_target_root_resolution(request)
    target_root_id = str(target_root_resolution.get("target_root_id") or "active_ion_control")
    movement_class = _movement_class_for_target_root(request, target_root_id)
    target_project_root = _target_root_path(root, target_root_id, request)
    target_content_root = _target_content_root_path(root, target_root_id, request)
    planned_writes, control_plane_writes = _movement_planned_writes(
        root,
        request,
        target_root_id=target_root_id,
        control_plane_write_paths=planned_write_paths,
    )
    planned_artifacts = _movement_planned_artifacts(root, request, target_root_id=target_root_id)
    if planned_artifact_paths:
        for path in planned_artifact_paths:
            clean = _workspace_prefixed_path(root, target_root_id, request, path)
            if clean not in planned_artifacts:
                planned_artifacts.append(clean)

    declared = _request_declared_ai_movement_envelope(request)
    agent_mount_resolution = _codex_agent_mount_resolution_for_request(
        root,
        request=request,
        declared=declared,
        target_root_id=target_root_id,
    )
    for path in agent_mount_resolution.get("required_read_paths") or []:
        clean = _clean_path_value(str(path))
        if clean and clean not in seen_reads:
            ordered_reads.append(clean)
            seen_reads.add(clean)
    domain_context_package = (
        request.get("domain_context_package")
        or agent_mount_resolution.get("domain_context_package")
        or "ION/05_context/current/codex_solo"
    )
    default_envelope: dict[str, Any] = {
        "schema_id": "ion.ai_movement_root_envelope.v1",
        "workspace_root": str(root.parent.resolve(strict=False)),
        "active_ion_root": str(root.resolve(strict=False)),
        "control_plane_cwd": str(root.resolve(strict=False)),
        "control_plane_realpath": str(root.resolve(strict=False)),
        "actual_cwd": str(root.resolve(strict=False)),
        "actual_realpath": str(root.resolve(strict=False)),
        "expected_cwd": str(root.resolve(strict=False)),
        "expected_realpath": str(root.resolve(strict=False)),
        "target_root_id": target_root_id,
        "target_root_resolution": target_root_resolution,
        "legacy_target_policy": target_root_resolution,
        "target_project_root": str(target_project_root),
        "target_content_root": str(target_content_root),
        "root_relation": str((AI_MOVEMENT_TARGETS.get(target_root_id) or {}).get("root_relation") or "active_ion_control_root"),
        "movement_class": movement_class,
        "domain_context_package": str(domain_context_package),
        "active_template": str(request.get("active_template") or "ION/07_templates/carriers/CODEX_CLI_EXECUTION_PACKET.md"),
        "requested_authority": _request_requested_authority(request),
        "planned_reads": ordered_reads,
        "planned_writes": planned_writes,
        "planned_artifacts": planned_artifacts,
        "control_plane_receipt_writes": control_plane_writes,
        "settlement_target": str(request.get("settlement_target") or run_packet_rel),
        "receipt_paths": [
            "ION/05_context/current/worker_shift/signons/**",
            "ION/05_context/current/worker_shift/leases/**",
            "ION/05_context/current/worker_shift/signoffs/**",
            "ION/05_context/current/chatgpt_connector/codex_queue_preflights/**",
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/**/context_receipt.json",
            "ION/05_context/current/chatgpt_connector/codex_queue_runs/**/worker_context_awareness_receipt.json",
        ],
    }
    for key, value in declared.items():
        if value not in (None, "", [], {}):
            default_envelope[key] = value
    default_envelope["codex_agent_mount_resolution"] = agent_mount_resolution
    if agent_mount_resolution.get("required") and agent_mount_resolution.get("accepted"):
        for key in (
            "worker_launch_cwd",
            "target_command_cwd",
            "codex_agent_mount_manifest",
            "domain_context_package",
        ):
            value = agent_mount_resolution.get(key)
            if value not in (None, "", [], {}):
                default_envelope[key] = value
        default_envelope["codex_agent_mount_id"] = agent_mount_resolution.get("mount_id")
    agent_cwd_boundary = build_agent_cwd_boundary(
        default_envelope,
        active_root=root,
        manifest_path=_workspace_manifest_for_root(root),
    )
    if agent_mount_resolution.get("required") and not agent_mount_resolution.get("accepted"):
        blockers = [
            dict(item)
            for item in (agent_cwd_boundary.get("blockers") or [])
            if isinstance(item, Mapping)
        ]
        blockers.extend(
            dict(item)
            for item in (agent_mount_resolution.get("blockers") or [])
            if isinstance(item, Mapping)
        )
        agent_cwd_boundary = dict(agent_cwd_boundary)
        agent_cwd_boundary["accepted"] = False
        agent_cwd_boundary["status"] = "AGENT_CWD_BLOCKED"
        agent_cwd_boundary["blockers"] = blockers
        agent_cwd_boundary["blocker_count"] = len(blockers)
        agent_cwd_boundary["blocker_codes"] = [str(item.get("code")) for item in blockers if item.get("code")]
        agent_cwd_boundary["codex_agent_mount_resolution"] = agent_mount_resolution
    elif agent_mount_resolution.get("required"):
        agent_cwd_boundary = dict(agent_cwd_boundary)
        agent_cwd_boundary["codex_agent_mount_resolution"] = agent_mount_resolution
    default_envelope["agent_cwd_boundary"] = agent_cwd_boundary
    default_envelope["worker_launch_cwd"] = agent_cwd_boundary["worker_launch_cwd"]
    default_envelope["worker_launch_realpath"] = agent_cwd_boundary["worker_launch_realpath"]
    default_envelope["target_command_cwd"] = agent_cwd_boundary["target_command_cwd"]
    default_envelope["target_command_realpath"] = agent_cwd_boundary["target_command_realpath"]
    default_envelope["cwd_boundary_status"] = agent_cwd_boundary["status"]
    return default_envelope


def _write_ai_movement_preflight_receipt(
    root: Path,
    *,
    preflight: Mapping[str, Any],
    run_dir: Path | None = None,
) -> str:
    if run_dir is not None:
        receipt_path = run_dir / "ai_movement_preflight.json"
    else:
        request_id = _safe_slug(str(preflight.get("request_id") or "request"))
        stamp = _now().replace(":", "").replace("+", "Z")
        receipt_path = root / CODEX_QUEUE_PREFLIGHTS_DIR / f"{stamp}_{request_id}_ai_movement_preflight.json"
    receipt_rel = _connector_rel(receipt_path, root)
    payload = dict(preflight)
    payload["receipt_path"] = receipt_rel
    _write_json(receipt_path, payload)
    return receipt_rel


def _evaluate_ai_movement_preflight(
    root: Path,
    *,
    request: Mapping[str, Any],
    request_rel: str,
    run_packet_rel: str,
    planned_write_paths: list[str],
    planned_artifact_paths: list[str] | None = None,
) -> dict[str, Any]:
    envelope = _ai_movement_root_envelope_for_request(
        root,
        request=request,
        request_rel=request_rel,
        run_packet_rel=run_packet_rel,
        planned_write_paths=planned_write_paths,
        planned_artifact_paths=planned_artifact_paths,
    )
    manifest_path = _workspace_manifest_for_root(root)
    try:
        decision = evaluate_ai_movement_gate(envelope, manifest_path=manifest_path)
        accepted = bool(decision.get("accepted"))
        finding = "ai_movement_gate_accepted" if accepted else "ai_movement_gate_blocked"
    except Exception as exc:
        decision = {
            "schema_id": "ion.ai_movement_gate_decision.v1",
            "accepted": False,
            "verdict": "BLOCKED",
            "movement_class": envelope.get("movement_class"),
            "blockers": [{"code": "AI_MOVEMENT_GATE_EXCEPTION", "detail": str(exc)}],
            "warnings": [],
            "path_authority_decisions": [],
            "root_classifications": [],
            "settlement_target": envelope.get("settlement_target"),
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
        accepted = False
        finding = "ai_movement_gate_exception"
    agent_cwd_boundary = envelope.get("agent_cwd_boundary") if isinstance(envelope.get("agent_cwd_boundary"), Mapping) else {}
    if agent_cwd_boundary.get("accepted") is False:
        boundary_blockers = [
            {
                "code": str(item.get("code") or "AGENT_CWD_BOUNDARY_BLOCKED"),
                "detail": str(item.get("detail") or "agent cwd boundary blocked movement"),
                **{k: v for k, v in dict(item).items() if k not in {"code", "detail"}},
            }
            for item in agent_cwd_boundary.get("blockers", [])
            if isinstance(item, Mapping)
        ]
        if not boundary_blockers:
            boundary_blockers = [{
                "code": "AGENT_CWD_BOUNDARY_BLOCKED",
                "detail": "agent cwd boundary rejected movement",
            }]
        decision = dict(decision)
        decision["accepted"] = False
        decision["verdict"] = "BLOCKED"
        decision["blockers"] = [*(decision.get("blockers") or []), *boundary_blockers]
        decision["agent_cwd_boundary"] = agent_cwd_boundary
        accepted = False
        finding = "ai_movement_gate_blocked"

    legacy_policy = envelope.get("legacy_target_policy") if isinstance(envelope.get("legacy_target_policy"), Mapping) else {}
    if legacy_policy.get("accepted") is False:
        blocker = dict(legacy_policy.get("blocker") or {})
        if not blocker:
            blocker = {
                "code": LEGACY_TARGET_POLICY_BLOCKER_CODE,
                "detail": "Legacy queued request target policy rejected implicit active-root default.",
            }
        decision = dict(decision)
        decision["accepted"] = False
        decision["verdict"] = "BLOCKED"
        decision["blockers"] = [*(decision.get("blockers") or []), blocker]
        decision["legacy_target_policy"] = legacy_policy
        accepted = False
        finding = "ai_movement_gate_blocked"
    return {
        "schema_id": AI_MOVEMENT_PREFLIGHT_SCHEMA_ID,
        "generated_at": _now(),
        "accepted": accepted,
        "verdict": "ACCEPTED" if accepted else "BLOCKED",
        "finding": finding,
        "request_id": request.get("request_id"),
        "request_path": request_rel,
        "run_packet_path": run_packet_rel,
        "manifest_path": str(manifest_path),
        "root_envelope": envelope,
        "gate_decision": decision,
        "preflight_scope": "codex_queue_runner_prepare",
        "runner_start_allowed": accepted,
        "worker_process_started": False,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }


def _model_move_for_request(root: Path, request: Mapping[str, Any]) -> dict[str, Any]:
    existing = request.get("codex_model_move") if isinstance(request.get("codex_model_move"), Mapping) else None
    route_metadata = request.get("route_metadata") if isinstance(request.get("route_metadata"), Mapping) else {}
    work_class = str(
        request.get("work_class")
        or request.get("workload_class")
        or route_metadata.get("work_class")
        or "",
    ).strip()
    risk_level = str(request.get("risk_level") or route_metadata.get("risk_level") or "").strip()
    context_need = str(
        request.get("context_need")
        or request.get("codex_context_need")
        or route_metadata.get("context_need")
        or "medium",
    ).strip() or "medium"
    model_move = (
        dict(existing)
        if existing
        else build_codex_model_move_plan(
            root,
            lane_id=str(request.get("lane_id") or "codex_general"),
            stage_id=str(request.get("ion_stage_id") or "codex_general_work"),
            work_class=work_class or None,
            objective=str(request.get("objective") or ""),
            risk_level=risk_level or None,
            context_need=context_need,
        )
    )

    override = request.get("codex_model_override") if isinstance(request.get("codex_model_override"), Mapping) else None
    if override is None:
        requested_model = str(request.get("requested_model") or "").strip()
        requested_effort = str(request.get("requested_reasoning_effort") or "").strip()
        requested_reason = str(request.get("model_override_reason") or "").strip()
        if requested_model or requested_effort or requested_reason:
            override = {
                "selected_model": requested_model,
                "selected_reasoning_effort": requested_effort,
                "reason": requested_reason,
                "source": "request.requested_model_fields",
            }

    override_receipt: dict[str, Any] = {
        "schema_id": "ion.codex_model_override_receipt.v1",
        "requested": False,
        "applied": False,
        "source": "none",
        "reason": "",
        "claim_boundary": [
            "Model overrides configure Codex CLI invocation only.",
            "Overrides do not authorize production, provider API dispatch, credentials, shell expansion, deploy, push, or accepted state.",
        ],
        "production_authority": False,
        "live_execution_authority": False,
    }

    if isinstance(override, Mapping):
        source = str(override.get("source") or "request.codex_model_override").strip() or "request.codex_model_override"
        requested_model = str(override.get("selected_model") or override.get("model") or override.get("requested_model") or "").strip()
        requested_effort = str(
            override.get("selected_reasoning_effort")
            or override.get("reasoning_effort")
            or override.get("requested_reasoning_effort")
            or ""
        ).strip()
        requested_reason = str(override.get("reason") or "").strip()
        validation = validate_codex_model_override(requested_model, requested_effort)
        override_receipt.update({
            "requested": True,
            "applied": bool(validation.get("ok")),
            "source": source,
            "reason": requested_reason,
            "requested_model": requested_model,
            "requested_reasoning_effort": requested_effort,
            "replacement_model": validation.get("replacement_model"),
            "supported_models": validation.get("supported_models"),
            "supported_reasoning_efforts": validation.get("supported_reasoning_efforts"),
            "validation": validation,
        })
        if not validation.get("ok"):
            return {
                "ok": False,
                "result": "MODEL_OVERRIDE_INVALID",
                "finding": str(validation.get("finding") or "model_override_invalid"),
                "model_override_receipt": override_receipt,
            }
        model_move["selected_model"] = validation["selected_model"]
        model_move["selected_reasoning_effort"] = validation["selected_reasoning_effort"]
        model_move["model_profile"] = dict(validation.get("model_profile") or {})
        if isinstance(model_move.get("model_profile"), Mapping):
            profile = dict(model_move.get("model_profile") or {})
            model_move["usage_pool_id"] = profile.get("usage_pool_id")
            model_move["usage_pool_authority"] = profile.get("usage_pool_authority")
            model_move["limit_authority"] = profile.get("limit_authority")
        model_move["config_overrides"] = {
            "model": validation["selected_model"],
            "model_reasoning_effort": validation["selected_reasoning_effort"],
        }
        model_move["codex_exec_args"] = codex_exec_args_from_model_move(model_move)
        model_move["command_preview"] = ["codex", "exec", *codex_exec_args_from_model_move(model_move)]
        reasons = list(model_move.get("selection_reason") or [])
        reasons.append("explicit_request_model_override")
        model_move["selection_reason"] = reasons
        model_move["model_override"] = {
            "source": source,
            "reason": requested_reason,
            "requested_model": requested_model,
            "requested_reasoning_effort": requested_effort,
        }

    final_validation = validate_codex_model_override(
        str(model_move.get("selected_model") or ""),
        str(model_move.get("selected_reasoning_effort") or ""),
    )
    if not final_validation.get("ok"):
        override_receipt["validation"] = final_validation
        return {
            "ok": False,
            "result": "MODEL_MOVE_INVALID",
            "finding": str(final_validation.get("finding") or "model_move_invalid"),
            "model_override_receipt": override_receipt,
        }

    return {
        "ok": True,
        "model_move": model_move,
        "model_override_receipt": override_receipt,
    }


def _request_requires_workload_diff(request: Mapping[str, Any]) -> bool:
    requested_by = str(request.get("requested_by") or "").strip().lower()
    if requested_by == "ion_agent_invocation_broker":
        return True
    signal_text = " ".join([
        str(request.get("request_kind") or ""),
        str(request.get("objective") or ""),
        str(request.get("agent_role") or ""),
        str(request.get("agent_role_id") or ""),
        str(request.get("agent_display_name") or ""),
    ]).lower()
    return any(hint in signal_text for hint in WORKLOAD_DIFF_REQUEST_HINTS)


def _return_contract_sections_for_request(request: Mapping[str, Any]) -> list[str]:
    configured = request.get("return_contract_sections")
    sections: list[str] = []
    if isinstance(configured, list):
        for item in configured:
            section = str(item or "").strip()
            if section.startswith("### ") and section not in sections:
                sections.append(section)
    if not sections:
        sections = list(BASE_RETURN_CONTRACT_SECTIONS)
    for required_section in MANDATORY_RETURN_SECTIONS:
        if required_section not in sections:
            sections.append(required_section)
    if operator_artifact_hygiene_required(request) and OPERATOR_ARTIFACT_HYGIENE_SECTION not in sections:
        sections.append(OPERATOR_ARTIFACT_HYGIENE_SECTION)
    if ion_operational_posture_required(request) and OPERATIONAL_POSTURE_SECTION not in sections:
        sections.append(OPERATIONAL_POSTURE_SECTION)
    return sections


def _agent_comms_followup_decision_required(request: Mapping[str, Any]) -> bool:
    text = "\n".join(
        [
            str(request.get("objective") or ""),
            str(request.get("task_body") or ""),
            str(request.get("agent_comms_followup_contract") or ""),
        ]
    )
    return "Agent follow-up contract:" in text or "ion.agent_comms.followup_decision.v1" in text


def _workload_class_for_request(request: Mapping[str, Any]) -> str:
    structured = str(request.get("workload_class") or request.get("work_class") or "").strip()
    if structured:
        return re.sub(r"[^a-z0-9]+", "_", structured.lower()).strip("_")
    signal = " ".join([
        str(request.get("request_kind") or ""),
        str(request.get("objective") or ""),
        str(request.get("agent_role") or ""),
    ]).lower()
    if "proof_repair" in signal or "repair the proof return" in signal:
        return "proof_repair"
    if "context_package" in signal and ("materialize" in signal or "materialization" in signal):
        return "context_package_materialization"
    if any(token in signal for token in ("cartography", "map", "route")):
        return "cartography"
    if any(token in signal for token in ("design", "report", "proposal", "plan")):
        return "design_report"
    return "code_patch"


def _worker_spawn_contract_for_request(request: Mapping[str, Any], *, timeout_seconds: int) -> dict[str, Any]:
    required_reads = request.get("required_context_reads")
    reads = required_reads if isinstance(required_reads, list) else [{"kind": "file", "path": path, "required": True} for path in DEFAULT_CONTEXT_READS]
    workload_class = _workload_class_for_request(request)
    return {
        "schema_id": "ion.codex_worker_spawn_contract.v1",
        "template_id": WORKLOAD_TEMPLATE_BY_CLASS.get(workload_class, "ion.template.autonomous_loop.local_worker.v1"),
        "action_id": "codex_queue_runner_process_once",
        "work_request_id": str(request.get("request_id") or ""),
        "workload_class": workload_class,
        "runtime_budget_seconds": int(timeout_seconds),
        "soft_deadline_seconds": max(30, int(timeout_seconds * 0.8)),
        "hard_timeout_seconds": int(timeout_seconds),
        "authority_boundaries": {
            "production_authority": False,
            "live_execution_authority": False,
            "ion_carrier_mount": "mounted_ion_codex_carrier",
        },
        "required_context_reads": reads,
        "proof_obligations": {
            "context_proof_format": "path/sha256/excerpt for each required read",
            "template_action_proof_required_fields": ["template_id", "action_id", "result", "touched_paths|no_touched_paths"],
            "workload_diff_required": True,
        },
        "return_contract_sections": _return_contract_sections_for_request(request),
        "settlement_posture": "candidate_only_blocked_returns_preserved",
    }


def _sha256_for_rel_path(root: Path, rel_path: str | None) -> str | None:
    if not rel_path:
        return None
    try:
        target = _safe_rel_path(root, rel_path)
    except ValueError:
        return None
    if not target.exists() or not target.is_file():
        return None
    return _sha256_file(target)


def _worker_context_awareness_receipt_path_for_run(root: Path, run: Mapping[str, Any]) -> str:
    configured = str(run.get("worker_context_awareness_receipt_path") or "").strip()
    if configured:
        return configured
    run_dir = str(run.get("run_dir") or "").strip()
    if not run_dir:
        return WORKER_CONTEXT_AWARENESS_RECEIPT_FILENAME
    return _connector_rel((root / run_dir / WORKER_CONTEXT_AWARENESS_RECEIPT_FILENAME), root)


def _build_worker_context_awareness_receipt(
    root: Path,
    run_packet_rel: str,
    run: Mapping[str, Any],
    *,
    worker_pid_or_process_ref: int | str | None = None,
    started_at: str | None = None,
) -> dict[str, Any]:
    prompt_path = str(run.get("prompt_path") or "")
    context_receipt_path = str(run.get("context_receipt_path") or "")
    run_packet_path = run_packet_rel
    prompt_sha = _sha256_for_rel_path(root, prompt_path)
    run_packet_sha = _sha256_for_rel_path(root, run_packet_path)
    context_receipt_sha = _sha256_for_rel_path(root, context_receipt_path)
    context_receipt = _read_json(root / context_receipt_path) if context_receipt_path else None
    context_rows: list[dict[str, Any]] = []
    if isinstance(context_receipt, Mapping):
        raw_rows = context_receipt.get("required_context_reads")
        if isinstance(raw_rows, list):
            for item in raw_rows:
                if isinstance(item, Mapping):
                    path = str(item.get("path") or "").strip()
                    if not path:
                        continue
                    required = bool(item.get("required", True))
                    status = str(item.get("status") or "").strip()
                    sha = str(item.get("sha256") or "").strip() or None
                    excerpt = str(item.get("excerpt") or "").strip() or None
                    if not status or not sha:
                        observed = _observe_context_path(root, path, required=required)
                        status = str(observed.get("status") or status)
                        sha = str(observed.get("sha256") or "").strip() or None
                        excerpt = str(observed.get("excerpt") or "").strip() or excerpt
                    context_rows.append({
                        "path": path,
                        "required": required,
                        "status": status,
                        "sha256": sha,
                        "excerpt": excerpt,
                    })
    findings: list[str] = []
    if not prompt_sha:
        findings.append("prompt_hash_missing")
    if not run_packet_sha:
        findings.append("run_packet_hash_missing")
    if not context_receipt_sha:
        findings.append("context_receipt_hash_missing")
    missing_required_context = [
        row["path"]
        for row in context_rows
        if row.get("required") and (row.get("status") != "READY" or not row.get("sha256"))
    ]
    if missing_required_context:
        findings.append("required_context_missing_or_unhashed")
    spawn_contract = run.get("worker_spawn_contract") if isinstance(run.get("worker_spawn_contract"), Mapping) else {}
    model_move = run.get("codex_model_move") if isinstance(run.get("codex_model_move"), Mapping) else {}
    ai_movement_preflight = run.get("ai_movement_preflight") if isinstance(run.get("ai_movement_preflight"), Mapping) else {}
    root_envelope = ai_movement_preflight.get("root_envelope") if isinstance(ai_movement_preflight.get("root_envelope"), Mapping) else {}
    agent_cwd_boundary = root_envelope.get("agent_cwd_boundary") if isinstance(root_envelope.get("agent_cwd_boundary"), Mapping) else {}
    status = WORKER_CONTEXT_ACKNOWLEDGED if not findings else WORKER_CONTEXT_BLOCKED
    observed: dict[str, Any] = {
        "schema_id": "ion.worker_context_awareness_receipt.v1",
        "generated_by": "runner_or_control_plane",
        "worker_authored": False,
        "status": status,
        "run_id": run.get("run_id"),
        "request_id": run.get("request_id"),
        "active_root_proof": run.get("active_root_proof") if isinstance(run.get("active_root_proof"), Mapping) else _active_root_proof(root),
        "worker_identity": run.get("worker_identity") if isinstance(run.get("worker_identity"), Mapping) else {},
        "domain_alignment": run.get("domain_alignment") if isinstance(run.get("domain_alignment"), Mapping) else {},
        "worker_return_status": run.get("worker_return_status") if isinstance(run.get("worker_return_status"), Mapping) else _worker_return_status_for_run(run),
        "worker_pid_or_process_ref": worker_pid_or_process_ref,
        "selected_model": model_move.get("selected_model"),
        "selected_reasoning_effort": model_move.get("selected_reasoning_effort"),
        "prompt_path": prompt_path,
        "prompt_sha256": prompt_sha,
        "run_packet_path": run_packet_path,
        "run_packet_sha256": run_packet_sha,
        "context_receipt_path": context_receipt_path,
        "context_receipt_sha256": context_receipt_sha,
        "required_context_reads": context_rows,
        "template_id": spawn_contract.get("template_id"),
        "action_id": spawn_contract.get("action_id"),
        "agent_cwd_boundary": agent_cwd_boundary,
        "worker_launch_cwd": agent_cwd_boundary.get("worker_launch_cwd"),
        "target_command_cwd": agent_cwd_boundary.get("target_command_cwd"),
        "codex_project_cwd": run.get("codex_project_cwd"),
        "codex_cli_launch_profile": run.get("codex_cli_launch_profile")
        if isinstance(run.get("codex_cli_launch_profile"), Mapping)
        else {},
        "authority_boundaries": spawn_contract.get("authority_boundaries") if isinstance(spawn_contract.get("authority_boundaries"), Mapping) else {
            "production_authority": False,
            "live_execution_authority": False,
            "ion_carrier_mount": "mounted_ion_codex_carrier",
        },
        "started_at": started_at or str(run.get("started_at") or _now()),
        "findings": findings,
        "missing_required_context_paths": missing_required_context,
    }
    observed["machine_attestation_sha256"] = _sha256_json_payload(observed)
    return observed


def _write_worker_context_awareness_receipt(
    root: Path,
    run_packet_rel: str,
    run: Mapping[str, Any],
    *,
    worker_pid_or_process_ref: int | str | None = None,
    started_at: str | None = None,
) -> tuple[str, str | None, dict[str, Any]]:
    receipt_rel = _worker_context_awareness_receipt_path_for_run(root, run)
    receipt_path = root / receipt_rel
    receipt = _build_worker_context_awareness_receipt(
        root,
        run_packet_rel,
        run,
        worker_pid_or_process_ref=worker_pid_or_process_ref,
        started_at=started_at,
    )
    _write_json(receipt_path, receipt)
    return receipt_rel, _sha256_file(receipt_path), receipt


def _codex_service_tier_for_request(request: Mapping[str, Any]) -> str:
    override = request.get("codex_model_override") if isinstance(request.get("codex_model_override"), Mapping) else {}
    configured = str(
        request.get("requested_service_tier")
        or request.get("codex_service_tier")
        or override.get("service_tier")
        or ""
    ).strip().lower()
    return configured if configured in CODEX_SERVICE_TIERS else ""


def _codex_command(
    codex_binary: str,
    model_move: Mapping[str, Any],
    last_message_path: str,
    *,
    codex_project_cwd: str = "",
    service_tier: str = "",
    disable_image_generation: bool = False,
) -> list[str]:
    args = [
        codex_binary,
        "exec",
    ]
    if codex_project_cwd:
        args.extend(["-C", codex_project_cwd])
    args.extend(codex_exec_args_from_model_move(model_move))
    if service_tier and service_tier != "auto":
        args.extend(["-c", f"service_tier={service_tier}"])
    args.extend([
        "--sandbox",
        "workspace-write",
        "--output-last-message",
        last_message_path,
    ])
    if disable_image_generation:
        args.extend(["--disable", "image_generation"])
    return args


def _codex_project_cwd_for_run(
    root: Path,
    *,
    worker_launch_cwd: str,
    agent_mount_resolution: Mapping[str, Any] | None = None,
) -> str:
    worker_cwd_path = Path(worker_launch_cwd).expanduser().resolve(strict=False)
    mount_root = (root / CODEX_AGENT_MOUNT_ROOT).resolve(strict=False)
    if (
        agent_mount_resolution
        and agent_mount_resolution.get("required")
        and agent_mount_resolution.get("accepted")
        and _is_path_within(worker_cwd_path, mount_root)
        and worker_cwd_path != mount_root
    ):
        return str(root.resolve(strict=False))
    return str(worker_cwd_path)


def _codex_cli_launch_profile(
    *,
    worker_launch_cwd: str,
    target_command_cwd: str,
    codex_project_cwd: str,
    codex_command: list[str],
) -> dict[str, Any]:
    worker_cwd_path = Path(worker_launch_cwd).expanduser().resolve(strict=False)
    project_cwd_path = Path(codex_project_cwd).expanduser().resolve(strict=False)
    config_path = project_cwd_path / ".codex/config.toml"
    mount_config_path = worker_cwd_path / ".codex/config.toml"
    generated_mount_context = worker_cwd_path != project_cwd_path
    return {
        "schema_id": "ion.codex_cli_launch_profile.v0_1",
        "worker_launch_cwd": str(worker_cwd_path),
        "target_command_cwd": str(Path(target_command_cwd).expanduser().resolve(strict=False)),
        "codex_project_cwd": str(project_cwd_path),
        "context_mount_cwd": str(worker_cwd_path) if generated_mount_context else None,
        "subprocess_cwd": str(project_cwd_path),
        "codex_cd_arg": str(project_cwd_path),
        "codex_cd_arg_present": "-C" in codex_command or "--cd" in codex_command,
        "codex_config_path": str(config_path),
        "codex_config_exists": config_path.exists(),
        "codex_config_sha256": _sha256_file(config_path) if config_path.exists() else None,
        "context_mount_config_path": str(mount_config_path) if generated_mount_context else None,
        "context_mount_config_exists": mount_config_path.exists() if generated_mount_context else None,
        "context_mount_config_sha256": _sha256_file(mount_config_path)
        if generated_mount_context and mount_config_path.exists()
        else None,
        "launch_policy": "active_root_codex_config_with_generated_mount_context"
        if generated_mount_context
        else "subprocess_cwd_and_codex_exec_cd_arg_both_bind_worker_launch_cwd",
        "hook_trust_surface": "codex_project_cwd_config",
        "context_binding_surface": "worker_launch_cwd",
        "claim_boundary": "Launch profile records local carrier configuration only; it is not accepted task state.",
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }


def _disable_image_generation_for_request(request: Mapping[str, Any]) -> bool:
    configured = request.get("disable_image_generation")
    if isinstance(configured, bool):
        return configured
    configured_text = str(configured or "").strip().lower()
    if configured_text in {"true", "1", "yes", "on", "enable"}:
        return True
    if configured_text in {"false", "0", "no", "off", "disable", "disable_none"}:
        return False
    return DEFAULT_DISABLE_IMAGE_GENERATION


def _build_prompt(
    request: Mapping[str, Any],
    request_rel: str,
    context_receipt_rel: str,
    task_return_body_rel: str,
    model_move: Mapping[str, Any],
    spawn_contract: Mapping[str, Any],
) -> str:
    objective = str(request.get("objective") or "")
    request_kind = str(request.get("request_kind") or "codex_work")
    skill_activation = request.get("ion_skill_activation") if isinstance(request.get("ion_skill_activation"), Mapping) else {}
    chat_engine = request.get("ion_chat_engine_turn") if isinstance(request.get("ion_chat_engine_turn"), Mapping) else {}
    native_lenses = chat_engine.get("native_lenses") if isinstance(chat_engine.get("native_lenses"), list) else []
    native_lens_lines = [
        f"    - \"{str(lens.get('display_name') or lens.get('lens_id') or 'lens').replace(chr(34), chr(39))}: {str(lens.get('purpose') or '')[:180].replace(chr(34), chr(39))}\""
        for lens in native_lenses[:8]
        if isinstance(lens, Mapping)
    ]
    template_refs = skill_activation.get("activates_templates") if isinstance(skill_activation.get("activates_templates"), list) else []
    template_lines = [f"    - \"{str(ref)}\"" for ref in template_refs[:8]]
    return_contract_sections = list(spawn_contract.get("return_contract_sections") or _return_contract_sections_for_request(request))
    return_contract_section_lines = [f"    - \"{section}\"" for section in return_contract_sections]
    followup_decision_required = _agent_comms_followup_decision_required(request)
    followup_decision_contract_lines = (
        [
            "  agent_comms_followup_decision_requirement: \"Because this is a Team Comms workpack, end the final response with exactly one fenced ion-agent-comms directive or one fenced ion-agent-decision block.\"",
            "  no_followup_decision_exact_shape: |",
            "    ```ion-agent-decision",
            "    {",
            "      \"schema_id\": \"ion.agent_comms.followup_decision.v1\",",
            "      \"decision\": \"no_followup\",",
            "      \"reason\": \"<why no further agent is needed>\",",
            "      \"evidence_refs\": [\"<repo-relative evidence path>\"]",
            "    }",
            "    ```",
            "  followup_directive_exact_shape: |",
            "    ```ion-agent-comms",
            "    {",
            "      \"schema_id\": \"ion.agent_comms.directive.v1\",",
            "      \"from_role\": \"<your role id>\",",
            "      \"agent\": \"<target role id>\",",
            "      \"dispatch_mode\": \"queue_workpack\",",
            "      \"objective\": \"<bounded objective>\",",
            "      \"body\": \"<workpack body>\",",
            "      \"source_refs\": [\"<repo-relative evidence path>\"]",
            "    }",
            "    ```",
        ]
        if followup_decision_required
        else []
    )
    followup_decision_template_lines = (
        [
            "",
            "  ```ion-agent-decision",
            "  {",
            "    \"schema_id\": \"ion.agent_comms.followup_decision.v1\",",
            "    \"decision\": \"no_followup\",",
            "    \"reason\": \"<why no further agent is needed>\",",
            "    \"evidence_refs\": [\"ION/...\"]",
            "  }",
            "  ```",
        ]
        if followup_decision_required
        else []
    )
    ai_movement_preflight = (
        spawn_contract.get("ai_movement_gate_preflight")
        if isinstance(spawn_contract.get("ai_movement_gate_preflight"), Mapping)
        else {}
    )
    root_envelope = ai_movement_preflight.get("root_envelope") if isinstance(ai_movement_preflight.get("root_envelope"), Mapping) else {}
    agent_cwd_boundary = root_envelope.get("agent_cwd_boundary") if isinstance(root_envelope.get("agent_cwd_boundary"), Mapping) else {}
    codex_launch_boundary = (
        spawn_contract.get("codex_launch_boundary")
        if isinstance(spawn_contract.get("codex_launch_boundary"), Mapping)
        else {}
    )
    operational_posture_template_lines = (
        [
            "  ### ION OPERATIONAL POSTURE",
            "  ion_operational_state: ION_CODEX_OPERATIONAL_READY",
            "  mount_truth_state: CODEX_CARRIER_LOCAL_MOUNT_READY",
            "  role_phase_sequence: PERSONA_INTERFACE_INGRESS -> RELAY -> STEWARD -> VIZIER -> MASON -> NEMESIS_OR_VICE_REVIEW -> SCRIBE -> STEWARD_FINAL -> PERSONA_INTERFACE_RESPONSE",
            "  context_fallback: Mini/Capsule are fallback witnesses only.",
            "  non_claims: no accepted-state claim",
            "",
        ]
        if OPERATIONAL_POSTURE_SECTION in return_contract_sections
        else []
    )
    return "\n".join([
        "carrier_mount:",
        "  title: \"ION Codex Queue Runner Work Packet\"",
        "  carrier: \"Codex CLI\"",
        "  carrier_identity: \"CODEX_CLI_CARRIER\"",
        "  ion_carrier_mount: \"mounted_ion_codex_carrier\"",
        "  production_authority: false",
        "  live_execution_authority: false",
        "",
        "mission:",
        f"  request_kind: \"{request_kind}\"",
        "  primary_goal: >",
        f"    {objective}",
        "",
        "ion_chat_engine:",
        f"  response_mode: \"{chat_engine.get('response_mode') if chat_engine else 'unspecified'}\"",
        f"  selected_skill: \"{skill_activation.get('display_name') if skill_activation else 'unspecified'}\"",
        f"  carrier_strategy: \"{(chat_engine.get('carrier_strategy') or {}).get('mode') if isinstance(chat_engine.get('carrier_strategy'), Mapping) else 'existing_codex_queue'}\"",
        "  native_lenses:",
        *(native_lens_lines or ["    - \"none declared\""]),
        "  active_template_refs:",
        *(template_lines or ["    - \"none declared\""]),
        "",
        "codex_model_move:",
        f"  summary: \"{summarize_model_move(model_move)}\"",
        f"  selected_model: \"{model_move.get('selected_model')}\"",
        f"  selected_reasoning_effort: \"{model_move.get('selected_reasoning_effort')}\"",
        f"  usage_pool_id: \"{model_move.get('usage_pool_id')}\"",
        f"  usage_pool_authority: \"{model_move.get('usage_pool_authority')}\"",
        "  usage_limits_authoritative: false",
        "  note: \"Usage-pool labels are advisory until externally verified.\"",
        "",
        "hard_boundaries:",
        "  - \"Operate as the mounted ION Codex carrier; STEWARD, RELAY, PERSONA, production, sovereign, and accepted-state authority require explicit proof and approval.\"",
        "  - \"Do not push git.\"",
        "  - \"Do not deploy production.\"",
        "  - \"Do not read, print, store, or request secrets/API keys/tokens.\"",
        "  - \"Do not delete files. If removal seems needed, propose lifecycle transition only.\"",
        "  - \"Do not mutate outside the current repo shell root.\"",
        "  - \"Reuse existing ION queue, task-return, carrier-message, and receipt owners.\"",
        "",
        "required_context:",
        f"  work_request_path: \"{request_rel}\"",
        f"  context_receipt_path: \"{context_receipt_rel}\"",
        f"  task_return_body_path: \"{task_return_body_rel}\"",
        "  instruction: \"Read the work request and every required path in the context receipt before writing.\"",
        "",
        "worker_spawn_contract:",
        f"  schema_id: \"{spawn_contract.get('schema_id')}\"",
        f"  template_id: \"{spawn_contract.get('template_id')}\"",
        f"  action_id: \"{spawn_contract.get('action_id')}\"",
        f"  work_request_id: \"{spawn_contract.get('work_request_id')}\"",
        f"  workload_class: \"{spawn_contract.get('workload_class')}\"",
        "  ai_movement_gate_preflight:",
        f"    schema_id: \"{ai_movement_preflight.get('schema_id') or AI_MOVEMENT_PREFLIGHT_SCHEMA_ID}\"",
        f"    verdict: \"{ai_movement_preflight.get('verdict') or 'UNKNOWN'}\"",
        f"    receipt_path: \"{ai_movement_preflight.get('receipt_path') or ''}\"",
        f"    runner_start_allowed: {str(bool(ai_movement_preflight.get('runner_start_allowed'))).lower()}",
        "  agent_cwd_boundary:",
        f"    status: \"{agent_cwd_boundary.get('status') or 'UNKNOWN'}\"",
        f"    control_plane_cwd: \"{agent_cwd_boundary.get('control_plane_cwd') or ''}\"",
        f"    worker_launch_cwd: \"{agent_cwd_boundary.get('worker_launch_cwd') or ''}\"",
        f"    target_command_cwd: \"{agent_cwd_boundary.get('target_command_cwd') or ''}\"",
        "    instruction: \"Run project-local commands from target_command_cwd; do not create sibling roots, duplicate project folders, or parent-relative write paths.\"",
        "  codex_launch_boundary:",
        f"    launch_policy: \"{codex_launch_boundary.get('launch_policy') or 'worker_launch_cwd_codex_config'}\"",
        f"    codex_project_cwd: \"{codex_launch_boundary.get('codex_project_cwd') or ''}\"",
        f"    context_mount_cwd: \"{codex_launch_boundary.get('context_mount_cwd') or ''}\"",
        f"    codex_config_path: \"{codex_launch_boundary.get('codex_config_path') or ''}\"",
        "    instruction: \"Codex may be launched from codex_project_cwd to preserve trusted hooks while the work context remains bound to worker_launch_cwd and target_command_cwd.\"",
        "",
        "ion_runtime_budget:",
        f"  runtime_budget_seconds: {spawn_contract.get('runtime_budget_seconds')}",
        f"  soft_deadline_seconds: {spawn_contract.get('soft_deadline_seconds')}",
        f"  hard_timeout_seconds: {spawn_contract.get('hard_timeout_seconds')}",
        "",
        "return_contract:",
        "  required_sections:",
        *return_contract_section_lines,
        f"  template_id: \"{spawn_contract.get('template_id')}\"",
        f"  action_id_hint: \"{spawn_contract.get('action_id')}\"",
        "  template_action_proof_exact_shape: |",
        "    ### TEMPLATE ACTION PROOF",
        f"    template_id: {spawn_contract.get('template_id')}",
        f"    action_id: {spawn_contract.get('action_id')}",
        "    result: <one-line result>",
        "    touched_paths:",
        "      - <repo-relative evidence or changed path>",
        "  context_proof_requirement: \"Mention every required context path with line/excerpt/sha256 evidence.\"",
        "  result_requirement: \"State touched paths, tests, remaining blockers, and next lawful moves.\"",
        "  touched_paths_requirement: \"Under TEMPLATE ACTION PROOF, include touched_paths as a non-empty YAML list. For read-only/no-edit work, list the work request, run packet, context receipt, or repo-relative source/status files inspected.\"",
        "  proof_rejection_warning: \"Do not omit template_id, action_id, result, or touched_paths; [] and none are not accepted for touched_paths.\"",
        *followup_decision_contract_lines,
        "",
        "return_template: |",
        "  ### CONTEXT PROOF",
        "  path: ION/...",
        "  sha256: ...",
        "  excerpt: \"...\"",
        "",
        *operational_posture_template_lines,
        "  ### TEMPLATE ACTION PROOF",
        f"  template_id: {spawn_contract.get('template_id')}",
        f"  action_id: {spawn_contract.get('action_id')}",
        "  result: <implemented|designed|blocked>",
        "  touched_paths:",
        "    - ION/...",
        "",
        "  ### VALIDATION",
        "  - <tests/checks>",
        "",
        "  ### RESULT",
        "  <what changed>",
        "",
        "  ### WORKLOAD DIFF",
        "  - ION/...",
        "",
        "  ### BLOCKERS",
        "  - none",
        "",
        "  ### RECOMMENDED NEXT PACKET",
        "  <one packet>",
        *followup_decision_template_lines,
        "",
    ])


def _select_request(root: Path, request_path: str | None, lane_id: str | None = None) -> tuple[Path | None, str | None]:
    if request_path:
        try:
            path = _safe_rel_path(root, request_path)
            path.relative_to((root / CODEX_WORK_REQUESTS_DIR).resolve())
        except (ValueError, RuntimeError):
            return None, "request_path_not_bounded_to_codex_work_requests"
        if not path.exists():
            return None, "request_path_missing"
        return path, None
    normalized_lane_id = normalize_codex_work_lane_id(lane_id)
    if lane_id and not normalized_lane_id:
        return None, "lane_id_not_supported"
    queued = _queued_request_paths(root, normalized_lane_id)
    if not queued:
        return None, "no_queued_codex_work_request_for_lane" if normalized_lane_id else "no_queued_codex_work_request"
    return queued[0], None


def _explicit_request_lane_id(root: Path, request_path: str | None) -> str | None:
    if not request_path:
        return None
    try:
        path = _safe_rel_path(root, request_path)
        path.relative_to((root / CODEX_WORK_REQUESTS_DIR).resolve())
    except (ValueError, RuntimeError):
        return None
    if not path.exists():
        return None
    payload = _load_request(path)
    return str(classify_codex_work_request_lane(payload).get("lane_id") or "needs_triage")


def _write_run_packet(path: Path, payload: Mapping[str, Any]) -> None:
    value = dict(payload)
    value["updated_at"] = _now()
    root_for_packet: Path | None = None
    try:
        root_for_packet = _resolve_root(path)
    except Exception:
        root_for_packet = None
    if root_for_packet is not None:
        value.setdefault("active_root_proof", _active_root_proof(root_for_packet))
    value["worker_return_status"] = _worker_return_status_for_run(value)
    terminal = str(value.get("status") or "") in TERMINAL_RUN_STATUSES
    if terminal:
        if root_for_packet is not None:
            _release_codex_queue_run_lease(
                root_for_packet,
                value,
                reason=f"terminal_run_packet_write_{str(value.get('status') or 'unknown').lower()}",
            )
        snapshot_rel = _worker_trace_snapshot_rel(value)
        if snapshot_rel:
            value["worker_trace_snapshot_path"] = snapshot_rel
    _write_json(path, value)
    if terminal:
        if root_for_packet is None:
            return
        _write_worker_trace_snapshot(root_for_packet, value)


def prepare_codex_queue_run(
    root: str | Path | None = None,
    *,
    request_path: str | None = None,
    lane_id: str | None = None,
    claim: bool = False,
    codex_binary: str = "codex",
    timeout_seconds: int = DEFAULT_CODEX_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    selected, finding = _select_request(shell_root, request_path, lane_id=lane_id)
    if finding or selected is None:
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "finding": finding or "request_selection_failed",
            "lane_id": normalize_codex_work_lane_id(lane_id) if lane_id else None,
            "production_authority": False,
            "live_execution_authority": False,
        }
    request = _load_request(selected)
    request_rel = _connector_rel(selected, shell_root)
    lane_route = classify_codex_work_request_lane(request)
    selected_lane_id = str(lane_route.get("lane_id") or "needs_triage")
    now = _now()
    run_id = f"codex_run_{now.replace(':', '').replace('+', 'Z')}_{_safe_slug(str(request.get('request_id') or selected.stem))}"
    run_dir = shell_root / CODEX_QUEUE_RUNS_DIR / run_id
    counter = 1
    while run_dir.exists():
        run_id = f"codex_run_{now.replace(':', '').replace('+', 'Z')}_{_safe_slug(str(request.get('request_id') or selected.stem))}_{counter}"
        run_dir = shell_root / CODEX_QUEUE_RUNS_DIR / run_id
        counter += 1
    context_receipt_path = run_dir / "context_receipt.json"
    prompt_path = run_dir / "prompt.md"
    stdout_path = run_dir / "stdout.log"
    stderr_path = run_dir / "stderr.log"
    last_message_path = run_dir / "latest_return.md"
    task_return_body_path = run_dir / "task_return_body.md"
    run_packet_path = run_dir / "run.json"
    worker_context_awareness_receipt_path = run_dir / WORKER_CONTEXT_AWARENESS_RECEIPT_FILENAME
    run_packet_rel = _connector_rel(run_packet_path, shell_root)
    planned_write_paths = [
        _connector_rel(context_receipt_path, shell_root),
        _connector_rel(prompt_path, shell_root),
        _connector_rel(stdout_path, shell_root),
        _connector_rel(stderr_path, shell_root),
        _connector_rel(last_message_path, shell_root),
        _connector_rel(task_return_body_path, shell_root),
        run_packet_rel,
        _connector_rel(worker_context_awareness_receipt_path, shell_root),
    ]
    if claim:
        planned_write_paths.extend([
            request_rel,
            CODEX_WORK_QUEUE_INDEX.as_posix(),
            RUNNER_STATE_PATH.as_posix(),
        ])
    ai_movement_preflight = _evaluate_ai_movement_preflight(
        shell_root,
        request=request,
        request_rel=request_rel,
        run_packet_rel=run_packet_rel,
        planned_write_paths=planned_write_paths,
    )
    if not ai_movement_preflight.get("accepted"):
        receipt_rel = _write_ai_movement_preflight_receipt(shell_root, preflight=ai_movement_preflight)
        ai_movement_preflight["receipt_path"] = receipt_rel
        if claim:
            _update_request_status(
                shell_root,
                request_rel,
                status="CODEX_QUEUE_RUNNER_FAILED",
                failure_classification="CARRIER_ADAPTER_FAILURE",
            )
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "result": AI_MOVEMENT_GATE_REJECTED_RESULT,
            "finding": ai_movement_preflight.get("finding") or "ai_movement_gate_blocked",
            "request_path": request_rel,
            "request_id": request.get("request_id"),
            "ai_movement_preflight": ai_movement_preflight,
            "ai_movement_preflight_receipt_path": receipt_rel,
            "production_authority": False,
            "live_execution_authority": False,
        }
    route_enforcement_receipt = validate_codex_route_enforcement(
        request,
        source="codex_queue_runner_prepare",
    )
    if not route_enforcement_receipt.get("ok"):
        if claim:
            _update_request_status(
                shell_root,
                request_rel,
                status="CODEX_QUEUE_RUNNER_FAILED",
                failure_classification="CARRIER_ADAPTER_FAILURE",
            )
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "result": "ROUTE_ENFORCEMENT_REJECTED",
            "finding": route_enforcement_receipt.get("finding") or "route_enforcement_rejected",
            "request_path": request_rel,
            "request_id": request.get("request_id"),
            "route_enforcement_receipt": route_enforcement_receipt,
            "production_authority": False,
            "live_execution_authority": False,
        }
    model_move_result = _model_move_for_request(shell_root, request)
    if not model_move_result.get("ok"):
        if claim:
            _update_request_status(
                shell_root,
                request_rel,
                status="CODEX_QUEUE_RUNNER_FAILED",
                failure_classification="CARRIER_ADAPTER_FAILURE",
            )
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "result": model_move_result.get("result") or "MODEL_MOVE_INVALID",
            "finding": model_move_result.get("finding") or "model_move_invalid",
            "request_path": request_rel,
            "request_id": request.get("request_id"),
            "model_override_receipt": model_move_result.get("model_override_receipt"),
            "production_authority": False,
            "live_execution_authority": False,
        }
    model_move = dict(model_move_result["model_move"])
    model_override_receipt = dict(model_move_result.get("model_override_receipt") or {})
    active_root_proof = _active_root_proof(shell_root)
    worker_identity = _worker_identity_for_request(request, lane_id=selected_lane_id, lane_route=lane_route)
    domain_alignment = _worker_domain_alignment(str(worker_identity.get("domain_id") or request.get("domain_id") or ""))
    run_dir.mkdir(parents=True, exist_ok=False)
    context_receipt = _context_receipt_for_request(shell_root, request_rel, request)
    context_receipt["active_root_proof"] = active_root_proof
    context_receipt["worker_identity"] = worker_identity
    context_receipt["domain_alignment"] = domain_alignment
    _write_json(context_receipt_path, context_receipt)
    timeout = min(max(int(timeout_seconds), 30), MAX_CODEX_TIMEOUT_SECONDS)
    spawn_contract = _worker_spawn_contract_for_request(request, timeout_seconds=timeout)
    spawn_contract["active_root_proof"] = active_root_proof
    spawn_contract["worker_identity"] = worker_identity
    spawn_contract["domain_alignment"] = domain_alignment
    preflight_receipt_rel = _write_ai_movement_preflight_receipt(
        shell_root,
        preflight=ai_movement_preflight,
        run_dir=run_dir,
    )
    ai_movement_preflight["receipt_path"] = preflight_receipt_rel
    spawn_contract["ai_movement_gate_preflight"] = {
        "schema_id": AI_MOVEMENT_PREFLIGHT_SCHEMA_ID,
        "verdict": ai_movement_preflight.get("verdict"),
        "finding": ai_movement_preflight.get("finding"),
        "receipt_path": preflight_receipt_rel,
        "runner_start_allowed": bool(ai_movement_preflight.get("accepted")),
        "root_envelope": {
            "target_root_id": (ai_movement_preflight.get("root_envelope") or {}).get("target_root_id")
            if isinstance(ai_movement_preflight.get("root_envelope"), Mapping)
            else None,
            "target_project_root": (ai_movement_preflight.get("root_envelope") or {}).get("target_project_root")
            if isinstance(ai_movement_preflight.get("root_envelope"), Mapping)
            else None,
            "agent_cwd_boundary": (ai_movement_preflight.get("root_envelope") or {}).get("agent_cwd_boundary")
            if isinstance(ai_movement_preflight.get("root_envelope"), Mapping)
            else None,
        },
    }
    root_envelope = ai_movement_preflight.get("root_envelope") if isinstance(ai_movement_preflight.get("root_envelope"), Mapping) else {}
    agent_cwd_boundary = root_envelope.get("agent_cwd_boundary") if isinstance(root_envelope.get("agent_cwd_boundary"), Mapping) else {}
    worker_launch_cwd = str(agent_cwd_boundary.get("worker_launch_cwd") or shell_root)
    target_command_cwd = str(agent_cwd_boundary.get("target_command_cwd") or worker_launch_cwd)
    agent_mount_resolution = (
        root_envelope.get("codex_agent_mount_resolution")
        if isinstance(root_envelope.get("codex_agent_mount_resolution"), Mapping)
        else None
    )
    codex_project_cwd = _codex_project_cwd_for_run(
        shell_root,
        worker_launch_cwd=worker_launch_cwd,
        agent_mount_resolution=agent_mount_resolution,
    )
    codex_config_path = Path(codex_project_cwd).expanduser().resolve(strict=False) / ".codex/config.toml"
    spawn_contract["codex_launch_boundary"] = {
        "schema_id": "ion.codex_queue_runner_codex_launch_boundary.v0_1",
        "launch_policy": "active_root_codex_config_with_generated_mount_context"
        if codex_project_cwd != str(Path(worker_launch_cwd).expanduser().resolve(strict=False))
        else "worker_launch_cwd_codex_config",
        "codex_project_cwd": codex_project_cwd,
        "context_mount_cwd": worker_launch_cwd if codex_project_cwd != str(Path(worker_launch_cwd).expanduser().resolve(strict=False)) else None,
        "worker_launch_cwd": worker_launch_cwd,
        "target_command_cwd": target_command_cwd,
        "codex_config_path": str(codex_config_path),
        "codex_config_exists": codex_config_path.exists(),
        "hook_trust_surface": "codex_project_cwd_config",
        "context_binding_surface": "worker_launch_cwd",
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
    }
    prompt = _build_prompt(
        request,
        request_rel,
        _connector_rel(context_receipt_path, shell_root),
        _connector_rel(task_return_body_path, shell_root),
        model_move,
        spawn_contract,
    )
    prompt_path.write_text(prompt, encoding="utf-8")
    last_message_rel = _connector_rel(last_message_path, shell_root)
    task_return_body_rel = _connector_rel(task_return_body_path, shell_root)
    service_tier = _codex_service_tier_for_request(request)
    codex_command = _codex_command(
        codex_binary,
        model_move,
        str(last_message_path.resolve(strict=False)),
        codex_project_cwd=codex_project_cwd,
        service_tier=service_tier,
        disable_image_generation=_disable_image_generation_for_request(request),
    )
    run = {
        "schema_id": "ion.codex_queue_runner_run.v1",
        "run_id": run_id,
        "created_at": now,
        "updated_at": now,
        "status": "CLAIMED_BY_CODEX_QUEUE_RUNNER" if claim else "PREPARED_NOT_STARTED",
        "request_id": request.get("request_id"),
        "request_path": request_rel,
        "lane_id": selected_lane_id,
        "domain_id": worker_identity.get("domain_id"),
        "role_id": worker_identity.get("role_id"),
        "role_tier": worker_identity.get("role_tier"),
        "callsign": worker_identity.get("callsign"),
        "active_root_proof": active_root_proof,
        "worker_identity": worker_identity,
        "domain_alignment": domain_alignment,
        "lane_route": lane_route,
        "run_dir": _connector_rel(run_dir, shell_root),
        "prompt_path": _connector_rel(prompt_path, shell_root),
        "context_receipt_path": _connector_rel(context_receipt_path, shell_root),
        "stdout_path": _connector_rel(stdout_path, shell_root),
        "stderr_path": _connector_rel(stderr_path, shell_root),
        "last_message_path": last_message_rel,
        "task_return_body_path": task_return_body_rel,
        "run_packet_path": run_packet_rel,
        "disable_image_generation": _disable_image_generation_for_request(request),
        "worker_context_awareness_receipt_path": _connector_rel(worker_context_awareness_receipt_path, shell_root),
        "codex_model_move": model_move,
        "codex_model_move_summary": summarize_model_move(model_move),
        "codex_model_override_receipt": model_override_receipt,
        "route_enforcement_receipt": route_enforcement_receipt,
        "ai_movement_preflight": ai_movement_preflight,
        "ai_movement_preflight_receipt_path": preflight_receipt_rel,
        "agent_cwd_boundary": agent_cwd_boundary,
        "codex_agent_mount_resolution": root_envelope.get("codex_agent_mount_resolution"),
        "codex_agent_mount_id": root_envelope.get("codex_agent_mount_id"),
        "codex_agent_mount_manifest": root_envelope.get("codex_agent_mount_manifest"),
        "domain_context_package": root_envelope.get("domain_context_package"),
        "worker_launch_cwd": worker_launch_cwd,
        "target_command_cwd": target_command_cwd,
        "codex_project_cwd": codex_project_cwd,
        "codex_service_tier": service_tier,
        "codex_command": codex_command,
        "codex_cli_launch_profile": _codex_cli_launch_profile(
            worker_launch_cwd=worker_launch_cwd,
            target_command_cwd=target_command_cwd,
            codex_project_cwd=codex_project_cwd,
            codex_command=codex_command,
        ),
        "worker_spawn_contract": spawn_contract,
        "worker_return_status": {
            "schema_id": "ion.codex_queue_runner.worker_return_status.v0_1_candidate",
            "run_status": "CLAIMED_BY_CODEX_QUEUE_RUNNER" if claim else "PREPARED_NOT_STARTED",
            "result": "CLAIMED_BY_CODEX_QUEUE_RUNNER" if claim else "PREPARED_NOT_STARTED",
            "terminal": False,
            "blockers": [],
            "carrier_intake_only": True,
            "product_state": False,
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
        },
        "timeout_seconds": timeout,
        "failure_classification": None,
        "production_authority": False,
        "live_execution_authority": False,
    }
    _write_run_packet(run_packet_path, run)
    _, awareness_sha, awareness_receipt = _write_worker_context_awareness_receipt(
        shell_root,
        run_packet_rel,
        run,
    )
    if claim:
        request["status"] = "CLAIMED_BY_CODEX_QUEUE_RUNNER"
        request["updated_at"] = now
        request["lane_id"] = selected_lane_id
        request["domain_id"] = request.get("domain_id") or worker_identity.get("domain_id")
        request["role_id"] = request.get("role_id") or worker_identity.get("role_id")
        request["role_tier"] = request.get("role_tier") or worker_identity.get("role_tier")
        request["callsign"] = request.get("callsign") or worker_identity.get("callsign")
        request["active_root_proof"] = active_root_proof
        request["worker_identity"] = worker_identity
        request["domain_alignment"] = domain_alignment
        request["worker_return_status"] = _worker_return_status_for_run(run)
        request["work_lane_route_receipt"] = lane_route
        runs = list(request.get("codex_queue_runner_runs") or [])
        runs.append(_connector_rel(run_packet_path, shell_root))
        request["codex_queue_runner_runs"] = runs
        _write_json(selected, request)
        _refresh_codex_work_queue_index(shell_root)
    return {
        "schema_id": SCHEMA_ID,
        "ok": True,
        "run": run,
        "context_receipt": context_receipt,
        "worker_context_awareness_receipt": awareness_receipt,
        "worker_context_awareness_receipt_sha256": awareness_sha,
        "prepared_only": not claim,
        "production_authority": False,
        "live_execution_authority": False,
    }


def stop_active_codex_queue_runner(
    root: str | Path | None = None,
    *,
    confirmation: str,
    reason: str | None = None,
) -> dict[str, Any]:
    if confirmation != CODEX_QUEUE_RUNNER_STOP_CONFIRMATION:
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "finding": "stop_confirmation_required",
            "required_confirmation": CODEX_QUEUE_RUNNER_STOP_CONFIRMATION,
            "production_authority": False,
            "live_execution_authority": False,
        }
    shell_root = _resolve_root(root)
    status = build_codex_queue_runner_status(shell_root, reconcile=True)
    entries = [
        dict(row)
        for row in (status.get("active_runs") or [])
        if isinstance(row, Mapping)
    ]
    if not entries and isinstance(status.get("active_run"), Mapping):
        entries = [dict(status["active_run"])]
    running_entries = []
    for entry in entries:
        try:
            pid = int(entry.get("pid")) if entry.get("pid") else None
        except (TypeError, ValueError):
            pid = None
        if _pid_running(pid):
            entry["pid"] = pid
            running_entries.append(entry)
    if not running_entries:
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "finding": "no_active_codex_agent",
            "runner_status": status,
            "production_authority": False,
            "live_execution_authority": False,
        }
    stopped: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    now = _now()
    for entry in running_entries:
        pid = int(entry["pid"])
        if pid <= 1 or pid == os.getpid():
            blocked.append({"pid": pid, "finding": "protected_pid"})
            continue
        run_rel = str(entry.get("run_packet_path") or "")
        run_path = None
        run: dict[str, Any] = {}
        if run_rel:
            try:
                run_path = _safe_rel_path(shell_root, run_rel)
                loaded = _read_json(run_path)
                if isinstance(loaded, dict):
                    run = loaded
            except ValueError:
                blocked.append({"pid": pid, "finding": "run_packet_path_not_repo_relative", "run_packet_path": run_rel})
                continue
        try:
            try:
                os.killpg(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            except OSError:
                os.kill(pid, signal.SIGTERM)
        except OSError as exc:
            blocked.append({"pid": pid, "finding": "stop_signal_failed", "error": exc.__class__.__name__})
            continue
        if run_path and run:
            previous_status = str(run.get("status") or "")
            run["status"] = OPERATOR_STOPPED_STATUS
            run["completed_at"] = now
            run["failure_classification"] = "OPERATOR_STOPPED"
            run["operator_stop"] = {
                "stopped_at": now,
                "reason": str(reason or "operator_stop_from_cockpit").strip() or "operator_stop_from_cockpit",
                "previous_status": previous_status,
                "pid": pid,
            }
            _append_worker_lifecycle_event(
                run,
                "worker_operator_stop_requested",
                terminal_state="operator_stopped",
                previous_status=previous_status,
                pid=pid,
            )
            _write_run_packet(run_path, run)
            request_rel = str(run.get("request_path") or entry.get("request_path") or "")
            if request_rel:
                _update_request_status(
                    shell_root,
                    request_rel,
                    status=OPERATOR_STOPPED_STATUS,
                    failure_classification="OPERATOR_STOPPED",
                )
        stopped.append({
            "pid": pid,
            "run_packet_path": run_rel or None,
            "request_path": entry.get("request_path"),
            "lane_id": entry.get("lane_id"),
        })
    remaining_entries = [
        row for row in _running_active_run_entries(_read_json(shell_root / RUNNER_STATE_PATH) or {})
        if int(row.get("pid") or 0) not in {int(item["pid"]) for item in stopped if item.get("pid")}
    ]
    latest_run = stopped[-1].get("run_packet_path") if stopped else str(status.get("latest_run") or "") or None
    _update_runner_state(
        shell_root,
        _state_for_active_entries(
            remaining_entries,
            latest_run=str(latest_run) if latest_run else None,
            latest_worker_lifecycle_event={
                "event": "operator_stop_requested",
                "stopped_at": now,
                "stopped_count": len(stopped),
                "blocked_count": len(blocked),
            },
        ),
    )
    return {
        "schema_id": SCHEMA_ID,
        "ok": bool(stopped),
        "result": "CODEX_AGENT_STOP_REQUESTED" if stopped else "CODEX_AGENT_STOP_NOT_APPLIED",
        "stopped": stopped,
        "blocked": blocked,
        "stopped_count": len(stopped),
        "blocked_count": len(blocked),
        "runner_status": build_codex_queue_runner_status(shell_root, reconcile=False),
        "production_authority": False,
        "live_execution_authority": False,
    }


def _update_runner_state(root: Path, state: Mapping[str, Any]) -> None:
    payload = dict(state)
    payload.setdefault("schema_id", "ion.codex_queue_runner_state.v1")
    payload["updated_at"] = _now()
    payload.setdefault("production_authority", False)
    payload.setdefault("live_execution_authority", False)
    entries = _active_run_entries(payload)
    if entries or "active_runs" in payload or "active_run" in payload:
        payload["active_runs"] = {_active_run_key(row): dict(row) for row in entries if _active_run_key(row)}
        payload["active_run"] = _latest_active_entry(entries)
        payload["active_lane_locks"] = _lane_lock_index(entries)
        payload["concurrency"] = _concurrency_summary(entries)
    _write_json(root / RUNNER_STATE_PATH, payload)


def _queueable_request_payloads(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    requests_root = root / CODEX_WORK_REQUESTS_DIR
    if not requests_root.is_dir():
        return []
    rows: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(requests_root.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(payload, Mapping):
            continue
        if str(payload.get("status") or "").strip() != "QUEUED_FOR_CODEX_CARRIER":
            continue
        payload = dict(payload)
        payload.setdefault("request_path", path.relative_to(root).as_posix())
        rows.append((path, dict(payload)))
    return rows


def _request_first_string(payload: Mapping[str, Any], fields: tuple[str, ...]) -> str:
    for field in fields:
        value = payload.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for field in ("routing", "route", "context", "metadata", "domain_weaver", "worker", "request", "payload"):
        value = payload.get(field)
        if isinstance(value, Mapping):
            found = _request_first_string(value, fields)
            if found:
                return found
    return ""


def _request_payload_for_start_gate(root: Path, request_path: str | None, lane_id: str | None) -> tuple[dict[str, Any] | None, str | None]:
    requested = _clean_path_value(str(request_path or "").strip())
    if requested:
        path = (root / requested).resolve(strict=False)
        requests_root = (root / CODEX_WORK_REQUESTS_DIR).resolve(strict=False)
        try:
            path.relative_to(requests_root)
        except ValueError:
            return None, "request_path_outside_codex_work_requests"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            return None, "request_path_unreadable_for_context_gate"
        if not isinstance(payload, Mapping):
            return None, "request_path_payload_invalid_for_context_gate"
        if str(payload.get("status") or "").strip() != "QUEUED_FOR_CODEX_CARRIER":
            return None, "request_path_not_queueable_for_context_gate"
        payload = dict(payload)
        payload.setdefault("request_path", path.relative_to(root).as_posix())
        return payload, None
    if lane_id:
        matches = [
            payload
            for _, payload in _queueable_request_payloads(root)
            if str(classify_codex_work_request_lane(payload).get("lane_id") or "").strip() == lane_id
        ]
        if len(matches) == 1:
            return matches[0], None
        if len(matches) > 1:
            return None, "multiple_queueable_requests_for_lane_require_explicit_request_path"
        return None, "no_queueable_request_for_lane"
    queueable = _queueable_request_payloads(root)
    if len(queueable) == 1:
        return queueable[0][1], None
    if len(queueable) > 1:
        return None, "multiple_queueable_requests_require_lane_or_request_path"
    return None, "no_queueable_request_for_context_gate"


def _codex_worker_start_context_gate(
    root: Path,
    *,
    request_path: str | None,
    lane_id: str | None,
) -> dict[str, Any]:
    active_root_proof = _active_root_proof(root)
    request_payload, finding = _request_payload_for_start_gate(root, request_path, lane_id)
    if finding:
        return {
            "schema_id": "ion.codex_queue_runner.worker_start_context_gate.v0_1",
            "ok": False,
            "finding": finding,
            "request_path": request_path,
            "lane_id": lane_id,
            "active_root_proof": active_root_proof,
            "worker_identity": _worker_identity_for_request({}, lane_id=lane_id),
            "production_authority": False,
            "live_execution_authority": False,
        }
    lane_route = classify_codex_work_request_lane(request_payload or {})
    classified_lane = str(lane_route.get("lane_id") or "").strip()
    raw_request_lane = str((request_payload or {}).get("lane_id") or lane_id or "").strip()
    request_lane = normalize_codex_work_lane_id(raw_request_lane or None) or classified_lane
    worker_identity = _worker_identity_for_request(request_payload or {}, lane_id=request_lane, lane_route=lane_route)
    if not request_lane:
        return {
            "schema_id": "ion.codex_queue_runner.worker_start_context_gate.v0_1",
            "ok": False,
            "finding": "queue_worker_start_lane_id_required_for_context_gate",
            "request_path": request_path,
            "active_root_proof": active_root_proof,
            "worker_identity": worker_identity,
            "production_authority": False,
            "live_execution_authority": False,
        }
    request_domain = _request_first_string(request_payload or {}, DOMAIN_REQUEST_FIELDS)
    request_role = _request_first_string(request_payload or {}, AGENT_ROLE_REQUEST_FIELDS)
    request_role_tier = _request_first_string(request_payload or {}, ROLE_TIER_REQUEST_FIELDS)
    request_callsign = _request_first_string(request_payload or {}, CALLSIGN_REQUEST_FIELDS)
    domain_alignment = _worker_domain_alignment(request_domain)
    if not request_domain:
        return {
            "schema_id": "ion.codex_queue_runner.worker_start_context_gate.v0_1",
            "ok": False,
            "finding": "queue_worker_start_domain_id_required_for_context_gate",
            "lane_id": request_lane,
            "request_id": (request_payload or {}).get("request_id"),
            "request_path": request_path or (request_payload or {}).get("request_path"),
            "active_root_proof": active_root_proof,
            "worker_identity": worker_identity,
            "domain_alignment": domain_alignment,
            "production_authority": False,
            "live_execution_authority": False,
        }
    resolver = resolve_domain_active_context(
        root,
        domain_id=request_domain,
        role_id=request_role or None,
        lane=request_lane,
    )
    if not resolver.get("ok"):
        return {
            "schema_id": "ion.codex_queue_runner.worker_start_context_gate.v0_1",
            "ok": False,
            "finding": "worker_start_context_active_resolver_blocked",
            "lane_id": request_lane,
            "domain_id": request_domain,
            "role_id": request_role or None,
            "role_tier": request_role_tier or None,
            "callsign": request_callsign or None,
            "request_id": (request_payload or {}).get("request_id"),
            "request_path": request_path or (request_payload or {}).get("request_path"),
            "context_active_resolver": resolver,
            "active_root_proof": active_root_proof,
            "worker_identity": worker_identity,
            "domain_alignment": domain_alignment,
            "worker_return_status": _worker_return_status_for_run(
                {
                    "status": "CODEX_QUEUE_RUNNER_BLOCKED_CONTEXT_GATE",
                    "failure_classification": "CONTEXT_ACTIVE_RESOLVER_BLOCKED",
                },
                context_gate={
                    "finding": "worker_start_context_active_resolver_blocked",
                    "context_active_resolver": resolver,
                },
            ),
            "production_authority": False,
            "live_execution_authority": False,
        }
    return {
        "schema_id": "ion.codex_queue_runner.worker_start_context_gate.v0_1",
        "ok": True,
        "lane_id": request_lane,
        "domain_id": request_domain,
        "role_id": request_role or None,
        "role_tier": request_role_tier or None,
        "callsign": request_callsign or None,
        "request_id": (request_payload or {}).get("request_id"),
        "request_path": request_path or (request_payload or {}).get("request_path"),
        "context_active_resolver": resolver,
        "active_root_proof": active_root_proof,
        "worker_identity": worker_identity,
        "domain_alignment": domain_alignment,
        "worker_return_status": _worker_return_status_for_run(
            {"status": "WORKER_START_CONTEXT_GATE_READY"},
            result="WORKER_START_CONTEXT_GATE_READY",
        ),
        "production_authority": False,
        "live_execution_authority": False,
    }


def process_codex_queue_once(
    root: str | Path | None = None,
    *,
    request_path: str | None = None,
    lane_id: str | None = None,
    start: bool = False,
    background: bool = True,
    codex_binary: str = "codex",
    timeout_seconds: int = DEFAULT_CODEX_TIMEOUT_SECONDS,
    task_output_override: str | None = None,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    status = build_codex_queue_runner_status(shell_root)
    running_entries = [
        dict(row)
        for row in (status.get("active_runs") or [])
        if isinstance(row, Mapping)
    ]
    explicit_request = bool(str(request_path or "").strip())
    normalized_lane_id = normalize_codex_work_lane_id(lane_id) if lane_id else None
    if lane_id and not normalized_lane_id:
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "finding": "lane_id_not_supported",
            "lane_id": lane_id,
            "supported_lane_ids": list(CODEX_WORK_LANES),
            "production_authority": False,
            "live_execution_authority": False,
        }
    if start and status.get("active_process_running") and not explicit_request and not normalized_lane_id:
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "finding": "codex_queue_runner_already_active",
            "active_run": status.get("active_run"),
            "active_runs": running_entries,
            "production_authority": False,
            "live_execution_authority": False,
        }
    lock_lane_id = normalized_lane_id or (_explicit_request_lane_id(shell_root, request_path) if explicit_request else None)
    if start and lock_lane_id:
        active_same_lane = [
            row for row in running_entries
            if str(row.get("lane_id") or "") == lock_lane_id
        ]
        active_unknown_lane = [
            row for row in running_entries
            if not str(row.get("lane_id") or "").strip()
        ]
        if active_same_lane or active_unknown_lane:
            return {
                "schema_id": SCHEMA_ID,
                "ok": False,
                "finding": "codex_queue_lane_already_active",
                "lane_id": lock_lane_id,
                "active_runs": active_same_lane or active_unknown_lane,
                "production_authority": False,
                "live_execution_authority": False,
            }
    if start and explicit_request:
        requested_rel = _clean_path_value(str(request_path or "").strip())
        already_running = [
            row for row in running_entries
            if _clean_path_value(str(row.get("request_path") or "").strip()) == requested_rel
        ]
        if already_running:
            return {
                "schema_id": SCHEMA_ID,
                "ok": False,
                "finding": "codex_queue_request_already_active",
                "request_path": requested_rel,
                "active_runs": already_running,
                "production_authority": False,
                "live_execution_authority": False,
            }
    if start:
        context_gate = _codex_worker_start_context_gate(
            shell_root,
            request_path=request_path,
            lane_id=normalized_lane_id,
        )
        if not context_gate.get("ok"):
            blocked_request_path = str(context_gate.get("request_path") or request_path or "").strip()
            if blocked_request_path:
                _update_request_status(
                    shell_root,
                    blocked_request_path,
                    status="CODEX_QUEUE_RUNNER_BLOCKED_CONTEXT_GATE",
                    failure_classification="CONTEXT_ACTIVE_RESOLVER_BLOCKED",
                    context_gate=context_gate,
                )
            return {
                "schema_id": SCHEMA_ID,
                "ok": False,
                "result": "WORKER_START_CONTEXT_GATE_BLOCKED",
                "finding": context_gate.get("finding") or "worker_start_context_gate_blocked",
                "context_gate": context_gate,
                "active_root_proof": context_gate.get("active_root_proof"),
                "worker_identity": context_gate.get("worker_identity"),
                "domain_alignment": context_gate.get("domain_alignment"),
                "worker_return_status": context_gate.get("worker_return_status") or _worker_return_status_for_run(
                    {
                        "status": "CODEX_QUEUE_RUNNER_BLOCKED_CONTEXT_GATE",
                        "failure_classification": "CONTEXT_ACTIVE_RESOLVER_BLOCKED",
                    },
                    result="WORKER_START_CONTEXT_GATE_BLOCKED",
                    context_gate=context_gate,
                ),
                "production_authority": False,
                "live_execution_authority": False,
            }
    prepared = prepare_codex_queue_run(
        shell_root,
        request_path=request_path,
        lane_id=normalized_lane_id,
        claim=start,
        codex_binary=codex_binary,
        timeout_seconds=timeout_seconds,
    )
    if not prepared.get("ok") or not start:
        return prepared
    run = dict(prepared["run"])
    run_packet = shell_root / str(run["run_packet_path"])
    awareness_receipt_rel, awareness_receipt_sha, awareness_receipt = _write_worker_context_awareness_receipt(
        shell_root,
        str(run["run_packet_path"]),
        run,
    )
    sign_in_status = str(awareness_receipt.get("status") or WORKER_CONTEXT_BLOCKED)
    _append_worker_lifecycle_event(
        run,
        "worker_sign_in_context_awareness",
        worker_sign_in_status=sign_in_status,
        worker_context_awareness_receipt_path=awareness_receipt_rel,
        worker_context_awareness_receipt_sha256=awareness_receipt_sha,
    )
    if sign_in_status != WORKER_CONTEXT_ACKNOWLEDGED:
        run["status"] = "WORKER_CONTEXT_MOUNT_INVALID"
        run["failure_classification"] = "CARRIER_ADAPTER_FAILURE"
        run["completed_at"] = _now()
        run["worker_return_status"] = _worker_return_status_for_run(run)
        _write_run_packet(run_packet, run)
        _update_request_status(
            shell_root,
            str(run["request_path"]),
            status="CODEX_QUEUE_RUNNER_FAILED",
            failure_classification="CARRIER_ADAPTER_FAILURE",
        )
        remaining_entries = _current_running_entries_without(shell_root, _active_entry_for_run(run))
        _update_runner_state(
            shell_root,
            _state_for_active_entries(
                remaining_entries,
                latest_run=run["run_packet_path"],
                latest_worker_lifecycle_event=run["worker_lifecycle_events"][-1],
            ),
        )
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "result": "WORKER_CONTEXT_MOUNT_INVALID",
            "finding": "worker_context_awareness_receipt_blocked",
            "run": run,
            "active_root_proof": run.get("active_root_proof"),
            "worker_identity": run.get("worker_identity"),
            "domain_alignment": run.get("domain_alignment"),
            "worker_return_status": run.get("worker_return_status"),
            "worker_context_awareness_receipt_path": awareness_receipt_rel,
            "worker_context_awareness_receipt_sha256": awareness_receipt_sha,
            "worker_context_awareness_receipt": awareness_receipt,
            "production_authority": False,
            "live_execution_authority": False,
        }
    lease = _claim_codex_queue_run_lease(shell_root, run)
    run["worker_shift_lease"] = lease
    if not lease.get("ok"):
        run["status"] = WORKER_SHIFT_LEASE_BLOCKED_STATUS
        run["failure_classification"] = "CARRIER_ADAPTER_FAILURE"
        run["completed_at"] = _now()
        run["worker_return_status"] = _worker_return_status_for_run(run)
        _write_run_packet(run_packet, run)
        _update_request_status(
            shell_root,
            str(run["request_path"]),
            status="CODEX_QUEUE_RUNNER_FAILED",
            failure_classification="CARRIER_ADAPTER_FAILURE",
        )
        remaining_entries = _current_running_entries_without(shell_root, _active_entry_for_run(run))
        _update_runner_state(
            shell_root,
            _state_for_active_entries(
                remaining_entries,
                latest_run=run["run_packet_path"],
            ),
        )
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "result": WORKER_SHIFT_LEASE_BLOCKED_STATUS,
            "finding": lease.get("finding") or "worker_shift_lease_claim_blocked",
            "run": run,
            "worker_shift_lease": lease,
            "active_root_proof": run.get("active_root_proof"),
            "worker_identity": run.get("worker_identity"),
            "domain_alignment": run.get("domain_alignment"),
            "worker_return_status": run.get("worker_return_status"),
            "production_authority": False,
            "live_execution_authority": False,
        }
    _write_run_packet(run_packet, run)
    if background:
        env = os.environ.copy()
        packages = str(shell_root / "ION/04_packages")
        env["PYTHONPATH"] = f"{packages}:{env.get('PYTHONPATH', '')}" if env.get("PYTHONPATH") else packages
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        cmd = [
            sys.executable,
            "-S",
            "-m",
            "kernel.ion_codex_queue_runner",
            "--ion-root",
            str(shell_root),
            "--worker-run",
            str(run_packet.relative_to(shell_root)),
            "--json",
        ]
        stdout = (run_packet.parent / "worker_stdout.log").open("wb")
        stderr = (run_packet.parent / "worker_stderr.log").open("wb")
        proc = subprocess.Popen(cmd, cwd=shell_root, stdout=stdout, stderr=stderr, env=env, start_new_session=True)
        _, awareness_receipt_sha, awareness_receipt = _write_worker_context_awareness_receipt(
            shell_root,
            str(run["run_packet_path"]),
            run,
            worker_pid_or_process_ref=proc.pid,
            started_at=_now(),
        )
        run["status"] = "CODEX_QUEUE_RUNNER_WORKER_STARTED"
        run["pid"] = proc.pid
        run["worker_command"] = cmd
        run["worker_return_status"] = _worker_return_status_for_run(run)
        _append_worker_lifecycle_event(
            run,
            "worker_process_spawned",
            worker_pid=proc.pid,
            worker_context_awareness_receipt_sha256=awareness_receipt_sha,
            worker_sign_in_status=str(awareness_receipt.get("status") or None),
        )
        _write_run_packet(run_packet, run)
        active_entry = _active_entry_for_run(run, pid=proc.pid, started_at=_now())
        active_entries = _current_running_entries_with(shell_root, active_entry)
        _update_runner_state(shell_root, _state_for_active_entries(active_entries, latest_run=run["run_packet_path"]))
        return {
            "schema_id": SCHEMA_ID,
            "ok": True,
            "result": "CODEX_QUEUE_RUNNER_WORKER_STARTED",
            "run": run,
            "active_root_proof": run.get("active_root_proof"),
            "worker_identity": run.get("worker_identity"),
            "domain_alignment": run.get("domain_alignment"),
            "worker_return_status": run.get("worker_return_status"),
            "manual_proceed_relay_required": False,
            "production_authority": False,
            "live_execution_authority": False,
        }
    worker = run_codex_queue_worker(shell_root, run_packet, task_output_override=task_output_override)
    return {
        "schema_id": SCHEMA_ID,
        "ok": bool(worker.get("ok")),
        "result": worker.get("result"),
        "run": worker.get("run"),
        "submit_result": worker.get("submit_result"),
        "active_root_proof": (worker.get("run") or {}).get("active_root_proof") if isinstance(worker.get("run"), Mapping) else None,
        "worker_identity": (worker.get("run") or {}).get("worker_identity") if isinstance(worker.get("run"), Mapping) else None,
        "domain_alignment": (worker.get("run") or {}).get("domain_alignment") if isinstance(worker.get("run"), Mapping) else None,
        "worker_return_status": (worker.get("run") or {}).get("worker_return_status") if isinstance(worker.get("run"), Mapping) else None,
        "manual_proceed_relay_required": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _update_request_status(
    root: Path,
    request_rel: str,
    *,
    status: str,
    failure_classification: str | None = None,
    context_gate: Mapping[str, Any] | None = None,
    carrier_session_recovery: Mapping[str, Any] | None = None,
) -> None:
    request_path = root / request_rel
    payload = _load_request(request_path)
    payload["status"] = status
    payload["updated_at"] = _now()
    if failure_classification:
        payload["failure_classification"] = failure_classification
    if context_gate:
        payload["context_gate"] = dict(context_gate)
    if carrier_session_recovery:
        payload["carrier_session_recovery"] = dict(carrier_session_recovery)
    _write_json(request_path, payload)
    _refresh_codex_work_queue_index(root)


def _sync_domain_weaver_agent_comms_task_return(
    root: Path,
    *,
    request: Mapping[str, Any],
    request_rel: str,
    run: Mapping[str, Any],
    submit_data: Mapping[str, Any],
) -> dict[str, Any]:
    annotation = request.get("domain_weaver_agent_comms_dispatch")
    if not isinstance(annotation, Mapping):
        annotation = {}
    thread_id = str(
        annotation.get("source_agent_comms_thread_id")
        or request.get("source_agent_comms_thread_id")
        or ""
    ).strip()
    source_message_id = str(
        annotation.get("source_agent_comms_message_id")
        or request.get("source_agent_comms_message_id")
        or ""
    ).strip()
    task_return_path = str(submit_data.get("packet_path") or "").strip()
    if not thread_id or not source_message_id or not task_return_path:
        return {
            "schema_id": "ion.domain_weaver.agent_comms_task_return_sync.v0_1",
            "ok": False,
            "attempted": False,
            "finding": "domain_weaver_agent_comms_sync_not_applicable",
            "thread_id": thread_id or None,
            "source_message_id": source_message_id or None,
            "task_return_packet_path": task_return_path or None,
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
        }
    from .ion_agent_comms import send_agent_message

    machine_receipt_path = str(submit_data.get("machine_receipt_path") or "").strip()
    source_refs = [
        ref
        for ref in [
            str(annotation.get("source_agent_comms_message_path") or request.get("source_agent_comms_message_path") or "").strip(),
            str(annotation.get("source_agent_comms_inbox_ref") or request.get("source_agent_comms_inbox_ref") or "").strip(),
            str(annotation.get("pickup_receipt_path") or request.get("pickup_receipt_path") or "").strip(),
            request_rel,
            str(run.get("run_packet_path") or "").strip(),
            task_return_path,
            machine_receipt_path,
        ]
        if ref
    ]
    result = send_agent_message(
        root,
        {
            "from_role": str(run.get("role_id") or request.get("agent_role_id") or request.get("agent_role") or "role.codex_carrier_steward"),
            "to_roles": ["role.codex_carrier_steward"],
            "thread_id": thread_id,
            "channel_id": "team",
            "subject": f"Synced task return for {source_message_id}",
            "body": (
                "Domain Weaver carrier-intake task return was recorded for the source comms message.\n\n"
                f"- source_message_id: {source_message_id}\n"
                f"- task_return_packet_path: {task_return_path}\n"
                f"- machine_receipt_path: {machine_receipt_path or 'not_recorded'}\n"
                "- boundary: synced reply only after accepted carrier-intake proof; not production/live/accepted-state authority."
            ),
            "message_kind": "answer",
            "requires_response": False,
            "source_refs": source_refs,
            "artifact_refs": [task_return_path],
            "receipt_refs": [machine_receipt_path] if machine_receipt_path else [],
            "domain_id": str(request.get("domain_id") or run.get("domain_id") or ""),
            "summary": "Accepted carrier-intake task return synced back to source Domain Weaver comms thread.",
            "emit_signal": True,
            "authority_boundary": "carrier_intake_sync_reply_not_product_state",
        },
    )
    return {
        "schema_id": "ion.domain_weaver.agent_comms_task_return_sync.v0_1",
        "ok": result.get("ok") is True,
        "attempted": True,
        "finding": result.get("finding") or ("synced_reply_written" if result.get("ok") else "synced_reply_failed"),
        "sync_kind": "synced_reply",
        "thread_id": thread_id,
        "source_message_id": source_message_id,
        "task_return_packet_path": task_return_path,
        "machine_receipt_path": machine_receipt_path or None,
        "synced_reply_message_id": result.get("message_id"),
        "synced_reply_message_path": result.get("message_path"),
        "synced_reply_signal_path": result.get("signal_path"),
        "send_result": result,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def requeue_codex_transient_usage_limit_request(
    root: str | Path | None = None,
    *,
    run_packet_path: str,
    confirmation: str,
    start: bool = False,
    background: bool = True,
    codex_binary: str = "codex",
    timeout_seconds: int = DEFAULT_CODEX_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    if confirmation != CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_CONFIRMATION:
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_SCHEMA_ID,
            "ok": False,
            "result": "CONFIRMATION_REQUIRED",
            "required_confirmation": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_CONFIRMATION,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    clean_run_rel = _clean_path_value(str(run_packet_path or "").strip())
    if not clean_run_rel:
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_SCHEMA_ID,
            "ok": False,
            "result": "RUN_PACKET_PATH_REQUIRED",
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    try:
        run_path = _safe_rel_path(shell_root, clean_run_rel)
    except ValueError:
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_SCHEMA_ID,
            "ok": False,
            "result": "RUN_PACKET_PATH_OUTSIDE_ROOT",
            "run_packet_path": clean_run_rel,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    run = _read_json(run_path)
    if not isinstance(run, Mapping):
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_SCHEMA_ID,
            "ok": False,
            "result": "RUN_PACKET_UNREADABLE",
            "run_packet_path": clean_run_rel,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    request_rel = _clean_path_value(str(run.get("request_path") or "").strip())
    projection = _transient_usage_limit_recovery_projection(shell_root, run, request_rel=request_rel)
    if not projection.get("eligible"):
        if projection.get("recovery_exhausted"):
            return {
                "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_SCHEMA_ID,
                "ok": False,
                "result": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_EXHAUSTED,
                "request_path": request_rel,
                "recovery_count": projection.get("request_recovery_count"),
                "max_requeues_per_request": MAX_CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_REQUEUES,
                "carrier_session_recovery": projection,
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_claim": False,
            }
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_SCHEMA_ID,
            "ok": False,
            "result": "RUN_NOT_ELIGIBLE_FOR_TRANSIENT_USAGE_LIMIT_RECOVERY",
            "carrier_session_recovery": projection,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    try:
        request_path = _safe_rel_path(shell_root, request_rel)
    except ValueError:
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_SCHEMA_ID,
            "ok": False,
            "result": "REQUEST_PATH_OUTSIDE_ROOT",
            "request_path": request_rel,
            "carrier_session_recovery": projection,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    request = _read_json(request_path)
    if not isinstance(request, Mapping):
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_SCHEMA_ID,
            "ok": False,
            "result": "REQUEST_UNREADABLE",
            "request_path": request_rel,
            "carrier_session_recovery": projection,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    state = _read_json(shell_root / RUNNER_STATE_PATH) or {}
    active_same_request = [
        dict(entry)
        for entry in _active_run_entries(state)
        if _clean_path_value(str(entry.get("request_path") or "").strip()) == request_rel
    ]
    if active_same_request:
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_SCHEMA_ID,
            "ok": False,
            "result": "ACTIVE_SAME_REQUEST_WORKER_PRESENT",
            "request_path": request_rel,
            "active_runs": active_same_request,
            "carrier_session_recovery": projection,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    history = [
        dict(item)
        for item in (request.get("carrier_session_recovery_history") or [])
        if isinstance(item, Mapping)
    ]
    already_requeued = any(
        str(item.get("recovery_id") or "") == str(projection.get("recovery_id") or "")
        for item in history
    ) and str(request.get("status") or "").strip() == "QUEUED_FOR_CODEX_CARRIER"
    if already_requeued:
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_SCHEMA_ID,
            "ok": True,
            "result": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_ALREADY_REQUEUED,
            "request_path": request_rel,
            "carrier_session_recovery": projection,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    if len(history) >= MAX_CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_REQUEUES:
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_SCHEMA_ID,
            "ok": False,
            "result": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_EXHAUSTED,
            "request_path": request_rel,
            "recovery_count": len(history),
            "max_requeues_per_request": MAX_CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_REQUEUES,
            "carrier_session_recovery": projection,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    previous_status = str(request.get("status") or "").strip()
    previous_failure = str(request.get("failure_classification") or "").strip()
    if previous_status != "CODEX_QUEUE_RUNNER_FAILED" or previous_failure != CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS:
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_SCHEMA_ID,
            "ok": False,
            "result": "REQUEST_NOT_IN_TRANSIENT_USAGE_LIMIT_FAILED_STATE",
            "request_path": request_rel,
            "request_status": previous_status,
            "failure_classification": previous_failure or None,
            "carrier_session_recovery": projection,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    now = _now()
    recovery_record = dict(projection)
    recovery_record.update(
        {
            "performed_at": now,
            "result": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_REQUEUED,
            "previous_request_status": previous_status,
            "new_request_status": "QUEUED_FOR_CODEX_CARRIER",
            "previous_failure_classification": previous_failure,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
        }
    )
    receipt_rel = (Path(clean_run_rel).parent / f"{recovery_record['recovery_id']}.json").as_posix()
    recovery_record["receipt_path"] = receipt_rel
    _write_json(shell_root / receipt_rel, recovery_record)
    request = dict(request)
    history.append(recovery_record)
    request["status"] = "QUEUED_FOR_CODEX_CARRIER"
    request["updated_at"] = now
    request["last_failure_classification"] = previous_failure
    request.pop("failure_classification", None)
    request["carrier_session_recovery"] = recovery_record
    request["carrier_session_recovery_history"] = history
    request["worker_return_status"] = {
        "schema_id": "ion.codex_queue_runner.worker_return_status.v0_1_candidate",
        "run_status": "QUEUED_FOR_CODEX_CARRIER",
        "result": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_REQUEUED,
        "terminal": False,
        "carrier_intake_only": True,
        "product_state_accepted": False,
        "product_state": False,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "blockers": [],
    }
    _write_json(request_path, request)
    _refresh_codex_work_queue_index(shell_root)
    result = {
        "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_SCHEMA_ID,
        "ok": True,
        "result": CODEX_TRANSIENT_USAGE_LIMIT_RECOVERY_REQUEUED,
        "request_path": request_rel,
        "run_packet_path": clean_run_rel,
        "receipt_path": receipt_rel,
        "carrier_session_recovery": recovery_record,
        "start_requested": bool(start),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }
    if start:
        start_result = process_codex_queue_once(
            shell_root,
            request_path=request_rel,
            start=True,
            background=background,
            codex_binary=codex_binary,
            timeout_seconds=timeout_seconds,
        )
        result["start_result"] = start_result
        result["ok"] = bool(start_result.get("ok"))
    return result


def bridge_codex_transient_usage_limit_request(
    root: str | Path | None = None,
    *,
    run_packet_path: str,
    confirmation: str,
    idempotency_key: str,
    bridge_mode: str = "parent_session_relay",
    requested_by: str = "codex_carrier_steward",
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    if confirmation != CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_CONFIRMATION:
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_SCHEMA_ID,
            "ok": False,
            "result": "CONFIRMATION_REQUIRED",
            "required_confirmation": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_CONFIRMATION,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        }
    bridge_key = _clean_path_value(str(idempotency_key or "").strip())
    if not bridge_key:
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_SCHEMA_ID,
            "ok": False,
            "result": "IDEMPOTENCY_KEY_REQUIRED",
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        }
    clean_run_rel = _clean_path_value(str(run_packet_path or "").strip())
    if not clean_run_rel:
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_SCHEMA_ID,
            "ok": False,
            "result": "RUN_PACKET_PATH_REQUIRED",
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        }
    try:
        run_path = _safe_rel_path(shell_root, clean_run_rel)
    except ValueError:
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_SCHEMA_ID,
            "ok": False,
            "result": "RUN_PACKET_PATH_OUTSIDE_ROOT",
            "run_packet_path": clean_run_rel,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        }
    run = _read_json(run_path)
    if not isinstance(run, Mapping):
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_SCHEMA_ID,
            "ok": False,
            "result": "RUN_PACKET_UNREADABLE",
            "run_packet_path": clean_run_rel,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        }
    request_rel = _clean_path_value(str(run.get("request_path") or "").strip())
    projection = _transient_usage_limit_bridge_projection(
        shell_root,
        run,
        request_rel=request_rel,
        idempotency_key=bridge_key,
        bridge_mode=bridge_mode,
    )
    if projection.get("already_created"):
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_SCHEMA_ID,
            "ok": True,
            "result": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_ALREADY_CREATED,
            "request_path": request_rel,
            "run_packet_path": clean_run_rel,
            "receipt_path": projection.get("existing_bridge_receipt_path"),
            "carrier_session_bridge": projection,
            "task_return_created": False,
            "accepted_for_carrier_intake": False,
            "automatic_agent_reaction_proven": False,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        }
    if not projection.get("eligible"):
        result = CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_NOT_ELIGIBLE
        if projection.get("active_same_request_worker_count"):
            result = "ACTIVE_SAME_REQUEST_WORKER_PRESENT"
        elif projection.get("bridge_exhausted"):
            result = CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_EXHAUSTED
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_SCHEMA_ID,
            "ok": False,
            "result": result,
            "request_path": request_rel,
            "run_packet_path": clean_run_rel,
            "carrier_session_bridge": projection,
            "task_return_created": False,
            "accepted_for_carrier_intake": False,
            "automatic_agent_reaction_proven": False,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        }
    try:
        request_path = _safe_rel_path(shell_root, request_rel)
    except ValueError:
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_SCHEMA_ID,
            "ok": False,
            "result": "REQUEST_PATH_OUTSIDE_ROOT",
            "request_path": request_rel,
            "carrier_session_bridge": projection,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        }
    request = _read_json(request_path)
    if not isinstance(request, Mapping):
        return {
            "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_SCHEMA_ID,
            "ok": False,
            "result": "REQUEST_UNREADABLE",
            "request_path": request_rel,
            "carrier_session_bridge": projection,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        }
    request = dict(request)
    annotation = request.get("domain_weaver_agent_comms_dispatch")
    if not isinstance(annotation, Mapping):
        annotation = {}
    source_refs = {
        "request_path": request_rel,
        "source_run_packet_path": clean_run_rel,
        "stdout_path": run.get("stdout_path"),
        "stderr_path": run.get("stderr_path"),
        "last_message_path": run.get("last_message_path"),
        "worker_shift_lease_release_receipt_path": (
            run.get("worker_shift_lease_release") or {}
        ).get("receipt_path") if isinstance(run.get("worker_shift_lease_release"), Mapping) else None,
        "source_agent_comms_message_path": annotation.get("source_agent_comms_message_path") or request.get("source_agent_comms_message_path"),
        "source_agent_comms_pickup_receipt_path": annotation.get("pickup_receipt_path") or request.get("pickup_receipt_path"),
        "source_agent_comms_thread_path": annotation.get("source_agent_comms_thread_path") or request.get("source_agent_comms_thread_path"),
    }
    source_refs = {key: value for key, value in source_refs.items() if value}
    objective = str(request.get("objective") or "")
    bridge_id = str(projection["bridge_id"])
    now = _now()
    receipt_rel = (CODEX_CARRIER_RECOVERY_BRIDGES_DIR / f"{bridge_id}.json").as_posix()
    relay_rel = (DOMAIN_WEAVER_CARRIER_RECOVERY_RELAY_REQUESTS_DIR / f"{bridge_id}.json").as_posix()
    stdout_text = _read_bounded_artifact_text(shell_root, _file_meta(shell_root, str(run.get("stdout_path") or "") or None), max_bytes=4096)
    stderr_text = _read_bounded_artifact_text(shell_root, _file_meta(shell_root, str(run.get("stderr_path") or "") or None), max_bytes=4096)
    last_message_text = _read_bounded_artifact_text(shell_root, _file_meta(shell_root, str(run.get("last_message_path") or "") or None), max_bytes=4096)
    bridge_failure_classification = str(
        projection.get("failure_classification") or run.get("failure_classification") or ""
    ).strip()
    bridge_record = {
        "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_SCHEMA_ID,
        "status": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_CREATED,
        "bridge_id": bridge_id,
        "bridge_mode": bridge_mode,
        "created_at": now,
        "requested_by": requested_by,
        "idempotency_key": bridge_key,
        "request_path": request_rel,
        "source_run_packet_path": clean_run_rel,
        "source_run_status": run.get("status"),
        "failure_classification": bridge_failure_classification or None,
        "source_run_failure_classification": projection.get("source_run_failure_classification"),
        "lineage_failure_classification_basis": projection.get("lineage_failure_classification_basis"),
        "recovery_exhausted": True,
        "same_request_requeue_allowed": False,
        "worker_start_allowed": False,
        "task_return_created": False,
        "creates_task_return": False,
        "accepted_for_carrier_intake": False,
        "automatic_agent_reaction_proven": False,
        "product_state_accepted": False,
        "source_failure_excerpt": _bounded_usage_limit_excerpt(stdout_text, stderr_text, last_message_text),
        "source_request_summary": {
            "request_id": request.get("request_id"),
            "objective": objective[:500],
            "objective_sha256": hashlib.sha256(objective.encode("utf-8", errors="replace")).hexdigest(),
            "work_class": request.get("work_class"),
            "lane_id": run.get("lane_id") or classify_codex_work_request_lane(request).get("lane_id"),
            "domain_id": request.get("domain_id"),
            "agent_role": request.get("agent_role_id") or request.get("agent_role"),
        },
        "source_refs": source_refs,
        "relay_request_path": relay_rel,
        "handoff_contract": {
            "handoff_target": "role.codex_carrier_steward",
            "required_action": "execute_original_objective_or_settle_blocker_in_parent_session",
            "forbidden_actions": [
                "do_not_requeue_same_request",
                "do_not_create_task_return_from_failed_logs",
                "do_not_claim_automatic_agent_reaction",
                "do_not_claim_accepted_state",
                "do_not_materialize_or_register",
            ],
            "completion_requirement": (
                "A future valid task return must be separately produced and pass normal "
                "carrier-intake proof before any comms synced reply is written."
            ),
        },
        "authority": {
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
        "secrets_authority": False,
    }
    relay_request = {
        "schema_id": "ion.domain_weaver.parent_session_relay_request.v0_1",
        "created_at": now,
        "bridge_id": bridge_id,
        "source_message_id": annotation.get("source_agent_comms_message_id") or request.get("source_agent_comms_message_id"),
        "source_thread_id": annotation.get("source_agent_comms_thread_id") or request.get("source_agent_comms_thread_id"),
        "source_request_path": request_rel,
        "source_run_packet": clean_run_rel,
        "bridge_receipt_path": receipt_rel,
        "reason": "codex_carrier_transient_usage_limit_recovery_exhausted",
        "requested_action": "parent_session_review_and_reissue",
        "original_objective": objective,
        "forbidden_actions": [
            "synthesize_task_return_from_failed_log",
            "requeue_same_request",
            "claim_automatic_agent_reaction",
            "claim_accepted_state",
            "materialize_or_register",
        ],
        "authority": {
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    }
    _write_json(shell_root / receipt_rel, bridge_record)
    _write_json(shell_root / relay_rel, relay_request)
    history = [
        dict(item)
        for item in (request.get("carrier_session_bridge_history") or [])
        if isinstance(item, Mapping)
    ]
    history.append(
        {
            "bridge_id": bridge_id,
            "idempotency_key": bridge_key,
            "bridge_mode": bridge_mode,
            "created_at": now,
            "receipt_path": receipt_rel,
            "relay_request_path": relay_rel,
            "task_return_created": False,
            "accepted_for_carrier_intake": False,
            "automatic_agent_reaction_proven": False,
        }
    )
    request["updated_at"] = now
    request["carrier_session_bridge"] = bridge_record
    request["carrier_session_bridge_history"] = history
    request["status"] = str(request.get("status") or "CODEX_QUEUE_RUNNER_FAILED")
    request["failure_classification"] = (
        bridge_failure_classification
        or str(request.get("failure_classification") or CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS)
    )
    request["worker_return_status"] = {
        "schema_id": "ion.codex_queue_runner.worker_return_status.v0_1_candidate",
        "run_status": request["status"],
        "result": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_CREATED,
        "terminal": True,
        "failure_classification": request["failure_classification"],
        "carrier_intake_only": True,
        "product_state_accepted": False,
        "product_state": False,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "blockers": [request["failure_classification"], "valid_task_return_missing"],
    }
    _write_json(request_path, request)
    _refresh_codex_work_queue_index(shell_root)
    return {
        "schema_id": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_SCHEMA_ID,
        "ok": True,
        "result": CODEX_TRANSIENT_USAGE_LIMIT_BRIDGE_CREATED,
        "request_path": request_rel,
        "run_packet_path": clean_run_rel,
        "receipt_path": receipt_rel,
        "relay_request_path": relay_rel,
        "carrier_session_bridge": bridge_record,
        "task_return_created": False,
        "accepted_for_carrier_intake": False,
        "automatic_agent_reaction_proven": False,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
        "secrets_authority": False,
    }


def _reconcile_multi_active_runs(
    root: Path,
    state: Mapping[str, Any],
    *,
    latest_run_rel: str,
    write: bool,
    result: dict[str, Any],
) -> bool:
    if "active_runs" not in state:
        return False
    entries = _active_run_entries(state)
    result["active_run_count_before"] = len(entries)
    result["reconciled_active_runs"] = []
    if not entries:
        return False

    now = _now()
    remaining_entries: list[dict[str, Any]] = []
    stale_count = 0
    terminal_count = 0
    running_count = 0
    latest_touched_run = latest_run_rel or None

    for entry in entries:
        entry_result: dict[str, Any] = {
            "run_id": entry.get("run_id"),
            "request_path": entry.get("request_path"),
            "lane_id": entry.get("lane_id"),
        }
        try:
            active_pid = int(entry.get("pid")) if entry.get("pid") else None
        except (TypeError, ValueError):
            active_pid = None
        active_running = _pid_running(active_pid)
        entry_result["pid"] = active_pid
        entry_result["active_process_running"] = active_running
        run_rel = str(entry.get("run_packet_path") or "").strip()
        if not run_rel:
            if active_running:
                remaining_entries.append(dict(entry))
                running_count += 1
                entry_result["action"] = "active_run_still_running_missing_run_packet_path"
            else:
                stale_count += 1
                entry_result["action"] = "drop_stale_active_reference_missing_run_packet_path"
            result["reconciled_active_runs"].append(entry_result)
            continue
        try:
            run_path = _safe_rel_path(root, run_rel)
        except ValueError:
            if active_running:
                remaining_entries.append(dict(entry))
                running_count += 1
                entry_result["action"] = "active_run_still_running_run_packet_path_not_repo_relative"
            else:
                stale_count += 1
                entry_result["action"] = "drop_stale_active_reference_run_packet_path_not_repo_relative"
            result["reconciled_active_runs"].append(entry_result)
            continue
        run = _read_json(run_path)
        if not isinstance(run, dict):
            if active_running:
                remaining_entries.append(dict(entry))
                running_count += 1
                entry_result["action"] = "active_run_still_running_run_packet_missing_or_invalid"
            else:
                stale_count += 1
                entry_result["action"] = "drop_stale_active_reference_run_packet_missing_or_invalid"
            result["reconciled_active_runs"].append(entry_result)
            continue

        run_rel_normalized = _connector_rel(run_path, root)
        latest_touched_run = run_rel_normalized
        previous_status = str(run.get("status") or "")
        entry_result["run_packet_path"] = run_rel_normalized
        entry_result["previous_run_status"] = previous_status
        entry_result["output_presence"] = _run_output_presence(root, run)

        if previous_status in TERMINAL_RUN_STATUSES:
            request_terminal = _terminal_request_result_for_run(root, run, str(entry.get("request_path") or ""))
            if (
                request_terminal
                and previous_status in TERMINAL_FAILED_STATUSES
                and str(request_terminal.get("status") or "") != previous_status
            ):
                terminal_count += 1
                entry_result["action"] = "repair_terminal_run_from_request_status_and_clear_active"
                if write:
                    entry_result["request_terminal_adoption"] = _adopt_terminal_request_result_for_run(
                        root,
                        run_path,
                        run,
                        request_terminal,
                        reason="terminal_request_status_supersedes_failed_run_status",
                        output_presence=entry_result["output_presence"],
                    )
                result["reconciled_active_runs"].append(entry_result)
                continue
            terminal_count += 1
            entry_result["action"] = "clear_terminal_active_reference"
            snapshot_rel = _worker_trace_snapshot_rel(run)
            if snapshot_rel:
                entry_result["worker_trace_snapshot_path"] = snapshot_rel
            if write:
                lease_release = _release_codex_queue_run_lease(
                    root,
                    run,
                    reason=f"reconcile_terminal_active_{previous_status.lower()}",
                )
                if lease_release:
                    entry_result["worker_shift_lease_release"] = lease_release
                    _write_run_packet(run_path, run)
            if previous_status == "RETURN_RECORDED_PROOF_BLOCKED" and not run.get("failure_classification"):
                entry_result["action"] = "classify_proof_blocked_terminal_run_and_clear_active"
                if write:
                    run["failure_classification"] = "BACKEND_CODEX_FAILURE"
                    _write_run_packet(run_path, run)
                    request_rel = str(run.get("request_path") or entry.get("request_path") or "")
                    if request_rel:
                        _update_request_status(
                            root,
                            request_rel,
                            status="RETURN_RECORDED_PROOF_BLOCKED",
                            failure_classification="BACKEND_CODEX_FAILURE",
                        )
            elif write and snapshot_rel:
                if not run.get("worker_trace_snapshot_path"):
                    run["worker_trace_snapshot_path"] = snapshot_rel
                    _write_run_packet(run_path, run)
                else:
                    _write_worker_trace_snapshot(root, run)
            result["reconciled_active_runs"].append(entry_result)
            continue

        if active_running:
            remaining_entries.append(dict(entry))
            running_count += 1
            entry_result["action"] = "active_run_still_running"
            result["reconciled_active_runs"].append(entry_result)
            continue

        request_terminal = _terminal_request_result_for_run(root, run, str(entry.get("request_path") or ""))
        if request_terminal:
            terminal_count += 1
            entry_result["action"] = "adopt_terminal_request_status_and_clear_active"
            if write:
                entry_result["request_terminal_adoption"] = _adopt_terminal_request_result_for_run(
                    root,
                    run_path,
                    run,
                    request_terminal,
                    reason="active_reference_stale_but_request_already_terminal",
                    output_presence=entry_result["output_presence"],
                )
            result["reconciled_active_runs"].append(entry_result)
            continue

        stale_count += 1
        if previous_status in ACTIVE_RUN_STATUSES:
            no_terminal_output = not _run_has_terminal_output(root, run)
            entry_result["action"] = (
                "mark_codex_cli_vanished_no_output_and_clear_active"
                if no_terminal_output
                else "mark_daemon_failure_and_clear_active"
            )
            if write:
                failure_status = CODEX_CLI_VANISHED_NO_OUTPUT_STATUS if no_terminal_output else "DAEMON_WORKER_EXITED_WITHOUT_FINALIZATION"
                request_rel = str(run.get("request_path") or entry.get("request_path") or "")
                classification_basis: dict[str, Any] = {}
                if no_terminal_output:
                    failure_classification, classification_basis = (
                        _vanished_no_output_failure_classification(root, run, request_rel)
                    )
                else:
                    failure_classification = "DAEMON_FAILURE"
                reason = (
                    "active_pid_not_running_no_terminal_output"
                    if no_terminal_output
                    else "active_pid_not_running_before_worker_finalized"
                )
                run["status"] = failure_status
                run["completed_at"] = now
                run["failure_classification"] = failure_classification
                run["daemon_reconciliation"] = {
                    "reconciled_at": now,
                    "reason": reason,
                    "previous_status": previous_status,
                    "pid": active_pid,
                    "output_presence": entry_result["output_presence"],
                }
                if classification_basis:
                    run["daemon_reconciliation"]["failure_classification_basis"] = classification_basis
                _append_worker_lifecycle_event(
                    run,
                    "worker_terminal",
                    terminal_state="vanished_no_output" if no_terminal_output else "daemon_exit",
                    failure_classification=failure_classification,
                )
                _write_run_packet(run_path, run)
                if request_rel:
                    _update_request_status(
                        root,
                        request_rel,
                        status="CODEX_QUEUE_RUNNER_FAILED",
                        failure_classification=failure_classification,
                    )
        elif previous_status not in TERMINAL_RUN_STATUSES:
            entry_result["action"] = "mark_unknown_stale_run_failed_and_clear_active"
            if write:
                run["status"] = "DAEMON_WORKER_EXITED_WITHOUT_FINALIZATION"
                run["completed_at"] = now
                run["failure_classification"] = "DAEMON_FAILURE"
                run["daemon_reconciliation"] = {
                    "reconciled_at": now,
                    "reason": "active_pid_not_running_with_unknown_run_status",
                    "previous_status": previous_status,
                    "pid": active_pid,
                    "output_presence": entry_result["output_presence"],
                }
                _write_run_packet(run_path, run)
                request_rel = str(run.get("request_path") or entry.get("request_path") or "")
                if request_rel:
                    _update_request_status(
                        root,
                        request_rel,
                        status="CODEX_QUEUE_RUNNER_FAILED",
                        failure_classification="DAEMON_FAILURE",
                    )
        result["reconciled_active_runs"].append(entry_result)

    result["stale_active_run_detected"] = stale_count > 0
    result["terminal_active_run_detected"] = terminal_count > 0
    result["active_process_running"] = bool(remaining_entries)
    result["active_run_count_after"] = len(remaining_entries)
    result["active_lane_locks"] = _lane_lock_index(remaining_entries)
    result["concurrency"] = _concurrency_summary(remaining_entries)
    if remaining_entries and not stale_count and not terminal_count:
        result["action"] = "active_runs_still_running"
    elif remaining_entries:
        result["action"] = "reconciled_multi_lane_active_runs_remaining"
    elif stale_count or terminal_count:
        result["action"] = "reconciled_multi_lane_active_runs_cleared"
    else:
        result["action"] = "no_active_run"
    if write:
        _update_runner_state(root, _state_for_active_entries(remaining_entries, latest_run=latest_touched_run))
    return True


def reconcile_codex_queue_runner_state(root: str | Path | None = None, *, write: bool = False) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    state_path = shell_root / RUNNER_STATE_PATH
    state = _read_json(state_path) or {}
    active = state.get("active_run") if isinstance(state.get("active_run"), dict) else None
    now = _now()
    result: dict[str, Any] = {
        "schema_id": "ion.codex_queue_runner_reconciliation.v1",
        "ok": True,
        "write": bool(write),
        "runner_state_path": RUNNER_STATE_PATH.as_posix(),
        "stale_active_run_detected": False,
        "active_process_running": False,
        "action": "no_active_run",
        "production_authority": False,
        "live_execution_authority": False,
    }

    latest_run_rel = str(state.get("latest_run") or "").strip() or (_latest_run_packet_rel(shell_root) or "")
    if _reconcile_multi_active_runs(shell_root, state, latest_run_rel=latest_run_rel, write=write, result=result):
        return result
    if not active:
        if latest_run_rel:
            if _classify_start_no_receipt_if_needed(shell_root, latest_run_rel, write=write, result=result):
                return result
            if _classify_vanished_latest_run_if_needed(shell_root, latest_run_rel, write=write, result=result):
                return result
            _classify_terminal_run_if_needed(shell_root, latest_run_rel, write=write, result=result)
        if write:
            _update_runner_state(shell_root, _state_for_active_entries([], latest_run=latest_run_rel or None))
        return result

    active_pid = int(active.get("pid")) if active.get("pid") else None
    active_running = _pid_running(active_pid)
    result["active_process_running"] = active_running
    result["active_run"] = active

    run_rel = str(active.get("run_packet_path") or "")
    if not run_rel:
        if active_running:
            result["action"] = "active_run_still_running"
            result["finding"] = "active_run_missing_run_packet_path"
            return result
        result["stale_active_run_detected"] = True
        result["action"] = "clear_stale_active_reference"
        result["finding"] = "active_run_missing_run_packet_path"
        if write:
            _update_runner_state(shell_root, {
                "active_run": None,
                "latest_run": latest_run_rel or None,
                "manual_proceed_relay_required": False,
            })
        return result

    try:
        run_path = _safe_rel_path(shell_root, run_rel)
    except ValueError:
        if active_running:
            result["action"] = "active_run_still_running"
            result["finding"] = "active_run_run_packet_path_not_repo_relative"
            return result
        result["stale_active_run_detected"] = True
        result["action"] = "clear_stale_active_reference"
        result["finding"] = "active_run_run_packet_path_not_repo_relative"
        if write:
            _update_runner_state(shell_root, {
                "active_run": None,
                "latest_run": latest_run_rel or run_rel,
                "manual_proceed_relay_required": False,
            })
        return result

    run = _read_json(run_path)
    if not isinstance(run, dict):
        if active_running:
            result["action"] = "active_run_still_running"
            result["finding"] = "active_run_run_packet_missing_or_invalid"
            return result
        result["stale_active_run_detected"] = True
        result["action"] = "clear_stale_active_reference"
        result["finding"] = "active_run_run_packet_missing_or_invalid"
        if write:
            _update_runner_state(shell_root, {
                "active_run": None,
                "latest_run": latest_run_rel or run_rel,
                "manual_proceed_relay_required": False,
            })
        return result

    previous_status = str(run.get("status") or "")
    result["run_packet_path"] = _connector_rel(run_path, shell_root)
    result["previous_run_status"] = previous_status
    result["output_presence"] = _run_output_presence(shell_root, run)

    if previous_status in TERMINAL_RUN_STATUSES:
        request_terminal = _terminal_request_result_for_run(shell_root, run, str(active.get("request_path") or ""))
        if (
            request_terminal
            and previous_status in TERMINAL_FAILED_STATUSES
            and str(request_terminal.get("status") or "") != previous_status
        ):
            result["terminal_active_run_detected"] = True
            result["action"] = "repair_terminal_run_from_request_status_and_clear_active"
            if write:
                result["request_terminal_adoption"] = _adopt_terminal_request_result_for_run(
                    shell_root,
                    run_path,
                    run,
                    request_terminal,
                    reason="terminal_request_status_supersedes_failed_run_status",
                    output_presence=result["output_presence"],
                )
                _update_runner_state(shell_root, {
                    "active_run": None,
                    "latest_run": _connector_rel(run_path, shell_root),
                    "manual_proceed_relay_required": False,
                })
            return result
        result["terminal_active_run_detected"] = True
        result["action"] = "clear_terminal_active_reference"
        snapshot_rel = _worker_trace_snapshot_rel(run)
        if snapshot_rel:
            result["worker_trace_snapshot_path"] = snapshot_rel
        if write:
            lease_release = _release_codex_queue_run_lease(
                shell_root,
                run,
                reason=f"reconcile_terminal_active_{previous_status.lower()}",
            )
            if lease_release:
                result["worker_shift_lease_release"] = lease_release
                _write_run_packet(run_path, run)
        if previous_status == "RETURN_RECORDED_PROOF_BLOCKED" and not run.get("failure_classification"):
            result["action"] = "classify_proof_blocked_terminal_run_and_clear_active"
            if write:
                run["failure_classification"] = "BACKEND_CODEX_FAILURE"
                _write_run_packet(run_path, run)
                request_rel = str(run.get("request_path") or active.get("request_path") or "")
                if request_rel:
                    _update_request_status(
                        shell_root,
                        request_rel,
                        status="RETURN_RECORDED_PROOF_BLOCKED",
                        failure_classification="BACKEND_CODEX_FAILURE",
                    )
        elif write and snapshot_rel:
            if not run.get("worker_trace_snapshot_path"):
                run["worker_trace_snapshot_path"] = snapshot_rel
                _write_run_packet(run_path, run)
            else:
                _write_worker_trace_snapshot(shell_root, run)
        if write:
            _update_runner_state(shell_root, {
                "active_run": None,
                "latest_run": _connector_rel(run_path, shell_root),
                "manual_proceed_relay_required": False,
            })
        return result

    if active_running:
        result["action"] = "active_run_still_running"
        return result

    request_terminal = _terminal_request_result_for_run(shell_root, run, str(active.get("request_path") or ""))
    if request_terminal:
        result["terminal_active_run_detected"] = True
        result["action"] = "adopt_terminal_request_status_and_clear_active"
        if write:
            result["request_terminal_adoption"] = _adopt_terminal_request_result_for_run(
                shell_root,
                run_path,
                run,
                request_terminal,
                reason="active_reference_stale_but_request_already_terminal",
                output_presence=result["output_presence"],
            )
            _update_runner_state(shell_root, {
                "active_run": None,
                "latest_run": _connector_rel(run_path, shell_root),
                "manual_proceed_relay_required": False,
            })
        return result

    result["stale_active_run_detected"] = True
    result["action"] = "clear_stale_active_reference"

    if previous_status in ACTIVE_RUN_STATUSES:
        no_terminal_output = not _run_has_terminal_output(shell_root, run)
        result["action"] = (
            "mark_codex_cli_vanished_no_output_and_clear_active"
            if no_terminal_output
            else "mark_daemon_failure_and_clear_active"
        )
        if write:
            failure_status = CODEX_CLI_VANISHED_NO_OUTPUT_STATUS if no_terminal_output else "DAEMON_WORKER_EXITED_WITHOUT_FINALIZATION"
            request_rel = str(run.get("request_path") or active.get("request_path") or "")
            classification_basis: dict[str, Any] = {}
            if no_terminal_output:
                failure_classification, classification_basis = (
                    _vanished_no_output_failure_classification(shell_root, run, request_rel)
                )
            else:
                failure_classification = "DAEMON_FAILURE"
            reason = (
                "active_pid_not_running_no_terminal_output"
                if no_terminal_output
                else "active_pid_not_running_before_worker_finalized"
            )
            run["status"] = failure_status
            run["completed_at"] = now
            run["failure_classification"] = failure_classification
            run["daemon_reconciliation"] = {
                "reconciled_at": now,
                "reason": reason,
                "previous_status": previous_status,
                "pid": active_pid,
                "output_presence": result["output_presence"],
            }
            if classification_basis:
                run["daemon_reconciliation"]["failure_classification_basis"] = classification_basis
            _append_worker_lifecycle_event(
                run,
                "worker_terminal",
                terminal_state="vanished_no_output" if no_terminal_output else "daemon_exit",
                failure_classification=failure_classification,
            )
            _write_run_packet(run_path, run)
            if request_rel:
                _update_request_status(
                    shell_root,
                    request_rel,
                    status="CODEX_QUEUE_RUNNER_FAILED",
                    failure_classification=failure_classification,
                )
    elif previous_status == "RETURN_RECORDED_PROOF_BLOCKED" and not run.get("failure_classification"):
        result["action"] = "classify_proof_blocked_terminal_run_and_clear_active"
        if write:
            run["failure_classification"] = "BACKEND_CODEX_FAILURE"
            _write_run_packet(run_path, run)
            request_rel = str(run.get("request_path") or active.get("request_path") or "")
            if request_rel:
                _update_request_status(
                    shell_root,
                    request_rel,
                    status="RETURN_RECORDED_PROOF_BLOCKED",
                    failure_classification="BACKEND_CODEX_FAILURE",
                )
    elif previous_status not in TERMINAL_RUN_STATUSES:
        result["action"] = "mark_unknown_stale_run_failed_and_clear_active"
        if write:
            run["status"] = "DAEMON_WORKER_EXITED_WITHOUT_FINALIZATION"
            run["completed_at"] = now
            run["failure_classification"] = "DAEMON_FAILURE"
            run["daemon_reconciliation"] = {
                "reconciled_at": now,
                "reason": "active_pid_not_running_with_unknown_run_status",
                "previous_status": previous_status,
                "pid": active_pid,
                "output_presence": result["output_presence"],
            }
            _write_run_packet(run_path, run)
            request_rel = str(run.get("request_path") or active.get("request_path") or "")
            if request_rel:
                _update_request_status(
                    shell_root,
                    request_rel,
                    status="CODEX_QUEUE_RUNNER_FAILED",
                    failure_classification="DAEMON_FAILURE",
                )

    if write:
        _update_runner_state(shell_root, {
            "active_run": None,
            "latest_run": _connector_rel(run_path, shell_root),
            "manual_proceed_relay_required": False,
        })
    return result


def _classify_start_no_receipt_if_needed(
    root: Path,
    run_rel: str,
    *,
    write: bool,
    result: dict[str, Any],
) -> bool:
    try:
        run_path = _safe_rel_path(root, run_rel)
    except ValueError:
        result["latest_run_finding"] = "latest_run_path_not_repo_relative"
        return False
    run = _read_json(run_path)
    if not isinstance(run, dict):
        result["latest_run_finding"] = "latest_run_packet_missing_or_invalid"
        return False
    previous_status = str(run.get("status") or "")
    if previous_status not in START_REQUESTED_RUN_STATUSES:
        return False

    run_pid = int(run.get("pid")) if run.get("pid") else None
    if _pid_running(run_pid):
        result["action"] = "start_requested_worker_running_without_active_state"
        result["latest_run_packet_path"] = _connector_rel(run_path, root)
        result["latest_run_status"] = previous_status
        result["active_process_running"] = True
        return True

    now_dt = datetime.now(timezone.utc)
    age = _run_start_request_age_seconds(run, now_dt)
    result["latest_run_packet_path"] = _connector_rel(run_path, root)
    result["latest_run_status"] = previous_status
    result["start_request_age_seconds"] = age
    result["start_no_receipt_grace_seconds"] = START_NO_RECEIPT_GRACE_SECONDS

    if age is None or age < START_NO_RECEIPT_GRACE_SECONDS:
        result["action"] = "start_requested_waiting_for_receipt"
        return True

    result["stale_active_run_detected"] = True
    result["action"] = "mark_start_no_receipt"
    if not write:
        return True

    now = _now()
    output_presence = _run_output_presence(root, run)
    run["status"] = START_NO_RECEIPT_STATUS
    run["completed_at"] = now
    run["updated_at"] = now
    run["failure_classification"] = "CARRIER_ADAPTER_FAILURE"
    run["start_no_receipt_diagnostic"] = {
        "detected_at": now,
        "reason": "start_requested_but_no_worker_receipt_or_active_process_after_grace",
        "previous_status": previous_status,
        "age_seconds": age,
        "grace_seconds": START_NO_RECEIPT_GRACE_SECONDS,
        "pid": run_pid,
        "output_presence": output_presence,
    }
    _append_worker_lifecycle_event(
        run,
        "start_no_receipt",
        terminal_state="start_no_receipt",
        failure_classification="CARRIER_ADAPTER_FAILURE",
    )
    _write_run_packet(run_path, run)
    request_rel = str(run.get("request_path") or "")
    if request_rel:
        _update_request_status(
            root,
            request_rel,
            status=START_NO_RECEIPT_STATUS,
            failure_classification="CARRIER_ADAPTER_FAILURE",
        )
    _update_runner_state(root, {
        "active_run": None,
        "latest_run": _connector_rel(run_path, root),
        "manual_proceed_relay_required": False,
    })
    result["start_no_receipt_updated"] = True
    result["output_presence"] = output_presence
    return True


def _classify_vanished_latest_run_if_needed(
    root: Path,
    run_rel: str,
    *,
    write: bool,
    result: dict[str, Any],
) -> bool:
    try:
        run_path = _safe_rel_path(root, run_rel)
    except ValueError:
        result["latest_run_finding"] = "latest_run_path_not_repo_relative"
        return False
    run = _read_json(run_path)
    if not isinstance(run, dict):
        result["latest_run_finding"] = "latest_run_packet_missing_or_invalid"
        return False
    previous_status = str(run.get("status") or "")
    if previous_status not in ACTIVE_RUN_STATUSES:
        return False
    if previous_status in START_REQUESTED_RUN_STATUSES:
        return False

    run_pid = int(run.get("pid")) if run.get("pid") else None
    if _pid_running(run_pid):
        result["action"] = "latest_active_run_process_running_without_active_state"
        result["latest_run_packet_path"] = _connector_rel(run_path, root)
        result["latest_run_status"] = previous_status
        result["active_process_running"] = True
        return True

    output_presence = _run_output_presence(root, run)
    request_terminal = _terminal_request_result_for_run(root, run)
    if request_terminal:
        result["terminal_active_run_detected"] = True
        result["latest_run_packet_path"] = _connector_rel(run_path, root)
        result["latest_run_status"] = previous_status
        result["output_presence"] = output_presence
        result["action"] = "adopt_latest_terminal_request_status"
        if write:
            result["request_terminal_adoption"] = _adopt_terminal_request_result_for_run(
                root,
                run_path,
                run,
                request_terminal,
                reason="latest_active_run_without_active_state_but_request_already_terminal",
                output_presence=output_presence,
            )
            _update_runner_state(root, {
                "active_run": None,
                "latest_run": _connector_rel(run_path, root),
                "manual_proceed_relay_required": False,
            })
        return True

    no_terminal_output = not _run_has_terminal_output(root, run)
    result["stale_active_run_detected"] = True
    result["latest_run_packet_path"] = _connector_rel(run_path, root)
    result["latest_run_status"] = previous_status
    result["output_presence"] = output_presence
    result["action"] = (
        "mark_codex_cli_vanished_no_output"
        if no_terminal_output
        else "mark_latest_active_run_daemon_failure"
    )
    if not write:
        return True

    now = _now()
    failure_status = CODEX_CLI_VANISHED_NO_OUTPUT_STATUS if no_terminal_output else "DAEMON_WORKER_EXITED_WITHOUT_FINALIZATION"
    request_rel = str(run.get("request_path") or "")
    classification_basis: dict[str, Any] = {}
    if no_terminal_output:
        failure_classification, classification_basis = (
            _vanished_no_output_failure_classification(root, run, request_rel)
        )
    else:
        failure_classification = "DAEMON_FAILURE"
    reason = (
        "latest_run_pid_not_running_no_terminal_output"
        if no_terminal_output
        else "latest_run_pid_not_running_before_worker_finalized"
    )
    run["status"] = failure_status
    run["completed_at"] = now
    run["updated_at"] = now
    run["failure_classification"] = failure_classification
    run["daemon_reconciliation"] = {
        "reconciled_at": now,
        "reason": reason,
        "previous_status": previous_status,
        "pid": run_pid,
        "output_presence": output_presence,
    }
    if classification_basis:
        run["daemon_reconciliation"]["failure_classification_basis"] = classification_basis
    _append_worker_lifecycle_event(
        run,
        "worker_terminal",
        terminal_state="vanished_no_output" if no_terminal_output else "daemon_exit",
        failure_classification=failure_classification,
    )
    _write_run_packet(run_path, run)
    if request_rel:
        _update_request_status(
            root,
            request_rel,
            status="CODEX_QUEUE_RUNNER_FAILED",
            failure_classification=failure_classification,
        )
    _update_runner_state(root, {
        "active_run": None,
        "latest_run": _connector_rel(run_path, root),
        "manual_proceed_relay_required": False,
    })
    result["latest_run_failure_classification_updated"] = True
    return True


def _classify_terminal_run_if_needed(
    root: Path,
    run_rel: str,
    *,
    write: bool,
    result: dict[str, Any],
) -> None:
    try:
        run_path = _safe_rel_path(root, run_rel)
    except ValueError:
        result["latest_run_finding"] = "latest_run_path_not_repo_relative"
        return
    run = _read_json(run_path)
    if not isinstance(run, dict):
        result["latest_run_finding"] = "latest_run_packet_missing_or_invalid"
        return
    run_status = str(run.get("status") or "")
    if run_status not in TERMINAL_RUN_STATUSES:
        return
    result["latest_run_packet_path"] = _connector_rel(run_path, root)
    changed = False
    request_terminal = _terminal_request_result_for_run(root, run)
    if (
        request_terminal
        and run_status in TERMINAL_FAILED_STATUSES
        and str(request_terminal.get("status") or "") != run_status
    ):
        result["latest_run_terminal_request_status_mismatch"] = True
        if write:
            result["request_terminal_adoption"] = _adopt_terminal_request_result_for_run(
                root,
                run_path,
                run,
                request_terminal,
                reason="terminal_request_status_supersedes_failed_latest_run_status",
                output_presence=_run_output_presence(root, run),
            )
        return
    if run_status == "RETURN_RECORDED_PROOF_BLOCKED" and not run.get("failure_classification"):
        result["latest_run_failure_classification_missing"] = True
        if write:
            run["failure_classification"] = "BACKEND_CODEX_FAILURE"
            request_rel = str(run.get("request_path") or "")
            if request_rel:
                _update_request_status(
                    root,
                    request_rel,
                    status="RETURN_RECORDED_PROOF_BLOCKED",
                    failure_classification="BACKEND_CODEX_FAILURE",
                )
            result["latest_run_failure_classification_updated"] = True
            changed = True
    snapshot_rel = _worker_trace_snapshot_rel(run)
    if snapshot_rel:
        result["worker_trace_snapshot_path"] = snapshot_rel
    if not write:
        return
    lease_release = _release_codex_queue_run_lease(
        root,
        run,
        reason=f"classify_terminal_latest_{run_status.lower()}",
    )
    if lease_release:
        result["worker_shift_lease_release"] = lease_release
        changed = True
    if snapshot_rel and not run.get("worker_trace_snapshot_path"):
        run["worker_trace_snapshot_path"] = snapshot_rel
        changed = True
    if changed:
        _write_run_packet(run_path, run)
    elif snapshot_rel:
        _write_worker_trace_snapshot(root, run)
        result["worker_trace_snapshot_written"] = True


def run_codex_queue_worker(
    root: str | Path | None,
    run_packet_path: str | Path,
    *,
    task_output_override: str | None = None,
) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    run_path = Path(run_packet_path)
    if not run_path.is_absolute():
        run_path = shell_root / run_path
    run = _read_json(run_path)
    if not isinstance(run, dict):
        raise ValueError(f"invalid run packet: {run_packet_path}")
    awareness_receipt_rel, awareness_receipt_sha, awareness_receipt = _write_worker_context_awareness_receipt(
        shell_root,
        str(run.get("run_packet_path") or _connector_rel(run_path, shell_root)),
        run,
        worker_pid_or_process_ref=os.getpid(),
        started_at=_now(),
    )
    sign_in_status = str(awareness_receipt.get("status") or WORKER_CONTEXT_BLOCKED)
    if sign_in_status != WORKER_CONTEXT_ACKNOWLEDGED:
        run["status"] = "WORKER_CONTEXT_MOUNT_INVALID"
        run["pid"] = os.getpid()
        run["completed_at"] = _now()
        run["failure_classification"] = "CARRIER_ADAPTER_FAILURE"
        lease_release = _release_codex_queue_run_lease(shell_root, run, reason="worker_context_mount_invalid")
        _append_worker_lifecycle_event(
            run,
            "worker_terminal",
            terminal_state="context_mount_invalid",
            worker_sign_in_status=sign_in_status,
            worker_context_awareness_receipt_path=awareness_receipt_rel,
            worker_context_awareness_receipt_sha256=awareness_receipt_sha,
            worker_shift_lease_release_receipt_path=(lease_release or {}).get("receipt_path"),
            worker_shift_lease_release_result=(lease_release or {}).get("release_result"),
            failure_classification="CARRIER_ADAPTER_FAILURE",
        )
        run["worker_return_status"] = _worker_return_status_for_run(run)
        _write_run_packet(run_path, run)
        _update_request_status(
            shell_root,
            str(run["request_path"]),
            status="CODEX_QUEUE_RUNNER_FAILED",
            failure_classification="CARRIER_ADAPTER_FAILURE",
        )
        remaining_entries = _current_running_entries_without(shell_root, _active_entry_for_run(run, pid=os.getpid()))
        _update_runner_state(
            shell_root,
            _state_for_active_entries(
                remaining_entries,
                latest_run=run["run_packet_path"],
                latest_worker_lifecycle_event=run["worker_lifecycle_events"][-1],
            ),
        )
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "result": "WORKER_CONTEXT_MOUNT_INVALID",
            "run": run,
            "active_root_proof": run.get("active_root_proof"),
            "worker_identity": run.get("worker_identity"),
            "domain_alignment": run.get("domain_alignment"),
            "worker_return_status": run.get("worker_return_status"),
            "production_authority": False,
            "live_execution_authority": False,
        }
    run["status"] = "CODEX_CLI_RUNNING"
    run["pid"] = os.getpid()
    run["started_at"] = _now()
    _append_worker_lifecycle_event(
        run,
        "worker_boot",
        worker_pid=os.getpid(),
        worker_sign_in_status=sign_in_status,
        worker_context_awareness_receipt_path=awareness_receipt_rel,
        worker_context_awareness_receipt_sha256=awareness_receipt_sha,
    )
    _write_run_packet(run_path, run)
    active_entry = _active_entry_for_run(run, pid=os.getpid(), started_at=run["started_at"])
    active_entries = _current_running_entries_with(shell_root, active_entry)
    _update_runner_state(shell_root, _state_for_active_entries(active_entries, latest_run=run["run_packet_path"]))
    request_rel = str(run["request_path"])
    task_output = task_output_override
    returncode: int | None = None
    timed_out = False
    if task_output is None:
        command = list(run["codex_command"])
        prompt = (shell_root / str(run["prompt_path"])).read_text(encoding="utf-8")
        launch_profile = (
            run.get("codex_cli_launch_profile")
            if isinstance(run.get("codex_cli_launch_profile"), Mapping)
            else {}
        )
        codex_project_cwd = Path(
            str(
                run.get("codex_project_cwd")
                or launch_profile.get("subprocess_cwd")
                or run.get("worker_launch_cwd")
                or shell_root
            )
        ).expanduser().resolve(strict=False)
        stdout_attempts: list[str] = []
        stderr_attempts: list[str] = []
        for attempt_index in range(MAX_CODEX_TRANSIENT_USAGE_LIMIT_RETRIES + 1):
            try:
                completed = subprocess.run(
                    command,
                    cwd=codex_project_cwd,
                    input=prompt,
                    text=True,
                    capture_output=True,
                    timeout=int(run.get("timeout_seconds") or DEFAULT_CODEX_TIMEOUT_SECONDS),
                    check=False,
                )
                returncode = completed.returncode
                stdout_text = str(completed.stdout or "")
                stderr_text = str(completed.stderr or "")
                stdout_attempts.append(stdout_text)
                stderr_attempts.append(stderr_text)
                transient_usage_limit = (
                    returncode not in {0, None}
                    and _looks_like_codex_transient_usage_limit_bug(stdout_text, stderr_text)
                )
                if transient_usage_limit:
                    prompt_through_receipts = [
                        dict(item)
                        for item in (run.get("codex_transient_usage_limit_prompt_through") or [])
                        if isinstance(item, Mapping)
                    ]
                    prompt_through_usage_limit_recurred = False
                    while len(prompt_through_receipts) < MAX_CODEX_TRANSIENT_USAGE_LIMIT_PROMPT_THROUGH_ATTEMPTS:
                        prompt_attempt = len(prompt_through_receipts) + 1
                        prompt_through = _attempt_codex_usage_limit_prompt_through(
                            shell_root,
                            run,
                            stdout_text=stdout_text,
                            stderr_text=stderr_text,
                            attempt=prompt_attempt,
                        )
                        prompt_through_public = dict(prompt_through)
                        prompt_through_task_output = str(prompt_through_public.pop("task_output", "") or "")
                        prompt_through_receipts.append(prompt_through_public)
                        run["codex_transient_usage_limit_prompt_through"] = prompt_through_receipts
                        _append_worker_lifecycle_event(
                            run,
                            CODEX_TRANSIENT_USAGE_LIMIT_PROMPT_THROUGH_EVENT,
                            prompt_through_attempt=len(prompt_through_receipts),
                            max_prompt_through_attempts=MAX_CODEX_TRANSIENT_USAGE_LIMIT_PROMPT_THROUGH_ATTEMPTS,
                            attempted=bool(prompt_through.get("attempted")),
                            ok=bool(prompt_through.get("ok")),
                            finding=prompt_through.get("finding"),
                            session_resolution=prompt_through.get("session_resolution"),
                            route_output_usage_limit_recurred=bool(
                                prompt_through_public.get("route_output_usage_limit_recurred")
                            ),
                            route_result=prompt_through_public.get("route_result"),
                            failure_classification=CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS,
                            retry_policy="bounded_prompt_through_until_task_output_or_recurrent_usage_limit",
                        )
                        run["updated_at"] = _now()
                        _write_run_packet(run_path, run)
                        if prompt_through.get("ok") and prompt_through_task_output.strip():
                            task_output = prompt_through_task_output
                            returncode = int(
                                (
                                    prompt_through_public.get("route_result")
                                    if isinstance(prompt_through_public.get("route_result"), Mapping)
                                    else {}
                                ).get("returncode")
                                or 0
                            )
                            (shell_root / str(run["last_message_path"])).write_text(
                                task_output,
                                encoding="utf-8",
                            )
                            stdout_attempts.append(task_output)
                            stderr_attempts.append("")
                            break
                        if prompt_through_public.get("route_output_usage_limit_recurred"):
                            prompt_through_usage_limit_recurred = True
                            break
                        route_result = prompt_through_public.get("route_result")
                        if not prompt_through.get("attempted") or not isinstance(route_result, Mapping):
                            break
                        if not (
                            int(route_result.get("line_count_delta") or 0) > 0
                            or int(route_result.get("message_count_delta") or 0) > 0
                        ):
                            break
                    if task_output is not None and returncode == 0:
                        break
                    if prompt_through_usage_limit_recurred:
                        break
                if transient_usage_limit and not prompt_through_usage_limit_recurred and attempt_index < MAX_CODEX_TRANSIENT_USAGE_LIMIT_RETRIES:
                    retry_receipts = [
                        dict(item)
                        for item in (run.get("codex_transient_usage_limit_retries") or [])
                        if isinstance(item, Mapping)
                    ]
                    retry_receipt = {
                        "schema_id": "ion.codex_cli_transient_usage_limit_retry.v1",
                        "attempt": attempt_index + 1,
                        "max_attempts": MAX_CODEX_TRANSIENT_USAGE_LIMIT_RETRIES,
                        "finding": "codex_cli_reported_usage_limit_but_operator_identified_transient_bug",
                        "retry_policy": "single_bounded_retry_preserve_proof_no_quota_claim",
                        "stderr_excerpt": _bounded_usage_limit_excerpt(stdout_text, stderr_text),
                        "production_authority": False,
                        "live_execution_authority": False,
                        "accepted_state_claim": False,
                    }
                    retry_receipts.append(retry_receipt)
                    run["codex_transient_usage_limit_retries"] = retry_receipts
                    _append_worker_lifecycle_event(
                        run,
                        CODEX_TRANSIENT_USAGE_LIMIT_RETRY_EVENT,
                        retry_attempt=attempt_index + 1,
                        max_retry_attempts=MAX_CODEX_TRANSIENT_USAGE_LIMIT_RETRIES,
                        failure_classification=CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS,
                        retry_policy="single_bounded_retry_preserve_proof_no_quota_claim",
                    )
                    run["updated_at"] = _now()
                    _write_run_packet(run_path, run)
                    continue
                break
            except subprocess.TimeoutExpired as exc:
                timed_out = True
                returncode = None
                stdout_attempts.append(str(exc.stdout or ""))
                stderr_attempts.append(str(exc.stderr or "codex command timed out"))
                break
        stdout_log = stdout_attempts[-1] if returncode == 0 and stdout_attempts else _combined_codex_attempt_output(stdout_attempts, label="stdout")
        (shell_root / str(run["stdout_path"])).write_text(
            stdout_log,
            encoding="utf-8",
            errors="replace",
        )
        (shell_root / str(run["stderr_path"])).write_text(
            _combined_codex_attempt_output(stderr_attempts, label="stderr"),
            encoding="utf-8",
            errors="replace",
        )
        last_message = shell_root / str(run["last_message_path"])
        if last_message.exists():
            task_output = last_message.read_text(encoding="utf-8", errors="replace")
        else:
            task_output = (shell_root / str(run["stdout_path"])).read_text(encoding="utf-8", errors="replace")
    else:
        (shell_root / str(run["last_message_path"])).write_text(task_output, encoding="utf-8")
        (shell_root / str(run["stdout_path"])).write_text("", encoding="utf-8")
        (shell_root / str(run["stderr_path"])).write_text("", encoding="utf-8")
        returncode = 0

    if timed_out:
        run["status"] = "CODEX_CLI_TIMEOUT"
        run["failure_classification"] = "CODEX_CLI_FAILURE"
        lease_release = _release_codex_queue_run_lease(shell_root, run, reason="codex_cli_timeout")
        _append_worker_lifecycle_event(
            run,
            "worker_terminal",
            terminal_state="timeout",
            worker_shift_lease_release_receipt_path=(lease_release or {}).get("receipt_path"),
            worker_shift_lease_release_result=(lease_release or {}).get("release_result"),
            failure_classification="CODEX_CLI_FAILURE",
        )
        run["worker_return_status"] = _worker_return_status_for_run(run)
        _write_run_packet(run_path, run)
        _update_request_status(shell_root, request_rel, status="CODEX_QUEUE_RUNNER_FAILED", failure_classification="CODEX_CLI_FAILURE")
        remaining_entries = _current_running_entries_without(shell_root, _active_entry_for_run(run, pid=os.getpid()))
        _update_runner_state(
            shell_root,
            _state_for_active_entries(
                remaining_entries,
                latest_run=_connector_rel(run_path, shell_root),
                latest_worker_lifecycle_event=run["worker_lifecycle_events"][-1],
            ),
        )
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "result": "CODEX_CLI_TIMEOUT",
            "run": run,
            "active_root_proof": run.get("active_root_proof"),
            "worker_identity": run.get("worker_identity"),
            "domain_alignment": run.get("domain_alignment"),
            "worker_return_status": run.get("worker_return_status"),
        }
    if returncode not in {0, None}:
        stdout_text = (shell_root / str(run["stdout_path"])).read_text(encoding="utf-8", errors="replace")
        stderr_text = (shell_root / str(run["stderr_path"])).read_text(encoding="utf-8", errors="replace")
        transient_usage_limit_bug = _looks_like_codex_transient_usage_limit_bug(str(task_output or ""), stdout_text, stderr_text)
        status = CODEX_TRANSIENT_USAGE_LIMIT_BUG_STATUS if transient_usage_limit_bug else "CODEX_CLI_EXIT_NONZERO"
        failure_classification = CODEX_TRANSIENT_USAGE_LIMIT_BUG_CLASS if transient_usage_limit_bug else "CODEX_CLI_FAILURE"
        terminal_state = "transient_usage_limit_bug_retry_exhausted" if transient_usage_limit_bug else "exit_nonzero"
        run["status"] = status
        run["returncode"] = returncode
        run["failure_classification"] = failure_classification
        if transient_usage_limit_bug:
            run["codex_transient_usage_limit_bug"] = {
                "schema_id": "ion.codex_cli_transient_usage_limit_bug.v1",
                "finding": "codex_cli_reported_usage_limit_after_bounded_retry",
                "operator_reported_actual_usage_exhausted": False,
                "retry_count": len(run.get("codex_transient_usage_limit_retries") or []),
                "stderr_excerpt": _bounded_usage_limit_excerpt(str(task_output or ""), stdout_text, stderr_text),
                "claim_boundary": "This is a carrier-session transient classification, not authoritative quota state.",
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_claim": False,
            }
            run["carrier_session_recovery"] = _transient_usage_limit_recovery_projection(
                shell_root,
                run,
                request_rel=request_rel,
            )
        lease_release = _release_codex_queue_run_lease(
            shell_root,
            run,
            reason="codex_transient_usage_limit_bug_retry_exhausted" if transient_usage_limit_bug else "codex_cli_exit_nonzero",
        )
        _append_worker_lifecycle_event(
            run,
            "worker_terminal",
            terminal_state=terminal_state,
            returncode=returncode,
            worker_shift_lease_release_receipt_path=(lease_release or {}).get("receipt_path"),
            worker_shift_lease_release_result=(lease_release or {}).get("release_result"),
            failure_classification=failure_classification,
        )
        run["worker_return_status"] = _worker_return_status_for_run(run)
        _write_run_packet(run_path, run)
        _update_request_status(
            shell_root,
            request_rel,
            status="CODEX_QUEUE_RUNNER_FAILED",
            failure_classification=failure_classification,
            carrier_session_recovery=run.get("carrier_session_recovery")
            if isinstance(run.get("carrier_session_recovery"), Mapping)
            else None,
        )
        remaining_entries = _current_running_entries_without(shell_root, _active_entry_for_run(run, pid=os.getpid()))
        _update_runner_state(
            shell_root,
            _state_for_active_entries(
                remaining_entries,
                latest_run=_connector_rel(run_path, shell_root),
                latest_worker_lifecycle_event=run["worker_lifecycle_events"][-1],
            ),
        )
        return {
            "schema_id": SCHEMA_ID,
            "ok": False,
            "result": status,
            "run": run,
            "active_root_proof": run.get("active_root_proof"),
            "worker_identity": run.get("worker_identity"),
            "domain_alignment": run.get("domain_alignment"),
            "worker_return_status": run.get("worker_return_status"),
        }

    from .ion_chatgpt_browser_mcp_connector_contract import call_chatgpt_connector_tool

    context_receipt = _read_json(shell_root / str(run["context_receipt_path"])) or {}
    request = _load_request(shell_root / request_rel)
    task_output_submit, task_output_source = _select_task_output_for_submit(shell_root, run, request, task_output)
    submit = call_chatgpt_connector_tool(
        shell_root,
        "ion_submit_task_return",
        {
            "task_output_text": task_output_submit,
            "context_receipt": context_receipt,
            "work_request_id": str(request.get("request_id") or ""),
            "work_request_path": request_rel,
        },
    )
    submit_data = submit.get("data") if isinstance(submit.get("data"), Mapping) else {}
    accepted = bool(submit_data.get("accepted_for_carrier_intake"))
    template_valid = bool(submit_data.get("return_template_valid", True))
    run["status"] = "RETURN_RECORDED_PROOF_ACCEPTED" if accepted else ("RETURN_TEMPLATE_INVALID" if not template_valid else "RETURN_RECORDED_PROOF_BLOCKED")
    run["returncode"] = returncode
    run["failure_classification"] = None if accepted else "BACKEND_CODEX_FAILURE"
    run["task_output_submission_source"] = task_output_source
    run["submit_result"] = submit_data
    submit_packet_path = str(submit_data.get("packet_path") or "").strip()
    submit_machine_receipt_path = str(submit_data.get("machine_receipt_path") or "").strip()
    if submit_packet_path:
        return_packet_paths = [
            str(item)
            for item in (run.get("return_packet_paths") or [])
            if str(item).strip()
        ]
        if submit_packet_path not in return_packet_paths:
            return_packet_paths.append(submit_packet_path)
        run["return_packet_paths"] = return_packet_paths
        run["latest_return_packet_path"] = submit_packet_path
    if submit_machine_receipt_path:
        run["latest_task_return_machine_receipt_path"] = submit_machine_receipt_path
    run["completed_at"] = _now()
    lease_release = _release_codex_queue_run_lease(
        shell_root,
        run,
        reason="return_recorded_proof_accepted" if accepted else ("return_template_invalid" if not template_valid else "return_recorded_proof_blocked"),
    )
    _append_worker_lifecycle_event(
        run,
        "worker_terminal",
        terminal_state="accepted" if accepted else ("template_invalid" if not template_valid else "blocked"),
        returncode=returncode,
        task_return_packet_path=submit_data.get("packet_path"),
        context_proof_accepted=submit_data.get("context_proof_accepted"),
        template_action_proof_accepted=submit_data.get("template_action_proof_accepted"),
        worker_shift_lease_release_receipt_path=(lease_release or {}).get("receipt_path"),
        worker_shift_lease_release_result=(lease_release or {}).get("release_result"),
    )
    if accepted:
        sync_reply = _sync_domain_weaver_agent_comms_task_return(
            shell_root,
            request=request,
            request_rel=request_rel,
            run=run,
            submit_data=submit_data,
        )
        if sync_reply.get("attempted"):
            run["domain_weaver_agent_comms_synced_reply"] = sync_reply
    run["worker_return_status"] = _worker_return_status_for_run(run)
    _write_run_packet(run_path, run)
    if not accepted:
        _update_request_status(
            shell_root,
            request_rel,
            status="RETURN_TEMPLATE_INVALID" if not template_valid else "RETURN_RECORDED_PROOF_BLOCKED",
            failure_classification="BACKEND_CODEX_FAILURE",
        )
    remaining_entries = _current_running_entries_without(shell_root, _active_entry_for_run(run, pid=os.getpid()))
    _update_runner_state(
        shell_root,
        _state_for_active_entries(
            remaining_entries,
            latest_run=_connector_rel(run_path, shell_root),
            latest_worker_lifecycle_event=run["worker_lifecycle_events"][-1],
        ),
    )
    return {
        "schema_id": SCHEMA_ID,
        "ok": accepted,
        "result": run["status"],
        "run": run,
        "submit_result": submit,
        "active_root_proof": run.get("active_root_proof"),
        "worker_identity": run.get("worker_identity"),
        "domain_alignment": run.get("domain_alignment"),
        "worker_return_status": run.get("worker_return_status"),
        "production_authority": False,
        "live_execution_authority": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ION bounded Codex queue runner.")
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--process-once", action="store_true")
    parser.add_argument("--reconcile", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--start", action="store_true")
    parser.add_argument("--request-path", default=None)
    parser.add_argument("--lane-id", default=None)
    parser.add_argument("--codex-binary", default="codex")
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_CODEX_TIMEOUT_SECONDS)
    parser.add_argument("--worker-run", default=None)
    parser.add_argument("--recover-transient-usage-limit", action="store_true")
    parser.add_argument("--recovery-run-packet", default=None)
    parser.add_argument("--bridge-transient-usage-limit", action="store_true")
    parser.add_argument("--bridge-run-packet", default=None)
    parser.add_argument("--bridge-mode", default="parent_session_relay")
    parser.add_argument("--idempotency-key", default=None)
    parser.add_argument("--confirmation", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.bridge_transient_usage_limit:
        result = bridge_codex_transient_usage_limit_request(
            args.ion_root,
            run_packet_path=args.bridge_run_packet or "",
            confirmation=args.confirmation or "",
            idempotency_key=args.idempotency_key or "",
            bridge_mode=args.bridge_mode,
        )
        ok = bool(result.get("ok"))
    elif args.recover_transient_usage_limit:
        result = requeue_codex_transient_usage_limit_request(
            args.ion_root,
            run_packet_path=args.recovery_run_packet or "",
            confirmation=args.confirmation or "",
            start=args.start,
            background=True,
            codex_binary=args.codex_binary,
            timeout_seconds=args.timeout_seconds,
        )
        ok = bool(result.get("ok"))
    elif args.worker_run:
        result = run_codex_queue_worker(args.ion_root, args.worker_run)
        ok = bool(result.get("ok"))
    elif args.reconcile:
        result = reconcile_codex_queue_runner_state(args.ion_root, write=args.write)
        ok = bool(result.get("ok"))
    elif args.process_once:
        result = process_codex_queue_once(
            args.ion_root,
            request_path=args.request_path,
            lane_id=args.lane_id,
            start=args.start,
            background=True,
            codex_binary=args.codex_binary,
            timeout_seconds=args.timeout_seconds,
        )
        ok = bool(result.get("ok"))
    else:
        result = build_codex_queue_runner_status(args.ion_root, reconcile=False)
        ok = result.get("verdict") == READY_VERDICT

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result.get("verdict") or result.get("result") or ("OK" if ok else "BLOCKED"))
        if result.get("finding"):
            print(f"- {result['finding']}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
