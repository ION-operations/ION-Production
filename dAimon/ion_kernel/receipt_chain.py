"""Receipt candidate issuance."""
from __future__ import annotations

from typing import List
import json
import hashlib

from ion_kernel.schemas import ContinuityObject, ReceiptCandidate, utc_now


def issue_receipt_candidate(
    session_id: str,
    objects: List[ContinuityObject],
    issued_by: str = "ion_kernel_sample",
    receipt_label: str = "sample_001",
    receipt_type: str = "CANDIDATE_SAMPLE",
    non_claims: List[str] | None = None,
) -> ReceiptCandidate:
    object_dicts = [o.to_dict() for o in objects]
    inheritable = [o["object_id"] for o in object_dicts if o["inheritance_status"] == "INHERITABLE_AFTER_RECEIPT"]
    proof_debt = [o for o in object_dicts if "PROOF_DEBT" in o["proof_status"] or "NEEDS" in o["proof_status"]]
    settled = [o for o in object_dicts if o.get("settlement_decision")]
    payload = {
        "session_id": session_id,
        "objects": object_dicts,
        "inheritable": inheritable,
        "proof_debt": [o["object_id"] for o in proof_debt],
    }
    proof_hash = "sha256:" + hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return ReceiptCandidate(
        receipt_id=f"receipt_{session_id}_{receipt_label}",
        session_id=session_id,
        receipt_type=receipt_type,
        issued_at=utc_now(),
        issued_by=issued_by,
        accepted_state_changed=False,
        external_mutation_attempted=False,
        objects_classified=len(objects),
        objects_settled=len(settled),
        proof_debt_count=len(proof_debt),
        non_claims=non_claims or [
            "Local sample mode did not mutate durable accepted state.",
            "MongoDB, Google Cloud, and MCP calls are represented as target integration boundaries only.",
            "Accepted sample objects are for demo inheritance only until operator/steward settlement in the real system.",
        ],
        inheritable_objects=inheritable,
        proof_hash=proof_hash,
    )
