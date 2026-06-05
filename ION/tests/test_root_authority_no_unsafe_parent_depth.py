from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[2]

SCAN_ROOTS = (
    "ION/04_packages/kernel",
    "ION/07_templates",
    "ION/tests",
    "product_packager",
    "Cursor",
    "browser_extension",
    "local_daemon",
    "systemd",
    "ION_VNEXT",
)

TEXT_SUFFIXES = {".py", ".md", ".yaml", ".yml", ".json"}
FIXED_PARENT_DEPTH_RE = re.compile(r"\.resolve\(\)\.parents\[(\d+)\]")
ROOT_AUTHORITY_HINT_RE = re.compile(r"\b(repo|workspace|root|authority|shell)\b", re.IGNORECASE)

SAFE_PACKAGE_RELATIVE_FILES = {
    "ION/04_packages/kernel/ion_bounded_agent_lane_smoke.py",
    "ION/04_packages/kernel/name_lineage.py",
}


@dataclass(frozen=True)
class ParentDepthOccurrence:
    path: str
    line_number: int
    line_text: str
    classification: str
    reason: str


def _iter_scan_files() -> tuple[Path, ...]:
    files: list[Path] = []
    seen: set[Path] = set()
    for root_rel in SCAN_ROOTS:
        root = (REPO_ROOT / root_rel).resolve()
        if not root.exists():
            continue
        for candidate in sorted(root.rglob("*")):
            if not candidate.is_file() or candidate.suffix not in TEXT_SUFFIXES:
                continue
            rel = candidate.relative_to(REPO_ROOT)
            if any(part in {".git", "node_modules", "__pycache__", ".pytest_cache"} for part in rel.parts):
                continue
            if candidate not in seen:
                files.append(candidate)
                seen.add(candidate)
    return tuple(files)


def _classify_occurrence(path: str, line: str) -> tuple[str, str]:
    if path.startswith("ION/tests/"):
        return "SAFE_TEST_FIXTURE_OR_DOC_HISTORICAL_WITNESS", "test fixture path math"
    if path in SAFE_PACKAGE_RELATIVE_FILES:
        return "SAFE_PACKAGE_RELATIVE_CONSTANT", "package-relative constant"
    if path == "product_packager/ion_product_package_builder.py" and "ROOT = Path(__file__).resolve().parents[1]" in line:
        return "SAFE_PACKAGE_RELATIVE_CONSTANT", "generated projection script uses package-local root"
    if "ION/09_integrations" in line or "historical" in line.lower() or "legacy" in line.lower():
        return "LEGACY_COMPATIBILITY_MAPPING", "legacy topology compatibility witness"
    if ROOT_AUTHORITY_HINT_RE.search(line):
        return "UNSAFE_REPO_ROOT_INFERENCE", "fixed parent-depth used in root/authority context"
    return "NEEDS_FOLLOWUP_REVIEW", "fixed parent-depth without explicit root-authority cue"


def _collect_fixed_parent_depth_occurrences() -> tuple[ParentDepthOccurrence, ...]:
    findings: list[ParentDepthOccurrence] = []
    for file_path in _iter_scan_files():
        rel = file_path.relative_to(REPO_ROOT).as_posix()
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if FIXED_PARENT_DEPTH_RE.search(line) is None:
                continue
            classification, reason = _classify_occurrence(rel, line)
            findings.append(
                ParentDepthOccurrence(
                    path=rel,
                    line_number=line_number,
                    line_text=line.strip(),
                    classification=classification,
                    reason=reason,
                )
            )
    return tuple(findings)


def test_no_unsafe_fixed_parent_depth_repo_root_inference() -> None:
    findings = _collect_fixed_parent_depth_occurrences()

    blocked = [
        finding
        for finding in findings
        if finding.classification in {"UNSAFE_REPO_ROOT_INFERENCE", "NEEDS_PATCH"}
    ]

    assert not blocked, "\\n".join(
        [
            "Unsafe fixed parent-depth root inference detected:",
            *[
                f"- {finding.path}:{finding.line_number} {finding.classification} :: {finding.line_text}"
                for finding in blocked
            ],
        ]
    )


def test_product_packager_repo_root_uses_marker_discovery() -> None:
    path = REPO_ROOT / "product_packager/ion_product_package_builder.py"
    text = path.read_text(encoding="utf-8")

    assert "def repo_root_from_script() -> Path:" in text
    assert '(candidate / "pyproject.toml").is_file()' in text
    assert '(candidate / "ION" / "REPO_AUTHORITY.md").is_file()' in text
    assert "Path(__file__).resolve().parents[3]" not in text
