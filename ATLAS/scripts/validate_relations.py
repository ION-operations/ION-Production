#!/usr/bin/env python3
"""
Validate relations.json targets reference existing system slugs.
Usage: python3 validate_relations.py [ATLAS_ROOT]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1])
    systems = (root / "systems").resolve()
    errors: list[str] = []

    for pkg in sorted(systems.iterdir()):
        if not pkg.is_dir() or pkg.name.startswith("_"):
            continue
        rel = pkg / "relations.json"
        if not rel.is_file():
            continue
        try:
            data = json.loads(rel.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{rel}: invalid JSON: {e}")
            continue
        for i, edge in enumerate(data.get("edges", [])):
            tgt = edge.get("target")
            if not tgt or not isinstance(tgt, str):
                errors.append(f"{rel}: edge {i} missing target string")
                continue
            tdir = systems / tgt
            if not tdir.is_dir():
                errors.append(f"{rel}: edge target {tgt!r} has no directory {tdir}")

    if errors:
        print("ATLAS relations validation FAILED:", file=sys.stderr)
        for line in errors:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print(f"ATLAS relations OK: {systems}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
