"""Local system diagnostics projection for the JOC cockpit.

This module is local-only. It reads process, port, memory, and disk state for
operator visibility and exposes a narrow guarded stop action for unprotected dev
server processes. It does not grant production or accepted-state authority.
"""

from __future__ import annotations

import os
import json
import re
import signal
import subprocess
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .ion_cockpit_service_manager import build_service_console_model
from .ion_helixion_authorization import build_authorization_evaluator_projection
from .ion_public_cockpit_auth import (
    ALLOWED_EMAILS_ENV,
    GOOGLE_CLIENT_ID_ENV,
    INVITE_TOKENS_ENV,
    PUBLIC_COCKPIT_TOKEN_ENV,
    SESSION_COOKIE,
    SESSION_SECRET_ENV,
    cockpit_session_secret,
    google_oauth_configured,
    invite_token_rows,
)

SCHEMA_ID = "ion.system_diagnostics.v1"
STOP_CONFIRMATION = "ION_SYSTEM_DIAGNOSTICS_STOP_CONFIRMED"
MAX_PROCESS_ROWS = 120
MAX_PORT_ROWS = 240
MAX_DEV_SERVER_ROWS = 120
HTTP_PROBE_TIMEOUT_SECONDS = 0.45
STOPPABLE_PROJECT_WORKSPACES = {"Application_Dev", "Cosmos"}
SENSITIVE_TEXT_PATTERNS = (
    re.compile(r"(?i)\b([a-z0-9_.-]*(?:token|secret|password|passwd|api[_-]?key|authorization|cookie)[a-z0-9_.-]*)(=)([^\s\"']+)"),
    re.compile(r"(?i)\b(bearer)\s+([a-z0-9._~+/=-]{12,})"),
    re.compile(r"\b(sk-[A-Za-z0-9_-]{12,})\b"),
    re.compile(r"\b(gh[pousr]_[A-Za-z0-9_]{12,})\b"),
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_text(path: str | Path, fallback: str = "") -> str:
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return fallback


def _redact_sensitive_text(value: str | None) -> tuple[str | None, int]:
    if value is None:
        return None, 0
    text = str(value)
    count = 0

    def replace_key_value(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return f"{match.group(1)}{match.group(2)}[REDACTED]"

    text = SENSITIVE_TEXT_PATTERNS[0].sub(replace_key_value, text)

    def replace_bearer(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return f"{match.group(1)} [REDACTED]"

    text = SENSITIVE_TEXT_PATTERNS[1].sub(replace_bearer, text)

    def replace_token(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return "[REDACTED]"

    for pattern in SENSITIVE_TEXT_PATTERNS[2:]:
        text = pattern.sub(replace_token, text)
    return text, count


def _run_text(command: str, args: list[str], *, timeout: float = 4.0) -> str:
    try:
        completed = subprocess.run(
            [command, *args],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=timeout,
        )
    except Exception:
        return ""
    return completed.stdout if completed.returncode == 0 else ""


def _route_matrix() -> list[dict[str, Any]]:
    route_rows = [
        {
            "id": "system_model",
            "method": "GET",
            "path": "/cockpit/system/model.json",
            "surface": "system_diagnostics",
            "route_class": "project_read",
            "capability": "curated_doc_read",
            "sensitivity": "internal",
            "auth_required": True,
            "same_origin_required": False,
            "confirmation_required": False,
            "policy_projection": "candidate_read_projection",
        },
        {
            "id": "system_preview_action",
            "method": "POST",
            "path": "/cockpit/system/preview_action",
            "surface": "system_diagnostics",
            "route_class": "local_control",
            "capability": "local_control_request",
            "sensitivity": "local_control",
            "auth_required": True,
            "same_origin_required": True,
            "confirmation_required": False,
            "policy_projection": "candidate_policy_projection_required",
        },
        {
            "id": "system_execute_action",
            "method": "POST",
            "path": "/cockpit/system/execute_action",
            "surface": "system_diagnostics",
            "route_class": "local_control",
            "capability": "local_control_request",
            "sensitivity": "local_control",
            "auth_required": True,
            "same_origin_required": True,
            "confirmation_required": True,
            "required_confirmation": STOP_CONFIRMATION,
            "policy_projection": "candidate_policy_projection_required",
        },
        {
            "id": "service_restart",
            "method": "POST",
            "path": "/cockpit/services/restart",
            "surface": "service_console",
            "route_class": "local_control",
            "capability": "local_control_request",
            "sensitivity": "local_control",
            "auth_required": True,
            "same_origin_required": True,
            "confirmation_required": True,
            "required_confirmation": "ION_SERVICE_CONTROL_APPROVED",
            "policy_projection": "candidate_policy_projection_required",
        },
        {
            "id": "app_diagnostics_timeline",
            "method": "POST",
            "path": "/cockpit/projects/launch/diagnostics/timeline",
            "surface": "app_diagnostics",
            "route_class": "project_read",
            "capability": "assigned_receipt_read",
            "sensitivity": "internal",
            "auth_required": True,
            "same_origin_required": True,
            "confirmation_required": False,
            "policy_projection": "candidate_read_projection",
        },
        {
            "id": "app_diagnostics_snapshot",
            "method": "POST",
            "path": "/cockpit/projects/launch/diagnostics/snapshot",
            "surface": "app_diagnostics",
            "route_class": "local_control",
            "capability": "preview_launch",
            "sensitivity": "local_control",
            "auth_required": True,
            "same_origin_required": True,
            "confirmation_required": False,
            "policy_projection": "candidate_policy_projection_required",
        },
        {
            "id": "project_launch_start",
            "method": "POST",
            "path": "/cockpit/projects/launch/start",
            "surface": "project_launcher",
            "route_class": "local_control",
            "capability": "preview_launch",
            "sensitivity": "local_control",
            "auth_required": True,
            "same_origin_required": True,
            "confirmation_required": False,
            "policy_projection": "candidate_policy_projection_required",
        },
        {
            "id": "project_launch_stop",
            "method": "POST",
            "path": "/cockpit/projects/launch/stop",
            "surface": "project_launcher",
            "route_class": "local_control",
            "capability": "local_control_request",
            "sensitivity": "local_control",
            "auth_required": False,
            "same_origin_required": True,
            "confirmation_required": True,
            "policy_projection": "needs_auth_parity_review",
        },
    ]
    for row in route_rows:
        row["mutation"] = row["method"] not in {"GET", "HEAD", "OPTIONS"}
    return route_rows


def _security_summary(env: dict[str, str] | None = None, route_matrix: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    values = env or os.environ
    routes = route_matrix or _route_matrix()
    public_token_configured = bool((values.get(PUBLIC_COCKPIT_TOKEN_ENV) or "").strip())
    dedicated_session_secret_configured = bool((values.get(SESSION_SECRET_ENV) or "").strip())
    session_secret_configured = bool(cockpit_session_secret(values))
    invite_rows = invite_token_rows(values)
    oauth_configured = google_oauth_configured(values)
    allowlist_configured = bool((values.get(ALLOWED_EMAILS_ENV) or "").strip())
    mutation_routes = [row for row in routes if row.get("mutation")]
    unguarded_mutations = [row for row in mutation_routes if not row.get("same_origin_required")]
    unauthenticated_local_control = [
        row
        for row in mutation_routes
        if row.get("route_class") == "local_control" and not row.get("auth_required")
    ]
    findings: list[dict[str, Any]] = []
    if not (session_secret_configured or public_token_configured or invite_rows or oauth_configured):
        findings.append(
            {
                "id": "public-cockpit-auth-not-configured",
                "severity": "high",
                "title": "Public cockpit auth is not configured",
                "detail": "The diagnostics model expects cockpit auth before exposing system routes.",
            }
        )
    if public_token_configured and not dedicated_session_secret_configured:
        findings.append(
            {
                "id": "session-secret-public-token-fallback",
                "severity": "medium",
                "title": "Session signing falls back to the public token",
                "detail": "Set a dedicated cockpit session secret so permission-token rotation does not also rotate session signing.",
            }
        )
    if oauth_configured and not allowlist_configured and not invite_rows:
        findings.append(
            {
                "id": "google-oauth-without-allowlist-or-invite",
                "severity": "medium",
                "title": "Google OAuth needs an allowlist or invite gate",
                "detail": "OAuth login should stay paired with explicit allowed emails or invite-token binding.",
            }
        )
    if unguarded_mutations:
        findings.append(
            {
                "id": "mutation-route-missing-same-origin",
                "severity": "high",
                "title": "Mutation route missing same-origin gate",
                "detail": f"{len(unguarded_mutations)} projected mutation route(s) are missing same-origin protection.",
            }
        )
    if unauthenticated_local_control:
        findings.append(
            {
                "id": "local-control-route-auth-parity-review",
                "severity": "medium",
                "title": "Local-control route needs auth parity review",
                "detail": f"{len(unauthenticated_local_control)} projected local-control route(s) are same-origin gated but not marked auth-required.",
            }
        )
    return {
        "schema_id": "ion.system_diagnostics.security_summary.v1",
        "auth_configured": bool(session_secret_configured or public_token_configured or invite_rows or oauth_configured),
        "session_cookie": SESSION_COOKIE,
        "session_secret_configured": session_secret_configured,
        "dedicated_session_secret_configured": dedicated_session_secret_configured,
        "session_secret_source": "dedicated_session_secret" if dedicated_session_secret_configured else "public_token_fallback" if public_token_configured else "missing",
        "public_token_configured": public_token_configured,
        "invite_token_count": len(invite_rows),
        "google_oauth_configured": oauth_configured,
        "google_client_id_configured": bool((values.get(GOOGLE_CLIENT_ID_ENV) or "").strip()),
        "google_allowlist_configured": allowlist_configured,
        "mutation_route_count": len(mutation_routes),
        "same_origin_mutation_required": not unguarded_mutations,
        "unauthenticated_local_control_route_count": len(unauthenticated_local_control),
        "cookie_policy": {"http_only": True, "same_site": "Lax", "secure_when_https": True},
        "token_values_emitted": False,
        "secret_values_emitted": False,
        "findings": _rank_issues(findings),
        "authority": {
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    }


def _service_health(root: Path) -> dict[str, Any]:
    try:
        model = build_service_console_model(root)
    except Exception as exc:
        return {
            "schema_id": "ion.system_diagnostics.service_health.v1",
            "verdict": "unknown",
            "ok": False,
            "finding": exc.__class__.__name__,
            "services": [],
            "authority": {
                "accepted_state_authority": False,
                "production_authority": False,
                "live_execution_authority": False,
            },
        }
    services = []
    for service in model.get("services") or []:
        if not isinstance(service, dict):
            continue
        services.append(
            {
                "id": service.get("id"),
                "unit": service.get("unit"),
                "label": service.get("label"),
                "role": service.get("role"),
                "critical": bool(service.get("critical")),
                "active": bool(service.get("active")),
                "status": service.get("status"),
                "finding": service.get("finding"),
                "severity": service.get("severity"),
                "restart_confirmation": service.get("restart_confirmation"),
            }
        )
    return {
        "schema_id": "ion.system_diagnostics.service_health.v1",
        "ok": bool(model.get("ok")),
        "verdict": model.get("verdict"),
        "headline": model.get("headline"),
        "required_issue_count": model.get("required_issue_count"),
        "warning_count": model.get("warning_count"),
        "service_count": len(services),
        "services": services,
        "authority": {
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
        },
    }


def _action_eligibility(
    *,
    pid: int | None,
    dev_server: bool,
    protected: bool,
    cleanup_candidate: bool,
    stale: bool = False,
) -> dict[str, Any]:
    reasons: list[str] = []
    if pid is None:
        reasons.append("NO_PID")
    if not dev_server:
        reasons.append("NOT_DEV_SERVER")
    if protected:
        reasons.append("PROTECTED_PROCESS")
    if dev_server and not protected and pid is not None and not cleanup_candidate:
        reasons.append("NOT_CLEANUP_CANDIDATE")
    if cleanup_candidate:
        reasons.append("SAFE_CLEANUP_CANDIDATE")
    if stale:
        reasons.append("STALE_LOW_CPU")
    allowed = bool(cleanup_candidate and pid is not None and dev_server and not protected)
    return {
        "action_type": "stop_process",
        "allowed": allowed,
        "stoppable": allowed,
        "reasons": reasons or ["NO_ACTION_REASON"],
        "requires_confirmation": True,
        "required_confirmation": STOP_CONFIRMATION if allowed else None,
        "policy_projection": "local_control_candidate",
    }


def _risk_summary(
    *,
    issues: list[dict[str, Any]],
    dev_servers: list[dict[str, Any]],
    cleanup_candidates: list[dict[str, Any]],
    security_summary: dict[str, Any],
    service_health: dict[str, Any],
) -> dict[str, Any]:
    severity_counts = Counter(str(issue.get("severity") or "info") for issue in issues)
    security_findings = security_summary.get("findings") if isinstance(security_summary.get("findings"), list) else []
    service_services = service_health.get("services") if isinstance(service_health.get("services"), list) else []
    service_blocked = [
        service for service in service_services
        if isinstance(service, dict) and service.get("critical") and not service.get("active")
    ]
    high_or_critical = severity_counts.get("high", 0) + severity_counts.get("critical", 0)
    security_high = sum(1 for item in security_findings if isinstance(item, dict) and item.get("severity") in {"high", "critical"})
    verdict = "ready"
    if high_or_critical or security_high or service_blocked:
        verdict = "attention"
    elif severity_counts.get("medium", 0) or security_findings or cleanup_candidates:
        verdict = "review"
    return {
        "schema_id": "ion.system_diagnostics.risk_summary.v1",
        "verdict": verdict,
        "issue_count": len(issues),
        "severity_counts": dict(severity_counts),
        "actionable_cleanup_count": len(cleanup_candidates),
        "protected_dev_server_count": sum(1 for server in dev_servers if server.get("protected")),
        "stale_dev_server_count": sum(1 for server in dev_servers if server.get("stale")),
        "security_finding_count": len(security_findings),
        "critical_service_issue_count": len(service_blocked),
        "authority": {
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "secrets_authority": False,
        },
    }


def _risk_findings(
    issues: list[dict[str, Any]],
    security_summary: dict[str, Any],
    service_health: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = [
        {
            "id": issue.get("id"),
            "severity": issue.get("severity"),
            "category": "system",
            "title": issue.get("title"),
            "detail": issue.get("detail"),
            "evidence": issue.get("evidence") or [],
        }
        for issue in issues
    ]
    for finding in security_summary.get("findings") or []:
        if not isinstance(finding, dict):
            continue
        rows.append(
            {
                "id": finding.get("id"),
                "severity": finding.get("severity"),
                "category": "security",
                "title": finding.get("title"),
                "detail": finding.get("detail"),
                "evidence": [],
            }
        )
    for service in service_health.get("services") or []:
        if not isinstance(service, dict) or service.get("active"):
            continue
        rows.append(
            {
                "id": f"service-{service.get('id')}",
                "severity": "high" if service.get("critical") else "medium",
                "category": "service",
                "title": f"{service.get('label') or service.get('id')} is {service.get('status') or 'not active'}",
                "detail": service.get("finding"),
                "evidence": [str(service.get("unit") or "")],
            }
        )
    return _rank_issues(rows)


def _read_cwd(pid: int) -> str | None:
    try:
        return os.readlink(f"/proc/{pid}/cwd")
    except Exception:
        return None


def _classify_workspace(cwd: str | None, command: str = "") -> str:
    haystack = f"{cwd or ''} {command}"
    if "/home/sev/Application_Dev" in haystack:
        return "Application_Dev"
    if "/home/sev/Cosmos" in haystack or "/Cosmos/" in haystack:
        return "Cosmos"
    if "/home/sev/ION - Production" in haystack:
        return "ION"
    if "/home/sev/.codex" in haystack:
        return "Codex"
    if "/home/sev/Documents" in haystack:
        return "Documents"
    if "/home/sev/Downloads" in haystack:
        return "Downloads"
    if "/home/sev" in haystack:
        return "Home"
    return "System"


def _is_under(path: str | None, root: Path) -> bool:
    if not path:
        return False
    try:
        Path(path).resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except Exception:
        return False


def _protected_process(pid: int, command: str = "", cwd: str | None = None, ion_root: Path | None = None) -> bool:
    lower = f"{command} {cwd or ''}".lower()
    if pid <= 1:
        return True
    markers = (
        "codex",
        "kernel.ion_",
        "ion_chatgpt",
        "ion_local_cockpit",
        "cloudflared",
        "systemd",
        "gnome-shell",
        "xorg",
        "chrome",
        "qdrant",
        "dgraph",
        "rustdesk",
        "pipewire",
        "pulseaudio",
    )
    if any(marker in lower for marker in markers):
        return True
    if ion_root is not None and _is_under(cwd, ion_root):
        return _classify_workspace(cwd, command) not in STOPPABLE_PROJECT_WORKSPACES
    return False


def _dev_server(command: str = "", cwd: str | None = None, ion_root: Path | None = None) -> bool:
    lower = command.lower()
    markers = (
        "vite",
        "webpack",
        "webpack-dev-server",
        "next-server",
        "next dev",
        "astro dev",
        "npm run dev",
        "pnpm dev",
        "yarn dev",
        "bun --bun vite",
        "react-scripts start",
        "remix vite:dev",
        "nuxt dev",
        "parcel",
        "http.server",
        "simplehttpserver",
        "live-server",
        "serve ",
    )
    return any(marker in lower for marker in markers) or (
        "node" in lower and cwd is not None and ("/application_dev/" in cwd.lower() or "/cosmos/" in cwd.lower()) and (Path(cwd) / "package.json").exists()
    )


def _dev_server_reason(command: str = "", cwd: str | None = None) -> str | None:
    lower = command.lower()
    if "vite" in lower:
        return "vite_command"
    if "next-server" in lower or "next dev" in lower:
        return "next_command"
    if "webpack" in lower:
        return "webpack_command"
    if "astro dev" in lower:
        return "astro_command"
    if "http.server" in lower or "simplehttpserver" in lower:
        return "python_http_server"
    if "live-server" in lower or "serve " in lower:
        return "static_server_command"
    if cwd and (Path(cwd) / "package.json").exists() and "node" in lower:
        return "node_package_listener"
    return None


def _framework_from_command(command: str = "", cwd: str | None = None) -> str:
    lower = command.lower()
    if "vite" in lower:
        return "vite"
    if "next-server" in lower or "next dev" in lower:
        return "next"
    if "astro dev" in lower:
        return "astro"
    if "webpack" in lower:
        return "webpack"
    if "react-scripts" in lower:
        return "cra"
    if "http.server" in lower or "simplehttpserver" in lower:
        return "static"
    package = _package_metadata(cwd)
    deps = " ".join(sorted(package.get("dependencies", [])))
    if "vite" in deps:
        return "vite"
    if "next" in deps:
        return "next"
    if "react" in deps:
        return "react"
    return "unknown"


def _package_metadata(cwd: str | None) -> dict[str, Any]:
    if not cwd:
        return {}
    root = Path(cwd).resolve(strict=False)
    for path in (root, *list(root.parents)[:3]):
        package_path = path / "package.json"
        if not package_path.exists():
            continue
        try:
            data = json.loads(package_path.read_text(encoding="utf-8"))
        except Exception:
            return {"package_path": package_path.as_posix(), "package_parse_error": True}
        deps = set()
        for key in ("dependencies", "devDependencies"):
            value = data.get(key)
            if isinstance(value, dict):
                deps.update(str(item) for item in value)
        return {
            "package_name": str(data.get("name") or path.name),
            "package_path": package_path.as_posix(),
            "dependencies": sorted(deps),
        }
    return {}


def collect_processes(ion_root: str | Path = ".") -> list[dict[str, Any]]:
    root = Path(ion_root).resolve()
    stdout = _run_text("ps", ["-eo", "pid=,ppid=,stat=,etimes=,pcpu=,pmem=,rss=,comm=,args="], timeout=6.0)
    rows: list[dict[str, Any]] = []
    for line in stdout.splitlines():
        parts = line.strip().split(None, 8)
        if len(parts) < 8:
            continue
        try:
            pid = int(parts[0])
        except ValueError:
            continue
        ppid = int(parts[1]) if parts[1].isdigit() else 0
        elapsed = int(parts[3]) if parts[3].isdigit() else 0
        cpu_percent = float(parts[4]) if _looks_float(parts[4]) else 0.0
        memory_percent = float(parts[5]) if _looks_float(parts[5]) else 0.0
        rss_kb = int(parts[6]) if parts[6].isdigit() else 0
        name = parts[7]
        raw_command = parts[8] if len(parts) > 8 else name
        command, redaction_count = _redact_sensitive_text(raw_command)
        command = command or name
        cwd = _read_cwd(pid)
        protected = _protected_process(pid, raw_command, cwd, root)
        dev_server = _dev_server(raw_command, cwd, root)
        package = _package_metadata(cwd)
        rows.append(
            {
                "pid": pid,
                "ppid": ppid,
                "state": parts[2],
                "elapsed_seconds": elapsed,
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "rss_kb": rss_kb,
                "command": command,
                "command_redacted": redaction_count > 0,
                "name": name,
                "cwd": cwd,
                "workspace": _classify_workspace(cwd, raw_command),
                "protected": protected,
                "dev_server": dev_server,
                "dev_server_reason": _dev_server_reason(raw_command, cwd),
                "framework": _framework_from_command(raw_command, cwd) if dev_server else None,
                "package_name": package.get("package_name"),
                "package_path": package.get("package_path"),
            }
        )
    rows.sort(key=lambda row: (-float(row["cpu_percent"]), -int(row["rss_kb"])))
    return rows


def collect_ports(processes: list[dict[str, Any]], ion_root: str | Path = ".") -> list[dict[str, Any]]:
    root = Path(ion_root).resolve()
    by_pid = {int(row["pid"]): row for row in processes}
    stdout = _run_text("ss", ["-ltnp"], timeout=5.0)
    rows: list[dict[str, Any]] = []
    for line in stdout.splitlines()[1:]:
        if "LISTEN" not in line:
            continue
        columns = line.strip().split()
        if len(columns) < 4:
            continue
        local = columns[3]
        port = _parse_port(local)
        if port is None:
            continue
        pid_match = re.search(r"pid=(\d+)", line)
        pid = int(pid_match.group(1)) if pid_match else None
        process = by_pid.get(pid) if pid is not None else None
        command = str(process.get("command") or "") if process else ""
        cwd = str(process.get("cwd") or "") if process and process.get("cwd") else None
        name_match = re.search(r'users:\(\("([^"]+)"', line)
        protected = bool(process.get("protected")) if process else True
        dev_server = bool(process.get("dev_server")) if process else _dev_server(command, cwd, root)
        package = _package_metadata(cwd)
        rows.append(
            {
                "protocol": "tcp",
                "local_address": _parse_address(local),
                "port": port,
                "pid": pid,
                "process_name": name_match.group(1) if name_match else (process.get("name") if process else None),
                "command": command or None,
                "cwd": cwd,
                "workspace": str(process.get("workspace")) if process else _classify_workspace(cwd, command),
                "dev_server": dev_server,
                "dev_server_reason": (process.get("dev_server_reason") if process else None) or _dev_server_reason(command, cwd),
                "framework": (process.get("framework") if process else None) or (_framework_from_command(command, cwd) if dev_server else None),
                "package_name": (process.get("package_name") if process else None) or package.get("package_name"),
                "package_path": (process.get("package_path") if process else None) or package.get("package_path"),
                "protected": protected,
                "cleanup_candidate": bool(dev_server and not protected and pid),
            }
        )
    rows.sort(key=lambda row: int(row["port"]))
    return rows[:MAX_PORT_ROWS]


def build_system_diagnostics_model(ion_root: str | Path = ".") -> dict[str, Any]:
    root = Path(ion_root).resolve()
    processes = collect_processes(root)
    ports = collect_ports(processes, root)
    mem = _mem_info()
    memory_total = int(mem.get("MemTotal", 0))
    memory_used = memory_total - int(mem.get("MemAvailable", 0))
    swap_total = int(mem.get("SwapTotal", 0))
    swap_used = swap_total - int(mem.get("SwapFree", 0))
    cpu_percent = _cpu_percent()
    disk_percent = _disk_percent()
    cleanup_candidates = _cleanup_candidates(ports, processes)
    dev_servers = _dev_servers(ports, processes)
    issues = _rank_issues(
        [
            *_detect_issues(memory_total, memory_used, swap_total, swap_used, cpu_percent, disk_percent, ports, processes),
            *_detect_dev_server_issues(dev_servers),
        ]
    )
    stale_count = sum(1 for row in cleanup_candidates if row.get("stale"))
    protected_dev_server_count = sum(1 for row in dev_servers if row.get("protected"))
    verified_dev_server_count = sum(1 for row in dev_servers if row.get("http_probe", {}).get("serves_http"))
    route_matrix = _route_matrix()
    security_summary = _security_summary(route_matrix=route_matrix)
    service_health = _service_health(root)
    risk_summary = _risk_summary(
        issues=issues,
        dev_servers=dev_servers,
        cleanup_candidates=cleanup_candidates,
        security_summary=security_summary,
        service_health=service_health,
    )
    risk_findings = _risk_findings(issues, security_summary, service_health)
    redacted_process_command_count = sum(1 for row in processes if row.get("command_redacted"))
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _utc_now(),
        "status": "ready",
        "summary": {
            "cpu_percent": cpu_percent,
            "load_avg": _load_avg(),
            "memory_total_mb": memory_total / 1024,
            "memory_used_mb": memory_used / 1024,
            "memory_percent": (memory_used / memory_total) * 100 if memory_total else 0,
            "swap_total_mb": swap_total / 1024,
            "swap_used_mb": swap_used / 1024,
            "swap_percent": (swap_used / swap_total) * 100 if swap_total else 0,
            "disk_percent": disk_percent,
            "uptime_seconds": _uptime_seconds(),
            "process_count": len(processes),
            "listener_count": len(ports),
            "active_dev_server_count": len(dev_servers),
            "protected_dev_server_count": protected_dev_server_count,
            "http_verified_dev_server_count": verified_dev_server_count,
            "cleanup_candidate_count": len(cleanup_candidates),
            "stale_port_count": stale_count,
            "issue_count": len(issues),
            "risk_finding_count": len(risk_findings),
            "security_finding_count": len(security_summary.get("findings") or []),
            "service_issue_count": int(service_health.get("required_issue_count") or 0) + int(service_health.get("warning_count") or 0),
        },
        "top_processes": processes[:MAX_PROCESS_ROWS],
        "ports": ports,
        "dev_servers": dev_servers,
        "cleanup_candidates": cleanup_candidates,
        "issues": issues,
        "risk_summary": risk_summary,
        "risk_findings": risk_findings,
        "service_health": service_health,
        "route_matrix": route_matrix,
        "security_summary": security_summary,
        "policy_projection": build_authorization_evaluator_projection(),
        "redaction_summary": {
            "schema_id": "ion.system_diagnostics.redaction_summary.v1",
            "command_redaction_enabled": True,
            "secret_value_redaction_enabled": True,
            "redacted_process_command_count": redacted_process_command_count,
            "token_values_emitted": False,
            "secret_values_emitted": False,
        },
        "data_quality": {
            "process_source": "ps",
            "port_source": "ss -ltnp",
            "http_probe_timeout_seconds": HTTP_PROBE_TIMEOUT_SECONDS,
            "active_dev_servers_are_probe_verified": verified_dev_server_count,
            "dev_server_count_includes_protected": True,
            "cleanup_candidates_exclude_protected": True,
            "command_redaction_enabled": True,
            "redacted_process_command_count": redacted_process_command_count,
            "route_matrix_source": "static_cockpit_projection",
            "service_health_source": "systemctl_user_is_active",
        },
        "action_contract": {
            "stop_confirmation": STOP_CONFIRMATION,
            "preview_endpoint": "/cockpit/system/preview_action",
            "execute_endpoint": "/cockpit/system/execute_action",
        },
        "authority": {
            "local_operator_action_authority": True,
            "accepted_state_authority": False,
            "production_authority": False,
            "live_execution_authority": False,
            "protected_processes_blocked": True,
        },
    }


def preview_system_diagnostic_action(ion_root: str | Path, action: dict[str, Any]) -> dict[str, Any]:
    if action.get("action_type") != "stop_process":
        raise ValueError(f"unsupported action type: {action.get('action_type')}")
    root = Path(ion_root).resolve()
    processes = collect_processes(root)
    ports = collect_ports(processes, root)
    target_pid = _target_pid(action, ports)
    if target_pid is None:
        raise ValueError("no process found for that target")
    process = next((row for row in processes if int(row["pid"]) == target_pid), None)
    if process is None:
        raise ValueError(f"pid {target_pid} is no longer running")
    child_pids = _descendants(target_pid, processes)
    affected_pids = sorted(set([target_pid, *child_pids]))
    affected_ports = sorted({int(row["port"]) for row in ports if row.get("pid") in affected_pids})
    warnings: list[str] = []
    if process.get("protected"):
        warnings.append("Protected process: ION, Codex, browser, desktop, system, or infrastructure marker matched.")
    if not process.get("dev_server"):
        warnings.append("This does not look like a normal local dev server.")
    allowed = bool(process.get("dev_server") and not process.get("protected"))
    return {
        "action_type": "stop_process",
        "title": f"Stop {process.get('name') or 'process'}",
        "detail": f"Send SIGTERM to pid {target_pid} and child processes, then refresh the diagnostics model.",
        "affected_pids": affected_pids,
        "affected_ports": affected_ports,
        "warnings": warnings,
        "allowed": allowed,
        "requires_confirmation": True,
        "required_confirmation": STOP_CONFIRMATION,
    }


def execute_system_diagnostic_action(ion_root: str | Path, action: dict[str, Any]) -> dict[str, Any]:
    if action.get("confirmation") != STOP_CONFIRMATION and action.get("confirmed") is not True:
        raise ValueError("action requires explicit confirmation")
    plan = preview_system_diagnostic_action(ion_root, action)
    if not plan["allowed"]:
        raise ValueError("action blocked: " + "; ".join(plan["warnings"]))
    for pid in reversed(plan["affected_pids"]):
        try:
            os.kill(int(pid), signal.SIGTERM)
        except ProcessLookupError:
            continue
    time.sleep(1.0)
    still_running = [pid for pid in plan["affected_pids"] if Path(f"/proc/{pid}").exists()]
    return {
        "timestamp": _utc_now(),
        "action_type": "stop_process",
        "target": f"pid {action.get('target_pid')}" if action.get("target_pid") else f"port {action.get('target_port')}",
        "status": "partial" if still_running else "ok",
        "detail": (
            f"SIGTERM sent, but these pids are still running: {', '.join(str(pid) for pid in still_running)}"
            if still_running
            else f"Stopped process group for {action.get('target_pid') or action.get('target_port')}"
        ),
        "affected_pids": plan["affected_pids"],
        "affected_ports": plan["affected_ports"],
    }


def _cleanup_candidates(ports: list[dict[str, Any]], processes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_pid = {int(row["pid"]): row for row in processes}
    candidates = []
    seen: set[int] = set()
    for port in ports:
        pid = port.get("pid")
        if not isinstance(pid, int) or pid in seen or not port.get("cleanup_candidate"):
            continue
        seen.add(pid)
        process = by_pid.get(pid, {})
        stale = int(process.get("elapsed_seconds") or 0) >= 4 * 3600 and float(process.get("cpu_percent") or 0) <= 2
        eligibility = _action_eligibility(
            pid=pid,
            dev_server=bool(port.get("dev_server")),
            protected=bool(port.get("protected")),
            cleanup_candidate=True,
            stale=stale,
        )
        candidates.append(
            {
                "id": f"{pid}:{port.get('port')}",
                "pid": pid,
                "port": port.get("port"),
                "process_name": port.get("process_name") or process.get("name"),
                "workspace": port.get("workspace"),
                "cwd": port.get("cwd"),
                "elapsed_seconds": process.get("elapsed_seconds", 0),
                "cpu_percent": process.get("cpu_percent", 0),
                "stale": stale,
                "action_eligibility": eligibility,
                "action": {"action_type": "stop_process", "target_pid": pid, "target_port": port.get("port")},
            }
        )
    candidates.sort(key=lambda row: (not bool(row["stale"]), str(row.get("workspace") or ""), int(row.get("port") or 0)))
    return candidates[:80]


def _dev_servers(ports: list[dict[str, Any]], processes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_pid = {int(row["pid"]): row for row in processes}
    rows: list[dict[str, Any]] = []
    seen: set[tuple[int | None, int]] = set()
    for port in ports:
        port_number = port.get("port")
        if not isinstance(port_number, int):
            continue
        process = by_pid.get(int(port["pid"])) if isinstance(port.get("pid"), int) else {}
        protected = bool(port.get("protected"))
        dev_server = bool(port.get("dev_server"))
        project_workspace = port.get("workspace") in {"Application_Dev", "Cosmos"}
        if not dev_server and not project_workspace:
            continue
        key = (port.get("pid") if isinstance(port.get("pid"), int) else None, port_number)
        if key in seen:
            continue
        seen.add(key)
        elapsed_seconds = int(process.get("elapsed_seconds") or 0)
        stale = elapsed_seconds >= 4 * 3600 and float(process.get("cpu_percent") or 0) <= 2
        probe = _probe_http_port(port)
        cleanup_candidate = bool(port.get("cleanup_candidate"))
        rows.append(
            {
                "id": f"{port.get('pid') or 'unknown'}:{port_number}",
                "port": port_number,
                "pid": port.get("pid"),
                "process_name": port.get("process_name") or process.get("name"),
                "workspace": port.get("workspace"),
                "cwd": port.get("cwd"),
                "command": port.get("command") or process.get("command"),
                "elapsed_seconds": elapsed_seconds,
                "cpu_percent": process.get("cpu_percent", 0),
                "rss_kb": process.get("rss_kb", 0),
                "protected": protected,
                "dev_server": dev_server,
                "cleanup_candidate": cleanup_candidate,
                "stale": stale,
                "framework": port.get("framework") or process.get("framework") or "unknown",
                "package_name": port.get("package_name") or process.get("package_name"),
                "package_path": port.get("package_path") or process.get("package_path"),
                "reason": port.get("dev_server_reason") or process.get("dev_server_reason") or ("project_workspace_listener" if project_workspace else "unknown"),
                "confidence": "high" if dev_server and probe.get("serves_http") else ("medium" if dev_server else "low"),
                "http_probe": probe,
                "action_eligibility": _action_eligibility(
                    pid=port.get("pid") if isinstance(port.get("pid"), int) else None,
                    dev_server=dev_server,
                    protected=protected,
                    cleanup_candidate=cleanup_candidate,
                    stale=stale,
                ),
                "action": {"action_type": "stop_process", "target_pid": port.get("pid"), "target_port": port_number},
            }
        )
    rows.sort(key=lambda row: (not bool(row.get("http_probe", {}).get("serves_http")), not bool(row.get("dev_server")), str(row.get("workspace") or ""), int(row.get("port") or 0)))
    return rows[:MAX_DEV_SERVER_ROWS]


def _probe_http_port(port: dict[str, Any]) -> dict[str, Any]:
    port_number = port.get("port")
    if not isinstance(port_number, int):
        return {"serves_http": False, "finding": "port_missing"}
    address = str(port.get("local_address") or "127.0.0.1").strip("[]")
    if address in {"", "0.0.0.0", "::", "*"} or "%" in address:
        address = "127.0.0.1"
    if address not in {"127.0.0.1", "localhost", "::1"}:
        return {"serves_http": False, "url": f"http://{address}:{port_number}/", "finding": "non_loopback_not_probed"}
    url = f"http://127.0.0.1:{port_number}/"
    try:
        request = urllib.request.Request(url, headers={"Accept": "text/html,application/json,text/plain"})
        with urllib.request.urlopen(request, timeout=HTTP_PROBE_TIMEOUT_SECONDS) as response:
            body = response.read(8192).decode("utf-8", errors="replace")
            status = int(getattr(response, "status", 0) or 0)
    except urllib.error.HTTPError as exc:
        body = exc.read(8192).decode("utf-8", errors="replace")
        status = int(exc.code)
        return {
            "serves_http": True,
            "url": url,
            "http_status": status,
            "finding": "http_error_status",
            "title": _html_title(body),
        }
    except Exception as exc:
        return {"serves_http": False, "url": url, "http_status": None, "finding": exc.__class__.__name__}
    return {
        "serves_http": 200 <= status < 500,
        "url": url,
        "http_status": status,
        "finding": "ok" if 200 <= status < 400 else "http_non_success_status",
        "title": _html_title(body),
    }


def _html_title(body: str) -> str | None:
    match = re.search(r"<title[^>]*>(.*?)</title>", body, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip()[:160] or None


def _detect_issues(
    memory_total: int,
    memory_used: int,
    swap_total: int,
    swap_used: int,
    cpu_percent: float,
    disk_percent: float,
    ports: list[dict[str, Any]],
    processes: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    memory_percent = (memory_used / memory_total) * 100 if memory_total else 0
    swap_percent = (swap_used / swap_total) * 100 if swap_total else 0
    if memory_percent >= 85:
        issues.append(_issue("memory-pressure", "high", "Memory pressure is high", f"Memory is {memory_percent:.0f}% used.", [f"{round(memory_used / 1024)} MB used"]))
    if swap_percent >= 40:
        issues.append(_issue("swap-pressure", "medium", "Swap usage can cause lag", f"Swap is {swap_percent:.0f}% used.", [f"{round(swap_used / 1024)} MB swap used"]))
    if cpu_percent >= 85:
        issues.append(_issue("cpu-pressure", "high", "CPU pressure is high", f"CPU is {cpu_percent:.0f}% busy.", ["Check top process list."]))
    if disk_percent >= 85:
        issues.append(_issue("disk-pressure", "medium", "Disk is getting full", f"Root disk is {disk_percent:.0f}% used.", ["Low disk can break builds and caches."]))
    app_dev_ports = [port for port in ports if port.get("workspace") == "Application_Dev" and port.get("dev_server")]
    if len(app_dev_ports) >= 10:
        issues.append(_issue("many-application-dev-listeners", "medium", "Many Application_Dev servers are listening", f"{len(app_dev_ports)} Application_Dev dev servers are holding localhost ports.", ["Use SYS cleanup candidates to stop unused servers."]))
    by_pid = {int(row["pid"]): row for row in processes}
    for candidate in _cleanup_candidates(ports, processes):
        if not candidate.get("stale"):
            continue
        pid = int(candidate["pid"])
        process = by_pid.get(pid, {})
        issues.append(
            {
                "id": f"stale-dev-server-{pid}",
                "severity": "medium",
                "title": f"Stale dev server on port {candidate.get('port')}",
                "detail": f"{candidate.get('process_name') or 'dev server'} has been running for {int(process.get('elapsed_seconds') or 0) // 3600} hours.",
                "evidence": [f"pid {pid}", f"port {candidate.get('port')}", str(candidate.get("cwd") or "no cwd")],
                "action": candidate["action"],
            }
        )
    return _rank_issues(issues)


def _detect_dev_server_issues(dev_servers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for server in dev_servers:
        probe = server.get("http_probe") or {}
        if server.get("dev_server") and not probe.get("serves_http"):
            port = server.get("port")
            finding = str(probe.get("finding") or "not_http_responsive")
            issues.append(
                {
                    "id": f"dev-server-http-probe-{port}",
                    "severity": "medium",
                    "title": f"Dev server on port {port} is not HTTP responsive",
                    "detail": f"{_dev_server_label(server)} is listening, but the local HTTP probe returned {finding}.",
                    "evidence": [
                        f"pid {server.get('pid') or 'unknown'}",
                        f"port {port}",
                        str(server.get("cwd") or server.get("command") or "no cwd"),
                    ],
                    "action": server.get("action") if server.get("cleanup_candidate") else None,
                }
            )
    return issues


def _dev_server_label(server: dict[str, Any]) -> str:
    probe = server.get("http_probe") or {}
    for key in ("package_name", "process_name", "framework"):
        value = server.get(key)
        if value:
            return str(value)
    if probe.get("title"):
        return str(probe["title"])
    return "Local dev server"


def _rank_issues(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rank = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
    return sorted(issues, key=lambda row: rank.get(str(row.get("severity")), 0), reverse=True)[:40]


def _issue(issue_id: str, severity: str, title: str, detail: str, evidence: list[str]) -> dict[str, Any]:
    return {"id": issue_id, "severity": severity, "title": title, "detail": detail, "evidence": evidence, "action": None}


def _mem_info() -> dict[str, int]:
    output: dict[str, int] = {}
    for line in _read_text("/proc/meminfo").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        parts = value.strip().split()
        output[key] = int(parts[0]) if parts and parts[0].isdigit() else 0
    return output


def _load_avg() -> list[float]:
    return [float(value) if _looks_float(value) else 0.0 for value in _read_text("/proc/loadavg").split()[:3]]


def _uptime_seconds() -> int:
    value = _read_text("/proc/uptime").split()
    return int(float(value[0])) if value and _looks_float(value[0]) else 0


def _cpu_snapshot() -> tuple[int, int]:
    parts = _read_text("/proc/stat").splitlines()[0].split()[1:]
    values = [int(value) if value.isdigit() else 0 for value in parts]
    idle = (values[3] if len(values) > 3 else 0) + (values[4] if len(values) > 4 else 0)
    return idle, sum(values)


def _cpu_percent() -> float:
    idle_a, total_a = _cpu_snapshot()
    time.sleep(0.05)
    idle_b, total_b = _cpu_snapshot()
    total = total_b - total_a
    idle = idle_b - idle_a
    return ((total - idle) / total) * 100 if total > 0 else 0.0


def _disk_percent() -> float:
    stdout = _run_text("df", ["-P", "/"], timeout=4.0)
    lines = stdout.splitlines()
    if len(lines) < 2:
        return 0.0
    parts = lines[1].split()
    return float(parts[4].rstrip("%")) if len(parts) > 4 and _looks_float(parts[4].rstrip("%")) else 0.0


def _descendants(root_pid: int, processes: list[dict[str, Any]]) -> list[int]:
    by_parent: dict[int, list[int]] = {}
    for row in processes:
        by_parent.setdefault(int(row.get("ppid") or 0), []).append(int(row["pid"]))
    out: list[int] = []
    stack = [root_pid]
    while stack:
        pid = stack.pop()
        for child in by_parent.get(pid, []):
            out.append(child)
            stack.append(child)
    return out


def _target_pid(action: dict[str, Any], ports: list[dict[str, Any]]) -> int | None:
    pid = action.get("target_pid")
    if isinstance(pid, int):
        return pid
    port = action.get("target_port")
    if isinstance(port, int):
        for row in ports:
            if row.get("port") == port and isinstance(row.get("pid"), int):
                return int(row["pid"])
    return None


def _parse_port(local: str) -> int | None:
    if ":" not in local:
        return None
    value = local.rsplit(":", 1)[-1]
    return int(value) if value.isdigit() else None


def _parse_address(local: str) -> str:
    if ":" not in local:
        return local
    return local.rsplit(":", 1)[0].strip("[]")


def _looks_float(value: str) -> bool:
    try:
        float(value)
    except ValueError:
        return False
    return True
