"""Resolve inheritance bundle from settled objects."""
from __future__ import annotations

from typing import List

from ion_kernel.schemas import ContinuityObject, InheritanceBundle, utc_now


def resolve_inheritance(session_id: str, objects: List[ContinuityObject], receipt_ids: List[str]) -> InheritanceBundle:
    inheritable = [o.to_dict() for o in objects if o.inheritance_status == "INHERITABLE_AFTER_RECEIPT"]
    return InheritanceBundle(
        session_id=session_id,
        generated_at=utc_now(),
        inherited_object_ids=[o["object_id"] for o in inheritable],
        objects=inheritable,
        non_claims=[
            "Inheritance bundle excludes rejected, deferred, and proof-debt objects.",
            "This bundle is generated in sample mode and does not claim production acceptance.",
        ],
        receipt_ids=receipt_ids,
    )
