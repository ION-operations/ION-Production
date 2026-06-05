"""ION cockpit view-model projection.

This module is intentionally small and dependency-free. It reads the live ION
runtime packet layer and emits a normalized cockpit projection that the
Cursor/VS Code extension and JOC React shell can render without guessing from
chat memory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .ion_agent_control_plane import build_agent_control_plane_projection
from .ion_automation_control_plane import build_automation_control_plane
from .ion_agent_invocation_broker import build_agent_broker_status
from .ion_action_mcp_branch_leaders import action_branch_describe, action_branch_invoke
from .ion_chatgpt_sandbox_return_intake import build_sandbox_return_queue_projection
from .ion_codex_cli_workbench import build_codex_cli_workbench_model
from .ion_codex_conversation_archive import build_codex_conversation_archive
from .ion_codex_git_rollback import build_codex_git_rollback_model
from .ion_codex_queue_runner import build_codex_queue_runner_status
from .ion_codex_browser_agent import build_capability_matrix, latest_codex_browser_agent_summary
from .ion_browser_gpt_dom_calibration import latest_browser_gpt_dom_summary
from .ion_cockpit_service_manager import build_service_console_model
from .ion_kernel_fanout_carrier_dryrun import build_kernel_fanout_carrier_dryrun_status
from .ion_local_service_status import build_local_service_status
from .ion_project_cockpit import build_project_cockpit_model
from .ion_project_portfolio import default_cosmos_project_root
from .ion_system_diagnostics import build_system_diagnostics_model
from .ion_workspace_paths import resolve_ion_path

CURRENT = Path("ION/05_context/current")
SIGNALS = Path("ION/05_context/signals")
REPORTS = Path("ION/docs/consolidation")

ACTIVE_FILES = {
    "hook": CURRENT / "ACTIVE_CURSOR_HOOK_STATE.json",
    "work": CURRENT / "ACTIVE_WORK_PACKET.json",
    "spawn": CURRENT / "ACTIVE_ROLE_SPAWN_PLAN.json",
    "turn": CURRENT / "ACTIVE_CARRIER_TURN_PACKET.json",
    "ledger": CURRENT / "ACTIVE_CARRIER_TASK_RETURN_LEDGER.json",
    "steward": CURRENT / "ACTIVE_STEWARD_INTEGRATION_QUEUE.json",
    "operator_queue": CURRENT / "ACTIVE_OPERATOR_MESSAGE_QUEUE.json",
    "carrier_messages": CURRENT / "ACTIVE_CARRIER_MESSAGE_QUEUE.json",
    "human_gates": CURRENT / "ACTIVE_HUMAN_GATE_QUEUE.json",
    "front_door_proof_trace": CURRENT / "ACTIVE_FRONT_DOOR_PROOF_TRACE.json",
    "lane_timeline": CURRENT / "ACTIVE_LANE_TIMELINE_VIEW_MODEL.json",
    "receipt_hydration": CURRENT / "ACTIVE_RECEIPT_HYDRATION_VIEW_MODEL.json",
    "runtime_debug_overlay": CURRENT / "ACTIVE_RUNTIME_DEBUG_OVERLAY.json",
    "v72_mcp_donor_reconciliation": CURRENT / "V108_V72_MCP_DONOR_RECONCILIATION_AUDIT.json",
}
DEFAULT_SAFE_FULL_PROJECT_PACKAGE_RESULT = CURRENT / "SAFE_FULL_PROJECT_PACKAGE_RESULT_V110.json"
HELIXION_REBUILD_PLAN = Path("ION/02_architecture/HELIXION_JOC_DAIMON_WISDOMNET_MASTER_EVOLUTION_PLAN.md")
HELIXION_REBUILD_REGISTRY = Path("ION/03_registry/helixion_joc_evolution_registry.yaml")
HELIXION_REBUILD_CURRENT_PLAN = CURRENT / "helixion_joc_rebuild/HELIXION_JOC_REBUILD_CURRENT_PLAN.json"
CODEX_CAPSULE_CHAT_MODEL = CURRENT / "ACTIVE_CODEX_CAPSULE_CHAT_MODEL.json"
PORTABLE_COMPANION_PRODUCT_CONTEXT = CURRENT / "portable_ion_page_companion/PORTABLE_ION_PAGE_COMPANION_001_PRODUCT_CONTEXT.json"
DOM_PERCEPTION_TASK_RETURN = CURRENT / "browser_perception/DOM_PERCEPTION_001/TASK_RETURN_DOM_PERCEPTION_001.md"
DOM_PERCEPTION_DOMAIN_REGISTRY = Path("ION/03_registry/browser_perception_domain_registry_proposal.yaml")
BROWSER_EXTENSION_ROOT = Path("../browser_extension/ion_chatops_bridge")
BROWSER_EXTENSION_LEGACY_ROOT = Path("ION/09_integrations/browser_extension/ion_chatops_bridge")
BROWSER_EXTENSION_MANIFEST = BROWSER_EXTENSION_ROOT / "manifest.json"
BROWSER_EXTENSION_AGENT_CONTRACT = BROWSER_EXTENSION_ROOT / "AGENT_INVOCATION_LANE_CONTRACT.json"
BROWSER_EXTENSION_QUEUE_PACK_AUTHORING = BROWSER_EXTENSION_ROOT / "QUEUE_PACK_AUTHORING.md"
CODEX_CONTEXT_PACKAGES = CURRENT / "codex_solo/CONTEXT_PACKAGES.json"
CODEX_SOLO_LONG_HORIZON = CURRENT / "codex_solo/LONG_HORIZON.json"
CODEX_SOLO_STATUS = CURRENT / "codex_solo/STATUS.json"
DOMAIN_WEAVER_PROJECTION = CURRENT / "domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
CONTEXT_PACKAGE_GRAPH_DIR = CURRENT / "context_package_graph_wave_001"
CONTEXT_PACKAGE_GRAPH_REVIEW = CONTEXT_PACKAGE_GRAPH_DIR / "CONTEXT_PACKAGE_GRAPH_WAVE_001_REVIEW.json"
CONTEXT_PACKAGE_GRAPH_ENRICHMENT = CONTEXT_PACKAGE_GRAPH_DIR / "CONTEXT_PACKAGE_GRAPH_WAVE_002_ENRICHMENT_MANIFEST.json"
CONTEXT_PACKAGE_GRAPH_COCKPIT_SPEC = CONTEXT_PACKAGE_GRAPH_DIR / "COCKPIT_CONTEXT_EXPLORER_PROJECTION_SPEC.json"
CUSTOM_GPT_CAPSULE_SYSTEM_DIR = CURRENT / "custom_gpt_capsule_system"
CUSTOM_GPT_FACTORY_DIR = CURRENT / "custom_gpt_factory"
ARTIFACT_PACKAGES_DIR = Path("ION/06_artifacts/packages")
WORKER_SETTLEMENT_DIR = CURRENT / "kernel_fanout_scheduler/settlement"
SUPABASE_EVENT_RECEIPTS_DIR = CURRENT / "supabase_event_mirror/receipts"
RUNTIME_SERVICE_RECEIPTS_DIR = CURRENT / "runtime_services/receipts"
RUNTIME_SERVICE_TEST_RECEIPTS_DIR = CURRENT / "runtime_services/test_run_receipts"
ACTION_GATEWAY_RECEIPTS_DIR = CURRENT / "action_gateway/receipts"
ACTION_GATEWAY_RUNTIME_DIR = CURRENT / "action_gateway/runtime"
CHATOPS_ACTIONS_DIR = CURRENT / "chatops_bridge/actions"
BRANCH_GATEWAY_CONFIRMATION_TOKEN = "ION_BOUNDED_WRITE_CONFIRMED"
RUNTIME_SERVICE_RETEST_SERVICE_ID = "mcp_preview"
VNEXT_ROOT = Path("ION_VNEXT")
VNEXT_WORK_DIR = VNEXT_ROOT / "07_work"
VNEXT_RELEASES_DIR = VNEXT_ROOT / "08_releases"
VNEXT_WORKSPACE_CANON = VNEXT_ROOT / "01_canon/WORKSPACE_CANON.yaml"
VNEXT_FRONT_DOOR_AI = VNEXT_ROOT / "00_front_door/AI_START_HERE.md"
VNEXT_FRONT_DOOR_HUMAN = VNEXT_ROOT / "00_front_door/HUMAN_START_HERE.md"
VNEXT_ROUTE_MAP = VNEXT_ROOT / "00_front_door/ROUTE_MAP.md"
VNEXT_AUTHORITY_BOUNDARIES = VNEXT_ROOT / "00_front_door/AUTHORITY_BOUNDARIES.md"
VNEXT_CONTROL_SURFACE_REGISTRY = VNEXT_ROOT / "01_canon/CONTROL_SURFACE_REGISTRY.yaml"
VNEXT_STATE_LIFECYCLE = VNEXT_ROOT / "01_canon/STATE_LIFECYCLE.yaml"

OUTPUT = CURRENT / "ACTIVE_COCKPIT_VIEW_MODEL.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    try:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive projection, not authority
        return {"_read_error": str(exc), "_path": str(path)}


def _domain_weaver_surface_agent_control_plane(root: Path) -> dict[str, Any]:
    domain_weaver = read_json(root / DOMAIN_WEAVER_PROJECTION)
    summary = domain_weaver.get("summary") if isinstance(domain_weaver.get("summary"), Mapping) else {}
    domains = domain_weaver.get("domains") if isinstance(domain_weaver.get("domains"), list) else []
    agents = domain_weaver.get("agents") if isinstance(domain_weaver.get("agents"), list) else []
    return {
        "schema_id": "ion.agent_control_plane.domain_weaver_surface.v0_1",
        "generated_at": utc_now(),
        "verdict": (
            "ION_DOMAIN_WEAVER_SURFACE_PROJECTION_READY"
            if domain_weaver
            else "ION_DOMAIN_WEAVER_SURFACE_PROJECTION_MISSING"
        ),
        "ok": bool(domain_weaver),
        "shell_root": root.as_posix(),
        "source_model": {
            "domain_weaver": "materialized_domain_weaver_projection",
            "full_agent_control_plane": "deferred_for_surface_boot",
        },
        "summary": {
            "agent_count": len(agents),
            "domain_count": len(domains),
            "active_process_running": False,
            "domain_weaver_usable_domain_count": summary.get("usable_domain_count", 0),
            "active_domain_count": summary.get("active_domain_count", 0),
            "candidate_domain_count": summary.get("candidate_domain_count", 0),
            "candidate_covered_domain_count": summary.get("candidate_covered_domain_count", 0),
            "covered_domain_count": summary.get("covered_domain_count", 0),
            "domain_weaver_gap_count": summary.get("gap_count", 0),
            "domain_weaver_edge_count": summary.get("edge_count", 0),
        },
        "agents": agents,
        "domains": domains,
        "domain_weaver": domain_weaver,
        "communications": {"schema_id": "ion.agent_control_plane.communications.v1", "summary": {}, "channels": []},
        "diagnostics": {
            "schema_id": "ion.agent_control_plane.diagnostics.v1",
            "domain_weaver": {
                "weave_status": domain_weaver.get("weave_status"),
                "projection_path": DOMAIN_WEAVER_PROJECTION.as_posix(),
                "current_capability_class": summary.get("current_capability_class"),
            },
            "full_agent_control_plane_deferred": True,
        },
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
    }


def _codex_surface_agent_control_plane(root: Path) -> dict[str, Any]:
    projection = _domain_weaver_surface_agent_control_plane(root)
    try:
        broker = build_agent_broker_status(root)
    except Exception as exc:  # pragma: no cover - defensive projection, not authority
        broker = {"_read_error": str(exc)}
    queue_runner = broker.get("codex_queue_runner") if isinstance(broker.get("codex_queue_runner"), Mapping) else {}
    summary = projection.get("summary") if isinstance(projection.get("summary"), Mapping) else {}
    projection["schema_id"] = "ion.agent_control_plane.codex_surface.v0_1"
    projection["verdict"] = (
        "ION_CODEX_SURFACE_AGENT_PROJECTION_READY"
        if projection.get("ok")
        else "ION_CODEX_SURFACE_AGENT_PROJECTION_DEGRADED"
    )
    projection["source_model"] = {
        "domain_weaver": "materialized_surface_projection",
        "codex_queue_runner": "lightweight_broker_status",
        "full_agent_control_plane": "deferred_for_codex_first_paint",
    }
    projection["summary"] = {
        **dict(summary),
        "active_process_running": bool(queue_runner.get("active_process_running")),
        "queued_agent_codex_work_request_count": broker.get("queued_agent_codex_work_request_count", 0),
        "codex_surface_first_paint": True,
    }
    projection["chain"] = {
        "schema_id": "ion.agent_control_plane.chain.v1",
        "steps": [],
        "active_process_running": bool(queue_runner.get("active_process_running")),
        "active_run": queue_runner.get("active_run"),
        "full_chain_deferred": True,
    }
    projection["runs"] = {
        "schema_id": "ion.agent_control_plane.runs.v1",
        "active_process_running": bool(queue_runner.get("active_process_running")),
        "active_run": queue_runner.get("active_run"),
        "live_worker_telemetry": queue_runner.get("live_worker_telemetry"),
        "queued_agent_codex_work_request_count": broker.get("queued_agent_codex_work_request_count", 0),
        "next_agent_codex_work_request_path": broker.get("next_agent_codex_work_request_path"),
    }
    projection["communications"] = {
        "schema_id": "ion.agent_control_plane.communications.v1",
        "summary": {"full_agent_comms_deferred": True},
        "timeline": [],
        "relays": [],
        "pending_relays": [],
        "receipts": [],
        "team_comms": {"schema_id": "ion.agent_comms_projection.v1", "summary": {}, "threads": []},
        "policy": "Full agent communication hydration is deferred for Codex first paint; timeline rows derive from current chat events.",
        "production_authority": False,
        "live_execution_authority": False,
    }
    projection["dispatcher"] = {
        "schema_id": "ion.steward_dispatcher_projection.v1",
        "summary": {"full_dispatcher_deferred": True},
    }
    diagnostics = projection.get("diagnostics") if isinstance(projection.get("diagnostics"), Mapping) else {}
    projection["diagnostics"] = {
        **dict(diagnostics),
        "full_agent_control_plane_deferred": True,
        "deferred_reason": "codex_surface_first_paint",
    }
    return projection


def _deferred_codex_git_rollback_model() -> dict[str, Any]:
    return {
        "schema_id": "ion.codex_git_rollback.v1",
        "generated_at": utc_now(),
        "verdict": "ION_CODEX_GIT_ROLLBACK_DEFERRED_FOR_SURFACE_BOOT",
        "ok": True,
        "surface_boot_deferred": True,
        "current_git": {},
        "current_worktree": {"diff_stats": {}, "file_edits": []},
        "summary": {
            "checkpoint_count": 0,
            "visible_checkpoint_count": 0,
            "rollback_receipt_count": 0,
            "rollback_ready_count": 0,
            "archive_diff_evidence_count": 0,
            "current_file_count": 0,
            "current_added_lines": 0,
            "current_removed_lines": 0,
            "current_untracked_file_count": 0,
        },
        "checkpoints": [],
        "archive_diff_evidence": [],
        "rollback_receipts": [],
        "policy": "Full diff and rollback hydration is served by /cockpit/git/rollback/model.json after Codex first paint.",
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def latest_safe_package_result_rel(root: Path) -> Path:
    current = root / CURRENT
    candidates = sorted(current.glob("SAFE_FULL_PROJECT_PACKAGE_RESULT_V*.json"))
    if not candidates:
        return DEFAULT_SAFE_FULL_PROJECT_PACKAGE_RESULT
    return candidates[-1].relative_to(root)


def compact(value: Any, fallback: str = "unknown") -> str:
    if value is None:
        return fallback
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, (int, float, bool)):
        return str(value)
    return fallback


def listify(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def repo_rel(path: Path, root: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def status_from_findings(findings: Iterable[Any], blocked: bool = False) -> str:
    if blocked:
        return "blocked"
    return "ready" if not list(findings) else "degraded"


def _spawn_rows(spawn: dict[str, Any], turn: dict[str, Any]) -> list[dict[str, Any]]:
    rows = listify(spawn.get("role_spawn_plan"))
    if rows:
        return rows
    for item in listify(turn.get("spawn_queue")):
        if isinstance(item, dict):
            rows.append(item)
    return rows


def _ledger_records(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    return [r for r in listify(ledger.get("records")) if isinstance(r, dict)]


def _steward_items(steward: dict[str, Any]) -> list[dict[str, Any]]:
    return [i for i in listify(steward.get("items")) if isinstance(i, dict)]


def _operator_items(queue: dict[str, Any]) -> list[dict[str, Any]]:
    return [i for i in listify(queue.get("items")) if isinstance(i, dict)]


def _carrier_message_items(queue: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in ("items", "messages", "carrier_messages"):
        rows.extend([i for i in listify(queue.get(key)) if isinstance(i, dict)])
    return rows


def _gates(gates: dict[str, Any]) -> list[dict[str, Any]]:
    return [g for g in listify(gates.get("gates")) if isinstance(g, dict)]


def _spawn_count(rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in rows if row.get("spawn") is True or str(row.get("spawn", "")).lower() == "true")


def _deferred_spawn_count(rows: list[dict[str, Any]]) -> int:
    return sum(
        1
        for row in rows
        if row.get("spawn") is not True and (row.get("spawn_intent") is True or row.get("spawn_deferral_reason"))
    )


def _active_spawn_queue_count(turn: dict[str, Any], spawn_rows: list[dict[str, Any]]) -> int:
    if isinstance(turn.get("spawn_queue"), list):
        return len([row for row in turn.get("spawn_queue", []) if isinstance(row, dict)])
    return _spawn_count(spawn_rows)


def _return_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"accepted": 0, "rejected": 0, "pending": 0, "needs_human_review": 0}
    for record in records:
        if record.get("accepted") is True:
            counts["accepted"] += 1
            continue
        if record.get("accepted") is False:
            counts["rejected"] += 1
            continue
        decision = str(record.get("decision") or record.get("status") or "pending").lower()
        if "accept" in decision:
            counts["accepted"] += 1
        elif "human" in decision or "review" in decision:
            counts["needs_human_review"] += 1
        elif "reject" in decision or "fail" in decision:
            counts["rejected"] += 1
        else:
            counts["pending"] += 1
    return counts


def _authority_for_return(record: dict[str, Any]) -> str:
    if record.get("accepted") is True:
        return "ACCEPTED_TASK_RETURN"
    if record.get("accepted") is False:
        return "REJECTED_TASK_RETURN"
    decision = str(record.get("decision") or record.get("status") or "pending").lower()
    if "accept" in decision:
        return "ACCEPTED_TASK_RETURN"
    if "reject" in decision or "fail" in decision:
        return "REJECTED_TASK_RETURN"
    if "human" in decision or "review" in decision:
        return "HUMAN_GATE_REQUIRED"
    return "PENDING_TASK_RETURN"


def summarize_agents(spawn_rows: list[dict[str, Any]], records: list[dict[str, Any]]) -> dict[str, Any]:
    return_index = {}
    for record in records:
        key = (str(record.get("role", "")).upper(), str(record.get("index", record.get("spawn_index", ""))))
        return_index[key] = record

    rows = []
    context_packages = []
    for idx, row in enumerate(spawn_rows, start=1):
        role = compact(row.get("role") or row.get("display_name"), f"ROW_{idx}").upper()
        row_index = compact(row.get("index"), str(idx))
        record = return_index.get((role, row_index), {})
        ctx_path = row.get("context_package_path") or row.get("session_context_package_path") or row.get("context_package")
        receipt_path = row.get("context_load_receipt_path") or row.get("receipt_path")
        rows.append(
            {
                "index": row_index,
                "role": role,
                "spawn": bool(row.get("spawn", False)),
                "status": "return_captured" if record else ("spawn_pending" if row.get("spawn") else "not_spawned"),
                "context_package_path": ctx_path,
                "context_load_receipt_path": receipt_path,
                "authority_class": _authority_for_return(record) if record else "ACTIVE_RUNTIME_AUTHORITY",
                "return_recorded": bool(record),
            }
        )
        if ctx_path:
            context_packages.append(
                {
                    "role": role,
                    "index": row_index,
                    "path": ctx_path,
                    "receipt_path": receipt_path,
                    "authority_class": "ACTIVE_RUNTIME_AUTHORITY",
                }
            )
    return {
        "spawn_rows": rows,
        "context_packages": context_packages,
        "returns": [
            {
                "role": compact(record.get("role"), "unknown").upper(),
                "index": compact(record.get("index") or record.get("spawn_index"), "unknown"),
                "decision": compact(record.get("decision") or record.get("status"), "pending"),
                "path": record.get("task_output_path") or record.get("output_path"),
                "authority_class": _authority_for_return(record),
            }
            for record in records
        ],
    }


def synthesize_timeline(data: dict[str, dict[str, Any]], counts: dict[str, Any], active_files: dict[str, Path] | None = None) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    paths = active_files or ACTIVE_FILES

    def add(kind: str, label: str, status: str, path: Path, detail: str = "") -> None:
        payload = data.get(kind, {})
        stamp = payload.get("updated_at") or payload.get("created_at") or payload.get("installed_at") or utc_now()
        events.append(
            {
                "time": stamp,
                "source": kind,
                "event_type": label,
                "status": status,
                "path": str(path),
                "detail": detail,
            }
        )

    add("hook", "cursor hook state", compact(data.get("hook", {}).get("status"), "unknown"), paths["hook"])
    add("work", "work packet", "ready" if data.get("work") else "missing", paths["work"], compact(data.get("work", {}).get("objective"), "no objective"))
    add("turn", "carrier turn", "blocked" if data.get("turn", {}).get("blocked_by_findings") else "ready", paths["turn"])
    add("spawn", "spawn plan", "ready", paths["spawn"], f"spawn rows: {counts['spawn_rows']}")
    add("ledger", "task-return ledger", "ready", paths["ledger"], f"accepted: {counts['returns']['accepted']} rejected: {counts['returns']['rejected']}")
    add("steward", "steward queue", "ready", paths["steward"], f"items: {counts['steward_queue']}")
    add("operator_queue", "operator queue", "ready", paths["operator_queue"], f"pending: {counts['operator_queue_pending']}")
    add("human_gates", "human gate queue", "blocked" if counts["open_gates"] else "ready", paths["human_gates"], f"open: {counts['open_gates']}")
    safe_package = data.get("safe_full_project_package", {})
    safe_package_root = safe_package.get("zip_root_audit", {}) if isinstance(safe_package.get("zip_root_audit"), dict) else {}
    add(
        "safe_full_project_package",
        "safe full-project package",
        "ready" if safe_package.get("accepted") is True and safe_package_root.get("verdict") == "ZIP_ROOT_CONFIRMED" else "degraded",
        paths["safe_full_project_package"],
        compact(safe_package_root.get("archive_root_mode"), "no safe package result"),
    )
    donor = data.get("v72_mcp_donor_reconciliation", {})
    donor_verdict = compact(donor.get("reconciliation_verdict"), "no donor reconciliation audit")
    add(
        "v72_mcp_donor_reconciliation",
        "V72 MCP donor reconciliation",
        "ready" if donor_verdict == "V72_MCP_DONOR_RECONCILIATION_PASS" else "degraded",
        paths["v72_mcp_donor_reconciliation"],
        f"{donor_verdict}; restored: {compact(donor.get('restored_donor_surface_count'), '0')}; forbidden runtime: {compact(donor.get('forbidden_runtime_file_count'), '0')}",
    )
    front_door = data.get("front_door_proof_trace", {})
    add(
        "front_door_proof_trace",
        "front-door proof trace",
        "ready" if front_door.get("proof_complete") else "degraded",
        paths["front_door_proof_trace"],
        compact(front_door.get("verdict"), "no front-door proof trace"),
    )
    return events


def recent_receipts(root: Path, limit: int = 12) -> list[dict[str, Any]]:
    candidates: list[Path] = []
    for base in (root / SIGNALS, root / REPORTS):
        if base.exists():
            candidates.extend([p for p in base.iterdir() if p.is_file() and p.suffix.lower() in {".txt", ".md", ".json"}])
    candidates.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    return [
        {
            "path": str(p.relative_to(root)),
            "name": p.name,
            "authority_class": "ACTIVE_RUNTIME_AUTHORITY" if "receipt" in p.name.lower() else "WITNESS_INPUT",
        }
        for p in candidates[:limit]
    ]


def _latest_files(root: Path, rel: str, *, limit: int = 5) -> list[dict[str, Any]]:
    base = root / rel
    if not base.exists():
        return []
    files = sorted([path for path in base.glob("*.json") if path.is_file()], key=lambda path: path.stat().st_mtime, reverse=True)
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "name": path.name,
            "mtime": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat(),
        }
        for path in files[:limit]
    ]


def _latest_task_return_machine_receipts(root: Path, *, limit: int = 5) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in _latest_files(root, "ION/05_context/current/chatgpt_connector/task_return_machine_receipts", limit=limit):
        payload = read_json(root / str(item.get("path") or ""))
        diagnosis = payload.get("diagnosis") if isinstance(payload.get("diagnosis"), Mapping) else {}
        row = dict(item)
        row.update({
            "receipt_source": payload.get("receipt_source"),
            "manual_ai_authored": payload.get("manual_ai_authored"),
            "accepted_for_carrier_intake": payload.get("accepted_for_carrier_intake"),
            "result": payload.get("result"),
            "classification": diagnosis.get("classification"),
            "summary": diagnosis.get("summary"),
            "task_return_packet_path": payload.get("task_return_packet_path"),
            "work_request_id": payload.get("work_request_id"),
        })
        rows.append(row)
    return rows


def _task_return_automation_diagnoses(root: Path, *, limit: int = 8) -> list[dict[str, Any]]:
    work_queue = read_json(root / CURRENT / "ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json")
    rows: list[dict[str, Any]] = []
    for request in listify(work_queue.get("requests")):
        if not isinstance(request, Mapping):
            continue
        diagnosis = request.get("settlement_relevant_automation_diagnosis")
        machine_receipt_path = request.get("settlement_relevant_machine_receipt_path")
        if not isinstance(diagnosis, Mapping):
            diagnosis = request.get("latest_task_return_automation_diagnosis")
        if not machine_receipt_path:
            machine_receipt_path = request.get("latest_task_return_machine_receipt_path")
        if not isinstance(diagnosis, Mapping) and not machine_receipt_path:
            continue
        if not isinstance(diagnosis, Mapping):
            diagnosis = {}
        rows.append({
            "request_id": request.get("request_id"),
            "status": request.get("status"),
            "classification": diagnosis.get("classification"),
            "summary": diagnosis.get("summary"),
            "next_action": diagnosis.get("next_action"),
            "finding_count": diagnosis.get("finding_count"),
            "manual_ai_receipt_required": diagnosis.get("manual_ai_receipt_required"),
            "automation_must_report": diagnosis.get("automation_must_report"),
            "machine_receipt_path": machine_receipt_path,
            "return_packet_path": request.get("settlement_relevant_return_packet_path") or request.get("latest_return_packet_path"),
        })
        if len(rows) >= limit:
            break
    return rows


def _latest_paths(root: Path, rel: str, *, limit: int = 8, suffixes: set[str] | None = None, recursive: bool = False) -> list[dict[str, Any]]:
    base = root / rel
    if not base.exists():
        return []
    iterator = base.rglob("*") if recursive else base.glob("*")
    files = [path for path in iterator if path.is_file() and (suffixes is None or path.suffix.lower() in suffixes)]
    files.sort(key=lambda path: path.stat().st_mtime if path.exists() else 0, reverse=True)
    return [
        {
            "path": path.relative_to(root).as_posix(),
            "name": path.name,
            "suffix": path.suffix.lower(),
            "bytes": path.stat().st_size if path.exists() else 0,
            "mtime": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat(),
        }
        for path in files[:limit]
    ]


def _latest_json_payloads(
    root: Path,
    rel: Path,
    *,
    limit: int = 8,
    name_contains: str | None = None,
) -> list[dict[str, Any]]:
    base = root / rel
    if not base.exists():
        return []
    files = [path for path in base.glob("*.json") if path.is_file()]
    if name_contains:
        needle = name_contains.lower()
        files = [path for path in files if needle in path.name.lower()]
    files.sort(key=lambda path: path.stat().st_mtime if path.exists() else 0, reverse=True)
    rows: list[dict[str, Any]] = []
    for path in files[: max(1, limit)]:
        payload = read_json(path)
        stat = path.stat()
        rows.append({
            "path": path.relative_to(root).as_posix(),
            "name": path.name,
            "mtime": datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0).isoformat(),
            "bytes": stat.st_size,
            "schema_id": payload.get("schema_id"),
            "status": payload.get("status") or payload.get("finding") or payload.get("verdict"),
            "operation": payload.get("operation"),
            "action_id": payload.get("action_id"),
            "intent": payload.get("intent"),
            "idempotency_key": payload.get("idempotency_key"),
            "created_at": payload.get("created_at") or payload.get("recorded_at"),
            "payload": payload,
        })
    return rows


def _tail_lines(path: Path, *, limit: int = 40) -> list[str]:
    text = _read_text(path)
    if not text:
        return []
    return text.splitlines()[-max(1, limit):]


def _pid_running(pid: int | None) -> bool:
    return bool(pid and pid > 0 and Path(f"/proc/{pid}").exists())


def _action_gateway_sync_summary(root: Path) -> dict[str, Any]:
    runtime_dir = root / ACTION_GATEWAY_RUNTIME_DIR
    pid_text = _read_text(runtime_dir / "action_gateway.pid").strip()
    try:
        pid = int(pid_text) if pid_text else None
    except ValueError:
        pid = None
    log_path = runtime_dir / "action_gateway.log"
    browser_queue_path = runtime_dir / "browser_queue.json"
    idempotency_ledger_path = runtime_dir / "idempotency_ledger.json"
    browser_queue = read_json(browser_queue_path)
    queue_packets = [item for item in listify(browser_queue.get("packets")) if isinstance(item, Mapping)]
    queue_packets.sort(key=lambda item: str(item.get("updated_at") or item.get("created_at") or ""), reverse=True)
    ledger = read_json(idempotency_ledger_path)
    ledger_entries = ledger.get("entries") if isinstance(ledger.get("entries"), Mapping) else {}
    idempotency_entries = [
        {"idempotency_key": key, **dict(value)}
        for key, value in ledger_entries.items()
        if isinstance(value, Mapping)
    ]
    idempotency_entries.sort(key=lambda item: str(item.get("recorded_at") or ""), reverse=True)
    recent_action_receipts = _latest_json_payloads(root, ACTION_GATEWAY_RECEIPTS_DIR, limit=16)
    recent_action_packets = _latest_json_payloads(root, CHATOPS_ACTIONS_DIR, limit=14)
    recent_service_receipts = _latest_json_payloads(root, RUNTIME_SERVICE_RECEIPTS_DIR, limit=10, name_contains="action_gateway")
    recent_test_receipts = _latest_json_payloads(root, RUNTIME_SERVICE_TEST_RECEIPTS_DIR, limit=10)
    return {
        "schema_id": "ion.browser_gpt.action_gateway_sync.v1",
        "status": "ready" if recent_action_receipts or queue_packets or idempotency_entries else "empty",
        "generated_at": utc_now(),
        "source": {
            "mode": "local_read_only_artifact_sync",
            "action_gateway_receipts_dir": ACTION_GATEWAY_RECEIPTS_DIR.as_posix(),
            "action_gateway_runtime_dir": ACTION_GATEWAY_RUNTIME_DIR.as_posix(),
            "chatops_actions_dir": CHATOPS_ACTIONS_DIR.as_posix(),
            "runtime_service_receipts_dir": RUNTIME_SERVICE_RECEIPTS_DIR.as_posix(),
            "runtime_service_test_receipts_dir": RUNTIME_SERVICE_TEST_RECEIPTS_DIR.as_posix(),
        },
        "summary": {
            "pid": pid,
            "pid_running": _pid_running(pid),
            "log_present": log_path.exists(),
            "queued_packet_count": len(queue_packets),
            "idempotency_entry_count": len(idempotency_entries),
            "recent_action_receipt_count": len(recent_action_receipts),
            "recent_action_packet_count": len(recent_action_packets),
            "recent_service_receipt_count": len(recent_service_receipts),
            "recent_test_receipt_count": len(recent_test_receipts),
        },
        "runtime": {
            "pid_path": (ACTION_GATEWAY_RUNTIME_DIR / "action_gateway.pid").as_posix(),
            "pid": pid,
            "pid_running": _pid_running(pid),
            "log_path": (ACTION_GATEWAY_RUNTIME_DIR / "action_gateway.log").as_posix(),
            "log_tail": _tail_lines(log_path, limit=30),
            "browser_queue_path": (ACTION_GATEWAY_RUNTIME_DIR / "browser_queue.json").as_posix(),
            "idempotency_ledger_path": (ACTION_GATEWAY_RUNTIME_DIR / "idempotency_ledger.json").as_posix(),
        },
        "browser_queue": {
            "schema_id": browser_queue.get("schema_id"),
            "killed": browser_queue.get("killed"),
            "auto_accept_actions": browser_queue.get("auto_accept_actions"),
            "packet_count": len(queue_packets),
            "packets": queue_packets[:12],
        },
        "idempotency_ledger": {
            "schema_id": ledger.get("schema_id"),
            "entry_count": len(idempotency_entries),
            "entries": idempotency_entries[:16],
        },
        "recent_action_receipts": recent_action_receipts,
        "recent_action_packets": recent_action_packets,
        "recent_service_receipts": recent_service_receipts,
        "recent_test_receipts": recent_test_receipts,
        "authority": {
            "read_only_projection": True,
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_fact(root: Path, rel_path: str | None) -> dict[str, Any]:
    row = {
        "path": rel_path,
        "exists": False,
        "bytes": None,
        "modified_at": None,
        "sha256": None,
    }
    if not rel_path:
        return row
    candidate = root / rel_path
    if not candidate.exists() or not candidate.is_file():
        return row
    stat = candidate.stat()
    row["exists"] = True
    row["bytes"] = int(stat.st_size)
    row["modified_at"] = datetime.fromtimestamp(stat.st_mtime, timezone.utc).replace(microsecond=0).isoformat()
    row["sha256"] = _sha256_file(candidate)
    return row


def _tail_preview(root: Path, rel_path: str | None, *, max_bytes: int = 640) -> dict[str, Any]:
    base = {
        "path": rel_path,
        "included": False,
        "shown_bytes": 0,
        "total_bytes": 0,
        "truncated": False,
        "text": "",
    }
    if not rel_path:
        return {**base, "finding": "path_missing"}
    target = root / rel_path
    if not target.exists() or not target.is_file():
        return {**base, "finding": "file_missing"}
    raw = target.read_bytes()
    bounded = max(64, min(max_bytes, 4096))
    tail = raw[-bounded:]
    return {
        "path": rel_path,
        "included": True,
        "shown_bytes": len(tail),
        "total_bytes": len(raw),
        "truncated": len(raw) > len(tail),
        "text": tail.decode("utf-8", errors="replace"),
    }


def _status_badge(status: str) -> str:
    normalized = status.lower()
    if "accepted" in normalized or normalized in {"active", "ready", "smoke_ready"}:
        return "ok"
    if "invalid" in normalized or "blocked" in normalized or "failed" in normalized or "deferred" in normalized:
        return "bad"
    if "running" in normalized or "started" in normalized or "prepared" in normalized:
        return "active"
    return "neutral"


def _worker_run_summary(root: Path, row: Mapping[str, Any]) -> dict[str, Any]:
    run_path = str(row.get("path") or "").strip()
    payload = read_json(root / run_path) if run_path else {}
    submit = payload.get("submit_result") if isinstance(payload.get("submit_result"), dict) else {}
    model_move = payload.get("codex_model_move") if isinstance(payload.get("codex_model_move"), dict) else {}
    lifecycle = listify(payload.get("worker_lifecycle_events"))
    latest_event = lifecycle[-1] if lifecycle and isinstance(lifecycle[-1], dict) else {}
    terminal_state = compact(latest_event.get("terminal_state"), "not-terminal")
    return {
        "run_id": payload.get("run_id") or row.get("run_id"),
        "request_id": payload.get("request_id") or row.get("request_id"),
        "request_path": payload.get("request_path"),
        "run_packet_path": run_path or payload.get("run_packet_path"),
        "status": payload.get("status") or row.get("status"),
        "status_badge": _status_badge(compact(payload.get("status") or row.get("status"), "unknown")),
        "terminal_state": terminal_state,
        "created_at": payload.get("created_at"),
        "started_at": payload.get("started_at"),
        "completed_at": payload.get("completed_at"),
        "mtime": row.get("mtime"),
        "selected_model": model_move.get("selected_model"),
        "selected_reasoning_effort": model_move.get("selected_reasoning_effort"),
        "usage_pool_id": model_move.get("usage_pool_id"),
        "model_move_id": model_move.get("model_move_id"),
        "routing_reasons": listify(model_move.get("selection_reason")),
        "context_proof_accepted": submit.get("context_proof_accepted"),
        "template_action_proof_accepted": submit.get("template_action_proof_accepted"),
        "return_template_valid": submit.get("return_template_valid"),
        "workload_diff_required": submit.get("workload_diff_required"),
        "workload_diff_present": submit.get("workload_diff_present"),
        "workload_diff_accepted": submit.get("workload_diff_accepted"),
        "task_return_packet_path": submit.get("packet_path"),
    }


def _fanout_parent_child_rows(root: Path, result: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scenario in [item for item in listify(result.get("scenarios")) if isinstance(item, dict)]:
        parent_path = str(scenario.get("parent_receipt_path") or "").strip()
        if not parent_path:
            continue
        parent = read_json(root / parent_path)
        for child in [item for item in listify(parent.get("child_receipt_paths")) if isinstance(item, dict)]:
            rows.append(
                {
                    "scenario": scenario.get("scenario"),
                    "child_id": child.get("child_id"),
                    "lease_receipt_path": child.get("lease_receipt_path"),
                    "heartbeat_receipt_path": child.get("heartbeat_receipt_path"),
                    "worker_context_awareness_receipt_path": child.get("worker_context_awareness_receipt_path"),
                    "parent_receipt_path": parent_path,
                }
            )
    return rows[:24]


def build_worker_cockpit_view_model(ion_root: str | Path = ".") -> dict[str, Any]:
    root = Path(ion_root).resolve()
    runner = build_codex_queue_runner_status(root, reconcile=False)
    telemetry = runner.get("live_worker_telemetry") if isinstance(runner.get("live_worker_telemetry"), dict) else {}
    worker_trace = telemetry.get("observability_trace") if isinstance(telemetry.get("observability_trace"), dict) else {}
    preferred_preview = telemetry.get("preferred_preview") if isinstance(telemetry.get("preferred_preview"), dict) else {}
    active_run_packet = str(telemetry.get("run_packet_path") or "").strip()
    active_run = read_json(root / active_run_packet) if active_run_packet else {}
    submit = active_run.get("submit_result") if isinstance(active_run.get("submit_result"), dict) else {}
    model_move = active_run.get("codex_model_move") if isinstance(active_run.get("codex_model_move"), dict) else {}
    awareness_path = str(telemetry.get("worker_context_awareness_receipt_path") or "").strip()
    awareness = read_json(root / awareness_path) if awareness_path else {}
    required_reads = [item for item in listify(awareness.get("required_context_reads")) if isinstance(item, dict)]
    ready_reads = [item for item in required_reads if str(item.get("status") or "") == "READY"]
    missing_reads = [item for item in required_reads if str(item.get("status") or "") != "READY"]
    active_status = compact(telemetry.get("phase_status") or telemetry.get("run_status"), "idle")
    pid = telemetry.get("active_worker_pid") or active_run.get("pid")
    active_running = bool(telemetry.get("active_process_running"))
    stale = bool(telemetry.get("stale_active_reference_detected"))
    non_terminal = active_status not in {"terminal-accepted", "terminal-blocked", "terminal-failed", "template-invalid"}
    zombie = bool(pid and not active_running and non_terminal)

    receipt_chain = [
        {"name": "prompt_md", **_file_fact(root, str(active_run.get("prompt_path") or "") or None)},
        {"name": "run_json", **_file_fact(root, active_run_packet or None)},
        {"name": "context_receipt_json", **_file_fact(root, str(active_run.get("context_receipt_path") or "") or None)},
        {"name": "worker_context_awareness_receipt_json", **_file_fact(root, awareness_path or None)},
        {"name": "stdout_log", **_file_fact(root, str(active_run.get("stdout_path") or "") or None)},
        {"name": "stderr_log", **_file_fact(root, str(active_run.get("stderr_path") or "") or None)},
        {
            "name": "worker_stdout_log",
            **_file_fact(root, (f"{active_run.get('run_dir')}/worker_stdout.log" if active_run.get("run_dir") else None)),
        },
        {
            "name": "worker_stderr_log",
            **_file_fact(root, (f"{active_run.get('run_dir')}/worker_stderr.log" if active_run.get("run_dir") else None)),
        },
        {"name": "latest_return_md", **_file_fact(root, str(active_run.get("last_message_path") or "") or None)},
        {"name": "task_return_packet_json", **_file_fact(root, str(submit.get("packet_path") or "") or None)},
    ]

    logs = [
        {
            "name": "latest_return",
            **_tail_preview(root, str(active_run.get("last_message_path") or "") or None),
        },
        {
            "name": "stdout",
            **_tail_preview(root, str(active_run.get("stdout_path") or "") or None),
        },
        {
            "name": "stderr",
            **_tail_preview(root, str(active_run.get("stderr_path") or "") or None),
        },
        {
            "name": "worker_stdout",
            **_tail_preview(root, f"{active_run.get('run_dir')}/worker_stdout.log" if active_run.get("run_dir") else None),
        },
        {
            "name": "worker_stderr",
            **_tail_preview(root, f"{active_run.get('run_dir')}/worker_stderr.log" if active_run.get("run_dir") else None),
        },
    ]

    latest_runs = [
        _worker_run_summary(root, row)
        for row in [item for item in listify(runner.get("latest_runs")) if isinstance(item, dict)]
    ]

    fanout_status = build_kernel_fanout_carrier_dryrun_status(root)
    fanout_result_path = str(fanout_status.get("latest_dryrun_result_path") or "").strip()
    fanout_result = read_json(root / fanout_result_path) if fanout_result_path else {}
    settlement_rows: list[dict[str, Any]] = []
    for file_row in _latest_paths(root, WORKER_SETTLEMENT_DIR.as_posix(), limit=6, suffixes={".json"}):
        payload = read_json(root / str(file_row.get("path")))
        settlement_rows.append(
            {
                "path": file_row.get("path"),
                "mtime": file_row.get("mtime"),
                "status": payload.get("status") or payload.get("verdict"),
                "required_unrestricted_validation": payload.get("required_unrestricted_validation"),
                "test_validation": payload.get("test_validation"),
            }
        )
    settlement_blockers = [
        row
        for row in settlement_rows
        if any(token in str(row.get("status") or "").upper() for token in ("BLOCKED", "DEFERRED", "INVALID"))
    ]

    supabase_events: list[dict[str, Any]] = []
    for file_row in _latest_paths(root, SUPABASE_EVENT_RECEIPTS_DIR.as_posix(), limit=8, suffixes={".json"}):
        payload = read_json(root / str(file_row.get("path")))
        remote = payload.get("remote_result") if isinstance(payload.get("remote_result"), dict) else {}
        supabase_events.append(
            {
                "path": file_row.get("path"),
                "mtime": file_row.get("mtime"),
                "event_type": remote.get("event_type"),
                "packet_id": remote.get("packet_id"),
                "event_id": remote.get("event_id"),
            }
        )

    return {
        "schema_id": "ion.worker_cockpit_view_model.v1",
        "generated_at": utc_now(),
        "read_only": {
            "view_only_default": True,
            "mutation_controls_enabled": False,
            "production_authority": False,
            "live_execution_authority": False,
        },
        "filters": {
            "search_fields": ["status", "run_id", "request_id", "model", "time"],
            "status_options": ["running", "accepted", "blocked", "template-invalid", "failed", "deferred"],
            "sort_options": ["time_desc", "time_asc", "status", "model", "run_id"],
        },
        "active_worker": {
            "status": active_status,
            "status_badge": _status_badge(active_status),
            "pid": pid,
            "run_id": telemetry.get("active_run_id"),
            "request_id": telemetry.get("request_id"),
            "age_seconds": telemetry.get("elapsed_seconds"),
            "heartbeat_at": telemetry.get("last_heartbeat_or_event_at"),
            "active_process_running": active_running,
            "stale_active_reference_detected": stale,
            "zombie_state_detected": zombie,
            "preferred_preview_target": preferred_preview.get("target"),
            "next_recommended_action": worker_trace.get("next_recommended_action"),
        },
        "latest_worker_runs": latest_runs[:12],
        "machine_sign_in": {
            "status": telemetry.get("worker_sign_in_status") or awareness.get("status"),
            "worker_authored": awareness.get("worker_authored"),
            "worker_context_awareness_receipt_path": awareness_path or None,
            "worker_context_awareness_receipt_sha256": telemetry.get("worker_context_awareness_receipt_sha256"),
            "machine_attestation_sha256": awareness.get("machine_attestation_sha256"),
            "required_context_reads_total": len(required_reads),
            "required_context_reads_ready": len(ready_reads),
            "required_context_reads_missing": len(missing_reads),
            "missing_required_context_paths": awareness.get("missing_required_context_paths") or [],
            "context_receipt_path": awareness.get("context_receipt_path"),
            "context_receipt_sha256": awareness.get("context_receipt_sha256"),
        },
        "receipt_chain": receipt_chain,
        "model_move_summary": {
            "selected_model": model_move.get("selected_model"),
            "selected_reasoning_effort": model_move.get("selected_reasoning_effort"),
            "usage_pool_id": model_move.get("usage_pool_id"),
            "usage_pool_authority": model_move.get("usage_pool_authority"),
            "model_move_id": model_move.get("model_move_id"),
            "routing_reasons": listify(model_move.get("selection_reason")),
            "summary": active_run.get("codex_model_move_summary"),
        },
        "proof_gate": {
            "context_proof_accepted": submit.get("context_proof_accepted"),
            "template_action_proof_accepted": submit.get("template_action_proof_accepted"),
            "return_template_valid": submit.get("return_template_valid"),
            "workload_diff_required": submit.get("workload_diff_required"),
            "workload_diff_present": submit.get("workload_diff_present"),
            "workload_diff_accepted": submit.get("workload_diff_accepted"),
            "terminal_intake_state": telemetry.get("terminal_intake_result", {}).get("state")
            if isinstance(telemetry.get("terminal_intake_result"), dict)
            else None,
        },
        "logs": logs,
        "observability_trace": worker_trace,
        "fanout": {
            "status": fanout_status,
            "scenario_rows": [item for item in listify(fanout_result.get("scenarios")) if isinstance(item, dict)][:8],
            "parent_child_rows": _fanout_parent_child_rows(root, fanout_result),
            "timeout_fail_closed_summary": fanout_status.get("timeout_fail_closed_summary"),
            "conflict_lock_summary": fanout_status.get("conflict_lock_summary"),
        },
        "event_links": {
            "supabase_receipts": supabase_events,
        },
        "settlement": {
            "rows": settlement_rows,
            "blockers": settlement_blockers,
        },
        "raw_worker_status": runner,
    }


def _read_text(path: Path) -> str:
    try:
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _profile_scalar(text: str, key: str) -> str | None:
    prefix = f"{key}:"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            value = stripped[len(prefix):].strip().strip("\"'")
            return value or None
    return None


def _chatgpt_browser_profile_summary(root: Path) -> dict[str, Any]:
    path = Path("ION/03_registry/chatgpt_browser_carrier_profile.yaml")
    text = _read_text(root / path)
    return {
        "profile_path": path.as_posix(),
        "carrier_id": _profile_scalar(text, "carrier_id"),
        "project_facing_callsign": _profile_scalar(text, "project_facing_callsign"),
        "callsign_authority": _profile_scalar(text, "callsign_authority"),
        "callsign_decision_receipt": _profile_scalar(text, "callsign_decision_receipt"),
    }


def _chatgpt_browser_mcp_summary(root: Path) -> dict[str, Any]:
    contract = read_json(root / CURRENT / "CHATGPT_BROWSER_MCP_CONNECTOR_CONTRACT_V120.json")
    http_preview = read_json(root / CURRENT / "CHATGPT_BROWSER_HTTP_MCP_PREVIEW_V121.json")
    tunnel = read_json(root / CURRENT / "CHATGPT_BROWSER_CLOUDFLARE_TUNNEL_V122.json")
    carrier_queue = read_json(root / CURRENT / "ACTIVE_CARRIER_MESSAGE_QUEUE.json")
    work_queue = read_json(root / CURRENT / "ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json")
    profile = _chatgpt_browser_profile_summary(root)
    uploads = _latest_files(root, "ION/05_context/current/chatgpt_connector/artifact_uploads")
    upload_payloads = [read_json(root / item["path"]) for item in uploads]
    upload_status_counts: dict[str, int] = {}
    for payload in upload_payloads:
        status = compact(payload.get("status"), "unknown")
        upload_status_counts[status] = upload_status_counts.get(status, 0) + 1
    tools = listify(contract.get("allowed_tools"))
    first_parity = [
        "ion_file_put_text",
        "ion_artifact_upload_init",
        "ion_artifact_upload_chunk",
        "ion_artifact_upload_commit",
        "ion_carrier_message_send",
        "ion_carrier_message_poll",
        "ion_carrier_message_ack",
    ]
    next_visibility = [
        "ion_file_read",
        "ion_file_search",
        "ion_tree_list",
        "ion_registry_read",
        "ion_template_read",
        "ion_context_compile",
        "ion_receipt_hydrate",
        "ion_tool_manifest",
    ]
    agent_tools = [
        "ion_agent_list",
        "ion_agent_status",
        "ion_agent_result",
        "ion_agent_queue",
        "ion_agent_spawn_plan",
        "ion_swarm_status",
        "ion_agent_invoke",
        "ion_agent_cancel",
        "ion_swarm_step_once",
    ]
    agent_broker = build_agent_broker_status(root)
    task_return_machine_receipts = _latest_task_return_machine_receipts(root)
    task_return_automation_diagnoses = _task_return_automation_diagnoses(root)
    return {
        "schema_id": "ion.chatgpt_browser_mcp_cockpit_summary.v1",
        "connector_contract_verdict": contract.get("verdict"),
        "http_preview_verdict": http_preview.get("verdict"),
        "transport_state": tunnel.get("transport_state") or tunnel.get("connector_state"),
        "active_connector_url": tunnel.get("active_connector_url"),
        "carrier_id": profile.get("carrier_id"),
        "project_facing_callsign": profile.get("project_facing_callsign"),
        "callsign_authority": profile.get("callsign_authority"),
        "callsign_decision_receipt": profile.get("callsign_decision_receipt"),
        "tool_count": len(tools),
        "first_parity_tools_present": sorted(set(first_parity) & set(tools)),
        "visibility_tools_present": sorted(set(next_visibility) & set(tools)),
        "agent_invocation_tools_present": sorted(set(agent_tools) & set(tools)),
        "carrier_message_count": len(listify(carrier_queue.get("messages"))),
        "codex_work_request_count": work_queue.get("request_count"),
        "latest_carrier_messages": _latest_files(root, "ION/05_context/current/chatgpt_connector/carrier_messages"),
        "latest_task_returns": _latest_files(root, "ION/05_context/current/chatgpt_connector/task_returns"),
        "latest_task_return_machine_receipts": task_return_machine_receipts,
        "latest_task_return_automation_diagnoses": task_return_automation_diagnoses,
        "latest_agent_invocations": _latest_files(root, "ION/05_context/current/chatgpt_connector/agent_invocations"),
        "latest_artifact_receipts": _latest_files(root, "ION/05_context/current/chatgpt_connector/artifact_receipts"),
        "latest_decisions": _latest_files(root, "ION/05_context/current/chatgpt_connector/decisions"),
        "codex_queue_runner": build_codex_queue_runner_status(root, reconcile=False),
        "agent_invocation_broker": agent_broker,
        "artifact_upload_status_counts": upload_status_counts,
        "adapter_gap_not_core_failure": True,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _chatgpt_sandbox_returns_summary(root: Path) -> dict[str, Any]:
    projection = build_sandbox_return_queue_projection(root)
    returns = [row for row in listify(projection.get("returns")) if isinstance(row, dict)]
    status_counts: dict[str, int] = {}
    for row in returns:
        status = compact(row.get("status"), "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "schema_id": "ion.chatgpt_sandbox_returns_cockpit_summary.v1",
        "queue_path": projection.get("queue_path"),
        "inbox_root": projection.get("inbox_root"),
        "return_count": projection.get("return_count"),
        "status_counts": status_counts,
        "latest_returns": returns[:10],
        "direct_apply_authority": False,
        "git_push_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _safe_record_list(value: Any, limit: int = 5) -> list[dict[str, Any]]:
    return [item for item in listify(value) if isinstance(item, dict)][:limit]


def _compact_file_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "name": record.get("name") or Path(str(record.get("path", ""))).name,
            "path": record.get("path"),
            "mtime": record.get("mtime") or record.get("updated_at") or record.get("created_at"),
            "status": record.get("status"),
        }
        for record in records
    ]


def _joc_comms_projection(
    root: Path,
    *,
    operator_items: list[dict[str, Any]],
    steward_items: list[dict[str, Any]],
    return_records: list[dict[str, Any]],
    agent_control_plane: Mapping[str, Any],
    chatgpt_browser_mcp: Mapping[str, Any],
    receipts: list[dict[str, Any]],
) -> dict[str, Any]:
    source_surfaces = {
        "operator_queue": CURRENT / "ACTIVE_OPERATOR_MESSAGE_QUEUE.json",
        "carrier_messages": CURRENT / "ACTIVE_CARRIER_MESSAGE_QUEUE.json",
        "steward_integration": CURRENT / "ACTIVE_STEWARD_INTEGRATION_QUEUE.json",
        "task_returns": CURRENT / "ACTIVE_CARRIER_TASK_RETURN_LEDGER.json",
        "agent_invocations": CURRENT / "chatgpt_connector/agent_invocations",
        "codex_queue": CURRENT / "ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json",
        "browser_queue": CURRENT / "CHATGPT_BROWSER_HTTP_MCP_PREVIEW_V121.json",
        "receipts": SIGNALS,
    }
    source_present = {key: (root / rel).exists() for key, rel in source_surfaces.items()}
    source_refs = {key: rel.as_posix() for key, rel in source_surfaces.items()}
    carrier_queue = read_json(root / source_surfaces["carrier_messages"])
    codex_queue = read_json(root / source_surfaces["codex_queue"])
    communications = (
        agent_control_plane.get("communications")
        if isinstance(agent_control_plane.get("communications"), Mapping)
        else {}
    )
    team_comms = communications.get("team_comms") if isinstance(communications.get("team_comms"), Mapping) else {}
    team_channels = [row for row in listify(team_comms.get("channels")) if isinstance(row, Mapping)]
    team_threads = [row for row in listify(team_comms.get("threads")) if isinstance(row, Mapping)]
    team_messages = [row for row in listify(team_comms.get("recent_messages")) if isinstance(row, Mapping)]
    team_agent_home_views = [row for row in listify(team_comms.get("agent_home_views")) if isinstance(row, Mapping)]
    latest_invocations = [
        row for row in listify(chatgpt_browser_mcp.get("latest_agent_invocations")) if isinstance(row, Mapping)
    ]
    browser_queue_hints = [
        row for row in listify(chatgpt_browser_mcp.get("latest_decisions")) if isinstance(row, Mapping)
    ]
    channels: list[dict[str, Any]] = []
    threads: list[dict[str, Any]] = []
    messages: list[dict[str, Any]] = []
    participants: list[dict[str, Any]] = []
    pins: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []

    def add_channel(
        *,
        channel_id: str,
        label: str,
        source_surface: str,
        channel_kind: str,
        required_tool_or_route: str,
        write_policy: str,
        item_count: int,
    ) -> None:
        channels.append(
            {
                "channel_id": channel_id,
                "label": label,
                "source_surface": source_surface,
                "channel_kind": channel_kind,
                "authority_scope": "candidate_state_only",
                "purpose": f"Read-only {label} projection over {channel_kind.replace('_', ' ')} surfaces.",
                "unread_or_pending_count": item_count,
                "required_tool_or_route": required_tool_or_route,
                "write_policy": write_policy,
                "production_authority": False,
                "live_execution_authority": False,
                "write_authority": False,
            }
        )

    add_channel(
        channel_id="team",
        label="Team",
        source_surface=source_refs["agent_invocations"],
        channel_kind="domain_room",
        required_tool_or_route="agent_control_plane.team_comms",
        write_policy="agent_comms_routes_require_explicit_operator_action",
        item_count=len(team_messages),
    )
    add_channel(
        channel_id="operator_queue",
        label="Operator Queue",
        source_surface=source_refs["operator_queue"],
        channel_kind="operator_queue",
        required_tool_or_route="ACTIVE_OPERATOR_MESSAGE_QUEUE",
        write_policy="operator_message_queue_routes_only",
        item_count=len(operator_items),
    )
    add_channel(
        channel_id="carrier_messages",
        label="Carrier Messages",
        source_surface=source_refs["carrier_messages"],
        channel_kind="carrier_messages",
        required_tool_or_route="ion_carrier_message_poll",
        write_policy="ion_carrier_message_send_requires_confirmation",
        item_count=len([row for row in listify(carrier_queue.get("messages")) if isinstance(row, Mapping)]),
    )
    add_channel(
        channel_id="steward_integration",
        label="Steward Integration",
        source_surface=source_refs["steward_integration"],
        channel_kind="steward_integration",
        required_tool_or_route="ACTIVE_STEWARD_INTEGRATION_QUEUE",
        write_policy="steward_gate_only",
        item_count=len(steward_items),
    )
    add_channel(
        channel_id="task_returns",
        label="Task Returns",
        source_surface=source_refs["task_returns"],
        channel_kind="task_returns",
        required_tool_or_route="ACTIVE_CARRIER_TASK_RETURN_LEDGER",
        write_policy="ion_submit_task_return_requires_confirmation_and_proof",
        item_count=len(return_records),
    )
    add_channel(
        channel_id="agent_invocations",
        label="Agent Invocations",
        source_surface=source_refs["agent_invocations"],
        channel_kind="agent_invocations",
        required_tool_or_route="ion_agent_status",
        write_policy="ion_agent_invoke_requires_confirmation",
        item_count=len(latest_invocations),
    )
    add_channel(
        channel_id="codex_queue",
        label="Codex Queue",
        source_surface=source_refs["codex_queue"],
        channel_kind="codex_queue",
        required_tool_or_route="ion_queue_status",
        write_policy="codex_work_packet_or_process_requires_confirmation",
        item_count=len([row for row in listify(codex_queue.get("requests")) if isinstance(row, Mapping)]),
    )
    add_channel(
        channel_id="browser_queue",
        label="Browser Queue",
        source_surface=source_refs["browser_queue"],
        channel_kind="browser_queue",
        required_tool_or_route="chatgpt_browser_http_mcp_preview",
        write_policy="gateway_or_browser_queue_authority_only",
        item_count=len(browser_queue_hints),
    )
    add_channel(
        channel_id="receipts",
        label="Receipts",
        source_surface=source_refs["receipts"],
        channel_kind="receipts",
        required_tool_or_route="ion_receipt_hydrate",
        write_policy="read_only_by_default",
        item_count=len(receipts),
    )

    for key, rel in source_refs.items():
        if source_present.get(key):
            continue
        blockers.append(
            {
                "blocker_id": f"missing_source:{key}",
                "status": "missing_source",
                "channel_id": key,
                "source_surface": rel,
                "detail": "source surface missing; projection falls back to empty rows",
                "production_authority": False,
                "live_execution_authority": False,
            }
        )

    for channel in team_channels:
        channel_id = compact(channel.get("channel_id"), "team")
        thread_count = sum(1 for row in team_threads if compact(row.get("channel_id"), "team") == channel_id)
        channels.append(
            {
                "channel_id": channel_id,
                "label": compact(channel.get("label"), channel_id),
                "source_surface": source_refs["agent_invocations"],
                "channel_kind": "domain_room",
                "authority_scope": "candidate_state_only",
                "purpose": compact(channel.get("purpose"), compact(channel.get("kind"), "team room")),
                "unread_or_pending_count": int(channel.get("pending_count") or channel.get("unread_count") or 0),
                "thread_count": thread_count,
                "required_tool_or_route": "agent_comms.team_projection",
                "write_policy": "agent_comms_routes_require_explicit_operator_action",
                "production_authority": False,
                "live_execution_authority": False,
                "write_authority": False,
            }
        )

    for thread in team_threads:
        thread_id = compact(thread.get("thread_id"), "")
        if not thread_id:
            continue
        threads.append(
            {
                "thread_id": thread_id,
                "channel_id": compact(thread.get("channel_id"), "team"),
                "title": compact(thread.get("subject"), thread_id),
                "subject": compact(thread.get("subject"), thread_id),
                "thread_kind": compact(thread.get("kind"), "domain_thread"),
                "source_refs": [text for text in listify(thread.get("source_refs")) if isinstance(text, str)],
                "context_refs": [text for text in listify(thread.get("context_refs")) if isinstance(text, str)],
                "receipt_refs": [text for text in listify(thread.get("receipt_refs")) if isinstance(text, str)],
                "status": compact(thread.get("status"), "active"),
                "next_allowed_actions": ["poll", "open_context", "open_receipt"],
                "authority_boundary": "read_only_projection",
                "message_count": int(thread.get("message_count") or 0),
                "latest_summary": compact(thread.get("latest_summary"), compact(thread.get("status"), "active")),
                "updated_at": thread.get("updated_at") or thread.get("created_at"),
                "production_authority": False,
                "live_execution_authority": False,
            }
        )

    for message in team_messages:
        message_id = compact(message.get("message_id"), "")
        thread_id = compact(message.get("thread_id"), "")
        if not message_id or not thread_id:
            continue
        messages.append(
            {
                "message_id": message_id,
                "thread_id": thread_id,
                "channel_id": compact(message.get("channel_id"), "team"),
                "sender_id": compact(message.get("from_role"), "agent"),
                "sender_kind": "agent",
                "recipient": listify(message.get("to_roles")),
                "body": compact(message.get("body"), compact(message.get("summary"), "")),
                "message_type": compact(message.get("message_kind"), "message"),
                "message_kind": compact(message.get("message_kind"), "message"),
                "subject": compact(message.get("subject"), compact(message.get("message_kind"), "message")),
                "from_role": compact(message.get("from_role"), "agent"),
                "source_path": message.get("path"),
                "source_refs": [text for text in listify(message.get("source_refs")) if isinstance(text, str)],
                "context_refs": [text for text in listify(message.get("context_refs")) if isinstance(text, str)],
                "receipt_refs": [text for text in listify(message.get("receipt_refs")) if isinstance(text, str)],
                "status": compact(message.get("status"), "sent"),
                "acked_by": listify(message.get("acked_by")),
                "created_at": message.get("created_at"),
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
                "work_panel": message.get("work_panel") if isinstance(message.get("work_panel"), Mapping) else {},
            }
        )

    for item in operator_items:
        item_id = compact(item.get("id") or item.get("message_id"), hashlib.sha256(json.dumps(item, sort_keys=True).encode("utf-8")).hexdigest()[:12])
        thread_id = f"operator_queue:{item_id}"
        threads.append(
            {
                "thread_id": thread_id,
                "channel_id": "operator_queue",
                "title": compact(item.get("subject"), "Operator queue item"),
                "subject": compact(item.get("subject"), "Operator queue item"),
                "thread_kind": "operator_queue_item",
                "source_refs": [source_refs["operator_queue"]],
                "context_refs": [compact(item.get("context_package_path"), "")] if item.get("context_package_path") else [],
                "receipt_refs": [],
                "status": compact(item.get("status"), "pending"),
                "next_allowed_actions": ["poll", "open_context"],
                "authority_boundary": "read_only_projection",
                "message_count": 1,
                "latest_summary": compact(item.get("text"), compact(item.get("objective"), "operator item")),
                "updated_at": item.get("updated_at") or item.get("created_at"),
                "production_authority": False,
                "live_execution_authority": False,
            }
        )
        messages.append(
            {
                "message_id": f"operator_message:{item_id}",
                "thread_id": thread_id,
                "channel_id": "operator_queue",
                "sender_id": "operator",
                "sender_kind": "human_operator",
                "recipient": ["steward", "carrier"],
                "body": compact(item.get("text"), compact(item.get("objective"), "operator queue item")),
                "message_type": "operator_intent",
                "message_kind": "operator_intent",
                "subject": compact(item.get("subject"), "operator intent"),
                "from_role": "operator",
                "source_path": source_refs["operator_queue"],
                "source_refs": [source_refs["operator_queue"]],
                "context_refs": [compact(item.get("context_package_path"), "")] if item.get("context_package_path") else [],
                "receipt_refs": [],
                "status": compact(item.get("status"), "pending"),
                "acked_by": [],
                "created_at": item.get("created_at") or item.get("updated_at"),
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        )

    for row in [item for item in listify(carrier_queue.get("messages")) if isinstance(item, Mapping)]:
        message_id = compact(row.get("message_id"), hashlib.sha256(json.dumps(row, sort_keys=True).encode("utf-8")).hexdigest()[:12])
        thread_label = compact(row.get("channel"), compact(row.get("thread_id"), "carrier"))
        thread_id = f"carrier_messages:{thread_label}"
        threads.append(
            {
                "thread_id": thread_id,
                "channel_id": "carrier_messages",
                "title": f"Carrier {thread_label}",
                "subject": f"Carrier {thread_label}",
                "thread_kind": "carrier_message_stream",
                "source_refs": [source_refs["carrier_messages"]],
                "context_refs": [compact(row.get("context_ref"), "")] if row.get("context_ref") else [],
                "receipt_refs": [compact(row.get("receipt_ref"), "")] if row.get("receipt_ref") else [],
                "status": compact(row.get("status"), "pending"),
                "next_allowed_actions": ["poll", "open_context", "open_receipt"],
                "authority_boundary": "read_only_projection",
                "message_count": 1,
                "latest_summary": compact(row.get("body"), "carrier message"),
                "updated_at": row.get("updated_at") or row.get("created_at"),
                "production_authority": False,
                "live_execution_authority": False,
            }
        )
        messages.append(
            {
                "message_id": f"carrier_message:{message_id}",
                "thread_id": thread_id,
                "channel_id": "carrier_messages",
                "sender_id": compact(row.get("from_carrier"), "carrier"),
                "sender_kind": "carrier",
                "recipient": [compact(row.get("to_carrier"), "carrier")],
                "body": compact(row.get("body"), "carrier message"),
                "message_type": compact(row.get("kind"), "carrier_message"),
                "message_kind": compact(row.get("kind"), "carrier_message"),
                "subject": compact(row.get("channel"), "carrier message"),
                "from_role": compact(row.get("from_carrier"), "carrier"),
                "source_path": source_refs["carrier_messages"],
                "source_refs": [source_refs["carrier_messages"]],
                "context_refs": [compact(row.get("context_ref"), "")] if row.get("context_ref") else [],
                "receipt_refs": [compact(row.get("receipt_ref"), "")] if row.get("receipt_ref") else [],
                "status": compact(row.get("status"), "pending"),
                "acked_by": listify(row.get("acked_by")),
                "created_at": row.get("created_at") or row.get("updated_at"),
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        )

    for item in steward_items:
        ref = compact(item.get("path"), compact(item.get("role"), "steward"))
        thread_id = f"steward_integration:{hashlib.sha256(ref.encode('utf-8')).hexdigest()[:12]}"
        threads.append(
            {
                "thread_id": thread_id,
                "channel_id": "steward_integration",
                "title": compact(item.get("summary"), "Steward integration item"),
                "subject": compact(item.get("summary"), "Steward integration item"),
                "thread_kind": "steward_integration_item",
                "source_refs": [source_refs["steward_integration"]],
                "context_refs": [],
                "receipt_refs": [compact(item.get("path"), "")] if item.get("path") else [],
                "status": compact(item.get("status"), "queued"),
                "next_allowed_actions": ["poll", "request_steward_review", "open_receipt"],
                "authority_boundary": "steward_gate_only",
                "message_count": 1,
                "latest_summary": compact(item.get("summary"), compact(item.get("path"), "steward item")),
                "updated_at": item.get("updated_at") or item.get("created_at"),
                "production_authority": False,
                "live_execution_authority": False,
            }
        )
        messages.append(
            {
                "message_id": f"steward_item:{thread_id.split(':', 1)[1]}",
                "thread_id": thread_id,
                "channel_id": "steward_integration",
                "sender_id": compact(item.get("role"), "steward"),
                "sender_kind": "steward",
                "recipient": ["operator"],
                "body": compact(item.get("summary"), compact(item.get("path"), "steward integration item")),
                "message_type": "steward_integration",
                "message_kind": "steward_integration",
                "subject": compact(item.get("status"), "steward queue"),
                "from_role": compact(item.get("role"), "steward"),
                "source_path": source_refs["steward_integration"],
                "source_refs": [source_refs["steward_integration"]],
                "context_refs": [],
                "receipt_refs": [compact(item.get("path"), "")] if item.get("path") else [],
                "status": compact(item.get("status"), "queued"),
                "acked_by": [],
                "created_at": item.get("created_at") or item.get("updated_at"),
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        )

    for idx, record in enumerate(return_records, start=1):
        role = compact(record.get("role"), f"worker_{idx}")
        row_index = compact(record.get("index"), str(idx))
        thread_id = f"task_returns:{role.lower()}:{row_index}"
        decision = compact(record.get("decision"), "pending")
        threads.append(
            {
                "thread_id": thread_id,
                "channel_id": "task_returns",
                "title": f"Return {role}#{row_index}",
                "subject": f"Task return {role}",
                "thread_kind": "task_return",
                "source_refs": [source_refs["task_returns"]],
                "context_refs": [compact(record.get("context_package_path"), "")] if record.get("context_package_path") else [],
                "receipt_refs": [compact(record.get("task_output_path"), "")] if record.get("task_output_path") else [],
                "status": decision,
                "next_allowed_actions": ["poll", "open_receipt"],
                "authority_boundary": "proof_gate_required",
                "message_count": 1,
                "latest_summary": decision,
                "updated_at": record.get("updated_at") or record.get("created_at"),
                "production_authority": False,
                "live_execution_authority": False,
            }
        )
        messages.append(
            {
                "message_id": f"task_return:{role.lower()}:{row_index}",
                "thread_id": thread_id,
                "channel_id": "task_returns",
                "sender_id": role,
                "sender_kind": "codex_worker",
                "recipient": ["steward", "operator"],
                "body": compact(record.get("summary"), decision),
                "message_type": "task_return",
                "message_kind": "task_return",
                "subject": compact(record.get("task_output_path"), decision),
                "from_role": role,
                "source_path": source_refs["task_returns"],
                "source_refs": [source_refs["task_returns"]],
                "context_refs": [compact(record.get("context_package_path"), "")] if record.get("context_package_path") else [],
                "receipt_refs": [compact(record.get("task_output_path"), "")] if record.get("task_output_path") else [],
                "status": decision,
                "acked_by": [],
                "created_at": record.get("created_at") or record.get("updated_at"),
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        )

    for row in latest_invocations:
        invocation_path = compact(row.get("path"), "")
        invocation_id = compact(row.get("name"), invocation_path or "invocation")
        thread_id = f"agent_invocations:{invocation_id}"
        threads.append(
            {
                "thread_id": thread_id,
                "channel_id": "agent_invocations",
                "title": invocation_id,
                "subject": "Agent invocation",
                "thread_kind": "agent_invocation",
                "source_refs": [invocation_path] if invocation_path else [source_refs["agent_invocations"]],
                "context_refs": [],
                "receipt_refs": [invocation_path] if invocation_path else [],
                "status": "recorded",
                "next_allowed_actions": ["poll", "open_receipt"],
                "authority_boundary": "confirmation_gated_invocation",
                "message_count": 1,
                "latest_summary": invocation_id,
                "updated_at": row.get("mtime"),
                "production_authority": False,
                "live_execution_authority": False,
            }
        )
        messages.append(
            {
                "message_id": f"agent_invocation:{invocation_id}",
                "thread_id": thread_id,
                "channel_id": "agent_invocations",
                "sender_id": "system",
                "sender_kind": "system_projection",
                "recipient": ["operator"],
                "body": invocation_id,
                "message_type": "agent_invocation",
                "message_kind": "agent_invocation",
                "subject": compact(row.get("name"), invocation_id),
                "from_role": "system",
                "source_path": invocation_path or source_refs["agent_invocations"],
                "source_refs": [invocation_path] if invocation_path else [source_refs["agent_invocations"]],
                "context_refs": [],
                "receipt_refs": [invocation_path] if invocation_path else [],
                "status": "recorded",
                "acked_by": [],
                "created_at": row.get("mtime"),
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        )

    for request in [row for row in listify(codex_queue.get("requests")) if isinstance(row, Mapping)]:
        request_id = compact(request.get("request_id"), "")
        if not request_id:
            continue
        thread_id = f"codex_queue:{request_id}"
        threads.append(
            {
                "thread_id": thread_id,
                "channel_id": "codex_queue",
                "title": request_id,
                "subject": compact(request.get("objective"), request_id),
                "thread_kind": "codex_work_request",
                "source_refs": [source_refs["codex_queue"]],
                "context_refs": [compact(request.get("request_path"), "")] if request.get("request_path") else [],
                "receipt_refs": [compact(request.get("latest_return_packet_path"), "")] if request.get("latest_return_packet_path") else [],
                "status": compact(request.get("status"), "queued"),
                "next_allowed_actions": ["poll", "open_context", "open_receipt"],
                "authority_boundary": "queue_processing_not_allowed_in_projection",
                "message_count": 1,
                "latest_summary": compact(request.get("status"), "queued"),
                "updated_at": request.get("updated_at") or request.get("created_at"),
                "production_authority": False,
                "live_execution_authority": False,
            }
        )
        messages.append(
            {
                "message_id": f"codex_request:{request_id}",
                "thread_id": thread_id,
                "channel_id": "codex_queue",
                "sender_id": "chatgpt_browser_connector",
                "sender_kind": "carrier",
                "recipient": ["codex_cli_carrier"],
                "body": compact(request.get("objective"), request_id),
                "message_type": "codex_work_request",
                "message_kind": "codex_work_request",
                "subject": compact(request.get("status"), "queued"),
                "from_role": "chatgpt_browser_connector",
                "source_path": source_refs["codex_queue"],
                "source_refs": [source_refs["codex_queue"]],
                "context_refs": [compact(request.get("request_path"), "")] if request.get("request_path") else [],
                "receipt_refs": [compact(request.get("latest_return_packet_path"), "")] if request.get("latest_return_packet_path") else [],
                "status": compact(request.get("status"), "queued"),
                "acked_by": [],
                "created_at": request.get("created_at") or request.get("updated_at"),
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        )

    for row in browser_queue_hints:
        hint_id = compact(row.get("name"), compact(row.get("path"), "browser_queue_hint"))
        thread_id = f"browser_queue:{hint_id}"
        threads.append(
            {
                "thread_id": thread_id,
                "channel_id": "browser_queue",
                "title": hint_id,
                "subject": "Browser queue hint",
                "thread_kind": "browser_queue_hint",
                "source_refs": [compact(row.get("path"), source_refs["browser_queue"])],
                "context_refs": [],
                "receipt_refs": [compact(row.get("path"), "")] if row.get("path") else [],
                "status": "recorded",
                "next_allowed_actions": ["poll", "open_receipt"],
                "authority_boundary": "read_only_projection",
                "message_count": 1,
                "latest_summary": hint_id,
                "updated_at": row.get("mtime"),
                "production_authority": False,
                "live_execution_authority": False,
            }
        )
        messages.append(
            {
                "message_id": f"browser_queue_hint:{hint_id}",
                "thread_id": thread_id,
                "channel_id": "browser_queue",
                "sender_id": "browser_queue",
                "sender_kind": "system_projection",
                "recipient": ["operator"],
                "body": hint_id,
                "message_type": "browser_queue_hint",
                "message_kind": "browser_queue_hint",
                "subject": "browser queue hint",
                "from_role": "system",
                "source_path": compact(row.get("path"), source_refs["browser_queue"]),
                "source_refs": [compact(row.get("path"), source_refs["browser_queue"])],
                "context_refs": [],
                "receipt_refs": [compact(row.get("path"), "")] if row.get("path") else [],
                "status": "recorded",
                "acked_by": [],
                "created_at": row.get("mtime"),
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        )

    for row in receipts[:12]:
        receipt_path = compact(row.get("path"), "")
        if not receipt_path:
            continue
        thread_id = f"receipts:{hashlib.sha256(receipt_path.encode('utf-8')).hexdigest()[:12]}"
        threads.append(
            {
                "thread_id": thread_id,
                "channel_id": "receipts",
                "title": compact(row.get("name"), receipt_path),
                "subject": "Receipt",
                "thread_kind": "receipt",
                "source_refs": [receipt_path],
                "context_refs": [],
                "receipt_refs": [receipt_path],
                "status": "recorded",
                "next_allowed_actions": ["open_receipt"],
                "authority_boundary": "read_only_projection",
                "message_count": 1,
                "latest_summary": compact(row.get("authority_class"), "receipt"),
                "updated_at": None,
                "production_authority": False,
                "live_execution_authority": False,
            }
        )
        messages.append(
            {
                "message_id": f"receipt:{thread_id.split(':', 1)[1]}",
                "thread_id": thread_id,
                "channel_id": "receipts",
                "sender_id": "receipt_surface",
                "sender_kind": "receipt_surface",
                "recipient": ["operator"],
                "body": compact(row.get("name"), receipt_path),
                "message_type": "receipt",
                "message_kind": "receipt",
                "subject": compact(row.get("authority_class"), "receipt"),
                "from_role": "receipt_surface",
                "source_path": receipt_path,
                "source_refs": [receipt_path],
                "context_refs": [],
                "receipt_refs": [receipt_path],
                "status": "recorded",
                "acked_by": [],
                "created_at": None,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            }
        )

    for agent in [row for row in listify(agent_control_plane.get("agents")) if isinstance(row, Mapping)]:
        participant_id = compact(agent.get("role_id") or agent.get("agent_id"), "")
        if not participant_id:
            continue
        participants.append(
            {
                "participant_id": participant_id,
                "display_name": compact(agent.get("display_name"), participant_id),
                "participant_kind": "agent",
                "carrier_id": compact(agent.get("carrier"), "codex_cli"),
                "domain_id": compact(agent.get("domain_id"), "unknown"),
                "context_package_path": agent.get("active_context_package_md_path"),
                "mount_receipt_path": agent.get("latest_mount_receipt_path"),
                "status": compact(agent.get("status"), "ready"),
                "available_for_comms": bool(agent.get("available_for_comms", True)),
                "authority_scope": "candidate_state_only",
                "production_authority": False,
                "live_execution_authority": False,
            }
        )

    participants.extend(
        [
            {
                "participant_id": "operator",
                "display_name": "Operator",
                "participant_kind": "human_operator",
                "carrier_id": "human",
                "domain_id": "operator",
                "status": "active",
                "available_for_comms": True,
                "authority_scope": "candidate_state_only",
                "production_authority": False,
                "live_execution_authority": False,
            },
            {
                "participant_id": "chatgpt_browser_carrier",
                "display_name": "ChatGPT Browser Carrier",
                "participant_kind": "carrier",
                "carrier_id": compact(chatgpt_browser_mcp.get("carrier_id"), "CHATGPT_BROWSER_CARRIER"),
                "domain_id": "chatgpt_connector",
                "status": compact(chatgpt_browser_mcp.get("transport_state"), "unknown"),
                "available_for_comms": True,
                "authority_scope": "candidate_state_only",
                "production_authority": False,
                "live_execution_authority": False,
            },
            {
                "participant_id": "codex_cli_carrier",
                "display_name": "Codex CLI Carrier",
                "participant_kind": "carrier",
                "carrier_id": "CODEX_CLI_CARRIER",
                "domain_id": "codex_cli",
                "status": "active",
                "available_for_comms": True,
                "authority_scope": "candidate_state_only",
                "production_authority": False,
                "live_execution_authority": False,
            },
        ]
    )

    pin_targets = [
        ("pin_hot_context", "HOT CONTEXT", CODEX_SOLO_STATUS.as_posix()),
        ("pin_codex_context_packages", "CODEX CONTEXT PACKAGES", CODEX_CONTEXT_PACKAGES.as_posix()),
        ("pin_codex_queue", "CODEX WORK QUEUE", source_refs["codex_queue"]),
    ]
    for pin_id, label, rel in pin_targets:
        path = root / rel
        if not path.exists():
            continue
        pins.append(
            {
                "pin_id": pin_id,
                "thread_id": "receipts",
                "label": label,
                "ref_path": rel,
                "ref_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "truth_class": "repo_observed",
                "authority_scope": "candidate_state_only",
                "stale_policy": "recompute_on_refresh",
                "production_authority": False,
                "live_execution_authority": False,
            }
        )

    actions = [
        {
            "action_id": "poll",
            "label": "Poll",
            "action_kind": "poll",
            "route_or_tool": "ion_carrier_message_poll",
            "confirmation_required": False,
            "approval_required": False,
            "production_authority": False,
            "live_execution_authority": False,
            "allowed_when": "always",
            "forbidden_when": "none",
            "state": "read_only_available",
        },
        {
            "action_id": "draft_message",
            "label": "Draft Message",
            "action_kind": "draft_message",
            "route_or_tool": "ui_local_draft_only",
            "confirmation_required": False,
            "approval_required": False,
            "production_authority": False,
            "live_execution_authority": False,
            "allowed_when": "local_draft_only",
            "forbidden_when": "no_live_send_in_read_only_slice",
            "state": "gated_disabled",
        },
        {
            "action_id": "send_message",
            "label": "Send Message",
            "action_kind": "send_message",
            "route_or_tool": "ion_carrier_message_send",
            "confirmation_required": True,
            "approval_required": True,
            "production_authority": False,
            "live_execution_authority": False,
            "allowed_when": "future_packet_only",
            "forbidden_when": "current_projection_read_only",
            "state": "forbidden_in_this_slice",
        },
        {
            "action_id": "queue_codex_packet",
            "label": "Queue Codex Packet",
            "action_kind": "queue_codex_packet",
            "route_or_tool": "ion_queue_submit",
            "confirmation_required": True,
            "approval_required": True,
            "production_authority": False,
            "live_execution_authority": False,
            "allowed_when": "future_packet_only",
            "forbidden_when": "current_projection_read_only",
            "state": "forbidden_in_this_slice",
        },
    ]

    threads.sort(
        key=lambda row: compact(row.get("updated_at") or row.get("created_at"), ""),
        reverse=True,
    )
    messages.sort(
        key=lambda row: compact(row.get("created_at"), ""),
        reverse=True,
    )
    thread_rows = threads[:400]
    message_rows = messages[:800]

    return {
        "schema_id": "ion.joc_comms_projection.v1",
        "status": "read_only_projection_ready",
        "generated_at": utc_now(),
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "write_authority": False,
            "write_authority_policy": "false_by_default",
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
        "source_paths": source_refs,
        "source_present": source_present,
        "channels": channels,
        "threads": thread_rows,
        "messages": message_rows,
        "agent_home_views": team_agent_home_views[:20],
        "summary": {
            "channel_count": len(channels),
            "thread_count": len(thread_rows),
            "message_count": len(message_rows),
            "agent_home_view_count": len(team_agent_home_views),
            "participant_count": len(participants),
            "pin_count": len(pins),
            "blocker_count": len(blockers),
        },
        "participants": participants,
        "pins": pins,
        "receipts": receipts[:24],
        "actions": actions,
        "blockers": blockers,
        "production_authority": False,
        "live_execution_authority": False,
        "read_only_projection": True,
        "non_claims": [
            "no_live_send",
            "no_live_ack",
            "no_agent_invoke_from_projection",
            "no_queue_process_once_from_projection",
            "no_production_write",
        ],
    }


def _cockpit_chat_turn_groups(turns: list[Mapping[str, Any]], *, limit: int = 80) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_turn in turns[-limit:]:
        turn = dict(raw_turn)
        kind = str(turn.get("kind") or "chat_turn")
        author = str(turn.get("author") or "")
        if kind == "chat_turn" and author in {"operator", "user"}:
            current = {
                "group_id": turn.get("turn_id"),
                "created_at": turn.get("created_at"),
                "user_turn": turn,
                "assistant_turns": [],
                "execution_turns": [],
                "return_records": [],
                "turn_trace": None,
                "context_turns": [],
                "other_turns": [],
            }
            groups.append(current)
            continue
        if current is None:
            current = {
                "group_id": f"system_{len(groups) + 1}",
                "created_at": turn.get("created_at"),
                "user_turn": None,
                "assistant_turns": [],
                "execution_turns": [],
                "return_records": [],
                "turn_trace": None,
                "context_turns": [],
                "other_turns": [],
            }
            groups.append(current)
        if kind == "assistant_response":
            current["assistant_turns"].append(turn)
        elif kind == "execution_status":
            current["execution_turns"].append(turn)
        elif kind == "mini_auto_post":
            current["context_turns"].append(turn)
        else:
            current["other_turns"].append(turn)
    return groups


def _codex_chat_lane_summary(lane: Mapping[str, Any]) -> dict[str, Any]:
    turns = [turn for turn in listify(lane.get("turns")) if isinstance(turn, Mapping)]
    queue_links = [link for link in listify(lane.get("queue_links")) if isinstance(link, Mapping)]
    return {
        "lane_id": lane.get("lane_id"),
        "label": lane.get("label"),
        "purpose": lane.get("purpose"),
        "turn_count": len(turns),
        "queue_link_count": len(queue_links),
        "latest_turn": dict(turns[-1]) if turns else {},
        "latest_queue_link": dict(queue_links[-1]) if queue_links else {},
    }


def _codex_capsule_chat_summary(root: Path) -> dict[str, Any]:
    model = read_json(root / CODEX_CAPSULE_CHAT_MODEL)
    ui = model.get("ui", {}) if isinstance(model.get("ui"), dict) else {}
    conversation = ui.get("conversation", {}) if isinstance(ui.get("conversation"), dict) else {}
    conversation_summary = conversation.get("summary", {}) if isinstance(conversation.get("summary"), dict) else {}
    turn_groups = conversation.get("turn_groups") if isinstance(conversation.get("turn_groups"), list) else []
    lanes = model.get("lanes", {}) if isinstance(model.get("lanes"), dict) else {}
    ion_lane = lanes.get("ion_system", {}) if isinstance(lanes.get("ion_system"), dict) else {}
    codex_lane = lanes.get("codex_general", {}) if isinstance(lanes.get("codex_general"), dict) else {}
    ion_turns = [turn for turn in listify(ion_lane.get("turns")) if isinstance(turn, Mapping)]
    codex_context = model.get("codex_solo_context", {}) if isinstance(model.get("codex_solo_context"), dict) else {}
    capsule = codex_context.get("capsule", {}) if isinstance(codex_context.get("capsule"), dict) else {}
    mini = codex_context.get("mini", {}) if isinstance(codex_context.get("mini"), dict) else {}
    hot_context = codex_context.get("hot_context", {}) if isinstance(codex_context.get("hot_context"), dict) else {}
    codex_queue = model.get("codex_queue", {}) if isinstance(model.get("codex_queue"), dict) else {}
    response_runs = model.get("response_runs", {}) if isinstance(model.get("response_runs"), dict) else {}
    turn_traces = model.get("turn_traces", {}) if isinstance(model.get("turn_traces"), dict) else {}
    state_memory = model.get("memory", {}) if isinstance(model.get("memory"), dict) else {}
    memory = model.get("memory_visualization", {}) if isinstance(model.get("memory_visualization"), dict) else {}
    return_hydration = (codex_queue.get("return_hydration") if isinstance(codex_queue.get("return_hydration"), dict) else {})
    skills = model.get("skills", {}) if isinstance(model.get("skills"), dict) else {}
    current_activation = skills.get("current_activation", {}) if isinstance(skills.get("current_activation"), dict) else {}
    chat_engine = model.get("chat_engine", {}) if isinstance(model.get("chat_engine"), dict) else {}
    response_carrier = model.get("chat_response_carrier", {}) if isinstance(model.get("chat_response_carrier"), dict) else {}
    execution_bridge = model.get("execution_bridge", {}) if isinstance(model.get("execution_bridge"), dict) else {}
    raw_codex_cli = model.get("raw_codex_cli", {}) if isinstance(model.get("raw_codex_cli"), dict) else {}
    codex_app_server = model.get("codex_app_server", {}) if isinstance(model.get("codex_app_server"), dict) else {}
    model_moves = model.get("model_moves", {}) if isinstance(model.get("model_moves"), dict) else {}
    assistant_work_routes = model.get("assistant_work_routes", {}) if isinstance(model.get("assistant_work_routes"), dict) else {}
    service_console = model.get("service_console", {}) if isinstance(model.get("service_console"), dict) else {}
    mini_text = compact(mini.get("text"), "")
    chat_context = model.get("chat_context") if isinstance(model.get("chat_context"), dict) else {}
    ide_context_bridge = model.get("ide_context_bridge") if isinstance(model.get("ide_context_bridge"), dict) else {}
    if not chat_context:
        chat_context = {
            "schema_id": "ion.codex_chat_context_surface.v1",
            "status": "empty",
            "active_binding_id": "",
            "active_binding": None,
            "bindings": [],
            "binding_count": 0,
            "domain_counts": {},
            "context_policy": {
                "capsule_mini_are_floor_not_chat_identity": True,
                "chat_context_binding_required_for_new_work": True,
                "same_domain_branch_awareness_only": True,
                "archive_attach_required_for_past_chat_context": True,
            },
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        }
    if not ide_context_bridge:
        ide_context_bridge = {
            "schema_id": "ion.codex_ide_context_bridge_surface.v0_1",
            "status": "empty",
            "latest_bridge": None,
            "bridges": [],
            "bridge_count": 0,
            "branch_ids": [],
            "context_policy": {
                "ide_bridge_is_read_only_projection": True,
                "lazy_branches_require_artifact_read_first": True,
                "chat_turn_must_mount_bridge_explicitly": True,
            },
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        }
    return {
        "schema_id": "ion.codex_capsule_chat_cockpit_summary.v1",
        "model_path": str(CODEX_CAPSULE_CHAT_MODEL),
        "model_present": bool(model),
        "verdict": compact(model.get("verdict"), "missing"),
        "generated_at": model.get("generated_at"),
        "product": model.get("product", {}),
        "product_mode": model.get("product_mode", {}),
        "authority": model.get("authority", {}),
        "conversation_summary": conversation_summary,
        "conversation_turn_groups": turn_groups[-80:],
        "ion_comms_turn_groups": _cockpit_chat_turn_groups(ion_turns),
        "pipeline_runs": _safe_record_list(model.get("pipeline_runs"), limit=12),
        "ion_comms": model.get("ion_comms", {}),
        "shared_digest": model.get("shared_digest", {}),
        "lanes": {
            "codex_general": _codex_chat_lane_summary(codex_lane),
            "ion_system": _codex_chat_lane_summary(ion_lane),
        },
        "chat_branches": _safe_record_list(model.get("chat_branches"), limit=80),
        "fresh_agent_capsule_chats": _safe_record_list(model.get("fresh_agent_capsule_chats"), limit=80),
        "chat_context": chat_context,
        "ide_context_bridge": ide_context_bridge,
        "turn_trace_count": turn_traces.get("trace_count", 0),
        "turn_traces": turn_traces,
        "queued_request_count": turn_traces.get("queued_request_count", 0),
        "runner_active": bool(turn_traces.get("runner_active")),
        "response_run_count": response_runs.get("record_count", 0),
        "latest_response_status": response_runs.get("latest_status"),
        "latest_response_runs": [
            {
                "run_id": record.get("run_id"),
                "status": record.get("status"),
                "selected_model": record.get("selected_model"),
                "selected_reasoning_effort": record.get("selected_reasoning_effort"),
                "created_at": record.get("created_at"),
                "updated_at": record.get("updated_at"),
                "finding": record.get("finding"),
                "prompt_path": record.get("prompt_path"),
                "latest_return_path": record.get("latest_return_path"),
                "events_path": record.get("events_path"),
                "stdout_path": record.get("stdout_path"),
                "stderr_path": record.get("stderr_path"),
                "operator_message_sha256": record.get("operator_message_sha256"),
                "path": record.get("path"),
            }
            for record in _safe_record_list(response_runs.get("records"), limit=5)
        ],
        "latest_work_requests": _compact_file_records(_safe_record_list(codex_queue.get("latest_work_requests"), limit=5)),
        "latest_task_returns": _compact_file_records(_safe_record_list(codex_queue.get("latest_task_returns"), limit=5)),
        "latest_task_return_machine_receipts": _latest_task_return_machine_receipts(root),
        "latest_task_return_automation_diagnoses": _task_return_automation_diagnoses(root),
        "return_hydration": return_hydration,
        "memory": {
            "pin_count": len(listify(state_memory.get("pins"))),
            "archive_attachments": listify(state_memory.get("archive_attachments"))[-12:],
            "archive_attachment_count": len(listify(state_memory.get("archive_attachments"))),
            "codex_memory_path": state_memory.get("codex_memory_path"),
        },
        "codex_queue_path": codex_queue.get("work_queue_path"),
        "capsule": {
            "ok": capsule.get("ok"),
            "path": capsule.get("path"),
            "entry_count": capsule.get("entry_count"),
            "context_line_limit": capsule.get("context_line_limit"),
            "recent_rows": _safe_record_list(capsule.get("recent_rows"), limit=5),
        },
        "mini": {
            "ok": mini.get("ok"),
            "role": mini.get("role"),
            "line_count": mini.get("line_count"),
            "max_lines": mini.get("max_lines"),
            "text_excerpt": "\n".join(mini_text.splitlines()[:16]),
        },
        "hot_context": hot_context,
        "memory_visualization": {
            "selected_turn_id": memory.get("selected_turn_id"),
            "active_process_running": memory.get("active_process_running"),
            "memory_segment_count": len(listify(memory.get("memory_segments"))),
            "context_layer_count": len(listify(memory.get("context_matryoshka_layers"))),
            "visible_window_count": len(listify(memory.get("visible_windows"))),
            "visible_windows": listify(memory.get("visible_windows"))[:16],
            "memory_segments": listify(memory.get("memory_segments"))[:120],
            "context_route_edges": listify(memory.get("context_route_edges"))[:180],
            "context_matryoshka_layers": listify(memory.get("context_matryoshka_layers"))[:12],
            "selected_turn_context": memory.get("selected_turn_context", {}),
            "protocol_manifest_summary": memory.get("protocol_manifest_summary", {}),
            "token_budget_summary": memory.get("token_budget_summary", {}),
            "carrier_phase_events": listify(memory.get("carrier_phase_events"))[:80],
            "forbidden_or_omitted_refs": listify(memory.get("forbidden_or_omitted_refs"))[:80],
            "raw_hidden_reasoning_exposed": bool(memory.get("raw_hidden_reasoning_exposed")),
        },
        "chat_engine": {
            "verdict": chat_engine.get("verdict"),
            "quality_target": chat_engine.get("quality_target"),
            "lens_count": chat_engine.get("lens_count"),
            "response_modes": listify(chat_engine.get("response_modes")),
        },
        "skills": {
            "verdict": skills.get("verdict"),
            "skill_count": skills.get("skill_count"),
            "current_activation_verdict": current_activation.get("verdict"),
            "selection_reason": current_activation.get("selection_reason"),
            "findings": listify(skills.get("findings")) + listify(current_activation.get("findings")),
        },
        "response_carrier": {
            "enabled": response_carrier.get("enabled"),
            "verdict": response_carrier.get("verdict"),
            "uses_codex_cli": response_carrier.get("uses_codex_cli"),
            "provider_api_dispatch_authorized": response_carrier.get("provider_api_dispatch_authorized"),
            "state_acceptance_granted": response_carrier.get("state_acceptance_granted"),
        },
        "execution_bridge": {
            "default_mode": execution_bridge.get("default_mode"),
            "allowed_modes": listify(execution_bridge.get("allowed_modes")),
            "runner_start_enabled": execution_bridge.get("runner_start_enabled"),
            "response_carrier_enabled": execution_bridge.get("response_carrier_enabled"),
        },
        "raw_codex_cli": raw_codex_cli,
        "codex_app_server": codex_app_server,
        "model_moves": model_moves,
        "assistant_work_routes": assistant_work_routes,
        "service_console": service_console,
        "telemetry_inventory": {
            "conversation_turn_groups": len(turn_groups),
            "turn_traces": turn_traces.get("trace_count", 0),
            "response_runs": response_runs.get("record_count", 0),
            "return_hydration_records": return_hydration.get("record_count", 0),
            "latest_work_requests": len(listify(codex_queue.get("latest_work_requests"))),
            "latest_task_returns": len(listify(codex_queue.get("latest_task_returns"))),
            "memory_segments": len(listify(memory.get("memory_segments"))),
            "carrier_phase_events": len(listify(memory.get("carrier_phase_events"))),
            "raw_hidden_reasoning_exposed": bool(memory.get("raw_hidden_reasoning_exposed")),
            "raw_session_transcript_exported": False,
            "secrets_exported": False,
        },
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def _markdown_headings(text: str, limit: int = 10) -> list[str]:
    headings: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            headings.append(stripped.lstrip("#").strip())
        if len(headings) >= limit:
            break
    return headings


def _yaml_domain_rows(text: str) -> list[dict[str, str]]:
    domains: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- domain_id:"):
            if current:
                domains.append(current)
            current = {"domain_id": stripped.split(":", 1)[1].strip().strip("\"'")}
            continue
        if current is None:
            continue
        for key in ("purpose", "safety_boundary"):
            prefix = f"{key}:"
            if stripped.startswith(prefix):
                current[key] = stripped[len(prefix):].strip().strip("\"'")
    if current:
        domains.append(current)
    return domains


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _computer_assistant_capability_map(
    root: Path,
    *,
    browser_gpt_dom: Mapping[str, Any],
    codex_browser_agent: Mapping[str, Any],
    manifest: Mapping[str, Any],
    agent_contract: Mapping[str, Any],
    page_perception_domains: list[dict[str, str]],
) -> dict[str, Any]:
    capability_rows = build_capability_matrix(root)
    capability_by_id = {
        str(row.get("capability_id")): row
        for row in capability_rows
        if isinstance(row, Mapping) and row.get("capability_id")
    }
    screen_automation = capability_by_id.get("screen_automation_memory", {})
    chatops_bridge = capability_by_id.get("chatops_bridge_extension", {})
    playwright = capability_by_id.get("python_playwright", {})
    action_messages = agent_contract.get("background_messages") if isinstance(agent_contract.get("background_messages"), Mapping) else {}
    manifest_permissions = listify(manifest.get("permissions"))
    host_permissions = listify(manifest.get("host_permissions"))
    dom_status = str(browser_gpt_dom.get("status") or "missing")
    agent_status = str(codex_browser_agent.get("status") or "missing")
    ready_surface_count = _safe_int(codex_browser_agent.get("ready_surface_count"))
    surface_count = _safe_int(codex_browser_agent.get("surface_count"))
    critical_gap_count = _safe_int(codex_browser_agent.get("critical_gap_count"))
    dialogue_loop = (
        codex_browser_agent.get("gpt_dialogue_action_loop")
        if isinstance(codex_browser_agent.get("gpt_dialogue_action_loop"), Mapping)
        else {}
    )
    dialogue_loop_authority = (
        dialogue_loop.get("authority")
        if isinstance(dialogue_loop.get("authority"), Mapping)
        else {}
    )
    cdp_accessibility_witness = (
        codex_browser_agent.get("cdp_accessibility_witness")
        if isinstance(codex_browser_agent.get("cdp_accessibility_witness"), Mapping)
        else {}
    )
    sandbox_skill_benchmark = (
        codex_browser_agent.get("sandbox_skill_benchmark")
        if isinstance(codex_browser_agent.get("sandbox_skill_benchmark"), Mapping)
        else {}
    )
    sandbox_skill_benchmark_result = (
        codex_browser_agent.get("sandbox_skill_benchmark_result")
        if isinstance(codex_browser_agent.get("sandbox_skill_benchmark_result"), Mapping)
        else {}
    )
    self_evolution_loop = (
        codex_browser_agent.get("self_evolution_loop")
        if isinstance(codex_browser_agent.get("self_evolution_loop"), Mapping)
        else {}
    )
    self_evolution_authority = (
        self_evolution_loop.get("authority")
        if isinstance(self_evolution_loop.get("authority"), Mapping)
        else {}
    )
    ranked_self_evolution_candidates = [
        row for row in listify(self_evolution_loop.get("ranked_candidate_queue")) if isinstance(row, Mapping)
    ]
    top_self_evolution_candidate = ranked_self_evolution_candidates[0] if ranked_self_evolution_candidates else {}

    architecture_lanes = [
        {
            "lane_id": "in_page_dom_bridge",
            "title": "In-page DOM bridge",
            "status": chatops_bridge.get("status", "missing"),
            "purpose": "Read visible ChatGPT tabs, conversation timeline, composer state, native history, downloads, and approval cards from the content script.",
            "local_refs": [
                "browser_extension/ion_chatops_bridge/src/content.ts",
                "browser_extension/ion_chatops_bridge/dist/content.js",
                "browser_extension/ion_chatops_bridge/src/background.ts",
            ],
            "authority": "read_projected_dom_with_approved_send_only",
            "research_basis": ["playwright_role_locator_contract", "openai_custom_harness"],
        },
        {
            "lane_id": "semantic_playwright_verifier",
            "title": "Semantic Playwright verifier",
            "status": playwright.get("status", "missing"),
            "purpose": "Use role/name/text/label locators, auto-waiting, phase sweeps, screenshots, and comparison profiles to verify Browser GPT DOM contracts.",
            "local_refs": [
                "ION/04_packages/kernel/ion_browser_gpt_dom_calibration.py",
                "ION/04_packages/kernel/ion_codex_browser_agent.py",
                "ION/tests/test_kernel_ion_codex_browser_agent.py",
            ],
            "authority": "inspection_only_no_send_click",
            "research_basis": ["playwright_locators", "playwright_auto_waiting"],
            "ready_surface_count": ready_surface_count,
            "surface_count": surface_count,
            "critical_gap_count": critical_gap_count,
        },
        {
            "lane_id": "cdp_accessibility_tree",
            "title": "CDP accessibility tree",
            "status": cdp_accessibility_witness.get("status", "planned"),
            "purpose": "Add a protocol-level accessibility-tree witness for role/name/state drift, active dialogs, hidden-but-focusable controls, and resilient selector fallback.",
            "local_refs": [
                "ION/04_packages/kernel/ion_browser_gpt_dom_calibration.py",
                "ION/05_context/current/browser_gpt_dom_profiles/",
            ],
            "authority": "read_only_candidate_probe",
            "research_basis": ["chrome_devtools_protocol_accessibility", "webdriver_bidi_event_stream"],
            "target_surface_count": len(listify(cdp_accessibility_witness.get("target_surfaces"))),
            "target_role_count": len(listify(cdp_accessibility_witness.get("target_roles"))),
        },
        {
            "lane_id": "screen_computer_use_harness",
            "title": "Screen and computer-use harness",
            "status": screen_automation.get("status", "missing"),
            "purpose": "Reuse learned browser geometry for extension reload and tab refresh, and keep screenshot/coordinate action loops gated behind explicit approval.",
            "local_refs": [
                "ION/04_packages/kernel/ion_browser_gpt_screen_automation.py",
                "ION/05_context/current/browser_gpt_dom_profiles/screen_automation/latest_state.json",
            ],
            "authority": "local_screen_actions_receipted_no_chatgpt_send",
            "research_basis": ["openai_computer_use_safety_loop"],
            "state_captured_at": screen_automation.get("state_captured_at"),
        },
        {
            "lane_id": "action_gateway_bridge",
            "title": "Action Gateway bridge",
            "status": "available" if "ion_browser_gpt_dom_tab_command" in action_messages else "projected",
            "purpose": "Mirror action requests, expose full native action details, and approve only through explicit operator/auto-approve policy.",
            "local_refs": [
                "ION/04_packages/kernel/ion_custom_gpt_action_gateway.py",
                "browser_extension/ion_chatops_bridge/src/content.ts",
                "ION/08_ui/joc_cockpit_shell/BrowserGptDomTwinPanel.tsx",
            ],
            "authority": "candidate_action_packets_and_explicit_approval_only",
            "research_basis": ["openai_confirm_at_risk_point"],
        },
        {
            "lane_id": "gpt_dialogue_action_loop",
            "title": "GPT dialogue/action loop",
            "status": dialogue_loop.get("status", "needs_plan"),
            "purpose": "Let Codex and the active GPT carry a bounded conversation: approved prompt, visible GPT response, GPT action proposal, DOM/action-detail verification, then a gated next reply or operator report.",
            "local_refs": [
                "ION/04_packages/kernel/ion_codex_browser_agent.py",
                "browser_extension/ion_chatops_bridge/src/content.ts",
                "ION/08_ui/joc_cockpit_shell/BrowserGptDomTwinPanel.tsx",
            ],
            "authority": "approved_dialogue_only_no_silent_send_or_action_execution",
            "research_basis": ["ion_browser_dom_perception_specialist", "openai_confirm_at_risk_point"],
            "turn_budget_default": dialogue_loop.get("turn_budget_default"),
            "operator_approved_send_required": bool(dialogue_loop_authority.get("operator_approved_send_required", True)),
            "native_action_approval_required": bool(dialogue_loop_authority.get("native_action_approval_required", True)),
        },
        {
            "lane_id": "sandbox_skill_benchmark",
            "title": "Sandbox skill benchmark",
            "status": sandbox_skill_benchmark_result.get("status") or sandbox_skill_benchmark.get("status", "sandbox_only_design"),
            "purpose": "Use demanding browser/game-like toy tasks to measure perception, timing, planning, recovery, and receipt quality without controlling third-party live game clients.",
            "local_refs": [
                "ION/04_packages/kernel/ion_codex_browser_agent.py",
                "ION/05_context/current/browser_gpt_dom_profiles/codex_browser_agent/",
            ],
            "authority": "sandbox_only_no_third_party_game_botting",
            "research_basis": ["ion_browser_dom_perception_specialist"],
            "case_count": _safe_int(sandbox_skill_benchmark.get("case_count")),
            "latest_measured_score": sandbox_skill_benchmark_result.get("measured_score"),
            "latest_result_path": sandbox_skill_benchmark_result.get("latest_result_path"),
            "third_party_game_client_control_authority": bool(
                sandbox_skill_benchmark.get("authority", {}).get("third_party_game_client_control_authority")
                if isinstance(sandbox_skill_benchmark.get("authority"), Mapping)
                else False
            ),
        },
        {
            "lane_id": "self_evolution_loop",
            "title": "Self-evolution loop",
            "status": self_evolution_loop.get("status", "needs_plan"),
            "purpose": "Let Browser GPT/Codex observe current gaps, ask for candidate improvements, rank them, prove them in sandbox/read-only probes, and write receipts before any gated mutation.",
            "local_refs": [
                "ION/04_packages/kernel/ion_codex_browser_agent.py",
                "ION/tests/test_kernel_ion_codex_browser_agent.py",
                "ION/05_context/current/browser_gpt_dom_profiles/codex_browser_agent/",
            ],
            "authority": "candidate_self_evolution_only_no_autonomous_mutation",
            "research_basis": [
                "playwright_auto_waiting",
                "chrome_extension_messaging",
                "chrome_content_script_isolation",
                "chrome_devtools_protocol_accessibility",
                "ion_browser_dom_perception_specialist",
            ],
            "candidate_class_count": len(listify(self_evolution_loop.get("candidate_classes"))),
            "ranked_candidate_count": len(ranked_self_evolution_candidates),
            "top_candidate_id": self_evolution_loop.get("top_candidate_id") or top_self_evolution_candidate.get("candidate_id"),
            "top_candidate_title": self_evolution_loop.get("top_candidate_title") or top_self_evolution_candidate.get("title"),
            "implemented_candidate_count": self_evolution_loop.get("implemented_candidate_count", 0),
            "stop_condition_count": len(listify(self_evolution_loop.get("stop_conditions"))),
            "operator_approved_send_required": bool(self_evolution_authority.get("operator_approved_send_required", True)),
            "patch_apply_from_gpt_text_authority": bool(self_evolution_authority.get("patch_apply_from_gpt_text_authority", False)),
            "native_action_auto_approval_authority": bool(self_evolution_authority.get("native_action_auto_approval_authority", False)),
        },
        {
            "lane_id": "context_capsule_memory",
            "title": "Context capsule memory",
            "status": agent_status,
            "purpose": "Carry Browser GPT DOM requirements, profile comparisons, screenshots, receipts, and next-step context into Codex/JOC without relying on chat memory.",
            "local_refs": [
                "ION/05_context/current/browser_gpt_dom_profiles/codex_browser_agent/",
                "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
                "ION/05_context/current/browser_dom_perception_specialist/RESEARCH_BRIEF_20260526.md",
            ],
            "authority": "candidate_context_only_no_accepted_state",
            "research_basis": ["ion_browser_dom_perception_specialist"],
        },
    ]
    ready_lane_count = sum(
        1
        for lane in architecture_lanes
        if str(lane.get("status", "")).lower()
        in {"available", "learned", "planned", "ready", "visibility_projection_ready", "ready_for_candidate_self_evolution"}
    )
    return {
        "schema_id": "ion.browser_gpt_computer_assistant_capability_map.v1",
        "status": "projection_ready",
        "dom_status": dom_status,
        "agent_status": agent_status,
        "lane_count": len(architecture_lanes),
        "ready_lane_count": ready_lane_count,
        "critical_gap_count": critical_gap_count,
        "architecture_lanes": architecture_lanes,
        "capabilities": capability_rows,
        "research_digest": [
            {
                "source_id": "openai_computer_use",
                "source_url": "https://developers.openai.com/api/docs/guides/tools-computer-use",
                "finding": "Computer-use style agents should run in isolated browser/VM environments, treat page content as untrusted, and keep human confirmation at risky actions.",
            },
            {
                "source_id": "playwright_locators",
                "source_url": "https://playwright.dev/docs/locators",
                "finding": "Prioritize role/name/text/label locators and user-facing attributes over brittle CSS-only selectors.",
            },
            {
                "source_id": "playwright_actionability",
                "source_url": "https://playwright.dev/docs/actionability",
                "finding": "Use auto-waiting/actionability checks and retrying assertions to reduce UI timing flake.",
            },
            {
                "source_id": "chrome_devtools_protocol",
                "source_url": "https://chromedevtools.github.io/devtools-protocol/",
                "finding": "CDP exposes protocol JSON, target websocket endpoints, and DOM/accessibility domains suitable for read-only inspector witnesses.",
            },
            {
                "source_id": "webdriver_bidi",
                "source_url": "https://www.w3.org/TR/webdriver-bidi/",
                "finding": "WebDriver BiDi is the standards-track evented automation protocol to track for future cross-browser transport.",
            },
            {
                "source_id": "ion_browser_dom_perception",
                "source_url": "ION/05_context/current/browser_dom_perception_specialist/RESEARCH_BRIEF_20260526.md",
                "finding": "Local ION research already identified Browser DOM Perception and BROWSER_DOM_CARTOGRAPHER as the ownership lane for DOM/accessibility/visual/mutation work.",
            },
        ],
        "source_refs": [
            "ION/04_packages/kernel/ion_browser_gpt_dom_calibration.py",
            "ION/04_packages/kernel/ion_codex_browser_agent.py",
            "ION/04_packages/kernel/ion_browser_gpt_screen_automation.py",
            "browser_extension/ion_chatops_bridge/src/content.ts",
            "browser_extension/ion_chatops_bridge/dist/content.js",
            "ION/08_ui/joc_cockpit_shell/BrowserGptDomTwinPanel.tsx",
            "ION/05_context/current/browser_gpt_dom_profiles/",
            "ION/05_context/current/browser_dom_perception_specialist/RESEARCH_BRIEF_20260526.md",
        ],
        "manifest_permission_count": len(manifest_permissions),
        "host_permission_count": len(host_permissions),
        "page_perception_domain_count": len(page_perception_domains),
        "next_slices": [
            "Add CDP accessibility-tree snapshot comparison as a read-only Browser GPT witness.",
            "Add a candidate-only self-evolution loop runner that can ask, rank, prove, and receipt improvements without autonomous mutation.",
            "Add a gated GPT dialogue/action loop runner that can ask, observe, verify, and report without silent sends.",
            "Build a local sandbox-only reaction/planning benchmark before any external real-time client is considered.",
            "Promote Browser DOM Perception specialist only through an explicit registry packet.",
            "Add policy-gated computer-use loop receipts for isolated-browser QA, never for silent authenticated actions.",
        ],
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
            "cookie_read_authority": False,
            "silent_send_authority": False,
            "computer_control_authority": False,
        },
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_authority": False,
        "secrets_authority": False,
    }


def _extension_micro_shell_summary(root: Path) -> dict[str, Any]:
    companion = read_json(root / PORTABLE_COMPANION_PRODUCT_CONTEXT)
    browser_gpt_dom = latest_browser_gpt_dom_summary(root)
    codex_browser_agent = latest_codex_browser_agent_summary(root)
    extension_root = resolve_ion_path(root, BROWSER_EXTENSION_ROOT)
    if not extension_root.exists():
        extension_root = resolve_ion_path(root, BROWSER_EXTENSION_LEGACY_ROOT)
    manifest_path = extension_root / "manifest.json"
    agent_contract_path = extension_root / "AGENT_INVOCATION_LANE_CONTRACT.json"
    queue_pack_path = extension_root / "QUEUE_PACK_AUTHORING.md"
    manifest = read_json(manifest_path)
    agent_contract = read_json(agent_contract_path)
    dom_registry_text = _read_text(root / DOM_PERCEPTION_DOMAIN_REGISTRY)
    task_return_text = _read_text(root / DOM_PERCEPTION_TASK_RETURN)
    queue_pack_text = _read_text(queue_pack_path)
    content_scripts = [item for item in listify(manifest.get("content_scripts")) if isinstance(item, dict)]
    background_messages = agent_contract.get("background_messages") if isinstance(agent_contract.get("background_messages"), dict) else {}
    authority = companion.get("current_v1_authority") if isinstance(companion.get("current_v1_authority"), dict) else {}
    joc_inheritance = companion.get("joc_inheritance_decision") if isinstance(companion.get("joc_inheritance_decision"), dict) else {}
    inherited_protocols = companion.get("inherited_protocols") if isinstance(companion.get("inherited_protocols"), dict) else {}
    domains = _yaml_domain_rows(dom_registry_text)
    computer_assistant_capability_map = _computer_assistant_capability_map(
        root,
        browser_gpt_dom=browser_gpt_dom,
        codex_browser_agent=codex_browser_agent,
        manifest=manifest,
        agent_contract=agent_contract,
        page_perception_domains=domains,
    )
    return {
        "schema_id": "ion.extension_micro_shell_cockpit_summary.v1",
        "status": "visibility_projection_ready" if companion or manifest else "missing_source",
        "extension_root": extension_root.as_posix(),
        "action_gateway_sync": _action_gateway_sync_summary(root),
        "manifest": {
            "path": manifest_path.as_posix(),
            "present": bool(manifest),
            "name": manifest.get("name"),
            "version": manifest.get("version"),
            "description": manifest.get("description"),
            "permissions": listify(manifest.get("permissions")),
            "host_permissions": listify(manifest.get("host_permissions")),
            "content_script_count": len(content_scripts),
            "content_script_matches": [match for script in content_scripts for match in listify(script.get("matches"))],
        },
        "agent_lane_contract": {
            "path": agent_contract_path.as_posix(),
            "present": bool(agent_contract),
            "status": agent_contract.get("status"),
            "purpose": agent_contract.get("purpose"),
            "panel_surfaces": listify(agent_contract.get("panel_surfaces")),
            "background_message_count": len(background_messages),
            "background_messages": sorted(background_messages.keys()),
            "safety_law": listify(agent_contract.get("safety_law")),
            "gateway_base_storage_key": agent_contract.get("gateway_base_storage_key"),
            "gateway_token_storage_key": agent_contract.get("gateway_token_storage_key"),
        },
        "portable_companion": {
            "path": str(PORTABLE_COMPANION_PRODUCT_CONTEXT),
            "present": bool(companion),
            "status": companion.get("status"),
            "context_id": companion.get("context_id"),
            "product_thesis": companion.get("product_thesis"),
            "joc_decision": joc_inheritance.get("decision"),
            "layout_zones": listify(joc_inheritance.get("layout_zones")),
            "visual_language": joc_inheritance.get("visual_language"),
            "inherited_protocol_count": len(inherited_protocols),
            "inherited_protocols": sorted(inherited_protocols.keys()),
            "shared_graph_model": companion.get("shared_graph_model", {}),
            "page_context_package_shape": companion.get("page_context_package_shape", {}),
        },
        "page_perception": {
            "domain_registry_path": str(DOM_PERCEPTION_DOMAIN_REGISTRY),
            "task_return_path": str(DOM_PERCEPTION_TASK_RETURN),
            "domain_registry_present": bool(dom_registry_text),
            "task_return_present": bool(task_return_text),
            "domain_count": len(domains),
            "domains": domains[:10],
            "task_return_headings": _markdown_headings(task_return_text, limit=8),
        },
        "browser_gpt_dom": browser_gpt_dom,
        "codex_browser_agent": codex_browser_agent,
        "computer_assistant_capability_map": computer_assistant_capability_map,
        "queue_pack_authoring": {
            "path": queue_pack_path.as_posix(),
            "present": bool(queue_pack_text),
            "headings": _markdown_headings(queue_pack_text, limit=8),
        },
        "current_v1_authority": authority,
        "safety_law": listify(companion.get("safety_law")),
        "required_boundaries": listify(companion.get("required_boundaries")),
        "implementation_gates": listify(companion.get("implementation_gates")),
        "non_claim_boundaries": listify(companion.get("non_claim_boundaries")),
        "production_authority": False,
        "live_execution_authority": False,
        "unrestricted_browser_control": False,
        "silent_browser_send_authority": False,
    }


def _docs_projects_packages_summary(root: Path) -> dict[str, Any]:
    context_packages = read_json(root / CODEX_CONTEXT_PACKAGES)
    package_rows = [row for row in listify(context_packages.get("packages")) if isinstance(row, dict)]
    safe_package_rel = latest_safe_package_result_rel(root)
    safe_package = read_json(root / safe_package_rel)
    preservation = safe_package.get("preservation_report") if isinstance(safe_package.get("preservation_report"), dict) else {}
    zip_audit = safe_package.get("zip_root_audit") if isinstance(safe_package.get("zip_root_audit"), dict) else {}
    artifact_packages = _latest_paths(root, ARTIFACT_PACKAGES_DIR.as_posix(), suffixes={".zip"}, recursive=True, limit=12)
    custom_gpt_builds = _latest_paths(root, (CUSTOM_GPT_CAPSULE_SYSTEM_DIR / "build_drafts").as_posix(), suffixes={".md", ".json"}, recursive=False, limit=8)
    custom_gpt_factory = _latest_paths(root, CUSTOM_GPT_FACTORY_DIR.as_posix(), suffixes={".md", ".json", ".yaml", ".yml"}, recursive=True, limit=8)
    workspace_root = root.parent
    daimon_root = workspace_root / "dAimon"
    cosmos_root = default_cosmos_project_root(root)
    project_favorites = [
        {
            "project_id": "ion_codex_full",
            "label": "ION Development",
            "path": root.as_posix(),
            "exists": root.exists(),
            "kind": "ion_root",
            "context_authority": "active_repo_authority",
        },
        {
            "project_id": "daimon",
            "label": "dAimon",
            "path": daimon_root.as_posix(),
            "exists": daimon_root.exists(),
            "kind": "companion_project",
            "context_authority": "receipt_backed_external_project",
        },
        {
            "project_id": "cosmos",
            "label": "Cosmos Water World",
            "path": cosmos_root.as_posix(),
            "exists": cosmos_root.exists(),
            "kind": "helixion_project_workbench",
            "context_authority": "registered_project_preview_and_bounded_diff_lane",
        },
        {
            "project_id": "helixion_joc_rebuild",
            "label": "Helixion JOC Rebuild",
            "path": (root / (CURRENT / "helixion_joc_rebuild")).as_posix(),
            "exists": (root / (CURRENT / "helixion_joc_rebuild")).exists(),
            "kind": "current_context_package",
            "context_authority": "active_rebuild_package",
        },
        {
            "project_id": "browser_extension",
            "label": "ION ChatOps Bridge",
            "path": resolve_ion_path(root, BROWSER_EXTENSION_ROOT).as_posix(),
            "exists": resolve_ion_path(root, BROWSER_EXTENSION_ROOT).exists(),
            "kind": "browser_extension",
            "context_authority": "bounded_extension_surface",
        },
        {
            "project_id": "custom_gpt_packages",
            "label": "Custom GPT Packages",
            "path": (root / (ARTIFACT_PACKAGES_DIR / "custom_gpt")).as_posix(),
            "exists": (root / (ARTIFACT_PACKAGES_DIR / "custom_gpt")).exists(),
            "kind": "artifact_package_lane",
            "context_authority": "candidate_package_artifacts",
        },
    ]
    package_types: dict[str, int] = {}
    for row in package_rows:
        kind = compact(row.get("context_type"), "unknown")
        package_types[kind] = package_types.get(kind, 0) + 1
    return {
        "schema_id": "ion.docs_projects_packages_cockpit_summary.v1",
        "status": "visibility_projection_ready",
        "context_packages": {
            "path": CODEX_CONTEXT_PACKAGES.as_posix(),
            "generated_at": context_packages.get("generated_at"),
            "package_count": context_packages.get("package_count", len(package_rows)),
            "selected_by_default": listify(context_packages.get("selected_by_default")),
            "package_types": package_types,
            "packages": package_rows[:10],
            "production_authority": False,
            "live_execution_authority": False,
        },
        "project_favorites": project_favorites,
        "artifact_packages": {
            "root": ARTIFACT_PACKAGES_DIR.as_posix(),
            "zip_count_visible": len(artifact_packages),
            "latest_zips": artifact_packages,
            "auto_zip_drop_authority": False,
            "drop_zone_execution_authority": False,
        },
        "safe_full_project_package": {
            "path": safe_package_rel.as_posix(),
            "present": bool(safe_package),
            "accepted": safe_package.get("accepted"),
            "zip_path": safe_package.get("zip_path"),
            "zip_sha256": safe_package.get("zip_sha256"),
            "packaging_verdict": preservation.get("packaging_verdict"),
            "files_before": preservation.get("files_before"),
            "files_after": preservation.get("files_after"),
            "zip_root_verdict": zip_audit.get("verdict"),
            "archive_root_mode": zip_audit.get("archive_root_mode"),
        },
        "custom_gpt_context": {
            "capsule_system_dir": CUSTOM_GPT_CAPSULE_SYSTEM_DIR.as_posix(),
            "factory_dir": CUSTOM_GPT_FACTORY_DIR.as_posix(),
            "latest_build_drafts": custom_gpt_builds,
            "latest_factory_files": custom_gpt_factory,
        },
        "operator_model": {
            "double_click_zip_drop": "planned_extension_runtime_capability_not_granted_here",
            "one_click_thumbnail": "planned_extension_runtime_capability_not_granted_here",
            "favorites_are_context_targets": True,
            "receipts_required_for_package_state": True,
        },
        "production_authority": False,
        "live_execution_authority": False,
        "unrestricted_filesystem_mutation": False,
    }


def _count_context_surfaces(surface_hints: Mapping[str, Any]) -> dict[str, int]:
    keys = (
        "readme",
        "agents",
        "package_files",
        "protocols",
        "receipts",
        "routes",
        "schemas",
        "source_files_sample",
        "status",
        "templates",
        "tests",
    )
    counts = {key: len(listify(surface_hints.get(key))) for key in keys}
    counts["total"] = sum(counts.values())
    return counts


def _preview_context_surfaces(surface_hints: Mapping[str, Any], *, limit: int = 4) -> dict[str, list[Any]]:
    preview: dict[str, list[Any]] = {}
    for key, value in surface_hints.items():
        items = listify(value)
        if items:
            preview[str(key)] = items[:limit]
    return preview


def _context_package_graph_projection(root: Path) -> dict[str, Any]:
    review = read_json(root / CONTEXT_PACKAGE_GRAPH_REVIEW)
    enrichment = read_json(root / CONTEXT_PACKAGE_GRAPH_ENRICHMENT)
    cockpit_spec = read_json(root / CONTEXT_PACKAGE_GRAPH_COCKPIT_SPEC)
    source_paths = {
        "review": CONTEXT_PACKAGE_GRAPH_REVIEW.as_posix(),
        "enrichment": CONTEXT_PACKAGE_GRAPH_ENRICHMENT.as_posix(),
        "cockpit_projection_spec": CONTEXT_PACKAGE_GRAPH_COCKPIT_SPEC.as_posix(),
    }
    source_present = {name: (root / Path(path)).exists() for name, path in source_paths.items()}
    enriched_by_path = {
        str(row.get("path")): row
        for row in listify(enrichment.get("enriched"))
        if isinstance(row, Mapping) and row.get("path")
    }
    review_by_path = {
        str(row.get("path")): row
        for row in listify(review.get("packages"))
        if isinstance(row, Mapping) and row.get("path")
    }
    raw_branches = [row for row in listify(cockpit_spec.get("branches")) if isinstance(row, Mapping)]
    if not raw_branches:
        raw_branches = [row for row in listify(review.get("packages")) if isinstance(row, Mapping)]
    branches: list[dict[str, Any]] = []
    for raw in raw_branches:
        path = compact(raw.get("path"), "")
        if not path:
            continue
        enriched = enriched_by_path.get(path, {})
        reviewed = review_by_path.get(path, {})
        surface_hints = raw.get("surface_hints") if isinstance(raw.get("surface_hints"), Mapping) else {}
        if not surface_hints and isinstance(reviewed.get("surface_hints"), Mapping):
            surface_hints = reviewed.get("surface_hints", {})
        authority = raw.get("authority") if isinstance(raw.get("authority"), Mapping) else {}
        branch_authority = {
            "accepted_state_authority": authority.get("accepted_state_authority") is True,
            "production_authority": authority.get("production_authority") is True,
            "live_execution_authority": authority.get("live_execution_authority") is True,
        }
        branches.append(
            {
                "path": path,
                "package_type": raw.get("package_type") or reviewed.get("package_type"),
                "parent_ref": raw.get("parent_ref") or reviewed.get("parent_ref"),
                "maturity_level": raw.get("maturity_level"),
                "read_first": listify(raw.get("read_first")),
                "candidate_capsule_path": raw.get("candidate_capsule_path") or reviewed.get("candidate_capsule_path"),
                "candidate_capsule_sha256_after_wave_002": enriched.get("candidate_capsule_sha256_after_wave_002"),
                "readme_projection_candidate": enriched.get("readme_projection_candidate"),
                "promotion_readiness": raw.get("promotion_readiness") or reviewed.get("promotion_readiness"),
                "classification": reviewed.get("classification"),
                "candidate_valid": reviewed.get("candidate_valid"),
                "accepted_capsule_exists": reviewed.get("accepted_capsule_exists"),
                "accepted_capsule_path": reviewed.get("accepted_capsule_path"),
                "gaps": listify(raw.get("gaps") or reviewed.get("gaps")),
                "blockers": listify(reviewed.get("blockers")),
                "recommended_next": listify(reviewed.get("recommended_next"))[:4],
                "authority": branch_authority,
                "surface_counts": _count_context_surfaces(surface_hints),
                "surface_hints_preview": _preview_context_surfaces(surface_hints),
            }
        )

    candidate_ready_count = review.get("candidate_review_ready_count")
    blocked_count = review.get("blocked_count")
    if not isinstance(candidate_ready_count, int):
        candidate_ready_count = sum(1 for row in branches if str(row.get("promotion_readiness", "")).startswith("candidate_review_ready"))
    if not isinstance(blocked_count, int):
        blocked_count = sum(1 for row in branches if row.get("blockers"))
    if source_present.get("cockpit_projection_spec") and branches:
        status = "visibility_projection_ready"
    elif any(source_present.values()):
        status = "partial_visibility_projection"
    else:
        status = "missing_source"
    return {
        "schema_id": "ion.cockpit_context_package_graph_projection.v1",
        "status": status,
        "generated_at": utc_now(),
        "packet_id": enrichment.get("packet_id") or cockpit_spec.get("packet_id") or review.get("next_packet_id"),
        "source_wave_id": enrichment.get("source_wave_id"),
        "source_paths": source_paths,
        "source_present": source_present,
        "branch_count": len(branches),
        "candidate_review_ready_count": candidate_ready_count,
        "blocked_count": blocked_count,
        "allowed_operations": listify(cockpit_spec.get("allowed_operations")),
        "forbidden_operations": listify(cockpit_spec.get("forbidden_operations")),
        "required_ui_fields": listify(cockpit_spec.get("required_ui_fields")),
        "candidate_state_only": bool(cockpit_spec.get("candidate_state_only", True)),
        "accepted_state_claim": False,
        "authority": {
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
        "branches": branches,
    }


def _yaml_scalar_block(text: str, key: str) -> str | None:
    prefix = f"{key}:"
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith(prefix):
            continue
        value = line.split(":", 1)[1].strip().strip("\"'")
        parts = [value] if value else []
        for follow in lines[index + 1:]:
            if not follow.strip():
                continue
            if not follow.startswith(" "):
                break
            stripped = follow.strip()
            if stripped.startswith("- "):
                break
            parts.append(stripped.strip("\"'"))
        joined = " ".join(part for part in parts if part).strip()
        return joined or None
    return None


def _yaml_top_list(text: str, key: str) -> list[str]:
    prefix = f"{key}:"
    values: list[str] = []
    collecting = False
    for line in text.splitlines():
        if line.startswith(prefix):
            collecting = True
            continue
        if not collecting:
            continue
        stripped = line.strip()
        if not stripped:
            continue
        if not line.startswith(" ") and not stripped.startswith("- "):
            break
        if stripped.startswith("- "):
            values.append(stripped[2:].strip().strip("\"'"))
    return values


def _yaml_mapping_scalars(text: str, key: str) -> dict[str, str]:
    prefix = f"{key}:"
    values: dict[str, str] = {}
    collecting = False
    for line in text.splitlines():
        if line.startswith(prefix):
            collecting = True
            continue
        if not collecting:
            continue
        if line and not line.startswith(" "):
            break
        if not line.startswith("  ") or line.startswith("    "):
            continue
        stripped = line.strip()
        if ":" not in stripped:
            continue
        field, value = stripped.split(":", 1)
        value = value.strip().strip("\"'")
        if value:
            values[field.strip()] = value
    return values


def _vnext_sequence_token(sequence_id: str) -> str:
    token = str(sequence_id or "").split("_", 1)[0].strip().upper()
    return token or "UNKNOWN"


def _vnext_sequence_sort_key(sequence_id: str) -> tuple[int, str]:
    token = _vnext_sequence_token(sequence_id)
    digits = ""
    suffix = ""
    for char in token[1:] if token.startswith("M") else token:
        if char.isdigit() and not suffix:
            digits += char
        else:
            suffix += char
    return (int(digits) if digits else 9999, suffix)


def _vnext_rel(root: Path, path: Path | None) -> str | None:
    if not path:
        return None
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _vnext_first_path(paths: list[Path]) -> Path | None:
    files = sorted({path for path in paths if path.exists() and path.is_file()}, key=lambda path: path.as_posix())
    return files[0] if files else None


def _vnext_first_dir(paths: list[Path]) -> Path | None:
    dirs = sorted({path for path in paths if path.exists() and path.is_dir()}, key=lambda path: path.as_posix())
    return dirs[-1] if dirs else None


def _vnext_gate_ids(value: Any) -> list[str]:
    gate_ids: list[str] = []
    for item in listify(value):
        if isinstance(item, Mapping):
            gate_id = item.get("gate_id") or item.get("requirement_id") or item.get("id")
            if gate_id:
                gate_ids.append(str(gate_id))
        elif item is not None:
            gate_ids.append(str(item))
    return gate_ids


def _vnext_closed_gates(result: Mapping[str, Any], token: str) -> list[str]:
    closed: list[str] = []
    lower = token.lower()
    for key, value in result.items():
        if key.startswith("blockers_closed_by_") or key == f"closed_by_{lower}":
            closed.extend(_vnext_gate_ids(value))
    return sorted(set(closed))


def _vnext_remaining_gates(result: Mapping[str, Any], token: str) -> list[str]:
    candidates = [
        result.get(f"remaining_gate_ids_after_{token.lower()}"),
        result.get("remaining_gate_ids"),
        result.get("remaining_cutover_blockers"),
        result.get("cutover_blockers"),
    ]
    remaining: list[str] = []
    for value in candidates:
        remaining.extend(_vnext_gate_ids(value))
    if not remaining:
        remaining.extend(_vnext_gate_ids(result.get("future_transition_requirements")))
    return sorted(set(remaining))


def _vnext_authority_flags(result: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "production_authority": bool(
            result.get("production_authority")
            or result.get("production_execution_authority_set")
            or result.get("production_cutover_authorized")
            or result.get("execution_authorized")
        ),
        "live_execution_authority": bool(result.get("live_execution_authority")),
        "accepted_state_claim": bool(result.get("accepted_state_claim")),
        "secrets_authority": bool(result.get("secrets_accessed")),
        "supabase_mutated": bool(result.get("supabase_mutated") or result.get("supabase_provider_api_call_attempted")),
    }


def _vnext_packet_row(root: Path, sequence_id: str) -> dict[str, Any]:
    token = _vnext_sequence_token(sequence_id)
    work_dir = root / VNEXT_WORK_DIR
    vnext_dir = root / VNEXT_ROOT
    packet_path = _vnext_first_path(list(work_dir.glob(f"{token}_*.md")) + list(vnext_dir.glob(f"**/{token}_*.md")))
    result_path = _vnext_first_path(list(work_dir.glob(f"{token.lower()}_*.json")))
    release_dir = _vnext_first_dir(list((root / VNEXT_RELEASES_DIR).glob(f"{token.lower()}_*")))
    result = read_json(result_path) if result_path else {}
    closed_gates = _vnext_closed_gates(result, token)
    remaining_gates = _vnext_remaining_gates(result, token)
    reviewed_gates = _vnext_gate_ids(result.get(f"reviewed_gate_ids_by_{token.lower()}") or result.get("reviewed_gate_ids"))
    status = "missing_evidence"
    if result_path:
        status = "result_recorded"
    elif packet_path:
        status = "packet_documented"
    return {
        "sequence_id": sequence_id,
        "token": token,
        "title": sequence_id.replace("_", " ").title(),
        "status": status,
        "packet_id": result.get("packet_id") or f"PCKT-{sequence_id}",
        "verdict": result.get("verdict") or result.get("status"),
        "created_at": result.get("created_at"),
        "packet_path": _vnext_rel(root, packet_path),
        "result_path": _vnext_rel(root, result_path),
        "artifact_root": _vnext_rel(root, release_dir) or result.get("artifact_root"),
        "release_artifact_count": len(list((release_dir / "OPERATOR_FINAL").glob("*"))) if release_dir and (release_dir / "OPERATOR_FINAL").exists() else 0,
        "closed_gates": closed_gates,
        "remaining_gates": remaining_gates,
        "reviewed_gates": reviewed_gates,
        "non_claims": [str(item) for item in listify(result.get("non_claims"))[:8]],
        "authority_flags": _vnext_authority_flags(result),
        "next_route": result.get("next_route"),
        "next_route_condition": result.get("next_route_condition"),
    }


def _vnext_gate_rows(packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gates: dict[str, dict[str, Any]] = {}
    for packet in packets:
        token = compact(packet.get("token"), "UNKNOWN")
        for gate_id in listify(packet.get("closed_gates")):
            gates[str(gate_id)] = {"gate_id": str(gate_id), "status": "closed", "latest_packet": token}
        for gate_id in listify(packet.get("reviewed_gates")):
            gates.setdefault(str(gate_id), {"gate_id": str(gate_id), "status": "reviewed", "latest_packet": token})
        for gate_id in listify(packet.get("remaining_gates")):
            gates[str(gate_id)] = {"gate_id": str(gate_id), "status": "open", "latest_packet": token}
    if not gates:
        gates = {
            "production_execution_authority_not_set": {
                "gate_id": "production_execution_authority_not_set",
                "status": "open",
                "latest_packet": "fallback",
            },
            "live_supabase_mirror_smoke_not_run_if_claimed": {
                "gate_id": "live_supabase_mirror_smoke_not_run_if_claimed",
                "status": "open",
                "latest_packet": "fallback",
            },
        }
    return sorted(gates.values(), key=lambda row: (0 if row.get("status") == "open" else 1, str(row.get("gate_id"))))


def _vnext_latest_receipt(root: Path) -> dict[str, Any]:
    status = read_json(root / CODEX_SOLO_STATUS)
    recent_rows = status.get("capsule", {}).get("recent_rows") if isinstance(status.get("capsule"), Mapping) else []
    rows = [row for row in listify(recent_rows) if isinstance(row, Mapping)]
    if not rows:
        return {}
    latest = rows[-1]
    return {
        "id": latest.get("id"),
        "date": latest.get("date"),
        "summary": latest.get("summary"),
        "status": latest.get("status"),
        "evidence": latest.get("evidence"),
    }


def _vnext_lanes(root: Path, operating_model: Mapping[str, str], packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    m93 = next((packet for packet in packets if packet.get("token") == "M93"), {})
    latest = next((packet for packet in reversed(packets) if packet.get("status") == "result_recorded"), {})
    return [
        {
            "lane_id": "local_ion_core",
            "label": "Local ION Core",
            "status": "active" if (root / "ION/REPO_AUTHORITY.md").exists() else "missing",
            "posture": compact(operating_model.get("source_truth"), "local_ion_files_receipts_context_packets"),
            "evidence_path": "ION/REPO_AUTHORITY.md",
        },
        {
            "lane_id": "codex_cli",
            "label": "Codex CLI",
            "status": "active",
            "posture": compact(operating_model.get("primary_build_and_test_loop"), "codex_cli_local_worker"),
            "evidence_path": "ION/05_context/current/codex_solo/STATUS.json",
        },
        {
            "lane_id": "browser_gpt",
            "label": "Browser GPT Relay",
            "status": "relay_defined",
            "posture": compact(operating_model.get("human_facing_relay"), "browser_gpt_relay_persona"),
            "evidence_path": VNEXT_FRONT_DOOR_AI.as_posix(),
        },
        {
            "lane_id": "actions_mcp",
            "label": "Actions / MCP",
            "status": "bounded_bridge",
            "posture": compact(operating_model.get("bridge_plane"), "actions_mcp_chatops"),
            "evidence_path": compact(m93.get("result_path"), "ION_VNEXT/05_runtime/M86_ACTIONS_MCP_SUPABASE_BRIDGE.md"),
        },
        {
            "lane_id": "supabase_mirror",
            "label": "Supabase Mirror",
            "status": "mirror_only",
            "posture": compact(operating_model.get("mirror_plane"), "supabase_mirror_cockpit_non_authoritative"),
            "evidence_path": compact(m93.get("result_path"), "ION_VNEXT/05_runtime/M86_ACTIONS_MCP_SUPABASE_BRIDGE.md"),
        },
        {
            "lane_id": "context_receipts",
            "label": "Context / Receipts",
            "status": "active",
            "posture": compact(operating_model.get("accepted_state_rule"), "proof_gate_receipt_then_steward_or_operator_acceptance"),
            "evidence_path": compact(latest.get("result_path"), "ION/05_context/current/codex_solo/STATUS.json"),
        },
        {
            "lane_id": "vnext_front_door",
            "label": "vNext Front Door",
            "status": "active" if (root / VNEXT_WORKSPACE_CANON).exists() else "missing",
            "posture": "front_door_canon_currentness",
            "evidence_path": VNEXT_WORKSPACE_CANON.as_posix(),
        },
    ]


VNEXT_MISSION_FAMILIES: dict[str, dict[str, Any]] = {
    "vnext_direct_rebuild": {
        "label": "vNext Direct Rebuild",
        "description": "Front-door, canon, cutover, release, rollback, and authority packet sequence.",
        "keywords": ["vnext", "cutover", "production", "authority", "release", "rollback", "m100", "m101", "m102"],
    },
    "codex_cockpit_carrier": {
        "label": "Codex / Cockpit Carrier",
        "description": "Codex CLI, Capsule chat, cockpit workbench, archive, local build/test carrier, and UI surfaces.",
        "keywords": ["codex", "cockpit", "capsule", "workbench", "chat", "ui", "joc", "conversation"],
    },
    "browser_actions_mcp": {
        "label": "Browser GPT / Actions / MCP",
        "description": "Browser relay, ChatOps, MCP bridge, Action Gateway, extension, and bounded tool surfaces.",
        "keywords": ["browser", "chatgpt", "mcp", "action", "chatops", "extension", "gateway", "connector"],
    },
    "context_receipts_memory": {
        "label": "Context / Receipts / Memory",
        "description": "Capsules, long horizon, receipts, continuity, context graph, proof and settlement lanes.",
        "keywords": ["context", "receipt", "memory", "continuity", "horizon", "settlement", "proof", "capsule"],
    },
    "agent_worker_orchestration": {
        "label": "Agents / Workers / Orchestration",
        "description": "Role phases, worker shift, branch gateways, spawn rows, fanout, Steward/Relay/Mason flows.",
        "keywords": ["agent", "worker", "branch", "spawn", "steward", "relay", "mason", "role", "fanout"],
    },
    "supabase_runtime_mirror": {
        "label": "Supabase / Runtime Mirror",
        "description": "Mirror-only Supabase posture, services, runtime state, cockpit visibility, and health planes.",
        "keywords": ["supabase", "runtime", "service", "daemon", "mirror", "health", "status"],
    },
    "docs_protocols_canon": {
        "label": "Docs / Protocols / Canon",
        "description": "Doctrine, protocol corpus, registries, templates, documentation surfaces, and currentness law.",
        "keywords": ["protocol", "doctrine", "canon", "registry", "template", "documentation", "docs"],
    },
    "product_release_packaging": {
        "label": "Product / Release / Packaging",
        "description": "Operator surfaces, package hygiene, GPT kits, release bundles, product packaging, and distribution.",
        "keywords": ["product", "package", "operator", "gpt", "bundle", "artifact", "release"],
    },
}


def _vnext_family_for_text(text: str) -> str:
    haystack = text.lower()
    best_family = "docs_protocols_canon"
    best_score = 0
    for family_id, spec in VNEXT_MISSION_FAMILIES.items():
        score = sum(haystack.count(keyword) for keyword in spec["keywords"])
        if score > best_score:
            best_family = family_id
            best_score = score
    return best_family


def _frontmatter_fields(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        value = value.strip().strip("\"'")
        if value:
            fields[key.strip()] = value
    return fields


def _first_markdown_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            title = stripped.lstrip("#").strip()
            if title:
                return title
    return fallback


def _protocol_kind(path: Path) -> str:
    name = path.name.upper()
    if "PROTOCOL" in name:
        return "protocol"
    if path.suffix.lower() in {".yaml", ".yml", ".json"}:
        return "structured_index"
    if "README" in name:
        return "readme"
    if "PLAN" in name or "ROADMAP" in name:
        return "plan"
    return "document"


def _vnext_protocol_inventory(root: Path) -> dict[str, Any]:
    scan_roots = [
        Path("ION/01_doctrine"),
        Path("ION/02_architecture"),
        Path("ION/docs/setup"),
        Path("ION/06_intelligence/orchestration"),
        VNEXT_ROOT / "00_front_door",
        VNEXT_ROOT / "01_canon",
        VNEXT_ROOT / "02_kernel",
        VNEXT_ROOT / "04_carriers",
        VNEXT_ROOT / "05_runtime",
        VNEXT_ROOT / "06_context",
        VNEXT_ROOT / "07_work",
    ]
    rows: list[dict[str, Any]] = []
    for base_rel in scan_roots:
        base = root / base_rel
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".md", ".yaml", ".yml", ".json"}:
                continue
            rel = path.relative_to(root).as_posix()
            text = _read_text(path)[:12000]
            fields = _frontmatter_fields(text)
            title = _first_markdown_heading(text, path.stem.replace("_", " ").title())
            family = _vnext_family_for_text(f"{rel} {title} {fields.get('type', '')} {fields.get('authority', '')}")
            rows.append(
                {
                    "path": rel,
                    "name": path.name,
                    "title": title,
                    "kind": _protocol_kind(path),
                    "family_id": family,
                    "authority": fields.get("authority"),
                    "status": fields.get("status"),
                    "type": fields.get("type"),
                    "bytes": path.stat().st_size if path.exists() else 0,
                }
            )
    groups: dict[str, dict[str, Any]] = {}
    for row in rows:
        family_id = str(row["family_id"])
        group = groups.setdefault(
            family_id,
            {
                "family_id": family_id,
                "label": VNEXT_MISSION_FAMILIES.get(family_id, {}).get("label", family_id),
                "protocol_count": 0,
                "authority_count": 0,
                "sample_paths": [],
            },
        )
        group["protocol_count"] += 1
        if row.get("authority"):
            group["authority_count"] += 1
        if len(group["sample_paths"]) < 5:
            group["sample_paths"].append(row["path"])
    return {
        "schema_id": "ion.vnext_protocol_inventory.v1",
        "generated_at": utc_now(),
        "source_roots": [path.as_posix() for path in scan_roots],
        "protocol_count": len(rows),
        "groups": sorted(groups.values(), key=lambda item: (-int(item["protocol_count"]), str(item["label"]))),
        "rows": rows,
    }


def _vnext_long_horizon_projection(root: Path) -> dict[str, Any]:
    payload = read_json(root / CODEX_SOLO_LONG_HORIZON)
    raw_epochs = listify(payload.get("epochs") or payload.get("latest_epochs"))
    epochs: list[dict[str, Any]] = []
    family_counts: dict[str, int] = {}
    for raw_epoch in raw_epochs:
        if not isinstance(raw_epoch, Mapping):
            continue
        summaries = [dict(row) for row in listify(raw_epoch.get("summaries")) if isinstance(row, Mapping)]
        evidence_refs = [str(item) for item in listify(raw_epoch.get("evidence_refs"))]
        family_text = " ".join(
            [
                str(raw_epoch.get("epoch_id") or ""),
                str(raw_epoch.get("row_start") or ""),
                str(raw_epoch.get("row_end") or ""),
                " ".join(str(row.get("summary") or "") for row in summaries),
                " ".join(evidence_refs[:24]),
            ]
        )
        family_id = _vnext_family_for_text(family_text)
        family_counts[family_id] = family_counts.get(family_id, 0) + 1
        epochs.append(
            {
                "epoch_id": raw_epoch.get("epoch_id"),
                "date_start": raw_epoch.get("date_start"),
                "date_end": raw_epoch.get("date_end"),
                "row_start": raw_epoch.get("row_start"),
                "row_end": raw_epoch.get("row_end"),
                "row_count": raw_epoch.get("row_count"),
                "status_counts": raw_epoch.get("status_counts", {}),
                "family_id": family_id,
                "evidence_refs": evidence_refs[:18],
                "summaries": summaries,
            }
        )
    latest_epoch_ids = [
        str(raw_epoch.get("epoch_id"))
        for raw_epoch in listify(payload.get("latest_epochs"))
        if isinstance(raw_epoch, Mapping) and raw_epoch.get("epoch_id")
    ]
    epochs_by_id = {str(epoch.get("epoch_id")): epoch for epoch in epochs if epoch.get("epoch_id")}
    latest_epochs = [epochs_by_id[epoch_id] for epoch_id in latest_epoch_ids if epoch_id in epochs_by_id]
    if not latest_epochs:
        latest_epochs = epochs[-6:]
    return {
        "schema_id": "ion.vnext_long_horizon_projection.v1",
        "generated_at": utc_now(),
        "source_path": CODEX_SOLO_LONG_HORIZON.as_posix(),
        "capsule_entry_count": payload.get("capsule_entry_count", 0),
        "epoch_count": payload.get("epoch_count") or len(epochs),
        "production_authority": False,
        "live_execution_authority": False,
        "family_counts": [
            {
                "family_id": family_id,
                "label": VNEXT_MISSION_FAMILIES.get(family_id, {}).get("label", family_id),
                "epoch_count": count,
            }
            for family_id, count in sorted(family_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
        "latest_epochs": latest_epochs,
        "epochs": epochs,
    }


def _vnext_context_package_projection(root: Path) -> dict[str, Any]:
    payload = read_json(root / CODEX_CONTEXT_PACKAGES)
    packages: list[dict[str, Any]] = []
    for raw in listify(payload.get("packages")):
        if not isinstance(raw, Mapping):
            continue
        refs = [str(item) for item in listify(raw.get("path_refs"))]
        missing = [ref for ref in refs if not (root / ref).exists()]
        family_id = _vnext_family_for_text(f"{raw.get('package_id')} {raw.get('context_type')} {' '.join(refs)}")
        packages.append(
            {
                "package_id": raw.get("package_id"),
                "context_type": raw.get("context_type"),
                "load_policy": raw.get("load_policy"),
                "family_id": family_id,
                "path_refs": refs,
                "missing_refs": missing,
                "window": raw.get("window", {}),
            }
        )
    return {
        "schema_id": "ion.vnext_context_package_projection.v1",
        "generated_at": utc_now(),
        "source_path": CODEX_CONTEXT_PACKAGES.as_posix(),
        "package_count": len(packages),
        "missing_ref_count": sum(len(row["missing_refs"]) for row in packages),
        "packages": packages,
    }


def _vnext_documentation_surfaces(root: Path) -> dict[str, Any]:
    surfaces = [
        {"surface_id": "front_door", "label": "vNext Front Door", "root": VNEXT_ROOT / "00_front_door"},
        {"surface_id": "canon", "label": "vNext Canon", "root": VNEXT_ROOT / "01_canon"},
        {"surface_id": "kernel", "label": "vNext Kernel", "root": VNEXT_ROOT / "02_kernel"},
        {"surface_id": "carriers", "label": "Carriers", "root": VNEXT_ROOT / "04_carriers"},
        {"surface_id": "runtime", "label": "Runtime", "root": VNEXT_ROOT / "05_runtime"},
        {"surface_id": "context", "label": "Context", "root": VNEXT_ROOT / "06_context"},
        {"surface_id": "work", "label": "Work Packets", "root": VNEXT_ROOT / "07_work"},
        {"surface_id": "releases", "label": "Releases", "root": VNEXT_ROOT / "08_releases"},
        {"surface_id": "doctrine", "label": "ION Doctrine", "root": Path("ION/01_doctrine")},
        {"surface_id": "architecture", "label": "ION Architecture", "root": Path("ION/02_architecture")},
    ]
    rows = []
    for surface in surfaces:
        base = root / surface["root"]
        files = sorted(
            [
                path
                for path in base.rglob("*")
                if path.is_file() and path.suffix.lower() in {".md", ".yaml", ".yml", ".json"}
            ]
        ) if base.exists() else []
        rows.append(
            {
                "surface_id": surface["surface_id"],
                "label": surface["label"],
                "root": surface["root"].as_posix(),
                "exists": base.exists(),
                "file_count": len(files),
                "sample_paths": [path.relative_to(root).as_posix() for path in files[:10]],
            }
        )
    return {
        "schema_id": "ion.vnext_documentation_surfaces.v1",
        "generated_at": utc_now(),
        "surface_count": len(rows),
        "file_count": sum(int(row["file_count"]) for row in rows),
        "surfaces": rows,
    }


def _vnext_mission_family_projection(
    *,
    packets: list[dict[str, Any]],
    long_horizon: Mapping[str, Any],
    protocol_index: Mapping[str, Any],
    context_packages: Mapping[str, Any],
) -> list[dict[str, Any]]:
    family_rows: dict[str, dict[str, Any]] = {
        family_id: {
            "family_id": family_id,
            "label": spec["label"],
            "description": spec["description"],
            "packet_count": 0,
            "epoch_count": 0,
            "protocol_count": 0,
            "context_package_count": 0,
            "evidence_paths": [],
            "status": "mapped",
        }
        for family_id, spec in VNEXT_MISSION_FAMILIES.items()
    }
    for packet in packets:
        family_id = _vnext_family_for_text(" ".join(str(packet.get(key) or "") for key in ("sequence_id", "title", "packet_id", "verdict")))
        row = family_rows[family_id]
        row["packet_count"] += 1
        path = packet.get("result_path") or packet.get("packet_path")
        if path and len(row["evidence_paths"]) < 6:
            row["evidence_paths"].append(path)
    for epoch in listify(long_horizon.get("epochs")):
        if not isinstance(epoch, Mapping):
            continue
        family_id = str(epoch.get("family_id") or "docs_protocols_canon")
        row = family_rows.setdefault(family_id, {
            "family_id": family_id,
            "label": family_id,
            "description": "",
            "packet_count": 0,
            "epoch_count": 0,
            "protocol_count": 0,
            "context_package_count": 0,
            "evidence_paths": [],
            "status": "mapped",
        })
        row["epoch_count"] += 1
        for path in listify(epoch.get("evidence_refs")):
            if path and len(row["evidence_paths"]) < 6:
                row["evidence_paths"].append(path)
    for group in listify(protocol_index.get("groups")):
        if isinstance(group, Mapping) and group.get("family_id") in family_rows:
            family_rows[str(group["family_id"])]["protocol_count"] = group.get("protocol_count", 0)
    for package in listify(context_packages.get("packages")):
        if isinstance(package, Mapping) and package.get("family_id") in family_rows:
            family_rows[str(package["family_id"])]["context_package_count"] += 1
    return sorted(
        family_rows.values(),
        key=lambda row: (
            -int(row["packet_count"]) - int(row["epoch_count"]) - int(row["protocol_count"]) - int(row["context_package_count"]),
            str(row["label"]),
        ),
    )


def _vnext_mission_control_summary(root: Path) -> dict[str, Any]:
    canon_text = _read_text(root / VNEXT_WORKSPACE_CANON)
    source_paths = {
        "vnext_root": VNEXT_ROOT.as_posix(),
        "workspace_canon": VNEXT_WORKSPACE_CANON.as_posix(),
        "ai_start": VNEXT_FRONT_DOOR_AI.as_posix(),
        "human_start": VNEXT_FRONT_DOOR_HUMAN.as_posix(),
        "route_map": VNEXT_ROUTE_MAP.as_posix(),
        "authority_boundaries": VNEXT_AUTHORITY_BOUNDARIES.as_posix(),
        "control_surface_registry": VNEXT_CONTROL_SURFACE_REGISTRY.as_posix(),
        "state_lifecycle": VNEXT_STATE_LIFECYCLE.as_posix(),
        "work_dir": VNEXT_WORK_DIR.as_posix(),
        "release_dir": VNEXT_RELEASES_DIR.as_posix(),
        "codex_solo_status": CODEX_SOLO_STATUS.as_posix(),
    }
    source_present = {key: (root / Path(path)).exists() for key, path in source_paths.items()}
    if not (root / VNEXT_ROOT).exists():
        return {
            "schema_id": "ion.vnext_mission_control_projection.v1",
            "generated_at": utc_now(),
            "status": "missing",
            "mission": "ION_VNEXT source tree is not present.",
            "read_only": True,
            "source_paths": source_paths,
            "source_present": source_present,
            "packets": [],
            "lanes": [],
            "gates": [],
            "drift_guards": [],
            "authority": {
                "accepted_state_authority": False,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
                "read_only_projection": True,
            },
        }
    sequence = _yaml_top_list(canon_text, "current_direct_rebuild_sequence")
    if not sequence:
        sequence = sorted(
            [path.stem.upper() for path in (root / VNEXT_WORK_DIR).glob("M*.md")],
            key=_vnext_sequence_sort_key,
        )
    packets = [_vnext_packet_row(root, sequence_id) for sequence_id in sequence]
    latest_packet = next((packet for packet in reversed(packets) if packet.get("status") == "result_recorded"), packets[-1] if packets else {})
    operating_model = _yaml_mapping_scalars(canon_text, "current_operating_model")
    deferred = _yaml_top_list(canon_text, "deferred_by_default")
    gates = _vnext_gate_rows(packets)
    long_horizon = _vnext_long_horizon_projection(root)
    protocol_index = _vnext_protocol_inventory(root)
    context_packages = _vnext_context_package_projection(root)
    documentation_surfaces = _vnext_documentation_surfaces(root)
    mission_families = _vnext_mission_family_projection(
        packets=packets,
        long_horizon=long_horizon,
        protocol_index=protocol_index,
        context_packages=context_packages,
    )
    open_gate_count = len([gate for gate in gates if gate.get("status") == "open"])
    any_authority = any(any(packet.get("authority_flags", {}).values()) for packet in packets)
    status = "mission_map_ready" if source_present.get("workspace_canon") and packets and not any_authority else "degraded"
    return {
        "schema_id": "ion.vnext_mission_control_projection.v1",
        "generated_at": utc_now(),
        "status": status,
        "mission": _yaml_scalar_block(canon_text, "mission") or "Clean local-first ION vNext operating layer.",
        "canon_status": _yaml_scalar_block(canon_text, "status"),
        "read_only": True,
        "source_paths": source_paths,
        "source_present": source_present,
        "operating_model": operating_model,
        "current_packet": latest_packet,
        "latest_result": {
            "path": latest_packet.get("result_path"),
            "verdict": latest_packet.get("verdict"),
            "created_at": latest_packet.get("created_at"),
        },
        "latest_receipt": _vnext_latest_receipt(root),
        "lanes": _vnext_lanes(root, operating_model, packets),
        "packets": packets,
        "gates": gates,
        "mission_families": mission_families,
        "long_horizon": long_horizon,
        "protocol_index": protocol_index,
        "context_packages": context_packages,
        "documentation_surfaces": documentation_surfaces,
        "gate_summary": {
            "open": open_gate_count,
            "closed": len([gate for gate in gates if gate.get("status") == "closed"]),
            "reviewed": len([gate for gate in gates if gate.get("status") == "reviewed"]),
        },
        "drift_guards": [
            {
                "guard_id": "deferred_by_default",
                "status": "active",
                "items": deferred,
                "detail": "These lanes remain reference/deferred unless a later packet reactivates them.",
            },
            {
                "guard_id": "model_output_is_not_state",
                "status": "active",
                "items": ["files", "receipts", "validation", "custody"],
                "detail": "The cockpit projects local evidence; it does not create accepted state.",
            },
            {
                "guard_id": "supabase_mirror_only",
                "status": "active",
                "items": ["refs", "hashes", "events", "health", "cockpit_state"],
                "detail": "Supabase remains visibility/mirror posture in this projection.",
            },
        ],
        "next_safe_route": {
            "route": latest_packet.get("next_route") or "NO_AUTOMATIC_ROUTE_RECORDED",
            "condition": latest_packet.get("next_route_condition") or "Use the next proof-gated packet before any authority movement.",
            "automatic": False,
        },
        "authority": {
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
            "read_only_projection": True,
            "supabase_mutation_authority": False,
        },
    }


def _helixion_joc_rebuild_summary(root: Path) -> dict[str, Any]:
    current_plan = read_json(root / HELIXION_REBUILD_CURRENT_PLAN)
    phase_0_gate = current_plan.get("phase_0_exit_gate") if isinstance(current_plan.get("phase_0_exit_gate"), dict) else {}
    phase_1_package = current_plan.get("phase_1_orchestration_context_package") if isinstance(current_plan.get("phase_1_orchestration_context_package"), dict) else {}
    phase_2_shell = current_plan.get("phase_2_local_shell_seed") if isinstance(current_plan.get("phase_2_local_shell_seed"), dict) else {}
    react_bundle = phase_2_shell.get("react_bundle") if isinstance(phase_2_shell.get("react_bundle"), dict) else {}
    return {
        "schema_id": "ion.helixion_joc_rebuild_projection.v1",
        "status": compact(current_plan.get("status"), "not_documented"),
        "decision": compact(current_plan.get("decision"), "no rebuild decision recorded"),
        "master_plan_path": str(HELIXION_REBUILD_PLAN),
        "registry_path": str(HELIXION_REBUILD_REGISTRY),
        "current_plan_path": str(HELIXION_REBUILD_CURRENT_PLAN),
        "master_plan_present": (root / HELIXION_REBUILD_PLAN).exists(),
        "registry_present": (root / HELIXION_REBUILD_REGISTRY).exists(),
        "current_plan_present": (root / HELIXION_REBUILD_CURRENT_PLAN).exists(),
        "ready_for_phase_1": bool(phase_0_gate.get("ready_for_phase_1")),
        "phase_0_gate": phase_0_gate,
        "product_roles": current_plan.get("primary_product_roles", {}),
        "required_surfaces": listify(current_plan.get("required_surfaces")),
        "canonical_zones": listify(current_plan.get("canonical_zones")),
        "canonical_object_types": listify(current_plan.get("canonical_object_types")),
        "allowed_v1_capabilities": listify(current_plan.get("allowed_v1_capabilities")),
        "forbidden_v1_capabilities": listify(current_plan.get("forbidden_v1_capabilities")),
        "next_build_sequence": listify(current_plan.get("next_build_sequence")),
        "source_authorities": listify(current_plan.get("source_authorities")),
        "orchestration_context_package": phase_1_package,
        "local_shell": phase_2_shell,
        "react_bundle": react_bundle,
        "development_urls": listify(phase_2_shell.get("development_urls")),
        "latest_capsule_entry_id": phase_2_shell.get("capsule_entry_id") or phase_1_package.get("capsule_entry_id"),
        "latest_history_receipt": phase_2_shell.get("history_receipt") or phase_1_package.get("history_receipt"),
        "latest_codex_solo_checkpoint_id": phase_2_shell.get("codex_solo_checkpoint_id") or phase_1_package.get("codex_solo_checkpoint_id"),
        "authority_posture": current_plan.get("authority_posture", {}),
        "production_authority": False,
        "live_execution_authority": False,
        "unrestricted_browser_control": False,
    }


def _branch_gateway_read(
    root: Path,
    *,
    branch_id: str,
    route_id: str,
    args: dict[str, Any] | None = None,
) -> dict[str, Any]:
    try:
        return action_branch_invoke(
            root,
            branch_id=branch_id,
            route_id=route_id,
            args=args or {},
            expected_route_schema_version="v0",
        )
    except Exception as exc:  # pragma: no cover - cockpit projection must fail soft
        return {
            "ok": False,
            "finding": exc.__class__.__name__,
            "branch_id": branch_id,
            "route_id": route_id,
            "mutates_active_state": False,
            "production_authority": False,
            "live_execution_authority": False,
        }


def _branch_gateway_describe(root: Path, branch_id: str) -> dict[str, Any]:
    try:
        return action_branch_describe(root, branch_id=branch_id, depth="summary")
    except Exception as exc:  # pragma: no cover - cockpit projection must fail soft
        return {
            "ok": False,
            "finding": exc.__class__.__name__,
            "branch_id": branch_id,
            "mutates_active_state": False,
            "production_authority": False,
            "live_execution_authority": False,
        }


def _delegated(payload: Mapping[str, Any]) -> dict[str, Any]:
    delegated = payload.get("delegated_result")
    return dict(delegated) if isinstance(delegated, Mapping) else {}


def _runtime_service_status_rows(status_payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    delegated = _delegated(status_payload)
    services = delegated.get("services")
    if not isinstance(services, list):
        return []
    return [dict(service) for service in services if isinstance(service, Mapping)]


def _service_ids_from_status(status_payload: Mapping[str, Any]) -> list[str]:
    delegated = _delegated(status_payload)
    allowed = delegated.get("allowed_service_ids")
    if isinstance(allowed, list):
        return [str(item) for item in allowed if str(item or "").strip()]
    ids = []
    for service in _runtime_service_status_rows(status_payload):
        service_id = str(service.get("service_id") or "").strip()
        if service_id:
            ids.append(service_id)
    return sorted(set(ids))


def _runtime_service_plan_map(root: Path, service_ids: Iterable[str]) -> dict[str, dict[str, Any]]:
    plans: dict[str, dict[str, Any]] = {}
    for service_id in service_ids:
        plans[service_id] = _branch_gateway_read(
            root,
            branch_id="runtime_services",
            route_id="service_reload_plan",
            args={"service_id": service_id},
        )
    return plans


def _runtime_service_control_rows(
    root: Path,
    status_payload: Mapping[str, Any],
    reload_plans: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    rows = []
    service_rows = _runtime_service_status_rows(status_payload)
    service_ids = {str(service.get("service_id") or "").strip() for service in service_rows}
    service_ids.update(str(service_id) for service_id in reload_plans)
    for service_id in sorted(service_id for service_id in service_ids if service_id):
        service = next((row for row in service_rows if row.get("service_id") == service_id), {})
        plan_payload = dict(reload_plans.get(service_id) or {})
        plan = _delegated(plan_payload)
        rows.append(
            {
                "service_id": service_id,
                "service_status": service,
                "service_reload_plan": plan,
                "allowed_service_id": service_id in _service_ids_from_status(status_payload),
                "restart_route_id": "restart_service",
                "reload_and_retest_route_id": "reload_and_retest",
                "requires_confirmation": True,
                "required_confirmation": BRANCH_GATEWAY_CONFIRMATION_TOKEN,
                "requires_idempotency_key": True,
                "shows_plan_before_action": bool(plan),
                "receipt_handoff_dir": repo_rel(root / RUNTIME_SERVICE_RECEIPTS_DIR, root),
                "cockpit_executes_mutation": False,
                "mutates_active_state": False,
            }
        )
    return rows


def _joc_message_body(row: Mapping[str, Any]) -> str:
    for key in ("body", "message", "content", "summary", "objective", "title", "detail"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _joc_timestamp(row: Mapping[str, Any]) -> str | None:
    for key in ("created_at", "updated_at", "timestamp", "time", "queued_at"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _joc_comms_channel(
    *,
    channel_id: str,
    label: str,
    source_surface: str,
    channel_kind: str,
    count: int,
    write_policy: str,
    latest_event_at: str | None = None,
    required_tool_or_route: str | None = None,
) -> dict[str, Any]:
    return {
        "channel_id": channel_id,
        "label": label,
        "source_surface": source_surface,
        "channel_kind": channel_kind,
        "authority_scope": "read_only_projection",
        "unread_or_pending_count": count,
        "thread_count": count,
        "latest_event_at": latest_event_at,
        "required_tool_or_route": required_tool_or_route,
        "write_policy": write_policy,
        "production_authority": False,
        "live_execution_authority": False,
        "write_authority": False,
    }


def _joc_comms_message(
    *,
    row: Mapping[str, Any],
    index: int,
    channel_id: str,
    sender_kind: str,
    source_path: str,
) -> dict[str, Any]:
    message_id = compact(row.get("message_id") or row.get("id") or row.get("request_id") or row.get("packet_id"), f"{channel_id}_{index}")
    thread_id = compact(row.get("thread_id") or row.get("request_id") or row.get("packet_id") or row.get("task_return_id"), f"{channel_id}_thread_{index}")
    sender_id = compact(row.get("sender_carrier_id") or row.get("sender_id") or row.get("from") or row.get("role") or row.get("requested_by"), sender_kind)
    receipt_refs = [item for item in listify(row.get("receipt_refs") or row.get("receipts") or row.get("receipt_path")) if item]
    context_refs = [item for item in listify(row.get("context_refs") or row.get("source_refs") or row.get("artifact_refs")) if item]
    return {
        "message_id": str(message_id),
        "thread_id": str(thread_id),
        "channel_id": channel_id,
        "sender_id": str(sender_id),
        "sender_kind": sender_kind,
        "recipient": row.get("recipient") or row.get("to") or row.get("target"),
        "body": _joc_message_body(row),
        "message_type": compact(row.get("message_type") or row.get("type") or row.get("status"), "message"),
        "source_path": source_path,
        "context_refs": context_refs,
        "receipt_refs": receipt_refs,
        "status": compact(row.get("status"), "unknown"),
        "acked_by": listify(row.get("acked_by")),
        "created_at": _joc_timestamp(row),
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def build_joc_comms_projection(
    root: Path,
    data: Mapping[str, dict[str, Any]],
    *,
    operator_items: list[dict[str, Any]],
    steward_items: list[dict[str, Any]],
    task_return_records: list[dict[str, Any]],
    agent_control_plane: Mapping[str, Any],
    chatgpt_browser_mcp: Mapping[str, Any],
) -> dict[str, Any]:
    carrier_items = _carrier_message_items(dict(data.get("carrier_messages") or {}))
    codex_queue = read_json(root / CURRENT / "ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json")
    codex_requests = [item for item in listify(codex_queue.get("requests")) if isinstance(item, dict)]
    agent_invocations = [item for item in listify(chatgpt_browser_mcp.get("latest_agent_invocations")) if isinstance(item, dict)]
    browser_queue_items = [item for item in listify(chatgpt_browser_mcp.get("latest_carrier_messages")) if isinstance(item, dict)]
    receipt_rows = recent_receipts(root, limit=8)

    source_paths = {
        "operator_queue": str(ACTIVE_FILES["operator_queue"]),
        "carrier_messages": str(ACTIVE_FILES["carrier_messages"]),
        "steward_integration": str(ACTIVE_FILES["steward"]),
        "task_returns": str(ACTIVE_FILES["ledger"]),
        "codex_queue": str(CURRENT / "ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json"),
        "agent_invocations": "ION/05_context/current/chatgpt_connector/agent_invocations/",
        "browser_queue": "ION/05_context/current/chatgpt_connector/browser_queue/",
        "receipts": "ION/05_context/current/chatgpt_connector/artifact_receipts/",
    }
    source_present = {key: (root / path).exists() for key, path in source_paths.items()}

    channel_sources: list[tuple[str, str, str, str, list[dict[str, Any]], str, str | None]] = [
        ("operator_queue", "Operator Queue", source_paths["operator_queue"], "operator_queue", operator_items, "existing_operator_queue_tools_only", None),
        ("carrier_messages", "Carrier Messages", source_paths["carrier_messages"], "carrier_messages", carrier_items, "ion_carrier_message_send_requires_confirmation", "ion_carrier_message_poll"),
        ("steward_integration", "Steward Integration", source_paths["steward_integration"], "steward_integration", steward_items, "steward_gate_only", None),
        ("task_returns", "Task Returns", source_paths["task_returns"], "task_returns", task_return_records, "ion_submit_task_return_requires_confirmation_and_proof", None),
        ("codex_queue", "Codex Queue", source_paths["codex_queue"], "codex_queue", codex_requests, "codex_work_packet_or_process_requires_confirmation", None),
        ("agent_invocations", "Agent Invocations", source_paths["agent_invocations"], "agent_invocations", agent_invocations, "ion_agent_invoke_requires_confirmation", None),
        ("browser_queue", "Browser Queue", source_paths["browser_queue"], "browser_queue", browser_queue_items, "gateway_or_browser_queue_authority_only", None),
        ("receipts", "Receipts", source_paths["receipts"], "receipts", receipt_rows, "read_only_by_default", "ion_receipt_search"),
    ]

    channels = [
        _joc_comms_channel(
            channel_id=channel_id,
            label=label,
            source_surface=source_surface,
            channel_kind=kind,
            count=len(rows),
            write_policy=write_policy,
            latest_event_at=next((_joc_timestamp(row) for row in rows if _joc_timestamp(row)), None),
            required_tool_or_route=route,
        )
        for channel_id, label, source_surface, kind, rows, write_policy, route in channel_sources
    ]

    messages: list[dict[str, Any]] = []
    sender_kinds = {
        "operator_queue": "human_operator",
        "carrier_messages": "carrier",
        "steward_integration": "steward",
        "task_returns": "codex_worker",
        "codex_queue": "system_projection",
        "agent_invocations": "agent",
        "browser_queue": "carrier",
        "receipts": "receipt_surface",
    }
    for channel_id, _label, source_surface, kind, rows, _write_policy, _route in channel_sources:
        for index, row in enumerate(rows[:50], start=1):
            messages.append(_joc_comms_message(row=row, index=index, channel_id=channel_id, sender_kind=sender_kinds.get(kind, "system_projection"), source_path=source_surface))

    threads: list[dict[str, Any]] = []
    for message in messages:
        thread_id = str(message.get("thread_id"))
        if any(existing.get("thread_id") == thread_id for existing in threads):
            continue
        sibling_count = sum(1 for item in messages if item.get("thread_id") == thread_id)
        threads.append(
            {
                "thread_id": thread_id,
                "channel_id": message.get("channel_id"),
                "title": message.get("body") or message.get("message_id"),
                "thread_kind": message.get("message_type"),
                "source_refs": [message.get("source_path")],
                "context_refs": message.get("context_refs", []),
                "receipt_refs": message.get("receipt_refs", []),
                "status": message.get("status"),
                "next_allowed_actions": ["open_context", "open_receipt"],
                "authority_boundary": "read_only_projection_no_live_send_ack_or_invoke",
                "message_count": sibling_count,
                "latest_summary": message.get("body"),
                "updated_at": message.get("created_at"),
                "production_authority": False,
                "live_execution_authority": False,
            }
        )

    participants = []
    for agent in [item for item in listify(agent_control_plane.get("agents")) if isinstance(item, dict)][:40]:
        participant_id = compact(agent.get("role_id") or agent.get("agent_id") or agent.get("display_name"), "agent")
        participants.append(
            {
                "participant_id": participant_id,
                "display_name": compact(agent.get("display_name"), participant_id),
                "participant_kind": "agent",
                "carrier_id": agent.get("backend_carrier_id"),
                "domain_id": agent.get("registry_primary_domain"),
                "context_package_path": agent.get("active_context_package"),
                "mount_receipt_path": agent.get("context_load_receipt_path"),
                "status": compact(agent.get("roster_status") or agent.get("context_system_status"), "unknown"),
                "available_for_comms": bool(agent.get("available_for_comms")),
                "authority_scope": "agent_context_system_projection",
                "production_authority": False,
                "live_execution_authority": False,
            }
        )

    blockers = [
        {"blocker_id": f"missing_{key}", "source_path": path, "severity": "warning", "status": "missing_or_not_materialized"}
        for key, path in source_paths.items()
        if not source_present.get(key)
    ]

    return {
        "schema_id": "ion.helixion_joc.comms_projection.v0_1",
        "status": "ready" if not blockers else "degraded",
        "generated_at": utc_now(),
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "write_authority": False,
            "write_authority_policy": "read_only_projection_first_slice",
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
        "source_paths": source_paths,
        "source_present": source_present,
        "channels": channels,
        "threads": threads[:80],
        "messages": messages[:120],
        "participants": participants,
        "pins": [
            {
                "pin_id": "codex_queue_path",
                "label": "Codex work queue",
                "ref_path": source_paths["codex_queue"],
                "truth_class": "ACTIVE_RUNTIME_QUEUE_PROJECTION",
                "authority_scope": "read_only_projection",
                "production_authority": False,
                "live_execution_authority": False,
            }
        ],
        "receipts": receipt_rows,
        "actions": [
            {
                "action_id": "poll_carrier_messages",
                "label": "Poll carrier messages",
                "action_kind": "poll",
                "route_or_tool": "ion_carrier_message_poll",
                "confirmation_required": False,
                "approval_required": False,
                "production_authority": False,
                "live_execution_authority": False,
                "state": "read_only_available_when_tool_mounted",
            },
            {
                "action_id": "send_carrier_message",
                "label": "Send carrier message",
                "action_kind": "send_message",
                "route_or_tool": "ion_carrier_message_send",
                "confirmation_required": True,
                "approval_required": True,
                "production_authority": False,
                "live_execution_authority": False,
                "state": "disabled_in_first_slice",
                "forbidden_when": "first_read_only_projection_slice",
            },
        ],
        "blockers": blockers,
        "summary": {
            "channel_count": len(channels),
            "thread_count": len(threads),
            "message_count": len(messages),
            "participant_count": len(participants),
            "blocker_count": len(blockers),
            "codex_queue_request_count": len(codex_requests),
            "carrier_message_count": len(carrier_items),
        },
        "read_only_projection": True,
        "production_authority": False,
        "live_execution_authority": False,
        "non_claims": [
            "no accepted ION state",
            "no production authority",
            "no live execution authority",
            "no live send, ack, invoke, or queue processing authority",
        ],
    }


def build_branch_gateway_consumer_model(ion_root: str | Path = ".") -> dict[str, Any]:
    root = Path(ion_root).resolve()
    worker_status = _branch_gateway_read(root, branch_id="worker_shift", route_id="status_summary")
    active_workers = _branch_gateway_read(root, branch_id="worker_shift", route_id="active_workers")
    coordination_state = _branch_gateway_read(root, branch_id="worker_shift", route_id="coordination_state")
    service_status = _branch_gateway_read(
        root,
        branch_id="runtime_services",
        route_id="service_status",
        args={"probe_health": False},
    )
    service_ids = _service_ids_from_status(service_status)
    reload_plans = _runtime_service_plan_map(root, service_ids)
    retest_result = _branch_gateway_read(
        root,
        branch_id="runtime_services",
        route_id="retest_service",
        args={"service_id": RUNTIME_SERVICE_RETEST_SERVICE_ID},
    )
    control_rows = _runtime_service_control_rows(root, service_status, reload_plans)
    return {
        "schema_id": "ion.branch_gateway_cockpit_consumers.v0_1",
        "generated_at": utc_now(),
        "worker_shift": {
            "branch": _branch_gateway_describe(root, "worker_shift"),
            "status_summary": worker_status,
            "active_workers": active_workers,
            "coordination_state": coordination_state,
            "mutates_active_state": False,
        },
        "runtime_services": {
            "branch": _branch_gateway_describe(root, "runtime_services"),
            "service_status": service_status,
            "service_reload_plans": reload_plans,
            "retest_service": retest_result,
            "default_retest_service_id": RUNTIME_SERVICE_RETEST_SERVICE_ID,
            "service_controls": control_rows,
            "mutation_gate": {
                "allowed_service_id_required": True,
                "confirmation_required": BRANCH_GATEWAY_CONFIRMATION_TOKEN,
                "idempotency_key_required": True,
                "plan_preview_required": True,
                "post_action_receipt_handoff_required": True,
                "receipt_handoff_dir": repo_rel(root / RUNTIME_SERVICE_RECEIPTS_DIR, root),
                "cockpit_executes_mutation": False,
            },
            "mutates_active_state": False,
        },
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def build_cockpit_view_model(ion_root: str | Path = ".") -> dict[str, Any]:
    root = Path(ion_root).resolve()
    active_files = dict(ACTIVE_FILES)
    active_files["safe_full_project_package"] = latest_safe_package_result_rel(root)
    data = {name: read_json(root / rel) for name, rel in active_files.items()}
    spawn_rows = _spawn_rows(data["spawn"], data["turn"])
    records = _ledger_records(data["ledger"])
    steward_items = _steward_items(data["steward"])
    operator_items = _operator_items(data["operator_queue"])
    gates = _gates(data["human_gates"])
    open_gates = [g for g in gates if str(g.get("status", "open")).lower() not in {"resolved", "closed"}]
    pending_operator = [i for i in operator_items if str(i.get("status", "pending")).lower() in {"pending", "queued"}]
    findings = listify(data["turn"].get("findings")) if isinstance(data["turn"].get("findings"), list) else []
    if isinstance(data["turn"].get("findings"), dict):
        for value in data["turn"].get("findings", {}).values():
            findings.extend(listify(value))
    blocked = bool(open_gates) or bool(data["turn"].get("blocked_by_findings"))
    return_counts = _return_counts(records)
    active_spawn_count = _active_spawn_queue_count(data["turn"], spawn_rows)
    plan_spawn_count = _spawn_count(spawn_rows)
    deferred_spawn_count = _deferred_spawn_count(spawn_rows)
    sandbox_returns = _chatgpt_sandbox_returns_summary(root)
    local_services = build_local_service_status(root)
    service_console = build_service_console_model(root)
    system_diagnostics = build_system_diagnostics_model(root)
    helixion_rebuild = _helixion_joc_rebuild_summary(root)
    chatgpt_browser_mcp = _chatgpt_browser_mcp_summary(root)
    codex_capsule_chat = _codex_capsule_chat_summary(root)
    codex_cli_workbench = build_codex_cli_workbench_model(root)
    codex_conversation_archive = build_codex_conversation_archive(root)
    codex_git_rollback = build_codex_git_rollback_model(root)
    vnext_mission_control = _vnext_mission_control_summary(root)
    extension_micro_shell = _extension_micro_shell_summary(root)
    docs_projects_packages = _docs_projects_packages_summary(root)
    context_package_graph = _context_package_graph_projection(root)
    agent_control_plane = build_agent_control_plane_projection(root)
    joc_comms = build_joc_comms_projection(
        root,
        data,
        operator_items=operator_items,
        steward_items=steward_items,
        task_return_records=records,
        agent_control_plane=agent_control_plane,
        chatgpt_browser_mcp=chatgpt_browser_mcp,
    )
    automation_control_plane = build_automation_control_plane(root)
    branch_gateway_consumers = build_branch_gateway_consumer_model(root)
    worker_shift_summary = _delegated(branch_gateway_consumers.get("worker_shift", {}).get("status_summary", {})).get("worker_shift_summary", {})
    runtime_services_status = _delegated(branch_gateway_consumers.get("runtime_services", {}).get("service_status", {}))
    counts = {
        "spawn_rows": len(spawn_rows),
        "spawn_true": active_spawn_count,
        "plan_spawn_true": plan_spawn_count,
        "deferred_spawn": deferred_spawn_count,
        "returns": return_counts,
        "steward_queue": len(steward_items),
        "operator_queue_pending": len(pending_operator),
        "open_gates": len(open_gates),
    }
    runtime_status = status_from_findings(findings, blocked=blocked)
    runtime_timeline = synthesize_timeline(data, counts, active_files)
    receipt_rows = recent_receipts(root)
    project_cockpit = build_project_cockpit_model(
        root,
        vnext=vnext_mission_control,
        runtime_timeline=runtime_timeline,
        lane_timeline=data["lane_timeline"],
    )
    project_summary = project_cockpit.get("summary") if isinstance(project_cockpit.get("summary"), Mapping) else {}
    joc_comms = _joc_comms_projection(
        root,
        operator_items=operator_items,
        steward_items=steward_items,
        return_records=records,
        agent_control_plane=agent_control_plane,
        chatgpt_browser_mcp=chatgpt_browser_mcp,
        receipts=receipt_rows,
    )

    view_model = {
        "schema_id": "ion.cockpit_view_model.v1",
        "generated_at": utc_now(),
        "runtime": {
            "status": runtime_status,
            "shell_root": str(root),
            "mode": compact(data["turn"].get("carrier") or data["work"].get("carrier"), "cursor"),
            "version": "V90_CURSOR_COCKPIT_LIVE_WEBVIEW_BINDING",
            "blocked": blocked,
            "audit_findings": findings,
        },
        "top_bar": {
            "objective": compact(data["turn"].get("objective") or data["work"].get("objective"), "no active objective"),
            "carrier_status": "blocked" if blocked else "ready",
            "hook_status": compact(data["hook"].get("status"), "unknown"),
            "gate_count": len(open_gates),
            "spawn_count": active_spawn_count,
            "plan_spawn_count": plan_spawn_count,
            "deferred_spawn_count": deferred_spawn_count,
            "spawn_rows_total": len(spawn_rows),
            "execution_bundle_materialized": data["spawn"].get("execution_bundle_materialized"),
            "return_counts": return_counts,
            "steward_queue_count": len(steward_items),
            "operator_queue_pending": len(pending_operator),
            "sandbox_return_count": sandbox_returns.get("return_count", 0),
            "local_service_status": local_services.get("status"),
            "local_service_count": local_services.get("service_count", 0),
            "local_service_missing_template_count": local_services.get("missing_template_count", 0),
            "system_cpu_percent": system_diagnostics.get("summary", {}).get("cpu_percent", 0),
            "system_memory_percent": system_diagnostics.get("summary", {}).get("memory_percent", 0),
            "system_swap_percent": system_diagnostics.get("summary", {}).get("swap_percent", 0),
            "system_listener_count": system_diagnostics.get("summary", {}).get("listener_count", 0),
            "system_cleanup_candidate_count": system_diagnostics.get("summary", {}).get("cleanup_candidate_count", 0),
            "system_stale_port_count": system_diagnostics.get("summary", {}).get("stale_port_count", 0),
            "system_issue_count": system_diagnostics.get("summary", {}).get("issue_count", 0),
            "worker_shift_active_worker_count": worker_shift_summary.get("active_worker_count", 0)
            if isinstance(worker_shift_summary, Mapping)
            else 0,
            "runtime_services_branch_service_count": runtime_services_status.get("service_count", 0)
            if isinstance(runtime_services_status, Mapping)
            else 0,
            "helixion_rebuild_status": helixion_rebuild.get("status"),
            "helixion_rebuild_ready_for_phase_1": helixion_rebuild.get("ready_for_phase_1"),
            "vnext_status": vnext_mission_control.get("status"),
            "vnext_current_packet": vnext_mission_control.get("current_packet", {}).get("token")
            if isinstance(vnext_mission_control.get("current_packet"), Mapping)
            else None,
            "vnext_open_gate_count": vnext_mission_control.get("gate_summary", {}).get("open", 0)
            if isinstance(vnext_mission_control.get("gate_summary"), Mapping)
            else 0,
            "vnext_packet_count": len(vnext_mission_control.get("packets", [])),
            "project_cockpit_status": project_cockpit.get("status"),
            "project_count": project_summary.get("project_count", 0),
            "project_mission_count": project_summary.get("mission_count", 0),
            "project_open_blocker_count": project_summary.get("open_blocker_count", 0),
            "project_open_question_count": project_summary.get("open_question_count", 0),
            "browser_carrier_message_count": chatgpt_browser_mcp.get("carrier_message_count", 0),
            "codex_work_request_count": chatgpt_browser_mcp.get("codex_work_request_count", 0),
            "action_gateway_tool_count": chatgpt_browser_mcp.get("tool_count", 0),
            "action_gateway_transport_state": chatgpt_browser_mcp.get("transport_state"),
            "codex_capsule_chat_verdict": codex_capsule_chat.get("verdict"),
            "codex_capsule_chat_turn_count": codex_capsule_chat.get("conversation_summary", {}).get("turn_count", 0),
            "codex_capsule_chat_response_run_count": codex_capsule_chat.get("response_run_count", 0),
            "codex_cli_workbench_verdict": codex_cli_workbench.get("verdict"),
            "codex_cli_workbench_tool_count": codex_cli_workbench.get("summary", {}).get("mcp_read_only_tool_count", 0),
            "codex_cli_workbench_hook_group_count": codex_cli_workbench.get("summary", {}).get("hook_group_count", 0),
            "codex_conversation_session_count": codex_conversation_archive.get("source_counts", {}).get("session_files_total", 0),
            "codex_git_rollback_checkpoint_count": codex_git_rollback.get("summary", {}).get("checkpoint_count", 0),
            "codex_git_rollback_ready_count": codex_git_rollback.get("summary", {}).get("rollback_ready_count", 0),
            "extension_version": extension_micro_shell.get("manifest", {}).get("version"),
            "extension_panel_count": len(extension_micro_shell.get("agent_lane_contract", {}).get("panel_surfaces", [])),
            "page_perception_domain_count": extension_micro_shell.get("page_perception", {}).get("domain_count", 0),
            "browser_gpt_dom_status": extension_micro_shell.get("browser_gpt_dom", {}).get("status")
            if isinstance(extension_micro_shell.get("browser_gpt_dom"), Mapping)
            else None,
            "context_package_count": docs_projects_packages.get("context_packages", {}).get("package_count", 0),
            "branch_context_package_count": context_package_graph.get("branch_count", 0),
            "branch_context_package_ready_count": context_package_graph.get("candidate_review_ready_count", 0),
            "context_package_graph_status": context_package_graph.get("status"),
            "artifact_package_count": docs_projects_packages.get("artifact_packages", {}).get("zip_count_visible", 0),
            "agent_control_plane_agent_count": agent_control_plane.get("summary", {}).get("agent_count", 0)
            if isinstance(agent_control_plane.get("summary"), Mapping)
            else 0,
            "agent_control_plane_domain_count": agent_control_plane.get("summary", {}).get("domain_count", 0)
            if isinstance(agent_control_plane.get("summary"), Mapping)
            else 0,
            "agent_control_plane_active": agent_control_plane.get("summary", {}).get("active_process_running", False)
            if isinstance(agent_control_plane.get("summary"), Mapping)
            else False,
            "joc_comms_channel_count": joc_comms.get("summary", {}).get("channel_count", 0)
            if isinstance(joc_comms.get("summary"), Mapping)
            else 0,
            "joc_comms_message_count": joc_comms.get("summary", {}).get("message_count", 0)
            if isinstance(joc_comms.get("summary"), Mapping)
            else 0,
            "joc_comms_blocker_count": joc_comms.get("summary", {}).get("blocker_count", 0)
            if isinstance(joc_comms.get("summary"), Mapping)
            else 0,
            "automation_action_count": automation_control_plane.get("summary", {}).get("action_count", 0)
            if isinstance(automation_control_plane.get("summary"), Mapping)
            else 0,
        },
        "joc_comms": joc_comms,
        "queues": {
            "operator_messages": operator_items,
            "carrier_messages": _carrier_message_items(data["carrier_messages"]),
            "human_gates": gates,
            "steward_integration": steward_items,
        },
        "agents": summarize_agents(spawn_rows, records),
        "timeline": runtime_timeline,
        "front_door_proof_trace": data["front_door_proof_trace"],
        "lane_timeline": data["lane_timeline"],
        "receipt_hydration": data["receipt_hydration"],
        "runtime_debug_overlay": data["runtime_debug_overlay"],
        "safe_full_project_package": data["safe_full_project_package"],
        "v72_mcp_donor_reconciliation": data["v72_mcp_donor_reconciliation"],
        "chatgpt_browser_mcp": chatgpt_browser_mcp,
        "codex_capsule_chat": codex_capsule_chat,
        "codex_cli_workbench": codex_cli_workbench,
        "codex_conversation_archive": codex_conversation_archive,
        "codex_git_rollback": codex_git_rollback,
        "vnext_mission_control": vnext_mission_control,
        "project_cockpit": project_cockpit,
        "extension_micro_shell": extension_micro_shell,
        "docs_projects_packages": docs_projects_packages,
        "context_package_graph": context_package_graph,
        "agent_control_plane": agent_control_plane,
        "automation_control_plane": automation_control_plane,
        "chatgpt_sandbox_returns": sandbox_returns,
        "local_services": local_services,
        "service_console": service_console,
        "system_diagnostics": system_diagnostics,
        "branch_gateway_consumers": branch_gateway_consumers,
        "helixion_joc_rebuild": helixion_rebuild,
        "receipts": receipt_rows,
        "authority_classes": [
            "ACTIVE_RUNTIME_AUTHORITY",
            "ACCEPTED_TASK_RETURN",
            "PENDING_TASK_RETURN",
            "REJECTED_TASK_RETURN",
            "HUMAN_GATE_REQUIRED",
            "LEGACY_CONTEXT_WITNESS",
            "DONOR_REFERENCE",
            "FORBIDDEN_CAPABILITY",
            "JOC_REBUILD_PLAN",
            "PAGE_BRANCH_PROVISIONAL",
            "WISDOMNET_CANDIDATE",
            "VNEXT_MISSION_CONTROL",
            "MIRROR_ONLY",
        ],
        "source_paths": {name: str(rel) for name, rel in active_files.items()},
    }
    return view_model


def build_cockpit_surface_view_model(ion_root: str | Path = ".", *, surface: str = "codex") -> dict[str, Any]:
    """Build a small cockpit shell model for heavy hash-page surfaces.

    The full cockpit model intentionally aggregates every major ION projection,
    which is useful for mission-control pages but too slow as the first payload
    for chat-focused surfaces. This keeps the shell contract intact while only
    hydrating the Codex and BrowserGPT data those pages need immediately.
    """
    root = Path(ion_root).resolve()
    is_codex_surface = surface == "codex"
    is_browser_gpt_surface = surface == "browser-gpt"
    hydrate_codex_context = is_codex_surface or is_browser_gpt_surface
    is_weave_surface = surface == "weave"
    active_files = dict(ACTIVE_FILES)
    active_files["safe_full_project_package"] = latest_safe_package_result_rel(root)
    data = {name: read_json(root / rel) for name, rel in active_files.items()}
    findings = listify(data["turn"].get("findings")) if isinstance(data["turn"].get("findings"), list) else []
    if isinstance(data["turn"].get("findings"), dict):
        for value in data["turn"].get("findings", {}).values():
            findings.extend(listify(value))
    gates = _gates(data["human_gates"])
    open_gates = [g for g in gates if str(g.get("status", "open")).lower() not in {"resolved", "closed"}]
    blocked = bool(open_gates) or bool(data["turn"].get("blocked_by_findings"))
    runtime_status = status_from_findings(findings, blocked=blocked)
    runtime_timeline = synthesize_timeline(
        data,
        {
            "spawn_rows": 0,
            "returns": {"accepted": 0, "rejected": 0},
            "steward_queue": 0,
            "operator_queue_pending": 0,
            "open_gates": len(open_gates),
        },
        active_files,
    )
    if surface == "build":
        top_bar = {
            "objective": "Build workbench",
            "carrier_status": "blocked" if blocked else "ready",
            "hook_status": compact(data["hook"].get("status"), "unknown"),
            "gate_count": len(open_gates),
            "spawn_count": 0,
            "plan_spawn_count": 0,
            "deferred_spawn_count": 0,
            "spawn_rows_total": 0,
            "execution_bundle_materialized": False,
            "return_counts": {},
            "steward_queue_count": 0,
            "operator_queue_pending": 0,
            "sandbox_return_count": 0,
            "local_service_status": "deferred",
            "local_service_count": 0,
            "local_service_missing_template_count": 0,
            "system_cpu_percent": 0,
            "system_memory_percent": 0,
            "system_swap_percent": 0,
            "system_listener_count": 0,
            "system_cleanup_candidate_count": 0,
            "system_stale_port_count": 0,
            "system_issue_count": 0,
            "worker_shift_active_worker_count": 0,
            "runtime_services_branch_service_count": 0,
            "helixion_rebuild_status": "deferred",
            "helixion_rebuild_ready_for_phase_1": False,
            "vnext_status": "deferred",
            "vnext_current_packet": "NA",
            "vnext_open_gate_count": 0,
            "vnext_packet_count": 0,
            "project_cockpit_status": "deferred",
            "project_count": 0,
            "project_mission_count": 0,
            "project_open_blocker_count": 0,
            "project_open_question_count": 0,
            "browser_carrier_message_count": 0,
            "codex_work_request_count": 0,
            "action_gateway_tool_count": 0,
            "action_gateway_transport_state": "deferred",
            "codex_capsule_chat_verdict": "deferred",
            "codex_capsule_chat_turn_count": 0,
            "codex_capsule_chat_response_run_count": 0,
            "codex_cli_workbench_verdict": "deferred",
            "codex_cli_workbench_tool_count": 0,
            "codex_cli_workbench_hook_group_count": 0,
            "codex_conversation_session_count": 0,
            "codex_git_rollback_checkpoint_count": 0,
            "codex_git_rollback_ready_count": 0,
            "extension_version": None,
            "extension_panel_count": 0,
            "page_perception_domain_count": 0,
            "browser_gpt_dom_status": "deferred",
            "context_package_count": 0,
            "branch_context_package_count": 0,
            "branch_context_package_ready_count": 0,
            "context_package_graph_status": "deferred",
            "artifact_package_count": 0,
            "agent_control_plane_agent_count": 0,
            "agent_control_plane_domain_count": 0,
            "agent_control_plane_active": False,
            "joc_comms_channel_count": 0,
            "joc_comms_message_count": 0,
            "joc_comms_blocker_count": 0,
            "automation_action_count": 0,
        }
        return {
            "schema_id": "ion.cockpit_surface_view_model.v1",
            "surface": surface,
            "generated_at": utc_now(),
            "runtime": {
                "status": runtime_status,
                "shell_root": str(root),
                "mode": compact(data["turn"].get("carrier") or data["work"].get("carrier"), "cursor"),
                "version": "V91_SURFACE_BOOT_BUILD_FAST",
                "blocked": blocked,
                "audit_findings": findings,
            },
            "top_bar": top_bar,
            "joc_comms": {"schema_id": "ion.joc_comms_projection.v1", "summary": {}, "channels": [], "messages": []},
            "queues": {"operator_messages": [], "carrier_messages": [], "human_gates": gates, "steward_integration": []},
            "agents": [],
            "timeline": runtime_timeline[:20],
            "front_door_proof_trace": data["front_door_proof_trace"],
            "lane_timeline": data["lane_timeline"],
            "receipt_hydration": data["receipt_hydration"],
            "runtime_debug_overlay": data["runtime_debug_overlay"],
            "safe_full_project_package": {},
            "v72_mcp_donor_reconciliation": data["v72_mcp_donor_reconciliation"],
            "chatgpt_browser_mcp": {"schema_id": "ion.chatgpt_browser_mcp_summary.v1", "status": "deferred"},
            "codex_capsule_chat": {"schema_id": "ion.codex_capsule_chat_cockpit_summary.v1", "verdict": "deferred", "conversation_summary": {"turn_count": 0}, "response_run_count": 0},
            "codex_cli_workbench": {},
            "codex_conversation_archive": {"schema_id": "ion.codex_conversation_archive.v1", "sessions": [], "source_counts": {"session_files_total": 0}},
            "codex_git_rollback": {"schema_id": "ion.codex_git_rollback.v1", "checkpoints": [], "summary": {}},
            "vnext_mission_control": {"schema_id": "ion.vnext_mission_control_projection.v1", "status": "missing", "packets": [], "gate_summary": {}},
            "project_cockpit": {"schema_id": "ion.project_cockpit.v1", "status": "deferred", "summary": {}},
            "extension_micro_shell": {"schema_id": "ion.extension_micro_shell_summary.v1", "status": "deferred"},
            "docs_projects_packages": {"schema_id": "ion.docs_projects_packages_cockpit_summary.v1", "status": "deferred", "context_packages": {}, "artifact_packages": {}},
            "context_package_graph": {"schema_id": "ion.context_package_graph.v1", "status": "deferred", "branch_count": 0},
            "agent_control_plane": {"schema_id": "ion.agent_control_plane_projection.v1", "summary": {}, "agents": [], "communications": {}},
            "automation_control_plane": {"schema_id": "ion.automation_control_plane.v1", "summary": {}, "actions": []},
            "chatgpt_sandbox_returns": {"schema_id": "ion.chatgpt_sandbox_returns_summary.v1", "return_count": 0},
            "local_services": {"schema_id": "ion.local_service_status.v1", "status": "deferred", "service_count": 0},
            "service_console": {"schema_id": "ion.cockpit_service_console.v1", "status": "deferred"},
            "system_diagnostics": {"schema_id": "ion.system_diagnostics.v1", "status": "deferred", "summary": {}},
            "branch_gateway_consumers": {"schema_id": "ion.branch_gateway_consumers.v1", "status": "deferred"},
            "helixion_joc_rebuild": {"schema_id": "ion.helixion_joc_rebuild_summary.v1", "status": "deferred"},
            "receipts": [],
            "authority_classes": [
                "ACTIVE_RUNTIME_AUTHORITY",
                "CANDIDATE_CONTEXT",
                "LOCAL_COCKPIT_PROJECTION",
                "NO_PRODUCTION_AUTHORITY",
                "NO_LIVE_EXECUTION_AUTHORITY",
            ],
            "source_paths": {name: str(rel) for name, rel in active_files.items()},
        }
    if surface == "projects":
        project_cockpit = build_project_cockpit_model(root, runtime_timeline=runtime_timeline, lane_timeline=data["lane_timeline"])
        project_summary = project_cockpit.get("summary") if isinstance(project_cockpit.get("summary"), Mapping) else {}
        top_bar = {
            "objective": compact(data["turn"].get("objective") or data["work"].get("objective"), "projects surface boot"),
            "carrier_status": "blocked" if blocked else "ready",
            "hook_status": compact(data["hook"].get("status"), "unknown"),
            "gate_count": len(open_gates),
            "spawn_count": 0,
            "plan_spawn_count": 0,
            "deferred_spawn_count": 0,
            "spawn_rows_total": 0,
            "execution_bundle_materialized": False,
            "return_counts": {},
            "steward_queue_count": 0,
            "operator_queue_pending": 0,
            "sandbox_return_count": 0,
            "local_service_status": "deferred",
            "local_service_count": 0,
            "local_service_missing_template_count": 0,
            "system_cpu_percent": 0,
            "system_memory_percent": 0,
            "system_swap_percent": 0,
            "system_listener_count": 0,
            "system_cleanup_candidate_count": 0,
            "system_stale_port_count": 0,
            "system_issue_count": 0,
            "worker_shift_active_worker_count": 0,
            "runtime_services_branch_service_count": 0,
            "helixion_rebuild_status": "deferred",
            "helixion_rebuild_ready_for_phase_1": False,
            "vnext_status": "deferred",
            "vnext_current_packet": "NA",
            "vnext_open_gate_count": 0,
            "vnext_packet_count": 0,
            "project_cockpit_status": project_cockpit.get("status"),
            "project_count": project_summary.get("project_count", 0),
            "project_mission_count": project_summary.get("mission_count", 0),
            "project_open_blocker_count": project_summary.get("open_blocker_count", 0),
            "project_open_question_count": project_summary.get("open_question_count", 0),
            "browser_carrier_message_count": 0,
            "codex_work_request_count": 0,
            "action_gateway_tool_count": 0,
            "action_gateway_transport_state": "deferred",
            "codex_capsule_chat_verdict": "deferred",
            "codex_capsule_chat_turn_count": 0,
            "codex_capsule_chat_response_run_count": 0,
            "codex_cli_workbench_verdict": "deferred",
            "codex_cli_workbench_tool_count": 0,
            "codex_cli_workbench_hook_group_count": 0,
            "codex_conversation_session_count": 0,
            "codex_git_rollback_checkpoint_count": 0,
            "codex_git_rollback_ready_count": 0,
            "extension_version": None,
            "extension_panel_count": 0,
            "page_perception_domain_count": 0,
            "browser_gpt_dom_status": "deferred",
            "context_package_count": 0,
            "branch_context_package_count": 0,
            "branch_context_package_ready_count": 0,
            "context_package_graph_status": "deferred",
            "artifact_package_count": 0,
            "agent_control_plane_agent_count": 0,
            "agent_control_plane_domain_count": 0,
            "agent_control_plane_active": False,
            "joc_comms_channel_count": 0,
            "joc_comms_message_count": 0,
            "joc_comms_blocker_count": 0,
            "automation_action_count": 0,
        }
        return {
            "schema_id": "ion.cockpit_surface_view_model.v1",
            "surface": surface,
            "generated_at": utc_now(),
            "runtime": {
                "status": runtime_status,
                "shell_root": str(root),
                "mode": compact(data["turn"].get("carrier") or data["work"].get("carrier"), "cursor"),
                "version": "V90_SURFACE_BOOT_PROJECTS_FAST",
                "blocked": blocked,
                "audit_findings": findings,
            },
            "top_bar": top_bar,
            "joc_comms": {"schema_id": "ion.joc_comms_projection.v1", "summary": {}, "channels": [], "messages": []},
            "queues": {"operator_messages": [], "carrier_messages": [], "human_gates": gates, "steward_integration": []},
            "agents": [],
            "timeline": runtime_timeline,
            "front_door_proof_trace": data["front_door_proof_trace"],
            "lane_timeline": data["lane_timeline"],
            "receipt_hydration": data["receipt_hydration"],
            "runtime_debug_overlay": data["runtime_debug_overlay"],
            "safe_full_project_package": {},
            "v72_mcp_donor_reconciliation": data["v72_mcp_donor_reconciliation"],
            "chatgpt_browser_mcp": {"schema_id": "ion.chatgpt_browser_mcp_summary.v1", "status": "deferred"},
            "codex_capsule_chat": {"schema_id": "ion.codex_capsule_chat_cockpit_summary.v1", "verdict": "deferred", "conversation_summary": {"turn_count": 0}, "response_run_count": 0},
            "codex_cli_workbench": {},
            "codex_conversation_archive": {"schema_id": "ion.codex_conversation_archive.v1", "sessions": [], "source_counts": {"session_files_total": 0}},
            "codex_git_rollback": {"schema_id": "ion.codex_git_rollback.v1", "checkpoints": [], "summary": {}},
            "vnext_mission_control": {"schema_id": "ion.vnext_mission_control_projection.v1", "status": "missing", "packets": [], "gate_summary": {}},
            "project_cockpit": project_cockpit,
            "extension_micro_shell": {"schema_id": "ion.extension_micro_shell_summary.v1", "status": "deferred"},
            "docs_projects_packages": {"schema_id": "ion.docs_projects_packages_cockpit_summary.v1", "status": "deferred", "context_packages": {}, "artifact_packages": {}},
            "context_package_graph": {"schema_id": "ion.context_package_graph.v1", "status": "deferred", "branch_count": 0},
            "agent_control_plane": {"schema_id": "ion.agent_control_plane_projection.v1", "summary": {}, "agents": [], "communications": {}},
            "automation_control_plane": {"schema_id": "ion.automation_control_plane.v1", "summary": {}, "actions": []},
            "chatgpt_sandbox_returns": {"schema_id": "ion.chatgpt_sandbox_returns_summary.v1", "return_count": 0},
            "local_services": {"schema_id": "ion.local_service_status.v1", "status": "deferred", "service_count": 0},
            "service_console": {"schema_id": "ion.cockpit_service_console.v1", "status": "deferred"},
            "system_diagnostics": {"schema_id": "ion.system_diagnostics.v1", "status": "deferred", "summary": {}},
            "branch_gateway_consumers": {"schema_id": "ion.branch_gateway_consumers.v1", "status": "deferred"},
            "helixion_joc_rebuild": {"schema_id": "ion.helixion_joc_rebuild_summary.v1", "status": "deferred"},
            "receipts": [],
            "authority_classes": [
                "ACTIVE_RUNTIME_AUTHORITY",
                "CANDIDATE_CONTEXT",
                "LOCAL_COCKPIT_PROJECTION",
                "NO_PRODUCTION_AUTHORITY",
                "NO_LIVE_EXECUTION_AUTHORITY",
            ],
        }
    local_services = build_local_service_status(root)
    service_console = build_service_console_model(root)
    system_diagnostics = build_system_diagnostics_model(root)
    chatgpt_browser_mcp = _chatgpt_browser_mcp_summary(root)
    extension_micro_shell = _extension_micro_shell_summary(root)
    codex_capsule_chat = (
        _codex_capsule_chat_summary(root)
        if hydrate_codex_context
        else {
            "schema_id": "ion.codex_capsule_chat_cockpit_summary.v1",
            "verdict": "deferred",
            "conversation_summary": {"turn_count": 0},
            "response_run_count": 0,
        }
    )
    context_package_graph = _context_package_graph_projection(root)
    codex_cli_workbench = build_codex_cli_workbench_model(root) if hydrate_codex_context else {}
    codex_conversation_archive = (
        build_codex_conversation_archive(root)
        if hydrate_codex_context
        else {"schema_id": "ion.codex_conversation_archive.v1", "sessions": [], "source_counts": {"session_files_total": 0}}
    )
    codex_git_rollback = _deferred_codex_git_rollback_model() if is_codex_surface else {"schema_id": "ion.codex_git_rollback.v1", "checkpoints": [], "summary": {}}
    project_cockpit = (
        build_project_cockpit_model(root, runtime_timeline=runtime_timeline, lane_timeline=data["lane_timeline"])
        if surface == "projects"
        else {"schema_id": "ion.project_cockpit.v1", "status": "missing", "summary": {}}
    )
    project_summary = project_cockpit.get("summary") if isinstance(project_cockpit.get("summary"), Mapping) else {}
    agent_control_plane = (
        _codex_surface_agent_control_plane(root)
        if is_codex_surface or is_browser_gpt_surface
        else _domain_weaver_surface_agent_control_plane(root)
        if is_weave_surface
        else {"schema_id": "ion.agent_control_plane_projection.v1", "summary": {}, "agents": [], "communications": {}}
    )
    agent_control_summary = agent_control_plane.get("summary") if isinstance(agent_control_plane.get("summary"), Mapping) else {}
    receipt_rows = recent_receipts(root)
    top_bar = {
        "objective": compact(data["turn"].get("objective") or data["work"].get("objective"), "surface boot"),
        "carrier_status": "blocked" if blocked else "ready",
        "hook_status": compact(data["hook"].get("status"), "unknown"),
        "gate_count": len(open_gates),
        "spawn_count": 0,
        "plan_spawn_count": 0,
        "deferred_spawn_count": 0,
        "spawn_rows_total": 0,
        "execution_bundle_materialized": False,
        "return_counts": {},
        "steward_queue_count": 0,
        "operator_queue_pending": 0,
        "sandbox_return_count": 0,
        "local_service_status": local_services.get("status"),
        "local_service_count": local_services.get("service_count", 0),
        "local_service_missing_template_count": local_services.get("missing_template_count", 0),
        "system_cpu_percent": system_diagnostics.get("summary", {}).get("cpu_percent", 0),
        "system_memory_percent": system_diagnostics.get("summary", {}).get("memory_percent", 0),
        "system_swap_percent": system_diagnostics.get("summary", {}).get("swap_percent", 0),
        "system_listener_count": system_diagnostics.get("summary", {}).get("listener_count", 0),
        "system_cleanup_candidate_count": system_diagnostics.get("summary", {}).get("cleanup_candidate_count", 0),
        "system_stale_port_count": system_diagnostics.get("summary", {}).get("stale_port_count", 0),
        "system_issue_count": system_diagnostics.get("summary", {}).get("issue_count", 0),
        "worker_shift_active_worker_count": 0,
        "runtime_services_branch_service_count": 0,
        "helixion_rebuild_status": "deferred",
        "helixion_rebuild_ready_for_phase_1": False,
        "vnext_status": "deferred",
        "vnext_current_packet": "NA",
        "vnext_open_gate_count": 0,
        "vnext_packet_count": 0,
        "project_cockpit_status": project_cockpit.get("status") if surface == "projects" else "deferred",
        "project_count": project_summary.get("project_count", 0),
        "project_mission_count": project_summary.get("mission_count", 0),
        "project_open_blocker_count": project_summary.get("open_blocker_count", 0),
        "project_open_question_count": project_summary.get("open_question_count", 0),
        "browser_carrier_message_count": chatgpt_browser_mcp.get("carrier_message_count", 0),
        "codex_work_request_count": chatgpt_browser_mcp.get("codex_work_request_count", 0),
        "action_gateway_tool_count": chatgpt_browser_mcp.get("tool_count", 0),
        "action_gateway_transport_state": chatgpt_browser_mcp.get("transport_state"),
        "codex_capsule_chat_verdict": codex_capsule_chat.get("verdict"),
        "codex_capsule_chat_turn_count": codex_capsule_chat.get("conversation_summary", {}).get("turn_count", 0),
        "codex_capsule_chat_response_run_count": codex_capsule_chat.get("response_run_count", 0),
        "codex_cli_workbench_verdict": codex_cli_workbench.get("verdict"),
        "codex_cli_workbench_tool_count": codex_cli_workbench.get("summary", {}).get("mcp_read_only_tool_count", 0)
        if isinstance(codex_cli_workbench.get("summary"), Mapping)
        else 0,
        "codex_cli_workbench_hook_group_count": codex_cli_workbench.get("summary", {}).get("hook_group_count", 0)
        if isinstance(codex_cli_workbench.get("summary"), Mapping)
        else 0,
        "codex_conversation_session_count": codex_conversation_archive.get("source_counts", {}).get("session_files_total", 0)
        if isinstance(codex_conversation_archive.get("source_counts"), Mapping)
        else 0,
        "codex_git_rollback_checkpoint_count": codex_git_rollback.get("summary", {}).get("checkpoint_count", 0)
        if isinstance(codex_git_rollback.get("summary"), Mapping)
        else 0,
        "codex_git_rollback_ready_count": codex_git_rollback.get("summary", {}).get("rollback_ready_count", 0)
        if isinstance(codex_git_rollback.get("summary"), Mapping)
        else 0,
        "extension_version": extension_micro_shell.get("manifest", {}).get("version")
        if isinstance(extension_micro_shell.get("manifest"), Mapping)
        else None,
        "extension_panel_count": len(extension_micro_shell.get("agent_lane_contract", {}).get("panel_surfaces", []))
        if isinstance(extension_micro_shell.get("agent_lane_contract"), Mapping)
        else 0,
        "page_perception_domain_count": extension_micro_shell.get("page_perception", {}).get("domain_count", 0)
        if isinstance(extension_micro_shell.get("page_perception"), Mapping)
        else 0,
        "browser_gpt_dom_status": extension_micro_shell.get("browser_gpt_dom", {}).get("status")
        if isinstance(extension_micro_shell.get("browser_gpt_dom"), Mapping)
        else None,
        "context_package_count": context_package_graph.get("branch_count", 0),
        "branch_context_package_count": context_package_graph.get("branch_count", 0),
        "branch_context_package_ready_count": context_package_graph.get("candidate_review_ready_count", 0),
        "context_package_graph_status": context_package_graph.get("status"),
        "artifact_package_count": 0,
        "agent_control_plane_agent_count": agent_control_summary.get("agent_count", 0),
        "agent_control_plane_domain_count": agent_control_summary.get("domain_count", 0),
        "agent_control_plane_active": agent_control_summary.get("active_process_running", False),
        "joc_comms_channel_count": 0,
        "joc_comms_message_count": 0,
        "joc_comms_blocker_count": 0,
        "automation_action_count": 0,
    }
    return {
        "schema_id": "ion.cockpit_surface_view_model.v1",
        "surface": surface,
        "generated_at": utc_now(),
        "runtime": {
            "status": runtime_status,
            "shell_root": str(root),
            "mode": compact(data["turn"].get("carrier") or data["work"].get("carrier"), "cursor"),
            "version": f"V90_SURFACE_BOOT_{surface.upper().replace('-', '_')}",
            "blocked": blocked,
            "audit_findings": findings,
        },
        "top_bar": top_bar,
        "joc_comms": {"schema_id": "ion.joc_comms_projection.v1", "summary": {}, "channels": [], "messages": []},
        "queues": {"operator_messages": [], "carrier_messages": [], "human_gates": gates, "steward_integration": []},
        "agents": [],
        "timeline": runtime_timeline,
        "front_door_proof_trace": data["front_door_proof_trace"],
        "lane_timeline": data["lane_timeline"],
        "receipt_hydration": data["receipt_hydration"],
        "runtime_debug_overlay": data["runtime_debug_overlay"],
        "safe_full_project_package": {},
        "v72_mcp_donor_reconciliation": data["v72_mcp_donor_reconciliation"],
        "chatgpt_browser_mcp": chatgpt_browser_mcp,
        "codex_capsule_chat": codex_capsule_chat,
        "codex_cli_workbench": codex_cli_workbench,
        "codex_conversation_archive": codex_conversation_archive,
        "codex_git_rollback": codex_git_rollback,
        "vnext_mission_control": {"schema_id": "ion.vnext_mission_control_projection.v1", "status": "missing", "packets": [], "gate_summary": {}},
        "project_cockpit": project_cockpit,
        "extension_micro_shell": extension_micro_shell,
        "docs_projects_packages": {"schema_id": "ion.docs_projects_packages_cockpit_summary.v1", "status": "deferred", "context_packages": {}, "artifact_packages": {}},
        "context_package_graph": context_package_graph,
        "agent_control_plane": agent_control_plane,
        "automation_control_plane": {"schema_id": "ion.automation_control_plane.v1", "summary": {}, "actions": []},
        "chatgpt_sandbox_returns": {"schema_id": "ion.chatgpt_sandbox_returns_summary.v1", "return_count": 0},
        "local_services": local_services,
        "service_console": service_console,
        "system_diagnostics": system_diagnostics,
        "branch_gateway_consumers": {"schema_id": "ion.branch_gateway_consumers.v1", "status": "deferred"},
        "helixion_joc_rebuild": {"schema_id": "ion.helixion_joc_rebuild_summary.v1", "status": "deferred"},
        "receipts": receipt_rows,
        "authority_classes": [
            "ACTIVE_RUNTIME_AUTHORITY",
            "HUMAN_GATE_REQUIRED",
            "MIRROR_ONLY",
            "FORBIDDEN_CAPABILITY",
        ],
        "source_paths": {name: str(rel) for name, rel in active_files.items()},
    }


def write_cockpit_view_model(ion_root: str | Path = ".", output: str | Path | None = None) -> dict[str, Any]:
    root = Path(ion_root).resolve()
    model = build_cockpit_view_model(root)
    out = root / (Path(output) if output else OUTPUT)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(model, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return model


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the ION/JOC cockpit runtime view model.")
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--write", action="store_true", help="Write ACTIVE_COCKPIT_VIEW_MODEL.json")
    parser.add_argument("--output", default=None, help="Optional output path relative to ion-root")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    model = write_cockpit_view_model(args.ion_root, args.output) if args.write else build_cockpit_view_model(args.ion_root)
    result = {"status": "ION_COCKPIT_VIEW_MODEL_READY", "view_model": model}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["status"])
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
