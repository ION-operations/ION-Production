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

from .ion_project_launcher import PROJECT_LOCAL_LAUNCH_CONFIRMATION, build_project_launcher_status

SCHEMA_ID = "ion.project_preview_sessions.v0_1"
SESSION_SCHEMA_ID = "ion.project_preview_session.v0_1"
PROVIDER_SCHEMA_ID = "ion.project_preview_provider.v0_1"
READY_VERDICT = "ION_PROJECT_PREVIEW_SESSIONS_READY"

_SAFE_ID_RE = re.compile(r"[^a-z0-9]+")


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
    if "stop_token=" in text or "token=" in text.lower():
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
            "public_preview_count": public_preview_count,
            "portfolio_session_count": portfolio_session_count,
            "source_counts": source_counts,
            "runtime_state_counts": runtime_state_counts,
        },
        "providers": providers,
        "sessions": sessions,
        "comparisons": [],
        "capability_classes": {
            "preview_read": "Read session state, safe same-origin URLs, screenshots, status, and receipt refs.",
            "preview_interaction": "Navigation, screenshot, and diagnostics actions remain separate authenticated routes.",
            "preview_mutation": "Not granted by this projection.",
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
            "Raw stop tokens and direct loopback URLs are not emitted.",
            "VM, remote, and viewer-local providers are placeholders only in Slice 1.",
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
