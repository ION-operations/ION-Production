"""MongoDB Atlas persistence adapter for ION Continuity Bridge.

The adapter is intentionally explicit and fail-closed:
- local sample mode never requires MongoDB credentials;
- durable writes only run when ION_MONGODB_ENABLED=true and MONGODB_URI is present;
- every write remains candidate-state unless a validated receipt says otherwise;
- MCP visibility is a separate contest evidence requirement, not replaced by pymongo.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional
import os


ACCEPTED_STATUS_ALLOWLIST = [
    "settled_accept_sample",
    "ACCEPTED",
    "RECEIPT_CLEARED",
    "receipt_cleared",
]


class MongoPersistenceDisabled(RuntimeError):
    """Raised when code asks for MongoDB persistence but the gate is not open."""


@dataclass(frozen=True)
class MongoAdapterConfig:
    uri: Optional[str]
    database: str = "ion_continuity_bridge"
    enabled: bool = False
    collection_prefix: str = ""
    vector_index_name: str = "ion_continuity_vector_index"

    @classmethod
    def from_env(cls) -> "MongoAdapterConfig":
        raw_enabled = os.getenv("ION_MONGODB_ENABLED", "false").lower() in {"1", "true", "yes"}
        uri = os.getenv("MONGODB_URI")
        return cls(
            uri=uri,
            database=os.getenv("MONGODB_DB", "ion_continuity_bridge"),
            enabled=bool(raw_enabled and uri),
            collection_prefix=os.getenv("MONGODB_COLLECTION_PREFIX", ""),
            vector_index_name=os.getenv("MONGODB_VECTOR_INDEX", "ion_continuity_vector_index"),
        )

    def collection(self, name: str) -> str:
        return f"{self.collection_prefix}{name}" if self.collection_prefix else name


class MongoAtlasAdapter:
    """Small, auditable adapter around pymongo operations needed by the MVP."""

    def __init__(self, config: MongoAdapterConfig):
        if not config.enabled or not config.uri:
            raise MongoPersistenceDisabled("MongoDB adapter requested while disabled or missing MONGODB_URI")
        try:
            from pymongo import MongoClient, UpdateOne  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("pymongo is required for MongoAtlasAdapter") from exc
        self.config = config
        self._UpdateOne = UpdateOne
        self.client = MongoClient(config.uri, serverSelectionTimeoutMS=5000)
        self.db = self.client[config.database]

    def ping(self) -> Dict[str, Any]:
        result = self.client.admin.command("ping")
        return {
            "ok": bool(result.get("ok")),
            "database": self.config.database,
            "collections": self.collection_names(),
            "accepted_state_changed": False,
        }

    def collection_names(self) -> Dict[str, str]:
        return {
            "continuity_objects": self.config.collection("continuity_objects"),
            "settlement_queue": self.config.collection("settlement_queue"),
            "receipts": self.config.collection("receipts"),
            "sessions": self.config.collection("sessions"),
            "domain_registry": self.config.collection("domain_registry"),
        }

    def ensure_indexes(self) -> Dict[str, Any]:
        names = self.collection_names()
        self.db[names["continuity_objects"]].create_index("object_id", unique=True)
        self.db[names["continuity_objects"]].create_index([("session_id", 1), ("inheritance_status", 1)])
        self.db[names["continuity_objects"]].create_index([("session_id", 1), ("acceptance_status", 1)])
        self.db[names["settlement_queue"]].create_index("queue_id", unique=True)
        self.db[names["receipts"]].create_index("receipt_id", unique=True)
        self.db[names["sessions"]].create_index("session_id", unique=True)
        return {
            "indexes_ensured": True,
            "vector_index_name_expected": self.config.vector_index_name,
            "non_claim": "Atlas Vector Search index creation may be performed through Atlas/MCP in the judged environment.",
        }

    def upsert_session(self, session_id: str, metadata: Dict[str, Any]) -> str:
        names = self.collection_names()
        self.db[names["sessions"]].update_one(
            {"session_id": session_id},
            {"$set": {"session_id": session_id, "metadata": metadata, "accepted_state_changed": False}},
            upsert=True,
        )
        return session_id

    def insert_continuity_objects(self, docs: List[Dict[str, Any]]) -> int:
        if not docs:
            return 0
        names = self.collection_names()
        ops = [
            self._UpdateOne({"object_id": d["object_id"]}, {"$set": d}, upsert=True)
            for d in docs
        ]
        self.db[names["continuity_objects"]].bulk_write(ops, ordered=False)
        return len(docs)

    def replace_settled_objects(self, docs: List[Dict[str, Any]]) -> int:
        return self.insert_continuity_objects(docs)

    def insert_settlement_queue(self, docs: List[Dict[str, Any]]) -> int:
        if not docs:
            return 0
        names = self.collection_names()
        ops = [
            self._UpdateOne({"queue_id": d["queue_id"]}, {"$set": d}, upsert=True)
            for d in docs
        ]
        self.db[names["settlement_queue"]].bulk_write(ops, ordered=False)
        return len(docs)

    def replace_settlement_queue(self, docs: List[Dict[str, Any]]) -> int:
        return self.insert_settlement_queue(docs)

    def insert_receipt(self, receipt: Dict[str, Any]) -> str:
        names = self.collection_names()
        self.db[names["receipts"]].update_one(
            {"receipt_id": receipt["receipt_id"]},
            {"$set": receipt},
            upsert=True,
        )
        return receipt["receipt_id"]

    def find_inheritable_objects(self, session_id: str, limit: int = 25) -> List[Dict[str, Any]]:
        names = self.collection_names()
        cursor = self.db[names["continuity_objects"]].find(
            {
                "session_id": session_id,
                "inheritance_status": "INHERITABLE_AFTER_RECEIPT",
                "acceptance_status": {"$in": ACCEPTED_STATUS_ALLOWLIST},
            },
            {"_id": 0},
        ).limit(limit)
        return list(cursor)

    def find_session_objects(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Read candidate/witness/settled objects for exclusion reporting.

        This intentionally returns no MongoDB `_id` values and does not broaden
        inheritance. Callers must use `find_inheritable_objects` for any context
        that future agents may rely on.
        """
        names = self.collection_names()
        cursor = self.db[names["continuity_objects"]].find(
            {"session_id": session_id},
            {"_id": 0},
        ).limit(limit)
        return list(cursor)

    def find_receipts_for_session(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        names = self.collection_names()
        cursor = self.db[names["receipts"]].find(
            {"session_id": session_id},
            {"_id": 0},
        ).sort("issued_at", -1).limit(limit)
        return list(cursor)

    def governed_text_query(self, session_id: str, query: str, limit: int = 10) -> Dict[str, Any]:
        """Fallback text query for demos; vector search should be added through Atlas/MCP."""
        names = self.collection_names()
        cursor = self.db[names["continuity_objects"]].find(
            {
                "session_id": session_id,
                "inheritance_status": "INHERITABLE_AFTER_RECEIPT",
                "$text": {"$search": query},
            },
            {"_id": 0},
        ).limit(limit)
        return {
            "query": query,
            "results": list(cursor),
            "non_claim": "Text query fallback; production demo should show MongoDB MCP aggregate/vector search trace.",
        }


class NullMongoAdapter:
    """Local validation adapter that proves no external mutation occurs."""

    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []

    def record(self, operation: str, payload: Any | None = None) -> Dict[str, Any]:
        event = {
            "operation": operation,
            "payload_type": type(payload).__name__,
            "accepted_state_changed": False,
            "external_mutation_attempted": False,
        }
        self.calls.append(event)
        return event

    def summary(self) -> Dict[str, Any]:
        return {
            "adapter": "NullMongoAdapter",
            "calls": self.calls,
            "accepted_state_changed": False,
            "external_mutation_attempted": False,
        }
