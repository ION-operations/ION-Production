"""ChatGPT Browser carrier operating card.

This is a read-only membrane card for Browser GPT / ION dev. It summarizes the
current local control-plane posture and points Browser GPT to the next lawful
Branch Gateway routes without granting production, live execution, secrets, git
push, deletion, materialization, or accepted-state authority.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_worker_shift_presence import summarize_shift_board

SCHEMA_ID = "ion.chatgpt_browser_carrier_operating_card.v0_1"

AUTHORITY_FALSE = {
    "accepted_state_claim": False,
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "git_push_authority": False,
    "deletion_authority": False,
}

CURRENT = Path("ION/05_context/current")
CODEX_SOLO = CURRENT / "codex_solo"
CHATGPT_CONNECTOR = CURRENT / "chatgpt_connector"
WORKER_SHIFT_BOARD = CURRENT / "worker_shift/ACTIVE_WORKER_SHIFT_BOARD.json"
CODEX_QUEUE = CURRENT / "ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json"
CODEX_QUEUE_STATE = CURRENT / "chatgpt_connector/runtime/codex_queue_runner_state.json"
DOMAIN_WEAVER_PROJECTION = CURRENT / "domain_weaver/DOMAIN_WEAVER_PROJECTION.json"
CODEX_LIVE_SESSIONS = CURRENT / "chatgpt_connector/codex_live_sessions"
CODEX_SESSION_RUNS = CURRENT / "chatgpt_connector/codex_session_store_runs"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_root(root: str | Path | None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").is_file() and (path / "ION/REPO_AUTHORITY.md").is_file():
            return path
    return candidate


def _rel(root: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _read_json(root: Path, rel_path: Path) -> dict[str, Any]:
    path = root / rel_path
    try:
        if not path.is_file():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_read_error": str(exc), "_path": _rel(root, path)}


def _path_status(root: Path, rel_path: Path) -> dict[str, Any]:
    path = root / rel_path
    return {"path": _rel(root, path), "exists": path.is_file() or path.is_dir()}


def _queue_card(root: Path) -> dict[str, Any]:
    queue = _read_json(root, CODEX_QUEUE)
    requests = queue.get("requests") if isinstance(queue.get("requests"), list) else []
    status_counts: dict[str, int] = {}
    for request in requests:
        if not isinstance(request, Mapping):
            continue
        status = str(request.get("status") or "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    state = _read_json(root, CODEX_QUEUE_STATE)
    active_run = state.get("active_run") if isinstance(state.get("active_run"), Mapping) else {}
    active_process_running = bool(active_run)
    return {
        "queue_path": _rel(root, root / CODEX_QUEUE),
        "state_path": _rel(root, root / CODEX_QUEUE_STATE),
        "queue_observed": bool(queue),
        "active_process_running": active_process_running,
        "active_run_id": active_run.get("run_id"),
        "active_run_count": 1 if active_process_running else 0,
        "queued_request_count": status_counts.get("QUEUED_FOR_CODEX_CARRIER", 0),
        "in_flight_count": status_counts.get("CLAIMED_BY_CODEX_QUEUE_RUNNER", 0),
        "request_count": int(queue.get("request_count") or len(requests) or 0),
        "status_counts": status_counts,
    }


def _domain_weaver_card(root: Path) -> dict[str, Any]:
    projection = _read_json(root, DOMAIN_WEAVER_PROJECTION)
    summary = projection.get("summary") if isinstance(projection.get("summary"), Mapping) else {}
    return {
        "projection_path": _rel(root, root / DOMAIN_WEAVER_PROJECTION),
        "projection_available": bool(projection),
        "weave_status": projection.get("weave_status") or summary.get("weave_status") or summary.get("status"),
        "domain_count": projection.get("domain_count") or summary.get("domain_count") or len(projection.get("domains") or []),
        "agent_count": projection.get("agent_count") or summary.get("agent_count") or len(projection.get("agents") or []),
        "available_agent_comms_count": projection.get("available_agent_comms_count")
        or summary.get("available_agent_comms_count"),
        "edge_count": projection.get("edge_count") or summary.get("edge_count"),
        "queue_request_count": projection.get("queue_request_count") or summary.get("queue_request_count"),
        "gap_count": projection.get("gap_count") or summary.get("gap_count"),
        "live_return_complete": projection.get("live_return_complete") or summary.get("live_return_complete"),
        "full_domain_weaver_ready": bool(projection.get("full_domain_weaver_ready") or summary.get("full_domain_weaver_ready")),
        "self_evolution_ready": bool(projection.get("self_evolution_ready") or summary.get("self_evolution_ready")),
        "ui_development_ready": bool(projection.get("ui_development_ready") or summary.get("ui_development_ready")),
        "source_of_truth_classification": "candidate_projection",
        "authority": dict(AUTHORITY_FALSE),
    }


def _live_session_card(root: Path) -> dict[str, Any]:
    index = _read_json(root, CODEX_LIVE_SESSIONS / "INDEX.json")
    sessions = index.get("sessions") if isinstance(index.get("sessions"), list) else []
    return {
        "index_path": _rel(root, root / CODEX_LIVE_SESSIONS / "INDEX.json"),
        "registered_session_count": len(sessions),
        "registered_sessions": [
            {
                "session_id": item.get("session_id"),
                "display_name": item.get("display_name"),
                "domain_id": item.get("domain_id"),
                "status": item.get("status"),
            }
            for item in sessions
            if isinstance(item, Mapping)
        ][:10],
        "durable_relay_proven": bool(index),
        "automatic_polling_proven": False,
        "direct_ui_control_proven": False,
    }


def _resume_card(root: Path) -> dict[str, Any]:
    runs_root = root / CODEX_SESSION_RUNS
    latest_receipt = None
    try:
        receipts = sorted(runs_root.glob("*/*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
        if receipts:
            latest_receipt = _rel(root, receipts[0])
    except Exception:
        latest_receipt = None
    return {
        "resume_preview_available": True,
        "resume_send_route_available": True,
        "workspace_write_passthrough_source_proven": True,
        "authenticated_http_retest_proven": False,
        "latest_resume_run_receipt": latest_receipt,
        "direct_live_ui_control_claimed": False,
    }


def _runtime_services_card(root: Path) -> dict[str, Any]:
    service = {
        "service_id": "action_gateway",
        "unit": "ion-action-gateway.service",
        "status_available": False,
        "action_gateway_fresh": None,
        "stale_services": [],
    }
    try:
        completed = subprocess.run(
            [
                "systemctl",
                "--user",
                "show",
                "ion-action-gateway.service",
                "-p",
                "MainPID",
                "-p",
                "ExecMainStartTimestamp",
                "-p",
                "ActiveState",
                "-p",
                "SubState",
                "--no-pager",
            ],
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
    except Exception as exc:
        service["finding"] = f"service_status_unavailable:{exc}"
        return service
    service["status_available"] = completed.returncode == 0
    fields: dict[str, str] = {}
    for line in completed.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            fields[key] = value
    service.update(
        {
            "active_state": fields.get("ActiveState"),
            "sub_state": fields.get("SubState"),
            "main_pid": fields.get("MainPID"),
            "exec_main_start_timestamp": fields.get("ExecMainStartTimestamp"),
            "action_gateway_fresh": bool(fields.get("MainPID") and fields.get("MainPID") != "0"),
        }
    )
    if service["action_gateway_fresh"] is False:
        service["stale_services"] = ["action_gateway"]
    return service


def build_operating_card(root: str | Path | None, args: Mapping[str, Any] | None = None) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    generated_at = _now()
    worker_shift_summary = summarize_shift_board(root=shell_root)
    queue = _queue_card(shell_root)
    domain_weaver = _domain_weaver_card(shell_root)
    runtime_services = _runtime_services_card(shell_root)
    live_sessions = _live_session_card(shell_root)
    resume_send = _resume_card(shell_root)
    blockers = list(worker_shift_summary.get("worker_shift_blockers") or [])
    if runtime_services.get("action_gateway_fresh") is False:
        blockers.append("action_gateway_not_fresh")
    direct_resume_status = (
        "workspace_write_preview_source_and_local_branch_proven_authenticated_http_unproven"
        if resume_send["workspace_write_passthrough_source_proven"]
        else "blocked_until_workspace_write_preview_proven"
    )
    return {
        "ok": True,
        "schema_id": SCHEMA_ID,
        "generated_at": generated_at,
        "mutates_active_state": False,
        "carrier": {
            "carrier_id": "CHATGPT_BROWSER_CARRIER",
            "callsign": "ION_dev",
            "domain_focus": "domain.domain_weaver",
            "authority_posture": {
                "accepted_state_claim": False,
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            },
        },
        "context": {
            "capsule_path": _path_status(shell_root, CHATGPT_CONNECTOR / "ION_CONTEXT_CAPSULE.candidate.yaml"),
            "active_context_package_path": _path_status(
                shell_root,
                CHATGPT_CONNECTOR / "context_packages/CHATGPT_BROWSER_ACTIVE_CONTEXT_PACKAGE.candidate.json",
            ),
            "codex_solo_capsule_path": _path_status(shell_root, CODEX_SOLO / "CAPSULE.md"),
            "codex_solo_hot_context_path": _path_status(shell_root, CODEX_SOLO / "HOT_CONTEXT.md"),
            "codex_solo_status_path": _path_status(shell_root, CODEX_SOLO / "STATUS.json"),
            "freshness": "computed_from_local_files",
        },
        "worker_shift": {
            "active_worker_count": worker_shift_summary.get("active_worker_count", 0),
            "active_lease_count": worker_shift_summary.get("active_lease_count", 0),
            "unbound_active_lease_count": worker_shift_summary.get("unbound_active_lease_count", 0),
            "blocking_leases": worker_shift_summary.get("orphan_exclusive_write_leases", []),
            "readiness_blocked_by_unbound_leases": worker_shift_summary.get("readiness_blocked_by_unbound_leases", False),
        },
        "codex_queue": queue,
        "agent_swarm": {
            "agent_count": domain_weaver.get("agent_count"),
            "queued_agent_request_count": queue.get("queued_request_count"),
            "mounted_agent_invocation": "proven_via_agent_swarm_codex_queue_when_routes_available",
        },
        "domain_weaver": domain_weaver,
        "contact_modes": {
            "mounted_agent_invocation": "proven",
            "durable_live_session_inbox": "delivered_polling_unproven" if live_sessions["durable_relay_proven"] else "not_registered",
            "direct_resume_send": direct_resume_status,
        },
        "codex_live_sessions": live_sessions,
        "codex_session_resume_send": resume_send,
        "runtime_services": runtime_services,
        "blockers": blockers,
        "recommended_next_routes": [
            {"branch_id": "worker_shift", "route_id": "status_summary", "purpose": "check active leases and stale workers"},
            {"branch_id": "domain_weaver_agents", "route_id": "projection_summary", "purpose": "read Domain Weaver readiness"},
            {"branch_id": "codex_session_store", "route_id": "session_resume_send_preview", "purpose": "preview existing-session resume command"},
            {"branch_id": "codex_live_session_bridge", "route_id": "session_status", "purpose": "check durable inbox/outbox relay state"},
            {"branch_id": "runtime_services", "route_id": "service_status", "purpose": "check local service freshness"},
        ],
        "authority": dict(AUTHORITY_FALSE),
        "non_claims": [
            "Operating card is a read-only projection and route membrane.",
            "No accepted-state, product-state, production, live external execution, secrets, git push, deletion, or materialization authority is granted.",
            "Saved-session transcripts and worker returns are evidence surfaces, not accepted state.",
            "Direct live UI control is not claimed.",
        ],
    }
