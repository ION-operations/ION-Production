#!/usr/bin/env python3
"""Run the full dAimon contest vertical slice with live MongoDB and Gemini.

The command remains fail-closed. Pass --confirm-live-run to write candidate demo
records to MongoDB and call Gemini with a receipt-cleared inheritance bundle.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

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
from run_gemini_handoff_demo import run_gemini_handoff
from seed_mongodb_candidate_sample import sample_decisions


def _write_json(output_dir: Path, filename: str, payload: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / filename).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _blocked_summary(reason: str) -> dict[str, Any]:
    return {
        "schema": "daimon.live_vertical_slice_summary.v0_1",
        "ok": False,
        "blocked": True,
        "reason": reason,
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm-live-run", action="store_true")
    parser.add_argument("--session-id", default="daimon_live_vertical_slice_20260509")
    parser.add_argument("--model", default="gemini-2.5-flash")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--ensure-indexes", action="store_true")
    parser.add_argument("--skip-gemini", action="store_true")
    parser.add_argument(
        "--question",
        default="For the next Gemini-era dAimon session, summarize only the receipt-cleared state and list excluded boundaries.",
    )
    args = parser.parse_args()

    output_dir = ROOT / "sample_outputs"
    if not args.confirm_live_run:
        summary = _blocked_summary("pass --confirm-live-run to write candidate demo records and call Gemini")
        _write_json(output_dir, "live_vertical_slice_summary.json", summary)
        print(json.dumps(summary, indent=2))
        return 2

    load_local_env(ROOT / ".env")
    cfg = MongoAdapterConfig.from_env()
    adapter = MongoAtlasAdapter(cfg)
    index_result = adapter.ensure_indexes() if args.ensure_indexes else {
        "indexes_ensured": False,
        "reason": "not requested",
    }

    objects = import_bundle(ROOT / "sample_inputs", args.session_id)
    queue = build_settlement_queue(objects)
    decisions = sample_decisions(objects)
    objects, queue = apply_decisions(objects, queue, decisions, settled_by="live_vertical_slice_operator")
    receipt = issue_receipt_candidate(
        args.session_id,
        objects,
        issued_by="live_vertical_slice",
        receipt_label="live_seed_001",
        receipt_type="LIVE_VERTICAL_SLICE_SEED",
        non_claims=[
            "MongoDB writes are candidate demo records, not accepted ION production state.",
            "Accepted sample objects are receipt-cleared only inside this contest vertical slice.",
            "This receipt proves API-level handoff readiness, not complete enterprise deployment.",
        ],
    )
    inheritance = resolve_inheritance(args.session_id, objects, [receipt.receipt_id])

    adapter.upsert_session(args.session_id, {
        "source": "sample_inputs",
        "mode": "live_vertical_slice",
        "claim_boundary": "candidate demo records only; accepted ION production state unchanged",
    })
    objects_written = adapter.insert_continuity_objects([obj.to_dict() for obj in objects])
    queue_written = adapter.insert_settlement_queue([item.to_dict() for item in queue])
    receipt_id = adapter.insert_receipt(receipt.to_dict())
    inherited_from_mongodb = adapter.find_inheritable_objects(args.session_id, limit=25)

    trace = build_mcp_visibility_trace(
        args.session_id,
        inheritance.inherited_object_ids,
        inherited_objects=inherited_from_mongodb,
        all_objects=[obj.to_dict() for obj in objects],
        receipt_ids=inheritance.receipt_ids,
        receipt_proof_hash=receipt.proof_hash,
        query="Retrieve receipt-cleared continuity for the live Gemini handoff.",
        database=cfg.database,
        collection=cfg.collection("continuity_objects"),
    )
    _write_json(output_dir, "live_vertical_slice_receipt.json", receipt.to_dict())
    _write_json(output_dir, "live_vertical_slice_inheritance_bundle.json", inheritance.to_dict())
    _write_json(output_dir, "live_vertical_slice_mcp_trace.json", trace)

    gemini_summary: dict[str, Any] | None = None
    gemini_candidate_written = 0
    gemini_queue_written = 0
    gemini_receipt_id = None
    if not args.skip_gemini:
        gemini_summary = run_gemini_handoff(
            session_id=args.session_id,
            inherited_objects=inherited_from_mongodb,
            receipt_ids=inheritance.receipt_ids,
            receipt_proof_hash=receipt.proof_hash,
            question=args.question,
            output_dir=output_dir,
            preferred_model=args.model,
            timeout=args.timeout,
        )
        candidate_objects = gemini_summary.get("candidate_objects") or []
        candidate_queue = gemini_summary.get("candidate_queue") or []
        candidate_receipt = gemini_summary.get("candidate_receipt")
        if candidate_objects:
            gemini_candidate_written = adapter.insert_continuity_objects(candidate_objects)
        if candidate_queue:
            gemini_queue_written = adapter.insert_settlement_queue(candidate_queue)
        if candidate_receipt:
            gemini_receipt_id = adapter.insert_receipt(candidate_receipt)

    phases = [
        {"phase": "import", "status": "ok", "objects_classified": len(objects)},
        {"phase": "settle", "status": "ok", "decisions_applied": len(decisions)},
        {"phase": "receipt", "status": "ok", "receipt_id": receipt_id},
        {"phase": "mongodb_write", "status": "ok", "objects_written": objects_written, "queue_items_written": queue_written},
        {"phase": "mongodb_accepted_only_read", "status": "ok", "returned_count": len(inherited_from_mongodb)},
        {"phase": "mcp_visibility_trace", "status": "ok", "returned_count": len(trace["returned_continuity_object_ids"])},
    ]
    if gemini_summary:
        phases.append({
            "phase": "gemini_handoff",
            "status": "ok" if gemini_summary.get("ok") else "blocked_or_failed",
            "model": gemini_summary.get("model"),
            "candidate_receipt_id": gemini_summary.get("candidate_receipt_id"),
        })
        phases.append({
            "phase": "gemini_candidate_persistence",
            "status": "ok" if gemini_candidate_written else "not_written",
            "candidate_objects_written": gemini_candidate_written,
            "queue_items_written": gemini_queue_written,
            "receipt_id": gemini_receipt_id,
        })

    gemini_ok = True if args.skip_gemini else bool(gemini_summary and gemini_summary.get("ok"))
    summary = {
        "schema": "daimon.live_vertical_slice_summary.v0_1",
        "ok": bool(inherited_from_mongodb) and gemini_ok,
        "session_id": args.session_id,
        "mongo_database": cfg.database,
        "mongo_collection": cfg.collection("continuity_objects"),
        "index_result": index_result,
        "phases": phases,
        "objects_classified": len(objects),
        "objects_written": objects_written,
        "settlement_queue_items_written": queue_written,
        "receipt_id": receipt_id,
        "inheritable_count_local": len(inheritance.inherited_object_ids),
        "inheritable_returned_from_mongodb": len(inherited_from_mongodb),
        "trace_returned_object_count": len(trace["returned_continuity_object_ids"]),
        "gemini": None if not gemini_summary else {
            key: value
            for key, value in gemini_summary.items()
            if key not in {"candidate_objects", "candidate_queue", "candidate_receipt"}
        },
        "claim_status": {
            "local_governance_pipeline": "proven_local",
            "mongodb_live_seed_and_inheritance": "proven_live_mongodb" if inherited_from_mongodb else "blocked",
            "gemini_receipt_cleared_handoff": "skipped" if args.skip_gemini else ("proven_live_google" if gemini_ok else "blocked"),
            "full_vertical_slice_end_to_end": "proven_live" if bool(inherited_from_mongodb) and gemini_ok else "blocked",
        },
        "artifacts": [
            "sample_outputs/live_vertical_slice_summary.json",
            "sample_outputs/live_vertical_slice_receipt.json",
            "sample_outputs/live_vertical_slice_inheritance_bundle.json",
            "sample_outputs/live_vertical_slice_mcp_trace.json",
            "sample_outputs/gemini_handoff_context_bundle.json",
            "sample_outputs/gemini_handoff_request.json",
            "sample_outputs/gemini_handoff_response.json",
            "sample_outputs/gemini_candidate_output.json",
            "sample_outputs/gemini_handoff_summary.json",
        ],
        "accepted_state_changed": False,
        "external_mutation_attempted": True,
        "non_claims": [
            "MongoDB writes are candidate demo records, not accepted ION production state.",
            "Gemini output is captured as candidate and is not automatically trusted.",
            "This script proves API-level Gemini handoff, not complete Google Agent Builder deployment.",
        ],
    }
    _write_json(output_dir, "live_vertical_slice_summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0 if summary["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
