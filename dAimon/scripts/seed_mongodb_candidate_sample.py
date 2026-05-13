#!/usr/bin/env python3
"""Seed sample candidate continuity objects into MongoDB Atlas.

This script performs external MongoDB writes only when explicitly confirmed.
It is for demo preparation, not accepted-state mutation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from env_loader import load_local_env
from ion_kernel.bridge_core import import_bundle
from ion_kernel.inheritance import resolve_inheritance
from ion_kernel.mcp_trace import build_mcp_visibility_trace
from ion_kernel.mongodb_adapter import MongoAdapterConfig, MongoAtlasAdapter
from ion_kernel.receipt_chain import issue_receipt_candidate
from ion_kernel.settlement_queue import apply_decisions, build_settlement_queue


def sample_decisions(objects: list) -> dict[str, str]:
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm-candidate-write", action="store_true")
    parser.add_argument("--ensure-indexes", action="store_true")
    parser.add_argument("--session-id", default="sample_session_20260509")
    args = parser.parse_args()

    if not args.confirm_candidate_write:
        print(json.dumps({
            "ok": False,
            "blocked": True,
            "reason": "pass --confirm-candidate-write to write sample candidate objects to MongoDB",
            "accepted_state_changed": False,
            "external_mutation_attempted": False,
        }, indent=2))
        return 2

    load_local_env(ROOT / ".env")
    cfg = MongoAdapterConfig.from_env()
    adapter = MongoAtlasAdapter(cfg)
    if args.ensure_indexes:
        adapter.ensure_indexes()

    objects = import_bundle(ROOT / "sample_inputs", args.session_id)
    queue = build_settlement_queue(objects)
    objects, queue = apply_decisions(objects, queue, sample_decisions(objects), settled_by="sample_operator")
    receipt = issue_receipt_candidate(args.session_id, objects, issued_by="mongodb_candidate_seed")
    inheritance = resolve_inheritance(args.session_id, objects, [receipt.receipt_id])

    adapter.upsert_session(args.session_id, {"source": "sample_inputs", "mode": "candidate_seed"})
    objects_written = adapter.insert_continuity_objects([o.to_dict() for o in objects])
    queue_written = adapter.insert_settlement_queue([q.to_dict() for q in queue])
    receipt_id = adapter.insert_receipt(receipt.to_dict())
    inherited_from_mongodb = adapter.find_inheritable_objects(args.session_id, limit=25)

    trace = build_mcp_visibility_trace(
        args.session_id,
        inheritance.inherited_object_ids,
        inherited_objects=inherited_from_mongodb,
        all_objects=[o.to_dict() for o in objects],
        receipt_ids=inheritance.receipt_ids,
        receipt_proof_hash=receipt.proof_hash,
        query="Show governed continuity that Gemini may inherit through MongoDB MCP.",
        database=cfg.database,
        collection=cfg.collection("continuity_objects"),
    )
    summary = {
        "schema": "daimon.mongodb_candidate_seed.v0_1",
        "ok": True,
        "session_id": args.session_id,
        "objects_written": objects_written,
        "queue_items_written": queue_written,
        "receipt_id": receipt_id,
        "inheritable_returned_from_mongodb": len(inherited_from_mongodb),
        "trace_returned_object_count": len(trace["returned_continuity_object_ids"]),
        "accepted_state_changed": False,
        "external_mutation_attempted": True,
        "non_claim": "MongoDB sample seed writes candidate demo records only; this is not accepted ION production state.",
    }
    (ROOT / "sample_outputs" / "mongodb_candidate_seed_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    (ROOT / "sample_outputs" / "mongodb_candidate_seed_mcp_trace.json").write_text(
        json.dumps(trace, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
