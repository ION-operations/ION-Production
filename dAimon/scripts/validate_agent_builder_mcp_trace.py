#!/usr/bin/env python3
"""Validate Agent Builder / MongoDB MCP trace evidence.

The repository already proves the local trace harness and the live MongoDB /
Gemini API handoff. This validator is the next proof gate: attach a real Agent
Builder trace export when available and verify it shows a read-only MongoDB MCP
retrieval of receipt-cleared objects.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRACE_PATH = ROOT / "sample_outputs" / "agent_builder_mcp_trace.json"
LEGACY_TRACE_PATH = ROOT / "sample_outputs" / "agent_builder_mcp_trace_raw.json"
OUTPUT_PATH = ROOT / "sample_outputs" / "agent_builder_mcp_trace_validation.json"
DASHBOARD_PATH = ROOT / "sample_outputs" / "agent_builder_mcp_dashboard_trace.json"
INHERITANCE_PATH = ROOT / "sample_outputs" / "live_vertical_slice_inheritance_bundle.json"
MCP_TRACE_PATH = ROOT / "sample_outputs" / "live_vertical_slice_mcp_trace.json"

OBJECT_ID_RE = re.compile(r"\bco_[a-f0-9]{10,16}\b")
RECEIPT_ID_RE = re.compile(r"\breceipt_[A-Za-z0-9_\-]+\b")
WRITE_OPERATION_RE = re.compile(
    r"\b(insert|update|delete|replace|drop|createCollection|bulkWrite|findOneAndUpdate)\b",
    re.IGNORECASE,
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def flatten(value: Any) -> Iterable[str]:
    if isinstance(value, Mapping):
        for key, item in value.items():
            yield str(key)
            yield from flatten(item)
    elif isinstance(value, list):
        for item in value:
            yield from flatten(item)
    else:
        yield str(value)


def text_blob(value: Any) -> str:
    return "\n".join(flatten(value))


def expected_inherited_ids() -> set[str]:
    ids: set[str] = set()
    if INHERITANCE_PATH.exists():
        bundle = load_json(INHERITANCE_PATH)
        ids.update(str(item) for item in bundle.get("inherited_object_ids", []))
    if MCP_TRACE_PATH.exists():
        trace = load_json(MCP_TRACE_PATH)
        ids.update(str(item) for item in trace.get("returned_continuity_object_ids", []))
    return ids


def expected_receipt_ids() -> set[str]:
    ids: set[str] = set()
    if INHERITANCE_PATH.exists():
        bundle = load_json(INHERITANCE_PATH)
        ids.update(str(item) for item in bundle.get("receipt_ids", []))
    if MCP_TRACE_PATH.exists():
        trace = load_json(MCP_TRACE_PATH)
        for citation in trace.get("returned_object_citations", []):
            ids.update(str(item) for item in citation.get("receipt_ids", []))
    return ids


def exclusion_report_ids(value: Any) -> set[str]:
    ids: set[str] = set()
    if isinstance(value, Mapping):
        report = value.get("exclusion_report")
        if isinstance(report, Mapping):
            by_reason = report.get("excluded_object_ids_by_reason", {})
            if isinstance(by_reason, Mapping):
                for reason_ids in by_reason.values():
                    if isinstance(reason_ids, list):
                        ids.update(str(item) for item in reason_ids)
        for item in value.values():
            ids.update(exclusion_report_ids(item))
    elif isinstance(value, list):
        for item in value:
            ids.update(exclusion_report_ids(item))
    return ids


def trace_kind(trace_path: Path, trace: Mapping[str, Any]) -> str:
    schema = str(trace.get("schema", ""))
    if trace_path.name == "live_vertical_slice_mcp_trace.json" or schema == "ion.mcp_visibility_trace.v0_2":
        return "local_or_api_harness"
    return "agent_builder_trace_export"


def validate_trace(trace_path: Path, *, require_live_trace: bool = False) -> tuple[dict[str, Any], int]:
    if trace_path == DEFAULT_TRACE_PATH and not trace_path.exists() and LEGACY_TRACE_PATH.exists():
        trace_path = LEGACY_TRACE_PATH

    expected_ids = expected_inherited_ids()
    expected_receipts = expected_receipt_ids()

    if not trace_path.exists():
        missing_message = "Attach sample_outputs/agent_builder_mcp_trace.json or pass --trace-path."
        result = {
            "schema": "daimon.agent_builder_mcp_trace_validation.v0_1",
            "ok": not require_live_trace,
            "proof_status": "agent_builder_trace_missing",
            "trace_path": str(trace_path.relative_to(ROOT)),
            "live_mcp_execution_proven": False,
            "local_harness_available": MCP_TRACE_PATH.exists(),
            "expected_inherited_ids": sorted(expected_ids),
            "expected_receipt_ids": sorted(expected_receipts),
            "errors": [missing_message] if require_live_trace else [],
            "warnings": [] if require_live_trace else [missing_message],
            "blockers": [
            "Need Agent Builder trace export or screenshot-transcribed JSON showing MongoDB MCP tool use.",
                "Need returned object IDs and receipt citations visible in that trace.",
            ],
            "accepted_state_changed": False,
            "external_mutation_attempted": False,
        }
        return result, 1 if require_live_trace else 0

    trace = load_json(trace_path)
    blob = text_blob(trace)
    object_ids = set(OBJECT_ID_RE.findall(blob))
    receipt_ids = set(RECEIPT_ID_RE.findall(blob))
    errors: list[str] = []
    warnings: list[str] = []
    kind = trace_kind(trace_path, trace)

    has_mongodb_mcp = any(
        needle in blob.lower()
        for needle in [
            "mongodb mcp",
            "mongodb.aggregate",
            "mongodb.find",
            "mongodb.vector",
            "mongodb atlas",
            "find_continuity_objects",
        ]
    )
    if not has_mongodb_mcp:
        errors.append("trace does not show MongoDB MCP / MongoDB tool usage")

    has_inheritance_gate = "INHERITABLE_AFTER_RECEIPT" in blob
    if not has_inheritance_gate:
        errors.append("trace does not show inheritance_status == INHERITABLE_AFTER_RECEIPT")

    has_acceptance_gate = any(
        status in blob
        for status in ["settled_accept_sample", "ACCEPTED", "RECEIPT_CLEARED", "receipt_cleared"]
    )
    if not has_acceptance_gate:
        errors.append("trace does not show an acceptance_status allowlist or equivalent accepted-state gate")

    if expected_ids:
        excluded_ids = exclusion_report_ids(trace)
        missing_ids = sorted(expected_ids.difference(object_ids))
        unexpected_ids = sorted(object_ids.difference(expected_ids).difference(excluded_ids))
        if missing_ids:
            errors.append(f"trace is missing expected inherited object IDs: {missing_ids}")
        if unexpected_ids:
            warnings.append(f"trace includes object IDs outside current inheritance bundle: {unexpected_ids}")
    else:
        missing_ids = []
        unexpected_ids = sorted(object_ids)
        warnings.append("no expected inheritance bundle IDs available for comparison")

    if expected_receipts:
        missing_receipts = sorted(expected_receipts.difference(receipt_ids))
        if missing_receipts:
            errors.append(f"trace is missing expected receipt IDs: {missing_receipts}")
    else:
        missing_receipts = []
        warnings.append("no expected receipt IDs available for comparison")

    write_matches = sorted(set(WRITE_OPERATION_RE.findall(blob)))
    if write_matches:
        warnings.append(f"trace text contains possible write operation words; verify read-only context: {write_matches}")

    live_mcp_execution_proven = kind == "agent_builder_trace_export" and not errors
    if require_live_trace and kind != "agent_builder_trace_export":
        errors.append("trace is a local/API harness artifact, not a live Agent Builder trace export")

    result = {
        "schema": "daimon.agent_builder_mcp_trace_validation.v0_1",
        "ok": not errors,
        "proof_status": "proven_live_agent_builder_mcp" if live_mcp_execution_proven else "local_harness_or_pending_live_trace",
        "trace_path": str(trace_path.relative_to(ROOT)),
        "trace_kind": kind,
        "live_mcp_execution_proven": live_mcp_execution_proven,
        "mongodb_mcp_tool_observed": has_mongodb_mcp,
        "inheritance_gate_observed": has_inheritance_gate,
        "acceptance_gate_observed": has_acceptance_gate,
        "expected_inherited_ids": sorted(expected_ids),
        "observed_object_ids": sorted(object_ids),
        "observed_excluded_object_ids": sorted(exclusion_report_ids(trace)),
        "missing_expected_object_ids": missing_ids,
        "unexpected_object_ids": unexpected_ids,
        "expected_receipt_ids": sorted(expected_receipts),
        "observed_receipt_ids": sorted(receipt_ids),
        "missing_expected_receipt_ids": missing_receipts,
        "read_only_review": {
            "possible_write_terms": write_matches,
            "state_boundary": "trace validation is read-only and does not mutate accepted state",
        },
        "errors": errors,
        "warnings": warnings,
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
    }
    return result, 0 if not errors else 1


def dashboard_rows(result: Mapping[str, Any]) -> dict[str, Any]:
    rows = [
        {
            "phase": "agent_builder_trace",
            "status": result.get("proof_status"),
            "evidence": result.get("trace_path"),
            "detail": "Live Agent Builder MCP proven" if result.get("live_mcp_execution_proven") else "Pending live Agent Builder MCP trace export.",
        },
        {
            "phase": "mongodb_mcp_tool",
            "status": "observed" if result.get("mongodb_mcp_tool_observed") else "missing",
            "evidence": "mongodb_mcp_tool_observed",
            "detail": "Trace must show MongoDB MCP aggregate/find/vector-search tool usage.",
        },
        {
            "phase": "accepted_only_filter",
            "status": "observed" if result.get("inheritance_gate_observed") and result.get("acceptance_gate_observed") else "missing",
            "evidence": "inheritance_gate_observed + acceptance_gate_observed",
            "detail": "Trace must preserve inheritance_status and acceptance_status gates.",
        },
        {
            "phase": "receipt_citations",
            "status": "observed" if result.get("observed_receipt_ids") else "missing",
            "evidence": "observed_receipt_ids",
            "detail": ", ".join(result.get("observed_receipt_ids", [])),
        },
    ]
    return {
        "schema": "daimon.agent_builder_mcp_dashboard_trace.v0_1",
        "trace_rows": rows,
        "live_mcp_execution_proven": bool(result.get("live_mcp_execution_proven")),
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-path", default=str(DEFAULT_TRACE_PATH))
    parser.add_argument("--require-live-trace", action="store_true")
    args = parser.parse_args()

    trace_path = Path(args.trace_path)
    if not trace_path.is_absolute():
        trace_path = ROOT / trace_path
    result, code = validate_trace(trace_path, require_live_trace=args.require_live_trace)
    write_json(OUTPUT_PATH, result)
    write_json(DASHBOARD_PATH, dashboard_rows(result))
    print(json.dumps(result, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
