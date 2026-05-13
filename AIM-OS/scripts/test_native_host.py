#!/usr/bin/env python3
"""
Test for the AIM-OS Gemini Bridge Native Messaging Host.

Simulates Chrome's stdin/stdout protocol by writing length-prefixed JSON
to the host's stdin and reading length-prefixed JSON from its stdout.
"""

import json
import struct
import subprocess
import sys
import os
from pathlib import Path

REPO_ROOT = str(Path(__file__).parent.parent.resolve())
HOST_SCRIPT = os.path.join(REPO_ROOT, "scripts", "aimos_bridge_host.py")


def encode_message(msg: dict) -> bytes:
    """Encode a message in Chrome Native Messaging format."""
    encoded = json.dumps(msg).encode("utf-8")
    return struct.pack("<I", len(encoded)) + encoded


def decode_message(raw: bytes) -> dict:
    """Decode a Chrome Native Messaging response."""
    if len(raw) < 4:
        raise ValueError(f"Response too short: {len(raw)} bytes")
    msg_length = struct.unpack("<I", raw[:4])[0]
    msg_data = raw[4:4 + msg_length]
    return json.loads(msg_data.decode("utf-8"))


def test_tool_call(tool: str, args: dict, request_id: str = "test_1"):
    """Send a single tool call and return the response."""
    payload = {"requestId": request_id, "tool": tool, "args": args}
    input_bytes = encode_message(payload)

    proc = subprocess.Popen(
        [sys.executable, HOST_SCRIPT],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=REPO_ROOT
    )

    # Write the message then close stdin to signal EOF
    proc.stdin.write(input_bytes)
    proc.stdin.close()

    # Read the 4-byte length prefix
    raw_length = proc.stdout.read(4)
    if not raw_length or len(raw_length) < 4:
        stderr = proc.stderr.read()
        if stderr:
            print(f"  STDERR: {stderr.decode('utf-8', errors='replace')[:500]}")
        print(f"  ERROR: No response from host")
        proc.terminate()
        return None

    msg_length = struct.unpack("<I", raw_length)[0]
    raw_msg = proc.stdout.read(msg_length)
    proc.terminate()

    try:
        return json.loads(raw_msg.decode("utf-8"))
    except json.JSONDecodeError as e:
        print(f"  ERROR: JSON decode: {e}")
        return None


def main():
    print("=" * 60)
    print("  AIM-OS Gemini Bridge — Native Host Test")
    print("=" * 60)

    # Test 1: Ping
    print("\n[TEST 1] Ping/Pong")
    ping_payload = encode_message({"type": "ping"})
    proc = subprocess.Popen(
        [sys.executable, HOST_SCRIPT],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=REPO_ROOT
    )
    stdout, _ = proc.communicate(input=ping_payload, timeout=10)
    if stdout:
        resp = decode_message(stdout)
        assert resp.get("type") == "pong", f"Expected pong, got: {resp}"
        print("  ✓ Ping/Pong works")
    else:
        print("  ✗ No response to ping")

    # Test 2: get_memory_stats (simple tool, no args)
    print("\n[TEST 2] get_memory_stats")
    resp = test_tool_call("get_memory_stats", {}, "test_memory_stats")
    if resp:
        print(f"  Response: {json.dumps(resp, indent=2)[:300]}")
        if resp.get("result"):
            print("  ✓ get_memory_stats returned result")
        elif resp.get("error"):
            print(f"  ⚠ Error (may be OK if no memories): {resp['error']}")
    else:
        print("  ✗ No response")

    # Test 3: send_ai_message (comms test)
    print("\n[TEST 3] send_ai_message")
    resp = test_tool_call("send_ai_message", {
        "from_ai": "Gemini Bridge Test",
        "to_ai": "all",
        "content": "[TEST] Native host integration test — if you see this, the bridge works!",
        "message_type": "status_update",
        "priority": "low"
    }, "test_send_msg")
    if resp:
        print(f"  Response: {json.dumps(resp, indent=2)[:300]}")
        result = resp.get("result", {})
        if result.get("success") or result.get("message_id"):
            print("  ✓ Message sent successfully")
        elif resp.get("error"):
            print(f"  ✗ Error: {resp['error']}")
    else:
        print("  ✗ No response")

    # Test 4: Invalid tool
    print("\n[TEST 4] Invalid tool name")
    resp = test_tool_call("nonexistent_tool_12345", {}, "test_invalid")
    if resp:
        if resp.get("error"):
            print(f"  ✓ Correctly returned error: {resp['error'][:100]}")
        else:
            print(f"  ⚠ Expected error, got: {resp}")
    else:
        print("  ✗ No response")

    print("\n" + "=" * 60)
    print("  Tests Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
