#!/usr/bin/env python3
"""Validate the v0.8 MongoDB adapter/tool-contract hardening without secrets."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "ion_kernel/mongodb_adapter.py",
    "ion_kernel/api.py",
    "ion_kernel/mcp_trace.py",
    "agent_builder/agent_tool_manifest.yaml",
    "agent_builder/openapi_tools_contract.json",
    "mcp/mongodb_atlas_schema_contract_v0_8.json",
    "mcp/mongodb_mcp_visibility_contract.json",
    "scripts/run_mcp_trace_harness.py",
    "scripts/run_gemini_handoff_demo.py",
    "scripts/run_live_vertical_slice.py",
    "scripts/validate_agent_builder_mcp_trace.py",
    "scripts/generate_demo_evidence_package.py",
    "scripts/deploy_cloud_run.py",
    "scripts/check_cloud_run_live.py",
    "scripts/validate_mcp_trace_harness.py",
    "ion_kernel/Dockerfile",
    ".gcloudignore",
    ".env.example",
]

errors = []
for rel in REQUIRED:
    if not (ROOT / rel).exists():
        errors.append(f"missing required file: {rel}")

for rel in ["ion_kernel/mongodb_adapter.py", "ion_kernel/api.py"]:
    try:
        ast.parse((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"python syntax error in {rel}: {exc}")

for rel in [
    "agent_builder/openapi_tools_contract.json",
    "mcp/mongodb_atlas_schema_contract_v0_8.json",
    "mcp/mongodb_mcp_visibility_contract.json",
]:
    try:
        json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"json parse error in {rel}: {exc}")

manifest_text = (ROOT / "agent_builder/agent_tool_manifest.yaml").read_text(encoding="utf-8")
for needle in [
    "find_continuity_objects",
    "query_governed_state_via_mongodb_mcp",
    "mcp_visibility_trace",
    "inheritance_status",
    "INHERITABLE_AFTER_RECEIPT",
    "MongoDB MCP Server",
]:
    if needle not in manifest_text:
        errors.append(f"tool manifest missing {needle}")

env_text = (ROOT / ".env.example").read_text(encoding="utf-8")
if "MONGODB_URI=" not in env_text or "ION_MONGODB_ENABLED=false" not in env_text:
    errors.append(".env.example must preserve fail-closed MongoDB defaults")

openapi = json.loads((ROOT / "agent_builder/openapi_tools_contract.json").read_text(encoding="utf-8"))
ops = []
for item in openapi["paths"].values():
    for method in item.values():
        if isinstance(method, dict) and method.get("operationId"):
            ops.append(method["operationId"])
for op in [
    "import_session_files",
    "settle_item",
    "issue_receipt",
    "get_inheritance",
    "find_continuity_objects",
    "query_governed_state",
    "mcp_visibility_trace",
    "live_vertical_slice_evidence",
]:
    if op not in ops:
        errors.append(f"OpenAPI contract missing operationId {op}")

mcp_contract = json.loads((ROOT / "mcp/mongodb_mcp_visibility_contract.json").read_text(encoding="utf-8"))
for field in [
    "accepted_only_query_shape",
    "mongodb_mcp_request_envelope",
    "returned_continuity_object_ids",
    "returned_object_citations",
    "exclusion_report",
]:
    if field not in mcp_contract.get("required_trace_fields", []):
        errors.append(f"MCP visibility contract missing required trace field {field}")

result = {
    "ok": not errors,
    "required_files_checked": len(REQUIRED),
    "openapi_operations": ops,
    "accepted_state_changed": False,
    "external_mutation_attempted": False,
    "errors": errors,
}
out = ROOT / "sample_outputs" / "mongodb_contract_validation.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
sys.exit(0 if not errors else 1)
