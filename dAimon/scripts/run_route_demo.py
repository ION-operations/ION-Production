#!/usr/bin/env python3
"""ION Route Endpoint Demo v1.0.

Runs the same routing logic that backs the /route API endpoint without calling
Google Cloud, Gemini, MongoDB Atlas, MCP, or any external service.
"""
from __future__ import annotations

import json
import csv
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ion_kernel.capability_router import route_many, route_objective, load_capability_graph
OUT_DIR = ROOT / "sample_outputs"
SUMMARY_PATH = OUT_DIR / "capability_route_demo_summary.json"
TRACE_JSON_PATH = OUT_DIR / "capability_graph_dashboard_trace.json"
TRACE_CSV_PATH = OUT_DIR / "capability_graph_dashboard_trace.csv"


OBJECTIVES = [
    "Which current docs support this contest claim and what evidence can we cite?",
    "Accept these candidate decisions into future context for the next session.",
    "What may the next Gemini session inherit from settled continuity objects?",
    "Push this generated patch to production immediately.",
    "Make a project handoff summary for the operator without mutating state.",
    "Show how MongoDB MCP participates in governed retrieval.",
]


def flatten_trace(routes: list[dict]) -> list[dict]:
    rows = []
    for route in routes:
        for step in route.get("trace", []):
            rows.append({
                "route_id": route.get("route_id"),
                "objective": route.get("objective"),
                "route_status": route.get("route_status"),
                "domain": route.get("domain"),
                "agent_role": route.get("agent_role"),
                "authority_ceiling": route.get("authority_ceiling"),
                "trace_step": step.get("step"),
                "trace_status": step.get("status"),
                "selected_rule": step.get("selected_rule", route.get("route_rule", "")),
                "accepted_state_changed": route.get("accepted_state_changed", False),
            })
    return rows


def main() -> int:
    graph = load_capability_graph()
    batch = route_many(OBJECTIVES, session_id="demo_route_session_v1_0", graph=graph)
    routes = batch["routes"]
    dashboard_trace = {
        "schema": "ion.capability_graph.dashboard_trace.v1_0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "graph_schema": graph.get("schema"),
        "capability_count": len(graph.get("capabilities", [])),
        "route_rule_count": len(graph.get("route_rules", [])),
        "routes": routes,
        "trace_rows": flatten_trace(routes),
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
        "non_claims": [
            "No cloud, Gemini, MongoDB Atlas, or MCP calls were made in this local demo.",
            "The /route endpoint returns candidate route plans only.",
            "The dashboard trace is evidence of route reasoning structure, not accepted state."
        ],
    }
    OUT_DIR.mkdir(exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(batch, indent=2))
    TRACE_JSON_PATH.write_text(json.dumps(dashboard_trace, indent=2))
    with TRACE_CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "route_id", "objective", "route_status", "domain", "agent_role",
            "authority_ceiling", "trace_step", "trace_status", "selected_rule",
            "accepted_state_changed"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dashboard_trace["trace_rows"])
    print(json.dumps({
        "schema": "ion.route_demo.result.v1_0",
        "routes": batch["route_counts"],
        "capability_count": dashboard_trace["capability_count"],
        "route_rule_count": dashboard_trace["route_rule_count"],
        "trace_rows": len(dashboard_trace["trace_rows"]),
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
        "summary_path": str(SUMMARY_PATH.relative_to(ROOT)),
        "dashboard_trace_path": str(TRACE_JSON_PATH.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
