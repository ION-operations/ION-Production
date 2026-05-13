"""ION Continuity Bridge schemas.

This module uses stdlib dataclasses so the local demo can run without external
packages. The FastAPI service can wrap the same dict structures with Pydantic
models later.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import hashlib
import json


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stable_hash(value: Any, length: int = 16) -> str:
    payload = json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:length]


@dataclass
class ContinuityObject:
    object_id: str
    session_id: str
    source_file: str
    source_format: str
    text: str
    declared_type: str
    inferred_role: str
    authority_class: str
    authority_score: int
    acceptance_status: str
    acceptance_role: str
    inheritance_status: str
    requires_settlement: bool
    proof_status: str
    risk_flags: List[str] = field(default_factory=list)
    text_hash: str = ""
    created_at: str = field(default_factory=utc_now)
    settled_at: Optional[str] = None
    settled_by: Optional[str] = None
    settlement_decision: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if not data["text_hash"]:
            data["text_hash"] = stable_hash({"text": self.text, "source": self.source_file})
        return data


@dataclass
class SettlementQueueItem:
    queue_id: str
    object_id: str
    session_id: str
    text: str
    inferred_role: str
    authority_score: int
    settlement_options: List[str]
    settled: bool = False
    settlement_decision: Optional[str] = None
    settled_at: Optional[str] = None
    settled_by: Optional[str] = None
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReceiptCandidate:
    receipt_id: str
    session_id: str
    receipt_type: str
    issued_at: str
    issued_by: str
    accepted_state_changed: bool
    external_mutation_attempted: bool
    objects_classified: int
    objects_settled: int
    proof_debt_count: int
    non_claims: List[str]
    inheritable_objects: List[str]
    proof_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InheritanceBundle:
    session_id: str
    generated_at: str
    inherited_object_ids: List[str]
    objects: List[Dict[str, Any]]
    non_claims: List[str]
    receipt_ids: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
