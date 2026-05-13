#!/usr/bin/env python3
"""
CodexGit status report for dirty-tree triage and branch hygiene.

Usage:
  python scripts/git/codexgit_status_report.py
  python scripts/git/codexgit_status_report.py --json
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Tuple


def run_git(args: List[str], cwd: Path, trim_stdout: bool = True) -> Tuple[int, str, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    stdout = proc.stdout.strip() if trim_stdout else proc.stdout
    return proc.returncode, stdout, proc.stderr.strip()


@dataclass
class BranchHealth:
    current_branch: str
    upstream: str | None
    ahead: int
    behind: int


@dataclass
class FileHealth:
    staged_count: int
    unstaged_count: int
    untracked_count: int
    conflict_count: int
    top_level_buckets: dict


def get_repo_root(cwd: Path) -> Path:
    code, out, err = run_git(["rev-parse", "--show-toplevel"], cwd)
    if code != 0:
        raise RuntimeError(err or "Not a git repository")
    return Path(out)


def get_branch_health(repo_root: Path) -> BranchHealth:
    _, branch, _ = run_git(["branch", "--show-current"], repo_root)
    code, upstream, _ = run_git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], repo_root)
    tracked = upstream if code == 0 and upstream else None

    ahead = 0
    behind = 0
    if tracked:
        code, counts, _ = run_git(["rev-list", "--left-right", "--count", f"{tracked}...HEAD"], repo_root)
        if code == 0 and counts:
            behind_str, ahead_str = counts.split()
            behind = int(behind_str)
            ahead = int(ahead_str)

    return BranchHealth(
        current_branch=branch or "(detached)",
        upstream=tracked,
        ahead=ahead,
        behind=behind,
    )


def parse_porcelain(repo_root: Path) -> tuple[FileHealth, list[str], list[str], list[str]]:
    _, out, _ = run_git(["status", "--porcelain"], repo_root, trim_stdout=False)
    lines = [line for line in out.splitlines() if line.strip()]

    staged = []
    unstaged = []
    untracked = []
    conflicts = []
    buckets = Counter()

    def normalize_path(raw_path: str) -> str:
        path = raw_path.strip()
        # Rename format: old -> new (keep new path for impact accounting)
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        # Porcelain may quote paths with spaces.
        if len(path) >= 2 and path[0] == '"' and path[-1] == '"':
            path = path[1:-1]
        return path.replace('\\"', '"')

    for line in lines:
        status = line[:2]
        path = normalize_path(line[3:] if len(line) > 3 else "")
        bucket = path.split("/", 1)[0] if "/" in path else (path.split("\\", 1)[0] if path else "(unknown)")
        buckets[bucket] += 1

        x, y = status[0], status[1]
        if status == "??":
            untracked.append(path)
            continue
        if x != " ":
            staged.append(path)
        if y != " ":
            unstaged.append(path)
        if x == "U" or y == "U" or status in {"AA", "DD"}:
            conflicts.append(path)

    file_health = FileHealth(
        staged_count=len(staged),
        unstaged_count=len(unstaged),
        untracked_count=len(untracked),
        conflict_count=len(conflicts),
        top_level_buckets=dict(buckets.most_common(12)),
    )
    return file_health, staged[:20], unstaged[:20], untracked[:20]


def build_report(repo_root: Path) -> dict:
    branch = get_branch_health(repo_root)
    file_health, staged_sample, unstaged_sample, untracked_sample = parse_porcelain(repo_root)
    return {
        "repo_root": str(repo_root),
        "branch_health": asdict(branch),
        "file_health": asdict(file_health),
        "samples": {
            "staged": staged_sample,
            "unstaged": unstaged_sample,
            "untracked": untracked_sample,
        },
    }


def print_human(report: dict) -> None:
    b = report["branch_health"]
    f = report["file_health"]
    print("CodexGit Status Report")
    print("======================")
    print(f"Repo:      {report['repo_root']}")
    print(f"Branch:    {b['current_branch']}")
    print(f"Upstream:  {b['upstream'] or '(none)'}")
    print(f"Ahead:     {b['ahead']}")
    print(f"Behind:    {b['behind']}")
    print("")
    print("Working Tree")
    print("------------")
    print(f"Staged:    {f['staged_count']}")
    print(f"Unstaged:  {f['unstaged_count']}")
    print(f"Untracked: {f['untracked_count']}")
    print(f"Conflicts: {f['conflict_count']}")
    print("")
    print("Top-Level Impact (count)")
    print("------------------------")
    if not f["top_level_buckets"]:
        print("(clean)")
    else:
        for key, count in f["top_level_buckets"].items():
            print(f"{key}: {count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate CodexGit branch/worktree status report")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--repo", default=".", help="Repository path (default: current directory)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cwd = Path(args.repo).resolve()
    try:
        repo_root = get_repo_root(cwd)
        report = build_report(repo_root)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
