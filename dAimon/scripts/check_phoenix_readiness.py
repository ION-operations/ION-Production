#!/usr/bin/env python3
"""Emit a tiny dAimon readiness trace to Arize Phoenix.

The script is intentionally proof-oriented:
- loads ignored local `.env`;
- never prints or writes API keys;
- tries the configured Phoenix endpoint first;
- retries the explicit OTLP `/v1/traces` endpoint when the first attempt looks
  like an export failure.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from env_loader import load_local_env

OUT = ROOT / "sample_outputs" / "phoenix_readiness.json"
DEFAULT_BASE_ENDPOINT = "https://app.phoenix.arize.com/s/crinkedart"
DEFAULT_TRACE_ENDPOINT = "https://app.phoenix.arize.com/s/crinkedart/v1/traces"
FAILURE_NEEDLES = [
    "failed",
    "failure",
    "exception",
    "unauthorized",
    "forbidden",
    "not found",
    "404",
    "401",
    "403",
]


def write_json(payload: dict[str, Any]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload.setdefault("schema", "daimon.phoenix_readiness.v0_1")
    payload.setdefault("accepted_state_changed", False)
    payload.setdefault("external_mutation_attempted", True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def redact_log(text: str) -> str:
    api_key = os.getenv("PHOENIX_API_KEY", "")
    if api_key:
        text = text.replace(api_key, "[REDACTED_PHOENIX_API_KEY]")
    arize_key = os.getenv("ARIZE_API_KEY", "")
    if arize_key:
        text = text.replace(arize_key, "[REDACTED_ARIZE_API_KEY]")
    return text.encode("ascii", "replace").decode("ascii")[-4000:]


def endpoint_candidates(primary: str, fallback: str) -> list[str]:
    candidates = [primary]
    if fallback not in candidates:
        candidates.append(fallback)
    return candidates


def try_export(endpoint: str, project_name: str) -> dict[str, Any]:
    capture = io.StringIO()
    try:
        from opentelemetry import trace as trace_api  # type: ignore
        from phoenix.otel import register  # type: ignore
    except Exception as exc:
        return {
            "endpoint": endpoint,
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "install_hint": "python -m pip install arize-phoenix-otel",
        }

    try:
        with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
            provider = register(
                endpoint=endpoint,
                project_name=project_name,
                protocol="http/protobuf",
                batch=False,
                auto_instrument=False,
            )
            tracer = trace_api.get_tracer("daimon.phoenix.readiness")
            with tracer.start_as_current_span("daimon.phoenix_readiness") as span:
                span.set_attribute("daimon.project", "dAimon")
                span.set_attribute("daimon.trace_kind", "readiness")
                span.set_attribute("daimon.accepted_state_changed", False)
                span.set_attribute("daimon.external_mutation_attempted", True)
            if hasattr(provider, "force_flush"):
                provider.force_flush(timeout_millis=10000)
            if hasattr(provider, "shutdown"):
                provider.shutdown()
    except Exception as exc:
        return {
            "endpoint": endpoint,
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "export_log_tail": redact_log(capture.getvalue()),
        }

    log_tail = redact_log(capture.getvalue())
    lower = log_tail.lower()
    looks_failed = any(needle in lower for needle in FAILURE_NEEDLES)
    return {
        "endpoint": endpoint,
        "ok": not looks_failed,
        "error": "export log indicates failure" if looks_failed else None,
        "export_log_tail": log_tail,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default=None)
    parser.add_argument("--fallback-endpoint", default=DEFAULT_TRACE_ENDPOINT)
    parser.add_argument("--project-name", default=None)
    args = parser.parse_args()

    loaded = load_local_env(ROOT / ".env")
    endpoint = args.endpoint or os.getenv("PHOENIX_COLLECTOR_ENDPOINT") or DEFAULT_BASE_ENDPOINT
    project_name = args.project_name or os.getenv("PHOENIX_PROJECT_NAME") or "daimon"
    api_key_present = bool(os.getenv("PHOENIX_API_KEY"))

    if not os.getenv("PHOENIX_CLIENT_HEADERS") and os.getenv("PHOENIX_API_KEY"):
        os.environ["PHOENIX_CLIENT_HEADERS"] = f"api_key={os.getenv('PHOENIX_API_KEY')}"

    if not api_key_present:
        result = {
            "ok": False,
            "stage": "preflight",
            "blockers": ["PHOENIX_API_KEY is missing from local .env or environment."],
            "endpoint": endpoint,
            "fallback_endpoint": args.fallback_endpoint,
            "project_name": project_name,
            "env_file_loaded": bool(loaded),
            "api_key_present": False,
        }
        write_json(result)
        print(json.dumps(result, indent=2))
        return 2

    attempts = []
    success = None
    for candidate in endpoint_candidates(endpoint, args.fallback_endpoint):
        attempt = try_export(candidate, project_name)
        attempts.append(attempt)
        if attempt.get("ok"):
            success = attempt
            if os.getenv("PHOENIX_COLLECTOR_ENDPOINT") != candidate:
                os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = candidate
            break

    result = {
        "ok": success is not None,
        "stage": "trace_export_attempted",
        "project_name": project_name,
        "configured_endpoint": endpoint,
        "successful_endpoint": success.get("endpoint") if success else None,
        "fallback_endpoint": args.fallback_endpoint,
        "api_key_present": True,
        "attempts": attempts,
        "blockers": [] if success else ["Phoenix trace export did not succeed with configured or fallback endpoint."],
    }
    write_json(result)
    print(json.dumps(result, indent=2))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
