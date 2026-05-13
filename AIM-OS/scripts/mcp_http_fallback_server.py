#!/usr/bin/env python3
"""
Fallback HTTP bridge for AIM-OS MCP tools.

Use this when Cursor's command server on :5001 is unavailable.
It exposes a compatible minimal surface:
  - GET  /health
  - GET  /mcp/list
  - POST /mcp/execute  { "tool": "...", "arguments": { ... } }
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import threading
import traceback
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import socketserver
from typing import Any, Dict, Tuple
from urllib.parse import urlparse

# Import security module
try:
    from security import get_security_gate, generate_initial_key
except ImportError:
    # Graceful fallback if security.py not on path
    import importlib.util as _ilu
    _sec_spec = _ilu.spec_from_file_location("security", os.path.join(os.path.dirname(__file__), "security.py"))
    if _sec_spec and _sec_spec.loader:
        _sec_mod = _ilu.module_from_spec(_sec_spec)
        _sec_spec.loader.exec_module(_sec_mod)
        get_security_gate = _sec_mod.get_security_gate  # type: ignore[attr-defined]
        generate_initial_key = _sec_mod.generate_initial_key  # type: ignore[attr-defined]
    else:
        raise

# Import SENTINEL engine
try:
    from sentinel import get_sentinel
except ImportError:
    _sent_spec = _ilu.spec_from_file_location("sentinel", os.path.join(os.path.dirname(__file__), "sentinel.py"))  # type: ignore[possibly-undefined]
    if _sent_spec and _sent_spec.loader:
        _sent_mod = _ilu.module_from_spec(_sent_spec)
        _sent_spec.loader.exec_module(_sent_mod)
        get_sentinel = _sent_mod.get_sentinel  # type: ignore[attr-defined]
    else:
        get_sentinel = None  # type: ignore[assignment]

# Log file for tool calls (observability — who uses MCP, when)
MCP_TOOL_CALL_LOG = os.path.join(os.path.dirname(__file__), "..", "data", "mcp", "mcp_tool_calls.jsonl")


def _log(message: str) -> None:
    print(f"[MCP-HTTP-FALLBACK] {message}", file=sys.stderr, flush=True)


class MCPHTTPBridge:
    """HTTP wrapper around SimpleMCPServer tool invocation."""

    def __init__(self, server_cls: Any, memory_dir: str) -> None:
        self.server_cls = server_cls
        self.memory_dir = memory_dir
        self.server = None
        self.request_id = 1
        self._init_lock = threading.Lock()
        self._init_error: str | None = None

    def _next_id(self) -> int:
        current = self.request_id
        self.request_id += 1
        return current

    def _ensure_server(self) -> Any:
        if self.server is not None:
            return self.server
        with self._init_lock:
            if self.server is not None:
                return self.server
            _log("Initializing SimpleMCPServer (lazy init)...")
            try:
                self.server = self.server_cls(memory_directory=self.memory_dir)
                self._init_error = None
            except Exception as exc:
                self._init_error = str(exc)
                raise
        return self.server

    def health(self) -> Dict[str, Any]:
        return {
            "ready": self.server is not None,
            "init_error": self._init_error,
        }

    def list_os_processes(self) -> Dict[str, Any]:
        """List Python and Node processes visible to the OS."""
        import subprocess
        try:
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-Process python,node -ErrorAction SilentlyContinue | '
                 'Select-Object Id, ProcessName, CPU, '
                 '@{N="MemMB";E={[math]::Round($_.WorkingSet64/1MB,1)}}, '
                 '@{N="UptimeMin";E={[math]::Round(((Get-Date)-$_.StartTime).TotalMinutes,1)}} | '
                 'ConvertTo-Json -Compress'],
                capture_output=True, text=True, timeout=5
            )
            if result.stdout.strip():
                data = json.loads(result.stdout)
                # PowerShell returns single object if only one process
                if isinstance(data, dict):
                    data = [data]
                return {"success": True, "processes": data}
            return {"success": True, "processes": []}
        except Exception as exc:
            return {"success": False, "error": str(exc), "processes": []}

    def kill_process(self, pid: int) -> Dict[str, Any]:
        """Kill a specific PID. Safety: won't kill own PID."""
        import signal
        my_pid = os.getpid()
        if pid == my_pid:
            return {"success": False, "error": "Cannot kill self"}
        try:
            os.kill(pid, signal.SIGTERM)
            return {"success": True, "killed": pid}
        except ProcessLookupError:
            return {"success": False, "error": f"PID {pid} not found"}
        except PermissionError:
            return {"success": False, "error": f"Permission denied for PID {pid}"}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def list_tools(self) -> Dict[str, Any]:
        server = self._ensure_server()
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list",
            "params": {},
        }
        response = server.handle_request(request)
        if not response:
            return {"success": False, "error": "No response from MCP server"}
        if "error" in response:
            return {"success": False, "error": response["error"].get("message", "Unknown MCP error")}
        tools = response.get("result", {}).get("tools", [])
        return {"success": True, "count": len(tools), "tools": tools}

    def execute_tool(self, tool: str, arguments: Dict[str, Any] | None) -> Dict[str, Any]:
        server = self._ensure_server()
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool,
                "arguments": arguments or {},
            },
        }
        response = server.handle_request(request)
        if not response:
            return {"success": False, "error": "No response from MCP server"}
        if "error" in response:
            return {
                "success": False,
                "error": response["error"].get("message", "Unknown MCP error"),
                "code": response["error"].get("code"),
            }

        raw_text = (
            response.get("result", {})
            .get("content", [{}])[0]
            .get("text", "")
        )
        if not raw_text:
            return {"success": True, "result": {}}

        try:
            parsed_result = json.loads(raw_text)
        except Exception:
            parsed_result = {"raw": raw_text}

        return {"success": True, "result": parsed_result}


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: Dict[str, Any], gate=None, origin=None) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    # Use SecurityGate CORS if available, otherwise permissive for local
    if gate:
        cors = gate.get_cors_headers(origin)
        for k, v in cors.items():
            handler.send_header(k, v)
    else:
        handler.send_header("Access-Control-Allow-Origin", "*")
        handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
    handler.end_headers()
    handler.wfile.write(body)


def build_handler(bridge: MCPHTTPBridge, port: int):
    gate = get_security_gate()
    sentinel = get_sentinel() if get_sentinel is not None else None  # type: ignore[comparison-overlap]

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:
            _log(f"{self.client_address[0]} - {fmt % args}")

        def _check_security(self, path: str, method: str) -> bool:
            """Run SENTINEL + SecurityGate checks. Returns True if allowed."""
            ip = self.client_address[0]
            token = self.headers.get("Authorization", "")
            origin = self.headers.get("Origin", "")
            ua = self.headers.get("User-Agent", "")

            # SENTINEL honeypot intercept (before SecurityGate)
            if sentinel and sentinel.is_banned(ip):
                _json_response(self, 403, {
                    "success": False, "error": "Access denied",
                }, gate, origin)
                return False

            # SecurityGate check
            result = gate.check(ip=ip, path=path, method=method, token=token, user_agent=ua, origin=origin)
            blocked = not result["allowed"]

            # Feed to SENTINEL for NL logging and analysis
            if sentinel:
                sentinel.process_request({
                    "ip": ip, "path": path, "method": method,
                    "blocked": blocked, "reason": result.get("reason", ""),
                    "user_agent": ua,
                })

            if blocked:
                _json_response(self, 403, {
                    "success": False,
                    "error": f"Access denied: {result['reason']}",
                    "reason": result["reason"],
                }, gate, origin)
                return False
            return True

        def do_OPTIONS(self) -> None:
            origin = self.headers.get("Origin", "")
            _json_response(self, 200, {"success": True}, gate, origin)

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            origin = self.headers.get("Origin", "")

            # Security check
            if not self._check_security(path, "GET"):
                return

            if path == "/health":
                bridge_health = bridge.health()
                _json_response(self, 200, {
                    "status": "ok",
                    "mode": "fallback-http-bridge",
                    "port": port,
                    "source": "scripts/mcp_http_fallback_server.py",
                    "ready": bridge_health.get("ready"),
                    "init_error": bridge_health.get("init_error"),
                    "security": "active",
                }, gate, origin)
                return

            if path == "/processes":
                result = bridge.list_os_processes()
                _json_response(self, 200, result)
                return

            if path == "/connections":
                conn_file = os.path.join(os.path.dirname(__file__), "..", "data", "mcp", "connections.json")
                try:
                    if os.path.exists(conn_file):
                        with open(conn_file, "r") as f:
                            data = json.load(f)
                        _json_response(self, 200, data)
                    else:
                        _json_response(self, 200, {"connections": {}, "note": "No connection manager running"})
                except Exception as exc:
                    _json_response(self, 500, {"success": False, "error": str(exc)})
                return

            if path == "/mcp/list":
                try:
                    result = bridge.list_tools()
                    _json_response(self, 200 if result.get("success") else 500, result, gate, origin)
                except Exception as exc:
                    _log("Unhandled list exception:\n" + traceback.format_exc())
                    _json_response(self, 500, {"success": False, "error": str(exc)}, gate, origin)
                return

            # ─── Security Endpoints ───
            if path == "/security/report":
                report = gate.get_security_report()
                _json_response(self, 200, report, gate, origin)
                return

            if path == "/security/keys":
                keys = gate.keys.list_keys()
                _json_response(self, 200, {"keys": keys}, gate, origin)
                return

            # ─── SENTINEL Endpoints ───
            if path == "/sentinel/feed":
                if sentinel:
                    feed = sentinel.get_nl_feed(limit=40)
                    _json_response(self, 200, {"feed": feed, "count": len(feed)}, gate, origin)
                else:
                    _json_response(self, 200, {"feed": [], "count": 0, "note": "SENTINEL not active"}, gate, origin)
                return

            if path == "/sentinel/status":
                if sentinel:
                    status = sentinel.get_status()
                    _json_response(self, 200, status, gate, origin)
                else:
                    _json_response(self, 200, {"threat_level": "UNKNOWN", "note": "SENTINEL not active"}, gate, origin)
                return

            if path == "/sentinel/telemetry":
                if sentinel and hasattr(sentinel, "telemetry") and sentinel.telemetry:
                    telem = sentinel.telemetry.get_telemetry_status()
                    _json_response(self, 200, telem, gate, origin)
                else:
                    _json_response(self, 200, {"status": "unavailable"}, gate, origin)
                return

            if path == "/sentinel/audit":
                if sentinel and hasattr(sentinel, "telemetry") and sentinel.telemetry:
                    entries = sentinel.telemetry.ledger.get_recent(50)
                    verify = sentinel.telemetry.ledger.verify_chain(100)
                    _json_response(self, 200, {"entries": entries, "chain": verify}, gate, origin)
                else:
                    _json_response(self, 200, {"entries": [], "chain": {"valid": True}}, gate, origin)
                return

            if path == "/sentinel/baselines":
                if sentinel and hasattr(sentinel, "host_baselines") and sentinel.host_baselines:
                    status = sentinel.host_baselines.get_status()
                    _json_response(self, 200, status, gate, origin)
                else:
                    _json_response(self, 200, {"status": "unavailable"}, gate, origin)
                return

            if path == "/sentinel/scan":
                if sentinel and hasattr(sentinel, "host_baselines") and sentinel.host_baselines:
                    results = sentinel.host_baselines.run_all_scans()
                    _json_response(self, 200, results, gate, origin)
                else:
                    _json_response(self, 200, {"status": "unavailable"}, gate, origin)
                return

            if path == "/sentinel/sessions":
                if sentinel and hasattr(sentinel, "sessions") and sentinel.sessions:
                    _json_response(self, 200, {
                        "status": sentinel.sessions.get_status(),
                        "sessions": sentinel.sessions.get_all_sessions(),
                    }, gate, origin)
                else:
                    _json_response(self, 200, {"status": "unavailable"}, gate, origin)
                return

            if path == "/sentinel/wraith/report":
                if sentinel and hasattr(sentinel, "wraith") and sentinel.wraith:
                    _json_response(self, 200, sentinel.wraith.get_report(), gate, origin)
                else:
                    _json_response(self, 200, {"status": "unavailable"}, gate, origin)
                return

            if path == "/sentinel/wraith/library":
                if sentinel and hasattr(sentinel, "wraith") and sentinel.wraith:
                    _json_response(self, 200, sentinel.wraith.get_library(), gate, origin)
                else:
                    _json_response(self, 200, {"status": "unavailable"}, gate, origin)
                return

            if path == "/sentinel/policies":
                if sentinel and hasattr(sentinel, "policy_engine") and sentinel.policy_engine:
                    _json_response(self, 200, {
                        "status": sentinel.policy_engine.get_status(),
                        "policies": sentinel.policy_engine.get_policies(),
                        "recent_enforcements": sentinel.policy_engine.get_enforcement_log(10),
                    }, gate, origin)
                else:
                    _json_response(self, 200, {"status": "unavailable"}, gate, origin)
                return

            if path == "/sentinel/governance":
                if sentinel and hasattr(sentinel, "governance") and sentinel.governance:
                    _json_response(self, 200, {
                        "status": sentinel.governance.get_status(),
                        "tool_policies": sentinel.governance.get_policies(),
                        "recent_decisions": sentinel.governance.get_decision_log(10),
                    }, gate, origin)
                else:
                    _json_response(self, 200, {"status": "unavailable"}, gate, origin)
                return

            if path == "/sentinel/phantom":
                if sentinel and hasattr(sentinel, "phantom") and sentinel.phantom:
                    _json_response(self, 200, {
                        "status": sentinel.phantom.get_status(),
                        "adversaries": sentinel.phantom.get_adversary_profiles(10),
                        "roe": sentinel.phantom.get_roe(),
                        "countermeasures": sentinel.phantom.get_countermeasure_catalog(),
                    }, gate, origin)
                else:
                    _json_response(self, 200, {"status": "unavailable"}, gate, origin)
                return

            if path == "/sentinel/recon":
                if sentinel and hasattr(sentinel, "recon") and sentinel.recon:
                    _json_response(self, 200, {
                        "status": sentinel.recon.get_status(),
                        "intel_reports": sentinel.recon.get_intel_reports(10),
                        "mitre_map": sentinel.recon.get_mitre_map(),
                        "known_tools": sentinel.recon.get_known_tools(),
                    }, gate, origin)
                else:
                    _json_response(self, 200, {"status": "unavailable"}, gate, origin)
                return

            if path == "/sentinel/chronicle":
                if sentinel and hasattr(sentinel, "chronicle") and sentinel.chronicle:
                    _json_response(self, 200, {
                        "status": sentinel.chronicle.get_status(),
                        "recent_entries": sentinel.chronicle.audit_chain.get_recent(15),
                        "active_incidents": sentinel.chronicle.get_active_incidents(),
                        "all_incidents": sentinel.chronicle.get_all_incidents(10),
                        "compliance": sentinel.chronicle.generate_compliance_report(),
                    }, gate, origin)
                else:
                    _json_response(self, 200, {"status": "unavailable"}, gate, origin)
                return

            if path == "/sentinel/nexus":
                if sentinel and hasattr(sentinel, "nexus") and sentinel.nexus:
                    _json_response(self, 200, sentinel.nexus.get_threat_landscape(), gate, origin)
                else:
                    _json_response(self, 200, {"status": "unavailable"}, gate, origin)
                return

            _json_response(self, 404, {"success": False, "error": "Endpoint not found"}, gate, origin)

        def do_POST(self) -> None:
            path = urlparse(self.path).path
            origin = self.headers.get("Origin", "")

            # Security check
            if not self._check_security(path, "POST"):
                return

            # ─── Security Key Generation ───
            if path == "/security/generate-key":
                try:
                    content_length = int(self.headers.get("Content-Length", "0"))
                    raw = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                    payload = json.loads(raw)
                    label = payload.get("label", "joc-generated")
                    scopes = payload.get("scopes", ["*"])
                    raw_key = gate.keys.generate_key(label=label, scopes=scopes)
                    _json_response(self, 200, {
                        "success": True,
                        "key": raw_key,
                        "label": label,
                        "warning": "Save this key now — it will never be shown again!",
                    }, gate, origin)
                except Exception as exc:
                    _json_response(self, 500, {"success": False, "error": str(exc)}, gate, origin)
                return

            if path == "/processes/kill":
                try:
                    content_length = int(self.headers.get("Content-Length", "0"))
                    raw = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                    payload = json.loads(raw)
                    pid = payload.get("pid")
                    if not pid or not isinstance(pid, int):
                        _json_response(self, 400, {"success": False, "error": "Missing or invalid pid (integer required)"})
                        return
                    result = bridge.kill_process(pid)
                    _json_response(self, 200 if result["success"] else 400, result)
                except Exception as exc:
                    _json_response(self, 500, {"success": False, "error": str(exc)})
                return

            # ─── SENTINEL Session Registration ───
            if path == "/sentinel/session/register":
                try:
                    content_length = int(self.headers.get("Content-Length", "0"))
                    raw = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                    payload = json.loads(raw)
                    agent_name = payload.get("agent_name", "")
                    genome_hash = payload.get("genome_hash", "")
                    capabilities = payload.get("capabilities", [])
                    if not agent_name:
                        _json_response(self, 400, {"error": "agent_name required"}, gate, origin)
                        return
                    if sentinel and hasattr(sentinel, "sessions") and sentinel.sessions:
                        result = sentinel.sessions.register(agent_name, genome_hash, capabilities)
                        _json_response(self, 200, result, gate, origin)
                    else:
                        _json_response(self, 503, {"error": "Sessions unavailable"}, gate, origin)
                except Exception as exc:
                    _json_response(self, 500, {"error": str(exc)}, gate, origin)
                return

            # ─── SENTINEL Session Validation ───
            if path == "/sentinel/session/validate":
                try:
                    content_length = int(self.headers.get("Content-Length", "0"))
                    raw = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                    payload = json.loads(raw)
                    token = payload.get("token", "")
                    if not token:
                        _json_response(self, 400, {"error": "token required"}, gate, origin)
                        return
                    if sentinel and hasattr(sentinel, "sessions") and sentinel.sessions:
                        result = sentinel.sessions.validate(token)
                        _json_response(self, 200, result, gate, origin)
                    else:
                        _json_response(self, 503, {"error": "Sessions unavailable"}, gate, origin)
                except Exception as exc:
                    _json_response(self, 500, {"error": str(exc)}, gate, origin)
                return

            # ─── WRAITH Test Suite ───
            if path == "/sentinel/wraith/run":
                try:
                    content_length = int(self.headers.get("Content-Length", "0"))
                    raw = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                    payload = json.loads(raw)
                    categories = payload.get("categories", None)
                    if sentinel and hasattr(sentinel, "wraith") and sentinel.wraith:
                        report = sentinel.wraith.run_dry_suite(categories)
                        _json_response(self, 200, report, gate, origin)
                    else:
                        _json_response(self, 503, {"error": "WRAITH unavailable"}, gate, origin)
                except Exception as exc:
                    _json_response(self, 500, {"error": str(exc)}, gate, origin)
                return

            # ─── WRAITH Test Response ───
            if path == "/sentinel/wraith/test":
                try:
                    content_length = int(self.headers.get("Content-Length", "0"))
                    raw = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                    payload = json.loads(raw)
                    pattern_id = payload.get("pattern_id", "")
                    response_text = payload.get("response", "")
                    if not pattern_id or not response_text:
                        _json_response(self, 400, {"error": "pattern_id and response required"}, gate, origin)
                        return
                    if sentinel and hasattr(sentinel, "wraith") and sentinel.wraith:
                        result = sentinel.wraith.test_response(pattern_id, response_text)
                        _json_response(self, 200, result, gate, origin)
                    else:
                        _json_response(self, 503, {"error": "WRAITH unavailable"}, gate, origin)
                except Exception as exc:
                    _json_response(self, 500, {"error": str(exc)}, gate, origin)
                return

            # ─── Policy Engine Evaluate ───
            if path == "/sentinel/policies/evaluate":
                try:
                    content_length = int(self.headers.get("Content-Length", "0"))
                    raw = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                    payload = json.loads(raw)
                    condition = payload.get("condition", "")
                    context_data = payload.get("context", {})
                    if not condition:
                        _json_response(self, 400, {"error": "condition required"}, gate, origin)
                        return
                    if sentinel and hasattr(sentinel, "policy_engine") and sentinel.policy_engine:
                        actions = sentinel.policy_engine.evaluate(condition, context_data)
                        _json_response(self, 200, {"actions_taken": actions, "count": len(actions)}, gate, origin)
                    else:
                        _json_response(self, 503, {"error": "Policy engine unavailable"}, gate, origin)
                except Exception as exc:
                    _json_response(self, 500, {"error": str(exc)}, gate, origin)
                return

            # ─── Governance Check ───
            if path == "/sentinel/governance/check":
                try:
                    content_length = int(self.headers.get("Content-Length", "0"))
                    raw = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                    payload = json.loads(raw)
                    agent_name = payload.get("agent_name", "")
                    tool_name = payload.get("tool_name", "")
                    params = payload.get("params", {})
                    session_token = payload.get("session_token", "")
                    if not agent_name or not tool_name:
                        _json_response(self, 400, {"error": "agent_name and tool_name required"}, gate, origin)
                        return
                    if sentinel and hasattr(sentinel, "governance") and sentinel.governance:
                        decision = sentinel.governance.check_access(agent_name, tool_name, params, session_token)
                        _json_response(self, 200, decision.to_dict(), gate, origin)
                    else:
                        _json_response(self, 503, {"error": "Governance unavailable"}, gate, origin)
                except Exception as exc:
                    _json_response(self, 500, {"error": str(exc)}, gate, origin)
                return

            # ─── PHANTOM Engage ───
            if path == "/sentinel/phantom/engage":
                try:
                    content_length = int(self.headers.get("Content-Length", "0"))
                    raw = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                    payload = json.loads(raw)
                    target_ip = payload.get("ip", "")
                    attack_cat = payload.get("attack_category", "manual")
                    atk_payload = payload.get("payload", "")
                    ua = payload.get("user_agent", "")
                    if not target_ip:
                        _json_response(self, 400, {"error": "ip required"}, gate, origin)
                        return
                    if sentinel and hasattr(sentinel, "phantom") and sentinel.phantom:
                        result = sentinel.phantom.engage(target_ip, attack_cat, atk_payload, ua)
                        _json_response(self, 200, result, gate, origin)
                    else:
                        _json_response(self, 503, {"error": "PHANTOM unavailable"}, gate, origin)
                except Exception as exc:
                    _json_response(self, 500, {"error": str(exc)}, gate, origin)
                return

            # ─── Recon Analyze ───
            if path == "/sentinel/recon/analyze":
                try:
                    content_length = int(self.headers.get("Content-Length", "0"))
                    raw = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                    payload = json.loads(raw)
                    target_ip = payload.get("ip", "")
                    ua = payload.get("user_agent", "")
                    attack_cat = payload.get("attack_category", "")
                    atk_payload = payload.get("payload", "")
                    if not target_ip:
                        _json_response(self, 400, {"error": "ip required"}, gate, origin)
                        return
                    if sentinel and hasattr(sentinel, "recon") and sentinel.recon:
                        result = sentinel.recon.analyze(target_ip, ua, attack_cat, atk_payload)
                        _json_response(self, 200, result, gate, origin)
                    else:
                        _json_response(self, 503, {"error": "Recon unavailable"}, gate, origin)
                except Exception as exc:
                    _json_response(self, 500, {"error": str(exc)}, gate, origin)
                return

            # ─── CHRONICLE Incident ───
            if path == "/sentinel/chronicle/incident":
                try:
                    content_length = int(self.headers.get("Content-Length", "0"))
                    raw = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                    payload = json.loads(raw)
                    severity = payload.get("severity", "P3-LOW")
                    title = payload.get("title", "Manual incident")
                    details = payload.get("details", {})
                    source_ip = payload.get("source_ip", "")
                    attack_type = payload.get("attack_type", "")
                    if sentinel and hasattr(sentinel, "chronicle") and sentinel.chronicle:
                        result = sentinel.chronicle.open_incident(severity, title, details, source_ip, attack_type)
                        _json_response(self, 200, result, gate, origin)
                    else:
                        _json_response(self, 503, {"error": "CHRONICLE unavailable"}, gate, origin)
                except Exception as exc:
                    _json_response(self, 500, {"error": str(exc)}, gate, origin)
                return

            if path != "/mcp/execute":
                _json_response(self, 404, {"success": False, "error": "Endpoint not found"})
                return

            try:
                content_length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
                payload = json.loads(raw)
            except Exception as exc:
                _json_response(self, 400, {"success": False, "error": f"Invalid JSON body: {exc}"})
                return

            tool = payload.get("tool")
            arguments = payload.get("arguments", {})
            if not tool:
                _json_response(self, 400, {"success": False, "error": "Missing required field: tool"})
                return

            # Log every tool call for observability (Codex vs Cursor — we can't tell caller, but we see IF calls happen)
            try:
                log_dir = os.path.dirname(MCP_TOOL_CALL_LOG)
                if log_dir and not os.path.isdir(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                caller_hint = self.headers.get("X-Caller", self.headers.get("User-Agent", "unknown"))[:80]
                entry = {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "tool": tool,
                    "args_keys": list(arguments.keys()) if isinstance(arguments, dict) else [],
                    "caller_hint": caller_hint,
                }
                with open(MCP_TOOL_CALL_LOG, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            except Exception:
                pass  # Don't fail the request if logging fails

            try:
                result = bridge.execute_tool(tool, arguments)
                status = 200 if result.get("success") else 500
                _json_response(self, status, result)
            except Exception as exc:
                _log("Unhandled execute exception:\n" + traceback.format_exc())
                _json_response(self, 500, {"success": False, "error": str(exc)})

    return Handler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AIM-OS MCP HTTP fallback bridge")
    parser.add_argument("--port", type=int, default=5001, help="HTTP port to bind (default: 5001)")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--memory-dir", default="./mcp_memory", help="MCP memory directory")
    return parser.parse_args()


def _load_simple_mcp_server(repo_root: str) -> Any:
    """Load repo-root lucid_mcp_server.py directly to avoid package name shadowing."""
    module_path = os.path.join(repo_root, "lucid_mcp_server.py")
    spec = importlib.util.spec_from_file_location("aimos_lucid_mcp_server_runtime", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load MCP server module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "SimpleMCPServer"):
        raise RuntimeError("SimpleMCPServer class not found in lucid_mcp_server.py")
    return module.SimpleMCPServer


def main() -> int:
    args = parse_args()

    # Keep imports consistent with repository-root execution.
    repo_root = os.getcwd()
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    packages_path = os.path.join(repo_root, "packages")
    if packages_path not in sys.path:
        sys.path.insert(0, packages_path)

    server_cls = _load_simple_mcp_server(repo_root)
    bridge = MCPHTTPBridge(server_cls=server_cls, memory_dir=args.memory_dir)
    handler_cls = build_handler(bridge, args.port)

    # Use SO_REUSEADDR to avoid TIME_WAIT socket exhaustion
    class ReusableHTTPServer(ThreadingHTTPServer):
        allow_reuse_address = True
        allow_reuse_port = True

    server = ReusableHTTPServer((args.host, args.port), handler_cls)
    _log(f"Listening on http://{args.host}:{args.port} (fallback mode, SO_REUSEADDR enabled)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        _log("Shutdown requested")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
