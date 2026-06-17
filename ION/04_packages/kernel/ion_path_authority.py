"""Workspace path authority for incident-hardened ION writes and artifacts."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path, PurePath
from typing import Any, Mapping

from .ion_workspace_paths import resolve_repo_root


SCHEMA_ID = "ion.path_authority_decision.v1"
MANIFEST_SCHEMA_ID = "ion.workspace_manifest.v1"
WORKSPACE_MANIFEST_NAME = "ION_WORKSPACE_MANIFEST.yaml"
DEFAULT_WORKSPACE_MANIFEST = (resolve_repo_root(Path(__file__)) / "ION_WORKSPACE_MANIFEST.yaml").resolve(strict=False)

CLASS_ACTIVE_REPO = "ACTIVE_REPO"
CLASS_ION_CONTENT = "ION_CONTENT"
CLASS_WORKSPACE_EXPORT = "WORKSPACE_EXPORT"
CLASS_WORKSPACE_VAULT = "WORKSPACE_VAULT"
CLASS_WORKSPACE_SIBLING = "WORKSPACE_SIBLING"
CLASS_OUTSIDE_WORKSPACE = "OUTSIDE_WORKSPACE"
CLASS_FORBIDDEN_ROOT = "FORBIDDEN_ROOT"

REASON_ALLOWED = "AUTHORIZED"
REASON_PARENT_SEGMENT_FORBIDDEN = "PARENT_SEGMENT_FORBIDDEN"
REASON_FORBIDDEN_ROOT = "FORBIDDEN_ROOT"
REASON_WORKSPACE_ESCAPE_BLOCKED = "WORKSPACE_ESCAPE_BLOCKED"
REASON_ARTIFACT_INSIDE_ACTIVE_REPO = "ARTIFACT_INSIDE_ACTIVE_REPO"
REASON_ARTIFACT_OUTSIDE_EXPORT_ROOT = "ARTIFACT_OUTSIDE_EXPORT_ROOT"
REASON_VAULT_WRITE_FORBIDDEN = "VAULT_WRITE_FORBIDDEN"
REASON_DOTENV_WRITE_FORBIDDEN = "DOTENV_WRITE_FORBIDDEN"


@dataclass(frozen=True)
class WorkspaceAuthority:
    workspace_root: Path
    active_repo_root: Path
    ion_content_root: Path
    export_root: Path
    vault_root: Path
    allowed_sibling_roots: tuple[Path, ...]
    forbidden_roots: tuple[Path, ...]
    path_policy: dict[str, bool]
    manifest_path: Path

    def to_manifest_summary(self) -> dict[str, Any]:
        return {
            "schema_id": MANIFEST_SCHEMA_ID,
            "manifest_path": str(self.manifest_path),
            "workspace_root": str(self.workspace_root),
            "active_repo_root": str(self.active_repo_root),
            "ion_content_root": str(self.ion_content_root),
            "export_root": str(self.export_root),
            "vault_root": str(self.vault_root),
            "allowed_sibling_roots": [str(path) for path in self.allowed_sibling_roots],
            "forbidden_roots": [str(path) for path in self.forbidden_roots],
            "path_policy": dict(self.path_policy),
        }


def _strip_scalar(value: str) -> Any:
    text = value.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"'}:
        text = text[1:-1]
    lowered = text.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "null":
        return None
    return text


def _load_simple_yaml(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None
    current_indent: int | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if indent == 0:
            key, sep, value = line.partition(":")
            if not sep:
                continue
            key = key.strip()
            value = value.strip()
            if value:
                data[key] = _strip_scalar(value)
                current_key = None
                current_indent = None
            else:
                current_key = key
                current_indent = indent
                data[key] = [] if key.endswith("_roots") else {}
            continue
        if current_key is None or current_indent is None:
            continue
        container = data[current_key]
        if line.startswith("- "):
            if not isinstance(container, list):
                data[current_key] = []
                container = data[current_key]
            container.append(_strip_scalar(line[2:]))
        elif ":" in line:
            if not isinstance(container, dict):
                continue
            key, _, value = line.partition(":")
            container[key.strip()] = _strip_scalar(value)
    return data


def _resolve_path(value: str | Path) -> Path:
    return Path(value).expanduser().resolve(strict=False)


def discover_workspace_manifest(start: str | Path | None = None) -> Path:
    """Resolve the workspace manifest from explicit or marker-discovered context."""

    env_path = os.environ.get("ION_WORKSPACE_MANIFEST")
    if env_path:
        path = _resolve_path(env_path)
        if not path.is_file():
            raise FileNotFoundError(f"ION_WORKSPACE_MANIFEST does not exist: {path}")
        return path

    start_path = _resolve_path(start or Path.cwd())
    if start_path.is_file():
        start_path = start_path.parent
    for candidate_root in (start_path, *start_path.parents):
        candidate = candidate_root / WORKSPACE_MANIFEST_NAME
        if candidate.is_file():
            return candidate.resolve(strict=False)
    raise FileNotFoundError(
        f"{WORKSPACE_MANIFEST_NAME} not found by upward marker discovery from {start_path}"
    )


def load_workspace_authority(manifest_path: str | Path | None = None) -> WorkspaceAuthority:
    path = _resolve_path(manifest_path or DEFAULT_WORKSPACE_MANIFEST)
    data = _load_simple_yaml(path)
    missing = [
        key
        for key in (
            "workspace_root",
            "active_repo_root",
            "ion_content_root",
            "export_root",
            "vault_root",
        )
        if not data.get(key)
    ]
    if missing:
        raise ValueError(f"workspace manifest missing required keys:{','.join(missing)}")
    return WorkspaceAuthority(
        workspace_root=_resolve_path(data["workspace_root"]),
        active_repo_root=_resolve_path(data["active_repo_root"]),
        ion_content_root=_resolve_path(data["ion_content_root"]),
        export_root=_resolve_path(data["export_root"]),
        vault_root=_resolve_path(data["vault_root"]),
        allowed_sibling_roots=tuple(_resolve_path(item) for item in data.get("allowed_sibling_roots", [])),
        forbidden_roots=tuple(_resolve_path(item) for item in data.get("forbidden_roots", [])),
        path_policy={key: bool(value) for key, value in dict(data.get("path_policy", {})).items()},
        manifest_path=path,
    )


def _is_within(path: Path, parent: Path) -> bool:
    path = path.resolve(strict=False)
    parent = parent.resolve(strict=False)
    return path == parent or parent in path.parents


def _has_parent_segment(path: str | Path) -> bool:
    return any(part == ".." for part in PurePath(str(path)).parts)


def _has_dotenv_part(path: Path) -> bool:
    return any(part == ".env" or part.startswith(".env.") for part in path.parts)


def _has_vault_part(path: Path) -> bool:
    return any(part == "ION_VAULT_LOCAL" for part in path.parts)


def _classification(authority: WorkspaceAuthority, resolved_path: Path) -> str:
    if any(_is_within(resolved_path, root) for root in authority.forbidden_roots):
        return CLASS_FORBIDDEN_ROOT
    if not _is_within(resolved_path, authority.workspace_root):
        return CLASS_OUTSIDE_WORKSPACE
    if _is_within(resolved_path, authority.export_root):
        return CLASS_WORKSPACE_EXPORT
    if _is_within(resolved_path, authority.vault_root):
        return CLASS_WORKSPACE_VAULT
    if _is_within(resolved_path, authority.ion_content_root):
        return CLASS_ION_CONTENT
    if _is_within(resolved_path, authority.active_repo_root):
        return CLASS_ACTIVE_REPO
    if any(_is_within(resolved_path, root) for root in authority.allowed_sibling_roots):
        return CLASS_WORKSPACE_SIBLING
    return CLASS_WORKSPACE_SIBLING


def _resolve_candidate(raw_path: str | Path, *, authority: WorkspaceAuthority, base_root: str) -> Path:
    candidate = Path(raw_path).expanduser()
    if candidate.is_absolute():
        return candidate.resolve(strict=False)
    if base_root == "workspace":
        base = authority.workspace_root
    elif base_root == "active_repo":
        base = authority.active_repo_root
    else:
        raise ValueError(f"unsupported base_root:{base_root}")
    return (base / candidate).resolve(strict=False)


def decide_path_authority(
    raw_path: str | Path,
    *,
    purpose: str = "write",
    base_root: str = "active_repo",
    manifest_path: str | Path | None = None,
    authority: WorkspaceAuthority | None = None,
    allow_vault: bool = False,
) -> dict[str, Any]:
    """Return a JSON-serializable path authority decision."""

    loaded = authority or load_workspace_authority(manifest_path)
    parent_forbidden = bool(loaded.path_policy.get("forbid_parent_segments_for_write", True))
    parent_sensitive = purpose in {"write", "artifact", "lease"}
    if parent_sensitive and parent_forbidden and _has_parent_segment(raw_path):
        resolved_for_evidence = _resolve_candidate(raw_path, authority=loaded, base_root=base_root)
        return {
            "schema_id": SCHEMA_ID,
            "authorized": False,
            "reason_code": REASON_PARENT_SEGMENT_FORBIDDEN,
            "classification": _classification(loaded, resolved_for_evidence),
            "raw_path": str(raw_path),
            "resolved_path": str(resolved_for_evidence),
            "purpose": purpose,
            "base_root": base_root,
            "manifest": loaded.to_manifest_summary(),
        }

    resolved = _resolve_candidate(raw_path, authority=loaded, base_root=base_root)
    classification = _classification(loaded, resolved)
    reason = REASON_ALLOWED
    authorized = True

    if classification == CLASS_FORBIDDEN_ROOT:
        authorized = False
        reason = REASON_FORBIDDEN_ROOT
    elif classification == CLASS_OUTSIDE_WORKSPACE:
        authorized = False
        reason = REASON_WORKSPACE_ESCAPE_BLOCKED
    elif _has_dotenv_part(Path(raw_path)) or _has_dotenv_part(resolved):
        authorized = False
        reason = REASON_DOTENV_WRITE_FORBIDDEN
    elif (classification == CLASS_WORKSPACE_VAULT or _has_vault_part(Path(raw_path)) or _has_vault_part(resolved)) and not allow_vault:
        authorized = False
        reason = REASON_VAULT_WRITE_FORBIDDEN
    elif purpose == "artifact":
        require_outside_active_repo = bool(loaded.path_policy.get("require_artifacts_outside_active_repo", True))
        if _is_within(resolved, loaded.active_repo_root):
            if require_outside_active_repo:
                authorized = False
                reason = REASON_ARTIFACT_INSIDE_ACTIVE_REPO
        elif not _is_within(resolved, loaded.export_root):
            authorized = False
            reason = REASON_ARTIFACT_OUTSIDE_EXPORT_ROOT

    return {
        "schema_id": SCHEMA_ID,
        "authorized": authorized,
        "reason_code": reason,
        "classification": classification,
        "raw_path": str(raw_path),
        "resolved_path": str(resolved),
        "purpose": purpose,
        "base_root": base_root,
        "manifest": loaded.to_manifest_summary(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ION workspace path authority decision helper")
    parser.add_argument("path")
    parser.add_argument("--purpose", default="write", choices=("write", "artifact", "lease", "read"))
    parser.add_argument("--base-root", default="active_repo", choices=("active_repo", "workspace"))
    parser.add_argument("--manifest-path")
    parser.add_argument("--allow-vault", action="store_true")
    args = parser.parse_args(argv)
    result = decide_path_authority(
        args.path,
        purpose=args.purpose,
        base_root=args.base_root,
        manifest_path=args.manifest_path,
        allow_vault=args.allow_vault,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["authorized"] else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
