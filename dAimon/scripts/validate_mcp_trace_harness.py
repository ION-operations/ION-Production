#!/usr/bin/env python3
"""Validate the local RAH-011A MongoDB MCP trace harness artifact."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TRACE_PATH = ROOT / "sample_outputs" / "mcp_visibility_trace.json"
INHERITANCE_PATH = ROOT / "sample_outputs" / "inheritance_bundle.json"
DASHBOARD_TRACE_PATH = ROOT / "sample_outputs" / "mcp_trace_dashboard_trace.json"


def main() -> int:
    errors: list[str] = []
    for path in [TRACE_PATH, INHERITANCE_PATH, DASHBOARD_TRACE_PATH]:
        if not path.exists():
            errors.append(f"missing {path.relative_to(ROOT)}")

    trace = {}
    inheritance = {}
    dashboard = {}
    if not errors:
        try:
            trace = json.loads(TRACE_PATH.read_text(encoding="utf-8"))
            inheritance = json.loads(INHERITANCE_PATH.read_text(encoding="utf-8"))
            dashboard = json.loads(DASHBOARD_TRACE_PATH.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"json parse failed: {exc}")

    if not errors:
        if trace.get("schema") != "ion.mcp_visibility_trace.v0_2":
            errors.append("mcp trace schema must be ion.mcp_visibility_trace.v0_2")
        if trace.get("required_mcp_server") != "MongoDB MCP Server":
            errors.append("trace must name MongoDB MCP Server")
        query_filter = trace.get("accepted_only_query_shape", {}).get("filter", {})
        if query_filter.get("inheritance_status") != "INHERITABLE_AFTER_RECEIPT":
            errors.append("query filter must require INHERITABLE_AFTER_RECEIPT")
        acceptance_filter = query_filter.get("acceptance_status", {})
        if "settled_accept_sample" not in acceptance_filter.get("$in", []):
            errors.append("query filter must allow settled accepted sample objects")

        envelope = trace.get("mongodb_mcp_request_envelope", {})
        if envelope.get("tool_name") != "mongodb.aggregate":
            errors.append("MCP envelope must name mongodb.aggregate")
        if envelope.get("read_only") is not True:
            errors.append("MCP envelope must be read-only")
        pipeline = envelope.get("arguments", {}).get("pipeline", [])
        if not pipeline or "$match" not in pipeline[0]:
            errors.append("MCP envelope must start with a $match pipeline stage")

        inherited_ids = set(inheritance.get("inherited_object_ids", []))
        returned_ids = set(trace.get("returned_continuity_object_ids", []))
        if not returned_ids:
            errors.append("trace returned_continuity_object_ids must be non-empty")
        if returned_ids != inherited_ids:
            errors.append("returned IDs must match sample inheritance bundle IDs")
        overlap = trace.get("exclusion_report", {}).get("returned_excluded_overlap", [])
        if overlap:
            errors.append(f"excluded IDs were returned: {overlap}")

        citations = trace.get("returned_object_citations", [])
        if len(citations) != len(returned_ids):
            errors.append("every returned object must have a receipt citation")
        for citation in citations:
            if not citation.get("receipt_ids") and not citation.get("receipt_proof_hash"):
                errors.append(f"missing receipt citation for {citation.get('object_id')}")
        if trace.get("accepted_state_changed") is not False:
            errors.append("trace must preserve accepted_state_changed=false")
        if trace.get("external_mutation_attempted") is not False:
            errors.append("trace must preserve external_mutation_attempted=false")
        if len(dashboard.get("trace_rows", [])) < 5:
            errors.append("dashboard trace must include at least five rows")

    result = {
        "ok": not errors,
        "errors": errors,
        "trace_path": str(TRACE_PATH.relative_to(ROOT)),
        "dashboard_trace_path": str(DASHBOARD_TRACE_PATH.relative_to(ROOT)),
        "returned_object_count": len(trace.get("returned_continuity_object_ids", [])) if trace else 0,
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
    }
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
