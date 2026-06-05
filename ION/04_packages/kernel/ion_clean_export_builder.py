"""Clean, secret-safe export builder for the ION single-carrier sandbox root."""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping

from .ion_path_authority import WorkspaceAuthority, decide_path_authority, load_workspace_authority
from .ion_status import build_ion_status

SCHEMA_ID = "ion.clean_export_manifest.v0_1"
DEFAULT_OUTPUT_DIR = Path("ION_EXPORTS_LOCAL")
ARCHIVE_ROOT = "ION_CLEAN_EXPORT"
MANIFEST_SIDECAR_NAME = "CLEAN_EXPORT_MANIFEST.json"
ARCHIVE_MANIFEST_NAME = "CLEAN_EXPORT_MANIFEST_PREHASH.json"
LEGACY_ESCAPED_OUTPUT_DIRS = (
    Path("/home/sev/ION_EXPORTS_LOCAL"),
)

ROOT_FILES = (
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "pyproject.toml",
    "ION_CONTEXT_CAPSULE.yaml",
    "ION/REPO_AUTHORITY.md",
    "ION/AGENT_CONTRACT.md",
    "ION/STATUS.md",
    "ION/PLAN.md",
)

INCLUDE_TREES = (
    "ION/01_doctrine",
    "ION/02_architecture",
    "ION/03_registry",
    "ION/04_packages/kernel",
    "ION/07_templates",
    "ION/docs",
    "ION/tests",
    "ION/05_context/current/reports",
    "ION/05_context/current/worker_shift/signons",
    "ION/05_context/current/worker_shift/leases",
    "ION/05_context/current/worker_shift/signoffs",
)

CURRENT_STATE_GLOBS = (
    "ION/05_context/current/*.json",
)

REQUIRED_REVIEW_FILES = (
    "ION/05_context/current/reports/SINGLE_CARRIER_OPERATING_SPINE_SETTLEMENT_REPORT.md",
    "ION/05_context/current/reports/SINGLE_CARRIER_OPERATING_SPINE_SETTLEMENT_LEDGER.json",
    "ION/05_context/current/reports/WAVE_001_002_RECONCILIATION_REPORT.md",
    "ION/05_context/current/reports/WAVE_001_002_RECONCILIATION_LEDGER.json",
    "ION/05_context/current/reports/WAVE_003_PLAN_ONLY.md",
)

FORBIDDEN_DIR_NAMES = {
    ".cache",
    ".codex",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "env",
    "ION_EXPORTS_LOCAL",
    "ION_VAULT_LOCAL",
    "node_modules",
    "venv",
}

FORBIDDEN_FILE_PREFIXES = (".env",)
FORBIDDEN_SUFFIXES = (".pyc", ".pyo")
SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
TOKEN_FILE_SUFFIXES = {".token", ".secret", ".credential"}
PRIVATE_KEY_NAMES = {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"}
TOKEN_NAME_RE = re.compile(r"(^|[._-])(token|secret|credential)([._-]|$)", re.IGNORECASE)
KEY_NAME_RE = re.compile(r"(^|[._-])(private[_-]?key|api[_-]?key|access[_-]?key)([._-]|$)", re.IGNORECASE)

SECRET_ASSIGNMENT_RE = re.compile(
    r"^\s*(?:export\s+)?(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*[:=]\s*['\"]?(?P<value>[^'\"\s#]+)",
    re.IGNORECASE,
)
SECRET_VALUE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("OPENAI_API_KEY_VALUE", re.compile(r"\bsk-(?!\[)[A-Za-z0-9_-]{20,}\b")),
    ("GITHUB_TOKEN_VALUE", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("AWS_ACCESS_KEY_ID_VALUE", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("SLACK_TOKEN_VALUE", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("PRIVATE_KEY_BLOCK", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
)
SAFE_PLACEHOLDER_FRAGMENTS = (
    "abcdefghijkl",
    "changeme",
    "dummy",
    "example",
    "fake",
    "must-not-print",
    "placeholder",
    "redacted",
    "replace",
    "sample",
    "secret-value",
    "test",
    "todo",
    "xxxx",
)
SAFE_SCHEMA_VALUES = {
    "false",
    "true",
    "none",
    "null",
    "required",
    "optional",
    "string",
    "integer",
    "number",
    "object",
    "array",
}
SECRET_NAME_TERMS = {
    "api_key",
    "access_key",
    "client_secret",
    "credential",
    "password",
    "private_key",
    "secret",
    "service_role_key",
    "token",
}
SAFE_SECRET_NAME_SUFFIXES = (
    "_audience",
    "_authority",
    "_budget",
    "_count",
    "_enabled",
    "_estimate",
    "_scan",
    "_source",
    "_source_path",
    "_total",
)

AUTHORITY_FALSE = {
    "accepted_state_claim": False,
    "production_authority": False,
    "live_execution_authority": False,
    "deploy_authority": False,
    "push_authority": False,
    "secrets_authority": False,
}


@dataclass(frozen=True)
class FileRecord:
    path: str
    bytes: int
    sha256: str
    source_posture: str


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def _stamp(value: str) -> str:
    return value.replace("-", "").replace(":", "").replace("+00:00", "Z")


def _slug(value: str, *, fallback: str = "export") -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip()).strip("._-")
    return slug or fallback


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def resolve_ion_root(ion_root: str | Path | None = None) -> Path:
    root = Path(ion_root or ".").expanduser().resolve(strict=False)
    if not (root / "pyproject.toml").is_file() or not (root / "ION/REPO_AUTHORITY.md").is_file():
        raise ValueError("ion root must contain sibling pyproject.toml and ION/REPO_AUTHORITY.md")
    return root


def _workspace_authority_for_ion_root(ion_root: Path) -> WorkspaceAuthority:
    root = ion_root.resolve(strict=False)
    try:
        authority = load_workspace_authority()
        if authority.active_repo_root == root:
            return authority
    except Exception:
        pass

    workspace_root = root.parent.resolve(strict=False)
    return WorkspaceAuthority(
        workspace_root=workspace_root,
        active_repo_root=root,
        ion_content_root=(root / "ION").resolve(strict=False),
        export_root=(workspace_root / "ION_EXPORTS_LOCAL").resolve(strict=False),
        vault_root=(workspace_root / "ION_VAULT_LOCAL").resolve(strict=False),
        allowed_sibling_roots=(
            (workspace_root / "ION_EXPORTS_LOCAL").resolve(strict=False),
            (workspace_root / "ION_VAULT_LOCAL").resolve(strict=False),
            (workspace_root / "Needs_Routed").resolve(strict=False),
            (workspace_root / "quarantine").resolve(strict=False),
            (workspace_root / "quarentine").resolve(strict=False),
        ),
        forbidden_roots=(
            Path("/home/sev/ION_EXPORTS_LOCAL").resolve(strict=False),
            Path("/home/sev/.ssh").resolve(strict=False),
            Path("/home/sev/.config").resolve(strict=False),
            Path("/home/sev/.codex").resolve(strict=False),
        ),
        path_policy={
            "forbid_parent_segments_for_write": True,
            "canonicalize_all_leases": True,
            "require_workspace_containment_for_artifacts": True,
            "require_artifacts_outside_active_repo": True,
            "require_human_override_for_external_paths": True,
        },
        manifest_path=Path("/home/sev/ION - Production/ION_WORKSPACE_MANIFEST.yaml"),
    )


def authorize_output_dir(ion_root: Path, output_dir: str | Path | None = None) -> dict[str, Any]:
    raw = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    return decide_path_authority(
        raw,
        purpose="artifact",
        base_root="workspace",
        authority=_workspace_authority_for_ion_root(ion_root),
    )


def _is_within(path: Path, parent: Path) -> bool:
    path = path.resolve(strict=False)
    parent = parent.resolve(strict=False)
    return path == parent or parent in path.parents


def resolve_output_dir(ion_root: Path, output_dir: str | Path | None = None) -> Path:
    decision = authorize_output_dir(ion_root, output_dir)
    if not decision["authorized"]:
        raise ValueError(
            "clean export output path authority rejected:"
            f"{decision['reason_code']}:{decision['resolved_path']}"
        )
    return Path(decision["resolved_path"])


def _rel(path: Path, root: Path) -> str:
    return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()


def _path_parts(rel_path: str) -> tuple[str, ...]:
    return PurePosixPath(rel_path.replace("\\", "/")).parts


def _is_needs_routed_raw(rel_path: str) -> bool:
    parts = _path_parts(rel_path)
    return bool(parts and parts[0] == "Needs_Routed")


def _forbidden_reason(rel_path: str, *, is_dir: bool = False) -> str | None:
    parts = _path_parts(rel_path)
    name = parts[-1] if parts else rel_path
    lowered_name = name.lower()
    lowered_path = rel_path.lower()
    if _is_needs_routed_raw(rel_path):
        return "needs_routed_raw_bulk"
    if any(part in FORBIDDEN_DIR_NAMES for part in parts):
        return "forbidden_runtime_or_cache_dir"
    if lowered_name.startswith(FORBIDDEN_FILE_PREFIXES):
        return "dotenv_file"
    if lowered_name.endswith(FORBIDDEN_SUFFIXES):
        return "python_bytecode"
    if "browser_profile" in lowered_path or "browser-profiles" in lowered_path:
        return "browser_profile"
    if "cloudflared" in lowered_path and ("credential" in lowered_name or "cert" in lowered_name):
        return "tunnel_credential"
    if not is_dir and _secret_filename_rule(rel_path):
        return "credential_shaped_filename"
    return None


def _secret_filename_rule(rel_path: str) -> str | None:
    path = PurePosixPath(rel_path)
    lowered_name = path.name.lower()
    suffix = path.suffix.lower()
    if lowered_name in PRIVATE_KEY_NAMES:
        return "PRIVATE_KEY_FILENAME"
    if suffix in SECRET_SUFFIXES:
        return "SECRET_KEY_SUFFIX"
    if suffix in TOKEN_FILE_SUFFIXES:
        return "TOKEN_SECRET_SUFFIX"
    if suffix == ".json" and TOKEN_NAME_RE.search(lowered_name):
        return "TOKEN_SECRET_JSON_NAME"
    if suffix in {".json", ".txt", ".conf", ".cfg"} and KEY_NAME_RE.search(lowered_name):
        return "KEY_FILE_NAME"
    return None


def _source_posture(rel_path: str) -> str:
    if rel_path.startswith("ION/05_context/current/reports/"):
        return "redacted_report_or_ledger"
    if rel_path.startswith("ION/05_context/current/worker_shift/"):
        return "worker_shift_review_receipt"
    if rel_path.startswith("ION/05_context/current/"):
        return "current_state_manifest"
    if rel_path.startswith("ION/04_packages/kernel/"):
        return "kernel_source"
    if rel_path.startswith("ION/tests/"):
        return "test_source"
    if rel_path.startswith("ION/07_templates/"):
        return "public_template"
    if rel_path.startswith("ION/02_architecture/"):
        return "public_protocol"
    return "public_source_or_doc"


def _iter_tree_files(root: Path, rel_root: str) -> Iterable[Path]:
    base = root / rel_root
    if not base.exists():
        return
    stack = [base]
    while stack:
        current = stack.pop()
        try:
            entries = sorted(current.iterdir(), key=lambda item: item.name)
        except OSError:
            continue
        for entry in entries:
            rel = _rel(entry, root)
            if entry.is_dir():
                if _forbidden_reason(rel, is_dir=True):
                    continue
                stack.append(entry)
            elif entry.is_file():
                yield entry


def _collect_excluded_summary(root: Path) -> dict[str, Any]:
    counts: dict[str, int] = {}
    samples: dict[str, list[str]] = {}
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            entries = sorted(current.iterdir(), key=lambda item: item.name)
        except OSError:
            continue
        for entry in entries:
            try:
                rel = _rel(entry, root)
            except ValueError:
                continue
            reason = _forbidden_reason(rel, is_dir=entry.is_dir())
            if reason:
                counts[reason] = counts.get(reason, 0) + 1
                samples.setdefault(reason, [])
                if len(samples[reason]) < 10:
                    samples[reason].append(rel)
                continue
            if entry.is_dir():
                stack.append(entry)
    return {
        "schema_id": "ion.clean_export_excluded_summary.v0_1",
        "counts_by_reason": dict(sorted(counts.items())),
        "sample_paths_by_reason": {key: samples[key] for key in sorted(samples)},
        "raw_needs_routed_included": False,
        "vault_content_read": False,
    }


def collect_candidate_files(root: Path) -> tuple[list[FileRecord], list[str]]:
    selected: dict[str, Path] = {}
    warnings: list[str] = []

    for rel in ROOT_FILES:
        path = root / rel
        if path.is_file() and not _forbidden_reason(rel):
            selected[rel] = path

    for rel_root in INCLUDE_TREES:
        base = root / rel_root
        if not base.exists():
            warnings.append(f"missing_include_tree:{rel_root}")
            continue
        for path in _iter_tree_files(root, rel_root):
            rel = _rel(path, root)
            if not _forbidden_reason(rel):
                selected[rel] = path

    for pattern in CURRENT_STATE_GLOBS:
        for path in sorted(root.glob(pattern)):
            if path.is_file():
                rel = _rel(path, root)
                if not _forbidden_reason(rel):
                    selected[rel] = path

    for rel in REQUIRED_REVIEW_FILES:
        path = root / rel
        if not path.is_file():
            warnings.append(f"missing_required_review_file:{rel}")
        elif not _forbidden_reason(rel):
            selected[rel] = path

    records = [
        FileRecord(
            path=rel,
            bytes=path.stat().st_size,
            sha256=_sha256_file(path),
            source_posture=_source_posture(rel),
        )
        for rel, path in sorted(selected.items())
        if path.is_file()
    ]
    return records, warnings


def _placeholder_value(value: str) -> bool:
    lowered = value.lower()
    return any(fragment in lowered for fragment in SAFE_PLACEHOLDER_FRAGMENTS)


def _secretish_name(name: str) -> bool:
    lowered = name.lower()
    if lowered.endswith(SAFE_SECRET_NAME_SUFFIXES):
        return False
    if any(term in lowered for term in ("api_key", "access_key", "private_key", "service_role_key", "client_secret")):
        return True
    parts = [part for part in re.split(r"[^a-z0-9]+", lowered) if part]
    return any(part in SECRET_NAME_TERMS for part in parts)


def _secretish_assignment_value(value: str) -> bool:
    stripped = value.strip().strip("'\"")
    lowered = stripped.lower()
    if not stripped or lowered in SAFE_SCHEMA_VALUES or _placeholder_value(stripped):
        return False
    if stripped.startswith(("$", "{", "<")):
        return False
    if "/" in stripped or "\\" in stripped:
        return False
    if "." in stripped and not any(mark in stripped for mark in ("=", "+", "/", "@")):
        return False
    if re.fullmatch(r"[A-Z][A-Z0-9_]{5,}", stripped):
        return False
    if len(stripped) < 16:
        return False
    return bool(re.search(r"[A-Za-z]", stripped) and re.search(r"[0-9_+=/@.-]", stripped))


def scan_included_files_for_secrets(root: Path, records: Iterable[FileRecord]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    scanned = 0
    for record in records:
        rel = record.path
        filename_rule = _secret_filename_rule(rel)
        if filename_rule:
            findings.append(
                {
                    "path": rel,
                    "rule_id": filename_rule,
                    "category": "secret_shaped_filename",
                    "secret_values_emitted": False,
                    "content_value_scan_performed": False,
                }
            )
            continue
        path = root / rel
        scanned += 1
        try:
            data = path.read_bytes()
        except OSError:
            findings.append(
                {
                    "path": rel,
                    "rule_id": "READ_FAILED",
                    "category": "scan_error",
                    "secret_values_emitted": False,
                    "content_value_scan_performed": False,
                }
            )
            continue
        if b"\x00" in data[:4096]:
            continue
        text = data[:2_000_000].decode("utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            assignment = SECRET_ASSIGNMENT_RE.match(line)
            suffix = path.suffix.lower()
            assignment_name = assignment.group("name") if assignment else ""
            py_assignment_allowed = suffix != ".py" or assignment_name.isupper()
            if (
                assignment
                and py_assignment_allowed
                and _secretish_name(assignment.group("name"))
                and _secretish_assignment_value(assignment.group("value"))
            ):
                findings.append(
                    {
                        "path": rel,
                        "line": line_number,
                        "rule_id": "SECRET_ASSIGNMENT_VALUE",
                        "category": "raw_secret_content",
                        "variable_name": assignment.group("name"),
                        "secret_values_emitted": False,
                        "content_value_scan_performed": True,
                    }
                )
                break
            for rule_id, pattern in SECRET_VALUE_PATTERNS:
                if pattern.search(line) and not _placeholder_value(line):
                    findings.append(
                        {
                            "path": rel,
                            "line": line_number,
                            "rule_id": rule_id,
                            "category": "raw_secret_content",
                            "secret_values_emitted": False,
                            "content_value_scan_performed": True,
                        }
                    )
                    break
            if findings and findings[-1]["path"] == rel and findings[-1].get("line") == line_number:
                break
    return {
        "schema_id": "ion.clean_export_secret_scan.v0_1",
        "status": "SECURITY_BLOCKED" if findings else "SECURITY_READY",
        "accepted": not findings,
        "included_file_count": len(list(records)) if not isinstance(records, list) else len(records),
        "scanned_file_count": scanned,
        "finding_count": len(findings),
        "findings": findings,
        "secret_values_emitted": False,
    }


def _status_snapshot(root: Path) -> dict[str, Any]:
    try:
        status = build_ion_status(root)
    except Exception as exc:  # pragma: no cover - defensive for incomplete temp roots
        return {
            "available": False,
            "verdict": "ION_STATUS_UNAVAILABLE",
            "error_class": exc.__class__.__name__,
            "production_authority": False,
            "live_execution_authority": False,
        }
    return {
        "available": True,
        "verdict": status.get("verdict"),
        "legacy_verdict_without_truth_gates": status.get("legacy_verdict_without_truth_gates"),
        "profile_id": status.get("profile_id"),
        "status_ceiling": status.get("status_ceiling"),
        "next_lawful_action": status.get("next_lawful_action"),
        "production_authority": bool(status.get("production_authority", False)),
        "live_execution_authority": bool(status.get("live_execution_authority", False)),
    }


def _manifest_payload(
    *,
    root: Path,
    output_dir: Path,
    output_authorization: Mapping[str, Any],
    export_id: str,
    created_at: str,
    dry_run: bool,
    records: list[FileRecord],
    warnings: list[str],
    excluded_summary: Mapping[str, Any],
    secret_scan: Mapping[str, Any],
    status_snapshot: Mapping[str, Any],
    archive_path: Path | None = None,
    archive_sha256: str | None = None,
    sidecar_manifest_path: Path | None = None,
) -> dict[str, Any]:
    return {
        "schema_id": SCHEMA_ID,
        "export_id": export_id,
        "created_at": created_at,
        "source_root": str(root),
        "workspace_root": str(root.parent),
        "output_dir": str(output_dir),
        "output_root_policy": "workspace_local_outside_active_repo",
        "output_authorization": dict(output_authorization),
        "dry_run": dry_run,
        "archive_root": ARCHIVE_ROOT,
        "archive_path": str(archive_path) if archive_path is not None else None,
        "archive_sha256": archive_sha256,
        "sidecar_manifest_path": str(sidecar_manifest_path) if sidecar_manifest_path is not None else None,
        "file_count": len(records),
        "total_bytes": sum(record.bytes for record in records),
        "required_review_files": {
            rel: any(record.path == rel for record in records)
            for rel in REQUIRED_REVIEW_FILES
        },
        "included_files": [record.__dict__ for record in records],
        "excluded_summary": dict(excluded_summary),
        "warnings": warnings,
        "secret_scan": dict(secret_scan),
        "status_verdict_at_export_time": dict(status_snapshot),
        "zip_metadata_normalized": True,
        "path_selection_sorted": True,
        "wave_003_generation_performed": False,
        "vault_content_read": False,
        "raw_needs_routed_included": False,
        **AUTHORITY_FALSE,
    }


def _blocked_output_manifest(
    *,
    root: Path,
    output_authorization: Mapping[str, Any],
    export_id: str,
    created_at: str,
    dry_run: bool,
) -> dict[str, Any]:
    return {
        "schema_id": SCHEMA_ID,
        "export_id": export_id,
        "created_at": created_at,
        "source_root": str(root),
        "workspace_root": str(root.parent),
        "output_dir": output_authorization.get("resolved_path"),
        "output_root_policy": "workspace_local_outside_active_repo",
        "output_authorization": dict(output_authorization),
        "dry_run": dry_run,
        "archive_root": ARCHIVE_ROOT,
        "archive_path": None,
        "archive_sha256": None,
        "sidecar_manifest_path": None,
        "file_count": 0,
        "total_bytes": 0,
        "required_review_files": {rel: False for rel in REQUIRED_REVIEW_FILES},
        "included_files": [],
        "excluded_summary": {},
        "warnings": ["clean export output path authority rejected"],
        "secret_scan": {"accepted": True, "skipped": True, "reason": "output_path_authority_blocked"},
        "status_verdict_at_export_time": {},
        "zip_metadata_normalized": True,
        "path_selection_sorted": True,
        "wave_003_generation_performed": False,
        "vault_content_read": False,
        "raw_needs_routed_included": False,
        "verdict": "BLOCKED_OUTPUT_PATH_AUTHORITY",
        "ok": False,
        **AUTHORITY_FALSE,
    }


def _zip_write_file(archive: zipfile.ZipFile, source: Path, arcname: str) -> None:
    info = zipfile.ZipInfo(arcname)
    info.date_time = (1980, 1, 1, 0, 0, 0)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, source.read_bytes())


def _zip_write_json(archive: zipfile.ZipFile, arcname: str, payload: Mapping[str, Any]) -> None:
    info = zipfile.ZipInfo(arcname)
    info.date_time = (1980, 1, 1, 0, 0, 0)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n")


def _write_archive(root: Path, output_dir: Path, export_id: str, records: list[FileRecord], prehash_manifest: Mapping[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / f"{export_id}.zip"
    tmp_path = output_dir / f".{export_id}.{os.getpid()}.tmp.zip"
    if tmp_path.exists():
        tmp_path.unlink()
    with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        _zip_write_json(archive, f"{ARCHIVE_ROOT}/{ARCHIVE_MANIFEST_NAME}", prehash_manifest)
        for record in records:
            _zip_write_file(archive, root / record.path, f"{ARCHIVE_ROOT}/{record.path}")
    os.replace(tmp_path, archive_path)
    return archive_path


def build_clean_export(
    ion_root: str | Path | None = None,
    *,
    output_dir: str | Path | None = None,
    dry_run: bool = False,
    export_id: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    root = resolve_ion_root(ion_root)
    timestamp = created_at or _now()
    run_id = export_id or f"ION_CLEAN_EXPORT_{_stamp(timestamp)}"
    run_id = _slug(run_id, fallback="ION_CLEAN_EXPORT")
    output_authorization = authorize_output_dir(root, output_dir)
    if not output_authorization["authorized"]:
        return _blocked_output_manifest(
            root=root,
            output_authorization=output_authorization,
            export_id=run_id,
            created_at=timestamp,
            dry_run=dry_run,
        )
    resolved_output = Path(output_authorization["resolved_path"])

    records, warnings = collect_candidate_files(root)
    excluded_summary = _collect_excluded_summary(root)
    secret_scan = scan_included_files_for_secrets(root, records)
    status_snapshot = _status_snapshot(root)

    manifest = _manifest_payload(
        root=root,
        output_dir=resolved_output,
        output_authorization=output_authorization,
        export_id=run_id,
        created_at=timestamp,
        dry_run=dry_run,
        records=records,
        warnings=warnings,
        excluded_summary=excluded_summary,
        secret_scan=secret_scan,
        status_snapshot=status_snapshot,
    )

    if not secret_scan.get("accepted"):
        manifest["verdict"] = "REFUSED_SECRET_SCAN_BLOCKER"
        manifest["ok"] = False
        return manifest

    if dry_run:
        manifest["verdict"] = "DRY_RUN_SAFE_NO_ARCHIVE_CREATED"
        manifest["ok"] = True
        return manifest

    prehash_manifest = dict(manifest)
    prehash_manifest["archive_sha256"] = None
    prehash_manifest["sidecar_manifest_required_for_archive_sha256"] = True
    archive_path = _write_archive(root, resolved_output, run_id, records, prehash_manifest)
    archive_sha256 = _sha256_file(archive_path)
    sidecar_path = resolved_output / f"{run_id}.{MANIFEST_SIDECAR_NAME}"
    manifest = _manifest_payload(
        root=root,
        output_dir=resolved_output,
        output_authorization=output_authorization,
        export_id=run_id,
        created_at=timestamp,
        dry_run=False,
        records=records,
        warnings=warnings,
        excluded_summary=excluded_summary,
        secret_scan=secret_scan,
        status_snapshot=status_snapshot,
        archive_path=archive_path,
        archive_sha256=archive_sha256,
        sidecar_manifest_path=sidecar_path,
    )
    manifest["verdict"] = "EXPORT_CREATED"
    manifest["ok"] = True
    _write_json(sidecar_path, manifest)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a clean secret-safe ION review export.")
    parser.add_argument("--ion-root", default=".")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--export-id")
    parser.add_argument("--created-at")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = build_clean_export(
        args.ion_root,
        output_dir=args.output_dir,
        dry_run=args.dry_run,
        export_id=args.export_id,
        created_at=args.created_at,
    )
    if args.json or args.dry_run:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["archive_path"] if result.get("ok") else result["verdict"])
    return 0 if result.get("ok") else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
