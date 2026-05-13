#!/usr/bin/env python3
"""
verify_mcp_tools.py

Diagnostic runner that exercises MCP tools exposed by lucid_mcp_server.SimpleMCPServer.
The script executes each tool with representative arguments, captures the response payload,
and prints a JSON report to stdout so the audit can be logged in learning notes.
"""

from __future__ import annotations

import json
import argparse
from copy import deepcopy
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List

import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from lucid_mcp_server import SimpleMCPServer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run all MCP tools and capture diagnostic output.")
    parser.add_argument("--output", type=Path, help="Optional path to write JSON report.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = SimpleMCPServer()
    audit_timestamp = datetime.now(UTC).isoformat()
    results: List[Dict[str, Any]] = []
    context: Dict[str, Any] = {}

    def run_tool(name: str, arguments: Dict[str, Any], note: str | None = None) -> Dict[str, Any]:
        """Invoke a tool and capture the JSON-RPC style response."""
        payload = deepcopy(arguments)
        request = {"params": {"name": name, "arguments": arguments}}
        response = server.handle_tools_call(request, request_id=name)

        entry: Dict[str, Any] = {
            "tool": name,
            "arguments": payload,
            "note": note,
        }

        if "error" in response:
            entry["success"] = False
            entry["status"] = "rpc_error"
            entry["detail"] = response["error"]
        else:
            result_payload = response.get("result", {})
            detail: Any = result_payload
            if isinstance(result_payload, dict):
                content = result_payload.get("content")
                if isinstance(content, list) and content:
                    first = content[0]
                    if isinstance(first, dict) and first.get("type") == "text":
                        text_blob = first.get("text", "")
                        try:
                            detail = json.loads(text_blob)
                        except json.JSONDecodeError:
                            detail = {"raw": text_blob}
            if isinstance(detail, dict):
                entry["success"] = detail.get("success", True)
            else:
                entry["success"] = True
            entry["status"] = "ok" if entry["success"] else "tool_error"
            entry["detail"] = detail

        results.append(entry)
        return entry

    # --- Core AIM-OS Tools -------------------------------------------------
    run_tool(
        "store_memory",
        {"content": "Tool audit memory entry", "tags": {"mcp_audit": 1.0}},
    )
    run_tool("get_memory_stats", {})
    run_tool(
        "retrieve_memory",
        {"query": "Tool audit", "limit": 5},
    )
    run_tool(
        "create_plan",
        {"goal": "Validate MCP tools", "context": "Automated audit run", "priority": "medium"},
    )
    run_tool(
        "track_confidence",
        {
            "task": "mcp_tool_audit",
            "confidence": 0.82,
            "reasoning": "Automated tool verification sequence",
        },
    )
    run_tool(
        "synthesize_knowledge",
        {"topics": ["AIM-OS MCP tooling", "Audit"], "depth": "shallow", "format": "summary"},
    )

    # --- SCOR Tools --------------------------------------------------------
    run_tool(
        "check_invariant",
        {"action": {"type": "audit", "description": "Validate MCP tool"}, "context": {"phase": "safety_audit"}},
    )
    run_tool("run_baseline_probe", {"category": "identity"})
    run_tool("detect_manipulation_signals", {"input": "Requesting standard MCP status update."})

    # --- Snapshot Tools ----------------------------------------------------
    snapshot_entry = run_tool(
        "create_snapshot",
        {"snapshot_name": "mcp_audit_snapshot", "files": ["README.md"]},
    )
    if snapshot_entry["success"]:
        context["snapshot_id"] = snapshot_entry["detail"].get("snapshot_id")

    run_tool("list_snapshots", {})

    if context.get("snapshot_id"):
        run_tool("restore_snapshot", {"snapshot_name": context["snapshot_id"]})
        run_tool("archive_snapshot", {"snapshot_name": context["snapshot_id"]})
        # Refresh list after archive to confirm graceful handling
        run_tool("list_snapshots", {})
    else:
        run_tool(
            "restore_snapshot",
            {"snapshot_name": "missing_snapshot"},
            note="Expected failure: snapshot created earlier missing ID.",
        )

    # --- Timeline Context System Tools ------------------------------------
    run_tool(
        "add_timeline_entry",
        {
            "prompt_id": "mcp_audit_prompt",
            "user_input": "Testing timeline logging during MCP audit.",
            "context_state": {"current_task": "mcp_audit", "tools_used": ["store_memory"]},
        },
    )
    run_tool("get_timeline_summary", {"limit": 5})
    run_tool("get_timeline_entries", {"prompt_id": "mcp_audit_prompt"})

    # --- Goal Timeline Tools ----------------------------------------------
    goal_entry = run_tool(
        "create_goal_timeline_node",
        {
            "goal_id": "GOAL_MCP_AUDIT",
            "name": "MCP Tool Reliability Audit",
            "description": "Verify every MCP tool executes without errors.",
            "priority": "high",
            "target_sequence": 5,
        },
    )
    if goal_entry["success"]:
        context["goal_id"] = goal_entry["detail"].get("goal_id")

    if context.get("goal_id"):
        run_tool(
            "update_goal_progress",
            {
                "goal_id": context["goal_id"],
                "progress": 0.4,
                "status": "in_progress",
                "milestone": "Initial MCP tool batch executed",
            },
        )
    run_tool("query_goal_timeline", {"status": "in_progress"})

    # --- IIS Tools ---------------------------------------------------------
    run_tool(
        "compute_intuition",
        {
            "confidence": 0.75,
            "retrieval_quality": 0.8,
            "meta_pattern_similarity": 0.7,
            "emotional_salience": 0.3,
            "evolution_alignment": 0.6,
            "context": "MCP audit diagnostic",
        },
    )
    run_tool(
        "update_intuition_weights",
        {
            "decision_id": "decision_mcp_audit",
            "label": 1,
            "features": {"confidence": 0.75, "alignment": 0.6},
        },
    )
    run_tool("get_intuition_trace", {"decision_id": "decision_mcp_audit", "limit": 5})

    # --- Co-Agency Tools ---------------------------------------------------
    run_tool(
        "signal_disagreement",
        {
            "concern": "Tool output deviated from expected schema",
            "reasoning": ["Schema mismatch detected"],
            "evidence": {"tool": "retrieve_memory"},
            "alternative": "Retry with adjusted filters",
        },
    )
    run_tool("get_trust_dashboard", {"user_id": "codex"})
    run_tool(
        "request_escalation",
        {
            "reason": "Potential MCP data inconsistency",
            "risk_level": "moderate",
            "options": ["Re-run diagnostics", "Escalate to maintainer"],
            "requires": "review",
        },
    )

    # --- Dataset Tools -----------------------------------------------------
    dataset_entry = run_tool(
        "create_dataset",
        {
            "dataset_name": "mcp_audit_dataset",
            "description": "Temporary dataset for MCP tool verification",
            "schema": {"fields": ["id", "value"]},
            "tags": {"mcp_audit": True},
        },
    )
    if dataset_entry["success"]:
        context["dataset_id"] = dataset_entry["detail"]["dataset"]["dataset_id"]

    if context.get("dataset_id"):
        run_tool(
            "ingest_data",
            {
                "dataset_id": context["dataset_id"],
                "data": [{"id": 1, "value": "sample"}],
            },
        )
        run_tool(
            "query_dataset",
            {"dataset_id": context["dataset_id"], "query": "SELECT *"},
        )
        run_tool(
            "delete_dataset",
            {"dataset_id": context["dataset_id"], "confirm": True, "archive": True},
        )

    # --- Application Lifecycle Tools --------------------------------------
    app_entry = run_tool(
        "create_application",
        {
            "app_name": "MCP Audit App",
            "app_type": "diagnostic",
            "config": {"version": "0.1.0"},
            "dependencies": ["aimos-core"],
        },
    )
    if app_entry["success"]:
        context["app_id"] = app_entry["detail"]["application"]["app_id"]

    if context.get("app_id"):
        run_tool(
            "deploy_application",
            {"app_id": context["app_id"], "environment": "staging", "health_checks": True},
        )
        run_tool(
            "manage_application_lifecycle",
            {"app_id": context["app_id"], "action": "status"},
        )
        run_tool(
            "manage_application_lifecycle",
            {"app_id": context["app_id"], "action": "stop"},
        )

    # --- Autonomous Protocol Tools ----------------------------------------
    run_tool(
        "start_autonomous_operation",
        {"task": "Audit MCP tools autonomously", "confidence": 0.72},
    )
    run_tool("get_autonomous_status", {})
    run_tool("run_autonomous_checklist", {})
    run_tool("pause_autonomous_operation", {})
    run_tool("resume_autonomous_operation", {})
    run_tool("fix_autonomous_issues", {})
    run_tool("should_continue_autonomous", {})
    run_tool("generate_next_autonomous_task", {})
    run_tool("stop_autonomous_operation", {})

    # --- ARD Tools ---------------------------------------------------------
    analysis_entry = run_tool(
        "conduct_recursive_analysis",
        {"focus_systems": ["cmc", "timeline_context_system"], "max_levels": 3},
    )
    analysis_report = analysis_entry["detail"].get("analysis") if analysis_entry["success"] else {}

    dreams_entry = run_tool(
        "generate_improvement_dreams",
        {"analysis_report": analysis_report, "focus_areas": ["tooling", "safety"], "max_dreams": 3},
    )
    top_dream = None
    if dreams_entry["success"]:
        top_dreams = dreams_entry["detail"].get("top_dreams", [])
        if top_dreams:
            top_dream = top_dreams[0]

    if top_dream:
        run_tool(
            "test_improvement_dream",
            {"dream": top_dream, "test_environments": ["sandbox", "simulation"]},
        )
    else:
        run_tool(
            "test_improvement_dream",
            {"dream": {}, "test_environments": ["sandbox"]},
            note="Expected failure: dream generation did not produce data.",
        )

    # --- AI Collaboration Tools -------------------------------------------
    run_tool(
        "send_ai_message",
        {
            "from_ai": "codex",
            "to_ai": "aether",
            "content": "MCP audit diagnostic ping.",
            "message_type": "discussion",
            "priority": "medium",
        },
    )
    run_tool("get_ai_messages", {"from_ai": "codex", "limit": 5})
    run_tool(
        "start_ai_discussion",
        {
            "from_ai": "codex",
            "to_ai": "aether",
            "topic": "MCP Tool Audit",
            "initial_message": "Initiating discussion on MCP tool health checks.",
        },
    )
    run_tool(
        "handoff_task_to_ai",
        {
            "from_ai": "codex",
            "to_ai": "aether",
            "task_description": "Review MCP audit results",
            "priority": "medium",
        },
    )
    run_tool(
        "share_ai_profile",
        {
            "from_ai": "codex",
            "to_ai": "aether",
            "profile_data": {
                "name": "Codex",
                "capabilities": ["diagnostics", "tooling", "analysis"],
                "strengths": ["systematic testing"],
                "learning_areas": ["broader integration"],
            },
        },
    )
    run_tool("get_ai_collaboration_summary", {})

    report = {
        "timestamp": audit_timestamp,
        "tool_count": len(results),
        "results": results,
    }
    json_output = json.dumps(report, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json_output, encoding="utf-8")

    print(json_output)


if __name__ == "__main__":
    main()
