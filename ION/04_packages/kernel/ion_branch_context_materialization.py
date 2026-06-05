"""Lazy branch context materialization helpers for ION.

The helper covers the pre-node moment: a carrier has entered a folder and needs
to know whether to inherit parent context, propose a candidate local context, or
skip the folder as non-branch material.  It is dry-run/candidate by default and
does not overwrite existing local capsules.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

try:
    import yaml
except Exception:  # pragma: no cover - degraded environment
    yaml = None  # type: ignore[assignment]


SCHEMA_ID = "ion.lazy_branch_context_materialization.v0_1"
CANDIDATE_CAPSULE_SCHEMA_ID = "ion.branch_context_capsule_candidate.v0_1"
RECEIPT_SCHEMA_ID = "ion.branch_context_materialization_receipt.v0_1"
RECEIPTS_PATH = "ION/05_context/current/branch_context_materialization/receipts"

LAZY_MATURITY_LEVELS: tuple[str, ...] = (
    "level_0_absent",
    "level_1_inherited",
    "level_2_stub",
    "level_3_candidate",
    "level_4_active",
    "level_5_reviewed",
    "level_6_accepted",
)

CONTEXT_FILE_NAMES: tuple[str, ...] = (
    "README.md",
    "ION_CONTEXT_CAPSULE.yaml",
    "AGENTS.md",
    "SKILL.md",
)

IGNORE_PARTS = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "dist",
    "build",
    "cache",
    ".cache",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    "coverage",
    "htmlcov",
    "target",
    "vendor",
    "third_party",
    "quarantine",
    "quarentine",
}

SECRET_PARTS = {
    "ion_vault_local",
    "vault",
    "vaults",
    "secrets",
    ".secrets",
    "secret",
    "credentials",
    ".credentials",
    "tokens",
    ".tokens",
}

GENERATED_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".o",
    ".so",
    ".dll",
    ".dylib",
    ".zip",
    ".tar",
    ".tgz",
    ".gz",
    ".7z",
    ".whl",
}

MEANINGFUL_FILE_SUFFIXES = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".md",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".sql",
    ".sh",
}

MEANINGFUL_NAMES = {
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "requirements.txt",
    "README.md",
    "ION_CONTEXT_CAPSULE.yaml",
    "AGENTS.md",
    "SKILL.md",
}

MEANINGFUL_DIR_NAMES = {
    "src",
    "test",
    "tests",
    "docs",
    "protocols",
    "templates",
    "schemas",
    "routes",
    "agents",
    "kernel",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stamp() -> str:
    return _now().replace("-", "").replace(":", "").replace("+00:00", "Z")


def _slug(value: str, *, fallback: str = "branch", limit: int = 96) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "").strip()).strip("._-")
    return (slug or fallback)[:limit]


def _resolve(path: Path | str) -> Path:
    return Path(path).expanduser().resolve(strict=False)


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _rel(path: Path, root: Path | None) -> str:
    if root is not None:
        try:
            return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
        except ValueError:
            pass
    return path.as_posix()


def _path_for_search(path: Path) -> Path:
    if path.exists() and path.is_file():
        return path.parent
    if path.suffix and not path.exists():
        return path.parent
    return path


def resolve_shell_root(path: Path | str | None = None, root: Path | str | None = None) -> Path | None:
    """Resolve the nearest ION shell root when available."""

    if root is not None:
        return _resolve(root)
    start = _path_for_search(_resolve(path or Path.cwd()))
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "ION" / "REPO_AUTHORITY.md").is_file():
            return candidate
    return None


def ignore_branch_path_reason(path: Path | str) -> str | None:
    """Return an ignore reason for cache/vendor/generated/secret paths."""

    candidate = Path(path)
    for raw_part in candidate.parts:
        part = raw_part.lower()
        if part in IGNORE_PARTS:
            return f"ignored_part:{raw_part}"
        if part in SECRET_PARTS or "secret" in part or "credential" in part:
            return f"secret_or_vault_part:{raw_part}"
        if part.endswith(".egg-info"):
            return f"generated_metadata_part:{raw_part}"
    suffixes = candidate.suffixes
    if suffixes:
        joined_suffix = "".join(suffixes[-2:]).lower()
        if joined_suffix in {".tar.gz"}:
            return f"generated_artifact_suffix:{joined_suffix}"
    suffix = candidate.suffix.lower()
    if suffix in GENERATED_SUFFIXES:
        return f"generated_artifact_suffix:{suffix}"
    return None


def should_ignore_branch_path(path: Path | str) -> bool:
    """Return true when a path must not receive branch context materialization."""

    return ignore_branch_path_reason(path) is not None


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    if yaml is None or not path.is_file():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _existing_context_summary(path: Path, root: Path | None) -> dict[str, Any] | None:
    readme = path / "README.md"
    capsule = path / "ION_CONTEXT_CAPSULE.yaml"
    if not readme.is_file() and not capsule.is_file():
        return None
    capsule_data = _load_yaml_mapping(capsule)
    return {
        "path": _rel(path, root),
        "readme_path": _rel(readme, root) if readme.is_file() else None,
        "capsule_path": _rel(capsule, root) if capsule.is_file() else None,
        "schema_id": capsule_data.get("schema_id"),
        "declared_maturity_level": capsule_data.get("maturity_level"),
        "accepted_state_claim": bool(
            capsule_data.get("accepted_state_claim")
            or (capsule_data.get("authority") if isinstance(capsule_data.get("authority"), dict) else {}).get(
                "accepted_state_claim"
            )
        ),
    }


def find_parent_branch_context(path: Path | str, root: Path | str | None = None) -> dict[str, Any]:
    """Find the nearest ancestor that has README or capsule context."""

    candidate = _path_for_search(_resolve(path))
    shell_root = resolve_shell_root(candidate, root=root)
    stop_at = shell_root.resolve(strict=False) if shell_root else None
    current = candidate.parent
    while True:
        summary = _existing_context_summary(current, stop_at)
        if summary:
            summary["found"] = True
            return summary
        if stop_at is not None and current == stop_at:
            break
        if current.parent == current:
            break
        if stop_at is not None and not _is_relative_to(current, stop_at) and current != stop_at:
            break
        current = current.parent
    return {"found": False, "path": _rel(stop_at, stop_at) if stop_at else None}


def _meaningful_child(child: Path) -> bool:
    if child.name in MEANINGFUL_NAMES:
        return True
    if child.is_dir() and child.name in MEANINGFUL_DIR_NAMES:
        return True
    return child.is_file() and child.suffix.lower() in MEANINGFUL_FILE_SUFFIXES


def inspect_branch_path(path: Path | str, root: Path | str | None = None) -> dict[str, Any]:
    """Inspect a possible branch folder without mutating it."""

    candidate = _path_for_search(_resolve(path))
    shell_root = resolve_shell_root(candidate, root=root)
    ignore_reason = ignore_branch_path_reason(candidate)
    exists = candidate.exists()
    local_context_files: list[str] = []
    direct_children: list[str] = []
    meaningful_markers: list[str] = []

    if exists and candidate.is_dir() and ignore_reason is None:
        for name in CONTEXT_FILE_NAMES:
            context_path = candidate / name
            if context_path.is_file():
                local_context_files.append(_rel(context_path, shell_root))
        try:
            children = sorted(candidate.iterdir(), key=lambda item: item.name.lower())[:80]
        except OSError:
            children = []
        for child in children:
            direct_children.append(child.name)
            if _meaningful_child(child):
                meaningful_markers.append(child.name)
    elif exists and candidate.is_file() and _meaningful_child(candidate):
        meaningful_markers.append(candidate.name)

    local_files_inspected = list(local_context_files)
    if exists and candidate.is_dir() and not local_files_inspected:
        for name in CONTEXT_FILE_NAMES:
            local_files_inspected.append(_rel(candidate / name, shell_root))

    return {
        "schema_id": f"{SCHEMA_ID}.inspection",
        "path": _rel(candidate, shell_root),
        "absolute_path": candidate.as_posix(),
        "exists": exists,
        "is_dir": candidate.is_dir(),
        "is_file": candidate.is_file(),
        "ignored": ignore_reason is not None,
        "ignore_reason": ignore_reason,
        "local_context_files": local_context_files,
        "local_files_inspected": local_files_inspected,
        "direct_children_sample": direct_children,
        "meaningful_markers": meaningful_markers,
        "meaningful": bool(meaningful_markers),
    }


def _local_lazy_maturity(path: Path, inspection: Mapping[str, Any]) -> str:
    readme = path / "README.md"
    capsule = path / "ION_CONTEXT_CAPSULE.yaml"
    if capsule.is_file():
        data = _load_yaml_mapping(capsule)
        maturity = str(data.get("maturity_level") or "")
        if maturity in LAZY_MATURITY_LEVELS:
            return maturity
        receipts = data.get("receipts") if isinstance(data.get("receipts"), dict) else {}
        surfaces = data.get("local_surfaces") if isinstance(data.get("local_surfaces"), dict) else {}
        has_receipts = bool(receipts.get("latest")) if isinstance(receipts, dict) else False
        has_surfaces = any(bool(value) for value in surfaces.values()) if isinstance(surfaces, dict) else False
        if has_receipts or has_surfaces:
            return "level_4_active"
        return "level_3_candidate"
    if readme.is_file() or inspection.get("local_context_files"):
        return "level_2_stub"
    return "level_1_inherited"


def classify_branch_context(
    path: Path | str,
    *,
    root: Path | str | None = None,
    materialize: bool = False,
) -> dict[str, Any]:
    """Classify a possible branch path.

    ``materialize=False`` is the default dry-run posture. A meaningful folder
    without local context inherits parent context and reports that candidate
    materialization is available; it does not create files.
    """

    candidate = _path_for_search(_resolve(path))
    shell_root = resolve_shell_root(candidate, root=root)
    inspection = inspect_branch_path(candidate, root=shell_root)
    parent_context = find_parent_branch_context(candidate, root=shell_root)

    if inspection["ignored"]:
        classification = "ignored_path"
        decision = "not_branch"
        maturity = "level_0_absent"
        next_action = "do_not_materialize_this_path"
        candidate_available = False
    elif not inspection["exists"]:
        classification = "missing_path"
        decision = "blocked"
        maturity = "level_0_absent"
        next_action = "resolve_or_create_the_target_folder_before_branch_materialization"
        candidate_available = False
    elif (candidate / "ION_CONTEXT_CAPSULE.yaml").is_file():
        classification = "existing_local_context"
        decision = "inherited"
        maturity = _local_lazy_maturity(candidate, inspection)
        next_action = "use_existing_local_context; do_not_overwrite_by_default"
        candidate_available = False
    elif (candidate / "README.md").is_file() or inspection["local_context_files"]:
        classification = "local_stub"
        decision = "inherited"
        maturity = "level_2_stub"
        next_action = "use_local_stub_and_parent_context; propose_capsule_only_if_task_requires_it"
        candidate_available = True
    elif inspection["meaningful"]:
        classification = "materializable_branch"
        decision = "proposed" if materialize else "inherited"
        maturity = "level_3_candidate" if materialize else "level_1_inherited"
        next_action = (
            "candidate_context_can_be_written_with_explicit_write"
            if materialize
            else "inherit_parent_context_for_this_task; candidate_context_available"
        )
        candidate_available = True
    else:
        classification = "unmaterialized_branch"
        decision = "inherited"
        maturity = "level_1_inherited"
        next_action = "inherit_parent_context_until_real_work_requires_local_context"
        candidate_available = False

    return {
        "schema_id": SCHEMA_ID,
        "path": _rel(candidate, shell_root),
        "absolute_path": candidate.as_posix(),
        "classification": classification,
        "decision": decision,
        "maturity_level": maturity,
        "candidate_available": candidate_available,
        "dry_run": not materialize,
        "should_write_files": False,
        "parent_context": parent_context,
        "inspection": inspection,
        "next_action": next_action,
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "candidate_state_only": True,
    }


def build_candidate_branch_capsule(
    path: Path | str,
    parent_context: Mapping[str, Any] | None = None,
    inspection: Mapping[str, Any] | None = None,
    *,
    root: Path | str | None = None,
) -> dict[str, Any]:
    """Build candidate capsule data without writing it."""

    candidate = _path_for_search(_resolve(path))
    shell_root = resolve_shell_root(candidate, root=root)
    parent = dict(parent_context or find_parent_branch_context(candidate, root=shell_root))
    inspect = dict(inspection or inspect_branch_path(candidate, root=shell_root))
    rel_path = _rel(candidate, shell_root)
    parent_ref = parent.get("capsule_path") or parent.get("readme_path") or parent.get("path") or "parent_context_unresolved"
    read_first = [item for item in inspect.get("local_context_files", []) if item]
    if not read_first:
        read_first = ["README.md", "ION_CONTEXT_CAPSULE.yaml"]

    return {
        "schema_id": CANDIDATE_CAPSULE_SCHEMA_ID,
        "branch_id": _slug(rel_path.replace("/", "_"), fallback="root"),
        "path": rel_path,
        "parent_branch_ref": parent_ref,
        "maturity_level": "level_3_candidate",
        "purpose": f"Candidate local context for work entering {rel_path}.",
        "when_to_enter": [
            "when a bounded packet or carrier task touches this folder",
            "when parent context is insufficient for safe local work",
        ],
        "read_first": read_first,
        "local_templates": [],
        "local_agents_or_roles": [],
        "allowed_operations": [
            "read_only_inspection",
            "candidate_patch_with_receipt",
            "focused_tests_when_in_scope",
        ],
        "receipts_path": RECEIPTS_PATH,
        "known_blockers": [] if not inspect.get("ignored") else [str(inspect.get("ignore_reason"))],
        "escalation_routes": [
            "parent_branch_context",
            "operator_gate_for_authority_or_destructive_work",
        ],
        "last_updated": _now(),
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "candidate_state_only": True,
    }


def _sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize_path_list(paths: list[Path | str] | tuple[Path | str, ...] | None, root: Path | None) -> list[str]:
    normalized: list[str] = []
    for item in paths or []:
        normalized.append(_rel(_resolve(item), root))
    return normalized


def build_materialization_receipt(
    branch_path: Path | str,
    *,
    parent_context: Mapping[str, Any] | None = None,
    inspection: Mapping[str, Any] | None = None,
    classification: Mapping[str, Any] | str | None = None,
    decision: str | None = None,
    touched_paths: list[Path | str] | tuple[Path | str, ...] | None = None,
    created_files: list[Path | str] | tuple[Path | str, ...] | None = None,
    next_carrier_instructions: list[str] | tuple[str, ...] | None = None,
    root: Path | str | None = None,
) -> dict[str, Any]:
    """Build a materialization receipt with hashes for created context files."""

    candidate = _path_for_search(_resolve(branch_path))
    shell_root = resolve_shell_root(candidate, root=root)
    parent = dict(parent_context or find_parent_branch_context(candidate, root=shell_root))
    inspect = dict(inspection or inspect_branch_path(candidate, root=shell_root))
    if isinstance(classification, Mapping):
        class_name = str(classification.get("classification") or "unknown")
        decision_value = decision or str(classification.get("decision") or "inherited")
    else:
        class_name = str(classification or "unknown")
        decision_value = decision or "inherited"

    touched = _normalize_path_list(touched_paths, shell_root)
    files_to_hash = list(created_files or [])
    if not files_to_hash:
        files_to_hash = list(touched_paths or [])
    created_sha: dict[str, str] = {}
    for item in files_to_hash:
        item_path = _resolve(item)
        digest = _sha256(item_path)
        if digest:
            created_sha[_rel(item_path, shell_root)] = digest

    return {
        "schema_id": RECEIPT_SCHEMA_ID,
        "created_at": _now(),
        "branch_path": _rel(candidate, shell_root),
        "parent_context_used": parent,
        "local_files_inspected": list(inspect.get("local_files_inspected") or []),
        "classification": class_name,
        "decision": decision_value,
        "touched_paths": touched,
        "created_file_sha256": created_sha,
        "next_carrier_instructions": list(
            next_carrier_instructions
            or ["continue_original_task; treat materialized context as candidate until reviewed"]
        ),
        "accepted_state_claim": False,
        "production_authority": False,
        "live_execution_authority": False,
        "candidate_state_only": True,
    }


def write_materialization_receipt(
    receipt: Mapping[str, Any],
    *,
    root: Path | str | None = None,
    receipt_dir: Path | str | None = None,
    write: bool = False,
) -> dict[str, Any]:
    """Write a receipt only when ``write=True`` is explicit."""

    shell_root = resolve_shell_root(root or Path.cwd(), root=root) or _resolve(root or Path.cwd())
    if not write:
        return {
            "wrote": False,
            "receipt_path": None,
            "receipt": dict(receipt),
            "candidate_state_only": True,
        }

    target_dir = _resolve(receipt_dir) if receipt_dir else shell_root / RECEIPTS_PATH
    target_dir.mkdir(parents=True, exist_ok=True)
    branch_slug = _slug(str(receipt.get("branch_path") or "branch"))
    target = target_dir / f"{_stamp()}_{branch_slug}_materialization_receipt.json"
    target.write_text(json.dumps(dict(receipt), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "wrote": True,
        "receipt_path": _rel(target, shell_root),
        "receipt": dict(receipt),
        "candidate_state_only": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ION lazy branch context materialization helper")
    parser.add_argument("--ion-root", dest="root", default=None)
    parser.add_argument("--json", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    classify = sub.add_parser("classify")
    classify.add_argument("path")
    classify.add_argument("--materialize", action="store_true")

    candidate = sub.add_parser("candidate")
    candidate.add_argument("path")

    receipt = sub.add_parser("receipt")
    receipt.add_argument("path")
    receipt.add_argument("--decision", default=None)
    receipt.add_argument("--classification", default=None)
    receipt.add_argument("--write", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "classify":
        payload = classify_branch_context(args.path, root=args.root, materialize=args.materialize)
    elif args.command == "candidate":
        payload = build_candidate_branch_capsule(args.path, root=args.root)
    else:
        classification = classify_branch_context(args.path, root=args.root)
        built = build_materialization_receipt(
            args.path,
            classification=args.classification or classification,
            decision=args.decision,
            root=args.root,
        )
        payload = write_materialization_receipt(built, root=args.root, write=args.write)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
