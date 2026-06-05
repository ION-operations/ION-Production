"""Git root-normalization preview for the active ION shell root.

This module projects the current legacy tracked-path model onto the active
root layout. It does not stage, commit, push, move, delete, restart services,
read secret-risk contents, or claim accepted state.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence

from .ion_codex_commit_boundary_audit import (
    AUTHORITY_FALSE,
    _is_secretish,
    _resolve_git_root,
    _resolve_shell_root,
    _run_git,
    build_codex_commit_boundary_audit,
)

SCHEMA_ID = "ion.git_root_normalization_preview.v1"
WRITE_CONFIRMATION_TOKEN = "ION_GIT_ROOT_NORMALIZATION_PREVIEW_WRITE_CONFIRMED"

OUTPUT_DIR = Path("ION/05_context/current/repo_organization")
PREVIEW_OUTPUT_PATH = OUTPUT_DIR / "GIT_ROOT_NORMALIZATION_PREVIEW.candidate.json"
PREVIEW_SUMMARY_OUTPUT_PATH = OUTPUT_DIR / "GIT_ROOT_NORMALIZATION_PREVIEW_SUMMARY.candidate.json"
PREVIEW_MARKDOWN_PATH = OUTPUT_DIR / "GIT_ROOT_NORMALIZATION_PREVIEW.candidate.md"
PROTOCOL_PATH = Path("ION/02_architecture/ION_GIT_ROOT_NORMALIZATION_PREVIEW_PROTOCOL.md")
SCHEMA_PATH = Path("ION/03_registry/ion_git_root_normalization_preview.schema.json")

LEGACY_PREFIX = "ION_Developement/"
ACTIVE_PREFIX = ""
CHUNK_SIZE = 80

NORMALIZATION_AUTHORITY_FALSE: dict[str, bool] = {
    **AUTHORITY_FALSE,
    "git_stage_authority": False,
    "git_delete_authority": False,
    "git_move_authority": False,
    "service_restart_authority": False,
    "secret_contents_read_or_printed": False,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _git_path_prefix(shell_root: Path, git_root: Path | None) -> str:
    if not git_root:
        return ""
    try:
        relative = shell_root.relative_to(git_root).as_posix()
    except ValueError:
        return ""
    return "" if relative == "." else relative.strip("/")


def _with_git_prefix(path: str, git_prefix: str) -> str:
    return f"{git_prefix}/{path}" if git_prefix else path


def _legacy_git_prefix(git_prefix: str) -> str:
    return _with_git_prefix(LEGACY_PREFIX.rstrip("/"), git_prefix)


def _tracked_legacy_paths(git_root: Path, git_prefix: str) -> list[str]:
    result = _run_git(
        git_root,
        ["ls-files", "-z", "--", _legacy_git_prefix(git_prefix)],
        timeout=20,
        max_output_chars=None,
    )
    if result.get("returncode") != 0:
        return []
    return [path for path in str(result.get("stdout") or "").split("\0") if path]


def _active_path_from_tracked_git_path(tracked_path: str, git_prefix: str) -> str | None:
    legacy_prefix = _legacy_git_prefix(git_prefix).rstrip("/") + "/"
    if not tracked_path.startswith(legacy_prefix):
        return None
    return tracked_path[len(legacy_prefix) :]


def _git_blob_bytes(git_root: Path, tracked_path: str) -> bytes | None:
    proc = subprocess.run(
        ["git", "show", f"HEAD:{tracked_path}"],
        cwd=git_root,
        check=False,
        capture_output=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _compare_tracked_to_active(git_root: Path, shell_root: Path, tracked_path: str, active_path: str) -> dict[str, Any]:
    active_file = shell_root / active_path
    risk_path = _is_secretish(tracked_path) or _is_secretish(active_path)
    base: dict[str, Any] = {
        "tracked_path": tracked_path,
        "active_path": active_path,
        "active_exists": active_file.exists(),
        "path_risk": risk_path,
    }
    if not active_file.exists():
        return {**base, "classification": "active_missing_deletion_review_candidate"}
    if risk_path:
        return {
            **base,
            "classification": "active_exists_path_risk_not_hashed",
            "content_compared": False,
            "reason": "path_name_requires_private_or_secret_review",
        }
    if not active_file.is_file():
        return {**base, "classification": "active_exists_not_file", "content_compared": False}
    tracked_bytes = _git_blob_bytes(git_root, tracked_path)
    if tracked_bytes is None:
        return {**base, "classification": "tracked_blob_unavailable", "content_compared": False}
    active_bytes = active_file.read_bytes()
    tracked_hash = _sha256_bytes(tracked_bytes)
    active_hash = _sha256_bytes(active_bytes)
    classification = (
        "same_content_relocation_candidate"
        if tracked_hash == active_hash
        else "changed_content_relocation_candidate"
    )
    return {
        **base,
        "classification": classification,
        "content_compared": True,
        "tracked_sha256": tracked_hash,
        "active_sha256": active_hash,
    }


def _bundle(audit: Mapping[str, Any], bundle_id: str) -> Mapping[str, Any]:
    for bundle in audit.get("bundles", []):
        if isinstance(bundle, Mapping) and bundle.get("bundle_id") == bundle_id:
            return bundle
    return {"paths": [], "count": 0}


def _top_families(paths: Sequence[str], limit: int = 25) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    for path in paths:
        family = path.split("/", 1)[0] if "/" in path else path
        counts[family] += 1
    return [{"family": family, "count": count} for family, count in counts.most_common(limit)]


def _source_family(path: str) -> str:
    parts = path.split("/")
    if len(parts) >= 3 and parts[0] == "ION":
        return "/".join(parts[:3])
    if len(parts) >= 2:
        return "/".join(parts[:2])
    return path


def _secret_risk_category(path: str) -> str:
    lowered = path.lower()
    if "cloudflared" in lowered:
        return "cloudflared_path_review"
    if "auth_token" in lowered:
        return "auth_token_path_review"
    if "access_token" in lowered or "refresh_token" in lowered:
        return "oauth_token_path_review"
    if "api_key" in lowered or "secret_key" in lowered or "client_secret" in lowered:
        return "api_secret_path_review"
    if "browser_profile" in lowered or "cookie" in lowered:
        return "browser_profile_or_cookie_path_review"
    if ".env" in lowered:
        return "env_file_path_review"
    if ".ssh" in lowered or "id_rsa" in lowered or lowered.endswith((".pem", ".key")):
        return "ssh_or_key_material_path_review"
    return "private_or_secret_path_review"


def _chunk_paths(paths: Sequence[str], chunk_size: int = CHUNK_SIZE) -> list[list[str]]:
    return [list(paths[i : i + chunk_size]) for i in range(0, len(paths), chunk_size)]


def _candidate_chunks(
    mapped_entries: Sequence[Mapping[str, Any]],
    deletion_paths: Sequence[str],
    new_active_source_paths: Sequence[str],
) -> dict[str, Any]:
    same = sorted(
        str(item["active_path"])
        for item in mapped_entries
        if item.get("classification") == "same_content_relocation_candidate"
    )
    changed = sorted(
        str(item["active_path"])
        for item in mapped_entries
        if item.get("classification") == "changed_content_relocation_candidate"
    )
    same_tracked = sorted(
        str(item["tracked_path"])
        for item in mapped_entries
        if item.get("classification") == "same_content_relocation_candidate"
    )
    changed_tracked = sorted(
        str(item["tracked_path"])
        for item in mapped_entries
        if item.get("classification") == "changed_content_relocation_candidate"
    )
    path_risk_tracked = sorted(
        str(item["tracked_path"])
        for item in mapped_entries
        if item.get("classification") == "active_exists_path_risk_not_hashed"
    )
    active_missing_tracked = sorted(
        str(item["tracked_path"])
        for item in mapped_entries
        if item.get("classification") == "active_missing_deletion_review_candidate"
    )
    deleted = sorted(dict.fromkeys(deletion_paths))
    new_source = sorted(dict.fromkeys(new_active_source_paths))
    return {
        "new_active_source_add_chunks": [
            {"chunk_index": index, "path_count": len(chunk), "argv_preview": ["git", "add", "--", *chunk]}
            for index, chunk in enumerate(_chunk_paths(new_source), start=1)
        ],
        "same_content_active_add_chunks": [
            {"chunk_index": index, "path_count": len(chunk), "argv_preview": ["git", "add", "--", *chunk]}
            for index, chunk in enumerate(_chunk_paths(same), start=1)
        ],
        "changed_content_active_add_chunks": [
            {"chunk_index": index, "path_count": len(chunk), "argv_preview": ["git", "add", "--", *chunk]}
            for index, chunk in enumerate(_chunk_paths(changed), start=1)
        ],
        "same_content_tracked_delete_chunks": [
            {"chunk_index": index, "path_count": len(chunk), "argv_preview": ["git", "rm", "--", *chunk]}
            for index, chunk in enumerate(_chunk_paths(same_tracked), start=1)
        ],
        "changed_content_tracked_delete_review_chunks": [
            {"chunk_index": index, "path_count": len(chunk), "argv_preview": ["git", "rm", "--", *chunk]}
            for index, chunk in enumerate(_chunk_paths(changed_tracked), start=1)
        ],
        "path_risk_tracked_delete_review_chunks": [
            {"chunk_index": index, "path_count": len(chunk), "argv_preview": ["git", "rm", "--", *chunk]}
            for index, chunk in enumerate(_chunk_paths(path_risk_tracked), start=1)
        ],
        "active_missing_tracked_delete_review_chunks": [
            {"chunk_index": index, "path_count": len(chunk), "argv_preview": ["git", "rm", "--", *chunk]}
            for index, chunk in enumerate(_chunk_paths(active_missing_tracked), start=1)
        ],
        "tracked_missing_delete_review_chunks": [
            {"chunk_index": index, "path_count": len(chunk), "argv_preview": ["git", "rm", "--", *chunk]}
            for index, chunk in enumerate(_chunk_paths(deleted), start=1)
        ],
        "truncated": False,
        "rule": "Preview only. Do not run candidate chunks until root-normalization, path-risk, source-stage, and deletion packets are accepted as applicable.",
    }


def build_git_root_normalization_preview(root: str | Path | None = None) -> dict[str, Any]:
    """Build a read-only preview for legacy tracked paths under ION_Developement."""
    shell_root = _resolve_shell_root(root)
    git_root = _resolve_git_root(shell_root)
    audit = build_codex_commit_boundary_audit(shell_root)
    git_prefix = _git_path_prefix(shell_root, git_root)

    tracked_paths = _tracked_legacy_paths(git_root, git_prefix) if git_root else []
    mapped_entries: list[dict[str, Any]] = []
    for tracked_path in tracked_paths:
        active_path = _active_path_from_tracked_git_path(tracked_path, git_prefix)
        if active_path is None:
            continue
        mapped_entries.append(_compare_tracked_to_active(git_root, shell_root, tracked_path, active_path))

    mapped_active_paths = {str(item["active_path"]) for item in mapped_entries}
    source_paths = sorted(dict.fromkeys(_bundle(audit, "source_protocol_schema_tests").get("paths", [])))
    new_active_source_paths = [path for path in source_paths if path not in mapped_active_paths]
    deletion_paths = sorted(dict.fromkeys(_bundle(audit, "deletion_review_required").get("paths", [])))
    secret_paths = sorted(dict.fromkeys(_bundle(audit, "private_or_secret_risk_exclude").get("paths", [])))

    classification_counts = Counter(str(item.get("classification")) for item in mapped_entries)
    new_source_family_counts = Counter(_source_family(path) for path in new_active_source_paths)
    secret_categories = Counter(_secret_risk_category(path) for path in secret_paths)
    ion_development_deletions = [path for path in deletion_paths if path.startswith(LEGACY_PREFIX)]

    root_file_map = [
        item
        for item in mapped_entries
        if "/" not in str(item.get("active_path") or "")
        or str(item.get("active_path") or "") in {"README.md", "SECURITY.md", "pyproject.toml", "ION_CONTEXT_CAPSULE.yaml"}
    ]

    status_ok = bool(git_root and audit.get("git", {}).get("available"))
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "status": "candidate_preview_only",
        "ok": status_ok,
        "root_normalization_ready": False,
        "root": str(shell_root),
        "git_root": str(git_root) if git_root else None,
        "protocol_ref": PROTOCOL_PATH.as_posix(),
        "schema_ref": SCHEMA_PATH.as_posix(),
        "output_ref": PREVIEW_OUTPUT_PATH.as_posix(),
        "summary_ref": PREVIEW_SUMMARY_OUTPUT_PATH.as_posix(),
        "markdown_ref": PREVIEW_MARKDOWN_PATH.as_posix(),
        "authority_proof": {
            "pyproject_toml_present": (shell_root / "pyproject.toml").is_file(),
            "repo_authority_present": (shell_root / "ION" / "REPO_AUTHORITY.md").is_file(),
        },
        "tracked_to_active_map_summary": {
            "tracked_prefix": _legacy_git_prefix(git_prefix),
            "active_prefix": ACTIVE_PREFIX,
            "tracked_path_count": len(mapped_entries),
            "classification_counts": dict(sorted(classification_counts.items())),
            "top_active_prefixes": _top_families([str(item["active_path"]) for item in mapped_entries]),
        },
        "root_file_map": root_file_map,
        "tracked_to_active_path_map": sorted(mapped_entries, key=lambda item: str(item["tracked_path"])),
        "new_active_source_summary": {
            "path_count": len(new_active_source_paths),
            "by_family": [
                {"family": family, "count": count}
                for family, count in new_source_family_counts.most_common(25)
            ],
        },
        "new_active_source_paths": new_active_source_paths,
        "secret_risk_path_review": {
            "path_count": len(secret_paths),
            "path_content_read": False,
            "categories": [
                {"category": category, "count": count}
                for category, count in secret_categories.most_common()
            ],
        },
        "deletion_review_manifest": {
            "path_count": len(deletion_paths),
            "top_families": _top_families(deletion_paths),
            "ion_development_top_families": _top_families(ion_development_deletions),
            "sample_paths": deletion_paths[:80],
        },
        "candidate_preview_chunks": _candidate_chunks(mapped_entries, deletion_paths, new_active_source_paths),
        "stop_conditions": [
            "Do not run git add . or git add -A.",
            "Do not stage private/secret-risk paths until path-level review clears them.",
            "Do not stage deletion paths without a deletion/archive packet.",
            "Do not use the parent /home/sev Git fallback as the project root.",
            "Do not push or claim accepted state from this preview.",
            "Do not read or print secret contents while classifying paths.",
        ],
        "mutation_boundary": {
            "git_staged": False,
            "git_committed": False,
            "git_pushed": False,
            "deleted_or_moved_files": False,
            "service_restarted": False,
            "secret_contents_read_or_printed": False,
            "accepted_state_claimed": False,
        },
        "non_claims": [
            "This preview does not normalize the repository root.",
            "This preview does not certify secret-risk paths as safe.",
            "This preview does not approve deletion of legacy tracked paths.",
            "This preview does not stage, commit, push, move, or delete files.",
        ],
        **NORMALIZATION_AUTHORITY_FALSE,
    }


def render_git_root_normalization_preview_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload.get("tracked_to_active_map_summary", {})
    class_counts = summary.get("classification_counts", {}) if isinstance(summary, Mapping) else {}
    root_files = payload.get("root_file_map", [])
    changed_samples = [
        item
        for item in payload.get("tracked_to_active_path_map", [])
        if isinstance(item, Mapping) and item.get("classification") == "changed_content_relocation_candidate"
    ][:30]
    new_summary = payload.get("new_active_source_summary", {})
    secret_review = payload.get("secret_risk_path_review", {})
    deletion_review = payload.get("deletion_review_manifest", {})
    preview_chunks = payload.get("candidate_preview_chunks", {})
    new_source_chunks = (
        preview_chunks.get("new_active_source_add_chunks", []) if isinstance(preview_chunks, Mapping) else []
    )
    same_delete_chunks = (
        preview_chunks.get("same_content_tracked_delete_chunks", []) if isinstance(preview_chunks, Mapping) else []
    )
    changed_delete_chunks = (
        preview_chunks.get("changed_content_tracked_delete_review_chunks", [])
        if isinstance(preview_chunks, Mapping)
        else []
    )
    path_risk_delete_chunks = (
        preview_chunks.get("path_risk_tracked_delete_review_chunks", []) if isinstance(preview_chunks, Mapping) else []
    )
    active_missing_delete_chunks = (
        preview_chunks.get("active_missing_tracked_delete_review_chunks", [])
        if isinstance(preview_chunks, Mapping)
        else []
    )

    lines = [
        f"# Git Root Normalization Preview - {payload.get('generated_at')}",
        "",
        "Status: candidate preview only. No Git staging, commit, push, move, delete, service restart, production action, live action, secrets access, or accepted-state claim.",
        "",
        "## Summary",
        "",
        f"- Tracked `{summary.get('tracked_prefix', LEGACY_PREFIX)}` paths mapped: `{summary.get('tracked_path_count', 0)}`",
    ]
    for key in sorted(class_counts):
        lines.append(f"- `{key}`: `{class_counts[key]}`")
    lines.extend(
        [
            f"- New active source/protocol/schema/test paths without tracked counterpart: `{new_summary.get('path_count', 0)}`",
            f"- Private/secret-risk path names requiring review: `{secret_review.get('path_count', 0)}`",
            f"- Deletion-review paths in current audit: `{deletion_review.get('path_count', 0)}`",
            "",
            "## Root File Map",
            "",
        ]
    )
    for item in root_files:
        if isinstance(item, Mapping):
            lines.append(
                f"- `{item.get('tracked_path')}` -> `{item.get('active_path')}`: `{item.get('classification')}`"
            )
    lines.extend(["", "## Changed Content Samples", ""])
    for item in changed_samples:
        lines.append(f"- `{item.get('tracked_path')}` -> `{item.get('active_path')}`")
    lines.extend(["", "## New Active Source Families", ""])
    for item in new_summary.get("by_family", []):
        if isinstance(item, Mapping):
            lines.append(f"- `{item.get('family')}`: `{item.get('count')}`")
    lines.extend(["", "## New Active Source Preview Chunks", ""])
    if new_source_chunks:
        for item in new_source_chunks:
            if isinstance(item, Mapping):
                lines.append(f"- Chunk `{item.get('chunk_index')}`: `{item.get('path_count')}` paths")
    else:
        lines.append("- No new active source chunks.")
    lines.extend(
        [
            "",
            "## Root Normalization Delete Preview",
            "",
            f"- Same-content old-root delete chunks: `{len(same_delete_chunks)}` chunks / `{_chunk_path_count(same_delete_chunks)}` paths",
            f"- Changed-content delete review chunks: `{len(changed_delete_chunks)}` chunks / `{_chunk_path_count(changed_delete_chunks)}` paths",
            f"- Path-risk delete review chunks: `{len(path_risk_delete_chunks)}` chunks / `{_chunk_path_count(path_risk_delete_chunks)}` paths",
            f"- Active-missing delete review chunks: `{len(active_missing_delete_chunks)}` chunks / `{_chunk_path_count(active_missing_delete_chunks)}` paths",
            "",
            "Exact `git rm` argv previews stay in the ignored full machine preview. Do not run them without an accepted deletion/archive packet.",
        ]
    )
    lines.extend(
        [
            "",
            "## Secret-Risk Path Review",
            "",
            "Path names only were classified. Contents were not read or printed.",
        ]
    )
    for item in secret_review.get("categories", []):
        if isinstance(item, Mapping):
            lines.append(f"- `{item.get('category')}`: `{item.get('count')}`")
    lines.extend(["", "## Deletion Review Top Families", ""])
    for item in deletion_review.get("top_families", []):
        if isinstance(item, Mapping):
            lines.append(f"- `{item.get('family')}`: `{item.get('count')}`")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "Keep staging blocked. The next lawful move is operator review of this preview plus a deletion/archive packet and path-level review of the private/secret-risk path names. Use only explicit path chunks after approval; never `git add .` or `git add -A`.",
            "",
            f"Machine preview: `{payload.get('output_ref')}`",
            "",
        ]
    )
    return "\n".join(lines)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _chunk_summary(chunks: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for chunk in chunks:
        argv = chunk.get("argv_preview", [])
        paths = argv[3:] if isinstance(argv, list) else []
        summary.append(
            {
                "chunk_index": chunk.get("chunk_index"),
                "path_count": chunk.get("path_count"),
                "first_path": paths[0] if paths else None,
                "last_path": paths[-1] if paths else None,
            }
        )
    return summary


def _chunk_path_count(chunks: Sequence[Mapping[str, Any]]) -> int:
    return sum(int(chunk.get("path_count", 0)) for chunk in chunks if isinstance(chunk, Mapping))


def compact_git_root_normalization_preview_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    deletion_review = dict(payload.get("deletion_review_manifest", {}))
    deletion_review.pop("sample_paths", None)
    preview_chunks = payload.get("candidate_preview_chunks", {})
    new_source_chunks = (
        preview_chunks.get("new_active_source_add_chunks", []) if isinstance(preview_chunks, Mapping) else []
    )
    same_delete_chunks = (
        preview_chunks.get("same_content_tracked_delete_chunks", []) if isinstance(preview_chunks, Mapping) else []
    )
    changed_delete_chunks = (
        preview_chunks.get("changed_content_tracked_delete_review_chunks", [])
        if isinstance(preview_chunks, Mapping)
        else []
    )
    path_risk_delete_chunks = (
        preview_chunks.get("path_risk_tracked_delete_review_chunks", []) if isinstance(preview_chunks, Mapping) else []
    )
    active_missing_delete_chunks = (
        preview_chunks.get("active_missing_tracked_delete_review_chunks", [])
        if isinstance(preview_chunks, Mapping)
        else []
    )
    return {
        "schema_id": "ion.git_root_normalization_preview_summary.v1",
        "generated_at": payload.get("generated_at"),
        "status": payload.get("status"),
        "ok": payload.get("ok"),
        "root_normalization_ready": payload.get("root_normalization_ready"),
        "root": payload.get("root"),
        "git_root": payload.get("git_root"),
        "full_preview_ref": payload.get("output_ref"),
        "markdown_ref": payload.get("markdown_ref"),
        "protocol_ref": payload.get("protocol_ref"),
        "schema_ref": payload.get("schema_ref"),
        "authority_proof": payload.get("authority_proof"),
        "tracked_to_active_map_summary": payload.get("tracked_to_active_map_summary"),
        "root_file_map": payload.get("root_file_map"),
        "new_active_source_summary": payload.get("new_active_source_summary"),
        "new_active_source_stage_preview": {
            "path_count": _chunk_path_count(new_source_chunks),
            "chunks": new_source_chunks,
            "rule": "Preview only. Do not run git add from this summary until path-risk and source-stage packets are accepted.",
        },
        "root_normalization_delete_preview": {
            "same_content": {
                "path_count": _chunk_path_count(same_delete_chunks),
                "chunk_count": len(same_delete_chunks),
                "chunks": _chunk_summary(same_delete_chunks),
            },
            "changed_content_review": {
                "path_count": _chunk_path_count(changed_delete_chunks),
                "chunk_count": len(changed_delete_chunks),
                "chunks": _chunk_summary(changed_delete_chunks),
            },
            "path_risk_review": {
                "path_count": _chunk_path_count(path_risk_delete_chunks),
                "chunk_count": len(path_risk_delete_chunks),
                "chunks": _chunk_summary(path_risk_delete_chunks),
            },
            "active_missing_review": {
                "path_count": _chunk_path_count(active_missing_delete_chunks),
                "chunk_count": len(active_missing_delete_chunks),
                "chunks": _chunk_summary(active_missing_delete_chunks),
            },
            "full_chunk_argv_ref": payload.get("output_ref"),
            "rule": "Preview only. Do not run git rm from this summary. Same-content delete chunks still require explicit deletion/archive packet approval; review chunks are stop-gated.",
        },
        "secret_risk_path_review": payload.get("secret_risk_path_review"),
        "deletion_review_manifest": deletion_review,
        "stop_conditions": payload.get("stop_conditions"),
        "mutation_boundary": payload.get("mutation_boundary"),
        "non_claims": payload.get("non_claims"),
        **NORMALIZATION_AUTHORITY_FALSE,
    }


def write_git_root_normalization_preview(root: str | Path | None = None) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    payload = build_git_root_normalization_preview(shell_root)
    summary = compact_git_root_normalization_preview_summary(payload)
    _write_json(shell_root / PREVIEW_OUTPUT_PATH, payload)
    _write_json(shell_root / PREVIEW_SUMMARY_OUTPUT_PATH, summary)
    markdown = render_git_root_normalization_preview_markdown(payload)
    (shell_root / PREVIEW_MARKDOWN_PATH).parent.mkdir(parents=True, exist_ok=True)
    (shell_root / PREVIEW_MARKDOWN_PATH).write_text(markdown, encoding="utf-8")
    result = dict(payload)
    result["written_paths"] = [
        PREVIEW_OUTPUT_PATH.as_posix(),
        PREVIEW_SUMMARY_OUTPUT_PATH.as_posix(),
        PREVIEW_MARKDOWN_PATH.as_posix(),
    ]
    return result


def _print_json(payload: Mapping[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview ION Git root normalization without mutating Git state.")
    parser.add_argument("--ion-root", default=".", help="Shell root or ION content root")
    parser.add_argument("--write", action="store_true", help="Write candidate root-normalization preview artifacts")
    parser.add_argument("--confirmation", default=None, help=f"Required with --write: {WRITE_CONFIRMATION_TOKEN}")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.write and args.confirmation != WRITE_CONFIRMATION_TOKEN:
        payload = {
            "ok": False,
            "schema_id": "ion.git_root_normalization_preview_write_refusal.v1",
            "refusal_class": "CONFIRMATION_REQUIRED",
            "required_confirmation": WRITE_CONFIRMATION_TOKEN,
            **NORMALIZATION_AUTHORITY_FALSE,
        }
        if args.json:
            _print_json(payload)
        else:
            print(f"Refused: confirmation must be {WRITE_CONFIRMATION_TOKEN}", file=sys.stderr)
        return 3

    payload = write_git_root_normalization_preview(args.ion_root) if args.write else build_git_root_normalization_preview(args.ion_root)
    if args.json:
        _print_json(payload)
    else:
        print(payload["status"])
        summary = payload.get("tracked_to_active_map_summary", {})
        print(f"tracked_to_active_paths={summary.get('tracked_path_count', 0)}")
        print(f"new_active_source_paths={payload.get('new_active_source_summary', {}).get('path_count', 0)}")
    return 0 if payload.get("ok") else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
