"""Candidate Codex memory curator helpers for ION.

Codex memory is treated as observable carrier recall, not ION truth.  This
module works through contribution lanes such as ``extensions/ad_hoc`` and
inspects generated memory artifacts without making claims about the hidden
consolidation engine.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

SCHEMA_ID = "ion.codex_memory_curator.v0_1"
SNAPSHOT_SCHEMA_ID = "ion.codex_memory_workspace_snapshot.v0_1"
DIFF_SCHEMA_ID = "ion.codex_memory_workspace_diff.v0_1"
AD_HOC_NOTE_SCHEMA_ID = "ion.codex_memory_ad_hoc_note.v0_1"

DEFAULT_MEMORY_ROOT = Path("/home/sev/.codex/memories")
AD_HOC_DIR = Path("extensions/ad_hoc")
ROLLOUT_SUMMARIES_DIR = Path("rollout_summaries")

GENERATED_MEMORY_FILES = {
    Path("MEMORY.md"),
    Path("memory_summary.md"),
    Path("raw_memories.md"),
}

CONTRIBUTION_LANES = {
    AD_HOC_DIR,
    ROLLOUT_SUMMARIES_DIR,
}

MEMORY_CLASSES: tuple[str, ...] = (
    "stable_workflow_fact",
    "user_preference",
    "project_convention",
    "rollout_evidence",
    "ad_hoc_note",
    "stale_path_or_blocker",
    "unsafe_secret_like_content",
    "generated_summary",
    "generated_raw_memory",
    "recovery_bootstrap",
    "unknown",
)

SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(api[_-]?key|token|secret|password|credential|private[_-]?key)\b", re.I),
    re.compile(r"\b[A-Za-z0-9_]{0,12}(?:sk|pat|ghp|xoxb|xoxp)[A-Za-z0-9_:-]{16,}\b"),
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stamp() -> str:
    return _now().replace("-", "").replace(":", "").replace("+00:00", "Z")


def _slug(value: str, *, fallback: str = "memory_note", limit: int = 96) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "").strip()).strip("._-").lower()
    return (slug or fallback)[:limit]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_read_text(path: Path, *, max_chars: int = 240_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except OSError:
        return ""


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _git(root: Path, args: Iterable[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=5,
        )
    except Exception:
        return ""
    return result.stdout.strip()


def looks_secret_like(text: str, path: str = "") -> bool:
    """Return true when a path or text appears to contain secret material.

    The caller should use this as a redaction/classification signal only.  The
    returned payloads never expose matched values.
    """

    haystack = f"{path}\n{text}"
    return any(pattern.search(haystack) for pattern in SECRET_PATTERNS)


def classify_memory_path(path: Path | str, text: str = "") -> dict[str, Any]:
    """Classify a memory workspace path into generated/contribution classes."""

    rel_path = Path(path)
    rel_posix = rel_path.as_posix()
    classes: list[str] = []
    generated = False
    contribution_lane: str | None = None

    if rel_path in GENERATED_MEMORY_FILES:
        generated = True
        if rel_path.name == "raw_memories.md":
            classes.append("generated_raw_memory")
        else:
            classes.append("generated_summary")

    if rel_path.parts[:2] == ("extensions", "ad_hoc"):
        contribution_lane = "ad_hoc"
        classes.append("ad_hoc_note")

    if rel_path.parts[:1] == ("rollout_summaries",):
        contribution_lane = "rollout_summary"
        classes.append("rollout_evidence")

    if rel_path.name == "ION_CONTEXT_RECOVERY_BOOTSTRAP.md":
        classes.append("recovery_bootstrap")

    lower = text.lower()
    if any(marker in lower for marker in ("user preference", "user said", "preference signals")):
        classes.append("user_preference")
    if any(marker in lower for marker in ("project-orientation", "project convention", "core framing")):
        classes.append("project_convention")
    if any(marker in lower for marker in ("workflow", "do differently", "reusable knowledge")):
        classes.append("stable_workflow_fact")
    if any(marker in lower for marker in ("stale", "blocker", "path_missing", "read-only file system")):
        classes.append("stale_path_or_blocker")
    if looks_secret_like(text, rel_posix):
        classes.append("unsafe_secret_like_content")

    ordered = [item for item in MEMORY_CLASSES if item in set(classes)]
    if not ordered:
        ordered = ["unknown"]

    return {
        "path": rel_posix,
        "classes": ordered,
        "generated": generated,
        "contribution_lane": contribution_lane,
        "write_policy": "observe_generated_output" if generated else "contribution_or_evidence_input",
        "authority": {
            "memory_is_recall_not_authority": True,
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
        },
    }


def snapshot_memory_workspace(memory_root: Path | str = DEFAULT_MEMORY_ROOT) -> dict[str, Any]:
    """Inventory the visible Codex memory artifact layer."""

    root = Path(memory_root).expanduser().resolve(strict=False)
    files: list[dict[str, Any]] = []
    if root.is_dir():
        for file_path in sorted(path for path in root.rglob("*") if path.is_file() and ".git" not in path.parts):
            rel_path = Path(_rel(file_path, root))
            stat = file_path.stat()
            text = _safe_read_text(file_path)
            classification = classify_memory_path(rel_path, text)
            files.append(
                {
                    "path": rel_path.as_posix(),
                    "size_bytes": stat.st_size,
                    "mtime_ns": stat.st_mtime_ns,
                    "sha256": _sha256_file(file_path),
                    "classification": classification,
                    "secret_like_content_detected": "unsafe_secret_like_content" in classification["classes"],
                }
            )

    git_status = _git(root, ["status", "--short"]) if root.is_dir() else ""
    git_head = _git(root, ["rev-parse", "--short", "HEAD"]) if root.is_dir() else ""
    return {
        "schema_id": SNAPSHOT_SCHEMA_ID,
        "created_at": _now(),
        "memory_root": root.as_posix(),
        "memory_root_exists": root.is_dir(),
        "git_head": git_head or None,
        "git_status_short": git_status.splitlines() if git_status else [],
        "generated_files": [path.as_posix() for path in sorted(GENERATED_MEMORY_FILES)],
        "contribution_lanes": [path.as_posix() for path in sorted(CONTRIBUTION_LANES)],
        "file_count": len(files),
        "files": files,
        "authority": {
            "memory_is_recall_not_authority": True,
            "direct_generated_edits_are_primary_path": False,
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
        },
    }


def diff_memory_snapshots(before: Mapping[str, Any], after: Mapping[str, Any]) -> dict[str, Any]:
    """Compare two memory snapshots without reading hidden Codex state."""

    before_files = {item["path"]: item for item in before.get("files", []) if isinstance(item, Mapping)}
    after_files = {item["path"]: item for item in after.get("files", []) if isinstance(item, Mapping)}
    before_paths = set(before_files)
    after_paths = set(after_files)
    added = sorted(after_paths - before_paths)
    removed = sorted(before_paths - after_paths)
    changed = sorted(
        path
        for path in before_paths & after_paths
        if before_files[path].get("sha256") != after_files[path].get("sha256")
        or before_files[path].get("mtime_ns") != after_files[path].get("mtime_ns")
    )
    generated_changed = sorted(path for path in changed + added + removed if Path(path) in GENERATED_MEMORY_FILES)
    contribution_changed = sorted(
        path
        for path in changed + added + removed
        if Path(path).parts[:2] == ("extensions", "ad_hoc") or Path(path).parts[:1] == ("rollout_summaries",)
    )
    return {
        "schema_id": DIFF_SCHEMA_ID,
        "created_at": _now(),
        "before_git_head": before.get("git_head"),
        "after_git_head": after.get("git_head"),
        "before_git_status_short": before.get("git_status_short", []),
        "after_git_status_short": after.get("git_status_short", []),
        "added_paths": added,
        "removed_paths": removed,
        "changed_paths": changed,
        "generated_paths_changed": generated_changed,
        "contribution_paths_changed": contribution_changed,
        "classification": "generated_consolidation_observed" if generated_changed else "contribution_or_no_generated_change",
        "inference_boundary": "Diff shows artifact changes only; it does not reveal Codex memory scoring, selection, or injection rules.",
        "authority": {
            "memory_is_recall_not_authority": True,
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
        },
    }


def build_ad_hoc_memory_note(
    *,
    title: str,
    body: str,
    source: str = "operator_or_curator",
    memory_classes: Iterable[str] = ("stable_workflow_fact",),
    created_at: str | None = None,
) -> str:
    """Build a reviewed ad-hoc memory contribution note."""

    selected = [item for item in memory_classes if item in MEMORY_CLASSES]
    if not selected:
        selected = ["unknown"]
    lines = [
        f"# {title.strip() or 'Ad-hoc Codex Memory Note'}",
        "",
        f"schema_id: {AD_HOC_NOTE_SCHEMA_ID}",
        f"created_at: {created_at or _now()}",
        f"source: {source}",
        "memory_classes:",
        *[f"  - {item}" for item in selected],
        "contribution_lane: extensions/ad_hoc",
        "memory_is_recall_not_authority: true",
        "accepted_state_claim: false",
        "production_authority: false",
        "live_execution_authority: false",
        "",
        "## Memory",
        "",
        body.strip(),
        "",
        "## Curator Notes",
        "",
        "- This note is input for Codex memory consolidation, not generated memory output.",
        "- Verify generated `MEMORY.md` and `memory_summary.md` after consolidation before treating recall behavior as observed.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def write_ad_hoc_memory_note(
    *,
    memory_root: Path | str = DEFAULT_MEMORY_ROOT,
    title: str,
    body: str,
    source: str = "operator_or_curator",
    memory_classes: Iterable[str] = ("stable_workflow_fact",),
    write: bool = False,
) -> dict[str, Any]:
    """Prepare or write an ad-hoc memory note.

    Dry-run is the default so callers can inspect the contribution before
    mutating carrier recall.
    """

    root = Path(memory_root).expanduser().resolve(strict=False)
    note = build_ad_hoc_memory_note(title=title, body=body, source=source, memory_classes=memory_classes)
    rel_path = AD_HOC_DIR / f"{_stamp()}_{_slug(title)}.md"
    path = root / rel_path
    result = {
        "schema_id": AD_HOC_NOTE_SCHEMA_ID,
        "memory_root": root.as_posix(),
        "relative_path": rel_path.as_posix(),
        "write": write,
        "note": note,
        "authority": {
            "memory_is_recall_not_authority": True,
            "accepted_state_claim": False,
            "production_authority": False,
            "live_execution_authority": False,
        },
    }
    if not write:
        result["wrote"] = False
        return result
    if not _is_relative_to(path, root):
        raise ValueError(f"Refusing to write outside memory root: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(path)
    path.write_text(note, encoding="utf-8")
    result["wrote"] = True
    result["path"] = path.as_posix()
    result["sha256"] = _sha256_file(path)
    return result


def _main() -> int:
    parser = argparse.ArgumentParser(description="Inspect and curate Codex memory contribution lanes.")
    parser.add_argument("--memory-root", default=str(DEFAULT_MEMORY_ROOT))
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("snapshot", help="Print a memory workspace snapshot as JSON")

    note = subparsers.add_parser("ad-hoc-note", help="Prepare or write an ad-hoc memory note")
    note.add_argument("--title", required=True)
    note.add_argument("--body", required=True)
    note.add_argument("--source", default="operator_or_curator")
    note.add_argument("--class", dest="classes", action="append", default=[])
    note.add_argument("--write", action="store_true")

    args = parser.parse_args()
    if args.command == "snapshot":
        print(json.dumps(snapshot_memory_workspace(args.memory_root), indent=2, sort_keys=True))
        return 0
    if args.command == "ad-hoc-note":
        print(
            json.dumps(
                write_ad_hoc_memory_note(
                    memory_root=args.memory_root,
                    title=args.title,
                    body=args.body,
                    source=args.source,
                    memory_classes=args.classes or ("stable_workflow_fact",),
                    write=args.write,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
