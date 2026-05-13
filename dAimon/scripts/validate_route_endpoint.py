#!/usr/bin/env python3
"""Validate v1.0 route endpoint and dashboard trace assets."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

REQUIRED = [
    "ion_kernel/capability_router.py",
    "ion_kernel/api.py",
    "scripts/run_route_demo.py",
    "capability_graph/capability_graph_seed.json",
    "sample_outputs/capability_route_demo_summary.json",
    "sample_outputs/capability_graph_dashboard_trace.json",
    "sample_outputs/capability_graph_dashboard_trace.csv",
    "agent_builder/openapi_tools_contract.json",
    "dashboard/index.html",
    "dashboard/styles.css",
]

def main() -> int:
    errors = []
    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            errors.append(f"missing {rel}")

    for rel in ["ion_kernel/capability_router.py", "ion_kernel/api.py", "scripts/run_route_demo.py"]:
        try:
            ast.parse((ROOT / rel).read_text())
        except Exception as exc:
            errors.append(f"python parse failed {rel}: {exc}")

    graph = json.loads((ROOT / "capability_graph/capability_graph_seed.json").read_text())
    if len(graph.get("capabilities", [])) < 10:
        errors.append("capability graph should have at least 10 seed capabilities")
    if not any(rule.get("rule_id") == "route_transfer_context" for rule in graph.get("route_rules", [])):
        errors.append("route_transfer_context missing")

    summary = json.loads((ROOT / "sample_outputs/capability_route_demo_summary.json").read_text())
    trace = json.loads((ROOT / "sample_outputs/capability_graph_dashboard_trace.json").read_text())
    if summary.get("accepted_state_changed") is not False:
        errors.append("summary accepted_state_changed must be false")
    if trace.get("accepted_state_changed") is not False:
        errors.append("trace accepted_state_changed must be false")
    if len(trace.get("routes", [])) < 5:
        errors.append("expected at least 5 sample routes")

    contract = json.loads((ROOT / "agent_builder/openapi_tools_contract.json").read_text())
    paths = contract.get("paths", {})
    if "/route" not in paths:
        errors.append("/route missing from OpenAPI contract")
    if "/capability-graph" not in paths:
        errors.append("/capability-graph missing from OpenAPI contract")

    html = (ROOT / "dashboard/index.html").read_text().lower()
    if "capability_graph_dashboard_trace.json" not in html:
        errors.append("dashboard does not reference route trace JSON")

    result = {
        "ok": not errors,
        "errors": errors,
        "required_files_checked": len(REQUIRED),
        "capability_count": len(graph.get("capabilities", [])),
        "route_rule_count": len(graph.get("route_rules", [])),
        "sample_routes": len(trace.get("routes", [])),
        "trace_rows": len(trace.get("trace_rows", [])),
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
    }
    print(json.dumps(result, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
