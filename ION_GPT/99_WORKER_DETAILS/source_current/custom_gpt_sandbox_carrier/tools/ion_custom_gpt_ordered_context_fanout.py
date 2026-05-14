#!/usr/bin/env python3
"""Candidate ordered context fan-out helper v4.4."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any


def make_baton(branch_id: str, source_range: str, summary: str, downstream_alerts: list | None = None) -> Dict[str, Any]:
    return {
        "ion_context_baton": {
            "schema_id": "ion.context_baton.v1",
            "branch_id": branch_id,
            "source_range": source_range,
            "summary_dense": summary,
            "source_anchors": [],
            "tags": [],
            "definitions": [],
            "entities": [],
            "claims": [],
            "dependency_edges": [],
            "downstream_alerts": downstream_alerts or [],
            "unresolved_questions": [],
            "upstream_reopen_alerts": [],
            "confidence": {"level": "scoped", "limitations": []},
        }
    }


def can_finalize(branch_id: str, available_batons: set[str], required_batons: dict[str, list[str]]) -> bool:
    return set(required_batons.get(branch_id, [])) <= set(available_batons)


def source_ordered_merge(branch_returns: list[dict]) -> list[dict]:
    return sorted(branch_returns, key=lambda item: item["source_order"])
