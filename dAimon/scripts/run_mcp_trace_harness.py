#!/usr/bin/env python3
"""Generate the local MongoDB MCP visibility trace harness artifact.

This is the credential-free proof path for RAH-011A. It does not call Google
Cloud, Agent Builder, MongoDB Atlas, or a live MCP server. It builds the exact
query/envelope/citation/exclusion shape that a live judged trace must later
replace with captured MCP evidence.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ion_kernel.bridge_core import import_bundle
from ion_kernel.inheritance import resolve_inheritance
from ion_kernel.mcp_trace import build_mcp_visibility_trace
from ion_kernel.persistence import JsonFileStore
from ion_kernel.receipt_chain import issue_receipt_candidate
from ion_kernel.settlement_queue import apply_decisions, build_settlement_queue


def _sample_decisions(objects: list) -> dict[str, str]:
    decisions: dict[str, str] = {}
    for obj in objects:
        if obj.authority_score >= 80 or obj.inferred_role in {"SOURCE_REFERENCE", "RECEIPT_REFERENCE"}:
            decisions[obj.object_id] = "ACCEPT"
        elif obj.inferred_role == "NEXT_WORK_CANDIDATE":
            decisions[obj.object_id] = "DEFER"
        elif "low_authority_import" in obj.risk_flags:
            decisions[obj.object_id] = "REQUEST_PROOF"
        else:
            decisions[obj.object_id] = "DEFER"
    return decisions


def main() -> int:
    session_id = "sample_session_20260509"
    output_dir = ROOT / "sample_outputs"
    store = JsonFileStore(output_dir)

    objects = import_bundle(ROOT / "sample_inputs", session_id)
    queue = build_settlement_queue(objects)
    objects, queue = apply_decisions(objects, queue, _sample_decisions(objects), settled_by="sample_operator")
    receipt = issue_receipt_candidate(session_id, objects, issued_by="mcp_trace_harness_local")
    inheritance = resolve_inheritance(session_id, objects, [receipt.receipt_id])
    trace = build_mcp_visibility_trace(
        session_id,
        inheritance.inherited_object_ids,
        inherited_objects=inheritance.objects,
        all_objects=[o.to_dict() for o in objects],
        receipt_ids=inheritance.receipt_ids,
        receipt_proof_hash=receipt.proof_hash,
        query="Show governed continuity that Gemini may inherit through MongoDB MCP.",
    )
    dashboard_trace = {
        "schema": "ion.mcp_trace.dashboard_trace.v0_2",
        "session_id": session_id,
        "trace_rows": trace["dashboard_trace_rows"],
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
        "non_claim": "Dashboard rows are local harness evidence, not a live Agent Builder or MongoDB MCP run.",
    }

    store.write_json("mcp_visibility_trace.json", trace)
    store.write_json("mcp_trace_dashboard_trace.json", dashboard_trace)

    summary = {
        "schema": "ion.mcp_trace_harness.result.v0_2",
        "trace_path": "sample_outputs/mcp_visibility_trace.json",
        "dashboard_trace_path": "sample_outputs/mcp_trace_dashboard_trace.json",
        "returned_object_count": len(trace["returned_continuity_object_ids"]),
        "receipt_citation_count": len(trace["returned_object_citations"]),
        "excluded_count": trace["exclusion_report"]["excluded_count"],
        "returned_excluded_overlap_count": len(trace["exclusion_report"]["returned_excluded_overlap"]),
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
    }
    print(json.dumps(summary, indent=2))
    return 0 if summary["returned_excluded_overlap_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
