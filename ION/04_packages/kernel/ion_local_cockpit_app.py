"""Local-only ION cockpit web app.

This app renders the live cockpit projection for the operator and exposes narrow
guarded candidate-state writes for cockpit-owned project records. It has no
shell bridge, production authority, accepted-state authority, or live execution
authority.
"""

from __future__ import annotations

import argparse
import html
import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse
import urllib.request

from .ion_agent_invocation_broker import (
    agent_result,
    build_bounded_agent_status,
    control_agent_invocation,
    create_agent_relay_message,
    invoke_agent,
    pending_agent_relays,
    recent_agent_invocation_receipts,
    respond_agent_relay,
    settle_agent_invocation,
    swarm_step_once,
)
from .ion_agent_comms import (
    ack_agent_message,
    create_agent_message_branch,
    list_agent_threads,
    read_agent_thread,
    send_agent_message,
)
from .ion_agent_comms_runs import continue_agent_comms_run, pickup_agent_comms_run, start_agent_comms_run, start_agent_comms_run_worker
from .ion_agent_comms_audit_actions import audit_agent_comms_run, maybe_audit_agent_comms_result
from .ion_agent_spawn_templates import execute_agent_spawn_template
from .ion_steward_dispatcher import pause_steward_dispatcher, route_steward_dispatcher, run_steward_dispatcher_runner, tick_steward_dispatcher
from .ion_automation_control_plane import execute_automation_action
from .ion_build_workspace_model import build_build_workspace_model
from .ion_cockpit_view_model import build_cockpit_surface_view_model, build_cockpit_view_model
from .ion_cockpit_service_manager import RESTART_CONFIRMATION, build_service_console_model, restart_service
from .ion_codex_conversation_archive import attach_codex_conversation_to_chat, build_codex_conversation_archive
from .ion_codex_context_timeline import build_codex_context_timeline_model
from .ion_codex_git_rollback import (
    apply_codex_git_rollback,
    build_codex_git_rollback_model,
    capture_codex_diff_checkpoint,
    preview_codex_git_rollback,
)
from .ion_codex_ide_workbench import build_codex_ide_workbench_model
from .ion_codex_queue_runner import stop_active_codex_queue_runner
from .ion_chatgpt_browser_mcp_connector_contract import call_chatgpt_connector_tool
from .ion_dual_codex_chat import (
    WRITE_CONFIRMATION_TOKEN,
    build_dual_codex_chat_model,
    create_chat_branch,
    pin_dual_chat_memory,
    queue_chat_codex_work_packet,
    record_chat_turn,
    render_dual_codex_chat_html,
    resolve_chat_model_override,
)
from .ion_domain_weaver import execute_domain_weaver_action
from .ion_project_cockpit import PROJECT_COCKPIT_WRITE_CONFIRMATION, apply_project_cockpit_action
from .ion_project_launcher import (
    build_project_launcher_open_html,
    project_launcher_diagnostics,
    project_launcher_diagnostics_matrix,
    project_launcher_proxy_fetch,
    project_launcher_screenshot_file,
    project_launcher_start,
    project_launcher_status,
    project_launcher_stop,
)
from .ion_project_preview_sessions import build_project_preview_sessions_model
from .ion_app_diagnostics_timeline import (
    app_diagnostics_config_update,
    app_diagnostics_record_browser_event,
    app_diagnostics_record_http_event,
    app_diagnostics_snapshot,
    app_diagnostics_timeline_model,
)
from .ion_helixion_project_access_inventory import build_helixion_projects_surface_model_from_file
from .ion_project_portfolio import materialize_project_portfolio_action
from .ion_system_diagnostics import (
    build_system_diagnostics_model,
    execute_system_diagnostic_action,
    preview_system_diagnostic_action,
)
from .ion_scope_cockpit import build_scope_cockpit_model, render_scope_cockpit_html

SCHEMA_ID = "ion.local_cockpit_app.v1"
READY_VERDICT = "ION_LOCAL_COCKPIT_APP_READY"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8788
JOC_REACT_DIST = Path("ION/08_ui/joc_cockpit_shell/dist")
LEGACY_CSP = "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'"
BUILD_PREVIEW_SCRIPT_HASHES = (
    "'sha256-k59sHn5lU/5KRNtJuBEjwy5JrO65xximXYR4JRPkg6Y='",
    "'sha256-/vrpKG4NHzSZI4p8EC40bTsM/nNtQacF53bcLOnacWM='",
    "'sha256-9LoPJR9VY/9/Ad/ASyDJX/gx+OptRwrsNQfGCtaoLeU='",
    "'sha256-AkJskVSRwbkGUEkSrb+BvYupGuGYi5VmmWiqU5G5E6k='",
    "'sha256-Fgo4ohJMTFedkF1coY7+0nanCs/81jHD31q3AuxQKTc='",
    "'sha256-oQ4zDlv/dJiXk1ecAlhFUZAj+avYhaQt/fmbswEgCt4='",
)
REACT_CSP = (
    "default-src 'none'; script-src 'self' https://static.cloudflareinsights.com "
    + " ".join(BUILD_PREVIEW_SCRIPT_HASHES)
    + "; style-src 'self' 'unsafe-inline'; connect-src 'self' https://cloudflareinsights.com; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'"
)
PROJECT_LAUNCH_CSP = "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; frame-src http://127.0.0.1:* http://localhost:*; child-src http://127.0.0.1:* http://localhost:*; base-uri 'none'; frame-ancestors 'none'"
DEFAULT_APPLICATION_DEV_LAUNCHER_URL = "http://127.0.0.1:5199"


def _text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    return str(value)


def _escape(value: Any) -> str:
    return html.escape(_text(value), quote=True)


def _payload_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.splitlines() if item.strip()]
    return []


def _payload_mapping(payload: dict[str, Any], key: str) -> dict[str, Any] | None:
    value = payload.get(key)
    return value if isinstance(value, dict) else None


def _payload_int(payload: dict[str, Any], key: str, default: int) -> int:
    try:
        return int(payload.get(key) or default)
    except (TypeError, ValueError):
        return default


def application_dev_launcher_url() -> str:
    return (os.environ.get("ION_APPLICATION_DEV_LAUNCHER_URL") or DEFAULT_APPLICATION_DEV_LAUNCHER_URL).rstrip("/")


def application_dev_root() -> Path:
    return Path(os.environ.get("ION_APPLICATION_DEV_ROOT") or Path.home() / "Application_Dev").expanduser().resolve()


def _status_class(value: Any) -> str:
    lowered = _text(value, "unknown").lower().replace("_", "-")
    if lowered in {"ready", "configured", "active"}:
        return "is-ready"
    if lowered in {"blocked", "degraded", "missing-template", "not-running"}:
        return "is-blocked"
    return "is-watch"


def build_cockpit_health(root: str | Path = ".") -> dict[str, Any]:
    shell_root = Path(root).expanduser().resolve()
    return {
        "schema_id": SCHEMA_ID,
        "verdict": READY_VERDICT,
        "status": "ready",
        "shell_root": shell_root.as_posix(),
        "bind_host": DEFAULT_HOST,
        "default_port": DEFAULT_PORT,
        "visibility_only": False,
        "guarded_candidate_state_write_authority": True,
        "project_cockpit_write_confirmation": PROJECT_COCKPIT_WRITE_CONFIRMATION,
        "accepted_state_authority": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def react_cockpit_dist_root(root: str | Path = ".") -> Path:
    return Path(root).expanduser().resolve() / JOC_REACT_DIST


def build_react_cockpit_html(root: str | Path = ".") -> str | None:
    index_path = react_cockpit_dist_root(root) / "index.html"
    if not index_path.exists() or not index_path.is_file():
        return None
    return index_path.read_text(encoding="utf-8")


def resolve_react_static_asset(root: str | Path, request_path: str) -> Path | None:
    prefix = "/joc-static/"
    if not request_path.startswith(prefix):
        return None
    rel = unquote(request_path[len(prefix):]).lstrip("/")
    if not rel or "\x00" in rel:
        return None
    dist_root = react_cockpit_dist_root(root).resolve()
    target = (dist_root / rel).resolve()
    try:
        target.relative_to(dist_root)
    except ValueError:
        return None
    if not target.exists() or not target.is_file():
        return None
    return target


def build_cockpit_html(model: dict[str, Any]) -> str:
    runtime = model.get("runtime") if isinstance(model.get("runtime"), dict) else {}
    service_console = build_service_console_model(runtime.get("shell_root") or ".")
    top = model.get("top_bar") if isinstance(model.get("top_bar"), dict) else {}
    services = model.get("local_services") if isinstance(model.get("local_services"), dict) else {}
    service_rows = services.get("services") if isinstance(services.get("services"), list) else []
    mcp = model.get("chatgpt_browser_mcp") if isinstance(model.get("chatgpt_browser_mcp"), dict) else {}
    codex = mcp.get("codex_queue_runner") if isinstance(mcp.get("codex_queue_runner"), dict) else {}
    agent_broker = mcp.get("agent_invocation_broker") if isinstance(mcp.get("agent_invocation_broker"), dict) else {}
    queues = model.get("queues") if isinstance(model.get("queues"), dict) else {}
    timeline = model.get("timeline") if isinstance(model.get("timeline"), list) else []
    receipts = model.get("receipts") if isinstance(model.get("receipts"), list) else []

    def metric(label: str, value: Any) -> str:
        return f"<div class=\"metric\"><span>{_escape(label)}</span><b>{_escape(value)}</b></div>"

    def service_row(row: dict[str, Any]) -> str:
        status = _text(row.get("status"), "unknown")
        endpoint = row.get("public_url") or row.get("health_url") or row.get("local_url") or ""
        findings = ", ".join(str(item) for item in row.get("findings", []) if item)
        return (
            "<tr>"
            f"<td>{_escape(row.get('unit_name'))}</td>"
            f"<td><span class=\"pill {_status_class(status)}\">{_escape(status)}</span>"
            f"<small>{_escape(findings)}</small></td>"
            f"<td class=\"path\">{_escape(endpoint)}</td>"
            "</tr>"
        )

    def timeline_card(event: dict[str, Any]) -> str:
        status = _text(event.get("status"), "unknown")
        detail = event.get("detail") or event.get("path") or ""
        return (
            f"<article class=\"timeline-card {_status_class(status)}\">"
            f"<b>{_escape(event.get('source'))}</b>"
            f"<span>{_escape(event.get('event_type'))}</span>"
            f"<em>{_escape(status)}</em>"
            f"<p>{_escape(detail)}</p>"
            "</article>"
        )

    receipt_cards = []
    for receipt in receipts[:20]:
        if not isinstance(receipt, dict):
            continue
        receipt_cards.append(
            "<article class=\"receipt-card\">"
            f"<b>{_escape(receipt.get('name') or 'receipt')}</b>"
            f"<span>{_escape(receipt.get('authority_class') or 'RECEIPT')}</span>"
            f"<p class=\"path\">{_escape(receipt.get('path') or '')}</p>"
            "</article>"
        )

    timeline_cards = [timeline_card(event) for event in timeline[:40] if isinstance(event, dict)]
    service_table = "".join(service_row(row) for row in service_rows if isinstance(row, dict))
    service_console_cards = []
    for row in service_console.get("services", []):
        if not isinstance(row, dict):
            continue
        severity = _text(row.get("severity"), "watch")
        unit = _escape(row.get("unit"))
        service_console_cards.append(
            "<article class=\"service-console-card\">"
            f"<div><b>{_escape(row.get('label'))}</b><span class=\"pill {_status_class(severity)}\">{_escape(row.get('status'))}</span></div>"
            f"<p>{_escape(row.get('role'))}</p>"
            f"<small>{_escape(row.get('finding'))}</small>"
            "<form method=\"post\" action=\"/cockpit/services/restart\">"
            f"<input type=\"hidden\" name=\"unit\" value=\"{unit}\">"
            f"<input type=\"hidden\" name=\"confirmation\" value=\"{_escape(RESTART_CONFIRMATION)}\">"
            "<input type=\"hidden\" name=\"next\" value=\"/cockpit\">"
            f"<button type=\"submit\">{_escape(row.get('fix_label') or 'Restart')}</button>"
            "</form>"
            "</article>"
        )
    human_gates = queues.get("human_gates") if isinstance(queues.get("human_gates"), list) else []
    steward_items = queues.get("steward_integration") if isinstance(queues.get("steward_integration"), list) else []

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="20">
<title>ION Local Cockpit</title>
<style>
:root {{
  color-scheme: dark;
  --bg: #090b0c;
  --panel: #111517;
  --panel-2: #151b1e;
  --line: #293237;
  --text: #e6ecef;
  --muted: #8d9aa0;
  --green: #57c785;
  --amber: #d3a847;
  --red: #e15f5f;
  --blue: #6aa9e9;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--text); }}
main {{ min-height: 100vh; display: grid; grid-template-rows: auto 1fr; }}
header {{ display: flex; align-items: center; gap: 18px; padding: 12px 16px; border-bottom: 1px solid var(--line); background: #0d1113; }}
.brand {{ font-weight: 800; letter-spacing: 0; }}
.root {{ color: var(--muted); font-size: 12px; overflow-wrap: anywhere; }}
.status {{ margin-left: auto; }}
.layout {{ display: grid; grid-template-columns: minmax(0, 1fr) 360px; gap: 12px; padding: 12px; }}
.grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }}
.panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 6px; padding: 12px; min-width: 0; }}
.panel.wide {{ grid-column: 1 / -1; }}
h1, h2 {{ margin: 0; letter-spacing: 0; }}
h1 {{ font-size: 18px; }}
h2 {{ color: var(--muted); font-size: 11px; text-transform: uppercase; margin-bottom: 10px; }}
.objective {{ margin-top: 8px; color: var(--text); line-height: 1.4; }}
.metrics {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; margin-top: 12px; }}
.metric {{ background: var(--panel-2); border: 1px solid var(--line); border-radius: 4px; padding: 8px; min-height: 56px; }}
.metric span {{ display: block; color: var(--muted); font-size: 11px; }}
.metric b {{ display: block; margin-top: 6px; font-size: 14px; overflow-wrap: anywhere; }}
.pill {{ display: inline-flex; align-items: center; min-height: 24px; padding: 3px 8px; border-radius: 999px; border: 1px solid var(--line); font-size: 12px; }}
.is-ready {{ color: var(--green); }}
.is-watch {{ color: var(--amber); }}
.is-blocked {{ color: var(--red); }}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
td, th {{ border-top: 1px solid var(--line); padding: 8px 6px; text-align: left; vertical-align: top; }}
th {{ color: var(--muted); font-size: 11px; text-transform: uppercase; }}
small {{ display: block; color: var(--muted); margin-top: 4px; }}
.path {{ color: var(--muted); overflow-wrap: anywhere; }}
.timeline {{ display: grid; gap: 8px; max-height: 540px; overflow: auto; }}
.timeline-card, .receipt-card {{ background: var(--panel-2); border: 1px solid var(--line); border-radius: 4px; padding: 9px; }}
.timeline-card b, .timeline-card span, .timeline-card em {{ display: inline-block; margin-right: 8px; font-size: 12px; }}
.timeline-card p, .receipt-card p {{ margin: 6px 0 0; }}
.rail {{ display: grid; gap: 12px; align-content: start; }}
.receipt-list {{ display: grid; gap: 8px; max-height: 420px; overflow: auto; }}
.service-alert {{ border-color: rgba(225,95,95,0.45); background: linear-gradient(135deg, rgba(225,95,95,0.18), rgba(17,21,23,0.94)); }}
.service-alert.is-ready {{ border-color: rgba(87,199,133,0.35); background: linear-gradient(135deg, rgba(87,199,133,0.12), rgba(17,21,23,0.94)); }}
.service-console {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }}
.service-console-card {{ display: grid; gap: 8px; background: var(--panel-2); border: 1px solid var(--line); border-radius: 6px; padding: 10px; }}
.service-console-card div {{ display: flex; gap: 8px; align-items: center; justify-content: space-between; }}
.service-console-card p {{ margin: 0; color: var(--muted); font-size: 12px; line-height: 1.35; }}
.service-console-card form {{ margin: 0; }}
.service-console-card button {{ width: 100%; border: 1px solid rgba(255,255,255,0.18); border-radius: 5px; background: var(--blue); color: #041018; font-weight: 800; padding: 8px 10px; cursor: pointer; }}
pre {{ white-space: pre-wrap; margin: 0; color: var(--muted); font-size: 12px; }}
@media (max-width: 980px) {{
  .layout {{ grid-template-columns: 1fr; }}
  .grid {{ grid-template-columns: 1fr; }}
  .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .status {{ margin-left: 0; }}
  header {{ flex-wrap: wrap; }}
}}
</style>
</head>
<body>
<main>
<header>
  <div class="brand">ION LOCAL COCKPIT</div>
  <div class="root">{_escape(runtime.get("shell_root"))}</div>
  <div class="status pill {_status_class(runtime.get("status"))}">{_escape(runtime.get("status"))}</div>
</header>
<section class="layout">
  <section class="grid">
    <article class="panel wide">
      <h1>{_escape(top.get("objective") or "No active objective")}</h1>
      <div class="objective">Visibility-only local cockpit. Codex output remains proposal until proof-gated and accepted.</div>
      <div class="metrics">
        {metric("Services", services.get("status", top.get("local_service_status", "unknown")))}
        {metric("Codex queue", codex.get("queued_request_count", 0))}
        {metric("Codex active", codex.get("active_process_running", False))}
        {metric("Agent broker", agent_broker.get("verdict", "unknown"))}
        {metric("MCP transport", mcp.get("transport_state", "unknown"))}
        {metric("Connector", mcp.get("active_connector_url", "none"))}
        {metric("Human gates", top.get("gate_count", 0))}
        {metric("Steward queue", top.get("steward_queue_count", 0))}
      </div>
    </article>
    <article class="panel wide service-alert {'is-ready' if service_console.get('ok') else 'is-blocked'}">
      <h2>Console Alerts</h2>
      <h1>{_escape(service_console.get("headline"))}</h1>
      <div class="objective">{_escape(service_console.get("operator_message"))}</div>
      <div class="service-console">{''.join(service_console_cards)}</div>
    </article>
    <article class="panel wide">
      <h2>Helixion JOC Evolution</h2>
      <h1>{_escape((model.get("helixion_joc_rebuild") or {}).get("status", "not_documented"))}</h1>
      <div class="objective">{_escape((model.get("helixion_joc_rebuild") or {}).get("decision", "No Helixion rebuild plan loaded."))}</div>
      <div class="objective">Development URL: <a href="/joc/evolution">/joc/evolution</a> | <a href="/helixion/development">/helixion/development</a></div>
      {metric("Phase 1", "unlocked" if (model.get("helixion_joc_rebuild") or {}).get("ready_for_phase_1") else "blocked")}
      {metric("Plan", "present" if (model.get("helixion_joc_rebuild") or {}).get("master_plan_present") else "missing")}
      {metric("Registry", "present" if (model.get("helixion_joc_rebuild") or {}).get("registry_present") else "missing")}
      <pre>{_escape(json.dumps({
          "roles": (model.get("helixion_joc_rebuild") or {}).get("product_roles", {}),
          "surfaces": (model.get("helixion_joc_rebuild") or {}).get("required_surfaces", []),
          "next": (model.get("helixion_joc_rebuild") or {}).get("next_build_sequence", [])[:5],
          "forbidden_v1": (model.get("helixion_joc_rebuild") or {}).get("forbidden_v1_capabilities", []),
      }, indent=2, sort_keys=True))}</pre>
    </article>
    <article class="panel wide">
      <h2>Local Services</h2>
      <table><thead><tr><th>Unit</th><th>Status</th><th>Endpoint</th></tr></thead><tbody>{service_table}</tbody></table>
    </article>
    <article class="panel">
      <h2>Codex Carrier</h2>
      {metric("Runner verdict", codex.get("verdict", "unknown"))}
      {metric("Reconciliation write", (codex.get("reconciliation") or {}).get("write", False))}
      {metric("Next request", codex.get("next_request_path", "none"))}
    </article>
    <article class="panel">
      <h2>Queues</h2>
      {metric("Human gates", len(human_gates))}
      {metric("Steward items", len(steward_items))}
      {metric("Operator pending", top.get("operator_queue_pending", 0))}
    </article>
    <article class="panel">
      <h2>Authority</h2>
      {metric("Production", model.get("production_authority", False))}
      {metric("Live execution", model.get("live_execution_authority", False))}
      {metric("Runtime blocked", runtime.get("blocked", False))}
    </article>
    <article class="panel wide">
      <h2>Runtime Timeline</h2>
      <div class="timeline">{''.join(timeline_cards) or '<p class="path">No timeline events found.</p>'}</div>
    </article>
  </section>
  <aside class="rail">
    <article class="panel">
      <h2>Recent Receipts</h2>
      <div class="receipt-list">{''.join(receipt_cards) or '<p class="path">No receipts found.</p>'}</div>
    </article>
    <article class="panel">
      <h2>Source Paths</h2>
      <pre>{_escape(json.dumps(model.get("source_paths", {}), indent=2, sort_keys=True))}</pre>
    </article>
  </aside>
</section>
</main>
<style>
:root {{
  --dxl-bg: #050505;
  --dxl-bg-deep: #0a0a0a;
  --dxl-surface: #0e0e0e;
  --dxl-panel: #111111;
  --dxl-border: #1e1e1e;
  --dxl-border-hot: #444444;
  --dxl-text: #cccccc;
  --dxl-text-soft: #aaaaaa;
  --dxl-text-hint: #555555;
  --dxl-ok: #33cc66;
  --dxl-watch: #cc9900;
  --dxl-blocked: #cc3333;
  --dxl-font: "IBM Plex Mono", "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  background:
    linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px) 0 0 / 28px 28px,
    linear-gradient(0deg, rgba(255,255,255,0.018) 1px, transparent 1px) 0 0 / 28px 28px,
    var(--dxl-bg);
  color: var(--dxl-text);
  font-family: var(--dxl-font);
  letter-spacing: 0.04em;
}}
main {{
  min-height: 100vh;
  background: radial-gradient(circle at top right, rgba(255,255,255,0.055), transparent 32%), transparent;
}}
header, .topbar, .hero {{
  background: rgba(14,14,14,0.96) !important;
  border-bottom: 1px solid var(--dxl-border) !important;
  box-shadow: none !important;
}}
button, input, textarea, select {{
  font-family: var(--dxl-font);
}}
button {{
  border: 1px solid var(--dxl-border) !important;
  border-radius: 2px !important;
  background: #090909 !important;
  color: var(--dxl-text-soft) !important;
  font-size: 9px !important;
  font-weight: 700 !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
}}
button:hover {{
  border-color: var(--dxl-border-hot) !important;
  color: var(--dxl-text) !important;
}}
a {{
  color: var(--dxl-text) !important;
  text-decoration: none !important;
  border-bottom: 1px solid var(--dxl-border-hot) !important;
}}
a:hover {{
  color: var(--dxl-ok) !important;
}}
.panel {{
  border: 1px solid var(--dxl-border) !important;
  border-radius: 2px !important;
  background: linear-gradient(180deg, rgba(17,17,17,0.98), rgba(10,10,10,0.98)) !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.035) !important;
}}
.panel h2 {{
  margin: 0 0 8px !important;
  color: var(--dxl-text-hint) !important;
  font-size: 9px !important;
  font-weight: 700 !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
}}
.panel h1 {{
  margin: 0 0 10px !important;
  color: var(--dxl-text) !important;
  font-size: 14px !important;
  font-weight: 700 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
}}
.objective, .path, td, th, pre, p {{
  color: var(--dxl-text-soft) !important;
  font-family: var(--dxl-font) !important;
  font-size: 9px !important;
  line-height: 1.45 !important;
}}
pre {{
  border: 1px solid var(--dxl-border) !important;
  border-radius: 2px !important;
  background: #070707 !important;
  padding: 8px !important;
}}
table {{
  border-collapse: collapse !important;
  width: 100% !important;
}}
th, td {{
  border-top: 1px solid var(--dxl-border) !important;
  padding: 6px 8px !important;
  text-align: left !important;
  vertical-align: top !important;
}}
th {{
  color: var(--dxl-text-hint) !important;
  font-size: 8px !important;
  text-transform: uppercase !important;
}}
.metric, .timeline article, .receipt-list article, .service-console article {{
  border: 1px solid var(--dxl-border) !important;
  border-radius: 2px !important;
  background: #090909 !important;
}}
.is-ready {{
  border-left: 2px solid var(--dxl-ok) !important;
}}
.is-warning {{
  border-left: 2px solid var(--dxl-watch) !important;
}}
.is-blocked {{
  border-left: 2px solid var(--dxl-blocked) !important;
}}
.rail {{
  border-left: 1px solid var(--dxl-border) !important;
  background: rgba(5,5,5,0.74) !important;
}}
</style>
</body>
</html>"""


def build_application_dev_bridge_html() -> str:
    launcher = application_dev_launcher_url() + "/"
    catalog = "/projects/application-dev/apps.json"
    root = application_dev_root()
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Application Dev Bridge</title>
<style>
:root {{ color-scheme: dark; background: #090b0f; color: #eef2f6; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
body {{ margin: 0; min-height: 100vh; display: grid; place-items: center; background: #090b0f; }}
main {{ width: min(820px, calc(100vw - 32px)); border: 1px solid rgba(255,255,255,.14); background: #121821; padding: 22px; }}
h1 {{ margin: 0 0 10px; font-size: clamp(28px, 5vw, 52px); line-height: 1; text-transform: uppercase; }}
p {{ color: #b6c2cf; line-height: 1.55; }}
code {{ color: #d2d9e2; overflow-wrap: anywhere; }}
.actions {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-top: 18px; }}
a {{ border: 1px solid rgba(255,255,255,.16); background: rgba(255,255,255,.07); color: #eef2f6; display: grid; min-height: 58px; align-content: center; padding: 12px; text-decoration: none; text-transform: uppercase; font-weight: 800; }}
a.primary {{ background: #8bd6ff; color: #071016; border-color: #8bd6ff; }}
@media (max-width: 700px) {{ .actions {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<main>
  <h1>Application Dev Apps</h1>
  <p>This local bridge points at the Application_Dev launcher. Launching and npm install remain local to this machine through the launcher at <code>{_escape(launcher)}</code>.</p>
  <p>Root: <code>{_escape(root.as_posix())}</code></p>
  <div class="actions">
    <a class="primary" href="{_escape(launcher)}" target="_blank" rel="noreferrer">Open Launcher</a>
    <a href="{_escape(catalog)}">Catalog JSON</a>
    <a href="/cockpit#projects">Back to Projects</a>
    <a href="/cockpit">Cockpit</a>
  </div>
</main>
</body>
</html>"""


def build_helixion_development_html(model: dict[str, Any]) -> str:
    rebuild = model.get("helixion_joc_rebuild") or {}
    roles = rebuild.get("product_roles") if isinstance(rebuild.get("product_roles"), dict) else {}
    surfaces = rebuild.get("required_surfaces") if isinstance(rebuild.get("required_surfaces"), list) else []
    phases = rebuild.get("next_build_sequence") if isinstance(rebuild.get("next_build_sequence"), list) else []
    allowed = rebuild.get("allowed_v1_capabilities") if isinstance(rebuild.get("allowed_v1_capabilities"), list) else []
    forbidden = rebuild.get("forbidden_v1_capabilities") if isinstance(rebuild.get("forbidden_v1_capabilities"), list) else []
    authorities = rebuild.get("source_authorities") if isinstance(rebuild.get("source_authorities"), list) else []

    def chips(values: list[Any]) -> str:
        return "".join(f"<span>{_escape(value)}</span>" for value in values) or "<span>none</span>"

    def role_rows() -> str:
        return "".join(
            f"<article><b>{_escape(name)}</b><p>{_escape(role)}</p></article>"
            for name, role in roles.items()
        ) or "<article><b>NO ROLES</b><p>No product role projection loaded.</p></article>"

    def phase_rows() -> str:
        return "".join(
            f"<article><b>{index:02d}</b><p>{_escape(phase)}</p></article>"
            for index, phase in enumerate(phases, start=1)
        ) or "<article><b>00</b><p>No build sequence loaded.</p></article>"

    ready = "UNLOCKED" if rebuild.get("ready_for_phase_1") else "BLOCKED"
    ready_class = "ok" if rebuild.get("ready_for_phase_1") else "blocked"
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Helixion JOC Development</title>
<style>
:root {{
  --bg: #050505;
  --surface: #0e0e0e;
  --panel: #111111;
  --border: #1e1e1e;
  --hot: #444444;
  --text: #cccccc;
  --soft: #aaaaaa;
  --hint: #555555;
  --ok: #33cc66;
  --watch: #cc9900;
  --blocked: #cc3333;
  --font: "IBM Plex Mono", "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  min-height: 100vh;
  background:
    linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px) 0 0 / 28px 28px,
    linear-gradient(0deg, rgba(255,255,255,0.018) 1px, transparent 1px) 0 0 / 28px 28px,
    radial-gradient(circle at 80% 0%, rgba(255,255,255,0.065), transparent 30%),
    var(--bg);
  color: var(--text);
  font-family: var(--font);
  letter-spacing: 0.045em;
}}
.shell {{
  display: grid;
  grid-template-rows: 42px 1fr 34px;
  min-height: 100vh;
}}
.top, .bottom {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid var(--border);
  background: rgba(14,14,14,0.96);
  padding: 0 12px;
}}
.bottom {{
  border-top: 1px solid var(--border);
  border-bottom: 0;
  color: var(--hint);
  font-size: 8px;
  text-transform: uppercase;
}}
.brand {{
  color: var(--text);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.16em;
}}
.state {{
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--soft);
  font-size: 8px;
  font-weight: 700;
  text-transform: uppercase;
}}
.dot {{
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--ok);
  box-shadow: 0 0 12px rgba(51,204,102,0.45);
}}
.dot.blocked {{
  background: var(--blocked);
  box-shadow: 0 0 12px rgba(204,51,51,0.45);
}}
.grid {{
  display: grid;
  grid-template-columns: 52px minmax(0, 1fr) 360px;
  min-height: 0;
}}
.rail {{
  border-right: 1px solid var(--border);
  background: rgba(5,5,5,0.82);
  padding: 10px 6px;
}}
.rail span {{
  display: block;
  border: 1px solid var(--border);
  color: var(--hint);
  font-size: 8px;
  font-weight: 800;
  margin-bottom: 6px;
  padding: 7px 0;
  text-align: center;
}}
.main {{
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(0, 0.75fr);
  gap: 10px;
  padding: 10px;
  overflow: auto;
}}
.inspector {{
  border-left: 1px solid var(--border);
  padding: 10px;
  overflow: auto;
  background: rgba(5,5,5,0.62);
}}
.panel {{
  border: 1px solid var(--border);
  border-radius: 2px;
  background: linear-gradient(180deg, rgba(17,17,17,0.98), rgba(8,8,8,0.98));
  margin-bottom: 10px;
  padding: 10px;
}}
.panel h1, .panel h2, .panel h3 {{
  margin: 0;
  text-transform: uppercase;
}}
.panel h1 {{
  color: var(--text);
  font-size: 16px;
  line-height: 1.25;
  letter-spacing: 0.08em;
}}
.panel h2 {{
  color: var(--hint);
  font-size: 9px;
  letter-spacing: 0.16em;
  margin-bottom: 8px;
}}
.panel h3 {{
  color: var(--soft);
  font-size: 10px;
  letter-spacing: 0.12em;
  margin-bottom: 8px;
}}
p, code, pre {{
  color: var(--soft);
  font-family: var(--font);
  font-size: 9px;
  line-height: 1.5;
}}
pre {{
  border: 1px solid var(--border);
  background: #070707;
  overflow: auto;
  padding: 8px;
  white-space: pre-wrap;
}}
.verdict {{
  display: inline-block;
  border: 1px solid var(--hot);
  color: var(--ok);
  font-size: 9px;
  font-weight: 800;
  margin-bottom: 8px;
  padding: 5px 8px;
  text-transform: uppercase;
}}
.verdict.blocked {{
  color: var(--blocked);
}}
.cards {{
  display: grid;
  gap: 6px;
}}
.cards article {{
  border: 1px solid var(--border);
  background: #090909;
  padding: 8px;
}}
.cards b {{
  color: var(--text);
  display: block;
  font-size: 9px;
  margin-bottom: 4px;
  text-transform: uppercase;
}}
.chips {{
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}}
.chips span {{
  border: 1px solid var(--border);
  background: #090909;
  color: var(--soft);
  font-size: 8px;
  font-weight: 700;
  padding: 5px 6px;
  text-transform: uppercase;
}}
a {{
  color: var(--text);
  text-decoration: none;
  border-bottom: 1px solid var(--hot);
}}
a:hover {{ color: var(--ok); }}
</style>
</head>
<body>
<main class="shell">
  <header class="top">
    <div class="brand">HELIXION / JOC DEVELOPMENT</div>
    <div class="state"><span class="dot {ready_class}"></span><span>PHASE 1: {ready}</span><span>{_escape(rebuild.get("status", "not_documented"))}</span></div>
  </header>
  <section class="grid">
    <aside class="rail"><span>JOC</span><span>ION</span><span>dAI</span><span>CODEX</span><span>WNET</span></aside>
    <section class="main">
      <div>
        <article class="panel">
          <h2>MASTER REBUILD DECISION</h2>
          <div class="verdict {ready_class}">{_escape(rebuild.get("status", "not_documented"))}</div>
          <h1>{_escape(rebuild.get("decision", "No Helixion rebuild decision loaded."))}</h1>
          <p>This URL is a visibility cockpit for the Helixion/JOC rebuild. It does not grant new production, browser-control, credential, purchase, destructive, or silent-send authority.</p>
        </article>
        <article class="panel">
          <h2>PRODUCT ROLES</h2>
          <div class="cards">{role_rows()}</div>
        </article>
        <article class="panel">
          <h2>BUILD SEQUENCE</h2>
          <div class="cards">{phase_rows()}</div>
        </article>
      </div>
      <div>
        <article class="panel">
          <h2>REQUIRED SURFACES</h2>
          <div class="chips">{chips(surfaces)}</div>
        </article>
        <article class="panel">
          <h2>ALLOWED V1</h2>
          <div class="chips">{chips(allowed)}</div>
        </article>
        <article class="panel">
          <h2>FORBIDDEN V1</h2>
          <div class="chips">{chips(forbidden)}</div>
        </article>
      </div>
    </section>
    <aside class="inspector">
      <article class="panel">
        <h2>URLS</h2>
        <p><a href="/cockpit">/cockpit</a></p>
        <p><a href="/joc/evolution">/joc/evolution</a></p>
        <p><a href="/helixion/development">/helixion/development</a></p>
        <p><a href="/model.json">/model.json</a></p>
      </article>
      <article class="panel">
        <h2>SOURCE AUTHORITIES</h2>
        <pre>{_escape(json.dumps(authorities, indent=2, sort_keys=True))}</pre>
      </article>
      <article class="panel">
        <h2>PLAN PATHS</h2>
        <pre>{_escape(json.dumps({
            "master_plan": rebuild.get("master_plan_path"),
            "registry": rebuild.get("registry_path"),
            "current_plan": rebuild.get("current_plan_path"),
        }, indent=2, sort_keys=True))}</pre>
      </article>
    </aside>
  </section>
  <footer class="bottom"><span>LOCAL JOC VISIBILITY SURFACE</span><span>NO NEW RUNTIME AUTHORITY</span></footer>
</main>
</body>
</html>"""


def make_handler(root: Path) -> type[BaseHTTPRequestHandler]:
    class IonCockpitHandler(BaseHTTPRequestHandler):
        server_version = "IONLocalCockpit/0.1"

        def log_message(self, fmt: str, *args: Any) -> None:
            return

        def _send_bytes(self, status: int, body: bytes, content_type: str, *, csp: str | None = None) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", csp or LEGACY_CSP)
            self.end_headers()
            self.wfile.write(body)

        def _send_react_static(self, request_path: str) -> None:
            target = resolve_react_static_asset(root, request_path)
            if target is None:
                self._send_json(404, {"ok": False, "finding": "react_static_not_found", "path": request_path})
                return
            content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            self._send_bytes(200, target.read_bytes(), content_type, csp=REACT_CSP)

        def _send_application_dev_launcher_catalog(self) -> None:
            target = application_dev_launcher_url() + "/apps.json"
            try:
                request = urllib.request.Request(
                    target,
                    headers={
                        "Accept": "application/json",
                        "Accept-Encoding": "identity",
                        "User-Agent": "IonLocalCockpitApplicationDevCatalog/0.1",
                    },
                )
                with urllib.request.urlopen(request, timeout=8) as response:
                    body = response.read()
                    self._send_bytes(
                        int(getattr(response, "status", 200) or 200),
                        body,
                        response.headers.get("content-type") or "application/json",
                    )
                    return
            except Exception as exc:
                self._send_json(
                    503,
                    {
                        "ok": False,
                        "error": "application_dev_launcher_offline",
                        "finding": exc.__class__.__name__,
                        "launcher": application_dev_launcher_url() + "/",
                        "root": application_dev_root().as_posix(),
                        "production_authority": False,
                        "live_execution_authority": False,
                    },
                )

        def _send_json(self, status: int, payload: dict[str, Any]) -> None:
            self._send_bytes(status, json.dumps(payload, indent=2, sort_keys=True).encode("utf-8"), "application/json")

        def _redirect(self, target: str) -> None:
            self.send_response(303)
            self.send_header("Location", target)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()

        def _read_payload(self) -> dict[str, Any]:
            length = int(self.headers.get("content-length") or "0")
            raw = self.rfile.read(length)
            content_type = (self.headers.get("content-type") or "").split(";", 1)[0].strip().lower()
            if content_type == "application/json":
                return json.loads(raw.decode("utf-8") or "{}")
            parsed = parse_qs(raw.decode("utf-8"), keep_blank_values=True)
            return {key: values[-1] if values else "" for key, values in parsed.items()}

        def _wants_json(self) -> bool:
            accept = self.headers.get("accept") or ""
            content_type = self.headers.get("content-type") or ""
            return "application/json" in accept or content_type.startswith("application/json")

        def do_GET(self) -> None:  # noqa: N802
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            if path.startswith("/joc-static/"):
                self._send_react_static(path)
                return
            if path in {"/projects/portfolio.json", "/projects/surface.json", "/cockpit/projects/portfolio.json"}:
                self._send_json(200, build_helixion_projects_surface_model_from_file(root))
                return
            if path in {"/projects/application-dev/apps.json", "/projects/appdev/apps.json"}:
                self._send_application_dev_launcher_catalog()
                return
            if path in {"/projects/application-dev", "/projects/application-dev/"}:
                self._send_bytes(200, build_application_dev_bridge_html().encode("utf-8"), "text/html; charset=utf-8", csp=REACT_CSP)
                return
            if path == "/health":
                self._send_json(200, build_cockpit_health(root))
                return
            if path in {"/model.json", "/cockpit/model.json"}:
                self._send_json(200, build_cockpit_view_model(root))
                return
            if path in {"/cockpit/previews/model.json", "/cockpit/projects/previews/model.json"}:
                self._send_json(200, build_project_preview_sessions_model(root))
                return
            if path == "/cockpit/build/workspace.json":
                query = parse_qs(parsed_url.query)
                project_id = str((query.get("project_id") or ["ion_dev"])[-1] or "ion_dev")
                probe_preview = str((query.get("probe_preview") or [""])[-1]).lower() in {"1", "true", "yes"}
                max_items = _payload_int({"max_items": (query.get("max_items") or ["8"])[-1]}, "max_items", 8)
                self._send_json(
                    200,
                    build_build_workspace_model(root, project_id=project_id, probe_preview=probe_preview, max_items=max_items),
                )
                return
            if path in {
                "/cockpit/codex/model.json",
                "/cockpit/browser-gpt/model.json",
                "/cockpit/projects/model.json",
                "/cockpit/apps/model.json",
                "/cockpit/build/model.json",
                "/cockpit/weave/model.json",
                "/cockpit/domain-weave/model.json",
            }:
                surface = (
                    "browser-gpt"
                    if path.startswith("/cockpit/browser-gpt/")
                    else "projects"
                    if path.startswith(("/cockpit/projects/", "/cockpit/apps/"))
                    else "build"
                    if path.startswith("/cockpit/build/")
                    else "weave"
                    if path.startswith(("/cockpit/weave/", "/cockpit/domain-weave/"))
                    else "codex"
                )
                self._send_json(200, build_cockpit_surface_view_model(root, surface=surface))
                return
            if path == "/cockpit/ide/model.json":
                self._send_json(200, build_codex_ide_workbench_model(root))
                return
            if path in {"/system/model.json", "/cockpit/system/model.json"}:
                self._send_json(200, build_system_diagnostics_model(root))
                return
            if path in {"/chat/model.json", "/cockpit/chat/model.json"}:
                self._send_json(200, build_dual_codex_chat_model(root))
                return
            if path in {"/chat/archive.json", "/cockpit/chat/archive.json"}:
                query = parse_qs(parsed_url.query)
                window_start = str((query.get("start") or query.get("window_start") or [""])[-1] or "")
                window_count = str((query.get("count") or query.get("window_count") or [""])[-1] or "")
                self._send_json(
                    200,
                    build_codex_conversation_archive(
                        root,
                        selected_session_id=str((query.get("session_id") or [""])[-1] or "") or None,
                        query=str((query.get("q") or [""])[-1] or "") or None,
                        selected_window_start=int(window_start) if window_start.isdigit() else None,
                        selected_window_count=int(window_count) if window_count.isdigit() else 500,
                    ),
                )
                return
            if path in {"/chat/diffs.json", "/cockpit/chat/diffs.json", "/cockpit/git/rollback/model.json"}:
                query = parse_qs(parsed_url.query)
                self._send_json(
                    200,
                    build_codex_git_rollback_model(
                        root,
                        selected_session_id=str((query.get("session_id") or [""])[-1] or "") or None,
                    ),
                )
                return
            if path in {"/chat/context_timeline.json", "/cockpit/chat/context_timeline.json", "/cockpit/context/timeline.json"}:
                query = parse_qs(parsed_url.query)
                limit = str((query.get("limit") or [""])[-1] or "")
                self._send_json(
                    200,
                    build_codex_context_timeline_model(
                        root,
                        history_limit=int(limit) if limit.isdigit() else 36,
                    ),
                )
                return
            if path in {"/cockpit/chat", "/cockpit/chat/"}:
                react_html = build_react_cockpit_html(root)
                if react_html:
                    self._send_bytes(200, react_html.encode("utf-8"), "text/html; charset=utf-8", csp=REACT_CSP)
                    return
                model = build_dual_codex_chat_model(root, write=True)
                self._send_bytes(
                    200,
                    render_dual_codex_chat_html(model, base_path="/cockpit/chat").encode("utf-8"),
                    "text/html; charset=utf-8",
                )
                return
            if path.startswith("/cockpit/projects/launch/open/"):
                launch_id = unquote(path.rsplit("/", 1)[-1])
                query = parse_qs(parsed_url.query)
                stop_token = str((query.get("stop_token") or [""])[-1] or "")
                html_text = build_project_launcher_open_html(root, launch_id, stop_token=stop_token)
                self._send_bytes(
                    200,
                    html_text.encode("utf-8"),
                    "text/html; charset=utf-8",
                    csp=PROJECT_LAUNCH_CSP,
                )
                return
            if path.startswith("/cockpit/projects/launch/proxy/"):
                rest = path.removeprefix("/cockpit/projects/launch/proxy/")
                launch_id, _, proxy_path = rest.partition("/")
                result = project_launcher_proxy_fetch(
                    root,
                    unquote(launch_id),
                    unquote(proxy_path),
                    query=parsed_url.query,
                    method="GET",
                    headers={key: value for key, value in self.headers.items()},
                )
                self._send_bytes(
                    int(result.get("status") or 502),
                    result.get("body") if isinstance(result.get("body"), bytes) else b"",
                    str(result.get("content_type") or "application/octet-stream"),
                )
                return
            if path.startswith("/cockpit/projects/launch/screenshot/"):
                screenshot = project_launcher_screenshot_file(root, unquote(path.rsplit("/", 1)[-1]))
                if screenshot is None:
                    self._send_json(404, {"ok": False, "finding": "project_launch_screenshot_not_found"})
                    return
                self._send_bytes(200, screenshot.read_bytes(), "image/png")
                return
            if path in {"/chat", "/chat/"}:
                model = build_dual_codex_chat_model(root, write=True)
                self._send_bytes(200, render_dual_codex_chat_html(model).encode("utf-8"), "text/html; charset=utf-8")
                return
            if path in {"/cockpit/scope", "/cockpit/scope/"}:
                query = parse_qs(parsed_url.query)
                model = build_scope_cockpit_model(root, thread_id=(query.get("thread_id") or [""])[0] or None)
                self._send_bytes(200, render_scope_cockpit_html(model).encode("utf-8"), "text/html; charset=utf-8")
                return
            if path == "/cockpit/scope/model.json":
                query = parse_qs(parsed_url.query)
                model = build_scope_cockpit_model(root, thread_id=(query.get("thread_id") or [""])[0] or None)
                self._send_json(200, model)
                return
            if path == "/cockpit/legacy":
                model = build_cockpit_view_model(root)
                self._send_bytes(200, build_cockpit_html(model).encode("utf-8"), "text/html; charset=utf-8")
                return
            if path in {"/", "/app", "/cockpit", "/cockpit/apps", "/cockpit/agents", "/agents", "/projects", "/projects/", "/joc/evolution", "/helixion/development", "/development"}:
                react_html = build_react_cockpit_html(root)
                if react_html:
                    self._send_bytes(200, react_html.encode("utf-8"), "text/html; charset=utf-8", csp=REACT_CSP)
                    return
                model = build_cockpit_view_model(root)
                self._send_bytes(200, build_cockpit_html(model).encode("utf-8"), "text/html; charset=utf-8")
                return
            self._send_json(404, {"ok": False, "finding": "not_found", "path": path})

        def do_POST(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path == "/cockpit/projects/launch/diagnostics/event":
                payload = self._read_payload()
                try:
                    result = app_diagnostics_record_browser_event(root, payload)
                except Exception as exc:
                    result = {"ok": False, "finding": "app_diagnostics_event_failed", "error": exc.__class__.__name__}
                self._send_json(200 if result.get("ok") else 409, result)
                return
            if path.startswith("/cockpit/projects/launch/proxy/"):
                parsed = urlparse(self.path)
                rest = parsed.path.removeprefix("/cockpit/projects/launch/proxy/")
                launch_id, _, proxy_path = rest.partition("/")
                result = project_launcher_proxy_fetch(
                    root,
                    unquote(launch_id),
                    unquote(proxy_path),
                    query=parsed.query,
                    method="POST",
                    body=json.dumps(self._read_payload()).encode("utf-8"),
                    headers={key: value for key, value in self.headers.items()},
                )
                self._send_bytes(
                    int(result.get("status") or 502),
                    result.get("body") if isinstance(result.get("body"), bytes) else b"",
                    str(result.get("content_type") or "application/octet-stream"),
                )
                return
            if path in {"/cockpit/projects/launch/diagnostics/config", "/cockpit/projects/launch/diagnostics/timeline", "/cockpit/projects/launch/diagnostics/snapshot", "/cockpit/projects/launch/diagnostics/matrix"}:
                payload = self._read_payload()
                try:
                    if path.endswith("/config"):
                        result = app_diagnostics_config_update(root, payload)
                    elif path.endswith("/snapshot"):
                        result = app_diagnostics_snapshot(root, payload)
                    elif path.endswith("/matrix"):
                        result = project_launcher_diagnostics_matrix(root, payload)
                    else:
                        result = app_diagnostics_timeline_model(root, payload)
                except Exception as exc:
                    result = {"ok": False, "finding": "app_diagnostics_action_failed", "error": exc.__class__.__name__}
                self._send_json(200 if result.get("ok") else 409, result)
                return
            if path in {"/cockpit/projects/launch/start", "/cockpit/projects/launch/status", "/cockpit/projects/launch/stop", "/cockpit/projects/launch/diagnostics"}:
                payload = self._read_payload()
                try:
                    if path == "/cockpit/projects/launch/start":
                        result = project_launcher_start(root, payload)
                    elif path == "/cockpit/projects/launch/status":
                        result = project_launcher_status(root, payload)
                    elif path == "/cockpit/projects/launch/diagnostics":
                        result = project_launcher_diagnostics(root, payload)
                    else:
                        result = project_launcher_stop(root, payload)
                except Exception as exc:
                    result = {"ok": False, "finding": "project_launch_action_failed", "error": exc.__class__.__name__}
                try:
                    app_diagnostics_record_http_event(root, route=path, payload=payload, result=result, source="local_cockpit_app")
                except Exception:
                    pass
                self._send_json(200 if result.get("ok") else 409, result)
                return
            if path == "/cockpit/projects/organizer/materialize":
                try:
                    result = materialize_project_portfolio_action(root, self._read_payload())
                except Exception as exc:
                    result = {"ok": False, "finding": "project_portfolio_materialize_failed", "error": exc.__class__.__name__}
                self._send_json(200 if result.get("ok") else 409, result)
                return
            project_actions = {
                "/cockpit/projects/blocker/create": ("blocker", "create"),
                "/cockpit/projects/blocker/update": ("blocker", "update"),
                "/cockpit/projects/blocker/resolve": ("blocker", "resolve"),
                "/cockpit/projects/question/create": ("question", "create"),
                "/cockpit/projects/question/update": ("question", "update"),
                "/cockpit/projects/question/resolve": ("question", "resolve"),
            }
            if path in project_actions:
                record_type, action = project_actions[path]
                try:
                    result = apply_project_cockpit_action(
                        root,
                        record_type=record_type,
                        action=action,
                        payload=self._read_payload(),
                    )
                except Exception as exc:
                    result = {"ok": False, "finding": "request_failed", "error": exc.__class__.__name__}
                self._send_json(200 if result.get("ok") else 400, result)
                return
            if path in {
                "/cockpit/agents/prepare",
                "/cockpit/agents/start",
                "/cockpit/agents/cancel",
                "/cockpit/agents/result",
                "/cockpit/agents/status",
                "/cockpit/agents/swarm-step",
                "/cockpit/agents/relay/create",
                "/cockpit/agents/relay/pending",
                "/cockpit/agents/relay/respond",
                "/cockpit/agents/settle",
                "/cockpit/agents/receipts",
                "/cockpit/agents/spawn-template",
                "/cockpit/agents/comms/send",
                "/cockpit/agents/comms/ack",
                "/cockpit/agents/comms/list",
                "/cockpit/agents/comms/thread",
                "/cockpit/agents/comms/branch",
                "/cockpit/agents/comms/run/start",
                "/cockpit/agents/comms/run/pickup",
                "/cockpit/agents/comms/run/continue",
                "/cockpit/agents/comms/run/start-worker",
                "/cockpit/agents/comms/run/audit",
                "/cockpit/agents/dispatcher/route",
                "/cockpit/agents/dispatcher/tick",
                "/cockpit/agents/dispatcher/runner",
                "/cockpit/agents/dispatcher/pause",
            }:
                try:
                    payload = self._read_payload()
                    if path in {"/cockpit/agents/prepare", "/cockpit/agents/start"}:
                        start = path.endswith("/start")
                        result = invoke_agent(
                            root,
                            agent=str(payload.get("agent") or payload.get("agent_id") or payload.get("role_id") or ""),
                            objective=str(payload.get("objective") or ""),
                            mode=str(payload.get("mode") or ("direct_codex" if start else "prepare_only")),
                            queue=bool(payload.get("queue") or start),
                            start=start,
                            context_refs=_payload_list(payload, "context_refs"),
                            timeout_seconds=_payload_int(payload, "timeout_seconds", 1800),
                            work_class=str(payload.get("work_class") or "agent_invocation"),
                            risk_level=str(payload.get("risk_level") or "medium"),
                            route_family=str(payload.get("route_family") or "agent_invocation"),
                            requested_model=str(payload.get("requested_model") or "") or None,
                            requested_reasoning_effort=str(payload.get("requested_reasoning_effort") or "") or None,
                            model_override_reason=str(payload.get("model_override_reason") or "") or None,
                            idempotency_key=str(payload.get("idempotency_key") or "") or None,
                            target_root_id=str(payload.get("target_root_id") or "active_ion_control"),
                            movement_class=str(payload.get("movement_class") or "ION_KERNEL_CONTROL_MOVEMENT"),
                            target_project_subpath=str(payload.get("target_project_subpath") or "") or None,
                            planned_writes=_payload_list(payload, "planned_writes"),
                            planned_artifacts=_payload_list(payload, "planned_artifacts"),
                            domain_id=str(payload.get("domain_id") or "") or None,
                            use_codex_mount=payload.get("use_codex_mount") is not False,
                        )
                    elif path == "/cockpit/agents/cancel":
                        result = control_agent_invocation(
                            root,
                            {"operation": "cancel", "invocation_id": str(payload.get("invocation_id") or "")},
                        )
                    elif path == "/cockpit/agents/result":
                        result = agent_result(root, invocation_id=str(payload.get("invocation_id") or "") or None)
                    elif path == "/cockpit/agents/swarm-step":
                        result = swarm_step_once(
                            root,
                            start=bool(payload.get("start")),
                            request_path=str(payload.get("request_path") or "") or None,
                            timeout_seconds=_payload_int(payload, "timeout_seconds", 1800),
                        )
                    elif path == "/cockpit/agents/relay/create":
                        result = create_agent_relay_message(root, payload)
                    elif path == "/cockpit/agents/relay/pending":
                        result = pending_agent_relays(
                            root,
                            invocation_id=str(payload.get("invocation_id") or "") or None,
                            include_answered=bool(payload.get("include_answered")),
                        )
                    elif path == "/cockpit/agents/relay/respond":
                        result = respond_agent_relay(root, payload)
                    elif path == "/cockpit/agents/settle":
                        result = settle_agent_invocation(root, payload)
                    elif path == "/cockpit/agents/receipts":
                        result = recent_agent_invocation_receipts(root, limit=_payload_int(payload, "limit", 20))
                    elif path == "/cockpit/agents/spawn-template":
                        result = execute_agent_spawn_template(root, payload)
                    elif path == "/cockpit/agents/comms/send":
                        result = send_agent_message(root, payload)
                    elif path == "/cockpit/agents/comms/ack":
                        result = ack_agent_message(root, payload)
                    elif path == "/cockpit/agents/comms/list":
                        result = list_agent_threads(
                            root,
                            role_id=str(payload.get("role_id") or "") or None,
                            channel_id=str(payload.get("channel_id") or "") or None,
                            limit=_payload_int(payload, "limit", 50),
                        )
                    elif path == "/cockpit/agents/comms/thread":
                        result = read_agent_thread(
                            root,
                            str(payload.get("thread_id") or ""),
                            role_id=str(payload.get("role_id") or "") or None,
                            limit=_payload_int(payload, "limit", 200),
                        )
                    elif path == "/cockpit/agents/comms/branch":
                        result = create_agent_message_branch(root, payload)
                    elif path == "/cockpit/agents/comms/run/start":
                        result = maybe_audit_agent_comms_result(root, payload, start_agent_comms_run(root, payload))
                    elif path == "/cockpit/agents/comms/run/pickup":
                        result = maybe_audit_agent_comms_result(root, payload, pickup_agent_comms_run(root, payload))
                    elif path == "/cockpit/agents/comms/run/continue":
                        result = maybe_audit_agent_comms_result(root, payload, continue_agent_comms_run(root, payload))
                    elif path == "/cockpit/agents/comms/run/start-worker":
                        result = maybe_audit_agent_comms_result(root, payload, start_agent_comms_run_worker(root, payload))
                    elif path == "/cockpit/agents/comms/run/audit":
                        result = audit_agent_comms_run(root, payload)
                    elif path == "/cockpit/agents/dispatcher/route":
                        result = route_steward_dispatcher(root, payload)
                    elif path == "/cockpit/agents/dispatcher/tick":
                        result = tick_steward_dispatcher(root, payload)
                    elif path == "/cockpit/agents/dispatcher/runner":
                        result = run_steward_dispatcher_runner(root, payload)
                    elif path == "/cockpit/agents/dispatcher/pause":
                        result = pause_steward_dispatcher(root, payload)
                    else:
                        result = build_bounded_agent_status(
                            root,
                            invocation_id=str(payload.get("invocation_id") or "") or None,
                        )
                except Exception as exc:
                    result = {"ok": False, "finding": "request_failed", "error": exc.__class__.__name__}
                self._send_json(200 if result.get("ok") else 409, result)
                return
            if path in {"/cockpit/automations/run"}:
                try:
                    result = execute_automation_action(root, self._read_payload())
                except Exception as exc:
                    result = {"ok": False, "finding": "request_failed", "error": exc.__class__.__name__}
                self._send_json(200 if result.get("ok") else 409, result)
                return
            if path in {"/cockpit/domain-weaver/action", "/cockpit/weave/action"}:
                try:
                    result = execute_domain_weaver_action(root, self._read_payload())
                except Exception as exc:
                    result = {"ok": False, "finding": "request_failed", "error": exc.__class__.__name__}
                self._send_json(200 if result.get("ok") else 409, result)
                return
            if path in {"/cockpit/scope/model"}:
                try:
                    payload = self._read_payload()
                    result = build_scope_cockpit_model(root, thread_id=str(payload.get("thread_id") or "") or None)
                except Exception as exc:
                    result = {"ok": False, "finding": "scope_cockpit_model_failed", "error": exc.__class__.__name__}
                self._send_json(200 if result.get("ok") else 409, result)
                return
            if path in {"/services/restart", "/cockpit/services/restart"}:
                result = restart_service(root, self._read_payload())
                if self._wants_json():
                    self._send_json(200 if result.get("ok") else 409, result)
                    return
                self._redirect("/cockpit")
                return
            if path in {"/system/preview_action", "/cockpit/system/preview_action"}:
                try:
                    payload = self._read_payload()
                    result = preview_system_diagnostic_action(root, payload.get("action") if isinstance(payload.get("action"), dict) else payload)
                except Exception as exc:
                    result = {"ok": False, "finding": "request_failed", "error": str(exc)}
                    self._send_json(400, result)
                    return
                self._send_json(200, {"ok": True, **result})
                return
            if path in {"/system/execute_action", "/cockpit/system/execute_action"}:
                try:
                    payload = self._read_payload()
                    result = execute_system_diagnostic_action(root, payload.get("action") if isinstance(payload.get("action"), dict) else payload)
                except Exception as exc:
                    result = {"ok": False, "finding": "request_failed", "error": str(exc)}
                    self._send_json(409, result)
                    return
                self._send_json(200, {"ok": True, **result})
                return
            if path in {"/chat/archive/attach", "/cockpit/chat/archive/attach"}:
                payload = self._read_payload()
                result = attach_codex_conversation_to_chat(
                    root,
                    session_id=str(payload.get("session_id") or ""),
                    confirmation=str(payload.get("confirmation") or ""),
                    prompt=str(payload.get("prompt") or "") or None,
                )
                self._send_json(200 if result.get("ok") else 400, result)
                return
            if path in {"/action-branch/invoke", "/cockpit/action-branch/invoke"}:
                from .ion_action_mcp_branch_leaders import action_branch_invoke

                payload = self._read_payload()
                route_args = payload.get("args") if isinstance(payload.get("args"), dict) else {}
                approval = payload.get("approval") if isinstance(payload.get("approval"), dict) else None
                result = action_branch_invoke(
                    root,
                    branch_id=str(payload.get("branch_id") or ""),
                    route_id=str(payload.get("route_id") or ""),
                    args=route_args,
                    idempotency_key=str(payload.get("idempotency_key") or "").strip() or None,
                    confirmation=str(payload.get("confirmation") or "").strip() or None,
                    approval=approval,
                    expected_route_schema_version=str(payload.get("expected_route_schema_version") or "v0").strip() or None,
                )
                self._send_json(200 if result.get("ok") else 400, result)
                return
            if path in {"/chat/branch", "/cockpit/chat/branch"}:
                payload = self._read_payload()
                result = create_chat_branch(
                    root,
                    confirmation=str(payload.get("confirmation") or ""),
                    lane_id=str(payload.get("lane_id") or "codex_general"),
                    parent_kind=str(payload.get("parent_kind") or ""),
                    title=str(payload.get("title") or ""),
                    objective=str(payload.get("objective") or ""),
                    prompt=str(payload.get("prompt") or ""),
                    parent_turn_id=str(payload.get("parent_turn_id") or ""),
                    parent_session_id=str(payload.get("parent_session_id") or ""),
                    parent_role=str(payload.get("parent_role") or ""),
                    parent_message=str(payload.get("parent_message") or ""),
                    parent_message_sha256=str(payload.get("parent_message_sha256") or ""),
                )
                self._send_json(200 if result.get("ok") else 400, result)
                return
            if path in {
                "/chat/agent/stop",
                "/cockpit/chat/agent/stop",
            }:
                payload = self._read_payload()
                result = stop_active_codex_queue_runner(
                    root,
                    confirmation=str(payload.get("confirmation") or ""),
                    reason=str(payload.get("reason") or "operator_stop_from_chat"),
                )
                self._send_json(200 if result.get("ok") else 409, result)
                return
            if path in {
                "/chat/git/rollback/capture",
                "/cockpit/chat/git/rollback/capture",
                "/cockpit/git/rollback/capture",
            }:
                result = capture_codex_diff_checkpoint(root, self._read_payload())
                self._send_json(200 if result.get("ok") else 409, result)
                return
            if path in {
                "/chat/git/rollback/preview",
                "/cockpit/chat/git/rollback/preview",
                "/cockpit/git/rollback/preview",
            }:
                result = preview_codex_git_rollback(root, self._read_payload())
                self._send_json(200 if result.get("ok") else 409, result)
                return
            if path in {
                "/chat/git/rollback/apply",
                "/cockpit/chat/git/rollback/apply",
                "/cockpit/git/rollback/apply",
            }:
                result = apply_codex_git_rollback(root, self._read_payload())
                self._send_json(200 if result.get("ok") else 409, result)
                return
            if path in {"/chat/file-tree", "/cockpit/chat/file-tree"}:
                payload = self._read_payload()
                result = call_chatgpt_connector_tool(
                    root,
                    "ion_tree_list",
                    {
                        "path": str(payload.get("path") or "ION"),
                        "max_depth": _payload_int(payload, "max_depth", 3),
                        "limit": _payload_int(payload, "limit", 700),
                    },
                )
                self._send_json(200 if result.get("ok") else 400, result)
                return
            if path not in {
                "/chat/turn",
                "/chat/queue",
                "/chat/memory",
                "/cockpit/chat/turn",
                "/cockpit/chat/queue",
                "/cockpit/chat/memory",
            }:
                self._send_json(404, {"ok": False, "finding": "not_found", "path": path})
                return
            try:
                payload = self._read_payload()
                if path in {"/chat/turn", "/cockpit/chat/turn"}:
                    result = record_chat_turn(
                        root,
                        lane_id=str(payload.get("lane_id") or ""),
                        message=str(payload.get("message") or ""),
                        author=str(payload.get("author") or "operator"),
                        execution_mode=str(payload.get("execution_mode") or ""),
                        agent_mode=str(payload.get("agent_mode") or ""),
                        codex_model_override=resolve_chat_model_override(
                            payload.get("codex_model_override"),
                            selected_model=payload.get("selected_model"),
                            thinking_mode=payload.get("thinking_mode"),
                        ),
                        raw_codex_cli_enabled=True,
                        client_id=str(payload.get("client_id") or ""),
                        target_session_id=str(payload.get("target_session_id") or ""),
                        new_codex_session=payload.get("new_codex_session") is True,
                        codex_session_transport=str(payload.get("codex_session_transport") or ""),
                        context_refs=_payload_list(payload, "context_refs"),
                        ide_context_bridge=_payload_mapping(payload, "ide_context_bridge"),
                    )
                elif path in {"/chat/queue", "/cockpit/chat/queue"}:
                    result = queue_chat_codex_work_packet(
                        root,
                        lane_id=str(payload.get("lane_id") or ""),
                        objective=str(payload.get("objective") or ""),
                        confirmation=str(payload.get("confirmation") or ""),
                        context_refs=_payload_list(payload, "context_refs"),
                    )
                else:
                    result = pin_dual_chat_memory(
                        root,
                        lane_id=str(payload.get("lane_id") or ""),
                        text=str(payload.get("text") or ""),
                        source_turn_id=str(payload.get("source_turn_id") or "") or None,
                        confirmation=str(payload.get("confirmation") or WRITE_CONFIRMATION_TOKEN),
                    )
            except Exception as exc:
                result = {"ok": False, "finding": "request_failed", "error": exc.__class__.__name__}
            if self._wants_json():
                self._send_json(200 if result.get("ok") else 400, result)
                return
            self._redirect("/cockpit/chat" if path.startswith("/cockpit/chat") else "/chat")

    return IonCockpitHandler


def run_server(root: str | Path = ".", *, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    shell_root = Path(root).expanduser().resolve()
    server = ThreadingHTTPServer((host, port), make_handler(shell_root))
    print(f"ION local cockpit listening on http://{host}:{port}", flush=True)
    server.serve_forever()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Serve the local-only ION cockpit app.")
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--health", action="store_true")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.serve:
        run_server(args.ion_root, host=args.host, port=args.port)
        return 0
    if args.html:
        print(build_cockpit_html(build_cockpit_view_model(args.ion_root)))
        return 0
    result = build_cockpit_health(args.ion_root)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json or args.health else result["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
