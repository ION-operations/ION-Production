#!/usr/bin/env python3
"""
AIM-OS Relay Bridge — Local WebSocket Client

Connects to the AIM-OS Relay server (deployed on Render/Railway/Lovable)
via WebSocket and proxies MCP requests to the local SSE server on :8000.

Usage:
    python scripts/aimos_relay/relay_bridge.py --relay-url wss://your-relay.onrender.com

The bridge:
  1. Opens a persistent WebSocket to the relay's /ws/bridge endpoint
  2. Receives MCP requests forwarded from ChatGPT
  3. Proxies them to localhost:8000 (local SSE MCP server)
  4. Returns responses through the WebSocket
  5. Auto-reconnects on disconnect with exponential backoff
"""

import argparse
import asyncio
import json
import logging
import signal
import sys
from datetime import datetime, timezone

try:
    import websockets
except ImportError:
    print("[BRIDGE] Error: 'websockets' not installed. Run: pip install websockets")
    sys.exit(1)

try:
    import aiohttp
except ImportError:
    print("[BRIDGE] Error: 'aiohttp' not installed. Run: pip install aiohttp")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [BRIDGE] %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger("relay-bridge")

# ─── Config ───
DEFAULT_RELAY = "ws://localhost:3001"
DEFAULT_SECRET = "aimos-relay-secret-2026"
LOCAL_MCP_URL = "http://127.0.0.1:8000"
HEARTBEAT_INTERVAL = 30
MAX_RECONNECT_DELAY = 60
STATUS_FILE = None  # Set by CLI arg


async def proxy_to_local(session: aiohttp.ClientSession, msg: dict) -> dict:
    """Forward an MCP request from the relay to the local SSE server."""
    request_id = msg.get("requestId", "?")
    body = msg.get("body", {})
    content_type = msg.get("contentType", "application/json")

    try:
        # Forward to local /messages endpoint (where FastMCP listens)
        async with session.post(
            f"{LOCAL_MCP_URL}/messages",
            json=body if isinstance(body, dict) else None,
            data=body if isinstance(body, str) else None,
            headers={"Content-Type": content_type},
            timeout=aiohttp.ClientTimeout(total=120),
        ) as resp:
            resp_body = await resp.text()
            return {
                "type": "mcp_response",
                "requestId": request_id,
                "status": resp.status,
                "body": resp_body,
                "contentType": resp.headers.get("Content-Type", "application/json"),
            }
    except aiohttp.ClientError as e:
        log.error(f"Local proxy failed for {request_id}: {e}")
        return {
            "type": "mcp_response",
            "requestId": request_id,
            "status": 502,
            "body": json.dumps({"error": f"Local MCP server unreachable: {e}"}),
            "contentType": "application/json",
        }


def write_status(relay_url: str, connected: bool, error: str | None = None):
    """Write bridge status to JSON file for JOC/connection_manager to read."""
    if not STATUS_FILE:
        return
    import os
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    status = {
        "method": "relay",
        "relay_url": relay_url,
        "connected": connected,
        "error": error,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)


async def bridge_loop(relay_url: str, secret: str):
    """Main bridge loop with auto-reconnect."""
    ws_url = f"{relay_url}/ws/bridge?secret={secret}"
    reconnect_delay = 1

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                log.info(f"Connecting to relay: {relay_url}")
                async with websockets.connect(ws_url, ping_interval=HEARTBEAT_INTERVAL) as ws:
                    log.info("✓ Connected to relay!")
                    reconnect_delay = 1  # Reset backoff
                    write_status(relay_url, connected=True)

                    # Send status message
                    await ws.send(json.dumps({
                        "type": "bridge_status",
                        "message": "AIM-OS local bridge connected",
                        "local_mcp": LOCAL_MCP_URL,
                    }))

                    async for raw in ws:
                        try:
                            msg = json.loads(raw)
                        except json.JSONDecodeError:
                            log.warning(f"Bad JSON from relay: {raw[:100]}")
                            continue

                        msg_type = msg.get("type")

                        if msg_type == "mcp_request":
                            log.info(f"← MCP request {msg.get('requestId', '?')[:8]}")
                            response = await proxy_to_local(session, msg)
                            await ws.send(json.dumps(response))
                            log.info(f"→ Response sent ({response.get('status')})")

                        elif msg_type == "session_open":
                            log.info(f"Session opened: {msg.get('sessionId', '?')[:8]}")

                        elif msg_type == "session_close":
                            log.info(f"Session closed: {msg.get('sessionId', '?')[:8]}")

                        else:
                            log.debug(f"Unknown message type: {msg_type}")

            except (websockets.ConnectionClosed, ConnectionRefusedError, OSError) as e:
                log.warning(f"Connection lost: {e}. Reconnecting in {reconnect_delay}s...")
                write_status(relay_url, connected=False, error=str(e))
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, MAX_RECONNECT_DELAY)

            except Exception as e:
                log.error(f"Unexpected error: {e}. Reconnecting in {reconnect_delay}s...")
                write_status(relay_url, connected=False, error=str(e))
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, MAX_RECONNECT_DELAY)


def main():
    global STATUS_FILE, LOCAL_MCP_URL

    parser = argparse.ArgumentParser(description="AIM-OS Relay Bridge")
    parser.add_argument("--relay-url", default=DEFAULT_RELAY,
                        help=f"Relay server URL (default: {DEFAULT_RELAY})")
    parser.add_argument("--secret", default=DEFAULT_SECRET,
                        help="Bridge authentication secret")
    parser.add_argument("--local-port", type=int, default=8000,
                        help="Local MCP SSE server port (default: 8000)")
    parser.add_argument("--status-file", default=None,
                        help="Path to write status JSON")
    args = parser.parse_args()

    LOCAL_MCP_URL = f"http://127.0.0.1:{args.local_port}"
    STATUS_FILE = args.status_file

    log.info("═══════════════════════════════════════════════════")
    log.info("  AIM-OS Relay Bridge")
    log.info(f"  Relay: {args.relay_url}")
    log.info(f"  Local MCP: {LOCAL_MCP_URL}")
    log.info("═══════════════════════════════════════════════════")

    loop = asyncio.new_event_loop()

    def shutdown():
        log.info("Shutting down bridge...")
        write_status(args.relay_url, connected=False, error="shutdown")
        for task in asyncio.all_tasks(loop):
            task.cancel()

    signal.signal(signal.SIGINT, lambda *_: shutdown())

    try:
        loop.run_until_complete(bridge_loop(args.relay_url, args.secret))
    except asyncio.CancelledError:
        pass
    finally:
        loop.close()
        log.info("Bridge stopped.")


if __name__ == "__main__":
    main()
