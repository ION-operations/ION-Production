"""Read-only Build workbench projection for the local cockpit.

The Build surface is an editor/control-plane preview. This module projects the
tools Codex may observe or request through existing bounded ION routes; it does
not expose arbitrary shell, direct TUI control, production authority, accepted
state authority, or secrets access.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .ion_codex_queue_runner import build_codex_queue_runner_status
from .ion_project_cockpit import build_project_cockpit_model
from .ion_project_workbench import (
    FORBIDDEN_PATH_PARTS,
    WRITE_CONFIRMATION_TOKEN,
    build_project_workbench_timeline,
    build_project_workspace_status,
)

SCHEMA_ID = "ion.build_workspace.v0_1"
READY_VERDICT = "ION_BUILD_WORKSPACE_READY"
AUTHORITY_CLASSES = [
    "LOCAL_COCKPIT_PROJECTION",
    "CANDIDATE_CONTEXT",
    "NO_PRODUCTION_AUTHORITY",
    "NO_LIVE_EXECUTION_AUTHORITY",
    "NO_ACCEPTED_STATE_CLAIM",
    "NO_SECRETS_AUTHORITY",
]
PARALLEL_PLAN_PREVIEW_FIELDS = [
    "read_set",
    "write_set",
    "authority_class",
    "dedupe_signature",
    "conflict_projection",
    "lease_decision",
]
EDIT_LEASE_REQUIRED_TOOLS = ["ion_project_patch_apply", "ion_bounded_patch_apply"]
CONDITIONAL_EDIT_LEASE_TOOLS = [
    "ion_file_put_text",
    "ion_artifact_upload_init",
    "ion_artifact_upload_chunk",
    "ion_artifact_upload_commit",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _safe_call(fallback: dict[str, Any], fn: Any, *args: Any, **kwargs: Any) -> dict[str, Any]:
    try:
        result = fn(*args, **kwargs)
    except Exception as exc:  # pragma: no cover - projection must fail soft in cockpit.
        return {**fallback, "ok": False, "finding": exc.__class__.__name__}
    return result if isinstance(result, dict) else fallback


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _string_list(value: Any, *, limit: int = 12) -> list[str]:
    if isinstance(value, str):
        return [value] if value.strip() else []
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        text = str(item or "").strip()
        if text:
            result.append(text)
        if len(result) >= limit:
            break
    return result


def _active_root_proof(root: Path) -> dict[str, Any]:
    return {
        "schema_id": "ion.build_workspace.active_root_proof.v0_1",
        "active_root": str(root),
        "pyproject_present": (root / "pyproject.toml").exists(),
        "repo_authority_present": (root / "ION/REPO_AUTHORITY.md").exists(),
        "content_root": "ION",
        "authority": {
            "production_authority": False,
            "live_execution_authority": False,
            "accepted_state_authority": False,
            "secrets_authority": False,
        },
    }


def _tool(
    tool_id: str,
    label: str,
    *,
    mode_ids: list[str],
    control_class: str,
    authority: str,
    status: str,
    endpoint: str | None = None,
    next_gate: str | None = None,
    description: str,
) -> dict[str, Any]:
    return {
        "tool_id": tool_id,
        "label": label,
        "mode_ids": mode_ids,
        "control_class": control_class,
        "authority": authority,
        "status": status,
        "endpoint": endpoint,
        "next_gate": next_gate,
        "description": description,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
        "secrets_authority": False,
    }


def _tool_contracts() -> list[dict[str, Any]]:
    all_modes = ["raw", "app", "world", "media", "flow", "docs"]
    return [
        _tool(
            "sandbox_reset",
            "Reset sandbox",
            mode_ids=all_modes,
            control_class="local_ui",
            authority="local_preview_only",
            status="enabled",
            description="Reset the isolated iframe to the selected starter document.",
        ),
        _tool(
            "sandbox_rollback",
            "Rollback preview",
            mode_ids=all_modes,
            control_class="local_ui",
            authority="local_preview_only",
            status="enabled_when_history_exists",
            description="Restore the previous iframe source document from local panel history.",
        ),
        _tool(
            "workspace_status",
            "Workspace status",
            mode_ids=all_modes,
            control_class="inspect_projection",
            authority="read_only_projection",
            status="ready",
            endpoint="/cockpit/build/workspace.json",
            description="Read registered project workspace, allowed paths, git status, receipts, and queue telemetry.",
        ),
        _tool(
            "file_slice_read",
            "Read file slice",
            mode_ids=all_modes,
            control_class="inspect_projection",
            authority="bounded_read",
            status="available_through_project_workbench",
            endpoint="/mcp",
            description="Bounded relative file reads through registered project APIs with path and byte limits.",
        ),
        _tool(
            "patch_preview",
            "Patch preview",
            mode_ids=["app", "world", "media", "flow", "docs"],
            control_class="patch_preview",
            authority="non_mutating_diff_preview",
            status="gated_route_available",
            endpoint="/mcp",
            next_gate="registered_project_and_path_allowlist",
            description="Generate a draft diff receipt without applying source changes.",
        ),
        _tool(
            "patch_apply",
            "Apply source edit",
            mode_ids=["app", "world", "media", "flow", "docs"],
            control_class="source_apply_revert",
            authority="requires_confirmation_and_edit_lease",
            status="requires_gate",
            endpoint="/mcp",
            next_gate="ION_BOUNDED_WRITE_CONFIRMED + active exclusive_write lease",
            description="Apply a revalidated bounded patch through project workbench only.",
        ),
        _tool(
            "project_action_run",
            "Run fixed action",
            mode_ids=["app", "world", "media", "flow", "docs"],
            control_class="fixed_project_action",
            authority="requires_confirmation",
            status="requires_gate",
            endpoint="/projects/cosmos/actions/run",
            next_gate="registered fixed action_id; no shell strings",
            description="Run a project spec command such as build/test/lint when registered and confirmed.",
        ),
        _tool(
            "browser_capture",
            "Capture preview",
            mode_ids=["app", "world", "media", "flow", "docs"],
            control_class="browser_capture",
            authority="evidence_capture_only",
            status="requires_gate",
            endpoint="/projects/cosmos/browser/capture",
            next_gate="allowlisted bookmark and bounded viewport",
            description="Capture screenshots and layout evidence; browser control remains forbidden.",
        ),
        _tool(
            "queue_codex_work",
            "Queue Codex work",
            mode_ids=all_modes,
            control_class="codex_queue_control",
            authority="durable_queue_only",
            status="requires_gate",
            endpoint="/cockpit/chat/queue",
            next_gate="bounded work packet confirmation",
            description="Submit durable Codex work through the existing queue runner path.",
        ),
        _tool(
            "codex_tui_direct_control",
            "Raw TUI control",
            mode_ids=all_modes,
            control_class="disabled_or_break_glass",
            authority="not_granted",
            status="disabled",
            description="Direct terminal key injection and arbitrary PTY control are intentionally not wired.",
        ),
    ]


def _mode_specs(tool_contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    mode_rows = [
        ("raw", "Raw expression", "expressive_docs", "Styled narrative, sources, images, motion.", []),
        ("app", "Apps", "react_app_surface", "Sites, apps, dashboards, product surfaces.", ["react"]),
        ("world", "Worlds", "3d_game_scene", "3D models, animation, games, simulation.", ["three", "@react-three/fiber"]),
        ("media", "Media", "image_video_studio", "Image, video, timeline, edit studio.", ["canvas", "media"]),
        ("flow", "Graphs", "data_flow_graphs", "Charts, data flows, node graphs.", ["charts"]),
        ("docs", "Docs", "latex_docs", "Documentation, equations, writing with AI.", ["latex"]),
    ]
    return [
        {
            "id": mode_id,
            "label": label,
            "kind": kind,
            "summary": summary,
            "deps": deps,
            "tool_ids": [
                str(tool.get("tool_id"))
                for tool in tool_contracts
                if mode_id in _string_list(tool.get("mode_ids"), limit=20)
            ],
            "base_workspace": {
                "template_id": mode_id,
                "isolated_iframe_required": True,
                "preview_crash_isolation": "iframe_srcdoc_error_boundary",
            },
        }
        for mode_id, label, kind, summary, deps in mode_rows
    ]


def _compact_queue_control(status: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "runner_state_path": status.get("runner_state_path"),
        "queue_path": status.get("queue_path"),
        "queued_request_count": _int(status.get("queued_request_count")),
        "next_request_path": status.get("next_request_path"),
        "lane_queue_path": status.get("lane_queue_path"),
        "lane_queue": dict(_as_mapping(status.get("lane_queue"))),
        "active_run": status.get("active_run") if isinstance(status.get("active_run"), Mapping) else None,
        "active_runs": [dict(row) for row in status.get("active_runs") or [] if isinstance(row, Mapping)][:6],
        "active_run_count": _int(status.get("active_run_count")),
        "active_process_running": bool(status.get("active_process_running")),
        "active_lane_locks": dict(_as_mapping(status.get("active_lane_locks"))),
        "concurrency": dict(_as_mapping(status.get("concurrency"))),
        "latest_runs": [dict(row) for row in status.get("latest_runs") or [] if isinstance(row, Mapping)][:5],
        "live_worker_telemetry": dict(_as_mapping(status.get("live_worker_telemetry"))),
        "parallel_plan_preview_fields": list(PARALLEL_PLAN_PREVIEW_FIELDS),
        "automation_surface": status.get("automation_surface"),
        "autorun_loop_state": status.get("autorun_loop_state"),
        "reconcile_mode": "read_only_no_reconcile",
    }


def _project_system_rows(project_cockpit: Mapping[str, Any], timeline: Mapping[str, Any], *, limit: int = 18) -> list[dict[str, Any]]:
    portfolio = _as_mapping(project_cockpit.get("portfolio"))
    organization_state = _as_mapping(project_cockpit.get("organization_state"))
    specialist = _as_mapping(organization_state.get("project_specialists"))
    families = [row for row in portfolio.get("families") or [] if isinstance(row, Mapping)]
    rows: list[dict[str, Any]] = []
    history = _as_mapping(timeline.get("history_counts"))
    visual = _as_mapping(timeline.get("visual_receipt"))
    for family in families[: max(1, limit)]:
        versions = [row for row in family.get("versions") or [] if isinstance(row, Mapping)]
        branches = [row for row in family.get("branches") or [] if isinstance(row, Mapping)]
        current = _as_mapping(family.get("current"))
        current_version = next((row for row in versions if row.get("is_current")), versions[0] if versions else {})
        branch = (
            current.get("branch_label")
            or _as_mapping(current_version).get("branch_label")
            or (branches[0].get("label") if branches else None)
            or current.get("branch_id")
            or "projected"
        )
        diff_count = _int(family.get("diff_count"), len([row for row in family.get("diffs") or [] if isinstance(row, Mapping)]))
        evidence = _string_list(
            [
                family.get("current_path"),
                family.get("organized_path"),
                current.get("path"),
                visual.get("latest_capture_screenshot_path"),
            ],
            limit=4,
        )
        rows.append(
            {
                "id": str(family.get("family_id") or current.get("project_id") or f"family_{len(rows) + 1}"),
                "label": str(family.get("label") or family.get("family_id") or current.get("project_id") or "Project family"),
                "status": str(
                    _as_mapping(family.get("operating_system")).get("posture")
                    or family.get("lineage_status")
                    or current.get("status")
                    or "projected"
                ),
                "branch": str(branch),
                "capsule": "active capsule"
                if specialist.get("status") == "project_specialist_contexts_ready"
                else str(specialist.get("status") or "capsule projected"),
                "diff": f"{diff_count} diff units",
                "notes": _int(family.get("doc_count")) + _int(family.get("reference_count")),
                "screenshots": _int(history.get("browser_capture_count")),
                "rollback": f"{_int(history.get('rollback_candidate_count'))} rollback candidates",
                "evidence": [item for item in evidence if item],
                "lanes": [
                    {"id": "branches", "label": "Branches", "value": str(_int(family.get("branch_count"))), "state": "projected"},
                    {"id": "diffs", "label": "Diffs", "value": str(diff_count), "state": "portfolio"},
                    {"id": "notes", "label": "Notes", "value": str(_int(family.get("doc_count"))), "state": "indexed"},
                    {"id": "shots", "label": "Shots", "value": str(_int(history.get("browser_capture_count"))), "state": "workbench"},
                    {"id": "capsules", "label": "Capsules", "value": str(specialist.get("project_specialist_capsule_count") or 0), "state": "candidate"},
                    {"id": "rollback", "label": "Rollback", "value": str(_int(history.get("rollback_candidate_count"))), "state": "candidate"},
                ],
            }
        )
    if rows:
        return rows
    return [
        {
            "id": "ion_dev",
            "label": "ION Development",
            "status": "projected",
            "branch": "active_ion_control",
            "capsule": str(specialist.get("status") or "context projected"),
            "diff": "deferred",
            "notes": 0,
            "screenshots": _int(history.get("browser_capture_count")),
            "rollback": f"{_int(history.get('rollback_candidate_count'))} rollback candidates",
            "evidence": [],
            "lanes": [
                {"id": "branches", "label": "Branches", "value": "active", "state": "root"},
                {"id": "diffs", "label": "Diffs", "value": "deferred", "state": "read"},
                {"id": "capsules", "label": "Capsules", "value": "candidate", "state": "bounded"},
                {"id": "rollback", "label": "Rollback", "value": str(_int(history.get("rollback_candidate_count"))), "state": "candidate"},
            ],
        }
    ]


def build_build_workspace_model(
    root: str | Path,
    *,
    project_id: str = "ion_dev",
    probe_preview: bool = False,
    max_items: int = 8,
) -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    selected_project_id = str(project_id or "ion_dev").strip() or "ion_dev"
    item_limit = min(max(_int(max_items, 8), 1), 20)
    workspace_status = _safe_call(
        {"schema_id": "ion.project_workspace_status.v1", "ok": False, "finding": "workspace_status_failed"},
        build_project_workspace_status,
        shell_root,
        project_id=selected_project_id,
        probe_preview=probe_preview,
    )
    timeline = _safe_call(
        {"schema_id": "ion.project_workbench_timeline.v1", "ok": False, "finding": "timeline_failed"},
        build_project_workbench_timeline,
        shell_root,
        project_id=selected_project_id,
        probe_preview=probe_preview,
        max_items=item_limit,
    )
    queue = _safe_call(
        {"schema_id": "ion.codex_queue_runner.v1", "verdict": "deferred", "active_run_count": 0},
        build_codex_queue_runner_status,
        shell_root,
        reconcile=False,
        include_preview=True,
    )
    project_cockpit = _safe_call(
        {"schema_id": "ion.project_cockpit.v1", "status": "deferred", "summary": {}},
        build_project_cockpit_model,
        shell_root,
        runtime_timeline=[],
        lane_timeline=[],
    )
    project = dict(_as_mapping(workspace_status.get("project")))
    tool_contracts = _tool_contracts()
    modes = _mode_specs(tool_contracts)
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": utc_now(),
        "ok": True,
        "verdict": READY_VERDICT,
        "surface": "build",
        "selected_project_id": selected_project_id,
        "active_root_proof": _active_root_proof(shell_root),
        "project": project,
        "workspace": {
            "target_root_id": "active_ion_control",
            "movement_class": "ION_KERNEL_CONTROL_MOVEMENT",
            "root_relation": "active_ion_control_root",
            "workspace_project_subpath": "",
            "content_subpath": "ION",
            "allowed_roots": _string_list(project.get("allowed_roots"), limit=24),
            "allowed_files": _string_list(project.get("allowed_files"), limit=24),
            "forbidden_path_parts": sorted(FORBIDDEN_PATH_PARTS),
            "files_index": [],
            "cursor_hints": [
                "Use registered project workbench APIs for reads and patch previews.",
                "Submit durable Codex work through the queue runner, not raw TUI control.",
            ],
            "suggested_next_reads": [
                "ION/08_ui/joc_cockpit_shell/BuildWorkbenchPage.tsx",
                "ION/08_ui/joc_cockpit_shell/ion-runtime-cockpit.css",
                "ION/04_packages/kernel/ion_project_workbench.py",
                "ION/04_packages/kernel/ion_codex_queue_runner.py",
            ],
        },
        "preview": dict(_as_mapping(workspace_status.get("preview"))),
        "git_status": dict(_as_mapping(workspace_status.get("git_status"))),
        "timeline": timeline,
        "project_cockpit": project_cockpit,
        "project_systems": _project_system_rows(project_cockpit, timeline, limit=18),
        "receipts": {
            "latest_patch_receipts": [dict(row) for row in timeline.get("latest_patch_receipts") or [] if isinstance(row, Mapping)][:item_limit],
            "latest_browser_captures": [dict(row) for row in timeline.get("latest_browser_captures") or [] if isinstance(row, Mapping)][:item_limit],
            "rollback_supported_receipts": [dict(row) for row in timeline.get("rollback_supported_receipts") or [] if isinstance(row, Mapping)][:item_limit],
            "latest_refs": {
                "latest_capture_receipt_path": _as_mapping(timeline.get("visual_receipt")).get("latest_capture_receipt_path"),
                "latest_capture_screenshot_path": _as_mapping(timeline.get("visual_receipt")).get("latest_capture_screenshot_path"),
            },
        },
        "agent_tool_control": {
            "mcp_endpoint_path": "/mcp",
            "write_confirmation_required": True,
            "write_confirmation_token": WRITE_CONFIRMATION_TOKEN,
            "edit_lease_required_tools": list(EDIT_LEASE_REQUIRED_TOOLS),
            "conditional_edit_lease_tools": list(CONDITIONAL_EDIT_LEASE_TOOLS),
            "read_tools": ["ion_project_workspace_status", "ion_project_workbench_timeline", "ion_project_file_slice_read"],
            "bounded_write_tools": ["ion_project_patch_preview", "ion_project_patch_apply", "ion_project_patch_revert", "ion_project_action_run"],
            "forbidden_tools": ["arbitrary_shell", "direct_tui_key_injection", "credential_access", "git_reset", "git_push"],
            "tool_contracts": tool_contracts,
            "modes": modes,
        },
        "codex_queue_control": _compact_queue_control(queue),
        "authority_classes": list(AUTHORITY_CLASSES),
        "mutates_active_state": False,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
        "secrets_authority": False,
    }
