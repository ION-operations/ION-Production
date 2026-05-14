"""Project workbench projection and bounded operations for Helixion.

The workbench is a visibility and approval-gated mutation layer for local
projects that ION can help inspect. It does not expose arbitrary shell or broad
filesystem access.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import subprocess
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SCHEMA_ID = "ion.project_workbench.v1"
READY_VERDICT = "ION_PROJECT_WORKBENCH_READY"
WRITE_CONFIRMATION_TOKEN = "ION_BOUNDED_WRITE_CONFIRMED"
WORKBENCH_ROOT = Path("ION/05_context/current/project_workbench")
PATCH_RECEIPT_DIR = WORKBENCH_ROOT / "patch_receipts"
ACTION_LOG_DIR = WORKBENCH_ROOT / "action_logs"
BROWSER_CAPTURE_DIR = WORKBENCH_ROOT / "browser_captures"
RUNTIME_DIR = WORKBENCH_ROOT / "runtime"
PATCH_IDEMPOTENCY_LEDGER = RUNTIME_DIR / "project_patch_apply_idempotency_ledger.json"
MAX_PATCH_OPERATIONS = 25
MAX_READ_BYTES = 256 * 1024
MAX_ACTION_LOG_BYTES = 160_000
DEFAULT_PREVIEW_TIMEOUT_SECONDS = 0.6
DEFAULT_BROWSER_TIMEOUT_MS = 45_000
BROWSER_CAPTURE_BASE_URL = os.environ.get("ION_HELIXION_PROJECT_BASE_URL") or "http://127.0.0.1:8765"

FORBIDDEN_PATH_PARTS = {
    ".git",
    ".env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "playwright-report",
    "test-results",
    "credentials",
    "credential",
    "secrets",
    "secret",
    "vault",
}

BROWSER_BOOKMARK_ROUTES = {
    "home": "/projects/cosmos/preview/",
    "lab": "/projects/cosmos/preview/lab",
    "orbit": "/projects/cosmos/preview/cosmos-review?bookmark=orbit&panel=1",
    "cloud-terminator": "/projects/cosmos/preview/cosmos-review?bookmark=cloud-terminator&panel=1",
    "high-altitude": "/projects/cosmos/preview/cosmos-review?bookmark=high-altitude&panel=1",
    "storm-zone": "/projects/cosmos/preview/cosmos-review?bookmark=storm-zone&panel=1",
    "sun-glitter": "/projects/cosmos/preview/cosmos-review?bookmark=sun-glitter&panel=1",
    "sea-level": "/projects/cosmos/preview/cosmos-review?bookmark=sea-level&panel=1",
    "underwater": "/projects/cosmos/preview/cosmos-review?bookmark=underwater&panel=1",
}


@dataclass(frozen=True)
class IonProjectSpec:
    project_id: str
    label: str
    root: Path
    preview_port: int
    preview_base_path: str
    preview_public_path: str
    allowed_roots: tuple[Path, ...]
    allowed_files: tuple[Path, ...]
    action_commands: Mapping[str, tuple[str, ...]]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _slug(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_")
    return cleaned[:90] or "project_workbench"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(dict(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def _cosmos_root() -> Path:
    configured = os.environ.get("ION_COSMOS_PROJECT_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.home() / "Cosmos/earth-forge").resolve()


def project_specs(ion_root: str | Path | None = None) -> dict[str, IonProjectSpec]:
    _ = ion_root
    cosmos_root = _cosmos_root()
    return {
        "cosmos": IonProjectSpec(
            project_id="cosmos",
            label="Cosmos Water World",
            root=cosmos_root,
            preview_port=int(os.environ.get("ION_COSMOS_PREVIEW_PORT") or "5173"),
            preview_base_path="/projects/cosmos/preview/",
            preview_public_path="/projects/cosmos",
            allowed_roots=(
                Path("src"),
                Path("public/cosmos"),
                Path("scripts/cosmos"),
                Path("docs/cosmos"),
            ),
            allowed_files=(
                Path("package.json"),
                Path("package-lock.json"),
                Path("vite.config.ts"),
                Path("README.md"),
                Path("index.html"),
            ),
            action_commands={
                "build": ("npm", "run", "build"),
                "test": ("npm", "run", "test"),
                "lint": ("npm", "run", "lint"),
                "screenshots": ("npm", "run", "cosmos:review:screenshots"),
                "gibs_snapshot": ("npm", "run", "cosmos:gibs:global-snapshot"),
            },
        )
    }


def resolve_project(ion_root: str | Path | None, project_id: str) -> tuple[IonProjectSpec | None, str | None]:
    normalized = (project_id or "").strip().lower()
    if not normalized:
        return None, "project_id_required"
    specs = project_specs(ion_root)
    spec = specs.get(normalized)
    if spec is None:
        return None, "project_not_registered"
    return spec, None


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _validate_project_path(spec: IonProjectSpec, value: str) -> tuple[Path | None, str | None]:
    if not value:
        return None, "path_required"
    rel = Path(value)
    if rel.is_absolute() or ".." in rel.parts:
        return None, "project_path_must_be_relative"
    lower_parts = {part.lower() for part in rel.parts}
    if lower_parts & FORBIDDEN_PATH_PARTS:
        return None, "project_path_contains_forbidden_part"
    target = (spec.root / rel).resolve()
    if not _is_under(target, spec.root):
        return None, "project_path_must_stay_under_project_root"
    rel_posix = rel.as_posix()
    allowed = rel in spec.allowed_files or any(
        rel_posix == root.as_posix() or rel_posix.startswith(root.as_posix().rstrip("/") + "/")
        for root in spec.allowed_roots
    )
    if not allowed:
        return None, "project_path_not_in_allowlist"
    if target.is_dir():
        return None, "project_path_is_directory"
    return target, None


def _run_read_command(cmd: list[str], cwd: Path, *, timeout: int = 8) -> dict[str, Any]:
    try:
        completed = subprocess.run(cmd, cwd=cwd, check=False, capture_output=True, text=True, timeout=timeout)
    except Exception as exc:
        return {"ok": False, "finding": exc.__class__.__name__, "stdout": "", "stderr": "", "returncode": None}
    return {
        "ok": completed.returncode == 0,
        "finding": "ok" if completed.returncode == 0 else "command_failed",
        "stdout": (completed.stdout or "")[-MAX_ACTION_LOG_BYTES:],
        "stderr": (completed.stderr or "")[-MAX_ACTION_LOG_BYTES:],
        "returncode": completed.returncode,
    }


def _probe_preview(spec: IonProjectSpec, *, timeout_seconds: float = DEFAULT_PREVIEW_TIMEOUT_SECONDS) -> dict[str, Any]:
    url = f"http://127.0.0.1:{spec.preview_port}/"
    try:
        request = urllib.request.Request(url, headers={"Accept": "text/html", "Accept-Encoding": "identity"})
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            status = int(getattr(response, "status", 0) or 0)
            return {
                "status": "ready" if 200 <= status < 300 else "degraded",
                "http_status": status,
                "local_url": url,
                "finding": None if 200 <= status < 300 else "preview_non_2xx",
            }
    except urllib.error.HTTPError as exc:
        return {"status": "degraded", "http_status": exc.code, "local_url": url, "finding": "preview_http_error"}
    except Exception as exc:
        return {"status": "not_running", "http_status": None, "local_url": url, "finding": exc.__class__.__name__}


def _latest_receipts(ion_root: Path, project_id: str, *, limit: int = 8) -> list[dict[str, Any]]:
    base = ion_root / PATCH_RECEIPT_DIR
    rows: list[dict[str, Any]] = []
    if not base.exists():
        return rows
    for path in sorted(base.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        data = _read_json(path)
        if data.get("project_id") != project_id:
            continue
        rows.append({
            "name": path.name,
            "path": path.relative_to(ion_root).as_posix(),
            "status": data.get("status"),
            "action": data.get("action"),
            "touched_paths": data.get("touched_paths", []),
            "created_at": data.get("created_at"),
        })
        if len(rows) >= limit:
            break
    return rows


def _latest_browser_captures(ion_root: Path, project_id: str, *, limit: int = 8) -> list[dict[str, Any]]:
    base = ion_root / BROWSER_CAPTURE_DIR / project_id
    rows: list[dict[str, Any]] = []
    if not base.exists():
        return rows
    for path in sorted(base.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        data = _read_json(path)
        screenshot = str(data.get("screenshot_path") or "")
        rows.append({
            "name": path.name,
            "path": path.relative_to(ion_root).as_posix(),
            "status": data.get("status"),
            "bookmark": data.get("bookmark"),
            "url": data.get("url"),
            "screenshot_path": screenshot,
            "created_at": data.get("created_at"),
            "console_error_count": len(data.get("console_errors") or []),
            "bad_response_count": len(data.get("bad_responses") or []),
        })
        if len(rows) >= limit:
            break
    return rows


def _stable_preview_session_id(project_id: str) -> str:
    return f"project_workbench:{_slug(project_id)}:preview_session"


def _all_patch_receipts(ion_root: Path, project_id: str) -> list[dict[str, Any]]:
    base = ion_root / PATCH_RECEIPT_DIR
    rows: list[dict[str, Any]] = []
    if not base.exists():
        return rows
    for path in sorted(base.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        data = _read_json(path)
        if data.get("project_id") != project_id:
            continue
        touched_paths = data.get("touched_paths") if isinstance(data.get("touched_paths"), list) else []
        rows.append({
            "receipt_path": path.relative_to(ion_root).as_posix(),
            "name": path.name,
            "action": data.get("action"),
            "status": data.get("status"),
            "created_at": data.get("created_at"),
            "rollback_supported": bool(data.get("rollback_supported")),
            "source_receipt_path": data.get("source_receipt_path"),
            "touched_paths_count": len(touched_paths),
            "touched_paths": [str(item) for item in touched_paths[:6]],
            "operations_sha256": data.get("operations_sha256"),
            "idempotency_key": data.get("idempotency_key"),
        })
    return rows


def _all_browser_capture_receipts(ion_root: Path, project_id: str) -> list[dict[str, Any]]:
    base = ion_root / BROWSER_CAPTURE_DIR / project_id
    rows: list[dict[str, Any]] = []
    if not base.exists():
        return rows
    for path in sorted(base.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        data = _read_json(path)
        console_errors = data.get("console_errors") if isinstance(data.get("console_errors"), list) else []
        bad_responses = data.get("bad_responses") if isinstance(data.get("bad_responses"), list) else []
        rows.append({
            "receipt_path": path.relative_to(ion_root).as_posix(),
            "name": path.name,
            "status": data.get("status"),
            "bookmark": data.get("bookmark"),
            "url": data.get("url"),
            "created_at": data.get("created_at"),
            "screenshot_path": data.get("screenshot_path"),
            "console_error_count": len(console_errors),
            "bad_response_count": len(bad_responses),
        })
    return rows


def _recommended_timeline_action(
    project_id: str,
    preview: Mapping[str, Any],
    rollback_candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    if rollback_candidates:
        latest = rollback_candidates[0]
        return {
            "tool": "ion_project_patch_revert",
            "reason": "Rollback-supported receipt is available; revert is the safest immediate bounded mutation.",
            "args_template": {
                "project_id": project_id,
                "receipt_path": latest.get("receipt_path"),
                "confirmation": WRITE_CONFIRMATION_TOKEN,
            },
        }
    if preview.get("status") != "ready":
        return {
            "tool": "ion_project_preview_status",
            "reason": "Preview process is not confirmed ready; probe local preview first.",
            "args_template": {
                "project_id": project_id,
                "probe_preview": True,
            },
        }
    return {
        "tool": "ion_project_browser_capture",
        "reason": "Capture current visual proof before proposing any patch apply.",
        "args_template": {
            "project_id": project_id,
            "bookmark": "orbit",
            "interaction": "none",
            "confirmation": WRITE_CONFIRMATION_TOKEN,
        },
    }


def build_project_workbench_timeline(
    ion_root: str | Path | None = None,
    *,
    project_id: str = "cosmos",
    probe_preview: bool = False,
    max_items: int = 6,
) -> dict[str, Any]:
    root = Path(ion_root or ".").expanduser().resolve()
    spec, finding = resolve_project(root, project_id)
    if spec is None:
        return {
            "schema_id": "ion.project_workbench_timeline.v1",
            "ok": False,
            "finding": finding,
            "project_id": project_id,
            "production_authority": False,
            "live_execution_authority": False,
        }
    item_limit = min(max(int(max_items), 1), 20)
    preview = _probe_preview(spec) if probe_preview else {
        "status": "not_probed",
        "http_status": None,
        "local_url": f"http://127.0.0.1:{spec.preview_port}/",
        "finding": None,
    }
    patch_receipts = _all_patch_receipts(root, spec.project_id)
    capture_receipts = _all_browser_capture_receipts(root, spec.project_id)
    reverted_sources = {
        str(row.get("source_receipt_path"))
        for row in patch_receipts
        if row.get("action") == "ion_project_patch_revert" and row.get("source_receipt_path")
    }
    rollback_candidates = [
        row for row in patch_receipts
        if row.get("action") == "ion_project_patch_apply"
        and row.get("rollback_supported") is True
        and str(row.get("receipt_path")) not in reverted_sources
    ]
    latest_capture = capture_receipts[0] if capture_receipts else {}
    session_id = _stable_preview_session_id(spec.project_id)
    allowed_bookmarks = [
        {"bookmark": name, "route": route}
        for name, route in sorted(BROWSER_BOOKMARK_ROUTES.items())
    ]
    recommended_action = _recommended_timeline_action(spec.project_id, preview, rollback_candidates)
    return {
        "schema_id": "ion.project_workbench_timeline.v1",
        "ok": True,
        "verdict": READY_VERDICT,
        "project_id": spec.project_id,
        "project": {
            "project_id": spec.project_id,
            "label": spec.label,
            "preview_public_path": spec.preview_public_path,
            "preview_base_path": spec.preview_base_path,
        },
        "session": {
            "session_id": session_id,
            "project_id": spec.project_id,
            "preview_status": preview.get("status"),
        },
        "preview": preview,
        "allowed_bookmarks": allowed_bookmarks,
        "latest_patch_receipts": patch_receipts[:item_limit],
        "latest_browser_captures": capture_receipts[:item_limit],
        "rollback_supported_receipts": [
            {
                "receipt_path": row.get("receipt_path"),
                "created_at": row.get("created_at"),
                "status": row.get("status"),
                "touched_paths_count": row.get("touched_paths_count"),
            }
            for row in rollback_candidates[:item_limit]
        ],
        "visual_receipt": {
            "latest_capture_receipt_path": latest_capture.get("receipt_path"),
            "latest_capture_bookmark": latest_capture.get("bookmark"),
            "latest_capture_screenshot_path": latest_capture.get("screenshot_path"),
        },
        "history_counts": {
            "patch_receipt_count": len(patch_receipts),
            "browser_capture_count": len(capture_receipts),
            "rollback_candidate_count": len(rollback_candidates),
        },
        "event_projection": {
            "schema_id": "ion.project_workbench_timeline_event.v1",
            "event_type": "project_workbench_timeline_snapshot",
            "branch_id": f"branch_project_workbench_{spec.project_id}",
            "context_instance_id": f"ctx_project_workbench_{spec.project_id}_preview_session",
            "payload": {
                "project_id": spec.project_id,
                "session_id": session_id,
                "preview_status": preview.get("status"),
                "latest_patch_receipt_path": patch_receipts[0]["receipt_path"] if patch_receipts else None,
                "latest_capture_receipt_path": latest_capture.get("receipt_path"),
                "rollback_candidate_count": len(rollback_candidates),
            },
        },
        "next_recommended_safe_action": recommended_action,
        "public_preview_allowed": True,
        "mutations_require_cockpit_auth": True,
        "write_confirmation_required": True,
        "production_authority": False,
        "live_execution_authority": False,
    }


def build_project_workspace_status(
    ion_root: str | Path | None = None,
    *,
    project_id: str = "cosmos",
    probe_preview: bool = False,
) -> dict[str, Any]:
    root = Path(ion_root or ".").expanduser().resolve()
    spec, finding = resolve_project(root, project_id)
    if spec is None:
        return {
            "schema_id": "ion.project_workspace_status.v1",
            "ok": False,
            "finding": finding,
            "project_id": project_id,
            "production_authority": False,
            "live_execution_authority": False,
        }
    package_json = _read_json(spec.root / "package.json")
    scripts = package_json.get("scripts") if isinstance(package_json.get("scripts"), dict) else {}
    git = _run_read_command(["git", "status", "--short", "--branch"], spec.root) if spec.root.exists() else {
        "ok": False,
        "finding": "project_root_missing",
        "stdout": "",
        "stderr": "",
        "returncode": None,
    }
    preview = _probe_preview(spec) if probe_preview else {
        "status": "not_probed",
        "http_status": None,
        "local_url": f"http://127.0.0.1:{spec.preview_port}/",
        "finding": None,
    }
    return {
        "schema_id": "ion.project_workspace_status.v1",
        "ok": True,
        "verdict": READY_VERDICT,
        "project": {
            "project_id": spec.project_id,
            "label": spec.label,
            "root": spec.root.as_posix(),
            "exists": spec.root.exists(),
            "preview_port": spec.preview_port,
            "preview_base_path": spec.preview_base_path,
            "preview_public_path": spec.preview_public_path,
            "allowed_roots": [path.as_posix() for path in spec.allowed_roots],
            "allowed_files": [path.as_posix() for path in spec.allowed_files],
        },
        "preview": preview,
        "package_scripts": sorted(str(key) for key in scripts),
        "action_ids": sorted(spec.action_commands),
        "git_status": {
            "ok": git["ok"],
            "finding": git["finding"],
            "returncode": git["returncode"],
            "lines": [line for line in str(git.get("stdout") or git.get("stderr") or "").splitlines()[:80]],
        },
        "latest_patch_receipts": _latest_receipts(root, spec.project_id),
        "latest_browser_captures": _latest_browser_captures(root, spec.project_id),
        "public_preview_allowed": True,
        "mutations_require_cockpit_auth": True,
        "write_confirmation_required": True,
        "production_authority": False,
        "live_execution_authority": False,
    }


def project_file_read(ion_root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    spec, finding = resolve_project(ion_root, str(args.get("project_id") or "cosmos"))
    if spec is None:
        return _blocked("ion_project_file_read", finding or "project_not_registered")
    target, path_finding = _validate_project_path(spec, str(args.get("path") or ""))
    if target is None:
        return _blocked("ion_project_file_read", path_finding or "invalid_project_path")
    if not target.exists():
        return _blocked("ion_project_file_read", "project_path_missing", {"path": target.relative_to(spec.root).as_posix()})
    max_bytes = min(max(int(args.get("max_bytes") or MAX_READ_BYTES), 1), MAX_READ_BYTES)
    data = target.read_bytes()[:max_bytes]
    text = data.decode("utf-8", errors="replace")
    return _ok("ion_project_file_read", {
        "schema_id": "ion.project_file_read_result.v1",
        "project_id": spec.project_id,
        "path": target.relative_to(spec.root).as_posix(),
        "bytes_returned": len(data),
        "truncated": target.stat().st_size > len(data),
        "sha256": _sha256_file(target),
        "text": text,
        "production_authority": False,
        "live_execution_authority": False,
    })


def _normalize_operations(args: Mapping[str, Any]) -> tuple[list[dict[str, Any]], str | None]:
    raw = args.get("operations")
    if raw is None:
        raw = [{
            "path": args.get("path") or args.get("target_path"),
            "old_text": args.get("old_text"),
            "new_text": args.get("new_text"),
            "expected_sha256": args.get("expected_sha256"),
        }]
    if not isinstance(raw, list):
        return [], "operations_must_be_list"
    operations: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            return [], "operation_must_be_object"
        path = str(item.get("path") or item.get("target_path") or "").strip()
        old_text = item.get("old_text")
        new_text = item.get("new_text")
        expected_sha = str(item.get("expected_sha256") or "").strip() or None
        if not path:
            return [], "operation_path_required"
        if not isinstance(old_text, str) or not isinstance(new_text, str):
            return [], "operation_old_text_and_new_text_required"
        operations.append({
            "path": path,
            "old_text": old_text,
            "new_text": new_text,
            "expected_sha256": expected_sha,
        })
    if not operations:
        return [], "operations_required"
    paths = [op["path"] for op in operations]
    if len(paths) != len(set(paths)):
        return [], "duplicate_patch_operation_path_not_supported"
    if len(operations) > MAX_PATCH_OPERATIONS:
        return [], "too_many_patch_operations"
    return operations, None


def _operations_fingerprint(operations: list[dict[str, Any]]) -> str:
    return _sha256_text(json.dumps(operations, sort_keys=True, separators=(",", ":")))


def project_patch_preview(ion_root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    spec, finding = resolve_project(ion_root, str(args.get("project_id") or "cosmos"))
    if spec is None:
        return _blocked("ion_project_patch_preview", finding or "project_not_registered")
    operations, op_finding = _normalize_operations(args)
    if op_finding:
        return _blocked("ion_project_patch_preview", op_finding)
    previews: list[dict[str, Any]] = []
    touched_paths: list[str] = []
    for op in operations:
        target, path_finding = _validate_project_path(spec, op["path"])
        if target is None:
            return _blocked("ion_project_patch_preview", path_finding or "invalid_project_path", {"path": op["path"]})
        rel = target.relative_to(spec.root).as_posix()
        if not target.exists():
            return _blocked("ion_project_patch_preview", "target_path_missing", {"path": rel})
        original = target.read_text(encoding="utf-8", errors="replace")
        original_sha = _sha256_text(original)
        expected_sha = op.get("expected_sha256")
        if expected_sha and expected_sha != original_sha:
            return _blocked("ion_project_patch_preview", "expected_sha256_mismatch", {
                "path": rel,
                "expected_sha256": expected_sha,
                "actual_sha256": original_sha,
            })
        occurrences = original.count(op["old_text"])
        if occurrences != 1:
            return _blocked("ion_project_patch_preview", "old_text_must_match_exactly_once", {
                "path": rel,
                "occurrences": occurrences,
            })
        updated = original.replace(op["old_text"], op["new_text"], 1)
        updated_sha = _sha256_text(updated)
        diff = "".join(difflib.unified_diff(
            original.splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile=f"a/{rel}",
            tofile=f"b/{rel}",
        ))
        previews.append({
            "path": rel,
            "original_sha256": original_sha,
            "updated_sha256": updated_sha,
            "old_text_sha256": _sha256_text(op["old_text"]),
            "new_text_sha256": _sha256_text(op["new_text"]),
            "diff": diff,
            "diff_bytes": len(diff.encode("utf-8")),
        })
        touched_paths.append(rel)
    return _ok("ion_project_patch_preview", {
        "schema_id": "ion.project_patch_preview.v1",
        "project_id": spec.project_id,
        "operation_count": len(operations),
        "touched_paths": touched_paths,
        "operations_sha256": _operations_fingerprint(operations),
        "previews": previews,
        "production_authority": False,
        "live_execution_authority": False,
    })


def _ledger_path(ion_root: Path) -> Path:
    return ion_root / PATCH_IDEMPOTENCY_LEDGER


def _load_ledger(ion_root: Path) -> dict[str, Any]:
    ledger = _read_json(_ledger_path(ion_root))
    if ledger:
        ledger.setdefault("records", {})
        return ledger
    return {
        "schema_id": "ion.project_patch_apply_idempotency_ledger.v1",
        "records": {},
        "production_authority": False,
        "live_execution_authority": False,
    }


def _record_ledger(ion_root: Path, key: str, record: Mapping[str, Any]) -> None:
    ledger = _load_ledger(ion_root)
    records = ledger.setdefault("records", {})
    records[key] = dict(record)
    ledger["updated_at"] = utc_now()
    _write_json(_ledger_path(ion_root), ledger)


def _receipt_path(ion_root: Path, prefix: str, project_id: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ%f")
    return ion_root / PATCH_RECEIPT_DIR / f"{stamp}_{project_id}_{prefix}.json"


def project_patch_apply(ion_root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    if str(args.get("confirmation") or "") != WRITE_CONFIRMATION_TOKEN:
        return _blocked("ion_project_patch_apply", "confirmation_required")
    root = Path(ion_root or ".").expanduser().resolve()
    spec, finding = resolve_project(root, str(args.get("project_id") or "cosmos"))
    if spec is None:
        return _blocked("ion_project_patch_apply", finding or "project_not_registered")
    operations, op_finding = _normalize_operations(args)
    if op_finding:
        return _blocked("ion_project_patch_apply", op_finding)
    operations_sha = _operations_fingerprint(operations)
    dedupe_key = str(args.get("idempotency_key") or args.get("client_request_id") or operations_sha).strip()
    if args.get("force_new") is not True:
        existing = _load_ledger(root).get("records", {}).get(dedupe_key)
        if isinstance(existing, Mapping):
            return _ok("ion_project_patch_apply", {
                "schema_id": "ion.project_patch_apply_result.v1",
                "project_id": spec.project_id,
                "idempotent_replay": True,
                "duplicate_prevented": True,
                "receipt_path": existing.get("receipt_path"),
                "operations_sha256": existing.get("operations_sha256"),
                "touched_paths": existing.get("touched_paths", []),
                "production_authority": False,
                "live_execution_authority": False,
            }, mutates_active_state=False)
    preview = project_patch_preview(root, {"project_id": spec.project_id, "operations": operations})
    if not preview.get("ok"):
        blocked = dict(preview)
        blocked["tool"] = "ion_project_patch_apply"
        return blocked
    updated_by_path: dict[str, str] = {}
    previews = list(preview["data"]["previews"])
    for op, item in zip(operations, previews):
        target, _ = _validate_project_path(spec, item["path"])
        if target is None:
            return _blocked("ion_project_patch_apply", "invalid_project_path", {"path": item["path"]})
        original = target.read_text(encoding="utf-8", errors="replace")
        updated_by_path[item["path"]] = original.replace(op["old_text"], op["new_text"], 1)
    for rel, updated in updated_by_path.items():
        target, _ = _validate_project_path(spec, rel)
        if target is not None:
            target.write_text(updated, encoding="utf-8")
    touched_paths = list(preview["data"]["touched_paths"])
    receipt = _receipt_path(root, "apply", spec.project_id)
    receipt_payload = {
        "schema_id": "ion.project_patch_receipt.v1",
        "action": "ion_project_patch_apply",
        "status": "CANDIDATE_PROJECT_PATCH_APPLIED",
        "project_id": spec.project_id,
        "created_at": utc_now(),
        "touched_paths": touched_paths,
        "operations": operations,
        "operations_sha256": operations_sha,
        "preview": previews,
        "idempotency_key": dedupe_key,
        "rollback_supported": True,
        "production_authority": False,
        "live_execution_authority": False,
        "settlement_required": True,
    }
    _write_json(receipt, receipt_payload)
    rel_receipt = receipt.relative_to(root).as_posix()
    _record_ledger(root, dedupe_key, {
        "receipt_path": rel_receipt,
        "operations_sha256": operations_sha,
        "touched_paths": touched_paths,
        "project_id": spec.project_id,
        "created_at": utc_now(),
    })
    return _ok("ion_project_patch_apply", {
        "schema_id": "ion.project_patch_apply_result.v1",
        "status": "CANDIDATE_PROJECT_PATCH_APPLIED",
        "project_id": spec.project_id,
        "receipt_path": rel_receipt,
        "touched_paths": touched_paths,
        "operations_sha256": operations_sha,
        "idempotent_replay": False,
        "duplicate_prevented": False,
        "production_authority": False,
        "live_execution_authority": False,
        "settlement_required": True,
    }, mutates_active_state=True)


def project_patch_revert(ion_root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    if str(args.get("confirmation") or "") != WRITE_CONFIRMATION_TOKEN:
        return _blocked("ion_project_patch_revert", "confirmation_required")
    root = Path(ion_root or ".").expanduser().resolve()
    receipt_rel = str(args.get("receipt_path") or "").strip()
    if not receipt_rel:
        return _blocked("ion_project_patch_revert", "receipt_path_required")
    receipt_path = (root / receipt_rel).resolve()
    if not _is_under(receipt_path, (root / PATCH_RECEIPT_DIR).resolve()) or not receipt_path.exists():
        return _blocked("ion_project_patch_revert", "receipt_path_not_found_or_not_project_patch_receipt")
    receipt = _read_json(receipt_path)
    project_id = str(args.get("project_id") or receipt.get("project_id") or "cosmos")
    spec, finding = resolve_project(root, project_id)
    if spec is None:
        return _blocked("ion_project_patch_revert", finding or "project_not_registered")
    operations = receipt.get("operations")
    previews = receipt.get("preview")
    if not isinstance(operations, list) or not isinstance(previews, list):
        return _blocked("ion_project_patch_revert", "receipt_missing_revert_operations")
    updated_by_path: dict[str, str] = {}
    for op, item in zip(operations, previews):
        if not isinstance(op, Mapping) or not isinstance(item, Mapping):
            return _blocked("ion_project_patch_revert", "receipt_operation_invalid")
        target, path_finding = _validate_project_path(spec, str(item.get("path") or op.get("path") or ""))
        if target is None:
            return _blocked("ion_project_patch_revert", path_finding or "invalid_project_path")
        current = target.read_text(encoding="utf-8", errors="replace")
        if _sha256_text(current) != item.get("updated_sha256"):
            return _blocked("ion_project_patch_revert", "current_file_does_not_match_patch_receipt", {
                "path": target.relative_to(spec.root).as_posix(),
                "expected_sha256": item.get("updated_sha256"),
                "actual_sha256": _sha256_text(current),
            })
        new_text = str(op.get("new_text") or "")
        old_text = str(op.get("old_text") or "")
        if current.count(new_text) != 1:
            return _blocked("ion_project_patch_revert", "patched_text_must_match_exactly_once", {
                "path": target.relative_to(spec.root).as_posix(),
            })
        updated_by_path[target.relative_to(spec.root).as_posix()] = current.replace(new_text, old_text, 1)
    for rel, updated in updated_by_path.items():
        target, _ = _validate_project_path(spec, rel)
        if target is not None:
            target.write_text(updated, encoding="utf-8")
    revert_receipt = _receipt_path(root, "revert", spec.project_id)
    _write_json(revert_receipt, {
        "schema_id": "ion.project_patch_revert_receipt.v1",
        "action": "ion_project_patch_revert",
        "status": "CANDIDATE_PROJECT_PATCH_REVERTED",
        "project_id": spec.project_id,
        "created_at": utc_now(),
        "source_receipt_path": receipt_rel,
        "touched_paths": list(updated_by_path),
        "production_authority": False,
        "live_execution_authority": False,
        "settlement_required": True,
    })
    return _ok("ion_project_patch_revert", {
        "schema_id": "ion.project_patch_revert_result.v1",
        "status": "CANDIDATE_PROJECT_PATCH_REVERTED",
        "project_id": spec.project_id,
        "receipt_path": revert_receipt.relative_to(root).as_posix(),
        "source_receipt_path": receipt_rel,
        "touched_paths": list(updated_by_path),
        "production_authority": False,
        "live_execution_authority": False,
        "settlement_required": True,
    }, mutates_active_state=True)


def project_action_run(ion_root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    if str(args.get("confirmation") or "") != WRITE_CONFIRMATION_TOKEN:
        return _blocked("ion_project_action_run", "confirmation_required")
    root = Path(ion_root or ".").expanduser().resolve()
    spec, finding = resolve_project(root, str(args.get("project_id") or "cosmos"))
    if spec is None:
        return _blocked("ion_project_action_run", finding or "project_not_registered")
    action_id = str(args.get("action_id") or "").strip()
    if action_id not in spec.action_commands:
        return _blocked("ion_project_action_run", "project_action_not_allowlisted", {
            "allowed_action_ids": sorted(spec.action_commands),
        })
    if not spec.root.exists():
        return _blocked("ion_project_action_run", "project_root_missing")
    timeout = min(max(int(args.get("timeout_seconds") or 900), 30), 7200)
    command = list(spec.action_commands[action_id])
    started_at = utc_now()
    result = _run_read_command(command, spec.root, timeout=timeout)
    completed_at = utc_now()
    log_path = root / ACTION_LOG_DIR / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ%f')}_{spec.project_id}_{_slug(action_id)}.json"
    payload = {
        "schema_id": "ion.project_action_run_log.v1",
        "project_id": spec.project_id,
        "action_id": action_id,
        "command": command,
        "started_at": started_at,
        "completed_at": completed_at,
        "ok": result["ok"],
        "returncode": result["returncode"],
        "stdout_tail": result["stdout"],
        "stderr_tail": result["stderr"],
        "production_authority": False,
        "live_execution_authority": False,
    }
    _write_json(log_path, payload)
    return _ok("ion_project_action_run", {
        "schema_id": "ion.project_action_run_result.v1",
        "project_id": spec.project_id,
        "action_id": action_id,
        "ok": result["ok"],
        "returncode": result["returncode"],
        "log_path": log_path.relative_to(root).as_posix(),
        "stdout_tail": result["stdout"][-4000:],
        "stderr_tail": result["stderr"][-4000:],
        "production_authority": False,
        "live_execution_authority": False,
    }, mutates_active_state=True)


def _default_browser_base_url() -> str:
    return os.environ.get("ION_HELIXION_PROJECT_BASE_URL") or BROWSER_CAPTURE_BASE_URL


def _validate_browser_base_url(value: str) -> tuple[str | None, str | None]:
    parsed = urllib.parse.urlparse(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None, "browser_base_url_must_be_http_or_https"
    host = (parsed.hostname or "").lower()
    if parsed.scheme == "http" and host in {"127.0.0.1", "localhost"}:
        return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, "", "", "", "")), None
    if parsed.scheme == "https" and host == "ion.helixion.net":
        return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, "", "", "", "")), None
    return None, "browser_base_url_not_allowlisted"


def _parse_last_json_line(value: str) -> dict[str, Any]:
    for line in reversed((value or "").splitlines()):
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data
    return {}


def _browser_capture_receipt_path(root: Path, project_id: str, bookmark: str) -> tuple[Path, Path]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ%f")
    base = root / BROWSER_CAPTURE_DIR / project_id
    screenshot = base / f"{stamp}_{_slug(bookmark)}.png"
    receipt = base / f"{stamp}_{_slug(bookmark)}.json"
    return screenshot, receipt


def project_browser_capture(ion_root: str | Path | None, args: Mapping[str, Any]) -> dict[str, Any]:
    """Capture an allowlisted project preview route with local Playwright.

    This is a bounded browser-driver lane for evidence capture. It can navigate
    only Helixion project-preview URLs and writes screenshots plus receipts
    under the ION project workbench context.
    """

    if str(args.get("confirmation") or "") != WRITE_CONFIRMATION_TOKEN:
        return _blocked("ion_project_browser_capture", "confirmation_required")
    root = Path(ion_root or ".").expanduser().resolve()
    spec, finding = resolve_project(root, str(args.get("project_id") or "cosmos"))
    if spec is None:
        return _blocked("ion_project_browser_capture", finding or "project_not_registered")
    if not spec.root.exists():
        return _blocked("ion_project_browser_capture", "project_root_missing")
    bookmark = str(args.get("bookmark") or "orbit").strip() or "orbit"
    route = BROWSER_BOOKMARK_ROUTES.get(bookmark)
    if route is None:
        return _blocked("ion_project_browser_capture", "project_browser_bookmark_not_allowlisted", {
            "allowed_bookmarks": sorted(BROWSER_BOOKMARK_ROUTES),
        })
    base_url, base_finding = _validate_browser_base_url(str(args.get("base_url") or _default_browser_base_url()))
    if base_url is None:
        return _blocked("ion_project_browser_capture", base_finding or "invalid_browser_base_url")
    interaction = str(args.get("interaction") or "none").strip() or "none"
    if interaction not in {"none", "reload"}:
        return _blocked("ion_project_browser_capture", "project_browser_interaction_not_allowlisted", {
            "allowed_interactions": ["none", "reload"],
        })
    width = min(max(int(args.get("width") or 1440), 320), 3840)
    height = min(max(int(args.get("height") or 1000), 320), 2400)
    wait_ms = min(max(int(args.get("wait_ms") or 1800), 0), 15_000)
    timeout_ms = min(max(int(args.get("timeout_ms") or DEFAULT_BROWSER_TIMEOUT_MS), 5_000), 180_000)
    url = f"{base_url}{route}"
    screenshot_path, receipt_path = _browser_capture_receipt_path(root, spec.project_id, bookmark)
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    script = textwrap.dedent(
        """
        const { chromium } = require("playwright");
        const url = %(url)s;
        const screenshotPath = %(screenshot_path)s;
        const viewport = %(viewport)s;
        const timeoutMs = %(timeout_ms)s;
        const waitMs = %(wait_ms)s;
        const interaction = %(interaction)s;

        (async () => {
          const browser = await chromium.launch({ args: ["--no-sandbox"] });
          const page = await browser.newPage({ viewport });
          const consoleErrors = [];
          const consoleWarnings = [];
          const badResponses = [];
          const pageErrors = [];
          page.on("console", (msg) => {
            const item = { type: msg.type(), text: msg.text().slice(0, 1600) };
            if (msg.type() === "error") consoleErrors.push(item);
            if (msg.type() === "warning") consoleWarnings.push(item);
          });
          page.on("pageerror", (err) => {
            pageErrors.push({ type: "pageerror", text: String(err && err.message || err).slice(0, 1600) });
          });
          page.on("response", (response) => {
            if (response.status() >= 400) {
              badResponses.push({ status: response.status(), url: response.url().slice(0, 1600) });
            }
          });
          await page.goto(url, { waitUntil: "domcontentloaded", timeout: timeoutMs });
          if (interaction === "reload") {
            await page.reload({ waitUntil: "domcontentloaded", timeout: timeoutMs });
          }
          if (waitMs > 0) await page.waitForTimeout(waitMs);
          const title = await page.title();
          await page.screenshot({ path: screenshotPath, fullPage: false });
          await browser.close();
          console.log(JSON.stringify({
            ok: true,
            title,
            console_errors: consoleErrors.concat(pageErrors),
            console_warnings: consoleWarnings,
            bad_responses: badResponses
          }));
        })().catch(async (err) => {
          console.error(JSON.stringify({ ok: false, error: String(err && err.message || err), name: String(err && err.name || "Error") }));
          process.exit(1);
        });
        """
        % {
            "url": json.dumps(url),
            "screenshot_path": json.dumps(screenshot_path.as_posix()),
            "viewport": json.dumps({"width": width, "height": height}),
            "timeout_ms": json.dumps(timeout_ms),
            "wait_ms": json.dumps(wait_ms),
            "interaction": json.dumps(interaction),
        }
    )
    started_at = utc_now()
    try:
        completed = subprocess.run(
            ["node", "-e", script],
            cwd=spec.root,
            check=False,
            capture_output=True,
            text=True,
            timeout=(timeout_ms // 1000) + 20,
        )
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        output = _parse_last_json_line(stdout) or _parse_last_json_line(stderr)
        returncode = completed.returncode
    except Exception as exc:
        stdout = ""
        stderr = f"{exc.__class__.__name__}: {exc}"
        output = {"ok": False, "error": str(exc), "name": exc.__class__.__name__}
        returncode = None
    completed_at = utc_now()
    ok = bool(output.get("ok")) and returncode == 0 and screenshot_path.exists()
    receipt_payload = {
        "schema_id": "ion.project_browser_capture_receipt.v1",
        "action": "ion_project_browser_capture",
        "status": "PROJECT_BROWSER_CAPTURE_COMPLETE" if ok else "PROJECT_BROWSER_CAPTURE_FAILED",
        "project_id": spec.project_id,
        "bookmark": bookmark,
        "interaction": interaction,
        "url": url,
        "base_url": base_url,
        "route": route,
        "viewport": {"width": width, "height": height},
        "started_at": started_at,
        "completed_at": completed_at,
        "ok": ok,
        "returncode": returncode,
        "title": output.get("title"),
        "console_errors": output.get("console_errors") or [],
        "console_warnings": output.get("console_warnings") or [],
        "bad_responses": output.get("bad_responses") or [],
        "error": output.get("error"),
        "screenshot_path": screenshot_path.relative_to(root).as_posix() if screenshot_path.exists() else None,
        "stdout_tail": stdout[-8000:],
        "stderr_tail": stderr[-8000:],
        "production_authority": False,
        "live_execution_authority": False,
        "settlement_required": True,
    }
    _write_json(receipt_path, receipt_payload)
    return _ok("ion_project_browser_capture", {
        "schema_id": "ion.project_browser_capture_result.v1",
        "project_id": spec.project_id,
        "bookmark": bookmark,
        "interaction": interaction,
        "url": url,
        "ok": ok,
        "returncode": returncode,
        "title": output.get("title"),
        "screenshot_path": screenshot_path.relative_to(root).as_posix() if screenshot_path.exists() else None,
        "receipt_path": receipt_path.relative_to(root).as_posix(),
        "console_error_count": len(output.get("console_errors") or []),
        "console_warning_count": len(output.get("console_warnings") or []),
        "bad_response_count": len(output.get("bad_responses") or []),
        "error": output.get("error"),
        "production_authority": False,
        "live_execution_authority": False,
        "settlement_required": True,
    }, mutates_active_state=True)


def _ok(tool: str, data: Mapping[str, Any], *, mutates_active_state: bool = False) -> dict[str, Any]:
    return {
        "schema_id": "ion.project_workbench_tool_result.v1",
        "tool": tool,
        "ok": True,
        "data": dict(data),
        "mutates_active_state": mutates_active_state,
        "production_authority": False,
        "live_execution_authority": False,
    }


def _blocked(tool: str, finding: str, data: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {
        "schema_id": "ion.project_workbench_tool_result.v1",
        "tool": tool,
        "ok": False,
        "finding": finding,
        "data": dict(data or {}),
        "mutates_active_state": False,
        "production_authority": False,
        "live_execution_authority": False,
    }
