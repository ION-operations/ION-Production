#!/usr/bin/env python3
"""
Check tagged-file coverage policy.

Purpose:
- Ensure coverage config excludes `*_TAGGED*.py` mirror files.
- Report syntax health of tagged mirrors without forcing immediate repair.
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path
from typing import Any, Dict, List


ROOT_DIR = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = ROOT_DIR / "pyproject.toml"
PACKAGES_DIR = ROOT_DIR / "packages"


def _read_coverage_omit_patterns() -> List[str]:
    if not PYPROJECT_PATH.exists():
        return []
    with PYPROJECT_PATH.open("rb") as f:
        pyproject = tomllib.load(f)
    return (
        pyproject.get("tool", {})
        .get("coverage", {})
        .get("run", {})
        .get("omit", [])
    )


def _has_tagged_omit(omit_patterns: List[str]) -> bool:
    return any("_TAGGED" in pattern for pattern in omit_patterns)


def _find_tagged_files() -> List[Path]:
    if not PACKAGES_DIR.exists():
        return []
    return sorted(PACKAGES_DIR.rglob("*_TAGGED*.py"))


def _compile_failures(tagged_files: List[Path]) -> List[Dict[str, Any]]:
    failures: List[Dict[str, Any]] = []
    for path in tagged_files:
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
            compile(source, str(path), "exec")
        except Exception as exc:  # SyntaxError / IndentationError etc.
            failures.append(
                {
                    "path": str(path.relative_to(ROOT_DIR)),
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
    return failures


def build_report() -> Dict[str, Any]:
    omit_patterns = _read_coverage_omit_patterns()
    tagged_files = _find_tagged_files()
    parse_failures = _compile_failures(tagged_files)
    tagged_omit_present = _has_tagged_omit(omit_patterns)

    return {
        "policy": {
            "coverage_omit_has_tagged_pattern": tagged_omit_present,
            "required_pattern_hint": "*_TAGGED*.py",
        },
        "inventory": {
            "tagged_file_count": len(tagged_files),
            "parse_failure_count": len(parse_failures),
            "parse_failures": parse_failures,
        },
        "status": {
            "policy_ok": tagged_omit_present,
            "parse_clean": len(parse_failures) == 0,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check tagged-file coverage policy")
    parser.add_argument(
        "--strict-parse",
        action="store_true",
        help="Also fail if tagged files contain syntax/indentation errors.",
    )
    args = parser.parse_args()

    report = build_report()
    print(json.dumps(report, indent=2))

    if not report["status"]["policy_ok"]:
        raise SystemExit(1)

    if args.strict_parse and not report["status"]["parse_clean"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

