"""Build a curated ION context mirror for Google Drive synced folders.

The mirror is source-postured export evidence. It is not the active repo and
does not claim accepted state. The builder uses local filesystem copies only;
it does not call Google APIs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from urllib.parse import urlparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_ID = "ion.gdrive_context_mirror.export_manifest.v1"
DEFAULT_OUTPUT = Path("/home/sev/ION - Production/ION_GDRIVE_CONTEXT_MIRROR")
INTENDED_DRIVE_ACCOUNT = "crinkedart@gmail.com"
INTENDED_DRIVE_FOLDER_URI = "google-drive://crinkedart@gmail.com/0ABqIU0r0h-u2Uk9PVA"
MAX_FILE_BYTES_DEFAULT = 2_000_000

CURATED_ROOTS = (
    "ION/02_architecture",
    "ION/03_registry",
    "ION/docs",
    "ION/07_templates",
)

SELECTED_CURRENT_CONTEXT = (
    "ION/05_context/current/codex_solo/CAPSULE.md",
    "ION/05_context/current/codex_solo/MINI.md",
    "ION/05_context/current/codex_solo/HOT_CONTEXT.md",
    "ION/05_context/current/codex_solo/CONTEXT_PACKAGES.json",
    "ION/05_context/current/codex_solo/ROUTE.json",
    "ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_ORCHESTRATION_CONTEXT_PACKAGE.md",
    "ION/05_context/current/helixion_joc_rebuild/HELIXION_JOC_ORCHESTRATION_CONTEXT_PACKAGE.json",
    "ION/05_context/current/action_surface_cartography/ACTION_SURFACE_CONTEXT_PACKAGE_MANIFEST_V0_1.json",
    "ION/05_context/current/action_surface_cartography/ION_ACTIONS_CONNECTOR_CONTEXT_PACKAGE_V0_1.md",
)

SOURCE_LANE_INDEXES = (
    "workpackets/README.md",
    "workpackets/WORKPACKET_INDEX_20260508T190626Z.json",
    "diffs/README.md",
    "diffs/DIFF_INDEX_20260508T190626Z.json",
)

TEMPLATE_FILES = {
    "START_HERE_FOR_GPT.md": "ION/07_templates/gdrive_context_mirror/START_HERE_FOR_GPT.md",
    "GPT_REPO_MOUNT_POLICY.md": "ION/07_templates/gdrive_context_mirror/GPT_REPO_MOUNT_POLICY.md",
}

TEXT_SUFFIXES = {
    ".css",
    ".csv",
    ".html",
    ".js",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}

EXCLUDE_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
    "tmp",
}

EXCLUDE_SUFFIXES = {
    ".db",
    ".gif",
    ".gz",
    ".ico",
    ".jpg",
    ".jpeg",
    ".log",
    ".mp4",
    ".pdf",
    ".png",
    ".pyc",
    ".pyo",
    ".sqlite",
    ".tar",
    ".webm",
    ".zip",
}

SECRET_MARKERS = (
    ".env",
    "secret",
    "secrets",
    "token",
    "tokens",
    "credential",
    "credentials",
    "vault",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _stamp(value: str) -> str:
    return value.replace("-", "").replace(":", "").replace("+00:00", "Z")


def _shell_root(root: str | Path) -> Path:
    p = Path(root).expanduser().resolve()
    return p.parent if p.name == "ION" else p


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_text(path: Path, limit: int = 8000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n\n[TRUNCATED_FOR_SUMMARY]\n"


def _rel(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _run_git(root: Path, args: Sequence[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=20,
        )
    except Exception as exc:  # pragma: no cover - defensive local fallback
        return 999, f"git_unavailable: {type(exc).__name__}: {exc}"
    return proc.returncode, proc.stdout


def _dirty_paths(root: Path) -> set[str]:
    code, output = _run_git(root, ["status", "--short"])
    if code != 0:
        return set()
    dirty: set[str] = set()
    for line in output.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path:
            dirty.add(path.strip('"'))
    return dirty


def _is_tracked(root: Path, rel: str) -> bool:
    code, _ = _run_git(root, ["ls-files", "--error-unmatch", rel])
    return code == 0


def _should_exclude(rel: Path, source: Path, *, max_file_bytes: int) -> tuple[bool, str | None]:
    parts = set(rel.parts)
    if parts & EXCLUDE_PARTS:
        return True, "excluded_path_part"
    lower_name = rel.name.lower()
    lower_path = rel.as_posix().lower()
    if lower_name == ".env" or any(marker in lower_path for marker in SECRET_MARKERS):
        return True, "secret_or_credential_marker"
    if rel.suffix.lower() in EXCLUDE_SUFFIXES:
        return True, "excluded_suffix"
    if rel.suffix.lower() and rel.suffix.lower() not in TEXT_SUFFIXES:
        return True, "non_text_suffix"
    if source.stat().st_size > max_file_bytes:
        return True, "file_too_large"
    return False, None


def _source_posture(rel: str, dirty: set[str], tracked: bool) -> str:
    if rel.startswith("ION/05_context/current/"):
        return "runtime_evidence"
    if rel in SOURCE_LANE_INDEXES:
        return "stale_index"
    if rel.startswith("workpackets/") or rel.startswith("diffs/"):
        return "candidate"
    if rel in dirty or any(path == rel or path.startswith(rel.rstrip("/") + "/") for path in dirty):
        return "candidate"
    if not tracked:
        return "candidate"
    return "accepted"


def _copy_file(
    *,
    root: Path,
    export_dir: Path,
    rel: str,
    source_posture: str,
    entries: list[dict[str, Any]],
    max_file_bytes: int,
) -> bool:
    source = root / rel
    if not source.is_file() or source.is_symlink():
        return False
    excluded, reason = _should_exclude(Path(rel), source, max_file_bytes=max_file_bytes)
    if excluded:
        entries.append(
            {
                "source_path": rel,
                "mirror_path": None,
                "source_posture": source_posture,
                "included": False,
                "exclude_reason": reason,
                "accepted_state_claim": False,
            }
        )
        return False
    target = export_dir / "repo" / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    entries.append(
        {
            "source_path": rel,
            "mirror_path": _rel(target, export_dir),
            "size_bytes": target.stat().st_size,
            "sha256": _sha256_file(target),
            "source_posture": source_posture,
            "source_type": "repo",
            "included": True,
            "accepted_state_claim": False,
        }
    )
    return True


def _iter_curated_files(root: Path) -> Iterable[str]:
    seen: set[str] = set()
    for root_rel in CURATED_ROOTS:
        base = root / root_rel
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.is_symlink():
                continue
            rel = _rel(path, root)
            if rel not in seen:
                seen.add(rel)
                yield rel
    for rel in (*SELECTED_CURRENT_CONTEXT, *SOURCE_LANE_INDEXES):
        if (root / rel).is_file() and rel not in seen:
            seen.add(rel)
            yield rel


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _copy_templates(root: Path, export_dir: Path, entries: list[dict[str, Any]]) -> None:
    start_dir = export_dir / "00_START_HERE"
    for name, rel in TEMPLATE_FILES.items():
        source = root / rel
        target = start_dir / name
        if source.is_file():
            text = source.read_text(encoding="utf-8")
        elif name == "START_HERE_FOR_GPT.md":
            text = "# START HERE FOR GPT\n\nRead EXPORT_MANIFEST.json first.\n"
        else:
            text = "# GPT Repo Mount Policy\n\nGoogle Drive is a mirror, not the active repo.\n"
        _write_text(target, text)
        entries.append(
            {
                "source_path": rel if source.is_file() else "generated_template_fallback",
                "mirror_path": _rel(target, export_dir),
                "size_bytes": target.stat().st_size,
                "sha256": _sha256_file(target),
                "source_posture": "candidate" if not source.is_file() else _source_posture(rel, set(), _is_tracked(root, rel)),
                "source_type": "repo" if source.is_file() else "generated",
                "included": True,
                "accepted_state_claim": False,
            }
        )


def _summarize_index(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"present": False, "path": path.as_posix()}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        files = payload.get("files", [])
        return {
            "present": True,
            "path": path.as_posix(),
            "schema_id": payload.get("schema_id"),
            "file_count": payload.get("file_count", len(files) if isinstance(files, list) else None),
            "total_size_bytes": payload.get("total_size_bytes"),
            "generated_at_utc": payload.get("generated_at_utc"),
            "active_runtime_authority": payload.get("active_runtime_authority", False),
            "note": "index may be stale compared to current loose source lane files",
        }
    except json.JSONDecodeError as exc:
        return {"present": True, "path": path.as_posix(), "parse_error": str(exc)}


def _receipt_summary(root: Path) -> dict[str, Any]:
    receipt_roots = (
        "ION/05_context/current/chatops_bridge/receipts",
        "ION/05_context/current/chatgpt_connector/receipts",
        "ION/05_context/current/action_gateway/receipts",
        "ION/05_context/current/context_settlement/inbox",
        "ION/05_context/current/helixion_joc_rebuild",
    )
    groups: list[dict[str, Any]] = []
    for rel in receipt_roots:
        base = root / rel
        files = sorted([path for path in base.glob("*.json") if path.is_file()], key=lambda p: p.name)[-20:] if base.exists() else []
        groups.append(
            {
                "path": rel,
                "present": base.exists(),
                "latest_count_included": len(files),
                "latest_files": [_rel(path, root) for path in files],
            }
        )
    return {
        "schema_id": "ion.gdrive_context_mirror.receipt_summary.v1",
        "source_posture": "runtime_evidence",
        "raw_receipts_dumped": False,
        "groups": groups,
        "accepted_state_claim": False,
    }


def _context_package_summary(root: Path) -> dict[str, Any]:
    paths = [rel for rel in SELECTED_CURRENT_CONTEXT if (root / rel).exists()]
    return {
        "schema_id": "ion.gdrive_context_mirror.context_package_summary.v1",
        "source_posture": "runtime_evidence",
        "selected_paths": paths,
        "accepted_state_claim": False,
    }


def _write_generated_summaries(root: Path, export_dir: Path, entries: list[dict[str, Any]], *, export_id: str) -> None:
    latest = export_dir / "01_LATEST_CONTEXT"
    workpacket_index = _summarize_index(root / "workpackets/WORKPACKET_INDEX_20260508T190626Z.json")
    diff_index = _summarize_index(root / "diffs/DIFF_INDEX_20260508T190626Z.json")
    receipt_summary = _receipt_summary(root)
    context_summary = _context_package_summary(root)

    current_summary = f"""# Current ION Context Mirror Summary

export_id: {export_id}
source_root: {root.as_posix()}
intended_drive_account: {INTENDED_DRIVE_ACCOUNT}

## Law

- Google Drive is a mirror, not the active repo.
- Exported files are not accepted state by themselves.
- Source posture is binding.
- Runtime evidence is summarized by default, not dumped raw.

## Mount path

1. `00_START_HERE/START_HERE_FOR_GPT.md`
2. `00_START_HERE/GPT_REPO_MOUNT_POLICY.md`
3. `EXPORT_MANIFEST.json`
4. `TREE_SNAPSHOT.txt`
5. `SHA256SUMS.json`
"""
    generated = {
        "CURRENT_CONTEXT_SUMMARY.md": current_summary,
        "WORKPACKET_INDEX_SUMMARY.json": json.dumps(workpacket_index, indent=2, sort_keys=True),
        "DIFF_INDEX_SUMMARY.json": json.dumps(diff_index, indent=2, sort_keys=True),
        "RECEIPT_SUMMARY.json": json.dumps(receipt_summary, indent=2, sort_keys=True),
        "CONTEXT_PACKAGE_SUMMARY.json": json.dumps(context_summary, indent=2, sort_keys=True),
    }
    for name, text in generated.items():
        path = latest / name
        _write_text(path, text)
        entries.append(
            {
                "source_path": "generated_summary",
                "mirror_path": _rel(path, export_dir),
                "size_bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
                "source_posture": "runtime_evidence",
                "source_type": "generated",
                "included": True,
                "accepted_state_claim": False,
            }
        )


def _write_tree_snapshot(export_dir: Path, entries: list[dict[str, Any]]) -> Path:
    included = sorted(entry["mirror_path"] for entry in entries if entry.get("included") and entry.get("mirror_path"))
    path = export_dir / "TREE_SNAPSHOT.txt"
    _write_text(path, "\n".join(included))
    return path


def _write_git_snapshots(root: Path, export_dir: Path, *, include_diff_patch: bool) -> dict[str, Any]:
    stat_code, stat_text = _run_git(root, ["diff", "--stat"])
    stat_path = export_dir / "LATEST_DIFF_STAT.txt"
    if stat_code != 0:
        stat_text = f"git diff --stat unavailable\n{stat_text}"
    if not stat_text.strip():
        stat_text = "No git diff stat output.\n"
    _write_text(stat_path, stat_text)
    result = {
        "diff_stat_path": _rel(stat_path, export_dir),
        "diff_stat_returncode": stat_code,
        "diff_patch_path": None,
        "diff_patch_returncode": None,
    }
    if include_diff_patch:
        patch_code, patch_text = _run_git(root, ["diff"])
        patch_path = export_dir / "LATEST_DIFF.patch"
        if patch_code != 0:
            patch_text = f"git diff unavailable\n{patch_text}"
        _write_text(patch_path, patch_text or "No git diff output.\n")
        result["diff_patch_path"] = _rel(patch_path, export_dir)
        result["diff_patch_returncode"] = patch_code
    return result


def _final_sha_sums(export_dir: Path) -> dict[str, str]:
    sums: dict[str, str] = {}
    for path in sorted(export_dir.rglob("*")):
        if not path.is_file() or path.name == "SHA256SUMS.json":
            continue
        sums[_rel(path, export_dir)] = _sha256_file(path)
    _write_json(export_dir / "SHA256SUMS.json", sums)
    return sums


def _copy_export_to_drive(export_dir: Path, output_root: Path, drive_output: Path, latest_payload: Mapping[str, Any]) -> dict[str, Any]:
    drive_output.mkdir(parents=True, exist_ok=True)
    target_exports = drive_output / "exports"
    target_exports.mkdir(parents=True, exist_ok=True)
    target_export = target_exports / export_dir.name
    shutil.copytree(export_dir, target_export, dirs_exist_ok=True)
    _write_json(drive_output / "LATEST.json", latest_payload)
    return {
        "drive_output": drive_output.as_posix(),
        "drive_export_path": target_export.as_posix(),
        "google_api_used": False,
        "copied": True,
    }


def resolve_drive_output_path(value: str | Path) -> Path:
    raw = str(value)
    if not raw.startswith("google-drive://"):
        return Path(value).expanduser().resolve()

    parsed = urlparse(raw)
    if parsed.scheme != "google-drive" or not parsed.netloc:
        raise ValueError(f"invalid google-drive uri: {raw}")
    if "@" not in parsed.netloc:
        raise ValueError(f"google-drive uri must include account email: {raw}")

    user, domain = parsed.netloc.split("@", 1)
    folder = parsed.path.strip("/")
    base = Path("/run/user") / str(os.getuid()) / "gvfs" / f"google-drive:host={domain},user={user}"
    resolved = base / folder if folder else base
    if not resolved.exists():
        raise FileNotFoundError(
            f"Google Drive URI is not mounted locally: {raw} -> {resolved.as_posix()}"
        )
    return resolved


def build_gdrive_context_mirror(
    root: str | Path,
    *,
    output: str | Path = DEFAULT_OUTPUT,
    drive_output: str | Path | None = None,
    drive_folder_uri: str = INTENDED_DRIVE_FOLDER_URI,
    include_diff_patch: bool = False,
    max_file_bytes: int = MAX_FILE_BYTES_DEFAULT,
    emitted_at: str | None = None,
) -> dict[str, Any]:
    shell = _shell_root(root)
    timestamp = emitted_at or _now()
    export_id = f"ion_gdrive_context_mirror_{_stamp(timestamp)}"
    output_root = Path(output).expanduser().resolve()
    export_dir = output_root / "exports" / export_id
    export_dir.mkdir(parents=True, exist_ok=True)

    dirty = _dirty_paths(shell)
    entries: list[dict[str, Any]] = []
    _copy_templates(shell, export_dir, entries)

    copied_count = 0
    for rel in _iter_curated_files(shell):
        tracked = _is_tracked(shell, rel)
        posture = _source_posture(rel, dirty, tracked)
        if _copy_file(root=shell, export_dir=export_dir, rel=rel, source_posture=posture, entries=entries, max_file_bytes=max_file_bytes):
            copied_count += 1

    _write_generated_summaries(shell, export_dir, entries, export_id=export_id)
    tree_path = _write_tree_snapshot(export_dir, entries)
    git_snapshot = _write_git_snapshots(shell, export_dir, include_diff_patch=include_diff_patch)

    root_confirmed = (shell / "pyproject.toml").exists() and (shell / "ION/REPO_AUTHORITY.md").exists()
    manifest = {
        "schema_id": SCHEMA_ID,
        "export_id": export_id,
        "generated_at": timestamp,
        "source_root": shell.as_posix(),
        "mirror_root": output_root.as_posix(),
        "export_path": export_dir.as_posix(),
        "drive_output": str(drive_output) if drive_output else None,
        "intended_drive_account": INTENDED_DRIVE_ACCOUNT,
        "intended_drive_folder_uri": drive_folder_uri,
        "root_confirmed": root_confirmed,
        "accepted_state_claim": False,
        "google_drive_is_active_repo": False,
        "google_api_used": False,
        "production_authority": False,
        "live_execution_authority": False,
        "source_posture_classes": ["accepted", "candidate", "runtime_evidence", "stale_index", "archive_witness"],
        "curated_roots": list(CURATED_ROOTS),
        "selected_current_context": [rel for rel in SELECTED_CURRENT_CONTEXT if (shell / rel).exists()],
        "excluded_policy": {
            "parts": sorted(EXCLUDE_PARTS),
            "suffixes": sorted(EXCLUDE_SUFFIXES),
            "secret_markers": list(SECRET_MARKERS),
            "max_file_bytes": max_file_bytes,
        },
        "counts": {
            "copied_repo_files": copied_count,
            "manifest_entries": len(entries),
            "included_entries": sum(1 for entry in entries if entry.get("included")),
            "excluded_entries": sum(1 for entry in entries if not entry.get("included")),
        },
        "git_snapshot": git_snapshot,
        "tree_snapshot": _rel(tree_path, export_dir),
        "files": entries,
        "non_claims": [
            "exported files are not accepted state",
            "google drive is not the active repo",
            "no google api used",
            "raw noisy runtime is summarized, not fully dumped",
        ],
    }
    manifest_path = export_dir / "EXPORT_MANIFEST.json"
    _write_json(manifest_path, manifest)

    latest_payload = {
        "schema_id": "ion.gdrive_context_mirror.latest.v1",
        "export_id": export_id,
        "generated_at": timestamp,
        "source_root": shell.as_posix(),
        "mirror_root": output_root.as_posix(),
        "export_path": export_dir.as_posix(),
        "export_manifest": (export_dir / "EXPORT_MANIFEST.json").as_posix(),
        "sha256sums": (export_dir / "SHA256SUMS.json").as_posix(),
        "start_here": (export_dir / "00_START_HERE/START_HERE_FOR_GPT.md").as_posix(),
        "accepted_state_claim": False,
        "google_drive_is_active_repo": False,
        "intended_drive_account": INTENDED_DRIVE_ACCOUNT,
        "intended_drive_folder_uri": drive_folder_uri,
    }
    _write_json(export_dir / "LATEST.json", latest_payload)
    _write_json(output_root / "LATEST.json", latest_payload)
    sha_sums = _final_sha_sums(export_dir)

    drive_result = None
    if drive_output:
        resolved_drive_output = resolve_drive_output_path(drive_output)
        drive_result = _copy_export_to_drive(export_dir, output_root, resolved_drive_output, latest_payload)
        drive_result["requested_drive_output"] = str(drive_output)
        drive_result["resolved_drive_output"] = resolved_drive_output.as_posix()
        drive_result["intended_drive_folder_uri"] = drive_folder_uri

    return {
        "ok": True,
        "schema_id": "ion.gdrive_context_mirror.build_result.v1",
        "export_id": export_id,
        "output_root": output_root.as_posix(),
        "export_path": export_dir.as_posix(),
        "manifest_path": manifest_path.as_posix(),
        "latest_path": (output_root / "LATEST.json").as_posix(),
        "sha256sums_path": (export_dir / "SHA256SUMS.json").as_posix(),
        "tree_snapshot_path": tree_path.as_posix(),
        "diff_stat_path": (export_dir / git_snapshot["diff_stat_path"]).as_posix(),
        "sha256_count": len(sha_sums),
        "included_count": manifest["counts"]["included_entries"],
        "excluded_count": manifest["counts"]["excluded_entries"],
        "drive_result": drive_result,
        "accepted_state_claim": False,
        "google_api_used": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build an ION Google Drive context mirror export.")
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--output", default=DEFAULT_OUTPUT.as_posix())
    parser.add_argument("--drive-output")
    parser.add_argument("--drive-folder-uri", default=INTENDED_DRIVE_FOLDER_URI)
    parser.add_argument("--include-diff-patch", action="store_true")
    parser.add_argument("--max-file-bytes", type=int, default=MAX_FILE_BYTES_DEFAULT)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = build_gdrive_context_mirror(
        args.ion_root,
        output=args.output,
        drive_output=args.drive_output,
        drive_folder_uri=args.drive_folder_uri,
        include_diff_patch=args.include_diff_patch,
        max_file_bytes=args.max_file_bytes,
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"ION Google Drive context mirror written: {result['export_path']}")
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
