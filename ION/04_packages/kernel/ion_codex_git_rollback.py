"""Diff-backed Codex chat rollback ledger.

This module gives the cockpit a Cursor-like rollback surface without using
destructive Git commands. It preserves diffs as evidence first; live rollback is
only available when the saved patch still reverse-applies cleanly.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from .ion_codex_conversation_archive import build_codex_conversation_archive

SCHEMA_ID = "ion.codex_git_rollback.v1"
CHECKPOINT_SCHEMA_ID = "ion.codex_git_diff_checkpoint.v1"
ROLLBACK_RECEIPT_SCHEMA_ID = "ion.codex_git_rollback_receipt.v1"
READY_VERDICT = "ION_CODEX_GIT_ROLLBACK_READY"
DEGRADED_VERDICT = "ION_CODEX_GIT_ROLLBACK_DEGRADED"
WRITE_CONFIRMATION_TOKEN = "ION_BOUNDED_WRITE_CONFIRMED"

ROLLBACK_ROOT = Path("ION/05_context/current/codex_carrier/git_rollback")
CHECKPOINT_DIR = ROLLBACK_ROOT / "diff_checkpoints"
ROLLBACK_RECEIPT_DIR = ROLLBACK_ROOT / "rollback_receipts"
MAX_CAPTURE_DIFF_BYTES = 800_000
MAX_PREVIEW_DIFF_CHARS = 80_000
MAX_CURRENT_DIFF_CHARS = 180_000
MAX_DIFF_FILE_EXCERPT_CHARS = 24_000
MAX_STATUS_SAMPLE = 20

SECRETISH_TOKENS = (
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


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _slug(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_")
    return cleaned[:90] or "codex_diff"


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def _resolve_shell_root(root: str | Path | None = None) -> Path:
    candidate = Path(root or ".").expanduser().resolve()
    for path in (candidate, *candidate.parents):
        if (path / "pyproject.toml").is_file() and (path / "ION" / "REPO_AUTHORITY.md").is_file():
            return path
        if path.name == "ION" and (path / "REPO_AUTHORITY.md").is_file() and (path.parent / "pyproject.toml").is_file():
            return path.parent
    return candidate


def _run_git(
    cwd: Path,
    args: Sequence[str],
    *,
    input_text: str | None = None,
    timeout: int = 12,
    max_output_chars: int = 120_000,
) -> dict[str, Any]:
    command = ["git", *args]
    try:
        proc = subprocess.run(
            command,
            cwd=cwd,
            input=input_text,
            check=False,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
        )
    except FileNotFoundError:
        return {"command": command, "available": False, "returncode": None, "stdout": "", "stderr": "git_not_found"}
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else "timeout_expired"
        return {
            "command": command,
            "available": True,
            "returncode": None,
            "stdout": stdout[:max_output_chars],
            "stderr": stderr[:max_output_chars],
            "timeout": timeout,
        }
    return {
        "command": command,
        "available": True,
        "returncode": proc.returncode,
        "stdout": (proc.stdout or "")[:max_output_chars],
        "stderr": (proc.stderr or "")[:max_output_chars],
    }


def _git_root(shell_root: Path) -> Path | None:
    result = _run_git(shell_root, ["rev-parse", "--show-toplevel"], timeout=5, max_output_chars=4000)
    if result.get("returncode") != 0:
        return None
    stdout = str(result.get("stdout") or "").strip()
    return Path(stdout).resolve() if stdout else None


def _shell_prefix(shell_root: Path, git_root: Path) -> str:
    try:
        rel = shell_root.resolve().relative_to(git_root.resolve()).as_posix()
    except ValueError:
        return ""
    return "" if rel == "." else rel


def _pathspec(prefix: str) -> list[str]:
    return ["--", prefix] if prefix else []


def _branch_from_status(status_stdout: str) -> str | None:
    for line in status_stdout.splitlines():
        if line.startswith("## "):
            return line[3:].split("...", 1)[0].strip() or None
    return None


def _status_entries(status_stdout: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for line in status_stdout.splitlines():
        if not line.strip() or line.startswith("##"):
            continue
        status = line[:2]
        raw_path = line[3:] if len(line) > 3 else ""
        path = raw_path.rsplit(" -> ", 1)[-1].strip()
        entries.append({
            "status": status,
            "path": path,
            "raw_path": raw_path,
            "untracked": status == "??",
            "deleted": "D" in status,
            "staged": status[0] not in {" ", "?"},
            "unstaged": status[1] not in {" ", "?"},
        })
    return entries


def _parse_diff_stats(diff_text: str) -> dict[str, Any]:
    files: list[str] = []
    seen: set[str] = set()
    added = 0
    removed = 0
    for raw_line in diff_text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                path = parts[3].removeprefix("b/")
                key = path.lower()
                if path and key not in seen:
                    seen.add(key)
                    files.append(path)
        elif line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed += 1
    return {
        "files": files,
        "file_count": len(files),
        "added_lines": added,
        "removed_lines": removed,
    }


def _unique_ordered(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = value.strip()
        key = cleaned.lower()
        if not cleaned or key in seen:
            continue
        seen.add(key)
        result.append(cleaned)
    return result


def _diff_header_path(line: str) -> str:
    parts = line.split()
    if len(parts) >= 4 and parts[0] == "diff" and parts[1] == "--git":
        return parts[3].removeprefix("b/")
    return ""


def _diff_file_path(lines: Sequence[str]) -> str:
    for line in lines:
        path = _diff_header_path(line)
        if path:
            return path
    for prefix in ("+++ b/", "--- a/"):
        for line in lines:
            if line.startswith(prefix):
                return line.removeprefix(prefix).strip()
    stats = _parse_diff_stats("\n".join(lines))
    files = stats.get("files") or []
    return str(files[0]) if files else ""


def _diff_change_kind(lines: Sequence[str]) -> str:
    joined = "\n".join(lines)
    if "new file mode" in joined:
        return "added"
    if "deleted file mode" in joined:
        return "deleted"
    if "rename from " in joined or "rename to " in joined:
        return "renamed"
    if "Binary files " in joined:
        return "binary"
    return "modified"


def _diff_file_records(
    diff_text: str,
    *,
    source: str,
    status_by_path: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    current: list[str] = []

    def flush() -> None:
        if not current:
            return
        chunk = "\n".join(current).rstrip()
        path = _diff_file_path(current)
        stats = _parse_diff_stats(chunk)
        files = list(stats.get("files") or [])
        if not path and files:
            path = str(files[0])
        status = status_by_path.get(path.lower(), {}) if path else {}
        secret_risk = _is_secretish(path)
        excerpt = "[diff redacted: path matches secret-risk policy]"
        if not secret_risk:
            excerpt = chunk[:MAX_DIFF_FILE_EXCERPT_CHARS]
        records.append({
            "schema_id": "ion.codex_current_file_edit.v1",
            "source": source,
            "path": path,
            "status": status.get("status") or source,
            "change_kind": _diff_change_kind(current),
            "added_lines": stats.get("added_lines", 0),
            "removed_lines": stats.get("removed_lines", 0),
            "hunk_count": sum(1 for line in current if line.startswith("@@")),
            "diff_bytes": len(chunk.encode("utf-8")),
            "diff_sha256": _sha256_text(chunk) if chunk else None,
            "safe_diff_excerpt": excerpt,
            "diff_excerpt_truncated": len(chunk) > MAX_DIFF_FILE_EXCERPT_CHARS,
            "secret_risk": secret_risk,
            "rollback_supported": False,
            "production_authority": False,
            "live_execution_authority": False,
        })

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            flush()
            current = [line]
        elif current:
            current.append(line)
    flush()
    return records


def _current_worktree_edits(shell_root: Path) -> dict[str, Any]:
    git_root = _git_root(shell_root)
    if git_root is None:
        return {
            "schema_id": "ion.codex_current_worktree_edits.v1",
            "available": False,
            "finding": "not_a_git_worktree",
            "dirty": False,
            "file_edits": [],
            "diff_stats": {"files": [], "file_count": 0, "added_lines": 0, "removed_lines": 0},
            "production_authority": False,
            "live_execution_authority": False,
        }

    prefix = _shell_prefix(shell_root, git_root)
    status = _run_git(git_root, ["status", "--porcelain=v1", "--branch", "-uall", *_pathspec(prefix)], max_output_chars=120_000)
    head = _run_git(git_root, ["rev-parse", "HEAD"], timeout=5, max_output_chars=2000)
    staged = _run_git(git_root, ["diff", "--cached", "--no-ext-diff", *_pathspec(prefix)], max_output_chars=MAX_CURRENT_DIFF_CHARS + 1)
    unstaged = _run_git(git_root, ["diff", "--no-ext-diff", *_pathspec(prefix)], max_output_chars=MAX_CURRENT_DIFF_CHARS + 1)
    status_entries = _status_entries(str(status.get("stdout") or ""))
    status_by_path = {str(entry.get("path") or "").lower(): entry for entry in status_entries}

    staged_diff = str(staged.get("stdout") or "")
    unstaged_diff = str(unstaged.get("stdout") or "")
    staged_truncated = len(staged_diff) > MAX_CURRENT_DIFF_CHARS
    unstaged_truncated = len(unstaged_diff) > MAX_CURRENT_DIFF_CHARS
    staged_diff = staged_diff[:MAX_CURRENT_DIFF_CHARS]
    unstaged_diff = unstaged_diff[:MAX_CURRENT_DIFF_CHARS]

    file_edits = [
        *_diff_file_records(staged_diff, source="staged", status_by_path=status_by_path),
        *_diff_file_records(unstaged_diff, source="unstaged", status_by_path=status_by_path),
    ]
    untracked = [entry for entry in status_entries if entry.get("untracked")]
    for entry in untracked:
        path = str(entry.get("path") or "")
        file_edits.append({
            "schema_id": "ion.codex_current_file_edit.v1",
            "source": "untracked",
            "path": path,
            "status": entry.get("status") or "??",
            "change_kind": "untracked",
            "added_lines": 0,
            "removed_lines": 0,
            "hunk_count": 0,
            "diff_bytes": 0,
            "diff_sha256": None,
            "safe_diff_excerpt": "Untracked file content is not exported by the cockpit diff projection.",
            "diff_excerpt_truncated": False,
            "secret_risk": _is_secretish(path),
            "rollback_supported": False,
            "production_authority": False,
            "live_execution_authority": False,
        })

    combined_diff = "\n".join(part for part in (staged_diff, unstaged_diff) if part)
    tracked_stats = _parse_diff_stats(combined_diff)
    all_files = _unique_ordered([*list(tracked_stats.get("files") or []), *[str(entry.get("path") or "") for entry in untracked]])
    secret_risk_paths = [path for path in all_files if _is_secretish(path)]
    return {
        "schema_id": "ion.codex_current_worktree_edits.v1",
        "available": status.get("returncode") == 0 and staged.get("returncode") == 0 and unstaged.get("returncode") == 0,
        "generated_at": _now(),
        "git_root": git_root.as_posix(),
        "shell_root": shell_root.as_posix(),
        "scope_prefix": prefix,
        "branch": _branch_from_status(str(status.get("stdout") or "")),
        "head": str(head.get("stdout") or "").strip() if head.get("returncode") == 0 else None,
        "dirty": bool(status_entries),
        "status_entries": status_entries[:100],
        "status_sample": status_entries[:MAX_STATUS_SAMPLE],
        "file_edits": file_edits[:100],
        "diff_stats": {
            "files": all_files[:100],
            "file_count": len(all_files),
            "added_lines": tracked_stats.get("added_lines", 0),
            "removed_lines": tracked_stats.get("removed_lines", 0),
        },
        "staged_file_count": sum(1 for item in file_edits if item.get("source") == "staged"),
        "unstaged_file_count": sum(1 for item in file_edits if item.get("source") == "unstaged"),
        "untracked_file_count": len(untracked),
        "secret_risk_path_count": len(secret_risk_paths),
        "secret_risk_paths": secret_risk_paths[:20],
        "diff_truncated": staged_truncated or unstaged_truncated,
        "staged_diff_truncated": staged_truncated,
        "unstaged_diff_truncated": unstaged_truncated,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _is_secretish(path: str) -> bool:
    lowered = path.lower()
    return any(token in lowered for token in SECRETISH_TOKENS)


def _checkpoint_path(root: Path, label: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ%f")
    return root / CHECKPOINT_DIR / f"{stamp}_{_slug(label)}.json"


def _rollback_receipt_path(root: Path, checkpoint_id: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ%f")
    return root / ROLLBACK_RECEIPT_DIR / f"{stamp}_{_slug(checkpoint_id)}_rollback.json"


def _checkpoint_files(root: Path) -> list[Path]:
    base = root / CHECKPOINT_DIR
    if not base.exists():
        return []
    return sorted(base.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)


def _rollback_receipt_files(root: Path) -> list[Path]:
    base = root / ROLLBACK_RECEIPT_DIR
    if not base.exists():
        return []
    return sorted(base.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)


def _load_checkpoint(root: Path, args: Mapping[str, Any]) -> tuple[dict[str, Any] | None, Path | None, str | None]:
    receipt_rel = str(args.get("receipt_path") or "").strip()
    checkpoint_id = str(args.get("checkpoint_id") or "").strip()
    if receipt_rel:
        path = (root / receipt_rel).resolve()
        allowed = (root / CHECKPOINT_DIR).resolve()
        try:
            path.relative_to(allowed)
        except ValueError:
            return None, None, "checkpoint_receipt_path_out_of_scope"
        if not path.exists():
            return None, None, "checkpoint_receipt_not_found"
        return _read_json(path), path, None
    if checkpoint_id:
        for path in _checkpoint_files(root):
            data = _read_json(path)
            if data.get("checkpoint_id") == checkpoint_id:
                return data, path, None
        return None, None, "checkpoint_id_not_found"
    return None, None, "checkpoint_id_or_receipt_path_required"


def _safe_rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _current_git_summary(shell_root: Path) -> dict[str, Any]:
    git_root = _git_root(shell_root)
    if git_root is None:
        return {
            "available": False,
            "finding": "not_a_git_worktree",
            "dirty": False,
            "scoped_porcelain_count": 0,
            "production_authority": False,
            "live_execution_authority": False,
        }
    prefix = _shell_prefix(shell_root, git_root)
    status = _run_git(git_root, ["status", "--porcelain=v1", "--branch", "--untracked-files=no", *_pathspec(prefix)], max_output_chars=40_000)
    head = _run_git(git_root, ["rev-parse", "HEAD"], timeout=5, max_output_chars=2000)
    entries = _status_entries(str(status.get("stdout") or ""))
    return {
        "available": status.get("returncode") == 0,
        "git_root": git_root.as_posix(),
        "shell_root": shell_root.as_posix(),
        "scope_prefix": prefix,
        "branch": _branch_from_status(str(status.get("stdout") or "")),
        "head": str(head.get("stdout") or "").strip() if head.get("returncode") == 0 else None,
        "dirty": bool(entries),
        "scoped_porcelain_count": len(entries),
        "sample": entries[:MAX_STATUS_SAMPLE],
        "untracked_files_omitted": True,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _checkpoint_summary(root: Path, path: Path, data: Mapping[str, Any]) -> dict[str, Any]:
    stats = data.get("diff_stats") if isinstance(data.get("diff_stats"), Mapping) else {}
    rollback_status = data.get("rollback_status") if isinstance(data.get("rollback_status"), Mapping) else {}
    return {
        "schema_id": "ion.codex_git_diff_checkpoint_summary.v1",
        "checkpoint_id": data.get("checkpoint_id"),
        "receipt_path": _safe_rel(path, root),
        "created_at": data.get("created_at"),
        "label": data.get("label"),
        "session_id": data.get("session_id"),
        "turn_id": data.get("turn_id"),
        "cwd": data.get("cwd"),
        "branch": data.get("branch"),
        "head": data.get("head"),
        "diff_sha256": data.get("diff_sha256"),
        "diff_bytes": data.get("diff_bytes"),
        "rollback_supported": bool(data.get("rollback_supported")),
        "rollback_status": rollback_status.get("status") or ("evidence_only" if not data.get("rollback_supported") else "available"),
        "diff_stats": {
            "files": list(stats.get("files") or [])[:12],
            "file_count": stats.get("file_count", 0),
            "added_lines": stats.get("added_lines", 0),
            "removed_lines": stats.get("removed_lines", 0),
        },
        "secret_risk_path_count": len(data.get("secret_risk_paths") or []),
        "production_authority": False,
        "live_execution_authority": False,
    }


def _archive_diff_evidence(root: Path, session_id: str | None) -> list[dict[str, Any]]:
    if not session_id:
        return []
    archive = build_codex_conversation_archive(root, selected_session_id=session_id, selected_window_count=500)
    excerpt = archive.get("selected_session_excerpt")
    if not isinstance(excerpt, Mapping):
        return []
    rows: list[dict[str, Any]] = []
    for item in excerpt.get("items") or []:
        if not isinstance(item, Mapping):
            continue
        lane = str(item.get("visual_lane") or "")
        kind = str(item.get("message_kind") or "")
        if lane != "diff" and kind not in {"diff", "file_edit"}:
            continue
        message = str(item.get("text") or item.get("snippet") or "")
        stats = item.get("diff_stats") if isinstance(item.get("diff_stats"), Mapping) else _parse_diff_stats(message)
        rows.append({
            "schema_id": "ion.codex_archive_diff_evidence.v1",
            "session_id": session_id,
            "item_index": item.get("index"),
            "timestamp": item.get("timestamp"),
            "message_kind": kind or "diff",
            "detail_label": item.get("detail_label") or "chat diff evidence",
            "diff_stats": stats,
            "path_refs": item.get("path_refs") or [],
            "diff_sha256": _sha256_text(message) if message else None,
            "evidence_only": True,
            "rollback_supported": False,
            "safe_text_excerpt": message[:MAX_PREVIEW_DIFF_CHARS],
        })
    return rows[:50]


def build_codex_git_rollback_model(
    root: str | Path | None = None,
    *,
    selected_session_id: str | None = None,
    limit: int = 12,
) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    checkpoints = [_checkpoint_summary(shell_root, path, _read_json(path)) for path in _checkpoint_files(shell_root)[: max(1, min(limit, 50))]]
    rollback_receipts = []
    for path in _rollback_receipt_files(shell_root)[: max(1, min(limit, 50))]:
        data = _read_json(path)
        rollback_receipts.append({
            "receipt_path": _safe_rel(path, shell_root),
            "created_at": data.get("created_at"),
            "status": data.get("status"),
            "checkpoint_id": data.get("checkpoint_id"),
            "source_receipt_path": data.get("source_receipt_path"),
            "touched_paths": data.get("touched_paths") or [],
        })
    archive_evidence = _archive_diff_evidence(shell_root, selected_session_id)
    ready_count = sum(1 for row in checkpoints if row.get("rollback_supported") and not row.get("secret_risk_path_count"))
    current_git = _current_git_summary(shell_root)
    current_worktree = _current_worktree_edits(shell_root)
    current_diff_stats = current_worktree.get("diff_stats") if isinstance(current_worktree.get("diff_stats"), Mapping) else {}
    return {
        "schema_id": SCHEMA_ID,
        "generated_at": _now(),
        "verdict": READY_VERDICT,
        "ok": True,
        "selected_session_id": selected_session_id,
        "current_git": current_git,
        "current_worktree": current_worktree,
        "tree_discipline": {
            "schema_id": "ion.codex_git_tree_discipline.v1",
            "active_chat_mode": "dirty_tree_compatible",
            "active_chat_dirty_allowed": True,
            "active_chat_policy": "Existing Codex chats preserve diff evidence and block unsafe rollback, but do not require the whole workspace to be clean.",
            "new_project_mode": "clean_tree_required",
            "new_project_start_clean_required": True,
            "new_project_policy": "New project lanes should begin from a clean git status, capture a baseline checkpoint, and settle each Codex work unit by commit or rollback before the next unrelated unit.",
            "current_tree_dirty": bool(current_git.get("dirty")),
            "current_tree_blocks_chat": False,
            "current_tree_blocks_new_project_start": bool(current_git.get("dirty")),
            "rules": [
                "dirty legacy roots are evidence-managed, not treated as unusable",
                "greenfield projects start from clean git status",
                "each edit-capable Codex turn records a diff checkpoint",
                "new-project work should not carry unrelated dirty paths between tasks",
            ],
        },
        "summary": {
            "checkpoint_count": len(_checkpoint_files(shell_root)),
            "visible_checkpoint_count": len(checkpoints),
            "rollback_receipt_count": len(_rollback_receipt_files(shell_root)),
            "rollback_ready_count": ready_count,
            "archive_diff_evidence_count": len(archive_evidence),
            "current_file_count": current_diff_stats.get("file_count", 0),
            "current_added_lines": current_diff_stats.get("added_lines", 0),
            "current_removed_lines": current_diff_stats.get("removed_lines", 0),
            "current_untracked_file_count": current_worktree.get("untracked_file_count", 0),
        },
        "checkpoints": checkpoints,
        "archive_diff_evidence": archive_evidence,
        "rollback_receipts": rollback_receipts,
        "policy": "Diff evidence is durable. Live rollback is allowed only when the saved diff reverse-applies cleanly to the current scoped worktree.",
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }


def capture_codex_diff_checkpoint(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    if str(args.get("confirmation") or "") != WRITE_CONFIRMATION_TOKEN:
        return {"ok": False, "tool": "ion_codex_git_diff_capture", "finding": "confirmation_required"}
    shell_root = _resolve_shell_root(root)
    git_root = _git_root(shell_root)
    if git_root is None:
        return {"ok": False, "tool": "ion_codex_git_diff_capture", "finding": "not_a_git_worktree"}
    prefix = _shell_prefix(shell_root, git_root)
    status = _run_git(git_root, ["status", "--porcelain=v1", "--branch", "-uall", *_pathspec(prefix)], max_output_chars=120_000)
    diff = _run_git(git_root, ["diff", "--binary", "--no-ext-diff", *_pathspec(prefix)], max_output_chars=MAX_CAPTURE_DIFF_BYTES + 1)
    if status.get("returncode") != 0 or diff.get("returncode") != 0:
        return {
            "ok": False,
            "tool": "ion_codex_git_diff_capture",
            "finding": "git_status_or_diff_failed",
            "status_stderr": status.get("stderr"),
            "diff_stderr": diff.get("stderr"),
        }
    diff_text = str(diff.get("stdout") or "")
    diff_bytes = len(diff_text.encode("utf-8"))
    if diff_bytes > MAX_CAPTURE_DIFF_BYTES:
        return {
            "ok": False,
            "tool": "ion_codex_git_diff_capture",
            "finding": "diff_too_large_for_safe_checkpoint",
            "diff_bytes": diff_bytes,
            "max_diff_bytes": MAX_CAPTURE_DIFF_BYTES,
        }
    entries = _status_entries(str(status.get("stdout") or ""))
    stats = _parse_diff_stats(diff_text)
    untracked = [entry for entry in entries if entry.get("untracked")]
    if not diff_text and not untracked:
        return {"ok": False, "tool": "ion_codex_git_diff_capture", "finding": "no_scoped_diff_detected"}
    secret_risk_paths = sorted({path for path in [*stats.get("files", []), *[str(row.get("path")) for row in untracked]] if _is_secretish(path)})
    post_sha256_by_path: dict[str, str | None] = {}
    for path in stats.get("files", []):
        post_sha256_by_path[path] = _sha256_file(git_root / path)
    untracked_hashes = []
    for entry in untracked[:100]:
        path = str(entry.get("path") or "")
        file_path = git_root / path
        untracked_hashes.append({
            "path": path,
            "sha256": _sha256_file(file_path) if file_path.is_file() and not _is_secretish(path) else None,
            "secret_risk": _is_secretish(path),
        })
    head = _run_git(git_root, ["rev-parse", "HEAD"], timeout=5, max_output_chars=2000)
    label = str(args.get("label") or args.get("turn_id") or args.get("session_id") or "codex_diff")
    checkpoint_id = f"codex-diff-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{_sha256_text(diff_text + json.dumps(entries, sort_keys=True))[:12]}"
    receipt_path = _checkpoint_path(shell_root, label)
    receipt = {
        "schema_id": CHECKPOINT_SCHEMA_ID,
        "checkpoint_id": checkpoint_id,
        "created_at": _now(),
        "label": label,
        "session_id": str(args.get("session_id") or ""),
        "turn_id": str(args.get("turn_id") or ""),
        "source": str(args.get("source") or "cockpit_manual_capture"),
        "cwd": shell_root.as_posix(),
        "git_root": git_root.as_posix(),
        "scope_prefix": prefix,
        "branch": _branch_from_status(str(status.get("stdout") or "")),
        "head": str(head.get("stdout") or "").strip() if head.get("returncode") == 0 else None,
        "status_entries": entries,
        "diff": diff_text,
        "diff_sha256": _sha256_text(diff_text),
        "diff_bytes": diff_bytes,
        "diff_stats": stats,
        "post_sha256_by_path": post_sha256_by_path,
        "untracked_file_hashes": untracked_hashes,
        "secret_risk_paths": secret_risk_paths,
        "rollback_supported": bool(diff_text) and not secret_risk_paths,
        "rollback_status": {
            "status": "available" if diff_text and not secret_risk_paths else "evidence_only",
            "reason": "reverse_patch_check_required" if diff_text and not secret_risk_paths else "no_safe_reverse_patch",
        },
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
    }
    _write_json(receipt_path, receipt)
    return {
        "ok": True,
        "tool": "ion_codex_git_diff_capture",
        "data": {
            "schema_id": "ion.codex_git_diff_capture_result.v1",
            "checkpoint_id": checkpoint_id,
            "receipt_path": _safe_rel(receipt_path, shell_root),
            "rollback_supported": receipt["rollback_supported"],
            "diff_stats": stats,
            "diff_bytes": diff_bytes,
            "secret_risk_path_count": len(secret_risk_paths),
            "production_authority": False,
            "live_execution_authority": False,
        },
    }


def preview_codex_git_rollback(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    shell_root = _resolve_shell_root(root)
    receipt, receipt_path, finding = _load_checkpoint(shell_root, args)
    if receipt is None or receipt_path is None:
        return {"ok": False, "tool": "ion_codex_git_rollback_preview", "finding": finding}
    git_root = Path(str(receipt.get("git_root") or "")).expanduser()
    if not git_root.exists():
        git_root = _git_root(shell_root) or shell_root
    diff_text = str(receipt.get("diff") or "")
    blockers: list[str] = []
    if not diff_text:
        blockers.append("checkpoint_has_no_patch_diff")
    if receipt.get("secret_risk_paths"):
        blockers.append("checkpoint_contains_secret_risk_paths")
    for path, expected_sha in dict(receipt.get("post_sha256_by_path") or {}).items():
        current_sha = _sha256_file(git_root / path)
        if current_sha != expected_sha:
            blockers.append("current_file_does_not_match_checkpoint")
            break
    check = {"returncode": None, "stderr": ""}
    if not blockers:
        check = _run_git(git_root, ["apply", "--reverse", "--check", "--whitespace=nowarn"], input_text=diff_text, timeout=15, max_output_chars=12000)
        if check.get("returncode") != 0:
            blockers.append("reverse_patch_check_failed")
    ready = not blockers
    data = {
        "schema_id": "ion.codex_git_rollback_preview.v1",
        "checkpoint_id": receipt.get("checkpoint_id"),
        "source_receipt_path": _safe_rel(receipt_path, shell_root),
        "status": "rollback_ready" if ready else "rollback_blocked",
        "rollback_ready": ready,
        "blockers": blockers,
        "diff_stats": receipt.get("diff_stats") or {},
        "touched_paths": list((receipt.get("diff_stats") or {}).get("files") or []),
        "apply_mode": "git apply --reverse",
        "saved_diff_excerpt": diff_text[:MAX_PREVIEW_DIFF_CHARS],
        "git_check_stderr": check.get("stderr", ""),
        "production_authority": False,
        "live_execution_authority": False,
    }
    return {"ok": True, "tool": "ion_codex_git_rollback_preview", "data": data}


def apply_codex_git_rollback(root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    if str(args.get("confirmation") or "") != WRITE_CONFIRMATION_TOKEN:
        return {"ok": False, "tool": "ion_codex_git_rollback_apply", "finding": "confirmation_required"}
    shell_root = _resolve_shell_root(root)
    preview = preview_codex_git_rollback(shell_root, args)
    if not preview.get("ok") or not (preview.get("data") or {}).get("rollback_ready"):
        return {
            "ok": False,
            "tool": "ion_codex_git_rollback_apply",
            "finding": "rollback_preview_not_ready",
            "preview": preview.get("data", preview),
        }
    receipt, receipt_path, finding = _load_checkpoint(shell_root, args)
    if receipt is None or receipt_path is None:
        return {"ok": False, "tool": "ion_codex_git_rollback_apply", "finding": finding}
    git_root = Path(str(receipt.get("git_root") or "")).expanduser()
    if not git_root.exists():
        git_root = _git_root(shell_root) or shell_root
    diff_text = str(receipt.get("diff") or "")
    applied = _run_git(git_root, ["apply", "--reverse", "--whitespace=nowarn"], input_text=diff_text, timeout=20, max_output_chars=12000)
    if applied.get("returncode") != 0:
        return {
            "ok": False,
            "tool": "ion_codex_git_rollback_apply",
            "finding": "reverse_patch_apply_failed",
            "stderr": applied.get("stderr"),
        }
    rollback_receipt = _rollback_receipt_path(shell_root, str(receipt.get("checkpoint_id") or "checkpoint"))
    payload = {
        "schema_id": ROLLBACK_RECEIPT_SCHEMA_ID,
        "created_at": _now(),
        "status": "CANDIDATE_CODEX_DIFF_ROLLBACK_APPLIED",
        "checkpoint_id": receipt.get("checkpoint_id"),
        "source_receipt_path": _safe_rel(receipt_path, shell_root),
        "touched_paths": list((receipt.get("diff_stats") or {}).get("files") or []),
        "apply_mode": "git apply --reverse",
        "production_authority": False,
        "live_execution_authority": False,
        "secrets_authority": False,
        "settlement_required": True,
    }
    _write_json(rollback_receipt, payload)
    return {
        "ok": True,
        "tool": "ion_codex_git_rollback_apply",
        "data": {
            "schema_id": "ion.codex_git_rollback_apply_result.v1",
            "status": "CANDIDATE_CODEX_DIFF_ROLLBACK_APPLIED",
            "checkpoint_id": receipt.get("checkpoint_id"),
            "receipt_path": _safe_rel(rollback_receipt, shell_root),
            "source_receipt_path": _safe_rel(receipt_path, shell_root),
            "touched_paths": payload["touched_paths"],
            "production_authority": False,
            "live_execution_authority": False,
            "settlement_required": True,
        },
    }
