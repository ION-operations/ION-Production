#!/usr/bin/env python3
"""
AIM-OS Connection Manager — Unified MCP Tunnel Controller

Starts the SSE MCP server and one or more tunnel methods to expose it
to ChatGPT and other remote agents.

Usage:
    python scripts/connection_manager.py --method all
    python scripts/connection_manager.py --method cloudflare
    python scripts/connection_manager.py --method relay --relay-url wss://your-relay.onrender.com
    python scripts/connection_manager.py --method direct  (SSE only, you handle port forwarding)

Methods:
    cloudflare  — Cloudflare Tunnel (free, no router config)
    relay       — AIM-OS Relay via WebSocket bridge (needs deployed relay)
    direct      — No tunnel, just local SSE server (you port-forward or use LAN)
    all         — Start SSE + all available tunnels

Status is written to data/mcp/connections.json for JOC to poll.
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS_DIR = os.path.join(REPO_ROOT, "data", "mcp")
STATUS_FILE = os.path.join(STATUS_DIR, "connections.json")
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")


def _log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [CONN-MGR] {msg}", flush=True)


def write_status(connections: dict):
    """Write combined connection status for JOC."""
    os.makedirs(STATUS_DIR, exist_ok=True)
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "connections": connections,
    }
    with open(STATUS_FILE, "w") as f:
        json.dump(payload, f, indent=2)


class ProcessManager:
    """Manages child processes for SSE server and tunnels."""

    def __init__(self):
        self.children: dict[str, subprocess.Popen] = {}
        self._shutting_down = False

    def start(self, name: str, cmd: list[str], cwd: str = REPO_ROOT) -> subprocess.Popen:
        _log(f"Starting {name}: {' '.join(cmd[:4])}...")
        proc = subprocess.Popen(
            cmd, cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        self.children[name] = proc
        _log(f"  ✓ {name} started (PID {proc.pid})")
        return proc

    def shutdown_all(self):
        if self._shutting_down:
            return
        self._shutting_down = True
        _log("Shutting down all processes...")
        for name, proc in self.children.items():
            if proc.poll() is None:
                _log(f"  Terminating {name} (PID {proc.pid})")
                proc.terminate()
        # Give them 5s to exit gracefully
        time.sleep(2)
        for name, proc in self.children.items():
            if proc.poll() is None:
                _log(f"  Force-killing {name}")
                proc.kill()
        _log("All processes stopped.")

    def any_alive(self) -> bool:
        return any(p.poll() is None for p in self.children.values())


def start_sse_server(mgr: ProcessManager, port: int):
    """Start the FastMCP SSE server."""
    return mgr.start("sse_server", [
        sys.executable, os.path.join(SCRIPTS_DIR, "mcp_sse_server.py"),
    ])


def start_cloudflare(mgr: ProcessManager, port: int):
    """Start Cloudflare Tunnel."""
    return mgr.start("cloudflare_tunnel", [
        sys.executable, os.path.join(SCRIPTS_DIR, "cloudflare_tunnel.py"),
        "--port", str(port),
    ])


def start_relay_bridge(mgr: ProcessManager, relay_url: str, port: int, secret: str):
    """Start the relay WebSocket bridge."""
    status_path = os.path.join(STATUS_DIR, "relay_status.json")
    return mgr.start("relay_bridge", [
        sys.executable, os.path.join(SCRIPTS_DIR, "aimos_relay", "relay_bridge.py"),
        "--relay-url", relay_url,
        "--local-port", str(port),
        "--secret", secret,
        "--status-file", status_path,
    ])


def collect_status(mgr: ProcessManager) -> dict:
    """Collect status from all children."""
    status = {}
    for name, proc in mgr.children.items():
        status[name] = {
            "pid": proc.pid,
            "running": proc.poll() is None,
            "exit_code": proc.poll(),
        }

    # Read tunnel URL if available
    tunnel_file = os.path.join(STATUS_DIR, "active_tunnel.json")
    if os.path.exists(tunnel_file):
        try:
            with open(tunnel_file) as f:
                tunnel_data = json.load(f)
            status["cloudflare_url"] = tunnel_data.get("tunnel_url")
            status["chatgpt_sse_url"] = tunnel_data.get("chatgpt_sse_url")
        except Exception:
            pass

    # Read relay status if available
    relay_file = os.path.join(STATUS_DIR, "relay_status.json")
    if os.path.exists(relay_file):
        try:
            with open(relay_file) as f:
                relay_data = json.load(f)
            status["relay_connected"] = relay_data.get("connected")
            status["relay_url"] = relay_data.get("relay_url")
        except Exception:
            pass

    return status


def main():
    parser = argparse.ArgumentParser(description="AIM-OS Connection Manager")
    parser.add_argument("--method", default="all",
                        choices=["cloudflare", "relay", "direct", "all"],
                        help="Connection method(s) to use")
    parser.add_argument("--port", type=int, default=8000,
                        help="Local SSE MCP server port (default: 8000)")
    parser.add_argument("--relay-url", default="ws://localhost:3001",
                        help="Relay server WebSocket URL")
    parser.add_argument("--relay-secret", default="aimos-relay-secret-2026",
                        help="Relay bridge secret")
    args = parser.parse_args()

    _log("═══════════════════════════════════════════════════")
    _log("  AIM-OS Connection Manager")
    _log(f"  Method: {args.method}")
    _log(f"  SSE Port: {args.port}")
    _log("═══════════════════════════════════════════════════")

    mgr = ProcessManager()

    def shutdown(*_):
        mgr.shutdown_all()
        write_status(collect_status(mgr))
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Always start SSE server
    start_sse_server(mgr, args.port)
    time.sleep(2)  # Let it initialize

    # Start tunnel(s) based on method
    if args.method in ("cloudflare", "all"):
        start_cloudflare(mgr, args.port)

    if args.method in ("relay", "all"):
        start_relay_bridge(mgr, args.relay_url, args.port, args.relay_secret)

    if args.method == "direct":
        _log(f"Direct mode — SSE server running on :{args.port}")
        _log("You handle port forwarding / LAN access.")

    _log("")
    _log("Connection Manager running. Press Ctrl+C to stop all.")
    _log("")

    # Monitor loop — keep running, log child outputs, update status
    try:
        while mgr.any_alive():
            # Print child output
            for name, proc in mgr.children.items():
                if proc.stdout and proc.poll() is None:
                    # Non-blocking read
                    import select
                    try:
                        # Windows doesn't support select on pipes, use polling
                        line = proc.stdout.readline()
                        if line:
                            print(f"  [{name}] {line.rstrip()}")
                    except Exception:
                        pass

            # Update status file periodically
            write_status(collect_status(mgr))
            time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        mgr.shutdown_all()
        write_status(collect_status(mgr))


if __name__ == "__main__":
    main()
