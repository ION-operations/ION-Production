"""Settlement queue logic."""
from __future__ import annotations

from typing import Dict, List

from ion_kernel.schemas import ContinuityObject, SettlementQueueItem, stable_hash, utc_now


DEFAULT_OPTIONS = ["ACCEPT", "REJECT", "DEFER", "REQUEST_PROOF"]


def build_settlement_queue(objects: List[ContinuityObject]) -> List[SettlementQueueItem]:
    queue: List[SettlementQueueItem] = []
    for obj in objects:
        d = obj.to_dict()
        if d["requires_settlement"]:
            queue.append(SettlementQueueItem(
                queue_id=f"sq_{stable_hash({'object_id': d['object_id'], 'session': d['session_id']}, 10)}",
                object_id=d["object_id"],
                session_id=d["session_id"],
                text=d["text"],
                inferred_role=d["inferred_role"],
                authority_score=d["authority_score"],
                settlement_options=DEFAULT_OPTIONS,
            ))
    return queue


def apply_decisions(objects: List[ContinuityObject], queue: List[SettlementQueueItem], decisions: Dict[str, str], settled_by: str = "sample_operator") -> tuple[List[ContinuityObject], List[SettlementQueueItem]]:
    object_by_id = {o.object_id: o for o in objects}
    for item in queue:
        decision = decisions.get(item.object_id)
        if not decision:
            continue
        item.settled = True
        item.settlement_decision = decision
        item.settled_by = settled_by
        item.settled_at = utc_now()
        obj = object_by_id.get(item.object_id)
        if not obj:
            continue
        obj.settlement_decision = decision
        obj.settled_by = settled_by
        obj.settled_at = item.settled_at
        if decision == "ACCEPT":
            obj.acceptance_status = "settled_accept_sample"
            obj.acceptance_role = "ACCEPTED_FOR_SAMPLE_INHERITANCE"
            obj.inheritance_status = "INHERITABLE_AFTER_RECEIPT"
        elif decision == "REJECT":
            obj.acceptance_status = "settled_reject_sample"
            obj.acceptance_role = "REJECTED_WITNESS"
            obj.inheritance_status = "NOT_INHERITABLE_REJECTED"
        elif decision == "REQUEST_PROOF":
            obj.acceptance_status = "proof_requested_sample"
            obj.acceptance_role = "PROOF_REQUESTED"
            obj.inheritance_status = "NOT_INHERITABLE_PENDING_PROOF"
        else:
            obj.acceptance_status = "deferred_sample"
            obj.acceptance_role = "DEFERRED"
            obj.inheritance_status = "NOT_INHERITABLE_DEFERRED"
    return objects, queue
