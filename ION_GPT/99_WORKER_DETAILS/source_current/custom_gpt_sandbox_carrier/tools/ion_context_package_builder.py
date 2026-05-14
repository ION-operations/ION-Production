#!/usr/bin/env python3
"""Build candidate ION context packages from a context mesh and workflow state."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import hashlib
import yaml
import zipfile


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def default_workflow_state() -> Dict[str, Any]:
    return {
        "schema_id": "ion.sequence_continuation.v1",
        "active_objective": "custom_gpt_v4_7_dogfood_context_packages",
        "active_route": "DOGFOOD_CONTEXT_PACKAGE_BUILD_ROUTE",
        "current_phase": "context_package_build_validated",
        "completed_phases": [
            "MOUNT_LOCAL_CAPSULES",
            "BUILD_CONTEXT_MESH",
            "BUILD_CONTEXT_PACKAGE",
            "EXPORT_TRANSFER_PACKAGE",
            "REMOUNT_SIMULATION",
            "VALIDATE",
        ],
        "pending_phases": ["REVIEW", "CODEX_APPLY", "RECEIPT_ACCEPTANCE"],
        "authority": {
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
        },
    }


def build_context_package(
    package_id: str,
    context_mesh: Dict[str, Any],
    workflow_state: Dict[str, Any] | None = None,
    architecture_signals: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    workflow_state = workflow_state or default_workflow_state()
    architecture_signals = architecture_signals or []
    return {
        "schema_id": "ion.context_package.v1",
        "package_id": package_id,
        "created_at_utc": "20260513T221500Z",
        "created_by": "custom_gpt_sandbox_carrier",
        "posture": "sandbox-candidate",
        "authority": {
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
        },
        "context_mesh": {
            "mesh_id": context_mesh.get("mesh_id"),
            "capsule_count": len(context_mesh.get("capsules", [])),
            "relevant_capsule_paths": context_mesh.get("relevant_capsule_paths", []),
            "inheritance_edges": context_mesh.get("inheritance_edges", []),
        },
        "workflow_state": workflow_state,
        "persona_state": {
            "schema": "ion.persona_response_envelope.v0_1",
            "selected_profile": "audit_repair",
            "visible_name": "ION Persona Interface",
            "hidden_chain_of_thought_exposed": False,
        },
        "domain_agent_state": {
            "schema_id": "ion.dynamic_domain_agent_expansion.v1",
            "status": "candidate_not_accepted_canon",
            "candidate_domains": [
                {"domain_id": "domain.context_mesh", "title": "Context Mesh", "status": "operational_candidate"},
                {"domain_id": "domain.transfer_profile", "title": "Transfer Profile", "status": "operational_candidate"},
            ],
            "candidate_agents": [
                {"agent_id": "agent.context_mesh_steward", "display_name": "Context Mesh Steward", "can_claim_state": False},
                {"agent_id": "agent.transfer_scribe", "display_name": "Transfer Scribe", "can_claim_state": False},
            ],
            "registry_boundary": {
                "mutates_accepted_registry": False,
                "requires_human_acceptance_to_land": True,
            },
        },
        "architecture_signals": architecture_signals,
        "fanout_state": {
            "schema_id": "ion.ordered_context_fanout.v1",
            "status": "not_active_for_this_package",
            "batons": [],
            "unresolved_alerts": [],
        },
        "continuity_export": {
            "profile": "working_handoff",
            "next_chat_prompt": "NEXT_CHAT_PROMPT.txt",
            "mount_before_substantive_answer": True,
        },
        "hashes": {},
    }


def write_context_package(package: Dict[str, Any], out_path: Path) -> Dict[str, Any]:
    rendered = yaml.safe_dump(package, sort_keys=False)
    package["hashes"]["self_without_hashes_note"] = sha256_bytes(rendered.encode("utf-8"))
    rendered = yaml.safe_dump(package, sort_keys=False)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")
    return package


def build_package_zip(package_dir: Path, zip_path: Path) -> Dict[str, str]:
    """Zip a context package directory and return member hashes."""
    hashes: Dict[str, str] = {}
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(p for p in package_dir.rglob("*") if p.is_file()):
            rel = path.relative_to(package_dir).as_posix()
            hashes[rel] = sha256_file(path)
            zf.write(path, rel)
    return hashes


def write_next_chat_prompt(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "BOOT-SEQUENCE\n\n"
        "Mount the attached ION context package before any substantive answer. "
        "Treat it as candidate context, not accepted state. Restore active route, "
        "candidate domains/agents, persona profile, folder capsule mesh, receipts, "
        "transfer profile, and blockers. Complete the next lawful sequence through "
        "Persona Interface response or emit persona_gate_blocked with missing proof.\n",
        encoding="utf-8",
    )
