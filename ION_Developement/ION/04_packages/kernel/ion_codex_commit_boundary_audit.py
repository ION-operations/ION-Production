"""Commit-boundary audit for the ION Codex carrier domain.

The Codex carrier can produce a mixed dirty tree: source patches, generated
carrier projections, local-PC evidence, runtime residue, archive cleanups, and
private/raw diagnostic lanes.  This module classifies that tree into candidate
stage bundles without staging, committing, pushing, reading secrets, or treating
any delta as accepted ION state.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

SCHEMA_ID = "ion.codex_commit_boundary_audit.v1"
STAGE_MANIFEST_SCHEMA_ID = "ion.codex_commit_stage_manifest.v1"
READY_VERDICT = "ION_CODEX_COMMIT_BOUNDARY_AUDIT_READY"
PARTIAL_VERDICT = "ION_CODEX_COMMIT_BOUNDARY_AUDIT_PARTIAL"
BLOCKED_VERDICT = "ION_CODEX_COMMIT_BOUNDARY_AUDIT_BLOCKED"
WRITE_CONFIRMATION_TOKEN = "ION_CODEX_COMMIT_BOUNDARY_AUDIT_WRITE_CONFIRMED"

OUTPUT_DIR = Path("ION/05_context/current/codex_carrier/commit_boundary")
AUDIT_OUTPUT_PATH = OUTPUT_DIR / "CODEX_COMMIT_BOUNDARY_AUDIT.json"
STAGE_MANIFEST_OUTPUT_PATH = OUTPUT_DIR / "CODEX_COMMIT_STAGE_MANIFEST.candidate.json"
PROTOCOL_PATH = Path("ION/02_architecture/CODEX_COMMIT_BOUNDARY_AUDIT_PROTOCOL.md")
SCHEMA_PATH = Path("ION/03_registry/ion_codex_commit_boundary_audit.schema.json")

AUTHORITY_FALSE: dict[str, bool] = {
    "accepted_state_authority": False,
    "production_authority": False,
    "live_execution_authority": False,
    "secrets_authority": False,
    "git_mutation_performed": False,
    "git_push_authority": False,
    "github_mutation_performed": False,
    "raw_codex_context_promoted": False,
}

SOURCE_PREFIXES: tuple[str, ...] = (
    ".codex/",
    "ION/02_architecture/",
    "ION/03_registry/",
    "ION/04_packages/kernel/",
    "ION/07_templates/",
    "ION/tests/",
)
SOURCE_EXACT: frozenset[str] = frozenset({
    ".gitignore",
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "pyproject.toml",
})
GENERATED_PREFIXES: tuple[str, ...] = (
    "ION/05_context/current/codex_carrier/",
    "ION/05_context/current/codex_local_pc/",
    "ION/05_context/current/agent_context_branches/",
    "ION/05_context/current/codex_solo/",
    "ION/05_context/current/ACTIVE_",
)
RUNTIME_EXCLUDE_PREFIXES: tuple[str, ...] = (
    ".git/",
    ".ion_private/",
    "ION/05_context/current/action_gateway/runtime/",
    "ION/05_context/current/chatgpt_connector/runtime/",
    "ION/05_context/current/codex_capsule_chat/response_runs/",
    "ION/05_context/runtime_state/",
)
SECRETISH_TOKENS: tuple[str, ...] = (
    ".env",
    "secret",
    "secrets",
    "credential",
    "credentials",
    "token",
    "oauth",
    "cookie",
    "session_cookie",
    "browser_profile",
    "cloudflared",
    ".cloudflared",
    "id_rsa",
    "private_key",
    "refresh_token",
)

BUNDLE_ORDER: tuple[str, ...] = (
    "source_protocol_schema_tests",
    "generated_projection_or_local_evidence",
    "deletion_review_required",
    "runtime_residue_exclude",
    "private_or_secret_risk_exclude",
    "untracked_review_required",
    "preexisting_dirty_or_unknown",
)

BUNDLE_META: dict[str, dict[str, str]] = {
    "source_protocol_schema_tests": {
        "stage_decision": "candidate_for_source_commit_after_tests",
        "commit_timing": "first_or_primary_commit",
        "risk": "medium",
        "description": "Source, protocol, schema, template, hook, and test paths that may form a narrow commit bundle.",
    },
    "generated_projection_or_local_evidence": {
        "stage_decision": "candidate_for_evidence_commit_or_regeneration_after_source_commit",
        "commit_timing": "after_source_commit_or_as_receipted_evidence_bundle",
        "risk": "medium",
        "description": "Generated carrier projections, branch-capsule records, and sanitized local-PC evidence.",
    },
    "deletion_review_required": {
        "stage_decision": "do_not_stage_until_deletion_packet_exists",
        "commit_timing": "separate_archive_cleanup_packet",
        "risk": "high",
        "description": "Deleted paths require explicit archive/cleanup intent and should not ride with carrier infrastructure commits.",
    },
    "runtime_residue_exclude": {
        "stage_decision": "exclude_from_commit",
        "commit_timing": "never_commit_runtime_residue_by_default",
        "risk": "high",
        "description": "Runtime state, bridge residues, response runs, private raw context, and local-only transient material.",
    },
    "private_or_secret_risk_exclude": {
        "stage_decision": "block_and_review_before_any_commit",
        "commit_timing": "never_commit_until_redacted_and_reclassified",
        "risk": "critical",
        "description": "Path names suggest credentials, tokens, browser profiles, tunnel material, or private logs.",
    },
    "untracked_review_required": {
        "stage_decision": "review_before_staging",
        "commit_timing": "only_after_owner_surface_is_known",
        "risk": "medium",
        "description": "Untracked files that are not clearly excluded or source-classified need owner classification.",
    },
    "preexisting_dirty_or_unknown": {
        "stage_decision": "do_not_stage_with_carrier_os_bundle",
        "commit_timing": "separate_packet_or_revert_decision_required",
        "risk": "high",
        "description": "Changed paths outside recognized owner surfaces; classify with the operator before staging.",
    },
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


def _run_git(shell_root: Path, args: Sequence[str], *, timeout: int = 8, max_output_chars: int = 12000) -> dict[str, Any]:
    command = ["git", *args]
    try:
        proc = subprocess.run(
            command,
            cwd=shell_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return {"command": command, "available": False, "returncode": None, "stdout": "", "stderr": "git_not_found"}
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "available": True,
            "returncode": None,
            "timeout": timeout,
            "stdout": (exc.stdout or "")[:max_output_chars] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[:max_output_chars] if isinstance(exc.stderr, str) else "timeout_expired",
        }
    return {
        "command": command,
        "available": True,
        "returncode": proc.returncode,
        "stdout": (proc.stdout or "")[:max_output_chars],
        "stderr": (proc.stderr or "")[:max_output_chars],
    }


def _path_after_status(raw_path: str) -> str:
    raw_path = raw_path.strip()
    if " -> " in raw_path:
        return raw_path.rsplit(" -> ", 1)[1].strip()
    return raw_path


def _parse_porcelain(stdout: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for line in stdout.splitlines():
        if not line.strip() or line.startswith("##"):
            continue
        status = line[:2]
        raw_path = line[3:] if len(line) > 3 else ""
        path = _path_after_status(raw_path)
        staged_status = status[0]
        unstaged_status = status[1]
        is_untracked = status == "??"
        is_deleted = "D" in status
        entries.append(
            {
                "status": status,
                "path": path,
                "raw_path": raw_path,
                "staged": staged_status not in {" ", "?"},
                "unstaged": unstaged_status not in {" ", "?"},
                "untracked": is_untracked,
                "deleted": is_deleted,
            }
        )
    return entries


def _starts_with_any(path: str, prefixes: Iterable[str]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


def _is_secretish(path: str) -> bool:
    lowered = path.lower()
    return any(token in lowered for token in SECRETISH_TOKENS)


def _classify_path(entry: Mapping[str, Any]) -> str:
    path = str(entry.get("path") or "")
    if _is_secretish(path):
        return "private_or_secret_risk_exclude"
    if _starts_with_any(path, RUNTIME_EXCLUDE_PREFIXES):
        return "runtime_residue_exclude"
    if bool(entry.get("deleted")):
        return "deletion_review_required"
    if path in SOURCE_EXACT or _starts_with_any(path, SOURCE_PREFIXES):
        return "source_protocol_schema_tests"
    if _starts_with_any(path, GENERATED_PREFIXES):
        return "generated_projection_or_local_evidence"
    if bool(entry.get("untracked")):
        return "untracked_review_required"
    return "preexisting_dirty_or_unknown"


def _bundle_entries(entries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {bundle_id: [] for bundle_id in BUNDLE_ORDER}
    for entry in entries:
        bundle_id = _classify_path(entry)
        grouped.setdefault(bundle_id, []).append(dict(entry))

    bundles: list[dict[str, Any]] = []
    for bundle_id in BUNDLE_ORDER:
        items = grouped.get(bundle_id, [])
        meta = BUNDLE_META[bundle_id]
        bundles.append(
            {
                "bundle_id": bundle_id,
                "count": len(items),
                "paths": [item["path"] for item in items],
                "entries": items,
                **meta,
            }
        )
    return bundles


def _stage_manifest_from_bundles(bundles: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    stage_groups = []
    for bundle in bundles:
        paths = list(bundle.get("paths", [])) if isinstance(bundle.get("paths"), list) else []
        if not paths:
            continue
        stage_groups.append(
            {
                "bundle_id": bundle["bundle_id"],
                "path_count": len(paths),
                "paths": paths,
                "stage_decision": bundle["stage_decision"],
                "commit_timing": bundle["commit_timing"],
                "risk": bundle["risk"],
            }
        )
    return {
        "schema_id": STAGE_MANIFEST_SCHEMA_ID,
        "generated_at": _now(),
        "stage_groups": stage_groups,
        "rule": "This is a proposal only. It does not run git add, git commit, git push, or settlement.",
        "recommended_commit_order": [
            "source_protocol_schema_tests",
            "generated_projection_or_local_evidence",
            "deletion_review_required only with separate cleanup packet",
        ],
        **AUTHORITY_FALSE,
    }


def _branch_from_status(status_stdout: str) -> str | None:
    for line in status_stdout.splitlines():
        if line.startswith("## "):
            value = line[3:].strip()
            return value.split("...", 1)[0].strip() or None
    return None


def build_codex_commit_boundary_audit(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    git_dir = shell_root / ".git"

    status = _run_git(shell_root, ["status", "--porcelain=v1", "--branch", "-uall"], timeout=8, max_output_chars=100000)
    head = _run_git(shell_root, ["rev-parse", "--short", "HEAD"], timeout=5, max_output_chars=1000)
    diff_check = _run_git(shell_root, ["diff", "--check"], timeout=10, max_output_chars=16000)
    cached_diff_check = _run_git(shell_root, ["diff", "--cached", "--check"], timeout=10, max_output_chars=16000)

    git_available = bool(status.get("available") and status.get("returncode") == 0 and git_dir.exists())
    entries = _parse_porcelain(status.get("stdout", "")) if git_available else []
    bundles = _bundle_entries(entries)
    manifest = _stage_manifest_from_bundles(bundles)

    counts = {bundle["bundle_id"]: bundle["count"] for bundle in bundles}
    blocking_findings: list[str] = []
    warning_findings: list[str] = []

    if not git_available:
        blocking_findings.append("git_status_unavailable_or_not_a_git_worktree")
    if diff_check.get("returncode") not in {0, None}:
        blocking_findings.append("git_diff_check_failed")
    if cached_diff_check.get("returncode") not in {0, None}:
        blocking_findings.append("git_diff_cached_check_failed")
    if counts.get("private_or_secret_risk_exclude", 0):
        blocking_findings.append("private_or_secret_risk_paths_present")
    if counts.get("runtime_residue_exclude", 0):
        warning_findings.append("runtime_residue_paths_present")
    if counts.get("deletion_review_required", 0):
        warning_findings.append("deleted_paths_require_separate_cleanup_packet")
    if counts.get("preexisting_dirty_or_unknown", 0):
        warning_findings.append("unknown_owner_surface_paths_present")
    if counts.get("untracked_review_required", 0):
        warning_findings.append("untracked_paths_require_owner_review")

    if blocking_findings:
        verdict = BLOCKED_VERDICT
        ready_for_source_commit = False
    elif warning_findings:
        verdict = PARTIAL_VERDICT
        ready_for_source_commit = counts.get("source_protocol_schema_tests", 0) > 0
    else:
        verdict = READY_VERDICT
        ready_for_source_commit = counts.get("source_protocol_schema_tests", 0) > 0

    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "verdict": verdict,
        "ok": git_available and not blocking_findings,
        "ready_for_source_commit_bundle": ready_for_source_commit,
        "shell_root": str(shell_root),
        "protocol_ref": PROTOCOL_PATH.as_posix(),
        "schema_ref": SCHEMA_PATH.as_posix(),
        "output_ref": AUDIT_OUTPUT_PATH.as_posix(),
        "stage_manifest_ref": STAGE_MANIFEST_OUTPUT_PATH.as_posix(),
        "packet_ref": "PCKT-ION-CODEX-COMMIT-BOUNDARY-AUDIT-001",
        "git": {
            "available": git_available,
            "git_dir_present": git_dir.exists(),
            "branch": _branch_from_status(status.get("stdout", "")),
            "head_short": head.get("stdout", "").strip() if head.get("returncode") == 0 else None,
            "dirty": bool(entries),
            "porcelain_count": len(entries),
            "diff_check_returncode": diff_check.get("returncode"),
            "diff_check_stderr": diff_check.get("stderr", ""),
            "diff_check_stdout": diff_check.get("stdout", ""),
            "cached_diff_check_returncode": cached_diff_check.get("returncode"),
        },
        "path_counts": counts,
        "bundles": bundles,
        "candidate_stage_manifest": manifest,
        "proof_obligations": [
            "git status --porcelain=v1 --branch -uall",
            "git diff --check",
            "focused pytest for source bundle",
            "secret/path review for excluded and generated evidence bundles",
            "separate packet for deletion/archive cleanup paths",
        ],
        "blocking_findings": blocking_findings,
        "warning_findings": warning_findings,
        "non_claims": [
            "This audit does not stage, commit, push, or accept state.",
            "This audit classifies path-level Git changes; it does not read raw Codex memories or secrets.",
            "Stage manifests are proposals until operator/Steward settlement.",
            "Generated local-PC evidence remains candidate until proof-gated and receipted.",
        ],
        **AUTHORITY_FALSE,
    }


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_codex_commit_boundary_audit(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    audit = build_codex_commit_boundary_audit(shell_root)
    manifest = audit["candidate_stage_manifest"]
    _write_json(shell_root / AUDIT_OUTPUT_PATH, audit)
    _write_json(shell_root / STAGE_MANIFEST_OUTPUT_PATH, manifest)
    result = dict(audit)
    result["written_paths"] = [AUDIT_OUTPUT_PATH.as_posix(), STAGE_MANIFEST_OUTPUT_PATH.as_posix()]
    return result


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Classify the Codex/ION dirty tree into lawful commit-boundary bundles.")
    parser.add_argument("--ion-root", default=".", help="Shell root or ION content root")
    parser.add_argument("--write", action="store_true", help="Write candidate audit and stage manifest artifacts")
    parser.add_argument("--confirmation", default=None, help=f"Required with --write: {WRITE_CONFIRMATION_TOKEN}")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.write and args.confirmation != WRITE_CONFIRMATION_TOKEN:
        payload = {
            "ok": False,
            "schema_id": "ion.codex_commit_boundary_audit_write_refusal.v1",
            "refusal_class": "CONFIRMATION_REQUIRED",
            "required_confirmation": WRITE_CONFIRMATION_TOKEN,
            **AUTHORITY_FALSE,
        }
        if args.json:
            _print_json(payload)
        else:
            print(f"Refused: confirmation must be {WRITE_CONFIRMATION_TOKEN}", file=sys.stderr)
        return 3

    payload = write_codex_commit_boundary_audit(args.ion_root) if args.write else build_codex_commit_boundary_audit(args.ion_root)
    if args.json:
        _print_json(payload)
    else:
        print(payload["verdict"])
        for finding in [*payload.get("blocking_findings", []), *payload.get("warning_findings", [])]:
            print(f"- {finding}")
    return 0 if payload.get("ok") else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
