#!/usr/bin/env python3
"""Candidate continuity transfer exporter for Custom GPT v4.3.

The exporter writes a deterministic remountable package from supplied workflow
objects. It never includes secrets or vault paths.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import hashlib
import json
import zipfile
import yaml

REQUIRED_FILES = [
    "README_START_HERE.md",
    "ion_continuity_transfer_manifest.yaml",
    "ion_boot_sequence_result.yaml",
    "ion_persona_response_envelope.yaml",
    "ion_sequence_continuation.yaml",
    "ion_dynamic_domain_agent_expansion.yaml",
    "ion_project_profile.yaml",
    "ion_receipt_summary.yaml",
    "ion_proof_manifest.yaml",
    "patches/cumulative_candidate.patch",
    "reports/validation_report.md",
    "tests/validation_results.yaml",
    "sources/source_manifest.yaml",
    "NEXT_CHAT_PROMPT.txt",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def default_objects() -> Dict[str, str]:
    return {
        "README_START_HERE.md": "# ION Continuity Transfer Package\n\nMount this package before substantive answer.\n",
        "ion_boot_sequence_result.yaml": yaml.safe_dump({"ion_boot_sequence_result": {"schema_id": "ion.boot_sequence_result.v1", "accepted_state_claim": False, "production_authority": False, "live_execution_authority": False}}, sort_keys=False),
        "ion_persona_response_envelope.yaml": yaml.safe_dump({"ion_persona": {"schema": "ion.persona_response_envelope.v0_1", "boundaries": {"hidden_chain_of_thought_exposed": False}}}, sort_keys=False),
        "ion_sequence_continuation.yaml": yaml.safe_dump({"ion_sequence_continuation": {"schema_id": "ion.sequence_continuation.v1", "candidate_domains": [], "candidate_agents": [], "authority": {"accepted_state_claim": False, "production_authority": False, "live_execution_authority": False}}}, sort_keys=False),
        "ion_dynamic_domain_agent_expansion.yaml": yaml.safe_dump({"ion_dynamic_domain_agent_expansion": {"schema_id": "ion.dynamic_domain_agent_expansion.v1", "status": "candidate_not_accepted_canon", "candidate_domains": [], "candidate_agents": [], "registry_boundary": {"mutates_accepted_registry": False}}}, sort_keys=False),
        "ion_project_profile.yaml": yaml.safe_dump({"schema_id": "ion.project_profile.v1", "status": "candidate_project_context", "authority": {"accepted_state_claim": False, "production_authority": False, "live_execution_authority": False}}, sort_keys=False),
        "ion_receipt_summary.yaml": yaml.safe_dump({"receipts": [], "accepted_state_claim": False}, sort_keys=False),
        "ion_proof_manifest.yaml": yaml.safe_dump({"proofs": [], "posture": "sandbox-candidate"}, sort_keys=False),
        "patches/cumulative_candidate.patch": "",
        "reports/validation_report.md": "# Validation Report\n\nCandidate-only.\n",
        "tests/validation_results.yaml": yaml.safe_dump({"tests": [], "result": "not_run"}, sort_keys=False),
        "sources/source_manifest.yaml": yaml.safe_dump({"sources": [], "omitted": []}, sort_keys=False),
        "NEXT_CHAT_PROMPT.txt": "BOOT-SEQUENCE\n\nMount the attached ION continuity transfer package first. Treat it as candidate context, not accepted state.\n",
    }


def build_package(out_dir: Path, package_id: str = "ION_CONTINUITY_TRANSFER_PACKAGE_CANDIDATE") -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    files = default_objects()
    hashes = {}
    for rel, content in files.items():
        path = out_dir / package_id / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        hashes[rel] = sha256_bytes(content.encode("utf-8"))

    manifest = {
        "schema_id": "ion.continuity_transfer_package.v1",
        "package_id": package_id,
        "created_by": "custom_gpt_sandbox_carrier",
        "posture": "sandbox-candidate",
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "active_objective": "candidate",
        "active_route": "candidate",
        "continuity_files": {
            "boot_receipt": "ion_boot_sequence_result.yaml",
            "persona_envelope": "ion_persona_response_envelope.yaml",
            "sequence_continuation": "ion_sequence_continuation.yaml",
            "dynamic_domain_agent_expansion": "ion_dynamic_domain_agent_expansion.yaml",
            "project_profile": "ion_project_profile.yaml",
            "receipt_summary": "ion_receipt_summary.yaml",
            "proof_manifest": "ion_proof_manifest.yaml",
        },
        "next_chat_prompt": "NEXT_CHAT_PROMPT.txt",
        "remount_rule": "mount_before_substantive_answer",
        "hashes": hashes,
        "blockers": [],
    }
    manifest_text = yaml.safe_dump(manifest, sort_keys=False)
    manifest_path = out_dir / package_id / "ion_continuity_transfer_manifest.yaml"
    manifest_path.write_text(manifest_text, encoding="utf-8")
    hashes["ion_continuity_transfer_manifest.yaml"] = sha256_bytes(manifest_text.encode("utf-8"))

    zip_path = out_dir / f"{package_id}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted((out_dir / package_id).rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(out_dir / package_id))
    return zip_path
