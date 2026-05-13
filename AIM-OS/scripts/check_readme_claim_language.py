#!/usr/bin/env python3
"""
Guard README against high-risk static readiness claim language.

Fails if banned phrases are present in README.md.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
README_PATH = ROOT_DIR / "README.md"

# Keep this list focused on phrases that caused trust-gap findings.
BANNED_PATTERNS = [
    r"\b100%\s+pass\s+rate\b",
    r"\b100%\s+complete\b",
    r"\b791/791\b",
    r"\bproduction\s+ready\b",
]


def main() -> None:
    if not README_PATH.exists():
        raise SystemExit("README.md not found")

    text = README_PATH.read_text(encoding="utf-8", errors="ignore")
    violations: list[tuple[str, int, str]] = []

    lines = text.splitlines()
    for pattern in BANNED_PATTERNS:
        regex = re.compile(pattern, re.IGNORECASE)
        for idx, line in enumerate(lines, start=1):
            if regex.search(line):
                violations.append((pattern, idx, line.strip()))

    if violations:
        print("[FAIL] README claim-language violations found:")
        for pattern, line_no, line in violations:
            print(f"  - line {line_no}: /{pattern}/ -> {line}")
        raise SystemExit(1)

    print("[OK] README claim-language policy passed.")


if __name__ == "__main__":
    main()

