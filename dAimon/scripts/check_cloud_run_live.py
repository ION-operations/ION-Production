#!/usr/bin/env python3
"""Check deployed Cloud Run dAimon kernel health and live MongoDB evidence."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from env_loader import load_local_env

OUT = ROOT / "sample_outputs" / "cloud_run_live_health.json"
DEFAULT_SESSION = "daimon_live_vertical_slice_20260509"


def write_json(payload: dict[str, Any]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload.setdefault("schema", "daimon.cloud_run_live_health.v0_1")
    payload.setdefault("accepted_state_changed", False)
    payload.setdefault("external_mutation_attempted", False)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_url(
    url: str,
    *,
    payload: dict[str, Any] | None = None,
    bearer_token: str | None = None,
) -> tuple[int, dict[str, Any]]:
    data = None
    headers = {"accept": "application/json"}
    if bearer_token:
        headers["authorization"] = f"Bearer {bearer_token}"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["content-type"] = "application/json"
    req = Request(url, data=data, headers=headers, method="POST" if payload is not None else "GET")
    try:
        with urlopen(req, timeout=20) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed: dict[str, Any] = json.loads(body)
        except Exception:
            parsed = {"body": body}
        return exc.code, parsed
    except URLError as exc:
        return 0, {"error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=None)
    parser.add_argument("--session-id", default=DEFAULT_SESSION)
    parser.add_argument("--bearer-token", default=None)
    parser.add_argument("--use-gcloud-identity-token", action="store_true")
    args = parser.parse_args()

    load_local_env(ROOT / ".env")
    base_url = (args.url or os.getenv("ION_CLOUD_RUN_URL") or "").rstrip("/")
    if not base_url:
        write_json({
            "ok": False,
            "stage": "preflight",
            "blockers": ["ION_CLOUD_RUN_URL is missing and --url was not provided."],
            "session_id": args.session_id,
        })
        print(json.dumps(json.loads(OUT.read_text(encoding="utf-8")), indent=2))
        return 2

    bearer_token = args.bearer_token
    auth_mode = "bearer_token" if bearer_token else "public"
    if args.use_gcloud_identity_token and not bearer_token:
        try:
            token = subprocess.check_output(
                ["gcloud", "auth", "print-identity-token"],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            bearer_token = token or None
            auth_mode = "gcloud_identity_token" if bearer_token else "public"
        except Exception:
            local_gcloud = Path.home() / "google-cloud-sdk" / "bin" / "gcloud"
            try:
                token = subprocess.check_output(
                    [str(local_gcloud), "auth", "print-identity-token"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                ).strip()
                bearer_token = token or None
                auth_mode = "gcloud_identity_token" if bearer_token else "public"
            except Exception:
                bearer_token = None
                auth_mode = "gcloud_identity_token_unavailable"

    health_status, health = read_url(f"{base_url}/health", bearer_token=bearer_token)
    evidence_status, evidence = read_url(
        f"{base_url}/live-vertical-slice-evidence/{quote(args.session_id)}",
        bearer_token=bearer_token,
    )
    query_status, query = read_url(
        f"{base_url}/query-governed-state-live",
        bearer_token=bearer_token,
        payload={
            "session_id": args.session_id,
            "query": "Find receipt-cleared dAimon continuity for the next Gemini session.",
            "limit": 5,
            "include_exclusion_report": True,
        },
    )

    ok = (
        health_status == 200
        and evidence_status == 200
        and health.get("ok") is True
        and evidence.get("ok") is True
        and int(evidence.get("inheritable_count", 0)) > 0
        and query_status == 200
        and len(query.get("matches", [])) > 0
    )
    write_json({
        "ok": ok,
        "cloud_run_url": base_url,
        "auth_mode": auth_mode,
        "session_id": args.session_id,
        "health_status": health_status,
        "evidence_status": evidence_status,
        "post_endpoint_probe_status": query_status,
        "health": health,
        "evidence": evidence,
        "post_endpoint_probe": query,
        "blockers": [] if ok else ["Cloud Run health/evidence endpoints did not return live seeded receipt-cleared objects."],
    })
    print(json.dumps(json.loads(OUT.read_text(encoding="utf-8")), indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
