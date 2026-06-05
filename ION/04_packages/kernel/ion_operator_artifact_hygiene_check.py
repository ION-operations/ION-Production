"""Operator artifact hygiene checker.

This gate keeps release/install artifacts separate from internal build material.
It is intentionally small and local: it reads a candidate folder and returns a
proof-bearing pass/fail report without mutating the artifact.
"""
from __future__ import annotations

import argparse
import json
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from pathlib import PurePosixPath
from typing import Iterable


GPT_KIT_ROOT_ENTRIES = (
    "00_READ_ME_FIRST_DO_THIS_ONLY.md",
    "01_PASTE_THIS_IN_GPT_BUILDER_INSTRUCTIONS.md",
    "02_UPLOAD_EVERY_FILE_IN_THIS_FOLDER_TO_GPT_KNOWLEDGE",
)

GENERAL_OPERATOR_OUTCOMES = (
    "OPERATOR_FINAL",
    "INTERNAL_REFERENCE_DO_NOT_TOUCH",
    "BLOCKED_NO_OPERATOR_ARTIFACT",
)

OPERATOR_UPLOAD_NAME_FRAGMENTS = (
    "FILES_TO_UPLOAD",
    "UPLOAD_THESE",
    "FINAL_OPERATOR_UPLOAD_KIT",
)

ROOT_REFERENCE_ONLY_NAMES = (
    "VALIDATION_LOGS",
    "OPERATOR_DO_NOT_UPLOAD_REFERENCE_ONLY",
    "INTERNAL_REFERENCE_DO_NOT_TOUCH",
)

LOOSE_REFERENCE_ONLY_FILE_FRAGMENTS = (
    "HASHES",
    "SHA256SUMS",
    "TASK_RETURN",
    "INSTALL_SHEET",
    "SMOKE_PLAN",
)

FORBIDDEN_EXACT_PARTS = (
    ".git",
    "__pycache__",
    "node_modules",
)

FORBIDDEN_PART_FRAGMENTS = (
    "ion_vault_local",
    "vault",
    "session",
    "cache",
)

FORBIDDEN_SUFFIXES = (
    ".pyc",
    ".pyo",
)

README_REQUIRED_PHRASES = (
    "paste the instructions",
    "upload every file inside 02_upload_every_file_in_this_folder_to_gpt_knowledge",
    "upload nothing else",
    "run the smoke prompt after save",
)


@dataclass(frozen=True)
class HygieneIssue:
    code: str
    path: str
    detail: str


@dataclass
class HygieneReport:
    checked_path: str
    mode: str
    passed: bool = True
    issues: list[HygieneIssue] = field(default_factory=list)
    root_entries: list[str] = field(default_factory=list)
    knowledge_files: list[str] = field(default_factory=list)
    knowledge_file_count: int = 0
    knowledge_file_limit: int | None = None

    def add_issue(self, code: str, path: Path | str, detail: str) -> None:
        self.passed = False
        self.issues.append(HygieneIssue(code=code, path=str(path), detail=detail))

    def to_dict(self) -> dict[str, object]:
        return {
            "checked_path": self.checked_path,
            "mode": self.mode,
            "passed": self.passed,
            "root_entries": self.root_entries,
            "knowledge_file_count": self.knowledge_file_count,
            "knowledge_file_limit": self.knowledge_file_limit,
            "knowledge_files": self.knowledge_files,
            "issues": [issue.__dict__ for issue in self.issues],
        }


def _entry_names(path: Path) -> list[str]:
    if not path.exists() or not path.is_dir():
        return []
    return sorted(child.name for child in path.iterdir())


def _has_fragment(name: str, fragments: Iterable[str]) -> bool:
    upper = name.upper()
    return any(fragment.upper() in upper for fragment in fragments)


def _is_forbidden_relative_path(relative_path: str) -> bool:
    parts = PurePosixPath(relative_path.replace("\\", "/")).parts
    for part in parts:
        lower = part.lower()
        if lower in FORBIDDEN_EXACT_PARTS:
            return True
        if any(fragment in lower for fragment in FORBIDDEN_PART_FRAGMENTS):
            return True
    return any(relative_path.lower().endswith(suffix) for suffix in FORBIDDEN_SUFFIXES)


def _find_forbidden_paths(root: Path) -> list[str]:
    forbidden: list[str] = []
    if not root.exists():
        return forbidden
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if _is_forbidden_relative_path(relative):
            forbidden.append(relative)
            continue
        if path.is_file() and path.suffix.lower() == ".zip":
            try:
                with zipfile.ZipFile(path) as archive:
                    for name in archive.namelist():
                        if _is_forbidden_relative_path(name):
                            forbidden.append(f"{relative}!/{name}")
            except zipfile.BadZipFile:
                forbidden.append(f"{relative}!/<bad_zip>")
    return forbidden


def _check_same_level_upload_conflicts(root: Path, report: HygieneReport) -> None:
    for directory in [root, *(path for path in root.rglob("*") if path.is_dir())]:
        child_dirs = [child.name for child in directory.iterdir() if child.is_dir()]
        has_files_to_upload = any(name.upper().startswith("FILES_TO_UPLOAD") for name in child_dirs)
        has_upload_these = any(name.upper().startswith("UPLOAD_THESE") for name in child_dirs)
        if has_files_to_upload and has_upload_these:
            report.add_issue(
                "mixed_upload_folder_names_same_level",
                directory,
                "FILES_TO_UPLOAD* and UPLOAD_THESE* are visible at the same level.",
            )


def _check_visible_fallbacks(root: Path, report: HygieneReport) -> None:
    for directory in [root, *(path for path in root.rglob("*") if path.is_dir())]:
        child_dirs = [child.name for child in directory.iterdir() if child.is_dir()]
        has_primary = any(
            name.upper().startswith("FILES_TO_UPLOAD")
            or "FINAL_OPERATOR_UPLOAD_KIT" in name.upper()
            for name in child_dirs
        )
        fallback_dirs = [name for name in child_dirs if "FALLBACK" in name.upper()]
        if has_primary and fallback_dirs:
            report.add_issue(
                "fallback_visible_beside_primary",
                directory,
                f"Fallback folders are visible beside a primary operator folder: {fallback_dirs}",
            )


def _check_root_reference_material(root: Path, report: HygieneReport) -> None:
    for child in root.iterdir() if root.exists() and root.is_dir() else []:
        if child.is_dir() and child.name in ROOT_REFERENCE_ONLY_NAMES:
            report.add_issue(
                "reference_material_in_operator_root",
                child,
                "Reference-only folder is visible in the operator upload root.",
            )
        if child.is_file() and _has_fragment(child.name, LOOSE_REFERENCE_ONLY_FILE_FRAGMENTS):
            report.add_issue(
                "loose_reference_file_in_operator_root",
                child,
                "Loose hash, task return, install sheet, or smoke plan is in the operator upload root.",
            )


def check_general_operator_artifact(root: str | Path) -> HygieneReport:
    """Validate a generic Codex operator artifact result root."""

    path = Path(root)
    report = HygieneReport(checked_path=str(path), mode="general")
    report.root_entries = _entry_names(path)
    if not path.exists() or not path.is_dir():
        report.add_issue("missing_root", path, "Checked path does not exist or is not a directory.")
        return report

    outcome_entries = [name for name in report.root_entries if name in GENERAL_OPERATOR_OUTCOMES]
    if len(outcome_entries) != 1 or len(report.root_entries) != 1:
        report.add_issue(
            "general_outcome_root_not_single",
            path,
            "General operator result root must contain exactly one outcome folder.",
        )
    _check_same_level_upload_conflicts(path, report)
    _check_visible_fallbacks(path, report)
    for forbidden in _find_forbidden_paths(path):
        report.add_issue("forbidden_path", forbidden, "Forbidden path fragment or bytecode file is present.")
    return report


def check_gpt_upload_kit(
    root: str | Path,
    *,
    knowledge_limit: int = 20,
    expected_knowledge_count: int | None = 20,
) -> HygieneReport:
    """Validate the collapsed GPT Builder upload-kit shape."""

    path = Path(root)
    report = HygieneReport(
        checked_path=str(path),
        mode="gpt_upload",
        knowledge_file_limit=knowledge_limit,
    )
    report.root_entries = _entry_names(path)
    if not path.exists() or not path.is_dir():
        report.add_issue("missing_root", path, "Checked path does not exist or is not a directory.")
        return report

    expected_entries = sorted(GPT_KIT_ROOT_ENTRIES)
    if report.root_entries != expected_entries:
        report.add_issue(
            "gpt_kit_root_entries_not_exact",
            path,
            f"GPT kit root must contain exactly {expected_entries}; found {report.root_entries}.",
        )

    operator_dirs = [
        child.name
        for child in path.iterdir()
        if child.is_dir() and _has_fragment(child.name, OPERATOR_UPLOAD_NAME_FRAGMENTS)
    ]
    if len(operator_dirs) > 1:
        report.add_issue(
            "multiple_operator_upload_folders",
            path,
            f"More than one operator-facing upload folder is visible: {operator_dirs}",
        )

    _check_same_level_upload_conflicts(path, report)
    _check_visible_fallbacks(path, report)
    _check_root_reference_material(path, report)

    readme = path / "00_READ_ME_FIRST_DO_THIS_ONLY.md"
    if not readme.exists():
        report.add_issue("missing_readme", readme, "Required README is missing.")
    else:
        readme_text = readme.read_text(encoding="utf-8").lower().replace("`", "")
        for phrase in README_REQUIRED_PHRASES:
            if phrase not in readme_text:
                report.add_issue(
                    "readme_missing_required_instruction",
                    readme,
                    f"README missing required phrase: {phrase}",
                )

    knowledge_dir = path / "02_UPLOAD_EVERY_FILE_IN_THIS_FOLDER_TO_GPT_KNOWLEDGE"
    if not knowledge_dir.exists() or not knowledge_dir.is_dir():
        report.add_issue("missing_knowledge_folder", knowledge_dir, "Knowledge upload folder is missing.")
    else:
        files = sorted(child.name for child in knowledge_dir.iterdir() if child.is_file())
        report.knowledge_files = files
        report.knowledge_file_count = len(files)
        if report.knowledge_file_count > knowledge_limit:
            report.add_issue(
                "knowledge_file_limit_exceeded",
                knowledge_dir,
                f"Knowledge folder has {report.knowledge_file_count} files; limit is {knowledge_limit}.",
            )
        if expected_knowledge_count is not None and report.knowledge_file_count != expected_knowledge_count:
            report.add_issue(
                "knowledge_file_count_not_exact",
                knowledge_dir,
                f"Knowledge folder has {report.knowledge_file_count} files; expected {expected_knowledge_count}.",
            )

    for forbidden in _find_forbidden_paths(path):
        report.add_issue("forbidden_path", forbidden, "Forbidden path fragment or bytecode file is present.")

    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check operator artifact hygiene.")
    parser.add_argument("path", help="Artifact root to check.")
    parser.add_argument("--mode", choices=("general", "gpt-upload"), default="general")
    parser.add_argument("--knowledge-limit", type=int, default=20)
    parser.add_argument("--expected-knowledge-count", type=int, default=20)
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(argv)

    if args.mode == "gpt-upload":
        report = check_gpt_upload_kit(
            args.path,
            knowledge_limit=args.knowledge_limit,
            expected_knowledge_count=args.expected_knowledge_count,
        )
    else:
        report = check_general_operator_artifact(args.path)

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        status = "PASS" if report.passed else "FAIL"
        print(f"{status} {report.checked_path}")
        for issue in report.issues:
            print(f"- {issue.code}: {issue.path}: {issue.detail}")
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
