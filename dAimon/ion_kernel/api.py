"""FastAPI surface for the ION Continuity Bridge Cloud Run service.

v1.0 adds the capability-route surface while preserving the boundary between
candidate routing, governed retrieval, and accepted state. Credentials are never
required for local validation and durable writes remain fail-closed unless
explicitly configured.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except Exception:  # pragma: no cover - service dependency missing in local sample
    FastAPI = None  # type: ignore
    BaseModel = object  # type: ignore

from ion_kernel.bridge_core import import_bundle
from ion_kernel.settlement_queue import build_settlement_queue, apply_decisions
from ion_kernel.receipt_chain import issue_receipt_candidate
from ion_kernel.inheritance import resolve_inheritance
from ion_kernel.mongodb_adapter import MongoAtlasAdapter, MongoAdapterConfig, MongoPersistenceDisabled
from ion_kernel.mcp_trace import build_mcp_visibility_trace
from ion_kernel.capability_router import load_capability_graph, route_objective

if FastAPI is None:
    app = None
else:
    app = FastAPI(title="dAimon — ION Continuity Bridge", version="1.1.0-candidate")


class ImportRequest(BaseModel):  # type: ignore[misc]
    session_id: str
    input_dir: str
    persist_to_mongodb: bool = False


class SettleRequest(BaseModel):  # type: ignore[misc]
    session_id: str
    decisions: Dict[str, str]
    settled_by: str = "operator"
    persist_to_mongodb: bool = False


class QueryRequest(BaseModel):  # type: ignore[misc]
    session_id: str
    query: str
    limit: int = 5


class LiveQueryRequest(BaseModel):  # type: ignore[misc]
    session_id: str
    query: str = "Find receipt-cleared continuity objects for the next Gemini session."
    limit: int = 5
    include_exclusion_report: bool = True


class TraceRequest(BaseModel):  # type: ignore[misc]
    session_id: str
    query: str = "Show governed continuity available to the next Gemini session."
    limit: int = 25


class RouteRequest(BaseModel):  # type: ignore[misc]
    session_id: str = "route_session"
    objective: str


_SESSION_CACHE: Dict[str, Dict[str, Any]] = {}


def _maybe_adapter(enabled: bool) -> MongoAtlasAdapter | None:
    if not enabled:
        return None
    cfg = MongoAdapterConfig.from_env()
    if not cfg.enabled:
        raise MongoPersistenceDisabled(
            "MongoDB persistence requested but ION_MONGODB_ENABLED is not true or MONGODB_URI is missing"
        )
    return MongoAtlasAdapter(cfg)


def _receipt_ids(receipts: list[Dict[str, Any]]) -> list[str]:
    return [str(item.get("receipt_id")) for item in receipts if item.get("receipt_id")]


def _proof_hash(receipts: list[Dict[str, Any]]) -> str | None:
    if not receipts:
        return None
    value = receipts[0].get("proof_hash")
    return str(value) if value else None


def _query_matches(objects: list[Dict[str, Any]], query: str, limit: int) -> list[Dict[str, Any]]:
    q = query.lower().strip()
    if not q:
        return objects[:limit]
    tokens = [token for token in q.split() if len(token) > 2]
    matches: list[Dict[str, Any]] = []
    for obj in objects:
        haystack = " ".join(
            str(obj.get(key, ""))
            for key in ["object_id", "object_type", "domain", "source_path", "text", "summary"]
        ).lower()
        if q in haystack or any(token in haystack for token in tokens):
            matches.append(obj)
    return (matches or objects)[:limit]


if app is not None:
    @app.get("/health")
    def health() -> Dict[str, Any]:
        cfg = MongoAdapterConfig.from_env()
        return {
            "ok": True,
            "service": "ion-continuity-bridge",
            "version": "1.1.0-candidate",
            "mode": os.getenv("ION_MODE", "sample"),
            "mongodb_enabled": cfg.enabled,
            "mongodb_database": cfg.database,
            "accepted_state_changed": False,
        }


    @app.post("/import")
    def import_session_files(req: ImportRequest) -> Dict[str, Any]:
        input_dir = Path(req.input_dir)
        if not input_dir.exists():
            raise HTTPException(status_code=400, detail=f"input_dir not found: {input_dir}")
        objects = import_bundle(input_dir, req.session_id)
        queue = build_settlement_queue(objects)
        _SESSION_CACHE[req.session_id] = {"objects": objects, "queue": queue, "receipts": []}
        persisted = False
        if req.persist_to_mongodb:
            try:
                adapter = _maybe_adapter(True)
                assert adapter is not None
                adapter.upsert_session(req.session_id, {"source": str(input_dir), "mode": "candidate_import"})
                adapter.insert_continuity_objects([o.to_dict() for o in objects])
                adapter.insert_settlement_queue([q.to_dict() for q in queue])
                persisted = True
            except Exception as exc:
                raise HTTPException(status_code=503, detail=f"MongoDB persistence blocked: {exc}") from exc
        return {
            "session_id": req.session_id,
            "objects_classified": len(objects),
            "settlement_queue_count": len(queue),
            "persisted_to_mongodb": persisted,
            "accepted_state_changed": False,
        }


    @app.get("/settlement-queue/{session_id}")
    def get_settlement_queue(session_id: str) -> Dict[str, Any]:
        data = _SESSION_CACHE.get(session_id)
        if not data:
            raise HTTPException(status_code=404, detail="session not found")
        return {"session_id": session_id, "queue": [q.to_dict() for q in data["queue"]]}


    @app.post("/settle")
    def settle(req: SettleRequest) -> Dict[str, Any]:
        data = _SESSION_CACHE.get(req.session_id)
        if not data:
            raise HTTPException(status_code=404, detail="session not found")
        objects, queue = apply_decisions(data["objects"], data["queue"], req.decisions, req.settled_by)
        data["objects"], data["queue"] = objects, queue
        persisted = False
        if req.persist_to_mongodb:
            try:
                adapter = _maybe_adapter(True)
                assert adapter is not None
                adapter.replace_settled_objects([o.to_dict() for o in objects])
                adapter.replace_settlement_queue([q.to_dict() for q in queue])
                persisted = True
            except Exception as exc:
                raise HTTPException(status_code=503, detail=f"MongoDB persistence blocked: {exc}") from exc
        return {
            "session_id": req.session_id,
            "decisions_applied": len(req.decisions),
            "persisted_to_mongodb": persisted,
            "accepted_state_changed": False,
            "note": "Objects are settled only inside candidate session scope until receipt validation passes.",
        }


    @app.post("/receipt/{session_id}")
    def issue_receipt(session_id: str, persist_to_mongodb: bool = False) -> Dict[str, Any]:
        data = _SESSION_CACHE.get(session_id)
        if not data:
            raise HTTPException(status_code=404, detail="session not found")
        receipt = issue_receipt_candidate(session_id, data["objects"], issued_by="fastapi_v0_8")
        data["receipts"].append(receipt)
        persisted = False
        if persist_to_mongodb:
            try:
                adapter = _maybe_adapter(True)
                assert adapter is not None
                adapter.insert_receipt(receipt.to_dict())
                persisted = True
            except Exception as exc:
                raise HTTPException(status_code=503, detail=f"MongoDB receipt persistence blocked: {exc}") from exc
        payload = receipt.to_dict()
        payload["persisted_to_mongodb"] = persisted
        return payload


    @app.get("/inheritance/{session_id}")
    def get_inheritance(session_id: str) -> Dict[str, Any]:
        data = _SESSION_CACHE.get(session_id)
        if not data:
            raise HTTPException(status_code=404, detail="session not found")
        receipt_ids = [r.receipt_id for r in data["receipts"]]
        return resolve_inheritance(session_id, data["objects"], receipt_ids).to_dict()


    @app.get("/capability-graph")
    def get_capability_graph() -> Dict[str, Any]:
        graph = load_capability_graph()
        return {
            "schema": graph.get("schema"),
            "state_claim": graph.get("state_claim"),
            "capability_count": len(graph.get("capabilities", [])),
            "route_rule_count": len(graph.get("route_rules", [])),
            "capabilities": graph.get("capabilities", []),
            "route_rules": graph.get("route_rules", []),
            "accepted_state_changed": False,
        }


    @app.post("/route")
    def route(req: RouteRequest) -> Dict[str, Any]:
        if not req.objective.strip():
            raise HTTPException(status_code=400, detail="objective is required")
        return route_objective(req.objective, session_id=req.session_id)


    @app.post("/query-governed-state")
    def query_governed_state(req: QueryRequest) -> Dict[str, Any]:
        data = _SESSION_CACHE.get(req.session_id)
        if not data:
            raise HTTPException(status_code=404, detail="session not found")
        bundle = resolve_inheritance(req.session_id, data["objects"], [r.receipt_id for r in data["receipts"]])
        latest_receipt = data["receipts"][-1] if data["receipts"] else None
        matches = []
        q = req.query.lower()
        for obj in bundle.objects:
            if q in obj["text"].lower() or any(token in obj["text"].lower() for token in q.split()):
                matches.append(obj)
        returned = matches[: req.limit]
        trace = build_mcp_visibility_trace(
            req.session_id,
            [obj["object_id"] for obj in returned],
            inherited_objects=returned,
            all_objects=[o.to_dict() for o in data["objects"]],
            receipt_ids=bundle.receipt_ids,
            receipt_proof_hash=latest_receipt.proof_hash if latest_receipt else None,
            query=req.query,
            limit=req.limit,
        )
        return {
            "session_id": req.session_id,
            "query": req.query,
            "matches": returned,
            "mcp_visibility_trace": trace,
            "non_claim": "Local endpoint simulates governed retrieval; judged build must show MongoDB MCP call trace.",
        }


    @app.post("/query-governed-state-live")
    def find_continuity_objects(req: LiveQueryRequest) -> Dict[str, Any]:
        """Read receipt-cleared continuity objects from live MongoDB.

        This endpoint exists for Cloud Run / Agent Builder wiring. It preserves
        the dAimon rule that live retrieval may consider broad session objects
        for exclusion reporting, but returns only objects that pass receipt and
        inheritance gates.
        """
        try:
            adapter = _maybe_adapter(True)
            assert adapter is not None
            inherited = adapter.find_inheritable_objects(req.session_id, req.limit)
            receipts = adapter.find_receipts_for_session(req.session_id, 10)
            all_limit = max(req.limit * 4, 25) if req.include_exclusion_report else req.limit
            all_objects = adapter.find_session_objects(req.session_id, all_limit)
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"MongoDB live query blocked: {exc}") from exc

        returned = _query_matches(inherited, req.query, req.limit)
        trace = build_mcp_visibility_trace(
            req.session_id,
            [str(obj.get("object_id")) for obj in returned if obj.get("object_id")],
            inherited_objects=returned,
            all_objects=all_objects,
            receipt_ids=_receipt_ids(receipts),
            receipt_proof_hash=_proof_hash(receipts),
            query=req.query,
            limit=req.limit,
        )
        return {
            "schema": "daimon.find_continuity_objects.live_response.v0_1",
            "tool_name": "find_continuity_objects",
            "session_id": req.session_id,
            "query": req.query,
            "matches": returned,
            "receipt_ids": _receipt_ids(receipts),
            "mcp_visibility_trace": trace,
            "governance_filter": {
                "inheritance_status": "INHERITABLE_AFTER_RECEIPT",
                "acceptance_status_allowlist": [
                    "settled_accept_sample",
                    "ACCEPTED",
                    "RECEIPT_CLEARED",
                    "receipt_cleared",
                ],
            },
            "state_boundary": "read_only_live_mongodb_adapter_query",
            "accepted_state_changed": False,
            "external_mutation_attempted": False,
        }


    @app.get("/live-vertical-slice-evidence/{session_id}")
    def live_vertical_slice_evidence(session_id: str, limit: int = 25) -> Dict[str, Any]:
        try:
            adapter = _maybe_adapter(True)
            assert adapter is not None
            ping = adapter.ping()
            inherited = adapter.find_inheritable_objects(session_id, limit)
            receipts = adapter.find_receipts_for_session(session_id, 10)
            all_objects = adapter.find_session_objects(session_id, max(limit * 2, 25))
        except Exception as exc:
            raise HTTPException(status_code=503, detail=f"MongoDB evidence query blocked: {exc}") from exc

        returned_ids = [str(obj.get("object_id")) for obj in inherited if obj.get("object_id")]
        trace = build_mcp_visibility_trace(
            session_id,
            returned_ids,
            inherited_objects=inherited,
            all_objects=all_objects,
            receipt_ids=_receipt_ids(receipts),
            receipt_proof_hash=_proof_hash(receipts),
            query="Cloud Run evidence read for receipt-cleared dAimon continuity.",
            limit=limit,
        )
        return {
            "schema": "daimon.cloud_run_live_vertical_slice_evidence.v0_1",
            "ok": True,
            "session_id": session_id,
            "mongodb": {
                "ok": ping.get("ok") is True,
                "database": ping.get("database"),
                "collections": ping.get("collections"),
            },
            "inheritable_count": len(inherited),
            "receipt_count": len(receipts),
            "returned_object_ids": returned_ids,
            "receipt_ids": _receipt_ids(receipts),
            "mcp_visibility_trace": trace,
            "accepted_state_changed": False,
            "external_mutation_attempted": False,
        }


    @app.post("/mcp-visibility-trace")
    def mcp_visibility_trace(req: TraceRequest) -> Dict[str, Any]:
        data = _SESSION_CACHE.get(req.session_id)
        if not data:
            raise HTTPException(status_code=404, detail="session not found")
        bundle = resolve_inheritance(req.session_id, data["objects"], [r.receipt_id for r in data["receipts"]])
        latest_receipt = data["receipts"][-1] if data["receipts"] else None
        return build_mcp_visibility_trace(
            req.session_id,
            bundle.inherited_object_ids,
            inherited_objects=bundle.objects,
            all_objects=[o.to_dict() for o in data["objects"]],
            receipt_ids=bundle.receipt_ids,
            receipt_proof_hash=latest_receipt.proof_hash if latest_receipt else None,
            query=req.query,
            limit=req.limit,
        )
