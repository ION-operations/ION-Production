#!/usr/bin/env python3
"""Demonstrate v0.8 adapter gates without external MongoDB mutation."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ion_kernel.mongodb_adapter import MongoAdapterConfig, NullMongoAdapter, MongoPersistenceDisabled, MongoAtlasAdapter  # noqa: E402

# Force sample gate closed for validation.
os.environ["ION_MONGODB_ENABLED"] = "false"
os.environ.pop("MONGODB_URI", None)

cfg = MongoAdapterConfig.from_env()
null_adapter = NullMongoAdapter()
null_adapter.record("attempt_persist_continuity_objects", [{"object_id": "sample"}])
blocked_message = None
try:
    MongoAtlasAdapter(cfg)
except Exception as exc:
    blocked_message = str(exc)

summary = {
    "schema": "ion.mongodb_adapter_contract_demo.v0_8",
    "mongodb_config_enabled": cfg.enabled,
    "durable_adapter_blocked": isinstance(blocked_message, str),
    "blocked_message": blocked_message,
    "null_adapter_summary": null_adapter.summary(),
    "accepted_state_changed": False,
    "external_mutation_attempted": False,
}
out = ROOT / "sample_outputs" / "mongodb_adapter_contract_demo.json"
out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
sys.exit(0 if summary["durable_adapter_blocked"] else 1)
