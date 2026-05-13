#!/usr/bin/env python3
"""
AIM-OS Cloudflare Tunnel — Zero-Config Public URL for MCP

Exposes the local MCP SSE server (:8000) via Cloudflare's free tunnel service.
No account needed, no router config, no port forwarding.

Usage:
    python scripts/cloudflare_tunnel.py
    python scripts/cloudflare_tunnel.py --port 8000

The URL is printed to stdout and saved to data/mcp/active_tunnel.json.
Paste it into ChatGPT's MCP App configuration.

Prerequisites:
    cloudflared must be installed. This script will attempt to install it
    via winget if not found.
"""

import argparse
import json
import os
import re
import signal
import subprocess
import shutil
import sys
import time
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS_DIR = os.path.join(REPO_ROOT, "data", "mcp")
STATUS_FILE = os.path.join(STATUS_DIR, "active_tunnel.json")


def _log(msg: str) -> None:
    print(f"[CF-TUNNEL] {msg}", flush=True)


def find_cloudflared() -> str | None:
    """Find cloudflared binary on PATH."""
    return shutil.which("cloudflared")


def install_cloudflared() -> bool:
    """Try to install cloudflared via winget (Windows)."""
    _log("cloudflared not found. Attempting install via winget...")
    try:
        result = subprocess.run(
            ["winget", "install", "--id", "Cloudflare.cloudflared",
             "--accept-package-agreements", "--accept-source-agreements"],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            _log("✓ cloudflared installed successfully!")
            _log("You may need to restart your terminal for PATH to update.")
            return True
        else:
            _log(f"✗ Install failed: {result.stderr[:200]}")
            return False
    except FileNotFoundError:
        _log("✗ winget not found. Please install cloudflared manually:")
        _log("  https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/")
        return False
    except Exception as e:
        _log(f"✗ Install error: {e}")
        return False


def write_status(url: str | None, running: bool, error: str | None = None):
    """Write tunnel status for JOC / connection_manager."""
    os.makedirs(STATUS_DIR, exist_ok=True)
    status = {
        "method": "cloudflare",
        "tunnel_url": url,
        "running": running,
        "error": error,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "chatgpt_sse_url": f"{url}/sse" if url else None,
    }
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)


def extract_tunnel_url(line: str) -> str | None:
    """Extract the trycloudflare.com URL from cloudflared output."""
    # cloudflared prints: "... https://xxx-xxx-xxx.trycloudflare.com ..."
    match = re.search(r'(https://[a-zA-Z0-9\-]+\.trycloudflare\.com)', line)
    if match:
        return match.group(1)
    # Also match custom domain tunnels
    match = re.search(r'(https://[a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,})', line)
    if match and 'cloudflare' not in match.group(1) and 'localhost' not in match.group(1):
        return match.group(1)
    return None


def start_tunnel(port: int):
    """Start cloudflared tunnel and capture the URL."""
    cf_path = find_cloudflared()
    if not cf_path:
        if not install_cloudflared():
            sys.exit(1)
        cf_path = find_cloudflared()
        if not cf_path:
            _log("✗ cloudflared still not found after install. Restart terminal and try again.")
            sys.exit(1)

    _log(f"Starting Cloudflare Tunnel → http://localhost:{port}")
    _log("═══════════════════════════════════════════════════")

    proc = subprocess.Popen(
        [cf_path, "tunnel", "--url", f"http://localhost:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # cloudflared logs to stderr
        text=True,
        bufsize=1,
    )

    tunnel_url = None

    def shutdown(*_):
        _log("Shutting down tunnel...")
        write_status(tunnel_url, running=False, error="shutdown")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Read output, looking for the tunnel URL
    try:
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue

            # Print all cloudflared output
            print(f"  {line}")

            # Try to extract URL
            if not tunnel_url:
                url = extract_tunnel_url(line)
                if url:
                    tunnel_url = url
                    _log("═══════════════════════════════════════════════════")
                    _log(f"  ✓ TUNNEL URL: {tunnel_url}")
                    _log(f"  ✓ ChatGPT MCP URL: {tunnel_url}/sse")
                    _log("═══════════════════════════════════════════════════")
                    _log("Paste the SSE URL above into ChatGPT's MCP App config.")
                    _log("Tunnel is running. Press Ctrl+C to stop.")
                    write_status(tunnel_url, running=True)

        # If we get here, cloudflared exited
        exit_code = proc.wait()
        _log(f"cloudflared exited with code {exit_code}")
        write_status(tunnel_url, running=False, error=f"exited with code {exit_code}")

    except Exception as e:
        _log(f"Error: {e}")
        write_status(tunnel_url, running=False, error=str(e))
        proc.terminate()


def main():
    parser = argparse.ArgumentParser(description="AIM-OS Cloudflare Tunnel")
    parser.add_argument("--port", type=int, default=8000,
                        help="Local port to expose (default: 8000)")
    args = parser.parse_args()

    _log("═══════════════════════════════════════════════════")
    _log("  AIM-OS Cloudflare Tunnel")
    _log(f"  Exposing: http://localhost:{args.port}")
    _log("  Cost: $0 (free Cloudflare tunnel)")
    _log("  Router config: NONE NEEDED")
    _log("═══════════════════════════════════════════════════")

    start_tunnel(args.port)


if __name__ == "__main__":
    main()
