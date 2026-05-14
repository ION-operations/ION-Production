#!/usr/bin/env python3
"""Candidate folder context capsule linter v4.5."""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List
import yaml

REQUIRED = [
    "schema_id",
    "capsule_id",
    "folder",
    "status",
    "generated_at_utc",
    "identity",
    "authority",
    "read_first",
    "active_objectives",
    "local_agents",
    "domains",
    "automations",
    "continuity_export",
    "freshness",
    "boundaries",
]


def lint_capsule(path: Path) -> List[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    errors = [f"missing:{key}" for key in REQUIRED if key not in data]
    authority = data.get("authority", {})
    for key in ["accepted_state_claim", "production_authority", "live_execution_authority", "requires_receipt_for_state_claim"]:
        if key not in authority:
            errors.append(f"missing_authority:{key}")
    if authority.get("production_authority") is True or authority.get("live_execution_authority") is True:
        errors.append("capsule_grants_live_or_production_authority")
    return errors
