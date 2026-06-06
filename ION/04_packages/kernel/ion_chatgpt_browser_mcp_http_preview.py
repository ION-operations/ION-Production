"""V121 local HTTP MCP preview for the ChatGPT browser connector.

This is a local preview harness for the V120 ChatGPT-browser connector
contract. It handles a small JSON-RPC MCP subset over HTTP-shaped payloads, but
it is not a public hosted connector and does not claim deployment authority.
"""
from __future__ import annotations

import argparse
import html
import json
import mimetypes
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import parse_qs, unquote, urlencode, urlparse
import urllib.error
import urllib.request

from .ion_chatgpt_browser_mcp_connector_contract import (
    BOUNDED_QUEUE_RECEIPT_TOOLS,
    FORBIDDEN_CAPABILITIES,
    STATUS_READ_TOOLS,
    audit_chatgpt_browser_mcp_connector_contract,
    call_chatgpt_connector_tool,
)
from .ion_agent_comms import ack_agent_message, create_agent_message_branch, list_agent_threads, read_agent_thread, send_agent_message
from .ion_agent_comms_runs import continue_agent_comms_run, pickup_agent_comms_run, start_agent_comms_run, start_agent_comms_run_worker
from .ion_agent_comms_audit_actions import audit_agent_comms_run, maybe_audit_agent_comms_result
from .ion_agent_spawn_templates import execute_agent_spawn_template
from .ion_steward_dispatcher import pause_steward_dispatcher, route_steward_dispatcher, run_steward_dispatcher_runner, tick_steward_dispatcher
from .ion_cockpit_view_model import (
    build_cockpit_view_model,
    build_cockpit_surface_view_model,
    build_worker_cockpit_view_model,
)
from .ion_browser_gpt_dom_calibration import record_browser_gpt_dom_probe_snapshot
from .ion_browser_gpt_screen_automation import (
    build_screen_automation_status,
    execute_extension_reload,
    execute_tab_refresh,
    learn_screen_automation_state,
)
from .ion_automation_control_plane import execute_automation_action
from .ion_build_workspace_model import build_build_workspace_model
from .ion_cockpit_service_manager import restart_service
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
from .ion_dual_codex_chat import (
    WRITE_CONFIRMATION_TOKEN,
    build_dual_codex_chat_model,
    create_chat_branch,
    create_fresh_agent_capsule_chat,
    pin_dual_chat_memory,
    queue_chat_codex_work_packet,
    record_chat_turn,
    render_dual_codex_chat_html,
    resolve_chat_model_override,
)
from .ion_domain_weaver import execute_domain_weaver_action
from .ion_local_cockpit_app import REACT_CSP, build_cockpit_html, build_react_cockpit_html, resolve_react_static_asset
from .ion_system_diagnostics import (
    build_system_diagnostics_model,
    execute_system_diagnostic_action,
    preview_system_diagnostic_action,
)
from .ion_project_cockpit import apply_project_cockpit_action
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
from .ion_helixion_project_access_inventory import (
    build_helixion_project_family_detail_model_from_file,
    build_helixion_projects_surface_model_from_file,
)
from .ion_helixion_collaboration_access import build_helixion_collaboration_access_model
from .ion_project_portfolio import materialize_project_portfolio_action
from .ion_project_workbench import (
    WRITE_CONFIRMATION_TOKEN as PROJECT_WRITE_CONFIRMATION_TOKEN,
    build_project_workspace_status,
    project_action_run,
    project_browser_capture,
    project_patch_apply,
    project_patch_preview,
    project_patch_revert,
    resolve_project,
)
from .ion_public_cockpit_auth import (
    ALLOWED_EMAILS_ENV,
    GOOGLE_CLIENT_ID_ENV,
    GOOGLE_CLIENT_SECRET_ENV,
    GOOGLE_REDIRECT_URI_ENV,
    INVITE_TOKENS_ENV,
    OAUTH_STATE_COOKIE,
    PUBLIC_COCKPIT_TOKEN_ENV,
    SESSION_COOKIE,
    SESSION_SECRET_ENV,
    auth_status,
    authorize_google_user,
    build_google_authorization_url,
    clear_cookie_header,
    cockpit_session_secret,
    exchange_google_code_for_userinfo,
    google_oauth_configured,
    make_oauth_state_cookie,
    make_session_cookie,
    safe_next_path,
    validate_oauth_state_cookie,
    validate_permission_token,
    validate_session_cookie,
)

PROJECT_LAUNCH_CSP = "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; frame-src http://127.0.0.1:* http://localhost:*; child-src http://127.0.0.1:* http://localhost:*; base-uri 'none'; frame-ancestors 'none'"

SCHEMA_ID = "ion.chatgpt_browser_http_mcp_preview.v1"
VERSION_LINE = "V121_CHATGPT_BROWSER_HTTP_MCP_PREVIEW"
READY_VERDICT = "ION_CHATGPT_BROWSER_HTTP_MCP_PREVIEW_READY"
BLOCKED_VERDICT = "ION_CHATGPT_BROWSER_HTTP_MCP_PREVIEW_BLOCKED"
WRITE_CONFIRMATION_TOKEN = "ION_BOUNDED_WRITE_CONFIRMED"
DEFAULT_BIND_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
EDIT_LEASE_REQUIRED_TOOLS = {"ion_project_patch_apply", "ion_bounded_patch_apply"}
CONDITIONAL_EDIT_LEASE_TOOLS = {
    "ion_file_put_text",
    "ion_artifact_upload_init",
    "ion_artifact_upload_chunk",
    "ion_artifact_upload_commit",
}
DEFAULT_APPLICATION_DEV_LAUNCHER_URL = "http://127.0.0.1:5199"
OUTPUT_RELATIVE_PATH = Path("ION/05_context/current/CHATGPT_BROWSER_HTTP_MCP_PREVIEW_V121.json")
APP_PATHS = {"/", "/app", "/ion", "/projects"}
COCKPIT_UI_PATHS = {
    "",
    "agents",
    "chatgpt-dom-twin",
    "browser-gpt",
    "chat",
    "collab",
    "codex",
    "devsecops",
    "docs",
    "extension",
    "gates",
    "legacy",
    "projects",
    "queue",
    "receipts",
    "system",
    "worker",
}
HELIXION_SITE_NAV_ITEMS = (
    {"id": "home", "label": "Home", "href": "/", "icon": "home"},
    {"id": "projects", "label": "Projects", "href": "/projects", "icon": "grid"},
    {"id": "cockpit", "label": "Cockpit", "href": "/cockpit", "icon": "grid"},
    {"id": "chat", "label": "Codex Chat", "href": "/cockpit/chat", "icon": "chat"},
    {"id": "worker", "label": "Worker", "href": "/cockpit/worker", "icon": "pulse"},
    {"id": "status", "label": "Status JSON", "href": "/app/status.json", "icon": "receipt"},
    {"id": "health", "label": "Health", "href": "/health", "icon": "check"},
    {"id": "login", "label": "Login", "href": "/cockpit/login", "icon": "key"},
)

HELIXION_SITE_CSS = """
.helix-sitebar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 0;
  min-height: 42px;
  padding: 0 10px;
  border-bottom: 1px solid #2b343a;
  background: #080a0b;
  color: #e7edf0;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
}
.helix-sitebar::before {
  content: "HELIXION";
  display: inline-flex;
  align-items: center;
  align-self: stretch;
  margin-right: 10px;
  padding: 0 12px 0 2px;
  border-right: 1px solid #2b343a;
  color: #f2c7a7;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0;
}
.helix-sitebar a {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  min-height: 30px;
  max-width: 180px;
  margin-right: 6px;
  padding: 5px 9px;
  border: 1px solid #2b343a;
  border-radius: 2px;
  background: #0d1113;
  color: #96a3aa;
  text-decoration: none;
  text-transform: uppercase;
  font-size: 10px;
  font-weight: 800;
  white-space: nowrap;
  overflow: hidden;
}
.helix-sitebar a:hover,
.helix-sitebar a:focus-visible {
  color: #e7edf0;
  border-color: #d7ad52;
  outline: none;
}
.helix-sitebar a.is-active {
  color: #e7edf0;
  border-color: #d7ad52;
  background: #151b1e;
  box-shadow: inset 0 -2px 0 #d7ad52;
}
.helix-sitebar svg {
  flex: 0 0 auto;
  width: 15px;
  height: 15px;
}
.helix-sitebar .helix-site-label {
  overflow: hidden;
  text-overflow: ellipsis;
}
@media (max-width: 820px) {
  .helix-sitebar {
    align-items: stretch;
    overflow-x: auto;
    padding: 6px 8px;
  }
  .helix-sitebar::before {
    min-height: 30px;
  }
  .helix-sitebar a {
    min-width: max-content;
  }
}
"""


def application_dev_launcher_url() -> str:
    return (os.environ.get("ION_APPLICATION_DEV_LAUNCHER_URL") or DEFAULT_APPLICATION_DEV_LAUNCHER_URL).rstrip("/")


def _json_text(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True)


def _html_text(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _payload_list(payload: Mapping[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in re.split(r"[\n,]", value) if item.strip()]
    return []


def _payload_mapping(payload: Mapping[str, Any], key: str) -> Mapping[str, Any] | None:
    value = payload.get(key)
    return value if isinstance(value, Mapping) else None


def _payload_int(payload: Mapping[str, Any], key: str, default: int) -> int:
    try:
        return int(payload.get(key) or default)
    except (TypeError, ValueError):
        return default


def _site_icon(name: str) -> str:
    paths = {
        "home": '<path d="M5 11.5 12 5l7 6.5V20H8v-6h8v6"/>',
        "grid": '<path d="M5 5h6v6H5z"/><path d="M13 5h6v6h-6z"/><path d="M5 13h6v6H5z"/><path d="M13 13h6v6h-6z"/>',
        "chat": '<path d="M5 6.5h14v8.5H9l-4 3V6.5Z"/><path d="M8 9.5h8M8 12h5"/>',
        "pulse": '<path d="M4 12h4l2-6 4 12 2-6h4"/>',
        "receipt": '<path d="M7 4h10v16l-2-1.2-2 1.2-2-1.2-2 1.2-2-1.2V4Z"/><path d="M9 8h6M9 12h6M9 16h4"/>',
        "check": '<path d="M5 12.5 9.5 17 19 7"/>',
        "key": '<path d="M14 9a4 4 0 1 0-2.6 3.7L13 14.3V17h2.7l1.1 1.1H19v-2.3l-4.2-4.2A4 4 0 0 0 14 9Z"/><path d="M7 9h.01"/>',
        "link": '<path d="M10 13a5 5 0 0 0 7 0l1-1a5 5 0 0 0-7-7l-1 1"/><path d="M14 11a5 5 0 0 0-7 0l-1 1a5 5 0 0 0 7 7l1-1"/>',
    }
    body = paths.get(name, paths["link"])
    return (
        '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
        f"{body}</svg>"
    )


def _site_href(path: str, *, auth_token: str | None = None, public_base_url: str | None = None) -> str:
    href = path
    _ = auth_token
    base = (public_base_url or "").rstrip("/")
    if base and href.startswith("/"):
        return f"{base}{href}"
    return href


def render_helixion_site_bar(
    active: str,
    *,
    auth_token: str | None = None,
    public_base_url: str | None = None,
) -> str:
    links = []
    for item in HELIXION_SITE_NAV_ITEMS:
        item_id = str(item["id"])
        active_class = " is-active" if item_id == active else ""
        current = ' aria-current="page"' if item_id == active else ""
        href = _site_href(str(item["href"]), auth_token=auth_token, public_base_url=public_base_url)
        links.append(
            f'<a class="helix-site-button{active_class}" href="{_html_text(href)}"{current}>'
            f'{_site_icon(str(item["icon"]))}<span class="helix-site-label">{_html_text(item["label"])}</span>'
            "</a>"
        )
    return f'<nav class="helix-sitebar" aria-label="HelixION site pages">{"".join(links)}</nav>'


def wrap_helixion_site_shell(
    page_html: str,
    active: str,
    *,
    auth_token: str | None = None,
    public_base_url: str | None = None,
) -> str:
    """Inject the shared HelixION site bar into existing cockpit HTML."""

    wrapped = page_html
    if "</style>" in wrapped:
        wrapped = wrapped.replace("</style>", HELIXION_SITE_CSS + "\n</style>", 1)
    elif "</head>" in wrapped:
        wrapped = wrapped.replace("</head>", f"<style>{HELIXION_SITE_CSS}</style></head>", 1)
    bar = render_helixion_site_bar(active, auth_token=auth_token, public_base_url=public_base_url)
    if "<body>" in wrapped:
        return wrapped.replace("<body>", f"<body>\n{bar}", 1)
    return bar + wrapped


def _tool_schema(name: str) -> dict[str, Any]:
    if name == "ion_read_active_packet":
        return {
            "type": "object",
            "properties": {"packet": {"type": "string"}},
            "required": ["packet"],
            "additionalProperties": False,
        }
    if name == "ion_carrier_onboarding_packet":
        return {
            "type": "object",
            "properties": {
                "carrier": {"type": "string"},
                "carrier_profile": {"type": "string"},
            },
            "additionalProperties": False,
        }
    if name == "ion_receipt_search":
        return {
            "type": "object",
            "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 50}},
            "additionalProperties": False,
        }
    if name == "ion_action_branch_list":
        return {
            "type": "object",
            "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 100}},
            "additionalProperties": False,
        }
    if name == "ion_action_branch_describe":
        return {
            "type": "object",
            "properties": {
                "branch_id": {"type": "string"},
                "path": {"type": "string"},
                "path_or_branch_id": {"type": "string"},
                "depth": {"type": "string"},
                "profile": {"type": "string"},
            },
            "additionalProperties": False,
        }
    if name == "ion_action_branch_receipts":
        return {
            "type": "object",
            "properties": {
                "branch_id": {"type": "string"},
                "route_id": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 50},
            },
            "required": ["branch_id"],
            "additionalProperties": False,
        }
    if name == "ion_action_branch_invoke":
        return {
            "type": "object",
            "properties": {
                "branch_id": {"type": "string"},
                "route_id": {"type": "string"},
                "args": {"type": "object", "additionalProperties": True, "properties": {}},
                "idempotency_key": {"type": "string"},
                "confirmation": {"type": "string"},
                "approval": {"type": "object", "additionalProperties": True, "properties": {}},
                "expected_route_schema_version": {"type": "string"},
            },
            "required": ["branch_id", "route_id", "expected_route_schema_version"],
            "additionalProperties": False,
        }
    if name == "ion_codex_work_queue":
        return {
            "type": "object",
            "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 100}},
            "additionalProperties": False,
        }
    if name == "ion_codex_queue_duplicate_audit":
        return {
            "type": "object",
            "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 100}},
            "additionalProperties": False,
        }
    if name == "ion_file_read":
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "max_bytes": {"type": "integer", "minimum": 1, "maximum": 262144},
            },
            "required": ["path"],
            "additionalProperties": False,
        }
    if name == "ion_file_search":
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "roots": {"type": "array", "items": {"type": "string"}, "maxItems": 10},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "max_files": {"type": "integer", "minimum": 1, "maximum": 500},
            },
            "required": ["query"],
            "additionalProperties": False,
        }
    if name == "ion_tree_list":
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "max_depth": {"type": "integer", "minimum": 0, "maximum": 6},
                "limit": {"type": "integer", "minimum": 1, "maximum": 1000},
            },
            "additionalProperties": False,
        }
    if name in {"ion_registry_read", "ion_template_read"}:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "name": {"type": "string"},
                "max_bytes": {"type": "integer", "minimum": 1, "maximum": 262144},
            },
            "additionalProperties": False,
        }
    if name == "ion_context_compile":
        return {
            "type": "object",
            "properties": {
                "profile": {"type": "string"},
                "include_excerpts": {"type": "boolean"},
            },
            "additionalProperties": False,
        }
    if name == "ion_receipt_hydrate":
        return {
            "type": "object",
            "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 100}},
            "additionalProperties": False,
        }
    if name == "ion_tool_manifest":
        return {"type": "object", "properties": {}, "additionalProperties": False}
    if name == "ion_codex_capsule_chat_status":
        return {
            "type": "object",
            "properties": {
                "include_preview": {"type": "boolean"},
                "max_preview_bytes": {"type": "integer", "minimum": 1, "maximum": 2048},
            },
            "additionalProperties": False,
        }
    if name == "ion_codex_capsule_message_poll":
        return {
            "type": "object",
            "properties": {
                "lane_id": {"type": "string"},
                "since_turn_id": {"type": "string"},
                "include_assistant": {"type": "boolean"},
                "include_context_posts": {"type": "boolean"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
            },
            "additionalProperties": False,
        }
    if name in {"ion_daemon_status", "ion_codex_queue_autorun_status"}:
        return {"type": "object", "properties": {}, "additionalProperties": False}
    if name == "ion_codex_worker_live_status":
        return {
            "type": "object",
            "properties": {
                "include_preview": {"type": "boolean"},
                "preview_target": {"type": "string", "enum": ["latest_return", "stdout", "stderr", "worker_stdout", "worker_stderr"]},
                "max_preview_bytes": {"type": "integer", "minimum": 1, "maximum": 2048},
                "include_observability_trace": {"type": "boolean"},
            },
            "additionalProperties": False,
        }
    if name == "ion_codex_worker_trace":
        return {
            "type": "object",
            "properties": {
                "max_preview_bytes": {"type": "integer", "minimum": 1, "maximum": 2048},
            },
            "additionalProperties": False,
        }
    if name in {"ion_agent_list", "ion_agent_status", "ion_swarm_status"}:
        return {"type": "object", "properties": {}, "additionalProperties": False}
    if name == "ion_agent_queue":
        return {
            "type": "object",
            "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 100}},
            "additionalProperties": False,
        }
    if name == "ion_agent_result":
        return {
            "type": "object",
            "properties": {"invocation_id": {"type": "string"}},
            "additionalProperties": False,
        }
    if name == "ion_agent_spawn_plan":
        return {
            "type": "object",
            "properties": {"objective": {"type": "string"}},
            "additionalProperties": False,
        }
    if name == "ion_codex_queue_process_once":
        return {
            "type": "object",
            "properties": {
                "request_path": {"type": "string"},
                "start": {"type": "boolean"},
                "max_runtime_seconds": {"type": "integer", "minimum": 30, "maximum": 7200},
                "include_preview": {"type": "boolean"},
                "preview_target": {"type": "string", "enum": ["result", "stdout", "stderr", "worker_stdout", "worker_stderr", "task_return_body"]},
                "max_preview_bytes": {"type": "integer", "minimum": 1, "maximum": 2048},
                "confirmation": {"type": "string"},
            },
            "required": ["confirmation"],
            "additionalProperties": False,
        }
    if name == "ion_agent_invoke":
        return {
            "type": "object",
            "properties": {
                "agent": {"type": "string"},
                "objective": {"type": "string"},
                "mode": {"type": "string"},
                "queue": {"type": "boolean"},
                "start": {"type": "boolean"},
                "context_refs": {"type": "array", "items": {"type": "string"}},
                "requested_by_carrier_id": {"type": "string"},
                "requested_by_callsign": {"type": "string"},
                "max_runtime_seconds": {"type": "integer", "minimum": 30, "maximum": 7200},
                "confirmation": {"type": "string"},
            },
            "required": ["agent", "objective", "confirmation"],
            "additionalProperties": False,
        }
    if name == "ion_agent_cancel":
        return {
            "type": "object",
            "properties": {
                "invocation_id": {"type": "string"},
                "confirmation": {"type": "string"},
            },
            "required": ["invocation_id", "confirmation"],
            "additionalProperties": False,
        }
    if name == "ion_swarm_step_once":
        return {
            "type": "object",
            "properties": {
                "request_path": {"type": "string"},
                "start": {"type": "boolean"},
                "max_runtime_seconds": {"type": "integer", "minimum": 30, "maximum": 7200},
                "confirmation": {"type": "string"},
            },
            "required": ["confirmation"],
            "additionalProperties": False,
        }
    if name == "ion_codex_runner_reconcile":
        return {
            "type": "object",
            "properties": {
                "write": {"type": "boolean"},
                "confirmation": {"type": "string"},
            },
            "required": ["confirmation"],
            "additionalProperties": False,
        }
    if name == "ion_codex_queue_supersede_duplicates":
        return {
            "type": "object",
            "properties": {
                "confirmation": {"type": "string"},
                "idempotency_key": {"type": "string"},
                "all_duplicates": {"type": "boolean"},
                "group_key": {"type": "string"},
                "dedupe_key": {"type": "string"},
                "objective_sha256": {"type": "string"},
                "request_ids": {"type": "array", "items": {"type": "string"}, "maxItems": 100},
                "reason": {"type": "string"},
                "force_new": {"type": "boolean"},
            },
            "required": ["confirmation", "idempotency_key"],
            "additionalProperties": False,
        }

    if name in {"ion_bounded_patch_preview", "ion_bounded_patch_apply"}:
        operation_schema = {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "target_path": {"type": "string"},
                "old_text": {"type": "string"},
                "new_text": {"type": "string"},
                "expected_sha256": {"type": "string"},
            },
            "additionalProperties": False,
        }
        properties = {
            "operations": {"type": "array", "items": operation_schema, "maxItems": 25},
            "path": {"type": "string"},
            "target_path": {"type": "string"},
            "old_text": {"type": "string"},
            "new_text": {"type": "string"},
            "expected_sha256": {"type": "string"},
        }
        required = []
        if name == "ion_bounded_patch_apply":
            properties.update({
                "confirmation": {"type": "string"},
                "agent_id": {"type": "string"},
                "lease_id": {"type": "string"},
                "idempotency_key": {
                    "type": "string",
                    "description": "Stable key for safe retries; repeated keys return the original patch receipt.",
                },
                "client_request_id": {"type": "string"},
                "force_new": {"type": "boolean"},
            })
            required = ["confirmation", "agent_id", "lease_id"]
        return {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        }

    if name in {"ion_project_workspace_status", "ion_project_preview_status", "ion_project_git_status"}:
        return {
            "type": "object",
            "properties": {
                "project_id": {"type": "string"},
                "probe_preview": {"type": "boolean"},
            },
            "additionalProperties": False,
        }
    if name == "ion_project_workbench_timeline":
        return {
            "type": "object",
            "properties": {
                "project_id": {"type": "string"},
                "probe_preview": {"type": "boolean"},
                "max_items": {"type": "integer", "minimum": 1, "maximum": 20},
            },
            "additionalProperties": False,
        }
    if name == "ion_project_file_read":
        return {
            "type": "object",
            "properties": {
                "project_id": {"type": "string"},
                "path": {"type": "string"},
                "max_bytes": {"type": "integer", "minimum": 1, "maximum": 262144},
            },
            "required": ["project_id", "path"],
            "additionalProperties": False,
        }
    if name in {"ion_project_patch_preview", "ion_project_patch_apply"}:
        operation_schema = {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "target_path": {"type": "string"},
                "old_text": {"type": "string"},
                "new_text": {"type": "string"},
                "expected_sha256": {"type": "string"},
            },
            "additionalProperties": False,
        }
        properties = {
            "project_id": {"type": "string"},
            "operations": {"type": "array", "items": operation_schema, "maxItems": 25},
            "path": {"type": "string"},
            "target_path": {"type": "string"},
            "old_text": {"type": "string"},
            "new_text": {"type": "string"},
            "expected_sha256": {"type": "string"},
        }
        required = ["project_id"]
        if name == "ion_project_patch_apply":
            properties.update({
                "confirmation": {"type": "string"},
                "idempotency_key": {"type": "string"},
                "client_request_id": {"type": "string"},
                "agent_id": {
                    "type": "string",
                    "description": "Active Worker Shift actor id that owns the edit lease.",
                },
                "lease_id": {
                    "type": "string",
                    "description": "Active exclusive_write Worker Shift lease covering every patch target.",
                },
                "force_new": {"type": "boolean"},
            })
            required = ["project_id", "confirmation", "agent_id", "lease_id"]
        return {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        }
    if name == "ion_project_patch_revert":
        return {
            "type": "object",
            "properties": {
                "project_id": {"type": "string"},
                "receipt_path": {"type": "string"},
                "confirmation": {"type": "string"},
                "agent_id": {"type": "string"},
                "lease_id": {"type": "string"},
            },
            "required": ["project_id", "receipt_path", "confirmation", "agent_id", "lease_id"],
            "additionalProperties": False,
        }
    if name == "ion_project_action_run":
        return {
            "type": "object",
            "properties": {
                "project_id": {"type": "string"},
                "action_id": {"type": "string", "enum": ["build", "test", "lint", "screenshots", "gibs_snapshot"]},
                "timeout_seconds": {"type": "integer", "minimum": 30, "maximum": 7200},
                "confirmation": {"type": "string"},
            },
            "required": ["project_id", "action_id", "confirmation"],
            "additionalProperties": False,
        }
    if name == "ion_project_browser_capture":
        return {
            "type": "object",
            "properties": {
                "project_id": {"type": "string"},
                "bookmark": {
                    "type": "string",
                    "enum": [
                        "home",
                        "lab",
                        "orbit",
                        "cloud-terminator",
                        "high-altitude",
                        "storm-zone",
                        "sun-glitter",
                        "sea-level",
                        "underwater",
                    ],
                },
                "interaction": {"type": "string", "enum": ["none", "reload"]},
                "base_url": {"type": "string"},
                "width": {"type": "integer", "minimum": 320, "maximum": 3840},
                "height": {"type": "integer", "minimum": 320, "maximum": 2400},
                "wait_ms": {"type": "integer", "minimum": 0, "maximum": 15000},
                "timeout_ms": {"type": "integer", "minimum": 5000, "maximum": 180000},
                "confirmation": {"type": "string"},
            },
            "required": ["project_id", "bookmark", "confirmation"],
            "additionalProperties": False,
        }

    if name == "ion_file_put_text":
        return {
            "type": "object",
            "properties": {
                "target_path": {"type": "string"},
                "text": {"type": "string"},
                "expected_sha256": {"type": "string"},
                "overwrite": {"type": "boolean"},
                "confirmation": {"type": "string"},
                "agent_id": {"type": "string"},
                "lease_id": {"type": "string"},
                "preview_only": {"type": "boolean"},
                "idempotency_key": {"type": "string"},
                "client_request_id": {"type": "string"},
                "force_new": {"type": "boolean"},
            },
            "required": ["target_path", "text"],
            "additionalProperties": False,
        }
    if name == "ion_artifact_upload_init":
        return {
            "type": "object",
            "properties": {
                "artifact_name": {"type": "string"},
                "target_path": {"type": "string"},
                "expected_sha256": {"type": "string"},
                "total_bytes": {"type": "integer", "minimum": 0},
                "mime_type": {"type": "string"},
                "confirmation": {"type": "string"},
                "agent_id": {"type": "string"},
                "lease_id": {"type": "string"},
            },
            "required": ["artifact_name", "confirmation", "agent_id", "lease_id"],
            "additionalProperties": False,
        }
    if name == "ion_artifact_upload_chunk":
        return {
            "type": "object",
            "properties": {
                "upload_id": {"type": "string"},
                "chunk_index": {"type": "integer", "minimum": 0},
                "data_base64": {"type": "string"},
                "chunk_sha256": {"type": "string"},
                "confirmation": {"type": "string"},
                "agent_id": {"type": "string"},
                "lease_id": {"type": "string"},
            },
            "required": ["upload_id", "chunk_index", "data_base64", "confirmation", "agent_id", "lease_id"],
            "additionalProperties": False,
        }
    if name == "ion_artifact_upload_commit":
        return {
            "type": "object",
            "properties": {
                "upload_id": {"type": "string"},
                "confirmation": {"type": "string"},
                "agent_id": {"type": "string"},
                "lease_id": {"type": "string"},
            },
            "required": ["upload_id", "confirmation", "agent_id", "lease_id"],
            "additionalProperties": False,
        }
    if name == "ion_carrier_message_send":
        return {
            "type": "object",
            "properties": {
                "sender_carrier_id": {"type": "string"},
                "recipient": {"type": "string"},
                "channel": {"type": "string"},
                "message_type": {"type": "string"},
                "body": {"type": "string"},
                "context_refs": {"type": "array", "items": {"type": "string"}},
                "receipt_refs": {"type": "array", "items": {"type": "string"}},
                "confirmation": {"type": "string"},
            },
            "required": ["sender_carrier_id", "recipient", "body", "confirmation"],
            "additionalProperties": False,
        }
    if name == "ion_carrier_message_poll":
        return {
            "type": "object",
            "properties": {
                "recipient": {"type": "string"},
                "channel": {"type": "string"},
                "include_acked": {"type": "boolean"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
            },
            "additionalProperties": False,
        }
    if name == "ion_carrier_message_ack":
        return {
            "type": "object",
            "properties": {
                "message_id": {"type": "string"},
                "ack_by_carrier": {"type": "string"},
                "confirmation": {"type": "string"},
            },
            "required": ["message_id", "ack_by_carrier", "confirmation"],
            "additionalProperties": False,
        }
    if name == "ion_codex_capsule_message_send":
        return {
            "type": "object",
            "properties": {
                "lane_id": {"type": "string"},
                "message": {"type": "string"},
                "body": {"type": "string"},
                "author": {"type": "string"},
                "execution_mode": {"type": "string"},
                "confirmation": {"type": "string"},
            },
            "required": ["confirmation"],
            "additionalProperties": False,
        }
    if name == "ion_codex_capsule_sync_to_queue":
        return {
            "type": "object",
            "properties": {
                "lane_id": {"type": "string"},
                "objective": {"type": "string"},
                "message": {"type": "string"},
                "source_turn_id": {"type": "string"},
                "confirmation": {"type": "string"},
            },
            "required": ["confirmation"],
            "additionalProperties": False,
        }
    if name == "ion_queue_operator_message":
        return {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "priority": {"type": "integer", "minimum": 0, "maximum": 100},
                "confirmation": {"type": "string"},
            },
            "required": ["message", "confirmation"],
            "additionalProperties": False,
        }
    if name == "ion_request_codex_work_packet":
        return {
            "type": "object",
            "properties": {
                "objective": {"type": "string"},
                "confirmation": {"type": "string"},
                "codex_model_move": {
                    "type": "object",
                    "description": "Optional deterministic Codex CLI model-move plan created by ION.",
                    "additionalProperties": True,
                },
                "codex_model_override": {
                    "type": "object",
                    "description": "Optional explicit Codex model override validated by queue-runner against model profiles.",
                    "properties": {
                        "selected_model": {"type": "string"},
                        "selected_reasoning_effort": {"type": "string"},
                        "reason": {"type": "string"},
                    },
                    "additionalProperties": True,
                },
                "requested_model": {"type": "string"},
                "requested_reasoning_effort": {"type": "string"},
                "model_override_reason": {"type": "string"},
                "project_hash": {"type": "string"},
                "required_context_reads": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "kind": {"type": "string"},
                            "path": {"type": "string"},
                            "required": {"type": "boolean"},
                        },
                        "required": ["path"],
                        "additionalProperties": False,
                    },
                },
                "idempotency_key": {
                    "type": "string",
                    "description": "Stable key for safe retries; repeated keys return the original packet instead of creating a duplicate.",
                },
                "client_request_id": {
                    "type": "string",
                    "description": "Optional carrier-side request id used for no-receipt/timeout replay recovery.",
                },
                "force_new": {
                    "type": "boolean",
                    "description": "Explicitly bypass dedupe for intentional duplicate work. Defaults to false.",
                },
            },
            "required": ["objective", "confirmation"],
            "additionalProperties": False,
        }
    if name == "ion_submit_task_return":
        return {
            "type": "object",
            "properties": {
                "task_output_text": {"type": "string"},
                "context_receipt": {"type": "object"},
                "work_request_id": {"type": "string"},
                "work_request_path": {"type": "string"},
                "confirmation": {"type": "string"},
            },
            "required": ["task_output_text", "context_receipt", "confirmation"],
            "additionalProperties": True,
        }
    if name == "ion_submit_alternate_worker_return":
        return {
            "type": "object",
            "properties": {
                "task_output_text": {"type": "string"},
                "context_receipt": {"type": "object", "additionalProperties": True},
                "work_request_id": {"type": "string"},
                "work_request_path": {"type": "string"},
                "confirmation": {"type": "string"},
                "alternate_worker_identity": {"type": "object", "additionalProperties": True},
                "alternate_worker_provenance": {"type": "object", "additionalProperties": True},
                "worker_output_sha256": {"type": "string"},
                "alternate_worker_provenance_receipt_path": {"type": "string"},
                "require_provenance_receipt": {"type": "boolean"},
            },
            "required": [
                "task_output_text",
                "context_receipt",
                "work_request_path",
                "confirmation",
                "alternate_worker_identity",
                "alternate_worker_provenance",
            ],
            "additionalProperties": False,
        }
    if name == "ion_record_native_subagent_transcript":
        return {
            "type": "object",
            "properties": {
                "confirmation": {"type": "string"},
                "idempotency_key": {"type": "string"},
                "subagent_id": {"type": "string"},
                "worker_id": {"type": "string"},
                "source_ref": {"type": "string"},
                "work_request_path": {"type": "string"},
                "status": {"type": "string"},
                "worker_output_text": {"type": "string"},
                "observed_by": {"type": "string"},
                "claim_boundary": {"type": "string"},
            },
            "required": [
                "confirmation",
                "idempotency_key",
                "subagent_id",
                "worker_id",
                "source_ref",
                "work_request_path",
                "status",
                "worker_output_text",
                "claim_boundary",
            ],
            "additionalProperties": False,
        }
    if name == "ion_record_alternate_worker_provenance":
        return {
            "type": "object",
            "properties": {
                "confirmation": {"type": "string"},
                "idempotency_key": {"type": "string"},
                "alternate_worker_identity": {"type": "object", "additionalProperties": True},
                "worker_identity": {"type": "object", "additionalProperties": True},
                "alternate_worker_provenance": {"type": "object", "additionalProperties": True},
                "worker_output_sha256": {"type": "string"},
                "native_subagent_transcript_receipt_path": {"type": "string"},
            },
            "required": [
                "confirmation",
                "idempotency_key",
                "alternate_worker_provenance",
                "worker_output_sha256",
            ],
            "additionalProperties": False,
        }
    if name == "ion_record_chatgpt_decision":
        return {
            "type": "object",
            "properties": {
                "decision": {"type": "string"},
                "rationale": {"type": "string"},
                "confirmation": {"type": "string"},
            },
            "required": ["decision", "confirmation"],
            "additionalProperties": False,
        }
    if name == "ion_create_containment_receipt":
        return {
            "type": "object",
            "properties": {
                "target_path": {"type": "string"},
                "transition": {"type": "string"},
                "reason": {"type": "string"},
                "confirmation": {"type": "string"},
            },
            "required": ["target_path", "reason", "confirmation"],
            "additionalProperties": False,
        }
    return {"type": "object", "properties": {}, "additionalProperties": False}


def http_mcp_tool_list() -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    for name in sorted(STATUS_READ_TOOLS | BOUNDED_QUEUE_RECEIPT_TOOLS):
        write_tool = name in BOUNDED_QUEUE_RECEIPT_TOOLS
        tools.append({
            "name": name,
            "description": (
                "ION bounded queue/receipt tool; requires explicit ION write confirmation."
                if write_tool
                else "ION bounded status/read tool."
            ),
            "inputSchema": _tool_schema(name),
            "annotations": {
                "readOnlyHint": not write_tool,
                "destructiveHint": False,
                "idempotentHint": not write_tool,
                "openWorldHint": False,
            },
        })
    return tools


def _jsonrpc_result(msg_id: Any, result: Mapping[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": msg_id, "result": dict(result)}


def _jsonrpc_error(msg_id: Any, message: str, code: int = -32000) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def _tool_call_result(tool_name: str, result: Mapping[str, Any], *, is_error: bool) -> dict[str, Any]:
    return {
        "content": [{"type": "text", "text": _json_text(result)}],
        "structuredContent": dict(result),
        "isError": is_error,
    }


def _requires_write_confirmation(root: str | Path, tool_name: str, args: Mapping[str, Any]) -> bool:
    if tool_name == "ion_action_branch_invoke":
        from .ion_action_mcp_branch_leaders import validate_branch_route

        _branch, route, blocked = validate_branch_route(
            root,
            str(args.get("branch_id") or ""),
            str(args.get("route_id") or ""),
        )
        if blocked or route is None:
            return False
        route_args = args.get("args") if isinstance(args.get("args"), Mapping) else {}
        route_confirmation = route_args.get("confirmation") or args.get("confirmation")
        conditional_write = bool(route.get("conditional_write")) and any(
            str(route_args.get(key) or "").strip().lower() in {"1", "true", "yes", "write"}
            for key in ("write", "write_receipt", "write_candidate_capsule")
        )
        if not bool(route.get("mutates_state")) and not conditional_write:
            return False
        return route_confirmation != WRITE_CONFIRMATION_TOKEN
    return tool_name in BOUNDED_QUEUE_RECEIPT_TOOLS and args.get("confirmation") != WRITE_CONFIRMATION_TOKEN


def handle_mcp_jsonrpc(root: str | Path, payload: Mapping[str, Any]) -> dict[str, Any] | None:
    method = payload.get("method")
    msg_id = payload.get("id")
    params = payload.get("params") or {}
    if method and str(method).startswith("notifications/"):
        return None

    if method == "initialize":
        return _jsonrpc_result(msg_id, {
            "protocolVersion": params.get("protocolVersion") or "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "ion-chatgpt-browser-preview", "version": VERSION_LINE},
        })
    if method == "tools/list":
        return _jsonrpc_result(msg_id, {"tools": http_mcp_tool_list()})
    if method == "tools/call":
        tool_name = str(params.get("name") or "")
        arguments = params.get("arguments") or {}
        if not isinstance(arguments, Mapping):
            return _jsonrpc_error(msg_id, "Tool arguments must be an object")
        if tool_name in FORBIDDEN_CAPABILITIES:
            blocked = {
                "schema_id": "ion.chatgpt_browser_http_mcp_tool_result.v1",
                "tool": tool_name,
                "ok": False,
                "finding": "forbidden_capability",
                "production_authority": False,
                "live_execution_authority": False,
            }
            return _jsonrpc_result(msg_id, _tool_call_result(tool_name, blocked, is_error=True))
        if _requires_write_confirmation(root, tool_name, arguments):
            blocked = {
                "schema_id": "ion.chatgpt_browser_http_mcp_tool_result.v1",
                "tool": tool_name,
                "ok": False,
                "finding": "bounded_write_confirmation_required",
                "required_confirmation": WRITE_CONFIRMATION_TOKEN,
                "production_authority": False,
                "live_execution_authority": False,
            }
            return _jsonrpc_result(msg_id, _tool_call_result(tool_name, blocked, is_error=True))

        # The HTTP/MCP adapter performs the public write-confirmation gate above,
        # but the connector contract also performs its own defense-in-depth
        # confirmation checks. Preserve the confirmation field when forwarding
        # bounded write calls; stripping it caused write tools such as
        # ion_bounded_patch_apply to fail closed with confirmation_required even
        # after a valid MCP confirmation.
        clean_args = dict(arguments)
        result = call_chatgpt_connector_tool(root, tool_name, clean_args)
        return _jsonrpc_result(msg_id, _tool_call_result(tool_name, result, is_error=not bool(result.get("ok"))))
    if method == "ping":
        return _jsonrpc_result(msg_id, {})
    return _jsonrpc_error(msg_id, f"Unsupported MCP method: {method}")


def audit_http_mcp_preview(root: str | Path | None = None) -> dict[str, Any]:
    contract = audit_chatgpt_browser_mcp_connector_contract(root)
    findings: list[str] = []
    tool_names = {tool["name"] for tool in http_mcp_tool_list()}
    allowed = STATUS_READ_TOOLS | BOUNDED_QUEUE_RECEIPT_TOOLS
    if tool_names != allowed:
        findings.append("http_tool_list_does_not_match_v120_contract")
    if tool_names & FORBIDDEN_CAPABILITIES:
        findings.append("http_tool_list_exposes_forbidden_capability")
    for tool in http_mcp_tool_list():
        if tool["name"] in BOUNDED_QUEUE_RECEIPT_TOOLS and "confirmation" not in tool["inputSchema"].get("properties", {}):
            findings.append(f"write_tool_missing_confirmation_schema:{tool['name']}")
        if tool["name"] in EDIT_LEASE_REQUIRED_TOOLS:
            properties = tool["inputSchema"].get("properties", {})
            required = set(tool["inputSchema"].get("required", []))
            if "agent_id" not in properties or "lease_id" not in properties:
                findings.append(f"edit_tool_missing_lease_schema:{tool['name']}")
            if not {"agent_id", "lease_id"}.issubset(required):
                findings.append(f"edit_tool_missing_required_lease_fields:{tool['name']}")
        if tool["name"] in CONDITIONAL_EDIT_LEASE_TOOLS:
            properties = tool["inputSchema"].get("properties", {})
            if "agent_id" not in properties or "lease_id" not in properties:
                findings.append(f"conditional_edit_tool_missing_lease_schema:{tool['name']}")
    if not contract.get("accepted"):
        findings.append("v120_connector_contract_not_ready")
    ready = not findings
    return {
        "schema_id": SCHEMA_ID,
        "version_line": VERSION_LINE,
        "verdict": READY_VERDICT if ready else BLOCKED_VERDICT,
        "accepted": ready,
        "connector_state": "LOCAL_HTTP_PREVIEW_NOT_PUBLIC_CONNECTOR" if ready else "BLOCKED",
        "endpoint_path": "/mcp",
        "public_cockpit_auth": auth_status(),
        "default_bind_host": DEFAULT_BIND_HOST,
        "default_port": DEFAULT_PORT,
        "write_confirmation_required": True,
        "write_confirmation_token": WRITE_CONFIRMATION_TOKEN,
        "allowed_tools": sorted(allowed),
        "forbidden_tools": sorted(FORBIDDEN_CAPABILITIES),
        "findings": findings,
        "production_authority": False,
        "live_execution_authority": False,
        "deployment_authority": False,
    }


def render_ion_connector_landing(
    root: str | Path,
    *,
    public_base_url: str | None = None,
    active_nav: str = "home",
) -> str:
    """Render a safe human-facing landing page for the tunnel root.

    The page intentionally exposes only connector posture and tool names. It does
    not expose secrets, local absolute paths, source excerpts, or shell controls.
    """

    audit = audit_http_mcp_preview(root)
    base = (public_base_url or "").rstrip("/")
    connector_hint = f"{base}/mcp" if base else "/mcp"
    health_hint = f"{base}/health" if base else "/health"
    worker_hint = f"{base}/cockpit/worker" if base else "/cockpit/worker"
    cockpit_hint = f"{base}/cockpit" if base else "/cockpit"
    chat_hint = f"{base}/cockpit/chat" if base else "/cockpit/chat"
    login_hint = f"{base}/cockpit/login" if base else "/cockpit/login"
    status_hint = f"{base}/app/status.json" if base else "/app/status.json"
    projects_hint = f"{base}/projects" if base else "/projects"
    status_class = "ready" if audit.get("accepted") else "blocked"
    allowed_tools = audit.get("allowed_tools") if isinstance(audit.get("allowed_tools"), list) else []
    forbidden_tools = audit.get("forbidden_tools") if isinstance(audit.get("forbidden_tools"), list) else []
    findings = audit.get("findings") if isinstance(audit.get("findings"), list) else []
    try:
        project_surface = build_helixion_projects_surface_model_from_file(root)
        project_surface_state = "live canon"
    except Exception as exc:
        project_surface = {
            "schema_id": "ion.helixion_projects_surface.unavailable.v0_1",
            "portfolio_summary": {},
            "access_summary": {"path_inspection_allowed": False},
            "canonical_domains": [],
            "featured_families": [],
            "agent_operating_model": [],
            "timeline_axes": [],
            "future_plan_lanes": [],
            "project_canon_contract": {
                "address_space": "ion://workspace virtual paths",
                "local_path_policy": "portfolio manifest unavailable",
                "management_rule": "visibility only; no production, live execution, accepted-state, or secrets authority",
            },
        }
        project_surface_state = f"surface unavailable: {exc.__class__.__name__}"
    portfolio_summary = project_surface.get("portfolio_summary") if isinstance(project_surface.get("portfolio_summary"), Mapping) else {}
    access_summary = project_surface.get("access_summary") if isinstance(project_surface.get("access_summary"), Mapping) else {}
    canon_contract = (
        project_surface.get("project_canon_contract")
        if isinstance(project_surface.get("project_canon_contract"), Mapping)
        else {}
    )

    def _metric_card(label: str, value: Any) -> str:
        return (
            '<article class="canon-metric">'
            f"<span>{_html_text(label)}</span>"
            f"<b>{_html_text(value if value not in {None, ''} else 0)}</b>"
            "</article>"
        )

    canon_metrics = "\n".join(
        _metric_card(label, portfolio_summary.get(key))
        for key, label in [
            ("project_root_count", "Project roots"),
            ("family_count", "Families"),
            ("canonical_domain_count", "Domains"),
            ("launchable_count", "Launchable"),
            ("documentation_surface_count", "Docs"),
            ("duplicate_cluster_count", "Duplicate clusters"),
            ("project_os_ready_count", "Ready"),
            ("project_os_watch_count", "Watch"),
            ("project_os_blocked_count", "Blocked"),
        ]
    )
    canon_domain_cards = "\n".join(
        (
            '<article class="canon-card">'
            f'<span>{_html_text(((domain.get("operating_system") or {}).get("posture")) if isinstance(domain.get("operating_system"), Mapping) else "mapped")}</span>'
            f'<b>{_html_text(domain.get("label"))}</b>'
            f'<p>{_html_text(domain.get("summary"))}</p>'
            '<div class="canon-stats">'
            f'<code>{_html_text(domain.get("family_count", 0))} families</code>'
            f'<code>{_html_text(domain.get("version_count", 0))} versions</code>'
            f'<code>{_html_text(domain.get("launchable_count", 0))} launch</code>'
            f'<code>{_html_text(domain.get("doc_count", 0))} docs</code>'
            "</div>"
            "</article>"
        )
        for domain in [
            item
            for item in (project_surface.get("canonical_domains") or [])
            if isinstance(item, Mapping)
        ][:6]
    )
    canon_family_cards = "\n".join(
        (
            f'<a class="canon-card canon-family-card" href="{_html_text(family.get("detail_href") or "#")}">'
            f'<span>{_html_text(((family.get("operating_system") or {}).get("posture")) if isinstance(family.get("operating_system"), Mapping) else family.get("lineage_status"))}</span>'
            f'<b>{_html_text(family.get("label"))}</b>'
            f'<p>{_html_text((family.get("current") or {}).get("display_label") if isinstance(family.get("current"), Mapping) else family.get("lineage_status"))}</p>'
            '<div class="canon-stats">'
            f'<code>{_html_text(family.get("version_count", 0))} versions</code>'
            f'<code>{_html_text(family.get("diff_count", 0))} diffs</code>'
            f'<code>{_html_text(family.get("launchable_count", 0))} launch</code>'
            f'<code>{_html_text(family.get("doc_count", 0))} docs</code>'
            "</div>"
            f'<code class="canon-path">{_html_text(family.get("virtual_path"))}</code>'
            "<span class=\"canon-open\">Open family</span>"
            "</a>"
        )
        for family in [
            item
            for item in (project_surface.get("featured_families") or [])
            if isinstance(item, Mapping)
        ][:6]
    )
    canon_agent_cards = "\n".join(
        (
            '<article class="canon-card compact">'
            f'<span>{_html_text(agent.get("role_id"))}</span>'
            f'<b>{_html_text(agent.get("label"))}</b>'
            f'<p>{_html_text(agent.get("responsibility"))}</p>'
            "</article>"
        )
        for agent in [
            item
            for item in (project_surface.get("agent_operating_model") or [])
            if isinstance(item, Mapping)
        ][:5]
    )
    canon_axis_items = "\n".join(
        f'<li><b>{_html_text(axis.get("label"))}</b><span>{_html_text(axis.get("unit"))}</span></li>'
        for axis in [
            item
            for item in (project_surface.get("timeline_axes") or [])
            if isinstance(item, Mapping)
        ][:5]
    )
    canon_future_items = "\n".join(
        f'<li><b>{_html_text(lane.get("label"))}</b><span>{_html_text(lane.get("goal"))}</span></li>'
        for lane in [
            item
            for item in (project_surface.get("future_plan_lanes") or [])
            if isinstance(item, Mapping)
        ][:5]
    )
    tool_items = "\n".join(f"<li><code>{_html_text(tool)}</code></li>" for tool in allowed_tools[:80])
    forbidden_items = "\n".join(f"<li><code>{_html_text(tool)}</code></li>" for tool in forbidden_tools[:80])
    finding_items = "\n".join(f"<li>{_html_text(item)}</li>" for item in findings) or "<li>none</li>"
    route_cards = "\n".join(
        (
            '<a class="route-card" href="{href}">'
            '<span>{kind}</span>'
            '<b>{label}</b>'
            '<p>{summary}</p>'
            '</a>'
        ).format(
            href=_html_text(href),
            kind=_html_text(kind),
            label=_html_text(label),
            summary=_html_text(summary),
        )
        for label, kind, href, summary in [
            ("Operator Cockpit", "HTML", cockpit_hint, "Runtime, queues, services, receipts, and authority state."),
            ("Projects Hub", "HTML", projects_hint, "Public and local ION Operations project directory."),
            ("Codex Chat", "HTML", chat_hint, "Capsule-backed operator chat and bounded queue controls."),
            ("Worker Telemetry", "HTML", worker_hint, "Live Codex runner status, phase, proof gate, and public artifacts."),
            ("Cockpit Login", "AUTH", login_hint, "Permission-token or Google account entry for protected pages."),
            ("Status JSON", "JSON", status_hint, "Connector audit posture for automated checks."),
            ("Health JSON", "JSON", health_hint, "Readiness endpoint for local preview and tunnel checks."),
        ]
    )
    project_cards = "\n".join(
        (
            '<a class="project-card" href="{href}" target="{target}" rel="{rel}">'
            '<span>{kind}</span>'
            '<b>{label}</b>'
            '<p>{summary}</p>'
            '<code>{surface}</code>'
            '</a>'
        ).format(
            href=_html_text(href),
            target="_blank" if external else "_self",
            rel="noreferrer" if external else "",
            kind=_html_text(kind),
            label=_html_text(label),
            summary=_html_text(summary),
            surface=_html_text(surface),
        )
        for label, kind, href, surface, summary, external in [
            (
                "Cosmos Water World",
                "LIVE WORKBENCH",
                f"{base}/projects/cosmos" if base else "/projects/cosmos",
                "Helixion live preview",
                "Local Cosmos renderer embedded through Helixion with gated diffs, actions, receipts, and rollback.",
                False,
            ),
            (
                "Cosmos Review",
                "LIVE REVIEW",
                f"{base}/projects/cosmos/preview/cosmos-review?bookmark=orbit&panel=1" if base else "/projects/cosmos/preview/cosmos-review?bookmark=orbit&panel=1",
                "proxied local review bookmarks",
                "Direct Helixion preview entry for lead-eyes critique of the current Cosmos image stack.",
                False,
            ),
            (
                "Helixion Operator Cockpit",
                "PROTECTED",
                cockpit_hint,
                "/cockpit",
                "Public protected cockpit route for runtime, queues, services, receipts, and authority state.",
                False,
            ),
            (
                "Codex Capsule Chat",
                "PROTECTED",
                chat_hint,
                "/cockpit/chat",
                "Capsule-backed operator chat surface with bounded queue controls and receipts.",
                False,
            ),
            (
                "Local JOC Cockpit",
                "LOCAL NUMBER",
                "http://127.0.0.1:8788/",
                "127.0.0.1:8788",
                "The local machine cockpit address. This only opens on the computer running ION.",
                True,
            ),
            (
                "ION MCP Preview",
                "LOCAL + TUNNEL",
                connector_hint,
                "127.0.0.1:8765 -> ion.helixion.net",
                "Human landing page here; MCP tool calls remain on the /mcp endpoint.",
                False,
            ),
            (
                "Action Gateway",
                "PUBLIC HEALTH",
                "https://ion-actions.helixion.net/health",
                "127.0.0.1:8777 -> ion-actions.helixion.net",
                "Custom GPT Actions health endpoint for bounded gateway checks.",
                True,
            ),
            (
                "dAimon / WisdomNET Line",
                "CANDIDATE",
                cockpit_hint,
                "JOC project lane",
                "Companion, browser extension, project/package, and federation work surfaces inside ION.",
                False,
            ),
        ]
    )
    local_port_cards = "\n".join(
        (
            '<article class="port-card">'
            '<span>{port}</span>'
            '<b>{label}</b>'
            '<p>{summary}</p>'
            '<code>{route}</code>'
            '</article>'
        ).format(
            port=_html_text(port),
            label=_html_text(label),
            summary=_html_text(summary),
            route=_html_text(route),
        )
        for port, label, route, summary in [
            ("8765", "ION site and MCP preview", "127.0.0.1:8765 / ion.helixion.net", "Root page, /app, /projects, /health, and /mcp."),
            ("8788", "Local JOC cockpit", "127.0.0.1:8788", "Local-only React cockpit for ION/JOC service visibility."),
            ("8777", "Action Gateway", "127.0.0.1:8777 / ion-actions.helixion.net", "Custom GPT Actions gateway and health route."),
            ("8767", "ChatOps daemon", "127.0.0.1:8767", "Local bridge health and routing visibility."),
            ("8795", "dAimon bridge", "127.0.0.1:8795", "Reserved local websocket bridge for the dAimon companion line."),
        ]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>ION Connector</title>
  <style>
    {HELIXION_SITE_CSS}
    :root {{
      color-scheme: dark;
      --bg: #101112;
      --panel: #181a1b;
      --line: #303336;
      --text: #f4f4f2;
      --muted: #a8a8a1;
      --ok: #20d88f;
      --warn: #ff9f43;
      --accent: #ff7a1a;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    main {{
      max-width: 1040px;
      margin: 0 auto;
      padding: 30px 22px 56px;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      padding-bottom: 22px;
      margin-bottom: 22px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: clamp(24px, 4vw, 40px);
      line-height: 1;
      letter-spacing: 0;
      text-transform: uppercase;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 18px;
      letter-spacing: 0;
    }}
    p {{ color: var(--muted); max-width: 760px; }}
    code {{
      background: #0b0c0d;
      border: 1px solid #26292b;
      border-radius: 2px;
      color: #f5d0b4;
      padding: 2px 5px;
      overflow-wrap: anywhere;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 2px;
      padding: 16px;
    }}
    .status {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      max-width: 100%;
      padding: 6px 10px;
      border: 1px solid var(--line);
      border-radius: 2px;
      color: var(--muted);
      font-size: 13px;
      text-transform: uppercase;
    }}
    .status span:last-child {{
      min-width: 0;
      overflow-wrap: anywhere;
    }}
    .dot {{
      width: 9px;
      height: 9px;
      border-radius: 999px;
      background: var(--warn);
      box-shadow: 0 0 14px rgba(255, 159, 67, 0.42);
    }}
    .status.ready .dot {{
      background: var(--ok);
      box-shadow: 0 0 14px rgba(32, 216, 143, 0.42);
    }}
    .status.blocked .dot {{
      background: #ff6565;
      box-shadow: 0 0 14px rgba(255, 101, 101, 0.42);
    }}
    .laws {{
      display: grid;
      gap: 8px;
      margin: 14px 0 0;
      padding: 0;
      list-style: none;
    }}
    .laws li {{
      border-left: 2px solid var(--accent);
      padding-left: 10px;
      color: var(--muted);
    }}
    .tools {{
      columns: 2;
      padding-left: 18px;
      color: var(--muted);
    }}
    .route-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
      margin: 18px 0 22px;
    }}
    .route-card {{
      display: grid;
      gap: 7px;
      min-height: 128px;
      padding: 13px;
      border: 1px solid var(--line);
      border-radius: 2px;
      background: #0d1113;
      color: var(--text);
      text-decoration: none;
    }}
    .route-card:hover,
    .route-card:focus-visible {{
      border-color: var(--accent);
      outline: none;
    }}
    .route-card span {{
      color: var(--accent);
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    .route-card b {{
      font-size: 14px;
      text-transform: uppercase;
    }}
    .route-card p {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
    }}
    .project-header {{
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 16px;
      margin: 28px 0 12px;
      padding-top: 18px;
      border-top: 1px solid var(--line);
    }}
    .project-header h2 {{
      margin: 0;
      color: var(--text);
      font-size: 22px;
      text-transform: uppercase;
    }}
    .project-header p {{
      margin: 6px 0 0;
      max-width: 660px;
    }}
    .canon-strip {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin: 16px 0 10px;
      padding: 6px 10px;
      border: 1px solid #425a62;
      border-radius: 2px;
      background: #10181b;
      color: #b8f7ff;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    .canon-metrics {{
      display: grid;
      grid-template-columns: repeat(9, minmax(0, 1fr));
      gap: 8px;
      margin: 12px 0 22px;
    }}
    .canon-metric {{
      min-height: 82px;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 2px;
      background: #101315;
    }}
    .canon-metric span {{
      display: block;
      min-height: 26px;
      color: var(--muted);
      font-size: 10px;
      font-weight: 800;
      line-height: 1.2;
      text-transform: uppercase;
    }}
    .canon-metric b {{
      display: block;
      margin-top: 7px;
      color: var(--text);
      font-size: 23px;
      line-height: 1;
    }}
    .canon-layout {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 320px;
      gap: 14px;
      margin-bottom: 22px;
    }}
    .canon-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }}
    .canon-grid.families {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }}
    .canon-card {{
      display: grid;
      gap: 8px;
      min-height: 162px;
      padding: 13px;
      border: 1px solid var(--line);
      border-radius: 2px;
      background: #0d1113;
      color: var(--text);
      text-decoration: none;
    }}
    .canon-family-card:hover,
    .canon-family-card:focus-visible {{
      border-color: #84f0d0;
      outline: none;
    }}
    .canon-card.compact {{
      min-height: 132px;
    }}
    .canon-card span {{
      color: #84f0d0;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    .canon-card b {{
      color: var(--text);
      font-size: 15px;
      text-transform: uppercase;
    }}
    .canon-card p {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
    }}
    .canon-stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: auto;
    }}
    .canon-path {{
      display: block;
      margin-top: 2px;
    }}
    .canon-open {{
      align-self: end;
      color: #f2c7a7;
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    .canon-list {{
      display: grid;
      gap: 8px;
      margin: 0;
      padding: 0;
      list-style: none;
    }}
    .canon-list li {{
      display: grid;
      gap: 3px;
      padding: 10px;
      border-left: 2px solid #7ce7ff;
      background: #111719;
    }}
    .canon-list b {{
      color: var(--text);
      font-size: 13px;
      text-transform: uppercase;
    }}
    .canon-list span {{
      color: var(--muted);
      font-size: 12px;
    }}
    .project-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 22px;
    }}
    .project-card,
    .port-card {{
      display: grid;
      gap: 8px;
      min-height: 170px;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 2px;
      background:
        linear-gradient(180deg, rgba(255, 122, 26, 0.08), rgba(13, 17, 19, 0) 52%),
        #0d1113;
      color: var(--text);
      text-decoration: none;
    }}
    .project-card:hover,
    .project-card:focus-visible {{
      border-color: var(--accent);
      outline: none;
    }}
    .project-card span,
    .port-card span {{
      color: #f2c7a7;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    .project-card b,
    .port-card b {{
      font-size: 15px;
      text-transform: uppercase;
    }}
    .project-card p,
    .port-card p {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
    }}
    .port-grid {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 10px;
      margin: 0 0 24px;
    }}
    .port-card {{
      min-height: 142px;
      background: #111517;
    }}
    @media (max-width: 760px) {{
      .grid {{ grid-template-columns: 1fr; }}
      .route-grid {{ grid-template-columns: 1fr; }}
      .project-header {{ display: block; }}
      .canon-metrics,
      .canon-layout,
      .canon-grid,
      .canon-grid.families {{
        grid-template-columns: 1fr;
      }}
      .project-grid,
      .port-grid {{ grid-template-columns: 1fr; }}
      .tools {{ columns: 1; }}
      main {{ padding-top: 28px; }}
    }}
    @media (min-width: 761px) and (max-width: 1100px) {{
      .canon-metrics {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
      .canon-layout {{ grid-template-columns: 1fr; }}
      .canon-grid.families {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .project-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .port-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
  </style>
</head>
<body>
  {render_helixion_site_bar(active_nav, public_base_url=base)}
  <main>
    <header>
      <div class="status {status_class}"><span class="dot"></span><span>{_html_text(audit.get("verdict"))}</span></div>
      <h1>ION Connector</h1>
      <p>A bounded browser-carrier surface for ION. This page is a status/UI landing surface; MCP tools remain on <code>{_html_text(connector_hint)}</code>.</p>
    </header>
    <section aria-label="HelixION project canon">
      <div class="project-header">
        <div>
          <span class="canon-strip">Project canon · {_html_text(project_surface_state)}</span>
          <h2>Main ION Project System</h2>
          <p>Canonical project visibility for the Helixion URL app: domains, families, versions, docs, launch posture, proof lanes, agent roles, context capsules, and future plans. Local filesystem references remain redacted from this public surface.</p>
        </div>
        <code>/projects/portfolio.json</code>
      </div>
      <div class="canon-metrics">
        {canon_metrics}
      </div>
      <div class="canon-layout">
        <div>
          <h2>Canonical Domains</h2>
          <div class="canon-grid">
            {canon_domain_cards or '<article class="canon-card"><span>unavailable</span><b>No domain model</b><p>Portfolio manifest is not available to this process.</p></article>'}
          </div>
        </div>
        <aside class="canon-card">
          <span>authority boundary</span>
          <b>{_html_text(canon_contract.get("address_space"))}</b>
          <p>{_html_text(canon_contract.get("local_path_policy"))}</p>
          <p>{_html_text(canon_contract.get("management_rule"))}</p>
          <div class="canon-stats">
            <code>visible {_html_text(access_summary.get("visible_object_count", 0))}</code>
            <code>hidden {_html_text(access_summary.get("hidden_object_count", 0))}</code>
            <code>paths {_html_text(access_summary.get("path_inspection_allowed", False))}</code>
          </div>
        </aside>
      </div>
      <h2>Featured Families</h2>
      <div class="canon-grid families">
        {canon_family_cards or '<article class="canon-card"><span>unavailable</span><b>No family model</b><p>Portfolio manifest is not available to this process.</p></article>'}
      </div>
      <div class="canon-layout">
        <div>
          <h2>Agents In The System</h2>
          <div class="canon-grid">
            {canon_agent_cards or '<article class="canon-card compact"><span>unavailable</span><b>No agent model</b><p>Project surface builder did not return agent roles.</p></article>'}
          </div>
        </div>
        <aside>
          <h2>Timeline Axes</h2>
          <ul class="canon-list">{canon_axis_items or '<li><b>Unavailable</b><span>No timeline axes returned.</span></li>'}</ul>
          <h2>Future Lanes</h2>
          <ul class="canon-list">{canon_future_items or '<li><b>Unavailable</b><span>No future lanes returned.</span></li>'}</ul>
        </aside>
      </div>
    </section>
    <section aria-label="ION Operations project directory">
      <div class="project-header">
        <div>
          <h2>Projects Hub</h2>
          <p>Public apps, protected ION cockpit routes, and the local number-address surfaces are gathered here so the main HelixION page is the front door.</p>
        </div>
        <code>{_html_text(projects_hint)}</code>
      </div>
      <div class="project-grid">
        {project_cards}
      </div>
      <div class="port-grid" aria-label="Local port map">
        {local_port_cards}
      </div>
    </section>
    <nav class="route-grid" aria-label="HelixION route directory">
      {route_cards}
    </nav>
    <section class="grid" aria-label="connector summary">
      <article class="card">
        <h2>Current Surface</h2>
        <p>Endpoint path: <code>{_html_text(audit.get("endpoint_path"))}</code></p>
        <p>Health JSON: <code>{_html_text(health_hint)}</code></p>
        <p>Worker telemetry: <code>{_html_text(worker_hint)}</code></p>
        <p>Write confirmation required: <code>{_html_text(audit.get("write_confirmation_required"))}</code></p>
      </article>
      <article class="card">
        <h2>Authority Boundary</h2>
        <ul class="laws">
          <li>Production authority: <code>{_html_text(audit.get("production_authority"))}</code></li>
          <li>Live execution authority: <code>{_html_text(audit.get("live_execution_authority"))}</code></li>
          <li>Deployment authority: <code>{_html_text(audit.get("deployment_authority"))}</code></li>
        </ul>
      </article>
      <article class="card">
        <h2>Allowed MCP Tools</h2>
        <ul class="tools">{tool_items}</ul>
      </article>
      <article class="card">
        <h2>Blocked Capabilities</h2>
        <ul class="tools">{forbidden_items}</ul>
        <h2>Findings</h2>
        <ul>{finding_items}</ul>
      </article>
    </section>
  </main>
</body>
</html>
"""


def render_helixion_project_family_detail(
    root: str | Path,
    family_id: str,
    *,
    public_base_url: str | None = None,
) -> str:
    """Render one canonical project family detail page from the redacted surface model."""

    base = (public_base_url or "").rstrip("/")
    detail = build_helixion_project_family_detail_model_from_file(root, family_id)
    family = detail.get("family") if isinstance(detail.get("family"), Mapping) else {}
    current = family.get("current") if isinstance(family.get("current"), Mapping) else {}
    preview = detail.get("preview_capability") if isinstance(detail.get("preview_capability"), Mapping) else {}
    workbench = detail.get("workbench_summary") if isinstance(detail.get("workbench_summary"), Mapping) else {}
    proof_summary = detail.get("proof_summary") if isinstance(detail.get("proof_summary"), Mapping) else {}
    canon_contract = detail.get("project_canon_contract") if isinstance(detail.get("project_canon_contract"), Mapping) else {}
    preview_href = _html_text(preview.get("preview_href") or "/projects")
    embed_src = _html_text(preview.get("embed_src") or "")
    status_class = "ready" if preview.get("capability") in {"embedded_workbench", "managed_launch"} else "watch"

    def _detail_metric(label: str, value: Any) -> str:
        return (
            '<article class="family-metric">'
            f"<span>{_html_text(label)}</span>"
            f"<b>{_html_text(value if value not in {None, ''} else 0)}</b>"
            "</article>"
        )

    metrics = "\n".join(
        [
            _detail_metric("Versions", family.get("version_count")),
            _detail_metric("Diffs", family.get("diff_count")),
            _detail_metric("Launchable", family.get("launchable_count")),
            _detail_metric("Docs", family.get("doc_count")),
            _detail_metric("Proof pass", proof_summary.get("pass_count")),
            _detail_metric("Proof watch", proof_summary.get("watch_count")),
        ]
    )

    lens_cards = "\n".join(
        (
            '<article class="family-card">'
            f'<span>{_html_text(lens.get("label"))}</span>'
            f'<b>{_html_text(lens.get("wants"))}</b>'
            f'<p>{_html_text(lens.get("surface"))}</p>'
            "</article>"
        )
        for lens in [item for item in (detail.get("audience_lenses") or []) if isinstance(item, Mapping)]
    )

    version_cards = "\n".join(
        (
            '<article class="version-row">'
            '<div>'
            f'<span>{_html_text(version.get("sequence_label") or version.get("version_id"))}</span>'
            f'<b>{_html_text(version.get("display_label"))}</b>'
            f'<p>{_html_text(version.get("stack") or "stack unknown")} / {_html_text((version.get("docs") or {}).get("doc_count") if isinstance(version.get("docs"), Mapping) else 0)} docs</p>'
            '</div>'
            '<div class="family-tags">'
            f'<code>{"current" if version.get("is_current") else "lineage"}</code>'
            f'<code>{"launchable" if version.get("launchable") else "catalog"}</code>'
            f'<code>{_html_text(version.get("virtual_path"))}</code>'
            '</div>'
            "</article>"
        )
        for version in [item for item in (detail.get("versions") or []) if isinstance(item, Mapping)]
    )

    diff_cards = "\n".join(
        (
            '<article class="diff-row">'
            '<div>'
            f'<span>{_html_text(diff.get("status"))}</span>'
            f'<b>{_html_text(diff.get("diff_id"))}</b>'
            f'<p>{_html_text(diff.get("from_label") or diff.get("from_project_id"))} -> {_html_text(diff.get("to_label") or diff.get("to_project_id"))}</p>'
            '</div>'
            '<div class="diff-counts">'
            f'<code>+{_html_text(diff.get("added_count", 0))}</code>'
            f'<code>~{_html_text(diff.get("changed_count", 0))}</code>'
            f'<code>-{_html_text(diff.get("removed_count", 0))}</code>'
            '</div>'
            '<div class="diff-samples">'
            f'<span>{_html_text(", ".join((diff.get("changed_sample") or [])[:4]) or "no changed sample")}</span>'
            f'<span>{_html_text(", ".join((diff.get("removed_sample") or [])[:3]) or "no removed sample")}</span>'
            '</div>'
            "</article>"
        )
        for diff in [item for item in (detail.get("diffs") or []) if isinstance(item, Mapping)]
    )

    proof_cards = "\n".join(
        (
            f'<article class="proof-row {("pass" if proof.get("status") == "pass" else "watch")}">'
            f'<span>{_html_text(proof.get("status"))}</span>'
            f'<b>{_html_text(proof.get("label"))}</b>'
            f'<p>{_html_text(proof.get("evidence"))}</p>'
            "</article>"
        )
        for proof in [item for item in (detail.get("proof_ladder") or []) if isinstance(item, Mapping)]
    )

    future_cards = "\n".join(
        (
            '<article class="family-card compact">'
            f'<span>{_html_text(lane.get("status"))}</span>'
            f'<b>{_html_text(lane.get("label"))}</b>'
            f'<p>{_html_text(lane.get("objective"))}</p>'
            f'<code>{_html_text(lane.get("next_action"))}</code>'
            "</article>"
        )
        for lane in [item for item in (detail.get("future_plan_lanes") or []) if isinstance(item, Mapping)]
    )

    workbench_counts = workbench.get("history_counts") if isinstance(workbench.get("history_counts"), Mapping) else {}
    preview_body = (
        f'<iframe class="project-preview-frame" src="{embed_src}" title="Embedded project preview"></iframe>'
        if embed_src
        else (
            '<div class="preview-placeholder">'
            f'<b>{_html_text(preview.get("label"))}</b>'
            f'<p>{_html_text(preview.get("summary"))}</p>'
            f'<a href="{preview_href}">Open preview surface</a>'
            "</div>"
        )
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>Project Family - {_html_text(family.get("label") or family_id)}</title>
  <style>
    {HELIXION_SITE_CSS}
    :root {{
      color-scheme: dark;
      --bg: #101112;
      --panel: #151819;
      --panel-2: #0d1113;
      --line: #303336;
      --text: #f4f4f2;
      --muted: #aaa8a1;
      --accent: #ff7a1a;
      --cyan: #7ce7ff;
      --green: #20d88f;
      --warn: #ffb057;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px 22px 58px;
    }}
    a {{ color: inherit; }}
    header {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 280px;
      gap: 18px;
      align-items: end;
      margin-bottom: 18px;
      padding-bottom: 18px;
      border-bottom: 1px solid var(--line);
    }}
    h1 {{
      margin: 8px 0;
      font-size: clamp(28px, 5vw, 54px);
      line-height: .94;
      letter-spacing: 0;
      text-transform: uppercase;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 18px;
      text-transform: uppercase;
    }}
    p {{
      margin: 0;
      color: var(--muted);
      max-width: 780px;
    }}
    code {{
      max-width: 100%;
      overflow-wrap: anywhere;
      border: 1px solid #2d3336;
      border-radius: 2px;
      background: #0a0d0e;
      color: #f5d0b4;
      padding: 2px 5px;
    }}
    .back-link,
    .primary-link {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 34px;
      padding: 7px 10px;
      border: 1px solid var(--line);
      border-radius: 2px;
      background: var(--panel-2);
      color: var(--text);
      font-size: 12px;
      font-weight: 800;
      text-decoration: none;
      text-transform: uppercase;
    }}
    .primary-link {{
      border-color: var(--accent);
      color: #ffd6b7;
    }}
    .status-pill {{
      display: inline-flex;
      align-items: center;
      width: fit-content;
      max-width: 100%;
      gap: 8px;
      padding: 6px 10px;
      border: 1px solid var(--line);
      border-radius: 2px;
      background: #121719;
      color: var(--muted);
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    .status-pill::before {{
      content: "";
      width: 9px;
      height: 9px;
      border-radius: 999px;
      background: var(--warn);
    }}
    .status-pill.ready::before {{ background: var(--green); }}
    .status-pill.watch::before {{ background: var(--warn); }}
    .header-actions {{
      display: grid;
      gap: 8px;
      justify-items: stretch;
    }}
    .family-metrics {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 8px;
      margin: 14px 0 18px;
    }}
    .family-metric {{
      min-height: 82px;
      padding: 10px;
      border: 1px solid var(--line);
      border-radius: 2px;
      background: var(--panel-2);
    }}
    .family-metric span {{
      display: block;
      min-height: 24px;
      color: var(--muted);
      font-size: 10px;
      font-weight: 800;
      line-height: 1.15;
      text-transform: uppercase;
    }}
    .family-metric b {{
      display: block;
      margin-top: 7px;
      font-size: 25px;
      line-height: 1;
    }}
    .family-grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(320px, .65fr);
      gap: 14px;
      margin: 14px 0;
    }}
    .family-card,
    .preview-panel,
    .version-row,
    .diff-row,
    .proof-row {{
      border: 1px solid var(--line);
      border-radius: 2px;
      background: var(--panel);
    }}
    .family-card {{
      display: grid;
      gap: 8px;
      min-height: 138px;
      padding: 13px;
    }}
    .family-card.compact {{
      min-height: 118px;
    }}
    .family-card span,
    .version-row span,
    .diff-row span,
    .proof-row span {{
      display: block;
      color: var(--cyan);
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      font-size: 10px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    .family-card b,
    .version-row b,
    .diff-row b,
    .proof-row b {{
      display: block;
      color: var(--text);
      font-size: 14px;
      text-transform: uppercase;
    }}
    .version-row p,
    .diff-row p {{
      margin-top: 5px;
    }}
    .lens-grid,
    .future-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }}
    .preview-panel {{
      display: grid;
      gap: 10px;
      min-height: 360px;
      padding: 12px;
      background: #0c1012;
    }}
    .project-preview-frame {{
      width: 100%;
      min-height: 420px;
      border: 1px solid #26353b;
      border-radius: 2px;
      background: #050607;
    }}
    .preview-placeholder {{
      display: grid;
      place-content: center;
      gap: 10px;
      min-height: 320px;
      padding: 24px;
      border: 1px dashed #39454a;
      background: #101517;
      text-align: left;
    }}
    .preview-placeholder a {{
      width: fit-content;
      padding: 8px 10px;
      border: 1px solid var(--accent);
      border-radius: 2px;
      color: #ffd6b7;
      font-size: 12px;
      font-weight: 800;
      text-decoration: none;
      text-transform: uppercase;
    }}
    .version-list,
    .diff-list,
    .proof-grid {{
      display: grid;
      gap: 8px;
    }}
    .version-row,
    .diff-row {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: start;
      padding: 12px;
    }}
    .diff-row {{
      grid-template-columns: minmax(0, 1fr) auto;
    }}
    .diff-samples {{
      grid-column: 1 / -1;
      display: grid;
      gap: 4px;
      color: var(--muted);
      font-size: 12px;
    }}
    .family-tags,
    .diff-counts {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      justify-content: flex-end;
    }}
    .proof-grid {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }}
    .proof-row {{
      display: grid;
      gap: 6px;
      min-height: 120px;
      padding: 12px;
      border-left: 3px solid var(--warn);
    }}
    .proof-row.pass {{
      border-left-color: var(--green);
    }}
    .authority-box {{
      display: grid;
      gap: 8px;
      padding: 12px;
      border: 1px solid #425a62;
      border-radius: 2px;
      background: #10181b;
    }}
    @media (max-width: 860px) {{
      main {{ padding-top: 24px; }}
      header,
      .family-grid,
      .lens-grid,
      .future-grid,
      .proof-grid {{
        grid-template-columns: 1fr;
      }}
      .family-metrics {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
      .version-row,
      .diff-row {{
        grid-template-columns: 1fr;
      }}
      .family-tags,
      .diff-counts {{
        justify-content: flex-start;
      }}
      .project-preview-frame {{
        min-height: 300px;
      }}
    }}
    @media (min-width: 861px) and (max-width: 1120px) {{
      .family-metrics {{
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }}
      .family-grid,
      .proof-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  {render_helixion_site_bar("projects", public_base_url=base)}
  <main>
    <header>
      <div>
        <a class="back-link" href="/projects">Back to projects</a>
        <h1>{_html_text(family.get("label") or family_id)}</h1>
        <p>Project Family command center for versions, diffs, docs, launch posture, proof, context capsules, agent lanes, and future plans.</p>
      </div>
      <div class="header-actions">
        <span class="status-pill {status_class}">{_html_text(preview.get("capability"))}</span>
        <a class="primary-link" href="{preview_href}">{_html_text(preview.get("label") or "Open preview")}</a>
        <code>{_html_text(family.get("virtual_path"))}</code>
      </div>
    </header>
    <section class="family-metrics" aria-label="Project family metrics">
      {metrics}
    </section>
    <section class="family-grid" aria-label="Project preview and audience lenses">
      <div>
        <h2>Audience Lenses</h2>
        <div class="lens-grid">
          {lens_cards}
        </div>
      </div>
      <aside class="authority-box">
        <span class="status-pill watch">Authority</span>
        <b>{_html_text(canon_contract.get("address_space"))}</b>
        <p>{_html_text(canon_contract.get("local_path_policy"))}</p>
        <p>{_html_text(canon_contract.get("preview_rule"))}</p>
      </aside>
    </section>
    <section class="family-grid" aria-label="Advanced preview">
      <div>
        <h2>Advanced Preview</h2>
        <div class="preview-panel">
          {preview_body}
        </div>
      </div>
      <aside class="authority-box">
        <span class="status-pill {status_class}">Preview Capability</span>
        <b>{_html_text(preview.get("label"))}</b>
        <p>{_html_text(preview.get("summary"))}</p>
        <code>patches {_html_text(workbench_counts.get("patch_receipt_count", 0))}</code>
        <code>captures {_html_text(workbench_counts.get("browser_capture_count", 0))}</code>
        <code>rollback {_html_text(workbench_counts.get("rollback_candidate_count", 0))}</code>
      </aside>
    </section>
    <section class="family-grid" aria-label="Version timeline and diff evolution">
      <div>
        <h2>Version Timeline</h2>
        <div class="version-list">
          {version_cards or '<article class="version-row"><div><span>empty</span><b>No versions</b><p>No versions are attached to this family.</p></div></article>'}
        </div>
      </div>
      <div>
        <h2>Diff Evolution</h2>
        <div class="diff-list">
          {diff_cards or '<article class="diff-row"><div><span>empty</span><b>No diffs</b><p>No adjacent diff manifests are attached yet.</p></div></article>'}
        </div>
      </div>
    </section>
    <section aria-label="Proof ladder">
      <h2>Proof Ladder</h2>
      <div class="proof-grid">
        {proof_cards}
      </div>
    </section>
    <section class="family-grid" aria-label="Context and future plans">
      <div>
        <h2>Future Plan Lanes</h2>
        <div class="future-grid">
          {future_cards}
        </div>
      </div>
      <aside class="authority-box">
        <span class="status-pill watch">Context Capsule</span>
        <b>{_html_text((detail.get("context_capsule_lane") or {}).get("label") if isinstance(detail.get("context_capsule_lane"), Mapping) else "Context Capsule Lane")}</b>
        <p>{_html_text((detail.get("context_capsule_lane") or {}).get("contract") if isinstance(detail.get("context_capsule_lane"), Mapping) else "")}</p>
        <code>{_html_text(current.get("display_label"))}</code>
      </aside>
    </section>
  </main>
</body>
</html>
"""


def render_project_workbench_html(
    root: str | Path,
    *,
    public_base_url: str | None = None,
    auth_token: str | None = None,
    authenticated: bool = False,
    project_id: str = "cosmos",
    action_result: Mapping[str, Any] | None = None,
) -> str:
    """Render the Helixion-hosted project workbench.

    The preview is intentionally public. Mutation controls are rendered only
    when the existing cockpit auth/session is present.
    """

    base = (public_base_url or "").rstrip("/")
    status = build_project_workspace_status(root, project_id=project_id, probe_preview=True)
    project = status.get("project") if isinstance(status.get("project"), Mapping) else {}
    preview = status.get("preview") if isinstance(status.get("preview"), Mapping) else {}
    git_status = status.get("git_status") if isinstance(status.get("git_status"), Mapping) else {}
    receipts = status.get("latest_patch_receipts") if isinstance(status.get("latest_patch_receipts"), list) else []
    browser_captures = status.get("latest_browser_captures") if isinstance(status.get("latest_browser_captures"), list) else []
    preview_src = "/projects/cosmos/preview/"
    login_href = "/cockpit/login?" + urlencode({"next": "/projects/cosmos"})
    _ = auth_token
    action_cards = []
    for action_id, label in [
        ("screenshots", "Capture screenshots"),
        ("build", "Build"),
        ("test", "Test"),
        ("lint", "Lint"),
        ("gibs_snapshot", "GIBS snapshot"),
    ]:
        action_cards.append(
            (
                '<form method="post" action="/projects/cosmos/actions/run" class="workbench-action">'
                f'<input type="hidden" name="confirmation" value="{_html_text(PROJECT_WRITE_CONFIRMATION_TOKEN)}">'
                f'<input type="hidden" name="project_id" value="{_html_text(project_id)}">'
                f'<input type="hidden" name="action_id" value="{_html_text(action_id)}">'
                f'<button type="submit">{_html_text(label)}</button>'
                "</form>"
            )
        )
    action_cards.append(
        (
            '<form method="post" action="/projects/cosmos/browser/capture" class="workbench-action">'
            f'<input type="hidden" name="confirmation" value="{_html_text(PROJECT_WRITE_CONFIRMATION_TOKEN)}">'
            f'<input type="hidden" name="project_id" value="{_html_text(project_id)}">'
            '<input type="hidden" name="bookmark" value="orbit">'
            '<input type="hidden" name="interaction" value="none">'
            '<button type="submit">Browser capture orbit</button>'
            "</form>"
        )
    )
    protected_controls = (
        '<div class="protected-grid">' + "".join(action_cards) + "</div>"
        if authenticated
        else f'<a class="login-card" href="{_html_text(login_href)}">Login to run builds, capture screenshots, apply diffs, and rollback patches.</a>'
    )
    action_result_card = ""
    if action_result:
        result_data = action_result.get("data") if isinstance(action_result.get("data"), Mapping) else {}
        artifact_path = result_data.get("log_path") or result_data.get("screenshot_path") or result_data.get("receipt_path") or ""
        action_result_card = (
            '<article class="result-card">'
            f'<span>ACTION RESULT</span><b>{_html_text(result_data.get("action_id") or result_data.get("bookmark") or action_result.get("tool") or "project action")}</b>'
            f'<p>ok: <code>{_html_text(action_result.get("ok"))}</code> return: <code>{_html_text(result_data.get("returncode"))}</code></p>'
            f'<p>artifact: <code>{_html_text(artifact_path)}</code></p>'
            "</article>"
        )
    route_links = "\n".join(
        f'<a href="{_html_text(href)}" target="cosmos-preview">{_html_text(label)}</a>'
        for label, href in [
            ("Home", "/projects/cosmos/preview/"),
            ("Projects", "/projects/cosmos/preview/projects"),
            ("Application Dev", "/projects/cosmos/preview/projects/application-dev"),
            ("Cosmos Project", "/projects/cosmos/preview/projects/cosmos"),
            ("Lab", "/projects/cosmos/preview/lab"),
            ("Orbit", "/projects/cosmos/preview/cosmos-review?bookmark=orbit&panel=1"),
            ("Cloud terminator", "/projects/cosmos/preview/cosmos-review?bookmark=cloud-terminator&panel=1"),
            ("High altitude", "/projects/cosmos/preview/cosmos-review?bookmark=high-altitude&panel=1"),
            ("Storm", "/projects/cosmos/preview/cosmos-review?bookmark=storm-zone&panel=1"),
            ("Sun glitter", "/projects/cosmos/preview/cosmos-review?bookmark=sun-glitter&panel=1"),
            ("Sea level", "/projects/cosmos/preview/cosmos-review?bookmark=sea-level&panel=1"),
            ("Underwater", "/projects/cosmos/preview/cosmos-review?bookmark=underwater&panel=1"),
        ]
    )
    receipt_cards = "\n".join(
        (
            '<article class="mini-card">'
            f'<span>{_html_text(item.get("action") or "patch")}</span>'
            f'<b>{_html_text(item.get("status") or "receipt")}</b>'
            f'<code>{_html_text(item.get("path") or "")}</code>'
            "</article>"
        )
        for item in receipts[:6]
        if isinstance(item, Mapping)
    ) or '<div class="empty">No project patch receipts yet.</div>'
    browser_capture_cards = "\n".join(
        (
            '<article class="mini-card">'
            f'<span>{_html_text(item.get("bookmark") or "browser")}</span>'
            f'<b>{_html_text(item.get("status") or "capture")}</b>'
            f'<code>{_html_text(item.get("screenshot_path") or item.get("path") or "")}</code>'
            "</article>"
        )
        for item in browser_captures[:6]
        if isinstance(item, Mapping)
    ) or '<div class="empty">No browser captures yet.</div>'
    git_lines = "\n".join(f"<li><code>{_html_text(line)}</code></li>" for line in list(git_status.get("lines") or [])[:28])
    if not git_lines:
        git_lines = "<li><code>no git status lines projected</code></li>"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>Helixion Projects - Cosmos Workbench</title>
  <style>
    {HELIXION_SITE_CSS}
    :root {{
      color-scheme: dark;
      --bg: #090b0c;
      --panel: #121619;
      --panel-2: #171d20;
      --line: #2c3439;
      --text: #f3f0ea;
      --muted: #9da8ad;
      --accent: #f28b33;
      --ok: #29d391;
      --warn: #e4b247;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--text); }}
    main {{ min-height: calc(100vh - 43px); display: grid; grid-template-rows: auto 1fr; }}
    header {{ display: flex; align-items: end; justify-content: space-between; gap: 18px; padding: 18px; border-bottom: 1px solid var(--line); background: #0d1113; }}
    h1 {{ margin: 0; font-size: clamp(24px, 4vw, 42px); line-height: 1; text-transform: uppercase; }}
    p {{ color: var(--muted); }}
    code {{ overflow-wrap: anywhere; color: #ffd3b1; }}
    .status-pill {{ border: 1px solid var(--line); padding: 7px 10px; color: var(--muted); text-transform: uppercase; font-size: 12px; }}
    .layout {{ min-height: 0; display: grid; grid-template-columns: minmax(0, 1fr) 360px; }}
    .preview-zone {{ min-width: 0; min-height: 0; display: grid; grid-template-rows: auto 1fr; }}
    .route-bar {{ display: flex; gap: 8px; overflow-x: auto; padding: 10px; border-bottom: 1px solid var(--line); background: #101518; }}
    .route-bar a, .route-bar button, .login-card, .workbench-action button {{ border: 1px solid var(--line); background: #0d1113; color: var(--text); text-decoration: none; padding: 8px 10px; font-weight: 800; text-transform: uppercase; font-size: 11px; cursor: pointer; }}
    .route-bar a:hover, .route-bar button:hover, .login-card:hover, .workbench-action button:hover {{ border-color: var(--accent); }}
    iframe {{ width: 100%; height: 100%; min-height: 680px; border: 0; background: #000; }}
    aside {{ border-left: 1px solid var(--line); background: #0f1315; overflow: auto; padding: 12px; }}
    .panel {{ border: 1px solid var(--line); background: var(--panel); padding: 12px; margin-bottom: 12px; }}
    .panel h2 {{ margin: 0 0 8px; font-size: 13px; color: var(--muted); text-transform: uppercase; }}
    .kv {{ display: grid; gap: 6px; font-size: 13px; }}
    .kv div {{ display: grid; gap: 2px; }}
    .kv span, .mini-card span, .result-card span {{ color: var(--accent); font-size: 10px; font-weight: 900; text-transform: uppercase; }}
    .protected-grid {{ display: grid; gap: 8px; }}
    .workbench-action {{ margin: 0; }}
    .workbench-action button, .login-card {{ display: block; width: 100%; min-height: 40px; text-align: left; }}
    .mini-card, .result-card {{ display: grid; gap: 6px; border: 1px solid var(--line); background: var(--panel-2); padding: 10px; margin-top: 8px; }}
    .mini-card b, .result-card b {{ font-size: 12px; text-transform: uppercase; }}
    .empty {{ color: var(--muted); border: 1px dashed var(--line); padding: 10px; }}
    ul {{ margin: 0; padding-left: 18px; color: var(--muted); }}
    @media (max-width: 980px) {{
      header {{ display: block; }}
      .layout {{ grid-template-columns: 1fr; }}
      aside {{ border-left: 0; border-top: 1px solid var(--line); }}
      iframe {{ min-height: 560px; }}
    }}
  </style>
</head>
<body>
  {render_helixion_site_bar("projects", auth_token=auth_token, public_base_url=base)}
  <main>
    <header>
      <div>
        <h1>Cosmos Workbench</h1>
        <p>Live Helixion-hosted preview for the local Cosmos project, with approval-gated project actions and patch receipts.</p>
      </div>
      <div class="status-pill">preview: {_html_text(preview.get("status") or "unknown")}</div>
    </header>
    <section class="layout">
      <div class="preview-zone">
        <nav class="route-bar" aria-label="Cosmos preview routes">
          {route_links}
          <button type="button" onclick="document.querySelector('iframe').contentWindow.location.reload()">Reload preview</button>
        </nav>
        <iframe title="Cosmos live preview" name="cosmos-preview" src="{_html_text(preview_src)}"></iframe>
      </div>
      <aside aria-label="Cosmos workbench inspector">
        <section class="panel">
          <h2>Project</h2>
          <div class="kv">
            <div><span>root</span><code>{_html_text(project.get("root") or "")}</code></div>
            <div><span>preview</span><code>{_html_text(preview.get("local_url") or "")}</code></div>
            <div><span>public route</span><code>{_html_text(project.get("preview_public_path") or "/projects/cosmos")}</code></div>
            <div><span>app dev catalog</span><code>/projects/cosmos/preview/projects/application-dev</code></div>
            <div><span>app dev launcher</span><code>{_html_text(application_dev_launcher_url() + "/")}</code></div>
          </div>
        </section>
        <section class="panel">
          <h2>Protected Actions</h2>
          {protected_controls}
          {action_result_card}
        </section>
        <section class="panel">
          <h2>Git Status</h2>
          <ul>{git_lines}</ul>
        </section>
        <section class="panel">
          <h2>Patch Receipts</h2>
          {receipt_cards}
        </section>
        <section class="panel">
          <h2>Browser Captures</h2>
          {browser_capture_cards}
        </section>
        <section class="panel">
          <h2>Boundary</h2>
          <p>Public preview is enabled. Source edits, patch apply, rollback, screenshots, browser capture, build, test, and lint require cockpit auth plus explicit write confirmation.</p>
        </section>
      </aside>
    </section>
  </main>
</body>
</html>
"""


def _format_bool(value: Any) -> str:
    return "true" if bool(value) else "false"


def _format_seconds(value: Any) -> str:
    try:
        seconds = int(value)
    except (TypeError, ValueError):
        return "unknown"
    minutes, rem = divmod(max(seconds, 0), 60)
    if minutes:
        return f"{minutes}m {rem}s"
    return f"{rem}s"


def _worker_badge(value: Any) -> str:
    status = str(value or "unknown").strip() or "unknown"
    lowered = status.lower()
    kind = "neutral"
    if any(token in lowered for token in ("accept", "ready", "running", "active", "true")):
        kind = "ok"
    if any(token in lowered for token in ("block", "invalid", "fail", "defer", "false")):
        kind = "bad"
    if "template" in lowered or "timeout" in lowered:
        kind = "warn"
    return f'<span class="badge badge-{kind}">{_html_text(status)}</span>'


def _worker_active_rows(active: Mapping[str, Any]) -> str:
    rows = [
        ("status", _worker_badge(active.get("status"))),
        ("pid", _html_text(active.get("pid") or "none")),
        ("run_id", _html_text(active.get("run_id") or "none")),
        ("request_id", _html_text(active.get("request_id") or "none")),
        ("age", _html_text(_format_seconds(active.get("age_seconds")))),
        ("heartbeat", _html_text(active.get("heartbeat_at") or "none")),
        ("preview", _html_text(active.get("preferred_preview_target") or "none")),
        ("stale", _worker_badge(active.get("stale_active_reference_detected"))),
        ("zombie", _worker_badge(active.get("zombie_state_detected"))),
        ("next action", _html_text(active.get("next_recommended_action") or "none")),
    ]
    return "".join(
        f"<tr><th>{_html_text(label)}</th><td>{value}</td></tr>"
        for label, value in rows
    )


def _worker_latest_run_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "<tr><td colspan=\"9\">No recent worker runs.</td></tr>"
    rendered: list[str] = []
    for row in rows:
        rendered.append(
            "<tr>"
            f"<td>{_worker_badge(row.get('status') or row.get('terminal_state') or 'unknown')}</td>"
            f"<td><code>{_html_text(row.get('run_id') or 'none')}</code></td>"
            f"<td><code>{_html_text(row.get('request_id') or 'none')}</code></td>"
            f"<td>{_html_text(row.get('selected_model') or 'none')}</td>"
            f"<td>{_html_text(row.get('selected_reasoning_effort') or 'none')}</td>"
            f"<td>{_html_text(row.get('started_at') or row.get('created_at') or row.get('mtime') or 'none')}</td>"
            f"<td>{_html_text(row.get('completed_at') or 'none')}</td>"
            f"<td>{_worker_badge(row.get('terminal_state') or 'not-terminal')}</td>"
            f"<td><code>{_html_text(row.get('run_packet_path') or 'none')}</code></td>"
            "</tr>"
        )
    return "".join(rendered)


def _worker_receipt_chain_rows(chain_rows: list[dict[str, Any]]) -> str:
    if not chain_rows:
        return "<tr><td colspan=\"6\">No receipt chain rows.</td></tr>"
    rendered: list[str] = []
    for item in chain_rows:
        rendered.append(
            "<tr>"
            f"<td><code>{_html_text(item.get('name') or '')}</code></td>"
            f"<td>{_worker_badge(item.get('exists'))}</td>"
            f"<td>{_html_text(item.get('bytes') if item.get('bytes') is not None else 'unknown')}</td>"
            f"<td><code>{_html_text(item.get('sha256') or 'none')}</code></td>"
            f"<td>{_html_text(item.get('modified_at') or 'none')}</td>"
            f"<td><code>{_html_text(item.get('path') or 'none')}</code></td>"
            "</tr>"
        )
    return "\n".join(rendered)


def _redact_local_preview_paths(value: Any) -> Any:
    if isinstance(value, str):
        text = value.replace("/home/sev/ION - Production/ION_Developement/", "")
        text = text.replace("/home/sev/ION - Production/ION_Developement", "<ION_ROOT>")
        return text.replace("/home/sev", "<HOME>")
    if isinstance(value, list):
        return [_redact_local_preview_paths(item) for item in value]
    if isinstance(value, dict):
        return {key: _redact_local_preview_paths(item) for key, item in value.items()}
    return value


def _worker_log_cards(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "<article class=\"card\"><h3>Logs</h3><p>No logs available.</p></article>"
    cards: list[str] = []
    for row in rows:
        text = str(_redact_local_preview_paths(row.get("text") or "")).strip()
        preview = _html_text(text if len(text) <= 900 else text[-900:])
        cards.append(
            "<article class=\"card\">"
            f"<h3>{_html_text(row.get('name') or 'log')}</h3>"
            f"<p>{_worker_badge('included' if row.get('included') else (row.get('finding') or 'missing'))} "
            f"<code>{_html_text(row.get('path') or 'none')}</code></p>"
            f"<p class=\"meta\">shown: {_html_text(row.get('shown_bytes') or 0)} bytes | total: {_html_text(row.get('total_bytes') or 0)} | truncated: {_html_text(_format_bool(row.get('truncated')))}</p>"
            f"<pre>{preview or 'empty'}</pre>"
            "</article>"
        )
    return "".join(cards)


def render_codex_worker_live_status_html(root: str | Path, *, auth_token: str | None = None) -> str:
    """Render a bounded JOC-style worker cockpit over machine-observed telemetry."""

    model = build_worker_cockpit_view_model(root)
    safe_model = _redact_local_preview_paths(model)
    active = model.get("active_worker") if isinstance(model.get("active_worker"), Mapping) else {}
    latest_runs = [row for row in model.get("latest_worker_runs", []) if isinstance(row, dict)]
    machine_signin = model.get("machine_sign_in") if isinstance(model.get("machine_sign_in"), Mapping) else {}
    receipt_chain = [row for row in model.get("receipt_chain", []) if isinstance(row, dict)]
    model_move = model.get("model_move_summary") if isinstance(model.get("model_move_summary"), Mapping) else {}
    proof_gate = model.get("proof_gate") if isinstance(model.get("proof_gate"), Mapping) else {}
    logs = [row for row in model.get("logs", []) if isinstance(row, dict)]
    fanout = model.get("fanout") if isinstance(model.get("fanout"), Mapping) else {}
    fanout_status = fanout.get("status") if isinstance(fanout.get("status"), Mapping) else {}
    fanout_parent_rows = [row for row in fanout.get("parent_child_rows", []) if isinstance(row, dict)]
    settlement = model.get("settlement") if isinstance(model.get("settlement"), Mapping) else {}
    settlement_rows = [row for row in settlement.get("rows", []) if isinstance(row, dict)]
    event_links = model.get("event_links") if isinstance(model.get("event_links"), Mapping) else {}
    supabase_rows = [row for row in event_links.get("supabase_receipts", []) if isinstance(row, dict)]
    readonly = model.get("read_only") if isinstance(model.get("read_only"), Mapping) else {}
    _ = auth_token
    model_endpoint = "/cockpit/worker/model.json"
    status_class = str(active.get("status_badge") or "neutral")
    status_label = active.get("status") or "unknown"
    latest_rows_html = _worker_latest_run_rows(latest_runs)
    chain_rows_html = _worker_receipt_chain_rows(receipt_chain)
    log_cards_html = _worker_log_cards(logs)
    parent_rows_html = "".join(
        "<tr>"
        f"<td>{_html_text(row.get('scenario') or 'unknown')}</td>"
        f"<td><code>{_html_text(row.get('child_id') or 'none')}</code></td>"
        f"<td><code>{_html_text(row.get('lease_receipt_path') or 'none')}</code></td>"
        f"<td><code>{_html_text(row.get('heartbeat_receipt_path') or 'none')}</code></td>"
        f"<td><code>{_html_text(row.get('worker_context_awareness_receipt_path') or 'none')}</code></td>"
        "</tr>"
        for row in fanout_parent_rows[:18]
    ) or "<tr><td colspan=\"5\">No parent/child receipts present.</td></tr>"
    supabase_html = "".join(
        "<tr>"
        f"<td>{_html_text(row.get('mtime') or 'none')}</td>"
        f"<td>{_html_text(row.get('event_type') or 'unknown')}</td>"
        f"<td><code>{_html_text(row.get('packet_id') or 'none')}</code></td>"
        f"<td><code>{_html_text(row.get('path') or 'none')}</code></td>"
        "</tr>"
        for row in supabase_rows[:10]
    ) or "<tr><td colspan=\"4\">No Supabase receipt links available.</td></tr>"
    settlement_html = "".join(
        "<tr>"
        f"<td>{_worker_badge(row.get('status') or 'unknown')}</td>"
        f"<td>{_html_text(row.get('mtime') or 'none')}</td>"
        f"<td><code>{_html_text(row.get('path') or 'none')}</code></td>"
        "</tr>"
        for row in settlement_rows[:10]
    ) or "<tr><td colspan=\"3\">No settlement rows found.</td></tr>"
    filters = model.get("filters") if isinstance(model.get("filters"), Mapping) else {}
    filter_status = "".join(
        f"<option value=\"{_html_text(opt)}\">{_html_text(opt)}</option>"
        for opt in [item for item in filters.get("status_options", []) if isinstance(item, str)]
    )
    filter_sort = "".join(
        f"<option value=\"{_html_text(opt)}\">{_html_text(opt)}</option>"
        for opt in [item for item in filters.get("sort_options", []) if isinstance(item, str)]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>ION Codex Worker</title>
  <style>
    {HELIXION_SITE_CSS}
    :root {{
      color-scheme: dark;
      --bg: #0d1013;
      --panel: #161d22;
      --line: #31404a;
      --text: #e8eef3;
      --muted: #9eb1be;
      --ok: #46d7a4;
      --warn: #f7b955;
      --bad: #ef6b77;
      --accent: #53a5ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
      line-height: 1.4;
    }}
    main {{ max-width: 1280px; margin: 0 auto; padding: 24px 18px 38px; }}
    header {{ display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 16px; align-items: start; border-bottom: 1px solid var(--line); padding-bottom: 14px; margin-bottom: 12px; }}
    h1 {{ margin: 0 0 5px; font-size: clamp(22px, 4.2vw, 42px); line-height: 1.05; font-family: "JetBrains Mono", "IBM Plex Sans", monospace; }}
    h2 {{ margin: 0 0 10px; font-size: 16px; font-family: "JetBrains Mono", "IBM Plex Sans", monospace; }}
    h3 {{ margin: 0 0 8px; font-size: 14px; font-family: "JetBrains Mono", "IBM Plex Sans", monospace; color: var(--muted); text-transform: uppercase; }}
    p {{ color: var(--muted); margin: 0 0 8px; }}
    code {{ background: #0a0e11; border: 1px solid #26323a; border-radius: 3px; color: #b9d7ff; padding: 1px 4px; overflow-wrap: anywhere; }}
    .status-badge {{ display: inline-flex; gap: 8px; align-items: center; border: 1px solid var(--line); padding: 7px 10px; border-radius: 3px; font-size: 12px; text-transform: uppercase; }}
    .status-dot {{ width: 9px; height: 9px; border-radius: 999px; }}
    .status-ok .status-dot {{ background: var(--ok); box-shadow: 0 0 12px rgba(70, 215, 164, 0.4); }}
    .status-active .status-dot {{ background: var(--accent); box-shadow: 0 0 12px rgba(83, 165, 255, 0.4); }}
    .status-bad .status-dot {{ background: var(--bad); box-shadow: 0 0 12px rgba(239, 107, 119, 0.4); }}
    .status-warn .status-dot {{ background: var(--warn); box-shadow: 0 0 12px rgba(247, 185, 85, 0.4); }}
    .status-neutral .status-dot {{ background: #8da0ae; }}
    .grid {{ display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: 10px; }}
    .card {{ background: linear-gradient(180deg, #182027 0%, #141b20 100%); border: 1px solid var(--line); border-radius: 4px; padding: 12px; min-height: 100%; }}
    .span-12 {{ grid-column: span 12; }}
    .span-8 {{ grid-column: span 8; }}
    .span-6 {{ grid-column: span 6; }}
    .span-4 {{ grid-column: span 4; }}
    .span-3 {{ grid-column: span 3; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
    th, td {{ border-bottom: 1px solid #2b3841; padding: 6px 5px; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-weight: 700; text-transform: uppercase; font-size: 11px; }}
    .badge {{ display: inline-flex; border: 1px solid var(--line); border-radius: 999px; padding: 1px 8px; font-size: 11px; white-space: nowrap; }}
    .badge-ok {{ color: var(--ok); border-color: rgba(70, 215, 164, 0.5); }}
    .badge-bad {{ color: var(--bad); border-color: rgba(239, 107, 119, 0.6); }}
    .badge-warn {{ color: var(--warn); border-color: rgba(247, 185, 85, 0.6); }}
    .badge-neutral {{ color: var(--muted); }}
    .filters {{ display: grid; gap: 8px; grid-template-columns: 1.2fr 1fr 1fr; }}
    .filters input, .filters select {{
      width: 100%;
      background: #10161b;
      color: var(--text);
      border: 1px solid #34424c;
      border-radius: 3px;
      padding: 7px 8px;
      font: inherit;
      font-size: 12px;
    }}
    pre {{ margin: 0; max-height: 200px; overflow: auto; background: #0b1116; border: 1px solid #29353f; border-radius: 3px; padding: 8px; color: #d5e5f2; font-size: 11px; }}
    .meta {{ font-size: 11px; color: var(--muted); }}
    .two-col {{ display: grid; gap: 10px; grid-template-columns: 1fr 1fr; }}
    .safety button {{
      margin-right: 8px;
      border: 1px solid #485864;
      background: #172027;
      color: #7e94a5;
      border-radius: 3px;
      padding: 7px 10px;
      cursor: not-allowed;
    }}
    @media (max-width: 840px) {{
      header {{ grid-template-columns: 1fr; }}
      .grid {{ grid-template-columns: 1fr; }}
      .span-12, .span-8, .span-6, .span-4, .span-3 {{ grid-column: span 1; }}
      .filters {{ grid-template-columns: 1fr; }}
      .two-col {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body data-endpoint="{_html_text(model_endpoint)}">
  {render_helixion_site_bar("worker", auth_token=auth_token)}
  <main>
    <header>
      <div>
        <h1>Worker Command Center</h1>
        <p>JOC-style read-only worker cockpit over machine-observed facts only. No mutation controls are active in this surface.</p>
        <p class="meta">model: <code>{_html_text(model.get('schema_id') or 'unknown')}</code> | generated: <code id="generated-at">{_html_text(model.get("generated_at") or "none")}</code></p>
      </div>
      <div class="status-badge status-{_html_text(status_class)}" id="phase-badge"><span class="status-dot"></span><span id="phase-label">{_html_text(status_label)}</span></div>
    </header>

    <section class="grid" aria-label="worker command center">
      <article class="card span-12">
        <h2>Filter and Sort</h2>
        <div class="filters">
          <input id="filter-search" type="search" placeholder="Search by run/request/model/status">
          <select id="filter-status"><option value="">all statuses</option>{filter_status}</select>
          <select id="filter-sort">{filter_sort}</select>
        </div>
      </article>

      <article class="card span-4">
        <h2>Active Worker</h2>
        <table><tbody id="active-worker">{_worker_active_rows(active)}</tbody></table>
      </article>
      <article class="card span-4">
        <h2>Machine Sign-In</h2>
        <table>
          <tbody>
            <tr><th>status</th><td>{_worker_badge(machine_signin.get("status") or "unknown")}</td></tr>
            <tr><th>worker_authored</th><td>{_worker_badge(machine_signin.get("worker_authored"))}</td></tr>
            <tr><th>required context</th><td>{_html_text(machine_signin.get("required_context_reads_ready") or 0)} / {_html_text(machine_signin.get("required_context_reads_total") or 0)}</td></tr>
            <tr><th>missing paths</th><td>{_html_text(machine_signin.get("required_context_reads_missing") or 0)}</td></tr>
            <tr><th>receipt path</th><td><code>{_html_text(machine_signin.get("worker_context_awareness_receipt_path") or "none")}</code></td></tr>
            <tr><th>receipt sha256</th><td><code>{_html_text(machine_signin.get("worker_context_awareness_receipt_sha256") or "none")}</code></td></tr>
          </tbody>
        </table>
      </article>
      <article class="card span-4">
        <h2>Proof Gate</h2>
        <table>
          <tbody>
            <tr><th>context proof</th><td>{_worker_badge(proof_gate.get("context_proof_accepted"))}</td></tr>
            <tr><th>template proof</th><td>{_worker_badge(proof_gate.get("template_action_proof_accepted"))}</td></tr>
            <tr><th>return template</th><td>{_worker_badge(proof_gate.get("return_template_valid"))}</td></tr>
            <tr><th>workload diff</th><td>{_worker_badge(proof_gate.get("workload_diff_accepted"))}</td></tr>
            <tr><th>terminal intake</th><td>{_worker_badge(proof_gate.get("terminal_intake_state") or "not-terminal")}</td></tr>
          </tbody>
        </table>
      </article>

      <article class="card span-12">
        <h2>Latest Worker Runs</h2>
        <table>
          <thead><tr><th>status</th><th>run_id</th><th>request_id</th><th>model</th><th>reasoning</th><th>started</th><th>completed</th><th>terminal</th><th>run packet</th></tr></thead>
          <tbody id="latest-runs">{latest_rows_html}</tbody>
        </table>
      </article>

      <article class="card span-12">
        <h2>Receipt Chain Matrix</h2>
        <table>
          <thead><tr><th>artifact</th><th>exists</th><th>bytes</th><th>sha256</th><th>modified</th><th>path</th></tr></thead>
          <tbody id="receipt-chain">{chain_rows_html}</tbody>
        </table>
      </article>

      <article class="card span-6">
        <h2>Model Move Summary</h2>
        <table>
          <tbody>
            <tr><th>model</th><td>{_html_text(model_move.get("selected_model") or "none")}</td></tr>
            <tr><th>reasoning</th><td>{_html_text(model_move.get("selected_reasoning_effort") or "none")}</td></tr>
            <tr><th>usage_pool</th><td><code>{_html_text(model_move.get("usage_pool_id") or "none")}</code></td></tr>
            <tr><th>model_move_id</th><td><code>{_html_text(model_move.get("model_move_id") or "none")}</code></td></tr>
            <tr><th>routing reasons</th><td>{_html_text(", ".join(str(x) for x in model_move.get("routing_reasons", [])) or "none")}</td></tr>
            <tr><th>summary</th><td>{_html_text(model_move.get("summary") or "none")}</td></tr>
          </tbody>
        </table>
      </article>

      <article class="card span-6 safety">
        <h2>View-Only Safety</h2>
        <p>Mutation controls disabled unless explicit bounded authority is present.</p>
        <p>production_authority: {_worker_badge(readonly.get("production_authority"))} live_execution_authority: {_worker_badge(readonly.get("live_execution_authority"))}</p>
        <button disabled>Queue Mutation (disabled)</button>
        <button disabled>Worker Kill (disabled)</button>
        <button disabled>Retry/Replay (disabled)</button>
      </article>

      <article class="card span-12">
        <h2>Logs</h2>
        <div class="two-col">{log_cards_html}</div>
      </article>

      <article class="card span-12">
        <h2>Fan-Out Telemetry</h2>
        <p>status: {_worker_badge(fanout_status.get("status") or "unknown")} | queue_mutation_detected: {_worker_badge(fanout_status.get("queue_mutation_detected"))}</p>
        <p>timeout fail-closed: {_worker_badge(fanout_status.get("timeout_fail_closed_summary", {}).get("fail_closed") if isinstance(fanout_status.get("timeout_fail_closed_summary"), Mapping) else False)} | conflict deferrals: {_html_text(fanout_status.get("conflict_lock_summary", {}).get("conflict_deferral_events") if isinstance(fanout_status.get("conflict_lock_summary"), Mapping) else '0')}</p>
        <table>
          <thead><tr><th>scenario</th><th>child</th><th>lease receipt</th><th>heartbeat receipt</th><th>worker sign-in receipt</th></tr></thead>
          <tbody>{parent_rows_html}</tbody>
        </table>
      </article>

      <article class="card span-6">
        <h2>Supabase Event Links</h2>
        <table>
          <thead><tr><th>time</th><th>event_type</th><th>packet_id</th><th>receipt path</th></tr></thead>
          <tbody>{supabase_html}</tbody>
        </table>
      </article>

      <article class="card span-6">
        <h2>Settlement Blockers</h2>
        <table>
          <thead><tr><th>status</th><th>time</th><th>path</th></tr></thead>
          <tbody>{settlement_html}</tbody>
        </table>
      </article>
    </section>
  </main>
  <script>
    const endpoint = document.body.dataset.endpoint;
    const phaseBadge = document.getElementById("phase-badge");
    const phaseLabel = document.getElementById("phase-label");
    const generatedAt = document.getElementById("generated-at");
    const search = document.getElementById("filter-search");
    const status = document.getElementById("filter-status");
    const sort = document.getElementById("filter-sort");
    const latestRunsBody = document.getElementById("latest-runs");

    function text(value) {{
      return value === undefined || value === null || value === "" ? "" : String(value);
    }}

    function esc(value) {{
      return text(value).replace(/[&<>"']/g, (ch) => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}}[ch]));
    }}

    function badge(value) {{
      const raw = text(value) || "unknown";
      const lower = raw.toLowerCase();
      let kind = "neutral";
      if (lower.includes("accept") || lower.includes("ready") || lower.includes("running") || lower === "true") kind = "ok";
      if (lower.includes("block") || lower.includes("invalid") || lower.includes("fail") || lower.includes("defer") || lower === "false") kind = "bad";
      if (lower.includes("template") || lower.includes("timeout")) kind = "warn";
      return `<span class="badge badge-${{kind}}">${{esc(raw)}}</span>`;
    }}

    function renderLatestRows(rows) {{
      if (!Array.isArray(rows) || rows.length === 0) {{
        latestRunsBody.innerHTML = '<tr><td colspan="9">No recent worker runs.</td></tr>';
        return;
      }}
      const query = text(search.value).toLowerCase();
      const statusFilter = text(status.value).toLowerCase();
      const sortValue = text(sort.value);
      let filtered = rows.filter((row) => {{
        const statusText = text(row.status || row.terminal_state).toLowerCase();
        if (statusFilter && !statusText.includes(statusFilter)) return false;
        if (!query) return true;
        const haystack = [
          row.status, row.run_id, row.request_id, row.selected_model, row.selected_reasoning_effort, row.started_at, row.completed_at,
        ].map((v) => text(v).toLowerCase()).join(" ");
        return haystack.includes(query);
      }});
      if (sortValue === "time_asc") {{
        filtered.sort((a, b) => text(a.started_at || a.created_at || a.mtime).localeCompare(text(b.started_at || b.created_at || b.mtime)));
      }} else if (sortValue === "status") {{
        filtered.sort((a, b) => text(a.status).localeCompare(text(b.status)));
      }} else if (sortValue === "model") {{
        filtered.sort((a, b) => text(a.selected_model).localeCompare(text(b.selected_model)));
      }} else if (sortValue === "run_id") {{
        filtered.sort((a, b) => text(a.run_id).localeCompare(text(b.run_id)));
      }} else {{
        filtered.sort((a, b) => text(b.started_at || b.created_at || b.mtime).localeCompare(text(a.started_at || a.created_at || a.mtime)));
      }}
      latestRunsBody.innerHTML = filtered.map((row) => `
        <tr>
          <td>${{badge(row.status || row.terminal_state || "unknown")}}</td>
          <td><code>${{esc(row.run_id || "none")}}</code></td>
          <td><code>${{esc(row.request_id || "none")}}</code></td>
          <td>${{esc(row.selected_model || "none")}}</td>
          <td>${{esc(row.selected_reasoning_effort || "none")}}</td>
          <td>${{esc(row.started_at || row.created_at || row.mtime || "none")}}</td>
          <td>${{esc(row.completed_at || "none")}}</td>
          <td>${{badge(row.terminal_state || "not-terminal")}}</td>
          <td><code>${{esc(row.run_packet_path || "none")}}</code></td>
        </tr>
      `).join("");
    }}

    let latestRows = {json.dumps(latest_runs)};
    function render(model) {{
      if (!model || typeof model !== "object") return;
      const active = model.active_worker || {{}};
      const statusClass = text(active.status_badge || "neutral");
      phaseBadge.className = `status-badge status-${{statusClass}}`;
      phaseLabel.textContent = text(active.status || "unknown");
      if (generatedAt) generatedAt.textContent = text(model.generated_at || "none");
      if (Array.isArray(model.latest_worker_runs)) {{
        latestRows = model.latest_worker_runs;
      }}
      renderLatestRows(latestRows);
    }}

    async function poll() {{
      try {{
        const response = await fetch(endpoint, {{cache: "no-store", headers: {{"accept": "application/json"}}}});
        if (!response.ok) return;
        render(await response.json());
      }} catch (_error) {{}}
    }}

    search.addEventListener("input", () => renderLatestRows(latestRows));
    status.addEventListener("change", () => renderLatestRows(latestRows));
    sort.addEventListener("change", () => renderLatestRows(latestRows));

    render({json.dumps(safe_model)});
    setInterval(poll, 5000);
    poll();
  </script>
</body>
</html>
"""


def render_public_cockpit_login(
    *,
    next_path: str = "/cockpit/chat",
    finding: str | None = None,
    env: Mapping[str, str] | None = None,
) -> str:
    status = auth_status(env)
    google_enabled = bool(status.get("google_oauth_configured"))
    token_enabled = bool(status.get("permission_token_configured"))
    allowed_count = int(status.get("google_allowed_email_count") or 0)
    google_status = (
        f"Google OAuth is configured. Allowed Google emails: {allowed_count}."
        if google_enabled
        else f"Google OAuth still needs client ID and secret. Allowed Google emails already listed: {allowed_count}."
    )
    finding_messages = {
        "google_oauth_state_missing_or_invalid": "Google login is not enabled yet. Use the permission token for now.",
        "google_oauth_not_configured": "Google login is not enabled yet. Use the permission token for now.",
        "google_oauth_state_mismatch": "Google login expired. Start again from this page after Google setup is complete.",
        "permission_token_invalid": "Permission token did not match.",
        "permission_token_required": "Enter the permission token.",
    }
    finding_text = finding_messages.get(str(finding or ""), str(finding or ""))
    finding_html = f"<p class=\"error\">{_html_text(finding_text)}</p>" if finding_text else ""
    google_button = (
        "<button type=\"submit\">Continue with Google</button>"
        if google_enabled
        else "<button type=\"submit\" disabled>Google OAuth setup needed</button>"
    )
    token_button = (
        "<button type=\"submit\">Login with permission token</button>"
        if token_enabled
        else "<button type=\"submit\" disabled>Permission token not configured</button>"
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow">
  <title>ION Cockpit Login</title>
  <style>
    {HELIXION_SITE_CSS}
    :root {{ color-scheme: dark; --bg:#090b0c; --panel:#121619; --line:#2b343a; --text:#edf2f4; --muted:#9aa7ad; --blue:#65a7e8; --red:#e15f5f; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; min-height:100vh; background:var(--bg); color:var(--text); }}
    main {{ width:min(920px, calc(100vw - 32px)); display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
    .login-wrap {{ min-height:calc(100vh - 43px); display:grid; place-items:center; padding:24px 0; }}
    header {{ grid-column:1 / -1; border-bottom:1px solid var(--line); padding-bottom:14px; }}
    h1,h2,p {{ margin:0; letter-spacing:0; }}
    h1 {{ font-size:32px; }}
    h2 {{ font-size:16px; margin-bottom:8px; }}
    p {{ color:var(--muted); line-height:1.4; }}
    section {{ background:var(--panel); border:1px solid var(--line); border-radius:2px; padding:14px; }}
    form {{ display:grid; gap:8px; margin-top:12px; }}
    label {{ color:var(--muted); font-size:13px; }}
    input {{ width:100%; border:1px solid var(--line); border-radius:2px; background:#0d1113; color:var(--text); padding:9px; font:inherit; }}
    button {{ justify-self:start; border:1px solid var(--line); background:#18242b; color:var(--text); border-radius:2px; padding:8px 11px; font-weight:700; cursor:pointer; text-transform:uppercase; }}
    button:disabled {{ opacity:.55; cursor:not-allowed; }}
    .error {{ grid-column:1 / -1; color:var(--red); }}
    code {{ color:#f5d0b4; overflow-wrap:anywhere; }}
    @media (max-width:760px) {{ main {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
{render_helixion_site_bar("login")}
<div class="login-wrap">
<main>
  <header>
    <h1>ION Cockpit Login</h1>
    <p>Access is limited to signed cockpit sessions, permission tokens, or approved Google accounts. This login does not grant production authority.</p>
  </header>
  {finding_html}
  <section>
    <h2>Permission Token</h2>
    <p>Use the current ION cockpit permission token or an invited token.</p>
    <form method="post" action="/cockpit/auth/token">
      <input type="hidden" name="next" value="{_html_text(safe_next_path(next_path))}">
      <label for="permission_token">Token</label>
      <input id="permission_token" name="permission_token" type="password" autocomplete="current-password">
      {token_button}
    </form>
  </section>
  <section>
    <h2>Google Account</h2>
    <p>{_html_text(google_status)}</p>
    <p>Allowed emails are controlled by <code>{ALLOWED_EMAILS_ENV}</code>. An invite token can permit an additional Google account.</p>
    <form method="post" action="/cockpit/auth/google/start">
      <input type="hidden" name="next" value="{_html_text(safe_next_path(next_path))}">
      <label for="invite_token">Invite token, optional</label>
      <input id="invite_token" name="invite_token" type="password" autocomplete="one-time-code">
      {google_button}
    </form>
  </section>
</main>
</div>
</body>
</html>"""


def write_http_mcp_preview_audit(
    root: str | Path | None = None,
    *,
    output: str | Path | None = None,
) -> dict[str, Any]:
    shell_root = Path(root or ".").expanduser().resolve()
    result = audit_http_mcp_preview(shell_root)
    out = shell_root / (Path(output) if output else OUTPUT_RELATIVE_PATH)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


class IonChatGPTPreviewHandler(BaseHTTPRequestHandler):
    server_version = "IONChatGPTMCPPreview/0.1"

    def _send_json(self, status: int, payload: Mapping[str, Any]) -> None:
        body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if self.path.split("?", 1)[0].startswith("/cockpit/browser-gpt-dom/"):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            return

    def _send_html(self, status: int, body_text: str) -> None:
        body = body_text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; frame-src 'self'; img-src 'self' data:; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def _public_base_url(self) -> str:
        host = self.headers.get("host") or ""
        if not host:
            return ""
        local_host = host.startswith("127.0.0.1") or host.startswith("localhost")
        proto = self.headers.get("x-forwarded-proto") or ("http" if local_host else "https")
        return f"{proto}://{host}"

    def _secure_cookie(self) -> bool:
        return self._public_base_url().startswith("https://")

    def _is_local_loopback_preview_request(self) -> bool:
        host = (self.headers.get("host") or "").split(":", 1)[0].lower()
        client_host = str(self.client_address[0] if self.client_address else "")
        server_host = str(getattr(self.server, "server_address", ("", 0))[0])  # type: ignore[attr-defined]
        return (
            client_host in {"127.0.0.1", "::1"}
            and host in {"127.0.0.1", "localhost", "[::1]"}
            and server_host in {"127.0.0.1", "localhost", "::1", ""}
        )

    def _same_origin_reference(self, value: str) -> bool:
        reference = urlparse((value or "").strip())
        base = urlparse(self._public_base_url())
        if reference.scheme not in {"http", "https"} or not reference.netloc or not base.netloc:
            return False
        return reference.scheme.lower() == base.scheme.lower() and reference.netloc.lower() == base.netloc.lower()

    def _check_mutation_origin(self) -> tuple[bool, str | None]:
        if self._is_local_loopback_preview_request():
            return True, None
        origin = (self.headers.get("origin") or "").strip()
        if origin:
            return (True, None) if self._same_origin_reference(origin) else (False, "origin_not_allowed")
        referer = (self.headers.get("referer") or "").strip()
        if referer:
            return (True, None) if self._same_origin_reference(referer) else (False, "referer_not_allowed")
        return False, "same_origin_required"

    def _request_token(self, payload: Mapping[str, Any] | None = None, *, allow_query_token: bool = False) -> str:
        auth = self.headers.get("authorization") or ""
        if auth.lower().startswith("bearer "):
            return auth.split(" ", 1)[1].strip()
        if allow_query_token:
            query = parse_qs(urlparse(self.path).query)
            if query.get("token"):
                return str(query["token"][-1])
        if payload and payload.get("public_token"):
            return str(payload.get("public_token") or "")
        return ""

    def _check_public_cockpit_access(
        self,
        payload: Mapping[str, Any] | None = None,
        *,
        allow_query_token: bool = False,
    ) -> tuple[bool, str | None, str | None]:
        context = self._resolve_public_cockpit_access_context(payload, allow_query_token=allow_query_token)
        return bool(context.get("ok")), context.get("finding"), context.get("token")

    def _resolve_public_cockpit_access_context(
        self,
        payload: Mapping[str, Any] | None = None,
        *,
        allow_query_token: bool = False,
    ) -> dict[str, Any]:
        """Resolve auth once and preserve a redacted server-side principal."""

        secret = cockpit_session_secret()
        if secret:
            session = validate_session_cookie(self.headers.get("cookie"), secret=secret)
            if session.ok:
                return {
                    "ok": True,
                    "finding": None,
                    "token": None,
                    "auth_source": "session_cookie",
                    "principal": dict(session.principal or {}),
                }
        if self._is_local_loopback_preview_request():
            return {
                "ok": True,
                "finding": None,
                "token": None,
                "auth_source": "local_loopback",
                "principal": {
                    "auth_method": "local_loopback",
                    "subject": "local_operator",
                    "token_label": "local_loopback",
                    "rank_ceiling": "founder_root_steward",
                    "production_authority": False,
                    "live_execution_authority": False,
                },
            }
        supplied = self._request_token(payload, allow_query_token=allow_query_token)
        if supplied:
            token_result = validate_permission_token(supplied)
            if token_result.ok:
                return {
                    "ok": True,
                    "finding": None,
                    "token": supplied,
                    "auth_source": "permission_token",
                    "principal": dict(token_result.principal or {}),
                }
            return {
                "ok": False,
                "finding": token_result.finding or "permission_token_invalid",
                "token": None,
                "auth_source": "permission_token",
                "principal": {},
            }
        if not secret and not validate_permission_token(os.environ.get(PUBLIC_COCKPIT_TOKEN_ENV) or "").ok and not google_oauth_configured():
            return {
                "ok": False,
                "finding": "public_cockpit_auth_not_configured",
                "token": None,
                "auth_source": "not_configured",
                "principal": {},
            }
        return {
            "ok": False,
            "finding": "public_cockpit_login_required",
            "token": None,
            "auth_source": "missing_login",
            "principal": {},
        }

    def _check_public_cockpit_mutation_access(self, payload: Mapping[str, Any] | None = None) -> tuple[bool, str | None, str | None]:
        ok, finding, token = self._check_public_cockpit_access(payload)
        if not ok:
            return ok, finding, token
        origin_ok, origin_finding = self._check_mutation_origin()
        if not origin_ok:
            return False, origin_finding, None
        return True, None, token

    def _login_path(self, next_path: str | None = None, finding: str | None = None) -> str:
        params: dict[str, str] = {"next": safe_next_path(next_path or self.path)}
        if finding:
            params["finding"] = finding
        return "/cockpit/login?" + urlencode(params)

    def _send_public_cockpit_blocked(self, finding: str, *, next_path: str | None = None) -> None:
        if not self._wants_json() and finding in {"public_cockpit_login_required", "permission_token_required", "permission_token_invalid"}:
            self._redirect(self._login_path(next_path or self.path, None if finding == "public_cockpit_login_required" else finding))
            return
        status = 503 if finding == "public_cockpit_auth_not_configured" else 401
        if finding in {"origin_not_allowed", "referer_not_allowed", "same_origin_required"}:
            status = 403
        self._send_json(
            status,
            {
                "ok": False,
                "finding": finding,
                "login_path": self._login_path(next_path or self.path),
                "public_cockpit_path": "/cockpit/chat",
                "session_cookie": SESSION_COOKIE,
                "requires_env": [
                    PUBLIC_COCKPIT_TOKEN_ENV,
                    SESSION_SECRET_ENV,
                    INVITE_TOKENS_ENV,
                    GOOGLE_CLIENT_ID_ENV,
                    GOOGLE_CLIENT_SECRET_ENV,
                    GOOGLE_REDIRECT_URI_ENV,
                    ALLOWED_EMAILS_ENV,
                ],
                "production_authority": False,
                "live_execution_authority": False,
            },
        )

    def _send_login(self, *, status: int = 200, next_path: str = "/cockpit/chat", finding: str | None = None) -> None:
        self._send_html(status, render_public_cockpit_login(next_path=next_path, finding=finding))

    def _redirect_with_headers(self, target: str, headers: Mapping[str, str]) -> None:
        self.send_response(303)
        self.send_header("Location", target)
        self.send_header("Cache-Control", "no-store")
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()

    def _session_redirect(self, principal: Mapping[str, Any], next_path: str) -> None:
        secret = cockpit_session_secret()
        if not secret:
            self._send_login(status=503, next_path=next_path, finding="cockpit_session_secret_not_configured")
            return
        self._redirect_with_headers(
            safe_next_path(next_path),
            {"Set-Cookie": make_session_cookie(principal, secret=secret, secure=self._secure_cookie())},
        )

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

    def _redirect(self, target: str) -> None:
        self.send_response(303)
        self.send_header("Location", target)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_OPTIONS(self) -> None:  # noqa: N802 - stdlib handler name
        path = self.path.split("?", 1)[0]
        if path.startswith("/cockpit/browser-gpt-dom/"):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return
        self._send_json(404, {"ok": False, "error": "not_found"})

    def _send_bytes(self, status: int, body: bytes, content_type: str, *, csp: str | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if csp:
            self.send_header("Content-Security-Policy", csp)
        self.end_headers()
        self.wfile.write(body)

    def _send_react_static(self, request_path: str) -> None:
        target = resolve_react_static_asset(self.server.ion_root, request_path)  # type: ignore[attr-defined]
        if target is None:
            self._send_json(404, {"ok": False, "finding": "react_static_not_found", "path": request_path})
            return
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self._send_bytes(200, target.read_bytes(), content_type, csp=REACT_CSP)

    def _optional_public_cockpit_access(self) -> tuple[bool, str | None]:
        ok, _finding, token = self._check_public_cockpit_access()
        return ok, token

    def _send_application_dev_launcher_catalog(self) -> None:
        launcher_url = application_dev_launcher_url()
        target = f"{launcher_url}/apps.json"
        try:
            request = urllib.request.Request(
                target,
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "identity",
                    "User-Agent": "HelixionApplicationDevCatalog/0.1",
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
                    "launcher": launcher_url + "/",
                },
            )

    def _send_project_preview_proxy(self, project_id: str, request_path: str) -> None:
        spec, finding = resolve_project(self.server.ion_root, project_id)  # type: ignore[attr-defined]
        if spec is None:
            self._send_json(404, {"ok": False, "finding": finding or "project_not_registered"})
            return
        if request_path.endswith("/@vite/client"):
            vite_client_stub = b"""
window.__vite_plugin_react_preamble_installed__ = true;
window.$RefreshReg$ = window.$RefreshReg$ || (() => {});
window.$RefreshSig$ = window.$RefreshSig$ || (() => (type) => type);
export function createHotContext() {
  return {
    data: {},
    accept() {},
    dispose() {},
    prune() {},
    decline() {},
    invalidate() {},
    on() {},
    off() {},
    send() {}
  };
}
export function updateStyle(id, content) {
  let el = document.querySelector('style[data-vite-dev-id="' + id + '"]');
  if (!el) {
    el = document.createElement("style");
    el.setAttribute("data-vite-dev-id", id);
    document.head.appendChild(el);
  }
  el.textContent = content;
}
export function removeStyle(id) {
  const el = document.querySelector('style[data-vite-dev-id="' + id + '"]');
  if (el) el.remove();
}
export function injectQuery(url) { return url; }
export class ErrorOverlay extends HTMLElement {}
try {
  if (!customElements.get("vite-error-overlay")) {
    customElements.define("vite-error-overlay", ErrorOverlay);
  }
} catch (_err) {}
"""
            self._send_bytes(
                200,
                vite_client_stub,
                "text/javascript; charset=utf-8",
            )
            return
        if request_path.endswith("/@react-refresh"):
            self._send_bytes(
                200,
                b"window.__vite_plugin_react_preamble_installed__ = true; window.$RefreshReg$ = window.$RefreshReg$ || (() => {}); window.$RefreshSig$ = window.$RefreshSig$ || (() => (type) => type); export function injectIntoGlobalHook() {}; export default {};\n",
                "text/javascript; charset=utf-8",
            )
            return
        query = urlparse(self.path).query
        target_path = request_path
        if target_path == f"/projects/{project_id}/preview":
            target_path += "/"
        target = f"http://127.0.0.1:{spec.preview_port}{target_path}"
        if query:
            target = f"{target}?{query}"
        try:
            request = urllib.request.Request(
                target,
                headers={
                    "Accept": self.headers.get("accept") or "*/*",
                    "Accept-Encoding": "identity",
                    "User-Agent": "HelixionProjectWorkbench/0.1",
                },
            )
            with urllib.request.urlopen(request, timeout=45) as response:
                body = response.read()
                content_type = response.headers.get("content-type")
                if not content_type:
                    content_type = mimetypes.guess_type(urlparse(target).path)[0] or "application/octet-stream"
                if "text/html" in content_type:
                    text = body.decode("utf-8", errors="replace")
                    text = re.sub(
                        r'<script type="module">import \{ injectIntoGlobalHook \} from "[^"]*/@react-refresh";.*?</script>\s*',
                        (
                            '<script type="module">'
                            'window.__vite_plugin_react_preamble_installed__ = true;'
                            'window.$RefreshReg$ = () => {};'
                            'window.$RefreshSig$ = () => (type) => type;'
                            '</script>\n'
                        ),
                        text,
                        flags=re.DOTALL,
                    )
                    text = re.sub(
                        r'\s*<script type="module" src="[^"]*/@vite/client"></script>\s*',
                        "\n",
                        text,
                    )
                    body = text.encode("utf-8")
                self._send_bytes(int(getattr(response, "status", 200) or 200), body, content_type)
                return
        except Exception as exc:
            html_text = (
                "<!doctype html><html><head><meta charset=\"utf-8\"><title>Cosmos Preview Offline</title>"
                "<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#050607;color:#f4f1eb;font-family:system-ui,sans-serif}"
                "main{max-width:680px;padding:24px;border:1px solid #30383d;background:#111619}code{color:#ffd3b1}</style></head>"
                "<body><main><h1>Cosmos preview is offline</h1>"
                f"<p>Helixion tried to proxy <code>{_html_text(target)}</code>.</p>"
                f"<p>Finding: <code>{_html_text(exc.__class__.__name__)}</code>.</p>"
                "<p>Start or restart the Cosmos preview service, then reload this frame.</p>"
                "</main></body></html>"
            )
            self._send_html(503, html_text)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler name
        path = self.path.split("?", 1)[0]
        if path == "/favicon.ico":
            self.send_response(204)
            self.send_header("Cache-Control", "max-age=86400")
            self.end_headers()
            return
        if path.startswith("/joc-static/"):
            self._send_react_static(path)
            return
        if path in {"/projects/portfolio.json", "/projects/surface.json", "/cockpit/projects/portfolio.json"}:
            self._send_json(200, build_helixion_projects_surface_model_from_file(self.server.ion_root))  # type: ignore[attr-defined]
            return
        if path.startswith("/projects/family/"):
            encoded_family_id = path[len("/projects/family/") :]
            wants_json = encoded_family_id.endswith(".json")
            if wants_json:
                encoded_family_id = encoded_family_id[:-5]
            family_id = unquote(encoded_family_id)
            if not family_id or "/" in family_id:
                self._send_json(404, {"ok": False, "finding": "project_family_not_found"})
                return
            try:
                if wants_json:
                    self._send_json(
                        200,
                        build_helixion_project_family_detail_model_from_file(
                            self.server.ion_root,  # type: ignore[attr-defined]
                            family_id,
                        ),
                    )
                else:
                    self._send_html(
                        200,
                        render_helixion_project_family_detail(
                            self.server.ion_root,  # type: ignore[attr-defined]
                            family_id,
                            public_base_url=self._public_base_url(),
                        ),
                    )
                return
            except KeyError:
                self._send_json(404, {"ok": False, "finding": "project_family_not_found", "family_id": family_id})
                return
            except Exception as exc:
                self._send_json(503, {"ok": False, "finding": exc.__class__.__name__, "family_id": family_id})
                return
        if path in {"/projects/application-dev/apps.json", "/projects/appdev/apps.json"}:
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit#projects")
                return
            self._send_application_dev_launcher_catalog()
            return
        if path == "/projects/cosmos/preview" or path.startswith("/projects/cosmos/preview/"):
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/projects/cosmos")
                return
            self._send_project_preview_proxy("cosmos", path)
            return
        if path in {"/projects", "/projects/"}:
            self._send_html(
                200,
                render_ion_connector_landing(
                    self.server.ion_root,  # type: ignore[attr-defined]
                    public_base_url=self._public_base_url(),
                    active_nav="projects",
                ),
            )
            return
        if path in {"/projects/cosmos", "/projects/cosmos/"}:
            authenticated, token = self._optional_public_cockpit_access()
            self._send_html(
                200,
                render_project_workbench_html(
                    self.server.ion_root,  # type: ignore[attr-defined]
                    public_base_url=self._public_base_url(),
                    auth_token=token,
                    authenticated=authenticated,
                    project_id="cosmos",
                ),
            )
            return
        if path == "/projects/cosmos/model.json":
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/projects/cosmos/model.json")
                return
            self._send_json(
                200,
                build_project_workspace_status(
                    self.server.ion_root,  # type: ignore[attr-defined]
                    project_id="cosmos",
                    probe_preview=True,
                ),
            )
            return
        query = parse_qs(urlparse(self.path).query)
        if path in {"/cockpit/login", "/cockpit/login/"}:
            self._send_login(
                next_path=str(query.get("next", ["/cockpit/chat"])[-1]),
                finding=str(query.get("finding", [""])[-1]) or None,
            )
            return
        if path in {"/cockpit/logout", "/cockpit/logout/"}:
            self.send_response(303)
            self.send_header("Location", "/cockpit/login")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Set-Cookie", clear_cookie_header(SESSION_COOKIE, secure=self._secure_cookie(), path="/"))
            self.send_header("Set-Cookie", clear_cookie_header(OAUTH_STATE_COOKIE, secure=self._secure_cookie()))
            self.end_headers()
            return
        if path == "/cockpit/auth/google/callback":
            if not google_oauth_configured():
                self._send_login(status=503, finding="google_oauth_not_configured")
                return
            secret = cockpit_session_secret()
            if not secret:
                self._send_login(status=503, finding="cockpit_session_secret_not_configured")
                return
            state_result = validate_oauth_state_cookie(
                self.headers.get("cookie"),
                secret=secret,
                state=str(query.get("state", [""])[-1]),
            )
            if not state_result.ok:
                self._send_login(status=401, finding=state_result.finding)
                return
            if query.get("error"):
                self._send_login(status=401, finding="google_oauth_" + str(query.get("error", ["error"])[-1]))
                return
            try:
                userinfo = exchange_google_code_for_userinfo(
                    code=str(query.get("code", [""])[-1]),
                    base_url=self._public_base_url(),
                )
                auth = authorize_google_user(userinfo, oauth_state=state_result.principal or {})
            except Exception as exc:
                self._send_login(status=401, finding=f"google_oauth_failed:{exc.__class__.__name__}")
                return
            if not auth.ok:
                self._send_login(status=401, finding=auth.finding)
                return
            self.send_response(303)
            self.send_header("Location", safe_next_path(str((state_result.principal or {}).get("next") or "/cockpit/chat")))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Set-Cookie", make_session_cookie(auth.principal or {}, secret=secret, secure=self._secure_cookie()))
            self.send_header("Set-Cookie", clear_cookie_header(OAUTH_STATE_COOKIE, secure=self._secure_cookie()))
            self.end_headers()
            return
        if path in {"/cockpit", "/cockpit/", "/cockpit/apps", "/cockpit/apps/"}:
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit")
                return
            react_html = build_react_cockpit_html(self.server.ion_root)  # type: ignore[attr-defined]
            if react_html:
                self._send_bytes(200, react_html.encode("utf-8"), "text/html; charset=utf-8", csp=REACT_CSP)
                return
            html_text = build_cockpit_html(build_cockpit_view_model(self.server.ion_root))  # type: ignore[attr-defined]
            self._send_html(200, wrap_helixion_site_shell(html_text, "cockpit"))
            return
        if path in {"/cockpit/legacy", "/cockpit/legacy/"}:
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/legacy")
                return
            html_text = build_cockpit_html(build_cockpit_view_model(self.server.ion_root))  # type: ignore[attr-defined]
            self._send_html(200, wrap_helixion_site_shell(html_text, "cockpit"))
            return
        if path in {"/cockpit/chat", "/cockpit/chat/"}:
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/chat")
                return
            react_html = build_react_cockpit_html(self.server.ion_root)  # type: ignore[attr-defined]
            if react_html:
                self._send_bytes(200, react_html.encode("utf-8"), "text/html; charset=utf-8", csp=REACT_CSP)
                return
            model = build_dual_codex_chat_model(self.server.ion_root, write=True)  # type: ignore[attr-defined]
            chat_html = render_dual_codex_chat_html(model, base_path="/cockpit/chat")
            self._send_html(200, wrap_helixion_site_shell(chat_html, "chat"))
            return
        if path.startswith("/cockpit/projects/launch/open/"):
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path=path)
                return
            launch_id = path.rsplit("/", 1)[-1]
            query = parse_qs(urlparse(self.path).query)
            stop_token = str((query.get("stop_token") or [""])[-1] or "")
            html_text = build_project_launcher_open_html(
                self.server.ion_root,  # type: ignore[attr-defined]
                launch_id,
                stop_token=stop_token,
            )
            self._send_bytes(
                200,
                html_text.encode("utf-8"),
                "text/html; charset=utf-8",
                csp=PROJECT_LAUNCH_CSP,
            )
            return
        if path.startswith("/cockpit/projects/launch/proxy/"):
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path=path)
                return
            parsed = urlparse(self.path)
            rest = parsed.path.removeprefix("/cockpit/projects/launch/proxy/")
            launch_id, _, proxy_path = rest.partition("/")
            result = project_launcher_proxy_fetch(
                self.server.ion_root,  # type: ignore[attr-defined]
                launch_id,
                proxy_path,
                query=parsed.query,
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
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path=path)
                return
            screenshot = project_launcher_screenshot_file(
                self.server.ion_root,  # type: ignore[attr-defined]
                path.rsplit("/", 1)[-1],
            )
            if screenshot is None:
                self._send_json(404, {"ok": False, "finding": "project_launch_screenshot_not_found"})
                return
            self._send_bytes(200, screenshot.read_bytes(), "image/png")
            return
        if path in {"/cockpit/worker", "/cockpit/worker/"}:
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/worker")
                return
            self._send_html(
                200,
                render_codex_worker_live_status_html(self.server.ion_root),  # type: ignore[attr-defined]
            )
            return
        if path == "/cockpit/model.json":
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/model.json")
                return
            self._send_json(200, build_cockpit_view_model(self.server.ion_root))  # type: ignore[attr-defined]
            return
        if path == "/cockpit/session/access.json":
            access_context = self._resolve_public_cockpit_access_context()
            if not access_context.get("ok"):
                self._send_public_cockpit_blocked(str(access_context.get("finding") or "public_cockpit_login_required"), next_path=path)
                return
            collab = build_helixion_collaboration_access_model(
                self.server.ion_root,  # type: ignore[attr-defined]
                principal=access_context.get("principal") if isinstance(access_context.get("principal"), Mapping) else {},
            )
            self._send_json(
                200,
                {
                    "schema_id": "ion.helixion_cockpit_session_access_projection.v0_2",
                    "authenticated": True,
                    "auth_source": access_context.get("auth_source"),
                    "principal_projection": collab["session_access"],
                    "route_registry": collab["route_registry"],
                    "candidate_enforcement_active": False,
                    "live_route_enforcement": False,
                    "redaction": "no_raw_cookie_or_token",
                    "authority": collab["authority"],
                },
            )
            return
        if path == "/cockpit/collab/model.json":
            access_context = self._resolve_public_cockpit_access_context()
            if not access_context.get("ok"):
                self._send_public_cockpit_blocked(str(access_context.get("finding") or "public_cockpit_login_required"), next_path=path)
                return
            self._send_json(
                200,
                build_cockpit_surface_view_model(
                    self.server.ion_root,  # type: ignore[attr-defined]
                    surface="collab",
                    principal=access_context.get("principal") if isinstance(access_context.get("principal"), Mapping) else {},
                ),
            )
            return
        if path == "/cockpit/devsecops/model.json":
            access_context = self._resolve_public_cockpit_access_context()
            if not access_context.get("ok"):
                self._send_public_cockpit_blocked(str(access_context.get("finding") or "public_cockpit_login_required"), next_path=path)
                return
            self._send_json(
                200,
                build_cockpit_surface_view_model(
                    self.server.ion_root,  # type: ignore[attr-defined]
                    surface="devsecops",
                    principal=access_context.get("principal") if isinstance(access_context.get("principal"), Mapping) else {},
                ),
            )
            return
        if path in {"/cockpit/previews/model.json", "/cockpit/projects/previews/model.json"}:
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path=path)
                return
            self._send_json(200, build_project_preview_sessions_model(self.server.ion_root))  # type: ignore[attr-defined]
            return
        if path == "/cockpit/system/model.json":
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/system/model.json")
                return
            self._send_json(200, build_system_diagnostics_model(self.server.ion_root))  # type: ignore[attr-defined]
            return
        if path == "/cockpit/build/workspace.json":
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path=path)
                return
            query = parse_qs(urlparse(self.path).query)
            project_id = str((query.get("project_id") or ["ion_dev"])[-1] or "ion_dev")
            probe_preview = str((query.get("probe_preview") or [""])[-1]).lower() in {"1", "true", "yes"}
            try:
                max_items = int((query.get("max_items") or ["8"])[-1] or 8)
            except (TypeError, ValueError):
                max_items = 8
            self._send_json(
                200,
                build_build_workspace_model(
                    self.server.ion_root,  # type: ignore[attr-defined]
                    project_id=project_id,
                    probe_preview=probe_preview,
                    max_items=max_items,
                ),
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
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path=path)
                return
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
            self._send_json(200, build_cockpit_surface_view_model(self.server.ion_root, surface=surface))  # type: ignore[attr-defined]
            return
        if path == "/cockpit/ide/model.json":
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path=path)
                return
            self._send_json(200, build_codex_ide_workbench_model(self.server.ion_root))  # type: ignore[attr-defined]
            return
        if path == "/cockpit/chat/model.json":
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/chat/model.json")
                return
            self._send_json(200, build_dual_codex_chat_model(self.server.ion_root))  # type: ignore[attr-defined]
            return
        if path == "/cockpit/chat/archive.json":
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/chat/archive.json")
                return
            query = parse_qs(urlparse(self.path).query)
            window_start = str((query.get("start") or query.get("window_start") or [""])[-1] or "")
            window_count = str((query.get("count") or query.get("window_count") or [""])[-1] or "")
            self._send_json(
                200,
                build_codex_conversation_archive(
                    self.server.ion_root,  # type: ignore[attr-defined]
                    selected_session_id=str((query.get("session_id") or [""])[-1] or "") or None,
                    query=str((query.get("q") or [""])[-1] or "") or None,
                    selected_window_start=int(window_start) if window_start.isdigit() else None,
                    selected_window_count=int(window_count) if window_count.isdigit() else 500,
                ),
            )
            return
        if path in {"/cockpit/chat/diffs.json", "/cockpit/git/rollback/model.json"}:
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/chat/diffs.json")
                return
            query = parse_qs(urlparse(self.path).query)
            self._send_json(
                200,
                build_codex_git_rollback_model(
                    self.server.ion_root,  # type: ignore[attr-defined]
                    selected_session_id=str((query.get("session_id") or [""])[-1] or "") or None,
                ),
            )
            return
        if path in {"/cockpit/chat/context_timeline.json", "/cockpit/context/timeline.json"}:
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/chat/context_timeline.json")
                return
            query = parse_qs(urlparse(self.path).query)
            limit = str((query.get("limit") or [""])[-1] or "")
            self._send_json(
                200,
                build_codex_context_timeline_model(
                    self.server.ion_root,  # type: ignore[attr-defined]
                    history_limit=int(limit) if limit.isdigit() else 36,
                ),
            )
            return
        if path == "/cockpit/worker/model.json":
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/worker/model.json")
                return
            self._send_json(200, build_worker_cockpit_view_model(self.server.ion_root))  # type: ignore[attr-defined]
            return
        if path in APP_PATHS:
            self._send_html(
                200,
                render_ion_connector_landing(
                    self.server.ion_root,  # type: ignore[attr-defined]
                    public_base_url=self._public_base_url(),
                    active_nav="projects" if path == "/projects" else "home",
                ),
            )
            return
        if path == "/app/status.json":
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/app/status.json")
                return
            self._send_json(200, audit_http_mcp_preview(self.server.ion_root))  # type: ignore[attr-defined]
            return
        if path.startswith("/cockpit/"):
            remaining_path = path[len("/cockpit/"):]
            if "/" not in remaining_path:
                segment = remaining_path
                if segment in COCKPIT_UI_PATHS:
                    ok, finding, token = self._check_public_cockpit_access()
                    if not ok:
                        self._send_public_cockpit_blocked(str(finding), next_path=f"/cockpit/{segment}")
                        return
                    react_html = build_react_cockpit_html(self.server.ion_root)  # type: ignore[attr-defined]
                    if react_html:
                        self._send_bytes(200, react_html.encode("utf-8"), "text/html; charset=utf-8", csp=REACT_CSP)
                        return
                    self._send_public_cockpit_blocked(str(finding), next_path=f"/cockpit/{segment}")
                    return
        if path == "/cockpit/browser-gpt/screen-automation/status":
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit#browser-gpt")
                return
            try:
                result = build_screen_automation_status(self.server.ion_root)  # type: ignore[attr-defined]
            except Exception as exc:
                result = {"ok": False, "finding": "screen_automation_status_failed", "error": exc.__class__.__name__}
            self._send_json(200 if result.get("ok") else 409, result)
            return
        if path != "/health":
            self._send_json(404, {"ok": False, "error": "not_found"})
            return
        self._send_json(
            200,
            {
                "schema_id": "ion.chatgpt_browser_http_mcp_preview.health.v1",
                "ok": True,
                "status": "ready",
                "production_authority": False,
                "live_execution_authority": False,
                "accepted_state_authority": False,
                "secrets_authority": False,
            },
        )

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler name
        path = self.path.split("?", 1)[0]
        if path == "/cockpit/browser-gpt-dom/probe-snapshot":
            try:
                payload = self._read_payload()
                result = record_browser_gpt_dom_probe_snapshot(self.server.ion_root, payload)  # type: ignore[attr-defined]
            except Exception as exc:
                result = {"ok": False, "finding": "probe_snapshot_record_failed", "error": exc.__class__.__name__}
            self._send_json(200 if result.get("ok") else 400, result)
            return
        if path.startswith("/cockpit/browser-gpt/screen-automation/"):
            payload = self._read_payload()
            ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit#browser-gpt")
                return
            action = path.rsplit("/", 1)[-1]
            try:
                if action == "learn":
                    result = learn_screen_automation_state(
                        self.server.ion_root,  # type: ignore[attr-defined]
                        window_id=str(payload.get("window_id") or "") or None,
                        probe_tabs=bool(payload.get("probe_tabs", True)),
                        write=True,
                    )
                elif action == "reload-extension":
                    result = execute_extension_reload(
                        self.server.ion_root,  # type: ignore[attr-defined]
                        dry_run=not bool(payload.get("execute")),
                    )
                elif action == "refresh-tabs":
                    raw_roles = payload.get("roles")
                    roles = (
                        tuple(str(role).strip() for role in raw_roles if str(role).strip())
                        if isinstance(raw_roles, list)
                        else ("chatgpt", "cockpit")
                    )
                    result = execute_tab_refresh(
                        self.server.ion_root,  # type: ignore[attr-defined]
                        roles=roles,
                        dry_run=not bool(payload.get("execute")),
                    )
                else:
                    result = {"ok": False, "finding": "screen_automation_action_not_found", "action": action}
            except Exception as exc:
                result = {"ok": False, "finding": "screen_automation_action_failed", "action": action, "error": exc.__class__.__name__}
            self._send_json(200 if result.get("ok") else 409, result)
            return
        if path == "/cockpit/projects/launch/diagnostics/event":
            payload = self._read_payload()
            ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit#apps")
                return
            try:
                result = app_diagnostics_record_browser_event(
                    self.server.ion_root,  # type: ignore[attr-defined]
                    payload,
                )
            except Exception as exc:
                result = {"ok": False, "finding": "app_diagnostics_event_failed", "error": exc.__class__.__name__}
            self._send_json(200 if result.get("ok") else 409, result)
            return
        if path.startswith("/cockpit/projects/launch/proxy/"):
            payload = self._read_payload()
            ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit#apps")
                return
            parsed = urlparse(self.path)
            rest = parsed.path.removeprefix("/cockpit/projects/launch/proxy/")
            launch_id, _, proxy_path = rest.partition("/")
            result = project_launcher_proxy_fetch(
                self.server.ion_root,  # type: ignore[attr-defined]
                launch_id,
                proxy_path,
                query=parsed.query,
                method="POST",
                body=json.dumps(payload).encode("utf-8"),
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
            origin_ok, origin_finding = self._check_mutation_origin()
            if not origin_ok:
                self._send_public_cockpit_blocked(str(origin_finding), next_path="/cockpit#apps")
                return
            if path.endswith("/config") or path.endswith("/snapshot") or path.endswith("/matrix"):
                ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
                if not ok:
                    self._send_public_cockpit_blocked(str(finding), next_path="/cockpit#apps")
                    return
            else:
                ok, finding, _token = self._check_public_cockpit_access(payload)
                if not ok:
                    self._send_public_cockpit_blocked(str(finding), next_path="/cockpit#apps")
                    return
            try:
                if path.endswith("/config"):
                    result = app_diagnostics_config_update(
                        self.server.ion_root,  # type: ignore[attr-defined]
                        payload,
                    )
                elif path.endswith("/snapshot"):
                    result = app_diagnostics_snapshot(
                        self.server.ion_root,  # type: ignore[attr-defined]
                        payload,
                    )
                elif path.endswith("/matrix"):
                    result = project_launcher_diagnostics_matrix(
                        self.server.ion_root,  # type: ignore[attr-defined]
                        payload,
                    )
                else:
                    result = app_diagnostics_timeline_model(
                        self.server.ion_root,  # type: ignore[attr-defined]
                        payload,
                    )
            except Exception as exc:
                result = {"ok": False, "finding": "app_diagnostics_action_failed", "error": exc.__class__.__name__}
            self._send_json(200 if result.get("ok") else 409, result)
            return
        if path in {"/cockpit/system/preview_action", "/cockpit/system/execute_action"}:
            payload = self._read_payload()
            ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit#system")
                return
            action = payload.get("action") if isinstance(payload.get("action"), dict) else payload
            try:
                if path.endswith("/preview_action"):
                    result = preview_system_diagnostic_action(
                        self.server.ion_root,  # type: ignore[attr-defined]
                        action,
                    )
                    self._send_json(200, {"ok": True, **result})
                else:
                    result = execute_system_diagnostic_action(
                        self.server.ion_root,  # type: ignore[attr-defined]
                        action,
                    )
                    self._send_json(200, {"ok": True, **result})
            except Exception as exc:
                self._send_json(409, {"ok": False, "finding": "system_diagnostics_action_failed", "error": str(exc)})
            return
        if path in {"/cockpit/projects/launch/start", "/cockpit/projects/launch/status", "/cockpit/projects/launch/stop", "/cockpit/projects/launch/diagnostics"}:
            payload = self._read_payload()
            origin_ok, origin_finding = self._check_mutation_origin()
            if not origin_ok:
                self._send_public_cockpit_blocked(str(origin_finding), next_path="/cockpit#projects")
                return
            if path != "/cockpit/projects/launch/stop":
                ok, finding, _token = self._check_public_cockpit_access(payload)
                if not ok:
                    self._send_public_cockpit_blocked(str(finding), next_path="/cockpit#projects")
                    return
            try:
                if path == "/cockpit/projects/launch/start":
                    result = project_launcher_start(
                        self.server.ion_root,  # type: ignore[attr-defined]
                        payload,
                    )
                elif path == "/cockpit/projects/launch/status":
                    result = project_launcher_status(
                        self.server.ion_root,  # type: ignore[attr-defined]
                        payload,
                    )
                elif path == "/cockpit/projects/launch/diagnostics":
                    result = project_launcher_diagnostics(
                        self.server.ion_root,  # type: ignore[attr-defined]
                        payload,
                    )
                else:
                    result = project_launcher_stop(
                        self.server.ion_root,  # type: ignore[attr-defined]
                        payload,
                    )
                    if not result.get("ok") and result.get("finding") == "launch_stop_confirmation_required":
                        ok, finding, _token = self._check_public_cockpit_access(payload)
                        if not ok:
                            self._send_json(401, {"ok": False, "finding": finding, "requires_stop_token": True})
                            return
                        result = project_launcher_stop(
                            self.server.ion_root,  # type: ignore[attr-defined]
                            payload,
                        )
            except Exception as exc:
                result = {"ok": False, "finding": "project_launch_action_failed", "error": exc.__class__.__name__}
            try:
                app_diagnostics_record_http_event(
                    self.server.ion_root,  # type: ignore[attr-defined]
                    route=path,
                    payload=payload,
                    result=result,
                    source="mcp_http_preview",
                )
            except Exception:
                pass
            self._send_json(200 if result.get("ok") else 409, result)
            return
        if path == "/cockpit/projects/organizer/materialize":
            payload = self._read_payload()
            ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit#projects")
                return
            try:
                result = materialize_project_portfolio_action(
                    self.server.ion_root,  # type: ignore[attr-defined]
                    payload,
                )
            except Exception as exc:
                result = {"ok": False, "finding": "project_portfolio_materialize_failed", "error": exc.__class__.__name__}
            self._send_json(200 if result.get("ok") else 409, result)
            return
        project_cockpit_actions = {
            "/cockpit/projects/blocker/create": ("blocker", "create"),
            "/cockpit/projects/blocker/update": ("blocker", "update"),
            "/cockpit/projects/blocker/resolve": ("blocker", "resolve"),
            "/cockpit/projects/question/create": ("question", "create"),
            "/cockpit/projects/question/update": ("question", "update"),
            "/cockpit/projects/question/resolve": ("question", "resolve"),
        }
        if path in project_cockpit_actions:
            payload = self._read_payload()
            ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit#projects")
                return
            record_type, action = project_cockpit_actions[path]
            try:
                result = apply_project_cockpit_action(
                    self.server.ion_root,  # type: ignore[attr-defined]
                    record_type=record_type,
                    action=action,
                    payload=payload,
                )
            except Exception as exc:
                result = {"ok": False, "finding": "request_failed", "error": exc.__class__.__name__}
            self._send_json(200 if result.get("ok") else 400, result)
            return
        if path in {
            "/projects/cosmos/actions/run",
            "/projects/cosmos/browser/capture",
            "/projects/cosmos/patch/preview",
            "/projects/cosmos/patch/apply",
            "/projects/cosmos/patch/revert",
        }:
            payload = self._read_payload()
            ok, finding, token = self._check_public_cockpit_mutation_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/projects/cosmos")
                return
            payload.setdefault("project_id", "cosmos")
            if path == "/projects/cosmos/actions/run":
                result = project_action_run(self.server.ion_root, payload)  # type: ignore[attr-defined]
            elif path == "/projects/cosmos/browser/capture":
                result = project_browser_capture(self.server.ion_root, payload)  # type: ignore[attr-defined]
            elif path == "/projects/cosmos/patch/preview":
                result = project_patch_preview(self.server.ion_root, payload)  # type: ignore[attr-defined]
            elif path == "/projects/cosmos/patch/apply":
                result = project_patch_apply(self.server.ion_root, payload)  # type: ignore[attr-defined]
            else:
                result = project_patch_revert(self.server.ion_root, payload)  # type: ignore[attr-defined]
            if self._wants_json() or path not in {"/projects/cosmos/actions/run", "/projects/cosmos/browser/capture"}:
                self._send_json(200 if result.get("ok") else 409, result)
                return
            self._send_html(
                200 if result.get("ok") else 409,
                render_project_workbench_html(
                    self.server.ion_root,  # type: ignore[attr-defined]
                    public_base_url=self._public_base_url(),
                    auth_token=token,
                    authenticated=True,
                    project_id="cosmos",
                    action_result=result,
                ),
            )
            return
        if path == "/cockpit/auth/token":
            payload = self._read_payload()
            next_path = safe_next_path(str(payload.get("next") or "/cockpit/chat"))
            origin_ok, origin_finding = self._check_mutation_origin()
            if not origin_ok:
                self._send_public_cockpit_blocked(str(origin_finding), next_path=next_path)
                return
            token_result = validate_permission_token(str(payload.get("permission_token") or ""))
            if not token_result.ok:
                self._send_login(status=401, next_path=next_path, finding=token_result.finding)
                return
            self._session_redirect(token_result.principal or {}, next_path)
            return
        if path == "/cockpit/auth/google/start":
            payload = self._read_payload()
            next_path = safe_next_path(str(payload.get("next") or "/cockpit/chat"))
            origin_ok, origin_finding = self._check_mutation_origin()
            if not origin_ok:
                self._send_public_cockpit_blocked(str(origin_finding), next_path=next_path)
                return
            if not google_oauth_configured():
                self._send_login(status=503, next_path=next_path, finding="google_oauth_not_configured")
                return
            secret = cockpit_session_secret()
            if not secret:
                self._send_login(status=503, next_path=next_path, finding="cockpit_session_secret_not_configured")
                return
            nonce, state_cookie = make_oauth_state_cookie(
                secret=secret,
                next_path=next_path,
                invite_token=str(payload.get("invite_token") or ""),
                secure=self._secure_cookie(),
            )
            self._redirect_with_headers(
                build_google_authorization_url(base_url=self._public_base_url(), state=nonce),
                {"Set-Cookie": state_cookie},
            )
            return
        if path == "/cockpit/chat/archive/attach":
            payload = self._read_payload()
            ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/chat")
                return
            result = attach_codex_conversation_to_chat(
                self.server.ion_root,  # type: ignore[attr-defined]
                session_id=str(payload.get("session_id") or ""),
                confirmation=str(payload.get("confirmation") or ""),
                prompt=str(payload.get("prompt") or "") or None,
            )
            self._send_json(200 if result.get("ok") else 400, result)
            return
        if path == "/cockpit/action-branch/invoke":
            from .ion_action_mcp_branch_leaders import action_branch_invoke

            payload = self._read_payload()
            ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit")
                return
            route_args = payload.get("args") if isinstance(payload.get("args"), Mapping) else {}
            approval = payload.get("approval") if isinstance(payload.get("approval"), Mapping) else None
            result = action_branch_invoke(
                self.server.ion_root,  # type: ignore[attr-defined]
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
        if path == "/cockpit/chat/branch":
            payload = self._read_payload()
            ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/chat")
                return
            result = create_chat_branch(
                self.server.ion_root,  # type: ignore[attr-defined]
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
        if path == "/cockpit/chat/context-starter/create":
            payload = self._read_payload()
            ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/chat")
                return
            result = create_fresh_agent_capsule_chat(
                self.server.ion_root,  # type: ignore[attr-defined]
                confirmation=str(payload.get("confirmation") or ""),
                title=str(payload.get("title") or ""),
                domain_id=str(payload.get("domain_id") or ""),
                role_id=str(payload.get("role_id") or ""),
                target_path=str(payload.get("target_path") or ""),
            )
            self._send_json(200 if result.get("ok") else 400, result)
            return
        if path in {
            "/cockpit/chat/git/rollback/capture",
            "/cockpit/git/rollback/capture",
            "/cockpit/chat/git/rollback/preview",
            "/cockpit/git/rollback/preview",
            "/cockpit/chat/git/rollback/apply",
            "/cockpit/git/rollback/apply",
        }:
            payload = self._read_payload()
            ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/chat")
                return
            if path.endswith("/capture"):
                result = capture_codex_diff_checkpoint(self.server.ion_root, payload)  # type: ignore[attr-defined]
            elif path.endswith("/preview"):
                result = preview_codex_git_rollback(self.server.ion_root, payload)  # type: ignore[attr-defined]
            else:
                result = apply_codex_git_rollback(self.server.ion_root, payload)  # type: ignore[attr-defined]
            self._send_json(200 if result.get("ok") else 409, result)
            return
        if path in {"/cockpit/chat/agent/stop"}:
            payload = self._read_payload()
            ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/chat")
                return
            result = stop_active_codex_queue_runner(
                self.server.ion_root,  # type: ignore[attr-defined]
                confirmation=str(payload.get("confirmation") or ""),
                reason=str(payload.get("reason") or "operator_stop_from_chat"),
            )
            self._send_json(200 if result.get("ok") else 409, result)
            return
        if path in {"/chat/file-tree", "/cockpit/chat/file-tree"}:
            payload = self._read_payload()
            ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/chat")
                return
            result = call_chatgpt_connector_tool(
                self.server.ion_root,  # type: ignore[attr-defined]
                "ion_tree_list",
                {
                    "path": str(payload.get("path") or "ION"),
                    "max_depth": _payload_int(payload, "max_depth", 3),
                    "limit": _payload_int(payload, "limit", 700),
                },
            )
            self._send_json(200 if result.get("ok") else 400, result)
            return
        if path in {"/cockpit/chat/turn", "/cockpit/chat/queue", "/cockpit/chat/memory"}:
            try:
                payload = self._read_payload()
                ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
                if not ok:
                    self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/chat")
                    return
                if path == "/cockpit/chat/turn":
                    result = record_chat_turn(
                        self.server.ion_root,  # type: ignore[attr-defined]
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
                elif path == "/cockpit/chat/queue":
                    result = queue_chat_codex_work_packet(
                        self.server.ion_root,  # type: ignore[attr-defined]
                        lane_id=str(payload.get("lane_id") or ""),
                        objective=str(payload.get("objective") or ""),
                        confirmation=str(payload.get("confirmation") or ""),
                        context_refs=_payload_list(payload, "context_refs"),
                    )
                else:
                    result = pin_dual_chat_memory(
                        self.server.ion_root,  # type: ignore[attr-defined]
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
            self._redirect("/cockpit/chat")
            return
        if path == "/cockpit/services/restart":
            payload = self._read_payload()
            ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit")
                return
            result = restart_service(self.server.ion_root, payload)  # type: ignore[attr-defined]
            if self._wants_json():
                self._send_json(200 if result.get("ok") else 409, result)
                return
            self._redirect(safe_next_path(str(payload.get("next") or "/cockpit")))
            return
        if path == "/cockpit/automations/run":
            payload = self._read_payload()
            ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/chat#agents")
                return
            try:
                result = execute_automation_action(self.server.ion_root, payload)  # type: ignore[attr-defined]
            except Exception as exc:
                result = {"ok": False, "finding": "request_failed", "error": exc.__class__.__name__}
            self._send_json(200 if result.get("ok") else 409, result)
            return
        if path in {"/cockpit/domain-weaver/action", "/cockpit/weave/action"}:
            payload = self._read_payload()
            ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit#weave")
                return
            try:
                result = execute_domain_weaver_action(self.server.ion_root, payload)  # type: ignore[attr-defined]
            except Exception as exc:
                result = {"ok": False, "finding": "request_failed", "error": exc.__class__.__name__}
            self._send_json(200 if result.get("ok") else 409, result)
            return
        if path in {
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
            payload = self._read_payload()
            ok, finding, _token = self._check_public_cockpit_mutation_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/chat#agents")
                return
            try:
                if path == "/cockpit/agents/spawn-template":
                    result = execute_agent_spawn_template(self.server.ion_root, payload)  # type: ignore[attr-defined]
                elif path == "/cockpit/agents/comms/send":
                    result = send_agent_message(self.server.ion_root, payload)  # type: ignore[attr-defined]
                elif path == "/cockpit/agents/comms/ack":
                    result = ack_agent_message(self.server.ion_root, payload)  # type: ignore[attr-defined]
                elif path == "/cockpit/agents/comms/list":
                    result = list_agent_threads(
                        self.server.ion_root,  # type: ignore[attr-defined]
                        role_id=str(payload.get("role_id") or "") or None,
                        channel_id=str(payload.get("channel_id") or "") or None,
                        limit=int(payload.get("limit") or 50),
                    )
                elif path == "/cockpit/agents/comms/thread":
                    result = read_agent_thread(
                        self.server.ion_root,  # type: ignore[attr-defined]
                        str(payload.get("thread_id") or ""),
                        role_id=str(payload.get("role_id") or "") or None,
                        limit=int(payload.get("limit") or 200),
                    )
                elif path == "/cockpit/agents/comms/run/start":
                    result = maybe_audit_agent_comms_result(self.server.ion_root, payload, start_agent_comms_run(self.server.ion_root, payload))  # type: ignore[attr-defined]
                elif path == "/cockpit/agents/comms/run/pickup":
                    result = maybe_audit_agent_comms_result(self.server.ion_root, payload, pickup_agent_comms_run(self.server.ion_root, payload))  # type: ignore[attr-defined]
                elif path == "/cockpit/agents/comms/run/continue":
                    result = maybe_audit_agent_comms_result(self.server.ion_root, payload, continue_agent_comms_run(self.server.ion_root, payload))  # type: ignore[attr-defined]
                elif path == "/cockpit/agents/comms/run/start-worker":
                    result = maybe_audit_agent_comms_result(self.server.ion_root, payload, start_agent_comms_run_worker(self.server.ion_root, payload))  # type: ignore[attr-defined]
                elif path == "/cockpit/agents/comms/run/audit":
                    result = audit_agent_comms_run(self.server.ion_root, payload)  # type: ignore[attr-defined]
                elif path == "/cockpit/agents/dispatcher/route":
                    result = route_steward_dispatcher(self.server.ion_root, payload)  # type: ignore[attr-defined]
                elif path == "/cockpit/agents/dispatcher/tick":
                    result = tick_steward_dispatcher(self.server.ion_root, payload)  # type: ignore[attr-defined]
                elif path == "/cockpit/agents/dispatcher/runner":
                    result = run_steward_dispatcher_runner(self.server.ion_root, payload)  # type: ignore[attr-defined]
                elif path == "/cockpit/agents/dispatcher/pause":
                    result = pause_steward_dispatcher(self.server.ion_root, payload)  # type: ignore[attr-defined]
                else:
                    result = create_agent_message_branch(self.server.ion_root, payload)  # type: ignore[attr-defined]
            except Exception as exc:
                result = {"ok": False, "finding": "request_failed", "error": exc.__class__.__name__}
            self._send_json(200 if result.get("ok") else 409, result)
            return
        if path != "/mcp":
            self._send_json(404, {"ok": False, "error": "not_found"})
            return
        ok, finding, _token = self._check_public_cockpit_access()
        if not ok:
            self._send_public_cockpit_blocked(str(finding), next_path="/mcp")
            return
        length = int(self.headers.get("content-length") or "0")
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
            response = handle_mcp_jsonrpc(self.server.ion_root, payload)  # type: ignore[attr-defined]
        except Exception as exc:
            self._send_json(400, {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}})
            return
        if response is None:
            self.send_response(204)
            self.end_headers()
            return
        self._send_json(200, response)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - stdlib signature
        return


def make_http_server(root: str | Path, host: str = DEFAULT_BIND_HOST, port: int = DEFAULT_PORT) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), IonChatGPTPreviewHandler)
    server.ion_root = Path(root).resolve()  # type: ignore[attr-defined]
    return server


def documented_launch_requests_serve(argv: list[str]) -> bool:
    """Honor the V120 setup-guide launch shape without changing no-arg audit mode."""
    explicit_bind = any(arg in {"--host", "--port"} or arg.startswith("--host=") or arg.startswith("--port=") for arg in argv)
    explicit_audit = any(arg in {"--self-test", "--write", "--json"} for arg in argv)
    return explicit_bind and not explicit_audit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ION ChatGPT browser HTTP MCP preview.")
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--host", default=DEFAULT_BIND_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", default=None)
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--json", action="store_true")
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    args = parser.parse_args(argv)
    serve_requested = args.serve or documented_launch_requests_serve(raw_argv)

    if args.write:
        result = write_http_mcp_preview_audit(args.ion_root, output=args.output)
        print(json.dumps(result, indent=2, sort_keys=True) if args.json or args.self_test else result["verdict"])
        return 0 if result["accepted"] else 1

    if args.self_test or not serve_requested:
        result = audit_http_mcp_preview(args.ion_root)
        print(json.dumps(result, indent=2, sort_keys=True) if args.json or args.self_test else result["verdict"])
        return 0 if result["accepted"] else 1

    server = make_http_server(args.ion_root, args.host, args.port)
    print(f"ION ChatGPT HTTP MCP preview listening on http://{args.host}:{args.port}/mcp")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
