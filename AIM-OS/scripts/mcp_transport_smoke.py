#!/usr/bin/env python3
"""
Smoke test MCP HTTP transport across primary and fallback endpoints.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List


ENDPOINTS_DEFAULT = [
    "http://localhost:5001",
    "http://127.0.0.1:5001",
    "http://localhost:5003",
    "http://127.0.0.1:5003",
]


def get_json(url: str, timeout: int = 8) -> Dict[str, Any]:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def post_json(url: str, payload: Dict[str, Any], timeout: int = 60) -> Dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_json_with_retry(
    url: str,
    total_wait_seconds: int = 180,
    request_timeout_seconds: int = 20,
    retry_interval_seconds: int = 5,
) -> Dict[str, Any]:
    deadline = time.monotonic() + max(total_wait_seconds, request_timeout_seconds)
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        try:
            return get_json(url, timeout=request_timeout_seconds)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(retry_interval_seconds)

    if last_error is None:
        raise TimeoutError(f"Timed out waiting for {url}")
    raise last_error


def run_endpoint_checks(base_url: str, include_message_test: bool, min_tools: int) -> Dict[str, Any]:
    result: Dict[str, Any] = {"base_url": base_url, "ok": False, "checks": {}}

    try:
        health = get_json(f"{base_url}/health", timeout=6)
        result["checks"]["health"] = {"ok": True, "response": health}
    except Exception as exc:
        result["checks"]["health"] = {"ok": False, "error": str(exc)}
        return result

    try:
        # Fallback bridge performs lazy MCP init on first request, which can take
        # >20s on cold start. Retry list until initialization settles.
        lst = get_json_with_retry(
            f"{base_url}/mcp/list",
            total_wait_seconds=240,
            request_timeout_seconds=30,
            retry_interval_seconds=5,
        )
        tool_count = int(lst.get("count") or 0)
        list_ok = bool(lst.get("success")) and tool_count >= min_tools
        result["checks"]["list"] = {
            "ok": list_ok,
            "count": tool_count,
            "min_expected": min_tools,
        }
    except Exception as exc:
        result["checks"]["list"] = {"ok": False, "error": str(exc)}
        return result

    try:
        stats = post_json(
            f"{base_url}/mcp/execute",
            {"tool": "get_memory_stats", "arguments": {}},
            timeout=120,
        )
        result["checks"]["execute_get_memory_stats"] = {
            "ok": bool(stats.get("success")),
            "has_result": "result" in stats,
        }
    except Exception as exc:
        result["checks"]["execute_get_memory_stats"] = {"ok": False, "error": str(exc)}
        return result

    if include_message_test:
        thread_id = f"mcp_transport_smoke_{datetime.now(timezone.utc).strftime('%Y%m%d')}"
        try:
            send = post_json(
                f"{base_url}/mcp/execute",
                {
                    "tool": "send_ai_message",
                    "arguments": {
                        "from_ai": "Codex Agent",
                        "to_ai": "Agent Aether",
                        "content": "MCP transport smoke test message.",
                        "message_type": "status_update",
                        "priority": "low",
                        "thread_id": thread_id,
                    },
                },
                timeout=180,
            )
            send_payload = send.get("result", {})
            result["checks"]["send_ai_message"] = {
                "ok": bool(send.get("success")) and bool(send_payload.get("success", True)),
                "message_id": send_payload.get("message_id"),
                "atom_id": send_payload.get("atom_id"),
            }
        except Exception as exc:
            result["checks"]["send_ai_message"] = {"ok": False, "error": str(exc)}
            return result

    result["ok"] = all(check.get("ok") for check in result["checks"].values())
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MCP transport smoke checks")
    parser.add_argument(
        "--endpoints",
        nargs="*",
        default=ENDPOINTS_DEFAULT,
        help="Base URLs to test (default includes :5001 and :5003)",
    )
    parser.add_argument(
        "--include-message-test",
        action="store_true",
        help="Also send a test AI message through MCP",
    )
    parser.add_argument(
        "--min-tools",
        type=int,
        default=20,
        help="Minimum acceptable tools/list count per endpoint (default: 20)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    report: List[Dict[str, Any]] = []
    any_ok = False

    for endpoint in args.endpoints:
        endpoint_report = run_endpoint_checks(
            endpoint,
            include_message_test=args.include_message_test,
            min_tools=args.min_tools,
        )
        report.append(endpoint_report)
        any_ok = any_ok or endpoint_report.get("ok", False)

    print(json.dumps({"success": any_ok, "endpoints": report}, indent=2, ensure_ascii=False))
    return 0 if any_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
