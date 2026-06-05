"""V120 ChatGPT browser MCP connector contract.

This module defines the bounded tool contract for a future ChatGPT-facing ION
connector. It is dependency-free and does not expose arbitrary shell, arbitrary
file writes, deletion, git push, credentials, provider calls, or browser control.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import difflib
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .ion_carrier_onboard import resolve_shell_root_from_ion_root
from .ion_carrier_onboarding_packet import build_carrier_onboarding_packet
from .ion_agent_invocation_broker import (
    agent_queue,
    agent_result,
    build_agent_broker_status,
    build_agent_spawn_plan,
    cancel_agent_invocation,
    invoke_agent,
    list_agents,
    swarm_step_once,
)
from .ion_action_mcp_branch_leaders import (
    action_branch_describe,
    action_branch_invoke,
    action_branch_list,
    action_branch_receipts,
)
from .ion_codex_queue_runner import (
    DEFAULT_CODEX_TIMEOUT_SECONDS,
    MAX_CODEX_TIMEOUT_SECONDS,
    build_ai_movement_preflight_warning_map,
    build_codex_parallel_plan_preview,
    build_codex_queue_runner_status,
    classify_codex_work_request_lane,
    materialize_codex_work_lane_index,
    process_codex_queue_once,
    reconcile_codex_queue_runner_state,
)
from .ion_codex_work_request_target_binding import (
    compact_codex_work_request_target_binding_projection,
    apply_codex_work_request_target_binding,
)
from .ion_agent_route_enforcement import (
    OPERATOR_ARTIFACT_HYGIENE_SECTION,
    apply_route_enforcement_metadata,
    operator_artifact_hygiene_required,
    validate_codex_route_enforcement,
)
from .ion_kernel_fanout_carrier_dryrun import build_kernel_fanout_carrier_dryrun_status
from .ion_cockpit_view_model import build_cockpit_view_model
from .ion_context_proof_gate import evaluate_context_proof_return, has_machine_read_evidence
from .ion_codex_operational_posture import (
    OPERATIONAL_POSTURE_SECTION,
    evaluate_operational_posture_proof,
    ion_operational_posture_required,
)
from .ion_project_workbench import (
    project_context_capsule,
    project_file_slice_read,
    build_project_workbench_timeline,
    build_project_workspace_status,
    project_action_run,
    project_browser_capture,
    project_file_read,
    project_patch_apply,
    project_patch_preview,
    project_patch_revert,
)
from .ion_receipt_hydration_mapper import build_receipt_hydration_view_model
from .ion_status import build_ion_status
from .ion_template_action_gate import evaluate_template_action_proof
from .ion_workspace_paths import display_path, resolve_ion_path
from .ion_artifact_purpose import (
    PURPOSE_MCP_CONNECTOR_CONTRACT,
    authorize_artifact_path,
    require_artifact_path,
)
from .ion_working_capsule_identity import (
    prepare_local_capsule_maintenance,
    working_capsule_preflight,
)
from .ion_worker_shift_presence import require_active_edit_lease

VERSION_LINE = "V120_CHATGPT_BROWSER_MCP_CONNECTOR_AND_CORRECT_CARRIER_ONBOARDING"
SCHEMA_ID = "ion.chatgpt_browser_mcp_connector_contract.v1"
CONNECTOR_ID = "ION_CHATGPT_BROWSER_CONNECTOR"
OUTPUT_RELATIVE_PATH = Path("ION/05_context/current/CHATGPT_BROWSER_MCP_CONNECTOR_CONTRACT_V120.json")
CONNECTOR_STATE_DIR = Path("ION/05_context/current/chatgpt_connector")
CODEX_WORK_QUEUE_RELATIVE_PATH = Path("ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json")
CODEX_WORK_REQUEST_IDEMPOTENCY_LEDGER_RELATIVE_PATH = CONNECTOR_STATE_DIR / "runtime" / "codex_work_request_idempotency_ledger.json"
BOUNDED_PATCH_APPLY_IDEMPOTENCY_LEDGER_RELATIVE_PATH = CONNECTOR_STATE_DIR / "runtime" / "bounded_patch_apply_idempotency_ledger.json"
CODEX_QUEUE_DUPLICATE_CLEANUP_IDEMPOTENCY_LEDGER_RELATIVE_PATH = CONNECTOR_STATE_DIR / "runtime" / "codex_queue_duplicate_cleanup_idempotency_ledger.json"
FILE_PUT_TEXT_IDEMPOTENCY_LEDGER_RELATIVE_PATH = CONNECTOR_STATE_DIR / "runtime" / "file_put_text_idempotency_ledger.json"
CODEX_QUEUE_DUPLICATE_CLEANUP_RECEIPT_DIR_RELATIVE_PATH = CONNECTOR_STATE_DIR / "receipts" / "codex_queue_duplicate_cleanup"
ACTIVE_CARRIER_MESSAGE_QUEUE_RELATIVE_PATH = Path("ION/05_context/current/ACTIVE_CARRIER_MESSAGE_QUEUE.json")

PROTOCOL_RELATIVE_PATH = Path("ION/02_architecture/ION_CHATGPT_BROWSER_MCP_CONNECTOR_PROTOCOL.md")
POLICY_RELATIVE_PATH = Path("ION/03_registry/ion_chatgpt_browser_mcp_tool_policy.yaml")
SCHEMA_RELATIVE_PATH = Path("ION/03_registry/ion_chatgpt_browser_mcp_connector.schema.json")
FULL_CARRIER_PROTOCOL_RELATIVE_PATH = Path("ION/02_architecture/ION_FULL_CARRIER_MCP_PARITY_PROTOCOL.md")
FULL_CARRIER_TOOL_REGISTRY_RELATIVE_PATH = Path("ION/03_registry/mcp_full_carrier_tool_registry.yaml")
FULL_CARRIER_CAPABILITY_REGISTRY_RELATIVE_PATH = Path("ION/03_registry/carrier_capability_registry.yaml")
INTEGRATION_DIR_RELATIVE_PATH = Path("../mcp/chatgpt_connector")
LEGACY_INTEGRATION_DIR_RELATIVE_PATH = Path("ION/09_integrations/mcp/chatgpt_connector")
SETUP_RELATIVE_PATH = Path("ION/docs/setup/CHATGPT_BROWSER_MCP_CONNECTOR_SETUP_V120.md")
WRAPPER_RELATIVE_PATH = INTEGRATION_DIR_RELATIVE_PATH / "ion_chatgpt_browser_connector.py"
MANIFEST_RELATIVE_PATH = INTEGRATION_DIR_RELATIVE_PATH / "connector_manifest.json"
MAX_TEXT_PUT_BYTES = 512 * 1024
MAX_UPLOAD_CHUNK_BYTES = 512 * 1024
MAX_UPLOAD_BYTES = 4 * 1024 * 1024
MAX_READ_BYTES = 256 * 1024
MAX_COMPACT_PREVIEW_BYTES = 2048
DEFAULT_COMPACT_PREVIEW_BYTES = 2048
MAX_COMPACT_CHANGED_PATHS = 64
MAX_QUEUE_PAGE_LIMIT = 200
DEFAULT_QUEUE_PAGE_LIMIT = 50
DEFAULT_COMPACT_WARNING_ROW_LIMIT = 5
MAX_COMPACT_WARNING_ROW_LIMIT = 25
DEFAULT_WORKER_LIFECYCLE_LIMIT = 12
MAX_WORKER_LIFECYCLE_LIMIT = 64
DEFAULT_WORKER_LATEST_RUNS_LIMIT = 5
MAX_WORKER_LATEST_RUNS_LIMIT = 25
PROCESS_ONCE_PREVIEW_TARGETS = {
    "result",
    "stdout",
    "stderr",
    "worker_stdout",
    "worker_stderr",
    "task_return_body",
}
MAX_SEARCH_FILE_BYTES = 128 * 1024
MAX_SEARCH_FILES = 500
MIN_COMPLEX_WORKLOAD_TIMEOUT_SECONDS = 900
CODEX_MODEL_OVERRIDE_ALLOWED_FIELDS = (
    "selected_model",
    "selected_reasoning_effort",
    "reason",
    "source",
    "model",
    "reasoning_effort",
    "requested_model",
    "requested_reasoning_effort",
)
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
RETURN_TEMPLATE_REQUIRED_SECTIONS = (
    "### CONTEXT PROOF",
    "### TEMPLATE ACTION PROOF",
    "### VALIDATION",
    "### RESULT",
    "### WORKLOAD DIFF",
    "### BLOCKERS",
    "### RECOMMENDED NEXT PACKET",
)
WORKLOAD_POLICY_HINTS = (
    "agent",
    "cartograph",
    "probe",
    "proof",
    "design",
)
LEGACY_ARTIFACT_TARGET_ROOTS = (
    Path("ION/05_context/current/chatgpt_connector/artifacts"),
    Path("ION/05_context/current/chatgpt_connector/context_packages"),
    Path("ION/05_context/current/chatgpt_connector/scripts"),
    Path("ION/05_context/current/gemini_cli_carrier"),
    Path("dAimon/gemini_cli"),
    Path("dAimon/ion_kernel"),
    Path("ION/05_context/inbox"),
    Path("ION/05_context/signals"),
    Path("ION_VNEXT/06_context"),
    Path("ION_VNEXT/07_work"),
    Path("ION_VNEXT/09_references"),
)
DIRECT_REPO_INGEST_ROOTS = (
    Path("ION/01_doctrine"),
    Path("ION/02_architecture"),
    Path("ION/03_registry"),
    Path("ION/05_context/current/ACTIVE_CARRIER_ONBOARDING_PACKET.json"),
    Path("ION/05_context/current/ACTIVE_CARRIER_ONBOARDING_PACKET.chatgpt_browser.json"),
    Path("ION/05_context/current/ACTIVE_CARRIER_ONBOARDING_PACKET.codex_cli.json"),
    Path("ION/05_context/current/ACTIVE_CARRIER_ONBOARDING_PACKET.codex_extension.json"),
    Path("ION/05_context/current/action_surface_cartography"),
    Path("ION/05_context/current/chatgpt_connector"),
    Path("ION/05_context/current/context_settlement"),
    Path("ION/05_context/inbox"),
    Path("ION/07_templates"),
    Path("ION/tests"),
)
ARTIFACT_TARGET_ROOTS = LEGACY_ARTIFACT_TARGET_ROOTS + DIRECT_REPO_INGEST_ROOTS
BOUNDED_PATCH_ALLOWED_ROOTS = (
    Path("ION/05_context/current/ACTIVE_CARRIER_ONBOARDING_PACKET.json"),
    Path("ION/05_context/current/ACTIVE_CARRIER_ONBOARDING_PACKET.chatgpt_browser.json"),
    Path("ION/05_context/current/ACTIVE_CARRIER_ONBOARDING_PACKET.codex_cli.json"),
    Path("ION/05_context/current/ACTIVE_CARRIER_ONBOARDING_PACKET.codex_extension.json"),
    Path(".codex"),
    Path("docs"),
    Path("ION/01_doctrine"),
    Path("ION/02_architecture"),
    Path("ION/03_registry"),
    Path("ION/04_packages/kernel"),
    Path("ION/05_context/current/action_surface_cartography"),
    Path("ION/05_context/current/chatgpt_connector"),
    Path("ION/05_context/current/context_settlement"),
    Path("ION/05_context/inbox"),
    Path("ION/06_artifacts"),
    Path("ION/07_templates"),
    Path("ION/09_integrations"),
    Path("ION_VNEXT/06_context"),
    Path("ION_VNEXT/07_work"),
    Path("ION_VNEXT/09_references"),
    Path("ION/tests"),
)
PROTECTED_SHARED_CONTEXT_RELATIVE_PATHS = {
    "ION/05_context/current/codex_solo/CAPSULE.md",
    "ION/05_context/current/codex_solo/MINI.md",
    "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
    "ION/05_context/current/codex_solo/STATUS.json",
    "ION/05_context/current/codex_solo/ROUTE.json",
}
DEFAULT_SEARCH_ROOTS = (
    Path("ION/02_architecture"),
    Path("ION/03_registry"),
    Path("ION/04_packages/kernel"),
    Path("ION/05_context/current"),
    Path("ION/07_templates"),
    Path("ION/09_integrations/mcp"),
    Path("../mcp"),
    Path("ION/tests"),
)
FORBIDDEN_TRANSFER_PATH_PARTS = {
    ".env",
    "credentials",
    "credential",
    "secrets",
    "secret",
    "vault",
}
FORBIDDEN_READ_PATH_PARTS = FORBIDDEN_TRANSFER_PATH_PARTS | {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    ".venv",
    "venv",
}

STATUS_READ_TOOLS = {
    "ion_status",
    "ion_current_operating_packet",
    "ion_carrier_onboarding_packet",
    "ion_read_active_packet",
    "ion_context_plan",
    "ion_cockpit_view",
    "ion_artifact_manifest",
    "ion_receipt_search",
    "ion_git_status_summary",
    "ion_codex_work_queue",
    "ion_codex_queue_duplicate_audit",
    "ion_codex_queue_parallel_plan_preview",
    "ion_carrier_message_poll",
    "ion_file_read",
    "ion_file_search",
    "ion_tree_list",
    "ion_registry_read",
    "ion_template_read",
    "ion_context_compile",
    "ion_receipt_hydrate",
    "ion_tool_manifest",
    "ion_daemon_status",
    "ion_codex_queue_autorun_status",
    "ion_codex_worker_live_status",
    "ion_codex_worker_trace",
    "ion_agent_list",
    "ion_agent_status",
    "ion_agent_result",
    "ion_agent_queue",
    "ion_agent_spawn_plan",
    "ion_swarm_status",
    "ion_codex_capsule_chat_status",
    "ion_codex_capsule_message_poll",
    "ion_bounded_patch_preview",
    "ion_project_workspace_status",
    "ion_project_preview_status",
    "ion_project_git_status",
    "ion_project_workbench_timeline",
    "ion_project_context_capsule",
    "ion_project_file_read",
    "ion_project_file_slice_read",
    "ion_project_patch_preview",
    "ion_kernel_fanout_carrier_dryrun_status",
    "ion_action_branch_list",
    "ion_action_branch_describe",
    "ion_action_branch_receipts",
}

BOUNDED_QUEUE_RECEIPT_TOOLS = {
    "ion_queue_operator_message",
    "ion_request_codex_work_packet",
    "ion_submit_task_return",
    "ion_submit_alternate_worker_return",
    "ion_record_alternate_worker_provenance",
    "ion_record_native_subagent_transcript",
    "ion_record_chatgpt_decision",
    "ion_create_containment_receipt",
    "ion_file_put_text",
    "ion_artifact_upload_init",
    "ion_artifact_upload_chunk",
    "ion_artifact_upload_commit",
    "ion_carrier_message_send",
    "ion_carrier_message_ack",
    "ion_codex_queue_process_once",
    "ion_codex_queue_supersede_duplicates",
    "ion_agent_invoke",
    "ion_agent_cancel",
    "ion_swarm_step_once",
    "ion_codex_runner_reconcile",
    "ion_codex_capsule_message_send",
    "ion_codex_capsule_sync_to_queue",
    "ion_bounded_patch_apply",
    "ion_project_patch_apply",
    "ion_project_patch_revert",
    "ion_project_action_run",
    "ion_project_browser_capture",
    "ion_action_branch_invoke",
}

TASK_RETURN_SUBMIT_TOOLS = {
    "ion_submit_task_return",
    "ion_submit_alternate_worker_return",
}

DEFAULT_TASK_RETURN_LANE = "codex_queue_runner"
ALTERNATE_WORKER_RETURN_LANE = "alternate_worker_return"
ALTERNATE_WORKER_RETURN_CONFIRMATION = "ION_ALTERNATE_WORKER_RETURN_CONFIRMED"
ALTERNATE_WORKER_PROVENANCE_CONFIRMATION = "ION_ALTERNATE_WORKER_PROVENANCE_CONFIRMED"
ALTERNATE_WORKER_PROVENANCE_RECEIPT_DIR = CONNECTOR_STATE_DIR / "alternate_worker_provenance_receipts"
NATIVE_SUBAGENT_TRANSCRIPT_CONFIRMATION = "ION_NATIVE_SUBAGENT_TRANSCRIPT_CONFIRMED"
NATIVE_SUBAGENT_TRANSCRIPT_RECEIPT_DIR = CONNECTOR_STATE_DIR / "native_subagent_transcript_receipts"
ALTERNATE_WORKER_IDENTITY_REQUIRED_FIELDS = (
    "worker_id",
    "worker_role",
    "worker_runtime",
    "origin",
    "source_ref",
)
ALTERNATE_WORKER_IDENTITY_OPTIONAL_FIELDS = (
    "agent_id",
    "role_id",
    "domain_id",
    "task_contract_id",
    "context_mount_path",
    "return_source_path",
    "run_ref",
    "thread_id",
    "message_id",
)
ALTERNATE_WORKER_PROVENANCE_REQUIRED_FIELDS = (
    "source_kind",
    "source_ref",
    "observed_by",
    "work_request_path",
    "worker_id",
    "worker_output_sha256",
    "claim_boundary",
)
ALTERNATE_WORKER_ALLOWED_SOURCE_KINDS = {
    "multi_agent_v1",
    "codex_subagent",
    "codex_cli_worker",
    "domain_weaver_worker",
    "external_worker_return",
}
ALTERNATE_WORKER_FORBIDDEN_SOURCE_MARKERS = {
    "parent_session_relay",
    "carrier_session_bridge",
    "transient_usage_limit_bridge",
    "failed_cli_log",
    "failed log",
    "stdout.log",
    "stderr.log",
    "codex_carrier_steward",
    "role.codex_carrier_steward",
}

FORBIDDEN_CAPABILITIES = {
    "arbitrary_shell",
    "arbitrary_file_write",
    "direct_delete",
    "git_push",
    "credential_access",
    "browser_computer_control",
    "provider_api_calls",
    "unbounded_local_filesystem_access",
    "production_deployment",
    "direct_accept_unproofed_worker_output",
}

ACTIVE_PACKET_ALLOWLIST = {
    "hook": "ION/05_context/current/ACTIVE_CURSOR_HOOK_STATE.json",
    "work": "ION/05_context/current/ACTIVE_WORK_PACKET.json",
    "spawn_plan": "ION/05_context/current/ACTIVE_ROLE_SPAWN_PLAN.json",
    "carrier_turn": "ION/05_context/current/ACTIVE_CARRIER_TURN_PACKET.json",
    "task_return_ledger": "ION/05_context/current/ACTIVE_CARRIER_TASK_RETURN_LEDGER.json",
    "steward_queue": "ION/05_context/current/ACTIVE_STEWARD_INTEGRATION_QUEUE.json",
    "operator_queue": "ION/05_context/current/ACTIVE_OPERATOR_MESSAGE_QUEUE.json",
    "human_gates": "ION/05_context/current/ACTIVE_HUMAN_GATE_QUEUE.json",
    "cockpit": "ION/05_context/current/ACTIVE_COCKPIT_VIEW_MODEL.json",
    "context_window": "ION/05_context/current/ACTIVE_AGENT_CONTEXT_WINDOW_PLAN.json",
    "front_door": "ION/05_context/current/ACTIVE_FRONT_DOOR_TEAM_PLAN.json",
    "lane_timeline": "ION/05_context/current/ACTIVE_LANE_TIMELINE_VIEW_MODEL.json",
    "receipt_hydration": "ION/05_context/current/ACTIVE_RECEIPT_HYDRATION_VIEW_MODEL.json",
    "runtime_debug": "ION/05_context/current/ACTIVE_RUNTIME_DEBUG_OVERLAY.json",
    "current_operating_packet": "ION/docs/setup/ION_CURRENT_OPERATING_PACKET_V119.md",
    "carrier_onboarding": "ION/05_context/current/ACTIVE_CARRIER_ONBOARDING_PACKET.json",
    "chatgpt_codex_work_queue": "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json",
    "carrier_messages": "ION/05_context/current/ACTIVE_CARRIER_MESSAGE_QUEUE.json",
    "chatgpt_tunnel": "ION/05_context/current/CHATGPT_BROWSER_CLOUDFLARE_TUNNEL_V122.json",
    "chatgpt_http_preview": "ION/05_context/current/CHATGPT_BROWSER_HTTP_MCP_PREVIEW_V121.json",
    "chatgpt_connector_contract": "ION/05_context/current/CHATGPT_BROWSER_MCP_CONNECTOR_CONTRACT_V120.json",
    "codex_queue_runner_state": "ION/05_context/current/chatgpt_connector/runtime/codex_queue_runner_state.json",
    "agent_invocation_broker_state": "ION/05_context/current/chatgpt_connector/runtime/agent_invocation_broker_state.json",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_connector_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    return resolve_shell_root_from_ion_root(root)


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _require_connector_artifact_path(root: Path, path: str | Path) -> Path:
    return require_artifact_path(
        path,
        purpose=PURPOSE_MCP_CONNECTOR_CONTRACT,
        active_root=root,
        base_root="active_repo",
    )


def _sanitize_required_context_reads(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    reads: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        if isinstance(item, Mapping):
            path = str(item.get("path") or "").strip()
            kind = str(item.get("kind") or "file").strip() or "file"
            required = bool(item.get("required", True))
        else:
            path = str(item or "").strip()
            kind = "file"
            required = True
        if not path or path in seen or path.startswith("/") or ".." in Path(path).parts:
            continue
        seen.add(path)
        reads.append({"kind": kind, "path": path, "required": required})
    return reads[:64]


def _sanitize_connector_string_list(value: Any, *, limit: int = 64) -> list[str]:
    if not isinstance(value, list):
        return []
    items: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = str(item or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        items.append(text)
    return items[:limit]


def _apply_domain_weaver_work_request_identity_fields(
    payload: dict[str, Any],
    args: Mapping[str, Any],
) -> None:
    """Preserve Domain Weaver worker identity fields on Codex queue rows."""

    for field in (
        "domain_id",
        "agent_role_id",
        "agent_role",
        "role_tier",
        "callsign",
        "true_name",
        "domain_context_package",
    ):
        value = str(args.get(field) or "").strip()
        if value:
            payload[field] = value
    for field in ("planned_writes", "planned_artifacts"):
        values = _sanitize_connector_string_list(args.get(field))
        if values:
            payload[field] = values
    if isinstance(args.get("domain_weaver_spawn_dispatch"), Mapping):
        payload["domain_weaver_spawn_dispatch"] = dict(args["domain_weaver_spawn_dispatch"])


def _sanitize_codex_model_override(value: Any) -> dict[str, str] | None:
    if not isinstance(value, Mapping):
        return None
    sanitized: dict[str, str] = {}
    for key in CODEX_MODEL_OVERRIDE_ALLOWED_FIELDS:
        text = str(value.get(key) or "").strip()
        if text:
            sanitized[key] = text
    return sanitized or None


def _safe_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")[:80] or "chatgpt_packet"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _safe_rel_path(root: Path, value: str) -> Path:
    rel = Path(value)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("path must be repo-relative and may not escape the ION root")
    candidate = (root / rel).resolve()
    candidate.relative_to(root)
    return candidate


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _is_under_any(path: Path, roots: tuple[Path, ...]) -> bool:
    return any(_is_under(path, candidate) for candidate in roots)


def _direct_repo_ingest_target(target: Path, root: Path) -> bool:
    direct_roots = tuple((root / rel).resolve() for rel in DIRECT_REPO_INGEST_ROOTS)
    return _is_under_any(target, direct_roots)


def _validate_transfer_target(root: Path, value: str) -> tuple[Path | None, str | None]:
    if not value.strip():
        return None, "target_path_required"
    try:
        target = _safe_rel_path(root, value)
    except (ValueError, RuntimeError):
        return None, "target_path_must_be_repo_relative_without_escape"
    rel_parts = [part.lower() for part in target.relative_to(root).parts]
    if ".git" in rel_parts or any(part in FORBIDDEN_TRANSFER_PATH_PARTS for part in rel_parts):
        return None, "target_path_forbidden_by_transfer_policy"
    allowed_roots = tuple((root / rel).resolve() for rel in ARTIFACT_TARGET_ROOTS)
    if not _is_under_any(target, allowed_roots):
        return None, "target_path_not_in_artifact_transfer_roots"
    if target.name in {"", ".", ".."}:
        return None, "target_filename_required"
    decision = authorize_artifact_path(
        target,
        purpose=PURPOSE_MCP_CONNECTOR_CONTRACT,
        active_root=root,
        base_root="active_repo",
    )
    if not decision["authorized"]:
        return None, f"path_authority_{decision['reason_code']}"
    return target, None


def _validate_read_path(
    root: Path,
    value: str,
    *,
    allowed_roots: tuple[Path, ...] | None = None,
) -> tuple[Path | None, str | None]:
    if not value.strip():
        return None, "path_required"
    try:
        target = _safe_rel_path(root, value)
    except (ValueError, RuntimeError):
        return None, "path_must_be_repo_relative_without_escape"
    rel_parts = [part.lower() for part in target.relative_to(root).parts]
    if any(part in FORBIDDEN_READ_PATH_PARTS for part in rel_parts):
        return None, "path_forbidden_by_read_policy"
    if allowed_roots:
        resolved_roots = [(root / rel).resolve() for rel in allowed_roots]
        if not any(_is_under(target, allowed) for allowed in resolved_roots):
            return None, "path_not_in_tool_read_roots"
    return target, None


def _connector_rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _extract_yaml_list(text: str, key: str) -> list[str]:
    values: list[str] = []
    in_block = False
    prefix = f"{key}:"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == prefix:
            in_block = True
            continue
        if in_block:
            if stripped.startswith("- "):
                values.append(stripped[2:].strip().strip("\"'"))
                continue
            if stripped and not line.startswith(" ") and not line.startswith("\t"):
                break
    return values


def _read_policy(root: Path) -> dict[str, list[str]]:
    policy_path = root / POLICY_RELATIVE_PATH
    text = _read_text(policy_path) if policy_path.exists() else ""
    return {
        "allowed_status_read_tools": _extract_yaml_list(text, "allowed_status_read_tools"),
        "allowed_bounded_queue_receipt_tools": _extract_yaml_list(text, "allowed_bounded_queue_receipt_tools"),
        "forbidden_tools": _extract_yaml_list(text, "forbidden_tools"),
        "required_task_return_sections": _extract_yaml_list(text, "required_task_return_sections"),
        "bounded_write_roots": _extract_yaml_list(text, "bounded_write_roots"),
    }


def tool_descriptors() -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    for name in sorted(STATUS_READ_TOOLS):
        tools.append({
            "name": name,
            "family": "status_read",
            "mutates_active_state": False,
            "requires_context_proof": False,
            "requires_template_action_proof": False,
        })
    for name in sorted(BOUNDED_QUEUE_RECEIPT_TOOLS):
        tools.append({
            "name": name,
            "family": "bounded_queue_receipt",
            "mutates_active_state": True,
            "writes_bounded_packet_only": True,
            "requires_context_proof": name in TASK_RETURN_SUBMIT_TOOLS,
            "requires_template_action_proof": name in TASK_RETURN_SUBMIT_TOOLS,
        })
    return tools


def _ok(name: str, data: Any, *, mutates_active_state: bool = False) -> dict[str, Any]:
    return {
        "schema_id": "ion.chatgpt_browser_connector_tool_result.v1",
        "tool": name,
        "ok": True,
        "mutates_active_state": mutates_active_state,
        "data": data,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _blocked(name: str, finding: str, data: Any | None = None) -> dict[str, Any]:
    return {
        "schema_id": "ion.chatgpt_browser_connector_tool_result.v1",
        "tool": name,
        "ok": False,
        "finding": finding,
        "data": data,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _latest_matching(root: Path, pattern: str) -> Path | None:
    candidates = sorted((root / "ION/05_context/current").glob(pattern))
    return candidates[-1] if candidates else None


def _packet_read(
    root: Path,
    packet: str,
    *,
    max_bytes: int | None = None,
    tool_name: str = "ion_read_active_packet",
) -> dict[str, Any]:
    rel = ACTIVE_PACKET_ALLOWLIST.get(packet)
    if not rel:
        return _blocked(tool_name, "packet_not_allowlisted", {"allowed": sorted(ACTIVE_PACKET_ALLOWLIST)})
    path = root / rel
    if not path.exists():
        return _blocked(tool_name, "packet_missing", {"path": rel})
    if max_bytes is not None:
        bounded_max = min(max(int(max_bytes), 1), MAX_READ_BYTES)
        data = path.read_bytes()
        shown = data[:bounded_max].decode("utf-8", errors="replace")
        return _ok(
            tool_name,
            {
                "path": rel,
                "content_preview": shown,
                "content_truncated": len(data) > bounded_max,
                "content_bytes": len(data),
                "max_bytes": bounded_max,
            },
        )
    if path.suffix == ".json":
        data: Any = _read_json(path)
    else:
        data = {"text": _read_text(path)}
    return _ok(tool_name, {"path": rel, "content": data})


def _artifact_manifest(root: Path) -> dict[str, Any]:
    safe = _latest_matching(root, "SAFE_FULL_PROJECT_PACKAGE_RESULT_V*.json")
    trunk = _latest_matching(root, "TRUNK_PRESERVATION_REPORT_V*.json")
    safe_payload = _read_json(safe) if safe else None
    trunk_payload = _read_json(trunk) if trunk else None
    return {
        "safe_full_project_package_result_path": str(safe.relative_to(root)) if safe else None,
        "trunk_preservation_report_path": str(trunk.relative_to(root)) if trunk else None,
        "zip_path": safe_payload.get("zip_path") if safe_payload else None,
        "zip_sha256": safe_payload.get("zip_sha256") if safe_payload else None,
        "packaging_verdict": trunk_payload.get("packaging_verdict") if trunk_payload else None,
        "unexpected_removed_files": trunk_payload.get("unexpected_removed_files") if trunk_payload else None,
        "protected_removed_files": trunk_payload.get("protected_removed_files") if trunk_payload else None,
    }


def _receipt_search(root: Path, query: str, limit: int) -> dict[str, Any]:
    normalized = query.lower().strip()
    matches: list[dict[str, Any]] = []
    for path in sorted((root / "ION/05_context/current").rglob("*.json")):
        rel = path.relative_to(root).as_posix()
        if len(matches) >= limit:
            break
        if "receipt" not in rel.lower() and "return" not in rel.lower():
            continue
        text = _read_text(path)
        if normalized and normalized not in text.lower() and normalized not in rel.lower():
            continue
        matches.append({"path": rel, "sha256": _sha256_text(text), "bytes": len(text.encode("utf-8"))})
    return {"query": query, "matches": matches, "limit": limit}


def _git_status_summary(root: Path) -> dict[str, Any]:
    git = root / ".git"
    if not git.exists():
        return {"git_present": False, "working_tree_scan": "not_available_without_git_metadata"}
    head_path = git / "HEAD"
    head = _read_text(head_path).strip() if head_path.exists() else None
    ref = None
    commit = None
    if head and head.startswith("ref: "):
        ref = head[5:]
        ref_path = git / ref
        commit = _read_text(ref_path).strip() if ref_path.exists() else None
    elif head:
        commit = head
    return {
        "git_present": True,
        "head": head,
        "ref": ref,
        "commit": commit,
        "working_tree_scan": "not_performed_no_shell_or_git_subprocess",
    }


def _bounded_file_read(
    root: Path,
    args: Mapping[str, Any],
    *,
    tool_name: str = "ion_file_read",
    allowed_roots: tuple[Path, ...] | None = None,
) -> dict[str, Any]:
    rel_value = str(args.get("path") or args.get("target_path") or "").strip()
    target, finding = _validate_read_path(root, rel_value, allowed_roots=allowed_roots)
    if finding or target is None:
        return _blocked(tool_name, finding or "invalid_path")
    if not target.exists():
        return _blocked(tool_name, "path_missing", {"path": rel_value})
    if not target.is_file():
        return _blocked(tool_name, "path_not_file", {"path": _connector_rel(target, root)})
    max_bytes = min(max(int(args.get("max_bytes") or 64 * 1024), 1), MAX_READ_BYTES)
    data = target.read_bytes()
    shown = data[:max_bytes]
    text = shown.decode("utf-8", errors="replace")
    return _ok(tool_name, {
        "path": _connector_rel(target, root),
        "bytes": len(data),
        "sha256": _sha256_bytes(data),
        "text": text,
        "truncated": len(data) > len(shown),
        "max_bytes": max_bytes,
        "production_authority": False,
        "live_execution_authority": False,
    })


def _tree_list(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    rel_value = str(args.get("path") or ".").strip() or "."
    base, finding = _validate_read_path(root, rel_value)
    if finding or base is None:
        return _blocked("ion_tree_list", finding or "invalid_path")
    if not base.exists():
        return _blocked("ion_tree_list", "path_missing", {"path": rel_value})
    max_depth = min(max(int(args.get("max_depth") or 2), 0), 6)
    limit = min(max(int(args.get("limit") or 200), 1), 1000)
    entries: list[dict[str, Any]] = []
    start_depth = len(base.relative_to(root).parts)
    paths = [base] if base.is_file() else sorted(base.rglob("*"), key=lambda item: item.relative_to(root).as_posix())
    for path in paths:
        rel_parts = [part.lower() for part in path.relative_to(root).parts]
        if any(part in FORBIDDEN_READ_PATH_PARTS for part in rel_parts):
            continue
        depth = len(path.relative_to(root).parts) - start_depth
        if depth > max_depth:
            continue
        stat = path.stat()
        entries.append({
            "path": _connector_rel(path, root),
            "kind": "dir" if path.is_dir() else "file",
            "bytes": stat.st_size if path.is_file() else None,
        })
        if len(entries) >= limit:
            break
    return _ok("ion_tree_list", {
        "root": _connector_rel(base, root),
        "max_depth": max_depth,
        "limit": limit,
        "entry_count": len(entries),
        "entries": entries,
        "truncated": len(entries) >= limit,
    })


def _file_search(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    query = str(args.get("query") or "").strip()
    if not query:
        return _blocked("ion_file_search", "query_required")
    limit = min(max(int(args.get("limit") or 25), 1), 100)
    max_files = min(max(int(args.get("max_files") or MAX_SEARCH_FILES), 1), MAX_SEARCH_FILES)
    raw_roots = args.get("roots")
    if isinstance(raw_roots, list) and raw_roots:
        search_roots: list[Path] = []
        for value in raw_roots[:10]:
            path, finding = _validate_read_path(root, str(value))
            if finding or path is None:
                continue
            search_roots.append(path)
    else:
        search_roots = [resolve_ion_path(root, rel) for rel in DEFAULT_SEARCH_ROOTS if resolve_ion_path(root, rel).exists()]
    normalized = query.lower()
    matches: list[dict[str, Any]] = []
    scanned = 0
    seen: set[str] = set()
    for base in search_roots:
        candidates = [base] if base.is_file() else sorted(base.rglob("*"), key=lambda item: item.relative_to(root).as_posix())
        for path in candidates:
            if scanned >= max_files or len(matches) >= limit:
                break
            if not path.is_file():
                continue
            rel = _connector_rel(path, root)
            if rel in seen:
                continue
            seen.add(rel)
            rel_parts = [part.lower() for part in path.relative_to(root).parts]
            if any(part in FORBIDDEN_READ_PATH_PARTS for part in rel_parts):
                continue
            scanned += 1
            try:
                data = path.read_bytes()
            except OSError:
                continue
            name_hit = normalized in rel.lower()
            text_hit = False
            line_hits: list[dict[str, Any]] = []
            if len(data) <= MAX_SEARCH_FILE_BYTES:
                text = data.decode("utf-8", errors="ignore")
                for number, line in enumerate(text.splitlines(), start=1):
                    if normalized in line.lower():
                        text_hit = True
                        line_hits.append({"line": number, "text": line[:240]})
                        if len(line_hits) >= 3:
                            break
            if name_hit or text_hit:
                matches.append({
                    "path": rel,
                    "sha256": _sha256_bytes(data),
                    "bytes": len(data),
                    "name_hit": name_hit,
                    "line_hits": line_hits,
                })
    return _ok("ion_file_search", {
        "query": query,
        "matches": matches,
        "match_count": len(matches),
        "scanned_files": scanned,
        "limit": limit,
        "max_files": max_files,
    })


def _registry_read(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    raw = str(args.get("path") or args.get("name") or "").strip()
    if raw and "/" not in raw:
        raw = f"ION/03_registry/{raw}"
    return _bounded_file_read(root, {"path": raw, "max_bytes": args.get("max_bytes")}, tool_name="ion_registry_read", allowed_roots=(Path("ION/03_registry"),))


def _template_read(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    raw = str(args.get("path") or args.get("name") or "").strip()
    if raw and "/" not in raw:
        raw = f"ION/07_templates/{raw}"
    return _bounded_file_read(root, {"path": raw, "max_bytes": args.get("max_bytes")}, tool_name="ion_template_read", allowed_roots=(Path("ION/07_templates"),))


def _context_compile(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    profile = str(args.get("profile") or "full_carrier_mcp_parity").strip()
    include_excerpts = bool(args.get("include_excerpts"))
    surface_paths = [
        "ION/REPO_AUTHORITY.md",
        "ION/02_architecture/ION_MOUNT_CONTRACT.md",
        "ION/02_architecture/ION_FULL_CARRIER_MCP_PARITY_PROTOCOL.md",
        "ION/02_architecture/ION_CARRIER_TO_CARRIER_COMMUNICATION_PROTOCOL.md",
        "ION/03_registry/chatgpt_browser_carrier_profile.yaml",
        "ION/03_registry/carrier_capability_registry.yaml",
        "ION/03_registry/mcp_full_carrier_tool_registry.yaml",
        "ION/03_registry/ion_action_mcp_branch_leader_registry.yaml",
        "ION/05_context/current/CHATGPT_BROWSER_MCP_CONNECTOR_CONTRACT_V120.json",
        "ION/05_context/current/CHATGPT_BROWSER_CLOUDFLARE_TUNNEL_V122.json",
        "ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json",
        "ION/05_context/current/ACTIVE_CARRIER_MESSAGE_QUEUE.json",
        "ION/05_context/current/chatgpt_connector/ION_CONTEXT_CAPSULE.candidate.yaml",
        "ION/05_context/current/chatgpt_connector/context_packages/CHATGPT_BROWSER_ACTIVE_CONTEXT_PACKAGE.candidate.json",
        "ION/05_context/current/chatgpt_connector/artifacts/context_packages/CHATGPT_BROWSER_ACTIVE_CONTEXT_PACKAGE.candidate.json",
        "ION/05_context/current/chatgpt_connector/artifacts/context_packages/SEV_VNEXT_DOMAIN_WEAVE_CONTEXT_PACKAGE.candidate.json",
        "ION_VNEXT/01_canon/DOMAIN_WEAVE_READ_FIRST_BINDING.yaml",
        "ION_VNEXT/06_context/domain_weave/MANIFEST.json",
        "ION/02_architecture/ION_SUPABASE_OPERATING_RUNTIME_PROTOCOL_V0_1.md",
    ]
    surfaces: list[dict[str, Any]] = []
    for rel in surface_paths:
        path, finding = _validate_read_path(root, rel)
        if finding or path is None or not path.exists() or not path.is_file():
            surfaces.append({"path": rel, "exists": False, "finding": finding or "path_missing"})
            continue
        data = path.read_bytes()
        item: dict[str, Any] = {
            "path": rel,
            "exists": True,
            "bytes": len(data),
            "sha256": _sha256_bytes(data),
        }
        if include_excerpts:
            item["excerpt"] = data[:2400].decode("utf-8", errors="replace")
            item["excerpt_truncated"] = len(data) > 2400
        surfaces.append(item)
    return _ok("ion_context_compile", {
        "schema_id": "ion.chatgpt_browser_connector_context_compile.v1",
        "profile": profile,
        "surface_count": len(surfaces),
        "surfaces": surfaces,
        "production_authority": False,
        "live_execution_authority": False,
    })


def _receipt_hydrate(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    model = build_receipt_hydration_view_model(root)
    limit = min(max(int(args.get("limit") or 25), 1), 100)
    records = list(model.get("records") or [])[:limit]
    return _ok("ion_receipt_hydrate", {
        "schema_id": model.get("schema_id"),
        "generated_at": model.get("generated_at"),
        "source_paths": model.get("source_paths"),
        "receipt_count": model.get("receipt_count"),
        "unresolved_count": model.get("unresolved_count"),
        "hydration_conflict_count": model.get("hydration_conflict_count"),
        "records": records,
        "limit": limit,
    })


def _tool_manifest(root: Path) -> dict[str, Any]:
    contract = audit_chatgpt_browser_mcp_connector_contract(root)
    return {
        "schema_id": "ion.chatgpt_browser_connector_tool_manifest.v1",
        "connector_id": CONNECTOR_ID,
        "tool_count": len(contract.get("allowed_tools") or []),
        "allowed_tools": contract.get("allowed_tools"),
        "status_read_tools": contract.get("status_read_tools"),
        "bounded_queue_receipt_tools": contract.get("bounded_queue_receipt_tools"),
        "tool_descriptors": contract.get("tool_descriptors"),
        "source_paths": contract.get("source_paths"),
        "forbidden_tools": contract.get("forbidden_tools"),
        "production_authority": False,
        "live_execution_authority": False,
    }


def _write_connector_packet(root: Path, subdir: str, prefix: str, payload: Mapping[str, Any]) -> Path:
    timestamp = _now()
    packet_id = f"{timestamp.replace(':', '').replace('+', 'Z')}_{_safe_slug(prefix)}"
    path = root / CONNECTOR_STATE_DIR / subdir / f"{packet_id}.json"
    counter = 1
    while path.exists():
        path = root / CONNECTOR_STATE_DIR / subdir / f"{packet_id}_{counter}.json"
        counter += 1
    _require_connector_artifact_path(root, path)
    value = dict(payload)
    value.setdefault("schema_id", f"ion.chatgpt_browser_connector_{subdir.rstrip('s')}.v1")
    value.setdefault("created_at", timestamp)
    value.setdefault("connector_id", CONNECTOR_ID)
    value.setdefault("production_authority", False)
    value.setdefault("live_execution_authority", False)
    _write_json(path, value)
    return path



def _normalize_idempotency_token(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.:-]+", "_", value.strip())[:180]


def _codex_work_request_objective_fingerprint(objective: str) -> str:
    normalized = re.sub(r"\s+", " ", objective).strip()
    return _sha256_text(normalized)


def _codex_work_request_dedupe_key(args: Mapping[str, Any], objective: str) -> tuple[str, str, bool]:
    """Return (dedupe_key, source, implicit).

    The ChatGPT carrier can see no response for a mutation even after the local
    server accepted it. Without a stable key, safe operator retries create
    duplicate Codex work packets. Prefer caller-provided idempotency/client
    keys; fall back to an objective fingerprint so no-receipt retries for the
    same objective return the original packet instead of mutating again.
    """

    explicit = str(args.get("idempotency_key") or "").strip()
    if explicit:
        return f"idempotency_key:{_normalize_idempotency_token(explicit)}", "idempotency_key", False
    client_request_id = str(args.get("client_request_id") or "").strip()
    if client_request_id:
        return f"client_request_id:{_normalize_idempotency_token(client_request_id)}", "client_request_id", False
    return f"objective_sha256:{_codex_work_request_objective_fingerprint(objective)}", "objective_sha256", True


def _load_codex_work_request_idempotency_ledger(root: Path) -> dict[str, Any]:
    path = root / CODEX_WORK_REQUEST_IDEMPOTENCY_LEDGER_RELATIVE_PATH
    payload = _read_json(path)
    if isinstance(payload, dict):
        payload.setdefault("schema_id", "ion.chatgpt_browser_connector_codex_work_request_idempotency_ledger.v1")
        payload.setdefault("entries", {})
        return payload
    return {
        "schema_id": "ion.chatgpt_browser_connector_codex_work_request_idempotency_ledger.v1",
        "created_at": _now(),
        "updated_at": _now(),
        "entries": {},
        "production_authority": False,
        "live_execution_authority": False,
    }


def _save_codex_work_request_idempotency_ledger(root: Path, ledger: Mapping[str, Any]) -> None:
    _write_json(root / CODEX_WORK_REQUEST_IDEMPOTENCY_LEDGER_RELATIVE_PATH, dict(ledger))


def _codex_work_request_existing_entry(root: Path, dedupe_key: str) -> dict[str, Any] | None:
    ledger = _load_codex_work_request_idempotency_ledger(root)
    entries = ledger.get("entries") if isinstance(ledger.get("entries"), Mapping) else {}
    entry = entries.get(dedupe_key)
    if isinstance(entry, Mapping):
        packet_path = root / str(entry.get("packet_path") or "")
        if packet_path.exists():
            return dict(entry)
    # Older packets may predate the ledger. Scan bounded request packets for
    # a recorded key so the first replay after an upgrade can still be safe.
    requests_root = root / CONNECTOR_STATE_DIR / "codex_work_requests"
    if requests_root.exists():
        for path in sorted(requests_root.glob("*.json"), reverse=True):
            payload = _load_json_file(path)
            if payload.get("dedupe_key") == dedupe_key:
                return {
                    "request_id": payload.get("request_id"),
                    "packet_path": path.relative_to(root).as_posix(),
                    "status": payload.get("status"),
                    "objective_sha256": payload.get("objective_sha256"),
                    "created_at": payload.get("created_at"),
                    "found_by": "request_scan",
                }
    return None


def _record_codex_work_request_idempotency(
    root: Path,
    dedupe_key: str,
    *,
    source: str,
    implicit: bool,
    payload: Mapping[str, Any],
    packet_path: Path,
) -> None:
    ledger = _load_codex_work_request_idempotency_ledger(root)
    entries = dict(ledger.get("entries") if isinstance(ledger.get("entries"), Mapping) else {})
    entries[dedupe_key] = {
        "recorded_at": _now(),
        "source": source,
        "implicit": implicit,
        "request_id": payload.get("request_id"),
        "packet_path": packet_path.relative_to(root).as_posix(),
        "status": payload.get("status"),
        "objective_sha256": payload.get("objective_sha256"),
        "production_authority": False,
        "live_execution_authority": False,
    }
    ledger["entries"] = entries
    ledger["updated_at"] = _now()
    _save_codex_work_request_idempotency_ledger(root, ledger)


def _codex_work_request_replay_result(root: Path, tool_name: str, existing: Mapping[str, Any], dedupe_key: str, source: str) -> dict[str, Any]:
    """Return a successful idempotent replay without mutating the queue.

    Retried mutation calls after a no-receipt/timeout must be safe. Returning
    ok=True lets ChatGPT recover the original packet handle while
    duplicate_prevented explains that no new packet was created.
    """

    queue = _codex_work_queue(root)
    return _ok(
        tool_name,
        {
            "request_id": existing.get("request_id"),
            "packet_path": existing.get("packet_path"),
            "codex_work_queue_path": CODEX_WORK_QUEUE_RELATIVE_PATH.as_posix(),
            "codex_work_queue_request_count": queue["request_count"],
            "idempotent_replay": True,
            "duplicate_prevented": True,
            "dedupe_key": dedupe_key,
            "idempotency_source": source,
            "existing": dict(existing),
        },
        mutates_active_state=False,
    )


def _load_bounded_patch_apply_idempotency_ledger(root: Path) -> dict[str, Any]:
    path = root / BOUNDED_PATCH_APPLY_IDEMPOTENCY_LEDGER_RELATIVE_PATH
    payload = _read_json(path)
    if isinstance(payload, dict):
        payload.setdefault("schema_id", "ion.chatgpt_browser_connector_bounded_patch_apply_idempotency_ledger.v1")
        payload.setdefault("entries", {})
        return payload
    return {
        "schema_id": "ion.chatgpt_browser_connector_bounded_patch_apply_idempotency_ledger.v1",
        "created_at": _now(),
        "updated_at": _now(),
        "entries": {},
        "production_authority": False,
        "live_execution_authority": False,
    }


def _save_bounded_patch_apply_idempotency_ledger(root: Path, ledger: Mapping[str, Any]) -> None:
    _write_json(root / BOUNDED_PATCH_APPLY_IDEMPOTENCY_LEDGER_RELATIVE_PATH, dict(ledger))


def _bounded_patch_operations_fingerprint(operations: list[dict[str, Any]]) -> str:
    canonical = json.dumps(operations, sort_keys=True, separators=(",", ":"))
    return _sha256_text(canonical)


def _bounded_patch_dedupe_key(args: Mapping[str, Any], operations: list[dict[str, Any]]) -> tuple[str, str, bool]:
    explicit = str(args.get("idempotency_key") or "").strip()
    if explicit:
        return f"idempotency_key:{_normalize_idempotency_token(explicit)}", "idempotency_key", False
    client_request_id = str(args.get("client_request_id") or "").strip()
    if client_request_id:
        return f"client_request_id:{_normalize_idempotency_token(client_request_id)}", "client_request_id", False
    return f"patch_sha256:{_bounded_patch_operations_fingerprint(operations)}", "patch_sha256", True


def _bounded_patch_existing_apply(root: Path, dedupe_key: str) -> dict[str, Any] | None:
    ledger = _load_bounded_patch_apply_idempotency_ledger(root)
    entries = ledger.get("entries") if isinstance(ledger.get("entries"), Mapping) else {}
    entry = entries.get(dedupe_key)
    if isinstance(entry, Mapping):
        receipt_path = root / str(entry.get("receipt_path") or "")
        if receipt_path.exists():
            return dict(entry)
    return None


def _record_bounded_patch_apply_idempotency(
    root: Path,
    dedupe_key: str,
    *,
    source: str,
    implicit: bool,
    receipt_path: Path,
    operations_sha256: str,
    touched_paths: list[str],
    edit_lease: Mapping[str, Any] | None = None,
) -> None:
    ledger = _load_bounded_patch_apply_idempotency_ledger(root)
    entries = dict(ledger.get("entries") if isinstance(ledger.get("entries"), Mapping) else {})
    entries[dedupe_key] = {
        "recorded_at": _now(),
        "source": source,
        "implicit": implicit,
        "receipt_path": receipt_path.relative_to(root).as_posix(),
        "operations_sha256": operations_sha256,
        "touched_paths": touched_paths,
        "production_authority": False,
        "live_execution_authority": False,
    }
    if edit_lease:
        entries[dedupe_key]["edit_lease"] = dict(edit_lease)
    ledger["entries"] = entries
    ledger["updated_at"] = _now()
    _save_bounded_patch_apply_idempotency_ledger(root, ledger)


def _bounded_patch_replay_result(
    root: Path,
    existing: Mapping[str, Any],
    dedupe_key: str,
    source: str,
    *,
    edit_lease: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return _ok(
        "ion_bounded_patch_apply",
        {
            "schema_id": "ion.chatgpt_browser_connector_bounded_patch_apply_result.v1",
            "idempotent_replay": True,
            "duplicate_prevented": True,
            "dedupe_key": dedupe_key,
            "idempotency_source": source,
            "receipt_path": existing.get("receipt_path"),
            "operations_sha256": existing.get("operations_sha256"),
            "touched_paths": list(existing.get("touched_paths") or []),
            "edit_lease": dict(edit_lease or existing.get("edit_lease") or {}),
            "production_authority": False,
            "live_execution_authority": False,
        },
        mutates_active_state=False,
    )


def _file_put_text_diff(target_rel: str, text: str) -> str:
    return "".join(
        difflib.unified_diff(
            [],
            text.splitlines(keepends=True),
            fromfile="/dev/null",
            tofile=f"b/{target_rel}",
        )
    )


def _file_put_text_dedupe_key(args: Mapping[str, Any], target_rel: str, payload_sha256: str) -> tuple[str, str, bool]:
    explicit = str(args.get("idempotency_key") or "").strip()
    if explicit:
        return f"idempotency_key:{_normalize_idempotency_token(explicit)}", "idempotency_key", False
    client_request_id = str(args.get("client_request_id") or "").strip()
    if client_request_id:
        return f"client_request_id:{_normalize_idempotency_token(client_request_id)}", "client_request_id", False
    implicit_seed = f"{target_rel}:{payload_sha256}"
    return f"target_sha256:{_sha256_text(implicit_seed)}", "target_sha256", True


def _load_file_put_text_idempotency_ledger(root: Path) -> dict[str, Any]:
    path = root / FILE_PUT_TEXT_IDEMPOTENCY_LEDGER_RELATIVE_PATH
    payload = _read_json(path)
    if isinstance(payload, dict):
        payload.setdefault("schema_id", "ion.chatgpt_browser_connector_file_put_text_idempotency_ledger.v1")
        payload.setdefault("entries", {})
        return payload
    return {
        "schema_id": "ion.chatgpt_browser_connector_file_put_text_idempotency_ledger.v1",
        "created_at": _now(),
        "updated_at": _now(),
        "entries": {},
        "production_authority": False,
        "live_execution_authority": False,
    }


def _save_file_put_text_idempotency_ledger(root: Path, ledger: Mapping[str, Any]) -> None:
    _write_json(root / FILE_PUT_TEXT_IDEMPOTENCY_LEDGER_RELATIVE_PATH, dict(ledger))


def _file_put_text_existing_entry(root: Path, dedupe_key: str) -> dict[str, Any] | None:
    ledger = _load_file_put_text_idempotency_ledger(root)
    entries = ledger.get("entries") if isinstance(ledger.get("entries"), Mapping) else {}
    entry = entries.get(dedupe_key)
    if isinstance(entry, Mapping):
        target_rel = str(entry.get("target_path") or "")
        target = root / target_rel
        target_sha = str(entry.get("sha256") or "")
        if target_rel and target.exists() and target.is_file() and target_sha and _sha256_file(target) == target_sha:
            return dict(entry)
    return None


def _record_file_put_text_idempotency(
    root: Path,
    dedupe_key: str,
    *,
    source: str,
    implicit: bool,
    target_path: str,
    sha256: str,
    receipt_path: str,
    mutation_lease: Mapping[str, Any] | None = None,
) -> None:
    ledger = _load_file_put_text_idempotency_ledger(root)
    entries = dict(ledger.get("entries") if isinstance(ledger.get("entries"), Mapping) else {})
    entries[dedupe_key] = {
        "recorded_at": _now(),
        "source": source,
        "implicit": implicit,
        "target_path": target_path,
        "sha256": sha256,
        "receipt_path": receipt_path,
        "production_authority": False,
        "live_execution_authority": False,
    }
    if mutation_lease:
        entries[dedupe_key]["mutation_lease"] = dict(mutation_lease)
    ledger["entries"] = entries
    ledger["updated_at"] = _now()
    _save_file_put_text_idempotency_ledger(root, ledger)


def _file_put_text_replay_result(
    existing: Mapping[str, Any],
    *,
    dedupe_key: str,
    source: str,
    mutation_lease: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return _ok(
        "ion_file_put_text",
        {
            "target_path": existing.get("target_path"),
            "sha256": existing.get("sha256"),
            "receipt_path": existing.get("receipt_path"),
            "idempotent_replay": True,
            "duplicate_prevented": True,
            "dedupe_key": dedupe_key,
            "idempotency_source": source,
            "mutation_lease": dict(mutation_lease or existing.get("mutation_lease") or {}),
            "production_authority": False,
            "live_execution_authority": False,
        },
        mutates_active_state=False,
    )


def _validate_bounded_patch_target(root: Path, value: str) -> tuple[Path | None, str | None]:
    if not value or value.startswith("/") or ".." in Path(value).parts:
        return None, "target_path_must_be_repo_relative"
    rel = Path(value)
    rel_posix = rel.as_posix()
    if rel_posix in PROTECTED_SHARED_CONTEXT_RELATIVE_PATHS:
        return None, "protected_shared_context_path_requires_settlement"
    if rel.name in {"CAPSULE.md", "MINI.md", "HOT_CONTEXT.md", "STATUS.json", "ROUTE.json"} and rel_posix.startswith("ION/05_context/current/codex_solo/"):
        return None, "protected_shared_context_path_requires_settlement"
    lower_parts = {part.lower() for part in rel.parts}
    if lower_parts & FORBIDDEN_TRANSFER_PATH_PARTS:
        return None, "target_path_contains_forbidden_secret_word"
    try:
        target = _safe_rel_path(root, rel_posix)
    except ValueError:
        return None, "target_path_must_be_repo_relative"
    allowed = any(_is_under(target, resolve_ion_path(root, allowed_root)) for allowed_root in BOUNDED_PATCH_ALLOWED_ROOTS)
    if not allowed:
        return None, "target_path_not_in_bounded_patch_roots"
    if target.is_dir():
        return None, "target_path_is_directory"
    return target, None


def _normalize_bounded_patch_operations(args: Mapping[str, Any]) -> tuple[list[dict[str, Any]], str | None]:
    raw = args.get("operations")
    if raw is None:
        raw = [{
            "path": args.get("path") or args.get("target_path"),
            "old_text": args.get("old_text"),
            "new_text": args.get("new_text"),
            "expected_sha256": args.get("expected_sha256"),
        }]
    if not isinstance(raw, list):
        return [], "operations_must_be_list"
    operations: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            return [], "operation_must_be_object"
        path = str(item.get("path") or item.get("target_path") or "").strip()
        old_text = item.get("old_text")
        new_text = item.get("new_text")
        expected_sha = str(item.get("expected_sha256") or "").strip() or None
        if not path:
            return [], "operation_path_required"
        if not isinstance(old_text, str) or not isinstance(new_text, str):
            return [], "operation_old_text_and_new_text_required"
        operations.append({
            "path": path,
            "old_text": old_text,
            "new_text": new_text,
            "expected_sha256": expected_sha,
        })
    if not operations:
        return [], "operations_required"
    paths = [op["path"] for op in operations]
    if len(paths) != len(set(paths)):
        return [], "duplicate_patch_operation_path_not_supported"
    return operations, None


def _bounded_patch_preview(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    operations, finding = _normalize_bounded_patch_operations(args)
    if finding:
        return _blocked("ion_bounded_patch_preview", finding)
    if len(operations) > 25:
        return _blocked("ion_bounded_patch_preview", "too_many_patch_operations")
    previews: list[dict[str, Any]] = []
    touched_paths: list[str] = []
    for op in operations:
        target, target_finding = _validate_bounded_patch_target(root, op["path"])
        if target_finding or target is None:
            return _blocked("ion_bounded_patch_preview", target_finding or "invalid_patch_target", {"path": op["path"]})
        rel = target.relative_to(root).as_posix()
        if not target.exists():
            return _blocked("ion_bounded_patch_preview", "target_path_missing", {"path": rel})
        original = target.read_text(encoding="utf-8", errors="replace")
        original_sha = _sha256_text(original)
        expected_sha = op.get("expected_sha256")
        if expected_sha and expected_sha != original_sha:
            return _blocked("ion_bounded_patch_preview", "expected_sha256_mismatch", {"path": rel, "expected_sha256": expected_sha, "actual_sha256": original_sha})
        occurrences = original.count(op["old_text"])
        if occurrences != 1:
            return _blocked("ion_bounded_patch_preview", "old_text_must_match_exactly_once", {"path": rel, "occurrences": occurrences})
        updated = original.replace(op["old_text"], op["new_text"], 1)
        updated_sha = _sha256_text(updated)
        diff = "".join(difflib.unified_diff(
            original.splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile=f"a/{rel}",
            tofile=f"b/{rel}",
        ))
        previews.append({
            "path": rel,
            "original_sha256": original_sha,
            "updated_sha256": updated_sha,
            "old_text_sha256": _sha256_text(op["old_text"]),
            "new_text_sha256": _sha256_text(op["new_text"]),
            "diff": diff,
            "diff_bytes": len(diff.encode("utf-8")),
        })
        touched_paths.append(rel)
    return _ok(
        "ion_bounded_patch_preview",
        {
            "schema_id": "ion.chatgpt_browser_connector_bounded_patch_preview.v1",
            "operation_count": len(operations),
            "touched_paths": touched_paths,
            "operations_sha256": _bounded_patch_operations_fingerprint(operations),
            "previews": previews,
            "production_authority": False,
            "live_execution_authority": False,
        },
        mutates_active_state=False,
    )


def _require_connector_mutation_lease(
    root: Path,
    *,
    tool_name: str,
    args: Mapping[str, Any],
    target_paths: Iterable[str],
    required_mode: str = "exclusive_write",
    lease_label: str = "edit_lease",
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    target_files = [str(path or "").strip() for path in target_paths if str(path or "").strip()]
    gate = require_active_edit_lease(
        root,
        agent_id=str(args.get("agent_id") or "").strip(),
        lease_id=str(args.get("lease_id") or "").strip(),
        target_files=target_files,
        required_mode=required_mode,
    )
    proof = {
        "schema_id": "ion.chatgpt_browser_connector.worker_shift_mutation_lease_gate.v0_1",
        "ok": bool(gate.get("ok")),
        "tool": tool_name,
        "lease_label": lease_label,
        "required_lease_type": required_mode,
        "required_fields": ["agent_id", "lease_id"],
        "agent_id": str(args.get("agent_id") or "").strip(),
        "lease_id": str(args.get("lease_id") or "").strip(),
        "target_files": target_files,
        "worker_shift_gate": gate,
        "authority": {
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    }
    if proof["ok"]:
        return proof, None
    finding = str(gate.get("finding") or f"{lease_label}_required")
    blocked_payload = {
        "mutation_lease": proof,
        lease_label: proof,
        "target_files": target_files,
    }
    if lease_label != "edit_lease":
        blocked_payload["edit_lease"] = proof
    return proof, _blocked(
        tool_name,
        finding,
        blocked_payload,
    )


def _bounded_patch_apply(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    if str(args.get("confirmation") or "") != "ION_BOUNDED_WRITE_CONFIRMED":
        return _blocked("ion_bounded_patch_apply", "confirmation_required")
    operations, finding = _normalize_bounded_patch_operations(args)
    if finding:
        return _blocked("ion_bounded_patch_apply", finding)
    target_paths: list[str] = []
    for op in operations:
        target, target_finding = _validate_bounded_patch_target(root, op["path"])
        if target_finding or target is None:
            return _blocked(
                "ion_bounded_patch_apply",
                target_finding or "invalid_patch_target",
                {"path": op["path"]},
            )
        target_paths.append(target.relative_to(root).as_posix())
    edit_lease, lease_blocked = _require_connector_mutation_lease(
        root,
        tool_name="ion_bounded_patch_apply",
        args=args,
        target_paths=target_paths,
        required_mode="exclusive_write",
        lease_label="edit_lease",
    )
    if lease_blocked:
        return lease_blocked
    dedupe_key, dedupe_source, implicit = _bounded_patch_dedupe_key(args, operations)
    if args.get("force_new") is not True:
        existing = _bounded_patch_existing_apply(root, dedupe_key)
        if existing:
            return _bounded_patch_replay_result(root, existing, dedupe_key, dedupe_source, edit_lease=edit_lease)
    preview = _bounded_patch_preview(root, {"operations": operations})
    if not preview.get("ok"):
        blocked = dict(preview)
        blocked["tool"] = "ion_bounded_patch_apply"
        return blocked
    previews = list(preview["data"]["previews"])
    updated_text_by_path: dict[str, str] = {}
    for op, item in zip(operations, previews):
        target = _safe_rel_path(root, item["path"])
        original = target.read_text(encoding="utf-8", errors="replace")
        updated_text_by_path[item["path"]] = original.replace(op["old_text"], op["new_text"], 1)
    for rel, updated in updated_text_by_path.items():
        target = _safe_rel_path(root, rel)
        target.write_text(updated, encoding="utf-8")
    touched_paths = list(preview["data"]["touched_paths"])
    receipt = _write_connector_packet(root, "patch_receipts", "bounded_patch_apply", {
        "schema_id": "ion.chatgpt_browser_connector_bounded_patch_receipt.v1",
        "action": "ion_bounded_patch_apply",
        "status": "CANDIDATE_PATCH_APPLIED",
        "touched_paths": touched_paths,
        "operations_sha256": preview["data"]["operations_sha256"],
        "preview": previews,
        "dedupe_key": dedupe_key,
        "idempotency_source": dedupe_source,
        "implicit_idempotency_key": implicit,
        "edit_lease": edit_lease,
        "production_authority": False,
        "live_execution_authority": False,
        "settlement_required": True,
    })
    _record_bounded_patch_apply_idempotency(
        root,
        dedupe_key,
        source=dedupe_source,
        implicit=implicit,
        receipt_path=receipt,
        operations_sha256=preview["data"]["operations_sha256"],
        touched_paths=touched_paths,
        edit_lease=edit_lease,
    )
    return _ok(
        "ion_bounded_patch_apply",
        {
            "schema_id": "ion.chatgpt_browser_connector_bounded_patch_apply_result.v1",
            "status": "CANDIDATE_PATCH_APPLIED",
            "receipt_path": receipt.relative_to(root).as_posix(),
            "touched_paths": touched_paths,
            "operations_sha256": preview["data"]["operations_sha256"],
            "idempotent_replay": False,
            "duplicate_prevented": False,
            "dedupe_key": dedupe_key,
            "idempotency_source": dedupe_source,
            "implicit_idempotency_key": implicit,
            "edit_lease": edit_lease,
            "production_authority": False,
            "live_execution_authority": False,
            "settlement_required": True,
        },
        mutates_active_state=True,
    )



def _artifact_receipt(root: Path, prefix: str, payload: Mapping[str, Any]) -> Path:
    return _write_connector_packet(root, "artifact_receipts", prefix, payload)


def _put_text_artifact(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    target_path = str(args.get("target_path") or "")
    target, finding = _validate_transfer_target(root, target_path)
    if finding or target is None:
        return _blocked("ion_file_put_text", finding or "invalid_target_path")
    target_rel = _connector_rel(target, root)
    text = str(args.get("text") or "")
    data = text.encode("utf-8")
    if len(data) > MAX_TEXT_PUT_BYTES:
        return _blocked("ion_file_put_text", "text_payload_exceeds_connector_limit")
    expected_sha = str(args.get("expected_sha256") or "").strip()
    actual_sha = _sha256_bytes(data)
    if expected_sha and expected_sha != actual_sha:
        return _blocked("ion_file_put_text", "sha256_mismatch", {"expected_sha256": expected_sha, "actual_sha256": actual_sha})
    preview_only = bool(args.get("preview_only"))
    requires_confirmation = True
    if requires_confirmation and not preview_only:
        if str(args.get("confirmation") or "") != "ION_BOUNDED_WRITE_CONFIRMED":
            return _blocked("ion_file_put_text", "confirmation_required")
    mutation_lease: dict[str, Any] = {}
    if requires_confirmation and not preview_only:
        mutation_lease, lease_blocked = _require_connector_mutation_lease(
            root,
            tool_name="ion_file_put_text",
            args=args,
            target_paths=[target_rel],
            required_mode="artifact",
            lease_label="artifact_lease",
        )
        if lease_blocked:
            return lease_blocked
    diff = _file_put_text_diff(target_rel, text)
    if preview_only:
        if target.exists():
            return _blocked(
                "ion_file_put_text",
                "target_exists_requires_lifecycle_receipt",
                {
                    "target_path": target_rel,
                    "target_sha256": _sha256_file(target) if target.is_file() else None,
                },
            )
        return _ok(
            "ion_file_put_text",
            {
                "schema_id": "ion.chatgpt_browser_connector_file_put_text_preview.v1",
                "preview_only": True,
                "target_path": target_rel,
                "bytes": len(data),
                "sha256": actual_sha,
                "unified_diff": diff,
                "diff_bytes": len(diff.encode("utf-8")),
                "overwrite": False,
                "confirmation_required": requires_confirmation,
                "confirmation_token": "ION_BOUNDED_WRITE_CONFIRMED" if requires_confirmation else None,
                "artifact_lease_required": True,
                "production_authority": False,
                "live_execution_authority": False,
            },
            mutates_active_state=False,
        )
    dedupe_key, dedupe_source, implicit = _file_put_text_dedupe_key(args, target_rel, actual_sha)
    if args.get("force_new") is not True:
        existing = _file_put_text_existing_entry(root, dedupe_key)
        if existing:
            return _file_put_text_replay_result(
                existing,
                dedupe_key=dedupe_key,
                source=dedupe_source,
                mutation_lease=mutation_lease,
            )
    if target.exists():
        receipt = _artifact_receipt(root, target.name, {
            "schema_id": "ion.chatgpt_browser_connector_artifact_receipt.v1",
            "action": "ion_file_put_text_blocked_existing_target",
            "target_path": target_rel,
            "target_sha256": _sha256_file(target) if target.is_file() else None,
            "overwrite_requested": bool(args.get("overwrite")),
            "status": "BLOCKED_NO_SILENT_LOSS_REQUIRES_LIFECYCLE_RECEIPT",
        })
        return _blocked("ion_file_put_text", "target_exists_requires_lifecycle_receipt", {"receipt_path": _connector_rel(receipt, root)})
    target_authority = authorize_artifact_path(
        target,
        purpose=PURPOSE_MCP_CONNECTOR_CONTRACT,
        active_root=root,
        base_root="active_repo",
    )
    if not target_authority["authorized"]:
        return _blocked("ion_file_put_text", f"path_authority_{target_authority['reason_code']}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    receipt = _artifact_receipt(root, target.name, {
        "schema_id": "ion.chatgpt_browser_connector_artifact_receipt.v1",
        "action": "ion_file_put_text",
        "target_path": target_rel,
        "bytes": len(data),
        "sha256": actual_sha,
        "unified_diff": diff,
        "diff_bytes": len(diff.encode("utf-8")),
        "dedupe_key": dedupe_key,
        "idempotency_source": dedupe_source,
        "implicit_idempotency_key": implicit,
        "mutation_lease": mutation_lease,
        "git_status_summary": _git_status_summary(root),
        "path_authority": target_authority,
        "status": "ARTIFACT_WRITTEN",
    })
    receipt_rel = _connector_rel(receipt, root)
    _record_file_put_text_idempotency(
        root,
        dedupe_key,
        source=dedupe_source,
        implicit=implicit,
        target_path=target_rel,
        sha256=actual_sha,
        receipt_path=receipt_rel,
        mutation_lease=mutation_lease,
    )
    return _ok("ion_file_put_text", {
        "target_path": target_rel,
        "bytes": len(data),
        "sha256": actual_sha,
        "receipt_path": receipt_rel,
        "unified_diff": diff,
        "diff_bytes": len(diff.encode("utf-8")),
        "git_status_summary": _git_status_summary(root),
        "idempotent_replay": False,
        "duplicate_prevented": False,
        "dedupe_key": dedupe_key,
        "idempotency_source": dedupe_source,
        "implicit_idempotency_key": implicit,
        "mutation_lease": mutation_lease,
    }, mutates_active_state=True)


def _upload_session_path(root: Path, upload_id: str) -> Path:
    if not re.fullmatch(r"upload_[0-9TZ-]+_[a-z0-9_]+", upload_id):
        raise ValueError("invalid_upload_id")
    return root / CONNECTOR_STATE_DIR / "artifact_uploads" / f"{upload_id}.json"


def _artifact_upload_init(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    artifact_name = str(args.get("artifact_name") or "").strip()
    if not artifact_name:
        return _blocked("ion_artifact_upload_init", "artifact_name_required")
    target_path = str(args.get("target_path") or (ARTIFACT_TARGET_ROOTS[0] / artifact_name).as_posix())
    target, finding = _validate_transfer_target(root, target_path)
    if finding or target is None:
        return _blocked("ion_artifact_upload_init", finding or "invalid_target_path")
    if str(args.get("confirmation") or "") != "ION_BOUNDED_WRITE_CONFIRMED":
        return _blocked("ion_artifact_upload_init", "confirmation_required")
    mutation_lease, lease_blocked = _require_connector_mutation_lease(
        root,
        tool_name="ion_artifact_upload_init",
        args=args,
        target_paths=[_connector_rel(target, root)],
        required_mode="artifact",
        lease_label="artifact_lease",
    )
    if lease_blocked:
        return lease_blocked
    if target.exists():
        return _blocked("ion_artifact_upload_init", "target_exists_requires_lifecycle_receipt")
    total_bytes = args.get("total_bytes")
    if total_bytes is not None and int(total_bytes) > MAX_UPLOAD_BYTES:
        return _blocked("ion_artifact_upload_init", "declared_upload_exceeds_connector_limit")
    now = _now()
    upload_id = f"upload_{now.replace(':', '').replace('+', 'Z')}_{_safe_slug(artifact_name)}"
    session = {
        "schema_id": "ion.chatgpt_browser_connector_artifact_upload_session.v1",
        "upload_id": upload_id,
        "artifact_name": artifact_name,
        "target_path": _connector_rel(target, root),
        "expected_sha256": str(args.get("expected_sha256") or "").strip() or None,
        "total_bytes": total_bytes,
        "mime_type": str(args.get("mime_type") or "application/octet-stream"),
        "status": "OPEN",
        "created_at": now,
        "updated_at": now,
        "chunks": {},
        "mutation_lease": mutation_lease,
        "production_authority": False,
        "live_execution_authority": False,
    }
    session["path_authority"] = authorize_artifact_path(
        target,
        purpose=PURPOSE_MCP_CONNECTOR_CONTRACT,
        active_root=root,
        base_root="active_repo",
    )
    path = _upload_session_path(root, upload_id)
    _require_connector_artifact_path(root, path)
    _write_json(path, session)
    return _ok("ion_artifact_upload_init", {
        "upload_id": upload_id,
        "session_path": _connector_rel(path, root),
        "target_path": _connector_rel(target, root),
        "max_chunk_bytes": MAX_UPLOAD_CHUNK_BYTES,
        "max_upload_bytes": MAX_UPLOAD_BYTES,
        "mutation_lease": mutation_lease,
    }, mutates_active_state=True)


def _load_upload_session(root: Path, upload_id: str) -> tuple[Path | None, dict[str, Any] | None, str | None]:
    try:
        path = _upload_session_path(root, upload_id)
    except ValueError:
        return None, None, "invalid_upload_id"
    if not path.exists():
        return None, None, "upload_session_missing"
    return path, _load_json_file(path), None


def _artifact_upload_chunk(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    upload_id = str(args.get("upload_id") or "").strip()
    path, session, finding = _load_upload_session(root, upload_id)
    if finding or path is None or session is None:
        return _blocked("ion_artifact_upload_chunk", finding or "upload_session_missing")
    if session.get("status") != "OPEN":
        return _blocked("ion_artifact_upload_chunk", "upload_session_not_open")
    if str(args.get("confirmation") or "") != "ION_BOUNDED_WRITE_CONFIRMED":
        return _blocked("ion_artifact_upload_chunk", "confirmation_required")
    mutation_lease, lease_blocked = _require_connector_mutation_lease(
        root,
        tool_name="ion_artifact_upload_chunk",
        args=args,
        target_paths=[str(session.get("target_path") or "")],
        required_mode="artifact",
        lease_label="artifact_lease",
    )
    if lease_blocked:
        return lease_blocked
    chunk_index = int(args.get("chunk_index"))
    if chunk_index < 0:
        return _blocked("ion_artifact_upload_chunk", "chunk_index_must_be_non_negative")
    try:
        data = base64.b64decode(str(args.get("data_base64") or ""), validate=True)
    except (binascii.Error, ValueError):
        return _blocked("ion_artifact_upload_chunk", "invalid_base64_chunk")
    if len(data) > MAX_UPLOAD_CHUNK_BYTES:
        return _blocked("ion_artifact_upload_chunk", "chunk_exceeds_connector_limit")
    expected = str(args.get("chunk_sha256") or "").strip()
    actual = _sha256_bytes(data)
    if expected and expected != actual:
        return _blocked("ion_artifact_upload_chunk", "chunk_sha256_mismatch", {"expected_sha256": expected, "actual_sha256": actual})
    chunk_dir = root / CONNECTOR_STATE_DIR / "artifact_uploads" / "chunks"
    _require_connector_artifact_path(root, chunk_dir)
    chunk_dir.mkdir(parents=True, exist_ok=True)
    chunk_path = chunk_dir / f"{upload_id}_{chunk_index:08d}.chunk"
    _require_connector_artifact_path(root, chunk_path)
    if chunk_path.exists():
        return _blocked("ion_artifact_upload_chunk", "chunk_index_already_received")
    chunk_path.write_bytes(data)
    chunks = dict(session.get("chunks") or {})
    chunks[str(chunk_index)] = {"path": _connector_rel(chunk_path, root), "bytes": len(data), "sha256": actual}
    session["chunks"] = chunks
    session["updated_at"] = _now()
    session["latest_chunk_mutation_lease"] = mutation_lease
    _require_connector_artifact_path(root, path)
    _write_json(path, session)
    return _ok("ion_artifact_upload_chunk", {
        "upload_id": upload_id,
        "chunk_index": chunk_index,
        "bytes": len(data),
        "sha256": actual,
        "mutation_lease": mutation_lease,
    }, mutates_active_state=True)


def _artifact_upload_commit(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    upload_id = str(args.get("upload_id") or "").strip()
    path, session, finding = _load_upload_session(root, upload_id)
    if finding or path is None or session is None:
        return _blocked("ion_artifact_upload_commit", finding or "upload_session_missing")
    if session.get("status") != "OPEN":
        return _blocked("ion_artifact_upload_commit", "upload_session_not_open")
    target, target_finding = _validate_transfer_target(root, str(session.get("target_path") or ""))
    if target_finding or target is None:
        return _blocked("ion_artifact_upload_commit", target_finding or "invalid_target_path")
    if str(args.get("confirmation") or "") != "ION_BOUNDED_WRITE_CONFIRMED":
        return _blocked("ion_artifact_upload_commit", "confirmation_required")
    mutation_lease, lease_blocked = _require_connector_mutation_lease(
        root,
        tool_name="ion_artifact_upload_commit",
        args=args,
        target_paths=[_connector_rel(target, root)],
        required_mode="artifact",
        lease_label="artifact_lease",
    )
    if lease_blocked:
        return lease_blocked
    if target.exists():
        receipt = _artifact_receipt(root, target.name, {
            "schema_id": "ion.chatgpt_browser_connector_artifact_receipt.v1",
            "action": "ion_artifact_upload_commit_blocked_existing_target",
            "upload_id": upload_id,
            "target_path": _connector_rel(target, root),
            "target_sha256": _sha256_file(target) if target.is_file() else None,
            "status": "BLOCKED_NO_SILENT_LOSS_REQUIRES_LIFECYCLE_RECEIPT",
        })
        return _blocked("ion_artifact_upload_commit", "target_exists_requires_lifecycle_receipt", {"receipt_path": _connector_rel(receipt, root)})
    chunks = session.get("chunks") or {}
    if not chunks:
        return _blocked("ion_artifact_upload_commit", "no_chunks_received")
    ordered_indices = sorted(int(index) for index in chunks)
    if ordered_indices != list(range(0, max(ordered_indices) + 1)):
        return _blocked("ion_artifact_upload_commit", "missing_chunk_index")
    assembled = bytearray()
    for index in ordered_indices:
        chunk_meta = chunks[str(index)]
        chunk_path = _safe_rel_path(root, str(chunk_meta.get("path") or ""))
        data = chunk_path.read_bytes()
        if _sha256_bytes(data) != chunk_meta.get("sha256"):
            return _blocked("ion_artifact_upload_commit", "stored_chunk_sha256_mismatch", {"chunk_index": index})
        assembled.extend(data)
        if len(assembled) > MAX_UPLOAD_BYTES:
            return _blocked("ion_artifact_upload_commit", "assembled_upload_exceeds_connector_limit")
    data = bytes(assembled)
    actual_sha = _sha256_bytes(data)
    expected_sha = str(session.get("expected_sha256") or "").strip()
    if expected_sha and expected_sha != actual_sha:
        return _blocked("ion_artifact_upload_commit", "sha256_mismatch", {"expected_sha256": expected_sha, "actual_sha256": actual_sha})
    declared_total = session.get("total_bytes")
    if declared_total is not None and int(declared_total) != len(data):
        return _blocked("ion_artifact_upload_commit", "declared_total_bytes_mismatch", {"declared": declared_total, "actual": len(data)})
    target_authority = authorize_artifact_path(
        target,
        purpose=PURPOSE_MCP_CONNECTOR_CONTRACT,
        active_root=root,
        base_root="active_repo",
    )
    if not target_authority["authorized"]:
        return _blocked("ion_artifact_upload_commit", f"path_authority_{target_authority['reason_code']}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    session["status"] = "COMMITTED"
    session["committed_at"] = _now()
    session["target_sha256"] = actual_sha
    session["target_bytes"] = len(data)
    session["commit_mutation_lease"] = mutation_lease
    _require_connector_artifact_path(root, path)
    _write_json(path, session)
    receipt = _artifact_receipt(root, target.name, {
        "schema_id": "ion.chatgpt_browser_connector_artifact_receipt.v1",
        "action": "ion_artifact_upload_commit",
        "upload_id": upload_id,
        "target_path": _connector_rel(target, root),
        "bytes": len(data),
        "sha256": actual_sha,
        "chunk_count": len(ordered_indices),
        "path_authority": target_authority,
        "mutation_lease": mutation_lease,
        "status": "ARTIFACT_COMMITTED",
    })
    return _ok("ion_artifact_upload_commit", {
        "upload_id": upload_id,
        "target_path": _connector_rel(target, root),
        "bytes": len(data),
        "sha256": actual_sha,
        "receipt_path": _connector_rel(receipt, root),
        "mutation_lease": mutation_lease,
    }, mutates_active_state=True)


def _carrier_message_queue(root: Path) -> dict[str, Any]:
    path = root / ACTIVE_CARRIER_MESSAGE_QUEUE_RELATIVE_PATH
    return _read_json(path) or {
        "schema_id": "ion.carrier_message_queue.v1",
        "created_at": _now(),
        "updated_at": _now(),
        "messages": [],
        "production_authority": False,
        "live_execution_authority": False,
    }


def _write_carrier_message_queue(root: Path, queue: Mapping[str, Any]) -> None:
    value = dict(queue)
    value["updated_at"] = _now()
    _write_json(root / ACTIVE_CARRIER_MESSAGE_QUEUE_RELATIVE_PATH, value)


def _carrier_message_send(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    sender = str(args.get("sender_carrier_id") or args.get("from_carrier") or "").strip()
    recipient = str(args.get("recipient") or args.get("to") or "").strip()
    body = str(args.get("body") or args.get("message") or "").strip()
    if not sender or not recipient or not body:
        return _blocked("ion_carrier_message_send", "sender_recipient_body_required")
    now = _now()
    message_id = f"carmsg_{now.replace(':', '').replace('+', 'Z')}_{_safe_slug(sender)}_to_{_safe_slug(recipient)}"
    message = {
        "schema_id": "ion.carrier_message.v1",
        "message_id": message_id,
        "created_at": now,
        "updated_at": now,
        "sender_carrier_id": sender,
        "recipient": recipient,
        "channel": str(args.get("channel") or "default"),
        "message_type": str(args.get("message_type") or "carrier_message"),
        "body": body,
        "context_refs": list(args.get("context_refs") or []),
        "receipt_refs": list(args.get("receipt_refs") or []),
        "status": "pending",
        "acked_by": [],
        "production_authority": False,
        "live_execution_authority": False,
    }
    packet_path = _write_connector_packet(root, "carrier_messages", message_id, message)
    message["packet_path"] = _connector_rel(packet_path, root)
    _write_json(packet_path, message)
    queue = _carrier_message_queue(root)
    queue.setdefault("messages", []).append(message)
    _write_carrier_message_queue(root, queue)
    return _ok("ion_carrier_message_send", {
        "message_id": message_id,
        "queue_path": ACTIVE_CARRIER_MESSAGE_QUEUE_RELATIVE_PATH.as_posix(),
        "packet_path": _connector_rel(packet_path, root),
    }, mutates_active_state=True)


def _carrier_message_poll(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    recipient = str(args.get("recipient") or "").strip()
    channel = str(args.get("channel") or "").strip()
    include_acked = bool(args.get("include_acked"))
    limit = int(args.get("limit") or 25)
    queue = _carrier_message_queue(root)
    messages = list(queue.get("messages") or [])
    filtered: list[dict[str, Any]] = []
    for item in messages:
        if recipient and item.get("recipient") not in {recipient, "*", "broadcast"}:
            continue
        if channel and item.get("channel") != channel:
            continue
        if not include_acked and item.get("status") == "acked":
            continue
        filtered.append(item)
        if len(filtered) >= limit:
            break
    return _ok("ion_carrier_message_poll", {
        "queue_path": ACTIVE_CARRIER_MESSAGE_QUEUE_RELATIVE_PATH.as_posix(),
        "message_count": len(filtered),
        "messages": filtered,
    })


def _carrier_message_ack(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    message_id = str(args.get("message_id") or "").strip()
    ack_by = str(args.get("ack_by_carrier") or args.get("ack_by") or "").strip()
    if not message_id or not ack_by:
        return _blocked("ion_carrier_message_ack", "message_id_and_ack_by_required")
    queue = _carrier_message_queue(root)
    messages = list(queue.get("messages") or [])
    for item in messages:
        if item.get("message_id") != message_id:
            continue
        ack = {"ack_by_carrier": ack_by, "acked_at": _now()}
        acked_by = list(item.get("acked_by") or [])
        acked_by.append(ack)
        item["acked_by"] = acked_by
        item["status"] = "acked"
        item["updated_at"] = _now()
        _write_carrier_message_queue(root, queue)
        packet_path = _write_connector_packet(root, "carrier_message_acks", message_id, {
            "schema_id": "ion.carrier_message_ack.v1",
            "message_id": message_id,
            "ack": ack,
            "queue_path": ACTIVE_CARRIER_MESSAGE_QUEUE_RELATIVE_PATH.as_posix(),
        })
        return _ok("ion_carrier_message_ack", {
            "message_id": message_id,
            "status": "acked",
            "ack_packet_path": _connector_rel(packet_path, root),
        }, mutates_active_state=True)
    return _blocked("ion_carrier_message_ack", "message_id_not_found")


def _preview_text(value: Any, *, limit: int = 280) -> str:
    text = str(value or "").replace("\r\n", "\n").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def _bounded_preview_bytes(value: Any, *, default: int = DEFAULT_COMPACT_PREVIEW_BYTES) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return min(max(parsed, 1), MAX_COMPACT_PREVIEW_BYTES)


def _bounded_positive_int(value: Any, *, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return min(max(parsed, minimum), maximum)


def _status_filter_values(value: Any) -> set[str]:
    if isinstance(value, list):
        raw_values = [str(item or "").strip() for item in value]
    else:
        raw = str(value or "").strip()
        raw_values = [part.strip() for part in raw.split(",")] if raw else []
    return {item.lower() for item in raw_values if item}


def _paginate_by_cursor(
    rows: list[dict[str, Any]],
    *,
    cursor: str | None,
    limit: int,
    cursor_keys: tuple[str, ...],
) -> dict[str, Any]:
    start_index = 0
    cursor_found = True
    cursor_value = str(cursor or "").strip()
    if cursor_value:
        cursor_found = False
        for idx, row in enumerate(rows):
            for key in cursor_keys:
                if str(row.get(key) or "") == cursor_value:
                    start_index = idx + 1
                    cursor_found = True
                    break
            if cursor_found:
                break
    page = rows[start_index:start_index + limit]
    has_more = (start_index + len(page)) < len(rows)
    next_cursor = None
    if has_more and page:
        last = page[-1]
        for key in cursor_keys:
            candidate = str(last.get(key) or "").strip()
            if candidate:
                next_cursor = candidate
                break
    return {
        "rows": page,
        "cursor": cursor_value or None,
        "cursor_found": cursor_found,
        "next_cursor": next_cursor,
        "has_more": has_more,
    }


def _compact_ai_movement_warning_map(
    warning_map: Mapping[str, Any],
    *,
    include_rows: bool = False,
    row_limit: int = DEFAULT_COMPACT_WARNING_ROW_LIMIT,
) -> dict[str, Any]:
    compact = {
        "schema_id": warning_map.get("schema_id") or "ion.codex_queue_runner_ai_movement_warning_map.v1",
        "status": warning_map.get("status"),
        "preflight_count": warning_map.get("preflight_count"),
        "accepted_count": warning_map.get("accepted_count"),
        "blocked_count": warning_map.get("blocked_count"),
        "warning_count": warning_map.get("warning_count"),
        "operator_warning_count": warning_map.get("operator_warning_count"),
        "agent_cwd_boundary_missing_count": warning_map.get("agent_cwd_boundary_missing_count"),
        "agent_cwd_boundary_blocked_count": warning_map.get("agent_cwd_boundary_blocked_count"),
        "agent_cwd_boundary_warning_count": warning_map.get("agent_cwd_boundary_warning_count"),
        "latest_preflight": warning_map.get("latest_preflight"),
    }
    if include_rows:
        bounded = _bounded_positive_int(
            row_limit,
            default=DEFAULT_COMPACT_WARNING_ROW_LIMIT,
            minimum=1,
            maximum=MAX_COMPACT_WARNING_ROW_LIMIT,
        )
        rows = [row for row in list(warning_map.get("warning_rows") or []) if isinstance(row, Mapping)]
        preflights = [row for row in list(warning_map.get("latest_preflights") or []) if isinstance(row, Mapping)]
        compact["warning_rows"] = rows[:bounded]
        compact["warning_rows_truncated"] = len(rows) > bounded
        compact["latest_preflights"] = preflights[:bounded]
        compact["latest_preflights_truncated"] = len(preflights) > bounded
        compact["row_limit"] = bounded
    return compact


def _compact_latest_run_row(row: Mapping[str, Any]) -> dict[str, Any]:
    submit = row.get("submit_result") if isinstance(row.get("submit_result"), Mapping) else {}
    lifecycle = [item for item in list(row.get("worker_lifecycle_events") or []) if isinstance(item, Mapping)]
    latest_lifecycle = lifecycle[-1] if lifecycle else {}
    return {
        "run_id": row.get("run_id"),
        "request_id": row.get("request_id"),
        "request_path": row.get("request_path"),
        "status": row.get("status"),
        "run_packet_path": row.get("run_packet_path"),
        "started_at": row.get("started_at"),
        "completed_at": row.get("completed_at"),
        "updated_at": row.get("updated_at"),
        "failure_classification": row.get("failure_classification"),
        "worker_sign_in_status": row.get("worker_sign_in_status"),
        "context_receipt_path": row.get("context_receipt_path"),
        "worker_context_awareness_receipt_path": row.get("worker_context_awareness_receipt_path"),
        "accepted_for_carrier_intake": submit.get("accepted_for_carrier_intake"),
        "task_return_packet_path": submit.get("packet_path"),
        "latest_worker_lifecycle_event": latest_lifecycle,
    }


def _artifact_surface(
    root: Path,
    rel_path: Any,
    *,
    include_preview: bool = False,
    max_preview_bytes: int = DEFAULT_COMPACT_PREVIEW_BYTES,
) -> dict[str, Any]:
    rel = str(rel_path or "").strip()
    payload: dict[str, Any] = {
        "path": rel or None,
        "exists": False,
        "bytes": None,
        "sha256": None,
    }
    if not rel:
        return payload
    try:
        target = _safe_rel_path(root, rel)
    except ValueError:
        payload["finding"] = "path_not_repo_relative"
        return payload
    if not target.exists() or not target.is_file():
        return payload
    data = target.read_bytes()
    payload["exists"] = True
    payload["bytes"] = len(data)
    payload["sha256"] = _sha256_bytes(data)
    if include_preview:
        bounded = _bounded_preview_bytes(max_preview_bytes)
        preview = data[:bounded].decode("utf-8", errors="replace")
        payload["preview"] = preview
        payload["preview_truncated"] = len(data) > bounded
        payload["shown_bytes"] = min(len(data), bounded)
    return payload


def _summarize_changed_paths(*containers: Any) -> dict[str, Any]:
    collected: list[str] = []
    seen: set[str] = set()
    keys = ("changed_files", "changed_paths", "touched_paths", "workload_diff_paths")

    def _append_path(candidate: Any) -> None:
        path = str(candidate or "").strip()
        if not path or path in seen:
            return
        seen.add(path)
        collected.append(path)

    for container in containers:
        if not isinstance(container, Mapping):
            continue
        for key in keys:
            value = container.get(key)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, Mapping):
                        _append_path(item.get("path") or item.get("target_path"))
                    else:
                        _append_path(item)
            elif isinstance(value, Mapping):
                for item in value.values():
                    if isinstance(item, list):
                        for row in item:
                            if isinstance(row, Mapping):
                                _append_path(row.get("path") or row.get("target_path"))
                            else:
                                _append_path(row)
    shown = collected[:MAX_COMPACT_CHANGED_PATHS]
    return {
        "count": len(collected),
        "paths": shown,
        "truncated": len(collected) > len(shown),
    }


def _compact_preview_from_artifacts(
    artifacts: Mapping[str, Mapping[str, Any]],
    *,
    include_preview: bool,
    preview_target: str | None,
    max_preview_bytes: int,
) -> dict[str, Any]:
    if not include_preview:
        return {"requested": False, "included": False}
    bounded = _bounded_preview_bytes(max_preview_bytes)
    target = str(preview_target or "").strip()
    if target and target not in PROCESS_ONCE_PREVIEW_TARGETS:
        return {
            "requested": True,
            "included": False,
            "target": target,
            "finding": "preview_target_not_allowed",
        }
    candidates = [target] if target else ["result", "stderr", "stdout", "worker_stderr", "worker_stdout", "task_return_body"]
    for candidate in candidates:
        surface = artifacts.get(candidate) if isinstance(artifacts.get(candidate), Mapping) else None
        if not surface or not surface.get("exists"):
            continue
        text = str(surface.get("preview") or "")
        if text:
            raw = text.encode("utf-8", errors="replace")
            shown = raw[:bounded].decode("utf-8", errors="replace")
            return {
                "requested": True,
                "included": True,
                "target": candidate,
                "text": shown,
                "truncated": bool(surface.get("preview_truncated")) or len(raw) > bounded,
                "shown_bytes": min(len(raw), bounded),
                "max_preview_bytes": bounded,
            }
        return {
            "requested": True,
            "included": False,
            "target": candidate,
            "finding": "preview_empty",
        }
    return {
        "requested": True,
        "included": False,
        "finding": "preview_unavailable",
        "max_preview_bytes": bounded,
    }


def _compact_process_once_result(
    root: Path,
    result: Mapping[str, Any],
    *,
    include_preview: bool,
    preview_target: str | None,
    max_preview_bytes: int,
) -> dict[str, Any]:
    run = result.get("run") if isinstance(result.get("run"), Mapping) else {}
    submit = run.get("submit_result") if isinstance(run.get("submit_result"), Mapping) else {}
    latest_event = None
    lifecycle = run.get("worker_lifecycle_events")
    if isinstance(lifecycle, list) and lifecycle and isinstance(lifecycle[-1], Mapping):
        latest_event = lifecycle[-1]
    task_return_packet_path = str(submit.get("packet_path") or result.get("task_return_packet_path") or "").strip() or None
    artifacts = {
        "result": _artifact_surface(root, run.get("last_message_path"), include_preview=include_preview, max_preview_bytes=max_preview_bytes),
        "stdout": _artifact_surface(root, run.get("stdout_path"), include_preview=include_preview, max_preview_bytes=max_preview_bytes),
        "stderr": _artifact_surface(root, run.get("stderr_path"), include_preview=include_preview, max_preview_bytes=max_preview_bytes),
        "worker_stdout": _artifact_surface(
            root,
            f"{run.get('run_dir')}/worker_stdout.log" if run.get("run_dir") else None,
            include_preview=include_preview,
            max_preview_bytes=max_preview_bytes,
        ),
        "worker_stderr": _artifact_surface(
            root,
            f"{run.get('run_dir')}/worker_stderr.log" if run.get("run_dir") else None,
            include_preview=include_preview,
            max_preview_bytes=max_preview_bytes,
        ),
        "task_return_body": _artifact_surface(root, run.get("task_return_body_path"), include_preview=include_preview, max_preview_bytes=max_preview_bytes),
    }
    blockers: list[str] = []
    for value in (
        result.get("finding"),
        run.get("failure_classification"),
        latest_event.get("terminal_state") if isinstance(latest_event, Mapping) else None,
    ):
        text = str(value or "").strip()
        if text and text not in blockers:
            blockers.append(text)
    status = str(result.get("result") or run.get("status") or "").strip() or None
    return {
        "schema_id": "ion.codex_queue_process_once_compact.v1",
        "ok": bool(result.get("ok")),
        "status": status,
        "finding": str(result.get("finding") or "").strip() or None,
        "request_id": run.get("request_id") or result.get("request_id"),
        "request_path": run.get("request_path") or result.get("request_path"),
        "lane_id": run.get("lane_id") or result.get("lane_id"),
        "run_id": run.get("run_id") or result.get("run_id"),
        "run_packet_path": run.get("run_packet_path") or result.get("run_packet_path"),
        "terminal_state": (latest_event.get("terminal_state") if isinstance(latest_event, Mapping) else None),
        "manual_proceed_relay_required": bool(result.get("manual_proceed_relay_required")),
        "changed_files": _summarize_changed_paths(result, run, submit),
        "receipts": {
            "context_receipt_path": run.get("context_receipt_path"),
            "worker_context_awareness_receipt_path": run.get("worker_context_awareness_receipt_path"),
            "ai_movement_preflight_receipt_path": run.get("ai_movement_preflight_receipt_path"),
            "task_return_body_path": run.get("task_return_body_path"),
            "task_return_packet_path": task_return_packet_path,
        },
        "artifacts": artifacts,
        "preview": _compact_preview_from_artifacts(
            artifacts,
            include_preview=include_preview,
            preview_target=preview_target,
            max_preview_bytes=max_preview_bytes,
        ),
        "blockers": blockers,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _compact_codex_worker_live_status(
    root: Path,
    status: Mapping[str, Any],
    *,
    include_observability_trace: bool = False,
    lifecycle_limit: int = DEFAULT_WORKER_LIFECYCLE_LIMIT,
    latest_runs_limit: int = DEFAULT_WORKER_LATEST_RUNS_LIMIT,
    latest_runs_cursor: str | None = None,
    latest_runs_status_filter: set[str] | None = None,
) -> dict[str, Any]:
    telemetry = status.get("live_worker_telemetry") if isinstance(status.get("live_worker_telemetry"), Mapping) else {}
    raw_artifacts = telemetry.get("artifacts") if isinstance(telemetry.get("artifacts"), Mapping) else {}
    artifact_surfaces: dict[str, Any] = {}
    for key in ("run_packet", "stdout", "stderr", "latest_return", "worker_stdout", "worker_stderr", "worker_context_awareness_receipt"):
        row = raw_artifacts.get(key) if isinstance(raw_artifacts.get(key), Mapping) else {}
        artifact_surfaces[key] = _artifact_surface(root, row.get("path"))
        artifact_surfaces[key]["modified_at"] = row.get("modified_at")

    preview = telemetry.get("preview") if isinstance(telemetry.get("preview"), Mapping) else {"requested": False, "included": False}
    preferred_preview = telemetry.get("preferred_preview") if isinstance(telemetry.get("preferred_preview"), Mapping) else None
    lifecycle_rows = [row for row in list(telemetry.get("worker_lifecycle_events") or []) if isinstance(row, Mapping)]
    lifecycle_bound = _bounded_positive_int(
        lifecycle_limit,
        default=DEFAULT_WORKER_LIFECYCLE_LIMIT,
        minimum=1,
        maximum=MAX_WORKER_LIFECYCLE_LIMIT,
    )
    lifecycle_visible = lifecycle_rows[-lifecycle_bound:]
    latest_lifecycle = (
        lifecycle_visible[-1]
        if lifecycle_visible
        else telemetry.get("latest_worker_lifecycle_event")
    )

    latest_runs_raw = [row for row in list(status.get("latest_runs") or []) if isinstance(row, Mapping)]
    compact_latest_runs = [_compact_latest_run_row(row) for row in latest_runs_raw]
    filtered_latest_runs = compact_latest_runs
    filter_values = latest_runs_status_filter or set()
    if filter_values:
        filtered_latest_runs = [
            row for row in compact_latest_runs
            if str(row.get("status") or "").strip().lower() in filter_values
        ]
    latest_runs_bound = _bounded_positive_int(
        latest_runs_limit,
        default=DEFAULT_WORKER_LATEST_RUNS_LIMIT,
        minimum=1,
        maximum=MAX_WORKER_LATEST_RUNS_LIMIT,
    )
    latest_runs_page = _paginate_by_cursor(
        filtered_latest_runs,
        cursor=latest_runs_cursor,
        limit=latest_runs_bound,
        cursor_keys=("run_packet_path", "run_id", "request_id"),
    )
    blockers: list[str] = []
    for value in (
        telemetry.get("phase_status"),
        telemetry.get("run_status"),
        telemetry.get("terminal_intake_result", {}).get("state") if isinstance(telemetry.get("terminal_intake_result"), Mapping) else None,
    ):
        text = str(value or "").strip()
        if text in {"terminal-blocked", "terminal-failed", "template-invalid", "RETURN_TEMPLATE_INVALID"} and text not in blockers:
            blockers.append(text)

    compact_telemetry: dict[str, Any] = {
        "schema_id": telemetry.get("schema_id") or "ion.codex_worker_live_status.v1",
        "phase_status": telemetry.get("phase_status"),
        "run_status": telemetry.get("run_status"),
        "active_worker_pid": telemetry.get("active_worker_pid"),
        "active_run_id": telemetry.get("active_run_id"),
        "request_id": telemetry.get("request_id"),
        "request_path": telemetry.get("request_path"),
        "run_packet_path": telemetry.get("run_packet_path"),
        "elapsed_seconds": telemetry.get("elapsed_seconds"),
        "start_request_age_seconds": telemetry.get("start_request_age_seconds"),
        "start_no_receipt_grace_seconds": telemetry.get("start_no_receipt_grace_seconds"),
        "active_process_running": telemetry.get("active_process_running"),
        "stale_active_reference_detected": telemetry.get("stale_active_reference_detected"),
        "worker_sign_in_status": telemetry.get("worker_sign_in_status"),
        "worker_context_awareness_receipt_path": telemetry.get("worker_context_awareness_receipt_path"),
        "worker_context_awareness_receipt_sha256": telemetry.get("worker_context_awareness_receipt_sha256"),
        "worker_context_awareness_machine_attestation_sha256": telemetry.get("worker_context_awareness_machine_attestation_sha256"),
        "latest_worker_lifecycle_event": latest_lifecycle,
        "worker_lifecycle_events": lifecycle_visible,
        "worker_lifecycle_event_count": len(lifecycle_rows),
        "worker_lifecycle_events_truncated": len(lifecycle_rows) > len(lifecycle_visible),
        "worker_lifecycle_limit": lifecycle_bound,
        "proof_gate_preflight": telemetry.get("proof_gate_preflight"),
        "ai_movement_gate_preflight": telemetry.get("ai_movement_gate_preflight"),
        "terminal_intake_result": telemetry.get("terminal_intake_result"),
        "artifacts": artifact_surfaces,
        "preview": preview,
        "preferred_preview": preferred_preview,
        "last_heartbeat_or_event_at": telemetry.get("last_heartbeat_or_event_at"),
        "blockers": blockers,
    }
    if include_observability_trace and isinstance(telemetry.get("observability_trace"), Mapping):
        compact_telemetry["observability_trace"] = telemetry.get("observability_trace")

    ai_map = status.get("ai_movement_preflight_warning_map") if isinstance(status.get("ai_movement_preflight_warning_map"), Mapping) else {}
    ai_summary = {
        "schema_id": ai_map.get("schema_id"),
        "status": ai_map.get("status"),
        "preflight_count": ai_map.get("preflight_count"),
        "accepted_count": ai_map.get("accepted_count"),
        "blocked_count": ai_map.get("blocked_count"),
        "warning_count": ai_map.get("warning_count"),
        "agent_cwd_boundary_missing_count": ai_map.get("agent_cwd_boundary_missing_count"),
        "agent_cwd_boundary_blocked_count": ai_map.get("agent_cwd_boundary_blocked_count"),
        "agent_cwd_boundary_warning_count": ai_map.get("agent_cwd_boundary_warning_count"),
        "operator_warning_count": ai_map.get("operator_warning_count"),
        "latest_preflight_request_id": ai_map.get("latest_preflight", {}).get("request_id") if isinstance(ai_map.get("latest_preflight"), Mapping) else None,
        "latest_preflight_receipt_path": ai_map.get("latest_preflight", {}).get("receipt_path") if isinstance(ai_map.get("latest_preflight"), Mapping) else None,
    }

    return {
        "schema_id": status.get("schema_id") or "ion.codex_queue_runner.v1",
        "verdict": status.get("verdict"),
        "runner_state_path": status.get("runner_state_path"),
        "queue_path": status.get("queue_path"),
        "queued_request_count": status.get("queued_request_count"),
        "next_request_path": status.get("next_request_path"),
        "active_run": status.get("active_run"),
        "active_process_running": status.get("active_process_running"),
        "stale_active_run_detected": status.get("stale_active_run_detected"),
        "reconciliation": status.get("reconciliation"),
        "live_worker_telemetry": compact_telemetry,
        "latest_runs": latest_runs_page["rows"],
        "latest_runs_total_count": len(compact_latest_runs),
        "latest_runs_filtered_count": len(filtered_latest_runs),
        "latest_runs_limit": latest_runs_bound,
        "latest_runs_cursor": latest_runs_page["cursor"],
        "latest_runs_next_cursor": latest_runs_page["next_cursor"],
        "latest_runs_has_more": latest_runs_page["has_more"],
        "latest_runs_cursor_found": latest_runs_page["cursor_found"],
        "latest_runs_status_filter": sorted(filter_values) if filter_values else [],
        "ai_movement_preflight_warning_map_summary": ai_summary,
        "ai_movement_preflight_warning_map": _compact_ai_movement_warning_map(ai_map),
        "failure_classes": status.get("failure_classes"),
        "manual_proceed_relay_required": bool(status.get("manual_proceed_relay_required")),
        "automation_surface": status.get("automation_surface"),
        "autorun_loop_state": status.get("autorun_loop_state"),
        "production_authority": False,
        "live_execution_authority": False,
    }


def _capsule_file_surface(
    root: Path,
    rel_path: str,
    *,
    include_preview: bool = False,
    max_preview_bytes: int = 512,
) -> dict[str, Any]:
    target, finding = _validate_read_path(
        root,
        rel_path,
        allowed_roots=(
            Path("ION/05_context/current/codex_solo"),
            Path("ION/05_context/current/codex_capsule_chat"),
        ),
    )
    if finding or target is None:
        return {"path": rel_path, "exists": False, "finding": finding or "invalid_path"}
    if not target.exists():
        return {"path": rel_path, "exists": False, "finding": "path_missing"}
    if not target.is_file():
        return {"path": rel_path, "exists": False, "finding": "path_not_file"}
    data = target.read_bytes()
    payload: dict[str, Any] = {
        "path": _connector_rel(target, root),
        "exists": True,
        "bytes": len(data),
        "sha256": _sha256_bytes(data),
    }
    if include_preview:
        bounded_max = min(max(int(max_preview_bytes), 1), 2048)
        preview = data[:bounded_max].decode("utf-8", errors="replace")
        payload["preview"] = preview
        payload["preview_truncated"] = len(data) > bounded_max
    return payload


def _codex_capsule_chat_status(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    include_preview = bool(args.get("include_preview"))
    max_preview_bytes = int(args.get("max_preview_bytes") or 512)
    state_rel = "ION/05_context/current/codex_capsule_chat/state.json"
    state_payload = _read_json(root / state_rel) or {}
    lanes = state_payload.get("lanes") if isinstance(state_payload.get("lanes"), Mapping) else {}
    lane_summaries: dict[str, Any] = {}
    for lane_id in ("codex_general", "ion_system"):
        lane = lanes.get(lane_id) if isinstance(lanes.get(lane_id), Mapping) else {}
        turns = lane.get("turns") if isinstance(lane.get("turns"), list) else []
        queue_links = lane.get("queue_links") if isinstance(lane.get("queue_links"), list) else []
        latest_turn = turns[-1] if turns and isinstance(turns[-1], Mapping) else {}
        lane_summaries[lane_id] = {
            "turn_count": len(turns),
            "queue_link_count": len(queue_links),
            "latest_turn_id": latest_turn.get("turn_id"),
            "latest_turn_kind": latest_turn.get("kind"),
            "latest_turn_created_at": latest_turn.get("created_at"),
        }
    return _ok("ion_codex_capsule_chat_status", {
        "schema_id": "ion.codex_capsule_chat_bridge_status.v1",
        "state_path": state_rel,
        "state_exists": (root / state_rel).exists(),
        "state_sha256": _sha256_file(root / state_rel) if (root / state_rel).exists() else None,
        "paths": {
            "capsule": _capsule_file_surface(
                root,
                "ION/05_context/current/codex_solo/CAPSULE.md",
                include_preview=include_preview,
                max_preview_bytes=max_preview_bytes,
            ),
            "mini": _capsule_file_surface(
                root,
                "ION/05_context/current/codex_solo/MINI.md",
                include_preview=include_preview,
                max_preview_bytes=max_preview_bytes,
            ),
            "hot_context": _capsule_file_surface(
                root,
                "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
                include_preview=include_preview,
                max_preview_bytes=max_preview_bytes,
            ),
        },
        "lanes": lane_summaries,
        "production_authority": False,
        "live_execution_authority": False,
    })


def _codex_capsule_message_send(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_dual_codex_chat import record_chat_turn

    lane_id = str(args.get("lane_id") or "codex_general").strip() or "codex_general"
    message = str(args.get("message") or args.get("body") or "").strip()
    author = str(args.get("author") or "user").strip() or "user"
    execution_mode = str(args.get("execution_mode") or "respond_only").strip() or "respond_only"
    if not message:
        return _blocked("ion_codex_capsule_message_send", "message_required")
    if execution_mode != "respond_only":
        return _blocked(
            "ion_codex_capsule_message_send",
            "execution_mode_must_be_respond_only_for_bounded_message_send",
            {"allowed_execution_modes": ["respond_only"]},
        )
    result = record_chat_turn(
        root,
        lane_id=lane_id,
        message=message,
        author=author,
        execution_mode="respond_only",
        context_refs=list(args.get("context_refs") or []),
    )
    if not result.get("ok"):
        return _blocked("ion_codex_capsule_message_send", str(result.get("finding") or "capsule_message_send_blocked"), result)
    turn = result.get("turn") if isinstance(result.get("turn"), Mapping) else {}
    assistant_turn = result.get("assistant_turn") if isinstance(result.get("assistant_turn"), Mapping) else {}
    packet = {
        "schema_id": "ion.codex_capsule_chat_message_packet.v1",
        "lane_id": lane_id,
        "author": author,
        "execution_mode": "respond_only",
        "turn_id": turn.get("turn_id"),
        "assistant_turn_id": assistant_turn.get("turn_id"),
        "message_sha256": _sha256_text(message),
        "message_preview": _preview_text(message),
        "created_at": _now(),
        "status": "RECORDED_TO_CAPSULE_CHAT_STATE",
        "production_authority": False,
        "live_execution_authority": False,
    }
    packet_path = _write_connector_packet(root, "capsule_messages", f"{lane_id}_message", packet)
    return _ok("ion_codex_capsule_message_send", {
        "lane_id": lane_id,
        "turn_id": turn.get("turn_id"),
        "assistant_turn_id": assistant_turn.get("turn_id"),
        "state_path": "ION/05_context/current/codex_capsule_chat/state.json",
        "packet_path": _connector_rel(packet_path, root),
        "status": "RECORDED_TO_CAPSULE_CHAT_STATE",
    }, mutates_active_state=True)


def _codex_capsule_message_poll(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_dual_codex_chat import load_dual_chat_state

    lane_id = str(args.get("lane_id") or "codex_general").strip() or "codex_general"
    limit = min(max(int(args.get("limit") or 25), 1), 100)
    include_assistant = bool(args.get("include_assistant", True))
    include_context_posts = bool(args.get("include_context_posts", False))
    since_turn_id = str(args.get("since_turn_id") or "").strip()
    state = load_dual_chat_state(root)
    lanes = state.get("lanes") if isinstance(state.get("lanes"), Mapping) else {}
    lane = lanes.get(lane_id) if isinstance(lanes.get(lane_id), Mapping) else None
    if lane is None:
        return _blocked("ion_codex_capsule_message_poll", "unknown_lane_id", {"allowed_lanes": sorted(lanes)})
    turns = lane.get("turns") if isinstance(lane.get("turns"), list) else []
    start_index = 0
    if since_turn_id:
        for idx, raw in enumerate(turns):
            if isinstance(raw, Mapping) and str(raw.get("turn_id") or "") == since_turn_id:
                start_index = idx + 1
                break
    records: list[dict[str, Any]] = []
    for raw in reversed(turns[start_index:]):
        if not isinstance(raw, Mapping):
            continue
        author = str(raw.get("author") or "")
        kind = str(raw.get("kind") or "")
        if not include_assistant and author not in {"operator", "user"}:
            continue
        if not include_context_posts and kind == "mini_auto_post":
            continue
        message = str(raw.get("message") or "")
        records.append({
            "turn_id": raw.get("turn_id"),
            "created_at": raw.get("created_at"),
            "author": author,
            "kind": kind,
            "execution_mode": raw.get("execution_mode"),
            "message_sha256": raw.get("message_sha256"),
            "message_preview": _preview_text(message, limit=420),
        })
        if len(records) >= limit:
            break
    return _ok("ion_codex_capsule_message_poll", {
        "lane_id": lane_id,
        "since_turn_id": since_turn_id or None,
        "message_count": len(records),
        "messages": records,
        "state_path": "ION/05_context/current/codex_capsule_chat/state.json",
    })


def _codex_capsule_sync_to_queue(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_dual_codex_chat import WRITE_CONFIRMATION_TOKEN as CAPSULE_WRITE_CONFIRMATION_TOKEN
    from .ion_dual_codex_chat import queue_chat_codex_work_packet

    lane_id = str(args.get("lane_id") or "codex_general").strip() or "codex_general"
    objective = str(args.get("objective") or args.get("message") or "").strip()
    source_turn_id = str(args.get("source_turn_id") or "").strip() or None
    if not objective:
        return _blocked("ion_codex_capsule_sync_to_queue", "objective_required")
    result = queue_chat_codex_work_packet(
        root,
        lane_id=lane_id,
        objective=objective,
        confirmation=CAPSULE_WRITE_CONFIRMATION_TOKEN,
        source_turn_id=source_turn_id,
        context_refs=list(args.get("context_refs") or []),
    )
    if not result.get("ok"):
        return _blocked("ion_codex_capsule_sync_to_queue", str(result.get("finding") or "capsule_sync_to_queue_blocked"), result)
    queue_link = result.get("queue_link") if isinstance(result.get("queue_link"), Mapping) else {}
    packet_path = _write_connector_packet(root, "capsule_queue_sync", f"{lane_id}_sync", {
        "schema_id": "ion.codex_capsule_chat_queue_sync_packet.v1",
        "lane_id": lane_id,
        "source_turn_id": source_turn_id,
        "objective_sha256": _sha256_text(objective),
        "objective_preview": _preview_text(objective, limit=420),
        "queue_link": queue_link,
        "created_at": _now(),
        "status": queue_link.get("status") or "QUEUED_FOR_CODEX_CARRIER",
        "production_authority": False,
        "live_execution_authority": False,
    })
    return _ok("ion_codex_capsule_sync_to_queue", {
        "queue_link": queue_link,
        "sync_packet_path": _connector_rel(packet_path, root),
    }, mutates_active_state=True)


def _bounded_connector_packet_path(root: Path, rel_value: str, *, subdir: str) -> Path:
    path = _safe_rel_path(root, rel_value)
    allowed_root = (root / CONNECTOR_STATE_DIR / subdir).resolve()
    path.relative_to(allowed_root)
    if path.suffix != ".json":
        raise ValueError("connector packet path must point to a JSON packet")
    return path


def _load_json_file(path: Path) -> dict[str, Any]:
    value = _read_json(path)
    return value if isinstance(value, dict) else {}


def _task_returns_for_request(root: Path, request_path: str | None, request_id: str | None) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    returns_root = root / CONNECTOR_STATE_DIR / "task_returns"
    if not returns_root.exists():
        return results
    for path in sorted(returns_root.glob("*.json")):
        payload = _load_json_file(path)
        if request_path and payload.get("work_request_path") == request_path:
            results.append({"path": path.relative_to(root).as_posix(), "packet": payload})
        elif request_id and payload.get("work_request_id") == request_id:
            results.append({"path": path.relative_to(root).as_posix(), "packet": payload})
    return results


def _task_return_sort_key(item: Mapping[str, Any]) -> tuple[str, str]:
    packet = item.get("packet") if isinstance(item.get("packet"), Mapping) else {}
    created_at = str(packet.get("created_at") or "")
    rel_path = str(item.get("path") or "")
    return (created_at, rel_path)


def _codex_work_request_return_projection(
    root: Path,
    *,
    request_path: str,
    request_id: str,
    payload_latest_return_packet_path: str | None,
) -> dict[str, Any]:
    returns = _task_returns_for_request(root, request_path, request_id)
    ordered = sorted(returns, key=_task_return_sort_key)
    accepted = [item for item in ordered if item["packet"].get("accepted_for_carrier_intake") is True]
    latest_observed = ordered[-1] if ordered else None
    settlement_pick = accepted[-1] if accepted else latest_observed
    settlement_path = str((settlement_pick or {}).get("path") or "") or None
    latest_observed_path = str((latest_observed or {}).get("path") or "") or None
    raw_latest_path = str(payload_latest_return_packet_path or "").strip() or None

    # When accepted evidence exists, treat later non-accepted packets as superseded wrapper evidence.
    superseded_wrapper = [
        str(item.get("path") or "")
        for item in ordered
        if item["packet"].get("accepted_for_carrier_intake") is not True
        and (
            not accepted
            or _task_return_sort_key(item) > _task_return_sort_key(accepted[-1])
        )
    ]
    effective_latest = settlement_path or latest_observed_path or raw_latest_path
    projection_source = (
        "accepted_carrier_intake"
        if settlement_path and accepted
        else ("latest_observed_return_packet" if latest_observed_path else "request_payload_latest_return_packet_path")
    )
    settlement_packet = settlement_pick["packet"] if isinstance(settlement_pick, Mapping) else {}
    return {
        "returns": returns,
        "linked_return_count": len(ordered),
        "accepted_return_count": len(accepted),
        "latest_observed_return_packet_path": latest_observed_path,
        "latest_return_packet_path_raw": raw_latest_path,
        "effective_latest_return_packet_path": effective_latest,
        "settlement_relevant_return_packet_path": settlement_path,
        "settlement_relevant_return_result": settlement_packet.get("result"),
        "settlement_relevant_return_created_at": settlement_packet.get("created_at"),
        "settlement_relevant_machine_receipt_path": settlement_packet.get("machine_receipt_path"),
        "settlement_relevant_automation_diagnosis": settlement_packet.get("automation_diagnosis"),
        "settlement_relevant_source": projection_source,
        "superseded_wrapper_return_packet_paths": superseded_wrapper,
    }


def _codex_work_queue_target_binding_audit(requests: list[Mapping[str, Any]]) -> dict[str, Any]:
    projections = [
        request.get("ai_movement_target_binding_projection")
        for request in requests
        if isinstance(request.get("ai_movement_target_binding_projection"), Mapping)
    ]
    blocked = [item for item in projections if item.get("warning_level") == "blocked"]
    warnings = [item for item in projections if item.get("warning_level") == "warning"]
    accepted = [item for item in projections if item.get("accepted") is True]
    return {
        "schema_id": "ion.chatgpt_browser_connector_codex_queue_target_binding_audit.v1",
        "status": "READ_ONLY_PROJECTION",
        "projection_only": True,
        "queue_processing_started": False,
        "worker_process_started": False,
        "request_count": len(projections),
        "accepted_count": len(accepted),
        "warning_count": len(warnings),
        "blocked_count": len(blocked),
        "operator_warning_count": len(warnings) + len(blocked),
        "blocked_request_ids": [
            str(request.get("request_id") or "")
            for request in requests
            if isinstance(request.get("ai_movement_target_binding_projection"), Mapping)
            and request["ai_movement_target_binding_projection"].get("warning_level") == "blocked"
        ],
        "warning_request_ids": [
            str(request.get("request_id") or "")
            for request in requests
            if isinstance(request.get("ai_movement_target_binding_projection"), Mapping)
            and request["ai_movement_target_binding_projection"].get("warning_level") == "warning"
        ],
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }


def _codex_work_queue(
    root: Path,
    args: Mapping[str, Any] | None = None,
    *,
    limit: int | None = None,
) -> dict[str, Any]:
    arguments = dict(args or {})
    queue_limit = _bounded_positive_int(
        limit if limit is not None else arguments.get("limit"),
        default=DEFAULT_QUEUE_PAGE_LIMIT,
        minimum=1,
        maximum=MAX_QUEUE_PAGE_LIMIT,
    )
    cursor = str(arguments.get("cursor") or "").strip() or None
    status_filter = _status_filter_values(arguments.get("status_filter") or arguments.get("status"))
    include_ai_rows = bool(arguments.get("include_ai_movement_rows"))
    ai_row_limit = _bounded_positive_int(
        arguments.get("ai_movement_row_limit"),
        default=DEFAULT_COMPACT_WARNING_ROW_LIMIT,
        minimum=1,
        maximum=MAX_COMPACT_WARNING_ROW_LIMIT,
    )
    include_full_warning_map = bool(arguments.get("include_full_warning_map"))

    requests_root = root / CONNECTOR_STATE_DIR / "codex_work_requests"
    all_requests: list[dict[str, Any]] = []
    ai_movement_warning_map = build_ai_movement_preflight_warning_map(root, limit=queue_limit)
    ai_movement_preflights = [
        item for item in ai_movement_warning_map.get("latest_preflights", [])
        if isinstance(item, Mapping)
    ]
    ai_movement_by_request_id = {
        str(item.get("request_id")): item
        for item in ai_movement_preflights
        if item.get("request_id")
    }
    ai_movement_by_request_path = {
        str(item.get("request_path")): item
        for item in ai_movement_preflights
        if item.get("request_path")
    }
    if requests_root.exists():
        for path in sorted(requests_root.glob("*.json"), reverse=True):
            payload = _load_json_file(path)
            rel_path = path.relative_to(root).as_posix()
            ai_movement_projection = (
                ai_movement_by_request_path.get(rel_path)
                or ai_movement_by_request_id.get(str(payload.get("request_id") or ""))
            )
            projection = _codex_work_request_return_projection(
                root,
                request_path=rel_path,
                request_id=str(payload.get("request_id") or ""),
                payload_latest_return_packet_path=str(payload.get("latest_return_packet_path") or ""),
            )
            target_binding_projection = compact_codex_work_request_target_binding_projection(payload)
            lane_projection = classify_codex_work_request_lane(payload)
            request_row = {
                "request_id": payload.get("request_id"),
                "path": rel_path,
                "objective": payload.get("objective"),
                "objective_sha256": payload.get("objective_sha256") or _codex_work_request_objective_fingerprint(str(payload.get("objective") or "")),
                "dedupe_key": payload.get("dedupe_key"),
                "idempotency_source": payload.get("idempotency_source"),
                "implicit_idempotency_key": payload.get("implicit_idempotency_key"),
                "status": payload.get("status"),
                "created_at": payload.get("created_at"),
                "updated_at": payload.get("updated_at"),
                "latest_return_packet_path": projection.get("effective_latest_return_packet_path"),
                "latest_return_packet_path_raw": projection.get("latest_return_packet_path_raw"),
                "latest_observed_return_packet_path": projection.get("latest_observed_return_packet_path"),
                "settlement_relevant_return_packet_path": projection.get("settlement_relevant_return_packet_path"),
                "settlement_relevant_return_result": projection.get("settlement_relevant_return_result"),
                "settlement_relevant_return_created_at": projection.get("settlement_relevant_return_created_at"),
                "settlement_relevant_machine_receipt_path": projection.get("settlement_relevant_machine_receipt_path"),
                "settlement_relevant_automation_diagnosis": projection.get("settlement_relevant_automation_diagnosis"),
                "settlement_relevant_source": projection.get("settlement_relevant_source"),
                "superseded_wrapper_return_packet_paths": projection.get("superseded_wrapper_return_packet_paths"),
                "return_packet_paths": payload.get("return_packet_paths", []),
                "queue_lifecycle_decision": payload.get("queue_lifecycle_decision"),
                "lane_id": lane_projection.get("lane_id"),
                "work_class": payload.get("work_class") or payload.get("workload_class") or lane_projection.get("work_class"),
                "work_lane_route_receipt": payload.get("work_lane_route_receipt") or lane_projection,
                "linked_return_count": projection.get("linked_return_count"),
                "accepted_return_count": projection.get("accepted_return_count"),
                "ai_movement_preflight_projection": ai_movement_projection,
                "agent_cwd_boundary_projection": (
                    ai_movement_projection.get("agent_cwd_boundary_projection")
                    if isinstance(ai_movement_projection, Mapping)
                    else None
                ),
                "ai_movement_target_binding_projection": target_binding_projection,
            }
            if status_filter:
                row_status = str(request_row.get("status") or "").strip().lower()
                if row_status not in status_filter:
                    continue
            all_requests.append(request_row)

    request_page = _paginate_by_cursor(
        all_requests,
        cursor=cursor,
        limit=queue_limit,
        cursor_keys=("path", "request_id"),
    )
    requests = request_page["rows"]
    groups: dict[str, list[dict[str, Any]]] = {}
    for request in all_requests:
        key = str(request.get("dedupe_key") or request.get("objective_sha256") or "").strip()
        if key:
            groups.setdefault(key, []).append(request)
    duplicate_group_count = 0
    for key, rows in groups.items():
        if len(rows) <= 1:
            continue
        duplicate_group_count += 1
        canonical = sorted(rows, key=lambda row: (str(row.get("created_at") or ""), str(row.get("path") or "")))[0]
        canonical_id = canonical.get("request_id")
        canonical_path = canonical.get("path")
        for index, row in enumerate(sorted(rows, key=lambda item: (str(item.get("created_at") or ""), str(item.get("path") or "")))):
            row["duplicate_group_key"] = key
            row["duplicate_group_count"] = len(rows)
            row["duplicate_index"] = index
            row["duplicate_of_request_id"] = None if row.get("path") == canonical_path else canonical_id
            row["duplicate_of_packet_path"] = None if row.get("path") == canonical_path else canonical_path
    compact_warning_map = _compact_ai_movement_warning_map(
        ai_movement_warning_map,
        include_rows=include_ai_rows,
        row_limit=ai_row_limit,
    )
    return {
        "schema_id": "ion.chatgpt_browser_connector_codex_work_queue.v1",
        "queue_path": CODEX_WORK_QUEUE_RELATIVE_PATH.as_posix(),
        "state_dir": (CONNECTOR_STATE_DIR / "codex_work_requests").as_posix(),
        "request_count": len(requests),
        "total_request_count": len(all_requests),
        "limit": queue_limit,
        "cursor": request_page["cursor"],
        "next_cursor": request_page["next_cursor"],
        "has_more": request_page["has_more"],
        "cursor_found": request_page["cursor_found"],
        "status_filter": sorted(status_filter) if status_filter else [],
        "duplicate_group_count": duplicate_group_count,
        "ai_movement_preflight_warning_map": compact_warning_map,
        "ai_movement_preflight_warning_map_full": ai_movement_warning_map if include_full_warning_map else None,
        "ai_movement_target_binding_audit": _codex_work_queue_target_binding_audit(requests),
        "requests": requests,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _write_codex_work_queue_index(root: Path) -> dict[str, Any]:
    queue = _codex_work_queue(root)
    _write_json(root / CODEX_WORK_QUEUE_RELATIVE_PATH, queue)
    materialize_codex_work_lane_index(root)
    return queue


def _codex_work_request_rows(root: Path) -> list[dict[str, Any]]:
    requests_root = root / CONNECTOR_STATE_DIR / "codex_work_requests"
    rows: list[dict[str, Any]] = []
    if not requests_root.exists():
        return rows
    for path in sorted(requests_root.glob("*.json")):
        payload = _load_json_file(path)
        rel_path = path.relative_to(root).as_posix()
        request_id = str(payload.get("request_id") or "").strip()
        objective = str(payload.get("objective") or "")
        objective_sha256 = str(payload.get("objective_sha256") or _codex_work_request_objective_fingerprint(objective))
        group_key = str(payload.get("dedupe_key") or objective_sha256).strip()
        projection = _codex_work_request_return_projection(
            root,
            request_path=rel_path,
            request_id=request_id,
            payload_latest_return_packet_path=str(payload.get("latest_return_packet_path") or ""),
        )
        lane_projection = classify_codex_work_request_lane(payload)
        rows.append({
            "request_id": request_id or None,
            "path": rel_path,
            "objective": objective,
            "objective_sha256": objective_sha256,
            "dedupe_key": payload.get("dedupe_key"),
            "group_key": group_key,
            "idempotency_source": payload.get("idempotency_source"),
            "implicit_idempotency_key": payload.get("implicit_idempotency_key"),
            "status": payload.get("status"),
            "created_at": payload.get("created_at"),
            "updated_at": payload.get("updated_at"),
            "latest_return_packet_path": projection.get("effective_latest_return_packet_path"),
            "latest_return_packet_path_raw": projection.get("latest_return_packet_path_raw"),
            "latest_observed_return_packet_path": projection.get("latest_observed_return_packet_path"),
            "settlement_relevant_return_packet_path": projection.get("settlement_relevant_return_packet_path"),
            "settlement_relevant_return_result": projection.get("settlement_relevant_return_result"),
            "settlement_relevant_return_created_at": projection.get("settlement_relevant_return_created_at"),
            "settlement_relevant_machine_receipt_path": projection.get("settlement_relevant_machine_receipt_path"),
            "settlement_relevant_automation_diagnosis": projection.get("settlement_relevant_automation_diagnosis"),
            "settlement_relevant_source": projection.get("settlement_relevant_source"),
            "superseded_wrapper_return_packet_paths": projection.get("superseded_wrapper_return_packet_paths"),
            "return_packet_paths": payload.get("return_packet_paths", []),
            "queue_lifecycle_decision": payload.get("queue_lifecycle_decision"),
            "lane_id": lane_projection.get("lane_id"),
            "work_class": payload.get("work_class") or payload.get("workload_class") or lane_projection.get("work_class"),
            "work_lane_route_receipt": payload.get("work_lane_route_receipt") or lane_projection,
            "linked_return_count": projection.get("linked_return_count"),
            "accepted_return_count": projection.get("accepted_return_count"),
            "payload": payload,
            "absolute_path": path,
        })
    return rows


def _codex_work_request_duplicate_groups(root: Path) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in _codex_work_request_rows(root):
        key = str(row.get("group_key") or "").strip()
        if key:
            grouped.setdefault(key, []).append(row)
    groups: list[dict[str, Any]] = []
    for key, rows in grouped.items():
        if len(rows) <= 1:
            continue
        ordered = sorted(rows, key=lambda item: (str(item.get("created_at") or ""), str(item.get("path") or "")))
        accepted = [row for row in ordered if int(row.get("accepted_return_count") or 0) > 0]
        canonical = accepted[0] if accepted else ordered[0]
        canonical_id = canonical.get("request_id")
        requests: list[dict[str, Any]] = []
        duplicates: list[dict[str, Any]] = []
        for index, row in enumerate(ordered):
            public = {k: v for k, v in row.items() if k not in {"payload", "absolute_path"}}
            public["duplicate_group_key"] = key
            public["duplicate_group_count"] = len(ordered)
            public["duplicate_index"] = index
            public["duplicate_of_request_id"] = None if row.get("path") == canonical.get("path") else canonical_id
            public["duplicate_of_packet_path"] = None if row.get("path") == canonical.get("path") else canonical.get("path")
            requests.append(public)
            if public["duplicate_of_packet_path"]:
                duplicates.append(public)
        groups.append({
            "group_key": key,
            "group_count": len(ordered),
            "canonical_request_id": canonical_id,
            "canonical_packet_path": canonical.get("path"),
            "duplicate_count": len(duplicates),
            "requests": requests,
            "duplicates": duplicates,
        })
    return sorted(
        groups,
        key=lambda group: max(str(row.get("created_at") or "") for row in group["requests"]),
        reverse=True,
    )


def _codex_queue_duplicate_audit(root: Path, args: Mapping[str, Any] | None = None) -> dict[str, Any]:
    arguments = dict(args or {})
    try:
        limit = int(arguments.get("limit") or 25)
    except (TypeError, ValueError):
        limit = 25
    limit = max(1, min(limit, 100))
    try:
        max_duplicates_per_group = int(arguments.get("max_duplicates_per_group") or 5)
    except (TypeError, ValueError):
        max_duplicates_per_group = 5
    max_duplicates_per_group = max(0, min(max_duplicates_per_group, 50))
    include_packets = bool(arguments.get("include_packets") or arguments.get("include_full") or arguments.get("full"))
    include_duplicates = bool(arguments.get("include_duplicates"))
    groups = _codex_work_request_duplicate_groups(root)
    visible_groups = groups[:limit]
    duplicate_request_count = sum(int(group.get("duplicate_count") or 0) for group in groups)

    def _compact_request(row: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "request_id": row.get("request_id"),
            "path": row.get("path"),
            "status": row.get("status"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
            "objective_sha256": row.get("objective_sha256"),
            "dedupe_key": row.get("dedupe_key"),
            "duplicate_index": row.get("duplicate_index"),
            "duplicate_of_request_id": row.get("duplicate_of_request_id"),
            "accepted_return_count": row.get("accepted_return_count"),
            "linked_return_count": row.get("linked_return_count"),
        }

    returned_groups = []
    for group in visible_groups:
        requests = list(group.get("requests") or [])
        duplicates = list(group.get("duplicates") or [])
        returned_duplicate_rows = duplicates[:max_duplicates_per_group] if (include_packets or include_duplicates) else []
        if include_packets:
            returned_groups.append(
                {
                    "group_key": group.get("group_key"),
                    "group_count": group.get("group_count"),
                    "canonical_request_id": group.get("canonical_request_id"),
                    "canonical_packet_path": group.get("canonical_packet_path"),
                    "requests": requests[:1],
                    "duplicate_count": group.get("duplicate_count"),
                    "duplicates_returned_count": len(returned_duplicate_rows),
                    "duplicates_truncated": len(duplicates) > len(returned_duplicate_rows),
                    "duplicates": returned_duplicate_rows,
                }
            )
        else:
            returned_groups.append(
                {
                    "group_key": group.get("group_key"),
                    "group_count": group.get("group_count"),
                    "canonical_request_id": group.get("canonical_request_id"),
                    "canonical_packet_path": group.get("canonical_packet_path"),
                    "canonical_request": _compact_request(requests[0]) if requests else None,
                    "duplicate_count": group.get("duplicate_count"),
                    "duplicates_returned_count": len(returned_duplicate_rows),
                    "duplicates_truncated": len(duplicates) > len(returned_duplicate_rows),
                    "duplicates": [_compact_request(row) for row in returned_duplicate_rows],
                }
            )
    response_mode = "full" if include_packets else "compact"

    return {
        "schema_id": "ion.chatgpt_browser_connector_codex_queue_duplicate_audit.v1",
        "status": "READ_ONLY_DUPLICATE_AUDIT",
        "response_mode": response_mode,
        "queue_path": CODEX_WORK_QUEUE_RELATIVE_PATH.as_posix(),
        "request_state_dir": (CONNECTOR_STATE_DIR / "codex_work_requests").as_posix(),
        "duplicate_group_count": len(groups),
        "duplicate_request_count": duplicate_request_count,
        "returned_group_count": len(returned_groups),
        "truncated": len(groups) > limit,
        "include_duplicates": include_duplicates,
        "max_duplicates_per_group": max_duplicates_per_group,
        "groups": returned_groups,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _load_codex_queue_duplicate_cleanup_idempotency_ledger(root: Path) -> dict[str, Any]:
    path = root / CODEX_QUEUE_DUPLICATE_CLEANUP_IDEMPOTENCY_LEDGER_RELATIVE_PATH
    payload = _read_json(path)
    if isinstance(payload, dict):
        payload.setdefault("schema_id", "ion.chatgpt_browser_connector_codex_queue_duplicate_cleanup_idempotency_ledger.v1")
        payload.setdefault("entries", {})
        return payload
    return {
        "schema_id": "ion.chatgpt_browser_connector_codex_queue_duplicate_cleanup_idempotency_ledger.v1",
        "created_at": _now(),
        "updated_at": _now(),
        "entries": {},
        "production_authority": False,
        "live_execution_authority": False,
    }


def _save_codex_queue_duplicate_cleanup_idempotency_ledger(root: Path, ledger: Mapping[str, Any]) -> None:
    _write_json(root / CODEX_QUEUE_DUPLICATE_CLEANUP_IDEMPOTENCY_LEDGER_RELATIVE_PATH, dict(ledger))


def _codex_queue_duplicate_cleanup_existing(root: Path, idempotency_key: str) -> dict[str, Any] | None:
    ledger = _load_codex_queue_duplicate_cleanup_idempotency_ledger(root)
    entries = ledger.get("entries") if isinstance(ledger.get("entries"), Mapping) else {}
    entry = entries.get(idempotency_key)
    if isinstance(entry, Mapping):
        receipt_path = root / str(entry.get("receipt_path") or "")
        if receipt_path.exists():
            return dict(entry)
    return None


def _record_codex_queue_duplicate_cleanup_idempotency(
    root: Path,
    idempotency_key: str,
    *,
    receipt_path: Path,
    superseded_request_ids: list[str],
) -> None:
    ledger = _load_codex_queue_duplicate_cleanup_idempotency_ledger(root)
    entries = dict(ledger.get("entries") if isinstance(ledger.get("entries"), Mapping) else {})
    entries[idempotency_key] = {
        "recorded_at": _now(),
        "receipt_path": receipt_path.relative_to(root).as_posix(),
        "superseded_request_ids": superseded_request_ids,
        "production_authority": False,
        "live_execution_authority": False,
    }
    ledger["entries"] = entries
    ledger["updated_at"] = _now()
    _save_codex_queue_duplicate_cleanup_idempotency_ledger(root, ledger)


def _codex_queue_duplicate_cleanup_replay_result(root: Path, existing: Mapping[str, Any], idempotency_key: str) -> dict[str, Any]:
    receipt_path = str(existing.get("receipt_path") or "")
    receipt = _load_json_file(root / receipt_path) if receipt_path else {}
    return _ok(
        "ion_codex_queue_supersede_duplicates",
        {
            "schema_id": "ion.chatgpt_browser_connector_codex_queue_supersede_duplicates_result.v1",
            "status": "IDEMPOTENT_REPLAY",
            "receipt_path": receipt_path,
            "receipt": receipt,
            "idempotent_replay": True,
            "duplicate_prevented": True,
            "idempotency_key": idempotency_key,
            "production_authority": False,
            "live_execution_authority": False,
        },
        mutates_active_state=False,
    )


def _codex_queue_supersede_duplicates(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    tool_name = "ion_codex_queue_supersede_duplicates"
    if str(args.get("confirmation") or "") != "ION_BOUNDED_WRITE_CONFIRMED":
        return _blocked(tool_name, "confirmation_required")
    idempotency_key_raw = str(args.get("idempotency_key") or "").strip()
    if not idempotency_key_raw:
        return _blocked(tool_name, "idempotency_key_required")
    idempotency_key = _normalize_idempotency_token(idempotency_key_raw)
    if args.get("force_new") is not True:
        existing = _codex_queue_duplicate_cleanup_existing(root, idempotency_key)
        if existing:
            return _codex_queue_duplicate_cleanup_replay_result(root, existing, idempotency_key)

    groups = _codex_work_request_duplicate_groups(root)
    selected_group_keys: set[str] = set()
    if args.get("all_duplicates") is True:
        selected_group_keys = {str(group.get("group_key")) for group in groups}
    for key_name in ("group_key", "dedupe_key", "objective_sha256"):
        value = str(args.get(key_name) or "").strip()
        if value:
            selected_group_keys.add(value)
    request_ids = {str(item).strip() for item in (args.get("request_ids") or []) if str(item).strip()}
    if not selected_group_keys and not request_ids:
        return _blocked(tool_name, "duplicate_selection_required")

    now = _now()
    to_update: list[tuple[Path, dict[str, Any], dict[str, Any]]] = []
    skipped: list[dict[str, Any]] = []
    for group in groups:
        group_key = str(group.get("group_key") or "")
        if selected_group_keys and group_key not in selected_group_keys:
            if not request_ids:
                continue
        canonical_id = str(group.get("canonical_request_id") or "")
        canonical_path = str(group.get("canonical_packet_path") or "")
        for row in group.get("duplicates") or []:
            rid = str(row.get("request_id") or "")
            if request_ids and rid not in request_ids:
                continue
            path = root / str(row.get("path") or "")
            payload = _load_json_file(path)
            status = str(payload.get("status") or "")
            if int(row.get("accepted_return_count") or 0) > 0:
                skipped.append({"request_id": rid, "path": row.get("path"), "reason": "accepted_return_present"})
                continue
            if status in {"CODEX_CLI_RUNNING", "CODEX_QUEUE_RUNNER_WORKER_STARTED"}:
                skipped.append({"request_id": rid, "path": row.get("path"), "reason": "active_or_running_status"})
                continue
            if status == "SUPERSEDED_DUPLICATE":
                skipped.append({"request_id": rid, "path": row.get("path"), "reason": "already_superseded"})
                continue
            to_update.append((path, payload, {
                "request_id": rid,
                "path": row.get("path"),
                "previous_status": status,
                "duplicate_group_key": group_key,
                "duplicate_of_request_id": canonical_id,
                "canonical_packet_path": canonical_path,
            }))

    if not to_update:
        return _blocked(
            tool_name,
            "no_supersedable_duplicates_found",
            {
                "selected_group_keys": sorted(selected_group_keys),
                "request_ids": sorted(request_ids),
                "skipped": skipped,
                "audit": _codex_queue_duplicate_audit(root, {"limit": 25}),
            },
        )

    reason = str(args.get("reason") or "Duplicate queued work created by no-receipt/retry/replay boundary; superseded without deleting evidence.").strip()
    receipt_payload = {
        "schema_id": "ion.chatgpt_browser_connector_codex_queue_duplicate_cleanup_receipt.v1",
        "action": tool_name,
        "status": "DUPLICATES_SUPERSEDED_NOT_DELETED",
        "created_at": now,
        "reason": reason,
        "idempotency_key": idempotency_key,
        "selected_group_keys": sorted(selected_group_keys),
        "selected_request_ids": sorted(request_ids),
        "superseded": [meta for _, _, meta in to_update],
        "skipped": skipped,
        "deleted_files": [],
        "accepted_state": False,
        "candidate_evidence_preserved": True,
        "production_authority": False,
        "live_execution_authority": False,
    }
    receipt_path = _write_connector_packet(root, "receipts/codex_queue_duplicate_cleanup", "supersede_duplicates", receipt_payload)
    receipt_rel = receipt_path.relative_to(root).as_posix()
    superseded_ids: list[str] = []
    for path, payload, meta in to_update:
        superseded_ids.append(str(meta.get("request_id") or ""))
        payload["previous_status"] = meta.get("previous_status")
        payload["status"] = "SUPERSEDED_DUPLICATE"
        payload["updated_at"] = now
        payload["superseded_at"] = now
        payload["superseded_by_tool"] = tool_name
        payload["superseded_reason"] = reason
        payload["duplicate_group_key"] = meta.get("duplicate_group_key")
        payload["duplicate_of_request_id"] = meta.get("duplicate_of_request_id")
        payload["canonical_packet_path"] = meta.get("canonical_packet_path")
        payload["cleanup_receipt_path"] = receipt_rel
        payload["blocked_but_preserved"] = True
        payload["accepted_state"] = False
        payload["salvage_route"] = "review_canonical_or_create_repair_packet"
        _write_json(path, payload)
    queue = _write_codex_work_queue_index(root)
    _record_codex_queue_duplicate_cleanup_idempotency(
        root,
        idempotency_key,
        receipt_path=receipt_path,
        superseded_request_ids=superseded_ids,
    )
    return _ok(
        tool_name,
        {
            "schema_id": "ion.chatgpt_browser_connector_codex_queue_supersede_duplicates_result.v1",
            "status": "DUPLICATES_SUPERSEDED_NOT_DELETED",
            "receipt_path": receipt_rel,
            "superseded_count": len(superseded_ids),
            "superseded_request_ids": superseded_ids,
            "skipped": skipped,
            "queue_path": CODEX_WORK_QUEUE_RELATIVE_PATH.as_posix(),
            "queue_duplicate_group_count": queue.get("duplicate_group_count"),
            "idempotent_replay": False,
            "duplicate_prevented": False,
            "production_authority": False,
            "live_execution_authority": False,
        },
        mutates_active_state=True,
    )



def _enqueue_connector_operator_message(root: Path, *, message: str, priority: int) -> dict[str, Any]:
    path = root / "ION/05_context/current/ACTIVE_OPERATOR_MESSAGE_QUEUE.json"
    queue = _read_json(path) or {
        "schema_id": "ion.operator_message_queue.v1",
        "created_at": _now(),
        "items": [],
        "production_authority": False,
        "live_execution_authority": False,
    }
    now = _now()
    item = {
        "id": f"opmsg_{now.replace(':', '').replace('+', 'Z')}_{_safe_slug(message)}",
        "created_at": now,
        "updated_at": now,
        "source": "chatgpt_browser_connector",
        "status": "pending",
        "priority": int(priority),
        "message": message,
        "classification": "chatgpt_browser_connector_queued_work",
        "classification_record": {
            "schema_id": "ion.chatgpt_browser_connector_operator_message_classification.v1",
            "classification": "chatgpt_browser_connector_queued_work",
            "production_authority": False,
            "live_execution_authority": False,
        },
        "consumed_at": None,
        "completed_at": None,
    }
    queue.setdefault("items", []).append(item)
    queue["updated_at"] = now
    _write_json(path, queue)
    return {
        "schema_id": "ion.operator_message_queue_result.v1",
        "verdict": "ION_OPERATOR_MESSAGE_ENQUEUED",
        "queue_path": "ION/05_context/current/ACTIVE_OPERATOR_MESSAGE_QUEUE.json",
        "item": item,
    }


def _coerce_timeout_seconds(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return DEFAULT_CODEX_TIMEOUT_SECONDS


def _load_timeout_policy_request(root: Path, request_path: str | None) -> dict[str, Any] | None:
    if not request_path:
        return None
    try:
        bounded = _bounded_connector_packet_path(root, request_path, subdir="codex_work_requests")
    except (ValueError, RuntimeError):
        return None
    if not bounded.exists():
        return None
    payload = _load_json_file(bounded)
    return payload if isinstance(payload, dict) else None


def _work_request_requires_workload_diff(payload: Mapping[str, Any]) -> bool:
    requested_by = str(payload.get("requested_by") or "").strip().lower()
    if requested_by == "ion_agent_invocation_broker":
        return True
    signal_text = " ".join([
        str(payload.get("request_kind") or ""),
        str(payload.get("objective") or ""),
        str(payload.get("agent_role") or ""),
        str(payload.get("agent_role_id") or ""),
        str(payload.get("agent_display_name") or ""),
    ]).lower()
    return any(hint in signal_text for hint in WORKLOAD_POLICY_HINTS)


def _return_contract_sections_for_work_request(payload: Mapping[str, Any]) -> list[str]:
    sections: list[str] = []
    configured = payload.get("return_contract_sections")
    if isinstance(configured, list):
        for item in configured:
            section = str(item or "").strip()
            if section.startswith("### ") and section not in sections:
                sections.append(section)
    if not sections:
        sections = list(BASE_RETURN_CONTRACT_SECTIONS)
    for required_section in RETURN_TEMPLATE_REQUIRED_SECTIONS:
        if required_section not in sections:
            sections.append(required_section)
    if operator_artifact_hygiene_required(payload) and OPERATOR_ARTIFACT_HYGIENE_SECTION not in sections:
        sections.append(OPERATOR_ARTIFACT_HYGIENE_SECTION)
    if ion_operational_posture_required(payload) and OPERATIONAL_POSTURE_SECTION not in sections:
        sections.append(OPERATIONAL_POSTURE_SECTION)
    return sections


def _section_heading_present(text: str, heading: str) -> bool:
    normalized = heading.strip().lower()
    for line in text.splitlines():
        if line.strip().lower() == normalized:
            return True
    return False


def _return_template_lint(text: str, required_reads: list[str]) -> dict[str, Any]:
    findings: list[str] = []
    for heading in RETURN_TEMPLATE_REQUIRED_SECTIONS:
        if not _section_heading_present(text, heading):
            findings.append(f"missing_required_section:{heading}")
    lower_text = text.lower()
    for required_field in ("template_id:", "action_id:", "result:"):
        if required_field not in lower_text:
            findings.append(f"missing_required_field:{required_field.rstrip(':')}")
    if "touched_paths:" not in lower_text and "no_touched_paths:" not in lower_text:
        findings.append("missing_required_field:touched_paths_or_no_touched_paths")
    return {
        "schema_id": "ion.return_template_lint_result.v1",
        "accepted": not findings,
        "findings": findings,
    }


def _carrier_intake_state(
    *,
    accepted: bool,
    content_returned: bool,
    return_template_valid: bool,
    context_accepted: bool,
    template_action_accepted: bool,
    workload_diff_accepted: bool,
    operator_hygiene_accepted: bool,
    operational_posture_accepted: bool,
) -> str:
    if accepted:
        return "carrier_intake_accepted"
    if not content_returned:
        return "no_content_returned"
    if not return_template_valid:
        return "content_returned_but_return_template_failed"
    if not context_accepted and template_action_accepted:
        return "template_action_proof_ok_context_failed"
    if not context_accepted:
        return "content_returned_but_context_proof_failed"
    if not template_action_accepted:
        return "content_returned_but_template_action_proof_failed"
    if not workload_diff_accepted:
        return "content_returned_but_workload_diff_failed"
    if not operator_hygiene_accepted:
        return "content_returned_but_operator_hygiene_failed"
    if not operational_posture_accepted:
        return "content_returned_but_operational_posture_failed"
    return "content_returned_but_unspecified_proof_failed"


def _task_return_automation_diagnosis(
    *,
    accepted: bool,
    return_template_valid: bool,
    context_result: Mapping[str, Any],
    template_result: Mapping[str, Any],
    workload_diff_accepted: bool,
    operator_hygiene_accepted: bool,
    operational_posture_accepted: bool,
    lint_findings: list[str],
    workload_diff_findings: list[str],
    operator_hygiene_findings: list[str],
    operational_posture_findings: list[str],
) -> dict[str, Any]:
    context_accepted = bool(context_result.get("accepted"))
    template_accepted = bool(template_result.get("accepted"))
    context_findings = [str(item) for item in context_result.get("findings", [])]
    template_findings = [str(item) for item in template_result.get("findings", [])]
    findings = (
        [str(item) for item in lint_findings]
        + context_findings
        + template_findings
        + [str(item) for item in workload_diff_findings]
        + [str(item) for item in operator_hygiene_findings]
        + [str(item) for item in operational_posture_findings]
    )
    if accepted:
        classification = "carrier_intake_ready"
        summary = "All automated return gates accepted the submitted task return."
        next_action = "automation_may_project_return_as_carrier_intake_ready"
    elif not return_template_valid:
        core_section_missing = any(
            finding in lint_findings
            for finding in (
                "missing_required_section:### CONTEXT PROOF",
                "missing_required_section:### TEMPLATE ACTION PROOF",
                "missing_required_section:### VALIDATION",
                "missing_required_section:### RESULT",
            )
        )
        if f"missing_required_section:{WORKLOAD_DIFF_SECTION}" in lint_findings and not core_section_missing:
            classification = "workload_diff_gate_blocked"
            summary = "Automation rejected carrier intake because the return is missing the required workload diff section."
            next_action = "rerun_or_repair_worker_return_with_required_workload_diff_section"
        elif any(item.startswith("missing_required_section:") for item in lint_findings):
            classification = "return_template_missing_required_section"
            summary = "Automation rejected carrier intake at the return-template gate."
            next_action = "rerun_or_repair_worker_return_to_satisfy_machine_return_contract"
        elif any(item.startswith("missing_required_field:") for item in lint_findings):
            classification = "return_template_missing_required_field"
            summary = "Automation rejected carrier intake at the return-template gate."
            next_action = "rerun_or_repair_worker_return_to_satisfy_machine_return_contract"
        elif any(item.startswith("missing_required_read_path:") for item in lint_findings):
            classification = "return_template_missing_required_read_path"
            summary = "Automation rejected carrier intake at the return-template gate."
            next_action = "rerun_or_repair_worker_return_to_satisfy_machine_return_contract"
        elif any(item.startswith("missing_read_evidence_near_required_read:") for item in lint_findings):
            classification = "return_template_required_read_evidence_missing"
            summary = "Automation rejected carrier intake at the return-template gate."
            next_action = "rerun_or_repair_worker_return_to_satisfy_machine_return_contract"
        else:
            classification = "return_template_invalid"
            summary = "Automation rejected carrier intake at the return-template gate."
            next_action = "rerun_or_repair_worker_return_to_satisfy_machine_return_contract"
    elif not context_accepted:
        classification = "context_proof_gate_blocked"
        summary = "Automation rejected carrier intake at the context-proof gate."
        next_action = "rerun_or_repair_worker_return_with_required_context_read_evidence"
    elif not template_accepted:
        classification = "template_action_gate_blocked"
        summary = "Automation rejected carrier intake at the template-action gate."
        next_action = "rerun_or_repair_worker_return_with_template_id_action_id_result_and_touched_paths"
    elif not workload_diff_accepted:
        classification = "workload_diff_gate_blocked"
        summary = "Automation rejected carrier intake because the work request requires a workload diff."
        next_action = "rerun_or_repair_worker_return_with_required_workload_diff_section"
    elif not operator_hygiene_accepted:
        classification = "operator_artifact_hygiene_gate_blocked"
        summary = "Automation rejected carrier intake because operator artifact hygiene proof is missing."
        next_action = "rerun_or_repair_worker_return_with_operator_artifact_hygiene_section"
    elif not operational_posture_accepted:
        classification = "ion_operational_posture_gate_blocked"
        summary = "Automation rejected carrier intake because ION operational posture proof is missing or invalid."
        next_action = "rerun_or_repair_worker_return_with_ion_operational_posture_section"
    else:
        classification = "proof_gate_blocked"
        summary = "Automation rejected carrier intake at an unspecified proof gate."
        next_action = "inspect_machine_findings_before_any_manual_receipt_or_wrapper"
    return {
        "schema_id": "ion.chatgpt_browser_connector_task_return_automation_diagnosis.v1",
        "classification": classification,
        "summary": summary,
        "next_action": next_action,
        "finding_count": len(findings),
        "findings": findings,
        "manual_ai_receipt_required": False,
        "automation_must_report": True,
    }


def _write_task_return_machine_receipt(
    root: Path,
    *,
    packet: Mapping[str, Any],
    task_return_packet_path: str,
    diagnosis: Mapping[str, Any],
    required_reads: list[str],
) -> str:
    receipt = {
        "schema_id": "ion.chatgpt_browser_connector_task_return_machine_receipt.v1",
        "event": "ion_submit_task_return_evaluated",
        "receipt_author": "kernel.ion_chatgpt_browser_mcp_connector_contract",
        "receipt_source": "automation",
        "manual_ai_authored": False,
        "task_return_packet_path": task_return_packet_path,
        "work_request_id": packet.get("work_request_id"),
        "work_request_path": packet.get("work_request_path"),
        "result": packet.get("result"),
        "accepted_for_carrier_intake": packet.get("accepted_for_carrier_intake"),
        "carrier_intake_state": packet.get("carrier_intake_state"),
        "content_returned": packet.get("content_returned"),
        "carrier_intake_only": packet.get("carrier_intake_only"),
        "product_state_accepted": packet.get("product_state_accepted"),
        "return_lane": packet.get("return_lane"),
        "alternate_worker_return": packet.get("alternate_worker_return"),
        "worker_identity_sha256": packet.get("worker_identity_sha256"),
        "return_source_contract": packet.get("return_source_contract"),
        "gate_results": {
            "return_template_valid": packet.get("return_template_valid"),
            "context_proof_accepted": (packet.get("context_proof_result") or {}).get("accepted")
            if isinstance(packet.get("context_proof_result"), Mapping)
            else None,
            "template_action_proof_accepted": (packet.get("template_action_proof_result") or {}).get("accepted")
            if isinstance(packet.get("template_action_proof_result"), Mapping)
            else None,
            "workload_diff_accepted": packet.get("workload_diff_accepted"),
            "operator_artifact_hygiene_accepted": packet.get("operator_artifact_hygiene_accepted"),
            "ion_operational_posture_accepted": packet.get("ion_operational_posture_accepted"),
        },
        "required_read_count": len(required_reads),
        "required_reads_sha256": _sha256_text("\n".join(required_reads)),
        "task_output_sha256": packet.get("task_output_sha256"),
        "diagnosis": dict(diagnosis),
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
    }
    path = _write_connector_packet(root, "task_return_machine_receipts", "task_return_machine_receipt", receipt)
    return path.relative_to(root).as_posix()


def _active_root_repair_allows_identity_repair(payload: Mapping[str, Any] | None) -> bool:
    if not isinstance(payload, Mapping):
        return False
    values = " ".join(
        str(payload.get(key) or "")
        for key in ("request_kind", "work_class", "route_family", "objective")
    ).lower()
    return "active_root_repair" in values or "active-root write repair" in values or "working capsule identity" in values


def _task_return_working_capsule_update(
    root: Path,
    *,
    request_payload: Mapping[str, Any] | None,
    accepted: bool,
    rel_return_path: str,
    machine_receipt_path: str,
) -> dict[str, Any]:
    if not isinstance(request_payload, Mapping):
        return {
            "schema_id": "ion.task_return_working_capsule_update.v1",
            "ok": True,
            "maintenance_attempted": False,
            "reason": "no_work_request_payload",
        }
    preflight = working_capsule_preflight(
        root,
        request_payload,
        active_root_repair_allowed=_active_root_repair_allows_identity_repair(request_payload),
    )
    identity = request_payload.get("working_capsule_identity")
    if accepted and isinstance(identity, Mapping) and preflight.get("ok"):
        maintenance = prepare_local_capsule_maintenance(
            root,
            identity,
            task_return_packet_path=rel_return_path,
            machine_receipt_path=machine_receipt_path,
            proof_status="RETURN_RECORDED_PROOF_ACCEPTED",
        )
        return {
            "schema_id": "ion.task_return_working_capsule_update.v1",
            "ok": bool(maintenance.get("ok")),
            "maintenance_attempted": True,
            "preflight": preflight,
            "maintenance": maintenance,
        }
    return {
        "schema_id": "ion.task_return_working_capsule_update.v1",
        "ok": bool(preflight.get("ok")),
        "maintenance_attempted": False,
        "preflight": preflight,
        "reason": "accepted_identity_required_for_maintenance",
        }


def _task_return_source_identity_sha256(identity: Mapping[str, Any]) -> str:
    return _sha256_text(json.dumps(dict(identity), sort_keys=True, separators=(",", ":")))


def _alternate_worker_provenance_receipt_path(root: Path, idempotency_key: str) -> Path:
    return root / ALTERNATE_WORKER_PROVENANCE_RECEIPT_DIR / f"{_safe_slug(idempotency_key)}.json"


def _native_subagent_transcript_receipt_path(root: Path, idempotency_key: str) -> Path:
    return root / NATIVE_SUBAGENT_TRANSCRIPT_RECEIPT_DIR / f"{_safe_slug(idempotency_key)}.json"


def _record_native_subagent_transcript(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    if str(args.get("confirmation") or "").strip() != NATIVE_SUBAGENT_TRANSCRIPT_CONFIRMATION:
        return _blocked("ion_record_native_subagent_transcript", "native_subagent_transcript_confirmation_required")
    idempotency_key = str(args.get("idempotency_key") or "").strip()
    if not idempotency_key:
        return _blocked("ion_record_native_subagent_transcript", "idempotency_key_required")
    subagent_id = str(args.get("subagent_id") or "").strip()
    worker_id = str(args.get("worker_id") or "").strip()
    source_ref = str(args.get("source_ref") or "").strip()
    work_request_path = str(args.get("work_request_path") or "").strip()
    status = str(args.get("status") or "").strip().lower()
    worker_output_text = str(args.get("worker_output_text") or "")
    claim_boundary = str(args.get("claim_boundary") or "").strip()
    if not subagent_id or not worker_id or not source_ref or not work_request_path or not status:
        return _blocked("ion_record_native_subagent_transcript", "subagent_id_worker_id_source_ref_work_request_path_status_required")
    if source_ref != f"subagent:{subagent_id}":
        return _blocked("ion_record_native_subagent_transcript", "source_ref_must_match_subagent_id")
    if not worker_output_text.strip():
        return _blocked("ion_record_native_subagent_transcript", "worker_output_text_required")
    if claim_boundary != "carrier_intake_not_product_state":
        return _blocked("ion_record_native_subagent_transcript", "claim_boundary_required")
    worker_output_sha256 = _sha256_text(worker_output_text)
    receipt_path = _native_subagent_transcript_receipt_path(root, idempotency_key)
    if receipt_path.exists():
        existing = _load_json_file(receipt_path)
        return _ok(
            "ion_record_native_subagent_transcript",
            {
                "schema_id": "ion.native_subagent_transcript_receipt_result.v0_1",
                "idempotent_replay": True,
                "receipt_path": receipt_path.relative_to(root).as_posix(),
                "subagent_id": existing.get("subagent_id"),
                "worker_id": existing.get("worker_id"),
                "source_ref": existing.get("source_ref"),
                "worker_output_sha256": existing.get("worker_output_sha256"),
                "native_subagent_transcript_verified": existing.get("native_subagent_transcript_verified"),
                "product_state_accepted": False,
            },
            mutates_active_state=False,
        )
    native_verified = status == "completed"
    receipt = {
        "schema_id": "ion.native_subagent_transcript_receipt.v0_1",
        "created_at": _now(),
        "receipt_source": "kernel.ion_chatgpt_browser_mcp_connector_contract",
        "receipt_author": "ion_record_native_subagent_transcript",
        "idempotency_key": idempotency_key,
        "subagent_id": subagent_id,
        "worker_id": worker_id,
        "source_ref": source_ref,
        "work_request_path": work_request_path,
        "status": status,
        "worker_output_sha256": worker_output_sha256,
        "worker_output_preview": worker_output_text[:2000],
        "native_tool_result_observed_by": str(args.get("observed_by") or "lead_codex_parent_session").strip()[:256],
        "native_tool_result_observed": True,
        "native_subagent_transcript_verified": native_verified,
        "native_subagent_transcript_verification_scope": "native_multi_agent_tool_result_observed_by_lead_codex",
        "filesystem_transcript_verified": False,
        "filesystem_transcript_blocker": "multi_agent_v1_result_received_via_tool_callback_not_local_transcript_file",
        "carrier_intake_only": True,
        "claim_boundary": claim_boundary,
        "product_state_accepted": False,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }
    _write_json(receipt_path, receipt)
    return _ok(
        "ion_record_native_subagent_transcript",
        {
            "schema_id": "ion.native_subagent_transcript_receipt_result.v0_1",
            "idempotent_replay": False,
            "receipt_path": receipt_path.relative_to(root).as_posix(),
            "subagent_id": subagent_id,
            "worker_id": worker_id,
            "source_ref": source_ref,
            "worker_output_sha256": worker_output_sha256,
            "native_subagent_transcript_verified": native_verified,
            "filesystem_transcript_verified": False,
            "product_state_accepted": False,
        },
        mutates_active_state=True,
    )


def _record_alternate_worker_provenance(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    if str(args.get("confirmation") or "").strip() != ALTERNATE_WORKER_PROVENANCE_CONFIRMATION:
        return _blocked("ion_record_alternate_worker_provenance", "alternate_worker_provenance_confirmation_required")
    idempotency_key = str(args.get("idempotency_key") or "").strip()
    if not idempotency_key:
        return _blocked("ion_record_alternate_worker_provenance", "idempotency_key_required")
    identity_raw = args.get("alternate_worker_identity") or args.get("worker_identity")
    provenance_raw = args.get("alternate_worker_provenance")
    if not isinstance(identity_raw, Mapping):
        return _blocked("ion_record_alternate_worker_provenance", "alternate_worker_identity_object_required")
    if not isinstance(provenance_raw, Mapping):
        return _blocked("ion_record_alternate_worker_provenance", "alternate_worker_provenance_object_required")
    identity = {
        str(key): str(value or "").strip()[:512]
        for key, value in identity_raw.items()
        if str(value or "").strip()
    }
    provenance = {
        str(key): str(value or "").strip()[:512]
        for key, value in provenance_raw.items()
        if str(value or "").strip()
    }
    missing_identity = [
        field
        for field in ALTERNATE_WORKER_IDENTITY_REQUIRED_FIELDS
        if not identity.get(field)
    ]
    missing_provenance = [
        field
        for field in ALTERNATE_WORKER_PROVENANCE_REQUIRED_FIELDS
        if not provenance.get(field)
    ]
    if missing_identity:
        return _blocked("ion_record_alternate_worker_provenance", "alternate_worker_identity_missing_required_fields:" + ",".join(missing_identity))
    if missing_provenance:
        return _blocked("ion_record_alternate_worker_provenance", "alternate_worker_provenance_missing_required_fields:" + ",".join(missing_provenance))
    if provenance.get("worker_id") != identity.get("worker_id"):
        return _blocked("ion_record_alternate_worker_provenance", "alternate_worker_provenance_worker_id_mismatch")
    if provenance.get("source_ref") != identity.get("source_ref"):
        return _blocked("ion_record_alternate_worker_provenance", "alternate_worker_provenance_source_ref_mismatch")
    task_output_sha256 = str(args.get("worker_output_sha256") or provenance.get("worker_output_sha256") or "").strip()
    if not task_output_sha256:
        return _blocked("ion_record_alternate_worker_provenance", "worker_output_sha256_required")
    if provenance.get("worker_output_sha256") != task_output_sha256:
        return _blocked("ion_record_alternate_worker_provenance", "alternate_worker_provenance_worker_output_sha256_mismatch")
    if provenance.get("claim_boundary") != "carrier_intake_not_product_state":
        return _blocked("ion_record_alternate_worker_provenance", "alternate_worker_provenance_claim_boundary_required")
    identity_sha = _task_return_source_identity_sha256(identity)
    provenance_sha = _task_return_source_identity_sha256(provenance)
    native_subagent_transcript_receipt_rel = str(args.get("native_subagent_transcript_receipt_path") or "").strip()
    native_subagent_transcript_verified = False
    native_subagent_transcript_payload: dict[str, Any] | None = None
    if native_subagent_transcript_receipt_rel:
        try:
            native_receipt_path = _safe_rel_path(root, native_subagent_transcript_receipt_rel)
        except (ValueError, RuntimeError):
            return _blocked("ion_record_alternate_worker_provenance", "native_subagent_transcript_receipt_path_invalid")
        allowed_native_root = (root / NATIVE_SUBAGENT_TRANSCRIPT_RECEIPT_DIR).resolve()
        if not _is_under(native_receipt_path, allowed_native_root):
            return _blocked("ion_record_alternate_worker_provenance", "native_subagent_transcript_receipt_path_not_allowed")
        if not native_receipt_path.exists():
            return _blocked("ion_record_alternate_worker_provenance", "native_subagent_transcript_receipt_missing")
        native_subagent_transcript_payload = _load_json_file(native_receipt_path)
        if native_subagent_transcript_payload.get("worker_id") != identity.get("worker_id"):
            return _blocked("ion_record_alternate_worker_provenance", "native_subagent_transcript_worker_id_mismatch")
        if native_subagent_transcript_payload.get("source_ref") != identity.get("source_ref"):
            return _blocked("ion_record_alternate_worker_provenance", "native_subagent_transcript_source_ref_mismatch")
        if native_subagent_transcript_payload.get("work_request_path") != provenance.get("work_request_path"):
            return _blocked("ion_record_alternate_worker_provenance", "native_subagent_transcript_work_request_path_mismatch")
        if native_subagent_transcript_payload.get("worker_output_sha256") != task_output_sha256:
            return _blocked("ion_record_alternate_worker_provenance", "native_subagent_transcript_worker_output_sha256_mismatch")
        native_subagent_transcript_verified = native_subagent_transcript_payload.get("native_subagent_transcript_verified") is True
        if not native_subagent_transcript_verified:
            return _blocked("ion_record_alternate_worker_provenance", "native_subagent_transcript_not_verified")
    receipt_path = _alternate_worker_provenance_receipt_path(root, idempotency_key)
    if receipt_path.exists():
        existing = _load_json_file(receipt_path)
        return _ok(
            "ion_record_alternate_worker_provenance",
            {
                "schema_id": "ion.alternate_worker_provenance_receipt_result.v0_1",
                "idempotent_replay": True,
                "receipt_path": receipt_path.relative_to(root).as_posix(),
                "identity_sha256": existing.get("identity_sha256"),
                "provenance_sha256": existing.get("provenance_sha256"),
                "worker_output_sha256": existing.get("worker_output_sha256"),
                "verification_scope": existing.get("verification_scope"),
                "product_state_accepted": False,
            },
            mutates_active_state=False,
        )
    receipt = {
        "schema_id": "ion.alternate_worker_provenance_receipt.v0_1",
        "created_at": _now(),
        "receipt_source": "kernel.ion_chatgpt_browser_mcp_connector_contract",
        "receipt_author": "ion_record_alternate_worker_provenance",
        "idempotency_key": idempotency_key,
        "work_request_path": provenance.get("work_request_path"),
        "worker_id": identity.get("worker_id"),
        "source_kind": provenance.get("source_kind"),
        "source_ref": identity.get("source_ref"),
        "identity": identity,
        "provenance": provenance,
        "identity_sha256": identity_sha,
        "provenance_sha256": provenance_sha,
        "worker_output_sha256": task_output_sha256,
        "verification_scope": "durable_parent_observed_subagent_provenance_receipt",
        "native_subagent_transcript_receipt_path": native_subagent_transcript_receipt_rel or None,
        "native_subagent_transcript_verified": native_subagent_transcript_verified,
        "native_subagent_transcript_verification_scope": (
            native_subagent_transcript_payload.get("native_subagent_transcript_verification_scope")
            if native_subagent_transcript_payload
            else None
        ),
        "machine_verified_fields": [
            "work_request_path",
            "worker_id",
            "source_ref",
            "worker_output_sha256",
            "claim_boundary",
        ],
        "native_subagent_transcript_blocker": None if native_subagent_transcript_verified else "no_native_subagent_transcript_receipt_supplied",
        "carrier_intake_only": True,
        "product_state_accepted": False,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }
    _write_json(receipt_path, receipt)
    return _ok(
        "ion_record_alternate_worker_provenance",
        {
            "schema_id": "ion.alternate_worker_provenance_receipt_result.v0_1",
            "idempotent_replay": False,
            "receipt_path": receipt_path.relative_to(root).as_posix(),
            "identity_sha256": identity_sha,
            "provenance_sha256": provenance_sha,
            "worker_output_sha256": task_output_sha256,
            "verification_scope": receipt["verification_scope"],
            "native_subagent_transcript_verified": native_subagent_transcript_verified,
            "native_subagent_transcript_receipt_path": native_subagent_transcript_receipt_rel or None,
            "product_state_accepted": False,
        },
        mutates_active_state=True,
    )


def _task_return_source_contract(
    *,
    root: Path,
    tool_name: str,
    args: Mapping[str, Any],
    request_payload: Mapping[str, Any] | None,
    work_request_path: str,
    work_request_id: str,
    task_output_sha256: str,
) -> tuple[dict[str, Any] | None, str | None]:
    raw_lane = str(args.get("return_lane") or args.get("worker_return_lane") or "").strip()
    alternate_fields_present = (
        bool(args.get("alternate_worker_return"))
        or bool(args.get("alternate_worker_identity"))
        or bool(args.get("worker_identity"))
        or bool(args.get("alternate_worker_provenance"))
        or raw_lane == ALTERNATE_WORKER_RETURN_LANE
    )
    alternate_requested = tool_name == "ion_submit_alternate_worker_return"
    if tool_name == "ion_submit_task_return" and alternate_fields_present:
        return None, "alternate_worker_return_requires_dedicated_tool"
    if not alternate_requested:
        return {
            "schema_id": "ion.chatgpt_browser_connector_task_return_source_contract.v0_1",
            "return_lane": DEFAULT_TASK_RETURN_LANE,
            "alternate_worker_return": False,
            "identity_required": False,
            "work_request_id": work_request_id or None,
            "work_request_path": work_request_path or None,
            "parent_session_relay_is_worker_return": False,
            "failed_cli_log_is_worker_return": False,
            "carrier_session_bridge_is_worker_return": False,
            "product_state_accepted": False,
        }, None
    if not work_request_path:
        return None, "alternate_worker_return_work_request_path_required"
    if str(args.get("confirmation") or "").strip() != ALTERNATE_WORKER_RETURN_CONFIRMATION:
        return None, "alternate_worker_return_confirmation_required"
    identity_raw = args.get("alternate_worker_identity")
    if identity_raw is None:
        identity_raw = args.get("worker_identity")
    if not isinstance(identity_raw, Mapping):
        return None, "alternate_worker_identity_object_required"
    missing = [
        field
        for field in ALTERNATE_WORKER_IDENTITY_REQUIRED_FIELDS
        if not str(identity_raw.get(field) or "").strip()
    ]
    if missing:
        return None, "alternate_worker_identity_missing_required_fields:" + ",".join(missing)
    identity: dict[str, Any] = {}
    for field in ALTERNATE_WORKER_IDENTITY_REQUIRED_FIELDS + ALTERNATE_WORKER_IDENTITY_OPTIONAL_FIELDS:
        value = str(identity_raw.get(field) or "").strip()
        if value:
            identity[field] = value[:512]
    combined_identity = " ".join(str(value).lower() for value in identity.values())
    forbidden_hits = sorted(
        marker
        for marker in ALTERNATE_WORKER_FORBIDDEN_SOURCE_MARKERS
        if marker in combined_identity
    )
    if forbidden_hits:
        return None, "alternate_worker_identity_forbidden_source_class:" + forbidden_hits[0]
    provenance_raw = args.get("alternate_worker_provenance")
    if not isinstance(provenance_raw, Mapping):
        return None, "alternate_worker_provenance_object_required"
    provenance_missing = [
        field
        for field in ALTERNATE_WORKER_PROVENANCE_REQUIRED_FIELDS
        if not str(provenance_raw.get(field) or "").strip()
    ]
    if provenance_missing:
        return None, "alternate_worker_provenance_missing_required_fields:" + ",".join(provenance_missing)
    provenance: dict[str, Any] = {
        key: str(value or "").strip()[:512]
        for key, value in provenance_raw.items()
        if str(value or "").strip()
    }
    source_kind = str(provenance.get("source_kind") or "").strip()
    if source_kind not in ALTERNATE_WORKER_ALLOWED_SOURCE_KINDS:
        return None, "alternate_worker_provenance_source_kind_not_allowed"
    if provenance.get("work_request_path") != work_request_path:
        return None, "alternate_worker_provenance_work_request_path_mismatch"
    if provenance.get("worker_id") != identity.get("worker_id"):
        return None, "alternate_worker_provenance_worker_id_mismatch"
    if provenance.get("source_ref") != identity.get("source_ref"):
        return None, "alternate_worker_provenance_source_ref_mismatch"
    if provenance.get("worker_output_sha256") != task_output_sha256:
        return None, "alternate_worker_provenance_worker_output_sha256_mismatch"
    if provenance.get("claim_boundary") != "carrier_intake_not_product_state":
        return None, "alternate_worker_provenance_claim_boundary_required"
    combined_provenance = " ".join(str(value).lower() for value in provenance.values())
    provenance_forbidden_hits = sorted(
        marker
        for marker in ALTERNATE_WORKER_FORBIDDEN_SOURCE_MARKERS
        if marker in combined_provenance
    )
    if provenance_forbidden_hits:
        return None, "alternate_worker_provenance_forbidden_source_class:" + provenance_forbidden_hits[0]
    request_id = work_request_id
    if not request_id and isinstance(request_payload, Mapping):
        request_id = str(request_payload.get("request_id") or "").strip()
    identity_sha = _task_return_source_identity_sha256(identity)
    provenance_sha = _task_return_source_identity_sha256(provenance)
    provenance_receipt_rel = str(args.get("alternate_worker_provenance_receipt_path") or "").strip()
    require_provenance_receipt = bool(args.get("require_provenance_receipt"))
    provenance_verification_state = "parent_observed_only"
    provenance_receipt_payload: dict[str, Any] | None = None
    if provenance_receipt_rel:
        try:
            provenance_receipt_path = _safe_rel_path(root, provenance_receipt_rel)
        except (ValueError, RuntimeError):
            return None, "alternate_worker_provenance_receipt_path_invalid"
        allowed_root = (root / ALTERNATE_WORKER_PROVENANCE_RECEIPT_DIR).resolve()
        if not _is_under(provenance_receipt_path, allowed_root):
            return None, "alternate_worker_provenance_receipt_path_not_allowed"
        if not provenance_receipt_path.exists():
            return None, "alternate_worker_provenance_receipt_missing"
        provenance_receipt_payload = _load_json_file(provenance_receipt_path)
        if provenance_receipt_payload.get("identity_sha256") != identity_sha:
            return None, "alternate_worker_provenance_receipt_identity_sha256_mismatch"
        if provenance_receipt_payload.get("provenance_sha256") != provenance_sha:
            return None, "alternate_worker_provenance_receipt_provenance_sha256_mismatch"
        if provenance_receipt_payload.get("worker_output_sha256") != task_output_sha256:
            return None, "alternate_worker_provenance_receipt_worker_output_sha256_mismatch"
        if provenance_receipt_payload.get("work_request_path") != work_request_path:
            return None, "alternate_worker_provenance_receipt_work_request_path_mismatch"
        provenance_verification_state = "durable_receipt_verified"
    elif require_provenance_receipt:
        return None, "alternate_worker_provenance_receipt_required"
    return {
        "schema_id": "ion.chatgpt_browser_connector_task_return_source_contract.v0_1",
        "return_lane": ALTERNATE_WORKER_RETURN_LANE,
        "alternate_worker_return": True,
        "identity_required": True,
        "identity": identity,
        "identity_sha256": identity_sha,
        "provenance": provenance,
        "provenance_sha256": provenance_sha,
        "provenance_verification_state": provenance_verification_state,
        "provenance_receipt_path": provenance_receipt_rel or None,
        "native_subagent_transcript_verified": bool(
            provenance_receipt_payload
            and provenance_receipt_payload.get("native_subagent_transcript_verified") is True
        ),
        "native_subagent_transcript_receipt_path": (
            provenance_receipt_payload.get("native_subagent_transcript_receipt_path")
            if provenance_receipt_payload
            else None
        ),
        "required_identity_fields": list(ALTERNATE_WORKER_IDENTITY_REQUIRED_FIELDS),
        "required_provenance_fields": list(ALTERNATE_WORKER_PROVENANCE_REQUIRED_FIELDS),
        "allowed_source_kinds": sorted(ALTERNATE_WORKER_ALLOWED_SOURCE_KINDS),
        "forbidden_source_markers": sorted(ALTERNATE_WORKER_FORBIDDEN_SOURCE_MARKERS),
        "work_request_id": request_id or None,
        "work_request_path": work_request_path or None,
        "source_bound_to_work_request": bool(work_request_path),
        "parent_session_relay_is_worker_return": False,
        "failed_cli_log_is_worker_return": False,
        "carrier_session_bridge_is_worker_return": False,
        "product_state_accepted": False,
    }, None


def _existing_accepted_task_return_for_idempotency(
    root: Path,
    *,
    work_request_path: str | None,
    work_request_id: str | None,
    task_output_sha256: str,
    required_reads: list[str],
    return_lane: str | None = None,
    worker_identity_sha256: str | None = None,
) -> dict[str, Any] | None:
    required_reads_sha256 = _sha256_text("\n".join(required_reads))
    for item in sorted(
        _task_returns_for_request(root, work_request_path, work_request_id),
        key=_task_return_sort_key,
        reverse=True,
    ):
        packet = item.get("packet") if isinstance(item.get("packet"), Mapping) else {}
        if packet.get("accepted_for_carrier_intake") is not True:
            continue
        if return_lane:
            packet_lane = str(packet.get("return_lane") or DEFAULT_TASK_RETURN_LANE)
            if packet_lane != return_lane:
                continue
            if return_lane == ALTERNATE_WORKER_RETURN_LANE:
                packet_identity_sha = str(packet.get("worker_identity_sha256") or "")
                if not worker_identity_sha256 or packet_identity_sha != worker_identity_sha256:
                    continue
        if packet.get("task_output_sha256") != task_output_sha256:
            continue
        receipt_rel = str(packet.get("machine_receipt_path") or "").strip()
        if not receipt_rel:
            continue
        try:
            receipt_path = _safe_rel_path(root, receipt_rel)
        except ValueError:
            continue
        if not receipt_path.exists():
            continue
        receipt = _load_json_file(receipt_path)
        if receipt.get("required_reads_sha256") != required_reads_sha256:
            continue
        return {
            "packet_path": str(item.get("path") or ""),
            "packet": packet,
            "machine_receipt_path": receipt_rel,
            "machine_receipt": receipt,
            "required_reads_sha256": required_reads_sha256,
        }
    return None


def _requires_extended_timeout(tool_name: str, args: Mapping[str, Any], request_payload: Mapping[str, Any] | None) -> bool:
    if tool_name in {"ion_agent_invoke", "ion_swarm_step_once"}:
        return True
    if request_payload and _work_request_requires_workload_diff(request_payload):
        return True
    signal_text = " ".join([
        str(args.get("request_kind") or ""),
        str(args.get("objective") or ""),
        str(args.get("agent") or ""),
    ]).lower()
    return any(hint in signal_text for hint in WORKLOAD_POLICY_HINTS)


def _normalized_timeout_for_tool(root: Path, tool_name: str, args: Mapping[str, Any]) -> int:
    raw = args.get("max_runtime_seconds")
    if raw is None:
        raw = args.get("timeout_seconds")
    timeout = _coerce_timeout_seconds(raw)
    request_payload = _load_timeout_policy_request(root, str(args.get("request_path") or "").strip() or None)
    if _requires_extended_timeout(tool_name, args, request_payload):
        timeout = max(timeout, MIN_COMPLEX_WORKLOAD_TIMEOUT_SECONDS)
    timeout = min(timeout, MAX_CODEX_TIMEOUT_SECONDS)
    timeout = max(timeout, 30)
    return timeout


def _evaluate_task_return_packet(root: Path, args: Mapping[str, Any], *, tool_name: str = "ion_submit_task_return") -> dict[str, Any]:
    text = str(args.get("task_output_text") or "")
    receipt = args.get("context_receipt")
    if not isinstance(receipt, Mapping):
        return _blocked(tool_name, "context_receipt_object_required")
    work_request_path = str(args.get("work_request_path") or "").strip()
    work_request_id = str(args.get("work_request_id") or "").strip()
    request_payload: dict[str, Any] | None = None
    request_path: Path | None = None
    if work_request_path:
        try:
            request_path = _bounded_connector_packet_path(root, work_request_path, subdir="codex_work_requests")
        except (ValueError, RuntimeError):
            return _blocked(tool_name, "work_request_path_not_bounded_to_codex_work_requests")
        if not request_path.exists():
            return _blocked(tool_name, "work_request_path_missing")
        request_payload = _load_json_file(request_path)
        work_request_id = work_request_id or str(request_payload.get("request_id") or "")
    task_output_sha256 = _sha256_text(text)
    source_contract, source_contract_finding = _task_return_source_contract(
        root=root,
        tool_name=tool_name,
        args=args,
        request_payload=request_payload,
        work_request_path=work_request_path,
        work_request_id=work_request_id,
        task_output_sha256=task_output_sha256,
    )
    if source_contract_finding:
        return _blocked(tool_name, source_contract_finding)
    required_reads = []
    receipt_reads = receipt.get("required_context_reads")
    if isinstance(receipt_reads, list):
        for item in receipt_reads:
            if isinstance(item, Mapping) and item.get("required") is True and str(item.get("kind") or "") == "file":
                read_path = str(item.get("path") or "").strip()
                if read_path:
                    required_reads.append(read_path)
    lint_result = _return_template_lint(text, required_reads)
    return_template_valid = bool(lint_result.get("accepted"))
    context_result = evaluate_context_proof_return(receipt=receipt, task_output=text)
    template_result = evaluate_template_action_proof(worker_output=text)
    required_sections = _return_contract_sections_for_work_request(request_payload or {})
    workload_diff_required = WORKLOAD_DIFF_SECTION in required_sections
    workload_diff_present = _section_heading_present(text, WORKLOAD_DIFF_SECTION)
    workload_diff_accepted = (not workload_diff_required) or workload_diff_present
    operator_hygiene_required = OPERATOR_ARTIFACT_HYGIENE_SECTION in required_sections
    operator_hygiene_present = _section_heading_present(text, OPERATOR_ARTIFACT_HYGIENE_SECTION)
    operator_hygiene_accepted = (not operator_hygiene_required) or operator_hygiene_present
    operational_posture_required = OPERATIONAL_POSTURE_SECTION in required_sections
    operational_posture_result = (
        evaluate_operational_posture_proof(text)
        if operational_posture_required
        else {"schema_id": "ion.codex_operational_posture_proof.v0_1", "accepted": True, "findings": []}
    )
    operational_posture_accepted = (not operational_posture_required) or bool(operational_posture_result.get("accepted"))
    accepted = (
        return_template_valid
        and bool(context_result.get("accepted"))
        and bool(template_result.get("accepted"))
        and workload_diff_accepted
        and operator_hygiene_accepted
        and operational_posture_accepted
    )
    workload_diff_findings: list[str] = []
    if workload_diff_required and not workload_diff_present:
        workload_diff_findings.append("missing_required_section:### WORKLOAD DIFF")
    operator_hygiene_findings: list[str] = []
    if operator_hygiene_required and not operator_hygiene_present:
        operator_hygiene_findings.append(f"missing_required_section:{OPERATOR_ARTIFACT_HYGIENE_SECTION}")
    operational_posture_findings = list(operational_posture_result.get("findings", []))
    lint_findings = list(lint_result.get("findings", []))
    content_returned = bool(text.strip())
    carrier_intake_state = _carrier_intake_state(
        accepted=accepted,
        content_returned=content_returned,
        return_template_valid=return_template_valid,
        context_accepted=bool(context_result.get("accepted")),
        template_action_accepted=bool(template_result.get("accepted")),
        workload_diff_accepted=workload_diff_accepted,
        operator_hygiene_accepted=operator_hygiene_accepted,
        operational_posture_accepted=operational_posture_accepted,
    )
    automation_diagnosis = _task_return_automation_diagnosis(
        accepted=accepted,
        return_template_valid=return_template_valid,
        context_result=context_result,
        template_result=template_result,
        workload_diff_accepted=workload_diff_accepted,
        operator_hygiene_accepted=operator_hygiene_accepted,
        operational_posture_accepted=operational_posture_accepted,
        lint_findings=lint_findings,
        workload_diff_findings=workload_diff_findings,
        operator_hygiene_findings=operator_hygiene_findings,
        operational_posture_findings=operational_posture_findings,
    )
    result_status = "RECORDED_FOR_CARRIER_INTAKE" if accepted else ("RETURN_TEMPLATE_INVALID" if not return_template_valid else "BLOCKED_BY_PROOF_GATE")
    packet = {
        "schema_id": "ion.chatgpt_browser_connector_task_return_packet.v1",
        "accepted_for_carrier_intake": accepted,
        "carrier_intake_state": carrier_intake_state,
        "content_returned": content_returned,
        "carrier_intake_only": True,
        "product_state_accepted": False,
        "return_lane": source_contract.get("return_lane") if source_contract else DEFAULT_TASK_RETURN_LANE,
        "alternate_worker_return": bool(source_contract.get("alternate_worker_return")) if source_contract else False,
        "return_source_contract": source_contract,
        "worker_identity_sha256": source_contract.get("identity_sha256") if source_contract else None,
        "parent_session_relay_is_worker_return": False,
        "failed_cli_log_is_worker_return": False,
        "carrier_session_bridge_is_worker_return": False,
        "return_template_valid": return_template_valid,
        "return_template_lint_result": lint_result,
        "blocked_but_preserved": not accepted,
        "salvage_route": "ION/05_context/current/chatgpt_connector/task_returns",
        "raw_latest_return_md_expected_from_run_packet": True,
        "work_request_id": work_request_id or None,
        "work_request_path": work_request_path or None,
        "context_proof_result": context_result,
        "template_action_proof_result": template_result,
        "workload_diff_required": workload_diff_required,
        "workload_diff_present": workload_diff_present,
        "workload_diff_accepted": workload_diff_accepted,
        "operator_artifact_hygiene_required": operator_hygiene_required,
        "operator_artifact_hygiene_present": operator_hygiene_present,
        "operator_artifact_hygiene_accepted": operator_hygiene_accepted,
        "operator_artifact_hygiene_findings": operator_hygiene_findings,
        "ion_operational_posture_required": operational_posture_required,
        "ion_operational_posture_accepted": operational_posture_accepted,
        "ion_operational_posture_result": operational_posture_result,
        "task_output_sha256": task_output_sha256,
        "task_output_preview": text[:1200],
        "automation_diagnosis": automation_diagnosis,
        "manual_ai_receipt_required": False,
        "result": result_status,
    }
    existing_return = _existing_accepted_task_return_for_idempotency(
        root,
        work_request_path=work_request_path or None,
        work_request_id=work_request_id or None,
        task_output_sha256=str(packet.get("task_output_sha256") or ""),
        required_reads=required_reads,
        return_lane=str(packet.get("return_lane") or DEFAULT_TASK_RETURN_LANE),
        worker_identity_sha256=str(packet.get("worker_identity_sha256") or "") or None,
    )
    if existing_return:
        rel_return_path = str(existing_return.get("packet_path") or "")
        machine_receipt_path = str(existing_return.get("machine_receipt_path") or "")
        existing_packet = existing_return.get("packet") if isinstance(existing_return.get("packet"), Mapping) else {}
        existing_receipt = (
            existing_return.get("machine_receipt")
            if isinstance(existing_return.get("machine_receipt"), Mapping)
            else {}
        )
        existing_diagnosis = (
            existing_packet.get("automation_diagnosis")
            if isinstance(existing_packet.get("automation_diagnosis"), Mapping)
            else automation_diagnosis
        )
        existing_context_result = (
            existing_packet.get("context_proof_result")
            if isinstance(existing_packet.get("context_proof_result"), Mapping)
            else {}
        )
        existing_template_result = (
            existing_packet.get("template_action_proof_result")
            if isinstance(existing_packet.get("template_action_proof_result"), Mapping)
            else {}
        )
        context_proof_accepted = existing_context_result.get("accepted", context_result.get("accepted"))
        template_action_proof_accepted = existing_template_result.get("accepted", template_result.get("accepted"))
        work_request_updated = False
        if request_path and request_payload is not None and rel_return_path:
            paths = list(request_payload.get("return_packet_paths") or [])
            if rel_return_path not in paths:
                paths.append(rel_return_path)
            request_payload["return_packet_paths"] = paths
            request_payload["latest_return_packet_path"] = rel_return_path
            request_payload["status"] = "RETURN_RECORDED_PROOF_ACCEPTED"
            request_payload.pop("failure_classification", None)
            request_payload["updated_at"] = _now()
            request_payload["latest_context_proof_accepted"] = context_proof_accepted
            request_payload["latest_template_action_proof_accepted"] = template_action_proof_accepted
            request_payload["latest_task_return_machine_receipt_path"] = machine_receipt_path
            request_payload["latest_task_return_automation_diagnosis"] = existing_diagnosis
            request_payload["latest_task_return_carrier_intake_state"] = existing_packet.get("carrier_intake_state", "carrier_intake_accepted")
            request_payload["latest_task_return_product_state_accepted"] = False
            request_payload["latest_task_return_lane"] = existing_packet.get("return_lane", source_contract.get("return_lane") if source_contract else DEFAULT_TASK_RETURN_LANE)
            request_payload["latest_task_return_source_contract"] = existing_packet.get("return_source_contract", source_contract)
            request_payload["latest_task_return_dedupe"] = {
                "deduped_existing_return_packet_path": rel_return_path,
                "deduped_existing_machine_receipt_path": machine_receipt_path,
                "task_output_sha256": packet.get("task_output_sha256"),
                "required_reads_sha256": existing_return.get("required_reads_sha256"),
            }
            working_capsule_update = _task_return_working_capsule_update(
                root,
                request_payload=request_payload,
                accepted=True,
                rel_return_path=rel_return_path,
                machine_receipt_path=machine_receipt_path,
            )
            request_payload["latest_working_capsule_preflight"] = working_capsule_update.get("preflight")
            if working_capsule_update.get("maintenance_attempted"):
                request_payload["latest_working_capsule_maintenance"] = working_capsule_update.get("maintenance")
            _write_json(request_path, request_payload)
            work_request_updated = True
        queue = _write_codex_work_queue_index(root)
        return _ok(
            "ion_submit_task_return",
            {
                "accepted_for_carrier_intake": True,
                "carrier_intake_state": existing_packet.get("carrier_intake_state", "carrier_intake_accepted"),
                "carrier_intake_only": True,
                "product_state_accepted": False,
                "content_returned": existing_packet.get("content_returned", True),
                "packet_path": rel_return_path,
                "machine_receipt_path": machine_receipt_path,
                "return_lane": existing_packet.get("return_lane", source_contract.get("return_lane") if source_contract else DEFAULT_TASK_RETURN_LANE),
                "alternate_worker_return": existing_packet.get("alternate_worker_return", False),
                "return_source_contract": existing_packet.get("return_source_contract", source_contract),
                "worker_identity_sha256": existing_packet.get("worker_identity_sha256"),
                "automation_diagnosis": existing_diagnosis,
                "work_request_id": work_request_id or None,
                "work_request_path": work_request_path or None,
                "work_request_updated": work_request_updated,
                "codex_work_queue_path": CODEX_WORK_QUEUE_RELATIVE_PATH.as_posix(),
                "codex_work_queue_request_count": queue["request_count"],
                "return_template_valid": existing_packet.get("return_template_valid", return_template_valid),
                "context_proof_accepted": context_proof_accepted,
                "template_action_proof_accepted": template_action_proof_accepted,
                "workload_diff_required": existing_packet.get("workload_diff_required", workload_diff_required),
                "workload_diff_present": existing_packet.get("workload_diff_present", workload_diff_present),
                "workload_diff_accepted": existing_packet.get("workload_diff_accepted", workload_diff_accepted),
                "ion_operational_posture_required": existing_packet.get("ion_operational_posture_required", operational_posture_required),
                "ion_operational_posture_accepted": existing_packet.get("ion_operational_posture_accepted", operational_posture_accepted),
                "blocked_but_preserved": False,
                "salvage_route": "ION/05_context/current/chatgpt_connector/task_returns",
                "findings": [],
                "deduped_existing_return": True,
                "deduped_existing_return_packet_path": rel_return_path,
                "deduped_existing_machine_receipt_path": machine_receipt_path,
                "dedupe_key": {
                    "work_request_id": work_request_id or None,
                    "work_request_path": work_request_path or None,
                    "task_output_sha256": packet.get("task_output_sha256"),
                    "required_reads_sha256": existing_return.get("required_reads_sha256"),
                },
                "deduped_existing_receipt_result": existing_receipt.get("result"),
                "working_capsule_update": working_capsule_update if work_request_updated else None,
            },
            mutates_active_state=True,
        )
    packet_path = _write_connector_packet(root, "task_returns", "task_return", packet)
    rel_return_path = packet_path.relative_to(root).as_posix()
    packet = _load_json_file(packet_path)
    machine_receipt_path = _write_task_return_machine_receipt(
        root,
        packet=packet,
        task_return_packet_path=rel_return_path,
        diagnosis=automation_diagnosis,
        required_reads=required_reads,
    )
    packet["machine_receipt_path"] = machine_receipt_path
    _write_json(packet_path, packet)
    work_request_updated = False
    if request_path and request_payload is not None:
        paths = list(request_payload.get("return_packet_paths") or [])
        if rel_return_path not in paths:
            paths.append(rel_return_path)
        request_payload["return_packet_paths"] = paths
        request_payload["latest_return_packet_path"] = rel_return_path
        request_payload["status"] = "RETURN_RECORDED_PROOF_ACCEPTED" if accepted else ("RETURN_TEMPLATE_INVALID" if not return_template_valid else "RETURN_RECORDED_PROOF_BLOCKED")
        if accepted:
            request_payload.pop("failure_classification", None)
        request_payload["updated_at"] = _now()
        request_payload["latest_context_proof_accepted"] = context_result.get("accepted")
        request_payload["latest_template_action_proof_accepted"] = template_result.get("accepted")
        request_payload["latest_task_return_machine_receipt_path"] = machine_receipt_path
        request_payload["latest_task_return_automation_diagnosis"] = automation_diagnosis
        request_payload["latest_task_return_carrier_intake_state"] = carrier_intake_state
        request_payload["latest_task_return_product_state_accepted"] = False
        request_payload["latest_task_return_lane"] = packet.get("return_lane")
        request_payload["latest_task_return_source_contract"] = packet.get("return_source_contract")
        working_capsule_update = _task_return_working_capsule_update(
            root,
            request_payload=request_payload,
            accepted=accepted,
            rel_return_path=rel_return_path,
            machine_receipt_path=machine_receipt_path,
        )
        request_payload["latest_working_capsule_preflight"] = working_capsule_update.get("preflight")
        if working_capsule_update.get("maintenance_attempted"):
            request_payload["latest_working_capsule_maintenance"] = working_capsule_update.get("maintenance")
        _write_json(request_path, request_payload)
        work_request_updated = True
    queue = _write_codex_work_queue_index(root)
    return _ok(
        "ion_submit_task_return",
        {
            "accepted_for_carrier_intake": accepted,
            "carrier_intake_state": carrier_intake_state,
            "carrier_intake_only": True,
            "product_state_accepted": False,
            "content_returned": content_returned,
            "packet_path": rel_return_path,
            "machine_receipt_path": machine_receipt_path,
            "return_lane": packet.get("return_lane"),
            "alternate_worker_return": packet.get("alternate_worker_return"),
            "return_source_contract": packet.get("return_source_contract"),
            "worker_identity_sha256": packet.get("worker_identity_sha256"),
            "automation_diagnosis": automation_diagnosis,
            "work_request_id": work_request_id or None,
            "work_request_path": work_request_path or None,
            "work_request_updated": work_request_updated,
            "codex_work_queue_path": CODEX_WORK_QUEUE_RELATIVE_PATH.as_posix(),
            "codex_work_queue_request_count": queue["request_count"],
                "return_template_valid": return_template_valid,
                "context_proof_accepted": context_result.get("accepted"),
                "template_action_proof_accepted": template_result.get("accepted"),
                "workload_diff_required": workload_diff_required,
                "workload_diff_present": workload_diff_present,
                "workload_diff_accepted": workload_diff_accepted,
                "ion_operational_posture_required": operational_posture_required,
                "ion_operational_posture_accepted": operational_posture_accepted,
                "blocked_but_preserved": not accepted,
                "salvage_route": "ION/05_context/current/chatgpt_connector/task_returns",
                "findings": lint_findings + list(context_result.get("findings", [])) + list(template_result.get("findings", [])) + workload_diff_findings + operational_posture_findings,
                "working_capsule_update": working_capsule_update if work_request_updated else None,
            },
            mutates_active_state=True,
        )


def call_chatgpt_connector_tool(
    root: str | Path | None,
    tool_name: str,
    arguments: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    shell_root = _resolve_connector_root(root)
    args = dict(arguments or {})
    if tool_name in FORBIDDEN_CAPABILITIES:
        return _blocked(tool_name, "forbidden_capability")
    if tool_name == "ion_status":
        return _ok(tool_name, build_ion_status(shell_root))
    if tool_name == "ion_current_operating_packet":
        return _packet_read(shell_root, "current_operating_packet")
    if tool_name == "ion_carrier_onboarding_packet":
        carrier = str(args.get("carrier") or "chatgpt_browser")
        profile = args.get("carrier_profile")
        profile_path = str(profile) if profile else None
        packet = build_carrier_onboarding_packet(shell_root, carrier_id=carrier, carrier_profile_path=profile_path)
        return _ok(tool_name, packet)
    if tool_name == "ion_read_active_packet":
        max_bytes = args.get("max_bytes")
        return _packet_read(
            shell_root,
            str(args.get("packet") or ""),
            max_bytes=int(max_bytes) if max_bytes is not None else None,
            tool_name=tool_name,
        )
    if tool_name == "ion_context_plan":
        return _packet_read(shell_root, "context_window", max_bytes=int(args.get("max_bytes") or 32 * 1024), tool_name=tool_name)
    if tool_name == "ion_cockpit_view":
        return _ok(tool_name, build_cockpit_view_model(shell_root))
    if tool_name == "ion_artifact_manifest":
        return _ok(tool_name, _artifact_manifest(shell_root))
    if tool_name == "ion_receipt_search":
        return _ok(tool_name, _receipt_search(shell_root, str(args.get("query") or ""), int(args.get("limit") or 10)))
    if tool_name == "ion_git_status_summary":
        return _ok(tool_name, _git_status_summary(shell_root))
    if tool_name == "ion_codex_work_queue":
        return _ok(tool_name, _codex_work_queue(shell_root, args))
    if tool_name == "ion_codex_queue_duplicate_audit":
        return _ok(tool_name, _codex_queue_duplicate_audit(shell_root, args))
    if tool_name == "ion_codex_queue_parallel_plan_preview":
        return _ok(tool_name, build_codex_parallel_plan_preview(shell_root, args), mutates_active_state=False)
    if tool_name == "ion_carrier_message_poll":
        return _carrier_message_poll(shell_root, args)
    if tool_name == "ion_file_read":
        return _bounded_file_read(shell_root, args)
    if tool_name == "ion_file_search":
        return _file_search(shell_root, args)
    if tool_name == "ion_tree_list":
        return _tree_list(shell_root, args)
    if tool_name == "ion_registry_read":
        return _registry_read(shell_root, args)
    if tool_name == "ion_template_read":
        return _template_read(shell_root, args)
    if tool_name == "ion_context_compile":
        return _context_compile(shell_root, args)
    if tool_name == "ion_receipt_hydrate":
        return _receipt_hydrate(shell_root, args)
    if tool_name == "ion_tool_manifest":
        return _ok(tool_name, _tool_manifest(shell_root))
    if tool_name == "ion_action_branch_list":
        return _ok(tool_name, action_branch_list(shell_root, limit=int(args.get("limit") or 100)))
    if tool_name == "ion_action_branch_describe":
        branch_id = str(args.get("branch_id") or "").strip()
        path = str(args.get("path") or "").strip()
        path_or_branch_id = str(args.get("path_or_branch_id") or "").strip()
        if not branch_id and not path and not path_or_branch_id:
            return _blocked(tool_name, "branch_id_or_path_required")
        return _ok(
            tool_name,
            action_branch_describe(
                shell_root,
                branch_id=branch_id or None,
                path=path or None,
                path_or_branch_id=path_or_branch_id or None,
                depth=str(args.get("depth") or "").strip() or None,
                profile=str(args.get("profile") or "").strip() or None,
            ),
        )
    if tool_name == "ion_action_branch_receipts":
        branch_id = str(args.get("branch_id") or "").strip()
        if not branch_id:
            return _blocked(tool_name, "branch_id_required")
        return _ok(
            tool_name,
            action_branch_receipts(
                shell_root,
                branch_id=branch_id,
                route_id=str(args.get("route_id") or "").strip() or None,
                limit=int(args.get("limit") or 20),
            ),
        )
    if tool_name == "ion_action_branch_invoke":
        branch_id = str(args.get("branch_id") or "").strip()
        route_id = str(args.get("route_id") or "").strip()
        route_args = args.get("args") if isinstance(args.get("args"), Mapping) else {}
        approval = args.get("approval") if isinstance(args.get("approval"), Mapping) else None
        if not branch_id or not route_id:
            return _blocked(tool_name, "branch_id_and_route_id_required")
        result = action_branch_invoke(
            shell_root,
            branch_id=branch_id,
            route_id=route_id,
            args=route_args,
            idempotency_key=str(args.get("idempotency_key") or "").strip() or None,
            confirmation=str(args.get("confirmation") or "").strip() or None,
            approval=approval,
            expected_route_schema_version=str(args.get("expected_route_schema_version") or "").strip() or None,
        )
        mutates = bool(result.get("mutates_active_state"))
        return _ok(tool_name, result, mutates_active_state=mutates) if result.get("ok") else _blocked(tool_name, str(result.get("finding") or "branch_invoke_blocked"), result)
    if tool_name == "ion_codex_capsule_chat_status":
        return _codex_capsule_chat_status(shell_root, args)
    if tool_name == "ion_codex_capsule_message_poll":
        return _codex_capsule_message_poll(shell_root, args)
    if tool_name in {"ion_daemon_status", "ion_codex_queue_autorun_status"}:
        data = build_codex_queue_runner_status(shell_root, reconcile=False)
        reconciliation = data.get("reconciliation") if isinstance(data.get("reconciliation"), dict) else {}
        mutates = bool(
            data.get("stale_active_run_detected")
            or reconciliation.get("latest_run_failure_classification_updated")
        )
        return _ok(tool_name, data, mutates_active_state=mutates)
    if tool_name == "ion_codex_worker_live_status":
        include_preview = bool(args.get("include_preview", True))
        preview_target = str(args.get("preview_target") or "").strip() or None
        preview_max_bytes = _bounded_preview_bytes(args.get("max_preview_bytes"), default=DEFAULT_COMPACT_PREVIEW_BYTES)
        include_observability_trace = bool(args.get("include_observability_trace"))
        lifecycle_limit = _bounded_positive_int(
            args.get("lifecycle_limit"),
            default=DEFAULT_WORKER_LIFECYCLE_LIMIT,
            minimum=1,
            maximum=MAX_WORKER_LIFECYCLE_LIMIT,
        )
        latest_runs_limit = _bounded_positive_int(
            args.get("latest_runs_limit"),
            default=DEFAULT_WORKER_LATEST_RUNS_LIMIT,
            minimum=1,
            maximum=MAX_WORKER_LATEST_RUNS_LIMIT,
        )
        latest_runs_cursor = str(args.get("latest_runs_cursor") or "").strip() or None
        latest_runs_status_filter = _status_filter_values(
            args.get("latest_runs_status_filter") or args.get("status_filter")
        )
        data = build_codex_queue_runner_status(
            shell_root,
            reconcile=False,
            include_preview=include_preview,
            preview_target=preview_target,
            preview_max_bytes=preview_max_bytes,
        )
        compact = _compact_codex_worker_live_status(
            shell_root,
            data,
            include_observability_trace=include_observability_trace,
            lifecycle_limit=lifecycle_limit,
            latest_runs_limit=latest_runs_limit,
            latest_runs_cursor=latest_runs_cursor,
            latest_runs_status_filter=latest_runs_status_filter,
        )
        reconciliation = data.get("reconciliation") if isinstance(data.get("reconciliation"), dict) else {}
        mutates = bool(
            data.get("stale_active_run_detected")
            or reconciliation.get("latest_run_failure_classification_updated")
        )
        return _ok(tool_name, compact, mutates_active_state=mutates)
    if tool_name == "ion_codex_worker_trace":
        preview_max_bytes = int(args.get("max_preview_bytes") or 512)
        data = build_codex_queue_runner_status(
            shell_root,
            reconcile=False,
            include_preview=True,
            preview_max_bytes=preview_max_bytes,
        )
        telemetry = data.get("live_worker_telemetry") if isinstance(data.get("live_worker_telemetry"), Mapping) else {}
        trace = telemetry.get("observability_trace") if isinstance(telemetry.get("observability_trace"), Mapping) else None
        return _ok(
            tool_name,
            trace
            or {
                "schema_id": "ion.codex_worker_observability_trace.v0",
                "available": False,
                "finding": "worker_trace_unavailable",
                "production_authority": False,
                "live_execution_authority": False,
            },
            mutates_active_state=False,
        )
    if tool_name == "ion_codex_runner_reconcile":
        write = bool(args.get("write", True))
        reconciliation = reconcile_codex_queue_runner_state(shell_root, write=write)
        status = build_codex_queue_runner_status(shell_root, reconcile=False)
        action = str(reconciliation.get("action") or "")
        mutates = bool(
            write
            and action not in {"", "no_active_run", "active_run_still_running", "not_requested"}
        )
        return _ok(
            tool_name,
            {
                "schema_id": "ion.codex_queue_runner_reconcile_result.v1",
                "reconcile_write": write,
                "reconciliation": reconciliation,
                "status": status,
            },
            mutates_active_state=mutates,
        )
    if tool_name == "ion_agent_list":
        return _ok(tool_name, list_agents(shell_root))
    if tool_name == "ion_agent_status":
        return _ok(tool_name, build_agent_broker_status(shell_root))
    if tool_name == "ion_agent_queue":
        return _ok(tool_name, agent_queue(shell_root, limit=int(args.get("limit") or 25)))
    if tool_name == "ion_agent_result":
        return _ok(tool_name, agent_result(shell_root, invocation_id=str(args.get("invocation_id") or "").strip() or None))
    if tool_name == "ion_agent_spawn_plan":
        return _ok(tool_name, build_agent_spawn_plan(shell_root, objective=str(args.get("objective") or "").strip() or None))
    if tool_name == "ion_swarm_status":
        return _ok(tool_name, build_agent_broker_status(shell_root))
    if tool_name == "ion_queue_operator_message":
        message = str(args.get("message") or "").strip()
        if not message:
            return _blocked(tool_name, "message_required")
        result = _enqueue_connector_operator_message(shell_root, message=message, priority=int(args.get("priority") or 50))
        return _ok(tool_name, result, mutates_active_state=True)
    if tool_name == "ion_file_put_text":
        return _put_text_artifact(shell_root, args)
    if tool_name == "ion_bounded_patch_preview":
        return _bounded_patch_preview(shell_root, args)
    if tool_name == "ion_bounded_patch_apply":
        return _bounded_patch_apply(shell_root, args)
    if tool_name in {"ion_project_workspace_status", "ion_project_preview_status", "ion_project_git_status"}:
        return _ok(
            tool_name,
            build_project_workspace_status(
                shell_root,
                project_id=str(args.get("project_id") or "cosmos"),
                probe_preview=tool_name == "ion_project_preview_status" or bool(args.get("probe_preview")),
            ),
        )
    if tool_name == "ion_project_workbench_timeline":
        return _ok(
            tool_name,
            build_project_workbench_timeline(
                shell_root,
                project_id=str(args.get("project_id") or "cosmos"),
                probe_preview=bool(args.get("probe_preview")),
                max_items=int(args.get("max_items") or 6),
            ),
        )
    if tool_name == "ion_project_context_capsule":
        return project_context_capsule(shell_root, args)
    if tool_name == "ion_project_file_read":
        return project_file_read(shell_root, args)
    if tool_name == "ion_project_file_slice_read":
        return project_file_slice_read(shell_root, args)
    if tool_name == "ion_project_patch_preview":
        return project_patch_preview(shell_root, args)
    if tool_name == "ion_kernel_fanout_carrier_dryrun_status":
        result_path = args.get("result_path")
        accepted_return_path = args.get("accepted_return_path")
        status_kwargs: dict[str, str] = {}
        if result_path is not None:
            status_kwargs["result_path"] = str(result_path)
        if accepted_return_path is not None:
            status_kwargs["accepted_return_path"] = str(accepted_return_path)
        return _ok(
            tool_name,
            build_kernel_fanout_carrier_dryrun_status(shell_root, **status_kwargs),
        )
    if tool_name == "ion_project_patch_apply":
        return project_patch_apply(shell_root, args)
    if tool_name == "ion_project_patch_revert":
        return project_patch_revert(shell_root, args)
    if tool_name == "ion_project_action_run":
        return project_action_run(shell_root, args)
    if tool_name == "ion_project_browser_capture":
        return project_browser_capture(shell_root, args)
    if tool_name == "ion_artifact_upload_init":
        return _artifact_upload_init(shell_root, args)
    if tool_name == "ion_artifact_upload_chunk":
        return _artifact_upload_chunk(shell_root, args)
    if tool_name == "ion_artifact_upload_commit":
        return _artifact_upload_commit(shell_root, args)
    if tool_name == "ion_carrier_message_send":
        return _carrier_message_send(shell_root, args)
    if tool_name == "ion_carrier_message_ack":
        return _carrier_message_ack(shell_root, args)
    if tool_name == "ion_codex_capsule_message_send":
        return _codex_capsule_message_send(shell_root, args)
    if tool_name == "ion_codex_capsule_sync_to_queue":
        return _codex_capsule_sync_to_queue(shell_root, args)
    if tool_name == "ion_codex_queue_process_once":
        request_path = str(args.get("request_path") or "").strip() or None
        lane_id = str(args.get("lane_id") or "").strip() or None
        timeout = _normalized_timeout_for_tool(shell_root, tool_name, args)
        start = bool(args.get("start"))
        include_preview = bool(args.get("include_preview", True))
        preview_target = str(args.get("preview_target") or "").strip() or None
        preview_max_bytes = _bounded_preview_bytes(args.get("max_preview_bytes"), default=DEFAULT_COMPACT_PREVIEW_BYTES)
        result = process_codex_queue_once(
            shell_root,
            request_path=request_path,
            lane_id=lane_id,
            start=start,
            background=True,
            timeout_seconds=timeout,
        )
        compact = _compact_process_once_result(
            shell_root,
            result if isinstance(result, Mapping) else {},
            include_preview=include_preview,
            preview_target=preview_target,
            max_preview_bytes=preview_max_bytes,
        )
        return _ok(tool_name, compact, mutates_active_state=True) if result.get("ok") else _blocked(tool_name, str(result.get("finding") or result.get("result") or "codex_queue_process_once_blocked"), compact)
    if tool_name == "ion_codex_queue_supersede_duplicates":
        return _codex_queue_supersede_duplicates(shell_root, args)
    if tool_name == "ion_agent_invoke":
        result = invoke_agent(
            shell_root,
            agent=str(args.get("agent") or ""),
            objective=str(args.get("objective") or ""),
            mode=str(args.get("mode") or "prepare_only"),
            queue=bool(args.get("queue")),
            start=bool(args.get("start")),
            context_refs=list(args.get("context_refs") or []),
            requested_by_carrier_id=str(args.get("requested_by_carrier_id") or "CHATGPT_BROWSER_CARRIER"),
            requested_by_callsign=str(args.get("requested_by_callsign") or "Sev"),
            timeout_seconds=_normalized_timeout_for_tool(shell_root, tool_name, args),
            work_class=str(args.get("work_class") or "").strip() or None,
            risk_level=str(args.get("risk_level") or "").strip() or None,
            route_family=str(args.get("route_family") or "").strip() or None,
            codex_model_override=args.get("codex_model_override") if isinstance(args.get("codex_model_override"), Mapping) else None,
            requested_model=str(args.get("requested_model") or "").strip() or None,
            requested_reasoning_effort=str(args.get("requested_reasoning_effort") or "").strip() or None,
            model_override_reason=str(args.get("model_override_reason") or "").strip() or None,
            idempotency_key=str(args.get("idempotency_key") or "").strip() or None,
            target_root_id=str(args.get("target_root_id") or args.get("ai_movement_target_root_id") or "").strip() or None,
            movement_class=str(args.get("movement_class") or "").strip() or None,
            target_project_subpath=str(args.get("target_project_subpath") or args.get("target_content_subpath") or "").strip() or None,
            planned_writes=list(args.get("planned_writes") or []) if isinstance(args.get("planned_writes"), list) else None,
            planned_artifacts=list(args.get("planned_artifacts") or []) if isinstance(args.get("planned_artifacts"), list) else None,
        )
        return _ok(tool_name, result, mutates_active_state=True) if result.get("ok") else _blocked(tool_name, str(result.get("finding") or "agent_invoke_blocked"), result)
    if tool_name == "ion_agent_cancel":
        result = cancel_agent_invocation(shell_root, invocation_id=str(args.get("invocation_id") or ""))
        return _ok(tool_name, result, mutates_active_state=True) if result.get("ok") else _blocked(tool_name, str(result.get("finding") or "agent_cancel_blocked"), result)
    if tool_name == "ion_swarm_step_once":
        result = swarm_step_once(
            shell_root,
            request_path=str(args.get("request_path") or "").strip() or None,
            start=bool(args.get("start")),
            timeout_seconds=_normalized_timeout_for_tool(shell_root, tool_name, args),
        )
        return _ok(tool_name, result, mutates_active_state=True) if result.get("ok") else _blocked(tool_name, str(result.get("finding") or result.get("result") or "swarm_step_once_blocked"), result)
    if tool_name == "ion_request_codex_work_packet":
        objective = str(args.get("objective") or "").strip()
        if not objective:
            return _blocked(tool_name, "objective_required")
        codex_model_override = _sanitize_codex_model_override(args.get("codex_model_override"))
        requested_model = str(args.get("requested_model") or "").strip()
        requested_reasoning_effort = str(args.get("requested_reasoning_effort") or "").strip()
        model_override_reason = str(args.get("model_override_reason") or "").strip()
        request_kind = str(args.get("request_kind") or "").strip()
        route_validation_payload: dict[str, Any] = {
            "objective": objective,
            "codex_model_override": codex_model_override or {},
            "requested_model": requested_model,
            "requested_reasoning_effort": requested_reasoning_effort,
            "model_override_reason": model_override_reason,
            "idempotency_key": str(args.get("idempotency_key") or "").strip(),
            "request_kind": request_kind,
            "work_class": str(args.get("work_class") or args.get("workload_class") or "").strip(),
            "lane_id": str(args.get("lane_id") or "").strip(),
            "risk_level": str(args.get("risk_level") or "").strip(),
            "route_family": str(args.get("route_family") or "").strip(),
        }
        if isinstance(args.get("codex_model_move"), Mapping):
            route_validation_payload["codex_model_move"] = dict(args["codex_model_move"])
        route_enforcement_receipt = validate_codex_route_enforcement(
            route_validation_payload,
            source="ion_request_codex_work_packet",
        )
        if not route_enforcement_receipt.get("ok"):
            return _blocked(
                tool_name,
                str(route_enforcement_receipt.get("finding") or "route_enforcement_rejected"),
                route_enforcement_receipt,
            )
        dedupe_key, dedupe_source, implicit_dedupe = _codex_work_request_dedupe_key(args, objective)
        if args.get("force_new") is not True:
            existing = _codex_work_request_existing_entry(shell_root, dedupe_key)
            if existing:
                return _codex_work_request_replay_result(shell_root, tool_name, existing, dedupe_key, dedupe_source)
        now = _now()
        request_stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S%fZ")
        request_id = f"codex_req_{request_stamp}_{_safe_slug(objective)}"
        objective_sha256 = _codex_work_request_objective_fingerprint(objective)
        payload = {
            "schema_id": "ion.chatgpt_browser_connector_codex_work_request.v1",
            "request_id": request_id,
            "objective": objective,
            "objective_sha256": objective_sha256,
            "dedupe_key": dedupe_key,
            "idempotency_source": dedupe_source,
            "implicit_idempotency_key": implicit_dedupe,
            "client_request_id": str(args.get("client_request_id") or "").strip() or None,
            "idempotency_key": str(args.get("idempotency_key") or "").strip() or None,
            "requested_by": "chatgpt_browser_connector",
            "status": "QUEUED_FOR_CODEX_CARRIER",
            "created_at": now,
            "updated_at": now,
            "return_packet_paths": [],
            "latest_return_packet_path": None,
            "production_authority": False,
            "live_execution_authority": False,
        }
        if isinstance(args.get("codex_model_move"), Mapping):
            payload["codex_model_move"] = dict(args["codex_model_move"])
        if codex_model_override:
            payload["codex_model_override"] = codex_model_override
        project_hash = str(args.get("project_hash") or "").strip()
        if requested_model:
            payload["requested_model"] = requested_model
        if requested_reasoning_effort:
            payload["requested_reasoning_effort"] = requested_reasoning_effort
        if model_override_reason:
            payload["model_override_reason"] = model_override_reason
        if project_hash:
            payload["project_hash"] = project_hash
        if request_kind:
            payload["request_kind"] = request_kind
        _apply_domain_weaver_work_request_identity_fields(payload, args)
        work_class = str(args.get("work_class") or args.get("workload_class") or "").strip()
        risk_level = str(args.get("risk_level") or "").strip()
        route_family = str(args.get("route_family") or "").strip()
        lane_id = str(args.get("lane_id") or "").strip()
        if work_class:
            payload["work_class"] = work_class
        if risk_level:
            payload["risk_level"] = risk_level
        if route_family:
            payload["route_family"] = route_family
        if lane_id:
            payload["lane_id"] = lane_id
        target_binding = apply_codex_work_request_target_binding(
            payload,
            args,
            source="ion_request_codex_work_packet",
        )
        apply_route_enforcement_metadata(payload, route_enforcement_receipt)
        lane_route = classify_codex_work_request_lane(payload)
        payload["lane_id"] = lane_route.get("lane_id")
        payload["work_lane_route_receipt"] = lane_route
        payload["return_contract_sections"] = _return_contract_sections_for_work_request(payload)
        if isinstance(args.get("ion_skill_activation"), Mapping):
            payload["ion_skill_activation"] = dict(args["ion_skill_activation"])
        if isinstance(args.get("ion_chat_engine_turn"), Mapping):
            payload["ion_chat_engine_turn"] = dict(args["ion_chat_engine_turn"])
        required_context_reads = _sanitize_required_context_reads(args.get("required_context_reads"))
        if required_context_reads:
            payload["required_context_reads"] = required_context_reads
        packet_path = _write_connector_packet(shell_root, "codex_work_requests", objective, payload)
        payload["packet_path"] = packet_path.relative_to(shell_root).as_posix()
        _write_json(packet_path, payload)
        _record_codex_work_request_idempotency(
            shell_root,
            dedupe_key,
            source=dedupe_source,
            implicit=implicit_dedupe,
            payload=payload,
            packet_path=packet_path,
        )
        queue = _write_codex_work_queue_index(shell_root)
        return _ok(
            tool_name,
            {
                "request_id": request_id,
                "packet_path": packet_path.relative_to(shell_root).as_posix(),
                "codex_work_queue_path": CODEX_WORK_QUEUE_RELATIVE_PATH.as_posix(),
                "codex_work_queue_request_count": queue["request_count"],
                "lane_id": payload.get("lane_id"),
                "work_lane_route_receipt": payload.get("work_lane_route_receipt"),
                "idempotent_replay": False,
                "duplicate_prevented": False,
                "dedupe_key": dedupe_key,
                "idempotency_source": dedupe_source,
                "implicit_idempotency_key": implicit_dedupe,
                "idempotency_ledger_path": CODEX_WORK_REQUEST_IDEMPOTENCY_LEDGER_RELATIVE_PATH.as_posix(),
                "route_enforcement_receipt": route_enforcement_receipt,
                "ai_movement_target_binding": target_binding,
            },
            mutates_active_state=True,
        )
    if tool_name in TASK_RETURN_SUBMIT_TOOLS:
        return _evaluate_task_return_packet(shell_root, args, tool_name=tool_name)
    if tool_name == "ion_record_native_subagent_transcript":
        return _record_native_subagent_transcript(shell_root, args)
    if tool_name == "ion_record_alternate_worker_provenance":
        return _record_alternate_worker_provenance(shell_root, args)
    if tool_name == "ion_record_chatgpt_decision":
        decision = str(args.get("decision") or "").strip()
        if not decision:
            return _blocked(tool_name, "decision_required")
        packet_path = _write_connector_packet(shell_root, "decisions", decision, {
            "schema_id": "ion.chatgpt_browser_connector_decision.v1",
            "decision": decision,
            "rationale": str(args.get("rationale") or ""),
            "status": "RECORDED_NOT_AUTHORITY_BY_ITSELF",
        })
        return _ok(tool_name, {"packet_path": packet_path.relative_to(shell_root).as_posix()}, mutates_active_state=True)
    if tool_name == "ion_create_containment_receipt":
        target = str(args.get("target_path") or "").strip()
        transition = str(args.get("transition") or "MOVE_TO_CONTAINMENT").strip()
        reason = str(args.get("reason") or "").strip()
        if not target or not reason:
            return _blocked(tool_name, "target_path_and_reason_required")
        target_path = _safe_rel_path(shell_root, target)
        packet_path = _write_connector_packet(shell_root, "containment_receipts", target, {
            "schema_id": "ion.chatgpt_browser_connector_containment_receipt.v1",
            "target_path": target,
            "target_exists": target_path.exists(),
            "target_sha256": _sha256_file(target_path) if target_path.exists() and target_path.is_file() else None,
            "transition": transition,
            "reason": reason,
            "movement_performed": False,
            "status": "RECEIPT_ONLY_REQUIRES_SEPARATE_BOUNDED_MUTATION",
        })
        return _ok(tool_name, {"packet_path": packet_path.relative_to(shell_root).as_posix()}, mutates_active_state=True)
    return _blocked(tool_name, "tool_not_in_v120_contract", {"allowed": sorted(STATUS_READ_TOOLS | BOUNDED_QUEUE_RECEIPT_TOOLS)})


def audit_chatgpt_browser_mcp_connector_contract(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_connector_root(root)
    findings: list[str] = []
    required_paths = {
        "protocol": PROTOCOL_RELATIVE_PATH,
        "full_carrier_protocol": FULL_CARRIER_PROTOCOL_RELATIVE_PATH,
        "policy": POLICY_RELATIVE_PATH,
        "full_carrier_tool_registry": FULL_CARRIER_TOOL_REGISTRY_RELATIVE_PATH,
        "carrier_capability_registry": FULL_CARRIER_CAPABILITY_REGISTRY_RELATIVE_PATH,
        "schema": SCHEMA_RELATIVE_PATH,
        "setup": SETUP_RELATIVE_PATH,
        "codex_queue_runner": Path("ION/04_packages/kernel/ion_codex_queue_runner.py"),
        "agent_invocation_broker": Path("ION/04_packages/kernel/ion_agent_invocation_broker.py"),
    }
    optional_paths = {
        "integration_dir": INTEGRATION_DIR_RELATIVE_PATH,
        "legacy_integration_dir": LEGACY_INTEGRATION_DIR_RELATIVE_PATH,
        "wrapper": WRAPPER_RELATIVE_PATH,
        "manifest": MANIFEST_RELATIVE_PATH,
    }
    for label, rel in required_paths.items():
        resolved = resolve_ion_path(shell_root, rel)
        if not resolved.exists():
            findings.append(f"missing_{label}:{rel.as_posix()}")

    policy = _read_policy(shell_root) if (shell_root / POLICY_RELATIVE_PATH).exists() else {}
    policy_read = set(policy.get("allowed_status_read_tools", []))
    policy_write = set(policy.get("allowed_bounded_queue_receipt_tools", []))
    policy_forbidden = set(policy.get("forbidden_tools", []))
    allowed = STATUS_READ_TOOLS | BOUNDED_QUEUE_RECEIPT_TOOLS

    if policy_read != STATUS_READ_TOOLS:
        findings.append("policy_allowed_status_read_tools_do_not_match_contract")
    if policy_write != BOUNDED_QUEUE_RECEIPT_TOOLS:
        findings.append("policy_allowed_bounded_queue_receipt_tools_do_not_match_contract")
    missing_forbidden = sorted(FORBIDDEN_CAPABILITIES - policy_forbidden)
    if missing_forbidden:
        findings.append(f"policy_missing_forbidden_capabilities:{','.join(missing_forbidden)}")
    overlap = sorted(allowed & policy_forbidden)
    if overlap:
        findings.append(f"forbidden_tool_also_allowed:{','.join(overlap)}")
    unsafe_overlap = sorted(allowed & FORBIDDEN_CAPABILITIES)
    if unsafe_overlap:
        findings.append(f"unsafe_capability_exposed_as_tool:{','.join(unsafe_overlap)}")

    protocol_text = _read_text(shell_root / PROTOCOL_RELATIVE_PATH) if (shell_root / PROTOCOL_RELATIVE_PATH).exists() else ""
    for phrase in (
        "mounted ION carrier posture",
        "production authority",
        "live execution authority",
        "arbitrary shell",
        "### CONTEXT PROOF",
        "### TEMPLATE ACTION PROOF",
    ):
        if phrase not in protocol_text:
            findings.append(f"protocol_missing_phrase:{phrase}")

    ready = not findings
    return {
        "schema_id": SCHEMA_ID,
        "version_line": VERSION_LINE,
        "generated_at": _now(),
        "connector_id": CONNECTOR_ID,
        "connector_state": "CONTRACT_READY_NOT_DEPLOYED" if ready else "BLOCKED",
        "verdict": "ION_CHATGPT_BROWSER_MCP_CONNECTOR_CONTRACT_READY" if ready else "ION_CHATGPT_BROWSER_MCP_CONNECTOR_CONTRACT_BLOCKED",
        "accepted": ready,
        "allowed_tools": sorted(allowed),
        "status_read_tools": sorted(STATUS_READ_TOOLS),
        "bounded_queue_receipt_tools": sorted(BOUNDED_QUEUE_RECEIPT_TOOLS),
        "forbidden_tools": sorted(FORBIDDEN_CAPABILITIES),
        "tool_descriptors": tool_descriptors(),
        "source_paths": {label: rel.as_posix() for label, rel in required_paths.items()},
        "optional_source_paths": {label: rel.as_posix() for label, rel in optional_paths.items()},
        "optional_source_path_status": {
            label: resolve_ion_path(shell_root, rel).exists()
            for label, rel in optional_paths.items()
        },
        "findings": findings,
        "must_state_mounted_ion_carrier_posture": True,
        "role_authority_requires_phase_proof": True,
        "production_authority": False,
        "live_execution_authority": False,
        "deployment_authority": False,
    }


def write_chatgpt_browser_mcp_connector_contract(
    root: str | Path | None = None,
    *,
    output: str | Path | None = None,
) -> dict[str, Any]:
    shell_root = _resolve_connector_root(root)
    result = audit_chatgpt_browser_mcp_connector_contract(shell_root)
    out = shell_root / (Path(output) if output else OUTPUT_RELATIVE_PATH)
    _write_json(out, result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit ION ChatGPT browser MCP connector contract.")
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", default=None)
    parser.add_argument("--tool", default=None)
    parser.add_argument("--arguments-json", default="{}")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.tool:
        result = call_chatgpt_connector_tool(args.ion_root, args.tool, json.loads(args.arguments_json or "{}"))
        ok = bool(result.get("ok"))
    elif args.write:
        result = write_chatgpt_browser_mcp_connector_contract(args.ion_root, output=args.output)
        ok = bool(result.get("accepted"))
    else:
        result = audit_chatgpt_browser_mcp_connector_contract(args.ion_root)
        ok = bool(result.get("accepted"))

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result.get("verdict") or ("OK" if ok else "BLOCKED"))
        for finding in result.get("findings", []):
            print(f"- {finding}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
