#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
AIM-OS MCP Bridge — Local Tunnel Client
═══════════════════════════════════════════════════════════════════

Connects to the cloud-hosted AIM-OS MCP Relay via WebSocket and
proxies all MCP traffic to the local SSE server (localhost:8000).

This is the "local half" of our self-hosted ngrok replacement.

Usage:
    python scripts/mcp_bridge.py --relay-url wss://your-relay.lovable.app/ws/bridge

Architecture:
    ChatGPT ──HTTP/SSE──► Relay (cloud) ◄──WebSocket──► THIS SCRIPT ──► localhost:8000
"""

import asyncio
import json
import sys
import argparse
import signal
import time
from urllib.parse import urlencode

try:
    import websockets
except ImportError:
    print("websockets not installed. Run: pip install websockets aiohttp")
    sys.exit(1)

try:
    import aiohttp
except ImportError:
    print("aiohttp not installed. Run: pip install aiohttp")
    sys.exit(1)

# ─── Config ───
DEFAULT_RELAY = "ws://localhost:3001/ws/bridge"
DEFAULT_SECRET = "aimos-relay-secret-2026"
LOCAL_SSE_SERVER = "http://localhost:8000"

# ─── Bridge Client ───

class MCPBridge:
    def __init__(self, relay_url: str, secret: str, local_server: str):
        self.relay_url = f"{relay_url}?secret={secret}"
        self.local_server = local_server.rstrip('/')
        self.ws = None
        self.session = None
        self.running = True
        self.reconnect_delay = 1
        self.max_reconnect_delay = 30

    async def start(self):
        """Main loop — connect to relay with auto-reconnect."""
        print("═" * 58)
        print("  AIM-OS MCP Bridge")
        print(f"  Relay:  {self.relay_url.split('?')[0]}")
        print(f"  Local:  {self.local_server}")
        print("═" * 58)

        self.session = aiohttp.ClientSession()

        while self.running:
            try:
                await self.connect()
            except Exception as e:
                if not self.running:
                    break
                print(f"[Bridge] Connection error: {e}")
                print(f"[Bridge] Reconnecting in {self.reconnect_delay}s...")
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay = min(
                    self.reconnect_delay * 2,
                    self.max_reconnect_delay
                )

        if self.session:
            await self.session.close()
        print("[Bridge] Shutdown complete.")

    async def connect(self):
        """Single connection attempt."""
        print("[Bridge] Connecting to relay...")

        async with websockets.connect(
            self.relay_url,
            ping_interval=20,
            ping_timeout=10,
            close_timeout=5,
        ) as ws:
            self.ws = ws
            self.reconnect_delay = 1  # Reset on successful connect
            print("[Bridge] ✓ Connected to relay!")

            # Announce ourselves
            await self.send({
                "type": "bridge_status",
                "message": f"Bridge online — proxying to {self.local_server}",
            })

            # Listen for messages
            async for raw in ws:
                try:
                    msg = json.loads(raw)
                    await self.handle_message(msg)
                except json.JSONDecodeError:
                    print(f"[Bridge] Bad JSON: {raw[:100]}")
                except Exception as e:
                    print(f"[Bridge] Handler error: {e}")

    async def handle_message(self, msg: dict):
        """Handle a message from the relay."""
        msg_type = msg.get("type")

        if msg_type == "mcp_request":
            # Forward request to local SSE server
            asyncio.create_task(self.proxy_request(msg))

        elif msg_type == "session_open":
            sid = msg.get("sessionId", "?")
            print(f"[Bridge] ChatGPT session opened: {sid[:8]}...")

        elif msg_type == "session_close":
            sid = msg.get("sessionId", "?")
            print(f"[Bridge] ChatGPT session closed: {sid[:8]}...")

        else:
            print(f"[Bridge] Unknown message: {msg_type}")

    async def proxy_request(self, msg: dict):
        """Proxy a single MCP request to the local server."""
        request_id = msg["requestId"]
        session_id = msg["sessionId"]
        body = msg.get("body")
        content_type = msg.get("contentType", "application/json")

        # Build URL for local SSE server
        url = f"{self.local_server}/messages?session_id={session_id}"

        try:
            headers = {"Content-Type": content_type} if content_type else {}

            # Send to local server
            async with self.session.post(
                url,
                json=body if isinstance(body, dict) else None,
                data=body if isinstance(body, str) else None,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=110),
            ) as resp:
                resp_body = await resp.text()

                # Send response back to relay
                await self.send({
                    "type": "mcp_response",
                    "requestId": request_id,
                    "status": resp.status,
                    "contentType": resp.headers.get("Content-Type", "application/json"),
                    "body": resp_body,
                })

        except aiohttp.ClientError as e:
            print(f"[Bridge] Local server error: {e}")
            await self.send({
                "type": "mcp_response",
                "requestId": request_id,
                "status": 502,
                "body": json.dumps({
                    "error": f"Local SSE server unreachable: {str(e)}"
                }),
            })

    async def send(self, msg: dict):
        """Send a message to the relay."""
        if self.ws and self.ws.open:
            await self.ws.send(json.dumps(msg))

    def stop(self):
        """Graceful shutdown."""
        print("\n[Bridge] Shutting down...")
        self.running = False
        if self.ws:
            asyncio.get_event_loop().create_task(self.ws.close())


# ─── CLI ───

def main():
    parser = argparse.ArgumentParser(
        description="AIM-OS MCP Bridge — tunnel local MCP to cloud relay"
    )
    parser.add_argument(
        "--relay-url",
        default=DEFAULT_RELAY,
        help=f"Relay WebSocket URL (default: {DEFAULT_RELAY})"
    )
    parser.add_argument(
        "--secret",
        default=DEFAULT_SECRET,
        help="Bridge authentication secret"
    )
    parser.add_argument(
        "--local",
        default=LOCAL_SSE_SERVER,
        help=f"Local SSE server URL (default: {LOCAL_SSE_SERVER})"
    )
    args = parser.parse_args()

    # Convert https to wss if needed
    relay = args.relay_url
    if relay.startswith("https://"):
        relay = "wss://" + relay[8:]
    elif relay.startswith("http://"):
        relay = "ws://" + relay[7:]
    if not relay.endswith("/ws/bridge"):
        relay = relay.rstrip("/") + "/ws/bridge"

    bridge = MCPBridge(relay, args.secret, args.local)

    # Graceful shutdown
    loop = asyncio.new_event_loop()

    def shutdown_handler():
        bridge.stop()

    try:
        if sys.platform != "win32":
            loop.add_signal_handler(signal.SIGINT, shutdown_handler)
            loop.add_signal_handler(signal.SIGTERM, shutdown_handler)
    except NotImplementedError:
        pass  # Windows — Ctrl+C works via KeyboardInterrupt

    try:
        loop.run_until_complete(bridge.start())
    except KeyboardInterrupt:
        bridge.stop()
        loop.run_until_complete(asyncio.sleep(0.5))
    finally:
        loop.close()


if __name__ == "__main__":
    main()
