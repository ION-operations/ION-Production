"""APOE→CMC spec/test synchronizer (Alex).

Purpose
-------
Provide a lightweight check that the APOE↔CMC implementation contract stays
aligned between:

- `APOE_CMC_PAYLOAD_SPEC_v1.md` (source of truth for payload shape)
- `packages/apoe/tests/test_cmc_integration.py` (test expectations)

This script does **NOT** touch code. It only reads files and reports:

- modality mismatches
- tag list mismatches (prefixes / required entries)
- metric name mismatches (spec vs tests)

Usage
-----
Run from the repo root:

    python -m packages.apoe.tools.apoe_cmc_spec_sync

Exit code is 0 on full alignment, non‑zero if mismatches are detected.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set


RE_MODALITY_SPEC = re.compile(r"modality\s*[:=]\s*\"?([A-Za-z0-9_]+)\"?", re.IGNORECASE)
RE_TAG_SPEC = re.compile(r"\"(apoe|plan|execution|plan_name:[^\" ]+|status:[^\" ]+)\"")
RE_MODALITY_TEST = re.compile(r"assert\s+kwargs\[\s*\"modality\"\s*]\s*==\s*\"([A-Za-z0-9_]+)\"")
RE_TAG_TEST = re.compile(r"\"(apoe|plan|execution|plan_name:[^\" ]+|status:[^\" ]+)\"")
RE_METRIC_SPEC = re.compile(r"\b(metrics|fields)\b\s*[:=]\s*(.+)", re.IGNORECASE)
RE_METADATA_KEY_TEST = re.compile(r"\"([a-zA-Z0-9_]+)\"\s*in\s*kwargs\[\s*\"metadata\"\s*]")


@dataclass
class SpecSnapshot:
    modality: str
    tags: Set[str]
    metrics: Set[str]


@dataclass
class TestSnapshot:
    modality: str
    tags: Set[str]
    metadata_keys: Set[str]


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"[apoe-cmc-spec-sync] ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(2)


def load_spec(spec_path: Path) -> SpecSnapshot:
    text = _read_text(spec_path)
    modality = ""
    tags: Set[str] = set()
    metrics: Set[str] = set()

    # modality
    for line in text.splitlines():
        m = RE_MODALITY_SPEC.search(line)
        if m:
            modality = m.group(1)
            break

    # tags (look across file)
    for m in RE_TAG_SPEC.finditer(text):
        tags.add(m.group(1))

    # metrics (very heuristic: look for "metrics: a, b, c" or similar)
    for line in text.splitlines():
        m = RE_METRIC_SPEC.search(line)
        if not m:
            continue
        # split on commas/whitespace
        rhs = m.group(2)
        for token in re.split(r"[,\s]+", rhs):
            token = token.strip().strip("`\"")
            if token:
                metrics.add(token)

    return SpecSnapshot(modality=modality, tags=tags, metrics=metrics)


def load_tests(test_path: Path) -> TestSnapshot:
    text = _read_text(test_path)
    modality = ""
    tags: Set[str] = set()
    metadata_keys: Set[str] = set()

    # modality assertion
    for line in text.splitlines():
        m = RE_MODALITY_TEST.search(line)
        if m:
            modality = m.group(1)
            break

    # tags seen in tests
    for m in RE_TAG_TEST.finditer(text):
        tags.add(m.group(1))

    # metadata keys asserted in tests
    for m in RE_METADATA_KEY_TEST.finditer(text):
        metadata_keys.add(m.group(1))

    return TestSnapshot(modality=modality, tags=tags, metadata_keys=metadata_keys)


def compare(spec: SpecSnapshot, tests: TestSnapshot) -> int:
    """Return 0 if aligned, non‑zero if mismatches are found."""
    status = 0

    print("[apoe-cmc-spec-sync] Spec snapshot:", spec)
    print("[apoe-cmc-spec-sync] Test snapshot:", tests)

    # Modality
    if spec.modality and tests.modality and spec.modality != tests.modality:
        print(
            f"[apoe-cmc-spec-sync] MISMATCH: modality (spec={spec.modality!r}, tests={tests.modality!r})",
            file=sys.stderr,
        )
        status = 1

    # Tags – ensure all required spec tags appear somewhere in tests
    missing_tags = spec.tags - tests.tags
    if missing_tags:
        print(
            f"[apoe-cmc-spec-sync] MISMATCH: spec tags not covered in tests: {sorted(missing_tags)}",
            file=sys.stderr,
        )
        status = 1

    # Metrics – warn if metrics are declared in spec but never asserted in tests
    missing_metrics = spec.metrics - tests.metadata_keys if spec.metrics else set()
    if missing_metrics:
        print(
            f"[apoe-cmc-spec-sync] WARNING: spec metrics not asserted in tests: {sorted(missing_metrics)}",
            file=sys.stderr,
        )
        # treat as non‑fatal for now

    if status == 0:
        print("[apoe-cmc-spec-sync] OK: spec and tests appear aligned on modality/tags.")
    else:
        print("[apoe-cmc-spec-sync] DONE: mismatches detected.", file=sys.stderr)
    return status


def main(argv: List[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    # Resolve repo root from this file
    here = Path(__file__).resolve()
    root = here.parents[3]  # .../AIM-OS/packages/apoe/tools/apoe_cmc_spec_sync.py

    spec_path = root / "ide_orchestration" / "prototypes" / "dac" / "docs" / "agents" / "alex" / "APOE_CMC_PAYLOAD_SPEC_v1.md"
    tests_path = root / "packages" / "apoe" / "tests" / "test_cmc_integration.py"

    print(f"[apoe-cmc-spec-sync] Using spec={spec_path}")
    print(f"[apoe-cmc-spec-sync] Using tests={tests_path}")

    spec = load_spec(spec_path)
    tests = load_tests(tests_path)
    return compare(spec, tests)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


