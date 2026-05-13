#!/usr/bin/env python3
"""Check live MongoDB readiness without printing secrets.

Reads `.env` if present, then environment variables. Default mode is read-only:
it pings Atlas and reports sanitized connection metadata. Use `--ensure-indexes`
only when schema/index creation is explicitly intended.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from env_loader import load_local_env
from ion_kernel.mongodb_adapter import MongoAdapterConfig, MongoAtlasAdapter, MongoPersistenceDisabled


def redact_uri(uri: str | None) -> dict:
    if not uri:
        return {"provided": False}
    parsed = urlsplit(uri)
    return {
        "provided": True,
        "scheme": parsed.scheme,
        "host": parsed.hostname,
        "database_in_uri": parsed.path.lstrip("/") or None,
        "username_supplied": bool(parsed.username),
        "password_supplied": bool(parsed.password),
        "query_supplied": bool(parsed.query),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ensure-indexes", action="store_true", help="Create expected MongoDB indexes.")
    args = parser.parse_args()

    loaded_keys = load_local_env(ROOT / ".env")
    cfg = MongoAdapterConfig.from_env()
    result = {
        "schema": "daimon.mongodb_live_readiness.v0_1",
        "env_file_loaded_keys": sorted(k for k in loaded_keys if k != "MONGODB_URI"),
        "mongodb_enabled": cfg.enabled,
        "mongodb_database": cfg.database,
        "collection_prefix_set": bool(cfg.collection_prefix),
        "vector_index_name": cfg.vector_index_name,
        "uri": redact_uri(cfg.uri),
        "ensure_indexes_requested": args.ensure_indexes,
        "accepted_state_changed": False,
        "external_mutation_attempted": bool(args.ensure_indexes),
        "ok": False,
        "errors": [],
    }
    try:
        adapter = MongoAtlasAdapter(cfg)
        result["ping"] = adapter.ping()
        if args.ensure_indexes:
            result["indexes"] = adapter.ensure_indexes()
        result["ok"] = True
    except MongoPersistenceDisabled as exc:
        result["errors"].append(str(exc))
    except Exception as exc:
        result["errors"].append(f"{type(exc).__name__}: {exc}")

    out = ROOT / "sample_outputs" / "mongodb_live_readiness.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
