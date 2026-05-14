#!/usr/bin/env python3
"""Candidate architecture signal capture helper v4.4b."""
from __future__ import annotations
from typing import Dict, Any, Iterable


def capture_signal(signal_id: str, raw_summary: str, normalized_requirement: str, version: str, aliases: Iterable[str] = ()) -> Dict[str, Any]:
    return {
        "ion_architecture_signal": {
            "schema_id": "ion.architecture_signal.v1",
            "signal_id": signal_id,
            "captured_at_utc": "candidate_timestamp",
            "source": "operator_chat",
            "raw_summary": raw_summary,
            "normalized_requirement": normalized_requirement,
            "aliases": list(aliases),
            "related_existing_protocols": [],
            "product_version_target": version,
            "status": "candidate_unimplemented",
            "continuity_export_required": True,
            "tests_required": True,
            "accepted_state_claim": False,
        }
    }
