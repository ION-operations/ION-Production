#!/usr/bin/env python3
"""
Validate YAML frontmatter in ATLAS package markdown files.
Usage: python3 validate_frontmatter.py [ATLAS_ROOT]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
REQUIRED_KEYS = ("atlas_package", "system_slug", "schema_version", "last_reviewed", "evidence_grade")
MD_FILES = (
    "00_identity.md",
    "01_scope.md",
    "02_architecture.md",
    "03_components.md",
    "04_process_memory_namespace.md",
    "05_storage_network_ipc.md",
    "06_security_permissions.md",
    "07_extension_tooling.md",
    "08_build_deploy_update.md",
    "09_operator_surface.md",
    "10_observability.md",
    "11_lineage.md",
    "12_relation_map.md",
    "13_evidence_ledger.md",
    "14_documented_vs_inferred.md",
)


def parse_frontmatter(text: str) -> dict | None:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1])
    root = root.resolve()
    systems = root / "systems"
    errors: list[str] = []

    if not systems.is_dir():
        print(f"No systems dir: {systems}", file=sys.stderr)
        return 2

    for pkg_dir in sorted(systems.iterdir()):
        if not pkg_dir.is_dir() or pkg_dir.name.startswith("_"):
            continue
        for name in MD_FILES:
            path = pkg_dir / name
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            fm = parse_frontmatter(text)
            if fm is None:
                errors.append(f"{path}: missing or invalid frontmatter")
                continue
            for k in REQUIRED_KEYS:
                if k not in fm:
                    errors.append(f"{path}: frontmatter missing key {k!r}")
            if fm.get("atlas_package") != "system":
                errors.append(f"{path}: atlas_package must be 'system'")
            if fm.get("system_slug") != pkg_dir.name:
                errors.append(
                    f"{path}: system_slug {fm.get('system_slug')!r} != directory {pkg_dir.name!r}"
                )

    if errors:
        print("ATLAS frontmatter validation FAILED:", file=sys.stderr)
        for line in errors:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print(f"ATLAS frontmatter OK: {root / 'systems'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
