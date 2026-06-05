"""Local security boundary checks for ION source/export roots.

The scanner is intentionally filename-first. It reports candidate credential
files without reading or emitting secret values.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .ion_carrier_onboard import resolve_shell_root_from_ion_root

SCHEMA_ID = "ion.security_boundary.v1"

EXCLUDED_DIR_NAMES = {
    ".git",
    ".ion_private",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "env",
    "ION_VAULT_LOCAL",
    "node_modules",
    "venv",
}
SAFE_TEMPLATE_SUFFIXES = (".example", ".sample", ".template", ".dist")
PRIVATE_KEY_NAMES = {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"}
SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
TOKEN_FILE_SUFFIXES = {".token", ".secret", ".credential"}
TOKEN_NAME_RE = re.compile(r"(^|[._-])(token|secret|credential)([._-]|$)")
KEY_NAME_RE = re.compile(r"(^|[._-])(private[_-]?key|api[_-]?key|access[_-]?key)([._-]|$)")
PUBLIC_RECEIPT_PREFIXES = (
    "ION/05_context/current/worker_shift/",
    "ION/05_context/current/security/",
)


@dataclass(frozen=True)
class SecurityCandidate:
    rel_path: str
    category: str
    rule_id: str
    blocker: bool


def _is_safe_template(path: Path) -> bool:
    lowered = path.name.lower()
    return lowered.endswith(SAFE_TEMPLATE_SUFFIXES)


def _dotenv_candidate(path: Path) -> SecurityCandidate | None:
    name = path.name
    if name == ".env" or name.startswith(".env."):
        return SecurityCandidate(
            rel_path="",
            category="dotenv_template" if _is_safe_template(path) else "dotenv_secret_candidate",
            rule_id="DOTENV_TEMPLATE" if _is_safe_template(path) else "DOTENV_SECRET_FILE",
            blocker=not _is_safe_template(path),
        )
    return None


def _credential_candidate(path: Path, *, rel_path: str | None = None) -> SecurityCandidate | None:
    lowered_name = path.name.lower()
    lowered_path = path.as_posix().lower()
    suffix = path.suffix.lower()
    if lowered_name in PRIVATE_KEY_NAMES:
        return SecurityCandidate("", "private_key_file", "PRIVATE_KEY_FILENAME", True)
    if suffix in SECRET_SUFFIXES:
        return SecurityCandidate("", "secret_key_material", "SECRET_KEY_SUFFIX", True)
    if suffix in TOKEN_FILE_SUFFIXES:
        return SecurityCandidate("", "token_or_secret_file", "TOKEN_SECRET_SUFFIX", True)
    if suffix == ".json" and "cloudflared" in lowered_path and ("credential" in lowered_name or "cert" in lowered_name):
        return SecurityCandidate("", "cloudflared_credential_json", "CLOUDFLARED_CREDENTIAL_JSON", True)
    if rel_path and any(rel_path.startswith(prefix) for prefix in PUBLIC_RECEIPT_PREFIXES):
        return None
    if suffix == ".json" and TOKEN_NAME_RE.search(lowered_name):
        return SecurityCandidate("", "token_or_secret_json", "TOKEN_SECRET_JSON_NAME", True)
    if suffix in {".json", ".txt", ".conf", ".cfg"} and KEY_NAME_RE.search(lowered_name):
        return SecurityCandidate("", "key_file_candidate", "KEY_FILE_NAME", True)
    return None


def _iter_files(scan_root: Path) -> Iterable[Path]:
    if not scan_root.exists():
        return
    stack = [scan_root]
    while stack:
        current = stack.pop()
        try:
            entries = sorted(current.iterdir(), key=lambda item: item.name)
        except OSError:
            continue
        for entry in entries:
            if entry.is_dir():
                if entry.name in EXCLUDED_DIR_NAMES:
                    continue
                stack.append(entry)
                continue
            if entry.is_file():
                yield entry


def _safe_template_variable_names(path: Path) -> list[str]:
    if not _is_safe_template(path):
        return []
    names: list[str] = []
    try:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            name = stripped.split("=", 1)[0].strip()
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                names.append(name)
    except OSError:
        return []
    return sorted(set(names))


def scan_security_boundary(
    root: str | Path | None = None,
    *,
    export_roots: Iterable[str | Path] | None = None,
) -> dict[str, Any]:
    shell_root = resolve_shell_root_from_ion_root(root)
    roots = [Path(".")]
    roots.extend(Path(item) for item in (export_roots or []))
    findings: list[dict[str, Any]] = []
    reviewed_files = 0
    skipped_roots: list[str] = []

    for root_rel in roots:
        scan_root = (shell_root / root_rel).resolve()
        try:
            scan_root.relative_to(shell_root)
        except ValueError:
            skipped_roots.append(root_rel.as_posix())
            continue
        for path in _iter_files(scan_root):
            reviewed_files += 1
            rel = path.relative_to(shell_root).as_posix()
            candidates = [_dotenv_candidate(path), _credential_candidate(path, rel_path=rel)]
            for candidate in [item for item in candidates if item is not None]:
                finding_id = f"SEC-{len(findings) + 1:04d}"
                findings.append(
                    {
                        "finding_id": finding_id,
                        "path": rel,
                        "filename": path.name,
                        "category": candidate.category,
                        "rule_id": candidate.rule_id,
                        "blocker": candidate.blocker,
                        "safe_variable_names": _safe_template_variable_names(path),
                        "secret_values_emitted": False,
                        "content_value_scan_performed": False,
                    }
                )

    blockers = [finding for finding in findings if finding["blocker"]]
    return {
        "schema_id": SCHEMA_ID,
        "status": "SECURITY_BLOCKED" if blockers else "SECURITY_BOUNDARY_READY",
        "accepted": not blockers,
        "root": str(shell_root),
        "reviewed_file_count": reviewed_files,
        "finding_count": len(findings),
        "blocker_count": len(blockers),
        "findings": findings,
        "skipped_roots": skipped_roots,
        "excluded_dir_names": sorted(EXCLUDED_DIR_NAMES),
        "secret_values_emitted": False,
        "production_authority": False,
        "live_execution_authority": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan ION source/export roots for credential-bearing filenames.")
    parser.add_argument("--ion-root", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = scan_security_boundary(args.ion_root)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["status"])
        for finding in result["findings"]:
            print(f"- {finding['finding_id']} {finding['path']} {finding['rule_id']}")
    return 0 if result["accepted"] else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
