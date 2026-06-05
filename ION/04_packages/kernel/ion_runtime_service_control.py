"""Branch-gated local runtime service control for ION development services.

This module is intentionally narrower than the cockpit service console. It
accepts stable service IDs only, never arbitrary unit names or shell text, and
records mutation receipts under the runtime_services context lane.
"""

from __future__ import annotations

import ast
import base64
import csv
import hashlib
import json
import re
import shutil
import subprocess
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_agent_comms import build_agent_comms_projection, send_agent_message
from .ion_agent_comms_runs import build_agent_comms_runs_projection
from .ion_agent_invocation_broker import invoke_bounded_agent
from .ion_agent_workspace_comms import pickup_agent_inbox_message, preview_agent_inbox_pickup
from .ion_codex_browser_agent import latest_codex_browser_agent_summary
from .ion_codex_conversation_archive import attach_codex_conversation_to_chat, build_codex_conversation_archive
from .ion_custom_gpt_action_gateway import build_codex_browser_agent_action_contact, submit_codex_browser_agent_action_invocation
from .ion_carrier_onboard import resolve_shell_root_from_ion_root
from .ion_local_service_status import LOCAL_SERVICE_SPECS
from .ion_domain_weaver_context_active_resolver import (
    apply_active_context_gated_refresh,
    build_active_context_gated_refresh_plan,
    build_active_context_reissue_preflight,
    build_context_active_resolver_status,
    resolve_domain_active_context,
)

SCHEMA_ID = "ion.runtime_service_control.v0_1"
CONFIRMATION_TOKEN = "ION_BOUNDED_WRITE_CONFIRMED"
RECEIPT_DIR = Path("ION/05_context/current/runtime_services/receipts")
DEFAULT_HEALTH_TIMEOUT_SECONDS = 1.5
DEFAULT_TEST_TIMEOUT_SECONDS = 120
TEST_RECEIPT_DIR = Path("ION/05_context/current/runtime_services/test_run_receipts")
DOMAIN_WEAVER_PROJECTION_PATH = Path("ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json")
DOMAIN_WEAVER_PROMOTION_REVIEW_PATH = Path("ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROMOTION_REVIEW.json")
DOMAIN_WEAVER_SWARM_EXPANSION_READ_ROOT = "ION/05_context/current/domain_weaver/swarm_expansion"
DOMAIN_WEAVER_SWARM_EXPANSION_INDEX_ROUTE_ID = "domain_weaver_swarm_expansion_index"
DOMAIN_WEAVER_SWARM_EXPANSION_INDEX_VERSION = "ion.local_intelligence.domain_weaver_swarm_expansion_index.v0_1"
DOMAIN_WEAVER_SWARM_EXPANSION_TEXT_SUFFIXES = {".md", ".markdown", ".txt", ".json", ".yaml", ".yml", ".csv", ".log"}
DOMAIN_WEAVER_WAVE0A_EXPECTED_FIRST_THREE_RETURNS = (
    "ION/05_context/current/domain_weaver/swarm_expansion/wave0_batch_a/returns/swarm_control_plane_steward.return.candidate.md",
    "ION/05_context/current/domain_weaver/swarm_expansion/wave0_batch_a/returns/worker_shift_lease_marshal.return.candidate.md",
    "ION/05_context/current/domain_weaver/swarm_expansion/wave0_batch_a/returns/browser_gpt_action_gateway_steward.return.candidate.md",
)
AGENT_COMMS_DIRECTORY_PATH = Path("ION/05_context/current/agent_comms/COMMUNICATION_DIRECTORY.json")
ION_WORKSPACE_MANIFEST_PATH = Path("ION_WORKSPACE_MANIFEST.yaml")
DOMAIN_WEAVER_CURRENT_READ_ROOT = "ION/05_context/current/domain_weaver"
LOCAL_INTELLIGENCE_ALLOWED_ROOTS = (
    "ION/04_packages/kernel",
    "ION/tests",
    "ION/03_registry",
    "ION/05_context/current/action_surface_cartography",
    "ION/05_context/current/runtime_services/test_run_receipts",
    "ION/05_context/current/chatgpt_connector",
    DOMAIN_WEAVER_CURRENT_READ_ROOT,
)
LOCAL_INTELLIGENCE_MAX_FILE_BYTES = 262_144
LARGE_ARTIFACT_ALLOWED_ROOTS = (
    "ION",
    "browser_extension",
)
LARGE_ARTIFACT_OVERSIZE_BYTES = 262_144
LARGE_ARTIFACT_DEFAULT_CHUNK_BYTES = 32_768
LARGE_ARTIFACT_MAX_CHUNK_BYTES = 65_536
LARGE_ARTIFACT_MAX_RESPONSE_BYTES = 64_000
LARGE_ARTIFACT_MAX_PARSE_BYTES = 5_000_000
ARTIFACT_TRANSFER_DIR = Path("ION/05_context/current/artifact_transfer")
ARTIFACT_TRANSFER_DEFAULT_MAX_BYTES = 2_000_000
ARTIFACT_TRANSFER_MAX_FILE_COUNT = 500
SECRET_PATH_MARKERS = (
    ".env",
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    "credential",
    "credentials",
    "secret",
    "secrets",
    "token",
    "tokens",
    "cookie",
    "cookies",
    "private_key",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "local storage",
    "session storage",
    "browser profile",
)
SECRET_PATH_PARTS = (".git", ".ssh", ".gnupg", ".config", ".codex")

TEST_ALLOWLIST: dict[str, list[str]] = {
    "native_ide_v4_alias_regression": [
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_native_ide_status_defaults_to_dist_status",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_native_ide_overlay_routes_target_v4_dist_commands",
    ],
    "runtime_services_branch_smoke": [
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_runtime_services_branch_describe_exposes_gated_routes",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_runtime_services_status_and_reload_plan_are_read_only",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_runtime_services_mutation_requires_idempotency_and_confirmation",
    ],
    "runtime_freshness_probe_smoke": [
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_runtime_services_freshness_probe_reports_registry_handler_parity",
    ],
    "repo_ingest_patch_smoke": [
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_repo_ingest_apply_create_and_readback_are_confirmation_gated",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_repo_ingest_patch_preview_apply_and_readback_smoke",
    ],
    "project_workbench_slice_smoke": [
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_branch_invoke_project_file_slice_forwards_line_args",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_project_workbench_file_slice_missing_path_is_classified",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_project_workbench_patch_preview_apply_and_replay_branch_smoke",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_project_workbench_branch_file_read_slice_patch_preview_and_gates",
    ],
    "action_schema_release_smoke": [
        "ION/tests/test_kernel_ion_action_schema_release.py::test_action_schema_preserves_core_operations",
        "ION/tests/test_kernel_ion_action_schema_release.py::test_action_schema_adds_supabase_operations",
        "ION/tests/test_kernel_ion_action_schema_release.py::test_action_schema_manifest_requires_branch_leader_group",
        "ION/tests/test_kernel_ion_action_schema_release.py::test_action_schema_enforces_openai_gpt_builder_operation_limit",
        "ION/tests/test_kernel_ion_action_schema_release.py::test_action_schema_rejects_missing_branch_leader_operations",
        "ION/tests/test_kernel_ion_action_schema_release.py::test_action_schema_rejects_fragment_install_target",
        "ION/tests/test_kernel_ion_action_schema_release.py::test_action_schema_no_duplicate_operation_ids",
        "ION/tests/test_kernel_ion_action_schema_release.py::test_action_schema_no_secret_strings",
        "ION/tests/test_kernel_ion_action_schema_release.py::test_action_schema_server_correct",
        "ION/tests/test_kernel_ion_action_schema_release.py::test_action_release_report_includes_operation_count_schema_hash_token_source_and_rollback",
        "ION/tests/test_kernel_ion_action_schema_release.py::test_install_sheet_requires_fresh_gpt_session",
        "ION/tests/test_kernel_ion_action_schema_release.py::test_auth_invalid_circuit_breaker_documented",
        "ION/tests/test_kernel_ion_action_schema_release.py::test_action_release_registry_yaml_parses",
        "ION/tests/test_kernel_ion_custom_gpt_action_gateway_policy.py::test_branch_invoke_schema_uses_flexible_args_in_all_action_copies",
    ],
    "browser_codex_agent_smoke": [
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_browser_codex_agent_routes_archive_attach_and_previews",
    ],
    "codex_model_routing_smoke": [
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_codex_queue_model_routing_surfaces_spark_preview_without_enqueue",
    ],
    "domain_weaver_agents_smoke": [
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_domain_weaver_agents_branch_views_comms_and_spawn_preview",
    ],
    "local_intelligence_manifest_smoke": [
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_local_intelligence_branch_indexes_symbols_without_execution",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_local_intelligence_dag_extracts_route_and_validation_graphs",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_local_intelligence_data_profile_profiles_common_formats",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_local_intelligence_receipt_graph_links_receipts_and_proof_refs",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_local_intelligence_local_search_plus_finds_symbols_schema_and_paths",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_local_intelligence_context_pack_compile_plus_rehydrates_operation_context",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_local_intelligence_lexical_index_manifest_is_read_only_and_deterministic",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_local_intelligence_domain_weaver_swarm_expansion_index_is_monitor_friendly",
    ],
    "large_artifact_intelligence_smoke": [
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_large_artifact_intelligence_branch_streams_and_indexes_oversized_files",
    ],
    "artifact_transfer_smoke": [
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_artifact_transfer_branch_previews_and_materializes_safe_zip",
    ],
    "large_artifact_inference_preview_smoke": [
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_large_artifact_inference_preview_routes_are_no_model_call",
    ],
    "browser_gpt_artifact_ui_endpoint_smoke": [
        "ION/tests/test_kernel_ion_local_cockpit_app.py::test_local_cockpit_action_branch_invoke_endpoint_profiles_large_artifact",
        "ION/tests/test_kernel_ion_chatgpt_browser_mcp_http_preview.py::test_public_cockpit_action_branch_invoke_endpoint_requires_auth_and_profiles_artifact",
    ],
    "chatgpt_native_validation_selftest": [
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_runtime_services_focused_test_plan_is_allowlisted_and_read_only",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_runtime_services_focused_test_run_requires_confirmation_and_writes_receipt",
    ],
    "chatgpt_native_validation_manifest_smoke": [
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_chatgpt_native_validation_manifest_and_receipts_are_read_only",
    ],
    "branch_gateway_core_smoke": [
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_branch_leader_registry_loads_initial_branches",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_branch_list_and_describe_return_route_capsules",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_branch_invoke_read_only_route_delegates_to_owner_tool",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_branch_invoke_mutation_route_requires_idempotency_and_confirmation",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_http_mcp_branch_invoke_read_only_does_not_require_confirmation",
    ],
    "worker_shift_coordination_smoke": [
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_worker_shift_branch_describe_and_routes_are_read_only",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_worker_shift_branch_invoke_status_summary_includes_overlap_and_queue_state",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_worker_shift_status_summary_reconciles_active_codex_queue_workers",
        "ION/tests/test_kernel_ion_action_mcp_branch_leaders.py::test_worker_shift_branch_invoke_coordination_state_route_returns_read_view",
    ],
    "parallel_scheduler_preview_smoke": [
        "ION/tests/test_kernel_ion_codex_queue_runner.py::test_validation_lane_aliases_to_audit_lane",
        "ION/tests/test_kernel_ion_codex_queue_runner.py::test_parallel_plan_preview_projects_conflicts_without_mutating_queue_state",
        "ION/tests/test_kernel_ion_chatgpt_browser_mcp_connector_contract.py::test_codex_queue_parallel_plan_preview_tool_is_read_only",
    ],
}


@dataclass(frozen=True)
class RuntimeServiceSpec:
    service_id: str
    unit_name: str
    role: str
    local_url: str | None
    health_url: str | None
    command_summary: str


_SOURCE_SPECS = {
    spec.service_id: spec
    for spec in LOCAL_SERVICE_SPECS
    if spec.service_id in {"action_gateway", "mcp_preview", "cosmos_preview", "cockpit_app", "chatops"}
}

SERVICE_ALLOWLIST: dict[str, RuntimeServiceSpec] = {
    service_id: RuntimeServiceSpec(
        service_id=service_id,
        unit_name=spec.unit_name,
        role=spec.role,
        local_url=spec.local_url,
        health_url=spec.health_url,
        command_summary=spec.command_summary,
    )
    for service_id, spec in _SOURCE_SPECS.items()
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_root(root: str | Path | None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").exists() and (path / "ION/REPO_AUTHORITY.md").exists():
            return path
    return resolve_shell_root_from_ion_root(root)


def _repo_rel(path: Path, root: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _blocked(finding: str, *, refusal_class: str = "SCHEMA_INVALID", data: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "ok": False,
        "finding": finding,
        "refusal_class": refusal_class,
        "production_authority": False,
        "live_execution_authority": False,
    }
    if data:
        payload.update(dict(data))
    return payload


def _ok(operation: str, data: Mapping[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_id": SCHEMA_ID,
        "operation": operation,
        "ok": True,
        "generated_at": _now(),
        "production_authority": False,
        "live_execution_authority": False,
    }
    payload.update(dict(data))
    return payload


def _service_spec(service_id: str) -> tuple[RuntimeServiceSpec | None, dict[str, Any] | None]:
    service_id = str(service_id or "").strip()
    spec = SERVICE_ALLOWLIST.get(service_id)
    if spec is None:
        return None, _blocked(
            "service_id_not_allowed",
            refusal_class="SERVICE_ID_NOT_ALLOWED",
            data={"service_id": service_id, "allowed_service_ids": sorted(SERVICE_ALLOWLIST)},
        )
    return spec, None


def _run_systemctl(args: list[str], *, timeout: float = 8.0) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            ["systemctl", "--user", *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except Exception as exc:
        return {
            "ok": False,
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "finding": exc.__class__.__name__,
        }
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": (completed.stdout or "").strip(),
        "stderr": (completed.stderr or "").strip(),
        "finding": "ok" if completed.returncode == 0 else "systemctl_failed",
    }


def _schedule_deferred_systemctl_restart(
    spec: RuntimeServiceSpec,
    *,
    idempotency_key: str,
    delay_seconds: int = 5,
) -> dict[str, Any]:
    """Schedule a service restart after this request can return its receipt.

    This exists for self-restarting the Action Gateway. It avoids killing the
    process while it is still serializing the HTTP action response.
    """
    safe_key = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in idempotency_key)[:40] or "no_key"
    transient_unit = f"ion-deferred-restart-{spec.service_id}-{safe_key}"
    command = [
        "systemd-run",
        "--user",
        "--unit",
        transient_unit,
        f"--on-active={max(int(delay_seconds), 1)}s",
        "systemctl",
        "--user",
        "restart",
        spec.unit_name,
    ]
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=8.0,
        )
    except Exception as exc:
        return {
            "ok": False,
            "returncode": None,
            "command_shape": command,
            "finding": exc.__class__.__name__,
            "stdout": "",
            "stderr": "",
        }
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "command_shape": command,
        "transient_unit": transient_unit,
        "delay_seconds": max(int(delay_seconds), 1),
        "stdout": (completed.stdout or "").strip(),
        "stderr": (completed.stderr or "").strip(),
        "finding": "deferred_restart_scheduled" if completed.returncode == 0 else "deferred_restart_schedule_failed",
    }


def _parse_systemctl_show(stdout: str) -> dict[str, str]:
    props: dict[str, str] = {}
    for line in stdout.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        props[key] = value
    return props


def _pid_cmdline(pid: int) -> dict[str, Any]:
    if pid <= 0:
        return {"pid": pid, "observed": False, "finding": "no_main_pid"}
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
    except Exception as exc:
        return {"pid": pid, "observed": False, "finding": exc.__class__.__name__}
    parts = [part.decode("utf-8", errors="replace") for part in raw.split(b"\0") if part]
    return {"pid": pid, "observed": True, "cmdline": parts[:16], "finding": "ok"}


def _unit_status(spec: RuntimeServiceSpec) -> dict[str, Any]:
    show = _run_systemctl(
        [
            "show",
            spec.unit_name,
            "--property=Id,MainPID,LoadState,ActiveState,SubState,FragmentPath,ExecMainStartTimestamp",
        ]
    )
    props = _parse_systemctl_show(show.get("stdout", "")) if show.get("ok") else {}
    main_pid = int(props.get("MainPID") or 0) if str(props.get("MainPID") or "").isdigit() else 0
    unit_matches = props.get("Id") == spec.unit_name
    return {
        "service_id": spec.service_id,
        "unit_name": spec.unit_name,
        "systemctl": {
            "ok": bool(show.get("ok")),
            "returncode": show.get("returncode"),
            "finding": show.get("finding"),
            "stderr_tail": str(show.get("stderr") or "")[-800:],
        },
        "properties": {
            "Id": props.get("Id"),
            "MainPID": main_pid,
            "LoadState": props.get("LoadState"),
            "ActiveState": props.get("ActiveState"),
            "SubState": props.get("SubState"),
            "FragmentPath": props.get("FragmentPath"),
            "ExecMainStartTimestamp": props.get("ExecMainStartTimestamp"),
        },
        "unit_identity_proof": {
            "unit_matches_allowlist": unit_matches,
            "expected_unit": spec.unit_name,
            "observed_unit": props.get("Id"),
            "arbitrary_unit_accepted": False,
        },
        "pid_identity_proof": _pid_cmdline(main_pid),
    }


def _probe_health(url: str | None, *, timeout_seconds: float = DEFAULT_HEALTH_TIMEOUT_SECONDS) -> dict[str, Any]:
    if not url:
        return {"probed": False, "status": "not_configured", "http_status": None, "finding": "health_url_not_configured"}
    try:
        request = urllib.request.Request(url, headers={"Accept": "application/json,text/plain,*/*"})
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            status = int(getattr(response, "status", 0) or 0)
            sample = response.read(2048).decode("utf-8", errors="replace")
            return {
                "probed": True,
                "status": "ready" if 200 <= status < 300 else "degraded",
                "http_status": status,
                "finding": "ok" if 200 <= status < 300 else "health_endpoint_non_2xx",
                "body_sample": sample[:300],
            }
    except urllib.error.HTTPError as exc:
        return {"probed": True, "status": "degraded", "http_status": exc.code, "finding": "health_endpoint_http_error"}
    except Exception as exc:
        return {"probed": True, "status": "not_running", "http_status": None, "finding": exc.__class__.__name__}


def _service_status(spec: RuntimeServiceSpec, *, probe_health: bool) -> dict[str, Any]:
    health = _probe_health(spec.health_url) if probe_health else {
        "probed": False,
        "status": "not_probed",
        "http_status": None,
        "finding": None,
    }
    unit = _unit_status(spec)
    return {
        "service_id": spec.service_id,
        "unit_name": spec.unit_name,
        "role": spec.role,
        "local_url": spec.local_url,
        "health_url": spec.health_url,
        "command_summary": spec.command_summary,
        "unit": unit,
        "health": health,
        "production_authority": False,
        "live_execution_authority": False,
    }


def service_status(root: str | Path | None, args: Mapping[str, Any] | None = None) -> dict[str, Any]:
    args = args or {}
    requested = str(args.get("service_id") or "").strip()
    probe_health = bool(args.get("probe_health"))
    if requested:
        spec, blocked = _service_spec(requested)
        if blocked:
            return blocked
        assert spec is not None
        services = [_service_status(spec, probe_health=probe_health)]
    else:
        services = [_service_status(spec, probe_health=probe_health) for spec in SERVICE_ALLOWLIST.values()]
    return _ok(
        "runtimeServicesStatus",
        {
            "service_count": len(services),
            "services": services,
            "allowed_service_ids": sorted(SERVICE_ALLOWLIST),
            "mutates_active_state": False,
        },
    )


def service_reload_plan(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    spec, blocked = _service_spec(str(args.get("service_id") or ""))
    if blocked:
        return blocked
    assert spec is not None
    return _ok(
        "runtimeServiceReloadPlan",
        {
            "service_id": spec.service_id,
            "unit_name": spec.unit_name,
            "would_restart": spec.service_id != "action_gateway",
            "self_restart_deferred": spec.service_id == "action_gateway",
            "restart_command_shape": ["systemctl", "--user", "restart", spec.unit_name],
            "proof_required_before_restart": [
                "service_id resolves through hardcoded allowlist",
                "systemctl show Id equals allowlisted unit name",
                "pre receipt records unit and PID evidence",
            ],
            "proof_recorded_after_restart": [
                "post systemctl show",
                "health endpoint retest",
                "runtime_services receipt path",
            ],
            "action_gateway_down_recovery": "Use MCP 8765 / codex_queue or a local operator terminal when the Action Gateway is down; do not rely on Action Gateway to recover itself.",
            "mutates_active_state": False,
        },
    )


def _receipt_path(root: Path, operation: str, service_id: str, idempotency_key: str) -> Path:
    safe_key = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in idempotency_key)[:96] or "no_key"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return root / RECEIPT_DIR / f"{stamp}_{operation}_{service_id}_{safe_key}.json"


def _write_receipt(
    root: Path,
    *,
    operation: str,
    service_id: str,
    idempotency_key: str,
    receipt_stage: str,
    payload: Mapping[str, Any],
) -> str:
    path = _receipt_path(root, f"{operation}_{receipt_stage}", service_id, idempotency_key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_id": "ion.runtime_service_control_receipt.v0_1",
                "created_at": _now(),
                "operation": operation,
                "receipt_stage": receipt_stage,
                "service_id": service_id,
                "idempotency_key": idempotency_key,
                "payload": dict(payload),
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_claim": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return _repo_rel(path, root)


def _mutation_fields(args: Mapping[str, Any]) -> tuple[str, str, dict[str, Any] | None]:
    confirmation = str(args.get("confirmation") or "").strip()
    idempotency_key = str(args.get("idempotency_key") or "").strip()
    if not idempotency_key:
        return confirmation, idempotency_key, _blocked("idempotency_key_required", refusal_class="IDEMPOTENCY_KEY_REQUIRED")
    if confirmation != CONFIRMATION_TOKEN:
        return confirmation, idempotency_key, _blocked(
            "confirmation_required",
            refusal_class="CONFIRMATION_REQUIRED",
            data={"required_confirmation": CONFIRMATION_TOKEN},
        )
    return confirmation, idempotency_key, None


def restart_service(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    _confirmation, idempotency_key, blocked = _mutation_fields(args)
    if blocked:
        return blocked
    spec, blocked = _service_spec(str(args.get("service_id") or ""))
    if blocked:
        return blocked
    assert spec is not None
    pre = _service_status(spec, probe_health=False)
    pre_receipt = _write_receipt(
        shell_root,
        operation="restart_service",
        service_id=spec.service_id,
        idempotency_key=idempotency_key,
        receipt_stage="pre",
        payload={"pre_status": pre},
    )
    proof = pre["unit"]["unit_identity_proof"]
    if proof.get("unit_matches_allowlist") is not True:
        post_payload = {
            "ok": False,
            "finding": "unit_ownership_not_proven",
            "pre_receipt_path": pre_receipt,
            "pre_status": pre,
        }
        post_receipt = _write_receipt(
            shell_root,
            operation="restart_service",
            service_id=spec.service_id,
            idempotency_key=idempotency_key,
            receipt_stage="post",
            payload=post_payload,
        )
        return _blocked(
            "unit_ownership_not_proven",
            refusal_class="SERVICE_OWNERSHIP_NOT_PROVEN",
            data={**post_payload, "post_receipt_path": post_receipt},
        )
    if spec.service_id == "action_gateway":
        deferred = _schedule_deferred_systemctl_restart(spec, idempotency_key=idempotency_key, delay_seconds=5)
        ok = bool(deferred.get("ok"))
        post_payload = {
            "ok": ok,
            "finding": "action_gateway_self_restart_scheduled" if ok else "action_gateway_self_restart_schedule_failed",
            "pre_receipt_path": pre_receipt,
            "deferred_restart": deferred,
            "pre_status": pre,
        }
        post_receipt = _write_receipt(
            shell_root,
            operation="restart_service",
            service_id=spec.service_id,
            idempotency_key=idempotency_key,
            receipt_stage="post",
            payload=post_payload,
        )
        if not ok:
            return _blocked(
                "action_gateway_self_restart_schedule_failed",
                refusal_class="SELF_RESTART_SCHEDULE_FAILED",
                data={**post_payload, "post_receipt_path": post_receipt},
            )
        deferred_payload = {key: value for key, value in post_payload.items() if key not in {"ok", "finding"}}
        return _blocked(
            "action_gateway_self_restart_deferred",
            refusal_class="SELF_RESTART_DEFERRED",
            data={
                **deferred_payload,
                "post_receipt_path": post_receipt,
                "recovery_route": "Use MCP 8765 / codex_queue or a local operator terminal when the Action Gateway is down.",
                "mutates_active_state": True,
                "self_restart_deferred": True,
            },
        )

    restart = _run_systemctl(["restart", spec.unit_name], timeout=30.0)
    post = _service_status(spec, probe_health=False)
    ok = bool(restart.get("ok"))
    post_payload = {
        "ok": ok,
        "finding": "service_restart_dispatched" if ok else "service_restart_failed",
        "pre_receipt_path": pre_receipt,
        "pre_status": pre,
        "restart": restart,
        "post_status": post,
    }
    post_receipt = _write_receipt(
        shell_root,
        operation="restart_service",
        service_id=spec.service_id,
        idempotency_key=idempotency_key,
        receipt_stage="post",
        payload=post_payload,
    )
    if not ok:
        return _blocked("service_restart_failed", refusal_class="SERVICE_RESTART_FAILED", data={**post_payload, "post_receipt_path": post_receipt})
    return _ok(
        "runtimeServiceRestart",
        {**post_payload, "post_receipt_path": post_receipt, "mutates_active_state": True},
    )


def retest_service(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    spec, blocked = _service_spec(str(args.get("service_id") or ""))
    if blocked:
        return blocked
    assert spec is not None
    status = _service_status(spec, probe_health=True)
    return _ok(
        "runtimeServiceRetest",
        {
            "service_id": spec.service_id,
            "status": status,
            "mutates_active_state": False,
        },
    )


def reload_and_retest(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    restarted = restart_service(root, args)
    if restarted.get("ok") is not True:
        return restarted
    retest = retest_service(root, args)
    shell_root = _resolve_root(root)
    idempotency_key = str(args.get("idempotency_key") or "").strip()
    spec, _blocked_payload = _service_spec(str(args.get("service_id") or ""))
    assert spec is not None
    combined_receipt = _write_receipt(
        shell_root,
        operation="reload_and_retest",
        service_id=spec.service_id,
        idempotency_key=idempotency_key,
        receipt_stage="post",
        payload={"restart_result": restarted, "retest_result": retest},
    )
    return _ok(
        "runtimeServiceReloadAndRetest",
        {
            "service_id": spec.service_id,
            "restart_result": restarted,
            "retest_result": retest,
            "combined_receipt_path": combined_receipt,
            "mutates_active_state": True,
        },
    )


HANDLER_ROUTE_IDS = {
    "service_status",
    "service_reload_plan",
    "restart_service",
    "retest_service",
    "reload_and_retest",
    "focused_test_plan",
    "focused_test_run",
    "focused_test_receipts",
    "receipts",
    "focused_test_suite_manifest",
    "suite_manifest",
    "runtime_freshness_probe",
    "tool_manifest_deep",
    "code_symbol_index",
    "dag_extract",
    "data_profile",
    "receipt_graph",
    "local_search_plus",
    "context_pack_compile_plus",
    "lexical_index_manifest",
    DOMAIN_WEAVER_SWARM_EXPANSION_INDEX_ROUTE_ID,
    "large_file_profile",
    "large_file_chunk_manifest",
    "large_file_slice_read",
    "large_file_stream_start",
    "large_file_stream_next",
    "large_file_stream_range",
    "large_file_anchor_search",
    "large_file_symbol_index",
    "large_file_json_path_read",
    "large_file_section_read",
    "large_artifact_claim_check",
    "zip_request_preview",
    "zip_materialize_request",
    "zip_manifest_read",
    "sandbox_upload_instruction",
    "sandbox_intake_manifest_preview",
    "inference_provider_status",
    "inference_plan_preview",
    "large_artifact_inference_index_preview",
    "large_artifact_inference_question_preview",
    "domain_weaver_status",
    "projection_summary",
    "projection_accepted_refresh_plan",
    "projection_replacement_body_candidate",
    "projection_accepted_refresh_apply",
    "semantic_alias_supervised_apply_preflight",
    "semantic_alias_projection_apply",
    "semantic_alias_mount_manifest_apply",
    "context_active_resolver_status",
    "resolve_context_active",
    "worker_start_readiness_summary",
    "worker_start_backlog_hygiene",
    "spawn_dispatch_legacy_receipt_quarantine",
    "pressure_wave_plan",
    "pressure_wave_spawn_request_seed",
    "comms_overview",
    "spawn_plan_preview",
    "comms_send_preview",
    "comms_send",
    "comms_pickup_preview",
    "comms_pickup",
    "comms_autoreaction_proof",
    "comms_dispatch_preview",
    "comms_dispatch_enqueue",
    "transient_usage_limit_bridge_preview",
    "transient_usage_limit_bridge_create",
    "codex_model_capability_status",
    "codex_model_route_preview",
    "spark_scout_packet_preview",
    "spark_scout_args_validate",
    "browser_codex_agent_status",
    "codex_archive_search_preview",
    "codex_archive_attach_preview",
    "codex_archive_attach",
    "playwright_work_preview",
    "browser_agent_contact",
    "browser_agent_invoke_preview",
    "browser_agent_invoke",
}


def _sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return None


def _registry_branch_route_ids(root: Path, branch_id: str) -> list[str]:
    registry_path = root / "ION/03_registry/ion_action_mcp_branch_leader_registry.yaml"
    try:
        lines = registry_path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    in_branch = False
    routes: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- branch_id:"):
            current = stripped.split(":", 1)[1].strip()
            if in_branch and current != branch_id:
                break
            in_branch = current == branch_id
            continue
        if in_branch and stripped.startswith("- route_id:"):
            routes.append(stripped.split(":", 1)[1].strip())
    return routes


def runtime_freshness_probe(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    service_id = str(args.get("service_id") or "action_gateway").strip()
    spec, blocked = _service_spec(service_id)
    if blocked:
        return blocked
    assert spec is not None
    branch_ids = args.get("branch_ids")
    if branch_ids is None:
        requested_branch_ids = ["runtime_services", "chatgpt_native_validation"]
    elif isinstance(branch_ids, list):
        requested_branch_ids = [str(item).strip() for item in branch_ids if str(item).strip()]
    else:
        return _blocked("branch_ids_must_be_list", refusal_class="SCHEMA_INVALID")
    source_path = Path(__file__).resolve()
    source_rel = _repo_rel(source_path, shell_root)
    service = _service_status(spec, probe_health=True)
    registry_routes = {branch_id: _registry_branch_route_ids(shell_root, branch_id) for branch_id in requested_branch_ids}
    missing_from_handler = {
        branch_id: [route_id for route_id in routes if route_id not in HANDLER_ROUTE_IDS]
        for branch_id, routes in registry_routes.items()
    }
    missing_from_handler = {key: value for key, value in missing_from_handler.items() if value}
    verdict = "fresh_enough" if not missing_from_handler else "registry_handler_route_mismatch"
    return _ok(
        "runtimeFreshnessProbe",
        {
            "service_id": spec.service_id,
            "source_path": source_rel,
            "source_sha256": _sha256_file(source_path),
            "handler_supported_route_ids": sorted(HANDLER_ROUTE_IDS),
            "registry_route_ids_by_branch": registry_routes,
            "missing_from_handler": missing_from_handler,
            "verdict": verdict,
            "stale_mismatch_detected": bool(missing_from_handler),
            "service_status": service,
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def _test_ids_from_args(args: Mapping[str, Any]) -> tuple[list[str], dict[str, Any] | None]:
    suite_id = str(args.get("suite_id") or "native_ide_v4_alias_regression").strip()
    requested = args.get("test_ids")
    if requested is None:
        test_ids = list(TEST_ALLOWLIST.get(suite_id, []))
    elif isinstance(requested, list):
        test_ids = [str(item).strip() for item in requested if str(item).strip()]
    else:
        return [], _blocked("test_ids_must_be_list", refusal_class="SCHEMA_INVALID")

    allowed = set(TEST_ALLOWLIST.get(suite_id, []))
    if not allowed:
        return [], _blocked(
            "suite_id_not_allowed",
            refusal_class="TEST_SUITE_NOT_ALLOWED",
            data={"suite_id": suite_id, "allowed_suite_ids": sorted(TEST_ALLOWLIST)},
        )
    disallowed = [test_id for test_id in test_ids if test_id not in allowed]
    if disallowed:
        return [], _blocked(
            "test_id_not_allowed",
            refusal_class="TEST_ID_NOT_ALLOWED",
            data={"suite_id": suite_id, "disallowed_test_ids": disallowed, "allowed_test_ids": sorted(allowed)},
        )
    if not test_ids:
        return [], _blocked("no_test_ids_selected", refusal_class="SCHEMA_INVALID", data={"suite_id": suite_id})
    return test_ids, None


def focused_test_plan(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    test_ids, blocked = _test_ids_from_args(args)
    if blocked:
        return blocked
    suite_id = str(args.get("suite_id") or "native_ide_v4_alias_regression").strip()
    command_shape = ["python3", "-m", "pytest", *test_ids, "-q"]
    return _ok(
        "runtimeFocusedTestPlan",
        {
            "suite_id": suite_id,
            "test_ids": test_ids,
            "command_shape": command_shape,
            "allowed_suite_ids": sorted(TEST_ALLOWLIST),
            "arbitrary_shell_authority": False,
            "arbitrary_test_authority": False,
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def _write_test_receipt(
    root: Path,
    *,
    suite_id: str,
    idempotency_key: str,
    payload: Mapping[str, Any],
) -> str:
    safe_key = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in idempotency_key)[:96] or "no_key"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = root / TEST_RECEIPT_DIR / f"{stamp}_focused_test_run_{suite_id}_{safe_key}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_id": "ion.runtime_focused_test_run_receipt.v0_1",
                "created_at": _now(),
                "suite_id": suite_id,
                "idempotency_key": idempotency_key,
                "payload": dict(payload),
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_claim": False,
                "secrets_authority": False,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return _repo_rel(path, root)


def focused_test_run(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    _confirmation, idempotency_key, blocked = _mutation_fields(args)
    if blocked:
        return blocked
    test_ids, blocked = _test_ids_from_args(args)
    if blocked:
        return blocked
    suite_id = str(args.get("suite_id") or "native_ide_v4_alias_regression").strip()
    timeout_seconds = int(args.get("timeout") or DEFAULT_TEST_TIMEOUT_SECONDS)
    timeout_seconds = max(1, min(timeout_seconds, 300))
    command_shape = ["python3", "-m", "pytest", *test_ids, "-q"]
    try:
        run_kwargs = {
            "check": False,
            "capture_output": True,
            "text": True,
            "timeout": timeout_seconds,
        }
        try:
            completed = subprocess.run(
                command_shape,
                cwd=shell_root,
                **run_kwargs,
            )
        except TypeError as exc:
            if "cwd" not in str(exc):
                raise
            completed = subprocess.run(
                command_shape,
                **run_kwargs,
            )
        result_payload: dict[str, Any] = {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "finding": "tests_passed" if completed.returncode == 0 else "tests_failed",
            "stdout_tail": (completed.stdout or "")[-6000:],
            "stderr_tail": (completed.stderr or "")[-6000:],
        }
    except subprocess.TimeoutExpired as exc:
        result_payload = {
            "ok": False,
            "returncode": None,
            "finding": "tests_timeout",
            "stdout_tail": str(exc.stdout or "")[-6000:],
            "stderr_tail": str(exc.stderr or "")[-6000:],
        }
    except Exception as exc:
        result_payload = {
            "ok": False,
            "returncode": None,
            "finding": exc.__class__.__name__,
            "stdout_tail": "",
            "stderr_tail": "",
        }
    payload = {
        "suite_id": suite_id,
        "test_ids": test_ids,
        "command_shape": command_shape,
        "timeout_seconds": timeout_seconds,
        "arbitrary_shell_authority": False,
        "arbitrary_test_authority": False,
        "accepted_state_claim": False,
        "secrets_authority": False,
        **result_payload,
    }
    receipt_path = _write_test_receipt(shell_root, suite_id=suite_id, idempotency_key=idempotency_key, payload=payload)
    return _ok(
        "runtimeFocusedTestRun",
        {
            **payload,
            "receipt_path": receipt_path,
            "mutates_active_state": True,
        },
    )


def _focused_test_receipt_summary(path: Path, root: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "path": _repo_rel(path, root),
            "ok": False,
            "finding": exc.__class__.__name__,
        }
    payload = data.get("payload") if isinstance(data, dict) else {}
    payload = payload if isinstance(payload, dict) else {}
    return {
        "path": _repo_rel(path, root),
        "created_at": data.get("created_at"),
        "suite_id": data.get("suite_id") or payload.get("suite_id"),
        "idempotency_key": data.get("idempotency_key"),
        "ok": payload.get("ok"),
        "finding": payload.get("finding"),
        "returncode": payload.get("returncode"),
        "test_count": len(payload.get("test_ids") or []),
        "production_authority": data.get("production_authority", False),
        "live_execution_authority": data.get("live_execution_authority", False),
        "accepted_state_claim": data.get("accepted_state_claim", False),
        "secrets_authority": data.get("secrets_authority", False),
    }


def focused_test_receipts(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    query = str(args.get("query") or "").strip().lower()
    suite_id = str(args.get("suite_id") or "").strip()
    limit = int(args.get("limit") or 20)
    limit = max(1, min(limit, 100))
    receipt_dir = shell_root / TEST_RECEIPT_DIR
    paths = sorted(receipt_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True) if receipt_dir.exists() else []
    matches: list[dict[str, Any]] = []
    for path in paths:
        haystack = path.name.lower()
        if suite_id and f"focused_test_run_{suite_id}_" not in path.name:
            continue
        if query and query not in haystack:
            try:
                if query not in path.read_text(encoding="utf-8", errors="replace").lower():
                    continue
            except Exception:
                continue
        matches.append(_focused_test_receipt_summary(path, shell_root))
        if len(matches) >= limit:
            break
    return _ok(
        "runtimeFocusedTestReceipts",
        {
            "receipt_dir": _repo_rel(receipt_dir, shell_root),
            "query": query,
            "suite_id": suite_id or None,
            "limit": limit,
            "matches": matches,
            "match_count": len(matches),
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def _parse_receipt_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _suite_latest_status_summary(
    suite_id: str,
    *,
    test_count: int,
    receipts: list[dict[str, Any]],
    stale_after_seconds: int,
) -> dict[str, Any]:
    latest = receipts[0] if receipts else None
    passed = [receipt for receipt in receipts if receipt.get("ok") is True]
    failed = [receipt for receipt in receipts if receipt.get("ok") is False]
    latest_created = _parse_receipt_datetime(latest.get("created_at")) if latest else None
    now = datetime.now(timezone.utc)
    stale = latest_created is None or (now - latest_created).total_seconds() > stale_after_seconds
    return {
        "suite_id": suite_id,
        "test_count": test_count,
        "latest": latest,
        "latest_ok": latest.get("ok") if latest else None,
        "latest_finding": latest.get("finding") if latest else "no_receipts",
        "latest_created_at": latest.get("created_at") if latest else None,
        "last_passed_at": passed[0].get("created_at") if passed else None,
        "last_failed_at": failed[0].get("created_at") if failed else None,
        "has_superseded_failures": bool(latest and latest.get("ok") is True and failed),
        "superseded_failure_count": len(failed) if latest and latest.get("ok") is True else 0,
        "receipt_history_count": len(receipts),
        "stale_after_seconds": stale_after_seconds,
        "is_stale": stale,
    }


def focused_test_suite_manifest(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    include_receipts = bool(args.get("include_receipts", True))
    receipt_limit = int(args.get("receipt_limit") or 1)
    receipt_limit = max(1, min(receipt_limit, 10))
    status_history_limit = int(args.get("status_history_limit") or max(receipt_limit, 10))
    status_history_limit = max(1, min(status_history_limit, 50))
    stale_after_seconds = int(args.get("stale_after_seconds") or 24 * 60 * 60)
    stale_after_seconds = max(60, min(stale_after_seconds, 30 * 24 * 60 * 60))
    suites: list[dict[str, Any]] = []
    latest_status_by_suite: dict[str, Any] = {}
    for suite_id, test_ids in sorted(TEST_ALLOWLIST.items()):
        history = focused_test_receipts(
            shell_root,
            {"suite_id": suite_id, "limit": status_history_limit},
        ).get("matches", [])
        suite = {
            "suite_id": suite_id,
            "test_ids": list(test_ids),
            "test_count": len(test_ids),
            "command_shape": ["python3", "-m", "pytest", *test_ids, "-q"],
        }
        if include_receipts:
            suite["recent_receipts"] = history[:receipt_limit]
        latest_status = _suite_latest_status_summary(
            suite_id,
            test_count=len(test_ids),
            receipts=history,
            stale_after_seconds=stale_after_seconds,
        )
        suite["latest_status"] = latest_status
        latest_status_by_suite[suite_id] = latest_status
        suites.append(suite)
    return _ok(
        "runtimeFocusedTestSuiteManifest",
        {
            "allowed_suite_ids": sorted(TEST_ALLOWLIST),
            "suite_count": len(suites),
            "suites": suites,
            "latest_status_by_suite": latest_status_by_suite,
            "stale_after_seconds": stale_after_seconds,
            "status_history_limit": status_history_limit,
            "arbitrary_shell_authority": False,
            "arbitrary_test_authority": False,
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def _read_workspace_manifest_scalar(root: Path, key: str) -> Path | None:
    """Read one absolute path scalar from ION_WORKSPACE_MANIFEST.yaml if present."""

    manifest = root / ION_WORKSPACE_MANIFEST_PATH
    if not manifest.is_file():
        return None
    pattern = re.compile(rf"^\s*{re.escape(key)}:\s*[\"']?([^\"'\n]+)[\"']?\s*$")
    try:
        for line in manifest.read_text(encoding="utf-8").splitlines():
            match = pattern.match(line)
            if match:
                return Path(match.group(1)).expanduser().resolve(strict=False)
    except OSError:
        return None
    return None


def _shared_read_root_registry(root: Path, relative_roots: tuple[str, ...]) -> list[tuple[str, Path]]:
    """Resolve static read roots plus manifest-derived active ION content roots."""

    rows: list[tuple[str, Path]] = []
    seen: set[str] = set()

    def add(label: str, path: Path) -> None:
        resolved = path.resolve(strict=False)
        key = resolved.as_posix()
        if key not in seen:
            rows.append((label, resolved))
            seen.add(key)

    for rel in relative_roots:
        add(rel, root / rel)

    active_repo_root = _read_workspace_manifest_scalar(root, "active_repo_root")
    if active_repo_root is not None:
        for rel in relative_roots:
            add(f"manifest:active_repo_root/{rel}", active_repo_root / rel)

    ion_content_root = _read_workspace_manifest_scalar(root, "ion_content_root")
    if ion_content_root is not None:
        for rel in relative_roots:
            if rel == "ION":
                add("manifest:ion_content_root", ion_content_root)
            elif rel.startswith("ION/"):
                add(f"manifest:ion_content_root/{rel[4:]}", ion_content_root / rel[4:])

    return rows


def _shared_read_root_labels(root: Path, relative_roots: tuple[str, ...]) -> list[str]:
    return [label for label, _path in _shared_read_root_registry(root, relative_roots)]


def _shared_read_allowed_roots(root: Path, relative_roots: tuple[str, ...]) -> list[Path]:
    return [path for _label, path in _shared_read_root_registry(root, relative_roots)]


def _local_intelligence_allowed_roots(root: Path) -> list[Path]:
    return _shared_read_allowed_roots(root, LOCAL_INTELLIGENCE_ALLOWED_ROOTS)


def _local_intelligence_is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(parent.resolve(strict=False))
        return True
    except ValueError:
        return False


def _shared_read_secret_reason(path: Path, root: Path) -> str | None:
    rel = _repo_rel(path, root)
    lowered_parts = [part.lower() for part in Path(rel).parts]
    lowered = rel.lower()
    if any(part in SECRET_PATH_PARTS for part in lowered_parts):
        return "hidden_credential_or_session_path"
    for marker in SECRET_PATH_MARKERS:
        if marker in lowered:
            return f"secret_path_marker:{marker}"
    return None


def _local_intelligence_resolve_path(root: Path, requested: str | None, *, default: str) -> tuple[Path | None, dict[str, Any] | None]:
    rel = str(requested or default).strip()
    if not rel:
        return None, _blocked("path_required", refusal_class="SCHEMA_INVALID")
    path = (root / rel).resolve(strict=False)
    if not any(_local_intelligence_is_under(path, allowed) for allowed in _local_intelligence_allowed_roots(root)):
        return None, _blocked(
            "path_not_allowed",
            refusal_class="PATH_NOT_ALLOWED",
            data={
                "path": rel,
                "allowed_roots": _shared_read_root_labels(root, LOCAL_INTELLIGENCE_ALLOWED_ROOTS),
                "read_root_policy": "shared_manifest_active_ion_read_roots",
            },
        )
    secret_reason = _shared_read_secret_reason(path, root)
    if secret_reason:
        return None, _blocked(
            "path_not_allowed",
            refusal_class="PATH_NOT_ALLOWED",
            data={"path": _repo_rel(path, root), "reason": secret_reason},
        )
    return path, None


def _local_intelligence_read_py(path: Path) -> tuple[str | None, str | None]:
    try:
        if path.stat().st_size > LOCAL_INTELLIGENCE_MAX_FILE_BYTES:
            return None, "file_too_large"
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        return None, "unicode_decode_error"
    except Exception as exc:
        return None, exc.__class__.__name__


def _local_intelligence_iter_py(path: Path, *, max_files: int, shell_root: Path):
    if path.is_file():
        if path.suffix == ".py" and _shared_read_secret_reason(path, shell_root) is None:
            yield path
        return
    count = 0
    for py_path in sorted(path.rglob("*.py")):
        if not py_path.is_file() or py_path.name.startswith("."):
            continue
        if _shared_read_secret_reason(py_path, shell_root):
            continue
        yield py_path
        count += 1
        if count >= max_files:
            return


def _local_intelligence_symbols(text: str) -> tuple[list[dict[str, Any]], list[str], str | None]:
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return [], [], f"SyntaxError:{exc.lineno}"
    symbols: list[dict[str, Any]] = []
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append(
                {
                    "name": node.name,
                    "kind": "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function",
                    "line_start": int(getattr(node, "lineno", 0) or 0),
                    "line_end": getattr(node, "end_lineno", None),
                    "docstring_excerpt": (ast.get_docstring(node) or "")[:200] or None,
                }
            )
        elif isinstance(node, ast.ClassDef):
            symbols.append(
                {
                    "name": node.name,
                    "kind": "class",
                    "line_start": int(getattr(node, "lineno", 0) or 0),
                    "line_end": getattr(node, "end_lineno", None),
                    "docstring_excerpt": (ast.get_docstring(node) or "")[:200] or None,
                }
            )
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append("." * int(node.level or 0) + str(node.module or ""))
    symbols.sort(key=lambda item: (item["line_start"], item["kind"], item["name"]))
    return symbols, sorted(set(imports)), None


def local_intelligence_tool_manifest_deep(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    requested_root, blocked = _local_intelligence_resolve_path(
        shell_root,
        str(args.get("root_path") or "").strip() or None,
        default="ION/04_packages/kernel",
    )
    if blocked:
        return blocked
    assert requested_root is not None
    limit = max(1, min(int(args.get("limit") or 80), 300))
    modules: list[dict[str, Any]] = []
    tests_root = shell_root / "ION/tests"
    test_texts: list[str] = []
    if tests_root.exists():
        for test_path in sorted(tests_root.rglob("test_*.py"))[:300]:
            if _shared_read_secret_reason(test_path, shell_root):
                continue
            text, error = _local_intelligence_read_py(test_path)
            if not error and text:
                test_texts.append(text)
    for py_path in _local_intelligence_iter_py(requested_root, max_files=limit, shell_root=shell_root):
        text, error = _local_intelligence_read_py(py_path)
        rel = _repo_rel(py_path, shell_root)
        if error or text is None:
            modules.append({"path": rel, "ok": False, "finding": error})
            continue
        symbols, imports, parse_error = _local_intelligence_symbols(text)
        public_symbols = [item["name"] for item in symbols if not str(item["name"]).startswith("_")]
        modules.append(
            {
                "path": rel,
                "ok": parse_error is None,
                "finding": parse_error or "ok",
                "bytes": len(text.encode("utf-8")),
                "function_count": sum(1 for item in symbols if item["kind"] in {"function", "async_function"}),
                "class_count": sum(1 for item in symbols if item["kind"] == "class"),
                "public_symbols": public_symbols[:40],
                "imports": imports[:40],
                "has_main_guard": "if __name__ == \"__main__\"" in text or "if __name__ == '__main__'" in text,
                "test_reference_count": sum(1 for test_text in test_texts if py_path.name in test_text or py_path.stem in test_text),
            }
        )
    return _ok(
        "localIntelligenceToolManifestDeep",
        {
            "root_path": _repo_rel(requested_root, shell_root),
            "module_count": len(modules),
            "modules": modules,
            "arbitrary_shell_authority": False,
            "exec_indexed_code": False,
            "network_authority": False,
        },
    )


def local_intelligence_code_symbol_index(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    path, blocked = _local_intelligence_resolve_path(
        shell_root,
        str(args.get("path") or args.get("root_path") or "").strip() or None,
        default="ION/04_packages/kernel/ion_action_mcp_branch_leaders.py",
    )
    if blocked:
        return blocked
    assert path is not None
    max_files = max(1, min(int(args.get("max_files") or 20), 100))
    files: list[dict[str, Any]] = []
    for py_path in _local_intelligence_iter_py(path, max_files=max_files, shell_root=shell_root):
        text, error = _local_intelligence_read_py(py_path)
        rel = _repo_rel(py_path, shell_root)
        if error or text is None:
            files.append({"path": rel, "ok": False, "finding": error, "symbols": []})
            continue
        symbols, imports, parse_error = _local_intelligence_symbols(text)
        files.append(
            {
                "path": rel,
                "ok": parse_error is None,
                "finding": parse_error or "ok",
                "symbol_count": len(symbols),
                "symbols": symbols[:120],
                "imports": imports[:80],
            }
        )
    return _ok(
        "localIntelligenceCodeSymbolIndex",
        {
            "path": _repo_rel(path, shell_root),
            "file_count": len(files),
            "files": files,
            "arbitrary_shell_authority": False,
            "exec_indexed_code": False,
            "network_authority": False,
        },
    )


def _registry_action_route_dag(root: Path, *, branch_filter: str | None = None) -> dict[str, Any]:
    registry_path = root / "ION/03_registry/ion_action_mcp_branch_leader_registry.yaml"
    try:
        lines = registry_path.read_text(encoding="utf-8").splitlines()
    except Exception as exc:
        return {"ok": False, "finding": exc.__class__.__name__, "nodes": [], "edges": []}
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, str]] = []
    current_branch: str | None = None
    current_route: dict[str, Any] | None = None
    in_routes = False

    def add_node(node_id: str, kind: str, **extra: Any) -> None:
        nodes.setdefault(node_id, {"id": node_id, "kind": kind, **extra})
        nodes[node_id].update(extra)

    def flush_route() -> None:
        nonlocal current_route
        if not current_branch or not current_route:
            current_route = None
            return
        route_id = str(current_route.get("route_id") or "")
        if not route_id:
            current_route = None
            return
        branch_node = f"branch:{current_branch}"
        route_node = f"route:{current_branch}.{route_id}"
        add_node(branch_node, "branch", branch_id=current_branch)
        add_node(route_node, "route", branch_id=current_branch, **current_route)
        edges.append({"from": branch_node, "to": route_node, "kind": "exposes_route"})
        owner = current_route.get("local_handler") or current_route.get("mcp_tool") or current_route.get("branch_ref")
        if owner:
            owner_kind = "local_handler" if current_route.get("local_handler") else "owner_tool"
            owner_node = f"{owner_kind}:{owner}"
            add_node(owner_node, owner_kind, name=owner)
            edges.append({"from": route_node, "to": owner_node, "kind": "delegates_to"})
        current_route = None

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- branch_id:"):
            flush_route()
            current_branch = stripped.split(":", 1)[1].strip()
            in_routes = False
            if branch_filter and current_branch != branch_filter:
                continue
            add_node(f"branch:{current_branch}", "branch", branch_id=current_branch)
            continue
        if branch_filter and current_branch != branch_filter:
            continue
        if stripped == "routes:":
            in_routes = True
            continue
        if not in_routes:
            continue
        if stripped.startswith("- route_id:"):
            flush_route()
            current_route = {"route_id": stripped.split(":", 1)[1].strip()}
            continue
        if current_route is not None and ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"')
            if key in {"title", "summary", "local_handler", "mcp_tool", "branch_ref", "mutates_state", "confirmation_required", "idempotency_required", "route_schema_version"}:
                if value in {"true", "false"}:
                    current_route[key] = value == "true"
                else:
                    current_route[key] = value
    flush_route()
    return {"ok": True, "finding": "ok", "nodes": list(nodes.values()), "edges": edges}


def _validation_suite_dag(root: Path, *, suite_id: str | None = None) -> dict[str, Any]:
    suites = {key: value for key, value in TEST_ALLOWLIST.items() if not suite_id or key == suite_id}
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, str]] = []
    for suite, test_ids in sorted(suites.items()):
        suite_node = f"suite:{suite}"
        receipt_view = focused_test_receipts(root, {"suite_id": suite, "limit": 1})
        recent = receipt_view.get("matches", []) if isinstance(receipt_view, dict) else []
        nodes[suite_node] = {
            "id": suite_node,
            "kind": "validation_suite",
            "suite_id": suite,
            "test_count": len(test_ids),
            "latest_receipt": recent[0] if recent else None,
        }
        for test_id in test_ids:
            test_node = f"test:{test_id}"
            file_part = test_id.split("::", 1)[0]
            file_node = f"file:{file_part}"
            nodes[test_node] = {"id": test_node, "kind": "test", "test_id": test_id}
            nodes.setdefault(file_node, {"id": file_node, "kind": "file", "path": file_part})
            edges.append({"from": suite_node, "to": test_node, "kind": "includes_test"})
            edges.append({"from": test_node, "to": file_node, "kind": "defined_in"})
        if recent:
            receipt_path = recent[0].get("path")
            receipt_node = f"receipt:{receipt_path}"
            nodes[receipt_node] = {"id": receipt_node, "kind": "receipt", **recent[0]}
            edges.append({"from": suite_node, "to": receipt_node, "kind": "latest_receipt"})
    return {"ok": True, "finding": "ok", "nodes": list(nodes.values()), "edges": edges}


def local_intelligence_dag_extract(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    dag_type = str(args.get("dag_type") or "validation_suite_dag").strip()
    if dag_type == "action_route_dag":
        graph = _registry_action_route_dag(shell_root, branch_filter=str(args.get("branch_id") or "").strip() or None)
    elif dag_type == "validation_suite_dag":
        graph = _validation_suite_dag(shell_root, suite_id=str(args.get("suite_id") or "").strip() or None)
    else:
        return _blocked(
            "dag_type_not_allowed",
            refusal_class="DAG_TYPE_NOT_ALLOWED",
            data={"dag_type": dag_type, "allowed_dag_types": ["action_route_dag", "validation_suite_dag"]},
        )
    return _ok(
        "localIntelligenceDagExtract",
        {
            "dag_type": dag_type,
            "node_count": len(graph.get("nodes", [])),
            "edge_count": len(graph.get("edges", [])),
            "nodes": graph.get("nodes", []),
            "edges": graph.get("edges", []),
            "arbitrary_shell_authority": False,
            "exec_indexed_code": False,
            "network_authority": False,
        },
    )


def _schema_ids_from_text(text: str) -> list[str]:
    matches = re.findall(r"['\"]?schema_id['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9_.:-]+)", text)
    return sorted(set(matches))[:20]


def _path_refs_from_text(text: str) -> list[str]:
    matches = re.findall(r"\b(?:ION|ION_Developement)/[A-Za-z0-9_./+@:=,-]+", text)
    return sorted(set(match.rstrip('.,)\"]') for match in matches))[:40]


def _profile_json_text(text: str) -> dict[str, Any]:
    try:
        data = json.loads(text)
    except Exception as exc:
        return {"parse_ok": False, "finding": exc.__class__.__name__}
    key_counts: dict[str, int] = {}

    def walk(value: Any) -> int:
        if isinstance(value, dict):
            for key, child in value.items():
                key_counts[str(key)] = key_counts.get(str(key), 0) + 1
                walk(child)
            return 1
        if isinstance(value, list):
            for child in value[:1000]:
                walk(child)
            return len(value)
        return 0

    record_count = walk(data)
    top_keys = sorted(key_counts.items(), key=lambda item: (-item[1], item[0]))[:30]
    return {
        "parse_ok": True,
        "root_type": type(data).__name__,
        "record_count_hint": record_count,
        "top_keys": [{"key": key, "count": count} for key, count in top_keys],
        "schema_ids": sorted({str(value) for key, value in (data.items() if isinstance(data, dict) else []) if key == "schema_id"})[:20],
    }


def _profile_yaml_text(text: str) -> dict[str, Any]:
    key_counts: dict[str, int] = {}
    schema_ids: list[str] = []
    for line in text.splitlines()[:5000]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        clean_key = key.strip().lstrip("- ").strip()
        if not clean_key:
            continue
        key_counts[clean_key] = key_counts.get(clean_key, 0) + 1
        if clean_key == "schema_id":
            schema_ids.append(value.strip().strip("'\""))
    top_keys = sorted(key_counts.items(), key=lambda item: (-item[1], item[0]))[:30]
    return {
        "parse_ok": True,
        "root_type": "yaml_text_projection",
        "top_keys": [{"key": key, "count": count} for key, count in top_keys],
        "schema_ids": sorted(set(schema_ids))[:20],
    }


def _profile_csv_text(text: str) -> dict[str, Any]:
    try:
        sample = text.splitlines()
        reader = csv.DictReader(sample)
        rows = list(reader)
    except Exception as exc:
        return {"parse_ok": False, "finding": exc.__class__.__name__}
    fieldnames = list(reader.fieldnames or [])
    non_empty_counts = {field: 0 for field in fieldnames}
    for row in rows[:1000]:
        for field in fieldnames:
            if str(row.get(field) or "").strip():
                non_empty_counts[field] += 1
    return {
        "parse_ok": True,
        "root_type": "csv",
        "row_count": len(rows),
        "field_count": len(fieldnames),
        "fieldnames": fieldnames[:80],
        "non_empty_counts": non_empty_counts,
    }


def _profile_markdown_text(text: str) -> dict[str, Any]:
    headings: list[dict[str, Any]] = []
    fenced_code_blocks = 0
    in_fence = False
    for index, line in enumerate(text.splitlines(), start=1):
        if line.strip().startswith("```"):
            if not in_fence:
                fenced_code_blocks += 1
            in_fence = not in_fence
        if not in_fence and line.startswith("#"):
            marker = line.split(" ", 1)[0]
            if set(marker) == {"#"} and 1 <= len(marker) <= 6:
                headings.append({"line": index, "level": len(marker), "text": line[len(marker):].strip()[:160]})
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    return {
        "parse_ok": True,
        "root_type": "markdown",
        "heading_count": len(headings),
        "headings": headings[:40],
        "link_count": len(links),
        "links": links[:40],
        "fenced_code_block_count": fenced_code_blocks,
        "schema_ids": _schema_ids_from_text(text),
        "path_refs": _path_refs_from_text(text),
    }


def local_intelligence_data_profile(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    path, blocked = _local_intelligence_resolve_path(
        shell_root,
        str(args.get("path") or "").strip() or None,
        default="ION/05_context/current/action_surface_cartography/ACTION_EVOLUTION_TESTING_ROADMAP_20260602.candidate.md",
    )
    if blocked:
        return blocked
    assert path is not None
    text, error = _local_intelligence_read_py(path)
    if error or text is None:
        return _blocked("data_profile_read_failed", refusal_class="DATA_PROFILE_READ_FAILED", data={"path": _repo_rel(path, shell_root), "finding": error})
    suffix = path.suffix.lower()
    if suffix == ".json":
        profile = _profile_json_text(text)
        file_type = "json"
    elif suffix in {".yaml", ".yml"}:
        profile = _profile_yaml_text(text)
        file_type = "yaml"
    elif suffix == ".csv":
        profile = _profile_csv_text(text)
        file_type = "csv"
    elif suffix in {".md", ".markdown", ".txt"}:
        profile = _profile_markdown_text(text)
        file_type = "markdown" if suffix in {".md", ".markdown"} else "text"
    else:
        profile = {"parse_ok": True, "root_type": "plain_text", "schema_ids": _schema_ids_from_text(text), "path_refs": _path_refs_from_text(text)}
        file_type = "text"
    return _ok(
        "localIntelligenceDataProfile",
        {
            "path": _repo_rel(path, shell_root),
            "file_type": file_type,
            "bytes": len(text.encode("utf-8")),
            "line_count": len(text.splitlines()),
            "profile": profile,
            "arbitrary_shell_authority": False,
            "exec_indexed_code": False,
            "network_authority": False,
            "content_returned": "summary_only",
        },
    )


def _json_walk_values(value: Any):
    if isinstance(value, dict):
        for child in value.values():
            yield from _json_walk_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from _json_walk_values(child)
    else:
        yield value


def _receipt_summary_from_json(path: Path, root: Path, data: Mapping[str, Any]) -> dict[str, Any]:
    payload = data.get("payload") if isinstance(data.get("payload"), dict) else {}
    nested_data = data.get("data") if isinstance(data.get("data"), dict) else {}
    schema_id = data.get("schema_id") or payload.get("schema_id") or nested_data.get("schema_id")
    suite_id = data.get("suite_id") or payload.get("suite_id")
    idempotency_key = data.get("idempotency_key") or payload.get("idempotency_key") or nested_data.get("idempotency_key")
    ok = data.get("ok") if "ok" in data else payload.get("ok", nested_data.get("ok"))
    finding = data.get("finding") or payload.get("finding") or nested_data.get("finding")
    returncode = payload.get("returncode") if isinstance(payload, dict) else None
    test_ids = payload.get("test_ids") if isinstance(payload.get("test_ids"), list) else []
    touched_paths = nested_data.get("touched_paths") if isinstance(nested_data.get("touched_paths"), list) else data.get("touched_paths", [])
    text = json.dumps(data, sort_keys=True, default=str)
    refs = _path_refs_from_text(text)
    return {
        "path": _repo_rel(path, root),
        "schema_id": schema_id,
        "created_at": data.get("created_at") or data.get("generated_at"),
        "suite_id": suite_id,
        "idempotency_key": idempotency_key,
        "ok": ok,
        "finding": finding,
        "returncode": returncode,
        "test_ids": test_ids[:40],
        "touched_paths": [str(item) for item in touched_paths[:40]] if isinstance(touched_paths, list) else [],
        "path_refs": refs,
        "production_authority": data.get("production_authority", False),
        "live_execution_authority": data.get("live_execution_authority", False),
        "accepted_state_claim": data.get("accepted_state_claim", False),
        "secrets_authority": data.get("secrets_authority", False),
    }


def local_intelligence_receipt_graph(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    receipt_dir, blocked = _local_intelligence_resolve_path(
        shell_root,
        str(args.get("receipt_dir") or args.get("path") or "").strip() or None,
        default="ION/05_context/current/runtime_services/test_run_receipts",
    )
    if blocked:
        return blocked
    assert receipt_dir is not None
    limit = max(1, min(int(args.get("limit") or 25), 100))
    query = str(args.get("query") or "").strip().lower()
    files = [receipt_dir] if receipt_dir.is_file() else sorted(receipt_dir.rglob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, str]] = []

    def add_node(node_id: str, kind: str, **extra: Any) -> None:
        nodes.setdefault(node_id, {"id": node_id, "kind": kind, **extra})
        nodes[node_id].update(extra)

    processed = 0
    for path in files:
        if processed >= limit:
            break
        text, error = _local_intelligence_read_py(path)
        if error or text is None:
            continue
        if query and query not in path.name.lower() and query not in text.lower():
            continue
        try:
            data = json.loads(text)
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        summary = _receipt_summary_from_json(path, shell_root, data)
        receipt_node = f"receipt:{summary['path']}"
        add_node(receipt_node, "receipt", **summary)
        if summary.get("suite_id"):
            suite_node = f"suite:{summary['suite_id']}"
            add_node(suite_node, "validation_suite", suite_id=summary["suite_id"])
            edges.append({"from": suite_node, "to": receipt_node, "kind": "has_receipt"})
        if summary.get("idempotency_key"):
            intent_node = f"intent:{summary['idempotency_key']}"
            add_node(intent_node, "idempotency_key", idempotency_key=summary["idempotency_key"])
            edges.append({"from": intent_node, "to": receipt_node, "kind": "produced_receipt"})
        for test_id in summary.get("test_ids", []):
            test_node = f"test:{test_id}"
            add_node(test_node, "test", test_id=test_id)
            edges.append({"from": receipt_node, "to": test_node, "kind": "covers_test"})
        for ref in summary.get("touched_paths", []) + summary.get("path_refs", []):
            if not ref or not isinstance(ref, str):
                continue
            file_node = f"file:{ref}"
            add_node(file_node, "file", path=ref)
            edges.append({"from": receipt_node, "to": file_node, "kind": "references_path"})
        processed += 1
    return _ok(
        "localIntelligenceReceiptGraph",
        {
            "receipt_dir": _repo_rel(receipt_dir, shell_root),
            "query": query,
            "processed_receipts": processed,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "nodes": list(nodes.values()),
            "edges": edges,
            "arbitrary_shell_authority": False,
            "exec_indexed_code": False,
            "network_authority": False,
            "content_returned": "summary_only",
        },
    )


def _local_search_iter_files(path: Path, *, max_files: int, shell_root: Path):
    allowed_suffixes = {".py", ".md", ".markdown", ".txt", ".json", ".yaml", ".yml", ".csv"}
    if path.is_file():
        if path.suffix.lower() in allowed_suffixes and _shared_read_secret_reason(path, shell_root) is None:
            yield path
        return
    count = 0
    for item in sorted(path.rglob("*")):
        if not item.is_file() or item.name.startswith("."):
            continue
        if _shared_read_secret_reason(item, shell_root):
            continue
        if item.suffix.lower() not in allowed_suffixes:
            continue
        yield item
        count += 1
        if count >= max_files:
            return


def _local_search_symbol_hits(text: str, query_lower: str) -> list[dict[str, Any]]:
    if not query_lower:
        return []
    symbols, _imports, parse_error = _local_intelligence_symbols(text)
    if parse_error:
        return []
    return [
        {
            "symbol": item["name"],
            "kind": item["kind"],
            "line_start": item["line_start"],
            "line_end": item.get("line_end"),
        }
        for item in symbols
        if query_lower in str(item["name"]).lower()
    ][:40]


def local_intelligence_local_search_plus(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    query = str(args.get("query") or "").strip()
    if not query:
        return _blocked("query_required", refusal_class="SCHEMA_INVALID")
    root_path, blocked = _local_intelligence_resolve_path(
        shell_root,
        str(args.get("path") or args.get("root_path") or "").strip() or None,
        default="ION/04_packages/kernel",
    )
    if blocked:
        return blocked
    assert root_path is not None
    max_files = max(1, min(int(args.get("max_files") or 80), 300))
    max_line_hits = max(1, min(int(args.get("max_line_hits") or 20), 100))
    query_lower = query.lower()
    results: list[dict[str, Any]] = []
    for file_path in _local_search_iter_files(root_path, max_files=max_files, shell_root=shell_root):
        text, error = _local_intelligence_read_py(file_path)
        rel = _repo_rel(file_path, shell_root)
        if error or text is None:
            continue
        line_hits: list[dict[str, Any]] = []
        for line_no, line in enumerate(text.splitlines(), start=1):
            if query_lower in line.lower():
                line_hits.append({"line": line_no, "text": line.strip()[:240]})
                if len(line_hits) >= max_line_hits:
                    break
        filename_hit = query_lower in file_path.name.lower() or query_lower in rel.lower()
        symbol_hits = _local_search_symbol_hits(text, query_lower) if file_path.suffix == ".py" else []
        schema_ids = [schema_id for schema_id in _schema_ids_from_text(text) if query_lower in schema_id.lower() or query_lower == "schema_id"]
        path_refs = _path_refs_from_text(text)
        test_id_hits = []
        if "::" in text or file_path.name.startswith("test_"):
            test_id_hits = [hit["text"] for hit in line_hits if "::" in hit["text"] or hit["text"].startswith("def test_")][:20]
        path_ref_match = any(query_lower in ref.lower() for ref in path_refs)
        if filename_hit or line_hits or symbol_hits or schema_ids or path_ref_match:
            results.append(
                {
                    "path": rel,
                    "file_type": file_path.suffix.lower().lstrip(".") or "text",
                    "filename_hit": filename_hit,
                    "line_hit_count": len(line_hits),
                    "line_hits": line_hits,
                    "symbol_hits": symbol_hits,
                    "schema_ids": schema_ids[:20],
                    "path_refs": path_refs[:20],
                    "test_id_hits": test_id_hits,
                    "bytes": len(text.encode("utf-8")),
                }
            )
    return _ok(
        "localIntelligenceLocalSearchPlus",
        {
            "query": query,
            "root_path": _repo_rel(root_path, shell_root),
            "searched_file_limit": max_files,
            "result_count": len(results),
            "results": results[:100],
            "arbitrary_shell_authority": False,
            "exec_indexed_code": False,
            "network_authority": False,
            "content_returned": "snippets_only",
        },
    )


def _lexical_terms(text: str, *, limit: int = 30) -> list[dict[str, Any]]:
    stop = {
        "the", "and", "for", "with", "that", "this", "from", "true", "false", "none",
        "return", "assert", "import", "def", "class", "path", "args", "root", "test",
        "ion", "schema", "id",
    }
    counts: dict[str, int] = {}
    for token in re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", text.lower()):
        if token in stop or len(token) > 64:
            continue
        counts[token] = counts.get(token, 0) + 1
    return [
        {"term": term, "count": count}
        for term, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]
    ]


def local_intelligence_lexical_index_manifest(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    requested_root, blocked = _local_intelligence_resolve_path(
        shell_root,
        str(args.get("root_path") or args.get("path") or "").strip() or None,
        default="ION/05_context/current/action_surface_cartography",
    )
    if blocked:
        return blocked
    assert requested_root is not None
    max_files = max(1, min(int(args.get("max_files") or 80), 300))
    term_limit = max(1, min(int(args.get("term_limit") or 30), 100))
    files: list[dict[str, Any]] = []
    aggregate_terms: dict[str, int] = {}
    total_bytes = 0
    for file_path in _local_search_iter_files(requested_root, max_files=max_files, shell_root=shell_root):
        text, error = _local_intelligence_read_py(file_path)
        rel = _repo_rel(file_path, shell_root)
        if error or text is None:
            files.append({"path": rel, "ok": False, "finding": error})
            continue
        encoded = text.encode("utf-8")
        total_bytes += len(encoded)
        symbols: list[dict[str, Any]] = []
        if file_path.suffix == ".py":
            symbols, _imports, _parse_error = _local_intelligence_symbols(text)
        headings = _profile_markdown_text(text).get("headings", []) if file_path.suffix.lower() in {".md", ".markdown"} else []
        terms = _lexical_terms(text, limit=term_limit)
        for item in terms:
            aggregate_terms[item["term"]] = aggregate_terms.get(item["term"], 0) + int(item["count"])
        files.append(
            {
                "path": rel,
                "ok": True,
                "file_type": file_path.suffix.lower().lstrip(".") or "text",
                "bytes": len(encoded),
                "sha256": hashlib.sha256(encoded).hexdigest(),
                "line_count": len(text.splitlines()),
                "schema_ids": _schema_ids_from_text(text),
                "path_refs": _path_refs_from_text(text)[:30],
                "symbol_names": [item["name"] for item in symbols[:40]],
                "heading_titles": [item["text"] for item in headings[:40]],
                "top_terms": terms,
            }
        )
    aggregate_top_terms = [
        {"term": term, "count": count}
        for term, count in sorted(aggregate_terms.items(), key=lambda item: (-item[1], item[0]))[:term_limit]
    ]
    manifest_seed = json.dumps(
        [{"path": item.get("path"), "sha256": item.get("sha256")} for item in files if item.get("ok")],
        sort_keys=True,
    ).encode("utf-8")
    return _ok(
        "localIntelligenceLexicalIndexManifest",
        {
            "root_path": _repo_rel(requested_root, shell_root),
            "file_count": len(files),
            "total_bytes": total_bytes,
            "manifest_sha256": hashlib.sha256(manifest_seed).hexdigest(),
            "files": files,
            "aggregate_top_terms": aggregate_top_terms,
            "arbitrary_shell_authority": False,
            "exec_indexed_code": False,
            "network_authority": False,
            "content_returned": "manifest_only",
            "stored_index_written": False,
        },
    )


def _domain_weaver_swarm_skip_reason(path: Path, shell_root: Path) -> str | None:
    secret_reason = _shared_read_secret_reason(path, shell_root)
    if secret_reason:
        return secret_reason
    rel = _repo_rel(path, shell_root)
    for part in Path(rel).parts:
        if part.startswith("."):
            return f"hidden_path_part:{part}"
    return None


def _domain_weaver_swarm_resolve_root(shell_root: Path, requested: str | None) -> tuple[Path | None, dict[str, Any] | None]:
    rel = str(requested or DOMAIN_WEAVER_SWARM_EXPANSION_READ_ROOT).strip()
    if not rel:
        return None, _blocked("path_required", refusal_class="SCHEMA_INVALID")
    requested_root = (shell_root / rel).resolve(strict=False)
    allowed_root = (shell_root / DOMAIN_WEAVER_SWARM_EXPANSION_READ_ROOT).resolve(strict=False)
    if not _local_intelligence_is_under(requested_root, allowed_root):
        return None, _blocked(
            "path_not_allowed",
            refusal_class="PATH_NOT_ALLOWED",
            data={
                "path": rel,
                "allowed_root": DOMAIN_WEAVER_SWARM_EXPANSION_READ_ROOT,
                "read_root_policy": "domain_weaver_swarm_expansion_only",
            },
        )
    skip_reason = _domain_weaver_swarm_skip_reason(requested_root, shell_root)
    if skip_reason:
        return None, _blocked(
            "path_not_allowed",
            refusal_class="PATH_NOT_ALLOWED",
            data={"path": _repo_rel(requested_root, shell_root), "reason": skip_reason},
        )
    return requested_root, None


def _domain_weaver_swarm_kind(rel: str) -> str:
    path = Path(rel)
    parts = set(path.parts)
    lower = rel.lower()
    name_lower = path.name.lower()
    if "durable_carrier_ladder" in lower or "carrier_ladder" in lower:
        return "durable_carrier_ladder"
    if "relaunch" in lower and "plan" in lower:
        return "relaunch_plan"
    if "work_packets" in parts or path.name.startswith("PCKT-"):
        return "work_packet"
    if "returns" in parts or ".return." in name_lower:
        return "return"
    if "launch_receipts" in parts or "launch_receipt" in lower:
        return "launch_receipt"
    if "launch_logs" in parts or name_lower.endswith(".log"):
        return "launch_log"
    if "fanin" in parts:
        return "fanin"
    if "monitors" in parts or ".monitor." in name_lower:
        return "monitor"
    return "other"


def _domain_weaver_swarm_role_from_path_text(path: Path, text: str | None) -> str | None:
    if text:
        for pattern in (
            r'"role"\s*:\s*"([^"]+)"',
            r'"role_id"\s*:\s*"([^"]+)"',
            r"(?im)^\s*role\s*[:=]\s*[`\"']?([A-Za-z0-9_.:-]+)",
        ):
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip("`\"' ")
    name = path.name
    for suffix in (".return.candidate.md", ".return.md", ".monitor.candidate.md", ".monitor.md"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return None


def _domain_weaver_swarm_expected_return_refs(text: str | None) -> list[str]:
    if not text:
        return []
    refs: list[str] = []
    seen: set[str] = set()
    pattern = r"(?:ION/05_context/current/domain_weaver/swarm_expansion/)?wave0_batch_a/returns/[A-Za-z0-9_.:-]+\.return\.candidate\.md"
    for match in re.findall(pattern, text):
        ref = match
        if not ref.startswith("ION/"):
            ref = f"{DOMAIN_WEAVER_SWARM_EXPANSION_READ_ROOT}/{ref}"
        if ref not in seen:
            refs.append(ref)
            seen.add(ref)
    return refs


def _domain_weaver_swarm_record_hidden(
    hidden: list[dict[str, Any]],
    item: Path,
    shell_root: Path,
    reason: str,
    *,
    limit: int,
) -> None:
    if len(hidden) >= limit:
        return
    hidden.append(
        {
            "path": _repo_rel(item, shell_root),
            "reason": reason,
            "path_kind": "directory" if item.is_dir() else "file",
            "content_read": False,
        }
    )


def _domain_weaver_swarm_iter_files(
    requested_root: Path,
    *,
    shell_root: Path,
    max_files: int,
    hidden_scaffolding_detected: list[dict[str, Any]],
):
    allowed_suffixes = {".md", ".markdown", ".txt", ".json", ".yaml", ".yml", ".csv", ".log"}
    hidden_limit = 100
    if requested_root.is_file():
        skip_reason = _domain_weaver_swarm_skip_reason(requested_root, shell_root)
        if skip_reason:
            _domain_weaver_swarm_record_hidden(
                hidden_scaffolding_detected,
                requested_root,
                shell_root,
                skip_reason,
                limit=hidden_limit,
            )
            return
        if requested_root.suffix.lower() in allowed_suffixes:
            yield requested_root
        return

    yielded = 0
    stack = [requested_root]
    while stack:
        current = stack.pop()
        try:
            children = sorted(current.iterdir(), key=lambda item: item.as_posix())
        except OSError:
            continue
        child_dirs: list[Path] = []
        for item in children:
            skip_reason = _domain_weaver_swarm_skip_reason(item, shell_root)
            if skip_reason:
                _domain_weaver_swarm_record_hidden(
                    hidden_scaffolding_detected,
                    item,
                    shell_root,
                    skip_reason,
                    limit=hidden_limit,
                )
                continue
            if item.is_dir():
                child_dirs.append(item)
                continue
            if not item.is_file() or item.suffix.lower() not in allowed_suffixes:
                continue
            yield item
            yielded += 1
            if yielded >= max_files:
                return
        stack.extend(reversed(child_dirs))


def local_intelligence_domain_weaver_swarm_expansion_index(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    requested_root, blocked = _domain_weaver_swarm_resolve_root(
        shell_root,
        str(args.get("root_path") or args.get("path") or "").strip() or None,
    )
    if blocked:
        return blocked
    assert requested_root is not None
    max_files = max(1, min(int(args.get("max_files") or 300), 1000))
    entries: list[dict[str, Any]] = []
    hidden_scaffolding_detected: list[dict[str, Any]] = []
    expected_refs_from_text: list[str] = []
    seen_expected_refs: set[str] = set()

    for file_path in _domain_weaver_swarm_iter_files(
        requested_root,
        shell_root=shell_root,
        max_files=max_files,
        hidden_scaffolding_detected=hidden_scaffolding_detected,
    ):
        rel = _repo_rel(file_path, shell_root)
        stat = file_path.stat()
        text, error = _local_intelligence_read_py(file_path)
        schema_ids = _schema_ids_from_text(text) if text is not None else []
        for ref in _domain_weaver_swarm_expected_return_refs(text):
            if ref not in seen_expected_refs:
                expected_refs_from_text.append(ref)
                seen_expected_refs.add(ref)
        entry: dict[str, Any] = {
            "path": rel,
            "kind": _domain_weaver_swarm_kind(rel),
            "role": _domain_weaver_swarm_role_from_path_text(file_path, text),
            "size_bytes": stat.st_size,
            "sha256": _sha256_file_stream(file_path),
            "mtime_ns": stat.st_mtime_ns,
            "mtime": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            "schema_ids": schema_ids,
            "route_id_used": DOMAIN_WEAVER_SWARM_EXPANSION_INDEX_ROUTE_ID,
            "index_route_version": DOMAIN_WEAVER_SWARM_EXPANSION_INDEX_VERSION,
            "secret_scan_status": "not_scanned_by_index_route",
        }
        if text is not None:
            entry["line_count"] = len(text.splitlines())
        elif error:
            entry["text_read_finding"] = error
        entries.append(entry)

    expected_first_three_returns = expected_refs_from_text or list(DOMAIN_WEAVER_WAVE0A_EXPECTED_FIRST_THREE_RETURNS)
    expected_set = set(expected_first_three_returns)
    wave0_return_paths = sorted(
        entry["path"]
        for entry in entries
        if entry["kind"] == "return" and "/wave0_batch_a/returns/" in entry["path"]
    )
    present_return_set = set(wave0_return_paths)
    wave0_summary = {
        "expected_first_three_returns": expected_first_three_returns,
        "expected_first_three_returns_source": "artifact_refs" if expected_refs_from_text else "hardcoded_first_three_fallback",
        "present_expected_returns": [path for path in expected_first_three_returns if path in present_return_set],
        "missing_expected_returns": [path for path in expected_first_three_returns if path not in present_return_set],
        "unexpected_returns": [path for path in wave0_return_paths if path not in expected_set],
        "work_packet_count": sum(1 for entry in entries if entry["kind"] == "work_packet" and "/wave0_batch_a/" in entry["path"]),
        "launch_receipt_count": sum(1 for entry in entries if entry["kind"] == "launch_receipt" and "/wave0_batch_a/" in entry["path"]),
        "fanin_artifact_count": sum(1 for entry in entries if entry["kind"] == "fanin" and "/wave0_batch_a/" in entry["path"]),
        "hidden_scaffolding_detected": hidden_scaffolding_detected,
    }
    manifest_payload = {"entries": entries, "wave0_batch_a": wave0_summary}
    manifest_sha256 = hashlib.sha256(json.dumps(manifest_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return _ok(
        "localIntelligenceDomainWeaverSwarmExpansionIndex",
        {
            "route_id_used": DOMAIN_WEAVER_SWARM_EXPANSION_INDEX_ROUTE_ID,
            "index_route_version": DOMAIN_WEAVER_SWARM_EXPANSION_INDEX_VERSION,
            "root_path": _repo_rel(requested_root, shell_root),
            "entry_count": len(entries),
            "entries": entries,
            "wave0_batch_a": wave0_summary,
            "manifest_sha256": manifest_sha256,
            "arbitrary_shell_authority": False,
            "exec_indexed_code": False,
            "network_authority": False,
            "content_returned": "digest_entries_and_summary_only",
            "stored_index_written": False,
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "materialization_claim": False,
            "secrets_authority": False,
            "secret_content_read": False,
        },
    )


def _compact_text_excerpt(path: Path, root: Path, *, max_chars: int = 4000) -> dict[str, Any]:
    text, error = _local_intelligence_read_py(path)
    if error or text is None:
        return {"path": _repo_rel(path, root), "ok": False, "finding": error}
    excerpt = text[:max_chars]
    return {
        "path": _repo_rel(path, root),
        "ok": True,
        "bytes": len(text.encode("utf-8")),
        "line_count": len(text.splitlines()),
        "excerpt": excerpt,
        "truncated": len(text) > max_chars,
        "schema_ids": _schema_ids_from_text(text),
        "path_refs": _path_refs_from_text(text),
    }


def local_intelligence_context_pack_compile_plus(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    capsule_path, blocked = _local_intelligence_resolve_path(
        shell_root,
        str(args.get("capsule_path") or "").strip() or None,
        default="ION/05_context/current/chatgpt_connector/context_packages/ACTION_EVOLUTION_OPERATION_CONTEXT_CAPSULE_20260602.candidate.yaml",
    )
    if blocked:
        return blocked
    assert capsule_path is not None
    state_card_path, blocked = _local_intelligence_resolve_path(
        shell_root,
        str(args.get("state_card_path") or "").strip() or None,
        default="ION/05_context/current/chatgpt_connector/context_packages/ACTION_EVOLUTION_ACTIVE_STATE_CARD.md",
    )
    if blocked:
        return blocked
    assert state_card_path is not None
    receipt_limit = max(1, min(int(args.get("receipt_limit") or 1), 5))
    include_route_dag = bool(args.get("include_route_dag", True))
    include_receipt_graph = bool(args.get("include_receipt_graph", True))
    include_lexical_manifest = bool(args.get("include_lexical_manifest", True))
    capsule_excerpt = _compact_text_excerpt(capsule_path, shell_root, max_chars=5000)
    state_card_excerpt = _compact_text_excerpt(state_card_path, shell_root, max_chars=5000)
    suite_manifest = focused_test_suite_manifest(shell_root, {"include_receipts": True, "receipt_limit": receipt_limit})
    latest_status_by_suite: dict[str, Any] = {}
    for suite in suite_manifest.get("suites", []):
        recent = suite.get("recent_receipts") or []
        latest_status_by_suite[suite.get("suite_id")] = recent[0] if recent else None
    route_dag = None
    if include_route_dag:
        route_dag = local_intelligence_dag_extract(shell_root, {"dag_type": "action_route_dag", "branch_id": "local_intelligence"})
    receipt_graph = None
    if include_receipt_graph:
        receipt_graph = local_intelligence_receipt_graph(
            shell_root,
            {"receipt_dir": "ION/05_context/current/runtime_services/test_run_receipts", "query": "local_intelligence", "limit": 5},
        )
    local_intel_search = local_intelligence_local_search_plus(
        shell_root,
        {"path": "ION/04_packages/kernel/ion_runtime_service_control.py", "query": "local_intelligence_context", "max_files": 1, "max_line_hits": 10},
    )
    lexical_manifest = None
    if include_lexical_manifest:
        lexical_manifest = local_intelligence_lexical_index_manifest(
            shell_root,
            {"root_path": "ION/05_context/current/action_surface_cartography", "max_files": 20, "term_limit": 12},
        )
    next_recommended = [
        "Use chatgpt_native_validation.suite_manifest(include_receipts=true, receipt_limit=1) before new action work.",
        "Use runtime_services.runtime_freshness_probe after registry/handler patches and before assuming a route is stale.",
        "Use local_intelligence.local_search_plus/code_symbol_index for bounded local comprehension before spawning Codex.",
        "Reserve embeddings/vector search for a later explicit privacy/storage policy.",
    ]
    return _ok(
        "localIntelligenceContextPackCompilePlus",
        {
            "capsule": capsule_excerpt,
            "state_card": state_card_excerpt,
            "latest_status_by_suite": latest_status_by_suite,
            "suite_count": suite_manifest.get("suite_count"),
            "route_dag_summary": None if route_dag is None else {
                "node_count": route_dag.get("node_count"),
                "edge_count": route_dag.get("edge_count"),
                "nodes": route_dag.get("nodes", [])[:20],
                "edges": route_dag.get("edges", [])[:30],
            },
            "receipt_graph_summary": None if receipt_graph is None else {
                "processed_receipts": receipt_graph.get("processed_receipts"),
                "node_count": receipt_graph.get("node_count"),
                "edge_count": receipt_graph.get("edge_count"),
                "nodes": receipt_graph.get("nodes", [])[:20],
                "edges": receipt_graph.get("edges", [])[:30],
            },
            "local_intelligence_self_search": local_intel_search,
            "lexical_index_manifest_summary": None if lexical_manifest is None else {
                "root_path": lexical_manifest.get("root_path"),
                "file_count": lexical_manifest.get("file_count"),
                "total_bytes": lexical_manifest.get("total_bytes"),
                "manifest_sha256": lexical_manifest.get("manifest_sha256"),
                "aggregate_top_terms": lexical_manifest.get("aggregate_top_terms", [])[:12],
                "files": [
                    {
                        "path": item.get("path"),
                        "sha256": item.get("sha256"),
                        "schema_ids": item.get("schema_ids", []),
                        "heading_titles": item.get("heading_titles", [])[:8],
                        "top_terms": item.get("top_terms", [])[:8],
                    }
                    for item in lexical_manifest.get("files", [])[:20]
                ],
                "content_returned": lexical_manifest.get("content_returned"),
                "stored_index_written": lexical_manifest.get("stored_index_written"),
            },
            "next_recommended": next_recommended,
            "arbitrary_shell_authority": False,
            "exec_indexed_code": False,
            "network_authority": False,
            "content_returned": "compact_context_pack",
        },
    )


def _bounded_int(value: Any, *, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except Exception:
        parsed = default
    return max(minimum, min(parsed, maximum))


def _path_is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False


def _secret_path_reason(path: Path, root: Path) -> str | None:
    return _shared_read_secret_reason(path, root)


def _large_artifact_resolve_path(
    root: Path,
    requested: str | Path | None,
    *,
    default: str | None = None,
    require_file: bool = True,
) -> tuple[Path | None, dict[str, Any] | None]:
    requested_text = str(requested or default or "").strip()
    if not requested_text:
        return None, _blocked("path_required", refusal_class="SCHEMA_INVALID")
    raw = Path(requested_text).expanduser()
    path = raw.resolve(strict=False) if raw.is_absolute() else (root / raw).resolve(strict=False)
    allowed_roots = _shared_read_allowed_roots(root, LARGE_ARTIFACT_ALLOWED_ROOTS)
    if not any(_path_is_under(path, allowed_root) for allowed_root in allowed_roots):
        return None, _blocked(
            "path_not_allowed",
            refusal_class="PATH_NOT_ALLOWED",
            data={
                "path": requested_text,
                "allowed_roots": _shared_read_root_labels(root, LARGE_ARTIFACT_ALLOWED_ROOTS),
                "read_root_policy": "shared_manifest_active_ion_read_roots",
            },
        )
    secret_reason = _secret_path_reason(path, root)
    if secret_reason:
        return None, _blocked(
            "path_not_allowed",
            refusal_class="PATH_NOT_ALLOWED",
            data={"path": _repo_rel(path, root), "reason": secret_reason},
        )
    if require_file and not path.is_file():
        return None, _blocked("file_not_found", refusal_class="PATH_NOT_ALLOWED", data={"path": _repo_rel(path, root)})
    if not require_file and not path.exists():
        return None, _blocked("path_not_found", refusal_class="PATH_NOT_ALLOWED", data={"path": _repo_rel(path, root)})
    return path, None


def _sha256_file_stream(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _line_count_stream(path: Path) -> int:
    count = 0
    last = b""
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            count += chunk.count(b"\n")
            if chunk:
                last = chunk[-1:]
    if path.stat().st_size and last != b"\n":
        count += 1
    return count


def _guess_file_encoding(path: Path) -> dict[str, Any]:
    sample = path.read_bytes()[:8192]
    if b"\x00" in sample:
        return {"encoding": "binary", "binary": True}
    for encoding in ("utf-8", "utf-8-sig"):
        try:
            sample.decode(encoding)
            return {"encoding": encoding, "binary": False}
        except UnicodeDecodeError:
            continue
    return {"encoding": "latin-1", "binary": False}


def _decode_bytes(data: bytes, encoding: str) -> str:
    if encoding == "binary":
        return data.decode("utf-8", errors="replace")
    return data.decode(encoding or "utf-8", errors="replace")


def _line_number_for_byte(path: Path, byte_offset: int) -> int:
    if byte_offset <= 0:
        return 1
    count = 1
    remaining = byte_offset
    with path.open("rb") as handle:
        while remaining > 0:
            chunk = handle.read(min(65_536, remaining))
            if not chunk:
                break
            count += chunk.count(b"\n")
            remaining -= len(chunk)
    return count


def _stream_cursor(path: Path, root: Path, *, whole_sha256: str, chunk_size: int, chunk_index: int) -> str:
    payload = {
        "v": 1,
        "path": _repo_rel(path, root),
        "sha256": whole_sha256,
        "chunk_size_bytes": chunk_size,
        "chunk_index": chunk_index,
    }
    encoded = base64.urlsafe_b64encode(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).decode("ascii")
    return encoded.rstrip("=")


def _artifact_id(path: Path, root: Path, *, whole_sha256: str) -> str:
    payload = {"v": 1, "path": _repo_rel(path, root), "sha256": whole_sha256}
    encoded = base64.urlsafe_b64encode(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).decode("ascii")
    return encoded.rstrip("=")


def _decode_artifact_id(root: Path, artifact_id: str) -> tuple[Path | None, str | None, dict[str, Any] | None]:
    if not artifact_id:
        return None, None, _blocked("path_or_artifact_id_required", refusal_class="SCHEMA_INVALID")
    try:
        padded = artifact_id + "=" * (-len(artifact_id) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8"))
    except Exception as exc:
        return None, None, _blocked("artifact_id_invalid", refusal_class="SCHEMA_INVALID", data={"error": exc.__class__.__name__})
    if not isinstance(payload, Mapping):
        return None, None, _blocked("artifact_id_invalid", refusal_class="SCHEMA_INVALID")
    path, blocked = _large_artifact_resolve_path(root, str(payload.get("path") or ""), require_file=True)
    if blocked:
        return None, None, blocked
    assert path is not None
    whole_sha = _sha256_file_stream(path)
    if str(payload.get("sha256") or "") != whole_sha:
        return None, None, _blocked("artifact_id_file_sha_mismatch", refusal_class="CURSOR_STALE", data={"path": _repo_rel(path, root)})
    return path, whole_sha, None


def _decode_stream_cursor(root: Path, cursor: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not cursor:
        return None, _blocked("cursor_required", refusal_class="SCHEMA_INVALID")
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8"))
    except Exception as exc:
        return None, _blocked("cursor_invalid", refusal_class="SCHEMA_INVALID", data={"error": exc.__class__.__name__})
    if not isinstance(payload, Mapping):
        return None, _blocked("cursor_invalid", refusal_class="SCHEMA_INVALID")
    path, blocked = _large_artifact_resolve_path(root, str(payload.get("path") or ""), require_file=True)
    if blocked:
        return None, blocked
    assert path is not None
    whole_sha = _sha256_file_stream(path)
    if str(payload.get("sha256") or "") != whole_sha:
        return None, _blocked("cursor_file_sha_mismatch", refusal_class="CURSOR_STALE", data={"path": _repo_rel(path, root)})
    return {
        "path": path,
        "sha256": whole_sha,
        "chunk_size_bytes": _bounded_int(payload.get("chunk_size_bytes"), default=LARGE_ARTIFACT_DEFAULT_CHUNK_BYTES, minimum=1, maximum=LARGE_ARTIFACT_MAX_CHUNK_BYTES),
        "chunk_index": _bounded_int(payload.get("chunk_index"), default=0, minimum=0, maximum=10_000_000),
    }, None


def _chunk_payload(
    path: Path,
    root: Path,
    *,
    whole_sha256: str,
    chunk_size: int,
    chunk_index: int,
    max_response_bytes: int,
) -> dict[str, Any]:
    size = path.stat().st_size
    chunk_count = max(1, (size + chunk_size - 1) // chunk_size)
    byte_start = min(size, chunk_index * chunk_size)
    byte_end = min(size, byte_start + chunk_size)
    with path.open("rb") as handle:
        handle.seek(byte_start)
        raw = handle.read(max(0, byte_end - byte_start))
    hard_clip = len(raw) > max_response_bytes
    returned = raw[:max_response_bytes]
    encoding = _guess_file_encoding(path)["encoding"]
    line_start = _line_number_for_byte(path, byte_start)
    line_end = line_start + raw.count(b"\n")
    next_index = chunk_index + 1
    complete = next_index >= chunk_count
    return {
        "artifact_id": _artifact_id(path, root, whole_sha256=whole_sha256),
        "path": _repo_rel(path, root),
        "chunk_index": chunk_index,
        "chunk_count": chunk_count,
        "line_start": line_start,
        "line_end": line_end,
        "byte_start": byte_start,
        "byte_end": byte_end,
        "chunk_sha256": hashlib.sha256(raw).hexdigest(),
        "content": _decode_bytes(returned, encoding),
        "next_cursor": None if complete else _stream_cursor(path, root, whole_sha256=whole_sha256, chunk_size=chunk_size, chunk_index=next_index),
        "complete": complete,
        "truncated": hard_clip,
    }


def _read_line_slice(path: Path, *, start_line: int, line_count: int, max_bytes: int) -> tuple[str, int, int, bool]:
    lines: list[str] = []
    byte_total = 0
    end_line = start_line - 1
    truncated = False
    encoding = _guess_file_encoding(path)["encoding"]
    with path.open("rb") as handle:
        for index, raw_line in enumerate(handle, start=1):
            if index < start_line:
                continue
            if len(lines) >= line_count:
                break
            if byte_total + len(raw_line) > max_bytes:
                remaining = max(0, max_bytes - byte_total)
                if remaining:
                    lines.append(_decode_bytes(raw_line[:remaining], encoding))
                truncated = True
                end_line = index
                break
            lines.append(_decode_bytes(raw_line, encoding))
            byte_total += len(raw_line)
            end_line = index
    return "".join(lines), start_line, max(end_line, start_line), truncated


def _large_artifact_file_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return "python"
    if suffix == ".json":
        return "json"
    if suffix in {".yaml", ".yml"}:
        return "yaml"
    if suffix in {".md", ".markdown"}:
        return "markdown"
    if suffix == ".csv":
        return "csv"
    return suffix.lstrip(".") or "text"


def _read_text_for_parse(path: Path, *, max_bytes: int = LARGE_ARTIFACT_MAX_PARSE_BYTES) -> tuple[str | None, str | None]:
    if path.stat().st_size > max_bytes:
        return None, "file_over_parse_limit"
    encoding = _guess_file_encoding(path)
    if encoding.get("binary"):
        return None, "binary_file"
    try:
        return path.read_text(encoding=str(encoding.get("encoding") or "utf-8"), errors="replace"), None
    except Exception as exc:
        return None, exc.__class__.__name__


def _python_symbol_projection(text: str) -> dict[str, Any]:
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return {"parse_ok": False, "parse_error": f"SyntaxError:{exc.lineno}", "functions": [], "classes": [], "imports": [], "top_level_constants": []}
    functions: list[dict[str, Any]] = []
    classes: list[dict[str, Any]] = []
    imports: list[str] = []
    constants: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append({"name": node.name, "line_start": node.lineno, "line_end": getattr(node, "end_lineno", None), "async": isinstance(node, ast.AsyncFunctionDef)})
        elif isinstance(node, ast.ClassDef):
            classes.append({"name": node.name, "line_start": node.lineno, "line_end": getattr(node, "end_lineno", None)})
        elif isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append("." * int(node.level or 0) + str(node.module or ""))
    for node in tree.body:
        targets: list[Any] = []
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = list(getattr(node, "targets", []) or ([node.target] if getattr(node, "target", None) is not None else []))
        for target in targets:
            if isinstance(target, ast.Name) and target.id.isupper():
                constants.append(target.id)
    return {
        "parse_ok": True,
        "functions": sorted(functions, key=lambda item: (item["line_start"], item["name"]))[:200],
        "classes": sorted(classes, key=lambda item: (item["line_start"], item["name"]))[:120],
        "imports": sorted(set(imports))[:120],
        "top_level_constants": sorted(set(constants))[:120],
    }


def _secret_content_scan(path: Path, *, max_bytes: int = 262_144) -> dict[str, Any]:
    if not path.is_file():
        return {"scanned": False, "high_risk_match_count": 0, "secret_values_returned": False}
    try:
        sample = path.read_bytes()[:max_bytes].decode("utf-8", errors="replace")
    except Exception:
        return {"scanned": False, "high_risk_match_count": 0, "secret_values_returned": False}
    patterns = [
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|password)\b\s*[:=]",
        r"ya29\.[0-9A-Za-z_.-]{20,}",
        r"AIza[0-9A-Za-z_-]{20,}",
    ]
    count = sum(len(re.findall(pattern, sample)) for pattern in patterns)
    return {
        "scanned": True,
        "sample_bytes": min(path.stat().st_size, max_bytes),
        "high_risk_match_count": count,
        "secret_values_returned": False,
    }


def large_file_profile(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    path, blocked = _large_artifact_resolve_path(shell_root, args.get("path"), require_file=True)
    if blocked:
        return blocked
    assert path is not None
    stat = path.stat()
    whole_sha = _sha256_file_stream(path)
    line_count = _line_count_stream(path)
    file_type = _large_artifact_file_type(path)
    text, parse_error = _read_text_for_parse(path)
    profile: dict[str, Any] = {}
    if text is not None:
        profile["schema_ids"] = _schema_ids_from_text(text)
        profile["path_refs"] = _path_refs_from_text(text)[:40]
        if file_type == "markdown":
            md = _profile_markdown_text(text)
            profile["heading_count"] = md.get("heading_count")
            profile["headings"] = md.get("headings", [])[:30]
        elif file_type == "json":
            json_profile = _profile_json_text(text)
            profile["json_profile"] = json_profile
            try:
                loaded = json.loads(text)
                profile["top_level_keys"] = list(loaded.keys())[:60] if isinstance(loaded, dict) else []
            except Exception:
                profile["top_level_keys"] = []
        elif file_type == "yaml":
            yaml_profile = _profile_yaml_text(text)
            profile["yaml_profile"] = yaml_profile
            profile["top_level_keys"] = [item["key"] for item in yaml_profile.get("top_keys", [])[:60]]
        elif file_type == "python":
            symbols = _python_symbol_projection(text)
            profile["symbol_counts"] = {
                "functions": len(symbols.get("functions", [])),
                "classes": len(symbols.get("classes", [])),
                "imports": len(symbols.get("imports", [])),
                "top_level_constants": len(symbols.get("top_level_constants", [])),
            }
    else:
        profile["parse_error"] = parse_error
    return _ok(
        "largeFileProfile",
        {
            "path": _repo_rel(path, shell_root),
            "size_bytes": stat.st_size,
            "line_count": line_count,
            "sha256": whole_sha,
            "file_type": file_type,
            "encoding_guess": _guess_file_encoding(path),
            "oversize": stat.st_size > LARGE_ARTIFACT_OVERSIZE_BYTES,
            "profile": profile,
            "secret_scan": _secret_content_scan(path),
            "recommended_next_routes": [
                "large_artifact_intelligence.large_file_chunk_manifest",
                "large_artifact_intelligence.large_file_anchor_search",
                "large_artifact_intelligence.large_file_slice_read",
                "large_artifact_intelligence.large_file_stream_start",
            ],
            "content_returned": "metadata_only",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def large_file_chunk_manifest(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    path, blocked = _large_artifact_resolve_path(shell_root, args.get("path"), require_file=True)
    if blocked:
        return blocked
    assert path is not None
    chunk_size = _bounded_int(args.get("chunk_size_bytes"), default=LARGE_ARTIFACT_DEFAULT_CHUNK_BYTES, minimum=1024, maximum=LARGE_ARTIFACT_MAX_CHUNK_BYTES)
    size = path.stat().st_size
    whole_sha = _sha256_file_stream(path)
    chunk_count = max(1, (size + chunk_size - 1) // chunk_size)
    chunks: list[dict[str, Any]] = []
    max_chunks = _bounded_int(args.get("max_chunks"), default=200, minimum=1, maximum=500)
    with path.open("rb") as handle:
        for index in range(min(chunk_count, max_chunks)):
            byte_start = index * chunk_size
            byte_end = min(size, byte_start + chunk_size)
            handle.seek(byte_start)
            raw = handle.read(max(0, byte_end - byte_start))
            line_start = _line_number_for_byte(path, byte_start)
            chunks.append(
                {
                    "chunk_id": f"{whole_sha[:12]}:{index}",
                    "index": index,
                    "line_start": line_start,
                    "line_end": line_start + raw.count(b"\n"),
                    "byte_start": byte_start,
                    "byte_end": byte_end,
                    "chunk_sha256": hashlib.sha256(raw).hexdigest(),
                    "hint": "",
                }
            )
    return _ok(
        "largeFileChunkManifest",
        {
            "path": _repo_rel(path, shell_root),
            "whole_file_sha256": whole_sha,
            "size_bytes": size,
            "chunk_size_bytes": chunk_size,
            "chunk_count": chunk_count,
            "returned_chunk_count": len(chunks),
            "chunks": chunks,
            "next_cursor": None if len(chunks) >= chunk_count else _stream_cursor(path, shell_root, whole_sha256=whole_sha, chunk_size=chunk_size, chunk_index=len(chunks)),
            "previous_cursor": None,
            "content_returned": "manifest_only",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def large_file_slice_read(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    path, blocked = _large_artifact_resolve_path(shell_root, args.get("path"), require_file=True)
    if blocked:
        return blocked
    assert path is not None
    start_line = _bounded_int(args.get("start_line"), default=1, minimum=1, maximum=100_000_000)
    line_count = _bounded_int(args.get("line_count"), default=80, minimum=1, maximum=1000)
    max_bytes = _bounded_int(args.get("max_bytes"), default=LARGE_ARTIFACT_MAX_RESPONSE_BYTES, minimum=1, maximum=LARGE_ARTIFACT_MAX_RESPONSE_BYTES)
    content, actual_start, actual_end, truncated = _read_line_slice(path, start_line=start_line, line_count=line_count, max_bytes=max_bytes)
    return _ok(
        "largeFileSliceRead",
        {
            "path": _repo_rel(path, shell_root),
            "source_range": {"start_line": actual_start, "end_line": actual_end, "requested_line_count": line_count},
            "content": content,
            "slice_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "whole_file_sha256": _sha256_file_stream(path),
            "truncated": truncated,
            "content_returned": "bounded_slice",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def large_file_stream_start(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    path, blocked = _large_artifact_resolve_path(shell_root, args.get("path"), require_file=True)
    if blocked:
        return blocked
    assert path is not None
    chunk_size = _bounded_int(args.get("chunk_size_bytes"), default=LARGE_ARTIFACT_DEFAULT_CHUNK_BYTES, minimum=1024, maximum=LARGE_ARTIFACT_MAX_CHUNK_BYTES)
    size = path.stat().st_size
    whole_sha = _sha256_file_stream(path)
    chunk_count = max(1, (size + chunk_size - 1) // chunk_size)
    return _ok(
        "largeFileStreamStart",
        {
            "artifact_id": _artifact_id(path, shell_root, whole_sha256=whole_sha),
            "path": _repo_rel(path, shell_root),
            "whole_sha256": whole_sha,
            "size_bytes": size,
            "line_count": _line_count_stream(path),
            "chunk_size_bytes": chunk_size,
            "chunk_count": chunk_count,
            "cursor": _stream_cursor(path, shell_root, whole_sha256=whole_sha, chunk_size=chunk_size, chunk_index=0),
            "recommended_next": "large_artifact_intelligence.large_file_stream_next",
            "content_returned": "stream_cursor_only",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def large_file_stream_next(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    cursor_payload, blocked = _decode_stream_cursor(shell_root, str(args.get("cursor") or ""))
    if blocked:
        return blocked
    assert cursor_payload is not None
    max_response_bytes = _bounded_int(args.get("max_response_bytes"), default=LARGE_ARTIFACT_MAX_RESPONSE_BYTES, minimum=1, maximum=LARGE_ARTIFACT_MAX_RESPONSE_BYTES)
    payload = _chunk_payload(
        cursor_payload["path"],
        shell_root,
        whole_sha256=str(cursor_payload["sha256"]),
        chunk_size=int(cursor_payload["chunk_size_bytes"]),
        chunk_index=int(cursor_payload["chunk_index"]),
        max_response_bytes=max_response_bytes,
    )
    return _ok(
        "largeFileStreamNext",
        {
            **payload,
            "content_returned": "bounded_stream_chunk",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def large_file_stream_range(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    path: Path | None = None
    whole_sha: str | None = None
    if str(args.get("path") or "").strip():
        path, blocked = _large_artifact_resolve_path(shell_root, args.get("path"), require_file=True)
        if blocked:
            return blocked
        assert path is not None
        whole_sha = _sha256_file_stream(path)
    else:
        path, whole_sha, blocked = _decode_artifact_id(shell_root, str(args.get("artifact_id") or ""))
        if blocked:
            return blocked
    assert path is not None and whole_sha is not None
    chunk_size = _bounded_int(args.get("chunk_size_bytes"), default=LARGE_ARTIFACT_DEFAULT_CHUNK_BYTES, minimum=1024, maximum=LARGE_ARTIFACT_MAX_CHUNK_BYTES)
    chunk_start = _bounded_int(args.get("chunk_start"), default=0, minimum=0, maximum=10_000_000)
    chunk_count = _bounded_int(args.get("chunk_count"), default=1, minimum=1, maximum=5)
    chunks = [
        _chunk_payload(path, shell_root, whole_sha256=whole_sha, chunk_size=chunk_size, chunk_index=index, max_response_bytes=LARGE_ARTIFACT_MAX_RESPONSE_BYTES)
        for index in range(chunk_start, chunk_start + chunk_count)
        if index * chunk_size < path.stat().st_size
    ]
    return _ok(
        "largeFileStreamRange",
        {
            "path": _repo_rel(path, shell_root),
            "whole_file_sha256": whole_sha,
            "chunk_start": chunk_start,
            "requested_chunk_count": chunk_count,
            "chunks": chunks,
            "content_returned": "bounded_stream_chunks",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def large_file_anchor_search(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    path, blocked = _large_artifact_resolve_path(shell_root, args.get("path"), require_file=True)
    if blocked:
        return blocked
    assert path is not None
    query = str(args.get("query") or args.get("anchor") or "").strip()
    if not query:
        return _blocked("query_required", refusal_class="SCHEMA_INVALID")
    max_hits = _bounded_int(args.get("max_hits"), default=20, minimum=1, maximum=100)
    query_lower = query.lower()
    hits: list[dict[str, Any]] = []
    encoding = _guess_file_encoding(path)["encoding"]
    with path.open("rb") as handle:
        for line_no, raw_line in enumerate(handle, start=1):
            line = _decode_bytes(raw_line, encoding)
            if query_lower in line.lower():
                preview = line.strip()
                hits.append(
                    {
                        "line": line_no,
                        "preview": preview[:240],
                        "recommended_slice_args": {"path": _repo_rel(path, shell_root), "start_line": max(1, line_no - 3), "line_count": 8},
                    }
                )
                if len(hits) >= max_hits:
                    break
    return _ok(
        "largeFileAnchorSearch",
        {
            "path": _repo_rel(path, shell_root),
            "query": query,
            "hit_count": len(hits),
            "hits": hits,
            "content_returned": "compact_hits_only",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def large_file_symbol_index(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    path, blocked = _large_artifact_resolve_path(shell_root, args.get("path"), require_file=True)
    if blocked:
        return blocked
    assert path is not None
    if path.suffix.lower() != ".py":
        return _blocked("python_file_required", refusal_class="SCHEMA_INVALID", data={"path": _repo_rel(path, shell_root)})
    text, error = _read_text_for_parse(path)
    if error or text is None:
        return _blocked("symbol_index_read_failed", refusal_class="SYMBOL_INDEX_READ_FAILED", data={"path": _repo_rel(path, shell_root), "finding": error})
    symbols = _python_symbol_projection(text)
    return _ok(
        "largeFileSymbolIndex",
        {
            "path": _repo_rel(path, shell_root),
            **symbols,
            "exec_indexed_code": False,
            "content_returned": "ast_symbol_map_only",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def _json_path_segments(path_expr: str) -> list[tuple[str, tuple[int | None, int | None] | None]]:
    if not path_expr:
        return []
    segments: list[tuple[str, tuple[int | None, int | None] | None]] = []
    for part in path_expr.split("."):
        match = re.fullmatch(r"([A-Za-z0-9_-]+)(?:\[(\d*)(?::(\d*))?\])?", part.strip())
        if not match:
            raise ValueError("unsupported_path_segment")
        key = match.group(1)
        if match.group(2) is None:
            segments.append((key, None))
            continue
        start = int(match.group(2)) if match.group(2) else None
        end = int(match.group(3)) if match.group(3) else None
        segments.append((key, (start, end)))
    return segments


def _bounded_json_value(value: Any, *, depth: int = 0, limit: int = 20) -> Any:
    if depth >= 4:
        if isinstance(value, dict):
            return {"type": "object", "key_count": len(value)}
        if isinstance(value, list):
            return {"type": "array", "item_count": len(value)}
        return value
    if isinstance(value, dict):
        items = list(value.items())[:limit]
        return {str(key): _bounded_json_value(child, depth=depth + 1, limit=limit) for key, child in items}
    if isinstance(value, list):
        return [_bounded_json_value(child, depth=depth + 1, limit=limit) for child in value[:limit]]
    return value


def large_file_json_path_read(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    path, blocked = _large_artifact_resolve_path(shell_root, args.get("path"), require_file=True)
    if blocked:
        return blocked
    assert path is not None
    if path.suffix.lower() != ".json":
        return _blocked("json_file_required", refusal_class="SCHEMA_INVALID", data={"path": _repo_rel(path, shell_root)})
    text, error = _read_text_for_parse(path)
    if error or text is None:
        return _blocked("json_read_failed", refusal_class="JSON_READ_FAILED", data={"path": _repo_rel(path, shell_root), "finding": error})
    try:
        data = json.loads(text)
        current: Any = data
        for key, array_slice in _json_path_segments(str(args.get("json_path") or args.get("path_expr") or "")):
            if not isinstance(current, dict) or key not in current:
                return _blocked("json_path_not_found", refusal_class="JSON_PATH_NOT_FOUND", data={"json_path": str(args.get("json_path") or "")})
            current = current[key]
            if array_slice is not None:
                if not isinstance(current, list):
                    return _blocked("json_path_slice_target_not_array", refusal_class="JSON_PATH_NOT_FOUND")
                start, end = array_slice
                current = current[start or 0 : end]
        if isinstance(current, list):
            offset = _bounded_int(args.get("offset"), default=0, minimum=0, maximum=1_000_000)
            limit = _bounded_int(args.get("limit"), default=20, minimum=1, maximum=100)
            current = current[offset : offset + limit]
    except ValueError as exc:
        return _blocked("json_path_invalid", refusal_class="SCHEMA_INVALID", data={"error": str(exc)})
    except Exception as exc:
        return _blocked("json_parse_failed", refusal_class="JSON_PARSE_FAILED", data={"error": exc.__class__.__name__})
    return _ok(
        "largeFileJsonPathRead",
        {
            "path": _repo_rel(path, shell_root),
            "json_path": str(args.get("json_path") or args.get("path_expr") or ""),
            "whole_file_sha256": _sha256_file_stream(path),
            "subtree": _bounded_json_value(current, limit=_bounded_int(args.get("limit"), default=20, minimum=1, maximum=100)),
            "content_returned": "bounded_json_subtree",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def large_file_section_read(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    path, blocked = _large_artifact_resolve_path(shell_root, args.get("path"), require_file=True)
    if blocked:
        return blocked
    assert path is not None
    heading = str(args.get("heading") or "").strip()
    if not heading:
        return _blocked("heading_required", refusal_class="SCHEMA_INVALID")
    text, error = _read_text_for_parse(path)
    if error or text is None:
        return _blocked("section_read_failed", refusal_class="SECTION_READ_FAILED", data={"path": _repo_rel(path, shell_root), "finding": error})
    lines = text.splitlines(keepends=True)
    found_index: int | None = None
    found_level = 0
    for index, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.*)$", line)
        if match and match.group(2).strip().lower() == heading.lower():
            found_index = index
            found_level = len(match.group(1))
            break
    if found_index is None:
        return _blocked("heading_not_found", refusal_class="SECTION_NOT_FOUND", data={"heading": heading})
    include_children = bool(args.get("include_children", True))
    end_index = len(lines)
    for index in range(found_index + 1, len(lines)):
        match = re.match(r"^(#{1,6})\s+", lines[index])
        if match and (include_children is False or len(match.group(1)) <= found_level):
            end_index = index
            break
    max_bytes = _bounded_int(args.get("max_bytes"), default=LARGE_ARTIFACT_MAX_RESPONSE_BYTES, minimum=1, maximum=LARGE_ARTIFACT_MAX_RESPONSE_BYTES)
    section_bytes = "".join(lines[found_index:end_index]).encode("utf-8")
    returned = section_bytes[:max_bytes].decode("utf-8", errors="replace")
    return _ok(
        "largeFileSectionRead",
        {
            "path": _repo_rel(path, shell_root),
            "heading": heading,
            "heading_path": [heading],
            "line_range": {"start_line": found_index + 1, "end_line": end_index},
            "section_text": returned,
            "truncated": len(section_bytes) > max_bytes,
            "whole_file_sha256": _sha256_file_stream(path),
            "content_returned": "bounded_section",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def large_artifact_claim_check(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    claim = str(args.get("claim") or "").strip()
    refs = args.get("evidence_refs") if isinstance(args.get("evidence_refs"), list) else []
    if not claim:
        return _blocked("claim_required", refusal_class="SCHEMA_INVALID")
    cited_ranges: list[dict[str, Any]] = []
    evidence_text = ""
    for ref in refs[:10]:
        if not isinstance(ref, Mapping):
            continue
        path, blocked = _large_artifact_resolve_path(shell_root, ref.get("path"), require_file=True)
        if blocked or path is None:
            continue
        start_line = _bounded_int(ref.get("start_line"), default=1, minimum=1, maximum=100_000_000)
        line_count = _bounded_int(ref.get("line_count"), default=20, minimum=1, maximum=200)
        content, actual_start, actual_end, _truncated = _read_line_slice(path, start_line=start_line, line_count=line_count, max_bytes=20_000)
        evidence_text += "\n" + content
        cited_ranges.append({"path": _repo_rel(path, shell_root), "start_line": actual_start, "end_line": actual_end, "sha256": _sha256_file_stream(path)})
    claim_lower = claim.lower()
    evidence_lower = evidence_text.lower()
    terms = [term for term in re.findall(r"[a-z0-9_]{4,}", claim_lower) if term not in {"that", "this", "with", "from"}]
    matched_terms = [term for term in sorted(set(terms)) if term in evidence_lower]
    strong_matched_terms = [term for term in matched_terms if "_" in term or len(term) >= 8]
    if claim_lower and claim_lower in evidence_lower:
        status = "supported"
    elif strong_matched_terms:
        status = "supported"
    elif terms and len(matched_terms) >= max(2, len(set(terms)) // 2):
        status = "supported"
    elif evidence_text:
        status = "insufficient"
    else:
        status = "insufficient"
    return _ok(
        "largeArtifactClaimCheck",
        {
            "claim": claim,
            "candidate_support_status": status,
            "matched_terms": matched_terms[:30],
            "cited_source_ranges": cited_ranges,
            "uncertainty_notes": ["Lexical candidate check only; not accepted-state authority."],
            "content_returned": "source_range_assessment_only",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def _artifact_transfer_inputs(args: Mapping[str, Any]) -> list[str]:
    paths = args.get("paths")
    roots = args.get("roots")
    raw = paths if isinstance(paths, list) else roots if isinstance(roots, list) else []
    return [str(item).strip() for item in raw if str(item).strip()]


def _artifact_transfer_package_id(label: str, included_paths: list[str], idempotency_key: str | None = None) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", label.strip().lower() or "artifact-package").strip("-")[:48] or "artifact-package"
    seed = json.dumps({"label": label, "paths": sorted(included_paths), "idempotency_key": idempotency_key or ""}, sort_keys=True)
    return f"{slug}-{hashlib.sha256(seed.encode('utf-8')).hexdigest()[:12]}"


def _artifact_transfer_collect(root: Path, args: Mapping[str, Any]) -> dict[str, Any]:
    requested = _artifact_transfer_inputs(args)
    max_bytes = _bounded_int(args.get("max_bytes"), default=ARTIFACT_TRANSFER_DEFAULT_MAX_BYTES, minimum=1, maximum=25_000_000)
    included: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    total_bytes = 0
    if not requested:
        return {"ok": False, "finding": "paths_required", "included": [], "excluded": [], "estimated_bytes": 0, "max_bytes": max_bytes}
    candidates: list[Path] = []
    for item in requested:
        path, blocked = _large_artifact_resolve_path(root, item, require_file=False)
        if blocked or path is None:
            excluded.append({"path": item, "reason": (blocked or {}).get("refusal_class", "PATH_NOT_ALLOWED")})
            continue
        if path.is_file():
            candidates.append(path)
        else:
            for child in sorted(path.rglob("*")):
                if child.is_file():
                    candidates.append(child)
    seen: set[str] = set()
    for path in candidates:
        rel = _repo_rel(path, root)
        if rel in seen:
            continue
        seen.add(rel)
        reason = _secret_path_reason(path, root)
        if reason:
            excluded.append({"path": rel, "reason": reason})
            continue
        secret_scan = _secret_content_scan(path)
        if int(secret_scan.get("high_risk_match_count") or 0) > 0:
            excluded.append({"path": rel, "reason": "content_secret_heuristic_match", "secret_values_returned": False})
            continue
        size = path.stat().st_size
        if len(included) >= ARTIFACT_TRANSFER_MAX_FILE_COUNT:
            excluded.append({"path": rel, "reason": "file_count_limit"})
            continue
        if total_bytes + size > max_bytes:
            excluded.append({"path": rel, "reason": "max_bytes_limit", "size_bytes": size})
            continue
        included.append({"path": rel, "abs_path": path, "size_bytes": size, "sha256": _sha256_file_stream(path)})
        total_bytes += size
    return {"ok": True, "included": included, "excluded": excluded, "estimated_bytes": total_bytes, "max_bytes": max_bytes}


def zip_request_preview(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    collected = _artifact_transfer_collect(shell_root, args)
    included = [{key: value for key, value in item.items() if key != "abs_path"} for item in collected.get("included", [])]
    package_label = str(args.get("package_label") or "artifact-package")
    package_id = _artifact_transfer_package_id(package_label, [item["path"] for item in included])
    return _ok(
        "zipRequestPreview",
        {
            "package_id": package_id,
            "package_label": package_label,
            "estimated_file_count": len(included),
            "estimated_bytes": collected.get("estimated_bytes", 0),
            "max_bytes": collected.get("max_bytes"),
            "included_files": included,
            "included_roots": _artifact_transfer_inputs(args),
            "excluded_paths": collected.get("excluded", []),
            "would_create_zip": False,
            "requires_confirmation_for_materialization": True,
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def zip_materialize_request(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    _confirmation, idempotency_key, blocked = _mutation_fields(args)
    if blocked:
        return blocked
    collected = _artifact_transfer_collect(shell_root, args)
    if collected.get("ok") is not True:
        return _blocked(str(collected.get("finding") or "zip_request_invalid"), refusal_class="SCHEMA_INVALID")
    included = collected.get("included", [])
    safe_files = [item for item in included if isinstance(item.get("abs_path"), Path)]
    package_label = str(args.get("package_label") or "artifact-package")
    package_id = _artifact_transfer_package_id(package_label, [str(item["path"]) for item in safe_files], idempotency_key=idempotency_key)
    package_dir = shell_root / ARTIFACT_TRANSFER_DIR / "packages"
    manifest_dir = shell_root / ARTIFACT_TRANSFER_DIR / "manifests"
    receipt_dir = shell_root / ARTIFACT_TRANSFER_DIR / "receipts"
    for directory in (package_dir, manifest_dir, receipt_dir):
        directory.mkdir(parents=True, exist_ok=True)
    zip_path = package_dir / f"{package_id}.zip"
    manifest_path = manifest_dir / f"{package_id}.json"
    receipt_path = receipt_dir / f"{package_id}.json"
    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in safe_files:
            archive.write(item["abs_path"], arcname=str(item["path"]))
    package_sha = _sha256_file_stream(zip_path)
    manifest = {
        "schema_id": "ion.artifact_transfer_manifest.v0_1_candidate",
        "package_id": package_id,
        "package_label": package_label,
        "created_at": _now(),
        "zip_path": _repo_rel(zip_path, shell_root),
        "package_sha256": package_sha,
        "estimated_bytes": collected.get("estimated_bytes", 0),
        "file_count": len(safe_files),
        "files": [{key: value for key, value in item.items() if key != "abs_path"} for item in safe_files],
        "excluded_paths": collected.get("excluded", []),
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "sandbox_upload_performed": False,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest_sha = _sha256_file_stream(manifest_path)
    receipt = {
        "schema_id": "ion.artifact_transfer_receipt.v0_1_candidate",
        "package_id": package_id,
        "idempotency_key": idempotency_key,
        "created_at": _now(),
        "manifest_path": _repo_rel(manifest_path, shell_root),
        "zip_path": _repo_rel(zip_path, shell_root),
        "package_sha256": package_sha,
        "manifest_sha256": manifest_sha,
        "file_count": len(safe_files),
        "excluded_count": len(collected.get("excluded", [])),
        "sandbox_upload_performed": False,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return _ok(
        "zipMaterializeRequest",
        {
            "package_id": package_id,
            "zip_path": _repo_rel(zip_path, shell_root),
            "manifest_path": _repo_rel(manifest_path, shell_root),
            "receipt_path": _repo_rel(receipt_path, shell_root),
            "package_sha256": package_sha,
            "manifest_sha256": manifest_sha,
            "file_count": len(safe_files),
            "excluded_paths": collected.get("excluded", []),
            "mutates_active_state": True,
            "accepted_state_claim": False,
            "secrets_authority": False,
            "sandbox_upload_performed": False,
        },
    )


def _artifact_manifest_path(root: Path, args: Mapping[str, Any]) -> tuple[Path | None, dict[str, Any] | None]:
    package_id = str(args.get("package_id") or "").strip()
    manifest_path_arg = str(args.get("manifest_path") or "").strip()
    if package_id:
        path = (root / ARTIFACT_TRANSFER_DIR / "manifests" / f"{package_id}.json").resolve(strict=False)
    elif manifest_path_arg:
        path = (root / manifest_path_arg).resolve(strict=False)
    else:
        return None, _blocked("package_id_or_manifest_path_required", refusal_class="SCHEMA_INVALID")
    allowed = (root / ARTIFACT_TRANSFER_DIR / "manifests").resolve(strict=False)
    if not _path_is_under(path, allowed):
        return None, _blocked("manifest_path_not_allowed", refusal_class="PATH_NOT_ALLOWED")
    if not path.is_file():
        return None, _blocked("manifest_not_found", refusal_class="PATH_NOT_ALLOWED", data={"path": _repo_rel(path, root)})
    return path, None


def zip_manifest_read(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    manifest_path, blocked = _artifact_manifest_path(shell_root, args)
    if blocked:
        return blocked
    assert manifest_path is not None
    loaded = _read_json_file(manifest_path)
    if loaded.get("ok") is not True:
        return _blocked("manifest_read_failed", refusal_class="MANIFEST_READ_FAILED", data=loaded)
    data = loaded.get("data") if isinstance(loaded.get("data"), Mapping) else {}
    return _ok(
        "zipManifestRead",
        {
            "manifest_path": _repo_rel(manifest_path, shell_root),
            "manifest_sha256": _sha256_file_stream(manifest_path),
            "manifest": data,
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
            "sandbox_upload_performed": False,
        },
    )


def sandbox_upload_instruction(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    manifest = zip_manifest_read(root, args)
    if manifest.get("ok") is not True:
        return manifest
    data = manifest.get("manifest") if isinstance(manifest.get("manifest"), Mapping) else {}
    return _ok(
        "sandboxUploadInstruction",
        {
            "package_id": data.get("package_id"),
            "zip_path": data.get("zip_path"),
            "manifest_path": manifest.get("manifest_path"),
            "instruction": "Upload this zip to the current ChatGPT thread.",
            "upload_performed": False,
            "would_upload": False,
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def sandbox_intake_manifest_preview(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    manifest = zip_manifest_read(root, args)
    if manifest.get("ok") is not True:
        return manifest
    data = manifest.get("manifest") if isinstance(manifest.get("manifest"), Mapping) else {}
    return _ok(
        "sandboxIntakeManifestPreview",
        {
            "package_id": data.get("package_id"),
            "expected_sandbox_steps": [
                "Unzip package in sandbox workspace.",
                "Verify package_sha256 and per-file sha256s against manifest.",
                "Use manifest file list as source bounds for reads.",
            ],
            "would_process_sandbox": False,
            "upload_performed": False,
            "accepted_state_claim": False,
            "mutates_active_state": False,
            "secrets_authority": False,
        },
    )


def inference_provider_status(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    _shell_root = _resolve_root(root)
    codex_bin = shutil.which("codex")
    gemini_bin = shutil.which("gemini")
    ollama_bin = shutil.which("ollama")
    return _ok(
        "inferenceProviderStatus",
        {
            "providers": {
                "codex_cli": {
                    "binary_present": bool(codex_bin),
                    "binary_path": codex_bin or "",
                    "configured_known_without_secret_read": False,
                    "would_call_model": False,
                },
                "codex_spark_preview": {
                    "route_preview_available": True,
                    "default_model_call_enabled": False,
                    "would_call_model": False,
                },
                "gemini_cli": {
                    "binary_present": bool(gemini_bin),
                    "binary_path": gemini_bin or "",
                    "config_known_without_secret_read": False,
                    "network_required_for_cloud": True,
                    "would_call_model": False,
                },
                "local_ollama": {
                    "binary_present": bool(ollama_bin),
                    "binary_path": ollama_bin or "",
                    "model_inventory_checked": False,
                    "would_call_model": False,
                },
            },
            "secrets_exposed": False,
            "config_files_read": False,
            "network_used": False,
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def inference_plan_preview(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    path, blocked = _large_artifact_resolve_path(shell_root, args.get("path"), require_file=True)
    if blocked:
        return blocked
    assert path is not None
    provider = str(args.get("provider") or "codex_spark_preview")
    task = str(args.get("task") or "summarize_or_index_large_artifact")
    secret_scan = _secret_content_scan(path)
    external = provider in {"gemini_cli", "codex_cli", "codex_spark_preview"}
    return _ok(
        "inferencePlanPreview",
        {
            "path": _repo_rel(path, shell_root),
            "size_bytes": path.stat().st_size,
            "task": task,
            "provider_candidate": provider,
            "privacy_class": "local_repo_candidate",
            "would_send_full_text": False,
            "redaction_secret_scan_summary": secret_scan,
            "requires_operator_approval_if_cloud_or_external": external,
            "would_call_model": False,
            "network_used": False,
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
            "recommended_source_routes": [
                "large_artifact_intelligence.large_file_profile",
                "large_artifact_intelligence.large_file_chunk_manifest",
                "large_artifact_intelligence.large_file_slice_read",
            ],
        },
    )


def large_artifact_inference_index_preview(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    plan = inference_plan_preview(root, {**dict(args), "task": str(args.get("task") or "large_artifact_index")})
    if plan.get("ok") is not True:
        return plan
    return _ok(
        "largeArtifactInferenceIndexPreview",
        {
            "plan": plan,
            "index_strategy": "chunk_then_summarize_preview_only",
            "would_write_index": False,
            "would_call_model": False,
            "accepted_state_claim": False,
            "mutates_active_state": False,
            "secrets_authority": False,
        },
    )


def large_artifact_inference_question_preview(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    plan = inference_plan_preview(root, {**dict(args), "task": str(args.get("task") or "question_answer_over_large_artifact")})
    if plan.get("ok") is not True:
        return plan
    question = str(args.get("question") or "").strip()
    return _ok(
        "largeArtifactInferenceQuestionPreview",
        {
            "question": question,
            "plan": plan,
            "evidence_plan": [
                "Run large_file_anchor_search for question terms.",
                "Read bounded source slices around hits.",
                "Use large_artifact_claim_check before presenting a claim as supported.",
            ],
            "would_call_model": False,
            "would_send_full_text": False,
            "accepted_state_claim": False,
            "mutates_active_state": False,
            "secrets_authority": False,
        },
    )


def _read_json_file(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"ok": False, "finding": "file_not_found", "path": path.as_posix()}
    except json.JSONDecodeError as exc:
        return {"ok": False, "finding": "json_decode_error", "path": path.as_posix(), "line": exc.lineno}
    if not isinstance(data, dict):
        return {"ok": False, "finding": "json_root_not_object", "path": path.as_posix()}
    return {"ok": True, "data": data, "path": path.as_posix()}


def _write_json_file(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _safe_existing_repo_file(root: Path, rel_path: str) -> tuple[Path | None, str | None]:
    value = Path(str(rel_path or ""))
    if not str(rel_path or "").strip():
        return None, "path_required"
    if value.is_absolute() or ".." in value.parts:
        return None, "path_must_be_repo_relative_without_escape"
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None, "path_must_stay_inside_repo"
    if not candidate.is_file():
        return None, "file_not_found"
    return candidate, None


def _domain_weaver_projection(shell_root: Path) -> tuple[dict[str, Any], dict[str, Any] | None]:
    loaded = _read_json_file(shell_root / DOMAIN_WEAVER_PROJECTION_PATH)
    if loaded.get("ok") is not True:
        return {}, loaded
    data = loaded.get("data") if isinstance(loaded.get("data"), dict) else {}
    return data, None


def _domain_weaver_comms_projection(shell_root: Path, agents: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    try:
        projection = build_agent_comms_projection(shell_root, agents=agents or [], limit=80)
    except Exception as exc:
        return {"ok": False, "finding": "agent_comms_projection_failed", "error": exc.__class__.__name__}
    return projection if isinstance(projection, dict) else {"ok": False, "finding": "agent_comms_projection_not_object"}


def _domain_weaver_runs_projection(shell_root: Path) -> dict[str, Any]:
    try:
        projection = build_agent_comms_runs_projection(shell_root, limit=20)
    except Exception as exc:
        return {"ok": False, "finding": "agent_comms_runs_projection_failed", "error": exc.__class__.__name__}
    return projection if isinstance(projection, dict) else {"ok": False, "finding": "agent_comms_runs_projection_not_object"}


def _compact_domain_weaver_item(item: Any) -> dict[str, Any]:
    if not isinstance(item, Mapping):
        return {"value": str(item)[:120]}
    return {
        "domain_id": item.get("domain_id") or item.get("id"),
        "role_id": item.get("role_id"),
        "agent_id": item.get("agent_id"),
        "title": item.get("title") or item.get("name"),
        "status": item.get("status") or item.get("state") or item.get("readiness"),
        "has_capsule": bool(item.get("capsule") or item.get("capsule_path") or item.get("context_capsule_path")),
        "has_comms": bool(item.get("comms") or item.get("communication") or item.get("inbox_path") or item.get("outbox_path")),
    }


def _domain_weaver_projection_summary(projection: Mapping[str, Any]) -> dict[str, Any]:
    summary = projection.get("summary") if isinstance(projection.get("summary"), Mapping) else {}
    domains = projection.get("domains") if isinstance(projection.get("domains"), list) else []
    agents = projection.get("agents") if isinstance(projection.get("agents"), list) else []
    summary_keys = [
        "usable_domain_count",
        "active_domain_count",
        "candidate_domain_count",
        "covered_domain_count",
        "agent_count",
        "gap_count",
        "edge_count",
        "available_agent_comms_count",
        "full_domain_weaver_ready",
        "self_evolution_ready",
        "ui_development_ready",
        "queue_request_count",
        "context_active_resolver_available",
        "context_active_resolver_fresh_active_context_count",
        "context_active_resolver_stale_or_missing_active_context_count",
        "context_active_resolver_inspected_mount_count",
        "worker_start_ready_to_start_workers",
        "worker_start_queueable_request_count",
        "worker_start_queueable_lane_count",
        "worker_start_ready_lane_count",
        "worker_start_blocked_lane_count",
        "live_return_complete",
    ]
    compact_summary = {key: summary.get(key) for key in summary_keys if key in summary}
    return {
        "weave_status": projection.get("weave_status"),
        "summary": compact_summary,
        "summary_key_count": len(summary),
        "domain_count": len(domains),
        "agent_count": len(agents),
        "domain_samples": [_compact_domain_weaver_item(item) for item in domains[:12]],
        "agent_samples": [_compact_domain_weaver_item(item) for item in agents[:12]],
        "content_returned": "compact_samples_only",
    }


def domain_weaver_agents_status(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    projection, missing = _domain_weaver_projection(shell_root)
    agents = projection.get("agents") if isinstance(projection.get("agents"), list) else []
    comms = _domain_weaver_comms_projection(shell_root, agents=agents)
    runs = _domain_weaver_runs_projection(shell_root)
    directory_exists = (shell_root / AGENT_COMMS_DIRECTORY_PATH).is_file()
    return _ok(
        "domainWeaverAgentsStatus",
        {
            "projection_path": DOMAIN_WEAVER_PROJECTION_PATH.as_posix(),
            "projection_exists": missing is None,
            "projection_missing": missing,
            "projection_summary": _domain_weaver_projection_summary(projection),
            "agent_comms_directory_path": AGENT_COMMS_DIRECTORY_PATH.as_posix(),
            "agent_comms_directory_exists": directory_exists,
            "agent_comms_summary": comms.get("summary", {}) if isinstance(comms.get("summary"), Mapping) else {},
            "agent_comms_run_count": runs.get("run_count", 0),
            "safe_spawn_authority": "preview_only",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_context_active_resolver_status(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    return _ok(
        "domainWeaverContextActiveResolverStatus",
        {
            **build_context_active_resolver_status(root),
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_resolve_context_active(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    return _ok(
        "domainWeaverResolveContextActive",
        {
            **resolve_domain_active_context(
                root,
                domain_id=str(args.get("domain_id") or "").strip() or None,
                role_id=str(args.get("role_id") or "").strip() or None,
                lane=str(args.get("lane") or "").strip() or None,
                max_age_seconds=int(args.get("max_age_seconds") or 48 * 60 * 60),
            ),
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_active_context_reissue_preflight(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    preflight = build_active_context_reissue_preflight(
        root,
        domain_id=str(args.get("domain_id") or "").strip() or None,
        role_id=str(args.get("role_id") or "").strip() or None,
        lane=str(args.get("lane") or "").strip() or None,
        max_age_seconds=int(args.get("max_age_seconds") or 48 * 60 * 60),
    )
    finding = "active_context_reissue_required" if preflight.get("target_mount_count") else None
    return _ok(
        "domainWeaverActiveContextReissuePreflight",
        {
            **preflight,
            "finding": finding,
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_active_context_gated_refresh_plan(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    preflight_path = str(args.get("preflight_path") or "").strip()
    if preflight_path:
        resolved_preflight_path, problem = _safe_existing_repo_file(shell_root, preflight_path)
        if problem:
            return _blocked(
                problem,
                refusal_class="PATH_INVALID",
                data={
                    "route": "domain_weaver_active_context_gated_refresh_plan",
                    "preflight_path": preflight_path,
                    "mutates_active_state": False,
                    "accepted_state_claim": False,
                    "secrets_authority": False,
                },
            )
        preflight: Mapping[str, Any] | str | Path = resolved_preflight_path
    else:
        preflight = build_active_context_reissue_preflight(
            shell_root,
            domain_id=str(args.get("domain_id") or "").strip() or None,
            role_id=str(args.get("role_id") or "").strip() or None,
            lane=str(args.get("lane") or "").strip() or None,
            max_age_seconds=int(args.get("max_age_seconds") or 48 * 60 * 60),
        )
    lease_target_paths = args.get("lease_target_paths")
    plan = build_active_context_gated_refresh_plan(
        preflight,
        root=shell_root,
        confirmation=str(args.get("confirmation") or ""),
        idempotency_key=str(args.get("idempotency_key") or ""),
        agent_id=str(args.get("agent_id") or ""),
        lease_id=str(args.get("lease_id") or ""),
        lease_type=str(args.get("lease_type") or ""),
        lease_target_paths=[
            str(item)
            for item in (lease_target_paths if isinstance(lease_target_paths, list) else [])
            if str(item or "").strip()
        ],
        lease_proof=args.get("lease_proof") if isinstance(args.get("lease_proof"), Mapping) else None,
        preview_only=bool(args.get("preview_only", True)),
        allow_write=bool(args.get("allow_write", False)),
    )
    return _ok(
        "domainWeaverActiveContextGatedRefreshPlan",
        {
            **plan,
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_active_context_gated_refresh_apply(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    preflight_path = str(args.get("preflight_path") or "").strip()
    resolved_preflight_path, problem = _safe_existing_repo_file(shell_root, preflight_path)
    if problem:
        return _blocked(
            problem,
            refusal_class="PATH_INVALID",
            data={
                "route": "domain_weaver_active_context_gated_refresh_apply",
                "preflight_path": preflight_path,
                "refresh_run": False,
                "mutates_active_state": False,
                "accepted_state_claim": False,
                "secrets_authority": False,
            },
        )
    assert resolved_preflight_path is not None
    apply_result = apply_active_context_gated_refresh(
        resolved_preflight_path,
        root=shell_root,
        confirmation=str(args.get("confirmation") or ""),
        idempotency_key=str(args.get("idempotency_key") or ""),
        agent_id=str(args.get("agent_id") or ""),
        lease_id=str(args.get("lease_id") or ""),
        lease_type=str(args.get("lease_type") or "exclusive_write"),
        execute_write=bool(args.get("execute_write")),
    )
    operation = "domainWeaverActiveContextGatedRefreshApply"
    if apply_result.get("ok") is False:
        return _blocked(
            str(apply_result.get("finding") or "active_context_refresh_apply_blocked"),
            refusal_class=str(apply_result.get("refusal_class") or "DELEGATED_ROUTE_BLOCKED"),
            data={
                **apply_result,
                "operation": operation,
                "route": "domain_weaver_active_context_gated_refresh_apply",
                "preflight_path": preflight_path,
                "accepted_state_claim": False,
                "secrets_authority": False,
            },
        )
    return _ok(
        operation,
        {
            **apply_result,
            "route": "domain_weaver_active_context_gated_refresh_apply",
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_worker_start_readiness(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_domain_weaver_worker_start_readiness import build_domain_weaver_worker_start_readiness

    readiness = build_domain_weaver_worker_start_readiness(
        root,
        max_age_seconds=int(args.get("max_age_seconds") or 48 * 60 * 60),
    )
    if readiness.get("ok") is False and not readiness.get("finding"):
        readiness["finding"] = "worker_start_readiness_blocked"
    return _ok(
        "domainWeaverWorkerStartReadiness",
        {
            **readiness,
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_worker_start_readiness_summary(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_domain_weaver_worker_start_readiness import build_domain_weaver_worker_start_readiness

    readiness = build_domain_weaver_worker_start_readiness(
        root,
        max_age_seconds=int(args.get("max_age_seconds") or 48 * 60 * 60),
    )
    summary = readiness.get("summary") if isinstance(readiness.get("summary"), Mapping) else {}
    blockers = [str(item) for item in readiness.get("blockers") or [] if str(item).strip()]
    lanes = readiness.get("lane_results") if isinstance(readiness.get("lane_results"), list) else []
    compact_lanes: list[dict[str, Any]] = []
    for lane in lanes[:12]:
        if not isinstance(lane, Mapping):
            continue
        compact_lanes.append(
            {
                "lane_id": lane.get("lane_id"),
                "ready": bool(lane.get("ready")),
                "request_count": lane.get("request_count", 0),
                "ready_request_count": lane.get("ready_request_count", 0),
                "blocked_request_count": lane.get("blocked_request_count", 0),
                "blockers": list(lane.get("blockers") or []),
            }
        )
    payload = {
        "ok": bool(readiness.get("ok")),
        "finding": None if readiness.get("ok") else str(readiness.get("finding") or "worker_start_readiness_blocked"),
        "readiness_ok": bool(readiness.get("ok")),
        "ready_to_start_workers": bool(summary.get("ready_to_start_workers")),
        "next_action": readiness.get("next_action"),
        "summary": {
            "queueable_request_count": summary.get("queueable_request_count", 0),
            "ready_queueable_request_count": summary.get("ready_queueable_request_count", 0),
            "queueable_lane_count": summary.get("queueable_lane_count", 0),
            "ready_lane_count": summary.get("ready_lane_count", 0),
            "blocked_lane_count": summary.get("blocked_lane_count", 0),
            "worker_shift_conflict_risk_level": summary.get("worker_shift_conflict_risk_level"),
            "shared_capsule_concurrency_hazard": bool(summary.get("shared_capsule_concurrency_hazard")),
        },
        "blockers": blockers,
        "lane_summaries": compact_lanes,
        "full_route": "domain_weaver_agents.worker_start_readiness",
        "content_returned": "compact_worker_start_readiness_summary_only",
        "mutates_active_state": False,
        "accepted_state_claim": False,
        "secrets_authority": False,
    }
    return _ok("domainWeaverWorkerStartReadinessSummary", payload)


def domain_weaver_worker_start_backlog_hygiene(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_domain_weaver_worker_start_readiness import build_domain_weaver_worker_start_backlog_hygiene

    hygiene = build_domain_weaver_worker_start_backlog_hygiene(
        root,
        max_age_seconds=int(args.get("max_age_seconds") or 48 * 60 * 60),
        stale_after_seconds=int(args.get("stale_after_seconds") or 12 * 60 * 60),
        example_limit=int(args.get("example_limit") or 8),
    )
    finding = None if hygiene.get("hygiene_ok") else "worker_start_backlog_hygiene_dirty"
    return _ok(
        "domainWeaverWorkerStartBacklogHygiene",
        {
            **hygiene,
            "finding": finding,
            "content_returned": "compact_worker_start_backlog_hygiene",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_spawn_dispatch_start_plan(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_domain_weaver_spawn_request_dispatcher import build_spawn_dispatch_start_plan

    raw_request_paths = args.get("request_paths")
    request_paths = [
        str(item)
        for item in (raw_request_paths if isinstance(raw_request_paths, list) else [])
        if str(item or "").strip()
    ]
    single_request_path = str(args.get("request_path") or "").strip()
    if single_request_path:
        request_paths.append(single_request_path)
    plan = build_spawn_dispatch_start_plan(
        root,
        request_paths=request_paths or None,
        max_lanes=int(args.get("max_lanes") or 3),
        max_age_seconds=int(args.get("max_age_seconds") or 48 * 60 * 60),
    )
    if plan.get("planned_start_count"):
        finding = None
    elif plan.get("queueable_spawn_dispatch_request_count"):
        finding = "spawn_dispatch_start_plan_blocked"
    else:
        finding = "no_queued_spawn_dispatch_requests"
    return _ok(
        "domainWeaverSpawnDispatchStartPlan",
        {
            **plan,
            "finding": finding,
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_pressure_wave_plan(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_domain_weaver_pressure_wave import build_pressure_wave_plan

    plan = build_pressure_wave_plan(
        root,
        native_slot_cap=int(args.get("native_slot_cap") or 6),
        active_native_agent_count=int(args.get("active_native_agent_count") or 0),
        exact_queue_start_cap=int(args.get("exact_queue_start_cap") or 2),
        candidate_packet_cap=int(args.get("candidate_packet_cap") or 12),
        active_patch_cap=int(args.get("active_patch_cap") or 3),
        request_paths=[
            str(item)
            for item in (args.get("request_paths") if isinstance(args.get("request_paths"), list) else [])
            if str(item or "").strip()
        ],
        max_age_seconds=int(args.get("max_age_seconds") or 48 * 60 * 60),
    )
    return _ok(
        "domainWeaverPressureWavePlan",
        {
            **plan,
            "finding": None if not plan.get("blockers") else "pressure_wave_plan_has_blockers",
            "content_returned": "pressure_wave_caps_batches_spawn_templates_nonclaims",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_spawn_dispatch_legacy_receipt_quarantine(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_domain_weaver_spawn_request_dispatcher import (
        build_spawn_dispatch_legacy_receipt_quarantine,
    )

    artifact_paths = [
        str(item)
        for item in (args.get("artifact_paths") if isinstance(args.get("artifact_paths"), list) else [])
        if str(item or "").strip()
    ]
    single_artifact_path = str(args.get("artifact_path") or "").strip()
    if single_artifact_path:
        artifact_paths.append(single_artifact_path)
    report = build_spawn_dispatch_legacy_receipt_quarantine(
        root,
        artifact_paths=artifact_paths or None,
    )
    return _ok(
        "domainWeaverSpawnDispatchLegacyReceiptQuarantine",
        {
            **report,
            "finding": (
                "legacy_false_enqueue_detected"
                if report.get("legacy_false_enqueue_detected")
                else None
            ),
            "content_returned": "legacy_false_enqueue_quarantine_counts_paths_nonclaims",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_pressure_wave_spawn_request_seed(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_domain_weaver_pressure_wave import seed_pressure_wave_spawn_requests

    result = seed_pressure_wave_spawn_requests(
        root,
        parent_worker_id=str(args.get("parent_worker_id") or "pressure_scheduler"),
        execute_write=bool(args.get("execute_write")),
        confirmation=str(args.get("confirmation") or ""),
        idempotency_key=str(args.get("idempotency_key") or ""),
        agent_id=str(args.get("agent_id") or ""),
        write_intent_lease_id=str(args.get("write_intent_lease_id") or ""),
        limit=int(args.get("limit")) if args.get("limit") is not None else None,
    )
    if bool(args.get("execute_write")) and not result.get("write_gate", {}).get("ok"):
        return _blocked(
            "domainWeaverPressureWaveSpawnRequestSeed",
            "pressure_wave_spawn_request_seed_gate_blocked",
            refusal_class="DELEGATED_ROUTE_BLOCKED",
            data={
                **result,
                "route": "domain_weaver_pressure_wave_spawn_request_seed",
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            },
        )
    return _ok(
        "domainWeaverPressureWaveSpawnRequestSeed",
        {
            **result,
            "route": "domain_weaver_pressure_wave_spawn_request_seed",
            "mutates_active_state": bool(result.get("execute_write") and result.get("spawn_request_count")),
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_agents_projection_summary(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    projection, missing = _domain_weaver_projection(shell_root)
    return _ok(
        "domainWeaverAgentsProjectionSummary",
        {
            "projection_path": DOMAIN_WEAVER_PROJECTION_PATH.as_posix(),
            "projection_exists": missing is None,
            "projection_missing": missing,
            "projection_summary": _domain_weaver_projection_summary(projection),
            "promotion_review_path": DOMAIN_WEAVER_PROMOTION_REVIEW_PATH.as_posix(),
            "promotion_review_exists": (shell_root / DOMAIN_WEAVER_PROMOTION_REVIEW_PATH).is_file(),
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_projection_accepted_refresh_plan(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_domain_weaver_projection_refresh_candidate import build_projection_accepted_refresh_plan

    plan = build_projection_accepted_refresh_plan(
        root,
        max_context_age_seconds=int(args.get("max_context_age_seconds") or 48 * 60 * 60),
    )
    return _ok(
        "domainWeaverProjectionAcceptedRefreshPlan",
        {
            **plan,
            "finding": None if plan.get("plan_ok") else "projection_accepted_refresh_plan_not_apply_ready",
            "content_returned": "accepted_projection_target_hashes_gate_blockers",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_projection_replacement_body_candidate(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_domain_weaver_projection_refresh_candidate import build_projection_replacement_body_candidate

    include_body = bool(args.get("include_body"))
    candidate = build_projection_replacement_body_candidate(
        root,
        max_context_age_seconds=int(args.get("max_context_age_seconds") or 48 * 60 * 60),
    )
    if not include_body:
        candidate = dict(candidate)
        candidate.pop("candidate_body", None)
        candidate["candidate_body_omitted"] = True
    return _ok(
        "domainWeaverProjectionReplacementBodyCandidate",
        {
            **candidate,
            "finding": None if candidate.get("ok") else "projection_replacement_body_candidate_blocked",
            "content_returned": "candidate_projection_body_hashes_invariants_summary",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_projection_accepted_refresh_apply(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_domain_weaver_projection_refresh_candidate import apply_projection_accepted_refresh

    shell_root = _resolve_root(root)
    apply_result = apply_projection_accepted_refresh(
        shell_root,
        confirmation=str(args.get("confirmation") or ""),
        accepted_state_write_confirmation=str(args.get("accepted_state_write_confirmation") or ""),
        idempotency_key=str(args.get("idempotency_key") or ""),
        agent_id=str(args.get("agent_id") or ""),
        lease_id=str(args.get("lease_id") or ""),
        before_sha256=str(args.get("before_sha256") or ""),
        replacement_body_sha256=str(args.get("replacement_body_sha256") or ""),
        replacement_body=args.get("replacement_body") if isinstance(args.get("replacement_body"), Mapping) else None,
        replacement_body_path=str(args.get("replacement_body_path") or "").strip() or None,
        execute_write=bool(args.get("execute_write")),
    )
    operation = "domainWeaverProjectionAcceptedRefreshApply"
    if apply_result.get("ok") is False:
        return _blocked(
            str(apply_result.get("finding") or "projection_accepted_refresh_apply_blocked"),
            refusal_class=str(apply_result.get("refusal_class") or "DELEGATED_ROUTE_BLOCKED"),
            data={
                **apply_result,
                "operation": operation,
                "route": "domain_weaver_projection_accepted_refresh_apply",
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            },
        )
    return _ok(
        operation,
        {
            **apply_result,
            "route": "domain_weaver_projection_accepted_refresh_apply",
            "mutates_active_state": bool(apply_result.get("mutates_active_state")),
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_semantic_alias_projection_apply(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_domain_weaver_semantic_alias_canonicalization import apply_semantic_alias_projection_rewrite

    shell_root = _resolve_root(root)
    apply_result = apply_semantic_alias_projection_rewrite(
        shell_root,
        confirmation=str(args.get("confirmation") or ""),
        semantic_alias_write_confirmation=str(args.get("semantic_alias_write_confirmation") or ""),
        idempotency_key=str(args.get("idempotency_key") or ""),
        agent_id=str(args.get("agent_id") or ""),
        lease_id=str(args.get("lease_id") or ""),
        before_sha256=str(args.get("before_sha256") or ""),
        replacement_body_sha256=str(args.get("replacement_body_sha256") or ""),
        execute_write=bool(args.get("execute_write")),
    )
    operation = "domainWeaverSemanticAliasProjectionApply"
    if apply_result.get("ok") is False:
        return _blocked(
            str(apply_result.get("finding") or "semantic_alias_projection_apply_blocked"),
            refusal_class=str(apply_result.get("refusal_class") or "DELEGATED_ROUTE_BLOCKED"),
            data={
                **apply_result,
                "operation": operation,
                "route": "domain_weaver_semantic_alias_projection_apply",
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            },
        )
    return _ok(
        operation,
        {
            **apply_result,
            "route": "domain_weaver_semantic_alias_projection_apply",
            "mutates_active_state": bool(apply_result.get("mutates_active_state")),
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_agents_comms_overview(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    projection, _missing = _domain_weaver_projection(shell_root)
    agents = projection.get("agents") if isinstance(projection.get("agents"), list) else []
    comms = _domain_weaver_comms_projection(shell_root, agents=agents)
    runs = _domain_weaver_runs_projection(shell_root)
    return _ok(
        "domainWeaverAgentsCommsOverview",
        {
            "agent_comms_directory_path": AGENT_COMMS_DIRECTORY_PATH.as_posix(),
            "agent_comms_directory_exists": (shell_root / AGENT_COMMS_DIRECTORY_PATH).is_file(),
            "projection": {
                "schema_id": comms.get("schema_id"),
                "summary": comms.get("summary", {}),
                "channels": comms.get("channels", [])[:20] if isinstance(comms.get("channels"), list) else [],
                "threads": comms.get("threads", [])[:20] if isinstance(comms.get("threads"), list) else [],
                "inbox": comms.get("inbox", {}) if isinstance(comms.get("inbox"), Mapping) else {},
            },
            "runs_projection": {
                "schema_id": runs.get("schema_id"),
                "run_count": runs.get("run_count", 0),
                "runs": runs.get("runs", [])[:20] if isinstance(runs.get("runs"), list) else [],
            },
            "write_routes_not_invoked": [
                "agent_comms.send_message",
                "agent_comms.start_run",
                "agent_swarm.invoke",
            ],
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_semantic_alias_supervised_apply_preflight(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_domain_weaver_semantic_alias_canonicalization import build_semantic_alias_supervised_apply_preflight

    shell_root = _resolve_root(root)
    preflight = build_semantic_alias_supervised_apply_preflight(
        shell_root,
        agent_id=str(args.get("agent_id") or "codex_cli:semantic-alias-supervised-apply"),
        lease_id=str(args.get("lease_id") or "<live-exclusive-write-lease-id-covering-semantic-alias-targets>"),
        idempotency_prefix=str(args.get("idempotency_prefix") or "semantic-alias-supervised-apply"),
        include_candidate_bodies=bool(args.get("include_candidate_bodies")),
    )
    return _ok(
        "domainWeaverSemanticAliasSupervisedApplyPreflight",
        {
            **preflight,
            "route": "domain_weaver_semantic_alias_supervised_apply_preflight",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_semantic_alias_mount_manifest_apply(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_domain_weaver_semantic_alias_canonicalization import apply_semantic_alias_mount_manifest_rewrite

    shell_root = _resolve_root(root)
    apply_result = apply_semantic_alias_mount_manifest_rewrite(
        shell_root,
        confirmation=str(args.get("confirmation") or ""),
        manifest_write_confirmation=str(args.get("manifest_write_confirmation") or ""),
        idempotency_key=str(args.get("idempotency_key") or ""),
        agent_id=str(args.get("agent_id") or ""),
        lease_id=str(args.get("lease_id") or ""),
        before_sha256=str(args.get("before_sha256") or ""),
        replacement_body_sha256=str(args.get("replacement_body_sha256") or ""),
        execute_write=bool(args.get("execute_write")),
    )
    operation = "domainWeaverSemanticAliasMountManifestApply"
    if apply_result.get("ok") is False:
        return _blocked(
            str(apply_result.get("finding") or "semantic_alias_mount_manifest_apply_blocked"),
            refusal_class=str(apply_result.get("refusal_class") or "DELEGATED_ROUTE_BLOCKED"),
            data={
                **apply_result,
                "operation": operation,
                "route": "domain_weaver_semantic_alias_mount_manifest_apply",
                "production_authority": False,
                "live_execution_authority": False,
                "secrets_authority": False,
            },
        )
    return _ok(
        operation,
        {
            **apply_result,
            "route": "domain_weaver_semantic_alias_mount_manifest_apply",
            "mutates_active_state": bool(apply_result.get("mutates_active_state")),
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_agents_spawn_plan_preview(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    objective = str(args.get("objective") or "Maintain or spawn a Domain Weaver-aligned agent.").strip()
    domain_id = str(args.get("domain_id") or "").strip() or None
    role_id = str(args.get("role_id") or "").strip() or None
    shell_root = _resolve_root(root)
    projection, _missing = _domain_weaver_projection(shell_root)
    projection_summary = _domain_weaver_projection_summary(projection)
    return _ok(
        "domainWeaverAgentsSpawnPlanPreview",
        {
            "objective": objective,
            "domain_id": domain_id,
            "role_id": role_id,
            "projection_summary": projection_summary,
            "plan": {
                "steps": [
                    "Read domain_weaver_agents.status and comms_overview.",
                    "Use worker_shift.parallel_plan_preview before parallel work.",
                    "Use agent_swarm.spawn_plan for generic spawn planning.",
                    "Use agent_comms start/run/directive routes only after explicit confirmation/idempotency gates exist on this branch.",
                ],
                "recommended_branch_calls": [
                    {"branch_id": "domain_weaver_agents", "route_id": "domain_weaver_status"},
                    {"branch_id": "domain_weaver_agents", "route_id": "comms_overview"},
                    {"branch_id": "agent_swarm", "route_id": "spawn_plan", "args": {"objective": objective}},
                    {"branch_id": "worker_shift", "route_id": "parallel_plan_preview"},
                ],
                "spawn_authority": "preview_only",
                "required_future_gates_for_spawn": ["idempotency_key", "ION_BOUNDED_WRITE_CONFIRMED", "operator_approval_for_live_agent_spawn"],
            },
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def _domain_weaver_comms_send_payload(args: Mapping[str, Any]) -> dict[str, Any]:
    allowed_keys = {
        "from_role",
        "to_roles",
        "cc_roles",
        "channel_id",
        "thread_id",
        "room_id",
        "room_kind",
        "subject",
        "body",
        "summary",
        "message_kind",
        "priority",
        "requires_response",
        "source_refs",
        "artifact_refs",
        "receipt_refs",
        "domain_id",
        "mission",
        "visibility",
        "emit_signal",
    }
    payload = {key: args.get(key) for key in allowed_keys if key in args}
    payload.setdefault("from_role", "operator")
    payload.setdefault("message_kind", "thread_note")
    payload.setdefault("authority_boundary", "candidate_domain_weaver_agent_comms_not_accepted_state")
    payload.setdefault("routing_policy", "domain_weaver_agents_action_gateway")
    return payload


def domain_weaver_agents_comms_send_preview(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    payload = _domain_weaver_comms_send_payload(args)
    body = str(payload.get("body") or "")
    subject = str(payload.get("subject") or "").strip()
    to_roles = payload.get("to_roles") or payload.get("to") or []
    return _ok(
        "domainWeaverAgentsCommsSendPreview",
        {
            "would_send": bool(body.strip()),
            "from_role": payload.get("from_role"),
            "to_roles": to_roles,
            "channel_id": payload.get("channel_id"),
            "subject": subject,
            "body_chars": len(body),
            "body_preview": body[:240],
            "message_kind": payload.get("message_kind"),
            "required_for_send": ["idempotency_key", CONFIRMATION_TOKEN],
            "send_route": "domain_weaver_agents.comms_send",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_agents_comms_send(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    _confirmation, idempotency_key, blocked = _mutation_fields(args)
    if blocked:
        return blocked
    payload = _domain_weaver_comms_send_payload(args)
    result = send_agent_message(shell_root, payload)
    receipt_path = _write_receipt(
        shell_root,
        operation="domain_weaver_agents_comms_send",
        service_id="agent_comms",
        idempotency_key=idempotency_key,
        receipt_stage="post",
        payload={
            "ok": result.get("ok"),
            "message_id": result.get("message_id"),
            "thread_id": result.get("thread_id"),
            "message_path": result.get("message_path"),
            "thread_path": result.get("thread_path"),
            "room_capsule_path": result.get("room_capsule_path"),
            "signal_path": result.get("signal_path"),
            "finding": result.get("finding"),
            "from_role": payload.get("from_role"),
            "to_roles": payload.get("to_roles"),
            "channel_id": payload.get("channel_id"),
            "message_kind": payload.get("message_kind"),
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )
    if result.get("ok") is not True:
        return _blocked(
            "domain_weaver_agent_comms_send_failed",
            refusal_class="AGENT_COMMS_SEND_FAILED",
            data={"send_result": result, "receipt_path": receipt_path},
        )
    return _ok(
        "domainWeaverAgentsCommsSend",
        {
            "send_result": result,
            "receipt_path": receipt_path,
            "mutates_active_state": True,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def _domain_weaver_comms_pickup_payload(args: Mapping[str, Any]) -> dict[str, Any]:
    allowed_keys = {
        "role_id",
        "message_id",
        "thread_id",
        "carrier_id",
        "context_package_id",
        "pickup_reason",
    }
    payload = {key: args.get(key) for key in allowed_keys if key in args}
    payload.setdefault("carrier_id", "CODEX_CLI_CARRIER")
    payload.setdefault("pickup_reason", "domain_weaver_agent_comms_pickup")
    return payload


def domain_weaver_agents_comms_pickup_preview(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    payload = _domain_weaver_comms_pickup_payload(args)
    result = preview_agent_inbox_pickup(
        shell_root,
        role_id=str(payload.get("role_id") or ""),
        message_id=str(payload.get("message_id") or ""),
        thread_id=str(payload.get("thread_id") or ""),
        carrier_id=str(payload.get("carrier_id") or "CODEX_CLI_CARRIER"),
        context_package_id=str(payload.get("context_package_id") or ""),
    )
    return _ok(
        "domainWeaverAgentsCommsPickupPreview",
        {
            "pickup_preview": result,
            "required_for_pickup": ["idempotency_key", CONFIRMATION_TOKEN],
            "pickup_route": "domain_weaver_agents.comms_pickup",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_agents_comms_pickup(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    _confirmation, idempotency_key, blocked = _mutation_fields(args)
    if blocked:
        return blocked
    payload = _domain_weaver_comms_pickup_payload(args)
    result = pickup_agent_inbox_message(
        shell_root,
        role_id=str(payload.get("role_id") or ""),
        message_id=str(payload.get("message_id") or ""),
        thread_id=str(payload.get("thread_id") or ""),
        carrier_id=str(payload.get("carrier_id") or "CODEX_CLI_CARRIER"),
        context_package_id=str(payload.get("context_package_id") or ""),
        pickup_reason=str(payload.get("pickup_reason") or "domain_weaver_agent_comms_pickup"),
        idempotency_key=idempotency_key,
    )
    receipt_path = _write_receipt(
        shell_root,
        operation="domain_weaver_agents_comms_pickup",
        service_id="agent_comms",
        idempotency_key=idempotency_key,
        receipt_stage="post",
        payload={
            "ok": result.get("ok"),
            "finding": result.get("finding"),
            "role_id": result.get("role_id"),
            "carrier_id": result.get("carrier_id"),
            "context_package_id": result.get("context_package_id"),
            "message_id": result.get("message_id"),
            "thread_id": result.get("thread_id"),
            "inbox_ref_path": result.get("inbox_ref_path"),
            "pickup_receipt_path": result.get("pickup_receipt_path"),
            "idempotent_replay": result.get("idempotent_replay", False),
            "ref_status": result.get("ref_status"),
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )
    if result.get("ok") is not True:
        return _blocked(
            "domain_weaver_agent_comms_pickup_failed",
            refusal_class="AGENT_COMMS_PICKUP_FAILED",
            data={"pickup_result": result, "receipt_path": receipt_path},
        )
    return _ok(
        "domainWeaverAgentsCommsPickup",
        {
            "pickup_result": result,
            "receipt_path": receipt_path,
            "mutates_active_state": bool(result.get("mutates_active_state", True)),
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def _domain_weaver_comms_proof_evidence(root: Path, rel_path: str, *, required: bool = True) -> dict[str, Any]:
    rel = str(rel_path or "").strip()
    row: dict[str, Any] = {
        "path": rel or None,
        "required": required,
        "exists": False,
        "ok": False,
    }
    target, problem = _safe_existing_repo_file(root, rel)
    if problem or target is None:
        row["finding"] = problem or "file_not_found"
        return row
    row.update(
        {
            "path": target.relative_to(root).as_posix(),
            "exists": True,
            "ok": True,
            "sha256": _sha256_file(target),
        }
    )
    if target.suffix == ".json":
        loaded = _read_json_file(target)
        row["json_ok"] = loaded.get("ok") is True
        if loaded.get("ok") is True:
            row["json"] = dict(loaded.get("data") or {})
        else:
            row["json_finding"] = loaded.get("finding")
    return row


def _domain_weaver_find_dispatch_request_for_comms(
    root: Path,
    *,
    message_id: str,
    pickup_receipt_path: str,
) -> str:
    request_dir = root / "ION/05_context/current/chatgpt_connector/codex_work_requests"
    if not request_dir.is_dir():
        return ""
    for path in sorted(request_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        loaded = _read_json_file(path)
        if loaded.get("ok") is not True:
            continue
        payload = dict(loaded.get("data") or {})
        if message_id and str(payload.get("source_agent_comms_message_id") or "") == message_id:
            return path.relative_to(root).as_posix()
        if pickup_receipt_path and str(payload.get("pickup_receipt_path") or "") == pickup_receipt_path:
            return path.relative_to(root).as_posix()
        annotation = payload.get("domain_weaver_agent_comms_dispatch")
        if isinstance(annotation, Mapping):
            if message_id and str(annotation.get("source_agent_comms_message_id") or "") == message_id:
                return path.relative_to(root).as_posix()
            if pickup_receipt_path and str(annotation.get("pickup_receipt_path") or "") == pickup_receipt_path:
                return path.relative_to(root).as_posix()
    return ""


def _domain_weaver_find_signal_for_comms(root: Path, *, message_id: str) -> str:
    if not message_id:
        return ""
    signals_dir = root / "ION/05_context/current/agent_comms/signals"
    if not signals_dir.is_dir():
        return ""
    for path in sorted(signals_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        loaded = _read_json_file(path)
        if loaded.get("ok") is not True:
            continue
        payload = dict(loaded.get("data") or {})
        if str(payload.get("message_id") or "") == message_id:
            return path.relative_to(root).as_posix()
    return ""


def _domain_weaver_find_message_for_comms(root: Path, *, message_id: str) -> dict[str, str]:
    if not message_id:
        return {}
    target = message_id.lower()
    inbox_dir = root / "ION/05_context/current/agent_comms/inbox"
    if inbox_dir.is_dir():
        candidates = sorted(
            inbox_dir.glob("*/*.json"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )[:2000]
        for path in candidates:
            loaded = _read_json_file(path)
            if loaded.get("ok") is not True:
                continue
            payload = dict(loaded.get("data") or {})
            message_ref = payload.get("message_ref") if isinstance(payload.get("message_ref"), Mapping) else {}
            observed_id = str(payload.get("message_id") or message_ref.get("message_id") or "").strip()
            if observed_id.lower() != target:
                continue
            return {
                "inbox_ref": path.relative_to(root).as_posix(),
                "message_path": str(payload.get("message_path") or message_ref.get("message_path") or "").strip(),
                "thread_path": str(payload.get("thread_path") or message_ref.get("thread_path") or "").strip(),
                "thread_id": str(payload.get("thread_id") or message_ref.get("thread_id") or "").strip(),
            }
    threads_dir = root / "ION/05_context/current/agent_comms/threads"
    if threads_dir.is_dir():
        candidates = sorted(
            threads_dir.glob("*/messages/*.json"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )[:2000]
        for path in candidates:
            loaded = _read_json_file(path)
            if loaded.get("ok") is not True:
                continue
            payload = dict(loaded.get("data") or {})
            observed_id = str(payload.get("message_id") or "").strip()
            if observed_id.lower() != target:
                continue
            thread_id = str(payload.get("thread_id") or path.parent.parent.name).strip()
            return {
                "message_path": path.relative_to(root).as_posix(),
                "thread_id": thread_id,
                "thread_path": (path.parent.parent / "THREAD.json").relative_to(root).as_posix(),
            }
    return {}


def _domain_weaver_find_pickup_for_comms(root: Path, *, message_id: str, inbox_ref: str) -> str:
    pickups_dir = root / "ION/05_context/current/agent_comms/receipts/pickups"
    if not pickups_dir.is_dir():
        return ""
    target_message = str(message_id or "").strip().lower()
    target_inbox = str(inbox_ref or "").strip()
    for path in sorted(pickups_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)[:2000]:
        loaded = _read_json_file(path)
        if loaded.get("ok") is not True:
            continue
        payload = dict(loaded.get("data") or {})
        if target_message and str(payload.get("message_id") or "").strip().lower() == target_message:
            return path.relative_to(root).as_posix()
        if target_inbox and str(payload.get("inbox_ref_path") or "").strip() == target_inbox:
            return path.relative_to(root).as_posix()
    return ""


def _domain_weaver_find_synced_reply_for_comms(root: Path, *, thread_id: str, source_message_id: str, task_return_path: str) -> str:
    if not thread_id:
        return ""
    message_dir = root / "ION/05_context/current/agent_comms/threads" / thread_id / "messages"
    if not message_dir.is_dir():
        return ""
    for path in sorted(message_dir.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        loaded = _read_json_file(path)
        if loaded.get("ok") is not True:
            continue
        payload = dict(loaded.get("data") or {})
        if str(payload.get("message_id") or "") == source_message_id:
            continue
        refs = [str(item) for item in list(payload.get("source_refs") or []) + list(payload.get("artifact_refs") or []) + list(payload.get("receipt_refs") or [])]
        text = json.dumps(payload, sort_keys=True)
        if task_return_path and (task_return_path in refs or task_return_path in text):
            return path.relative_to(root).as_posix()
        if source_message_id and source_message_id in text and str(payload.get("message_kind") or "") in {"task_return", "synced_reply", "worker_return", "thread_reply"}:
            return path.relative_to(root).as_posix()
    return ""


def domain_weaver_agents_comms_autoreaction_proof(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    message_id = str(args.get("message_id") or "").strip()
    role_id = str(args.get("role_id") or args.get("agent_role") or "").strip()
    pickup_receipt_rel = str(args.get("pickup_receipt_path") or "").strip()
    explicit_request_rel = str(args.get("codex_work_request_path") or args.get("work_request_path") or "").strip()
    explicit_run_rel = str(args.get("worker_run_packet_path") or args.get("run_packet_path") or "").strip()
    explicit_task_return_rel = str(args.get("task_return_path") or "").strip()
    explicit_synced_reply_rel = str(args.get("synced_reply_message_path") or "").strip()

    pickup_evidence = _domain_weaver_comms_proof_evidence(shell_root, pickup_receipt_rel)
    pickup_payload: dict[str, Any] = {}
    if pickup_evidence.get("json_ok"):
        loaded = dict(pickup_evidence.get("json") or {})
        pickup_payload = dict(loaded.get("data") or loaded)
    message_lookup = _domain_weaver_find_message_for_comms(shell_root, message_id=message_id)
    message_rel = str(args.get("source_message_path") or pickup_payload.get("message_path") or message_lookup.get("message_path") or "").strip()
    inbox_rel = str(args.get("source_inbox_ref") or pickup_payload.get("inbox_ref_path") or message_lookup.get("inbox_ref") or "").strip()
    thread_rel = str(args.get("source_thread_path") or pickup_payload.get("thread_path") or message_lookup.get("thread_path") or "").strip()
    thread_id = str(args.get("thread_id") or pickup_payload.get("thread_id") or message_lookup.get("thread_id") or "").strip()
    if not pickup_receipt_rel:
        pickup_receipt_rel = _domain_weaver_find_pickup_for_comms(
            shell_root,
            message_id=message_id,
            inbox_ref=inbox_rel,
        )
        pickup_evidence = _domain_weaver_comms_proof_evidence(shell_root, pickup_receipt_rel)
        pickup_payload = {}
        if pickup_evidence.get("json_ok"):
            loaded = dict(pickup_evidence.get("json") or {})
            pickup_payload = dict(loaded.get("data") or loaded)
        inbox_rel = str(inbox_rel or pickup_payload.get("inbox_ref_path") or "").strip()
        thread_rel = str(thread_rel or pickup_payload.get("thread_path") or "").strip()
        thread_id = str(thread_id or pickup_payload.get("thread_id") or "").strip()

    message_evidence = _domain_weaver_comms_proof_evidence(shell_root, message_rel)
    message_payload = dict(message_evidence.get("json") or {}) if message_evidence.get("json_ok") else {}
    inbox_evidence = _domain_weaver_comms_proof_evidence(shell_root, inbox_rel)
    thread_evidence = _domain_weaver_comms_proof_evidence(shell_root, thread_rel)
    signal_rel = str(
        args.get("signal_path")
        or message_payload.get("signal_path")
        or message_payload.get("signal_file_path")
        or _domain_weaver_find_signal_for_comms(shell_root, message_id=message_id)
        or ""
    ).strip()
    signal_evidence = _domain_weaver_comms_proof_evidence(shell_root, signal_rel)

    request_rel = explicit_request_rel or _domain_weaver_find_dispatch_request_for_comms(
        shell_root,
        message_id=message_id,
        pickup_receipt_path=pickup_receipt_rel,
    )
    request_evidence = _domain_weaver_comms_proof_evidence(shell_root, request_rel)
    request_payload = dict(request_evidence.get("json") or {}) if request_evidence.get("json_ok") else {}
    run_rel = explicit_run_rel
    if not run_rel:
        runs = request_payload.get("codex_queue_runner_runs")
        if isinstance(runs, list) and runs:
            run_rel = str(runs[-1] or "").strip()
    run_evidence = _domain_weaver_comms_proof_evidence(shell_root, run_rel)
    run_payload = dict(run_evidence.get("json") or {}) if run_evidence.get("json_ok") else {}
    run_return_rel = str(run_payload.get("latest_return_packet_path") or "").strip()
    request_return_rel = str(request_payload.get("latest_return_packet_path") or "").strip()
    if explicit_task_return_rel:
        task_return_rel = explicit_task_return_rel
    elif run_return_rel:
        task_return_rel = run_return_rel
    elif explicit_run_rel:
        task_return_rel = ""
    else:
        task_return_rel = request_return_rel
    task_return_evidence = _domain_weaver_comms_proof_evidence(shell_root, task_return_rel)
    task_return_payload = dict(task_return_evidence.get("json") or {}) if task_return_evidence.get("json_ok") else {}
    task_return_lane = str(task_return_payload.get("return_lane") or "").strip()
    alternate_worker_return = (
        bool(task_return_payload.get("alternate_worker_return"))
        or task_return_lane == "alternate_worker_return"
    )
    synced_reply_rel = explicit_synced_reply_rel or _domain_weaver_find_synced_reply_for_comms(
        shell_root,
        thread_id=thread_id,
        source_message_id=message_id,
        task_return_path=task_return_rel,
    )
    synced_reply_evidence = _domain_weaver_comms_proof_evidence(shell_root, synced_reply_rel)

    links = [
        {"link_id": "message_path", "ok": message_evidence.get("ok") is True, "evidence": message_evidence},
        {"link_id": "thread_path", "ok": thread_evidence.get("ok") is True, "evidence": thread_evidence},
        {"link_id": "inbox_ref", "ok": inbox_evidence.get("ok") is True, "evidence": inbox_evidence},
        {
            "link_id": "pickup_receipt",
            "ok": pickup_evidence.get("ok") is True and str(pickup_payload.get("ref_status") or "") == "picked_up",
            "evidence": pickup_evidence,
            "detail": {"ref_status": pickup_payload.get("ref_status"), "role_id": pickup_payload.get("role_id")},
        },
        {"link_id": "signal_file", "ok": signal_evidence.get("ok") is True, "evidence": signal_evidence},
        {"link_id": "dispatcher_work_request", "ok": request_evidence.get("ok") is True, "evidence": request_evidence},
        {
            "link_id": "worker_run",
            "ok": run_evidence.get("ok") is True,
            "evidence": run_evidence,
            "detail": {"run_status": run_payload.get("status"), "failure_classification": run_payload.get("failure_classification")},
        },
        {"link_id": "task_return_path", "ok": task_return_evidence.get("ok") is True, "evidence": task_return_evidence},
        {"link_id": "synced_reply_message", "ok": synced_reply_evidence.get("ok") is True, "evidence": synced_reply_evidence},
    ]
    missing_links = [str(link["link_id"]) for link in links if link.get("ok") is not True]
    first_missing = missing_links[0] if missing_links else ""
    delivery_and_pickup = all(
        link.get("ok") is True
        for link in links[:4]
    )
    if not missing_links:
        if alternate_worker_return:
            proof_state = "alternate_worker_return_recovery_chain_proven"
        else:
            proof_state = "automatic_agent_reaction_chain_proven"
    elif delivery_and_pickup:
        proof_state = "durable_delivery_and_pickup_only"
    else:
        proof_state = f"blocked_at_{first_missing or 'unknown'}"
    automatic_agent_reaction_proven = not missing_links and not alternate_worker_return
    alternate_worker_return_recovery_proven = not missing_links and alternate_worker_return

    return _ok(
        "domainWeaverAgentsCommsAutoreactionProof",
        {
            "schema_id": "ion.domain_weaver.agent_comms_autoreaction_proof.v0_1",
            "proof_ok": not missing_links,
            "proof_state": proof_state,
            "automatic_agent_reaction_proven": automatic_agent_reaction_proven,
            "alternate_worker_return_recovery_proven": alternate_worker_return_recovery_proven,
            "codex_live_consumption_proven": run_evidence.get("ok") is True,
            "task_return_lane": task_return_lane or None,
            "alternate_worker_return": alternate_worker_return,
            "message_id": message_id,
            "role_id": role_id,
            "thread_id": thread_id,
            "first_missing_link": first_missing,
            "missing_links": missing_links,
            "links": links,
            "chain_sequence": "message_path -> thread_path -> inbox_ref -> pickup_receipt -> signal_file -> dispatcher_work_request -> worker_run -> task_return_path -> synced_reply_message",
            "claim_boundary": "Delivery, inbox write, signal file, pickup, dispatch request, and worker run evidence are not autonomous reaction proof unless the full chain reaches a non-alternate task return and synced reply. Alternate-worker task returns prove recovery-chain completion only.",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    )


def _domain_weaver_comms_dispatch_payload(args: Mapping[str, Any]) -> dict[str, Any]:
    allowed_keys = {
        "role_id",
        "message_id",
        "thread_id",
        "agent_role",
        "objective",
        "pickup_receipt_path",
        "consumer_role_id",
        "context_package_id",
        "domain_id",
        "source_message_path",
        "source_inbox_ref",
        "source_thread_path",
        "proof_correlation_id",
        "work_class",
        "risk_level",
        "route_family",
        "requested_model",
        "requested_reasoning_effort",
        "model_override_reason",
        "codex_model_override",
        "timeout_seconds",
    }
    payload = {key: args.get(key) for key in allowed_keys if key in args}
    payload.setdefault("agent_role", payload.get("role_id"))
    payload.setdefault("consumer_role_id", payload.get("role_id"))
    payload.setdefault("work_class", "domain_weaver_agent_comms_dispatch")
    payload.setdefault("risk_level", "critical")
    payload.setdefault("route_family", "domain_weaver_agent_comms")
    override = payload.get("codex_model_override")
    selected_model = str(payload.get("requested_model") or "").strip()
    selected_reasoning = str(payload.get("requested_reasoning_effort") or "").strip()
    override_reason = str(payload.get("model_override_reason") or "").strip()
    if isinstance(override, Mapping):
        selected_model = selected_model or str(override.get("selected_model") or "").strip()
        selected_reasoning = selected_reasoning or str(override.get("selected_reasoning_effort") or "").strip()
        override_reason = override_reason or str(override.get("reason") or "").strip()
    payload["requested_model"] = selected_model or "gpt-5.5"
    payload["requested_reasoning_effort"] = selected_reasoning or "xhigh"
    payload["model_override_reason"] = override_reason or "domain_weaver_agent_comms_dispatch_high_stakes_route"
    payload["codex_model_override"] = {
        "selected_model": payload["requested_model"],
        "selected_reasoning_effort": payload["requested_reasoning_effort"],
        "reason": payload["model_override_reason"],
    }
    return payload


def _domain_weaver_comms_dispatch_preview_result(root: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    role_id = str(payload.get("role_id") or "").strip()
    agent_role = str(payload.get("agent_role") or role_id).strip()
    message_id = str(payload.get("message_id") or "").strip()
    thread_id = str(payload.get("thread_id") or "").strip()
    pickup_receipt_rel = str(payload.get("pickup_receipt_path") or "").strip()
    objective = str(payload.get("objective") or "").strip()
    domain_id = str(payload.get("domain_id") or "").strip()
    if not role_id:
        return {"ok": False, "finding": "role_id_required"}
    if not agent_role:
        return {"ok": False, "finding": "agent_role_required"}
    if not message_id:
        return {"ok": False, "finding": "message_id_required"}
    if not domain_id:
        return {"ok": False, "finding": "domain_id_required_for_queue_context_gate"}
    if not objective:
        return {"ok": False, "finding": "objective_required"}
    pickup_path, pickup_problem = _safe_existing_repo_file(root, pickup_receipt_rel)
    if pickup_problem or pickup_path is None:
        return {"ok": False, "finding": f"pickup_receipt_{pickup_problem}", "pickup_receipt_path": pickup_receipt_rel}
    loaded_pickup = _read_json_file(pickup_path)
    if loaded_pickup.get("ok") is not True:
        return {"ok": False, "finding": "pickup_receipt_unreadable", "pickup_receipt_path": pickup_receipt_rel, "pickup_receipt_load": loaded_pickup}
    pickup = dict(loaded_pickup.get("data") or {})
    if pickup.get("ok") is not True:
        return {"ok": False, "finding": "pickup_receipt_not_ok", "pickup_receipt_path": pickup_receipt_rel}
    if str(pickup.get("message_id") or "") != message_id:
        return {"ok": False, "finding": "pickup_receipt_message_id_mismatch", "pickup_message_id": pickup.get("message_id"), "message_id": message_id}
    if str(pickup.get("role_id") or "") != role_id:
        return {"ok": False, "finding": "pickup_receipt_role_id_mismatch", "pickup_role_id": pickup.get("role_id"), "role_id": role_id}
    if thread_id and str(pickup.get("thread_id") or "") != thread_id:
        return {"ok": False, "finding": "pickup_receipt_thread_id_mismatch", "pickup_thread_id": pickup.get("thread_id"), "thread_id": thread_id}
    if str(pickup.get("ref_status") or "") != "picked_up":
        return {"ok": False, "finding": "pickup_receipt_not_picked_up", "pickup_ref_status": pickup.get("ref_status")}

    message_rel = str(payload.get("source_message_path") or pickup.get("message_path") or "").strip()
    inbox_rel = str(payload.get("source_inbox_ref") or pickup.get("inbox_ref_path") or "").strip()
    thread_rel = str(payload.get("source_thread_path") or pickup.get("thread_path") or "").strip()
    required_paths = [pickup_receipt_rel, message_rel, inbox_rel]
    if thread_rel:
        required_paths.append(thread_rel)
    missing: list[dict[str, str]] = []
    for rel_path in required_paths:
        _path, problem = _safe_existing_repo_file(root, rel_path)
        if problem:
            missing.append({"path": rel_path, "finding": problem})
    if missing:
        return {"ok": False, "finding": "dispatch_required_evidence_missing", "missing": missing}

    proof_correlation_id = str(payload.get("proof_correlation_id") or f"agent_comms_dispatch:{message_id}:{agent_role}").strip()
    context_refs = [path for path in [message_rel, inbox_rel, thread_rel, pickup_receipt_rel] if path]
    return {
        "ok": True,
        "proof_correlation_id": proof_correlation_id,
        "role_id": role_id,
        "agent_role": agent_role,
        "consumer_role_id": str(payload.get("consumer_role_id") or role_id),
        "domain_id": domain_id,
        "message_id": message_id,
        "thread_id": str(pickup.get("thread_id") or thread_id),
        "objective": objective,
        "pickup_receipt_path": pickup_receipt_rel,
        "source_agent_comms_message_path": message_rel,
        "source_agent_comms_inbox_ref": inbox_rel,
        "source_agent_comms_thread_path": thread_rel,
        "context_refs": context_refs,
        "model_route": {
            "requested_model": str(payload.get("requested_model") or ""),
            "requested_reasoning_effort": str(payload.get("requested_reasoning_effort") or ""),
            "model_override_reason": str(payload.get("model_override_reason") or ""),
            "codex_model_override": dict(payload.get("codex_model_override") or {}),
            "frontier_required": True,
            "spark_allowed": False,
        },
        "would_enqueue_codex_work_request": True,
        "would_start_worker": False,
        "dispatch_status_after_enqueue": "queued_not_started",
        "required_for_enqueue": ["idempotency_key", CONFIRMATION_TOKEN],
        "claim_boundary": "queued_work_request_only_not_worker_execution_or_autonomous_reaction",
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def domain_weaver_agents_comms_dispatch_preview(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    payload = _domain_weaver_comms_dispatch_payload(args)
    preview = _domain_weaver_comms_dispatch_preview_result(shell_root, payload)
    return _ok(
        "domainWeaverAgentsCommsDispatchPreview",
        {
            "dispatch_preview": preview,
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def domain_weaver_agents_comms_dispatch_enqueue(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    _confirmation, idempotency_key, blocked = _mutation_fields(args)
    if blocked:
        return blocked
    payload = _domain_weaver_comms_dispatch_payload(args)
    preview = _domain_weaver_comms_dispatch_preview_result(shell_root, payload)
    if preview.get("ok") is not True:
        receipt_path = _write_receipt(
            shell_root,
            operation="domain_weaver_agents_comms_dispatch_enqueue",
            service_id="agent_comms",
            idempotency_key=idempotency_key,
            receipt_stage="blocked",
            payload={"ok": False, "preview": preview, "accepted_state_claim": False, "secrets_authority": False},
        )
        return _blocked(
            "domain_weaver_agent_comms_dispatch_refused",
            refusal_class="AGENT_COMMS_DISPATCH_REFUSED",
            data={"dispatch_preview": preview, "receipt_path": receipt_path},
        )

    context_refs = list(preview.get("context_refs") or [])
    proof_correlation_id = str(preview.get("proof_correlation_id") or "")
    dispatch_objective = "\n".join(
        [
            f"Domain Weaver agent-comms dispatch for {preview.get('agent_role')}.",
            "",
            f"Operator objective: {preview.get('objective')}",
            "",
            "Source proof:",
            f"- proof_correlation_id: {proof_correlation_id}",
            f"- source_agent_comms_message_id: {preview.get('message_id')}",
            f"- source_agent_comms_thread_id: {preview.get('thread_id')}",
            f"- pickup_receipt_path: {preview.get('pickup_receipt_path')}",
            "",
            "Required posture:",
            "- Treat this as queued_not_started until queue-runner proof exists.",
            "- Do not claim autonomous reaction from delivery, pickup, or queue request creation.",
            "- Return proof sections and blockers; do not claim accepted state.",
        ]
    )
    invocation_packet = {
        "schema_id": "ion.agent_invocation_packet.v1",
        "idempotency_key": idempotency_key,
        "created_by": "domain_weaver_agents.comms_dispatch_enqueue",
        "agent_role": str(preview.get("agent_role") or ""),
        "domain_id": str(preview.get("domain_id") or ""),
        "objective": dispatch_objective,
        "work_class": str(payload.get("work_class") or "domain_weaver_agent_comms_dispatch"),
        "risk_level": str(payload.get("risk_level") or "medium"),
        "route_family": str(payload.get("route_family") or "domain_weaver_agent_comms"),
        "requested_model": str(payload.get("requested_model") or ""),
        "requested_reasoning_effort": str(payload.get("requested_reasoning_effort") or ""),
        "model_override_reason": str(payload.get("model_override_reason") or ""),
        "codex_model_override": dict(payload.get("codex_model_override") or {}),
        "capsule_context": {
            "mode": "refs_and_inline_summary",
            "context_refs": context_refs,
            "required_reads": context_refs,
            "inline_summary": (
                f"Dispatch from picked-up Domain Weaver agent comms message {preview.get('message_id')} "
                f"for {preview.get('agent_role')}; pickup receipt {preview.get('pickup_receipt_path')}. "
                "Queue request creation is not worker execution."
            ),
            "source_posture": "candidate_agent_comms_pickup",
        },
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "local_write_authority": "none",
            "requires_operator_approval": False,
            "allowed_paths": ["ION/"],
            "forbidden_paths": [".env", "secrets", "credentials"],
        },
        "execution": {
            "backend": "codex_cli",
            "queue": True,
            "start": False,
            "max_runtime_seconds": int(payload.get("timeout_seconds") or 1800),
            "stop_condition": "return proof packet, relay question, or blocker",
        },
        "proof_required": {
            "context_receipt": True,
            "template_action_proof": True,
            "changed_files_summary": True,
            "tests_or_validation": True,
            "receipt": True,
            "source_agent_comms_message_id": str(preview.get("message_id") or ""),
            "pickup_receipt_path": str(preview.get("pickup_receipt_path") or ""),
            "domain_id": str(preview.get("domain_id") or ""),
        },
        "relay_policy": {
            "allow_relay_to_chatgpt": True,
            "allow_relay_to_operator": True,
            "ask_operator_on_authority_gap": True,
            "no_silent_authority_expansion": True,
        },
        "settlement": {
            "settlement_target": "domain_weaver_steward",
            "terminal_states": ["accepted", "blocked", "deferred", "rejected", "failed"],
        },
        "production_authority": False,
        "live_execution_authority": False,
    }
    result = invoke_bounded_agent(shell_root, invocation_packet)
    annotation = {
        "schema_id": "ion.domain_weaver.agent_comms_dispatch.annotation.v0_1",
        "proof_correlation_id": proof_correlation_id,
        "source_agent_comms_message_id": preview.get("message_id"),
        "source_agent_comms_message_path": preview.get("source_agent_comms_message_path"),
        "source_agent_comms_thread_id": preview.get("thread_id"),
        "source_agent_comms_thread_path": preview.get("source_agent_comms_thread_path"),
        "source_agent_comms_inbox_ref": preview.get("source_agent_comms_inbox_ref"),
        "pickup_receipt_path": preview.get("pickup_receipt_path"),
        "consumer_role_id": preview.get("consumer_role_id"),
        "domain_id": preview.get("domain_id"),
        "dispatch_status": "queued_not_started" if result.get("ok") else "dispatch_failed",
        "claim_boundary": "work_request_creation_only_not_queue_run_not_worker_execution_not_autonomous_reaction",
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }
    if result.get("ok"):
        for rel_key in ("invocation_path", "codex_work_request_path"):
            rel_path = str(result.get(rel_key) or "")
            target, problem = _safe_existing_repo_file(shell_root, rel_path)
            if target is not None and not problem:
                loaded = _read_json_file(target)
                if loaded.get("ok") is True:
                    data = dict(loaded.get("data") or {})
                    data["domain_weaver_agent_comms_dispatch"] = annotation
                    for key, value in annotation.items():
                        if key not in {"schema_id", "claim_boundary"}:
                            data[key] = value
                    _write_json_file(target, data)
    receipt_path = _write_receipt(
        shell_root,
        operation="domain_weaver_agents_comms_dispatch_enqueue",
        service_id="agent_comms",
        idempotency_key=idempotency_key,
        receipt_stage="post",
        payload={
            "ok": result.get("ok"),
            "dispatch_preview": preview,
            "invocation_result": result,
            "annotation": annotation,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )
    if result.get("ok") is not True:
        return _blocked(
            "domain_weaver_agent_comms_dispatch_enqueue_failed",
            refusal_class="AGENT_COMMS_DISPATCH_FAILED",
            data={"dispatch_preview": preview, "invocation_result": result, "receipt_path": receipt_path},
        )
    return _ok(
        "domainWeaverAgentsCommsDispatchEnqueue",
        {
            "dispatch_result": result,
            "dispatch_preview": preview,
            "dispatch_status": "queued_not_started",
            "receipt_path": receipt_path,
            "mutates_active_state": True,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


CODEX_SPARK_MODEL_ALIASES = (
    "codex-5.3-spark",
    "codex_5_3_spark",
    "codex-spark",
    "spark",
)
CODEX_HIGH_STAKES_ROUTE_FAMILIES = {
    "red_alert",
    "action_native_mount",
    "authority_security",
    "gpt_builder",
    "settlement",
    "branch_gateway_mount_equivalence",
    "operator_release_packaging",
}
CODEX_SPARK_SAFE_ROUTE_FAMILIES = {
    "scout",
    "large_artifact_summary",
    "large_artifact_index",
    "code_cartography",
    "routine_plan",
    "low_risk_research",
}


def _codex_config_status() -> dict[str, Any]:
    paths = [Path.home() / ".codex/config.toml"]
    for path in paths:
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            return {"config_exists": True, "config_path": path.as_posix(), "read_ok": False, "finding": exc.__class__.__name__}
        safe: dict[str, str] = {}
        for line in text.splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip().strip('"').strip("'")
            if key in {"model", "model_provider", "provider", "service_tier", "reasoning_effort", "approval_policy", "sandbox_mode"}:
                safe[key] = value.strip().strip('"').strip("'")[:120]
        return {"config_exists": True, "config_path": path.as_posix(), "read_ok": True, "safe_fields": safe}
    return {"config_exists": False, "config_path": paths[0].as_posix(), "read_ok": False, "safe_fields": {}}


def codex_model_capability_status(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    config = _codex_config_status()
    safe_fields = config.get("safe_fields", {}) if isinstance(config.get("safe_fields"), Mapping) else {}
    configured_model = str(safe_fields.get("model") or "")
    spark_configured = configured_model in CODEX_SPARK_MODEL_ALIASES or "spark" in configured_model.lower()
    return _ok(
        "codexModelCapabilityStatus",
        {
            "config": config,
            "spark_aliases": list(CODEX_SPARK_MODEL_ALIASES),
            "spark_configured_in_default_model": spark_configured,
            "spark_request_supported_by_packet_schema": True,
            "spark_actual_cli_call_verified": False,
            "high_stakes_route_families_require_frontier": sorted(CODEX_HIGH_STAKES_ROUTE_FAMILIES),
            "spark_safe_route_families": sorted(CODEX_SPARK_SAFE_ROUTE_FAMILIES),
            "recommended_default_spark_model": "codex-5.3-spark",
            "recommended_spark_reasoning_effort": "low",
            "secrets_exposed": False,
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def codex_model_route_preview(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    route_family = str(args.get("route_family") or "scout").strip() or "scout"
    requested_model = str(args.get("requested_model") or "codex-5.3-spark").strip()
    requested_effort = str(args.get("requested_reasoning_effort") or "low").strip() or "low"
    high_stakes = route_family in CODEX_HIGH_STAKES_ROUTE_FAMILIES
    selected_model = "gpt-5.5" if high_stakes else requested_model
    selected_effort = "xhigh" if high_stakes else requested_effort
    return _ok(
        "codexModelRoutePreview",
        {
            "route_family": route_family,
            "requested_model": requested_model,
            "requested_reasoning_effort": requested_effort,
            "selected_model": selected_model,
            "selected_reasoning_effort": selected_effort,
            "spark_allowed": not high_stakes,
            "frontier_required": high_stakes,
            "reason": "high_stakes_route_family_requires_gpt_5_5" if high_stakes else "low_risk_route_family_may_use_requested_model",
            "codex_model_override": {
                "selected_model": selected_model,
                "selected_reasoning_effort": selected_effort,
                "reason": "route_family_model_policy_preview",
            },
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def codex_spark_scout_packet_preview(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    objective = str(args.get("objective") or "Scout/index a large artifact or low-risk code area.").strip()
    route_family = str(args.get("route_family") or "scout").strip() or "scout"
    route_preview = codex_model_route_preview(
        root,
        {
            "route_family": route_family,
            "requested_model": str(args.get("requested_model") or "codex-5.3-spark"),
            "requested_reasoning_effort": str(args.get("requested_reasoning_effort") or "low"),
        },
    )
    selected = route_preview
    packet = {
        "objective": objective,
        "work_class": "scout",
        "risk_level": "low",
        "route_family": route_family,
        "requested_model": selected.get("selected_model"),
        "requested_reasoning_effort": selected.get("selected_reasoning_effort"),
        "codex_model_override": selected.get("codex_model_override"),
        "requires_confirmation_to_enqueue": True,
        "suggested_branch_call": {
            "branch_id": "codex_queue",
            "route_id": "request_work_packet",
            "expected_route_schema_version": "v0",
            "args": {
                "objective": objective,
                "work_class": "scout",
                "risk_level": "low",
                "route_family": route_family,
                "requested_model": selected.get("selected_model"),
                "requested_reasoning_effort": selected.get("selected_reasoning_effort"),
                "codex_model_override": selected.get("codex_model_override"),
                "confirmation": CONFIRMATION_TOKEN,
                "idempotency_key": "spark-scout-<stable-id>",
            },
        },
    }
    return _ok(
        "codexSparkScoutPacketPreview",
        {
            "packet_preview": packet,
            "would_enqueue": False,
            "spark_allowed": selected.get("spark_allowed"),
            "frontier_required": selected.get("frontier_required"),
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def codex_spark_scout_args_validate(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    preview = codex_spark_scout_packet_preview(root, args)
    packet = preview.get("packet_preview", {}) if isinstance(preview.get("packet_preview"), Mapping) else {}
    call = packet.get("suggested_branch_call", {}) if isinstance(packet.get("suggested_branch_call"), Mapping) else {}
    call_args = call.get("args", {}) if isinstance(call.get("args"), Mapping) else {}
    override = call_args.get("codex_model_override", {}) if isinstance(call_args.get("codex_model_override"), Mapping) else {}
    generated_model_args = {
        "model": override.get("selected_model") or call_args.get("requested_model"),
        "reasoning_effort": override.get("selected_reasoning_effort") or call_args.get("requested_reasoning_effort"),
    }
    findings: list[str] = []
    if generated_model_args["model"] not in CODEX_SPARK_MODEL_ALIASES and call_args.get("route_family") not in CODEX_HIGH_STAKES_ROUTE_FAMILIES:
        findings.append("selected_model_not_spark_alias_for_low_risk_route")
    if not generated_model_args.get("reasoning_effort"):
        findings.append("reasoning_effort_missing")
    if "service_tier" in call_args or "service_tier" in override or "service_tier" in generated_model_args:
        findings.append("service_tier_override_present")
    if call.get("route_id") != "request_work_packet":
        findings.append("suggested_route_not_request_work_packet")
    if call_args.get("confirmation") != CONFIRMATION_TOKEN:
        findings.append("confirmation_token_missing_from_enqueue_shape")
    if not call_args.get("idempotency_key"):
        findings.append("idempotency_key_missing_from_enqueue_shape")
    return _ok(
        "codexSparkScoutArgsValidate",
        {
            "valid": not findings,
            "findings": findings,
            "generated_model_args": generated_model_args,
            "forbidden_generated_keys_absent": {"service_tier": "service_tier" not in generated_model_args},
            "packet_preview": packet,
            "would_enqueue": False,
            "would_call_codex": False,
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def codex_transient_usage_limit_bridge_preview(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_codex_queue_runner import preview_codex_transient_usage_limit_bridge

    result = preview_codex_transient_usage_limit_bridge(
        root,
        run_packet_path=str(args.get("run_packet_path") or args.get("bridge_run_packet") or ""),
        idempotency_key=str(args.get("idempotency_key") or "") or None,
        bridge_mode=str(args.get("bridge_mode") or "parent_session_relay"),
    )
    return _ok(
        "codexTransientUsageLimitBridgePreview",
        {
            "preview_result": result,
            "would_create_bridge": bool(result.get("would_create_bridge")),
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def codex_transient_usage_limit_bridge_create(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    from .ion_codex_queue_runner import bridge_codex_transient_usage_limit_request

    result = bridge_codex_transient_usage_limit_request(
        root,
        run_packet_path=str(args.get("run_packet_path") or args.get("bridge_run_packet") or ""),
        confirmation=str(args.get("confirmation") or ""),
        idempotency_key=str(args.get("idempotency_key") or ""),
        bridge_mode=str(args.get("bridge_mode") or "parent_session_relay"),
        requested_by=str(args.get("agent_id") or "codex_carrier_steward"),
    )
    if result.get("ok") is not True:
        return _blocked(
            "codex_transient_usage_limit_bridge_create_blocked",
            refusal_class=str(result.get("result") or "CODEX_CARRIER_BRIDGE_BLOCKED"),
            data={"bridge_result": result},
        )
    return _ok(
        "codexTransientUsageLimitBridgeCreate",
        {
            "bridge_result": result,
            "receipt_path": result.get("receipt_path"),
            "relay_request_path": result.get("relay_request_path"),
            "mutates_active_state": True,
            "task_return_created": False,
            "accepted_for_carrier_intake": False,
            "automatic_agent_reaction_proven": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def _compact_archive_attachment(path: Path, root: Path) -> dict[str, Any]:
    loaded = _read_json_file(path)
    data = loaded.get("data") if loaded.get("ok") is True and isinstance(loaded.get("data"), Mapping) else {}
    return {
        "path": _repo_rel(path, root),
        "ok": loaded.get("ok") is True,
        "attachment_id": data.get("attachment_id"),
        "session_id": data.get("session_id"),
        "thread_name": data.get("thread_name"),
        "created_at": data.get("created_at"),
        "raw_transcript_exported": data.get("raw_transcript_exported", False),
        "hidden_reasoning_exposed": data.get("hidden_reasoning_exposed", False),
        "production_authority": data.get("production_authority", False),
        "live_execution_authority": data.get("live_execution_authority", False),
    }


def browser_codex_agent_status(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    agent_summary = latest_codex_browser_agent_summary(shell_root)
    archive = build_codex_conversation_archive(shell_root, session_limit=int(args.get("session_limit") or 12), query=str(args.get("query") or "") or None)
    attachments_root = shell_root / "ION/05_context/current/codex_capsule_chat/archive_attachments"
    attachments = []
    if attachments_root.is_dir():
        attachments = [_compact_archive_attachment(path, shell_root) for path in sorted(attachments_root.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:12]]
    return _ok(
        "browserCodexAgentStatus",
        {
            "codex_browser_agent": agent_summary,
            "archive_verdict": archive.get("verdict"),
            "archive_source_counts": archive.get("source_counts", {}),
            "current_session_id": archive.get("current_session_id"),
            "session_count_returned": len(archive.get("sessions", []) if isinstance(archive.get("sessions"), list) else []),
            "archive_attachments_dir": _repo_rel(attachments_root, shell_root),
            "archive_attachment_count_sampled": len(attachments),
            "archive_attachments": attachments,
            "playwright_execution_authority": "not_granted_by_this_route",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
            "raw_transcript_exported": False,
        },
    )


def codex_archive_search_preview(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    query = str(args.get("query") or "").strip() or None
    limit = max(1, min(int(args.get("session_limit") or 12), 40))
    archive = build_codex_conversation_archive(shell_root, session_limit=limit, query=query)
    sessions = archive.get("sessions", []) if isinstance(archive.get("sessions"), list) else []
    return _ok(
        "codexArchiveSearchPreview",
        {
            "query": query or "",
            "archive_verdict": archive.get("verdict"),
            "source_counts": archive.get("source_counts", {}),
            "sessions": [
                {
                    "session_id": item.get("session_id"),
                    "display_title": item.get("display_title") or item.get("thread_name"),
                    "updated_at": item.get("updated_at"),
                    "project_label": item.get("project_label"),
                    "mission_labels": item.get("mission_labels", [])[:6] if isinstance(item.get("mission_labels"), list) else [],
                    "agent_labels": item.get("agent_labels", [])[:6] if isinstance(item.get("agent_labels"), list) else [],
                    "raw_transcript_exported": item.get("raw_transcript_exported", False),
                }
                for item in sessions[:limit]
            ],
            "selected_session_excerpt": archive.get("selected_session_excerpt"),
            "raw_transcript_exported": False,
            "hidden_reasoning_exposed": False,
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def codex_archive_attach_preview(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    session_id = str(args.get("session_id") or "").strip()
    if not session_id:
        return _blocked("session_id_required", refusal_class="SCHEMA_INVALID")
    shell_root = _resolve_root(root)
    archive = build_codex_conversation_archive(shell_root, session_limit=1, selected_session_id=session_id, selected_window_count=24)
    selected = archive.get("selected_session_excerpt") if isinstance(archive.get("selected_session_excerpt"), Mapping) else {}
    found = bool(selected.get("found"))
    return _ok(
        "codexArchiveAttachPreview",
        {
            "session_id": session_id,
            "found": found,
            "would_write_attachment_packet": found,
            "required_for_attach": ["idempotency_key", CONFIRMATION_TOKEN],
            "attach_route": "browser_codex_agent.codex_archive_attach",
            "selected_excerpt_summary": {
                "item_count": selected.get("item_count"),
                "display_mode": selected.get("display_mode"),
                "window_start_index": selected.get("window_start_index"),
                "window_end_index": selected.get("window_end_index"),
                "raw_transcript_exported": selected.get("raw_transcript_exported", False),
                "hidden_reasoning_exposed": selected.get("hidden_reasoning_exposed", False),
            },
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def codex_archive_attach(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    _confirmation, idempotency_key, blocked = _mutation_fields(args)
    if blocked:
        return blocked
    session_id = str(args.get("session_id") or "").strip()
    if not session_id:
        return _blocked("session_id_required", refusal_class="SCHEMA_INVALID")
    result = attach_codex_conversation_to_chat(
        shell_root,
        session_id=session_id,
        confirmation=CONFIRMATION_TOKEN,
        prompt=str(args.get("prompt") or "").strip() or None,
    )
    attachment = result.get("attachment") if isinstance(result.get("attachment"), Mapping) else {}
    receipt_path = _write_receipt(
        shell_root,
        operation="browser_codex_agent_archive_attach",
        service_id="codex_conversation_archive",
        idempotency_key=idempotency_key,
        receipt_stage="post",
        payload={
            "ok": result.get("ok"),
            "finding": result.get("finding"),
            "attachment_id": attachment.get("attachment_id"),
            "session_id": session_id,
            "packet_path": attachment.get("packet_path"),
            "raw_transcript_exported": False,
            "hidden_reasoning_exposed": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )
    if result.get("ok") is not True:
        return _blocked("codex_archive_attach_failed", refusal_class="CODEX_ARCHIVE_ATTACH_FAILED", data={"result": result, "receipt_path": receipt_path})
    return _ok(
        "codexArchiveAttach",
        {
            "attach_result": result,
            "receipt_path": receipt_path,
            "mutates_active_state": True,
            "accepted_state_claim": False,
            "secrets_authority": False,
            "raw_transcript_exported": False,
        },
    )


def playwright_work_preview(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    objective = str(args.get("objective") or "Run a browser/Playwright Codex-agent smoke or inspection.").strip()
    target_url = str(args.get("target_url") or "").strip() or "<target-url>"
    summary = latest_codex_browser_agent_summary(_resolve_root(root))
    return _ok(
        "playwrightWorkPreview",
        {
            "objective": objective,
            "target_url": target_url,
            "codex_browser_agent_summary": summary,
            "recommended_commands": [
                "PYTHONPATH=ION/04_packages python3 -S -m kernel.ion_codex_browser_agent --ion-root . --plan --json",
                f"PYTHONPATH=ION/04_packages python3 -S -m kernel.ion_codex_browser_agent --ion-root . --inspect --profile-id browser-gpt --target-url {target_url} --json",
            ],
            "recommended_branch_calls": [
                {"branch_id": "browser_codex_agent", "route_id": "browser_codex_agent_status"},
                {"branch_id": "codex_queue", "route_id": "spark_scout_packet_preview", "args": {"objective": objective, "route_family": "large_artifact_index"}},
            ],
            "would_launch_browser": False,
            "would_call_playwright": False,
            "requires_future_gates_for_execution": ["idempotency_key", CONFIRMATION_TOKEN, "operator_approval_for_browser_or_playwright_execution"],
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def browser_agent_contact(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    contact = build_codex_browser_agent_action_contact(_resolve_root(root))
    return _ok(
        "browserAgentContact",
        {
            "contact": contact,
            "tag": contact.get("tag") or contact.get("contact_tag") or contact.get("agent_tag"),
            "silent_send": bool(contact.get("silent_send", False)),
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
        },
    )


def _browser_agent_invoke_packet(args: Mapping[str, Any]) -> dict[str, Any]:
    objective = str(args.get("objective") or "Inspect Browser GPT / Playwright agent state.").strip()
    return {
        "objective": objective,
        "agent_role": str(args.get("agent_role") or "role.browser_dom_cartographer"),
        "agent_display_name": str(args.get("agent_display_name") or "Browser DOM Cartographer"),
        "queue": bool(args.get("queue", False)),
        "target_url": str(args.get("target_url") or ""),
        "source_refs": args.get("source_refs") if isinstance(args.get("source_refs"), list) else [],
        "context_refs": args.get("context_refs") if isinstance(args.get("context_refs"), list) else [],
        "silent_send": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def browser_agent_invoke_preview(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    packet = _browser_agent_invoke_packet(args)
    return _ok(
        "browserAgentInvokePreview",
        {
            "packet_preview": packet,
            "would_invoke": False,
            "would_queue": bool(packet.get("queue")),
            "required_for_invoke": ["idempotency_key", CONFIRMATION_TOKEN],
            "invoke_route": "browser_codex_agent.browser_agent_invoke",
            "mutates_active_state": False,
            "accepted_state_claim": False,
            "secrets_authority": False,
            "silent_send": False,
        },
    )


def browser_agent_invoke(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_root(root)
    _confirmation, idempotency_key, blocked = _mutation_fields(args)
    if blocked:
        return blocked
    packet = _browser_agent_invoke_packet(args)
    packet["idempotency_key"] = idempotency_key
    result = submit_codex_browser_agent_action_invocation(shell_root, packet)
    invocation = result.get("invocation") if isinstance(result.get("invocation"), Mapping) else {}
    receipt_path = _write_receipt(
        shell_root,
        operation="browser_agent_invoke",
        service_id="codex_browser_agent",
        idempotency_key=idempotency_key,
        receipt_stage="post",
        payload={
            "ok": result.get("ok"),
            "status": result.get("status") or invocation.get("status"),
            "finding": result.get("finding") or invocation.get("finding"),
            "agent_role": result.get("agent_role") or invocation.get("agent_role"),
            "agent_tag": result.get("agent_tag"),
            "invocation_id": result.get("invocation_id") or invocation.get("invocation_id"),
            "invocation_path": result.get("invocation_path") or invocation.get("invocation_path"),
            "codex_work_request_path": result.get("codex_work_request_path") or invocation.get("codex_work_request_path"),
            "queue": packet.get("queue"),
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_claim": False,
            "silent_send": False,
        },
    )
    if result.get("ok") is not True:
        return _blocked("browser_agent_invoke_failed", refusal_class="BROWSER_AGENT_INVOKE_FAILED", data={"result": result, "receipt_path": receipt_path})
    return _ok(
        "browserAgentInvoke",
        {
            "invoke_result": result,
            "receipt_path": receipt_path,
            "mutates_active_state": True,
            "accepted_state_claim": False,
            "secrets_authority": False,
            "silent_send": False,
        },
    )


def invoke_runtime_service_route(root: str | Path | None, *, route_id: str, args: Mapping[str, Any]) -> dict[str, Any]:
    if route_id == "service_status":
        return service_status(root, args)
    if route_id == "service_reload_plan":
        return service_reload_plan(root, args)
    if route_id == "restart_service":
        return restart_service(root, args)
    if route_id == "retest_service":
        return retest_service(root, args)
    if route_id == "reload_and_retest":
        return reload_and_retest(root, args)
    if route_id == "focused_test_plan":
        return focused_test_plan(root, args)
    if route_id == "focused_test_run":
        return focused_test_run(root, args)
    if route_id in {"focused_test_receipts", "receipts"}:
        return focused_test_receipts(root, args)
    if route_id in {"focused_test_suite_manifest", "suite_manifest"}:
        return focused_test_suite_manifest(root, args)
    if route_id == "runtime_freshness_probe":
        return runtime_freshness_probe(root, args)
    if route_id == "tool_manifest_deep":
        return local_intelligence_tool_manifest_deep(root, args)
    if route_id == "code_symbol_index":
        return local_intelligence_code_symbol_index(root, args)
    if route_id == "dag_extract":
        return local_intelligence_dag_extract(root, args)
    if route_id == "data_profile":
        return local_intelligence_data_profile(root, args)
    if route_id == "receipt_graph":
        return local_intelligence_receipt_graph(root, args)
    if route_id == "local_search_plus":
        return local_intelligence_local_search_plus(root, args)
    if route_id == "context_pack_compile_plus":
        return local_intelligence_context_pack_compile_plus(root, args)
    if route_id == "lexical_index_manifest":
        return local_intelligence_lexical_index_manifest(root, args)
    if route_id == DOMAIN_WEAVER_SWARM_EXPANSION_INDEX_ROUTE_ID:
        return local_intelligence_domain_weaver_swarm_expansion_index(root, args)
    if route_id == "large_file_profile":
        return large_file_profile(root, args)
    if route_id == "large_file_chunk_manifest":
        return large_file_chunk_manifest(root, args)
    if route_id == "large_file_slice_read":
        return large_file_slice_read(root, args)
    if route_id == "large_file_stream_start":
        return large_file_stream_start(root, args)
    if route_id == "large_file_stream_next":
        return large_file_stream_next(root, args)
    if route_id == "large_file_stream_range":
        return large_file_stream_range(root, args)
    if route_id == "large_file_anchor_search":
        return large_file_anchor_search(root, args)
    if route_id == "large_file_symbol_index":
        return large_file_symbol_index(root, args)
    if route_id == "large_file_json_path_read":
        return large_file_json_path_read(root, args)
    if route_id == "large_file_section_read":
        return large_file_section_read(root, args)
    if route_id == "large_artifact_claim_check":
        return large_artifact_claim_check(root, args)
    if route_id == "zip_request_preview":
        return zip_request_preview(root, args)
    if route_id == "zip_materialize_request":
        return zip_materialize_request(root, args)
    if route_id == "zip_manifest_read":
        return zip_manifest_read(root, args)
    if route_id == "sandbox_upload_instruction":
        return sandbox_upload_instruction(root, args)
    if route_id == "sandbox_intake_manifest_preview":
        return sandbox_intake_manifest_preview(root, args)
    if route_id == "inference_provider_status":
        return inference_provider_status(root, args)
    if route_id == "inference_plan_preview":
        return inference_plan_preview(root, args)
    if route_id == "large_artifact_inference_index_preview":
        return large_artifact_inference_index_preview(root, args)
    if route_id == "large_artifact_inference_question_preview":
        return large_artifact_inference_question_preview(root, args)
    if route_id == "domain_weaver_status":
        return domain_weaver_agents_status(root, args)
    if route_id == "context_active_resolver_status":
        return domain_weaver_context_active_resolver_status(root, args)
    if route_id == "resolve_context_active":
        return domain_weaver_resolve_context_active(root, args)
    if route_id == "active_context_reissue_preflight":
        return domain_weaver_active_context_reissue_preflight(root, args)
    if route_id == "active_context_gated_refresh_plan":
        return domain_weaver_active_context_gated_refresh_plan(root, args)
    if route_id == "active_context_gated_refresh_apply":
        return domain_weaver_active_context_gated_refresh_apply(root, args)
    if route_id == "worker_start_readiness":
        return domain_weaver_worker_start_readiness(root, args)
    if route_id == "worker_start_readiness_summary":
        return domain_weaver_worker_start_readiness_summary(root, args)
    if route_id == "worker_start_backlog_hygiene":
        return domain_weaver_worker_start_backlog_hygiene(root, args)
    if route_id == "spawn_dispatch_start_plan":
        return domain_weaver_spawn_dispatch_start_plan(root, args)
    if route_id == "spawn_dispatch_legacy_receipt_quarantine":
        return domain_weaver_spawn_dispatch_legacy_receipt_quarantine(root, args)
    if route_id == "pressure_wave_plan":
        return domain_weaver_pressure_wave_plan(root, args)
    if route_id == "pressure_wave_spawn_request_seed":
        return domain_weaver_pressure_wave_spawn_request_seed(root, args)
    if route_id == "projection_summary":
        return domain_weaver_agents_projection_summary(root, args)
    if route_id == "projection_accepted_refresh_plan":
        return domain_weaver_projection_accepted_refresh_plan(root, args)
    if route_id == "projection_replacement_body_candidate":
        return domain_weaver_projection_replacement_body_candidate(root, args)
    if route_id == "projection_accepted_refresh_apply":
        return domain_weaver_projection_accepted_refresh_apply(root, args)
    if route_id == "semantic_alias_supervised_apply_preflight":
        return domain_weaver_semantic_alias_supervised_apply_preflight(root, args)
    if route_id == "semantic_alias_projection_apply":
        return domain_weaver_semantic_alias_projection_apply(root, args)
    if route_id == "semantic_alias_mount_manifest_apply":
        return domain_weaver_semantic_alias_mount_manifest_apply(root, args)
    if route_id == "comms_overview":
        return domain_weaver_agents_comms_overview(root, args)
    if route_id == "spawn_plan_preview":
        return domain_weaver_agents_spawn_plan_preview(root, args)
    if route_id == "comms_send_preview":
        return domain_weaver_agents_comms_send_preview(root, args)
    if route_id == "comms_send":
        return domain_weaver_agents_comms_send(root, args)
    if route_id == "comms_pickup_preview":
        return domain_weaver_agents_comms_pickup_preview(root, args)
    if route_id == "comms_pickup":
        return domain_weaver_agents_comms_pickup(root, args)
    if route_id == "comms_autoreaction_proof":
        return domain_weaver_agents_comms_autoreaction_proof(root, args)
    if route_id == "comms_dispatch_preview":
        return domain_weaver_agents_comms_dispatch_preview(root, args)
    if route_id == "comms_dispatch_enqueue":
        return domain_weaver_agents_comms_dispatch_enqueue(root, args)
    if route_id == "codex_model_capability_status":
        return codex_model_capability_status(root, args)
    if route_id == "codex_model_route_preview":
        return codex_model_route_preview(root, args)
    if route_id == "spark_scout_packet_preview":
        return codex_spark_scout_packet_preview(root, args)
    if route_id == "spark_scout_args_validate":
        return codex_spark_scout_args_validate(root, args)
    if route_id == "transient_usage_limit_bridge_preview":
        return codex_transient_usage_limit_bridge_preview(root, args)
    if route_id == "transient_usage_limit_bridge_create":
        return codex_transient_usage_limit_bridge_create(root, args)
    if route_id == "browser_codex_agent_status":
        return browser_codex_agent_status(root, args)
    if route_id == "codex_archive_search_preview":
        return codex_archive_search_preview(root, args)
    if route_id == "codex_archive_attach_preview":
        return codex_archive_attach_preview(root, args)
    if route_id == "codex_archive_attach":
        return codex_archive_attach(root, args)
    if route_id == "playwright_work_preview":
        return playwright_work_preview(root, args)
    if route_id == "browser_agent_contact":
        return browser_agent_contact(root, args)
    if route_id == "browser_agent_invoke_preview":
        return browser_agent_invoke_preview(root, args)
    if route_id == "browser_agent_invoke":
        return browser_agent_invoke(root, args)
    return _blocked("route_not_supported_by_runtime_services", refusal_class="BRANCH_ROUTE_NOT_FOUND", data={"route_id": route_id})
