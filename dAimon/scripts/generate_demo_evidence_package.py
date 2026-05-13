#!/usr/bin/env python3
"""Generate the judge-facing dAimon evidence package and dashboard feed."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from ion_kernel.schemas import utc_now
from validate_agent_builder_mcp_trace import DASHBOARD_PATH as AGENT_BUILDER_DASHBOARD_PATH
from validate_agent_builder_mcp_trace import OUTPUT_PATH as AGENT_BUILDER_VALIDATION_PATH
from validate_agent_builder_mcp_trace import DEFAULT_TRACE_PATH, validate_trace, write_json

OUT_DIR = ROOT / "sample_outputs"
PACKAGE_PATH = OUT_DIR / "demo_evidence_package.json"
DASHBOARD_PATH = OUT_DIR / "dashboard_evidence_trace.json"
CLAIMS_PATH = OUT_DIR / "demo_video_claims.json"


def load_json(rel: str) -> dict[str, Any]:
    path = ROOT / rel
    if not path.exists():
        return {"missing": True, "path": rel}
    return json.loads(path.read_text(encoding="utf-8"))


def has_stop_finish(response: Mapping[str, Any]) -> bool:
    for candidate in response.get("raw_response", {}).get("candidates", []) or []:
        if candidate.get("finishReason") == "STOP":
            return True
    return False


def artifact(rel: str, purpose: str, required: bool = True) -> dict[str, Any]:
    path = ROOT / rel
    return {
        "path": rel,
        "purpose": purpose,
        "exists": path.exists(),
        "required": required,
    }


def claim_matrix(
    live_summary: Mapping[str, Any],
    gemini_summary: Mapping[str, Any],
    gemini_response: Mapping[str, Any],
    agent_builder_validation: Mapping[str, Any],
    cloud_run_deploy: Mapping[str, Any],
    cloud_run_health: Mapping[str, Any],
    google_user_access: Mapping[str, Any],
) -> list[dict[str, Any]]:
    claim_status = live_summary.get("claim_status", {})
    cloud_blockers = list(cloud_run_deploy.get("blockers", [])) + list(cloud_run_health.get("blockers", []))
    return [
        {
            "claim_id": "local_governance_pipeline",
            "claim": "dAimon imports, classifies, settles, receipts, and exports governed inheritance.",
            "status": claim_status.get("local_governance_pipeline", "proven_local"),
            "evidence": ["sample_outputs/local_demo_summary.json", "sample_outputs/live_vertical_slice_summary.json"],
            "non_claim": False,
        },
        {
            "claim_id": "mongodb_live_seed_and_inheritance",
            "claim": "dAimon can write candidate demo records to MongoDB and read only receipt-cleared inherited objects back.",
            "status": claim_status.get("mongodb_live_seed_and_inheritance", "blocked"),
            "evidence": ["sample_outputs/mongodb_live_readiness.json", "sample_outputs/live_vertical_slice_mcp_trace.json"],
            "non_claim": False,
        },
        {
            "claim_id": "gemini_receipt_cleared_handoff",
            "claim": "Gemini receives a receipt-cleared context bundle and returns candidate output.",
            "status": claim_status.get("gemini_receipt_cleared_handoff", "blocked"),
            "evidence": ["sample_outputs/gemini_handoff_summary.json", "sample_outputs/gemini_candidate_output.json"],
            "checks": {
                "gemini_ok": gemini_summary.get("ok") is True,
                "finish_reason_stop": has_stop_finish(gemini_response),
                "candidate_not_inheritable": gemini_summary.get("candidate_inheritance_status") == "NOT_INHERITABLE_AS_STATE_WITHOUT_SETTLEMENT",
            },
            "non_claim": False,
        },
        {
            "claim_id": "cloud_run_kernel_live_endpoint",
            "claim": "The dAimon kernel can run on Cloud Run and query live MongoDB-backed receipt-cleared state.",
            "status": "proven_live_cloud_run" if cloud_run_health.get("ok") is True else "pending_cloud_run_deploy",
            "evidence": ["sample_outputs/cloud_run_deploy_summary.json", "sample_outputs/cloud_run_live_health.json"],
            "blockers": [] if cloud_run_health.get("ok") is True else cloud_blockers or [
                "Install/authenticate gcloud, deploy Cloud Run, and capture live health/evidence response.",
            ],
            "non_claim": cloud_run_health.get("ok") is not True,
        },
        {
            "claim_id": "agent_builder_mongodb_mcp_tool_trace",
            "claim": "Agent Builder called MongoDB MCP with an accepted-only retrieval filter.",
            "status": "proven_live_agent_builder_mcp" if agent_builder_validation.get("live_mcp_execution_proven") else "pending_live_trace",
            "evidence": ["sample_outputs/agent_builder_mcp_trace_validation.json"],
            "blockers": [] if agent_builder_validation.get("live_mcp_execution_proven") else agent_builder_validation.get("blockers", [
                "Attach a live Agent Builder trace export as sample_outputs/agent_builder_mcp_trace.json.",
            ]),
            "non_claim": not agent_builder_validation.get("live_mcp_execution_proven"),
        },
        {
            "claim_id": "google_user_tester_access",
            "claim": "Named Google user or tester accounts can access the shared dAimon Google surfaces.",
            "status": "proven_google_user_access" if google_user_access.get("ok") is True else "pending_google_user_access",
            "evidence": ["sample_outputs/google_user_access_readiness.json"],
            "blockers": [] if google_user_access.get("ok") is True else google_user_access.get("blockers", [
                "Run scripts/check_google_user_access_readiness.py with target tester principals.",
            ]),
            "non_claim": google_user_access.get("ok") is not True,
        },
        {
            "claim_id": "complete_enterprise_deployment",
            "claim": "dAimon is production-ready enterprise governance.",
            "status": "non_claim",
            "evidence": ["docs/contest_vertical_slice_plan.md"],
            "non_claim": True,
        },
    ]


def video_scenes(claims: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "scene": 1,
            "title": "Failure Mode",
            "screen": "Show messy AI work entering as witness material.",
            "claim_ids": ["local_governance_pipeline"],
            "evidence": ["sample_inputs/", "sample_outputs/continuity_objects.json"],
        },
        {
            "scene": 2,
            "title": "Settlement Boundary",
            "screen": "Show accepted, deferred, and proof-debt objects split before inheritance.",
            "claim_ids": ["local_governance_pipeline"],
            "evidence": ["sample_outputs/settlement_queue.json", "sample_outputs/live_vertical_slice_receipt.json"],
        },
        {
            "scene": 3,
            "title": "MongoDB Accepted-Only Retrieval",
            "screen": "Show the accepted-only query filter and returned object IDs.",
            "claim_ids": ["mongodb_live_seed_and_inheritance"],
            "evidence": ["sample_outputs/live_vertical_slice_mcp_trace.json"],
        },
        {
            "scene": 4,
            "title": "Gemini Handoff",
            "screen": "Show Gemini receives only receipt-cleared objects and returns candidate output.",
            "claim_ids": ["gemini_receipt_cleared_handoff"],
            "evidence": ["sample_outputs/gemini_handoff_context_bundle.json", "sample_outputs/gemini_candidate_output.json"],
        },
        {
            "scene": 5,
            "title": "Agent Builder MCP Gate",
            "screen": "Show Cloud Run endpoint proof plus pending or attached Agent Builder/MongoDB MCP trace evidence.",
            "claim_ids": ["cloud_run_kernel_live_endpoint", "agent_builder_mongodb_mcp_tool_trace"],
            "evidence": [
                "sample_outputs/cloud_run_live_health.json",
                "sample_outputs/agent_builder_mcp_trace_validation.json",
            ],
        },
        {
            "scene": 6,
            "title": "Tester Access Gate",
            "screen": "Show runtime proof is separate from named Google account access readiness.",
            "claim_ids": ["google_user_tester_access"],
            "evidence": ["sample_outputs/google_user_access_readiness.json"],
        },
        {
            "scene": 7,
            "title": "Honest Boundary",
            "screen": "Show non-claims and what remains roadmap.",
            "claim_ids": ["complete_enterprise_deployment"],
            "evidence": ["docs/contest_vertical_slice_plan.md"],
        },
    ]


def dashboard_trace(package: Mapping[str, Any]) -> dict[str, Any]:
    claims = package.get("claim_matrix", [])
    return {
        "schema": "daimon.dashboard_evidence_trace.v0_1",
        "generated_at": package.get("generated_at"),
        "headline_status": package.get("headline_status"),
        "metrics": package.get("metrics"),
        "claims": claims,
        "phases": package.get("live_vertical_slice", {}).get("phases", []),
        "video_scenes": package.get("video_scenes", []),
        "artifact_inventory": package.get("artifact_inventory", []),
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
    }


def main() -> int:
    agent_builder_validation, _ = validate_trace(DEFAULT_TRACE_PATH, require_live_trace=False)
    write_json(AGENT_BUILDER_VALIDATION_PATH, agent_builder_validation)
    write_json(AGENT_BUILDER_DASHBOARD_PATH, {
        "schema": "daimon.agent_builder_mcp_dashboard_trace.v0_1",
        "live_mcp_execution_proven": bool(agent_builder_validation.get("live_mcp_execution_proven")),
        "trace_rows": [
            {
                "phase": "agent_builder_mcp_trace",
                "status": agent_builder_validation.get("proof_status"),
                "evidence": agent_builder_validation.get("trace_path"),
                "detail": "Attach live Agent Builder trace export to promote this claim.",
            }
        ],
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
    })

    live_summary = load_json("sample_outputs/live_vertical_slice_summary.json")
    gemini_summary = load_json("sample_outputs/gemini_handoff_summary.json")
    gemini_response = load_json("sample_outputs/gemini_handoff_response.json")
    mcp_trace = load_json("sample_outputs/live_vertical_slice_mcp_trace.json")
    cloud_run_deploy = load_json("sample_outputs/cloud_run_deploy_summary.json")
    cloud_run_health = load_json("sample_outputs/cloud_run_live_health.json")
    google_user_access = load_json("sample_outputs/google_user_access_readiness.json")
    connector_expansion = load_json("sample_outputs/connector_expansion_plan.json")
    claims = claim_matrix(
        live_summary,
        gemini_summary,
        gemini_response,
        agent_builder_validation,
        cloud_run_deploy,
        cloud_run_health,
        google_user_access,
    )
    scenes = video_scenes(claims)
    artifacts = [
        artifact("sample_outputs/live_vertical_slice_summary.json", "One-command end-to-end live proof."),
        artifact("sample_outputs/live_vertical_slice_mcp_trace.json", "Accepted-only MongoDB trace envelope."),
        artifact("sample_outputs/gemini_handoff_summary.json", "Gemini API handoff summary."),
        artifact("sample_outputs/gemini_candidate_output.json", "Gemini return captured as candidate."),
        artifact("sample_outputs/cloud_run_deploy_summary.json", "Cloud Run deploy summary.", required=False),
        artifact("sample_outputs/cloud_run_live_health.json", "Cloud Run live health and evidence check.", required=False),
        artifact("sample_outputs/agent_builder_mcp_trace_validation.json", "Agent Builder/MongoDB MCP trace gate."),
        artifact("sample_outputs/agent_builder_mcp_trace.json", "Optional live Agent Builder trace export.", required=False),
        artifact("sample_outputs/google_user_access_readiness.json", "Named Google user/tester access readiness gate.", required=False),
        artifact("sample_outputs/custom_gpt_action_visibility_smoke.json", "Custom GPT Action Gateway dAimon visibility smoke receipt.", required=False),
        artifact("sample_outputs/connector_expansion_plan.json", "Connector expansion readiness plan.", required=False),
        artifact("docs/contest_vertical_slice_plan.md", "Claim and non-claim boundaries."),
        artifact("docs/google_user_access_readiness.md", "Google tester access readiness protocol."),
        artifact("docs/custom_gpt_action_connection.md", "Custom GPT Action connection setup."),
        artifact("docs/gitlab_connection_readiness.md", "GitLab read-only connector setup."),
        artifact("docs/self_demonstrating_video_agent.md", "Governed demo-video plan."),
        artifact("docs/ui_canon_product_plan.md", "UI canon product planning boundary."),
        artifact("orchestration/ui_surface_plan.json", "Structured UI surface plan."),
        artifact("orchestration/connector_expansion_registry.json", "Structured connector expansion registry."),
    ]
    metrics = {
        "objects_classified": live_summary.get("objects_classified", 0),
        "objects_written": live_summary.get("objects_written", 0),
        "inheritable_returned_from_mongodb": live_summary.get("inheritable_returned_from_mongodb", 0),
        "trace_returned_object_count": live_summary.get("trace_returned_object_count", 0),
        "gemini_candidate_object_count": gemini_summary.get("candidate_object_count", 0),
        "excluded_count": mcp_trace.get("exclusion_report", {}).get("excluded_count", 0),
        "live_agent_builder_mcp_proven": bool(agent_builder_validation.get("live_mcp_execution_proven")),
        "cloud_run_live_proven": bool(cloud_run_health.get("ok")),
        "google_user_access_proven": bool(google_user_access.get("ok")),
        "connector_target_count": connector_expansion.get("connector_count", 0),
    }
    next_proof_gates = []
    if cloud_run_health.get("ok") is not True:
        next_proof_gates.append("Deploy the Cloud Run kernel and attach sample_outputs/cloud_run_live_health.json.")
    if not agent_builder_validation.get("live_mcp_execution_proven"):
        next_proof_gates.append("Capture Agent Builder trace export showing MongoDB MCP tool call.")
    if google_user_access.get("ok") is not True:
        next_proof_gates.append("Reauthenticate gcloud and run the Google user access readiness gate with target tester accounts.")
    if connector_expansion.get("ok") is True:
        next_proof_gates.append("Configure GitLab read-only env values and add a live readiness probe.")
    else:
        next_proof_gates.append("Run scripts/generate_connector_expansion_plan.py.")
    next_proof_gates.append("Add dashboard screenshot and video narration receipt.")
    headline_status = (
        "live_vertical_slice_proven_agent_builder_mcp_proven"
        if agent_builder_validation.get("live_mcp_execution_proven")
        else "live_vertical_slice_proven_agent_builder_mcp_pending"
    )
    package = {
        "schema": "daimon.demo_evidence_package.v0_1",
        "generated_at": utc_now(),
        "headline_status": headline_status,
        "live_vertical_slice": live_summary,
        "claim_matrix": claims,
        "video_scenes": scenes,
        "artifact_inventory": artifacts,
        "metrics": metrics,
        "next_proof_gates": next_proof_gates,
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
    }
    write_json(PACKAGE_PATH, package)
    write_json(CLAIMS_PATH, {"schema": "daimon.demo_video_claims.v0_1", "claims": claims, "scenes": scenes})
    write_json(DASHBOARD_PATH, dashboard_trace(package))
    print(json.dumps({
        "ok": True,
        "package_path": str(PACKAGE_PATH.relative_to(ROOT)),
        "dashboard_path": str(DASHBOARD_PATH.relative_to(ROOT)),
        "claims": len(claims),
        "video_scenes": len(scenes),
        "headline_status": package["headline_status"],
        "accepted_state_changed": False,
        "external_mutation_attempted": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
