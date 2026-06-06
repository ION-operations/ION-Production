"""Read-only Helixion project preview-session projection.

This module composes existing launcher, project cockpit, portfolio, and
workbench signals into one preview-session model. It does not start, stop,
probe, install, screenshot, or proxy any app runtime.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
from typing import Any, Mapping
from urllib.parse import parse_qsl, unquote, urlsplit

from .ion_project_launcher import PROJECT_LOCAL_LAUNCH_CONFIRMATION, build_project_launcher_status

SCHEMA_ID = "ion.project_preview_sessions.v0_1"
SESSION_SCHEMA_ID = "ion.project_preview_session.v0_1"
PROVIDER_SCHEMA_ID = "ion.project_preview_provider.v0_1"
COMPARISON_SCHEMA_ID = "ion.project_preview_comparison.v0_1"
SURFACE_MATRIX_SCHEMA_ID = "ion.project_preview_surface_matrix.v0_1"
AI_OBSERVE_SUBSTRATE_SCHEMA_ID = "ion.project_preview_ai_observe_substrate.v0_1"
APP_CAST_PREVIEW_SCHEMA_ID = "ion.project_preview_app_cast_preview.v0_1"
APP_CAST_SHARE_GRANT_CONTRACT_SCHEMA_ID = "ion.project_preview_app_cast_share_grant_contract.v0_1"
READY_VERDICT = "ION_PROJECT_PREVIEW_SESSIONS_READY"

_SAFE_ID_RE = re.compile(r"[^a-z0-9]+")
_SECRET_ROUTE_KEYS = frozenset(
    {
        "stop_token",
        "token",
        "access_token",
        "id_token",
        "refresh_token",
        "session",
        "session_id",
        "auth",
        "api_key",
        "key",
    }
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def compact(value: Any, fallback: str = "") -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, (int, float, bool)):
        return str(value)
    return fallback


def listify(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if value is None:
        return []
    return [value]


def slug(value: Any, fallback: str = "preview") -> str:
    text = compact(value, fallback).lower()
    text = _SAFE_ID_RE.sub("-", text).strip("-")
    return text or fallback


def _path_ref(value: Any) -> str:
    text = compact(value)
    if not text:
        return ""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    if text.startswith("/"):
        return f"local_path_sha256:{digest}"
    return f"workspace_path_sha256:{digest}"


def _same_origin_path(value: Any) -> str:
    text = compact(value)
    if not text or not text.startswith("/"):
        return ""
    lower = text.lower()
    decoded = unquote(text)
    decoded_lower = decoded.lower()
    if text.startswith("//") or "\\" in text or "\\" in decoded:
        return ""
    if "%2f" in lower or "%5c" in lower:
        return ""
    parts = urlsplit(text)
    if parts.scheme or parts.netloc:
        return ""
    decoded_path = unquote(parts.path)
    if not decoded_path.startswith("/") or decoded_path.startswith("//") or "\\" in decoded_path:
        return ""
    if any(segment == ".." for segment in decoded_path.split("/")):
        return ""
    query_keys = {unquote(key).lower() for key, _value in parse_qsl(parts.query, keep_blank_values=True)}
    if query_keys & _SECRET_ROUTE_KEYS:
        return ""
    if re.search(r"(^|[?&#;/])(?:stop_token|token|access_token|id_token|refresh_token|session|session_id|auth|api_key|key)=", decoded_lower):
        return ""
    return text


def _authority(*, control: bool = False) -> dict[str, bool]:
    return {
        "preview_read": True,
        "preview_interaction": control,
        "preview_mutation": False,
        "process_start_authority": False,
        "process_stop_authority": False,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def _comparison_authority() -> dict[str, bool]:
    return {
        "preview_read": True,
        "preview_interaction": False,
        "preview_mutation": False,
        "ai_observe_preview": False,
        "process_start_authority": False,
        "process_stop_authority": False,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def _observe_authority() -> dict[str, bool]:
    return {
        "preview_read": True,
        "preview_mutation": False,
        "ai_observe_preview": False,
        "capture_authority": False,
        "browser_automation_authority": False,
        "loopback_probe": False,
        "loopback_mutation": False,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def _app_cast_authority() -> dict[str, bool]:
    return {
        "preview_read": True,
        "preview_mutation": False,
        "app_cast_authority": False,
        "app_cast_preview": False,
        "app_cast_host_authority": False,
        "app_cast_view_authority": False,
        "app_cast_interaction_authority": False,
        "stream_authority": False,
        "capture_authority": False,
        "browser_automation_authority": False,
        "viewer_control_authority": False,
        "loopback_probe": False,
        "loopback_mutation": False,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def _provider(
    provider_id: str,
    label: str,
    *,
    state: str,
    runner_location: str,
    capabilities: list[str],
    summary: str,
) -> dict[str, Any]:
    return {
        "schema_id": PROVIDER_SCHEMA_ID,
        "provider_id": provider_id,
        "label": label,
        "state": state,
        "runner_location": runner_location,
        "capabilities": capabilities,
        "summary": summary,
        "authority": _authority(control="preview_interaction" in capabilities),
    }


def preview_provider_catalog(*, launcher_ready: bool = True) -> list[dict[str, Any]]:
    return [
        _provider(
            "local_loopback_launcher",
            "Local loopback launcher",
            state="ready" if launcher_ready else "degraded",
            runner_location="local_host",
            capabilities=["preview_read", "preview_interaction", "managed_local_preview_launch"],
            summary="Existing local project launcher. Launch mutations remain confirmation-gated outside this projection.",
        ),
        _provider(
            "local_static_file_server",
            "Local static file server",
            state="registered",
            runner_location="local_host",
            capabilities=["preview_read", "preview_interaction"],
            summary="Static preview sessions served through the existing local launcher when started elsewhere.",
        ),
        _provider(
            "application_dev_launcher",
            "Application Dev launcher",
            state="registered",
            runner_location="local_host",
            capabilities=["preview_read"],
            summary="Same-origin catalog bridge for the local Application_Dev launcher.",
        ),
        _provider(
            "cockpit_internal_surface",
            "Cockpit internal surface",
            state="registered",
            runner_location="local_host",
            capabilities=["preview_read", "preview_interaction", "ai_observe_preview"],
            summary="Registered Project Workbench and cockpit preview routes.",
        ),
        _provider(
            "static_hosted_artifact",
            "Static hosted artifact",
            state="planned",
            runner_location="static_host",
            capabilities=["preview_read"],
            summary="Future immutable build or artifact preview adapter.",
        ),
        _provider(
            "vm_runner",
            "VM runner",
            state="planned",
            runner_location="vm",
            capabilities=["preview_read", "managed_vm_preview_launch"],
            summary="Schema placeholder only. No VM launch authority is granted by Slice 1.",
        ),
        _provider(
            "remote_runner",
            "Remote runner",
            state="planned",
            runner_location="remote_host",
            capabilities=["preview_read"],
            summary="Schema placeholder only. No remote process authority is granted by Slice 1.",
        ),
        _provider(
            "viewer_local_runner",
            "Viewer-local runner",
            state="planned",
            runner_location="viewer_local",
            capabilities=["preview_read", "viewer_local_preview_launch"],
            summary="Schema placeholder only. No viewer-local helper mutation is granted by Slice 1.",
        ),
    ]


def _session(
    *,
    preview_id: str,
    label: str,
    project_id: str,
    provider_id: str,
    runner_location: str,
    source_kind: str,
    version_id: str = "",
    family_id: str = "",
    runner_id: str = "local_operator",
    source_root_ref: str = "",
    public_url: str = "",
    same_origin_embed_url: str = "",
    local_url_ref: str = "",
    control_url: str = "",
    status_url: str = "",
    diagnostics_url: str = "",
    screenshot_url: str = "",
    hmr_proxy: str = "",
    auth_mode: str = "read_only",
    viewer_scope: str = "local_operator",
    lifecycle_state: str = "registered",
    created_at: str = "",
    updated_at: str = "",
    receipt_refs: list[str] | None = None,
    public_preview_allowed: bool = False,
    finding: str = "",
    interaction: bool = False,
    runtime_state_class: str = "",
    state_basis: str = "",
    association_state: str = "",
    detached: bool = False,
    process_attached: bool = False,
    actual_process_control: bool = False,
    stop_available: bool = False,
    last_known_state: str = "",
    recovered_at: str = "",
    launcher_finding: str = "",
    ownership_confidence: str = "",
    process_control_level: str = "",
    loopback_reachable: bool = False,
    stale: bool = False,
    stale_reasons: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_id": SESSION_SCHEMA_ID,
        "preview_id": preview_id,
        "project_id": project_id,
        "version_id": version_id,
        "family_id": family_id,
        "label": label,
        "provider_id": provider_id,
        "runner_id": runner_id,
        "runner_location": runner_location,
        "source_kind": source_kind,
        "source_root_ref": source_root_ref,
        "public_url": _same_origin_path(public_url),
        "same_origin_embed_url": _same_origin_path(same_origin_embed_url),
        "local_url_ref": local_url_ref,
        "control_url": _same_origin_path(control_url),
        "status_url": _same_origin_path(status_url),
        "diagnostics_url": _same_origin_path(diagnostics_url),
        "screenshot_url": _same_origin_path(screenshot_url),
        "hmr_proxy": _same_origin_path(hmr_proxy),
        "auth_mode": auth_mode,
        "viewer_scope": viewer_scope,
        "lifecycle_state": lifecycle_state,
        "created_at": created_at,
        "updated_at": updated_at,
        "expires_at": "",
        "stop_token_ref": "launcher_internal_stop_token_present" if source_kind == "launcher_record" else "",
        "receipt_refs": receipt_refs or [],
        "public_preview_allowed": public_preview_allowed,
        "finding": finding,
        "runtime_state_class": compact(runtime_state_class, lifecycle_state),
        "state_basis": compact(state_basis, source_kind),
        "association_state": compact(association_state, "catalog_projection"),
        "detached": detached,
        "process_attached": process_attached,
        "actual_process_control": actual_process_control,
        "stop_available": stop_available,
        "last_known_state": last_known_state,
        "recovered_at": recovered_at,
        "launcher_finding": launcher_finding,
        "ownership_confidence": ownership_confidence,
        "process_control_level": process_control_level,
        "loopback_reachable": loopback_reachable,
        "stale": stale,
        "stale_reasons": stale_reasons or [],
        "capabilities": {
            "preview_read": True,
            "preview_interaction": interaction,
            "preview_mutation": False,
        },
        "authority": _authority(control=interaction),
    }


def _launcher_runtime_state_class(record: Mapping[str, Any], *, running: bool) -> str:
    if running:
        return "running"
    ownership = compact(record.get("ownership_confidence"))
    state = compact(record.get("state"), "not_running")
    if ownership == "orphaned_local_preview_unverified":
        return "orphaned"
    if bool(record.get("detached")) and ownership == "stale_manifest_no_listener":
        return "stale"
    if bool(record.get("detached")):
        return "detached"
    return state


def _launcher_state_basis(record: Mapping[str, Any], *, running: bool) -> str:
    if running and bool(record.get("actual_process_control")):
        return "attached_process_object"
    if bool(record.get("detached")) or compact(record.get("recovered_at")):
        return "durable_state_recovery"
    return "launcher_record"


def _launcher_association_state(record: Mapping[str, Any], runtime_state_class: str) -> str:
    if runtime_state_class == "running" and bool(record.get("actual_process_control")):
        return "managed_attached_process"
    if runtime_state_class == "orphaned":
        return "orphaned_listener_unverified"
    if bool(record.get("detached")):
        return "recovered_detached_record"
    return "launcher_record"


def _launcher_stale_reasons(record: Mapping[str, Any], runtime_state_class: str) -> list[str]:
    reasons: list[str] = []
    if bool(record.get("detached")):
        reasons.append("detached_durable_manifest")
    if runtime_state_class == "stale":
        reasons.append("loopback_listener_absent")
    if runtime_state_class == "orphaned":
        reasons.extend(["loopback_listener_present", "process_ownership_unverified"])
    if not bool(record.get("actual_process_control")) and runtime_state_class in {"detached", "orphaned", "stale"}:
        reasons.append("no_attached_process_control")
    return list(dict.fromkeys(reasons))


def _session_from_launch_record(root: Path, record: Mapping[str, Any]) -> dict[str, Any] | None:
    launch_id = compact(record.get("launch_id"))
    if not launch_id:
        return None
    running = bool(record.get("running") and not record.get("detached") and record.get("actual_process_control") is not False)
    lifecycle = "running" if running else compact(record.get("state"), "not_running")
    framework = compact(record.get("framework"))
    provider_id = "local_static_file_server" if framework == "static" else "local_loopback_launcher"
    same_origin_embed_url = f"/cockpit/projects/launch/proxy/{launch_id}/" if running else ""
    runtime_state_class = _launcher_runtime_state_class(record, running=running)
    state_basis = _launcher_state_basis(record, running=running)
    association_state = _launcher_association_state(record, runtime_state_class)
    runtime_truth = record.get("runtime_truth") if isinstance(record.get("runtime_truth"), Mapping) else {}
    launcher_finding = compact(runtime_truth.get("finding"), compact(record.get("finding")))
    stale_reasons = _launcher_stale_reasons(record, runtime_state_class)
    return _session(
        preview_id=f"launch:{launch_id}",
        label=compact(record.get("label"), launch_id),
        project_id=compact(record.get("project_id")),
        version_id=compact(record.get("version_id")),
        provider_id=provider_id,
        runner_location="local_host",
        source_kind="launcher_record",
        source_root_ref=_path_ref(record.get("path")),
        public_url=same_origin_embed_url,
        same_origin_embed_url=same_origin_embed_url,
        local_url_ref="loopback_url_present" if running and compact(record.get("url")) else "loopback_listener_unverified" if record.get("loopback_reachable") else "",
        control_url=compact(record.get("status_path"), "/cockpit/projects/launch/status"),
        status_url=compact(record.get("status_path"), "/cockpit/projects/launch/status"),
        diagnostics_url=compact(record.get("diagnostics_path"), "/cockpit/projects/launch/diagnostics"),
        auth_mode="cockpit_confirmation_or_internal_stop_token" if running else "read_only_detached_state",
        lifecycle_state=lifecycle,
        created_at=compact(record.get("created_at")),
        updated_at=compact(record.get("updated_at")),
        receipt_refs=_latest_receipt_refs_for_launch(root, launch_id),
        public_preview_allowed=False,
        finding=launcher_finding,
        interaction=running,
        runtime_state_class=runtime_state_class,
        state_basis=state_basis,
        association_state=association_state,
        detached=bool(record.get("detached")),
        process_attached=bool(record.get("process_attached")),
        actual_process_control=bool(record.get("actual_process_control") and running),
        stop_available=bool(record.get("stop_available") and running),
        last_known_state=compact(record.get("last_known_state")),
        recovered_at=compact(record.get("recovered_at")),
        launcher_finding=launcher_finding,
        ownership_confidence=compact(record.get("ownership_confidence")),
        process_control_level=compact(record.get("process_control_level")),
        loopback_reachable=bool(record.get("loopback_reachable")),
        stale=runtime_state_class == "stale",
        stale_reasons=stale_reasons,
    )


def _session_from_project_row(project: Mapping[str, Any]) -> dict[str, Any] | None:
    project_id = compact(project.get("project_id"))
    if not project_id:
        return None
    preview_href = compact(project.get("preview_href"))
    route_href = compact(project.get("route_href"))
    launcher_url = compact(project.get("launcher_url"))
    catalog_url = compact(project.get("app_catalog_url"))
    if not (preview_href or route_href or launcher_url or catalog_url):
        return None
    if project_id == "application_dev" or catalog_url:
        return _session(
            preview_id="project:application-dev:application_dev_launcher",
            label=compact(project.get("label"), "Application Dev"),
            project_id=project_id,
            provider_id="application_dev_launcher",
            runner_location="local_host",
            source_kind="project_row",
            source_root_ref=_path_ref(project.get("path")),
            public_url=route_href or catalog_url,
            same_origin_embed_url=route_href or catalog_url,
            status_url=catalog_url,
            auth_mode="read_only_same_origin",
            viewer_scope="same_origin_viewer",
            lifecycle_state="ready" if compact(project.get("status")) != "missing" else "missing",
            public_preview_allowed=True,
        )
    return _session(
        preview_id=f"project:{slug(project_id)}:cockpit_internal_surface",
        label=compact(project.get("label"), project_id),
        project_id=project_id,
        provider_id="cockpit_internal_surface",
        runner_location="local_host",
        source_kind="project_row",
        source_root_ref=_path_ref(project.get("path")),
        public_url=preview_href or route_href,
        same_origin_embed_url=preview_href or route_href,
        control_url=route_href,
        auth_mode="read_only_same_origin",
        viewer_scope="same_origin_viewer",
        lifecycle_state=compact(project.get("status"), "registered"),
        public_preview_allowed=bool(preview_href),
        interaction=bool(preview_href),
    )


def _session_from_portfolio_version(family: Mapping[str, Any], version: Mapping[str, Any]) -> dict[str, Any] | None:
    launch = version.get("launch") if isinstance(version.get("launch"), Mapping) else {}
    launchable = bool(launch.get("launchable", version.get("launchable")))
    path = compact(launch.get("project_path"), compact(version.get("path")))
    if not launchable and not path:
        return None
    family_id = compact(family.get("family_id"), "portfolio")
    version_id = compact(launch.get("version_id"), compact(version.get("version_id"), slug(path, "version")))
    provider_id = "local_loopback_launcher" if launchable else "static_hosted_artifact"
    return _session(
        preview_id=f"portfolio:{slug(family_id)}:{slug(version_id)}",
        label=compact(launch.get("label"), compact(version.get("display_label"), compact(version.get("label"), family_id))),
        project_id=compact(launch.get("project_id"), compact(version.get("project_id"), family_id)),
        version_id=version_id,
        family_id=family_id,
        provider_id=provider_id,
        runner_location="local_host" if launchable else "static_host",
        source_kind="portfolio_version",
        source_root_ref=_path_ref(path),
        control_url=compact(launch.get("action_path"), "/cockpit/projects/launch/start") if launchable else "",
        status_url=compact(launch.get("status_path")),
        diagnostics_url=compact(launch.get("diagnostics_path")),
        auth_mode="cockpit_confirmation_required" if launchable else "read_only_catalog",
        viewer_scope="local_operator" if launchable else "same_origin_viewer",
        lifecycle_state=compact(launch.get("status"), "ready_to_launch" if launchable else "static"),
        public_preview_allowed=False,
        interaction=False,
    )


def _latest_receipt_refs_for_launch(root: Path, launch_id: str) -> list[str]:
    base = root / "ION/05_context/current/project_launcher/receipts"
    if not base.exists():
        return []
    refs: list[str] = []
    for path in sorted(base.glob(f"*{launch_id}*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            refs.append(path.relative_to(root).as_posix())
        except ValueError:
            refs.append(path.as_posix())
        if len(refs) >= 4:
            break
    return refs


def _session_group_keys(session: Mapping[str, Any]) -> list[tuple[str, str]]:
    keys: list[tuple[str, str]] = []
    project_id = compact(session.get("project_id"))
    version_id = compact(session.get("version_id"))
    family_id = compact(session.get("family_id"))
    if project_id and version_id:
        keys.append(("project_version", f"project_version:{project_id}:{version_id}"))
    if project_id:
        keys.append(("project", f"project:{project_id}"))
    if family_id and version_id:
        keys.append(("family_version", f"family_version:{family_id}:{version_id}"))
    if family_id:
        keys.append(("family", f"family:{family_id}"))
    return keys


def _session_comparison_priority(session: Mapping[str, Any]) -> tuple[int, str]:
    provider = compact(session.get("provider_id"))
    source = compact(session.get("source_kind"))
    state = compact(session.get("runtime_state_class"), compact(session.get("lifecycle_state")))
    if session.get("public_preview_allowed") or provider in {"cockpit_internal_surface", "static_hosted_artifact"}:
        priority = 0
    elif state == "running" and provider in {"local_loopback_launcher", "local_static_file_server"}:
        priority = 1
    elif source == "portfolio_version":
        priority = 2
    else:
        priority = 3
    return (priority, compact(session.get("preview_id")))


def _comparison_surface_route(session: Mapping[str, Any]) -> tuple[str, str]:
    for field in ("same_origin_embed_url", "public_url"):
        value = _same_origin_path(session.get(field))
        if value:
            return value, field
    return "", ""


def _comparison_surface(session: Mapping[str, Any], *, route: str, route_basis: str) -> dict[str, Any]:
    return {
        "preview_id": compact(session.get("preview_id")),
        "label": compact(session.get("label")),
        "project_id": compact(session.get("project_id")),
        "version_id": compact(session.get("version_id")),
        "family_id": compact(session.get("family_id")),
        "provider_id": compact(session.get("provider_id")),
        "runner_location": compact(session.get("runner_location")),
        "source_kind": compact(session.get("source_kind")),
        "source_root_ref": compact(session.get("source_root_ref")),
        "runtime_state_class": compact(session.get("runtime_state_class"), compact(session.get("lifecycle_state"))),
        "route": route,
        "route_basis": route_basis,
        "viewer_scope": compact(session.get("viewer_scope")),
        "auth_mode": compact(session.get("auth_mode")),
        "public_preview_allowed": bool(session.get("public_preview_allowed")),
    }


def _comparison_from_pair(baseline: Mapping[str, Any], candidate: Mapping[str, Any], *, pair_basis: str) -> dict[str, Any]:
    left_id = compact(baseline.get("preview_id"))
    right_id = compact(candidate.get("preview_id"))
    digest = hashlib.sha256(f"{left_id}\0{right_id}".encode("utf-8")).hexdigest()[:16]
    baseline_route, baseline_route_basis = _comparison_surface_route(baseline)
    candidate_route, candidate_route_basis = _comparison_surface_route(candidate)
    if candidate_route:
        route = candidate_route
        route_source = "candidate"
        route_basis = candidate_route_basis
    elif baseline_route:
        route = baseline_route
        route_source = "baseline"
        route_basis = baseline_route_basis
    else:
        route = ""
        route_source = ""
        route_basis = ""
    return {
        "schema_id": COMPARISON_SCHEMA_ID,
        "comparison_id": f"compare:{digest}",
        "pair_basis": pair_basis,
        "project_id": compact(candidate.get("project_id"), compact(baseline.get("project_id"))),
        "version_id": compact(candidate.get("version_id"), compact(baseline.get("version_id"))),
        "family_id": compact(candidate.get("family_id"), compact(baseline.get("family_id"))),
        "baseline_preview_id": left_id,
        "candidate_preview_id": right_id,
        "baseline_provider_id": compact(baseline.get("provider_id")),
        "candidate_provider_id": compact(candidate.get("provider_id")),
        "baseline_runner_location": compact(baseline.get("runner_location")),
        "candidate_runner_location": compact(candidate.get("runner_location")),
        "baseline_surface": _comparison_surface(baseline, route=baseline_route, route_basis=baseline_route_basis),
        "candidate_surface": _comparison_surface(candidate, route=candidate_route, route_basis=candidate_route_basis),
        "surface_pair": f"{compact(baseline.get('runner_location'), 'unknown')}_to_{compact(candidate.get('runner_location'), 'unknown')}",
        "route": route,
        "route_source": route_source,
        "route_basis": route_basis,
        "baseline_route": baseline_route,
        "baseline_route_basis": baseline_route_basis,
        "candidate_route": candidate_route,
        "candidate_route_basis": candidate_route_basis,
        "viewport": "desktop",
        "capture_pair_receipt_refs": [],
        "screenshot_refs": [],
        "console_delta": "not_captured",
        "network_delta": "not_captured",
        "dom_delta_ref": "",
        "accessibility_delta_ref": "",
        "visual_diff_ref": "",
        "verdict": "not_compared",
        "status": "registered_read_only",
        "finding": "comparison_pair_registered_no_capture",
        "capabilities": {
            "preview_read": True,
            "preview_interaction": False,
            "preview_mutation": False,
            "ai_observe_preview": False,
        },
        "authority": _comparison_authority(),
        "non_claims": [
            "No screenshot capture occurred.",
            "No DOM, network, console, accessibility, or visual diff was computed.",
            "No preview start, stop, probe, patch, deploy, or accepted-state action is authorized by this comparison record.",
        ],
    }


def _build_preview_comparisons(sessions: list[dict[str, Any]], *, max_comparisons: int = 60) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for session in sessions:
        for pair_basis, key in _session_group_keys(session):
            group = grouped.setdefault(key, {"pair_basis": pair_basis, "sessions": []})
            group["sessions"].append(session)

    comparisons: list[dict[str, Any]] = []
    seen_pairs: set[tuple[str, str]] = set()
    for key in sorted(grouped):
        group_data = grouped[key]
        group = sorted(group_data["sessions"], key=_session_comparison_priority)
        if len(group) < 2:
            continue
        pair_basis = compact(group_data.get("pair_basis"), "unknown")
        baseline = group[0]
        for candidate in group[1:]:
            if compact(candidate.get("preview_id")) == compact(baseline.get("preview_id")):
                continue
            pair = (compact(baseline.get("preview_id")), compact(candidate.get("preview_id")))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            comparisons.append(_comparison_from_pair(baseline, candidate, pair_basis=pair_basis))
            if len(comparisons) >= max_comparisons:
                return comparisons
    return comparisons


def _build_surface_matrix(providers: list[dict[str, Any]], sessions: list[dict[str, Any]], comparisons: list[dict[str, Any]]) -> dict[str, Any]:
    provider_ids_by_location: dict[str, list[str]] = {}
    for provider in providers:
        location = compact(provider.get("runner_location"), "unknown")
        provider_ids_by_location.setdefault(location, []).append(compact(provider.get("provider_id"), "unknown"))

    session_counts_by_location: dict[str, int] = {}
    session_counts_by_provider: dict[str, int] = {}
    comparable_session_ids: set[str] = set()
    for session in sessions:
        location = compact(session.get("runner_location"), "unknown")
        provider = compact(session.get("provider_id"), "unknown")
        session_counts_by_location[location] = session_counts_by_location.get(location, 0) + 1
        session_counts_by_provider[provider] = session_counts_by_provider.get(provider, 0) + 1
    for comparison in comparisons:
        comparable_session_ids.add(compact(comparison.get("baseline_preview_id")))
        comparable_session_ids.add(compact(comparison.get("candidate_preview_id")))

    return {
        "schema_id": SURFACE_MATRIX_SCHEMA_ID,
        "runner_locations": sorted(provider_ids_by_location),
        "provider_ids_by_location": {key: sorted(value) for key, value in sorted(provider_ids_by_location.items())},
        "session_counts_by_location": dict(sorted(session_counts_by_location.items())),
        "session_counts_by_provider": dict(sorted(session_counts_by_provider.items())),
        "comparison_count": len(comparisons),
        "comparable_session_count": len([item for item in comparable_session_ids if item]),
        "capability_boundaries": {
            "local_host": "Current managed local launcher and static sessions; mutation remains confirmation-gated outside this read-only model.",
            "vm": "Registered provider class only; no VM launch authority.",
            "remote_host": "Registered provider class only; no remote process authority.",
            "viewer_local": "Registered provider class only; no viewer-local helper launch authority.",
            "static_host": "Read-only artifact/session projection.",
        },
    }


def _observe_target_common(*, target_id: str, target_kind: str, route: str, route_basis: str) -> dict[str, Any]:
    return {
        "target_id": target_id,
        "target_kind": target_kind,
        "route": route,
        "route_basis": route_basis,
        "capture_state": "not_captured",
        "observation_receipt_refs": [],
        "artifact_refs": [],
    }


def _observe_target_from_session(session: Mapping[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    preview_id = compact(session.get("preview_id"))
    runtime_state = compact(session.get("runtime_state_class"), compact(session.get("lifecycle_state"), "unknown"))
    blocked = bool(session.get("detached")) or bool(session.get("stale")) or runtime_state in {"detached", "stale", "orphaned"}
    if blocked:
        blocked_reason = f"runtime_state_{slug(runtime_state, 'unknown')}_not_observable"
        target = _observe_target_common(
            target_id=f"blocked:session:{slug(preview_id, 'preview')}",
            target_kind="preview_session",
            route="",
            route_basis="",
        )
        target.update(
            {
                "preview_id": preview_id,
                "project_id": compact(session.get("project_id")),
                "provider_id": compact(session.get("provider_id")),
                "runner_location": compact(session.get("runner_location")),
                "runtime_state_class": runtime_state,
                "auth_mode": compact(session.get("auth_mode")),
                "viewer_scope": compact(session.get("viewer_scope")),
                "public_preview_allowed": bool(session.get("public_preview_allowed")),
                "blocked_reason": blocked_reason,
                "finding": blocked_reason,
                "stale_reasons": [compact(item) for item in listify(session.get("stale_reasons")) if compact(item)],
            }
        )
        return None, target

    route = ""
    route_basis = ""
    for field in ("same_origin_embed_url", "public_url"):
        candidate_route = _same_origin_path(session.get(field))
        if candidate_route:
            route = candidate_route
            route_basis = field
            break
    if not route:
        return None, None

    target = _observe_target_common(
        target_id=f"observe:session:{slug(preview_id, 'preview')}",
        target_kind="preview_session",
        route=route,
        route_basis=route_basis,
    )
    target.update(
        {
            "preview_id": preview_id,
            "project_id": compact(session.get("project_id")),
            "provider_id": compact(session.get("provider_id")),
            "runner_location": compact(session.get("runner_location")),
            "runtime_state_class": runtime_state,
            "auth_mode": compact(session.get("auth_mode")),
            "viewer_scope": compact(session.get("viewer_scope")),
            "public_preview_allowed": bool(session.get("public_preview_allowed")),
        }
    )
    return target, None


def _observe_target_from_comparison(comparison: Mapping[str, Any]) -> dict[str, Any] | None:
    route = _same_origin_path(comparison.get("route"))
    if not route:
        return None
    comparison_id = compact(comparison.get("comparison_id"))
    route_source = compact(comparison.get("route_source"))
    surface_key = f"{route_source}_surface" if route_source in {"baseline", "candidate"} else ""
    surface = comparison.get(surface_key) if surface_key else {}
    if not isinstance(surface, Mapping):
        surface = {}
    target = _observe_target_common(
        target_id=f"observe:comparison:{slug(comparison_id, 'comparison')}",
        target_kind="preview_comparison",
        route=route,
        route_basis="comparison.route",
    )
    target.update(
        {
            "comparison_id": comparison_id,
            "project_id": compact(comparison.get("project_id")),
            "provider_id": compact(comparison.get("candidate_provider_id"), compact(comparison.get("baseline_provider_id"))),
            "runner_location": compact(
                comparison.get("candidate_runner_location"),
                compact(comparison.get("baseline_runner_location"), "unknown"),
            ),
            "runtime_state_class": "comparison_pair_registered",
            "comparison_route_source": compact(comparison.get("route_source")),
            "comparison_route_basis": compact(comparison.get("route_basis")),
            "auth_mode": compact(surface.get("auth_mode")),
            "viewer_scope": compact(surface.get("viewer_scope")),
            "public_preview_allowed": bool(surface.get("public_preview_allowed")),
        }
    )
    return target


def _build_ai_observe_preview_substrate(sessions: list[dict[str, Any]], comparisons: list[dict[str, Any]]) -> dict[str, Any]:
    targets: list[dict[str, Any]] = []
    blocked_targets: list[dict[str, Any]] = []
    for session in sessions:
        target, blocked_target = _observe_target_from_session(session)
        if target:
            targets.append(target)
        if blocked_target:
            blocked_targets.append(blocked_target)
    for comparison in comparisons:
        target = _observe_target_from_comparison(comparison)
        if target:
            targets.append(target)

    target_counts_by_kind: dict[str, int] = {}
    for target in targets:
        kind = compact(target.get("target_kind"), "unknown")
        target_counts_by_kind[kind] = target_counts_by_kind.get(kind, 0) + 1

    return {
        "schema_id": AI_OBSERVE_SUBSTRATE_SCHEMA_ID,
        "status": "registered_read_only",
        "observe_mode": "metadata_only_no_capture",
        "target_count": len(targets),
        "blocked_target_count": len(blocked_targets),
        "target_counts_by_kind": dict(sorted(target_counts_by_kind.items())),
        "targets": targets,
        "blocked_targets": blocked_targets,
        "policy": {
            "route_policy": "same_origin_relative_paths_only",
            "allowed_route_basis": ["same_origin_embed_url", "public_url", "comparison.route"],
            "forbidden_capabilities": [
                "capture",
                "browser_automation",
                "loopback_probe",
                "loopback_mutation",
                "secrets_access",
                "live_execution",
                "accepted_state_claim",
            ],
        },
        "authority": _observe_authority(),
        "non_claims": [
            "No screenshot capture occurred.",
            "No browser automation, loopback probe, DOM read, console read, network read, or visual diff was executed.",
            "Observation targets are metadata-only references to existing same-origin preview routes.",
            "Detached, stale, and orphaned preview records are blocked from observation targets.",
            "No production, live execution, secrets, mutation, or accepted-state authority is granted.",
        ],
    }


def _collaboration_route_evidence(route: str) -> dict[str, Any]:
    def fallback(status: str, finding: str) -> dict[str, Any]:
        object_resolver = "project_launch" if route.startswith("/cockpit/projects/launch/proxy/") else "project_portfolio"
        return {
            "schema_id": "ion.project_preview_app_cast_route_auth_evidence.v0_1",
            "status": status,
            "route": route,
            "method": "GET",
            "registered_route": False,
            "finding": finding,
            "route_registry_model": "ion.helixion_collaboration_route_registry.v0_1",
            "route_class": "project_read",
            "capability": "public_preview_read",
            "sensitivity": "internal",
            "object_resolver": object_resolver,
            "mutation": False,
            "same_origin_required": True,
            "localhost_context_required": False,
            "object_grant_required": True,
            "approval_required": False,
            "receipt_required": True,
            "shareable_with_co_users": True,
            "candidate_enforcement_active": False,
            "live_route_enforcement": False,
            "authority": _app_cast_authority(),
        }

    try:
        from .ion_helixion_collaboration_access import find_registered_route

        row, finding = find_registered_route(route, method="GET")
    except Exception as exc:  # pragma: no cover - defensive against optional collaboration slices.
        return fallback("route_registry_unavailable_reference_inferred", f"route_registry_unavailable:{exc.__class__.__name__}")
    if row is None:
        return fallback("route_registry_reference_not_registered", finding or "ROUTE_NOT_REGISTERED")
    route_row = row.to_dict()
    return {
        "schema_id": "ion.project_preview_app_cast_route_auth_evidence.v0_1",
        "status": "registered_candidate_route",
        "route": route,
        "method": "GET",
        "registered_route": True,
        "route_registry_model": "ion.helixion_collaboration_route_registry.v0_1",
        "route_id": compact(route_row.get("route_id")),
        "path_template": compact(route_row.get("path_template")),
        "route_class": compact(route_row.get("route_class")),
        "capability": compact(route_row.get("capability")),
        "sensitivity": compact(route_row.get("sensitivity")),
        "object_resolver": compact(route_row.get("object_resolver")),
        "mutation": bool(route_row.get("mutation")),
        "same_origin_required": bool(route_row.get("same_origin_required")),
        "localhost_context_required": bool(route_row.get("localhost_context_required")),
        "object_grant_required": bool(route_row.get("object_grant_required")),
        "approval_required": bool(route_row.get("approval_required")),
        "receipt_required": bool(route_row.get("receipt_required")),
        "shareable_with_co_users": bool(route_row.get("shareable_with_co_users")),
        "candidate_enforcement_active": False,
        "live_route_enforcement": False,
        "authority": _app_cast_authority(),
    }


def _target_share_grant_contract(*, route: str, target: Mapping[str, Any], blocked: bool = False) -> dict[str, Any]:
    public_preview_allowed = bool(target.get("public_preview_allowed"))
    object_grant_required = blocked or not public_preview_allowed
    route_auth_evidence = _collaboration_route_evidence(route) if route else {
        "schema_id": "ion.project_preview_app_cast_route_auth_evidence.v0_1",
        "status": "blocked_no_route",
        "route": "",
        "method": "GET",
        "registered_route": False,
        "finding": compact(target.get("blocked_reason"), "target_blocked"),
        "candidate_enforcement_active": False,
        "live_route_enforcement": False,
    }
    route_auth_evidence = dict(route_auth_evidence)
    route_auth_evidence.update(
        {
            "target_access_basis": "public_preview_read" if public_preview_allowed else "explicit_object_share_grant_required",
            "target_object_grant_required": object_grant_required,
            "target_public_preview_allowed": public_preview_allowed,
        }
    )
    source_target_kind = compact(target.get("target_kind"))
    target_object_id = compact(target.get("comparison_id"), compact(target.get("preview_id"), compact(target.get("target_id"))))
    return {
        "schema_id": APP_CAST_SHARE_GRANT_CONTRACT_SCHEMA_ID,
        "status": "candidate_contract_only_no_grant",
        "share_target_id": f"share:{slug(target_object_id, 'target')}",
        "target_object_id": target_object_id,
        "target_object_type": source_target_kind,
        "workspace_id": "wsp_local_operator",
        "membership_model": "ion.helixion_workspace_membership.v0_1",
        "route_registry_model": "ion.helixion_collaboration_route_registry.v0_1",
        "candidate_enforcement_active": False,
        "live_route_enforcement": False,
        "host_membership_required": True,
        "host_membership_status": "required_not_evaluated",
        "host_required_rank_ceiling": "builder_contributor",
        "host_required_capability": "preview_launch",
        "host_object_grant_required": True,
        "host_object_grant_ref": "",
        "host_approval_required": True,
        "viewer_session_required": True,
        "viewer_session_status": "required_not_evaluated",
        "viewer_membership_required": object_grant_required,
        "viewer_membership_status": "required_not_evaluated" if object_grant_required else "public_preview_session_required_not_membership_grant",
        "viewer_minimum_rank_ceiling": "viewer_client",
        "viewer_required_capability": "public_preview_read",
        "viewer_object_grant_required": object_grant_required,
        "viewer_object_grant_ref": "",
        "viewer_grant_requirement": "public_preview_read" if public_preview_allowed else "explicit_object_share_grant_required",
        "viewer_interaction": "view_only",
        "share_grant_state": "blocked_no_active_grant" if blocked else "not_granted",
        "share_grant_ref": "",
        "object_share_grant_ref": "",
        "pairing_state": "not_paired",
        "host_viewer_pair_ref": "",
        "expiry_policy": {
            "expires_at_required_for_active_grant": True,
            "default_ttl_minutes": 60,
            "expires_at": "",
        },
        "revocation_policy": {
            "revocable": True,
            "revocation_state": "revocable_no_active_grant",
            "revoked_at": "",
        },
        "audit_policy": {
            "audit_receipt_required": True,
            "audit_receipt_refs": [],
            "audit_event_refs": [],
            "required_events": [
                "share_grant_requested",
                "share_grant_approved",
                "viewer_joined",
                "viewer_left",
                "share_grant_revoked",
                "share_grant_expired",
            ],
        },
        "route_auth_evidence": route_auth_evidence,
        "authorization_preview": {
            "status": "not_evaluated_no_viewer_principal",
            "route_class": compact(route_auth_evidence.get("route_class"), "project_read"),
            "capability": compact(route_auth_evidence.get("capability"), "public_preview_read"),
            "sensitivity": compact(route_auth_evidence.get("sensitivity"), "internal"),
            "rank_is_permission": False,
            "rank_is_ceiling": True,
            "requires_object_grant": object_grant_required,
            "requires_approval": False,
            "path_authority_evaluated": False,
            "authority": _app_cast_authority(),
        },
        "non_claims": [
            "No share grant is active.",
            "No host-viewer pair is active.",
            "No stream, media, capture, browser automation, loopback, or viewer-control channel is active.",
        ],
        "authority": _app_cast_authority(),
    }


def _cast_target_from_observe_target(target: Mapping[str, Any]) -> dict[str, Any] | None:
    route = _same_origin_path(target.get("route"))
    if not route:
        return None
    source_target_id = compact(target.get("target_id"))
    share_grant_contract = _target_share_grant_contract(route=route, target=target)
    return {
        "cast_target_id": f"cast:{slug(source_target_id, 'target')}",
        "target_kind": "app_cast_target",
        "source_target_id": source_target_id,
        "source_target_kind": compact(target.get("target_kind")),
        "preview_id": compact(target.get("preview_id")),
        "comparison_id": compact(target.get("comparison_id")),
        "project_id": compact(target.get("project_id")),
        "provider_id": compact(target.get("provider_id")),
        "runner_location": compact(target.get("runner_location")),
        "runtime_state_class": compact(target.get("runtime_state_class")),
        "auth_mode": compact(target.get("auth_mode")),
        "viewer_scope": compact(target.get("viewer_scope")),
        "public_preview_allowed": bool(target.get("public_preview_allowed")),
        "viewer_grant_requirement": compact(share_grant_contract.get("viewer_grant_requirement")),
        "route": route,
        "route_basis": compact(target.get("route_basis")),
        "cast_mode": "app_only_view",
        "stream_state": "not_streaming",
        "transport_state": "transport_deferred",
        "viewer_interaction": "view_only",
        "viewer_interaction_state": "view_only",
        "host_control_state": "not_granted",
        "app_only_boundary": "single_preview_route_only",
        "source_capture_state": compact(target.get("capture_state"), "not_captured"),
        "share_grant_state": compact(share_grant_contract.get("share_grant_state")),
        "share_grant_contract": share_grant_contract,
        "receipt_refs": [],
        "authority": _app_cast_authority(),
    }


def _cast_blocked_target_from_observe_target(target: Mapping[str, Any]) -> dict[str, Any]:
    share_grant_contract = _target_share_grant_contract(route="", target=target, blocked=True)
    return {
        "cast_target_id": f"blocked_cast:{slug(target.get('target_id'), 'target')}",
        "source_target_id": compact(target.get("target_id")),
        "preview_id": compact(target.get("preview_id")),
        "project_id": compact(target.get("project_id")),
        "provider_id": compact(target.get("provider_id")),
        "runner_location": compact(target.get("runner_location")),
        "runtime_state_class": compact(target.get("runtime_state_class")),
        "auth_mode": compact(target.get("auth_mode")),
        "viewer_scope": compact(target.get("viewer_scope")),
        "public_preview_allowed": bool(target.get("public_preview_allowed")),
        "viewer_grant_requirement": "explicit_object_share_grant_required",
        "blocked_reason": compact(target.get("blocked_reason"), "observe_target_blocked"),
        "finding": compact(target.get("finding"), "observe_target_blocked"),
        "route": "",
        "route_basis": "",
        "cast_mode": "app_only_view",
        "stream_state": "blocked_not_streaming",
        "transport_state": "blocked_transport_deferred",
        "viewer_interaction": "view_only",
        "viewer_interaction_state": "view_only",
        "host_control_state": "not_granted",
        "app_only_boundary": "single_preview_route_only",
        "share_grant_state": compact(share_grant_contract.get("share_grant_state")),
        "share_grant_contract": share_grant_contract,
        "authority": _app_cast_authority(),
    }


def _build_app_cast_preview(ai_observe_preview: Mapping[str, Any]) -> dict[str, Any]:
    targets: list[dict[str, Any]] = []
    for target in listify(ai_observe_preview.get("targets")):
        if isinstance(target, Mapping):
            cast_target = _cast_target_from_observe_target(target)
            if cast_target:
                targets.append(cast_target)

    blocked_targets: list[dict[str, Any]] = []
    for target in listify(ai_observe_preview.get("blocked_targets")):
        if isinstance(target, Mapping):
            blocked_targets.append(_cast_blocked_target_from_observe_target(target))
    target_contracts = [target["share_grant_contract"] for target in targets if isinstance(target.get("share_grant_contract"), Mapping)]
    blocked_contracts = [target["share_grant_contract"] for target in blocked_targets if isinstance(target.get("share_grant_contract"), Mapping)]
    registered_route_target_count = sum(
        1
        for contract in target_contracts
        if isinstance(contract.get("route_auth_evidence"), Mapping) and bool(contract["route_auth_evidence"].get("registered_route"))
    )
    object_grant_required_target_count = sum(1 for contract in target_contracts if bool(contract.get("viewer_object_grant_required")))

    return {
        "schema_id": APP_CAST_PREVIEW_SCHEMA_ID,
        "status": "candidate_projection_only_no_stream",
        "cast_mode": "app_only_not_desktop_screen_share",
        "target_count": len(targets),
        "blocked_target_count": len(blocked_targets),
        "share_grant_contract_count": len(target_contracts),
        "share_grant_blocked_contract_count": len(blocked_contracts),
        "registered_route_target_count": registered_route_target_count,
        "object_grant_required_target_count": object_grant_required_target_count,
        "targets": targets,
        "blocked_targets": blocked_targets,
        "share_grant_contract": {
            "schema_id": APP_CAST_SHARE_GRANT_CONTRACT_SCHEMA_ID,
            "status": "candidate_contract_only_no_grants_active",
            "contract_mode": "read_only_membership_and_object_grant_projection",
            "membership_model": "ion.helixion_multi_user_identity.v0_1",
            "route_registry_model": "ion.helixion_collaboration_route_registry.v0_1",
            "candidate_enforcement_active": False,
            "live_route_enforcement": False,
            "target_contract_count": len(target_contracts),
            "blocked_contract_count": len(blocked_contracts),
            "active_share_grant_count": 0,
            "registered_route_target_count": registered_route_target_count,
            "object_grant_required_target_count": object_grant_required_target_count,
            "host_viewer_pairing_state": "not_paired",
            "grant_states": ["not_granted", "requested", "approved", "active", "revoked", "expired"],
            "viewer_access_modes": {
                "public_preview": "public_preview_read with active session",
                "non_public_preview": "public_preview_read plus explicit object share grant",
            },
            "expiry_policy": {
                "expires_at_required_for_active_grant": True,
                "default_ttl_minutes": 60,
            },
            "revocation_policy": {
                "revocable": True,
                "revocation_receipt_required": True,
            },
            "audit_policy": {
                "audit_receipt_required": True,
                "required_events": [
                    "share_grant_requested",
                    "share_grant_approved",
                    "viewer_joined",
                    "viewer_left",
                    "share_grant_revoked",
                    "share_grant_expired",
                ],
            },
            "authority": _app_cast_authority(),
        },
        "roles": {
            "host_user": {
                "role_id": "app_cast_host",
                "capability_model": "ion_helixion_multi_user_identity",
                "minimum_rank_ceiling": "builder_contributor",
                "required_capabilities": ["preview_launch"],
                "conditional_capabilities": {
                    "local_control_request": "required before any local control, stop, or viewer interaction grant",
                },
                "object_grant_required": True,
                "approval_required": True,
            },
            "host_control_user": {
                "role_id": "app_cast_local_control_host",
                "capability_model": "ion_helixion_multi_user_identity",
                "minimum_rank_ceiling": "lead_architect",
                "required_capabilities": ["local_control_request"],
                "object_grant_required": True,
                "approval_required": True,
                "control_authority_granted_by_projection": False,
            },
            "viewer_user": {
                "role_id": "app_cast_viewer",
                "capability_model": "ion_helixion_multi_user_identity",
                "minimum_rank_ceiling": "viewer_client",
                "required_capabilities": ["public_preview_read"],
                "object_grant_required": "non_public_targets_only",
                "view_only": True,
            },
        },
        "policy": {
            "target_source_policy": "derived_from_ai_observe_preview_targets_only",
            "app_only_boundary": "single_preview_route_only",
            "transport_policy": "transport_deferred_no_webrtc_or_media_stream_started",
            "viewer_control_policy": "view_only_no_interaction_granted",
            "forbidden_capabilities": [
                "desktop_screen_share",
                "full_desktop_capture",
                "whole_browser_share",
                "terminal_capture",
                "filesystem_capture",
                "source_file_share",
                "raw_local_path_share",
                "screenshot_capture",
                "browser_automation",
                "secret_value_read",
                "secrets_access",
                "viewer_control",
                "viewer_mutation",
                "loopback_probe",
                "loopback_mutation",
                "live_execution",
                "production_deploy",
                "accepted_state_claim",
            ],
        },
        "multi_user_system_contract": {
            "expected_from_parallel_multi_user_agent": [
                "membership_and_object_grants",
                "host_viewer_session_pairing",
                "ephemeral_cast_channel",
                "revocation_and_expiry",
                "audit_events",
                "viewer_presence",
            ],
            "preview_layer_provides": [
                "safe_same_origin_cast_targets",
                "blocked_target_reasons",
                "host_viewer_role_requirements",
                "app_only_boundary_non_claims",
            ],
        },
        "authority": _app_cast_authority(),
        "non_claims": [
            "No app stream was started.",
            "No WebRTC, websocket, snapshot, or media transport was opened.",
            "No screenshot, DOM, console, network, accessibility, or visual capture occurred.",
            "No desktop, full browser, terminal, source file, local path, or secret surface is shared.",
            "No viewer interaction, mutation, production, live execution, or accepted-state authority is granted.",
        ],
    }


def build_preview_sessions_from_cockpit(
    root: str | Path,
    *,
    projects: Any = None,
    portfolio: Any = None,
    launcher_status: Mapping[str, Any] | None = None,
    max_portfolio_sessions: int = 160,
) -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    launcher = dict(launcher_status or build_project_launcher_status(shell_root))
    providers = preview_provider_catalog(launcher_ready=bool(launcher.get("ok", True)))
    sessions: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(session: dict[str, Any] | None) -> None:
        if not session:
            return
        preview_id = compact(session.get("preview_id"))
        if not preview_id or preview_id in seen:
            return
        seen.add(preview_id)
        sessions.append(session)

    for record in listify(launcher.get("launches")):
        if isinstance(record, Mapping):
            add(_session_from_launch_record(shell_root, record))

    for project in listify(projects):
        if isinstance(project, Mapping):
            add(_session_from_project_row(project))

    portfolio_session_count = 0
    if isinstance(portfolio, Mapping):
        for family in listify(portfolio.get("families")):
            if not isinstance(family, Mapping):
                continue
            for version in listify(family.get("versions")):
                if not isinstance(version, Mapping):
                    continue
                if portfolio_session_count >= max_portfolio_sessions:
                    break
                before = len(sessions)
                add(_session_from_portfolio_version(family, version))
                if len(sessions) > before:
                    portfolio_session_count += 1
            if portfolio_session_count >= max_portfolio_sessions:
                break

    comparisons = _build_preview_comparisons(sessions)
    surface_matrix = _build_surface_matrix(providers, sessions, comparisons)
    ai_observe_preview = _build_ai_observe_preview_substrate(sessions, comparisons)
    app_cast_preview = _build_app_cast_preview(ai_observe_preview)
    source_counts: dict[str, int] = {}
    runtime_state_counts: dict[str, int] = {}
    for session in sessions:
        source_kind = compact(session.get("source_kind"), "unknown")
        source_counts[source_kind] = source_counts.get(source_kind, 0) + 1
        runtime_state = compact(session.get("runtime_state_class"), "unknown")
        runtime_state_counts[runtime_state] = runtime_state_counts.get(runtime_state, 0) + 1
    running_count = len([session for session in sessions if session.get("runtime_state_class") == "running"])
    detached_count = len([session for session in sessions if session.get("detached")])
    orphaned_count = len([session for session in sessions if session.get("runtime_state_class") == "orphaned"])
    stale_count = len([session for session in sessions if session.get("stale")])
    public_preview_count = len([session for session in sessions if session.get("public_preview_allowed")])
    return {
        "schema_id": SCHEMA_ID,
        "ok": True,
        "verdict": READY_VERDICT,
        "status": "ready",
        "generated_at": utc_now(),
        "summary": {
            "provider_count": len(providers),
            "session_count": len(sessions),
            "running_count": running_count,
            "detached_count": detached_count,
            "orphaned_count": orphaned_count,
            "stale_count": stale_count,
            "comparison_count": len(comparisons),
            "comparable_session_count": surface_matrix.get("comparable_session_count", 0),
            "ai_observe_target_count": ai_observe_preview.get("target_count", 0),
            "ai_observe_blocked_target_count": ai_observe_preview.get("blocked_target_count", 0),
            "app_cast_target_count": app_cast_preview.get("target_count", 0),
            "app_cast_blocked_target_count": app_cast_preview.get("blocked_target_count", 0),
            "public_preview_count": public_preview_count,
            "portfolio_session_count": portfolio_session_count,
            "source_counts": source_counts,
            "runtime_state_counts": runtime_state_counts,
            "session_counts_by_location": surface_matrix.get("session_counts_by_location", {}),
            "session_counts_by_provider": surface_matrix.get("session_counts_by_provider", {}),
        },
        "providers": providers,
        "sessions": sessions,
        "comparisons": comparisons,
        "surface_matrix": surface_matrix,
        "ai_observe_preview": ai_observe_preview,
        "app_cast_preview": app_cast_preview,
        "capability_classes": {
            "preview_read": "Read session state, safe same-origin URLs, screenshots, status, and receipt refs.",
            "preview_compare": "Register safe pairs of preview surfaces for later capture/diff work without performing capture.",
            "preview_interaction": "Navigation, screenshot, and diagnostics actions remain separate authenticated routes.",
            "preview_mutation": "Not granted by this projection.",
            "ai_observe_preview": "Metadata-only observe target registry; capture, DOM, AX, console, network, and visual work are not executed by this projection.",
            "app_cast_preview": "App-only cast target registry for future multi-user host/viewer sharing; no stream or capture is executed by this projection.",
        },
        "routes": {
            "model": "/cockpit/previews/model.json",
            "projects_model": "/cockpit/projects/model.json",
            "apps_model": "/cockpit/apps/model.json",
            "launch_start": "/cockpit/projects/launch/start",
            "launch_status": "/cockpit/projects/launch/status",
        },
        "source_models": {
            "project_launcher": "ion_project_launcher.build_project_launcher_status",
            "project_cockpit": "ion_project_cockpit.build_project_cockpit_model",
            "project_portfolio": "project_cockpit.portfolio",
        },
        "authority": {
            "preview_read": True,
            "preview_mutation": False,
            "generic_launch_app_permission": False,
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
        "non_claims": [
            "This model does not start, stop, probe, install, screenshot, or proxy any app.",
            "Preview comparisons are registered pairings only; no capture, DOM diff, visual diff, or equivalence verdict is produced.",
            "AI observe preview is a metadata-only target registry; no capture, browser automation, loopback probe, or observation execution occurred.",
            "App cast preview is a metadata-only target registry; no app stream, screen share, media transport, or viewer interaction is active.",
            "Raw stop tokens and direct loopback URLs are not emitted.",
            "VM, remote, and viewer-local providers are registered as read-only provider classes only.",
            "Launch, stop, diagnostics, patch, and rollback mutations keep their existing cockpit gates.",
        ],
        "findings": [],
    }


def build_project_preview_sessions_model(root: str | Path = ".") -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    from .ion_project_cockpit import build_project_cockpit_model

    cockpit = build_project_cockpit_model(shell_root)
    return build_preview_sessions_from_cockpit(
        shell_root,
        projects=cockpit.get("projects"),
        portfolio=cockpit.get("portfolio"),
        launcher_status=cockpit.get("launcher") if isinstance(cockpit.get("launcher"), Mapping) else None,
    )
