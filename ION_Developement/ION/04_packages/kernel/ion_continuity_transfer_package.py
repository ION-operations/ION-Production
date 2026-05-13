"""Build portable ION continuity transfer packages.

The package is a candidate handoff artifact for moving between GPT/chat/carrier
sessions without losing route, authority, receipt, and next-action posture.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

PACKAGE_PREFIX = "ION_CONTINUITY_TRANSFER_PACKAGE"
DEFAULT_OUTPUT = Path("ION_EXPORTS_LOCAL/continuity_transfer")
TEMPLATE_ROOT = Path("ION_Developement/ION/07_templates/continuity_transfer")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def build_project_hash(workspace: Path, branch: str, commit: str, timestamp: str) -> str:
    """Return a stable candidate project hash for this transfer package."""
    seed = f"ion_project|{workspace}|{branch}|{commit}|{timestamp}"
    return "ionproj_" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:24]


def git_value(workspace: Path, args: list[str], default: str = "unknown") -> str:
    try:
        return subprocess.check_output(["git", *args], cwd=workspace, text=True, stderr=subprocess.DEVNULL).strip() or default
    except Exception:
        return default


def load_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def read_text_if_exists(path: Path, max_chars: int = 12000) -> str:
    if not path.exists() or not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[:max_chars]


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if yaml is not None:
        path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=False), encoding="utf-8")
    else:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists() or not src.is_file():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def build_package(workspace: Path, output_root: Path, timestamp: str | None = None) -> dict[str, Any]:
    workspace = workspace.resolve()
    timestamp = timestamp or utc_stamp()
    package_id = f"{PACKAGE_PREFIX}_{timestamp}"
    output_root = (workspace / output_root).resolve() if not output_root.is_absolute() else output_root.resolve()
    staging = output_root / f".{package_id}_staging"
    zip_path = output_root / f"{package_id}.zip"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)
    output_root.mkdir(parents=True, exist_ok=True)

    branch = git_value(workspace, ["branch", "--show-current"])
    commit = git_value(workspace, ["rev-parse", "--short", "HEAD"])
    status_short = git_value(workspace, ["status", "--short"], default="")
    project_hash = build_project_hash(workspace, branch, commit, timestamp)

    template_dir = workspace / TEMPLATE_ROOT
    if not template_dir.exists():
        active_root_template_dir = workspace / "ION/07_templates/continuity_transfer"
        if active_root_template_dir.exists():
            template_dir = active_root_template_dir
    readme_template = template_dir / "README_START_HERE_TEMPLATE.md"
    next_prompt_template = template_dir / "NEXT_CHAT_PROMPT_TEMPLATE.txt"
    (staging / "README_START_HERE.md").write_text(read_text_if_exists(readme_template) or "# ION Continuity Transfer Package\n", encoding="utf-8")
    (staging / "NEXT_CHAT_PROMPT.txt").write_text(read_text_if_exists(next_prompt_template) or "boot-sequence\n", encoding="utf-8")

    boot_result = {
        "schema_id": "ion.boot_sequence_result.v1",
        "boot_id": f"continuity_transfer_{timestamp}",
        "ion_project_hash": project_hash,
        "project_hash_status": "assigned_candidate",
        "route_id": "CONTINUITY_TRANSFER_EXPORT",
        "mounted_packages": {"count": 0, "posture": "candidate_context"},
        "objective": "portable continuity handoff",
        "active_workflow_object": package_id,
        "phases_completed": ["SCRIBE_EXPORT", "PROOF_MANIFEST", "NEXT_CHAT_PROMPT"],
        "persona_return_gate": "not_applicable_export_package",
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "receipt_status": "candidate_transfer_receipt",
    }
    write_yaml(staging / "ion_boot_sequence_result.yaml", {"ion_boot_sequence_result": boot_result})

    persona = {
        "schema": "ion.persona_response_envelope.v0_1",
        "verdict": "ION_PERSONA_RESPONSE_ENVELOPE_READY",
        "persona": {
            "visible_name": "ION Continuity Transfer",
            "role_ref": "role.persona_interface",
            "selected_profile": "technical_plain",
            "profile_status": "active_candidate",
            "persona_is_total_ion": False,
        },
        "route": {
            "route_id": "CONTINUITY_TRANSFER_EXPORT",
            "selection_basis": "local package export requested by operator",
            "candidate_domains": ["continuity_transfer", "custom_gpt_front_door"],
            "candidate_agents": ["SCRIBE", "RELAY", "PERSONA_INTERFACE"],
        },
        "dynamic_domain_signal": {"needed": False, "semantic": "Transfer package builder is sufficient for this handoff."},
        "confidence": {"level": "scoped", "semantic": "Package is portable candidate evidence, not accepted state."},
        "gesture": {"gesture": "direct_open_hand", "semantic": "Symbolic response posture, not a body claim."},
        "inner_monologue": {
            "type": "operator_visible_persona_signal_not_hidden_reasoning",
            "text": "I am preserving continuity with explicit proof and authority boundaries.",
            "not_claimed": ["hidden_chain_of_thought", "private_reasoning_transcript", "lived_human_emotion", "personal_consciousness"],
        },
        "boundaries": {
            "output_is_not_state": True,
            "candidate_until_receipted_or_accepted": True,
            "production_authority": False,
            "live_execution_authority": False,
            "hidden_chain_of_thought_exposed": False,
        },
    }
    write_yaml(staging / "ion_persona_response_envelope.yaml", {"ion_persona": persona})

    continuation = {
        "active_objective": "continue ION work from this transfer package",
        "active_workflow_object": package_id,
        "ion_project_hash": project_hash,
        "project_hash_status": "reuse_this_hash_when_mounting_this_package",
        "current_phase": "TRANSFER_READY",
        "completed_phases": ["PACKAGE_BUILT"],
        "pending_phases": ["MOUNT_IN_NEXT_CHAT", "RUN_BOOT_SEQUENCE", "SELECT_NEXT_ROUTE"],
        "next_phase": "MOUNT_IN_NEXT_CHAT",
        "required_context_or_files": ["README_START_HERE.md", "ion_continuity_transfer_manifest.yaml"],
        "blocker": "none",
        "authority": "read-only until operator approves bounded mutation",
        "exact_continuation_route_or_prompt": "Use NEXT_CHAT_PROMPT.txt in the next chat with this package attached.",
    }
    write_yaml(staging / "ion_sequence_continuation.yaml", {"ion_sequence_continuation": continuation})

    write_yaml(staging / "ion_dynamic_domain_agent_expansion.yaml", {
        "ion_dynamic_domain_agent_expansion": {
            "needed": False,
            "candidate_domains": [],
            "candidate_agents": [],
            "semantic": "No new domain required to consume this transfer package.",
        }
    })

    write_yaml(staging / "ion_project_profile.yaml", {
        "ion_project_profile": {
            "workspace_root": str(workspace),
            "ion_project_hash": project_hash,
            "project_hash_status": "assigned_candidate",
            "git_branch": branch,
            "git_commit": commit,
            "status_short_present": bool(status_short.strip()),
            "active_ion_root": "ION_Developement",
            "custom_gpt_folder": "ION_GPT",
            "source_posture": "local_working_tree_candidate",
        }
    })

    receipt_sources = [
        workspace / "Needs_Routed/ion_custom_gpt_front_door_carrier_v4_codex_settlement_20260513T194500Z.yaml",
        workspace / "Needs_Routed/ion_custom_gpt_front_door_carrier_v4_chatgpt_followup_audit_20260513T200600Z.yaml",
        workspace / "Needs_Routed/ion_custom_gpt_front_door_carrier_v4_2_persona_visible_envelope_repair_20260513T202000Z.yaml",
    ]
    receipt_summary = []
    for src in receipt_sources:
        if src.exists():
            receipt_summary.append({"path": str(src.relative_to(workspace)), "sha256": sha256(src)})
    write_yaml(staging / "ion_receipt_summary.yaml", {"ion_receipt_summary": {"receipts": receipt_summary}})

    non_claims = {
        "accepted_state_claim": False,
        "production_deployment": False,
        "git_push_authority": False,
        "live_execution_authority": False,
        "secrets_included": False,
        "hidden_chain_of_thought_included": False,
    }
    write_yaml(staging / "ion_non_claims.yaml", {"ion_non_claims": non_claims})
    write_yaml(staging / "ion_settlement_required.yaml", {"ion_settlement_required": {"required": True, "reason": "Transfer package is candidate evidence only."}})

    (staging / "patches").mkdir()
    try:
        patch_text = subprocess.check_output(["git", "diff", "--", "ION_GPT", "Needs_Routed"], cwd=workspace, text=True, stderr=subprocess.DEVNULL)
    except Exception:
        patch_text = ""
    (staging / "patches/cumulative_candidate.patch").write_text(patch_text, encoding="utf-8")

    (staging / "reports").mkdir()
    (staging / "reports/validation_report.md").write_text(
        "# Validation Report\n\nGenerated by ion_continuity_transfer_package.\n\nRun package tests before treating this as release-ready.\n",
        encoding="utf-8",
    )
    (staging / "tests").mkdir()
    write_yaml(staging / "tests/validation_results.yaml", {"validation_results": {"builder_created_package": True, "accepted_state_claim": False}})
    (staging / "sources").mkdir()
    source_manifest = {
        "sources": [
            {"path": "ION_GPT/01_GPT_BUILDER_INPUTS/CURRENT_INSTRUCTIONS_TO_PASTE.md"},
            {"path": "ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"},
            {"path": "ION_Developement/ION/07_templates/continuity_transfer"},
        ]
    }
    write_yaml(staging / "sources/source_manifest.yaml", source_manifest)

    files = sorted(p for p in staging.rglob("*") if p.is_file())
    proof = {str(p.relative_to(staging)): sha256(p) for p in files}
    write_yaml(staging / "ion_proof_manifest.yaml", {"ion_proof_manifest": proof})

    manifest = {
        "schema_id": "ion.continuity_transfer_manifest.v0_1",
        "package_id": package_id,
        "ion_project_hash": project_hash,
        "project_hash_status": "assigned_candidate",
        "created_at_utc": timestamp,
        "source_workspace": str(workspace),
        "source_branch": branch,
        "source_commit": commit,
        "posture": "candidate_continuity_transfer",
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "settlement_required": True,
        "package_files": sorted(str(p.relative_to(staging)) for p in staging.rglob("*") if p.is_file()),
    }
    write_yaml(staging / "ion_continuity_transfer_manifest.yaml", manifest)

    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(staging.rglob("*")):
            if p.is_file():
                zf.write(p, p.relative_to(staging))
    file_count = len([p for p in staging.rglob("*") if p.is_file()])
    shutil.rmtree(staging)
    return {
        "ok": True,
        "package_id": package_id,
        "zip_path": str(zip_path),
        "zip_sha256": sha256(zip_path),
        "bytes": zip_path.stat().st_size,
        "file_count": file_count,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build an ION continuity transfer package")
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--timestamp")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = build_package(Path(args.workspace_root), Path(args.output_root), args.timestamp)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
