#!/usr/bin/env python3
"""Run the local ION Continuity Bridge sample.

No external services are contacted. This script exercises the same functional
lifecycle the contest implementation will connect to MongoDB MCP and Agent
Builder.
"""
from __future__ import annotations

from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from ion_kernel.bridge_core import import_bundle
from ion_kernel.settlement_queue import build_settlement_queue, apply_decisions
from ion_kernel.receipt_chain import issue_receipt_candidate
from ion_kernel.inheritance import resolve_inheritance
from ion_kernel.mcp_trace import build_mcp_visibility_trace
from ion_kernel.persistence import JsonFileStore


def main() -> int:
    session_id = "sample_session_20260509"
    input_dir = REPO_ROOT / "sample_inputs"
    output_dir = REPO_ROOT / "sample_outputs"
    store = JsonFileStore(output_dir)

    objects = import_bundle(input_dir, session_id)
    queue = build_settlement_queue(objects)

    # Deterministic sample decisions: accept high-authority operator decisions
    # and source references, request proof for low-authority synthesis, defer tasks.
    decisions = {}
    for obj in objects:
        if obj.authority_score >= 80 or obj.inferred_role in {"SOURCE_REFERENCE", "RECEIPT_REFERENCE"}:
            decisions[obj.object_id] = "ACCEPT"
        elif obj.inferred_role == "NEXT_WORK_CANDIDATE":
            decisions[obj.object_id] = "DEFER"
        elif "low_authority_import" in obj.risk_flags:
            decisions[obj.object_id] = "REQUEST_PROOF"
        else:
            decisions[obj.object_id] = "DEFER"

    objects, queue = apply_decisions(objects, queue, decisions, settled_by="sample_operator")
    receipt = issue_receipt_candidate(session_id, objects)
    inheritance = resolve_inheritance(session_id, objects, [receipt.receipt_id])
    mcp_trace = build_mcp_visibility_trace(
        session_id,
        inheritance.inherited_object_ids,
        inherited_objects=inheritance.objects,
        all_objects=[o.to_dict() for o in objects],
        receipt_ids=inheritance.receipt_ids,
        receipt_proof_hash=receipt.proof_hash,
        query="What governed continuity may the next Gemini session inherit?",
    )

    store.write_json("continuity_objects.json", [o.to_dict() for o in objects])
    store.write_json("settlement_queue.json", [q.to_dict() for q in queue])
    store.write_json("receipt_candidate.json", receipt.to_dict())
    store.write_json("inheritance_bundle.json", inheritance.to_dict())
    store.write_json("mcp_visibility_trace.json", mcp_trace)
    store.write_json("mcp_trace_dashboard_trace.json", {
        "schema": "ion.mcp_trace.dashboard_trace.v0_2",
        "session_id": session_id,
        "trace_rows": mcp_trace["dashboard_trace_rows"],
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
    })
    output_files = [
        "continuity_objects.json",
        "settlement_queue.json",
        "receipt_candidate.json",
        "inheritance_bundle.json",
        "mcp_visibility_trace.json",
        "mcp_trace_dashboard_trace.json",
        "local_demo_summary.json",
    ]

    summary = {
        "session_id": session_id,
        "objects_classified": len(objects),
        "settlement_queue_count": len(queue),
        "decisions_applied": len(decisions),
        "inheritable_count": len(inheritance.inherited_object_ids),
        "proof_debt_count": receipt.proof_debt_count,
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
        "outputs": output_files,
    }
    store.write_json("local_demo_summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
