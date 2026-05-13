"""MCP visibility trace helpers for the judged build.

The contest demo needs to show that MongoDB MCP is not decorative. This module
emits a local trace with the same evidence fields the real Agent Builder / MCP
integration should fill: query filter, MCP request envelope, returned object
IDs, receipt citations, and excluded non-inheritable objects.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Sequence
from ion_kernel.schemas import utc_now

INHERITABLE_STATUS = "INHERITABLE_AFTER_RECEIPT"
ACCEPTED_STATUS_ALLOWLIST = [
    "settled_accept_sample",
    "ACCEPTED",
    "RECEIPT_CLEARED",
    "receipt_cleared",
]
DEFAULT_COLLECTION = "continuity_objects"
DEFAULT_DATABASE = "ion_continuity_bridge"


def _as_dicts(values: Iterable[Any] | None) -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []
    for value in values or []:
        if hasattr(value, "to_dict"):
            docs.append(value.to_dict())
        elif isinstance(value, Mapping):
            docs.append(dict(value))
    return docs


def _object_id(doc: Mapping[str, Any]) -> str:
    return str(doc.get("object_id", ""))


def build_accepted_only_query_shape(
    session_id: str,
    *,
    query: str = "retrieve governed continuity for next Gemini session",
    limit: int = 25,
) -> Dict[str, Any]:
    """Return the fail-closed query shape the MongoDB MCP call must preserve."""
    return {
        "schema": "ion.mongodb_mcp.accepted_only_query.v0_2",
        "query": query,
        "limit": limit,
        "filter": {
            "session_id": session_id,
            "inheritance_status": INHERITABLE_STATUS,
            "acceptance_status": {"$in": ACCEPTED_STATUS_ALLOWLIST},
        },
        "projection": {
            "_id": 0,
            "object_id": 1,
            "session_id": 1,
            "source_file": 1,
            "inferred_role": 1,
            "authority_class": 1,
            "authority_score": 1,
            "acceptance_status": 1,
            "inheritance_status": 1,
            "proof_status": 1,
            "text_hash": 1,
            "settled_at": 1,
            "settled_by": 1,
        },
        "forbidden_statuses": [
            "NOT_INHERITABLE_REJECTED",
            "NOT_INHERITABLE_DEFERRED",
            "NOT_INHERITABLE_PENDING_PROOF",
            "NOT_INHERITABLE_AS_STATE_WITHOUT_SETTLEMENT",
        ],
    }


def build_mongodb_mcp_request_envelope(
    session_id: str,
    query_shape: Mapping[str, Any],
    *,
    database: str = DEFAULT_DATABASE,
    collection: str = DEFAULT_COLLECTION,
) -> Dict[str, Any]:
    """Build a representative MongoDB MCP aggregate envelope for trace review."""
    query_filter = dict(query_shape.get("filter", {}))
    projection = dict(query_shape.get("projection", {}))
    limit = int(query_shape.get("limit", 25))
    return {
        "schema": "ion.mongodb_mcp.request_envelope.v0_2",
        "transport": "MongoDB MCP Server",
        "tool_name": "mongodb.aggregate",
        "operation_name": "aggregate",
        "database": database,
        "collection": collection,
        "read_only": True,
        "arguments": {
            "pipeline": [
                {"$match": query_filter},
                {"$project": projection},
                {"$limit": limit},
            ]
        },
        "state_boundary": {
            "accepted_state_changed": False,
            "external_mutation_attempted": False,
            "writes_allowed": False,
            "reason": "MCP visibility is read-only evidence; ION settlement and receipt law decide inheritance.",
        },
        "trace_expectation": "A live Agent Builder run should show this tool name, filter, returned IDs, and receipt citations.",
        "session_id": session_id,
    }


def build_returned_object_citations(
    returned_objects: Sequence[Mapping[str, Any]],
    receipt_ids: Sequence[str] | None,
    receipt_proof_hash: str | None,
) -> List[Dict[str, Any]]:
    citations: List[Dict[str, Any]] = []
    for obj in returned_objects:
        citations.append({
            "object_id": _object_id(obj),
            "receipt_ids": list(receipt_ids or []),
            "receipt_proof_hash": receipt_proof_hash,
            "source_file": obj.get("source_file"),
            "source_authority": {
                "authority_class": obj.get("authority_class"),
                "authority_score": obj.get("authority_score"),
            },
            "proof_status": obj.get("proof_status"),
            "text_hash": obj.get("text_hash"),
            "inheritance_status": obj.get("inheritance_status"),
            "acceptance_status": obj.get("acceptance_status"),
        })
    return citations


def build_exclusion_report(
    all_objects: Sequence[Mapping[str, Any]],
    returned_ids: Sequence[str],
) -> Dict[str, Any]:
    returned = set(returned_ids)
    buckets: Dict[str, List[str]] = {
        "rejected": [],
        "deferred": [],
        "proof_debt": [],
        "witness_only": [],
        "other_not_inherited": [],
    }
    for obj in all_objects:
        obj_id = _object_id(obj)
        if obj_id in returned:
            continue
        status = str(obj.get("inheritance_status", ""))
        proof_status = str(obj.get("proof_status", ""))
        if "REJECTED" in status:
            buckets["rejected"].append(obj_id)
        elif "DEFERRED" in status:
            buckets["deferred"].append(obj_id)
        elif "PENDING_PROOF" in status or "PROOF_DEBT" in proof_status:
            buckets["proof_debt"].append(obj_id)
        elif "WITHOUT_SETTLEMENT" in status:
            buckets["witness_only"].append(obj_id)
        else:
            buckets["other_not_inherited"].append(obj_id)
    excluded_ids = sorted({item for ids in buckets.values() for item in ids})
    overlap = sorted(set(excluded_ids).intersection(returned))
    return {
        "schema": "ion.mongodb_mcp.exclusion_report.v0_2",
        "excluded_object_ids_by_reason": buckets,
        "excluded_count": len(excluded_ids),
        "returned_excluded_overlap": overlap,
        "exclusion_note": "Rejected, deferred, proof-debt, and witness-only objects were excluded from returned governed context.",
    }


def build_dashboard_trace_rows(trace: Mapping[str, Any]) -> List[Dict[str, Any]]:
    returned_ids = trace.get("returned_continuity_object_ids", [])
    exclusion = trace.get("exclusion_report", {})
    query_shape = trace.get("accepted_only_query_shape", {})
    envelope = trace.get("mongodb_mcp_request_envelope", {})
    return [
        {
            "phase": "inheritance_bundle",
            "status": "observed",
            "evidence": "sample_outputs/inheritance_bundle.json",
            "detail": f"{len(returned_ids)} receipt-cleared object IDs selected for retrieval.",
        },
        {
            "phase": "accepted_only_query_shape",
            "status": "gated",
            "evidence": "accepted_only_query_shape.filter",
            "detail": str(query_shape.get("filter", {})),
        },
        {
            "phase": "mongodb_mcp_request_envelope",
            "status": "read_only",
            "evidence": "mongodb_mcp_request_envelope.arguments.pipeline",
            "detail": f"{envelope.get('tool_name')} on {envelope.get('database')}.{envelope.get('collection')}",
        },
        {
            "phase": "returned_object_ids",
            "status": "receipt_cited",
            "evidence": "returned_object_citations",
            "detail": ", ".join(returned_ids),
        },
        {
            "phase": "excluded_non_inheritable",
            "status": "excluded",
            "evidence": "exclusion_report",
            "detail": f"{exclusion.get('excluded_count', 0)} non-inheritable objects excluded; overlap={exclusion.get('returned_excluded_overlap', [])}",
        },
    ]


def build_mcp_visibility_trace(
    session_id: str,
    inherited_ids: List[str],
    *,
    inherited_objects: Sequence[Mapping[str, Any]] | None = None,
    all_objects: Sequence[Mapping[str, Any]] | None = None,
    receipt_ids: Sequence[str] | None = None,
    receipt_proof_hash: str | None = None,
    query: str = "retrieve governed continuity for next Gemini session",
    limit: int = 25,
    database: str = DEFAULT_DATABASE,
    collection: str = DEFAULT_COLLECTION,
) -> Dict[str, Any]:
    returned_objects = _as_dicts(inherited_objects)
    if not returned_objects:
        returned_objects = [{"object_id": obj_id, "inheritance_status": INHERITABLE_STATUS} for obj_id in inherited_ids]
    returned_ids = [_object_id(obj) for obj in returned_objects if _object_id(obj)]
    all_docs = _as_dicts(all_objects)
    query_shape = build_accepted_only_query_shape(session_id, query=query, limit=limit)
    envelope = build_mongodb_mcp_request_envelope(
        session_id,
        query_shape,
        database=database,
        collection=collection,
    )
    citations = build_returned_object_citations(returned_objects, receipt_ids, receipt_proof_hash)
    exclusion_report = build_exclusion_report(all_docs, returned_ids) if all_docs else {
        "schema": "ion.mongodb_mcp.exclusion_report.v0_2",
        "excluded_object_ids_by_reason": {},
        "excluded_count": 0,
        "returned_excluded_overlap": [],
        "exclusion_note": "No full object corpus was supplied to local trace builder.",
    }
    trace: Dict[str, Any] = {
        "schema": "ion.mcp_visibility_trace.v0_2",
        "session_id": session_id,
        "generated_at": utc_now(),
        "partner_track": "MongoDB",
        "required_mcp_server": "MongoDB MCP Server",
        "intended_agent_path": [
            "Gemini carrier receives user question",
            "Agent Builder calls MongoDB MCP tool for governed-state query",
            "MongoDB query filters acceptance_status / inheritance_status",
            "Gemini receives only receipt-cleared continuity objects",
            "Gemini answer cites receipt IDs and excludes rejected/deferred/proof-debt objects",
        ],
        "accepted_only_query_shape": query_shape,
        "mongodb_mcp_request_envelope": envelope,
        "returned_continuity_object_ids": returned_ids,
        "sample_inherited_ids": returned_ids,
        "returned_object_citations": citations,
        "exclusion_report": exclusion_report,
        "answer_citation_trace": {
            "mode": "local_sample_answer_trace",
            "answer_must_cite": [
                {
                    "object_id": c["object_id"],
                    "receipt_ids": c["receipt_ids"],
                    "receipt_proof_hash": c["receipt_proof_hash"],
                }
                for c in citations
            ],
            "answer_must_not_claim": [
                "No rejected object is inherited as state.",
                "No deferred object is inherited as state.",
                "No proof-debt object is inherited as settled fact.",
                "No live MongoDB MCP call is proven unless a live Agent Builder trace is attached.",
            ],
        },
        "minimum_demo_evidence": [
            "MCP server config visible in repo",
            "Agent tool definition named query_governed_state_via_mongodb_mcp",
            "Trace screenshot or log line from Agent Builder showing MCP call",
            "Returned object IDs match inheritance bundle",
            "Receipt IDs or proof hash are attached to every returned object",
        ],
        "validation_expectations": {
            "returned_ids_subset_of_inheritance_bundle": True,
            "returned_excluded_overlap_count": len(exclusion_report.get("returned_excluded_overlap", [])),
            "receipt_citation_count": len(citations),
            "accepted_state_changed": False,
            "external_mutation_attempted": False,
        },
        "non_claim": "This local trace is a harness artifact; the judged build must attach a real Agent Builder/MongoDB MCP call trace before claiming live MCP execution.",
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
    }
    trace["dashboard_trace_rows"] = build_dashboard_trace_rows(trace)
    return trace
