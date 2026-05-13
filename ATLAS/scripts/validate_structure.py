#!/usr/bin/env python3
"""
Validate ATLAS directory layout and required package files.
Usage: python3 validate_structure.py [ATLAS_ROOT]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REQUIRED_ROOT_DIRS = ("_meta", "systems", "comparative", "graphs", "indexes", "prompts", "scripts")
REQUIRED_META = (
    "ontology.md",
    "evidence_tiers.md",
    "package_schema.yaml",
    "tag_taxonomy.yaml",
    "naming_conventions.md",
    "relation_types.md",
    "quality_bar.md",
    "package_template.md",
)
REQUIRED_INDEXES = ("systems_index.yaml", "tag_index.yaml", "evidence_index.yaml")


def load_schema(root: Path) -> dict:
    path = root / "_meta" / "package_schema.yaml"
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_package(pkg_dir: Path, required_files: list[str]) -> list[str]:
    errors: list[str] = []
    for name in required_files:
        p = pkg_dir / name
        if not p.is_file():
            errors.append(f"Missing file: {p}")
    rel = pkg_dir / "relations.json"
    if rel.is_file():
        try:
            data = json.loads(rel.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {rel}: {e}")
            return errors
        for key in ("schema_version", "edges"):
            if key not in data:
                errors.append(f"{rel} missing key: {key}")
        for i, edge in enumerate(data.get("edges") or []):
            for k in ("type", "target", "evidence_tier"):
                if k not in edge:
                    errors.append(f"{rel} edges[{i}] missing: {k}")
    return errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1])
    root = root.resolve()
    errors: list[str] = []

    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 2

    for d in REQUIRED_ROOT_DIRS:
        if not (root / d).is_dir():
            errors.append(f"Missing directory: {root / d}")

    meta = root / "_meta"
    for name in REQUIRED_META:
        if not (meta / name).is_file():
            errors.append(f"Missing meta file: {meta / name}")

    idx = root / "indexes"
    for name in REQUIRED_INDEXES:
        if not (idx / name).is_file():
            errors.append(f"Missing index file: {idx / name}")

    schema = {}
    try:
        schema = load_schema(root)
    except Exception as e:  # noqa: BLE001
        errors.append(f"Could not load package_schema.yaml: {e}")

    required_paths = schema.get("required_paths") if schema else None
    if not required_paths:
        errors.append("package_schema.yaml: required_paths missing or empty")
        return 1

    systems = root / "systems"
    if systems.is_dir():
        for pkg_dir in sorted(systems.iterdir()):
            if not pkg_dir.is_dir():
                continue
            if pkg_dir.name.startswith("_") or pkg_dir.name == "_template":
                continue
            errors.extend(validate_package(pkg_dir, required_paths))

    if errors:
        print("ATLAS structure validation FAILED:", file=sys.stderr)
        for line in errors:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print(f"ATLAS structure OK: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
