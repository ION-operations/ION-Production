"""Read-only workspace root registry projection.

This module classifies the parent ION workspace roots without mutating the
filesystem. It is intentionally narrower than a movement gate: it projects root
classes, archive witnesses, aliases, and conflicts that future movement gates
can consume.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .ion_path_authority import DEFAULT_WORKSPACE_MANIFEST


SCHEMA_ID = "ion.workspace_root_registry_projection.v1"
MANIFEST_SCHEMA_ID = "ion.workspace_manifest.v1"

CLASS_WORKSPACE_ESTATE_ROOT = "WORKSPACE_ESTATE_ROOT"
CLASS_ACTIVE_ION_CONTROL_ROOT = "ACTIVE_ION_CONTROL_ROOT"
CLASS_ION_CONTENT_ROOT = "ION_CONTENT_ROOT"
CLASS_CARRIER_INTEGRATION_ROOT = "CARRIER_INTEGRATION_ROOT"
CLASS_PRODUCT_PROJECTION_ROOT = "PRODUCT_PROJECTION_ROOT"
CLASS_EXTERNAL_GOVERNED_PROJECT_ROOT = "EXTERNAL_GOVERNED_PROJECT_ROOT"
CLASS_REFERENCE_LIBRARY_ROOT = "REFERENCE_LIBRARY_ROOT"
CLASS_INTAKE_ROOT = "INTAKE_ROOT"
CLASS_ARCHIVE_WITNESS_ROOT = "ARCHIVE_WITNESS_ROOT"
CLASS_EXPORT_OUTPUT_ROOT = "EXPORT_OUTPUT_ROOT"
CLASS_SECRET_BOUNDARY_ROOT = "SECRET_BOUNDARY_ROOT"
CLASS_FORBIDDEN_EXTERNAL_ROOT = "FORBIDDEN_EXTERNAL_ROOT"
CLASS_ARCHIVE_FILE_WITNESS = "ARCHIVE_FILE_WITNESS"
CLASS_UNKNOWN_ROOT = "UNKNOWN_ROOT"

CONFLICT_ROOT_ALIAS_OR_TYPO = "ROOT_ALIAS_OR_TYPO_CONFLICT"
WARNING_MISSING_ALLOWED_SIBLING = "MISSING_ALLOWED_SIBLING_ROOT"
WARNING_UNKNOWN_TOP_LEVEL = "UNKNOWN_TOP_LEVEL_WORKSPACE_ENTRY"

ROOT_CLASS_BY_FAMILY = {
    "ION_Developement": CLASS_ACTIVE_ION_CONTROL_ROOT,
    "ION_GPT": CLASS_PRODUCT_PROJECTION_ROOT,
    "product_packager": CLASS_PRODUCT_PROJECTION_ROOT,
    "browser_extension": CLASS_CARRIER_INTEGRATION_ROOT,
    "mcp": CLASS_CARRIER_INTEGRATION_ROOT,
    "local_daemon": CLASS_CARRIER_INTEGRATION_ROOT,
    "systemd": CLASS_CARRIER_INTEGRATION_ROOT,
    "Cursor": CLASS_CARRIER_INTEGRATION_ROOT,
    "dAimon": CLASS_EXTERNAL_GOVERNED_PROJECT_ROOT,
    "AIM-OS": CLASS_REFERENCE_LIBRARY_ROOT,
    "ATLAS": CLASS_REFERENCE_LIBRARY_ROOT,
    "wisdomNET": CLASS_REFERENCE_LIBRARY_ROOT,
    "Needs_Routed": CLASS_INTAKE_ROOT,
    "quarentine": CLASS_ARCHIVE_WITNESS_ROOT,
}

ROOT_ID_BY_FAMILY = {
    "ION_Developement": "active_ion_control",
    "ION_GPT": "ion_gpt",
    "product_packager": "product_packager",
    "browser_extension": "browser_extension",
    "mcp": "mcp",
    "local_daemon": "local_daemon",
    "systemd": "systemd",
    "Cursor": "cursor",
    "dAimon": "daimon",
    "AIM-OS": "aim_os",
    "ATLAS": "atlas",
    "wisdomNET": "wisdomnet",
    "Needs_Routed": "needs_routed",
    "quarentine": "quarentine",
}

MOVEMENT_CLASSES_BY_ROOT_CLASS = {
    CLASS_WORKSPACE_ESTATE_ROOT: ["WORKSPACE_MANIFEST_MOVEMENT"],
    CLASS_ACTIVE_ION_CONTROL_ROOT: ["ION_KERNEL_CONTROL_MOVEMENT"],
    CLASS_ION_CONTENT_ROOT: ["ION_KERNEL_CONTROL_MOVEMENT"],
    CLASS_PRODUCT_PROJECTION_ROOT: ["CUSTOM_GPT_RELEASE_MOVEMENT", "EXPORT_PACKAGE_MOVEMENT"],
    CLASS_CARRIER_INTEGRATION_ROOT: [
        "BROWSER_EXTENSION_MOVEMENT",
        "MCP_BRIDGE_MOVEMENT",
        "LOCAL_DAEMON_MOVEMENT",
    ],
    CLASS_EXTERNAL_GOVERNED_PROJECT_ROOT: ["DAIMON_PROJECT_MOVEMENT"],
    CLASS_REFERENCE_LIBRARY_ROOT: ["ARCHIVE_REFERENCE_MOVEMENT"],
    CLASS_INTAKE_ROOT: ["INTAKE_ROUTING_MOVEMENT"],
    CLASS_ARCHIVE_WITNESS_ROOT: ["ARCHIVE_REFERENCE_MOVEMENT"],
    CLASS_EXPORT_OUTPUT_ROOT: ["EXPORT_PACKAGE_MOVEMENT"],
    CLASS_SECRET_BOUNDARY_ROOT: [],
    CLASS_FORBIDDEN_EXTERNAL_ROOT: [],
    CLASS_UNKNOWN_ROOT: [],
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


def _load_manifest(path: Path) -> dict[str, Any]:
    """Parse the constrained workspace manifest shape used by ION.

    The repo already has a lightweight manifest parser in path authority, but it
    intentionally ignores nested family metadata. This parser stays constrained
    to the same local manifest style and avoids adding a YAML dependency.
    """

    data: dict[str, Any] = {}
    current_key: str | None = None
    current_child: str | None = None
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
                current_child = None
            else:
                data[key] = {}
                current_key = key
                current_child = None
            continue
        if current_key is None:
            continue
        container = data[current_key]
        if indent == 2 and line.startswith("- "):
            if not isinstance(container, list):
                data[current_key] = []
                container = data[current_key]
            container.append(_strip_scalar(line[2:]))
            current_child = None
            continue
        if indent == 2 and ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if not isinstance(container, dict):
                continue
            if value:
                container[key] = _strip_scalar(value)
                current_child = None
            else:
                container[key] = {}
                current_child = key
            continue
        if indent >= 4 and current_child and isinstance(container, dict):
            child = container.get(current_child)
            if not isinstance(child, dict) or ":" not in line:
                continue
            key, _, value = line.partition(":")
            child[key.strip()] = _strip_scalar(value)
    return data


def _resolve(value: str | Path) -> Path:
    return Path(value).expanduser().resolve(strict=False)


def _is_within(path: Path, parent: Path) -> bool:
    path = path.resolve(strict=False)
    parent = parent.resolve(strict=False)
    return path == parent or parent in path.parents


def _root_relation(root_class: str) -> str:
    return {
        CLASS_WORKSPACE_ESTATE_ROOT: "workspace_root",
        CLASS_ACTIVE_ION_CONTROL_ROOT: "active_repo_root",
        CLASS_ION_CONTENT_ROOT: "ion_content_root",
        CLASS_PRODUCT_PROJECTION_ROOT: "sibling_projection_root",
        CLASS_CARRIER_INTEGRATION_ROOT: "sibling_project_root",
        CLASS_EXTERNAL_GOVERNED_PROJECT_ROOT: "external_governed_project_root",
        CLASS_REFERENCE_LIBRARY_ROOT: "reference_library_root",
        CLASS_INTAKE_ROOT: "intake_root",
        CLASS_ARCHIVE_WITNESS_ROOT: "archive_witness_root",
        CLASS_EXPORT_OUTPUT_ROOT: "export_root",
        CLASS_SECRET_BOUNDARY_ROOT: "vault_root",
        CLASS_FORBIDDEN_EXTERNAL_ROOT: "forbidden_external_root",
        CLASS_UNKNOWN_ROOT: "unknown_root",
    }.get(root_class, "unknown_root")


def _source_truth_level(root_class: str, active_source: bool) -> str:
    if root_class in {CLASS_ACTIVE_ION_CONTROL_ROOT, CLASS_ION_CONTENT_ROOT}:
        return "primary"
    if active_source:
        return "project_primary"
    if root_class == CLASS_PRODUCT_PROJECTION_ROOT:
        return "projection"
    if root_class == CLASS_ARCHIVE_WITNESS_ROOT:
        return "archive_witness"
    if root_class == CLASS_SECRET_BOUNDARY_ROOT:
        return "secret_boundary"
    if root_class == CLASS_EXPORT_OUTPUT_ROOT:
        return "output"
    return "conditional"


def _root_entry(
    *,
    root_id: str,
    path: Path,
    root_class: str,
    exists: bool,
    role: str = "",
    git_status: str | None = None,
    active_source: bool = False,
) -> dict[str, Any]:
    return {
        "root_id": root_id,
        "path": str(path),
        "root_class": root_class,
        "root_relation": _root_relation(root_class),
        "exists": exists,
        "role": role,
        "git_status": git_status,
        "active_source": active_source,
        "source_truth_level": _source_truth_level(root_class, active_source),
        "allowed_movement_classes": MOVEMENT_CLASSES_BY_ROOT_CLASS.get(root_class, []),
    }


def _archive_files(workspace_root: Path) -> list[dict[str, Any]]:
    if not workspace_root.exists():
        return []
    entries = []
    for path in sorted(workspace_root.iterdir(), key=lambda item: item.name.lower()):
        if path.is_file() and path.suffix.lower() == ".zip":
            entries.append(
                {
                    "path": str(path.resolve(strict=False)),
                    "root_class": CLASS_ARCHIVE_FILE_WITNESS,
                    "active_source": False,
                    "extraction_allowed": False,
                    "promotion_required": True,
                }
            )
    return entries


def _detect_aliases_and_conflicts(
    *,
    workspace_root: Path,
    families: dict[str, Any],
    allowed_sibling_roots: list[Path],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    aliases: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    allowed_by_name = {path.name: path for path in allowed_sibling_roots}
    quarentine_path = workspace_root / "quarentine"
    quarantine_path = workspace_root / "quarantine"

    if "quarentine" in families or quarentine_path.exists():
        aliases.append(
            {
                "alias_id": "quarantine_quarentine_alias",
                "canonical_root_id": "quarentine",
                "canonical_path": str(quarentine_path.resolve(strict=False)),
                "alias_path": str(quarantine_path.resolve(strict=False)),
                "alias_status": "BLOCKED_ALIAS_DO_NOT_CREATE",
                "allowed_to_create_alias_path": False,
            }
        )

    if "quarantine" in allowed_by_name and ("quarentine" in families or quarentine_path.exists()):
        conflicts.append(
            {
                "conflict_id": "ROOT-CONFLICT-0001",
                "type": CONFLICT_ROOT_ALIAS_OR_TYPO,
                "severity": "P1_BLOCKS_GATE_IMPLEMENTATION_WITHOUT_POLICY_DECISION",
                "manifest_path": str(allowed_by_name["quarantine"]),
                "observed_path": str(quarentine_path.resolve(strict=False)),
                "recommendation": "block_creation_of_quarantine_until_explicit_migration_or_alias_policy_exists",
            }
        )

    for path in allowed_sibling_roots:
        if not path.exists():
            warnings.append(
                {
                    "warning_id": f"MISSING-ALLOWED-SIBLING-{path.name}",
                    "type": WARNING_MISSING_ALLOWED_SIBLING,
                    "path": str(path),
                }
            )
    return aliases, conflicts, warnings


def build_workspace_root_registry(manifest_path: str | Path | None = None) -> dict[str, Any]:
    manifest = _resolve(manifest_path or DEFAULT_WORKSPACE_MANIFEST)
    data = _load_manifest(manifest)
    workspace_root = _resolve(data["workspace_root"])
    active_repo_root = _resolve(data["active_repo_root"])
    ion_content_root = _resolve(data["ion_content_root"])
    export_root = _resolve(data["export_root"])
    vault_root = _resolve(data["vault_root"])
    allowed_sibling_roots = [_resolve(path) for path in data.get("allowed_sibling_roots", [])]
    forbidden_roots = [_resolve(path) for path in data.get("forbidden_roots", [])]
    families = data.get("families", {})
    if not isinstance(families, dict):
        families = {}

    root_entries = [
        _root_entry(
            root_id="workspace_estate",
            path=workspace_root,
            root_class=CLASS_WORKSPACE_ESTATE_ROOT,
            exists=workspace_root.exists(),
            role="parent workspace estate",
            active_source=False,
        ),
        _root_entry(
            root_id="active_ion_control",
            path=active_repo_root,
            root_class=CLASS_ACTIVE_ION_CONTROL_ROOT,
            exists=active_repo_root.exists(),
            role="active ION kernel/context repo",
            active_source=True,
        ),
        _root_entry(
            root_id="ion_content",
            path=ion_content_root,
            root_class=CLASS_ION_CONTENT_ROOT,
            exists=ion_content_root.exists(),
            role="ION content tree",
            active_source=True,
        ),
        _root_entry(
            root_id="ion_exports_local",
            path=export_root,
            root_class=CLASS_EXPORT_OUTPUT_ROOT,
            exists=export_root.exists(),
            role="local export/archive output root",
            active_source=False,
        ),
        _root_entry(
            root_id="ion_vault_local",
            path=vault_root,
            root_class=CLASS_SECRET_BOUNDARY_ROOT,
            exists=vault_root.exists(),
            role="local secret boundary",
            active_source=False,
        ),
    ]

    seen = {entry["path"] for entry in root_entries}
    for family_name, raw_meta in families.items():
        if not isinstance(raw_meta, dict):
            raw_meta = {}
        path = (workspace_root / family_name).resolve(strict=False)
        root_class = ROOT_CLASS_BY_FAMILY.get(family_name, CLASS_UNKNOWN_ROOT)
        active_source = bool(raw_meta.get("active_source", root_class in {CLASS_ACTIVE_ION_CONTROL_ROOT, CLASS_EXTERNAL_GOVERNED_PROJECT_ROOT}))
        if str(path) in seen:
            continue
        root_entries.append(
            _root_entry(
                root_id=ROOT_ID_BY_FAMILY.get(family_name, family_name.lower().replace("-", "_")),
                path=path,
                root_class=root_class,
                exists=path.exists(),
                role=str(raw_meta.get("role") or ""),
                git_status=raw_meta.get("git_status"),
                active_source=active_source,
            )
        )
        seen.add(str(path))

    aliases, conflicts, warnings = _detect_aliases_and_conflicts(
        workspace_root=workspace_root,
        families=families,
        allowed_sibling_roots=allowed_sibling_roots,
    )

    return {
        "schema_id": SCHEMA_ID,
        "accepted": not conflicts,
        "production_authority": False,
        "live_execution_authority": False,
        "accepted_state_claim": False,
        "manifest": {
            "schema_id": data.get("schema_id", MANIFEST_SCHEMA_ID),
            "manifest_path": str(manifest),
            "workspace_root": str(workspace_root),
            "active_repo_root": str(active_repo_root),
            "ion_content_root": str(ion_content_root),
            "export_root": str(export_root),
            "vault_root": str(vault_root),
            "allowed_sibling_roots": [str(path) for path in allowed_sibling_roots],
            "forbidden_roots": [str(path) for path in forbidden_roots],
            "path_policy": data.get("path_policy", {}),
        },
        "roots": root_entries,
        "aliases": aliases,
        "archive_files": _archive_files(workspace_root),
        "conflicts": conflicts,
        "warnings": warnings,
    }


def classify_workspace_path(path: str | Path, *, registry: dict[str, Any] | None = None, manifest_path: str | Path | None = None) -> dict[str, Any]:
    loaded = registry or build_workspace_root_registry(manifest_path)
    target = _resolve(path)
    for entry in sorted(loaded["roots"], key=lambda item: len(str(item["path"])), reverse=True):
        root_path = _resolve(entry["path"])
        if entry["root_class"] == CLASS_WORKSPACE_ESTATE_ROOT and target != root_path:
            continue
        if target == root_path or _is_within(target, root_path):
            return {
                "schema_id": "ion.workspace_root_classification.v1",
                "path": str(target),
                "root_id": entry["root_id"],
                "root_path": entry["path"],
                "root_class": entry["root_class"],
                "root_relation": entry["root_relation"],
                "exists": target.exists(),
            }
    workspace_root = _resolve(loaded["manifest"]["workspace_root"])
    root_class = CLASS_UNKNOWN_ROOT if _is_within(target, workspace_root) else CLASS_FORBIDDEN_EXTERNAL_ROOT
    return {
        "schema_id": "ion.workspace_root_classification.v1",
        "path": str(target),
        "root_id": None,
        "root_path": None,
        "root_class": root_class,
        "root_relation": _root_relation(root_class),
        "exists": target.exists(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only ION workspace root registry projection")
    parser.add_argument("--manifest-path")
    parser.add_argument("--classify")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    registry = build_workspace_root_registry(args.manifest_path)
    result = classify_workspace_path(args.classify, registry=registry) if args.classify else registry
    if args.json or args.classify:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("WORKSPACE_ROOT_REGISTRY_READY" if registry["accepted"] else "WORKSPACE_ROOT_REGISTRY_CONFLICT")
    return 0 if registry["accepted"] else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
