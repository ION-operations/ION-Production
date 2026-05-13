#!/usr/bin/env python3
"""
AIM-OS Gemini Bridge — Chrome Native Messaging Host

Receives MCP tool call payloads from the Chrome extension via stdin (length-prefixed JSON),
delegates to SimpleMCPServer from lucid_mcp_server.py, and returns results via stdout.

Chrome Native Messaging Protocol:
  - Input:  4 bytes (uint32 little-endian length) + JSON message
  - Output: 4 bytes (uint32 little-endian length) + JSON message
"""

import sys
import os
import json
import struct
import logging
from pathlib import Path

# ── Setup paths ──────────────────────────────────────────────────────

REPO_ROOT = str(Path(__file__).parent.parent.resolve())
sys.path.insert(0, REPO_ROOT)

MEMORY_DIR = os.path.join(REPO_ROOT, "data", "memory")
os.makedirs(MEMORY_DIR, exist_ok=True)

LOG_FILE = os.path.join(REPO_ROOT, "data", "mcp", "gemini_bridge.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("aimos-bridge-host")

# ── Windows binary stdin/stdout mode ─────────────────────────────────

if sys.platform == "win32":
    import msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)


# ── SimpleMCPServer delegate ────────────────────────────────────────

_delegate = None
_request_id = 0


def get_delegate():
    """Lazy-load the SimpleMCPServer from lucid_mcp_server.py."""
    global _delegate
    if _delegate is not None:
        return _delegate

    try:
        import importlib.util
        server_path = os.path.join(REPO_ROOT, "lucid_mcp_server.py")
        spec = importlib.util.spec_from_file_location("lucid_mcp_server", server_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _delegate = mod.SimpleMCPServer(memory_directory=MEMORY_DIR)
        logger.info("SimpleMCPServer loaded successfully")
        return _delegate
    except Exception as e:
        logger.error(f"Failed to load SimpleMCPServer: {e}")
        return None


def call_tool(tool_name: str, arguments: dict) -> dict:
    """Call a tool on the delegate SimpleMCPServer."""
    global _request_id

    delegate = get_delegate()
    if delegate is None:
        return {"error": "SimpleMCPServer not available"}

    _request_id += 1
    request = {
        "jsonrpc": "2.0",
        "id": _request_id,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        }
    }

    try:
        response = delegate.handle_request(request)
        if "result" in response:
            content = response["result"].get("content", [])
            if content and len(content) > 0:
                text = content[0].get("text", "")
                try:
                    return json.loads(text)
                except (json.JSONDecodeError, TypeError):
                    return {"text": text}
        if "error" in response:
            return {"error": response["error"].get("message", "Unknown error")}
        return response
    except Exception as e:
        logger.error(f"Tool call failed for {tool_name}: {e}")
        return {"error": str(e)}


# ── Chrome Native Messaging Protocol ────────────────────────────────

def read_message():
    """Read a length-prefixed JSON message from stdin."""
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) == 0:
        return None  # EOF — Chrome disconnected
    if len(raw_length) < 4:
        logger.warning(f"Short read for length: {len(raw_length)} bytes")
        return None

    msg_length = struct.unpack("<I", raw_length)[0]

    if msg_length > 1024 * 1024:  # 1MB safety limit
        logger.error(f"Message too large: {msg_length} bytes")
        return None

    raw_msg = sys.stdin.buffer.read(msg_length)
    if len(raw_msg) < msg_length:
        logger.warning(f"Short read for message: {len(raw_msg)}/{msg_length} bytes")
        return None

    try:
        return json.loads(raw_msg.decode("utf-8"))
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return None


def send_message(message: dict):
    """Write a length-prefixed JSON message to stdout."""
    encoded = json.dumps(message, ensure_ascii=False).encode("utf-8")
    length = struct.pack("<I", len(encoded))
    sys.stdout.buffer.write(length)
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()


# ── Main Loop ────────────────────────────────────────────────────────

def main():
    logger.info("AIM-OS Gemini Bridge Host started")

    while True:
        message = read_message()
        if message is None:
            logger.info("No more messages (EOF). Exiting.")
            break

        logger.info(f"Received: {json.dumps(message)[:500]}")

        # Handle ping/keepalive
        if message.get("type") == "ping":
            send_message({"type": "pong"})
            continue

        request_id = message.get("requestId", "unknown")
        tool = message.get("tool")
        args = message.get("args", {})

        if not tool:
            send_message({
                "requestId": request_id,
                "error": "Missing 'tool' field in request"
            })
            continue

        try:
            result = call_tool(tool, args)
            response = {
                "requestId": request_id,
                "result": result
            }
            if "error" in result:
                response["error"] = result["error"]
                del response["result"]
        except Exception as e:
            logger.error(f"Unhandled error for {tool}: {e}")
            response = {
                "requestId": request_id,
                "error": str(e)
            }

        logger.info(f"Sending response for {request_id}: {json.dumps(response)[:500]}")
        send_message(response)

    logger.info("AIM-OS Gemini Bridge Host shutting down")


if __name__ == "__main__":
    main()
