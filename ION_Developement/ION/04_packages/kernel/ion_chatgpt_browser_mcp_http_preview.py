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
from urllib.parse import parse_qs, urlencode, urlparse
import urllib.error
import urllib.request

from .ion_chatgpt_browser_mcp_connector_contract import (
    BOUNDED_QUEUE_RECEIPT_TOOLS,
    FORBIDDEN_CAPABILITIES,
    STATUS_READ_TOOLS,
    audit_chatgpt_browser_mcp_connector_contract,
    call_chatgpt_connector_tool,
)
from .ion_cockpit_view_model import (
    build_cockpit_view_model,
    build_worker_cockpit_view_model,
)
from .ion_cockpit_service_manager import restart_service
from .ion_dual_codex_chat import (
    WRITE_CONFIRMATION_TOKEN,
    build_dual_codex_chat_model,
    pin_dual_chat_memory,
    queue_chat_codex_work_packet,
    record_chat_turn,
    render_dual_codex_chat_html,
)
from .ion_local_cockpit_app import build_cockpit_html
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

SCHEMA_ID = "ion.chatgpt_browser_http_mcp_preview.v1"
VERSION_LINE = "V121_CHATGPT_BROWSER_HTTP_MCP_PREVIEW"
READY_VERDICT = "ION_CHATGPT_BROWSER_HTTP_MCP_PREVIEW_READY"
BLOCKED_VERDICT = "ION_CHATGPT_BROWSER_HTTP_MCP_PREVIEW_BLOCKED"
WRITE_CONFIRMATION_TOKEN = "ION_BOUNDED_WRITE_CONFIRMED"
DEFAULT_BIND_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
OUTPUT_RELATIVE_PATH = Path("ION/05_context/current/CHATGPT_BROWSER_HTTP_MCP_PREVIEW_V121.json")
APP_PATHS = {"/", "/app", "/ion", "/projects"}
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


def _json_text(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True)


def _html_text(value: Any) -> str:
    return html.escape(str(value), quote=True)


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
    if auth_token and path.startswith("/cockpit") and path not in {"/cockpit/login", "/cockpit/logout"}:
        href = f"{path}{'&' if '?' in path else '?'}{urlencode({'token': auth_token})}"
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
                "preview_target": {"type": "string", "enum": ["worker_stdout", "worker_stderr"]},
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
                "idempotency_key": {
                    "type": "string",
                    "description": "Stable key for safe retries; repeated keys return the original patch receipt.",
                },
                "client_request_id": {"type": "string"},
                "force_new": {"type": "boolean"},
            })
            required = ["confirmation"]
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
                "force_new": {"type": "boolean"},
            })
            required = ["project_id", "confirmation"]
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
            },
            "required": ["project_id", "receipt_path", "confirmation"],
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
            },
            "required": ["target_path", "text", "confirmation"],
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
            },
            "required": ["artifact_name", "confirmation"],
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
            },
            "required": ["upload_id", "chunk_index", "data_base64", "confirmation"],
            "additionalProperties": False,
        }
    if name == "ion_artifact_upload_commit":
        return {
            "type": "object",
            "properties": {
                "upload_id": {"type": "string"},
                "confirmation": {"type": "string"},
            },
            "required": ["upload_id", "confirmation"],
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


def _requires_write_confirmation(tool_name: str, args: Mapping[str, Any]) -> bool:
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
        if _requires_write_confirmation(tool_name, arguments):
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
      padding: 6px 10px;
      border: 1px solid var(--line);
      border-radius: 2px;
      color: var(--muted);
      font-size: 13px;
      text-transform: uppercase;
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
      .project-grid,
      .port-grid {{ grid-template-columns: 1fr; }}
      .tools {{ columns: 1; }}
      main {{ padding-top: 28px; }}
    }}
    @media (min-width: 761px) and (max-width: 1100px) {{
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
    token_input = f'<input type="hidden" name="public_token" value="{_html_text(auth_token)}">' if auth_token else ""
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
                f'{token_input}'
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
            f'{token_input}'
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
        ("stale", _worker_badge(active.get("stale_active_reference_detected"))),
        ("zombie", _worker_badge(active.get("zombie_state_detected"))),
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


def _worker_log_cards(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "<article class=\"card\"><h3>Logs</h3><p>No logs available.</p></article>"
    cards: list[str] = []
    for row in rows:
        text = str(row.get("text") or "").strip()
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
    query = f"?{urlencode({'token': auth_token})}" if auth_token else ""
    model_endpoint = f"/cockpit/worker/model.json{query}"
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

    render({json.dumps(model)});
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
        self.end_headers()
        self.wfile.write(body)

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

    def _request_token(self, payload: Mapping[str, Any] | None = None) -> str:
        auth = self.headers.get("authorization") or ""
        if auth.lower().startswith("bearer "):
            return auth.split(" ", 1)[1].strip()
        query = parse_qs(urlparse(self.path).query)
        if query.get("token"):
            return str(query["token"][-1])
        if payload and payload.get("public_token"):
            return str(payload.get("public_token") or "")
        return ""

    def _check_public_cockpit_access(self, payload: Mapping[str, Any] | None = None) -> tuple[bool, str | None, str | None]:
        secret = cockpit_session_secret()
        if secret:
            session = validate_session_cookie(self.headers.get("cookie"), secret=secret)
            if session.ok:
                return True, None, None
        supplied = self._request_token(payload)
        if supplied:
            token_result = validate_permission_token(supplied)
            if token_result.ok:
                return True, None, supplied
            return False, token_result.finding or "permission_token_invalid", None
        if not secret and not validate_permission_token(os.environ.get(PUBLIC_COCKPIT_TOKEN_ENV) or "").ok and not google_oauth_configured():
            return False, "public_cockpit_auth_not_configured", None
        return False, "public_cockpit_login_required", None

    def _login_path(self, next_path: str | None = None, finding: str | None = None) -> str:
        params: dict[str, str] = {"next": safe_next_path(next_path or self.path)}
        if finding:
            params["finding"] = finding
        return "/cockpit/login?" + urlencode(params)

    def _send_public_cockpit_blocked(self, finding: str, *, next_path: str | None = None) -> None:
        if not self._wants_json() and finding in {"public_cockpit_login_required", "permission_token_required", "permission_token_invalid"}:
            self._redirect(self._login_path(next_path or self.path, None if finding == "public_cockpit_login_required" else finding))
            return
        self._send_json(
            503 if finding == "public_cockpit_auth_not_configured" else 401,
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

    def _send_bytes(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _optional_public_cockpit_access(self) -> tuple[bool, str | None]:
        ok, _finding, token = self._check_public_cockpit_access()
        return ok, token

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
        if path == "/projects/cosmos/preview" or path.startswith("/projects/cosmos/preview/"):
            self._send_project_preview_proxy("cosmos", path)
            return
        if path in {"/projects", "/projects/", "/projects/cosmos", "/projects/cosmos/"}:
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
            self.send_header("Set-Cookie", clear_cookie_header(SESSION_COOKIE, secure=self._secure_cookie()))
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
        if path in {"/cockpit", "/cockpit/"}:
            ok, finding, token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit")
                return
            html_text = build_cockpit_html(build_cockpit_view_model(self.server.ion_root))  # type: ignore[attr-defined]
            replacement = f'href="/cockpit?token={_html_text(token)}"' if token else 'href="/cockpit"'
            html_text = html_text.replace('href="/cockpit"', replacement)
            if token:
                html_text = html_text.replace(
                    '<input type="hidden" name="confirmation"',
                    f'<input type="hidden" name="auth_token" value="{_html_text(token)}"><input type="hidden" name="confirmation"',
                )
            self._send_html(200, wrap_helixion_site_shell(html_text, "cockpit", auth_token=token))
            return
        if path in {"/cockpit/chat", "/cockpit/chat/"}:
            ok, finding, token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/chat")
                return
            model = build_dual_codex_chat_model(self.server.ion_root, write=True)  # type: ignore[attr-defined]
            chat_html = render_dual_codex_chat_html(model, base_path="/cockpit/chat", auth_token=token)
            self._send_html(200, wrap_helixion_site_shell(chat_html, "chat", auth_token=token))
            return
        if path in {"/cockpit/worker", "/cockpit/worker/"}:
            ok, finding, token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/worker")
                return
            self._send_html(
                200,
                render_codex_worker_live_status_html(self.server.ion_root, auth_token=token),  # type: ignore[attr-defined]
            )
            return
        if path == "/cockpit/model.json":
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/model.json")
                return
            self._send_json(200, build_cockpit_view_model(self.server.ion_root))  # type: ignore[attr-defined]
            return
        if path == "/cockpit/chat/model.json":
            ok, finding, _token = self._check_public_cockpit_access()
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit/chat/model.json")
                return
            self._send_json(200, build_dual_codex_chat_model(self.server.ion_root))  # type: ignore[attr-defined]
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
            self._send_json(200, audit_http_mcp_preview(self.server.ion_root))  # type: ignore[attr-defined]
            return
        if path != "/health":
            self._send_json(404, {"ok": False, "error": "not_found"})
            return
        self._send_json(200, audit_http_mcp_preview(self.server.ion_root))  # type: ignore[attr-defined]

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler name
        path = self.path.split("?", 1)[0]
        if path in {
            "/projects/cosmos/actions/run",
            "/projects/cosmos/browser/capture",
            "/projects/cosmos/patch/preview",
            "/projects/cosmos/patch/apply",
            "/projects/cosmos/patch/revert",
        }:
            payload = self._read_payload()
            ok, finding, token = self._check_public_cockpit_access(payload)
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
            token_result = validate_permission_token(str(payload.get("permission_token") or ""))
            if not token_result.ok:
                self._send_login(status=401, next_path=next_path, finding=token_result.finding)
                return
            self._session_redirect(token_result.principal or {}, next_path)
            return
        if path == "/cockpit/auth/google/start":
            payload = self._read_payload()
            next_path = safe_next_path(str(payload.get("next") or "/cockpit/chat"))
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
        if path in {"/cockpit/chat/turn", "/cockpit/chat/queue", "/cockpit/chat/memory"}:
            try:
                payload = self._read_payload()
                ok, finding, token = self._check_public_cockpit_access(payload)
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
                    )
                elif path == "/cockpit/chat/queue":
                    result = queue_chat_codex_work_packet(
                        self.server.ion_root,  # type: ignore[attr-defined]
                        lane_id=str(payload.get("lane_id") or ""),
                        objective=str(payload.get("objective") or ""),
                        confirmation=str(payload.get("confirmation") or ""),
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
                token = None
            if self._wants_json():
                self._send_json(200 if result.get("ok") else 400, result)
                return
            suffix = f"?token={token}" if token else ""
            self._redirect(f"/cockpit/chat{suffix}")
            return
        if path == "/cockpit/services/restart":
            payload = self._read_payload()
            ok, finding, _token = self._check_public_cockpit_access(payload)
            if not ok:
                self._send_public_cockpit_blocked(str(finding), next_path="/cockpit")
                return
            result = restart_service(self.server.ion_root, payload)  # type: ignore[attr-defined]
            if self._wants_json():
                self._send_json(200 if result.get("ok") else 409, result)
                return
            self._redirect(safe_next_path(str(payload.get("next") or "/cockpit")))
            return
        if path != "/mcp":
            self._send_json(404, {"ok": False, "error": "not_found"})
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
