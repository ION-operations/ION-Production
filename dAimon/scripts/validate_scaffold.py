#!/usr/bin/env python3
"""Validate the functional scaffold without external services."""
from __future__ import annotations

from pathlib import Path
import ast
import json
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "LICENSE",
    "ion_kernel/bridge_core.py",
    "ion_kernel/api.py",
    "ion_kernel/schemas.py",
    "ion_kernel/receipt_chain.py",
    "ion_kernel/settlement_queue.py",
    "ion_kernel/inheritance.py",
    "ion_kernel/mcp_trace.py",
    "ion_kernel/persistence.py",
    "scripts/run_mcp_trace_harness.py",
    "scripts/run_gemini_handoff_demo.py",
    "scripts/run_live_vertical_slice.py",
    "scripts/validate_agent_builder_mcp_trace.py",
    "scripts/generate_demo_evidence_package.py",
    "scripts/validate_mcp_trace_harness.py",
    "scripts/deploy_cloud_run.py",
    "scripts/check_cloud_run_live.py",
    "scripts/check_phoenix_readiness.py",
    "scripts/validate_orchestration_plan.py",
    "agent_builder/agent_tool_manifest.yaml",
    "agent_builder/system_prompt.md",
    "agent_builder/openapi_tools_contract.json",
    ".gcloudignore",
    "mcp/mongodb_mcp_visibility_contract.json",
    "docs/full_orchestration_plan.md",
    "docs/self_demonstrating_video_agent.md",
    "docs/contest_vertical_slice_plan.md",
    "docs/custom_gpt_expansion_plan.md",
    "docs/ui_canon_product_plan.md",
    "docs/partner_ecosystem_expansion.md",
    "docs/agent_builder_mcp_trace_capture.md",
    "orchestration/product_layers.json",
    "orchestration/partner_adapter_registry.json",
    "orchestration/domain_registry.json",
    "orchestration/template_registry.json",
    "orchestration/receipt_registry.json",
    "orchestration/build_roadmap.json",
    "orchestration/test_matrix.json",
    "orchestration/management_cadence.json",
    "orchestration/ui_surface_plan.json",
    "sample_inputs/sample_assistant_export.json",
    "sample_inputs/sample_project_notes.md",
    "sample_inputs/sample_tasks.csv",
    "sample_inputs/sample_sources.csv",
    "sample_outputs/local_demo_summary.json",
    "sample_outputs/inheritance_bundle.json",
    "sample_outputs/mcp_visibility_trace.json",
    "sample_outputs/mcp_trace_dashboard_trace.json",
    "sample_outputs/orchestration_validation.json",
    "sample_outputs/receipt_candidate.json",
    "sample_outputs/demo_evidence_package.json",
    "sample_outputs/dashboard_evidence_trace.json",
    "sample_outputs/demo_video_claims.json",
]

PY_FILES = list((REPO_ROOT / "ion_kernel").glob("*.py")) + list((REPO_ROOT / "scripts").glob("*.py"))


def main() -> int:
    failures = []
    for rel in REQUIRED:
        if not (REPO_ROOT / rel).exists():
            failures.append(f"missing required file: {rel}")

    for py_file in PY_FILES:
        try:
            ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            failures.append(f"syntax error in {py_file.relative_to(REPO_ROOT)}: {exc}")

    for rel in [
        "sample_outputs/local_demo_summary.json",
        "sample_outputs/inheritance_bundle.json",
        "sample_outputs/mcp_visibility_trace.json",
        "sample_outputs/mcp_trace_dashboard_trace.json",
        "sample_outputs/orchestration_validation.json",
        "sample_outputs/receipt_candidate.json",
        "sample_outputs/demo_evidence_package.json",
        "sample_outputs/dashboard_evidence_trace.json",
        "sample_outputs/demo_video_claims.json",
        "mcp/mongodb_mcp_visibility_contract.json",
        "orchestration/product_layers.json",
        "orchestration/partner_adapter_registry.json",
        "orchestration/domain_registry.json",
        "orchestration/template_registry.json",
        "orchestration/receipt_registry.json",
        "orchestration/build_roadmap.json",
        "orchestration/test_matrix.json",
        "orchestration/management_cadence.json",
        "orchestration/ui_surface_plan.json",
    ]:
        try:
            json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))
        except Exception as exc:
            failures.append(f"invalid json {rel}: {exc}")

    if not failures:
        summary = json.loads((REPO_ROOT / "sample_outputs/local_demo_summary.json").read_text(encoding="utf-8"))
        if summary.get("accepted_state_changed") is not False:
            failures.append("local demo summary must preserve accepted_state_changed=false")
        if summary.get("external_mutation_attempted") is not False:
            failures.append("local demo summary must preserve external_mutation_attempted=false")
        if summary.get("objects_classified", 0) < 8:
            failures.append("expected at least 8 sample continuity objects")
        if summary.get("inheritable_count", 0) < 1:
            failures.append("expected at least 1 sample inheritable object")

        orchestration = json.loads(
            (REPO_ROOT / "sample_outputs/orchestration_validation.json").read_text(encoding="utf-8")
        )
        if orchestration.get("ok") is not True:
            failures.append("orchestration validation sample must have ok=true")
        if orchestration.get("accepted_state_changed") is not False:
            failures.append("orchestration validation must preserve accepted_state_changed=false")
        if orchestration.get("external_mutation_attempted") is not False:
            failures.append("orchestration validation must preserve external_mutation_attempted=false")

    result = {
        "ok": not failures,
        "failures": failures,
        "checked_files": len(REQUIRED),
        "python_files": len(PY_FILES),
    }
    print(json.dumps(result, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
