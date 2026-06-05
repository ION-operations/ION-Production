"""Source-bundle stage review for the ION Codex carrier domain.

This module consumes the commit-boundary audit and isolates the first safe
source/protocol/schema/test stage proposal. It never runs git add, git commit,
git push, GitHub mutation, raw Codex memory export, or ION settlement.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .ion_codex_commit_boundary_audit import (
    AUTHORITY_FALSE,
    OUTPUT_DIR as COMMIT_BOUNDARY_OUTPUT_DIR,
    build_codex_commit_boundary_audit,
)

SCHEMA_ID = "ion.codex_source_bundle_stage_review.v1"
STAGE_MANIFEST_SCHEMA_ID = "ion.codex_source_bundle_stage_manifest.v1"
READY_VERDICT = "ION_CODEX_SOURCE_BUNDLE_STAGE_REVIEW_READY"
PARTIAL_VERDICT = "ION_CODEX_SOURCE_BUNDLE_STAGE_REVIEW_PARTIAL"
BLOCKED_VERDICT = "ION_CODEX_SOURCE_BUNDLE_STAGE_REVIEW_BLOCKED"
WRITE_CONFIRMATION_TOKEN = "ION_CODEX_SOURCE_BUNDLE_STAGE_REVIEW_WRITE_CONFIRMED"

OUTPUT_DIR = COMMIT_BOUNDARY_OUTPUT_DIR
REVIEW_OUTPUT_PATH = OUTPUT_DIR / "CODEX_SOURCE_BUNDLE_STAGE_REVIEW.json"
STAGE_MANIFEST_OUTPUT_PATH = OUTPUT_DIR / "CODEX_SOURCE_BUNDLE_STAGE_MANIFEST.candidate.json"
PROTOCOL_PATH = Path("ION/02_architecture/CODEX_SOURCE_BUNDLE_STAGE_REVIEW_PROTOCOL.md")
SCHEMA_PATH = Path("ION/03_registry/ion_codex_source_bundle_stage_review.schema.json")
SOURCE_BUNDLE_ID = "source_protocol_schema_tests"

SOURCE_REVIEW_AUTHORITY_FALSE: dict[str, bool] = {
    **AUTHORITY_FALSE,
    "git_stage_authority": False,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_shell_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").is_file() and (path / "ION" / "REPO_AUTHORITY.md").is_file():
            return path
        if path.name == "ION" and (path / "REPO_AUTHORITY.md").is_file() and (path.parent / "pyproject.toml").is_file():
            return path.parent
    raise FileNotFoundError("Could not resolve ION shell root; expected pyproject.toml and ION/REPO_AUTHORITY.md")


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _bundle_by_id(audit: Mapping[str, Any], bundle_id: str) -> dict[str, Any]:
    for bundle in audit.get("bundles", []):
        if isinstance(bundle, dict) and bundle.get("bundle_id") == bundle_id:
            return dict(bundle)
    return {
        "bundle_id": bundle_id,
        "count": 0,
        "paths": [],
        "entries": [],
        "stage_decision": "not_present",
        "commit_timing": "not_present",
        "risk": "unknown",
        "description": "Bundle not present in commit-boundary audit.",
    }


def _excluded_bundles(audit: Mapping[str, Any]) -> list[dict[str, Any]]:
    excluded: list[dict[str, Any]] = []
    for bundle in audit.get("bundles", []):
        if not isinstance(bundle, dict) or bundle.get("bundle_id") == SOURCE_BUNDLE_ID:
            continue
        count = int(bundle.get("count") or 0)
        if count <= 0:
            continue
        excluded.append(
            {
                "bundle_id": bundle.get("bundle_id"),
                "path_count": count,
                "paths": list(bundle.get("paths", [])),
                "stage_decision": bundle.get("stage_decision"),
                "commit_timing": bundle.get("commit_timing"),
                "risk": bundle.get("risk"),
                "reason": _exclusion_reason(str(bundle.get("bundle_id"))),
            }
        )
    return excluded


def _exclusion_reason(bundle_id: str) -> str:
    return {
        "generated_projection_or_local_evidence": "Generated projections and local-PC evidence must be committed/regenerated after source settlement.",
        "deletion_review_required": "Deleted paths require a separate archive/cleanup packet.",
        "runtime_residue_exclude": "Runtime residue is local/transient and excluded by default.",
        "private_or_secret_risk_exclude": "Secret/private-risk paths block source staging until redacted and reclassified.",
        "untracked_review_required": "Untracked owner surfaces require operator classification before staging.",
        "preexisting_dirty_or_unknown": "Unknown owner-surface paths must not ride with the Codex carrier source bundle.",
    }.get(bundle_id, "Excluded from first source bundle by default.")


def _path_kind(path: str) -> str:
    if path.startswith(".codex/"):
        return "codex_native_config_or_hook"
    if path.startswith("ION/02_architecture/"):
        return "protocol_or_architecture_doc"
    if path.startswith("ION/03_registry/"):
        return "registry_or_schema"
    if path.startswith("ION/04_packages/kernel/"):
        return "kernel_source"
    if path.startswith("ION/tests/"):
        return "test_source"
    if path.startswith("ION/07_templates/"):
        return "template_source"
    if path.endswith(".py"):
        return "python_source"
    if path.endswith(".json"):
        return "json_source"
    if path.endswith(".md"):
        return "documentation_source"
    if path.endswith(".toml"):
        return "packaging_config"
    if path == ".gitignore":
        return "gitignore_policy"
    return "source_surface"


def _source_entries(source_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    entries = source_bundle.get("entries")
    if isinstance(entries, list) and entries:
        result = []
        for entry in entries:
            if isinstance(entry, dict):
                path = str(entry.get("path") or "")
                if path:
                    result.append({**entry, "path_kind": _path_kind(path), "stage_in_source_bundle": True})
        return result
    result = []
    for path in source_bundle.get("paths", []):
        if isinstance(path, str) and path:
            result.append({"path": path, "path_kind": _path_kind(path), "stage_in_source_bundle": True})
    return result


def _validation_commands(paths: Sequence[str]) -> list[str]:
    commands = [
        "git status --porcelain=v1 --branch -uall",
        "git diff --check",
    ]
    has_kernel = any(path.startswith("ION/04_packages/kernel/") for path in paths)
    has_tests = any(path.startswith("ION/tests/") for path in paths)
    has_codex = any("codex" in path.lower() for path in paths)
    if has_kernel or has_tests or has_codex:
        commands.append(
            "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ION/04_packages PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "
            "python3 -m pytest ION/tests/test_kernel_ion_codex_commit_boundary_audit.py "
            "ION/tests/test_kernel_ion_codex_source_bundle_stage_review.py "
            "ION/tests/test_kernel_ion_codex_carrier_os.py "
            "ION/tests/test_kernel_ion_mcp_local_bridge.py -q"
        )
    else:
        commands.append(
            "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=ION/04_packages PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "
            "python3 -m pytest ION/tests -q"
        )
    commands.extend(
        [
            "python3 -m py_compile $(git diff --name-only -- '*.py')",
            "review CODEX_SOURCE_BUNDLE_STAGE_MANIFEST.candidate.json before any git add",
        ]
    )
    return commands


def _chunk_paths(paths: Sequence[str], chunk_size: int = 80) -> list[list[str]]:
    return [list(paths[i : i + chunk_size]) for i in range(0, len(paths), chunk_size)]


def _candidate_stage_manifest(source_paths: Sequence[str], excluded: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    sorted_paths = sorted(dict.fromkeys(source_paths))
    return {
        "schema_id": STAGE_MANIFEST_SCHEMA_ID,
        "generated_at": _now(),
        "bundle_id": "codex_carrier_os_source_protocol_schema_tests",
        "source_path_count": len(sorted_paths),
        "source_paths": sorted_paths,
        "excluded_bundle_count": len(excluded),
        "excluded_bundle_summaries": [
            {
                "bundle_id": item.get("bundle_id"),
                "path_count": item.get("path_count"),
                "risk": item.get("risk"),
                "reason": item.get("reason"),
            }
            for item in excluded
        ],
        "candidate_git_add_chunks": [
            {
                "chunk_index": index,
                "path_count": len(chunk),
                "argv_preview": ["git", "add", "--", *chunk],
            }
            for index, chunk in enumerate(_chunk_paths(sorted_paths), start=1)
        ],
        "candidate_commit_message": "work/codex-carrier-os-source-bundle-stage-review",
        "validation_commands": _validation_commands(sorted_paths),
        "rule": "Proposal only. Do not run candidate git add chunks until operator/Steward review accepts the source bundle boundary.",
        **SOURCE_REVIEW_AUTHORITY_FALSE,
    }


def build_codex_source_bundle_stage_review(root: str | Path | None = None) -> dict[str, Any]:
    """Build a source-bundle stage proposal from the commit-boundary audit."""
    shell_root = _resolve_shell_root(root)
    audit = build_codex_commit_boundary_audit(shell_root)
    source_bundle = _bundle_by_id(audit, SOURCE_BUNDLE_ID)
    source_entries = _source_entries(source_bundle)
    source_paths = [entry["path"] for entry in source_entries]
    excluded = _excluded_bundles(audit)
    manifest = _candidate_stage_manifest(source_paths, excluded)

    blocking_findings: list[str] = []
    warning_findings: list[str] = []

    if not audit.get("ok"):
        blocking_findings.append("commit_boundary_audit_not_ok")
    for finding in audit.get("blocking_findings", []):
        blocking_findings.append(f"commit_boundary:{finding}")
    if not source_paths:
        blocking_findings.append("no_source_protocol_schema_test_paths_available")
    if int(audit.get("path_counts", {}).get("private_or_secret_risk_exclude", 0)) > 0:
        blocking_findings.append("private_or_secret_risk_paths_present")

    for finding in audit.get("warning_findings", []):
        warning_findings.append(f"commit_boundary:{finding}")
    for item in excluded:
        bundle_id = item.get("bundle_id")
        warning_findings.append(f"excluded_bundle_present:{bundle_id}:{item.get('path_count')}")

    source_ready = not blocking_findings and bool(source_paths)
    if blocking_findings:
        verdict = BLOCKED_VERDICT
    elif warning_findings:
        verdict = PARTIAL_VERDICT
    else:
        verdict = READY_VERDICT

    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "verdict": verdict,
        "ok": source_ready,
        "source_bundle_stage_ready": source_ready,
        "shell_root": str(shell_root),
        "protocol_ref": PROTOCOL_PATH.as_posix(),
        "schema_ref": SCHEMA_PATH.as_posix(),
        "output_ref": REVIEW_OUTPUT_PATH.as_posix(),
        "stage_manifest_ref": STAGE_MANIFEST_OUTPUT_PATH.as_posix(),
        "packet_ref": "PCKT-ION-CODEX-SOURCE-BUNDLE-STAGE-REVIEW-003",
        "commit_boundary_audit": {
            "verdict": audit.get("verdict"),
            "ok": audit.get("ok"),
            "ready_for_source_commit_bundle": audit.get("ready_for_source_commit_bundle"),
            "audit_ref": audit.get("output_ref"),
            "stage_manifest_ref": audit.get("stage_manifest_ref"),
            "path_counts": audit.get("path_counts"),
            "warning_findings": audit.get("warning_findings", []),
            "blocking_findings": audit.get("blocking_findings", []),
        },
        "source_bundle": {
            "bundle_id": SOURCE_BUNDLE_ID,
            "path_count": len(source_paths),
            "paths": sorted(dict.fromkeys(source_paths)),
            "entries": source_entries,
            "stage_decision": "candidate_for_first_source_bundle_after_review",
            "commit_timing": "first_source_commit_before_generated_evidence_bundle",
            "risk": "medium",
        },
        "excluded_bundles": excluded,
        "candidate_stage_manifest": manifest,
        "proof_obligations": [
            "Operator/Steward review of CODEX_SOURCE_BUNDLE_STAGE_MANIFEST.candidate.json",
            "git diff --check",
            "focused pytest for included kernel/tests/protocol paths",
            "path-level secret review before staging",
            "separate evidence/projection commit or regeneration after source commit",
            "no raw Codex context, runtime residue, generated projection, deletion cleanup, or unknown owner path in first source bundle",
        ],
        "recommended_next_action": "If reviewed, stage only source_paths from the candidate manifest; do not stage excluded bundles.",
        "blocking_findings": blocking_findings,
        "warning_findings": warning_findings,
        "non_claims": [
            "Source-bundle stage review does not stage, commit, push, or accept state.",
            "Candidate git add chunks are previews only.",
            "Generated local evidence and projections remain excluded from the first source bundle.",
            "Raw Codex context remains diagnostic continuity and is not promoted.",
        ],
        **SOURCE_REVIEW_AUTHORITY_FALSE,
    }


def write_codex_source_bundle_stage_review(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    review = build_codex_source_bundle_stage_review(shell_root)
    manifest = review["candidate_stage_manifest"]
    _write_json(shell_root / REVIEW_OUTPUT_PATH, review)
    _write_json(shell_root / STAGE_MANIFEST_OUTPUT_PATH, manifest)
    result = dict(review)
    result["written_paths"] = [REVIEW_OUTPUT_PATH.as_posix(), STAGE_MANIFEST_OUTPUT_PATH.as_posix()]
    return result


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review the Codex carrier source/protocol/schema/test bundle before staging.")
    parser.add_argument("--ion-root", default=".", help="Shell root or ION content root")
    parser.add_argument("--write", action="store_true", help="Write candidate source stage review and manifest artifacts")
    parser.add_argument("--confirmation", default=None, help=f"Required with --write: {WRITE_CONFIRMATION_TOKEN}")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.write and args.confirmation != WRITE_CONFIRMATION_TOKEN:
        payload = {
            "ok": False,
            "schema_id": "ion.codex_source_bundle_stage_review_write_refusal.v1",
            "refusal_class": "CONFIRMATION_REQUIRED",
            "required_confirmation": WRITE_CONFIRMATION_TOKEN,
            **SOURCE_REVIEW_AUTHORITY_FALSE,
        }
        if args.json:
            _print_json(payload)
        else:
            print(f"Refused: confirmation must be {WRITE_CONFIRMATION_TOKEN}", file=sys.stderr)
        return 3

    payload = write_codex_source_bundle_stage_review(args.ion_root) if args.write else build_codex_source_bundle_stage_review(args.ion_root)
    if args.json:
        _print_json(payload)
    else:
        print(payload["verdict"])
        for finding in [*payload.get("blocking_findings", []), *payload.get("warning_findings", [])]:
            print(f"- {finding}")
    return 0 if payload.get("source_bundle_stage_ready") else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
